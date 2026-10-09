"""Connect the sealed experiment package to the existing Modal fit executor.

No spec rewriting, provider calls, scientific choices or admission occur here.
The actual driver seal is reverified before emitting a provider package. Existing
cost, input, environment and fit guards still apply when that package is sent.
"""
from pathlib import Path
from orchestrator import experiment_package, private_records as pr
from orchestrator.manual_executor import digest, inventory, read
from orchestrator.manual_driver import write_once
from orchestrator.modal_executor import canonical

from orchestrator.experiment_worker import SUPPORT_FILES
WORKER = Path(__file__).with_name("experiment_worker.py")
DERIVED_FIELDS = frozenset({"execution", "code_sha256", "spec_sha256", "review_sha256", "execution_plan_sha256"})


def support_files():
    release = WORKER.parent.parent
    return {name:(release/name).read_bytes() for name in SUPPORT_FILES}


def manifest_for(binding):
    """Reconstruct only the file hashes already in the admitted binding.

    Scientific files stay immutable across segments. The complete per-segment
    manifest remains in controller records and travels in the bound launch.
    """
    execution=binding['execution']
    if set(execution['support_sha256'])!=set(SUPPORT_FILES):
        raise ValueError('EXPERIMENT_MANIFEST_FILE_BINDING')
    files={"run.py":execution['worker_sha256'], "execution.py":execution['module_sha256'],
        "SPEC.md":binding['spec_sha256'], "review.json":binding['review_sha256'],
        "execution-plan.json":binding['execution_plan_sha256'],
        "approval.json":execution['approval_sha256'],
        "reviewed-package.json":execution['package_manifest_sha256'], **execution['support_sha256']}
    extra={}
    if 'preprocessing' in binding:
        extra={'cohort.json':binding['preprocessing']['cohort_sha256'],
               'input-inventory.json':binding['preprocessing']['input_contract_sha256']}
        if binding['preprocessing'].get('schema') == 'reviewed-preprocessing-partitions/v1':
            extra['frozen-partitions.json'] = binding['preprocessing']['partitions_sha256']
        files.update(extra)
    if set(files)!={"run.py","execution.py","SPEC.md","review.json","execution-plan.json",
                   "approval.json","reviewed-package.json",*SUPPORT_FILES,*extra}:
        raise ValueError('EXPERIMENT_MANIFEST_FILE_BINDING')
    return {'schema':'modal-run/v1','binding':binding,'files':files}


