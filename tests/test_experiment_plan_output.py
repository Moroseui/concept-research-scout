"""Synthetic author plan -> exact review delivery/seal -> provider package.

Native judgments and notebook sandbox receipts are explicitly labelled fixtures
from test_experiment_approval; all binding consumers here are real.
"""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import experiment_plan_output as authored, experiment_context as ec
from orchestrator import private_records as pr, review_submission as rs, manual_context as mc
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import digest
from test_experiment_context import experiment, root
from test_experiment_approval import reviewed


def synthetic_plan(selected):
    from test_experiment_projection import example
    plan,_=example()
    for fit in plan["fits"]:
        fit.update(realization="synthetic",validation_checks=["synthetic-check"])
        fit.setdefault("outputs",["timing.json","validation.json"])
    plan.update(schema="scientific-execution-plan/v1",run_id=selected["run_id"],
        operator_scope_sha256=selected["plan_sha256"],dispatch_mode="incremental",preprocessing=[])
    return plan


def configure_authored(d):
    d.config["authored_execution_plan"]=authored.MODE
    prep=json.loads((d.state/"preparation-plan.json").read_bytes())
    prep["authored_execution_plan"]=authored.MODE
    pr.write_text(d.state/"preparation-plan.json",json.dumps(prep))
    d.config["plan_sha256"]=digest((d.state/"preparation-plan.json").read_bytes())


def validation_args(experiment):
    from test_experiment_revisions import as_item4
    d,value=experiment;as_item4(d);configure_authored(d)
    raw,cases=authored.cohort(d)
    return d,value,raw,cases


def test_new_output_requires_explicit_item4_mode_and_legacy_unchanged(experiment):
    d,value,_,_=validation_args(experiment)
    assert ec.outputs(d,"run_spec_author")==("SPEC.proposed.md","notebook.patch.json","execution.plan.json")
    assert ec.outputs(d,"run_spec_review")==("review.json",)
    assert authored.enabled({"item_number":4}) is False
    for config in ({"item_number":6,"authored_execution_plan":authored.MODE},
                   {"item_number":4,"authored_execution_plan":"unknown"}):
        with pytest.raises(ValueError,match="^EXPERIMENT_AUTHORED_PLAN_MODE$"):authored.enabled(config)
    prep=json.loads((d.state/"preparation-plan.json").read_bytes());prep.pop("authored_execution_plan")
    with pytest.raises(ValueError,match="^EXPERIMENT_AUTHORED_PLAN_MODE_CHANGED$"):
        ec.validate_selection(d.config,prep,d.context)


def test_plan_shape_and_downstream_consumers_are_shared(experiment):
    d,value,raw,cases=validation_args(experiment);selected=ec.selection(d)
    plan=synthetic_plan(selected)
    assert authored.validate(rs.canonical(plan),selected,cases,raw)==plan
    for change,code in [
        (lambda p:p.update(run_id="another"),"EXPERIMENT_AUTHORED_PLAN_BINDING"),
        (lambda p:p.update(operator_scope_sha256="f"*64),"EXPERIMENT_AUTHORED_PLAN_BINDING"),
        (lambda p:p["fits"][0].update(fold=True),"EXPERIMENT_FROZEN_FIT_FIELDS"),
        (lambda p:p["fits"][0].update(validation_checks=[]),"EXPERIMENT_RESULT_CHECK_SELECTION"),
        (lambda p:p["fits"][0].update(outputs=["../result.json","validation.json"]),"EXPERIMENT_RESULT_AGGREGATE_PATH"),
        (lambda p:p["full_training"].update(full_fits=[]),"EXPERIMENT_PROJECTION_")]:
        bad=copy.deepcopy(plan);change(bad)
        with pytest.raises(ValueError,match=code):authored.validate(rs.canonical(bad),selected,cases,raw)
    with pytest.raises(ValueError):authored.validate(b'{"schema":1,"schema":2}',selected,cases,raw)
    with pytest.raises(ValueError,match="^EXPERIMENT_AUTHORED_PLAN_LIMIT$"):
        authored.validate(b" "*(authored.LIMIT+1),selected,cases,raw)


