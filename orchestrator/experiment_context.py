"""Protected item4/6 model-input connection; no admission or execution here.

Driver.prepare_input calls this before reserving any scientific call. This
module does not make a completed spec into an execution or create an allowance.
"""
import json
from pathlib import Path
from orchestrator import manual_context, context_budget, diagnostics_policy
from orchestrator.manual_executor import digest
from orchestrator.modal_item4_policy import AUTHORITY as ITEM4_AUTHORITY

ITEM4_RUN = "experiment-" + ITEM4_AUTHORITY[:24]
TASKS = {4: "sprint13b-execution", 6: "directions-diagnostics"}


def validate_selection(config, plan, context):
    """Pure pre-write selection check shared by initialization and live input assembly."""
    from orchestrator.analysis_revisions import POLICY
    if config.get("revision_policy") != POLICY:
        raise ValueError("EXPERIMENT_REVISION_POLICY_REQUIRED")
    from orchestrator.experiment_plan_output import enabled
    enabled(config)
    from orchestrator import experiment_partition_input as partitions
    if config.get("frozen_partitions") != plan.get("frozen_partitions"):
        raise ValueError("EXPERIMENT_PARTITIONS_SELECTION_CHANGED")
    partitions.resolve(config, context)
    if config.get("authored_execution_plan") != plan.get("authored_execution_plan"):
        raise ValueError("EXPERIMENT_AUTHORED_PLAN_MODE_CHANGED")
    value = config.get("execution_scope")
    fields = {"schema", "item_number", "run_id", "authority_sha256", "plan_sha256"}
    if not isinstance(value, dict) or set(value) != fields or value["schema"] != "scientific-execution/v1":
        raise ValueError("EXPERIMENT_SELECTION_FIELDS")
    item = value["item_number"]
    if type(item) is not int or item not in TASKS or config.get("item_number") != item:
        raise ValueError("EXPERIMENT_SELECTION_ITEM")
    expected_run = ITEM4_RUN if item == 4 else diagnostics_policy.RUN_ID
    expected_authority = ITEM4_AUTHORITY if item == 4 else diagnostics_policy.authority()
    if (value["run_id"] != expected_run or config.get("run_id") != expected_run
            or value["authority_sha256"] != expected_authority
            or config.get("backend") != ("modal" if item == 4 else "cpu")
            or config.get("review_contract") != "bound-review/v1"
            or not isinstance(config.get("idea_ids"), list) or not config["idea_ids"]
            or config["idea_ids"][0] != TASKS[item]):
        raise ValueError("EXPERIMENT_SELECTION_BINDING")
    # This is a separate, hash-bound execution selection in the immutable plan,
    # not a self-referential hash of a plan containing its own hash.
    if plan.get("execution_scope") != value:
        raise ValueError("EXPERIMENT_SELECTION_CHANGED")
    ref = plan.get("execution_plan")
    if (not isinstance(ref, dict) or set(ref) != {"path", "sha256"}
            or ref["sha256"] != value["plan_sha256"]):
        raise ValueError("EXPERIMENT_PLAN_BINDING")
    selected = context_budget.relative_file(context, ref["path"]).read_bytes()
    if digest(selected) != ref["sha256"]:
        raise ValueError("EXPERIMENT_PLAN_CHANGED")
    for key in ("private_intake", "idea_ids", "item_number", "item_sha256", "revision_policy"):
        if plan.get(key) != config.get(key):
            raise ValueError("EXPERIMENT_CONTEXT_BINDING")
    if item == 6:
        diagnostics_policy.validate_config(config, expected_run)
        environment = config.get("synthetic_environment")
        if (not isinstance(environment, dict) or set(environment) != {"environment_root", "environment_sha256"}
                or plan.get("synthetic_environment") != environment):
            raise ValueError("EXPERIMENT_SYNTHETIC_ENVIRONMENT_BINDING")
    elif (config.get("notebook_revision", {}).get("mode") != "item4-execution-revision"
            or plan.get("notebook_revision") != config["notebook_revision"]):
        raise ValueError("EXPERIMENT_NOTEBOOK_REVISION_REQUIRED")
    return value



