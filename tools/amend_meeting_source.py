"""One reviewed source amendment; prior approval and accounting remain intact."""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, os, subprocess, sys
BASE=Path("/opt/research-system/manual-repair-helpers/meeting-preparation-20261013")
CHANGE="meeting-source-amendment-20261013"
RUN="meeting-775e80719952cfe222a61dcd"
DOCUMENT="docs/MEETING_SOURCE_AMENDMENT_PRIVATE.json"
PIN="ed0de4bed57452f0632cf089a7bcc7aadbd1fea94e1b2ea82e5efc70ae2c14c5"
ENTRY="tools/amend_meeting_source.py"
BRANCH="astra/manual-meeting-source-amendment-20261013"
QUESTION="docs/MEETING_SOURCE_AMENDMENT.md"
QUESTION_PIN="de5b6ba0df60aae92c0d2e0cf5bc4c2767790943c408778a55106dd74aac9f15"
def require(ok,why):
    if not ok:raise ValueError("MEETING_AMENDMENT_"+why)
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
                 "orchestrator/meeting_preparation.py","orchestrator/scientific_program.py",
                 "tools/meeting_preparation_runtime.py","tests/test_meeting_source_amendment.py",
                 "docs/MEETING_SOURCE_EVIDENCE_PRIVATE.md","orchestrator/author_revision_accounting.py"]:
        require(name in m["source_files"],"WHOLE_COMPONENT")
    raw=trusted(source/DOCUMENT).read_bytes();require(sha(raw)==PIN,"CHECKPOINT")
    b=json.loads(raw);require(b["run_id"]==RUN and b["preserved_calls"]==2 and b["new_allowance"]==0,"SCOPE")
    question=trusted(source/QUESTION).read_bytes();require(sha(question)==QUESTION_PIN,"QUESTION")
    evidence=trusted(source/b["evidence_path"]).read_bytes()
    require(b["evidence_path"]=="docs/MEETING_SOURCE_EVIDENCE_PRIVATE.md"
        and sha(evidence)==b["evidence_sha256"],"SOURCE_EVIDENCE")
    return a,b,question,evidence
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
    require(v["phase"]=="COMMIT_SPEC" and v.get("reason") is None
        and v["rounds"]=={"run_spec_author":1,"run_spec_review":1}and not v.get("pending"),"REVISION")
    bodies={}
    for name,ref in b["files"].items():
        p=Path(ref["path"]);require(p.is_absolute(),"FILE_PATH")
        raw=pr.check(p).read_bytes()
        require(sha(raw)==ref["sha256"] and len(raw)==ref["bytes"],"EVIDENCE_BYTES")
        bodies[name]=raw
    review=json.loads(bodies["review"])
    require(review["verdict"]=="APPROVE" and review["findings"]==[], "PRESERVED_APPROVAL")
    tests=json.loads(bodies["synthetic"])
    require(tests["status"]=="PASS" and tests["binding"]["files"]["analysis.py"]==sha(bodies["accepted_source"])
        and tests["binding"]["files"]["test_analysis.py"]==sha(bodies["accepted_tests"])
        and sha(bodies["synthetic"])==v["program_result"]["synthetic_receipt_sha256"],"TEST_BINDING")
    require(tests["isolation"]=={"credentials":False,"denied_paths":15,"network":"UNSHARED",
        "package_read_only":True,"patient_mounts":False,"status":"ISOLATED","workspace_writable":True},"ISOLATION")
    for ref in v["artifacts"]:
        rel=Path(ref["path"]);require(not rel.is_absolute()and".."not in rel.parts,"ARTIFACT_PATH")
        require(sha(pr.check(d.context/rel).read_bytes())==ref["sha256"],"ARTIFACT_BYTES")
    return v,bodies
