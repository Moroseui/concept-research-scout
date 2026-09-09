"""Fixed supervised P001 launch, preserving the frozen 0770 launcher and child.

Preparation grants no authority. One exact operator decision and a fresh scoped
source review admit one launch, bounded status observations and one terminal copy.
Each operation appends two cells / eight native calls. Original-ID collection and
frozen full return validation remain required; no OS exit or acceptance is inferred.
"""
import argparse
import ast
import asyncio
import datetime
import inspect
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

from orchestrator import p001_native_setup as native
from orchestrator import p001_runtime_setup as setup
from orchestrator import p001_runtime_intake as intake
from orchestrator import p001_return_transport as transport
from orchestrator import research_context
from orchestrator.colab_patient import CPU_CELL

ROOT = Path(__file__).resolve().parents[1]
SCOPE = "p001-native-launch-v1"
FROZEN_PACKET_SHA = "1c7d3e6140b439d58ce3ebe87e21842b72f8e81c3dc9152e09bba3c47ab1bd47"
WRAPPER_SHA = "d84ffb0b189578349b0230a750cbae3495ff0b5a80dfb6e49c4b8220be5ed775"
LAUNCH_SHA = "882c987592c7e32934117ab1b9c7db6c25768ca22bb262ca90d8ecfd75ff7947"
CHILD_SHA = "58e033fb8b836e999009053e1e8e91d3a0e60cdd173794ae450c49cac871fd9f"
PARAMETERS_SHA = "d695ca88c632fb5752c1d506903e93585482e3fcd79dca38ddd365287391fc10"
INTENT_ROOT = intake.OUTPUT + ".native-launch"
REQUIRED_SOURCES = {
    "orchestrator/p001_native_launch.py", "tests/test_p001_native_launch.py",
    "orchestrator/p001_native_setup.py", "orchestrator/p001_runtime_setup.py",
    "orchestrator/p001_runtime_intake.py", "orchestrator/colab_patient.py",
    "orchestrator/colab_worker.py", "orchestrator/p001_return_transport.py",
    "orchestrator/p001_return_intake.py", "orchestrator/research_context.py",
    "orchestrator/drive_evidence.py", "orchestrator/p001_native_return_canary.py",
    "tests/test_p001_native_setup.py", "tests/test_p001_native_return_canary.py",
    "tests/test_p001_runtime_setup.py", "tests/test_p001_return_transport.py",
    "tests/test_p001_return_intake.py",
}
TOOL_SEQUENCE = [
    "open_colab_browser_connection", "get_cells", "add_code_cell", "add_code_cell",
    "get_cells", "run_code_cell", "get_cells", "run_code_cell",
]


def frozen_packet(snapshot):
    """Invoke only frozen preparation/review binding; no preflight or experiment."""
    snapshot = Path(snapshot).absolute()
    if any(path.is_symlink() for path in [snapshot, *snapshot.parents]):
        raise ValueError("LAUNCH_FROZEN_SNAPSHOT_PATH")
    def git(*args):
        return subprocess.check_output(["git", "--no-optional-locks", *args],
            cwd=snapshot, timeout=30, stderr=subprocess.DEVNULL)
    if (git("rev-parse", "HEAD").decode().strip() != intake.EXECUTION_PIN or
            git("status", "--porcelain") or git("remote")):
        raise ValueError("LAUNCH_CLEAN_PRIVATE_FROZEN_SNAPSHOT_REQUIRED")
    for name in ("orchestrator/colab_patient.py", "orchestrator/colab_worker.py",
                 "orchestrator/campaign.py", "orchestrator/campaign_review.py"):
        if (snapshot / name).read_bytes() != git("show", intake.EXECUTION_PIN + ":" + name):
            raise ValueError("LAUNCH_FROZEN_IMPORT_CHANGED")
    source = """import sys,json
sys.path.insert(0,sys.argv[1])
from orchestrator.colab_patient import execution_packet,child_script
import hashlib
p=execution_packet(sys.argv[2])
h=lambda raw:hashlib.sha256(raw).hexdigest()
print(json.dumps({'packet':p,'parameters_sha256':h(json.dumps(p['parameters']).encode()),
    'child_sha256':h(child_script(p['original_notebook'],p['parameters']).encode())},sort_keys=True,separators=(',',':')))
"""
    result = subprocess.run([sys.executable, "-B", "-I", "-c", source, str(snapshot), intake.ARCHIVE],
        cwd=snapshot.parent, capture_output=True, timeout=60)
    if result.returncode or len(result.stdout) > 131072:
        raise ValueError("LAUNCH_FROZEN_PREPARATION_FAILED")
    prepared = native.read_json(result.stdout)
    value = prepared["packet"]
    if (native.digest(native.encoded(value)) != FROZEN_PACKET_SHA or
            prepared["parameters_sha256"] != PARAMETERS_SHA or prepared["child_sha256"] != CHILD_SHA):
        raise ValueError("LAUNCH_FROZEN_PACKET_CHANGED")
    return value


def context_hashes(root):
    selected = research_context.selected_prediction_context(root)
    if not selected:
        raise ValueError("LAUNCH_CURRENT_SELECTED_CHARTER_REQUIRED")
    selected.pop("context-disposition.json")
    names = {
        "docs/operations/REMOTE_OPERATING_DIRECTION.md", "docs/operations/CLAUDE_REVIEWER_DIRECTIVE.md",
        "campaigns/isles24-pilot/CAMPAIGN.md", "docs/isles-pilot/CURRENT_STATUS.md",
        "campaigns/isles24-pilot/experiments/P001/SPEC.md",
    }
    for name in names:
        selected[name] = research_context.checked(root, name)
    return {name: native.digest(text.encode()) for name, text in sorted(selected.items())}


