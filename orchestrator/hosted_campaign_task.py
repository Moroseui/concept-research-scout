"""Preparation-only controller integration; deployment remains separately tested."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from types import SimpleNamespace
from orchestrator.hosted_cycle import encoded, immutable
from orchestrator.public_export import text


def task_contract(value):
    """Installed preparation request, not an arbitrary experiment/backend handler."""
    if isinstance(value,dict) and value.get('schema') in ('continuing-research-task/v1','prospective-research-task/v1','protocol-proposal-task/v1','investigator-task/v1'):
        from orchestrator.continuing_research import task_contract as continuing_contract
        return continuing_contract(value)
    if (not isinstance(value,dict) or set(value) not in
            ({'mode','request','trigger_job'}, {'mode','request','task_id'})
            or value['mode'] not in ('readiness','discuss')
            or not isinstance(value['request'],str) or not value['request'].strip()
            or not isinstance(value.get('trigger_job',value.get('task_id')),str)
            or not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}',value.get('trigger_job',value.get('task_id')))):
        raise ValueError('HOSTED_CAMPAIGN_TASK_CONTRACT')
    text(value['request'],limit=8000)
    return {'version':1,'experiment':'P001','mode':value['mode']}


def installed_research_request(config,task_id=None):
    """Read one installed task, retaining the legacy source/request identity."""
    from datetime import date
    from orchestrator.change_requests import actor
    from orchestrator.handover_coordinator import digest
    from orchestrator.handover_runtime import configuration
    from orchestrator.research_catalog import selection
    config,entry=selection(config,task_id)
    request = config.get('research_request')
    if (not isinstance(request,dict) or set(request) !=
            {'task','evidence_file','evidence_sha256','day','initiator'}):
        raise ValueError('INSTALLED_RESEARCH_REQUEST_REQUIRED')
    task_contract(request['task'])
    if 'task_id' not in request['task']:
        raise ValueError('INSTALLED_RESEARCH_TASK_ID_REQUIRED')
    try:
        day=date.fromisoformat(request['day'])
    except (ValueError,TypeError):
        raise ValueError('INSTALLED_RESEARCH_INPUT_BINDING_REQUIRED') from None
    if (not isinstance(request['evidence_file'],str)
            or not Path(request['evidence_file']).is_absolute()
            or not isinstance(request['evidence_sha256'],str)
            or not re.fullmatch('[0-9a-f]{64}',request['evidence_sha256'])
            or day.isoformat() != request['day']):
        raise ValueError('INSTALLED_RESEARCH_INPUT_BINDING_REQUIRED')
    if request['task'].get('schema') == 'investigator-task/v1':
        from orchestrator.investigator_wakes import service
        if request['initiator'] != service(config):
            raise ValueError('INVESTIGATOR_TEMPLATE_SERVICE_ORIGIN_REQUIRED')
    else:
        actor(request['initiator'])  # Prepared request proposer; not a human signature.
    if task_contract(request['task'])['version']==2:
        from orchestrator.continuing_research import read_evidence
        evidence=read_evidence(config,request)
    else:
        evidence = configuration(request['evidence_file'], maximum=1500000,
            expected_sha256=request['evidence_sha256'], private_gid=config['controller_gid'])
    if not isinstance(evidence,dict):raise ValueError('RESEARCH_PRIMARY_EVIDENCE_OBJECT_REQUIRED')
    from orchestrator.git_publication import scan
    raw=encoded(evidence);scan('research-evidence.json',raw);text(raw.decode(),limit=1500000)
    identity={'source':config['source'],'installed_request':request}
    if entry is not None:identity['catalog_entry_sha256']=digest(entry)
    binding={'identity':digest(identity),
        'source':config['source'],'task_id':request['task']['task_id'],
        'evidence_sha256':request['evidence_sha256'],'day':request['day'],
        'initiator':request['initiator']}
    if entry is not None:binding['catalog_entry_sha256']=digest(entry)
    return request['task'], evidence, binding


def installed_packet_task(config, packet):
    """Recheck the packet's retained installed version, never the latest request."""
    if 'research_request_binding' in packet:
        task,evidence,binding=installed_research_request(config,packet['research_request_binding'].get('task_id'))
        if (packet.get('trigger')!='installed-research-request'
                or packet['research_request_binding']!=binding
                or packet.get('reviewer_evidence')!=evidence):
            raise ValueError('INSTALLED_RESEARCH_PACKET_CHANGED')
        return task
    return config.get('campaign_preparation')


