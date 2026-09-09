"""Offline fixed-canary native protocol tests; no live MCP, Drive or model call."""
import asyncio
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator import p001_native_return_canary as canary
from orchestrator import p001_native_setup as native
from orchestrator import p001_return_transport as transport
from test_p001_return_transport import FakeDrive


@pytest.fixture
def bound(tmp_path):
    tmp_path.chmod(0o700)
    reserve_root = tmp_path / "reservations"
    reserve_root.mkdir(mode=0o700)
    reservation = transport.reserve_slots(FakeDrive(), {"output_folder_id": "approved-private-folder"},
        reserve_root, "p001-native-canary-fixture", purpose="SYNTHETIC_CANARY")
    packet = transport.prepare_copy(reservation, "/content/drive/MyDrive/research-system",
        runtime_fingerprint="a" * 64, launch_manifest_sha256="b" * 64, max_extracted_bytes=65536)
    dispatch_root = tmp_path / "native"
    dispatch_root.mkdir(mode=0o700)
    return reservation, packet, dispatch_root


class Response:
    def __init__(self, result):
        self.result = result

    def model_dump(self, **kwargs):
        return self.result


def outcome(packet, index):
    if index == 0:
        return {"cpu_only": True, "colab_runtime": True}
    terminal, raw = canary.terminal_expected(packet)
    return {"status": "COPIED_PENDING_ORIGINAL_ID_READBACK", "purpose": "SYNTHETIC_CANARY",
        "zip_bytes": terminal["zip_bytes"], "zip_sha256": terminal["zip_sha256"],
        "terminal_bytes": len(raw), "terminal_sha256": transport.digest(raw),
        "scientific_acceptance": False, "os_exit_independently_observed": False}


class FakeSession:
    def __init__(self, packet, *, fail_at=None, changed_readback=False, failed_stage=None):
        self.packet, self.fail_at = packet, fail_at
        self.changed_readback, self.failed_stage = changed_readback, failed_stage
        self.calls, self.rows = [], []
        self.cells = [{"id": "existing-unexecuted", "source": ["# preserved prior source\n"]}]

    def record(self, direction, rpc):
        self.rows.append({"sequence": len(self.rows), "direction": direction,
            "recorded_at_utc": "2026-09-09T00:00:00+00:00", "rpc": copy.deepcopy(rpc)})

    async def list_tools(self):
        return SimpleNamespace(tools=[SimpleNamespace(name=name) for name in native.TOOL_NAMES])

    async def call_tool(self, name, args, **kwargs):
        index = len(self.calls)
        self.calls.append((name, args))
        self.record("sent", {"jsonrpc": "2.0", "id": index, "method": "tools/call",
            "params": {"name": name, "arguments": args}})
        if index == self.fail_at:
            raise TimeoutError("synthetic lost response")
        if name == "open_colab_browser_connection":
            value = {"result": True}
        elif name == "get_cells":
            value = {"cells": copy.deepcopy(self.cells)}
            if self.changed_readback and len(self.cells) == 3:
                value["cells"][0]["source"] = ["# changed existing cell\n"]
        elif name == "add_code_cell":
            cell_id = "canary-" + str(index)
            self.cells.append({"id": cell_id, "source": [args["code"]]})
            value = {"newCellId": cell_id}
        elif name == "run_code_cell":
            stage = [cell["id"] for cell in self.cells[1:]].index(args["cellId"])
            outputs = [{"output_type": "stream", "text": [json.dumps(outcome(self.packet, stage))]}]
            if stage == self.failed_stage:
                outputs = [{"output_type": "error", "ename": "synthetic"}]
            value = {"outputs": outputs}
        else:
            raise AssertionError(name)
        raw = {"content": [{"type": "text", "text": json.dumps(value)}], "isError": False}
        self.record("received", {"jsonrpc": "2.0", "id": index, "result": raw})
        return Response(raw)

    def raw(self):
        return b"".join(native.encoded(row) + b"\n" for row in self.rows)


def execute(bound, **kwargs):
    reservation, packet, directory = bound
    session = FakeSession(packet, **kwargs)
    asyncio.run(canary.dispatch(reservation, packet, session, directory))
    return session


