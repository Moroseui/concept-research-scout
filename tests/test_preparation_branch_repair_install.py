import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import pytest
from tools import install_preparation_branch_repair as target
from tools import preparation_branch_repair_runtime as runtime
from test_preparation_branch_repair_runtime import old_unit

@pytest.fixture
def installation(monkeypatch):
    assert os.getuid()==0, 'Run these permission tests as actual root; do not silently skip'
    with tempfile.TemporaryDirectory(prefix='preparation-branch-install-',dir='/opt') as folder:
        base=Path(folder);base.chmod(0o755)
        source=base/'source';source.mkdir();review=base/'approval';review.mkdir()
        oldroot=base/'old';oldroot.mkdir();oldrecord=base/'oldrecord';oldrecord.mkdir();(oldrecord/'review').mkdir()
        units=base/'units';units.mkdir();newroot=base/'new';record=base/'record'
        for name,value in [('ROOT',newroot),('RECORD',record),('ORIGINAL_ROOT',oldroot),('ORIGINAL_RECORD',oldrecord),('UNIT_DIR',units)]:monkeypatch.setattr(target,name,value)
        approval={'verdict':'APPROVE','findings':[],'change_id':target.CHANGE,'source_sha':'a'*40,'report_sha256':'b'*64}
        oldapproval={'verdict':'APPROVE','source_sha':target.ORIGINAL_SOURCE,'report_sha256':'c'*64}
        names=['tools/install_preparation_branch_repair.py','tools/preparation_branch_repair_runtime.py','tools/preparation_branch_repair_host.py','tools/preparation_premodel_recovery.py','orchestrator/preparation_interleaving.py']
        bodies={n:(Path(target.__file__).read_bytes() if n==names[0] else b'# reviewed synthetic fixture\n') for n in names}
        for name,raw in bodies.items():
            path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        manifest={'source_files':{n:target.sha(v) for n,v in bodies.items()}}
        (review/'packet-manifest.json').write_text(json.dumps(manifest));(review/'report.md').write_text('{}')
        helper=oldroot/'tools/install_preparation_runtime.py';helper.parent.mkdir()
        helper.write_text("def standalone_git(source):\n assert (source/'.git').is_dir()\ndef verify_units(units):\n assert len(units)==2\n")
        (source/'.git').mkdir()
        oldmanifest={'source_files':{'tools/install_preparation_runtime.py':target.sha(helper.read_bytes())}}
        (oldrecord/'review/packet-manifest.json').write_text(json.dumps(oldmanifest))
        unitpins={}
        for key in target.LANES:
            path=units/('research-preparation-and-cap-repair-20261010-'+key+'.service');path.write_bytes(old_unit(key));unitpins[str(path)]=target.sha(path.read_bytes())
        oldreceipt={'source':target.ORIGINAL_SOURCE,'review_sha256':'c'*64,'root':str(oldroot),'units':unitpins}
        (oldrecord/'installed.json').write_text(json.dumps(oldreceipt))
        from orchestrator import autonomy_review
        monkeypatch.setattr(autonomy_review,'verify_result',lambda path:approval if Path(path)==review else oldapproval)
        realcheck=subprocess.check_output;realrun=subprocess.run;commands=[]
        def check(args,**kwargs):
            commands.append(args)
            if args[0]=='git':
                return {'rev-parse':'a'*40,'branch':'astra/manual-repair-test','status':''}[args[1]]+'\n'
            if args[0]=='systemctl':return 'MainPID=0\nActiveState=inactive\n'
            if args[:3]==['runuser','-u','partho']:return '{"status":"NO_RUNNING_CALL","ledger_writes":0}\n'
            return realcheck(args,**kwargs)
        def run(args,**kwargs):
            commands.append(args)
            if args==['systemctl','daemon-reload']:return SimpleNamespace(returncode=0)
            if args[:3]==['runuser','-u','partho']:
                assert 'PYTHONPATH='+str(oldroot) in args
                assert 'RESEARCH_MANUAL_RUNTIME_CONFIG='+str(target.RUNTIME) in args
                assert args[-1]=='verify'
                return SimpleNamespace(returncode=0,stdout=b'{"status":"VERIFIED_HELD"}',stderr=b'')
            return realrun(args,**kwargs)
        monkeypatch.setattr(subprocess,'check_output',check);monkeypatch.setattr(subprocess,'run',run)
        yield SimpleNamespace(base=base,source=source,review=review,root=newroot,record=record,approval=approval,manifest=manifest,oldroot=oldroot,oldrecord=oldrecord,units=units,commands=commands,realcheck=realcheck,realrun=realrun)

