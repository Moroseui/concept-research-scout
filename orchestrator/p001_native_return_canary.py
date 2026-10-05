"""One synthetic P001 return canary over native MCP; never a patient dispatcher.

Reuses the existing native journal/decoders and transport renderer. Exactly two
appended cells and eight tool calls are allowed. Original Drive ID readback is a
separate required stage; native completion alone never accepts the canary.
"""
import argparse
import asyncio
import datetime
import json
import os
from pathlib import Path
import stat

from orchestrator import p001_native_setup as native
from orchestrator import p001_return_transport as transport

ROOT = Path(__file__).resolve().parents[1]
SCOPE = "p001-return-native-canary-v1"
REQUIRED_SOURCES = {
    "orchestrator/p001_native_return_canary.py", "tests/test_p001_native_return_canary.py",
    "orchestrator/p001_native_setup.py", "orchestrator/p001_return_transport.py",
    "orchestrator/p001_return_intake.py", "orchestrator/p001_runtime_intake.py",
    "orchestrator/p001_runtime_setup.py", "orchestrator/colab_patient.py",
    "orchestrator/colab_worker.py", "orchestrator/drive_evidence.py",
}
TOOL_SEQUENCE = [
    "open_colab_browser_connection", "get_cells", "add_code_cell", "add_code_cell",
    "get_cells", "run_code_cell", "get_cells", "run_code_cell",
]


def require_review(directory):
    """Separate exact canary review; setup approval cannot authorize this route."""
    directory = Path(directory)
    execution = native.read_json(native.private_file(directory / "execution.json"))
    raw_response = native.private_file(directory / "response.json")
    response = native.read_json(raw_response)
    review = response.get("structured_output", {})
    if (execution.get("returncode") != 0 or response.get("is_error") or response.get("subtype") != "success" or
            review.get("verdict") != "APPROVE" or review.get("scope") != SCOPE or
            review.get("reviewed_commit") != execution.get("reviewed_commit") or
            execution.get("requested_model") != "claude-fable-5" or
            execution.get("assistant_message_models") != ["claude-fable-5"] or
            native.digest(raw_response) != execution.get("response_sha256") or
            native.digest(native.private_file(directory / "protocol.jsonl")) != execution.get("protocol_sha256") or
            not REQUIRED_SOURCES <= set(execution.get("input_file_sha256", {}))):
        raise ValueError("CANARY_EXACT_SOURCE_REVIEW_REQUIRED")
    for name, expected in execution["input_file_sha256"].items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or (ROOT / path).is_symlink():
            raise ValueError("CANARY_REVIEW_INPUT_PATH")
        if native.digest((ROOT / path).read_bytes()) != expected:
            raise ValueError("CANARY_REVIEW_INPUT_CHANGED")
    return {"reviewed_commit": execution["reviewed_commit"],
            "execution_sha256": native.digest(native.private_file(directory / "execution.json")),
            "scope": SCOPE}


def checked_packet(reservation, packet):
    if (reservation.get("purpose") != "SYNTHETIC_CANARY" or
            packet.get("task") != "p001_return_copy" or
            packet.get("authority") != "SYNTHETIC_CANARY_ONLY" or
            packet.get("request", {}).get("purpose") != "SYNTHETIC_CANARY"):
        raise ValueError("CANARY_SYNTHETIC_ONLY")
    transport.verify_packet(reservation, packet)
    if (len(packet["cells"]) != 2 or
            any(not isinstance(source, str) or len(source.encode()) > 131072 for source in packet["cells"])):
        raise ValueError("CANARY_EXACT_TWO_CELLS_REQUIRED")
    return packet


def terminal_expected(packet):
    """The fixed synthetic transport metadata, with no clinical member or payload."""
    request = packet["request"]
    raw = transport.synthetic_zip()
    value = {"schema": "p001-return-canary-terminal/v1", "request_id": request["request_id"],
        "runtime_fingerprint_sha256": request["runtime_fingerprint_sha256"], "worker_status": "SYNTHETIC_CANARY",
        "execution_snapshot": transport.EXECUTION_PIN, "source_pin": transport.SOURCE_PIN,
        "notebook_pin": transport.NOTEBOOK_PIN, "zip_name": "P001-private-return.zip",
        "zip_bytes": len(raw), "zip_sha256": transport.digest(raw),
        "launch_manifest_sha256": request["launch_manifest_sha256"],
        "max_extracted_bytes": request["max_extracted_bytes"]}
    encoded = transport.canonical(value)
    transport.validate_terminal(encoded, request)
    return value, encoded


