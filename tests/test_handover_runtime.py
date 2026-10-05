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


def test_recorded_change_reaches_private_task_and_public_status_without_proposal(tmp_path,monkeypatch):
    from orchestrator import change_requests as changes
    r=runtime(tmp_path,monkeypatch)
    store=tmp_path/'changes';r.config['change_request_store']=str(store)
    source=Path(__file__).resolve().parents[1]
    actor={'kind':'human','identity':'fixture-operator'}
    request=changes.submit(store,source,'remote-handover','Clarify this private task explanation.',
                           actor,key='fixture-repair',scope_limits=['Explanation only'])
    folder=store/request['identity']
    changes.record(folder,'AUTHORIZED',actor,{'authority_reference':'fixture-only',
        'rationale':'Eligible explanation repair','review_policy':'Deferred review pending'})
    applied=changes.record(folder,'APPLIED',actor,{'modification':'Updated the explanation',
        'checks':'Fixture check','result_binding':'Preserved original, revised version recorded','review_status':'PENDING'})
    first=r.enqueue_report('2026-09-10',[],{'waiting':'review'})
    task=r.state/'tasks'/first['id']
    original=(task/'packet.json').read_bytes();packet=json.loads(original)
    assert packet['recorded_changes']['requests'][0]['review_status']=='PENDING'
    report=json.loads((task/'report.json').read_text())
    public=(r.state/'reports'/(report['id']+'.md')).read_text()
    assert request['identity'] in public and 'PENDING' in public
    assert request['requested_change'] not in public
    changes.record(folder,'REVIEW',actor,{'applied_event':applied['identity'],'verdict':'REQUEST_CHANGES',
        'rationale':'Explanation is still ambiguous','review_evidence':'Fixture independent finding',
        'affected_results':['Correct the revised explanation before dependent use']})
    second=r.enqueue_report('2026-09-10',[],{'waiting':'review'})
    assert second['id']!=first['id'] and (task/'packet.json').read_bytes()==original
    revised=json.loads((r.state/'tasks'/second['id']/'packet.json').read_text())
    assert revised['recorded_changes']['requests'][0]['review_status']=='REQUEST_CHANGES'


def test_large_permitted_source_packet_keeps_public_report_small(tmp_path,monkeypatch):
    r=runtime(tmp_path,monkeypatch)
    binding=r.enqueue_report('2026-09-07',[],{},reviewer_evidence={'permitted_source':'x'*120000})
    folder=r.state/'tasks'/binding['id']
    assert (folder/'packet.json').stat().st_size>100000
    report=json.loads((folder/'report.json').read_text())
    assert (r.state/'reports'/(report['id']+'.md')).stat().st_size<100000


def test_human_pause_command_detects_existing_state_without_new_request(tmp_path,monkeypatch):
    import orchestrator.handover_runtime as module
    monkeypatch.setattr(module.os,'getuid',lambda:0)
    monkeypatch.setattr(module,'controller_command',lambda config,op:{'revision':7,'paused':True})
    result=module.operator_request({'source':'a'*40},'pause')
    assert result=={'status':'ALREADY_PAUSED','revision':7}
    # No inbox or internal state file was needed or rewritten for this repeat.
    assert list(tmp_path.iterdir())==[]


def test_completed_report_delivery_waits_for_permission_and_pause(tmp_path,monkeypatch):
    import orchestrator.report_delivery as delivery
    r=runtime(tmp_path,monkeypatch);binding=r.enqueue_report('2026-09-07',[],{})
    r.q.submit(binding)
    r.q.db.execute('INSERT INTO bookkeeping VALUES(?,?,1,NULL)',(binding['id'],'COMPLETE'))
    r.deliver_reports()
    assert r.status()['report_delivery'][0]['status']=='PRIVATE_ONLY'
    calls=[]
    def perform(*args):calls.append(args);return {'source':'c'*40}
    monkeypatch.setattr(delivery,'deliver',perform)
    r.config['publication']={'checkout':'dedicated','permission_sha256':'d'*64}
    r.q.db.execute('UPDATE controls SET paused=1')
    r.deliver_reports();assert not calls
    r.q.db.execute('UPDATE controls SET paused=0')
    r.deliver_reports();r.deliver_reports()
    assert len(calls)==1 and r.status()['report_delivery'][0]['commit_pin']=='c'*40


