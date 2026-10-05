"""Offline credential-routing checks; all credential values here are synthetic."""
import base64
import copy
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
from unittest.mock import patch
import zipfile

import pytest
import yaml

from orchestrator import model_secret_relocation as m

SOURCE = 'a' * 40
RUN_ID = '12345'


def identity():
    return {'source': SOURCE, 'run_id': RUN_ID, 'attempt': '1', 'actor': 'fixture-operator',
            'workflow_ref': m.REPOSITORY + '/' + m.WORKFLOW + '@refs/heads/main', 'request': m.REQUEST}


def valid_manifest():
    # Structurally valid synthetic bytes, not a claim of real encryption.
    cipher = bytes(range(128, 256))
    return {'schema': m.SCHEMA, 'kind': 'GITHUB_ENVIRONMENT_SEALED_BOX', 'recipient': m.target(),
            'run': identity(), 'reviewed_source': SOURCE, 'preflight_sha256': 'b' * 64,
            'secrets': {name: {'encrypted_value': base64.b64encode(cipher).decode(),
                              'ciphertext_sha256': m.sha(cipher)} for name in m.NAMES}}


def test_fixed_recipient_and_closed_names_are_required():
    good = valid_manifest()
    assert m.validate(good, source=SOURCE, run_id=RUN_ID) == good
    for name, changed in [('repository', 'somewhere/else'), ('repository_id', 1),
                          ('environment', 'unrestricted'), ('environment_id', 1),
                          ('key_id', 'another-key'), ('public_key', 'A' * 44)]:
        value = copy.deepcopy(good)
        value['recipient'][name] = changed
        with pytest.raises(ValueError, match='RECIPIENT_MISMATCH'):
            m.validate(value, source=SOURCE, run_id=RUN_ID)
    for names in ({}, {**good['secrets'], 'OTHER_SECRET': {}}):
        value = dict(good, secrets=names)
        with pytest.raises(ValueError, match='SECRET_NAMES_OR_BINDING'):
            m.validate(value, source=SOURCE, run_id=RUN_ID)


