"""One exact terminal-author continuation; preserves owners, rows and allowances.

The existing held promotion and native services remain the only execution path.
The administrative terminal proof is evidence, not the authority: this change
requires its own genuine implementation approval and operator decision binding.
"""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
from contextlib import ExitStack
from orchestrator import private_records as pr
from orchestrator.manual_executor import digest, read, inventory, atomic, lock
from orchestrator.stocktake_recovery import connect
from tools.deploy_manual_lane import bound

CHECKPOINT = "01c256d5016abb3461b6c3dcf2bc1521be3c729a35c71e4d35692f3cc41ac638"
KEY = "experiment-timeout-continuation-20261007"
FAILED = "ed4eb7f9300898b6dfea30e58ec00e45e8b9585fe0162e7ee16e49f06c2a08a5"
ITEM4 = "experiment-a74959ac4546a982af4ae137"
ITEM6 = "diagnostics-b203ee1ce27e909d9d78d44a"
STAGES = {"run_spec_author", "run_spec_review", "result_interpretation_author", "result_interpretation_review"}


def encoded(value): return json.dumps(value, sort_keys=True)
def sha(value): return digest(encoded(value).encode())
def require(ok, reason):
    if not ok: raise ValueError("EXPERIMENT_TIMEOUT_" + reason)
def rows(db, table):
    require(table in {"manual_state", "manual_calls", "manual_account", "manual_recoveries"}, "TABLE")
    return [dict(r) for r in db.execute("SELECT * FROM " + table + " ORDER BY 1")]


def checkpoint():
    root = Path(__file__).resolve().parents[1]
    raw = (root / "docs/EXPERIMENT_TIMEOUT_CHECKPOINT_20261007.json").read_bytes()
    require(digest(raw) == CHECKPOINT, "CHECKPOINT_CHANGED")
    p = json.loads(raw)
    require(digest((root / "docs/EXPERIMENT_TIMEOUT_AUTHORITY_20261007.txt").read_bytes()) == p["authority_sha256"], "AUTHORITY_CHANGED")
    return p


def prior(host, *, quiescent=True):
    if os.geteuid() == 0:
        # Root publishes the held release, but only the existing owner opens
        # live SQLite (even a read-only connection can touch WAL sidecars).
        source = str(Path(__file__).resolve().parents[1])
        code = ("import sys,os,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);"
                "from orchestrator.experiment_timeout_continuation import prior;"
                "assert os.getuid()==os.geteuid()==1003;"
                "print(json.dumps({'uid':os.getuid(),'value':prior(Path(sys.argv[2]),quiescent=json.loads(sys.argv[3]))}))")
        result = subprocess.run(['/usr/bin/python3', '-I', '-B', '-c', code, source, str(host), json.dumps(quiescent)],
            user=1003, group=1003, extra_groups=[], cwd='/', env={'PATH':'/usr/bin:/bin'},
            close_fds=True, timeout=60, check=True, capture_output=True, text=True)
        value = json.loads(result.stdout)
        require(value['uid'] == 1003, 'OWNER_READER_REQUIRED')
        return value['value']
    p = checkpoint(); result = {}
    for item, pin in p["lanes"].items():
        lane = bound(host, pin["state"])
        pr.check_tree(lane / "context")
        require(not (lane / "HALT").exists(), "HALTED")
        require(digest(pr.check(lane / "lane.json").read_bytes()) == pin["config_sha256"], "OLD_CONFIG_CHANGED")
        c = read(lane / "lane.json")
        require(digest(pr.check(lane / "preparation-plan.json").read_bytes()) == pin["plan_sha256"], "PLAN_CHANGED")
        require(digest(pr.check(bound(host, c["owner_path"])).read_bytes()) == pin["owner_sha256"], "OWNER_CHANGED")
        require(sha(inventory(lane / "context")) == pin["context_sha256"], "CONTEXT_CHANGED")
        with connect(lane / "jobs.sqlite") as db:
            require(all(sha(rows(db, t)) == h for t, h in pin["tables"].items()), "OLD_ROWS_CHANGED")
            value = json.loads(rows(db, "manual_state")[0]["payload"])
        if item == "4":
            require(value.get("phase") == "BLOCKED" and value.get("reason") == "MODEL_FAILED_OR_UNCERTAIN_NO_RETRY"
                and value.get("pending", {}).get("id") == FAILED and not value.get("rounds"), "EXACT_TIMEOUT_STATE")
            work = bound(host, value["pending"]["workspace"])
            require(all(digest(pr.check(work / name).read_bytes()) == pin for name, pin in p["partial_outputs"].items()), "PARTIAL_OUTPUT_CHANGED")
        else:
            require(value.get("phase") == "run_spec_review" and not value.get("pending"), "ITEM6_REVIEW_READY")
        result[item] = (c, value)
    ledger = bound(host, result["6"][0]["batch_ledger"])
    require(not (ledger / "HALT").exists(), "BATCH_HALTED")
    with connect(ledger / "jobs.sqlite") as db:
        for ident, pin in p["global_calls"].items():
            row = db.execute("SELECT * FROM autonomy_calls WHERE id=?", (ident,)).fetchone()
            require(row is not None and sha(dict(row)) == pin, "ORIGINAL_GLOBAL_CALL_CHANGED")
        for ident, pin in p["owners"].items():
            row = db.execute("SELECT * FROM autonomy_runs WHERE id=?", (ident,)).fetchone()
            require(row is not None and row["status"] in {"ACTIVE", "COMPLETE"}, "OWNER_STATUS")
            value = {**dict(row), "status": "ACTIVE"}
            require(sha(value) == pin, "GLOBAL_OWNER_CHANGED")
        if quiescent:
            require(not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(), "CALL_RUNNING")
    return result


