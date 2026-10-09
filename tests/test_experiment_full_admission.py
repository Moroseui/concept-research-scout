"""Real approval/package/selection/collection/projection/admission connections.

No model, patient or provider computation: synthetic outputs and terminal facts
are inserted as fixtures with explicit columns. Actual MCP qualification, seals,
validators, binding replay, owner and budget transactions are not patched.
Host root provenance only is simulated by the portable tests.
"""
import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import experiment_full_admission as admission,experiment_projection as projection
from orchestrator import experiment_dispatch as dispatch,experiment_package as package
from orchestrator import experiment_modal_package as bridge,experiment_continuation as continuation
from orchestrator import experiment_result as results,private_records as pr,modal_item4_budget as budget
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import digest,inventory,atomic
from orchestrator.modal_executor import canonical,item4_job,ModalExecutor
from orchestrator.modal_budget import ComputeAccounts
from orchestrator.modal_fit_progress import encoded
from orchestrator.modal_item4_policy import AUTHORITY,TEAM_AUTHORITY,quote
from test_experiment_context import experiment as base_experiment,root
from test_experiment_approval import reviewed
from test_experiment_projection import example
from test_modal_item4_budget import snapshot,NOW


@pytest.fixture
def experiment(base_experiment):
    d,v=base_experiment;plan,_=example()
    for fit in plan['fits']:
        fit.update(realization='one',outputs=['timing.json','validation.json'],validation_checks=['synthetic-check'])
    raw=canonical(plan);pr.write_bytes(d.context/'execution-plan.json',raw)
    d.config['execution_scope']['plan_sha256']=digest(raw)
    prep=json.loads((d.state/'preparation-plan.json').read_bytes())
    prep['execution_scope']=d.config['execution_scope'];prep['execution_plan']['sha256']=digest(raw)
    pr.write_bytes(d.state/'preparation-plan.json',canonical(prep))
    d.config['plan_sha256']=digest(canonical(prep))
    return d,v


