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


def checked_reply(response, stage, packet_sha256):
    """Validate an unchanged original reply against its actual bound packet hash."""
    if stage not in ('continuation','review','disposition'):
        raise ValueError('HOSTED_CAMPAIGN_STAGE_ORDER_OR_BOUND')
    if response.get('status')!='COMPLETE':
        raise ValueError('HOSTED_CAMPAIGN_BLOCKED_RECONCILE_NO_RETRY')
    text(json.dumps(response),limit=80000)
    answer=response['answer'];receipt=response['receipt']
    text(answer,limit=80000)
    model='claude-fable-5' if stage=='review' else 'gpt-6-astra'
    if (receipt.get('requested_model')!=model or receipt.get('returncode')!=0
            or receipt.get('answer_sha256')!=hashlib.sha256(answer.encode()).hexdigest()
            or response.get('packet_sha256')!=packet_sha256
            or not re.fullmatch('[0-9a-f]{64}',receipt.get('operating_context_sha256',''))):
        raise ValueError('HOSTED_CAMPAIGN_RECEIPT_BINDING')
    if stage=='review' and receipt.get('actual_model')!=model:
        raise ValueError('HOSTED_CAMPAIGN_REVIEW_MODEL')
    return answer,receipt


CAMPAIGN_GROUNDING_VERSION = 1
GROUNDING_PREFIX = 'SOURCE-BOUND HOSTED INVESTIGATOR INPUT:\n'
GROUNDING_SCHEMA = 'hosted-investigator-grounding/v1'
GROUNDING_REFERENCE = 'same-prompt-investigator-grounding/v1'
CHARTER = 'campaigns/isles24-pilot/pipeline/prediction-charter-20260906-v1/'
GROUNDING_TARGETS = {
    'campaigns/isles24-pilot/CAMPAIGN.md': ('documents','campaigns/isles24-pilot/CAMPAIGN.md','content'),
    **{name: ('shared_policy','operating_context','documents',name,'text') for name in (
        'docs/operations/CONTINUING_RESEARCH_AUTHORIZATION_20260911.md',
        'docs/operations/REMOTE_OPERATING_DIRECTION.md',
        'docs/operations/CLAUDE_REVIEWER_DIRECTIVE.md')},
    **{CHARTER+name: ('selected_scientific_context',CHARTER+name,'content') for name in (
        'receipt.json','round-1/CHARTER.proposed.md','round-1/RUBRIC.proposed.md',
        'round-1/PROMPTS.proposed.md','round-1/P001_ADOPTION.proposed.md','round-1/review.json')},
    'campaigns/isles24-pilot/prediction_selection.json':
        ('selected_scientific_context','campaigns/isles24-pilot/prediction_selection.json','content'),
}


def grounding_version(root, source):
    """Read the marker only from the already checked immutable source."""
    import ast
    from orchestrator.remote_supervisor import checked_source
    from orchestrator.scientific_authority import read
    root = checked_source(root, source)
    tree = ast.parse(read(Path(root)/'orchestrator/hosted_campaign.py'))
    stores = [n for n in ast.walk(tree) if isinstance(n,ast.Name)
        and n.id=='CAMPAIGN_GROUNDING_VERSION' and isinstance(n.ctx,(ast.Store,ast.Del))]
    definitions = [n for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1
        and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='CAMPAIGN_GROUNDING_VERSION']
    if not stores: return 0
    if (len(stores)!=1 or len(definitions)!=1 or not isinstance(definitions[0].value,ast.Constant)
            or type(definitions[0].value.value) is not int or definitions[0].value.value!=1):
        raise ValueError('SOURCE_BOUND_CAMPAIGN_GROUNDING_VERSION_REQUIRED')
    return 1


def artifact_prompt(body, names, *, evidence_enabled=False):
    return ('Produce the requested scientific artifact contents as ONE JSON object whose keys are exactly '
        +json.dumps(names)+'. Each value must be a string containing that file body. '
        'Keep the entire JSON response below 80000 UTF-8 bytes and each file below 30000 UTF-8 bytes. '
        + ('The controller writes these checked files; only bound read-only evidence tools are permitted. '
           'Do not claim to have written files or execute actions. ' if evidence_enabled else
           'The controller writes these checked files; do not use tools or claim to have written them. ')
        + 'Keep proposals distinct from ratification and launch authority.\n'+body)