def promotion_check(host, previous, source, entrypoint):
    p = checkpoint(); prior(host)
    require(entrypoint == "experiment" and previous["source"] == p["source"]
        and previous["state"] + "/lane" == p["lanes"]["6"]["state"]
        and digest((Path(source)/"deploy/manual-lane/runtime.promotion.json").read_bytes()) == p["runtime_sha256"], "PROMOTION_SCOPE")
    return [bound(host, pin["state"]) for pin in p["lanes"].values()]


def binding(batch):
    row = batch.db.execute("SELECT payload FROM events WHERE id=?", (KEY,)).fetchone()
    if row is None: return None
    v = json.loads(row[0]); p = checkpoint()
    require(v["kind"] == KEY and v["checkpoint_sha256"] == CHECKPOINT and v["authority_sha256"] == p["authority_sha256"], "GRANT_BINDING")
    require(str(batch.folder.resolve()) == str(bound(v["filesystem_root"], "/var/lib/research-system-autonomy/reviews")), "GLOBAL_LEDGER")
    from orchestrator.autonomy_review import verify_result
    approved = verify_result(Path(v["review_path"]).parent)
    require((approved["verdict"], approved["source_sha"], approved["runtime_sha256"], approved["report_sha256"]) ==
        ("APPROVE", v["source"], p["runtime_sha256"], v["review_sha256"]), "GENUINE_APPROVAL")
    row = batch.db.execute("SELECT * FROM autonomy_calls WHERE id=?", (FAILED,)).fetchone()
    require(row is not None and sha(dict(row)) == p["global_calls"][FAILED], "ORIGINAL_GLOBAL_CALL_CHANGED")
    # Reuse the reviewed exact native classification and root-sealed evidence.
    # This separately reviewed grant authorizes only the two existing owners.
    from orchestrator.administrative_terminal import verify
    proof = verify(dict(row), bound(v["filesystem_root"], "/var/lib/research-system-autonomy/scientific-terminal") / FAILED)
    require(proof["proof_sha256"] == v["terminal_proof_sha256"]
        and proof["classification"] == "PROVEN_EXACT_AUTHOR_TIMEOUT_ADMIN_ONLY", "TERMINAL_PROOF")
    return v


def global_exception(batch, run, *, source=None, stage=None, completing=False):
    if run not in {ITEM6, ITEM4}: return None
    v = binding(batch)
    if v is None: return None
    require(source is None or source == v["source"], "RUNTIME_SOURCE")
    require(stage is None or stage in STAGES, "STAGE_SCOPE")
    if completing and run == ITEM4:
        successor = digest((ITEM4 + ":run_spec_author:2").encode())
        row = batch.db.execute("SELECT status FROM autonomy_calls WHERE id=?", (successor,)).fetchone()
        require(row is not None and row["status"] == "COMPLETE", "SUCCESSOR_NOT_COMPLETE")
    return FAILED


