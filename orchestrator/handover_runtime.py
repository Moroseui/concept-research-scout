"""Non-root handover service and human CLI over the shared coordinator.

Installed configuration is root-owned; operator requests are root-owned files,
not phone comments or caller-asserted roles. Live activation remains separate.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import socket
import stat

from orchestrator.handover_coordinator import Coordinator,encoded,digest
from orchestrator.operations_report import finalize,Queue,immutable
from orchestrator.remote_supervisor import checked_source
from orchestrator.public_export import text


def configuration(path):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        info=os.fstat(fd)
        if info.st_uid!=0 or info.st_mode & 0o022 or not stat.S_ISREG(info.st_mode) or info.st_size>65536:raise ValueError('INSTALLED_CONFIG_REQUIRED')
        return json.loads(os.read(fd,65536))
    finally:os.close(fd)


def request_broker(path,operation,body):
    raw=encoded({'operation':operation,'body':body});text(raw.decode(),limit=1500000)
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as client:
        client.settimeout(300);client.connect(path);client.sendall(raw)
        result=b''
        while not result.endswith(b'\n'):
            chunk=client.recv(65536)
            if not chunk or len(result)+len(chunk)>1500000:raise ValueError('BROKER_RESPONSE_UNAVAILABLE')
            result+=chunk
    value=json.loads(result)
    if value.get('status')=='REFUSED':raise ValueError('BROKER_REFUSED_RECONCILE')
    return value


class Runtime:
    def __init__(self,config):
        self.config=config
        self.root=checked_source(config['source_root'],config['source'])
        if os.getuid()!=config['controller_uid']:raise ValueError('NONROOT_CONTROLLER_IDENTITY_REQUIRED')
        self.state=Path(config['state'])
        self.q=Coordinator(self.state,{'continuation':self.model,'review':self.model,'disposition':self.model},self.admit,self.validate_binding)
        self.q.db.executescript('''
            CREATE TABLE IF NOT EXISTS bookkeeping(task TEXT PRIMARY KEY,status TEXT,attempts INTEGER,reason TEXT);
            CREATE TABLE IF NOT EXISTS control_delivery(id TEXT PRIMARY KEY,outcome TEXT);
            CREATE TABLE IF NOT EXISTS runtime_blocks(phase TEXT PRIMARY KEY,reason TEXT);
        ''')
        self.completions=None
        if config.get('synthetic_execution') is not None:
            from orchestrator.completion_bridge import CompletionBridge
            self.completions=CompletionBridge(self,config['synthetic_execution'])

    @staticmethod
    def validate_binding(binding):
        if binding['stages']!=['continuation','review','disposition']:
            raise ValueError('CANONICAL_REPORT_STAGES_REQUIRED')

    def event(self,binding):
        return {'turn_id':binding['id'],'attempt':'1','source':binding['source'],
                'branch':'astra/infrastructure-milestone-record','kind':binding['kind']}

    def admit(self,binding):
        return request_broker(self.config['broker_socket'],'admit_server',self.event(binding))

    def model(self,binding,position):
        task_root=self.state/'tasks'/binding['id']
        raw=(task_root/'packet.json').read_bytes();packet=json.loads(raw)
        # Task ID includes the complete immutable packet, source, and report identity.
        expected=digest({'source':binding['source'],'packet':packet,'report':json.loads((task_root/'report.json').read_text())})
        if expected!=binding['id']:raise ValueError('TASK_PACKET_CHANGED')
        report=json.loads((task_root/'report.json').read_text())
        report_root=self.state/'reports'
        report_text=(report_root/(report['id']+'.md')).read_text()
        if hashlib.sha256(report_text.encode()).hexdigest()!=report['id']:raise ValueError('REPORT_CHANGED')
        self.validate_binding(binding)
        stage=binding['stages'][position]
        prompt={'continuation':'Assess this report against approved goals, identify the next eligible task and limits. Do not execute or grant authority.',
                'review':'Fresh Claude primary-evidence review under the supplied directive. Assess science, implementation and human operation; distinguish verified evidence and missing proof. Do not infer nonexistent evidence from omission.',
                'disposition':'Record Astra disposition of the existing fresh review and the next eligible bounded task. No execution or ratification.'}[stage]
        proposal=packet.get('execution_proposal')
        if proposal is not None:
            prompt+=' The installed supervised configuration offers exactly one synthetic successor; review its eligibility and boundaries.'
            if stage=='disposition':
                prompt=('Record your response to the fresh review and select the configured synthetic successor. '
                        'Return exactly one JSON object with task_id equal to '+proposal['job']+
                        ' and reason containing your review disposition and rationale; if a blocking concern remains, '
                        'use task_id null and explain it in reason. The system validates the selection '
                        'before submission. Do not select patient work, a different job or a new scope.')
        prompt+='\nREPORT:\n'+report_text+'\nPRIMARY EVIDENCE:\n'+json.dumps(packet)
        for previous in ['continuation','review'][:position]:
            prior=self.q._receipt(binding['id'],['continuation','review'].index(previous),binding)
            if prior is None:raise ValueError('PREDECESSOR_RECEIPT_REQUIRED')
            prompt+='\n'+previous.upper()+':\n'+prior['output']['answer']
        response=request_broker(self.config['broker_socket'],'model_stage',{'event':self.event(binding),'stage':stage,'packet':packet,'prompt':prompt})
        if response.get('status')!='COMPLETE':raise ValueError('MODEL_COMPLETION_REQUIRED')
        return response

    def enqueue_report(self,day,receipts,task_state,reviewer_evidence=None,execution_proposal=None,trigger='scheduled-report'):
        if trigger not in ('scheduled-report','verified-completion'):raise ValueError('REPORT_TRIGGER_REQUIRED')
        finalized=finalize(self.state/'reports',self.config['source'],day,receipts,task_state=task_state)
        report={'id':finalized['id']}
        packet={'jobs':receipts,'trigger':trigger,'decision_inbox':task_state}
        if reviewer_evidence is not None:packet['reviewer_evidence']=reviewer_evidence
        if execution_proposal is not None:packet['execution_proposal']=execution_proposal
        identity=digest({'source':self.config['source'],'packet':packet,'report':report})
        directory=self.state/'tasks'/identity;directory.mkdir(parents=True,mode=0o700,exist_ok=True)
        immutable(directory/'packet.json',encoded(packet));immutable(directory/'report.json',encoded(report))
        return {'id':identity,'source':self.config['source'],'kind':'nightly_review','thread':'adjacent',
                'dependencies':[],'stages':['continuation','review','disposition']}

    def bookkeeping(self):
        # Capped, per-task finalization. Completed or blocked entries do not rescan
        # model artifacts forever; scientific/model execution is never retried here.
        rows=self.q.db.execute("""SELECT t.id FROM tasks t LEFT JOIN bookkeeping b ON t.id=b.task
            WHERE t.status='COMPLETE' AND (b.status IS NULL OR b.status='RETRY') LIMIT 32""").fetchall()
        for row in rows:
            prior=self.q.db.execute('SELECT attempts FROM bookkeeping WHERE task=?',(row['id'],)).fetchone()
            attempt=(prior[0] if prior else 0)+1
            try:
                self._bookkeep(row)
                status,reason='COMPLETE',None
            except (ValueError,KeyError,TypeError,OSError):
                status='BLOCKED' if attempt>=3 else 'RETRY'
                reason='BOOKKEEPING_EVIDENCE_PRESERVED'
                # A failed attachment must not leave a claimed review pretending
                # it is still running. Preserve its actual original review files.
                try:
                    report=json.loads((self.state/'tasks'/row['id']/'report.json').read_text())
                    queue=Queue(self.state/'reports');claim=queue.status(report['id'])
                    if claim['status']=='REVIEWING':queue.unavailable(report['id'],claim['attempt_id'],'bookkeeping-preserved')
                except (ValueError,KeyError,TypeError,OSError):pass
            self.q.db.execute('INSERT OR REPLACE INTO bookkeeping VALUES(?,?,?,?)',(row['id'],status,attempt,reason))

    def _bookkeep(self,row):
        folder=self.state/'tasks'/row['id'];report=json.loads((folder/'report.json').read_text())
        queue=Queue(self.state/'reports');status=queue.status(report['id'])
        binding=json.loads(self.q.db.execute('SELECT binding FROM tasks WHERE id=?',(row['id'],)).fetchone()[0])
        review=self.q._receipt(row['id'],1,binding)['output']
        if status['status']!='REVIEWED':
            claim=status if status['status']=='REVIEWING' else queue.claim(report['id'])
            if not claim:raise ValueError('REVIEW_BOOKKEEPING_CLAIM_REQUIRED')
            r=review['receipt'];answer=review['answer']
            queue.attach(report['id'],claim['attempt_id'],answer,{'family':'claude','model':r['actual_model'],'source':self.config['source'],
                'report_sha256':report['id'],'review_sha256':hashlib.sha256(answer.encode()).hexdigest(),
                'execution_receipt_sha256':hashlib.sha256((json.dumps(r,sort_keys=True,indent=2)+'\n').encode()).hexdigest(),
                'session_id':r['session_id'],'status':'COMPLETE'})
        disposition=self.q._receipt(row['id'],2,binding)['output']['answer']
        queue.disposition(report['id'],disposition)
        if self.completions is not None:
            self.completions.finish(row['id'],json.loads((folder/'packet.json').read_text()),disposition)


    def controls(self):
        results=[]
        directory=Path(self.config['control_inbox'])
        if directory.is_symlink() or directory.stat().st_uid!=0 or directory.stat().st_mode & 0o022:
            raise ValueError('PROTECTED_CONTROL_INBOX')
        for path in sorted(directory.glob('*.json')):
            if len(path.stem)!=64 or any(c not in '0123456789abcdef' for c in path.stem):
                continue
            receipt=self.state/('control-'+path.stem+'.json')
            if self.q.db.execute('SELECT 1 FROM control_delivery WHERE id=?',(path.stem,)).fetchone():continue
            try:
                request=configuration(path)
                if set(request)!={'source','control'} or request['source']!=self.config['source']:
                    raise ValueError('STALE_CONTROL_SOURCE')
                result=self.q.control(request['control'],authenticated_operator=True)
                outcome={'status':'APPLIED','request':path.stem,'revision':result['revision']}
            except (ValueError,KeyError,TypeError,OSError):
                outcome={'status':'BLOCKED','request':path.stem,
                    'reason':'CONTROL_INVALID_OR_STALE','next_action':'Submit a new operator request bound to current source and control revision.'}
            try:immutable(receipt,encoded(outcome))
            except (ValueError,OSError):
                outcome={**outcome,'receipt_status':'WRITE_BLOCKED','next_action':'Preserve the SQLite control record and repair the receipt destination.'}
            self.q.db.execute('INSERT OR IGNORE INTO control_delivery VALUES(?,?)',(path.stem,encoded(outcome).decode()))
            results.append(outcome)
        return results

    def scheduled_report(self,now):
        """Explicit installed schedule; deterministic polling spends no model call."""
        from zoneinfo import ZoneInfo
        schedule=self.config.get('report_schedule')
        if schedule is None:return {'status':'SCHEDULE_DISABLED'}
        if set(schedule)!={'zone','hour','minute','evidence_file'}:raise ValueError('SCHEDULE_SCHEMA')
        local=now.astimezone(ZoneInfo(schedule['zone']))
        if (local.hour,local.minute)<(schedule['hour'],schedule['minute']):return {'status':'NOT_DUE'}
        day=local.date().isoformat()
        prior=self.q.db.execute('SELECT task FROM schedules WHERE day=?',(day,)).fetchone()
        if prior:return {'status':'ALREADY_SCHEDULED','task':prior[0]}
        evidence=configuration(schedule['evidence_file'])
        if set(evidence) not in ({'source','receipts','task_state'},{'source','receipts','task_state','reviewer_evidence'}) or evidence['source']!=self.config['source']:raise ValueError('REPORT_EVIDENCE_SOURCE')
        # Installed evidence is a supplied snapshot, not a live queue census.
        # Capture current coordinator state in the same transaction used for
        # daily identity creation. Never read prompts or private job payloads.
        self.q.db.execute('BEGIN IMMEDIATE')
        try:
            state=self.q.status()
            task_state=dict(evidence['task_state'])
            task_state['coordinator_observed_at']=now.isoformat()
            priority={'RUNNING':0,'BLOCKED':1,'QUEUED':2,'COMPLETE':3}
            selected=sorted(state['tasks'],key=lambda row:(priority.get(row['status'],4),row['id']))[:24]
            task_state['coordinator_tasks']=[{**row,'reason':row['reason'] if row['reason'] is None or len(row['reason'])<=256
                else 'REASON_TOO_LONG_SEE_PRIVATE_TASK_RECORD'} for row in selected]
            task_state['coordinator_tasks_total']=len(state['tasks'])
            task_state['coordinator_tasks_omitted']=len(state['tasks'])-len(selected)
            task_state['coordinator_control']={'revision':state['revision'],'paused':bool(state['paused'])}
            task_state['evidence_scope']='Installed evidence plus current coordinator metadata; not a census of other execution queues.'
            task_state['coordinator_summary']=', '.join(
                str(sum(row['status']==status for row in state['tasks']))+' '+status.lower()
                for status in ('QUEUED','RUNNING','COMPLETE','BLOCKED'))
            if self.completions is not None:
                task_state['completion_blocks']=[dict(row) for row in self.q.db.execute('SELECT * FROM completion_blocks')]
                task_state['selected_work']=[dict(row) for row in self.q.db.execute('SELECT task,status,attempts FROM selected_dispatch')]
            binding=self.enqueue_report(day,evidence['receipts'],task_state,evidence.get('reviewer_evidence'))
        finally:
            self.q.db.execute('ROLLBACK')
        # schedule owns its transaction. Concurrent callers converge on the
        # already-persisted day; an unused immutable snapshot grants no authority.
        return self.q.schedule(now,schedule['zone'],schedule['hour'],schedule['minute'],binding)

    def recover(self):
        outcomes=[]
        def retrieve(binding,position):
            return request_broker(self.config['broker_socket'],'stage_status',
                {'event':self.event(binding),'stage':binding['stages'][position]})
        for row in self.q.status()['tasks']:
            if row['status'] in ('BLOCKED','RUNNING'):
                try:outcomes.append(self.q.recover(row['id'],retrieve))
                except (ValueError,KeyError,TypeError,OSError):
                    self.q.db.execute("UPDATE tasks SET status='BLOCKED',reason='RECOVERY_EVIDENCE_UNAVAILABLE' WHERE id=?",(row['id'],))
        return outcomes

    def tick(self):
        for name,operation in [('controls',self.controls),('recovery',self.recover),
                               ('completions',lambda:self.completions.ingest() if self.completions else None),
                               ('selected-work',lambda:self.completions.advance() if self.completions else None),
                               ('schedule',lambda:self.scheduled_report(datetime.now(timezone.utc)))]:
            try:
                operation()
                self.q.db.execute('DELETE FROM runtime_blocks WHERE phase=?',(name,))
            except (ValueError,KeyError,TypeError,OSError):
                self.q.db.execute('INSERT OR REPLACE INTO runtime_blocks VALUES(?,?)',(name,'EVIDENCE_OR_CONFIGURATION_REQUIRES_RECONCILIATION'))
        control_block=self.q.db.execute("SELECT 1 FROM runtime_blocks WHERE phase='controls'").fetchone()
        result={'status':'CONTROL_TRANSPORT_BLOCKED'} if control_block else self.q.tick()
        self.bookkeeping()
        return result

    def status(self):
        return {**self.q.status(),
                'completion_events':[] if self.completions is None else [dict(row) for row in self.q.db.execute('SELECT * FROM completion_ingest')],
                'selected_work':[] if self.completions is None else [dict(row) for row in self.q.db.execute('SELECT task,status,attempts FROM selected_dispatch')],
                'completion_blocks':[] if self.completions is None else [dict(row) for row in self.q.db.execute('SELECT * FROM completion_blocks')],
                'runtime_blocks':[dict(row) for row in self.q.db.execute('SELECT * FROM runtime_blocks')],
                'bookkeeping':[dict(row) for row in self.q.db.execute('SELECT * FROM bookkeeping')],
                'controls':[json.loads(row[0]) for row in self.q.db.execute('SELECT outcome FROM control_delivery')]}


def operator_request(config,action,revision,request_id):
    if os.getuid()!=0:raise ValueError('OPERATOR_ADMIN_REQUIRED')
    directory=Path(config['control_inbox'])
    if directory.is_symlink() or directory.stat().st_uid!=0 or directory.stat().st_mode & 0o022:raise ValueError('PROTECTED_CONTROL_INBOX')
    request={'source':config['source'],'control':{'id':request_id,'expected_revision':revision,'action':action}}
    # Numeric/hash-derived filename; no user-controlled traversal.
    path=directory/(digest(request)+'.json')
    immutable(path,encoded(request));os.chown(path,0,config['controller_gid']);os.chmod(path,0o640)
    return {'status':'REQUESTED_NOT_YET_APPLIED','request':digest(request)}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True)
    p.add_argument('operation',choices=['tick','status','controls','pause','resume'])
    p.add_argument('--revision',type=int);p.add_argument('--request-id')
    a=p.parse_args();config=configuration(a.config)
    if a.operation in ('pause','resume'):
        if a.revision is None or not a.request_id:p.error('pause/resume require --revision and --request-id')
        result=operator_request(config,a.operation,a.revision,a.request_id)
    else:
        runtime=Runtime(config)
        result=runtime.status() if a.operation=='status' else (runtime.tick() if a.operation=='tick' else runtime.controls())
    print(text(json.dumps(result)))


if __name__=='__main__':main()
