"""Real assembly, ledger and MCP submission on labelled synthetic evidence only."""
import json
from pathlib import Path
import pytest
from orchestrator import experiment_approval as approval, experiment_context as ec
from orchestrator import review_submission as rs, private_records as pr, scientific_program as sp
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import digest
from test_experiment_context import experiment, root
from test_experiment_revisions import store_for, as_item4
from test_scientific_program import program


@pytest.fixture(params=[6,4])
def reviewed(experiment, monkeypatch, request):
    d,value = experiment
    d.artifact = lambda *a:Driver.artifact(d,*a)
    author = d.state/"author"
    pr.mkdir(author)
    payload = program(d.config["run_id"], d.config["execution_scope"]["plan_sha256"])
    pr.write_bytes(author/"analysis.program.json", rs.canonical(payload))
    pr.write_text(author/"SPEC.proposed.md", "# Synthetic fixture, not scientific approval\nrun_id: "+
        payload["run_id"]+"\nexecution_plan_sha256: "+payload["execution_plan_sha256"]+"\n")
    def synthetic(folder,files,environment):
        files=dict(files)
        if "execution.py" in files:
            from orchestrator.experiment_modal_package import support_files
            files.update({name:raw.decode() for name,raw in support_files().items()})
        if request.node.callspec.params.get("wrong_tested_code",False):
            name=next(iter(files));files[name]+="\n# Different synthetic tested bytes\n"
        pr.mkdir(folder, parents=True)
        pr.mkdir(folder/"package")
        for name,text in files.items():pr.write_bytes(folder/"package"/name,text.encode())
        pins={name:digest(text.encode()) for name,text in files.items()}
        receipt = {"status":"PASS", "synthetic_test_fixture":True,
            "binding":{"environment":environment,"patient_data":False,"files":pins},
            "preserved_files":{"package/"+name:pin for name,pin in pins.items()}}
        if "execution.py" in pins:
            receipt["tests"] = {"records":[{"test":"test_execution_module", "status":"PASS",
                "details":{"module_sha256":pins["execution.py"], "tests_run":1,
                    "failures":0,"errors":0,"skipped":0,"expected_failures":0,"unexpected_successes":0,
                    "patient_data":False,"network":False}}]}
        pr.write_text(folder/"receipt.json", json.dumps(receipt))
        return receipt
    monkeypatch.setattr(sp,"run",synthetic)  # OS sandbox proof belongs to native isolation tests.
    ec.accept_author(d,value,{"id":"synthetic-author", "round":1, "workspace":str(author)})
    if request.param in (4, "authored4", "partitions4", "requirements4"):
        # Synthetic notebook/receipt fixture. This exercises the real approval
        # consumer and assembly, not the scientific patching/OS-isolation proof.
        from test_scientific_intake import save_registry
        from orchestrator import manual_context as mc
        as_item4(d)
        reg = json.loads((d.context/d.config["private_intake"]["path"]).read_bytes())
        reg.update(task=ec.TASKS[4],idea_ids=[ec.TASKS[4]])
        d.config["private_intake"] = save_registry(d.context,reg)
        prep=json.loads((d.state/"preparation-plan.json").read_bytes())
        prep["private_intake"]=d.config["private_intake"]
        pr.write_text(d.state/"preparation-plan.json",json.dumps(prep))
        d.config["plan_sha256"]=digest((d.state/"preparation-plan.json").read_bytes())
        folder=d.state/"notebook-revisions/author-1";pr.mkdir(folder,parents=True)
        d.config["notebook_revision"]["environment"]={"environment_root":"/synthetic-tools","environment_sha256":"a"*64}
        prep=json.loads((d.state/"preparation-plan.json").read_bytes())
        prep["notebook_revision"]=d.config["notebook_revision"]
        pr.write_text(d.state/"preparation-plan.json",json.dumps(prep))
        d.config["plan_sha256"]=digest((d.state/"preparation-plan.json").read_bytes())
        from test_notebook_execution import notebook
        from orchestrator.notebook_execution import extract
        fixture_notebook=notebook()
        if request.param in ("partitions4", "requirements4"):
            from test_experiment_plan_output import configure_authored
            from partition_fixture import register, module_source
            configure_authored(d);register(d)
            fixture_notebook=notebook(module_source())
        files={"revised.ipynb":("notebook_source",fixture_notebook),
            "notebook.diff":("notebook_diff",b"Synthetic notebook diff\n"),
            "patch-receipt.json":("notebook_provenance",b'{"synthetic_fixture":true}'),
            "carried-conditions.json":("execution_conditions",b'{"synthetic_fixture":true}')}
        tests=synthetic(folder/"synthetic",{"revised.ipynb":files["revised.ipynb"][1].decode(),
            "execution.py":extract(files["revised.ipynb"][1]).decode()},d.config["notebook_revision"]["environment"])
        for name,(kind,raw) in files.items():
            pr.write_bytes(folder/name,raw);d.artifact(value,kind,"fixture-"+name,raw,1)
        d.artifact(value,"notebook_patch","fixture-patch.json",b'{"synthetic_fixture":true}',1)
        d.artifact(value,"synthetic_tests","fixture-tests.json",rs.canonical(tests),2)
        spec=("# Synthetic notebook spec\nrun_id: "+d.config["run_id"]+"\nexecution_plan_sha256: "+d.config["execution_scope"]["plan_sha256"]+"\n").encode()
        pr.write_bytes(author/"SPEC.proposed.md",spec)
        for kind in ("run_spec","proposed_run_spec"):d.artifact(value,kind,"fixture-"+kind+".md",spec,2)
        value["notebook_revision_result"]={"folder":str(folder),"synthetic_status":"PASS",
            "notebook_sha256":digest(files["revised.ipynb"][1]),"tests_sha256":digest(rs.canonical(tests))}
        value["artifacts"]=[r for r in value["artifacts"] if r["type"] not in mc.PROGRAM_TYPES]
    if request.param in ("authored4", "partitions4", "requirements4"):
        from test_experiment_plan_output import configure_authored, synthetic_plan
        from orchestrator import experiment_plan_output as authored
        configure_authored(d)
        plan = synthetic_plan(d.config["execution_scope"])
        if request.param in ("partitions4", "requirements4"):
            from partition_fixture import scope
            cohort_raw,_ = authored.cohort(d)
            monkeypatch.setattr("orchestrator.experiment_preprocessing.COHORT",digest(cohort_raw)) # Synthetic cohort only.
            selected=scope(cohort_raw);plan["preprocessing"]=[selected]
            for fit in plan["fits"]: fit["preprocessing_id"]=selected["id"]
        if request.param == "requirements4":
            from test_experiment_environment_requirements import declared_plan
            plan = declared_plan(plan)
        proposed = rs.canonical(plan)
        if request.param != "requirements4":
            authored.preserve(d, value, {"round":1}, proposed)
        spec=("# Synthetic author-owned plan; no scientific judgment\nrun_id: "+d.config["run_id"]+
            "\noperator_scope_sha256: "+d.config["execution_scope"]["plan_sha256"]+
            "\nexecution_plan_sha256: "+digest(proposed)+"\n").encode()
        pr.write_bytes(author/"SPEC.proposed.md",spec)
        if request.param == "requirements4":
            pr.write_bytes(author/authored.OUTPUT, proposed)
            def existing_synthetic_notebook(*args):
                # Reuse the explicitly labelled synthetic code/test fixture;
                # no production plan, scan, SPEC or preservation check is mocked.
                assert value["notebook_revision_result"]["synthetic_status"] == "PASS"
            monkeypatch.setattr("orchestrator.notebook_revision.prepare_artifacts",existing_synthetic_notebook)
            ec.accept_author(d,value,{"round":3,"workspace":str(author)})
        else:
            for kind in ("run_spec","proposed_run_spec"):d.artifact(value,kind,"authored-"+kind+".md",spec,3)
    store,_ = store_for(d)
    d.config.update(source="a"*40, clients={"runtime_config_sha256":"b"*64})
    d.config["workspace_root"] = str(d.state/"scientific-workspaces")
    stage = "run_spec_review";work = Path(d.config["workspace_root"])/(stage+"-1")
    if request.param == 6:
        prompt,measured = Driver.prepare_input(d,value,stage,work)
    else:
        prep=json.loads((d.state/"preparation-plan.json").read_bytes())
        artifacts=value["artifacts"]+[{"id":"frozen-execution-plan","type":"configuration","version":1,**prep["execution_plan"]}]
        prompt,measured=mc.prepare(d.context,stage=stage,idea_ids=d.config["idea_ids"],
            task="Synthetic notebook approval interface test",artifacts=artifacts,workspace=work,
            private_intake=d.config["private_intake"],structured_review=True,execution_mode=ec.TASKS[4])
    pr.write_text(work/"prompt.md",prompt);pr.atomic(work/"input-measurement.json",measured)
    call_id = digest((d.config["run_id"]+":"+stage+":1").encode())
    bindings = {"call_id":call_id,"run_id":d.config["run_id"],"stage":stage,
        "source_sha":d.config["source"],"runtime_sha256":d.config["clients"]["runtime_config_sha256"],
        "input_sha256":digest(prompt.encode())}
    pins = rs.prepare(work,"scientific",bindings)
    verdict=request.node.callspec.params.get("verdict","APPROVE")
    decision = {"verdict":verdict,"findings":[],"rationale":"Synthetic submission fixture; no model or research judgment.","bindings":bindings}
    ack = rs.submit(work,pins["config_sha256"],decision)
    events = [
        {"type":"assistant","session_id":"synthetic-session","message":{"content":[
            {"type":"tool_use","id":"submit-1","name":rs.TOOL,"input":decision}]}},
        {"type":"user","session_id":"synthetic-session","message":{"content":[
            {"type":"tool_result","tool_use_id":"submit-1","content":json.dumps(ack)}]}},
        {"type":"result","subtype":"success","is_error":False,"session_id":"synthetic-session"}]
    console=b"\n".join(rs.canonical(x) for x in events)
    pr.write_bytes(work/"console.log",console)
    native={"review_submission":rs.collect_scientific(work,console),"console_sha256":digest(console)}
    receipt={"stage":stage,"workspace":str(work),"input_sha256":digest(prompt.encode()),
        "submission_preflight":pins,"native":native,"outcome":"COMPLETE",
        "output_sha256":{"review.json":digest((work/"review.json").read_bytes())}}
    monkeypatch.setattr("orchestrator.connectivity.require",lambda *a,**k:{"synthetic_fixture":True})
    ident,n,charged=store.reserve_call(d.config["run_id"],stage,d.config["source"],"astra/manual-test",d.config["policy"],receipt)
    assert ident==call_id and n==1
    store.finish_call(ident,charged,"COMPLETE")
    value.update(pending={"id":ident,"round":n,"stage":stage,"workspace":str(work)},rounds={})
    d.finding_prefix=lambda s:Driver.finding_prefix(d,s)
    d.save=lambda v:None
    d.status=lambda:value
    return d,value,work


