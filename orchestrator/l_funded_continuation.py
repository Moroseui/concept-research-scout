"""Existing L lane: authenticated baseline context and its funded allocation.

No scientific code, provider launcher, new owner, cap increase or status rewrite.
Runtime authentication must provide the installed budget policy and sibling proof.
"""
from pathlib import Path
import copy
import hashlib
import json

RUN = "colab-arm-47e6a72d9a2c821a4938fcae"
CHANGE = "l-funded-continuation-20261013"

def require(ok, why):
    if not ok:
        raise ValueError("L_FUNDED_" + why)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def activate(checkpoint, history, qualify, policy, budget_scope, review_sha256):
    from orchestrator import colab_arm_question as old
    originals = old.preserved, old.batch_allowance, old.terminal_ids
    def preserved(accounts, scope):
        require(scope == old.document(), "ORIGINAL_SCOPE")
        return history.preserved(accounts, scope, checkpoint["lanes"]["multiwin"], qualify)
    def allowance(accounts, scope):
        preserved(accounts, scope)
        return policy.allowance(accounts, RUN, budget_scope, review_sha256)
    def terminals(accounts, scope):
        # The inherited verifier requires equality of the entire pending set.
        # Qualify the exact union, never call it on an obsolete six-row subset.
        proof = preserved(accounts, scope)
        from orchestrator import colab_simple_full as prior
        original = scope["prior"]["uncertain"]
        additions = [r for r in checkpoint["lanes"]["multiwin"]["global_rows"]
                     if r["id"] == history.AUTHOR]
        require(len(original) == 6 and len(additions) == 1 and
                history.AUTHOR not in {r["id"] for r in original},
                "EXACT_TERMINAL_CONTRACT")
        expected = sorted([*original, *additions], key=lambda r: r["id"])
        require(len({r["id"] for r in expected}) == 7, "TERMINAL_COLLISION")
        rows = [dict(r) for r in accounts.db.execute(
            "SELECT * FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN') ORDER BY id")]
        require(rows == expected and all(r["status"] == "UNCERTAIN" for r in rows),
                "UNCLASSIFIED_OR_RUNNING_CALL")
        require(callable(prior._TERMINAL_QUALIFIER), "INSTALLED_TERMINAL_QUALIFIER_REQUIRED")
        for row in rows:
            if row["id"] == history.AUTHOR:
                require(proof["call"] == row["id"] and proof["native_exit"] == "ok" and
                        proof["original_status"] == "UNCERTAIN" and proof["new_calls"] == 0 and
                        proof["scientific_acceptance"] is False, "RECOVERY_QUALIFICATION")
                continue
            result = prior._TERMINAL_QUALIFIER(accounts, row)
            require(isinstance(result, dict) and result.get("id") == row["id"] and
                    isinstance(result.get("proof_sha256"), str) and len(result["proof_sha256"]) == 64,
                    "AUTHENTIC_TERMINAL_PROOF_REQUIRED")
        return [r["id"] for r in rows]
    old.preserved, old.batch_allowance, old.terminal_ids = preserved, allowance, terminals
    def restore():
        old.preserved, old.batch_allowance, old.terminal_ids = originals
    return restore