def _campaign_task(packet, source):
    from orchestrator.hosted_campaign_task import task_contract
    task = packet.get('campaign_task')
    binding = packet.get('research_request_binding')
    if (packet.get('trigger')!='installed-research-request' or not isinstance(task,dict)
            or task.get('schema')!='investigator-task/v1' or task.get('mode')!='investigate'
            or not isinstance(binding,dict) or binding.get('source')!=source
            or binding.get('task_id')!=task.get('task_id')
            or task_contract(task)!=packet.get('campaign_artifacts')):
        raise ValueError('CAMPAIGN_GROUNDING_TASK_SOURCE_CHANGED')
    return task


def _literal(current, name):
    path = GROUNDING_TARGETS[name]
    try:
        value = current
        for key in path: value=value[key]
    except (KeyError,TypeError) as error:
        raise ValueError('CAMPAIGN_GROUNDING_LITERAL_TARGET_MISSING') from error
    if not isinstance(value,str):
        raise ValueError('CAMPAIGN_GROUNDING_DIRECT_LITERAL_REQUIRED')
    return value


def _reference(current, name, source):
    value=_literal(current,name)
    return {'schema':GROUNDING_REFERENCE,'source':source,'name':name,
        'literal_location':['operating_context',*GROUNDING_TARGETS[name]],
        'sha256':hashlib.sha256(value.encode()).hexdigest(),'utf8_bytes':len(value.encode()),
        'trust':'Original named grounding and target disposition are unchanged. No new authority.'}


def grounding_view(context, current, source):
    if not isinstance(context,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in context.items()):
        raise ValueError('CAMPAIGN_GROUNDING_ORIGINAL_STRINGS_REQUIRED')
    view=dict(context)
    for name in GROUNDING_TARGETS:
        if name not in context or context[name]!=_literal(current,name):
            raise ValueError('CAMPAIGN_GROUNDING_ORIGINAL_LITERAL_CHANGED')
        view[name]=_reference(current,name,source)
    return view


def _restore_grounding(view, current, source):
    if not isinstance(view,dict): raise ValueError('CAMPAIGN_GROUNDING_VIEW_REQUIRED')
    result=dict(view)
    for name in GROUNDING_TARGETS:
        reference=view.get(name)
        if (not isinstance(reference,dict) or type(reference.get('utf8_bytes')) is not int
                or reference!=_reference(current,name,source)):
            raise ValueError('CAMPAIGN_GROUNDING_REFERENCE_CHANGED')
        result[name]=_literal(current,name)
    if any(not isinstance(k,str) or not isinstance(v,str) for k,v in result.items()):
        raise ValueError('CAMPAIGN_GROUNDING_UNDECLARED_REFERENCE')
    return result


def _stage_body(prepared, task, stage, proposal, *, context=None, evidence_enabled=False):
    from orchestrator.campaign_pipeline import author_body,reviewer_body
    if stage not in ('continuation','review') or not isinstance(proposal,str):
        raise ValueError('CAMPAIGN_GROUNDING_STAGE_REQUIRED')
    if stage=='continuation' and proposal:
        raise ValueError('CAMPAIGN_AUTHOR_REFUSES_PRIOR_PROPOSAL')
    body=author_body('investigate',task['request'],prepared['context'] if context is None else context,task)
    if stage=='review': body=reviewer_body(body,proposal,('APPROVE','REVISE','REQUEST_CHANGES'))
    return artifact_prompt(body,MODES['investigate'] if stage=='continuation' else ['review.json'],
                           evidence_enabled=evidence_enabled)


