"""Real reserve/interrupt/resume/collect/validate/projection on synthetic returns.

Only the provider and prior scientific package seal are synthetic. No model,
patient computation, GPU or paid SDK operation. Original ledger paths are real.
"""
import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import experiment_projection as projection, experiment_collection as collection
from orchestrator import private_records as pr, modal_item4_budget as budget
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest,inventory
from test_experiment_projection import example
from test_modal_executor import setup,item4_dispatch,make_item4_package
from test_modal_item4_budget import snapshot,NOW


@pytest.fixture
def measured(item4_dispatch,monkeypatch):
    e,p,b,run=item4_dispatch;plan,observations=example()
    for f in plan['fits']:
        if f['stage']=='SMOKE':f['validation_checks']=['synthetic-epoch-check']
    state=e.path.parent;pr.mkdir(state/'experiment-package')
    pr.write_bytes(state/'experiment-package/execution-plan.json',canonical(plan))
    value={'phase':'EXECUTE_EXPERIMENT','fit_dispatch':{},'artifacts':[]}
    d=NS(state=state,context=state/'context',config={'run_id':run,'source':'a'*40},store=e,
        save=lambda value:None,status=lambda:{'phase':value['phase']})
    adapter=NS(db=NS(close=lambda:None),collect_remote=e.collect_remote,_paths=e._paths)
    monkeypatch.setattr(collection.dispatch,'executor',lambda *args:adapter)
    monkeypatch.setattr(collection.dispatch.bridge,'emit',lambda d,v,folder,binding,**kwargs:
        json.loads((folder/'manifest.json').read_bytes()))
    selected={'sha256':'d'*64,'complete_selection':False,'jobs':[]}
    def make(fit,segment=1,resume=None):
        job,binding,prepared,submitted=make_item4_package(item4_dispatch,fit=fit,segment=segment,
            gpu=observations[fit]['resources']['gpu'])
        binding.update(outputs=['timing.json','validation.json'],execution_plan_sha256=digest(canonical(plan)))
        binding['experiment']['billing_object_id']='ap-'+fit.replace('-','')
        if resume:binding['resume']=resume
        manifest=json.loads((prepared/'manifest.json').read_bytes());manifest['binding']=binding
        pr.write_bytes(prepared/'manifest.json',canonical(manifest))
        p.state='RUNNING'
        assert e.submit(job,binding,prepared,submitted)['status']=='SUBMITTED'
        folder=state/'fit-packages'/job/'prepared';pr.copytree(prepared,folder)
        return job,binding,manifest
    old,oldbinding,_=make('arm-smoke')
    oldid=digest(canonical(oldbinding))
    oldrow=b.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(oldid,)).fetchone()
    reason=state/'synthetic-interruption.json'
    pr.write_bytes(reason,canonical({'schema':'modal-interruption-cause/v1','segment_id':oldid,
        'provider_id':oldrow['provider_id'],'reason':'DELIBERATE_SMOKE_INTERRUPTION',
        'evidence':{'synthetic_test_only':True}}))
    from orchestrator.modal_fit_progress import encoded
    checkpoint={'synthetic_fixture_only':True,'metadata':{'next_epoch':1}}
    checkpoint_sha=digest(encoded(checkpoint))
    proof={'schema':'modal-fit-terminal-proof/v1','provider_id':oldrow['provider_id'],
        'binding_sha256':oldid,'fit_id':'arm-smoke','terminal_exit_code':137,
        'may_launch':False,'checkpoint_record':checkpoint,'checkpoint_record_sha256':checkpoint_sha}
    terminal=NS(terminal_fit_checkpoint=lambda *args:proof)
    budget.record_interruption(e.costs,oldid,terminal,reason_record=reason)
    event=b.db.execute('SELECT payload FROM events WHERE id=?',(oldid+':fit-interruption',)).fetchone()[0]
    resume={'previous_segment_id':oldid,'terminal_receipt_sha256':digest(event.encode()),
        'checkpoint_record_sha256':checkpoint_sha}
    for fit_id in observations:
        job,binding,manifest=make(fit_id,2 if fit_id=='arm-smoke' else 1,
            resume if fit_id=='arm-smoke' else None)
        value['fit_dispatch'][job]={'phase':'COMPLETE','manifest_sha256':digest(canonical(manifest))}
        selected['jobs'].append({'job':job,'binding':binding,'runtime':e.config})
    def returned(provider_id,binding,folder):
        p.calls.append('collect');fit=binding['experiment']['fit_id']
        raw=canonical(observations[fit]['timing']);pr.write_bytes(folder/'timing.json',raw)
        validation={'schema':'experiment-validation/v1','run_id':run,'fit_id':fit,
            **{k:binding[k] for k in ('spec_sha256','code_sha256','execution_plan_sha256')},
            'files':{'timing.json':{'sha256':digest(raw),'bytes':len(raw)}},
            'checks':[{'id':'synthetic-epoch-check','status':'PASS','evidence':['timing.json']}]}
        pr.write_bytes(folder/'validation.json',canonical(validation))
        return {'provider_id':provider_id,'binding_sha256':digest(canonical(binding)),
            'file_sha256':inventory(folder)}
    p.collect=returned;p.state='COMPLETE'
    while collection.collect_ready(d,value,selected):pass
    return d,value,selected,e,p,b


