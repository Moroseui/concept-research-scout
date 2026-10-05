"""Native history is authenticated before compact construction; final limits stay."""
from copy import deepcopy
from pathlib import Path
import pytest
from orchestrator import current_scientific_input as current, disposition_context as dc
from orchestrator import change_requests as changes
from orchestrator.hosted_cycle import encoded
from test_current_input_integration import current_packet
from test_linked_input_integration import integrated
from test_selected_scientific_history import captured, append, write_state
from test_campaign_grounding_presentation import example
from test_current_successor_history import next_packet
from test_disposition_context import SOURCE


def test_native_history_is_removed_only_from_preparation_view_after_exact_authentication(current_packet,monkeypatch):
    e=current_packet;packet=deepcopy(e.original_input)
    native=deepcopy(packet['recorded_changes']);native['events'].append({'synthetic_large_native_body':'x'*2100000})
    packet['recorded_changes']=native
    # This seam supplies already loaded native bytes; chain authenticity and
    # original evidence reads are exercised by the unmocked integration below.
    monkeypatch.setattr(changes,'load',lambda *a,**kw:deepcopy(native))
    before=deepcopy(packet)
    assert len(encoded(packet))>2000000
    with pytest.raises(ValueError):dc._bytes(packet)
    view=current.preparation_view(e.config,packet)
    assert len(dc._bytes(view))<2000000
    assert view['recorded_changes']['schema']=='current-change-state-location/v1'
    assert packet==before
    altered=deepcopy(packet);altered['recorded_changes']['head_sha256']='0'*64
    with pytest.raises(ValueError,match='PRIMARY_ORIGINAL_CHANGED'):current.preparation_view(e.config,altered)
    # An already saved context gets no preparation exemption.
    saved={**packet,'scientific_change_history':{'schema':current.SCHEMA}}
    assert current.preparation_view(e.config,saved) is saved
    with pytest.raises(ValueError):dc._bytes(saved)


def test_native_compact_capture_keeps_same_snapshot_and_does_not_accept_forged_placeholder(current_packet):
    e=current_packet
    assert dc.capture_current_history(e.config,e.original_input)==e.current_packet
    placeholder=current.preparation_view(e.config,e.original_input)
    with pytest.raises(ValueError,match='PRIMARY_ORIGINAL_CHANGED'):
        current.capture_history(e.config,placeholder)


def test_expanding_unresolved_obligations_still_hit_final_packet_limit(current_packet):
    e=current_packet;packet,state,_=next_packet(e,'TASK')
    # Newly unreviewed criticism cannot be classified as settled by age.
    for i in range(101):
        append(state,'DISPOSITION',{'rationale':str(i)+':'+('unresolved evidence '*1050),
                                   'affected_results':['Synthetic pending correction']})
    write_state(Path(e.config['change_request_store']),state)
    packet['recorded_changes']=state
    before=deepcopy(packet)
    assert len(encoded(packet))>2000000
    with pytest.raises(ValueError):dc.capture_current_history(e.config,packet)
    assert packet==before
