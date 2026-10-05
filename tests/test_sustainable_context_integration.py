"""Native composition/capture fixtures, never live scientific judgments."""
from copy import deepcopy
import json
import os
from pathlib import Path

import pytest
from orchestrator import scientific_context_references as refs
from orchestrator import scientific_evidence_runtime as runtime, scientific_evidence_access as access
from orchestrator import disposition_context as dc, continuing_operations as ops
from orchestrator.hosted_cycle import encoded
from test_current_input_integration import current_packet
from test_linked_input_integration import integrated
from test_selected_scientific_history import captured, append, write_state
from test_campaign_grounding_presentation import example
from test_disposition_context import SOURCE


def native_operation(config, number, kind="ACCEPT_RESULT"):
    """Real native original readers; explicitly synthetic operation records."""
    interpretation = {"task": f"{number+1:064x}", "artifact": "round-1/interpretation.md", "sha256": "b"*64}
    inputs = ({"interpretation": interpretation} if kind == "ACCEPT_RESULT" else
        {"experiment": "P002", "protocol_id": f"synthetic-protocol-{number}", "prior_protocol": None,
         "artifacts": {key: {"task": interpretation["task"], "artifact": "round-1/proposal.md",
                            "sha256": "b"*64} for key in ops.PROTOCOL_ARTIFACTS}})
    core = {"source": SOURCE, "operation": {"schema": ops.SCHEMA,
        "operation_id": f"synthetic-context-{number}", "kind": kind, "inputs": inputs},
        "selected_by": {"synthetic": True}, "predecessor": {"synthetic": True},
        "actor": {"synthetic": True}, "change_request": {"synthetic": True}}
    identity = ops.digest(core)
    saved = {**core, "identity": identity, "created_at_utc": "2026-09-20T00:00:00Z"}
    folder = ops._directory(config)/identity
    folder.mkdir(parents=True, mode=0o700)
    result = {"interpretation": interpretation, "scientific_acceptance": True,
        "adoption": False, "execution_authorized": False,
        "original_observation": f"SYNTHETIC hidden observation {number}; " + "aggregate evidence "*400}
    if kind == "AUTHORIZE_PROTOCOL":
        result["protocol"] = {"subject": f"synthetic-protocol-{number}", "bindings": {"fixture": number},
            "decision_path": f"/synthetic/formal/protocol-{number}/decision.json", "decision_sha256": "b"*64}
        result["scientific_acceptance"] = False
    native = {"schema": ops.RESULT_SCHEMA, "source": SOURCE, "operation": identity,
        "status": "COMPLETE", "kind": kind, "scientific_acceptance": kind == "ACCEPT_RESULT", "result": result}
    (folder/"request.json").write_bytes(encoded(saved))
    (folder/"result.json").write_bytes(encoded(native))
    final = {k:v for k,v in result.items() if k != "protocol"} if kind == "AUTHORIZE_PROTOCOL" else result
    (folder/f"step-{len(ops.STEPS[kind])-1}.json").write_bytes(encoded({"result": final}))
    return {"reference": {"operation": identity, "result_sha256": refs.digest(native)},
            "kind": kind, "result": result}


def packet_with_catalog(e, config, rows):
    packet = deepcopy(e.campaign); packet.pop("scientific_change_history")
    packet["reviewer_evidence"] = deepcopy(e.current_packet["reviewer_evidence"]["input_evidence"])
    packet["research_catalog_entry"]["change_request"] = {
        "request_id": e.current_app["request_identity"], "applied_event": e.current_app["identity"]}
    observed = {"continuing_operations": {"completed": rows, "operations": [
        {"operation": row["reference"]["operation"], "kind": row["kind"],
         "step": "complete", "position": len(ops.STEPS[row["kind"]]), "status": "COMPLETE", "reason": None}
        for row in rows]}, "scientific_completions": []}
    packet["continuing_context"] = refs.snapshot(config, observed)
    return dc.capture_current_history(config, packet)


