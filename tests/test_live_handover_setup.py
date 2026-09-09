import copy
import fcntl
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'live_handover_setup', ROOT / 'deploy/research-system/prepare_live_handover_setup.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def inputs():
    return {
        'source': 'a' * 40,
        'approval_raw': (ROOT / m.APPROVAL).read_bytes(),
        'policy': json.loads((ROOT / m.POLICY_FILE).read_text()),
        'identity': json.loads((ROOT / m.IDENTITY_FILE).read_text()),
        'writer': {'app_id': 4879374, 'installation_id': 160193942,
                   'repository_id': 1323461276, 'private_key': '/etc/research-system/writer/key.pem',
                   'permission_decision': 'existing verified private configuration'},
        'broker': {'mode': 'SYNTHETIC_FIXTURE', 'repository': m.REMOTE, 'branch': m.BRANCH,
                   'controller_uid': 997, 'operator_uids': [0], 'sources': ['b' * 40],
                   'ledger_repo': '/var/lib/research-system/handover-broker/ledger',
                   'publication_root': '/var/lib/research-system/handover-broker/publication-disabled',
                   'turn_root': '/var/lib/research-system/handover-broker/consumed-turns',
                   'writer_config': None, 'model_mode': 'SUPERVISED', 'max_model_turns': 1},
        'runtime': {'controller_uid': 997, 'source': 'b' * 40,
                    'state': '/var/lib/research-system/handover-controller',
                    'report_schedule': None, 'publication': None},
        'destination': '/etc/research-system/live-setup/proposal',
        'writer_path': '/etc/research-system/writer/config.json'}


def test_exact_shared_policy_and_disabled_broker_match_existing_consumers():
    from orchestrator.dispatch_limiter import policy
    from orchestrator.protected_handover import Broker
    from orchestrator.actions_admission_wait import observe
    from orchestrator.dispatch_limiter import initial
    value = inputs()
    original = copy.deepcopy(value)
    configured, deployment = m.plan(**value)
    assert value == original
    assert policy(configured['policy']) == 48
    assert configured['policy'] == m.approved_policy()
    assert deployment['policy_sha256'] == m.policy_digest(configured['policy'])
    assert Broker(configured).config['model_mode'] == 'DISABLED'
    assert configured['max_model_turns'] == 0
    assert configured['sources'] == [value['source']]
    assert 'activation_decision_sha256' not in configured
    state = {**initial(), 'policy_sha256': deployment['policy_sha256']}
    request = {'repository_id': 1323461276, 'run_id': '12', 'attempt': '1',
               'source': 'a' * 40, 'branch': 'main', 'workflow_sha256': 'b' * 64}
    assert observe(request, state, m.policy_digest(value['policy']))['status'] == 'WAITING_ADMISSION'
    changed = {**value['policy'], 'note': 'apparently harmless wording'}
    with pytest.raises(ValueError, match='SHARED_POLICY_BINDING_CHANGED'):
        observe(request, state, m.policy_digest(changed))


@pytest.mark.parametrize('change', [
    {'n': 96}, {'n': 48.0}, {'version': True}, {'status': 'PROPOSED'},
    {'reset_operators': ['ssh-uid:997']}, {'server_semantics': 'UNBOUNDED'},
    {'operator_approval': 'unbound approval'}, {'state_ref': 'refs/heads/main'},
    {'note': 'changing an incidental field changes the shared hash'}])
def test_reject_policy_drift(change):
    value = inputs()
    value['policy'].update(change)
    with pytest.raises(ValueError, match='EXACT_APPROVED_SHARED_POLICY_REQUIRED'):
        m.plan(**value)


