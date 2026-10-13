"""Operator-funded 128 -> 140 continuation; no historical accounting changes.

This policy is used only by a separately reviewed installed adapter after the
original lane, stage, owner, source, uncertainty and per-run guards pass.
It never reserves a call or grants execution authority.
"""
from pathlib import Path
import hashlib
import json

DOCUMENT = "docs/SCIENTIFIC_BATCH140_PRIVATE.json"
PIN = "bdb146318ef9dc84cf9979ebbe10c380c6745b1dabb66592b00592c45a73b13e"
ANSWER = "22096bb48c3adae5e3f9968049603628315de7774dba227e2726aaae9504dacf"
QUESTION = "7a7d5ab21c00e4b556bc71defca4bd139279da925f908092316bd44c43e873a1"
RUNS = {
    "colab-1ad5fafc220b3d65f576ce08": "returned_colab",
    "colab-arm-b9d64a3c09b799bc10b0eba7": "returned_colab",
    "colab-arm-47e6a72d9a2c821a4938fcae": "L",
    "meeting-775e80719952cfe222a61dcd": "meeting",
}
ALLOCATIONS = {"returned_colab": 4, "L": 4, "meeting": 4}

def require(ok, why):
    if not ok:
        raise ValueError("SCIENTIFIC_BATCH140_" + why)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def document(root):
    from orchestrator import private_records as pr
    root = Path(root)
    raw = pr.check(root / DOCUMENT).read_bytes()
    require(sha(raw) == PIN, "SCOPE_CHANGED")
    scope = json.loads(raw)
    require(scope["schema"] == "scientific-batch140/v1"
            and scope["baseline_count"] == 128 and scope["batch_limit"] == 140
            and scope["allocations"] == ALLOCATIONS and scope["runs"] == RUNS,
            "FIXED_LIMITS")
    for name, pin in scope["authority_files"].items():
        require(sha(pr.check(root / name).read_bytes()) == pin, "OPERATOR_AUTHORITY_CHANGED")
    require(scope["authority_files"]["docs/SCIENTIFIC_BATCH140_OPERATOR_APPROVAL.txt"] == ANSWER
            and scope["authority_files"]["docs/SCIENTIFIC_BATCH140_OPERATOR_QUESTION.txt"] == QUESTION,
            "EXACT_MONEY_AUTHORITY")
    record = json.loads(pr.check(root / "docs/SCIENTIFIC_BATCH140_OPERATOR_RECORD_PRIVATE.json").read_bytes())
    matches = [r for r in record["decisions"] if r["id"] == "scientific-batch-140-20261013"]
    require(len(matches) == 1 and sha(matches[0]["text"].encode()) == ANSWER
            and sha(matches[0]["question"].encode()) == QUESTION, "OPERATOR_RECORD")
    return scope

def allowance(accounts, run, scope, review_sha256):
    """Read inside the existing BEGIN IMMEDIATE reservation transaction.

    COMPLETE, FAILED, UNCERTAIN and RUNNING rows all consume their original
    slot. Purpose limits are additive only against the exact preserved baseline;
    unknown future calls refuse rather than disappearing from accounting.
    """
    require(run in RUNS and scope["runs"] == RUNS
            and scope["allocations"] == ALLOCATIONS and scope["baseline_count"] == 128
            and scope["batch_limit"] == 140, "FIXED_SCOPE")
    require(isinstance(review_sha256, str) and len(review_sha256) == 64
            and all(c in "0123456789abcdef" for c in review_sha256), "REVIEW_BINDING")
    frozen = scope["frozen_calls"]
    ids = {r["id"] for r in frozen}
    require(len(frozen) == len(ids) == 128, "BASELINE_COUNT")
    rows = [dict(r) for r in accounts.db.execute(
        "SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY id")]
    by_id = {r["id"]: r for r in rows}
    for old in frozen:
        require(old["id"] in by_id and sha(canonical(by_id[old["id"]])) == old["sha256"],
                "ORIGINAL_CALL_CHANGED")
    used = {purpose: 0 for purpose in ALLOCATIONS}
    for row in rows:
        if row["id"] in ids:
            continue
        require(row["change_id"] in RUNS, "UNCLASSIFIED_NEW_CALL")
        used[RUNS[row["change_id"]]] += 1
    require(all(used[k] <= ALLOCATIONS[k] for k in used), "ALLOCATION_ALREADY_EXCEEDED")
    require(len(rows) < 140, "BATCH_EXHAUSTED")
    purpose = RUNS[run]
    require(used[purpose] < ALLOCATIONS[purpose], "PURPOSE_EXHAUSTED")
    return {"limit": 140, "scoped_run_id": run, "scope_sha256": PIN,
            "review_sha256": review_sha256, "operator_answer_sha256": ANSWER,
            "operator_question_sha256": QUESTION, "purpose": purpose,
            "purpose_used": used[purpose], "purpose_limit": 4,
            "original_calls_preserved": 128, "actual_scientific_calls": len(rows)}
