"""Four funded meeting calls on the existing lane; no scientific code or executor."""
from pathlib import Path
import copy, hashlib, json
RUN = "meeting-775e80719952cfe222a61dcd"
CHANGE = "scientific-batch140-20261013"
DOCUMENT = "docs/MEETING_BATCH140_CHECKPOINT_PRIVATE.json"
PIN = "87295ed72b700a0123b3ad69684e9562ee684ea6639e51659b84363fc0ac6da1"
QUESTION = "docs/MEETING_BATCH140_QUESTION.md"
QUESTION_PIN = "8fa3ec5f6cd65d0f2d75293f16f0ccea335470cd4047c56e391416f9abc13c63"
def require(ok, why):
    if not ok: raise ValueError("MEETING_BATCH140_" + why)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(v): return json.dumps(v, sort_keys=True, separators=(",", ":")).encode()

def document(root):
    from orchestrator import private_records as pr
    raw = pr.check(Path(root)/DOCUMENT).read_bytes()
    require(sha(raw) == PIN, "CHECKPOINT")
    b = json.loads(raw)
    question = pr.check(Path(root)/QUESTION).read_bytes()
    evidence = pr.check(Path(root)/b["evidence_path"]).read_bytes()
    require(b["run_id"] == RUN and b["preserved_calls"] == 4 and b["new_allowance"] == 0,
            "CHECKPOINT_SCOPE")
    require(sha(question) == QUESTION_PIN and sha(evidence) == b["evidence_sha256"],
            "SOURCE_BINDINGS")
    return b, question, evidence

def activate(root, review_sha256):
    """Only replace the exhausted allocation; every original guard remains."""
    from orchestrator import meeting_preparation as old
    import importlib.util
    spec = importlib.util.spec_from_file_location("_batch140_policy", Path(root)/"orchestrator/scientific_batch140.py")
    policy = importlib.util.module_from_spec(spec); spec.loader.exec_module(policy)
    scope = policy.document(root)
    original = old.batch_allowance
    def funded(accounts, original_scope):
        require(original_scope == old.document(), "ORIGINAL_SCOPE")
        old.preserved(accounts, original_scope)
        return policy.allowance(accounts, RUN, scope, review_sha256)
    old.batch_allowance = funded
    return original

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
    require(len(b["local_rows"])==len(b["global_rows"])==4 and all(r["status"]=="COMPLETE"for r in b["local_rows"]),"OUTCOMES")
    if state:require(dict(d.store.db.execute("SELECT * FROM manual_state WHERE id=1").fetchone())==b["state_row"],"STATE")
    v=json.loads(b["state_row"]["payload"])
    require(v["phase"]=="COMMIT_SPEC" and v.get("reason") is None
        and v["rounds"]=={"run_spec_author":2,"run_spec_review":2}and not v.get("pending"),"REVISION")
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
    updated=copy.deepcopy(value)
    updated["artifacts"] = [r for r in updated["artifacts"] if r["id"] not in {"question", "prior_results"}] + [question_ref,evidence_ref]
    updated["interventions"].append({"kind":CHANGE,"checkpoint_sha256":PIN,
        "review_sha256":approval["report_sha256"],"preserved_calls":4,"new_allowance":4,
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
        dest=d.state/CHANGE;require(not dest.exists()and not dest.is_symlink(),"ALREADY_ATTEMPTED")
        require(sha(evidence)==b["evidence_sha256"],"SOURCE_EVIDENCE")
        require(sha(question)==b["question_sha256"],"QUESTION_BYTES")
        pr.mkdir(dest);pr.write_bytes(dest/"original-state.json",b["state_row"]["payload"].encode())
        pr.write_bytes(dest/"INTENT.json",canonical({"source":approval["source_sha"],"review":approval["report_sha256"],"model_calls":0}))
        temporary=copy.deepcopy(value)
        d.artifact(temporary,"question","meeting-batch140-question-20261013.md",question,1)
        d.artifact(temporary,"prior_results","meeting-batch140-evidence-20261013.md",evidence,1)
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
            "review_sha256":approval["report_sha256"],"model_calls":0,"new_allowance":4,
            "preserved_calls":4,"phase":updated["phase"],"artifacts":refs}
        pr.write_bytes(dest/"COMPLETE.json",canonical(result));return result
