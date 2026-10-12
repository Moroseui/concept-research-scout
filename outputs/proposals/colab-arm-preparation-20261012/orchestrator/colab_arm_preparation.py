"""One operator-directed multiwin question inside existing Colab limits.

Reuses the reviewed driver; no new owner, allowance, compute or scientific code.
"""
from pathlib import Path
import hashlib, importlib.util, json

RUN = "colab-1ad5fafc220b3d65f576ce08"
DOCUMENT = "docs/COLAB_MULTIWIN_PRIVATE.json"
DOCUMENT_SHA = "ee873227842e067e6c069c0c095e918929c4b845e080622cb8afc891b4efb26c"
EVENT = "colab-multiwin-question-20261012"
OPERATOR = "docs/COLAB_ARM_ORDER_OPERATOR_20261012.txt"
TASK = "docs/COLAB_MULTIWIN_AUTHOR_TASK.md"
REFERENCE = "docs/COLAB_MULTIWIN_INPUT_REFERENCE_PRIVATE.json"
CALL = "ca4a98a824a7f3da1e5ebb3bf6d765c62832df4cf6cd44e5f7ecde3a9ca0fa49"
RUNTIME = ".colab-feedback"
sha = lambda raw: hashlib.sha256(raw).hexdigest()
canonical = lambda value: json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()

def require(ok, why):
    if not ok: raise ValueError("COLAB_ARM_"+why)

def frozen(root):
    root=Path(root);raw=(root/DOCUMENT).read_bytes()
    require(sha(raw)==DOCUMENT_SHA,"SCOPE_CHANGED")
    value=json.loads(raw)
    require(value["arm"]=="A1_multiwin" and value["next_author"]==9 and value["next_review"]==8
            and value["maximum_new_calls"]==2 and value["run_limit"]==20
            and value["batch_limit"]==104 and value["daily_limit"]==50
            and value["execution_authorized"] is False,"SCOPE_LIMITS")
    require(sha((root/OPERATOR).read_bytes())==value["operator_sha256"]
            =="9029bd20ae0ef24faa7e57c174db8bec843321518c5e3018997982cd1dbe080c","OPERATOR_CHANGED")
    require(sha((root/TASK).read_bytes())==value["task_sha256"],"TASK_CHANGED")
    require(sha((root/REFERENCE).read_bytes())==value["reference_sha256"],"REFERENCE_CHANGED")
    return value

def legacy(root):
    path=Path(root)/"orchestrator/colab_bound_revision.py"
    spec=importlib.util.spec_from_file_location("_retained_colab_feedback",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def check_originals(driver,b,*,initial=False):
    from orchestrator import private_records as pr
    require(driver.config["run_id"]==RUN and driver.config==b["config"],"ORIGINAL_CONFIGURATION")
    for name,pin in b["files"].items():
        require(sha(pr.check(driver.state.parent/name).read_bytes())==pin,"ORIGINAL_FILE_CHANGED")
    for table,key,db in (("manual_calls","local_rows",driver.store.db),
                         ("autonomy_calls","global_rows",driver.store.batch.db)):
        require(len(b[key])==16,"BASELINE_CALL_COUNT")
        for row in b[key]:
            current=db.execute("SELECT * FROM "+table+" WHERE id=?",(row["id"],)).fetchone()
            require(current is not None and dict(current)==row,"ORIGINAL_CALL_CHANGED")
    owner=driver.store.batch.db.execute("SELECT * FROM autonomy_runs WHERE id=?",(RUN,)).fetchone()
    require(owner is not None and dict(owner)==b["owner"],"ORIGINAL_OWNER_CHANGED")
    if initial:
        require(driver.store.db.execute("SELECT count(*) FROM manual_calls").fetchone()[0]==16,"NEW_ADMISSION")
        require(dict(driver.store.db.execute("SELECT * FROM manual_account WHERE id=1").fetchone())==b["account_row"],"ACCOUNT_CHANGED")
        require(dict(driver.store.db.execute("SELECT * FROM manual_state WHERE id=1").fetchone())==b["state_row"],"STATE_CHANGED")
        require(not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),"LIVE_CALL")
    review=json.loads(pr.check(driver.state.parent/"lane-scientific-workspaces/run_spec_review-7/review.json").read_bytes())
    require(review["verdict"]=="APPROVE" and not review["findings"],"BASELINE_NOT_APPROVED")

