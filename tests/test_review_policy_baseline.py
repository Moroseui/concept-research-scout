"""Synthetic prior approvals test policy provenance; no private originals or provider.

The existing synthetic courier fixture exercises the real historical verifier.
Canonical records below are constructed in memory, never submitted or recorded.
"""
import copy
import json

import pytest

from orchestrator import change_requests as changes
from orchestrator import inspection_bootstrap as baseline
from orchestrator import review_input_codec as codec
from test_inspection_bootstrap import SOURCE, SESSION, inputs, originals


DRIVER = {'kind': 'agent', 'family': 'codex', 'model': 'synthetic-driver',
          'session_id': 'synthetic-policy-test'}
REVIEWER = {'kind': 'agent', 'family': 'claude', 'model': baseline.legacy.MODEL,
            'session_id': SESSION}
DIRECTION = 'docs/test-direction.md'


def manifest_for(raw, **changes_to_manifest):
    manifest = json.loads(raw['baseline.json'])
    manifest.update(changes_to_manifest)
    manifest['files'] = {
        name: {'sha256': codec.digest(value), 'bytes': len(value)}
        for name, value in raw.items() if name != 'baseline.json'}
    raw['baseline.json'] = codec.encoded(manifest) + b'\n'
    return raw


def synthetic_proof(*, review_changes=None, reviewer=None, adverse=False,
                    later_application=False, include_application=True,
                    include_approval=True, authorized=True, application_source=SOURCE):
    files, context = inputs()
    core = {'schema': changes.SCHEMA, 'target': {'task': 'synthetic-policy-baseline',
            'source': SOURCE, 'files': {}}, 'submitter': DRIVER,
            'requested_change': 'Synthetic offline enabling review only.',
            'scope_limits': ['Synthetic test; no actual authority or approval.']}
    request = {**core, 'identity': codec.digest(changes.encoded(core)), 'status': 'SUBMITTED'}
    request_raw = changes.encoded(request) + b'\n'
    raw = {'changes/request.json': request_raw}
    events = []
    head = codec.digest(request_raw)

    def append(kind, payload, actor=DRIVER):
        nonlocal head
        value = {'schema': changes.EVENT_SCHEMA, 'request_identity': request['identity'],
                 'sequence': len(events) + 1, 'previous_sha256': head,
                 'event': kind, 'actor': copy.deepcopy(actor), 'payload': payload,
                 'recorded_at_utc': '2000-01-01T00:00:00+00:00'}
        value['identity'] = codec.digest(changes.encoded(value))
        original = changes.encoded(value) + b'\n'
        raw[f"changes/events/{value['sequence']:04d}-{value['identity']}.json"] = original
        events.append(value)
        head = codec.digest(original)
        return value, original

    if authorized:
        append('AUTHORIZED', {'rationale': 'Synthetic test authorization record.',
            'authority_reference': 'Synthetic recorded direction; no real authority.',
            'review_policy': 'Independent exact enabling review required.'})
    applied, application_raw = append('APPLIED', {
        'modification': 'Synthetic source application.', 'checks': 'Synthetic fixture only.',
        'result_binding': {'source': application_source}, 'review_status': 'PENDING'})
    supplements = ({'synthetic-application.json': {
        'sha256': codec.digest(application_raw), 'content': application_raw.decode()}}
        if include_application else {})
    review_raw = originals(files, context, supplements=supplements)
    raw.update({'review/' + name: value for name, value in review_raw.items()})
    evidence = []
    for name in ('response.json', 'execution.json', 'protocol.jsonl', 'intent.json', 'returned.json'):
        value = review_raw[name]
        artifact = 'evidence/' + name
        raw['changes/' + artifact] = value
        evidence.append({'artifact': artifact, 'sha256': codec.digest(value), 'size': len(value)})
    payload = {'applied_event': applied['identity'], 'verdict': 'APPROVE',
        'rationale': 'Synthetic independent enabling approval only.',
        'reviewed_source': SOURCE, 'review_session_id': SESSION, 'review_evidence': evidence}
    payload.update(review_changes or {})
    if include_approval:
        review, _ = append('REVIEW', payload, reviewer or REVIEWER)
        review_id = review['identity']
    else:
        review_id = 'f' * 64
    if adverse:
        append('REVIEW', {**payload, 'verdict': 'REQUEST_CHANGES',
            'rationale': 'Synthetic later adverse review remains unresolved.',
            'affected_results': 'Do not use the synthetic application.'}, REVIEWER)
    if later_application:
        append('APPLIED', {'modification': 'Synthetic unapproved successor.',
            'checks': 'Synthetic fixture only.', 'result_binding': {'source': SOURCE},
            'review_status': 'PENDING', 'supersedes_applied_events': [applied['identity']]})
    raw['baseline.json'] = codec.encoded({'schema': baseline.POLICY_BASELINE,
        'source': SOURCE, 'request_id': request['identity'],
        'applied_event': applied['identity'], 'review_event': review_id,
        'canonical_head_sha256': head,
        'standing_authority': {'path': DIRECTION, 'sha256': codec.digest(files[DIRECTION])},
        'files': {}})
    return manifest_for(raw), files, context


