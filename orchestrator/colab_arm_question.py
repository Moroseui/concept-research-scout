"""One distinct L question under unchanged shared limits.

Uses the normal analysis initializer and scientific stages. The exhausted Colab
run is evidence, never a source of reset calls or a copied allowance.
"""
from pathlib import Path
import hashlib
import json
import sqlite3

RUN = "colab-arm-47e6a72d9a2c821a4938fcae"
DOCUMENT = "docs/COLAB_L_QUESTION_PRIVATE.json"
DOCUMENT_SHA = "8550cdcf443a027d1dce73d6fa291bb3d7704806ba28bdb70a723c985ef76a3d"
CHANGE = "colab-l-reader-retry-20261013"
STAGES = frozenset(("run_spec_author", "run_spec_review"))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(",", ":"),allow_nan=False).encode()


def require(ok, why):
    if not ok:
        raise ValueError("COLAB_ARM_QUESTION_" + why)


def document():
    root = Path(__file__).resolve().parents[1]
    from orchestrator import private_records as pr
    raw = pr.check(root / DOCUMENT).read_bytes()
    require(sha(raw) == DOCUMENT_SHA, "SCOPE_CHANGED")
    scope = json.loads(raw)
    require(scope["run_id"] == RUN and scope["arm"] == "A1_L"
            and scope["call_limit"] == 20 and scope["batch_limit"] == 128
            and scope["allocation_limit"] == 16 and scope["allocation_baseline"] == 104
            and scope["admitted_stages"] == sorted(STAGES)
            and scope["execution_authorized"] is False, "SCOPE_LIMITS")
    for name, key in (
        ("COLAB_ARM_LEVEL_OPERATOR_20261012.txt", "arm_decision_sha256"),
        ("SCIENTIFIC_BATCH128_OPERATOR_APPROVAL.txt", "batch_answer_sha256"),
        ("SCIENTIFIC_BATCH128_OPERATOR_QUESTION.txt", "batch_question_sha256"),
    ):
        require(sha(pr.check(root / "docs" / name).read_bytes()) == scope[key],
                "OPERATOR_AUTHORITY_CHANGED")
    require(RUN == "colab-arm-" + sha(
        (scope["arm"] + ":" + scope["arm_decision_sha256"]).encode())[:24],
        "STABLE_QUESTION_ID")
    return scope


def selected(value):
    scope = value.get("colab_preparation", {})
    return isinstance(scope, dict) and "arm_question" in scope


def validate_scope(plan):
    scope = document()
    ref = plan["colab_preparation"]["arm_question"]
    require(ref == {"arm": scope["arm"], "scope_sha256": DOCUMENT_SHA},
            "QUESTION_BINDING")
    require(plan["item_number"] == 4 and plan["idea_ids"] ==
            ["sprint13b-execution", "colab-preparation-20261010"], "APPROVED_ITEM")
    return scope


def path(accounts, name):
    from tools.deploy_manual_lane import bound
    from orchestrator import private_records as pr
    return pr.check(bound(accounts.filesystem_root, name))


