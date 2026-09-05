"""Persistent local coordinator for the reviewed, immutable P001 execution snapshot."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid
from orchestrator.job_store import Store

ROOT=Path(__file__).resolve().parents[1]
FILES=['orchestrator/pilot_jobs.py','orchestrator/job_store.py','tests/test_pilot_jobs.py','tests/test_job_store.py']
SNAPSHOT_PIN='0770c7d'


def reviewed():
    prefix=ROOT/'docs/isles-pilot/reviews/pilot-jobs'
    e=json.loads(Path(str(prefix)+'.execution.json').read_text());p=Path(str(prefix)+'.response.json')
    r=json.loads(p.read_text());v=r.get('structured_output',{})
    if (e['returncode'] or r.get('is_error') or r.get('subtype')!='success' or v.get('verdict')!='APPROVE'
        or v.get('scope')!='pilot-jobs' or v.get('reviewed_commit')!=e['reviewed_commit']
        or 'claude-fable-5' not in e.get('assistant_message_models',[])
        or hashlib.sha256(p.read_bytes()).hexdigest()!=e['response_sha256']):raise ValueError('job coordinator review required')
    for f in FILES:
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=e['input_file_sha256'].get(f):raise ValueError('job review stale')


def snapshot(path,pin):
    path=Path(path).resolve()
    actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=path,text=True).strip()
    if actual!=pin or subprocess.check_output(['git','status','--porcelain'],cwd=path).strip():
        raise ValueError('execution snapshot changed')


def classify(phase,meta):
    if meta.get('status')!='COMPLETE':return 'FAILED'
    value=meta.get('remote',{}).get('status') if phase=='acquisition' else meta.get('job_status')
    return {'STARTING':'RUNNING','RUNNING':'RUNNING','VALIDATED':'VALIDATED',
        'DISPATCHED_NOT_YET_VALIDATED':'DISPATCHED','NOT_VISIBLE':'NOT_VISIBLE','FAILED':'FAILED'}.get(value,'FAILED')


def tick(store,job,private_root):
    reviewed()
    row=store.claim(job)
    if row is None:return store.get(job)['status']
    binding=json.loads(row['binding']);attempt=uuid.uuid4().hex
    folder=Path(private_root)/job;folder.mkdir(mode=0o700,exist_ok=True)
    out=folder/(attempt+'.stdout');err=folder/(attempt+'.stderr')
    try:
        snapshot(binding['snapshot'],binding['source_pin'])
        phase=row['phase'];command=[sys.executable,'-m']
        if phase=='acquisition':command+=['orchestrator.colab_acquire','poll']
        elif phase=='dispatch':command+=['orchestrator.colab_patient','dispatch','--archive','/content/isles-p001-input-16813698/train.7z']
        elif phase=='patient':command+=['orchestrator.colab_patient','poll']
        else:raise ValueError('unknown phase')
        command+=['--private-dir',str(folder/attempt)]
        with out.open('xb') as stdout,err.open('xb') as stderr:
            os.chmod(out,0o600);os.chmod(err,0o600)
            result=subprocess.run(command,cwd=binding['snapshot'],stdout=stdout,stderr=stderr,timeout=700)
        meta=json.loads(out.read_text()) if result.returncode==0 else {}
        status=classify(phase,meta)
    except subprocess.TimeoutExpired:status='TRANSIENT'
    except Exception:status='FAILED'
    store.complete_event(job,attempt,status,lease=row['lease'])
    return store.get(job)['status']


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['register','tick','run','status','inbox','demo'])
    p.add_argument('--private-root',type=Path,required=True);p.add_argument('--job',default='P001')
    p.add_argument('--snapshot',type=Path);p.add_argument('--source-pin');a=p.parse_args()
    if not re.fullmatch('[A-Za-z0-9_-]{1,64}',a.job):p.error('invalid job identifier')
    private=a.private_root.resolve()
    if a.private_root.is_symlink() or private.is_relative_to(ROOT):p.error('job state must remain private outside checkout')
    private.mkdir(mode=0o700,parents=True,exist_ok=True);os.chmod(private,0o700)
    os.umask(0o077);store=Store(private/'jobs.sqlite')
    if a.action=='register':
        reviewed()
        if not a.snapshot or not a.source_pin or not re.fullmatch('[0-9a-f]{40}',a.source_pin):p.error('exact snapshot and source pin required')
        snapshot(a.snapshot,a.source_pin)
        store.register(a.job,{'snapshot':str(a.snapshot.resolve()),'source_pin':a.source_pin,'experiment':'P001'})
    elif a.action=='demo':
        job='SYNTHETIC';store.register(job,{'driver':'synthetic-no-patient-execution'})
        for n,result in enumerate(['VALIDATED','DISPATCHED','VALIDATED']):
            row=store.claim(job,10000*n)
            if row:store.complete_event(job,'demo-'+str(n),result,10000*n,lease=row['lease'])
        print(json.dumps({'status':'SYNTHETIC_ONLY','inbox':store.inbox()}));return
    elif a.action in ['tick','run']:
        while True:
            status=tick(store,a.job,private)
            if a.action=='tick' or status=='BLOCKED':break
            time.sleep(60)
    if a.action=='inbox':print(json.dumps(store.inbox()))
    else:
        row=store.get(a.job)
        print(json.dumps({k:row[k] for k in ['id','phase','status','retries']}))


if __name__=='__main__':main()