def prepare(snapshot, setup_packet, setup_receipt, reservation, canary_native, canary_collection,
            canary_reservation, canary_packet,
            *, request_id, mounted_folder, max_extracted_bytes, private_validation_destination,
            context_root=ROOT):
    transport.request_identity(request_id)
    frozen = frozen_packet(snapshot)
    if (setup_receipt.get("status") != "SOURCE_DEPENDENCIES_AND_DEFAULT_CHILD_ENVIRONMENT_VERIFIED" or
            setup_receipt.get("packet_sha256") != native.digest(native.encoded(setup_packet)) or
            setup_receipt.get("binding_sha256") != setup_packet["request"]["binding_sha256"] or
            setup_receipt.get("scientific_acceptance") is not False):
        raise ValueError("LAUNCH_ACTUAL_SETUP_RECEIPT_REQUIRED")
    setup.validate_environment(setup_receipt["environment"])
    environment_sha = native.digest(native.encoded(setup_receipt["environment"]))
    fingerprint = setup_packet["request"]["runtime_fingerprint_sha256"]
    if (environment_sha != setup_receipt["environment_sha256"] or
            setup_receipt["runtime_fingerprint_sha256"] != fingerprint):
        raise ValueError("LAUNCH_SETUP_ENVIRONMENT_BINDING")
    transport.validate_reservation(reservation)
    if reservation["purpose"] != "PATIENT_RETURN":
        raise ValueError("LAUNCH_PATIENT_SLOTS_REQUIRED")
    if (canary_native.get("status") != "SYNTHETIC_CANARY_COPIED_PENDING_ORIGINAL_ID_READBACK" or
            canary_native.get("transport") != "NATIVE_MCP_JSONRPC_NOT_MODEL_OUTPUT" or
            canary_native.get("runtime_fingerprint_sha256") != fingerprint or
            canary_native.get("actual_tool_calls") != 8 or canary_native.get("model_calls") != 0 or
            canary_collection.get("status") != "SYNTHETIC_ORIGINAL_IDS_AND_BYTES_VERIFIED" or
            canary_collection.get("purpose") != "SYNTHETIC_CANARY" or
            canary_collection.get("slot_binding_sha256") != canary_native.get("slot_binding_sha256") or
            canary_collection.get("launch_manifest_sha256") != canary_native.get("launch_manifest_sha256") or
            canary_collection.get("zip_sha256") != native.digest(transport.synthetic_zip()) or
            canary_collection.get("originals_preserved") is not True or
            canary_collection.get("scientific_acceptance") is not False):
        raise ValueError("LAUNCH_COMPLETED_ORIGINAL_ID_CANARY_REQUIRED")
    transport.verify_packet(canary_reservation, canary_packet)
    if (canary_reservation["purpose"] != "SYNTHETIC_CANARY" or
            canary_reservation["parent_id"] != reservation["parent_id"] or
            canary_reservation["binding_sha256"] != canary_native["slot_binding_sha256"] or
            native.digest(native.encoded(canary_packet)) != canary_native["packet_sha256"] or
            any(str(Path(slot["path"]).parent) != mounted_folder for slot in canary_packet["request"]["slots"].values())):
        raise ValueError("LAUNCH_CANARY_ORIGINAL_FOLDER_BINDING")
    # Path and explicit caps use the existing exact return renderer's checks.
    transport.prepare_copy(reservation, mounted_folder, runtime_fingerprint=fingerprint,
        launch_manifest_sha256="0" * 64, max_extracted_bytes=max_extracted_bytes,
        worker_parameters_sha256=PARAMETERS_SHA, canary_receipt_sha256=native.digest(native.encoded(canary_collection)))
    guard = {key: setup_packet["request"][key] for key in
        ("runtime_fingerprint_sha256", "archive_metadata", "source_root", "runtime_request")}
    # The preflight source is not the scientific child's environment or source.
    guard["runtime_request"] = json.loads(json.dumps(guard["runtime_request"]))
    guard["runtime_request"]["source_files"] = [row for row in guard["runtime_request"]["source_files"]
        if row["path"].startswith(setup.SOURCE_ROOT + "/")]
    core = {"schema": "p001-exact-native-launch-core/v1", "request_id": request_id,
        "attempt_identity": intake.OUTPUT + ".worker", "intent_root": INTENT_ROOT,
        "execution_snapshot": intake.EXECUTION_PIN, "source_pin": intake.SOURCE_PIN,
        "notebook_pin": intake.NOTEBOOK_PIN, "frozen_packet_sha256": FROZEN_PACKET_SHA,
        "launch_source_sha256": LAUNCH_SHA, "launch_wrapper_sha256": WRAPPER_SHA,
        "child_source_sha256": CHILD_SHA, "worker_parameters_sha256": PARAMETERS_SHA,
        "setup_packet_sha256": native.digest(native.encoded(setup_packet)),
        "setup_receipt_sha256": native.digest(native.encoded(setup_receipt)),
        "environment_sha256": environment_sha, "runtime_guard": guard,
        "reservation_sha256": native.digest(native.encoded(reservation)),
        "slot_binding_sha256": reservation["binding_sha256"], "mounted_folder": mounted_folder,
        "private_validation_destination": validation_destination(private_validation_destination),
        "canary_native_receipt_sha256": native.digest(native.encoded(canary_native)),
        "canary_collection_receipt_sha256": native.digest(native.encoded(canary_collection)),
        "context_sha256": context_hashes(context_root),
        "derived_member_count": 206, "combined_transfer_cap": transport.TRANSFER_CAP,
        "max_extracted_bytes": max_extracted_bytes, "raw_or_staged_input_transfer": False,
        "validation": "UNCHANGED_FROZEN_0770_FULL_RETURN_VALIDATION_REQUIRED"}
    value = {"task": "p001_fixed_native_launch", "core": core,
        "core_manifest_sha256": native.digest(native.encoded(core)), "frozen_packet": frozen,
        "return_reservation": native.read_json(native.encoded(reservation)),
        "launch_authorized": False, "derived_transfer_authorized": False}
    value["cells"] = render(value)
    return checked_packet(value, context_root=context_root)


def validation_destination(value):
    """Bind a named private destination; intake checks ownership/existence/disk later."""
    if not isinstance(value, str) or not value or len(value) > 1024 or any(ord(c) < 32 for c in value):
        raise ValueError("LAUNCH_PRIVATE_VALIDATION_DESTINATION_REQUIRED")
    path = Path(value)
    if (not path.is_absolute() or str(path) != value or ".." in path.parts or
            path == path.parent or path.is_relative_to(ROOT.resolve())):
        raise ValueError("LAUNCH_PRIVATE_VALIDATION_DESTINATION_REQUIRED")
    return value