def preserved(accounts, scope):
    """Read exact original rows; no owner, attempt or status is rewritten."""
    old = scope["prior"]
    current = accounts.db.execute("SELECT * FROM autonomy_runs WHERE id=?",
                                  (old["config"]["run_id"],)).fetchone()
    require(current is not None and dict(current) == old["owner"], "OLD_OWNER_CHANGED")
    for row in old["global_calls"]:
        current = accounts.db.execute("SELECT * FROM autonomy_calls WHERE id=?",
                                      (row["id"],)).fetchone()
        require(current is not None and dict(current) == row, "OLD_GLOBAL_CALL_CHANGED")
    lane = path(accounts, old["lane"])
    require(sha(path(accounts, str(Path(old["lane"]) / "preparation-plan.json")).read_bytes()) ==
            old["plan_sha256"], "OLD_PLAN_CHANGED")
    require(json.loads(path(accounts, str(Path(old["lane"]) / "lane.json")).read_bytes()) ==
            old["config"], "OLD_CONFIG_CHANGED")
    database = path(accounts, str(Path(old["lane"]) / "jobs.sqlite"))
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        require([dict(r) for r in db.execute("SELECT * FROM manual_calls ORDER BY rowid")] ==
                old["local_calls"], "OLD_LOCAL_CALL_CHANGED")
        require(dict(db.execute("SELECT * FROM manual_state WHERE id=1").fetchone()) ==
                old["state_row"], "OLD_STATE_CHANGED")
    require(len(old["local_calls"]) == 24 and old["local_calls"][-1]["status"] == "COMPLETE"
            and json.loads(old["state_row"]["payload"])["phase"] == "BLOCKED"
            and json.loads(old["state_row"]["payload"])["reason"] == "OUTPUT_VALIDATION_REFUSED: ANALYSIS_REVISION_ROUND"
            and not any(r["status"] == "RUNNING" for r in old["local_calls"]),
            "OLD_RUN_NOT_TERMINAL")


def preflight(accounts, run, binding):
    """Register only this genuine question; retain the parked old ACTIVE owner."""
    scope = document()
    require(run == RUN and selected(binding), "DISTINCT_QUESTION_ONLY")
    require(not accounts.db.execute("SELECT 1 FROM autonomy_runs WHERE id=?", (run,)).fetchone(),
            "EXISTING_QUESTION_NO_NEW_ALLOWANCE")
    require(binding["colab_preparation"]["arm_question"] ==
            {"arm": scope["arm"], "scope_sha256": DOCUMENT_SHA}, "OWNER_QUESTION")
    require(binding["state"] == scope["new_lane"], "EXACT_NEW_STATE")
    require(not accounts.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),
            "LIVE_MODEL_CALL")
    preserved(accounts, scope)
    original = {r["id"]: r for r in scope["prior"]["active_owners"]}
    current = {r["id"]: dict(r) for r in accounts.db.execute(
        "SELECT * FROM autonomy_runs WHERE status!='COMPLETE'")}
    require(current == original and RUN not in current, "ACTIVE_OWNERS_CHANGED")


def configuration(accounts, run):
    if run != RUN:
        return None
    scope = document()
    row = accounts.db.execute("SELECT * FROM autonomy_runs WHERE id=?", (run,)).fetchone()
    require(row is not None and row["status"] == "ACTIVE", "ACTIVE_QUESTION_REQUIRED")
    owner = json.loads(row["binding"])
    require(owner["state"] == scope["new_lane"] and selected(owner), "OWNER_BINDING")
    config = json.loads(path(accounts, str(Path(owner["state"]) / "lane.json")).read_bytes())
    plan_raw = path(accounts, str(Path(owner["state"]) / "preparation-plan.json")).read_bytes()
    plan = json.loads(plan_raw)
    validate_scope(plan)
    require(config["run_id"] == run and config["owner_binding"] == owner
            and config["source"] == owner["source"]
            and config["plan_sha256"] == owner["plan_sha256"] == sha(plan_raw)
            and config["colab_preparation"] == plan["colab_preparation"] ==
            owner["colab_preparation"], "PLAN_CONFIG_OWNER_CHANGED")
    from orchestrator.autonomy_review import verify_result
    review_path = path(accounts, config["engine_review"]["path"])
    approval = verify_result(review_path.parent)
    require(approval["verdict"] == "APPROVE" and approval["change_id"] == CHANGE
            and approval["source_sha"] == config["source"]
            and approval["report_sha256"] == owner["review_sha256"] ==
            config["engine_review"]["sha256"], "INDEPENDENT_APPROVAL")
    require(json.loads(review_path.read_bytes())["findings"] == [], "UNRESOLVED_FINDINGS")
    preserved(accounts, scope)
    return scope


def validate(store, run):
    return configuration(store.batch, run)


def offset(store, run, stage):
    validate(store, run)
    return 0


