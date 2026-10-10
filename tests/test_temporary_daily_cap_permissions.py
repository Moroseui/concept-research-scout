"""Synthetic root-owned installation under real0077 and real UID/GID1003 reads."""
from pathlib import Path
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import pytest
from tools import install_temporary_daily_cap as installer
from tools import repair_temporary_daily_cap_permissions as repair

pytestmark=pytest.mark.skipif(os.getuid()!=0,reason='requires synthetic root-owned directories and uid1003 privilege drop')


def read_as_service(path):
    return subprocess.run(['/usr/bin/python3','-s','-B','-c',
        "import os,sys;assert os.getuid()==os.getgid()==1003;print(open(sys.argv[1]).read())",str(path)],
        user=1003,group=1003,extra_groups=[],capture_output=True,text=True)


def write_file(path,raw):
    path=Path(path);path.write_bytes(raw);os.chown(path,0,1003);path.chmod(0o440)


def test_installer_directory_modes_ignore_restrictive_umask():
    old=os.umask(0o077)
    try:
        with tempfile.TemporaryDirectory(prefix='cap-permissions-test-') as name:
            base=Path(name);base.chmod(0o755)
            for index,mode in enumerate((0o750,0o550)):
                directory=base/str(index);installer.make_directory(directory,mode)
                write_file(directory/'proof.txt',b'synthetic permission proof')
                st=directory.stat()
                assert stat.S_IMODE(st.st_mode)==mode and (st.st_uid,st.st_gid)==(0,1003)
                assert read_as_service(directory/'proof.txt').returncode==0
            broken=base/'broken';broken.mkdir(mode=0o550);os.chown(broken,0,1003)
            write_file(broken/'proof.txt',b'synthetic permission proof')
            assert stat.S_IMODE(broken.stat().st_mode)==0o500
            assert read_as_service(broken/'proof.txt').returncode!=0
    finally:os.umask(old)


@pytest.fixture
def installation(monkeypatch):
    with tempfile.TemporaryDirectory(prefix='cap-repair-test-') as name:
        base=Path(name);base.chmod(0o755)
        root=base/'source';record=base/'installed';repair_record=base/'one-use-repair'
        monkeypatch.setattr(repair,'ROOT',root);monkeypatch.setattr(repair,'RECORD',record)
        monkeypatch.setattr(repair,'REPAIR_RECORD',repair_record)
        monkeypatch.setattr(repair,'UNIT_PATH',base/'new.service')
        monkeypatch.setattr(repair,'ORIGINAL_UNIT',base/'old.service')
        for p,mode in repair.modes().items():
            p.mkdir();os.chown(p,0,1003);p.chmod(mode)
        source={'tools/entry.py':b'original entry','orchestrator/policy.py':b'original policy','docs/authority.txt':b'original authority'}
        for path,raw in source.items():write_file(root/path,raw)
        write_file(repair.UNIT_PATH,b'original held unit');write_file(repair.ORIGINAL_UNIT,b'old unchanged unit')
        state={'root':str(root),'source':repair.ORIGINAL_SOURCE,'report_sha256':repair.ORIGINAL_REPORT,
               'files':{p:repair.sha(raw) for p,raw in source.items()},
               'units':{str(repair.UNIT_PATH):repair.sha(repair.UNIT_PATH.read_bytes())},
               'preserved_original_unit':repair.sha(repair.ORIGINAL_UNIT.read_bytes())}
        write_file(record/'installed.json',json.dumps(state).encode())
        write_file(record/'complete.json',b'{"status":"PASS"}')
        write_file(record/'review/packet-manifest.json',json.dumps({'source_files':state['files']}).encode())
        write_file(record/'review/receipt.json',b'original simulated approval')
        monkeypatch.setattr(repair,'INSTALL_PIN',repair.sha((record/'installed.json').read_bytes()))
        monkeypatch.setattr(repair,'COMPLETE_PIN',repair.sha((record/'complete.json').read_bytes()))
        # Review qualification is simulated only in synthetic tests; all actual
        # ownership/modes, source hashes, membership and UID1003 reads are real.
        review=base/'repair-review';review.mkdir()
        script=Path(repair.__file__)
        (review/'packet-manifest.json').write_text(json.dumps({'source_sha':'d'*40,'source_files':{repair.FILE:repair.sha(script.read_bytes())}}))
        def qualify(path):
            if Path(path)==record/'review':return {'verdict':'APPROVE','source_sha':repair.ORIGINAL_SOURCE,'report_sha256':repair.ORIGINAL_REPORT}
            assert Path(path)==review
            return {'verdict':'APPROVE','source_sha':'d'*40,'report_sha256':'e'*64,'change_id':repair.CHANGE}
        monkeypatch.setattr('orchestrator.autonomy_review.verify_result',qualify)
        monkeypatch.setattr(repair,'trusted',lambda p:Path(p))  # Synthetic temp ancestor only.
        monkeypatch.setattr(repair,'held',lambda:None)  # No real systemd invoked.
        native_run=subprocess.run
        def local_uid_run(argv,**kwargs):
            if argv[:4]==['runuser','-u','partho','--']:
                return native_run(['/usr/bin/python3',*argv[5:]],user=1003,group=1003,extra_groups=[],**kwargs)
            return native_run(argv,**kwargs)
        monkeypatch.setattr(repair.subprocess,'run',local_uid_run)
        yield root,record,repair_record,review,qualify


