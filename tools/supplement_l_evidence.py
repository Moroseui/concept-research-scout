"""One reviewed additive evidence correction; no call, verdict or phase change."""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, os, subprocess, sys
BASE=Path("/opt/research-system/manual-repair-helpers/colab-l-question-20261013")
CHANGE="colab-l-evidence-context-20261013"
RUN="colab-arm-47e6a72d9a2c821a4938fcae"
DOCUMENT="docs/L_EVIDENCE_CONTEXT_PRIVATE.json"
PIN="a56ccbe078cf75ea2eba7c2e1b6ef01853b2a9945893255ff6c631cf294cf68e"
ENTRY="tools/supplement_l_evidence.py"
BRANCH="astra/manual-l-evidence-context-20261013"
QUESTION="docs/L_EVIDENCE_CORRECTION.md"
QUESTION_PIN="cbe364bbf57c302dda026932cce59c4eb71f53159ba3bf5482f77fef3fd2f2f9"
def require(ok,why):
    if not ok:raise ValueError("L_EVIDENCE_"+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":")).encode()
def authority(source,review):
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    source=trusted(source);review=trusted(review);a=verify_result(review)
    m=json.loads(trusted(review/"packet-manifest.json").read_bytes())
    require(a["verdict"]=="APPROVE" and a["change_id"]==CHANGE
        and json.loads(trusted(review/"report.md").read_bytes())["findings"]==[],"APPROVAL")
    require(Path(__file__).resolve()==source/ENTRY,"ENTRY")
    git=lambda *args:subprocess.check_output(["git","-c","safe.directory="+str(source),*args],cwd=source,text=True).strip()
    require(git("rev-parse","HEAD")==a["source_sha"] and git("branch","--show-current")==BRANCH
        and not git("status","--porcelain"),"SOURCE")
    for name,p in m["source_files"].items():require(sha(trusted(source/name).read_bytes())==p,"SOURCE_FILE")
    for name in [ENTRY,DOCUMENT,QUESTION,"orchestrator/manual_driver.py","orchestrator/manual_context.py",
                 "orchestrator/analysis_driver.py","orchestrator/notebook_synthetic_harness.py"]:
        require(name in m["source_files"],"WHOLE_COMPONENT")
    raw=trusted(source/DOCUMENT).read_bytes();require(sha(raw)==PIN,"CHECKPOINT")
    b=json.loads(raw);require(b["run_id"]==RUN and b["preserved_calls"]==2 and b["new_allowance"]==0,"SCOPE")
    question=trusted(source/QUESTION).read_bytes();require(sha(question)==QUESTION_PIN,"QUESTION")
    return a,b,question
def originals(d,b,*,state=True):
    from orchestrator import private_records as pr
    require(d.config==b["config"] and d.config["run_id"]==RUN,"CONFIG")
    require(str(d.state)==b["lane"] and Path(d.store.path)==d.state/"jobs.sqlite","LANE")
    require(sha(pr.check(d.state/"lane.json").read_bytes())==b["configuration_sha256"],"CONFIG_BYTES")
    require(not(d.state/"HALT").exists()and not(d.store.batch.folder/"HALT").exists(),"HALT")
    require(not d.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),"LIVE_MODEL")
    require([dict(r)for r in d.store.db.execute("SELECT * FROM manual_calls ORDER BY rowid")]==b["local_rows"],"LOCAL_CALLS")
    require([dict(r)for r in d.store.batch.db.execute("SELECT * FROM autonomy_calls WHERE change_id=? ORDER BY rowid",(RUN,))]==b["global_rows"],"GLOBAL_CALLS")
    require(dict(d.store.db.execute("SELECT * FROM manual_account WHERE id=1").fetchone())==b["account_row"],"ACCOUNT")
    require(dict(d.store.batch.db.execute("SELECT * FROM autonomy_runs WHERE id=?",(RUN,)).fetchone())==b["owner"],"OWNER")
    require(len(b["local_rows"])==len(b["global_rows"])==2 and all(r["status"]=="COMPLETE"for r in b["local_rows"]),"OUTCOMES")
    if state:require(dict(d.store.db.execute("SELECT * FROM manual_state WHERE id=1").fetchone())==b["state_row"],"STATE")
    v=json.loads(b["state_row"]["payload"])
    require(v["phase"]=="run_spec_author" and v["reason"]=="REVISION_REQUIRED"
        and v["rounds"]=={"run_spec_author":1,"run_spec_review":1}and not v.get("pending"),"REVISION")
    bodies={}
    for name,ref in b["files"].items():
        p=Path(ref["path"]);require(p.is_absolute(),"FILE_PATH")
        raw=pr.check(p).read_bytes()
        require(sha(raw)==ref["sha256"] and len(raw)==ref["bytes"],"EVIDENCE_BYTES")
        bodies[name]=raw
    review=json.loads(bodies["review"]);require(review["verdict"]=="REVISE" and len(review["findings"])==4,"REVIEW")
    tests=json.loads(bodies["synthetic"])
    require(tests["status"]=="FAIL" and tests["binding"]["files"]["run.py"]==sha(bodies["harness"])
        and tests["binding"]["files"]["revised.ipynb"]==v["notebook_revision_result"]["notebook_sha256"],"TEST_BINDING")
    require(tests["isolation"]=={"credentials":False,"denied_paths":15,"network":"UNSHARED",
        "package_read_only":True,"patient_mounts":False,"status":"ISOLATED","workspace_writable":True},"ISOLATION")
    for ref in v["artifacts"]:
        rel=Path(ref["path"]);require(not rel.is_absolute()and".."not in rel.parts,"ARTIFACT_PATH")
        require(sha(pr.check(d.context/rel).read_bytes())==ref["sha256"],"ARTIFACT_BYTES")
    return v,bodies