@pytest.fixture
def full_lane(reviewed,monkeypatch):
    d,v,_=reviewed;assert d.config['item_number']==4
    Driver._accept_completed(d,v);sealed=package.emit(d,v)
    plan=json.loads((d.state/'experiment-package/execution-plan.json').read_bytes());_,observations=example()
    accounts=ComputeAccounts(d.store.batch);db=accounts.db
    d.store.batch.filesystem_root=Path('/')
    owner={'state':str(d.state),'source':d.config['source'],'run_id':d.config['run_id'],
        'plan_sha256':d.config['plan_sha256'],'review_sha256':'e'*64,'execution_scope':d.config['execution_scope']}
    db.execute('UPDATE autonomy_runs SET binding=? WHERE id=?',(canonical(owner).decode(),d.config['run_id']))
    d.config.update(owner_binding=owner,engine_review={'sha256':'e'*64},batch_ledger=str(d.store.batch.folder),
        execution_provisioning=str(d.state/'runtimes'),context=str(d.context))
    atomic(d.state/'lane.json',d.config)
    pr.mkdir(d.state/'runtimes')
    monkeypatch.setattr(dispatch,'trusted',lambda p:Path(p)) # Root provenance ONLY, labelled above.
    v.update(phase='EXECUTE_EXPERIMENT',fit_dispatch={},fit_collections={},fit_collection_receipts={})
    rows=[];bases={};manifests={}
    for fit in plan['fits']:
        fit_id=fit['fit_id'];runtime={'batch_ledger':str(d.store.batch.folder),'synthetic_runtime_only':True}
        runtime_path=d.state/(fit_id+'-runtime.json');pr.write_bytes(runtime_path,canonical(runtime))
        resource=deepcopy(observations.get(fit_id,observations['arm-smoke'])['resources'])
        if fit['stage']=='FULL':resource['timeout_seconds']=12000
        base={'purpose':'M4_ITEM4','run_id':d.config['run_id'],'source':d.config['source'],
            'runtime_sha256':digest(canonical(runtime)),'resources':resource,'overhead_micro_usd':1000,
            'outputs':fit['outputs'],'cost':quote(resource,snapshot()['rates'],1000),
            'experiment':{'backlog_item':4,'authority_sha256':AUTHORITY,'team_authority_sha256':TEAM_AUTHORITY,
                'fit_id':fit_id,'stage':fit['stage'],'segment':1,'billing_object_id':'ap-'+fit_id.replace('-','')},
            'progress':{'fit_binding':{**{k:fit[k] for k in ('arm','fold','realization')},'environment_sha256':'c'*64}}}
        rows.append({'runtime':{'path':str(runtime_path),'sha256':digest(canonical(runtime))},'binding':base})
        job=item4_job(base);folder=d.state/'fit-packages'/job/'prepared';pr.mkdir(folder.parent,parents=True)
        manifests[fit_id]=bridge.emit(d,v,folder,base);bases[fit_id]=base
    ready={'schema':'experiment-fit-dispatch/v1','source':d.config['source'],'run_id':d.config['run_id'],
        'package_manifest_sha256':digest((d.state/'experiment-package/manifest.json').read_bytes()),'jobs':rows}
    pr.write_bytes(d.state/'runtimes/READY.json',canonical(ready))
    # A real interruption recorder and real successor resolver, on synthetic terminal evidence.
    old=bases['arm-smoke'];oldjob=item4_job(old);full=manifests['arm-smoke']['binding'];ident=digest(canonical(full))
    db.execute("INSERT INTO autonomy_compute(id,run,binding,status,reserved_micro_usd,provider_id,month) VALUES(?,?,?,'RUNNING',1000,'sb-synthetic','2026-10')",
        (ident,d.config['run_id'],canonical(full).decode()))
    reason=d.state/'synthetic-cause.json'
    pr.write_bytes(reason,canonical({'schema':'modal-interruption-cause/v1','segment_id':ident,
        'provider_id':'sb-synthetic','reason':'DELIBERATE_SMOKE_INTERRUPTION','evidence':{'synthetic_fixture_only':True}}))
    checkpoint={'synthetic_fixture_only':True,'metadata':{'next_epoch':1}}
    proof={'schema':'modal-fit-terminal-proof/v1','provider_id':'sb-synthetic','binding_sha256':ident,
        'fit_id':'arm-smoke','terminal_exit_code':137,'may_launch':False,'observed_at':NOW.isoformat(),
        'checkpoint_record':checkpoint,'checkpoint_record_sha256':digest(encoded(checkpoint))}
    budget.record_interruption(accounts,ident,NS(terminal_fit_checkpoint=lambda *a:proof),reason_record=reason)
    job={'job':oldjob,'binding':old,'runtime':runtime}
    terminal=continuation.terminal(d,v,job)
    new=continuation.successor(job,terminal)
    folder=d.state/'fit-packages'/new['job']/'prepared';pr.mkdir(folder.parent,parents=True)
    manifests['arm-smoke']=bridge.emit(d,v,folder,new['binding'])
    v['fit_continuations']={oldjob:[{'previous_job':oldjob,'event_sha256':terminal['event_sha256']}]}
    v['fit_dispatch'][oldjob]={'phase':'INTERRUPTED'}
    for fit_id,manifest in manifests.items():
        binding=manifest['binding'];job=item4_job(binding)
        if binding['experiment']['stage']=='FULL':continue
        folder=d.state/'fit-results'/job;pr.mkdir(folder,parents=True)
        timing=canonical(observations[fit_id]['timing']);pr.write_bytes(folder/'timing.json',timing)
        validation={'schema':'experiment-validation/v1','run_id':d.config['run_id'],'fit_id':fit_id,
            **{k:binding[k] for k in ('spec_sha256','code_sha256','execution_plan_sha256')},
            'files':{'timing.json':{'sha256':digest(timing),'bytes':len(timing)}},
            'checks':[{'id':'synthetic-check','status':'PASS','evidence':['timing.json']}]}
        pr.write_bytes(folder/'validation.json',canonical(validation))
        receipt=results.validate(folder,binding,plan);files={n:p['sha256'] for n,p in receipt['files'].items()}
        local=d.store.db
        local.execute("INSERT INTO jobs(id,binding,phase,status) VALUES(?,?,'collect','COMPLETE')",(job,canonical(binding).decode()))
        local.execute('INSERT INTO manual_collections VALUES(?,?)',(job,canonical(files).decode()))
        db.execute("INSERT INTO autonomy_compute(id,run,binding,status,reserved_micro_usd,provider_id,month) VALUES(?,?,?,'COLLECTED',1000,?,'2026-10')",
            (digest(canonical(binding)),d.config['run_id'],canonical(binding).decode(),'sb-'+fit_id))
        native={'binding_sha256':digest(canonical(binding)),'file_sha256':files,'synthetic_fixture_only':True}
        path=ModalExecutor._paths(d.store,job)/'collection-receipt.json';pr.mkdir(path.parent,parents=True)
        pr.write_bytes(path,canonical(native))
        v['fit_dispatch'][job]={'phase':'COMPLETE','manifest_sha256':digest(canonical(manifest))}
        v['fit_collections'][job]=receipt;v['fit_collection_receipts'][job]=digest(canonical(native))
    selected=dispatch.load(d,v)
    for kind,key in [('hardware','measured_hardware'),('full','measured_projection')]:
        saved=projection.prepare(d,v,selected,snapshot(),now=NOW,kind=kind)
        v[key]={k:saved[k] for k in ('path','sha256')}
    d.store.db.execute('INSERT INTO manual_state VALUES(1,?)',(canonical(v).decode(),))
    d.save=lambda value:d.store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(canonical(value).decode(),))
    return d,v,accounts,manifests['full']['binding']