def restored(value,approval):
    require(value["phase"]=="COMMIT_SPEC" and value.get("pending") is None
            and value["rounds"]["run_spec_author"]==8 and value["rounds"]["run_spec_review"]==7,
            "EXACT_ACCEPTED_BASELINE_STATE")
    result=json.loads(json.dumps(value))
    result.update(phase="run_spec_author",reason="NEW_OPERATOR_ARM_QUESTION")
    for key in ("blocked_stage","blocker_categories","review"): result.pop(key,None)
    result["interventions"].append({"kind":EVENT,"baseline_review_call":CALL,"proof_sha256":DOCUMENT_SHA,
        "implementation_review_sha256":approval,"scientific_acceptance":False,"reviewer_revise":False,
        "new_allowance":0,"arm":"A1_multiwin","maximum_new_calls":2})
    return result

def grant(driver,b,approval):
    from orchestrator import private_records as pr
    check_originals(driver,b)
    record=json.loads(pr.check(driver.state/EVENT/"COMPLETE.json").read_bytes())
    require(record["proof_sha256"]==DOCUMENT_SHA and record["review_sha256"]==approval
            and record["new_allowance"]==0 and record["maximum_new_calls"]==2,"QUESTION_APPROVAL")
    events=driver.store.db.execute("SELECT payload FROM events WHERE id=?",(EVENT,)).fetchone()
    require(events is not None and json.loads(events[0])==record,"QUESTION_EVENT")
    rows=[dict(r) for r in driver.store.db.execute("SELECT * FROM manual_calls ORDER BY rowid")]
    old={r["id"] for r in b["local_rows"]};new=[r for r in rows if r["id"] not in old]
    require(len(new)<=2 and all((r["stage"],r["attempt"]) in
            {("run_spec_author",9),("run_spec_review",8)} and
            r["id"]==sha((RUN+":"+r["stage"]+":"+str(r["attempt"])).encode())
            for r in new),"QUESTION_TWO_CALL_BOUND")
    return record

def resume(driver,b,approval):
    from orchestrator import private_records as pr
    from orchestrator.experiment_approval import verified_review_delivery
    require(isinstance(approval,str) and len(approval)==64 and all(c in "0123456789abcdef" for c in approval),"APPROVAL")
    require(not(driver.state/"HALT").exists() and not(Path(driver.config["batch_ledger"])/"HALT").exists(),"HALT")
    check_originals(driver,b,initial=True)
    pending={"id":CALL,"stage":"run_spec_review","round":7,
             "workspace":str(driver.state.parent/"lane-scientific-workspaces/run_spec_review-7")}
    _,_,raw,_,_,_=verified_review_delivery(driver,pending,"run_spec_review")
    require(json.loads(raw)["verdict"]=="APPROVE" and not json.loads(raw)["findings"],"AUTHENTIC_BASELINE_APPROVAL")
    before=b["state_row"]["payload"];after=restored(json.loads(before),approval)
    dest=driver.state/EVENT;require(not dest.exists() and not dest.is_symlink(),"QUESTION_ALREADY_ATTEMPTED")
    pr.mkdir(dest);pr.write_bytes(dest/"original-rows.json",canonical(b))
    record={"proof_sha256":DOCUMENT_SHA,"review_sha256":approval,"operator_sha256":b["operator_sha256"],
            "new_calls":0,"new_allowance":0,"maximum_new_calls":2,
            "before_state_sha256":sha(before.encode()),"after_state_sha256":sha(canonical(after))}
    pr.write_bytes(dest/"INTENT.json",canonical(record))
    db=driver.store.db;db.execute("BEGIN IMMEDIATE")
    try:
        check_originals(driver,b,initial=True)
        require(not db.execute("SELECT 1 FROM events WHERE id=?",(EVENT,)).fetchone(),"QUESTION_EVENT_EXISTS")
        db.execute("INSERT INTO events VALUES(?,?,?)",(EVENT,RUN,canonical(record).decode()))
        db.execute("UPDATE manual_state SET payload=? WHERE id=1",(json.dumps(after,sort_keys=True),))
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK");raise
    pr.write_bytes(dest/"COMPLETE.json",canonical(record));require(driver.current()==after,"READBACK")
    return {"status":"READY_MULTIWIN_AUTHOR9","calls_preserved":16,"new_calls":0,"new_allowance":0}

