"""Real ledger/collection/validator/context connection; provider is synthetic.

Root provisioning and scientific seal are separately tested. Only that selection
and the provider boundary are mocked here. No model, SDK or patient computation.
"""
import json
from types import SimpleNamespace as NS
import pytest
from orchestrator import experiment_collection as collection, private_records as pr
from orchestrator import manual_context
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest, inventory
from test_modal_executor import setup, item4_dispatch, make_item4_package, private_test_environment
from test_context_budget import root
from test_scientific_intake import registered, save_registry


@pytest.fixture
def collected_lane(item4_dispatch,root,monkeypatch):
    executor,provider,batch,run=item4_dispatch
    job,binding,prepared,submitted=make_item4_package(item4_dispatch)
    binding['outputs']=['aggregate.csv','validation.json']
    plan={'fits':[{'fit_id':'one','outputs':binding['outputs'],'validation_checks':['synthetic-check']}]}
    binding['execution_plan_sha256']=digest(canonical(plan))
    manifest=json.loads((prepared/'manifest.json').read_bytes());manifest['binding']=binding
    pr.write_bytes(prepared/'manifest.json',canonical(manifest))
    assert executor.submit(job,binding,prepared,submitted)['status']=='SUBMITTED'
    provider.state='COMPLETE'
    def returned(provider_id,binding,folder):
        provider.calls.append('collect')
        raw=b'group,metric\naggregate,0.5\n';pr.write_bytes(folder/'aggregate.csv',raw)
        v={'schema':'experiment-validation/v1','run_id':run,'fit_id':'one',
            **{k:binding[k] for k in ('spec_sha256','code_sha256','execution_plan_sha256')},
            'files':{'aggregate.csv':{'sha256':digest(raw),'bytes':len(raw)}},
            'checks':[{'id':'synthetic-check','status':'PASS','evidence':['aggregate.csv']}]}
        pr.write_bytes(folder/'validation.json',canonical(v))
        return {'provider_id':provider_id,'binding_sha256':digest(canonical(binding)),
                'file_sha256':inventory(folder)}
    provider.collect=returned
    state=executor.path.parent;pr.mkdir(state/'experiment-package')
    pr.write_bytes(state/'experiment-package/execution-plan.json',canonical(plan))
    folder=state/'fit-packages'/job/'prepared';pr.copytree(prepared,folder)
    value={'phase':'COLLECT_EXPERIMENT','dispatch_sha256':'d'*64,
        'fit_dispatch':{job:{'phase':'COMPLETE','manifest_sha256':digest(canonical(manifest))}},'artifacts':[]}
    saved=[]
    driver=NS(state=state,context=root,config={'run_id':run,'source':binding['source']},store=executor,
        save=lambda v:saved.append(json.loads(json.dumps(v))),status=lambda:{'phase':value['phase']})
    # Actual ModalExecutor methods retain the real ledger; test controls ownership
    # of its connection so the production finally-close does not close our fixture.
    adapter=NS(db=NS(close=lambda:None),collect_remote=executor.collect_remote,_paths=executor._paths)
    monkeypatch.setattr(collection.dispatch,'executor',lambda *a:adapter)
    monkeypatch.setattr(collection.dispatch,'load',lambda *a:{'sha256':'d'*64,
        'jobs':[{'job':job,'binding':binding,'runtime':executor.config}]})
    monkeypatch.setattr(collection.dispatch.bridge,'emit',lambda *a:manifest)
    collection.artifact(driver,value,'run_spec','run_spec','SPEC.md',(prepared/'SPEC.md').read_bytes())
    return driver,value,executor,provider,batch,job