@pytest.mark.parametrize('field,change,reason', [
    ('identity', {'installation_id': 1}, 'IDENTITY'),
    ('identity', {'permissions': {'contents': 'write', 'actions': 'write', 'metadata': 'read'}}, 'IDENTITY'),
    ('identity', {'total_repositories': 2}, 'IDENTITY'),
    ('writer', {'app_id': True}, 'CONFIGURATION'),
    ('writer', {'token': 'must not be accepted'}, 'CONFIGURATION'),
    ('broker', {'writer_config': '/existing/live/config'}, 'SCIENCE'),
    ('broker', {'mode': 'LIVE_APPROVED'}, 'SCIENCE'),
    ('broker', {'max_model_turns': 0}, 'SCIENCE'),
    ('runtime', {'controller_uid': 998}, 'SCIENCE')])
def test_refuse_changed_authority_identity_or_existing_live_fixture(field, change, reason):
    value = inputs()
    value[field].update(change)
    with pytest.raises(ValueError, match=reason):
        m.plan(**value)


def test_refuse_approval_change_and_preserved_state_overlap():
    value = inputs()
    value['approval_raw'] += b' '
    with pytest.raises(ValueError, match='EXACT_OPERATOR_APPROVAL_REQUIRED'):
        m.plan(**value)
    value = inputs()
    value['broker']['ledger_repo'] = str(m.STATE_BASE)
    with pytest.raises(ValueError, match='EXISTING_SCIENCE_STATE_OVERLAP'):
        m.plan(**value)


def test_private_metadata_rejects_nonprivate_file_without_reading(tmp_path):
    path = tmp_path / 'not-private'
    path.write_text('not a credential')
    path.chmod(0o644)
    with pytest.raises(ValueError, match='ROOT_PROTECTED_INPUT_REQUIRED'):
        m.protected_metadata(path, private=True)


@pytest.fixture
def prepared_environment(tmp_path, monkeypatch):
    """Emulate root-owned input metadata; test real byte writes and preservation.

    The production ownership check has a separate denial test. CI need not run as
    root or write /etc, and source checking is already tested by its existing suite.
    """
    config = tmp_path / 'config'
    config.mkdir(mode=0o700)
    parent = config / 'preparation'
    parent.mkdir(mode=0o700)
    monkeypatch.setattr(m, 'CONFIG_BASE', config)
    monkeypatch.setattr(m, 'STATE_BASE', tmp_path / 'planned-state')
    monkeypatch.setattr(m.os, 'getuid', lambda: 0)
    real_lstat = Path.lstat

    def metadata(path, *, private=False):
        result = real_lstat(Path(path))
        assert result.st_mode & (0o077 if private else 0o022) == 0
        return result

    monkeypatch.setattr(m, 'protected_metadata', metadata)

    def lstat(path):
        result = real_lstat(path)
        if path == parent:
            return SimpleNamespace(st_mode=result.st_mode, st_uid=0)
        return result

    monkeypatch.setattr(Path, 'lstat', lstat)
    monkeypatch.setattr('orchestrator.remote_supervisor.checked_source', lambda root, source: root)
    value = inputs()
    key = config / 'writer.pem'
    key.write_bytes(b'PRIVATE TEST SENTINEL NEVER READ')
    key.chmod(0o600)
    value['writer']['private_key'] = str(key)
    science = tmp_path / 'science'
    for name in ('ledger_repo', 'publication_root', 'turn_root'):
        directory = science / name
        directory.mkdir(parents=True, mode=0o700)
        (directory / 'preserved.original').write_bytes(b'consumed evidence; never reset')
        value['broker'][name] = str(directory)
    paths = {}
    for name in ('broker', 'runtime', 'writer'):
        path = config / (name + '.json')
        path.write_bytes(m.encoded(value[name]))
        path.chmod(0o640 if name == 'runtime' else 0o600)
        paths[name] = path
    destination = parent / 'result'
    params = {'source': value['source'], 'writer_config': str(paths['writer']),
              'destination': str(destination), 'broker_config': str(paths['broker']),
              'runtime_config': str(paths['runtime'])}
    before = {name: path.read_bytes() for name, path in paths.items()}
    # Fail if any code opens the PEM, starts a process or touches remote services.
    real_open = os.open

    def checked_open(path, *args, **kwargs):
        assert Path(path) != key, 'Preparation must not open the private key'
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(m.os, 'open', checked_open)
    monkeypatch.setattr('subprocess.run', lambda *a, **k: pytest.fail('No deployment or Git command'))
    monkeypatch.setattr('orchestrator.protected_writer.credentials', lambda *a, **k: pytest.fail('No token'))
    return params, paths, destination, before


