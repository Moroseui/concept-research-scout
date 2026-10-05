"""Scientific-role MCP wiring over one immutable authenticated capture.

No model admission, authority, settlement, execution or generic filesystem tool.
The hosted runner creates role-readable root-owned copies of the same capture,
and qualifies an answer only after matching actual tool returns to its journal.
"""
import json
import os
from pathlib import Path

from orchestrator import scientific_evidence_access as evidence

SCIENTIFIC_ROLE_INPUT_VERSION = 1
FORMAL_EVIDENCE_INPUT_VERSION = 1
CURRENT_FORMAL_INPUT_VERSION = 1
LINKED_EVIDENCE_INPUT_VERSION = 1
SERVER = "scientific_evidence"
TOOLS = tuple(item["name"] for item in evidence.definitions())


def require(ok, reason):
    if not ok:
        raise ValueError("SCIENTIFIC_RUNTIME_" + reason)


def profile(value, *, source):
    require(isinstance(value, dict) and set(value) == {"descriptor", "directory", "role"},
            "EXACT_PROFILE_REQUIRED")
    descriptor = value["descriptor"]
    require(isinstance(descriptor, dict) and set(descriptor) == {
        "schema", "source", "task_binding", "manifest_sha256", "record_count"} and
        descriptor["schema"] == evidence.SCHEMA and descriptor["source"] == source,
        "SOURCE_BOUND_CAPTURE_REQUIRED")
    evidence.pin(source, 40)
    evidence.pin(descriptor["task_binding"])
    evidence.pin(descriptor["manifest_sha256"])
    require(type(descriptor["record_count"]) is int and
            1 <= descriptor["record_count"] <= evidence.MAX_RECORDS, "RECORD_BOUND")
    require(value["role"] in ("author", "reviewer", "disposition"), "ROLE_REQUIRED")
    directory = Path(value["directory"])
    require(directory.is_absolute() and ".." not in directory.parts and str(directory) != "/",
            "ABSOLUTE_CAPTURE_REQUIRED")
    return descriptor



def stage_profile(value, *, source, packet_sha256, stage, family):
    """A valid capture for another task or stage is not this call's evidence."""
    descriptor = profile(value, source=source)
    roles = {"continuation": ("author", "astra"), "review": ("reviewer", "claude"),
             "disposition": ("disposition", "astra")}
    require(stage in roles and roles[stage] == (value["role"], family),
            "EXACT_STAGE_ROLE_REQUIRED")
    require(descriptor["task_binding"] == packet_sha256, "EXACT_TASK_CAPTURE_REQUIRED")
    return descriptor



def enabled(root, source, *, formal=False, linked=False, formal_current=False):
    """Immutable source opt-in; historical task receipts keep their original input."""
    import ast
    from orchestrator.remote_supervisor import checked_source
    evidence.pin(source, 40)
    root = checked_source(root, source)
    path = Path(root)/"orchestrator/scientific_evidence_runtime.py"
    if not path.exists():
        return False
    tree = ast.parse(path.read_text())
    require(sum(bool(v) for v in (formal,linked,formal_current)) <= 1, "ONE_SOURCE_PROFILE_REQUIRED")
    name = ("CURRENT_FORMAL_INPUT_VERSION" if formal_current else
            "LINKED_EVIDENCE_INPUT_VERSION" if linked else
            "FORMAL_EVIDENCE_INPUT_VERSION" if formal else "SCIENTIFIC_ROLE_INPUT_VERSION")
    definitions = [n for n in tree.body if isinstance(n, ast.Assign)
        and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
        and n.targets[0].id == name]
    bindings = [n for n in ast.walk(tree) if isinstance(n, ast.Name)
        and n.id == name and isinstance(n.ctx, (ast.Store, ast.Del))]
    if not bindings:
        return False
    require(len(definitions) == len(bindings) == 1
            and isinstance(definitions[0].value, ast.Constant)
            and type(definitions[0].value.value) is int
            and definitions[0].value.value == 1, "SOURCE_PROFILE_CHANGED")
    return True


