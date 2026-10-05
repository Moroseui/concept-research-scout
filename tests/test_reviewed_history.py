"""Approved-prefix commitment, retained criticism and native capture failures."""
from copy import deepcopy
import hashlib
from pathlib import Path

import pytest
from orchestrator import reviewed_history as r, disposition_context as d
from orchestrator.hosted_cycle import encoded
from test_selected_scientific_history import captured, append, write_state
from test_campaign_grounding_presentation import example
from test_disposition_context import SOURCE


@pytest.fixture
def prepared(captured):
    e = captured
    state = deepcopy(e.current_chain)
    bound = r.boundary(state)
    previous = e.latest
    app = append(state, 'APPLIED', {'modification': 'Reviewed prefix input repair.',
        'checks': ['Focused integration'], 'review_status': 'PENDING',
        'result_binding': {'source': SOURCE, 'reviewed_history_prefix': bound},
        'supersedes_applied_events': [previous]})
    write_state(Path(e.config['change_request_store']), state)
    original = deepcopy(e.authority)
    original.pop('scientific_change_history')
    original['recorded_changes'] = state
    original['reviewer_evidence']['catalog_core']['change_request']['applied_event'] = app['identity']
    e.input = original; e.successor = app; e.bound = bound
    e.compact = d.capture_current_history(e.config, original)
    return e


def test_native_capture_keeps_all_criticism_and_originals(prepared):
    e = prepared; packet = e.compact
    state = packet['recorded_changes']
    assert state['schema'] == r.SCHEMA
    assert r.validate(state) == [x['identity'] for x in e.input['recorded_changes']['events']]
    assert d.validate_current_history(packet, SOURCE)[state['request']['identity']] == state
    assert packet['scientific_change_history']['response_originals'][e.response_sha].encode() == e.raw_response
    literal = {x['identity']: x for x in state['events']}
    for event in e.input['recorded_changes']['events']:
        if event['event'] != 'APPLIED':
            assert literal[event['identity']] == event
    assert e.intermediate not in literal
    assert e.old_active in literal  # needed by the supplied historical proof
    assert len(encoded(packet)) < len(encoded(e.input))
    view = d.selected_packet_view(packet, SOURCE)
    d.validate_selected_packet_view(view, packet, SOURCE)
    assert 'Complete external criticism.' in str(view)


@pytest.mark.parametrize('mutation', ['boundary_head','index_hash','payload','request','tail_link','drop_criticism','drop_application','wrong_source'])
def test_corrupted_commitments_and_protected_material_fail(prepared, mutation):
    value = deepcopy(prepared.compact); state = value['recorded_changes']
    if mutation == 'boundary_head': state['boundary']['head_sha256'] = '0'*64
    elif mutation == 'index_hash': state['prefix_index'][1]['payload_sha256'] = '0'*64
    elif mutation == 'payload': state['events'][0]['payload']['rationale'] += 'changed'
    elif mutation == 'request': state['request']['requested_change'] += 'changed'
    elif mutation == 'tail_link': state['events'][-1]['previous_sha256'] = '0'*64
    elif mutation == 'drop_criticism': state['events'] = [x for x in state['events'] if x['event'] != 'REVIEW']
    elif mutation == 'drop_application': state['events'] = state['events'][:-1]
    elif mutation == 'wrong_source': value['reviewer_evidence']['catalog_core']['source'] = '0'*40
    with pytest.raises(ValueError): d.validate_current_history(value, SOURCE)


@pytest.mark.parametrize('change', ['missing','altered'])
def test_controller_retrieval_checks_actual_report_before_capture(prepared, change):
    e = prepared; state = e.input['recorded_changes']
    ref = next(x for x in d._literal_descriptors(state) if x['descriptor']['sha256'] == e.response_sha)
    path = Path(e.config['change_request_store']) / ref['request'] / ref['descriptor']['artifact']
    if change == 'missing': path.unlink()
    else: path.write_bytes(b'altered original')
    with pytest.raises((ValueError, FileNotFoundError)): d.capture_current_history(e.config, e.input)


