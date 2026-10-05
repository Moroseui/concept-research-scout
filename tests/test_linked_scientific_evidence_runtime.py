"""Actual role capture wiring with explicit synthetic task/protected-reader seams."""
from copy import deepcopy
from types import SimpleNamespace
import os
import pytest

from orchestrator import scientific_evidence_access as access, scientific_evidence_runtime as runtime
from orchestrator import disposition_context as context, disposition_successors as native
from orchestrator import protected_scientific_jobs, handover_runtime, change_requests
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded
from test_scientific_evidence_access import capture, case
from test_linked_disposition_reference import original


def selected(source, value):
    event = {"kind":"DISPOSITION","identity":value["originals"]["origin_task"],
             "original_sha256":value["result_sha256"]}
    core = {"schema":context.WAKE,"source":source,"template_sha256":"a"*64,
            "events":[event],"day":"2026-09-19"}
    return {"investigator_wake":{**core,"identity":digest(core)},
            "verified_events":[{"event":event,"linked_disposition":deepcopy(value)}]}


@pytest.mark.parametrize("projected", [False, True])
def test_only_fixed_validated_wake_dispositions_supply_references(monkeypatch, projected):
    value = original(); source = "a"*40
    evidence = selected(source,value); reference = native.result_reference(value)
    if projected:
        evidence["verified_events"][0]["linked_disposition"]["input_presentation"] = {
            "original_reference":reference}
    # The full native source/application validator has separate integration tests.
    # Keep the slot selection and reference/original authentication real here.
    calls=[]
    monkeypatch.setattr(context,"_selected_evidence",lambda packet,pin:evidence)
    monkeypatch.setattr(context,"validate_current_history",lambda packet,pin:calls.append(pin))
    packet={"unrelated":{"input_presentation":{"original_reference":{"path":"/not-permitted"}}}}
    assert access.task_disposition_references(packet,source=source) == [reference]
    assert calls == [source]
    evidence["investigator_wake"]["identity"] = "f"*64
    with pytest.raises(ValueError):
        access.task_disposition_references(packet,source=source)


def test_invalid_native_history_cannot_reach_linked_reader(monkeypatch):
    value=original(); evidence=selected("a"*40,value)
    monkeypatch.setattr(context,"_selected_evidence",lambda *a:evidence)
    def refused(*args): raise ValueError("SYNTHETIC_SOURCE_APPLICATION_SUPERSEDED")
    monkeypatch.setattr(context,"validate_current_history",refused)
    with pytest.raises(ValueError,match="SUPERSEDED"):
        access.task_disposition_references({},source="a"*40)


@pytest.mark.parametrize("operation",["admit_server","model_stage","scientific_job_launch","execute","anything"])
def test_broker_original_adapter_cannot_mutate_or_dispatch(operation):
    class Never:
        def __getattr__(self,name): pytest.fail("Unrecognized operation must not reach broker")
    with pytest.raises(ValueError,match="ORIGINAL_READ_ONLY"):
        runtime.protected_original_client(Never())("",operation,{})


def test_controller_and_broker_capture_share_selected_scientific_originals(capture,tmp_path,monkeypatch):
    # This legacy native-reader fixture supplies no admitted application.
    # Runtime-prerequisite admission is tested separately; do not invent one.
    monkeypatch.setattr("orchestrator.scientific_runtime_prerequisites.verify",
                        lambda *args, **kwargs: None)
    store,folder,request,cache,descriptor,reader=capture
    source=descriptor["source"];state=change_requests.load(folder)
    value=original(); reference=native.result_reference(value)
    evidence=selected(source,value)
    packet={"scientific_change_history":{"fixture":"Native history bound separately"},
            "reviewer_evidence":evidence}
    config={"source":source,"source_root":str(tmp_path),"state":str(tmp_path/"state"),
            "change_request_store":str(store),"broker_socket":"fixed-synthetic-socket",
            "controller_uid":os.getuid()}
    monkeypatch.setattr(context,"_selected_evidence",lambda actual,pin: actual["reviewer_evidence"])
    monkeypatch.setattr(context,"validate_current_history",lambda actual,pin:{request["identity"]:state})
    monkeypatch.setattr(runtime,"enabled",lambda *a,**kw:True)
    monkeypatch.setattr(protected_scientific_jobs,"controller_configuration",lambda broker:config)
    calls=[]
    def original_read(actual,identity,client):
        assert actual == config and identity == reference["origin_task"]
        for operation in ("stage_status","stage_packet","disposition_refusal"):
            assert client("ignored",operation,{"original":identity}) == {"existing_original":True}
        return deepcopy(value)
    monkeypatch.setattr(native,"read_result",original_read)
    def socket_read(socket,op,body):
        assert socket == config["broker_socket"]
        calls.append(("controller",op,body));return {"existing_original":True}
    monkeypatch.setattr(handover_runtime,"request_broker",socket_read)
    class Broker:
        def stage_status(self,body): return self.read("stage_status",body)
        def stage_packet(self,body): return self.read("stage_packet",body)
        def read(self,op,body):
            calls.append(("protected",op,body));return {"existing_original":True}
    broker=Broker()
    # Selection fixture only; the real Broker/read-lock integration is exercised
    # in test_protected_disposition. Never invent a Broker method absent in production.
    monkeypatch.setattr("orchestrator.protected_disposition.disposition_refusal",
                        lambda actual,body:actual.read("disposition_refusal",body))
    for stage in ("continuation","review","disposition"):
        expected=runtime.controller_options(config,tmp_path,source,packet,stage)["evidence_access"]
        actual=runtime.broker_capture(broker,packet,source=source,folder=tmp_path/"broker",stage=stage)
        assert expected["descriptor"] == actual["descriptor"]
        r=access.Reader(actual["directory"],actual["descriptor"]["manifest_sha256"],
            source=source,task_binding=access.sha(encoded(packet)),owner=os.getuid())
        rows=[x for x in r.records if x["kind"]=="scientific_stage_output"]
        assert {x["provenance"]["role"] for x in rows} == {"author","reviewer","disposition"}
        for row in rows:
            text=value
            for key in row["provenance"]["path_in_native_original"]:text=text[key]
            assert r._body(row) == text
        assert any("REQUEST_CHANGES" in r._body(row) for row in rows)
    assert len(calls)==18
    assert {op for _,op,_ in calls}=={"stage_status","stage_packet","disposition_refusal"}
    assert sum(side=="controller" for side,_,_ in calls)==9


def test_old_profile_does_not_reinterpret_original_capture(capture,tmp_path,monkeypatch):
    # This legacy native-reader fixture supplies no admitted application.
    # Runtime-prerequisite admission is tested separately; do not invent one.
    monkeypatch.setattr("orchestrator.scientific_runtime_prerequisites.verify",
                        lambda *args, **kwargs: None)
    store,folder,request,cache,descriptor,reader=capture
    state=change_requests.load(folder);source=descriptor["source"]
    packet={"scientific_change_history":{},"reviewer_evidence":selected(source,original())}
    monkeypatch.setattr(context,"_selected_evidence",lambda packet,pin:packet["reviewer_evidence"])
    monkeypatch.setattr(context,"validate_current_history",lambda *a:{request["identity"]:state})
    monkeypatch.setattr(runtime,"enabled",lambda *a,**kw:not kw.get("linked",False))
    monkeypatch.setattr(native,"read_result",lambda *a:pytest.fail("Historical receipt must not acquire a new read"))
    config={"source":source,"source_root":str(tmp_path),"change_request_store":str(store)}
    actual=runtime._capture(config,packet,source)
    assert actual==access.capture_task_changes(store,packet,source=source)