def test_live_report_requires_admission_then_publication_before_review(tmp_path,monkeypatch):
    import pytest
    import orchestrator.report_delivery as delivery
    import orchestrator.handover_runtime as module
    r=runtime(tmp_path,monkeypatch);binding=r.enqueue_report('2026-09-07',[],{})
    r.config['purpose']='LIVE_APPROVED_HANDOVER'
    calls=[]
    monkeypatch.setattr(module,'request_broker',lambda *args:calls.append('admit') or {'status':'ADMITTED'})
    with pytest.raises(ValueError,match='LIVE_REPORT_PUBLICATION_CONFIGURATION'):
        r.admit(binding)
    assert not calls
    r.config['publication']={'checkout':'dedicated','permission_sha256':'d'*64}
    def publish(*args,**kwargs):
        assert kwargs['phase']=='finalized';calls.append('publish');return {'status':'PUBLISHED'}
    monkeypatch.setattr(delivery,'deliver',publish)
    assert r.admit(binding)['status']=='ADMITTED' and calls==['admit','publish']
    calls.clear()
    monkeypatch.setattr(module,'request_broker',lambda *args:calls.append('refused') or {'status':'HALTED'})
    assert r.admit(binding)['status']=='HALTED' and calls==['refused']


def test_notifications_are_optional_information_and_do_not_dispatch(tmp_path,monkeypatch):
    import orchestrator.handover_runtime as module
    r=runtime(tmp_path,monkeypatch);binding=r.enqueue_report('2026-09-07',[],{});r.q.submit(binding)
    r.q.db.execute("UPDATE tasks SET status='BLOCKED',reason='UNCERTAIN_STAGE_RECONCILE_NO_RETRY'")
    calls=[]
    def notify(path,operation,body):
        calls.append(operation)
        return {'status':'SENT','issue':7}
    monkeypatch.setattr(module,'request_broker',notify)
    r.notifications();assert not calls
    r.config['notifications']=True
    r.notifications();r.notifications()
    assert calls==['flush_notifications','notify_task_block','flush_notifications']
    assert r.q.status()['tasks'][0]['status']=='BLOCKED'
    assert r.status()['notification_delivery'][0]['status']=='SENT'


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
    monkeypatch.setattr(module,'configuration',lambda path,**kwargs:{'source':'a'*40,'receipts':[],'task_state':{'blocked':'operator gate'}})
    first=r.scheduled_report(now)
    assert first['status']=='SCHEDULED'
    assert r.scheduled_report(now)=={'status':'ALREADY_SCHEDULED','task':first['task']}
    assert len(r.q.status()['tasks'])==1


def test_scheduled_report_records_current_queue_without_private_binding(tmp_path,monkeypatch):
    from datetime import datetime,timezone
    import orchestrator.handover_runtime as module
    r=runtime(tmp_path,monkeypatch)
    pending=r.enqueue_report('2026-09-06',[],{'fixture':'pending'})
    r.q.submit(pending)
    r.q.db.execute("UPDATE tasks SET status='BLOCKED',reason='RECONCILE_ORIGINAL_RECEIPT'")
    r.config['report_schedule']={'zone':'UTC','hour':0,'minute':0,'evidence_file':'synthetic'}
    monkeypatch.setattr(module,'configuration',lambda path,**kwargs:{'source':'a'*40,'receipts':[],
        'task_state':{'research_queue':'Recorded independent research remains queued.'}})
    result=r.scheduled_report(datetime(2026,9,7,tzinfo=timezone.utc))
    packet=json.loads((r.state/'tasks'/result['task']/'packet.json').read_text())
    state=packet['decision_inbox']
    assert state['coordinator_tasks']==[{'id':pending['id'],'status':'BLOCKED','reason':'RECONCILE_ORIGINAL_RECEIPT'}]
    assert '1 blocked' in state['coordinator_summary']
    assert 'not a census' in state['evidence_scope']
    assert 'binding' not in state['coordinator_tasks'][0]


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


