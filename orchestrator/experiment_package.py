"""Freeze the actual reviewed code, plan and tests at the driver package boundary.

This package is not a provider admission or an execution receipt. The execution
adapter must verify it before reserving a job; no legacy Sprint10 fall-through.
"""
import json
from pathlib import Path
from orchestrator import experiment_approval as approval, private_records as pr
from orchestrator import context_budget as cb, review_submission as rs
from orchestrator.manual_executor import digest, inventory
from orchestrator.manual_driver import write_once, git


def contents(driver, value):
    approved = approval.verify(driver, value)
    selection = approved["selection"]
    prep = json.loads(approval.checked(driver.state/"preparation-plan.json"))
    work = Path(approved["pending_review"]["workspace"])
    plan_ref = approved.get("authored_execution_plan", prep["execution_plan"])
    files = {
        "SPEC.md": approval.checked(Path(approved["spec"])),
        "review.json": approval.checked(work/"review.json", approved["review_sha256"]),
        "approval.json": approval.checked(Path(value["reviewed_execution"]["path"]),
                                          value["reviewed_execution"]["sha256"]),
        "execution-plan.json": approval.checked(cb.relative_file(driver.context, plan_ref["path"]),
                                                plan_ref["sha256"]),
    }
    if "private_execution_inputs" in approved:
        ref = approved["private_execution_inputs"]["frozen_partitions"]
        files[ref["package_name"]] = approval.checked(
            cb.relative_file(driver.context, ref["source_path"]), ref["sha256"])
    for name, ref in approved["code_files"].items():
        if Path(name).name != name or name in {".", ".."}:
            raise ValueError("EXPERIMENT_PACKAGE_CODE_PATH")
        files["code/"+name] = approval.checked(Path(ref["path"]), ref["sha256"])
    # Include the exact selected review artifacts, not old prompts or transcripts.
    # Their original references and hashes stay in approval.json.
    for index, ref in enumerate(approved["artifacts"]):
        files["reviewed-artifacts/"+str(index)+".bin"] = approval.checked(
            cb.relative_file(driver.context, ref["path"]), ref["sha256"])
    result = value["notebook_revision_result" if selection["item_number"] == 4 else "program_result"]
    folder = Path(result["folder"])/"synthetic"
    raw = approval.checked(folder/"receipt.json")
    files["synthetic/receipt.json"] = raw
    for name, sha in rs.contract.strict_json(raw)["preserved_files"].items():
        files["synthetic/"+name] = approval.checked(cb.relative_file(folder, name), sha)
    manifest = {"schema":"experiment-package/v1", "source":driver.config["source"],
        "selection":selection, "reviewed_execution_sha256":value["reviewed_execution"]["sha256"],
        "files":{name:digest(raw) for name,raw in sorted(files.items())},
        "execution_admitted":False, "real_data_execution":False}
    return files, manifest


def verify(driver, value, folder):
    folder = Path(folder)
    pr.check_tree(folder)
    expected, manifest = contents(driver, value)
    raw = rs.canonical(manifest)
    approval.checked(folder/"manifest.json", digest(raw))
    if inventory(folder) != {**manifest["files"], "manifest.json":digest(raw)}:
        raise ValueError("EXPERIMENT_PACKAGE_INVENTORY_CHANGED")
    return manifest


@pr.private_umask
def emit(driver, value):
    files, manifest = contents(driver, value)
    folder = driver.state/"experiment-package"
    if folder.exists() or folder.is_symlink():
        if not (folder/"manifest.json").is_file():
            raise ValueError("EXPERIMENT_PACKAGE_PARTIAL_INSPECT_NO_REBUILD")
        return verify(driver, value, folder)
    pr.mkdir(folder)
    for name, raw in sorted(files.items()):
        write_once(folder/name, raw)
    write_once(folder/"manifest.json", rs.canonical(manifest))
    return verify(driver, value, folder)


