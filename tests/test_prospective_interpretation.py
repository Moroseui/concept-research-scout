"""Original-result plumbing fixtures; no model or scientific acceptance evidence."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from orchestrator import continuing_research as continuing, scientific_job_results as results
from orchestrator.hosted_campaign import BrokerStages, run_pipeline, recover_projection
from orchestrator.hosted_campaign_task import completed_pipeline, task_contract
from orchestrator.hosted_cycle import encoded
from test_hosted_campaign import client_for


def fixture():
    prefix = 'campaigns/isles24-pilot/experiments/P002/'
    task = {'schema': continuing.PROSPECTIVE_SCHEMA, 'task_id': 'fixture-interpret-v1',
        'experiment': 'P002', 'mode': 'interpret', 'request': 'Interpret the original fixture aggregates with limitations.',
        'references': [], 'selected_by': None,
        'protocol': {'subject': 'fixture-protocol', 'bindings': {'source': 'c'*40, 'experiment': 'P002'},
            'decision_path': '/private/formal-decisions/protocol/round-1/decision.json', 'decision_sha256': 'd'*64},
        'import_result': {'operation': 'a'*64, 'result_sha256': 'b'*64}}
    version = {'core_path': 'scientific-version.json', 'core_sha256': 'f'*64,
        'decision_path': 'scientific-authority/fixture/round-1/decision.json', 'decision_sha256': '1'*64}
    context = {prefix+name: 'Exact fixture executed '+name for name in
               ('run.py','SPEC.md','settings.json','requirements.txt','validate_return.py','publication.json')}
    core = {'source': 'c'*40, 'experiment': 'P002', 'scientific_version': version,
        'protocol': {'decision_sha256': 'd'*64}, 'code': prefix+'run.py', 'spec': prefix+'SPEC.md',
        'settings': prefix+'settings.json', 'requirements': prefix+'requirements.txt',
        'files': {name: hashlib.sha256(body.encode()).hexdigest() for name, body in context.items()}}
    value = {'schema': results.SCHEMA, 'status': results.STATUS, 'completion': 'e'*64,
        'source': 'c'*40, 'experiment': 'P002', 'scientific_version': version,
        'protocol_decision_sha256': 'd'*64, 'result_manifest_sha256': '2'*64,
        'event': {'event': 'e'*64, 'source': 'c'*40, 'execution_binding': core, 'result_manifest_sha256': '2'*64},
        'aggregates': {'summary.json': '{"fixture_count":3}'},
        'aggregate_file_sha256': {'summary.json': hashlib.sha256(b'{"fixture_count":3}').hexdigest()},
        'scientific_context': context, 'scientific_acceptance': False, 'model_calls': 0,
        'validation_status': 'PENDING_FORMAL_SCIENTIFIC_VALIDATION', 'original_outputs_modified': False}
    receipt = {'schema': 'scientific-result-import-receipt/v1', 'status': results.STATUS,
        'source': 'c'*40, 'experiment': 'P002', 'completion': 'e'*64, 'import': value,
        'original_response_sha256': hashlib.sha256(encoded(value)).hexdigest(),
        'scientific_acceptance': False, 'model_calls': 0, 'interpretation_review_status': 'PENDING',
        'original_outputs_modified': False, 'applied_by': {'kind': 'agent', 'family': 'codex', 'model': 'fixture', 'session_id': 'fixture'}}
    supplement = {'continuing-research-inputs.json': json.dumps({'task': task, 'references': [],
        'protocol': {'descriptor': task['protocol'], 'decision': {'decision': 'APPLY', '_decision_sha256': 'd'*64}},
        'import_result': {'reference': task['import_result'], 'receipt': receipt}}, sort_keys=True)}
    return task, receipt, supplement


@pytest.mark.parametrize('verdict', ['APPROVE', 'REQUEST_CHANGES'])
def test_original_result_reaches_both_roles_and_recovery_without_false_acceptance(tmp_path, verdict):
    task, imported, supplement = fixture()
    packet = {'campaign_task': task, 'campaign_artifacts': task_contract(task)}
    answers = [json.dumps({'interpretation.md': 'Fixture count is 3; scientific validation is still pending.',
        'investigator_next_decision.json': json.dumps({'status': 'PROPOSAL_ONLY', 'rationale': 'Validate the fixture semantics before any acceptance.'})}),
        json.dumps({'review.json': json.dumps({'verdict': verdict, 'rationale': 'Fixture opposing review of the stated limitations.'})})]
    provider, calls = client_for(answers); originals = {}; prompts = []
    def client(socket, operation, body):
        prompts.append(body['prompt']); reply = provider(socket, operation, body)
        originals[body['stage']] = reply; return reply
    output = tmp_path/'campaigns/isles24-pilot/pipeline/original'
    with patch('orchestrator.campaign_pipeline.grounding', return_value={}), patch(
            'orchestrator.research_context.evidence_context', return_value={}), patch(
            'orchestrator.campaign_lifecycle.require_review', side_effect=AssertionError('No fabricated legacy receipt')):
        receipt = run_pipeline(SimpleNamespace(ROOT=tmp_path), 'interpret', task['request'], output,
            BrokerStages('fixture', {}, packet, client=client), supplement=supplement)
        completed_pipeline(tmp_path, output, packet, {}, supplement=supplement)
        assert receipt['acceptance_status'] == ('APPROVED_PROPOSAL_ONLY' if verdict == 'APPROVE' else 'NOT_ACCEPTED')
        assert receipt['result_import_binding']['scientific_acceptance'] is False
        before = {str(p): p.read_bytes() for p in output.rglob('*') if p.is_file()}
        def recover(socket, operation, body):
            assert operation == 'stage_status'
            return {**originals[body['stage']], 'duplicate': True}
        restored = recover_projection(SimpleNamespace(ROOT=tmp_path), 'interpret', task['request'], output,
            output.parent/'recovered', BrokerStages('fixture', {}, packet, client=recover, recovery=True), supplement=supplement)
        assert restored['result_import_binding'] == receipt['result_import_binding']
        assert len(calls) == 2
        assert before == {str(p): p.read_bytes() for p in output.rglob('*') if p.is_file()}
    for prompt in prompts:
        assert 'PENDING_FORMAL_SCIENTIFIC_VALIDATION' in prompt and 'summary.json' in prompt
        assert 'Exact fixture executed settings.json' in prompt and 'Exact fixture executed run.py' in prompt
        assert 'Do not claim the generated return validator ran' in prompt
    assert not (tmp_path/'campaigns/isles24-pilot/experiments/P002/import_receipt.json').exists()


def test_changed_result_protocol_or_executed_context_refuses_before_any_stage():
    task, _, supplement = fixture()
    for modify in ('protocol', 'code', 'accepted'):
        value = json.loads(supplement['continuing-research-inputs.json'])
        imported = value['import_result']['receipt']['import']
        if modify == 'protocol': imported['protocol_decision_sha256'] = '9'*64
        elif modify == 'code': imported['scientific_context']['campaigns/isles24-pilot/experiments/P002/run.py'] = 'Changed code'
        else: imported['scientific_acceptance'] = True
        with pytest.raises(ValueError): continuing.checked_supplement(task, {'continuing-research-inputs.json': json.dumps(value)})
    del task['import_result']
    with pytest.raises(ValueError, match='INTERPRETATION_IMPORT_REQUIRED'): task_contract(task)


def test_import_reader_binds_actual_broker_and_preserves_completed_recovery_after_criticism(tmp_path, monkeypatch):
    task, receipt, _ = fixture(); flags = []
    config = {'state': str(tmp_path), 'broker_socket': 'fixture'}
    directory = tmp_path/'scientific-results'/receipt['completion']; directory.mkdir(parents=True)
    (directory/'original-response.json').write_bytes(encoded(receipt['import']))
    (directory/'import.json').write_bytes(encoded(receipt))
    def saved(cfg, ref, *, kinds, current_review=True):
        assert ref == task['import_result'] and kinds == ('IMPORT_RESULT',)
        flags.append(current_review)
        if current_review: raise ValueError('RESEARCH_CHANGE_REVIEW_PENDING')
        return {'result': receipt}
    monkeypatch.setattr('orchestrator.continuing_operations.read_operation_result', saved)
    def original(socket, operation, body):
        assert operation == 'scientific_job_result' and body == {'completion': 'e'*64}
        return receipt['import']
    with pytest.raises(ValueError, match='REVIEW_PENDING'):
        continuing.read_result_import(config, task, original_client=original)
    actual = continuing.read_result_import(config, task, original_client=original, read_only=True)
    assert actual['receipt'] == receipt and flags == [True, False]
    with pytest.raises(ValueError, match='PROTECTED_JOB_RESULT_CHANGED'):
        continuing.read_result_import(config, task, original_client=lambda *a: {'changed': True}, read_only=True)
    (directory/'original-response.json').write_text('{}')
    with pytest.raises(ValueError, match='SAVED_IMPORT_ORIGINAL_CHANGED'):
        continuing.read_result_import(config, task, original_client=original, read_only=True)


def test_originals_child_accepts_only_its_named_protected_completion(monkeypatch):
    task, receipt, _ = fixture()
    def validate(config, entry, *, client):
        return client('fixture', 'scientific_job_result', {'completion': 'e'*64})
    monkeypatch.setattr(continuing, 'validate_registration', validate)
    value = {'config': {}, 'entry': {}, 'originals': {}, 'result_originals': {'e'*64: receipt['import']}}
    assert continuing._validate_originals_input(value) == receipt['import']
    value['result_originals'] = {}
    with pytest.raises(ValueError, match='ORIGINAL_RESULT_UNAVAILABLE'): continuing._validate_originals_input(value)


def test_historical_interpretation_still_requires_its_original_validation_receipt(tmp_path):
    from orchestrator.campaign_pipeline import execute
    with pytest.raises(ValueError, match='RESULT_IMPORT_REQUIRED'):
        execute(SimpleNamespace(ROOT=tmp_path), 'interpret', 'P001', 'Fixture historical interpretation',
                tmp_path/'campaigns/isles24-pilot/pipeline/legacy')
