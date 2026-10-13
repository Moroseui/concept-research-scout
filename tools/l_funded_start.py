"""Bounded start repair: retain the installed L runtime; validate its service receipt."""
from pathlib import Path
import argparse,importlib.util,json,os,stat,subprocess,sys
BASE=Path("/opt/research-system/manual-repair-helpers/colab-l-question-20261013")
PARENT=Path("/opt/research-system/manual-repair-helpers/l-funded-continuation-20261013")
ROOT=Path("/opt/research-system/manual-repair-helpers/l-funded-receipt-start-20261013")
RECORD=Path("/var/lib/research-system-manual-sprint10-deployment/l-funded-receipt-start-20261013")
CHANGE="l-funded-receipt-start-20261013"
ENTRY="tools/l_funded_start.py"
OLD_SOURCE="d58718fabd2fa348ee264f7af68376e63d10f2be"
OLD_REVIEW="303b99d60a86d2839a3555d441bc22c991bb24d7e7777fdb17b198d45fce2cb8"
def require(ok,why):
    if not ok:raise ValueError("L_RECEIPT_START_"+why)
def service_receipt(path,work):
    """Open every private component without following links; enforce actual writer."""
    from orchestrator.manual_host_guard import trusted
    work=Path(work);path=Path(path)
    require(path==work/"lane"/"l-funded-continuation-20261013"/"COMPLETE.json","EXACT_RECEIPT_PATH")
    trusted(work.parent)
    fd=os.open(work.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for name in [work.name,"lane","l-funded-continuation-20261013"]:
            nextfd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd);fd=nextfd;s=os.fstat(fd)
            require(s.st_uid==s.st_gid==1003 and stat.S_IMODE(s.st_mode)==0o700,"PRIVATE_DIRECTORY")
        filefd=os.open("COMPLETE.json",os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
        try:
            s=os.fstat(filefd)
            require(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==s.st_gid==1003
                    and stat.S_IMODE(s.st_mode)==0o600 and s.st_size<=65536,"PRIVATE_RECEIPT")
            raw=os.read(filefd,65537)
            require(len(raw)==s.st_size,"RECEIPT_READ")
            return json.loads(raw)
        finally:os.close(filefd)
    finally:os.close(fd)
def authority():
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    require(Path(__file__).resolve()==ROOT/ENTRY,"INSTALLED_ENTRY")
    a=verify_result(trusted(RECORD/"review"))
    m=json.loads(trusted(RECORD/"review/packet-manifest.json").read_bytes())
    require(a["verdict"]=="APPROVE" and a["change_id"]==CHANGE
            and json.loads(trusted(RECORD/"review/report.md").read_bytes())["findings"]==[],"INDEPENDENT_APPROVE")
    import hashlib
    require(hashlib.sha256(trusted(ROOT/ENTRY).read_bytes()).hexdigest()==m["source_files"][ENTRY],"SELF_SOURCE")
    spec=importlib.util.spec_from_file_location("_installed_l_funded",trusted(PARENT/"tools/l_funded_runtime.py"))
    r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
    old,p=r.authority()
    require(old["source_sha"]==OLD_SOURCE and old["report_sha256"]==OLD_REVIEW,"INSTALLED_PARENT")
    return r,old,p,a
def start(transition):
    import fcntl
    from tools.install_preparation_branch_repair import put,OWNER_CHECK
    require(os.getuid()==0 and sys.flags.no_user_site,"ROOT_START")
    r,approval,p,repair=authority();scope,n=p.metadata();r.quiet(p)
    require(isinstance(transition,str) and len(transition)==64 and all(c in "0123456789abcdef" for c in transition),"EXACT_TRANSITION")
    record=Path(n["record"])
    with (record/"start.lock").open("a") as stream:
        fcntl.flock(stream,fcntl.LOCK_EX);r.quiet(p)
        cmd=["runuser","-u","partho","--","env","RESEARCH_MANUAL_RUNTIME_CONFIG="+n["runtime"],
             "PYTHONPATH="+str(BASE),"python3","-s","-B",str(PARENT/"tools/l_funded_runtime.py"),"status"]
        current=json.loads(subprocess.check_output(cmd,text=True))
        require(current["transition"]==transition and current["phase"] in {"run_spec_author","run_spec_review"},"STATE_CHANGED_OR_HELD")
        require(json.loads(subprocess.check_output(["runuser","-u","partho","--","python3","-s","-B","-c",OWNER_CHECK],text=True))["status"]=="NO_RUNNING_CALL","LIVE_MODEL")
        lane=Path(scope["new_lane"])
        amended=service_receipt(lane/r.CHANGE/"COMPLETE.json",lane.parent)
        require(amended["source"]==approval["source_sha"] and amended["review_sha256"]==approval["report_sha256"]
                and amended["status"]=="L_BASELINE_CONTEXT_READY_NO_CALL","AMENDMENT_REQUIRED")
        intent=record/"operations"/("advance-"+transition+".json")
        require(not intent.exists() and not intent.is_symlink(),"START_ALREADY_ATTEMPTED_RECONCILE")
        original=p.authority()
        operation={"mode":"advance","transition":transition,"source":original["source_sha"],
                   "review_sha256":original["report_sha256"],"unit":n["unit"]}
        put(intent,r.encoded({**operation,"continuation_source":approval["source_sha"],
            "continuation_review_sha256":approval["report_sha256"],"start_repair_review_sha256":repair["report_sha256"]}))
        temp=record/"OPERATION.next";put(temp,r.encoded(operation));os.replace(temp,record/"OPERATION.json")
        subprocess.run(["systemctl","start","--no-block",n["unit"]],check=True)
        return {"status":"START_REQUESTED_RECONCILE_SAME_UNIT","unit":n["unit"],"transition":transition,"new_owner":False}
if __name__=="__main__":
    os.umask(0o077);sys.path.insert(0,str(BASE))
    parser=argparse.ArgumentParser();parser.add_argument("--transition",required=True)
    print(json.dumps(start(parser.parse_args().transition),sort_keys=True))