def test_real_collect_validate_deliver_and_repeat_without_new_job(collected_lane,monkeypatch):
    d,v,e,p,b,job=collected_lane
    ref,registry=registered(d.context,monkeypatch)
    registry.update(task='sprint13b-execution',idea_ids=['sprint13b-execution'])
    ref=save_registry(d.context,registry)
    calls=[tuple(r) for r in b.db.execute('SELECT * FROM autonomy_calls')]
    assert collection.advance(d,v)['phase']=='COLLECT_EXPERIMENT'
    assert p.calls.count('collect')==1
    assert collection.advance(d,v)['phase']=='result_interpretation_author'
    before=list(p.calls)
    # Pure re-entry verifies preserved results; no another provider call/charge.
    collection.advance(d,v)
    assert p.calls==before and p.calls.count('create')==1 and p.calls.count('launch')==1
    assert [tuple(r) for r in b.db.execute('SELECT * FROM autonomy_calls')]==calls
    assert b.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==1
    assert b.db.execute('SELECT status FROM autonomy_compute').fetchone()[0]=='COLLECTED'
    for stage in ('result_interpretation_author','result_interpretation_review'):
        work=d.state/stage
        text,measurement=manual_context.prepare(d.context,stage=stage,idea_ids=['sprint13b-execution'],
            task='Synthetic connection only.',artifacts=v['artifacts'],workspace=work,
            private_intake=ref,structured_review=True,execution_mode='sprint13b-execution')
        assert len(text)<200000
        table=next(x for x in measurement['workspace_files'] if x.get('id','').endswith('aggregate.csv'))
        assert (work/table['path']).read_bytes()==(d.state/'fit-results'/job/'aggregate.csv').read_bytes()
        assert table['sha256']==digest((work/table['path']).read_bytes())
        assert 'aggregate,0.5' not in text
    assert json.loads((d.state/'validation.json').read_bytes())['scientifically_accepted'] is False


@pytest.mark.parametrize('change',['data','receipt','package','state'])
def test_changed_collection_refuses_before_interpretation(collected_lane,change):
    d,v,e,p,b,job=collected_lane
    collection.advance(d,v)
    if change=='data':pr.write_text(d.state/'fit-results'/job/'aggregate.csv','changed')
    elif change=='receipt':pr.write_bytes(e._paths(job)/'collection-receipt.json',b'{}')
    elif change=='package':v['fit_dispatch'][job]['manifest_sha256']='f'*64
    else:v['fit_dispatch'][job]['phase']='RUNNING'
    with pytest.raises(ValueError):collection.advance(d,v)
    assert v['phase']=='COLLECT_EXPERIMENT' and p.calls.count('collect')==1


def test_resume_history_reaches_both_actual_interpretation_inputs(collected_lane,monkeypatch):
    """Synthetic prior segment selection; the resumed ledger admission is
    covered unpatched in test_experiment_continuation. Actual collection and
    both real input composers must carry the resulting provenance unchanged."""
    d,v,e,p,b,job=collected_lane
    selected=collection.dispatch.load(d,v)
    history=[{'fit_id':'one','segment':1,'reason':'OBSERVED_TRAINING_STALL',
        'terminal_receipt_sha256':'a'*64,'checkpoint_record_sha256':'b'*64,
        'epoch_resumed_from':10,'terminal_observed_at':'2026-10-06T01:00:00+00:00',
        'environment_sha256':'c'*64,'prior_reserved_micro_usd':123}]
    previous='synthetic-prior-segment'
    selected.update(all_jobs=[previous,job],continuations=history)
    v['fit_dispatch'][previous]={'phase':'INTERRUPTED'}
    monkeypatch.setattr(collection.dispatch,'load',lambda *args:selected)
    ref,registry=registered(d.context,monkeypatch)
    registry.update(task='sprint13b-execution',idea_ids=['sprint13b-execution'])
    ref=save_registry(d.context,registry)
    collection.advance(d,v);collection.advance(d,v)
    assert collection.verified(d,v)['continuations']==history
    receipt=next(a for a in v['artifacts'] if a['type']=='execution_receipt')
    expected=(d.context/receipt['path']).read_bytes()
    assert json.loads(expected)['continuations']==history
    for stage in ('result_interpretation_author','result_interpretation_review'):
        work=d.state/(stage+'-continuation')
        text,measurement=manual_context.prepare(d.context,stage=stage,idea_ids=['sprint13b-execution'],
            task='Synthetic continuation evidence delivery.',artifacts=v['artifacts'],workspace=work,
            private_intake=ref,structured_review=True,execution_mode='sprint13b-execution')
        # Small receipts may be included inline or as exact hash-bound files.
        if 'OBSERVED_TRAINING_STALL' in text:
            assert 'epoch_resumed_from' in text and 'terminal_receipt_sha256' in text
        else:
            row=next(x for x in measurement['workspace_files'] if x.get('id')==receipt['id'])
            assert (work/row['path']).read_bytes()==expected and row['sha256']==digest(expected)
        assert len(text)<200000
    selected['continuations'][0]['epoch_resumed_from']=11
    with pytest.raises(ValueError,match='^EXPERIMENT_FINAL_VALIDATION_CHANGED$'):collection.verified(d,v)


