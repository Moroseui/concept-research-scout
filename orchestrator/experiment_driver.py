"""Bound experiment lane for approved items4/6; scientific code belongs to models.

Initialization never executes science or creates a provider. Native author/review
calls reuse Driver, ManualExecutor and BatchAccounts; execution packages go only
through experiment_package, never the old Sprint10 or analysis-only dispatch.
"""
import argparse
import json
import os
import re
from pathlib import Path

from orchestrator import analysis_driver as analysis, autonomy_backlog as backlog
from orchestrator import experiment_context as context, manual_context, manual_stage
from orchestrator import private_records as pr, context_budget, diagnostics_policy
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.manual_driver import Driver, STAGES, git, stamp, write_once
from orchestrator.manual_executor import ManualExecutor, read, digest, atomic
from orchestrator.scientific_intake import load_views

BASE_FIELDS = {"schema", "context", "context_files", "backlog", "backlog_binding", "operator",
    "item_number", "item_sha256", "private_intake", "idea_ids", "artifacts", "batch_ledger",
    "execution_scope", "execution_plan", "revision_policy", "prerequisites"}
SCOPED_FIELDS = {4: {"notebook_revision", "execution_provisioning"}, 6: {"synthetic_environment", "diagnostics", "execution_provisioning"}}


def selected_config(plan):
    item = plan.get("item_number")
    if type(item) is not int or item not in SCOPED_FIELDS:
        raise ValueError("EXPERIMENT_ITEM_REQUIRED")
    return {**plan, "backend": "modal" if item == 4 else "cpu",
            "run_id": context.ITEM4_RUN if item == 4 else diagnostics_policy.RUN_ID,
            "review_contract": "bound-review/v1"}


def verify_plan(plan, batch=None, *, context_root=None, inventory=True):
    if not isinstance(plan, dict): raise ValueError("EXPERIMENT_PLAN_FIELDS")
    config = selected_config(plan)
    from orchestrator.experiment_plan_output import enabled
    extra = {"authored_execution_plan"} if enabled(config) else set()
    from orchestrator.experiment_partition_input import enabled as partitions_enabled
    if partitions_enabled(config): extra.add("frozen_partitions")
    if set(plan) != BASE_FIELDS | SCOPED_FIELDS[plan["item_number"]] | extra or plan["schema"] != "experiment-lane/v1":
        raise ValueError("EXPERIMENT_PLAN_FIELDS")
    root = Path(context_root if context_root is not None else plan["context"])
    if not root.is_absolute(): raise ValueError("EXPERIMENT_ABSOLUTE_CONTEXT_REQUIRED")
    pr.check_tree(root)
    if inventory:
        observed = {str(p.relative_to(root)): digest(p.read_bytes()) for p in root.rglob("*") if p.is_file()}
        if observed != plan["context_files"]:
            raise ValueError("EXPERIMENT_CONTEXT_INVENTORY_CHANGED")
    context.validate_selection(config, plan, root)
    bound = lambda ref: analysis.bound_file(root, ref)
    authority = bound(plan["operator"])
    verified = backlog.load(bound(plan["backlog"]), json.loads(bound(plan["backlog_binding"])), authority)
    # The backlog's current authorization binding and each experiment's original
    # operator scope are separate: adding item6 must not replace item4's authority.
    scope = plan["execution_scope"]
    if plan["item_number"] == 6:
        if plan["item_sha256"] != diagnostics_policy.ITEM_SHA256:
            raise ValueError("DIAGNOSTICS_BACKLOG_ITEM_CHANGED")
    else:
        original = Path(__file__).resolve().parents[1]/"docs/SPRINT13B_EXECUTION_OPERATOR_DECISION.txt"
        if digest(original.read_bytes()) != scope["authority_sha256"]:
            raise ValueError("EXPERIMENT_OPERATOR_AUTHORITY_CHANGED")
    required = plan["prerequisites"]
    if not isinstance(required, list): raise ValueError("EXPERIMENT_PREREQUISITES_REQUIRED")
    completed = []
    for prior in required:
        if (not isinstance(prior, dict) or set(prior) != {"item_number", "run_id", "report"}
                or type(prior["item_number"]) is not int or prior["item_number"] not in (1, 2, 5)
                or prior["item_number"] in completed or not isinstance(prior["run_id"], str)):
            raise ValueError("EXPERIMENT_PREREQUISITE_BINDING")
        raw = bound(prior["report"])
        if batch is not None:
            row = batch.db.execute("SELECT binding,status FROM autonomy_runs WHERE id=?", (prior["run_id"],)).fetchone()
            event = batch.db.execute("SELECT payload FROM events WHERE id=?", (prior["run_id"]+":accepted",)).fetchone()
            if row is None or row["status"] != "COMPLETE" or event is None:
                raise ValueError("EXPERIMENT_PREREQUISITE_NOT_ACCEPTED")
            owner = json.loads(row["binding"])
            from tools.deploy_manual_lane import bound as host_path
            lane = pr.check(host_path(batch.filesystem_root, owner["state"])/"lane.json")
            config_prior = read(lane)
            if (config_prior.get("item_number") != prior["item_number"]
                    or config_prior.get("run_id") != prior["run_id"]
                    or config_prior.get("owner_binding") != owner
                    or json.loads(event["payload"]).get("report_sha256") != digest(raw)):
                raise ValueError("EXPERIMENT_PREREQUISITE_BINDING")
        completed.append(prior["item_number"])
    item = backlog.require_item(verified, plan["item_number"], plan["item_sha256"],
        "gpu" if plan["item_number"] == 4 else "cpu", completed_items=completed)
    if set(item.prerequisites) != set(completed):
        raise ValueError("EXPERIMENT_PREREQUISITE_SELECTION")
    for stage in manual_context.OUTPUTS:
        load_views(root, plan["private_intake"], stage=stage, idea_ids=plan["idea_ids"])
    for artifact in plan["artifacts"]: bound({k:artifact[k] for k in ("path", "sha256")})
    manual_context.selected_artifacts("run_spec_author", plan["artifacts"])
    context_budget.load(root)
    if plan["item_number"] == 4:
        from orchestrator.notebook_revision import validate_config
        validate_config(root, plan["notebook_revision"])
        directory = plan["execution_provisioning"]
        if not isinstance(directory, str) or not Path(directory).is_absolute():
            raise ValueError("EXPERIMENT_RUNTIME_DIRECTORY")
        from orchestrator.manual_host_guard import trusted
        if not pr.check(trusted(Path(directory))).is_dir(): raise ValueError("EXPERIMENT_RUNTIME_DIRECTORY")
        environment = plan["notebook_revision"]["environment"]
    else:
        directory = plan["execution_provisioning"]
        if not isinstance(directory,str) or not Path(directory).is_absolute():
            raise ValueError("EXPERIMENT_RUNTIME_DIRECTORY")
        # A draft binds only the future root-selected execution location. No
        # image/data readiness is invented or required before authoring.
        environment = plan["synthetic_environment"]
    from orchestrator.cpu_isolation import verify_environment
    verify_environment(environment)
    return verified, item


