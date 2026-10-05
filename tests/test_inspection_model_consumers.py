"""Offline consumer contracts; synthetic receipts confer no provider approval."""
import copy
import json
from pathlib import Path

import pytest
from orchestrator import inspection_deployment as adapter, deployment_review as gate
from orchestrator import inspection_bootstrap as bootstrap
from orchestrator import change_requests as changes
from test_inspection_deployment import material_fixture
from test_deployment_review import fixture as bundle_fixture, SOURCE

VERSION = 'direct-inspection-cyber-fallback/v2'
DIRECT_VERSION = 'direct-inspection-opus-4-8/v1'
FALLBACK = 'claude-opus-4-8'


def consumer_receipt(review, *, model=FALLBACK):
    # Isolate downstream attribution from separately tested protocol validation.
    # This fixture is never passed off as raw model or host evidence.
    result = copy.deepcopy(review)
    session_id = result['response']['session_id']
    proof = {'policy_version': VERSION, 'session_id': session_id,
             'requested_model': gate.MODEL, 'provider_model': model,
             'assistant_models': sorted({gate.MODEL, model})}
    last = {'status': 'APPROVE', 'requested_model': gate.MODEL,
            'provider_model': model, 'assistant_models': proof['assistant_models'],
            'model_policy_version': VERSION, 'model_policy': proof}
    result.update(inspection_profile=adapter.PROFILE, model_policy_version=VERSION,
        inspection_session={'status': 'APPROVE', 'source': result['execution']['reviewed_commit'],
            'session_id': session_id, 'attempts': [last], 'requested_model': gate.MODEL,
            'provider_model': model, 'model_policy_version': VERSION})
    return result


def test_unmarked_actual_originals_keep_legacy_attribution_and_receipt_shape():
    review = adapter.validate_deployment_session(**material_fixture())
    assert review['provider_model'] == gate.MODEL
    assert gate._review_model(review) == gate.MODEL
    assert 'model_policy_version' not in review['inspection_session']
    assert 'requested_model' not in review['inspection_session']['attempts'][-1]


@pytest.mark.parametrize('model', [gate.MODEL, FALLBACK])
def test_direct_consumer_attributes_final_actual_model(model):
    review = adapter.validate_deployment_session(**material_fixture())
    reviewed = consumer_receipt(review, model=model)
    assert adapter.review_model(reviewed) == gate._review_model(reviewed) == model


@pytest.mark.parametrize('mutation', ['marker', 'absent_marker', 'session_model', 'attempt_model',
    'requested', 'assistants', 'policy_model', 'policy_session', 'negative', 'source', 'session'])
def test_inconsistent_direct_attribution_is_refused(mutation):
    review = consumer_receipt(adapter.validate_deployment_session(**material_fixture()))
    session = review['inspection_session']; last = session['attempts'][-1]
    if mutation == 'marker': review['model_policy_version'] = 'unknown/v1'
    if mutation == 'absent_marker': review.pop('model_policy_version')
    if mutation == 'session_model': session['provider_model'] = gate.MODEL
    if mutation == 'attempt_model': last['provider_model'] = gate.MODEL
    if mutation == 'requested': session['requested_model'] = FALLBACK
    if mutation == 'assistants': last['assistant_models'] = [gate.MODEL]
    if mutation == 'policy_model': last['model_policy']['provider_model'] = gate.MODEL
    if mutation == 'policy_session': last['model_policy']['session_id'] = 'synthetic-other-session'
    if mutation == 'negative': last['status'] = 'REQUEST_CHANGES'
    if mutation == 'source': session['source'] = 'f' * 40
    if mutation == 'session': session['session_id'] = 'synthetic-other-session'
    with pytest.raises(ValueError): gate._review_model(review)


def test_unknown_model_cannot_pass_by_matching_every_mirror():
    review = consumer_receipt(adapter.validate_deployment_session(**material_fixture()), model='unknown-model')
    with pytest.raises(ValueError, match='FINAL_MODEL_BINDING'): adapter.review_model(review)


