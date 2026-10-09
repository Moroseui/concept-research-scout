"""Dispatch transitions: synthetic root provenance/assets, no SDK or paid work.

Real package approval/Modal admission have dedicated integration tests. These
checks exercise the new binding/transition connection and its external calls.
"""
import copy
import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import experiment_dispatch as dispatch, private_records as pr
from orchestrator.modal_executor import canonical, item4_job
from orchestrator.manual_executor import digest


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    state=tmp_path/'lane';root=tmp_path/'root-preserved';pr.mkdir(state);pr.mkdir(root)
    package=state/'experiment-package';pr.mkdir(package)
    sealed={'selection':{'item_number':4},'synthetic_fixture':True}
    pr.write_text(package/'manifest.json',json.dumps(sealed,separators=(',',':')))
    # Root identity and prior scientific seal are labelled synthetic fixtures.
    monkeypatch.setattr(dispatch,'trusted',lambda path:Path(path))
    monkeypatch.setattr(dispatch.experiment_package,'verify',lambda *args:sealed)
    runtime={'batch_ledger':str(tmp_path/'ledger'),'package_volume_id':'vo-package'}
    path=root/'runtime.json';pr.write_bytes(path,canonical(runtime))
    binding={'purpose':'M4_ITEM4','run_id':'synthetic-run','source':'a'*40,
        'runtime_sha256':digest(canonical(runtime)),
        'experiment':{'fit_id':'fit-one','segment':1,'stage':'SMOKE'},
        'progress':{'fit_binding':{'arm':'synthetic-arm','fold':0,'realization':'one'}},
        'outputs':['synthetic-result.json','validation.json']}
    fits=[{'fit_id':'fit-one','stage':'SMOKE','arm':'synthetic-arm','fold':0,'realization':'one',
        'outputs':['synthetic-result.json','validation.json'],'validation_checks':['synthetic-check']}]
    pr.write_bytes(package/'execution-plan.json',canonical({'fits':fits}))
    selection={'schema':'experiment-fit-dispatch/v1','source':'a'*40,'run_id':'synthetic-run',
        'package_manifest_sha256':digest((package/'manifest.json').read_bytes()),
        'jobs':[{'runtime':{'path':str(path),'sha256':digest(path.read_bytes())},'binding':binding}]}
    pr.write_bytes(root/'READY.json',canonical(selection))
    value={'phase':'EXECUTE_EXPERIMENT'};saves=[]
    d=NS(state=state,config={'source':'a'*40,'run_id':'synthetic-run','batch_ledger':runtime['batch_ledger'],
        'execution_provisioning':str(root)},save=lambda v:saves.append(copy.deepcopy(v)),
        status=lambda:{'phase':value['phase']})
    return d,value,root,selection,binding,saves


def test_full_provisioned_selection_binds_exact_raw_package_bytes(prepared):
    d,value,root,selection,binding,_=prepared
    result=dispatch.load(d,value)
    assert result['sha256']==digest((root/'READY.json').read_bytes())
    assert result['jobs'][0]['job']==item4_job(binding)
    value['dispatch_sha256']=result['sha256']
    assert dispatch.load(d,value)==result


@pytest.mark.parametrize('damage',['source','package','run','runtime','ledger','fit','outputs','duplicate','resume','changed-selection','unsafe','relative'])
def test_provisioning_drift_refuses_before_provider(prepared,damage):
    d,value,root,selection,binding,_=prepared
    if damage=='source':selection['source']='b'*40
    elif damage=='package':selection['package_manifest_sha256']='b'*64
    elif damage=='run':selection['run_id']='another'
    elif damage=='runtime':pr.write_text(root/'runtime.json','{}')
    elif damage=='ledger':d.config['batch_ledger']='other'
    elif damage=='fit':binding['progress']['fit_binding']['arm']='unselected'
    elif damage=='outputs':binding['outputs'].append('unreviewed.csv')
    elif damage=='duplicate':selection['jobs']*=2
    elif damage=='resume':binding['experiment']['segment']=2
    elif damage=='changed-selection':value['dispatch_sha256']='b'*64
    elif damage=='relative':selection['jobs'][0]['runtime']['path']='runtime.json'
    pr.write_bytes(root/'READY.json',canonical(selection))
    if damage=='unsafe':(root/'READY.json').chmod(0o644)
    with pytest.raises(ValueError):dispatch.load(d,value)
    assert 'fit_dispatch' not in value