def verify(package, binding, files):
    package = Path(package)
    execution = binding.get("execution")
    if (binding.get("purpose") != "M4_ITEM4" or not isinstance(execution, dict)
            or set(execution) != {"schema", "module", "package_manifest_sha256", "approval_sha256", "module_sha256", "worker_sha256", "support_sha256"}
            or execution["schema"] != "reviewed-module/v1" or execution["module"] != "execution.py"):
        raise ValueError("EXPERIMENT_MODAL_EXECUTION_SCOPE")
    if (files.get("execution.py") != execution["module_sha256"]
            or files.get("run.py") != execution["worker_sha256"]
            or execution["worker_sha256"] != digest(WORKER.read_bytes())
            or files.get("reviewed-package.json") != execution["package_manifest_sha256"]
            or files.get("approval.json") != execution["approval_sha256"]):
        raise ValueError("EXPERIMENT_MODAL_CODE_OR_SEAL_CHANGED")
    expected_support = {name:digest(raw) for name,raw in support_files().items()}
    if (execution['support_sha256'] != expected_support
            or any(files.get(name) != pin for name,pin in expected_support.items())):
        raise ValueError("EXPERIMENT_MODAL_SUPPORT_CHANGED")
    sealed = read(package/"reviewed-package.json")
    approval = read(package/"approval.json")
    selection = sealed["selection"]
    if (sealed["schema"] != "experiment-package/v1" or selection["item_number"] != 4
            or sealed["source"] != binding["source"] or selection["run_id"] != binding["run_id"]
            or approval.get("authored_execution_plan", {"sha256":selection["plan_sha256"]})["sha256"] != binding["execution_plan_sha256"]
            or approval["selection"] != selection or approval["execution_admitted"] is not False
            or sealed["reviewed_execution_sha256"] != execution["approval_sha256"]):
        raise ValueError("EXPERIMENT_MODAL_SELECTION_CHANGED")
    for name in ("SPEC.md", "review.json", "execution-plan.json", "approval.json"):
        if files.get(name) != sealed["files"].get(name):
            raise ValueError("EXPERIMENT_MODAL_REVIEWED_BYTES_CHANGED")
    if (files.get("execution.py") != sealed["files"].get("code/execution.py")
            or files["execution.py"] != approval["code_files"]["execution.py"]["sha256"]
            or binding["review_sha256"] != approval["review_sha256"]
            or files["execution-plan.json"] != binding["execution_plan_sha256"]):
        raise ValueError("EXPERIMENT_MODAL_REVIEWED_BYTES_CHANGED")
    lines = (package/"SPEC.md").read_text().splitlines()
    for line in ("run_id: "+binding["run_id"], "execution_plan_sha256: "+binding["execution_plan_sha256"]):
        if lines.count(line) != 1: raise ValueError("EXPERIMENT_MODAL_SPEC_BINDING")
    if "authored_execution_plan" in approval:
        plan = read(package/"execution-plan.json")
        if (plan.get("operator_scope_sha256") != selection["plan_sha256"]
                or lines.count("operator_scope_sha256: "+selection["plan_sha256"]) != 1):
            raise ValueError("EXPERIMENT_MODAL_OPERATOR_BINDING")
    code = {k:v for k,v in files.items() if k.endswith(".py")}
    if set(code) != {"run.py", "execution.py", *SUPPORT_FILES} or digest(canonical(code)) != binding["code_sha256"]:
        raise ValueError("EXPERIMENT_MODAL_CODE_IDENTITY")
    expected = {"run.py", "execution.py", "SPEC.md", "review.json", "execution-plan.json", "approval.json", "reviewed-package.json", *SUPPORT_FILES}
    if 'preprocessing' in binding:
        from orchestrator.experiment_preprocessing import scope
        scope(binding,read(package/'execution-plan.json'),(package/'cohort.json').read_bytes())
        expected.update({'cohort.json','input-inventory.json'})
        selected_input = approval.get('private_execution_inputs')
        if binding['preprocessing']['schema'] == 'reviewed-preprocessing-partitions/v1':
            if not isinstance(selected_input, dict) or set(selected_input) != {'frozen_partitions'}:
                raise ValueError('EXPERIMENT_PARTITIONS_REVIEW_REQUIRED')
            ref = selected_input['frozen_partitions']
            pin = binding['preprocessing']['partitions_sha256']
            if (ref.get('package_name') != 'frozen-partitions.json'
                    or ref.get('sha256') != pin or files.get('frozen-partitions.json') != pin
                    or sealed['files'].get('frozen-partitions.json') != pin
                    or ref.get('cohort_sha256') != binding['preprocessing']['cohort_sha256']):
                raise ValueError('EXPERIMENT_PARTITIONS_PACKAGE_BINDING')
            expected.add('frozen-partitions.json')
        elif selected_input is not None:
            raise ValueError('EXPERIMENT_PARTITIONS_UNSELECTED')
        for name,key in [('cohort.json','cohort_sha256'),('input-inventory.json','input_contract_sha256')]:
            if files.get(name)!=binding['preprocessing'][key]:raise ValueError('EXPERIMENT_PREPROCESSING_INPUT_BINDING')
    if set(files) != expected: raise ValueError("EXPERIMENT_MODAL_MEMBER_SET")