def test_superseded_binding_is_not_a_valid_prefix_authority(prepared):
    e = prepared; state = deepcopy(e.input['recorded_changes'])
    append(state, 'APPLIED', {'modification':'Later application', 'checks':['Synthetic'],
        'result_binding':{'source':SOURCE}, 'review_status':'PENDING',
        'supersedes_applied_events':[e.successor['identity']]})
    with pytest.raises(ValueError): r.capture(state, e.successor['identity'])


def test_all_unreviewed_tail_stays_literal_and_index_growth_is_explicit(prepared):
    e = prepared; state = deepcopy(e.input['recorded_changes'])
    for i in range(50):
        append(state, 'DISPOSITION', {'rationale':f'Unreviewed observation {i}.', 'affected_results':['Synthetic']})
    result = r.capture(state, e.successor['identity'])
    assert result['events'][-50:] == state['events'][-50:]
    assert len(r.index(result)) == len(state['events'])
    assert len(encoded(result)) > len(encoded(e.compact['recorded_changes']))


def test_wrong_prefix_and_missing_tail_refuse(prepared):
    state = deepcopy(prepared.compact['recorded_changes'])
    state['events'][-1]['sequence'] += 1
    with pytest.raises(ValueError): r.validate(state)
    wrong = deepcopy(prepared.input['recorded_changes'])
    wrong['events'][1]['payload']['modification'] = 'changed'
    with pytest.raises(ValueError): r.boundary(wrong)


def test_administrative_label_cannot_hide_criticism_or_conditions():
    for value in ['REQUEST_CHANGES: source remains blocked',
            {'finding':'unresolved', 'sha256':'a'*64},
            [{'artifact':'evidence/example', 'sha256':'a'*64, 'remaining':'human stop'}],
            ['Do not retry the failed attempt.']]:
        assert not r._referenceable_metadata(value)
    assert r._referenceable_metadata({'artifact':'evidence/example', 'sha256':'a'*64,'size':42})


def test_display_keeps_every_payload_value_except_typed_metadata(prepared):
    e=prepared; state=e.compact['recorded_changes']; view=r.presentation(state)
    original={row['identity']:row for row in state['events']}
    from orchestrator.disposition_context import _selected_event
    for shown in view['events']:
        expected=_selected_event(original[shown['identity']])
        omitted=shown.get('historical_administrative_fields',[])
        assert all(r._referenceable_metadata(expected['payload'][key]) for key in omitted)
        assert shown['payload']=={k:v for k,v in expected['payload'].items() if k not in omitted}
    assert len(view['referenced_applications'])==len(state['prefix_index'])-sum(row['sequence']<=state['boundary']['event_count'] for row in state['events'])


@pytest.fixture(params=['operator-terminal-review/v1', 'server-terminal-review/v1'])
def report_selection(captured, request):
    import json
    from orchestrator import terminal_review as terminal
    e=captured; state=deepcopy(e.current_chain)
    findings={name:{'disposition':'preserve','reason':'Synthetic remaining condition.'} for name in terminal.FINDINGS}
    findings['C006']['disposition']=findings['C007']['disposition']='resolved'
    statement={'schema':request.param,'source':SOURCE,'proposal_sha256':'a'*64,
        'manifest_sha256':'b'*64,'session_id':'synthetic-review-session','scope':'material-source-integration',
        'verdict':'APPROVE','inspected':['Synthetic source fixture.'],'unavailable':[],
        'unverified':['Synthetic H2 remains pending.'],'findings':findings,
        'resolution_of':terminal.BASE_SOURCE,'remaining_gates':['held-deployment','accounting-halt',
            'retained-history-audit','conditional-activation','scientific-acceptance']}
    raw=('Final source/integration verdict: APPROVE\n```terminal-review-verdict\n'+json.dumps(statement)+'\n```\n').encode()
    sha=hashlib.sha256(raw).hexdigest();descriptor={'artifact':'evidence/'+sha+'-synthetic-resolution.md','sha256':sha,'size':len(raw)}
    approval=append(state,'REVIEW',{'applied_event':e.latest,'verdict':'APPROVE',
        'rationale':'Synthetic source-only provenance, not the new selection approval.',
        'review_evidence':{'report':descriptor},'source':SOURCE,'proposal_sha256':'a'*64})
    plan={'schema':'reviewed-prefix-report-selection/v1','references':{e.response_sha:'Synthetic proposed source-only reconciliation; all later conditions retained.'},
        'resolution_event':approval['identity'],'resolution_original':descriptor,'resolution_text':raw.decode(),
        'scope':'historical-source-findings-only','qualification':'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION'}
    app=append(state,'APPLIED',{'modification':'Synthetic pending report selection.','checks':['Synthetic'],
        'result_binding':{'source':SOURCE,'reviewed_history_prefix':r.boundary(state),
            'historical_report_selection':plan},'review_status':'PENDING','supersedes_applied_events':[e.latest]})
    e.report_state=r.capture(state,app['identity']);e.report_refs=d._literal_descriptors(state)
    e.report_originals={e.response_sha:e.raw_response.decode()};e.report_plan=plan
    return e