def test_untrusted_provisioning_is_not_a_permission_to_launch(prepared,monkeypatch):
    def refuse(path):raise ValueError('HOST_PROOF_NOT_ROOT_OWNED')
    monkeypatch.setattr(dispatch,'trusted',refuse)
    with pytest.raises(ValueError,match='^HOST_PROOF_NOT_ROOT_OWNED$'):dispatch.load(*prepared[:2])


def test_missing_preparation_waits_without_model_or_provider(prepared):
    d,value,root,*_=prepared;(root/'READY.json').unlink() # Disposable fixture.
    result=dispatch.advance(d,value)
    assert result['provider_called'] is False and result['next_action']=='WAIT_EXECUTION_PREPARATION'
    assert value=={'phase':'EXECUTE_EXPERIMENT'}


@pytest.fixture
def external(prepared,monkeypatch):
    d,value,root,selection,binding,saves=prepared;events=[];remote={'status':'RUNNING'}
    manifest={'binding':dict(binding,package_volume_id='vo-package'),'synthetic_fixture':True}
    monkeypatch.setattr(dispatch.bridge,'emit',lambda *a:(events.append('package') or manifest))
    def uploaded(*a):
        events.append('upload')
        return {'status':'READY','manifest_sha256':digest(canonical(manifest)),'volume_id':'vo-package'}
    monkeypatch.setattr(dispatch,'prepare_package',uploaded)
    submissions={}
    class Store:
        provider=object()
        db=NS(close=lambda:None)
        def submit(self,job,binding,*args):
            events.append('submit')
            if job not in submissions:submissions[job]={'status':'SUBMITTED','job':job,'provider_id':'sb-synthetic'}
            return submissions[job]
        def remote_status(self,job):events.append('observe');return dict(remote)
        def monitor_fit(self,job):events.append('health');return {'status':'OBSERVE'}
    monkeypatch.setattr(dispatch,'executor',lambda *a:Store())
    return prepared,events,remote,submissions


def test_package_upload_submit_and_completion_are_separate_ticks(external):
    (d,value,_,_,binding,saves),events,remote,submissions=external
    dispatch.advance(d,value);assert events==['package']
    dispatch.advance(d,value);assert events[-2:]==['package','upload'] and not submissions
    dispatch.advance(d,value);assert len(submissions)==1 and value['fit_dispatch'][item4_job(binding)]['phase']=='RUNNING'
    before=len(events);dispatch.advance(d,value);assert events[before:]==['observe','health']
    remote['status']='OBSERVATION_UNAVAILABLE';dispatch.advance(d,value)
    assert value['phase']=='EXECUTE_EXPERIMENT' and events.count('submit')==1
    remote['status']='COMPLETE';dispatch.advance(d,value)
    assert value['phase']=='COLLECT_EXPERIMENT' and events.count('submit')==1
    assert not (d.state/'validation.json').exists()


def test_failure_preserved_and_not_relaunched(external):
    (d,value,_,_,binding,saves),events,remote,submissions=external
    for _ in range(3):dispatch.advance(d,value)
    remote['status']='FAILED'
    with pytest.raises(ValueError,match='^EXPERIMENT_FIT_FAILED_RECONCILE$'):dispatch.advance(d,value)
    assert saves[-1]['fit_dispatch'][item4_job(binding)]['observation']['status']=='FAILED'
    assert events.count('submit')==1