@pr.private_umask
def initialize(root, state, engine_review, plan_path):
    root, state, engine_review, plan_path = map(Path, (root, state, engine_review, plan_path))
    if not all(p.is_absolute() for p in (root, state, engine_review, plan_path)):
        raise ValueError("EXPERIMENT_ABSOLUTE_PATHS_REQUIRED")
    if state.exists() or state.is_symlink(): raise ValueError("EXISTING_EXPERIMENT_LANE_RECONCILE")
    if git(root, "status", "--porcelain"): raise ValueError("CLEAN_REVIEWED_SOURCE_REQUIRED")
    source = git(root, "rev-parse", "HEAD"); branch = git(root, "branch", "--show-current")
    if not re.fullmatch("astra/manual-[a-z0-9-]+", branch): raise ValueError("EXPERIMENT_ACCOUNTED_BRANCH_REQUIRED")
    from orchestrator.autonomy_review import verify_result
    approved = verify_result(engine_review.parent)
    runtime = os.environ.get("RESEARCH_MANUAL_RUNTIME_CONFIG")
    if not runtime or not Path(runtime).is_absolute(): raise ValueError("EXPLICIT_REVIEWED_RUNTIME_CONFIG_REQUIRED")
    if (approved["verdict"] != "APPROVE" or approved["source_sha"] != source
            or digest(pr.check(engine_review).read_bytes()) != approved["report_sha256"]
            or approved["runtime_sha256"] != digest(pr.check(Path(runtime)).read_bytes())):
        raise ValueError("QUALIFIED_EXACT_ENGINE_APPROVAL_REQUIRED")
    raw = pr.check(plan_path).read_bytes(); plan = json.loads(raw)
    manifest = read(engine_review.parent/"packet-manifest.json")
    from orchestrator.experiment_selection import reviewed_plan
    reviewed_plan(raw, manifest)
    verify_plan(plan)
    profile, engine = analysis.release_identities(root)
    from orchestrator import autonomy_limits
    from orchestrator.modal_item4_policy import AUTHORITY, TEAM_AUTHORITY
    authorities = {autonomy_limits.DOCUMENT:autonomy_limits.AUTHORITY,
        diagnostics_policy.DOCUMENT:diagnostics_policy.AUTHORITY,
        "docs/SPRINT13B_EXECUTION_OPERATOR_DECISION.txt":AUTHORITY,
        "docs/SPRINT13B_TEAM_OPERATOR_DECISION.txt":TEAM_AUTHORITY}
    for name, pin in authorities.items():
        if digest(pr.check(context_budget.relative_file(root,name)).read_bytes()) != pin:
            raise ValueError("EXPERIMENT_RELEASE_AUTHORITY_CHANGED")
        engine[name] = pin
    git(root, "var", "GIT_AUTHOR_IDENT"); git(root, "var", "GIT_COMMITTER_IDENT")
    clients = manual_stage.preflight()
    batch = BatchAccounts(plan["batch_ledger"])
    try:
        verify_plan(plan, batch)
        cfg = selected_config(plan); run = cfg["run_id"]
        batch.preflight_experiment_run(run, plan["execution_scope"])
        common = Path(git(root, "rev-parse", "--git-common-dir"))
        common = common if common.is_absolute() else root/common
        owner = common.resolve()/("experiment-owner-"+run+".json")
        if owner.exists() or owner.is_symlink(): raise ValueError("EXISTING_EXPERIMENT_OWNER_NO_NEW_ALLOWANCE")
        pr.mkdir(state, parents=True)
        pr.copytree(plan["context"], state/"context")
        pr.write_bytes(state/"preparation-plan.json", raw)
        binding = {"state":str(state.resolve()), "source":source, "run_id":run,
            "plan_sha256":digest(raw), "review_sha256":digest(engine_review.read_bytes()),
            "execution_scope":plan["execution_scope"]}
        write_once(owner, json.dumps(binding, sort_keys=True).encode())
        # Transaction rechecks parallel owners. A partial initializer never
        # removes an owner or silently retries with a fresh allowance.
        batch.register_experiment_run(run, binding)
        # Reuse the existing CAS policy; selected_run_limit supplies the exact
        # reviewed 20/30-call amendment. No new allowance/reset semantics.
        policy = {"status":"RATIFIED", "operator_approval":plan["execution_scope"]["authority_sha256"],
            "state_write_permission":"OPERATOR_AUTHORIZED", "n":4, "window":"UTC_CALENDAR_DAY",
            "state_ref":"refs/heads/automation/dispatch-state", "manual_semantics":"OPERATOR_STEP_D_MAX_EIGHT"}
        store = ManualExecutor(state/"jobs.sqlite", batch=batch)
        try:
            store.initialize_allowance(policy)
            authority_path = "docs/AUTONOMY_BATCH_2026-09-27.md"
            cfg.update(root=str(root), context=str(state/"context"), source=source, branch=branch,
                owner_path=str(owner), owner_binding=binding,
                engine_review={"path":str(engine_review), "sha256":digest(engine_review.read_bytes())},
                authority_path=authority_path, authority_sha256=digest((root/authority_path).read_bytes()),
                profile_files=profile, engine_files=engine, clients=clients, policy=policy,
                started_utc=stamp(), plan_sha256=digest(raw),
                workspace_root=str(state.parent/(state.name+"-scientific-workspaces")))
            atomic(state/"lane.json", cfg)
            store.db.execute("INSERT INTO manual_state VALUES(1,?)", (json.dumps({"phase":STAGES[0],
                "rounds":{}, "artifacts":plan["artifacts"], "interventions":[]}),))
        finally: store.db.close()
    finally: batch.db.close()
    return {"status":"READY", "run_id":run, "next":STAGES[0], "calls_used":0,
            "call_limit":20 if plan["item_number"] == 4 else 30}