def historical_report_fixture(tmp_path,monkeypatch):
    """Synthetic model originals; exercise actual saved queue/report bindings."""
    import hashlib
    import orchestrator.handover_runtime as module
    from orchestrator.hosted_cycle import encoded as broker_encoded
    r=runtime(tmp_path,monkeypatch);binding=r.enqueue_report('2026-09-06',[],{})
    packet=json.loads((r.state/'tasks'/binding['id']/'packet.json').read_bytes())
    replies={}
    def fixture(bound,position):
        stage=binding['stages'][position]
        answer='Synthetic original report assessment '+str(position)
        model='claude-fable-5' if stage=='review' else 'gpt-6-astra'
        output={'status':'COMPLETE','answer':answer,'packet_sha256':hashlib.sha256(broker_encoded(packet)).hexdigest(),
            'receipt':{'requested_model':model,'actual_model':model,'returncode':0,
                'session_id':'synthetic-report-session','answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),
                'operating_context_sha256':'c'*64}}
        replies[stage]=output;return output
    r.q.handlers={name:fixture for name in binding['stages']};r.q.admission=lambda b:{'status':'ADMITTED'}
    r.q.submit(binding);assert r.q.tick()['status']=='COMPLETE'
    # Complete originals exist, but derived report review has not yet attached.
    r.q.db.execute("UPDATE tasks SET status='BLOCKED' WHERE id=?",(binding['id'],))
    (r.state/(binding['id']+'-0.json')).unlink()
    upgraded=module.Runtime({**r.config,'source':'b'*40})
    calls=[]
    def retrieve(socket,operation,body):
        assert operation=='stage_status' and body['event']==r.event(binding)
        calls.append(body['stage']);return {**replies[body['stage']],'duplicate':True}
    monkeypatch.setattr(module,'request_broker',retrieve)
    return upgraded,binding,replies,calls


def test_completed_old_report_recovers_original_review_without_new_admission(tmp_path,monkeypatch):
    import pytest
    from orchestrator.operations_report import Queue
    r,binding,replies,calls=historical_report_fixture(tmp_path,monkeypatch)
    packet_path=r.state/'tasks'/binding['id']/'packet.json';original=packet_path.read_bytes()
    r.recover()
    assert r.q.status()['tasks'][0]['status']=='COMPLETE'
    assert calls==['continuation','review','disposition']
    r.bookkeeping()
    report=json.loads((packet_path.parent/'report.json').read_text())['id']
    assert Queue(r.state/'reports').status(report)['status']=='REVIEWED'
    review=json.loads((r.state/'reports'/(report+'.claude-review.json')).read_bytes())
    assert review['source']=='a'*40 and review['model']=='claude-fable-5'
    assert packet_path.read_bytes()==original
    assert r.q.tick()['status']=='WAITING_FOR_ELIGIBLE_WORK'
    assert calls==['continuation','review','disposition']
    with pytest.raises(ValueError,match='HISTORICAL_REPORT_SOURCE_READ_ONLY'):r.admit(binding)
    with pytest.raises(ValueError,match='HISTORICAL_REPORT_SOURCE_READ_ONLY'):r.model(binding,0)


def test_incomplete_old_report_and_changed_protected_reply_remain_blocked(tmp_path,monkeypatch):
    r,binding,replies,calls=historical_report_fixture(tmp_path,monkeypatch)
    r.q.db.execute('DELETE FROM stages WHERE task=? AND position=2',(binding['id'],))
    r.recover()
    assert calls==[]
    assert r.q.status()['tasks'][0]['reason']=='HISTORICAL_STAGES_INCOMPLETE_NO_RETRY'
    r.q.db.execute("INSERT INTO stages VALUES(?,2,'COMPLETE',NULL)",(binding['id'],))
    replies['review']['packet_sha256']='d'*64
    r.recover()
    assert r.q.status()['tasks'][0]['status']=='BLOCKED'
    assert calls==['continuation','review']


def test_changed_old_report_content_refuses_before_original_retrieval(tmp_path,monkeypatch):
    r,binding,replies,calls=historical_report_fixture(tmp_path,monkeypatch)
    report=json.loads((r.state/'tasks'/binding['id']/'report.json').read_bytes())['id']
    (r.state/'reports'/(report+'.md')).write_text('Changed report')
    r.recover()
    assert calls==[] and r.q.status()['tasks'][0]['status']=='BLOCKED'


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
    monkeypatch.setattr(module,'configuration',lambda path,**kwargs:requests[str(path)])
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


