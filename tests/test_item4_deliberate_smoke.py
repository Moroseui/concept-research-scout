"""Real checkpoint, termination and SQLite accounting; synthetic SDK and data."""
import copy
import json
from types import SimpleNamespace as NS
import pytest
from test_modal_fit_monitor import monitored
from test_modal_fit_health import health
from test_modal_fit_result import connection
from test_modal_item4_provider import candidate
from orchestrator import item4_deliberate_smoke as stop, private_records as pr
from orchestrator.modal_executor import canonical
from orchestrator.modal_provider import ModalProvider
from orchestrator.manual_executor import digest
from orchestrator.modal_fit_progress import encoded

@pytest.fixture
def connected(monitored,monkeypatch):
    e,j,ident,b,path,stops,log,progress,sandbox=monitored
    with progress.writer(initial=False):
        progress.publish('latest',lambda p:p.write_bytes(b'synthetic partial checkpoint'),
            metadata={'next_epoch':1,'total_epochs':5,'native_version':'2.8.1'})
        progress.training_log(log,segment=b['experiment']['segment'])
    e.provider.fit_health=lambda pid,binding:ModalProvider.fit_health(e.provider,pid,binding,now=1000)
    # Production scope is separately tested with its real immutable source pins.
    monkeypatch.setattr(stop,'scope',lambda binding:None)
    raw=canonical({'binding':b})
    pr.write_bytes(e.path.parent/'fit-packages'/j/'prepared/manifest.json',raw)
    value={'phase':'EXECUTE_EXPERIMENT','fit_dispatch':{j:{'phase':'RUNNING','manifest_sha256':digest(raw)}}}
    saves=[]
    driver=NS(state=e.path.parent,config={'run_id':b['run_id']},save=lambda v:saves.append(copy.deepcopy(v)),status=lambda:{'phase':value['phase']})
    return monitored,driver,value,{'job':j,'binding':b},saves


def execute(connected):
    m,d,v,j,_=connected
    return stop.run(d,v,j,m[0])


def test_real_checkpoint_stop_and_idempotent_accounting(connected):
    m,d,v,j,saves=connected;e,job,ident,b,path,stops,*_=m
    before=[tuple(x) for x in e.costs.db.execute('SELECT * FROM autonomy_compute')]
    result=execute(connected)
    assert result['epoch_resumed_from']==1 and result['next_action']=='RECONCILE_FIT_CONTINUATION'
    assert v['fit_dispatch'][job]['phase']=='INTERRUPTED' and stops==['sb-fit']
    row=e.costs.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
    assert row['status']=='ACCOUNTED' and row['reserved_micro_usd']==b['cost']['reserved_micro_usd']
    proof=json.loads(e.costs.db.execute('SELECT payload FROM events WHERE id=?',(ident+':fit-interruption',)).fetchone()[0])
    assert proof['resume_reason']=='DELIBERATE_SMOKE_INTERRUPTION'
    assert proof['proof']['terminal_exit_code']==137 and proof['proof']['may_launch'] is False
    assert proof['proof']['checkpoint_record_sha256']==digest(encoded(proof['proof']['checkpoint_record']))
    accounted=[tuple(x) for x in e.costs.db.execute('SELECT * FROM autonomy_compute')]
    assert execute(connected)['epoch_resumed_from']==1
    assert stops==['sb-fit'] and accounted==[tuple(x) for x in e.costs.db.execute('SELECT * FROM autonomy_compute')]
    assert e.costs.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==len(before)==1
    assert e.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    pr.check_tree(e._paths(job)/'deliberate-stop')


def test_uncertain_stop_is_never_repeated(connected):
    m,*_=connected;e,j,ident,b,path,stops,log,progress,sandbox=m
    def uncertain(wait):stops.append('uncertain');raise TimeoutError('synthetic')
    sandbox.terminate=uncertain
    with pytest.raises(TimeoutError):execute(connected)
    with pytest.raises(ValueError,match='STOP_INTENT_RECONCILIATION_REQUIRED'):execute(connected)
    assert stops==['uncertain']
    assert e.costs.db.execute('SELECT status FROM autonomy_compute WHERE id=?',(ident,)).fetchone()[0]=='RUNNING'


