"""Exact pre-existing data layout is distinct from root-owned code/config."""
from pathlib import Path
import stat
from types import SimpleNamespace as NS
import pytest
from tools import install_item4_image_runtime as install
from orchestrator import manual_host_guard


@pytest.fixture
def parents(monkeypatch):
    rows={install.STATE_PARENT:NS(st_uid=0,st_gid=1003,st_mode=stat.S_IFDIR|0o750),
          install.STATE_PARENT.parent:NS(st_uid=1003,st_gid=1003,st_mode=stat.S_IFDIR|0o700)}
    oldstat=Path.lstat;oldexists=Path.exists
    monkeypatch.setattr(Path,'lstat',lambda p:rows[p] if p in rows else oldstat(p))
    monkeypatch.setattr(Path,'exists',lambda p:True if p in rows else oldexists(p))
    seen=[];monkeypatch.setattr(manual_host_guard,'trusted',lambda p:seen.append(p) or p)
    return rows,seen


def test_exact_service_owned_data_ancestor_passes_without_permissions_mutation(parents):
    rows,seen=parents;before=[(p,x.st_uid,x.st_gid,x.st_mode) for p,x in rows.items()]
    assert install.destination_parent(install.STATE)==install.STATE_PARENT
    assert seen==[install.STATE_PARENT.parent.parent]
    assert before==[(p,x.st_uid,x.st_gid,x.st_mode) for p,x in rows.items()]


@pytest.mark.parametrize('which,field,value',[(0,'st_uid',1003),(0,'st_gid',0),(0,'st_mode',stat.S_IFDIR|0o770),
 (0,'st_mode',stat.S_IFLNK|0o750),(0,'st_mode',stat.S_IFREG|0o750),(1,'st_uid',0),(1,'st_gid',0),
 (1,'st_mode',stat.S_IFDIR|0o750),(1,'st_mode',stat.S_IFDIR|0o777),(1,'st_mode',stat.S_IFLNK|0o700)])
def test_wrong_identity_alias_type_or_permissions_refuse(parents,which,field,value):
    rows,seen=parents;target=list(rows)[which];setattr(rows[target],field,value)
    with pytest.raises(ValueError,match='IMAGE_STATE_PARENT_CHANGED'):install.destination_parent(install.STATE)
    assert seen==[]


def test_missing_exact_existing_parent_refuses(parents,monkeypatch):
    rows,seen=parents;old=Path.exists
    monkeypatch.setattr(Path,'exists',lambda p:False if p==install.STATE_PARENT else old(p))
    with pytest.raises(ValueError,match='IMAGE_STATE_PARENT_MISSING'):install.destination_parent(install.STATE)
    assert seen==[]


@pytest.mark.parametrize('path',[install.STATE_PARENT/'another-state',Path('/opt/research-system/manual-repair-helpers/image'),
 Path('/etc/research-system-manual-sprint10/image-config'),Path('/var/lib/research-system-manual-sprint10-deployment/image-record')])
def test_every_other_destination_retains_root_only_ancestor_guard(parents,monkeypatch,path):
    def refuse(p):raise ValueError('HOST_PROOF_NOT_ROOT_OWNED')
    monkeypatch.setattr(manual_host_guard,'trusted',refuse)
    with pytest.raises(ValueError,match='HOST_PROOF_NOT_ROOT_OWNED'):install.destination_parent(path)