def _typed_prompt(root, source, packet, prepared, stage, proposal):
    from orchestrator.hosted_context import build,TASK_KEYS
    task=_campaign_task(packet,source)
    current=build(root,{key:packet[key] for key in TASK_KEYS if key in packet})
    view=grounding_view(prepared['context'],current,source)
    from orchestrator.scientific_evidence_runtime import enabled
    tool_profile = 'scientific_change_history' in packet and enabled(root, source)
    original=_stage_body(prepared,task,stage,proposal,evidence_enabled=tool_profile)
    value={'schema':GROUNDING_SCHEMA,'source':source,'stage':stage,'task':task,
        'packet_sha256':hashlib.sha256(encoded(packet)).hexdigest(),
        'context':view,'input_sha256':prepared['input_sha256'],'proposal':proposal,
        'original_context_sha256':hashlib.sha256(encoded(prepared['context'])).hexdigest(),
        'original_prompt_sha256':hashlib.sha256(original.encode()).hexdigest()}
    return GROUNDING_PREFIX+json.dumps(value,sort_keys=True)


def grounding_presentation(root, packet, current, prompt, source, *, family):
    """Strict whole-envelope grammar; return a checked text view, not changed receipts."""
    if not prompt.startswith(GROUNDING_PREFIX): return prompt
    if grounding_version(root,source)!=1:
        raise ValueError('CAMPAIGN_GROUNDING_SOURCE_PROFILE_REQUIRED')
    raw=prompt[len(GROUNDING_PREFIX):]
    try: value=json.loads(raw)
    except ValueError as error: raise ValueError('CAMPAIGN_GROUNDING_ENVELOPE_INVALID') from error
    keys={'schema','source','stage','task','packet_sha256','context','input_sha256','proposal',
          'original_context_sha256','original_prompt_sha256'}
    task=_campaign_task(packet,source)
    if (not isinstance(value,dict) or set(value)!=keys or json.dumps(value,sort_keys=True)!=raw
            or value['schema']!=GROUNDING_SCHEMA or value['source']!=source or value['task']!=task
            or value['packet_sha256']!=hashlib.sha256(encoded(packet)).hexdigest()
            or value['stage']!=('continuation' if family=='codex' else 'review' if family=='claude' else None)):
        raise ValueError('CAMPAIGN_GROUNDING_ENVELOPE_CHANGED')
    restored=_restore_grounding(value['context'],current,source)
    from orchestrator.campaign_pipeline import prepare_input
    supplement={'continuing-research-inputs.json':restored.get('continuing-research-inputs.json')}
    prepared=prepare_input(root,'investigate',task['experiment'],task['request'],
        formal_task=task,supplemental_context=supplement)
    if (restored!=prepared['context'] or value['input_sha256']!=prepared['input_sha256']
            or value['original_context_sha256']!=hashlib.sha256(encoded(prepared['context'])).hexdigest()
            or value['context']!=grounding_view(prepared['context'],current,source)):
        raise ValueError('CAMPAIGN_GROUNDING_COMPLETE_CONTEXT_CHANGED')
    from orchestrator.scientific_evidence_runtime import enabled
    tool_profile = 'scientific_change_history' in packet and enabled(root, source)
    original=_stage_body(prepared,task,value['stage'],value['proposal'],evidence_enabled=tool_profile)
    if value['original_prompt_sha256']!=hashlib.sha256(original.encode()).hexdigest():
        raise ValueError('CAMPAIGN_GROUNDING_ORIGINAL_BODY_CHANGED')
    # Original insertion order is reconstructed by the native preparation helper.
    view=grounding_view(prepared['context'],current,source)
    from orchestrator import scientific_context_references as context_refs
    catalog_view = False
    if tool_profile and context_refs.enabled(root, source, protocol=True):
        view, catalog_view = context_refs.protocol_presentation(view, packet)
    shown=_stage_body(prepared,task,value['stage'],value['proposal'],context=view,evidence_enabled=tool_profile)
    if catalog_view:
        return ('SOURCE-BOUND CAMPAIGN PRESENTATION: policy references resolve to the same prompt. '
            'The eligible-protocol list uses the authenticated completed catalog; original operation '
            'bodies and descriptors are retrievable through the task-bound scientific reader. '
            'All protocol_blocks remain literal. The full original prepared context is validated '
            'before this display, and native selection still checks the chosen original and authority. '
            'Original context SHA256 '+value['original_context_sha256']+'; original body SHA256 '
            +value['original_prompt_sha256']+'.\n'+shown)
    return ('SOURCE-BOUND CAMPAIGN PRESENTATION: each fixed reference resolves directly to a full literal '
        'in this same operating context. Restore those named strings to reconstruct the complete original '
        'grounding and body; no policy, criticism or authority is omitted. Original context SHA256 '
        +value['original_context_sha256']+'; original body SHA256 '+value['original_prompt_sha256']+'.\n'+shown)


