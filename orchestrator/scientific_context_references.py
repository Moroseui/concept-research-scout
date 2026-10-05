"""Typed scientific context references in the existing continuing-evidence store.

These records preserve bytes and submission-time membership, never authority.
Full originals stay outside initial model context and enter the existing bounded
scientific evidence reader. Native selection still validates each selected result.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from orchestrator import continuing_research as continuing
from orchestrator.hosted_cycle import encoded

SCHEMA = "scientific-context-reference/v1"
RECORD = "scientific-context-original/v1"
CATALOG = "scientific-context-catalog/v1"
KINDS = frozenset(("predecessor_evidence", "predecessor_context",
                  "completed_operations", "scientific_completions", "catalog_page"))
SCIENTIFIC_CONTEXT_INPUT_VERSION = 1
PROTOCOL_CATALOG_INPUT_VERSION = 1
DEFERRED_OPERATION_INPUT_VERSION = 1
PAGE_SIZE = 100
MAX_RECORDS = 10000  # Same finite scope as the existing scientific evidence reader.


def require(ok, reason):
    if not ok:
        raise ValueError("SCIENTIFIC_CONTEXT_" + reason)


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def _pin(value, length=64):
    from orchestrator.scientific_evidence_access import pin
    return pin(value, length)


def enabled(root, source, *, protocol=False, deferred=False):
    """Only an immutable source with this profile changes newly prepared inputs."""
    import ast
    from orchestrator.remote_supervisor import checked_source
    path = Path(root) / "orchestrator/scientific_context_references.py"
    if not path.exists():
        return False  # Historical source does not implement this representation.
    root = checked_source(root, source)
    tree = ast.parse(path.read_text())
    require(type(protocol) is bool and type(deferred) is bool and not (protocol and deferred), "SOURCE_PROFILE_OPTION")
    name = ("DEFERRED_OPERATION_INPUT_VERSION" if deferred else
            "PROTOCOL_CATALOG_INPUT_VERSION" if protocol else "SCIENTIFIC_CONTEXT_INPUT_VERSION")
    names = [node for node in ast.walk(tree) if isinstance(node, ast.Name)
             and node.id == name
             and isinstance(node.ctx, (ast.Store, ast.Del))]
    definitions = [node for node in tree.body if isinstance(node, ast.Assign)
                   and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                   and node.targets[0].id == name]
    if (protocol or deferred) and not names:
        return False  # d1fc's original composed input remains unchanged.
    require(len(names) == len(definitions) == 1
            and isinstance(definitions[0].value, ast.Constant)
            and type(definitions[0].value.value) is int
            and definitions[0].value.value == 1, "SOURCE_PROFILE_CHANGED")
    return True


def reference(value):
    require(isinstance(value, dict) and set(value) == {
        "schema", "source", "kind", "subject", "sha256", "utf8_bytes"},
        "EXACT_REFERENCE_REQUIRED")
    require(value["schema"] == SCHEMA and value["kind"] in KINDS,
            "REFERENCE_KIND_REQUIRED")
    _pin(value["source"], 40); _pin(value["subject"]); _pin(value["sha256"])
    require(type(value["utf8_bytes"]) is int and 0 < value["utf8_bytes"] <= 750000,
            "REFERENCE_BOUND")
    return value


def save(config, kind, subject, value):
    """Controller-only native intake; stores an original, not a semantic summary."""
    require(kind in KINDS, "REFERENCE_KIND_REQUIRED")
    _pin(config["source"], 40); _pin(subject)
    record = {"schema": RECORD, "source": config["source"], "kind": kind,
              "subject": subject, "value": deepcopy(value)}
    raw = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    # Native intake enforces controller uid, private ownership and the existing bound.
    saved = continuing.preserve_evidence(config, record)
    require(saved["evidence_sha256"] == hashlib.sha256(raw).hexdigest(),
            "NATIVE_INTAKE_BYTES_CHANGED")
    return reference({"schema": SCHEMA, "source": config["source"], "kind": kind,
        "subject": subject, "sha256": saved["evidence_sha256"], "utf8_bytes": len(raw)})


def read(config, ref, *, kind=None, subject=None):
    """Resolve a fixed content address using the native owner/hash/scanner reader."""
    reference(ref)
    # A later source may read a preserved predecessor. Its original source is
    # checked against the native body below; reading confers no current authority.
    require(kind is None or ref["kind"] == kind, "REFERENCE_KIND_CHANGED")
    require(subject is None or ref["subject"] == subject, "REFERENCE_SUBJECT_CHANGED")
    path = Path(config["state"]).absolute() / "continuing-evidence" / (ref["sha256"] + ".json")
    value = continuing.read_evidence(config, {
        "evidence_file": str(path), "evidence_sha256": ref["sha256"]})
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    require(len(raw) == ref["utf8_bytes"] and hashlib.sha256(raw).hexdigest() == ref["sha256"],
            "REFERENCE_BYTES_CHANGED")
    require(isinstance(value, dict) and set(value) == {
        "schema", "source", "kind", "subject", "value"} and value["schema"] == RECORD
        and all(value[key] == ref[key] for key in ("source", "kind", "subject")),
        "ORIGINAL_BINDING_CHANGED")
    return deepcopy(value["value"])


def save_catalog(config, kind, subject, rows):
    """Page a captured selection universe; no growing index is put in the prompt."""
    require(kind in ("completed_operations", "scientific_completions"),
            "CATALOG_KIND_REQUIRED")
    require(isinstance(rows, list) and len(rows) <= MAX_RECORDS, "CATALOG_BOUND")
    pages = [save(config, "catalog_page", subject, {"kind": kind, "rows": rows[offset:offset+PAGE_SIZE]})
             for offset in range(0, len(rows), PAGE_SIZE)]
    catalog = {"schema": CATALOG, "kind": kind, "count": len(rows), "pages": pages}
    return save(config, kind, subject, catalog)


def read_catalog(config, ref, *, kind):
    catalog = read(config, ref, kind=kind)
    require(isinstance(catalog, dict) and set(catalog) == {"schema", "kind", "count", "pages"}
            and catalog["schema"] == CATALOG and catalog["kind"] == kind,
            "CATALOG_BINDING_CHANGED")
    require(type(catalog["count"]) is int and 0 <= catalog["count"] <= MAX_RECORDS
            and isinstance(catalog["pages"], list)
            and len(catalog["pages"]) == (catalog["count"] + PAGE_SIZE - 1) // PAGE_SIZE,
            "CATALOG_BOUND")
    rows = []
    for index, page in enumerate(catalog["pages"]):
        value = read(config, page, kind="catalog_page", subject=ref["subject"])
        expected = min(PAGE_SIZE, catalog["count"] - index * PAGE_SIZE)
        require(isinstance(value, dict) and set(value) == {"kind", "rows"}
                and value["kind"] == kind and isinstance(value["rows"], list)
                and len(value["rows"]) == expected, "CATALOG_PAGE_CHANGED")
        rows.extend(value["rows"])
    return rows


def predecessor(config, packet):
    """Preserve exact predecessor subtrees once; no recursive body copy forward."""
    from orchestrator.current_scientific_input import is_current
    require(is_current(packet), "PREDECESSOR_CURRENT_HISTORY_REQUIRED")
    subject = digest(packet)
    return {
        "prior_history_prefixes": deepcopy(packet["scientific_change_history"]["native_prefixes"]),
        "prior_packet_evidence": save(config, "predecessor_evidence", subject,
                                       packet.get("reviewer_evidence", {})),
        "prior_continuing_context": save(config, "predecessor_context", subject,
                                          packet.get("continuing_context", {}))}


def operation_metadata(row):
    """Discovery metadata only; exact native original remains the authority input."""
    from orchestrator.continuing_operations import operation_reference
    require(isinstance(row, dict) and set(row) == {"reference", "kind", "result"},
            "COMPLETED_ROW_REQUIRED")
    operation_reference(row["reference"])
    result = row["result"]
    require(isinstance(result, dict), "COMPLETED_RESULT_REQUIRED")
    return {"reference": deepcopy(row["reference"]), "kind": row["kind"],
            "discovery": {key: deepcopy(result[key]) for key in ("protocol", "interpretation")
                          if key in result}}


def snapshot(config, full, *, deferred=False, original_client=None):
    """Compact completed history only; all unfinished/refused states stay literal."""
    require(isinstance(full, dict), "CONTINUING_CONTEXT_REQUIRED")
    require(type(deferred) is bool, "DEFERRED_SNAPSHOT_OPTION")
    shown = deepcopy(full)
    operations = shown.get("continuing_operations")
    if not isinstance(operations, dict):
        return shown
    if deferred:
        from orchestrator.scientific_deferred_evidence import attach
        attach(config, operations, original_client=original_client)
    completed = operations.get("completed", [])
    require(isinstance(completed, list), "COMPLETED_ROWS_REQUIRED")
    metadata = [operation_metadata(row) for row in completed]
    identities = [digest(row["reference"]) for row in metadata]
    require(len(set(identities)) == len(identities), "DUPLICATE_COMPLETED_REFERENCE")
    # Submission-time content binding, not a claim of new native retrieval.
    subject = digest(full)
    operations["completed"] = []
    operations["completed_catalog"] = save_catalog(config, "completed_operations", subject, metadata)
    # Only the exact native terminal status shape, with no reason or extra
    # observation, is redundant with the immutable completed catalog. A new
    # condition or linked replacement remains literal even on a COMPLETE row.
    terminal_keys = {"operation", "kind", "step", "position", "status", "reason"}
    members = {row["reference"]["operation"] for row in metadata}
    operations["operations"] = [row for row in operations.get("operations", [])
        if not (isinstance(row, dict) and set(row) == terminal_keys
                and row["status"] == "COMPLETE" and row["step"] == "complete"
                and row["reason"] is None and row["operation"] in members)]
    if "scientific_completions" in shown:
        shown["scientific_completion_catalog"] = save_catalog(
            config, "scientific_completions", subject, shown["scientific_completions"])
        shown["scientific_completions"] = []
    shown["completed_context_notice"] = (
        "Completed originals are independently discoverable in the task-bound capture. "
        "The immutable catalog defines selection membership; it is not scientific acceptance, "
        "adoption or execution authority. Open, deferred, blocked and uncertain states stay literal.")
    return shown


def completed_rows(config, packet):
    """Shared native selection reader for old literal and new snapshot forms."""
    operations = packet.get("continuing_context", {}).get("continuing_operations", {})
    if "completed_catalog" not in operations:
        return deepcopy(operations.get("completed", []))
    require(operations.get("completed") == [], "MIXED_COMPLETED_REPRESENTATION")
    rows = read_catalog(config, operations["completed_catalog"], kind="completed_operations")
    seen = set()
    for row in rows:
        require(isinstance(row, dict) and set(row) == {"reference", "kind", "discovery"},
                "COMPLETED_METADATA_REQUIRED")
        from orchestrator.continuing_operations import operation_reference
        operation_reference(row["reference"])
        identity = digest(row["reference"])
        require(identity not in seen, "DUPLICATE_COMPLETED_REFERENCE")
        seen.add(identity)
        require(isinstance(row["discovery"], dict)
                and set(row["discovery"]) <= {"protocol", "interpretation"},
                "COMPLETED_DISCOVERY_FIELDS")
    return rows


def completion_rows(config, packet):
    context = packet.get("continuing_context", {})
    if "scientific_completion_catalog" not in context:
        return deepcopy(context.get("scientific_completions", []))
    require(context.get("scientific_completions") == [], "MIXED_COMPLETION_REPRESENTATION")
    return read_catalog(config, context["scientific_completion_catalog"], kind="scientific_completions")


def native_result(config, row, *, kinds=(), current_review=True):
    """Validate selected original and its exact submitted metadata, never metadata alone."""
    from orchestrator.continuing_operations import read_operation_result
    original = read_operation_result(config, row["reference"], kinds=kinds,
                                     current_review=current_review)
    require(original["kind"] == row["kind"], "COMPLETED_KIND_CHANGED")
    if "discovery" in row:
        expected = operation_metadata({"reference": row["reference"], "kind": original["kind"],
                                       "result": original["result"]})
        require(expected == row, "COMPLETED_DISCOVERY_CHANGED")
    else:
        require(original["result"] == row["result"], "COMPLETED_ORIGINAL_CHANGED")
    return original


def historical_result(config, row):
    """Authenticate original bytes without converting past completion to current authority.

    The saved, hash-checked request supplies its source. Scientific selection still
    uses native_result with today's source and current_review=True.
    """
    from orchestrator import continuing_operations as ops
    saved = ops._saved(ops._directory(config) / row["reference"]["operation"])
    return native_result({**config, "source": saved["source"]}, row, current_review=False)


def evidence_slots(packet):
    """Only producer-owned predecessor slots, never arbitrary path discovery."""
    if packet.get("trigger") == "installed-research-eligibility":
        value = packet.get("reviewer_evidence", {}).get("input_evidence", {})
    elif packet.get("trigger") == "installed-research-request":
        value = packet.get("reviewer_evidence", {})
    else:
        return []
    return _predecessor_slots(value)


def _predecessor_slots(value):
    if not isinstance(value, dict):
        return []
    rows = []
    for key, kind in (("prior_packet_evidence", "predecessor_evidence"),
                      ("prior_continuing_context", "predecessor_context")):
        ref = value.get(key)
        if isinstance(ref, dict) and ref.get("schema") == SCHEMA:
            reference(ref)
            require(ref["kind"] == kind, "PREDECESSOR_KIND_CHANGED")
            rows.append(ref)
    # A predecessor eligibility packet uses this one fixed evidence wrapper.
    nested = value.get("input_evidence")
    if isinstance(nested, dict):
        for key, kind in (("prior_packet_evidence", "predecessor_evidence"),
                          ("prior_continuing_context", "predecessor_context")):
            ref = nested.get(key)
            if isinstance(ref, dict) and ref.get("schema") == SCHEMA:
                reference(ref)
                require(ref["kind"] == kind, "PREDECESSOR_KIND_CHANGED")
                rows.append(ref)
    return rows


def required_history(packet):
    """Current capture must include every inherited history namespace/prefix."""
    if packet.get("trigger") == "installed-research-eligibility":
        value = packet.get("reviewer_evidence", {}).get("input_evidence", {})
    else:
        value = packet.get("reviewer_evidence", {})
    if not isinstance(value, dict):
        return {}
    found = value.get("prior_history_prefixes", {})
    require(isinstance(found, dict) and len(found) <= 4, "PREDECESSOR_HISTORY_SCOPE")
    for identity, prefix in found.items():
        _pin(identity)
        require(isinstance(prefix, dict) and set(prefix) == {
            "event_count", "head_sha256", "index_sha256"}
            and type(prefix["event_count"]) is int and prefix["event_count"] > 0,
            "PREDECESSOR_HISTORY_PREFIX")
        _pin(prefix["head_sha256"]); _pin(prefix["index_sha256"])
    return deepcopy(found)


def has_references(packet):
    context = packet.get("continuing_context", {})
    return bool(evidence_slots(packet) or
                context.get("continuing_operations", {}).get("completed_catalog") or
                context.get("scientific_completion_catalog"))


def capture(captured, config, packet, *, original_client=None):
    """Append originals to the SAME task-bound reader used by all scientific roles."""
    from orchestrator import scientific_evidence_access as access
    require(captured["manifest"]["source"] == config["source"] and
            captured["manifest"]["task_binding"] == digest(packet), "EXACT_TASK_CAPTURE_REQUIRED")
    result = deepcopy(captured)
    records = {row["name"]: row for row in result["manifest"]["records"]}
    payloads = result["payloads"]
    visited = set()
    def add_reference(ref):
        reference(ref)
        key = ref["sha256"]
        if key in visited:
            return read(config, ref)
        require(len(visited) < MAX_RECORDS, "CAPTURE_BOUND")
        value = read(config, ref)
        visited.add(key)
        original = {"schema": RECORD, "source": ref["source"], "kind": ref["kind"],
                    "subject": ref["subject"], "value": value}
        raw = (json.dumps(original, sort_keys=True, separators=(",", ":")) + "\n").encode()
        require(access.sha(raw) == ref["sha256"] and len(raw) == ref["utf8_bytes"],
                "CAPTURE_ORIGINAL_BYTES_CHANGED")
        access._add(records, payloads, "context/"+key+".json", "continuing_context_original",
                    raw, {"reference": deepcopy(ref), "source": config["source"],
                    "meaning": "Exact native content-addressed original; not scientific authority."})
        if ref["kind"] == "predecessor_evidence":
            for nested in _predecessor_slots(value):
                add_reference(nested)
        elif ref["kind"] == "predecessor_context":
            add_context(value)
        elif ref["kind"] in ("completed_operations", "scientific_completions"):
            # Validate every page/count/binding even when the model reads none.
            read_catalog(config, ref, kind=ref["kind"])
            for page in value["pages"]:
                add_reference(page)
        return value

    def add_context(context):
        operations = context.get("continuing_operations", {})
        from orchestrator.scientific_deferred_evidence import capture as capture_deferred
        capture_deferred(records, payloads, config, operations, original_client=original_client)
        if "completed_catalog" in operations:
            add_reference(operations["completed_catalog"])
            rows = completed_rows(config, {"continuing_context": context})
            for row in rows:
                native = historical_result(config, row)
                require(access.sha(encoded(native)) == row["reference"]["result_sha256"],
                        "OPERATION_ORIGINAL_ENCODING_CHANGED")
                access._add(records, payloads,
                    "operation/"+row["reference"]["operation"]+"/result.original.json",
                    "completed_operation_result", encoded(native),
                    {"reference": deepcopy(row["reference"]), "kind": row["kind"],
                     "discovery": deepcopy(row["discovery"]), "source": native["source"],
                     "meaning": "Native completed original in the selecting snapshot; no adoption or execution inferred."})
        if "scientific_completion_catalog" in context:
            add_reference(context["scientific_completion_catalog"])
            for row in completion_rows(config, {"continuing_context": context}):
                identity = digest(row)
                access._add(records, payloads, "completion/"+identity+".json",
                    "scientific_completion_observation", encoded(row),
                    {"snapshot": deepcopy(context["scientific_completion_catalog"]),
                     "meaning": "Exact captured observation; not a new computation or accepted conclusion."})

    for ref in evidence_slots(packet):
        add_reference(ref)
    add_context(packet.get("continuing_context", {}))
    result["manifest"]["records"] = [records[name] for name in sorted(records)]
    return result


def protocol_presentation(context, packet):
    """Reference a derived eligible-protocol list through its original catalog.

    Native grounding validates the complete prepared context before this call.
    All failed/currently unavailable protocols stay literal in protocol_blocks.
    This changes provider display only, not saved pipeline inputs or validation.
    """
    operations = packet.get("continuing_context", {}).get("continuing_operations", {})
    catalog = operations.get("completed_catalog")
    if catalog is None:
        return context, False
    reference(catalog)
    require(catalog["kind"] == "completed_operations", "PROTOCOL_CATALOG_REQUIRED")
    raw = context.get("continuing-research-inputs.json")
    require(isinstance(raw, str), "PROTOCOL_SUPPLEMENT_REQUIRED")
    value = json.loads(raw)
    if "eligible_protocols" not in value:
        return context, False
    protocols = value["eligible_protocols"]
    require(isinstance(protocols, list) and isinstance(value.get("protocol_blocks"), list),
            "PROTOCOL_LIST_REQUIRED")
    from orchestrator.continuing_research import protocol_descriptor
    for protocol in protocols:
        protocol_descriptor(protocol)
    # An empty list is already smaller and says plainly that none were supplied.
    if not protocols:
        return context, False
    value["eligible_protocols"] = {
        "schema": "retrievable-protocol-candidates/v1",
        "catalog": deepcopy(catalog),
        "eligible_count": len(protocols),
        "original_list_sha256": digest(protocols),
        "original_list_utf8_bytes": len(encoded(protocols)),
        "discovery": "List completed_operation_result records; inspect AUTHORIZE_PROTOCOL "
            "originals and their discovery.protocol descriptors. Exclude the exact operation IDs "
            "in the literal protocol_blocks list. Duplicate descriptors retain original provenance.",
        "authority": "Snapshot candidates only. Native selection revalidates the chosen original "
            "protocol and current authority; availability is not permission or scientific equivalence."}
    shown = deepcopy(context)
    shown["continuing-research-inputs.json"] = json.dumps(value, sort_keys=True)
    return shown, True
