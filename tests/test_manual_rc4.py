"""RC4 portability: same exposure with present/absent stdlib package directory."""
import json
from pathlib import Path
import pytest
from orchestrator import manual_isolation as iso


@pytest.mark.parametrize('present', [False, True])
def test_package_mask_handles_python_layout_without_creating_host_paths(tmp_path, monkeypatch, present):
    work=tmp_path/'work';home=tmp_path/'home';stdlib=tmp_path/'stdlib'
    for p in [work,home,stdlib]:p.mkdir()
    packages=stdlib/'site-packages'
    if present:
        packages.mkdir();(packages/'private-package').write_text('synthetic package marker')
    before={str(p.relative_to(tmp_path)) for p in tmp_path.rglob('*')}
    monkeypatch.setattr(iso.manual_runtime,'validate_packages',lambda *a,**k:None)
    monkeypatch.setattr(iso,'runtime_mounts',lambda family:{str(stdlib):str(stdlib)})
    monkeypatch.setattr(iso.subprocess,'check_output',lambda *a,**k:str(stdlib)+'\n')
    args=iso.command(work,home,'codex',[])
    masks=[args[i+1] for i,value in enumerate(args[:-1]) if value=='--tmpfs']
    assert (str(packages) in masks) is present
    assert packages.exists() is present
    if present:assert (packages/'private-package').read_text()=='synthetic package marker'
    assert args.count('--ro-bind')==5  # stdlib plus the unchanged four synthetic /etc files
    assert '--remount-ro' in args and args[args.index('--remount-ro')+1]=='/'
    assert '--cap-drop' in args and '--clearenv' in args and '--unshare-user' in args
    # No host stdlib entry was created/changed to make an absent mask work.
    assert {str(p.relative_to(stdlib)) for p in stdlib.rglob('*')} == ({'site-packages','site-packages/private-package'} if present else set())
    assert json.loads(args[-2])['mode']=='probe'


def test_synthetic_login_fixture_never_uses_configured_host_login(tmp_path, monkeypatch):
    from test_manual_release import logins
    from orchestrator import manual_auth as auth
    outside=tmp_path/'host-login';outside.mkdir()
    marker=outside/'preserved';marker.write_text('not a credential')
    config=tmp_path/'runtime.json'
    config.write_text(json.dumps({'login_root':str(outside)}))
    monkeypatch.setenv('RESEARCH_MANUAL_RUNTIME_CONFIG',str(config))
    assert auth.login_root()==outside
    home=logins.__wrapped__(tmp_path,monkeypatch)
    assert auth.login_root().is_relative_to(home)
    assert auth.credential_path('codex').is_relative_to(home)
    assert auth.credential_path('claude').is_relative_to(home)
    assert list(outside.iterdir())==[marker]
    assert marker.read_text()=='not a credential'
    assert json.loads(config.read_text())['login_root']==str(outside)
