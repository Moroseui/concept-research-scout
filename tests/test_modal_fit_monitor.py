"""Real executor/accounting/provider connection; synthetic SDK/data/clock only."""
import json
import pytest
from test_modal_fit_result import connection
from test_modal_item4_provider import candidate
from test_modal_fit_health import health
from test_modal_item4_budget import bound, snapshot, NOW
from orchestrator import private_records, connectivity
from orchestrator.modal_executor import ModalExecutor, item4_job, canonical
from orchestrator.manual_executor import digest, read
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_item4_budget import AUTHORITY


@pytest.fixture
def monitored(health,tmp_path,monkeypatch):
    progress,binding,provider,sandbox,commits,log,path=health
    selected=bound('fit');binding.update({k:v for k,v in selected.items() if k!='run_id'})
    batch=BatchAccounts(tmp_path/'batch')
    batch.register_run('run',{'backlog_item':4,'experiment_authority_sha256':AUTHORITY})
    private_records.mkdir(tmp_path/'lane')
    # The shared monitor/continuation fixture includes its frozen synthetic
    # plan at the common dispatcher boundary, even though the old load() is
    # mocked. It has no preprocessing prerequisite. Production stays strict.
    fit=binding['progress']['fit_binding']
    plan={'synthetic_fixture':True,'fits':[{'fit_id':binding['experiment']['fit_id'],
        'stage':binding['experiment']['stage'],**{k:fit[k] for k in ('arm','fold','realization')},
        'outputs':binding['outputs'],'validation_checks':['synthetic-check']}]}
    private_records.write_bytes(tmp_path/'lane/experiment-package/execution-plan.json',canonical(plan))
    executor=ModalExecutor(tmp_path/'lane/jobs.sqlite',{},provider,batch)
    job=item4_job(binding);ident=digest(canonical(binding));executor.register(job,binding)
    assert executor.costs.reserve_item4(ident,'run',binding,billing_snapshot=snapshot(),now=NOW)
    executor.costs.observe(ident,'CREATED','sb-fit');executor.costs.observe(ident,'RUNNING','sb-fit')
    work=executor._paths(job);private_records.mkdir(work,parents=True)
    private_records.write_bytes(work/'created.json',canonical({'provider_id':'sb-fit','binding_sha256':ident}))
    # Network itself is absent from the deterministic fixture; guards stay real.
    monkeypatch.setattr(connectivity,'require',lambda *a,**k:None)
    clock=iter([1000,1901,1961,1962]);native=provider.fit_health
    provider.fit_health=lambda i,b,p:native(i,b,p,now=next(clock))
    stops=[]
    def terminate(wait):
        assert wait is True;stops.append('sb-fit');sandbox.poll=lambda:137
    sandbox.terminate=terminate
    return executor,job,ident,binding,path,stops,log,progress,sandbox


def advance_to_stop(m):
    executor,job,_,_,path,*_=m
    assert executor.monitor_fit(job,path)['status']=='OBSERVE'
    assert executor.monitor_fit(job,path)['status']=='OBSERVE'
    return executor.monitor_fit(job,path)


def test_real_monitor_stop_terminal_checkpoint_charge_and_duplicate_connection(monitored):
    e,j,ident,binding,path,stops,_,_,_=monitored
    amount=e.costs.db.execute('SELECT reserved_micro_usd FROM autonomy_compute WHERE id=?',(ident,)).fetchone()[0]
    result=advance_to_stop(monitored)
    assert result['status']=='INTERRUPTED_CHECKPOINT_PRESERVED' and result['may_launch'] is False
    assert stops==['sb-fit']
    row=e.costs.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
    assert row['status']=='ACCOUNTED' and row['reserved_micro_usd']==amount
    proof=json.loads(e.costs.db.execute('SELECT payload FROM events WHERE id=?',(ident+':fit-interruption',)).fetchone()[0])
    assert proof['resume_reason']=='OBSERVED_TRAINING_STALL'
    assert proof['proof']['terminal_exit_code']==137 and proof['proof']['may_launch'] is False
    before=[tuple(x) for x in e.costs.db.execute('SELECT * FROM autonomy_compute')]
    assert e.monitor_fit(j,path)['duplicate_observation'] is True
    assert stops==['sb-fit'] and [tuple(x) for x in e.costs.db.execute('SELECT * FROM autonomy_compute')]==before
    assert e.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    private_records.check_tree(e._paths(j)/'health')


def test_progress_on_immediate_recheck_cancels_stop(monitored):
    e,j,_,_,path,stops,log,_,_=monitored;original=e.provider.fit_health;calls=[]
    def read_progress(*args):
        calls.append(1)
        if len(calls)==4:
            with log.open('ab') as f:f.write(b'2026-10-06 06:19:00: Epoch 1 \n')
        return original(*args)
    e.provider.fit_health=read_progress
    result=advance_to_stop(monitored)
    assert result['status']=='OBSERVE' and result['stop_cancelled'] and stops==[]
    assert not (e._paths(j)/'health/stop-intent.json').exists()


def test_stop_transport_uncertainty_does_not_repeat_termination(monitored):
    e,j,_,_,path,stops,_,_,sandbox=monitored
    def fail(wait):stops.append('uncertain');raise TimeoutError('synthetic stop uncertainty')
    sandbox.terminate=fail
    with pytest.raises(TimeoutError):advance_to_stop(monitored)
    assert e.monitor_fit(j,path)['status']=='STOP_INTENT_RECONCILIATION_REQUIRED'
    assert stops==['uncertain']