def campaign_preflight(root, source, packet, *, supplement, evidence_config=None):
    """Both real constructor paths, before coordinator admission; no client/model call."""
    task=packet.get('campaign_task',{})
    if task.get('schema')!='investigator-task/v1' or grounding_version(root,source)!=1:
        return {'status':'UNCHANGED_CAMPAIGN_INPUT_PROFILE','models':0,'admissions':0}
    task=_campaign_task(packet,source)
    from orchestrator.campaign_pipeline import prepare_input
    from orchestrator.hosted_context import compose_input,measure_input,context_bytes
    from orchestrator.scientific_output import contract as output_contract
    prepared=prepare_input(root,'investigate',task['experiment'],task['request'],
        formal_task=task,supplemental_context=supplement)
    # artifact_files enforces 30000 UTF8 bytes per file. After envelope restoration,
    # proposal bodies are concatenated as literal text, not JSON-escaped again.
    proposal='\n'.join(name+'\n'+'x'*30000 for name in MODES['investigate'])
    rows=[]
    for stage,family,body in [('continuation','codex',''),('review','claude',proposal)]:
        prompt=_typed_prompt(root,source,packet,prepared,stage,body)
        from orchestrator.scientific_evidence_runtime import controller_options
        options = controller_options(evidence_config, root, source, packet, stage)
        final,current=compose_input(root,encoded(packet),prompt,verified_source=source,family=family,output_format='json', **options)
        rows.append({**measure_input(final,family,stage,task_state=packet,output_contract=output_contract(packet,stage)),
            'operating_context_sha256':hashlib.sha256(context_bytes(root,current,source)).hexdigest()})
    return {'schema':'hosted-investigator-input-preflight/v1','source':source,
        'packet_sha256':hashlib.sha256(encoded(packet)).hexdigest(),'input_sha256':prepared['input_sha256'],
        'stages':rows,'prior_file_utf8_bytes_each':30000,
        'projection':'PERMITTED_ARTIFACT_UTF8_BOUND_WITH_LITERAL_PROPOSAL_RESTORATION',
        'models':0,'admissions':0}