def supplemented(value,question_ref,validator_ref,approval):
    require(not any(r["id"]in {"question","validator"}for r in value["artifacts"]),"ARTIFACT_COLLISION")
    updated=copy.deepcopy(value)
    updated["artifacts"] += [question_ref,validator_ref]
    updated["interventions"].append({"kind":CHANGE,"checkpoint_sha256":PIN,
        "review_sha256":approval["report_sha256"],"preserved_calls":2,"new_allowance":0,
        "original_findings_preserved":True,"scientific_verdict_unchanged":True})
    return updated
def apply(d,b,approval,question):
    from orchestrator import private_records as pr
    from orchestrator.manual_executor import lock
    with lock(d.state/"driver.lock"):
        d.guard();value,bodies=originals(d,b)
        require(not any(r["id"]in {"question","validator"}for r in value["artifacts"]),"ARTIFACT_COLLISION")
        dest=d.state/CHANGE;require(not dest.exists()and not dest.is_symlink(),"ALREADY_ATTEMPTED")
        validator=(b"# Current installed L host synthetic evidence\n"
            b"Original FAIL is preserved. This is not the author-side static checker. "
            b"The older component inventory remains historical, not the installed harness.\n"
            b"## Exact installed harness\n"+bodies["harness"]+
            b"\n## Exact original host receipt\n"+bodies["synthetic"])
        pr.mkdir(dest);pr.write_bytes(dest/"original-state.json",b["state_row"]["payload"].encode())
        pr.write_bytes(dest/"INTENT.json",canonical({"source":approval["source_sha"],"review":approval["report_sha256"],"model_calls":0}))
        temporary=copy.deepcopy(value)
        d.artifact(temporary,"question","L-evidence-correction-20261013.md",question,1)
        d.artifact(temporary,"validator","L-current-host-evidence-20261013.md",validator,1)
        refs=[next(r for r in temporary["artifacts"]if r["id"]==k)for k in ("question","validator")]
        updated=supplemented(value,*refs,approval)
        require({k:v for k,v in updated.items()if k not in {"artifacts","interventions"}}==
                {k:v for k,v in value.items()if k not in {"artifacts","interventions"}},"STATE_SCOPE")
        # Assemble both real inputs without invoking any model. A delivery
        # failure leaves the original state intact and the intent preserved.
        measurements={}
        for stage in ("run_spec_author","run_spec_review"):
            work=dest/(stage+"-preflight")
            body,measurement=d.prepare_input(updated,stage,work)
            require(all(ref["sha256"] in body for ref in refs),"INPUT_BINDINGS")
            measurements[stage]=measurement
        pr.write_bytes(dest/"INPUT_PREFLIGHT.json",canonical(measurements))
        db=d.store.db;db.execute("BEGIN IMMEDIATE")
        try:
            originals(d,b)
            db.execute("UPDATE manual_state SET payload=? WHERE id=1",(json.dumps(updated),))
            db.execute("COMMIT")
        except BaseException:db.execute("ROLLBACK");raise
        originals(d,b,state=False)
        require(d.current()==updated,"COMMITTED_STATE")
        result={"status":"EVIDENCE_SUPPLEMENTED_NO_CALL","source":approval["source_sha"],
            "review_sha256":approval["report_sha256"],"model_calls":0,"new_allowance":0,
            "preserved_calls":2,"phase":updated["phase"],"artifacts":refs}
        pr.write_bytes(dest/"COMPLETE.json",canonical(result));return result
def worker(source,review):
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,"SERVICE_OWNER")
    approval,b,question=authority(source,review)
    from orchestrator.manual_host_guard import trusted
    spec=importlib.util.spec_from_file_location("_installed_l_runtime",trusted(BASE/"tools/colab_l_runtime.py"))
    parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
    old=parent.authority();scope,n=parent.metadata()
    require(old["source_sha"]=="b1249aaf4f9782c6d60270a28e8e787385211ce5"
        and old["report_sha256"]=="ee2d22aadbf82345c8d8b2301cb6420e254e14464292a8ef72059c7357a2a3f0","INSTALLED_PARENT")
    require(os.environ.get("RESEARCH_MANUAL_RUNTIME_CONFIG")==n["runtime"]
        and approval["runtime_sha256"]==sha(trusted(n["runtime"]).read_bytes()),"RUNTIME")
    props=dict(x.split("=",1)for x in subprocess.check_output(["systemctl","show",n["unit"],"-p","MainPID","-p","ActiveState"],text=True).splitlines())
    require(props=={"MainPID":"0","ActiveState":"inactive"},"UNIT_LIVE")
    parent.held_prior();parent.connect_qualifier()
    from orchestrator import colab_pnormct_policy
    colab_pnormct_policy.connect()
    os.environ.update(GIT_CONFIG_COUNT="1",GIT_CONFIG_KEY_0="safe.directory",GIT_CONFIG_VALUE_0=str(BASE))
    from orchestrator.analysis_driver import AnalysisDriver
    from orchestrator.colab_pnorm_v2_feedback import prepared
    d=prepared(AnalysisDriver)(scope["new_lane"])
    try:return apply(d,b,approval,question)
    finally:d.store.db.close();d.store.batch.db.close()
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--source",type=Path,required=True);parser.add_argument("--review",type=Path,required=True)
    args=parser.parse_args();return worker(args.source,args.review)
if __name__=="__main__":
    os.umask(0o077);sys.path.insert(0,str(BASE));print(json.dumps(main(),sort_keys=True))
