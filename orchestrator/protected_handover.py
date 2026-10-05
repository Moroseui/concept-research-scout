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
import re

from orchestrator.dispatch_limiter import GitLedger,admit_server,admit,reset,initialize,policy,validate_server_event
from orchestrator.git_publication import publish,scan
from orchestrator.phone_notifications import protected_read

REPOSITORY='https://github.com/Moroseui/concept-research-scout.git'
BRANCH='astra/infrastructure-milestone-record'



def model_output_format(packet, stage):
    """Validate each installed typed workflow before selecting its output format."""
    if not isinstance(packet, dict):
        raise ValueError('MODEL_PACKET_SCHEMA')
    from orchestrator.protected_disposition import successor_packet
    if successor_packet(packet, stage):
        return 'markdown'
    if 'scientific_decision_artifacts' in packet:
        contract = packet['scientific_decision_artifacts']
        if ('campaign_artifacts' in packet or packet.get('execution_proposal') is not None
                or not isinstance(contract, dict)):
            raise ValueError('SCIENTIFIC_DECISION_CONTRACT')
        if contract.get('version') == 3:
            from orchestrator.formal_decisions import contract as formal_contract
            formal_contract(contract)
        elif contract.get('version') == 2:
            from orchestrator.continuing_research import artifact_contract
            if contract.get('action') != 'authorize_research_task':
                raise ValueError('SCIENTIFIC_DECISION_CONTRACT')
            artifact_contract({k: v for k, v in contract.items() if k != 'action'})
        elif (set(contract) != {'version', 'action', 'experiment', 'mode'}
                or type(contract['version']) is not int or contract['version'] != 1
                or contract['action'] != 'authorize_research_task' or contract['experiment'] != 'P001'
                or contract['mode'] not in ('discuss', 'readiness')):
            raise ValueError('FINITE_SCIENTIFIC_DECISION_CONTRACT')
        if stage not in ('continuation', 'review'):
            raise ValueError('SCIENTIFIC_DECISION_TWO_STAGES_AND_SEAL')
        return 'json'
    if 'campaign_artifacts' in packet:
        contract = packet['campaign_artifacts']
        if not isinstance(contract, dict):
            raise ValueError('CAMPAIGN_ARTIFACT_CONTRACT')
        if contract.get('version') == 2:
            from orchestrator.continuing_research import artifact_contract, task_contract
            artifact_contract(contract)
            if task_contract(packet.get('campaign_task')) != contract:
                raise ValueError('CAMPAIGN_TASK_CONTRACT_CHANGED')
        elif (set(contract) != {'version', 'experiment', 'mode'}
                or type(contract['version']) is not int or contract['version'] != 1
                or contract['experiment'] != 'P001' or contract['mode'] not in ('readiness', 'discuss')):
            raise ValueError('CAMPAIGN_ARTIFACT_CONTRACT')
        if stage not in ('continuation', 'review', 'disposition'):
            raise ValueError('CAMPAIGN_ARTIFACT_STAGE')
        return 'json' if stage in ('continuation', 'review') else 'markdown'
    return 'json' if stage == 'disposition' and packet.get('execution_proposal') is not None else 'markdown'


def scientific_timeout(config, packet):
    """The protected installation selects a bound; a model request cannot raise it."""
    value = config.get('scientific_model_timeout_seconds', 240)
    if type(value) is not int or value not in (240, 600):
        raise ValueError('BOUNDED_SCIENTIFIC_MODEL_TIMEOUT_REQUIRED')
    from orchestrator.protected_disposition import successor_packet
    return value if ('campaign_artifacts' in packet or 'scientific_decision_artifacts' in packet
        or successor_packet(packet, 'disposition')) else 240

