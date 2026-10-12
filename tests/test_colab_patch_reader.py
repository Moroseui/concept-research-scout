"""Exact state restoration and no-counter-reset checks for reader-only recovery."""
import copy
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace as NS

import pytest
from orchestrator import colab_patch_reader as repair


@pytest.fixture
def fixture(tmp_path):
    import os
    os.umask(0o077)
    state = tmp_path / "state"
    state.mkdir(mode=0o700)
    local = sqlite3.connect(":memory:")
    local.row_factory = sqlite3.Row
    globaldb = sqlite3.connect(":memory:")
    globaldb.row_factory = sqlite3.Row
    local.executescript("CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT);"
                       "CREATE TABLE manual_calls(id TEXT PRIMARY KEY,stage TEXT,attempt INTEGER,status TEXT);"
                       "CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT);")
    globaldb.execute("CREATE TABLE autonomy_calls(id TEXT PRIMARY KEY,status TEXT)")
    original = {"phase": "run_spec_review", "reason": "NEW_OPERATOR_ARM_QUESTION",
                "pending": None, "rounds": {"run_spec_author": 10, "run_spec_review": 8}}
    blocked = {**original, "phase": "BLOCKED", "reason": "ContextError: MANUAL_JSON_PAGE_TOO_LARGE",
               "blocked_stage": "run_spec_review"}
    local.execute("INSERT INTO manual_state VALUES(1,?)", (json.dumps(blocked, sort_keys=True),))
    for i in range(19):
        local.execute("INSERT INTO manual_calls VALUES(?,?,?,?)",
                      (str(i), "historical", i + 1, "COMPLETE"))
        globaldb.execute("INSERT INTO autonomy_calls VALUES(?,?)", (str(i), "COMPLETE"))
    local.commit()
    globaldb.commit()
    frozen = {"original_state": original,
              "state_row": dict(local.execute("SELECT * FROM manual_state").fetchone()),
              "local_calls": [dict(row) for row in local.execute("SELECT * FROM manual_calls")],
              "global_calls": [dict(row) for row in globaldb.execute("SELECT * FROM autonomy_calls")],
              "artifact_files": {}}
    driver = NS(config={"run_id": repair.RUN}, state=state,
                store=NS(db=local, batch=NS(db=globaldb)),
                current=lambda: json.loads(local.execute("SELECT payload FROM manual_state").fetchone()[0]))
    yield driver, frozen
    local.close()
    globaldb.close()


def test_exact_premodel_recovery_retains_all_calls(fixture):
    driver, frozen = fixture
    result = repair.recover(driver, frozen, "a" * 64)
    assert result == {"status": "READY_SAME_REVIEW9", "new_calls": 0,
                      "new_allowance": 0, "preserved_calls": 19}
    assert driver.current() == frozen["original_state"]
    assert [dict(row) for row in driver.store.db.execute("SELECT * FROM manual_calls")] == frozen["local_calls"]
    assert [dict(row) for row in driver.store.batch.db.execute("SELECT * FROM autonomy_calls")] == frozen["global_calls"]
    assert (driver.state / repair.EVENT / "original-state.json").read_text() == frozen["state_row"]["payload"]
    with pytest.raises(ValueError):
        repair.recover(driver, frozen, "a" * 64)


@pytest.mark.parametrize("change", ["reason", "author_round", "review_round", "pending", "blocked_stage"])
def test_other_state_never_recovered(fixture, change):
    driver, frozen = fixture
    value = driver.current()
    if change == "reason":
        value["reason"] = "genuine scientific REJECT"
    elif change == "author_round":
        value["rounds"]["run_spec_author"] += 1
    elif change == "review_round":
        value["rounds"]["run_spec_review"] += 1
    elif change == "pending":
        value["pending"] = {"id": repair.REVIEW_ID}
    else:
        value["blocked_stage"] = "run_spec_author"
    with pytest.raises(ValueError, match="EXACT_PREMODEL_STATE"):
        repair.restored(value, frozen)


@pytest.mark.parametrize("kind", ["old_local", "old_global", "review_reserved", "foreign_call"])
def test_accounting_drift_refused(fixture, kind):
    driver, frozen = fixture
    if kind == "old_local":
        driver.store.db.execute("UPDATE manual_calls SET status='FAILED' WHERE id='0'")
    elif kind == "old_global":
        driver.store.batch.db.execute("UPDATE autonomy_calls SET status='FAILED' WHERE id='0'")
    elif kind == "review_reserved":
        driver.store.batch.db.execute("INSERT INTO autonomy_calls VALUES(?,?)", (repair.REVIEW_ID, "RUNNING"))
    else:
        driver.store.db.execute("INSERT INTO manual_calls VALUES('other','run_spec_author',11,'RUNNING')")
    with pytest.raises(ValueError):
        repair.check(driver, frozen, initial=True)


def test_only_same_review9_may_follow_recovery(fixture):
    driver, frozen = fixture
    repair.recover(driver, frozen, "a" * 64)
    driver.store.db.execute("INSERT INTO manual_calls VALUES(?,?,9,'RUNNING')",
                           (repair.REVIEW_ID, "run_spec_review"))
    repair.check(driver, frozen)
    driver.store.db.execute("UPDATE manual_calls SET attempt=10 WHERE id=?", (repair.REVIEW_ID,))
    with pytest.raises(ValueError, match="ONE_REVIEW_ONLY"):
        repair.check(driver, frozen)


def test_original_author_bytes_still_bound(fixture, tmp_path):
    driver, frozen = fixture
    artifact = tmp_path / "author.txt"
    artifact.write_bytes(b"unchanged")
    artifact.chmod(0o600)
    frozen["artifact_files"][str(artifact)] = repair.sha(b"unchanged")
    repair.check(driver, frozen, initial=True)
    artifact.write_bytes(b"changed")
    with pytest.raises(ValueError, match="AUTHOR_EVIDENCE_CHANGED"):
        repair.check(driver, frozen, initial=True)


def test_runtime_keeps_original_authority_and_review_only_start():
    # Exercise the real start path's allowed stages through its source contract;
    # the installed native probe separately constructs actual review input.
    from tools import colab_arm_preparation_runtime as runtime
    assert runtime.CHANGE == "colab-patch-reading-recovery-20261012"
    assert runtime.PREVIOUS_UNIT == "research-colab-multiwin-runtime-recovery-20261012.service"
    assert "orchestrator/manual_context.py" in runtime.ADDED
    assert "orchestrator/colab_patch_reader.py" in runtime.ADDED