class BrokerStages:
    def __init__(self, socket, event, packet, *, client=request_broker, recovery=False,
                 source_root=None, source=None, supplement=None, evidence_config=None):
        self.socket=socket;self.event=event;self.packet=packet;self.client=client
        if type(recovery) is not bool:raise ValueError('HOSTED_CAMPAIGN_RECOVERY_MODE')
        self.recovery=recovery
        self.completed=[];self.receipts={};self.mode=None
        self.source_root=source_root;self.source=source;self.supplement=supplement
        self.evidence_config=evidence_config
        self._evidence_profiles={}
        self.prepared=None;self.answers={}
        if source_root is not None and packet.get('campaign_task',{}).get('schema')=='investigator-task/v1':
            if event.get('source')!=source:raise ValueError('CAMPAIGN_NATIVE_SOURCE_BINDING_CHANGED')
            if grounding_version(source_root,source)==1:
                task=_campaign_task(packet,source)
                from orchestrator.campaign_pipeline import prepare_input
                self.prepared=prepare_input(source_root,'investigate',task['experiment'],task['request'],
                    formal_task=task,supplemental_context=supplement)

    def evidence_options(self, stage, *, root=None, source=None):
        from orchestrator.scientific_evidence_runtime import controller_options, packet_kind
        if packet_kind(self.packet) is None:
            return {}
        if stage not in self._evidence_profiles:
            self._evidence_profiles[stage] = controller_options(self.evidence_config, self.source_root or root,
                source or self.source or self.event['source'], self.packet, stage)
        return self._evidence_profiles[stage]

    def stage_prompt(self, stage):
        proposal=''
        if stage=='review':
            if 'continuation' not in self.answers:raise ValueError('CAMPAIGN_ORIGINAL_AUTHOR_REQUIRED')
            files=artifact_files(self.answers['continuation'],MODES['investigate'])
            proposal='\n'.join(name+'\n'+files[name] for name in MODES['investigate'])
        return _typed_prompt(self.source_root,self.source,self.packet,self.prepared,stage,proposal)


    def call(self, stage, prompt):
        expected=('continuation','review','disposition')
        if len(self.completed)>=3 or stage!=expected[len(self.completed)]:
            raise ValueError('HOSTED_CAMPAIGN_STAGE_ORDER_OR_BOUND')
        expected=None
        if self.prepared is not None and stage in ('continuation','review'):
            expected=self.stage_prompt(stage)
            if not self.recovery and prompt!=expected:
                raise ValueError('CAMPAIGN_ACTUAL_TYPED_INPUT_CHANGED')
        if self.recovery:
            response=self.client(self.socket,'stage_status',{'event':self.event,'stage':stage})
        else:
            response=self.client(self.socket,'model_stage',{'event':self.event,'stage':stage,
                                                          'packet':self.packet,'prompt':prompt})
        # Leave room for the coordinator's receipt envelope; validate escaped
        # JSON size, not only the unescaped answer bytes. Originals stay private.
        answer,receipt=checked_reply(response,stage,hashlib.sha256(encoded(self.packet)).hexdigest())
        if expected is not None:
            from orchestrator.hosted_context import compose_input,context_bytes
            final,current=compose_input(self.source_root,encoded(self.packet),expected,
                verified_source=self.source,family='codex' if stage=='continuation' else 'claude',output_format='json',
                **self.evidence_options(stage))
            if (receipt.get('input_sha256')!=hashlib.sha256(final.encode()).hexdigest()
                    or receipt.get('operating_context_sha256')!=hashlib.sha256(context_bytes(self.source_root,current,self.source)).hexdigest()):
                raise ValueError('CAMPAIGN_ORIGINAL_INPUT_OR_CONTEXT_CHANGED')
        self.answers[stage]=answer
        self.receipts[stage]={'receipt':receipt,'duplicate':response.get('duplicate')}
        self.completed.append(stage)
        return answer,receipt

    def __call__(self, sc, directory, family, stage, body, names):
        index=len(self.completed)
        if index>=2 or family!=('codex','claude')[index]:
            raise ValueError('HOSTED_CAMPAIGN_AUTHOR_REVIEW_BOUND')
        allowed=('readiness','discuss')
        contract=self.packet.get('campaign_artifacts',{})
        if contract.get('version')==2:
            from orchestrator.continuing_research import artifact_contract
            allowed=(artifact_contract(contract)['mode'],)
        if (index==0 and (stage not in tuple('campaign_'+mode for mode in allowed)
                or names!=MODES[stage.removeprefix('campaign_')])) or (index==1 and (names!=['review.json'] or stage!='campaign_'+str(self.mode)+'_review')):
            raise ValueError('HOSTED_CAMPAIGN_ARTIFACT_SCOPE')
        if index==0:self.mode=stage.removeprefix('campaign_')
        evidence_enabled = bool(self.evidence_options(('continuation','review')[index]))
        prompt=artifact_prompt(body,names,evidence_enabled=evidence_enabled)
        if self.prepared is not None:
            proposal=''
            if index:
                files=artifact_files(self.answers['continuation'],MODES['investigate'])
                proposal='\n'.join(name+'\n'+files[name] for name in MODES['investigate'])
            expected=_stage_body(self.prepared,self.packet['campaign_task'],('continuation','review')[index],proposal,
                                 evidence_enabled=evidence_enabled)
            if prompt!=expected:raise ValueError('CAMPAIGN_PIPELINE_ORIGINAL_BODY_CHANGED')
            prompt=self.stage_prompt(('continuation','review')[index])
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