def test_existing_install_repair_preserves_all_bytes_owners_and_original_records(installation):
    root,record,receipt,review,qualify=installation
    before=repair.inventory()
    assert read_as_service(root/'tools/entry.py').returncode!=0
    result=repair.apply(review)
    after=repair.inventory()
    assert result['directories_changed']==5 and result['readability']['uid']==1003
    assert after['files']==before['files']
    expected=dict(before['directories']);expected.update({str(p):m for p,m in repair.targets().items()})
    assert after['directories']==expected
    assert read_as_service(root/'tools/entry.py').returncode==0
    assert (receipt/'INTENT.json').is_file() and (receipt/'COMPLETE.json').is_file()
    with pytest.raises(ValueError):repair.apply(review)
    assert repair.inventory()==after


@pytest.mark.parametrize('fault',['source','directory_mode','record','owner','extra_file','unit','approval'])
def test_repair_refuses_before_chmod_for_changed_originals(installation,monkeypatch,fault):
    root,record,receipt,review,qualify=installation
    if fault=='source':(root/'tools/entry.py').write_bytes(b'changed')
    elif fault=='directory_mode':(root/'tools').chmod(0o755)
    elif fault=='record':(record/'complete.json').write_bytes(b'changed')
    elif fault=='owner':os.chown(root/'tools',0,0)
    elif fault=='extra_file':write_file(root/'docs/extra.txt',b'extra')
    elif fault=='unit':repair.UNIT_PATH.write_bytes(b'changed unit')
    else:monkeypatch.setattr('orchestrator.autonomy_review.verify_result',lambda p:{'verdict':'REVISE','findings':['synthetic']})
    before={p:stat.S_IMODE(p.lstat().st_mode) for p in repair.modes()}
    with pytest.raises(ValueError):repair.apply(review)
    assert not receipt.exists()
    assert {p:stat.S_IMODE(p.lstat().st_mode) for p in repair.modes()}==before


def test_active_unit_refusal_has_no_mutation(installation,monkeypatch):
    root,record,receipt,review,qualify=installation
    def refuse():raise ValueError('CAP_PERMISSION_REPAIR_UNIT_NOT_HELD')
    monkeypatch.setattr(repair,'held',refuse)
    before=repair.inventory()
    with pytest.raises(ValueError,match='UNIT_NOT_HELD'):repair.apply(review)
    assert repair.inventory()==before and not receipt.exists()



def test_bootstrap_requires_50_after_operator_temporary_day():
    from tools import review_preparation_cap_repair_once as bootstrap
    from orchestrator import autonomy_limits
    bootstrap.verify_dated_policy(autonomy_limits.daily_allowance)
    with pytest.raises(ValueError, match='DATED_POLICY'):
        bootstrap.verify_dated_policy(lambda day: {'limit': 100 if day=='2026-10-10' else 51})