@pytest.mark.parametrize('reviewed',[4],indirect=True)
def test_real_originals_to_record_to_full_reservation_is_idempotent(full_lane):
    d,v,accounts,binding=full_lane;before=inventory(d.state/'fit-packages')
    counts=accounts.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]
    event=admission.record(d,v)
    assert admission.record(d,v)==event
    assert accounts.reserve_item4(digest(canonical(binding)),d.config['run_id'],binding,billing_snapshot=snapshot(),now=NOW)
    assert not accounts.reserve_item4(digest(canonical(binding)),d.config['run_id'],binding,billing_snapshot=snapshot(),now=NOW)
    saved=json.loads(accounts.db.execute('SELECT payload FROM events WHERE id=?',(digest(canonical(binding))+':gpu-reserved',)).fetchone()[0])
    assert saved['full_admission']['record_sha256']==event['record']['sha256']
    assert saved['full_admission']['scientific_results_accepted'] is False
    assert inventory(d.state/'fit-packages')==before
    assert accounts.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==counts
    assert v['phase']=='EXECUTE_EXPERIMENT' and not (d.state/'REPORT.md').exists()


@pytest.mark.parametrize('reviewed',[4],indirect=True)
@pytest.mark.parametrize('damage',['missing-record','generic-acceptance','timing','review','plan','halt','record','runtime','missing-package','native','ledger','owner','uncertain-call','cap'])
def test_real_full_admission_refuses_changed_or_missing_evidence_without_reservation(full_lane,damage):
    d,v,accounts,binding=full_lane;event=admission.record(d,v)
    if damage=='missing-record':accounts.db.execute('DELETE FROM events WHERE id=?',(d.config['run_id']+':full-projection-approved',))
    elif damage=='generic-acceptance':accounts.db.execute('UPDATE events SET payload=? WHERE id=?',
        (canonical({'status':'ACCEPTED','full_projection_micro_usd':1}).decode(),d.config['run_id']+':full-projection-approved'))
    elif damage=='timing':pr.write_bytes(next((d.state/'fit-results').glob('*/timing.json')),b'{}')
    elif damage in ('review','plan'):pr.write_bytes(d.state/'experiment-package'/('review.json' if damage=='review' else 'execution-plan.json'),b'{}')
    elif damage=='halt':pr.write_bytes(accounts.batch.folder/'HALT',b'synthetic stop')
    elif damage=='record':pr.write_bytes(event['record']['path'],b'{}')
    elif damage=='runtime':binding['runtime_sha256']='f'*64
    elif damage=='native':pr.write_bytes(next((d.state/'modal-executions').glob('*/collection-receipt.json')),b'{}')
    elif damage=='ledger':accounts.db.execute("UPDATE autonomy_compute SET status='RUNNING' WHERE status='COLLECTED'")
    elif damage=='owner':accounts.db.execute("UPDATE autonomy_runs SET binding='{}' WHERE id=?",(d.config['run_id'],))
    elif damage=='uncertain-call':accounts.db.execute("INSERT INTO autonomy_calls VALUES('synthetic-uncertain','scientific',?,2,'2026-10-06','UNCERTAIN','{}',NULL)",(d.config['run_id'],))
    elif damage=='cap':accounts.db.execute("UPDATE autonomy_compute SET reserved_micro_usd=1275000000 WHERE status='ACCOUNTED'")
    else:
        folder=d.state/'fit-packages'/item4_job(binding)/'prepared'
        folder.rename(folder.with_name('preserved-test-original'))
    before=[tuple(r) for r in accounts.db.execute('SELECT * FROM autonomy_compute')]
    with pytest.raises((ValueError,FileNotFoundError)):
        accounts.reserve_item4(digest(canonical(binding)),d.config['run_id'],binding,billing_snapshot=snapshot(),now=NOW)
    assert [tuple(r) for r in accounts.db.execute('SELECT * FROM autonomy_compute')]==before