def pipeline_contract(stages,mode,request):
    contract=stages.packet.get('campaign_artifacts',{})
    if contract.get('version')==2:
        from orchestrator.continuing_research import task_contract
        task=stages.packet.get('campaign_task')
        if task_contract(task)!=contract or task['mode']!=mode or task['request']!=request:
            raise ValueError('HOSTED_CONTINUING_TASK_BINDING')
        return contract['experiment'],task
    if mode not in ('readiness','discuss'):raise ValueError('HOSTED_CAMPAIGN_PREPARATION_ONLY')
    if contract!={'version':1,'experiment':'P001','mode':mode} or type(contract['version']) is not int:
        raise ValueError('HOSTED_CAMPAIGN_PACKET_CONTRACT')
    return 'P001',None


def run_pipeline(sc, mode, request, output, stages, *, supplement=None):
    experiment,task=pipeline_contract(stages,mode,request)
    options={} if task is None else {'formal_task':task,'supplemental_context':supplement}
    return execute(sc,mode,experiment,request,output,max_rounds=1,stage_runner=stages,
        complete_negative_review=True,initiator={'kind':'agent','family':'codex','model':'gpt-6-astra',
            'route':'protected-hosted-campaign-v1','event':stages.event,
            'packet_sha256':hashlib.sha256(encoded(stages.packet)).hexdigest()},**options)


def recover_projection(sc,mode,request,original,output,stages,*,supplement=None):
    """Restore derived artifacts from verified original broker replies only.

    Existing files and contradictory human edits are never overwritten. A missing
    or unsuccessful original stage is a block, not permission for a model retry.
    The output is explicitly a recovery projection, not a fresh reviewer session.
    """
    from orchestrator.campaign_pipeline import grounding
    from orchestrator.research_context import evidence_context
    if not stages.recovery:raise ValueError('READ_ONLY_RECOVERY_CLIENT_REQUIRED')
    if stages.packet.get('campaign_artifacts',{}).get('version')==2:
        experiment,task=pipeline_contract(stages,mode,request)
    else:
        if mode not in ('readiness','discuss'):raise ValueError('HOSTED_CAMPAIGN_PREPARATION_ONLY')
        experiment,task='P001',None
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
    options={'prospective_task':task} if task is not None and task.get('schema')=='prospective-research-task/v1' else {}
    if task is not None and task.get('schema')=='protocol-proposal-task/v1':options={'protocol_task':task}
    if task is not None and task.get('schema')=='investigator-task/v1':options={'investigator_task':task}
    context=grounding(sc.ROOT,experiment,**options)
    context['related-evidence.json']=json.dumps(evidence_context(sc.ROOT,'isles24-prediction'))
    if task is not None:
        from orchestrator.continuing_research import checked_supplement
        context.update(checked_supplement(task,supplement))
    hashes={k:hashlib.sha256(v.encode()).hexdigest() for k,v in context.items()}
    if any(prior.get(k)!=v for k,v in {'mode':mode,'experiment':experiment,'request':request,'max_rounds':1,'input_sha256':hashes}.items()):
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
    restored=BrokerStages(stages.socket,stages.event,stages.packet,client=replay,recovery=True,
        source_root=stages.source_root,source=stages.source,supplement=supplement,
        evidence_config=stages.evidence_config)
    receipt=run_pipeline(sc,mode,request,output,restored,supplement=supplement)
    immutable(output/'recovery.json',encoded({'status':'RECOVERED_ORIGINAL_MODEL_ARTIFACTS',
        'original_request_sha256':hashlib.sha256(prior_raw).hexdigest(),
        'event':stages.event,'packet_sha256':hashlib.sha256(encoded(stages.packet)).hexdigest(),
        'new_model_calls':0,'new_review':False,'original_preserved':True}))
    return receipt
