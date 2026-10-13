"""Recover one terminal review; retain all calls and bound this question to60 tool turns."""
from pathlib import Path
import hashlib,json
RUN="colab-arm-b9d64a3c09b799bc10b0eba7"
CALL="170d554f16e1cfec8aadfa0a768e52115d0fc956651835be5e3c91e435c70468"
NEXT=hashlib.sha256((RUN+":run_spec_review:2").encode()).hexdigest()
STAGE="run_spec_review"
EVENT="pnorm-v2-review-turns-20261012"
DOCUMENT="docs/PNORM_V2_REVIEW_TURNS_PRIVATE.json"
PIN="24ad8ad99ced85f83ae88a21d78e14d9b7ab95e6fc01e09793297821faee8555"
REASON="REVIEW_SUBMISSION_FAILED_NO_RETRY: ACCEPTED_SUBMISSION_REQUIRED"
def require(ok,why):
    if not ok:raise ValueError("PNORM_V2_REVIEW_TURNS_"+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":")).encode()
def document(root):
    from orchestrator import private_records as pr
    raw=pr.check(Path(root)/DOCUMENT).read_bytes();require(sha(raw)==PIN,"SCOPE_PIN")
    b=json.loads(raw)
    require(b["run_id"]==RUN and (b["preserved_calls"],b["next_review"],b["max_turns"],
        b["run_limit"],b["batch_limit"],b["new_allowance"])==(2,2,60,20,128,0),"SCOPE")
    return b
def originals(d,b):
    from orchestrator import private_records as pr,review_submission as rs
    require(d.config==b["config"]and d.config["run_id"]==RUN
        and Path(d.store.path)==Path(b["lane"])/"jobs.sqlite","CONFIG")
    require(sha(pr.check(d.state/"lane.json").read_bytes())==b["configuration_sha256"],"CONFIG_BYTES")
    for db,table,key in[(d.store.db,"manual_calls","local_rows"),(d.store.batch.db,"autonomy_calls","global_rows")]:
        expected=b[key];require(len(expected)==2 and len({r["id"]for r in expected})==2,"ORIGINAL_SET")
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
    require(work==Path(d.config["workspace_root"])/"run_spec_review-1","FAILED_WORKSPACE")
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
    author=next(r for r in b["local_rows"]if r["stage"]=="run_spec_author"and r["attempt"]==1)
    receipt=json.loads(author["receipt"]);work=Path(receipt["workspace"])
    for name,pin in receipt["output_sha256"].items():
        require(Path(name).name==name and sha(pr.check(work/name).read_bytes())==pin,"AUTHOR_OUTPUT_CHANGED")
    revised=scientific["notebook_revision_result"];folder=Path(revised["folder"])
    require(sha(pr.check(folder/"revised.ipynb").read_bytes())==revised["notebook_sha256"]
        and sha(pr.check(folder/"notebook.diff").read_bytes())==revised["diff_sha256"],"REVISED_NOTEBOOK_CHANGED")
def record(b,approval):
    require(isinstance(approval,str)and len(approval)==64 and all(c in "0123456789abcdef"for c in approval),"APPROVAL")
    return{"kind":EVENT,"scope_sha256":PIN,"review_sha256":approval,"failed_call":CALL,
        "next_review":2,"max_turns":60,"preserved_calls":2,"run_limit":20,"new_allowance":0}
def next_state(b,approval):
    v=json.loads(b["state_row"]["payload"])
    require(v["phase"]=="BLOCKED"and v["reason"]==REASON and
        v["rounds"]=={"run_spec_author":1}
        and v["pending"]=={"id":CALL,"stage":STAGE,"round":1,"workspace":b["failed_workspace"]},"EXACT_STATE")
    out=json.loads(json.dumps(v));out.pop("pending")
    out["rounds"][STAGE]=1
    out.update(phase=STAGE,reason="REVIEWED_NATIVE_TURN_RECOVERY",linked_recovery_of=CALL)
    out["interventions"].append(record(b,approval));return out
def granted(d,b,approval):
    from orchestrator import private_records as pr
    originals(d,b);expected=record(b,approval)
    row=d.store.db.execute("SELECT payload FROM events WHERE id=?",(EVENT,)).fetchone()
    require(row is not None and json.loads(row[0])==expected
        and json.loads(pr.check(d.state/EVENT/"COMPLETE.json").read_bytes())==expected,"RECOVERY_COMPLETE")
    return expected
def recover(d,b,approval):
    from orchestrator import private_records as pr
    require(not(d.state/"HALT").exists()and not(d.store.batch.folder/"HALT").exists(),"HALT")
    originals(d,b);before=b["state_row"];db=d.store.db
    require(dict(db.execute("SELECT * FROM manual_state WHERE id=1").fetchone())==before,"STATE_MOVED")
    require(dict(db.execute("SELECT * FROM manual_account WHERE id=1").fetchone())==b["account_row"],"ACCOUNT_MOVED")
    require(db.execute("SELECT count(*) FROM manual_calls").fetchone()[0]==2
        and d.store.batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'AND change_id=?",(RUN,)).fetchone()[0]==2,"CALL_SET")
    require(not d.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),"LIVE_MODEL")
    require(not(Path(d.config["workspace_root"])/"run_spec_review-2").exists(),"NEXT_WORKSPACE_EXISTS")
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
    return{"status":"READY_REVIEW2","model_calls":0,"preserved_calls":2,"new_allowance":0}
def bind_command(d,b,approval,probe=False):
    """Only tool-turn budget changes; this question's normal admission remains."""
    from orchestrator import manual_stage
    previous=manual_stage.reviewer_command
    def command(work,stage):
        if stage!=STAGE:return previous(work,stage)
        require(d.config["run_id"]==RUN,"COMMAND_RUN")
        granted(d,b,approval)
        value=d.current()
        if probe:
            expected=d.state/(EVENT+"-qualification")/"reviewer"
            require(value==next_state(b,approval) and Path(work)==expected,"PROBE_STATE")
            require(not d.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE id=?",(NEXT,)).fetchone(),"PROBE_RESERVED")
        else:
            pending=value.get("pending")or {}
            n=pending.get("round")
            require(type(n)is int and 2<=n<=4 and value["phase"]=="MODEL_RUNNING"
                and pending.get("stage")==STAGE,"ACTIVE_REVIEW")
            ident=sha((RUN+":"+STAGE+":"+str(n)).encode())
            expected=Path(d.config["workspace_root"])/("run_spec_review-"+str(n))
            require(pending=={"id":ident,"stage":STAGE,"round":n,"workspace":str(expected)}
                and Path(work)==expected,"EXACT_WORKSPACE")
            for db,table in[(d.store.db,"manual_calls"),(d.store.batch.db,"autonomy_calls")]:
                row=db.execute("SELECT status FROM "+table+" WHERE id=?",(ident,)).fetchone()
                require(row is not None and row[0]=="RUNNING","ADMISSION_REQUIRED")
        argv=previous(work,stage)
        require(argv.count("--max-turns")==1 and argv[argv.index("--max-turns")+1]=="30","EXACT_OLD_COMMAND")
        result=list(argv);result[result.index("--max-turns")+1]="60";return result
    manual_stage.reviewer_command=command
    def restore():manual_stage.reviewer_command=previous
    return restore
