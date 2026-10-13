"""Candidate fixed entry-point patch for the existing L service.

Only ExecStart changes. Original source, unit, lane, owner, calls, account,
transport, confinement and per-run limits are retained. No new executor.
"""
from pathlib import Path
import argparse, importlib.util, json, os, subprocess, sys
BASE = Path("/opt/research-system/manual-repair-helpers/colab-l-question-20261013")
ROOT = Path("/opt/research-system/manual-repair-helpers/l-funded-continuation-20261013")
RECORD = Path("/var/lib/research-system-manual-sprint10-deployment/l-funded-continuation-20261013")
ENTRY = "tools/l_funded_runtime.py"
CHANGE = "l-funded-continuation-20261013"
REVIEW_CHANGE = "l-funded-terminal-routing-20261013"
BRANCH = "astra/l-funded-continuation-20261013"
UNIT = "research-colab-l-question-20261013.service"
DROP = Path("/etc/systemd/system")/(UNIT+".d")/"l-funded.conf"
ADDED = {'orchestrator/l_funded_history.py', 'tools/l_funded_runtime.py', 'docs/SCIENTIFIC_BATCH140_OPERATOR_APPROVAL.txt', 'docs/L_FUNDED_BASELINE_PRIVATE.json', 'tests/test_l_funded_runtime.py', 'docs/L_FUNDED_SCOPE.md', 'tests/test_l_funded_history.py', 'docs/L_FUNDED_CHECKPOINT_PRIVATE.json', 'docs/SCIENTIFIC_BATCH140_OPERATOR_RECORD_PRIVATE.json', 'tests/test_scientific_batch140.py', 'orchestrator/scientific_batch140.py', 'docs/SCIENTIFIC_BATCH140_PRIVATE.json', 'docs/L_FUNDED_AUTHOR_TASK.md', 'tests/test_l_funded_continuation.py', 'orchestrator/l_funded_continuation.py', 'docs/SCIENTIFIC_BATCH140_OPERATOR_QUESTION.txt'}
REQUIRED = ADDED | {'orchestrator/manual_context.py', 'orchestrator/colab_pnormct_policy.py', 'orchestrator/autonomy_limits.py', 'tools/colab_l_runtime.py', 'orchestrator/manual_stage.py', 'orchestrator/manual_executor.py', 'orchestrator/preparation_followup.py', 'orchestrator/analysis_driver.py', 'orchestrator/author_revision_accounting.py', 'orchestrator/colab_pnorm_v2_feedback.py', 'orchestrator/notebook_synthetic_harness.py', 'orchestrator/manual_driver.py', 'orchestrator/colab_arm_question.py', 'orchestrator/autonomy_accounting.py', 'tests/test_colab_arm_question.py', 'orchestrator/notebook_revision.py'}
def require(ok, why):
    if not ok: raise ValueError("L_FUNDED_RUNTIME_" + why)
