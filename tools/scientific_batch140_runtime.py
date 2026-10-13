"""Fixed reviewed entry-point patch for the existing meeting service.

Only ExecStart changes. Original source, unit, lane, owner, calls, account,
transport, confinement and per-run limits are retained. No new executor.
"""
from pathlib import Path
import argparse, importlib.util, json, os, subprocess, sys
BASE = Path("/opt/research-system/manual-repair-helpers/meeting-preparation-20261013")
ROOT = Path("/opt/research-system/manual-repair-helpers/scientific-batch140-20261013")
RECORD = Path("/var/lib/research-system-manual-sprint10-deployment/scientific-batch140-20261013")
ENTRY = "tools/scientific_batch140_runtime.py"
CHANGE = "scientific-batch140-20261013"
BRANCH = "astra/scientific-batch140-20261013"
UNIT = "research-meeting-preparation-20261013.service"
DROP = Path("/etc/systemd/system")/(UNIT+".d")/"batch140.conf"
ADDED = {
    ENTRY, "docs/SCIENTIFIC_BATCH140_SCOPE.md", "orchestrator/scientific_batch140.py", "orchestrator/meeting_batch140.py",
    "docs/SCIENTIFIC_BATCH140_PRIVATE.json", "docs/SCIENTIFIC_BATCH140_OPERATOR_APPROVAL.txt",
    "docs/SCIENTIFIC_BATCH140_OPERATOR_QUESTION.txt",
    "docs/SCIENTIFIC_BATCH140_OPERATOR_RECORD_PRIVATE.json",
    "docs/MEETING_BATCH140_CHECKPOINT_PRIVATE.json", "docs/MEETING_BATCH140_QUESTION.md",
    "docs/MEETING_BATCH140_EVIDENCE_PRIVATE.md", "tests/test_scientific_batch140.py",
    "tests/test_meeting_batch140.py", "tests/test_scientific_batch140_runtime.py",
}
REQUIRED = ADDED | {
    "orchestrator/meeting_preparation.py", "tools/meeting_preparation_runtime.py",
    "orchestrator/autonomy_accounting.py", "orchestrator/autonomy_limits.py",
    "orchestrator/manual_executor.py", "orchestrator/manual_driver.py",
    "orchestrator/manual_stage.py", "orchestrator/manual_context.py",
    "orchestrator/preparation_followup.py", "orchestrator/author_revision_accounting.py",
    "orchestrator/scientific_program.py", "orchestrator/meeting_author_feedback.py",
    "tests/test_meeting_preparation.py",
}
def require(ok, why):
    if not ok: raise ValueError("BATCH140_RUNTIME_" + why)
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
    p=load("_batch140_original_meeting",BASE/"tools/meeting_preparation_runtime.py")
    a=p.authority()
    require(a["source_sha"]=="b06d64da7568ad1dbd51926c985806e6719897cb"
            and a["report_sha256"]=="23538a2c19750ed70ddc2a9efae83bc960b0e91894f7d1d2c0819be844741ab5",
            "ORIGINAL_APPROVAL")
    return p
def drop_bytes():
    return ("[Service]\nExecStart=\nExecStart=/usr/bin/python3 -s -B "+str(ROOT/ENTRY)+" run\n").encode()
def properties():
    names=("FragmentPath","DropInPaths","ExecStart","ExecStartPre","ExecStopPost","User","Group",
           "Environment","WorkingDirectory","TimeoutStartUSec","TimeoutStopUSec","KillMode",
           "Restart","UMask","NoNewPrivileges","ProtectSystem","ReadWritePaths","PrivateTmp","Type")
    cmd=["systemctl","show",UNIT]
    for name in names:cmd+=["-p",name]
    v=dict(x.split("=",1)for x in subprocess.check_output(cmd,text=True).splitlines())
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
    require(a["verdict"]=="APPROVE" and a["change_id"]==CHANGE
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
    return {"status":"INSTALLED_HELD","scientific_calls":0,"batch_ceiling":140,"meeting_additional_max":4,
            "other_allocations_held":8}
def service(action):
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,"SERVICE_OWNER")
    a,p=authority();scope,n=p.metadata()
    require(os.environ.get("RESEARCH_MANUAL_RUNTIME_CONFIG")==n["runtime"],"RUNTIME_PATH")
    helper=load("_meeting_batch140",ROOT/"orchestrator/meeting_batch140.py")
    helper.activate(ROOT,a["report_sha256"])
    if action in {"run","status"}:
        # Original native operation/transition, host transport and all lane guards.
        return p.service(action)
    require(action=="amend","ACTION");quiet(p);p.connect_qualifier()
    os.environ.update(GIT_CONFIG_COUNT="1",GIT_CONFIG_KEY_0="safe.directory",GIT_CONFIG_VALUE_0=str(BASE))
    from orchestrator.meeting_preparation import MeetingDriver
    d=MeetingDriver(scope["new_lane"])
    try:
        b,question,evidence=helper.document(ROOT)
        return helper.apply(d,b,a,question,evidence)
    finally:d.store.db.close();d.store.batch.db.close()
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
        _,p=authority();return p.start("advance",args.transition)
    require(args.transition is None,"NO_TRANSITION_OVERRIDE")
    return service(args.action)
if __name__=="__main__":
    os.umask(0o077);sys.path.insert(0,str(BASE));print(json.dumps(main(),sort_keys=True))
