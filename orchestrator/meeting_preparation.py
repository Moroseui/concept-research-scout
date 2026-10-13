"""One private meeting preparation question; no patient executor or new budget.

Reuses scientific transport, structured review, code scanning and the existing
isolated synthetic test runner. Every historical call and acceptance is retained.
"""
from pathlib import Path
import hashlib
import json
import os
import sqlite3

from orchestrator import private_records as pr
from orchestrator.manual_driver import Driver, git, stamp, write_once
from orchestrator.manual_executor import ManualExecutor, atomic, read
from orchestrator.autonomy_accounting import BatchAccounts

DOCUMENT = "docs/MEETING_PREPARATION_PRIVATE.json"
DOCUMENT_SHA = "aeba65df7e2d514ad4515e238c800b506c3bc5d11bb6b43a6cc1cddd77f3eca6"
RUN = "meeting-775e80719952cfe222a61dcd"
CHANGE = "meeting-preparation-20261013"
FIELD = "meeting_preparation"
BRANCH = "astra/manual-meeting-preparation-20261013"
STAGES = frozenset(("run_spec_author", "run_spec_review"))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def require(ok, why):
    if not ok:
        raise ValueError("MEETING_PREPARATION_" + why)


def document():
    root = Path(__file__).resolve().parents[1]
    raw = pr.check(root / DOCUMENT).read_bytes()
    require(sha(raw) == DOCUMENT_SHA, "SCOPE_CHANGED")
    scope = json.loads(raw)
    require(scope["schema"] == "meeting-preparation/v1" and scope["run_id"] == RUN
            and scope["call_limit"] == 20 and scope["allocation_limit"] == 4
            and scope["batch_limit"] == 128 and scope["baseline_count"] == 124
            and scope["execution_authorized"] is False
            and scope["offsets"] == {stage: 0 for stage in STAGES}, "FIXED_LIMITS")
    for name, pin in scope["authority_files"].items():
        require(sha(pr.check(root / name).read_bytes()) == pin, "OPERATOR_AUTHORITY_CHANGED")
    require(RUN == "meeting-" + sha((scope["proposal_sha256"] + ":" +
            scope["authority_files"]["docs/OPERATOR_DIRECTION_20261010.txt"]).encode())[:24],
            "STABLE_QUESTION")
    return scope


def validate_scope(plan):
    scope = document()
    require(sha(json.dumps(plan, sort_keys=True, indent=2).encode()) == scope["plan_sha256"]
            and plan["schema"] == "meeting-preparation-plan/v1" and plan["run_id"] == RUN
            and plan["context"] == scope["native"]["work"] + "/protected-context"
            and plan["execution_authorized"] is False, "EXACT_PREPARATION_PLAN")
    return scope


def selected(config):
    return FIELD in config


def path(accounts, name):
    from tools.deploy_manual_lane import bound
    return pr.check(bound(accounts.filesystem_root, name))


def preserved(accounts, scope):
    rows = scope["frozen_calls"]
    require(len(rows) == 124 and len({r["id"] for r in rows}) == 124, "BASELINE_COUNT")
    for row in rows:
        actual = accounts.db.execute("SELECT * FROM autonomy_calls WHERE id=?", (row["id"],)).fetchone()
        require(actual is not None and sha(encoded(dict(actual))) == row["sha256"],
                "ORIGINAL_CALL_CHANGED")
    for table, key in (("autonomy_runs", "parent_owner"), ("events", "parent_event")):
        old = scope[key]
        actual = accounts.db.execute("SELECT * FROM " + table + " WHERE id=?", (old["id"],)).fetchone()
        require(actual is not None and dict(actual) == old, "ACCEPTED_PARENT_CHANGED")



    expected = sorted(scope["active_owners"], key=lambda r: r["id"])
    actual = [dict(r) for r in accounts.db.execute(
        "SELECT * FROM autonomy_runs WHERE status!='COMPLETE' AND id!=? ORDER BY id", (RUN,))]
    require(actual == expected, "OTHER_OWNER_CHANGED")


