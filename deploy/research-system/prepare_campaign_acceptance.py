#!/usr/bin/env python3
"""Prepare one explicitly bounded campaign turn on an idle supervised fixture.

Preserve its consumed turn root/configuration and shared synthetic admission ledger.
No job, model or timer is started; no live writer/reset authority is installed.
Existing or uncertain preparation is refused, never automatically retried.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys

REQUEST = ('Through the ratified prediction charter and unchanged externally seeded P001, '
           'assess the baseline question and scientific value, identify what admission-input '
           'preflight must establish about Tmax units/scaling and integrity, and state the '
           'next eligible action. No validated terminal preflight receipt is supplied to '
           'this task. Do not infer it completed, invent measurements, re-request unchanged '
           'charter ratification, or authorize launch. P001 does not depend on 047 acceptance. '
           'Keep the discussion concise and distinguish evidence gaps from operator decisions.')


def planned(broker,runtime,source):
    if (not re.fullmatch('[0-9a-f]{40}',source) or runtime['source']!=source
            or source not in broker['sources'] or broker['mode']!='SYNTHETIC_FIXTURE'
            or broker['model_mode']!='SUPERVISED' or broker['writer_config'] is not None
            or broker['max_model_turns']!=3 or runtime.get('campaign_preparation') is not None
            or runtime.get('report_schedule') is not None or runtime.get('publication') is not None
            or runtime['purpose']!='SUPERVISED_COMPLETION_ACCEPTANCE'):
        raise ValueError('IDLE_CONSUMED_SYNTHETIC_CONFIGURATION_REQUIRED')
    execution=runtime.get('synthetic_execution')
    if not isinstance(execution,dict) or execution.get('authority')!='OPERATOR_SUPERVISED_SYNTHETIC_ONLY':
        raise ValueError('EXISTING_SYNTHETIC_EXECUTOR_REQUIRED')
    job='60-campaign-'+source[:12]
    newroot=Path(broker['turn_root']).parent/('campaign-turns-'+source)
    return ({**broker,'turn_root':str(newroot),'max_model_turns':1},
            {**runtime,'campaign_preparation':{'mode':'discuss','request':REQUEST,'trigger_job':job},
             'synthetic_execution':{**execution,'pairs':{job:None}}})


def require_active_broker(prior):
    if not prior or any(state!='active' for state in prior.values()):
        raise ValueError('EXPECTED_ACTIVE_IDLE_BROKER_REQUIRED')


def restore_configuration(config, originals, replacements):
    """Restore only our exact bytes; never overwrite a third-party edit."""
    for name, original in originals.items():
        if (config/name).read_bytes() not in (original, replacements[name]):
            raise ValueError('CONCURRENT_CONFIGURATION_RECOVERY_HELD')
    for name, original in originals.items():
        target=config/name
        if target.read_bytes()==original:continue
        info=target.stat(); temporary=config/(name+'.campaign-restore')
        with temporary.open('xb') as stream:stream.write(original)
        os.chown(temporary,info.st_uid,info.st_gid)
        os.chmod(temporary,info.st_mode&0o777)
        os.replace(temporary,target)


def configuration_transaction(config, originals, replacements, mutate):
    """Preserve failed attempt evidence, restore the pair on ordinary exceptions.

    Abrupt process/host loss still requires inspecting the preserved intent and
    exact current bytes before recovery. This function never dispatches or retries.
    """
    try:
        mutate()
    except BaseException:
        restore_configuration(config, originals, replacements)
        raise


def prepare(source):
    if os.getuid()!=0:raise ValueError('SETUP_ADMIN_REQUIRED')
    os.umask(0o077)
    root=Path('/opt/research-system/handover').resolve();sys.path.insert(0,str(root))
    from orchestrator.remote_supervisor import checked_source
    from orchestrator.protected_handover import Broker
    checked_source(root,source)
    config=Path('/etc/research-system')
    originals={name:(config/name).read_bytes() for name in ('handover-broker.json','handover-controller.json')}
    broker,runtime=(json.loads(originals[name]) for name in ('handover-broker.json','handover-controller.json'))
    newbroker,newruntime=planned(broker,runtime,source)
    evidence=Path('/var/lib/research-system')/('campaign-preparation-'+source)
    newturns=Path(newbroker['turn_root'])
    dropdir=Path('/etc/systemd/system/research-system-handover-controller.service.d')
    drop=dropdir/'campaign-diagnostics.conf'
    if any(p.exists() or p.is_symlink() for p in (evidence,newturns,drop)):
        raise ValueError('EXISTING_PREPARATION_RECONCILE_NO_RETRY')
    for unit in ('research-system-handover-controller.service','research-system-handover-controller.timer','research-system-completion-fixture.timer'):
        state=subprocess.check_output(['systemctl','show',unit,'--property=ActiveState','--value'],text=True).strip()
        if state not in ('inactive','failed'):raise ValueError('ACTIVE_HANDOVER_RECONCILE')
    execution=runtime['synthetic_execution'];checked_source(execution['source_root'],execution['source'])
    old=Broker(broker)
    with (Path(broker['turn_root'])/'branch.lock').open('a') as gate:
        fcntl.flock(gate,fcntl.LOCK_EX|fcntl.LOCK_NB)
        turns=list(Path(broker['turn_root']).glob('*/binding.json'))
        if len(turns)!=3:raise ValueError('OLD_FIXTURE_NOT_FULLY_CONSUMED')
        for path in turns:
            event=json.loads(path.read_text())['event']
            for stage in ('continuation','review','disposition'):
                if old.stage_status({'event':event,'stage':stage})['status']!='COMPLETE':raise ValueError('ORIGINAL_MODEL_RECONCILE')
        for database,query in [(Path(runtime['state'])/'coordinator.sqlite',"SELECT count(*) FROM tasks WHERE status!='COMPLETE'"),
                               (Path(runtime['state'])/'coordinator.sqlite',"SELECT count(*) FROM bookkeeping WHERE status!='COMPLETE'")]:
            db=sqlite3.connect('file:'+str(database)+'?mode=ro',uri=True)
            try:
                if db.execute(query).fetchone()[0]:raise ValueError('COORDINATOR_WORK_RECONCILE')
            finally:db.close()
        db=sqlite3.connect('file:'+execution['state']+'/jobs.sqlite?mode=ro',uri=True)
        try:
            if db.execute('SELECT 1 FROM jobs WHERE id=?',(newruntime['campaign_preparation']['trigger_job'],)).fetchone():
                raise ValueError('EXISTING_JOB_RECONCILE_NO_RETRY')
        finally:db.close()
        before,_=old.ledger.read()
        evidence.mkdir(mode=0o700)
        for name,raw in originals.items():(evidence/name).write_bytes(raw)
        (evidence/'intent.json').write_text(json.dumps({'source':source,'old_turn_root':broker['turn_root'],
            'new_turn_root':str(newturns),'additional_turn_limit':1,'additional_model_call_limit':3,
            'scope':'OPERATOR_SUPERVISED_PREPARATION_ONLY','old_allowance_preserved':True}))
        for name,raw in originals.items():
            if (config/name).read_bytes()!=raw:raise ValueError('CONCURRENT_CONFIGURATION_CHANGE')
        units=('research-system-handover.socket','research-system-handover.service')
        prior={unit:subprocess.check_output(['systemctl','show',unit,'--property=ActiveState','--value'],text=True).strip() for unit in units}
        require_active_broker(prior)
        replacements={name:json.dumps(value,indent=2).encode() for name,value in
                      [('handover-broker.json',newbroker),('handover-controller.json',newruntime)]}
        (evidence/'prior-units.json').write_text(json.dumps(prior))
        def mutate():
            newturns.mkdir(mode=0o700)
            for name,value in [('handover-broker.json',newbroker),('handover-controller.json',newruntime)]:
                target=config/name
                if target.read_bytes()!=originals[name]:raise ValueError('CONCURRENT_CONFIGURATION_CHANGE')
                info=target.stat();temporary=config/(name+'.campaign-new')
                with temporary.open('xb') as stream:stream.write(replacements[name])
                os.chown(temporary,info.st_uid,info.st_gid);os.chmod(temporary,info.st_mode&0o777);os.replace(temporary,target)
            dropdir.mkdir(mode=0o755,exist_ok=True)
            with drop.open('x') as stream:stream.write('[Service]\nEnvironment=RESEARCH_GIT_DIAGNOSTICS='+runtime['state']+'/git-diagnostics\n')
            drop.chmod(0o644)
            subprocess.run(['systemctl','daemon-reload'],check=True)
            if old.ledger.read()[0]!=before:raise ValueError('ADMISSION_CHANGED_DURING_SETUP')
        try:
            subprocess.run(['systemctl','stop',*units],check=True)
            configuration_transaction(config,originals,replacements,mutate)
            subprocess.run(['systemctl','start',*units],check=True)
            after,_=old.ledger.read()
            if after!=before:raise ValueError('ADMISSION_CHANGED_DURING_RESTART')
        except BaseException as failure:
            # Preserve intent/new turn root. Restore only byte-owned configuration.
            try:
                restore_configuration(config,originals,replacements)
                if drop.exists():
                    expected='[Service]\nEnvironment=RESEARCH_GIT_DIAGNOSTICS='+runtime['state']+'/git-diagnostics\n'
                    if drop.read_text()!=expected:raise ValueError('CONCURRENT_DROPIN_RECOVERY_HELD')
                    drop.unlink()
                subprocess.run(['systemctl','daemon-reload'],check=True)
                subprocess.run(['systemctl','start',*units],check=True)
                recovery='ORIGINAL_CONFIGURATION_AND_ACTIVE_BROKER_RESTORED'
            except BaseException:
                recovery='RECOVERY_HELD_INSPECT_PRIVATE_INTENT_NO_RETRY'
            (evidence/'failure.json').write_text(json.dumps({'failure_type':type(failure).__name__,'recovery':recovery}))
            raise
        result={'status':'PREPARED_NOT_DISPATCHED','source':source,'job':newruntime['campaign_preparation']['trigger_job'],
                'old_completed_turns_preserved':3,'new_fixture_turn_limit':1,'maximum_new_model_calls':3,
                'admission_pin_unchanged':after==before,'prior_units':prior,'diagnostic_dropin':str(drop),'models_started':0,'jobs_submitted':0,
                'timer_started':False,'live_activation':False,'writer_credentials':False,
                'request_sha256':hashlib.sha256(REQUEST.encode()).hexdigest()}
        (evidence/'receipt.json').write_text(json.dumps(result,indent=2));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True)
    os.umask(0o077);print(json.dumps(prepare(p.parse_args().source)))
