"""Non-root handover service and human CLI over the shared coordinator.

Installed configuration is root-owned; operator requests are root-owned files,
not phone comments or caller-asserted roles. Live activation remains separate.
"""
import argparse
from datetime import datetime,timezone
import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
import socket
import stat
import sqlite3
import subprocess

from orchestrator.handover_coordinator import Coordinator,encoded,digest
from orchestrator.operations_report import finalize,Queue,immutable
from orchestrator.remote_supervisor import checked_source
from orchestrator.public_export import text

# Match the existing continuing_research private-evidence intake/read bound.
# Configuration files retain their separate64KiB default below.
RESEARCH_EVIDENCE_MAXIMUM = 750000


def configuration(path, *, maximum=65536, expected_sha256=None, private_gid=None):
    if private_gid is not None:
        parent=Path(path).parent
        if any(p.is_symlink() for p in (Path(path),*Path(path).parents)):
            raise ValueError('PRIVATE_RESEARCH_INPUT_PATH_REQUIRED')
        info=parent.stat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid!=0 or info.st_gid!=private_gid
                or info.st_mode & 0o027):
            raise ValueError('PROTECTED_RESEARCH_INPUT_PARENT_REQUIRED')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        info=os.fstat(fd)
        if info.st_uid!=0 or info.st_mode & 0o022 or not stat.S_ISREG(info.st_mode) or info.st_size>maximum:raise ValueError('INSTALLED_CONFIG_REQUIRED')
        if private_gid is not None and (info.st_gid!=private_gid or info.st_mode & 0o007):
            raise ValueError('PRIVATE_RESEARCH_INPUT_PERMISSIONS_REQUIRED')
        raw=os.read(fd,maximum+1)
        if len(raw)>maximum:raise ValueError('INSTALLED_CONFIG_REQUIRED')
        if expected_sha256 is not None and hashlib.sha256(raw).hexdigest()!=expected_sha256:
            raise ValueError('RESEARCH_INPUT_BINDING_CHANGED')
        return json.loads(raw)
    finally:os.close(fd)


def request_broker(path,operation,body):
    raw=encoded({'operation':operation,'body':body});text(raw.decode(),limit=1500000)
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as client:
        # Model responses may use the reviewed600second scientific bound.
        # A transport timeout never authorizes a second model or registration.
        timeout = 660 if operation == 'model_stage' else 120 if operation in (
            'register_research', 'register_scientific_job', 'dispatch_scientific_job') else 300
        client.settimeout(timeout);client.connect(path);client.sendall(raw)
        result=b''
        while not result.endswith(b'\n'):
            chunk=client.recv(65536)
            if not chunk or len(result)+len(chunk)>1500000:raise ValueError('BROKER_RESPONSE_UNAVAILABLE')
            result+=chunk
    value=json.loads(result)
    if value.get('status')=='REFUSED':
        reason=value.get('reason')
        if isinstance(reason,str) and re.fullmatch('[A-Z][A-Z0-9_]{1,100}',reason):raise ValueError(reason)
        raise ValueError('BROKER_REFUSED_RECONCILE')
    return value


def research_schedule(config):
    """An optional finite selection list is configuration, never authority."""
    value=config.get('research_schedule')
    if value is None:return None
    from orchestrator.research_catalog import identifier,MAX_ENTRIES,setting
    if (not isinstance(value,dict) or set(value)!={'task_ids'}
            or not isinstance(value['task_ids'],list) or not 1<=len(value['task_ids'])<=MAX_ENTRIES):
        raise ValueError('FINITE_RESEARCH_SCHEDULE_REQUIRED')
    identifiers=[identifier(item) for item in value['task_ids']]
    if len(set(identifiers))!=len(identifiers) or setting(config) is None:
        raise ValueError('EXPLICIT_UNIQUE_CATALOG_SCHEDULE_REQUIRED')
    return identifiers


