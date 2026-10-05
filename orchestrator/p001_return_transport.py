"""Fixed P001 private return transport. No new OAuth scope or scientific acceptance.

Reservation creates only two app-owned marker files and proposes protected aliases.
Actual patient ZIP copying/collection requires the separately approved launch manifest.
Synthetic canaries use separate reservations and can never satisfy scientific intake.
"""
import copy
import hashlib
import inspect
import io
import json
import os
from pathlib import Path
import re
import secrets
import zipfile

from orchestrator.drive_evidence import DriveEvidence, FIELDS, private_write
from orchestrator.p001_return_intake import (
    TRANSFER_CAP, RECEIPT_CAP, EXECUTION_PIN, SOURCE_PIN, NOTEBOOK_PIN,
    MEMBER_COUNT, DIRECTORY_CAP, AGGREGATES, check_directory, inspect_members,
    canonical, digest, regular_file, terminal_receipt,
)
from orchestrator.p001_runtime_intake import packet as runtime_packet, runtime_observation
from orchestrator.colab_patient import CPU_CELL

ROLES = ("zip", "terminal")
PURPOSES = ("SYNTHETIC_CANARY", "PATIENT_RETURN")


def request_identity(value):
    if not isinstance(value, str) or not re.fullmatch("[a-z0-9][a-z0-9-]{7,47}", value):
        raise ValueError("P001_TRANSPORT_REQUEST_ID")
    return value


def sha(value):
    if not isinstance(value, str) or not re.fullmatch("[0-9a-f]{64}", value):
        raise ValueError("P001_TRANSPORT_SHA256")
    return value


def private_root(path):
    path = Path(path).absolute()
    for parent in [*reversed(path.parents), path]:
        if parent.is_symlink() or not parent.is_dir():
            raise ValueError("P001_TRANSPORT_PRIVATE_ROOT")
    if path.stat().st_mode & 0o077:
        raise ValueError("P001_TRANSPORT_PRIVATE_ROOT")
    return path


def read_json(path, maximum=65536):
    with regular_file(path) as handle:
        raw = handle.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError("P001_TRANSPORT_RECORD_BOUND")
    return json.loads(raw)


def blocked():
    return {"status": "BLOCKED_RECONCILE", "automatic_retry": False,
            "scientific_acceptance": False}


def marker(binding, role):
    return canonical({"schema": "p001-return-reserved-slot/v1",
        "request_id": binding["request_id"], "purpose": binding["purpose"],
        "nonce": binding["nonce"], "role": role})


def validate_reservation(value):
    if (value.get("schema") != "p001-return-reservation/v1" or
            value.get("status") != "RESERVED_MARKERS_VERIFIED" or
            value.get("purpose") not in PURPOSES or set(value["slots"]) != set(ROLES)):
        raise ValueError("P001_TRANSPORT_RESERVATION")
    request_identity(value["request_id"])
    sha(value["nonce"])
    binding = {key: value[key] for key in ("request_id", "purpose", "nonce", "parent_id", "slots")}
    if digest(canonical(binding)) != value["binding_sha256"]:
        raise ValueError("P001_TRANSPORT_RESERVATION_BINDING")
    if len({value["slots"][r]["id"] for r in ROLES}) != 2:
        raise ValueError("P001_TRANSPORT_SLOT_IDENTITIES")
    for role in ROLES:
        slot = value["slots"][role]
        suffix = ".zip" if role == "zip" else ".terminal.json"
        if (slot["name"] != "p001-" + value["request_id"] + "-" + value["nonce"][:16] + suffix or
                slot["alias"] != value["request_id"] + "-" + role or
                slot["marker_sha256"] != digest(marker(value, role))):
            raise ValueError("P001_TRANSPORT_SLOT_BINDING")
    return value


def alias_proposal(reservation):
    value = validate_reservation(reservation)
    return {slot["alias"]: {"id": slot["id"], "expected_name": slot["name"],
        "access": "small-evidence-read", "max_bytes": TRANSFER_CAP if role == "zip" else RECEIPT_CAP}
        for role, slot in value["slots"].items()}


