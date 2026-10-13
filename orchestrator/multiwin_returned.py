"""One provenance-only correction and review on the same owner; all24calls retained."""
from pathlib import Path
import hashlib,importlib.util,json
RUN="colab-1ad5fafc220b3d65f576ce08"
DOCUMENT="docs/MULTIWIN_RETURNED_PRIVATE.json"
DOCUMENT_SHA="4e455fa70f0e778f338f42b1c9af30435ada20a04b50efb79f8aa570d0a02362"
EVENT="multiwin-returned-provenance-20261013"
TASK="docs/MULTIWIN_RETURNED_TASK.md"
_PROBE_DB=None
sha=lambda raw:hashlib.sha256(raw).hexdigest()
canonical=lambda v:json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def require(ok,why):
    if not ok:raise ValueError("MULTIWIN_RETURNED_"+why)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def frozen(root):
    root=Path(root);raw=(root/DOCUMENT).read_bytes()
    require(sha(raw)==DOCUMENT_SHA,"SCOPE_CHANGED");b=json.loads(raw)
    require(b["run"]==RUN and b["maximum_new_calls"]==2 and b["run_limit"]==26
        and b["batch_limit"]==140 and b["execution_authorized"]is False,"LIMITS")
    require(len(b["local_calls_pins"])==len(b["global_calls_pins"])==24
        and len(b["scientific_calls_pins"])==128,"ORIGINAL_COUNTS")
    require(b["allowed_calls"]==[{"stage":"run_spec_author","attempt":13},
        {"stage":"run_spec_review","attempt":12}],"EXACT_CALLS")
    for name,pin in b["context_files"].items():
        path=root/name;require(not path.is_symlink()and sha(path.read_bytes())==pin,"CONTEXT_CHANGED")
    require(sha((root/"docs/OVERNIGHT_AUTONOMY_OPERATOR_DECISION_20261008.txt").read_bytes())==
        "a7fbba4b5c49426c099f1eb8d91e45489b454fc51a527f5df1566a60c1cabcb1","DELEGATION_CHANGED")
    return b
def check_originals(driver,b,initial=False):
    from orchestrator import private_records as pr
    require(driver.config==b["config"]and driver.config["run_id"]==RUN,"ORIGINAL_CONFIGURATION")
    for name,pin in b["files"].items():require(sha(pr.check(name).read_bytes())==pin,"ORIGINAL_FILE")
    for table,key,db in [("manual_calls","local_calls_pins",driver.store.db),
        ("autonomy_calls","global_calls_pins",driver.store.batch.db),
        ("autonomy_calls","scientific_calls_pins",driver.store.batch.db)]:
        for ident,pin in b[key].items():
            row=db.execute("SELECT * FROM "+table+" WHERE id=?",(ident,)).fetchone()
            require(row is not None and sha(canonical(dict(row)))==pin,"ORIGINAL_CALL")
    owner=driver.store.batch.db.execute("SELECT * FROM autonomy_runs WHERE id=?",(RUN,)).fetchone()
    require(owner is not None and dict(owner)==b["owner"],"OWNER_CHANGED")
    rows=[dict(r)for r in driver.store.db.execute("SELECT * FROM manual_calls ORDER BY rowid")]
    extra=[r for r in rows if r["id"]not in b["local_calls_pins"]]
    allowed={(r["stage"],r["attempt"])for r in b["allowed_calls"]}
    require(len(extra)<=2 and all((r["stage"],r["attempt"])in allowed and
        r["id"]==sha((RUN+":"+r["stage"]+":"+str(r["attempt"])).encode())for r in extra),"TWO_CALL_SCOPE")
    g=[dict(r)for r in driver.store.batch.db.execute("SELECT * FROM autonomy_calls WHERE change_id=?",(RUN,))]
    require(len(g)<=26 and all(r["id"]in b["global_calls_pins"]or
        r["id"]in {sha((RUN+":"+stage+":"+str(n)).encode())for stage,n in allowed}for r in g),"GLOBAL_SCOPE")
    if initial:
        require(not extra and len(g)==24,"ALREADY_CONTINUED")
        require(dict(driver.store.db.execute("SELECT * FROM manual_state WHERE id=1").fetchone())==b["state_row"],"STATE_CHANGED")
        require(dict(driver.store.db.execute("SELECT * FROM manual_account WHERE id=1").fetchone())==b["account_row"],"ACCOUNT_CHANGED")
        require(not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),"LIVE_CALL")