class Runtime:
    def __init__(self,config):
        self.config=config
        self.root=checked_source(config['source_root'],config['source'])
        if os.getuid()!=config['controller_uid']:raise ValueError('NONROOT_CONTROLLER_IDENTITY_REQUIRED')
        research_schedule(config)
        self.state=Path(config['state'])
        if config.get('research_request') is not None:
            from orchestrator.hosted_campaign_task import installed_research_request
            if config.get('campaign_preparation') is not None:
                raise ValueError('ONE_INSTALLED_CAMPAIGN_REQUEST_REQUIRED')
            installed_research_request(config)
        if config.get('campaign_preparation') is not None:
            from orchestrator.hosted_campaign_task import task_contract
            task_contract(config['campaign_preparation'])
            pairs=config.get('synthetic_execution',{}).get('pairs',{})
            trigger=config['campaign_preparation'].get('trigger_job')
            if trigger not in pairs or pairs[trigger] is not None:
                raise ValueError('CAMPAIGN_TERMINAL_TRIGGER_CONFIGURATION_REQUIRED')
        self.q=Coordinator(self.state,{'continuation':self.model,'review':self.model,'disposition':self.model},self.admit,self.validate_binding)
        self.q.db.executescript('''
            CREATE TABLE IF NOT EXISTS bookkeeping(task TEXT PRIMARY KEY,status TEXT,attempts INTEGER,reason TEXT);
            CREATE TABLE IF NOT EXISTS control_delivery(id TEXT PRIMARY KEY,outcome TEXT);
            CREATE TABLE IF NOT EXISTS runtime_blocks(phase TEXT PRIMARY KEY,reason TEXT);
            CREATE TABLE IF NOT EXISTS report_delivery(report TEXT PRIMARY KEY,status TEXT,attempts INTEGER,reason TEXT,commit_pin TEXT);
            CREATE TABLE IF NOT EXISTS notification_delivery(id TEXT PRIMARY KEY,status TEXT,attempts INTEGER,issue INTEGER);
            CREATE TABLE IF NOT EXISTS research_submissions(task_id TEXT PRIMARY KEY,request_identity TEXT,task TEXT);
            CREATE TABLE IF NOT EXISTS research_submitters(task TEXT PRIMARY KEY,actor TEXT);
            CREATE TABLE IF NOT EXISTS research_scheduling(singleton INTEGER PRIMARY KEY CHECK(singleton=1),configuration TEXT,outcome TEXT);
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

    def deployment_status(self):
        """Use root's exact installed review proof without reading protected launchers."""
        if not self.config.get('continuing_operations') and not self.config.get('scientific_jobs_config'):
            return {'status': 'LEGACY_CONFIGURATION_NO_CONTINUING_AUTHORITY'}
        proof = request_broker(self.config['broker_socket'], 'deployment_status', {})
        expected = hashlib.sha256(json.dumps(self.config, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        if (proof.get('status') != 'INSTALLED_REVIEW_VERIFIED' or proof.get('source') != self.config['source']
                or proof.get('controller_config_sha256') != expected):
            raise ValueError('CURRENT_DEPLOYMENT_REVIEW_PROOF_REQUIRED')
        return proof

    def continuing_context(self):
        """Immutable submission-time state, separate from approved catalog evidence."""
        from orchestrator import continuing_operations, investigator_wakes, disposition_successors
        from orchestrator.protected_scientific_jobs import read_observation
        observation = read_observation(self.config)
        return {'disposition_successors': disposition_successors.status(self.config),
                'continuing_operations': continuing_operations.status(self.config),
                'investigator': investigator_wakes.status(self.config),
                'scientific_completions': observation['events'],
                'scientific_observation': {key: value for key, value in observation.items() if key != 'events'}}

    def continuing_step(self):
        from orchestrator import continuing_operations, investigator_wakes, authority_replacements
        if not continuing_operations.enabled(self.config):
            return {'status': 'DISABLED', 'models': 0}
        self.deployment_status()
        replacement = authority_replacements.advance(self)
        if replacement['status'] != 'NO_REPLACEMENT_WORK': return replacement
        result = continuing_operations.advance(self)
        if result['status'] in ('AWAITING_REVIEWED_SELECTION','OPERATIONS_REQUIRE_RECONCILIATION') and investigator_wakes.setting(self.config) is not None:
            return {**investigator_wakes.advance(self),
                    'blocked_operations':result.get('blocked_operations',[])}
        return result

    def admit(self,binding):
        self.deployment_status()
        # Validate configuration and admission before outward publication. A
        # finalized public identity is still available to the fresh report review.
        private_research=self.research_packet(binding)
        if private_research:self.research_eligibility(binding)
        elif binding['source']!=self.config['source']:
            self.historical_report_packet(binding)
            raise ValueError('HISTORICAL_REPORT_SOURCE_READ_ONLY')
        public_report=self.config.get('purpose')=='LIVE_APPROVED_HANDOVER' and not private_research
        if public_report:
            configured=self.config.get('publication')
            if not configured or set(configured)!={'checkout','permission_sha256'}:
                raise ValueError('LIVE_REPORT_PUBLICATION_CONFIGURATION_REQUIRED')
        admitted=request_broker(self.config['broker_socket'],'admit_server',self.event(binding))
        if admitted['status']!='ADMITTED':return admitted
        if public_report:
            from orchestrator.report_delivery import deliver
            report=json.loads((self.state/'tasks'/binding['id']/'report.json').read_text())['id']
            result=deliver(self.state/'reports',report,configured['checkout'],self.state/'delivery',
                self.config['broker_socket'],configured['permission_sha256'],phase='finalized')
            if result['status']!='PUBLISHED':raise ValueError('FINALIZED_REPORT_PUBLICATION_REQUIRED')
        return admitted

    def research_packet(self,binding):
        """A configured scientific task remains private and uses normal admission."""
        folder=self.state/'tasks'/binding['id']
        packet=json.loads((folder/'packet.json').read_text())
        if 'research_request_binding' not in packet:return False
        from orchestrator.hosted_campaign_task import installed_packet_task,task_contract
        task=installed_packet_task(self.config,packet)
        report=json.loads((folder/'report.json').read_text())
        if (binding['source']!=packet['research_request_binding']['source'] or binding['kind']!='astra_turn'
                or digest({'source':binding['source'],'packet':packet,'report':report})!=binding['id']
                or packet.get('campaign_task')!=task or packet.get('campaign_artifacts')!=task_contract(task)):
            raise ValueError('INSTALLED_RESEARCH_PACKET_CHANGED')
        from orchestrator.research_catalog import selection
        _,entry=selection(self.config,task['task_id'])
        if entry is not None and packet.get('research_catalog_entry')!=entry:
            raise ValueError('INSTALLED_RESEARCH_PACKET_CHANGED')
        return True

    def historical_report_packet(self,binding):
        """Verify the original report before read-only source-upgrade recovery."""
        self.validate_binding(binding)
        folder=self.state/'tasks'/binding['id']
        paths=(folder/'packet.json',folder/'report.json')
        if any(path.is_symlink() for path in (folder,*paths)):
            raise ValueError('HISTORICAL_REPORT_PATH_CHANGED')
        packet,report=(json.loads(path.read_bytes()) for path in paths)
        if (binding['kind']!='nightly_review' or 'campaign_task' in packet
                or set(report)!={'id'} or not re.fullmatch('[0-9a-f]{64}',report['id'])
                or digest({'source':binding['source'],'packet':packet,'report':report})!=binding['id']):
            raise ValueError('HISTORICAL_REPORT_PACKET_CHANGED')
        path=self.state/'reports'/(report['id']+'.md')
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=report['id']:
            raise ValueError('HISTORICAL_REPORT_CONTENT_CHANGED')
        status=Queue(self.state/'reports').status(report['id'])
        if status['source']!=binding['source'] or status['report_sha256']!=report['id']:
            raise ValueError('HISTORICAL_REPORT_SOURCE_CHANGED')
        return packet

    def research_predecessors(self,entry):
        """Completion is transport state; acceptance needs the original review."""
        for required in entry['predecessors']:
            row=self.q.db.execute('SELECT binding,status FROM tasks WHERE id=?',(required['task'],)).fetchone()
            if not row or row['status']!='COMPLETE':raise ValueError('RESEARCH_PREDECESSOR_INCOMPLETE')
            binding=json.loads(row['binding'])
            if binding['source']!=required['source'] or not self.research_packet(binding):
                raise ValueError('RESEARCH_PREDECESSOR_BINDING_CHANGED')
            # Reuse original pipeline/broker verification, never another model.
            self._bookkeep({'id':required['task']})
            path=self.state/'tasks'/required['task']/'scientific-disposition.json'
            if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=required['disposition_sha256']:
                raise ValueError('RESEARCH_PREDECESSOR_DISPOSITION_CHANGED')
            outcome=json.loads(path.read_bytes())
            if (outcome.get('task')!=required['task'] or outcome.get('source')!=required['source']
                    or outcome.get('status')!='DISPOSITION_RECORDED'):
                raise ValueError('RESEARCH_PREDECESSOR_DISPOSITION_REQUIRED')
            if required['requires']=='APPROVED_PROPOSAL_ONLY' and (
                    outcome.get('review_verdict')!='APPROVE'
                    or outcome.get('acceptance_status')!='APPROVED_PROPOSAL_ONLY'):
                raise ValueError('RESEARCH_PREDECESSOR_NOT_ACCEPTED')

    def research_eligibility(self,binding):
        if binding['source']!=self.config['source']:
            raise ValueError('HISTORICAL_RESEARCH_SOURCE_READ_ONLY')
        from orchestrator.research_catalog import selection,eligibility
        packet=json.loads((self.state/'tasks'/binding['id']/'packet.json').read_text())
        _,entry=selection(self.config,packet['campaign_task']['task_id'])
        if entry is not None:
            if eligibility(self.config,entry)!=packet.get('research_eligibility'):
                raise ValueError('RESEARCH_ELIGIBILITY_CHANGED')
            self.research_predecessors(entry)

    def submit_research(self,task_id=None,*,submitted_by=None):
        """Queue one installed eligible request; never admit or call a model.

        A stable task ID binds its first exact source/configuration/input identity.
        Repeated human/agent submission returns that same saved work, including
        after completion or changed reporting context, without another execution.
        """
        from orchestrator.hosted_campaign_task import installed_research_request
        from orchestrator.research_catalog import selection,eligibility
        if isinstance(submitted_by,dict) and submitted_by.get('kind')=='service':
            if submitted_by!=self.research_service_submitter():
                raise ValueError('EXACT_RESEARCH_SERVICE_TRANSPORT_REQUIRED')
        elif submitted_by is not None:
            from orchestrator.change_requests import actor
            actor(submitted_by)
        task,evidence,request=installed_research_request(self.config,task_id)
        _,entry=selection(self.config,task['task_id'])
        self.q.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.q.db.execute('SELECT * FROM research_submissions WHERE task_id=?',
                (task['task_id'],)).fetchone()
            if prior:
                if prior['request_identity']!=request['identity']:
                    raise ValueError('RESEARCH_REQUEST_IDENTITY_CONFLICT')
                row=self.q.db.execute('SELECT binding,status FROM tasks WHERE id=?',(prior['task'],)).fetchone()
                if not row:raise ValueError('RESEARCH_SUBMISSION_RECONCILE_NO_RETRY')
                self.research_packet(json.loads(row['binding']))
                result={'status':row['status'],'task':prior['task'],'duplicate':True}
            else:
                if request['source']!=self.config['source']:
                    raise ValueError('HISTORICAL_RESEARCH_SOURCE_READ_ONLY')
                if entry is not None:
                    if submitted_by is None:raise ValueError('RESEARCH_SUBMITTER_ATTRIBUTION_REQUIRED')
                    eligibility(self.config,entry)
                    self.research_predecessors(entry)
                binding=self.enqueue_report(request['day'],[],
                    {'research_task':task['task_id'],'research_request_identity':request['identity'],
                     'scope':'Installed versioned scientific operation; separate review and execution authority remain required.'},
                    reviewer_evidence=evidence,trigger='installed-research-request',research_task_id=task['task_id'])
                self.q.submit(binding)
                self.q.db.execute('INSERT INTO research_submissions VALUES(?,?,?)',
                    (task['task_id'],request['identity'],binding['id']))
                self.q.db.execute('INSERT INTO research_submitters VALUES(?,?)',
                    (binding['id'],json.dumps(submitted_by,sort_keys=True)))
                result={'status':'QUEUED','task':binding['id'],'duplicate':False}
            self.q.db.execute('COMMIT')
        except BaseException:
            self.q.db.execute('ROLLBACK');raise
        return {**result,'request_identity':request['identity'],'task_id':task['task_id'],
            'request_initiator':request['initiator'],'controller_uid':os.getuid(),
            'paused':bool(self.q.status()['paused']),'model_calls':0,'admissions':0}

    def research_inspect(self,task_id=None):
        """Read the same installed and submitted work without authorizing it."""
        from orchestrator.hosted_campaign_task import installed_research_request
        from orchestrator.research_catalog import selection,eligibility
        task,_,request=installed_research_request(self.config,task_id)
        configured,entry=selection(self.config,task['task_id'])
        status='LEGACY_INSTALLED_REQUEST';reason=None
        if entry is not None:
            try:eligibility(self.config,entry);status='ELIGIBLE'
            except ValueError as error:
                status='NOT_ELIGIBLE';reason=str(error)
        if request['source']!=self.config['source']:status='HISTORICAL_READ_ONLY'
        row=self.q.db.execute('SELECT * FROM research_submissions WHERE task_id=?',(task['task_id'],)).fetchone()
        saved=None
        if row:
            if row['request_identity']!=request['identity']:raise ValueError('RESEARCH_REQUEST_IDENTITY_CONFLICT')
            work=self.q.db.execute('SELECT * FROM tasks WHERE id=?',(row['task'],)).fetchone()
            if not work:raise ValueError('RESEARCH_SUBMISSION_RECONCILE_NO_RETRY')
            self.research_packet(json.loads(work['binding']))
            saved={'task':row['task'],'status':work['status'],'reason':work['reason'],
                'directory':str(self.state/'tasks'/row['task']),
                'revalidation_required':reason=='RESEARCH_CHANGE_REQUIRES_CORRECTION'}
            submitter=self.q.db.execute('SELECT actor FROM research_submitters WHERE task=?',(row['task'],)).fetchone()
            saved['submitted_by']=None if submitter is None else json.loads(submitter['actor'])
            disposition=Path(saved['directory'])/'scientific-disposition.json'
            if disposition.exists():
                if disposition.is_symlink():raise ValueError('RESEARCH_DISPOSITION_PATH_CHANGED')
                raw=disposition.read_bytes()
                saved['disposition']=json.loads(raw)
                saved['disposition_sha256']=hashlib.sha256(raw).hexdigest()
        return {'task_id':task['task_id'],'request':configured['research_request'],
            'binding':request,'catalog_entry':entry,'eligibility_status':status,'reason':reason,
            'saved':saved,'models':0,'admissions':0}

    def research_list(self):
        from orchestrator.research_catalog import paths
        identifiers=list(paths(self.config))
        legacy=self.config.get('research_request',{}).get('task',{}).get('task_id')
        if legacy in identifiers:raise ValueError('CATALOG_LEGACY_ID_CONFLICT')
        if legacy:identifiers.append(legacy)
        records=[]
        for identity in sorted(identifiers):
            item=self.research_inspect(identity)
            records.append({'task_id':identity,'source':item['binding']['source'],
                'request_identity':item['binding']['identity'],'eligibility_status':item['eligibility_status'],
                'reason':item['reason'],'saved':None if item['saved'] is None else
                    {k:item['saved'][k] for k in ('task','status','reason')}})
        return {'requests':records,'catalog_history_limit':None,
            'scheduled_selection_bound':32,'models':0,'admissions':0}

    def research_service_submitter(self):
        # This attests only the authenticated controller transport. The entry's
        # original model judgment/review remains the scientific authority.
        return {'kind':'service','identity':'controller-uid:'+str(self.config['controller_uid']),
            'identity_source':'authenticated_controller_uid','operation':'finite_catalog_submission',
            'source':self.config['source']}

    def research_schedule_status(self):
        identifiers=research_schedule(self.config)
        if identifiers is None:return {'status':'DISABLED','task_ids':[]}
        configuration=digest({'source':self.config['source'],'task_ids':identifiers})
        row=self.q.db.execute('SELECT configuration,outcome FROM research_scheduling WHERE singleton=1').fetchone()
        if row and row['configuration']==configuration:return json.loads(row['outcome'])
        return {'status':'NOT_OBSERVED','task_ids':identifiers,'requests':[]}

    def scheduled_research(self):
        """Select at most one preinstalled eligible task through shared submit.

        A saved submission is never reset. Missing, deferred or criticized work
        stays visible while independent allowlisted work can still progress.
        """
        identifiers=research_schedule(self.config)
        if identifiers is None:return {'status':'DISABLED','task_ids':[]}
        configuration=digest({'source':self.config['source'],'task_ids':identifiers})
        def record(status,requests=(),submitted=None):
            value={'status':status,'task_ids':identifiers,'requests':list(requests),
                'submitted_task':submitted,'source':self.config['source'],
                'observed_at':datetime.now(timezone.utc).isoformat(),'models':0,'admissions':0}
            self.q.db.execute('INSERT OR REPLACE INTO research_scheduling VALUES(1,?,?)',
                (configuration,json.dumps(value,sort_keys=True)))
            return value
        held=[]
        try:
            for name in ('branch.lock','admission.lock'):
                handle=(self.state/name).open('a');held.append(handle)
                try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError:return {'status':'WRITER_OR_ADMISSION_BUSY','source':self.config['source'],
                     'task_ids':identifiers,'models':0,'admissions':0,'previous_observation_preserved':True}
            if self.q.db.execute("SELECT 1 FROM runtime_blocks WHERE phase='controls'").fetchone():
                return record('CONTROL_TRANSPORT_BLOCKED')
            if self.q.status()['paused']:return record('PAUSED')
            from orchestrator.research_catalog import paths
            installed=paths(self.config);requests=[];submitted=None
            for identity in identifiers:
                if identity not in installed:
                    requests.append({'task_id':identity,'status':'PENDING','reason':'CATALOG_ENTRY_NOT_INSTALLED'})
                    continue
                try:
                    item=self.research_inspect(identity)
                    saved=item['saved']
                    if item['eligibility_status']!='ELIGIBLE':
                        raise ValueError(item['reason'] or item['eligibility_status'])
                    self.research_predecessors(item['catalog_entry'])
                    if saved:
                        requests.append({'task_id':identity,'status':saved['status'],'task':saved['task'],
                            'reason':saved['reason']})
                    elif submitted is not None:
                        requests.append({'task_id':identity,'status':'PENDING','reason':'ONE_SUBMISSION_PER_TICK'})
                    else:
                        result=self.submit_research(identity,submitted_by=self.research_service_submitter())
                        requests.append({'task_id':identity,'status':result['status'],'task':result['task'],'reason':None})
                        if not result['duplicate']:submitted=result['task']
                except (ValueError,KeyError,TypeError,OSError,sqlite3.Error) as error:
                    reason=str(error)
                    if not re.fullmatch('[A-Z][A-Z0-9_]{1,100}',reason):
                        reason='RESEARCH_SCHEDULE_RECONCILIATION_REQUIRED'
                    requests.append({'task_id':identity,'status':'PENDING' if reason.endswith('_PENDING') else 'BLOCKED',
                        'reason':reason})
            states={item['status'] for item in requests}
            status=('SUBMITTED' if submitted else 'EXHAUSTED' if states=={'COMPLETE'} else
                'QUEUED' if states&{'QUEUED','RUNNING'} else 'BLOCKED' if 'BLOCKED' in states else 'PENDING')
            return record(status,requests,submitted)
        except (ValueError,KeyError,TypeError,OSError,sqlite3.Error) as error:
            reason=str(error)
            if not re.fullmatch('[A-Z][A-Z0-9_]{1,100}',reason):
                reason='RESEARCH_SCHEDULE_RECONCILIATION_REQUIRED'
            return record('BLOCKED',[{'task_id':identity,'status':'BLOCKED','reason':reason}
                for identity in identifiers])
        finally:
            for handle in held:handle.close()

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
        if 'campaign_task' not in packet and binding['source']!=self.config['source']:
            self.historical_report_packet(binding)
            raise ValueError('HISTORICAL_REPORT_SOURCE_READ_ONLY')
        stage=binding['stages'][position]
        from orchestrator.disposition_context import authenticate_report_references
        retrieval = authenticate_report_references(self.config, packet, binding['source'])
        if retrieval is not None:
            from orchestrator.hosted_cycle import immutable as private_immutable
            private_immutable(task_root / ('report-references-' + stage + '.json'), encoded(retrieval))
        if 'campaign_task' in packet:
            if 'research_request_binding' in packet:
                self.research_packet(binding);self.research_eligibility(binding)
            from orchestrator.hosted_campaign_task import stage_result
            outcome=stage_result(self,binding,position,packet)
            if position<2:return outcome
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
        if 'campaign_task' not in packet:
            prompt+='\nREPORT:\n'+report_text+'\nPRIMARY EVIDENCE:\n'+json.dumps(packet)
        if self.config.get('purpose')=='LIVE_APPROVED_HANDOVER' and not self.research_packet(binding):
            published=json.loads((self.state/'delivery'/(report['id']+'-finalized')/'published.json').read_text())
            if published['report']!=report['id'] or published['phase']!='finalized':
                raise ValueError('PUBLISHED_REPORT_BINDING_CHANGED')
            prompt+='\nPUBLISHED REPORT IDENTITY:\n'+json.dumps(published)
        originals = {}
        for previous in ['continuation','review'][:position]:
            prior=self.q._receipt(binding['id'],['continuation','review'].index(previous),binding)
            if prior is None:raise ValueError('PREDECESSOR_RECEIPT_REQUIRED')
            if 'campaign_task' in packet:
                original=outcome['original_stage_outputs'][previous]
                if any(prior['output'].get(key)!=original[key] for key in ('answer','receipt')):
                    raise ValueError('CAMPAIGN_PREDECESSOR_ORIGINAL_REPLY_MISMATCH')
            originals[previous] = prior['output']['answer']
            if 'campaign_task' not in packet:
                prompt+='\n'+previous.upper()+':\n'+prior['output']['answer']
        if 'campaign_task' in packet:
            from orchestrator.campaign_disposition import prompt as disposition_prompt
            prompt = disposition_prompt(packet, binding['source'], report_text, outcome,
                originals['continuation'], originals['review'])
        response=request_broker(self.config['broker_socket'],'model_stage',{'event':self.event(binding),'stage':stage,'packet':packet,'prompt':prompt})
        if response.get('status')!='COMPLETE':raise ValueError('MODEL_COMPLETION_REQUIRED')
        return response

    def enqueue_report(self,day,receipts,task_state,reviewer_evidence=None,execution_proposal=None,trigger='scheduled-report',research_task_id=None,*,amendment_of=None):
        if trigger not in ('scheduled-report','verified-completion','installed-research-request'):raise ValueError('REPORT_TRIGGER_REQUIRED')
        if amendment_of is not None and (trigger!='scheduled-report' or execution_proposal is not None or research_task_id is not None):
            raise ValueError('REPORT_AMENDMENT_TRIGGER_REQUIRED')
        changes = None
        if self.config.get('change_request_store') is not None:
            from orchestrator.change_requests import context as change_context
            changes = change_context(Path(self.config['change_request_store']))
            # Public reports carry operational state only. Full proposals, evidence
            # and criticism stay in the immutable private task supplied to both roles.
            summary = '; '.join(row['identity']+': '+row['state']+
                ', review '+row['review_status'] for row in changes['requests'])
            if 'projection' in changes:
                summary += ('; Bounded change summary; omitted review states: '+json.dumps(
                    changes['projection']['omitted_review_status_counts'],sort_keys=True)+
                    '; full private records require inspection before acceptance.')
            task_state = {**task_state, 'recorded_change_status':
                summary or 'No recorded changes in the configured task store.'}
        source=self.config['source'];entry=None
        if trigger=='installed-research-request':
            from orchestrator.hosted_campaign_task import installed_research_request,task_contract
            from orchestrator.research_catalog import selection,eligibility
            task,evidence,request=installed_research_request(self.config,research_task_id)
            _,entry=selection(self.config,task['task_id'])
            source=request['source']
        finalized=finalize(self.state/'reports',source,day,receipts,amendment_of=amendment_of,task_state=task_state)
        report={'id':finalized['id']}
        packet={'jobs':receipts,'trigger':trigger,'decision_inbox':task_state}
        if amendment_of is not None:packet['amendment_of']=amendment_of
        if self.config.get('continuing_operations') or self.config.get('scientific_jobs_config'):
            observed_context = self.continuing_context()
            from orchestrator import scientific_context_references as context_refs
            packet['continuing_context'] = (context_refs.snapshot(self.config, observed_context,
                deferred=context_refs.enabled(self.config['source_root'], source, deferred=True),
                original_client=lambda socket, operation, body: request_broker(
                    self.config['broker_socket'], operation, body))
                if trigger == 'installed-research-request'
                and context_refs.enabled(self.config['source_root'], source) else observed_context)
        if changes is not None:packet['recorded_changes']=changes
        if reviewer_evidence is not None:packet['reviewer_evidence']=reviewer_evidence
        if execution_proposal is not None:packet['execution_proposal']=execution_proposal
        campaign=self.config.get('campaign_preparation')
        if trigger=='installed-research-request':
            if (execution_proposal is not None or receipts or reviewer_evidence!=evidence
                    or day!=request['day'] or task_state.get('research_request_identity')!=request['identity']):
                raise ValueError('INSTALLED_RESEARCH_ENQUEUE_BINDING_REQUIRED')
            packet['campaign_task']=task
            packet['campaign_artifacts']=task_contract(task)
            packet['research_request_binding']=request
            if entry is not None:
                packet['research_catalog_entry']=entry
                packet['research_eligibility']=eligibility(self.config,entry)
        if campaign is not None and task_state.get('completed_job')==campaign['trigger_job']:
            from orchestrator.hosted_campaign_task import task_contract
            if trigger!='verified-completion' or execution_proposal is not None:raise ValueError('CAMPAIGN_COMPLETION_BINDING_REQUIRED')
            packet['campaign_task']=campaign
            packet['campaign_artifacts']=task_contract(campaign)
        from orchestrator.scientific_context_references import has_references
        if trigger == 'installed-research-request' and (
                task.get('schema') == 'investigator-task/v1' or has_references(packet)):
            from orchestrator.hosted_context import selected_history_profile
            source_root = self.root if source == self.config['source'] else entry['source_root']
            if selected_history_profile(source_root, source) == 1:
                from orchestrator.disposition_context import capture_current_history
                packet = capture_current_history({**self.config, 'source': source}, packet)
        if has_references(packet):
            from orchestrator.current_scientific_input import is_current
            if not is_current(packet):
                raise ValueError('SCIENTIFIC_CONTEXT_REVIEWED_CURRENT_PLAN_REQUIRED')
        identity=digest({'source':source,'packet':packet,'report':report})
        directory=self.state/'tasks'/identity;directory.mkdir(parents=True,mode=0o700,exist_ok=True)
        # Source/evidence packets use the existing bounded private-context route;
        # published report bodies retain their smaller public-output limit.
        from orchestrator.hosted_cycle import immutable as private_immutable
        private_immutable(directory/'packet.json',encoded(packet));immutable(directory/'report.json',encoded(report))
        if 'campaign_task' in packet and source == self.config['source']:
            if packet['campaign_task'].get('schema')=='investigator-task/v1':
                from orchestrator.hosted_campaign import campaign_preflight
                from orchestrator.continuing_research import supplemental_context
                from orchestrator.hosted_context import InputTooLarge
                supplement=supplemental_context(self.config,packet['campaign_task'],packet=packet)
                try:
                    campaign_inputs=campaign_preflight(self.root,source,packet,supplement=supplement,evidence_config=self.config)
                except InputTooLarge as error:
                    private_immutable(directory/'campaign-input-projection-refused.json',
                        encoded({'status':'PROSPECTIVE_CAMPAIGN_INPUT_REFUSED','source':source,
                            'task':identity,'measurement':error.measurement,'models':0,'admissions':0,
                            'automatic_retry':False}))
                    raise
                private_immutable(directory/'campaign-input-projection.json',encoded(campaign_inputs))
            from orchestrator.campaign_disposition import preflight
            from orchestrator.hosted_context import InputTooLarge
            try:
                disposition_preflight = preflight(self.root, source, packet,
                    (self.state/'reports'/(report['id']+'.md')).read_text(), evidence_config=self.config)
            except InputTooLarge as error:
                private_immutable(directory/'disposition-input-projection-refused.json',
                    encoded({'status': 'PROSPECTIVE_DISPOSITION_INPUT_REFUSED',
                        'source': source, 'task': identity, 'measurement': error.measurement,
                        'models': 0, 'admissions': 0, 'automatic_retry': False}))
                raise
            private_immutable(directory/'disposition-input-projection.json', encoded(disposition_preflight))

        return {'id':identity,'source':source,
                'kind':'astra_turn' if trigger=='installed-research-request' else 'nightly_review',
                'thread':'primary' if trigger=='installed-research-request' else 'adjacent',
                'dependencies':[] if entry is None else [p['task'] for p in entry['predecessors']],
                'stages':['continuation','review','disposition']}

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
            except (ValueError,KeyError,TypeError,OSError,sqlite3.Error):
                status='BLOCKED' if attempt>=3 else 'RETRY'
                reason='BOOKKEEPING_EVIDENCE_PRESERVED'
                # A failed attachment must not leave a claimed review pretending
                # it is still running. Preserve its actual original review files.
                try:
                    report=json.loads((self.state/'tasks'/row['id']/'report.json').read_text())
                    queue=Queue(self.state/'reports');claim=queue.status(report['id'])
                    if claim['status']=='REVIEWING':queue.unavailable(report['id'],claim['attempt_id'],'bookkeeping-preserved')
                except (ValueError,KeyError,TypeError,OSError,sqlite3.Error):pass
            self.q.db.execute('INSERT OR REPLACE INTO bookkeeping VALUES(?,?,?,?)',(row['id'],status,attempt,reason))

    def _bookkeep(self,row):
        folder=self.state/'tasks'/row['id'];report=json.loads((folder/'report.json').read_text())
        binding=json.loads(self.q.db.execute('SELECT binding FROM tasks WHERE id=?',(row['id'],)).fetchone()[0])
        packet=json.loads((folder/'packet.json').read_text())
        if 'campaign_task' in packet:
            return self._bookkeep_campaign(folder,binding,packet,report)
        if binding['source']!=self.config['source']:self.historical_report_packet(binding)
        queue=Queue(self.state/'reports');status=queue.status(report['id'])
        review=self.q._receipt(row['id'],1,binding)['output']
        if status['status']!='REVIEWED':
            claim=status if status['status']=='REVIEWING' else queue.claim(report['id'])
            if not claim:raise ValueError('REVIEW_BOOKKEEPING_CLAIM_REQUIRED')
            r=review['receipt'];answer=review['answer']
            if not isinstance(r.get('actual_model'),str) or not r['actual_model'].startswith('claude-'):
                raise ValueError('CLAUDE_REVIEW_MODEL_IDENTITY_REQUIRED')
            queue.attach(report['id'],claim['attempt_id'],answer,{'family':'claude','model':r['actual_model'],'source':binding['source'],
                'report_sha256':report['id'],'review_sha256':hashlib.sha256(answer.encode()).hexdigest(),
                'execution_receipt_sha256':hashlib.sha256((json.dumps(r,sort_keys=True,indent=2)+'\n').encode()).hexdigest(),
                'session_id':r['session_id'],'status':'COMPLETE'})
        disposition=self.q._receipt(row['id'],2,binding)['output']['answer']
        queue.disposition(report['id'],disposition)
        if self.completions is not None:
            self.completions.finish(row['id'],json.loads((folder/'packet.json').read_text()),disposition)

    def _bookkeep_campaign(self,folder,binding,packet,report):
        """Bind the scientific disposition without inventing a report review."""
        from orchestrator.hosted_campaign_task import stage_result
        from orchestrator.hosted_campaign import BrokerStages
        outcome=stage_result(self,binding,2,packet,read_only=True)
        reader=BrokerStages(self.config['broker_socket'],self.event(binding),packet,
            client=request_broker,recovery=True)
        reader.completed=['continuation','review']
        answer,receipt=reader.call('disposition','')
        originals={**outcome['original_stage_outputs'],'disposition':{'answer':answer,'receipt':receipt}}
        for position,stage in enumerate(('continuation','review','disposition')):
            saved=self.q._receipt(binding['id'],position,binding)
            if saved is None or any(saved['output'].get(key)!=originals[stage][key] for key in ('answer','receipt')):
                raise ValueError('CAMPAIGN_PREDECESSOR_ORIGINAL_REPLY_MISMATCH')
        review=originals['review']
        from orchestrator.hosted_campaign import artifact_files
        verdict=json.loads(artifact_files(review['answer'],['review.json'])['review.json']).get('verdict')
        if verdict not in ('APPROVE','REVISE','REQUEST_CHANGES'):
            raise ValueError('CAMPAIGN_ORIGINAL_REVIEW_VERDICT_REQUIRED')
        acceptance='APPROVED_PROPOSAL_ONLY' if verdict=='APPROVE' else 'NOT_ACCEPTED'
        if (outcome.get('review_verdict',verdict)!=verdict
                or outcome.get('acceptance_status',acceptance)!=acceptance):
            raise ValueError('CAMPAIGN_ORIGINAL_REVIEW_DISPOSITION_CHANGED')
        record={'schema':'hosted-campaign-disposition/v1','status':'DISPOSITION_RECORDED',
            'task':binding['id'],'source':binding['source'],
            'campaign_status':outcome['status'],'review_verdict':verdict,
            'acceptance_status':acceptance,
            'campaign_output':outcome['campaign_output'],'campaign_receipt_sha256':outcome['campaign_receipt_sha256'],
            'artifact_sha256':outcome['artifact_sha256'],
            'reviewer':{'family':'claude','model':review['receipt']['actual_model'],
                'session_id':review['receipt']['session_id'],'model_receipt_sha256':digest(review['receipt']),
                'answer_sha256':hashlib.sha256(review['answer'].encode()).hexdigest()},
            'disposition_actor':{'family':'codex','requested_model':receipt['requested_model'],
                'actual_model':receipt.get('actual_model'),
                'model_identity_source':('CLI request; provider actual model unavailable' if receipt.get('actual_model') is None
                    else 'Provider model identity from the original model receipt'),
                'session_id':receipt['session_id'],'model_receipt_sha256':digest(receipt)},
            'disposition_sha256':hashlib.sha256(answer.encode()).hexdigest(),
            'operational_report':{'id':report['id'],'review_status':'NOT_REVIEWED_BY_SCIENTIFIC_STAGE'},
            'authority':'Disposition only; no adoption, execution, publication or new task is authorized.'}
        immutable(folder/'scientific-disposition.md',answer.encode())
        immutable(folder/'scientific-disposition.json',encoded(record))
        if self.completions is not None:self.completions.finish(binding['id'],packet,answer)


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
            except (ValueError,KeyError,TypeError,OSError,sqlite3.Error):
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
        evidence=configuration(schedule['evidence_file'],maximum=RESEARCH_EVIDENCE_MAXIMUM)
        if set(evidence) not in ({'source','receipts','task_state'},{'source','receipts','task_state','reviewer_evidence'}) or evidence['source']!=self.config['source']:raise ValueError('REPORT_EVIDENCE_SOURCE')
        # Installed evidence is a supplied snapshot, not a live queue census.
        # Capture current coordinator state in the same transaction used for
        # daily identity creation. Never read prompts or private job payloads.
        self.q.db.execute('BEGIN IMMEDIATE')
        try:
            task_state=dict(evidence['task_state'])
            task_state.update(self.coordinator_context(now))
            binding=self.enqueue_report(day,evidence['receipts'],task_state,evidence.get('reviewer_evidence'))
        finally:
            self.q.db.execute('ROLLBACK')
        # schedule owns its transaction. Concurrent callers converge on the
        # already-persisted day; an unused immutable snapshot grants no authority.
        return self.q.schedule(now,schedule['zone'],schedule['hour'],schedule['minute'],binding)

    def coordinator_context(self,now):
        """Same bounded, permitted queue census for scheduled and event reports."""
        state=self.q.status();priority={'RUNNING':0,'BLOCKED':1,'QUEUED':2,'COMPLETE':3}
        selected=sorted(state['tasks'],key=lambda row:(priority.get(row['status'],4),row['id']))[:24]
        result={'coordinator_observed_at':now.isoformat(),
            'research_schedule':self.research_schedule_status(),
            'coordinator_tasks':[{**row,'reason':row['reason'] if row['reason'] is None or len(row['reason'])<=256
                else 'REASON_TOO_LONG_SEE_PRIVATE_TASK_RECORD'} for row in selected],
            'coordinator_tasks_total':len(state['tasks']),'coordinator_tasks_omitted':len(state['tasks'])-len(selected),
            'coordinator_control':{'revision':state['revision'],'paused':bool(state['paused'])},
            'evidence_scope':'Installed evidence plus current coordinator metadata; not a census of other execution queues.',
            'research_task_scope':'The versioned scientific task record is supplied in operating context; it is not a fresh observation of a separate queue.',
            'coordinator_summary':', '.join(str(sum(row['status']==s for row in state['tasks']))+' '+s.lower()
                for s in ('QUEUED','RUNNING','COMPLETE','BLOCKED'))}
        if self.config.get('continuing_operations') or self.config.get('scientific_jobs_config'):
            observed=self.continuing_context()
            result['continuing_operation_status']=observed['continuing_operations']['operations']
            result['scientific_job_status']=observed['scientific_observation']
            result['scientific_completion_count']=len(observed['scientific_completions'])
        if self.completions is not None:
            result['completion_blocks']=[dict(row) for row in self.q.db.execute('SELECT * FROM completion_blocks')]
            result['selected_work']=[dict(row) for row in self.q.db.execute('SELECT task,status,attempts FROM selected_dispatch')]
        return result

    def recover(self):
        outcomes=[]
        def retrieve(binding,position):
            packet=json.loads((self.state/'tasks'/binding['id']/'packet.json').read_text())
            if 'campaign_task' in packet:
                from orchestrator.hosted_campaign_task import stage_result
                recovered=stage_result(self,binding,position,packet,read_only=True)
                if position<2:return recovered
            elif binding['source']!=self.config['source']:
                from orchestrator.hosted_campaign import BrokerStages
                from orchestrator.hosted_cycle import encoded as broker_encoded
                packet=self.historical_report_packet(binding)
                reader=BrokerStages(self.config['broker_socket'],self.event(binding),packet,
                    client=request_broker,recovery=True)
                reader.completed=binding['stages'][:position]
                answer,receipt=reader.call(binding['stages'][position],'')
                return {'status':'COMPLETE','duplicate':True,'answer':answer,'receipt':receipt,
                    'packet_sha256':hashlib.sha256(broker_encoded(packet)).hexdigest()}
            return request_broker(self.config['broker_socket'],'stage_status',
                {'event':self.event(binding),'stage':binding['stages'][position]})
        for row in self.q.status()['tasks']:
            if row['status'] in ('BLOCKED','RUNNING'):
                try:
                    binding=json.loads(self.q.db.execute('SELECT binding FROM tasks WHERE id=?',(row['id'],)).fetchone()[0])
                    historical=binding['source']!=self.config['source']
                    if historical and not self.research_packet(binding):self.historical_report_packet(binding)
                    outcomes.append(self.q.recover(row['id'],retrieve,completed_only=historical))
                except (ValueError,KeyError,TypeError,OSError,sqlite3.Error):
                    self.q.db.execute("UPDATE tasks SET status='BLOCKED',reason=coalesce(reason,'RECOVERY_EVIDENCE_UNAVAILABLE') WHERE id=?",(row['id'],))
        return outcomes

    def tick(self):
        from orchestrator import continuing_operations, investigator_wakes
        for name,operation in [('controls',self.controls),('recovery',self.recover),
                               ('completions',lambda:self.completions.ingest() if self.completions else None),
                               ('selected-work',lambda:self.completions.advance() if self.completions else None),
                               ('research-schedule',self.scheduled_research),
                               ('continuing-discovery',lambda:continuing_operations.discover(self)),
                               ('investigator-discovery',lambda:investigator_wakes.discover(self)),
                               ('schedule',lambda:self.scheduled_report(datetime.now(timezone.utc)))]:
            try:
                operation()
                self.q.db.execute('DELETE FROM runtime_blocks WHERE phase=?',(name,))
            except (ValueError,KeyError,TypeError,OSError,sqlite3.Error):
                self.q.db.execute('INSERT OR REPLACE INTO runtime_blocks VALUES(?,?)',(name,'EVIDENCE_OR_CONFIGURATION_REQUIRES_RECONCILIATION'))
        control_block=self.q.db.execute("SELECT 1 FROM runtime_blocks WHERE phase='controls'").fetchone()
        result={'status':'CONTROL_TRANSPORT_BLOCKED'} if control_block else self.q.tick()
        # At most one model-bearing work item per service invocation. The
        # coordinator releases branch.lock before a formal operation owns it.
        if not control_block and result.get('status')=='WAITING_FOR_ELIGIBLE_WORK':
            try:
                from orchestrator.disposition_successors import advance as disposition_advance
                successor = disposition_advance(self)
                self.q.db.execute("DELETE FROM runtime_blocks WHERE phase='disposition-successors'")
                if successor['status'] != 'NO_QUEUED_DISPOSITION_SUCCESSOR':
                    result = successor
            except (ValueError,KeyError,TypeError,OSError,sqlite3.Error):
                self.q.db.execute("INSERT OR REPLACE INTO runtime_blocks VALUES('disposition-successors','SAVED_DISPOSITION_REQUIRES_RECONCILIATION')")
                result = {'status': 'SAVED_DISPOSITION_REQUIRES_RECONCILIATION'}
        if not control_block and result.get('status')=='WAITING_FOR_ELIGIBLE_WORK':
            try:
                operation=self.continuing_step()
                self.q.db.execute("DELETE FROM runtime_blocks WHERE phase='continuing-operations'")
                if operation['status']!='DISABLED':result=operation
            except (ValueError,KeyError,TypeError,OSError,sqlite3.Error):
                self.q.db.execute("INSERT OR REPLACE INTO runtime_blocks VALUES('continuing-operations','SAVED_OPERATION_REQUIRES_RECONCILIATION')")
                result={'status':'SAVED_OPERATION_REQUIRES_RECONCILIATION'}
        self.bookkeeping()
        try:
            if not control_block:self.deliver_reports()
        except (ValueError,KeyError,TypeError,OSError,sqlite3.Error):
            self.q.db.execute("INSERT OR REPLACE INTO runtime_blocks VALUES('publication','DELIVERY_EVIDENCE_RECONCILIATION_REQUIRED')")
        try:self.notifications()
        except (ValueError,KeyError,TypeError,OSError,sqlite3.Error):
            self.q.db.execute("INSERT OR REPLACE INTO runtime_blocks VALUES('notifications','NOTIFICATION_CONFIGURATION_OR_TRANSPORT_BLOCKED')")
        return result

    def notifications(self):
        """Optional protected notices; no reply is interpreted as an action."""
        if self.config.get('notifications') is not True:return
        request_broker(self.config['broker_socket'],'flush_notifications',{})
        pending=[]
        for row in self.q.status()['tasks']:
            if row['status']=='BLOCKED' and row['reason']:
                pending.append(('block:'+row['id']+':'+row['reason'],'notify_task_block',
                    {'source':self.config['source'],'task':row['id'],'reason':row['reason']}))
        for row in self.q.db.execute("SELECT report,commit_pin FROM report_delivery WHERE status='PUBLISHED'"):
            pending.append(('report:'+row['report'],'notify_report',
                {'source':row['commit_pin'],'report':row['report'],'phase':'reviewed'}))
        for identity,operation,body in pending:
            old=self.q.db.execute('SELECT * FROM notification_delivery WHERE id=?',(identity,)).fetchone()
            if old and (old['status']=='SENT' or old['attempts']>=3):continue
            attempt=(old['attempts'] if old else 0)+1
            self.q.db.execute('INSERT OR REPLACE INTO notification_delivery VALUES(?,?,?,NULL)',(identity,'PENDING',attempt))
            try:
                result=request_broker(self.config['broker_socket'],operation,body)
                status='SENT' if result.get('status')=='SENT' else ('BLOCKED' if attempt>=3 else 'RETRY')
                self.q.db.execute('UPDATE notification_delivery SET status=?,issue=? WHERE id=?',(status,result.get('issue'),identity))
            except (ValueError,KeyError,TypeError,OSError):
                self.q.db.execute('UPDATE notification_delivery SET status=? WHERE id=?',('BLOCKED' if attempt>=3 else 'RETRY',identity))
            break

    def deliver_reports(self):
        """Separate checked delivery; unavailable publication never reruns models."""
        from orchestrator.remote_supervisor import lock
        with lock(self.state/'branch.lock'):
            if self.q.status()['paused']:return
            return self._deliver_reports()

    def _deliver_reports(self):
        from orchestrator.report_delivery import deliver
        configured=self.config.get('publication')
        if configured is not None and set(configured)!={'checkout','permission_sha256'}:
            self.q.db.execute("INSERT OR REPLACE INTO runtime_blocks VALUES('publication','PUBLICATION_CONFIGURATION_REQUIRED')")
            return
        for row in self.q.db.execute("SELECT task FROM bookkeeping WHERE status='COMPLETE' ORDER BY rowid").fetchall():
            task=self.state/'tasks'/row['task']
            report=json.loads((task/'report.json').read_text())['id']
            if 'research_request_binding' in json.loads((task/'packet.json').read_text()):
                self.q.db.execute('INSERT OR IGNORE INTO report_delivery VALUES(?,?,0,?,NULL)',
                    (report,'PRIVATE_ONLY','Configured research artifacts require their separate publication authority.'))
                continue
            prior=self.q.db.execute('SELECT * FROM report_delivery WHERE report=?',(report,)).fetchone()
            if prior and (prior['status']=='PUBLISHED' or prior['attempts']>=3):continue
            if configured is None:
                self.q.db.execute('INSERT OR IGNORE INTO report_delivery VALUES(?,?,0,?,NULL)',
                    (report,'PRIVATE_ONLY','Writer permission and protected publication configuration remain reserved.'))
                continue
            attempt=(prior['attempts'] if prior else 0)+1
            self.q.db.execute('INSERT OR REPLACE INTO report_delivery VALUES(?,?,?,NULL,NULL)',(report,'DELIVERING',attempt))
            try:
                result=deliver(self.state/'reports',report,configured['checkout'],self.state/'delivery',
                    self.config['broker_socket'],configured['permission_sha256'])
                self.q.db.execute('UPDATE report_delivery SET status=?,commit_pin=?,reason=NULL WHERE report=?',
                    ('PUBLISHED',result['source'],report))
            except (ValueError,KeyError,TypeError,OSError,sqlite3.Error):
                self.q.db.execute('UPDATE report_delivery SET status=?,reason=? WHERE report=?',
                    ('BLOCKED' if attempt>=3 else 'RETRY','DELIVERY_PRESERVED_RECONCILE_BEFORE_NEW_COMMIT',report))
            break  # At most one delivery per deterministic poll.

    def status(self):
        from orchestrator.disposition_successors import status as disposition_status
        return {'disposition_successors': disposition_status(self.config), 'source':self.config['source'],'purpose':self.config.get('purpose','UNSPECIFIED'),
                'report_schedule_configured':self.config.get('report_schedule') is not None,
                'publication_configured':self.config.get('publication') is not None,
                'notifications_configured':self.config.get('notifications') is True,
                'report_directory':str(self.state/'reports'),
                'research_submissions':[dict(row) for row in self.q.db.execute('SELECT * FROM research_submissions')],
                'research_schedule':self.research_schedule_status(),
                'continuing_research':self.continuing_context() if self.config.get('continuing_operations') or self.config.get('scientific_jobs_config') else {'status':'DISABLED'},
                'execution_jobs':[] if self.completions is None else self.completions.controller.status()['jobs'],
                **self.q.status(),
                'completion_events':[] if self.completions is None else [dict(row) for row in self.q.db.execute('SELECT * FROM completion_ingest')],
                'selected_work':[] if self.completions is None else [dict(row) for row in self.q.db.execute('SELECT task,status,attempts FROM selected_dispatch')],
                'completion_blocks':[] if self.completions is None else [dict(row) for row in self.q.db.execute('SELECT * FROM completion_blocks')],
                'runtime_blocks':[dict(row) for row in self.q.db.execute('SELECT * FROM runtime_blocks')],
                'bookkeeping':[dict(row) for row in self.q.db.execute('SELECT * FROM bookkeeping')],
                'report_delivery':[dict(row) for row in self.q.db.execute('SELECT * FROM report_delivery')],
                'notification_delivery':[dict(row) for row in self.q.db.execute('SELECT * FROM notification_delivery')],
                'controls':[json.loads(row[0]) for row in self.q.db.execute('SELECT outcome FROM control_delivery')]}


def control_status(config, operation='control-status'):
    """Authenticated deterministic controls remain available if research inputs fail.

    No Runtime construction, broker/model request, scientific validation or branch
    lock belongs in this path. Coordinator.control still serializes admission and
    checks the expected revision and the original idempotency binding.
    """
    if os.getuid()!=config['controller_uid'] or operation not in ('control-status','controls'):
        raise ValueError('NONROOT_CONTROL_IDENTITY_REQUIRED')
    from types import SimpleNamespace
    checked_source(config['source_root'],config['source'])
    state=Path(config['state'])
    q=Coordinator(state,{},lambda binding: (_ for _ in ()).throw(ValueError('CONTROL_MODEL_PATH_FORBIDDEN')))
    q.db.execute('CREATE TABLE IF NOT EXISTS control_delivery(id TEXT PRIMARY KEY,outcome TEXT)')
    view=SimpleNamespace(config=config,state=state,q=q)
    if operation=='controls':return Runtime.controls(view)
    return {**q.status(),'source':config['source'],'purpose':config.get('purpose','UNSPECIFIED'),
            'controls':[json.loads(row[0]) for row in q.db.execute('SELECT outcome FROM control_delivery ORDER BY id')],
            'runtime_status_available':False,'status_scope':'CONTROLS_AND_SAVED_TASKS_ONLY',
            'execution_jobs':[],'report_directory':str(state/'reports')}


def controller_command(config,operation,config_path='/etc/research-system/handover-controller.json',task_id=None,submitted_by=None,replacement=None):
    """Fixed non-root control transport, never a model or arbitrary command."""
    if os.getuid()!=0 or operation not in ('status','control-status','controls','submit-research','research-list','research-inspect','operation-status','operation-recover','operation-replace','investigator-status','investigator-recover','disposition-request','disposition-revise','disposition-status','disposition-recover'):raise ValueError('OPERATOR_CONTROL_TRANSPORT_REQUIRED')
    from orchestrator.research_catalog import identifier
    if task_id is not None:
        identifier(task_id)
        if operation not in ('submit-research','research-inspect','operation-recover','operation-replace','investigator-recover','disposition-request','disposition-revise','disposition-recover'):raise ValueError('RESEARCH_TASK_ARGUMENT_REQUIRED')
    if operation in ('research-inspect','operation-recover','operation-replace','investigator-recover','disposition-request','disposition-revise','disposition-recover') and task_id is None:raise ValueError('SAVED_TASK_OR_OPERATION_ID_REQUIRED')
    if operation in ('operation-recover','operation-replace','investigator-recover','disposition-request','disposition-revise','disposition-recover'):
        from orchestrator.continuing_operations import pin
        pin(task_id)
    if submitted_by is not None:
        from orchestrator.change_requests import actor
        actor(submitted_by)
        if operation not in ('submit-research','operation-replace','disposition-request','disposition-revise'):raise ValueError('RESEARCH_SUBMITTER_OPERATION_REQUIRED')
    if (operation in ('operation-replace','disposition-request','disposition-revise')) != (replacement is not None):raise ValueError('REPLACEMENT_ARGUMENTS_REQUIRED')
    if replacement is not None and (not isinstance(replacement,dict) or set(replacement) not in ({'reason','expected_source','change_request'}, {'reason','expected_source','change_request','previous_request'}, {'reason','expected_source','change_request','previous_request','predecessor_sha256','control_revision'})):raise ValueError('REPLACEMENT_ARGUMENTS_REQUIRED')
    if operation in ('disposition-request','disposition-revise') and submitted_by is None:
        raise ValueError('DISPOSITION_REQUEST_ACTOR_REQUIRED')
    if operation == 'disposition-request' and 'previous_request' in replacement:
        raise ValueError('DISPOSITION_REQUEST_HAS_NO_RETRY_CHAIN')
    if operation == 'disposition-revise' and set(replacement) != {
            'reason','expected_source','change_request','previous_request','predecessor_sha256','control_revision'}:
        raise ValueError('DISPOSITION_REVISION_ARGUMENTS_REQUIRED')
    if operation != 'disposition-revise' and replacement is not None and (
            'predecessor_sha256' in replacement or 'control_revision' in replacement):
        raise ValueError('DISPOSITION_REVISION_ARGUMENTS_ONLY')
    import pwd
    if pwd.getpwuid(config['controller_uid']).pw_name!='research-controller':raise ValueError('CONTROLLER_ROLE_REQUIRED')
    checked_source(config['source_root'],config['source'])
    command=['/usr/sbin/runuser','-u','research-controller','--','env','-i','PATH=/usr/bin:/bin',
        'PYTHONDONTWRITEBYTECODE=1','PYTHONPATH='+config['source_root'],'/usr/bin/python3','-B',
        '-m','orchestrator.handover_runtime','--config',str(config_path),operation]
    if task_id is not None:command.append(task_id)
    if submitted_by is not None:command+=['--submitter',json.dumps(submitted_by,sort_keys=True)]
    if replacement is not None:
        command+=['--reason',replacement['reason'],'--expected-source',replacement['expected_source'],
                  '--change-request',replacement['change_request']['request_id'],
                  '--applied-event',replacement['change_request']['applied_event']]
        if 'previous_request' in replacement: command+=['--previous-request',replacement['previous_request']]
        if operation == 'disposition-revise':
            command+=['--predecessor-sha256',json.dumps(replacement['predecessor_sha256'],sort_keys=True),
                      '--revision',str(replacement['control_revision'])]
    try:
        result=subprocess.run(command,capture_output=True,timeout=60,check=True)
    except (subprocess.TimeoutExpired,subprocess.CalledProcessError):
        raise ValueError('CONTROL_TRANSPORT_PENDING_CHECK_STATUS_NO_BLIND_RETRY') from None
    if len(result.stdout)>100000:raise ValueError('CONTROL_RESPONSE_LIMIT')
    return json.loads(result.stdout)


def operator_request(config,action,revision=None,request_id=None,config_path=None):
    if os.getuid()!=0:raise ValueError('OPERATOR_ADMIN_REQUIRED')
    if action not in ('pause','resume'):raise ValueError('CONTROL_ACTION')
    if revision is None:
        state=(controller_command(config,'control-status') if config_path is None
               else controller_command(config,'control-status',config_path));revision=state['revision']
        if bool(state['paused'])==(action=='pause'):
            return {'status':'ALREADY_'+('PAUSED' if state['paused'] else 'RESUMED'),'revision':revision}
    if request_id is None:request_id=digest({'source':config['source'],'action':action,'revision':revision})
    directory=Path(config['control_inbox'])
    if directory.is_symlink() or directory.stat().st_uid!=0 or directory.stat().st_mode & 0o022:raise ValueError('PROTECTED_CONTROL_INBOX')
    request={'source':config['source'],'control':{'id':request_id,'expected_revision':revision,'action':action}}
    # Numeric/hash-derived filename; no user-controlled traversal.
    path=directory/(digest(request)+'.json')
    immutable(path,encoded(request));os.chown(path,0,config['controller_gid']);os.chmod(path,0o640)
    return {'status':'REQUESTED_NOT_YET_APPLIED','request':digest(request)}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True)
    p.add_argument('operation',choices=['tick','status','control-status','controls','pause','resume','submit-research','research-list','research-inspect','operation-status','operation-recover','operation-replace','investigator-status','investigator-recover','disposition-request','disposition-revise','disposition-status','disposition-recover'])
    p.add_argument('task_id',nargs='?')
    p.add_argument('--submitter',help='Explicit human/agent attribution JSON; never an authorization grant')
    p.add_argument('--reason',help='Why this linked source-bound continuation is requested; no model runs inline')
    p.add_argument('--expected-source',help='Exact current installed source for the explicit continuation request')
    p.add_argument('--change-request',help='Current independently reviewed repair request ID')
    p.add_argument('--applied-event',help='Exact current-source APPLIED event in that request')
    p.add_argument('--previous-request',help='Exact previous replacement or never-started disposition request identity')
    p.add_argument('--predecessor-sha256',help='For disposition-revise only: exact four original filename/SHA256 bindings')
    p.add_argument('--revision',type=int);p.add_argument('--request-id')
    p.add_argument('--human',action='store_true')
    a=p.parse_args();config=configuration(a.config)
    if a.task_id is not None:
        from orchestrator.research_catalog import identifier
        identifier(a.task_id)
        if a.operation not in ('submit-research','research-inspect','operation-recover','operation-replace','investigator-recover','disposition-request','disposition-revise','disposition-recover'):raise ValueError('RESEARCH_TASK_ARGUMENT_REQUIRED')
    if a.operation in ('research-inspect','operation-recover','operation-replace','investigator-recover','disposition-request','disposition-revise','disposition-recover') and a.task_id is None:raise ValueError('SAVED_TASK_OR_OPERATION_ID_REQUIRED')
    if a.operation in ('operation-recover','operation-replace','investigator-recover','disposition-request','disposition-revise','disposition-recover'):
        from orchestrator.continuing_operations import pin
        pin(a.task_id)
    submitted_by=None if a.submitter is None else json.loads(a.submitter)
    if submitted_by is not None and a.operation not in ('submit-research','operation-replace','disposition-request','disposition-revise'):raise ValueError('RESEARCH_SUBMITTER_OPERATION_REQUIRED')
    if a.operation in ('submit-research','operation-replace','disposition-request','disposition-revise') and os.getuid()==0 and a.human:
        if submitted_by is not None:raise ValueError('HUMAN_TRANSPORT_SUBMITTER_FIXED')
        submitted_by={'kind':'human','identity':'ssh-uid:0',
            'identity_source':'authenticated_root_transport_declared_human'}
    replacement=None
    if a.operation in ('operation-replace','disposition-request','disposition-revise'):
        if not all((a.reason,a.expected_source,a.change_request,a.applied_event)) or submitted_by is None:raise ValueError('REPLACEMENT_REASON_SOURCE_CHANGE_AND_ACTOR_REQUIRED')
        replacement={'reason':a.reason,'expected_source':a.expected_source,
                     'change_request':{'request_id':a.change_request,'applied_event':a.applied_event}}
        if a.previous_request is not None:
            if a.operation == 'disposition-request':
                raise ValueError('DISPOSITION_REQUEST_HAS_NO_RETRY_CHAIN')
            replacement['previous_request']=a.previous_request
        if a.operation == 'disposition-revise':
            if a.previous_request is None or a.predecessor_sha256 is None or a.revision is None:
                raise ValueError('DISPOSITION_REVISION_ARGUMENTS_REQUIRED')
            replacement.update(predecessor_sha256=json.loads(a.predecessor_sha256),
                               control_revision=a.revision)
    elif any(v is not None for v in (a.reason,a.expected_source,a.change_request,a.applied_event,a.previous_request)):
        raise ValueError('REPLACEMENT_ARGUMENTS_FOR_EXPLICIT_REQUEST_ONLY')
    if a.predecessor_sha256 is not None and a.operation != 'disposition-revise':
        raise ValueError('DISPOSITION_REVISION_ARGUMENTS_ONLY')
    if a.operation in ('pause','resume'):
        result=operator_request(config,a.operation,a.revision,a.request_id,a.config)
        if result['status']=='REQUESTED_NOT_YET_APPLIED':
            outcomes=controller_command(config,'controls',a.config)
            matched=next((row for row in outcomes if row['request']==result['request']),None)
            if matched is not None:result=matched
            else:
                state=controller_command(config,'control-status',a.config)
                matched=next((row for row in state['controls'] if row['request']==result['request']),None)
                if matched is not None:result={**matched,'duplicate':True}
    elif a.operation in ('status','control-status','submit-research','research-list','research-inspect','operation-status','operation-recover','operation-replace','investigator-status','investigator-recover','disposition-request','disposition-revise','disposition-status','disposition-recover') and os.getuid()==0:
        result=controller_command(config,a.operation,a.config,a.task_id,submitted_by,**({'replacement':replacement} if replacement is not None else {}))
    elif a.operation in ('controls','control-status'):
        result=control_status(config,a.operation)
    else:
        try:runtime=Runtime(config)
        except (ValueError,KeyError,TypeError,OSError):
            if a.operation!='status':raise
            result=control_status(config)
            result['reason']='RESEARCH_STATUS_UNAVAILABLE_CONTROLS_REMAIN_AVAILABLE'
            print(text(json.dumps(result,indent=2)));return
        from orchestrator import continuing_operations, investigator_wakes, authority_replacements, disposition_successors
        result=(disposition_successors.revise(runtime,a.task_id,by=submitted_by,**replacement) if a.operation=='disposition-revise' else
                disposition_successors.request(runtime,a.task_id,by=submitted_by,**replacement) if a.operation=='disposition-request' else
                disposition_successors.status(config) if a.operation=='disposition-status' else
                disposition_successors.recover(runtime,a.task_id) if a.operation=='disposition-recover' else
                continuing_operations.status(config) if a.operation=='operation-status' else
                authority_replacements.request(runtime,a.task_id,by=submitted_by,**replacement) if a.operation=='operation-replace' else
                continuing_operations.recover(runtime,a.task_id) if a.operation=='operation-recover' else
                investigator_wakes.status(config) if a.operation=='investigator-status' else
                investigator_wakes.recover(runtime,a.task_id) if a.operation=='investigator-recover' else
                runtime.submit_research(a.task_id,submitted_by=submitted_by) if a.operation=='submit-research' else
                runtime.research_list() if a.operation=='research-list' else
                runtime.research_inspect(a.task_id) if a.operation=='research-inspect' else
                runtime.status() if a.operation=='status' else (runtime.tick() if a.operation=='tick' else runtime.controls()))
    if a.human and isinstance(result,dict):
        if a.operation=='status':
            scheduled=result.get('research_schedule',{'status':'DISABLED','requests':[]})
            lines=['Installed source: '+result['source'],'Configured purpose: '+result['purpose'],
                   ('Paused' if result['paused'] else 'Not paused; timer/admission activation is not implied')+'; control revision '+str(result['revision']),
                   'Finite research schedule: '+scheduled['status'].lower().replace('_',' ')+' (saved observation).']
            lines+=['- '+row['task_id']+': '+row['status'].lower().replace('_',' ')
                +(' — '+row['reason'] if row.get('reason') else '') for row in scheduled.get('requests',[])[:4]]
            if len(scheduled.get('requests',[]))>4:lines.append('Additional scheduled requests are visible in JSON status.')
            successors = result.get('disposition_successors', {}).get('successors', [])
            for successor in successors[-8:]:
                lines.append('Disposition continuation for '+successor['origin_task'][:12]+': '
                    +successor['status'].lower().replace('_',' ')
                    +'; original task remains blocked.')
            if successors:
                lines.append('Inspect saved disposition-status; original-only recovery uses disposition-recover.')
            continuing=result.get('continuing_research',{})
            investigator=continuing.get('investigator',{})
            if investigator:
                lines.append('Investigator: '+investigator['status'].lower().replace('_',' '))
                lines+=['- '+row['wake'][:12]+': '+row['status'].lower().replace('_',' ')
                    +(' — '+row['reason'] if row.get('reason') else '') for row in investigator['wakes'][-8:]]
                lines.append('Saved investigator work and original-only recovery: investigator-status / investigator-recover.')
            operations=continuing.get('continuing_operations',{})
            observation=continuing.get('scientific_observation',{})
            if operations:
                lines.append('Continuing research: '+operations['status'].lower().replace('_',' '))
                lines+=['- '+row['operation'][:12]+': '+(row.get('kind') or 'unidentified operation')+'; '+row['status']
                    +(' ? '+row['reason'] if row.get('reason') else '') for row in operations['operations'][:12]]
                if len(operations['operations'])>12:lines.append('Additional saved work: operation-status.')
                for row in operations['operations']:
                    if row.get('linked_replacement'):
                        replacement=row['linked_replacement']
                        lines.append('  Linked replacement '+str(replacement['replacement'])+' for '+row['operation'][:12]+': '+replacement['status']
                            +'; '+replacement.get('reason','')+'; inspect full original and replacement with operation-status.')
            if observation:
                lines.append('Scientific completion observation: '+observation['status'].lower().replace('_',' '))
                lines+=['- '+row['id']+': '+row['status'] for row in observation.get('jobs',[])[:12]]
                lines.append('Completed job events available for analysis: '+str(len(continuing.get('scientific_completions',[]))))
            lines+=['Attention: '+row['phase']+' ? '+row['reason'] for row in result.get('runtime_blocks',[])[:12]]
            lines.append('Recorded coordinator tasks:')
            lines+=['- '+row['id'][:12]+': '+row['status']+(' — '+row['reason'] if row['reason'] else '') for row in result['tasks'][:24]]
            if len(result['tasks'])>24:lines.append('Additional tasks omitted; use the JSON status interface.')
            lines+=['Recorded execution jobs:']+['- '+row['job_id']+': '+row['status'] for row in result['execution_jobs'][:24]]
            lines.append('Reports: '+result['report_directory']+'; checked public links appear in report delivery records.')
            print(text('\n'.join(lines)))
        else:print(text(json.dumps(result,indent=2)))
    else:print(text(json.dumps(result)))


if __name__=='__main__':main()