@pytest.mark.parametrize('kind',['halt','created','prepared','wrong-observation','checkpoint-corrupt','terminal','completed','wrong-total','final'])
def test_refusals_do_not_admit_or_account(connected,kind):
    m,d,v,j,_=connected;e,job,ident,b,path,stops,log,progress,sandbox=m
    if kind=='halt':pr.write_bytes(e.path.parent/'HALT',b'synthetic')
    elif kind=='created':
        p=e._paths(job)/'created.json';x=json.loads(p.read_bytes());x['binding_sha256']='0'*64;pr.write_bytes(p,canonical(x))
    elif kind=='prepared':v['fit_dispatch'][job]['manifest_sha256']='0'*64
    elif kind=='wrong-observation':
        native=e.provider.fit_health
        def wrong(*args):x=native(*args);x['provider_id']='sb-other';return x
        e.provider.fit_health=wrong
    elif kind=='checkpoint-corrupt':
        cp=json.loads((progress.root/'latest.json').read_bytes())
        (progress.root/'objects'/cp['object']/'data').write_bytes(b'corrupt synthetic checkpoint')
    elif kind=='terminal':sandbox.poll=lambda:137
    else:
        with progress.writer(initial=False):
            progress.publish('final' if kind=='final' else 'latest',lambda p:p.write_bytes(b'synthetic'),metadata={
                'next_epoch':5 if kind in {'completed','final'} else 1,'total_epochs':6 if kind=='wrong-total' else 5,'native_version':'2.8.1'})
    with pytest.raises(ValueError):execute(connected)
    assert stops==(['sb-fit'] if kind=='checkpoint-corrupt' else [])
    assert e.costs.db.execute('SELECT status FROM autonomy_compute WHERE id=?',(ident,)).fetchone()[0]=='RUNNING'
    assert e.costs.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==1
    assert e.costs.db.execute('SELECT count(*) FROM events WHERE id=?',(ident+':fit-interruption',)).fetchone()[0]==0


def test_checkpoint_drift_between_read_and_accounting_refuses(connected):
    m,*_=connected;e,j,ident,b,path,stops,log,progress,sandbox=m
    native=e.provider.terminal_fit_checkpoint;calls=[]
    def changed(*args):
        calls.append(1)
        if len(calls)==2:
            with progress.writer(initial=False):
                progress.publish('latest',lambda p:p.write_bytes(b'another synthetic checkpoint'),metadata={'next_epoch':2,'total_epochs':5,'native_version':'2.8.1'})
        return native(*args)
    e.provider.terminal_fit_checkpoint=changed
    with pytest.raises(ValueError,match='ITEM4_INTERRUPTION_CHECKPOINT_CHANGED'):execute(connected)
    assert stops==['sb-fit'] and len(calls)==2
    assert e.costs.db.execute('SELECT status FROM autonomy_compute WHERE id=?',(ident,)).fetchone()[0]=='RUNNING'


def test_zero_epoch_and_transport_wait_reuse_one_deadline(connected,monkeypatch):
    m,*_=connected;e,j,ident,b,path,stops,log,progress,sandbox=m
    clock=[1000.0];monkeypatch.setattr(stop.time,'time',lambda:clock[0])
    monkeypatch.setattr(stop.time,'sleep',lambda s:clock.__setitem__(0,clock[0]+s))
    monkeypatch.setattr(stop,'MAX_WAIT_SECONDS',10)
    native=e.provider.fit_health;calls=[]
    def pending(*args):
        calls.append(1)
        if len(calls)==1:raise TimeoutError('synthetic')
        result=native(*args);result['checkpoint']['next_epoch']=0;return result
    e.provider.fit_health=pending
    with pytest.raises(ValueError,match='DEADLINE_RECONCILE'):execute(connected)
    assert len(calls)==2 and not stops
    with pytest.raises(ValueError,match='DEADLINE_RECONCILE'):execute(connected)
    assert len(calls)==2 and not stops
    recorded=json.loads((e._paths(j)/'deliberate-stop/observation-000001.json').read_bytes())
    assert recorded['error_type']=='TimeoutError' and 'synthetic' not in str(recorded)