def permit(store, run):
    if run != ITEM4 or store.batch is None: return None
    v = binding(store.batch)
    if v is None: return None
    pin = v["lanes"]["4"]
    require(str(store.path.resolve()) == str(Path(pin["state"]) / "jobs.sqlite"), "LOCAL_LEDGER")
    c = read(store.path.parent / "lane.json")
    require(sha(c) == pin["config_sha256"], "CONFIG_CHANGED")
    with connect(bound(v["filesystem_root"], checkpoint()["lanes"]["4"]["state"]) / "jobs.sqlite") as old:
        require(sha(rows(old, "manual_calls")) == checkpoint()["lanes"]["4"]["tables"]["manual_calls"], "ORIGINAL_LOCAL_ROWS_CHANGED")
        original = old.execute("SELECT * FROM manual_calls WHERE id=?", (FAILED,)).fetchone()
    current = store.db.execute("SELECT * FROM manual_calls WHERE id=?", (FAILED,)).fetchone()
    require(original is not None and current is not None and dict(original) == dict(current), "LOCAL_ORIGINAL_CHANGED")
    return {"failed_id": FAILED, "stage": "terminal_author_continuation", "decision_sha256": v["authority_sha256"], "runtime_source": v["source"]}


def validate_driver(driver):
    v = binding(driver.store.batch)
    require(v is not None and driver.config.get("timeout_continuation") == KEY, "GRANT_REQUIRED")
    pin = v["lanes"][str(driver.config["item_number"])]
    require(driver.config["run_id"] == checkpoint()["lanes"][str(driver.config["item_number"])]["run_id"]
        and str(driver.state.resolve()) == pin["state"] and sha(driver.config) == pin["config_sha256"]
        and driver.config["source"] == v["source"], "DRIVER_BINDING")


