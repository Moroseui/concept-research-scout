"""Exact reviewed condition display; no model, approval or scientific result."""
from copy import deepcopy
import hashlib

import pytest

from orchestrator import change_requests as changes, reviewed_history as history
from orchestrator import scientific_evidence_access as access
from orchestrator import current_scientific_input as current, terminal_review
from test_current_scientific_state import build, agent_append
from test_selected_scientific_history import captured, write_state
from test_current_input_integration import current_packet
from test_linked_input_integration import integrated
from test_campaign_grounding_presentation import example
from test_disposition_context import SOURCE


def selection(raw, end=None):
    end = end or raw.index(b'```terminal-review-verdict')
    return {'schema': history.RESOLUTION_CONDITIONS,
        'scope': 'source-review-narrative-only',
        'qualification': 'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION',
        'sections': [{'start_utf8': 0, 'end_utf8': end,
                      'sha256': hashlib.sha256(raw[:end]).hexdigest()}]}


def prepared(e, tmp_path, *, wrong_target=False):
    capture, state, old_app, closed, resolution = build(e, tmp_path)
    descriptor = resolution['payload']['review_evidence']['report']
    raw = capture['payloads'][descriptor['sha256']]
    plan = deepcopy(old_app['payload']['result_binding']['current_state_settlement'])
    plan['resolution_presentations'] = {
        '0'*64 if wrong_target else descriptor['sha256']: selection(raw)}
    app = agent_append(state, 'APPLIED', {
        'modification': 'Synthetic exact condition presentation pending review.',
        'checks': ['Synthetic fixture, no execution.'], 'review_status': 'PENDING',
        'result_binding': {'source': SOURCE, 'current_state_settlement': plan},
        'supersedes_applied_events': [old_app['identity']]})
    store = tmp_path/'store-1-None'
    write_state(store, state)
    capture = access.capture_changes(store, [state['request']['identity']],
                                    source=SOURCE, task_binding='d'*64)
    return capture, state, app, resolution, descriptor, raw


def test_full_statement_conditions_and_original_retrieval_are_preserved(captured,tmp_path):
    cap,state,app,resolution,descriptor,raw = prepared(captured,tmp_path)
    before=deepcopy(cap);request=state['request']['identity']
    view=history.current_state_view(cap,request,app['identity'],source=SOURCE)
    entry=view['resolution_condition_views'][descriptor['sha256']]
    shown=entry['presentation']
    assert shown['original_statement']==terminal_review._statement(raw)
    assert 'H2 is not accepted.' in str(shown)
    assert 'conditional-activation' in str(shown)
    assert shown['verbatim_scope_conditions'][0]['text']==raw[:raw.index(b'```')].decode()
    assert view['literal_resolution_reports'][resolution['identity']][
        'same_bound_original_reports'][descriptor['sha256']]==history.resolution_condition_reference(shown)
    assert raw.decode() not in str(view)
    assert 'Unresolved extra condition.' in str(view)
    assert 'Unreviewed tail: do not execute.' in str(view)
    assert 'Latest criticism remains unresolved.' in str(view)
    for name in shown['authenticated_reader_names']:
        row=next(row for row in cap['manifest']['records'] if row['name']==name)
        assert cap['payloads'][row['sha256']]==raw
    assert cap==before
    assert app['payload']['review_status']=='PENDING'
    assert history.validate_current_state_view(view,cap,request,app['identity'],source=SOURCE)==view


def test_unlinked_or_unresolved_report_cannot_be_selected(captured,tmp_path):
    cap,state,app,_,_,_=prepared(captured,tmp_path,wrong_target=True)
    with pytest.raises(ValueError,match='REVIEWED_HISTORY_BINDING_CHANGED'):
        history.current_state_view(cap,state['request']['identity'],app['identity'],source=SOURCE)


@pytest.mark.parametrize('fault',['hash','missing_body','edited_presentation','edited_selector',
                                 'edited_reader','drop_findings'])