@pytest.mark.parametrize('change',['traversal','schema','epoch','hash','unknown'])
def test_stop_intent_cannot_redirect_evidence(connected,change):
    m,*_=connected;e,j,ident,b,path,stops,*_=m;execute(connected)
    p=e._paths(j)/'deliberate-stop/stop-intent.json';value=json.loads(p.read_bytes())
    if change=='traversal':value['observation']='../created.json'
    elif change=='schema':value['schema']='other'
    elif change=='epoch':value['completed_epoch']=2
    elif change=='hash':value['observation_sha256']='0'*64
    else:value['extra']=True
    pr.write_bytes(p,canonical(value))
    with pytest.raises(ValueError):execute(connected)
    assert stops==['sb-fit']


def test_exact_frozen_scope_and_resume_exclusion():
    from test_item4_stage1_cap import selected
    b=selected();b['run_id']=stop.cap.RUN;b['experiment'].update(fit_id=stop.FIT,stage='SMOKE',segment=1)
    b['resources'].update(gpu='B200')
    stop.scope(b)
    for key,value in [('run_id','other'),('resume',{}),('resources',dict(b['resources'],gpu='H100'))]:
        other=copy.deepcopy(b);other[key]=value
        if key=='resume':other[key]={'checkpoint':'synthetic'}
        with pytest.raises(ValueError):stop.scope(other)
    for segment in [2,3]:
        other=copy.deepcopy(b);other['experiment']['segment']=segment
        assert not stop.target(other)
    other=copy.deepcopy(b);other['experiment']['fit_id']='smoke-A1_repeat2'
    assert not stop.target(other)


def test_dispatch_running_reaches_connected_control(connected,monkeypatch):
    from orchestrator import experiment_dispatch as dispatch
    m,d,v,j,_=connected;e,job,ident,b,path,stops,*_=m
    monkeypatch.setattr(dispatch,'load',lambda *a:{'sha256':'a'*64,'jobs':[j]})
    monkeypatch.setattr(stop,'target',lambda binding:True)
    proxy=NS(**{k:getattr(e,k) for k in ['path','_guard','get','_paths','costs','provider']},db=NS(close=lambda:None))
    monkeypatch.setattr(dispatch,'executor',lambda *a:proxy)
    assert dispatch.advance(d,v)['epoch_resumed_from']==1
    assert v['fit_dispatch'][job]['phase']=='INTERRUPTED' and stops==['sb-fit']


def test_submit_starts_stop_control_before_returning_to_host(connected,monkeypatch):
    from orchestrator import experiment_dispatch as dispatch, experiment_preprocessing_dispatch as prep
    m,d,v,j,_=connected;e,job,ident,b,path,stops,*_=m
    v['fit_dispatch'][job]['phase']='SUBMIT'
    monkeypatch.setattr(dispatch,'load',lambda *a:{'sha256':'a'*64,'jobs':[j]})
    monkeypatch.setattr(stop,'target',lambda binding:True)
    monkeypatch.setattr(prep,'advance',lambda *a:None)
    manifest={'binding':b}
    monkeypatch.setattr(dispatch.bridge,'emit',lambda *a:manifest)
    order=[]
    proxy=NS(**{k:getattr(e,k) for k in ['path','_guard','get','_paths','costs','provider']},db=NS(close=lambda:order.append('close')))
    def submit(*args):order.append('submit');return {'status':'SUBMITTED'}
    proxy.submit=submit
    monkeypatch.setattr(dispatch,'executor',lambda *a:proxy)
    def save(value):order.append('save:'+value['fit_dispatch'][job]['phase'])
    d.save=save
    assert dispatch.advance(d,v)['epoch_resumed_from']==1
    assert order==['submit','close','save:RUNNING','save:INTERRUPTED','close']
    assert stops==['sb-fit']
