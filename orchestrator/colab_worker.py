"""Private, bounded Claude execution handoff; never changes experiment approvals."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PIN = "1a81c037343598f4e4585153b11d761b87a9ae3a"
SOURCE_PIN = "d6a1184b4378e849213fd887a6f7b103fb1a64d5"
RECEIPT_PIN = '04385ed546189d942f7383b162e28de9e65dac37'
RECEIPT_PATH = "docs/isles-pilot/COLAB_MCP_REMOTE_EXECUTION_20260905.json"
PRIVATE_CONFIG = Path("/home/partho/.local/share/isles-colab-mcp/claude-worker.json")
EXPECTED = "ISLES pilot synthetic execution: 6 * 7 = 42\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git_bytes(pin, path):
    return subprocess.check_output(["git", "show", pin + ":" + path], cwd=ROOT)


def require(condition):
    if not condition: raise ValueError("handoff evidence mismatch")


def verify_handoff():
    raw = git_bytes(RECEIPT_PIN, RECEIPT_PATH)
    receipt = json.loads(raw)
    notebook = receipt["notebook"]
    require(notebook["commit"] == NOTEBOOK_PIN)
    require(notebook["embedded_source_pin"] == SOURCE_PIN)
    require(digest(git_bytes(NOTEBOOK_PIN, notebook["path"])) == notebook["sha256"])
    require(receipt["client"]["name"] == "claude-code")
    require(receipt["connection"]["result"] is True)
    require(receipt["server"]["notebook_tools_available"] is True)
    for key in ("acquisition_cell_executed", "synthetic_write_cell_executed", "separate_retrieval_cell_executed"):
        require(receipt["remote_execution"][key] is True)
    returned = receipt["returned"]
    require(returned == {"text": EXPECTED, "sha256": digest(EXPECTED.encode())})
    transport = json.loads(receipt["transport_cell"]["returned_stream"][0])
    require(transport == {"retrieved_text": EXPECTED, "sha256": returned["sha256"]})
    return {"status": "HANDOFF_RECEIPT_VERIFIED", "receipt_sha256": digest(raw),
            "notebook_sha256": notebook["sha256"], "returned_sha256": returned["sha256"],
            "successful_client": "claude-code", "codex_notebook_discovery_resolved": False,
            "limitations": "Committed worker report; not an independent replay. CPU evidence is no GPU requested and no nvidia-smi, not hardware attestation. Original fd-level console was not returned by the pinned synthetic cells."}


def private_dir(path):
    path = Path(path).absolute()
    if path.is_symlink() or path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("worker evidence must be outside the checkout")
    path.mkdir(mode=0o700, parents=False, exist_ok=False)
    return path


def write_private(path, value):
    with path.open("x", encoding="utf-8") as f:
        os.chmod(path, 0o600)
        f.write(value)


def task_packet():
    report = verify_handoff()
    return {"task": "verify_synthetic_handoff", "role": "execution-worker, not independent reviewer",
            "notebook_pin": NOTEBOOK_PIN, "executable_source_pin": SOURCE_PIN,
            "receipt": json.loads(git_bytes(RECEIPT_PIN, RECEIPT_PATH)),
            "expected_receipt_sha256": report["receipt_sha256"],
            "expected_notebook_sha256": report["notebook_sha256"]}


def invoke_handoff_worker(destination, timeout=300, remote=False):
    """Real subscription invocation proving request/result exchange; no remote replay."""
    destination = private_dir(destination)
    packet = task_packet()
    if remote:
        packet["task"] = "execute_synthetic_colab"
        packet["notebook"] = json.loads(git_bytes(NOTEBOOK_PIN, "campaigns/isles24-pilot/colab/synthetic_execution.ipynb"))
    write_private(destination / "task.json", json.dumps(packet, indent=2))
    prompt = ("You are a bounded execution worker, NOT a reviewer. Inspect the supplied synthetic "
              "handoff report. No tools, browser, patient data, file changes or new execution are needed. "
              "Return only JSON with status HANDOFF_CHECKED, task verify_synthetic_handoff, "
              "receipt_sha256 equal to expected_receipt_sha256, notebook_sha256 equal to "
              "expected_notebook_sha256, and returned_sha256 independently checked from the reported "
              "expected/returned fields. Do not claim a new remote run or scientific approval.\n" + json.dumps(packet))
    if remote:
        prompt = ("You are an execution worker, NOT a reviewer. Perform ONLY this synthetic CPU Colab task. "
                  "Use colab-worker official open_colab_browser_connection. If unavailable or connection "
                  "fails, return status BLOCKED; do not invent success. Use its fresh blank notebook only; "
                  "if it contains any nonempty cells, stop rather than read existing outputs. No Drive, "
                  "patient data, GPU, provisioning, shell tools or credentials. Insert the packet notebook "
                  "cells exactly, read back source without exposing other outputs, and compare exact source "
                  "strings. Execute acquisition, then write, then separately retrieval with run_code_cell. "
                  "Stop on errors. Append packet.receipt.transport_cell.source exactly as the separately "
                  "identified read-only transport cell. Never repeat write to obtain retrieval. Check returned "
                  "text and SHA against the packet. Return status SYNTHETIC_REMOTE_VERIFIED only after all "
                  "three pinned executions and separate transport retrieval succeed. Return task, "
                  "receipt_sha256 (the input receipt hash), notebook_sha256, returned_sha256. Record no "
                  "tokens. This is remote execution, not scientific review. Packet:\n" + json.dumps(packet))
    schema = {"type": "object", "additionalProperties": False,
              "properties": {k: {"type": "string"} for k in
                             ["status", "task", "receipt_sha256", "notebook_sha256", "returned_sha256"]},
              "required": ["status", "task", "receipt_sha256", "notebook_sha256", "returned_sha256"]}
    if remote:
        schema["properties"]["blocker"] = {"type": "string", "enum": ["NONE", "CONNECTION_FAILED", "NOTEBOOK_TOOLS_UNAVAILABLE", "NONEMPTY_NOTEBOOK", "EXECUTION_FAILED", "RETRIEVAL_MISMATCH", "OTHER"]}
        schema["required"].append("blocker")
        prompt += " Return blocker from the schema enum, NONE only on success."
    command = ["claude", "-p", "--model", "claude-fable-5", "--output-format", "stream-json", "--verbose",
               "--mcp-config", str(PRIVATE_CONFIG) if remote else '{"mcpServers":{}}', "--strict-mcp-config", "--tools", "",
               "--permission-mode", "dontAsk", "--max-turns", "3", "--json-schema", json.dumps(schema)]
    if remote:
        command[command.index("--max-turns")+1] = "40"
        command[command.index("--tools")+1] = "ToolSearch"
        command += ["--allowedTools", "mcp__colab-worker__*"]
    # Raw CLI response is private even for synthetic tasks; publish only parsed fixed fields.
    start = time.monotonic()
    launch_failure = None
    with (destination / "stdout.json").open("xb") as out, (destination / "stderr.log").open("xb") as err:
        os.chmod(out.name, 0o600); os.chmod(err.name, 0o600)
        try:
            run = subprocess.run(command, input=prompt.encode(), stdout=out, stderr=err,
                                 cwd=destination, timeout=timeout)
            code = run.returncode
        except subprocess.TimeoutExpired:
            code = None; launch_failure = "WORKER_TIMEOUT"
        except OSError:
            code = None; launch_failure = "WORKER_LAUNCH_FAILED"
    meta = {"task": packet["task"], "returncode": code, "wall_seconds": time.monotonic()-start,
            "remote_replay": remote, "review_approval": False, "status": "WORKER_FAILED",
            "usage": None, "reported_cost_usd": None, "human_intervention_minutes": None,
            "failure_category": launch_failure}
    try:
        events = [json.loads(line) for line in (destination / "stdout.json").read_text().splitlines() if line.strip()]
        if any(not isinstance(e, dict) for e in events): raise ValueError("non-object worker event")
        responses = [e for e in events if e.get("type") == "result"]
        if len(responses) != 1: raise ValueError("missing terminal worker result")
        response = responses[0]
        meta["observed_tool_names"] = sorted({block["name"] for e in events if e.get("type") == "assistant"
                                            for block in e.get("message", {}).get("content", [])
                                            if isinstance(block, dict) and block.get("type") == "tool_use"})
        if code != 0 or response.get("is_error") or response.get("subtype") != "success":
            raise ValueError("incomplete worker response")
        result = response["structured_output"]
        if not isinstance(result, dict): raise ValueError("non-object worker result")
        expected = {"status": "SYNTHETIC_REMOTE_VERIFIED" if remote else "HANDOFF_CHECKED", "task": packet["task"],
                    "receipt_sha256": packet["expected_receipt_sha256"],
                    "notebook_sha256": packet["expected_notebook_sha256"],
                    "returned_sha256": digest(EXPECTED.encode())}
        if remote:
            expected["blocker"] = "NONE"
            blockers = schema["properties"]["blocker"]["enum"][1:]
            if result.get("status") == "BLOCKED" and result.get("blocker") in blockers:
                meta["status"] = "WORKER_BLOCKED"
                meta["blocker"] = result["blocker"]
                raise ValueError("remote worker blocked; no success claimed")
        if result != expected or "claude-fable-5" not in response.get("modelUsage", {}):
            raise ValueError("worker result or model mismatch")
        if remote:
            meta["failure_category"] = "REMOTE_PROTOCOL_REJECTED"
            meta["protocol_verification"] = verify_synthetic_protocol(events)
        meta["failure_category"] = None
        meta.update(status="REMOTE_SYNTHETIC_VALIDATED" if remote else "WORKER_HANDOFF_VALIDATED", result=result, model="claude-fable-5",
                    usage=response.get("usage"), reported_cost_usd=response.get("total_cost_usd"))
    except (ValueError, KeyError, TypeError, AttributeError, IndexError):
        if meta["failure_category"] is None: meta["failure_category"] = "WORKER_RESPONSE_REJECTED"  # Detailed raw evidence stays private; no echoed model text on failures.
    write_private(destination / "validated_status.json", json.dumps(meta, indent=2))
    return meta


def verify_synthetic_protocol(events):
    """Check actual tool exchanges, not just the worker's final claim. Synthetic only."""
    calls = []
    results = {}
    for event in events:
        for block in event.get("message", {}).get("content", []):
            if not isinstance(block, dict): continue
            if event.get("type") == "assistant" and block.get("type") == "tool_use":
                if block.get("name", "").startswith("mcp__colab-worker__"):
                    calls.append(block)
            if event.get("type") == "user" and block.get("type") == "tool_result" and block.get("tool_use_id") in {c["id"] for c in calls}:
                if block.get("is_error"): raise ValueError("MCP error in synthetic attempt")
                content = block.get("content")
                if isinstance(content, list):
                    if any(not isinstance(b, dict) or b.get("type") != "text" for b in content):
                        raise ValueError("unexpected tool-result block shape")
                    content = "".join(b["text"] for b in content)
                if not isinstance(content, str): raise ValueError("unexpected tool-result shape")
                results[block["tool_use_id"]] = json.loads(content)
    connected = [c for c in calls if c["name"].endswith("__open_colab_browser_connection")]
    if len(connected) != 1 or results[connected[0]["id"]] != {"result": True}:
        raise ValueError("missing actual browser connection")
    snapshots = [results[c["id"]]["cells"] for c in calls if c["name"].endswith("__get_cells")]
    if len(snapshots) != 2 or any("".join(c["source"]).strip() for c in snapshots[0]):
        raise ValueError("synthetic notebook was not initially blank or readback missing")
    expected = json.loads(git_bytes(NOTEBOOK_PIN, "campaigns/isles24-pilot/colab/synthetic_execution.ipynb"))["cells"]
    cells = snapshots[1]
    if len(cells) != len(expected) or any("".join(a["source"]) != "".join(b["source"]) or a["cell_type"] != b["cell_type"] for a,b in zip(cells, expected)):
        raise ValueError("pinned cells changed")
    runs = [c for c in calls if c["name"].endswith("__run_code_cell")]
    if len(runs) != 4 or [c["input"]["cellId"] for c in runs[:3]] != [c["id"] for c in cells[1:]]:
        raise ValueError("acquisition, write and separate retrieval sequence differs")
    readback_index = max(i for i,c in enumerate(calls) if c["name"].endswith("__get_cells"))
    if calls.index(runs[0]) <= readback_index:
        raise ValueError("execution preceded source readback")
    pinned_ids = {c["id"] for c in cells}
    if any(c["name"].endswith(("__update_cell", "__delete_cell", "__move_cell")) and c["input"].get("cellId") in pinned_ids for c in calls[readback_index+1:]):
        raise ValueError("pinned cell mutated after readback")
    outputs = [results[c["id"]]["outputs"] for c in runs]
    if any(o.get("output_type") == "error" for group in outputs for o in group):
        raise ValueError("remote cell failed")
    for group in outputs[1:3]:
        if not any("returncode=0" in "".join(o.get("data", {}).get("text/plain", [])) for o in group):
            raise ValueError("pinned subprocess did not return success")
    streams = "".join("".join(o.get("text", [])) for o in outputs[3] if o.get("output_type") == "stream")
    if not streams.strip(): raise ValueError("missing transport stream")
    returned = json.loads(streams.splitlines()[0])
    if returned != {"retrieved_text": EXPECTED, "sha256": digest(EXPECTED.encode())}:
        raise ValueError("actual retrieved bytes/hash mismatch")
    supplements = [c for c in calls if c["name"].endswith("__add_code_cell") and results[c["id"]].get("newCellId") == runs[3]["input"]["cellId"]]
    if len(supplements) != 1: raise ValueError("transport cell provenance missing")
    expected_transport = json.loads(git_bytes(RECEIPT_PIN, RECEIPT_PATH))["transport_cell"]["source"]
    if supplements[0]["input"]["code"].strip() != expected_transport.strip():
        raise ValueError("transport code differs from the read-only pinned supplement")
    return {"status": "ACTUAL_SYNTHETIC_TOOL_EXCHANGES_VERIFIED", "pinned_execution_calls": 3,
            "separate_transport_retrieval_calls": 1, "returned_text": EXPECTED,
            "returned_sha256": returned["sha256"],
            "transport_source_sha256": digest(supplements[0]["input"]["code"].encode())}