def test_saved_condition_view_is_recomputed_from_native_originals(captured,tmp_path,fault):
    cap,state,app,_,descriptor,_=prepared(captured,tmp_path)
    request=state['request']['identity']
    view=history.current_state_view(cap,request,app['identity'],source=SOURCE)
    row=view['resolution_condition_views'][descriptor['sha256']]
    if fault=='hash':cap['payloads'][descriptor['sha256']]+=b'changed'
    elif fault=='missing_body':del cap['payloads'][descriptor['sha256']]
    elif fault=='edited_presentation':row['presentation']['notice']='invented approval'
    elif fault=='edited_selector':row['selection']['sections'][0]['end_utf8']+=1
    elif fault=='edited_reader':row['reader_names']=['change/'+'a'*64+'/evidence/other.md']
    else:row['presentation']['original_statement']['findings']={}
    with pytest.raises(ValueError):
        history.validate_current_state_view(view,cap,request,app['identity'],source=SOURCE)


@pytest.mark.parametrize('fault',['wrong_scope','self_approval','empty','out_of_bounds',
                                 'overlap','boolean_offset','wrong_section_hash','utf8_split',
                                 'rejection','in_progress','unknown_schema','unknown_field',
                                 'missing_reader','unsafe_reader'])
def test_invalid_selections_and_nonapprovals_refuse(captured,tmp_path,fault):
    cap,_,_,_,descriptor,raw=prepared(captured,tmp_path)
    body='é scope condition\n'+raw.decode()
    raw=body.encode();plan=selection(raw)
    names=['change/'+'a'*64+'/evidence/original.md']
    if fault=='wrong_scope':plan['scope']='all-science'
    elif fault=='self_approval':plan['qualification']='APPROVED_BY_PROJECTION'
    elif fault=='empty':plan['sections']=[]
    elif fault=='out_of_bounds':plan['sections'][0]['end_utf8']=len(raw)+1
    elif fault=='overlap':plan['sections']*=2
    elif fault=='boolean_offset':plan['sections'][0]['start_utf8']=False
    elif fault=='wrong_section_hash':plan['sections'][0]['sha256']='0'*64
    elif fault=='utf8_split':
        plan['sections']=[{'start_utf8':1,'end_utf8':2,'sha256':hashlib.sha256(raw[1:2]).hexdigest()}]
    elif fault=='rejection':body=body.replace('APPROVE','REQUEST_CHANGES')
    elif fault=='in_progress':body=body.replace('APPROVE','IN_PROGRESS')
    elif fault=='unknown_schema':plan['schema']='unknown'
    elif fault=='unknown_field':plan['driver_summary']='No problems'
    elif fault=='missing_reader':names=[]
    else:names=['/etc/private-file']
    with pytest.raises(ValueError):history.resolution_conditions(body,plan,names)


def test_actual_display_has_one_condition_floor_without_mutating_saved_originals(current_packet,tmp_path):
    cap,state,app,_,descriptor,raw=prepared(current_packet,tmp_path)
    request=state['request']['identity']
    native=history.current_state_view(cap,request,app['identity'],source=SOURCE)
    packet=deepcopy(current_packet.current_packet)
    packet['scientific_change_history']['current_requests']={request:native}
    before=deepcopy(packet)
    shown=current.presentation(packet,SOURCE)
    conditions=shown['scientific_change_history']['literal_response_originals'][descriptor['sha256']]
    assert conditions['original_statement']==terminal_review._statement(raw)
    row=shown['scientific_change_history']['current_requests'][request]
    assert row['resolution_condition_views'][descriptor['sha256']]['schema']=='same-prompt-current-literal/v1'
    assert packet==before
    native['resolution_condition_views'][descriptor['sha256']]['presentation']['original_statement']['findings']={}
    packet['scientific_change_history']['current_requests']={request:native}
    with pytest.raises(ValueError,match='CURRENT_INPUT_RESOLUTION_CONDITIONS_CHANGED'):
        current.presentation(packet,SOURCE)


def test_narrative_growth_is_retrievable_while_new_condition_growth_stays_literal(captured,tmp_path):
    _,_,_,_,_,original=prepared(captured,tmp_path)
    names=['change/'+'a'*64+'/evidence/original.md']
    sizes=[]
    for count in (1,10,100):
        # Synthetic narrative growth only. The exact selection still requires
        # independent review; this is not evidence of real task sufficiency.
        raw=original+b'\nHistorical source inspection narrative.\n'*count
        view=history.resolution_conditions(raw.decode(),selection(raw),names)
        sizes.append(len(changes.encoded(view)))
    assert max(sizes)-min(sizes)<10
    expanded=original.replace(b'H2 is not accepted.',b'H2 is not accepted. '+b'Open condition. '*100)
    view=history.resolution_conditions(expanded.decode(),selection(expanded),names)
    assert len(changes.encoded(view))>sizes[0]+1000
