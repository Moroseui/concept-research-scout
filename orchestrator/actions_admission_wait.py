"""Credential-free request artifact and read-only wait for shared admission.

The hosted protected collector, not this Actions job, writes the ledger. A halt
does not revoke an already admitted attempt. No timeout or missing Git object is
permission to run. This helper is prepared for reviewed workflow integration;
it does not activate the inactive standing policy or replace existing controls.
"""
import hashlib
import argparse
import os
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


def workflow_prepare(config,environment,repository,output):
    """Preserve existing manual controls while the proposed policy is inactive."""
    if config.get('status')=='PROPOSED':
        return {'status':'PROPOSED_NOT_ACTIVE','active':False,'standing_dispatch_grant':False}
    from orchestrator.dispatch_limiter import policy
    policy(config)
    if environment.get('GITHUB_ACTIONS')!='true' or environment.get('GITHUB_REPOSITORY')!='Moroseui/concept-research-scout':
        raise ValueError('HOSTED_ADMISSION_REPOSITORY_REQUIRED')
    branch=environment.get('GITHUB_REF_NAME')
    prefix='Moroseui/concept-research-scout/'
    workflow_ref=environment.get('GITHUB_WORKFLOW_REF','')
    if not workflow_ref.startswith(prefix):raise ValueError('CALLER_WORKFLOW_REQUIRED')
    path,separator,ref=workflow_ref[len(prefix):].partition('@')
    if (not separator or ref!='refs/heads/'+str(branch) or
            not re.fullmatch(r'\.github/workflows/[A-Za-z0-9_-]+\.yml',path)):
        raise ValueError('CALLER_WORKFLOW_BINDING')
    workflow=Path(repository)/path
    if workflow.is_symlink() or workflow.stat().st_size>65536:
        raise ValueError('CALLER_WORKFLOW_BYTES_REQUIRED')
    from orchestrator.remote_supervisor import checked_source
    source=environment.get('GITHUB_SHA','')
    checked_source(repository,source)
    record=identity({'repository_id':1323461276,'run_id':environment.get('GITHUB_RUN_ID'),
        'attempt':environment.get('GITHUB_RUN_ATTEMPT'),'source':source,'branch':branch,
        'workflow_sha256':hashlib.sha256(workflow.read_bytes()).hexdigest()})
    result=prepare(record,output)
    return {**result,'active':True,'policy_sha256':hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['prepare','wait','workflow-prepare'])
    parser.add_argument('--record')
    parser.add_argument('--output')
    parser.add_argument('--repository-cache')
    parser.add_argument('--policy-sha256')
    parser.add_argument('--config',default='configs/pilot/dispatch-limiter.json')
    args=parser.parse_args()
    if args.operation=='workflow-prepare':
        if not args.output or not args.repository_cache:parser.error('workflow-prepare requires --output and --repository-cache')
        result=workflow_prepare(json.loads(Path(args.config).read_text()),os.environ,args.repository_cache,args.output)
        if os.environ.get('GITHUB_OUTPUT'):
            with Path(os.environ['GITHUB_OUTPUT']).open('a') as stream:
                stream.write('active='+str(result['active']).lower()+'\n')
                if result['active']:
                    stream.write('artifact_name='+result['artifact_name']+'\npolicy_sha256='+result['policy_sha256']+'\n')
        print(json.dumps(result));return 0
    if not args.record:parser.error('prepare/wait require --record')
    record=identity(json.loads(Path(args.record).read_text()))
    if args.operation=='prepare':
        if not args.output:parser.error('prepare requires --output')
        result=prepare(record,args.output)
    else:
        if not args.repository_cache or not args.policy_sha256:
            parser.error('wait requires --repository-cache and --policy-sha256')
        from orchestrator.dispatch_limiter import GitLedger
        ledger=GitLedger(args.repository_cache,remote=True)
        origin=ledger.git('remote','get-url','origin').stdout.strip()
        if origin not in ('https://github.com/Moroseui/concept-research-scout',
                          'https://github.com/Moroseui/concept-research-scout.git'):
            raise ValueError('LIMITER_REPOSITORY_MISMATCH')
        ledger.expected_remote=origin
        result=wait(record,ledger.read,args.policy_sha256)
    raw=json.dumps(result);scan('admission-status.json',raw.encode());print(raw)
    return 0 if result['status'] in ('REQUESTED_NOT_ADMITTED','ADMITTED') else 2


if __name__=='__main__':raise SystemExit(main())
