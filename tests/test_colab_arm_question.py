import copy
import json
import os
import sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import colab_arm_question as q
from orchestrator.autonomy_accounting import BatchAccounts


@pytest.fixture
def scenario(tmp_path, monkeypatch):
    os.umask(0o077)
    accounts = BatchAccounts(tmp_path / "batch", filesystem_root=tmp_path)
    old = tmp_path / "old"
    old.mkdir(mode=0o700)
    db = sqlite3.connect(old / "jobs.sqlite", isolation_level=None)
    db.row_factory = sqlite3.Row
    db.executescript("CREATE TABLE manual_calls(id TEXT PRIMARY KEY,stage TEXT,attempt INTEGER,status TEXT);"
                    "CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT);")
    for i in range(24):
        db.execute("INSERT INTO manual_calls VALUES(?,?,?,?)",
                   ("old-" + str(i), "run_spec_review", i + 1, "COMPLETE"))
    db.execute("INSERT INTO manual_state VALUES(1,?)", (json.dumps({"phase": "BLOCKED", "reason": "OUTPUT_VALIDATION_REFUSED: ANALYSIS_REVISION_ROUND"}),))
    cfg = {"run_id": "old"}
    (old / "lane.json").write_text(json.dumps(cfg))
    (old / "preparation-plan.json").write_text('{"frozen":true}')
    old_owner = {"id": "old", "binding": json.dumps({"colab_preparation": {}}), "status": "ACTIVE"}
    accounts.db.execute("INSERT INTO autonomy_runs VALUES(?,?,?)", tuple(old_owner.values()))
    accounts.db.execute("INSERT INTO autonomy_runs VALUES('history','{}','COMPLETE')")
    for i in range(106):
        owner = "history" if i < 82 else "old"
        ident = "history-" + str(i) if i < 82 else "old-" + str(i - 82)
        accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                            (ident, "scientific", owner, i + 1, "2026-10-11", "COMPLETE", "{}", "{}"))
    scope = {"run_id": q.RUN, "arm": "A1_pnorm_v2", "call_limit": 20, "batch_limit": 128,
             "allocation_limit": 16, "allocation_baseline": 104,
             "batch_answer_sha256": "a" * 64, "batch_question_sha256": "b" * 64,
             "new_lane": "/new/lane",
             "prior": {"config": cfg, "lane": "/old", "owner": old_owner,
                       "local_calls": [dict(r) for r in db.execute("SELECT * FROM manual_calls ORDER BY rowid")],
                       "state_row": dict(db.execute("SELECT * FROM manual_state").fetchone()),
                       "global_calls": [dict(r) for r in accounts.db.execute("SELECT * FROM autonomy_calls ORDER BY rowid")],
                       "plan_sha256": q.sha((old / "preparation-plan.json").read_bytes()),
                       "active_owners": [old_owner], "uncertain": []}}
    monkeypatch.setattr(q, "document", lambda: scope)
    yield NS(accounts=accounts, old=db, scope=scope, root=tmp_path)
    db.close()
    accounts.db.close()


def binding():
    return {"state": "/new/lane", "source": "a" * 40,
            "colab_preparation": {"arm_question": {"arm": "A1_pnorm_v2", "scope_sha256": q.DOCUMENT_SHA}}}


def test_preflight_preserves_original_owner_state_and_all_calls(scenario):
    x = scenario
    before = list(x.accounts.db.iterdump())
    q.preflight(x.accounts, q.RUN, binding())
    assert list(x.accounts.db.iterdump()) == before
    assert q.batch_allowance(x.accounts, x.scope)["colab_allocation_used"] == 2


