"""Both scientific roles receive lossless failure pages; omissions fail closed."""
import json,copy
from pathlib import Path
import pytest
from tools import item4_smoke_response_runtime as route
from orchestrator import item4_fixture_correction as fixture,item4_smoke_response as post,manual_context as mc
from test_item4_smoke_response_delivery import response_delivery,delivery,root,registered,save_registry,compose

@pytest.fixture
def with_failure(response_delivery,monkeypatch,tmp_path):
 d,value,p=response_delivery;d.store=object()
 folder=tmp_path/'failure';folder.mkdir()
 originals={'console.txt':('synthetic full failure record\n'*2000).encode(),'proof.json':b'{"status":"FAIL","no_automatic_retry":true}'}
 for name,raw in originals.items():(folder/name).write_bytes(raw)
 frozen={'files':{n:route.sha(raw) for n,raw in originals.items()}}
 monkeypatch.setattr(fixture,'STATE',folder);monkeypatch.setattr(fixture,'failure',lambda *args:frozen)
 monkeypatch.setattr(route,'failure_qualification',lambda:{'status':'FAIL','scientific_acceptance':False})
 route.deliver_failure(d,value,p)
 return d,value,p,originals

@pytest.mark.parametrize('stage',['run_spec_author','run_spec_review'])
def test_complete_original_failure_reaches_both_roles(with_failure,stage):
 d,value,p,originals=with_failure
 _,_,_,work,prompt,measurement=compose((d,value,p),stage)
 post.verify_delivered(d,value,stage,work,prompt,measurement,p);route.verify_failure_delivery(d,value,p)
 refs=[r for r in measurement['workspace_files'] if r.get('id','').startswith(route.FAILURE_PREFIX)]
 index=next(r for r in refs if r['id']==route.FAILURE_PREFIX+'index.json')
 manifest=json.loads((work/index['path']).read_bytes());assert manifest['omissions']==[]
 reconstructed=b''
 for page in manifest['pages']:
  ref=next(r for r in refs if r['id']==page['name']);raw=(work/ref['path']).read_bytes()
  assert len(raw)==page['bytes'] and route.sha(raw)==page['sha256'];reconstructed+=raw
 assert route.sha(reconstructed)==manifest['sha256'] and len(reconstructed)==manifest['bytes']
 result=json.loads(reconstructed)
 assert result['files']=={n:raw.decode() for n,raw in originals.items()}
 assert result['corrected_fixture_executed'] is False and result['qualification']['status']=='FAIL'

@pytest.mark.parametrize('stage',['run_spec_author','run_spec_review'])
@pytest.mark.parametrize('fault',['missing-page','changed-page','missing-index'])
def test_incomplete_or_changed_failure_never_passes_delivery(with_failure,stage,fault):
 d,value,p,originals=with_failure
 _,_,_,work,prompt,measurement=compose((d,value,p),stage)
 name=route.FAILURE_PREFIX+('index.json' if fault=='missing-index' else 'page-001.txt')
 ref=next(r for r in measurement['workspace_files'] if r.get('id')==name)
 if fault=='changed-page':
  path=work/ref['path'];path.chmod(0o600);path.write_bytes(b'truncated')
 else:measurement['workspace_files'].remove(ref)
 with pytest.raises(ValueError):post.verify_delivered(d,value,stage,work,prompt,measurement,p)
