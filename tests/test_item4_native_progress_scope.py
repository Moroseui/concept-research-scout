"""Exercise the actual authored sibling paths with real checkpoint storage."""
from pathlib import Path
import pytest
from orchestrator import private_records as pr
from orchestrator.modal_fit_progress import FitProgress
from tools import item4_native_worker as worker


def generated(root):
    pr.mkdir(root,parents=True);pr.mkdir(root/'inputs')
    for i in range(893):pr.write_bytes(root/'inputs'/f'synthetic-{i}.bin',str(i).encode())
    return root


@pytest.fixture
def fixture(tmp_path):
    root=generated(tmp_path/'item4-native-synthetic-contract')
    return root,worker.progress_factory({'module_sha256':'c'*64})


def test_authored_sibling_calls_reopen_base_and_keep_diagnostic_separate(fixture):
    root,factory=fixture
    # Accepted21 calls: base1667, reopen1684, diagnostic1708. Full accepted
    # source AST is independently checked by the release contract rehearsal.
    first=factory(root/'durable','synthetic-fit','a'*64,'b'*64)
    reopened=factory(root/'durable','synthetic-fit','a'*64,'b'*64)
    diagnostic=factory(root/'diagnostic','synthetic-fit','a'*64,'b'*64)
    assert all(type(p) is FitProgress for p in (first,reopened,diagnostic))
    assert first.root==reopened.root and diagnostic.root!=first.root
    assert first.root.is_relative_to(root/'durable')
    assert diagnostic.root.is_relative_to(root/'diagnostic')


@pytest.mark.parametrize('suffix',['other','nested/diagnostic','diagnostic/nested','durable/../diagnostic'])
def test_arbitrary_nesting_and_traversal_refused_before_output_creation(fixture,suffix):
    root,factory=fixture
    with pytest.raises(ValueError,match='PROGRESS_SCOPE'):
        factory(root/suffix,'synthetic-fit','a'*64,'b'*64)
    assert set(p.name for p in root.iterdir())=={'inputs'}


def test_relative_mount_and_other_fit_refused(fixture,monkeypatch):
    root,factory=fixture;monkeypatch.chdir(root.parent)
    with pytest.raises(ValueError,match='PROGRESS_SCOPE'):
        factory(Path(root.name)/'diagnostic','synthetic-fit','a'*64,'b'*64)
    with pytest.raises(ValueError,match='PROGRESS_SCOPE'):
        factory(root/'diagnostic','other-fit','a'*64,'b'*64)
    assert set(p.name for p in root.iterdir())=={'inputs'}


@pytest.mark.parametrize('place',['mount','root','inputs','input-file'])
def test_synthetic_aliases_refused(fixture,tmp_path,place):
    root,factory=fixture
    if place=='mount':(root/'diagnostic').symlink_to(root/'inputs',target_is_directory=True)
    elif place=='root':
        alias=tmp_path/'item4-native-synthetic-alias';alias.symlink_to(root,target_is_directory=True);root=alias
    elif place=='inputs':
        old=root/'inputs';saved=root/'saved-inputs';old.rename(saved);old.symlink_to(saved,target_is_directory=True)
    else:(root/'inputs'/'alias').symlink_to(root/'inputs'/'synthetic-0.bin')
    with pytest.raises(ValueError,match='SYMLINK|SYNTHETIC_ALIAS|SYNTHETIC_INPUTS'):
        factory(root/'diagnostic','synthetic-fit','a'*64,'b'*64)


def test_same_factory_cannot_switch_synthetic_root(fixture,tmp_path):
    root,factory=fixture;factory(root/'durable','synthetic-fit','a'*64,'b'*64)
    other=generated(tmp_path/'item4-native-synthetic-other')
    with pytest.raises(ValueError,match='PROGRESS_ROOT_CHANGED'):
        factory(other/'diagnostic','synthetic-fit','a'*64,'b'*64)
    assert not (other/'diagnostic').exists()


def test_inputs_cannot_change_between_sibling_fits(fixture):
    root,factory=fixture;factory(root/'durable','synthetic-fit','a'*64,'b'*64)
    pr.write_bytes(root/'inputs'/'synthetic-0.bin',b'changed')
    with pytest.raises(ValueError,match='SYNTHETIC_INPUTS_CHANGED'):
        factory(root/'diagnostic','synthetic-fit','a'*64,'b'*64)


def test_missing_generated_member_refused(fixture):
    root,factory=fixture;(root/'inputs'/'synthetic-0.bin').unlink()
    with pytest.raises(ValueError,match='SYNTHETIC_INPUT_MEMBERSHIP'):
        factory(root/'diagnostic','synthetic-fit','a'*64,'b'*64)
