"""Real item4 executor/job/accounting; synthetic paid provider, no real calls."""
import json
import pytest
from orchestrator import private_records as pr
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest,read
from test_modal_executor import setup,item4_dispatch,make_item4_package,private_test_environment


def test_failed_fit_stops_once_preserves_cost_blocks_and_never_collects(item4_dispatch):
    e,p,b,run=item4_dispatch;args=make_item4_package(item4_dispatch);e.submit(*args)
    ident=digest(canonical(args[1]));before=dict(b.db.execute('SELECT * FROM autonomy_compute').fetchone())
    p.state='FAILED'
    result=e.remote_status(args[0]);assert result['status']=='FAILED' and result['cleanup']=='TERMINATED_FAILURE_PRESERVED'
    work=e._paths(args[0]);original=(work/'failed-outcome.json').read_bytes()
    after=dict(b.db.execute('SELECT * FROM autonomy_compute').fetchone())
    assert after==dict(before,status='UNCERTAIN')
    assert e.get(args[0])['status']=='BLOCKED'
    assert e.remote_status(args[0])==result and e.submit(*args)==result
    called=[]
    assert e.collect_remote(args[0],args[3],e.path.parent/'results',lambda p:called.append(p))==result
    assert called==[] and 'collect' not in p.calls
    assert p.calls.count('create')==p.calls.count('launch')==p.calls.count('terminate')==1
    assert (work/'failed-outcome.json').read_bytes()==original
    assert b.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==1
    assert b.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    pr.check_tree(work)


def test_uncertain_stop_is_not_reissued_or_mistaken_for_success(item4_dispatch):
    e,p,b,run=item4_dispatch;args=make_item4_package(item4_dispatch);e.submit(*args)
    p.state='FAILED';p.failure='terminate'
    with pytest.raises(TimeoutError):e.remote_status(args[0])
    work=e._paths(args[0]);assert (work/'failed-outcome.json').is_file() and (work/'failed-stop-intent.json').is_file()
    assert not (work/'failed-stopped.json').exists()
    p.failure=None
    for _ in range(3):assert e.remote_status(args[0])['cleanup']=='STOP_INTENT_RECONCILIATION_REQUIRED'
    assert p.calls.count('terminate')==1 and b.db.execute('SELECT status FROM autonomy_compute').fetchone()[0]=='UNCERTAIN'
    assert not (work/'terminated.json').exists()


@pytest.mark.parametrize('state',['RUNNING','UNKNOWN'])
def test_nonterminal_observation_never_triggers_failed_cleanup(item4_dispatch,state):
    e,p,b,run=item4_dispatch;args=make_item4_package(item4_dispatch);e.submit(*args);p.state=state
    assert e.remote_status(args[0])['status']==state
    assert 'terminate' not in p.calls and not (e._paths(args[0])/'failed-outcome.json').exists()
    assert b.db.execute('SELECT status FROM autonomy_compute').fetchone()[0]=='RUNNING'


def test_observation_timeout_remains_running_without_cleanup(item4_dispatch):
    e,p,b,run=item4_dispatch;args=make_item4_package(item4_dispatch);e.submit(*args);p.failure='status'
    assert e.remote_status(args[0])['status']=='OBSERVATION_UNAVAILABLE'
    assert 'terminate' not in p.calls and b.db.execute('SELECT status FROM autonomy_compute').fetchone()[0]=='RUNNING'


@pytest.mark.parametrize('target',['failure','intent','receipt','ledger','private'])
def test_changed_failure_bindings_refuse_without_new_operation(item4_dispatch,target):
    e,p,b,run=item4_dispatch;args=make_item4_package(item4_dispatch);e.submit(*args);p.state='FAILED';e.remote_status(args[0])
    work=e._paths(args[0]);before=list(p.calls)
    if target=='ledger':b.db.execute("UPDATE autonomy_compute SET provider_id='sb-different'")
    elif target=='private':(work/'failed-outcome.json').chmod(0o644)
    else:pr.write_text(work/{'failure':'failed-outcome.json','intent':'failed-stop-intent.json','receipt':'failed-stopped.json'}[target],'{}')
    with pytest.raises(ValueError):e.remote_status(args[0])
    assert p.calls==before


def test_legacy_m3_failure_semantics_unchanged(setup):
    e,p,b,run,binding,prepared,package=setup;e.submit(run,binding,prepared,package);p.state='FAILED'
    assert e.remote_status(run)['status']=='FAILED' and 'terminate' not in p.calls
    assert b.db.execute('SELECT status FROM autonomy_compute').fetchone()[0]=='RUNNING'


# Import the complete transitive fixture graph explicitly; pytest fixture lookup
# does not inherit fixtures merely because an imported function uses them.
from test_modal_item4_provider import candidate
from test_modal_fit_result import connection,proof_fixture


def test_real_input_guard_failure_reaches_executor_cleanup(connection,tmp_path):
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator.modal_executor import ModalExecutor,item4_job
    from orchestrator.modal_item4_budget import AUTHORITY,quote
    from test_modal_item4_budget import snapshot,NOW
    progress,binding,outputs,provider,sandbox,commits=connection
    binding['experiment']['stage']='SMOKE'
    bill=snapshot();binding['cost']=quote(binding['resources'],bill['rates'],binding['overhead_micro_usd'])
    # Binding changes are confined to the synthetic prior-dispatch fixture.
    proof_fixture(provider,binding,progress.mount)
    ident=digest(canonical(binding));path=progress.mount/'input-verification'/(ident+'.json')
    proof=read(path);proof.update(status='FAILED',reason='INPUT_GUARD_HASH');pr.write_bytes(path,canonical(proof));original=path.read_bytes()
    terminal=[None];stops=[];sandbox.poll=lambda:terminal[0]
    def stop(**kwargs):stops.append(kwargs);terminal[0]=143
    sandbox.terminate=stop
    batch=BatchAccounts(tmp_path/'failure-batch');batch.register_run('run',{'backlog_item':4,'experiment_authority_sha256':AUTHORITY})
    pr.mkdir(tmp_path/'failure-lane')
    e=ModalExecutor(tmp_path/'failure-lane/jobs.sqlite',provider.config,provider,batch)
    job=item4_job(binding);e.register(job,binding)
    assert e.costs.reserve_item4(ident,'run',binding,billing_snapshot=bill,now=NOW)
    e.costs.observe(ident,'CREATED','sb-fit');e.costs.observe(ident,'RUNNING','sb-fit')
    work=e._paths(job);pr.mkdir(work,parents=True)
    pr.write_bytes(work/'created.json',canonical({'provider_id':'sb-fit','binding_sha256':ident}))
    result=e.remote_status(job)
    assert result['status']=='FAILED' and result['cleanup']=='TERMINATED_FAILURE_PRESERVED'
    assert e.remote_status(job)==result and stops==[{'wait':True}]
    assert path.read_bytes()==original
    row=batch.db.execute('SELECT status,reserved_micro_usd FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
    assert row['status']=='UNCERTAIN' and row['reserved_micro_usd']==binding['cost']['reserved_micro_usd']
    assert not (e.path.parent/'collected').exists()