def preparation_workspace(source, destination):
    """Copy the already checked sparse source, without Git fetching or credentials.

    The controller owns this private working copy. The immutable installed source
    remains separate; original copied inputs are verified on every reuse. Pipeline
    outputs may be added, but changing a copied input causes a named refusal.
    """
    source=Path(source);destination=Path(destination)
    from orchestrator.operations_report import private_root
    private_root(destination.parent)
    marker=destination.parent/(destination.name+'-inputs.json')
    if destination.is_symlink() or marker.is_symlink():raise ValueError('CAMPAIGN_WORKSPACE_SYMLINK')
    entries={};total=0
    from orchestrator.git_diagnostics import output as git_output
    try:
        tracked=git_output(['git','-c','safe.directory='+str(source),'ls-files','-z'],cwd=source,timeout=30).decode().split('\0')
    except (subprocess.SubprocessError,RuntimeError) as error:
        raise ValueError('CAMPAIGN_SOURCE_INVENTORY_UNAVAILABLE') from error
    for name in sorted(set(tracked)-{''}):
        relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts or '.git' in relative.parts:raise ValueError('CAMPAIGN_SOURCE_PATH')
        path=source/relative
        if path.is_symlink():raise ValueError('CAMPAIGN_SOURCE_SYMLINK')
        if not path.is_file():continue
        size=path.stat().st_size;total+=size
        if size>2000000 or total>50000000 or len(entries)>=2000:
            raise ValueError('CAMPAIGN_SOURCE_COPY_BOUND')
        entries[relative.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    if destination.exists():
        if not marker.is_file() or json.loads(marker.read_text())!=entries:
            raise ValueError('CAMPAIGN_WORKSPACE_RECONCILE_NO_RETRY')
        for name,expected in entries.items():
            path=destination/name
            if (any(p.is_symlink() for p in [path,*path.parents]) or not path.is_file()
                    or hashlib.sha256(path.read_bytes()).hexdigest()!=expected):
                raise ValueError('CAMPAIGN_WORKSPACE_INPUT_CHANGED')
        return destination
    if marker.exists():raise ValueError('CAMPAIGN_WORKSPACE_RECONCILE_NO_RETRY')
    destination.mkdir(mode=0o700)
    for name,expected in entries.items():
        raw=(source/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('CAMPAIGN_SOURCE_CHANGED')
        path=destination/name;path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        # This is an exact private copy of checked source, including Git
        # metadata such as .gitignore; it is not model output or publication.
        # Exclusive creation and the source digest preserve the copy boundary.
        with path.open('xb') as stream:stream.write(raw)
        path.chmod(0o600)
    immutable(marker,encoded(entries))
    return destination


def completed_pipeline(root,output,packet,event,*,supplement=None):
    """Validate the shared pipeline's saved result before coordinator advancement."""
    from orchestrator.campaign_pipeline import grounding,MODES
    from orchestrator.research_context import evidence_context
    if output.is_symlink() or (output/'receipt.json').is_symlink():raise ValueError('CAMPAIGN_RESULT_SYMLINK')
    receipt=json.loads((output/'receipt.json').read_text())
    request=json.loads((output/'request.json').read_text())
    contract=packet['campaign_task'];mode=contract['mode']
    artifact_contract=task_contract(contract);experiment=artifact_contract['experiment']
    options={'prospective_task':contract} if contract.get('schema')=='prospective-research-task/v1' else {}
    if contract.get('schema')=='protocol-proposal-task/v1':options={'protocol_task':contract}
    if contract.get('schema')=='investigator-task/v1':options={'investigator_task':contract}
    context=grounding(root,experiment,**options);context['related-evidence.json']=json.dumps(evidence_context(root,'isles24-prediction'))
    if artifact_contract['version']==2:
        from orchestrator.continuing_research import checked_supplement
        context.update(checked_supplement(contract,supplement))
    hashes={k:hashlib.sha256(v.encode()).hexdigest() for k,v in context.items()}
    expected={'mode':mode,'experiment':experiment,'request':contract['request'],'input_sha256':hashes,'max_rounds':1,
        'status':'PROPOSAL_ONLY','actor_type':'agent','family':'codex','authority':'campaign_delegated_investigator'}
    if any(request.get(k)!=v for k,v in expected.items()) or type(request.get('max_rounds')) is not int:
        raise ValueError('CAMPAIGN_RESULT_CONTEXT_CHANGED')
    actor=request.get('initiator',{})
    if actor.get('event')!=event or actor.get('packet_sha256')!=hashlib.sha256(encoded(packet)).hexdigest():raise ValueError('CAMPAIGN_RESULT_TURN_CHANGED')
    if (receipt.get('status') not in ('REVIEWED_PROPOSAL_NOT_ADOPTED','REVISION_REQUIRED')
            or type(receipt.get('round')) is not int or receipt.get('round')!=1
            or receipt.get('input_sha256')!=hashes or receipt.get('mode')!=mode or receipt.get('experiment')!=experiment
            or receipt.get('author_family')!='codex' or receipt.get('reviewer_family')!='claude'
            or receipt.get('ci') is not False or receipt.get('initiator')!=actor):
        raise ValueError('CAMPAIGN_REVIEWED_RESULT_REQUIRED')
    names=set(MODES[mode]+['review.json','campaign_'+mode+'.hosted-provenance.json','campaign_'+mode+'_review.hosted-provenance.json'])
    expected_paths={'round-1/'+name for name in names}
    artifacts=receipt.get('artifact_sha256',{})
    if set(artifacts)!=expected_paths:raise ValueError('CAMPAIGN_RESULT_ARTIFACT_SET')
    for name,expected in artifacts.items():
        path=output/name
        if path.is_symlink() or path.parent.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError('CAMPAIGN_RESULT_ARTIFACT_CHANGED')
    review=json.loads((output/'round-1/review.json').read_text())
    if (set(review)!={'verdict','rationale'} or review['verdict'] not in ('APPROVE','REVISE','REQUEST_CHANGES')
            or not isinstance(review['rationale'],str) or not review['rationale'].strip()):
        raise ValueError('CAMPAIGN_REVIEW_VERDICT_REQUIRED')
    approved=review['verdict']=='APPROVE'
    if receipt['status']!=('REVIEWED_PROPOSAL_NOT_ADOPTED' if approved else 'REVISION_REQUIRED'):
        raise ValueError('CAMPAIGN_REVIEW_STATUS_MISMATCH')
    # Historical approved receipts remain readable. A negative outcome, or any
    # new policy fields, must carry the complete exact policy/verdict binding.
    fields={'review_completion_policy','review_verdict','acceptance_status'}
    if not approved or fields.intersection(receipt):
        if (receipt.get('review_completion_policy')!='HOSTED_BOUNDED_REVIEW_WITH_DISPOSITION'
                or receipt.get('review_verdict')!=review['verdict']
                or receipt.get('acceptance_status')!=('APPROVED_PROPOSAL_ONLY' if approved else 'NOT_ACCEPTED')):
            raise ValueError('CAMPAIGN_REVIEW_POLICY_BINDING')
    if 'import_result' in contract:
        imported=json.loads(supplement['continuing-research-inputs.json'])['import_result']['receipt']
        expected={'reference':contract['import_result'],'completion':imported['completion'],
            'original_response_sha256':imported['original_response_sha256'],
            'validation_status':'PENDING_FORMAL_SCIENTIFIC_VALIDATION','scientific_acceptance':False}
        if receipt.get('result_import_binding')!=expected:
            raise ValueError('CAMPAIGN_ORIGINAL_RESULT_IMPORT_BINDING_CHANGED')
    if contract.get('schema')=='protocol-proposal-task/v1':
        from orchestrator.protocol_proposals import validate_bundle
        validation=validate_bundle(contract,{name:(output/'round-1'/name).read_text() for name in MODES[mode]},context)
        if receipt.get('protocol_proposal_validation')!=validation:
            raise ValueError('CAMPAIGN_PROTOCOL_PROPOSAL_VALIDATION_CHANGED')
    return receipt


def stage_result(runtime,binding,position,packet,*,read_only=False):
    """One existing campaign pipeline, original review retrieval, no patient route."""
    from orchestrator.hosted_campaign import BrokerStages,run_pipeline,recover_projection,artifact_files
    from orchestrator.campaign_pipeline import MODES
    from orchestrator.handover_runtime import request_broker
    from orchestrator.handover_coordinator import digest
    report=json.loads((runtime.state/'tasks'/binding['id']/'report.json').read_text())
    if digest({'source':binding['source'],'packet':packet,'report':report})!=binding['id']:
        raise ValueError('TASK_PACKET_CHANGED')
    configured=installed_packet_task(runtime.config,packet)
    if packet.get('campaign_task')!=configured or task_contract(configured)!=packet.get('campaign_artifacts'):
        raise ValueError('INSTALLED_CAMPAIGN_TASK_REQUIRED')
    if packet.get('execution_proposal') is not None:raise ValueError('CAMPAIGN_TASK_REFUSES_SYNTHETIC_SUCCESSOR')
    if position not in (0,1,2):raise ValueError('CAMPAIGN_TASK_STAGE')
    task=runtime.state/'tasks'/binding['id']
    source=runtime.root
    if 'research_request_binding' in packet:
        from orchestrator.research_catalog import selection
        from orchestrator.remote_supervisor import checked_source
        configured_source,_=selection(runtime.config,configured['task_id'])
        if not read_only and binding['source']!=runtime.config['source']:
            raise ValueError('HISTORICAL_RESEARCH_SOURCE_READ_ONLY')
        if binding['source']==runtime.config['source']:
            if Path(configured_source['source_root']).resolve()!=runtime.root.resolve():
                raise ValueError('CATALOG_CURRENT_SOURCE_ROOT_CHANGED')
        else:source=checked_source(configured_source['source_root'],binding['source'])
    supplement=None
    if task_contract(configured)['version']==2:
        from orchestrator.continuing_research import supplemental_context
        supplement=supplemental_context({**runtime.config,'source_root':str(source),'source':binding['source']},configured,
            read_only=read_only,**({'packet':packet} if configured.get('schema')=='investigator-task/v1' else {}))
    workspace=preparation_workspace(source,task/'campaign-workspace')
    original=workspace/'campaigns/isles24-pilot/pipeline/hosted-original'
    projection=original.parent/'hosted-recovery'
    event=runtime.event(binding);mode=configured['mode'];request=configured['request']
    def stages(recovery):return BrokerStages(runtime.config['broker_socket'],event,packet,
        client=request_broker,recovery=recovery,source_root=source,source=binding['source'],supplement=supplement,
        evidence_config=runtime.config)
    output=projection if projection.exists() else original
    if not (output/'receipt.json').exists():
        if projection.exists():raise ValueError('CAMPAIGN_RECOVERY_INCOMPLETE_NO_RETRY')
        if original.exists():
            recover_projection(SimpleNamespace(ROOT=workspace),mode,request,original,projection,stages(True),supplement=supplement);output=projection
        elif read_only or position!=0:raise ValueError('CAMPAIGN_OUTCOME_UNCERTAIN_NO_RETRY')
        else:run_pipeline(SimpleNamespace(ROOT=workspace),mode,request,original,stages(False),supplement=supplement)
    receipt=completed_pipeline(workspace,output,packet,event,supplement=supplement)
    # A mutable local manifest is not independent proof of scientific bytes.
    # Compare both artifacts to the protected broker's original model replies.
    original_replies={};reader=stages(True)
    for stage,names in [('continuation',MODES[mode]),('review',['review.json'])]:
        answer,model_receipt=reader.call(stage,'')
        for name,content in artifact_files(answer,names).items():
            if (output/'round-1'/name).read_bytes()!=content.encode():
                raise ValueError('CAMPAIGN_ARTIFACT_ORIGINAL_REPLY_MISMATCH')
        label='campaign_'+mode+('_review' if stage=='review' else '')
        provenance=json.loads((output/'round-1'/(label+'.hosted-provenance.json')).read_text())
        if provenance.get('model_receipt_sha256')!=hashlib.sha256(encoded(model_receipt)).hexdigest():
            raise ValueError('CAMPAIGN_ORIGINAL_MODEL_RECEIPT_CHANGED')
        original_replies[stage]=(answer,model_receipt)
    if output==projection:
        # Finish a lost recovery marker only from the hash-validated projection.
        for name in ['campaign_'+mode,'campaign_'+mode+'_review']:
            provenance=json.loads((output/'round-1'/(name+'.hosted-provenance.json')).read_text())
            if provenance.get('recovered_original') is not True:raise ValueError('CAMPAIGN_RECOVERY_PROVENANCE_REQUIRED')
        if ((original/'request.json').is_symlink() or json.loads((original/'request.json').read_text())!=json.loads((output/'request.json').read_text())):
            raise ValueError('CAMPAIGN_RECOVERY_ORIGINAL_REQUEST_CHANGED')
        immutable(output/'recovery.json',encoded({'status':'RECOVERED_ORIGINAL_MODEL_ARTIFACTS',
            'original_request_sha256':hashlib.sha256((original/'request.json').read_bytes()).hexdigest(),
            'event':event,'packet_sha256':hashlib.sha256(encoded(packet)).hexdigest(),
            'new_model_calls':0,'new_review':False,'original_preserved':True}))
    result_binding={'campaign_status':receipt['status'],
        'campaign_receipt_sha256':hashlib.sha256((output/'receipt.json').read_bytes()).hexdigest(),
        'campaign_output':output.relative_to(runtime.state).as_posix()}
    if position==2:
        return {**receipt,**result_binding,'original_stage_outputs':{
            stage:{'answer':answer,'receipt':model_receipt}
            for stage,(answer,model_receipt) in original_replies.items()}}
    answer,model_receipt=original_replies[('continuation','review')[position]]
    return {'status':'COMPLETE','duplicate':True,'answer':answer,'receipt':model_receipt,
            **result_binding}
