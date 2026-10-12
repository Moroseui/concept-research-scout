import json
import sqlite3
from pathlib import Path
import pytest
from orchestrator import idea2_results_intake as intake, idea2_cpu_contract as c
from orchestrator.diagnostics_contract import validate_outputs

SOURCE="a"*40
REVIEW="b"*64

def write(work, name, value):
    p=work/name;p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    p.write_bytes(value if isinstance(value,bytes)else c.encoded(value));p.chmod(0o600)

def complete_fixture(tmp_path,monkeypatch):
    work=tmp_path/"work";work.mkdir(mode=0o700)
    code=b"# synthetic infrastructure fixture";tests=b"# synthetic fixture test"
    monkeypatch.setattr(c,"CODE",c.sha(code));monkeypatch.setattr(c,"TESTS",c.sha(tests))
    pc={"schema":"diagnostics-program-contract/v1","outputs":sorted(intake.OUTPUTS),
        "validation_checks":["synthetic-integrity"],"requirements":{"python":"3.12","distributions":{}},
        "input_contract_sha256":c.PINS["input-contract.json"],"input_capture_sha256":c.PINS["capture.jsonl"]}
    monkeypatch.setattr(intake,"PROGRAM_CONTRACT_SHA",c.sha(c.encoded(pc)))
    inp={"synthetic.bin":{"bytes":5,"sha256":c.sha(b"hello")}}
    runtime={"run_id":c.RUN,"source":SOURCE,"spec_sha256":c.SPEC,"code_sha256":c.CODE,
             "execution_plan_sha256":c.PINS["execution-plan.json"],
             "input_contract_sha256":c.PINS["input-contract.json"],"environment_sha256":c.ENVIRONMENT,
             "input_verification":{"files":inp}}
    full={**pc,"runtime":runtime}
    package={"analysis.py":code,"test_analysis.py":tests,"contract.json":c.encoded(full),"run.py":b"# wrapper"}
    for name,raw in package.items():write(work,"package/"+name,raw)
    pins={n:{"sha256":c.sha(raw),"bytes":len(raw)}for n,raw in package.items()}
    binding={**runtime,"program_sha256":c.PROGRAM,"scientific_review_sha256":c.REVIEW,
             "implementation_review_sha256":REVIEW,"venue":"existing-server-cpu",
             "incremental_micro_usd":0,"package_files":pins,"program_contract":pc}
    db=sqlite3.connect(work/"jobs.sqlite")
    db.executescript("CREATE TABLE jobs(id TEXT,binding TEXT,status TEXT,phase TEXT); CREATE TABLE manual_packages(job TEXT,manifest TEXT);")
    db.execute("INSERT INTO jobs VALUES(?,?,?,?)",(intake.JOB,c.encoded(binding).decode(),"READY","patient"))
    db.execute("INSERT INTO manual_packages VALUES(?,?)",(intake.JOB,c.encoded(pins).decode()));db.commit();db.close()
    (work/"jobs.sqlite").chmod(0o600)
    controls=[]
    for mode,exit in [("readonly",0),("deliberately-writable",1)]:
        streams={"stdout":b"synthetic control","stderr":b""}
        for name,raw in streams.items():write(work,"qualification/"+mode+"/"+name,raw)
        controls.append({"mode":mode,"exit":exit,**{name+"_sha256":c.sha(raw)for name,raw in streams.items()}})
    write(work,"qualification/COMPLETE.json",{"status":"PASS","source":SOURCE,
        "review_sha256":REVIEW,"patient_payloads_opened":0,"model_calls":0,"controls":controls})
    observed={"files":1,"bytes":5,"manifest_sha256":c.sha(c.encoded(inp))}
    monkeypatch.setattr(intake,"EXECUTION_INPUTS",observed)
    admission={**observed,"manifest_sha256":c.sha(c.encoded({"full_synthetic_manifest":inp}))}
    monkeypatch.setattr(intake,"ADMISSION_INPUTS",admission)
    before={"inputs":observed,"package":c.verify_tree(work/"package",pins)}
    write(work,"execution/before.json",before);write(work,"execution/after.json",before)
    intent={"job":intake.JOB,"binding_sha256":c.sha(c.encoded(binding)),"lease":"synthetic",
            "started_at":1,"incremental_micro_usd":0}
    write(work,"execution/dispatch-intent.json",intent)
    write(work,"execution/console.log",b"synthetic only")
    write(work,"execution/process-exit.json",{**intent,"exit_code":0,"uncertain":False,"valid":True,
        "error":None,"completed_at":2,"console_sha256":c.sha(b"synthetic only")})
    outputs={n:b'{"count": 0}'for n in intake.OUTPUTS if n.endswith(".json")and n!="validation.json"}
    outputs["limitations.md"]=b"Synthetic fixture only."
    for n,raw in outputs.items():write(work,"execution/return/"+n,raw)
    validation={"schema":"diagnostics-validation/v1",
        **{k:runtime[k]for k in ("run_id","source","spec_sha256","code_sha256","execution_plan_sha256","input_contract_sha256","environment_sha256")},
        "files":{n:{"sha256":c.sha(raw),"bytes":len(raw)}for n,raw in outputs.items()},
        "checks":[{"id":"synthetic-integrity","status":"PASS","evidence":sorted(outputs)}]}
    write(work,"execution/return/validation.json",validation)
    write(work,"execution/validation.json",validate_outputs(work/"execution/return",binding))
    write(work,"EXECUTION_COMPLETE.json",{"status":"EXECUTED_VALIDATED_NOT_SCIENTIFICALLY_ACCEPTED",
        "job":intake.JOB,"source":SOURCE,"review_sha256":REVIEW,"incremental_micro_usd":0,
        "return_path":str(work/"execution/return"),"scientific_acceptance":False,"interpretation_required":True,
        "admission":{"status":"QUEUED_EXISTING_SERVER_CPU","job":intake.JOB,"input_verification":admission,
                     "incremental_micro_usd":0,"scientific_acceptance":False}})
    return work

