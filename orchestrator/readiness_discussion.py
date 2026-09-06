"""One bounded system discussion per completed readiness event set, never dispatch.

Run by the investigator identity with existing subscription access, separately
from the credential-free queue. No recurring loop or live admission is enabled.
"""
import argparse
import hashlib
import json
from pathlib import Path
from orchestrator.job_store import Store
from orchestrator.remote_supervisor import lock
from orchestrator.campaign_pipeline import execute


def discuss(sc,state,output,proposal):
    state=Path(state)
    with lock(state/'branch.lock'):
        q=Store(state/'readiness.sqlite')
        events=[dict(r) for r in q.db.execute('SELECT id,job,payload FROM events ORDER BY id')]
        if not events: raise ValueError('COMPLETION_REQUIRED')
        # Payloads are hash-bound metadata emitted by the fixed queue; no console,
        # image, label, prediction or raw model protocol belongs in this packet.
        packet=[]
        for event in events:
            value=json.loads(event['payload'])
            if value.get('scope')!='METADATA_ONLY_NOT_SCIENTIFIC_VALIDATION': raise ValueError('EVENT_SCOPE')
            packet.append({'event':event['id'],'source':value['binding']['source'],
                           'handler':value['binding']['handler'],'facts':value['facts'],
                           'completed_at':value['finished']})
        from orchestrator.public_export import text
        text(json.dumps(packet))
        identity=hashlib.sha256(json.dumps(events,sort_keys=True).encode()).hexdigest()
        q.db.execute('CREATE TABLE IF NOT EXISTS readiness_discussions(id TEXT PRIMARY KEY,status TEXT,output TEXT)')
        prior=q.db.execute('SELECT status,output FROM readiness_discussions WHERE id=?',(identity,)).fetchone()
        if prior:
            return {'identity':identity,'status':prior['status'],'output':prior['output'],'duplicate':True,'model_calls':0}
        q.db.execute('INSERT INTO readiness_discussions VALUES(?,?,?)',(identity,'CLAIMED_RECONCILE_IF_INTERRUPTED',str(output)))
        request=('Process these actual completed readiness events through the system. Recommend the next eligible bounded task and explain priorities toward Wednesday. Distinguish metadata inventories from scientific results. Preserve pending charter ratification, patient launch, 047 landing and unattended activation. No execution, import or adoption. Include the relevant predecessor conclusions only when evidence gates pass. This is a proposed investigator disposition, not operator approval.\n'+json.dumps(packet)+'\nDecision inbox:\n'+json.dumps(q.inbox()))
        try:
            result=execute(sc,'discuss','P001',request,output,proposal=proposal)
        except BaseException:
            q.db.execute("UPDATE readiness_discussions SET status='BLOCKED_RECONCILE_NO_AUTOMATIC_RETRY' WHERE id=?",(identity,))
            raise
        q.db.execute("UPDATE readiness_discussions SET status='REVIEWED_PROPOSAL_NOT_DISPATCHED' WHERE id=?",(identity,))
        return {'identity':identity,'status':'REVIEWED_PROPOSAL_NOT_DISPATCHED','output':str(output),'duplicate':False,'review_status':result['status']}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--proposal',required=True)
    a=p.parse_args();import scout
    print(json.dumps(discuss(scout,a.state,a.output,a.proposal)))