@pytest.mark.parametrize('kind',['read-error','wrong-binding','halt','changed-history'])
def test_failed_observation_or_guard_never_stops_or_relaunches(monitored,kind):
    e,j,ident,b,path,stops,_,_,_=monitored
    e.monitor_fit(j,path)
    if kind=='read-error':
        def fail(*a):raise TimeoutError('synthetic network')
        e.provider.fit_health=fail
    elif kind=='wrong-binding':
        p=e._paths(j)/'created.json';v=read(p);v['binding_sha256']='0'*64;private_records.write_bytes(p,canonical(v))
    elif kind=='halt':private_records.write_bytes(e.path.parent/'HALT',b'synthetic operator stop')
    else:
        p=e._paths(j)/'health/observation-000001.json';v=read(p);v['assessment']['action']='RECHECK_BEFORE_STOP';private_records.write_bytes(p,canonical(v))
    with pytest.raises((TimeoutError,ValueError)):e.monitor_fit(j,path)
    assert not stops and e.costs.db.execute('SELECT status FROM autonomy_compute WHERE id=?',(ident,)).fetchone()[0]=='RUNNING'


def test_verified_stall_qualifies_same_fit_segment_resume_not_new_realization(monitored):
    e,j,ident,b,path,stops,_,_,_=monitored;advance_to_stop(monitored)
    raw=e.costs.db.execute('SELECT payload FROM events WHERE id=?',(ident+':fit-interruption',)).fetchone()[0]
    old=json.loads(raw);successor=json.loads(canonical(b));successor['experiment']['segment']=2
    successor['resume']={'previous_segment_id':ident,'terminal_receipt_sha256':digest(raw.encode()),
                         'checkpoint_record_sha256':old['proof']['checkpoint_record_sha256']}
    new=digest(canonical(successor))
    assert e.costs.reserve_item4(new,'run',successor,billing_snapshot=snapshot(),now=NOW)
    assert e.costs.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==2
    assert e.costs.db.execute('SELECT reserved_micro_usd FROM autonomy_compute WHERE id=?',(ident,)).fetchone()[0]==b['cost']['reserved_micro_usd']
    assert stops==['sb-fit'] # reservation did not launch or repeat any fit


def test_real_registered_path_drives_monitor_without_guessed_log_name(monitored):
    e,j,ident,b,path,stops,log,progress,_=monitored
    with progress.writer(initial=False):progress.training_log(log,segment=b['experiment']['segment'])
    assert e.monitor_fit(j)['status']=='OBSERVE'
    assert e.monitor_fit(j)['status']=='OBSERVE'
    assert e.monitor_fit(j)['status']=='INTERRUPTED_CHECKPOINT_PRESERVED'
    assert stops==['sb-fit']


def test_registration_disappearance_after_progress_refuses_instead_of_startup(monitored):
    e,j,_,b,_,stops,log,progress,_=monitored
    with progress.writer(initial=False):progress.training_log(log,segment=b['experiment']['segment'])
    assert e.monitor_fit(j)['status']=='OBSERVE'
    (progress.root/('training-log-'+str(b['experiment']['segment'])+'.json')).unlink() # Synthetic only.
    with pytest.raises(ValueError,match='^FIT_MONITOR_PROGRESS_DISAPPEARED$'):e.monitor_fit(j)
    assert stops==[]


def test_dispatcher_reaches_real_monitor_terminal_checkpoint_and_accounting(monitored,monkeypatch):
    """Only prior scientific selection, SDK and clock are synthetic. Actual
    dispatcher, monitor, terminal checkpoint reader and ledger transaction run."""
    from types import SimpleNamespace as NS
    from orchestrator import experiment_dispatch as dispatch
    e,j,ident,b,_,stops,log,progress,_=monitored
    with progress.writer(initial=False):progress.training_log(log,segment=b['experiment']['segment'])
    selected={'sha256':'a'*64,'jobs':[{'job':j,'runtime':{},'binding':b}]}
    monkeypatch.setattr(dispatch,'load',lambda *args:selected)
    # remote_status's result is a deterministic status fixture; the monitor
    # independently calls the connected provider and verifies its checkpoint.
    proxy=NS(db=NS(close=lambda:None),remote_status=lambda job:{'status':'RUNNING'},monitor_fit=e.monitor_fit)
    monkeypatch.setattr(dispatch,'executor',lambda *args:proxy)
    value={'phase':'EXECUTE_EXPERIMENT','fit_dispatch':{j:{'phase':'RUNNING'}}};saves=[]
    d=NS(state=e.path.parent,status=lambda:{'phase':value['phase']},save=lambda v:saves.append(json.loads(json.dumps(v))))
    dispatch.advance(d,value);dispatch.advance(d,value)
    assert dispatch.advance(d,value)['next_action']=='RECONCILE_FIT_CONTINUATION'
    assert value['fit_dispatch'][j]['phase']=='INTERRUPTED' and stops==['sb-fit']
    row=e.costs.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
    assert row['status']=='ACCOUNTED' and row['reserved_micro_usd']==b['cost']['reserved_micro_usd']
    before=[tuple(r) for r in e.costs.db.execute('SELECT * FROM autonomy_compute')]
    assert e.monitor_fit(j)['duplicate_observation'] is True
    assert before==[tuple(r) for r in e.costs.db.execute('SELECT * FROM autonomy_compute')]
    assert stops==['sb-fit'] and e.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
