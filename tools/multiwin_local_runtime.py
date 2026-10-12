"""Reviewed allowance connector; retain the installed scientific runtime."""
from pathlib import Path
import argparse, importlib.util, json, os, subprocess, sys
BASE=Path("/opt/research-system/manual-repair-helpers/colab-simple-admission-20261012")
PRIOR=Path("/opt/research-system/manual-repair-helpers/multiwin-tonight-continuation-20261012")
ROOT=Path("/opt/research-system/manual-repair-helpers/multiwin-local-accounting-20261012")
RECORD=Path("/var/lib/research-system-manual-sprint10-deployment/multiwin-local-accounting-20261012")
ENTRY="tools/multiwin_local_runtime.py"
UNIT="research-multiwin-local-accounting-20261012.service"
CHANGE="multiwin-local-accounting-20261012"
BRANCH="astra/multiwin-local-accounting-20261012"
ADDED=("orchestrator/multiwin_local_allowance.py","orchestrator/multiwin_local_recovery.py",
       ENTRY,"docs/MULTIWIN_LOCAL_ADMISSION_PRIVATE.json","docs/MULTIWIN_LOCAL_ACCOUNTING_SCOPE.md",
       "tests/test_multiwin_local_allowance.py","tests/test_multiwin_local_recovery.py")
COMPONENT=("orchestrator/manual_executor.py","orchestrator/manual_driver.py",
           "orchestrator/dispatch_limiter.py","orchestrator/autonomy_limits.py",
           "orchestrator/item4_scoped_calls.py","orchestrator/autonomy_accounting.py",
           "orchestrator/multiwin_tonight.py","tools/multiwin_tonight_runtime.py")
def require(ok,why):
    if not ok:raise ValueError("MULTIWIN_LOCAL_RUNTIME_"+why)
def sha(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":")).encode()
def load(name,path):
    from orchestrator.manual_host_guard import trusted
    s=importlib.util.spec_from_file_location(name,trusted(path))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def prior():
    require(Path(__import__("orchestrator").__file__).resolve().parent==BASE/"orchestrator","BASE_IMPORT")
    p=load("_installed_prior_multiwin",PRIOR/"tools/multiwin_tonight_runtime.py")
    a,_,_=p.authority()
    require(a["source_sha"]=="83ef32d51e1ffd3f105fb5df073d27a4dd5164d0"
        and a["report_sha256"]=="6fd1112340bfa87ac9e788bbd892c56909f4246b12fd325142e36eb53b0e6d33"
        and a["verdict"]=="APPROVE","PRIOR_APPROVAL")
    return p
def reviewed(folder):
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    folder=trusted(folder);a=verify_result(folder)
    m=json.loads(trusted(folder/"packet-manifest.json").read_bytes())
    require(a["verdict"]=="APPROVE"and a["change_id"]==CHANGE
        and json.loads(trusted(folder/"report.md").read_bytes())["findings"]==[],"INDEPENDENT_APPROVE")
    require(set(ADDED)|set(COMPONENT)<=set(m["source_files"]),"WHOLE_COMPONENT")
    return a,m
def unit_bytes(p):
    _,parent,_=p.authority();raw=p.unit_bytes(parent)
    old=("/usr/bin/python3 -s -B "+str(PRIOR/p.ENTRY)+" run").encode()
    new=("/usr/bin/python3 -s -B "+str(ROOT/ENTRY)+" run").encode()
    tail=bytes([10])
    require(raw.count(b"ExecStart="+old+tail)==1,"OLD_COMMAND")
    return raw.replace(b"ExecStart="+old+tail,b"ExecStart="+new+tail)
def held(p):
    _,parent,_=p.authority();p.held(parent)
    v=dict(x.split("=",1)for x in subprocess.check_output(
        ["systemctl","show",UNIT,"-p","MainPID","-p","ActiveState"],text=True).splitlines())
    require(v["MainPID"]=="0"and v["ActiveState"]in{"inactive","failed"},"LIVE_UNIT")
def source_qualify(source,review):
    """Read-only service-UID proof, never a generic pending-call exception."""
    from orchestrator.manual_host_guard import trusted
    import sqlite3
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,"SERVICE_OWNER")
    a,m=reviewed(review)
    for n in ADDED:require(sha(trusted(source/n).read_bytes())==m["source_files"][n],"SOURCE_PIN")
    p=prior();q=load("_candidate_exact_terminal_proof",source/"orchestrator/multiwin_local_recovery.py")
    b=q.document(source)
    with sqlite3.connect((Path(b["config"]["batch_ledger"])/"jobs.sqlite").as_uri()+"?mode=ro",uri=True)as db:
        db.row_factory=sqlite3.Row;db.execute("PRAGMA query_only=ON");db.execute("BEGIN")
        require([r["id"]for r in db.execute("SELECT id FROM autonomy_calls WHERE status='RUNNING'")]==[q.CALL],
                "ONLY_EXACT_PREMODEL_RESERVATION")
        return q.qualify(db,b,p)
