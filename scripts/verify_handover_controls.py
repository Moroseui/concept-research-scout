#!/usr/bin/env python3
"""Supervised installed-human-controls verification; no timer or model start.

Requires an idle, consumed synthetic fixture and preserves exact original command
outputs privately. Exercises real status/pause/repeat/resume through shared state.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def verify(source, destination):
    if os.getuid()!=0:raise ValueError('SETUP_OPERATOR_REQUIRED')
    from orchestrator.remote_supervisor import checked_source
    root=Path('/opt/research-system/handover').resolve();checked_source(root,source)
    config=json.loads(Path('/etc/research-system/handover-broker.json').read_text())
    if config['mode']!='SYNTHETIC_FIXTURE' or config['model_mode']!='SUPERVISED' or config['writer_config'] is not None:
        raise ValueError('SYNTHETIC_FIXTURE_REQUIRED')
    for unit in ('research-system-handover-controller.service','research-system-handover-controller.timer','research-system-completion-fixture.timer'):
        state=subprocess.check_output(['systemctl','show',unit,'--property=ActiveState','--value'],text=True).strip()
        if state not in ('inactive','failed'):raise ValueError('ACTIVE_SERVICE_RECONCILE')
    turns=Path(config['turn_root']);bindings=sorted(turns.glob('*/binding.json'))
    if len(bindings)!=config['max_model_turns']:raise ValueError('CONSUMED_ALLOWANCE_REQUIRED')
    destination=Path(destination);destination.mkdir(mode=0o700)
    def command(label,argv,valid=True):
        r=subprocess.run(argv,capture_output=True,timeout=65)
        (destination/(label+'.stdout')).write_bytes(r.stdout)
        (destination/(label+'.stderr')).write_bytes(r.stderr)
        if valid and r.returncode:raise ValueError('CONTROL_FAILED_'+label.upper())
        return r
    base=['/usr/bin/python3','-B','-m','orchestrator.handover_runtime','--config','/etc/research-system/handover-controller.json']
    # Imported source and CLI source are explicitly identical.
    os.environ['PYTHONPATH']=str(root);os.environ['PYTHONDONTWRITEBYTECODE']='1'
    before=json.loads(command('before',base+['status']).stdout)
    if before['paused'] or any(t['status']!='COMPLETE' for t in before['tasks']):
        raise ValueError('EXISTING_STATE_REQUIRES_RECONCILIATION')
    command('human-status',['/usr/local/bin/research-system-control','status'])
    command('pause',['/usr/local/bin/research-system-control','pause'])
    paused=json.loads(command('paused-state',base+['status']).stdout)
    if not paused['paused'] or paused['revision']!=before['revision']+1:raise ValueError('PAUSE_NOT_APPLIED')
    command('repeat-pause',['/usr/local/bin/research-system-control','pause'])
    repeated=json.loads(command('repeated-state',base+['status']).stdout)
    if repeated['revision']!=paused['revision']:raise ValueError('REPEATED_CONTROL_MUTATED_STATE')
    command('resume',['/usr/local/bin/research-system-control','resume'])
    after=json.loads(command('after',base+['status']).stdout)
    if after['paused'] or after['revision']!=before['revision']+2:raise ValueError('RESUME_NOT_APPLIED')
    invalid=command('invalid',['/usr/local/bin/research-system-control','launch'],False)
    if invalid.returncode!=2:raise ValueError('INVALID_OPERATION_NOT_REFUSED')
    if after['tasks']!=before['tasks'] or after['execution_jobs']!=before['execution_jobs'] or sorted(turns.glob('*/binding.json'))!=bindings:
        raise ValueError('UNEXPECTED_EXECUTION_STATE_CHANGE')
    receipt={'status':'PASSED','source':source,'revision_before':before['revision'],'revision_after':after['revision'],
        'actual_commands':['status','pause','repeat-pause','resume','invalid-operation'],
        'new_model_calls':0,'new_jobs':0,'timer_started':False,'live_activation':False,
        'original_output_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destination.glob('*'))}}
    (destination/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();os.umask(0o077);print(json.dumps(verify(a.source,a.destination)))