@pr.private_umask
def commit_spec(driver, value):
    approved = approval.verify(driver, value)
    target = driver.root/"projects/isles24/experiments"/approved["selection"]["run_id"]/"spec"
    # A completed identical commit can be recovered after local save interruption;
    # changed or unrelated edits never get swept into this commit.
    expected = {"SPEC.md":approval.checked(Path(approved["spec"])),
        "review.json":approval.checked(Path(value["spec_review"]), approved["review_sha256"]),
        "reviewed-execution.json":approval.checked(Path(value["reviewed_execution"]["path"]),
                                                   value["reviewed_execution"]["sha256"])}
    if git(driver.root, "status", "--porcelain"):
        raise ValueError("UNRELATED_EDITS_BEFORE_EXPERIMENT_COMMIT")
    if target.exists():
        pr.check_tree(target)
        if inventory(target) != {k:digest(v) for k,v in expected.items()}:
            raise ValueError("EXPERIMENT_COMMITTED_SPEC_CHANGED")
        for name, raw in expected.items():
            relative = str((target/name).relative_to(driver.root))
            # git() strips output, so inspect bytes directly for exact identity.
            import subprocess
            committed = subprocess.check_output(["git", "show", "HEAD:"+relative], cwd=driver.root)
            if committed != raw:
                raise ValueError("EXPERIMENT_COMMITTED_SPEC_CHANGED")
    else:
        import subprocess
        for name, raw in expected.items(): write_once(target/name, raw)
        subprocess.run(["git", "add", "--", str(target)], cwd=driver.root, check=True,
                       capture_output=True)
        subprocess.run(["git", "commit", "-m", "Record reviewed experiment specification and code binding"],
                       cwd=driver.root, check=True, capture_output=True)
        pr.check_tree(target)
    value.update(phase="EMIT_EXPERIMENT_PACKAGE", spec_commit=git(driver.root,"rev-parse","HEAD"))
    driver.save(value)
    return driver.status()


def advance(driver, value, collect_folder=None, identity_refusal=None):
    if collect_folder is not None or identity_refusal is not None:
        raise ValueError("EXPERIMENT_LEGACY_COLLECTION_REFUSED")
    if value["phase"] == "COMMIT_SPEC":
        return commit_spec(driver, value)
    if value["phase"] == "EMIT_EXPERIMENT_PACKAGE":
        manifest = emit(driver, value)
        value.update(phase="EXECUTE_EXPERIMENT", execution_package={
            "path":str(driver.state/"experiment-package"),
            "sha256":digest(rs.canonical(manifest))})
        driver.save(value)
        return driver.status()
    if driver.config['item_number']==6 and value['phase'] in {'EXECUTE_EXPERIMENT','COLLECT_EXPERIMENT'}:
        from orchestrator import diagnostics_execution
        return (diagnostics_execution.advance if value['phase']=='EXECUTE_EXPERIMENT' else diagnostics_execution.collect)(driver,value)
    if value["phase"] == "EXECUTE_EXPERIMENT" and driver.config["item_number"] == 4:
        from orchestrator.experiment_dispatch import advance as dispatch
        return dispatch(driver, value)
    if value['phase'] == 'COLLECT_EXPERIMENT' and driver.config['item_number'] == 4:
        from orchestrator.experiment_collection import advance as collect
        return collect(driver, value)
    if value['phase']=='UPDATE_STATE' and driver.config['item_number'] in {4,6}:
        from orchestrator.experiment_acceptance import prepare
        return prepare(driver,value)
    if value['phase'] in {'REPORT','COMPLETE'} and driver.config['item_number'] in {4,6}:
        from orchestrator.experiment_acceptance import finish
        return finish(driver,value)
    # Other execution modes remain required downstream connections.
    # Do not fall through to Sprint10 or an analysis-only validation.
    raise ValueError("EXPERIMENT_EXECUTOR_CONNECTION_REQUIRED")
