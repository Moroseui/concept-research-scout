"""Exact interpretation-only continuation for completed Idea2 aggregates.

Preserves the accepted preparation lane, original acceptance and all charges.
Uses the ordinary author/reviewer stages; no computation or provider authority.
"""
from pathlib import Path
import hashlib, json, sqlite3, os
from orchestrator import private_records as pr, idea2_cpu_lane as cpu_lane
from orchestrator import idea2_results_intake as results

RUN = results.contract.RUN
FIELD = "idea2_interpretation"
DOCUMENT = "docs/IDEA2_INTERPRETATION_PRIVATE.json"
DOCUMENT_SHA = "a99cad1f186ebae26527e966355e5ab0e8829008b91d9b6eb63b2b51bc515fd4"
CHANGE = "item6-smoothing-intake-20261012"
BRANCH = "astra/manual-item6-smoothing-intake-20261012"
EVENT = RUN + ":smoothing-interpretation-grant"
ACCEPTED = RUN + ":smoothing-results-accepted"
STAGES = frozenset(("result_interpretation_author", "result_interpretation_review"))
_TERMINAL_QUALIFIER = None
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encoded=lambda v:json.dumps(v,sort_keys=True,allow_nan=False).encode()

def require(ok, why):
    if not ok:raise ValueError("IDEA2_INTERPRETATION_"+why)

def document():
    raw=(Path(__file__).resolve().parents[1]/DOCUMENT).read_bytes()
    require(sha(raw)==DOCUMENT_SHA,"SCOPE_CHANGED")
    s=json.loads(raw)
    require(s["run_id"]==RUN and s["admitted_stages"]==sorted(STAGES)
        and s["call_limit"]==30 and s["batch_limit"]==128 and s["item_cap_micro_usd"]==100000000
        and s["new_execution_authorized"] is False and s["new_provider_commitment_micro_usd"]==0,
        "FIXED_SCOPE")
    require(s["allocation_limit"]==4 and s["allocation_prior_call_count"]==13
        and len(s["prior"]["global"]["calls"])==15
        and len(s["allocation_original_call_ids"])==13, "UNCHANGED_ANALYSIS_ALLOCATION")
    for row in s["operator_decisions"]:
        require(sha(row["text"].encode())==row["text_sha256"],"OPERATOR_RECORD_CHANGED")
    return s

def _path(root, absolute):
    p=Path(absolute)
    require(p.is_absolute() and ".."not in p.parts,"ABSOLUTE_PATH")
    p=Path(root)/p.relative_to("/")
    require(not any(q.is_symlink()for q in (p,*p.parents)),"PATH_ALIAS")
    return p

def selected(store):
    p=Path(store.path).parent/"lane.json"
    return p.exists() and FIELD in json.loads(pr.check(p).read_bytes())

def _approval(config,scope,host):
    from orchestrator.autonomy_review import verify_result
    folder=_path(host,scope["review_directory"])
    if Path(host)==Path("/"):
        from orchestrator.manual_host_guard import trusted
        trusted(folder)
    approval=verify_result(folder)
    manifest=json.loads((folder/"packet-manifest.json").read_bytes())
    report=json.loads((folder/"report.md").read_bytes())
    require(approval["verdict"]=="APPROVE" and not report["findings"]
        and approval["change_id"]==CHANGE and approval["source_sha"]==config["source"],
        "INDEPENDENT_APPROVE")
    required={DOCUMENT,"docs/SCIENTIFIC_REVISE_OPERATOR_DECISION_20261012.txt","orchestrator/idea2_interpretation.py","orchestrator/idea2_results_intake.py",
        "orchestrator/autonomy_accounting.py","orchestrator/manual_driver.py",
        "orchestrator/experiment_acceptance.py","tools/idea2_interpretation_runtime.py"}
    require(required<=set(manifest["source_files"]),"WHOLE_COMPONENT")
    root=Path(config["root"])
    for name,pin in manifest["source_files"].items():
        require(sha(pr.check(root/name).read_bytes())==pin,"REVIEWED_SOURCE_CHANGED")
    return approval["report_sha256"]