def selection(driver):
    raw = (driver.state / "preparation-plan.json").read_bytes()
    if digest(raw) != driver.config.get("plan_sha256"):
        raise ValueError("EXPERIMENT_PREPARATION_CHANGED")
    return validate_selection(driver.config, json.loads(raw), driver.context)


def outputs(driver, stage):
    selected = selection(driver)
    if stage not in manual_context.OUTPUTS:
        raise ValueError("EXPERIMENT_STAGE")
    extra = ()
    if stage == "run_spec_author":
        extra = ("notebook.patch.json",) if selected["item_number"] == 4 else ("analysis.program.json",)
    from orchestrator.experiment_plan_output import enabled, OUTPUT
    if stage == "run_spec_author" and enabled(driver.config): extra += (OUTPUT,)
    return manual_context.OUTPUTS[stage] + extra


def prepare(driver, value, stage, work):
    selected = selection(driver)
    item = selected["item_number"]
    if item == 4:
        from orchestrator.notebook_revision import validate_config, successor_instructions
        from orchestrator.cpu_isolation import verify_environment
        config = driver.config["notebook_revision"]
        validate_config(driver.context, config)
        verify_environment(config["environment"])
        contract = successor_instructions(config["safe_view"]["sha256"])
        contract += (" The frozen execution plan must set dispatch_mode to incremental for staged "
            "runtime provisioning. Keep every smoke, benchmark and full fit in its original fits list; "
            "each fit names the exact preprocessing_id it consumes when preprocessing is declared. "
            "Runtime selections are append-only subsets, not changes to scientific identities. "
            "Coverage-independent fits must not depend on coverage-only preprocessing. Full fits "
            "remain subject to the measured projection and smoke gates. The frozen plan's "
            "full_training contract uses measured-full-training/v1: timing_file, three "
            "benchmark_fit_ids, benchmark_comparability_id, resume_fit_id, and full_fits "
            "in frozen FULL-fit order. Each projection row names fit_id, timing_fit_id "
            "for the same arm on the benchmark-selected GPU, epochs, fixed_seconds, "
            "overhead_micro_usd and assumption (that exact field name), a nonempty string explaining scientific applicability. No additional projection-row keys are allowed. "
            "The declared timing_file uses experiment-epoch-timing/v1 with fit_id, "
            "completed_epochs, elapsed_training_seconds, real_epoch, loader_not_bottleneck "
            "and comparability_id. Implement the frozen validation criteria; never write "
            "a passing boolean without the measured supporting evidence. Benchmark all "
            "three GPUs with comparable arm/fold/work and CPU/RAM resources. Record actual "
            "epochs; controller measurements and synthetic tests are not scientific approval. "
            "Before fits, the same reviewed module must implement preprocess(input_root, "
            "output_root, contract) on verified source files and validate_preprocessing(output_root, "
            "contract). The frozen plan's preprocessing selection declares its ID, input contract, "
            "environment requirements (with real native image identity resolved separately before execution), "
            "split, plans name, cohort and source-capture identities before execution. "
            "No outcome tuning or new cohort is permitted. All scientific preprocessing choices "
            "belong to you and the independent reviewer. Persist each completed step with "
            "contract['checkpoint'](step_id, files), where files maps newly completed relative paths "
            "to sha256 and bytes. Do not alter a committed file or emit a fake training checkpoint. "
            "A linked interrupted segment supplies contract['completed_steps'], mapping each "
            "already committed step to its verified file hashes and sizes. Reuse those files "
            "without recomputation or rewriting them; continue only missing steps and retain "
            "the same frozen methods. The infrastructure copies and verifies original bytes "
            "inside the existing private Volume and separately admits the linked segment. "
            "The validator returns exactly proposed and validation: proposed uses the existing "
            "modal-item4-preprocessed/v1 receipt with all 99 case files and shared dataset/plans/splits; "
            "validation uses modal-preprocessing-validation/v1 with status PASS, errors [], "
            "run/spec/module/validator/cohort/input/environment bindings and the same complete files. "
            "Both code hashes name your exact exported module. The wrapper checks every output byte; "
            "returning successfully alone is not validation. Include synthetic tests of preprocessing "
            "and its refusals in synthetic_tests. The resulting plans hash is observed and then "
            "frozen for every consuming fit. The execution module's main(input_root, output_root, contract) receives "
            "the unchanged frozen plan as contract['execution_plan'] and the validated controller "
            "binding as contract['runtime']. input_root contains only verified preprocessed inputs; "
            "output_root is a fresh private directory for the declared returned files only. "
            "contract['progress'] is the already-locked FitProgress writer for the bound private "
            "Volume; use it to publish periodic checkpoints and the complete native final checkpoint. "
            "The package supplies orchestrator.modal_nnunet.run_fit(trainer, progress, initial=..., "
            "save_every=..., segment=..., interruption=...) for the existing native save/load path; "
            "construct the scientifically selected trainer in your reviewed module and do not open "
            "a second progress.writer while this one is locked. "
            "Keep the native trainer log_file inside this fit's private progress.root/work directory; "
            "run_fit records that native log for the controller before training starts. "
            "Use contract['runtime']['experiment']['segment'] as the segment, initial=(segment == 1), "
            "and pass contract['runtime'].get('resume') as interruption; a later segment must load "
            "the existing native checkpoint, never initialize fresh weights. "
            "The wrapper publishes declared outputs through the existing durable result contract "
            "after main returns; incomplete checkpoints or missing/extra files refuse. "
            "Each frozen fit lists validation_checks (unique check IDs) and aggregate-only output "
            "filenames, including validation.json. Your reviewed code evaluates those checks and "
            "writes validation.json with schema experiment-validation/v1, run_id, fit_id, "
            "spec_sha256, code_sha256 and execution_plan_sha256 from contract['runtime']; "
            "files maps every other declared output to its sha256 and byte count (bytes); "
            "checks lists each frozen ID in order with status PASS and evidence filenames. "
            "Every returned file must support a check. Missing, failed or ambiguous checks refuse. "
            "Return only aggregate UTF-8 JSON/CSV/Markdown/text, at most 1500000 bytes per file, "
            "with no patient rows, identifiers, secrets or opaque payloads. Patient-level predictions "
            "and native weights stay on the approved private Volume, outside output_root. "
            "The infrastructure scan and envelope validation do not establish scientific acceptance. "
            "Choose no new patients, definitions or arms at "
            "runtime. Code, not the infrastructure wrapper, owns scientific preprocessing, training, "
            "scoring and methodological checks. A program execution receipt is not validation. ")
    else:
        from orchestrator.cpu_isolation import verify_environment
        verify_environment(driver.config["synthetic_environment"])
        contract = ("You own the diagnostic definitions, implementation and scientific conclusions. "
            "Write analysis.program.json with schema scientific-program/v2, run_id, "
            "execution_plan_sha256, and files with exactly analysis.py and test_analysis.py "
            "as UTF-8 source strings, plus contract with schema diagnostics-program-contract/v1, "
            "input_contract_sha256 and input_capture_sha256 copied from the frozen input selection, "
            "outputs (2-32 aggregate .json/.csv/.md/.txt filenames including validation.json), "
            "validation_checks (unique check IDs), and requirements {python: major.minor, "
            "distributions: {package: exact_version}}. No dependency installation at execution. "
            "The selected immutable image must satisfy those requirements before patient computation. "
            "No future image hash is needed to draft your requirements. All five diagnostics share "
            "one CPU run with no training. analysis.py must expose main(input_root, output_root, contract); "
            "test_analysis.py contains unittest tests using synthetic inputs only. "
            "The controller scans, compiles and runs those tests in the existing isolated CPU sandbox. "
            "Do not execute patient computation, model training, provider operations or other model calls "
            "in this author workspace. Review the actual code and test receipts, not just the spec. "
            "main receives the frozen operator constraints as contract['execution_plan'] and "
            "the validated binding as contract['runtime']. Write validation.json with schema "
            "diagnostics-validation/v1 and runtime run_id, source, spec_sha256, code_sha256, "
            "execution_plan_sha256, input_contract_sha256, environment_sha256; files maps "
            "all other declared outputs to sha256/bytes, checks lists each declared id in order "
            "with status PASS and evidence filenames. Every output must support a check. "
            "No passing boolean without measured evidence. Only aggregate UTF-8 returns, at most "
            "1500000 bytes each; no per-patient rows, identifiers, secrets or opaque payloads. ")
    if stage.startswith("result_interpretation"):
        contract = ("The scientific code belongs to the reviewed spec. Interpret and independently "
            "review the actual execution results; do not revise or rerun the implementation here. ")
    elif stage == "run_spec_review":
        contract = ("Review the actual author-produced code/diff and controller synthetic-test "
            "receipts against the frozen execution plan. No implementation or experiment execution "
            "in this reviewer workspace. ")
    from orchestrator import experiment_plan_output as authored
    if authored.enabled(driver.config) and stage == "run_spec_author":
        contract = authored.instructions(selected) + contract
    from orchestrator import experiment_partition_input as partitions
    if partitions.enabled(driver.config) and stage.startswith("run_spec"):
        contract += (" Frozen development partitions are supplied through registered view " +
            driver.config["frozen_partitions"]["view_id"] + " with original SHA256 " +
            driver.config["frozen_partitions"]["sha256"] + ". Every authored preprocessing selection "
            "must bind partitions_sha256 to that original hash. New declared-environment plans use "
            "declared-preprocessing-partitions/v1; legacy native-bound plans retain "
            "reviewed-preprocessing-partitions/v1. Draft approval does not admit paid execution. "
            "The reviewed preprocess function receives contract['frozen_partitions'] with path and sha256 "
            "for the exact read-only frozen-partitions.json on the package. This is the original membership "
            "input, not the emitted splits_final.json; split_sha256 separately binds your reviewed output. "
            "You own split implementation and checks; infrastructure does not choose or generate folds. ")
    task = driver.task(stage, value) + "\n" + contract
    # Actual drivers bind this policy before calling prepare; pure context
    # fixtures without a ledger do not claim an admitted revision allowance.
    if hasattr(driver, "store"):
        from orchestrator.analysis_revisions import instructions
        task += "\n" + instructions(driver.store, driver.config["run_id"], notebook_revision=item == 4)
    if stage.startswith("run_spec") and not authored.enabled(driver.config):
        task += ("\nSPEC.proposed.md must contain exactly these binding lines:\nrun_id: " +
                 selected["run_id"] + "\nexecution_plan_sha256: " + selected["plan_sha256"] + "\n")
    task += ("\nExecution selection SHA256: " + selected["plan_sha256"] +
             ". Every definition must be frozen before real computation. "
             "A later execution requires its own ordinary validation and spending gates. ")
    plan = json.loads((driver.state/"preparation-plan.json").read_bytes())
    selected_plan = {"id":"frozen-execution-plan", "type":"configuration", "version":1,
                     **plan["execution_plan"]}
    artifacts = list(value["artifacts"])
    if authored.enabled(driver.config) and stage != "run_spec_author":
        current_plan = authored.ref(driver, value)
        task += ("\nOriginal operator constraint SHA256: " + selected["plan_sha256"] +
                 "; current authored execution plan SHA256: " + current_plan["sha256"] +
                 ". Review/interpret the exact current plan and its separate SPEC bindings. ")
    existing = [row for row in artifacts if row.get("id") == selected_plan["id"]]
    if existing and existing != [selected_plan]:
        raise ValueError("EXPERIMENT_DELIVERY_PLAN_CONFLICT")
    if not existing:
        artifacts.append(selected_plan)
    return manual_context.prepare(driver.context, stage=stage, idea_ids=driver.config["idea_ids"],
        task=task, artifacts=artifacts, workspace=work,
        private_intake=driver.config["private_intake"], structured_review=True,
        reference_prior_results=True, execution_mode=TASKS[item],
        notebook_patch=item == 4 and stage == "run_spec_author",
        analysis_program=item == 6 and stage == "run_spec_author",
        execution_plan=authored.enabled(driver.config) and stage == "run_spec_author")


