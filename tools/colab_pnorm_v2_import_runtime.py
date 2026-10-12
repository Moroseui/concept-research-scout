"""Supply the single missing feedback import; preserve the installed lane and all checks."""
from pathlib import Path
import argparse, importlib.util, json, os, subprocess, sys
BASE=Path("/opt/research-system/manual-repair-helpers/colab-pnorm-v2-question-20261012")
PRIOR=Path("/opt/research-system/manual-repair-helpers/colab-pnorm-v2-question-20261012")
ROOT=Path("/opt/research-system/manual-repair-helpers/colab-pnorm-v2-feedback-import-20261012")
RECORD=Path("/var/lib/research-system-manual-sprint10-deployment/colab-pnorm-v2-feedback-import-20261012")
ENTRY="tools/colab_pnorm_v2_import_runtime.py"
UNIT="research-colab-pnorm-v2-feedback-import-20261012.service"
CHANGE="colab-pnorm-v2-feedback-import-20261012"
BRANCH="astra/manual-colab-pnorm-v2-question-20261012"
ADDED=("orchestrator/colab_pnorm_v2_feedback.py",ENTRY,
       "tests/test_colab_pnorm_v2_feedback.py","tests/test_colab_pnorm_v2_import_runtime.py",
       "docs/PNORM_V2_FEEDBACK_IMPORT_PRIVATE.json","docs/PNORM_V2_FEEDBACK_IMPORT_SCOPE.md")
COMPONENT=("orchestrator/colab_arm_question.py","tools/colab_pnorm_v2_runtime.py",
 "orchestrator/colab_pnormct_policy.py","orchestrator/analysis_driver.py",
 "orchestrator/manual_driver.py","orchestrator/manual_executor.py",
 "orchestrator/manual_stage.py","orchestrator/autonomy_accounting.py","orchestrator/autonomy_limits.py")
FROZEN_PIN='2c2d5235399d94aabf9e0de7fd79dd11eeb07f98976f5af1b7c91de392d0a658'
def require(ok,why):
    if not ok:raise ValueError("PNORM_V2_FEEDBACK_IMPORT_"+why)
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
    p=load("_approved_interpretation_runtime",BASE/"tools/colab_pnorm_v2_runtime.py")
    a=p.authority()
    require(a["source_sha"]=="dd83f3c5c96d5f903aed40c4e56f8f2b27b39a8a"
        and a["report_sha256"]=="1d5f9280c2369c87ca7011f1593ae55ff83f499882d73cde3299eb8b12cb2574","PRIOR_APPROVAL")
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
    raw=trusted(Path("/etc/systemd/system")/p.metadata()[1]["unit"]).read_bytes()
    # The only service directive change is its entry point.
    old=("ExecStart=/usr/bin/python3 -s -B "+str(PRIOR/p.ENTRY)+" run"+chr(10)).encode()
    new=("ExecStart=/usr/bin/python3 -s -B "+str(ROOT/ENTRY)+" run"+chr(10)).encode()
    require(raw.count(old)==1,"EXACT_PRIOR_COMMAND")
    return raw.replace(old,new)
def held(p):
    p.held_prior()
    for unit in (p.metadata()[1]["unit"],UNIT):
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
    p=prior();held(p)
    require(a["runtime_sha256"]==sha(trusted(p.metadata()[1]["runtime"]).read_bytes()),"SAME_RUNTIME")
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
def corrected_feedback(root=ROOT,base=BASE):
    from orchestrator.manual_host_guard import trusted
    old=trusted(base/"orchestrator/colab_pnorm_v2_feedback.py").read_bytes()
    new=trusted(root/"orchestrator/colab_pnorm_v2_feedback.py").read_bytes()
    line=("from pathlib import Path"+chr(10)).encode()
    require(old.count(line)==1 and new==old.replace(line,line+b"import json"+bytes([10]),1),
            "ONLY_MISSING_IMPORT_REPAIR")
    return load("_approved_pnorm_v2_feedback",root/"orchestrator/colab_pnorm_v2_feedback.py")

def checkpoint(driver,initial=False):
    from orchestrator.manual_host_guard import trusted
    raw=trusted(ROOT/"docs/PNORM_V2_FEEDBACK_IMPORT_PRIVATE.json").read_bytes()
    require(sha(raw)==FROZEN_PIN,"FROZEN_BINDING")
    b=json.loads(raw)
    require(b["schema"]=="pnorm-v2-feedback-import/v1" and b["calls"]==b["new_allowance"]==0,
            "ZERO_CALL_REPAIR")
    require(str(driver.state)==b["lane"] and driver.config["run_id"]==b["run_id"]
        and driver.config["source"]==b["source"]
        and sha((driver.state/"lane.json").read_bytes())==b["config_sha256"],"ORIGINAL_CONFIG")
    if initial:
        require(dict(driver.store.db.execute("SELECT *FROM manual_state WHERE id=1").fetchone())==b["state_row"]
            and not driver.store.db.execute("SELECT 1 FROM manual_calls").fetchone()
            and not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE change_id=?",(b["run_id"],)).fetchone()
            and dict(driver.store.batch.db.execute("SELECT *FROM autonomy_runs WHERE id=?",(b["run_id"],)).fetchone())==b["owner"],
            "EXACT_INITIAL_STATE")
    return b