def test_report_selection_preserves_originals_and_carries_conditions(report_selection):
    e=report_selection;before=deepcopy(e.report_originals)
    views=d._response_presentations(e.report_originals)
    result=r.report_views(e.report_state,e.report_originals,views,e.report_refs)
    assert e.report_originals==before
    assert result[e.response_sha]['schema']=='reviewed-historical-source-report-reference/v1'
    assert 'not newly' in result[e.response_sha]['notice']
    assert 'Synthetic H2 remains pending.' in e.report_plan['resolution_text']
    assert e.report_state['events'][-1]['payload']['review_status']=='PENDING'


@pytest.mark.parametrize('fault',['missing_body','changed_resolution','unknown_reference','wrong_scope','unreviewed_tail'])
def test_report_selection_must_not_hide_unbound_or_unreviewed_material(report_selection,fault):
    e=report_selection;state=deepcopy(e.report_state);originals=deepcopy(e.report_originals)
    if fault=='missing_body': originals.clear()
    elif fault=='changed_resolution': state['events'][-1]['payload']['result_binding']['historical_report_selection']['resolution_text']+='changed'
    elif fault=='unknown_reference': state['events'][-1]['payload']['result_binding']['historical_report_selection']['references']['0'*64]='Unknown reference must refuse.'
    elif fault=='wrong_scope': state['events'][-1]['payload']['result_binding']['historical_report_selection']['scope']='all-authority'
    else:
        # An additional adverse reference after the boundary remains fully literal
        # even if its body duplicates a historical report. Ambiguous bindings refuse.
        e.report_refs=deepcopy(e.report_refs)
        e.report_refs[0]['event']=state['events'][-1]['identity']
    with pytest.raises(ValueError):r.report_views(state,originals,d._response_presentations(e.report_originals),e.report_refs)


def test_nested_metadata_maps_do_not_hide_narratives_or_unreviewed_events():
    descriptor={'artifact':'evidence/example','sha256':'a'*64,'size':42}
    assert r._referenceable_metadata({'report':descriptor,'nested':{'receipt':descriptor}})
    assert r._referenceable_metadata({'protocol_sha256':'a'*64,'source_sha1':'b'*40})
    for value in [
        {'report':descriptor,'pending':'REQUEST_CHANGES'},
        {'report':descriptor,'scope':{'H2':'unresolved'}},
        {'Do not execute until reviewed':descriptor},
        {'arbitrary_status':'a'*64},
        {'report':{**descriptor,'finding':'unresolved'}},
        {'report':{**descriptor,'size':True}},
    ]:
        assert not r._referenceable_metadata(value)
    for kind,sequence,omitted in [
        ('REVIEW',2,True),('DISPOSITION',2,True),
        ('REVIEW',4,False),('DISPOSITION',4,False),
        ('AUTHORIZED',2,False),('APPLIED',2,False),
    ]:
        event={'sequence':sequence,'event':kind,'payload':{
            'review_evidence':{'report':descriptor},
            'rationale':'Exact unresolved adverse finding.',
            'conditions':['No adoption before formal acceptance.'],
            'unknown':{'report':descriptor}}}
        before=deepcopy(event)
        shown=r._administrative_event(event,3,deepcopy)
        assert event==before
        assert ('review_evidence' not in shown['payload']) is omitted
        for name in ('rationale','conditions','unknown'):
            assert shown['payload'][name]==event['payload'][name]


