"""Bounded recovery of a pre-reservation JSON serialization refusal."""
from pathlib import Path
import hashlib,json,os
RUN="diagnostics-b203ee1ce27e909d9d78d44a"
EVENT="item6-smoothing-serialization-20261012"
DOCUMENT="docs/IDEA2_SERIALIZATION_PRIVATE.json"
PIN="91a96ac1caf8e02c70bc1ecbd2a5e7053be4b02998f6b4e4ceae9223b692d36e"
REASON="ValueError: IDEA2_INTERPRETATION_ALLOCATION_HISTORY_CHANGED"
STAGE="result_interpretation_author"
sha=lambda raw:hashlib.sha256(raw).hexdigest()
canonical=lambda value:json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def require(ok,why):
    if not ok:raise ValueError("IDEA2_SERIALIZATION_"+why)
def document(root):
    from orchestrator import private_records as pr
    raw=pr.check(Path(root)/DOCUMENT).read_bytes();require(sha(raw)==PIN,"SCOPE_PIN")
    b=json.loads(raw)
    require(b["config"]["run_id"]==RUN and len(b["local_calls"])==len(b["global_calls"])==15,"SCOPE")
    require(b["next_call_id"]==sha((RUN+":"+STAGE+":3").encode()),"NEXT_ID")
    return b
def originals(d,b):
    from orchestrator import private_records as pr
    require(d.config==b["config"]and Path(d.store.path)==Path(b["lane"])/"jobs.sqlite","CONFIG")
    require(sha(pr.check(d.state/"lane.json").read_bytes())==b["config_sha256"],"CONFIG_BYTES")
    for db,table,key in [(d.store.db,"manual_calls","local_calls"),(d.store.batch.db,"autonomy_calls","global_calls")]:
        for old in b[key]:
            row=db.execute("SELECT *FROM "+table+" WHERE id=?",(old["id"],)).fetchone()
            require(row is not None and dict(row)==old,"ORIGINAL_CALL_CHANGED")
    owner=d.store.batch.db.execute("SELECT *FROM autonomy_runs WHERE id=?",(RUN,)).fetchone()
    require(owner is not None and dict(owner)==b["owner"]and owner["status"]=="ACTIVE","OWNER")
    grant=d.store.batch.db.execute("SELECT *FROM events WHERE id=?",(b["grant"]["id"],)).fetchone()
    require(grant is not None and dict(grant)==b["grant"],"ORIGINAL_GRANT")
def record(b,approval):
    require(isinstance(approval,str)and len(approval)==64 and all(c in "0123456789abcdef"for c in approval),"APPROVAL")
    return {"kind":EVENT,"scope_sha256":PIN,"review_sha256":approval,"prior_calls":15,
        "new_allowance":0,"next_call_id":b["next_call_id"],"preserved_workspace":b["workspace"]}
def next_state(b,approval):
    v=json.loads(b["state_row"]["payload"])
    require(v["phase"]=="BLOCKED"and v["reason"]==REASON and v["blocked_stage"]==STAGE
        and v["rounds"]=={"result_interpretation_author":2,"result_interpretation_review":2,
                            "run_spec_author":6,"run_spec_review":5}and"pending"not in v,"EXACT_REFUSAL")
    v.update(phase=STAGE,reason="REVIEWED_SERIALIZATION_RECOVERY")
    v.pop("blocked_stage");v.pop("blocker_categories",None)
    v["interventions"].append(record(b,approval));return v
def workspace(folder,b):
    from orchestrator import private_records as pr
    require(folder.is_dir()and not folder.is_symlink(),"WORKSPACE")
    pr.check_tree(folder)
    actual={str(p.relative_to(folder)):{"sha256":sha(pr.check(p).read_bytes()),"bytes":p.stat().st_size}
            for p in folder.rglob("*")if p.is_file()}
    require(actual==b["workspace_files"],"PREMODEL_FILES_CHANGED")
    require(not any(Path(n).name in {"console.log","transport.log","sent-input.json","process.json",
        "interpretation.md","REPORT.md",".review-submission.json"}for n in actual),"CLIENT_EVIDENCE_EXISTS")
