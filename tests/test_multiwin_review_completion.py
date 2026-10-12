"""Real SQLite recovery and actual counted final-slot admission, no models."""
import copy,json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from test_multiwin_local_allowance import live,reserve
from orchestrator import multiwin_review_completion as r, multiwin_local_allowance as bridge
from orchestrator import private_records as pr,manual_stage
from orchestrator.manual_executor import Accounts,digest

@pytest.fixture
def failed(live):
    x=live;lane=Path(x.store.path).parent
    x.config["context"]=str(lane/"context");pr.mkdir(lane/"context");pr.atomic(lane/"lane.json",x.config)
    workroot=Path(x.config["workspace_root"]);pr.mkdir(workroot)
    author=workroot/"run_spec_author-12";pr.mkdir(author)
    pr.write_text(author/"SPEC.proposed.md","synthetic spec");pr.write_text(author/"notebook.patch.json","{}")
    areceipt={"workspace":str(author),"output_sha256":{n:r.sha((author/n).read_bytes())for n in["SPEC.proposed.md","notebook.patch.json"]}}
    failed_receipt={"error_type":"TerminalSubmissionFailure","reason":"ACCEPTED_SUBMISSION_REQUIRED","outcome":"FAILED"}
    for stage,n,receipt,status in[("run_spec_author",12,areceipt,"COMPLETE"),(r.STAGE,10,failed_receipt,"FAILED")]:
        ident=digest((r.RUN+":"+stage+":"+str(n)).encode())
        x.store.db.execute("INSERT INTO manual_calls VALUES(?,?,?,?,?)",(ident,stage,n,status,json.dumps(receipt)))
        x.batch.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
            (ident,"scientific",r.RUN,22 if n==12 else 23,"2026-10-12",status,"{}",json.dumps(receipt)))
    work=workroot/"run_spec_review-10";pr.mkdir(work)
    final={"type":"result","subtype":"error_max_turns","is_error":False,"num_turns":30,"session_id":"synthetic-terminal"}
    pr.write_text(work/"console.log",json.dumps(final))
    pr.write_text(work/".review-submission-config.json","{}")
    revised=lane/"revised";pr.mkdir(revised)
    for name in["revised.ipynb","notebook.diff","manifest.json"]:pr.write_text(revised/name,"synthetic "+name)
    state={"phase":"BLOCKED","reason":r.REASON,"pending":{"id":r.CALL,"stage":r.STAGE,"round":10,"workspace":str(work)},
      "rounds":{"run_spec_author":12,"run_spec_review":9},"interventions":[],"artifacts":[],
      "spec":str(author/"SPEC.proposed.md"),"notebook_revision_result":{"folder":str(revised),
      "notebook_sha256":r.sha((revised/"revised.ipynb").read_bytes()),"diff_sha256":r.sha((revised/"notebook.diff").read_bytes())},
      "colab_delivery":{"folder":str(revised),"manifest_sha256":r.sha((revised/"manifest.json").read_bytes())}}
    x.store.db.execute("INSERT INTO manual_state VALUES(1,?)",(json.dumps(state),))
    version,account=Accounts(x.store).read()
    account["count"]=12;account["sequence"]=20
    account["events"]["manual:"+digest(b"synthetic-author12")+":1"]={
      "source":x.config["source"],"branch":x.config["branch"],"day":"2026-10-12","count":12,"notification":None,"halted":False}
    assert Accounts(x.store).cas(version,account)
    rows=lambda db,table:[dict(a)for a in db.execute("SELECT *FROM "+table+" ORDER BY rowid")]
    b={"config":copy.deepcopy(x.config),"lane":str(lane),"configuration_sha256":r.sha((lane/"lane.json").read_bytes()),
       "local_rows":rows(x.store.db,"manual_calls"),"global_rows":rows(x.batch.db,"autonomy_calls"),
       "owner":dict(x.batch.db.execute("SELECT *FROM autonomy_runs WHERE id=?",(r.RUN,)).fetchone()),
       "failed_workspace":str(work),"native_final":final,
       "files":{f.name:{"sha256":r.sha(f.read_bytes()),"bytes":f.stat().st_size}for f in work.iterdir()},
       "state_row":dict(x.store.db.execute("SELECT *FROM manual_state WHERE id=1").fetchone()),
       "account_row":dict(x.store.db.execute("SELECT *FROM manual_account WHERE id=1").fetchone())}
    d=NS(store=x.store,state=lane,config=x.config,
         current=lambda:json.loads(x.store.db.execute("SELECT payload FROM manual_state WHERE id=1").fetchone()[0]))
    return NS(x=x,b=b,d=d,approval="c"*64,work=work)

