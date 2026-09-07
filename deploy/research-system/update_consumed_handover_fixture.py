#!/usr/bin/env python3
"""Upgrade an idle, fully consumed synthetic fixture without enlarging authority.

Preserve old configuration, installed source and original model evidence. No job,
model, timer or credential is added. Refuse active, incomplete or partial setup.
"""
import argparse
import fcntl
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tarfile

from install_handover_fixture import verified_archive,readable_source


def plan(broker,runtime,before,source,root):
    if not all(re.fullmatch('[0-9a-f]{40}',p) for p in (before,source)) or before==source:
        raise ValueError('DISTINCT_EXACT_SOURCE_PINS_REQUIRED')
    if (broker['mode']!='SYNTHETIC_FIXTURE' or broker['model_mode']!='SUPERVISED'
            or broker['writer_config'] is not None or runtime['source']!=before
            or before not in broker['sources'] or source in broker['sources']
            or not 1<=broker['max_model_turns']<=4 or runtime.get('report_schedule') is not None
            or runtime.get('publication') is not None
            or runtime['purpose']!='SUPERVISED_COMPLETION_ACCEPTANCE'):
        raise ValueError('CONSUMED_SYNTHETIC_CONFIGURATION_REQUIRED')
    return ({**broker,'sources':[*broker['sources'],source]},
            {**runtime,'source':source,'source_root':str(root)})


def update(before,source,archive,sha):
    if os.getuid()!=0:raise ValueError('SETUP_ADMIN_REQUIRED')
    config=Path('/etc/research-system');link=Path('/opt/research-system/handover')
    oldroot=link.resolve();sys.path.insert(0,str(oldroot))
    from orchestrator.remote_supervisor import checked_source
    from orchestrator.protected_handover import Broker
    checked_source(oldroot,before)
    broker=json.loads((config/'handover-broker.json').read_text())
    runtime=json.loads((config/'handover-controller.json').read_text())
    release=Path('/opt/research-system/releases')/(source+'-handover-update')
    evidence=Path('/var/lib/research-system')/('handover-update-'+source)
    newbroker,newruntime=plan(broker,runtime,before,source,release/'snapshot')
    if release.exists() or evidence.exists():raise ValueError('PARTIAL_UPDATE_RECONCILE')
    for unit in ('research-system-handover-controller.service','research-system-handover-controller.timer',
                 'research-system-completion-fixture.timer'):
        state=subprocess.check_output(['systemctl','show',unit,'--property=ActiveState','--value'],text=True).strip()
        if state not in ('inactive','failed'):raise ValueError('ACTIVE_HANDOVER_RECONCILE')
    raw=verified_archive(archive,sha)
    turns=Path(broker['turn_root'])
    with (turns/'branch.lock').open('a') as gate:
        fcntl.flock(gate,fcntl.LOCK_EX|fcntl.LOCK_NB)
        folders=list(turns.glob('*/binding.json'))
        if len(folders)!=broker['max_model_turns']:raise ValueError('FIXTURE_ALLOWANCE_NOT_CONSUMED')
        old=Broker(broker)
        for path in folders:
            event=json.loads(path.read_text())['event']
            for stage in ('continuation','review','disposition'):
                if old.stage_status({'event':event,'stage':stage})['status']!='COMPLETE':
                    raise ValueError('INCOMPLETE_ORIGINAL_MODEL_RECONCILE')
        db=sqlite3.connect('file:'+runtime['state']+'/coordinator.sqlite?mode=ro',uri=True)
        try:
            if (db.execute("SELECT count(*) FROM tasks WHERE status!='COMPLETE'").fetchone()[0]
                    or db.execute("SELECT count(*) FROM bookkeeping WHERE status!='COMPLETE'").fetchone()[0]):
                raise ValueError('INCOMPLETE_COORDINATOR_RECONCILE')
        finally:db.close()
        ledger_before,_=old.ledger.read()
        evidence.mkdir(mode=0o700)
        for name in ('handover-broker.json','handover-controller.json'):
            (evidence/name).write_bytes((config/name).read_bytes())
        (evidence/'previous-source.txt').write_text(str(oldroot))
        release.mkdir(mode=0o755);os.chmod(release,0o755)
        with tarfile.open(fileobj=io.BytesIO(raw)) as bundle:bundle.extractall(release,filter='data')
        readable_source(release/'snapshot');checked_source(release/'snapshot',source)
        unit='research-system-handover-controller.service'
        if (Path('/etc/systemd/system')/unit).read_bytes()!=(release/'snapshot/deploy/research-system'/unit).read_bytes():
            raise ValueError('UNIT_CHANGE_REQUIRES_SEPARATE_REVIEWED_SETUP')
        wrapper=Path('/usr/local/bin/research-system-control')
        wrapper_bytes=(release/'snapshot/deploy/research-system/research-system-control.sh').read_bytes()
        if wrapper.is_symlink() or (wrapper.exists() and (wrapper.read_bytes()!=wrapper_bytes
                or wrapper.stat().st_uid!=0 or wrapper.stat().st_mode&0o022)):
            raise ValueError('EXISTING_HUMAN_WRAPPER_PRESERVED')
        subprocess.run(['systemctl','stop','research-system-handover.socket','research-system-handover.service'],check=True)
        for name,value in [('handover-broker.json',newbroker),('handover-controller.json',newruntime)]:
            target=config/name;info=target.stat();temporary=config/(name+'.update-new')
            with temporary.open('x') as out:json.dump(value,out,indent=2)
            os.chown(temporary,info.st_uid,info.st_gid);os.chmod(temporary,info.st_mode&0o777);os.replace(temporary,target)
        temporary=link.with_name('handover-update-new');temporary.symlink_to(release/'snapshot');os.replace(temporary,link)
        if not wrapper.exists():
            with wrapper.open('xb') as out:out.write(wrapper_bytes)
            os.chmod(wrapper,0o755)
        if old.ledger.read()[0]!=ledger_before:raise ValueError('ADMISSION_CHANGED_BEFORE_RESTART_RECONCILE')
        subprocess.run(['systemctl','start','research-system-handover.socket','research-system-handover.service'],check=True)
        ledger_after,_=old.ledger.read()
        if ledger_before!=ledger_after:raise ValueError('ADMISSION_CHANGED_DURING_UPDATE')
        result={'status':'UPDATED_IDLE_CONSUMED_FIXTURE','before':before,'source':source,
            'retained_model_turns':len(folders),'max_model_turns':newbroker['max_model_turns'],
            'ledger_pin_unchanged':True,'models_started':0,'timer_started':False,
            'writer_credentials':False,'live_activation':False,'archive_sha256':sha}
        (evidence/'receipt.json').write_text(json.dumps(result,indent=2));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('before','source','archive','archive-sha256'):p.add_argument('--'+name,required=True)
    a=p.parse_args();os.umask(0o077);print(json.dumps(update(a.before,a.source,a.archive,a.archive_sha256)))
