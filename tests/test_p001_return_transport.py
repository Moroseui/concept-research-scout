"""Offline transport tests: synthetic bytes, fake Drive, no credentials or patient run."""
import copy
import hashlib
import io
import json
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator import p001_return_transport as transport
from orchestrator.drive_evidence import DriveEvidence


class FakeDrive:
    def __init__(self):
        self.data, self.names, self.parents = {}, {}, {}
        self.allocations, self.creates, self.downloads, self.calls = 0, [], [], []
        self.fail_create = None
        self.api = self

    def files(self):
        return self

    def get(self, fileId, fields):
        assert "parents" in fields and "ownedByMe" in fields
        return SimpleNamespace(execute=lambda num_retries: self.metadata(fileId))

    def private_folder(self, file_id):
        assert file_id == "approved-private-folder"
        self.calls.append(("private_folder", file_id))

    def allocate_ids(self, count):
        self.allocations += 1
        assert count == 2
        return ["slot-id-" + str(self.allocations) + "-" + str(i) for i in range(count)]

    def create(self, file_id, name, parent, data=None):
        self.creates.append(file_id)
        assert file_id not in self.data
        if len(self.creates) == self.fail_create:
            raise OSError("synthetic uncertain creation")
        self.data[file_id], self.names[file_id], self.parents[file_id] = data, name, parent
        return self.metadata(file_id)

    def metadata(self, file_id):
        data = self.data[file_id]
        return {"id": file_id, "name": self.names[file_id], "size": str(len(data)),
            "mimeType": "application/octet-stream", "version": hashlib.md5(data).hexdigest(),
            "md5Checksum": hashlib.md5(data).hexdigest(), "parents": [self.parents[file_id]],
            "ownedByMe": True, "permissions": [{"type": "user", "role": "owner"}]}

    def download(self, file_id, output, maximum):
        self.downloads.append((file_id, maximum))
        if len(self.data[file_id]) > maximum:
            raise ValueError("synthetic size bound")
        output.write(self.data[file_id])


@pytest.fixture
def state(tmp_path):
    tmp_path.chmod(0o700)
    for name in ("reservations", "collections", "broker", "mount"):
        (tmp_path / name).mkdir(mode=0o700)
    client = FakeDrive()
    config = {"version": 1, "mode": "REGISTERED_EVIDENCE_ONLY",
        "private_root": str(tmp_path / "broker"), "output_folder_id": "approved-private-folder",
        "caller_uids": [42], "files": {}}
    return {"root": tmp_path, "client": client, "config": config}


def reserve(state, purpose="SYNTHETIC_CANARY"):
    value = transport.reserve_slots(state["client"], state["config"],
        state["root"] / "reservations", "p001-test-001", purpose=purpose)
    state["reservation"] = value
    return value


def packet(state, purpose="SYNTHETIC_CANARY"):
    value = state.get("reservation") or reserve(state, purpose)
    result = transport.prepare_copy(value, "/content/drive/MyDrive/synthetic-output",
        runtime_fingerprint="a" * 64, launch_manifest_sha256="b" * 64, max_extracted_bytes=65536,
        worker_parameters_sha256="c" * 64 if purpose == "PATIENT_RETURN" else None,
        canary_receipt_sha256="d" * 64 if purpose == "PATIENT_RETURN" else None)
    state["packet"] = result
    return result


def observed(request):
    return {"runtime": {"fingerprint_sha256": "a" * 64},
        "cpu_guard": {"colab_runtime": True, "nvidia_smi_absent": True},
        "drive": {"mounted": True, "visible": True},
        "processes": {"scan_complete": True, "matches": []},
        "source_files": [{"matches_expected": True}]}


def synthetic_patient_members():
    members = {"bundle/" + name for name in transport.AGGREGATES} | {"console.log", "private/binding.json", "private/checkpoint_index.json"}
    members.update("private/checkpoints/synthetic-" + str(i) + ".json" for i in range(99))
    members.update("private/predictions/synthetic-" + str(i) + ".npy" for i in range(99))
    return members