class Broker:
    def __init__(self,config, *, config_path=None):
        required={'mode','repository','branch','controller_uid','operator_uids','sources','ledger_repo','publication_root','policy','writer_config','model_mode','turn_root','max_model_turns'}
        if not required<=set(config) or set(config)-required-{'activation_decision_sha256','notification_config','research_controller_config','scientific_jobs_config','scientific_model_timeout_seconds'} or config['mode'] not in ('SYNTHETIC_FIXTURE','LIVE_APPROVED') or config['repository']!=REPOSITORY or config['branch']!=BRANCH:raise ValueError('PROTECTED_CONFIG_SCHEMA')
        if type(config['controller_uid']) is not int or config['controller_uid']<=0 or not config['operator_uids'] or config['controller_uid'] in config['operator_uids']:raise ValueError('DISTINCT_OPERATOR_REQUIRED')
        if config['model_mode'] not in ('DISABLED','SUPERVISED','GOVERNED') or type(config['max_model_turns']) is not int or not 0<=config['max_model_turns']<=4:raise ValueError('BOUNDED_MODEL_CONFIGURATION')
        if config.get('notification_config') is not None and (not isinstance(config['notification_config'],str)
                or not Path(config['notification_config']).is_absolute()):raise ValueError('PROTECTED_NOTIFICATION_CONFIG_PATH')
        if config['model_mode']=='GOVERNED':
            if config['mode']!='LIVE_APPROVED' or config['max_model_turns']!=0:
                raise ValueError('GOVERNED_MODE_REQUIRES_LIVE_PERMISSION')
            policy(config['policy'])
            if config['policy'].get('server_semantics')!='OPERATOR_AUTHORIZED_V1':
                raise ValueError('SERVER_ADMISSION_NOT_AUTHORIZED')
            if not isinstance(config.get('activation_decision_sha256'),str) or not re.fullmatch('[0-9a-f]{64}',config['activation_decision_sha256']):
                raise ValueError('SEPARATE_UNATTENDED_ACTIVATION_REQUIRED')
        if not isinstance(config['sources'],list) or not config['sources'] or len(config['sources'])>16:raise ValueError('BOUNDED_REVIEWED_SOURCES')
        if any(not isinstance(pin,str) or not re.fullmatch('[0-9a-f]{40}',pin) for pin in config['sources']):raise ValueError('REVIEWED_SOURCE_REQUIRED')
        roots=[Path(config[name]).resolve() for name in ('publication_root','ledger_repo','turn_root')]
        if any(a.is_relative_to(b) or b.is_relative_to(a) for i,a in enumerate(roots) for b in roots[i+1:]):
            raise ValueError('DISTINCT_PROTECTED_STATE_ROOTS_REQUIRED')
        if roots[0].is_relative_to(Path(__file__).resolve().parents[1]):
            raise ValueError('PUBLICATION_CACHE_MUST_NOT_BE_EXECUTION_SOURCE')
        scientific_timeout(config, {})
        for name in ('research_controller_config', 'scientific_jobs_config'):
            if name in config and (not isinstance(config[name], str) or not Path(config[name]).is_absolute()
                    or '..' in Path(config[name]).parts):
                raise ValueError('PROTECTED_RESEARCH_CONFIG_PATH_REQUIRED')
        self.config_path = None if config_path is None else str(Path(config_path).absolute())
        self.config=config
        self.ledger=GitLedger(config['ledger_repo'],remote=config['mode']=='LIVE_APPROVED',
            expected_remote=REPOSITORY,
            protected_owner_group=config['mode']=='LIVE_APPROVED' and os.geteuid()==0)

    def reviewed_deployment(self):
        """Root verifies the actual installed review; no supplied verdict is accepted."""
        if self.config['mode'] != 'LIVE_APPROVED':
            return {'status': 'SYNTHETIC_FIXTURE_NO_LIVE_AUTHORITY', 'model_calls': 0}
        if self.config_path != '/etc/research-system/live-research/broker.json':
            raise ValueError('FIXED_LIVE_DEPLOYMENT_CONFIGURATION_REQUIRED')
        from orchestrator.handover_runtime import configuration
        from orchestrator.deployment_review import verify_installed
        controller_path = self.config.get('research_controller_config')
        if controller_path != '/etc/research-system/live-research/controller.json':
            raise ValueError('FIXED_LIVE_CONTROLLER_CONFIGURATION_REQUIRED')
        controller = configuration(controller_path)
        root = Path(__file__).resolve().parents[1]
        if Path(controller['source_root']) != root or controller['source'] not in self.config['sources']:
            raise ValueError('DEPLOYMENT_CONTROLLER_SOURCE_CHANGED')
        result = verify_installed(root, controller['source'], config_path=self.config_path, config=self.config)
        return {'status': 'INSTALLED_REVIEW_VERIFIED', 'source': result['source'],
            'proposal_sha256': result['proposal_sha256'], 'review_response_sha256': result['review_response_sha256'],
            'review_session': result['review_session'], 'review_model': result['review_model'],
            'running_broker': result['running_broker'],
            'controller_config_sha256': hashlib.sha256(json.dumps(controller, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'model_calls': 0, 'unattended_activation_authority': False}

    def authentication(self):
        if self.config['mode']=='SYNTHETIC_FIXTURE':return nullcontext()
        from orchestrator.protected_writer import credentials
        return credentials(json.loads(protected_read(self.config['writer_config'])))

    def handle(self,request,peer_uid):
        if not isinstance(request,dict) or set(request)!={'operation','body'}:raise ValueError('BROKER_REQUEST_SCHEMA')
        if peer_uid!=self.config['controller_uid']:raise ValueError('BROKER_PEER_REFUSED')
        op=request['operation'];body=request['body']
        if not isinstance(body,dict):raise ValueError('BROKER_BODY_SCHEMA')
        if op == 'deployment_status':
            if body != {}:raise ValueError('DEPLOYMENT_STATUS_BODY')
            return self.reviewed_deployment()
        if op in {'admit_server', 'model_stage', 'register_research', 'register_scientific_job',
                'register_scientific_validation',
                'dispatch_scientific_job', 'publish', 'stage_candidate', 'flush_notifications',
                'notify_report', 'notify_task_block', 'observe_scientific_jobs', 'reserve_investigator', 'disposition_unstarted'}:
            self.reviewed_deployment()
        if op=='status':
            if body!={}:raise ValueError('STATUS_BODY')
            with self.authentication():pin,state=self.ledger.read()
            return {'mode':self.config['mode'],'pin':pin,'sequence':state['sequence'],'count':state['count'],'halted':state['halted'],'day':state['day']}
        if op=='publication_status':
            if body!={}:raise ValueError('PUBLICATION_STATUS_BODY')
            if self.config['mode']!='LIVE_APPROVED':
                return {'status':'PUBLICATION_NOT_AUTHORIZED'}
            from orchestrator.publication_candidate import git
            ref='refs/heads/'+BRANCH
            observed=git(self.config['publication_root'],'ls-remote',REPOSITORY,ref).decode().split()
            if len(observed)!=2 or observed[1]!=ref or not re.fullmatch('[0-9a-f]{40}',observed[0]):
                raise ValueError('PUBLICATION_DESTINATION_UNAVAILABLE')
            return {'status':'OBSERVED','source':observed[0],'repository':REPOSITORY,'branch':BRANCH}
        if op=='flush_notifications':
            if body!={}:raise ValueError('NOTIFICATION_STATUS_BODY')
            notices=self.notices()
            if notices is None:return {'status':'NOTIFICATIONS_DISABLED'}
            from orchestrator.dispatch_limiter import pending_notifications
            with self.authentication():pin,state=self.ledger.read()
            result=[]
            for key in pending_notifications(state):
                notice=state['notifications'][key]
                summary=('Admission threshold '+notice['threshold']+' recorded at count '+str(notice['count'])+
                    ' on '+notice['day']+'. '+('Subsequent admissions are halted pending operator reset.'
                        if notice['threshold']=='2N' else 'Work continues; this is a job-count warning, not a dollar limit.'))
                result.append(notices.send('admission:'+key,pin,summary))
            return {'status':'NOTIFICATION_RECONCILIATION','deliveries':result}
        if op=='notify_report':
            if (set(body)!={'source','report','phase'} or body['phase'] not in ('finalized','reviewed')
                    or not isinstance(body['source'],str) or not isinstance(body['report'],str)
                    or not re.fullmatch('[0-9a-f]{40}',body['source'])
                    or not re.fullmatch('[0-9a-f]{64}',body['report'])):raise ValueError('REPORT_NOTIFICATION_SCHEMA')
            notices=self.notices()
            if notices is None:return {'status':'NOTIFICATIONS_DISABLED'}
            observed=self.handle({'operation':'publication_status','body':{}},peer_uid)
            from orchestrator.publication_candidate import git
            git(self.config['publication_root'],'merge-base','--is-ancestor',body['source'],observed['source'])
            path='docs/operations/daily/'+body['report']+'.md'
            raw=git(self.config['publication_root'],'show',body['source']+':'+path);scan(path,raw)
            if hashlib.sha256(raw).hexdigest()!=body['report']:raise ValueError('PUBLISHED_REPORT_CHANGED')
            summary=('A checked '+body['phase']+' system report is available: https://github.com/Moroseui/concept-research-scout/blob/'+body['source']+'/'+path)
            return notices.send('report:'+body['report']+':'+body['phase'],body['source'],summary)
        if op=='notify_task_block':
            if (set(body)!={'source','task','reason'} or body['source'] not in self.config['sources']
                    or not isinstance(body['task'],str) or not re.fullmatch('[0-9a-f]{64}',body['task'])
                    or not isinstance(body['reason'],str) or not re.fullmatch('[A-Z0-9_]{1,80}',body['reason'])):
                raise ValueError('BLOCK_NOTIFICATION_SCHEMA')
            notices=self.notices()
            if notices is None:return {'status':'NOTIFICATIONS_DISABLED'}
            summary=('A handover task is blocked: '+body['task']+'. Reason: '+body['reason']+
                '. Original evidence is preserved. Inspect the source-bound status and decision inbox; do not blindly retry uncertain execution.')
            return notices.send('block:'+body['task']+':'+body['reason'],body['source'],summary)
        if op=='admit_server':
            if body.get('source') not in self.config['sources']:raise ValueError('REVIEWED_SOURCE_REQUIRED')
            with self.authentication():return admit_server(self.ledger,self.config['policy'],body)
        from orchestrator.protected_scientific_jobs import OPERATIONS as job_operations
        if op in job_operations:
            from orchestrator.protected_scientific_jobs import handle as scientific_job
            return scientific_job(self, op, body)
        if op in ('reserve_investigator','read_investigator_wake','list_recorded_steering',
                  'read_recorded_steering','stage_failure','stage_input_refusal'):
            from orchestrator.protected_investigator import handle as investigator_operation
            return investigator_operation(self, op, body)
        if op=='register_research':
            from orchestrator.continuing_research import protected_register
            return protected_register(self, body)
        if op == 'disposition_unstarted':
            from orchestrator.protected_disposition import disposition_unstarted
            return disposition_unstarted(self, body)
        if op == 'disposition_refusal':
            from orchestrator.protected_disposition import disposition_refusal
            return disposition_refusal(self, body)
        if op=='stage_packet':return self.stage_packet(body)
        if op=='stage_status':return self.stage_status(body)
        if op=='model_stage':return self.model_stage(body)
        if op=='stage_candidate':
            import base64
            from orchestrator.publication_candidate import receive
            if set(body)!={'source','before','inventory','bundle_sha256','bundle_base64'}:
                raise ValueError('CANDIDATE_REQUEST_SCHEMA')
            raw=base64.b64decode(body['bundle_base64'],validate=True)
            # Fixed protected cache, no credentials and no remote publication.
            return receive(self.config['publication_root'],body['source'],body['before'],
                           body['inventory'],raw,body['bundle_sha256'])
        if op=='publish':
            if self.config['mode']!='LIVE_APPROVED':raise ValueError('LIVE_PUBLICATION_NOT_AUTHORIZED')
            policy(self.config['policy'])
            from orchestrator.publication_candidate import pins
            # Installed execution sources are distinct from new branch commits.
            # Every candidate still passes the complete audit and exact ref lease.
            pins(body.get('source'),body.get('audit_baseline') if body.get('operation')=='create' else body.get('before'))
            if body.get('destination')!=BRANCH or body.get('remote')!=REPOSITORY:raise ValueError('PUBLICATION_DESTINATION_REFUSED')
            keys={'operation','source','audit_baseline','baseline_ref','destination','remote','expected_destination'} if body.get('operation')=='create' else {'source','before','destination','remote'}
            if set(body)!=keys|{'inventory'}:raise ValueError('PUBLICATION_SCHEMA')
            # Checkout is a fixed protected import/cache path, never a request path.
            with self.authentication():return publish(Path(self.config['publication_root']),body,{k:body[k] for k in keys})
        raise ValueError('BROKER_OPERATION_REFUSED')

    def notices(self):
        path=self.config.get('notification_config')
        if self.config['mode']!='LIVE_APPROVED' or path is None:return None
        from orchestrator.handover_notifications import Notices
        return Notices(Path(self.config['turn_root']).parent/'notifications',path)

    def model_stage(self,body):
        from orchestrator.hosted_cycle import model_call,immutable,encoded
        from orchestrator.operations_report import private_root
        if self.config['model_mode'] not in ('SUPERVISED','GOVERNED') or os.getuid()!=0:raise ValueError('SUPERVISED_ROLE_LAUNCHER_REQUIRED')
        if set(body)!={'event','stage','packet','prompt'}:raise ValueError('MODEL_STAGE_SCHEMA')
        event=body['event'];stage=body['stage']
        output_format=model_output_format(body['packet'],stage)
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
            from orchestrator.protected_disposition import successor_packet, verify_successor_launch
            linked = successor_packet(body['packet'], stage)
            if linked:
                verify_successor_launch(self, body, gate)
            folder=root/(event['turn_id']+'-'+event['attempt'])
            binding={'event':event,'packet_sha256':hashlib.sha256(encoded(body['packet'])).hexdigest()}
            if not folder.exists():
                retained=len(list(root.glob('*/binding.json')))
                if self.config['model_mode']=='SUPERVISED' and retained>=self.config['max_model_turns']:
                    raise ValueError('SUPERVISED_MODEL_BUDGET_EXHAUSTED')
                if retained>=10000:raise ValueError('MODEL_EVIDENCE_CAPACITY_REQUIRES_MAINTENANCE')
                folder.mkdir(mode=0o700)
                immutable(folder/'binding.json',encoded(binding))
                immutable(folder/'packet.json',encoded(body['packet']))
            if folder.is_symlink() or json.loads((folder/'binding.json').read_text())!=binding:raise ValueError('TURN_BINDING_CHANGED')
            immutable(folder/(stage+'.request.json'),encoded({'prompt_sha256':hashlib.sha256(body['prompt'].encode()).hexdigest()}))
            receipt_path=folder/(stage+'.receipt.json')
            if receipt_path.exists():return self.stage_status({'event':event,'stage':stage})
            if (folder/(stage+'.started.json')).exists():raise ValueError('UNCERTAIN_MODEL_RECONCILE_NO_RETRY')
            refused = folder/(stage+'.input-refused.json')
            if refused.exists() or refused.is_symlink():raise ValueError('INPUT_PREFLIGHT_RECONCILE_NO_RETRY')
            if not linked:
                for prior in stages[:stages.index(stage)]:
                    if self.stage_status({'event':event,'stage':prior})['status']!='COMPLETE':raise ValueError('PREDECESSOR_MODEL_RECEIPT_REQUIRED')
            from orchestrator.hosted_context import compose_input, measure_input, InputTooLarge
            from orchestrator.scientific_output import contract as output_contract
            family='claude' if stage=='review' else 'astra'
            from orchestrator.scientific_evidence_runtime import broker_capture
            evidence_access = broker_capture(self, body['packet'], source=event['source'],
                                             folder=folder, stage=stage, disposition_lock=gate)
            evidence_options = {} if evidence_access is None else {'evidence_access': evidence_access}
            # Check the actual composed input before this broker's admission. The
            # authority adapter also projects both roles before its first admission.
            final, _ = compose_input(Path(__file__).resolve().parents[1], encoded(body['packet']),
                body['prompt'], verified_source=event['source'], family=family,
                prepared_prompt=False, output_format=output_format, **evidence_options)
            try: measurement = measure_input(final, family, stage, task_state=body['packet'], output_contract=output_contract(body['packet'], stage))
            except InputTooLarge as error:
                immutable(refused, encoded({'status':'PREFLIGHT_INPUT_REFUSED',
                    'measurement':error.measurement,'provider_calls':0,'automatic_retry':False}))
                raise
            immutable(folder/(stage+'.input-preflight.json'), encoded(measurement))
            with self.authentication():admission=admit_server(self.ledger,self.config['policy'],event)
            if admission['status']!='ADMITTED':return admission
            # Read-only evidence tools confer no execution or selection authority.
            # Existing typed selection, admission and patient gates remain separate.
            answer,receipt=model_call(folder,stage,family,body['prompt'],output_format=output_format,
                timeout_seconds=scientific_timeout(self.config, body['packet']), **evidence_options)
            return {'status':'COMPLETE','duplicate':False,'answer':answer,'receipt':receipt,'packet_sha256':binding['packet_sha256']}

    def historical_event(self, event):
        """Allow an original read, never a launch, after execution-source retirement.

        Active sources retain their existing unstarted/absence behavior. A retired
        source needs its exact admitted identity in the authenticated ledger; the
        caller must still verify the protected packet and original output hashes.
        No growing historical allowlist is copied into runtime configuration.
        """
        from orchestrator.dispatch_limiter import validate
        validate_server_event(event)
        if event['source'] in self.config['sources']:
            return
        with self.authentication():
            _, state = self.ledger.read()
        validate(state)
        expected_policy = hashlib.sha256(json.dumps(self.config['policy'], sort_keys=True).encode()).hexdigest()
        row = state['events'].get('server:'+event['turn_id']+':'+event['attempt'])
        if (state['policy_sha256'] != expected_policy or not isinstance(row, dict)
                or any(row.get(key) != event[key] for key in ('source', 'branch', 'kind'))):
            raise ValueError('MODEL_STAGE_HISTORICAL_ADMISSION_REQUIRED')

    def stage_packet(self, body):
        """Original packet proof for scientific lineage; read no caller-selected path."""
        from orchestrator.hosted_cycle import encoded
        if set(body) != {'event'}:
            raise ValueError('STAGE_PACKET_SCHEMA')
        event = body['event']
        self.historical_event(event)
        folder = Path(self.config['turn_root']) / (event['turn_id']+'-'+event['attempt'])
        paths = (folder, folder/'binding.json', folder/'packet.json')
        if any(path.is_symlink() for path in paths):
            raise ValueError('TURN_BINDING_CHANGED')
        if not folder.exists():
            return {'status': 'NOT_OBSERVED_NO_RETRY'}
        binding = json.loads((folder/'binding.json').read_bytes())
        raw = (folder/'packet.json').read_bytes()
        if len(raw) > 1500000:
            raise ValueError('MODEL_PACKET_BOUND')
        packet = json.loads(raw)
        sha = hashlib.sha256(raw).hexdigest()
        if (binding['event'] != event or sha != binding.get('packet_sha256')
                or raw != encoded(packet)):
            raise ValueError('MODEL_PACKET_BINDING_CHANGED')
        # Existence is original packet evidence, not successful scientific review.
        # Consumers separately require both actual stage replies and disposition.
        return {'status': 'COMPLETE', 'packet_sha256': sha, 'packet': packet}

    def stage_status(self,body):
        """Retrieve original completion only. This path cannot invoke a model."""
        if set(body)!={'event','stage'}:raise ValueError('STAGE_STATUS_SCHEMA')
        event=body['event'];stage=body['stage'];validate_server_event(event)
        if stage not in ('continuation','review','disposition'):raise ValueError('MODEL_STAGE_SOURCE')
        self.historical_event(event)
        folder=Path(self.config['turn_root'])/(event['turn_id']+'-'+event['attempt'])
        if folder.is_symlink():raise ValueError('TURN_BINDING_CHANGED')
        if not folder.exists():return {'status':'NOT_OBSERVED_NO_RETRY'}
        binding_path=folder/'binding.json'
        if binding_path.is_symlink():raise ValueError('TURN_BINDING_CHANGED')
        binding=json.loads(binding_path.read_text())
        if binding['event']!=event:raise ValueError('TURN_BINDING_CHANGED')
        path=folder/(stage+'.receipt.json')
        if not path.exists():
            status='UNCERTAIN_MODEL_RECONCILE_NO_RETRY' if (folder/(stage+'.started.json')).exists() else 'NOT_STARTED_RECONCILIATION_REQUIRED'
            return {'status':status}
        if path.is_symlink():raise ValueError('MODEL_RECEIPT_CHANGED')
        receipt=json.loads(path.read_text())
        for suffix,key in [('.stdout','stdout_sha256'),('.stderr','stderr_sha256'),('.input.md','input_sha256'),('.md','answer_sha256'),('.operating-context.json','operating_context_sha256')]:
            file=folder/(stage+suffix)
            if file.is_symlink() or hashlib.sha256(file.read_bytes()).hexdigest()!=receipt[key]:raise ValueError('MODEL_RECEIPT_CHANGED')
        packet_sha=binding.get('packet_sha256')
        if not isinstance(packet_sha,str) or not re.fullmatch('[0-9a-f]{64}',packet_sha):raise ValueError('MODEL_PACKET_BINDING_MISSING')
        return {'status':'COMPLETE','duplicate':True,'answer':(folder/(stage+'.md')).read_text(),'receipt':receipt,'packet_sha256':binding['packet_sha256']}

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
            previous=self.ledger.allow_initialization
            try:
                self.ledger.allow_initialization=True
                with self.authentication():return initialize(self.ledger,self.config['policy'],{'actor':actor,'role':'operator',**body})
            finally:self.ledger.allow_initialization=previous
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
    broker=Broker(json.loads(protected_read(config_path)), config_path=config_path)
    # systemd owns the socket across service restarts; no unlink-and-rebind race.
    activated=os.environ.get('LISTEN_PID')==str(os.getpid()) and os.environ.get('LISTEN_FDS')=='1'
    if activated:
        server=socket.socket(fileno=3)
        if server.family!=socket.AF_UNIX or server.getsockname()!=socket_path:raise ValueError('ACTIVATED_SOCKET_MISMATCH')
    else:
        raise ValueError('SYSTEMD_SOCKET_ACTIVATION_REQUIRED')
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
        broker=Broker(json.loads(protected_read(a.config)), config_path=a.config)
        print(json.dumps(broker.operator(a.operation,json.loads(protected_read(a.request)))))
