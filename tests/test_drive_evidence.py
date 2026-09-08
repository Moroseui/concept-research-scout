import hashlib
import json
from pathlib import Path
import pytest
from orchestrator.drive_evidence import DriveEvidence
from scripts.drive_consent import callback_fields


class FakeDrive:
    def __init__(self):
        self.data = {"console-id": b"original console\n"}
        self.reads = 0
        self.uploads = 0
        self.changed = False

    def metadata(self, id):
        data = self.data[id]
        return {
            "id": id,
            "name": "console.log",
            "size": str(len(data)),
            "mimeType": "text/plain",
            "version": "2" if self.changed and self.reads else "1",
            "md5Checksum": hashlib.md5(data).hexdigest(),
        }

    def download(self, id, out, maximum):
        self.reads += 1
        out.write(self.data[id])

    def private_folder(self, id):
        pass

    def allocate_ids(self, n):
        return ["new-id-" + str(i) for i in range(n)]

    def create(self, id, name, parent, data=None):
        self.uploads += 1
        if data is None:
            return {}
        self.data[id] = data
        return {"size": str(len(data)), "md5Checksum": hashlib.md5(data).hexdigest()}


@pytest.fixture
def setup(tmp_path):
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    spool = tmp_path / "spool"
    spool.mkdir()
    config = {
        "version": 1,
        "mode": "REGISTERED_EVIDENCE_ONLY",
        "private_root": str(root),
        "upload_spool": str(spool),
        "output_folder_id": "private-folder",
        "caller_uids": [42],
        "files": {
            "047-console": {
                "id": "console-id",
                "expected_name": "console.log",
                "access": "small-evidence-read",
                "max_bytes": 1000,
            },
            "archive": {
                "id": "archive-id",
                "expected_name": "train.7z",
                "access": "metadata-only",
            },
        },
    }
    client = FakeDrive()
    return DriveEvidence(config, client), client, root, spool


def request(operation="collect", alias="047-console", id="receipt-0001"):
    return {"operation": operation, "body": {"alias": alias, "request_id": id}}


def test_collect_recovery_no_duplicate_and_no_payload_reply(setup):
    broker, client, root, _ = setup
    result = broker.handle(request(), 42)
    assert result["status"] == "PRIVATE_ORIGINAL_COLLECTED"
    assert client.reads == 1 and b"original console" not in json.dumps(result).encode()
    assert broker.handle(request(), 42) == result and client.reads == 1
    recreated = DriveEvidence(broker.config, client)
    assert recreated.handle(request("status"), 42) == result and client.reads == 1
    assert (root / "receipt-0001" / "original").read_bytes() == client.data[
        "console-id"
    ]


def test_uid_alias_archive_and_replay_binding_refused(setup):
    b, c, _, _ = setup
    for req, uid in [
        (request(), 43),
        (request(alias="unknown"), 42),
        (request(alias="archive"), 42),
    ]:
        with pytest.raises(ValueError):
            b.handle(req, uid)
    b.handle(request("metadata"), 42)
    with pytest.raises(ValueError, match="CONFLICT"):
        b.handle(request(), 42)
    assert c.reads == 0


def test_changed_remote_and_crash_intent_preserve_failure(setup):
    b, c, root, _ = setup
    c.changed = True
    assert b.handle(request(), 42)["status"] == "BLOCKED_RECONCILE"
    assert (root / "receipt-0001" / "original.part").exists()
    assert b.handle(request(), 42)["status"] == "BLOCKED_RECONCILE" and c.reads == 1
    (root / "interrupted-0001").mkdir()
    assert b.handle(request(id="interrupted-0001"), 42)["status"] == "BLOCKED_RECONCILE"


def test_storage_collects_console_receipt_and_verifies_retrieval(setup):
    b, c, root, spool = setup
    run = spool / "run-00001"
    run.mkdir()
    (run / "console.log").write_bytes(b"console")
    (run / "receipt.json").write_text("{}")
    (run / "notebook.ipynb").write_text("{}")
    req = request("store", "run-artifacts", "run-00001")
    result = b.handle(req, 42)
    assert result["status"] == "PRIVATE_RUN_STORED" and result["file_count"] == 3
    assert c.uploads == 4 and c.reads == 3
    assert b.handle(req, 42) == result and c.uploads == 4
    (run / "receipt.json").write_text('{"changed":true}')
    with pytest.raises(ValueError, match="CONFLICT"):
        b.handle(req, 42)