def test_prepare_preserves_science_and_key_and_emits_only_private_proposals(prepared_environment):
    params, paths, destination, before = prepared_environment
    result = m.prepare(**params)
    assert result['status'] == 'LIVE_HANDOVER_SETUP_PREPARED_NOT_INSTALLED'
    assert result['remote_operations'] == 0 and result['models_started'] == 0
    assert result['writer_key_contents_read'] is False and result['state_initialized'] is False
    assert not m.STATE_BASE.exists()
    assert {name: path.read_bytes() for name, path in paths.items()} == before
    assert (destination / 'broker.original.bytes').read_bytes() == before['broker']
    assert (destination / 'runtime.original.bytes').read_bytes() == before['runtime']
    assert (destination / 'dispatch-limiter.approved.json').read_bytes() == (ROOT / m.POLICY_FILE).read_bytes()
    assert all(p.stat().st_mode & 0o777 == 0o600 for p in destination.iterdir())
    science = Path(json.loads(before['broker'])['turn_root']).parent
    assert len(list(science.glob('*/preserved.original'))) == 3
    assert all(p.read_bytes() == b'consumed evidence; never reset'
               for p in science.glob('*/preserved.original'))
    original = {p.name: p.read_bytes() for p in destination.iterdir()}
    with pytest.raises(ValueError, match='EXISTING_OR_PARTIAL_SETUP_RECONCILE'):
        m.prepare(**params)
    assert original == {p.name: p.read_bytes() for p in destination.iterdir()}


def test_existing_partial_destination_and_planned_live_state_refuse(prepared_environment):
    params, paths, destination, before = prepared_environment
    destination.mkdir(mode=0o700)
    (destination / 'interrupted').write_bytes(b'preserve')
    with pytest.raises(ValueError, match='EXISTING_OR_PARTIAL_SETUP_RECONCILE'):
        m.prepare(**params)
    assert (destination / 'interrupted').read_bytes() == b'preserve'
    params['destination'] = str(destination.with_name('another'))
    policy = json.loads((ROOT / m.POLICY_FILE).read_text())
    planned = m.STATE_BASE / ('live-setup-' + params['source'][:12] + '-' + m.policy_digest(policy)[:12])
    planned.mkdir(parents=True)
    with pytest.raises(ValueError, match='EXISTING_LIVE_STATE_RECONCILE'):
        m.prepare(**params)
    assert not Path(params['destination']).exists()
    assert {name: path.read_bytes() for name, path in paths.items()} == before


def test_concurrent_preparation_refuses_without_creating_output(prepared_environment):
    params, paths, destination, before = prepared_environment
    fd = os.open(m.CONFIG_BASE, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(ValueError, match='CONCURRENT_SETUP_RECONCILE'):
            m.prepare(**params)
    finally:
        os.close(fd)
    assert not destination.exists()
    assert {name: path.read_bytes() for name, path in paths.items()} == before


def test_concurrent_input_change_preserves_partial_without_success_receipt(prepared_environment, monkeypatch):
    params, paths, destination, before = prepared_environment
    original_write = m.write_new
    changed = False

    def change_during_write(path, raw):
        nonlocal changed
        original_write(path, raw)
        if not changed:
            changed = True
            paths['runtime'].write_bytes(before['runtime'] + b' ')

    monkeypatch.setattr(m, 'write_new', change_during_write)
    with pytest.raises(ValueError, match='SCIENCE_OR_WRITER_CONFIGURATION_CHANGED'):
        m.prepare(**params)
    assert destination.exists() and not (destination / 'receipt.json').exists()
    assert (destination / 'runtime.original.bytes').read_bytes() == before['runtime']
    assert paths['runtime'].read_bytes() == before['runtime'] + b' '
    assert paths['broker'].read_bytes() == before['broker']
