"""Native-store formal capture plus synthetic protected transport; no model calls."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest
from orchestrator import change_requests as changes, formal_decisions as formal
from orchestrator import scientific_evidence_access as access, scientific_evidence_runtime as runtime
from orchestrator.hosted_cycle import encoded
from test_change_requests import case, authority, application, review, AGENT
from test_research_task_authority import setup as authority_setup
from test_formal_scientific_versions import formal_request, formal_broker

NATIVE_LOAD = changes.load


@pytest.fixture
def formal_case(case, tmp_path):
    repo, store, folder, change = case
    authority(folder)
    applied = application(folder, tmp_path, source=change["target"]["source"])
    review(folder, applied, tmp_path, verdict="REQUEST_CHANGES")
    source = change["target"]["source"]
    config = {"source": source, "source_root": str(repo), "state": str(tmp_path/"state"),
              "change_request_store": str(store), "controller_uid": os.getuid()}
    request = formal_request(config)
    request["change_request"] = {"request_id": change["identity"], "applied_event": applied["identity"]}
    request["evidence"] = {"original.json": '{"finding":"unresolved synthetic criticism"}'}
    return config, request, formal._packet(config, request), folder


def test_formal_originals_are_readable_and_not_scientific_acceptance(formal_case, tmp_path):
    config, request, packet, folder = formal_case
    captured = access.capture_formal_changes(config["change_request_store"], packet, source=config["source"])
    descriptor = access.write_capture(tmp_path/"cache", captured)
    reader = access.Reader(tmp_path/"cache", descriptor["manifest_sha256"],
                           source=config["source"], task_binding=access.sha(encoded(packet)), owner=os.getuid())
    assert any(row["provenance"].get("event_kind") == "REVIEW" for row in reader.records)
    assert reader.call("search", {"capture":reader.identity,"cursor":0,"text":"REQUEST_CHANGES"})["matches"]
    row = reader.rows["formal/evidence/original.json"]
    reply = reader.call("read", {"capture":reader.identity,"name":row["name"],"sha256":row["sha256"],
                                "offset":0,"characters":8192})
    assert reply["content"] == request["evidence"]["original.json"]
    assert "not independent validation" in row["provenance"]["meaning"]
    changes.record(folder, "DISPOSITION", AGENT, {
        "rationale":"Later appended state must not change the saved formal capture.", "affected_results":["fixture"]})
    again = access.capture_formal_changes(config["change_request_store"], packet, source=config["source"])
    assert access.describe_capture(again) == descriptor


@pytest.mark.parametrize("failure", ["source", "contract", "application", "namespace",
                                   "event_body", "request_body", "native_artifact", "missing_event",
                                   "extra_packet_field", "hybrid_history"])
def test_formal_capture_rejects_changed_or_unbound_evidence(formal_case, failure):
    config, request, packet, folder = formal_case
    source = config["source"]
    if failure == "source": source = "f"*40
    elif failure == "contract": packet["scientific_decision_artifacts"]["subject"] = "changed"
    elif failure == "application": packet["formal_request"]["change_request"]["applied_event"] = "f"*64
    elif failure == "namespace": packet["formal_request"]["change_request"]["request_id"] = "f"*64
    elif failure == "event_body": packet["recorded_changes"]["events"][-1]["payload"]["rationale"] = "changed"
    elif failure == "request_body": packet["recorded_changes"]["request"]["requested_change"] = "changed"
    elif failure == "native_artifact": next((folder/"evidence").iterdir()).write_text("changed")
    elif failure == "missing_event":
        # Directory order varies by filesystem; .lock is not a history event.
        sorted((folder/"events").glob("*.json"))[0].rename(folder/"preserved-event")
    elif failure == "hybrid_history": packet["scientific_change_history"] = {}
    else: packet["extra"] = True
    with pytest.raises((ValueError,FileNotFoundError)):
        access.capture_formal_changes(config["change_request_store"], packet, source=source)


def test_formal_source_opt_in_preserves_previous_packet_input(formal_case):
    config, _, packet, _ = formal_case
    root = Path(config["source_root"])
    assert runtime.controller_options(config, root, config["source"], packet, "continuation") == {}
    module = root/"orchestrator/scientific_evidence_runtime.py"
    module.parent.mkdir()
    module.write_text("SCIENTIFIC_ROLE_INPUT_VERSION = 1\n")  # Prior b62 capability only.
    subprocess.run(["git","add","."], cwd=root, check=True)
    subprocess.run(["git","commit","-qm","Synthetic previous scientific role profile"], cwd=root, check=True)
    previous = subprocess.check_output(["git","rev-parse","HEAD"], cwd=root, text=True).strip()
    assert runtime.enabled(root, previous) is True
    assert runtime.enabled(root, previous, formal=True) is False
    module.write_text(module.read_text()+"FORMAL_EVIDENCE_INPUT_VERSION = 1\n")
    subprocess.run(["git","add","."], cwd=root, check=True)
    subprocess.run(["git","commit","-qm","Synthetic formal role profile"], cwd=root, check=True)
    current = subprocess.check_output(["git","rev-parse","HEAD"], cwd=root, text=True).strip()
    assert runtime.enabled(root, current, formal=True) is True


def test_controller_and_protected_broker_derive_same_formal_capture(formal_case, tmp_path, monkeypatch):
    from orchestrator import protected_scientific_jobs
    config, request, packet, folder = formal_case
    monkeypatch.setattr(runtime,"enabled",lambda *a,**kw: kw.get("formal") is True)
    monkeypatch.setattr(protected_scientific_jobs,"controller_configuration",lambda broker: config)
    descriptors = []
    for stage, role in [("continuation","author"),("review","reviewer")]:
        expected = runtime.controller_options(config,config["source_root"],config["source"],packet,stage)
        actual = runtime.broker_capture(SimpleNamespace(),packet,source=config["source"],folder=tmp_path/"broker",stage=stage)
        assert actual["descriptor"] == expected["evidence_access"]["descriptor"]
        assert actual["role"] == role
        descriptors.append(actual["descriptor"])
    assert descriptors[0] == descriptors[1]
    assert not (Path(config["state"])/"scientific-evidence-expectations").exists()
    monkeypatch.setattr(runtime,"enabled",lambda *a,**kw: False)
    assert runtime.broker_capture(SimpleNamespace(),packet,source=config["source"],folder=tmp_path/"unused",stage="review") is None


def test_actual_formal_caller_opt_in_and_recovery_are_not_new_admission(case, authority_setup, monkeypatch):
    # Real saved native change chain; explicit synthetic protected provider/policy
    # fixture. This does not assert native CLI consumption or a scientific result.
    config, _, _ = authority_setup
    repo, store, folder, change = case
    monkeypatch.setattr(changes, "load", NATIVE_LOAD)
    authority(folder)
    applied = application(folder, folder.parent, name="formal-runtime-fixture", source=config["source"])
    request = formal_request(config)
    request["change_request"] = {"request_id":change["identity"],"applied_event":applied["identity"]}
    config["change_request_store"] = str(store)
    module = Path(config["source_root"])/"orchestrator/scientific_evidence_runtime.py"
    module.write_text("SCIENTIFIC_ROLE_INPUT_VERSION = 1\nFORMAL_EVIDENCE_INPUT_VERSION = 1\n")
    broker = formal_broker(monkeypatch)
    output = Path(config["state"])/"formal-decisions/evidence"
    profiles = []
    native_options = runtime.controller_options
    def observed(*args, **kwargs):
        options = native_options(*args, **kwargs)
        profiles.append(options)
        return options
    monkeypatch.setattr(runtime, "controller_options", observed)
    first = formal.execute_formal_decision(config,request,output,client=broker)
    assert first["new_model_calls"] == 2 and first["application_status"] == "NOT_APPLIED"
    assert {p["evidence_access"]["role"] for p in profiles} == {"author","reviewer"}
    assert len({p["evidence_access"]["descriptor"]["manifest_sha256"] for p in profiles}) == 1
    assert all("Only bound read-only scientific evidence tools" in prompt for prompt in broker.prompts)
    originals = {p.relative_to(output):p.read_bytes() for p in output.rglob("*") if p.is_file()}
    recovered = formal.execute_formal_decision(config,request,output,client=broker)
    assert recovered["new_model_calls"] == 0
    assert broker.calls.count("admit_server") == 1 and broker.calls.count("model_stage") == 2
    assert {p.relative_to(output):p.read_bytes() for p in output.rglob("*") if p.is_file()} == originals
    # Protected proof lookup must still recover original replies without loading
    # the controller-private store. It does not assert a fresh retrieval.
    monkeypatch.setattr(changes,"load",lambda *a: pytest.fail("Protected proof must not load private store"))
    formal.verify_original_decision(config["source_root"],first["decision_path"],
        action=request["action"],subject=request["subject"],bindings=request["bindings"],
        source=request["source"],original_client=broker)


def test_formal_capture_cross_owner_reads_same_exact_originals(formal_case, monkeypatch):
    config, request, packet, folder = formal_case
    expected = access.capture_formal_changes(config["change_request_store"], packet, source=config["source"])
    owner = os.getuid()
    monkeypatch.setattr(os, "getuid", lambda: 0)
    with pytest.raises(ValueError, match="CHANGE_PRIVATE_FILE_REQUIRED"):
        access.capture_formal_changes(config["change_request_store"], packet, source=config["source"])
    assert access.capture_formal_changes(config["change_request_store"], packet,
        source=config["source"], owner=owner) == expected