def test_complete_snapshot_yields_only_original_aggregates_without_writes(tmp_path,monkeypatch):
    work=complete_fixture(tmp_path,monkeypatch)
    before={str(p.relative_to(work)):p.read_bytes()for p in work.rglob("*")if p.is_file()}
    result=intake.verify(work,SOURCE,REVIEW)
    assert set(result["files"])==intake.OUTPUTS
    assert result["receipt"]["scientifically_accepted"] is False
    assert result["receipt"]["successor_execution_authorized"] is False
    assert not (work/"synthetic.bin").exists() # no input payload is required/opened
    assert before=={str(p.relative_to(work)):p.read_bytes()for p in work.rglob("*")if p.is_file()}

@pytest.mark.parametrize("name,key,value,match",[
    ("execution/process-exit.json","uncertain",True,"TERMINAL_EXECUTION"),
    ("execution/process-exit.json","valid",False,"TERMINAL_EXECUTION"),
    ("execution/process-exit.json","exit_code",1,"TERMINAL_EXECUTION"),
    ("execution/process-exit.json","error","failure","TERMINAL_EXECUTION"),
    ("EXECUTION_COMPLETE.json","scientific_acceptance",True,"FINAL_RECEIPT"),
    ("EXECUTION_COMPLETE.json","source","0"*40,"FINAL_RECEIPT"),
    ("qualification/COMPLETE.json","status","FAILED","QUALIFICATION"),
])
def test_terminal_or_authority_failures_refuse(tmp_path,monkeypatch,name,key,value,match):
    work=complete_fixture(tmp_path,monkeypatch);v=json.loads((work/name).read_bytes());v[key]=value;write(work,name,v)
    with pytest.raises(ValueError,match=match):intake.verify(work,SOURCE,REVIEW)

def test_post_hash_difference_refuses(tmp_path,monkeypatch):
    work=complete_fixture(tmp_path,monkeypatch);v=json.loads((work/"execution/after.json").read_bytes())
    v["inputs"]["manifest_sha256"]="0"*64;write(work,"execution/after.json",v)
    with pytest.raises(ValueError,match="BEFORE_AFTER"):intake.verify(work,SOURCE,REVIEW)

@pytest.mark.parametrize("change",["alter","extra","symlink"])
def test_result_tampering_refused(tmp_path,monkeypatch,change):
    work=complete_fixture(tmp_path,monkeypatch);p=work/"execution/return/paired.json"
    if change=="alter":p.write_text('{"count": 1}')
    elif change=="extra":write(work,"execution/return/unexpected.json",b"{}")
    else:
        raw=p.read_bytes();p.unlink();target=work/"elsewhere.json";target.write_bytes(raw);p.symlink_to(target)
    with pytest.raises(ValueError):intake.verify(work,SOURCE,REVIEW)

def test_missing_database_never_created(tmp_path):
    p=tmp_path/"missing.sqlite"
    with pytest.raises((ValueError,FileNotFoundError)):intake.read_job(p)
    assert not p.exists()

def test_running_job_refused(tmp_path,monkeypatch):
    work=complete_fixture(tmp_path,monkeypatch);db=sqlite3.connect(work/"jobs.sqlite")
    db.execute("UPDATE jobs SET status='RUNNING',phase='dispatch'");db.commit();db.close()
    with pytest.raises(ValueError,match="JOB_NOT_EXECUTED"):intake.verify(work,SOURCE,REVIEW)

@pytest.mark.parametrize("source,review",[("0"*40,REVIEW),(SOURCE,"0"*64),("bad",REVIEW)])
def test_other_release_identity_cannot_reuse_terminal_result(tmp_path,monkeypatch,source,review):
    work=complete_fixture(tmp_path,monkeypatch)
    with pytest.raises(ValueError,match="APPROVAL_IDENTITY|EXECUTION_BINDING"):
        intake.verify(work,source,review)

def test_no_future_result_is_fabricated(tmp_path):
    work=tmp_path/"not-executed";work.mkdir(mode=0o700)
    with pytest.raises((FileNotFoundError,ValueError)):
        intake.verify(work,SOURCE,REVIEW)
    assert not list(work.iterdir())
