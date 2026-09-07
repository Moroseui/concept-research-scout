"""Consume a protected list of Actions requests through the shared admission CAS.

This deterministic command is run by the installed protected service identity.
The operator-installed manifest pins each allowed workflow/source. Run IDs alone
are untrusted: the existing GitHub collector checks the actual attempt and bytes.
No workflow, model, reset or publication is launched. Each invocation is bounded;
API failures leave a named durable outcome and other requests can proceed.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path

from orchestrator.actions_admission_transport import collect
from orchestrator.handover_coordinator import encoded
from orchestrator.operations_report import immutable, private_root
from orchestrator.phone_notifications import protected_read,api
from orchestrator.protected_handover import Broker


def discover(allowlist,token,*,get=api):
    """Find uploaded requests only; never spend retry attempts before upload."""
    fields={'source','branch','workflow_path','workflow_sha256'}
    if (not isinstance(allowlist,list) or not 1<=len(allowlist)<=16 or
            any(not isinstance(row,dict) or set(row)!=fields for row in allowlist)):
        raise ValueError('BOUNDED_WORKFLOW_ALLOWLIST_REQUIRED')
    prefix='/repos/Moroseui/concept-research-scout'
    page=get('GET',prefix+'/actions/runs?event=workflow_dispatch&status=in_progress&per_page=100',token)
    runs=page.get('workflow_runs')
    if not isinstance(runs,list) or len(runs)>=100:
        raise ValueError('ACTIONS_DISCOVERY_WINDOW_LIMIT')
    found=[];examined=0
    for run in runs:
        matches=[row for row in allowlist if (row['source'],row['branch'],row['workflow_path'])==
                 (run.get('head_sha'),run.get('head_branch'),run.get('path'))]
        if not matches:continue
        if len(matches)!=1:raise ValueError('AMBIGUOUS_WORKFLOW_ALLOWLIST')
        examined+=1
        if examined>16:raise ValueError('ACTIONS_DISCOVERY_REQUEST_LIMIT')
        if (run.get('repository',{}).get('id')!=1323461276 or run.get('event')!='workflow_dispatch'
                or type(run.get('id')) is not int or run['id']<=0
                or type(run.get('run_attempt')) is not int or run['run_attempt']<=0):
            raise ValueError('ACTIONS_DISCOVERY_IDENTITY')
        expected={**matches[0],'run_id':str(run['id']),'attempt':str(run['run_attempt'])}
        name='research-admission-'+expected['run_id']+'-'+expected['attempt']
        artifacts=get('GET',prefix+'/actions/runs/'+expected['run_id']+'/artifacts?per_page=100',token).get('artifacts')
        if not isinstance(artifacts,list) or len(artifacts)>=100:
            raise ValueError('ACTIONS_DISCOVERY_ARTIFACT_LIMIT')
        if any(row.get('name')==name for row in artifacts):found.append(expected)
        if len(found)>16:raise ValueError('ACTIONS_DISCOVERY_REQUEST_LIMIT')
    # This is only discovery. collect rechecks the exact attempt, source, artifact
    # identity and actual workflow bytes before any admission can be written.
    return sorted(found,key=lambda row:(int(row['run_id']),int(row['attempt'])))


def reconcile(broker, requests, output, *, fetch=collect):
    if not isinstance(requests,list) or len(requests)>16:
        raise ValueError('BOUNDED_PROTECTED_REQUEST_LIST_REQUIRED')
    root=private_root(output)
    with (root/'collector.lock').open('a') as gate:
        fcntl.flock(gate,fcntl.LOCK_EX)
        return _reconcile(broker,requests,root,fetch)


def _reconcile(broker,requests,root,fetch):
    results=[]
    for expected in requests:
        identity=hashlib.sha256(encoded(expected)).hexdigest()
        final=root/(identity+'.json')
        if final.exists():
            if final.is_symlink():raise ValueError('ADMISSION_RECEIPT_SYMLINK')
            previous=json.loads(final.read_text())
            if previous.get('request_sha256')!=identity:
                raise ValueError('ADMISSION_RECEIPT_BINDING')
            results.append(previous);continue
        observations=list(root.glob(identity+'.attempt-*.json'))
        if len(observations)>=3:
            results.append({'request_sha256':identity,'outcome':{
                'status':'BLOCKED','reason':'ACTIONS_ADMISSION_READ_RETRY_LIMIT'}})
            continue
        # Persist before network access, so process death consumes the bounded
        # read attempt. Shared admission identity still prevents a second charge.
        immutable(root/(identity+'.attempt-'+str(len(observations)+1)+'.json'),
                  encoded({'request_sha256':identity,'status':'READ_ATTEMPT_STARTED'}))
        try:
            # A protected manifest is necessary but not sufficient provenance.
            # The authenticated API must independently establish the same record.
            with broker.authentication():
                verified=fetch(expected,os.environ.get('GH_TOKEN',''))
            outcome=broker.actions_admission(verified,verified)
            record={'request_sha256':identity,'outcome':outcome}
            immutable(final,encoded(record))
        except (ValueError,KeyError,TypeError,OSError):
            # Do not persist arbitrary API error text or signed download URLs.
            # Preserve a failed observation; a later bounded poll can reconcile.
            record={'request_sha256':identity,'outcome':{
                'status':'BLOCKED','reason':'ACTIONS_ADMISSION_RECONCILIATION_REQUIRED'}}
            immutable(root/(identity+'.blocked.json'),encoded(record))
        results.append(record)
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    inputs=parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--manifest')
    inputs.add_argument('--allowlist')
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    if os.getuid()!=0:raise ValueError('PROTECTED_SERVICE_IDENTITY_REQUIRED')
    broker=Broker(json.loads(protected_read(args.config)))
    if args.manifest:requests=json.loads(protected_read(args.manifest))
    else:
        with broker.authentication():
            requests=discover(json.loads(protected_read(args.allowlist)),os.environ.get('GH_TOKEN',''))
    print(json.dumps(reconcile(broker,requests,args.output)))


if __name__=='__main__':main()
