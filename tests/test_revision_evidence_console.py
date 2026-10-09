import json,hashlib
import pytest
from orchestrator import revision_evidence as e,context_budget as cb,manual_context as mc

def raw(name,console=None):
 text=console if console is not None else ('line with complete synthetic log detail\n'*1100)
 v={'console':text,'console_sha256':hashlib.sha256(text.encode()).hexdigest(),'console_truncated':False,'other':['keep',3]}
 if name=='NATIVE_VERIFIED.json':v={'native_synthetic':v,'status':'VERIFIED'}
 return (json.dumps(v)+'\n').encode()

@pytest.mark.parametrize('name',['NATIVE_OUTPUT.json','NATIVE_VERIFIED.json'])
def test_long_native_console_reconstructs_every_original_value(name):
 original=raw(name);pretty,encoding=e.readable_original(name,original)
 value=json.loads(pretty);node=value
 for k in encoding['json_path'][:-1]:node=node[k]
 node['console']=''.join(node['console'])
 assert value==json.loads(original)
 assert mc._pageable_json(pretty)==pretty
 assert encoding['schema']=='native-console-string-chunks/v1'

@pytest.mark.parametrize('name',['OTHER.json','NATIVE_OUTPUT.json','NATIVE_VERIFIED.json'])
def test_short_json_uses_original_semantics(name):
 original=raw(name,'short\n');pretty,encoding=e.readable_original(name,original)
 assert json.loads(pretty)==json.loads(original) and encoding is None

@pytest.mark.parametrize('damage',['other-name','hash','truncated','duplicate','nonfinite','different-long-field'])
def test_no_general_pager_or_integrity_exception(damage):
 name='NATIVE_OUTPUT.json';original=raw(name);v=json.loads(original)
 if damage=='other-name':name='OTHER.json'
 elif damage=='hash':v['console_sha256']='0'*64
 elif damage=='truncated':v['console_truncated']=True
 elif damage=='different-long-field':v['unrelated']='x'*20000
 if damage=='duplicate':original=b'{"console":0,"console":1}'
 elif damage=='nonfinite':original=b'{"console":NaN}'
 else:original=json.dumps(v).encode()
 with pytest.raises((ValueError,cb.ContextError)):e.readable_original(name,original)
