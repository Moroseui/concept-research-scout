#!/usr/bin/env python3
"""Bounded non-patient hosted check; never enables a service or invokes a model.

Uses a fresh private attempt directory. Original fixture receipts remain there.
The compact returned result identifies synthetic behavior, not scientific approval.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time

from orchestrator.handover_coordinator import Coordinator,encoded,digest
from orchestrator.operations_report import immutable
from orchestrator.remote_supervisor import checked_source
from orchestrator.git_publication import scan


def run(root,source,attempt):
    checked_source(root,source)
    if os.getuid()==0:raise ValueError('NONROOT_FIXTURE_REQUIRED')
    attempt=Path(attempt)
    attempt.mkdir(mode=0o700)  # Never reuse an uncertain attempt.
    started=time.monotonic();calls=[]
    def complete(binding,position):
        calls.append(position)
        if position==1:
            immutable(attempt/'transport-original.json',encoded({'status':'COMPLETE','kind':'synthetic','result':'original transport fixture'}))
            raise ConnectionError('synthetic lost response')
        return {'kind':'synthetic','result':'original fixture stage'}
    binding={'id':hashlib.sha256(b'hosted-handover-fixture-v1').hexdigest(),
             'source':source,'kind':'astra_turn','thread':'primary','dependencies':[],
             'stages':['fixture','fixture']}
    q=Coordinator(attempt/'state',{'fixture':complete},lambda b:{'status':'ADMITTED','kind':'synthetic'})
    q.submit(binding)
    if q.tick()['status']!='BLOCKED':raise ValueError('EXPECTED_FIXTURE_FAILURE_MISSING')
    restarted=Coordinator(attempt/'state',{'fixture':complete},lambda b:{'status':'ADMITTED','kind':'synthetic'})
    recovered=restarted.recover(binding['id'],lambda b,p:json.loads((attempt/'transport-original.json').read_text()))
    if recovered['model_calls']!=0 or restarted.tick()['status']!='COMPLETE' or calls!=[0,1]:raise ValueError('RECOVERY_DUPLICATED')
    if not restarted.submit(binding)['duplicate']:raise ValueError('DUPLICATE_NOT_DETECTED')
    if restarted.tick()['status']!='WAITING_FOR_ELIGIBLE_WORK':raise ValueError('DUPLICATE_EXECUTION')
    # Library authentication is fixture-supplied here; OS-authenticated operator
    # control and socket services need their separate deployed acceptance test.
    restarted.control({'id':'fixture-pause','expected_revision':0,'action':'pause'},authenticated_operator=True)
    if restarted.tick()['status']!='PAUSED':raise ValueError('PAUSE_FAILED')
    restarted.control({'id':'fixture-resume','expected_revision':1,'action':'resume'},authenticated_operator=True)
    result={'version':1,'kind':'HOSTED_NONROOT_COMPONENT_FIXTURE','source':source,
            'uid':os.getuid(),'status':'PASS','model_calls':0,'patient_files':0,
            'recovery':'original fixture outcome reused; completed predecessor not repeated',
            'duplicate':'no second dispatch','controls':'library fixture only; OS operator path not established',
            'wall_seconds':time.monotonic()-started,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'verified_utc':datetime.now(timezone.utc).isoformat(),
            'limits':'not an installed broker, scheduled model cycle, phone decision or unattended acceptance'}
    scan('fixture-result.json',encoded(result));immutable(attempt/'result.json',encoded(result))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True);parser.add_argument('--attempt',required=True)
    args=parser.parse_args()
    print(json.dumps(run(Path(__file__).resolve().parents[1],args.source,args.attempt),sort_keys=True))
