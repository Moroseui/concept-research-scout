"""Author-owned item4 plan output, separate from immutable operator selection.

Only the explicitly selected new preparation mode uses this connection. No
fit, scientific parameter, runtime selection or execution approval is invented.
"""
import re
from pathlib import Path
from orchestrator import context_budget as cb, manual_context as mc, private_records as pr
from orchestrator.manual_executor import digest
from orchestrator.review_contract import strict_json

MODE = "author-output/v1"
OUTPUT = "execution.plan.json"
ARTIFACT = "authored-execution-plan"
LIMIT = 80000


def enabled(config):
    mode = config.get("authored_execution_plan")
    if mode is not None and (mode != MODE or config.get("item_number") != 4):
        raise ValueError("EXPERIMENT_AUTHORED_PLAN_MODE")
    return mode == MODE


def cohort(driver):
    from orchestrator import scientific_intake as intake
    ref = driver.config["private_intake"]
    raw = cb.relative_file(driver.context, ref["path"]).read_bytes()
    if digest(raw) != ref["sha256"]: raise ValueError("EXPERIMENT_REGISTRY_CHANGED")
    registry = strict_json(raw)
    original = cb.relative_file(driver.context, registry["cohort"]).read_bytes()
    return original, intake.cohort(original)


def validate(raw, selected, cases, cohort_raw, *, partitions_sha256=None):
    """Check delivery/schema using the same fit/result/projection consumers."""
    from orchestrator import scientific_intake, experiment_result
    from orchestrator.experiment_preprocessing import scope
    from orchestrator import experiment_environment_requirements as requirements
    if not isinstance(raw, bytes) or len(raw) > LIMIT:
        raise ValueError("EXPERIMENT_AUTHORED_PLAN_LIMIT")
    scientific_intake.scan(raw, cases, kind="plan")
    from orchestrator.git_publication import scan
    scan("context/execution.plan.json", raw)
    plan = strict_json(raw)
    fields = {"schema", "run_id", "operator_scope_sha256", "dispatch_mode", "fits", "preprocessing", "full_training"}
    declared = isinstance(plan, dict) and plan.get("schema") == requirements.PLAN_SCHEMA
    if declared: fields.add("environment_requirements")
    if (not isinstance(plan, dict) or set(plan) != fields
            or plan["schema"] not in {"scientific-execution-plan/v1", requirements.PLAN_SCHEMA}
            or plan["run_id"] != selected["run_id"]
            or plan["operator_scope_sha256"] != selected["plan_sha256"]
            or plan["dispatch_mode"] != "incremental"
            or not isinstance(plan["fits"], list) or not plan["fits"]
            or not isinstance(plan["preprocessing"], list)):
        raise ValueError("EXPERIMENT_AUTHORED_PLAN_BINDING")
    if declared:
        requirements.validate(plan["environment_requirements"])
        if partitions_sha256 is None or not plan["preprocessing"]:
            raise ValueError("EXPERIMENT_DECLARED_PARTITIONS_REQUIRED")
    from orchestrator.experiment_plan_validation import validate_fits, contract
    validate_fits(plan, incremental=True)
    fit_ids = [f["fit_id"] for f in plan["fits"]]
    ids = [p.get("id") for p in plan["preprocessing"] if isinstance(p, dict)]
    if (len(ids) != len(plan["preprocessing"]) or len(set(ids)) != len(ids)
            or len(set(fit_ids)) != len(fit_ids)
            or any(not isinstance(x, str) or not re.fullmatch("[a-zA-Z0-9_-]{1,96}", x) for x in fit_ids)
            or (ids and set(ids) != {f.get("preprocessing_id") for f in plan["fits"]})):
        raise ValueError("EXPERIMENT_AUTHORED_PLAN_IDENTITIES")
    from orchestrator.experiment_partition_input import require_plan
    require_plan(plan, partitions_sha256)
    for row in plan["preprocessing"]:
        if declared:
            requirements.preprocessing(row, plan, cohort_raw)
        else:
            scope({"preprocessing": row, "resources": {"gpu": None}, "experiment": {"stage": "SMOKE"}}, plan, cohort_raw)
    for fit in plan["fits"]:
        experiment_result.selected(plan, {"experiment": {"fit_id": fit["fit_id"]}, "outputs": fit["outputs"]})
    contract(plan)
    return plan