def failed_preparation(scope,host):
    previous=scope["failed_prepare"]
    folder=_path(host,previous["lane"])
    pr.check_tree(folder)
    files={str(p.relative_to(folder)):p for p in folder.rglob("*")if p.is_file()}
    require(set(files)==set(previous["files"]),"PARTIAL_PREPARATION_MEMBERSHIP")
    for name,path in files.items():
        raw=pr.check(path).read_bytes();pin=previous["files"][name]
        require(len(raw)==pin["bytes"] and sha(raw)==pin["sha256"],"PARTIAL_PREPARATION_CHANGED")
    require(previous["grant_absent_at_capture"] is True
        and len(previous["calls"])==15
        and json.loads(previous["state_row"]["payload"])["phase"]=="COMMIT_SPEC",
        "PARTIAL_PREPARATION_SCOPE")

def _originals(db,scope,host):
    prior=scope["prior"]
    failed_preparation(scope,host)
    cpu_lane.read_accepted_lane(_path(host,prior["parent_lane"]),Path(__file__).resolve().parents[1])
    owner=db.execute("SELECT * FROM autonomy_runs WHERE id=?",(RUN,)).fetchone()
    expected=prior["global"]["owner"][0]
    require(owner is not None and owner["binding"]==expected["binding"],"ORIGINAL_OWNER")
    for row in prior["global"]["calls"]:
        actual=db.execute("SELECT * FROM autonomy_calls WHERE id=?",(row["id"],)).fetchone()
        require(actual is not None and dict(actual)==row,"ORIGINAL_CALL_CHANGED")
    for old in prior["global"]["preserved_events"]:
        event=db.execute("SELECT * FROM events WHERE id=?",(old["id"],)).fetchone()
        require(event is not None and dict(event)==old,"ORIGINAL_ACCEPTANCE_CHANGED")
    return dict(owner)

def _configuration(store,run):
    if not selected(store):return None
    config=json.loads(pr.check(Path(store.path).parent/"lane.json").read_bytes())
    scope=document();host=Path(store.batch.filesystem_root);before=scope["prior"]["config"]
    require(run==RUN==config["run_id"] and config["item_number"]==6 and config["backend"]=="cpu"
        and config[FIELD]=={"schema":"idea2-interpretation/v1","scope_sha256":DOCUMENT_SHA},
        "CONFIG_SCOPE")
    require(Path(store.path).parent==_path(host,scope["new_lane"]),"EXACT_LANE")
    mutable={"root","source","branch","context","workspace_root","engine_files","engine_review"}
    require(set(config)==set(before)|{FIELD}
        and all(config[k]==v for k,v in before.items()if k not in mutable),"CONFIG_CHANGED")
    require(config["branch"]==BRANCH and config["author_timeout_seconds"]==1800
        and Path(config["context"])==_path(host,scope["new_lane"])/"context"
        and Path(config["workspace_root"])==_path(host,scope["new_lane"]).with_name("lane-scientific-workspaces"),
        "EXACT_PATHS")
    if host==Path("/"):
        require(Path(config["root"])==Path(__file__).resolve().parents[1],"EXACT_ROOT")
    approval=_approval(config,scope,host)
    for old in scope["prior"]["local"]["manual_calls"]:
        actual=store.db.execute("SELECT * FROM manual_calls WHERE id=?",(old["id"],)).fetchone()
        require(actual is not None and dict(actual)==old,"LOCAL_HISTORY_CHANGED")
    return config,scope,host,approval

def _grant(config,scope,approval,host):
    return {"schema":"idea2-interpretation-grant/v1","run_id":RUN,"source":config["source"],
        "scope_sha256":DOCUMENT_SHA,"implementation_review_sha256":approval,
        "configuration_sha256":sha(encoded(config)),"stages":sorted(STAGES),
        "prior_calls":15,"call_limit":30,"batch_limit":128,"item_cap_micro_usd":100000000,
        "execution_receipt_sha256":native_results(scope,host)["receipt"]["execution_receipt_sha256"],
        "new_execution_authorized":False}