def test_literal_eight_calls_preserve_native_ids_and_leave_drive_readback_pending(bound):
    reservation, packet, directory = bound
    session = execute(bound)
    result = canary.verify_native(reservation, packet, session.raw())
    assert [name for name, args in session.calls] == canary.TOOL_SEQUENCE
    assert result["actual_tool_calls"] == 8 and result["model_calls"] == 0
    assert result["status"] == "SYNTHETIC_CANARY_COPIED_PENDING_ORIGINAL_ID_READBACK"
    assert result["original_drive_ids_verified"] is False
    assert result["scientific_acceptance"] is False and result["patient_launch_authorized"] is False
    assert result["native_protocol_sha256"] == native.digest(session.raw())
    assert len(list(directory.glob("*.intent.json"))) == 8
    assert "existing-unexecuted" not in [args.get("cellId") for name, args in session.calls if name == "run_code_cell"]


@pytest.mark.parametrize("fail_at", [0, 2, 3, 5, 7])
def test_uncertain_native_request_never_retries_or_invents_a_response(bound, fail_at):
    reservation, packet, directory = bound
    session = FakeSession(packet, fail_at=fail_at)
    with pytest.raises(TimeoutError):
        asyncio.run(canary.dispatch(reservation, packet, session, directory))
    assert len(session.calls) == fail_at + 1
    assert (directory / (str(fail_at).zfill(2) + ".intent.json")).is_file()
    assert not (directory / (str(fail_at).zfill(2) + ".response.json")).exists()
    with pytest.raises(ValueError, match="UNCERTAIN"):
        canary.verify_native(reservation, packet, session.raw())
    replay = FakeSession(packet)
    with pytest.raises(FileExistsError):
        asyncio.run(canary.dispatch(reservation, packet, replay, directory))
    assert replay.calls == []


def test_any_changed_existing_source_blocks_before_execution(bound):
    session = FakeSession(bound[1], changed_readback=True)
    with pytest.raises(ValueError, match="READBACK_CHANGED"):
        asyncio.run(canary.dispatch(*bound[:2], session, bound[2]))
    assert not any(name == "run_code_cell" for name, args in session.calls)


@pytest.mark.parametrize("stage", [0, 1])
def test_remote_error_stops_at_that_stage(bound, stage):
    session = FakeSession(bound[1], failed_stage=stage)
    with pytest.raises(ValueError, match="FAILED_OUTPUT"):
        asyncio.run(canary.dispatch(*bound[:2], session, bound[2]))
    assert sum(name == "run_code_cell" for name, args in session.calls) == stage + 1


@pytest.mark.parametrize("change", ["patient-purpose", "arbitrary-code", "different-reservation", "extra-cell"])
def test_only_exact_synthetic_packet_is_admitted_before_any_call(bound, change):
    reservation, packet, directory = copy.deepcopy(bound)
    if change == "patient-purpose":
        reservation["purpose"] = "PATIENT_RETURN"
    elif change == "arbitrary-code":
        packet["cells"][1] = "print('unapproved source')"
    elif change == "different-reservation":
        reservation["nonce"] = "c" * 64
    else:
        packet["cells"].append("# extra")
    session = FakeSession(packet)
    with pytest.raises(ValueError):
        asyncio.run(canary.dispatch(reservation, packet, session, directory))
    assert session.calls == []


@pytest.mark.parametrize("change", ["trailing-run", "original-cell-run", "duplicate-request-id", "missing-response", "output-read", "wrong-add-source"])
def test_original_protocol_rejects_extra_wrong_or_unbound_calls(bound, change):
    session = execute(bound)
    rows = copy.deepcopy(session.rows)
    sent = [row for row in rows if row["direction"] == "sent"]
    if change == "trailing-run":
        extra = copy.deepcopy(sent[-1])
        extra["rpc"]["id"] = 100
        rows.extend([extra, {"direction": "received", "rpc": {"id": 100, "result": session.rows[-1]["rpc"]["result"]}}])
    elif change == "original-cell-run":
        sent[-1]["rpc"]["params"]["arguments"]["cellId"] = "existing-unexecuted"
    elif change == "duplicate-request-id":
        sent[-1]["rpc"]["id"] = sent[0]["rpc"]["id"]
    elif change == "missing-response":
        rows.pop()
    elif change == "output-read":
        sent[-2]["rpc"]["params"]["arguments"]["includeOutputs"] = True
    else:
        sent[2]["rpc"]["params"]["arguments"]["code"] = "# different"
    for index, row in enumerate(rows):
        row["sequence"] = index
    raw = b"".join(native.encoded(row) + b"\n" for row in rows)
    with pytest.raises(ValueError):
        canary.verify_native(bound[0], bound[1], raw)


