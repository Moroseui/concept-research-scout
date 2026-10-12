"""One same-owner multiwin correction, four calls maximum; history immutable."""
from pathlib import Path
import hashlib,importlib.util,json
RUN="colab-1ad5fafc220b3d65f576ce08"
DOCUMENT="docs/MULTIWIN_TONIGHT_CONTINUATION_PRIVATE.json"
DOCUMENT_SHA="e298ad21e22acd041b8b4a78d551125b5e1694ae17155ee0f9012cced7afee01"
EVENT="multiwin-tonight-continuation-20261012"
REVIEW9="125d26e2f74b735214b344e2ac868b3fdea629b54d90e1f9094ce3a5637c3a8c"
TASK="docs/MULTIWIN_TONIGHT_AUTHOR_TASK.md"
REFERENCE="docs/PNORMCT_REVIEWED_REFERENCE_PRIVATE.py"
FAILURE="docs/MULTIWIN_AUTHOR10_TEST_FAILURE_PRIVATE.txt"
_PROBE_DB=None
sha=lambda raw:hashlib.sha256(raw).hexdigest()
canonical=lambda v:json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def require(ok,why):
    if not ok:raise ValueError("MULTIWIN_TONIGHT_"+why)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def frozen(root):
    root=Path(root);raw=(root/DOCUMENT).read_bytes()
    require(sha(raw)==DOCUMENT_SHA,"SCOPE_CHANGED");b=json.loads(raw)
    require(b["run"]==RUN and b["maximum_new_calls"]==4 and b["run_limit"]==24
            and b["batch_limit"]==128 and b["colab_allocation_remaining"]==11
            and b["scientific_baseline_count"]==111 and b["execution_authorized"]is False,"LIMITS")
    require(len(b["local_calls_pins"])==len(b["global_calls_pins"])==20
            and len(b["scientific_calls_pins"])==111,"ORIGINAL_COUNTS")
    require(b["allowed_calls"]==[{"stage":"run_spec_author","attempt":11},
            {"stage":"run_spec_review","attempt":10},{"stage":"run_spec_author","attempt":12},
            {"stage":"run_spec_review","attempt":11}],"EXACT_CALLS")
    for name,key in [(TASK,"task_sha256"),(REFERENCE,"pnormct_reference_sha256"),(FAILURE,"failure_sha256"),
                     ("docs/COLAB_TONIGHT_OPERATOR_20261012.txt","operator_sha256")]:
        path=root/name
        require(not path.is_symlink()and sha(path.read_bytes())==b[key],"CONTEXT_CHANGED")
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
    require(len(extra)<=4 and all((r["stage"],r["attempt"])in allowed and
        r["id"]==sha((RUN+":"+r["stage"]+":"+str(r["attempt"])).encode())for r in extra),"FOUR_CALL_SCOPE")
    g=[dict(r)for r in driver.store.batch.db.execute("SELECT * FROM autonomy_calls WHERE change_id=?",(RUN,))]
    require(len(g)<=24 and all(r["id"]in b["global_calls_pins"]or
        r["id"]in {sha((RUN+":"+stage+":"+str(n)).encode())for stage,n in allowed}for r in g),"GLOBAL_SCOPE")
    if initial:
        require(not extra and len(g)==20,"ALREADY_CONTINUED")
        require(dict(driver.store.db.execute("SELECT * FROM manual_state WHERE id=1").fetchone())==b["state_row"],"STATE_CHANGED")
        require(dict(driver.store.db.execute("SELECT * FROM manual_account WHERE id=1").fetchone())==b["account_row"],"ACCOUNT_CHANGED")
        require(not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),"LIVE_CALL")
def mechanical_review(driver,b):
    from orchestrator import private_records as pr,review_submission as rs
    work=driver.state.parent/"lane-scientific-workspaces/run_spec_review-9"
    raw=pr.check(work/"console.log").read_bytes()
    require(sha(raw)==b["files"][str(work/"console.log")],"REVIEW_STREAM")
    require(rs.terminal_without_submission(work,raw.decode()),"UNQUALIFIED_TERMINAL")
    events=[]
    for line in raw.splitlines():
        try:value=json.loads(line)
        except ValueError:continue
        if isinstance(value,dict):events.append(value)
    final=events[-1]
    require(final.get("type")=="result"and final.get("subtype")=="error_max_turns"
            and final.get("is_error")is False and final.get("num_turns")==30,"EXACT_MECHANICAL_CAUSE")
    require(not(work/rs.RECORD).exists(),"SCIENTIFIC_VERDICT_EXISTS")
    return sha(raw)
def restored(value,approval):
    require(value["phase"]=="BLOCKED"and value["reason"]=="REVIEW_SUBMISSION_FAILED_NO_RETRY: ACCEPTED_SUBMISSION_REQUIRED"
        and value["pending"]["id"]==REVIEW9 and value["pending"]["round"]==9
        and value["rounds"]["run_spec_author"]==10 and value["rounds"]["run_spec_review"]==8,"EXACT_TERMINAL_STATE")
    result=json.loads(json.dumps(value))
    result.update(phase="run_spec_author",pending=None,reason="BOUNDED_MULTIWIN_FIXTURE_CORRECTION")
    result["rounds"]["run_spec_review"]=9  # Failed attempt remains consumed; never replay reviewer9.
    result["interventions"].append({"kind":EVENT,"review_sha256":approval,"scope_sha256":DOCUMENT_SHA,
        "preserved_calls":20,"maximum_new_calls":4,"run_limit":24,"batch_limit":128,
        "scientific_acceptance":False,"reviewer_revise":False})
    return result
