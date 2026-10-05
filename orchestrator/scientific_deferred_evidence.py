"""Read-only evidence for deferred acceptance/adoption; never retry or apply.

The existing terminal receipt remains unchanged. Both original scientific roles
are authenticated before reasons enter a new snapshot or its bounded reader.
"""
from pathlib import Path
import json

from orchestrator.scientific_context_references import digest, require

SCHEMA = "deferred-formal-operation-evidence/v1"
KINDS = {"ACCEPT_RESULT": ("accept_interpretation", "accept-", "VALIDATED_REVIEWED_INTERPRETATION", "AGENT_ACCEPTED"),
         "ADOPT_FOLLOWUP": ("adopt_followup", "adopt-", "ACCEPTED_RESULT_AND_REVIEWED_SUCCESSOR", "AGENT_ADOPTED")}


def read(config, identity, *, original_client):
    """Authenticate one immutable terminal outcome, including its original source.

    Current policy must still authenticate the original seal. A changed policy
    or unavailable original refuses explicitly; neither grants current authority.
    The callback is confined to original status reads even if a caller supplies
    a transport that also supports model admissions.
    """
    from orchestrator import continuing_operations as ops, formal_decisions as formal
    from orchestrator import scientific_authority as authority
    from orchestrator.remote_supervisor import checked_source
    from orchestrator.scientific_evidence_access import sha
    ops.pin(identity)
    require(callable(original_client), "DEFERRED_ORIGINAL_READER_REQUIRED")
    folder = ops._directory(config) / identity
    saved = ops._saved(folder)
    kind = saved["operation"]["kind"]
    require(kind in KINDS, "DEFERRED_OPERATION_SCOPE")
    raw_result = ops._read(folder / "result.json")
    result = json.loads(raw_result)
    require(set(result) == {"schema", "operation", "source", "kind", "status", "result", "scientific_acceptance"}
            and result["schema"] == ops.RESULT_SCHEMA and result["operation"] == identity
            and result["source"] == saved["source"] and result["kind"] == kind
            and result["status"] == "DEFERRED" and result["scientific_acceptance"] is False,
            "DEFERRED_TERMINAL_RESULT_REQUIRED")
    receipt = result["result"]
    require(isinstance(receipt, dict) and receipt.get("status") == "AGENT_REVIEWED_DEFERRAL",
            "DEFERRED_ORIGINAL_RECEIPT_REQUIRED")
    require(json.loads(ops._read(folder / "step-0.json")) == {"result": receipt}
            and not (folder / "step-1.json").exists(), "DEFERRED_AUTHORITY_STEP_CHANGED")
    prepared = json.loads(ops._read(folder / "prepared.json"))
    require(set(prepared) == {"formal_request"}, "DEFERRED_PREPARED_REQUEST_REQUIRED")
    request = formal.checked_request(prepared["formal_request"])
    action, prefix, before, after = KINDS[kind]
    require(request["source"] == saved["source"] and request["action"] == action
            and request["subject"] == prefix + digest(request["bindings"])[:56]
            and request["transition"] == {"from": before, "to": after}
            and request["change_request"] == saved["change_request"]
            and request["workspace"] is None and request["application"] is None,
            "DEFERRED_OPERATION_REQUEST_CHANGED")
    inputs = saved["operation"]["inputs"]
    bindings = request["bindings"]
    require(bindings.get("source") == saved["source"], "DEFERRED_BINDING_SOURCE_CHANGED")
    if kind == "ACCEPT_RESULT":
        require(bindings.get("interpretation_task") == inputs["interpretation"]["task"]
                and bindings.get("interpretation_sha256") == inputs["interpretation"]["sha256"],
                "DEFERRED_INTERPRETATION_CHANGED")
    else:
        require(bindings.get("selection") == inputs["selection"]
                and bindings.get("acceptance_sha256") == digest(inputs["acceptance"]),
                "DEFERRED_ADOPTION_CHANGED")
    path = Path(receipt.get("decision_path", ""))
    parent = Path(config["state"]).absolute() / "formal-decisions"
    require(path.is_absolute() and path.name == "decision.json" and path.parent.name == "round-1"
            and path.parent.parent.parent == parent
            and path.parent.parent.name in (identity, identity + "-recovery"),
            "DEFERRED_FIXED_DECISION_PATH_REQUIRED")
    output = path.parent.parent
    formal.original_transport(output, request)
    fixed = {"operation/request.json": folder / "request.json",
             "operation/result.json": folder / "result.json",
             "operation/prepared.json": folder / "prepared.json",
             "operation/step-0.json": folder / "step-0.json",
             "formal/authority-transport.json": output / "authority-transport.json"}
    for name in ("decision.json", "judgment.json", "review.json",
                 "scientific_decision.provider-receipt.json", "scientific_decision_review.provider-receipt.json"):
        fixed["formal/" + name] = path.parent / name
    original = {name: ops._read(target) for name, target in fixed.items()}
    require(json.loads(original["operation/request.json"]) == saved
            and json.loads(original["operation/prepared.json"]) == prepared
            and json.loads(original["operation/step-0.json"]) == {"result": receipt},
            "DEFERRED_ORIGINAL_CHANGED_DURING_READ")
    def originals_only(socket, operation, body):
        require(operation == "stage_status", "DEFERRED_READER_FORBIDS_EXECUTION")
        return original_client(socket, operation, body)
    root = checked_source(config["source_root"], config["source"])
    proof = formal.verify_original_decision(root, path, action=action, subject=request["subject"],
        bindings=bindings, source=saved["source"], original_client=originals_only)
    require(proof["decision"] == "DEFER" and proof["transition"] == {"from": before, "to": "DEFERRED"}
            and receipt.get("decision_sha256") == proof["_decision_sha256"]
            and receipt.get("actor") == proof["actor"] and receipt.get("context_sha256") == proof["context_sha256"],
            "DEFERRED_ORIGINAL_DECISION_CHANGED")
    require(sha(original["formal/decision.json"]) == proof["_decision_sha256"],
            "DEFERRED_ORIGINAL_CHANGED_DURING_READ")
    for key in ("author_provenance", "reviewer_provenance"):
        # The seal's native artifact reader checks relative paths and exact hashes.
        original["formal/" + key + ".json"] = authority._artifact(path.parent, proof[key])
    require(all(ops._read(target) == original[name] for name, target in fixed.items()),
            "DEFERRED_ORIGINAL_CHANGED_DURING_READ")
    require(original["operation/result.json"] == raw_result, "DEFERRED_RESULT_CHANGED_DURING_READ")
    descriptor = {"schema": SCHEMA, "source": saved["source"], "kind": kind,
        "reference": {"operation": identity, "result_sha256": sha(raw_result)},
        "formal_request_sha256": digest(request), "decision_sha256": proof["_decision_sha256"],
        "rationale": proof["rationale"], "reconsideration": proof["reconsideration"]}
    return {"descriptor": descriptor, "originals": original}


