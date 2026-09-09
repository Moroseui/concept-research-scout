import copy
from types import SimpleNamespace
import pytest
from scripts.drive_register_provenance import plan


def fixture():
    config={'version':1,'mode':'REGISTERED_EVIDENCE_ONLY','output_folder_id':'keep-folder','caller_uids':[42], 'files':{'p001-archive':{'id':'original-archive','access':'metadata-only','max_bytes':0}}}
    values={'binding-file':{'id':'binding-file','name':'binding.json','size':'300','mimeType':'application/json'}}
    return config,values,SimpleNamespace(metadata=lambda i:values[i])


def test_adds_only_small_provenance_and_retains_exact_existing_grants():
    c,v,client=fixture();before=copy.deepcopy(c);new,metadata,aliases=plan(c,['binding-file'],client)
    assert c==before and new['output_folder_id']==c['output_folder_id']
    assert new['files']['p001-archive']==c['files']['p001-archive']
    assert aliases==['p001-preflight-binding'] and new['files'][aliases[0]]['max_bytes']==65536


@pytest.mark.parametrize('kind',['unknown','oversize','changed_id','native','existing','duplicate'])
def test_refuses_unrelated_or_repeated_selection(kind):
    c,v,client=fixture();selected=['binding-file']
    if kind=='unknown':v['binding-file']['name']='train.7z'
    if kind=='oversize':v['binding-file']['size']='65537'
    if kind=='changed_id':v['binding-file']['id']='other'
    if kind=='native':v['binding-file']['mimeType']='application/vnd.google-apps.document'
    if kind=='existing':c['files']['p001-preflight-binding']={'id':'old'}
    if kind=='duplicate':selected*=2
    before=copy.deepcopy(c)
    with pytest.raises(ValueError):plan(c,selected,client)
    assert c==before


@pytest.mark.parametrize('name',['launch.console.log','setup.console.log'])
def test_empty_original_logs_register_metadata_only_without_fabricated_content(name):
    c,v,client=fixture();v['binding-file'].update(name=name,size='0')
    new,metadata,aliases=plan(c,['binding-file'],client)
    entry=new['files'][aliases[0]]
    assert entry['access']=='metadata-only' and entry['max_bytes']==0
    assert metadata[0]['size']=='0'
    assert 'p001-preflight-binding' not in new['files']


@pytest.mark.parametrize('name,size',[('binding.json','0'),('process.json','0'),('launch.console.log','-1'),('setup.console.log',None)])
def test_empty_json_and_invalid_log_sizes_remain_refused(name,size):
    c,v,client=fixture();v['binding-file']['name']=name
    if size is None:del v['binding-file']['size']
    else:v['binding-file']['size']=size
    with pytest.raises(ValueError):plan(c,['binding-file'],client)
