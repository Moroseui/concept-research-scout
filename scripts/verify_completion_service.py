#!/usr/bin/env python3
"""Verify a completed finite hosted pair and stop only its temporary poll timer.

Run through the setup administrator with an exact installed source and a fresh
private output directory. Verification uses the installed system's validators.
No model, job, import, reset, publication or permanent timer is started here.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys


def verify(source,destination):
    if os.getuid()!=0:raise ValueError('SETUP_ADMIN_REQUIRED')
    root=Path('/opt/research-system/handover').resolve();sys.path.insert(0,str(root))
    from orchestrator.remote_supervisor import checked_source
    from orchestrator.hosted_cycle import controller_snapshot,verified_jobs
    from orchestrator.protected_handover import Broker
    from orchestrator.handover_coordinator import digest
    from orchestrator.git_publication import scan
    checked_source(root,source)
    config=json.loads(Path('/etc/research-system/handover-controller.json').read_text())
    broker_config=json.loads(Path('/etc/research-system/handover-broker.json').read_text())
    if config['source']!=source or config['purpose']!='SUPERVISED_COMPLETION_ACCEPTANCE':
        raise ValueError('INSTALLED_FIXTURE_BINDING_REQUIRED')
    if broker_config['mode']!='SYNTHETIC_FIXTURE' or broker_config['writer_config'] is not None:
        raise ValueError('NO_LIVE_AUTHORITY_REQUIRED')
    pairs=config['synthetic_execution']['pairs'];jobs=list(pairs)+list(pairs.values())
    if len(jobs)!=2:raise ValueError('ONE_PAIR_REQUIRED')
    controller=controller_snapshot(config['synthetic_execution']['state'])
    rows,events=verified_jobs(controller,config['synthetic_execution']['outputs'],jobs)
    if len(rows)!=2 or any(r['status']!='COMPLETE' for r in rows):raise ValueError('SYNTHETIC_PAIR_NOT_COMPLETE')
    state=Path(config['state'])
    db=sqlite3.connect('file:'+str(state/'coordinator.sqlite')+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    ingested=[dict(r) for r in db.execute('SELECT * FROM completion_ingest WHERE job IN (?,?)',jobs)]
    if len(ingested)!=2 or any(r['status']!='PROCESSED' for r in ingested):raise ValueError('COMPLETION_NOT_PROCESSED')
    broker=Broker(broker_config);before,ledger=broker.ledger.read()
    if ledger['count']!=3 or len(list(Path(broker_config['turn_root']).glob('*/binding.json')))!=3:
        raise ValueError('UNEXPECTED_MODEL_ADMISSION_COUNT')
    exported={};calls=[];observations=[]
    for item in ingested:
        task=db.execute('SELECT * FROM tasks WHERE id=?',(item['task'],)).fetchone()
        bookkeeping=db.execute('SELECT status FROM bookkeeping WHERE task=?',(item['task'],)).fetchone()
        if task['status']!='COMPLETE' or bookkeeping[0]!='COMPLETE':raise ValueError('BOOKKEEPING_NOT_COMPLETE')
        binding=json.loads(task['binding']);event={'turn_id':item['task'],'attempt':'1','source':source,
            'branch':'astra/infrastructure-milestone-record','kind':'astra_turn'}
        turn=Path(broker_config['turn_root'])/(item['task']+'-1')
        for position,stage in enumerate(('continuation','review','disposition')):
            original=broker.stage_status({'event':event,'stage':stage})
            receipt=json.loads((state/(item['task']+'-'+str(position)+'.json')).read_text())
            if (receipt['binding']!=digest(binding) or receipt['position']!=position
                    or receipt['output_sha256']!=digest(receipt['output'])
                    or receipt['output']['answer']!=original['answer']
                    or receipt['output']['receipt']!=original['receipt']):
                raise ValueError('COORDINATOR_ORIGINAL_RECEIPT_MISMATCH')
            model=original['receipt']
            if model['returncode']!=0 or model['requested_model']!=('claude-fable-5' if stage=='review' else 'gpt-6-astra'):
                raise ValueError('MODEL_IDENTITY_OR_FAILURE')
            if stage=='review' and model['actual_model']!='claude-fable-5':raise ValueError('REVIEWER_IDENTITY_REQUIRED')
            calls.append({'job':item['job'],'stage':stage,**model})
            for suffix in ('.md','.receipt.json','.operating-context.json'):
                exported[item['job']+'-'+stage+suffix]=(turn/(stage+suffix)).read_bytes()
        report=json.loads((state/'tasks'/item['task']/'report.json').read_text())['id']
        raw=(state/'reports'/(report+'.md')).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=report:raise ValueError('REPORT_CHANGED')
        exported[report+'.md']=raw
        for name in re.findall(r'\]\(([0-9a-f]{64}\.(?:receipts|context)\.json)\)',raw.decode()):
            payload=(state/'reports'/name).read_bytes()
            if hashlib.sha256(payload).hexdigest()!=name[:64]:raise ValueError('REPORT_EVIDENCE_CHANGED')
            exported[name]=payload
        observations.append(json.loads((state/('completion-observation-'+item['event']+'-'+source+'.json')).read_text())['evidence']['controller_process'])
    selected=[dict(r) for r in db.execute('SELECT task,status,attempts FROM selected_dispatch')]
    if len(selected)!=1 or selected[0]['status']!='SUBMITTED' or selected[0]['attempts']!=1:
        raise ValueError('SUCCESSOR_NOT_SUBMITTED_EXACTLY_ONCE')
    # Never stop a model or controller process. The timer alone is temporary.
    subprocess.run(['systemctl','stop','research-system-completion-fixture.timer'],check=True)
    observed=subprocess.check_output(['systemctl','show','research-system-handover-controller.service','--property=ActiveState','--value'],text=True).strip()
    if observed!='inactive':
        raise ValueError('CONTROLLER_STILL_RUNNING_RECONCILE')
    after,final=broker.ledger.read()
    if before!=after or final['count']!=3:raise ValueError('ADMISSION_CHANGED_DURING_COLLECTION')
    result={'kind':'SUPERVISED_PERSISTENT_COMPLETION_ACCEPTANCE','status':'PASS','source':source,
        'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'verified_utc':datetime.now(timezone.utc).isoformat(),'jobs':rows,'events':events,
        'completion_ingest':ingested,'selected_dispatch':selected,'model_calls':calls,
        'controller_observations':observations,'ledger_count':3,'new_model_calls':6,
        'original_stage_bytes_verified':True,'temporary_timer_stopped':True,
        'live_activation':False,'patient_execution':False,
        'limitations':['Astra was explicitly requested; this CLI does not independently report its resolved model.',
            'Finite supervised service execution; not 24–48 hour disconnected acceptance.',
            'No live writer credential or shared limiter activation.']}
    exported['receipt.json']=(json.dumps(result,indent=2)+'\n').encode()
    for name,raw in exported.items():scan('docs/operations/hosted-completion-20260907/'+name,raw)
    destination=Path(destination);destination.mkdir(mode=0o700)
    public=destination/'checked';public.mkdir(mode=0o700)
    for name,raw in exported.items():(public/name).write_bytes(raw)
    for name in ('handover-controller.json','handover-broker.json'):
        (destination/name).write_bytes((Path('/etc/research-system')/name).read_bytes())
    journal=subprocess.run(['journalctl','--no-pager','-u','research-system-handover-controller.service','-n','1000','-o','json'],capture_output=True,check=True)
    (destination/'original-service-journal.jsonl').write_bytes(journal.stdout)
    return {'status':'PASS','source':source,'new_model_calls':6,'jobs':jobs,'temporary_timer_stopped':True}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();os.umask(0o077);print(json.dumps(verify(a.source,a.destination)))
