"""Exact private development-image contract for the approved item4 Volume.

Metadata verification only. This module does not upload, discover patients,
read scan stores, create provider resources or authorize a training job.
"""
import hashlib
import json
import re
from orchestrator.review_contract import strict_json


def canonical(value):
    return json.dumps(value,sort_keys=True).encode()

AUTHORITY = '3ff8dfa8073158512e4098aa329c070e3272abe5053bf3274adaeb5abd30ecd9'
COHORT = '45c5746f60e2275383a2c4f4096295fe7a171da85a73737c5a35a8cc6fc9fe86'
SOURCE = 'b252b308815e983df2d9d86975a6d590e20d2600ea2f118696263797e8509f5c'
COUNT = 99
KINDS = ('ncct','cta','cbf','cbv','mtt','tmax','brain','lesion')
MAX_FILE = 1024**3
MAX_TOTAL = 8*1024**3


def expected_paths(cases):
    if (not isinstance(cases,list) or len(cases)!=COUNT
            or any(not isinstance(c,str) or not re.fullmatch(r'sub-stroke[0-9]{4}',c) for c in cases)
            or len(set(cases))!=COUNT):
        raise ValueError('ITEM4_DEVELOPMENT_COHORT_REQUIRED')
    files={}
    for case in cases:
        files[f'train/raw_data/{case}/ses-01/{case}_ses-01_ncct.nii.gz']=(case,'ncct')
        files[f'train/derivatives/{case}/ses-01/{case}_ses-01_space-ncct_cta.nii.gz']=(case,'cta')
        for kind in ('cbf','cbv','mtt','tmax'):
            files[f'train/derivatives/{case}/ses-01/perfusion-maps/{case}_ses-01_space-ncct_{kind}.nii.gz']=(case,kind)
        files[f'brainmask/{case}_brainmask.nii.gz']=(case,'brain')
        files[f'train/derivatives/{case}/ses-02/{case}_ses-02_space-ncct_lesion-msk.nii.gz']=(case,'lesion')
    return files


def validate_inventory(cases, files):
    """Validate the entire member set; no intensity-derived coverage claims."""
    expected=expected_paths(cases)
    if not isinstance(files,dict) or set(files)!=set(expected):
        raise ValueError('ITEM4_DEVELOPMENT_MEMBER_SET')
    for name,item in files.items():
        if (not isinstance(item,dict) or set(item)!={'sha256','bytes'} or
                not isinstance(item['sha256'],str) or not re.fullmatch('[a-f0-9]{64}',item['sha256']) or
                type(item['bytes']) is not int or not 0<item['bytes']<=MAX_FILE):
            raise ValueError('ITEM4_DEVELOPMENT_FILE_IDENTITY')
    total=sum(item['bytes'] for item in files.values())
    if total>MAX_TOTAL:raise ValueError('ITEM4_DEVELOPMENT_TOTAL_BYTES')
    return {'files':len(files),'development_count':COUNT,'bytes':total,
            'by_kind':{kind:COUNT for kind in KINDS},'inventory_sha256':hashlib.sha256(canonical(files)).hexdigest()}


def frozen_inventory(cohort_raw,source_raw,authority_raw):
    for raw,pin in [(cohort_raw,COHORT),(source_raw,SOURCE),(authority_raw,AUTHORITY)]:
        if not isinstance(raw,bytes) or hashlib.sha256(raw).hexdigest()!=pin:
            raise ValueError('ITEM4_DEVELOPMENT_AUTHENTICATED_SOURCE')
    cohort=strict_json(cohort_raw);source=strict_json(source_raw)
    if (cohort.get('count')!=COUNT or source.get('cohort_sha256')!=COHORT or
            source.get('originals_changed') is not False or source.get('uploaded_files')!=0 or
            source.get('status')!='SOURCE_HASHED_NOT_UPLOADED'):
        raise ValueError('ITEM4_DEVELOPMENT_CAPTURE_SCOPE')
    # The frozen source producer includes kind/path/time provenance. Validate
    # these records before deriving the provider reader's bytes/hash projection.
    expected=expected_paths(cohort['cases']);files={}
    if not isinstance(source.get('files'),dict) or set(source['files'])!=set(expected):
        raise ValueError('ITEM4_DEVELOPMENT_MEMBER_SET')
    for name,item in source['files'].items():
        if (not isinstance(item,dict) or set(item)!={'bytes','kind','modified_utc','relative_path','sha256'}
                or item['relative_path']!=name or item['kind']!=expected[name][1]
                or not isinstance(item['modified_utc'],str) or not item['modified_utc']):
            raise ValueError('ITEM4_DEVELOPMENT_CAPTURE_RECORD')
        files[name]={key:item[key] for key in ('sha256','bytes')}
    summary=validate_inventory(cohort['cases'],files)
    if source['file_count']!=summary['files'] or source['bytes']!=summary['bytes']:
        raise ValueError('ITEM4_DEVELOPMENT_CAPTURE_TOTAL')
    return {'schema':'modal-development-inputs/v1','authority_sha256':AUTHORITY,
            'cohort_sha256':COHORT,'source_capture_sha256':SOURCE,'files':files,
            'summary':summary,'scope':'DEVELOPMENT_99_ONLY_PRIVATE_MODAL_VOLUME'}


def verify_volume(provider,volume_id,cohort_raw,source_raw,authority_raw):
    """Verify existing private Volume bytes through the existing authenticated reader.

    No creation or upload is performed. Re-read the member set after streaming
    hashes, so unrelated files or size changes cannot hide in the observation.
    """
    contract=frozen_inventory(cohort_raw,source_raw,authority_raw)
    volume=provider._verify_volume(volume_id,contract['files'])
    entries=volume.listdir('/',recursive=True)
    if (sum(x.type.name=='FILE' for x in entries)!=len(contract['files']) or
            any(x.type.name not in {'FILE','DIRECTORY'} for x in entries) or
            {x.path.lstrip('/'):x.size for x in entries if x.type.name=='FILE'}!=
            {name:item['bytes'] for name,item in contract['files'].items()}):
        raise ValueError('ITEM4_DEVELOPMENT_VOLUME_CHANGED')
    return {'status':'VERIFIED','volume_id':volume_id,'contract_sha256':hashlib.sha256(canonical(contract)).hexdigest(),
            **contract['summary'],'uploaded_by_this_check':0,
            'scope':'private development imaging and labels; no public or scientific-model delivery'}
