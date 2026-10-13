"""Read-only continuation of the original sibling history check for L.

This is a candidate patch, not an admission grant. Installation must authenticate
the separately approved sibling continuation and recovery, then supply their
read-only qualifier. Original rows, ownership and every charge remain exact.
"""
from pathlib import Path
import hashlib
import json
import sqlite3

RUN = "colab-arm-47e6a72d9a2c821a4938fcae"
SIBLING = "colab-1ad5fafc220b3d65f576ce08"
AUTHOR = "b1dad7a10b0830b2cd2b569032792dcae04e4b16224f410a0df2a2c0e6a3c686"
REVIEW = "bf26d2ebec5c7b13e9f763c2b1885e04b966e2e2b6d0ba17bc171d407f7a39f4"

def require(ok, why):
    if not ok:
        raise ValueError("L_FUNDED_HISTORY_" + why)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def preserved(accounts, scope, checkpoint, qualify):
    """Equivalent history check: exact old prefix plus exact approved additions.

    The callback is mandatory and must be supplied only by the reviewed runtime
    after verifying installed approvals and source hashes. No status is rewritten.
    """
    from orchestrator.colab_arm_question import path
    old = scope["prior"]
    require(old["config"]["run_id"] == checkpoint["run"] == SIBLING, "SIBLING")
    require((old["config"], old["owner"], old["lane"]) ==
            (checkpoint["config"], checkpoint["owner"], checkpoint["lane"]),
            "ORIGINAL_IDENTITY")
    require(len(old["local_calls"]) == 24 and
            checkpoint["local_rows"][:24] == old["local_calls"], "ORIGINAL_PREFIX")
    original_state = json.loads(old["state_row"]["payload"])
    require(original_state["phase"] == "BLOCKED" and original_state["reason"] ==
            "OUTPUT_VALIDATION_REFUSED: ANALYSIS_REVISION_ROUND" and
            all(r["status"] != "RUNNING" for r in old["local_calls"]),
            "ORIGINAL_TERMINAL_STATE")
    local = checkpoint["local_rows"]
    require(len(local) == 26 and
            [(r["id"], r["stage"], r["attempt"], r["status"]) for r in local[24:]] ==
            [(AUTHOR, "run_spec_author", 13, "UNCERTAIN"),
             (REVIEW, "run_spec_review", 12, "COMPLETE")], "EXACT_ADDITIONS")
    state = json.loads(checkpoint["state_row"]["payload"])
    require(state["phase"] == "BLOCKED" and state["reason"] ==
            "BOUNDED_PROVENANCE_REVIEW_REVISE" and not state.get("pending"),
            "CURRENT_TERMINAL_STATE")
    owner = accounts.db.execute("SELECT * FROM autonomy_runs WHERE id=?", (SIBLING,)).fetchone()
    require(owner is not None and dict(owner) == old["owner"], "OWNER_CHANGED")
    for row in old["global_calls"]:
        current = accounts.db.execute("SELECT * FROM autonomy_calls WHERE id=?", (row["id"],)).fetchone()
        require(current is not None and dict(current) == row, "ORIGINAL_GLOBAL_CHANGED")
    rows = [dict(r) for r in accounts.db.execute(
        "SELECT * FROM autonomy_calls WHERE change_id=? ORDER BY rowid", (SIBLING,))]
    require(rows == checkpoint["global_rows"] and len(rows) == 26, "GLOBAL_HISTORY")
    require([(r["id"], r["status"]) for r in rows[-2:]] ==
            [(AUTHOR, "UNCERTAIN"), (REVIEW, "COMPLETE")], "GLOBAL_ADDITIONS")
    lane = Path(old["lane"])
    require(digest(path(accounts, str(lane / "preparation-plan.json")).read_bytes()) ==
            old["plan_sha256"], "PLAN_CHANGED")
    raw_config = path(accounts, str(lane / "lane.json")).read_bytes()
    require(json.loads(raw_config) == old["config"] and
            digest(raw_config) == checkpoint["config_sha256"], "CONFIG_CHANGED")
    database = path(accounts, str(lane / "jobs.sqlite"))
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        require([dict(r) for r in db.execute("SELECT * FROM manual_calls ORDER BY rowid")] ==
                local, "LOCAL_HISTORY")
        require(dict(db.execute("SELECT * FROM manual_state WHERE id=1").fetchone()) ==
                checkpoint["state_row"], "STATE_CHANGED")
        require(dict(db.execute("SELECT * FROM manual_account WHERE id=1").fetchone()) ==
                checkpoint["account_row"], "ACCOUNT_CHANGED")
        proof = qualify(accounts, db)
        require(proof["call"] == AUTHOR and proof["native_exit"] == "ok" and
                proof["original_status"] == "UNCERTAIN" and
                proof["new_calls"] == 0 and proof["scientific_acceptance"] is False,
                "INSTALLED_QUALIFICATION")
        db.rollback()
    return proof