def ref(driver, value):
    rows = [r for r in mc.selected_artifacts("run_spec_review", value["artifacts"])
            if r["id"] == ARTIFACT and r["type"] == "configuration"]
    if len(rows) != 1: raise ValueError("EXPERIMENT_AUTHORED_PLAN_REQUIRED")
    row = rows[0]
    raw = pr.check(cb.relative_file(driver.context, row["path"])).read_bytes()
    if digest(raw) != row["sha256"]: raise ValueError("EXPERIMENT_AUTHORED_PLAN_CHANGED")
    from orchestrator.experiment_context import selection
    original, cases = cohort(driver)
    from orchestrator.experiment_partition_input import plan_pin
    validate(raw, selection(driver), cases, original, partitions_sha256=plan_pin(driver.config, driver.context))
    return row


def preserve(driver, value, pending, raw):
    from orchestrator.manual_driver import write_once
    from orchestrator.experiment_context import selection
    original, cases = cohort(driver)
    from orchestrator.experiment_partition_input import plan_pin
    validate(raw, selection(driver), cases, original, partitions_sha256=plan_pin(driver.config, driver.context))
    relative = "current/runs/" + digest(driver.config["run_id"].encode()) + "/execution-plan-" + str(pending["round"]) + ".json"
    write_once(driver.context/relative, raw)
    row = {"id": ARTIFACT, "type": "configuration", "version": pending["round"],
           "path": relative, "sha256": digest(raw)}
    # Keep each prior version; selected_artifacts delivers only the newest.
    if row not in value["artifacts"]: value["artifacts"].append(row)
    if ref(driver, value) != row: raise ValueError("EXPERIMENT_AUTHORED_PLAN_VERSION")
    return row


def instructions(selected):
    from orchestrator.experiment_plan_validation import author_schema
    import json
    return ("Exact projection output schema: " + json.dumps(author_schema(), sort_keys=True) + "\n" + "Write execution.plan.json as strict JSON (at most 80000 bytes; no duplicate keys). "
        "This is your scientific plan; the separately supplied original execution selection is operator constraints, "
        "not an invented or already approved fit plan. Use exactly schema, run_id, operator_scope_sha256, "
        "dispatch_mode, fits, preprocessing, full_training and environment_requirements. "
        "schema is scientific-execution-plan/v2; "
        "run_id is " + selected["run_id"] + "; operator_scope_sha256 is " + selected["plan_sha256"] + ". "
        "dispatch_mode is incremental. Choose the complete scientific fits, preprocessing and full_training "
        "under the supplied operator constraints and recorded evidence. Each fit contains only fit_id, stage "
        "(SMOKE or FULL), arm, fold, realization, outputs and validation_checks; include preprocessing_id "
        "when preprocessing is declared. Use declared-preprocessing-partitions/v1 and measured-full-training/v1. "
        "environment_requirements uses scientific-environment-requirements/v1 with exactly schema, python "
        "(major.minor), packages (canonical distribution names to exact versions), and cuda (major.minor). "
        "Choose scientifically justified dependencies; the existing runtime requires nnunetv2 2.8.1 and torch. "
        "These are declared requirements, not an observed image. The supplied synthetic CPU environment "
        "tests your code; its hash is not the future execution environment. Each preprocessing row uses "
        "environment_requirements_sha256, the SHA256 of its requirements encoded as sorted compact JSON "
        "with a final newline, instead of environment_sha256. Preserve all real original input, cohort, "
        "source, split and partition bindings. A later root-selected image must satisfy these exact reviewed "
        "requirements with genuine native evidence before execution. Approval and sealing here do not "
        "admit execution and never rewrite the approved plan to insert a future image. "
        "Do not invent missing input or split hashes: report any missing "
        "prerequisite explicitly. The independent reviewer must judge this exact plan, actual code and tests. "
        "SPEC.proposed.md must contain exactly one run_id line, one operator_scope_sha256 line with the "
        "original operator constraint hash above, and one execution_plan_sha256 line with SHA256 of the "
        "exact execution.plan.json bytes you wrote. A revised plan is a new preserved version and needs review. ")