def granted(d,b,approval):
    from orchestrator import private_records as pr
    originals(d,b);expected=record(b,approval)
    row=d.store.db.execute("SELECT payload FROM events WHERE id=?",(EVENT,)).fetchone()
    require(row is not None and json.loads(row[0])==expected
        and json.loads(pr.check(d.state/EVENT/"COMPLETE.json").read_bytes())==expected,"RECOVERY_COMPLETE")
    workspace(d.state/EVENT/"original-workspace",b)
    return expected
def recover(d,b,approval):
    from orchestrator import private_records as pr
    originals(d,b)
    require(not(d.state/"HALT").exists()and not(d.store.batch.folder/"HALT").exists(),"HALT")
    require(dict(d.store.db.execute("SELECT *FROM manual_state WHERE id=1").fetchone())==b["state_row"],"STATE_MOVED")
    require(dict(d.store.db.execute("SELECT *FROM manual_account WHERE id=1").fetchone())==b["account_row"],"ACCOUNT_MOVED")
    require(d.store.db.execute("SELECT count(*)FROM manual_calls").fetchone()[0]==15
        and d.store.batch.db.execute("SELECT count(*)FROM autonomy_calls WHERE change_id=?",(RUN,)).fetchone()[0]==15,"CALL_SET")
    require(not d.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),"LIVE_MODEL")
    require(not d.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE id=?",(b["next_call_id"],)).fetchone(),"ALREADY_RESERVED")
    work=Path(b["workspace"]);require(work==Path(d.config["workspace_root"])/(STAGE+"-3"),"EXACT_WORKSPACE")
    workspace(work,b);folder=d.state/EVENT;require(not folder.exists()and not folder.is_symlink(),"ALREADY_ATTEMPTED")
    expected=record(b,approval);after=next_state(b,approval)
    pr.mkdir(folder);pr.write_bytes(folder/"INTENT.json",canonical(expected))
    pr.write_bytes(folder/"original-state.json",b["state_row"]["payload"].encode())
    # Same owner and filesystem; no deletion. An interrupted recovery is held.
    os.rename(work,folder/"original-workspace")
    db=d.store.db;db.execute("BEGIN IMMEDIATE")
    try:
        originals(d,b)
        require(dict(db.execute("SELECT *FROM manual_state WHERE id=1").fetchone())==b["state_row"],"STATE_RACE")
        require(dict(db.execute("SELECT *FROM manual_account WHERE id=1").fetchone())==b["account_row"],"ACCOUNT_RACE")
        db.execute("INSERT INTO events VALUES(?,?,?)",(EVENT,RUN,canonical(expected).decode()))
        db.execute("UPDATE manual_state SET payload=?WHERE id=1",(json.dumps(after,sort_keys=True),));db.execute("COMMIT")
    except BaseException:db.execute("ROLLBACK");raise
    require(d.current()==after,"READBACK");pr.write_bytes(folder/"COMPLETE.json",canonical(expected))
    granted(d,b,approval)
    return {"status":"READY_SAME_UNRESERVED_AUTHOR3","model_calls":0,"prior_calls":15,"new_allowance":0}
def bind(d,b,approval,implementation,base):
    """Replace one reviewed function, preserving every other installed byte."""
    require(base.RUN==implementation.RUN==RUN and base.DOCUMENT_SHA==implementation.DOCUMENT_SHA
        and base.EVENT==implementation.EVENT,"SAME_SCOPE")
    original=base.batch_allowance
    def corrected(accounts,scope):
        require(accounts is d.store.batch and scope==base.document(),"EXACT_ACCOUNT_SCOPE")
        granted(d,b,approval)
        return implementation.batch_allowance(accounts,scope)
    base.batch_allowance=corrected
    def restore():base.batch_allowance=original
    return restore