def test_exact_recovery_preserves_all23_calls_science_and_account(failed):
    f=failed;x=f.x
    assert r.recover(f.d,f.b,f.approval)=={"status":"READY_REVIEW11","model_calls":0,"preserved_calls":23,"maximum_remaining_calls":1}
    after=f.d.current()
    assert after["rounds"]=={"run_spec_author":12,"run_spec_review":10}
    assert after["phase"]==r.STAGE and "pending"not in after
    for key in["artifacts","spec","notebook_revision_result","colab_delivery"]:
        assert after[key]==json.loads(f.b["state_row"]["payload"])[key]
    assert [dict(a)for a in x.store.db.execute("SELECT *FROM manual_calls ORDER BY rowid")]==f.b["local_rows"]
    assert [dict(a)for a in x.batch.db.execute("SELECT *FROM autonomy_calls ORDER BY rowid")]==f.b["global_rows"]
    assert dict(x.store.db.execute("SELECT *FROM manual_account WHERE id=1").fetchone())==f.b["account_row"]
    with pytest.raises(ValueError):r.recover(f.d,f.b,f.approval)

@pytest.mark.parametrize("bad",["local","global","owner","state","account","config","console","accepted","review","author","notebook","delivery","halt","live","nextwork"])
def test_any_drift_or_genuine_verdict_refuses_without_recovery(failed,bad):
    f=failed;x=f.x
    if bad in{"local","global"}:
        db,table=(x.store.db,"manual_calls")if bad=="local"else(x.batch.db,"autonomy_calls")
        db.execute("UPDATE "+table+" SET receipt='changed' WHERE id=?",(f.b["local_rows"][0]["id"],))
    elif bad=="owner":x.batch.db.execute("UPDATE autonomy_runs SET status='STOPPED'")
    elif bad=="state":x.store.db.execute("UPDATE manual_state SET payload='{}'")
    elif bad=="account":x.store.db.execute("UPDATE manual_account SET version=version+1")
    elif bad=="config":pr.atomic(f.d.state/"lane.json",{**x.config,"extra":True})
    elif bad=="console":pr.write_text(f.work/"console.log","changed")
    elif bad in{"accepted","review"}:pr.write_text(f.work/(".review-submission.json"if bad=="accepted"else"review.json"),'{"verdict":"REVISE"}')
    elif bad=="author":pr.write_text(Path(x.config["workspace_root"])/"run_spec_author-12/SPEC.proposed.md","changed")
    elif bad in{"notebook","delivery"}:pr.write_text(f.d.state/"revised"/("revised.ipynb"if bad=="notebook"else"manifest.json"),"changed")
    elif bad=="halt":pr.write_text(f.d.state/"HALT","operator stop")
    elif bad=="live":x.batch.db.execute("INSERT INTO autonomy_calls VALUES('live','scientific','other',1,'2026-10-12','RUNNING','{}',NULL)")
    else:pr.mkdir(Path(x.config["workspace_root"])/"run_spec_review-11")
    before=[tuple(a)for a in x.store.db.execute("SELECT *FROM manual_state")]
    with pytest.raises(ValueError):r.recover(f.d,f.b,f.approval)
    assert [tuple(a)for a in x.store.db.execute("SELECT *FROM manual_state")]==before
    assert not(f.d.state/r.EVENT).exists()

