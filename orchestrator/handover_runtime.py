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
        self.q=Coordinator(self.state,{'continuation':self.model,'review':self.model,'disposition':self.model},self.admit)

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
        stage=['continuation','review','disposition'][position]
        prompt={'continuation':'Assess this report against approved goals, identify the next eligible task and limits. Do not execute or grant authority.',
                'review':'Fresh Claude primary-evidence review under the supplied directive. Assess science, implementation and human operation; distinguish verified evidence and missing proof. Do not infer nonexistent evidence from omission.',
                'disposition':'Record Astra disposition of the existing fresh review and the next eligible bounded task. No execution or ratification.'}[stage]
        prompt+='\nREPORT:\n'+report_text+'\nPRIMARY EVIDENCE:\n'+json.dumps(packet)
        for previous in ['continuation','review'][:position]:
            prior=json.loads((self.state/(binding['id']+'-'+str(['continuation','review'].index(previous))+'.json')).read_text())
            prompt+='\n'+previous.upper()+':\n'+prior['output']['answer']
        response=request_broker(self.config['broker_socket'],'model_stage',{'event':self.event(binding),'stage':stage,'packet':packet,'prompt':prompt})
        if response.get('status')!='COMPLETE':raise ValueError('MODEL_COMPLETION_REQUIRED')
        return response

    def enqueue_report(self,day,receipts,task_state):
        finalized=finalize(self.state/'reports',self.config['source'],day,receipts)
        report={'id':finalized['id']}
        packet={'jobs':receipts,'trigger':'scheduled-report','decision_inbox':task_state}
        identity=digest({'source':self.config['source'],'packet':packet,'report':report})
        directory=self.state/'tasks'/identity;directory.mkdir(parents=True,mode=0o700,exist_ok=True)
        immutable(directory/'packet.json',encoded(packet));immutable(directory/'report.json',encoded(report))
        return {'id':identity,'source':self.config['source'],'kind':'nightly_review','thread':'adjacent',
                'dependencies':[],'stages':['continuation','review','disposition']}

    def bookkeeping(self):
        # Resume artifact attachment after model success without another model call.
        for row in self.q.status()['tasks']:
            if row['status']!='COMPLETE':continue
            folder=self.state/'tasks'/row['id'];report=json.loads((folder/'report.json').read_text())
            queue=Queue(self.state/'reports');status=queue.status(report['id'])
            review=json.loads((self.state/(row['id']+'-1.json')).read_text())['output']
            if status['status']!='REVIEWED':
                claim=status if status['status']=='REVIEWING' else queue.claim(report['id'])
                if not claim:raise ValueError('REVIEW_BOOKKEEPING_CLAIM_REQUIRED')
                r=review['receipt'];answer=review['answer']
                queue.attach(report['id'],claim['attempt_id'],answer,{'family':'claude','model':r['actual_model'],'source':self.config['source'],
                    'report_sha256':report['id'],'review_sha256':hashlib.sha256(answer.encode()).hexdigest(),
                    'execution_receipt_sha256':hashlib.sha256((json.dumps(r,sort_keys=True,indent=2)+'\n').encode()).hexdigest(),
                    'session_id':r['session_id'],'status':'COMPLETE'})
            disposition=json.loads((self.state/(row['id']+'-2.json')).read_text())['output']['answer']
            queue.disposition(report['id'],disposition)

    def controls(self):
        results=[]
        directory=Path(self.config['control_inbox'])
        if directory.is_symlink() or directory.stat().st_uid!=0 or directory.stat().st_mode & 0o022:
            raise ValueError('PROTECTED_CONTROL_INBOX')
        for path in sorted(directory.glob('*.json')):
            if len(path.stem)!=64 or any(c not in '0123456789abcdef' for c in path.stem):
                continue
            receipt=self.state/('control-'+path.stem+'.json')
            if receipt.exists():continue
            try:
                request=configuration(path)
                if set(request)!={'source','control'} or request['source']!=self.config['source']:
                    raise ValueError('STALE_CONTROL_SOURCE')
                result=self.q.control(request['control'],authenticated_operator=True)
                outcome={'status':'APPLIED','request':path.stem,'revision':result['revision']}
            except (ValueError,KeyError,TypeError,OSError):
                outcome={'status':'BLOCKED','request':path.stem,
                    'reason':'CONTROL_INVALID_OR_STALE','next_action':'Submit a new operator request bound to current source and control revision.'}
            immutable(receipt,encoded(outcome));results.append(outcome)
        return results

    def recover(self):
        outcomes=[]
        def retrieve(binding,position):
            return request_broker(self.config['broker_socket'],'stage_status',
                {'event':self.event(binding),'stage':binding['stages'][position]})
        for row in self.q.status()['tasks']:
            if row['status'] in ('BLOCKED','RUNNING'):
                outcomes.append(self.q.recover(row['id'],retrieve))
        return outcomes

    def tick(self):
        self.controls()
        self.recover()
        result=self.q.tick();self.bookkeeping()
        return result


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
        result=runtime.q.status() if a.operation=='status' else (runtime.tick() if a.operation=='tick' else runtime.controls())
    print(text(json.dumps(result)))


if __name__=='__main__':main()
