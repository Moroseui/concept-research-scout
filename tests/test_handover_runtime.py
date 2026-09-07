"""Human controls and report recovery use the same persistent runtime interface."""
import json
from pathlib import Path
from orchestrator.handover_runtime import Runtime
from orchestrator.handover_coordinator import Coordinator,encoded,digest


def runtime(tmp_path,monkeypatch):
    import orchestrator.handover_runtime as module
    monkeypatch.setattr(module,'checked_source',lambda root,pin:Path(root))
    config={'source_root':str(tmp_path),'source':'a'*40,'controller_uid':module.os.getuid(),
            'state':str(tmp_path/'state'),'broker_socket':str(tmp_path/'socket')}
    return Runtime(config)


def test_report_identity_stable_after_review_queue_mutates(tmp_path,monkeypatch):
    from orchestrator.operations_report import Queue
    r=runtime(tmp_path,monkeypatch)
    first=r.enqueue_report('2026-09-06',[],{'waiting':'operator'})
    report=json.loads((r.state/'tasks'/first['id']/'report.json').read_text())
    Queue(r.state/'reports').claim(report['id'])
    second=r.enqueue_report('2026-09-06',[],{'waiting':'operator'})
    assert first==second


def test_recovery_uses_status_operation_only(tmp_path,monkeypatch):
    import orchestrator.handover_runtime as module
    r=runtime(tmp_path,monkeypatch);binding=r.enqueue_report('2026-09-06',[],{})
    r.q.submit(binding)
    r.q.db.execute("INSERT INTO stages VALUES(?,0,'STARTED',NULL)",(binding['id'],))
    r.q.db.execute("UPDATE tasks SET status='BLOCKED'")
    calls=[]
    def retrieve(path,operation,body):
        calls.append(operation)
        return {'status':'UNCERTAIN_MODEL_RECONCILE_NO_RETRY'}
    monkeypatch.setattr(module,'request_broker',retrieve)
    r.recover()
    assert calls==['stage_status']
    assert r.q.status()['tasks'][0]['status']=='BLOCKED'


def test_schedule_disabled_by_default_and_daily_identity_deduplicates(tmp_path,monkeypatch):
    from datetime import datetime,timezone
    import orchestrator.handover_runtime as module
    r=runtime(tmp_path,monkeypatch);now=datetime(2026,9,7,2,tzinfo=timezone.utc)
    assert r.scheduled_report(now)['status']=='SCHEDULE_DISABLED'
    r.config['report_schedule']={'zone':'America/New_York','hour':21,'minute':0,'evidence_file':'synthetic'}
    monkeypatch.setattr(module,'configuration',lambda path:{'source':'a'*40,'receipts':[],'task_state':{'blocked':'operator gate'}})
    first=r.scheduled_report(now)
    assert first['status']=='SCHEDULED'
    assert r.scheduled_report(now)=={'status':'ALREADY_SCHEDULED','task':first['task']}
    assert len(r.q.status()['tasks'])==1


def test_completed_review_bookkeeping_is_repeatable_without_models(tmp_path,monkeypatch):
    from orchestrator.operations_report import Queue
    r=runtime(tmp_path,monkeypatch);binding=r.enqueue_report('2026-09-06',[],{})
    calls=[]
    def fixture(bound,position):
        calls.append(position)
        return {'status':'COMPLETE','answer':'Synthetic fixture assessment '+str(position),
                'receipt':{'actual_model':'claude-fable-5','session_id':'fixture-session'}}
    r.q.handlers={name:fixture for name in binding['stages']}
    r.q.admission=lambda b:{'status':'ADMITTED'}
    r.q.submit(binding);assert r.q.tick()['status']=='COMPLETE'
    r.bookkeeping();r.bookkeeping()
    report=json.loads((r.state/'tasks'/binding['id']/'report.json').read_text())
    assert Queue(r.state/'reports').status(report['id'])['status']=='REVIEWED'
    assert calls==[0,1,2]


