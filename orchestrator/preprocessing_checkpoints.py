"""Committed preprocessing steps, never a training checkpoint or retry grant.

The controller admits a linked segment only from positive terminal evidence.
This worker-side reader rechecks that link and every reused byte inside the
existing private output Volume before scientific code can resume.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
from orchestrator import private_records as pr
from orchestrator.modal_input_guard import validate_inventory
from orchestrator.modal_fit_progress import file_hash
from orchestrator.review_contract import strict_json


def encoded(value):return json.dumps(value,sort_keys=True,allow_nan=False).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def hash_value(value):return sha(encoded(value))


def resume(binding):
    segment=binding['experiment'].get('segment',1);value=binding.get('resume')
    if type(segment) is not int or segment<1:raise ValueError('PREPROCESSING_RESUME_SEGMENT')
    if segment==1:
        if value is not None:raise ValueError('PREPROCESSING_INITIAL_RESUME_REFUSED')
        return None
    if (not isinstance(value,dict) or set(value)!={'previous_segment_id','terminal_receipt_sha256','steps_record_sha256'}
            or any(not isinstance(v,str) or not re.fullmatch('[a-f0-9]{64}',v) for v in value.values())):
        raise ValueError('PREPROCESSING_RESUME_BINDING')
    return value


def same_execution(previous,current):
    if current['experiment']['segment']!=previous['experiment']['segment']+1:
        raise ValueError('PREPROCESSING_RESUME_SEGMENT')
    def identity(binding):
        value=copy.deepcopy(binding);value.pop('resume',None);value['experiment'].pop('segment',None)
        return value
    if identity(previous)!=identity(current):raise ValueError('PREPROCESSING_RESUME_IDENTITY_CHANGED')


def snapshot(binding_sha256,records):
    """Shared provider/worker canonical projection of original step records."""
    if not re.fullmatch('[a-f0-9]{64}',binding_sha256) or not isinstance(records,dict) or not records:
        raise ValueError('PREPROCESSING_COMMITTED_STEPS_REQUIRED')
    steps={};files={}
    for name,raw in sorted(records.items()):
        if not isinstance(name,str) or not re.fullmatch('[a-zA-Z0-9_-]{1,96}',name):
            raise ValueError('PREPROCESSING_STEP_NAME')
        value=strict_json(raw)
        if (not isinstance(value,dict) or set(value)!={'binding_sha256','step','files'}
                or value['binding_sha256']!=binding_sha256 or value['step']!=name
                or not isinstance(value['files'],dict) or not value['files']):
            raise ValueError('PREPROCESSING_STEP_BINDING')
        validate_inventory(value['files'])
        if set(files)&set(value['files']):raise ValueError('PREPROCESSING_STEP_OVERLAP')
        files.update(value['files']);steps[name]={'record_sha256':sha(raw),'files':value['files']}
    return {'schema':'preprocessing-steps/v1','binding_sha256':binding_sha256,'steps':steps}


def local_snapshot(attempt,ident):
    attempt=pr.check(attempt);pr.check_tree(attempt/'steps')
    paths=list((attempt/'steps').iterdir())
    if any(not p.is_file() or p.suffix!='.json' for p in paths):raise ValueError('PREPROCESSING_STEP_MEMBERS')
    return snapshot(ident,{p.stem:p.read_bytes() for p in paths})


def restore(progress,artifacts,binding):
    link=resume(binding)
    if link is None:return {},None
    previous=pr.check(Path(progress)/'preprocessing'/link['previous_segment_id'])
    raw=pr.check(previous/'binding.json').read_bytes()
    if sha(raw)!=link['previous_segment_id']:raise ValueError('PREPROCESSING_PREDECESSOR_CHANGED')
    old=strict_json(raw);same_execution(old,binding)
    if (previous/'result.json').exists() or (previous/'author-validation.json').exists() or (previous/'failed.json').exists():
        raise ValueError('PREPROCESSING_PREDECESSOR_NOT_INTERRUPTED')
    snap=local_snapshot(previous,link['previous_segment_id'])
    if hash_value(snap)!=link['steps_record_sha256']:raise ValueError('PREPROCESSING_STEPS_CHANGED')
    # Copy only committed bytes to a fresh attempt. Never hardlink writable
    # files to the preserved predecessor or change its modes/ownership.
    completed={}
    for step,row in snap['steps'].items():
        for name,item in row['files'].items():
            source=pr.check(previous/'artifacts'/name)
            if not source.is_file() or source.stat().st_size!=item['bytes'] or file_hash(source)!=item['sha256']:
                raise ValueError('PREPROCESSING_COMMITTED_BYTES_CHANGED')
            target=Path(artifacts)/name;pr.mkdir(target.parent,parents=True,exist_ok=True)
            with source.open('rb') as reader,pr.open_file(target,'xb') as writer:
                while True:
                    block=reader.read(1024*1024)
                    if not block:break
                    writer.write(block)
                writer.flush();os.fsync(writer.fileno())
            if file_hash(target)!=item['sha256'] or file_hash(source)!=item['sha256']:
                raise ValueError('PREPROCESSING_COMMITTED_BYTES_CHANGED')
        completed[step]=copy.deepcopy(row['files'])
    if local_snapshot(previous,link['previous_segment_id'])!=snap:
        raise ValueError('PREPROCESSING_STEPS_CHANGED')
    return completed,snap
