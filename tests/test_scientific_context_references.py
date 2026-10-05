"""Native store/membership checks; synthetic results are never scientific approval."""
from copy import deepcopy
import json
import os

import pytest
from orchestrator import scientific_context_references as refs


@pytest.fixture
def config(tmp_path):
    tmp_path.chmod(0o700)
    return {"state": str(tmp_path), "source": "a"*40, "controller_uid": os.getuid(),
            "controller_gid": os.getgid()}


def completed(number=0):
    return {"reference": {"operation": f"{number+1:064x}", "result_sha256": f"{number+100:064x}"},
            "kind": "ACCEPT_RESULT",
            "result": {"interpretation": {"task": "b"*64, "artifact": "round-1/analysis.md", "sha256": "c"*64},
                       "scientific_acceptance": True, "adoption": False,
                       "body": "Synthetic complete result, not a real acceptance."*100}}


def context(count):
    return {"continuing_operations": {"status": "SAVED_OPERATIONS",
        "operations": [{"operation": f"{i+1:064x}", "kind": "ACCEPT_RESULT",
                        "step": "complete", "position": 3, "status": "COMPLETE", "reason": None} for i in range(count)] +
            [{"operation": "d"*64, "status": "DEFERRED", "reason": "Explicit unresolved condition."},
             {"operation": "e"*64, "status": "RECONCILIATION_REQUIRED", "reason": "No retry."}],
        "completed": [completed(i) for i in range(count)]},
        "scientific_completions": [{"event": f"{i+500:064x}", "status": "COMPLETE"} for i in range(count)]}


def test_reference_preserves_actual_original_and_fixed_scope(config):
    value = {"unresolved": "Do not accept.", "nested": [1, "?"]}
    ref = refs.save(config, "predecessor_evidence", "b"*64, value)
    assert refs.read(config, ref, kind="predecessor_evidence", subject="b"*64) == value
    assert "evidence_file" not in ref
    for key, replacement in [("source", "c"*40), ("subject", "c"*64), ("kind", "catalog_page")]:
        bad = {**ref, key: replacement}
        with pytest.raises(ValueError):
            refs.read(config, bad, kind="predecessor_evidence", subject="b"*64)


@pytest.mark.parametrize("fault", ["changed", "missing", "symlink", "size"])
def test_missing_or_changed_original_refuses(config, fault):
    from pathlib import Path
    ref = refs.save(config, "predecessor_evidence", "b"*64, {"value": "Original"})
    p = Path(config["state"])/"continuing-evidence"/(ref["sha256"]+".json")
    if fault == "changed":
        p.write_bytes(p.read_bytes().replace(b"Original", b"Modified"))
    elif fault == "missing":
        p.unlink()
    elif fault == "symlink":
        q = p.with_suffix(".preserved"); p.rename(q); p.symlink_to(q)
    else:
        ref = {**ref, "utf8_bytes": ref["utf8_bytes"]+1}
    with pytest.raises((ValueError, OSError)):
        refs.read(config, ref)


def test_predecessor_body_is_saved_once_and_does_not_expand_on_next_cycle(config):
    packet = {"reviewer_evidence": {"original": "Evidence "*1000}, "continuing_context": context(3)}
    packet["scientific_change_history"] = {"schema": "authenticated-current-scientific-input/v1",
                                           "native_prefixes": {}}
    first = refs.predecessor(config, packet)
    assert refs.read(config, first["prior_packet_evidence"]) == packet["reviewer_evidence"]
    next_packet = {"reviewer_evidence": first, "continuing_context": {},
                   "scientific_change_history": packet["scientific_change_history"]}
    second = refs.predecessor(config, next_packet)
    assert refs.read(config, second["prior_packet_evidence"]) == first
    assert len(json.dumps(second)) < 1000


def test_snapshot_retains_open_states_and_freezes_membership(config):
    full = context(101)
    shown = refs.snapshot(config, full)
    packet = {"continuing_context": shown}
    rows = refs.completed_rows(config, packet)
    assert len(rows) == 101
    assert rows[0] == refs.operation_metadata(completed(0))
    assert [r["status"] for r in shown["continuing_operations"]["operations"]] == [
        "DEFERRED", "RECONCILIATION_REQUIRED"]
    assert len(refs.completion_rows(config, packet)) == 101
    newer = refs.snapshot(config, context(102))
    assert len(refs.completed_rows(config, packet)) == 101
    assert len(refs.completed_rows(config, {"continuing_context": newer})) == 102
    assert full == context(101)