@pytest.mark.parametrize("change", ["hash", "payload", "number-as-bool", "duplicate-json-key"])
def test_copy_output_is_exact_small_metadata(bound, change):
    value = outcome(bound[1], 1)
    if change == "hash":
        value["zip_sha256"] = "0" * 64
    elif change == "payload":
        value["patient_payload"] = "must never be accepted"
    elif change == "number-as-bool":
        value["scientific_acceptance"] = 0
    raw = json.dumps(value)
    if change == "duplicate-json-key":
        raw = raw[:-1] + ', "purpose": "SYNTHETIC_CANARY"}'
    with pytest.raises(ValueError):
        canary.validate_stage(bound[1], 1, {"outputs": [{"output_type": "stream", "text": [raw]}]})


def reviewed_fixture(tmp_path, monkeypatch):
    root = tmp_path / "reviewed-source"
    root.mkdir()
    monkeypatch.setattr(canary, "ROOT", root)
    hashes = {}
    for name in canary.REQUIRED_SOURCES:
        path = root / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b"synthetic reviewed source\n")
        hashes[name] = native.digest(path.read_bytes())
    directory = tmp_path / "review"
    directory.mkdir(mode=0o700)
    protocol = b'{"synthetic":"review protocol fixture"}\n'
    (directory / "protocol.jsonl").write_bytes(protocol)
    (directory / "protocol.jsonl").chmod(0o600)
    response = {"subtype": "success", "is_error": False, "structured_output": {
        "verdict": "APPROVE", "scope": canary.SCOPE, "reviewed_commit": "a" * 40}}
    native.write_new(directory / "response.json", response)
    execution = {"returncode": 0, "reviewed_commit": "a" * 40, "requested_model": "claude-fable-5",
        "assistant_message_models": ["claude-fable-5"], "input_file_sha256": hashes,
        "response_sha256": native.digest((directory / "response.json").read_bytes()),
        "protocol_sha256": native.digest(protocol)}
    native.write_new(directory / "execution.json", execution)
    return root, directory, execution


def test_separate_review_requires_scope_actual_family_and_current_input_hashes(tmp_path, monkeypatch):
    root, directory, execution = reviewed_fixture(tmp_path, monkeypatch)
    assert canary.require_review(directory)["scope"] == canary.SCOPE
    path = root / "orchestrator/p001_native_return_canary.py"
    path.write_bytes(b"changed after review")
    with pytest.raises(ValueError, match="INPUT_CHANGED"):
        canary.require_review(directory)


@pytest.mark.parametrize("change", ["setup-scope", "wrong-family", "missing-dependency"])
def test_setup_review_or_wrong_family_cannot_admit_canary(tmp_path, monkeypatch, change):
    _, directory, execution = reviewed_fixture(tmp_path, monkeypatch)
    if change == "setup-scope":
        response = native.read_json((directory / "response.json").read_bytes())
        response["structured_output"]["scope"] = "p001-transparent-setup-native-v1"
        (directory / "response.json").write_bytes(native.encoded(response))
        execution["response_sha256"] = native.digest((directory / "response.json").read_bytes())
    elif change == "wrong-family":
        execution["assistant_message_models"] = ["not-the-requested-family"]
    else:
        execution["input_file_sha256"].pop("orchestrator/p001_return_transport.py")
    (directory / "execution.json").write_bytes(native.encoded(execution))
    with pytest.raises(ValueError, match="EXACT_SOURCE_REVIEW"):
        canary.require_review(directory)


def test_cli_failure_does_not_expose_private_error_text(monkeypatch, capsys):
    import sys
    monkeypatch.setattr(sys, "argv", ["canary", "--reservation", "r", "--packet", "p", "--destination", "d", "--review", "v"])
    async def failed(**kwargs):
        raise OSError("PRIVATE_PATH_OR_TOKEN_MUST_NOT_ESCAPE")
    monkeypatch.setattr(canary, "run", failed)
    with pytest.raises(SystemExit) as error:
        canary.main()
    assert error.value.code == 1
    assert "PRIVATE_PATH_OR_TOKEN" not in capsys.readouterr().out
