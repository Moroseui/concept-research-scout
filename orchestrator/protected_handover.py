"""Narrow OS-authenticated handover broker. No live grant is bundled here.

Protected service configuration/checkout/ledger/key ownership is the security
boundary. Scientific and model users must not own these paths or service code.
Remote Git credentials remain exclusively in the protected publisher identity.
"""
import argparse
from contextlib import nullcontext
import json
import hashlib
import fcntl
import os
from pathlib import Path
import socket
import struct

from orchestrator.dispatch_limiter import GitLedger,admit_server,admit,reset,initialize,policy,validate_server_event
from orchestrator.git_publication import publish,scan
from orchestrator.phone_notifications import protected_read

REPOSITORY='https://github.com/Moroseui/concept-research-scout.git'
BRANCH='astra/infrastructure-milestone-record'


class Broker:
    def __init__(self,config):
        required={'mode','repository','branch','controller_uid','operator_uids','sources','ledger_repo','publication_root','policy','writer_config','model_mode','turn_root','max_model_turns'}
        if set(config)!=required or config['mode'] not in ('SYNTHETIC_FIXTURE','LIVE_APPROVED') or config['repository']!=REPOSITORY or config['branch']!=BRANCH:raise ValueError('PROTECTED_CONFIG_SCHEMA')
        if type(config['controller_uid']) is not int or config['controller_uid']<=0 or not config['operator_uids'] or config['controller_uid'] in config['operator_uids']:raise ValueError('DISTINCT_OPERATOR_REQUIRED')
        if config['model_mode'] not in ('DISABLED','SUPERVISED') or type(config['max_model_turns']) is not int or not 0<=config['max_model_turns']<=4:raise ValueError('BOUNDED_MODEL_CONFIGURATION')
        if not isinstance(config['sources'],list) or not config['sources'] or len(config['sources'])>16:raise ValueError('BOUNDED_REVIEWED_SOURCES')
        import re
        if any(not isinstance(pin,str) or not re.fullmatch('[0-9a-f]{40}',pin) for pin in config['sources']):raise ValueError('REVIEWED_SOURCE_REQUIRED')
        self.config=config
        self.ledger=GitLedger(config['ledger_repo'],remote=config['mode']=='LIVE_APPROVED',expected_remote=REPOSITORY)

    def authentication(self):
        if self.config['mode']=='SYNTHETIC_FIXTURE':return nullcontext()
        from orchestrator.protected_writer import credentials
        return credentials(json.loads(protected_read(self.config['writer_config'])))

    def handle(self,request,peer_uid):
        if not isinstance(request,dict) or set(request)!={'operation','body'}:raise ValueError('BROKER_REQUEST_SCHEMA')
        if peer_uid!=self.config['controller_uid']:raise ValueError('BROKER_PEER_REFUSED')
        op=request['operation'];body=request['body']
        if not isinstance(body,dict):raise ValueError('BROKER_BODY_SCHEMA')
        if op=='status':
            if body!={}:raise ValueError('STATUS_BODY')
            with self.authentication():pin,state=self.ledger.read()
            return {'mode':self.config['mode'],'pin':pin,'sequence':state['sequence'],'count':state['count'],'halted':state['halted'],'day':state['day']}
        if op=='admit_server':
            if body.get('source') not in self.config['sources']:raise ValueError('REVIEWED_SOURCE_REQUIRED')
            with self.authentication():return admit_server(self.ledger,self.config['policy'],body)
        if op=='stage_status':return self.stage_status(body)
        if op=='model_stage':return self.model_stage(body)
        if op=='publish':
            if self.config['mode']!='LIVE_APPROVED':raise ValueError('LIVE_PUBLICATION_NOT_AUTHORIZED')
            policy(self.config['policy'])
            if body.get('source') not in self.config['sources']:raise ValueError('REVIEWED_SOURCE_REQUIRED')
            if body.get('destination')!=BRANCH or body.get('remote')!=REPOSITORY:raise ValueError('PUBLICATION_DESTINATION_REFUSED')
            keys={'operation','source','audit_baseline','baseline_ref','destination','remote','expected_destination'} if body.get('operation')=='create' else {'source','before','destination','remote'}
            if set(body)!=keys|{'inventory'}:raise ValueError('PUBLICATION_SCHEMA')
            # Checkout is a fixed protected import/cache path, never a request path.
            with self.authentication():return publish(Path(self.config['publication_root']),body,{k:body[k] for k in keys})
        raise ValueError('BROKER_OPERATION_REFUSED')

    def model_stage(self,body):
        from orchestrator.hosted_cycle import model_call,immutable,encoded
        from orchestrator.operations_report import private_root
        if self.config['model_mode']!='SUPERVISED' or os.getuid()!=0:raise ValueError('SUPERVISED_ROLE_LAUNCHER_REQUIRED')
        if set(body)!={'event','stage','packet','prompt'}:raise ValueError('MODEL_STAGE_SCHEMA')
        event=body['event'];stage=body['stage']
        validate_server_event(event)
        stages=['continuation','review','disposition']
        if stage not in stages or event.get('source') not in self.config['sources']:raise ValueError('MODEL_STAGE_SOURCE')
        scan('model-stage-request.json',json.dumps(body).encode())
        # Validate identity before forming a path, even if admission is unavailable.
        import re
        if not re.fullmatch('[0-9a-f]{64}',event.get('turn_id','')) or not re.fullmatch('[1-9][0-9]*',event.get('attempt','')):raise ValueError('TURN_ID')
        from orchestrator.remote_supervisor import checked_source
        checked_source(Path(__file__).resolve().parents[1],event['source'])
        root=private_root(self.config['turn_root'])
        with (root/'branch.lock').open('a') as gate:
            try:fcntl.flock(gate,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise ValueError('MODEL_WRITER_BUSY')
            folder=root/(event['turn_id']+'-'+event['attempt'])
            binding={'event':event,'packet_sha256':hashlib.sha256(encoded(body['packet'])).hexdigest()}
            if not folder.exists():
                if len(list(root.glob('*/binding.json')))>=self.config['max_model_turns']:raise ValueError('SUPERVISED_MODEL_BUDGET_EXHAUSTED')
                folder.mkdir(mode=0o700)
                immutable(folder/'binding.json',encoded(binding))
                immutable(folder/'packet.json',encoded(body['packet']))
            if folder.is_symlink() or json.loads((folder/'binding.json').read_text())!=binding:raise ValueError('TURN_BINDING_CHANGED')
            immutable(folder/(stage+'.request.json'),encoded({'prompt_sha256':hashlib.sha256(body['prompt'].encode()).hexdigest()}))
            receipt_path=folder/(stage+'.receipt.json')
            if receipt_path.exists():return self.stage_status({'event':event,'stage':stage})
            if (folder/(stage+'.started.json')).exists():raise ValueError('UNCERTAIN_MODEL_RECONCILE_NO_RETRY')
            for prior in stages[:stages.index(stage)]:
                if self.stage_status({'event':event,'stage':prior})['status']!='COMPLETE':raise ValueError('PREDECESSOR_MODEL_RECEIPT_REQUIRED')
            with self.authentication():admission=admit_server(self.ledger,self.config['policy'],event)
            if admission['status']!='ADMITTED':return admission
            family='claude' if stage=='review' else 'astra'
            answer,receipt=model_call(folder,stage,family,body['prompt'])
            return {'status':'COMPLETE','duplicate':False,'answer':answer,'receipt':receipt}

    def stage_status(self,body):
        """Retrieve original completion only. This path cannot invoke a model."""
        if set(body)!={'event','stage'}:raise ValueError('STAGE_STATUS_SCHEMA')
        event=body['event'];stage=body['stage'];validate_server_event(event)
        if stage not in ('continuation','review','disposition') or event['source'] not in self.config['sources']:raise ValueError('MODEL_STAGE_SOURCE')
        folder=Path(self.config['turn_root'])/(event['turn_id']+'-'+event['attempt'])
        if folder.is_symlink():raise ValueError('TURN_BINDING_CHANGED')
        if not folder.exists():return {'status':'NOT_OBSERVED_NO_RETRY'}
        binding_path=folder/'binding.json'
        if binding_path.is_symlink() or json.loads(binding_path.read_text())['event']!=event:raise ValueError('TURN_BINDING_CHANGED')
        path=folder/(stage+'.receipt.json')
        if not path.exists():
            status='UNCERTAIN_MODEL_RECONCILE_NO_RETRY' if (folder/(stage+'.started.json')).exists() else 'NOT_STARTED_RECONCILIATION_REQUIRED'
            return {'status':status}
        if path.is_symlink():raise ValueError('MODEL_RECEIPT_CHANGED')
        receipt=json.loads(path.read_text())
        for suffix,key in [('.stdout','stdout_sha256'),('.stderr','stderr_sha256'),('.input.md','input_sha256'),('.md','answer_sha256'),('.operating-context.json','operating_context_sha256')]:
            file=folder/(stage+suffix)
            if file.is_symlink() or hashlib.sha256(file.read_bytes()).hexdigest()!=receipt[key]:raise ValueError('MODEL_RECEIPT_CHANGED')
        return {'status':'COMPLETE','duplicate':True,'answer':(folder/(stage+'.md')).read_text(),'receipt':receipt}

    def actions_admission(self,artifact,verified_run):
        # Trusted Actions API collector supplies verified_run; requester JSON does
        # not establish repo/run provenance. No run text or artifact is executed.
        required={'repository_id','run_id','attempt','source','branch','workflow_sha256'}
        if set(artifact)!=required or artifact!=verified_run:raise ValueError('ACTIONS_PROVENANCE_REQUIRED')
        if artifact['repository_id']!=1323461276 or artifact['source'] not in self.config['sources']:raise ValueError('ACTIONS_SOURCE_REFUSED')
        with self.authentication():return admit(self.ledger,self.config['policy'],{k:artifact[k] for k in ('run_id','attempt','source','branch')})

    def operator(self,operation,body):
        uid=os.getuid()
        if uid not in self.config['operator_uids']:raise ValueError('OPERATOR_OS_IDENTITY_REQUIRED')
        actor='ssh-uid:'+str(uid)
        if operation=='reset':
            if set(body)!={'expected_sequence','decision_ref','policy_sha256'}:raise ValueError('RESET_SCHEMA')
            if body['policy_sha256']!=hashlib.sha256(json.dumps(self.config['policy'],sort_keys=True).encode()).hexdigest():raise ValueError('RESET_POLICY_MOVED')
            with self.authentication():return reset(self.ledger,self.config['policy'],{'actor':actor,'role':'operator','expected_sequence':body['expected_sequence'],'decision_ref':body['decision_ref']})
        if operation=='initialize':
            if set(body)!={'decision_ref'}:raise ValueError('INITIALIZE_SCHEMA')
            self.ledger.allow_initialization=True
            with self.authentication():return initialize(self.ledger,self.config['policy'],{'actor':actor,'role':'operator',**body})
        raise ValueError('OPERATOR_OPERATION_REFUSED')


def exchange(broker,connection):
    """One bounded request; a disconnected client must not kill the broker."""
    try:
        connection.settimeout(10)
        _,uid,_=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
        raw=b''
        while b'\n' not in raw and len(raw)<=1500000:
            data=connection.recv(65536)
            if not data:break
            raw+=data
        if len(raw)>1500000 or not raw.endswith(b'\n') or raw.count(b'\n')!=1:raise ValueError('BOUNDED_REQUEST_REQUIRED')
        request=json.loads(raw);scan('broker-request.json',raw)
        response=broker.handle(request,uid)
        value=json.dumps(response).encode();scan('broker-response.json',value)
    except Exception as error:
        # Never echo request data or arbitrary exception text. Named codes only.
        import re
        reason=str(error)
        if not re.fullmatch('[A-Z][A-Z0-9_]{1,100}',reason):reason='BROKER_FAILURE_PRESERVED'
        value=json.dumps({'status':'REFUSED','reason':reason,
            'next_action':'Inspect protected evidence and recover original receipts before retrying.'}).encode()
    try:connection.sendall(value+b'\n')
    except OSError:pass  # Original completion persists even when transport fails.


def serve(config_path,socket_path):
    broker=Broker(json.loads(protected_read(config_path)))
    # systemd owns the socket across service restarts; no unlink-and-rebind race.
    activated=os.environ.get('LISTEN_PID')==str(os.getpid()) and os.environ.get('LISTEN_FDS')=='1'
    if activated:
        server=socket.socket(fileno=3)
        if server.family!=socket.AF_UNIX or server.getsockname()!=socket_path:raise ValueError('ACTIVATED_SOCKET_MISMATCH')
    else:
        path=Path(socket_path)
        if path.exists() or path.is_symlink():raise ValueError('SOCKET_ALREADY_EXISTS_RECONCILE')
        server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        server.bind(str(path));os.chmod(path,0o660);server.listen(8)
    with server:
        while True:
            connection,_=server.accept()
            with connection:exchange(broker,connection)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True)
    p.add_argument('operation',choices=['serve','reset','initialize']);p.add_argument('--socket');p.add_argument('--request')
    a=p.parse_args()
    if a.operation=='serve':serve(a.config,a.socket)
    else:
        broker=Broker(json.loads(protected_read(a.config)))
        print(json.dumps(broker.operator(a.operation,json.loads(protected_read(a.request)))))
