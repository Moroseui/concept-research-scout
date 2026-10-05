"""Native formal sealing/capture with synthetic providers; no scientific result."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from orchestrator import continuing_operations as ops, formal_decisions as formal
from orchestrator import scientific_context_references as refs
from orchestrator import scientific_deferred_evidence as deferred
from orchestrator import scientific_evidence_access as access
from orchestrator.hosted_cycle import encoded
from test_research_task_authority import setup as authority_setup
from test_formal_scientific_versions import formal_broker


@pytest.fixture(params=["ACCEPT_RESULT", "ADOPT_FOLLOWUP"])
def case(authority_setup, monkeypatch, request):
    config, _, _ = authority_setup
    config["continuing_operations"] = {"enabled": True}
    kind = request.param
    interpretation = {"task": "1"*64, "artifact": "round-1/interpretation.md", "sha256": "2"*64}
    selection = {"task": "3"*64, "artifact": "round-1/selection.json", "sha256": "4"*64}
    acceptance = {"operation": "5"*64, "result_sha256": "6"*64}
    inputs = {"interpretation": interpretation} if kind == "ACCEPT_RESULT" else {
        "acceptance": acceptance, "selection": selection}
    core = {"source": config["source"], "operation": {"schema": ops.SCHEMA,
        "operation_id": "synthetic-deferred-h2", "kind": kind, "inputs": inputs},
        "selected_by": selection, "predecessor": {"task": selection["task"]},
        "actor": {"kind": "agent", "family": "codex", "model": "synthetic", "session_id": "fixture"},
        "change_request": {"request_id": "c"*64, "applied_event": "d"*64}}
    identity = ops.digest(core)
    saved = {**core, "identity": identity, "created_at_utc": "2026-09-23T00:00:00Z"}
    folder = ops._directory(config)/identity
    folder.mkdir(parents=True, mode=0o700)
    (folder/"request.json").write_bytes(encoded(saved))
    bindings = {"source": config["source"]}
    if kind == "ACCEPT_RESULT":
        bindings.update(interpretation_task=interpretation["task"], interpretation_sha256=interpretation["sha256"])
    else:
        bindings.update(selection=selection, acceptance_sha256=refs.digest(acceptance))
    action, prefix, before, after = deferred.KINDS[kind]
    formal_request = {"schema": formal.SCHEMA, "source": config["source"],
        "action": action, "subject": prefix + refs.digest(bindings)[:56], "bindings": bindings,
        "evidence": {"synthetic-input.json": '{"status":"TEST_ONLY"}'},
        "request": "Synthetic fixture; preserve this unresolved scientific question.",
        "transition": {"from": before, "to": after}, "workspace": None, "application": None,
        "change_request": saved["change_request"]}
    original_broker = formal_broker(monkeypatch, decision="DEFER")
    def broker(socket, operation, body):
        result = original_broker(socket, operation, body)
        if operation == "model_stage" and body["stage"] == "continuation":
            answer = json.loads(result["answer"])
            judgment = json.loads(answer["judgment.json"])
            judgment["transition"]["from"] = before
            judgment["rationale"] = "Synthetic unresolved inference; no acceptance or adoption."
            judgment["reconsideration"] = "Obtain the missing independent evidence before any new decision."
            answer["judgment.json"] = json.dumps(judgment)
            result["answer"] = json.dumps(answer)
            result["receipt"]["answer_sha256"] = hashlib.sha256(result["answer"].encode()).hexdigest()
            original_broker.originals["continuation"] = deepcopy(result)
        return result
    output = Path(config["state"])/"formal-decisions"/identity
    outcome = formal.execute_formal_decision(config, formal_request, output, client=broker)
    (folder/"prepared.json").write_bytes(encoded({"formal_request": formal_request}))
    (folder/"step-0.json").write_bytes(encoded({"result": outcome}))
    ops._finalize(saved, folder, outcome)
    return SimpleNamespace(config=config, identity=identity, folder=folder, output=output,
        source=config["source"], kind=kind, broker=broker, transport=original_broker,
        request=formal_request, saved=saved, outcome=outcome)


def full(case):
    return {"continuing_operations": ops.status(case.config), "scientific_completions": []}


def captured(case):
    shown = refs.snapshot(case.config, full(case), deferred=True, original_client=case.broker)
    packet = {"continuing_context": shown}
    base = {"manifest": {"schema": access.SCHEMA, "source": case.source,
        "task_binding": refs.digest(packet), "request_heads": {}, "records": [],
        "semantics": "Synthetic originals only; no acceptance inferred."}, "payloads": {}}
    return packet, refs.capture(base, case.config, packet, original_client=case.broker)


def test_native_defer_originals_reach_actual_bounded_reader(case, tmp_path):
    packet, capture = captured(case)
    row = packet["continuing_context"]["continuing_operations"]["operations"][0]
    assert row["status"] == "DEFERRED"
    descriptor = row["deferred_decision"]
    decision = json.loads((case.output/"round-1/decision.json").read_text())
    assert descriptor["rationale"] == decision["rationale"]
    assert descriptor["reconsideration"] == decision["reconsideration"]
    assert descriptor["source"] == case.source
    written = access.write_capture(tmp_path/"capture", capture)
    reader = access.Reader(tmp_path/"capture", written["manifest_sha256"], source=case.source,
        task_binding=refs.digest(packet), owner=os.getuid())
    for name in ["judgment.json", "review.json", "decision.json"]:
        key = "deferred-operation/"+case.identity+"/formal/"+name
        original = reader.rows[key]
        reply = reader.call("read", {"capture": reader.identity, "name": key,
            "sha256": original["sha256"], "offset": 0, "characters": 8192})
        assert reply["content"] == (case.output/"round-1"/name).read_text()
        assert "no acceptance" in original["provenance"]["meaning"]
    assert reader.call("search", {"capture": reader.identity, "cursor": 0,
                                  "text": decision["reconsideration"]})["matches"]


def test_repeated_capture_cannot_admit_execute_apply_or_replace_originals(case):
    packet, capture = captured(case)
    before = {p: p.read_bytes() for p in Path(case.config["state"]).rglob("*") if p.is_file()}
    counts = {name: case.transport.calls.count(name) for name in ("admit_server", "model_stage")}
    for _ in range(2):
        other_packet, other_capture = captured(case)
        assert other_packet == packet and other_capture == capture
        ops.status(case.config)
    assert before == {p: p.read_bytes() for p in Path(case.config["state"]).rglob("*") if p.is_file()}
    assert counts == {name: case.transport.calls.count(name) for name in counts}
    ref = packet["continuing_context"]["continuing_operations"]["operations"][0]["deferred_decision"]["reference"]
    with pytest.raises(ValueError, match="COMPLETED_OPERATION_BINDING"):
        ops.read_operation_result(case.config, ref)
    with pytest.raises(ValueError, match="FORMAL_DECISION_DEFERRED"):
        from orchestrator.investigator_wakes import _formal
        _formal(case.config, case.outcome["decision_path"], case.broker)
    assert not (case.folder/"step-1.json").exists()
    assert not (Path(case.config["state"])/"scientific-adoptions").exists()
    assert not (Path(case.config["state"])/"scientific-results").exists()


@pytest.mark.parametrize("damage", ["missing", "changed_judgment", "changed_review", "changed_seal",
    "provider_reply", "provider_receipt", "result_status", "result_source", "step", "prepared",
    "different_decision", "applied_step", "operation_input"])
def test_missing_or_changed_originals_fail_closed_without_new_call(case, damage):
    before = case.transport.calls.count("model_stage")
    if damage in ("missing", "changed_judgment", "changed_review", "changed_seal"):
        name = {"missing": "review.json", "changed_judgment": "judgment.json",
                "changed_review": "review.json", "changed_seal": "decision.json"}[damage]
        path = case.output/"round-1"/name
        if damage == "missing": path.unlink()
        else: path.write_text("{}")
    elif damage in ("provider_reply", "provider_receipt"):
        original = case.transport.originals["review"]
        if damage == "provider_reply":
            original["answer"] = json.dumps({"review.json": "Changed provider original"})
            original["receipt"]["answer_sha256"] = hashlib.sha256(original["answer"].encode()).hexdigest()
        else: original["receipt"]["session_id"] = "changed-session"
    elif damage == "applied_step": (case.folder/"step-1.json").write_text("{}")
    elif damage == "operation_input":
        path = case.folder/"request.json"; value = json.loads(path.read_text())
        value["operation"]["operation_id"] = "different-operation"
        path.write_bytes(encoded(value))
    else:
        target = "step-0.json" if damage == "step" else "prepared.json" if damage == "prepared" else "result.json"
        path = case.folder/target; value = json.loads(path.read_text())
        if damage == "result_status": value["status"] = "COMPLETE"
        elif damage == "result_source": value["source"] = "f"*40
        elif damage == "different_decision": value["result"]["decision_path"] = "/different/round-1/decision.json"
        elif damage == "prepared": value["formal_request"]["bindings"]["source"] = "f"*40
        else: value["result"]["decision_sha256"] = "f"*64
        path.write_bytes(encoded(value))
    with pytest.raises((ValueError, OSError, KeyError)):
        deferred.read(case.config, case.identity, original_client=case.broker)
    assert case.transport.calls.count("model_stage") == before


@pytest.mark.parametrize("damage", ["missing_descriptor", "changed_reason", "changed_pin", "relabel", "duplicate"])
def test_saved_snapshot_membership_and_original_reasons_are_bound(case, damage):
    packet, _ = captured(case)
    operations = packet["continuing_context"]["continuing_operations"]
    row = operations["operations"][0]
    if damage == "missing_descriptor": row.pop("deferred_decision")
    elif damage == "changed_reason": row["deferred_decision"]["rationale"] = "Fabricated settlement."
    elif damage == "changed_pin": row["deferred_decision"]["reference"]["result_sha256"] = "f"*64
    elif damage == "relabel": row["status"] = "COMPLETE"
    else: operations["operations"].append(deepcopy(row))
    base = {"manifest": {"schema": access.SCHEMA, "source": case.source,
        "task_binding": refs.digest(packet), "request_heads": {}, "records": [],
        "semantics": "Synthetic originals only; no acceptance inferred."}, "payloads": {}}
    with pytest.raises(ValueError):
        refs.capture(base, case.config, packet, original_client=case.broker)


def test_legacy_snapshot_unchanged_and_original_source_not_relabeled(case):
    old = refs.snapshot(case.config, full(case))
    assert "deferred_evidence_version" not in old["continuing_operations"]
    assert "deferred_decision" not in old["continuing_operations"]["operations"][0]
    newer = {**case.config, "source": "e"*40}
    native = deferred.read(newer, case.identity, original_client=case.broker)
    assert native["descriptor"]["source"] == case.source
    assert native["descriptor"]["reference"]["result_sha256"] == access.sha((case.folder/"result.json").read_bytes())


def test_source_profile_preserves_old_preparation(tmp_path, monkeypatch):
    root = tmp_path/"source"; (root/"orchestrator").mkdir(parents=True)
    path = root/"orchestrator/scientific_context_references.py"
    path.write_text("SCIENTIFIC_CONTEXT_INPUT_VERSION = 1\nPROTOCOL_CATALOG_INPUT_VERSION = 1\n")
    monkeypatch.setattr("orchestrator.remote_supervisor.checked_source", lambda path, source: path)
    assert refs.enabled(root, "a"*40) and not refs.enabled(root, "a"*40, deferred=True)
    path.write_text(path.read_text()+"DEFERRED_OPERATION_INPUT_VERSION = 1\n")
    assert refs.enabled(root, "a"*40, deferred=True)
    with pytest.raises(ValueError, match="SOURCE_PROFILE_OPTION"):
        refs.enabled(root, "a"*40, protocol=True, deferred=True)


def test_actual_runtime_capture_threads_original_reader(case, monkeypatch):
    from orchestrator import scientific_evidence_runtime as runtime
    packet, expected = captured(case)
    packet["scientific_change_history"] = {"schema": "authenticated-current-scientific-input/v1", "native_prefixes": {}}
    base = {"manifest": {"schema": access.SCHEMA, "source": case.source,
        "task_binding": refs.digest(packet), "request_heads": {}, "records": [],
        "semantics": "Synthetic original change capture boundary."}, "payloads": {}}
    # The change-store fixture is separate; this check exercises the actual
    # runtime -> context capture -> native deferred formal original reader path.
    monkeypatch.setattr(access, "capture_task_changes", lambda *a, **kw: deepcopy(base))
    monkeypatch.setattr(runtime, "enabled", lambda *a, **kw: True)
    monkeypatch.setattr(refs, "enabled", lambda *a, **kw: True)
    before = case.transport.calls.count("model_stage")
    capture = runtime._capture_originals(case.config, packet, case.source,
        root=case.config["source_root"], original_client=case.broker)
    selected = [row for row in capture["manifest"]["records"] if row["name"].startswith("deferred-operation/")]
    assert len(selected) == 12
    assert all(capture["payloads"][row["sha256"]] == expected["payloads"][row["sha256"]] for row in selected)
    assert case.transport.calls.count("model_stage") == before
    with pytest.raises(ValueError, match="DEFERRED_ORIGINAL_READER_REQUIRED"):
        runtime._capture_originals(case.config, packet, case.source, root=case.config["source_root"])
    packet["continuing_context"]["continuing_operations"].pop("deferred_evidence_version")
    base["manifest"]["task_binding"] = refs.digest(packet)
    with pytest.raises(ValueError, match="DEFERRED_CURRENT_SNAPSHOT_REQUIRED"):
        runtime._capture_originals(case.config, packet, case.source,
            root=case.config["source_root"], original_client=case.broker)


def test_newly_accumulating_unresolved_deferrals_remain_visible(case, monkeypatch, record_property):
    full_context = full(case)
    actual = deferred.read(case.config, case.identity, original_client=case.broker)
    original_read = deferred.read
    # Size projection only: copied synthetic obligations are not native results.
    # The prior tests authenticate every real fixture through the native parser.
    def projected_read(config, identity, **kw):
        if identity == case.identity: return original_read(config, identity, **kw)
        projected = deepcopy(actual)
        projected["descriptor"]["reference"]["operation"] = identity
        return projected
    monkeypatch.setattr(deferred, "read", projected_read)
    first = refs.snapshot(case.config, full_context, deferred=True, original_client=case.broker)
    for number in range(10):
        row = deepcopy(full_context["continuing_operations"]["operations"][0])
        row["operation"] = f"{1000+number:064x}"
        full_context["continuing_operations"]["operations"].append(row)
    later = refs.snapshot(case.config, full_context, deferred=True, original_client=case.broker)
    record_property("synthetic_one_defer_characters", len(encoded(first).decode()))
    record_property("synthetic_one_defer_utf8_bytes", len(encoded(first)))
    record_property("synthetic_eleven_defers_characters", len(encoded(later).decode()))
    record_property("synthetic_eleven_defers_utf8_bytes", len(encoded(later)))
    assert len(encoded(later)) > len(encoded(first)) + 8000
    assert len(later["continuing_operations"]["operations"]) == 11
    assert all(row["deferred_decision"]["reconsideration"] == actual["descriptor"]["reconsideration"]
               for row in later["continuing_operations"]["operations"])