def reserve_slots(client, config, destination, request_id, *, purpose):
    """Protected operator action; never installs aliases or allocates again on recovery."""
    request_identity(request_id)
    if purpose not in PURPOSES or not config.get("output_folder_id"):
        raise ValueError("P001_TRANSPORT_RESERVATION_PURPOSE_OR_FOLDER")
    destination = private_root(destination) / request_id
    if destination.exists() or destination.is_symlink():
        if (destination / "receipt.json").is_file():
            old = validate_reservation(read_json(destination / "receipt.json"))
            if (old["request_id"] != request_id or old["purpose"] != purpose or
                    old["parent_id"] != config["output_folder_id"]):
                raise ValueError("P001_TRANSPORT_RESERVATION_CONFLICT")
            return old
        return blocked()
    destination.mkdir(mode=0o700)
    binding = {"request_id": request_id, "purpose": purpose,
               "nonce": secrets.token_hex(32), "parent_id": config["output_folder_id"]}
    # Persist before even ID allocation. A lost allocation reply is a reconciliation stop.
    private_write(destination / "binding.json", binding)
    try:
        client.private_folder(binding["parent_id"])
        ids = client.allocate_ids(2)
        if (len(ids) != 2 or len(set(ids)) != 2 or
                any(not isinstance(item, str) or not re.fullmatch("[A-Za-z0-9_-]{3,200}", item) for item in ids)):
            raise ValueError("P001_TRANSPORT_PREALLOCATED_IDS")
        slots = {}
        for role, file_id in zip(ROLES, ids):
            suffix = ".zip" if role == "zip" else ".terminal.json"
            slots[role] = {"id": file_id, "name": "p001-" + request_id + "-" + binding["nonce"][:16] + suffix,
                "alias": request_id + "-" + role, "marker_sha256": digest(marker(binding, role))}
        binding["slots"] = slots
        private_write(destination / "intent.json", binding)
        for role in ROLES:
            slot = slots[role]
            data = marker(binding, role)
            client.private_folder(binding["parent_id"])
            created = client.create(slot["id"], slot["name"], binding["parent_id"], data)
            private_write(destination / (role + "-created.json"), created)
            before = slot_metadata(client, slot["id"])
            check_slot_metadata(before, slot, binding["parent_id"])
            if int(before["size"]) != len(data) or before.get("md5Checksum") != hashlib.md5(data).hexdigest():
                raise ValueError("P001_TRANSPORT_MARKER_METADATA")
            returned = io.BytesIO()
            client.download(slot["id"], returned, RECEIPT_CAP)
            after = slot_metadata(client, slot["id"])
            if after != before or returned.getvalue() != data:
                raise ValueError("P001_TRANSPORT_MARKER_READBACK")
            private_write(destination / (role + "-verified.json"), {"metadata": after, "sha256": digest(data)})
        receipt = {"schema": "p001-return-reservation/v1", "status": "RESERVED_MARKERS_VERIFIED",
                   **binding, "binding_sha256": digest(canonical(binding)),
                   "alias_proposal_installed": False, "scientific_acceptance": False}
        private_write(destination / "receipt.json", receipt)
        private_write(destination / "protected-alias-proposal.json", alias_proposal(receipt))
        return receipt
    except Exception as error:
        private_write(destination / "failure.json", {"exception_type": type(error).__name__,
                                                   "detail": str(error), "automatic_retry": False})
        return blocked()


def slot_metadata(client, file_id):
    """Read exact parents and ownership using the existing protected Google client."""
    return client.api.files().get(fileId=file_id,
        fields=FIELDS + ",parents,ownedByMe,permissions(type,role)").execute(num_retries=0)


def check_slot_metadata(value, slot, parent):
    if (value.get("id") != slot["id"] or value.get("name") != slot["name"] or value.get("trashed") or
            value.get("mimeType", "").startswith("application/vnd.google-apps.") or
            value.get("parents") != [parent] or value.get("ownedByMe") is not True or
            not value.get("permissions") or any(row.get("type") != "user" or row.get("role") != "owner"
                for row in value["permissions"])):
        raise ValueError("P001_TRANSPORT_REGISTERED_SLOT_CHANGED")


