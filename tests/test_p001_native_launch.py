"""Offline native launch tests. No Colab, models, patient files or live APIs."""
import asyncio
import ast
import copy
import inspect
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator import p001_native_launch as launch
from orchestrator import p001_native_setup as native
from orchestrator import p001_runtime_setup as setup
from orchestrator import colab_patient
from orchestrator import p001_return_transport as transport
from test_p001_runtime_setup import inputs, make_packet, environment
from test_p001_return_transport import FakeDrive
from test_p001_native_return_canary import FakeSession as CanarySession, reviewed_fixture


def authority(packet):
    return {"schema": "p001-exact-native-launch-approval/v1", "status": "OPERATOR_APPROVED",
        "core_manifest_sha256": packet["core_manifest_sha256"], "patient_launch": True,
        "derived_return_transfer_206_members": True, "combined_transfer_cap": transport.TRANSFER_CAP,
        "max_extracted_bytes": packet["core"]["max_extracted_bytes"],
        "private_validation_destination": packet["core"]["private_validation_destination"],
        "raw_or_staged_input_transfer": False}


@pytest.fixture
def bound(tmp_path, monkeypatch, inputs):
    tmp_path.chmod(0o700)
    monkeypatch.setattr(colab_patient, "require_patient_review", lambda: "465a0c3b1f2e8486a13e68dfd2179b3bfd16840d")
    frozen = colab_patient.execution_packet(launch.intake.ARCHIVE)
    assert native.digest(native.encoded(frozen)) == launch.FROZEN_PACKET_SHA
    monkeypatch.setattr(launch, "frozen_packet", lambda snapshot: copy.deepcopy(frozen))
    monkeypatch.setattr(launch, "require_review", lambda directory: {"scope": launch.SCOPE})
    setup_packet = make_packet(inputs)
    env = environment()
    setup_receipt = {"status": "SOURCE_DEPENDENCIES_AND_DEFAULT_CHILD_ENVIRONMENT_VERIFIED",
        "packet_sha256": native.digest(native.encoded(setup_packet)),
        "binding_sha256": setup_packet["request"]["binding_sha256"],
        "runtime_fingerprint_sha256": "a" * 64, "environment": env,
        "environment_sha256": native.digest(native.encoded(env)), "scientific_acceptance": False}
    reservations = tmp_path / "slots"
    reservations.mkdir(mode=0o700)
    client = FakeDrive()
    config = {"output_folder_id": "approved-private-folder"}
    canary_reservation = transport.reserve_slots(client, config, reservations, "synthetic-canary", purpose="SYNTHETIC_CANARY")
    reservation = transport.reserve_slots(client, config, reservations, "patient-return", purpose="PATIENT_RETURN")
    canary_packet = transport.prepare_copy(canary_reservation, "/content/drive/MyDrive/research-system",
        runtime_fingerprint="a" * 64, launch_manifest_sha256="b" * 64, max_extracted_bytes=65536)
    canary_native = {"status": "SYNTHETIC_CANARY_COPIED_PENDING_ORIGINAL_ID_READBACK",
        "transport": "NATIVE_MCP_JSONRPC_NOT_MODEL_OUTPUT", "runtime_fingerprint_sha256": "a" * 64,
        "actual_tool_calls": 8, "model_calls": 0, "slot_binding_sha256": canary_reservation["binding_sha256"],
        "launch_manifest_sha256": "b" * 64, "packet_sha256": native.digest(native.encoded(canary_packet))}
    canary_collection = {"status": "SYNTHETIC_ORIGINAL_IDS_AND_BYTES_VERIFIED", "purpose": "SYNTHETIC_CANARY",
        "slot_binding_sha256": canary_reservation["binding_sha256"], "launch_manifest_sha256": "b" * 64,
        "zip_sha256": native.digest(transport.synthetic_zip()), "originals_preserved": True, "scientific_acceptance": False}
    args = (Path("/synthetic/frozen"), setup_packet, setup_receipt, reservation,
        canary_native, canary_collection, canary_reservation, canary_packet)
    kwargs = dict(request_id="p001-launch-fixture", mounted_folder="/content/drive/MyDrive/research-system",
        max_extracted_bytes=64 * 1024 * 1024, private_validation_destination=str(tmp_path / "private-validation"))
    packet = launch.prepare(*args, **kwargs)
    directory = tmp_path / "native"
    directory.mkdir(mode=0o700)
    return packet, directory, args, kwargs


