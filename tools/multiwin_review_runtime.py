"""One reviewed terminal-review recovery; original driver and confinement retained."""
from pathlib import Path
import argparse, importlib.util, json, os, subprocess, sys
BASE=Path("/opt/research-system/manual-repair-helpers/colab-simple-admission-20261012")
PRIOR=Path("/opt/research-system/manual-repair-helpers/multiwin-shared-guard-20261012")
ROOT=Path("/opt/research-system/manual-repair-helpers/multiwin-review11-20261012")
RECORD=Path("/var/lib/research-system-manual-sprint10-deployment/multiwin-review11-20261012")
ENTRY="tools/multiwin_review_runtime.py"
UNIT="research-multiwin-review11-20261012.service"
CHANGE="multiwin-review11-20261012"
BRANCH="astra/multiwin-review11-20261012"
ADDED=("orchestrator/multiwin_review_completion.py",ENTRY,"tests/test_multiwin_review_completion.py",
       "docs/MULTIWIN_REVIEW11_PRIVATE.json","docs/MULTIWIN_REVIEW11_SCOPE.md")
COMPONENT=("orchestrator/multiwin_shared_guard.py","tools/multiwin_shared_runtime.py",
 "orchestrator/multiwin_local_recovery.py","orchestrator/multiwin_local_allowance.py",
 "tools/multiwin_local_runtime.py","orchestrator/manual_stage.py","orchestrator/review_submission.py",
 "orchestrator/multiwin_tonight.py","orchestrator/manual_driver.py","orchestrator/analysis_driver.py",
 "orchestrator/autonomy_limits.py","orchestrator/manual_executor.py","orchestrator/autonomy_accounting.py")
def require(ok,why):
    if not ok:raise ValueError("MULTIWIN_REVIEW_RUNTIME_"+why)
def sha(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":")).encode()
def load(name,path):
    from orchestrator.manual_host_guard import trusted
    s=importlib.util.spec_from_file_location(name,trusted(path))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def prior():
    require(Path(__import__("orchestrator").__file__).resolve().parent==BASE/"orchestrator","BASE_IMPORT")
    p=load("_installed_accounting_parent",PRIOR/"tools/multiwin_shared_runtime.py")
    a,_=p.authority()
    require(a["source_sha"]=="63da504cf54872be1fb022f36f3206067d42839b"
        and a["report_sha256"]=="b099bf795f3ad5b5f8a9c3b4027c0e8ff3ca7abcf1814f1c70abf68be7c0d921",
        "PRIOR_APPROVAL")
    return p
def reviewed(folder):
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    a=verify_result(trusted(folder));m=json.loads(trusted(folder/"packet-manifest.json").read_bytes())
    require(a["verdict"]=="APPROVE"and a["change_id"]==CHANGE
        and json.loads(trusted(folder/"report.md").read_bytes())["findings"]==[],"APPROVE")
    require(set(ADDED)|set(COMPONENT)<=set(m["source_files"]),"WHOLE_COMPONENT")
    return a,m
def unit_bytes(p):
    from orchestrator.manual_host_guard import trusted
    p.authority()
    raw=trusted(Path("/etc/systemd/system")/p.UNIT).read_bytes()
    # The only service directive change is its entry point.
    old=("ExecStart=/usr/bin/python3 -s -B "+str(PRIOR/p.ENTRY)+" run"+chr(10)).encode()
    new=("ExecStart=/usr/bin/python3 -s -B "+str(ROOT/ENTRY)+" run"+chr(10)).encode()
    require(raw.count(old)==1,"EXACT_PRIOR_COMMAND")
    return raw.replace(old,new)
def held(p):
    p.held(p.prior())
    for unit in (p.UNIT,UNIT):
        v=dict(x.split("=",1)for x in subprocess.check_output(
            ["systemctl","show",unit,"-p","MainPID","-p","ActiveState"],text=True).splitlines())
        require(v["MainPID"]=="0"and v["ActiveState"]in{"inactive","failed"},"LIVE_UNIT")