def packet_kind(packet):
    """Recognize a route, then let its native reader validate every binding."""
    if packet.get("trigger") == "registered-formal-scientific-decision":
        return "formal"
    from orchestrator.scientific_context_references import has_references
    from orchestrator.current_scientific_input import is_current
    require(not has_references(packet) or is_current(packet),
            "CONTEXT_REFERENCE_CURRENT_CAPTURE_REQUIRED")
    return "task" if "scientific_change_history" in packet else None


def _capture_originals(config, packet, source, *, root=None, original_client=None, change_owner=None):
    if packet_kind(packet) == "formal":
        from orchestrator.current_scientific_input import is_current
        if is_current(packet):
            require(enabled(root or config["source_root"],source,formal_current=True),
                    "CURRENT_FORMAL_SOURCE_PROFILE_REQUIRED")
        return evidence.capture_formal_changes(config["change_request_store"], packet, source=source, owner=change_owner)
    capture = evidence.capture_task_changes(config["change_request_store"], packet, source=source, owner=change_owner)
    from orchestrator import current_scientific_input
    if current_scientific_input.is_current(packet):
        require(enabled(root or config["source_root"], source, linked=True),
                "CURRENT_INPUT_NATIVE_RETRIEVAL_REQUIRED")
        capture = evidence.capture_tasks(capture, config, packet, original_client=original_client)
    from orchestrator import scientific_context_references as context_refs
    operations = packet.get("continuing_context", {}).get("continuing_operations")
    if isinstance(operations, dict) and context_refs.enabled(
            root or config["source_root"], source, deferred=True):
        require(type(operations.get("deferred_evidence_version")) is int
                and operations["deferred_evidence_version"] == 1,
                "DEFERRED_CURRENT_SNAPSHOT_REQUIRED")
    if context_refs.has_references(packet):
        require(context_refs.enabled(root or config["source_root"], source),
                "CONTEXT_REFERENCE_SOURCE_PROFILE_REQUIRED")
        capture = context_refs.capture(capture, config, packet, original_client=original_client)
    # Resolve only the fixed investigator/eligibility wake evidence slots.
    # No schema-independent recursive search can widen this task's namespace.
    from orchestrator.disposition_context import _selected_evidence, _dispositions
    selected = _selected_evidence(packet, source)
    if selected is None or not _dispositions(selected, source):
        return capture
    if not enabled(root or config["source_root"], source, linked=True):
        from orchestrator import current_scientific_input
        require(not current_scientific_input.is_current(packet), "CURRENT_INPUT_NATIVE_RETRIEVAL_REQUIRED")
        return capture  # Preserve earlier source profiles and their receipt hashes.
    references = evidence.task_disposition_references(packet, source=source)
    require(callable(original_client), "LINKED_ORIGINAL_READER_REQUIRED")
    capture = evidence.capture_dispositions(capture, config, references, original_client=original_client)
    from orchestrator import current_scientific_input
    if current_scientific_input.is_current(packet):
        current_scientific_input.authenticate_linked_capture(capture, packet, source)
    return capture


def _capture(config, packet, source, *, root=None, original_client=None, change_owner=None):
    capture = _capture_originals(config, packet, source, root=root,
        original_client=original_client, change_owner=change_owner)
    from orchestrator.investigator_eligibility263_reconsideration import capture_original_history
    capture = capture_original_history(config, packet, source, capture, original_client, owner=change_owner)
    from orchestrator.scientific_runtime_prerequisites import verify
    verify(config, packet, source, capture, owner=change_owner)
    from orchestrator import scientific_policy_references as policy_references
    return policy_references.capture(root or config["source_root"], source, packet, capture)


def protected_original_client(broker, *, disposition_lock=None):
    """Read existing replies directly; no self-socket recursion or model dispatch."""
    def read(_socket, operation, body):
        if operation == "stage_status":
            return broker.stage_status(body)
        if operation == "stage_packet":
            return broker.stage_packet(body)
        if operation == "disposition_refusal":
            from orchestrator.protected_investigator import original
            return original(broker, operation, body, disposition_lock=disposition_lock)
        raise ValueError("SCIENTIFIC_RUNTIME_ORIGINAL_READ_ONLY")
    return read