def synthetic_patient_zip():
    result = io.BytesIO()
    with zipfile.ZipFile(result, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(synthetic_patient_members()):
            archive.writestr(name, b"synthetic nonclinical fixture")
    return result.getvalue()


def local_copy(state, monkeypatch, purpose="SYNTHETIC_CANARY"):
    bound = state.get("packet") or packet(state, purpose)
    request = copy.deepcopy(bound["request"])
    for role in transport.ROLES:
        path = state["root"] / "mount" / state["reservation"]["slots"][role]["name"]
        path.write_bytes(transport.marker(state["reservation"], role))
        request["slots"][role]["path"] = str(path)
    request["intent_path"] = str(state["root"] / "copy-intent.json")
    if purpose == "PATIENT_RETURN":
        (state["root"] / "worker").mkdir(mode=0o700)
        for key, name, data in [
            ("source_zip", "original.zip", synthetic_patient_zip()),
            ("worker_status", "status.json", b'{"status":"VALIDATED"}'),
            ("worker_parameters", "parameters.json", b'{"synthetic":"parameters"}'),
        ]:
            path = state["root"] / "worker" / name
            path.write_bytes(data)
            request[key] = str(path)
        request["worker_parameters_sha256"] = hashlib.sha256((state["root"] / "worker/parameters.json").read_bytes()).hexdigest()
        monkeypatch.setattr(transport, "runtime_member_names", lambda request: synthetic_patient_members())
    monkeypatch.setattr(transport, "runtime_observation", observed)
    return request


def sync_fake_mount(state, request):
    for role in transport.ROLES:
        file_id = state["reservation"]["slots"][role]["id"]
        state["client"].data[file_id] = Path(request["slots"][role]["path"]).read_bytes()


def broker(state):
    state["config"]["files"].update(transport.alias_proposal(state["reservation"]))
    return DriveEvidence(state["config"], state["client"])


def test_reservation_allocates_once_persists_ids_and_only_proposes_aliases(state):
    value = reserve(state)
    assert value["status"] == "RESERVED_MARKERS_VERIFIED"
    assert state["client"].allocations == 1 and len(state["client"].creates) == 2
    assert state["config"]["files"] == {}
    folder = state["root"] / "reservations/p001-test-001"
    assert json.loads((folder / "intent.json").read_text())["slots"] == value["slots"]
    assert json.loads((folder / "protected-alias-proposal.json").read_text()) == transport.alias_proposal(value)
    assert len({transport.marker(value, role) for role in transport.ROLES}) == 2
    before = len(state["client"].calls)
    assert reserve(state) == value
    assert len(state["client"].calls) == before and state["client"].allocations == 1


def test_uncertain_slot_create_preserves_exact_ids_and_never_retries(state):
    state["client"].fail_create = 2
    assert reserve(state)["status"] == "BLOCKED_RECONCILE"
    folder = state["root"] / "reservations/p001-test-001"
    assert (folder / "intent.json").is_file() and (folder / "failure.json").is_file()
    assert reserve(state)["status"] == "BLOCKED_RECONCILE"
    assert state["client"].allocations == 1 and len(state["client"].creates) == 2


@pytest.mark.parametrize("field", ["parents", "ownedByMe", "permissions"])
def test_reservation_checks_actual_child_parent_and_private_ownership(state, monkeypatch, field):
    original = state["client"].metadata
    def altered(file_id):
        value = original(file_id)
        value[field] = ["wrong-parent"] if field == "parents" else False if field == "ownedByMe" else [{"type": "anyone", "role": "reader"}]
        return value
    monkeypatch.setattr(state["client"], "metadata", altered)
    assert reserve(state)["status"] == "BLOCKED_RECONCILE"
    assert state["client"].downloads == []


def test_packet_is_exact_bounded_and_contains_no_ids_or_credentials(state):
    value = packet(state)
    transport.verify_packet(state["reservation"], value)
    text = json.dumps(value)
    assert all(slot["id"] not in text for slot in state["reservation"]["slots"].values())
    assert "approved-private-folder" not in text
    assert "SYNTHETIC_CANARY_ONLY" == value["authority"]
    assert len(value["cells"]) == 2
    assert value["request"]["transfer_cap"] == 32 * 1024 * 1024
    value["request"]["max_extracted_bytes"] += 1
    with pytest.raises(ValueError, match="PACKET_NOT_EXACT"):
        transport.verify_packet(state["reservation"], value)


def test_patient_packet_requires_worker_binding_and_completed_canary(state):
    reserve(state, "PATIENT_RETURN")
    with pytest.raises(ValueError, match="SHA256"):
        transport.prepare_copy(state["reservation"], "/content/drive/MyDrive/synthetic-output",
            runtime_fingerprint="a" * 64, launch_manifest_sha256="b" * 64, max_extracted_bytes=65536)
    value = packet(state, "PATIENT_RETURN")
    assert value["request"]["source_zip"] == "/content/drive/MyDrive/isles-pilot/P001-v1.worker/P001-private-return.zip"
    assert "REQUIRES_EXACT_LAUNCH" in value["authority"]


def test_copy_preserves_existing_inodes_writes_receipt_last_and_intent(state, monkeypatch):
    request = local_copy(state, monkeypatch)
    identities = {role: Path(request["slots"][role]["path"]).stat().st_ino for role in transport.ROLES}
    result = transport.copy_return(request)
    assert result["status"] == "COPIED_PENDING_ORIGINAL_ID_READBACK"
    assert result["scientific_acceptance"] is False and result["os_exit_independently_observed"] is False
    for role in transport.ROLES:
        assert Path(request["slots"][role]["path"]).stat().st_ino == identities[role]
    assert Path(request["intent_path"]).is_file()
    terminal = Path(request["slots"]["terminal"]["path"]).read_bytes()
    assert transport.validate_terminal(terminal, state["packet"]["request"])["worker_status"] == "SYNTHETIC_CANARY"
    with pytest.raises(ValueError, match="MARKER_MISMATCH"):
        transport.copy_return(request)


@pytest.mark.parametrize("failure", ["runtime", "process", "incomplete", "drive"])
def test_runtime_and_current_process_guards_block_before_write(state, monkeypatch, failure):
    request = local_copy(state, monkeypatch)
    value = observed(request)
    if failure == "runtime":
        value["runtime"]["fingerprint_sha256"] = "different"
    elif failure == "process":
        value["processes"]["matches"] = [{"pid": 123}]
    elif failure == "incomplete":
        value["processes"]["scan_complete"] = False
    else:
        value["drive"]["mounted"] = False
    monkeypatch.setattr(transport, "runtime_observation", lambda request: value)
    with pytest.raises(ValueError, match="P001_COPY_"):
        transport.copy_return(request)
    assert not Path(request["intent_path"]).exists()


@pytest.mark.parametrize("failure", ["source", "worker", "parameters"])
def test_patient_copy_requires_original_source_terminal_and_parameters(state, monkeypatch, failure):
    request = local_copy(state, monkeypatch, "PATIENT_RETURN")
    if failure == "source":
        value = observed(request)
        value["source_files"] = [{"matches_expected": False}]
        monkeypatch.setattr(transport, "runtime_observation", lambda request: value)
    elif failure == "worker":
        Path(request["worker_status"]).write_text('{"status":"RUNNING"}')
    else:
        Path(request["worker_parameters"]).write_text('{"changed":true}')
    with pytest.raises(ValueError, match="P001_COPY_"):
        transport.copy_return(request)
    assert not Path(request["intent_path"]).exists()


def test_wrong_mounted_folder_marker_and_prior_intent_refuse_without_overwrite(state, monkeypatch):
    request = local_copy(state, monkeypatch)
    zip_path = Path(request["slots"]["zip"]["path"])
    zip_path.write_bytes(b"unrelated existing file")
    with pytest.raises(ValueError, match="MARKER"):
        transport.copy_return(request)
    assert zip_path.read_bytes() == b"unrelated existing file"
    zip_path.write_bytes(transport.marker(state["reservation"], "zip"))
    Path(request["intent_path"]).write_bytes(b"interrupted intent")
    with pytest.raises(FileExistsError):
        transport.copy_return(request)
    assert zip_path.read_bytes() == transport.marker(state["reservation"], "zip")


def test_combined_copy_limit_accounts_for_receipt_before_any_slot_write(state, monkeypatch):
    request = local_copy(state, monkeypatch)
    request["transfer_cap"] = len(transport.synthetic_zip()) + 1
    with pytest.raises(ValueError, match="COMBINED_TRANSFER_CAP"):
        transport.copy_return(request)
    assert not Path(request["intent_path"]).exists()


def test_copy_partial_write_leaves_terminal_marker_and_refuses_retry(state, monkeypatch):
    request = local_copy(state, monkeypatch)
    original_fsync = transport.os.fsync
    calls = []
    def interrupted_fsync(fd):
        calls.append(fd)
        if len(calls) == 3:
            raise OSError("synthetic interruption after ZIP write")
        return original_fsync(fd)
    monkeypatch.setattr(transport.os, "fsync", interrupted_fsync)
    with pytest.raises(OSError):
        transport.copy_return(request)
    assert Path(request["slots"]["terminal"]["path"]).read_bytes() == transport.marker(state["reservation"], "terminal")
    assert Path(request["intent_path"]).exists()
    with pytest.raises(ValueError, match="MARKER"):
        transport.copy_return(request)


def test_canary_pair_collects_original_ids_with_aggregate_bound_and_private_originals(state, monkeypatch):
    request = local_copy(state, monkeypatch)
    transport.copy_return(request)
    sync_fake_mount(state, request)
    monkeypatch.undo()
    b = broker(state)
    previous = len(state["client"].downloads)
    result = transport.collect_pair(b, state["reservation"], state["root"] / "collections",
        "p001-collect-001", 42, state["packet"])
    assert result["status"] == "SYNTHETIC_ORIGINAL_IDS_AND_BYTES_VERIFIED"
    assert result["scientific_acceptance"] is False
    calls = state["client"].downloads[previous:]
    assert [row[0] for row in calls] == [state["reservation"]["slots"][r]["id"] for r in ("terminal", "zip")]
    assert calls[-1][1] == len(transport.synthetic_zip())
    assert (b.root / "p001-collect-001-zip/original").read_bytes() == transport.synthetic_zip()
    assert transport.collect_pair(b, state["reservation"], state["root"] / "collections",
        "p001-collect-001", 42, state["packet"])["status"] == "BLOCKED_RECONCILE"
    assert len(state["client"].downloads) == previous + 2


def test_missing_protected_aliases_refuse_before_network(state):
    packet(state)
    b = DriveEvidence(state["config"], state["client"])
    previous = len(state["client"].calls)
    with pytest.raises(ValueError, match="PROTECTED_ALIASES"):
        transport.collect_pair(b, state["reservation"], state["root"] / "collections",
            "p001-collect-001", 42, state["packet"])
    assert len(state["client"].calls) == previous


def test_invalid_terminal_stops_before_zip_download_and_preserves_partial(state, monkeypatch):
    request = local_copy(state, monkeypatch)
    transport.copy_return(request)
    sync_fake_mount(state, request)
    monkeypatch.undo()
    terminal_id = state["reservation"]["slots"]["terminal"]["id"]
    state["client"].data[terminal_id] = b'{"unexpected":true}'
    b = broker(state)
    previous = len(state["client"].downloads)
    assert transport.collect_pair(b, state["reservation"], state["root"] / "collections",
        "p001-collect-001", 42, state["packet"])["status"] == "BLOCKED_RECONCILE"
    assert state["client"].downloads[previous:] == [(terminal_id, transport.RECEIPT_CAP)]
    assert (b.root / "p001-collect-001-terminal/original").is_file()


def test_canary_detects_fuse_replacement_ids_even_when_names_stay_same(state, monkeypatch):
    request = local_copy(state, monkeypatch)
    transport.copy_return(request)
    monkeypatch.undo()
    # Model a FUSE implementation that created replacements; API original IDs retain markers.
    b = broker(state)
    result = transport.collect_pair(b, state["reservation"], state["root"] / "collections",
        "p001-collect-001", 42, state["packet"])
    assert result["status"] == "BLOCKED_RECONCILE"
    assert not (b.root / "p001-collect-001-zip").exists()


def test_generated_cell_body_executes_same_synthetic_copy_logic(state, monkeypatch):
    request = local_copy(state, monkeypatch)
    # Execute exact generated definitions, substituting only a synthetic observation fixture.
    namespace = {}
    exec(state["packet"]["cells"][1].split("\nimport json\ntry:\n")[0], namespace)
    namespace["runtime_observation"] = observed
    assert namespace["copy_return"](request)["status"] == "COPIED_PENDING_ORIGINAL_ID_READBACK"


def test_copy_refuses_replaced_original_path_before_writing_terminal(state, monkeypatch):
    request = local_copy(state, monkeypatch, "PATIENT_RETURN")
    original_fsync = transport.os.fsync
    calls = []
    def replace_after_zip_copy(fd):
        calls.append(fd)
        if len(calls) == 3:
            original = Path(request["source_zip"])
            original.rename(original.with_suffix(".preserved.zip"))
            original.write_bytes(b"different output at original path")
        return original_fsync(fd)
    monkeypatch.setattr(transport.os, "fsync", replace_after_zip_copy)
    with pytest.raises(ValueError, match="SOURCE_OR_STATUS_CHANGED"):
        transport.copy_return(request)
    assert Path(request["slots"]["terminal"]["path"]).read_bytes() == transport.marker(state["reservation"], "terminal")


def test_collection_combined_limit_refuses_before_either_download(state, monkeypatch):
    request = local_copy(state, monkeypatch)
    transport.copy_return(request)
    sync_fake_mount(state, request)
    monkeypatch.undo()
    b = broker(state)
    original = state["client"].metadata
    def oversized(file_id):
        value = original(file_id)
        if file_id == state["reservation"]["slots"]["zip"]["id"]:
            value["size"] = str(transport.TRANSFER_CAP)
        return value
    monkeypatch.setattr(state["client"], "metadata", oversized)
    previous = len(state["client"].downloads)
    assert transport.collect_pair(b, state["reservation"], state["root"] / "collections",
        "p001-collect-001", 42, state["packet"])["status"] == "BLOCKED_RECONCILE"
    assert len(state["client"].downloads) == previous


def test_extra_original_zip_member_is_refused_before_any_transfer(state, monkeypatch):
    request = local_copy(state, monkeypatch, "PATIENT_RETURN")
    with zipfile.ZipFile(request["source_zip"], "a") as archive:
        archive.writestr("private/failed_attempts/unexpected.json", b"synthetic")
    with pytest.raises(ValueError, match="P001_RETURN_ZIP_DIRECTORY"):
        transport.copy_return(request)
    assert not Path(request["intent_path"]).exists()
    assert Path(request["slots"]["zip"]["path"]).read_bytes() == transport.marker(state["reservation"], "zip")


def test_generated_patient_cell_preserves_complete_member_scope_before_copy(state, monkeypatch):
    request = local_copy(state, monkeypatch, "PATIENT_RETURN")
    namespace = {}
    exec(state["packet"]["cells"][1].split("\nimport json\ntry:\n")[0], namespace)
    namespace["runtime_observation"] = observed
    namespace["runtime_member_names"] = lambda request: synthetic_patient_members()
    result = namespace["copy_return"](request)
    assert result["status"] == "COPIED_PENDING_ORIGINAL_ID_READBACK"
    terminal = Path(request["slots"]["terminal"]["path"]).read_bytes()
    assert transport.validate_terminal(terminal, request)["worker_status"] == "VALIDATED"


def test_runtime_member_derivation_reuses_selection_only(monkeypatch):
    def run(command, **kwargs):
        assert command[1:4] == ["-B", "-I", "-c"]
        assert "module.selection()" in command[4] and "module.run(" not in command[4]
        assert kwargs["capture_output"] is True
        return SimpleNamespace(returncode=0, stdout=json.dumps(["synthetic-" + str(i) for i in range(99)]).encode())
    monkeypatch.setattr("subprocess.run", run)
    assert transport.runtime_member_names({"source_root": "/synthetic/frozen"}) == synthetic_patient_members()