def validate(store,run):
    chosen=_configuration(store,run)
    if chosen is None:return None
    config,scope,host,approval=chosen;owner=_originals(store.batch.db,scope,host)
    row=store.batch.db.execute("SELECT job,payload FROM events WHERE id=?",(EVENT,)).fetchone()
    require(row is not None and row["job"]==RUN and json.loads(row["payload"])==_grant(config,scope,approval,host),
            "ACTIVATION_REQUIRED")
    if owner["status"]!="ACTIVE":
        event=store.batch.db.execute("SELECT payload FROM events WHERE id=?",(ACCEPTED,)).fetchone()
        report=Path(store.path).parent/"REPORT.md"
        require(owner["status"]=="COMPLETE" and event is not None and report.is_file()
            and json.loads(event[0])["report_sha256"]==sha(pr.check(report).read_bytes()),"OWNER_STATUS")
    return scope

def activate(store,run):
    config,scope,host,approval=_configuration(store,run);db=store.batch.db
    db.execute("BEGIN IMMEDIATE")
    try:
        require(_originals(db,scope,host)==scope["prior"]["global"]["owner"][0],"ACTIVE_OWNER")
        require(not db.execute("SELECT 1 FROM events WHERE id=?",(EVENT,)).fetchone(),"ALREADY_ACTIVATED")
        require(not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),"LIVE_MODEL")
        require(db.execute("SELECT count(*) FROM autonomy_calls WHERE change_id=?",(RUN,)).fetchone()[0]==15,
                "NEW_CALL_BEFORE_ACTIVATION")
        value=json.loads(store.db.execute("SELECT payload FROM manual_state WHERE id=1").fetchone()[0])
        require(value["phase"]=="result_interpretation_author" and value["rounds"]==scope["offsets"],
                "FRESH_INTERPRETATION_STATE")
        verified_by_store(store,value,config,scope,host)
        db.execute("INSERT INTO events VALUES(?,?,?)",(EVENT,RUN,encoded(_grant(config,scope,approval,host)).decode()))
        db.execute("COMMIT")
    except BaseException:db.execute("ROLLBACK");raise
    return {"status":"IDEA2_INTERPRETATION_READY","prior_calls":15,"new_allowance":0}

def offset(store,run,stage):
    scope=validate(store,run)
    return 0 if scope is None else scope["offsets"].get(stage,0)

def guard_admission(accounts,run,stage,source,receipt):
    require(run==RUN,"EXACT_RUN")
    scope=document();host=Path(accounts.filesystem_root)
    row=accounts.db.execute("SELECT payload FROM events WHERE id=?",(EVENT,)).fetchone()
    if row is None:return None
    require(stage in STAGES,"INTERPRETATION_ONLY")
    from types import SimpleNamespace
    path=pr.check(_path(host,scope["new_lane"])/"jobs.sqlite")
    local=sqlite3.connect(path.as_uri()+"?mode=ro",uri=True);local.row_factory=sqlite3.Row
    local.execute("PRAGMA query_only=ON");local.execute("BEGIN")
    try:
        config,scope,host,approval=_configuration(
            SimpleNamespace(path=path,db=local,batch=accounts),run)
    finally:local.rollback();local.close()
    grant=json.loads(row[0])
    require(grant==_grant(config,scope,approval,host) and grant["source"]==source,"ADMISSION_APPROVAL")
    owner=_originals(accounts.db,scope,host);require(owner["status"]=="ACTIVE","ACTIVE_OWNER")
    work=Path(receipt["workspace"]);root=_path(host,scope["new_lane"]).with_name("lane-scientific-workspaces")
    require(work.parent==root and work.name.startswith(stage+"-"),"ADMISSION_WORKSPACE")
    number=work.name.removeprefix(stage+"-")
    require(number.isdecimal() and int(number)>scope["offsets"][stage]
        and int(number)<=scope["offsets"][stage]+4,"INTERPRETATION_ROUNDS")
    used=accounts.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific' AND change_id=?",(RUN,)).fetchone()[0]
    require(used < scope["allocation_prior_call_count"]+scope["allocation_limit"], "ANALYSIS_ALLOCATION_EXHAUSTED")
    # Run/day/batch caps, duplicate refusal and actual reservation remain normal.
    return scope