def install(source,review):
    from orchestrator.manual_host_guard import trusted
    from tools.install_preparation_branch_repair import put,mkdir
    from tools.install_preparation_runtime import standalone_git,verify_units
    import shutil
    require(os.getuid()==0 and sys.flags.no_user_site,"ROOT_INSTALL")
    source=trusted(source);review=trusted(review);a,m=reviewed(review);standalone_git(source)
    git=lambda *args:subprocess.check_output(["git",*args],cwd=source,text=True).strip()
    require(git("rev-parse","HEAD")==a["source_sha"]and git("branch","--show-current")==BRANCH
        and not git("status","--porcelain"),"CLEAN_REVIEWED_SOURCE")
    require((source/ENTRY).read_bytes()==Path(__file__).read_bytes(),"INSTALLER_BYTES")
    for n,pin in m["source_files"].items():require(sha(trusted(source/n).read_bytes())==pin,"SOURCE_CHANGED")
    p=prior();held(p);_,parent,_=p.authority()
    require(a["runtime_sha256"]==sha(trusted(parent.metadata()[1]["runtime"]).read_bytes()),"SAME_RUNTIME")
    for dest in(ROOT,RECORD,Path("/etc/systemd/system")/UNIT):
        trusted(dest.parent);require(not dest.exists()and not dest.is_symlink(),"INSTALL_EXISTS")
        require(shutil.disk_usage(dest.parent).free>=8*2**30,"DISK_STOP")
    proof=json.loads(subprocess.check_output(
        ["runuser","-u","partho","--","env","PYTHONPATH="+str(BASE),"python3","-s","-B",
         str(source/ENTRY),"qualify","--source",str(source),"--review",str(review)],text=True))
    require(proof["model_client_launched"]is False and proof["scientific_successor"]is False,"EXACT_TERMINAL_PROOF")
    unit=unit_bytes(p);verify_units({Path("/etc/systemd/system")/UNIT:unit})
    mkdir(RECORD);put(RECORD/"INSTALL_INTENT.json",canonical({"source":a["source_sha"],"review":a["report_sha256"],"proof":proof}))
    mkdir(ROOT)
    for n in ADDED:put(ROOT/n,trusted(source/n).read_bytes())
    for f in review.iterdir():
        require(f.is_file()and not f.is_symlink(),"FLAT_REVIEW")
        put(RECORD/"review"/f.name,trusted(f).read_bytes())
    put(Path("/etc/systemd/system")/UNIT,unit)
    put(RECORD/"INSTALLED.json",canonical({"source":a["source_sha"],"review_sha256":a["report_sha256"],
        "files":{n:m["source_files"][n]for n in ADDED},"unit_sha256":sha(unit)}))
    subprocess.run(["systemctl","daemon-reload"],check=True)
    return{"status":"INSTALLED_HELD_NO_RECONCILIATION","model_calls":0}
def authority():
    from orchestrator.manual_host_guard import trusted
    require(Path(__file__).resolve()==ROOT/ENTRY,"INSTALLED_ENTRY")
    a,m=reviewed(RECORD/"review");p=prior()
    expected={"source":a["source_sha"],"review_sha256":a["report_sha256"],
              "files":{n:m["source_files"][n]for n in ADDED},"unit_sha256":sha(unit_bytes(p))}
    require(json.loads(trusted(RECORD/"INSTALLED.json").read_bytes())==expected,"RECEIPT")
    for n in ADDED:require(sha(trusted(ROOT/n).read_bytes())==m["source_files"][n],"INSTALLED_BYTES")
    require(trusted(Path("/etc/systemd/system")/UNIT).read_bytes()==unit_bytes(p),"UNIT_CHANGED")
    return a,p
def connect():
    a,p=authority()
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,"SERVICE_OWNER")
    _,parent,old_helper,driver=p.connect()
    q=load("_local_exact_recovery",ROOT/"orchestrator/multiwin_local_recovery.py");b=q.document(ROOT)
    bridge=load("_local_allowance_bridge",ROOT/"orchestrator/multiwin_local_allowance.py")
    def grant(store):
        require(store is driver.store,"EXACT_STORE")
        old_helper.grant(driver,old_helper.frozen(PRIOR),b["prior_review_sha256"])
        q.guard(driver,b,a)
    restore=bridge.bind(driver.config,q.PIN,a["report_sha256"],grant)
    return a,p,parent,q,b,driver,restore