def test_originals_to_projection_and_repeat_without_charge_or_final_acceptance(measured):
    d,v,selected,e,p,b=measured
    calls=list(p.calls);rows=[tuple(r) for r in b.db.execute('SELECT * FROM autonomy_compute')]
    result=projection.prepare(d,v,selected,snapshot(),now=NOW)
    assert result['record']['calculation']['selected_gpu']=='H100'
    assert result['record']['scientifically_accepted'] is False
    assert result['record']['execution_admitted'] is False
    assert len(result['record']['evidence']['collections'])==4
    assert projection.prepare(d,v,selected,snapshot(),now=NOW)==result
    assert p.calls==calls and rows==[tuple(r) for r in b.db.execute('SELECT * FROM autonomy_compute')]
    assert not b.db.execute("SELECT 1 FROM events WHERE id LIKE '%:full-projection-approved'").fetchone()
    assert b.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    assert v['phase']=='EXECUTE_EXPERIMENT' and not (d.state/'validation.json').exists()
    assert sum(r['status']=='ACCOUNTED' for r in b.db.execute('SELECT * FROM autonomy_compute'))==1


@pytest.mark.parametrize('damage',['timing','validation','ledger','native','resume','missing','price'])
def test_changed_or_missing_originals_never_produce_a_projection(measured,damage):
    d,v,selected,e,p,b=measured;job=selected['jobs'][0]['job'];bill=deepcopy(snapshot())
    if damage in ('timing','validation'):
        pr.write_bytes(d.state/'fit-results'/job/(damage+'.json'),b'{}')
    elif damage=='ledger':b.db.execute("UPDATE autonomy_compute SET status='RUNNING' WHERE status='COLLECTED'")
    elif damage=='native':pr.write_bytes(e._paths(job)/'collection-receipt.json',b'{}')
    elif damage=='resume':b.db.execute("DELETE FROM events WHERE id LIKE '%:fit-interruption'")
    elif damage=='missing':v['fit_collections'].pop(job)
    else:bill['rates']['gpu_hour_cost_h100']='0.1'
    calls=list(p.calls)
    with pytest.raises(ValueError):projection.prepare(d,v,selected,bill,now=NOW)
    assert p.calls==calls and not (d.state/'measured-projections').exists()


def test_owner_producer_reads_billing_once_then_replays_originals(measured,monkeypatch):
    from datetime import datetime,timezone
    from orchestrator.modal_billing import canonical as billing_canonical
    d,v,selected,e,p,b=measured;requests=[]
    billing=deepcopy(snapshot());billing['observed_at']=datetime.now(timezone.utc).isoformat()
    body=dict(billing);body.pop('sha256');billing['sha256']=digest(billing_canonical(body))
    d.provider_factory=lambda runtime:NS(billing_snapshot=lambda:requests.append('read-only-billing') or billing)
    monkeypatch.setattr(collection.dispatch,'load',lambda *args:selected)
    result=projection.produce(d,v)
    assert result['status']=='MEASURED_NOT_ACCEPTED' and requests==['read-only-billing']
    repeated=projection.produce(d,v)
    assert repeated['projection']==result['projection'] and repeated['provider_called'] is False
    assert requests==['read-only-billing']
    job=selected['jobs'][0]['job'];pr.write_bytes(d.state/'fit-results'/job/'timing.json',b'{}')
    with pytest.raises(ValueError):projection.produce(d,v)
    assert requests==['read-only-billing']


def test_hardware_measured_before_other_smokes_and_controls_next_runtime(measured,monkeypatch):
    d,v,selected,e,p,b=measured
    monkeypatch.setattr(collection.dispatch,'load',lambda *args:selected)
    # Only the benchmark originals are needed to choose later smoke hardware.
    remaining=selected['jobs'][-1];v['fit_dispatch'][remaining['job']]['phase']='RUNNING'
    hardware=projection.prepare(d,v,selected,snapshot(),now=NOW,kind='hardware')
    v['measured_hardware']={k:hardware[k] for k in ('path','sha256')}
    assert hardware['record']['calculation']['selected_gpu']=='H100'
    assert len(hardware['record']['evidence']['collections'])==3
    assert 'full_projection_micro_usd' not in hardware['record']['calculation']
    with pytest.raises(ValueError,match='^EXPERIMENT_COLLECTION_SUBSET_NOT_COMPLETE$'):
        projection.prepare(d,v,selected,snapshot(),now=NOW)
    projection.require_hardware(d,v,[remaining])
    wrong=deepcopy(remaining);wrong['binding']['resources']['gpu']='B200'
    with pytest.raises(ValueError,match='^EXPERIMENT_MEASURED_HARDWARE_MISMATCH$'):
        projection.require_hardware(d,v,[wrong])
    v.pop('measured_hardware')
    with pytest.raises(ValueError,match='^EXPERIMENT_MEASURED_HARDWARE_REQUIRED$'):
        projection.require_hardware(d,v,[remaining])
    # The original benchmark wave has no circular dependence on itself.
    projection.require_hardware(d,v,selected['jobs'][:3])


@pytest.mark.parametrize('damage',['row','event','checkpoint'])
def test_resume_original_replayed_not_only_returned_pass_boolean(measured,damage):
    d,v,selected,e,p,b=measured
    if damage=='row':b.db.execute("UPDATE autonomy_compute SET status='RUNNING' WHERE status='ACCOUNTED'")
    else:
        event=b.db.execute("SELECT id,payload FROM events WHERE id LIKE '%:fit-interruption'").fetchone()
        data=json.loads(event['payload'])
        if damage=='event':data['proof']['provider_id']='sb-changed'
        else:data['proof']['checkpoint_record']['metadata']['next_epoch']=99
        b.db.execute('UPDATE events SET payload=? WHERE id=?',(json.dumps(data,sort_keys=True),event['id']))
    with pytest.raises(ValueError,match='^EXPERIMENT_RESUME_'):
        projection.prepare(d,v,selected,snapshot(),now=NOW)
