import json,sqlite3
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import idea2_cpu_executor as e,idea2_cpu_contract as c

def ready(tmp_path,monkeypatch):
    d=e.Idea2CPUExecutor(tmp_path/'jobs.sqlite',{'data_root':str(tmp_path/'data'),'environment_root':'synthetic','environment_sha256':c.ENVIRONMENT})
    data=tmp_path/'data';data.mkdir();(data/'frozen.bin').write_bytes(b'synthetic only')
    package=tmp_path/'package';package.mkdir();(package/'analysis.py').write_bytes(b'# synthetic fixture only')
    expected={'frozen.bin':{'sha256':c.sha(b'synthetic only'),'bytes':14}}
    package_hashes={'analysis.py':{'sha256':c.sha(b'# synthetic fixture only'),'bytes':24}}
    assert (package/'analysis.py').stat().st_size==24
    binding={'cpu_config_sha256':c.sha(c.encoded(d.cpu)),'venue':'existing-server-cpu','incremental_micro_usd':0,
             'input_verification':{'files':expected},'package_files':package_hashes}
    d.register(e.JOB,binding);lease=d.claim(e.JOB);d.complete_event(e.JOB,'acquired','VALIDATED',lease=lease['lease'])
    d.db.execute('INSERT INTO manual_packages VALUES(?,?)',(e.JOB,c.encoded(package_hashes).decode()))
    monkeypatch.setattr(e.cpu_isolation,'command',lambda *a,**k:['synthetic-fixture'])
    monkeypatch.setattr(e.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=0,stdout=b'isolated synthetic',stderr=b''))
    monkeypatch.setattr(e,'validate_outputs',lambda *a,**k:{'status':'VALIDATED','scientifically_accepted':False})
    return d,package,data,tmp_path/'work'

def fake_process(monkeypatch,*,rc=0,mutate=None):
    seen=[]
    class Process:
        pid=99999999
        def __init__(self,*args,**kwargs):seen.append(args);kwargs['stdout'].write(b'synthetic execution only\n')
        def wait(self,timeout):
            if mutate:mutate()
            return rc
    monkeypatch.setattr(e.subprocess,'Popen',Process)
    return seen

def test_success_has_immutable_before_after_and_cannot_reexecute(tmp_path,monkeypatch):
    d,package,data,work=ready(tmp_path,monkeypatch);seen=fake_process(monkeypatch)
    result=d.execute(package,work)
    assert result['status']=='EXECUTED_VALIDATED_NOT_SCIENTIFICALLY_ACCEPTED'
    assert json.loads((work/'before.json').read_bytes())==json.loads((work/'after.json').read_bytes())
    assert d.get(e.JOB)['phase']=='patient'
    with pytest.raises(ValueError,match='UNCERTAIN_OR_PREVIOUS'):d.execute(package,work)
    assert len(seen)==1

def test_input_mutation_marks_result_invalid_and_blocks_relaunch(tmp_path,monkeypatch):
    d,package,data,work=ready(tmp_path,monkeypatch)
    fake_process(monkeypatch,mutate=lambda:(data/'frozen.bin').write_bytes(b'changed input!'))
    with pytest.raises(ValueError,match='INVALID_OR_UNCERTAIN'):d.execute(package,work)
    exit=json.loads((work/'process-exit.json').read_bytes())
    assert exit['valid'] is False and 'INPUT_HASH' in exit['error']
    assert d.get(e.JOB)['status']=='BLOCKED'
    assert not(work/'validation.json').exists()

def test_nonzero_exit_still_hashes_every_input_and_package(tmp_path,monkeypatch):
    d,package,data,work=ready(tmp_path,monkeypatch);fake_process(monkeypatch,rc=2)
    with pytest.raises(ValueError,match='INVALID_OR_UNCERTAIN'):d.execute(package,work)
    assert (work/'after.json').exists()
    exit=json.loads((work/'process-exit.json').read_bytes())
    assert exit['exit_code']==2 and exit['valid'] is False
    assert not(work/'validation.json').exists()

def test_unknown_running_dispatch_never_starts_process(tmp_path,monkeypatch):
    d,package,data,work=ready(tmp_path,monkeypatch);d.claim(e.JOB)
    seen=fake_process(monkeypatch)
    with pytest.raises(ValueError,match='UNCERTAIN_OR_PREVIOUS'):d.execute(package,work)
    assert not seen and not work.exists()

def test_package_change_refused_before_process(tmp_path,monkeypatch):
    d,package,data,work=ready(tmp_path,monkeypatch);(package/'analysis.py').write_bytes(b'changed')
    seen=fake_process(monkeypatch)
    with pytest.raises(ValueError,match='INPUT_SIZE'):d.execute(package,work)
    assert not seen
