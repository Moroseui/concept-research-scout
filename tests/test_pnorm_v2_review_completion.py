"""Real SQLite recovery and ordinary local/global admission; no model clients."""
import copy,json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from test_colab_arm_question import scenario,install_owner
from orchestrator import pnorm_v2_review_completion as r,colab_arm_question as q
from orchestrator import private_records as pr,manual_stage,dispatch_limiter
from orchestrator.manual_executor import ManualExecutor,Accounts

@pytest.fixture
def failed(scenario,monkeypatch):
    x=scenario;install_owner(x);lane=x.root/"new/lane"
    x.scope["offsets"]={stage:0 for stage in q.STAGES}
    config=json.loads((lane/"lane.json").read_bytes())
    policy={"status":"RATIFIED","operator_approval":"synthetic","state_write_permission":"OPERATOR_AUTHORIZED",
            "n":3,"window":"UTC_CALENDAR_DAY","state_ref":dispatch_limiter.REF,
            "manual_semantics":"OPERATOR_SERVER_SPRINT10_MAX_SIX"}
    config.update(context=str(lane/"context"),workspace_root=str(x.root/"work"),source="a"*40,
                  branch="astra/manual-synthetic",policy=policy)
    pr.mkdir(lane/"context");pr.atomic(lane/"lane.json",config)
    store=ManualExecutor(lane/"jobs.sqlite",batch=x.accounts);store.initialize_allowance(policy)
    pr.mkdir(Path(config["workspace_root"]))
    author=Path(config["workspace_root"])/"run_spec_author-1";pr.mkdir(author)
    for name in ["SPEC.proposed.md","notebook.patch.json"]:pr.write_text(author/name,"synthetic "+name)
    areceipt={"workspace":str(author),"output_sha256":{p.name:r.sha(p.read_bytes())for p in author.iterdir()}}
    freceipt={"error_type":"TerminalSubmissionFailure","reason":"ACCEPTED_SUBMISSION_REQUIRED","outcome":"FAILED"}
    for i,(stage,receipt,status)in enumerate([("run_spec_author",areceipt,"COMPLETE"),(r.STAGE,freceipt,"FAILED")]):
        ident=r.sha((r.RUN+":"+stage+":1").encode())
        store.db.execute("INSERT INTO manual_calls VALUES(?,?,?,?,?)",(ident,stage,1,status,json.dumps(receipt)))
        x.accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",(ident,"scientific",r.RUN,i+1,"2026-10-12",status,"{}",json.dumps(receipt)))
    work=Path(config["workspace_root"])/"run_spec_review-1";pr.mkdir(work)
    final={"type":"result","subtype":"error_max_turns","num_turns":30,"is_error":False,"session_id":"synthetic-terminal"}
    pr.write_text(work/"console.log",json.dumps(final))
    pr.write_text(work/".review-submission-config.json","{}")
    revised=lane/"revised";pr.mkdir(revised)
    for name in ["revised.ipynb","notebook.diff"]:pr.write_text(revised/name,"synthetic "+name)
    state={"phase":"BLOCKED","reason":r.REASON,"pending":{"id":r.CALL,"stage":r.STAGE,"round":1,"workspace":str(work)},
        "rounds":{"run_spec_author":1},"interventions":[],"artifacts":[],"spec":str(author/"SPEC.proposed.md"),
        "notebook_revision_result":{"folder":str(revised),"synthetic_status":"FAIL",
            "notebook_sha256":r.sha((revised/"revised.ipynb").read_bytes()),"diff_sha256":r.sha((revised/"notebook.diff").read_bytes())}}
    store.db.execute("INSERT INTO manual_state VALUES(1,?)",(json.dumps(state),))
    version,account=Accounts(store).read();account.update(count=2,sequence=2,day="2026-10-12",halted=False)
    for i in range(2):
        account["events"]["manual:"+r.sha(("old"+str(i)).encode())+":1"]={"source":config["source"],"branch":config["branch"],"day":"2026-10-12","count":i+1,"notification":None,"halted":False}
    assert Accounts(store).cas(version,account)
    rows=[dict(a)for a in store.db.execute("SELECT *FROM manual_calls ORDER BY rowid")]
    b={"config":copy.deepcopy(config),"lane":str(lane),"configuration_sha256":r.sha((lane/"lane.json").read_bytes()),
       "local_rows":rows,"global_rows":[dict(x.accounts.db.execute("SELECT *FROM autonomy_calls WHERE id=?",(a["id"],)).fetchone())for a in rows],
       "owner":dict(x.accounts.db.execute("SELECT *FROM autonomy_runs WHERE id=?",(r.RUN,)).fetchone()),
       "failed_workspace":str(work),"native_final":final,"files":{p.name:{"bytes":p.stat().st_size,"sha256":r.sha(p.read_bytes())}for p in work.iterdir()},
       "state_row":dict(store.db.execute("SELECT *FROM manual_state").fetchone()),"account_row":dict(store.db.execute("SELECT *FROM manual_account").fetchone())}
    d=NS(store=store,state=lane,config=config,current=lambda:json.loads(store.db.execute("SELECT payload FROM manual_state").fetchone()[0]))
    # Only proof/terminal lookup and external connectivity mocked; real caps,
    # scoped allocation, both ledger writes and local CAS admission execute.
    monkeypatch.setattr(q,"configuration",lambda accounts,run:x.scope if run==q.RUN else None)
    monkeypatch.setattr(q,"terminal_ids",lambda *args:[])
    monkeypatch.setattr("orchestrator.connectivity.require",lambda *args,**kw:{"synthetic":True})
    yield NS(x=x,b=b,d=d,approval="c"*64,work=work)
    store.db.close()