def controller_options(config, root, source, packet, stage, *, original_client=None):
    """Expected provider input, derived from the same native immutable prefix."""
    kind = packet_kind(packet)
    if kind is None:
        return {}
    opted_in = enabled(root, source, formal=True) if kind == "formal" else enabled(root, source)
    if not opted_in:
        return {}
    require(isinstance(config, dict) and config.get("source") == source,
            "CONTROLLER_CONFIG_REQUIRED")
    from orchestrator.handover_runtime import request_broker
    if original_client is None:
        original_client = lambda _socket, operation, body: request_broker(config["broker_socket"], operation, body)
    capture = _capture(config, packet, source, root=root, original_client=original_client)
    return _captured_options(config, source, packet, stage, evidence.describe_capture(capture))


def _captured_options(config, source, packet, stage, descriptor):
    """Internal projection of an already authenticated, invocation-local capture.

    No native retrieval or model inspection is asserted here. The caller must
    authenticate originals in this invocation, before checking either receipt.
    """
    from orchestrator.hosted_cycle import encoded
    require(config.get("source") == source, "CONTROLLER_CONFIG_REQUIRED")
    require(descriptor.get("task_binding") == evidence.sha(encoded(packet)),
            "EXACT_TASK_CAPTURE_REQUIRED")
    roles = {"continuation": "author", "review": "reviewer", "disposition": "disposition"}
    require(stage in roles, "EXACT_STAGE_ROLE_REQUIRED")
    # This expectation is not a filesystem retrieval claim. Only the protected
    # broker writes the actual role cache; paths never enter the provider input.
    directory = Path(config["state"])/"scientific-evidence-expectations"/descriptor["task_binding"]
    value = {"descriptor": descriptor, "directory": str(directory), "role": roles[stage]}
    profile(value, source=source)
    return {"evidence_access": value}


def broker_capture(broker, packet, *, source, folder, stage, disposition_lock=None):
    """Protected configuration selects originals; request/model supplies no path."""
    kind = packet_kind(packet)
    if kind is None:
        return None
    from orchestrator.protected_scientific_jobs import controller_configuration
    config = controller_configuration(broker)
    require(config["source"] == source, "CONTROLLER_SOURCE_CHANGED")
    if kind == "formal" and not enabled(config["source_root"], source, formal=True):
        return None
    require(type(config["controller_uid"]) is int and config["controller_uid"] > 0,
            "SCIENTIFIC_CAPTURE_CONTROLLER_OWNER_REQUIRED")
    # Protected configuration supplies the owner, never the packet/model.
    capture = _capture(config, packet, source, original_client=protected_original_client(broker, disposition_lock=disposition_lock),
                       change_owner=config["controller_uid"])
    directory = Path(folder)/"scientific-evidence-capture"
    descriptor = evidence.write_capture(directory, capture)
    roles = {"continuation": "author", "review": "reviewer", "disposition": "disposition"}
    require(stage in roles, "EXACT_STAGE_ROLE_REQUIRED")
    return {"descriptor": descriptor, "directory": str(directory), "role": roles[stage]}


