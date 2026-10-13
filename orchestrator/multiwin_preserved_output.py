"""Preserve one completed author's bytes and failed receipt; normal review remains required."""
from pathlib import Path
import copy,hashlib,json
RUN="colab-1ad5fafc220b3d65f576ce08"
CALL="b1dad7a10b0830b2cd2b569032792dcae04e4b16224f410a0df2a2c0e6a3c686"
DOC="docs/MULTIWIN_OUTPUT_BOUNDARY_PRIVATE.json"
PIN="3227009e4f969a5868be6debe005def1ffaf9cae5589d6aacad611e1f6b3e499"
EVENT="multiwin-author13-preserved-output-20261013"
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encoded=lambda v:json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def require(ok,why):
    if not ok:raise ValueError("MULTIWIN_OUTPUT_"+why)
def document(root):
    raw=(Path(root)/DOC).read_bytes();require(sha(raw)==PIN,"BINDING_CHANGED")
    b=json.loads(raw)
    require(b["run"]==RUN and b["call"]==CALL and b["output_limit"]==96000
        and b["exact_output_bytes"]==84502 and b["prior_model_limit"]==80000
        and b["new_author_calls"]==0 and b["next_review_attempt"]==12
        and b["scientific_acceptance"]is False and len(b["local_rows"])==25,"FIXED_SCOPE")
    return b
def native(b,read_file):
    bodies={}
    for name,pin in b["files"].items():
        require(Path(name).name==name,"FILE_NAME")
        raw=read_file(Path(b["workspace"])/name)
        require(len(raw)==pin["bytes"]and sha(raw)==pin["sha256"],"NATIVE_BYTES_CHANGED");bodies[name]=raw
    p=[json.loads(l)for l in bodies["stage_provenance.jsonl"].splitlines()if l.strip()]
    require(len(p)==1,"ONE_CALL");p=p[0]
    require(p["stage"]=="run_spec_author"and p["family_effective"]=="codex"and
        p["exit_class"]=="ok"and p["fallback"]is False and
        p["attempts"]==[{"model":"gpt-6-astra","returncode":0}],"NATIVE_COMPLETION")
    input_pin=sha(bodies["prompt.md"])
    require(input_pin==p["prompt_sha256"]==json.loads(bodies["sent-input.json"])["input_sha256"]
        ==json.loads(b["global_row"]["binding"])["input"]["input_sha256"],"INPUT_BINDING")
    require(json.loads(bodies["isolation-live.json"])["status"]=="ISOLATED","ISOLATION")
    for ref in json.loads(bodies["input-measurement.json"])["workspace_files"]:
        require(sha(read_file(Path(b["workspace"])/ref["path"]))==ref["sha256"],"BOUND_INPUT_CHANGED")
    events=[json.loads(l)for l in bodies["console.log"].splitlines()if l.strip()]
    require(events[-1].get("type")=="turn.completed"and
        sum(e.get("type")=="turn.completed"for e in events)==1 and
        not any(e.get("type")in {"turn.failed","error"}for e in events),"TERMINAL_STREAM")
    writes=[e["item"]for e in events if e.get("type")=="item.completed"
        and e.get("item",{}).get("id")=="item_18"]
    require(len(writes)==1 and writes[0]["type"]=="command_execution"and
        writes[0]["status"]=="completed"and writes[0]["exit_code"]==0,"AUTHOR_HASH_EVENT")
    for name in ("SPEC.proposed.md","notebook.patch.json"):
        line=name+" characters "+str(len(bodies[name].decode()))+" sha256 "+sha(bodies[name])
        require(writes[0]["aggregated_output"].splitlines().count(line)==1,"AUTHOR_OUTPUT_HASH")
    require(len(bodies["notebook.patch.json"])==84502 and
        b["prior_model_limit"]<84502<=b["output_limit"],"EXACT_OUTPUT_BOUNDARY")
    return {"call":CALL,"input_sha256":input_pin,"native_exit":"ok",
        "original_status":"UNCERTAIN","output_sha256":{n:sha(bodies[n])for n in
        ("SPEC.proposed.md","notebook.patch.json")},"new_calls":0,"scientific_acceptance":False}
