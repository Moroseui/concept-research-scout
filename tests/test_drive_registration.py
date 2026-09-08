"""Selected-ID registration fixtures; no Google calls or real credentials."""

import json
from pathlib import Path
from types import SimpleNamespace
import pytest
import scripts.drive_register as registration


@pytest.fixture
def registry_setup(tmp_path, monkeypatch):
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    names = list(registration.EXPECTED)
    selected = ["selected-" + str(i) for i in range(len(names))]
    metadata = {
        i: {
            "id": i,
            "name": n,
            "size": "50",
            "md5Checksum": "synthetic",
            "version": "1",
        }
        for i, n in zip(selected, names)
    }
    archive = next(v for v in metadata.values() if v["name"] == "train.7z")
    archive.update(size="99014629647", md5Checksum="36ae28b9a17f7340b8bbef62b595cb57")

    class Client:
        def metadata(self, file_id):
            return metadata[file_id]

        def allocate_ids(self, count):
            return ["new-private-folder"]

        def create(self, *args):
            pass

        def private_folder(self, *args):
            pass

    monkeypatch.setattr(registration.os, "getuid", lambda: 0)
    monkeypatch.setattr(
        registration,
        "protected_read",
        lambda p: json.dumps({"file_ids": selected}).encode(),
    )
    monkeypatch.setattr(registration, "GoogleDrive", lambda p: Client())
    monkeypatch.setattr(
        registration.pwd,
        "getpwnam",
        lambda p: SimpleNamespace(pw_uid=42 if p == "research-controller" else 43),
    )
    return parent, metadata, archive


def test_actual_selected_ids_registered_without_download(registry_setup):
    parent, metadata, _ = registry_setup
    registration.register(parent / "consent", parent / "registered")
    config = json.loads((parent / "registered" / "config.json").read_text())
    assert len(config["files"]) == 5
    assert {v["id"] for v in config["files"].values()} == set(metadata)
    assert config["files"]["p001-archive"]["max_bytes"] == 0
    assert config["files"]["p001-preflight-headers"]["max_bytes"] == 65536
    assert config["files"]["p001-preflight-receipt"]["max_bytes"] == 65536
    assert len(list((parent / "registered").glob("selected-[0-9].json"))) == 5


def test_mismatched_archive_metadata_remains_preserved(registry_setup):
    parent, metadata, archive = registry_setup
    archive["size"] = "1"
    with pytest.raises(ValueError, match="ARCHIVE_METADATA"):
        registration.register(parent / "consent", parent / "registered")
    saved = [
        json.loads(p.read_text())
        for p in (parent / "registered").glob("selected-[0-9].json")
    ]
    assert any(v["name"] == "train.7z" and v["size"] == "1" for v in saved)
    assert not (parent / "registered" / "config.json").exists()