def genuine_review(driver,b):
    from orchestrator import private_records as pr,review_submission as rs
    work=driver.state.parent/"lane-scientific-workspaces/run_spec_review-11"
    require(b["prior_review_call"]==sha((RUN+":run_spec_review:11").encode()),"REVIEW_ID")
    raw=pr.check(work/"review.json").read_bytes()
    submission=pr.check(work/rs.RECORD).read_bytes()
    require(sha(raw)==b["files"][str(work/"review.json")]
        and sha(submission)==b["files"][str(work/rs.RECORD)],"GENUINE_REVIEW_BYTES")
    report=json.loads(raw);accepted=json.loads(submission)
    require(report["verdict"]==accepted["submission"]["verdict"]=="REVISE"
        and len(report["findings"])==2 and accepted["submission"]["bindings"]["call_id"]==b["prior_review_call"],
        "GENUINE_REVISE_REQUIRED")
    return sha(submission)
def restored(value,approval):
    require(value["phase"]=="BLOCKED" and value["reason"]=="OUTPUT_VALIDATION_REFUSED: ANALYSIS_REVISION_ROUND"
        and value["pending"]["id"]==sha((RUN+":run_spec_review:11").encode())
        and value["rounds"]["run_spec_author"]==12 and value["rounds"]["run_spec_review"]==11,"EXACT_STATE")
    result=json.loads(json.dumps(value))
    result.update(phase="run_spec_author",pending=None,reason="PROVENANCE_ONLY_CORRECTION")
    result["interventions"].append({"kind":EVENT,"review_sha256":approval,"scope_sha256":DOCUMENT_SHA,
        "preserved_calls":24,"maximum_new_calls":2,"run_limit":26,"batch_limit":140,
        "scientific_acceptance":False,"genuine_revise_preserved":True})
    return result
def grant(driver,b,approval):
    from orchestrator import private_records as pr
    check_originals(driver,b)
    row=driver.store.db.execute("SELECT payload FROM events WHERE id=?",(EVENT,)).fetchone()
    require(row is not None,"MISSING_APPROVED_GRANT");record=json.loads(row[0])
    require(record==json.loads(pr.check(driver.state/EVENT/"COMPLETE.json").read_bytes())
        and record["scope_sha256"]==DOCUMENT_SHA and record["review_sha256"]==approval
        and record["preserved_calls"]==24 and record["maximum_new_calls"]==2
        and record["run_limit"]==26 and record["batch_limit"]==140,"GRANT_CHANGED")
    return record
def active(driver,b,approval):
    if _PROBE_DB is driver.store.db:
        require(driver.store.db.in_transaction,"PROBE_TRANSACTION");check_originals(driver,b)
    else:grant(driver,b,approval)
def resume(driver,b,approval):
    from orchestrator import private_records as pr
    require(isinstance(approval,str)and len(approval)==64 and all(c in "0123456789abcdef"for c in approval),"APPROVAL")
    require(not(driver.state/"HALT").exists()and not(driver.store.batch.folder/"HALT").exists(),"HALT")
    check_originals(driver,b,initial=True);stream=genuine_review(driver,b)
    before=driver.current();after=restored(before,approval)
    dest=driver.state/EVENT;require(not dest.exists()and not dest.is_symlink(),"ALREADY_ATTEMPTED")
    record={"scope_sha256":DOCUMENT_SHA,"review_sha256":approval,"preserved_calls":24,
            "maximum_new_calls":2,"run_limit":26,"batch_limit":140,"review_submission_sha256":stream,
            "before_sha256":sha(canonical(before)),"after_sha256":sha(canonical(after))}
    pr.mkdir(dest);pr.write_bytes(dest/"INTENT.json",canonical(record))
    db=driver.store.db;db.execute("BEGIN IMMEDIATE")
    try:
        check_originals(driver,b,initial=True);genuine_review(driver,b)
        db.execute("INSERT INTO events VALUES(?,?,?)",(EVENT,RUN,canonical(record).decode()))
        db.execute("UPDATE manual_state SET payload=?WHERE id=1",(json.dumps(after,sort_keys=True),))
        db.execute("COMMIT")
    except BaseException:db.execute("ROLLBACK");raise
    require(driver.current()==after,"READBACK");pr.write_bytes(dest/"COMPLETE.json",canonical(record))
    return {"status":"READY_MULTIWIN_AUTHOR13","new_calls":0,"preserved_calls":24,"maximum_new_calls":2}