def capture_cell(source, log_path):
    """Supplementary transport source. Executes exact pinned bytes in kernel namespace.

    Captures Python streams AND subprocess fd output, including tracebacks, privately.
    Emits only a fixed status and source hash; never emits original console text.
    """
    compile(source, "pinned-scientific-cell", "exec")
    return "\n".join([
        "# Supplementary transport wrapper; original cell source is unchanged.",
        "import os as _cw_os, sys as _cw_sys, contextlib as _cw_context, traceback as _cw_tb",
        "from pathlib import Path as _cw_Path",
        "_cw_log = _cw_Path(" + repr(str(log_path)) + ")",
        "_cw_log.parent.mkdir(parents=True, exist_ok=True, mode=0o700)",
        "if _cw_log.is_symlink(): raise RuntimeError('Unsafe transport destination')",
        "_cw_ok = False",
        "with _cw_log.open('a', buffering=1) as _cw_file:",
        "    _cw_os.chmod(_cw_log, 0o600)",
        "    _cw_sys.stdout.flush(); _cw_sys.stderr.flush()",
        "    _cw_fds = [_cw_os.dup(1), _cw_os.dup(2)]",
        "    try:",
        "        _cw_os.dup2(_cw_file.fileno(), 1); _cw_os.dup2(_cw_file.fileno(), 2)",
        "        with _cw_context.redirect_stdout(_cw_file), _cw_context.redirect_stderr(_cw_file):",
        "            try:",
        "                exec(compile(" + repr(source) + ", 'pinned-scientific-cell', 'exec'), globals())",
        "                _cw_ok = True",
        "            except BaseException:",
        "                _cw_tb.print_exc()",
        "            finally:",
        "                _cw_file.flush()",
        "    finally:",
        "        _cw_os.dup2(_cw_fds[0], 1); _cw_os.dup2(_cw_fds[1], 2)",
        "        for _cw_fd in _cw_fds: _cw_os.close(_cw_fd)",
        "print({'transport_status': 'COMPLETE' if _cw_ok else 'FAILED', 'source_sha256': " + repr(digest(source.encode())) + "})",
        "if not _cw_ok: raise RuntimeError('Pinned cell failed; original evidence retained privately; stop')",
    ])