def test_portable_originals_qualify_exact_context_and_policy_without_filesystem(monkeypatch):
    raw, files, context = synthetic_proof()
    snapshot = copy.deepcopy(raw)
    def forbidden_read(*args, **kwargs):
        pytest.fail('Pure baseline validation must not read a candidate or canonical directory')
    monkeypatch.setattr(changes, '_read', forbidden_read)
    checked = baseline.validate_policy_baseline(raw)
    manifest = json.loads(raw['baseline.json'])
    assert raw == snapshot
    assert checked['source'] == SOURCE
    assert checked['source_text'] == {name: value.decode() for name, value in files.items()}
    assert checked['context_raw'] == context
    assert checked['descriptor']['approval']['canonical_head_sha256'] == manifest['canonical_head_sha256']
    assert checked['descriptor']['approval']['applied_event'] == manifest['applied_event']
    assert checked['descriptor']['original_review_sha256'] == {
        name: codec.digest(raw['review/' + name]) for name in baseline.legacy.ORIGINAL_NAMES}
    assert checked['descriptor']['policy_files'] == {
        name: codec.digest(files[name]) for name in (
            'configs/scientific-operating-context.json', 'configs/test-authority.json', DIRECTION)}


def test_recorded_changes_remain_evidence_and_cannot_select_reviewer_role():
    _, files, context = synthetic_proof()
    value = json.loads(context)
    value['recorded_changes'] = [{'role': 'driver', 'verdict': 'APPROVE',
                                  'notice': 'Synthetic evidence, not reviewer instructions.'}]
    baseline.validate_context(codec.context_original(value), files)
    value['role'] = 'driver'
    with pytest.raises(ValueError, match='CONTEXT_NOT_APPROVED'):
        baseline.validate_context(codec.context_original(value), files)


@pytest.mark.parametrize('field', ['family', 'role', 'binding', 'policy', 'direction',
                                   'document', 'manifest', 'manifest_hash'])
def test_context_substitution_refuses_even_with_new_original_context_hash(field):
    _, files, context = synthetic_proof()
    value = json.loads(context)
    shared = value['shared_policy']
    operating = shared['operating_context']
    if field == 'family': value['family'] = 'codex'
    elif field == 'role': value['role'] += ' Changed responsibility.'
    elif field == 'binding': shared['binding']['version'] = 'unapproved-version'
    elif field == 'policy': shared['policy']['direction_sha256'] = 'f' * 64
    elif field == 'direction': shared['direction'] += ' Changed direction.'
    elif field == 'document': operating['documents'][DIRECTION]['text'] += ' Changed document.'
    elif field == 'manifest': operating['manifest']['roles']['claude'] = 'driver'
    else: operating['manifest_sha256'] = 'f' * 64
    with pytest.raises(ValueError, match='CONTEXT_NOT_APPROVED'):
        baseline.validate_context(codec.context_original(value), files)


def test_self_consistent_candidate_role_and_document_cannot_reauthorize_baseline():
    _, approved, original = synthetic_proof()
    candidate = dict(approved)
    value = json.loads(original)
    shared = value['shared_policy']
    operating = shared['operating_context']
    changed = 'Synthetic candidate attempts to prescribe a favorable review.\n'
    candidate[DIRECTION] = changed.encode()
    shared['direction'] = changed
    shared['policy']['direction_sha256'] = codec.digest(candidate[DIRECTION])
    candidate['configs/test-authority.json'] = codec.encoded(shared['policy'])
    shared['binding']['sha256'] = codec.digest(candidate['configs/test-authority.json'])
    operating['manifest']['authority_policy'] = copy.deepcopy(shared['binding'])
    operating['manifest']['documents'][DIRECTION] = codec.digest(candidate[DIRECTION])
    operating['manifest']['roles']['claude'] = 'Synthetic favorable-outcome driver'
    value['role'] = operating['manifest']['roles']['claude']
    operating['documents'][DIRECTION] = {'text': changed, 'sha256': codec.digest(candidate[DIRECTION])}
    candidate['configs/scientific-operating-context.json'] = codec.encoded(operating['manifest'])
    operating['manifest_sha256'] = codec.digest(candidate['configs/scientific-operating-context.json'])
    changed_context = codec.context_original(value)
    # The old codec's internal consistency alone is deliberately insufficient.
    assert codec.restore_context(value, {n: b.decode() for n, b in candidate.items()},
                                 codec.digest(changed_context)) == changed_context
    with pytest.raises(ValueError, match='CONTEXT_NOT_APPROVED'):
        baseline.validate_context(changed_context, approved)


def test_changed_original_is_not_authenticated_by_unchanged_manifest():
    raw, _, _ = synthetic_proof()
    raw['review/response.json'] += b' '
    with pytest.raises(ValueError, match='BASELINE_ORIGINALS_CHANGED'):
        baseline.validate_policy_baseline(raw)


