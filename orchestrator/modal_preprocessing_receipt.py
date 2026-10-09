"""Seal technical preprocessing results using the fit provider's same contract.

The scientific author owns preprocessing code and the reviewed package selects
its input/output contract. This controller adapter does no preprocessing and
makes no scientific acceptance claim. It verifies a successful bound validator
receipt and every resulting file before creating an immutable provider receipt.
"""
import hashlib
import json
from pathlib import Path
from orchestrator import private_records
from orchestrator.modal_executor import canonical
from orchestrator.modal_item4_provider import validate_inputs
from orchestrator.modal_fit_progress import file_hash
from orchestrator.context_budget import relative_file


def check_validation(validation, proposed, cohort_raw, assets, binding, validator_sha256):
    """Same validator/output binding at sealing and root fit provisioning."""
    from orchestrator.modal_preprocessed_contract import validate_validation
    fit=binding['progress']['fit_binding']
    expected={'run_id':binding['run_id'],'spec_sha256':binding['spec_sha256'],
        'preprocessing_code_sha256':assets['preprocessing_code_sha256'],
        'validator_sha256':validator_sha256,'cohort_sha256':hashlib.sha256(cohort_raw).hexdigest(),
        'input_contract_sha256':fit['input_contract_sha256'],'environment_sha256':fit['environment_sha256']}
    files=validate_inputs(proposed,cohort_raw,assets,binding)
    return validate_validation(validation,expected,files)


@private_records.private_umask
def seal(folder, destination, *, proposed, cohort_raw, assets, binding,
         validator_path, validator_sha256, validation_path, validation_sha256):
    """Both code and validation receipt are selected by the reviewed package.

    The validator runs in the admitted worker; callers bind its original receipt
    by hash. A zero exit status or mere existence of output files is insufficient.
    This does not run a validator, launch a job, or accept scientific findings.
    """
    folder = private_records.check(folder)
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise ValueError('ITEM4_EXISTING_PREPROCESSING_RECEIPT')
    validator_path = private_records.check(validator_path)
    validation_path = private_records.check(validation_path)
    raw = validation_path.read_bytes()
    if (file_hash(validator_path)!=validator_sha256 or
            hashlib.sha256(raw).hexdigest()!=validation_sha256):
        raise ValueError('ITEM4_PREPROCESSING_VALIDATOR_BINDING')
    from orchestrator.review_contract import strict_json
    validation = strict_json(raw)
    expected = check_validation(validation, proposed, cohort_raw, assets, binding, validator_sha256)
    private_records.check_tree(folder)
    actual = {str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file()}
    if actual != set(expected):
        raise ValueError('ITEM4_PREPROCESSING_OUTPUT_MEMBER_SET')
    for name,item in expected.items():
        path = private_records.check(relative_file(folder,name))
        if path.stat().st_size!=item['bytes'] or file_hash(path)!=item['sha256']:
            raise ValueError('ITEM4_PREPROCESSING_OUTPUT_CHANGED')
    # A second inventory catches member-set/size drift while streaming hashes.
    after = {str(p.relative_to(folder)):p.stat().st_size for p in folder.rglob('*') if p.is_file()}
    if after != {name:v['bytes'] for name,v in expected.items()}:
        raise ValueError('ITEM4_PREPROCESSING_OUTPUT_CHANGED')
    record = canonical(proposed)
    with private_records.open_file(destination,'xb') as stream:stream.write(record)
    return {'status':'SEALED_TECHNICAL_VALIDATION','path':str(destination),
            'sha256':hashlib.sha256(record).hexdigest(),'files':len(expected),
            'validation_sha256':validation_sha256,'validator_sha256':validator_sha256,
            'scientific_acceptance':False,'execution_performed':False}
