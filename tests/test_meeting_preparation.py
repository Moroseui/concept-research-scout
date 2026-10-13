import copy
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from orchestrator import meeting_preparation as m
from orchestrator import colab_simple_full, manual_context, preparation_followup, autonomy_limits
from orchestrator import meeting_author_feedback as feedback

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def accounts(tmp_path, monkeypatch):
    db = sqlite3.connect(":memory:", isolation_level=None)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE autonomy_calls(id TEXT PRIMARY KEY,kind TEXT,change_id TEXT,round INTEGER,day TEXT,status TEXT,binding TEXT,receipt TEXT);
        CREATE TABLE autonomy_runs(id TEXT PRIMARY KEY,binding TEXT,status TEXT);
        CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT);
    """)
    for i in range(124):
        db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                   (f"prior-{i:03}", "scientific", "old-run", i, "2026-10-12", "COMPLETE", "{}", "{}"))
    parent = {"id": "accepted-parent", "binding": "{}", "status": "COMPLETE"}
    event = {"id": "accepted-parent:accepted", "job": "accepted-parent", "payload": '{"accepted":true}'}
    db.execute("INSERT INTO autonomy_runs VALUES(?,?,?)", tuple(parent.values()))
    db.execute("INSERT INTO events VALUES(?,?,?)", tuple(event.values()))
    scope = copy.deepcopy(m.document())
    scope.update(parent_owner=parent, parent_event=event, uncertain_rows=[], active_owners=[],
                 frozen_calls=[{"id":r["id"],"sha256":m.sha(m.encoded(dict(r)))} for r in db.execute("SELECT * FROM autonomy_calls ORDER BY id")])
    monkeypatch.setattr(m, "document", lambda: scope)
    monkeypatch.setattr(colab_simple_full, "_TERMINAL_QUALIFIER",
                        lambda a,r: {"id": r["id"], "proof_sha256": "a"*64})
    a = SimpleNamespace(db=db, folder=tmp_path, filesystem_root=tmp_path, scope=scope)
    yield a
    db.close()


def add_call(a, ident, run, status="COMPLETE"):
    a.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                 (ident, "scientific", run, 1, "2026-10-13", status, "{}", "{}"))


def owner(a):
    return {"state": a.scope["new_lane"], m.FIELD: {"scope_sha256": m.DOCUMENT_SHA},
            "source": "a"*40, "plan_sha256": a.scope["plan_sha256"], "review_sha256": "b"*64, "run_id": m.RUN}


def test_real_scope_and_exact_four_meeting_slots():
    scope = m.document()
    assert scope["allocation_limit"] == 4 and scope["baseline_count"] == 124
    assert scope["execution_authorized"] is False
    assert preparation_followup.module(m.RUN) is m
    assert preparation_followup.module("unrelated") is not m


def test_fourth_call_admitted_fifth_refused(accounts):
    for i in range(4):
        assert m.batch_allowance(accounts, accounts.scope)["meeting_allocation_used"] == i
        add_call(accounts, f"meeting-{i}", m.RUN)
    with pytest.raises(ValueError, match="MEETING_ALLOCATION_EXHAUSTED"):
        m.batch_allowance(accounts, accounts.scope)
    assert accounts.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0] == 128


def test_other_purpose_cannot_create_extra_global_capacity(accounts):
    for i in range(4):
        add_call(accounts, f"elsewhere-{i}", "other-purpose")
    with pytest.raises(ValueError, match="GLOBAL_BATCH_EXHAUSTED"):
        m.batch_allowance(accounts, accounts.scope)


def test_all_original_rows_and_acceptance_preserved(accounts):
    m.preserved(accounts, accounts.scope)
    accounts.db.execute("UPDATE autonomy_calls SET receipt='altered' WHERE id='prior-001'")
    with pytest.raises(ValueError, match="ORIGINAL_CALL_CHANGED"):
        m.preserved(accounts, accounts.scope)


def test_parent_acceptance_cannot_change(accounts):
    accounts.db.execute("UPDATE events SET payload='{}'")
    with pytest.raises(ValueError, match="ACCEPTED_PARENT_CHANGED"):
        m.preserved(accounts, accounts.scope)


def test_new_owner_is_distinct_and_duplicate_does_not_reset(accounts):
    before = [dict(r) for r in accounts.db.execute("SELECT * FROM autonomy_calls ORDER BY id")]
    m.register(accounts, owner(accounts), accounts.scope)
    current = dict(accounts.db.execute("SELECT * FROM autonomy_runs WHERE id=?", (m.RUN,)).fetchone())
    assert current["status"] == "ACTIVE" and json.loads(current["binding"]) == owner(accounts)
    with pytest.raises(ValueError, match="EXISTING_OWNER_NO_RESET"):
        m.register(accounts, owner(accounts), accounts.scope)
    assert before == [dict(r) for r in accounts.db.execute("SELECT * FROM autonomy_calls ORDER BY id")]


@pytest.mark.parametrize("state", ["RUNNING", "UNCERTAIN"])
def test_unknown_open_call_refuses_registration(accounts, state):
    accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                       ("unknown-open", "implementation_review", "other", 1, "2026-10-13", state, "{}", "{}"))
    with pytest.raises(ValueError, match="LIVE_MODEL_CALL|UNCLASSIFIED_OR_RUNNING_CALL"):
        m.register(accounts, owner(accounts), accounts.scope)
    assert not accounts.db.execute("SELECT 1 FROM autonomy_runs WHERE id=?", (m.RUN,)).fetchone()


def test_halt_refuses_without_mutation(accounts):
    (accounts.folder / "HALT").write_text("operator hold")
    with pytest.raises(ValueError, match="BATCH_HALT"):
        m.register(accounts, owner(accounts), accounts.scope)
    assert not accounts.db.execute("SELECT 1 FROM autonomy_runs WHERE id=?", (m.RUN,)).fetchone()


def test_terminal_classifier_must_exist(accounts, monkeypatch):
    monkeypatch.setattr(colab_simple_full, "_TERMINAL_QUALIFIER", None)
    with pytest.raises(ValueError, match="INSTALLED_TERMINAL_QUALIFIER_REQUIRED"):
        m.terminal_ids(accounts, accounts.scope)


def test_changed_allocation_document_refused(accounts):
    changed = {**accounts.scope, "allocation_limit": 5}
    with pytest.raises(ValueError, match="EXACT_ALLOCATION_SCOPE"):
        m.batch_allowance(accounts, changed)


def test_preparation_holds_commit_and_refuses_execution(monkeypatch):
    monkeypatch.setattr(m, "validate", lambda *a: {})
    driver = SimpleNamespace(config={"run_id":m.RUN}, store=object(), status=lambda:{"phase":"COMMIT_SPEC"})
    assert m.preparation_hold(driver, {"phase":"COMMIT_SPEC"}, None, None)["execution_authorized"] is False
    for phase in ["EXECUTE_CPU", "EMIT_PACKAGE", "WAIT_OUTPUTS", "UPDATE_STATE", "COMPLETE"]:
        with pytest.raises(ValueError, match="PREPARATION_ONLY"):
            m.preparation_hold(driver, {"phase":phase}, None, None)
    with pytest.raises(ValueError, match="NO_EXECUTION_OR_COLLECTION"):
        m.preparation_hold(driver, {"phase":"run_spec_author"}, Path("returned"), None)
    with pytest.raises(ValueError, match="NO_DATA_COMPLETION"):
        m.refuse_legacy_completion(None, m.RUN)


def test_config_cannot_impersonate_scope_or_change_author_timeout():
    config = {"run_id":m.RUN, m.FIELD:{"scope_sha256":m.DOCUMENT_SHA},
              "backend":"meeting-preparation","item_number":6,
              "author_timeout_seconds":1800,"review_contract":"bound-review/v1"}
    assert autonomy_limits.selected_run_limit(config, m.RUN) == 20
    for k,v in [("run_id","other"),("backend","cpu"),("author_timeout_seconds",900),
                ("review_contract","unbound"),(m.FIELD,{"scope_sha256":"0"*64})]:
        with pytest.raises(ValueError):
            m.validate_config({**config,k:v}, m.RUN)


@pytest.mark.parametrize("changed", [
    {"stage":"run_spec_review"}, {"structured_review":False},
    {"idea_ids":["directions-diagnostics"]}, {"execution_mode":"directions-diagnostics"},
    {"notebook_patch":True}, {"analysis_program":True}])
def test_output_request_does_not_expand_other_scopes(tmp_path, changed):
    args={"stage":"run_spec_author","idea_ids":["meeting-case-review"],"task":"test",
          "artifacts":[],"workspace":tmp_path/"w","structured_review":True,"preparation_program":True}
    args.update(changed)
    with pytest.raises(ValueError):
        manual_context.prepare(tmp_path, **args)


def fixture_program():
    return {"schema":"scientific-program/v1","run_id":m.RUN,"execution_plan_sha256":"b"*64,
            "files":{"analysis.py":"def main(input_root, output_root, contract):\n    return None\n",
                     "test_analysis.py":"import unittest\nclass Smoke(unittest.TestCase):\n    def test_fixture(self): self.assertEqual(2+2,4)\n"}}


def checker(tmp_path, program=None, spec=None):
    folder=tmp_path/".meeting-feedback";folder.mkdir()
    (folder/"check.py").write_text(feedback.CHECKER)
    (folder/"binding.json").write_text(json.dumps({"run_id":m.RUN,"plan_sha256":"b"*64}))
    (tmp_path/"SPEC.proposed.md").write_text(spec if spec is not None else "run_id: "+m.RUN+"\nmeeting_plan_sha256: "+"b"*64+"\n")
    raw=program if isinstance(program,str) else json.dumps(program or fixture_program())
    (tmp_path/"analysis.program.json").write_text(raw)
    return subprocess.run([sys.executable,"-I","-B",str(folder/"check.py")],cwd=tmp_path,capture_output=True,text=True)


def test_in_call_checker_accepts_schema_without_running_code(tmp_path):
    p=fixture_program()
    p["files"]["analysis.py"] += "\nraise RuntimeError('MUST_NOT_EXECUTE')\n"
    result=checker(tmp_path,p)
    assert result.returncode == 0, result.stderr
    assert "static only" in result.stdout


@pytest.mark.parametrize("mutation", ["extra-key","bad-plan","extra-file","missing-entry","bad-spec","duplicate-json","too-large"])
def test_in_call_checker_rejects_format_errors(tmp_path, mutation):
    p=fixture_program();spec=None
    if mutation=="extra-key":p["receipt"]="invented"
    elif mutation=="bad-plan":p["execution_plan_sha256"]="a"*64
    elif mutation=="extra-file":p["files"]["other.py"]="pass"
    elif mutation=="missing-entry":p["files"]["analysis.py"]="pass"
    elif mutation=="bad-spec":spec="run_id: wrong"
    elif mutation=="duplicate-json":p='{"schema":"scientific-program/v1","schema":"other"}'
    elif mutation=="too-large":p["files"]["analysis.py"] += "#"*80001
    assert checker(tmp_path,p,spec).returncode != 0


def test_native_template_preserves_protections(monkeypatch):
    from tools import meeting_preparation_runtime as rt
    scope=m.document()
    monkeypatch.setattr(rt,"metadata",lambda:(scope,scope["native"]))
    text=rt.unit_bytes(scope).decode()
    for required in ["User=partho","Group=partho","Restart=no","NoNewPrivileges=true",
                     "ProtectSystem=strict","PrivateTmp=true","TimeoutStartSec=3700"]:
        assert required in text.splitlines()
    assert "meeting_preparation_runtime.py run" in text
    old=scope["native"]["template_bytes"].splitlines()
    assert [x for x in text.splitlines() if x.startswith(("ExecStartPre=","ExecStopPost="))] == [x for x in old if x.startswith(("ExecStartPre=","ExecStopPost="))]

def test_global_reservation_counts_real_rows_and_refuses_fifth(accounts, monkeypatch):
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator.autonomy_review_runner import ReviewQueue
    from tools.deploy_manual_lane import bound
    accounts.db.execute("CREATE TABLE jobs(id TEXT PRIMARY KEY,binding TEXT,phase TEXT,status TEXT,receipt TEXT)")
    accounts.status=lambda ident: ReviewQueue.status(accounts,ident)
    m.register(accounts,owner(accounts),accounts.scope)
    config={"run_id":m.RUN,m.FIELD:{"scope_sha256":m.DOCUMENT_SHA},
            "backend":"meeting-preparation","item_number":6,"author_timeout_seconds":1800,
            "review_contract":"bound-review/v1"}
    lane=bound(accounts.filesystem_root,accounts.scope["new_lane"])
    lane.mkdir(parents=True);(lane/"lane.json").write_text(json.dumps(config))
    monkeypatch.setattr(m,"configuration",lambda a,run: accounts.scope if run==m.RUN else None)
    for i in range(4):
        stage="run_spec_author" if i%2==0 else "run_spec_review"
        workspace=Path(accounts.scope["new_lane"]).with_name("lane-scientific-workspaces")/(stage+"-"+str(i//2+1))
        bound(accounts.filesystem_root,str(workspace)).mkdir(parents=True)
        result=BatchAccounts.reserve_scientific(accounts,"new-"+str(i),m.RUN,stage,"a"*40,
                                                {"stage":stage,"workspace":str(workspace)})
        assert result["batch_limit"]==128 and result["run_limit"]==20
        assert accounts.db.execute("SELECT status FROM autonomy_calls WHERE id=?",("new-"+str(i),)).fetchone()[0]=="RUNNING"
        accounts.db.execute("UPDATE autonomy_calls SET status='COMPLETE' WHERE id=?",("new-"+str(i),))
        accounts.db.execute("UPDATE jobs SET status='COMPLETE' WHERE id=?",("new-"+str(i),))
    workspace=Path(accounts.scope["new_lane"]).with_name("lane-scientific-workspaces")/"run_spec_author-3"
    bound(accounts.filesystem_root,str(workspace)).mkdir()
    with pytest.raises(ValueError,match="MEETING_ALLOCATION_EXHAUSTED"):
        BatchAccounts.reserve_scientific(accounts,"new-4",m.RUN,"run_spec_author","a"*40,
                                        {"stage":"run_spec_author","workspace":str(workspace)})
    assert accounts.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==128
    assert not accounts.db.execute("SELECT 1 FROM jobs WHERE id='new-4'").fetchone()
    m.preserved(accounts,accounts.scope)


def test_unknown_active_owner_refuses_registration(accounts):
    accounts.db.execute("INSERT INTO autonomy_runs VALUES('new-unclassified','{}','ACTIVE')")
    with pytest.raises(ValueError,match="OTHER_OWNER_CHANGED"):
        m.register(accounts,owner(accounts),accounts.scope)


def test_changed_prior_owner_refuses_preservation(accounts):
    old={"id":"known-held","status":"ACTIVE","binding":"{}"}
    accounts.scope["active_owners"]=[old]
    accounts.db.execute("INSERT INTO autonomy_runs VALUES(?,?,?)",(old["id"],old["binding"],old["status"]))
    m.preserved(accounts,accounts.scope)
    accounts.db.execute("UPDATE autonomy_runs SET binding='changed' WHERE id='known-held'")
    with pytest.raises(ValueError,match="OTHER_OWNER_CHANGED"):
        m.preserved(accounts,accounts.scope)


def test_reviewer_approval_requires_host_pass_before_base_transition(tmp_path):
    d=m.MeetingDriver.__new__(m.MeetingDriver)
    db=sqlite3.connect(":memory:");db.row_factory=sqlite3.Row
    db.execute("CREATE TABLE manual_calls(id TEXT,status TEXT,receipt TEXT)")
    work=tmp_path/"work";work.mkdir()
    raw=json.dumps({"verdict":"APPROVE"}).encode();(work/"review.json").write_bytes(raw)
    db.execute("INSERT INTO manual_calls VALUES(?,?,?)",("review","COMPLETE",json.dumps({"output_sha256":{"review.json":m.sha(raw)}})))
    d.store=SimpleNamespace(db=db)
    value={"pending":{"id":"review","workspace":str(work),"stage":"run_spec_review","round":1},
           "program_result":{"synthetic_status":"FAIL"}}
    with pytest.raises(ValueError,match="SYNTHETIC_PASS_REQUIRED"):
        d._accept_completed(value)
    assert "pending" in value
    folder=tmp_path/"program";(folder/"synthetic").mkdir(parents=True)
    (folder/"synthetic/receipt.json").write_text("altered")
    value["program_result"]={"synthetic_status":"PASS","folder":str(folder),"synthetic_receipt_sha256":"b"*64}
    with pytest.raises(ValueError,match="SYNTHETIC_RECEIPT_CHANGED"):
        d._accept_completed(value)
    db.close()
