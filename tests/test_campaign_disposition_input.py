"""Lossless final-stage evidence and capacity; no scientific/provider assertions."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from orchestrator import hosted_context as context
from orchestrator import campaign_disposition as disposition
from orchestrator.hosted_cycle import encoded

SOURCE = 'a' * 40


def packet():
    return {'trigger': 'installed-research-request',
        'campaign_task': {'mode': 'discuss', 'request': 'Unique bounded request.',
                          'task_id': 'discussion-fixture'},
        'campaign_artifacts': {'version': 1, 'experiment': 'P001', 'mode': 'discuss'},
        'research_request_binding': {'source': SOURCE, 'task_id': 'discussion-fixture'},
        'reviewer_evidence': {'qualification': 'Unique original evidence limitation.'},
        'recorded_changes': {'criticism': 'Unique pending reviewer correction.'},
        'decision_inbox': {'next': 'Proposal only'}, 'jobs': []}


@pytest.fixture
def root(tmp_path, monkeypatch):
    # Synthetic original-only source; the new presentation profile has separate tests.
    tmp_path.chmod(0o700)
    module = tmp_path / 'orchestrator/hosted_context.py'
    module.parent.mkdir()
    module.write_text('"""Synthetic original-only hosted source; no outer document view."""\n')
    monkeypatch.setattr('orchestrator.remote_supervisor.checked_source',
        lambda root, source: Path(root))
    monkeypatch.setattr(context, 'build',
        lambda root, state: {'task_state': state, 'policy': 'Synthetic fixed policy.'})
    return tmp_path


def body(value):
    return disposition.prompt(value, SOURCE, 'Unique unchanged report.',
        outcome(),
        'Unique original discussion.', 'Unique original opposing criticism.')


def outcome():
    return {'status': 'REVISION_REQUIRED', 'review_verdict': 'REQUEST_CHANGES',
        'acceptance_status': 'NOT_ACCEPTED',
        'review_completion_policy': 'HOSTED_BOUNDED_REVIEW_WITH_DISPOSITION',
        'campaign_receipt_sha256': 'a' * 64,
        'artifact_sha256': {name: 'b' * 64 for name in (
            'round-1/discussion.md', 'round-1/review.json',
            'round-1/campaign_discuss.hosted-provenance.json',
            'round-1/campaign_discuss_review.hosted-provenance.json')}}


@pytest.mark.parametrize('family', ['codex', 'claude'])
def test_full_packet_reconstructs_with_each_original_present_once(root, family):
    value = packet()
    final, current = context.compose_input(root, encoded(value), body(value),
        verified_source=SOURCE, family=family)
    ref = context.campaign_prompt_reference(encoded(value), SOURCE)
    restored = {**{key: current['task_state'][key] for key in ref['task_state_keys']},
                **ref['packet_header']}
    assert encoded(restored) == encoded(value)
    assert ref['packet_sha256'] == hashlib.sha256(encoded(value)).hexdigest()
    for literal in ['Unique original evidence limitation.', 'Unique pending reviewer correction.',
                    'Unique bounded request.', 'Unique unchanged report.',
                    'Unique original discussion.', 'Unique original opposing criticism.']:
        assert final.count(literal) == 1
    assert 'REQUEST_CHANGES' in final and 'NOT_ACCEPTED' in final
    assert ref['trust'] == current['task_state_trust'] == context.TRUST


def test_default_change_warning_does_not_falsify_packet_reconstruction(root):
    value = packet(); del value['recorded_changes']
    final, current = context.compose_input(root, encoded(value), body(value),
        verified_source=SOURCE, family='codex')
    ref = context.campaign_prompt_reference(encoded(value), SOURCE)
    assert 'TASK_CHANGE_CONTEXT_NOT_SUPPLIED' in final
    assert encoded({**{key: current['task_state'][key] for key in ref['task_state_keys']},
                    **ref['packet_header']}) == encoded(value)


@pytest.mark.parametrize('field', ['packet_sha256', 'source', 'packet_header', 'task_state_keys'])
def test_changed_reference_refuses_instead_of_dropping_evidence(root, field):
    value = packet(); ref = context.campaign_prompt_reference(encoded(value), SOURCE)
    wrong = deepcopy(ref)
    wrong[field] = {} if field == 'packet_header' else [] if field == 'task_state_keys' else 'b' * len(wrong[field])
    changed = body(value).replace(json.dumps(ref), json.dumps(wrong))
    with pytest.raises(ValueError, match='CAMPAIGN_SOURCE_BOUND_REFERENCE_CHANGED'):
        context.compose_input(root, encoded(value), changed,
            verified_source=SOURCE, family='codex')


def test_packet_mutation_or_duplicate_marker_refuses(root):
    value = packet(); original = body(value)
    value['recorded_changes']['criticism'] = 'Changed criticism.'
    with pytest.raises(ValueError, match='CAMPAIGN_SOURCE_BOUND_REFERENCE_CHANGED'):
        context.compose_input(root, encoded(value), original,
            verified_source=SOURCE, family='codex')
    value = packet()
    with pytest.raises(ValueError, match='CAMPAIGN_EXACT_REFERENCE_SECTION_REQUIRED'):
        context.compose_input(root, encoded(value),
            body(value) + context.CAMPAIGN_EVIDENCE_MARKER + '{}',
            verified_source=SOURCE, family='codex')


def test_distinct_campaign_contract_does_not_relax_eligibility():
    value = packet()
    with pytest.raises(ValueError, match='HOSTED_EVIDENCE_REFERENCE_PACKET'):
        context.same_prompt_reference(encoded(value), SOURCE)
    value['research_request_binding']['source'] = 'b' * 40
    with pytest.raises(ValueError, match='CAMPAIGN_REFERENCE_SOURCE'):
        context.campaign_prompt_reference(encoded(value), SOURCE)
    value = packet(); value['campaign_artifacts']['mode'] = 'readiness'
    with pytest.raises(ValueError, match='CAMPAIGN_REFERENCE_CONTRACT'):
        context.campaign_prompt_reference(encoded(value), SOURCE)


def test_projection_bounds_actual_accepted_answers_and_summary(root):
    value = packet()
    measured = disposition.preflight(root, SOURCE, value, 'report')
    final, _ = context.compose_input(root, encoded(value),
        disposition.prompt(value, SOURCE, 'report', outcome(),
            'a' * disposition.PRIOR_ANSWER_CHARACTERS,
            'b' * disposition.PRIOR_ANSWER_CHARACTERS),
        verified_source=SOURCE, family='codex')
    assert measured['characters'] >= len(final)
    assert measured['characters'] - len(final) < 100
    assert measured['admissions'] == measured['provider_calls'] == 0
    assert measured['projection'] == 'ENFORCED_PRIOR_REPLY_AND_SUMMARY_CHARACTER_CEILINGS'


def test_future_third_stage_overflow_refuses_before_any_model(root, monkeypatch):
    monkeypatch.setattr(context, 'build',
        lambda root, state: {'task_state': state, 'policy': 'x' * 900000})
    with pytest.raises(context.InputTooLarge) as error:
        disposition.preflight(root, SOURCE, packet(), 'report')
    assert error.value.measurement['stage'] == 'disposition'
    assert error.value.measurement['provider_calls'] == 0


def test_actual_reply_and_summary_cannot_exceed_projected_bound(root):
    with pytest.raises(ValueError):
        disposition.prompt(packet(), SOURCE, 'report', {},
            'a' * (disposition.PRIOR_ANSWER_CHARACTERS + 1), 'review')
    with pytest.raises(ValueError):
        disposition.prompt(packet(), SOURCE, 'report',
            {'artifact_sha256': 'a' * 80000}, 'author', 'review')


@pytest.mark.parametrize('change', [
    {'status': 'COMPLETE'}, {'review_verdict': 'APPROVE'},
    {'acceptance_status': 'APPROVED_PROPOSAL_ONLY'}, {'review_completion_policy': None},
    {'review_verdict': None, 'acceptance_status': None},
    {'status': True}, {'campaign_receipt_sha256': 'a' * 63},
    {'campaign_receipt_sha256': 'A' * 64}, {'campaign_receipt_sha256': 1},
])
def test_malformed_outcome_never_reaches_prompt(change):
    value = outcome(); value.update(change)
    with pytest.raises(ValueError, match='CAMPAIGN_SUMMARY'):
        disposition.prompt(packet(), SOURCE, 'report', value, 'author', 'review')


@pytest.mark.parametrize('mutation', ['missing', 'extra', 'hash', 'type', 'other-mode'])
def test_exact_registered_artifacts_and_original_digests_required(mutation):
    value = outcome()
    if mutation == 'missing': value['artifact_sha256'].pop('round-1/discussion.md')
    elif mutation == 'extra': value['artifact_sha256']['round-1/extra.md'] = 'b' * 64
    elif mutation == 'hash': value['artifact_sha256']['round-1/discussion.md'] = 'not a hash'
    elif mutation == 'type': value['artifact_sha256'] = ['round-1/discussion.md']
    else:
        value['artifact_sha256']['round-1/selection.json'] = value['artifact_sha256'].pop('round-1/discussion.md')
    with pytest.raises(ValueError, match='CAMPAIGN_SUMMARY'):
        disposition.prompt(packet(), SOURCE, 'report', value, 'author', 'review')


def test_historical_approved_null_fields_are_preserved_without_fabricated_verdict():
    value = outcome(); value['status'] = 'REVIEWED_PROPOSAL_NOT_ADOPTED'
    for key in ('review_completion_policy', 'review_verdict', 'acceptance_status'): value.pop(key)
    summary = json.loads(disposition.checked_summary(packet(), value))
    assert summary == {key: value.get(key) for key in disposition.SUMMARY_KEYS}
    assert summary['review_verdict'] is None and summary['acceptance_status'] is None
    value['review_verdict'] = None
    with pytest.raises(ValueError, match='REVIEW_POLICY_BINDING'):
        disposition.checked_summary(packet(), value)


@pytest.mark.parametrize('verdict', ['APPROVE', 'REVISE', 'REQUEST_CHANGES'])
def test_closed_outcomes_keep_exact_actual_summary_and_bound(verdict):
    value = outcome(); value['review_verdict'] = verdict
    value['status'] = 'REVIEWED_PROPOSAL_NOT_ADOPTED' if verdict == 'APPROVE' else 'REVISION_REQUIRED'
    value['acceptance_status'] = 'APPROVED_PROPOSAL_ONLY' if verdict == 'APPROVE' else 'NOT_ACCEPTED'
    summary = disposition.checked_summary(packet(), value)
    assert json.loads(summary) == {key: value.get(key) for key in disposition.SUMMARY_KEYS}
    assert len(summary) <= disposition.summary_characters(packet()) < 1000
    value['irrelevant_to_summary'] = 'A full receipt retains this field separately.'
    assert disposition.checked_summary(packet(), value) == summary


def test_preflight_uses_registered_mode_and_retains_both_prior_answer_ceilings(root):
    value = packet(); value['campaign_task']['mode'] = 'readiness'; value['campaign_artifacts']['mode'] = 'readiness'
    measured = disposition.preflight(root, SOURCE, value, 'report')
    assert 0 < measured['summary_characters'] < 1000
    assert measured['summary_characters'] == disposition.summary_characters(value)
    assert measured['summary_characters'] > disposition.summary_characters(packet())
    assert measured['prior_answer_characters_each'] == 80000
    malformed = deepcopy(value); malformed['campaign_artifacts']['mode'] = 'discuss'
    with pytest.raises(ValueError, match='ARTIFACT_CONTRACT'):
        disposition.preflight(root, SOURCE, malformed, 'report')


def test_full_limit_prior_answers_pass_and_one_extra_byte_refuses():
    disposition.prompt(packet(), SOURCE, 'report', outcome(), 'a' * 80000, 'b' * 80000)
    with pytest.raises(ValueError):
        disposition.prompt(packet(), SOURCE, 'report', outcome(), 'a' * 80001, 'review')