def check(driver,b,initial=False):
    from orchestrator import private_records as pr
    require(driver.config["run_id"]==RUN and str(driver.state)==b["lane"]
        and sha(pr.check(driver.state/"lane.json").read_bytes())==b["config_sha256"],"LANE")
    for old in b["local_rows"]:
        row=driver.store.db.execute("SELECT * FROM manual_calls WHERE id=?",(old["id"],)).fetchone()
        require(row is not None and dict(row)==old,"LOCAL_HISTORY")
    row=driver.store.batch.db.execute("SELECT * FROM autonomy_calls WHERE id=?",(CALL,)).fetchone()
    require(row is not None and dict(row)==b["global_row"]and row["status"]=="UNCERTAIN","GLOBAL_HISTORY")
    require(dict(driver.store.batch.db.execute("SELECT * FROM autonomy_runs WHERE id=?",(RUN,)).fetchone())==b["owner"],"OWNER")
    if initial:
        require(dict(driver.store.db.execute("SELECT * FROM manual_state").fetchone())==b["state_row"]
            and dict(driver.store.db.execute("SELECT * FROM manual_account").fetchone())==b["account_row"],"EXACT_STATE")
        require(driver.store.db.execute("SELECT count(*)FROM manual_calls").fetchone()[0]==25,"CALL_COUNT")
        require(not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),"LIVE_CALL")
    return native(b,lambda p:pr.check(p).read_bytes())
def grant(driver,b,review):
    from orchestrator import private_records as pr
    proof=check(driver,b)
    folder=driver.state/EVENT
    q=json.loads(pr.check(folder/"qualification.json").read_bytes())
    done=json.loads(pr.check(folder/"COMPLETE.json").read_bytes())
    require(q=={"scope_sha256":PIN,"review_sha256":review,"evidence":proof}
        and done["qualification_sha256"]==sha(encoded(q))and done["review_sha256"]==review,"QUALIFIED_RECOVERY")
    return proof
def apply(driver,b,review):
    from orchestrator import private_records as pr,notebook_revision as nr,scientific_intake as intake
    from orchestrator import colab_preparation_scope as scope,colab_notebook_delivery as delivery
    from orchestrator.git_publication import scan
    proof=check(driver,b,True);value=driver.current();pending=value["pending"]
    require(value["phase"]=="BLOCKED"and value["reason"]=="MODEL_FAILED_OR_UNCERTAIN_NO_RETRY"
        and pending=={"id":CALL,"stage":"run_spec_author","round":13,"workspace":b["workspace"]}
        and value["rounds"]["run_spec_author"]==12 and value["rounds"]["run_spec_review"]==11,"EXACT_BLOCK")
    folder=driver.state/EVENT;require(not folder.exists()and not folder.is_symlink(),"ALREADY_ATTEMPTED")
    raw=pr.check(Path(b["workspace"])/"SPEC.proposed.md").read_bytes();text=raw.decode()
    scan("context/SPEC.proposed.md",raw)
    require(len(text)<=12000 and all(text.splitlines().count(line)==1 for line in
        ["run_id: "+RUN,"analysis_registry_sha256: "+driver.config["private_intake"]["sha256"]]),"SPEC")
    registry=json.loads(nr.bound(driver.context,driver.config["private_intake"]))
    cases=intake.cohort((driver.context/registry["cohort"]).read_bytes())
    patch=pr.check(Path(b["workspace"])/"notebook.patch.json").read_bytes();nr.scan(patch,cases)
    pr.mkdir(folder);q={"scope_sha256":PIN,"review_sha256":review,"evidence":proof}
    pr.write_bytes(folder/"qualification.json",encoded(q))
    pr.write_bytes(folder/"ORIGINAL_ROWS.json",encoded(b))
    # Only these exact author-emitted bytes receive the already supported96KB parser bound.
    original_apply=nr.apply
    def bound_apply(original,selection,raw,cases,**kwargs):
        require(raw==patch and sha(raw)==b["files"]["notebook.patch.json"]["sha256"]
            and "patch_limit"not in kwargs,"EXACT_PATCH_ONLY")
        return original_apply(original,selection,raw,cases,patch_limit=96000,**kwargs)
    after=copy.deepcopy(value);nr.apply=bound_apply
    try:scope.prepare_notebook_artifacts(driver,after,pending,cases)
    finally:nr.apply=original_apply
    delivery.prepare_variants(driver,after,pending,cases)
    require(after["notebook_revision_result"]["synthetic_status"]=="PASS","SYNTHETIC_PASS_REQUIRED")
    for kind in ("run_spec","proposed_run_spec"):
        driver.artifact(after,kind,"ANALYSIS-SPEC-13.md",raw,13)
    after["rounds"]["run_spec_author"]=13
    after.update(phase="run_spec_review",reason=None,spec=str(Path(b["workspace"])/"SPEC.proposed.md"))
    after.pop("pending");after.pop("blocked_stage",None)
    after["interventions"].append({"kind":EVENT,"scope_sha256":PIN,"review_sha256":review,
        "qualification_sha256":sha(encoded(q)),"original_call_status":"UNCERTAIN",
        "new_calls":0,"scientific_acceptance":False})
    check(driver,b,True);db=driver.store.db;db.execute("BEGIN IMMEDIATE")
    try:
        check(driver,b,True)
        db.execute("UPDATE manual_state SET payload=? WHERE id=1",(json.dumps(after,sort_keys=True),))
        db.execute("INSERT INTO events VALUES(?,?,?)",(EVENT,RUN,encoded(q).decode()))
        db.commit()
    except BaseException:db.rollback();raise
    require(driver.current()==after,"STATE_READBACK")
    check(driver,b)
    done={"status":"READY_FOR_NORMAL_SCIENTIFIC_REVIEW","qualification_sha256":sha(encoded(q)),
        "review_sha256":review,"model_calls":0,"original_calls_preserved":25}
    pr.write_bytes(folder/"COMPLETE.json",encoded(done));return done
