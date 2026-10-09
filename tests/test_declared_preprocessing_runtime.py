"""Synthetic no-patient integration; native proof fixture is not provider evidence."""
import copy
import json
import pytest
from orchestrator import experiment_environment_requirements as req
from orchestrator import experiment_preprocessing as prep, experiment_worker as worker
from orchestrator import private_records as pr
from orchestrator.manual_executor import digest, inventory
from orchestrator.modal_executor import canonical
from orchestrator.modal_scientific_environment import environment_bytes
from test_experiment_preprocessing import prepared


def pinned_environment():
    actual = {"python":"3.12.7 (synthetic fixture)", "cuda":"12.8",
        "packages":{"nnunetv2":"2.8.1", "torch":"2.11.0+cu128",
                    **{"synthetic-dependency-"+str(i):"1.0" for i in range(11)}}}
    return {"schema":"modal-pinned-image/v1", "python_executable":"/opt/research-scientific-python/bin/python",
        "image_id":"im-synthetic", "base_image":"pytorch/pytorch@sha256:"+"a"*64,
        "builder_sha256":"b"*64, "selection_sha256":"c"*64, "native_sha256":"d"*64,
        "expected":actual}


@pytest.fixture
def declared(prepared):
    root, package, inputs, progress, seal = prepared
    binding, _ = seal()
    environment = pinned_environment()
    requirements = {"schema":req.SCHEMA, "python":"3.12", "cuda":"12.8",
                    "packages":{"nnunetv2":"2.8.1", "torch":"2.11.0+cu128"}}
    row = copy.deepcopy(binding["preprocessing"])
    row.pop("environment_sha256")
    partition = b'{"synthetic_partition_fixture":true}'
    row.update(schema=req.PREPROCESSING_SCHEMA,
        environment_requirements_sha256=req.digest(requirements), partitions_sha256=digest(partition))
    plan = {"schema":req.PLAN_SCHEMA, "environment_requirements":requirements, "preprocessing":[row]}
    cohort = (package/"cohort.json").read_bytes()
    binding["preprocessing"] = req.runtime_preprocessing(row, plan, cohort, environment)
    binding["scientific_environment"] = environment
    pr.write_bytes(package/"execution-plan.json", canonical(plan))
    pr.write_bytes(package/"frozen-partitions.json", partition)
    binding["execution_plan_sha256"] = digest(canonical(plan))
    files = {k:v for k,v in inventory(package).items() if k != "manifest.json"}
    pr.write_bytes(package/"manifest.json", canonical({"schema":"modal-run/v1", "binding":binding,"files":files}))
    ident = digest(canonical(binding))
    proof = {"schema":"scientific-environment-proof/v1", "binding_sha256":ident,
        "expected_sha256":digest(environment_bytes(environment["expected"])),
        "actual":environment["expected"], "offline":True,
        "image_id":environment["image_id"], "native_sha256":environment["native_sha256"]}
    pr.write_bytes(progress/"environment-verification"/ident/"environment.json",environment_bytes(proof))
    return package, inputs, progress, binding, ident, plan, cohort


def test_declared_plan_runs_real_worker_with_separate_native_row_and_keeps_original(declared):
    package, inputs, progress, binding, ident, plan, cohort = declared
    before = (package/"execution-plan.json").read_bytes()
    assert prep.scope(binding, plan, cohort) == binding["preprocessing"]
    result = worker.execute(package, inputs, progress, ident)
    assert result["status"] == "VALIDATED" and result["files"] == 300
    assert result["scientifically_accepted"] is False
    assert (package/"execution-plan.json").read_bytes() == before
    assert "environment_sha256" not in plan["preprocessing"][0]
    assert "environment_requirements_sha256" not in binding["preprocessing"]


@pytest.mark.parametrize("damage",["torch", "cuda", "python", "requirements-pin", "native-pin",
    "image-kind", "cohort", "source", "split", "partition", "duplicate", "gpu", "stage"])
def test_changed_runtime_or_plan_refuses_before_import(declared, damage):
    package, inputs, progress, binding, ident, plan, cohort = declared
    original = copy.deepcopy(plan)
    if damage in {"torch","cuda","python"}:
        actual = binding["scientific_environment"]["expected"]
        if damage == "torch": actual["packages"]["torch"] = "2.11.0"
        else: actual[damage] = {"cuda":"12.4", "python":"3.13.0"}[damage]
    elif damage == "requirements-pin": plan["preprocessing"][0]["environment_requirements_sha256"] = "f"*64
    elif damage == "native-pin": binding["preprocessing"]["environment_sha256"] = "f"*64
    elif damage == "image-kind": binding["scientific_environment"]["schema"] = "offline-scientific-python/v1"
    elif damage in {"cohort","source","split","partition"}:
        key = {"cohort":"cohort_sha256","source":"source_capture_sha256","split":"split_sha256","partition":"partitions_sha256"}[damage]
        binding["preprocessing"][key] = "f"*64
    elif damage == "duplicate": plan["preprocessing"] *= 2
    elif damage == "gpu": binding["resources"]["gpu"] = "H100"
    else: binding["experiment"]["stage"] = "FULL"
    with pytest.raises(ValueError): prep.scope(binding, plan, cohort)
    assert not (progress/"preprocessing").exists()
    if damage not in {"requirements-pin","duplicate"}: assert plan == original


@pytest.mark.parametrize("damage",["missing", "offline", "binding", "image", "native"])
def test_mapping_never_replaces_binding_specific_native_proof(declared, damage):
    package, inputs, progress, binding, ident, plan, cohort = declared
    path = progress/"environment-verification"/ident/"environment.json"
    if damage == "missing": path.unlink()  # Synthetic test fixture only.
    else:
        proof = json.loads(path.read_bytes())
        field = {"offline":"offline","binding":"binding_sha256","image":"image_id","native":"native_sha256"}[damage]
        proof[field] = False if damage == "offline" else "unbound"
        pr.write_bytes(path, canonical(proof))
    with pytest.raises((ValueError, FileNotFoundError)): worker.execute(package,inputs,progress,ident)
    assert not (progress/"preprocessing").exists()