@pytest.mark.parametrize("operation_kind", ["ACCEPT_RESULT", "AUTHORIZE_PROTOCOL"])
def test_real_composition_settled_growth_and_role_reads(current_packet, tmp_path, monkeypatch, operation_kind):
    e = current_packet
    config = {**e.config, "state": str(tmp_path/"native-state"),
        "controller_uid": os.getuid(), "controller_gid": os.getgid(), "broker_socket": "synthetic"}
    Path(config["state"]).mkdir(mode=0o700)
    monkeypatch.setattr("orchestrator.disposition_successors.read_result_reference",
                        lambda *a, **kw: deepcopy(e.linked_original))
    monkeypatch.setattr(runtime, "enabled", lambda *a, **kw: True)
    # This fixture exercises the completed-operation catalogue, not the later
    # deferred-operation profile (which has its own required snapshot schema).
    monkeypatch.setattr(refs, "enabled", lambda *a, **kw: not kw.get("deferred", False))
    rows = [native_operation(config, i, operation_kind) for i in range(100)]
    from orchestrator import hosted_campaign as campaign, campaign_disposition as disposition
    measured = []
    for count in (1, 10, 100):
        packet = packet_with_catalog(e, config, rows[:count])
        cap = runtime._capture(config, packet, SOURCE, root=e.root, original_client=lambda *a: None)
        names = {r["name"] for r in cap["manifest"]["records"]}
        assert any(name.endswith("/author.original.txt") for name in names)
        assert any(name.endswith("/reviewer.original.txt") for name in names)
        assert any(name.endswith("/disposition.original.txt") for name in names)
        original_name = "operation/"+rows[count-1]["reference"]["operation"]+"/result.original.json"
        assert original_name in names
        folder = tmp_path/f"capture-{count}"
        descriptor = access.write_capture(folder, cap)
        reader = access.Reader(folder, descriptor["manifest_sha256"], source=SOURCE,
                               task_binding=descriptor["task_binding"], owner=os.getuid())
        row = reader.rows[original_name]
        returned = reader.call("read", {"capture": reader.identity, "name": original_name,
            "sha256": row["sha256"], "offset": 0, "characters": 8192})
        assert f"SYNTHETIC hidden observation {count-1}" in returned["content"]
        supplement = deepcopy(e.supplement)
        if operation_kind == "AUTHORIZE_PROTOCOL":
            supplied = json.loads(supplement["continuing-research-inputs.json"])
            supplied["eligible_protocols"] = [row["result"]["protocol"] for row in rows[:count]]
            supplement["continuing-research-inputs.json"] = json.dumps(supplied, sort_keys=True)
        author_review = campaign.campaign_preflight(e.root, SOURCE, packet,
            supplement=supplement, evidence_config=config)
        third = disposition.preflight(e.root, SOURCE, packet, "Synthetic report only.", evidence_config=config)
        stages = author_review["stages"] + [third]
        measured.append({"count": count, "packet_utf8_bytes": len(encoded(packet)),
            "capture_records": descriptor["record_count"],
            "provider_characters": [stage["characters"] for stage in stages]})
        assert author_review["models"] == author_review["admissions"] == third["admissions"] == 0
        assert "Full original synthetic adverse finding." in str(packet)
    # The backend grows, but initial context does not contain a per-result list.
    for stage in range(3):
        assert max(m["provider_characters"][stage] for m in measured) - min(
            m["provider_characters"][stage] for m in measured) < 100
    assert measured[-1]["capture_records"] > measured[0]["capture_records"] + 90
    # Genuinely unresolved obligations are a separate growth axis and stay literal.
    packet["continuing_context"]["continuing_operations"]["operations"] = [
        {"operation": f"{1000+i:064x}", "status": "BLOCKED",
         "reason": "Synthetic new unresolved scientific obligation; do not treat as settled."}
        for i in range(100)]
    expanded = campaign.campaign_preflight(e.root, SOURCE, packet,
        supplement=supplement, evidence_config=config)
    expanded_third = disposition.preflight(e.root, SOURCE, packet,
        "Synthetic report only.", evidence_config=config)
    unresolved = [row["characters"] for row in expanded["stages"]+[expanded_third]]
    assert all(later > before + 15000 for later, before in zip(
        unresolved, measured[-1]["provider_characters"]))
    print("SYNTHETIC_NATIVE_COMPOSITION_GROWTH=" + json.dumps({
        "operation_kind": operation_kind, "settled": measured,
        "additional_unresolved_100_characters": unresolved}))