def prepare_p001(destination):
    """Prepare only. No patient execution is enabled by generating this packet."""
    from orchestrator.campaign_review import verify_receipt
    exp = ROOT / "campaigns/isles24-pilot/experiments/P001"
    verify_receipt(ROOT, exp, json.loads((exp / "review.json").read_text()))
    raw = git_bytes(NOTEBOOK_PIN, "campaigns/isles24-pilot/experiments/P001/colab_P001.ipynb")
    nb = json.loads(raw)
    packet = {"status": "PREPARED_NOT_EXECUTED", "notebook_pin": NOTEBOOK_PIN,
              "source_pin": SOURCE_PIN, "notebook_sha256": digest(raw), "cells": [],
              "gates": ["independent adapter review", "fresh browser CPU connection",
                        "operator Drive authorization", "actual archive or staged-root path"],
              "instructions": "Do not execute until all gates pass. Keep original cells separately and do not run them directly over MCP. Drive cell requires operator authorization. Run supplementary wrappers in order, stopping on any failure. Original runner sibling console and all private checkpoints must be retained. Never expose raw logs/get_cells outputs containing private evidence to models. Transport consoles in /content must be copied privately to Drive before disconnect. Aggregate release requires the existing P001 return validator, not filename filtering alone."}
    for i, cell in enumerate(nb["cells"]):
        source = "".join(cell["source"])
        item = {"index": i, "type": cell["cell_type"], "original_source": source,
                "source_sha256": digest(source.encode())}
        if cell["cell_type"] == "code":
            item["supplementary_transport_source"] = capture_cell(source, f"/content/isles-worker-private/P001-cell-{i}.console.log")
            item["transport_sha256"] = digest(item["supplementary_transport_source"].encode())
        packet["cells"].append(item)
    destination = private_dir(destination)
    write_private(destination / "p001-task.json", json.dumps(packet, indent=2))
    return {"status": packet["status"], "notebook_sha256": packet["notebook_sha256"],
            "original_approval_verified": True, "gates": packet["gates"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["verify-handoff", "worker-handoff", "synthetic-remote", "prepare-p001"])
    ap.add_argument("--private-dir", type=Path)
    args = ap.parse_args()
    if args.mode == "verify-handoff": result = verify_handoff()
    else:
        if args.private_dir is None: ap.error("--private-dir required")
        if args.mode == "synthetic-remote":
            result = invoke_handoff_worker(args.private_dir, timeout=600, remote=True)
        else:
            result = (invoke_handoff_worker if args.mode == "worker-handoff" else prepare_p001)(args.private_dir)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
