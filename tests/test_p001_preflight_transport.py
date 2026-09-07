import ast
import json
import pytest
from orchestrator.p001_preflight_transport import notebook,cells,public_receipt


def test_thin_notebook_preserves_separate_retrieval_and_private_capture():
    sources=cells('a'*40,'/content/drive/MyDrive/isles-pilot/archive/train.7z','/content/drive/MyDrive/isles-pilot/p001-preflight-'+'b'*32)
    n=notebook('a'*40,'/content/drive/MyDrive/isles-pilot/archive/train.7z','/content/drive/MyDrive/isles-pilot/p001-preflight-'+'b'*32)
    assert len(sources)==6
    assert all(not c['outputs'] for c in n['cells'] if c['cell_type']=='code')
    for source in sources:ast.parse(source)
    assert 'receipt.json' in sources[-1] and 'subprocess' not in sources[-1]
    assert 'dup2' in sources[3] and 'dup2' in sources[4]
    assert '--filter=blob:none' in sources[3] and 'clone' not in sources[3]
    assert 'DISPATCH_INTENT_NO_AUTOMATIC_RETRY' in sources[4]
    assert 'P001/run.py' not in sources[4]


def test_private_text_in_allowed_field_refuses_before_transport():
    r={'status':'FAILED','prediction_executed':False,'labels_opened':False,'reserved_access':False,'elapsed_seconds':1,'failure_type':'ValueError'}
    assert public_receipt(r)==r
    r['failure_type']='private clinical detail'
    with pytest.raises(ValueError,match='RECEIPT_REJECTED'):public_receipt(r)
    r['failure_type']='ValueError';r['extra']='private detail'
    with pytest.raises(ValueError,match='RECEIPT_REJECTED'):public_receipt(r)


def test_generated_acquisition_real_git_and_dirty_refusal(tmp_path,monkeypatch):
    import hashlib
    import subprocess
    from pathlib import Path
    source=cells('a'*40,'/content/drive/MyDrive/isles-pilot/archive/train.7z','/content/drive/MyDrive/isles-pilot/p001-preflight-'+'b'*32)[3]
    wrapped=ast.parse(source)
    setup=next(n.args[0].value for n in ast.walk(wrapped) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='compile' and isinstance(n.args[0],ast.Constant))
    function=next(n for n in ast.parse(setup).body if isinstance(n,ast.FunctionDef) and n.name=='acquire')
    original_run=subprocess.run
    seed=tmp_path/'seed';seed.mkdir()
    original_run(['git','init','-q',str(seed)],check=True)
    (seed/'wanted.txt').write_text('synthetic reviewed bytes')
    (seed/'unwanted.txt').write_text('synthetic out-of-scope file')
    original_run(['git','-C',str(seed),'add','.'],check=True)
    original_run(['git','-C',str(seed),'-c','user.name=Fixture','-c','user.email=fixture@local.invalid','commit','-qm','fixture'],check=True)
    pin=subprocess.check_output(['git','-C',str(seed),'rev-parse','HEAD'],text=True).strip()
    seen=[]
    def routed(args,**kw):
        seen.append(list(args))
        if 'remote' in args and 'add' in args:
            assert args[-1]=='https://github.com/Moroseui/concept-research-scout.git'
            args=[*args[:-1],str(seed)]
        return original_run(args,**kw)
    monkeypatch.setattr(subprocess,'run',routed)
    namespace={'subprocess':subprocess,'hashlib':hashlib}
    exec(compile(ast.Module(body=[function],type_ignores=[]),'generated-acquisition','exec'),namespace)
    destination=tmp_path/'acquired'
    namespace['acquire'](destination,pin,['wanted.txt'])
    assert (destination/'wanted.txt').read_text()=='synthetic reviewed bytes'
    assert not (destination/'unwanted.txt').exists()
    assert any('--no-tags' in args and '--depth=1' in args and args[-1]==pin for args in seen)
    (destination/'wanted.txt').write_text('preserve operator edit')
    with pytest.raises(AssertionError,match='source bytes changed'):
        namespace['acquire'](destination,pin,['wanted.txt'])
    assert (destination/'wanted.txt').read_text()=='preserve operator edit'