def validate_config(config, run):
    scope = document()
    require(run == RUN and config.get("run_id") == RUN
            and config.get(FIELD) == {"scope_sha256": DOCUMENT_SHA}
            and config.get("backend") == "meeting-preparation"
            and config.get("item_number") == 6
            and config.get("author_timeout_seconds") == 1800
            and config.get("review_contract") == "bound-review/v1",
            "CONFIGURATION_SCOPE")
    return scope


def approval(config, accounts):
    from orchestrator.autonomy_review import verify_result
    folder = path(accounts, config["engine_review"]["path"]).parent
    result = verify_result(folder)
    manifest = json.loads(pr.check(folder / "packet-manifest.json").read_bytes())
    report = json.loads(pr.check(folder / "report.md").read_bytes())
    require(result["verdict"] == "APPROVE" and result["change_id"] == CHANGE
            and not report["findings"] and result["source_sha"] == config["source"]
            and result["report_sha256"] == config["engine_review"]["sha256"],
            "INDEPENDENT_APPROVAL")
    required = {DOCUMENT, "orchestrator/meeting_preparation.py",
                "tools/meeting_preparation_runtime.py", "orchestrator/manual_context.py",
                "orchestrator/autonomy_accounting.py", "orchestrator/manual_driver.py",
                "orchestrator/manual_stage.py", "orchestrator/scientific_program.py",
                "tests/test_meeting_preparation.py", "orchestrator/meeting_author_feedback.py"}
    require(required <= set(manifest["source_files"]), "WHOLE_COMPONENT")
    root = Path(__file__).resolve().parents[1]
    for name, pin in manifest["source_files"].items():
        require(sha(pr.check(root / name).read_bytes()) == pin, "REVIEWED_SOURCE_CHANGED")
    return result


def configuration(accounts, run):
    if run != RUN:
        return None
    scope = document()
    row = accounts.db.execute("SELECT * FROM autonomy_runs WHERE id=?", (run,)).fetchone()
    require(row is not None and row["status"] == "ACTIVE", "ACTIVE_OWNER")
    owner = json.loads(row["binding"])
    require(owner["state"] == scope["new_lane"] and owner.get(FIELD) ==
            {"scope_sha256": DOCUMENT_SHA}, "OWNER_SCOPE")
    config = json.loads(path(accounts, str(Path(scope["new_lane"]) / "lane.json")).read_bytes())
    validate_config(config, run)
    raw = path(accounts, str(Path(scope["new_lane"]) / "preparation-plan.json")).read_bytes()
    require(sha(raw) == scope["plan_sha256"] == config["plan_sha256"] == owner["plan_sha256"]
            and config["owner_binding"] == owner and config["source"] == owner["source"]
            and config["engine_review"]["sha256"] == owner["review_sha256"],
            "OWNER_PLAN_BINDING")
    require(config["root"] == str(Path(__file__).resolve().parents[1])
            and config["context"] == scope["native"]["work"] + "/protected-context"
            and config["workspace_root"] == scope["native"]["work"] + "/lane-scientific-workspaces"
            and config["synthetic_environment"] == scope["synthetic_environment"]
            and config["branch"] == BRANCH, "EXACT_RUNTIME_LAYOUT")
    validate_scope(json.loads(raw))
    approval(config, accounts)
    preserved(accounts, scope)
    return scope


def validate(store, run):
    return configuration(store.batch, run)


def offset(store, run, stage):
    validate(store, run)
    return 0


def terminal_ids(accounts, scope):
    from orchestrator.colab_simple_full import terminal_ids as existing
    return existing(accounts, {"uncertain_rows": scope["uncertain_rows"]})


