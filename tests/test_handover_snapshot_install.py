"""Source transfer cannot escape its isolated destination or expand without bound."""
import importlib.util
from pathlib import Path
import tarfile
from types import SimpleNamespace

import pytest


def installer():
    path=Path(__file__).parents[1]/'deploy/research-system/install_handover_fixture.py'
    spec=importlib.util.spec_from_file_location('handover_installer',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('name', ['../snapshot/code.py','/snapshot/code.py',
                                  'snapshot/../../etc/config','elsewhere/code.py'])
def test_archive_traversal_refused(name):
    item=tarfile.TarInfo(name)
    with pytest.raises(ValueError,match='ROOT'):
        installer().validate_members(SimpleNamespace(getmembers=lambda:[item]))


def test_archive_link_and_expansion_refused():
    item=tarfile.TarInfo('snapshot/code.py');item.type=tarfile.SYMTYPE
    with pytest.raises(ValueError,match='TYPE'):
        installer().validate_members(SimpleNamespace(getmembers=lambda:[item]))
    item.type=tarfile.REGTYPE;item.size=20000001
    with pytest.raises(ValueError,match='EXPANSION'):
        installer().validate_members(SimpleNamespace(getmembers=lambda:[item]))


def test_ordinary_code_archive_allowed():
    item=tarfile.TarInfo('snapshot/code.py');item.size=100
    installer().validate_members(SimpleNamespace(getmembers=lambda:[item]))


def test_source_modes_preserve_executable_identity_and_reject_links(tmp_path):
    import os
    root=tmp_path/'snapshot';root.mkdir(mode=0o700)
    code=root/'module.py';code.write_text('pass\n');code.chmod(0o600)
    executable=root/'launcher.py';executable.write_text('pass\n');executable.chmod(0o700)
    installer().readable_source(root)
    assert root.stat().st_mode & 0o777==0o755
    assert code.stat().st_mode & 0o777==0o644
    assert executable.stat().st_mode & 0o777==0o755
    assert code.read_text()==executable.read_text()=='pass\n'
    code.chmod(0o600);(root/'linked').symlink_to(code)
    with pytest.raises(ValueError,match='REGULAR_SOURCE_TREE'):
        installer().readable_source(root)
    assert code.stat().st_mode & 0o777==0o600


def test_archive_uses_only_verified_bytes_and_refuses_symlinks(tmp_path):
    import hashlib,io
    path=tmp_path/'source.tar';buffer=io.BytesIO()
    with tarfile.open(fileobj=buffer,mode='w') as archive:
        item=tarfile.TarInfo('snapshot/module.py');item.size=5
        archive.addfile(item,io.BytesIO(b'pass\n'))
    original=buffer.getvalue();path.write_bytes(original)
    raw=installer().verified_archive(path,hashlib.sha256(original).hexdigest())
    path.write_bytes(b'changed after verification')
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        assert archive.extractfile('snapshot/module.py').read()==b'pass\n'
    with pytest.raises(ValueError,match='SOURCE_ARCHIVE_CHANGED'):
        installer().verified_archive(path,hashlib.sha256(original).hexdigest())
    link=tmp_path/'linked.tar';link.symlink_to(path)
    with pytest.raises(OSError):installer().verified_archive(link,'a'*64)
