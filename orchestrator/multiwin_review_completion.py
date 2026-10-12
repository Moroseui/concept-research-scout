"""One terminal 30-turn review; use the already granted final reviewer slot."""
from pathlib import Path
import hashlib,json
RUN="colab-1ad5fafc220b3d65f576ce08"
CALL="1da84010d48239e6a5173d9b432e0f4501edcc8c7164a716b13f8d20c911d7af"
NEXT=hashlib.sha256((RUN+":run_spec_review:11").encode()).hexdigest()
STAGE="run_spec_review"
EVENT="multiwin-review11-20261012"
DOCUMENT="docs/MULTIWIN_REVIEW11_PRIVATE.json"
PIN="88fbbf5901400697dc64dd37cd9d268877b62b783a086e2afcc73f3aee0333c8"
REASON="REVIEW_SUBMISSION_FAILED_NO_RETRY: ACCEPTED_SUBMISSION_REQUIRED"
def require(ok,why):
    if not ok:raise ValueError("MULTIWIN_REVIEW11_"+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":")).encode()
def document(root):
    from orchestrator import private_records as pr
    raw=pr.check(Path(root)/DOCUMENT).read_bytes();require(sha(raw)==PIN,"SCOPE_PIN")
    b=json.loads(raw)
    require(b["run_id"]==RUN and (b["preserved_calls"],b["next_review"],b["max_turns"],
        b["run_limit"],b["batch_limit"],b["new_allowance"])==(23,11,60,24,128,0),"SCOPE")
    return b
def originals(d,b):
    from orchestrator import private_records as pr,review_submission as rs
    require(d.config==b["config"]and d.config["run_id"]==RUN
        and Path(d.store.path)==Path(b["lane"])/"jobs.sqlite","CONFIG")
    require(sha(pr.check(d.state/"lane.json").read_bytes())==b["configuration_sha256"],"CONFIG_BYTES")
    for db,table,key in[(d.store.db,"manual_calls","local_rows"),(d.store.batch.db,"autonomy_calls","global_rows")]:
        expected=b[key];require(len(expected)==23 and len({r["id"]for r in expected})==23,"ORIGINAL_SET")
        for old in expected:
            row=db.execute("SELECT * FROM "+table+" WHERE id=?",(old["id"],)).fetchone()
            require(row is not None and dict(row)==old,"ORIGINAL_CALL")
        failed=db.execute("SELECT status,receipt FROM "+table+" WHERE id=?",(CALL,)).fetchone()
        receipt=json.loads(failed["receipt"])
        require(failed["status"]=="FAILED"and receipt["error_type"]=="TerminalSubmissionFailure"
            and receipt["reason"]=="ACCEPTED_SUBMISSION_REQUIRED","MECHANICAL_FAILED")
    owner=d.store.batch.db.execute("SELECT * FROM autonomy_runs WHERE id=?",(RUN,)).fetchone()
    require(owner is not None and dict(owner)==b["owner"]and owner["status"]=="ACTIVE","OWNER")
    work=Path(b["failed_workspace"])
    require(work==Path(d.config["workspace_root"])/"run_spec_review-10","FAILED_WORKSPACE")
    for n,v in b["files"].items():
        require(Path(n).name==n,"FILE_NAME");raw=pr.check(work/n).read_bytes()
        require(len(raw)==v["bytes"]and sha(raw)==v["sha256"],"FAILED_BYTES")
    require(not(work/rs.RECORD).exists()and not(work/"review.json").exists(),"VERDICT_EXISTS")
    text=pr.check(work/"console.log").read_text();require(rs.terminal_without_submission(work,text),"TERMINAL")
    events=[]
    for line in text.splitlines():
        try:v=json.loads(line)
        except ValueError:continue
        if isinstance(v,dict):events.append(v)
    finals=[e for e in events if e.get("type")=="result"]
    require(len(finals)==1 and finals[0]==b["native_final"]and
        (finals[0].get("subtype"),finals[0].get("num_turns"))==("error_max_turns",30),"MAX_TURNS")
    require(not any(p.get("type")=="tool_use"and"submit_review"in p.get("name","")
        for e in events for p in e.get("message",{}).get("content",[])if isinstance(p,dict)),"SUBMISSION_ATTEMPT")
    scientific=json.loads(b["state_row"]["payload"])
    for ref in scientific["artifacts"]:
        path=Path(ref["path"])
        require(not path.is_absolute()and".."not in path.parts,"ARTIFACT_PATH")
        require(sha(pr.check(Path(d.config["context"])/path).read_bytes())==ref["sha256"],"AUTHOR_ARTIFACT_CHANGED")
    author=next(r for r in b["local_rows"]if r["stage"]=="run_spec_author"and r["attempt"]==12)
    receipt=json.loads(author["receipt"]);work=Path(receipt["workspace"])
    for name,pin in receipt["output_sha256"].items():
        require(Path(name).name==name and sha(pr.check(work/name).read_bytes())==pin,"AUTHOR_OUTPUT_CHANGED")
    revised=scientific["notebook_revision_result"];folder=Path(revised["folder"])
    require(sha(pr.check(folder/"revised.ipynb").read_bytes())==revised["notebook_sha256"]
        and sha(pr.check(folder/"notebook.diff").read_bytes())==revised["diff_sha256"],"REVISED_NOTEBOOK_CHANGED")
    delivery=scientific["colab_delivery"]
    require(sha(pr.check(Path(delivery["folder"])/"manifest.json").read_bytes())==delivery["manifest_sha256"],"DELIVERY_CHANGED")