def grant(driver,b,approval):
    from orchestrator import private_records as pr
    check_originals(driver,b)
    row=driver.store.db.execute("SELECT payload FROM events WHERE id=?",(EVENT,)).fetchone()
    require(row is not None,"MISSING_APPROVED_GRANT");record=json.loads(row[0])
    require(record==json.loads(pr.check(driver.state/EVENT/"COMPLETE.json").read_bytes())
        and record["scope_sha256"]==DOCUMENT_SHA and record["review_sha256"]==approval
        and record["preserved_calls"]==20 and record["maximum_new_calls"]==4
        and record["run_limit"]==24 and record["batch_limit"]==128,"GRANT_CHANGED")
    return record
def active(driver,b,approval):
    if _PROBE_DB is driver.store.db:
        require(driver.store.db.in_transaction,"PROBE_TRANSACTION");check_originals(driver,b)
    else:grant(driver,b,approval)
def resume(driver,b,approval):
    from orchestrator import private_records as pr
    require(isinstance(approval,str)and len(approval)==64 and all(c in "0123456789abcdef"for c in approval),"APPROVAL")
    require(not(driver.state/"HALT").exists()and not(driver.store.batch.folder/"HALT").exists(),"HALT")
    check_originals(driver,b,initial=True);stream=mechanical_review(driver,b)
    before=driver.current();after=restored(before,approval)
    dest=driver.state/EVENT;require(not dest.exists()and not dest.is_symlink(),"ALREADY_ATTEMPTED")
    record={"scope_sha256":DOCUMENT_SHA,"review_sha256":approval,"preserved_calls":20,
            "maximum_new_calls":4,"run_limit":24,"batch_limit":128,"terminal_stream_sha256":stream,
            "before_sha256":sha(canonical(before)),"after_sha256":sha(canonical(after))}
    pr.mkdir(dest);pr.write_bytes(dest/"INTENT.json",canonical(record))
    db=driver.store.db;db.execute("BEGIN IMMEDIATE")
    try:
        check_originals(driver,b,initial=True);mechanical_review(driver,b)
        db.execute("INSERT INTO events VALUES(?,?,?)",(EVENT,RUN,canonical(record).decode()))
        db.execute("UPDATE manual_state SET payload=?WHERE id=1",(json.dumps(after,sort_keys=True),))
        db.execute("COMMIT")
    except BaseException:db.execute("ROLLBACK");raise
    require(driver.current()==after,"READBACK");pr.write_bytes(dest/"COMPLETE.json",canonical(record))
    return {"status":"READY_MULTIWIN_AUTHOR11","new_calls":0,"preserved_calls":20,"maximum_new_calls":4}
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
        return 24
    def local_limit(store,run,policy):
        original=old_local(store,run,policy)
        if run!=RUN:return original
        require(original==20,"PRIOR_LOCAL_LIMIT");active(proxy(store),b,approval);return 24
    def role_limit(store,run,stage):
        original=old_role(store,run,stage)
        if run!=RUN:return original
        require(stage in {"run_spec_author","run_spec_review"},"PREPARATION_ONLY")
        active(proxy(store),b,approval)
        return 12 if stage=="run_spec_author"else 11
    def batch_allowance(accounts,scope):
        previous=old_batch(accounts,scope)
        require(scope["run_id"]==RUN,"BATCH_OWNER")
        # Original104 calls and genuine batch128 operator authority are still verified.
        value=old.authorized_batch(accounts,prior,approval,previous)
        return {**value,"process_continuation":{"scope_sha256":DOCUMENT_SHA,"review_sha256":approval,
            "same_owner":RUN,"preserved_calls":20,"maximum_new_calls":4,"run_limit":24}}
    def cap_authority(cap):
        if cap!=24:return old_cap_authority(cap)
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
        require(pending["stage"]=="run_spec_author"and pending["round"]in {11,12},"EXACT_AUTHOR")
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
            bodies=old.feedback_files(self,prior,root)
            author=self.state.parent/"lane-scientific-workspaces/run_spec_author-10"
            for name in ("SPEC.proposed.md","notebook.patch.json"):
                bodies[old.RUNTIME+"/baseline-"+name]=pr.check(author/name).read_bytes()
            bodies[old.RUNTIME+"/pnormct-reviewed-reference.py"]=(root/REFERENCE).read_bytes()
            bodies[old.RUNTIME+"/author10-test-failure.txt"]=(root/FAILURE).read_bytes()
            from orchestrator import notebook_revision as nr,scientific_intake as intake
            registry=json.loads(nr.bound(self.context,self.config["private_intake"]))
            cases=intake.cohort((self.context/registry["cohort"]).read_bytes())
            refs=[]
            for name,raw in bodies.items():
                nr.scan(raw,cases);target=Path(work)/name;pr.mkdir(target.parent,parents=True,exist_ok=True)
                require(not target.exists()and not target.is_symlink(),"FEEDBACK_ALREADY_PREPARED")
                pr.write_bytes(target,raw);target.chmod(0o400);refs.append({"path":name,"sha256":sha(raw),"bytes":len(raw)})
            return body,{**measurement,"workspace_files":[*measurement["workspace_files"],*refs]}
        def task(self,stage,value):
            require(stage in {"run_spec_author","run_spec_review"},"TASK_STAGE")
            return (root/TASK).read_text()+"\nRequired binding lines:\nrun_id: "+RUN+"\nanalysis_registry_sha256: "+self.config["private_intake"]["sha256"]+"\n"
    return Correction
