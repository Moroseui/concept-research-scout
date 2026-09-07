"""Campaign artifacts through the existing protected three-stage model broker.

This adapter supplies no credential, admission grant, scheduler or patient runner.
A trusted caller must bind the completion and source and use the protected socket.
The shared campaign pipeline still checks its scientific context and opposing
families. One author/reviewer round leaves the third stage for a disposition.
"""
import hashlib
import json
from pathlib import Path
import re
from orchestrator.campaign_pipeline import MODES, execute
from orchestrator.handover_runtime import request_broker
from orchestrator.hosted_cycle import encoded, immutable
from orchestrator.public_export import text



def artifact_files(answer,names):
    """Parse checked file contents, never execute a model-produced wrapper."""
    raw=answer.strip()
    match=re.fullmatch(r'```(?:json)?\s*\n(.*)\n```',raw,re.S)
    if match:raw=match.group(1)
    try:files=json.loads(raw)
    except json.JSONDecodeError as error:raise ValueError('HOSTED_CAMPAIGN_INVALID_JSON') from error
    if not isinstance(files,dict) or set(files)!=set(names) or any(not isinstance(v,str) for v in files.values()):
        raise ValueError('HOSTED_CAMPAIGN_FILE_SCHEMA')
    for content in files.values():
        text(content,limit=30000)
        if not content.strip():raise ValueError('HOSTED_CAMPAIGN_EMPTY_ARTIFACT')
    return files


class BrokerStages:
    def __init__(self, socket, event, packet, *, client=request_broker, recovery=False):
        self.socket=socket;self.event=event;self.packet=packet;self.client=client
        if type(recovery) is not bool:raise ValueError('HOSTED_CAMPAIGN_RECOVERY_MODE')
        self.recovery=recovery
        self.completed=[];self.receipts={};self.mode=None

    def call(self, stage, prompt):
        expected=('continuation','review','disposition')
        if len(self.completed)>=3 or stage!=expected[len(self.completed)]:
            raise ValueError('HOSTED_CAMPAIGN_STAGE_ORDER_OR_BOUND')
        if self.recovery:
            response=self.client(self.socket,'stage_status',{'event':self.event,'stage':stage})
        else:
            response=self.client(self.socket,'model_stage',{'event':self.event,'stage':stage,
                                                          'packet':self.packet,'prompt':prompt})
        if response.get('status')!='COMPLETE':
            raise ValueError('HOSTED_CAMPAIGN_BLOCKED_RECONCILE_NO_RETRY')
        # Leave room for the coordinator's receipt envelope; validate escaped
        # JSON size, not only the unescaped answer bytes. Originals stay private.
        text(json.dumps(response),limit=80000)
        answer=response['answer'];receipt=response['receipt']
        text(answer,limit=80000)
        model='claude-fable-5' if stage=='review' else 'gpt-6-astra'
        if (receipt.get('requested_model')!=model or receipt.get('returncode')!=0
                or receipt.get('answer_sha256')!=hashlib.sha256(answer.encode()).hexdigest()
                or response.get('packet_sha256')!=hashlib.sha256(encoded(self.packet)).hexdigest()
                or not re.fullmatch('[0-9a-f]{64}',receipt.get('operating_context_sha256',''))):
            raise ValueError('HOSTED_CAMPAIGN_RECEIPT_BINDING')
        if stage=='review' and receipt.get('actual_model')!=model:
            raise ValueError('HOSTED_CAMPAIGN_REVIEW_MODEL')
        self.receipts[stage]={'receipt':receipt,'duplicate':response.get('duplicate')}
        self.completed.append(stage)
        return answer,receipt

    def __call__(self, sc, directory, family, stage, body, names):
        index=len(self.completed)
        if index>=2 or family!=('codex','claude')[index]:
            raise ValueError('HOSTED_CAMPAIGN_AUTHOR_REVIEW_BOUND')
        if (index==0 and (stage not in ('campaign_readiness','campaign_discuss')
                or names!=MODES[stage.removeprefix('campaign_')])) or (index==1 and (names!=['review.json'] or stage!='campaign_'+str(self.mode)+'_review')):
            raise ValueError('HOSTED_CAMPAIGN_ARTIFACT_SCOPE')
        if index==0:self.mode=stage.removeprefix('campaign_')
        prompt=('Produce the requested scientific artifact contents as ONE JSON object whose keys are exactly '
                +json.dumps(names)+'. Each value must be a string containing that file body. '
                'Keep the entire JSON response below 80000 UTF-8 bytes and each file below 30000 UTF-8 bytes. '
                'The controller writes these checked files; do not use tools or claim to have written them. '
                'Keep proposals distinct from ratification and launch authority.\n'+body)
        answer,receipt=self.call(('continuation','review')[index],prompt)
        files=artifact_files(answer,names)
        # The private original broker receipts remain authoritative. These are
        # validated transport-derived provenance, not manufactured model receipts.
        record={'family_effective':family,'exit_class':'ok','ci':False,
                'runner':{'adapter':'protected-hosted-campaign-v1'},
                'requested_model':receipt['requested_model'],'actual_model':receipt.get('actual_model'),
                'model_receipt_sha256':hashlib.sha256(encoded(receipt)).hexdigest(),
                'operating_context_sha256':receipt['operating_context_sha256'],
                'original_protocol_private':True,'event':self.event,
                'packet_sha256':hashlib.sha256(encoded(self.packet)).hexdigest(),
                'broker_duplicate':self.receipts[('continuation','review')[index]]['duplicate'],
                'recovered_original':self.recovery}
        for name,content in files.items():immutable(Path(directory)/name,content.encode())
        immutable(Path(directory)/(stage+'.hosted-provenance.json'),encoded(record))
        return record