@pr.private_umask
def emit(driver, value, folder, runtime_binding, *, preprocessing_inputs=None):
    original = driver.state/"experiment-package"
    sealed = experiment_package.verify(driver, value, original)
    if sealed["selection"]["item_number"] != 4:
        raise ValueError("EXPERIMENT_MODAL_ITEM4_ONLY")
    if any(k in runtime_binding for k in DERIVED_FIELDS):
        raise ValueError("EXPERIMENT_MODAL_DERIVED_BINDING_FIELDS")
    if (runtime_binding.get("source") != sealed["source"]
            or runtime_binding.get("run_id") != sealed["selection"]["run_id"]):
        raise ValueError("EXPERIMENT_MODAL_RUNTIME_SELECTION")
    from orchestrator.item4_validation_admission import scope as validation_scope
    validation_scope(read(original/'approval.json'), runtime_binding)
    files = {name:(original/name).read_bytes() for name in
        ("SPEC.md", "review.json", "execution-plan.json", "approval.json")}
    files.update({"reviewed-package.json":(original/"manifest.json").read_bytes(),
                  "execution.py":(original/"code/execution.py").read_bytes(), "run.py":WORKER.read_bytes()})
    files.update(support_files())
    if 'preprocessing' in runtime_binding:
        if (not isinstance(preprocessing_inputs,dict) or set(preprocessing_inputs)!={'cohort.json','input-inventory.json'}
                or any(not isinstance(raw,bytes) for raw in preprocessing_inputs.values())):
            raise ValueError('EXPERIMENT_PREPROCESSING_INPUT_FILES_REQUIRED')
        files.update(preprocessing_inputs)
        if runtime_binding['preprocessing'].get('schema') == 'reviewed-preprocessing-partitions/v1':
            files['frozen-partitions.json'] = pr.check(original/'frozen-partitions.json').read_bytes()
    elif preprocessing_inputs is not None:raise ValueError('EXPERIMENT_PREPROCESSING_UNSELECTED_INPUTS')
    hashes = {name:digest(raw) for name,raw in files.items()}
    binding = {**runtime_binding, "spec_sha256":hashes["SPEC.md"], "review_sha256":hashes["review.json"],
        "execution_plan_sha256":hashes["execution-plan.json"],
        "code_sha256":digest(canonical({k:v for k,v in hashes.items() if k.endswith(".py")})),
        "execution":{"schema":"reviewed-module/v1", "module":"execution.py",
            "package_manifest_sha256":hashes["reviewed-package.json"], "approval_sha256":hashes["approval.json"],
            "module_sha256":hashes["execution.py"], "worker_sha256":hashes["run.py"],
            "support_sha256":{name:hashes[name] for name in SUPPORT_FILES}}}
    manifest = {"schema":"modal-run/v1", "binding":binding, "files":hashes}
    if manifest_for(binding)!=manifest:raise ValueError('EXPERIMENT_MANIFEST_FILE_BINDING')
    folder = Path(folder)
    if folder.exists() or folder.is_symlink():
        pr.check_tree(folder)
        if inventory(folder) != {**hashes, "manifest.json":digest(canonical(manifest))}:
            raise ValueError("EXPERIMENT_MODAL_EXISTING_PACKAGE_CHANGED")
    else:
        pr.mkdir(folder)
        for name, raw in sorted(files.items()): write_once(folder/name, raw)
        write_once(folder/"manifest.json", canonical(manifest))
    from orchestrator.modal_executor import verify_package
    verify_package(folder, binding)
    return manifest


def base_binding(binding):
    """Recover runtime fields for replay; emit must rederive and compare the seal."""
    return {k:v for k,v in binding.items() if k not in DERIVED_FIELDS}


def replay(driver, value, folder, binding):
    """Authenticate an existing full binding without creating a missing package.

    Recompute every derived field from the original approved package. Merely
    stripping those fields would lose the very evidence we need to verify.
    """
    folder=Path(folder)
    if not folder.is_dir():raise ValueError('EXPERIMENT_REPLAY_PACKAGE_REQUIRED')
    pr.check_tree(folder)
    inputs=None
    if 'preprocessing' in binding:
        inputs={name:pr.check(folder/name).read_bytes() for name in ('cohort.json','input-inventory.json')}
    manifest=emit(driver,value,folder,base_binding(binding),preprocessing_inputs=inputs)
    if manifest['binding']!=binding:raise ValueError('EXPERIMENT_REPLAY_BINDING_CHANGED')
    return manifest
