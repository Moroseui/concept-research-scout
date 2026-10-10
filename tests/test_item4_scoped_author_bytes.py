"""Frozen byte/reference checks independent of the slower ledger replay."""
import json
from types import SimpleNamespace as NS
from pathlib import Path
import pytest
from orchestrator import item4_smoke_response as post,author_revision_accounting as accounting

@pytest.mark.parametrize('fault',[None,'output','artifact-bytes','reference','superseding-author','revision-folder'])
def test_frozen_scientific_bytes_and_references(tmp_path,monkeypatch,fault):
    work=tmp_path/'run_spec_author-17';work.mkdir();context=tmp_path/'context';context.mkdir()
    outputs={}
    for name in ['SPEC.proposed.md','notebook.patch.json','execution.plan.json']:
        (work/name).write_bytes(b'frozen synthetic output');outputs[name]=post.sha((work/name).read_bytes())
    artifact=context/'spec.txt';artifact.write_bytes(b'frozen synthetic artifact')
    ref={'id':'run_spec','type':'run_spec','version':17,'path':'spec.txt','sha256':post.sha(artifact.read_bytes())}
    old={'artifacts':[ref],'notebook_revision_result':{'folder':'unchanged synthetic folder'}}
    p={'schema':post.SCOPED_SCHEMA,'author_outputs':outputs,'original_state':json.dumps(old)}
    row={'receipt':json.dumps({'workspace':str(work),'output_sha256':outputs})}
    class DB:
        def execute(self,*args):return self
        def fetchone(self):return row
    driver=NS(store=NS(db=DB()),config={'context':str(context)})
    monkeypatch.setattr(accounting,'_accepted',lambda *a:True) # Actual acceptance tested with real SQLite separately.
    value=json.loads(json.dumps(old))
    if fault=='output':(work/'notebook.patch.json').write_bytes(b'changed')
    elif fault=='artifact-bytes':artifact.write_bytes(b'changed')
    elif fault=='reference':value['artifacts'][0]['sha256']='0'*64
    elif fault=='superseding-author':value['artifacts'].append(dict(ref,version=18))
    elif fault=='revision-folder':value['notebook_revision_result']['folder']='changed'
    if fault is None:
        assert post.frozen_author(driver,p,value)==row
        value['artifacts'].append({'id':'cpu-diagnostic-scoped-review-carried-review','type':'result_tables'})
        assert post.frozen_author(driver,p,value)==row
    else:
        with pytest.raises(ValueError):post.frozen_author(driver,p,value)