def prepare(value, *, source, source_root, work, account):
    """Root controller preparation only; no credential or original-store changes."""
    descriptor = profile(value, source=source)
    require(os.getuid() == 0 and account.pw_uid > 0 and account.pw_gid > 0,
            "ROOT_PREPARATION_REQUIRED")
    reader = evidence.Reader(value["directory"], descriptor["manifest_sha256"],
                             source=source, task_binding=descriptor["task_binding"], owner=0)
    require(reader.manifest["record_count"] == descriptor["record_count"], "CAPTURE_COUNT_CHANGED")
    from orchestrator import scientific_policy_references as policy_references
    policy_references.verify_reader(source_root, source, reader)
    work = Path(work); source_root = Path(source_root)
    require(work.is_absolute() and source_root.is_absolute() and
            not work.is_symlink() and work.stat().st_uid == account.pw_uid,
            "ROLE_WORK_DIRECTORY_REQUIRED")
    cache = work / "scientific-evidence"
    journal = work / "scientific-retrieval"
    require(not cache.exists() and not journal.exists(), "FRESH_ROLE_CAPTURE_REQUIRED")
    cache.mkdir(mode=0o700)
    files = {"manifests/" + reader.identity + ".json":
             evidence._regular(reader.directory/"manifests"/(reader.identity+".json"), 0, 1500000)}
    for page in reader.manifest["pages"]:
        name = "indexes/" + page["sha256"] + ".json"
        raw = evidence._regular(reader.directory/name, 0, 1500000)
        require(evidence.sha(raw) == page["sha256"], "INDEX_CHANGED")
        files[name] = raw
    for row in reader.records:
        raw = reader._body(row).encode("utf-8")
        files["objects/" + row["sha256"] + ".txt"] = raw
    for name, raw in files.items():
        target = cache / name
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        os.chown(target, 0, account.pw_gid); target.chmod(0o440)
    for directory in [cache, *(p for p in cache.rglob("*") if p.is_dir())]:
        os.chown(directory, 0, account.pw_gid); directory.chmod(0o550)
    journal.mkdir(mode=0o700); os.chown(journal, account.pw_uid, account.pw_gid)
    launch = ("import sys;sys.path.insert(0," + repr(str(source_root)) + ");"
              "from orchestrator.scientific_evidence_access import main;main()")
    args = ["-B", "-c", launch, "--directory", str(cache),
            "--manifest", descriptor["manifest_sha256"], "--source", source,
            "--task-binding", descriptor["task_binding"], "--journal", str(journal),
            "--role", value["role"], "--owner", "0", "--reader-uid", str(account.pw_uid)]
    return {"schema": "scientific-role-runtime/v1", "descriptor": descriptor,
            "role": value["role"], "uid": account.pw_uid, "gid": account.pw_gid,
            "journal": str(journal), "command": "/usr/bin/python3", "args": args,
            "original_capture": str(reader.directory),
            "meaning": "Same authenticated capture copied for access; not a new native evidence retrieval."}


def client_options(runtime, family):
    """Fixed MCP only. Existing model, timeout, storage and iteration caps stay."""
    spec = {"command": runtime["command"], "args": runtime["args"]}
    if family == "astra":
        # Inline TOML avoids persistent user/project configuration changes.
        settings = "{command=" + json.dumps(spec["command"]) + ",args=" + json.dumps(spec["args"])
        settings += ",enabled=true,required=true,enabled_tools=" + json.dumps(TOOLS)
        settings += ',default_tools_approval_mode="approve",startup_timeout_sec=10,tool_timeout_sec=30}'
        return ["-c", "mcp_servers={" + SERVER + "=" + settings + "}"]
    require(family == "claude", "FAMILY_REQUIRED")
    return ["--mcp-config", json.dumps({"mcpServers": {SERVER: {"type": "stdio", **spec}}}),
            "--allowedTools", ",".join("mcp__" + SERVER + "__" + name for name in TOOLS)]


def _text(content):
    if isinstance(content, str):
        return content
    require(isinstance(content, list) and len(content) == 1 and
            isinstance(content[0], dict) and content[0].get("type") == "text" and
            isinstance(content[0].get("text"), str), "EXACT_TEXT_TOOL_RETURN_REQUIRED")
    return content[0]["text"]