def test_actual_completed_review_seals_exact_input_code_and_submission(reviewed):
    d,value,work=reviewed
    raw=(work/"review.json").read_bytes();console=(work/"console.log").read_bytes()
    Driver._accept_completed(d,value)
    assert value["phase"]=="COMMIT_SPEC" and "pending" not in value
    manifest=approval.verify(d,value)
    assert manifest["review_sha256"]==digest(raw)
    assert manifest["execution_admitted"] is False
    assert set(manifest["code_files"])==({"analysis.py","test_analysis.py","analysis.program.json"}
        if d.config["item_number"]==6 else {"revised.ipynb","notebook.diff","patch-receipt.json","carried-conditions.json","execution.py"})
    assert (work/"review.json").read_bytes()==raw and (work/"console.log").read_bytes()==console
    # Idempotent verification creates no new scientific row or charge.
    before=d.store.db.execute("SELECT * FROM manual_calls").fetchall()
    assert approval.verify(d,value)==manifest
    assert d.store.db.execute("SELECT * FROM manual_calls").fetchall()==before


@pytest.mark.parametrize("file",["prompt.md","review.json","console.log",rs.RECORD,rs.CONFIG,rs.MODULE])
def test_changed_call_evidence_never_seals(reviewed,file):
    d,value,work=reviewed
    pr.write_bytes(work/file,(work/file).read_bytes()+b" ")
    with pytest.raises(ValueError):approval.record(d,value,value["pending"])
    assert "reviewed_execution" not in value