@pytest.mark.parametrize("fault", ["head", "count", "index", "namespace"])
def test_inherited_unresolved_history_cannot_be_lost(current_packet, fault):
    e = current_packet
    packet = deepcopy(e.original_input)
    evidence = packet["reviewer_evidence"]["input_evidence"]
    prior = deepcopy(e.current_packet["scientific_change_history"]["native_prefixes"])
    evidence["prior_history_prefixes"] = prior
    dc.capture_current_history(e.config, packet)
    key = next(iter(prior))
    if fault == "head": prior[key]["head_sha256"] = "0"*64
    elif fault == "count": prior[key]["event_count"] += 100
    elif fault == "index": prior[key]["index_sha256"] = "0"*64
    else: prior["0"*64] = prior.pop(key)
    with pytest.raises(ValueError, match="INHERITED_HISTORY"):
        dc.capture_current_history(e.config, packet)

# These existing fixtures construct acceptance/adoption from the real native
# constructors with explicitly synthetic scientific judgments/transport.
from test_current_formal_input import current_formal, prepare as prepare_formal
from test_scientific_adoption import adoption
from test_scientific_acceptance import prepared
from test_semantic_validation_contract import checked_import, validation_import
from orchestrator import formal_decisions as formal, hosted_context as hosted
from orchestrator import scientific_decision as decision


def test_h2_completed_original_retrievable_in_both_formal_runners(current_formal, adoption, monkeypatch, tmp_path):
    e = current_formal
    # The independently constructed H2 fixture has an older/different source.
    # Preserve it as a historical original: never relabel its authority as this
    # new formal request or claim that this composition applies its adoption.
    request = deepcopy(e.formal_request)
    request["evidence"] = {**adoption.request["evidence"],
        "historical-h2-request.original.json": encoded(adoption.request).decode()}
    e.formal_request = request
    e.formal_packet = formal._packet(e.config, request)
    assert "original-result.json" in request["evidence"]
    assert "successor-opposing-review.original.txt" in request["evidence"]
    assert "successor-disposition.original.md" in request["evidence"]
    prepared_input = prepare_formal(e, monkeypatch)
    config = {**e.config, "state": str(tmp_path/"formal-state"), "broker_socket": "synthetic"}
    measurements = []
    for stage, family in [("continuation", "codex"), ("review", "claude")]:
        options = runtime.controller_options(config, e.root, SOURCE, e.formal_packet, stage)
        prompt = prepared_input["body"] if stage == "continuation" else decision.review_body(
            prepared_input["body"], b"Synthetic formal predecessor judgment.")
        body, context = hosted.compose_input(e.root, encoded(e.formal_packet), prompt,
            verified_source=SOURCE, family=family, prepared_prompt=True, **options)
        hosted.measure_input(body, family, stage, task_state=e.formal_packet)
        capture = runtime._capture(config, e.formal_packet, SOURCE, root=e.root)
        rows = {row["name"]: row for row in capture["manifest"]["records"]}
        for name, original in request["evidence"].items():
            row = rows["formal/evidence/"+name]
            assert capture["payloads"][row["sha256"]] == original.encode()
        assert "Full original synthetic adverse finding." in body
        measurements.append({"stage": stage, "characters": len(body), "utf8_bytes": len(body.encode()),
            "tokens": None, "stored_context_utf8_bytes": len(hosted.context_bytes(e.root, context, SOURCE)),
            "original_evidence_files": len(request["evidence"])})
    print("SYNTHETIC_NATIVE_H2_COMPOSITION=" + json.dumps(measurements))
