#!/usr/bin/env python3
"""Start a finite supervised completion test, preserving every partial attempt.

The temporary timer only polls the installed non-root coordinator. Its automatic
30-minute stop is armed before the first job is submitted. Already admitted work
is preserved if the timer stops. No permanent timer or live authority is enabled.
"""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import subprocess


def start(source):
    if os.getuid()!=0:raise ValueError('SETUP_ADMIN_REQUIRED')
    config=json.loads(Path('/etc/research-system/handover-controller.json').read_text())
    broker=json.loads(Path('/etc/research-system/handover-broker.json').read_text())
    if (config['source']!=source or config['purpose']!='SUPERVISED_COMPLETION_ACCEPTANCE'
            or broker['mode']!='SYNTHETIC_FIXTURE' or broker['writer_config'] is not None
            or broker['model_mode']!='SUPERVISED' or broker['max_model_turns']!=3
            or config['report_schedule'] is not None):raise ValueError('BOUNDED_INSTALLED_FIXTURE_REQUIRED')
    execution=config['synthetic_execution']
    if execution['authority']!='OPERATOR_SUPERVISED_SYNTHETIC_ONLY' or len(execution['pairs'])!=1:
        raise ValueError('ONE_SYNTHETIC_PAIR_REQUIRED')
    parent,child=next(iter(execution['pairs'].items()))
    evidence=Path('/var/lib/research-system')/('completion-install-'+source)
    marker=evidence/'start-intent.json'
    timer='research-system-completion-fixture.timer'
    target=Path('/run/systemd/system')/timer
    if marker.exists() or target.exists():raise ValueError('EXISTING_START_RECONCILE_NO_RETRY')
    db=sqlite3.connect('file:'+execution['state']+'/jobs.sqlite?mode=ro',uri=True)
    try:
        if db.execute('SELECT count(*) FROM jobs WHERE id IN (?,?)',(parent,child)).fetchone()[0]:
            raise ValueError('EXISTING_JOB_RECONCILE_NO_RETRY')
    finally:db.close()
    with marker.open('x') as out:json.dump({'source':source,'parent':parent,'child':child},out)
    unit='[Unit]\nDescription=Temporary supervised completion acceptance poll\n[Timer]\nOnActiveSec=2s\nOnUnitInactiveSec=5s\nUnit=research-system-handover-controller.service\n'
    with target.open('x') as out:out.write(unit)
    os.chmod(target,0o644)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    subprocess.run(['systemd-run','--unit=research-system-completion-fixture-stop-'+source[:7],
        '--on-active=30m','/usr/bin/systemctl','stop',timer],check=True)
    # Existing controller identity, immutable executor and shared job store.
    subprocess.run(['runuser','-u','research-controller','--','env','-i',
        'PATH=/usr/bin:/bin','PYTHONDONTWRITEBYTECODE=1','PYTHONPATH='+execution['source_root'],
        '/usr/bin/python3','-B','-m','orchestrator.remote_supervisor','submit',
        '--state',execution['state'],'--source',execution['source'],'--job',parent,'--delay','10'],
        check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['systemctl','start',timer],check=True)
    receipt={'status':'STARTED_BOUNDED_SYNTHETIC','source':source,'parent':parent,'child':child,
        'timer':timer,'automatic_poll_stop_minutes':30,'maximum_new_model_calls':6,
        'permanent_timer_enabled':False,'live_activation':False,'patient_execution':False}
    (evidence/'start-receipt.json').write_text(json.dumps(receipt,indent=2));return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',required=True)
    print(json.dumps(start(parser.parse_args().source)))
