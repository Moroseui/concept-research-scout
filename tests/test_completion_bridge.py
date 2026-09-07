"""Real synthetic child execution with fixture model receipts, never real models."""
import json
from pathlib import Path
import shutil

from orchestrator.remote_supervisor import worker,SMOKE
from test_handover_runtime import runtime


def configured(tmp_path,monkeypatch,pairs=None):
    import orchestrator.completion_bridge as module
    import orchestrator.remote_supervisor as supervisor
    r=runtime(tmp_path,monkeypatch)
    source=tmp_path/'execution-source';(source/SMOKE).parent.mkdir(parents=True)
    shutil.copyfile(Path(__file__).resolve().parents[1]/SMOKE,source/SMOKE)
    monkeypatch.setattr(module,'checked_source',lambda root,pin:Path(root))
    monkeypatch.setattr(supervisor,'checked_source',lambda root,pin:Path(root))
    state=tmp_path/'execution-state';state.mkdir()
    requests=tmp_path/'requests';requests.mkdir()
    outputs=tmp_path/'outputs';outputs.mkdir()
    config={'authority':'OPERATOR_SUPERVISED_SYNTHETIC_ONLY','source':'a'*40,
        'source_root':str(source),'state':str(state),'outputs':str(outputs),
        'pairs':pairs or {'predecessor':'successor'}}
    r.completions=module.CompletionBridge(r,config)
    return r,state,requests,outputs,source


def execute(r,state,requests,outputs,source):
    controller=r.completions.controller
    controller.tick(state,requests,outputs,source,'a'*40)
    worker(requests,outputs,source,'a'*40)
    controller.tick(state,requests,outputs,source,'a'*40)


def handlers(r,*,decline=False):
    calls=[]
    def model(binding,position):
        calls.append((binding['id'],position))
        packet=json.loads((r.state/'tasks'/binding['id']/'packet.json').read_text())
        proposal=packet.get('execution_proposal')
        answer='Fixture assessment; not an actual model call.'
        if position==2 and proposal:
            answer=json.dumps({'task_id':None if decline else proposal['job'],'reason':'Fixture review disposition.'})
        return {'status':'COMPLETE','answer':answer,
                'receipt':{'actual_model':'claude-fable-5','session_id':'synthetic-fixture-only'}}
    r.q.handlers={name:model for name in ('continuation','review','disposition')}
    r.q.admission=lambda b:{'status':'ADMITTED'}
    return calls


def test_completion_selects_one_successor_and_reconciles_lost_submit_response(tmp_path,monkeypatch):
    r,state,requests,outputs,source=configured(tmp_path,monkeypatch)
    controller=r.completions.controller;controller.submit('predecessor','a'*40)
    execute(r,state,requests,outputs,source)
    calls=handlers(r)
    r.completions.ingest();r.completions.ingest()
    assert len(r.q.status()['tasks'])==1
    assert r.q.tick()['status']=='COMPLETE'
    submit=controller.submit;lost=[False]
    def response_lost(*args):
        submit(*args)
        if not lost[0]:lost[0]=True;raise OSError('synthetic lost submission response')
    monkeypatch.setattr(controller,'submit',response_lost)
    r.bookkeeping()
    assert controller.get('successor')['status']=='READY'
    # The actual child can finish while local submission bookkeeping is pending.
    execute(r,state,requests,outputs,source)
    r.completions.advance();r.bookkeeping();r.bookkeeping()
    assert controller.db.execute("SELECT count(*) FROM linux_attempts WHERE job='successor'").fetchone()[0]==1
    assert r.q.db.execute('SELECT status FROM selected_dispatch').fetchone()[0]=='SUBMITTED'
    r.completions.ingest();r.completions.ingest()
    assert len(r.q.status()['tasks'])==2
    assert r.q.tick()['status']=='COMPLETE'
    r.bookkeeping();r.completions.ingest()
    assert len(calls)==6
    assert r.q.tick()['status']=='WAITING_FOR_ELIGIBLE_WORK'
    assert controller.db.execute("SELECT count(*) FROM wakes WHERE status='PROCESSED'").fetchone()[0]==2


def test_investigator_can_decline_without_dispatch_or_losing_review(tmp_path,monkeypatch):
    r,state,requests,outputs,source=configured(tmp_path,monkeypatch)
    r.completions.controller.submit('predecessor','a'*40)
    execute(r,state,requests,outputs,source);handlers(r,decline=True)
    r.completions.ingest();r.q.tick();r.bookkeeping()
    assert r.q.db.execute('SELECT status FROM selected_dispatch').fetchone()[0]=='DECLINED'
    assert not r.completions.controller.db.execute("SELECT 1 FROM jobs WHERE id='successor'").fetchone()
    assert r.q.db.execute('SELECT status FROM bookkeeping').fetchone()[0]=='COMPLETE'


