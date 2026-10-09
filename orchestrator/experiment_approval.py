"""Bind an execution candidate to the exact accepted scientific review delivery.

This does not admit execution, grant spending, or reinterpret a verdict. The
preserved call receipt and MCP submission remain the independent judgment.
"""
import json
from pathlib import Path
from orchestrator import context_budget as cb, experiment_context as ec
from orchestrator import manual_context as mc, private_records as pr, review_submission as rs
from orchestrator.manual_executor import digest

REQUIRED = {
    4: {"run_spec", "notebook_source", "notebook_diff", "notebook_patch", "synthetic_tests",
        "notebook_provenance", "execution_conditions"},
    6: {"run_spec", "analysis_source", "analysis_tests", "analysis_provenance", "synthetic_tests"},
}


def checked(path, pin=None):
    raw = pr.check(path).read_bytes()
    if pin is not None and digest(raw) != pin:
        raise ValueError("EXPERIMENT_APPROVAL_EVIDENCE_CHANGED")
    return raw


def verified_review_delivery(driver, pending, stage):
    """Verify actual call, immutable input and server-side accepted submission."""
    work = Path(pending["workspace"])
    expected_work = Path(driver.config.get("workspace_root",
        driver.state.parent/(driver.state.name+"-scientific-workspaces")))/(stage+"-"+str(pending["round"]))
    expected_id = digest((driver.config["run_id"]+":"+stage+":"+str(pending["round"])).encode())
    if pending["stage"] != stage or work != expected_work or pending["id"] != expected_id:
        raise ValueError("EXPERIMENT_APPROVAL_CALL_BINDING")
    row = driver.store.db.execute("SELECT * FROM manual_calls WHERE id=?", (expected_id,)).fetchone()
    if row is None or row["status"] != "COMPLETE":
        raise ValueError("EXPERIMENT_APPROVAL_COMPLETE_CALL_REQUIRED")
    if row["stage"] != stage or row["attempt"] != pending["round"]:
        raise ValueError("EXPERIMENT_APPROVAL_CALL_BINDING")
    receipt = json.loads(row["receipt"])
    if receipt.get("stage") != stage or receipt.get("workspace") != str(work) or receipt.get("outcome") != "COMPLETE":
        raise ValueError("EXPERIMENT_APPROVAL_RECEIPT_BINDING")
    prompt = checked(work/"prompt.md", receipt["input_sha256"]).decode()
    raw_review = checked(work/"review.json", receipt["output_sha256"]["review.json"])
    pins = rs.runtime_pins(work)
    if pins != receipt.get("submission_preflight"):
        raise ValueError("EXPERIMENT_APPROVAL_SUBMISSION_CHANGED")
    cfg = rs.load(work, pins["config_sha256"])
    expected = {"call_id":expected_id, "run_id":driver.config["run_id"], "stage":stage,
        "source_sha":driver.config["source"], "runtime_sha256":driver.config["clients"]["runtime_config_sha256"],
        "input_sha256":receipt["input_sha256"]}
    if cfg["kind"] != "scientific" or cfg["bindings"] != expected:
        raise ValueError("EXPERIMENT_APPROVAL_SUBMISSION_BINDING")
    native = receipt["native"]
    submission = native["review_submission"]
    raw_submission = checked(work/rs.RECORD, submission["record_sha256"])
    if submission["config_sha256"] != pins["config_sha256"]:
        raise ValueError("EXPERIMENT_APPROVAL_SUBMISSION_CHANGED")
    console = checked(work/"console.log", native["console_sha256"])
    decision, verified_submission = rs.verify_scientific(work, console)
    if verified_submission != submission:
        raise ValueError("EXPERIMENT_APPROVAL_NATIVE_BINDING")
    if rs.canonical(decision) != raw_review:
        raise ValueError("EXPERIMENT_APPROVAL_NATIVE_BINDING")
    return work, prompt, raw_review, receipt, row, raw_submission


def review_delivery(driver, pending, stage):
    """Execution and acceptance still require a genuine clean APPROVE."""
    result = verified_review_delivery(driver, pending, stage)
    decision = rs.contract.strict_json(result[2])
    if decision["verdict"] != "APPROVE" or decision["findings"]:
        raise ValueError("EXPERIMENT_APPROVAL_REQUIRED")
    return result


