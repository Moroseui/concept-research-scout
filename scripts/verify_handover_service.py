#!/usr/bin/env python3
"""Supervised, three-model-call service acceptance; not unattended activation.

The first phase deliberately withholds an already received disposition response
from the coordinator. The protected broker retains its real original evidence.
After an operator-controlled service restart, recovery must use that evidence
without another model invocation. This harness never enables a timer.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

import orchestrator.handover_runtime as runtime_module
from orchestrator.handover_coordinator import encoded
from orchestrator.operations_report import immutable


def resources():
    status=dict(line.split(':',1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
    result={'uid':os.getuid(),'no_new_privileges':status.get('NoNewPrivs','').strip()}
    try:
        path=next(line.split('::',1)[1] for line in Path('/proc/self/cgroup').read_text().splitlines() if line.startswith('0::'))
        base=Path('/sys/fs/cgroup')/path.lstrip('/')
        result['cgroup']={name:(base/name).read_text().strip() for name in ('memory.max','cpu.max','pids.max')}
    except (OSError,StopIteration):result['cgroup_status']='UNAVAILABLE'
    return result


def run(config,phase):
    if config.get('purpose')!='SUPERVISED_SERVICE_ACCEPTANCE' or os.getuid()==0:
        raise ValueError('SUPERVISED_NONROOT_CONFIGURATION_REQUIRED')
    observed_resources=resources()
    bounds=observed_resources.get('cgroup',{})
    cpu=bounds.get('cpu.max','').split()
    if (observed_resources['no_new_privileges']!='1' or bounds.get('memory.max')!='536870912'
            or len(cpu)!=2 or not cpu[0].isdigit() or cpu[0]!=cpu[1] or bounds.get('pids.max')!='32'):
        raise ValueError('OBSERVED_FIXTURE_RESOURCE_BOUNDARY_REQUIRED')
    runtime=runtime_module.Runtime(config)
    original=runtime_module.request_broker
    before=original(config['broker_socket'],'status',{})
    if before.get('mode')!='SYNTHETIC_FIXTURE':raise ValueError('PRIVATE_FIXTURE_LEDGER_REQUIRED')
    output=runtime.state/('service-fixture-'+phase+'.json')
    if output.exists():raise ValueError('FIXTURE_ALREADY_RECORDED_RECONCILE')
    started=time.monotonic();calls=[]
    def transport(path,operation,body):
        if phase=='recover' and operation=='model_stage':raise ValueError('RECOVERY_MODEL_CALL_FORBIDDEN')
        response=original(path,operation,body)
        if operation=='model_stage':
            receipt=response.get('receipt',{})
            calls.append({'stage':body['stage'],'duplicate':response.get('duplicate'),
                          'receipt_sha256':hashlib.sha256(encoded(receipt)).hexdigest(),
                          'requested_model':receipt.get('requested_model'),'actual_model':receipt.get('actual_model'),
                          'session_id':receipt.get('session_id')})
            if body['stage']=='disposition' and response.get('status')=='COMPLETE':
                immutable(runtime.state/'simulated-response-loss.json',encoded({
                    'kind':'SYNTHETIC_CLIENT_FAULT','response_received_then_withheld':True,
                    'receipt_sha256':hashlib.sha256(encoded(receipt)).hexdigest()}))
                raise ConnectionError('Synthetic withheld disposition response')
        return response
    if phase=='first' and (before['count']!=0 or runtime.q.status()['tasks']):
        raise ValueError('FRESH_FIXTURE_STATE_REQUIRED')
    if phase=='recover' and not (runtime.state/'service-fixture-first.json').exists():
        raise ValueError('FIRST_PHASE_EVIDENCE_REQUIRED')
    runtime_module.request_broker=transport
    try:outcome=runtime.tick()
    finally:runtime_module.request_broker=original
    after=original(config['broker_socket'],'status',{})
    if phase=='first':
        if (outcome['status']!='BLOCKED' or len(calls)!=3 or any(c['duplicate'] for c in calls)
                or [c['stage'] for c in calls]!=['continuation','review','disposition']
                or [c['requested_model'] for c in calls]!=['gpt-6-astra','claude-fable-5','gpt-6-astra']
                or calls[1]['actual_model']!='claude-fable-5'):
            raise ValueError('FIRST_PHASE_NOT_COMPLETE_INSPECT_PRIVATE_EVIDENCE')
    else:
        if outcome['status']!='COMPLETE' or calls or after['count']!=before['count']:
            raise ValueError('RECOVERY_ACCEPTANCE_FAILED')
        # A repeated poll may inspect bookkeeping; it must not make model calls.
        runtime_module.request_broker=transport
        try:repeat=runtime.tick()
        finally:runtime_module.request_broker=original
        if calls or repeat['status']!='WAITING_FOR_ELIGIBLE_WORK':raise ValueError('DUPLICATE_ACCEPTANCE_FAILED')
        if any(row['status']!='COMPLETE' for row in runtime.status()['bookkeeping']):raise ValueError('BOOKKEEPING_INCOMPLETE')
    result={'kind':'SUPERVISED_SERVICE_ACCEPTANCE','phase':phase,'source':config['source'],
            'status':'PASS','coordinator_outcome':outcome,'model_calls':calls,
            'ledger_count_before':before['count'],'ledger_count_after':after['count'],
            'resources':observed_resources,'wall_seconds':time.monotonic()-started,
            'live_activation':False,'patient_execution':False}
    immutable(output,encoded(result));return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True);parser.add_argument('--phase',choices=['first','recover'],required=True)
    args=parser.parse_args()
    print(json.dumps(run(runtime_module.configuration(args.config),args.phase)))