def test_partial_upload_is_not_turned_into_submit(external,monkeypatch):
    (d,value,*_),events,remote,submissions=external
    dispatch.advance(d,value)
    def fail(*a):raise ValueError('MODAL_PACKAGE_UPLOAD_UNCERTAIN_RECONCILE')
    monkeypatch.setattr(dispatch,'prepare_package',fail)
    with pytest.raises(ValueError,match='^MODAL_PACKAGE_UPLOAD_UNCERTAIN_RECONCILE$'):dispatch.advance(d,value)
    assert not submissions


def test_package_change_after_preparation_blocks(external):
    (d,value,_,_,binding,_),events,_,submissions=external
    dispatch.advance(d,value);value['fit_dispatch'][item4_job(binding)]['manifest_sha256']='b'*64
    with pytest.raises(ValueError,match='^EXPERIMENT_DISPATCH_PACKAGE_CHANGED$'):dispatch.advance(d,value)
    assert not submissions and 'upload' not in events


from test_experiment_approval import reviewed
from test_experiment_context import experiment, root


def test_actual_scientific_seal_driver_dispatch_and_provider_package_connect(reviewed,monkeypatch):
    """Only root ownership is simulated. Actual seal, source, bindings and
    producer/consumer validators run; no provider or model is launched."""
    from orchestrator.manual_driver import Driver
    from orchestrator import experiment_package as package
    from orchestrator.modal_executor import verify_package
    from orchestrator.modal_item4_policy import AUTHORITY,TEAM_AUTHORITY
    d,value,_=reviewed
    if d.config['item_number']!=4:
        return
    Driver._accept_completed(d,value);sealed=package.emit(d,value)
    provisioning=d.state/'root-provisioned';pr.mkdir(provisioning)
    d.config['execution_provisioning']=str(provisioning)
    d.config['batch_ledger']=str(d.store.batch.folder)
    monkeypatch.setattr(dispatch,'trusted',lambda path:Path(path))
    runtime={'batch_ledger':d.config['batch_ledger'],'package_volume_id':'vo-synthetic'}
    pr.write_bytes(provisioning/'runtime.json',canonical(runtime))
    binding={'purpose':'M4_ITEM4','run_id':d.config['run_id'],'source':d.config['source'],
        'runtime_sha256':digest(canonical(runtime)),
        'experiment':{'backlog_item':4,'authority_sha256':AUTHORITY,'team_authority_sha256':TEAM_AUTHORITY,
                     'fit_id':'fit-one','stage':'SMOKE','segment':1,'billing_object_id':'ap-synthetic'},
        'progress':{'fit_binding':{'arm':'synthetic-arm','fold':0,'realization':'one'}},
        'outputs':['synthetic-result.json','validation.json']}
    record={'schema':'experiment-fit-dispatch/v1','source':d.config['source'],'run_id':d.config['run_id'],
        'package_manifest_sha256':digest((d.state/'experiment-package/manifest.json').read_bytes()),
        'jobs':[{'runtime':{'path':str(provisioning/'runtime.json'),
                          'sha256':digest((provisioning/'runtime.json').read_bytes())},'binding':binding}]}
    pr.write_bytes(provisioning/'READY.json',canonical(record))
    value['phase']='EXECUTE_EXPERIMENT';d.current=lambda:value;d.guard=lambda:None # Outer source setup only.
    calls=[tuple(r) for r in d.store.db.execute('SELECT * FROM manual_calls')]
    Driver._advance(d)
    assert value['fit_dispatch'][item4_job(binding)]['phase']=='UPLOAD'
    folder=d.state/'fit-packages'/item4_job(binding)/'prepared'
    manifest=json.loads((folder/'manifest.json').read_bytes())
    assert verify_package(folder,manifest['binding'])==manifest
    assert (folder/'SPEC.md').read_bytes()==(d.state/'experiment-package/SPEC.md').read_bytes()
    assert (folder/'execution.py').read_bytes()==(d.state/'experiment-package/code/execution.py').read_bytes()
    assert [tuple(r) for r in d.store.db.execute('SELECT * FROM manual_calls')]==calls
    if d.store.batch.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='autonomy_compute'").fetchone():
        assert not d.store.batch.db.execute('SELECT 1 FROM autonomy_compute').fetchone()