@pytest.mark.parametrize("damage", ["owner", "global", "local", "state", "config", "plan", "live", "unknown_owner", "wrong_arm", "wrong_run", "wrong_state"])
def test_registration_refuses_drift_and_wrong_question(scenario, damage):
    x = scenario
    args = binding()
    run = q.RUN
    if damage == "owner":
        x.accounts.db.execute("UPDATE autonomy_runs SET status='COMPLETE' WHERE id='old'")
    elif damage == "global":
        x.accounts.db.execute("UPDATE autonomy_calls SET receipt='changed' WHERE id='old-0'")
    elif damage == "local":
        x.old.execute("UPDATE manual_calls SET status='FAILED' WHERE id='old-0'")
    elif damage == "state":
        x.old.execute("UPDATE manual_state SET payload='{}'")
    elif damage in {"config", "plan"}:
        name = "lane.json" if damage == "config" else "preparation-plan.json"
        (x.root / "old" / name).write_text("{}")
    elif damage == "live":
        x.accounts.db.execute("UPDATE autonomy_calls SET status='RUNNING' WHERE id='old-0'")
    elif damage == "unknown_owner":
        x.accounts.db.execute("INSERT INTO autonomy_runs VALUES('other','{}','ACTIVE')")
    elif damage == "wrong_arm":
        args["colab_preparation"]["arm_question"]["arm"] = "A1_multiwin"
    elif damage == "wrong_run":
        run = "new-salt-to-reset-usage"
    else:
        args["state"] = "/different"
    with pytest.raises(ValueError):
        q.preflight(x.accounts, run, args)


def install_owner(x):
    state = x.root / "new/lane"
    state.mkdir(parents=True, mode=0o700)
    cfg = {"run_id": q.RUN, "item_number": 4, "idea_ids": ["sprint13b-execution", "colab-preparation-20261010"],
           "colab_preparation": binding()["colab_preparation"]}
    (state / "lane.json").write_text(json.dumps(cfg))
    x.accounts.db.execute("INSERT INTO autonomy_runs VALUES(?,?,'ACTIVE')",
                          (q.RUN, json.dumps(binding())))


def reserve(x, monkeypatch, ident):
    # Only host approval/terminal qualification is replaced; actual global
    # transaction, daily, run, batch and Colab-allocation refusals execute.
    monkeypatch.setattr(q, "configuration", lambda accounts, run: x.scope if run == q.RUN else None)
    monkeypatch.setattr(q, "terminal_ids", lambda accounts, scope: [])
    return x.accounts.reserve_scientific(ident, q.RUN, "run_spec_author", "a" * 40,
                                        {"stage": "run_spec_author"})


def test_actual_reservation_counts_once_and_duplicate_refuses(scenario, monkeypatch):
    x = scenario
    install_owner(x)
    result = reserve(x, monkeypatch, "fresh")
    assert result["run_limit"] == 20 and result["batch_limit"] == 128 and result["daily_limit"] == __import__("orchestrator.autonomy_limits",fromlist=["daily_allowance"]).daily_allowance(__import__("datetime").datetime.now(__import__("datetime").timezone.utc).date().isoformat())["limit"]
    with pytest.raises(ValueError, match="DUPLICATE"):
        reserve(x, monkeypatch, "fresh")
    assert x.accounts.db.execute("SELECT count(*) FROM autonomy_calls WHERE id='fresh'").fetchone()[0] == 1


@pytest.mark.parametrize("cap", ["allocation", "batch", "daily", "run"])
def test_actual_admission_still_refuses_every_cap(scenario, monkeypatch, cap):
    from datetime import datetime, timezone
    x = scenario
    install_owner(x)
    today = datetime.now(timezone.utc).date().isoformat()
    if cap == "allocation":
        for i in range(14):
            x.accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                                  ("new-" + str(i), "scientific", q.RUN, i + 1, "2026-10-11", "COMPLETE", "{}", "{}"))
        error = "COLAB_ALLOCATION_EXHAUSTED"
    elif cap == "batch":
        for i in range(22):
            x.accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                                  ("new-" + str(i), "scientific", "history", i + 1, "2026-10-11", "COMPLETE", "{}", "{}"))
        error = "AUTONOMY_BATCH_CALL_LIMIT"
    elif cap == "daily":
        for i in range(__import__("orchestrator.autonomy_limits",fromlist=["daily_allowance"]).daily_allowance(today)["limit"]):
            x.accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                                  ("admin-" + str(i), "implementation_review", "admin", i + 1, today, "COMPLETE", "{}", "{}"))
        error = "AUTONOMY_DAILY_CALL_LIMIT"
    else:
        # Independently reach run20 without the narrower allocation masking it.
        monkeypatch.setattr(q, "batch_allowance", lambda *args: {"limit": 128})
        for i in range(20):
            x.accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                                  ("run-" + str(i), "scientific", q.RUN, i + 1, "2026-10-11", "COMPLETE", "{}", "{}"))
        error = "AUTONOMY_RUN_CALL_LIMIT"
    before = x.accounts.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]
    with pytest.raises(ValueError, match=error):
        reserve(x, monkeypatch, "refused")
    assert x.accounts.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0] == before
    assert not x.accounts.db.execute("SELECT 1 FROM autonomy_calls WHERE id='refused'").fetchone()


