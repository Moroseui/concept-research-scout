"""Exact recovery, immutable accounting and genuine independent refusal behavior."""
import copy
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import experiment_timeout_continuation as t
from orchestrator import private_records as pr
from orchestrator.manual_executor import ManualExecutor, read, digest, atomic
from orchestrator.autonomy_accounting import BatchAccounts


def test_real_checkpoint_and_authority():
    p = t.checkpoint()
    assert p["source"] == "bd95553715d5049fcd459721b7b62487b9fbab95"
    assert set(p["lanes"]) == {"4", "6"}
    assert p["global_calls"][t.FAILED] == "2bd4bac93647618fcd17d1868dc9a4279ca66c3a0a9b1e04c46bbc12ec2d19be"


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    host = tmp_path; oldbase = host / "old"; newbase = host / "new"
    batch = BatchAccounts(host / "var/lib/research-system-autonomy/reviews", filesystem_root=host)
    p = {"source": "a" * 40, "runtime_sha256": digest(b"runtime"), "authority_sha256": "d" * 64,
         "lanes": {}, "owners": {}, "global_calls": {}, "partial_outputs": {}}
    lanes = []; oldcalls = {}; configs = {}
    for item, run in [(6, t.ITEM6), (4, t.ITEM4)]:
        old = oldbase / str(item) / "lane"; pr.mkdir(old, parents=True)
        pr.mkdir(old / "context"); pr.write_text(old / "context/unchanged.txt", "original evidence")
        pr.write_text(old / "preparation-plan.json", "original plan")
        owner = {"state": str(old), "run_id": run, "source": p["source"]}
        pr.write_text(old.parent / "owner.json", json.dumps(owner))
        batch.db.execute("INSERT INTO autonomy_runs VALUES(?,?,'ACTIVE')", (run, json.dumps(owner, sort_keys=True)))
        store = ManualExecutor(old / "jobs.sqlite")
        call = t.FAILED if item == 4 else "9" * 64
        receipt = json.dumps({"charged": True, "original": True})
        store.db.execute("INSERT INTO manual_calls VALUES(?,?,?,?,?)", (call, "run_spec_author", 1, "UNCERTAIN" if item == 4 else "COMPLETE", receipt))
        store.db.execute("INSERT INTO manual_account VALUES(1,7,?)", (json.dumps({"never_reset": True, "used": 1}),))
        batch.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)", (call, "scientific", run, 1, "2000-01-01", "UNCERTAIN" if item == 4 else "COMPLETE", "{}", receipt))
        work = oldbase / str(item) / "workspace"; pr.mkdir(work)
        for name in ("SPEC.proposed.md", "notebook.patch.json", "execution.plan.json"):
            body = ("unaccepted partial " + name).encode(); pr.write_bytes(work / name, body)
            if item == 4: p["partial_outputs"][name] = digest(body)
        value = {"phase": "BLOCKED" if item == 4 else "run_spec_review", "rounds": {} if item == 4 else {"run_spec_author": 1},
                 "artifacts": [], "interventions": [], "scientific_marker": "must not change"}
        if item == 4: value.update(reason="MODEL_FAILED_OR_UNCERTAIN_NO_RETRY", pending={"id": call, "workspace": "/old/4/workspace"})
        store.db.execute("INSERT INTO manual_state VALUES(1,?)", (json.dumps(value),))
        c = {"source": p["source"], "root": "/old/repository", "context": str(old / "context"), "run_id": run,
             "batch_ledger": "/var/lib/research-system-autonomy/reviews", "owner_path": "/old/" + str(item) + "/owner.json",
             "owner_binding": owner, "engine_files": {}, "profile_files": {}, "item_number": item}
        atomic(old / "lane.json", c); configs[item] = c
        pin = {"state": "/old/" + str(item) + "/lane", "run_id": run, "config_sha256": digest((old / "lane.json").read_bytes()),
               "plan_sha256": digest((old / "preparation-plan.json").read_bytes()), "owner_sha256": digest((old.parent / "owner.json").read_bytes()),
               "context_sha256": t.sha(t.inventory(old / "context")),
               "tables": {name: t.sha(t.rows(store.db, name)) for name in ["manual_state", "manual_calls", "manual_account", "manual_recoveries"]}}
        p["lanes"][str(item)] = pin
        p["global_calls"][call] = t.sha(dict(batch.db.execute("SELECT * FROM autonomy_calls WHERE id=?", (call,)).fetchone()))
        p["owners"][run] = t.sha(dict(batch.db.execute("SELECT * FROM autonomy_runs WHERE id=?", (run,)).fetchone()))
        oldcalls[item] = t.rows(store.db, "manual_calls"); store.db.close()
        row = {"item_number": item, "lane": "/new/" + str(item) + "/lane", "repository": "/new/" + str(item) + "/repository"}
        lanes.append(row); pr.mkdir(host / row["repository"].lstrip("/"), parents=True)
    selected = {"source": "b" * 40, "state": "/new", "runtime": "/runtime.json", "hash_list": "/record/hashes.json", "units": ["new.service", "new.timer"]}
    report = host / "review/report.md"; pr.mkdir(report.parent); pr.write_text(report, "actual review boundary mocked")
    approved = {"verdict": "APPROVE", "source_sha": selected["source"], "runtime_sha256": p["runtime_sha256"], "report_sha256": digest(report.read_bytes())}
    pr.write_bytes(host / "runtime.json", b"runtime")
    pr.mkdir(host / "etc/research-system-manual-sprint10", parents=True)
    atomic(host / "etc/research-system-manual-sprint10/selected-release.json", selected)
    monkeypatch.setattr(t, "checkpoint", lambda: p)
    monkeypatch.setattr("orchestrator.autonomy_review.verify_result", lambda path: approved)
    monkeypatch.setattr("orchestrator.administrative_terminal.verify", lambda row, folder: {"proof_sha256": "f" * 64, "classification": "PROVEN_EXACT_AUTHOR_TIMEOUT_ADMIN_ONLY"})
    monkeypatch.setattr("orchestrator.manual_host_guard.trusted", lambda path: Path(path))
    monkeypatch.setattr("tools.manual_host_control.release_lanes", lambda value, **kw: lanes)
    monkeypatch.setattr("tools.manual_promotion.manifest_check", lambda *a: {"source": selected["source"], "entrypoint": "experiment"})
    monkeypatch.setattr("tools.deploy_manual_lane.system", lambda *a: {"enabled": False, "active": False})
    monkeypatch.setattr("orchestrator.manual_driver.git", lambda root, *a: selected["source"] if a == ("rev-parse", "HEAD") else "astra/manual-test" if a == ("branch", "--show-current") else "")
    monkeypatch.setattr("orchestrator.analysis_driver.release_identities", lambda root: ({}, {}))
    return SimpleNamespace(host=host, batch=batch, p=p, selected=selected, report=report, approved=approved, lanes=lanes, oldcalls=oldcalls)