def sha(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()
def encoded(v): return json.dumps(v, sort_keys=True, separators=(",", ":")).encode()
def load(name, path):
    from orchestrator.manual_host_guard import trusted
    spec=importlib.util.spec_from_file_location(name,trusted(path))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def parent():
    require(Path(__import__("orchestrator").__file__).resolve().parent == BASE/"orchestrator", "BASE_IMPORT")
    p=load("_l_original_runtime",BASE/"tools/colab_l_runtime.py")
    a=p.authority()
    require(a["source_sha"]=="b1249aaf4f9782c6d60270a28e8e787385211ce5"
            and a["report_sha256"]=="ee2d22aadbf82345c8d8b2301cb6420e254e14464292a8ef72059c7357a2a3f0",
            "ORIGINAL_APPROVAL")
    return p
def drop_bytes():
    return ("[Service]\nExecStart=\nExecStart=/usr/bin/python3 -s -B "+str(ROOT/ENTRY)+" run\n").encode()
def properties():
    names=("FragmentPath","DropInPaths","ExecStart","ExecStartPre","ExecStopPost","User","Group",
           "Environment","WorkingDirectory","TimeoutStartUSec","TimeoutStopUSec","KillMode",
           "Restart","UMask","NoNewPrivileges","ProtectSystem","ReadWritePaths","PrivateTmp","Type")
    cmd=["systemctl","show","--all",UNIT]
    for name in names:cmd+=["-p",name]
    v=dict(x.split("=",1)for x in subprocess.check_output(cmd,text=True).splitlines())
    # Query command configuration as typed fields. systemctl's human rendering
    # omits empty arrays and includes runtime timestamps/PIDs/exit results.
    hooks={"ExecStartPre","ExecStopPost"}
    require(set(names)-hooks <= set(v) <= set(names),"UNIT_PROPERTIES")
    import shlex
    endpoint="org.freedesktop.systemd1"
    unit_path=shlex.split(subprocess.check_output(["busctl","call",endpoint,
        "/org/freedesktop/systemd1",endpoint+".Manager","LoadUnit","s",UNIT],text=True))
    require(len(unit_path)==2 and unit_path[0]=="o"
            and unit_path[1].startswith("/org/freedesktop/systemd1/unit/"),"UNIT_OBJECT")
    for hook in sorted(hooks):
        raw=json.loads(subprocess.check_output(["busctl","--json=short","get-property",
            endpoint,unit_path[1],endpoint+".Service",hook],text=True))
        require(set(raw)=={"type","data"} and raw["type"]=="a(sasbttttuii)"
                and type(raw["data"]) is list,"TYPED_HOOK_ARRAY")
        commands=[]
        for row in raw["data"]:
            require(type(row)is list and len(row)==10 and type(row[0])is str
                    and type(row[1])is list and all(type(x)is str for x in row[1])
                    and type(row[2])is bool
                    and all(type(x)is int for x in row[3:]),"TYPED_HOOK_FIELDS")
            # path, complete argv and ignore-failure flag, in command order.
            # Remaining fields are execution timestamps, PID, exit code/status.
            commands.append(row[:3])
        v[hook]=json.dumps(commands,sort_keys=True,separators=(",",":"))
    require(set(v)==set(names),"UNIT_PROPERTIES")
    return v
def verify_delta(before, after):
    require(before["DropInPaths"]=="" and after["DropInPaths"]==str(DROP),"ONLY_FIXED_DROPIN")
    require("argv[]=/usr/bin/python3 -s -B "+str(ROOT/ENTRY)+" run ;" in after["ExecStart"],"FIXED_COMMAND")
    require({k:v for k,v in before.items()if k not in {"DropInPaths","ExecStart"}}==
            {k:v for k,v in after.items()if k not in {"DropInPaths","ExecStart"}},"CONFINEMENT_CHANGED")
def quiet(p):
    p.held_prior()
    v=dict(x.split("=",1)for x in subprocess.check_output(
        ["systemctl","show",UNIT,"-p","MainPID","-p","ActiveState"],text=True).splitlines())
    require(v["MainPID"]=="0" and v["ActiveState"] in {"inactive","failed"},"LIVE_UNIT")
def reviewed(folder):
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    a=verify_result(trusted(folder));m=json.loads(trusted(Path(folder)/"packet-manifest.json").read_bytes())
    require(a["verdict"]=="APPROVE" and a["change_id"]==REVIEW_CHANGE
            and json.loads(trusted(Path(folder)/"report.md").read_bytes())["findings"]==[],"INDEPENDENT_APPROVE")
    require(REQUIRED <= set(m["source_files"]),"WHOLE_COMPONENT")
    return a,m
def authority():
    from orchestrator.manual_host_guard import trusted
    require(Path(__file__).resolve()==ROOT/ENTRY,"INSTALLED_ENTRY")
    p=parent();a,m=reviewed(RECORD/"review")
    require(a["runtime_sha256"]==sha(trusted(p.metadata()[1]["runtime"]).read_bytes()),"RUNTIME")
    receipt=json.loads(trusted(RECORD/"INSTALLED.json").read_bytes())
    require(receipt["source"]==a["source_sha"] and receipt["review_sha256"]==a["report_sha256"]
            and receipt["files"]==m["source_files"] and receipt["drop_sha256"]==sha(drop_bytes()),"INSTALL_RECEIPT")
    for name,pin in m["source_files"].items():
        require(sha(trusted((ROOT if name in ADDED else BASE)/name).read_bytes())==pin,"SOURCE_CHANGED")
    require(trusted(DROP).read_bytes()==drop_bytes(),"DROP_CHANGED")
    verify_delta(receipt["before"],properties())
    return a,p
def install(source, review):
    from orchestrator.manual_host_guard import trusted
    from tools.install_preparation_branch_repair import mkdir,put,OWNER_CHECK
    from tools.install_preparation_runtime import standalone_git
    require(os.getuid()==0 and sys.flags.no_user_site,"ROOT_INSTALL")
    source=trusted(source);review=trusted(review);standalone_git(source)
    a,m=reviewed(review);p=parent();quiet(p)
    require(a["runtime_sha256"]==sha(trusted(p.metadata()[1]["runtime"]).read_bytes()),"RUNTIME")
    git=lambda *args:subprocess.check_output(["git",*args],cwd=source,text=True).strip()
    require(git("rev-parse","HEAD")==a["source_sha"] and git("branch","--show-current")==BRANCH
            and not git("status","--porcelain"),"CLEAN_REVIEWED_SOURCE")
    require(trusted(source/ENTRY).read_bytes()==Path(__file__).read_bytes(),"INSTALLER")
    for name,pin in m["source_files"].items():
        require(sha(trusted(source/name).read_bytes())==pin,"SOURCE_CHANGED")
        if name not in ADDED:require(trusted(source/name).read_bytes()==trusted(BASE/name).read_bytes(),"ONLY_ADDITIONS")
    before=properties();require(before["DropInPaths"]=="","NO_PRIOR_DROPIN")
    for target in [ROOT,RECORD,DROP.parent]:
        trusted(target.parent);require(not target.exists() and not target.is_symlink(),"ALREADY_ATTEMPTED")
    import shutil
    require(all(shutil.disk_usage(x.parent).free>8*2**30 for x in [ROOT,RECORD]),"DISK_STOP")
    require(json.loads(subprocess.check_output(["runuser","-u","partho","--","python3","-s","-B","-c",OWNER_CHECK],text=True))["status"]=="NO_RUNNING_CALL","LIVE_MODEL")
    mkdir(RECORD);put(RECORD/"INSTALL_INTENT.json",encoded({"source":a["source_sha"],"review":a["report_sha256"],"model_calls":0}))
    mkdir(ROOT)
    for name in sorted(ADDED):put(ROOT/name,trusted(source/name).read_bytes())
    for path in review.iterdir():
        require(path.is_file() and not path.is_symlink(),"FLAT_REVIEW")
        put(RECORD/"review"/path.name,trusted(path).read_bytes())
    mkdir(DROP.parent);put(DROP,drop_bytes())
    subprocess.run(["systemctl","daemon-reload"],check=True)
    after=properties();verify_delta(before,after)
    put(RECORD/"INSTALLED.json",encoded({"source":a["source_sha"],"review_sha256":a["report_sha256"],
        "files":m["source_files"],"drop_sha256":sha(drop_bytes()),"before":before}))
    return {"status":"INSTALLED_HELD","scientific_calls":0,"batch_ceiling":140,"L_additional_max":4,
            "other_allocations_held":8}

def context():
    from orchestrator.manual_host_guard import trusted
    pins = {
        "docs/L_FUNDED_CHECKPOINT_PRIVATE.json": "b10d68a5ef3a84ecd5fd9e38735952b84e8d6e4d83851dad9cbdd163d4e76d32",
        "docs/L_FUNDED_AUTHOR_TASK.md": "846d531c4caedf7868c669023bbda25f8ab18acbeebcf1216c102a2b3b852aff",
        "docs/L_FUNDED_BASELINE_PRIVATE.json": "c99831e0789f6d26f2ed700093a0a2a45a5112a68697d13033f23659cb214365",
    }
    raw = {}
    for name, pin in pins.items():
        raw[name] = trusted(ROOT/name).read_bytes()
        require(sha(raw[name]) == pin, "FROZEN_CONTEXT")
    return (json.loads(raw["docs/L_FUNDED_CHECKPOINT_PRIVATE.json"]),
            raw["docs/L_FUNDED_AUTHOR_TASK.md"], raw["docs/L_FUNDED_BASELINE_PRIVATE.json"],
            {"question_sha256": pins["docs/L_FUNDED_AUTHOR_TASK.md"],
             "baseline_sha256": pins["docs/L_FUNDED_BASELINE_PRIVATE.json"]})

def qualifier(checkpoint):
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    from types import SimpleNamespace
    recovery = Path("/opt/research-system/manual-repair-helpers/multiwin-output-boundary-20261013")
    record = Path("/var/lib/research-system-manual-sprint10-deployment/multiwin-output-boundary-20261013")
    approval = verify_result(trusted(record/"review"))
    require(approval["verdict"] == "APPROVE" and approval["source_sha"] ==
            "71423b5ec057c7d366073c012ed5d7578f2bfcba" and approval["report_sha256"] ==
            "3b677a20dded99f70dd33f7e6a2b6aea9a9059341e26d26c4b470bdc3c48782b",
            "INSTALLED_RECOVERY_APPROVAL")
    manifest = json.loads(trusted(record/"review/packet-manifest.json").read_bytes())
    installed = json.loads(trusted(record/"INSTALLED.json").read_bytes())
    require(installed["source"] == approval["source_sha"] and
            installed["review_sha256"] == approval["report_sha256"] and
            set(installed["files"]) == {"tools/multiwin_preserved_runtime.py",
                "orchestrator/multiwin_preserved_output.py","docs/MULTIWIN_OUTPUT_BOUNDARY_PRIVATE.json"},
            "INSTALLED_RECOVERY_RECEIPT")
    for name, pin in installed["files"].items():
        require(sha(trusted(recovery/name).read_bytes()) == pin == manifest["source_files"][name],
                "INSTALLED_RECOVERY_SOURCE")
    helper = load("_l_installed_recovery", recovery/"orchestrator/multiwin_preserved_output.py")
    frozen = helper.document(recovery)
    bound = checkpoint["lanes"]["multiwin"]
    require(bound["lane"] == frozen["lane"], "RECOVERY_LANE")
    def verify(accounts, local):
        for unit in ("research-multiwin-returned-provenance-20261013.service",
                     "research-multiwin-output-boundary-20261013.service"):
            current = dict(line.split("=",1) for line in subprocess.check_output(
                ["systemctl","show",unit,"-p","MainPID","-p","ActiveState","-p","ControlGroup"],
                text=True).splitlines())
            require(current == {"MainPID":"0","ActiveState":"inactive","ControlGroup":""},
                    "RECOVERY_UNIT_LIVE")
        driver = SimpleNamespace(state=Path(bound["lane"]), config=bound["config"],
                    store=SimpleNamespace(db=local,batch=accounts))
        return helper.grant(driver,frozen,approval["report_sha256"])
    return verify

def activate(approval):
    checkpoint, question, baseline, pins = context()
    helper = load("_l_funded_continuation",ROOT/"orchestrator/l_funded_continuation.py")
    history = load("_l_funded_history",ROOT/"orchestrator/l_funded_history.py")
    policy = load("_l_existing_batch140",ROOT/"orchestrator/scientific_batch140.py")
    undo = helper.activate(checkpoint,history,qualifier(checkpoint),
                           policy,policy.document(ROOT),approval["report_sha256"])
    return helper,checkpoint,question,baseline,pins,undo

def service(action):
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,"SERVICE_OWNER")
    approval,p = authority()
    scope,n = p.metadata()
    require(os.environ.get("RESEARCH_MANUAL_RUNTIME_CONFIG")==n["runtime"],"RUNTIME_PATH")
    helper,checkpoint,question,baseline,pins,undo = activate(approval)
    try:
        if action in {"run","status"}:
            return p.service(action)
        require(action=="amend","ACTION")
        quiet(p)
        p.connect_qualifier()
        from orchestrator import colab_pnormct_policy
        colab_pnormct_policy.connect()
        os.environ.update(GIT_CONFIG_COUNT="1",GIT_CONFIG_KEY_0="safe.directory",GIT_CONFIG_VALUE_0=str(BASE))
        from orchestrator.analysis_driver import AnalysisDriver
        from orchestrator.colab_pnorm_v2_feedback import prepared
        driver = prepared(AnalysisDriver)(scope["new_lane"])
        try:
            return helper.apply(driver,checkpoint,approval,question,baseline,pins)
        finally:
            driver.store.db.close()
            driver.store.batch.db.close()
    finally:
        undo()