def test_incremental_fit_collects_once_without_completing_unselected_plan(collected_lane,monkeypatch):
    d,v,e,p,b,job=collected_lane
    selected=collection.dispatch.load(d,v);selected.update(complete_selection=False,wave_pins=['a'*64])
    monkeypatch.setattr(collection.dispatch,'load',lambda *args:selected)
    v['phase']='EXECUTE_EXPERIMENT'
    calls=[tuple(r) for r in b.db.execute('SELECT * FROM autonomy_calls')]
    assert collection.collect_ready(d,v,selected) is True
    rows=[tuple(r) for r in b.db.execute('SELECT * FROM autonomy_compute')]
    original=inventory(d.state/'fit-results'/job)
    assert collection.collect_ready(d,v,selected) is False
    assert p.calls.count('collect')==1
    assert inventory(d.state/'fit-results'/job)==original
    assert [tuple(r) for r in b.db.execute('SELECT * FROM autonomy_compute')]==rows
    assert [tuple(r) for r in b.db.execute('SELECT * FROM autonomy_calls')]==calls
    assert not (d.state/'validation.json').exists() and v['phase']=='EXECUTE_EXPERIMENT'
    with pytest.raises(ValueError,match='^EXPERIMENT_COLLECTION_NOT_COMPLETE$'):collection.advance(d,v)
    with pytest.raises(ValueError,match='^EXPERIMENT_COLLECTION_NOT_COMPLETE$'):collection.verified(d,v)
    selected['complete_selection']=True
    assert collection.advance(d,v)['phase']=='result_interpretation_author'
    assert p.calls.count('collect')==1


def test_incremental_collection_never_collects_running_fit(collected_lane):
    d,v,e,p,b,job=collected_lane;selected=collection.dispatch.load(d,v)
    v['fit_dispatch'][job]['phase']='RUNNING'
    assert collection.collect_ready(d,v,selected) is False
    assert p.calls.count('collect')==0


@pytest.mark.parametrize('change',['none','data','native','global','local','collected','running'])
def test_subset_replays_originals_and_real_ledgers_without_finalizing(collected_lane,change,monkeypatch):
    d,v,e,p,b,job=collected_lane;selected=collection.dispatch.load(d,v)
    selected['complete_selection']=False;v['phase']='EXECUTE_EXPERIMENT'
    monkeypatch.setattr(collection.dispatch,'load',lambda *args:selected)
    assert collection.collect_ready(d,v,selected)
    before=list(p.calls)
    if change=='data':pr.write_text(d.state/'fit-results'/job/'aggregate.csv','changed')
    elif change=='native':pr.write_bytes(e._paths(job)/'collection-receipt.json',b'{}')
    elif change=='global':b.db.execute("UPDATE autonomy_compute SET status='ACCOUNTED'")
    elif change=='local':e.db.execute("UPDATE jobs SET status='RUNNING'")
    elif change=='collected':e.db.execute("DELETE FROM manual_collections")
    elif change=='running':v['fit_dispatch'][job]['phase']='RUNNING'
    if change=='none':
        records=collection.verified_subset(d,v,selected,['one'])
        assert len(records)==1 and records[0]['scientifically_accepted'] is False
    else:
        with pytest.raises(ValueError):collection.verified_subset(d,v,selected,['one'])
    assert p.calls==before and v['phase']=='EXECUTE_EXPERIMENT'
    assert not (d.state/'validation.json').exists()
    with pytest.raises(ValueError,match='^EXPERIMENT_COLLECTION_NOT_COMPLETE$'):collection.verified(d,v)