def prepare(f): return t.prepare(f.selected, f.report, filesystem_root=f.host)


def test_two_lanes_copied_once_with_original_charges(fixture):
    f = fixture; before = [dict(r) for r in f.batch.db.execute("SELECT * FROM autonomy_calls")]
    result = prepare(f); assert result["status"] == "CONTINUED_NO_CALL_OR_RESET"
    assert [dict(r) for r in f.batch.db.execute("SELECT * FROM autonomy_calls")] == before
    for item in [6, 4]:
        state = f.host / "new" / str(item) / "lane"
        with t.connect(state / "jobs.sqlite") as db:
            assert t.rows(db, "manual_calls") == f.oldcalls[item]
            assert t.rows(db, "manual_account")[0]["version"] == 7
            value = json.loads(t.rows(db, "manual_state")[0]["payload"])
        assert value["scientific_marker"] == "must not change"
        assert value["phase"] == ("run_spec_review" if item == 6 else "run_spec_author")
        if item == 4:
            assert value["rounds"] == {"run_spec_author": 1} and "pending" not in value
            assert value["linked_recovery_of"] == t.FAILED
            assert len(value["artifacts"]) == 4
    t.prior(f.host)
    assert t.global_exception(f.batch, t.ITEM6, source="b" * 40) == t.FAILED
    assert t.global_exception(f.batch, "unrelated", source="b" * 40) is None
    with pytest.raises(ValueError, match="ALREADY_CONTINUED"): prepare(f)
    store = ManualExecutor(f.host / "new/4/lane/jobs.sqlite", batch=f.batch)
    assert t.permit(store, t.ITEM4)["failed_id"] == t.FAILED
    assert t.permit(store, t.ITEM6) is None
    c = read(store.path.parent / "lane.json")
    t.validate_driver(SimpleNamespace(store=store, state=store.path.parent, config=c))
    c["item_number"] = 6
    with pytest.raises(ValueError, match="DRIVER_BINDING"): t.validate_driver(SimpleNamespace(store=store, state=store.path.parent, config=c))


