"""Actual helper/pipeline integration with explicitly synthetic provider replies."""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from orchestrator import continuing_research as continuing, protocol_proposals as protocol
from orchestrator.hosted_campaign import BrokerStages, run_pipeline, recover_projection
from orchestrator.hosted_campaign_task import completed_pipeline, task_contract
from test_hosted_campaign import client_for


def fixture():
    task = {'schema': protocol.TASK_SCHEMA, 'task_id': 'fixture-initial-protocol-v1',
        'experiment': 'P002', 'mode': protocol.MODE, 'request': 'Propose methodology and preserve missing-evidence deferral.',
        'references': [], 'selected_by': None}
    files = {'protocol.proposed.json': json.dumps({'schema': 'scientific-protocol-proposal/v1',
        'protocol_id': 'fixture-protocol', 'experiment': 'P002', 'status': 'DEFERRED',
        'design': 'Fixture methodology proposal only.', 'rationale': 'Original input evidence is unavailable.',
        'unknowns': ['Obtain the actual recorded input inventory and literature.'], 'evidence': [],
        'data_sources': {name: None for name in protocol.DATA_OUTPUTS}}),
        'methodology.proposed.md': 'Fixture methodology and limitations; no execution or acceptance.',
        'literature-review.proposed.json': json.dumps({'schema': 'recorded-literature-review/v1',
            'status': 'DEFERRED', 'rationale': 'No actual literature evidence supplied.', 'citations': [],
            'unknowns': ['Actual literature needed.']})}
    for kind, name in protocol.DATA_OUTPUTS.items():
        files[name] = json.dumps({'schema': 'protocol-evidence-unavailable/v1', 'kind': kind,
            'reason': 'Original evidence was not supplied to this fixture.'})
    supplement = {'continuing-research-inputs.json': json.dumps({'task': task, 'references': []}, sort_keys=True)}
    return task, files, supplement


@pytest.mark.parametrize('verdict', ['APPROVE', 'REQUEST_CHANGES'])
def test_first_protocol_uses_existing_opposing_stages_and_preserves_deferral(tmp_path, verdict):
    task, files, supplement = fixture()
    packet = {'campaign_task': task, 'campaign_artifacts': task_contract(task)}
    provider, calls = client_for([json.dumps(files), json.dumps({'review.json': json.dumps(
        {'verdict': verdict, 'rationale': 'Fixture review of methodology and acknowledged unknowns.'})})])
    replies = {}; prompts = []
    def client(socket, operation, body):
        prompts.append(body['prompt']); reply = provider(socket, operation, body)
        replies[body['stage']] = reply; return reply
    output = tmp_path/'campaigns/isles24-pilot/pipeline/original'
    with patch('orchestrator.protocol_proposals.grounding', return_value={}), patch(
            'orchestrator.research_context.evidence_context', return_value={}):
        receipt = run_pipeline(SimpleNamespace(ROOT=tmp_path), protocol.MODE, task['request'], output,
            BrokerStages('fixture', {}, packet, client=client), supplement=supplement)
        completed_pipeline(tmp_path, output, packet, {}, supplement=supplement)
        assert receipt['protocol_proposal_validation']['status'] == 'DEFERRED'
        assert receipt['protocol_proposal_validation']['scientific_approval'] is False
        assert receipt['acceptance_status'] == ('APPROVED_PROPOSAL_ONLY' if verdict == 'APPROVE' else 'NOT_ACCEPTED')
        before = {str(p): p.read_bytes() for p in output.rglob('*') if p.is_file()}
        def original(socket, operation, body):
            assert operation == 'stage_status'; return {**replies[body['stage']], 'duplicate': True}
        recovered = recover_projection(SimpleNamespace(ROOT=tmp_path), protocol.MODE, task['request'], output,
            output.parent/'recovered', BrokerStages('fixture', {}, packet, client=original, recovery=True), supplement=supplement)
        assert recovered['protocol_proposal_validation'] == receipt['protocol_proposal_validation']
        assert before == {str(p): p.read_bytes() for p in output.rglob('*') if p.is_file()}
        assert len(calls) == 2
    assert all('DEFERRED' in prompt and 'grants no data access' in prompt for prompt in prompts)
    assert not list(tmp_path.rglob('decision.json'))


def test_missing_originals_cannot_be_relabelled_complete_before_reviewer(tmp_path):
    task, files, supplement = fixture()
    proposal = json.loads(files['protocol.proposed.json']); proposal.update(status='PROPOSED', unknowns=[])
    files['protocol.proposed.json'] = json.dumps(proposal)
    provider, calls = client_for([json.dumps(files)])
    packet = {'campaign_task': task, 'campaign_artifacts': task_contract(task)}
    with patch('orchestrator.protocol_proposals.grounding', return_value={}), patch(
            'orchestrator.research_context.evidence_context', return_value={}):
        with pytest.raises(ValueError, match='MISSING_EVIDENCE_REQUIRES_DEFERRAL'):
            run_pipeline(SimpleNamespace(ROOT=tmp_path), protocol.MODE, task['request'],
                tmp_path/'campaigns/isles24-pilot/pipeline/refused', BrokerStages('fixture', {}, packet, client=provider), supplement=supplement)
    assert calls == ['continuation']
    assert not list(tmp_path.rglob('receipt.json'))


def test_protocol_helper_grounding_uses_selected_current_context_without_old_p001_results():
    from orchestrator.campaign_pipeline import grounding
    task, _, _ = fixture()
    root = Path(__file__).resolve().parents[1]
    actual = grounding(root, 'P002', protocol_task=task)
    assert actual['protocol-proposal-scope.json']
    assert 'PROPOSAL_ONLY' in actual['protocol-proposal-scope.json']
    old = {**task, 'schema': continuing.TASK_SCHEMA}
    with pytest.raises(ValueError, match='TYPED_TASK_REQUIRED'): continuing.task_contract(old)