def test_settled_growth_stays_outside_starting_context_and_open_growth_remains(config):
    sizes = []
    for count in (1, 10, 100):
        shown = refs.snapshot(config, context(count))
        sizes.append(len(json.dumps(shown).encode()))
    assert max(sizes)-min(sizes) < 10  # fixed descriptors, not all references inline
    full = context(1)
    base = len(json.dumps(refs.snapshot(config, full)))
    full["continuing_operations"]["operations"] += [
        {"operation": f"{1000+i:064x}", "status": "BLOCKED", "reason": "New unresolved obligation."}
        for i in range(100)]
    assert len(json.dumps(refs.snapshot(config, full))) > base + 10000


def test_duplicate_reference_and_mixed_representation_refuse(config):
    full = context(1); full["continuing_operations"]["completed"].append(completed())
    with pytest.raises(ValueError, match="DUPLICATE_COMPLETED_REFERENCE"):
        refs.snapshot(config, full)
    shown = refs.snapshot(config, context(1))
    shown["continuing_operations"]["completed"] = [completed()]
    with pytest.raises(ValueError, match="MIXED_COMPLETED"):
        refs.completed_rows(config, {"continuing_context": shown})


def test_selected_native_result_must_match_submitted_discovery(config, monkeypatch):
    from orchestrator import continuing_operations
    row = completed()
    native = {"kind": row["kind"], "result": row["result"]}
    calls = []
    def read(cfg, reference, **kw):
        calls.append((reference,kw))
        return deepcopy(native)
    monkeypatch.setattr(continuing_operations, "read_operation_result", read)
    metadata = refs.operation_metadata(row)
    assert refs.native_result(config, metadata, kinds=("ACCEPT_RESULT",)) == native
    assert calls[-1][1] == {"kinds": ("ACCEPT_RESULT",), "current_review": True}
    bad = deepcopy(metadata); bad["discovery"]["interpretation"]["sha256"] = "f"*64
    with pytest.raises(ValueError, match="COMPLETED_DISCOVERY_CHANGED"):
        refs.native_result(config, bad)
    native["kind"] = "ADOPT_FOLLOWUP"
    with pytest.raises(ValueError, match="COMPLETED_KIND_CHANGED"):
        refs.native_result(config, metadata)


def test_empty_and_later_page_integrity(config):
    ref = refs.save_catalog(config, "completed_operations", "b"*64, [])
    assert refs.read_catalog(config, ref, kind="completed_operations") == []
    ref = refs.save_catalog(config, "completed_operations", "b"*64, [completed(i) for i in range(101)])
    catalog = refs.read(config, ref)
    from pathlib import Path
    page = catalog["pages"][1]
    (Path(config["state"])/"continuing-evidence"/(page["sha256"]+".json")).write_text("{}")
    with pytest.raises(ValueError):
        refs.read_catalog(config, ref, kind="completed_operations")


def test_role_capture_contains_exact_originals_and_membership(config, tmp_path, monkeypatch):
    from orchestrator import scientific_evidence_access as access, continuing_operations
    from orchestrator.hosted_cycle import encoded
    full = context(1)
    native = {"schema": continuing_operations.RESULT_SCHEMA, "source": config["source"],
              "kind": "ACCEPT_RESULT", "status": "COMPLETE", "scientific_acceptance": True,
              "operation": full["continuing_operations"]["completed"][0]["reference"]["operation"],
              "result": completed()["result"]}
    row = full["continuing_operations"]["completed"][0]
    row["reference"]["result_sha256"] = access.sha(encoded(native))
    calls = []
    def original(cfg, ref, **kw):
        calls.append((ref, kw))
        assert ref == row["reference"]
        return deepcopy(native)
    monkeypatch.setattr(continuing_operations, "read_operation_result", original)
    monkeypatch.setattr(continuing_operations, "_saved", lambda path: {"source": config["source"]})
    prior = refs.predecessor(config, {"reviewer_evidence": {"kept": "Exact predecessor scientific observation."},
        "scientific_change_history": {"schema": "authenticated-current-scientific-input/v1", "native_prefixes": {}}})
    packet = {"trigger": "installed-research-request", "reviewer_evidence": prior,
              "continuing_context": refs.snapshot(config, full)}
    base = {"manifest": {"schema": access.SCHEMA, "source": config["source"],
        "task_binding": refs.digest(packet), "request_heads": {}, "records": []}, "payloads": {}}
    capture = refs.capture(base, config, packet)
    records = {v["name"]:v for v in capture["manifest"]["records"]}
    p = prior["prior_packet_evidence"]
    assert capture["payloads"][p["sha256"]] == (
        tmp_path/"continuing-evidence"/(p["sha256"]+".json")).read_bytes()
    name = "operation/"+row["reference"]["operation"]+"/result.original.json"
    assert capture["payloads"][records[name]["sha256"]] == encoded(native)
    assert calls and calls[0][1]["current_review"] is False
    # Capture is historical availability, never a selection or fresh authority.
    assert base["payloads"] == {}
    with pytest.raises(ValueError, match="EXACT_TASK_CAPTURE"):
        refs.capture(base, config, {**packet, "new": "changed"})