def terminal_ids(accounts,scope):
    require(callable(_TERMINAL_QUALIFIER),"TERMINAL_QUALIFIER_REQUIRED")
    rows=[dict(r)for r in accounts.db.execute(
        "SELECT * FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN') ORDER BY id")]
    require(rows==scope["uncertain_rows"] and all(r["status"]=="UNCERTAIN"for r in rows),
            "UNCLASSIFIED_OR_RUNNING")
    out=[]
    for row in rows:
        proof=_TERMINAL_QUALIFIER(accounts,row)
        require(isinstance(proof,dict) and proof.get("id")==row["id"]
            and isinstance(proof.get("proof_sha256"),str) and len(proof["proof_sha256"])==64,"TERMINAL_PROOF")
        out.append(row["id"])
    return out

def batch_allowance(accounts,scope):
    row=accounts.db.execute("SELECT payload FROM events WHERE id=?",(EVENT,)).fetchone()
    require(row is not None,"BATCH_GRANT")
    grant=json.loads(row[0])
    require(grant["scope_sha256"]==DOCUMENT_SHA and grant["batch_limit"]==scope["batch_limit"]==128,"BATCH_SCOPE")
    frozen=scope["allocation_initial_calls"]
    require(len(frozen)==109 and len({r["id"]for r in frozen})==109,"INITIAL_CALL_SET")
    for row in frozen:
        actual=accounts.db.execute("SELECT * FROM autonomy_calls WHERE id=?",(row["id"],)).fetchone()
        require(actual is not None and sha(encoded(dict(actual)))==row["sha256"],"ALLOCATION_HISTORY_CHANGED")
    original=set(scope["allocation_original_call_ids"])
    rows=accounts.db.execute("SELECT id FROM autonomy_calls WHERE kind='scientific' AND change_id=?",(RUN,)).fetchall()
    used=sum(row["id"]not in original for row in rows)
    require(used < 4,"ANALYSIS_ALLOCATION_EXHAUSTED")
    return {"limit":128,"scoped_run_id":RUN,"scope_sha256":DOCUMENT_SHA,
        "review_sha256":grant["implementation_review_sha256"],
        "operator_answer_sha256":scope["batch_answer_sha256"],
        "operator_question_sha256":scope["batch_question_sha256"],
        "analysis_allocation_used":used,"analysis_allocation_limit":4}

def native_results(scope,host):
    from orchestrator.autonomy_review import verify_result
    approval=verify_result(_path(host,scope["cpu_review_directory"]))
    require(approval["verdict"]=="APPROVE" and approval["change_id"]==scope["cpu_change_id"]
        and approval["source_sha"]==scope["cpu_source"]
        and approval["report_sha256"]==scope["cpu_review_sha256"],"CPU_APPROVAL")
    work=_path(host,scope["result_work"])
    # This repair consumes the already completed, separately approved CPU run.
    # Exact observed bytes are now pinned; no recomputation or invented receipt.
    for name,pin in scope["result_files"].items():
        require(sha(pr.check(work/name).read_bytes())==pin,"NATIVE_RESULT_CHANGED")
    return results.verify(work,approval["source_sha"],approval["report_sha256"])

def verified_by_store(store,value,config,scope,host):
    native=native_results(scope,host)
    folder=Path(store.path).parent
    require(json.loads(pr.check(folder/"validation.json").read_bytes())==native["validation"],
            "LOCAL_VALIDATION")
    for name,raw in native["files"].items():
        require(pr.check(folder/"diagnostics-results"/name).read_bytes()==raw,"LOCAL_RESULT_CHANGED")
    require(value["idea2_result_receipt_sha256"]==sha(encoded(native["receipt"])),"RESULT_RECEIPT")
    return native["validation"]

def verified(driver,value):
    config,scope,host,_=_configuration(driver.store,RUN)
    return verified_by_store(driver.store,value,config,scope,host)

def task(driver,stage,value):
    scope=validate(driver.store,RUN);require(stage in STAGES,"INTERPRETATION_ONLY")
    raw=pr.check(driver.root/"docs/IDEA2_INTERPRETATION_TASK.md").read_bytes()
    require(sha(raw)==scope["author_task_sha256"],"TASK_CHANGED")
    return raw.decode()

def preparation_hold(driver,value,collect_folder,identity_refusal):
    validate(driver.store,RUN)
    require(collect_folder is None and identity_refusal is None,"NO_EXECUTION")
    require(value["phase"] in STAGES|{"MODEL_RUNNING","BLOCKED","UPDATE_STATE","COMPLETE"},
            "INTERPRETATION_ONLY")
    if value["phase"]=="UPDATE_STATE":return finish(driver,value)
    if value["phase"]=="COMPLETE":return driver.status()
    return None

