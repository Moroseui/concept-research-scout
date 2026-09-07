#!/usr/bin/env python3
"""Prepare exactly two additional supervised synthetic report turns.

This is a one-time setup migration of the consumed fixture, not live activation.
It preserves old configuration and evidence, refuses uncertain work, and does
not start a timer, submit a job, or call a model. A separately bounded start
operation must follow inspection of its receipt. Partial setup is not retried.
"""
import argparse
import fcntl
import json
import io
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tarfile

from install_handover_fixture import verified_archive,readable_source

OLD='6863968863ddfb1d82b25c7b358857e666c950a5'
EXECUTOR='6b555075fcf553994ecac8e368f4676cbdffdc56'


def planned(broker,runtime,source,root):
    if not re.fullmatch('[0-9a-f]{40}',source) or source==OLD:
        raise ValueError('NEW_EXACT_SOURCE_REQUIRED')
    if (broker['mode']!='SYNTHETIC_FIXTURE' or broker['model_mode']!='SUPERVISED'
            or broker['writer_config'] is not None or broker['max_model_turns']!=1
            or broker['sources']!=[OLD] or runtime['source']!=OLD
            or runtime.get('synthetic_execution') is not None):
        raise ValueError('ORIGINAL_CONSUMED_FIXTURE_REQUIRED')
    broker={**broker,'sources':[OLD,source],'max_model_turns':3}
    parent='50-handover-'+source[:7];child='51-handover-'+source[:7]
    runtime={**runtime,'purpose':'SUPERVISED_COMPLETION_ACCEPTANCE',
        'source':source,'source_root':str(root),'report_schedule':None,
        'synthetic_execution':{'authority':'OPERATOR_SUPERVISED_SYNTHETIC_ONLY',
            'source':EXECUTOR,'source_root':'/opt/research-system/releases/'+EXECUTOR,
            'state':'/var/lib/research-system/research-controller',
            'outputs':'/var/lib/research-system/outputs','pairs':{parent:child}}}
    return broker,runtime


def prepare(source,archive,sha):
    if os.getuid()!=0:raise ValueError('SETUP_ADMIN_REQUIRED')
    config=Path('/etc/research-system');base=Path('/var/lib/research-system/handover-broker')
    state=Path('/var/lib/research-system/handover-controller')
    evidence=Path('/var/lib/research-system')/('completion-install-'+source)
    release=Path('/opt/research-system/releases')/(source+'-handover-completion')
    link=Path('/opt/research-system/handover')
    if evidence.exists() or release.exists():raise ValueError('PARTIAL_OR_EXISTING_SETUP_RECONCILE')
    if str(link.resolve())!='/opt/research-system/releases/'+OLD+'-handover/snapshot':
        raise ValueError('INSTALLED_SOURCE_CHANGED')
    if str(Path('/opt/research-system/current').resolve())!='/opt/research-system/releases/'+EXECUTOR:
        raise ValueError('EXECUTOR_CHANGED')
    broker=json.loads((config/'handover-broker.json').read_text())
    runtime=json.loads((config/'handover-controller.json').read_text())
    newbroker,newruntime=planned(broker,runtime,source,release/'snapshot')
    for unit in ('research-system-handover-controller.service','research-system-handover-controller.timer'):
        if subprocess.run(['systemctl','is-active','--quiet',unit]).returncode==0:
            raise ValueError('CONTROLLER_OR_TIMER_ACTIVE')
    raw=verified_archive(archive,sha)
    with (base/'turns/branch.lock').open('a') as gate:
        fcntl.flock(gate,fcntl.LOCK_EX|fcntl.LOCK_NB)
        turns=list((base/'turns').glob('*/binding.json'))
        if len(turns)!=1:raise ValueError('ORIGINAL_TURN_COUNT_CHANGED')
        for stage in ('continuation','review','disposition'):
            if not (turns[0].parent/(stage+'.receipt.json')).is_file():
                raise ValueError('UNCERTAIN_ORIGINAL_MODEL_RECONCILE')
        db=sqlite3.connect('file:'+str(state/'coordinator.sqlite')+'?mode=ro',uri=True)
        try:
            if db.execute("SELECT count(*) FROM tasks WHERE status!='COMPLETE'").fetchone()[0]:
                raise ValueError('EXISTING_COORDINATOR_WORK_RECONCILE')
        finally:db.close()
        evidence.mkdir(mode=0o700)
        for name in ('handover-broker.json','handover-controller.json'):
            (evidence/name).write_bytes((config/name).read_bytes())
        unit='research-system-handover-controller.service'
        (evidence/unit).write_bytes((Path('/etc/systemd/system')/unit).read_bytes())
        (evidence/'previous-source.txt').write_text(str(link.resolve()))
        release.mkdir(mode=0o755);os.chmod(release,0o755)
        with tarfile.open(fileobj=io.BytesIO(raw)) as bundle:bundle.extractall(release,filter='data')
        root=release/'snapshot';readable_source(root);sys.path.insert(0,str(root))
        from orchestrator.remote_supervisor import checked_source
        from orchestrator.protected_handover import Broker
        checked_source(root,source)
        # Verify retained original protocols before replacing the idle broker.
        old=Broker(broker)
        event=json.loads(turns[0].read_text())['event']
        for stage in ('continuation','review','disposition'):
            if old.stage_status({'event':event,'stage':stage})['status']!='COMPLETE':
                raise ValueError('ORIGINAL_STAGE_NOT_COMPLETE')
        _,ledger=old.ledger.read()
        if ledger['count']!=1:raise ValueError('FIXTURE_LEDGER_CHANGED')
        Broker(newbroker)
        subprocess.run(['systemctl','stop','research-system-handover.socket','research-system-handover.service'],check=True)
        for name,value in [('handover-broker.json',newbroker),('handover-controller.json',newruntime)]:
            target=config/name;info=target.stat();temporary=config/(name+'.completion-new')
            with temporary.open('x') as output:json.dump(value,output,indent=2)
            os.chown(temporary,info.st_uid,info.st_gid);os.chmod(temporary,info.st_mode&0o777)
            os.replace(temporary,target)
        temporary=link.with_name('handover-completion-new');temporary.symlink_to(root);os.replace(temporary,link)
        (Path('/etc/systemd/system')/unit).write_bytes((root/'deploy/research-system'/unit).read_bytes())
        subprocess.run(['systemd-analyze','verify',str(Path('/etc/systemd/system')/unit)],check=True)
        subprocess.run(['systemctl','daemon-reload'],check=True)
        subprocess.run(['systemctl','start','research-system-handover.socket','research-system-handover.service'],check=True)
        receipt={'status':'PREPARED_NOT_DISPATCHED','source':source,'previous_source':OLD,
            'execution_source':EXECUTOR,'pairs':newruntime['synthetic_execution']['pairs'],
            'old_retained_turns':1,'additional_turn_limit':2,'additional_model_call_limit':6,
            'live_activation':False,'patient_execution':False,'timer_started':False,
            'archive_sha256':sha}
        (evidence/'receipt.json').write_text(json.dumps(receipt,indent=2));return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True);parser.add_argument('--archive',required=True)
    parser.add_argument('--archive-sha256',required=True)
    args=parser.parse_args();print(json.dumps(prepare(args.source,args.archive,args.archive_sha256)))
