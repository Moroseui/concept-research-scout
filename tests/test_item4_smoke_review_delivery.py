"""Exact aggregate originals reach the real context composer; no model call."""
import copy,json
from types import SimpleNamespace as NS
import pytest
from orchestrator import item4_smoke_review as smoke,experiment_collection as collection,private_records as pr,manual_context as mc
from test_context_budget import root
from test_scientific_intake import registered,save_registry

@pytest.fixture
def delivery(root,tmp_path,monkeypatch):
    ref,registry=registered(root,monkeypatch)
    registry.update(task='sprint13b-execution',idea_ids=['sprint13b-execution']);ref=save_registry(root,registry)
    state=tmp_path/'stage';pr.mkdir(state)
    d=NS(state=state,context=root,config={'run_id':smoke.RUN,'private_intake':ref},save=lambda v:None)
    value={'artifacts':[]};old_review=state/'original-review.json'
    pr.write_bytes(old_review,b'{"verdict":"REVISE","synthetic_fixture":true}')
    for kind in ['run_spec','notebook_source','synthetic_tests','configuration']:
        collection.artifact(d,value,kind,kind,'old-'+kind+'.json',b'{"synthetic_original":true}')
    old={'artifacts':copy.deepcopy(value['artifacts']),'spec_review':str(old_review),'fit_continuations':{'synthetic-old':[{'epoch_resumed_from':1}]}}
    fits=[]
    for i,fit in enumerate(smoke.FITS):
        job='synthetic-job-'+str(i);files={}
        for name in ['metrics.json','epoch-timing.json','validation.json']:
            raw=json.dumps({'fit_id':fit,'synthetic_fixture':True,'file':name}).encode()
            pr.write_bytes(state/'fit-results'/job/name,raw)
            files[name]={'sha256':smoke.sha(raw),'bytes':len(raw)}
        fits.append({'job':job,'fit_id':fit,'validation':{'files':files},'termination':{'sha256':'d'*64}})
    p={'original_state':json.dumps(old),'fits':fits,'package_files':{'review.json':{'sha256':smoke.sha(old_review.read_bytes())}}}
    monkeypatch.setattr(smoke,'ready',lambda *a:[{'fit_id':f,'scientifically_accepted':False} for f in smoke.FITS])
    monkeypatch.setattr(smoke,'scope',lambda *a:old)
    monkeypatch.setattr(smoke,'proof',lambda *a:{'synthetic_fixture':True})
    return d,value,p


def compose(delivery):
    d,value,p=delivery
    refs=smoke.deliver(d,value,p,'a'*64,{'timing-comparison.json':b'{"scientifically_accepted":false}',
        'sprint12-timing.json':b'{"synthetic_prior_timing":true}'})
    work=d.state/'review'
    prompt,measurement=mc.prepare(d.context,stage='run_spec_review',idea_ids=['sprint13b-execution'],
        task=smoke.GUIDANCE,artifacts=value['artifacts'],workspace=work,
        private_intake=d.config['private_intake'],structured_review=True,reference_prior_results=True,
        execution_mode='sprint13b-execution')
    return d,value,p,work,prompt,measurement,refs


def test_all19_stage_files_and_original_science_delivered_unchanged(delivery):
    d,value,p,work,prompt,measurement,refs=compose(delivery)
    assert len(refs)==19
    smoke.verify_delivered(d,value,work,prompt,measurement,p)
    for ref in refs:
        item=next(r for r in measurement['workspace_files'] if r.get('id')==ref['id'])
        assert (work/item['path']).read_bytes()==(d.context/ref['path']).read_bytes()
    task=next(r for r in measurement['workspace_files'] if r.get('id')=='scientific-review-instructions')
    assert smoke.GUIDANCE in (work/task['path']).read_text()
    assert 'cannot authorize full training' in (work/task['path']).read_text()


@pytest.mark.parametrize('fault',['missing-original','missing-stage','changed-original','changed-stage','descriptor','prompt','index','task'])
def test_incomplete_or_changed_delivery_refuses(delivery,fault):
    d,value,p,work,prompt,measurement,refs=compose(delivery)
    target=next(r for r in measurement['workspace_files'] if r.get('id')==('notebook_source' if 'original' in fault else refs[0]['id']))
    if fault.startswith('missing'):
        measurement['selected_artifacts']=[r for r in measurement['selected_artifacts'] if r['id']!=target['id']]
    elif fault.startswith('changed'):
        path=work/target['path'];path.chmod(0o600);pr.write_bytes(path,b'changed')
    elif fault=='descriptor':target['source_path']='different'
    elif fault in ('index','task'):
        ident='scientific-review-artifact-index' if fault=='index' else 'scientific-review-instructions'
        row=next(r for r in measurement['workspace_files'] if r.get('id')==ident)
        path=work/row['path'];path.chmod(0o600);pr.write_bytes(path,b'changed')
    else:prompt='replacement prompt'
    with pytest.raises(ValueError):smoke.verify_delivered(d,value,work,prompt,measurement,p)