def batch_allowance(accounts, scope):
    require(scope == document(), "EXACT_ALLOCATION_SCOPE")
    preserved(accounts, scope)
    used = accounts.db.execute(
        "SELECT count(*) FROM autonomy_calls WHERE kind='scientific' AND change_id=?", (RUN,)).fetchone()[0]
    require(used < 4, "MEETING_ALLOCATION_EXHAUSTED")
    require(accounts.db.execute(
        "SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0] < 128,
        "GLOBAL_BATCH_EXHAUSTED")
    return {"limit": 128, "scoped_run_id": RUN, "scope_sha256": DOCUMENT_SHA,
            "meeting_allocation_used": used, "meeting_allocation_limit": 4,
            "operator_answer_sha256": scope["authority_files"]["docs/SCIENTIFIC_BATCH128_OPERATOR_APPROVAL.txt"],
            "operator_question_sha256": scope["authority_files"]["docs/SCIENTIFIC_BATCH128_OPERATOR_QUESTION.txt"]}


def guard_admission(accounts, run, stage, source, receipt):
    scope = configuration(accounts, run)
    if scope is None:
        return None
    require(stage in STAGES and receipt.get("stage") == stage, "PREPARATION_STAGE_ONLY")
    owner = json.loads(accounts.db.execute("SELECT binding FROM autonomy_runs WHERE id=?", (run,)).fetchone()[0])
    require(source == owner["source"], "ADMISSION_SOURCE")
    workspace = Path(receipt["workspace"])
    expected = Path(scope["new_lane"]).with_name("lane-scientific-workspaces")
    require(workspace.parent == expected and workspace.name.startswith(stage + "-"),
            "EXACT_WORKSPACE")
    suffix = workspace.name[len(stage) + 1:]
    count = accounts.db.execute("SELECT count(*) FROM autonomy_calls WHERE change_id=? AND "
                               "json_extract(binding,'$.stage')=?", (RUN, stage)).fetchone()[0]
    require(suffix.isdecimal() and int(suffix) == count + 1, "EXACT_NEXT_ATTEMPT")
    path(accounts, str(workspace))
    return scope


def refuse_legacy_completion(accounts, run):
    if run == RUN:
        raise ValueError("MEETING_PREPARATION_NO_DATA_COMPLETION")


def preparation_hold(driver, value, collect_folder, identity_refusal):
    if driver.config.get("run_id") != RUN:
        return None
    validate(driver.store, RUN)
    require(collect_folder is None and identity_refusal is None, "NO_EXECUTION_OR_COLLECTION")
    require(value["phase"] in STAGES | {"MODEL_RUNNING", "BLOCKED", "COMMIT_SPEC"}, "PREPARATION_ONLY")
    if value["phase"] == "COMMIT_SPEC":
        return {**driver.status(), "next_action": "HELD: reviewed preparation only; real-case execution requires qualified inputs and separate admission",
                "execution_authorized": False}
    return None


def register(accounts, owner, scope):
    db = accounts.db
    db.execute("BEGIN IMMEDIATE")
    try:
        require(not (accounts.folder / "HALT").exists(), "BATCH_HALT")
        preserved(accounts, scope)
        require(not db.execute("SELECT 1 FROM autonomy_runs WHERE id=?", (RUN,)).fetchone(),
                "EXISTING_OWNER_NO_RESET")
        require(not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),
                "LIVE_MODEL_CALL")
        terminal_ids(accounts, scope)
        batch_allowance(accounts, scope)
        require(owner["state"] == scope["new_lane"] and owner[FIELD] == {"scope_sha256": DOCUMENT_SHA},
                "NEW_OWNER_SCOPE")
        db.execute("INSERT INTO autonomy_runs(id,binding,status) VALUES(?,?,?)", (RUN, json.dumps(owner, sort_keys=True), "ACTIVE"))
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise


