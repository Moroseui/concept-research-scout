"""Reconcile an already completed supervised cycle; never dispatch a model/job."""
import argparse
import hashlib
import json
from pathlib import Path
from orchestrator.remote_supervisor import Controller, identifier, lock
from orchestrator.operations_report import Queue
from orchestrator.hosted_cycle import encoded


def read_checked(path):
    path=Path(path)
    if any(p.is_symlink() for p in (path,*path.parents)) or not path.is_file():
        raise ValueError('REGULAR_PRIVATE_EVIDENCE_REQUIRED')
    return path.read_bytes()


def reconcile(state,destination,event):
    identifier(event)
    destination=Path(destination)
    with lock(destination/'driver.lock'):
        folder=destination/event
        binding=json.loads(read_checked(folder/'binding.json'))
        complete=json.loads(read_checked(folder/'complete.json'))
        if complete.get('status')!='COMPLETE' or complete.get('real_model_calls')!=3 or any(complete.get(k)!=v for k,v in binding.items()) or binding.get('event')!=event:
            raise ValueError('COMPLETE_CYCLE_BINDING_REQUIRED')
        for stage,model in [('continuation','gpt-6-astra'),('review','claude-fable-5'),('disposition','gpt-6-astra')]:
            receipt=json.loads(read_checked(folder/(stage+'.receipt.json')))
            if receipt.get('stage')!=stage or receipt.get('returncode')!=0 or receipt.get('requested_model')!=model:
                raise ValueError('COMPLETED_MODEL_RECEIPT_REQUIRED')
            if stage=='review' and receipt.get('actual_model')!=model:raise ValueError('REVIEW_MODEL_MISMATCH')
            for suffix,key in [('stdout','stdout_sha256'),('stderr','stderr_sha256'),('input.md','input_sha256'),('md','answer_sha256')]:
                if hashlib.sha256(read_checked(folder/(stage+'.'+suffix))).hexdigest()!=receipt.get(key):raise ValueError('MODEL_EVIDENCE_CHANGED')
        report=complete['report']
        if len(report)!=64 or any(c not in '0123456789abcdef' for c in report):raise ValueError('REPORT_ID')
        report_root=folder/'reports'
        if hashlib.sha256(read_checked(report_root/(report+'.md'))).hexdigest()!=report:raise ValueError('REPORT_CHANGED')
        q=Queue(report_root);row=q.status(report)
        if row['status']!='REVIEWED' or row['source']!=binding['source']:raise ValueError('ACTUAL_REVIEW_REQUIRED')
        if read_checked(report_root/(report+'.claude-review.md'))!=read_checked(folder/'review.md'):raise ValueError('REVIEW_CHANGED')
        if read_checked(report_root/(report+'.astra-disposition.md'))!=read_checked(folder/'disposition.md'):raise ValueError('DISPOSITION_CHANGED')
        controller=Controller(Path(state)/'jobs.sqlite')
        controller.db.execute('BEGIN IMMEDIATE')
        try:
            e=controller.db.execute('SELECT job,payload FROM events WHERE id=?',(event,)).fetchone()
            w=controller.db.execute('SELECT * FROM wakes WHERE id=?',(event,)).fetchone()
            if not e or not w or w['job']!=e['job'] or hashlib.sha256(encoded(json.loads(e['payload']))).hexdigest()!=binding['event_sha256']:
                raise ValueError('TRIGGER_EVENT_CHANGED')
            if w['status'] not in ('PENDING_AUTH','PROCESSED'):raise ValueError('WAKE_STATE_RECONCILE_REQUIRED')
            duplicate=w['status']=='PROCESSED'
            if duplicate and w['reason']!='SUPERVISED_CYCLE_'+report:raise ValueError('OTHER_CYCLE_ALREADY_PROCESSED')
            controller.db.execute("UPDATE wakes SET status='PROCESSED',reason=? WHERE id=?",('SUPERVISED_CYCLE_'+report,event))
            controller.db.execute('COMMIT')
        except BaseException:controller.db.execute('ROLLBACK');raise
        return {'event':event,'status':'PROCESSED','report':report,'duplicate':duplicate,'model_calls':0,'job_dispatches':0}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('state','destination','event'):p.add_argument('--'+key,required=True)
    print(json.dumps(reconcile(**vars(p.parse_args()))))

if __name__=='__main__':main()