def test_upload_missing_console_and_partial_outcome_not_retried(setup):
    b, c, root, spool = setup
    run = spool / "run-00001"
    run.mkdir()
    (run / "receipt.json").write_text("{}")
    with pytest.raises(ValueError, match="CONSOLE"):
        b.handle(request("store", "run-artifacts", "run-00001"), 42)
    (run / "console.log").write_text("console")
    folder = root / "upload-run-00001"
    folder.mkdir()
    assert (
        b.handle(request("store", "run-artifacts", "run-00001"), 42)["status"]
        == "UPLOAD_OUTCOME_UNCERTAIN"
    )
    assert c.uploads == 0


def test_picker_callback_state_and_actual_ids():
    assert callback_fields(
        "http://localhost/?state=secret&code=private&picked_file_ids=file-123,file-456",
        "secret",
    ) == ["file-123", "file-456"]
    for query in [
        "state=wrong&code=x&picked_file_ids=file-123",
        "state=secret&code=x",
        "state=secret&error=denied",
    ]:
        with pytest.raises(ValueError):
            callback_fields("http://localhost/?" + query, "secret")


def test_concurrent_duplicate_collection_dispatches_once(setup):
    from concurrent.futures import ThreadPoolExecutor

    b, c, _, _ = setup

    def call():
        try:
            return b.handle(request(), 42)
        except (FileExistsError, ValueError):
            return {"status": "RECONCILE"}

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: call(), range(4)))
    assert c.reads == 1
    assert b.handle(request("status"), 42)["status"] == "PRIVATE_ORIGINAL_COLLECTED"


def test_upload_credentials_refused_before_network(setup):
    b, c, _, spool = setup
    run = spool / "run-00001"
    run.mkdir()
    (run / "receipt.json").write_text("{}")
    (run / "console.log").write_text("gh" + "p_" + "x" * 30)
    with pytest.raises(ValueError, match="CREDENTIAL"):
        b.handle(request("store", "run-artifacts", "run-00001"), 42)
    assert c.uploads == 0


def test_upload_status_survives_spool_cleanup_and_restart(setup):
    import shutil

    b, c, root, spool = setup
    run = spool / "run-00001"
    run.mkdir()
    (run / "console.log").write_text("console")
    (run / "receipt.json").write_text("{}")
    result = b.handle(request("store", "run-artifacts", "run-00001"), 42)
    shutil.rmtree(run)
    restored = DriveEvidence(b.config, c)
    assert (
        restored.handle(request("status", "run-artifacts", "run-00001"), 42) == result
    )
    assert c.uploads == 3 and c.reads == 2


def test_controller_staging_preserves_originals_and_sets_private_group_modes(setup):
    import os
    from orchestrator.drive_evidence import stage_run_bundle

    b, c, root, spool = setup
    spool.chmod(0o2750)
    source = root / "source"
    source.mkdir()
    (source / "console.log").write_text("console")
    (source / "receipt.json").write_text("{}")
    result = stage_run_bundle(source, spool, "run-00001")
    assert result["status"] == "STAGED_PRIVATELY"
    assert (spool / "run-00001").stat().st_mode & 0o2777 == 0o2750
    assert (spool / "run-00001" / "console.log").stat().st_mode & 0o777 == 0o640
    assert (source / "console.log").read_text() == "console"
    with pytest.raises(ValueError, match="EXISTING"):
        stage_run_bundle(source, spool, "run-00001")
    assert (
        b.handle(request("store", "run-artifacts", "run-00001"), 42)["status"]
        == "PRIVATE_RUN_STORED"
    )


def test_bookkeeping_namespace_and_reserved_alias(setup):
    b, c, root, _ = setup
    for operation, alias in [
        ("collect", "047-console"),
        ("store", "run-artifacts"),
        ("status", "run-artifacts"),
    ]:
        with pytest.raises(ValueError, match="NAMESPACE"):
            b.handle(request(operation, alias, "upload-run-0001"), 42)
    bad = dict(b.config, files={"run-artifacts": b.config["files"]["047-console"]})
    with pytest.raises(ValueError, match="RESERVED_DRIVE_ALIAS"):
        DriveEvidence(bad, c)
    folder = root / "upload-run-0001"
    folder.mkdir()
    (folder / "receipt.json").write_text(
        json.dumps({"stage": "drive-evidence", "request_id": "run-0001"})
    )
    with pytest.raises(ValueError, match="RECEIPT_KIND"):
        b.handle(request("status", "run-artifacts", "run-0001"), 42)