def test_plaintext_extra_fields_hash_changes_and_size_are_refused():
    good = valid_manifest()
    for replacement in ('synthetic-plaintext', base64.b64encode(b'synthetic plaintext ' * 10).decode(),
                        base64.b64encode(b'\xff' * (m.MAX_SECRET + 49)).decode()):
        value = copy.deepcopy(good)
        value['secrets'][m.NAMES[0]]['encrypted_value'] = replacement
        try:
            value['secrets'][m.NAMES[0]]['ciphertext_sha256'] = m.sha(base64.b64decode(replacement, validate=True))
        except ValueError:
            pass
        with pytest.raises(ValueError):
            m.validate(value, source=SOURCE, run_id=RUN_ID)
    value = copy.deepcopy(good)
    value['secrets'][m.NAMES[0]]['ciphertext_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='HASH_CHANGED'):
        m.validate(value, source=SOURCE, run_id=RUN_ID)
    value = copy.deepcopy(good)
    value['secrets'][m.NAMES[0]]['plaintext'] = 'synthetic source value'
    with pytest.raises(ValueError, match='FIELDS_REQUIRED'):
        m.validate(value, source=SOURCE, run_id=RUN_ID)


def test_original_main_run_and_canonical_manifest_are_required():
    good = valid_manifest()
    for field, change in [('attempt', '2'), ('workflow_ref', 'other/workflow'), ('request', 'other'),
                          ('source', 'b' * 40), ('run_id', '67890')]:
        value = copy.deepcopy(good)
        value['run'][field] = change
        with pytest.raises(ValueError):
            m.validate(value, source=SOURCE, run_id=RUN_ID)
    raw = m.encoded(good) + b'\n'
    assert m.manifest(raw, source=SOURCE, run_id=RUN_ID) == good
    for bad in (raw + b' ', b'{"kind":"synthetic plaintext",' + raw[1:], b' ' * (m.MAX_MANIFEST + 1)):
        with pytest.raises(ValueError):
            m.manifest(bad, source=SOURCE, run_id=RUN_ID)


def test_configuration_cannot_select_another_public_key(tmp_path):
    for name in (m.CONFIG, m.GRANT):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((m.ROOT / name).read_bytes())
    assert m.target(tmp_path) == m.target()
    value = m.target()
    value['public_key'] = base64.b64encode(b'\x01' * 32).decode()
    value['public_key_sha256'] = m.sha(value['public_key'].encode())
    (tmp_path / m.CONFIG).write_bytes(m.encoded(value))
    with pytest.raises(ValueError, match='FIXED_RECIPIENT'):
        m.target(tmp_path)


def test_real_sealed_box_preserves_exact_bytes_and_emits_only_ciphertext(tmp_path, monkeypatch, capsys):
    public = pytest.importorskip('nacl.public', reason='Dedicated hash-locked relocation dependency required')
    private = public.PrivateKey.generate()
    recipient = m.target()
    recipient['public_key'] = base64.b64encode(bytes(private.public_key)).decode()
    values = {name: 'synthetic ' + name + ' value with a final newline\n' for name in m.NAMES}
    for name, value in values.items():
        monkeypatch.setenv('SOURCE_' + name, value)
    before = {'schema': m.SCHEMA + '/preflight', 'run': identity(), 'recipient': recipient,
              'reviewed_source': SOURCE, 'checked_at_utc': datetime.now(timezone.utc).isoformat()}
    path = tmp_path / 'preflight.json'
    path.write_bytes(m.encoded(before) + b'\n')
    with patch.object(m, 'hosted_identity', return_value=identity()), patch.object(m, 'source_review', return_value=SOURCE), patch.object(m, 'target', return_value=recipient):
        result = m.seal(path, tmp_path / 'out' / 'manifest.json', source=SOURCE)
    raw = (tmp_path / 'out' / 'manifest.json').read_bytes()
    saved = json.loads(raw)
    for name, value in values.items():
        assert value.encode() not in raw
        assert base64.b64encode(value.encode()) not in raw
        cipher = base64.b64decode(saved['secrets'][name]['encrypted_value'])
        assert public.SealedBox(private).decrypt(cipher) == value.encode()
    assert result['status'] == 'CIPHERTEXT_PREPARED_NOT_STAGED'
    assert (tmp_path / 'out' / 'manifest.json').stat().st_mode & 0o077 == 0
    assert capsys.readouterr().out == ''


def test_preflight_stops_duplicate_run_without_reading_source_secrets(tmp_path):
    calls = []
    def request(endpoint, **kwargs):
        calls.append(endpoint)
        return {'total_count': 2, 'workflow_runs': [{'id': int(RUN_ID), 'head_sha': SOURCE}, {'id': 999, 'head_sha': SOURCE}]}
    with patch.object(m, 'hosted_identity', return_value=identity()), patch.object(m, 'source_review', return_value=SOURCE), patch.object(m, 'remote_target', return_value=m.target()), patch.object(m, 'api', side_effect=request):
        with pytest.raises(ValueError, match='EXISTING_RUN_RECONCILE'):
            m.preflight(SOURCE, tmp_path / 'preflight.json')
    assert len(calls) == 1
    assert not (tmp_path / 'preflight.json').exists()


def test_remote_recipient_policy_and_existing_values_fail_before_put():
    target = m.target()
    values = [{'id': m.REPOSITORY_ID, 'default_branch': 'main'},
              {'id': m.ENVIRONMENT_ID, 'name': m.ENVIRONMENT,
               'deployment_branch_policy': {'protected_branches': False, 'custom_branch_policies': True}},
              {'total_count': 1, 'branch_policies': [{'name': 'main', 'type': 'branch'}]},
              {'key_id': m.KEY_ID, 'key': target['public_key']}]
    with patch.object(m, 'api', side_effect=values):
        assert m.remote_target() == target
    for index, replacement in [(1, dict(values[1], id=1)), (2, {'total_count': 0, 'branch_policies': []}),
                               (3, {'key_id': 'rotated', 'key': target['public_key']})]:
        changed = copy.deepcopy(values)
        changed[index] = replacement
        with patch.object(m, 'api', side_effect=changed), pytest.raises(ValueError, match='REMOTE_RECIPIENT_OR_POLICY'):
            m.remote_target()
    with patch.object(m, 'api', side_effect=values + [{'total_count': 1, 'secrets': [{'name': m.NAMES[0]}]}, {}]), pytest.raises(ValueError, match='EXISTING_ENVIRONMENT_VALUES'):
        m.remote_target(require_empty=True)


def test_runner_checks_public_metadata_without_environment_secret_permissions(tmp_path):
    recipient = m.target()
    values = [{'id': m.REPOSITORY_ID, 'default_branch': 'main'},
              {'id': m.ENVIRONMENT_ID, 'name': m.ENVIRONMENT,
               'deployment_branch_policy': {'protected_branches': False, 'custom_branch_policies': True}},
              {'total_count': 1, 'branch_policies': [{'name': 'main', 'type': 'branch'}]},
              {'total_count': 1, 'workflow_runs': [{'id': int(RUN_ID), 'head_sha': SOURCE}]}]
    with patch.object(m, 'api', side_effect=values) as api, \
            patch.object(m, 'hosted_identity', return_value=identity()), \
            patch.object(m, 'source_review', return_value=SOURCE):
        assert m.preflight(SOURCE, tmp_path/'preflight.json')['recipient'] == recipient
        assert not any('/secrets' in call.args[0] for call in api.call_args_list)
    with patch.object(m, 'api', side_effect=values[:3]), \
            pytest.raises(ValueError, match='OWNER_KEY_VALIDATION_REQUIRED'):
        m.remote_target(require_empty=True, read_key=False)


def test_owner_staging_serializes_concurrent_operations(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    import time
    entered = threading.Event()
    active = 0
    maximum = 0
    def operation(*args):
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        entered.set()
        time.sleep(0.03)
        active -= 1
        return {'status': 'synthetic-serialized'}
    with patch.object(m, '_stage_locked', side_effect=operation), ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(m.stage, RUN_ID, SOURCE, tmp_path/'state')
        assert entered.wait(2)
        second = pool.submit(m.stage, RUN_ID, SOURCE, tmp_path/'state')
        assert first.result() == second.result()
    assert maximum == 1


def artifact_fixture():
    raw = m.encoded(valid_manifest()) + b'\n'
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as bundle:
        bundle.writestr('manifest.json', raw)
    archive = stream.getvalue()
    run = {'repository': {'id': m.REPOSITORY_ID}, 'head_sha': SOURCE, 'head_branch': 'main',
           'event': 'workflow_dispatch', 'path': m.WORKFLOW, 'run_attempt': 1,
           'status': 'completed', 'conclusion': 'success', 'actor': {'login': identity()['actor']}}
    artifact = {'id': 42, 'name': m.REQUEST, 'expired': False, 'size_in_bytes': len(archive),
                'workflow_run': {'id': int(RUN_ID), 'head_sha': SOURCE}}
    return raw, run, {'total_count': 1, 'artifacts': [artifact]}, archive


def test_artifact_origin_rejects_other_workflow_or_source():
    raw, run, listing, archive = artifact_fixture()
    with patch.object(m, 'api', side_effect=[run, listing, archive]):
        assert m.original_artifact(RUN_ID, SOURCE)[0] == raw
    for changed in (dict(run, path='.github/workflows/another.yml'), dict(run, run_attempt=2), dict(run, head_sha='b' * 40)):
        with patch.object(m, 'api', return_value=changed) as request, pytest.raises(ValueError, match='ORIGINAL_SUCCESSFUL_WORKFLOW'):
            m.original_artifact(RUN_ID, SOURCE)
        assert request.call_count == 1
    changed = copy.deepcopy(listing)
    changed['artifacts'][0]['workflow_run']['head_sha'] = 'b' * 40
    with patch.object(m, 'api', side_effect=[run, changed]) as request, pytest.raises(ValueError, match='ARTIFACT_IDENTITY'):
        m.original_artifact(RUN_ID, SOURCE)
    assert request.call_count == 2


def test_stage_uses_three_fixed_ciphertext_puts_preserves_originals_and_deduplicates(tmp_path, monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    raw, _, _, archive = artifact_fixture()
    original = {'run_id': RUN_ID, 'source': SOURCE, 'artifact_id': 42,
                'archive_sha256': m.sha(archive), 'manifest_sha256': m.sha(raw)}
    calls = []
    def request(endpoint, **kwargs):
        calls.append((endpoint, kwargs))
        if endpoint.endswith('git/ref/heads/main'):
            return {'object': {'sha': SOURCE}}
        if kwargs.get('method') == 'PUT':
            assert set(kwargs['payload']) == {'encrypted_value', 'key_id'}
            assert kwargs['payload']['key_id'] == m.KEY_ID
            assert endpoint.startswith(m.endpoint('environments/' + m.ENVIRONMENT + '/secrets/'))
            return None
        return {'name': endpoint.rsplit('/', 1)[-1]}
    with patch.object(m, 'source_review', return_value=SOURCE), patch.object(m, 'original_artifact', return_value=(raw, original)), patch.object(m, 'remote_target', return_value=m.target()), patch.object(m, 'api', side_effect=request):
        result = m.stage(RUN_ID, SOURCE, tmp_path / 'state')
        assert result['repository_secrets_removed'] is False
        assert result['puts_this_call'] == 3
        before = len([c for c in calls if c[1].get('method') == 'PUT'])
        assert m.stage(RUN_ID, SOURCE, tmp_path / 'state')['puts_this_call'] == 0
    assert before == 3 == len([c for c in calls if c[1].get('method') == 'PUT'])
    assert not any('/actions/secrets/' in c[0] for c in calls)


def test_partial_or_uncertain_stage_preserves_intent_and_refuses_retry(tmp_path, monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    raw, _, _, archive = artifact_fixture()
    original = {'run_id': RUN_ID, 'source': SOURCE, 'artifact_id': 42,
                'archive_sha256': m.sha(archive), 'manifest_sha256': m.sha(raw)}
    puts = []
    def request(endpoint, **kwargs):
        if kwargs.get('method') == 'PUT':
            puts.append(endpoint)
            raise TimeoutError('Synthetic ambiguous transport interruption')
        return {'object': {'sha': SOURCE}}
    with patch.object(m, 'source_review', return_value=SOURCE), patch.object(m, 'original_artifact', return_value=(raw, original)), patch.object(m, 'remote_target', return_value=m.target()), patch.object(m, 'api', side_effect=request):
        with pytest.raises(TimeoutError):
            m.stage(RUN_ID, SOURCE, tmp_path / 'state')
        assert (tmp_path / 'state' / RUN_ID / ('intent-' + m.NAMES[0] + '.json')).exists()
        with pytest.raises(ValueError, match='PARTIAL_STAGING_RECONCILE'):
            m.stage(RUN_ID, SOURCE, tmp_path / 'state')
    assert len(puts) == 1


def test_stage_cannot_run_inside_actions_or_select_a_path(tmp_path, monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    with patch.object(m, 'api') as request, pytest.raises(ValueError, match='OWNER_ROUTE_OUTSIDE_ACTIONS'):
        m.stage(RUN_ID, SOURCE, tmp_path)
    request.assert_not_called()
    monkeypatch.delenv('GITHUB_ACTIONS')
    with patch.object(m, 'api') as request, pytest.raises(ValueError, match='RUN_ID_REQUIRED'):
        m.stage('../../other', SOURCE, tmp_path)
    request.assert_not_called()


def test_workflow_exposes_source_secrets_only_to_fixed_seal_step():
    workflow = yaml.load((m.ROOT / m.WORKFLOW).read_text(), Loader=yaml.BaseLoader)
    assert set(workflow['on']) == {'workflow_dispatch'}
    assert workflow['permissions'] == {'contents': 'read', 'actions': 'read'}
    job = workflow['jobs']['encrypt_for_existing_environment']
    assert 'environment' not in job
    assert set(job['env']) == {'SOURCE_SHA'}
    credential_steps = [s for s in job['steps'] if 'secrets.' in json.dumps(s)]
    assert len(credential_steps) == 1
    seal = credential_steps[0]
    assert set(seal['env']) == {'SOURCE_' + name for name in m.NAMES}
    assert 'orchestrator.model_secret_relocation seal ' in seal['run']
    assert 'GH_TOKEN' not in seal['env']
    positions = {s['name']: i for i, s in enumerate(job['steps']) if 'name' in s}
    assert positions['Check current source review and fixed recipient before reading source secrets'] < positions[seal['name']]
    assert positions['Validate the closed ciphertext artifact before upload'] < positions['Preserve only the validated ciphertext manifest']
    assert job['steps'][-1]['with']['path'].endswith('/manifest.json')
    assert job['steps'][-1]['with']['retention-days'] == '1'