def test_explicit_reviewer_evidence_is_part_of_task_identity(tmp_path,monkeypatch):
    r=runtime(tmp_path,monkeypatch)
    first=r.enqueue_report('2026-09-06',[],{},reviewer_evidence={'observation':'unavailable'})
    second=r.enqueue_report('2026-09-06',[],{},reviewer_evidence={'observation':'configured only'})
    assert first['id']!=second['id']
    packet=json.loads((r.state/'tasks'/first['id']/'packet.json').read_text())
    assert packet['reviewer_evidence']=={'observation':'unavailable'}


def test_prompt_rejects_corrupted_predecessor_before_broker(tmp_path,monkeypatch):
    import pytest
    import orchestrator.handover_runtime as module
    r=runtime(tmp_path,monkeypatch);binding=r.enqueue_report('2026-09-07',[],{})
    (r.state/(binding['id']+'-0.json')).write_text(json.dumps({
        'binding':'wrong','position':0,'output':{'answer':'changed'},'output_sha256':'wrong'}))
    monkeypatch.setattr(module,'request_broker',lambda *args:pytest.fail('broker must not be called'))
    with pytest.raises(ValueError,match='STAGE_RECEIPT_CHANGED'):
        r.model(binding,1)



def test_report_task_history_is_bounded_with_honest_omission_count(tmp_path,monkeypatch):
    from datetime import datetime,timezone
    import orchestrator.handover_runtime as module
    r=runtime(tmp_path,monkeypatch)
    for n in range(220):
        r.q.db.execute('INSERT INTO tasks VALUES(?,?,?,?)',(format(n,'064x'),'{}','COMPLETE',None))
    r.config['report_schedule']={'zone':'UTC','hour':0,'minute':0,'evidence_file':'synthetic'}
    monkeypatch.setattr(module,'configuration',lambda path,**kwargs:{'source':'a'*40,'receipts':[],'task_state':{}})
    scheduled=r.scheduled_report(datetime(2026,9,7,tzinfo=timezone.utc))
    packet=json.loads((r.state/'tasks'/scheduled['task']/'packet.json').read_text())
    state=packet['decision_inbox']
    assert len(state['coordinator_tasks'])==24
    assert state['coordinator_tasks_total']==220 and state['coordinator_tasks_omitted']==196
    assert '220 complete' in state['coordinator_summary']


def test_bookkeeping_rejects_non_claude_identity_and_keeps_prior_recovery_reason(tmp_path,monkeypatch):
    import pytest
    import orchestrator.handover_runtime as module
    r=runtime(tmp_path,monkeypatch);binding=r.enqueue_report('2026-09-07',[],{});r.q.submit(binding)
    monkeypatch.setattr(r.q,'_receipt',lambda *args:{'output':{'receipt':{'actual_model':'different-family'},'answer':'Fixture review'}})
    with pytest.raises(ValueError,match='CLAUDE_REVIEW_MODEL_IDENTITY_REQUIRED'):
        r._bookkeep({'id':binding['id']})
    r.q.db.execute("UPDATE tasks SET status='BLOCKED',reason='ORIGINAL_FAILURE_PRESERVED'")
    def failed(*args):raise OSError('Synthetic retrieval failure')
    monkeypatch.setattr(r.q,'recover',failed)
    r.recover()
    assert r.q.status()['tasks'][0]['reason']=='ORIGINAL_FAILURE_PRESERVED'


def test_operator_transport_uses_fixed_runuser_outside_scrubbed_path(tmp_path,monkeypatch):
    import types,pwd
    import orchestrator.handover_runtime as module
    monkeypatch.setattr(module.os,'getuid',lambda:0)
    monkeypatch.setattr(pwd,'getpwuid',lambda uid:types.SimpleNamespace(pw_name='research-controller'))
    monkeypatch.setattr(module,'checked_source',lambda *args:None)
    def execute(command,**kwargs):
        assert command[0]=='/usr/sbin/runuser'
        assert 'PATH=/usr/bin:/bin' in command and command[-1]=='status'
        return types.SimpleNamespace(stdout=b'{"revision":2,"paused":false}')
    monkeypatch.setattr(module.subprocess,'run',execute)
    assert module.controller_command({'controller_uid':997,'source_root':'/fixed','source':'a'*40},'status')['revision']==2
