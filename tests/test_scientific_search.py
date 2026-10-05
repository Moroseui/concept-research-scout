import hashlib,json,os,subprocess,sys
from pathlib import Path
import pytest
from orchestrator import scientific_search as search
from orchestrator import manual_stage

@pytest.fixture
def work(tmp_path):
    p=tmp_path/'workspace';p.mkdir(mode=0o700);(p/'evidence').mkdir(mode=0o700)
    raw=('HEADER\n'+('noise\n'*1000)+'answer Dice 0.2\n'+('Dice '+('x'*400)+'\n')*70).encode()
    f=p/'evidence/original.txt';f.write_bytes(raw)
    (p/'input-measurement.json').write_text(json.dumps({'workspace_files':[{'id':'original','path':'evidence/original.txt','sha256':hashlib.sha256(raw).hexdigest()}]}))
    for f in p.rglob('*'):f.chmod(0o700 if f.is_dir() else 0o600)
    return p

def test_real_stdio_search_pages_originals_and_does_not_write(work):
    prepared=search.prepare(work);before={str(p):p.read_bytes() for p in work.rglob('*') if p.is_file()}
    requests=[{'jsonrpc':'2.0','id':1,'method':'initialize'},{'jsonrpc':'2.0','id':2,'method':'tools/list'},
      {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'evidence_search','arguments':{'query':'answer'}}}]
    x=subprocess.run([sys.executable,'-I','-B',str(work/search.SERVER),prepared['manifest_sha256']],cwd=work,input=''.join(json.dumps(r)+'\n' for r in requests),text=True,capture_output=True)
    assert x.returncode==0,x.stderr
    replies=[json.loads(s) for s in x.stdout.splitlines()];hit=json.loads(replies[-1]['result']['content'][0]['text'])['hits'][0]
    assert hit['line']==1002 and hit['sha256']==hashlib.sha256((work/'evidence/original.txt').read_bytes()).hexdigest()
    assert {str(p):p.read_bytes() for p in work.rglob('*') if p.is_file()}==before
    result=search.query(work,prepared['manifest_sha256'],'evidence_search',{'query':'Dice'})
    assert result['next_cursor'] is not None and len(result['hits'])<=40 and len(json.dumps(result).encode())<16000
    second=search.query(work,prepared['manifest_sha256'],'evidence_search',{'query':'Dice','cursor':result['next_cursor']})
    assert result['hits'][-1]['line']<second['hits'][0]['line']

@pytest.mark.parametrize('args',[{'pattern':'/etc/*'},{'pattern':'../*'},{'pattern':'*','command':'cat /etc/passwd'},{'cursor':-1},{'cursor':True}])
def test_outside_and_execution_requests_refuse(work,args):
    pin=search.prepare(work)['manifest_sha256']
    with pytest.raises(ValueError):search.query(work,pin,'evidence_glob',args)

@pytest.mark.parametrize('damage',['changed','symlink','missing','manifest','oversize'])
def test_changed_missing_aliased_and_oversized_files_fail_closed(work,damage):
    pin=search.prepare(work)['manifest_sha256'];f=work/'evidence/original.txt'
    if damage=='changed':f.write_text('changed')
    elif damage=='missing':f.unlink()
    elif damage=='manifest':(work/search.MANIFEST).write_text('{}')
    elif damage=='oversize':f.write_bytes(b'x'*(search.MAX_FILE+1))
    else:
        outside=work.parent/'private';outside.write_text('PLANTED OUTSIDE');f.unlink();f.symlink_to(outside)
    with pytest.raises((ValueError,OSError)):search.query(work,pin,'evidence_glob',{})

def test_unregistered_file_is_not_discoverable(work):
    pin=search.prepare(work)['manifest_sha256'];(work/'extra-private.txt').write_text('PLANTED')
    assert search.query(work,pin,'evidence_search',{'query':'PLANTED'})['hits']==[]
    assert search.query(work,pin,'evidence_glob',{'pattern':'extra*'})['hits']==[]

@pytest.mark.parametrize('stage,turns',[('run_spec_review','30'),('result_interpretation_review','60')])
def test_actual_reviewer_command_has_bounded_search_and_only_report_write(work,stage,turns):
    cmd=manual_stage.reviewer_command(work,stage)
    assert cmd[cmd.index('--max-turns')+1]==turns
    assert cmd[cmd.index('--tools')+1]=='Read,Write'
    allow=cmd[cmd.index('--allowedTools')+1]
    assert allow == 'Read(./**),Edit(./review.json),mcp__evidence__evidence_search,mcp__evidence__evidence_glob'
    config=json.loads(cmd[cmd.index('--mcp-config')+1]);entry=config['mcpServers']['evidence']
    assert entry['command']=='/usr/bin/python3' and entry['args'][:3]==['-I','-B','/workspace/.scientific-search.py']

def test_unsupported_role_gets_no_budget_extension(work):
    with pytest.raises(ValueError,match='SCIENTIFIC_REVIEW_STAGE_REQUIRED'):manual_stage.reviewer_command(work,'result_interpretation_author')
