"""Read-only intake of the completed, independently approved Idea2 CPU job.

No science, execution, model admission or acceptance. The native interpretation
controller must verify the installed CPU authority before using this result.
Only validated aggregate output bytes may be delivered to scientific models.
"""
import json
import sqlite3
from pathlib import Path
from orchestrator import private_records as pr, idea2_cpu_contract as contract
from orchestrator.idea2_cpu_executor import JOB
from orchestrator.diagnostics_contract import validate_outputs, strict

PROGRAM_CONTRACT_SHA = '0ddf423f1a4327dca1db6904711245ea58f5c106d6cdea28a6a4ef7c05d7bfe3'
# Admission hashed the full frozen manifest (including kind); execution hashed
# its byte/hash projection. Both describe the same files and remain separately pinned.
ADMISSION_INPUTS = {"files": 728, "bytes": 3125648444,
    "manifest_sha256": "6e3e0c40ab3ed2e0acf134b8f5867293828ca538e749d618a5459c2d0607012e"}
EXECUTION_INPUTS = {"files": 728, "bytes": 3125648444,
    "manifest_sha256": "3c777cecfd7802742a39336a095364b603aa481327017c66b9bab603702a263a"}
OUTPUTS = frozenset(("integrity.json", "smoothing.json", "paired.json",
                     "limitations.md", "validation.json"))


def require(ok, reason):
    if not ok:
        raise ValueError("IDEA2_RESULTS_" + reason)


def read_job(path):
    """Never construct a write-capable executor or initialize a missing database."""
    path = pr.check(path)
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA query_only=ON")
    db.execute("BEGIN")
    try:
        rows = db.execute("SELECT * FROM jobs").fetchall()
        require(len(rows) == 1 and rows[0]["id"] == JOB, "EXACT_JOB")
        row = dict(rows[0])
        package = db.execute("SELECT manifest FROM manual_packages WHERE job=?", (JOB,)).fetchone()
        require(package is not None, "PACKAGE_RECORD")
        return row, strict(package[0])
    finally:
        db.rollback()
        db.close()


