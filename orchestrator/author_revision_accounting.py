"""Separate verified scientific revisions from failed author attempts.

Prospective receipt/event metadata only: no old rows, charges or caps change.
A COMPLETE provider call alone never proves that its output passed validation.
"""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

AUTHORITY = "c9f088863d00ca160e7f104a2571291f36be2af1907e296783eb172785fa1d63"
DOCUMENT = "docs/AUTHOR_REVISE_ACCOUNTING_OPERATOR_DECISION_20261008.txt"
FIELD = "scientific_revision_response"
AUTHORS = {"run_spec_author", "result_interpretation_author"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def authority():
    path = Path(__file__).resolve().parents[1]/DOCUMENT
    if path.is_symlink() or sha(path.read_bytes()) != AUTHORITY:
        raise ValueError("AUTHOR_REVISION_AUTHORITY_CHANGED")


def context(store, run):
    from orchestrator.analysis_revisions import enabled
    if not enabled(store, run):
        return None
    authority()
    state = Path(store.path).parent
    config = json.loads((state/"lane.json").read_bytes())
    return SimpleNamespace(store=store, state=state, config=config)


def review_binding(driver, stage, number, author_number):
    from orchestrator.experiment_approval import verified_review_delivery
    from orchestrator.analysis_revisions import review_transition
    review_stage = stage.replace("_author", "_review")
    work = Path(driver.config.get("workspace_root",
        driver.state.parent/(driver.state.name+"-scientific-workspaces")))/(review_stage+"-"+str(number))
    run = driver.config["run_id"]
    pending = {"stage": review_stage, "round": number, "workspace": str(work),
               "id": sha((run+":"+review_stage+":"+str(number)).encode())}
    _, _, raw, receipt, row, submission = verified_review_delivery(driver, pending, review_stage)
    review = json.loads(raw)
    if review_transition(review, review_stage, number) != (stage, "REVISION_REQUIRED"):
        raise ValueError("AUTHOR_GENUINE_ACTIONABLE_REVISE_REQUIRED")
    return {"schema": "scientific-revision-response/v1", "authority_sha256": AUTHORITY,
            "run_id": run, "stage": stage, "author_attempt": author_number,
            "author_call_id": sha((run+":"+stage+":"+str(author_number)).encode()),
            "review_call_id": pending["id"], "review_round": number,
            "review_sha256": sha(raw), "review_receipt_sha256": sha(row["receipt"].encode()),
            "submission_sha256": sha(submission)}


def _accepted(store, row):
    event = store.db.execute("SELECT payload FROM events WHERE id=?",
                            ("author-accepted:"+row["id"],)).fetchone()
    if event is None:
        return False  # Historical COMPLETE-but-format-rejected calls stay counted.
    receipt = json.loads(row["receipt"])
    expected = {"schema": "validated-author-output/v1", "call_id": row["id"],
                "stage": row["stage"], "attempt": row["attempt"],
                "output_sha256": receipt["output_sha256"]}
    if row["status"] != "COMPLETE" or json.loads(event[0]) != expected:
        raise ValueError("AUTHOR_ACCEPTANCE_RECORD_CHANGED")
    return True


def inspect(store, run, stage):
    """Recompute at both the driver guard and durable reservation boundary."""
    if stage not in AUTHORS:
        return None
    driver = context(store, run)
    if driver is None:
        return None
    rows = [dict(r) for r in store.db.execute("SELECT * FROM manual_calls ORDER BY rowid")]
    authors = [r for r in rows if r["stage"] == stage]
    number = len(authors)+1
    used = set()
    failures = 0
    for row in authors:
        binding = json.loads(row["receipt"]).get(FIELD)
        if binding is not None:
            expected = review_binding(driver, stage, binding["review_round"], row["attempt"])
            if binding != expected or row["id"] != binding["author_call_id"] or binding["review_call_id"] in used:
                raise ValueError("AUTHOR_REVISION_RECEIPT_CHANGED")
            used.add(binding["review_call_id"])
        elif not _accepted(store, row):
            failures += 1
    state_row = store.db.execute("SELECT payload FROM manual_state WHERE id=1").fetchone()
    state = json.loads(state_row[0]) if state_row else {}
    if state.get("phase") == stage and state.get("reason") == "REVISION_REQUIRED":
        review_stage = stage.replace("_author", "_review")
        reviews = [r for r in rows if r["stage"] == review_stage]
        if not reviews or rows[-1]["id"] != reviews[-1]["id"] or len(used) >= 3:
            raise ValueError("AUTHOR_REVISION_NEW_REVIEW_REQUIRED")
        latest = reviews[-1]
        binding = review_binding(driver, stage, latest["attempt"], number)
        expected_path = Path(driver.config.get("workspace_root",
            driver.state.parent/(driver.state.name+"-scientific-workspaces")))/(review_stage+"-"+str(latest["attempt"]))/"review.json"
        if (state.get("review") != str(expected_path) or latest["id"] != binding["review_call_id"]
                or binding["review_call_id"] in used):
            raise ValueError("AUTHOR_REVISION_STATE_BINDING")
        return {"limit": number, "binding": binding, "failed_attempts": failures}
    # Four failed/unsubmitted/format-rejected attempts, not four total authors.
    # An admitted revision consumes its revision slot even if it later fails.
    return {"limit": number if failures < 4 else number-1, "binding": None,
            "failed_attempts": failures}


def accepted(driver, pending):
    """Called only after the host's complete output validators succeed."""
    stage = pending["stage"]
    if stage not in AUTHORS or context(driver.store, driver.config["run_id"]) is None:
        return
    row = driver.store.db.execute("SELECT * FROM manual_calls WHERE id=?", (pending["id"],)).fetchone()
    if row is None or row["status"] != "COMPLETE" or row["stage"] != stage or row["attempt"] != pending["round"]:
        raise ValueError("AUTHOR_ACCEPTANCE_CALL_BINDING")
    receipt = json.loads(row["receipt"])
    payload = json.dumps({"schema": "validated-author-output/v1", "call_id": row["id"],
        "stage": stage, "attempt": row["attempt"], "output_sha256": receipt["output_sha256"]}, sort_keys=True)
    ident = "author-accepted:"+row["id"]
    old = driver.store.db.execute("SELECT payload FROM events WHERE id=?", (ident,)).fetchone()
    if old:
        if old[0] != payload:
            raise ValueError("AUTHOR_ACCEPTANCE_RECORD_CHANGED")
    else:
        driver.store.db.execute("INSERT INTO events VALUES(?,?,?)", (ident, driver.config["run_id"], payload))
