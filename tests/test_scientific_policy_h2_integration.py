"""Combined native captures/readers with synthetic prior outcomes, never live science.

Only the initial change-store capture and already-covered admission prerequisites
are fixture seams. H2 sealing/original recovery, completed-result binding,
reference catalogs, source-policy authentication and role journals are native.
These tests do not prove deployed UID access or a real H2 acceptance/adoption.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
from types import SimpleNamespace

import pytest
from orchestrator import continuing_operations as ops
from orchestrator import scientific_authority as authority
from orchestrator import scientific_context_references as refs
from orchestrator import scientific_evidence_access as access
from orchestrator import scientific_evidence_runtime as runtime
from orchestrator import scientific_policy_references as policy
from orchestrator.hosted_cycle import encoded
from test_research_task_authority import setup as base_authority_setup
from test_h2_deferred_evidence import case


@pytest.fixture
def authority_setup(base_authority_setup):
    # Copy authentic current policy before the synthetic formal outcome is sealed.
    config, entry, output = base_authority_setup
    root = Path(config["source_root"])
    original = Path(__file__).resolve().parents[1]
    current = authority.context(original)
    names = {"configs/scientific-operating-context.json", current["binding"]["path"],
             current["policy"]["direction_path"], *current["operating_context"]["documents"]}
    for name in names:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original / name, target)
    (root / "orchestrator/scientific_policy_references.py").write_text(
        "SCIENTIFIC_POLICY_REFERENCE_VERSION = 1\n")
    return config, entry, output


def _completed(case):
    """Synthetic stored acceptance; native request/step/result checks remain real."""
    from orchestrator.scientific_acceptance import STATUS
    core = {key: deepcopy(value) for key, value in case.saved.items()
            if key not in ("identity", "created_at_utc")}
    interpretation = {"task": "7" * 64, "artifact": "round-1/interpretation.md",
                      "sha256": "8" * 64}
    core["operation"] = {"schema": ops.SCHEMA, "operation_id": "synthetic-completed-h2",
                         "kind": "ACCEPT_RESULT", "inputs": {"interpretation": interpretation}}
    identity = ops.digest(core)
    saved = {**core, "identity": identity, "created_at_utc": "2026-09-23T00:00:01Z"}
    folder = ops._directory(case.config) / identity
    folder.mkdir(mode=0o700)
    (folder / "request.json").write_bytes(encoded(saved))
    result = {"status": STATUS, "scientific_acceptance": True, "adoption": False,
              "execution_authorized": False, "model_calls": 0, "interpretation": interpretation,
              "fixture_scope": "Synthetic completed original, not a performed scientific acceptance."}
    last = folder / ("step-" + str(len(ops.STEPS["ACCEPT_RESULT"]) - 1) + ".json")
    last.write_bytes(encoded({"result": result}))
    native = ops._finalize(saved, folder, result)
    ref = {"operation": identity, "result_sha256": access.sha(encoded(native))}
    assert ops.read_operation_result(case.config, ref, current_review=False) == native
    return SimpleNamespace(folder=folder, last=last, native=native, ref=ref)


@pytest.fixture
def combined(case, monkeypatch):
    complete = _completed(case)
    full = {"continuing_operations": ops.status(case.config), "scientific_completions": []}
    shown = refs.snapshot(case.config, full, deferred=True, original_client=case.broker)
    prior = refs.predecessor(case.config, {"reviewer_evidence": {
        "observation": "Synthetic exact predecessor evidence; unresolved limitation stays visible."},
        "scientific_change_history": {"schema": "authenticated-current-scientific-input/v1",
                                      "native_prefixes": {}}})
    packet = {"trigger": "installed-research-request", "reviewer_evidence": prior,
              "continuing_context": shown, "scientific_change_history": {
                  "schema": "authenticated-current-scientific-input/v1", "native_prefixes": {}}}
    base = {"manifest": {"schema": access.SCHEMA, "source": case.source,
        "task_binding": refs.digest(packet), "request_heads": {}, "records": [],
        "semantics": "Synthetic change-store boundary; no new authority."}, "payloads": {}}
    monkeypatch.setattr(access, "capture_task_changes", lambda *a, **kw: deepcopy(base))
    monkeypatch.setattr(runtime, "enabled", lambda *a, **kw: True)
    monkeypatch.setattr(refs, "enabled", lambda *a, **kw: True)
    monkeypatch.setattr("orchestrator.investigator_eligibility263_reconsideration.capture_original_history",
                        lambda config, packet, source, capture, client, **kw: capture)
    prerequisite_calls = []
    def prerequisites(config, actual_packet, source, capture, **kw):
        # The new policy hook must follow the existing original/prerequisite hooks.
        rows = capture["manifest"]["records"]
        assert sum(row["name"].startswith("deferred-operation/") for row in rows) == 12
        assert sum(row["kind"] == "completed_operation_result" for row in rows) == 1
        assert not any(row["kind"] == policy.KIND for row in rows)
        prerequisite_calls.append(access.sha(encoded(capture["manifest"])))
    monkeypatch.setattr("orchestrator.scientific_runtime_prerequisites.verify", prerequisites)
    def capture():
        return runtime._capture(case.config, packet, case.source,
            root=case.config["source_root"], original_client=case.broker)
    return SimpleNamespace(case=case, completed=complete, packet=packet, capture=capture,
                           prerequisite_calls=prerequisite_calls)


def _counts(case):
    return {name: case.transport.calls.count(name) for name in ("admit_server", "model_stage")}


def _state(case):
    return {str(p): p.read_bytes() for p in Path(case.config["state"]).rglob("*") if p.is_file()}


def _reader(combined, tmp_path):
    result = combined.capture()
    folder = tmp_path / "combined-capture"
    descriptor = access.write_capture(folder, result)
    reader = access.Reader(folder, descriptor["manifest_sha256"], source=combined.case.source,
                           task_binding=refs.digest(combined.packet), owner=os.getuid())
    return result, descriptor, reader


@pytest.mark.parametrize("role", ["author", "reviewer", "disposition"])
def test_one_final_capture_serves_all_three_evidence_classes_to_each_role(combined, tmp_path, role):
    case = combined.case
    before, counts = _state(case), _counts(case)
    captured, descriptor, reader = _reader(combined, tmp_path)
    policy.verify_reader(case.config["source_root"], case.source, reader)
    groups = {
        "deferred": [row for row in reader.records if row["name"].startswith("deferred-operation/")],
        "completed": [row for row in reader.records if row["kind"] == "completed_operation_result"],
        "policy": [row for row in reader.records if row["kind"] == policy.KIND],
    }
    assert {key: len(rows) for key, rows in groups.items()} == {"deferred": 12, "completed": 1, "policy": 3}
    assert descriptor["record_count"] == len(reader.records)
    assert captured["manifest"]["task_binding"] == refs.digest(combined.packet)
    session = access.Session(reader, tmp_path / ("journal-" + role), role=role,
                             task_binding=refs.digest(combined.packet))
    for rows in groups.values():
        for row in rows:
            parts, offset = [], 0
            while offset is not None:
                response = session.call("read", {"capture": reader.identity, "name": row["name"],
                    "sha256": row["sha256"], "offset": offset, "characters": access.READ_CHARACTERS})
                assert response["ok"] is True
                parts.append(response["result"]["content"])
                offset = response["result"]["next_offset_characters"]
            assert "".join(parts).encode() == captured["payloads"][row["sha256"]]
    search = session.call("search", {"capture": reader.identity, "cursor": 0,
        "text": "Synthetic unresolved inference"})
    assert search["ok"] and search["result"]["matches"]
    completed_row = groups["completed"][0]
    assert captured["payloads"][completed_row["sha256"]] == encoded(combined.completed.native)
    operation = combined.packet["continuing_context"]["continuing_operations"]["operations"][0]
    assert operation["status"] == "DEFERRED" and operation["deferred_decision"]["rationale"]
    assert combined.capture() == captured
    assert len(combined.prerequisite_calls) == 2
    assert before == _state(case) and counts == _counts(case)
    calls, returned, _ = session._history()
    assert calls > 16 and returned > 40000
    assert calls <= access.MAX_CALLS and returned <= access.MAX_RETURN_BYTES
    assert not (case.folder / "step-1.json").exists()


@pytest.mark.parametrize("damage", ["defer_missing", "completed_changed", "completed_step_changed",
                                   "catalog_missing", "policy_changed"])
def test_combined_capture_refuses_damaged_originals_without_any_new_call(combined, damage):
    case = combined.case
    counts = _counts(case)
    if damage == "defer_missing":
        (case.output / "round-1/review.json").unlink()
    elif damage == "completed_changed":
        path = combined.completed.folder / "result.json"
        path.write_bytes(path.read_bytes() + b" ")
    elif damage == "completed_step_changed":
        combined.completed.last.write_text('{"result":{}}')
    elif damage == "catalog_missing":
        ref = combined.packet["continuing_context"]["continuing_operations"]["completed_catalog"]
        (Path(case.config["state"]) / "continuing-evidence" / (ref["sha256"] + ".json")).unlink()
    else:
        path = Path(case.config["source_root"]) / next(iter(policy.DOCUMENTS))
        path.write_bytes(path.read_bytes() + b"\nChanged policy without binding.\n")
    with pytest.raises((ValueError, OSError)):
        combined.capture()
    assert counts == _counts(case)


@pytest.mark.parametrize("kind", ["deferred", "completed", "policy"])
@pytest.mark.parametrize("damage", ["missing", "changed"])
def test_role_read_rejects_missing_or_changed_bytes_in_each_class(combined, tmp_path, kind, damage):
    counts = _counts(combined.case)
    _, _, reader = _reader(combined, tmp_path)
    if kind == "deferred":
        row = next(row for row in reader.records if row["name"].endswith("formal/judgment.json"))
    else:
        record_kind = "completed_operation_result" if kind == "completed" else policy.KIND
        row = next(row for row in reader.records if row["kind"] == record_kind)
    original = reader.directory / "objects" / (row["sha256"] + ".txt")
    if damage == "missing": original.unlink()
    else:
        original.chmod(0o600); original.write_text("Altered original"); original.chmod(0o400)
    session = access.Session(reader, tmp_path / "damaged-journal", role="reviewer",
                             task_binding=refs.digest(combined.packet))
    result = session.call("read", {"capture": reader.identity, "name": row["name"],
        "sha256": row["sha256"], "offset": 0, "characters": access.READ_CHARACTERS})
    assert result["ok"] is False
    assert counts == _counts(combined.case)