def service(action):
    from orchestrator import colab_arm_question as q,manual_stage,private_records as pr,colab_pnormct_policy
    from orchestrator.manual_executor import lock,atomic
    from orchestrator.analysis_driver import AnalysisDriver
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,"SERVICE_OWNER")
    a,p=authority();scope,n=p.metadata()
    require(os.environ.get("RESEARCH_MANUAL_RUNTIME_CONFIG")==n["runtime"],"SAME_RUNTIME")
    p.held_prior();p.connect_qualifier();colab_pnormct_policy.connect()
    os.environ["GIT_CONFIG_COUNT"]="1";os.environ["GIT_CONFIG_KEY_0"]="safe.directory";os.environ["GIT_CONFIG_VALUE_0"]=str(BASE)
    helper=corrected_feedback()
    d=helper.prepared(AnalysisDriver)(scope["new_lane"])
    folder=d.state.parent/"qualification-feedback-import"
    try:
        q.validate(d.store,q.RUN);checkpoint(d)
        if action=="status":return {**d.status(),"transition":p.snapshot(d)}
        require(action=="run"and bool(os.environ.get("INVOCATION_ID")),"NATIVE_INVOCATION")
        op=json.loads((RECORD/"OPERATION.json").read_bytes())
        require(op["source"]==a["source_sha"]and op["review_sha256"]==a["report_sha256"]
            and op["transition"]==p.snapshot(d),"STATE_BOUND")
        if op["mode"]=="probe":
            with lock(d.state/"driver.lock"):
                checkpoint(d,initial=True);before=p.snapshot(d);d.guard();value=d.current()
                from orchestrator import manual_recovery
                require(value["phase"]=="run_spec_author" and value["rounds"]=={} and
                    d.model_round_number(value)==1 and
                    manual_recovery.role_limit(d.store,q.RUN,"run_spec_author")==1 and
                    manual_recovery.role_limit(d.store,q.RUN,"run_spec_review")==4,"INITIAL_ADMISSION")
                allowance=q.batch_allowance(d.store.batch,q.document())
                require(allowance["colab_allocation_used"]==9,"UNCHANGED_ALLOCATION")
                require(not folder.exists()and not folder.is_symlink(),"PROBE_EXISTS")
                pr.mkdir(folder);work=folder/"author"
                body,measurement=d.prepare_input(value,"run_spec_author",work)
                pr.write_text(work/"prompt.md",body);atomic(work/"input-measurement.json",measurement)
                manual_stage.data_access_guard(work,"run_spec_author")
                require(manual_stage.preflight()==d.config["clients"],"CLIENTS_CHANGED")
                require(manual_stage.scientific_stage_timeout("run_spec_author")==1800,"AUTHOR_TIMEOUT")
                transport=[manual_stage.transport_check(work,stage,sha(body.encode()))
                    for stage in ("run_spec_author","run_spec_review")]
                require(all(t["model_client_launched"]is False for t in transport)and p.snapshot(d)==before,"PROBE_MUTATION")
                result={"status":"PASS","source":a["source_sha"],"review_sha256":a["report_sha256"],
                    "transition":before,"model_calls":0,"allocation":allowance,"transport":transport}
                atomic(folder/"COMPLETE.json",result);return result
        require(op["mode"]=="advance","MODE")
        passed=json.loads(pr.check(folder/"COMPLETE.json").read_bytes())
        require(passed["status"]=="PASS"and passed["source"]==a["source_sha"]
            and passed["review_sha256"]==a["report_sha256"],"PROBE_REQUIRED")
        require(d.current()["phase"]in q.STAGES|{"MODEL_RUNNING"},"PREPARATION_STAGES_ONLY")
        return d.advance()
    finally:d.store.db.close();d.store.batch.db.close()
def start(mode,transition):
    import fcntl
    from tools.install_preparation_branch_repair import put,OWNER_CHECK
    require(os.getuid()==0 and sys.flags.no_user_site and mode in{"probe","advance"},"ROOT_START")
    a,p=authority()
    with(RECORD/"start.lock").open("a")as stream:
        fcntl.flock(stream,fcntl.LOCK_EX);held(p)
        runtime=p.metadata()[1]["runtime"]
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
        put(intent,canonical(value));put(RECORD/"OPERATION.next",canonical(value));os.replace(RECORD/"OPERATION.next",RECORD/"OPERATION.json")
        subprocess.run(["systemctl","start","--no-block",UNIT],check=True)
        return{"status":"START_REQUESTED_RECONCILE","mode":mode,"unit":UNIT}
def main():
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["install","status","run","start"])
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