def outcome(packet, stage):
    if stage == 0:
        return json.dumps({"cpu_only": True, "colab_runtime": True})
    pid = 12345
    value = {"status": "DISPATCHED_PENDING_COMPLETION_RECONCILIATION",
        "core_manifest_sha256": packet["core_manifest_sha256"], "original_pid": pid,
        "process_observation": {"state": "NOT_VISIBLE_OR_NOT_MATCHING", "start_ticks": None},
        "parameters_sha256": launch.PARAMETERS_SHA, "process_sha256": native.digest(json.dumps({"pid": pid}).encode()),
        "child_source_sha256": launch.CHILD_SHA,
        "runtime_fingerprint_sha256": packet["core"]["runtime_guard"]["runtime_fingerprint_sha256"],
        "scientific_acceptance": False, "completion_observed": False,
        "os_exit_independently_observed": False, "automatic_retry": False}
    return repr({"transport_status": "COMPLETE", "source_sha256": launch.LAUNCH_SHA}) + "\n" + json.dumps(value)


class FakeSession(CanarySession):
    async def call_tool(self, name, args, **kwargs):
        response = await super().call_tool(name, args, **kwargs)
        if name == "run_code_cell":
            stage = [cell["id"] for cell in self.cells[1:]].index(args["cellId"])
            value = native.decode_result(name, response.result)
            if stage != self.failed_stage:
                value["outputs"] = [{"output_type": "stream", "text": [outcome(self.packet, stage)]}]
            response.result = {"content": [{"type": "text", "text": json.dumps(value)}], "isError": False}
            self.rows[-1]["rpc"]["result"] = copy.deepcopy(response.result)
        return response


@pytest.fixture(autouse=True)
def fake_parent_outcome(monkeypatch):
    # Parent protocol fixture otherwise attempts canary-specific packet decoding.
    monkeypatch.setattr("test_p001_native_return_canary.outcome", lambda packet, index: {})


def execute(bound, **kwargs):
    packet, directory, _, _ = bound
    session = FakeSession(packet, **kwargs)
    asyncio.run(launch.dispatch(packet, session, directory, approval=authority(packet), review="fixture"))
    return session


def test_fixed_frozen_bytes_survive_sorted_packet_reload_and_remain_unauthorized(bound):
    packet = bound[0]
    reloaded = native.read_json(native.encoded(packet))
    assert launch.checked_packet(reloaded) == packet
    assert packet["launch_authorized"] is False and packet["derived_transfer_authorized"] is False
    frozen = packet["frozen_packet"]
    assert native.digest(frozen["cells"][1].encode()) == launch.WRAPPER_SHA
    assert native.digest(frozen["launch_source"].encode()) == launch.LAUNCH_SHA
    assert repr(frozen["cells"][1]) in packet["cells"][1]
    child = colab_patient.child_script(frozen["original_notebook"], frozen["parameters"])
    # child string serializes insertion order; derive original from frozen launcher.
    original_assignments = [n for n in ast.walk(ast.parse(frozen["launch_source"]))
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "params" for t in n.targets)]
    original_params = ast.literal_eval(original_assignments[0].value)
    assert native.digest(json.dumps(original_params).encode()) == launch.PARAMETERS_SHA
    assert native.digest(colab_patient.child_script(frozen["original_notebook"], original_params).encode()) == launch.CHILD_SHA
    assert json.dumps(reloaded["frozen_packet"]["parameters"]).encode() != json.dumps(original_params).encode()
    assert packet["cells"][1].rindex("fresh_guard(core,") < packet["cells"][1].rindex("claim_launch(core, manifest_sha)")
    for cell in packet["cells"]:
        compile(cell, "fixed-p001-launch-test", "exec")


def test_literal_eight_calls_observe_only_dispatch_not_completion(bound):
    session = execute(bound)
    result = launch.verify_native(bound[0], session.raw())
    assert [name for name, args in session.calls] == launch.TOOL_SEQUENCE
    assert result["actual_tool_calls"] == 8 and result["model_calls"] == 0
    assert result["status"] == "DISPATCHED_PENDING_COMPLETION_RECONCILIATION"
    assert result["completion_observed"] is False and result["scientific_acceptance"] is False
    assert result["os_exit_independently_observed"] is False
    assert not any(args.get("cellId") == "existing-unexecuted" for name, args in session.calls)