def synthetic_zip():
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        info = zipfile.ZipInfo("SYNTHETIC-CANARY.txt", date_time=(2026, 9, 8, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100600 << 16
        archive.writestr(info, b"P001 transport canary. No patient data.\n")
    return output.getvalue()


def runtime_member_names(request):
    """Read frozen source metadata through selection; no evaluation or member output."""
    import json
    import re
    import subprocess
    import sys
    program = """import importlib.util,json,sys
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root))
path=root/'campaigns/isles24-pilot/experiments/P001/run.py'
spec=importlib.util.spec_from_file_location('frozen_p001_return_selection',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
print(json.dumps(sorted(module.selection())))
"""
    result = subprocess.run([sys.executable, "-B", "-I", "-c", program,
        request["source_root"]], capture_output=True, timeout=60)
    if result.returncode or len(result.stdout) > 16384:
        raise ValueError("P001_COPY_FROZEN_MEMBER_SELECTION")
    cases = json.loads(result.stdout)
    if (not isinstance(cases, list) or len(cases) != 99 or
            any(not isinstance(case, str) or not re.fullmatch("[A-Za-z0-9][A-Za-z0-9_-]{0,63}", case) for case in cases) or
            len(set(cases)) != 99):
        raise ValueError("P001_COPY_FROZEN_MEMBER_SELECTION")
    members = {"bundle/" + name for name in AGGREGATES} | {"console.log", "private/binding.json", "private/checkpoint_index.json"}
    members.update("private/checkpoints/" + case + ".json" for case in cases)
    members.update("private/predictions/" + case + ".npy" for case in cases)
    return members


def copy_return(request):
    """Standalone fixed cell body. Return only bounded status and hashes."""
    import hashlib
    import io
    import json
    import os
    from pathlib import Path
    import stat

    def canonical(value):
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    def digest(raw):
        return hashlib.sha256(raw).hexdigest()
    def identity(value):
        return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
    def opened(path, write=False):
        path = Path(path)
        for ancestor in reversed(path.parents):
            if not stat.S_ISDIR(ancestor.lstat().st_mode):
                raise ValueError("P001_COPY_PATH_ANCESTOR")
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("P001_COPY_REGULAR_FILE")
        flags = (os.O_RDWR if write else os.O_RDONLY) | os.O_NOFOLLOW | os.O_NONBLOCK
        fd = os.open(path, flags)
        handle = os.fdopen(fd, "r+b" if write else "rb")
        if identity(os.fstat(fd)) != identity(before):
            handle.close()
            raise ValueError("P001_COPY_FILE_CHANGED")
        return handle
    def read_small(path, limit):
        with opened(path) as handle:
            raw = handle.read(limit + 1)
        if len(raw) > limit:
            raise ValueError("P001_COPY_METADATA_BOUND")
        return raw
    def stream_hash(handle):
        handle.seek(0)
        hashed = hashlib.sha256()
        for block in iter(lambda: handle.read(1 << 20), b""):
            hashed.update(block)
        handle.seek(0)
        return hashed.hexdigest()
    def marker_ok(handle, role):
        handle.seek(0)
        raw = handle.read(16385)
        if digest(raw) != request["slots"][role]["marker_sha256"]:
            raise ValueError("P001_COPY_RESERVED_MARKER_MISMATCH")
        handle.seek(0)

    observation = runtime_observation(request["observation"])
    if (observation["runtime"]["fingerprint_sha256"] != request["runtime_fingerprint_sha256"] or
            observation["cpu_guard"] != {"colab_runtime": True, "nvidia_smi_absent": True} or
            observation["drive"] != {"mounted": True, "visible": True}):
        raise ValueError("P001_COPY_RUNTIME_OR_DRIVE_CHANGED")
    if not observation["processes"]["scan_complete"] or observation["processes"]["matches"]:
        raise ValueError("P001_COPY_PROCESS_STATE_RECONCILE")
    patient = request["purpose"] == "PATIENT_RETURN"
    source = None
    if patient:
        if any(row.get("matches_expected") is not True for row in observation["source_files"]):
            raise ValueError("P001_COPY_FROZEN_SOURCE_CHANGED")
        if read_small(request["worker_status"], 256).strip() not in (b'{"status": "VALIDATED"}', b'{"status":"VALIDATED"}'):
            raise ValueError("P001_COPY_WORKER_NOT_VALIDATED")
        if digest(read_small(request["worker_parameters"], 16384)) != request["worker_parameters_sha256"]:
            raise ValueError("P001_COPY_WORKER_PARAMETERS_CHANGED")
        source = opened(request["source_zip"])
        source_identity = identity(os.fstat(source.fileno()))
    else:
        source = io.BytesIO(bytes.fromhex(request["synthetic_zip_hex"]))
        source_identity = None
    try:
        source.seek(0, 2)
        size = source.tell()
        source.seek(0)
        if not 0 < size <= request["transfer_cap"]:
            raise ValueError("P001_COPY_COMBINED_TRANSFER_CAP")
        if patient:
            # Metadata-only ZIP admission before transfer; original scientific
            # validation remains authoritative after private extraction.
            import zipfile
            expected = runtime_member_names(request)
            check_directory(source, size)
            with zipfile.ZipFile(source) as archive:
                inspect_members(archive, expected, request["max_extracted_bytes"])
        zipped_sha = stream_hash(source)
        terminal = {"schema": "p001-full-return-terminal/v1" if patient else "p001-return-canary-terminal/v1",
            "request_id": request["request_id"], "runtime_fingerprint_sha256": request["runtime_fingerprint_sha256"],
            "worker_status": "VALIDATED" if patient else "SYNTHETIC_CANARY",
            "execution_snapshot": request["execution_snapshot"], "source_pin": request["source_pin"],
            "notebook_pin": request["notebook_pin"], "zip_name": "P001-private-return.zip",
            "zip_bytes": size, "zip_sha256": zipped_sha, "launch_manifest_sha256": request["launch_manifest_sha256"],
            "max_extracted_bytes": request["max_extracted_bytes"]}
        terminal_raw = canonical(terminal)
        if len(terminal_raw) > request["receipt_cap"] or size + len(terminal_raw) > request["transfer_cap"]:
            raise ValueError("P001_COPY_COMBINED_TRANSFER_CAP")
        with opened(request["slots"]["zip"]["path"], True) as target, opened(request["slots"]["terminal"]["path"], True) as receipt:
            marker_ok(target, "zip")
            marker_ok(receipt, "terminal")
            os.umask(0o077)
            # Fixed current-runtime intent; a prior intent always requires reconciliation.
            with open(request["intent_path"], "xb") as intent:
                intent.write(canonical({"request_id": request["request_id"],
                    "slot_binding_sha256": request["slot_binding_sha256"],
                    "launch_manifest_sha256": request["launch_manifest_sha256"],
                    "zip_sha256": zipped_sha, "zip_bytes": size}))
                intent.flush()
                os.fsync(intent.fileno())
            intent_parent = os.open(Path(request["intent_path"]).parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(intent_parent)
            finally:
                os.close(intent_parent)
            target.truncate(0)
            copied = 0
            for block in iter(lambda: source.read(1 << 20), b""):
                copied += len(block)
                if copied > size:
                    raise ValueError("P001_COPY_SOURCE_CHANGED")
                target.write(block)
            target.flush()
            os.fsync(target.fileno())
            if copied != size or stream_hash(target) != zipped_sha:
                raise ValueError("P001_COPY_ZIP_READBACK")
            if patient and (identity(os.fstat(source.fileno())) != source_identity or
                    identity(Path(request["source_zip"]).lstat()) != source_identity or
                    stream_hash(source) != zipped_sha or
                    read_small(request["worker_status"], 256).strip() not in (b'{"status": "VALIDATED"}', b'{"status":"VALIDATED"}')):
                raise ValueError("P001_COPY_SOURCE_OR_STATUS_CHANGED")
            if any(identity(Path(request["slots"][role]["path"]).lstat())[:2] !=
                    identity(os.fstat(handle.fileno()))[:2] for role, handle in (("zip", target), ("terminal", receipt))):
                raise ValueError("P001_COPY_SLOT_PATH_REPLACED")
            # The successful terminal receipt is the last slot write.
            receipt.truncate(0)
            receipt.write(terminal_raw)
            receipt.flush()
            os.fsync(receipt.fileno())
            receipt.seek(0)
            if receipt.read(request["receipt_cap"] + 1) != terminal_raw:
                raise ValueError("P001_COPY_TERMINAL_READBACK")
        return {"status": "COPIED_PENDING_ORIGINAL_ID_READBACK", "purpose": request["purpose"],
                "zip_bytes": size, "zip_sha256": zipped_sha, "terminal_bytes": len(terminal_raw),
                "terminal_sha256": digest(terminal_raw), "scientific_acceptance": False,
                "os_exit_independently_observed": False}
    finally:
        source.close()


def prepare_copy(reservation, mounted_folder, *, runtime_fingerprint, launch_manifest_sha256,
                 max_extracted_bytes, worker_parameters_sha256=None, canary_receipt_sha256=None):
    value = validate_reservation(reservation)
    sha(runtime_fingerprint)
    sha(launch_manifest_sha256)
    if type(max_extracted_bytes) is not int or not 0 < max_extracted_bytes < 2**63:
        raise ValueError("P001_TRANSPORT_EXPLICIT_EXPANSION_CAP")
    folder = Path(mounted_folder)
    if (not isinstance(mounted_folder, str) or str(folder) != mounted_folder or
            not mounted_folder.startswith("/content/drive/MyDrive/") or ".." in folder.parts or
            len(mounted_folder) > 240 or any(ord(c) < 32 for c in mounted_folder)):
        raise ValueError("P001_TRANSPORT_MOUNTED_FOLDER")
    patient = value["purpose"] == "PATIENT_RETURN"
    if patient:
        sha(worker_parameters_sha256)
        sha(canary_receipt_sha256)
    observation = runtime_packet(value["request_id"])["request"]
    root = "/content/scout-pilot-" + SOURCE_PIN[:12] + "/"
    observation["source_files"] = [row for row in observation["source_files"] if row["path"].startswith(root)]
    request = {"purpose": value["purpose"], "request_id": value["request_id"],
        "runtime_fingerprint_sha256": runtime_fingerprint, "launch_manifest_sha256": launch_manifest_sha256,
        "slot_binding_sha256": value["binding_sha256"], "max_extracted_bytes": max_extracted_bytes,
        "execution_snapshot": EXECUTION_PIN, "source_pin": SOURCE_PIN, "notebook_pin": NOTEBOOK_PIN,
        "transfer_cap": TRANSFER_CAP, "receipt_cap": RECEIPT_CAP, "observation": observation,
        "slots": {role: {"path": mounted_folder + "/" + value["slots"][role]["name"],
                        "marker_sha256": value["slots"][role]["marker_sha256"]} for role in ROLES},
        "intent_path": "/content/p001-return-" + value["request_id"] + "-" + value["nonce"][:16] + ".copy-intent.json"}
    if patient:
        output = "/content/drive/MyDrive/isles-pilot/P001-v1.worker"
        request.update(source_zip=output + "/P001-private-return.zip", worker_status=output + "/status.json",
            worker_parameters=output + "/parameters.json", worker_parameters_sha256=worker_parameters_sha256,
            canary_receipt_sha256=canary_receipt_sha256, source_root=root.rstrip("/"))
    else:
        request["synthetic_zip_hex"] = synthetic_zip().hex()
    source = ("import stat, struct, zipfile\nfrom pathlib import PurePosixPath\n" +
        "MEMBER_COUNT = " + repr(MEMBER_COUNT) + "\nDIRECTORY_CAP = " + repr(DIRECTORY_CAP) +
        "\nAGGREGATES = " + repr(AGGREGATES) + "\n" +
        "\n".join(inspect.getsource(function) for function in
            (runtime_observation, check_directory, inspect_members, runtime_member_names, copy_return)))
    cell = source + "\nimport json\ntry:\n    _return_status = copy_return(" + repr(request) + ")\nexcept Exception as _error:\n    import re\n    _code = str(_error) if isinstance(_error, ValueError) and re.fullmatch('P001_COPY_[A-Z_]+', str(_error)) else 'P001_COPY_FAILED_PRESERVE_PRIVATE_STATE'\n    _return_status = {'status':'BLOCKED_RECONCILE','failure_code':_code,'exception_type':type(_error).__name__,'automatic_retry':False,'scientific_acceptance':False}\nprint(json.dumps(_return_status, sort_keys=True))\n"
    compile(cell, "p001-fixed-return-copy", "exec")
    return {"task": "p001_return_copy", "request": request, "cells": [CPU_CELL, cell],
        "slot_binding_sha256": value["binding_sha256"], "copy_cell_sha256": digest(cell.encode()),
        "authority": "SYNTHETIC_CANARY_ONLY" if not patient else "REQUIRES_EXACT_LAUNCH_AND_DERIVED_RETURN_TRANSFER_DECISION",
        "worker_instructions": "Reuse the existing connected CPU runtime and notebook. Append only these two exact cells, read sources back with includeOutputs=false, then execute each once in order. Never mount, restart, create or replace a runtime, execute existing cells, run an experiment or retry. Stop on any failure. Return only fixed cell status; no payload or log reads."}


def validate_terminal(raw, request):
    if request["purpose"] == "PATIENT_RETURN":
        return terminal_receipt(raw, request_id=request["request_id"],
            runtime_fingerprint=request["runtime_fingerprint_sha256"],
            launch_manifest_sha256=request["launch_manifest_sha256"],
            max_extracted_bytes=request["max_extracted_bytes"])
    expected = {"schema": "p001-return-canary-terminal/v1", "request_id": request["request_id"],
        "runtime_fingerprint_sha256": request["runtime_fingerprint_sha256"], "worker_status": "SYNTHETIC_CANARY",
        "execution_snapshot": EXECUTION_PIN, "source_pin": SOURCE_PIN, "notebook_pin": NOTEBOOK_PIN,
        "zip_name": "P001-private-return.zip", "zip_bytes": len(synthetic_zip()), "zip_sha256": digest(synthetic_zip()),
        "launch_manifest_sha256": request["launch_manifest_sha256"], "max_extracted_bytes": request["max_extracted_bytes"]}
    if raw != canonical(expected):
        raise ValueError("P001_TRANSPORT_CANARY_TERMINAL")
    return expected


def verify_packet(reservation, packet):
    request = packet["request"]
    folder = str(Path(request["slots"]["zip"]["path"]).parent)
    rebuilt = prepare_copy(reservation, folder,
        runtime_fingerprint=request["runtime_fingerprint_sha256"],
        launch_manifest_sha256=request["launch_manifest_sha256"],
        max_extracted_bytes=request["max_extracted_bytes"],
        worker_parameters_sha256=request.get("worker_parameters_sha256"),
        canary_receipt_sha256=request.get("canary_receipt_sha256"))
    if packet != rebuilt:
        raise ValueError("P001_TRANSPORT_PACKET_NOT_EXACT")


def collect_pair(broker, reservation, destination, request_id, peer_uid, copy_packet):
    """Protected alias-only collection; separate terminal then exact remaining ZIP cap."""
    request_identity(request_id)
    value = validate_reservation(reservation)
    verify_packet(value, copy_packet)
    request = copy_packet["request"]
    if (request["request_id"] != value["request_id"] or request["slot_binding_sha256"] != value["binding_sha256"] or
            request["purpose"] != value["purpose"] or peer_uid not in broker.config["caller_uids"] or
            value["parent_id"] != broker.config["output_folder_id"]):
        raise ValueError("P001_TRANSPORT_COLLECTION_BINDING")
    proposal = alias_proposal(value)
    if any(broker.config["files"].get(alias) != entry for alias, entry in proposal.items()):
        raise ValueError("P001_TRANSPORT_PROTECTED_ALIASES_REQUIRED")
    root = private_root(destination) / request_id
    if root.exists() or root.is_symlink():
        return blocked()
    root.mkdir(mode=0o700)
    ids = {role: request_id + "-" + role for role in ROLES}
    private_write(root / "intent.json", {"slot_binding_sha256": value["binding_sha256"],
        "copy_packet_sha256": digest(canonical(copy_packet)), "collection_request_ids": ids})
    try:
        broker.client.private_folder(value["parent_id"])
        before = {}
        for role in ROLES:
            slot = value["slots"][role]
            before[role] = slot_metadata(broker.client, slot["id"])
            check_slot_metadata(before[role], slot, value["parent_id"])
        sizes = {role: int(before[role].get("size", -1)) for role in ROLES}
        if not 0 < sizes["terminal"] <= RECEIPT_CAP or not 0 < sizes["zip"] or sum(sizes.values()) > TRANSFER_CAP:
            raise ValueError("P001_TRANSPORT_COMBINED_TRANSFER_CAP")
        private_write(root / "metadata-before-pair.json", before)
        collected = {}
        for role in ("terminal", "zip"):
            config = copy.deepcopy(broker.config)
            alias = value["slots"][role]["alias"]
            maximum = RECEIPT_CAP if role == "terminal" else min(terminal["zip_bytes"], TRANSFER_CAP - collected["terminal"]["bytes"])
            config["files"][alias]["max_bytes"] = min(config["files"][alias]["max_bytes"], maximum)
            scoped = DriveEvidence(config, broker.client)
            result = scoped.handle({"operation": "collect", "body": {"alias": alias, "request_id": ids[role]}}, peer_uid)
            if result.get("status") != "PRIVATE_ORIGINAL_COLLECTED":
                raise ValueError("P001_TRANSPORT_COLLECTION_INCOMPLETE")
            collected[role] = result
            if role == "terminal":
                with regular_file(broker.root / ids[role] / "original") as original:
                    raw_terminal = original.read(RECEIPT_CAP + 1)
                terminal = validate_terminal(raw_terminal, request)
                if terminal["zip_bytes"] != sizes["zip"] or terminal["zip_bytes"] + len(raw_terminal) > TRANSFER_CAP:
                    raise ValueError("P001_TRANSPORT_COMBINED_TRANSFER_CAP")
        if (collected["zip"]["sha256"] != terminal["zip_sha256"] or
                collected["zip"]["bytes"] != terminal["zip_bytes"]):
            raise ValueError("P001_TRANSPORT_TERMINAL_ZIP_IDENTITY")
        after = {role: slot_metadata(broker.client, value["slots"][role]["id"]) for role in ROLES}
        if before != after:
            raise ValueError("P001_TRANSPORT_PAIR_CHANGED_DURING_COLLECTION")
        private_write(root / "metadata-after-pair.json", after)
        receipt = {"schema": "p001-return-pair-collection/v1",
            "status": "SYNTHETIC_ORIGINAL_IDS_AND_BYTES_VERIFIED" if value["purpose"] == "SYNTHETIC_CANARY" else "PRIVATE_PAIR_COLLECTED_PENDING_FROZEN_VALIDATION",
            "slot_binding_sha256": value["binding_sha256"], "launch_manifest_sha256": request["launch_manifest_sha256"],
            "purpose": value["purpose"], "request_id": request_id, "combined_transfer_bytes": sum(row["bytes"] for row in collected.values()),
            "zip_sha256": terminal["zip_sha256"], "terminal_sha256": digest(raw_terminal),
            "collection_request_ids": ids, "originals_preserved": True, "scientific_acceptance": False,
            "os_exit_independently_observed": False}
        private_write(root / "receipt.json", receipt)
        return receipt
    except Exception as error:
        private_write(root / "failure.json", {"exception_type": type(error).__name__, "detail": str(error), "automatic_retry": False})
        return blocked()
