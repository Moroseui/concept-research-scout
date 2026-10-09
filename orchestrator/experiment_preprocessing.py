"""Execute reviewed preprocessing and its validator inside the admitted worker.

This module contains no image processing, cohort choice or scientific rule.
The provider must admit the CPU job and verify its source inventory/environment
before this adapter runs. It preserves the author's original return, verifies
all produced bytes, and publishes no fit checkpoint or scientific acceptance.
"""
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import time
from orchestrator import private_records as pr
from orchestrator.modal_input_guard import verify as verify_files
from orchestrator.modal_preprocessed_contract import validate_preprocessed,validate_validation
from orchestrator.modal_scientific_environment import environment_proof,environment_bytes
from orchestrator.modal_development_inputs import COHORT,SOURCE
from orchestrator.modal_fit_progress import volume_commit as commit, file_hash


def encoded(value):return json.dumps(value,sort_keys=True,allow_nan=False).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()


def write(path,value):
    with pr.open_file(path,'xb') as stream:
        stream.write(encoded(value));stream.flush();os.fsync(stream.fileno())


def write_step(records,name,value):
    # Publish a complete record only. A hard stop during its write preserves
    # the unfinished file outside the committed-step index.
    pending=records.parent/'step-records-pending';pr.mkdir(pending,exist_ok=True)
    temporary=pending/(name+'.json');target=records/(name+'.json')
    write(temporary,value)
    if target.exists() or target.is_symlink():raise ValueError('EXPERIMENT_PREPROCESSING_STEP')
    os.rename(temporary,target)
    descriptor=os.open(records,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(descriptor)
    finally:os.close(descriptor)


def scope(binding,plan,cohort_raw):
    value=binding.get('preprocessing')
    fields={'schema','id','input_contract_sha256','environment_sha256',
            'split_sha256','plans_name','cohort_sha256','source_capture_sha256'}
    schema = value.get("schema") if isinstance(value, dict) else None
    if schema == "reviewed-preprocessing-partitions/v1": fields.add("partitions_sha256")
    if (not isinstance(value,dict) or set(value)!=fields
            or schema not in {"reviewed-preprocessing/v1", "reviewed-preprocessing-partitions/v1"}
            or (schema == "reviewed-preprocessing-partitions/v1" and
                (not isinstance(value["partitions_sha256"], str) or not re.fullmatch("[a-f0-9]{64}", value["partitions_sha256"])))
            or not isinstance(value['id'],str) or not re.fullmatch('[a-zA-Z0-9_-]{1,96}',value['id'])
            or value['cohort_sha256']!=COHORT or sha(cohort_raw)!=COHORT
            or value['source_capture_sha256']!=SOURCE
            or any(not isinstance(value[k],str) or not re.fullmatch('[a-f0-9]{64}',value[k])
                   for k in ('input_contract_sha256','environment_sha256','split_sha256'))
            or not isinstance(value['plans_name'],str) or not re.fullmatch('[a-zA-Z0-9_-]{1,96}',value['plans_name'])):
        raise ValueError('EXPERIMENT_PREPROCESSING_SCOPE')
    selected=plan.get('preprocessing')
    if not isinstance(selected,list) or not selected or any(not isinstance(row,dict) for row in selected):
        raise ValueError('EXPERIMENT_PREPROCESSING_PLAN')
    matches=[row for row in selected if row.get('id')==value['id']]
    if plan.get('schema') == 'scientific-execution-plan/v2':
        from orchestrator.experiment_environment_requirements import runtime_preprocessing
        if len(matches) != 1:
            raise ValueError('EXPERIMENT_PREPROCESSING_PLAN_BINDING')
        resolved = runtime_preprocessing(matches[0], plan, cohort_raw,
                                         binding.get('scientific_environment'))
        if resolved != value:
            raise ValueError('EXPERIMENT_PREPROCESSING_PLAN_BINDING')
    elif matches != [value]:
        raise ValueError('EXPERIMENT_PREPROCESSING_PLAN_BINDING')
    if binding['resources']['gpu'] is not None or binding['experiment']['stage']!='SMOKE':
        raise ValueError('EXPERIMENT_PREPROCESSING_CPU_ONLY')
    return value


@pr.private_umask
def execute(module_path,inputs,progress,binding,plan,*,cohort_raw,input_files,frozen_partitions=None):
    """Called after the parent worker's complete package/hash verification.

    A repeated or interrupted invocation is never a fresh execution. Durable
    completed-step records remain available for explicitly admitted recovery;
    this function itself neither retries nor changes an accounting outcome.
    """
    selected=scope(binding,plan,cohort_raw)
    module_path=pr.check(module_path);inputs=Path(inputs);progress=pr.check(progress)
    partition_contract = None
    if selected["schema"] == "reviewed-preprocessing-partitions/v1":
        expected_path = module_path.parent/"frozen-partitions.json"
        if frozen_partitions is None or Path(frozen_partitions) != expected_path:
            raise ValueError("EXPERIMENT_PARTITIONS_WORKER_PATH")
        raw = pr.check(expected_path).read_bytes()
        if sha(raw) != selected["partitions_sha256"]:
            raise ValueError("EXPERIMENT_PARTITIONS_WORKER_HASH")
        from orchestrator.scientific_view_scan import scan
        scan(raw, frozenset(json.loads(cohort_raw)["cases"]), kind="per_patient",
             reason="Reproduce the reviewed development-only fold membership; no outcomes or clinical fields.")
        partition_contract = {"path":str(expected_path), "sha256":sha(raw)}
    elif frozen_partitions is not None:
        raise ValueError("EXPERIMENT_PARTITIONS_UNSELECTED")
    pin=binding['execution']['module_sha256']
    if sha(module_path.read_bytes())!=pin:raise ValueError('EXPERIMENT_PREPROCESSING_CODE_CHANGED')
    if sha(encoded(input_files))!=selected['input_contract_sha256']:
        raise ValueError('EXPERIMENT_PREPROCESSING_INPUT_BINDING')
    # Hash source bytes before any scientific module import. Only the existing
    # provider-selected, read-only source view is supplied as inputs.
    verify_files(inputs,input_files)
    ident=sha(encoded(binding))
    proof_path=pr.check(progress/'environment-verification'/ident/'environment.json')
    observed=environment_proof(proof_path.read_bytes(),binding)
    if sha(environment_bytes(observed['actual']))!=selected['environment_sha256']:
        raise ValueError('EXPERIMENT_PREPROCESSING_ENVIRONMENT_CHANGED')
    attempt=progress/'preprocessing'/ident
    pr.mkdir(attempt.parent,exist_ok=True);pr.mkdir(attempt)
    artifacts=attempt/'artifacts';pr.mkdir(artifacts)
    records=attempt/'steps';pr.mkdir(records)
    write(attempt/'binding.json',binding)
    started=time.time();write(attempt/'started.json',{'binding_sha256':ident,'at':started})
    commit(progress)
    completed={}
    def checkpoint(name,files):
        if (not isinstance(name,str) or not re.fullmatch('[a-zA-Z0-9_-]{1,96}',name)
                or name in completed or not isinstance(files,dict) or not files):
            raise ValueError('EXPERIMENT_PREPROCESSING_STEP')
        # Each completed step owns new output paths. Scientific code supplies
        # the exact file hashes/sizes; the wrapper independently checks bytes.
        if set(files)&{p for row in completed.values() for p in row}:
            raise ValueError('EXPERIMENT_PREPROCESSING_STEP_OVERLAP')
        from orchestrator.modal_input_guard import validate_inventory
        validate_inventory(files);pr.check_tree(artifacts)
        for path,item in files.items():
            target=pr.check(artifacts/path)
            if not target.is_file() or target.stat().st_size!=item['bytes']:
                raise ValueError('EXPERIMENT_PREPROCESSING_STEP_CHANGED')
            if file_hash(target)!=item['sha256']:raise ValueError('EXPERIMENT_PREPROCESSING_STEP_CHANGED')
            with target.open('rb') as stream:os.fsync(stream.fileno())
        write_step(records,name,{'binding_sha256':ident,'step':name,'files':files})
        commit(progress);completed[name]=json.loads(encoded(files))
    contract={'execution_plan':plan,'runtime':binding,'cohort':json.loads(cohort_raw),
              'preprocessing':selected,'checkpoint':checkpoint}
    if partition_contract is not None: contract['frozen_partitions'] = partition_contract
    try:
        from orchestrator.preprocessing_checkpoints import restore
        inherited,snapshot=restore(progress,artifacts,binding)
        for name,files in inherited.items():
            write_step(records,name,{'binding_sha256':ident,'step':name,'files':files})
        completed.update(inherited)
        contract['completed_steps']=json.loads(encoded(completed))
        if snapshot is not None:
            write(attempt/'inherited.json',{'resume':binding['resume'],'snapshot':snapshot})
            commit(progress)
        with pr.open_file(attempt/'console.log','x') as console:
            with contextlib.redirect_stdout(console),contextlib.redirect_stderr(console):
                loaded=importlib.util.spec_from_file_location('reviewed_preprocessing',module_path)
                module=importlib.util.module_from_spec(loaded);loaded.loader.exec_module(module)
                module.preprocess(inputs,artifacts,contract)
                returned=module.validate_preprocessing(artifacts,contract)
        # Preserve returned evidence before qualification; never reconstruct a
        # passing scientific receipt from a zero process exit status.
        write(attempt/'author-validation.json',returned)
        if not isinstance(returned,dict) or set(returned)!={'proposed','validation'}:
            raise ValueError('EXPERIMENT_PREPROCESSING_RETURN')
        assets={'preprocessing_code_sha256':pin,'plans_name':selected['plans_name'],
                'split_sha256':selected['split_sha256']}
        files=validate_preprocessed(returned['proposed'],cohort_raw,assets,
            {k:selected[k] for k in ('input_contract_sha256','environment_sha256')},
            cohort_sha256=COHORT,source_sha256=SOURCE)
        expected={'run_id':binding['run_id'],'spec_sha256':binding['spec_sha256'],
            'preprocessing_code_sha256':pin,'validator_sha256':pin,'cohort_sha256':COHORT,
            'input_contract_sha256':selected['input_contract_sha256'],
            'environment_sha256':selected['environment_sha256']}
        validate_validation(returned['validation'],expected,files)
        pr.check_tree(artifacts);verify_files(artifacts,files)
        covered={p:item for group in completed.values() for p,item in group.items()}
        if covered!=files:raise ValueError('EXPERIMENT_PREPROCESSING_UNCOMMITTED_OUTPUTS')
        write(attempt/'preprocessing.json',returned['proposed'])
        write(attempt/'validation.json',returned['validation'])
        receipt={'schema':'experiment-preprocessing-result/v1','status':'VALIDATED',
            'binding_sha256':ident,'preprocessing_sha256':sha(encoded(returned['proposed'])),
            'validation_sha256':sha(encoded(returned['validation'])),
            'files':len(files),'bytes':sum(row['bytes'] for row in files.values()),
            'steps':len(completed),'elapsed_seconds':time.time()-started,
            'scientifically_accepted':False,'fit_completed':False}
        write(attempt/'result.json',receipt);commit(progress)
        return receipt
    except BaseException as error:
        write(attempt/'failed.json',{'status':'FAILED','binding_sha256':ident,
            'error_type':type(error).__name__,'completed_steps':len(completed),
            'elapsed_seconds':time.time()-started,'may_retry':False})
        commit(progress);raise
