"""Credential-free request artifact and read-only wait for shared admission.

The hosted protected collector, not this Actions job, writes the ledger. A halt
does not revoke an already admitted attempt. No timeout or missing Git object is
permission to run. This helper is prepared for reviewed workflow integration;
it does not activate the inactive standing policy or replace existing controls.
"""
import hashlib
import json
import re
import time
from pathlib import Path

from orchestrator.dispatch_limiter import validate
from orchestrator.git_publication import scan
from orchestrator.operations_report import immutable


def identity(record):
    if (not isinstance(record,dict) or set(record)!={
            'repository_id','run_id','attempt','source','branch','workflow_sha256'}
            or record['repository_id']!=1323461276
            or record['branch'] not in ('main','astra/autonomous-isles-pilot')
            or not all(isinstance(record[k],str) and re.fullmatch(pattern,record[k])
                       for k,pattern in [('run_id','[1-9][0-9]*'),('attempt','[1-9][0-9]*'),
                                         ('source','[0-9a-f]{40}'),('workflow_sha256','[0-9a-f]{64}')])):
        raise ValueError('ACTIONS_REQUEST_IDENTITY')
    return record


def prepare(record,output):
    record=identity(record)
    raw=(json.dumps(record,sort_keys=True)+'\n').encode()
    scan('admission.json',raw)
    output=Path(output)
    if output.exists() or output.is_symlink():raise ValueError('FRESH_ADMISSION_OUTPUT_REQUIRED')
    output.mkdir(mode=0o700)
    immutable(output/'admission.json',raw)
    return {'artifact_name':'research-admission-'+record['run_id']+'-'+record['attempt'],
            'sha256':hashlib.sha256(raw).hexdigest(),'status':'REQUESTED_NOT_ADMITTED'}


def observe(record,state,expected_policy_sha256):
    identity(record);validate(state)
    if not re.fullmatch('[0-9a-f]{64}',expected_policy_sha256):raise ValueError('APPROVED_POLICY_PIN_REQUIRED')
    if state['policy_sha256']!=expected_policy_sha256:
        raise ValueError('SHARED_POLICY_BINDING_CHANGED')
    event=state['events'].get(record['run_id']+':'+record['attempt'])
    if event:
        if any(event[k]!=record[k] for k in ('source','branch')):
            raise ValueError('SHARED_ADMISSION_BINDING_CHANGED')
        return {'status':'ADMITTED','count':event['count'],'day':event['day']}
    return {'status':'HALTED_OPERATOR_RESET_REQUIRED' if state['halted'] else 'WAITING_ADMISSION'}


def wait(record,read,expected_policy_sha256,*,timeout=600,interval=30,clock=time.monotonic,sleep=time.sleep):
    identity(record)
    if not 0<timeout<=600 or not 1<=interval<=30:raise ValueError('BOUNDED_ADMISSION_WAIT_REQUIRED')
    deadline=clock()+timeout
    while True:
        # read is the existing read-only Git ledger route. Authentication and
        # provenance errors stop immediately; they never become an admission.
        pin,state=read()
        outcome=observe(record,state,expected_policy_sha256)
        if outcome['status']!='WAITING_ADMISSION':return {**outcome,'state_pin':pin}
        remaining=deadline-clock()
        if remaining<=0:return {'status':'BLOCKED','reason':'ADMISSION_WAIT_TIMEOUT'}
        sleep(min(interval,remaining))