def test_bad_console_does_not_block_other_configured_completion(tmp_path,monkeypatch):
    r,state,requests,outputs,source=configured(tmp_path,monkeypatch,{'bad':'bad-next','good':'good-next'})
    controller=r.completions.controller
    for name in ('bad','good'):
        controller.submit(name,'a'*40);execute(r,state,requests,outputs,source)
    attempt=controller.db.execute("SELECT id FROM linux_attempts WHERE job='bad'").fetchone()[0]
    (outputs/attempt/'console-0.stdout').write_text('Changed fixture original')
    r.completions.ingest()
    assert len(r.q.status()['tasks'])==1
    assert r.q.db.execute('SELECT job FROM completion_ingest').fetchone()[0]=='good'
    assert r.q.db.execute('SELECT job FROM completion_blocks').fetchone()[0]=='bad'


def test_pause_holds_selected_work_until_explicit_resume(tmp_path,monkeypatch):
    r,state,requests,outputs,source=configured(tmp_path,monkeypatch)
    controller=r.completions.controller;controller.submit('predecessor','a'*40)
    execute(r,state,requests,outputs,source);calls=handlers(r)
    r.completions.ingest();r.q.tick()
    r.q.control({'id':'pause','expected_revision':0,'action':'pause'},authenticated_operator=True)
    r.bookkeeping();r.completions.advance()
    assert r.q.db.execute('SELECT status FROM selected_dispatch').fetchone()[0]=='INTENT'
    assert not controller.db.execute("SELECT 1 FROM jobs WHERE id='successor'").fetchone()
    r.q.control({'id':'resume','expected_revision':1,'action':'resume'},authenticated_operator=True)
    r.completions.advance();r.completions.advance()
    assert controller.get('successor')['status']=='READY'
    assert len(calls)==3


def test_submission_errors_have_a_durable_retry_ceiling(tmp_path,monkeypatch):
    r,state,requests,outputs,source=configured(tmp_path,monkeypatch)
    controller=r.completions.controller;controller.submit('predecessor','a'*40)
    execute(r,state,requests,outputs,source);handlers(r)
    r.completions.ingest();r.q.tick()
    attempted=[]
    def fail(*args):attempted.append(1);raise OSError('fixture submission unavailable')
    monkeypatch.setattr(controller,'submit',fail)
    r.bookkeeping()
    for _ in range(6):r.completions.advance()
    assert len(attempted)==3
    row=r.q.db.execute('SELECT status,attempts FROM selected_dispatch').fetchone()
    assert tuple(row)==('BLOCKED',3)


def test_sqlite_submission_failure_is_capped_and_visible(tmp_path,monkeypatch):
    import sqlite3
    r,state,requests,outputs,source=configured(tmp_path,monkeypatch)
    controller=r.completions.controller;controller.submit('predecessor','a'*40)
    execute(r,state,requests,outputs,source);handlers(r)
    r.completions.ingest();r.q.tick()
    def unavailable(*args):raise sqlite3.OperationalError('synthetic execution database unavailable')
    monkeypatch.setattr(controller,'submit',unavailable)
    r.bookkeeping()
    for _ in range(5):r.completions.advance()
    assert tuple(r.q.db.execute('SELECT status,attempts FROM selected_dispatch').fetchone())==('BLOCKED',3)


def test_report_retry_reuses_first_observation_and_original_report(tmp_path,monkeypatch):
    import sqlite3
    import orchestrator.completion_bridge as module
    r,state,requests,outputs,source=configured(tmp_path,monkeypatch)
    r.completions.controller.submit('predecessor','a'*40)
    execute(r,state,requests,outputs,source)
    collect=module.collect;observations=[]
    def counted(*args,**kwargs):observations.append(1);return collect(*args,**kwargs)
    monkeypatch.setattr(module,'collect',counted)
    submit=r.q.submit;failed=[False]
    def fail_once(binding):
        if not failed[0]:failed[0]=True;raise sqlite3.OperationalError('fixture before coordinator commit')
        return submit(binding)
    monkeypatch.setattr(r.q,'submit',fail_once)
    r.completions.ingest()
    assert r.q.status()['tasks']==[]
    reports=list((r.state/'reports').glob('*.md'))
    r.completions.ingest()
    assert len(observations)==1 and len(r.q.status()['tasks'])==1
    assert list((r.state/'reports').glob('*.md'))==reports
