import json,os,subprocess,tempfile
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import install_timing_author24_recovery as target

def old_unit():
    return ("[Service]\nUser=partho\nGroup=partho\nEnvironment=PYTHONPATH="+str(target.SCIENCE)+"\nExecStartPre=+/usr/bin/python3 -s -B existing-host before\nExecStart=/usr/bin/python3 -s -B "+str(target.CAP/'tools/temporary_daily_cap.py')+" author run\nExecStopPost=+/usr/bin/python3 -s -B existing-host after\nRestart=no\nTimeoutStartSec=3700\nKillMode=control-group\nUMask=0077\nNoNewPrivileges=true\nProtectSystem=strict\nPrivateTmp=true\n").encode()

@pytest.fixture
def setup(monkeypatch):
    assert os.getuid()==0, 'Actual root permission tests required; no skip'
    with tempfile.TemporaryDirectory(prefix='timing-held-install-',dir='/opt') as tmp:
        base=Path(tmp);base.chmod(0o755)
        paths={n:base/n.lower() for n in ['ROOT','RECORD','CAP','CAP_RECORD','UNIT_DIR','PREPARATION','PREPARATION_RECORD']}
        for n,p in paths.items():monkeypatch.setattr(target,n,p)
        for n in ['CAP','CAP_RECORD','UNIT_DIR','PREPARATION','PREPARATION_RECORD']:paths[n].mkdir()
        source=base/'source';source.mkdir();review=base/'review';review.mkdir()
        approval={'change_id':target.REVIEW_CHANGE,'source_sha':'a'*40,'report_sha256':'b'*64,'verdict':'APPROVE','findings':[]}
        binding={'operation_run_sha256':target.sha(b'original operation'),'failed_unit':{'MainPID':'0','ActiveState':'failed','SubState':'failed','ExecMainStatus':'1','InvocationID':'c'*32,'ControlGroup':''}}
        bodies={n:b'# synthetic reviewed source\n' for n in target.REQUIRED}
        bodies['tools/install_timing_author24_recovery.py']=Path(target.__file__).read_bytes()
        bodies['docs/TIMING_AUTHOR24_PREPARATION_PRIVATE.json']=json.dumps(binding).encode()
        bodies['tools/install_preparation_runtime.py']=b"def standalone_git(source):\n assert (source/'.git').is_dir()\ndef verify_units(units):\n assert len(units)==2\n"
        for n,raw in bodies.items():
            p=source/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        (source/'.git').mkdir()
        manifest={'source_files':{n:target.sha(raw) for n,raw in bodies.items()}}
        (review/'packet-manifest.json').write_text(json.dumps(manifest));(review/'report.md').write_text('synthetic authority boundary')
        cap=paths['CAP']/'tools/temporary_daily_cap.py';cap.parent.mkdir();cap.write_text('def verified():return {}\n')
        operation=paths['CAP_RECORD']/'operation/author/RUN.json';operation.parent.mkdir(parents=True);operation.write_bytes(b'original operation');operation.chmod(0o600)
        unit=paths['UNIT_DIR']/target.OLD_UNIT;unit.write_bytes(old_unit())
        prep=paths['PREPARATION']/'tools/preparation_branch_repair_runtime.py';prep.parent.mkdir();prep.write_text('def authority():return {}\n')
        colab_unit=paths['UNIT_DIR']/target.COLAB_OLD_UNIT
        colab_raw=old_unit().replace(('ExecStart=/usr/bin/python3 -s -B '+str(target.CAP/'tools/temporary_daily_cap.py')+' author run').encode(),('ExecStart=/usr/bin/python3 -s -B '+str(target.PREPARATION/'tools/preparation_branch_repair_runtime.py')+' advance --lane colab_preparation').encode())
        colab_unit.write_bytes(colab_raw)
        (paths['PREPARATION_RECORD']/'installed.json').write_text(json.dumps({'units':{str(colab_unit):target.sha(colab_raw)}}))
        (paths['CAP_RECORD']/'installed.json').write_text(json.dumps({'units':{str(unit):target.sha(unit.read_bytes())}}))
        from orchestrator import autonomy_review
        monkeypatch.setattr(autonomy_review,'verify_result',lambda p:approval)
        realrun=subprocess.run;realcheck=subprocess.check_output;commands=[]
        def check(args,**kw):
            commands.append(args)
            if args[0]=='git':return {'rev-parse':'a'*40,'branch':'astra/manual-timing-test','status':''}[args[1]]+'\n'
            if args[0]=='systemctl':
                if args[2]==target.COLAB_OLD_UNIT:return 'MainPID=0\nActiveState=inactive\nExecMainStatus=0\n'
                return ''.join(k+'='+v+'\n' for k,v in binding['failed_unit'].items())
            if args[:3]==['runuser','-u','partho']:return '{"status":"NO_RUNNING_CALL","ledger_writes":0}\n'
            return realcheck(args,**kw)
        def run(args,**kw):
            commands.append(args)
            if args==['systemctl','daemon-reload']:return NS(returncode=0)
            if args[:3]==['runuser','-u','partho']:
                expected=target.ORIGINAL_PREPARATION if args[-1]=='verify-colab' else target.SCIENCE
                assert 'PYTHONPATH='+str(expected) in args and 'RESEARCH_MANUAL_RUNTIME_CONFIG='+str(target.RUNTIME) in args and args[-1] in {'verify','verify-colab'}
                return NS(returncode=0,stdout=b'VERIFIED',stderr=b'')
            return realrun(args,**kw)
        monkeypatch.setattr(subprocess,'check_output',check);monkeypatch.setattr(subprocess,'run',run)
        yield NS(base=base,source=source,review=review,approval=approval,binding=binding,paths=paths,unit=unit,commands=commands,realrun=realrun)

