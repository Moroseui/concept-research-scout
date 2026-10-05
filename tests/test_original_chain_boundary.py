"""Original-history growth versus compact input, offline synthetic chains only."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import pytest
from orchestrator import disposition_context as dc, reviewed_history as history
from orchestrator import scientific_evidence_access as access, change_requests as changes
from orchestrator.hosted_cycle import encoded
from test_selected_scientific_history import captured, append, write_state
from test_campaign_grounding_presentation import example
from test_current_scientific_state import build
from test_disposition_context import SOURCE


def grow(e, count=42):
    state=deepcopy(e.current_chain);last=e.latest
    for i in range(count):
        event=append(state,'APPLIED',{'modification':'Synthetic superseded implementation '+str(i)+':'+'x'*50000,
            'checks':['Synthetic only'],'result_binding':{'source':SOURCE},'review_status':'PENDING',
            'supersedes_applied_events':[last]})
        last=event['identity']
    return state,last


@pytest.fixture
def large(captured):
    state,last=grow(captured)
    assert len(encoded(state))>2000000
    assert max(len(changes.encoded(e)+b'\n') for e in state['events'])<100000
    return captured,state,last


def test_complete_native_chain_and_prefix_hashes_scale_before_compact_selection(large):
    e,state,last=large
    assert dc._chain(state)==[event['identity'] for event in state['events']]
    assert dc._chain_sha(state)==hashlib.sha256(encoded(state)).hexdigest()
    with pytest.raises(ValueError,match='CONTEXT_REFERENCE_CHANGED'):dc._bytes(state)
    bound=history.boundary(state)
    current=deepcopy(state)
    app=append(current,'APPLIED',{'modification':'Synthetic new prefix application','checks':['Synthetic'],
        'result_binding':{'source':SOURCE,'reviewed_history_prefix':bound},'review_status':'PENDING',
        'supersedes_applied_events':[last]})
    ref=dc.prefix_reference(state,current,SOURCE)
    assert dc._restore_prefix(ref,current,SOURCE)==state
    assert ref['original_state_sha256']==hashlib.sha256(encoded(state)).hexdigest()
    compact=history.capture(current,app['identity'])
    assert len(dc._bytes(compact))<2000000
    assert history.validate(compact)==dc._chain(current)
    historical=history.capture_linked_history(state,bound,app['identity'])
    assert history.validate(historical)==dc._chain(state)
    selected=dc._selected_chain(state,SOURCE,'e'*64,{last})
    assert selected['original_chain_value_sha256']==hashlib.sha256(encoded(state)).hexdigest()
    assert len(dc._bytes(selected))<2000000
    assert 'Latest criticism remains unresolved.' in str(selected)


def test_native_extension_preserves_same_original_encoding(large,monkeypatch):
    _,state,_=large;current=deepcopy(state)
    append(current,'DISPOSITION',{'rationale':'Unreviewed tail stays literal.','affected_results':['Synthetic']})
    monkeypatch.setattr(dc,'_literal_histories',lambda packet,source:{(0,'historical_authority'):state})
    value=dc._current_extension(current,{},SOURCE)
    assert value['historical_chain_value_sha256']==hashlib.sha256(encoded(state)).hexdigest()
    assert value['current_chain_value_sha256']==hashlib.sha256(encoded(current)).hexdigest()
    assert dc._restore_current(value,{},SOURCE)==current


def test_current_capture_and_original_reader_cross_two_mb_without_model_expansion(large,tmp_path):
    e,state,last=large;e.current_chain=state;e.latest=last
    capture,original,app,closed,_=build(e,tmp_path)
    request=original['request']['identity']
    assert history.captured_chain(capture,request)==original
    view=history.current_state_view(capture,request,app['identity'],source=SOURCE)
    assert len(dc._bytes(view))<2000000 and len(encoded(original))>2000000
    assert 'Latest criticism remains unresolved.' in str(view)
    assert 'Unreviewed tail: do not execute.' in str(view)
    assert 'Human stop remains effective.' in str(view)
    assert app['payload']['review_status']=='PENDING'
    assert history.validate_current_state_view(view,capture,request,app['identity'],source=SOURCE)==view
    # Originals remain in the authenticated reader's actual record/payload route.
    name='change/'+request+'/event/'+str(closed[0]['sequence'])+'.json'
    row=next(x for x in capture['manifest']['records'] if x['name']==name)
    assert json.loads(capture['payloads'][row['sha256']])==closed[0]
    broken=deepcopy(capture);broken['payloads'].pop(row['sha256'])
    with pytest.raises(ValueError):history.current_state_view(broken,request,app['identity'],source=SOURCE)


@pytest.mark.parametrize('field',['previous_sha256','identity','request_identity','sequence','actor','head'])
def test_large_corrupted_chain_never_acquires_a_boundary(large,field):
    _,state,_=large;state=deepcopy(state)
    if field=='head':state['head_sha256']='e'*64
    elif field=='sequence':state['events'][-1][field]=1
    elif field=='actor':state['events'][-1][field]={'kind':'unknown'}
    else:state['events'][-1][field]='0'*64
    with pytest.raises(ValueError):history.boundary(state)


@pytest.mark.parametrize('bound',['record','count','aggregate'])
def test_original_reader_has_distinct_explicit_bounds(large,monkeypatch,bound):
    _,state,_=large;state=deepcopy(state)
    if bound=='record':
        state['events'][-1]['payload']['modification']='x'*100001
        reason='ORIGINAL_CHAIN_RECORD_BOUND'
    elif bound=='count':
        monkeypatch.setattr(access,'MAX_RECORDS',len(state['events']))
        reason='ORIGINAL_CHAIN_COUNT'
    else:
        monkeypatch.setattr(dc,'ORIGINAL_CHAIN_BYTES',len(encoded(state))-1)
        reason='ORIGINAL_CHAIN_AGGREGATE_BOUND'
    with pytest.raises(ValueError,match=reason):dc._chain(state)


def test_small_original_hash_and_compact_input_bounds_remain_unchanged(captured):
    state=captured.current_chain
    assert dc._chain_bytes(state)==dc._bytes(state)
    assert dc._chain_sha(state)==dc._sha(state)
    with pytest.raises(ValueError,match='CONTEXT_REFERENCE_CHANGED'):dc._bytes({'unresolved':'x'*2000000})
