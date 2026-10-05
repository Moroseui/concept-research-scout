"""Real local Git fixtures verify explicit branch selection and retained bounds."""
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest


def builder():
    path = Path(__file__).parents[1] / 'scripts/prepare_handover_snapshot.py'
    spec = importlib.util.spec_from_file_location('snapshot_builder', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.PIPE).decode().strip()


@pytest.fixture
def source(tmp_path, monkeypatch):
    module = builder()
    root = tmp_path / 'source'
    root.mkdir()
    branch = 'fixture/isolated-reviewed-handover'
    git(root, 'init', '--initial-branch', branch)
    git(root, 'config', 'user.name', 'Synthetic fixture')
    git(root, 'config', 'user.email', 'fixture@example.invalid')
    proposal = 'campaigns/isles24-pilot/pipeline/prediction-charter-20260906-v1'
    names = ['orchestrator/fixture.py', 'scripts/verify_handover_service.py',
             'scripts/verify_protected_intake.py', 'deploy/research-system/research-system-control.sh']
    names += list(module.REQUIRED_ADMIN_SOURCE)
    names += list(module.REQUIRED_CONTINUING_SOURCE)
    names += sorted(module.scientific_support_files(root))
    names += [proposal + '/round-1/' + name for name in
              ('CHARTER.proposed.md', 'RUBRIC.proposed.md', 'PROMPTS.proposed.md',
               'P001_ADOPTION.proposed.md', 'review.json')]
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('Synthetic source fixture: ' + name + '\n')
    (root / proposal / 'receipt.json').write_text(json.dumps({'round': 1, 'input_sha256': {}}))
    (root / 'excluded-fixture.py').write_text('This unrelated fixture blob must stay out of the snapshot.\n')
    git(root, 'add', '.')
    git(root, 'commit', '-m', 'Synthetic source only')
    head = git(root, 'rev-parse', 'HEAD')
    monkeypatch.setattr(module, 'DOCUMENTS', ())
    monkeypatch.setattr(module, 'SOURCES', {})
    monkeypatch.setattr(module, 'policy_files', lambda root: set())
    monkeypatch.setattr('orchestrator.campaign_pipeline.grounding', lambda root, experiment: {})
    return module, root, head, branch, tmp_path / 'prepared'


def test_explicit_branch_clones_pinned_source_and_binds_manifest(source):
    module, root, head, branch, destination = source
    manifest = module.prepare(root, head, destination, source_branch=branch)
    snapshot = destination / 'snapshot'
    assert manifest['source'] == head and manifest['source_branch'] == branch
    assert set(module.REQUIRED_ADMIN_SOURCE) <= set(manifest['files'])
    assert set(module.REQUIRED_CONTINUING_SOURCE) <= set(manifest['files'])
    assert module.scientific_support_files(root) <= set(manifest['files'])
    assert not any('/experiments/P002/' in name or '/experiments/P003/' in name for name in manifest['files'])
    assert json.loads((destination / 'manifest.json').read_text()) == manifest
    assert git(snapshot, 'rev-parse', 'HEAD') == head
    assert git(snapshot, 'config', '--get', 'remote.origin.fetch') == f'+refs/heads/{branch}:refs/remotes/origin/{branch}'
    assert not (snapshot / 'excluded-fixture.py').exists()
    excluded = git(root, 'rev-parse', head + ':excluded-fixture.py')
    objects = git(snapshot, 'cat-file', '--batch-all-objects', '--batch-check=%(objectname) %(objecttype)')
    assert excluded not in objects
    blobs = [line for line in objects.splitlines() if line.endswith(' blob')]
    assert len(blobs) == manifest['physical_blob_count'] == len(manifest['files'])
    original = (destination / 'manifest.json').read_bytes()
    with pytest.raises(ValueError, match='FRESH_EXTERNAL_DESTINATION_REQUIRED'):
        module.prepare(root, head, destination, source_branch=branch)
    assert (destination / 'manifest.json').read_bytes() == original


def test_historical_default_is_preserved(source):
    module, root, head, branch, destination = source
    # Create a fixture with the historical branch; no real project ref is renamed.
    git(root, 'switch', '-c', module.DEFAULT_SOURCE_BRANCH)
    manifest = module.prepare(root, head, destination)
    assert manifest['source_branch'] == 'astra/infrastructure-milestone-record'


