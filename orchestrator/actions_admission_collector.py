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
from orchestrator.phone_notifications import protected_read
from orchestrator.protected_handover import Broker


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
    parser.add_argument('--manifest',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    if os.getuid()!=0:raise ValueError('PROTECTED_SERVICE_IDENTITY_REQUIRED')
    broker=Broker(json.loads(protected_read(args.config)))
    requests=json.loads(protected_read(args.manifest))
    print(json.dumps(reconcile(broker,requests,args.output)))


if __name__=='__main__':main()