@pr.private_umask
def prepare(selected, report, *, filesystem_root=Path("/")):
    """Copy two held lanes once, then publish one append-only grant. No launches."""
    from tools import manual_promotion, deploy_manual_lane as deploy
    from tools.manual_host_control import release_lanes
    from orchestrator.manual_driver import git, write_once
    from orchestrator.analysis_driver import release_identities
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_context import selected_artifacts
    from orchestrator.git_publication import scan
    from orchestrator.administrative_terminal import verify
    host = Path(filesystem_root).resolve(); p = checkpoint(); report = Path(report)
    require(host != Path("/") or os.getuid() == os.getgid() == 1003, "OWNER_REQUIRED")
    from orchestrator.manual_host_guard import trusted
    require(read(trusted(bound(host, manual_promotion.POINTER))) == selected, "SELECTED_RELEASE_CHANGED")
    installed = manual_promotion.manifest_check(host, str(Path(selected["hash_list"]).parent))
    require(installed["source"] == selected["source"] and installed.get("entrypoint") == "experiment", "HELD_INSTALL_REQUIRED")
    approved = verify_result(report.parent)
    require((approved["verdict"], approved["source_sha"], approved["runtime_sha256"], approved["report_sha256"]) ==
        ("APPROVE", selected["source"], p["runtime_sha256"], digest(report.read_bytes())), "EXACT_APPROVAL")
    require(digest(pr.check(bound(host, selected["runtime"])).read_bytes()) == p["runtime_sha256"], "RUNTIME_CHANGED")
    lanes = release_lanes(selected, filesystem_root=host)
    require({r["item_number"] for r in lanes} == {4, 6}, "TWO_LANES_REQUIRED")
    units = selected["units"] + [Path(p["lanes"]["6"]["state"]).parent.name + s for s in (".service", ".timer", "-item4.service", "-item4.timer")]
    require(all(deploy.system(host, "state", u) == {"enabled": False, "active": False} for u in units), "UNITS_NOT_HELD")
    with ExitStack() as stack:
        for pin in p["lanes"].values(): stack.enter_context(lock(bound(host, pin["state"]) / "driver.lock"))
        old = prior(host); ledger = bound(host, old["6"][0]["batch_ledger"])
        db = pr.Connection(ledger / "jobs.sqlite"); db.row_factory = sqlite3.Row; stack.callback(db.close)
        require(db.execute("SELECT 1 FROM events WHERE id=?", (KEY,)).fetchone() is None, "ALREADY_CONTINUED")
        failed = dict(db.execute("SELECT * FROM autonomy_calls WHERE id=?", (FAILED,)).fetchone())
        proof = verify(failed, bound(host, "/var/lib/research-system-autonomy/scientific-terminal") / FAILED)
        grant = {"kind": KEY, "checkpoint_sha256": CHECKPOINT, "authority_sha256": p["authority_sha256"],
            "source": selected["source"], "filesystem_root": str(host), "review_path": str(report.resolve()),
            "review_sha256": approved["report_sha256"], "terminal_proof_sha256": proof["proof_sha256"], "lanes": {}}
        work = []
        for row in lanes:
            item = str(row["item_number"]); before, value = old[item]
            state, root = bound(host, row["lane"]), bound(host, row["repository"])
            require(not state.exists() and not state.is_symlink(), "DESTINATION_EXISTS_RECONCILE")
            require(git(root, "rev-parse", "HEAD") == selected["source"] and not git(root, "status", "--porcelain"), "REVIEWED_REPOSITORY")
            profile, engine = release_identities(root)
            require(profile == before["profile_files"], "PROFILE_CHANGED")
            # Preserve extra authority bindings from the original experiment init.
            for name, pin in before["engine_files"].items():
                if name not in engine:
                    require(digest((root / name).read_bytes()) == pin, "AUTHORITY_CHANGED")
                    engine[name] = pin
            c = {**before, "root": str(root), "source": selected["source"], "branch": git(root, "branch", "--show-current"),
                "context": str(state / "context"), "workspace_root": str(state.parent / "lane-scientific-workspaces"),
                "engine_files": engine, "engine_review": {"path": str(report), "sha256": approved["report_sha256"]}, "timeout_continuation": KEY}
            grant["lanes"][item] = {"state": str(state), "config_sha256": sha(c)}
            work.append((item, state, c, value))
        write_once(bound(host, selected["state"]) / (KEY + "-intent.json"), encoded(grant).encode())
        for item, state, c, value in work:
            original = bound(host, p["lanes"][item]["state"]); pr.mkdir(state)
            for path in original.iterdir():
                if path.name in {"jobs.sqlite", "jobs.sqlite-wal", "jobs.sqlite-shm", "lane.json"}: continue
                if path.is_dir(): pr.copytree(path, state / path.name)
                else: pr.copyfile(path, state / path.name)
            with connect(original / "jobs.sqlite") as src, pr.Connection(state / "jobs.sqlite") as dst: src.backup(dst)
            atomic(state / "lane.json", c)
            if item == "4":
                require(value["phase"] == "BLOCKED" and value.get("reason") == "MODEL_FAILED_OR_UNCERTAIN_NO_RETRY"
                    and value["pending"]["id"] == FAILED and not value["rounds"], "EXACT_TIMEOUT_STATE")
                folder = state / "context/current/timeout-continuation-20261007"; pr.mkdir(folder, parents=True)
                descriptors = []
                pending = bound(host, value["pending"]["workspace"])
                materials = [("run_spec", "SPEC.proposed.md", pr.check(pending / "SPEC.proposed.md").read_bytes()),
                    ("notebook_patch", "notebook.patch.json", pr.check(pending / "notebook.patch.json").read_bytes()),
                    ("execution_conditions", "execution.plan.json", pr.check(pending / "execution.plan.json").read_bytes()),
                    ("configuration", "CONTINUATION.txt", b"The previous author invocation reached its fixed timeout. These are preserved UNACCEPTED partial drafts, not scientific approval. Continue and complete them; independently inspect and correct all unresolved implementation gaps. Preserve the frozen scope and pinned-image approach. SPEC.proposed.md must have at most 12000 Unicode characters; target below 11000. Write the complete required outputs, not a diff against the partial files. No patient execution or scientific acceptance occurred. The original call and charge remain counted.\n")]
                require(all(digest(body) == p["partial_outputs"][name] for kind, name, body in materials if name in p["partial_outputs"]), "PARTIAL_OUTPUT_CHANGED")
                for kind, name, body in materials:
                    scan("context/" + name, body); pr.write_bytes(folder / name, body)
                    descriptors.append({"id": "timeout-original-" + name, "type": kind, "version": 1,
                        "path": str((folder / name).relative_to(state / "context")), "sha256": digest(body)})
                value = {**value, "phase": "run_spec_author", "reason": None, "rounds": {"run_spec_author": 1},
                    "linked_recovery_of": FAILED, "artifacts": [*value["artifacts"], *descriptors]}
                value.pop("pending")
                selected_artifacts("run_spec_author", value["artifacts"])
                with pr.Connection(state / "jobs.sqlite") as dst:
                    dst.execute("UPDATE manual_state SET payload=? WHERE id=1", (json.dumps(value),))
            pr.check_tree(state)
        prior(host)
        with db:
            require(not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(), "CALL_RUNNING")
            db.execute("INSERT INTO events VALUES(?,?,?)", (KEY, ITEM4, encoded(grant)))
        return {"status": "CONTINUED_NO_CALL_OR_RESET", "first": ITEM6, "originals_preserved": True, "grant": grant}