def bind(driver,b,review):
    from orchestrator import colab_simple_full as full
    previous_terminal,previous_local,previous_qualifier=full.terminal_ids,full.local_terminal_ids,full._TERMINAL_QUALIFIER
    def qualifier(accounts,row):
        if row["id"]!=CALL:return previous_qualifier(accounts,row)
        require(accounts is driver.store.batch and dict(row)==b["global_row"],"EXACT_GLOBAL_CONNECTION")
        grant(driver,b,review)
        return {"id":CALL,"proof_sha256":PIN,"classification":"PRESERVED_COMPLETED_OUTPUT_SIZE_REFUSAL"}
    def terminals(accounts,scope):
        if scope.get("run_id")!=RUN:return previous_terminal(accounts,scope)
        require(accounts is driver.store.batch,"GLOBAL_CONNECTION");grant(driver,b,review)
        value=copy.deepcopy(scope)
        require(not any(r["id"]==CALL for r in value["uncertain_rows"]),"NO_DUPLICATE_TERMINAL")
        value["uncertain_rows"]=sorted([*value["uncertain_rows"],b["global_row"]],key=lambda r:r["id"])
        return previous_terminal(accounts,value)
    def local(store,run):
        if run!=RUN:return previous_local(store,run)
        require(store is driver.store,"LOCAL_CONNECTION");grant(driver,b,review)
        allowed=set(terminals(store.batch,full.validate(store,run)))
        originals={r["id"]:r for r in b["local_rows"]}
        rows=[dict(r)for r in store.db.execute("SELECT * FROM manual_calls WHERE status IN ('RUNNING','UNCERTAIN')")]
        require(all(r["status"]=="UNCERTAIN"and originals.get(r["id"])==r and r["id"]in allowed for r in rows),"UNKNOWN_LOCAL_CALL")
        return [r["id"]for r in rows]
    full._TERMINAL_QUALIFIER=qualifier;full.terminal_ids=terminals;full.local_terminal_ids=local
    def restore():
        full.terminal_ids,full.local_terminal_ids,full._TERMINAL_QUALIFIER=previous_terminal,previous_local,previous_qualifier
    return restore

def administrative(db,b,read_file,verify_old,stopped,change):
    """Standing one-use administrative repair review; no scientific admission."""
    require(change=="multiwin-output-boundary-20261013"and db.in_transaction,"ADMIN_SCOPE")
    require(not db.execute("SELECT 1 FROM autonomy_calls WHERE change_id=?",(change,)).fetchone(),"ONE_ADMIN_ONLY")
    rows=[dict(r)for r in db.execute("SELECT * FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')")]
    require(all(r["status"]=="UNCERTAIN"for r in rows),"LIVE_ADMIN_BLOCK")
    require(sum(r["id"]==CALL for r in rows)==1,"EXACT_ADMIN_FAILURE")
    result=[]
    for row in rows:
        if row["id"]!=CALL:
            result.append(verify_old(row));continue
        require(row==b["global_row"],"ADMIN_ROW_CHANGED")
        require(stopped(b["unit"]),"AUTHOR_NOT_STOPPED")
        evidence=native(b,read_file)
        result.append({"id":CALL,"classification":"STANDING_ONE_ADMIN_COMPLETED_OUTPUT_REPAIR",
            "proof_sha256":sha(encoded({"scope_sha256":PIN,"native":evidence}))})
    return result
