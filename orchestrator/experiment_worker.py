"""Generic, stdlib-only invocation of an already reviewed scientific module.

No methods, patient selection, metrics or training decisions live here. The
provider's input guard runs first. Completion means program execution only;
validation, scientific interpretation and acceptance remain downstream gates.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import time
import tempfile

SUPPORT_FILES = (
    'orchestrator/__init__.py', 'orchestrator/private_records.py',
    'orchestrator/modal_files.py', 'orchestrator/modal_fit_progress.py',
    'orchestrator/modal_fit_contract.py', 'orchestrator/modal_fit_publication.py',
    'orchestrator/modal_nnunet.py', 'orchestrator/experiment_result.py',
    'orchestrator/scientific_view_scan.py', 'orchestrator/privacy_patterns.py',
    'orchestrator/experiment_preprocessing.py', "orchestrator/preprocessing_checkpoints.py", 'orchestrator/modal_preprocessed_contract.py',
    'orchestrator/modal_input_guard.py', 'orchestrator/modal_scientific_environment.py',
    'orchestrator/experiment_environment_requirements.py',
    'orchestrator/modal_development_inputs.py', 'orchestrator/review_contract.py',
)


def encoded(value):
    return json.dumps(value, sort_keys=True, allow_nan=False).encode()


def sha(raw): return hashlib.sha256(raw).hexdigest()


def read_regular(path):
    path = Path(path)
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError("EXPERIMENT_WORKER_ALIAS")
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("EXPERIMENT_WORKER_FILE_TYPE")
        return stream.read()


def save(path, value):
    with Path(path).open("xb") as stream:
        stream.write(encoded(value)); stream.flush(); os.fsync(stream.fileno())


@contextlib.contextmanager
def private_preprocessing_files(package, pins, *, partitions):
    """Copy only pinned invocation files; provider mount modes are not private.

    The worker verifies complete package membership and hashes before entry.
    Source mounts stay untouched. Each copy is exclusive, private, independently
    rehashed and temporary; the preprocessing adapter retains all its checks.
    """
    names = ['execution.py'] + (['frozen-partitions.json'] if partitions else [])
    with tempfile.TemporaryDirectory(prefix='reviewed-preprocessing-') as directory:
        private = Path(directory)
        if private.is_symlink() or stat.S_IMODE(private.stat().st_mode) != 0o700:
            raise ValueError('EXPERIMENT_PRIVATE_PACKAGE_MODE')
        for name in names:
            raw = read_regular(Path(package)/name)
            if sha(raw) != pins.get(name):
                raise ValueError('EXPERIMENT_PRIVATE_PACKAGE_HASH')
            target = private/name
            descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            if sha(read_regular(target)) != pins[name]:
                raise ValueError('EXPERIMENT_PRIVATE_PACKAGE_HASH')
        yield private


def execute(package, inputs, progress, binding_sha256, *, execution_manifest=None):
    os.umask(0o077)
    package, inputs, progress = map(Path, (package, inputs, progress))
    manifest = json.loads(read_regular(package/"manifest.json")) if execution_manifest is None else execution_manifest
    if (not isinstance(manifest,dict) or set(manifest)!={'schema','binding','files'}
            or execution_manifest is not None and (package/'manifest.json').exists()):
        raise ValueError('EXPERIMENT_WORKER_MANIFEST_TRANSPORT')
    binding = manifest["binding"]
    if sha(encoded(binding)) != binding_sha256:
        raise ValueError("EXPERIMENT_WORKER_BINDING")
    # Compare the exact complete package inventory before importing any module.
    actual = {}
    for p in package.rglob("*"):
        if p.is_symlink(): raise ValueError("EXPERIMENT_WORKER_ALIAS")
        if p.is_file() and p.relative_to(package).as_posix() != "manifest.json":
            actual[p.relative_to(package).as_posix()] = sha(read_regular(p))
    if actual != manifest["files"]:
        raise ValueError("EXPERIMENT_WORKER_PACKAGE_CHANGED")
    execution = binding["execution"]
    if (manifest["schema"] != "modal-run/v1" or execution["schema"] != "reviewed-module/v1"
            or execution["module"] != "execution.py" or binding["purpose"] != "M4_ITEM4"):
        raise ValueError("EXPERIMENT_WORKER_SCOPE")
    for name, key in [("SPEC.md", "spec_sha256"), ("review.json", "review_sha256"),
                      ("execution-plan.json", "execution_plan_sha256")]:
        if actual.get(name) != binding[key]: raise ValueError("EXPERIMENT_WORKER_EVIDENCE_CHANGED")
    code = {k:v for k,v in actual.items() if k.endswith(".py")}
    if (set(code) != {"run.py", "execution.py", *SUPPORT_FILES} or sha(encoded(code)) != binding["code_sha256"]
            or actual["execution.py"] != execution["module_sha256"]
            or actual["run.py"] != execution["worker_sha256"]
            or actual.get('approval.json')!=execution['approval_sha256']
            or actual.get('reviewed-package.json')!=execution['package_manifest_sha256']
            or execution.get("support_sha256") != {name:actual[name] for name in SUPPORT_FILES}):
        raise ValueError("EXPERIMENT_WORKER_CODE_BINDING")
    plan = json.loads(read_regular(package/"execution-plan.json"))
    # Only these exact release-bound support modules enter the package. No
    # controller, provider SDK, billing or credentials are imported in the worker.
    import sys
    sys.path.insert(0, str(package))
    from orchestrator.modal_fit_contract import progress_scope
    from orchestrator.modal_fit_progress import FitProgress
    from orchestrator.modal_fit_publication import publish
    from orchestrator.experiment_result import selected, validate
    if 'preprocessing' in binding:
        from orchestrator.experiment_preprocessing import execute as preprocess
        if (actual.get('cohort.json')!=binding['preprocessing']['cohort_sha256']
                or actual.get('input-inventory.json')!=binding['preprocessing']['input_contract_sha256']):
            raise ValueError('EXPERIMENT_PREPROCESSING_INPUT_BINDING')
        if binding['preprocessing'].get('schema') == 'reviewed-preprocessing-partitions/v1':
            if actual.get('frozen-partitions.json') != binding['preprocessing'].get('partitions_sha256'):
                raise ValueError('EXPERIMENT_PARTITIONS_WORKER_HASH')
        elif 'frozen-partitions.json' in actual:
            raise ValueError('EXPERIMENT_PARTITIONS_UNSELECTED')
        partitions = binding['preprocessing'].get('schema') == 'reviewed-preprocessing-partitions/v1'
        with private_preprocessing_files(package, actual, partitions=partitions) as private:
            return preprocess(private/execution['module'],inputs,progress,binding,plan,
                cohort_raw=read_regular(package/'cohort.json'),
                input_files=json.loads(read_regular(package/'input-inventory.json')),
                frozen_partitions=private/'frozen-partitions.json' if partitions else None)
    selected(plan, binding)  # Refuse a missing reviewed result contract before execution.
    scope = progress_scope(binding)
    segment = binding['experiment']['segment']
    if type(segment) is not int or segment < 1:
        raise ValueError("EXPERIMENT_WORKER_SEGMENT")
    fit = FitProgress(progress, scope['fit_id'], scope['fit_binding'])
    # The model owns methods and checkpoints. Infrastructure provides the
    # already-locked durable writer and publishes only validated declared files.
    contract = {"execution_plan":plan, "runtime":binding, "progress":fit}
    output = progress/"executions"/binding_sha256
    if any(p.is_symlink() for p in [progress, *progress.parents]):
        raise ValueError("EXPERIMENT_WORKER_ALIAS")
    if not progress.is_dir() or progress.stat().st_mode & 0o077:
        raise ValueError("EXPERIMENT_WORKER_OUTPUT_PERMISSIONS")
    output.parent.mkdir(mode=0o700, exist_ok=True)
    if output.parent.is_symlink() or output.parent.stat().st_mode & 0o077:
        raise ValueError("EXPERIMENT_WORKER_OUTPUT_PERMISSIONS")
    output.mkdir(mode=0o700)  # An existing attempt never executes again.
    start = time.time()
    save(output/"started.json", {"binding_sha256":binding_sha256, "at":start})
    module_path = package/execution["module"]
    outcome = {"schema":"experiment-program-execution/v1", "binding_sha256":binding_sha256,
               "code_sha256":actual[execution["module"]], "scientifically_validated":False}
    artifacts = output/'artifacts'
    artifacts.mkdir(mode=0o700)
    with fit.writer(initial=segment == 1):
        try:
            if segment > 1:
                # The terminal controller proof selected this exact committed
                # checkpoint. Refuse drift before importing scientific code.
                from orchestrator.modal_fit_progress import encoded as progress_encoded
                resume=binding.get('resume')
                key='final' if (fit.root/'final.json').exists() else 'latest'
                _,checkpoint=fit.select(key)
                if (not isinstance(resume,dict) or set(resume)!={
                        'previous_segment_id','terminal_receipt_sha256','checkpoint_record_sha256'}
                        or resume['checkpoint_record_sha256']!=sha(progress_encoded(checkpoint))):
                    raise ValueError('EXPERIMENT_WORKER_RESUME_CHECKPOINT_CHANGED')
            with (output/"console.log").open("x") as console:
                with contextlib.redirect_stdout(console), contextlib.redirect_stderr(console):
                    spec = importlib.util.spec_from_file_location("reviewed_experiment", module_path)
                    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
                    module.main(inputs, artifacts, contract)
            # The existing publisher requires the bound complete native final
            # checkpoint and exact outputs. Returning from main alone is not
            # sufficient. Scientific validation and acceptance remain downstream.
            validation = validate(artifacts, binding, plan)
            save(output/'validation-receipt.json', validation)
            published = publish(fit, binding, artifacts)
            outcome.update(status="EXECUTED", elapsed_seconds=time.time()-start,
                           result_sha256=sha(encoded(published)), validation_sha256=sha(encoded(validation)))
        except BaseException as error:
            outcome.update(status="FAILED", error_type=type(error).__name__, elapsed_seconds=time.time()-start)
            save(output/"execution.json", outcome)
            os.sync()
            publish(fit, binding, None, status='FAILED')
            raise
    save(output/"execution.json", outcome)
    os.sync()
    return outcome


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--binding", required=True)
    parser.add_argument('--input-root',required=True)
    parser.add_argument('--progress-root',required=True)
    parser.add_argument('--manifest-json')
    args = parser.parse_args()
    package=Path(__file__).parent
    manifest=json.loads(args.manifest_json) if args.manifest_json is not None else json.loads(read_regular(package/'manifest.json'))
    binding=manifest['binding']
    roots={'package':package,'inputs':Path(args.input_root),'progress':Path(args.progress_root)}
    ids={'package':binding['package_volume_id'],
         'inputs':binding['source_volume_id'] if 'preprocessing' in binding else binding['preprocessed_volume_id'],
         'progress':binding['preprocessing_output_volume_id'] if 'preprocessing' in binding else binding['progress']['volume_id']}
    import re
    if (any(not isinstance(v,str) or not re.fullmatch('vo-[A-Za-z0-9]{1,80}',v) for v in ids.values()) or len(set(ids.values()))!=3
            or any(path!=Path('/__modal/volumes')/ids[role] for role,path in roots.items())):
        raise ValueError('EXPERIMENT_WORKER_VOLUME_BINDING')
    execute(package,roots['inputs'],roots['progress'],args.binding,
            execution_manifest=manifest if args.manifest_json is not None else None)