def test_recovery_preserves_calls_account_and_failed_science(failed):
    f=failed;before=list(f.x.accounts.db.iterdump())
    result=r.recover(f.d,f.b,f.approval)
    assert result=={"status":"READY_REVIEW2","model_calls":0,"preserved_calls":2,"new_allowance":0}
    assert list(f.x.accounts.db.iterdump())==before
    assert f.d.current()["notebook_revision_result"]["synthetic_status"]=="FAIL"
    assert f.d.current()["rounds"]=={"run_spec_author":1,"run_spec_review":1}
    assert [dict(a)for a in f.d.store.db.execute("SELECT *FROM manual_calls")]==f.b["local_rows"]
    assert dict(f.d.store.db.execute("SELECT *FROM manual_account").fetchone())==f.b["account_row"]
    with pytest.raises(ValueError):r.recover(f.d,f.b,f.approval)

@pytest.mark.parametrize("bad",["local","global","owner","state","account","config","console","accepted","review","author","notebook","halt","live","nextwork"])
def test_drift_and_genuine_verdict_refuse_without_state_mutation(failed,bad):
    f=failed;db=f.d.store.db;g=f.x.accounts.db
    if bad=="local":db.execute("UPDATE manual_calls SET receipt='changed' WHERE id=?",(r.CALL,))
    elif bad=="global":g.execute("UPDATE autonomy_calls SET receipt='changed' WHERE id=?",(r.CALL,))
    elif bad=="owner":g.execute("UPDATE autonomy_runs SET status='STOPPED' WHERE id=?",(r.RUN,))
    elif bad=="state":db.execute("UPDATE manual_state SET payload='{}'")
    elif bad=="account":db.execute("UPDATE manual_account SET version=version+1")
    elif bad=="config":pr.atomic(f.d.state/"lane.json",{})
    elif bad=="console":pr.write_text(f.work/"console.log","changed")
    elif bad in {"accepted","review"}:pr.write_text(f.work/(".review-submission.json"if bad=="accepted"else"review.json"),'{"verdict":"REVISE"}')
    elif bad=="author":pr.write_text(Path(f.d.config["workspace_root"])/"run_spec_author-1/SPEC.proposed.md","changed")
    elif bad=="notebook":pr.write_text(f.d.state/"revised/revised.ipynb","changed")
    elif bad=="halt":pr.write_text(f.d.state/"HALT","stop")
    elif bad=="live":g.execute("INSERT INTO autonomy_calls VALUES('live','scientific','other',1,'2026-10-12','RUNNING','{}',NULL)")
    else:pr.mkdir(Path(f.d.config["workspace_root"])/"run_spec_review-2")
    before=list(db.iterdump());other=list(g.iterdump())
    with pytest.raises(ValueError):r.recover(f.d,f.b,f.approval)
    assert list(db.iterdump())==before and list(g.iterdump())==other
    assert not(f.d.state/r.EVENT).exists()