def test_canonical_review_actor_must_match_actual_final_direct_judge(tmp_path, monkeypatch):
    f = bundle_fixture(tmp_path, monkeypatch)
    review = consumer_receipt(gate.review_originals(f['raw'], SOURCE))
    binding = json.loads((f['bundle']/'proposal.json').read_bytes())['changes'][0]
    # The already recorded Fable actor must not qualify an Opus final judgment.
    with pytest.raises(ValueError, match='ORIGINAL_CLAUDE_REVIEW_REQUIRED'):
        gate.change_review(f['bundle'], binding, review)
    changes.record(f['change'], 'REVIEW', {**f['actor'], 'model': FALLBACK}, f['payload'])
    assert gate.change_review(f['bundle'], binding, review)


def test_legacy_actor_cannot_borrow_a_direct_provider_model_field(tmp_path, monkeypatch):
    f = bundle_fixture(tmp_path, monkeypatch)
    review = gate.review_originals(f['raw'], SOURCE)
    review['provider_model'] = FALLBACK
    assert gate._review_model(review) == gate.MODEL
    assert gate.verify_bundle(f['bundle'], f['root'], SOURCE)['review_model'] == gate.MODEL


def test_new_policy_module_is_mandatory_old_route_bootstrap_source():
    assert 'orchestrator/inspection_model_policy.py' in bootstrap.MANDATORY_SOURCE


def test_both_roles_and_document_hashes_bind_the_same_narrow_policy():
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root/'configs/scientific-operating-context.json').read_bytes())
    assert config['version'] == '20260915-terminal-review-import-v23'
    for role in ('codex', 'claude'):
        assert DIRECT_VERSION in config['roles'][role]
        assert 'Legacy bootstrap remains Fable-only' in config['roles'][role]
        assert '32 native model iterations per invocation and 16 native attempts' in config['roles'][role]
        assert 'native canaries retain eight iterations' in config['roles'][role]
        assert '60-second allowance' in config['roles'][role]
        assert 'Require V2 and its complete approved baseline' in config['roles'][role]
        assert 'historical V1 receipts and baseline validation' in config['roles'][role]
        assert 'candidate instructions do not replace the separately approved baseline' in config['roles'][role]
    for name, expected in config['documents'].items():
        assert gate.digest((root/name).read_bytes()) == expected


@pytest.mark.parametrize('family', ['codex', 'claude'])
def test_loaded_role_context_has_exact_current_review_budgets(tmp_path, monkeypatch, family):
    from orchestrator import scientific_authority as authority
    root = Path(__file__).resolve().parents[1]
    monkeypatch.delenv('SCOUT_CHANGE_REQUEST_STORE', raising=False)
    supplied = authority.stage_context(root, tmp_path, family, 'review-budget')
    raw = (tmp_path/'context_review-budget.json').read_bytes()
    value = json.loads(raw)
    config_raw = (root/'configs/scientific-operating-context.json').read_bytes()
    config = json.loads(config_raw)
    assert value['family'] == family and value['role'] == config['roles'][family]
    assert value['shared_policy']['operating_context']['manifest_sha256'] == gate.digest(config_raw)
    assert raw.decode() in supplied
    assert '32 native model iterations per invocation and 16 native attempts' in value['role']
    assert 'native canaries retain eight iterations' in value['role']
    assert '60-second allowance' in value['role']
    if family == 'claude':
        # Pure exact-closure check only; this fixture confers no independent approval.
        policy_name = config['authority_policy']['path']
        policy = json.loads((root/policy_name).read_bytes())
        names = {policy_name, policy['direction_path'],
                 'configs/scientific-operating-context.json', *config['documents']}
        expected = {name: (root/name).read_bytes() for name in names}
        bootstrap.validate_context(raw, expected)