def initialize(root, state, engine_review, plan_path):
    from orchestrator import manual_stage, context_budget
    from orchestrator.analysis_driver import release_identities
    from orchestrator.analysis_revisions import POLICY
    root, state, engine_review, plan_path = map(Path, (root, state, engine_review, plan_path))
    scope = document()
    require(str(state) == scope["new_lane"] and not state.exists() and not state.is_symlink(),
            "EXCLUSIVE_NEW_LANE")
    require(root.resolve() == Path(__file__).resolve().parents[1] and
            git(root, "branch", "--show-current") == BRANCH and not git(root, "status", "--porcelain"),
            "CLEAN_REVIEWED_SOURCE")
    git(root, "var", "GIT_AUTHOR_IDENT"); git(root, "var", "GIT_COMMITTER_IDENT")
    source = git(root, "rev-parse", "HEAD")
    raw = pr.check(plan_path).read_bytes()
    require(sha(raw) == scope["plan_sha256"], "PLAN_CHANGED")
    plan = json.loads(raw)
    context = Path(plan["context"])
    require(context == state.parent / "protected-context" and plan["run_id"] == RUN
            and plan["execution_authorized"] is False, "PLAN_SCOPE")
    require({str(p.relative_to(context)): sha(p.read_bytes()) for p in context.rglob("*") if p.is_file()}
            == plan["context_files"] and not any(p.is_symlink() for p in context.rglob("*")),
            "CONTEXT_INVENTORY")
    context_budget.load(context)
    from orchestrator.scientific_intake import cohort
    cohort(pr.check(context / "development99.json").read_bytes())
    clients = manual_stage.preflight()
    profile, engine = release_identities(root)
    owner = {"state": str(state), "source": source, "run_id": RUN,
             "plan_sha256": sha(raw), "review_sha256": sha(pr.check(engine_review).read_bytes()),
             FIELD: {"scope_sha256": DOCUMENT_SHA}}
    policy = {"status": "RATIFIED", "operator_approval": scope["authority_files"]["docs/OPERATOR_DIRECTION_20261010.txt"],
              "state_write_permission": "OPERATOR_AUTHORIZED", "n": 4, "window": "UTC_CALENDAR_DAY",
              "state_ref": "refs/heads/automation/dispatch-state", "manual_semantics": "OPERATOR_STEP_D_MAX_EIGHT"}
    config = {"backend": "meeting-preparation", "item_number": 6, "run_id": RUN, "source": source,
              "branch": BRANCH, "root": str(root), "context": str(context),
              "batch_ledger": scope["batch_ledger"], "owner_binding": owner,
              "engine_review": {"path": str(engine_review), "sha256": owner["review_sha256"]},
              "authority_path": "docs/OPERATOR_DIRECTION_20261010.txt",
              "authority_sha256": policy["operator_approval"], "profile_files": profile, "engine_files": engine,
              "workspace_root": str(state.parent / "lane-scientific-workspaces"), "clients": clients,
              "policy": policy, "started_utc": stamp(), "plan_sha256": sha(raw), "idea_ids": ["meeting-case-review"],
              "review_contract": "bound-review/v1", "revision_policy": POLICY, "author_timeout_seconds": 1800,
              "synthetic_environment": scope["synthetic_environment"], FIELD: {"scope_sha256": DOCUMENT_SHA}}
    accounts = BatchAccounts(scope["batch_ledger"])
    try:
        result = approval(config, accounts)
        manifest = json.loads(pr.check(engine_review.parent / "packet-manifest.json").read_bytes())
        require(manifest["files"].get("evidence/meeting-preparation-plan.json") == sha(raw),
                "REVIEWED_PLAN_REQUIRED")
        require(result["runtime_sha256"] == sha(pr.check(os.environ["RESEARCH_MANUAL_RUNTIME_CONFIG"]).read_bytes()),
                "REVIEWED_RUNTIME_REQUIRED")
        require(not (accounts.folder / "HALT").exists(), "BATCH_HALT")
        pr.mkdir(state)
        pr.write_bytes(state / "preparation-plan.json", raw)
        pr.write_bytes(state / "owner.json", encoded(owner))
        # Register before allowance. Partial failures are retained, never reset.
        register(accounts, owner, scope)
        atomic(state / "lane.json", config)
        store = ManualExecutor(state / "jobs.sqlite", batch=accounts)
        try:
            store.initialize_allowance(policy)
            store.db.execute("INSERT INTO manual_state VALUES(1,?)",
                (json.dumps({"phase": "run_spec_author", "rounds": {}, "artifacts": plan["artifacts"],
                             "interventions": []}),))
        finally:
            store.db.close()
    finally:
        accounts.db.close()
    return {"status": "READY", "run_id": RUN, "calls_used": 0, "meeting_allocation": 4,
            "execution_authorized": False}


