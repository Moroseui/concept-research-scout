#!/usr/bin/env python3
"""Register operator tasks in a separate Store and include them in a report.

No execution/adoption/import handler is provided; existing gates remain required.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from orchestrator.job_store import Store
from orchestrator.remote_supervisor import checked_source,Controller
from orchestrator.operations_report import finalize,Queue
from orchestrator.public_export import text

def register(state,root,source,day):
    root=checked_source(root,source);state=Path(state)
    document=json.loads((root/'docs/operations/QUEUED_SCIENTIFIC_TASKS_20260906.json').read_text())
    tasks=document['tasks']
    if {t['id'] for t in tasks}!={'isles24-prediction-charter','047b-evidence-and-lifecycle','cross-charter-evidence-propagation'}:raise ValueError('OPERATOR_TASK_SET_CHANGED')
    store=Store(state/'operator-tasks.sqlite')
    rows=[]
    for task in tasks:
        old=store.db.execute('SELECT binding FROM jobs WHERE id=?',(task['id'],)).fetchone()
        binding=json.loads(old[0]) if old else {'source':source,'operator_task':task,'execution_authorized':False}
        if binding['operator_task']!=task or binding['execution_authorized'] is not False:raise ValueError('TASK_AMENDMENT_REQUIRED')
        store.register(task['id'],binding)
        store.db.execute("UPDATE jobs SET phase='operator_task' WHERE id=? AND phase='acquisition'",(task['id'],))
        reason={'isles24-prediction-charter':'REMOTE_AUTH_SOURCE_RECOVERY_CLAUDE_ALIGNMENT_CHARTER_RATIFICATION',
                '047b-evidence-and-lifecycle':'REMOTE_AUTH_047B_IDENTITY_ORIGINAL_CONSOLE_EXCLUSIONS_REGISTRY_LANDING_GATE',
                'cross-charter-evidence-propagation':'CONTEXT_PATH_AUDIT_SOURCE_BINDINGS_PENDING_EVIDENCE_CLAUDE_REVIEW'}[task['id']]
        if store.get(task['id'])['status']=='READY':store.block(task['id'],reason)
        row=store.get(task['id'])
        reason=next((r['reason'] for r in store.inbox() if r['job']==task['id'] and r['status']=='OPEN'),None)
        rows.append({'job_id':task['id'],'source':binding['source'],'kind':'queued_scientific_task','backend':'linux','status':row['status'],'reason':reason})
    controller=Controller(state/'jobs.sqlite')
    reports=state/'reports';q=Queue(reports)
    # Deterministic supplementary report identity makes identical retries idempotent.
    report=finalize(reports,source,day,controller.status()['jobs']+rows)
    return {'task_count':len(rows),'tasks':rows,'report':report,'duplicate':False,'execution_dispatched':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--source-root',type=Path,required=True);p.add_argument('--source',required=True);p.add_argument('--day',required=True);a=p.parse_args()
    print(text(json.dumps(register(a.state,a.source_root,a.source,a.day),sort_keys=True)))