class ExperimentDriver(Driver):
    def __init__(self, state, runner=None, provider_factory=None):
        self.state = Path(state); self.config = read(self.state/"lane.json")
        self.root = Path(self.config["root"]); self.context = Path(self.config["context"])
        context.selection(self)
        self.store = ManualExecutor(self.state/"jobs.sqlite", batch=BatchAccounts(self.config["batch_ledger"]))
        self.runner = runner or manual_stage.invoke
        self.provider_factory = provider_factory

    def guard(self):
        super().guard()
        plan = read(self.state/"preparation-plan.json")
        context.selection(self)
        for key in BASE_FIELDS | SCOPED_FIELDS[self.config["item_number"]]:
            if key not in {"context", "context_files"} and self.config.get(key) != plan[key]:
                raise ValueError("EXPERIMENT_CONFIG_PLAN_MISMATCH")
        # Immutable original files remain pinned. Current stage artifacts and
        # obligation dispositions are separately guarded by Driver and intake.
        verify_plan(plan, self.store.batch, context_root=self.context, inventory=False)
        owner = self.store.batch.db.execute("SELECT binding,status FROM autonomy_runs WHERE id=?",
            (self.config["run_id"],)).fetchone()
        if owner is None or json.loads(owner['binding'])!=self.config['owner_binding']:
            raise ValueError('EXPERIMENT_GLOBAL_OWNER_CHANGED')
        if owner['status']!='ACTIVE':
            event=self.store.batch.db.execute('SELECT payload FROM events WHERE id=?',(self.config['run_id']+':accepted',)).fetchone()
            report=self.state/'REPORT.md'
            if (owner['status']!='COMPLETE' or self.current()['phase'] not in {'REPORT','COMPLETE'}
                    or event is None or not report.is_file()
                    or json.loads(event['payload']).get('report_sha256')!=digest(report.read_bytes())):
                raise ValueError('EXPERIMENT_GLOBAL_OWNER_CHANGED')

    def task(self, stage, value):
        item = self.config["item_number"]
        return ("Approved BACKLOG item "+str(item)+". Use the frozen execution plan and original "
            "registered evidence. You are the scientific author or independent reviewer for this stage. "
            "Implement and test the actual experiment, preserving contrary evidence and unresolved findings. "
            "Only the controller executes reviewed code on development data after validation and cost gates. "
            "No final-evaluation or reserve patients. Report measured results, uncertainty and limitations; "
            "do not represent a synthetic test or a proposal as execution evidence. "
            + ("All five diagnostics share one CPU-only, no-training run and budget. " if item == 6 else
               "Follow the approved exhaustive screen, benchmark, checkpoint/resume and dollar caps. "))

    def status(self):
        value = super().status()
        value.update(package=str(self.state/"experiment-package"), collection_inbox=None,
            next_action=self.current()["phase"], execution_scope=self.config["execution_scope"])
        return value


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    for field in ("root", "state", "engine-review", "plan"): init.add_argument("--"+field, required=True)
    for cmd in ("status", "advance", "measure-projection", "measure-benchmark", "record-full-admission"):
        sub.add_parser(cmd).add_argument("--state", required=True)
    for cmd in ("prepare-execution", "prepare-preprocessing"):
        prepare = sub.add_parser(cmd)
        for field in ("state", "jobs", "destination"): prepare.add_argument("--"+field, required=True)
    reconcile = sub.add_parser("reconcile-preprocessing")
    for field in ("state", "job", "reason"): reconcile.add_argument("--"+field, required=True)
    args = parser.parse_args(argv)
    if args.command == "init": result = initialize(args.root, args.state, args.engine_review, args.plan)
    else:
        if args.command in {"prepare-execution", "prepare-preprocessing", "reconcile-preprocessing", "measure-projection", "measure-benchmark", "record-full-admission"}:
            # Root publication is separate and opens no service ledger. A root
            # command must not construct the write-capable lane driver here.
            if os.geteuid()==0 or pr.check(Path(args.state)/'jobs.sqlite').stat().st_uid!=os.geteuid():
                raise ValueError('EXPERIMENT_PREPARATION_OWNER_REQUIRED')
        driver = ExperimentDriver(args.state)
        try:
            if args.command in {"prepare-execution", "prepare-preprocessing"}:
                from orchestrator.manual_executor import lock
                from orchestrator.experiment_provisioning import prepare as prepare_handoff
                from orchestrator.review_contract import strict_json
                with lock(driver.state/'driver.lock'):
                    driver.guard()
                    rows=strict_json(pr.check(args.jobs).read_bytes())
                    result=prepare_handoff(driver,driver.current(),rows,args.destination,
                        kind="preprocessing" if args.command=="prepare-preprocessing" else "fit")
            elif args.command == "record-full-admission":
                from orchestrator.manual_executor import lock
                from orchestrator.experiment_full_admission import record
                with lock(driver.state/'driver.lock'):
                    driver.guard()
                    result=record(driver,driver.current())
            elif args.command in {"measure-projection", "measure-benchmark"}:
                from orchestrator.manual_executor import lock
                from orchestrator.experiment_projection import produce
                with lock(driver.state/'driver.lock'):
                    driver.guard()
                    result=produce(driver,driver.current(),kind="hardware" if args.command=="measure-benchmark" else "full")
            elif args.command == "reconcile-preprocessing":
                from orchestrator.manual_executor import lock
                from orchestrator.preprocessing_continuation import reconcile
                with lock(driver.state/'driver.lock'):
                    driver.guard()
                    result=reconcile(driver,driver.current(),args.job,args.reason)
            else: result = driver.status() if args.command == "status" else driver.advance()
        finally:
            driver.store.db.close(); driver.store.batch.db.close()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__": main()
