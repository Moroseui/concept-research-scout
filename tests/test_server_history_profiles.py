"""Both existing review routes retain exact originals and strict approval bindings."""
from copy import deepcopy
import pytest
from orchestrator import reviewed_history as history, terminal_review as terminal
from orchestrator.server_terminal_review import PROFILE as SERVER
from test_current_scientific_state import build
from test_resolution_conditions import selection
from test_selected_scientific_history import captured
from test_campaign_grounding_presentation import example
from test_disposition_context import SOURCE


@pytest.mark.parametrize('profile', [terminal.PROFILE, SERVER])
def test_native_current_view_and_conditions_accept_both_approved_profiles(captured, tmp_path, profile):
    cap, state, app, closed, review = build(captured, tmp_path, profile=profile)
    before = deepcopy(cap)
    view = history.current_state_view(cap, state['request']['identity'], app['identity'], source=SOURCE)
    assert closed[0]['identity'] not in {e['identity'] for e in view['events']}
    assert 'Latest criticism remains unresolved.' in str(view)
    assert 'Unreviewed tail: do not execute.' in str(view)
    assert app['payload']['review_status'] == 'PENDING'
    descriptor = review['payload']['review_evidence']['report']
    raw = cap['payloads'][descriptor['sha256']]
    names = sorted(row['name'] for row in cap['manifest']['records'] if row['sha256'] == descriptor['sha256'])
    shown = history.resolution_conditions(raw.decode(), selection(raw), names)
    assert shown['original_statement'] == terminal._statement(raw, profile=profile)
    assert 'H2 is not accepted.' in str(shown)
    assert cap == before
    assert history.validate_current_state_view(view, cap, state['request']['identity'], app['identity'], source=SOURCE) == view


@pytest.mark.parametrize('profile', [terminal.PROFILE, SERVER])
@pytest.mark.parametrize('fault', ['rejection', 'in_progress', 'schema', 'scope', 'findings', 'gates', 'ambiguous'])
def test_both_profiles_keep_strict_final_approval_contract(captured, tmp_path, profile, fault):
    cap, _, _, _, review = build(captured, tmp_path, profile=profile)
    raw = cap['payloads'][review['payload']['review_evidence']['report']['sha256']]
    if fault == 'rejection': raw = raw.replace(b'APPROVE', b'REQUEST_CHANGES')
    elif fault == 'in_progress': raw = raw.replace(b'APPROVE', b'IN_PROGRESS')
    elif fault == 'schema': raw = raw.replace(profile.encode(), b'unknown-review/v1')
    elif fault == 'scope': raw = raw.replace(b'material-source-integration', b'scientific-acceptance')
    elif fault == 'findings': raw = raw.replace(b'"resolved"', b'"preserve"')
    elif fault == 'gates': raw = raw.replace(b'conditional-activation', b'waived-activation')
    else: raw += raw
    with pytest.raises(ValueError): history._source_review_statement(raw)


@pytest.mark.parametrize('fault', ['missing_original', 'changed_original', 'wrong_source', 'wrong_proposal', 'missing_source', 'missing_proposal'])
def test_server_profile_does_not_relax_authenticated_resolution_binding(captured, tmp_path, fault):
    metadata = {'source': SOURCE, 'proposal_sha256': 'a'*64}
    if fault == 'wrong_source': metadata['source'] = '0'*40
    elif fault == 'wrong_proposal': metadata['proposal_sha256'] = '0'*64
    elif fault == 'missing_source': del metadata['source']
    elif fault == 'missing_proposal': del metadata['proposal_sha256']
    cap, state, app, _, review = build(captured, tmp_path, profile=SERVER, resolution_metadata=metadata)
    request = state['request']['identity']
    desc = review['payload']['review_evidence']['report']
    if fault == 'missing_original': del cap['payloads'][desc['sha256']]
    elif fault == 'changed_original': cap['payloads'][desc['sha256']] += b'changed'
    expected = {'missing_original': 'SCIENTIFIC_EVIDENCE_COMPLETE_PAYLOAD_SET_REQUIRED',
                'changed_original': 'SCIENTIFIC_EVIDENCE_PAYLOAD_CHANGED'}.get(fault, 'REVIEWED_HISTORY_BINDING_CHANGED')
    with pytest.raises(ValueError, match=expected):
        history.current_state_view(cap, request, app['identity'], source=SOURCE)