def test_actual_root_umask_preserves_service_readability_and_originals(installation):
    x=installation;before={str(p):p.read_bytes() for root in (x.oldroot,x.oldrecord,x.units) for p in root.rglob('*') if p.is_file()}
    prior=os.umask(0o077)
    try:result=target.install(x.source,x.review)
    finally:os.umask(prior)
    assert result['status']=='INSTALLED_HELD' and result['scientific_calls']==result['provider_calls']==0
    assert all(Path(name).read_bytes()==raw for name,raw in before.items())
    for root in (x.root,x.record):
        for path in [root,*root.rglob('*')]:
            stat=path.stat();assert stat.st_uid==0 and stat.st_gid==1003
            assert stat.st_mode&0o777==(0o550 if path.is_dir() else 0o440)
    # Actual service UID/GID reads files through nested dirs under root umask0077.
    child="import os,sys;from pathlib import Path;assert os.getuid()==os.getgid()==1003;[p.read_bytes() for root in sys.argv[1:] for p in Path(root).rglob('*') if p.is_file()];print('PASS')"
    result=x.realrun(['setpriv','--reuid=1003','--regid=1003','--clear-groups','python3','-s','-B','-c',child,str(x.root),str(x.record)],capture_output=True,text=True)
    assert result.returncode==0 and result.stdout.strip()=='PASS',result.stderr
    assert not any('start' in command or 'clone' in command or 'checkout' in command or 'reset' in command for command in x.commands)

@pytest.mark.parametrize('field,value',[('verdict','REJECT'),('change_id','other'),('findings',['problem'])])
def test_install_refuses_without_genuine_exact_approval(installation,field,value):
    x=installation;x.approval[field]=value
    with pytest.raises(ValueError,match='GENUINE_APPROVAL'):target.install(x.source,x.review)
    assert not x.record.exists() and not x.root.exists()

def test_install_refuses_changed_source_before_writes(installation):
    x=installation;(x.source/'tools/preparation_branch_repair_runtime.py').write_text('changed')
    with pytest.raises(ValueError,match='REVIEWED_SOURCE'):target.install(x.source,x.review)
    assert not x.record.exists()

def test_install_refuses_changed_original_engine(installation):
    x=installation;(x.oldroot/'tools/install_preparation_runtime.py').write_text('changed')
    with pytest.raises(ValueError,match='ORIGINAL_SOURCE_CHANGED'):target.install(x.source,x.review)
    assert not x.record.exists()

def test_install_refuses_existing_destination(installation):
    x=installation;x.root.mkdir()
    with pytest.raises(ValueError,match='DESTINATION_EXISTS'):target.install(x.source,x.review)
    assert not x.record.exists()

def test_install_refuses_changed_prior_unit(installation):
    x=installation;next(x.units.iterdir()).write_text('changed')
    with pytest.raises(ValueError,match='ORIGINAL_UNIT_CHANGED'):target.install(x.source,x.review)
    assert not x.record.exists()

def test_put_refuses_overwrite_with_original_preserved(installation):
    p=installation.base/'exclusive';p.write_bytes(b'original')
    with pytest.raises(FileExistsError):target.put(p,b'new')
    assert p.read_bytes()==b'original'