def collect(driver,value,scope,host):
    from orchestrator.experiment_collection import artifact
    native=native_results(scope,host)
    oldtypes={"result_tables","validation_result","execution_receipt","execution_manifest",
        "package_manifest","interpretation","interpretation_original","interpretation_format_repair",
        "investigator_next_decision"}
    value["preserved_prior_result_artifacts"]=[r for r in value["artifacts"]if r["type"] in oldtypes]
    value["artifacts"]=[r for r in value["artifacts"]if r["type"] not in oldtypes]
    folder=driver.state/"diagnostics-results";pr.mkdir(folder)
    for name,raw in native["files"].items():
        pr.write_bytes(folder/name,raw)
        artifact(driver,value,"validation_result"if name=="validation.json"else"result_tables",
            "diagnostics-result-"+name,"smoothing/"+name,raw)
    pr.write_bytes(driver.state/"validation.json",encoded(native["validation"]))
    receipt=encoded(native["receipt"]);value["idea2_result_receipt_sha256"]=sha(receipt)
    for kind,name,raw in [
        ("execution_receipt","smoothing-execution-receipt.json",receipt),
        ("execution_manifest","smoothing-execution-manifest.json",encoded({
            "run_id":RUN,"cpu_source":native["receipt"]["cpu_source"],"program_sha256":results.contract.PROGRAM,
            "cpu_only":True,"training":False,"input_files_verified":728})),
        ("package_manifest","smoothing-package-manifest.json",encoded({
            "program_sha256":results.contract.PROGRAM,"scientific_review_sha256":results.contract.REVIEW,
            "implementation_review_sha256":native["receipt"]["implementation_review_sha256"],"package_files_verified":4}))]:
        artifact(driver,value,kind,"diagnostics-"+kind,name,raw)
    verified_by_store(driver.store,value,driver.config,scope,host)

@pr.private_umask
def prepare(root,*,filesystem_root=Path("/")):
    from orchestrator.manual_driver import git
    from orchestrator.analysis_driver import release_identities
    from orchestrator.manual_executor import ManualExecutor,atomic,lock
    from orchestrator.autonomy_accounting import BatchAccounts
    from types import SimpleNamespace
    scope=document();host=Path(filesystem_root);root=Path(root)
    require(host!=Path("/")or os.getuid()==os.getgid()==1003,"SERVICE_OWNER")
    require(not git(root,"status","--porcelain")and git(root,"branch","--show-current")==BRANCH,
            "CLEAN_REVIEWED_SOURCE")
    parent=_path(host,scope["prior"]["parent_lane"]);state=_path(host,scope["new_lane"])
    require(not state.exists()and not state.is_symlink(),"EXISTING_LANE")
    old=scope["prior"]["config"];batch=BatchAccounts(_path(host,old["batch_ledger"]),filesystem_root=host)
    try:
        with lock(parent/"driver.lock"):
            require(not(parent/"HALT").exists()and not(batch.folder/"HALT").exists(),"HALT")
            require(_originals(batch.db,scope,host)==scope["prior"]["global"]["owner"][0],"ACTIVE_OWNER")
            require(not batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),"LIVE_MODEL")
            profile,engine=release_identities(root);require(profile==old["profile_files"],"PROFILE_CHANGED")
            for name,pin in old["engine_files"].items():
                if name not in engine:
                    require(sha((root/name).read_bytes())==pin,"RETAINED_AUTHORITY");engine[name]=pin
            config={**old,"root":str(root),"source":git(root,"rev-parse","HEAD"),"branch":BRANCH,
                "context":str(state/"context"),"workspace_root":str(state.with_name("lane-scientific-workspaces")),
                "engine_files":engine,FIELD:{"schema":"idea2-interpretation/v1","scope_sha256":DOCUMENT_SHA}}
            approved=_approval(config,scope,host)
            config["engine_review"]={"path":str(_path(host,scope["review_directory"])/"report.md"),"sha256":approved}
            # Verify terminal actual results before any new lane is created.
            native_results(scope,host)
            pr.mkdir(state);pr.write_bytes(state/"PREPARE_INTENT.json",encoded({
                "scope_sha256":DOCUMENT_SHA,"source":config["source"],"prior_calls":15,"new_allowance":0}))
            pr.copytree(parent/"context",state/"context")
            pr.copyfile(parent/"preparation-plan.json",state/"preparation-plan.json")
            with sqlite3.connect((parent/"jobs.sqlite").as_uri()+"?mode=ro",uri=True)as original:
                with pr.Connection(state/"jobs.sqlite")as target:original.backup(target)
            atomic(state/"lane.json",config)
            store=ManualExecutor(state/"jobs.sqlite",batch=batch)
            try:
                value=json.loads(scope["prior"]["local"]["manual_state"][0]["payload"])
                value.update(phase="result_interpretation_author",reason=None)
                for key in ("interpretation","next_decision","reviewed_results","pending"):value.pop(key,None)
                value["interventions"].append({"kind":"VALIDATED_IDEA2_INTERPRETATION",
                    "scope_sha256":DOCUMENT_SHA,"original_acceptance_preserved":True})
                collect(SimpleNamespace(state=state,config=config,context=state/"context",store=store),value,scope,host)
                store.db.execute("UPDATE manual_state SET payload=? WHERE id=1",(encoded(value).decode(),))
                _configuration(store,RUN)
                for table in ("manual_account","manual_recoveries"):
                    require([dict(r)for r in store.db.execute("SELECT * FROM "+table)]==scope["prior"]["local"][table],
                            "ACCOUNTING_COPY_CHANGED")
                require(_originals(batch.db,scope,host)==scope["prior"]["global"]["owner"][0],"ORIGINAL_CHANGED")
            finally:store.db.close()
            pr.write_bytes(state/"PREPARED.json",encoded({"status":"PREPARED_NOT_ACTIVATED","prior_calls":15,"model_calls":0}))
            return {"status":"PREPARED_NOT_ACTIVATED","calls_preserved":15,"model_calls":0,"new_allowance":0}
    finally:batch.db.close()