def fresh_guard(core, environment_source):
    """Read-only fresh guard before any exclusive attempt intent or child launch."""
    import hashlib
    import json
    import os
    from pathlib import Path
    import subprocess
    import sys
    request = core["runtime_guard"]
    observed = runtime_observation(request["runtime_request"])
    check_observation(observed, request, source_absent=False)
    source = environment_source + "\nimport json\nprint(json.dumps(child_environment(" + repr(request["source_root"]) + "),sort_keys=True,separators=(',',':')))\n"
    result = subprocess.run([sys.executable, "-B", "-c", source], cwd="/content",
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), capture_output=True, timeout=120)
    if result.returncode or len(result.stdout) > 131072 or len(result.stderr) > 4096:
        raise ValueError("LAUNCH_DEFAULT_ENVIRONMENT_PROBE_FAILED")
    value = json.loads(result.stdout)
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    if hashlib.sha256(raw).hexdigest() != core["environment_sha256"]:
        raise ValueError("LAUNCH_DEFAULT_ENVIRONMENT_CHANGED")
    # Repeat after the probe so process/path/source changes during that wait block.
    check_observation(runtime_observation(request["runtime_request"]), request, source_absent=False)


def claim_launch(core, manifest_sha):
    import json
    import os
    from pathlib import Path
    import stat
    root = Path(core["intent_root"])
    for parent in reversed(root.parents):
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise ValueError("LAUNCH_INTENT_PARENT_UNSAFE")
    os.umask(0o077)
    root.mkdir(mode=0o700, exist_ok=False)
    with (root / "intent.json").open("x") as handle:
        json.dump({"status": "LAUNCH_INTENT_NO_AUTOMATIC_RETRY", "core_manifest_sha256": manifest_sha,
                   "core": core}, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())


