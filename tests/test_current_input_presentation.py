
from copy import deepcopy
import hashlib
import pytest
from orchestrator import current_scientific_input as current, disposition_context as dc
from orchestrator import reviewed_history as history, change_requests as changes
from test_current_input_integration import current_packet
from test_linked_input_integration import integrated
from test_campaign_grounding_presentation import example
from test_selected_scientific_history import captured
from test_current_scientific_state import build
from test_disposition_context import SOURCE


def shared_science(e):
    packet=deepcopy(e.current_packet)
    evidence=packet['reviewer_evidence']['input_evidence']
    science=evidence['verified_events'][0]['linked_disposition']['originals']['scientific_input_context']
    evidence['installed_charter_evidence']={'reviewer_evidence':deepcopy(science)}
    return packet


def test_identical_science_has_one_exact_literal_and_original_stays_whole(current_packet):
    packet=shared_science(current_packet);original=deepcopy(packet)
    view=dc.selected_packet_view(packet,SOURCE)
    evidence=view['reviewer_evidence']['input_evidence']
    ref=evidence['verified_events'][0]['linked_disposition']['originals']['scientific_input_context']
    assert ref['schema']=='same-prompt-current-literal/v1'
    target=view
    for key in ref['literal_path_in_task_state']:target=target[key]
    assert ref['value_sha256']==hashlib.sha256(changes.encoded(target)).hexdigest()
    assert packet==original
    dc.validate_selected_packet_view(view,packet,SOURCE)


@pytest.mark.parametrize('fault',['target','reference','drop_literal'])
def test_changed_display_or_target_is_not_original(current_packet,fault):
    packet=shared_science(current_packet);view=dc.selected_packet_view(packet,SOURCE)
    evidence=view['reviewer_evidence']['input_evidence']
    if fault=='target':evidence['installed_charter_evidence']['reviewer_evidence']['new']='changed'
    elif fault=='reference':evidence['verified_events'][0]['linked_disposition']['originals']['scientific_input_context']['value_sha256']='0'*64
    else:del evidence['installed_charter_evidence']['reviewer_evidence']
    with pytest.raises(ValueError):dc.validate_selected_packet_view(view,packet,SOURCE)


def test_different_science_remains_two_complete_literals(current_packet):
    packet=shared_science(current_packet)
    evidence=packet['reviewer_evidence']['input_evidence']
    evidence['installed_charter_evidence']['reviewer_evidence']['later_evidence']='Must remain distinct.'
    view=dc.selected_packet_view(packet,SOURCE)
    assert view['reviewer_evidence']==packet['reviewer_evidence']


def test_no_selection_leaves_full_native_current_history(current_packet):
    packet=shared_science(current_packet);view=dc.selected_packet_view(packet,SOURCE)
    assert view['scientific_change_history']['current_requests']==packet['scientific_change_history']['current_requests']


def test_existing_typed_renderer_and_report_sharing_preserve_tail_and_conditions(current_packet,tmp_path):
    e=current_packet
    cap,state,app,closed,resolution=build(e,tmp_path,extra_resolution='bound')
    projected=history.current_state_view(cap,state['request']['identity'],app['identity'],source=SOURCE)
    packet=shared_science(e)
    # Display fixture combines independently native-checked projections. It is
    # not a registered task or a substitute for native admission authentication.
    identity=state['request']['identity']
    packet['scientific_change_history']['current_requests']={identity:projected}
    original=deepcopy(packet)
    view=current.presentation(packet,SOURCE)
    shown=view['scientific_change_history']['current_requests'][identity]
    count=projected['reviewed_boundary']['event_count']
    for before in projected['events']:
        after=next(row for row in shown['events'] if row['identity']==before['identity'])
        if before['sequence']>count:assert after==before
        assert after['actor']==before['actor']
    assert 'Unresolved extra condition.' in str(shown)
    assert 'Unreviewed tail: do not execute.' in str(shown)
    literals=view['scientific_change_history']['literal_response_originals']
    for sha,ref in shown['literal_resolution_reports'][resolution['identity']]['same_bound_original_reports'].items():
        assert hashlib.sha256(literals[sha].encode()).hexdigest()==sha
        assert 'conditional-activation' in literals[sha]
        assert ref['literal_path_in_task_state'][-1]==sha
    assert packet==original


@pytest.mark.parametrize('same',[True,False])
def test_native_result_wrapper_only_shares_a_proven_duplicate(current_packet,same):
    import json
    packet=shared_science(current_packet)
    judgment={'verdict':'REQUEST_CHANGES','findings':['This criticism must remain.']}
    raw=json.dumps({'type':'result','structured_output':judgment,
        'result':json.dumps(judgment if same else {'findings':['Distinct text remains.']}),
        'session_id':'synthetic-independent-review','is_error':False,'subtype':'success',
        'modelUsage':{'synthetic-model':{'input_tokens':12}},'usage':{'input_tokens':12}})
    sha=hashlib.sha256(raw.encode()).hexdigest()
    packet['scientific_change_history']['literal_response_originals'][sha]=raw
    view=current.presentation(packet,SOURCE)
    body=view['scientific_change_history']['literal_response_originals'][sha]
    assert body['value']['structured_output']==judgment
    assert ('result' not in body['value'])==same
    assert body['value']['session_id']=='synthetic-independent-review'
    assert packet['scientific_change_history']['literal_response_originals'][sha]==raw
    if not same:assert 'Distinct text remains.' in body['value']['result']


def test_unknown_response_shape_stays_exact_literal(current_packet):
    packet=shared_science(current_packet);raw='{"schema":"unknown","condition":"Do not execute."}'
    sha=hashlib.sha256(raw.encode()).hexdigest()
    packet['scientific_change_history']['literal_response_originals'][sha]=raw
    view=current.presentation(packet,SOURCE)
    assert view['scientific_change_history']['literal_response_originals'][sha]==raw