@pytest.mark.parametrize("field,value", [
    ("patient_launch", False), ("derived_return_transfer_206_members", False),
    ("core_manifest_sha256", "0" * 64), ("combined_transfer_cap", 2**30),
    ("raw_or_staged_input_transfer", True), ("patient_launch", 1),
    ("private_validation_destination", "/another/private-return"),
])
def test_exact_launch_and_derived_transfer_authority_before_any_call(bound, field, value):
    packet = bound[0]
    approval = authority(packet)
    approval[field] = value
    session = FakeSession(packet)
    with pytest.raises(ValueError, match="APPROVAL_REQUIRED"):
        asyncio.run(launch.dispatch(packet, session, bound[1], approval=approval, review="fixture"))
    assert session.calls == []


def test_missing_source_review_blocks_before_any_call(bound, monkeypatch):
    monkeypatch.setattr(launch, "require_review", lambda directory: (_ for _ in ()).throw(ValueError("source review")))
    session = FakeSession(bound[0])
    with pytest.raises(ValueError, match="source review"):
        asyncio.run(launch.dispatch(bound[0], session, bound[1], approval=authority(bound[0]), review="fixture"))
    assert session.calls == []


@pytest.mark.parametrize("fail_at", [0, 2, 5, 7])
def test_lost_response_preserved_without_automatic_retry(bound, fail_at):
    session = FakeSession(bound[0], fail_at=fail_at)
    with pytest.raises(TimeoutError):
        asyncio.run(launch.dispatch(bound[0], session, bound[1], approval=authority(bound[0]), review="fixture"))
    assert len(session.calls) == fail_at + 1
    assert (bound[1] / (str(fail_at).zfill(2) + ".intent.json")).is_file()
    assert not (bound[1] / (str(fail_at).zfill(2) + ".response.json")).exists()
    with pytest.raises(ValueError, match="UNCERTAIN"):
        launch.verify_native(bound[0], session.raw())
    repeat = FakeSession(bound[0])
    with pytest.raises(FileExistsError):
        asyncio.run(launch.dispatch(bound[0], repeat, bound[1], approval=authority(bound[0]), review="fixture"))
    assert repeat.calls == []


@pytest.mark.parametrize("change", ["existing-source", "extra-run", "wrong-cell", "missing-response", "duplicate-request"])
def test_source_readback_and_original_native_request_ids_fail_closed(bound, change):
    if change == "existing-source":
        session = FakeSession(bound[0], changed_readback=True)
        with pytest.raises(ValueError, match="READBACK_CHANGED"):
            asyncio.run(launch.dispatch(bound[0], session, bound[1], approval=authority(bound[0]), review="fixture"))
        assert not any(name == "run_code_cell" for name, args in session.calls)
        return
    session = execute(bound)
    rows = copy.deepcopy(session.rows)
    sent = [row for row in rows if row["direction"] == "sent"]
    if change == "extra-run":
        extra = copy.deepcopy(sent[-1])
        extra["rpc"]["id"] = 100
        rows.extend([extra, {"direction": "received", "rpc": {"id": 100, "result": rows[-1]["rpc"]["result"]}}])
    elif change == "wrong-cell":
        sent[-1]["rpc"]["params"]["arguments"]["cellId"] = "existing-unexecuted"
    elif change == "missing-response":
        rows.pop()
    else:
        sent[-1]["rpc"]["id"] = sent[0]["rpc"]["id"]
    for index, row in enumerate(rows):
        row["sequence"] = index
    with pytest.raises(ValueError):
        launch.verify_native(bound[0], b"".join(native.encoded(row) + b"\n" for row in rows))


@pytest.mark.parametrize("change", ["stale-context", "arbitrary-source", "missing-process-guard", "extra-cell"])
def test_changed_packet_refused_before_native_call(bound, monkeypatch, change):
    packet = copy.deepcopy(bound[0])
    if change == "stale-context":
        monkeypatch.setattr(launch, "context_hashes", lambda root: {})
    elif change == "arbitrary-source":
        packet["frozen_packet"]["cells"][1] = "print('unapproved')"
    elif change == "missing-process-guard":
        packet["core"]["runtime_guard"]["runtime_request"]["process_markers"] = []
        packet["core_manifest_sha256"] = native.digest(native.encoded(packet["core"]))
        packet["cells"] = launch.render(packet)
    else:
        packet["cells"].append("# extra")
    session = FakeSession(packet)
    with pytest.raises(ValueError):
        asyncio.run(launch.dispatch(packet, session, bound[1], approval=authority(packet), review="fixture"))
    assert session.calls == []


