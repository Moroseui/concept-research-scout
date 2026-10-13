"""One reviewed synthetic retest and normal acceptance; no model or provider launch."""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, os, subprocess, sys
BASE=Path("/opt/research-system/manual-repair-helpers/colab-pnorm-v2-question-20261012")
CURRENT=Path("/opt/research-system/manual-repair-helpers/pnorm-v2-review-turns-20261012")
CHANGE="pnorm-v2-synthetic-revalidation-20261013"
RUN="colab-arm-b9d64a3c09b799bc10b0eba7"
CALL="7d44f07e32ed9343acba871aeb8c0f7232c6da281227c1b9585fa06a6a70572e"
DOCUMENT="docs/PNORM_V2_SYNTHETIC_REVALIDATION_PRIVATE.json"
PIN="18afe6b16187026c3224aa7dd40cfc3408d4ec9c87e571a648a210e30eaf2512"
ENTRY="tools/revalidate_pnorm_v2_synthetic.py"
REASON="OUTPUT_VALIDATION_REFUSED: NOTEBOOK_APPROVAL_REQUIRES_SYNTHETIC_PASS"
def require(ok,why):
    if not ok:raise ValueError("PNORM_SYNTHETIC_REVALIDATION_"+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":")).encode()
def load(name,path):
    from orchestrator.manual_host_guard import trusted
    s=importlib.util.spec_from_file_location(name,trusted(path))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def authority(source,review):
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    source=trusted(source);review=trusted(review)
    a=verify_result(review);manifest=json.loads(trusted(review/"packet-manifest.json").read_bytes())
    require(a["verdict"]=="APPROVE"and a["change_id"]==CHANGE
        and json.loads(trusted(review/"report.md").read_bytes())["findings"]==[],"APPROVE")
    require(Path(__file__).resolve()==source/ENTRY,"EXACT_ENTRY")
    require(subprocess.check_output(["git","-c","safe.directory="+str(source),"rev-parse","HEAD"],cwd=source,text=True).strip()==a["source_sha"],"SOURCE")
    require(subprocess.check_output(["git","-c","safe.directory="+str(source),"branch","--show-current"],cwd=source,text=True).strip()=="astra/manual-colab-pnorm-v2-question-20261012","BRANCH")
    require(not subprocess.check_output(["git","-c","safe.directory="+str(source),"status","--porcelain"],cwd=source),"CLEAN_SOURCE")
    for name,pin in manifest["source_files"].items():
        require(sha(trusted(source/name).read_bytes())==pin,"SOURCE_FILE")
    for name in (ENTRY,DOCUMENT,"orchestrator/notebook_synthetic.py",
                 "orchestrator/notebook_synthetic_harness.py","orchestrator/analysis_driver.py"):
        require(name in manifest["source_files"],"COMPONENT")
    raw=trusted(source/DOCUMENT).read_bytes();require(sha(raw)==PIN,"FROZEN_PIN")
    b=json.loads(raw);require(b["run_id"]==RUN and b["preserved_calls"]==3 and b["new_allowance"]==0,"SCOPE")
    return a,b