def validate_stage(packet, index, result):
    if index not in (0, 1) or type(index) is not int:
        raise ValueError("CANARY_STAGE_INDEX")
    if not isinstance(result, dict) or not isinstance(result.get("outputs"), list):
        raise ValueError("CANARY_NATIVE_OUTPUT_REQUIRED")
    parts = []
    for output in result["outputs"]:
        if not isinstance(output, dict) or output.get("output_type") != "stream":
            raise ValueError("CANARY_UNEXPECTED_OR_FAILED_OUTPUT")
        text = output.get("text")
        if isinstance(text, str):
            text = [text]
        if not isinstance(text, list) or any(not isinstance(item, str) for item in text):
            raise ValueError("CANARY_STREAM_SCHEMA")
        parts.extend(text)
    raw = "".join(parts)
    if len(raw.encode()) > 4096:
        raise ValueError("CANARY_OUTPUT_BOUND")
    value = native.read_json(raw)
    if index == 0:
        if value != {"cpu_only": True, "colab_runtime": True} or any(type(item) is not bool for item in value.values()):
            raise ValueError("CANARY_CPU_COLAB_REQUIRED")
    else:
        terminal, encoded = terminal_expected(packet)
        expected = {"status": "COPIED_PENDING_ORIGINAL_ID_READBACK", "purpose": "SYNTHETIC_CANARY",
            "zip_bytes": terminal["zip_bytes"], "zip_sha256": terminal["zip_sha256"],
            "terminal_bytes": len(encoded), "terminal_sha256": transport.digest(encoded),
            "scientific_acceptance": False, "os_exit_independently_observed": False}
        if (value != expected or value.get("scientific_acceptance") is not False or
                value.get("os_exit_independently_observed") is not False):
            raise ValueError("CANARY_FIXED_COPY_RESULT_REQUIRED")
    return {"index": index, "cell_sha256": native.digest(packet["cells"][index].encode()),
            "native_result_sha256": native.digest(native.encoded(result)), "checked_outcome": value}


async def dispatch(reservation, packet, session, directory):
    """Literal eight-call attempt; every original request intent precedes submission."""
    checked_packet(reservation, packet)
    ordinal = 0

    async def call(name, arguments):
        nonlocal ordinal
        if ordinal >= len(TOOL_SEQUENCE) or name != TOOL_SEQUENCE[ordinal]:
            raise ValueError("CANARY_FIXED_TOOL_SEQUENCE")
        number = ordinal
        ordinal += 1
        native.write_new(directory / (str(number).zfill(2) + ".intent.json"),
            {"tool": name, "arguments": arguments, "packet_sha256": native.digest(native.encoded(packet))})
        response = await session.call_tool(name, arguments,
            read_timeout_seconds=datetime.timedelta(seconds=180 if name == "run_code_cell" else 90))
        raw = response.model_dump(mode="json", by_alias=True, exclude_none=True)
        native.write_new(directory / (str(number).zfill(2) + ".response.json"), raw)
        return native.decode_result(name, raw)

    if await call("open_colab_browser_connection", {}) != {"result": True}:
        raise ValueError("CANARY_EXISTING_BROWSER_REQUIRED")
    tools = await session.list_tools()
    if not native.TOOL_NAMES <= {tool.name for tool in tools.tools}:
        raise ValueError("CANARY_CONNECTED_TOOL_SET_REQUIRED")
    initial = native.cells_result(await call("get_cells", {"includeOutputs": False}))
    if len(initial) > 62:
        raise ValueError("CANARY_NOTEBOOK_CELL_BOUND")
    created = []
    for index, source in enumerate(packet["cells"]):
        result = await call("add_code_cell", {"cellIndex": len(initial) + index, "language": "python", "code": source})
        cell_id = result.get("newCellId")
        if not isinstance(cell_id, str) or not cell_id or cell_id in initial or cell_id in created:
            raise ValueError("CANARY_NEW_CELL_ID_REQUIRED")
        created.append(cell_id)
    expected = {**initial, **dict(zip(created, packet["cells"]))}
    outcomes = []
    for index, cell_id in enumerate(created):
        readback = native.cells_result(await call("get_cells", {"includeOutputs": False}))
        if readback != expected or list(readback) != list(expected):
            raise ValueError("CANARY_SOURCE_READBACK_CHANGED")
        outcomes.append(validate_stage(packet, index, await call("run_code_cell", {"cellId": cell_id})))
    return outcomes


