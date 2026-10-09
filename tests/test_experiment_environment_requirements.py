"""Declared requirements are draft science, never fabricated native evidence.

All data are synthetic. The shared fixture labels the simulated native review
and CPU test receipt; delivery, plan validation, sealing and packaging are real.
"""
import copy
import json
import sys
import pytest
from orchestrator import experiment_environment_requirements as req
from orchestrator import experiment_plan_output as authored, experiment_partition_input as partitions
from orchestrator import experiment_context as ec, review_submission as rs
from orchestrator import experiment_approval as approval, experiment_package as package
from orchestrator import experiment_modal_package as bridge, experiment_preprocessing as preprocessing
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import digest
from test_experiment_approval import reviewed
from test_experiment_context import experiment, root
from test_experiment_plan_output import synthetic_plan, validation_args
from partition_fixture import RAW, FILES


def requirements():
    return {"schema":req.SCHEMA, "python":"3.12", "packages":{"nnunetv2":"2.8.1", "torch":"2.5.1"}, "cuda":"12.4"}


def declared_plan(original):
    plan=copy.deepcopy(original)
    plan.update(schema=req.PLAN_SCHEMA,environment_requirements=requirements())
    for row in plan["preprocessing"]:
        row.pop("environment_sha256")
        row.update(schema=req.PREPROCESSING_SCHEMA,environment_requirements_sha256=req.digest(requirements()))
    return plan


def test_strict_requirement_shape_and_metadata_match_do_not_claim_proof():
    selected=requirements()
    assert req.validate(selected)==selected
    actual={"python":"3.12.7 (synthetic metadata only)","packages":{**selected["packages"],"numpy":"2.0.0"},"cuda":"12.4"}
    assert req.matches_native(selected,actual)==actual
    for field,value in [("python","3.13.1"),("python","3.120.1"),("cuda",None),("cuda","12.5"),("packages",{"nnunetv2":"2.8.1","torch":"2.6.0"})]:
        bad=copy.deepcopy(actual);bad[field]=value
        with pytest.raises(ValueError,match="^EXPERIMENT_ENVIRONMENT_REQUIREMENTS_UNSATISFIED$"):
            req.matches_native(selected,bad)


@pytest.mark.parametrize("change",[
    lambda x:x.update(extra=True),lambda x:x.update(python="unknown"),lambda x:x.update(cuda=None),
    lambda x:x.update(packages={}),lambda x:x["packages"].update(torch=">=2"),
    lambda x:x["packages"].update(nnunetv2="2.8.2"),lambda x:x["packages"].update({"Torch":"2.5.1"}),
    lambda x:x["packages"].update({"some_package":"1.0"})])
def test_unpinned_ambiguous_or_unknown_requirement_fields_refuse(change):
    value=requirements();change(value)
    with pytest.raises(ValueError,match="^EXPERIMENT_ENVIRONMENT_REQUIREMENTS$"):req.validate(value)


@pytest.mark.parametrize("reviewed",["requirements4"],indirect=True)
def test_actual_draft_delivery_seal_and_package_keep_original_bytes(reviewed):
    d,value,work=reviewed
    row=authored.ref(d,value);original=(d.context/row["path"]).read_bytes();plan=json.loads(original)
    measurement=json.loads((work/"input-measurement.json").read_bytes())
    assert measurement["selected_artifacts"].count(row)==1
    shown=next(x for x in measurement["workspace_files"] if x.get("id")==row["id"])
    assert (work/shown["path"]).read_bytes()==original
    from orchestrator.context_budget import encoded
    assert encoded(shown) in (work/"prompt.md").read_text()
    assert "environment_sha256" not in plan["preprocessing"][0]
    assert plan["preprocessing"][0]["environment_requirements_sha256"]==req.digest(plan["environment_requirements"])
    before=d.store.db.execute("SELECT * FROM manual_calls").fetchall()
    Driver._accept_completed(d,value)
    sealed=approval.verify(d,value)
    assert sealed["execution_admitted"] is False
    assert sealed["authored_execution_plan"]==row
    package.emit(d,value)
    assert (d.state/"experiment-package/execution-plan.json").read_bytes()==original
    assert (d.state/"experiment-package"/partitions.FILE).read_bytes()==RAW
    assert d.store.db.execute("SELECT * FROM manual_calls").fetchall()==before
    assert package.verify(d,value,d.state/"experiment-package")["reviewed_execution_sha256"]