def originals(d,b,*,state=True):
    from orchestrator import private_records as pr
    require(d.config==b["config"]and d.config["run_id"]==RUN,"CONFIG")
    require(sha(pr.check(d.state/"lane.json").read_bytes())==b["configuration_sha256"],"CONFIG_BYTES")
    require(Path(d.store.path)==Path(b["lane"])/"jobs.sqlite","LANE")
    require(not(d.state/"HALT").exists()and not(d.store.batch.folder/"HALT").exists(),"HALT")
    require(not d.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),"LIVE_MODEL")
    for db,table,key in [(d.store.db,"manual_calls","local_rows"),(d.store.batch.db,"autonomy_calls","global_rows")]:
        rows=[dict(db.execute("SELECT * FROM "+table+" WHERE id=?",(r["id"],)).fetchone()or{})for r in b[key]]
        require(rows==b[key]and len(rows)==3,"CALLS")
    require([dict(r)for r in d.store.db.execute("SELECT * FROM manual_calls ORDER BY rowid")]==b["local_rows"],"LOCAL_SET")
    require(d.store.batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'AND change_id=?",(RUN,)).fetchone()[0]==3,"GLOBAL_SET")
    require(dict(d.store.db.execute("SELECT * FROM manual_account WHERE id=1").fetchone())==b["account_row"],"ACCOUNT")
    require(dict(d.store.batch.db.execute("SELECT * FROM autonomy_runs WHERE id=?",(RUN,)).fetchone())==b["owner"],"OWNER")
    if state:require(dict(d.store.db.execute("SELECT * FROM manual_state WHERE id=1").fetchone())==b["state_row"],"STATE")
    value=json.loads(b["state_row"]["payload"])
    require(value["phase"]=="BLOCKED"and value["reason"]==REASON,"REFUSAL")
    require(value["pending"]=={"id":CALL,"stage":"run_spec_review","round":2,
        "workspace":b["failed_workspace"]},"PENDING")
    require([r["status"]for r in b["local_rows"]]==["COMPLETE","FAILED","COMPLETE"],"OUTCOMES")
    work=Path(b["failed_workspace"])
    for name,pin in b["files"].items():
        require(Path(name).name==name and sha(pr.check(work/name).read_bytes())==pin["sha256"],"REVIEW_BYTES")
    review=json.loads(pr.check(work/"review.json").read_bytes())
    require(review["verdict"]=="APPROVE"and review["findings"]==[],"SCIENTIFIC_APPROVAL")
    folder=Path(value["notebook_revision_result"]["folder"])
    require(folder==d.state/"notebook-revisions/author-1","NOTEBOOK_FOLDER")
    for name,pin in b["synthetic_original_files"].items():
        rel=Path(name);require(not rel.is_absolute()and".."not in rel.parts,"ORIGINAL_PATH")
        raw=pr.check(folder/rel).read_bytes()
        require(len(raw)==pin["bytes"]and sha(raw)==pin["sha256"],"ORIGINAL_BYTES")
    for ref in value["artifacts"]:
        rel=Path(ref["path"]);require(not rel.is_absolute()and".."not in rel.parts,"ARTIFACT_PATH")
        require(sha(pr.check(d.context/rel).read_bytes())==ref["sha256"],"ARTIFACT_BYTES")
    raw=pr.check(folder/"revised.ipynb").read_bytes()
    require(sha(raw)==value["notebook_revision_result"]["notebook_sha256"],"NOTEBOOK")
    return value,raw
def retest_and_accept(d,b,approval,runner):
    from orchestrator import private_records as pr
    from orchestrator.manual_executor import lock
    with lock(d.state/"driver.lock"):
        d.guard();value,raw=originals(d,b)
        folder=d.state/CHANGE;require(not folder.exists()and not folder.is_symlink(),"ALREADY_ATTEMPTED")
        pr.mkdir(folder);pr.write_bytes(folder/"original-state.json",b["state_row"]["payload"].encode())
        pr.write_bytes(folder/"INTENT.json",canonical({"source":approval["source_sha"],"review":approval["report_sha256"],"scope":PIN,"model_calls":0}))
        result=runner(folder/"synthetic",raw,d.config["notebook_revision"]["environment"],execution=True)
        originals(d,b)
        pr.write_bytes(folder/"RETEST.json",canonical(result))
        require(result["status"]=="PASS"and result["binding"]["files"]["revised.ipynb"]==sha(raw)
            and result["isolation"]["status"]=="ISOLATED"
            and result["isolation"]["patient_mounts"]is False
            and result["isolation"]["network"]=="UNSHARED"
            and result["isolation"]["credentials"]is False,"SYNTHETIC_PASS")
        updated=copy.deepcopy(value)
        d.artifact(updated,"synthetic_tests","13B-tests-1-revalidated-20261013.json",canonical(result),1)
        updated["notebook_revision_result"].update(tests_sha256=sha(canonical(result)),synthetic_status="PASS")
        updated["interventions"].append({"kind":CHANGE,"scope_sha256":PIN,
            "review_sha256":approval["report_sha256"],"original_tests_sha256":value["notebook_revision_result"]["tests_sha256"],
            "new_tests_sha256":sha(canonical(result)),"notebook_unchanged":True,"preserved_calls":3,"new_allowance":0})
        # The ordinary validator still requires PASS and the original completed
        # scientific output hashes. No phase, verdict, call or limit is invented.
        accepted=d.accept_completed(updated)
        originals(d,b,state=False)
        require(d.current()["phase"]=="COMMIT_SPEC"and d.current()["spec_review"]==str(Path(b["failed_workspace"])/"review.json"),"NORMAL_ACCEPTANCE")
        record={"status":"SYNTHETIC_PASS_NORMAL_SPEC_ACCEPTANCE","source":approval["source_sha"],
            "review_sha256":approval["report_sha256"],"tests_sha256":sha(canonical(result)),
            "notebook_sha256":sha(raw),"model_calls":0,"new_allowance":0,"preserved_calls":3}
        pr.write_bytes(folder/"COMPLETE.json",canonical(record));return record
def worker(source,review):
    from orchestrator import colab_arm_question as q,colab_pnormct_policy
    from orchestrator.analysis_driver import AnalysisDriver
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,"SERVICE_OWNER")
    approval,b=authority(source,review)
    current=load("_current_reviewed_runtime",CURRENT/"tools/pnorm_v2_review_runtime.py")
    accepted,p=current.authority()
    require(accepted["source_sha"]=="e43cb51f70b8da4de8c5b6dd7537e6555f522578"
        and accepted["report_sha256"]=="a7f4ddfc15106bcf8b78e008f6e1e6f89c46afededad6da7868d016556508897","INSTALLED_PARENT")
    parent=p.prior();scope,n=parent.metadata()
    require(os.environ.get("RESEARCH_MANUAL_RUNTIME_CONFIG")==n["runtime"],"SAME_RUNTIME")
    parent.held_prior();parent.connect_qualifier();colab_pnormct_policy.connect()
    os.environ["GIT_CONFIG_COUNT"]="1";os.environ["GIT_CONFIG_KEY_0"]="safe.directory";os.environ["GIT_CONFIG_VALUE_0"]=str(BASE)
    d=p.corrected_feedback().prepared(AnalysisDriver)(scope["new_lane"])
    try:
        q.validate(d.store,q.RUN);p.checkpoint(d)
        original=BASE/"orchestrator/notebook_synthetic.py"
        require((source/"orchestrator/notebook_synthetic.py").read_bytes()==original.read_bytes(),"UNCHANGED_SANDBOX")
        synthetic=load("_reviewed_retest_sandbox",source/"orchestrator/notebook_synthetic.py")
        return retest_and_accept(d,b,approval,synthetic.run)
    finally:d.store.db.close();d.store.batch.db.close()
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--source",type=Path,required=True);parser.add_argument("--review",type=Path,required=True)
    args=parser.parse_args()
    return worker(args.source,args.review)
if __name__=="__main__":
    os.umask(0o077);sys.path.insert(0,str(BASE));print(json.dumps(main(),sort_keys=True))
