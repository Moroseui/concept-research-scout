#!/usr/bin/env python3
"""Fresh, supervised hosted orientation/report/review/disposition. No job dispatch."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from orchestrator.hosted_cycle import model_call,immutable,encoded,claim
from orchestrator.remote_supervisor import checked_source,lock
from orchestrator.operations_report import finalize,Queue


def run(root,source,state,destination):
    if os.getuid()!=0:raise ValueError('BOUNDED_SETUP_TRANSPORT_REQUIRED')
    root=checked_source(root,source);state=Path(state);destination=Path(destination)
    if root!=Path(__file__).resolve().parents[2]:raise ValueError('EXECUTING_SOURCE_MISMATCH')
    # Read WAL state as its owner, preserving the existing consistent-snapshot route.
    script="""import sqlite3,json,sys,os
c=sqlite3.connect('file:'+sys.argv[1]+'?mode=ro',uri=True);c.row_factory=sqlite3.Row;c.execute('BEGIN')
print(json.dumps({'reader_uid':os.getuid(),**{t:[dict(r) for r in c.execute('SELECT * FROM '+t+' ORDER BY 1')] for t in ['jobs','events','inbox']}}))
"""
    raw=subprocess.check_output(['runuser','-u','research-controller','--','python3','-c',script,str(state/'readiness.sqlite')],timeout=30)
    snapshot=json.loads(raw)
    if len(snapshot['events'])!=4 or any(r['status'] not in ('COMPLETE','BLOCKED') for r in snapshot['jobs']):raise ValueError('READINESS_NOT_COMPLETE_RECONCILE')
    for row in snapshot['events']:
        p=state/row['job']/'result.json'
        if p.is_symlink() or json.loads(p.read_text())!=json.loads(row['payload']):raise ValueError('PRIMARY_RESULT_CHANGED')
    event_hash=hashlib.sha256(encoded(snapshot['events'])).hexdigest()
    destination.mkdir(mode=0o700,parents=True,exist_ok=True)
    with lock(destination/'driver.lock'):
        folder=destination/event_hash
        binding={'source':source,'completion_event_set_sha256':event_hash,'maximum_model_calls':3,'patient':False,'standing_activation':False}
        if not claim(folder,binding):return json.loads((folder/'complete.json').read_text())
        packet={'jobs':[{'job_id':r['id'],'status':r['status'],'source':json.loads(r['binding'])['source'],'kind':'readiness_metadata','backend':'linux'} for r in snapshot['jobs']],
                'trigger':{'completion_event_set_sha256':event_hash},'verified_events':snapshot['events'],'decision_inbox':snapshot['inbox'],
                'implementation':{n:(root/n).read_text() for n in ['orchestrator/hosted_context.py','orchestrator/readiness_queue.py','deploy/research-system/operating_context_acceptance.py']},
                'deployed_evidence':json.loads((root/'docs/operations/READINESS_HOSTED_ACCEPTANCE_20260906.json').read_text())}
        immutable(folder/'packet.json',encoded(packet))
        orientation,receipt=model_call(folder,'continuation','astra',
            'This is a fresh hosted investigator session with no laptop conversation. Identify your research objective, the next eligible bounded system task and authority limits from the supplied operating context. Return exactly JSON keys objective (string), next_eligible_task (string), authority_limits (nonempty array of strings), patient_launch_authorized (false), prediction_charter_ratified (false), unattended_activation_authorized (false). Propose no execution. Actual completed readiness evidence:\n'+json.dumps(packet),output_format='json')
        answer=json.loads(orientation)
        if set(answer)!={'objective','next_eligible_task','authority_limits','patient_launch_authorized','prediction_charter_ratified','unattended_activation_authorized'} or any(answer[k] is not False for k in ['patient_launch_authorized','prediction_charter_ratified','unattended_activation_authorized']):raise ValueError('ORIENTATION_AUTHORITY_MISMATCH')
        if any(not isinstance(answer[k],str) or not answer[k].strip() for k in ['objective','next_eligible_task']) or not isinstance(answer['authority_limits'],list) or not answer['authority_limits']:raise ValueError('ORIENTATION_MISSING')
        report=finalize(folder/'reports',source,'2026-09-06',packet['jobs']);q=Queue(folder/'reports');review_claim=q.claim(report['id'])
        body=(folder/'reports'/(report['id']+'.md')).read_text()
        review,r=model_call(folder,'review','claude','Fresh primary-evidence review: assess whether this new hosted session identified the approved scientific objective, an actually eligible next system task and authority limits without laptop context. Inspect supplied implementation and actual hosted evidence; qualify unproven sandbox/resource properties. Check scientific direction, evidence propagation and pending gates, not just software quality. No ratification or launch authority.\n'+json.dumps(packet)+'\nASTRA:\n'+orientation+'\nREPORT:\n'+body)
        q.attach(report['id'],review_claim['attempt_id'],review,{'family':'claude','model':r['actual_model'],'source':source,'report_sha256':report['id'],'review_sha256':hashlib.sha256(review.encode()).hexdigest(),'execution_receipt_sha256':hashlib.sha256(encoded(r)).hexdigest(),'session_id':r['session_id'],'status':'COMPLETE'})
        response,_=model_call(folder,'disposition','astra','Record your response to the fresh review and the next eligible system action. Address findings honestly; do not dispatch or grant authority.\n'+json.dumps(packet)+'\nREVIEW:\n'+review)
        q.disposition(report['id'],response)
        result={'status':'COMPLETE',**binding,'report':report['id'],'actual_model_calls':3,'snapshot_reader_uid':snapshot['reader_uid'],'objective':answer['objective'],'next_eligible_task':answer['next_eligible_task']}
        immutable(folder/'complete.json',encoded(result));return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('root','source','state','destination'):p.add_argument('--'+name,required=True)
    a=p.parse_args();os.umask(0o077);print(json.dumps(run(**vars(a))))