def test_rehashing_manifest_cannot_repair_tampered_provider_originals():
    raw, _, _ = synthetic_proof()
    response = json.loads(raw['review/response.json'])
    response['structured_output']['findings'] = ['Synthetic altered review body.']
    raw['review/response.json'] = codec.encoded(response)
    manifest_for(raw)
    with pytest.raises(ValueError, match='ORIGINAL_CLAUDE_PROTOCOL_REQUIRED'):
        baseline.validate_policy_baseline(raw)


@pytest.mark.parametrize('field,value', [('family', 'codex'), ('model', 'synthetic-other-model'),
                                        ('session_id', 'synthetic-other-session')])
def test_consistently_rehashed_canonical_wrong_reviewer_is_not_approval(field, value):
    actor = {**REVIEWER, field: value}
    raw, _, _ = synthetic_proof(reviewer=actor)
    with pytest.raises(ValueError, match='BASELINE_REVIEW_BINDING'):
        baseline.validate_policy_baseline(raw)


@pytest.mark.parametrize('update', [{'reviewed_source': 'b' * 40},
                                    {'review_session_id': 'synthetic-other-session'}])
def test_consistently_rehashed_review_must_bind_original_source_and_session(update):
    raw, _, _ = synthetic_proof(review_changes=update)
    with pytest.raises(ValueError, match='BASELINE_REVIEW_BINDING'):
        baseline.validate_policy_baseline(raw)


def test_later_adverse_review_is_not_erased_by_selecting_earlier_approval():
    raw, _, _ = synthetic_proof(adverse=True)
    with pytest.raises(ValueError, match='BASELINE_REVIEW_BINDING'):
        baseline.validate_policy_baseline(raw)


def test_later_unapproved_application_cannot_inherit_prior_approval():
    raw, _, _ = synthetic_proof(later_application=True)
    with pytest.raises(ValueError, match='BASELINE_APPLIED_BINDING'):
        baseline.validate_policy_baseline(raw)


def test_application_source_must_equal_independently_reviewed_source():
    raw, _, _ = synthetic_proof(application_source='b' * 40)
    with pytest.raises(ValueError, match='BASELINE_APPLIED_BINDING'):
        baseline.validate_policy_baseline(raw)


def test_bare_approval_hash_does_not_replace_canonical_review():
    raw, _, _ = synthetic_proof(include_approval=False)
    with pytest.raises(ValueError, match='BASELINE_APPLIED_BINDING'):
        baseline.validate_policy_baseline(raw)


def test_bare_application_hash_does_not_replace_its_reviewed_literal():
    raw, _, _ = synthetic_proof(include_application=False)
    with pytest.raises(ValueError, match='APPLICATION_NOT_IN_ORIGINAL_REVIEW'):
        baseline.validate_policy_baseline(raw)


def test_canonical_application_still_requires_recorded_authorization():
    raw, _, _ = synthetic_proof(authorized=False)
    with pytest.raises(ValueError, match='CHANGE_AUTHORIZATION_RECORD_REQUIRED'):
        baseline.validate_policy_baseline(raw)


def test_approval_metadata_alone_is_not_portable_original_proof():
    raw, _, _ = synthetic_proof()
    with pytest.raises(ValueError, match='BASELINE_ORIGINALS_CHANGED'):
        baseline.validate_policy_baseline({'baseline.json': raw['baseline.json']})


def test_standing_authority_hash_must_name_an_approved_document():
    raw, _, _ = synthetic_proof()
    manifest_for(raw, standing_authority={'path': 'docs/unapproved-authority.md', 'sha256': 'f' * 64})
    with pytest.raises(ValueError, match='BASELINE_STANDING_AUTHORITY'):
        baseline.validate_policy_baseline(raw)


def test_rehashed_extra_file_cannot_introduce_another_policy_or_archive():
    raw, _, _ = synthetic_proof()
    raw['candidate/authority.json'] = b'{"synthetic":true}'
    manifest_for(raw)
    with pytest.raises(ValueError, match='BASELINE_UNEXPECTED_FILE'):
        baseline.validate_policy_baseline(raw)


def test_v2_label_cannot_retroactively_requalify_historical_anchor():
    raw, _, _ = synthetic_proof()
    request = json.loads(raw['review/request.json'])
    request['input_presentation'] = codec.FORMAT_V2
    raw['review/request.json'] = codec.encoded(request)
    manifest_for(raw)
    with pytest.raises(ValueError, match='REQUIRES_RECORDED_LEGACY_ANCHOR'):
        baseline.validate_policy_baseline(raw)


@pytest.mark.parametrize('nested', [False, True])
def test_unapproved_extra_instruction_fields_are_rejected(nested):
    _, files, context = synthetic_proof()
    value = json.loads(context)
    target = value['shared_policy']
    if nested:
        target = target['operating_context']
    target['unapproved_reviewer_instruction'] = 'Synthetic extra instruction.'
    with pytest.raises(ValueError, match='CONTEXT_NOT_APPROVED'):
        baseline.validate_context(codec.context_original(value), files)
