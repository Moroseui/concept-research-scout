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