@pytest.mark.parametrize("damage",["source","plan","code","test","receipt","record_missing","not_complete","binding","inline","descriptor","measurement","workspace"])
def test_approval_is_not_transferable_to_other_code_or_delivery(reviewed,damage):
    d,value,work=reviewed
    notebook=d.config["item_number"]==4
    source_type="notebook_source" if notebook else "analysis_source"
    result=value["notebook_revision_result" if notebook else "program_result"]
    if damage=="source":d.config["source"]="f"*40
    elif damage=="plan":pr.write_text(d.context/"execution-plan.json","changed")
    elif damage in {"code","test","receipt"}:
        folder=Path(result["folder"])
        name={"code":"revised.ipynb" if notebook else "analysis.py",
              "test":"notebook.diff" if notebook else "test_analysis.py","receipt":"synthetic/receipt.json"}[damage]
        pr.write_text(folder/name,"changed")
    elif damage=="record_missing":(work/rs.RECORD).unlink()
    elif damage=="not_complete":d.store.db.execute("UPDATE manual_calls SET status='UNCERTAIN'")
    elif damage=="binding":value["pending"]["id"]="f"*64
    else:
        measured=json.loads((work/"input-measurement.json").read_bytes())
        if damage=="measurement":measured["selected_artifacts"]=[]
        elif damage=="descriptor":
            next(r for r in measured["workspace_files"] if r.get("type")==source_type)["source_path"]="another-source"
        elif damage=="workspace":
            ref=next(r for r in measured["workspace_files"] if r.get("type")==source_type)
            path=work/ref["path"];path.chmod(0o600);pr.write_text(path,"changed")
        else:
            ref=next(r for r in value["artifacts"] if r["type"]=="run_spec")
            pr.write_text(d.context/ref["path"],"changed")
        pr.atomic(work/"input-measurement.json",measured)
    with pytest.raises((ValueError,FileNotFoundError)):approval.record(d,value,value["pending"])
    assert "reviewed_execution" not in value


