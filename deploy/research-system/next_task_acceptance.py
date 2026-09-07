#!/usr/bin/env python3
"""One supervised, fresh synthetic predecessor -> selected successor cycle.

Run as a bounded setup service, not a standing driver. Never replace an existing
attempt, execution source or installed controller/worker service.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from orchestrator.hosted_cycle import run,immutable,encoded
from orchestrator.remote_supervisor import checked_source,lock

PARENT='40-closeout-trigger'
CHILD='41-closeout-followup'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['source-root','source','execution-root','execution-source','state','outputs','destination','day']:p.add_argument('--'+key,required=True)
    a=p.parse_args();os.umask(0o077)
    if os.getuid()!=0:raise ValueError('BOUNDED_SETUP_ADMIN_REQUIRED')
    root=checked_source(a.source_root,a.source);checked_source(a.execution_root,a.execution_source)
    dest=Path(a.destination)
    # Fresh invocation only. Existing state always requires reconciliation.
    dest.mkdir(mode=0o700,exist_ok=False)
    immutable(dest/'supervised-launch.json',encoded({'reporting_source':a.source,'execution_source':a.execution_source,'parent':PARENT,'eligible_successor':CHILD,'maximum_jobs':2,'maximum_model_calls':3,'patient':False,'standing_activation':False}))
    def command(*args):
        return subprocess.run(['runuser','-u','research-controller','--','env','GIT_OPTIONAL_LOCKS=0','python3','-B','-m','orchestrator.remote_supervisor',*args,'--state',a.state],cwd=root,capture_output=True,check=True,timeout=30)
    current=json.loads(command('status').stdout)
    if any(row['job_id'] in [PARENT,CHILD] for row in current['jobs']):raise ValueError('JOB_ALREADY_EXISTS_RECONCILE_NO_RETRY')
    command('submit','--source',a.execution_source,'--job',PARENT)
    deadline=time.monotonic()+240
    while True:
        status=json.loads(command('status').stdout)
        row=next(r for r in status['jobs'] if r['job_id']==PARENT)
        if row['status'] in ('COMPLETE','FAILED','BLOCKED'):break
        if time.monotonic()>deadline:raise ValueError('PREDECESSOR_UNCERTAIN_RECONCILE')
        time.sleep(2)
    if row['status']!='COMPLETE':raise ValueError('PREDECESSOR_NOT_COMPLETE')
    result=run(root,a.source,a.state,a.outputs,dest,PARENT,a.day,a.execution_root,CHILD)
    immutable(dest/'acceptance-result.json',encoded(result));print(json.dumps(result))

if __name__=='__main__':main()