@pytest.mark.parametrize("change", ["incomplete-canary", "wrong-parent", "different-mounted-folder", "setup-environment"])
def test_preparation_requires_bound_setup_and_original_id_canary(bound, change):
    args, kwargs = copy.deepcopy(bound[2]), copy.deepcopy(bound[3])
    if change == "incomplete-canary":
        args[5]["status"] = "PENDING"
    elif change == "wrong-parent":
        args[3]["parent_id"] = "another-parent"
        args[3]["binding_sha256"] = transport.digest(transport.canonical({key: args[3][key]
            for key in ("request_id", "purpose", "nonce", "parent_id", "slots")}))
    elif change == "different-mounted-folder":
        kwargs["mounted_folder"] = "/content/drive/MyDrive/same-display-name"
    else:
        args[2]["environment_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        launch.prepare(*args, **kwargs)


def test_approved_manifest_binds_decision_original_slots_and_complete_return(bound):
    packet = native.read_json(native.encoded(bound[0]))
    approval = authority(packet)
    result = launch.prepare_return(packet, approval)
    manifest = result["launch_manifest"]
    assert manifest["operator_launch_decision_sha256"] == native.digest(native.encoded(approval))
    assert manifest["launch_packet_sha256"] == native.digest(native.encoded(packet))
    assert manifest["attempt_identity"] == launch.intake.OUTPUT + ".worker"
    assert manifest["setup_receipt_sha256"] == packet["core"]["setup_receipt_sha256"]
    assert manifest["reservation_sha256"] == native.digest(native.encoded(packet["return_reservation"]))
    assert manifest["derived_member_count"] == 206
    assert manifest["combined_transfer_cap"] == 32 * 1024 * 1024
    assert result["launch_manifest_sha256"] == native.digest(native.encoded(manifest))
    assert result["copy_packet"]["request"]["launch_manifest_sha256"] == result["launch_manifest_sha256"]
    assert result["intake_expected"]["request_id"] == packet["return_reservation"]["request_id"]
    assert result["intake_expected"]["request_id"] != packet["core"]["request_id"]
    assert result["intake_expected"]["destination"] == approval["private_validation_destination"]
    assert result["completion_observed"] is False and result["scientific_acceptance"] is False
    transport.verify_packet(packet["return_reservation"], result["copy_packet"])


@pytest.mark.parametrize("change", ["decision", "original-slot", "reservation-substitution", "destination"])
def test_return_binding_refuses_changed_approved_scope_or_original_reservation(bound, change):
    packet = copy.deepcopy(bound[0])
    approval = authority(packet)
    if change == "decision":
        approval["derived_return_transfer_206_members"] = False
    elif change == "original-slot":
        packet["return_reservation"]["slots"]["zip"]["id"] = "other-id"
    elif change == "reservation-substitution":
        packet["return_reservation"] = copy.deepcopy(bound[2][6])
    else:
        packet["core"]["private_validation_destination"] = "/different/private-return"
        packet["core_manifest_sha256"] = native.digest(native.encoded(packet["core"]))
        packet["cells"] = launch.render(packet)
    with pytest.raises(ValueError):
        launch.prepare_return(packet, approval)


@pytest.mark.parametrize("destination", ["relative/return", "/", "/tmp/../private", "/tmp/return/",
                                        "/tmp/private\nreturn", str(launch.ROOT / "patient-return")])
def test_launch_packet_requires_canonical_private_validation_destination(bound, destination):
    kwargs = dict(bound[3], private_validation_destination=destination)
    with pytest.raises(ValueError, match="VALIDATION_DESTINATION"):
        launch.prepare(*bound[2], **kwargs)


def observed_source_present(inputs):
    observed = copy.deepcopy(inputs[1]["observation"])
    for row in observed["source_files"]:
        row.update(state="PRESENT", matches_expected=True)
    return observed


@pytest.mark.parametrize("mutation", [
    lambda observed: observed["runtime"].update(fingerprint_sha256="0" * 64),
    lambda observed: observed["drive"].update(visible=False),
    lambda observed: observed["processes"].update(scan_complete=False),
    lambda observed: observed["processes"].update(matches=[{"pid": 5}]),
    lambda observed: observed["execution_paths"].update(worker={"state": "PRESENT"}),
    lambda observed: observed["execution_paths"].update(checkpoint_index={"state": "NOT_VISIBLE"}),
    lambda observed: observed["source_files"][0].update(matches_expected=False),
])
def test_fresh_metadata_guard_blocks_before_intent_or_environment_child(bound, inputs, monkeypatch, mutation):
    observed = observed_source_present(inputs)
    mutation(observed)
    monkeypatch.setattr(launch, "runtime_observation", lambda request: observed, raising=False)
    monkeypatch.setattr(launch, "check_observation", setup.check_observation, raising=False)
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("child must not run")))
    with pytest.raises(ValueError):
        launch.fresh_guard(bound[0]["core"], inspect.getsource(setup.child_environment))