def deliveries(events, family):
    """Extract observed calls; never infer a retrieval from a manifest or prompt."""
    out = []
    if family == "astra":
        for event in events:
            if event.get("type") != "item.completed":
                continue
            item = event.get("item", {})
            if item.get("type") != "mcp_tool_call":
                require(item.get("type") in ("agent_message", "reasoning", "todo_list", "error"),
                        "UNEXPECTED_TOOL_EXECUTION")
                continue
            require(item.get("server") == SERVER and item.get("tool") in TOOLS and
                    item.get("status") in ("completed", "failed") and not item.get("error"),
                    "UNEXPECTED_MCP_CALL")
            result = item.get("result")
            require(isinstance(result, dict) and set(result) <= {"content", "_meta", "structured_content"},
                    "MCP_RESULT_REQUIRED")
            out.append({"id": item["id"], "operation": item["tool"].removeprefix("scientific_evidence_"),
                        "arguments": item["arguments"], "text": _text(result["content"]),
                        "failed": item["status"] == "failed"})
    else:
        require(family == "claude", "FAMILY_REQUIRED")
        calls = {}
        for event in events:
            content = event.get("message", {}).get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if block.get("type") == "tool_use":
                    name = block.get("name")
                    require(name in {"mcp__" + SERVER + "__" + tool for tool in TOOLS},
                            "UNEXPECTED_TOOL_EXECUTION")
                    require(block["id"] not in calls, "DUPLICATE_TOOL_ID")
                    calls[block["id"]] = block
                elif block.get("type") == "tool_result":
                    require(type(block.get("is_error", False)) is bool, "MCP_ERROR_FLAG_REQUIRED")
                    call = calls.pop(block["tool_use_id"], None)
                    require(call is not None, "ORIGINAL_TOOL_CALL_REQUIRED")
                    out.append({"id": call["id"],
                                "operation": call["name"].split("__")[-1].removeprefix("scientific_evidence_"),
                                "arguments": call["input"], "text": _text(block["content"]),
                                "failed": block.get("is_error", False)})
        require(not calls, "UNFINISHED_TOOL_CALL")
    require(len({row["id"] for row in out}) == len(out), "DUPLICATE_TOOL_ID")
    return out


def verify(runtime, events, family):
    journal = Path(runtime["journal"]); uid = runtime["uid"]
    descriptor = runtime["descriptor"]
    expected = {"schema": "scientific-evidence-session/v1", "role": runtime["role"],
                "capture": descriptor["manifest_sha256"], "task_binding": descriptor["task_binding"],
                "max_calls": evidence.MAX_CALLS, "max_return_utf8_bytes": evidence.MAX_RETURN_BYTES}
    raw = evidence._regular(journal/"binding.json", uid, 10000)
    require(json.loads(raw) == expected and not (journal/"pending.json").exists(),
            "BOUND_COMPLETED_JOURNAL_REQUIRED")
    previous = evidence.sha(raw); rows = []; total = 0
    for number, path in enumerate(sorted(journal.glob("call-*.json")), 1):
        require(path.name == f"call-{number:04d}.json", "JOURNAL_SEQUENCE_CHANGED")
        raw = evidence._regular(path, uid, 200000); row = json.loads(raw)
        require(set(row) == {"number", "previous_sha256", "request", "response", "returned_utf8_bytes"}
                and row["number"] == number and row["previous_sha256"] == previous,
                "JOURNAL_CHAIN_CHANGED")
        text = evidence.tool_text(row["response"])
        require(len(text.encode()) == row["returned_utf8_bytes"], "RETURN_SIZE_CHANGED")
        rows.append({"number": number, "request": row["request"], "text": text,
                     "failed": not row["response"]["ok"]})
        total += row["returned_utf8_bytes"]; previous = evidence.sha(raw)
    require(len(rows) <= evidence.MAX_CALLS and total <= evidence.MAX_RETURN_BYTES, "ROLE_BUDGET")
    actual = deliveries(events, family); unmatched = list(rows); matches = []
    for observed in actual:
        request = {"operation": observed["operation"], "arguments": observed["arguments"]}
        match = next((row for row in unmatched if row["request"] == request and
                      row["text"] == observed["text"] and row["failed"] == observed["failed"]), None)
        require(match is not None, "TOOL_RETURN_DIFFERS_FROM_ORIGINAL")
        unmatched.remove(match); matches.append({"tool_id": observed["id"], "journal_number": match["number"]})
    require(not unmatched and len(actual) == len(rows), "UNDELIVERED_OR_UNRECORDED_RETRIEVAL")
    return {"schema": "scientific-role-retrieval-receipt/v1", "role": runtime["role"],
            "uid": uid, "capture": descriptor, "calls": len(rows),
            "successful_calls": sum(not row["failed"] for row in rows),
            "refused_calls": sum(row["failed"] for row in rows), "returned_utf8_bytes": total,
            "journal_head_sha256": previous, "actual_tool_matches": matches,
            "meaning": "Exact observed delivery of the bound immutable capture; no new native fetch or authority."}
