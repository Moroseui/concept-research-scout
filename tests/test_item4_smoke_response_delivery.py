"""Real context assembly for both response roles, with labelled synthetic artifacts."""
import copy,json
import pytest
from orchestrator import item4_smoke_response as post,item4_smoke_review as smoke,private_records as pr,manual_context as mc
from test_item4_smoke_review_delivery import delivery,root,registered,save_registry

@pytest.fixture
def response_delivery(delivery,monkeypatch):
    d,value,old=delivery
    smoke.deliver(d,value,old,'a'*64,{'timing-comparison.json':b'{"synthetic":true}', 'sprint12-timing.json':b'{"synthetic":true}'})
    raw=b'{"verdict":"REVISE","synthetic_fixture":true}'
    pr.write_bytes(d.state/'smoke-review11/review.json',raw)
    frozen={'schema':'item4-post-smoke-response/v1','original_state':json.dumps(value),'assessment':{'report_sha256':post.sha(raw),'synthetic':True}}
    monkeypatch.setattr(post,'ready',lambda *a:None)
    monkeypatch.setattr(post,'scope',lambda p,*a:json.loads(p['original_state']))
    post.deliver(d,value,frozen,'c'*64,{n:b'{"synthetic_original":true}' for n in post.SUPPLEMENTAL})
    return d,value,frozen


def compose(v,stage):
    d,value,p=v;work=d.state/stage
    prompt,measurement=mc.prepare(d.context,stage=stage,idea_ids=['sprint13b-execution'],
        task=post.guidance(p),artifacts=value['artifacts'],workspace=work,
        private_intake=d.config['private_intake'],structured_review=True,reference_prior_results=True,
        execution_mode='sprint13b-execution')
    return d,value,p,work,prompt,measurement

@pytest.mark.parametrize('stage',['run_spec_author','run_spec_review'])
def test_both_roles_receive_all_originals_and_current_authority(response_delivery,stage):
    d,value,p,work,prompt,measurement=compose(response_delivery,stage)
    post.verify_delivered(d,value,stage,work,prompt,measurement,p)
    refs=[r for r in value['artifacts'] if r['id'].startswith(('smoke-review11-','post-smoke-response-'))]
    assert len(refs)==26
    for ref in refs:
        item=next(r for r in measurement['workspace_files'] if r.get('id')==ref['id'])
        assert (work/item['path']).read_bytes()==(d.context/ref['path']).read_bytes()

@pytest.mark.parametrize('stage',['run_spec_author','run_spec_review'])
@pytest.mark.parametrize('fault',['missing-result','missing-cap','changed-file','descriptor','task','prompt','old-artifact'])
def test_missing_or_changed_response_input_refuses(response_delivery,stage,fault):
    d,value,p,work,prompt,measurement=compose(response_delivery,stage)
    ident='post-smoke-response-current-cap-decision.txt' if fault=='missing-cap' else 'smoke-review11-benchmark-A100-80GB/metrics.json'
    item=next(r for r in measurement['workspace_files'] if r.get('id')==ident)
    if fault.startswith('missing'):measurement['selected_artifacts']=[r for r in measurement['selected_artifacts'] if r['id']!=ident]
    elif fault=='old-artifact':value['artifacts']=[r for r in value['artifacts'] if r['id']!=ident]
    elif fault=='descriptor':item['source_path']='changed'
    elif fault=='changed-file':
        path=work/item['path'];path.chmod(0o600);pr.write_bytes(path,b'changed')
    elif fault=='task':
        role='author' if stage.endswith('author') else 'review';item=next(r for r in measurement['workspace_files'] if r.get('id')=='scientific-'+role+'-instructions')
        path=work/item['path'];path.chmod(0o600);pr.write_bytes(path,b'changed')
    else:prompt='changed prompt'
    with pytest.raises(ValueError):post.verify_delivered(d,value,stage,work,prompt,measurement,p)


@pytest.fixture
def diagnostic_delivery(response_delivery):
    from pathlib import Path
    d,value,old=response_delivery
    raw=b'{"verdict":"REVISE","synthetic_review12":true}'
    pr.write_bytes(d.state/'post-smoke-response/review.json',raw)
    p={'schema':post.DIAGNOSTIC_SCHEMA,'original_state':json.dumps(value),
        'assessment':{'report_sha256':post.sha(raw),'synthetic':True}}
    supplemental={n:b'{"synthetic_original":true}' for n in post.SUPPLEMENTAL}
    supplemental['cpu-diagnostic-operator-decision.txt']=(Path(__file__).parents[1]/'docs/ITEM4_CPU_DIAGNOSTIC_OPERATOR_DECISION.txt').read_bytes()
    post.deliver(d,value,p,'8'*64,supplemental)
    return d,value,p


@pytest.mark.parametrize('stage',['run_spec_author','run_spec_review'])
def test_cpu_diagnostic_delivers_operator_and_all_preserved_science(diagnostic_delivery,stage):
    d,value,p,work,prompt,measurement=compose(diagnostic_delivery,stage)
    post.verify_delivered(d,value,stage,work,prompt,measurement,p)
    refs=[r for r in value['artifacts'] if r['id'].startswith(('smoke-review11-','post-smoke-response-','cpu-diagnostic-authoring-'))]
    assert len(refs)==34
    for ref in refs:
        item=next(r for r in measurement['workspace_files'] if r.get('id')==ref['id'])
        assert (work/item['path']).read_bytes()==(d.context/ref['path']).read_bytes()


@pytest.mark.parametrize('stage',['run_spec_author','run_spec_review'])
@pytest.mark.parametrize('ident',['cpu-diagnostic-authoring-cpu-diagnostic-operator-decision.txt','post-smoke-response-scientific-review11.json'])
def test_cpu_diagnostic_missing_authority_or_prior_review_refused(diagnostic_delivery,stage,ident):
    d,value,p,work,prompt,measurement=compose(diagnostic_delivery,stage)
    measurement['selected_artifacts']=[r for r in measurement['selected_artifacts'] if r['id']!=ident]
    with pytest.raises(ValueError):post.verify_delivered(d,value,stage,work,prompt,measurement,p)
