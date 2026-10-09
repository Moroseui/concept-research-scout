"""Worker-safe preprocessing receipt contract; no SDK, ledger or model code.

The fit consumer always supplies its pinned plans hash. The preprocessing
producer has not produced those plan bytes yet: it binds the observed plans
hash to the actual output file, then the controller freezes that hash for fits.
Both consumers use these same cohort, member and hash checks.
"""
import hashlib
import json
import re
from pathlib import Path
from orchestrator.modal_files import safe_name


def _hash(value):
    return isinstance(value,str) and re.fullmatch('[a-f0-9]{64}',value)


def validate_preprocessed(receipt, cohort, scope, expected, *, cohort_sha256, source_sha256):
    required = {'schema','status','cohort_sha256','source_capture_sha256',
                'input_contract_sha256','environment_sha256','plans_sha256',
                'preprocessing_code_sha256','case_files','shared_files'}
    if (not isinstance(receipt,dict) or set(receipt)!=required or
            receipt['schema']!='modal-item4-preprocessed/v1' or receipt['status']!='VALIDATED' or
            receipt['cohort_sha256']!=cohort_sha256 or receipt['source_capture_sha256']!=source_sha256):
        raise ValueError('ITEM4_PREPROCESSING_SCOPE')
    if hashlib.sha256(cohort).hexdigest()!=cohort_sha256:
        raise ValueError('ITEM4_PREPROCESSING_COHORT_CHANGED')
    cases = json.loads(cohort)['cases']
    if len(cases)!=99 or len(set(cases))!=99 or set(receipt['case_files'])!=set(cases):
        raise ValueError('ITEM4_PREPROCESSING_CASE_SET')
    if set(expected) not in ({'input_contract_sha256','environment_sha256'},
            {'input_contract_sha256','environment_sha256','plans_sha256'}):
        raise ValueError('ITEM4_PREPROCESSING_EXPECTATIONS')
    for key in expected:
        if not _hash(receipt[key]) or receipt[key]!=expected[key]:
            raise ValueError('ITEM4_PREPROCESSING_FIT_BINDING')
    if (not _hash(receipt['preprocessing_code_sha256']) or
            receipt['preprocessing_code_sha256']!=scope['preprocessing_code_sha256']):
        raise ValueError('ITEM4_PREPROCESSING_CODE_BINDING')
    files = {}
    for case, members in receipt['case_files'].items():
        if not isinstance(members,dict) or set(members)!={'image','segmentation','properties'}:
            raise ValueError('ITEM4_PREPROCESSING_CASE_MEMBERS')
        for role, item in members.items():
            if not isinstance(item,dict) or set(item)!={'path','sha256','bytes'}:
                raise ValueError('ITEM4_PREPROCESSING_FILE')
            name = safe_name(item['path']); base = Path(name).name
            extensions = {'image':(case+'.b2nd',case+'.npy',case+'.npz'),
                          'segmentation':(case+'_seg.b2nd',case+'_seg.npy',case+'_seg.npz'),
                          'properties':(case+'.pkl',)}
            if base not in extensions[role] or name in files:
                raise ValueError('ITEM4_PREPROCESSING_CASE_PATH')
            files[name] = {key:item[key] for key in ('sha256','bytes')}
    shared = receipt['shared_files']
    if (not isinstance(shared,dict) or set(shared)!={'dataset','plans','splits'}):
        raise ValueError('ITEM4_PREPROCESSING_SHARED_MEMBERS')
    for kind,item in shared.items():
        if not isinstance(item,dict) or set(item)!={'path','sha256','bytes'}:
            raise ValueError('ITEM4_PREPROCESSING_FILE')
        name = safe_name(item['path'])
        expected = {'dataset':'dataset.json','plans':scope['plans_name']+'.json','splits':'splits_final.json'}
        if Path(name).name!=expected[kind] or name in files:
            raise ValueError('ITEM4_PREPROCESSING_SHARED_PATH')
        files[name]={key:item[key] for key in ('sha256','bytes')}
    if shared['plans']['sha256']!=receipt['plans_sha256'] or shared['splits']['sha256']!=scope['split_sha256']:
        raise ValueError('ITEM4_PREPROCESSING_PLAN_OR_SPLIT')
    if any(set(v)!={'sha256','bytes'} or not _hash(v['sha256']) or
           type(v['bytes']) is not int or not 0<v['bytes']<=8*1024**3 for v in files.values()):
        raise ValueError('ITEM4_PREPROCESSING_FILE')
    if sum(v['bytes'] for v in files.values())>128*1024**3:
        raise ValueError('ITEM4_PREPROCESSING_TOTAL')
    return files



def validate_validation(value, expected, files):
    """The original author-written validation receipt, not a reconstructed pass."""
    identities={'run_id','spec_sha256','preprocessing_code_sha256','validator_sha256',
                'cohort_sha256','input_contract_sha256','environment_sha256'}
    if set(expected)!=identities:
        raise ValueError('ITEM4_PREPROCESSING_VALIDATOR_EXPECTATIONS')
    if (not isinstance(value,dict) or set(value)!=identities|{'schema','status','files','errors'}
            or value['schema']!='modal-preprocessing-validation/v1'
            or value['status']!='PASS' or value['errors']!=[]):
        raise ValueError('ITEM4_PREPROCESSING_VALIDATOR_REFUSED')
    if any(value[key]!=content for key,content in expected.items()):
        raise ValueError('ITEM4_PREPROCESSING_VALIDATOR_SCOPE')
    if value['files']!=files:
        raise ValueError('ITEM4_PREPROCESSING_VALIDATOR_OUTPUTS')
    return files