@pytest.mark.parametrize('change',['bool-fold','extra-fit-field','empty-outputs','duplicate-json'])
def test_ambiguous_frozen_or_runtime_fields_refuse(prepared,change):
    d,value,root,selection,binding,_=prepared
    if change=='duplicate-json':
        raw=(root/'READY.json').read_text().replace('"schema":', '"schema":"duplicate", "schema":',1)
        pr.write_text(root/'READY.json',raw)
    elif change=='bool-fold':
        binding['progress']['fit_binding']['fold']=False
        pr.write_bytes(root/'READY.json',canonical(selection))
    else:
        path=d.state/'experiment-package/execution-plan.json';plan=json.loads(path.read_bytes())
        if change=='extra-fit-field':plan['fits'][0]['unreviewed']=True
        else:plan['fits'][0]['outputs']=[]
        pr.write_bytes(path,canonical(plan))
    with pytest.raises(ValueError):dispatch.load(d,value)


@pytest.mark.parametrize('status',['UNKNOWN','OBSERVATION_UNAVAILABLE'])
def test_unavailable_status_never_submits_same_fit_again(external,status):
    (d,value,*_),events,remote,submissions=external
    for _ in range(3):dispatch.advance(d,value)
    remote['status']=status
    for _ in range(3):dispatch.advance(d,value)
    assert events.count('submit')==1 and len(submissions)==1
    assert value['phase']=='EXECUTE_EXPERIMENT'


def test_headroom_wait_keeps_same_job_and_prepared_package(external):
    (d,value,_,_,binding,_),events,_,submissions=external
    dispatch.advance(d,value);dispatch.advance(d,value)
    job=item4_job(binding);submissions[job]={'status':'WAIT_PROVIDER_HEADROOM','reserved':False}
    result=dispatch.advance(d,value)
    assert result['execution_wait']['reserved'] is False
    assert value['fit_dispatch'][job]['phase']=='SUBMIT'
    submissions[job]={'status':'SUBMITTED','provider_id':'sb-synthetic'}
    dispatch.advance(d,value)
    assert value['fit_dispatch'][job]['phase']=='RUNNING' and events.count('upload')==1


@pytest.mark.parametrize('state',[{'other':{'phase':'RUNNING'}}, {'bad':None}, []])
def test_invalid_saved_dispatch_state_refuses(prepared,state):
    d,value,*_=prepared;value['fit_dispatch']=state
    with pytest.raises(ValueError,match='^EXPERIMENT_DISPATCH_STATE$'):dispatch.advance(d,value)


@pytest.mark.parametrize('result',['INTERRUPTED_CHECKPOINT_PRESERVED','STOP_INTENT_RECONCILIATION_REQUIRED'])
def test_monitor_stop_cannot_be_mistaken_for_fit_completion(external,monkeypatch,result):
    (d,value,_,_,binding,saves),events,remote,submissions=external
    for _ in range(3):dispatch.advance(d,value)
    make=dispatch.executor
    def monitored(*args):
        store=make(*args)
        store.monitor_fit=lambda job:{'status':result,'may_launch':False}
        return store
    monkeypatch.setattr(dispatch,'executor',monitored)
    if result=='STOP_INTENT_RECONCILIATION_REQUIRED':
        with pytest.raises(ValueError,match='^EXPERIMENT_STOP_INTENT_RECONCILIATION_REQUIRED$'):
            dispatch.advance(d,value)
    else:
        assert dispatch.advance(d,value)['next_action']=='RECONCILE_FIT_CONTINUATION'
        assert value['fit_dispatch'][item4_job(binding)]['phase']=='INTERRUPTED'
    assert value['phase']=='EXECUTE_EXPERIMENT' and events.count('submit')==1
    assert saves[-1]['fit_dispatch'][item4_job(binding)]['health']['status']==result