def install(source,review):
    from orchestrator.manual_host_guard import trusted
    from tools.install_preparation_branch_repair import put,mkdir,OWNER_CHECK
    from tools.install_preparation_runtime import standalone_git,verify_units
    import shutil
    require(os.getuid()==0 and sys.flags.no_user_site,"ROOT_INSTALL")
    source=trusted(source);review=trusted(review);a,m=reviewed(review);standalone_git(source)
    git=lambda *args:subprocess.check_output(["git",*args],cwd=source,text=True).strip()
    require(git("rev-parse","HEAD")==a["source_sha"]and git("branch","--show-current")==BRANCH
        and not git("status","--porcelain"),"CLEAN_SOURCE")
    require((source/ENTRY).read_bytes()==Path(__file__).read_bytes(),"INSTALLER_BYTES")
    for n,pin in m["source_files"].items():require(sha(trusted(source/n).read_bytes())==pin,"SOURCE_PIN")
    p=prior();held(p);_,shared_parent=p.authority();_,old=shared_parent.authority();_,parent,_=old.authority()
    require(a["runtime_sha256"]==sha(trusted(parent.metadata()[1]["runtime"]).read_bytes()),"SAME_RUNTIME")
    require(json.loads(subprocess.check_output(
        ["runuser","-u","partho","--","python3","-s","-B","-c",OWNER_CHECK],text=True))["status"]=="NO_RUNNING_CALL","LIVE_MODEL")
    for dest in(ROOT,RECORD,Path("/etc/systemd/system")/UNIT):
        trusted(dest.parent);require(not dest.exists()and not dest.is_symlink(),"INSTALL_EXISTS")
        require(shutil.disk_usage(dest.parent).free>=8*2**30,"DISK_STOP")
    unit=unit_bytes(p);verify_units({Path("/etc/systemd/system")/UNIT:unit})
    mkdir(RECORD);put(RECORD/"INSTALL_INTENT.json",canonical({"source":a["source_sha"],"review":a["report_sha256"]}))
    mkdir(ROOT)
    for n in ADDED:put(ROOT/n,trusted(source/n).read_bytes())
    for f in review.iterdir():
        require(f.is_file()and not f.is_symlink(),"FLAT_REVIEW")
        put(RECORD/"review"/f.name,trusted(f).read_bytes())
    put(Path("/etc/systemd/system")/UNIT,unit)
    put(RECORD/"INSTALLED.json",canonical({"source":a["source_sha"],"review_sha256":a["report_sha256"],
        "files":{n:m["source_files"][n]for n in ADDED},"unit_sha256":sha(unit)}))
    subprocess.run(["systemctl","daemon-reload"],check=True)
    return{"status":"INSTALLED_HELD_ZERO_CALL","model_calls":0}
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
def service(action):
    from orchestrator.manual_executor import lock,atomic
    from orchestrator import private_records as pr,manual_stage
    a,p=authority()
    old,_,parent,q,b,d,restore=p.prior().connect()
    helper=load("_reviewed_shared_guard",PRIOR/"orchestrator/multiwin_shared_guard.py")
    undo=helper.bind(d,lambda:q.guard(d,b,old))
    completion=load("_reviewed_completion",ROOT/"orchestrator/multiwin_review_completion.py")
    frozen=completion.document(ROOT);command_restore=lambda:None
    folder=d.state/(CHANGE+"-qualification")
    try:
        if action=="status":return{**d.status(),"transition":parent.snapshot(d),"effective_run_limit":24}
        if action=="recover":
            held(p)
            with lock(d.state/"driver.lock"):return completion.recover(d,frozen,a["report_sha256"])
        require(action=="run"and bool(os.environ.get("INVOCATION_ID")),"NATIVE_INVOCATION")
        op=json.loads((RECORD/"OPERATION.json").read_bytes())
        require(op["source"]==a["source_sha"]and op["review_sha256"]==a["report_sha256"]
            and op["transition"]==parent.snapshot(d),"STATE_BOUND")
        if op["mode"]=="probe":
            with lock(d.state/"driver.lock"):
                q.guard(d,b,old);completion.granted(d,frozen,a["report_sha256"])
                before=parent.snapshot(d);d.guard();value=d.current()
                require(value["phase"]=="run_spec_review"and value["rounds"]["run_spec_review"]==10
                    and value["rounds"]["run_spec_author"]==12,"REVIEW11_STATE")
                require(not folder.exists()and not folder.is_symlink(),"PROBE_EXISTS")
                pr.mkdir(folder);work=folder/"reviewer"
                body,measurement=d.prepare_input(value,"run_spec_review",work)
                pr.write_text(work/"prompt.md",body);atomic(work/"input-measurement.json",measurement)
                from orchestrator import review_submission as rs
                submission=rs.prepare(work,"scientific",{"call_id":completion.NEXT,"run_id":d.config["run_id"],
                    "stage":"run_spec_review","source_sha":d.config["source"],
                    "runtime_sha256":d.config["clients"]["runtime_config_sha256"],"input_sha256":sha(body.encode())})
                command_restore=completion.bind_command(d,frozen,a["report_sha256"],probe=True)
                argv=manual_stage.reviewer_command(work,"run_spec_review")
                require(argv[argv.index("--max-turns")+1]=="60","REVIEW_TURNS")
                atomic(work/"review-command-qualification.json",{"argv":argv,"submission":submission})
                manual_stage.data_access_guard(work,"run_spec_review")
                require(manual_stage.preflight()==d.config["clients"],"CLIENTS_CHANGED")
                transport=manual_stage.transport_check(work,"run_spec_review",sha(body.encode()))
                require(transport["model_client_launched"]is False and parent.snapshot(d)==before,"PROBE_MUTATION")
                result={"status":"PASS","source":a["source_sha"],"review_sha256":a["report_sha256"],
                    "transition":before,"model_calls":0,"review_attempt":11,"max_turns":60,"transport":transport}
                atomic(folder/"COMPLETE.json",result);return result
        require(op["mode"]=="advance","MODE")
        passed=json.loads(pr.check(folder/"COMPLETE.json").read_bytes())
        require(passed["status"]=="PASS"and passed["source"]==a["source_sha"]
            and passed["review_sha256"]==a["report_sha256"],"PROBE_REQUIRED")
        q.guard(d,b,old);completion.granted(d,frozen,a["report_sha256"])
        command_restore=completion.bind_command(d,frozen,a["report_sha256"])
        return d.advance()
    finally:command_restore();undo();restore();d.store.db.close();d.store.batch.db.close()
