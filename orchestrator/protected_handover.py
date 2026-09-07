"""Narrow OS-authenticated handover broker. No live grant is bundled here.

Protected service configuration/checkout/ledger/key ownership is the security
boundary. Scientific and model users must not own these paths or service code.
Remote Git credentials remain exclusively in the protected publisher identity.
"""
import argparse
from contextlib import nullcontext
import json
import hashlib
import os
from pathlib import Path
import socket
import struct

from orchestrator.dispatch_limiter import GitLedger,admit_server,admit,reset,initialize,policy
from orchestrator.git_publication import publish,scan
from orchestrator.phone_notifications import protected_read

REPOSITORY='https://github.com/Moroseui/concept-research-scout.git'
BRANCH='astra/infrastructure-milestone-record'


class Broker:
    def __init__(self,config):
        required={'mode','repository','branch','controller_uid','operator_uids','sources','ledger_repo','publication_root','policy','writer_config'}
        if set(config)!=required or config['mode'] not in ('SYNTHETIC_FIXTURE','LIVE_APPROVED') or config['repository']!=REPOSITORY or config['branch']!=BRANCH:raise ValueError('PROTECTED_CONFIG_SCHEMA')
        if type(config['controller_uid']) is not int or not config['operator_uids'] or config['controller_uid'] in config['operator_uids']:raise ValueError('DISTINCT_OPERATOR_REQUIRED')
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
            return {'pin':pin,'sequence':state['sequence'],'count':state['count'],'halted':state['halted'],'day':state['day']}
        if op=='admit_server':
            if body.get('source') not in self.config['sources']:raise ValueError('REVIEWED_SOURCE_REQUIRED')
            with self.authentication():return admit_server(self.ledger,self.config['policy'],body)
        if op=='publish':
            if self.config['mode']!='LIVE_APPROVED':raise ValueError('LIVE_PUBLICATION_NOT_AUTHORIZED')
            policy(self.config['policy'])
            if body.get('destination')!=BRANCH or body.get('remote')!=REPOSITORY:raise ValueError('PUBLICATION_DESTINATION_REFUSED')
            keys={'operation','source','audit_baseline','baseline_ref','destination','remote','expected_destination'} if body.get('operation')=='create' else {'source','before','destination','remote'}
            if set(body)!=keys|{'inventory'}:raise ValueError('PUBLICATION_SCHEMA')
            # Checkout is a fixed protected import/cache path, never a request path.
            with self.authentication():return publish(Path(self.config['publication_root']),body,{k:body[k] for k in keys})
        raise ValueError('BROKER_OPERATION_REFUSED')

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


def serve(config_path,socket_path):
    broker=Broker(json.loads(protected_read(config_path)))
    path=Path(socket_path)
    if path.exists() or path.is_symlink():raise ValueError('SOCKET_ALREADY_EXISTS_RECONCILE')
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as server:
        server.bind(str(path));os.chmod(path,0o660);server.listen(8)
        while True:
            connection,_=server.accept()
            with connection:
                connection.settimeout(10)
                _,uid,_=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
                raw=b''
                while b'\n' not in raw and len(raw)<=1500000:
                    data=connection.recv(65536)
                    if not data:break
                    raw+=data
                try:
                    if len(raw)>1500000 or not raw.endswith(b'\n') or raw.count(b'\n')!=1:raise ValueError('BOUNDED_REQUEST_REQUIRED')
                    request=json.loads(raw);scan('broker-request.json',raw)
                    response=broker.handle(request,uid)
                    value=json.dumps(response).encode();scan('broker-response.json',value)
                except (ValueError,KeyError,TypeError):value=b'{"status":"REFUSED","next_action":"Inspect protected broker evidence; do not retry a changed request blindly."}'
                connection.sendall(value+b'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True)
    p.add_argument('operation',choices=['serve','reset','initialize']);p.add_argument('--socket');p.add_argument('--request')
    a=p.parse_args()
    if a.operation=='serve':serve(a.config,a.socket)
    else:
        broker=Broker(json.loads(protected_read(a.config)))
        print(json.dumps(broker.operator(a.operation,json.loads(protected_read(a.request)))))