class MeetingDriver(Driver):
    def __init__(self, state, runner=None):
        from orchestrator import manual_stage
        self.state = Path(state); self.config = read(self.state / "lane.json")
        validate_config(self.config, RUN)
        self.root = Path(self.config["root"]); self.context = Path(self.config["context"])
        self.store = ManualExecutor(self.state / "jobs.sqlite",
            batch=BatchAccounts(self.config["batch_ledger"]))
        self.runner = runner or manual_stage.invoke

    def guard(self):
        super().guard()
        scope = validate(self.store, RUN)
        raw = pr.check(self.state / "preparation-plan.json").read_bytes()
        require(sha(raw) == scope["plan_sha256"] == self.config["plan_sha256"], "PLAN_CHANGED")
        require(json.loads(pr.check(self.state / "owner.json").read_bytes()) == self.config["owner_binding"],
                "OWNER_FILE_CHANGED")
        from orchestrator.analysis_driver import bound_file
        for artifact in json.loads(raw)["artifacts"]:
            bound_file(self.context, {k: artifact[k] for k in ("path", "sha256")})
        from orchestrator.scientific_intake import cohort
        cohort(pr.check(self.context / "development99.json").read_bytes())

    def status(self):
        return {**super().status(), "execution_backend": "meeting preparation and synthetic tests only; real cases held",
                "meeting_allocation": 4, "execution_authorized": False}

    def task(self, stage, value):
        require(stage in STAGES, "PREPARATION_STAGE_ONLY")
        return (pr.check(self.context / "meeting/author-task.md").read_text() +
            "\nExact required SPEC binding lines:\nrun_id: " + RUN +
            "\nmeeting_plan_sha256: " + self.config["plan_sha256"] +
            "\nUse the same plan hash as execution_plan_sha256 in scientific-program/v1. "
            "That legacy field name binds this preparation plan and grants no data execution. "
            "Review the whole authored code and actual synthetic receipt. Genuine REVISE returns to the author; "
            "REJECT or unresolved revise limit stops. All calls count within the four meeting slots.\n")

    def output_names(self, stage):
        return ("SPEC.proposed.md", "analysis.program.json") if stage == "run_spec_author" else super().output_names(stage)

    def prepare_input(self, value, stage, work):
        from orchestrator import manual_context
        from orchestrator import meeting_author_feedback as feedback
        bodies = feedback.files(self) if stage == "run_spec_author" else {}
        task = self.task(stage, value) + (feedback.instructions(bodies) if bodies else "")
        body, measurement = manual_context.prepare(self.context, stage=stage, idea_ids=self.config["idea_ids"],
            task=task, artifacts=value["artifacts"], workspace=work,
            structured_review=True, reference_prior_results=True,
            preparation_program=(stage == "run_spec_author"))
        return body, feedback.install(work, bodies, measurement) if bodies else measurement

    def _accept_completed(self, value):
        pending = value["pending"]
        row = self.store.db.execute("SELECT * FROM manual_calls WHERE id=?", (pending["id"],)).fetchone()
        require(row is not None and row["status"] == "COMPLETE", "TERMINAL_OUTPUT_REQUIRED")
        receipt = json.loads(row["receipt"]); work = Path(pending["workspace"])
        for name, pin in receipt["output_sha256"].items():
            require(sha(pr.check(work / name).read_bytes()) == pin, "COMPLETED_OUTPUT_CHANGED")
        if pending["stage"] == "run_spec_review":
            review = read(work / "review.json")
            if review.get("verdict") == "APPROVE":
                result = value.get("program_result", {})
                require(result.get("synthetic_status") == "PASS", "SYNTHETIC_PASS_REQUIRED")
                receipt_path = Path(result["folder"]) / "synthetic/receipt.json"
                require(sha(pr.check(receipt_path).read_bytes()) == result["synthetic_receipt_sha256"],
                        "SYNTHETIC_RECEIPT_CHANGED")
            return super()._accept_completed(value)
        require(pending["stage"] == "run_spec_author", "PREPARATION_STAGE_ONLY")
        spec_raw = pr.check(work / "SPEC.proposed.md").read_bytes(); spec = spec_raw.decode()
        require(len(spec) <= 12000 and all(spec.splitlines().count(line) == 1 for line in
                ("run_id: " + RUN, "meeting_plan_sha256: " + self.config["plan_sha256"])), "SPEC_BINDING")
        from orchestrator import scientific_program, scientific_intake
        program_raw = pr.check(work / "analysis.program.json").read_bytes()
        require(json.loads(program_raw).get("schema") == "scientific-program/v1", "PREPARATION_PROGRAM_SCHEMA")
        cases = scientific_intake.cohort(pr.check(self.context / "development99.json").read_bytes())
        program, compiled = scientific_program.validate(program_raw, run_id=RUN,
            plan_sha256=self.config["plan_sha256"], cases=cases)
        folder = self.state / "scientific-programs" / ("author-" + str(pending["round"]))
        write_once(folder / "analysis.program.json", program_raw)
        for name, text in program["files"].items():
            write_once(folder / name, text.encode())
        tests = (scientific_program.run(folder / "synthetic", program["files"], self.config["synthetic_environment"])
                 if all(r["compile"] == "PASS" for r in compiled) else
                 {"status": "FAIL", "reason": "COMPILE_FAILED_NO_EXECUTION", "real_data_execution": False})
        n = pending["round"]
        provenance = {"source_call_id": pending["id"], "program_sha256": sha(program_raw), "compile": compiled,
                      "plan_sha256": self.config["plan_sha256"], "scientific_approval": False,
                      "real_data_execution": False}
        for kind, name, raw in (
            ("run_spec", "SPEC-" + str(n) + ".md", spec_raw),
            ("proposed_run_spec", "proposed-SPEC-" + str(n) + ".md", spec_raw),
            ("analysis_source", "analysis-" + str(n) + ".py", program["files"]["analysis.py"].encode()),
            ("analysis_tests", "analysis-tests-" + str(n) + ".py", program["files"]["test_analysis.py"].encode()),
            ("analysis_provenance", "program-provenance-" + str(n) + ".json", encoded(provenance)),
            ("synthetic_tests", "program-tests-" + str(n) + ".json", encoded(tests))):
            self.artifact(value, kind, name, raw, n)
        result = {"folder": str(folder), "program_sha256": sha(program_raw), "synthetic_status": tests["status"]}
        if (folder / "synthetic/receipt.json").exists():
            result["synthetic_receipt_sha256"] = sha((folder / "synthetic/receipt.json").read_bytes())
        value.update(phase="run_spec_review", spec=str(work / "SPEC.proposed.md"), program_result=result)
        value["rounds"]["run_spec_author"] = n
        from orchestrator.author_revision_accounting import accepted
        accepted(self, pending)
        value.pop("pending")
        self.save(value)
        return self.status()
