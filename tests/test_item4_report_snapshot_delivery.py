"""Author22 receives actual interfaces and counterexample through ordinary context assembly."""
import json
from pathlib import Path
import pytest
from orchestrator import item4_smoke_response as post,private_records as pr
from tools import item4_smoke_response_runtime as route
from test_item4_smoke_response_delivery import response_delivery,delivery,root,registered,save_registry,compose

@pytest.fixture
def snapshot_delivery(response_delivery,monkeypatch):
    d,value,old=response_delivery
    raw=b'{"verdict":"REVISE","synthetic_review15":true}'
    pr.mkdir(d.state/'cpu-diagnostic-fixture-correction')
    pr.write_bytes(d.state/'cpu-diagnostic-fixture-correction/review.json',raw)
    root=Path(__file__).parents[1]
    monkeypatch.setattr(route,'ROOT',root);monkeypatch.setattr(route,'trusted',lambda p:Path(p))
    p={'schema':post.SNAPSHOT_SCHEMA,'original_state':json.dumps(value),
        'assessment':{'report_sha256':post.sha(raw),'synthetic':True},
        'reference_native_harness_sha256':post.fixture.SNAPSHOT_MODULE}
    supplemental=route.supplemental(d,p)
    post.deliver(d,value,p,'8'*64,supplemental)
    return d,value,p

def test_real_snapshot_supplemental_context_is_complete(snapshot_delivery):
    d,value,p,work,prompt,measurement=compose(snapshot_delivery,'run_spec_author')
    post.verify_delivered(d,value,'run_spec_author',work,prompt,measurement,p)
    for name in post.SNAPSHOT_SUPPLEMENTAL|post.NATIVE_SUPPLEMENTAL:
        item=next(r for r in measurement['workspace_files'] if r.get('id')=='report-snapshot-author-'+name)
        raw=(work/item['path']).read_bytes()
        assert raw==route.supplemental(d,p)[name]

@pytest.mark.parametrize('name',sorted(post.SNAPSHOT_SUPPLEMENTAL))
def test_missing_report_lifecycle_evidence_refused(snapshot_delivery,name):
    d,value,p,work,prompt,measurement=compose(snapshot_delivery,'run_spec_author')
    measurement['workspace_files']=[r for r in measurement['workspace_files'] if r.get('id')!='report-snapshot-author-'+name]
    with pytest.raises(ValueError):post.verify_delivered(d,value,'run_spec_author',work,prompt,measurement,p)