def test_fresh_environment_mismatch_and_during_probe_process_change_block(bound, inputs, monkeypatch):
    observed = observed_source_present(inputs)
    monkeypatch.setattr(launch, "runtime_observation", lambda request: observed, raising=False)
    monkeypatch.setattr(launch, "check_observation", setup.check_observation, raising=False)
    env = environment()
    env["python_version"] = "3.12.1"
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout=native.encoded(env), stderr=b""))
    with pytest.raises(ValueError, match="ENVIRONMENT_CHANGED"):
        launch.fresh_guard(bound[0]["core"], inspect.getsource(setup.child_environment))
    env["python_version"] = "3.12.0"
    def after_probe(*args, **kwargs):
        observed["processes"]["matches"] = [{"pid": 5}]
        return SimpleNamespace(returncode=0, stdout=native.encoded(env), stderr=b"")
    monkeypatch.setattr("subprocess.run", after_probe)
    with pytest.raises(ValueError, match="UNCERTAIN_PROCESS"):
        launch.fresh_guard(bound[0]["core"], inspect.getsource(setup.child_environment))


def test_fixed_exclusive_intent_cannot_be_evaded_with_another_request(bound, tmp_path):
    core = copy.deepcopy(bound[0]["core"])
    core["intent_root"] = str(tmp_path / "fixed-intent")
    launch.claim_launch(core, "a" * 64)
    original = (Path(core["intent_root"]) / "intent.json").read_bytes()
    core["request_id"] = "second-request"
    with pytest.raises(FileExistsError):
        launch.claim_launch(core, "b" * 64)
    assert (Path(core["intent_root"]) / "intent.json").read_bytes() == original


@pytest.mark.parametrize("change", ["private-output", "completion", "wrong-parameters", "malformed-capture", "duplicate-key"])
def test_result_only_accepts_bounded_original_dispatch_metadata(bound, change):
    raw = outcome(bound[0], 1)
    lines = raw.splitlines()
    value = json.loads(lines[1])
    if change == "private-output":
        value["patient_payload"] = "must not cross"
    elif change == "completion":
        value["completion_observed"] = True
    elif change == "wrong-parameters":
        value["parameters_sha256"] = "0" * 64
    elif change == "malformed-capture":
        lines[0] = "not a literal"
    lines[1] = json.dumps(value)
    if change == "duplicate-key":
        lines[1] = lines[1][:-1] + ', "original_pid": 12345}'
    with pytest.raises(ValueError):
        launch.validate_stage(bound[0], 1, {"outputs": [{"output_type": "stream", "text": ["\n".join(lines)]}]})


def test_dispatch_metadata_refuses_fifo_without_opening(bound, tmp_path):
    import os
    core = copy.deepcopy(bound[0]["core"])
    job = tmp_path / "job"
    job.mkdir()
    os.mkfifo(job / "parameters.json")
    core["attempt_identity"] = str(job)
    with pytest.raises(ValueError, match="TYPE_OR_BOUND"):
        launch.dispatch_metadata(core, bound[0]["core_manifest_sha256"])


def test_scoped_source_review_rejects_setup_scope(tmp_path, monkeypatch):
    from orchestrator import p001_native_return_canary as canary
    # Reuse the exact reviewed fixture, adapting its source list/root to this route.
    monkeypatch.setattr(canary, "REQUIRED_SOURCES", launch.REQUIRED_SOURCES)
    monkeypatch.setattr(canary, "SCOPE", launch.SCOPE)
    root, directory, execution = reviewed_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(launch, "ROOT", root)
    assert launch.require_review(directory)["scope"] == launch.SCOPE
    response = native.read_json((directory / "response.json").read_bytes())
    response["structured_output"]["scope"] = "p001-transparent-setup-native-v1"
    (directory / "response.json").write_bytes(native.encoded(response))
    execution["response_sha256"] = native.digest((directory / "response.json").read_bytes())
    (directory / "execution.json").write_bytes(native.encoded(execution))
    with pytest.raises(ValueError, match="EXACT_SOURCE_REVIEW"):
        launch.require_review(directory)