@pytest.mark.parametrize("payload",["sub-"+"stroke9999", "sk-"+"syntheticsecretfixture000000000000000000000000000000"])
def test_privacy_scans_run_before_preservation(experiment,payload):
    d,value,_,_=validation_args(experiment);plan=synthetic_plan(ec.selection(d))
    plan["full_training"]["full_fits"][0]["assumption"]=payload
    before=list(value["artifacts"])
    with pytest.raises(ValueError):authored.preserve(d,value,{"round":1},rs.canonical(plan))
    assert value["artifacts"]==before
    assert not (d.context/"current/runs"/digest(d.config["run_id"].encode())/"execution-plan-1.json").exists()


def test_revision_preserves_old_plan_and_delivers_only_latest(experiment):
    d,value,_,_=validation_args(experiment);plan=synthetic_plan(ec.selection(d))
    first=rs.canonical(plan);a=authored.preserve(d,value,{"round":1},first)
    plan["full_training"]["full_fits"][0]["assumption"]="Synthetic revised applicability statement."
    second=rs.canonical(plan);b=authored.preserve(d,value,{"round":2},second)
    assert a!=b and (d.context/a["path"]).read_bytes()==first
    assert authored.ref(d,value)==b
    assert [r for r in mc.selected_artifacts("run_spec_review",value["artifacts"]) if r["id"]==authored.ARTIFACT]==[b]
    with pytest.raises(ValueError):authored.preserve(d,value,{"round":1},second)
    assert (d.context/a["path"]).read_bytes()==first


@pytest.mark.parametrize("reviewed",["authored4"],indirect=True)
def test_exact_author_plan_reaches_review_seal_package_bridge_and_owner(reviewed):
    from orchestrator import experiment_approval as approval, experiment_package as package
    from orchestrator import experiment_modal_package as bridge, experiment_owner
    from test_experiment_modal_package import emit
    d,value,work=reviewed
    constraints=copy.deepcopy(ec.selection(d));ref=authored.ref(d,value)
    original=(d.context/ref["path"]).read_bytes()
    measured=json.loads((work/"input-measurement.json").read_bytes())
    assert measured["selected_artifacts"].count(ref)==1
    shown=next(x for x in measured['workspace_files'] if x.get('id')==ref['id'])
    assert (work/shown['path']).read_bytes()==original
    assert __import__('orchestrator.context_budget',fromlist=['encoded']).encoded(shown) in (work/'prompt.md').read_text()
    manifest,_=emit(d,value)
    assert approval.verify(d,value)["authored_execution_plan"]==ref
    assert package.verify(d,value,d.state/"experiment-package")["selection"]==constraints
    assert (d.state/"experiment-package/execution-plan.json").read_bytes()==original
    assert manifest["binding"]["execution_plan_sha256"]==digest(original)!=constraints["plan_sha256"]
    # Real owner consumer opens the same synthetic lane ledger read-only.
    owner={"state":str(d.state),"source":d.config["source"],"run_id":d.config["run_id"],
        "plan_sha256":d.config["plan_sha256"],"review_sha256":"c"*64,"execution_scope":constraints}
    d.config.update(owner_binding=owner,engine_review={"sha256":"c"*64})
    pr.atomic(d.state/"lane.json",d.config)
    d.store.db.execute("INSERT INTO manual_state VALUES(1,?)",(json.dumps(value),))
    before=d.store.db.execute("SELECT * FROM manual_calls").fetchall()
    batch=SimpleNamespace(filesystem_root=Path("/"))
    experiment_owner.verify_item4(batch,d.config["run_id"],owner,manifest["binding"])
    assert d.store.db.execute("SELECT * FROM manual_calls").fetchall()==before
    assert len(before)==1 and ec.selection(d)==constraints
    wrong=copy.deepcopy(manifest["binding"]);wrong["execution_plan_sha256"]=constraints["plan_sha256"]
    with pytest.raises(ValueError,match="^ITEM4_EXECUTION_OWNER_BINDING$"):
        experiment_owner.verify_item4(batch,d.config["run_id"],owner,wrong)
    # Different scientific plan is not accepted by rebinding a mutable artifact.
    pr.write_bytes(d.context/ref["path"],original+b" ")
    with pytest.raises(ValueError,match="^EXPERIMENT_AUTHORED_PLAN_CHANGED$"):approval.verify(d,value)