def inspect(driver, value, pending):
    selected = ec.selection(driver)
    ec.require_tested_approval(driver, value)
    stage = "run_spec_review"
    work, prompt, raw_review, receipt, row, raw_submission = review_delivery(driver,pending,stage)
    measurement = json.loads(checked(work/"input-measurement.json"))
    rows = mc.selected_artifacts(stage, value["artifacts"])
    plan = json.loads(checked(driver.state/"preparation-plan.json"))
    required_rows = []
    for kind in sorted(REQUIRED[selected["item_number"]]):
        matches = [r for r in rows if r["type"] == kind and r["id"] == kind]
        if len(matches) != 1: raise ValueError("EXPERIMENT_APPROVAL_ARTIFACT_REQUIRED:"+kind)
        required_rows.append(matches[0])
    required_rows.append({"id":"frozen-execution-plan", "type":"configuration", "version":1, **plan["execution_plan"]})
    from orchestrator import experiment_plan_output as authored
    authored_ref = authored.ref(driver, value) if authored.enabled(driver.config) else None
    if authored_ref is not None: required_rows.append(authored_ref)
    for ref in required_rows:
        if measurement["selected_artifacts"].count(ref) != 1:
            raise ValueError("EXPERIMENT_APPROVAL_NOT_DELIVERED:"+ref["type"])
        raw = checked(cb.relative_file(driver.context, ref["path"]), ref["sha256"])
        if mc.workspace_artifact(ref["type"], artifact_id=ref["id"]):
            matches = [r for r in measurement["workspace_files"] if r.get("id") == ref["id"] and r.get("type") == ref["type"]]
            if len(matches) != 1: raise ValueError("EXPERIMENT_APPROVAL_WORKSPACE_REQUIRED")
            delivered = matches[0]
            if (any(delivered.get(k) != ref[k] for k in ("id", "type", "version", "sha256"))
                    or delivered.get("source_path") != ref["path"] or cb.encoded(delivered) not in prompt):
                raise ValueError("EXPERIMENT_APPROVAL_DELIVERY_CHANGED")
            checked(cb.relative_file(work, delivered["path"]), ref["sha256"])
            if ref['type']=='configuration' and ref['id']=='authored-execution-plan':
                copy=delivered.get('readable_json',{})
                if (measurement['workspace_files'].count(copy)!=1 or copy.get('original_path')!=delivered['path']
                        or copy.get('original_sha256')!=ref['sha256'] or
                        checked(cb.relative_file(work,copy['path']),copy['sha256'])!=mc._pageable_json(raw)):
                    raise ValueError('EXPERIMENT_APPROVAL_PLAN_READING_COPY_CHANGED')
        elif cb.encoded(ref)+"\n"+raw.decode() not in prompt:
            raise ValueError("EXPERIMENT_APPROVAL_INLINE_CHANGED")
    by_type = {r["type"]:r for r in required_rows}
    result = value["notebook_revision_result" if selected["item_number"] == 4 else "program_result"]
    folder = Path(result["folder"])
    files = ({"revised.ipynb":"notebook_source", "notebook.diff":"notebook_diff",
              "patch-receipt.json":"notebook_provenance", "carried-conditions.json":"execution_conditions"}
             if selected["item_number"] == 4 else {"analysis.py":"analysis_source", "test_analysis.py":"analysis_tests"})
    outputs = {}
    for name,kind in files.items():
        checked(folder/name, by_type[kind]["sha256"])
        outputs[name] = {"path":str(folder/name), "sha256":by_type[kind]["sha256"]}
    test_receipt = rs.contract.strict_json(checked(folder/"synthetic/receipt.json"))
    shown_tests = rs.contract.strict_json(checked(cb.relative_file(driver.context, by_type["synthetic_tests"]["path"])))
    environment = (driver.config["notebook_revision"]["environment"] if selected["item_number"] == 4
                   else driver.config["synthetic_environment"])
    if (test_receipt != shown_tests or test_receipt.get("binding", {}).get("environment") != environment
            or test_receipt["binding"].get("patient_data") is not False):
        raise ValueError("EXPERIMENT_APPROVAL_TEST_BINDING")
    for name in (["revised.ipynb"] if selected["item_number"] == 4 else ["analysis.py", "test_analysis.py"]):
        pin = outputs[name]["sha256"]
        if (test_receipt["binding"].get("files", {}).get(name) != pin
                or test_receipt["preserved_files"].get("package/"+name) != pin):
            raise ValueError("EXPERIMENT_APPROVAL_TESTED_CODE_CHANGED")
        checked(folder/"synthetic/package"/name, pin)
    if selected["item_number"] == 4:
        from orchestrator.notebook_execution import extract
        module = extract(checked(folder/"revised.ipynb", outputs["revised.ipynb"]["sha256"]), preprocessing=True)
        module_pin = digest(module)
        if (test_receipt["binding"].get("files", {}).get("execution.py") != module_pin
                or test_receipt["preserved_files"].get("package/execution.py") != module_pin):
            raise ValueError("EXPERIMENT_APPROVAL_TESTED_CODE_CHANGED")
        checked(folder/"synthetic/package/execution.py", module_pin)
        from orchestrator.experiment_modal_package import support_files
        for name,raw in support_files().items():
            pin = digest(raw)
            if (test_receipt["binding"]["files"].get(name) != pin
                    or test_receipt["preserved_files"].get("package/"+name) != pin):
                raise ValueError("EXPERIMENT_APPROVAL_SUPPORT_TEST_BINDING")
            checked(folder/"synthetic/package"/name, pin)
        from orchestrator.notebook_execution import tests_passed
        if not tests_passed(test_receipt.get("tests"), module_pin):
            raise ValueError("EXPERIMENT_APPROVAL_EXECUTION_TEST_REQUIRED")
        outputs["execution.py"] = {"path":str(folder/"synthetic/package/execution.py"), "sha256":module_pin}
    if selected["item_number"] == 6:
        if rs.contract.strict_json(checked(cb.relative_file(driver.context, by_type["analysis_provenance"]["path"]))) != result["provenance"]:
            raise ValueError("EXPERIMENT_APPROVAL_PROVENANCE_CHANGED")
        raw_program = checked(folder/"analysis.program.json", result["program_sha256"])
        program = rs.contract.strict_json(raw_program)
        if (program["run_id"] != selected["run_id"] or program["execution_plan_sha256"] != selected["plan_sha256"]
                or set(program["files"]) != set(files) or any(digest(v.encode()) != outputs[k]["sha256"] for k,v in program["files"].items())):
            raise ValueError("EXPERIMENT_APPROVAL_PROGRAM_CHANGED")
        outputs["analysis.program.json"] = {"path":str(folder/"analysis.program.json"), "sha256":digest(raw_program)}
    checked(Path(value["spec"]), by_type["run_spec"]["sha256"])
    extra = {"authored_execution_plan":authored_ref} if authored_ref is not None else {}
    from orchestrator.experiment_partition_input import reviewed as reviewed_partitions
    partition_input = reviewed_partitions(driver.config, driver.context, work, measurement, prompt)
    if partition_input is not None:
        extra["private_execution_inputs"] = {"frozen_partitions":partition_input}
    if authored_ref is not None:
        lines = checked(Path(value["spec"])).decode().splitlines()
        for line in ("operator_scope_sha256: "+selected["plan_sha256"],
                     "execution_plan_sha256: "+authored_ref["sha256"]):
            if lines.count(line) != 1: raise ValueError("EXPERIMENT_APPROVAL_PLAN_SPEC_BINDING")
    return {"schema":"reviewed-execution-artifacts/v1", "selection":selected, **extra,
        "pending_review":pending, "review_sha256":digest(raw_review), "submission_sha256":digest(raw_submission),
        "input_sha256":receipt["input_sha256"], "call_receipt_sha256":digest(row["receipt"].encode()),
        "artifacts":required_rows, "code_files":outputs, "spec":str(value["spec"]),
        "execution_admitted":False}


@pr.private_umask
def record(driver, value, pending):
    from orchestrator.manual_driver import write_once
    manifest = inspect(driver, value, pending)
    path = driver.state/"reviewed-execution"/(pending["id"]+".json")
    raw = rs.canonical(manifest)
    write_once(path, raw)
    value["reviewed_execution"] = {"path":str(path), "sha256":digest(raw)}
    return manifest


def verify(driver, value):
    ref = value["reviewed_execution"]
    manifest = rs.contract.strict_json(checked(Path(ref["path"]), ref["sha256"]))
    expected = driver.state/"reviewed-execution"/(manifest["pending_review"]["id"]+".json")
    if Path(ref["path"]) != expected or inspect(driver, value, manifest["pending_review"]) != manifest:
        raise ValueError("EXPERIMENT_APPROVAL_SEAL_CHANGED")
    return manifest
