"""Pinned evidence retrieval, not integration/approval of compact wake inputs."""
from copy import deepcopy
import hashlib

import pytest

from orchestrator import disposition_successors as d, git_publication
from orchestrator.hosted_cycle import encoded
from test_disposition_context import chain


def original():
    _, history = chain()
    proof = {'schema': 'disposition-successor-original-proof/v1',
        'origin_task': 'c' * 64, 'origin_source': 'b' * 40,
        'packet': {'scientific_conditions': 'Preserve the proposed cohort and all limitations.'},
        'protected_original': {'stages': {
            'continuation': {'answer': 'Original discussion; no accepted measurements.'},
            'review': {'answer': 'REQUEST_CHANGES: missing paired observations.'}}}}
    result = {'schema': 'linked-disposition-result/v1', 'status': 'DISPOSITION_RECORDED',
        'original_task_status': 'BLOCKED', 'acceptance_status': 'APPROVED_PROPOSAL_ONLY',
        'new_scientific_authority': False, 'scientific_execution': False, 'automatic_retry': False,
        'origin_task': proof['origin_task'], 'origin_source': proof['origin_source'],
        'source': 'a' * 40, 'request': 'd' * 64,
        'original_proof_sha256': hashlib.sha256(encoded(proof)).hexdigest(),
        'answer': 'Retain criticism. This result does not adopt or execute a successor.'}
    return {'result': result, 'result_sha256': hashlib.sha256(encoded(result)).hexdigest(),
        'originals': proof, 'reviewed_repair': history, 'scope': 'Evidence only, no acceptance.'}


def test_exact_read_preserves_every_original_and_criticism(monkeypatch):
    value = original(); before = encoded(value); ref = d.result_reference(value); calls = []
    client = object(); config = object()
    def read(c, task, broker):
        assert c is config and broker is client and task == value['originals']['origin_task']
        calls.append(task)
        return deepcopy(value)
    monkeypatch.setattr(d, 'read_result', read)
    assert d.read_result_reference(config, ref, client) == value
    assert d.read_result_reference(config, ref, client) == value
    assert encoded(value) == before and len(calls) == 2
    assert 'REQUEST_CHANGES' in str(value['originals'])
    assert len(encoded(ref)) < 1600


@pytest.mark.parametrize('field', [
    'origin_task', 'origin_source', 'disposition_source', 'disposition_request',
    'result_sha256', 'original_proof_sha256', 'repair_request', 'repair_head_sha256',
    'repair_event_count', 'repair_value_sha256', 'original_value_sha256'])
def test_changed_pin_refuses_instead_of_substituting_new_original(monkeypatch, field):
    value = original(); ref = d.result_reference(value)
    ref[field] = ref[field] + 1 if field == 'repair_event_count' else 'f' * len(ref[field])
    monkeypatch.setattr(d, 'read_result', lambda *args: deepcopy(value))
    with pytest.raises(ValueError, match='REFERENCE_CHANGED'):
        d.read_result_reference({}, ref, None)


@pytest.mark.parametrize('bad', [None, {}, {'path': '/tmp/untrusted-proof.json'},
    {'schema': d.LINKED_REFERENCE, 'origin_task': 'c' * 64}])
def test_descriptor_cannot_supply_a_path_or_omit_bindings(monkeypatch, bad):
    def never(*args): raise AssertionError('Malformed descriptor must fail before native read.')
    monkeypatch.setattr(d, 'read_result', never)
    with pytest.raises(ValueError, match='REFERENCE_REQUIRED'):
        d.read_result_reference({}, bad, None)


@pytest.mark.parametrize('count', [True, False, 0, -1, '4'])
def test_invalid_count_fails_before_retrieval(monkeypatch, count):
    ref = d.result_reference(original()); ref['repair_event_count'] = count
    monkeypatch.setattr(d, 'read_result', lambda *args: pytest.fail('Unexpected retrieval'))
    with pytest.raises(ValueError, match='REFERENCE_REQUIRED'):
        d.read_result_reference({}, ref, None)


def test_changed_scientific_body_refuses_even_with_same_result_identifier(monkeypatch):
    value = original(); ref = d.result_reference(value)
    value['originals']['protected_original']['stages']['review']['answer'] = 'APPROVE'
    monkeypatch.setattr(d, 'read_result', lambda *args: value)
    with pytest.raises(ValueError, match='ORIGINAL_CHANGED'):
        d.read_result_reference({}, ref, None)


def test_missing_original_native_refusal_propagates(monkeypatch):
    ref = d.result_reference(original())
    def missing(*args): raise ValueError('DISPOSITION_PROTECTED_ORIGINAL_CHANGED')
    monkeypatch.setattr(d, 'read_result', missing)
    with pytest.raises(ValueError, match='DISPOSITION_PROTECTED_ORIGINAL_CHANGED'):
        d.read_result_reference({}, ref, None)


def test_later_live_history_is_not_used_as_saved_repair(monkeypatch):
    value = original(); ref = d.result_reference(value)
    unrelated_live_history = deepcopy(value['reviewed_repair'])
    unrelated_live_history['events'].append({'invalid_later_live_event': True})
    monkeypatch.setattr(d, 'read_result', lambda *args: deepcopy(value))
    assert d.read_result_reference({'live_history': unrelated_live_history}, ref, None) == value


@pytest.mark.parametrize('field,bad', [('new_scientific_authority', True),
    ('scientific_execution', True), ('automatic_retry', True),
    ('acceptance_status', 'ADOPTED'), ('original_task_status', 'COMPLETE')])
def test_reference_cannot_relabel_evidence_as_authority(field, bad):
    value = original(); value['result'][field] = bad
    with pytest.raises(ValueError, match='ORIGINAL_CHANGED'): d.result_reference(value)


def test_scans_full_original_not_only_descriptor_and_preserves_refusal(monkeypatch):
    value = original(); ref = d.result_reference(value); scanned = []
    monkeypatch.setattr(d, 'read_result', lambda *args: deepcopy(value))
    def reject(name, body):
        scanned.append((name, body))
        raise ValueError('SYNTHETIC_ORIGINAL_SCAN_REFUSAL')
    monkeypatch.setattr(git_publication, 'scan', reject)
    with pytest.raises(ValueError, match='SYNTHETIC_ORIGINAL_SCAN_REFUSAL'):
        d.read_result_reference({}, ref, None)
    assert scanned == [('linked-disposition-original.json', encoded(value))]


def test_changed_history_link_fails_even_when_descriptor_hash_could_be_remade():
    value = original(); value['reviewed_repair']['events'][1]['previous_sha256'] = 'f' * 64
    with pytest.raises(ValueError): d.result_reference(value)
