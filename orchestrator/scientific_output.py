"""Finite provider output contracts; projection changes representation, never judgment.

Historical answers use the existing strict reader. This module is prospective;
it provides no original-output exception, retry, admission or scientific authority.
"""
import hashlib
import json

PROFILE = "scientific-provider-artifacts/v1"


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _object(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


def _string():
    return {"type": "string", "minLength": 1, "maxLength": 30000}


def contract(packet, stage):
    """Select only already-validated scientific artifact workflows, not prompt text."""
    if not isinstance(packet, dict) or stage not in ("continuation", "review", "disposition"):
        raise ValueError("SCIENTIFIC_OUTPUT_PACKET_STAGE_REQUIRED")
    if not ("scientific_decision_artifacts" in packet or "campaign_artifacts" in packet):
        return None
    from orchestrator.protected_handover import model_output_format
    if model_output_format(packet, stage) != "json":
        return None
    if "scientific_decision_artifacts" in packet:
        if stage == "continuation":
            name = "judgment.json"
            value = _object({"context_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "decision": {"type": "string", "enum": ["APPLY", "DEFER"]},
                "rationale": _string(),
                "transition": _object({"from": _string(), "to": _string()}),
                "reconsideration": _string()})
        else:
            name = "review.json"
            value = _object({"verdict": {"type": "string", "enum": ["APPROVE", "REVISE"]},
                "rationale": _string(),
                "judgment_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}})
        kind, properties = "typed-decision", {name: value}
    else:
        from orchestrator.hosted_campaign import MODES
        names = MODES[packet["campaign_artifacts"]["mode"]] if stage == "continuation" else ["review.json"]
        kind, properties = "artifact-strings", {name: _string() for name in names}
    schema = _object(properties)
    return {"profile": PROFILE, "kind": kind, "stage": stage, "schema": schema,
            "schema_sha256": hashlib.sha256(encoded(schema)).hexdigest()}


def validate(value, schema):
    """Validate this closed schema vocabulary locally without a new dependency."""
    import re
    if schema["type"] == "object":
        if not isinstance(value, dict) or set(value) != set(schema["properties"]):
            raise ValueError("SCIENTIFIC_STRUCTURED_OUTPUT_OBJECT_REQUIRED")
        for name, child in schema["properties"].items():
            validate(value[name], child)
    elif schema["type"] == "string":
        if not isinstance(value, str) or not value.strip():
            raise ValueError("SCIENTIFIC_STRUCTURED_OUTPUT_STRING_REQUIRED")
        if (len(value) > schema.get("maxLength", 30000)
                or "enum" in schema and value not in schema["enum"]
                or "pattern" in schema and re.fullmatch(schema["pattern"], value) is None):
            raise ValueError("SCIENTIFIC_STRUCTURED_OUTPUT_VALUE_REQUIRED")
    else:
        raise ValueError("SCIENTIFIC_OUTPUT_SCHEMA_VOCABULARY")


def project(value, selected):
    """Keep typed provider originals separate from existing string-valued artifacts."""
    validate(value, selected["schema"])
    files = ({name: encoded(content).decode() for name, content in value.items()}
             if selected["kind"] == "typed-decision" else value)
    answer = encoded(files).decode()
    from orchestrator.hosted_campaign import artifact_files
    artifact_files(answer, list(selected["schema"]["properties"]))
    if len(answer.encode()) > 80000:
        raise ValueError("SCIENTIFIC_STRUCTURED_OUTPUT_REPLY_BOUND")
    return answer


def loads(raw):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("SCIENTIFIC_OUTPUT_DUPLICATE_JSON_KEY")
            out[key] = value
        return out
    def invalid_constant(value):
        raise ValueError("SCIENTIFIC_OUTPUT_NONFINITE_JSON")
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid_constant)


def retrieval_events(events, selected, value, *, evidence_enabled=False):
    """Account for the CLI's data-only schema emission, never a general tool grant.

    Originals remain intact. Only a paired successful exact StructuredOutput
    emission is omitted from the MCP retrieval matching view. Other calls stay
    visible to the unchanged unexpected-tool rejection.
    """
    from copy import deepcopy
    from orchestrator.scientific_evidence_runtime import SERVER, TOOLS
    allowed_retrieval = {"mcp__"+SERVER+"__"+name for name in TOOLS} if evidence_enabled else set()
    out = deepcopy(events)
    calls = {}
    completed = []
    for event in out:
        if not isinstance(event.get("message"), dict):
            continue
        content = event["message"].get("content", [])
        if not isinstance(content, list):
            continue
        kept = []
        for block in content:
            if not isinstance(block, dict):
                raise ValueError("SCIENTIFIC_STRUCTURED_TOOL_PROTOCOL")
            if block.get("type") == "tool_use" and block.get("name") == "StructuredOutput":
                if selected is None or block.get("id") in calls or completed:
                    raise ValueError("SCIENTIFIC_STRUCTURED_TOOL_SCOPE")
                validate(block.get("input"), selected["schema"])
                if block["input"] != value:
                    raise ValueError("SCIENTIFIC_STRUCTURED_TOOL_OUTPUT_CHANGED")
                calls[block["id"]] = block
            elif block.get("type") == "tool_result" and block.get("tool_use_id") in calls:
                if block.get("is_error", False) is not False:
                    raise ValueError("SCIENTIFIC_STRUCTURED_TOOL_FAILED")
                completed.append(calls.pop(block["tool_use_id"]))
            else:
                if (block.get("type") == "tool_use" and block.get("name") not in allowed_retrieval
                        or block.get("type") == "tool_result" and not evidence_enabled):
                    raise ValueError("SCIENTIFIC_STRUCTURED_UNEXPECTED_TOOL_EXECUTION")
                kept.append(block)
        event["message"]["content"] = kept
    if calls or len(completed) > 1:
        raise ValueError("SCIENTIFIC_STRUCTURED_TOOL_INCOMPLETE")
    return out, {"data_only_tool": "StructuredOutput", "successful_calls": len(completed),
                 "original_events_unchanged": True}


def claude_value(final, selected):
    """The structured field cannot silently discard conflicting final commentary."""
    value = final.get("structured_output")
    validate(value, selected["schema"])
    commentary = final.get("result")
    if commentary not in (None, ""):
        try:
            same = isinstance(commentary, str) and loads(commentary) == value
        except ValueError:
            same = False
        if not same:
            raise ValueError("SCIENTIFIC_STRUCTURED_OUTPUT_COMMENTARY_REQUIRES_RECONCILIATION")
    return value