def test_actual_root_umask_readability_and_preserved_failed_unit(setup):
    x=setup;old=x.unit.read_bytes();previous=os.umask(0o077)
    try:result=target.install(x.source,x.review)
    finally:os.umask(previous)
    assert result['status']=='INSTALLED_HELD' and result['scientific_calls']==result['provider_calls']==0
    assert x.unit.read_bytes()==old
    assert json.loads((x.paths['RECORD']/'installed.json').read_text())['preserved_operation_run_sha256']==target.sha(b'original operation')
    for root in [x.paths['ROOT'],x.paths['RECORD']]:
        for p in [root,*root.rglob('*')]:
            st=p.stat();assert st.st_uid==0 and st.st_gid==1003 and st.st_mode&0o777==(0o550 if p.is_dir() else 0o440)
    child="import os,sys;from pathlib import Path;assert os.getuid()==os.getgid()==1003;[p.read_bytes() for name in sys.argv[1:] for p in Path(name).rglob('*') if p.is_file()];print('PASS')"
    r=x.realrun(['setpriv','--reuid=1003','--regid=1003','--clear-groups','python3','-s','-B','-c',child,str(x.paths['ROOT']),str(x.paths['RECORD'])],capture_output=True,text=True)
    assert r.returncode==0 and r.stdout.strip()=='PASS',r.stderr
    assert not any('start' in a or 'reset-failed' in a or 'clone' in a for a in x.commands)
    new=(x.paths['UNIT_DIR']/target.NEW_UNIT).read_bytes()
    oldline=next(l for l in old.splitlines() if l.startswith(b'ExecStart='));newline=next(l for l in new.splitlines() if l.startswith(b'ExecStart='))
    assert new.replace(newline,oldline)==old
    colabold=(x.paths['UNIT_DIR']/target.COLAB_OLD_UNIT).read_bytes();colabnew=(x.paths['UNIT_DIR']/target.COLAB_NEW_UNIT).read_bytes()
    first=next(l for l in colabold.splitlines() if l.startswith(b'ExecStart='));second=next(l for l in colabnew.splitlines() if l.startswith(b'ExecStart='))
    assert colabnew.replace(second,first)==colabold

@pytest.mark.parametrize('key,value',[('verdict','REJECT'),('findings',['defect']),('change_id','other')])
def test_approval_refusal_before_writes(setup,key,value):
    setup.approval[key]=value
    with pytest.raises(ValueError,match='GENUINE_APPROVAL'):target.install(setup.source,setup.review)
    assert not setup.paths['ROOT'].exists() and not setup.paths['RECORD'].exists()

def test_changed_source_refused(setup):
    (setup.source/'tools/timing_author24_runtime.py').write_text('changed')
    with pytest.raises(ValueError,match='REVIEWED_SOURCE'):target.install(setup.source,setup.review)
    assert not setup.paths['RECORD'].exists()

def test_prior_unit_change_refused(setup):
    setup.unit.write_bytes(setup.unit.read_bytes()+b'# changed\n')
    with pytest.raises(ValueError,match='PRIOR_UNIT_CHANGED'):target.install(setup.source,setup.review)
    assert not setup.paths['RECORD'].exists()

def test_wrong_failed_invocation_refused(setup):
    setup.binding['failed_unit']['InvocationID']='d'*32
    with pytest.raises(ValueError,match='EXACT_FAILED_UNIT_REQUIRED'):target.install(setup.source,setup.review)
    assert not setup.paths['RECORD'].exists()

@pytest.mark.parametrize('name',['ROOT','RECORD'])
def test_existing_destination_preserved(setup,name):
    setup.paths[name].mkdir();marker=setup.paths[name]/'original';marker.write_bytes(b'original')
    with pytest.raises(ValueError,match='DESTINATION_EXISTS'):target.install(setup.source,setup.review)
    assert marker.read_bytes()==b'original'

@pytest.mark.parametrize('mutation',[lambda raw:raw.replace(b' author run',b' run'),lambda raw:raw+next(l for l in raw.splitlines(keepends=True) if l.startswith(b'ExecStart='))])
def test_unit_unknown_or_duplicate_entry_refused(mutation):
    with pytest.raises(ValueError,match='EXACT_PRIOR_ENTRY'):target.unit_bytes(mutation(old_unit()))

def test_exclusive_write_preserves_original(setup):
    p=setup.base/'original';p.write_bytes(b'unchanged')
    with pytest.raises(FileExistsError):target.put(p,b'new')
    assert p.read_bytes()==b'unchanged'


def test_changed_root_private_operation_refused_before_writes(setup):
    (setup.paths['CAP_RECORD']/'operation/author/RUN.json').write_bytes(b'changed operation')
    with pytest.raises(ValueError,match='ORIGINAL_OPERATION_CHANGED'):target.install(setup.source,setup.review)
    assert not setup.paths['RECORD'].exists()


def test_changed_colab_original_unit_refused_before_writes(setup):
    p=setup.paths['UNIT_DIR']/target.COLAB_OLD_UNIT;p.write_bytes(p.read_bytes()+b'# changed\n')
    with pytest.raises(ValueError,match='COLAB_PRIOR_UNIT_CHANGED'):target.install(setup.source,setup.review)
    assert not setup.paths['RECORD'].exists()

def test_colab_unit_unknown_or_duplicate_command_refused(setup):
    raw=(setup.paths['UNIT_DIR']/target.COLAB_OLD_UNIT).read_bytes()
    for changed in [raw.replace(b'advance --lane colab_preparation',b'run'),raw+next(l for l in raw.splitlines(keepends=True) if l.startswith(b'ExecStart='))]:
        with pytest.raises(ValueError,match='EXACT_COLAB_PRIOR_ENTRY'):target.colab_unit_bytes(changed)
