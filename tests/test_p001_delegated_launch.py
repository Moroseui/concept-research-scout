"""The P001 authority layer keeps exact scope and live human controls.

These are authority-only packets. The unchanged native protocol suite separately
checks packet reconstruction, runtime guards, exclusive intent and return limits.
"""
import copy
import json
from pathlib import Path
import shutil

import pytest

from orchestrator import scientific_authority as authority
from orchestrator import p001_native_launch as launch


@pytest.fixture
def delegated(tmp_path, monkeypatch):
    tmp_path.chmod(0o700)
    source = Path(__file__).resolve().parents[1]
    for name in (authority.POLICY_PATH, 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md'):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, path)
    monkeypatch.setattr(launch, 'ROOT', tmp_path)
    core = {k: 'a' * 64 for k in ('execution_snapshot', 'source_pin', 'notebook_pin',
            'setup_receipt_sha256', 'environment_sha256', 'slot_binding_sha256')}
    core.update(derived_member_count=206, combined_transfer_cap=33554432,
                max_extracted_bytes=8589934592, private_validation_destination='/private/unit-fixture',
                raw_or_staged_input_transfer=False, runtime_guard={
                    'runtime_fingerprint_sha256': 'b' * 64, 'archive_metadata': {'fixture': True}})
    packet = {'core': core, 'core_manifest_sha256': authority.P001_SCOPE['p001_exact_core_sha256']}
    directory = tmp_path / 'decision'
    directory.mkdir(mode=0o700)
    def seal(value):
        kw = dict(action='launch_p001', subject='campaign:isles24-pilot:P001',
                  bindings=launch.delegated_bindings(value))
        judgment = {'context_sha256': authority.digest(authority.encoded(authority.decision_context(tmp_path, **kw))),
                    'decision': 'APPLY', 'rationale': 'Exact baseline has useful exploratory value within the reviewed scope.',
                    'transition': {'from': 'PREPARED', 'to': 'LAUNCH_AUTHORIZED'},
                    'reconsideration': 'Defer if runtime, human controls or reserved resource boundaries change.'}
        (directory / 'judgment.json').write_bytes(authority.encoded(judgment) + b'\n')
        (directory / 'review.json').write_bytes(authority.encoded({'verdict': 'APPROVE',
            'rationale': 'The exact bound decision preserves the authorized limits.',
            'judgment_sha256': authority.digest((directory / 'judgment.json').read_bytes())}) + b'\n')
        authority.seal(tmp_path, directory, **kw,
            author={'family_effective': 'codex', 'model_used': 'gpt-6-astra', 'run_id': 'author000001', 'exit_class': 'ok'},
            reviewer={'family_effective': 'claude', 'model_used': 'claude-fable-5', 'run_id': 'review000001', 'exit_class': 'ok'})
        for p in directory.iterdir():
            p.chmod(0o600)
        return directory / 'decision.json'
    return tmp_path, packet, seal


def test_model_judgment_crosses_exact_authority_gate_without_human_signature(delegated):
    root, packet, seal = delegated
    path = seal(packet)
    assert launch.require_authority(packet, path) == authority.digest(path.read_bytes())
    result = launch._agent_decision(packet, path)
    assert result['actor']['kind'] == 'agent'
    assert result['actor']['session_id_source'] == 'system_stage_run_id'
    assert not list(root.rglob('HUMAN_APPROVED_PROBE'))
    # A bare JSON copy lacks the original authority artifacts and is not a human approval.
    with pytest.raises(ValueError, match='APPROVAL_REQUIRED'):
        launch.require_authority(packet, json.loads(path.read_text()))


@pytest.mark.parametrize('field,value', [('combined_transfer_cap', 33554433),
    ('max_extracted_bytes', 8589934593), ('core_manifest_sha256', 'f' * 64)])
def test_even_a_reviewed_model_cannot_expand_exact_p001_scope(delegated, field, value):
    _, packet, seal = delegated
    if field == 'core_manifest_sha256':
        packet[field] = value
    else:
        packet['core'][field] = value
    path = seal(packet)
    with pytest.raises(ValueError, match='EXACT_DELEGATED_P001_SCOPE'):
        launch.require_authority(packet, path)


def test_current_human_stop_blocks_previously_valid_agent_decision(delegated):
    root, packet, seal = delegated
    path = seal(packet)
    launch.require_authority(packet, path)
    events = root / 'campaigns/isles24-pilot/experiments/P001/lifecycle.jsonl'
    events.parent.mkdir(parents=True)
    events.write_text(json.dumps({'actor_type': 'human', 'stage': 'STOP'}) + '\n')
    with pytest.raises(ValueError, match='HUMAN_STOP_PRESERVED'):
        launch.require_authority(packet, path)
    with events.open('a') as handle:
        handle.write(json.dumps({'actor_type': 'agent', 'stage': 'RESUME'}) + '\n')
    with pytest.raises(ValueError, match='HUMAN_STOP_PRESERVED'):
        launch.require_authority(packet, path)


def test_later_human_stop_also_blocks_original_human_approval(delegated):
    root, packet, _ = delegated
    approval = {'schema': 'p001-exact-native-launch-approval/v1', 'status': 'OPERATOR_APPROVED',
        'core_manifest_sha256': packet['core_manifest_sha256'], 'patient_launch': True,
        'derived_return_transfer_206_members': True, 'combined_transfer_cap': 33554432,
        'max_extracted_bytes': 8589934592, 'private_validation_destination': '/private/unit-fixture',
        'raw_or_staged_input_transfer': False}
    launch.require_authority(packet, approval)
    events = root / 'campaigns/isles24-pilot/experiments/P001/lifecycle.jsonl'
    events.parent.mkdir(parents=True)
    events.write_text(json.dumps({'actor_type': 'human', 'stage': 'STOP'}) + '\n')
    with pytest.raises(ValueError, match='HUMAN_STOP_PRESERVED'):
        launch.require_authority(packet, approval)
    with events.open('a') as handle:
        handle.write(json.dumps({'actor_type': 'human', 'stage': 'RESUME'}) + '\n')
    launch.require_authority(packet, approval)


def test_original_model_decision_cannot_move_to_another_input_or_destination(delegated):
    _, packet, seal = delegated
    path = seal(packet)
    original = copy.deepcopy(packet)
    for field in ('private_validation_destination', 'source_pin', 'slot_binding_sha256'):
        packet = copy.deepcopy(original)
        packet['core'][field] = 'changed'
        with pytest.raises(ValueError, match='EXACT_DELEGATED_SCIENTIFIC_AUTHORITY'):
            launch.require_authority(packet, path)