def verify_native(reservation, packet, raw):
    """Validate original JSON-RPC identities/readbacks, never a reconstructed transcript."""
    checked_packet(reservation, packet)
    lines = raw.splitlines()
    if (not raw or len(raw) > native.MAX_PROTOCOL or len(lines) > 256 or
            any(len(line) > native.MAX_FRAME for line in lines)):
        raise ValueError("CANARY_PROTOCOL_BOUND")
    requests, responses, calls = {}, {}, []
    pings, ping_responses = set(), set()
    for index, line in enumerate(lines):
        row = native.read_json(line)
        if row.get("sequence") != index or row.get("direction") not in ("sent", "received"):
            raise ValueError("CANARY_PROTOCOL_SEQUENCE")
        rpc = row["rpc"]
        if row["direction"] == "received" and rpc.get("method") == "ping" and "id" in rpc:
            if rpc["id"] in pings or rpc.get("params", {}) != {}:
                raise ValueError("CANARY_UNEXPECTED_SERVER_REQUEST")
            pings.add(rpc["id"])
        elif row["direction"] == "sent" and "id" in rpc and "method" not in rpc:
            if rpc["id"] not in pings or rpc["id"] in ping_responses or rpc.get("result") != {}:
                raise ValueError("CANARY_UNEXPECTED_CLIENT_RESPONSE")
            ping_responses.add(rpc["id"])
        elif row["direction"] == "sent" and "method" in rpc and "id" in rpc:
            if rpc["id"] in requests or rpc["method"] not in ("initialize", "tools/list", "tools/call"):
                raise ValueError("CANARY_DUPLICATE_OR_UNEXPECTED_REQUEST")
            requests[rpc["id"]] = rpc
            if rpc["method"] == "tools/call":
                if set(rpc["params"]) != {"name", "arguments"}:
                    raise ValueError("CANARY_TOOL_ARGUMENT_SCHEMA")
                calls.append((index, rpc))
        elif row["direction"] == "received" and "id" in rpc:
            if ("method" in rpc or rpc["id"] not in requests or rpc["id"] in responses or
                    "error" in rpc or "result" not in rpc):
                raise ValueError("CANARY_RESPONSE_ID_OR_ERROR")
            responses[rpc["id"]] = (index, rpc["result"])
    if pings != ping_responses or any(request_id not in responses for request_id in requests):
        raise ValueError("CANARY_UNCERTAIN_REQUEST_RECONCILE")
    if [rpc["params"]["name"] for _, rpc in calls] != TOOL_SEQUENCE:
        raise ValueError("CANARY_FIXED_TOOL_SEQUENCE")
    initial, expected, created, outcomes = None, None, [], []
    for position, (sent_index, rpc) in enumerate(calls):
        response_index, result = responses[rpc["id"]]
        if response_index <= sent_index or (position + 1 < len(calls) and response_index >= calls[position + 1][0]):
            raise ValueError("CANARY_SERIAL_RESPONSE_ORDER")
        name, arguments = rpc["params"]["name"], rpc["params"]["arguments"]
        value = native.decode_result(name, result)
        if name == "open_colab_browser_connection":
            if arguments != {} or value != {"result": True}:
                raise ValueError("CANARY_EXISTING_BROWSER_REQUIRED")
        elif name == "get_cells":
            if arguments != {"includeOutputs": False}:
                raise ValueError("CANARY_SOURCE_ONLY_READ_REQUIRED")
            observed = native.cells_result(value)
            if initial is None:
                if len(observed) > 62:
                    raise ValueError("CANARY_NOTEBOOK_CELL_BOUND")
                initial = observed
            elif observed != expected or list(observed) != list(expected):
                raise ValueError("CANARY_SOURCE_READBACK_CHANGED")
        elif name == "add_code_cell":
            index = len(created)
            if arguments != {"cellIndex": len(initial) + index, "language": "python", "code": packet["cells"][index]}:
                raise ValueError("CANARY_EXACT_SOURCE_REQUIRED")
            cell_id = value.get("newCellId")
            if not isinstance(cell_id, str) or not cell_id or cell_id in initial or cell_id in created:
                raise ValueError("CANARY_NEW_CELL_ID_REQUIRED")
            created.append(cell_id)
            expected = {**initial, **dict(zip(created, packet["cells"]))}
        else:
            index = len(outcomes)
            if arguments != {"cellId": created[index]}:
                raise ValueError("CANARY_BOUND_RUN_REQUIRED")
            outcomes.append(validate_stage(packet, index, value))
    if len(outcomes) != 2:
        raise ValueError("CANARY_COMPLETE_SEQUENCE_REQUIRED")
    return {"status": "SYNTHETIC_CANARY_COPIED_PENDING_ORIGINAL_ID_READBACK",
        "transport": "NATIVE_MCP_JSONRPC_NOT_MODEL_OUTPUT", "native_protocol_sha256": native.digest(raw),
        "packet_sha256": native.digest(native.encoded(packet)), "slot_binding_sha256": reservation["binding_sha256"],
        "request_id": packet["request"]["request_id"],
        "runtime_fingerprint_sha256": packet["request"]["runtime_fingerprint_sha256"],
        "launch_manifest_sha256": packet["request"]["launch_manifest_sha256"], "stages": outcomes,
        "actual_tool_calls": 8, "model_calls": 0, "patient_launch_authorized": False,
        "scientific_acceptance": False, "original_drive_ids_verified": False, "automatic_retry": False}