def dispatch_metadata(core, manifest_sha):
    """Original small parameters/process records only; never scientific output."""
    import hashlib
    import json
    import os
    from pathlib import Path
    import stat
    job = Path(core["attempt_identity"])
    records = {}
    for name in ("parameters.json", "process.json", "run.py"):
        path = job / name
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_size > 65536:
            raise ValueError("LAUNCH_ORIGINAL_METADATA_TYPE_OR_BOUND")
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as handle:
            after = os.fstat(handle.fileno())
            if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino) or not stat.S_ISREG(after.st_mode):
                raise ValueError("LAUNCH_ORIGINAL_METADATA_IDENTITY_CHANGED")
            raw = handle.read(65537)
        if len(raw) > 65536:
            raise ValueError("LAUNCH_ORIGINAL_METADATA_BOUND")
        records[name] = (raw, hashlib.sha256(raw).hexdigest())
    if records["parameters.json"][1] != core["worker_parameters_sha256"] or records["run.py"][1] != core["child_source_sha256"]:
        raise ValueError("LAUNCH_ORIGINAL_EXECUTABLE_BINDING_CHANGED")
    process = json.loads(records["process.json"][0])
    if set(process) != {"pid"} or type(process["pid"]) is not int or not 0 < process["pid"] < 2**31:
        raise ValueError("LAUNCH_ORIGINAL_PROCESS_RECORD")
    # Preserve start ticks only when the observed command still names this exact
    # child. A later PID with different ticks is reuse, not this launch.
    import sys
    process_observation = {"state": "NOT_VISIBLE_OR_NOT_MATCHING", "start_ticks": None}
    proc = Path("/proc") / str(process["pid"])
    try:
        before_stat = (proc / "stat").read_bytes()
        command = (proc / "cmdline").read_bytes()
        after_stat = (proc / "stat").read_bytes()
        if (len(command) <= 4096 and len(before_stat) <= 4096 and before_stat.rsplit(b")", 1)[1].split()[19] ==
                after_stat.rsplit(b")", 1)[1].split()[19] and
                command == (sys.executable + "\0" + str(job / "run.py") + "\0").encode()):
            ticks = int(before_stat.rsplit(b")", 1)[1].split()[19])
            if ticks > 0:
                process_observation = {"state": "MATCHING_CHILD_OBSERVED", "start_ticks": ticks}
    except (OSError, ValueError, IndexError):
        pass
    # This is deliberately not a claim about future liveness or independent OS exit.
    value = {"status": "DISPATCHED_PENDING_COMPLETION_RECONCILIATION",
        "core_manifest_sha256": manifest_sha, "original_pid": process["pid"],
        "parameters_sha256": records["parameters.json"][1], "process_sha256": records["process.json"][1],
        "child_source_sha256": records["run.py"][1], "process_observation": process_observation,
        "runtime_fingerprint_sha256": core["runtime_guard"]["runtime_fingerprint_sha256"],
        "scientific_acceptance": False, "completion_observed": False, "os_exit_independently_observed": False,
        "automatic_retry": False}
    with (Path(core["intent_root"]) / "dispatch.json").open("x") as handle:
        json.dump(value, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    return value


def render(packet):
    frozen, core = packet["frozen_packet"], native.read_json(native.encoded(packet["core"]))
    helper = "\n".join(inspect.getsource(function) for function in
        (intake.runtime_observation, setup.check_observation, fresh_guard, claim_launch, dispatch_metadata))
    # Frozen wrapper is a literal unchanged substring; its own private capture
    # suppresses original scientific/source diagnostics. The outer guard emits
    # fixed failure metadata only; no retry and no original evidence deletion.
    body = "\n".join([
        "fresh_guard(core," + repr(inspect.getsource(setup.child_environment)) + ")",
        "claim_launch(core, manifest_sha)",
        "exec(compile(" + repr(frozen["cells"][1]) + ", 'frozen-0770-launch-wrapper', 'exec'), globals())",
        "print(json.dumps(dispatch_metadata(core,manifest_sha),sort_keys=True))",
    ])
    cell = helper + "\nimport json\ncore = " + repr(core) + "\nmanifest_sha = " + repr(packet["core_manifest_sha256"])
    cell += "\ntry:\n" + "\n".join("    " + line for line in body.splitlines())
    cell += "\nexcept BaseException as error:\n    print(json.dumps({'status':'LAUNCH_STOPPED_RECONCILE_ORIGINAL_INTENT','error_type':type(error).__name__,'automatic_retry':False}))\n"
    compile(cell, "p001-fixed-native-launch", "exec")
    return [CPU_CELL, cell]


def checked_packet(packet, *, context_root=ROOT):
    core = packet["core"]
    validation_destination(core["private_validation_destination"])
    reservation = transport.validate_reservation(packet["return_reservation"])
    if (reservation["purpose"] != "PATIENT_RETURN" or
            native.digest(native.encoded(reservation)) != core["reservation_sha256"] or
            reservation["binding_sha256"] != core["slot_binding_sha256"]):
        raise ValueError("LAUNCH_EXACT_PATIENT_RETURN_RESERVATION_REQUIRED")
    transport.request_identity(core["request_id"])
    transport.sha(core["runtime_guard"]["runtime_fingerprint_sha256"])
    transport.sha(core["environment_sha256"])
    runtime_request = intake.packet(core["runtime_guard"]["runtime_request"]["request_id"])["request"]
    runtime_request["source_files"] = [row for row in runtime_request["source_files"]
        if row["path"].startswith(setup.SOURCE_ROOT + "/")]
    if (core["runtime_guard"]["runtime_request"] != runtime_request or
            core["runtime_guard"]["source_root"] != setup.SOURCE_ROOT or
            core["runtime_guard"]["archive_metadata"].get("size_bytes") != 99014629647 or
            core["runtime_guard"]["archive_metadata"].get("kind") != "file" or
            type(core["max_extracted_bytes"]) is not int or not 0 < core["max_extracted_bytes"] < 2**63 or
            core["execution_snapshot"] != intake.EXECUTION_PIN or core["source_pin"] != intake.SOURCE_PIN or
            core["notebook_pin"] != intake.NOTEBOOK_PIN):
        raise ValueError("LAUNCH_EXACT_RUNTIME_GUARD_REQUIRED")
    if (packet.get("task") != "p001_fixed_native_launch" or packet.get("launch_authorized") is not False or
            packet.get("derived_transfer_authorized") is not False or
            native.digest(native.encoded(packet["frozen_packet"])) != FROZEN_PACKET_SHA or
            core["frozen_packet_sha256"] != FROZEN_PACKET_SHA or core["launch_source_sha256"] != LAUNCH_SHA or
            core["launch_wrapper_sha256"] != WRAPPER_SHA or core["child_source_sha256"] != CHILD_SHA or
            core["worker_parameters_sha256"] != PARAMETERS_SHA or core["intent_root"] != INTENT_ROOT or
            core["attempt_identity"] != intake.OUTPUT + ".worker" or
            packet["core_manifest_sha256"] != native.digest(native.encoded(core)) or
            core["context_sha256"] != context_hashes(context_root) or
            core["combined_transfer_cap"] != transport.TRANSFER_CAP or core["derived_member_count"] != 206 or
            core["raw_or_staged_input_transfer"] is not False or
            packet["cells"] != render(packet) or any(len(cell.encode()) > 131072 for cell in packet["cells"])):
        raise ValueError("LAUNCH_EXACT_PACKET_REQUIRED")
    return packet


def require_authority(packet, approval):
    expected = {"schema": "p001-exact-native-launch-approval/v1", "status": "OPERATOR_APPROVED",
        "core_manifest_sha256": packet["core_manifest_sha256"], "patient_launch": True,
        "derived_return_transfer_206_members": True,
        "combined_transfer_cap": packet["core"]["combined_transfer_cap"],
        "max_extracted_bytes": packet["core"]["max_extracted_bytes"],
        "private_validation_destination": packet["core"]["private_validation_destination"],
        "raw_or_staged_input_transfer": False}
    if approval != expected or any(type(approval[key]) is not bool for key in
            ("patient_launch", "derived_return_transfer_206_members", "raw_or_staged_input_transfer")):
        raise ValueError("LAUNCH_EXACT_OPERATOR_LAUNCH_AND_TRANSFER_APPROVAL_REQUIRED")
    # Governance input recorded by the operator-controlled caller. This reader
    # verifies scope/bindings; it cannot authenticate a human from JSON alone.
    return native.digest(native.encoded(approval))


def prepare_return(packet, approval):
    """Offline decision-to-return binding; no copy, collection, extraction or science."""
    checked_packet(packet)
    approval_sha = require_authority(packet, approval)
    core = packet["core"]
    manifest = {"schema": "p001-approved-launch-manifest/v1",
        "operator_launch_decision_sha256": approval_sha,
        "launch_packet_sha256": native.digest(native.encoded(packet)),
        "core_manifest_sha256": packet["core_manifest_sha256"],
        **{key: core[key] for key in (
            "request_id", "attempt_identity", "execution_snapshot", "source_pin", "notebook_pin",
            "setup_packet_sha256", "setup_receipt_sha256", "environment_sha256", "reservation_sha256",
            "slot_binding_sha256", "canary_collection_receipt_sha256", "worker_parameters_sha256",
            "private_validation_destination", "derived_member_count", "combined_transfer_cap",
            "max_extracted_bytes", "raw_or_staged_input_transfer")},
        "runtime_fingerprint_sha256": core["runtime_guard"]["runtime_fingerprint_sha256"]}
    manifest_sha = native.digest(native.encoded(manifest))
    copy_packet = transport.prepare_copy(packet["return_reservation"], core["mounted_folder"],
        runtime_fingerprint=manifest["runtime_fingerprint_sha256"], launch_manifest_sha256=manifest_sha,
        max_extracted_bytes=core["max_extracted_bytes"], worker_parameters_sha256=PARAMETERS_SHA,
        canary_receipt_sha256=core["canary_collection_receipt_sha256"])
    transport.verify_packet(packet["return_reservation"], copy_packet)
    return {"status": "APPROVED_LAUNCH_RETURN_BINDINGS_PREPARED_NO_EXECUTION",
        "launch_manifest": manifest, "launch_manifest_sha256": manifest_sha, "copy_packet": copy_packet,
        "intake_expected": {"request_id": copy_packet["request"]["request_id"],
            "runtime_fingerprint": manifest["runtime_fingerprint_sha256"],
            "launch_manifest_sha256": manifest_sha, "max_extracted_bytes": core["max_extracted_bytes"],
            "destination": core["private_validation_destination"], "execution_snapshot": intake.EXECUTION_PIN},
        "completion_observed": False, "scientific_acceptance": False, "automatic_retry": False}


def poll_guard(core, manifest_sha):
    """Read bound original launch ownership and worker code before frozen status."""
    import hashlib
    import json
    import os
    from pathlib import Path
    import stat
    observation = runtime_observation(core["runtime_guard"]["runtime_request"])
    if (observation["runtime"]["fingerprint_sha256"] != core["runtime_guard"]["runtime_fingerprint_sha256"] or
            observation["cpu_guard"] != {"colab_runtime": True, "nvidia_smi_absent": True} or
            observation["drive"] != {"mounted": True, "visible": True}):
        raise ValueError("POLL_BOUND_RUNTIME_NOT_VISIBLE_OR_CHANGED")
    def read_original(path):
        for parent in reversed(path.parents):
            if not stat.S_ISDIR(parent.lstat().st_mode):
                raise ValueError("POLL_ORIGINAL_PATH_UNSAFE")
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_size > 65536:
            raise ValueError("POLL_ORIGINAL_RECORD_TYPE_OR_BOUND")
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as handle:
            opened = os.fstat(handle.fileno())
            raw = handle.read(65537)
            after = os.fstat(handle.fileno())
        identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        if (len(raw) > 65536 or identity(before) != identity(opened) or identity(opened) != identity(after) or
                identity(after) != identity(path.lstat())):
            raise ValueError("POLL_ORIGINAL_RECORD_CHANGED")
        return raw
    original = json.loads(read_original(Path(core["intent_root"]) / "intent.json"))
    if original != {"status": "LAUNCH_INTENT_NO_AUTOMATIC_RETRY", "core_manifest_sha256": manifest_sha, "core": core}:
        raise ValueError("POLL_ORIGINAL_LAUNCH_BINDING_CHANGED")
    job = Path(core["attempt_identity"])
    for name, expected in (("parameters.json", core["worker_parameters_sha256"]),
                           ("run.py", core["child_source_sha256"])):
        if hashlib.sha256(read_original(job / name)).hexdigest() != expected:
            raise ValueError("POLL_ORIGINAL_WORKER_BINDING_CHANGED")
    # Bound and read the original status before the unchanged frozen poll reads it.
    # No process is waited on or terminated, and status is not an OS exit receipt.
    status = json.loads(read_original(job / "status.json"))
    if status not in ({"status": value} for value in ("STARTING", "RUNNING", "VALIDATED", "FAILED")):
        raise ValueError("POLL_ORIGINAL_STATUS_SCHEMA")


def render_poll(packet):
    core = native.read_json(native.encoded(packet["core"]))
    helper = "\n".join(inspect.getsource(function) for function in (intake.runtime_observation, poll_guard))
    source = helper + "\nimport json\ncore = " + repr(core)
    source += "\ntry:\n    poll_guard(core, " + repr(packet["core_manifest_sha256"]) + ")\n"
    source += "    exec(compile(" + repr(packet["frozen_packet"]["poll_source"]) + ", 'frozen-0770-status', 'exec'), globals())\n"
    source += "except BaseException as error:\n    print(json.dumps({'status':'POLL_STOPPED_RECONCILE_ORIGINAL_STATE','error_type':type(error).__name__,'automatic_retry':False}))\n"
    compile(source, "p001-bound-frozen-poll", "exec")
    return [CPU_CELL, source]


def operation_packet(packet, approval, operation, completion_protocol=None):
    """Closed operation set, all bound to the same exact decision and return manifest."""
    if operation not in ("launch", "poll", "copy"):
        raise ValueError("LAUNCH_FIXED_OPERATION_REQUIRED")
    bindings = prepare_return(packet, approval)
    if operation == "copy":
        if not completion_protocol:
            raise ValueError("LAUNCH_ORIGINAL_VALIDATED_POLL_PROTOCOL_REQUIRED")
        completion = verify_native(packet, completion_protocol, operation="poll", approval=approval)
        if completion["stages"][1]["checked_outcome"] != {"status": "VALIDATED"}:
            raise ValueError("LAUNCH_ORIGINAL_VALIDATED_POLL_PROTOCOL_REQUIRED")
        cells = bindings["copy_packet"]["cells"]
    else:
        if completion_protocol is not None:
            raise ValueError("LAUNCH_UNEXPECTED_COMPLETION_PROTOCOL")
        cells = packet["cells"] if operation == "launch" else render_poll(packet)
    if len(cells) != 2 or any(len(cell.encode()) > 131072 for cell in cells):
        raise ValueError("LAUNCH_FIXED_OPERATION_CELL_BOUND")
    return {"operation": operation, "cells": cells, "core_manifest_sha256": packet["core_manifest_sha256"],
        "launch_manifest_sha256": bindings["launch_manifest_sha256"],
        "completion_protocol_sha256": native.digest(completion_protocol) if completion_protocol is not None else None}


def validate_operation_stage(packet, selected, index, result):
    if selected["operation"] == "launch":
        return validate_stage(packet, index, result)
    if index == 0:
        value = validate_stage(packet, index, result)["checked_outcome"]
    else:
        if not isinstance(result.get("outputs"), list):
            raise ValueError("LAUNCH_NATIVE_OUTPUT_REQUIRED")
        parts = []
        for output in result["outputs"]:
            if output.get("output_type") != "stream":
                raise ValueError("LAUNCH_UNEXPECTED_OR_FAILED_OUTPUT")
            text = output.get("text")
            if isinstance(text, str):
                text = [text]
            if not isinstance(text, list) or any(not isinstance(item, str) for item in text):
                raise ValueError("LAUNCH_STREAM_SCHEMA")
            parts.extend(text)
        raw = "".join(parts)
        if len(raw.encode()) > 4096:
            raise ValueError("LAUNCH_OUTPUT_BOUND")
        value = native.read_json(raw)
        if selected["operation"] == "poll":
            if value not in ({"status": state} for state in ("STARTING", "RUNNING", "VALIDATED", "FAILED", "NOT_VISIBLE", "INVALID_STATUS")):
                raise ValueError("LAUNCH_FIXED_STATUS_RESULT_REQUIRED")
        else:
            terminal = {"schema": "p001-full-return-terminal/v1", "request_id": packet["return_reservation"]["request_id"],
                "runtime_fingerprint_sha256": packet["core"]["runtime_guard"]["runtime_fingerprint_sha256"],
                "worker_status": "VALIDATED", "execution_snapshot": intake.EXECUTION_PIN,
                "source_pin": intake.SOURCE_PIN, "notebook_pin": intake.NOTEBOOK_PIN,
                "zip_name": "P001-private-return.zip", "zip_bytes": value.get("zip_bytes"),
                "zip_sha256": value.get("zip_sha256"), "launch_manifest_sha256": selected["launch_manifest_sha256"],
                "max_extracted_bytes": packet["core"]["max_extracted_bytes"]}
            terminal_raw = transport.canonical(terminal)
            transport.terminal_receipt(terminal_raw, request_id=terminal["request_id"],
                runtime_fingerprint=terminal["runtime_fingerprint_sha256"],
                launch_manifest_sha256=selected["launch_manifest_sha256"],
                max_extracted_bytes=terminal["max_extracted_bytes"])
            expected = {"status": "COPIED_PENDING_ORIGINAL_ID_READBACK", "purpose": "PATIENT_RETURN",
                "zip_bytes": terminal["zip_bytes"], "zip_sha256": terminal["zip_sha256"],
                "terminal_bytes": len(terminal_raw), "terminal_sha256": native.digest(terminal_raw),
                "scientific_acceptance": False, "os_exit_independently_observed": False}
            if (value != expected or type(value.get("terminal_bytes")) is not int or
                    value.get("scientific_acceptance") is not False or value.get("os_exit_independently_observed") is not False or
                    value["zip_bytes"] + value["terminal_bytes"] > transport.TRANSFER_CAP):
                raise ValueError("LAUNCH_EXACT_PATIENT_COPY_RESULT_REQUIRED")
    return {"index": index, "cell_sha256": native.digest(selected["cells"][index].encode()),
        "native_result_sha256": native.digest(native.encoded(result)), "checked_outcome": value}


def validate_stage(packet, index, result):
    if type(index) is not int or index not in (0, 1) or not isinstance(result.get("outputs"), list):
        raise ValueError("LAUNCH_NATIVE_OUTPUT_REQUIRED")
    parts = []
    for output in result["outputs"]:
        if output.get("output_type") != "stream":
            raise ValueError("LAUNCH_UNEXPECTED_OR_FAILED_OUTPUT")
        text = output.get("text")
        if isinstance(text, str):
            text = [text]
        if not isinstance(text, list) or any(not isinstance(item, str) for item in text):
            raise ValueError("LAUNCH_STREAM_SCHEMA")
        parts.extend(text)
    raw = "".join(parts)
    if len(raw.encode()) > 4096:
        raise ValueError("LAUNCH_OUTPUT_BOUND")
    if index == 0:
        value = native.read_json(raw)
        if value != {"cpu_only": True, "colab_runtime": True} or any(type(item) is not bool for item in value.values()):
            raise ValueError("LAUNCH_CPU_COLAB_REQUIRED")
    else:
        lines = raw.splitlines()
        if len(lines) != 2:
            raise ValueError("LAUNCH_DISPATCH_EVIDENCE_REQUIRED_RECONCILE")
        try:
            capture = ast.literal_eval(lines[0])
        except (ValueError, SyntaxError) as error:
            raise ValueError("LAUNCH_CAPTURE_SCHEMA") from error
        if capture != {"transport_status": "COMPLETE", "source_sha256": LAUNCH_SHA}:
            raise ValueError("LAUNCH_FROZEN_WRAPPER_FAILED_RECONCILE")
        value = native.read_json(lines[1])
        pid = value.get("original_pid")
        observation = value.get("process_observation", {})
        if (set(observation) != {"state", "start_ticks"} or not (
                observation == {"state": "NOT_VISIBLE_OR_NOT_MATCHING", "start_ticks": None} or
                (observation["state"] == "MATCHING_CHILD_OBSERVED" and
                 type(observation["start_ticks"]) is int and observation["start_ticks"] > 0))):
            raise ValueError("LAUNCH_PROCESS_OBSERVATION_SCHEMA")
        expected = {"status": "DISPATCHED_PENDING_COMPLETION_RECONCILIATION",
            "core_manifest_sha256": packet["core_manifest_sha256"], "original_pid": pid,
            "process_observation": observation, "parameters_sha256": PARAMETERS_SHA,
            "process_sha256": native.digest(json.dumps({"pid": pid}).encode()), "child_source_sha256": CHILD_SHA,
            "runtime_fingerprint_sha256": packet["core"]["runtime_guard"]["runtime_fingerprint_sha256"],
            "scientific_acceptance": False, "completion_observed": False,
            "os_exit_independently_observed": False, "automatic_retry": False}
        if (value != expected or type(pid) is not int or not 0 < pid < 2**31 or
                any(value.get(key) is not False for key in
                    ("scientific_acceptance", "completion_observed", "os_exit_independently_observed", "automatic_retry"))):
            raise ValueError("LAUNCH_EXACT_DISPATCH_METADATA_REQUIRED")
    return {"index": index, "cell_sha256": native.digest(packet["cells"][index].encode()),
        "native_result_sha256": native.digest(native.encoded(result)), "checked_outcome": value}


def require_review(directory):
    """Exact launch source review; no prior setup/canary approval substitutes."""
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
        raise ValueError("LAUNCH_EXACT_SOURCE_REVIEW_REQUIRED")
    for name, expected in execution["input_file_sha256"].items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or (ROOT / path).is_symlink():
            raise ValueError("LAUNCH_REVIEW_INPUT_PATH")
        if native.digest((ROOT / path).read_bytes()) != expected:
            raise ValueError("LAUNCH_REVIEW_INPUT_CHANGED")
    return {"reviewed_commit": execution["reviewed_commit"],
            "execution_sha256": native.digest(native.private_file(directory / "execution.json")),
            "scope": SCOPE}


async def dispatch(packet, session, directory, *, approval, review, operation="launch", completion_protocol=None):
    """Literal eight-call attempt; every original request intent precedes submission."""
    checked_packet(packet)
    require_authority(packet, approval)
    require_review(review)
    selected = operation_packet(packet, approval, operation, completion_protocol)
    ordinal = 0

    async def call(name, arguments):
        nonlocal ordinal
        if ordinal >= len(TOOL_SEQUENCE) or name != TOOL_SEQUENCE[ordinal]:
            raise ValueError("LAUNCH_FIXED_TOOL_SEQUENCE")
        number = ordinal
        ordinal += 1
        native.write_new(directory / (str(number).zfill(2) + ".intent.json"),
            {"tool": name, "arguments": arguments, "packet_sha256": native.digest(native.encoded(packet)),
             "operation": operation, "operation_packet_sha256": native.digest(native.encoded(selected))})
        response = await session.call_tool(name, arguments,
            read_timeout_seconds=datetime.timedelta(seconds=180 if name == "run_code_cell" else 90))
        raw = response.model_dump(mode="json", by_alias=True, exclude_none=True)
        native.write_new(directory / (str(number).zfill(2) + ".response.json"), raw)
        return native.decode_result(name, raw)

    if await call("open_colab_browser_connection", {}) != {"result": True}:
        raise ValueError("LAUNCH_EXISTING_BROWSER_REQUIRED")
    tools = await session.list_tools()
    if not native.TOOL_NAMES <= {tool.name for tool in tools.tools}:
        raise ValueError("LAUNCH_CONNECTED_TOOL_SET_REQUIRED")
    initial = native.cells_result(await call("get_cells", {"includeOutputs": False}))
    if len(initial) > 62:
        raise ValueError("LAUNCH_NOTEBOOK_CELL_BOUND")
    created = []
    for index, source in enumerate(selected["cells"]):
        result = await call("add_code_cell", {"cellIndex": len(initial) + index, "language": "python", "code": source})
        cell_id = result.get("newCellId")
        if not isinstance(cell_id, str) or not cell_id or cell_id in initial or cell_id in created:
            raise ValueError("LAUNCH_NEW_CELL_ID_REQUIRED")
        created.append(cell_id)
    expected = {**initial, **dict(zip(created, selected["cells"]))}
    outcomes = []
    for index, cell_id in enumerate(created):
        readback = native.cells_result(await call("get_cells", {"includeOutputs": False}))
        if readback != expected or list(readback) != list(expected):
            raise ValueError("LAUNCH_SOURCE_READBACK_CHANGED")
        outcomes.append(validate_operation_stage(packet, selected, index, await call("run_code_cell", {"cellId": cell_id})))
    return outcomes


def verify_native(packet, raw, *, operation="launch", approval=None, completion_protocol=None):
    """Validate original JSON-RPC identities/readbacks, never a reconstructed transcript."""
    checked_packet(packet)
    if approval is None:
        if operation != "launch" or completion_protocol is not None:
            raise ValueError("LAUNCH_EXACT_OPERATOR_LAUNCH_AND_TRANSFER_APPROVAL_REQUIRED")
        selected = {"operation": "launch", "cells": packet["cells"],
            "core_manifest_sha256": packet["core_manifest_sha256"], "launch_manifest_sha256": None,
            "completion_protocol_sha256": None}
    else:
        selected = operation_packet(packet, approval, operation, completion_protocol)
    lines = raw.splitlines()
    if (not raw or len(raw) > native.MAX_PROTOCOL or len(lines) > 256 or
            any(len(line) > native.MAX_FRAME for line in lines)):
        raise ValueError("LAUNCH_PROTOCOL_BOUND")
    requests, responses, calls = {}, {}, []
    pings, ping_responses = set(), set()
    for index, line in enumerate(lines):
        row = native.read_json(line)
        if row.get("sequence") != index or row.get("direction") not in ("sent", "received"):
            raise ValueError("LAUNCH_PROTOCOL_SEQUENCE")
        rpc = row["rpc"]
        if row["direction"] == "received" and rpc.get("method") == "ping" and "id" in rpc:
            if rpc["id"] in pings or rpc.get("params", {}) != {}:
                raise ValueError("LAUNCH_UNEXPECTED_SERVER_REQUEST")
            pings.add(rpc["id"])
        elif row["direction"] == "sent" and "id" in rpc and "method" not in rpc:
            if rpc["id"] not in pings or rpc["id"] in ping_responses or rpc.get("result") != {}:
                raise ValueError("LAUNCH_UNEXPECTED_CLIENT_RESPONSE")
            ping_responses.add(rpc["id"])
        elif row["direction"] == "sent" and "method" in rpc and "id" in rpc:
            if rpc["id"] in requests or rpc["method"] not in ("initialize", "tools/list", "tools/call"):
                raise ValueError("LAUNCH_DUPLICATE_OR_UNEXPECTED_REQUEST")
            requests[rpc["id"]] = rpc
            if rpc["method"] == "tools/call":
                if set(rpc["params"]) != {"name", "arguments"}:
                    raise ValueError("LAUNCH_TOOL_ARGUMENT_SCHEMA")
                calls.append((index, rpc))
        elif row["direction"] == "received" and "id" in rpc:
            if ("method" in rpc or rpc["id"] not in requests or rpc["id"] in responses or
                    "error" in rpc or "result" not in rpc):
                raise ValueError("LAUNCH_RESPONSE_ID_OR_ERROR")
            responses[rpc["id"]] = (index, rpc["result"])
    if pings != ping_responses or any(request_id not in responses for request_id in requests):
        raise ValueError("LAUNCH_UNCERTAIN_REQUEST_RECONCILE")
    if [rpc["params"]["name"] for _, rpc in calls] != TOOL_SEQUENCE:
        raise ValueError("LAUNCH_FIXED_TOOL_SEQUENCE")
    initial, expected, created, outcomes = None, None, [], []
    for position, (sent_index, rpc) in enumerate(calls):
        response_index, result = responses[rpc["id"]]
        if response_index <= sent_index or (position + 1 < len(calls) and response_index >= calls[position + 1][0]):
            raise ValueError("LAUNCH_SERIAL_RESPONSE_ORDER")
        name, arguments = rpc["params"]["name"], rpc["params"]["arguments"]
        value = native.decode_result(name, result)
        if name == "open_colab_browser_connection":
            if arguments != {} or value != {"result": True}:
                raise ValueError("LAUNCH_EXISTING_BROWSER_REQUIRED")
        elif name == "get_cells":
            if arguments != {"includeOutputs": False}:
                raise ValueError("LAUNCH_SOURCE_ONLY_READ_REQUIRED")
            observed = native.cells_result(value)
            if initial is None:
                if len(observed) > 62:
                    raise ValueError("LAUNCH_NOTEBOOK_CELL_BOUND")
                initial = observed
            elif observed != expected or list(observed) != list(expected):
                raise ValueError("LAUNCH_SOURCE_READBACK_CHANGED")
        elif name == "add_code_cell":
            index = len(created)
            if arguments != {"cellIndex": len(initial) + index, "language": "python", "code": selected["cells"][index]}:
                raise ValueError("LAUNCH_EXACT_SOURCE_REQUIRED")
            cell_id = value.get("newCellId")
            if not isinstance(cell_id, str) or not cell_id or cell_id in initial or cell_id in created:
                raise ValueError("LAUNCH_NEW_CELL_ID_REQUIRED")
            created.append(cell_id)
            expected = {**initial, **dict(zip(created, selected["cells"]))}
        else:
            index = len(outcomes)
            if arguments != {"cellId": created[index]}:
                raise ValueError("LAUNCH_BOUND_RUN_REQUIRED")
            outcomes.append(validate_operation_stage(packet, selected, index, value))
    if len(outcomes) != 2:
        raise ValueError("LAUNCH_COMPLETE_SEQUENCE_REQUIRED")
    status = {"launch": "DISPATCHED_PENDING_COMPLETION_RECONCILIATION", "poll": "P001_WORKER_STATUS_OBSERVED",
              "copy": "PATIENT_RETURN_COPIED_PENDING_ORIGINAL_ID_READBACK"}[operation]
    return {"status": status, "operation": operation,
        "transport": "NATIVE_MCP_JSONRPC_NOT_MODEL_OUTPUT", "native_protocol_sha256": native.digest(raw),
        "packet_sha256": native.digest(native.encoded(packet)), "core_manifest_sha256": packet["core_manifest_sha256"],
        "request_id": packet["core"]["request_id"], "stages": outcomes, "actual_tool_calls": 8, "model_calls": 0,
        "launch_manifest_sha256": selected["launch_manifest_sha256"],
        "operation_packet_sha256": native.digest(native.encoded(selected)),
        "completion_protocol_sha256": selected["completion_protocol_sha256"],
        "scientific_acceptance": False,
        "completion_observed": operation == "copy" or (operation == "poll" and outcomes[1]["checked_outcome"] == {"status": "VALIDATED"}),
        "os_exit_independently_observed": False, "original_drive_ids_verified": False,
        "automatic_retry": False}


async def run(packet, approval, destination, review, operation="launch", completion_evidence=None):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    reviewed = require_review(review)
    packet_value = checked_packet(native.read_json(native.private_file(packet)))
    approval_value = native.read_json(native.private_file(approval))
    approval_sha = require_authority(packet_value, approval_value)
    return_binding = prepare_return(packet_value, approval_value)
    if operation == "copy":
        if completion_evidence is None:
            raise ValueError("LAUNCH_ORIGINAL_VALIDATED_POLL_PROTOCOL_REQUIRED")
        completion_protocol = native.private_file(Path(completion_evidence) / "native-protocol.jsonl")
    else:
        if completion_evidence is not None:
            raise ValueError("LAUNCH_UNEXPECTED_COMPLETION_PROTOCOL")
        completion_protocol = None
    selected = operation_packet(packet_value, approval_value, operation, completion_protocol)
    config_raw = native.private_file(native.CONFIG)
    if native.digest(config_raw) != native.CONFIG_SHA256:
        raise ValueError("LAUNCH_EXISTING_MCP_CONFIGURATION_CHANGED")
    config = native.read_json(config_raw)
    if set(config.get("mcpServers", {})) != {"colab-worker"}:
        raise ValueError("LAUNCH_EXISTING_MCP_CONFIGURATION_CHANGED")
    server = config["mcpServers"]["colab-worker"]
    if server["command"] != native.COMMAND or server.get("args", []) != []:
        raise ValueError("LAUNCH_EXISTING_MCP_CONFIGURATION_CHANGED")
    destination = Path(destination).absolute()
    if destination.is_relative_to(ROOT.resolve()):
        raise ValueError("LAUNCH_PRIVATE_DESTINATION_REQUIRED")
    for parent in destination.parents:
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise ValueError("LAUNCH_PRIVATE_PATH_ANCESTOR")
    info = destination.parent.stat()
    if info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("LAUNCH_PRIVATE_PARENT_REQUIRED")
    os.umask(0o077)
    destination.mkdir(mode=0o700, exist_ok=False)
    native.write_new(destination / "packet.json", packet_value)
    native.write_new(destination / "return-bindings.json", return_binding)
    native.write_new(destination / "operation-packet.json", selected)
    if completion_protocol is not None:
        with (destination / "completion-native-protocol.jsonl").open("xb") as handle:
            handle.write(completion_protocol)
    native.write_new(destination / "execution-intent.json", {"packet_sha256": native.digest(native.encoded(packet_value)),
        "operator_approval_sha256": approval_sha,
        "client_sha256": native.digest(Path(__file__).read_bytes()), "review": reviewed,
        "configuration_sha256": native.CONFIG_SHA256, "max_wall_seconds": 900,
        "operation": operation, "operation_packet_sha256": native.digest(native.encoded(selected)),
        "patient_launch_authorized": True, "automatic_retry": False})
    journal = native.Journal(destination / "native-protocol.jsonl")
    try:
        with (destination / "server.stderr.log").open("x") as errors:
            async with asyncio.timeout(900):
                async with stdio_client(StdioServerParameters(command=native.COMMAND, args=[], env=server.get("env")), errlog=errors) as (read, write):
                    async with ClientSession(native.RecordedReceive(read, journal), native.RecordedSend(write, journal),
                            read_timeout_seconds=datetime.timedelta(seconds=90)) as session:
                        await session.initialize()
                        await dispatch(packet_value, session, destination, approval=approval_value, review=review,
                            operation=operation, completion_protocol=completion_protocol)
        journal.close()
        result = verify_native(packet_value, native.private_file(destination / "native-protocol.jsonl"),
            operation=operation, approval=approval_value, completion_protocol=completion_protocol)
        native.write_new(destination / "verified.json", result)
        return result
    except BaseException as error:
        journal.close()
        native.write_new(destination / "stopped.json", {"status": "NATIVE_LAUNCH_STOPPED_RECONCILE_ORIGINAL_REQUESTS",
            "operation": operation, "error_type": type(error).__name__, "patient_launch_authorized": True, "automatic_retry": False})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("packet", "approval", "destination", "review"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--operation", choices=("launch", "poll", "copy"), default="launch")
    parser.add_argument("--completion-evidence", type=Path,
        help="For copy only: private completed poll directory containing its original native-protocol.jsonl")
    args = parser.parse_args()
    try:
        result = asyncio.run(run(**vars(args)))
    except BaseException as error:
        print(json.dumps({"status": "NATIVE_LAUNCH_STOPPED_RECONCILE_ORIGINAL_REQUESTS",
            "error_type": type(error).__name__, "automatic_retry": False}))
        raise SystemExit(1) from None
    print(json.dumps({key: result[key] for key in ("status", "native_protocol_sha256", "actual_tool_calls",
        "model_calls", "completion_observed", "scientific_acceptance")}))


if __name__ == "__main__":
    main()
