"""Install only the reviewed root-owned L start command; no service or ledger changes."""
from pathlib import Path
import json,os,subprocess,sys
BASE=Path("/opt/research-system/manual-repair-helpers/colab-l-question-20261013")
sys.path.insert(0,str(BASE))
from tools import install_preparation_branch_repair as files
from tools.install_preparation_runtime import standalone_git
from orchestrator.manual_host_guard import trusted
from orchestrator.autonomy_review import verify_result
NEW={"tools/l_funded_start.py","tools/install_l_funded_start.py","tests/test_l_funded_start.py"}
def install(source,review):
    from importlib.util import spec_from_file_location,module_from_spec
    def require(ok,why):
        if not ok:raise ValueError("L_START_INSTALL_"+why)
    require(os.getuid()==0 and sys.flags.no_user_site,"ROOT")
    source=trusted(source);review=trusted(review);standalone_git(source)
    a=verify_result(review);m=json.loads(trusted(review/"packet-manifest.json").read_bytes())
    require(a["verdict"]=="APPROVE" and a["change_id"]=="l-funded-receipt-start-20261013"
            and json.loads(trusted(review/"report.md").read_bytes())["findings"]==[],"APPROVE")
    git=lambda *args:subprocess.check_output(["git","-C",str(source),*args],text=True).strip()
    require(git("rev-parse","HEAD")==a["source_sha"] and not git("status","--porcelain"),"CLEAN_SOURCE")
    require(trusted(source/"tools/install_l_funded_start.py").read_bytes()==Path(__file__).read_bytes(),"INSTALLER")
    spec=spec_from_file_location("_parent_l",trusted(Path("/opt/research-system/manual-repair-helpers/l-funded-continuation-20261013/tools/l_funded_runtime.py")))
    r=module_from_spec(spec);spec.loader.exec_module(r)
    old,p=r.authority();r.quiet(p)
    require(old["source_sha"]=="d58718fabd2fa348ee264f7af68376e63d10f2be"
            and old["report_sha256"]=="303b99d60a86d2839a3555d441bc22c991bb24d7e7777fdb17b198d45fce2cb8","PARENT")
    previous=json.loads(trusted(r.RECORD/"review/packet-manifest.json").read_bytes())
    require(set(m["source_files"])==set(previous["source_files"])|NEW,"WHOLE_COMPONENT")
    require(all(m["source_files"][n]==pin for n,pin in previous["source_files"].items()),"PARENT_UNCHANGED")
    for n,pin in m["source_files"].items():require(r.sha(trusted(source/n).read_bytes())==pin,"SOURCE")
    require(a["runtime_sha256"]==old["runtime_sha256"],"RUNTIME")
    root=Path("/opt/research-system/manual-repair-helpers/l-funded-receipt-start-20261013")
    record=Path("/var/lib/research-system-manual-sprint10-deployment/l-funded-receipt-start-20261013")
    import shutil
    for target in [root,record]:
        trusted(target.parent);require(not target.exists() and not target.is_symlink(),"EXCLUSIVE")
        require(shutil.disk_usage(target.parent).free>8*2**30,"DISK")
    require(json.loads(subprocess.check_output(["runuser","-u","partho","--","python3","-s","-B","-c",files.OWNER_CHECK],text=True))["status"]=="NO_RUNNING_CALL","LIVE_MODEL")
    files.mkdir(record);files.put(record/"INSTALL_INTENT.json",r.encoded({"source":a["source_sha"],"review":a["report_sha256"]}))
    files.mkdir(root);files.put(root/"tools/l_funded_start.py",trusted(source/"tools/l_funded_start.py").read_bytes())
    for path in review.iterdir():
        require(path.is_file() and not path.is_symlink(),"FLAT_REVIEW")
        files.put(record/"review"/path.name,trusted(path).read_bytes())
    result={"status":"INSTALLED_HELD","source":a["source_sha"],"review":a["report_sha256"],"service_changed":False,"ledger_changed":False,"model_calls":0}
    files.put(record/"COMPLETE.json",r.encoded(result));return result
if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument("--source",type=Path,required=True);parser.add_argument("--review",type=Path,required=True)
    args=parser.parse_args();os.umask(0o077);print(json.dumps(install(args.source,args.review),sort_keys=True))