def marked_material_fixture(*, status='APPROVE'):
    """Full synthetic originals through the real policy and material validators."""
    from orchestrator import inspection_review as inspection, inspection_model_policy as policy
    from test_inspection_model_policy import fallback
    fixture = material_fixture(status=status)
    manifest = json.loads(fixture['manifest_raw'])
    originals = fixture['attempts'][0]['originals']
    probe = json.loads(originals['permission_probe'])
    probe.update(model_policy_version=policy.VERSION, runtime_cli_sha256=policy.CLI_SHA256)
    originals['permission_probe'] = inspection.encoded(probe)
    manifest.update(model_policy_version=policy.VERSION,
                    permission_probe_sha256=inspection.digest(originals['permission_probe']))
    fixture['manifest_raw'] = inspection.encoded(manifest)
    manifest_sha = inspection.digest(fixture['manifest_raw'])
    request = json.loads(originals['request']); request['manifest_sha256'] = manifest_sha
    originals['request'] = inspection.encoded(request)
    intent = json.loads(originals['intent'])
    intent.update(manifest_sha256=manifest_sha, request_sha256=inspection.digest(originals['request']))
    originals['intent'] = inspection.encoded(intent)
    protocol = fallback([json.loads(line) for line in originals['protocol'].splitlines()])
    protocol[-1]['structured_output']['manifest_sha256'] = manifest_sha
    originals['protocol'] = b''.join((json.dumps(event)+'\n').encode() for event in protocol)
    wrapped = fixture['attempts'][0]
    wrapped['response_raw'] = inspection.encoded(protocol[-1])
    execution = json.loads(wrapped['execution_raw'])
    execution.update(manifest_sha256=manifest_sha,
        request_sha256=inspection.digest(originals['request']),
        response_sha256=inspection.digest(wrapped['response_raw']),
        protocol_sha256=inspection.digest(originals['protocol']),
        assistant_message_models=[policy.REQUESTED, policy.FALLBACK],
        actual_usage_models=list(protocol[-1]['modelUsage']))
    wrapped['execution_raw'] = inspection.encoded(execution)
    return fixture


def test_full_marked_material_originals_preserve_reads_and_final_actual_identity():
    from orchestrator import inspection_review as inspection
    fixture = marked_material_fixture(); before = copy.deepcopy(fixture)
    result = adapter.validate_deployment_session(**fixture)
    assert fixture == before
    assert result['provider_model'] == FALLBACK
    assert result['execution_metadata_projection']['assistant_message_models'] == [gate.MODEL, FALLBACK]
    receipt = result['inspection_session']['attempts'][0]
    assert receipt['model_policy']['unexecuted_retracted'][0]['coverage'] == []
    assert all(name in result['inspection_session']['reads'] for name in fixture['required_files'])
    assert result['original_attempt_file_sha256'][0]['protocol_sha256'] == inspection.digest(fixture['attempts'][0]['originals']['protocol'])


def test_full_marked_material_execution_cannot_relabel_actual_opus_as_only_fable():
    fixture = marked_material_fixture()
    execution = json.loads(fixture['attempts'][0]['execution_raw'])
    execution['assistant_message_models'] = [gate.MODEL]
    fixture['attempts'][0]['execution_raw'] = gate.encoded(execution)
    with pytest.raises(ValueError, match='EXECUTION_ORIGINAL_BINDING'):
        adapter.validate_deployment_session(**fixture)


def test_full_marked_material_adverse_final_judgment_remains_adverse():
    with pytest.raises(ValueError, match='FULL_TERMINAL_APPROVAL_REQUIRED'):
        adapter.validate_deployment_session(**marked_material_fixture(status='REQUEST_CHANGES'))


def test_full_marked_material_final_assistant_model_reset_refuses():
    fixture = marked_material_fixture(); wrapped = fixture['attempts'][0]
    originals = wrapped['originals']
    protocol = [json.loads(line) for line in originals['protocol'].splitlines()]
    last = [event for event in protocol if event.get('type') == 'assistant'][-1]
    last['message']['model'] = gate.MODEL
    originals['protocol'] = b''.join((json.dumps(event)+'\n').encode() for event in protocol)
    execution = json.loads(wrapped['execution_raw'])
    execution['protocol_sha256'] = gate.digest(originals['protocol'])
    wrapped['execution_raw'] = gate.encoded(execution)
    with pytest.raises(ValueError, match='FULL_TERMINAL_APPROVAL_REQUIRED'):
        adapter.validate_deployment_session(**fixture)
