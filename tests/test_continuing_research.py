"""Synthetic fixtures for continuing operations; no scientific/model approval."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import pytest

from orchestrator import continuing_research as continuing
from orchestrator.hosted_campaign import BrokerStages, run_pipeline, recover_projection
from orchestrator.hosted_campaign_task import completed_pipeline, task_contract
from orchestrator.hosted_cycle import encoded
from orchestrator.handover_coordinator import digest
from test_hosted_campaign import client_for


def task(mode='investigate', identifier='synthetic-investigator-v1'):
    return {'schema': continuing.TASK_SCHEMA, 'task_id': identifier, 'experiment': 'P001',
            'mode': mode, 'request': 'Assess the supplied synthetic research context.',
            'references': [], 'selected_by': None}


def choice(original):
    return {'schema': continuing.SELECTION_SCHEMA, 'status': 'PROPOSE',
            'rationale': 'A formal proposal is the next useful task.',
            'reconsideration': 'Reassess on new evidence or criticism.',
            'successor': task('propose', 'synthetic-proposal-v2')}


def supplement(original):
    return {'continuing-research-inputs.json': json.dumps({'task': original, 'references': []}, sort_keys=True)}


@pytest.mark.parametrize('verdict', ['APPROVE', 'REVISE'])
def test_investigator_uses_actual_pipeline_and_preserves_original_recovery(tmp_path, verdict):
    original = task()
    proposed = choice(original)
    packet = {'campaign_task': original, 'campaign_artifacts': task_contract(original)}
    answers = [json.dumps({'selection.json': json.dumps(proposed)}),
               json.dumps({'review.json': json.dumps({'verdict': verdict, 'rationale': 'Synthetic opposing review.'})})]
    original_client, calls = client_for(answers)
    originals = {}
    def capture(socket, operation, body):
        response = original_client(socket, operation, body)
        originals[body['stage']] = response
        return response
    output = tmp_path / 'campaigns/isles24-pilot/pipeline/original'
    sc = SimpleNamespace(ROOT=tmp_path)
    with patch('orchestrator.campaign_pipeline.grounding', return_value={}), patch(
            'orchestrator.research_context.evidence_context', return_value={}):
        receipt = run_pipeline(sc, 'investigate', original['request'], output,
                               BrokerStages('fixture', {}, packet, client=capture),
                               supplement=supplement(original))
        assert calls == ['continuation', 'review']
        assert receipt['acceptance_status'] == ('APPROVED_PROPOSAL_ONLY' if verdict == 'APPROVE' else 'NOT_ACCEPTED')
        completed_pipeline(tmp_path, output, packet, {}, supplement=supplement(original))
        (output / 'receipt.json').unlink()
        before = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
        def recover(socket, operation, body):
            assert operation == 'stage_status'
            return {**originals[body['stage']], 'duplicate': True}
        recovered = output.parent / 'recovery'
        restored = recover_projection(sc, 'investigate', original['request'], output, recovered,
            BrokerStages('fixture', {}, packet, client=recover, recovery=True), supplement=supplement(original))
        assert restored['acceptance_status'] == receipt['acceptance_status']
        assert len(calls) == 2
        assert {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()} == before
        assert json.loads((recovered / 'recovery.json').read_text())['new_model_calls'] == 0


def test_investigator_cannot_select_shell_unknown_subject_or_unseen_evidence():
    original = task()
    value = choice(original)
    for field, replacement in [('mode', 'shell'), ('experiment', 'NEW_DATASET'), ('task_id', original['task_id'])]:
        changed = deepcopy(value); changed['successor'][field] = replacement
        with pytest.raises(ValueError):
            continuing.selection(original, changed)
    value['successor']['references'] = [{'task': 'a' * 64, 'artifact': 'round-1/proposal.md', 'sha256': 'b' * 64}]
    with pytest.raises(ValueError, match='NOT_IN_INVESTIGATOR_CONTEXT'):
        continuing.selection(original, value)
    value = choice(original); value['status'] = 'DEFER'
    with pytest.raises(ValueError, match='DEFERRED_SELECTION'):
        continuing.selection(original, value)


def test_reference_content_and_context_are_bound_not_just_labels():
    original = task()
    ref = {'task': 'a' * 64, 'artifact': 'round-1/proposal.md', 'sha256': hashlib.sha256(b'Original').hexdigest()}
    original['references'] = [ref]
    context = {'continuing-research-inputs.json': json.dumps(
        {'task': original, 'references': [{'reference': ref, 'content': 'Changed'}]})}
    with pytest.raises(ValueError, match='INPUT_ARTIFACT_CHANGED'):
        continuing.checked_supplement(original, context)
    with pytest.raises(ValueError, match='ARTIFACT_PATH'):
        continuing.reference({**ref, 'artifact': '../credentials.json'})


def saved_selection(tmp_path, verdict='APPROVE'):
    original = task()
    selected = choice(original)
    task_id = 'a' * 64
    state = tmp_path / 'state'; state.mkdir(mode=0o700)
    folder = state / 'tasks' / task_id
    output = folder / 'campaign-workspace/campaigns/isles24-pilot/pipeline/hosted-original'
    (output / 'round-1').mkdir(parents=True)
    raw = json.dumps(selected).encode()
    (output / 'round-1/selection.json').write_bytes(raw)
    (folder / 'packet.json').write_text(json.dumps({'campaign_task': original}))
    disposition = {'task': task_id, 'source': 'c' * 40, 'status': 'DISPOSITION_RECORDED',
        'review_verdict': verdict, 'acceptance_status': 'APPROVED_PROPOSAL_ONLY' if verdict == 'APPROVE' else 'NOT_ACCEPTED',
        'campaign_output': output.relative_to(state).as_posix(),
        'artifact_sha256': {'round-1/selection.json': hashlib.sha256(raw).hexdigest()}}
    (folder / 'scientific-disposition.json').write_text(json.dumps(disposition))
    config = {'state': str(state), 'source': 'c' * 40, 'source_root': str(tmp_path),
              'controller_uid': os.getuid(), 'controller_gid': os.getgid(), 'broker_socket': 'fixture'}
    return config, task_id, output


def test_saved_selection_requires_review_and_original_bytes(tmp_path):
    config, identity, output = saved_selection(tmp_path)
    selected = continuing.selected_successor(config, identity)
    assert selected['status'] == 'PROPOSED_PENDING_ELIGIBILITY'
    assert selected['task']['selected_by']['task'] == identity
    (output / 'round-1/selection.json').write_text('Locally changed model outcome')
    with pytest.raises(ValueError, match='ORIGINAL_ARTIFACT_CHANGED'):
        continuing.selected_successor(config, identity)


def test_saved_negative_review_cannot_register_successor(tmp_path):
    config, identity, output = saved_selection(tmp_path, 'REVISE')
    with pytest.raises(ValueError, match='OPPOSING_REVIEW_REQUIRED'):
        continuing.selected_successor(config, identity)


def test_private_evidence_intake_is_content_addressed_and_changed_bytes_fail(tmp_path):
    tmp_path.chmod(0o700)
    config = {'state': str(tmp_path), 'controller_uid': os.getuid(), 'controller_gid': os.getgid()}
    record = continuing.preserve_evidence(config, {'status': 'Synthetic retained input'})
    assert continuing.read_evidence(config, record)['status'] == 'Synthetic retained input'
    assert continuing.preserve_evidence(config, {'status': 'Synthetic retained input'}) == record
    Path(record['evidence_file']).write_text('{}')
    with pytest.raises(ValueError, match='EVIDENCE_CHANGED'):
        continuing.read_evidence(config, record)


def registration_fixture(tmp_path, monkeypatch):
    config, identity, output = saved_selection(tmp_path)
    selected = continuing.selected_successor(config, identity)['task']
    evidence = continuing.preserve_evidence(config, {'status': 'Synthetic original evidence'})
    entry = {'schema': 'installed-research-catalog-entry/v1', 'source': config['source'],
             'source_root': config['source_root'],
             'request': {'task': selected, **evidence, 'day': '2026-09-11',
                         'initiator': {'kind': 'human', 'identity': 'Synthetic operator'}},
             'eligibility': {'path': str(Path(config['state']) / 'decision/round-1/decision.json'), 'sha256': 'd' * 64},
             'predecessors': [{'task': identity, 'source': config['source'], 'disposition_sha256': 'e' * 64,
                               'requires': 'APPROVED_PROPOSAL_ONLY'}],
             'change_request': {'request_id': 'f' * 64, 'applied_event': 'b' * 64}}
    checks = []
    class Runtime:
        def __init__(self, cfg): assert cfg == config
        def research_predecessors(self, value):
            assert value == entry
            checks.append('original_predecessors')
    monkeypatch.setattr('orchestrator.handover_runtime.Runtime', Runtime)
    monkeypatch.setattr('orchestrator.research_catalog.linked_change',
                        lambda c, e: checks.append('live_change_review'))
    actor = {'kind': 'agent', 'family': 'codex', 'model': 'gpt-6-astra', 'session_id': 'synthetic-original'}
    def eligibility(c, e, *, client):
        checks.append('provider_authority')
        return {'status': 'ELIGIBLE', 'review_status': 'APPROVE', 'actor': actor}
    monkeypatch.setattr('orchestrator.research_task_authority.verify_eligibility', eligibility)
    return config, entry, checks, actor


def test_registration_rechecks_selection_predecessors_live_review_and_provider_authority(tmp_path, monkeypatch):
    config, entry, checks, actor = registration_fixture(tmp_path, monkeypatch)
    result = continuing.validate_registration(config, entry, client=lambda *a: None)
    assert result['entry_sha256'] == digest(entry)
    assert checks == ['original_predecessors', 'live_change_review', 'provider_authority']
    assert result['model_calls'] == result['admissions'] == 0
    altered = deepcopy(entry); altered['request']['task']['request'] = 'A different scientific task'
    with pytest.raises(ValueError, match='DIFFERS_FROM_ORIGINAL'):
        continuing.validate_registration(config, altered, client=lambda *a: None)
    altered = deepcopy(entry); altered['predecessors'][0]['requires'] = 'DISPOSITION_RECORDED'
    with pytest.raises(ValueError, match='ACCEPTED_PREDECESSOR'):
        continuing.validate_registration(config, altered, client=lambda *a: None)
    monkeypatch.setattr('orchestrator.research_catalog.linked_change',
                        lambda *a: (_ for _ in ()).throw(ValueError('RESEARCH_CHANGE_REVIEW_PENDING')))
    with pytest.raises(ValueError, match='REVIEW_PENDING'):
        continuing.validate_registration(config, entry, client=lambda *a: None)


def test_existing_selected_successor_is_queued_only_after_protected_registration(tmp_path, monkeypatch):
    config, entry, checks, actor = registration_fixture(tmp_path, monkeypatch)
    submitted = []
    class Runtime:
        def submit_research(self, task_id, *, submitted_by):
            submitted.append((task_id, submitted_by))
            return {'status': 'QUEUED', 'admissions': 0}
    runtime = Runtime(); runtime.config = config
    def broker(socket, op, body):
        assert op == 'register_research' and body == {'entry': entry}
        return {'status': 'REGISTERED', 'entry_sha256': digest(entry)}
    monkeypatch.setattr('orchestrator.handover_runtime.request_broker', broker)
    result = continuing.register_and_submit(runtime, entry)
    assert submitted == [(entry['request']['task']['task_id'], actor)]
    assert result['new_model_calls'] == 0
    monkeypatch.setattr('orchestrator.handover_runtime.request_broker', lambda *a: {'status': 'REFUSED'})
    with pytest.raises(ValueError, match='REGISTRATION_RECEIPT'):
        continuing.register_and_submit(runtime, entry)
    assert len(submitted) == 1


def test_protected_route_requires_root_and_no_caller_verifier(tmp_path, monkeypatch):
    monkeypatch.setattr(continuing.os, 'getuid', lambda: 1000)
    with pytest.raises(ValueError, match='PROTECTED_SUCCESSOR_REGISTRATION'):
        continuing.protected_register(SimpleNamespace(config={}), {'entry': {}, 'verifier': 'trust-me'})
    assert list(tmp_path.iterdir()) == []


def test_originals_only_validator_cannot_turn_missing_reply_into_model_operation(monkeypatch):
    def verify(config, entry, *, client):
        return client('fixture', 'model_stage', {'event': {}, 'stage': 'continuation'})
    monkeypatch.setattr(continuing, 'validate_registration', verify)
    with pytest.raises(ValueError, match='FORBIDS_NEW_MODEL'):
        continuing._validate_originals_input({'config': {}, 'entry': {}, 'originals': {}})


def prospective_task(mode='code_bundle'):
    return {**task(mode, 'synthetic-prospective-v1'), 'schema': continuing.PROSPECTIVE_SCHEMA,
        'experiment': 'P002', 'protocol': {'subject': 'synthetic-protocol-v1',
            'bindings': {'experiment': 'P002'}, 'decision_path': '/private/formal-decisions/p/round-1/decision.json',
            'decision_sha256': 'd' * 64}}


def test_prospective_bundle_keeps_frozen_paths_and_requires_bound_protocol():
    from orchestrator.campaign_pipeline import grounding
    source = Path(__file__).resolve().parents[1]
    original = prospective_task()
    context = grounding(source, 'P002', prospective_task=original)
    assert 'campaigns/isles24-pilot/CAMPAIGN.md' in context
    assert 'charters/isles24/CHARTER.md' not in context  # Selected charter already supersedes it.
    with pytest.raises(FileNotFoundError):
        grounding(source, 'P002')  # Historical P002 still requires the old P001 interpretation.
    with pytest.raises(ValueError, match='CODE_BUNDLE_REQUIRES_PROSPECTIVE_PROTOCOL'):
        continuing.task_contract(task('code_bundle'))
    bad = deepcopy(original); bad['experiment'] = 'P001'
    with pytest.raises(ValueError, match='PROSPECTIVE_OPERATION_SCOPE'):
        continuing.task_contract(bad)
    value = {'task': original, 'references': [], 'protocol': {'descriptor': original['protocol'],
        'decision': {'decision': 'APPLY', '_decision_sha256': 'e' * 64}}}
    with pytest.raises(ValueError, match='ORIGINAL_PROTOCOL_CONTEXT'):
        continuing.checked_supplement(original, {'continuing-research-inputs.json': json.dumps(value)})


def test_code_bundle_requires_accepted_idea_and_matching_spec_before_construction(tmp_path):
    original = prospective_task()
    config = {'state': str(tmp_path)}
    with pytest.raises(ValueError, match='REVIEWED_IDEA_AND_SPEC'):
        continuing.require_code_inputs(config, original)
    for identifier, name, mode in [('a', 'proposal.md', 'propose'), ('b', 'SPEC.proposed.md', 'specify')]:
        identity = identifier * 64
        folder = tmp_path / 'tasks' / identity
        output = folder / 'campaign-workspace/campaigns/isles24-pilot/pipeline/original'
        (output / 'round-1').mkdir(parents=True)
        raw = ('Synthetic ' + mode + ' only').encode()
        (output / 'round-1' / name).write_bytes(raw)
        ref = {'task': identity, 'artifact': 'round-1/' + name, 'sha256': hashlib.sha256(raw).hexdigest()}
        original['references'].append(ref)
        (folder / 'packet.json').write_text(json.dumps({'campaign_task': {**original, 'mode': mode}}))
        (folder / 'scientific-disposition.json').write_text(json.dumps({'task': identity,
            'status': 'DISPOSITION_RECORDED', 'review_verdict': 'APPROVE',
            'acceptance_status': 'APPROVED_PROPOSAL_ONLY', 'campaign_output': output.relative_to(tmp_path).as_posix(),
            'artifact_sha256': {ref['artifact']: ref['sha256']}}))
    continuing.require_code_inputs(config, original)
    idea_path = tmp_path / 'tasks' / ('a' * 64) / 'packet.json'
    idea_raw = idea_path.read_bytes()
    idea = json.loads(idea_raw); idea['campaign_task']['experiment'] = 'P003'
    idea_path.write_text(json.dumps(idea))
    with pytest.raises(ValueError, match='REVIEWED_PREDECESSOR_REQUIRED'):
        continuing.require_code_inputs(config, original)
    idea_path.write_bytes(idea_raw)
    path = tmp_path / 'tasks' / ('b' * 64) / 'packet.json'
    packet = json.loads(path.read_text()); packet['campaign_task']['protocol']['decision_sha256'] = 'e' * 64
    path.write_text(json.dumps(packet))
    with pytest.raises(ValueError, match='SPEC_PROTOCOL_CHANGED'):
        continuing.require_code_inputs(config, original)


def test_code_bundle_is_reviewed_by_existing_pipeline_without_execution(tmp_path):
    from orchestrator import campaign_pipeline
    original = prospective_task()
    packet = {'campaign_task': original, 'campaign_artifacts': task_contract(original)}
    outputs = {name: '# Synthetic proposed file: ' + name for name in campaign_pipeline.MODES['code_bundle']}
    answers = [json.dumps(outputs), json.dumps({'review.json': json.dumps(
        {'verdict': 'APPROVE', 'rationale': 'Synthetic proposal review only.'})})]
    client, calls = client_for(answers)
    value = {'task': original, 'references': [], 'protocol': {'descriptor': original['protocol'],
        'decision': {'decision': 'APPLY', '_decision_sha256': original['protocol']['decision_sha256']}}}
    output = tmp_path / 'campaigns/isles24-pilot/pipeline/code'
    with patch('orchestrator.campaign_pipeline.grounding', return_value={}), patch(
            'orchestrator.research_context.evidence_context', return_value={}):
        receipt = run_pipeline(SimpleNamespace(ROOT=tmp_path), 'code_bundle', original['request'], output,
            BrokerStages('fixture', {}, packet, client=client),
            supplement={'continuing-research-inputs.json': json.dumps(value)})
    assert calls == ['continuation', 'review']
    assert receipt['acceptance_status'] == 'APPROVED_PROPOSAL_ONLY'
    assert all((output / 'round-1' / name).read_text() == raw for name, raw in outputs.items())
    assert not (tmp_path / 'campaigns/isles24-pilot/experiments/P002/run.py').exists()


def test_protocol_verification_requires_exact_installed_source_before_reading_decision(monkeypatch):
    from orchestrator import remote_supervisor
    observed = []
    def changed(root, source):
        observed.append((root, source))
        raise ValueError('SYNTHETIC_SOURCE_PIN_CHANGED')
    monkeypatch.setattr(remote_supervisor, 'checked_source', changed)
    with pytest.raises(ValueError, match='SOURCE_PIN_CHANGED'):
        continuing.read_protocol({'source_root': '/fixed/source', 'source': 'f' * 40},
            prospective_task(), original_client=lambda *args: pytest.fail('No original/model request before source check'))
    assert observed == [('/fixed/source', 'f' * 40)]


def test_investigator_can_select_fixed_operation_but_not_arbitrary_commands():
    original = task()
    proposed = choice(original)
    proposed['successor'] = {'schema':'continuing-operation/v1','operation_id':'synthetic-import-v1',
        'kind':'IMPORT_RESULT','inputs':{'completion':'a'*64}}
    assert continuing.selection(original, proposed) == proposed
    assert 'IMPORT_RESULT' in continuing.investigator_instruction(original)
    proposed['successor']['inputs']['command'] = 'forbidden'
    with pytest.raises(ValueError): continuing.selection(original, proposed)
