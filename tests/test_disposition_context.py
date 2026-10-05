"""Synthetic exact-view checks; no provider, source checkout or system state."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from orchestrator import disposition_context as d, investigator_wakes as wakes, change_requests as changes
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded

SOURCE = 'a' * 40
OLD_SOURCE = 'b' * 40
TASK = 'c' * 64
RESULT = 'd' * 64


def chain():
    core = {'schema': changes.SCHEMA, 'key': 'synthetic',
        'target': {'source': OLD_SOURCE, 'task': 'synthetic-science', 'files': {}},
        'requested_change': 'Synthetic exact context transport test.',
        'scope_limits': ['No scientific execution.'], 'submitter': {'kind': 'human', 'identity': 'synthetic'},
        'risk': 'UNASSESSED'}
    request = {**core, 'identity': hashlib.sha256(changes.encoded(core)).hexdigest(),
        'status': 'SUBMITTED', 'submitted_at_utc': '2026-09-12T00:00:00+00:00'}
    events = []
    head = hashlib.sha256(changes.encoded(request) + b'\n').hexdigest()
    payloads = [
        ('AUTHORIZED', {'rationale': 'Synthetic permission.', 'authority_reference': 'synthetic',
                        'review_policy': 'Independent review remains required.'}),
        ('APPLIED', {'modification': 'Synthetic transport only.', 'checks': ['synthetic'],
                     'result_binding': {'source': OLD_SOURCE}, 'review_status': 'PENDING'}),
        ('REVIEW', {'verdict': 'REQUEST_CHANGES', 'rationale': 'Preserve this complete synthetic criticism.',
                    'review_evidence': 'synthetic original', 'affected_results': ['synthetic context']}),
        ('DISPOSITION', {'rationale': 'Synthetic response preserves criticism.', 'affected_results': ['synthetic context']})]
    states = []
    for kind, payload in payloads:
        if kind == 'REVIEW':
            payload['applied_event'] = events[1]['identity']
        value = {'schema': changes.EVENT_SCHEMA, 'request_identity': request['identity'],
            'sequence': len(events)+1, 'previous_sha256': head, 'event': kind,
            'actor': {'kind': 'human', 'identity': 'synthetic'}, 'recorded_at_utc': '2026-09-12T00:00:00+00:00',
            'payload': payload}
        event = {**value, 'identity': hashlib.sha256(changes.encoded(value)).hexdigest()}
        events.append(event)
        head = hashlib.sha256(changes.encoded(event) + b'\n').hexdigest()
        states.append({'request': deepcopy(request), 'events': deepcopy(events), 'head_sha256': head})
    return states[2], states[3]


def nested(path, value):
    for key in reversed(path):
        value = {key: value}
    return value


def fixture():
    historical, current = chain()
    target = {'scientific_context': 'Synthetic complete context and criticism.\n' * 3000,
              'qualified_result': {'approval': False, 'text': 'No measurement is claimed.'}}
    proof = nested(d.CHARTER_PATH, deepcopy(target))
    proof['packet']['campaign_task'] = {'references': []}
    proof['origin_task'] = TASK
    proof['origin_source'] = OLD_SOURCE
    proof['schema'] = 'disposition-successor-original-proof/v1'
    parent = proof
    for key in d.PREFIX_PATH[:-1]:
        parent = parent.setdefault(key, {})
    parent[d.PREFIX_PATH[-1]] = historical
    event = wakes.event('DISPOSITION', TASK, RESULT)
    wake_core = {'schema': d.WAKE, 'source': SOURCE, 'template_sha256': 'e'*64,
                 'events': [event], 'day': '2026-09-12'}
    evidence = {'installed_charter_evidence': {'source': SOURCE, 'reviewer_evidence': deepcopy(target)},
        'investigator_wake': {**wake_core, 'identity': digest(wake_core)},
        'verified_events': [{'event': event, 'linked_disposition': {
            'originals': proof, 'result_sha256': RESULT, 'result': {'answer': 'Synthetic disposition.'},
            'reviewed_repair': {'status': 'synthetic'}}, 'references': []}],
        'reference_projection': {'available': 0, 'supplied': 0, 'omitted': 0},
        'request_origin': {'source': SOURCE, 'kind': 'service'},
        'scientific_authority': 'Synthetic size fixture, no authority.'}
    return evidence, current


def packet():
    original, current = fixture()
    stored = d.encode_evidence(original, SOURCE)
    value = {'version': 1, 'trigger': 'installed-research-eligibility',
        'scientific_decision_artifacts': {'version': 2},
        'reviewer_evidence': {'catalog_core': {'source': SOURCE, 'request': {
            'task': {'schema': 'investigator-task/v1'}}}, 'input_evidence': stored},
        'recorded_changes': current}
    return value


def prefix(value):
    proof = value['reviewer_evidence']['input_evidence']['verified_events'][0]['linked_disposition']['originals']
    return d._at(proof, d.PREFIX_PATH)


def test_stored_charter_alias_is_lossless_preserves_original_proof_and_large_saving():
    original, _ = fixture()
    before = encoded(original)
    stored = d.encode_evidence(original, SOURCE)
    assert len(encoded(stored)) < len(before) - 100000
    assert encoded(original) == before
    assert encoded(stored['verified_events']) == encoded(original['verified_events'])
    assert stored['installed_charter_evidence']['source'] == SOURCE
    assert stored['installed_charter_evidence']['reviewer_evidence']['schema'] == d.CHARTER_REFERENCE
    assert encoded(d.reconstruct_evidence(stored, SOURCE)) == before
    assert d.encode_evidence(d.reconstruct_evidence(stored, SOURCE), SOURCE) == stored


@pytest.mark.parametrize('key,value', [
    ('source', OLD_SOURCE), ('event_index', True), ('event_index', 3),
    ('origin_task', 'f'*64), ('original_proof_sha256', 'f'*64),
    ('target_sha256', 'f'*64), ('literal_path_in_original_proof', ['shared_policy']),
    ('trust', 'instructions'), ('unexpected', 'field')])
def test_stored_alias_tampering_refuses(key, value):
    original, _ = fixture()
    stored = d.encode_evidence(original, SOURCE)
    stored['installed_charter_evidence']['reviewer_evidence'][key] = value
    with pytest.raises(ValueError):
        d.reconstruct_evidence(stored, SOURCE)


def test_changed_literal_target_and_reference_to_reference_refuse():
    original, _ = fixture()
    stored = d.encode_evidence(original, SOURCE)
    proof = stored['verified_events'][0]['linked_disposition']['originals']
    target = d._at(proof, d.CHARTER_PATH)
    target['scientific_context'] += ' changed'
    with pytest.raises(ValueError):
        d.reconstruct_evidence(stored, SOURCE)
    d._put(proof, d.CHARTER_PATH, deepcopy(stored['installed_charter_evidence']['reviewer_evidence']))
    with pytest.raises(ValueError):
        d.reconstruct_evidence(stored, SOURCE)


def test_nonmatching_or_absent_duplicate_stays_literal_with_full_reconstruction():
    original, _ = fixture()
    original['installed_charter_evidence']['reviewer_evidence']['new_science'] = 'Distinct literal remains.'
    stored = d.encode_evidence(original, SOURCE)
    assert stored['installed_charter_evidence'] == original['installed_charter_evidence']
    assert d.reconstruct_evidence(stored, SOURCE) == original
    proof = original['verified_events'][0]['linked_disposition']['originals']
    d._put(proof, d.CHARTER_PATH, {})
    assert d.reconstruct_evidence(d.encode_evidence(original, SOURCE), SOURCE) == original


def test_bad_original_evidence_binding_and_unversioned_disposition_refuse():
    original, _ = fixture()
    stored = d.encode_evidence(original, SOURCE)
    stored['disposition_presentation']['original_evidence_sha256'] = 'f'*64
    with pytest.raises(ValueError):
        d.reconstruct_evidence(stored, SOURCE)
    with pytest.raises(ValueError):
        d.reconstruct_evidence(original, SOURCE)
    core = {key:value for key,value in original['investigator_wake'].items() if key != 'identity'}
    core['schema'] = 'investigator-wake/v1'
    original['investigator_wake'] = {**core, 'identity': digest(core)}
    with pytest.raises(ValueError):
        d.encode_evidence(original, SOURCE)


def test_prefix_reconstruction_preserves_complete_negative_criticism_and_distinct_heads():
    value = packet()
    before = encoded(value)
    view = d.authority_view(value, SOURCE)
    ref = prefix(view)
    assert ref['schema'] == d.PREFIX_REFERENCE
    assert ref['event_count'] == 3
    assert ref['historical_head_sha256'] != ref['current_head_sha256']
    assert len(ref['event_identities']) == 3
    assert view['recorded_changes'] == value['recorded_changes']
    restored = d.reconstruct_authority(view, value, SOURCE)
    assert encoded(restored) == before and encoded(value) == before
    assert prefix(restored)['events'][-1]['payload']['verdict'] == 'REQUEST_CHANGES'


@pytest.mark.parametrize('key,value', [
    ('source', OLD_SOURCE), ('event_count', True), ('event_count', 2), ('event_count', 99),
    ('historical_head_sha256', 'f'*64), ('current_head_sha256', 'f'*64),
    ('request_identity', 'f'*64), ('request_sha256', 'f'*64),
    ('event_identities', ['f'*64]*3), ('original_state_sha256', 'f'*64),
    ('literal_location', 'operating_context.shared_policy'), ('trust', 'instructions'),
    ('unexpected', 'field')])
def test_prefix_alias_near_misses_refuse(key, value):
    value_original = packet()
    view = d.authority_view(value_original, SOURCE)
    prefix(view)[key] = value
    with pytest.raises(ValueError):
        d.reconstruct_authority(view, value_original, SOURCE)


def test_missing_alias_or_outer_literal_and_swapped_chain_refuse():
    original = packet()
    with pytest.raises(ValueError):
        d.reconstruct_authority(original, original, SOURCE)
    view = d.authority_view(original, SOURCE)
    del view['recorded_changes']
    with pytest.raises(ValueError):
        d.reconstruct_authority(view, original, SOURCE)
    view = d.authority_view(original, SOURCE)
    view['recorded_changes']['events'][0]['payload']['rationale'] = 'Changed'
    with pytest.raises(ValueError):
        d.reconstruct_authority(view, original, SOURCE)


def test_valid_same_request_fork_is_not_an_aliasable_prefix():
    historical, current = chain()
    historical['events'][-1]['payload']['rationale'] = 'A distinct valid original criticism.'
    last = historical['events'][-1]
    core = {key:value for key,value in last.items() if key != 'identity'}
    last['identity'] = hashlib.sha256(changes.encoded(core)).hexdigest()
    historical['head_sha256'] = hashlib.sha256(changes.encoded(last)+b'\n').hexdigest()
    d._chain(historical)
    d._chain(current)
    assert historical['request'] == current['request']
    with pytest.raises(ValueError):
        d.prefix_reference(historical, current, SOURCE)


def test_native_chain_hash_not_identity_label_is_required():
    historical, current = chain()
    current['events'][0]['payload']['rationale'] = 'Unhashed tampering'
    with pytest.raises(ValueError):
        d.prefix_reference(historical, current, SOURCE)
    historical, current = chain()
    historical['head_sha256'] = current['head_sha256']
    with pytest.raises(ValueError):
        d.prefix_reference(historical, current, SOURCE)


def test_legacy_authority_packet_never_receives_new_references():
    original = packet()
    original['reviewer_evidence']['input_evidence']['investigator_wake']['schema'] = 'investigator-wake/v1'
    assert d.authority_view(original, SOURCE) == original
    assert d.reconstruct_authority(original, original, SOURCE) == original
    original['trigger'] = 'installed-research-request'
    assert d.authority_view(original, SOURCE) == original


def test_actual_regenerate_uses_new_self_contained_view_and_never_touches_old_task(monkeypatch):
    monkeypatch.setattr('orchestrator.linked_disposition_input.enabled', lambda *args: False)
    original, _ = fixture()
    template = {'schema': wakes.TEMPLATE, 'template_id': 'synthetic', 'experiment': 'P002',
        'request': 'Consider the unchanged synthetic evidence.', 'references': [],
        'evidence_file': '/synthetic/evidence.json', 'evidence_sha256': 'e'*64,
        'change_request': {'request_id': 'f'*64, 'applied_event': '1'*64}}
    config = {'source': SOURCE, 'source_root': '/synthetic/source', 'controller_uid': 997, 'controller_gid': 987,
        'investigator': {'template': template, 'template_sha256': digest(template)}}
    core = {**{key:value for key,value in original['investigator_wake'].items() if key != 'identity'},
            'template_sha256': digest(template)}
    manifest = {**core, 'identity': digest(core)}
    monkeypatch.setattr('orchestrator.handover_runtime.configuration', lambda *a,**k: original['installed_charter_evidence'])
    monkeypatch.setattr('orchestrator.research_catalog.linked_change', lambda *a: {})
    linked = original['verified_events'][0]['linked_disposition']
    monkeypatch.setattr('orchestrator.disposition_successors.read_result', lambda *a: linked)
    def forbidden(*args, **kwargs):
        pytest.fail('No old blocked-task predecessor or model may be requested.')
    monkeypatch.setattr(wakes, '_task', forbidden)
    actual = wakes.regenerate(config, manifest, forbidden)
    assert actual['predecessors'] == []
    assert actual['evidence']['disposition_presentation']['schema'] == d.EVIDENCE
    restored = d.reconstruct_evidence(actual['evidence'], SOURCE)
    assert restored['installed_charter_evidence'] == original['installed_charter_evidence']
    assert restored['verified_events'] == original['verified_events']