@pytest.mark.parametrize("reviewed",["requirements4"],indirect=True)
def test_declared_plan_cannot_construct_paid_package_or_run_worker(reviewed):
    d,value,_=reviewed
    Driver._accept_completed(d,value);package.emit(d,value)
    original=(d.state/"experiment-package/execution-plan.json").read_bytes();plan=json.loads(original)
    selected=plan["preprocessing"][0];cohort=(d.context/"cohort.json").read_bytes()
    binding={"preprocessing":selected,"resources":{"gpu":None},"experiment":{"stage":"SMOKE"}}
    with pytest.raises(ValueError,match="^EXPERIMENT_PREPROCESSING_SCOPE$"):
        preprocessing.scope(binding,plan,cohort)
    # The existing bridge also rejects the unselected declared schema before
    # writes/provider construction: it cannot claim an executable manifest.
    # No native environment proof or hash is invented here.
    from orchestrator.modal_item4_policy import AUTHORITY,TEAM_AUTHORITY
    binding.update(purpose="M4_ITEM4",source=d.config["source"],run_id=d.config["run_id"])
    binding["experiment"].update(backlog_item=4,authority_sha256=AUTHORITY,team_authority_sha256=TEAM_AUTHORITY)
    with pytest.raises(ValueError,match="^EXPERIMENT_MANIFEST_FILE_BINDING$"):
        bridge.emit(d,value,d.state/"unadmitted-modal-package",binding,preprocessing_inputs={
            "cohort.json":cohort,"input-inventory.json":rs.canonical(FILES)})
    assert not (d.state/"unadmitted-modal-package").exists()
    assert (d.state/"experiment-package/execution-plan.json").read_bytes()==original
    assert "modal" not in sys.modules


@pytest.mark.parametrize("reviewed",["requirements4"],indirect=True)
@pytest.mark.parametrize("damage,code",[
    ("requirements-hash","EXPERIMENT_DECLARED_PREPROCESSING_SCOPE"),
    ("cohort","EXPERIMENT_DECLARED_PREPROCESSING_SCOPE"),
    ("source","EXPERIMENT_DECLARED_PREPROCESSING_SCOPE"),
    ("split","EXPERIMENT_DECLARED_PREPROCESSING_SCOPE"),
    ("partition","EXPERIMENT_PARTITIONS_PLAN_BINDING"),
    ("schema","EXPERIMENT_PARTITIONS_PLAN_BINDING"),
    ("fake-environment","EXPERIMENT_DECLARED_PREPROCESSING_SCOPE"),
    ("legacy-fields","EXPERIMENT_AUTHORED_PLAN_BINDING")])
def test_draft_does_not_relax_original_bindings_or_accept_placeholder_native_identity(reviewed,damage,code):
    d,value,_=reviewed;ref=authored.ref(d,value)
    plan=json.loads((d.context/ref["path"]).read_bytes());row=plan["preprocessing"][0]
    if damage=="requirements-hash":row["environment_requirements_sha256"]="f"*64
    elif damage=="cohort":row["cohort_sha256"]="f"*64
    elif damage=="source":row["source_capture_sha256"]="f"*64
    elif damage=="split":row["split_sha256"]="pending"
    elif damage=="partition":row["partitions_sha256"]="f"*64
    elif damage=="schema":row["schema"]=partitions.SCHEMA
    elif damage=="fake-environment":row["environment_sha256"]="f"*64
    else:plan["schema"]="scientific-execution-plan/v1"
    cohort,cases=authored.cohort(d)
    with pytest.raises(ValueError,match="^"+code+"$"):
        authored.validate(rs.canonical(plan),ec.selection(d),cases,cohort,partitions_sha256=digest(RAW))


def test_new_schema_requires_original_partition_and_complete_preprocessing(experiment):
    d,_,cohort,cases=validation_args(experiment)
    plan=declared_plan(synthetic_plan(ec.selection(d)))
    with pytest.raises(ValueError,match="^EXPERIMENT_DECLARED_PARTITIONS_REQUIRED$"):
        authored.validate(rs.canonical(plan),ec.selection(d),cases,cohort)
    instructions=authored.instructions(ec.selection(d))
    assert req.PLAN_SCHEMA in instructions and req.SCHEMA in instructions
    assert "not an observed image" in instructions and "never rewrite the approved plan" in instructions
