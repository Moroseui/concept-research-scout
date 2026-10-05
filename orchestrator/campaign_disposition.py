"""Exact campaign disposition presentation and pure prospective capacity check."""
import json
import re
from orchestrator.hosted_context import (
    CAMPAIGN_EVIDENCE_MARKER, campaign_prompt_reference, compose_input, measure_input,
)
from orchestrator.hosted_cycle import encoded
from orchestrator.public_export import text

# ASCII placeholders conservatively cover the existing enforced UTF-8 byte
# ceilings in hosted_campaign.checked_reply. No prior-answer limit is reduced.
PRIOR_ANSWER_CHARACTERS = 80000
SUMMARY_KEYS = ('status', 'review_verdict', 'acceptance_status',
                'campaign_receipt_sha256', 'artifact_sha256')
REVIEW_POLICY = 'HOSTED_BOUNDED_REVIEW_WITH_DISPOSITION'
INSTRUCTION = (
    'Record Astra disposition of the bounded scientific proposal and its unchanged opposing review below. '
    'Address the criticism and identify a next eligible action within the installed request, or a reasoned deferral. '
    'A completed model call is not scientific acceptance. REQUEST_CHANGES or REVISE means REVISION_REQUIRED '
    'and NOT_ACCEPTED: preserve that outcome and identify corrections or evidence needed before reconsideration. '
    'Do not override a negative review, claim agreement, adopt a proposal, amend frozen artifacts, execute work, '
    'select a follow-up experiment or grant authority. This stage records a disposition only. '
    'Claude reviewed the scientific proposal and its bound context; the generated operational report has no report review. '
    'Withheld original review text remains unavailable and does not establish absence of criticism.\n'
    'VALIDATED SCIENTIFIC OUTCOME:\n'
)


def _artifact_paths(packet):
    from orchestrator.campaign_pipeline import MODES
    from orchestrator.hosted_campaign_task import task_contract
    contract = task_contract(packet['campaign_task'])
    if packet.get('campaign_artifacts') != contract:
        raise ValueError('CAMPAIGN_SUMMARY_ARTIFACT_CONTRACT')
    mode = contract['mode']
    return {'round-1/' + name for name in (
        MODES[mode] + ['review.json', 'campaign_' + mode + '.hosted-provenance.json',
                      'campaign_' + mode + '_review.hosted-provenance.json'])}


def _outcomes():
    # Legacy approved receipts predate all three review-policy fields. They are
    # still represented with null verdict/acceptance, never invented approval.
    return [('REVIEWED_PROPOSAL_NOT_ADOPTED', None, None),
            ('REVIEWED_PROPOSAL_NOT_ADOPTED', 'APPROVE', 'APPROVED_PROPOSAL_ONLY'),
            ('REVISION_REQUIRED', 'REVISE', 'NOT_ACCEPTED'),
            ('REVISION_REQUIRED', 'REQUEST_CHANGES', 'NOT_ACCEPTED')]


def summary_characters(packet):
    """Exact maximum JSON length for the checked, finite five-field schema."""
    hashes = {name: 'f' * 64 for name in sorted(_artifact_paths(packet))}
    return max(len(json.dumps(dict(zip(SUMMARY_KEYS,
        (status, verdict, acceptance, 'f' * 64, hashes)))))
        for status, verdict, acceptance in _outcomes())


def checked_summary(packet, outcome):
    """Retain the original selected fields after the native outcome checks.

    This validates the summary's shape and bounds, not provider provenance or
    artifact-file bytes. completed_pipeline still verifies those originals.
    """
    if not isinstance(outcome, dict):
        raise ValueError('CAMPAIGN_SUMMARY_OUTCOME_REQUIRED')
    fields = {'review_completion_policy', 'review_verdict', 'acceptance_status'}
    state = tuple(outcome.get(key) for key in SUMMARY_KEYS[:3])
    if not fields.intersection(outcome):
        if state != _outcomes()[0]:
            raise ValueError('CAMPAIGN_SUMMARY_LEGACY_APPROVED_REQUIRED')
    elif (not fields.issubset(outcome) or outcome['review_completion_policy'] != REVIEW_POLICY
            or state not in _outcomes()[1:]):
        raise ValueError('CAMPAIGN_SUMMARY_REVIEW_POLICY_BINDING')
    hashes = outcome.get('artifact_sha256')
    if not isinstance(hashes, dict) or set(hashes) != _artifact_paths(packet):
        raise ValueError('CAMPAIGN_SUMMARY_ARTIFACT_SET')
    for value in [outcome.get('campaign_receipt_sha256'), *hashes.values()]:
        if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
            raise ValueError('CAMPAIGN_SUMMARY_ORIGINAL_HASH_REQUIRED')
    summary = json.dumps({key: outcome.get(key) for key in SUMMARY_KEYS})
    text(summary, limit=summary_characters(packet))
    return summary


def _compose(packet, source, report_text, summary_text, continuation, review):
    return (INSTRUCTION + summary_text + '\nREPORT:\n' + report_text
        + CAMPAIGN_EVIDENCE_MARKER + json.dumps(campaign_prompt_reference(encoded(packet), source))
        + '\nCONTINUATION:\n' + continuation + '\nREVIEW:\n' + review)


def prompt(packet, source, report_text, outcome, continuation, review):
    summary = checked_summary(packet, outcome)
    for answer in (continuation, review):
        text(answer, limit=PRIOR_ANSWER_CHARACTERS)
    return _compose(packet, source, report_text, summary, continuation, review)


def preflight(root, source, packet, report_text, *, evidence_config=None):
    """Bound the final third stage before starting the campaign's first model.

    No model output, scientific conclusion or approval is fabricated. The
    placeholders are size projections only and are never dispatched.
    """
    maximum = summary_characters(packet)
    projected = _compose(packet, source, report_text, 'x' * maximum,
                         'x' * PRIOR_ANSWER_CHARACTERS, 'x' * PRIOR_ANSWER_CHARACTERS)
    from orchestrator.scientific_evidence_runtime import controller_options
    options = controller_options(evidence_config, root, source, packet, 'disposition')
    final, _ = compose_input(root, encoded(packet), projected,
        verified_source=source, family='codex', output_format='markdown', **options)
    return {**measure_input(final, 'codex', 'disposition', task_state=packet),
        'projection': 'ENFORCED_PRIOR_REPLY_AND_SUMMARY_CHARACTER_CEILINGS',
        'prior_answer_characters_each': PRIOR_ANSWER_CHARACTERS,
        'summary_characters': maximum,
        'summary_bound_basis': 'CHECKED_OUTCOME_ENUMS_REGISTERED_ARTIFACT_PATHS_AND_SHA256',
        'admissions': 0}
