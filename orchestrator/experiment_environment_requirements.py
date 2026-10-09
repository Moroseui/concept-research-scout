"""Declared item4 dependencies, not a native image or execution approval.

The author chooses requirements; the existing synthetic environment tests code.
These pure checks neither resolve an image nor construct a provider. The actual
runtime proof and its trusted selection remain separate execution prerequisites.
"""
import hashlib
import json
import re

PLAN_SCHEMA = "scientific-execution-plan/v2"
SCHEMA = "scientific-environment-requirements/v1"
PREPROCESSING_SCHEMA = "declared-preprocessing-partitions/v1"


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)+"\n").encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def validate(value):
    if (not isinstance(value, dict) or set(value) != {"schema", "python", "packages", "cuda"}
            or value["schema"] != SCHEMA
            or not isinstance(value["python"], str) or not re.fullmatch(r"3\.[0-9]{1,2}", value["python"])
            or not isinstance(value["cuda"], str) or not re.fullmatch(r"[0-9]{1,2}\.[0-9]{1,2}", value["cuda"])
            or not isinstance(value["packages"], dict) or not 1 <= len(value["packages"]) <= 300):
        raise ValueError("EXPERIMENT_ENVIRONMENT_REQUIREMENTS")
    for name, version in value["packages"].items():
        # Canonical distribution names prevent two spellings from selecting
        # conflicting requirements. Exact versions do not claim installation.
        if (not isinstance(name, str) or not re.fullmatch("[a-z0-9][a-z0-9-]{0,99}", name)
                or not isinstance(version, str) or not re.fullmatch(r"[0-9][A-Za-z0-9.+!_-]{0,79}", version)):
            raise ValueError("EXPERIMENT_ENVIRONMENT_REQUIREMENTS")
    # The already-existing item4 native gate requires this nnU-Net release and
    # torch. Keep that contract visible to the author rather than invent pins.
    if value["packages"].get("nnunetv2") != "2.8.1" or "torch" not in value["packages"]:
        raise ValueError("EXPERIMENT_ENVIRONMENT_REQUIREMENTS")
    return value


def preprocessing(value, plan, cohort_raw):
    # Reuse the existing immutable cohort/source selection. This is deliberately
    # separate from executable scope(): no placeholder native environment hash.
    from orchestrator.experiment_preprocessing import COHORT, SOURCE
    fields = {"schema", "id", "input_contract_sha256", "environment_requirements_sha256",
              "split_sha256", "plans_name", "cohort_sha256", "source_capture_sha256", "partitions_sha256"}
    requirements = validate(plan["environment_requirements"])
    if (not isinstance(value, dict) or set(value) != fields or value["schema"] != PREPROCESSING_SCHEMA
            or not isinstance(value["id"], str) or not re.fullmatch("[a-zA-Z0-9_-]{1,96}", value["id"])
            or value["cohort_sha256"] != COHORT or hashlib.sha256(cohort_raw).hexdigest() != COHORT
            or value["source_capture_sha256"] != SOURCE
            or value["environment_requirements_sha256"] != digest(requirements)
            or any(not isinstance(value[k], str) or not re.fullmatch("[a-f0-9]{64}", value[k])
                   for k in ("input_contract_sha256", "split_sha256", "partitions_sha256"))
            or not isinstance(value["plans_name"], str) or not re.fullmatch("[a-zA-Z0-9_-]{1,96}", value["plans_name"])):
        raise ValueError("EXPERIMENT_DECLARED_PREPROCESSING_SCOPE")
    if [row for row in plan["preprocessing"] if row.get("id") == value["id"]] != [value]:
        raise ValueError("EXPERIMENT_DECLARED_PREPROCESSING_BINDING")
    return value


def matches_native(requirements, actual):
    """Compare requirements with metadata; this does NOT qualify its provenance.

A caller must independently authenticate the pinned image and native proof.
Returning metadata from this pure function cannot authorize execution.
"""
    validate(requirements)
    if (not isinstance(actual, dict) or set(actual) != {"python", "packages", "cuda"}
            or not isinstance(actual["python"], str)
            or re.match(r"^"+re.escape(requirements["python"])+r"\.[0-9]+(?:\s|$)", actual["python"]) is None
            or actual["cuda"] != requirements["cuda"] or not isinstance(actual["packages"], dict)
            or any(actual["packages"].get(k) != v for k, v in requirements["packages"].items())):
        raise ValueError("EXPERIMENT_ENVIRONMENT_REQUIREMENTS_UNSATISFIED")
    return actual


def runtime_preprocessing(value, plan, cohort_raw, environment):
    """Resolve metadata without rewriting the declared scientific plan.

    This validates correspondence, not provider provenance or admission. The
    controller still authenticates the pinned image/native record; the worker
    still requires its binding-specific native environment proof before import.
    """
    from orchestrator.modal_scientific_environment import environment_validate, environment_bytes
    if plan.get("schema") != PLAN_SCHEMA:
        raise ValueError("EXPERIMENT_DECLARED_RUNTIME_PLAN")
    preprocessing(value, plan, cohort_raw)
    if not isinstance(environment, dict) or environment.get("schema") != "modal-pinned-image/v1":
        raise ValueError("EXPERIMENT_DECLARED_RUNTIME_IMAGE")
    environment_validate(environment)
    matches_native(plan["environment_requirements"], environment["expected"])
    resolved = {key:content for key,content in value.items()
                if key not in {"schema", "environment_requirements_sha256"}}
    resolved.update(schema="reviewed-preprocessing-partitions/v1",
        environment_sha256=hashlib.sha256(environment_bytes(environment["expected"])).hexdigest())
    return resolved
