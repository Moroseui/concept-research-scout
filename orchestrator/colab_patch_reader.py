"""Exact pre-admission review9 reader recovery; original state and calls preserved."""
from pathlib import Path
import hashlib
import json

DOCUMENT = "docs/COLAB_PATCH_READING_FAILURE_PRIVATE.json"
DOCUMENT_SHA = "93afe3beae1803374d273a66d2d6d9faf7e7e91bce3ce2823a62fc2c66401d3d"
EVENT = "colab-patch-reading-recovery-20261012"
RUN = "colab-1ad5fafc220b3d65f576ce08"
REVIEW_ID = "125d26e2f74b735214b344e2ac868b3fdea629b54d90e1f9094ce3a5637c3a8c"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def require(ok, why):
    if not ok:
        raise ValueError("COLAB_PATCH_READING_" + why)


def document(root):
    from orchestrator import private_records as pr
    raw = pr.check(Path(root) / DOCUMENT).read_bytes()
    require(sha(raw) == DOCUMENT_SHA, "DOCUMENT_CHANGED")
    value = json.loads(raw)
    require(value["run_id"] == RUN and value["review_id"] == REVIEW_ID
            and value["global_row"] is None and value["workspace_files"] is None
            and len(value["local_calls"]) == 19, "PREMODEL_SCOPE")
    restored(json.loads(value["state_row"]["payload"]), value)
    return value


def restored(current, frozen):
    original = frozen["original_state"]
    expected = {**original, "phase": "BLOCKED",
                "reason": "ContextError: MANUAL_JSON_PAGE_TOO_LARGE",
                "blocked_stage": "run_spec_review"}
    require(current == expected and original["phase"] == "run_spec_review"
            and original.get("pending") is None
            and original["rounds"]["run_spec_author"] == 10
            and original["rounds"]["run_spec_review"] == 8, "EXACT_PREMODEL_STATE")
    return dict(original)


def check(driver, frozen, initial=False):
    from orchestrator import private_records as pr
    require(driver.config["run_id"] == RUN, "RUN")
    rows = [dict(row) for row in driver.store.db.execute("SELECT * FROM manual_calls ORDER BY rowid")]
    original = {row["id"]: row for row in frozen["local_calls"]}
    require(all(next((row for row in rows if row["id"] == key), None) == value
                for key, value in original.items()), "ORIGINAL_LOCAL_CALL")
    extra = [row for row in rows if row["id"] not in original]
    require(len(extra) <= 1 and all(row["id"] == REVIEW_ID and row["stage"] == "run_spec_review"
                                   and row["attempt"] == 9 for row in extra), "ONE_REVIEW_ONLY")
    for row in frozen["global_calls"]:
        current = driver.store.batch.db.execute("SELECT * FROM autonomy_calls WHERE id=?", (row["id"],)).fetchone()
        require(current is not None and dict(current) == row, "ORIGINAL_GLOBAL_CALL")
    for name, pin in frozen["artifact_files"].items():
        require(sha(pr.check(Path(name)).read_bytes()) == pin, "AUTHOR_EVIDENCE_CHANGED")
    if initial:
        require(not extra and driver.store.batch.db.execute(
            "SELECT 1 FROM autonomy_calls WHERE id=?", (REVIEW_ID,)).fetchone() is None, "REVIEW_ALREADY_RESERVED")
        row = dict(driver.store.db.execute("SELECT * FROM manual_state WHERE id=1").fetchone())
        require(row == frozen["state_row"], "BLOCKED_STATE_CHANGED")
        restored(driver.current(), frozen)


def recover(driver, frozen, approval):
    from orchestrator import private_records as pr
    check(driver, frozen, initial=True)
    require(isinstance(approval, str) and len(approval) == 64, "APPROVAL")
    dest = driver.state / EVENT
    require(not dest.exists() and not dest.is_symlink(), "ALREADY_ATTEMPTED")
    value = restored(driver.current(), frozen)
    record = {"proof_sha256": DOCUMENT_SHA, "review_sha256": approval,
              "review_id": REVIEW_ID, "model_calls": 0, "new_allowance": 0,
              "preserved_calls": 19}
    pr.mkdir(dest)
    pr.write_bytes(dest / "original-state.json", frozen["state_row"]["payload"].encode())
    db = driver.store.db
    db.execute("BEGIN IMMEDIATE")
    try:
        check(driver, frozen, initial=True)
        db.execute("INSERT INTO events VALUES(?,?,?)", (EVENT, RUN, encoded(record).decode()))
        db.execute("UPDATE manual_state SET payload=? WHERE id=1", (json.dumps(value, sort_keys=True),))
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise
    require(driver.current() == value, "STATE_READBACK")
    pr.write_bytes(dest / "COMPLETE.json", encoded(record))
    return {"status": "READY_SAME_REVIEW9", "new_calls": 0, "new_allowance": 0, "preserved_calls": 19}
