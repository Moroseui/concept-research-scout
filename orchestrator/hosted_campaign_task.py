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
    if (not isinstance(value,dict) or set(value)!={'mode','request','trigger_job'}
            or value['mode'] not in ('readiness','discuss')
            or not isinstance(value['request'],str) or not value['request'].strip()
            or not isinstance(value['trigger_job'],str)
            or not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}',value['trigger_job'])):
        raise ValueError('HOSTED_CAMPAIGN_TASK_CONTRACT')
    text(value['request'],limit=8000)
    return {'version':1,'experiment':'P001','mode':value['mode']}


def preparation_workspace(source, destination):
    """Copy the already checked sparse source, without Git fetching or credentials.

    The controller owns this private working copy. The immutable installed source
    remains separate; original copied inputs are verified on every reuse. Pipeline
    outputs may be added, but changing a copied input causes a named refusal.
    """
    source=Path(source);destination=Path(destination)
    marker=destination.parent/(destination.name+'-inputs.json')
    if destination.is_symlink() or marker.is_symlink():raise ValueError('CAMPAIGN_WORKSPACE_SYMLINK')
    entries={};total=0
    tracked=subprocess.check_output(['git','-c','safe.directory='+str(source),'ls-files','-z'],cwd=source).decode().split('\0')
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
        immutable(path,raw)
    immutable(marker,encoded(entries))
    return destination


def completed_pipeline(root,output,packet,event):
    """Validate the shared pipeline's saved result before coordinator advancement."""
    from orchestrator.campaign_pipeline import grounding,MODES
    from orchestrator.research_context import evidence_context
    if output.is_symlink() or (output/'receipt.json').is_symlink():raise ValueError('CAMPAIGN_RESULT_SYMLINK')
    receipt=json.loads((output/'receipt.json').read_text())
    request=json.loads((output/'request.json').read_text())
    contract=packet['campaign_task'];mode=contract['mode']
    context=grounding(root,'P001');context['related-evidence.json']=json.dumps(evidence_context(root,'isles24-prediction'))
    hashes={k:hashlib.sha256(v.encode()).hexdigest() for k,v in context.items()}
    expected={'mode':mode,'experiment':'P001','request':contract['request'],'input_sha256':hashes,'max_rounds':1}
    if any(request.get(k)!=v for k,v in expected.items()):raise ValueError('CAMPAIGN_RESULT_CONTEXT_CHANGED')
    actor=request.get('initiator',{})
    if actor.get('event')!=event or actor.get('packet_sha256')!=hashlib.sha256(encoded(packet)).hexdigest():raise ValueError('CAMPAIGN_RESULT_TURN_CHANGED')
    if (receipt.get('status')!='REVIEWED_PROPOSAL_NOT_ADOPTED' or receipt.get('round')!=1
            or receipt.get('input_sha256')!=hashes or receipt.get('mode')!=mode or receipt.get('experiment')!='P001'):
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
    if review.get('verdict')!='APPROVE':raise ValueError('CAMPAIGN_REVIEW_NOT_APPROVED')
    return receipt


def stage_result(runtime,binding,position,packet,*,read_only=False):
    """One existing campaign pipeline, original review retrieval, no patient route."""
    from orchestrator.hosted_campaign import BrokerStages,run_pipeline,recover_projection
    from orchestrator.handover_runtime import request_broker
    from orchestrator.handover_coordinator import digest
    report=json.loads((runtime.state/'tasks'/binding['id']/'report.json').read_text())
    if digest({'source':binding['source'],'packet':packet,'report':report})!=binding['id']:
        raise ValueError('TASK_PACKET_CHANGED')
    configured=runtime.config.get('campaign_preparation')
    if packet.get('campaign_task')!=configured or task_contract(configured)!=packet.get('campaign_artifacts'):
        raise ValueError('INSTALLED_CAMPAIGN_TASK_REQUIRED')
    if packet.get('execution_proposal') is not None:raise ValueError('CAMPAIGN_TASK_REFUSES_SYNTHETIC_SUCCESSOR')
    if position not in (0,1,2):raise ValueError('CAMPAIGN_TASK_STAGE')
    task=runtime.state/'tasks'/binding['id']
    workspace=preparation_workspace(runtime.root,task/'campaign-workspace')
    original=workspace/'campaigns/isles24-pilot/pipeline/hosted-original'
    projection=original.parent/'hosted-recovery'
    event=runtime.event(binding);mode=configured['mode'];request=configured['request']
    def stages(recovery):return BrokerStages(runtime.config['broker_socket'],event,packet,client=request_broker,recovery=recovery)
    output=projection if projection.exists() else original
    if not (output/'receipt.json').exists():
        if projection.exists():raise ValueError('CAMPAIGN_RECOVERY_INCOMPLETE_NO_RETRY')
        if original.exists():
            recover_projection(SimpleNamespace(ROOT=workspace),mode,request,original,projection,stages(True));output=projection
        elif read_only or position!=0:raise ValueError('CAMPAIGN_OUTCOME_UNCERTAIN_NO_RETRY')
        else:run_pipeline(SimpleNamespace(ROOT=workspace),mode,request,original,stages(False))
    receipt=completed_pipeline(workspace,output,packet,event)
    if position==2:return receipt
    client=stages(True)
    if position==1:client.completed=['continuation']
    answer,model_receipt=client.call(('continuation','review')[position],'')
    return {'status':'COMPLETE','duplicate':True,'answer':answer,'receipt':model_receipt,
            'campaign_status':receipt['status'],'campaign_receipt_sha256':hashlib.sha256((output/'receipt.json').read_bytes()).hexdigest(),
            'campaign_output':output.relative_to(runtime.state).as_posix()}