@pytest.mark.parametrize("reviewed",["authored4"],indirect=True)
def test_missing_actual_plan_delivery_cannot_be_sealed(reviewed):
    from orchestrator import experiment_approval as approval
    d,value,work=reviewed
    measured=json.loads((work/"input-measurement.json").read_bytes())
    measured["selected_artifacts"]=[r for r in measured["selected_artifacts"] if r["id"]!=authored.ARTIFACT]
    pr.atomic(work/"input-measurement.json",measured)
    with pytest.raises(ValueError,match="^EXPERIMENT_APPROVAL_NOT_DELIVERED:configuration$"):
        approval.record(d,value,value["pending"])


def test_author_accepts_exact_output_and_spec_separate_bindings(experiment,monkeypatch):
    d,value,_,_=validation_args(experiment)
    d.artifact=lambda *args:Driver.artifact(d,*args)
    work=d.state/"authored-call";pr.mkdir(work)
    raw=rs.canonical(synthetic_plan(ec.selection(d)))
    pr.write_bytes(work/authored.OUTPUT,raw)
    spec=("run_id: "+d.config["run_id"]+"\noperator_scope_sha256: "+
          d.config["execution_scope"]["plan_sha256"]+"\nexecution_plan_sha256: "+digest(raw)+"\n")
    pr.write_text(work/"SPEC.proposed.md",spec)
    calls=[]
    # Only the independent notebook test boundary is replaced. Selection,
    # registry/scans, output bytes, SPEC pins and artifact writes are actual.
    monkeypatch.setattr("orchestrator.notebook_revision.prepare_artifacts",lambda *args:calls.append(args))
    ec.accept_author(d,value,{"round":1,"workspace":str(work)})
    assert len(calls)==1 and value["phase"]=="run_spec_review"
    assert authored.ref(d,value)["sha256"]==digest(raw)
    before=list(value["artifacts"])
    pr.write_text(work/"SPEC.proposed.md",spec.replace(digest(raw),d.config["execution_scope"]["plan_sha256"]))
    with pytest.raises(ValueError,match="^EXPERIMENT_SPEC_BINDING$"):
        ec.accept_author(d,value,{"round":2,"workspace":str(work)})
    assert value["artifacts"]==before and len(calls)==1


def test_actual_assembly_declares_new_author_output_and_reviewer_plan(experiment,monkeypatch):
    from test_scientific_intake import save_registry
    d,value,_,_=validation_args(experiment)
    registry=json.loads((d.context/d.config["private_intake"]["path"]).read_bytes())
    registry.update(task=ec.TASKS[4],idea_ids=[ec.TASKS[4]])
    d.config["private_intake"]=save_registry(d.context,registry)
    d.config["notebook_revision"].update(safe_view={"sha256":"a"*64},environment={"environment_root":"/synthetic-tools","environment_sha256":"b"*64})
    prep=json.loads((d.state/"preparation-plan.json").read_bytes())
    for key in ("private_intake","notebook_revision"):prep[key]=d.config[key]
    pr.write_text(d.state/"preparation-plan.json",json.dumps(prep))
    d.config["plan_sha256"]=digest((d.state/"preparation-plan.json").read_bytes())
    monkeypatch.setattr("orchestrator.notebook_revision.validate_config",lambda *args:None) # Config-only fixture.
    text,measured=Driver.prepare_input(d,value,"run_spec_author",d.state/"plan-author")
    assert measured["outputs"]==list(ec.outputs(d,"run_spec_author"))
    instructions=next(x for x in measured['workspace_files'] if x['id']=='scientific-author-instructions')
    raw=(d.state/'plan-author'/instructions['path']).read_bytes();assert digest(raw)==instructions['sha256']
    task=raw.decode()
    assert authored.OUTPUT in task and 'operator_scope_sha256' in task and 'at most 80000 bytes' in task
    plan=rs.canonical(synthetic_plan(ec.selection(d)))
    ref=authored.preserve(d,value,{"round":1},plan)
    text,measured=Driver.prepare_input(d,value,"run_spec_review",d.state/"plan-review")
    assert measured["outputs"]==["review.json"]
    assert measured["selected_artifacts"].count(ref)==1
    shown=next(x for x in measured['workspace_files'] if x.get('id')==ref['id'])
    assert (d.state/'plan-review'/shown['path']).read_bytes()==plan
    assert __import__('orchestrator.context_budget',fromlist=['encoded']).encoded(shown) in text
    assert "current authored execution plan SHA256: "+digest(plan) in text
    assert "Original operator constraint SHA256: "+ec.selection(d)["plan_sha256"] in text