def test_normal_retry_admission_counts_both_ledgers_and_command(failed,monkeypatch):
    f=failed;r.recover(f.d,f.b,f.approval);store=f.d.store
    argv=["claude","--max-turns","30","--permission-mode","default","--tools","Read"]
    monkeypatch.setattr(manual_stage,"reviewer_command",lambda *args:list(argv))
    undo=r.bind_command(f.d,f.b,f.approval)
    try:
        work=Path(f.d.config["workspace_root"])/"run_spec_review-2"
        ident,n,receipt=store.reserve_call(r.RUN,r.STAGE,f.d.config["source"],f.d.config["branch"],f.d.config["policy"],{"stage":r.STAGE,"workspace":str(work)})
        assert (ident,n)==(r.NEXT,2)
        assert receipt["batch_accounting"]["batch_limit"]==128 and receipt["batch_accounting"]["run_limit"]==20
        state=f.d.current();state.update(phase="MODEL_RUNNING",pending={"id":ident,"stage":r.STAGE,"round":2,"workspace":str(work)})
        store.db.execute("UPDATE manual_state SET payload=?",(json.dumps(state),))
        assert manual_stage.reviewer_command(work,r.STAGE)==["claude","--max-turns","60",*argv[3:]]
        with pytest.raises(ValueError):store.reserve_call(r.RUN,r.STAGE,f.d.config["source"],f.d.config["branch"],f.d.config["policy"],{"stage":r.STAGE})
        assert store.db.execute("SELECT count(*)FROM manual_calls").fetchone()[0]==3
        assert dict(store.db.execute("SELECT *FROM manual_calls WHERE id=?",(r.CALL,)).fetchone())==f.b["local_rows"][-1]
        assert manual_stage.reviewer_command(work,"result_interpretation_review")==argv
    finally:undo()

@pytest.mark.parametrize("bad",["work","stage","command","grant","reserved"])
def test_probe_refuses_unqualified_command(failed,monkeypatch,bad):
    f=failed;r.recover(f.d,f.b,f.approval)
    argv=["claude","--max-turns","60"if bad=="command"else"30"]
    monkeypatch.setattr(manual_stage,"reviewer_command",lambda *args:list(argv))
    if bad=="grant":f.d.store.db.execute("DELETE FROM events WHERE id=?",(r.EVENT,))
    if bad=="reserved":f.x.accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,'scientific',?,3,'2026-10-12','RUNNING','{}',NULL)",(r.NEXT,r.RUN))
    undo=r.bind_command(f.d,f.b,f.approval,probe=True)
    try:
        work=f.d.state/(r.EVENT+"-qualification")/("wrong"if bad=="work"else"reviewer")
        if bad=="stage":
            assert manual_stage.reviewer_command(work,"other")==argv
        else:
            with pytest.raises(ValueError):manual_stage.reviewer_command(work,r.STAGE)
    finally:undo()

def test_future_review_budget_allows_new_scientific_revision_but_not_unadmitted_call(failed,monkeypatch):
    f=failed;r.recover(f.d,f.b,f.approval)
    monkeypatch.setattr(manual_stage,"reviewer_command",lambda *args:["claude","--max-turns","30"])
    state=f.d.current();state["notebook_revision_result"]={"synthetic_status":"PASS","next":"authored revision"}
    work=Path(f.d.config["workspace_root"])/"run_spec_review-3";ident=r.sha((r.RUN+":"+r.STAGE+":3").encode())
    state.update(phase="MODEL_RUNNING",pending={"id":ident,"stage":r.STAGE,"round":3,"workspace":str(work)})
    f.d.store.db.execute("UPDATE manual_state SET payload=?",(json.dumps(state),))
    undo=r.bind_command(f.d,f.b,f.approval)
    try:
        with pytest.raises(ValueError,match="ADMISSION_REQUIRED"):manual_stage.reviewer_command(work,r.STAGE)
        f.d.store.db.execute("INSERT INTO manual_calls VALUES(?,?,3,'RUNNING','{}')",(ident,r.STAGE))
        f.x.accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,'scientific',?,4,'2026-10-12','RUNNING','{}',NULL)",(ident,r.RUN))
        assert manual_stage.reviewer_command(work,r.STAGE)==["claude","--max-turns","60"]
    finally:undo()

def test_runtime_changes_only_entry_directive(monkeypatch,tmp_path):
    from tools import pnorm_v2_review_runtime as rt
    from orchestrator import manual_host_guard
    unit=("User=partho\nProtectSystem=strict\nNoNewPrivileges=yes\nExecStart=/usr/bin/python3 -s -B "+str(rt.PRIOR/"tools/colab_pnorm_v2_import_runtime.py")+" run\n").replace("\n","\n".encode().decode("unicode_escape")).encode()
    p=tmp_path/"unit";p.write_bytes(unit)
    monkeypatch.setattr(manual_host_guard,"trusted",lambda path:p)
    parent=NS(UNIT="old.service",ENTRY="tools/colab_pnorm_v2_import_runtime.py",authority=lambda:None)
    assert rt.unit_bytes(parent).replace(str(rt.ROOT/rt.ENTRY).encode(),str(rt.PRIOR/parent.ENTRY).encode())==unit

def test_actual_scope_is_exact_and_has_no_new_allowance():
    b=r.document(Path(__file__).resolve().parents[1])
    assert (b["preserved_calls"],b["run_limit"],b["batch_limit"],b["new_allowance"])==(2,20,128,0)
    assert b["native_final"]["subtype"]=="error_max_turns" and b["native_final"]["num_turns"]==30
