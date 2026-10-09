"""Actual guard subprocess and trivial synthetic code, never patient computation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest
from orchestrator import modal_input_guard as guard, private_records as pr


def sha(raw):return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def setup(tmp_path):
    root=tmp_path/'inputs';progress=tmp_path/'progress'
    pr.mkdir(root);pr.mkdir(progress)
    files={}
    for name,raw in {'dataset/plans.json':b'{"synthetic":true}',
                     'dataset/array.bin':b'harmless synthetic bytes'}.items():
        pr.write_bytes(root/name,raw);files[name]={'bytes':len(raw),'sha256':sha(raw)}
    payload={'binding_sha256':'a'*64,'guard_sha256':sha(Path(guard.__file__).read_bytes()),
             'preprocessing_sha256':'b'*64,'files':files}
    script=tmp_path/'science.py';marker=tmp_path/'executed.txt'
    pr.write_text(script,'from pathlib import Path; Path('+repr(str(marker))+').write_text("synthetic executed")')
    return root,progress,payload,script,marker


def execute(setup):
    root,progress,payload,script,_=setup
    # Same execute() as production; only fixed mount locations are replaced by
    # disposable fixture directories. The guard and child process are real.
    code=('from orchestrator.modal_input_guard import execute; execute('+repr(str(root))+','+
          repr(str(progress))+','+repr(str(script))+','+repr(payload)+')')
    return subprocess.run([sys.executable,'-B','-s','-c',code],capture_output=True,text=True)


def test_real_guard_then_real_code_and_duplicate_refusal(setup):
    root,progress,payload,script,marker=setup
    result=execute(setup);assert result.returncode==0,result.stderr
    assert marker.read_text()=='synthetic executed'
    path=guard.proof_path(progress,payload['binding_sha256']);raw=path.read_bytes();proof=json.loads(raw)
    assert proof['status']=='VERIFIED' and proof['reason'] is None
    assert proof['inventory_sha256']==sha(guard.canonical(payload['files']))
    assert proof['file_count']==2 and proof['total_bytes']==sum(r['bytes'] for r in payload['files'].values())
    pr.check_tree(progress)
    marker.unlink() # Disposable synthetic marker, not a preserved record.
    second=execute(setup);assert second.returncode!=0 and 'FileExistsError' in second.stderr
    assert not marker.exists() and path.read_bytes()==raw


@pytest.mark.parametrize('damage,code',[
    ('hash','INPUT_GUARD_HASH'),('size','INPUT_GUARD_MEMBER_OR_SIZE'),
    ('extra','INPUT_GUARD_MEMBER_OR_SIZE'),('missing','INPUT_GUARD_MEMBER_OR_SIZE'),
    ('symlink','INPUT_GUARD_ALIAS_OR_TYPE'),('dir-link','INPUT_GUARD_ALIAS_OR_TYPE'),
    ('fifo','INPUT_GUARD_ALIAS_OR_TYPE')])
def test_failed_hash_or_member_check_prevents_any_scientific_code(setup,damage,code):
    root,progress,payload,script,marker=setup
    p=root/'dataset/array.bin'
    if damage=='hash':pr.write_bytes(p,b'x'*p.stat().st_size)
    if damage=='size':pr.write_bytes(p,b'x')
    if damage=='extra':pr.write_bytes(root/'unexpected.bin',b'extra')
    if damage=='missing':p.unlink()
    if damage=='symlink':p.unlink();p.symlink_to(script)
    if damage=='dir-link':(root/'alias').symlink_to(script.parent,target_is_directory=True)
    if damage=='fifo':p.unlink();os.mkfifo(p)
    result=execute(setup);assert result.returncode!=0 and code in result.stderr
    assert not marker.exists()
    proof=json.loads(guard.proof_path(progress,payload['binding_sha256']).read_bytes())
    assert proof['status']=='FAILED' and proof['reason']==code


@pytest.mark.parametrize('name',['../escape','/absolute','a/../escape','a//b','a\\b','a\x00b'])
def test_unsafe_member_names_refuse_before_record_or_code(setup,name):
    root,progress,payload,script,marker=setup
    payload['files'][name]={'bytes':1,'sha256':'a'*64}
    result=execute(setup);assert result.returncode!=0 and 'INPUT_GUARD_INVENTORY' in result.stderr
    assert not marker.exists() and not list(progress.iterdir())


def test_unsafe_existing_record_directory_is_not_repaired(setup):
    root,progress,payload,script,marker=setup
    p=progress/'input-verification';p.mkdir();p.chmod(0o755)
    result=execute(setup);assert result.returncode!=0 and 'INPUT_GUARD_RECORD_PERMISSIONS' in result.stderr
    assert not marker.exists() and p.stat().st_mode&0o777==0o755


def test_independent_guards_share_progress_directory_without_collision(setup,tmp_path):
    import copy
    from concurrent.futures import ThreadPoolExecutor
    root,progress,payload,script,marker=setup
    other=copy.deepcopy(payload);other['binding_sha256']='c'*64
    script2=tmp_path/'science2.py';marker2=tmp_path/'executed2.txt'
    pr.write_text(script2,'from pathlib import Path;Path('+repr(str(marker2))+').write_text("second")')
    with ThreadPoolExecutor(max_workers=2) as pool:
        a=pool.submit(execute,setup)
        b=pool.submit(execute,(root,progress,other,script2,marker2))
        first,second=a.result(),b.result()
    assert first.returncode==second.returncode==0,(first.stderr,second.stderr)
    assert marker.exists() and marker2.exists()
    assert len(list((progress/'input-verification').glob('*.json')))==2


from test_modal_fit_mounts import mounted

@pytest.mark.parametrize('damage',[None,'hash','path','binding','alias'])
def test_native_packaged_inventory_transport_and_refusals(mounted,damage):
    # Actual confined command and existing resolver. This lower-level guard
    # fixture launches a harmless marker, not scientific code or environment.
    roots,payload,run=mounted
    script=roots['package']/'run.py'
    pr.write_text(script,script.read_text().replace("a=p.parse_args()", "p.add_argument('--manifest-json');a=p.parse_args()"))
    files=dict(payload['files'])
    for n in range(850):
        name='synthetic/'+str(n).zfill(4)+'-metadata-padding-to-exercise-real-argument-limit.bin'
        pr.write_bytes(roots['inputs']/name,b'fixture');files[name]={'sha256':sha(b'fixture'),'bytes':7}
    raw=guard.canonical(files);assert len(raw)>100000
    inventory=roots['package']/'input-inventory.json';pr.write_bytes(inventory,raw)
    binding={'purpose':'M4_ITEM4','preprocessing':{'input_contract_sha256':sha(raw)}}
    payload.pop('files');payload.update(binding_sha256=sha(guard.canonical(binding)),
        inventory_ref={'path':'input-inventory.json','sha256':sha(raw)},
        execution_manifest={'schema':'modal-run/v1','binding':binding,'files':{'input-inventory.json':sha(raw)}})
    assert len(guard.canonical(payload))<10000
    if damage=='hash':pr.write_bytes(inventory,b'{}')
    if damage=='path':payload['inventory_ref']['path']='../outside'
    if damage=='binding':payload['execution_manifest']['binding']['preprocessing']['input_contract_sha256']='f'*64
    if damage=='alias':inventory.unlink();inventory.symlink_to('/usr') # Disposable fixture only.
    result=run(payload)
    if damage:
        assert result.returncode!=0 and 'INPUT_GUARD_INVENTORY_BINDING' in result.stderr
        assert not (roots['progress']/'executed.json').exists()
        return
    assert result.returncode==0,result.stderr
    proof=json.loads((roots['progress']/'input-verification'/(payload['binding_sha256']+'.json')).read_bytes())
    assert proof['status']=='VERIFIED' and proof['file_count']==851
    before=(roots['progress']/'executed.json').read_bytes()
    again=run(payload);assert again.returncode!=0 and 'FileExistsError' in again.stderr
    assert (roots['progress']/'executed.json').read_bytes()==before