def start(mode,transition):
    import fcntl
    from tools.install_preparation_branch_repair import put,OWNER_CHECK
    require(os.getuid()==0 and sys.flags.no_user_site and mode in{"probe","advance"},"ROOT_START")
    a,p=authority()
    with(RECORD/"start.lock").open("a")as stream:
        fcntl.flock(stream,fcntl.LOCK_EX);held(p)
        _,shared_parent=p.authority();_,old=shared_parent.authority();_,parent,_=old.authority();runtime=parent.metadata()[1]["runtime"]
        status=json.loads(subprocess.check_output(
            ["runuser","-u","partho","--","env","RESEARCH_MANUAL_RUNTIME_CONFIG="+runtime,
             "PYTHONPATH="+str(BASE),"python3","-s","-B",str(ROOT/ENTRY),"status"],text=True))
        allowed={"run_spec_review"}if mode=="probe"else{"run_spec_review","MODEL_RUNNING"}
        require(status["transition"]==transition and status["phase"]in allowed,"STATE_CHANGED")
        require(json.loads(subprocess.check_output(
            ["runuser","-u","partho","--","python3","-s","-B","-c",OWNER_CHECK],text=True))["status"]=="NO_RUNNING_CALL","LIVE_MODEL")
        intent=RECORD/"operations"/(mode+"-"+transition+".json")
        require(not intent.exists()and not intent.is_symlink(),"START_ALREADY_ATTEMPTED")
        value={"mode":mode,"transition":transition,"source":a["source_sha"],"review_sha256":a["report_sha256"]}
        put(intent,canonical(value));put(RECORD/"OPERATION.next",canonical(value));os.replace(RECORD/"OPERATION.next",RECORD/"OPERATION.json")
        subprocess.run(["systemctl","start","--no-block",UNIT],check=True)
        return{"status":"START_REQUESTED_RECONCILE","mode":mode,"unit":UNIT}
def main():
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["install","recover","status","run","start"])
    parser.add_argument("--source",type=Path);parser.add_argument("--review",type=Path)
    parser.add_argument("--mode",choices=["probe","advance"]);parser.add_argument("--transition")
    args=parser.parse_args()
    if args.action=="install":
        require(args.source is not None and args.review is not None and args.mode is None and args.transition is None,"INSTALL_ARGS")
        return install(args.source,args.review)
    require(args.source is None and args.review is None,"NO_SOURCE_OVERRIDE")
    if args.action=="start":return start(args.mode,args.transition)
    require(args.mode is None and args.transition is None,"NO_OPERATION_OVERRIDE")
    return service(args.action)
if __name__=="__main__":
    os.umask(0o077);sys.path.insert(0,str(BASE));print(json.dumps(main(),sort_keys=True))