def test_original_dispatch_records_remain_private_and_parameters_keep_original_order(bound, tmp_path):
    packet = bound[0]
    core = copy.deepcopy(packet["core"])
    core["attempt_identity"] = str(tmp_path / "synthetic-worker")
    core["intent_root"] = str(tmp_path / "intent")
    job = Path(core["attempt_identity"])
    job.mkdir()
    Path(core["intent_root"]).mkdir()
    params_node = next(n for n in ast.walk(ast.parse(packet["frozen_packet"]["launch_source"]))
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "params" for t in n.targets))
    params = ast.literal_eval(params_node.value)
    (job / "parameters.json").write_text(json.dumps(params))
    (job / "process.json").write_text(json.dumps({"pid": 2147483646}))
    (job / "run.py").write_text(colab_patient.child_script(packet["frozen_packet"]["original_notebook"], params))
    value = launch.dispatch_metadata(core, packet["core_manifest_sha256"])
    assert value["process_observation"] == {"state": "NOT_VISIBLE_OR_NOT_MATCHING", "start_ticks": None}
    assert value["parameters_sha256"] == launch.PARAMETERS_SHA
    assert value["completion_observed"] is False
    assert (Path(core["intent_root"]) / "dispatch.json").is_file()
    original = (job / "parameters.json").read_bytes()
    (job / "parameters.json").write_text(json.dumps(params, sort_keys=True))
    with pytest.raises(ValueError, match="EXECUTABLE_BINDING"):
        launch.dispatch_metadata(core, packet["core_manifest_sha256"])
    assert original != (job / "parameters.json").read_bytes()


def operation_outcome(packet, selected, stage, status="VALIDATED"):
    if stage == 0:
        return {"cpu_only": True, "colab_runtime": True}
    if selected["operation"] == "poll":
        return {"status": status}
    request = launch.prepare_return(packet, authority(packet))["copy_packet"]["request"]
    terminal = {"schema": "p001-full-return-terminal/v1", "request_id": request["request_id"],
        "runtime_fingerprint_sha256": request["runtime_fingerprint_sha256"], "worker_status": "VALIDATED",
        "execution_snapshot": launch.intake.EXECUTION_PIN, "source_pin": launch.intake.SOURCE_PIN,
        "notebook_pin": launch.intake.NOTEBOOK_PIN, "zip_name": "P001-private-return.zip",
        "zip_bytes": 4096, "zip_sha256": "c" * 64, "launch_manifest_sha256": selected["launch_manifest_sha256"],
        "max_extracted_bytes": request["max_extracted_bytes"]}
    raw = transport.canonical(terminal)
    return {"status": "COPIED_PENDING_ORIGINAL_ID_READBACK", "purpose": "PATIENT_RETURN",
        "zip_bytes": terminal["zip_bytes"], "zip_sha256": terminal["zip_sha256"],
        "terminal_bytes": len(raw), "terminal_sha256": native.digest(raw),
        "scientific_acceptance": False, "os_exit_independently_observed": False}


class OperationSession(CanarySession):
    def __init__(self, packet, selected, *, status="VALIDATED", **kwargs):
        super().__init__(selected, **kwargs)
        self.launch_packet, self.selected, self.status = packet, selected, status

    async def call_tool(self, name, args, **kwargs):
        response = await super().call_tool(name, args, **kwargs)
        if name == "run_code_cell":
            stage = [cell["id"] for cell in self.cells[1:]].index(args["cellId"])
            value = native.decode_result(name, response.result)
            if stage != self.failed_stage:
                value["outputs"] = [{"output_type": "stream", "text": [json.dumps(operation_outcome(
                    self.launch_packet, self.selected, stage, self.status))]}]
            response.result = {"content": [{"type": "text", "text": json.dumps(value)}], "isError": False}
            self.rows[-1]["rpc"]["result"] = copy.deepcopy(response.result)
        return response


def execute_operation(bound, operation, *, completion_protocol=None, directory=None, **kwargs):
    packet = bound[0]
    selected = launch.operation_packet(packet, authority(packet), operation, completion_protocol)
    session = OperationSession(packet, selected, **kwargs)
    asyncio.run(launch.dispatch(packet, session, directory or bound[1], approval=authority(packet), review="fixture",
        operation=operation, completion_protocol=completion_protocol))
    return session