def probe(a,parent,q,b,driver):
    from orchestrator import manual_stage,private_records as pr
    from orchestrator.manual_executor import atomic
    q.guard(driver,b,a);driver.guard();before=parent.snapshot(driver);value=driver.current()
    require(value["phase"]=="run_spec_author"and value["rounds"]["run_spec_author"]==11,"AUTHOR12_STATE")
    folder=driver.state/(q.EVENT+"-qualification")
    require(not folder.exists()and not folder.is_symlink(),"PROBE_EXISTS")
    pr.mkdir(folder);work=folder/"author"
    body,measurement=driver.prepare_input(value,"run_spec_author",work)
    pr.write_text(work/"prompt.md",body);atomic(work/"input-measurement.json",measurement)
    manual_stage.data_access_guard(work,"run_spec_author")
    require(manual_stage.preflight()==driver.config["clients"],"CLIENTS_CHANGED")
    transport=manual_stage.transport_check(work,"run_spec_author",sha(body.encode()))
    require(transport["model_client_launched"]is False and parent.snapshot(driver)==before,"PROBE_MUTATION")
    result={"status":"PASS","source":a["source_sha"],"review_sha256":a["report_sha256"],
            "transition":before,"model_calls":0,"author_attempt":12,"transport":transport}
    atomic(folder/"COMPLETE.json",result);return result
def service(action):
    from orchestrator.manual_executor import lock
    a,p,parent,q,b,driver,restore=connect()
    try:
        if action=="status":return{**driver.status(),"transition":parent.snapshot(driver),"effective_run_limit":24}
        if action=="recover":
            held(p)
            with lock(driver.state/"driver.lock"):return q.recover(driver,b,a,p)
        require(action=="run"and bool(os.environ.get("INVOCATION_ID")),"NATIVE_INVOCATION")
        op=json.loads((RECORD/"OPERATION.json").read_bytes())
        require(op["source"]==a["source_sha"]and op["review_sha256"]==a["report_sha256"]
                and op["transition"]==parent.snapshot(driver),"STATE_BOUND")
        if op["mode"]=="probe":
            with lock(driver.state/"driver.lock"):return probe(a,parent,q,b,driver)
        require(op["mode"]=="advance","MODE")
        passed=json.loads((driver.state/(q.EVENT+"-qualification")/"COMPLETE.json").read_bytes())
        require(passed["status"]=="PASS"and passed["source"]==a["source_sha"],"PROBE_REQUIRED")
        q.guard(driver,b,a)
        return driver.advance()
    finally:restore();driver.store.db.close();driver.store.batch.db.close()
def start(mode,transition):
    import fcntl
    from tools.install_preparation_branch_repair import put,OWNER_CHECK
    require(os.getuid()==0 and sys.flags.no_user_site and mode in{"probe","advance"},"ROOT_START")
    a,p=authority()
    with(RECORD/"start.lock").open("a")as stream:
        fcntl.flock(stream,fcntl.LOCK_EX);held(p);_,parent,_=p.authority();runtime=parent.metadata()[1]["runtime"]
        status=json.loads(subprocess.check_output(
            ["runuser","-u","partho","--","env","RESEARCH_MANUAL_RUNTIME_CONFIG="+runtime,
             "PYTHONPATH="+str(BASE),"python3","-s","-B",str(ROOT/ENTRY),"status"],text=True))
        allowed={"run_spec_author"}if mode=="probe"else{"run_spec_author","run_spec_review","MODEL_RUNNING"}
        require(status["transition"]==transition and status["phase"]in allowed,"STATE_CHANGED")
        require(json.loads(subprocess.check_output(
            ["runuser","-u","partho","--","python3","-s","-B","-c",OWNER_CHECK],text=True))["status"]=="NO_RUNNING_CALL","LIVE_MODEL")
        intent=RECORD/"operations"/(mode+"-"+transition+".json")
        require(not intent.exists()and not intent.is_symlink(),"START_ALREADY_ATTEMPTED")
        value={"mode":mode,"transition":transition,"source":a["source_sha"],"review_sha256":a["report_sha256"]}
        put(intent,canonical(value));put(RECORD/"OPERATION.next",canonical(value))
        os.replace(RECORD/"OPERATION.next",RECORD/"OPERATION.json")
        subprocess.run(["systemctl","start","--no-block",UNIT],check=True)
        return{"status":"START_REQUESTED_RECONCILE","mode":mode,"unit":UNIT}
def main():
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["install","qualify","status","recover","run","start"])
    parser.add_argument("--source",type=Path);parser.add_argument("--review",type=Path)
    parser.add_argument("--mode",choices=["probe","advance"]);parser.add_argument("--transition")
    args=parser.parse_args()
    if args.action in{"install","qualify"}:
        require(args.source is not None and args.review is not None and args.mode is None and args.transition is None,"SOURCE_ARGS")
        return install(args.source,args.review)if args.action=="install"else source_qualify(args.source,args.review)
    require(args.source is None and args.review is None,"NO_SOURCE_OVERRIDE")
    if args.action=="start":return start(args.mode,args.transition)
    require(args.mode is None and args.transition is None,"NO_OPERATION_OVERRIDE")
    return service(args.action)
if __name__=="__main__":
    os.umask(0o077);sys.path.insert(0,str(BASE));print(json.dumps(main(),sort_keys=True))