def run_pipeline(sc, mode, request, output, stages):
    if mode not in ('readiness','discuss'):raise ValueError('HOSTED_CAMPAIGN_PREPARATION_ONLY')
    if (stages.packet.get('campaign_artifacts')!={'version':1,'experiment':'P001','mode':mode}
            or type(stages.packet['campaign_artifacts']['version']) is not int):
        raise ValueError('HOSTED_CAMPAIGN_PACKET_CONTRACT')
    return execute(sc,mode,'P001',request,output,max_rounds=1,stage_runner=stages,
                   initiator={'kind':'agent','family':'codex','model':'gpt-6-astra',
                              'route':'protected-hosted-campaign-v1','event':stages.event,
                              'packet_sha256':hashlib.sha256(encoded(stages.packet)).hexdigest()})


def recover_projection(sc,mode,request,original,output,stages):
    """Restore derived artifacts from verified original broker replies only.

    Existing files and contradictory human edits are never overwritten. A missing
    or unsuccessful original stage is a block, not permission for a model retry.
    The output is explicitly a recovery projection, not a fresh reviewer session.
    """
    from orchestrator.campaign_pipeline import grounding
    from orchestrator.research_context import evidence_context
    if not stages.recovery:raise ValueError('READ_ONLY_RECOVERY_CLIENT_REQUIRED')
    if mode not in ('readiness','discuss'):raise ValueError('HOSTED_CAMPAIGN_PREPARATION_ONLY')
    original=Path(original);output=Path(output)
    permitted=Path(sc.ROOT)/'campaigns/isles24-pilot/pipeline'
    if any(p.is_symlink() for p in (original,*original.parents)) or not original.resolve().is_relative_to(permitted.resolve()):
        raise ValueError('RECOVERY_ORIGINAL_PATH')
    if output.exists() or output.resolve().is_relative_to(original.resolve()):raise ValueError('FRESH_RECOVERY_PROJECTION_REQUIRED')
    if (original/'request.json').is_symlink() or (original/'round-1').is_symlink():
        raise ValueError('RECOVERY_ORIGINAL_PATH')
    prior_raw=(original/'request.json').read_bytes()
    prior=json.loads(prior_raw)
    initiator=prior.get('initiator',{})
    if (initiator.get('event')!=stages.event or initiator.get('packet_sha256')!=hashlib.sha256(encoded(stages.packet)).hexdigest()):
        raise ValueError('RECOVERY_ORIGINAL_TURN_BINDING_REQUIRED')
    context=grounding(sc.ROOT,'P001')
    context['related-evidence.json']=json.dumps(evidence_context(sc.ROOT,'isles24-prediction'))
    hashes={k:hashlib.sha256(v.encode()).hexdigest() for k,v in context.items()}
    if any(prior.get(k)!=v for k,v in {'mode':mode,'experiment':'P001','request':request,'max_rounds':1,'input_sha256':hashes}.items()):
        raise ValueError('RECOVERY_REQUEST_OR_CONTEXT_CHANGED')
    cached={}
    for stage,names in [('continuation',MODES[mode]),('review',['review.json'])]:
        response=stages.client(stages.socket,'stage_status',{'event':stages.event,'stage':stage})
        # Reuse all normal response/packet/model checks without making a model call.
        def read_cached(socket,operation,body,response=response):
            if operation!='stage_status':raise ValueError('RECOVERY_MODEL_CALL_FORBIDDEN')
            return response
        checker=BrokerStages(stages.socket,stages.event,stages.packet,client=read_cached,recovery=True)
        if stage=='review':checker.completed=['continuation']
        answer,_=checker.call(stage,'')
        files=artifact_files(answer,names)
        for name,content in files.items():
            existing=original/'round-1'/name
            if existing.is_symlink() or (existing.exists() and existing.read_bytes()!=content.encode()):
                raise ValueError('RECOVERY_PRESERVES_CONFLICTING_ORIGINAL')
        cached[stage]=response
    def replay(socket,operation,body):
        if operation!='stage_status' or body['event']!=stages.event:raise ValueError('RECOVERY_MODEL_CALL_FORBIDDEN')
        return cached[body['stage']]
    restored=BrokerStages(stages.socket,stages.event,stages.packet,client=replay,recovery=True)
    receipt=run_pipeline(sc,mode,request,output,restored)
    immutable(output/'recovery.json',encoded({'status':'RECOVERED_ORIGINAL_MODEL_ARTIFACTS',
        'original_request_sha256':hashlib.sha256(prior_raw).hexdigest(),
        'event':stages.event,'packet_sha256':hashlib.sha256(encoded(stages.packet)).hexdigest(),
        'new_model_calls':0,'new_review':False,'original_preserved':True}))
    return receipt
