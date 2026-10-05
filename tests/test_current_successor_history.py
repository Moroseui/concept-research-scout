
from copy import deepcopy
from pathlib import Path
import pytest
from orchestrator import current_scientific_input as current, disposition_context as dc
from orchestrator import change_requests as changes, reviewed_history as history
from orchestrator import scientific_evidence_access as access
from orchestrator.handover_coordinator import digest
from test_current_input_integration import current_packet
from test_linked_input_integration import integrated
from test_selected_scientific_history import captured, append, write_state
from test_campaign_grounding_presentation import example
from test_disposition_context import SOURCE


def next_packet(e,kind):
    packet=deepcopy(e.current_packet);packet.pop('scientific_change_history')
    store=Path(e.config['change_request_store'])
    primary=dc._primary_change(packet)
    states={key:changes.load(store/key) for key in e.current_packet['scientific_change_history']['native_prefixes']}
    state=states[primary['request_id']]
    plans={key:{'schema':history.CURRENT_SETTLEMENT,'boundary':history.boundary(value),
        'settlements':{},'scope':'settled-implementation-history-only',
        'qualification':'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION'} for key,value in states.items()}
    app=append(state,'APPLIED',{'modification':'Synthetic same-plan later wake.',
        'checks':['Synthetic native scope check'],'review_status':'PENDING',
        'result_binding':{'source':SOURCE,'current_state_settlements':plans},
        'supersedes_applied_events':[primary['applied_event']]})
    write_state(store,state)
    packet['recorded_changes']=state
    packet['reviewer_evidence']['catalog_core']['change_request']['applied_event']=app['identity']
    evidence=packet['reviewer_evidence']['input_evidence']
    # This tests native history capture, not the separately gated original-event
    # verifier. No model authority, acceptance or real result is fabricated.
    event={'kind':kind,'identity':'1'*64,'original_sha256':'2'*64}
    evidence['verified_events']=[{'event':event}]
    wake=evidence['investigator_wake'];wake['events']=[event]
    wake['identity']=digest({k:v for k,v in wake.items() if k!='identity'})
    return packet,state,app


@pytest.mark.parametrize('kind',['BOOTSTRAP','TASK','OPERATION','STEERING'])
def test_later_wake_uses_same_native_current_plan(current_packet,kind):
    e=current_packet;packet,state,app=next_packet(e,kind)
    assert not current.has_references(packet,SOURCE)
    assert current.has_current_plan(e.config,packet)
    saved=dc.capture_current_history(e.config,packet)
    assert current.is_current(saved)
    assert all(v['schema']==history.CURRENT_VIEW for v in saved['scientific_change_history']['current_requests'].values())
    cap=access.capture_task_changes(e.config['change_request_store'],saved,source=SOURCE)
    # Later history remains available but cannot rewrite the already saved view.
    append(state,'DISPOSITION',{'rationale':'Synthetic later unreviewed criticism.',
                               'affected_results':['Synthetic next wake']})
    write_state(Path(e.config['change_request_store']),state)
    assert access.capture_task_changes(e.config['change_request_store'],saved,source=SOURCE)==cap


@pytest.mark.parametrize('fault',['drop_namespace','extra_namespace','wrong_source','changed_prefix','drop_criticism'])
def test_later_wake_scope_or_history_tampering_refuses(current_packet,fault):
    e=current_packet;packet,_,_=next_packet(e,'TASK')
    saved=dc.capture_current_history(e.config,packet)
    h=saved['scientific_change_history'];key=next(iter(h['native_prefixes']))
    if fault=='drop_namespace':h['native_prefixes'].pop(key)
    elif fault=='extra_namespace':h['native_prefixes']['0'*64]=deepcopy(h['native_prefixes'][key])
    elif fault=='wrong_source':h['source']='0'*40
    elif fault=='changed_prefix':h['native_prefixes'][key]['head_sha256']='0'*64
    else:h['current_requests'][key]['events']=[]
    with pytest.raises((ValueError,KeyError)):
        access.capture_task_changes(e.config['change_request_store'],saved,source=SOURCE)