def test_allocation_counts_failed_and_open_attempts(scenario):
    x = scenario
    install_owner(x)
    for i, status in enumerate(["FAILED", "UNCERTAIN", "RUNNING"]):
        x.accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                              ("new-" + str(i), "scientific", q.RUN, i + 1, "2026-10-12", status, "{}", "{}"))
    assert q.batch_allowance(x.accounts, x.scope)["colab_allocation_used"] == 5


def test_exact_module_navigation_preserves_author_bytes_and_failed_test_status(tmp_path):
    module = ("def main(input_root, output_root, contract): pass\n"
              "def preprocess(input_root, output_root, contract): pass\n"
              "def validate_preprocessing(output_root, contract): pass\n"
              "def synthetic_tests(): pass\n")
    nb = json.dumps({"cells": [{"cell_type": "code", "source": ["%%writefile /content/sprint13_pipeline.py\n", module]}]}).encode()
    folder = tmp_path / "notebook"
    package = folder / "synthetic/package"
    package.mkdir(parents=True, mode=0o700)
    file = package / "execution.py"
    file.write_bytes(module.encode())
    file.chmod(0o600)
    tests = {"status": "FAIL", "binding": {"files": {"execution.py": q.sha(module.encode())}}}
    captured = []
    driver = NS(artifact=lambda *args: captured.append(args))
    q.execution_reading_artifact(driver, {}, {"round": 1}, nb, tests, folder)
    assert len(captured) == 1 and captured[0][3] == module.encode()
    assert tests["status"] == "FAIL"
    file.write_bytes(b"changed")
    with pytest.raises(ValueError, match="AUTHORED_MODULE_BINDING"):
        q.execution_reading_artifact(driver, {}, {"round": 1}, nb, tests, folder)


def test_compile_failure_does_not_invent_execution_module(tmp_path):
    q.execution_reading_artifact(NS(artifact=lambda *args: pytest.fail("invented module")),
                                {}, {"round": 1}, b"invalid", {"status": "FAIL"}, tmp_path)


def test_completed_question_cannot_receive_another_allowance(scenario):
    x = scenario
    x.accounts.db.execute("INSERT INTO autonomy_runs VALUES(?,?,'COMPLETE')",
                          (q.RUN, json.dumps(binding())))
    with pytest.raises(ValueError, match="EXISTING_QUESTION"):
        q.preflight(x.accounts, q.RUN, binding())


def test_bound_real_scope_preserves_caps_and_specific_distinct_arm():
    # Read actual immutable authority after undoing per-test fixture patches.
    scope = q.document()
    assert scope["arm"] == "A1_pnorm_v2" and scope["run_id"] == q.RUN
    assert (scope["call_limit"], scope["batch_limit"], scope["allocation_limit"]) == (20, 128, 16)
    assert len(scope["prior"]["global_calls"]) == 117
    assert len(scope["prior"]["local_calls"]) == 24
    assert scope["prior"]["local_calls"][-1]["status"] == "COMPLETE"
    assert scope["execution_authorized"] is False


def test_native_unit_changes_only_question_specific_paths(monkeypatch):
    from tools import colab_pnorm_v2_runtime as runtime
    root = Path(__file__).resolve().parents[1]
    native = json.loads((root / "docs/COLAB_PNORM_V2_NATIVE_PRIVATE.json").read_bytes())
    scope = {"new_lane": native["work"] + "/lane"}
    monkeypatch.setattr(runtime, "metadata", lambda: (scope, native))
    result = runtime.unit_bytes(scope).decode()
    changed = {"Description", "ConditionPathExists", "WorkingDirectory", "ExecStart",
               "Environment", "ReadWritePaths"}
    untouched = lambda text: [line for line in text.splitlines()
                              if line.split("=", 1)[0] not in changed]
    assert untouched(result) == untouched(native["template_bytes"])
    before = next(line for line in native["template_bytes"].splitlines() if line.startswith("ReadWritePaths="))
    after = next(line for line in result.splitlines() if line.startswith("ReadWritePaths="))
    assert after == before.replace(native["template_work"], native["work"])
    assert "TimeoutStartSec=3700" in result and "Restart=no" in result
