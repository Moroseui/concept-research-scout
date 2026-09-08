#!/usr/bin/env python3
"""Operator setup: register actual picked Drive IDs and a fresh private output root.

Run only after the concrete credential/access grant is approved. Never downloads
archive content, moves originals, overwrites configuration or repeats a partial
setup. Metadata and remote creation intent remain private for reconciliation.
"""

import argparse
import json
import os
from pathlib import Path
import pwd
from orchestrator.drive_evidence import GoogleDrive, private_write
from orchestrator.phone_notifications import protected_read

EXPECTED = {
    "047_B_dc586665d0be.console.log": ("047-console", "small-evidence-read"),
    "train.7z": ("p001-archive", "metadata-only"),
    # Existing outputs from the separately authorized admission-only preflight.
    # Selection registers evidence, not a new patient execution or image transfer.
    "receipt.json": ("p001-preflight-receipt", "small-evidence-read"),
    "preflight.console.log": ("p001-preflight-console", "small-evidence-read"),
    "admission_headers.private.json": ("p001-preflight-headers", "small-evidence-read"),
}


def register(consent_dir, destination):
    if os.getuid() != 0:
        raise ValueError("OPERATOR_SETUP_ADMIN_REQUIRED")
    consent_dir, destination = Path(consent_dir), Path(destination)
    if (
        destination.exists()
        or destination.parent.is_symlink()
        or destination.parent.stat().st_mode & 0o077
    ):
        raise ValueError("FRESH_PROTECTED_REGISTRATION_REQUIRED")
    selected = json.loads(protected_read(consent_dir / "picked-files.json"))["file_ids"]
    if not 1 <= len(selected) <= 5:
        raise ValueError("BOUNDED_SELECTED_FILES_REQUIRED")
    client = GoogleDrive(consent_dir / "oauth.json")
    destination.mkdir(mode=0o700)
    metadata = []
    files = {}
    for ordinal, file_id in enumerate(selected):
        value = client.metadata(file_id)
        private_write(destination / f"selected-{ordinal}.json", value)
        metadata.append(value)
        if value["name"] not in EXPECTED:
            continue
        alias, access = EXPECTED[value["name"]]
        if alias in files:
            raise ValueError("AMBIGUOUS_SELECTED_FILES_OPERATOR_CHOICE_REQUIRED")
        if value.get("trashed"):
            raise ValueError("SELECTED_FILE_TRASHED")
        if alias == "p001-archive" and (
            int(value.get("size", 0)) != 99014629647
            or value.get("md5Checksum") != "36ae28b9a17f7340b8bbef62b595cb57"
        ):
            raise ValueError("ARCHIVE_METADATA_IDENTITY_MISMATCH_NO_DOWNLOAD")
        files[alias] = {
            "id": file_id,
            "expected_name": value["name"],
            "access": access,
            "max_bytes": (
                0
                if access == "metadata-only"
                else (
                    65536
                    if alias in ("p001-preflight-receipt", "p001-preflight-headers")
                    else 32 * 1024 * 1024
                )
            ),
        }
    private_write(destination / "selected-metadata.json", metadata)
    # A missing historical console must not block authorized P001 evidence.
    # Unknown selections alone cannot create a destination folder.
    if not files:
        raise ValueError("NO_SUPPORTED_EVIDENCE_SELECTED")
    ids = client.allocate_ids(1)
    private_write(
        destination / "folder-intent.json",
        {"folder_id": ids[0], "name": "research-system", "parent": "root"},
    )
    client.create(ids[0], "research-system", "root")
    client.private_folder(ids[0])
    config = {
        "version": 1,
        "mode": "REGISTERED_EVIDENCE_ONLY",
        "caller_uids": [
            pwd.getpwnam(name).pw_uid
            for name in ("research-controller", "research-driver")
        ],
        "private_root": "/var/lib/research-system/drive-evidence",
        "upload_spool": "/var/lib/research-system/drive-upload-spool",
        "output_folder_id": ids[0],
        "files": files,
    }
    private_write(destination / "config.json", config)
    private_write(
        destination / "registration-receipt.json",
        {
            "status": "REGISTERED_NOT_INSTALLED",
            "aliases": list(files),
            "output_folder_id": ids[0],
            "archive_downloaded": False,
            "originals_moved": False,
        },
    )
    print(
        json.dumps(
            {
                "status": "REGISTERED_NOT_INSTALLED",
                "aliases": list(files),
                "archive_downloaded": False,
                "originals_moved": False,
            }
        )
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--consent-dir", required=True)
    p.add_argument("--private-destination", required=True)
    a = p.parse_args()
    register(a.consent_dir, a.private_destination)