@pytest.mark.parametrize("field,value", [("verdict", "REVISE"), ("verdict", "REJECT"), ("source_sha", "c" * 40), ("runtime_sha256", "c" * 64), ("report_sha256", "c" * 64)])
def test_wrong_approval_no_copy(fixture, field, value):
    f = fixture; f.approved[field] = value
    with pytest.raises(ValueError, match="EXACT_APPROVAL"): prepare(f)
    assert not (f.host / "new/6/lane").exists()


@pytest.mark.parametrize("kind", ["config", "context", "account", "call", "owner", "halt", "running", "partial"])
def test_changed_originals_refused(fixture, kind):
    f = fixture; lane = f.host / "old/4/lane"
    if kind == "config": pr.write_text(lane / "lane.json", "{}")
    elif kind == "context": pr.write_text(lane / "context/unchanged.txt", "changed")
    elif kind == "owner": pr.write_text(lane.parent / "owner.json", "{}")
    elif kind == "halt": pr.write_text(lane / "HALT", "operator stop")
    elif kind == "partial": pr.write_text(f.host / "old/4/workspace/notebook.patch.json", "changed")
    elif kind == "running": f.batch.db.execute("UPDATE autonomy_calls SET status='RUNNING' WHERE id=?", (t.FAILED,))
    else:
        with sqlite3.connect(lane / "jobs.sqlite") as db:
            db.execute("UPDATE manual_account SET version=0" if kind == "account" else "UPDATE manual_calls SET status='COMPLETE'")
    with pytest.raises(ValueError, match="EXPERIMENT_TIMEOUT_"): prepare(f)
    assert not f.batch.db.execute("SELECT 1 FROM events WHERE id=?", (t.KEY,)).fetchone()


def test_real_global_admission_retains_other_uncertainty_and_caps(fixture, monkeypatch):
    f = fixture; prepare(f)
    monkeypatch.setattr("orchestrator.autonomy_limits.global_limit", lambda *a: 20)
    monkeypatch.setattr("orchestrator.completed_run.closed_ids", lambda *a, **kw: set())
    ident = "2" * 64
    f.batch.reserve_scientific(ident, t.ITEM6, "run_spec_review", "b" * 40, {"synthetic": True})
    assert f.batch.status(t.FAILED)["status"] == "UNCERTAIN"
    with pytest.raises(ValueError, match="BATCH_UNCERTAIN_OR_RUNNING_CALL"):
        f.batch.reserve_scientific("3" * 64, t.ITEM4, "run_spec_author", "b" * 40, {})
    f.batch.finish_scientific(ident, {"synthetic": True}, "COMPLETE")
    with pytest.raises(ValueError, match="RUNTIME_SOURCE"):
        f.batch.reserve_scientific("3" * 64, t.ITEM4, "run_spec_author", "c" * 40, {})
    monkeypatch.setattr("orchestrator.autonomy_limits.DAILY", 0)
    with pytest.raises(ValueError, match="AUTONOMY_DAILY_CALL_LIMIT"):
        f.batch.reserve_scientific("3" * 64, t.ITEM4, "run_spec_author", "b" * 40, {})
    monkeypatch.setattr("orchestrator.autonomy_limits.DAILY", 30)
    f.batch.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)", ("8" * 64, "scientific", "other", 1, "2000-01-01", "UNCERTAIN", "{}", "{}"))
    with pytest.raises(ValueError, match="BATCH_UNCERTAIN_OR_RUNNING_CALL"):
        f.batch.reserve_scientific("3" * 64, t.ITEM4, "run_spec_author", "b" * 40, {})