def supplemented(value,question_ref,evidence_ref,approval):
    require(not any(r["id"]in {"question","prior_results"}for r in value["artifacts"]),"ARTIFACT_COLLISION")
    updated=copy.deepcopy(value)
    updated["artifacts"] += [question_ref,evidence_ref]
    updated["interventions"].append({"kind":CHANGE,"checkpoint_sha256":PIN,
        "review_sha256":approval["report_sha256"],"preserved_calls":2,"new_allowance":0,
        "original_approval_preserved":True,"scientific_verdict_unchanged":True,
        "original_phase":value["phase"],"source_amendment_not_reviewer_revise":True})
    updated["phase"]="run_spec_author"
    updated["reason"]="SOURCE_AMENDMENT_REQUIRED"
    return updated
def apply(d,b,approval,question,evidence):
    from orchestrator import private_records as pr
    from orchestrator.manual_executor import lock
    with lock(d.state/"driver.lock"):
        d.guard();value,bodies=originals(d,b)
        require(not any(r["id"]in {"question","prior_results"}for r in value["artifacts"]),"ARTIFACT_COLLISION")
        dest=d.state/CHANGE;require(not dest.exists()and not dest.is_symlink(),"ALREADY_ATTEMPTED")
        require(sha(evidence)==b["evidence_sha256"],"SOURCE_EVIDENCE")
        pr.mkdir(dest);pr.write_bytes(dest/"original-state.json",b["state_row"]["payload"].encode())
        pr.write_bytes(dest/"INTENT.json",canonical({"source":approval["source_sha"],"review":approval["report_sha256"],"model_calls":0}))
        temporary=copy.deepcopy(value)
        d.artifact(temporary,"question","meeting-source-amendment-20261013.md",question,1)
        d.artifact(temporary,"prior_results","meeting-source-evidence-20261013.md",evidence,1)
        refs=[next(r for r in temporary["artifacts"]if r["id"]==k)for k in ("question","prior_results")]
        updated=supplemented(value,*refs,approval)
        require({k:v for k,v in updated.items()if k not in {"artifacts","interventions","phase","reason"}}==
                {k:v for k,v in value.items()if k not in {"artifacts","interventions","phase","reason"}},"STATE_SCOPE")
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
        result={"status":"SOURCE_AMENDMENT_READY_NO_CALL","source":approval["source_sha"],
            "review_sha256":approval["report_sha256"],"model_calls":0,"new_allowance":0,
            "preserved_calls":2,"phase":updated["phase"],"artifacts":refs}
        pr.write_bytes(dest/"COMPLETE.json",canonical(result));return result
def worker(source,review):
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,"SERVICE_OWNER")
    approval,b,question,evidence=authority(source,review)
    from orchestrator.manual_host_guard import trusted
    spec=importlib.util.spec_from_file_location("_installed_meeting_runtime",trusted(BASE/"tools/meeting_preparation_runtime.py"))
    parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
    old=parent.authority();scope,n=parent.metadata()
    require(old["source_sha"]=="b06d64da7568ad1dbd51926c985806e6719897cb"
        and old["report_sha256"]=="23538a2c19750ed70ddc2a9efae83bc960b0e91894f7d1d2c0819be844741ab5","INSTALLED_PARENT")
    require(os.environ.get("RESEARCH_MANUAL_RUNTIME_CONFIG")==n["runtime"]
        and approval["runtime_sha256"]==sha(trusted(n["runtime"]).read_bytes()),"RUNTIME")
    props=dict(x.split("=",1)for x in subprocess.check_output(["systemctl","show",n["unit"],"-p","MainPID","-p","ActiveState"],text=True).splitlines())
    require(props=={"MainPID":"0","ActiveState":"inactive"},"UNIT_LIVE")
    parent.held_prior();parent.connect_qualifier()
    os.environ.update(GIT_CONFIG_COUNT="1",GIT_CONFIG_KEY_0="safe.directory",GIT_CONFIG_VALUE_0=str(BASE))
    from orchestrator.meeting_preparation import MeetingDriver
    d=MeetingDriver(scope["new_lane"])
    try:return apply(d,b,approval,question,evidence)
    finally:d.store.db.close();d.store.batch.db.close()
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--source",type=Path,required=True);parser.add_argument("--review",type=Path,required=True)
    args=parser.parse_args();return worker(args.source,args.review)
if __name__=="__main__":
    os.umask(0o077);sys.path.insert(0,str(BASE));print(json.dumps(main(),sort_keys=True))
