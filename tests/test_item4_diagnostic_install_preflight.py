"""Refuse changed state topology without touching existing ownership/modes."""
from pathlib import Path
from types import SimpleNamespace
import stat
import pytest
from tools import install_item4_diagnostic_native as install

PARENT=Path('/var/lib/research-system-manual-sprint10/environment-inventory')

def topology(monkeypatch,changed=None,symlink=None):
    values={PARENT:(0,1003,stat.S_IFDIR|0o750),PARENT.parent:(1003,1003,stat.S_IFDIR|0o700)}
    if changed:values[changed[0]]=changed[1]
    def info(path):
        uid,gid,mode=values.get(path,(0,0,stat.S_IFDIR|0o755))
        return SimpleNamespace(st_uid=uid,st_gid=gid,st_mode=mode)
    monkeypatch.setattr(Path,'lstat',info)
    monkeypatch.setattr(Path,'is_symlink',lambda p:p==symlink)
    # Any attempt to modify an existing directory must fail the test.
    monkeypatch.setattr(Path,'chmod',lambda *a:pytest.fail('existing permissions changed'))
    monkeypatch.setattr(install.os,'chown',lambda *a:pytest.fail('existing ownership changed'))

def test_existing_private_root_inventory_passes(monkeypatch):
    topology(monkeypatch);install.state_parent(PARENT)

@pytest.mark.parametrize('path',[PARENT,PARENT.parent,Path('/var/lib'),Path('/var'),Path('/')])
def test_symlink_at_each_level_refused(monkeypatch,path):
    topology(monkeypatch,symlink=path)
    with pytest.raises(ValueError):install.state_parent(PARENT)

@pytest.mark.parametrize('path,values',[
 (PARENT,(1003,1003,stat.S_IFDIR|0o750)),
 (PARENT,(0,0,stat.S_IFDIR|0o750)),
 (PARENT,(0,1003,stat.S_IFDIR|0o770)),
 (PARENT,(0,1003,stat.S_IFDIR|0o755)),
 (PARENT,(0,1003,stat.S_IFREG|0o750)),
 (PARENT.parent,(0,1003,stat.S_IFDIR|0o700)),
 (PARENT.parent,(1003,0,stat.S_IFDIR|0o700)),
 (PARENT.parent,(1003,1003,stat.S_IFDIR|0o750)),
 (PARENT.parent,(1003,1003,stat.S_IFDIR|0o777)),
 (Path('/var/lib'),(1003,0,stat.S_IFDIR|0o755)),
 (Path('/var/lib'),(0,0,stat.S_IFDIR|0o775)),
])
def test_changed_ownership_mode_or_type_refused(monkeypatch,path,values):
    topology(monkeypatch,changed=(path,values))
    with pytest.raises(ValueError):install.state_parent(PARENT)

def test_unrelated_state_parent_refused(monkeypatch):
    topology(monkeypatch)
    with pytest.raises(ValueError,match='STATE_PARENT_PATH'):install.state_parent(PARENT/'unexpected')
