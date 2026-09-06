"""Explicit one-time review recovery, preserving failed-cycle originals.

Never relaunch a scientific task or repeat the initial investigator selection.
Process uncertainty refuses; actual retry uses the original report and context.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from orchestrator.hosted_cycle import encoded,model_call,immutable,sha
from orchestrator.hosted_cycle_reconcile import read_checked
from orchestrator.operations_report import Queue
from orchestrator.remote_supervisor import lock,checked_source


def live_group(identity):
    if type(identity.get('process_group'))!=int or identity['process_group']<=1:raise ValueError('PROCESS_IDENTITY_INVALID')
    boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    if identity['boot_id']!=boot:return False
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            fields=(p/'stat').read_text().rsplit(')',1)[1].split()
            if int(fields[2])==identity['process_group'] and fields[0]!='Z':return True
        except FileNotFoundError:pass
        except PermissionError:return True
    return False


def recover(folder,execute=False,call=model_call,is_live=live_group):
    folder=Path(folder)
    with lock(folder.parent/'driver.lock'):
        if (folder/'complete.json').exists():raise ValueError('CYCLE_ALREADY_COMPLETE')
        binding=json.loads(read_checked(folder/'binding.json'))
        claim=json.loads(read_checked(folder/'review-claim.json'));q=Queue(folder/'reports')
        row=q.status(claim['id'])
        if row['source']!=binding['source'] or row['attempt_id']!=claim['attempt_id']:raise ValueError('RECOVERY_CLAIM_CHANGED')
        if hashlib.sha256(read_checked(folder/'reports'/(row['id']+'.md'))).hexdigest()!=row['id']:raise ValueError('REPORT_CHANGED')
        if (folder/'review.started.json').exists():
            identity=json.loads(read_checked(folder/'review.process-identity.json'))
            if is_live(identity):raise ValueError('MODEL_PROCESS_STILL_LIVE')
        if row['status']=='REVIEWING':
            q.unavailable(row['id'],row['attempt_id'],'INTERRUPTED_REVIEW_RECONCILED_NO_LIVE_PROCESS')
        elif row['status']!='NOT_REVIEWED':raise ValueError('REVIEW_NOT_RECOVERABLE')
        if not execute:return {'status':'NOT_REVIEWED','report':row['id'],'model_calls':0,'scientific_dispatches':0}
        if row['attempts']!=1:raise ValueError('SINGLE_RETRY_BUDGET_EXHAUSTED')
        recovery=folder/'review-recovery'
        if recovery.exists():raise ValueError('RECOVERY_ATTEMPT_UNCERTAIN_NO_REPLAY')
        recovery.mkdir(mode=0o700);immutable(recovery/'binding.json',encoded({'original_report':row['id'],'original_source':row['source'],'maximum_model_calls':2}))
        retry=q.claim(row['id'])
        if retry is None:raise ValueError('RETRY_NOT_ADMITTED')
        original=read_checked(folder/'review.input.md').decode()
        try:
            review,receipt=call(recovery,'review','claude',original,prepared_prompt=True)
            q.attach(row['id'],retry['attempt_id'],review,{'family':'claude','model':receipt['actual_model'],'source':row['source'],'report_sha256':row['id'],'review_sha256':sha(review.encode()),'execution_receipt_sha256':sha(encoded(receipt)),'session_id':receipt['session_id'],'status':'COMPLETE'})
            response,_=call(recovery,'disposition','astra','The original review failed and has now been retried once. Record response and next action only; do not dispatch.\n'+original+'\nFresh review:\n'+review)
            q.disposition(row['id'],response)
            result={'status':'RECOVERED_REVIEW_AND_DISPOSITION','report':row['id'],'additional_model_calls':2,'scientific_dispatches':0}
            immutable(recovery/'complete.json',encoded(result));return result
        except BaseException:
            if q.status(row['id'])['status']=='REVIEWING':q.unavailable(row['id'],retry['attempt_id'],'RETRY_FAILED_NO_FURTHER_AUTOMATIC_RETRY')
            immutable(recovery/'blocked.json',encoded({'reason':'RECONCILE_RETRY_ORIGINALS_NO_REPLAY'}));raise


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',required=True);p.add_argument('--execute-single-retry',action='store_true');p.add_argument('--source-root',required=True);p.add_argument('--source',required=True);a=p.parse_args()
    if os.getuid()!=0:raise ValueError('SUPERVISED_SETUP_REQUIRED')
    os.umask(0o077);checked_source(a.source_root,a.source)
    print(json.dumps(recover(a.folder,a.execute_single_retry)))

if __name__=='__main__':main()