def guard_admission(accounts, run, stage, source, receipt):
    scope = configuration(accounts, run)
    if scope is None:
        return None
    require(stage in STAGES and receipt.get("stage") == stage, "PREPARATION_STAGE_ONLY")
    owner = json.loads(accounts.db.execute(
        "SELECT binding FROM autonomy_runs WHERE id=?", (run,)).fetchone()[0])
    require(source == owner["source"], "ADMISSION_SOURCE")
    return scope


def terminal_ids(accounts, scope):
    from orchestrator import colab_simple_full as prior
    return prior.terminal_ids(accounts, {"uncertain_rows": sorted(scope["prior"]["uncertain"], key=lambda row: row["id"])})


def batch_allowance(accounts, scope):
    """Count original rows and all Colab-scoped owners against the 16-call allocation."""
    baseline = {r["id"] for r in scope["prior"]["global_calls"][:104]}
    require(len(baseline) == 104, "ORIGINAL_BASELINE")
    owners = {r["id"]: json.loads(r["binding"]) for r in accounts.db.execute(
        "SELECT id,binding FROM autonomy_runs")}
    rows = accounts.db.execute("SELECT id,change_id FROM autonomy_calls WHERE kind='scientific'").fetchall()
    used = sum(r["id"] not in baseline and
               "colab_preparation" in owners.get(r["change_id"], {}) for r in rows)
    require(used < scope["allocation_limit"], "COLAB_ALLOCATION_EXHAUSTED")
    return {"limit": 128, "scope_sha256": DOCUMENT_SHA, "scoped_run_id": RUN,
            "operator_answer_sha256": scope["batch_answer_sha256"],
            "operator_question_sha256": scope["batch_question_sha256"],
            "colab_allocation_used": used, "colab_allocation_limit": 16}


def refuse_legacy_completion(accounts, run):
    if run == RUN:
        raise ValueError("COLAB_ARM_QUESTION_NO_AUTOMATED_COMPLETION")


def preparation_hold(driver, value, collect_folder, identity_refusal):
    if driver.config.get("run_id") != RUN:
        return None
    validate(driver.store, RUN)
    require(collect_folder is None and identity_refusal is None, "NO_DATA_EXECUTION")
    require(value["phase"] in STAGES | {"MODEL_RUNNING", "BLOCKED", "COMMIT_SPEC"},
            "PREPARATION_ONLY")
    if value["phase"] == "COMMIT_SPEC":
        return {**driver.status(), "next_action": "HELD: real trainer integration and exact notebook delivery qualification required",
                "execution_authorized": False}
    return None


def instructions(stage, plan):
    scope = validate_scope(plan)
    require(stage in STAGES, "PREPARATION_STAGE_ONLY")
    from orchestrator.analysis_driver import bound_file
    tasks = [row for row in plan["artifacts"] if row["id"] == "l-arm-author-task"
             and row["type"] == "question"]
    require(len(tasks) == 1, "TASK_REQUIRED")
    task = bound_file(Path(plan["context"]), {k: tasks[0][k] for k in ("path", "sha256")})
    return (task.decode() + "\nRequired specification binding lines:\nrun_id: " +
            RUN + "\nanalysis_registry_sha256: " + plan["private_intake"]["sha256"] + "\n")


def execution_reading_artifact(driver, value, pending, notebook, tests, folder):
    """Give the reviewer exact executable text as well as the unchanged notebook."""
    pin = tests.get("binding", {}).get("files", {}).get("execution.py")
    if pin is None:
        return  # Compile failure is still reviewed as failure; no module invented.
    from orchestrator.notebook_execution import extract
    from orchestrator import private_records as pr
    raw = extract(notebook, preprocessing=True)
    require(sha(raw) == pin and
            sha(pr.check(Path(folder) / "synthetic/package/execution.py").read_bytes()) == pin,
            "AUTHORED_MODULE_BINDING")
    driver.artifact(value, "notebook_source", "exact-authored-execution-" +
                    str(pending["round"]) + ".py", raw, pending["round"])