def attach(config, operations, *, original_client):
    """Keep each unresolved reason literal; complete history remains referenced."""
    require("deferred_evidence_version" not in operations, "DEFERRED_SNAPSHOT_ALREADY_PREPARED")
    operations["deferred_evidence_version"] = 1
    seen = set()
    for row in operations.get("operations", []):
        if row.get("status") != "DEFERRED" or row.get("kind") not in KINDS:
            continue
        identity = row["operation"]
        require(identity not in seen, "DEFERRED_DUPLICATE_OPERATION")
        seen.add(identity)
        require("deferred_decision" not in row, "DEFERRED_SNAPSHOT_ALREADY_PREPARED")
        row["deferred_decision"] = read(config, identity, original_client=original_client)["descriptor"]


def capture(records, payloads, config, operations, *, original_client):
    """Reauthenticate snapshot bindings before exposing exact originals to any role."""
    from orchestrator import scientific_evidence_access as access
    if "deferred_evidence_version" not in operations:
        return  # Earlier immutable snapshots retain their original capture bytes.
    require(type(operations["deferred_evidence_version"]) is int
            and operations["deferred_evidence_version"] == 1, "DEFERRED_PROFILE_CHANGED")
    seen = set()
    for row in operations.get("operations", []):
        expected = row.get("status") == "DEFERRED" and row.get("kind") in KINDS
        require(("deferred_decision" in row) is expected, "DEFERRED_SNAPSHOT_MEMBERSHIP_CHANGED")
        if not expected:
            continue
        identity = row["operation"]
        require(identity not in seen, "DEFERRED_DUPLICATE_OPERATION")
        seen.add(identity)
        native = read(config, identity, original_client=original_client)
        require(row["deferred_decision"] == native["descriptor"], "DEFERRED_SNAPSHOT_BINDING_CHANGED")
        for name, raw in native["originals"].items():
            access._add(records, payloads, "deferred-operation/" + identity + "/" + name,
                "task_packet_original" if name.endswith("authority-transport.json") else "formal_request_evidence",
                raw, {"deferred_decision": {key: value for key, value in native["descriptor"].items()
                    if key not in ("rationale", "reconsideration")},
                      "meaning": "Original reviewed DEFER; evidence only, no acceptance, adoption, eligibility or retry."})
