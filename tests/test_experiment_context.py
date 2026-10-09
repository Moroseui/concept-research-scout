"""Actual driver input connection, synthetic context only, no scientific calls."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import experiment_context as ec, manual_context, diagnostics_policy as dp
from orchestrator import private_records, context_budget, scientific_intake
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import digest
from test_context_budget import root
from test_scientific_intake import registered, save_registry
from test_manual_context import artifact


@pytest.fixture
def experiment(root, monkeypatch):
    monkeypatch.setattr("orchestrator.cpu_isolation.verify_environment", lambda cfg: Path(cfg["environment_root"]))
    ref, registry = registered(root, monkeypatch)
    registry.update(task=dp.TASK, idea_ids=[dp.TASK])
    ref = save_registry(root, registry)
    state = root / "lane"
    private_records.mkdir(state)
    raw = json.dumps({"fixture":"synthetic execution interface; not a scientific design",
        "fits":[{"fit_id":"fit-one", "stage":"SMOKE", "arm":"synthetic-arm", "fold":0,
                 "realization":"one", "outputs":["synthetic-result.json","validation.json"], "validation_checks":["synthetic-check"]}]}).encode()
    private_records.write_bytes(root/"execution-plan.json", raw)
    scope = {"schema":"scientific-execution/v1", "item_number":6, "run_id":dp.RUN_ID,
             "authority_sha256":dp.AUTHORITY, "plan_sha256":digest(raw)}
    config = {"execution_scope":scope, "backend":"cpu", "item_number":6,
              "item_sha256":dp.ITEM_SHA256, "run_id":dp.RUN_ID, "diagnostics":dp.policy(),
              "synthetic_environment":{"environment_root":"/synthetic-tools", "environment_sha256":"a"*64},
              "revision_policy":copy.deepcopy(__import__("orchestrator.analysis_revisions",fromlist=["POLICY"]).POLICY),
              "review_contract":"bound-review/v1", "idea_ids":[dp.TASK], "private_intake":ref}
    plan = {k:config[k] for k in ("execution_scope", "private_intake", "idea_ids", "item_number", "item_sha256", "synthetic_environment", "revision_policy")}
    plan["execution_plan"] = {"path":"execution-plan.json", "sha256":digest(raw)}
    private_records.write_text(state/"preparation-plan.json", json.dumps(plan))
    config["plan_sha256"] = digest((state/"preparation-plan.json").read_bytes())
    d = SimpleNamespace(config=config, context=root, state=state,
        task=lambda stage,value:"Synthetic interface test only; not an experiment or model call.")
    rows = [artifact(root, kind, kind, text=json.dumps({"synthetic_fixture":kind,"not_execution_evidence":True}))
        for kind in ("run_spec", "execution_receipt", "execution_manifest", "package_manifest",
                     "validation_result", "result_tables", "analysis_source", "analysis_tests", "analysis_provenance")]
    return d, {"artifacts":rows}


def test_actual_driver_connection_all_four_roles_preserves_files_and_provenance(experiment):
    d, value = experiment
    for stage in manual_context.OUTPUTS:
        work = d.state/stage
        text, measured = Driver.prepare_input(d, value, stage, work)
        assert measured["execution_mode"] == dp.TASK
        assert measured["outputs"] == list(Driver.output_names(d, stage))
        assert len(text) == measured["characters"] < 200000
        assert "This is analysis of saved external evidence, not a new execution." not in text
        if stage.startswith("result_interpretation"):
            assert "newly executed approved experiment" in text
            assert "analysis.program.json with schema" not in text
        for row in measured["workspace_files"]:
            assert digest((work/row["path"]).read_bytes()) == row["sha256"]
        assert {"analysis_source","analysis_tests","analysis_provenance"} <= {
            row["type"] for row in measured["selected_artifacts"]}
        assert measured["private_scientific_views"]
        assert "synthetic execution interface; not a scientific design" in text
        assert sum(row["id"] == "frozen-execution-plan" for row in measured["selected_artifacts"]) == 1
    assert Driver.output_names(d,"run_spec_author") == ("SPEC.proposed.md","analysis.program.json")
    assert Driver.output_names(d,"run_spec_review") == ("review.json",)


@pytest.mark.parametrize("stage", ["result_interpretation_author", "result_interpretation_review"])
@pytest.mark.parametrize("missing", ["run_spec","execution_receipt","execution_manifest",
                                     "package_manifest","validation_result","result_tables"])
def test_interpretation_cannot_skip_execution_evidence(experiment, stage, missing):
    d, value = experiment
    value["artifacts"] = [row for row in value["artifacts"] if row["type"] != missing]
    with pytest.raises(context_budget.ContextError, match="EXECUTION_EVIDENCE_REQUIRED:"+missing):
        Driver.prepare_input(d, value, stage, d.state/stage)
    assert not (d.state/stage).exists()


@pytest.mark.parametrize("field,new", [("backend","modal"), ("run_id","unbound-run"),
    ("item_number",True), ("idea_ids",[]), ("idea_ids",["sprints-stocktake"]),
    ("review_contract","legacy")])
def test_wrong_selection_refuses_before_workspace(experiment,field,new):
    d,value=experiment;d.config[field]=new
    with pytest.raises(ValueError,match="EXPERIMENT_SELECTION_"):
        Driver.prepare_input(d,value,"run_spec_author",d.state/"refused")
    assert not (d.state/"refused").exists()


@pytest.mark.parametrize("path,error", [("execution-plan.json","EXPERIMENT_PLAN_CHANGED"),
    ("lane/preparation-plan.json","EXPERIMENT_PREPARATION_CHANGED"),
    ("view.txt","PRIVATE_INTAKE_VIEW_CHANGED")])
def test_changed_original_is_not_delivered(experiment,path,error):
    d,value=experiment;private_records.write_text(d.context/path,"altered")
    with pytest.raises(ValueError,match=error):
        Driver.prepare_input(d,value,"run_spec_author",d.state/"refused")
    assert not (d.state/"refused").exists()


def test_saved_analysis_route_retains_its_accurate_provenance(root,monkeypatch):
    ref,_=registered(root,monkeypatch)
    text,_=manual_context.build(root,stage="result_interpretation_author",
        idea_ids=["sprints-stocktake"],task="Synthetic saved evidence",artifacts=[],
        private_intake=ref,workspace=root/"old-route")
    assert "This is analysis of saved external evidence, not a new execution." in text


def test_unapproved_mode_or_program_output_refused(experiment):
    d,_=experiment
    for mode,program in [("unapproved",False),(None,True),("sprint13b-execution",True)]:
        with pytest.raises(context_budget.ContextError):
            manual_context.build(d.context,stage="run_spec_author",idea_ids=[dp.TASK],
                task="Synthetic",artifacts=[],private_intake=d.config["private_intake"],
                structured_review=True,workspace=d.state/"refused",execution_mode=mode,analysis_program=program)


def test_history_growth_does_not_change_experiment_inputs(experiment):
    d,value=experiment
    before={stage:Driver.prepare_input(d,value,stage,d.state/(stage+"-before"))[0]
            for stage in manual_context.OUTPUTS}
    with (d.context/"evidence/decisions.md").open("a") as stream:
        for i in range(1000):stream.write("\n## unrelated history\nidea_ids: [other-"+str(i)+"]\nNo authority.\n")
    assert before=={stage:Driver.prepare_input(d,value,stage,d.state/(stage+"-after"))[0]
                   for stage in manual_context.OUTPUTS}


def test_scoped_stop_and_closed_stop_apply_to_actual_experiment_caller(experiment):
    from test_context_budget import add_obligation, save_manifest
    d,value=experiment
    add_obligation(d.context,"stop")
    path=d.context/context_budget.PROJECT/"obligations.json"
    data=json.loads(path.read_bytes());record=data["obligations"][-1]
    record["scope"]["idea_ids"]=[dp.TASK];record["scope"]["stages"]=["run_spec_author"]
    path.write_text(json.dumps(data));save_manifest(d.context)
    with pytest.raises(context_budget.ContextError,match="SCOPED_STOP"):
        Driver.prepare_input(d,value,"run_spec_author",d.state/"blocked-stage")
    Driver.prepare_input(d,value,"run_spec_review",d.state/"other-stage")
    resolution=d.context/"resolution.txt";raw=b"Synthetic operator closes this fixture stop."
    resolution.write_bytes(raw)
    record.update(status="closed",disposition={"path":resolution.name,"sha256":digest(raw),
        "start":0,"end":len(raw),"text":raw.decode()})
    path.write_text(json.dumps(data));save_manifest(d.context)
    Driver.prepare_input(d,value,"run_spec_author",d.state/"closed-stop")


def test_execution_plan_cannot_be_shadowed_by_later_artifact(experiment):
    d,value=experiment
    value["artifacts"].append(artifact(d.context,"configuration","frozen-execution-plan",2,"Changed contract"))
    with pytest.raises(ValueError,match="EXPERIMENT_DELIVERY_PLAN_CONFLICT"):
        Driver.prepare_input(d,value,"run_spec_author",d.state/"shadowed")


@pytest.mark.parametrize("phase", ["EXECUTE_EXPERIMENT","EMIT_PACKAGE","EXECUTE_CPU","WAIT_OUTPUTS","UPDATE_STATE"])
def test_unfinished_executor_cannot_fall_through_to_old_sprint10(experiment,phase):
    d,value=experiment;d.current=lambda:{"phase":phase};d.guard=lambda:None # Outer guard fixture only.
    code={"EXECUTE_EXPERIMENT":"DIAGNOSTICS_REVIEWED_PACKAGE_REQUIRED","UPDATE_STATE":"EXPERIMENT_REVIEWED_RESULTS_REQUIRED"}.get(phase,"EXPERIMENT_EXECUTOR_CONNECTION_REQUIRED")
    with pytest.raises(ValueError,match="^"+code+"$"):
        Driver._advance(d)