def accept_author(driver, value, pending):
    """Called after the existing driver verified the native output hashes."""
    selected = selection(driver)
    work = Path(pending["workspace"])
    raw = (work/"SPEC.proposed.md").read_bytes()
    text = raw.decode()
    if len(text) > 12000:
        raise ValueError("EXPERIMENT_SPEC_LIMIT")
    from orchestrator import experiment_plan_output as authored
    plan_raw = None
    plan_pin = selected["plan_sha256"]
    if authored.enabled(driver.config):
        plan_raw = (work/authored.OUTPUT).read_bytes()
        original, cases = authored.cohort(driver)
        from orchestrator.experiment_partition_input import plan_pin
        authored.validate(plan_raw, selected, cases, original, partitions_sha256=plan_pin(driver.config, driver.context))
        plan_pin = digest(plan_raw)
        if text.splitlines().count("operator_scope_sha256: "+selected["plan_sha256"]) != 1:
            raise ValueError("EXPERIMENT_SPEC_OPERATOR_BINDING")
    for line in ("run_id: "+selected["run_id"], "execution_plan_sha256: "+plan_pin):
        if text.splitlines().count(line) != 1:
            raise ValueError("EXPERIMENT_SPEC_BINDING")
    from orchestrator.scientific_intake import cohort
    registry_ref = driver.config["private_intake"]
    registry_raw = context_budget.relative_file(driver.context, registry_ref["path"]).read_bytes()
    if digest(registry_raw) != registry_ref["sha256"]:
        raise ValueError("EXPERIMENT_REGISTRY_CHANGED")
    registry = json.loads(registry_raw)
    cases = cohort(context_budget.relative_file(driver.context, registry["cohort"]).read_bytes())
    if selected["item_number"] == 4:
        from orchestrator.notebook_revision import prepare_artifacts
    else:
        from orchestrator.scientific_program import prepare_artifacts
    prepare_artifacts(driver, value, pending, cases)
    if plan_raw is not None: authored.preserve(driver, value, pending, plan_raw)
    for kind in ("run_spec", "proposed_run_spec"):
        driver.artifact(value, kind, "EXPERIMENT-SPEC-"+str(pending["round"])+".md", raw, pending["round"])
    value.update(phase="run_spec_review", spec=str(work/"SPEC.proposed.md"))