def test_post_grant_drift_and_incomplete_successor_refuse(fixture):
    f = fixture; prepare(f)
    with pytest.raises(ValueError, match="SUCCESSOR_NOT_COMPLETE"):
        f.batch.complete_run(t.ITEM4, {"not_accepted": True})
    with pytest.raises(ValueError, match="STAGE_SCOPE"):
        t.global_exception(f.batch, t.ITEM6, source="b" * 40, stage="unrelated")
    f.approved["verdict"] = "REVISE"
    with pytest.raises(ValueError, match="GENUINE_APPROVAL"):
        t.global_exception(f.batch, t.ITEM6)
    f.approved["verdict"] = "APPROVE"
    f.batch.db.execute("UPDATE autonomy_calls SET status='COMPLETE' WHERE id=?", (t.FAILED,))
    with pytest.raises(ValueError, match="ORIGINAL_GLOBAL_CALL_CHANGED"):
        t.global_exception(f.batch, t.ITEM6)


def test_promotion_accepts_only_exact_two_held_predecessors(fixture):
    f = fixture; source = f.host / "source"; pr.mkdir(source / "deploy/manual-lane", parents=True)
    pr.write_bytes(source / "deploy/manual-lane/runtime.promotion.json", b"runtime")
    previous = {"source": "a" * 40, "state": "/old/6"}
    result = t.promotion_check(f.host, previous, source, "experiment")
    assert set(result) == {f.host / "old/6/lane", f.host / "old/4/lane"}
    for prior, entrypoint in [({**previous, "source": "f" * 40}, "experiment"), (previous, "analysis")]:
        with pytest.raises(ValueError, match="PROMOTION_SCOPE"):
            t.promotion_check(f.host, prior, source, entrypoint)


@pytest.mark.parametrize("uid", [0, 1003])
def test_root_prior_delegates_live_ledger_reads_to_existing_owner(monkeypatch, uid):
    calls = []
    monkeypatch.setattr(t.os, "geteuid", lambda: 0)
    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return SimpleNamespace(stdout=json.dumps({"uid": uid, "value": {"read_as_owner": True}}))
    monkeypatch.setattr(t.subprocess, "run", run)
    if uid == 0:
        with pytest.raises(ValueError, match="OWNER_READER_REQUIRED"): t.prior(Path("/"))
    else: assert t.prior(Path("/")) == {"read_as_owner": True}
    args, options = calls[0]
    assert options["user"] == options["group"] == 1003 and options["extra_groups"] == []
    assert options["check"] and options["close_fds"] and options["cwd"] == "/"
    assert args[:4] == ["/usr/bin/python3", "-I", "-B", "-c"]


@pytest.mark.parametrize("uid", [0, 1003])
def test_root_promotion_closure_checks_use_existing_owner(monkeypatch, uid):
    from tools import manual_promotion as mp
    calls = []; monkeypatch.setattr(mp.os, "geteuid", lambda: 0)
    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return SimpleNamespace(stdout=json.dumps({"uid": uid, "status": "PASS"}))
    monkeypatch.setattr(mp.subprocess, "run", run)
    if uid == 0:
        with pytest.raises(ValueError, match="PROMOTION_OWNER_READER_REQUIRED"):
            mp.require_uninitialized_lane(Path("/"), [Path("/original/lane")])
    else: mp.require_uninitialized_lane(Path("/"), [Path("/original/lane")])
    argv, options = calls[0]
    assert options["user"] == options["group"] == 1003 and options["extra_groups"] == []
    assert json.loads(argv[-1]) == ["/original/lane"] and options["check"]