def verify(work, source, review):
    """Authenticate terminal records and aggregates; never open input payloads.

    The calling installed controller separately checks CPU authority and that
    its native unit is terminal. This function cannot authorize a model call.
    """
    import re
    require(re.fullmatch("[0-9a-f]{40}", source) and re.fullmatch("[0-9a-f]{64}", review), "APPROVAL_IDENTITY")
    work = Path(work)
    require(work.is_absolute(), "ABSOLUTE_WORK")
    read = lambda name: pr.check(work / name).read_bytes()
    value = lambda name: strict(read(name))
    row, package = read_job(work / "jobs.sqlite")
    require(row["status"] == "READY" and row["phase"] == "patient", "JOB_NOT_EXECUTED")
    binding = strict(row["binding"])
    fixed = {
        "run_id": contract.RUN, "source": source, "spec_sha256": contract.SPEC,
        "code_sha256": contract.CODE, "program_sha256": contract.PROGRAM,
        "scientific_review_sha256": contract.REVIEW,
        "implementation_review_sha256": review,
        "execution_plan_sha256": contract.PINS["execution-plan.json"],
        "input_contract_sha256": contract.PINS["input-contract.json"],
        "environment_sha256": contract.ENVIRONMENT,
        "venue": "existing-server-cpu", "incremental_micro_usd": 0,
    }
    require(all(binding.get(k) == v for k, v in fixed.items()), "EXECUTION_BINDING")
    require(package == binding["package_files"], "PACKAGE_BINDING")
    require(set(package) == {"analysis.py", "test_analysis.py", "contract.json", "run.py"},
            "PACKAGE_MEMBERS")
    require(package["analysis.py"]["sha256"] == contract.CODE
            and package["test_analysis.py"]["sha256"] == contract.TESTS,
            "SCIENTIFIC_BYTES")
    # Re-read only this tiny package. No patient input tree or scientific code executes.
    observed_package = contract.verify_tree(work / "package", package)
    full_contract = value("package/contract.json")
    require(full_contract["runtime"] == {k: binding[k] for k in full_contract["runtime"]}
            and all(full_contract[k] == v for k, v in binding["program_contract"].items()),
            "PROGRAM_CONTRACT_BINDING")
    require(contract.sha(contract.encoded(binding["program_contract"])) == PROGRAM_CONTRACT_SHA
            and set(binding["program_contract"]["outputs"]) == OUTPUTS, "EXACT_OUTPUTS")
    q = value("qualification/COMPLETE.json")
    require(q["status"] == "PASS" and q["source"] == source and q["review_sha256"] == review
            and q["patient_payloads_opened"] == q["model_calls"] == 0, "QUALIFICATION")
    require([(v["mode"], v["exit"]) for v in q["controls"]] ==
            [("readonly", 0), ("deliberately-writable", 1)], "NATIVE_CONTROLS")
    for control in q["controls"]:
        for stream in ("stdout", "stderr"):
            raw = read("qualification/" + control["mode"] + "/" + stream)
            require(contract.sha(raw) == control[stream + "_sha256"], "CONTROL_CHANGED")
    before, after = value("execution/before.json"), value("execution/after.json")
    expected_inputs = binding["input_verification"]["files"]
    expected = {"files": len(expected_inputs),
                "bytes": sum(r["bytes"] for r in expected_inputs.values()),
                "manifest_sha256": contract.sha(contract.encoded(expected_inputs))}
    require(expected == EXECUTION_INPUTS and before == after
            and before == {"inputs": expected, "package": observed_package},
            "BEFORE_AFTER_HASHES")
    intent = value("execution/dispatch-intent.json")
    exit_record = value("execution/process-exit.json")
    require(intent["job"] == JOB
            and intent["binding_sha256"] == contract.sha(row["binding"].encode())
            and intent["incremental_micro_usd"] == 0, "DISPATCH_BINDING")
    require(all(exit_record.get(k) == v for k, v in intent.items())
            and exit_record["exit_code"] == 0 and exit_record["uncertain"] is False
            and exit_record["valid"] is True and exit_record["error"] is None
            and exit_record["completed_at"] >= intent["started_at"]
            and exit_record["console_sha256"] == contract.sha(read("execution/console.log")),
            "TERMINAL_EXECUTION")
    validated = validate_outputs(work / "execution/return", binding)
    require(value("execution/validation.json") == validated, "VALIDATION_CHANGED")
    final = value("EXECUTION_COMPLETE.json")
    require(final["status"] == "EXECUTED_VALIDATED_NOT_SCIENTIFICALLY_ACCEPTED"
            and final["job"] == JOB and final["source"] == source
            and final["review_sha256"] == review and final["incremental_micro_usd"] == 0
            and final["return_path"] == str(work / "execution/return")
            and final["scientific_acceptance"] is False and final["interpretation_required"] is True,
            "FINAL_RECEIPT")
    require(final["admission"] == {"status": "QUEUED_EXISTING_SERVER_CPU", "job": JOB,
            "input_verification": ADMISSION_INPUTS, "incremental_micro_usd": 0,
            "scientific_acceptance": False}, "ADMISSION_RECEIPT")
    files = {name: read("execution/return/" + name) for name in sorted(OUTPUTS)}
    # Do not disclose metadata paths, IDs, package contract or raw logs to a model.
    public_receipt = {"schema": "idea2-private-aggregate-intake/v1",
        "run_id": contract.RUN, "cpu_source": source, "implementation_review_sha256": review,
        "scientific_program_sha256": contract.PROGRAM, "scientific_review_sha256": contract.REVIEW,
        "execution_receipt_sha256": contract.sha(read("EXECUTION_COMPLETE.json")),
        "exit_receipt_sha256": contract.sha(read("execution/process-exit.json")),
        "validation_sha256": contract.sha(read("execution/validation.json")),
        "input_files_verified_before_and_after": expected["files"],
        "package_files_verified_before_and_after": len(package),
        "files": validated["files"], "incremental_micro_usd": 0,
        "scientifically_accepted": False, "successor_execution_authorized": False}
    return {"validation": validated, "receipt": public_receipt, "files": files}