def test_status_projection_does_not_hide_unrecognized_or_failed_states(config):
    full = context(1)
    full["continuing_operations"]["operations"] += [
        {"operation": "f"*64, "status": "NEW_UNKNOWN_STATE", "condition": "Needs review."}]
    shown = refs.snapshot(config, full)
    assert full["continuing_operations"]["operations"][-1] in shown["continuing_operations"]["operations"]


def test_complete_status_with_new_condition_stays_literal(config):
    full = context(2)
    full["continuing_operations"]["operations"][0]["linked_replacement"] = {
        "status": "PENDING_REVIEW", "reason": "Explicit adverse condition."}
    full["continuing_operations"]["operations"][1]["reason"] = "Requires deployed verification."
    shown = refs.snapshot(config, full)
    assert shown["continuing_operations"]["operations"] == full["continuing_operations"]["operations"]


def test_historical_capture_source_is_native_request_not_current_or_result(config, monkeypatch):
    from orchestrator import continuing_operations as ops
    row = refs.operation_metadata(completed())
    calls = []
    monkeypatch.setattr(ops, "_saved", lambda path: {"source": "d"*40})
    def original(cfg, reference, **kw):
        calls.append((cfg["source"], kw))
        return {"kind": "ACCEPT_RESULT", "result": completed()["result"]}
    monkeypatch.setattr(ops, "read_operation_result", original)
    refs.historical_result(config, row)
    assert calls == [("d"*40, {"kinds": (), "current_review": False})]
    refs.native_result(config, row)
    assert calls[-1] == (config["source"], {"kinds": (), "current_review": True})

def test_source_upgrade_preserves_readable_original_but_not_relabeling(config):
    ref = refs.save(config, "predecessor_evidence", "b"*64, {"original": "Older source"})
    newer = {**config, "source": "e"*40}
    assert refs.read(newer, ref) == {"original": "Older source"}
    with pytest.raises(ValueError, match="ORIGINAL_BINDING_CHANGED"):
        refs.read(newer, {**ref, "source": newer["source"]})


def test_predecessor_without_bound_current_history_stays_on_legacy_route(config):
    with pytest.raises(ValueError, match="PREDECESSOR_CURRENT_HISTORY_REQUIRED"):
        refs.predecessor(config, {"reviewer_evidence": {"unclassified": "Adverse finding"}})


def test_protocol_view_keeps_blockers_and_leaves_saved_science_intact(config):
    full = context(1)
    shown = refs.snapshot(config, full)
    packet = {"continuing_context": shown}
    protocol = {"subject": "fixture", "bindings": {"fixture": True},
        "decision_path": "/synthetic/decision.json", "decision_sha256": "b"*64}
    value = {"eligible_protocols": [protocol], "protocol_blocks": [
        {"operation": "c"*64, "reason": "ORIGINAL_PROTOCOL_UNAVAILABLE_FOR_FRESH_SELECTION"}],
        "references": [{"original": "Literal scientific evidence"}]}
    original = {"continuing-research-inputs.json": json.dumps(value)}
    display, changed = refs.protocol_presentation(original, packet)
    assert changed
    parsed = json.loads(display["continuing-research-inputs.json"])
    assert parsed["protocol_blocks"] == value["protocol_blocks"]
    assert parsed["references"] == value["references"]
    assert parsed["eligible_protocols"]["eligible_count"] == 1
    assert original["continuing-research-inputs.json"] == json.dumps(value)
    value["eligible_protocols"][0]["decision_sha256"] = "changed"
    with pytest.raises(ValueError):
        refs.protocol_presentation({"continuing-research-inputs.json": json.dumps(value)}, packet)


def test_protocol_source_opt_in_preserves_prior_composition(tmp_path, monkeypatch):
    root = tmp_path/"old-source"
    (root/"orchestrator").mkdir(parents=True)
    path = root/"orchestrator/scientific_context_references.py"
    path.write_text("SCIENTIFIC_CONTEXT_INPUT_VERSION = 1\n")
    monkeypatch.setattr("orchestrator.remote_supervisor.checked_source", lambda path, source: path)
    assert refs.enabled(root, "a"*40)
    assert not refs.enabled(root, "a"*40, protocol=True)
    path.write_text(path.read_text()+"PROTOCOL_CATALOG_INPUT_VERSION = 1\n")
    assert refs.enabled(root, "a"*40, protocol=True)