@pytest.mark.parametrize("status", ["STARTING", "RUNNING", "VALIDATED", "FAILED", "NOT_VISIBLE", "INVALID_STATUS"])
def test_one_bound_frozen_poll_observes_status_without_retry_or_acceptance(bound, status):
    packet = bound[0]
    selected = launch.operation_packet(packet, authority(packet), "poll")
    assert repr(packet["frozen_packet"]["poll_source"]) in selected["cells"][1]
    assert selected["cells"][1].rindex("poll_guard(core,") < selected["cells"][1].rindex("exec(compile(")
    session = execute_operation(bound, "poll", status=status)
    result = launch.verify_native(packet, session.raw(), operation="poll", approval=authority(packet))
    assert [name for name, _ in session.calls] == launch.TOOL_SEQUENCE
    assert result["status"] == "P001_WORKER_STATUS_OBSERVED"
    assert result["stages"][1]["checked_outcome"] == {"status": status}
    assert result["completion_observed"] is (status == "VALIDATED")
    assert result["os_exit_independently_observed"] is False and result["scientific_acceptance"] is False
    assert result["automatic_retry"] is False


def test_terminal_copy_uses_exact_existing_cells_and_original_validated_poll(bound, tmp_path):
    packet = bound[0]
    poll = execute_operation(bound, "poll")
    selected = launch.operation_packet(packet, authority(packet), "copy", poll.raw())
    bindings = launch.prepare_return(packet, authority(packet))
    assert selected["cells"] == bindings["copy_packet"]["cells"]
    directory = tmp_path / "copy"
    directory.mkdir(mode=0o700)
    copied = execute_operation(bound, "copy", completion_protocol=poll.raw(), directory=directory)
    result = launch.verify_native(packet, copied.raw(), operation="copy", approval=authority(packet),
        completion_protocol=poll.raw())
    assert result["status"] == "PATIENT_RETURN_COPIED_PENDING_ORIGINAL_ID_READBACK"
    assert result["completion_observed"] is True and result["original_drive_ids_verified"] is False
    assert result["scientific_acceptance"] is False and result["os_exit_independently_observed"] is False
    assert result["completion_protocol_sha256"] == native.digest(poll.raw())
    assert result["launch_manifest_sha256"] == bindings["launch_manifest_sha256"]
    assert len(copied.calls) == 8


@pytest.mark.parametrize("status", ["STARTING", "RUNNING", "FAILED", "NOT_VISIBLE", "INVALID_STATUS"])
def test_nonvalidated_status_never_admits_terminal_copy(bound, status):
    poll = execute_operation(bound, "poll", status=status)
    with pytest.raises(ValueError, match="VALIDATED_POLL"):
        launch.operation_packet(bound[0], authority(bound[0]), "copy", poll.raw())


@pytest.mark.parametrize("change", ["missing", "truncated", "other-core", "launch-transcript", "changed-source"])
def test_copy_requires_original_complete_protocol_from_same_bound_poll(bound, change):
    packet = bound[0]
    if change == "launch-transcript":
        raw = execute(bound).raw()
    else:
        raw = execute_operation(bound, "poll").raw()
    if change == "missing":
        raw = None
    elif change == "truncated":
        raw = b"\n".join(raw.splitlines()[:-1]) + b"\n"
    elif change == "other-core":
        packet = copy.deepcopy(packet)
        packet["core"]["request_id"] = "other-approved-attempt"
        packet["core_manifest_sha256"] = native.digest(native.encoded(packet["core"]))
        packet["cells"] = launch.render(packet)
    elif change == "changed-source":
        raw = raw.replace(b"frozen-0770-status", b"changed-0770-status")
    with pytest.raises(ValueError):
        launch.operation_packet(packet, authority(packet), "copy", raw)