@pr.private_umask
def finish(driver,value):
    from orchestrator.experiment_acceptance import verify
    from orchestrator.manual_driver import write_once
    manifest=verify(driver,value);config,scope,host,approval=_configuration(driver.store,RUN)
    require(json.loads(pr.check(value["next_decision"]).read_bytes())["proposed_action_type"]=="stop",
            "NO_SUCCESSOR_EXECUTION")
    report="# Independently reviewed smoothing interpretation\n\n"+pr.check(value["interpretation"]).read_text()
    report+="\n\nThis accepted saved-output analysis preserves the original item6 acceptance and all calls. It authorizes no successor execution.\n"
    write_once(driver.state/"REPORT.md",report.encode())
    receipt={"schema":"idea2-results-accepted/v1","report_sha256":sha(report.encode()),
        "reviewed_results_sha256":value["reviewed_results"]["sha256"],
        "cpu_execution_receipt_sha256":native_results(scope,host)["receipt"]["execution_receipt_sha256"],
        "scope_sha256":DOCUMENT_SHA,"successor_execution_authorized":False}
    db=driver.store.batch.db;db.execute("BEGIN IMMEDIATE")
    try:
        owner=_originals(db,scope,host)
        require(not db.execute("SELECT 1 FROM autonomy_calls WHERE change_id=? AND status!='COMPLETE'",(RUN,)).fetchone(),
                "UNRESOLVED_CALL")
        old=db.execute("SELECT job,payload FROM events WHERE id=?",(ACCEPTED,)).fetchone()
        require(old is None or(old["job"]==RUN and json.loads(old["payload"])==receipt),"ACCEPTANCE_CHANGED")
        require(owner["status"]==("COMPLETE"if old else"ACTIVE"),"OWNER_COMPLETION")
        db.execute("INSERT OR IGNORE INTO events VALUES(?,?,?)",(ACCEPTED,RUN,encoded(receipt).decode()))
        db.execute("UPDATE autonomy_runs SET status='COMPLETE' WHERE id=?",(RUN,))
        db.execute("COMMIT")
    except BaseException:db.execute("ROLLBACK");raise
    value.update(phase="COMPLETE",operator_review_pending=True);driver.save(value)
    return driver.status()