def test_missing_installer_dependency_refuses_before_snapshot(source):
    module, root, _, branch, destination = source
    git(root, 'rm', '--', module.REQUIRED_ADMIN_SOURCE[0])
    git(root, 'commit', '-m', 'Synthetic missing installer')
    head = git(root, 'rev-parse', 'HEAD')
    with pytest.raises(ValueError, match='MANDATORY_INSTALL_SOURCE_MISSING'):
        module.prepare(root, head, destination, source_branch=branch)
    assert not destination.exists()


@pytest.mark.parametrize('name', ['scripts/pilot_review.py', 'scripts/package_pilot.py',
    'tests/test_pilot_notebook_acquisition.py',
    'deploy/research-system/research-system-scientific-job@.service.in'])
def test_missing_materialization_or_courier_input_refuses_before_snapshot(source, name):
    module, root, _, branch, destination = source
    git(root, 'rm', '--', name)
    git(root, 'commit', '-m', 'Synthetic missing scientific support')
    with pytest.raises(ValueError, match='MANDATORY_SCIENTIFIC_SUPPORT_MISSING'):
        module.prepare(root, git(root, 'rev-parse', 'HEAD'), destination, source_branch=branch)
    assert not destination.exists()


@pytest.mark.parametrize('mode', ['different-branch', 'default-on-isolated', 'detached', 'wrong-pin', 'dirty', 'empty'])
def test_refusals_happen_before_destination_creation(source, mode):
    module, root, head, branch, destination = source
    kwargs = {'source_branch': branch}
    expected = 'SOURCE_BRANCH_MISMATCH'
    if mode == 'different-branch':
        kwargs['source_branch'] = 'fixture/other'
    elif mode == 'default-on-isolated':
        kwargs = {}
    elif mode == 'detached':
        git(root, 'checkout', '--detach', head)
    elif mode == 'wrong-pin':
        head = '0' * 40
        expected = 'SOURCE_HEAD_CHANGED'
    elif mode == 'dirty':
        (root / 'orchestrator/fixture.py').write_text('Changed fixture source')
        expected = 'SOURCE_WORKTREE_CHANGED'
    else:
        kwargs['source_branch'] = ''
        expected = 'EXPLICIT_SOURCE_BRANCH_REQUIRED'
    with pytest.raises(ValueError, match=expected):
        module.prepare(root, head, destination, **kwargs)
    assert not destination.exists()


def test_selected_blob_scan_still_refuses_before_clone(source, monkeypatch):
    module, root, head, branch, destination = source
    def refuse(name, raw):
        raise ValueError('FIXTURE_EXISTING_SCAN_REFUSAL')
    monkeypatch.setattr(module, 'scan', refuse)
    with pytest.raises(ValueError, match='FIXTURE_EXISTING_SCAN_REFUSAL'):
        module.prepare(root, head, destination, source_branch=branch)
    assert not destination.exists()


def test_exact_template_still_passes_the_existing_content_guard(source):
    module, root, _, branch, destination = source
    (root/module.SERVICE_TEMPLATES[0]).write_bytes(b'Unsafe fixture\x00\n')
    git(root, 'add', '.'); git(root, 'commit', '-m', 'Synthetic invalid template content')
    with pytest.raises(ValueError, match='PUBLICATION_CONTENT_REJECTED'):
        module.prepare(root, git(root, 'rev-parse', 'HEAD'), destination, source_branch=branch)
    assert not destination.exists()


def test_extra_physical_blob_is_rejected_and_failed_snapshot_preserved(source, monkeypatch):
    module, root, head, branch, destination = source
    original = subprocess.check_output
    def changed_inventory(command, **kwargs):
        if command[1:3] == ['cat-file', '--batch-all-objects']:
            return original(command, **kwargs) + b'0000000000000000000000000000000000000000 blob\n'
        return original(command, **kwargs)
    monkeypatch.setattr(module.subprocess, 'check_output', changed_inventory)
    with pytest.raises(ValueError, match='UNEXPECTED_OR_MISSING_PHYSICAL_BLOBS'):
        module.prepare(root, head, destination, source_branch=branch)
    assert (destination / 'snapshot').is_dir()
    assert not (destination / 'manifest.json').exists()
    assert not (destination / 'snapshot.tar.gz').exists()
