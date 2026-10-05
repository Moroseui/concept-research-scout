"""Deterministic private membership and comparison-identity validation.

No patient computation, model invocation or modification of original results.
"""
import hashlib
import json
from pathlib import Path


def load_exclusions(reference, split_manifest_path, split_sha256):
    if set(reference) != {"path", "sha256", "count"} or type(reference["count"]) is not int or reference["count"] < 0:
        raise ValueError("EXCLUSIONS_REFERENCE_INVALID")
    path = Path(reference["path"])
    split_path = Path(split_manifest_path)
    if path.is_symlink() or split_path.is_symlink() or path.resolve().parent != split_path.resolve().parent:
        raise ValueError("EXCLUSIONS_MUST_BE_BESIDE_SPLIT_MANIFEST")
    split_raw = split_path.read_bytes()
    if hashlib.sha256(split_raw).hexdigest() != split_sha256:
        raise ValueError("SPLIT_MANIFEST_HASH_MISMATCH")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != reference["sha256"]:
        raise ValueError("EXCLUSIONS_HASH_MISMATCH")
    values = json.loads(raw)
    if (not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values)
            or len(set(values)) != len(values) or len(values) != reference["count"]):
        raise ValueError("EXCLUSIONS_COUNT_OR_MEMBERSHIP_INVALID")
    return frozenset(values)


def comparison_fingerprint(identity):
    return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:12]


def validate_comparison_reference(record, reference, split_manifest_path, split_sha256):
    # Reread the private reference so a stale report never authorizes changed membership.
    load_exclusions(reference, split_manifest_path, split_sha256)
    identity = record["run_identity"]
    if (identity.get("exclusions_sha256") != reference["sha256"]
            or identity.get("exclusions_count") != reference["count"]
            or identity.get("split_manifest_sha256") != split_sha256):
        raise ValueError("COMPARISON_EXCLUSIONS_BINDING_MISMATCH")
    if record.get("fingerprint") != comparison_fingerprint(identity):
        raise ValueError("COMPARISON_FINGERPRINT_MISMATCH")
    return {"status": "REFERENCE_INTEGRITY_VALID", "scientific_acceptance": False,
            "exclusions_sha256": reference["sha256"], "exclusions_count": reference["count"],
            "split_manifest_sha256": split_sha256, "fingerprint": record["fingerprint"]}