def record(b,approval):
    require(isinstance(approval,str)and len(approval)==64 and all(c in "0123456789abcdef"for c in approval),"APPROVAL")
    return{"kind":EVENT,"scope_sha256":PIN,"review_sha256":approval,"failed_call":CALL,
        "next_review":11,"max_turns":60,"preserved_calls":23,"run_limit":24,"new_allowance":0}
def next_state(b,approval):
    v=json.loads(b["state_row"]["payload"])
    require(v["phase"]=="BLOCKED"and v["reason"]==REASON and
        v["rounds"]["run_spec_author"]==12 and v["rounds"]["run_spec_review"]==9
        and v["pending"]=={"id":CALL,"stage":STAGE,"round":10,"workspace":b["failed_workspace"]},"EXACT_STATE")
    out=json.loads(json.dumps(v));out.pop("pending")
    out["rounds"][STAGE]=10
    out.update(phase=STAGE,reason="REVIEWED_NATIVE_TURN_RECOVERY",linked_recovery_of=CALL)
    out["interventions"].append(record(b,approval));return out
def granted(d,b,approval):
    from orchestrator import private_records as pr
    originals(d,b);expected=record(b,approval)
    row=d.store.db.execute("SELECT payload FROM events WHERE id=?",(EVENT,)).fetchone()
    require(row is not None and json.loads(row[0])==expected
        and json.loads(pr.check(d.state/EVENT/"COMPLETE.json").read_bytes())==expected,"RECOVERY_COMPLETE")
    for key in("artifacts","spec","notebook_revision_result","colab_delivery"):
        # The review may append its own verdict artifact on completion, so only
        # the recovered state/active next call is checked here, before verdict.
        before=json.loads(b["state_row"]["payload"]).get(key)
        require(d.current().get(key)==before,"SCIENTIFIC_INPUT_CHANGED")
    return expected
def recover(d,b,approval):
    from orchestrator import private_records as pr
    require(not(d.state/"HALT").exists()and not(d.store.batch.folder/"HALT").exists(),"HALT")
    originals(d,b);before=b["state_row"];db=d.store.db
    require(dict(db.execute("SELECT * FROM manual_state WHERE id=1").fetchone())==before,"STATE_MOVED")
    require(dict(db.execute("SELECT * FROM manual_account WHERE id=1").fetchone())==b["account_row"],"ACCOUNT_MOVED")
    require(db.execute("SELECT count(*) FROM manual_calls").fetchone()[0]==23
        and d.store.batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'AND change_id=?",(RUN,)).fetchone()[0]==23,"CALL_SET")
    require(not d.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),"LIVE_MODEL")
    require(not(Path(d.config["workspace_root"])/"run_spec_review-11").exists(),"NEXT_WORKSPACE_EXISTS")
    folder=d.state/EVENT;require(not folder.exists()and not folder.is_symlink(),"ALREADY_ATTEMPTED")
    expected=record(b,approval);after=next_state(b,approval)
    pr.mkdir(folder);pr.write_bytes(folder/"INTENT.json",canonical(expected))
    pr.write_bytes(folder/"original-state.json",before["payload"].encode())
    db.execute("BEGIN IMMEDIATE")
    try:
        originals(d,b)
        require(dict(db.execute("SELECT * FROM manual_state WHERE id=1").fetchone())==before,"STATE_RACE")
        require(dict(db.execute("SELECT * FROM manual_account WHERE id=1").fetchone())==b["account_row"],"ACCOUNT_RACE")
        db.execute("INSERT INTO events VALUES(?,?,?)",(EVENT,RUN,canonical(expected).decode()))
        db.execute("UPDATE manual_state SET payload=?WHERE id=1",(json.dumps(after,sort_keys=True),));db.execute("COMMIT")
    except BaseException:db.execute("ROLLBACK");raise
    require(d.current()==after and dict(db.execute("SELECT * FROM manual_account WHERE id=1").fetchone())==b["account_row"],"READBACK");pr.write_bytes(folder/"COMPLETE.json",canonical(expected))
    granted(d,b,approval)
    return{"status":"READY_REVIEW11","model_calls":0,"preserved_calls":23,"maximum_remaining_calls":1}
def bind_command(d,b,approval,probe=False):
    from orchestrator import manual_stage
    previous=manual_stage.reviewer_command
    def command(work,stage):
        require(stage==STAGE,"STAGE")
        expected=d.state/(EVENT+"-qualification")/"reviewer"if probe else Path(d.config["workspace_root"])/"run_spec_review-11"
        require(Path(work)==expected,"EXACT_WORKSPACE")
        granted(d,b,approval)
        if probe:
            require(d.current()==next_state(b,approval),"PROBE_STATE")
            require(not d.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE id=?",(NEXT,)).fetchone(),"PROBE_RESERVED")
        else:
            value=d.current();require(value["phase"]=="MODEL_RUNNING"and value["pending"]=={
                "id":NEXT,"stage":STAGE,"round":11,"workspace":str(expected)},"ACTIVE_REVIEW11")
            for db,table in[(d.store.db,"manual_calls"),(d.store.batch.db,"autonomy_calls")]:
                row=db.execute("SELECT status FROM "+table+" WHERE id=?",(NEXT,)).fetchone()
                require(row is not None and row[0]=="RUNNING","ADMISSION_REQUIRED")
        argv=previous(work,stage)
        require(argv.count("--max-turns")==1 and argv[argv.index("--max-turns")+1]=="30","EXACT_OLD_COMMAND")
        result=list(argv);result[result.index("--max-turns")+1]="60";return result
    manual_stage.reviewer_command=command
    def restore():manual_stage.reviewer_command=previous
    return restore