def feedback_files(driver,b,root=None):
    from orchestrator import notebook_revision as nr,colab_preparation_scope as scope,scientific_intake as intake
    require(root is not None,"REFERENCE_ROOT")
    original,selection=scope.validate_notebook_config(driver.context,driver.config["notebook_revision"])
    registry=json.loads(nr.bound(driver.context,driver.config["private_intake"]))
    cases=intake.cohort((driver.context/registry["cohort"]).read_bytes())
    view,manifest=nr.partition(original,selection,cases,nr.VIEW);old=legacy(root)
    bodies={"check.py":old.CHECKER.encode(),"orchestrator/__init__.py":b"",
        **{"orchestrator/"+name+".py":raw for name,raw in old.runtime_libraries().items()},
        "view.txt":view,"manifest.json":canonical(manifest),
        "binding.json":canonical({"run_id":RUN,"analysis_registry_sha256":driver.config["private_intake"]["sha256"],
                                  "original_sha256":nr.ORIGINAL,"view_sha256":nr.VIEW})}
    prior=driver.state.parent/"lane-scientific-workspaces/run_spec_author-8"
    for name in ("SPEC.proposed.md","notebook.patch.json"): bodies["baseline-"+name]=(prior/name).read_bytes()
    bodies["accepted-input-reference-A1_multiwin.json"]=(Path(root)/REFERENCE).read_bytes()
    require(sha(bodies["accepted-input-reference-A1_multiwin.json"])==b["reference_sha256"],"REFERENCE_CHANGED")
    for raw in bodies.values(): nr.scan(raw,cases)
    return {RUNTIME+"/"+name:raw for name,raw in bodies.items()}

def probe_admission(driver,root,approval):
    from orchestrator import manual_recovery
    b=frozen(root);check_originals(driver,b,initial=True)
    before=b["state_row"]["payload"];db=driver.store.db
    require(not db.in_transaction,"CLEAN_PROBE")
    db.execute("BEGIN IMMEDIATE")
    try:
        value=restored(json.loads(before),approval)
        db.execute("UPDATE manual_state SET payload=? WHERE id=1",(json.dumps(value,sort_keys=True),))
        author=driver.model_round_number(value)
        reviewer=driver.model_round_number({**value,"phase":"run_spec_review"})
        require(author==9 and reviewer==8,"NATIVE_STAGE_ROUNDS")
        require(manual_recovery.role_limit(driver.store,RUN,"run_spec_author")>=author
                and manual_recovery.role_limit(driver.store,RUN,"run_spec_review")>=reviewer,"NATIVE_ROLE_LIMIT")
    finally: db.rollback()
    require(db.execute("SELECT payload FROM manual_state WHERE id=1").fetchone()[0]==before,"PROBE_ROLLBACK")
    check_originals(driver,b,initial=True)
    return {"status":"PASS","author_attempt":9,"review_attempt":8,"model_calls":0,"reservations":0,
            "persistent_state_mutations":0,"new_allowance":0}

def install_hook(base,root,approval):
    from orchestrator import private_records as pr,colab_notebook_delivery as delivery
    b=frozen(root);legacy(root).activate_correction_modules(root)
    path=Path(root)/"orchestrator/colab_notebook_delivery.py"
    spec=importlib.util.spec_from_file_location("_reviewed_arm_delivery",path)
    materializer=importlib.util.module_from_spec(spec);spec.loader.exec_module(materializer)
    original_delivery=delivery.prepare_variants
    def prepare_variants(driver,value,pending,cases):
        if driver.config.get("run_id")!=RUN:return original_delivery(driver,value,pending,cases)
        grant(driver,b,approval)
        require(pending["stage"]=="run_spec_author" and pending["round"]==9,"EXACT_AUTHOR")
        return materializer.prepare_variants(driver,value,pending,cases,expected_arm=b["arm"])
    delivery.prepare_variants=prepare_variants
    class ArmQuestion(base):
        def guard(self):
            super().guard()
            check_originals(self,b)
        def prepare_input(self,value,stage,work):
            grant(self,b,approval)
            require(stage in {"run_spec_author","run_spec_review"},"PREPARATION_ONLY")
            number=value["rounds"].get(stage,0)+1
            require((stage,number) in {("run_spec_author",9),("run_spec_review",8)},"EXACT_NEXT_CALL")
            if stage!="run_spec_author":return super().prepare_input(value,stage,work)
            body,measurement=super().prepare_input(value,stage,work);refs=[]
            for name,raw in feedback_files(self,b,root).items():
                target=Path(work)/name;pr.mkdir(target.parent,parents=True,exist_ok=True)
                require(not target.exists() and not target.is_symlink(),"FEEDBACK_ALREADY_PREPARED")
                pr.write_bytes(target,raw);target.chmod(0o400)
                refs.append({"path":name,"sha256":sha(raw),"bytes":len(raw)})
            return body,{**measurement,"workspace_files":[*measurement["workspace_files"],*refs]}
        def task(self,stage,value):
            require(stage in {"run_spec_author","run_spec_review"},"TASK_STAGE")
            return ((Path(root)/TASK).read_text()+"\nRequired specification binding lines:\nrun_id: "+RUN+
                "\nanalysis_registry_sha256: "+self.config["private_intake"]["sha256"]+"\n")
    return ArmQuestion