@pytest.mark.parametrize('command',['record-full-admission'])
def test_full_admission_command_refuses_root_before_opening_writer(monkeypatch,tmp_path,command):
    from orchestrator import experiment_driver
    calls=[];monkeypatch.setattr(experiment_driver.os,'geteuid',lambda:0)
    monkeypatch.setattr(experiment_driver,'ExperimentDriver',lambda *a:calls.append(a))
    with pytest.raises(ValueError,match='^EXPERIMENT_PREPARATION_OWNER_REQUIRED$'):
        experiment_driver.main([command,'--state',str(tmp_path)])
    assert calls==[]


@pytest.mark.parametrize('reviewed',[4],indirect=True)
@pytest.mark.parametrize('damage',['phase','halt','validation','owner'])
def test_record_does_not_turn_unmet_conditions_into_an_admission(full_lane,damage):
    d,v,accounts,_=full_lane
    if damage=='phase':v['phase']='run_spec_review'
    elif damage=='halt':pr.write_bytes(accounts.batch.folder/'HALT',b'synthetic stop')
    elif damage=='owner':accounts.db.execute("UPDATE autonomy_runs SET status='COMPLETE' WHERE id=?",(d.config['run_id'],))
    else:pr.write_bytes(next((d.state/'fit-results').glob('*/validation.json')),b'{}')
    with pytest.raises(ValueError):admission.record(d,v)
    assert not accounts.db.execute('SELECT 1 FROM events WHERE id=?',(d.config['run_id']+':full-projection-approved',)).fetchone()


@pytest.mark.parametrize('reviewed',[4],indirect=True)
def test_changed_existing_admission_is_not_overwritten(full_lane):
    d,v,accounts,_=full_lane;admission.record(d,v)
    key=d.config['run_id']+':full-projection-approved'
    raw=canonical({'synthetic_changed_record':True}).decode()
    accounts.db.execute('UPDATE events SET payload=? WHERE id=?',(raw,key))
    with pytest.raises(ValueError,match='^ITEM4_FULL_EXISTING_RECORD_CHANGED$'):admission.record(d,v)
    assert accounts.db.execute('SELECT payload FROM events WHERE id=?',(key,)).fetchone()[0]==raw