def require_tested_approval(driver, value):
    selected = selection(driver)
    key = "notebook_revision_result" if selected["item_number"] == 4 else "program_result"
    result = value.get(key, {})
    if result.get("synthetic_status") != "PASS":
        raise ValueError("EXPERIMENT_APPROVAL_REQUIRES_SYNTHETIC_PASS")
    expected = driver.state / ("notebook-revisions" if selected["item_number"] == 4 else "scientific-programs")
    folder = Path(result.get("folder", ""))
    from orchestrator import private_records, scientific_intake
    if not folder.is_absolute() or folder.parent != expected:
        raise ValueError("EXPERIMENT_TEST_RECEIPT_SCOPE")
    raw = private_records.check(folder/"synthetic/receipt.json").read_bytes()
    receipt = json.loads(raw)
    pin = (digest(scientific_intake.canonical(receipt)) if selected["item_number"] == 4
           else digest(json.dumps(receipt, sort_keys=True).encode()))
    expected_pin = (result.get("tests_sha256") if selected["item_number"] == 4
                    else result.get("provenance", {}).get("synthetic_tests_sha256"))
    if pin != expected_pin or receipt.get("status") != "PASS":
        raise ValueError("EXPERIMENT_TEST_RECEIPT_CHANGED")
    for name, expected_pin in receipt["preserved_files"].items():
        source = context_budget.relative_file(folder/"synthetic", name)
        private_records.check(source)
        if digest(source.read_bytes()) != expected_pin:
            raise ValueError("EXPERIMENT_TEST_EVIDENCE_CHANGED")
