"""Installer checks against synthetic inputs only; no server or provider access."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import pytest
from tools import install_preparation_runtime as install

pytestmark=pytest.mark.skipif(os.getuid()!=0,reason='requires real root-owned paths and UID1003 read checks')
UNIT=b"""[Unit]
Description=Original
ConditionPathExists=/original/lane.json
[Service]
User=partho
Group=partho
WorkingDirectory=/original/repository
ExecStart=/usr/bin/python3 /original/runtime.py
Environment=PYTHONPATH=/original
ReadWritePaths=/original/state
ExecStopPost=/original/retention-hook
TimeoutStartSec=7200
TimeoutStopSec=30
KillMode=control-group
Restart=no
NoNewPrivileges=yes
ProtectSystem=strict
PrivateTmp=yes
"""


def service_read(path):
    return subprocess.run(['/usr/bin/python3','-s','-B','-c',
        'import os,sys;assert os.getuid()==os.getgid()==1003;open(sys.argv[1],"rb").read()',str(path)],
        user=1003,group=1003,extra_groups=[],capture_output=True)


def test_installed_tree_readable_under_real_restrictive_umask():
    old=os.umask(0o077)
    try:
        with tempfile.TemporaryDirectory(prefix='preparation-install-mode-') as name:
            base=Path(name);base.chmod(0o755)
            root=base/'root';install.mkdir(root)
            install.put(root/'nested/code.py',b'synthetic code')
            assert stat.S_IMODE((root/'nested').stat().st_mode)==0o550
            assert stat.S_IMODE((root/'nested/code.py').stat().st_mode)==0o440
            assert service_read(root/'nested/code.py').returncode==0
            writable=base/'result';install.mkdir(writable,1003,0o700)
            install.put(writable/'nested/result.txt',b'synthetic result',1003)
            assert stat.S_IMODE((writable/'nested').stat().st_mode)==0o700
            assert (writable/'nested/result.txt').stat().st_uid==1003
            assert stat.S_IMODE((writable/'nested/result.txt').stat().st_mode)==0o600
            assert service_read(writable/'nested/result.txt').returncode==0
            with pytest.raises(FileExistsError):install.put(root/'nested/code.py',b'overwrite')
            assert (root/'nested/code.py').read_bytes()==b'synthetic code'
    finally:os.umask(old)


def test_unit_keeps_original_confinement_retention_timeout_and_no_restart(monkeypatch):
    monkeypatch.setattr(install,'PRIOR_PIN',install.sha(UNIT))
    original=UNIT.decode().splitlines()
    for lane in install.LANES:
        actual=install.unit_bytes(UNIT,lane).decode().splitlines()
        for prefix in ('User=','Group=','ExecStopPost=','TimeoutStartSec=','TimeoutStopSec=',
                       'KillMode=','Restart=','NoNewPrivileges=','ProtectSystem=','PrivateTmp='):
            assert [x for x in actual if x.startswith(prefix)]==[x for x in original if x.startswith(prefix)]
        assert 'ReadWritePaths=/original/state '+str(install.LANES[lane]) in actual
        assert any(x.endswith('--lane '+lane) for x in actual if x.startswith('ExecStart='))
    with pytest.raises(ValueError,match='PRIOR_UNIT'):install.unit_bytes(UNIT+b'#changed','aggregate_analysis')


@pytest.mark.parametrize('bad',['../escape','/absolute','a/../b','a//b','./file'])
def test_relative_paths_reject_escape_and_noncanonical(bad):
    with pytest.raises(ValueError,match='RELATIVE_PATH'):install.relative(bad)


def test_input_tree_rejects_symlinks_and_hardlinks(tmp_path):
    (tmp_path/'original').write_bytes(b'x');(tmp_path/'alias').symlink_to('original')
    with pytest.raises(ValueError,match='TREE_ALIAS'):install.plain_tree(tmp_path)
    (tmp_path/'alias').unlink();os.link(tmp_path/'original',tmp_path/'alias')
    with pytest.raises(ValueError,match='TREE_HARDLINK'):install.plain_tree(tmp_path)


@pytest.fixture
def candidate(tmp_path,monkeypatch):
    source=tmp_path/'source';source.mkdir();(source/'tools').mkdir();(source/'.git').mkdir()
    code=Path(install.__file__).read_bytes();(source/'tools/install_preparation_runtime.py').write_bytes(code)
    review=tmp_path/'review';review.mkdir();inputs=tmp_path/'inputs';inputs.mkdir()
    root=tmp_path/'install-root';record=tmp_path/'record';prior=tmp_path/'original.service';prior.write_bytes(UNIT)
    lanes={k:tmp_path/k for k in ('aggregate_analysis','colab_preparation')}
    monkeypatch.setattr(install,'ROOT',root);monkeypatch.setattr(install,'RECORD',record)
    monkeypatch.setattr(install,'PRIOR',prior);monkeypatch.setattr(install,'PRIOR_PIN',install.sha(UNIT))
    monkeypatch.setattr(install,'LANES',lanes)
    monkeypatch.setattr(install,'trusted',lambda p:Path(p)) # temp ancestors only
    scope={'source_sha':'d'*40,'lanes':{}};filepins={}
    for key,parent in lanes.items():
        incoming=inputs/key;incoming.mkdir();context=incoming/'protected-context';context.mkdir()
        (context/'aggregate.md').write_bytes(b'synthetic aggregate')
        plan={'context':str(parent/'protected-context'),'context_files':{'aggregate.md':install.sha(b'synthetic aggregate')}}
        raw=json.dumps(plan).encode();(incoming/'analysis-plan.json').write_bytes(raw)
        scope['lanes'][key]={'state':str(parent/'lane'),'plan':str(parent/'analysis-plan.json'),'plan_sha256':install.sha(raw)}
        filepins['evidence/'+('aggregate-analysis-plan.json' if key=='aggregate_analysis' else 'colab-preparation-plan.json')]=install.sha(raw)
    scope_path=tmp_path/'scope.json';scope_path.write_text(json.dumps(scope))
    filepins['evidence/preparation-interleaving.json']=install.sha(scope_path.read_bytes())
    manifest={'source_files':{'tools/install_preparation_runtime.py':install.sha(code)},'files':filepins}
    (review/'packet-manifest.json').write_text(json.dumps(manifest))
    approval={'verdict':'APPROVE','change_id':install.CHANGE,'source_sha':'d'*40,'report_sha256':'e'*64}
    monkeypatch.setattr('orchestrator.autonomy_review.verify_result',lambda p:approval)
    answers={'rev-parse':'d'*40,'branch':'astra/test','status':'','ls-files':'tools/install_preparation_runtime.py\0','systemctl':'MainPID=0\nActiveState=inactive\n'}
    def read(argv,**kw):
        if argv[0]=='runuser':return 'Synthetic Test' if argv[-1]=='user.name' else 'synthetic@example.invalid'
        return answers['systemctl' if argv[0]=='systemctl' else argv[1]]
    monkeypatch.setattr(install.subprocess,'check_output',read)
    return source,review,scope_path,inputs,root,record,approval,answers


@pytest.mark.parametrize('fault,error',[('destination','DESTINATION_EXISTS'),('dirty','CLEAN_SOURCE'),
 ('source','REVIEWED_SOURCE'),('plan','PLAN_BINDING'),('context','CONTEXT_MEMBERSHIP_HASHES'),
 ('scope','REVIEWED_SCOPE'),('review','GENUINE_APPROVAL'),('active','PRIOR_NOT_HELD')])
def test_invalid_install_refuses_before_any_installation(candidate,fault,error):
    source,review,scope,inputs,root,record,approval,answers=candidate
    if fault=='destination':root.mkdir()
    elif fault=='dirty':answers['status']=' M tools/install_preparation_runtime.py'
    elif fault=='source':(source/'tools/install_preparation_runtime.py').write_bytes(b'changed')
    elif fault=='plan':(inputs/'aggregate_analysis/analysis-plan.json').write_text('{}')
    elif fault=='context':(inputs/'aggregate_analysis/protected-context/aggregate.md').write_bytes(b'changed')
    elif fault=='scope':scope.write_text('{}')
    elif fault=='review':approval['verdict']='REVISE'
    elif fault=='active':answers['systemctl']='MainPID=42\nActiveState=active\n'
    with pytest.raises(ValueError,match=error):install.install(source,review,scope,inputs)
    assert not record.exists()
    if fault!='destination':assert not root.exists()
    assert not any(p.exists() for p in install.LANES.values())

@pytest.mark.parametrize('fault',['pointer','alternates','commondir','core-worktree','include'])
def test_shared_git_storage_refuses_before_copy(tmp_path,fault):
    source=tmp_path/'source';source.mkdir();folder=source/'.git'
    if fault=='pointer':folder.write_text('gitdir: /outside')
    else:
        folder.mkdir()
        if fault=='alternates':
            (folder/'objects/info').mkdir(parents=True);(folder/'objects/info/alternates').write_text('/outside')
        elif fault=='commondir':(folder/'commondir').write_text('/outside')
        elif fault=='core-worktree':(folder/'config').write_text('[core]\nworktree = /outside\n')
        elif fault=='include':(folder/'config').write_text('[include]\npath = /outside\n')
    with pytest.raises(ValueError,match='(?:STANDALONE|EXTERNAL)_GIT'):install.standalone_git(source)


@pytest.mark.parametrize('edit',['missing_exec','duplicate_exec','duplicate_write','duplicate_env'])
def test_unit_shape_cannot_drop_or_duplicate_required_bindings(monkeypatch,edit):
    raw=UNIT
    if edit=='missing_exec':raw=raw.replace(b'ExecStart=/usr/bin/python3 /original/runtime.py\n',b'')
    elif edit=='duplicate_exec':raw+=b'ExecStart=/unexpected\n'
    elif edit=='duplicate_write':raw+=b'ReadWritePaths=/unexpected\n'
    else:raw+=b'Environment=PYTHONPATH=/unexpected\n'
    monkeypatch.setattr(install,'PRIOR_PIN',install.sha(raw))
    with pytest.raises(ValueError):install.unit_bytes(raw,'aggregate_analysis')