def test_noncanonical_stages_refuse_before_admission(tmp_path,monkeypatch):
    import pytest
    r=runtime(tmp_path,monkeypatch);binding=r.enqueue_report('2026-09-06',[],{})
    with pytest.raises(ValueError,match='CANONICAL'):r.q.submit({**binding,'stages':['review']})
    assert r.q.status()['tasks']==[]


def test_bookkeeping_failure_does_not_block_other_completed_task(tmp_path,monkeypatch):
    r=runtime(tmp_path,monkeypatch)
    bad=r.enqueue_report('2026-09-06',[],{'fixture':'bad'})
    good=r.enqueue_report('2026-09-07',[],{'fixture':'good'})
    for binding in (bad,good):
        r.q.submit(binding)
        r.q.db.execute("UPDATE tasks SET status='COMPLETE' WHERE id=?",(binding['id'],))
    seen=[]
    def save(row):
        seen.append(row['id'])
        if row['id']==bad['id']:raise OSError('fixture failure')
    monkeypatch.setattr(r,'_bookkeep',save)
    for _ in range(5):r.bookkeeping()
    assert seen.count(good['id'])==1
    assert seen.count(bad['id'])==3
    assert r.q.db.execute('SELECT status FROM bookkeeping WHERE task=?',(bad['id'],)).fetchone()[0]=='BLOCKED'


def test_control_receipt_failure_is_recorded_and_next_request_applies(tmp_path,monkeypatch):
    import types,stat
    import orchestrator.handover_runtime as module
    r=runtime(tmp_path,monkeypatch);directory=tmp_path/'controls';directory.mkdir()
    r.config['control_inbox']=str(directory)
    requests={}
    for i,action in enumerate(('pause','resume')):
        path=directory/(format(i+1,'064x')+'.json');path.write_text('{}')
        requests[str(path)]={'source':'a'*40,'control':{'id':action,'expected_revision':i,'action':action}}
    real_stat=Path.stat
    def fixture_stat(path,*a,**kw):
        if path==directory:return types.SimpleNamespace(st_uid=0,st_mode=stat.S_IFDIR|0o750)
        return real_stat(path,*a,**kw)
    monkeypatch.setattr(Path,'stat',fixture_stat)
    monkeypatch.setattr(module,'configuration',lambda path:requests[str(path)])
    original=module.immutable
    def write(path,raw):
        if path.name=='control-'+format(1,'064x')+'.json':raise OSError('fixture receipt destination failure')
        original(path,raw)
    monkeypatch.setattr(module,'immutable',write)
    results=r.controls()
    assert results[0]['receipt_status']=='WRITE_BLOCKED'
    assert results[1]['status']=='APPLIED'
    assert r.q.status()['revision']==2 and not r.q.status()['paused']
    assert r.controls()==[]


def test_corrupt_running_task_isolated_from_independent_work(tmp_path,monkeypatch):
    r=runtime(tmp_path,monkeypatch)
    bad=r.enqueue_report('2026-09-06',[],{'fixture':'corrupt'})
    good=r.enqueue_report('2026-09-07',[],{'fixture':'eligible'})
    for binding in (bad,good):r.q.submit(binding)
    r.q.db.execute("UPDATE tasks SET status='RUNNING' WHERE id=?",(bad['id'],))
    r.q.db.execute("INSERT INTO stages VALUES(?,0,'STARTED',NULL)",(bad['id'],))
    (r.state/(bad['id']+'-0.json')).write_text('{}')
    r.recover()
    assert r.q.db.execute('SELECT status FROM tasks WHERE id=?',(bad['id'],)).fetchone()[0]=='BLOCKED'
    r.q.handlers={name:lambda *a:{'status':'COMPLETE','kind':'synthetic'} for name in good['stages']}
    r.q.admission=lambda b:{'status':'ADMITTED'}
    assert r.q.tick()=={'status':'COMPLETE','task':good['id']}