def test_recovery_then_real_final_slot_admission_and_command(failed,monkeypatch):
    f=failed;x=f.x;r.recover(f.d,f.b,f.approval)
    restore=bridge.bind(x.config,"b"*64,"c"*64,lambda store:r.granted(f.d,f.b,f.approval))
    argv=["claude","--max-turns","30","--permission-mode","default","--tools","Read","--allowedTools","bound"]
    monkeypatch.setattr(manual_stage,"reviewer_command",lambda *args:list(argv))
    undo=r.bind_command(f.d,f.b,f.approval)
    try:
        ident,n,receipt=reserve(x,r.STAGE)
        assert(ident,n)==(r.NEXT,11)
        assert receipt["batch_accounting"]["run_limit"]==24
        assert receipt["batch_accounting"]["batch_limit"]==128
        assert receipt["accounting"]["count"]==13
        work=Path(x.config["workspace_root"])/"run_spec_review-11"
        state=f.d.current();state.update(phase="MODEL_RUNNING",pending={"id":ident,"stage":r.STAGE,"round":11,"workspace":str(work)})
        x.store.db.execute("UPDATE manual_state SET payload=?",(json.dumps(state),))
        actual=manual_stage.reviewer_command(work,r.STAGE)
        expected=list(argv);expected[2]="60";assert actual==expected
        with pytest.raises(ValueError):reserve(x,r.STAGE)
    finally:undo();restore()
    assert x.store.db.execute("SELECT count(*)FROM manual_calls").fetchone()[0]==24
    assert x.batch.db.execute("SELECT count(*)FROM autonomy_calls").fetchone()[0]==24

@pytest.mark.parametrize("bad",["work","stage","command","grant","reserved"])
def test_zero_call_command_binds_only_qualified_probe(failed,monkeypatch,bad):
    f=failed;x=f.x;r.recover(f.d,f.b,f.approval)
    argv=["claude","--max-turns","60"if bad=="command"else"30","--tools","Read"]
    monkeypatch.setattr(manual_stage,"reviewer_command",lambda *args:argv)
    if bad=="grant":x.store.db.execute("DELETE FROM events WHERE id=?",(r.EVENT,))
    if bad=="reserved":x.batch.db.execute("INSERT INTO autonomy_calls VALUES(?,'scientific',?,24,'2026-10-12','RUNNING','{}',NULL)",(r.NEXT,r.RUN))
    undo=r.bind_command(f.d,f.b,f.approval,probe=True)
    try:
        work=f.d.state/(r.EVENT+"-qualification")/("wrong"if bad=="work"else"reviewer")
        with pytest.raises(ValueError):manual_stage.reviewer_command(work,"result_interpretation_review"if bad=="stage"else r.STAGE)
    finally:undo()

def test_probe_changes_only_turn_value_no_reservation(failed,monkeypatch):
    f=failed;r.recover(f.d,f.b,f.approval)
    original=["claude","--max-turns","30","--tools","Read","--permission-mode","default"]
    monkeypatch.setattr(manual_stage,"reviewer_command",lambda *args:list(original))
    undo=r.bind_command(f.d,f.b,f.approval,probe=True)
    try:assert manual_stage.reviewer_command(f.d.state/(r.EVENT+"-qualification")/"reviewer",r.STAGE)==["claude","--max-turns","60",*original[3:]]
    finally:undo()
    assert f.x.store.db.execute("SELECT count(*)FROM manual_calls").fetchone()[0]==23
    assert f.x.batch.db.execute("SELECT count(*)FROM autonomy_calls").fetchone()[0]==23

def test_runtime_keeps_unit_protections(monkeypatch,tmp_path):
    from tools import multiwin_review_runtime as rt
    from orchestrator import manual_host_guard
    unit=(chr(10).join(["[Service]","User=partho","ProtectSystem=strict","NoNewPrivileges=yes",
        "ExecStart=/usr/bin/python3 -s -B "+str(rt.PRIOR/"tools/multiwin_shared_runtime.py")+" run",""])).encode()
    path=tmp_path/"unit";path.write_bytes(unit)
    monkeypatch.setattr(manual_host_guard,"trusted",lambda p:path)
    parent=NS(UNIT="old.service",ENTRY="tools/multiwin_shared_runtime.py",authority=lambda:None)
    assert rt.unit_bytes(parent).replace(str(rt.ROOT/rt.ENTRY).encode(),str(rt.PRIOR/parent.ENTRY).encode())==unit