@pytest.mark.parametrize("operation", ["poll", "copy"])
def test_status_and_copy_missing_authority_review_and_lost_response_fail_closed(bound, tmp_path, monkeypatch, operation):
    packet = bound[0]
    completion = execute_operation(bound, "poll").raw() if operation == "copy" else None
    directory = tmp_path / "followup"
    directory.mkdir(mode=0o700)
    selected = launch.operation_packet(packet, authority(packet), operation, completion)
    session = OperationSession(packet, selected, fail_at=7)
    unapproved = authority(packet)
    unapproved["patient_launch"] = False
    with pytest.raises(ValueError, match="APPROVAL_REQUIRED"):
        asyncio.run(launch.dispatch(packet, session, directory, approval=unapproved, review="fixture",
            operation=operation, completion_protocol=completion))
    assert session.calls == []
    with monkeypatch.context() as patch:
        patch.setattr(launch, "require_review", lambda directory: (_ for _ in ()).throw(ValueError("source review")))
        with pytest.raises(ValueError, match="source review"):
            asyncio.run(launch.dispatch(packet, session, directory, approval=authority(packet), review="fixture",
                operation=operation, completion_protocol=completion))
    assert session.calls == []
    with pytest.raises(TimeoutError):
        asyncio.run(launch.dispatch(packet, session, directory, approval=authority(packet), review="fixture",
            operation=operation, completion_protocol=completion))
    assert len(session.calls) == 8 and (directory / "07.intent.json").exists()
    assert not (directory / "07.response.json").exists()
    with pytest.raises(ValueError, match="UNCERTAIN"):
        launch.verify_native(packet, session.raw(), operation=operation, approval=authority(packet), completion_protocol=completion)
    repeat = OperationSession(packet, selected)
    with pytest.raises(FileExistsError):
        asyncio.run(launch.dispatch(packet, repeat, directory, approval=authority(packet), review="fixture",
            operation=operation, completion_protocol=completion))
    assert repeat.calls == []


@pytest.mark.parametrize("change", ["payload", "wrong-purpose", "wrong-terminal", "oversize", "exit-claim", "copy-stopped"])
def test_patient_copy_result_enforces_scope_terminal_binding_and_combined_cap(bound, change):
    packet = bound[0]
    poll = execute_operation(bound, "poll")
    selected = launch.operation_packet(packet, authority(packet), "copy", poll.raw())
    value = operation_outcome(packet, selected, 1)
    if change == "payload":
        value["patient_payload"] = "forbidden"
    elif change == "wrong-purpose":
        value["purpose"] = "SYNTHETIC_CANARY"
    elif change == "wrong-terminal":
        value["terminal_sha256"] = "0" * 64
    elif change == "oversize":
        value["zip_bytes"] = transport.TRANSFER_CAP
    elif change == "exit-claim":
        value["os_exit_independently_observed"] = True
    else:
        value = {"status": "BLOCKED_RECONCILE", "failure_code": "P001_COPY_WORKER_NOT_VALIDATED",
            "exception_type": "ValueError", "automatic_retry": False, "scientific_acceptance": False}
    with pytest.raises(ValueError):
        launch.validate_operation_stage(packet, selected, 1, {"outputs": [{"output_type": "stream", "text": json.dumps(value)}]})


@pytest.mark.parametrize("change", [None, "runtime", "intent", "parameters", "child", "status", "fifo"])
def test_poll_guard_reads_only_original_bound_attempt_and_preserves_every_byte(bound, tmp_path, monkeypatch, change):
    import os
    packet = bound[0]
    core = copy.deepcopy(packet["core"])
    core["intent_root"] = str(tmp_path / "original-launch")
    core["attempt_identity"] = str(tmp_path / "original-worker")
    launch.claim_launch(core, packet["core_manifest_sha256"])
    job = Path(core["attempt_identity"])
    job.mkdir()
    params_node = next(n for n in ast.walk(ast.parse(packet["frozen_packet"]["launch_source"]))
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "params" for t in n.targets))
    params = ast.literal_eval(params_node.value)
    (job / "parameters.json").write_text(json.dumps(params))
    (job / "run.py").write_text(colab_patient.child_script(packet["frozen_packet"]["original_notebook"], params))
    (job / "status.json").write_text(json.dumps({"status": "RUNNING"}))
    observation = {"runtime": {"fingerprint_sha256": core["runtime_guard"]["runtime_fingerprint_sha256"]},
        "cpu_guard": {"colab_runtime": True, "nvidia_smi_absent": True}, "drive": {"mounted": True, "visible": True}}
    monkeypatch.setattr(launch, "runtime_observation", lambda request: observation, raising=False)
    if change == "runtime":
        observation["runtime"]["fingerprint_sha256"] = "0" * 64
    elif change == "intent":
        (Path(core["intent_root"]) / "intent.json").write_text("{}")
    elif change in ("parameters", "child", "status"):
        (job / {"parameters": "parameters.json", "child": "run.py", "status": "status.json"}[change]).write_text("{}")
    elif change == "fifo":
        (job / "status.json").unlink()
        os.mkfifo(job / "status.json")
    originals = {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    if change is None:
        launch.poll_guard(core, packet["core_manifest_sha256"])
    else:
        with pytest.raises(ValueError):
            launch.poll_guard(core, packet["core_manifest_sha256"])
    assert all(path.read_bytes() == raw for path, raw in originals.items())