def field_selection_packet(e, fault=None):
    state=deepcopy(e.current_chain)
    event=append(state,'DISPOSITION',{'rationale':'Synthetic settled source preparation. '*100,
        'affected_results':['No scientific acceptance.'],
        'conditions':['Unresolved independent condition stays literal.']})
    identity=state['request']['identity']
    plan={'schema':r.EVENT_FIELD_SELECTION,
        'qualification':'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION',
        'purpose':'settled-implementation-history-only',
        'requests':{identity:[{'event':event['identity'],'fields':['rationale'],
            'reason':'Synthetic proposed source-preparation reference; independent classification review pending.'}]}}
    if fault:
        row=plan['requests'][identity][0]
        if fault=='unknown_field':row['fields']=['unknown']
        elif fault=='conditions':row['fields']=['conditions']
        elif fault=='verdict':row['fields']=['verdict']
        elif fault=='duplicate':plan['requests'][identity].append(deepcopy(row))
        elif fault=='unknown_event':row['event']='0'*64
        elif fault=='unknown_request':plan['requests']['0'*64]=plan['requests'].pop(identity)
        elif fault=='self_approval':plan['qualification']='APPROVED_BY_PRESENTATION'
        elif fault=='authority_scope':plan['purpose']='settled-scientific-authority'
        elif fault=='applied':row['event']=e.latest;row['fields']=['rationale']
    bound=r.boundary(state)
    if fault=='tail':
        late=append(state,'DISPOSITION',{'rationale':'Unreviewed new tail.', 'affected_results':['Synthetic']})
        plan['requests'][identity][0]['event']=late['identity']
    app=append(state,'APPLIED',{'modification':'Synthetic pending exact field selection.',
        'checks':['Synthetic binding checks'], 'review_status':'PENDING',
        'result_binding':{'source':SOURCE,'reviewed_history_prefix':bound,
                         'historical_event_selection':plan},
        'supersedes_applied_events':[e.latest]})
    write_state(Path(e.config['change_request_store']),state)
    packet=deepcopy(e.authority);packet.pop('scientific_change_history')
    packet['recorded_changes']=state
    packet['reviewer_evidence']['catalog_core']['change_request']['applied_event']=app['identity']
    return d.capture_current_history(e.config,packet),event


def test_explicit_field_view_keeps_native_original_and_unresolved_condition(captured):
    packet,event=field_selection_packet(captured);before=encoded(packet)
    view=d.selected_packet_view(packet,SOURCE)
    d.validate_selected_packet_view(view,packet,SOURCE)
    assert encoded(packet)==before
    rows=view['recorded_changes']['events'];selected=next(x for x in rows if x['identity']==event['identity'])
    assert 'rationale' not in selected['payload']
    assert selected['payload']['conditions']==event['payload']['conditions']
    assert selected['historical_source_fields']['fields']==['rationale']
    assert 'Complete external criticism.' in str(view)
    assert 'Synthetic settled source preparation.' not in str(view)
    assert next(x for x in packet['recorded_changes']['events'] if x['identity']==event['identity'])==event
    assert rows[-1]['payload']['review_status']=='PENDING'  # view grants nothing
    view['recorded_changes']['events'][-2]['payload']['conditions']=[]
    with pytest.raises(ValueError):d.validate_selected_packet_view(view,packet,SOURCE)


@pytest.mark.parametrize('fault',['unknown_field','conditions','verdict','duplicate','unknown_event',
    'unknown_request','self_approval','authority_scope','applied','tail'])
def test_field_selection_refuses_unknown_authority_and_unreviewed_scope(captured,fault):
    packet,event=field_selection_packet(captured,fault)
    with pytest.raises(ValueError):d.selected_packet_view(packet,SOURCE)