def install_hook(base,root,approval):
    root=Path(root);b=frozen(root)
    old=load("_retained_multiwin_question",root/"orchestrator/colab_arm_preparation.py")
    prior=old.frozen(root);old.legacy(root).activate_correction_modules(root)
    from orchestrator import autonomy_limits as limits,manual_recovery as recovery,colab_simple_full as full
    from orchestrator import colab_notebook_delivery as delivery,private_records as pr,manual_context
    # Existing daily reservation method remains intact; load the reviewed date policy only.
    policy=load("_reviewed_tonight_scientific_policy",root/"orchestrator/autonomy_limits.py")
    require(policy.daily_allowance("2026-10-12")["limit"]==100 and policy.daily_allowance("2026-10-13")["limit"]==50,"DAILY_POLICY")
    limits.daily_allowance=policy.daily_allowance
    old_global,old_local,old_role,old_batch=limits.global_limit,limits.local_limit,recovery.role_limit,full.batch_allowance
    old_cap_authority=limits.cap_authority
    def proxy(store):return type("BoundDriver",(),{"store":store,"state":Path(b["config"]["context"]).parent,"config":b["config"]})()
    def global_limit(batch,run):
        original=old_global(batch,run)
        if run!=RUN:return original
        require(original==20,"PRIOR_GLOBAL_LIMIT")
        # Use existing local connection if supplied by local admission, otherwise readonly.
        import sqlite3
        d=_PROBE_DB
        owned=d is None
        if owned:
            d=sqlite3.connect((Path(b["config"]["context"]).parent/"jobs.sqlite").as_uri()+"?mode=ro",uri=True);d.row_factory=sqlite3.Row
        try:
            store=type("Store",(),{"db":d,"batch":batch})()
            active(proxy(store),b,approval)
        finally:
            if owned:d.close()
        return 26
    def local_limit(store,run,policy):
        original=old_local(store,run,policy)
        if run!=RUN:return original
        require(original==20,"PRIOR_LOCAL_LIMIT");active(proxy(store),b,approval);return 26
    def role_limit(store,run,stage):
        original=old_role(store,run,stage)
        if run!=RUN:return original
        require(stage in {"run_spec_author","run_spec_review"},"PREPARATION_ONLY")
        active(proxy(store),b,approval)
        return 13 if stage=="run_spec_author"else 12
    policy140=load("_returned_batch140",root/"orchestrator/scientific_batch140.py")
    scope140=policy140.document(root)
    def batch_allowance(accounts,scope):
        require(scope["run_id"]==RUN,"BATCH_OWNER")
        value=policy140.allowance(accounts,RUN,scope140,approval)
        require(value["purpose"]=="returned_colab" and value["purpose_limit"]==4,"PURPOSE")
        return {**value,"process_continuation":{"scope_sha256":DOCUMENT_SHA,"review_sha256":approval,
            "same_owner":RUN,"preserved_calls":24,"maximum_new_calls":2,"run_limit":26}}
    def cap_authority(cap):
        if cap!=26:return old_cap_authority(cap)
        return "a7fbba4b5c49426c099f1eb8d91e45489b454fc51a527f5df1566a60c1cabcb1"
    limits.global_limit=global_limit;limits.local_limit=local_limit
    recovery.role_limit=role_limit;full.batch_allowance=batch_allowance;limits.cap_authority=cap_authority
    reader=load("_retained_dense_patch_reader",root/"orchestrator/manual_context.py")
    require(reader.JSON_PAGE_LINES==manual_context.JSON_PAGE_LINES==100
            and reader.JSON_PAGE_BYTES==manual_context.JSON_PAGE_BYTES==16000,"READER_LIMITS")
    manual_context._notebook_patch_reading_copy=reader._notebook_patch_reading_copy
    materializer=load("_reviewed_multiwin_delivery",root/"orchestrator/colab_notebook_delivery.py")
    previous_delivery=delivery.prepare_variants
    def prepare_variants(driver,value,pending,cases):
        if driver.config.get("run_id")!=RUN:return previous_delivery(driver,value,pending,cases)
        active(driver,b,approval)
        require(pending["stage"]=="run_spec_author"and pending["round"]==13,"EXACT_AUTHOR")
        return materializer.prepare_variants(driver,value,pending,cases,expected_arm="A1_multiwin",arm_level_only=True)
    delivery.prepare_variants=prepare_variants
    from orchestrator.autonomy_accounting import BatchAccounts
    previous_reserve=BatchAccounts.reserve_scientific
    def reserve_scientific(accounts,ident,run,stage,source,receipt):
        if run==RUN:
            require(source==b["config"]["source"],"ADMISSION_SOURCE")
            work=Path(receipt["workspace"]);prefix=stage+"-"
            require(work.parent==Path(b["config"]["workspace_root"])and work.name.startswith(prefix),"ADMISSION_WORKSPACE")
            number=work.name.removeprefix(prefix)
            require(number.isdecimal()and {"stage":stage,"attempt":int(number)}in b["allowed_calls"]
                and ident==sha((RUN+":"+stage+":"+number).encode()),"EXACT_CALL_ID")
        return previous_reserve(accounts,ident,run,stage,source,receipt)
    BatchAccounts.reserve_scientific=reserve_scientific
    class Correction(base):
        def guard(self):
            super().guard();check_originals(self,b)
        def prepare_input(self,value,stage,work):
            active(self,b,approval);number=value["rounds"].get(stage,0)+1
            require({"stage":stage,"attempt":number}in b["allowed_calls"],"EXACT_NEXT_CALL")
            body,measurement=super().prepare_input(value,stage,work)
            if stage!="run_spec_author":return body,measurement
            bodies={"multiwin-returned/"+Path(name).name:(root/name).read_bytes()
                    for name in b["context_files"]}
            from orchestrator import notebook_revision as nr,scientific_intake as intake
            registry=json.loads(nr.bound(self.context,self.config["private_intake"]))
            cases=intake.cohort((self.context/registry["cohort"]).read_bytes())
            refs=[]
            for name,raw in bodies.items():
                nr.scan(raw,cases);target=Path(work)/name;pr.mkdir(target.parent,parents=True,exist_ok=True)
                require(not target.exists()and not target.is_symlink(),"FEEDBACK_ALREADY_PREPARED")
                pr.write_bytes(target,raw);target.chmod(0o400);refs.append({"path":name,"sha256":sha(raw),"bytes":len(raw)})
            return body,{**measurement,"workspace_files":[*measurement["workspace_files"],*refs]}
        def _accept_completed(self,value):
            pending=value["pending"]
            if pending["stage"]!="run_spec_review":return super()._accept_completed(value)
            require(pending["round"]==12,"EXACT_REVIEW")
            from orchestrator import analysis_revisions as revisions
            previous=revisions.review_transition
            def bounded(review,stage,round_no,*,offset=0):
                require(stage=="run_spec_review" and round_no==12 and offset==4,"EXACT_REVIEW_TRANSITION")
                if review["verdict"]=="REJECT":return "BLOCKED","REVIEW_REJECTED"
                require(review["verdict"]=="REVISE" and review["findings"],"ACTIONABLE_REVISE")
                return "BLOCKED","BOUNDED_PROVENANCE_REVIEW_REVISE"
            revisions.review_transition=bounded
            try:return super()._accept_completed(value)
            finally:revisions.review_transition=previous
        def task(self,stage,value):
            require(stage in {"run_spec_author","run_spec_review"},"TASK_STAGE")
            return (root/TASK).read_text()+"\nRequired binding lines:\nrun_id: "+RUN+"\nanalysis_registry_sha256: "+self.config["private_intake"]["sha256"]+"\n"
    return Correction