def test_post_approval_code_change_refuses_at_package_boundary(reviewed):
    d,value,_=reviewed
    approval.record(d,value,value["pending"])
    notebook=d.config["item_number"]==4
    result=value["notebook_revision_result" if notebook else "program_result"]
    pr.write_text(Path(result["folder"])/("revised.ipynb" if notebook else "analysis.py"),"changed")
    with pytest.raises(ValueError,match="EXPERIMENT_APPROVAL_EVIDENCE_CHANGED"):approval.verify(d,value)


@pytest.mark.parametrize("verdict",["REVISE","REJECT"])
def test_real_nonapproval_submission_cannot_authorize_execution(reviewed,verdict):
    d,value,work=reviewed
    with pytest.raises(ValueError,match="^EXPERIMENT_APPROVAL_REQUIRED$"):
        approval.record(d,value,value["pending"])
    assert "reviewed_execution" not in value
    assert json.loads((work/"review.json").read_bytes())["verdict"]==verdict


@pytest.mark.parametrize("wrong_tested_code",[True])
def test_passing_tests_on_other_code_do_not_qualify(reviewed,wrong_tested_code):
    d,value,_=reviewed
    with pytest.raises(ValueError,match="^EXPERIMENT_APPROVAL_TESTED_CODE_CHANGED$"):
        approval.record(d,value,value["pending"])
    assert "reviewed_execution" not in value