def start(transition):
    import fcntl
    from orchestrator.manual_host_guard import trusted
    from tools.install_preparation_branch_repair import put, OWNER_CHECK
    require(os.getuid()==0 and sys.flags.no_user_site,"ROOT_START")
    approval,p = authority()
    scope,n = p.metadata()
    quiet(p)
    require(isinstance(transition,str) and len(transition)==64 and
            all(c in "0123456789abcdef" for c in transition),"EXACT_TRANSITION")
    record = Path(n["record"])
    with (record/"start.lock").open("a") as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        quiet(p)
        cmd = ["runuser","-u","partho","--","env",
               "RESEARCH_MANUAL_RUNTIME_CONFIG="+n["runtime"],
               "PYTHONPATH="+str(BASE),"python3","-s","-B",str(ROOT/ENTRY),"status"]
        current = json.loads(subprocess.check_output(cmd,text=True))
        require(current["transition"]==transition and
                current["phase"] in {"run_spec_author","run_spec_review"},
                "STATE_CHANGED_OR_HELD")
        require(json.loads(subprocess.check_output(
            ["runuser","-u","partho","--","python3","-s","-B","-c",OWNER_CHECK],
            text=True))["status"]=="NO_RUNNING_CALL","LIVE_MODEL")
        amended = json.loads(trusted(Path(scope["new_lane"])/CHANGE/"COMPLETE.json").read_bytes())
        require(amended["source"]==approval["source_sha"] and
                amended["review_sha256"]==approval["report_sha256"] and
                amended["status"]=="L_BASELINE_CONTEXT_READY_NO_CALL","AMENDMENT_REQUIRED")
        intent = record/"operations"/("advance-"+transition+".json")
        require(not intent.exists() and not intent.is_symlink(),"START_ALREADY_ATTEMPTED_RECONCILE")
        original = p.authority()
        operation = {"mode":"advance","transition":transition,"source":original["source_sha"],
                     "review_sha256":original["report_sha256"],"unit":n["unit"]}
        put(intent,encoded({**operation,"continuation_source":approval["source_sha"],
                            "continuation_review_sha256":approval["report_sha256"]}))
        temp=record/"OPERATION.next"
        put(temp,encoded(operation))
        os.replace(temp,record/"OPERATION.json")
        subprocess.run(["systemctl","start","--no-block",n["unit"]],check=True)
        return {"status":"START_REQUESTED_RECONCILE_SAME_UNIT","unit":n["unit"],
                "transition":transition,"new_owner":False}

def main():
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["install","status","run","amend","start"])
    parser.add_argument("--source",type=Path);parser.add_argument("--review",type=Path);parser.add_argument("--transition")
    args=parser.parse_args()
    if args.action=="install":
        require(args.source is not None and args.review is not None and args.transition is None,"INSTALL_ARGS")
        return install(args.source,args.review)
    require(args.source is None and args.review is None,"NO_SOURCE_OVERRIDE")
    if args.action=="start":
        require(os.getuid()==0 and sys.flags.no_user_site and args.transition is not None,"ROOT_START")
        return start(args.transition)
    require(args.transition is None,"NO_TRANSITION_OVERRIDE")
    return service(args.action)
if __name__=="__main__":
    os.umask(0o077);sys.path.insert(0,str(BASE));print(json.dumps(main(),sort_keys=True))