async def run(reservation, packet, destination, review):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    reviewed = require_review(review)
    reservation_value = native.read_json(native.private_file(reservation))
    packet_value = checked_packet(reservation_value, native.read_json(native.private_file(packet)))
    config_raw = native.private_file(native.CONFIG)
    if native.digest(config_raw) != native.CONFIG_SHA256:
        raise ValueError("CANARY_EXISTING_MCP_CONFIGURATION_CHANGED")
    config = native.read_json(config_raw)
    if set(config.get("mcpServers", {})) != {"colab-worker"}:
        raise ValueError("CANARY_EXISTING_MCP_CONFIGURATION_CHANGED")
    server = config["mcpServers"]["colab-worker"]
    if server["command"] != native.COMMAND or server.get("args", []) != []:
        raise ValueError("CANARY_EXISTING_MCP_CONFIGURATION_CHANGED")
    destination = Path(destination).absolute()
    if destination.is_relative_to(ROOT.resolve()):
        raise ValueError("CANARY_PRIVATE_DESTINATION_REQUIRED")
    for parent in destination.parents:
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise ValueError("CANARY_PRIVATE_PATH_ANCESTOR")
    info = destination.parent.stat()
    if info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("CANARY_PRIVATE_PARENT_REQUIRED")
    os.umask(0o077)
    destination.mkdir(mode=0o700, exist_ok=False)
    native.write_new(destination / "packet.json", packet_value)
    native.write_new(destination / "execution-intent.json", {"packet_sha256": native.digest(native.encoded(packet_value)),
        "reservation_sha256": native.digest(native.encoded(reservation_value)),
        "client_sha256": native.digest(Path(__file__).read_bytes()), "review": reviewed,
        "configuration_sha256": native.CONFIG_SHA256, "max_wall_seconds": 900,
        "patient_launch_authorized": False, "automatic_retry": False})
    journal = native.Journal(destination / "native-protocol.jsonl")
    try:
        with (destination / "server.stderr.log").open("x") as errors:
            async with asyncio.timeout(900):
                async with stdio_client(StdioServerParameters(command=native.COMMAND, args=[], env=server.get("env")), errlog=errors) as (read, write):
                    async with ClientSession(native.RecordedReceive(read, journal), native.RecordedSend(write, journal),
                            read_timeout_seconds=datetime.timedelta(seconds=90)) as session:
                        await session.initialize()
                        await dispatch(reservation_value, packet_value, session, destination)
        journal.close()
        result = verify_native(reservation_value, packet_value, native.private_file(destination / "native-protocol.jsonl"))
        native.write_new(destination / "verified.json", result)
        return result
    except BaseException as error:
        journal.close()
        native.write_new(destination / "stopped.json", {"status": "NATIVE_CANARY_STOPPED_RECONCILE_ORIGINAL_REQUESTS",
            "error_type": type(error).__name__, "patient_launch_authorized": False, "automatic_retry": False})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("reservation", "packet", "destination", "review"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        result = asyncio.run(run(**vars(args)))
    except BaseException as error:
        print(json.dumps({"status": "NATIVE_CANARY_STOPPED_RECONCILE_ORIGINAL_REQUESTS",
            "error_type": type(error).__name__, "patient_launch_authorized": False}))
        raise SystemExit(1) from None
    print(json.dumps({key: result[key] for key in ("status", "native_protocol_sha256", "actual_tool_calls",
        "model_calls", "patient_launch_authorized", "original_drive_ids_verified")}))


if __name__ == "__main__":
    main()
