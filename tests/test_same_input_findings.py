"""Exact same-input quotation sharing; no model or scientific acceptance."""
from copy import deepcopy
import json

import pytest

from orchestrator import disposition_context as d

SHA = 'a' * 64
DRIVER = 'b' * 64
SOURCE = 'c' * 40
FINDINGS = ['Unresolved authority concern. ' * 30, 'Pending runtime condition. ' * 30]


def fixture():
    original = {'schema': 'independent-direction-and-driver-response/v1',
        'actual_verdict': 'REQUEST_CHANGES', 'applied_material_approval': False,
        'science_or_activation_approval': False, 'response_sha256': SHA,
        'source': SOURCE, 'session_id': 'actual-session', 'scope': 'bounded-direction',
        'distinct_condition': 'No installation; no retry.',
        'findings_and_responses': [
            {'number': i + 1, 'finding_verbatim': finding,
             'driver_response': 'Distinct response ' + str(i), 'driver_disposition': 'UNRESOLVED'}
            for i, finding in enumerate(FINDINGS)]}
    response = {'schema': 'selected-original-response/v1', 'original_raw_sha256': SHA,
        'value': {'session_id': 'actual-session', 'is_error': False,
            'structured_output': {'scope': 'bounded-direction', 'reviewed_commit': SOURCE,
                'verdict': 'REQUEST_CHANGES', 'findings': deepcopy(FINDINGS)}}}
    views = {SHA: response, DRIVER: {'schema': 'selected-original-response/v1',
        'original_raw_sha256': DRIVER, 'value': original}}
    event = {'event': 'REVIEW', 'identity': 'd' * 64, 'payload': {
        'verdict': 'REQUEST_CHANGES', 'rationale': 'Preserve negative judgment',
        'affected_results': ['no science accepted'], 'findings': deepcopy(FINDINGS),
        'original_review': {'response_sha256': SHA, 'session_id': 'actual-session',
            'scope': 'bounded-direction', 'source': SOURCE}}}
    return views, {'events': [event]}


def resolve(views, value):
    assert value['schema'] == d.RESPONSE_FIELD_REFERENCE
    target = views[value['response_original_raw_sha256']]
    for key in value['literal_path_in_selected_response']:
        target = target[key]
    assert d._sha(target) == value['value_sha256']
    return deepcopy(target)


def test_exact_originals_reconstructed_without_changing_negative_judgment():
    views, chain = fixture()
    before_views, before_chain = deepcopy(views), deepcopy(chain)
    d._share_direction_findings(views)
    d._share_review_event_findings(chain, views)
    assert views[SHA] == before_views[SHA]
    rows = views[DRIVER]['value']['findings_and_responses']
    assert all(isinstance(row['finding_verbatim'], dict) for row in rows)
    for row in rows:
        row['finding_verbatim'] = resolve(views, row['finding_verbatim'])
    chain['events'][0]['payload']['findings'] = resolve(views, chain['events'][0]['payload']['findings'])
    assert views == before_views
    assert chain == before_chain


@pytest.mark.parametrize('mutation', [
    'missing', 'archival', 'hash', 'session', 'source', 'scope', 'verdict',
    'error', 'findings_changed', 'findings_empty', 'findings_reference',
])
def test_missing_or_different_literal_target_keeps_every_quote(mutation):
    views, chain = fixture()
    selected = views[SHA]
    response = selected['value']
    output = response['structured_output']
    if mutation == 'missing': del views[SHA]
    elif mutation == 'archival': selected['schema'] = 'reviewed-historical-source-report-reference/v1'
    elif mutation == 'hash': selected['original_raw_sha256'] = 'e' * 64
    elif mutation == 'session': response['session_id'] = 'different-session'
    elif mutation == 'source': output['reviewed_commit'] = 'e' * 40
    elif mutation == 'scope': output['scope'] = 'different-scope'
    elif mutation == 'verdict': output['verdict'] = 'APPROVE'
    elif mutation == 'error': response['is_error'] = True
    elif mutation == 'findings_changed': output['findings'][0] += ' Changed.'
    elif mutation == 'findings_empty': output['findings'] = []
    elif mutation == 'findings_reference': output['findings'] = {'schema': 'elsewhere'}
    before = deepcopy((views, chain))
    d._share_direction_findings(views)
    d._share_review_event_findings(chain, views)
    assert (views, chain) == before


@pytest.mark.parametrize('mutation', ['extra_row', 'wrong_number', 'bool_number', 'changed_quote',
                                     'approval_claim', 'unknown_schema', 'missing_binding'])
def test_driver_ambiguity_stays_literal(mutation):
    views, chain = fixture()
    value = views[DRIVER]['value']
    if mutation == 'extra_row': value['findings_and_responses'].append({'number': 3})
    elif mutation == 'wrong_number': value['findings_and_responses'][0]['number'] = 2
    elif mutation == 'bool_number': value['findings_and_responses'][0]['number'] = True
    elif mutation == 'changed_quote': value['findings_and_responses'][0]['finding_verbatim'] += ' Changed.'
    elif mutation == 'approval_claim': value['applied_material_approval'] = True
    elif mutation == 'unknown_schema': value['schema'] = 'unknown/v1'
    elif mutation == 'missing_binding':
        value.pop('scope')
        views[SHA]['value']['structured_output'].pop('scope')
    before = deepcopy(views)
    d._share_direction_findings(views)
    assert views == before


def test_unlinked_or_nonreview_event_is_not_selected_by_text_similarity():
    views, chain = fixture()
    for kind in ['DISPOSITION', 'AUTHORIZED', 'APPLIED']:
        event = deepcopy(chain['events'][0])
        event['event'] = kind
        chain['events'].append(event)
    chain['events'][0]['payload'].pop('original_review')
    before = deepcopy(chain)
    d._share_review_event_findings(chain, views)
    assert chain == before
