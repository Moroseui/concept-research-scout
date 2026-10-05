"""Existing019 campaign allowance is enforced, not reset by a source pin."""
import json
from pathlib import Path
import pytest
from orchestrator import hosted_context as hc, hosted_cycle as cycle
from orchestrator.current_scientific_input import SCHEMA
from test_broker_input_preflight import case


def state(source="a"*40):
    return {"trigger":"installed-research-request",
            "scientific_change_history":{"schema":SCHEMA,"source":source}}


@pytest.mark.parametrize("stage,family,ceiling",[
    ("continuation","codex",830403),("review","claude",860699),
    ("disposition","codex",1007069)])
@pytest.mark.parametrize("source",["a"*40,"b"*40])
def test_exact_original_boundary_and_source_does_not_reset(stage,family,ceiling,source):
    result=hc.measure_input(chr(233)*ceiling,family,stage,task_state=state(source))
    assert result["reviewed_growth"]["remaining_characters"]==0
    assert result["utf8_bytes"]==2*result["characters"]
    with pytest.raises(hc.InputTooLarge,match="REVIEWED_GROWTH_ALLOWANCE") as e:
        hc.measure_input("x"*(ceiling+1),family,stage,task_state=state(source))
    assert e.value.measurement["provider_calls"]==0
    assert e.value.measurement["reviewed_growth"]["allowance_characters"]==60000


def test_historical_and_other_scientific_actions_keep_their_original_bounds():
    for value in [None, {"trigger":"installed-research-request"},
                  {**state(),"trigger":"installed-research-eligibility"},
                  {**state(),"trigger":"formal-scientific-decision"}]:
        result=hc.measure_input("x"*900000,"claude","review",task_state=value)
        assert "reviewed_growth" not in result


def test_protected_broker_refuses_before_admission_and_preserves_no_retry(tmp_path,monkeypatch):
    broker,body,folder,calls=case(tmp_path,monkeypatch,830404)
    body["packet"]=state()
    # These existing components have their own native binding tests. Isolate
    # actual dispatch ordering, refusal persistence and repeat reconciliation.
    monkeypatch.setattr("orchestrator.protected_handover.model_output_format",lambda *a:"markdown")
    monkeypatch.setattr("orchestrator.scientific_evidence_runtime.broker_capture",lambda *a,**k:None)
    with pytest.raises(hc.InputTooLarge,match="REVIEWED_GROWTH_ALLOWANCE"):
        broker.model_stage(body)
    assert calls==["compose"]
    receipt=json.loads((folder/"continuation.input-refused.json").read_bytes())
    assert receipt["measurement"]["reviewed_growth"]["remaining_characters"]==-1
    assert receipt["automatic_retry"] is False
    with pytest.raises(ValueError,match="INPUT_PREFLIGHT_RECONCILE_NO_RETRY"):
        broker.model_stage(body)
    assert calls==["compose"]


def test_actual_model_dispatch_checks_again_before_worker_preparation(tmp_path,monkeypatch):
    folder=tmp_path/"turn";folder.mkdir(mode=0o700)
    monkeypatch.setattr(cycle.subprocess,"check_output",lambda *a,**k:"a"*40)
    monkeypatch.setattr(cycle,"checked_source",lambda *a:tmp_path)
    monkeypatch.setattr(hc,"envelope",lambda *a,**k:("x"*830404,{"task_state":state(),"verified_source_commit":"a"*40}))
    monkeypatch.setattr(cycle.pwd,"getpwnam",lambda *a:pytest.fail("worker prepared"))
    monkeypatch.setattr(cycle.subprocess,"Popen",lambda *a,**k:pytest.fail("model launched"))
    with pytest.raises(hc.InputTooLarge,match="REVIEWED_GROWTH_ALLOWANCE"):
        cycle.model_call(folder,"continuation","astra","fixture")
    receipt=json.loads((folder/"continuation.input-preflight-failure.json").read_bytes())
    assert receipt["measurement"]["refusal_reason"]=="HOSTED_REVIEWED_GROWTH_ALLOWANCE_EXCEEDED"
    assert not (folder/"continuation.started.json").exists()