def original_lane(driver, bound, *, state=True):
    from orchestrator import private_records as pr
    require(driver.config == bound["config"] and driver.config["run_id"] == RUN, "CONFIG")
    require(str(driver.state) == bound["lane"] and
            Path(driver.store.path) == driver.state / "jobs.sqlite", "LANE")
    require(sha(pr.check(driver.state / "lane.json").read_bytes()) == bound["config_sha256"], "CONFIG_BYTES")
    require(not (driver.state / "HALT").exists() and
            not (driver.store.batch.folder / "HALT").exists(), "HALT")
    require(not driver.store.batch.db.execute(
        "SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(), "LIVE_MODEL")
    require([dict(r) for r in driver.store.db.execute("SELECT * FROM manual_calls ORDER BY rowid")] ==
            bound["local_rows"], "LOCAL_CALLS")
    require([dict(r) for r in driver.store.batch.db.execute(
        "SELECT * FROM autonomy_calls WHERE change_id=? ORDER BY rowid", (RUN,))] ==
            bound["global_rows"], "GLOBAL_CALLS")
    require(len(bound["local_rows"]) == len(bound["global_rows"]) == 4 and
            all(r["status"] == "COMPLETE" for r in bound["local_rows"]), "FOUR_ORIGINAL_CALLS")
    require(dict(driver.store.db.execute("SELECT * FROM manual_account WHERE id=1").fetchone()) ==
            bound["account_row"], "ACCOUNT")
    require(dict(driver.store.batch.db.execute(
        "SELECT * FROM autonomy_runs WHERE id=?", (RUN,)).fetchone()) == bound["owner"], "OWNER")
    if state:
        require(dict(driver.store.db.execute("SELECT * FROM manual_state WHERE id=1").fetchone()) ==
                bound["state_row"], "STATE")
    value = json.loads(bound["state_row"]["payload"])
    require(value["phase"] == "run_spec_author" and value["reason"] == "REVISION_REQUIRED" and
            value["rounds"] == {"run_spec_author": 2, "run_spec_review": 2} and
            not value.get("pending"), "GENUINE_REVISION")
    for ref in value["artifacts"]:
        name = Path(ref["path"])
        require(not name.is_absolute() and ".." not in name.parts, "ARTIFACT_PATH")
        require(sha(pr.check(driver.context / name).read_bytes()) == ref["sha256"], "ARTIFACT_CHANGED")
    return value

def apply(driver, checkpoint, approval, question, baseline, pins):
    from orchestrator import private_records as pr
    from orchestrator.manual_executor import lock
    with lock(driver.state / "driver.lock"):
        driver.guard()
        bound = checkpoint["lanes"]["L"]
        value = original_lane(driver, bound)
        require(sha(question) == pins["question_sha256"] and
                sha(baseline) == pins["baseline_sha256"], "CONTEXT_BINDINGS")
        dest = driver.state / CHANGE
        require(not dest.exists() and not dest.is_symlink(), "ALREADY_ATTEMPTED")
        pr.mkdir(dest)
        pr.write_bytes(dest / "original-state.json", bound["state_row"]["payload"].encode())
        pr.write_bytes(dest / "INTENT.json", encoded({
            "source": approval["source_sha"], "review": approval["report_sha256"],
            "model_calls": 0, "original_calls": 4}))
        temporary = copy.deepcopy(value)
        driver.artifact(temporary, "question", "L-funded-revision-question.md", question, 3)
        driver.artifact(temporary, "prior_results", "L-authenticated-baseline-reference.json", baseline, 3)
        refs = [next(r for r in temporary["artifacts"] if r["id"] == k)
                for k in ("question", "prior_results")]
        updated = copy.deepcopy(value)
        updated["artifacts"] = [r for r in value["artifacts"]
                                if r["id"] not in {"question", "prior_results"}] + refs
        updated["interventions"].append({
            "kind": CHANGE, "review_sha256": approval["report_sha256"],
            "checkpoint_sha256": sha(encoded(checkpoint)), "original_calls": 4,
            "budget_policy": "existing scientific-batch140 L allocation",
            "scientific_findings_unchanged": True})
        require({k:v for k,v in updated.items() if k not in {"artifacts", "interventions"}} ==
                {k:v for k,v in value.items() if k not in {"artifacts", "interventions"}},
                "CONTEXT_ONLY")
        measurements = {}
        for stage in ("run_spec_author", "run_spec_review"):
            body, measurement = driver.prepare_input(updated, stage, dest / (stage + "-preflight"))
            require(all(ref["sha256"] in body for ref in refs), "INPUT_BINDINGS")
            measurements[stage] = measurement
        pr.write_bytes(dest / "INPUT_PREFLIGHT.json", encoded(measurements))
        db = driver.store.db
        db.execute("BEGIN IMMEDIATE")
        try:
            original_lane(driver, bound)
            db.execute("UPDATE manual_state SET payload=? WHERE id=1", (json.dumps(updated),))
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
        original_lane(driver, bound, state=False)
        require(driver.current() == updated, "COMMITTED_STATE")
        result = {"status": "L_BASELINE_CONTEXT_READY_NO_CALL", "model_calls": 0,
                  "source": approval["source_sha"], "review_sha256": approval["report_sha256"],
                  "phase": updated["phase"], "original_calls": 4, "artifacts": refs}
        pr.write_bytes(dest / "COMPLETE.json", encoded(result))
        return result
