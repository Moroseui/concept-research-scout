"""Synthetic original-provider boundary tests, not scientific judgments."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import pytest

from orchestrator import formal_decisions as formal
from orchestrator import scientific_versions as versions
from orchestrator.hosted_cycle import encoded
from test_research_task_authority import setup as authority_setup, OriginalBroker


def formal_request(config):
    return {'schema': formal.SCHEMA, 'source': config['source'], 'action': 'approve_probe',
        'subject': 'synthetic-proposal', 'bindings': {'synthetic_input_sha256': 'f' * 64},
        'evidence': {'synthetic-input.json': '{"status":"TEST_ONLY"}'},
        'request': 'Make only the synthetic test decision.',
        'transition': {'from': 'PROPOSED', 'to': 'ELIGIBLE'}, 'workspace': None,
        'application': None, 'change_request': {'request_id': 'c' * 64, 'applied_event': 'd' * 64}}


def formal_broker(monkeypatch, **kwargs):
    import test_research_task_authority as fixture_module
    def output_format(packet, stage):
        formal.contract(packet['scientific_decision_artifacts'])
        assert stage in ('continuation', 'review')
        return 'json'
    monkeypatch.setattr(fixture_module, 'model_output_format', output_format)
    return OriginalBroker(**kwargs)


def test_existing_decision_workflow_has_two_original_roles_and_idempotent_recovery(authority_setup, monkeypatch):
    config, _, _ = authority_setup
    request = formal_request(config)
    output = Path(config['state']) / 'formal-decisions/original'
    broker = formal_broker(monkeypatch)
    first = formal.execute_formal_decision(config, request, output, client=broker)
    assert first['new_model_calls'] == 2 and first['application_status'] == 'NOT_APPLIED'
    assert broker.calls.count('admit_server') == 1
    originals = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
    second = formal.execute_formal_decision(config, request, output, client=broker)
    assert second['new_model_calls'] == 0 and broker.calls.count('model_stage') == 2
    recovered = output.parent / 'recovered'
    third = formal.execute_formal_decision(config, request, recovered, recover_from=output, client=broker)
    assert third['new_model_calls'] == 0 and broker.calls.count('admit_server') == 1
    assert {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()} == originals
    for prompt in broker.prompts:
        assert 'synthetic_input_sha256' in prompt and 'TEST_ONLY' in prompt
        assert request['change_request']['applied_event'] in prompt
    changed = deepcopy(request); changed['evidence']['synthetic-input.json'] = '{"status":"CHANGED"}'
    with pytest.raises(ValueError, match='ORIGINAL_REQUEST_CHANGED'):
        formal.execute_formal_decision(config, changed, output, client=broker)
    assert broker.calls.count('model_stage') == 2


def test_formal_negative_review_preserves_originals_and_never_applies(authority_setup, monkeypatch):
    config, _, _ = authority_setup
    broker = formal_broker(monkeypatch, verdict='REVISE')
    output = Path(config['state']) / 'formal-decisions/negative'
    with pytest.raises(ValueError, match='REVIEW_REVISION_LIMIT'):
        formal.execute_formal_decision(config, formal_request(config), output, client=broker)
    assert (output / 'round-1/judgment.json').is_file()
    assert (output / 'round-1/review.json').is_file()
    assert not (output / 'round-1/decision.json').exists()
    assert broker.calls.count('model_stage') == 2


def test_protected_root_can_read_original_proof_without_loading_controller_change_store(authority_setup, monkeypatch):
    from orchestrator import change_requests
    config, _, _ = authority_setup
    request = formal_request(config); broker = formal_broker(monkeypatch)
    output = Path(config['state']) / 'formal-decisions/original-proof'
    receipt = formal.execute_formal_decision(config, request, output, client=broker)
    monkeypatch.setattr(formal.os, 'getuid', lambda: 0)
    monkeypatch.setattr(change_requests, 'load', lambda *args: pytest.fail('Root proof reader must not load controller-private change history'))
    before = broker.calls.count('model_stage')
    decision = formal.verify_original_decision(config['source_root'], receipt['decision_path'],
        action=request['action'], subject=request['subject'], bindings=request['bindings'],
        source=config['source'], expected_transition=request['transition'], original_client=broker)
    assert decision['decision'] == 'APPLY' and broker.calls.count('model_stage') == before


def test_formal_new_admission_obeys_pause_and_readonly_original_recovery(authority_setup, monkeypatch):
    import sqlite3
    config, _, _ = authority_setup
    output = Path(config['state']) / 'formal-decisions/paused'
    db = sqlite3.connect(Path(config['state']) / 'coordinator.sqlite')
    db.execute('UPDATE controls SET paused=1'); db.commit(); db.close()
    broker = formal_broker(monkeypatch)
    with pytest.raises(ValueError, match='SYSTEM_PAUSED'):
        formal.execute_formal_decision(config, formal_request(config), output, client=broker)
    assert not output.exists() and not broker.calls


def version_fixture(tmp_path):
    from orchestrator import continuing_research as continuing
    core = {'schema': versions.SCHEMA, 'source': 'a' * 40, 'experiment': 'P002',
        'version_id': 'synthetic-p002-version-v1', 'parent_version_sha256': None,
        'files': {}, 'proposals': [], 'protocol_decision_sha256': 'b' * 64}
    outputs = {
        'propose': {'proposal.md': 'Synthetic proposed scientific idea.'},
        'specify': {'SPEC.proposed.md': 'Synthetic specification; no patient execution.'},
        'code_bundle': {name: '# Synthetic source fixture: ' + name for name in versions.CODE_BUNDLE}}
    packets = {}
    for index, (mode, artifacts) in enumerate(outputs.items(), 1):
        task = {'schema': continuing.PROSPECTIVE_SCHEMA, 'task_id': 'synthetic-' + mode.replace('_', '-') + '-v1',
            'experiment': 'P002', 'mode': mode, 'request': 'Synthetic original proposal only.',
            'references': [], 'selected_by': None,
            'protocol': {'subject': 'synthetic-protocol-v1', 'bindings': {'experiment': 'P002'},
                         'decision_path': '/private/protocol/round-1/decision.json',
                         'decision_sha256': core['protocol_decision_sha256']}}
        packet = {'campaign_task': task, 'campaign_artifacts': continuing.task_contract(task)}
        packets[str(index) * 64] = packet
        core['proposals'].append({'task': str(index) * 64, 'source': core['source'], 'mode': mode,
            'packet_sha256': hashlib.sha256(encoded(packet)).hexdigest(),
            'artifacts': {'round-1/' + name: hashlib.sha256(raw.encode()).hexdigest() for name, raw in artifacts.items()}})
    source = {name: 'Synthetic review input: ' + name for name in versions.required_files(tmp_path, 'P002')}
    for mode, targets in versions.artifact_targets('P002').items():
        for name, target in targets.items():
            source[target] = outputs[mode][name]
    source['campaigns/isles24-pilot/experiments/P002/scientific-origin.json'] = json.dumps(versions.origin(core))
    for name, content in source.items():
        path = tmp_path / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content)
        core['files'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
    def original_client(socket, operation, body):
        assert operation in ('stage_status', 'stage_packet'), 'Version verification must not start a model'
        row = next(row for row in core['proposals'] if row['task'] == body['event']['turn_id'])
        if operation == 'stage_packet':
            packet = deepcopy(packets[row['task']])
            return {'status': 'COMPLETE', 'packet': packet,
                    'packet_sha256': hashlib.sha256(encoded(packet)).hexdigest()}
        stage = body['stage']
        if stage == 'continuation':
            answer = json.dumps(outputs[row['mode']])
        elif stage == 'review':
            answer = json.dumps({'review.json': json.dumps({'verdict': 'APPROVE', 'rationale': 'Synthetic review only.'})})
        else:
            answer = 'Retain the original reviewed proposal; a separate authority decision is required.'
        model = 'claude-fable-5' if stage == 'review' else 'gpt-6-astra'
        return {'status': 'COMPLETE', 'packet_sha256': row['packet_sha256'], 'answer': answer,
            'receipt': {'requested_model': model, 'actual_model': model if stage == 'review' else None,
                'returncode': 0, 'stage': stage, 'session_id': 'synthetic-' + row['mode'] + '-' + stage,
                'answer_sha256': hashlib.sha256(answer.encode()).hexdigest(), 'operating_context_sha256': 'c' * 64}}
    return core, original_client


def test_scientific_version_binds_full_inputs_and_original_generated_bytes(tmp_path):
    core, original_client = version_fixture(tmp_path)
    assert versions.validate_core(tmp_path, core) == core
    proof = versions.verify_proposals(core, original_client=original_client)
    assert len(proof) == 3 and proof[0]['author']['actual_model'] is None
    old = deepcopy(core)
    target = 'campaigns/isles24-pilot/experiments/P002/run.py'
    (tmp_path / target).write_text('Changed code after original proposal')
    core['files'][target] = hashlib.sha256((tmp_path / target).read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='DIFFERS_FROM_REVIEWED_PROPOSALS'):
        versions.validate_core(tmp_path, core)
    old['files'].pop('tests/test_prediction_p002.py')
    with pytest.raises(ValueError, match='CORE_REQUIRED'):
        versions.validate_core(tmp_path, old)
    with pytest.raises(ValueError, match='FROZEN_P001'):
        versions.required_files(tmp_path, 'P001')


def test_original_proposal_model_reply_and_negative_review_are_not_local_metadata(tmp_path):
    core, original_client = version_fixture(tmp_path)
    def wrong(socket, operation, body):
        value = original_client(socket, operation, body)
        if body.get('stage') == 'continuation':
            value = deepcopy(value); value['answer'] = json.dumps({'proposal.md': 'Different model output'})
            value['receipt']['answer_sha256'] = hashlib.sha256(value['answer'].encode()).hexdigest()
        return value
    with pytest.raises(ValueError, match='DIFFERS_FROM_MODEL_ORIGINAL'):
        versions.verify_proposals(core, original_client=wrong)
    def negative(socket, operation, body):
        value = original_client(socket, operation, body)
        if body.get('stage') == 'review':
            value = deepcopy(value)
            value['answer'] = json.dumps({'review.json': json.dumps({'verdict': 'REVISE', 'rationale': 'Synthetic correction needed.'})})
            value['receipt']['answer_sha256'] = hashlib.sha256(value['answer'].encode()).hexdigest()
        return value
    with pytest.raises(ValueError, match='OPPOSING_APPROVAL_REQUIRED'):
        versions.verify_proposals(core, original_client=negative)
    with pytest.raises(ValueError, match='ORIGINAL_PROVIDER_CLIENT'):
        versions.verify_proposals(core, original_client=None)


@pytest.mark.parametrize('mode', ['specify', 'code_bundle'])
def test_another_valid_protocol_cannot_rebind_original_scientific_proposals(tmp_path, mode):
    core, original_client = version_fixture(tmp_path)
    core['protocol_decision_sha256'] = 'e' * 64
    with pytest.raises(ValueError, match='ORIGINAL_PROTOCOL_CHANGED'):
        versions.verify_proposals(core, original_client=original_client)
    # Even a changed packet with matching local metadata cannot replace the
    # original protected packet hash. The broker's original pin remains decisive.
    core['protocol_decision_sha256'] = 'b' * 64
    def rewritten(socket, operation, body):
        result = original_client(socket, operation, body)
        if operation == 'stage_packet' and result['packet']['campaign_task']['mode'] == mode:
            result['packet']['campaign_task']['protocol']['decision_sha256'] = 'e' * 64
        return result
    with pytest.raises(ValueError, match='ORIGINAL_PACKET_REQUIRED'):
        versions.verify_proposals(core, original_client=rewritten)


def test_full_review_content_must_have_reached_both_actual_roles(tmp_path, monkeypatch):
    core, original_client = version_fixture(tmp_path)
    raw = encoded(core); (tmp_path / 'scientific-version.json').write_bytes(raw)
    path = tmp_path / 'scientific-authority' / core['version_id'] / 'round-1/decision.json'
    path.parent.mkdir(parents=True); path.write_text('Synthetic descriptor fixture only')
    descriptor = {'core_path': 'scientific-version.json', 'core_sha256': hashlib.sha256(raw).hexdigest(),
                  'decision_path': path.relative_to(tmp_path).as_posix(),
                  'decision_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    monkeypatch.setattr(versions, 'verify_original_decision',
        lambda *args, **kw: {'decision': 'APPLY', 'actor': {'identity': 'synthetic'}})
    monkeypatch.setattr(versions, 'original_transport', lambda path: {'packet': {
        'formal_request': {'evidence': {'scientific-version.json': raw.decode()}}}})
    with pytest.raises(ValueError, match='FULL_REVIEW_INPUTS_NOT_SUPPLIED'):
        versions.verify_authority(tmp_path, descriptor, original_client=original_client)
