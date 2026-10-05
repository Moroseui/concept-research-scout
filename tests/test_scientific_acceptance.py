"""H2 application fixtures; simulated decisions never constitute scientific authority."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from orchestrator import scientific_acceptance as accept, continuing_operations as ops
from orchestrator import formal_decisions as formal, investigator_wakes as wakes
from orchestrator.hosted_cycle import encoded
from test_semantic_validation_contract import checked_import, validation_import
from test_validated_interpretation import setup


@pytest.fixture
def prepared(validation_import, monkeypatch, tmp_path):
    config, task, reader, response, reads, observed = setup(validation_import, monkeypatch, 'VALID')
    config.update(source='c'*40,source_root=str(tmp_path/'source'))
    monkeypatch.setattr(accept,'checked_source',lambda root,source:Path(root))
    monkeypatch.setattr('orchestrator.research_catalog.linked_change',lambda *a:{'fixture':True})
    monkeypatch.setattr('orchestrator.campaign.require_no_human_stop',lambda *a:None)
    identity='5'*64;folder=Path(config['state'])/'tasks'/identity;folder.mkdir(parents=True)
    change={'request_id':'6'*64,'applied_event':'7'*64}
    packet={'campaign_task':task,'research_catalog_entry':{'change_request':change}}
    sha=hashlib.sha256(encoded(packet)).hexdigest()
    files={'interpretation.md':'Fixture interpretation binds a VALID validator but acceptance remains separate.',
           'investigator_next_decision.json':json.dumps({'status':'PROPOSAL_ONLY','rationale':'Request formal judgment.'})}
    review=json.dumps({'verdict':'APPROVE','rationale':'Independent fixture interpretation review only.'})
    answers={'continuation':json.dumps(files),'review':json.dumps({'review.json':review}),
             'disposition':'Fixture disposition: interpretation approved as proposal only.'}
    replies={}
    for stage,answer in answers.items():
        model='claude-fable-5' if stage=='review' else 'gpt-6-astra'
        replies[stage]={'status':'COMPLETE','answer':answer,'packet_sha256':sha,
            'receipt':{'requested_model':'claude-fable-5' if stage=='review' else 'gpt-6-astra','actual_model':model,'returncode':0,'stage':stage,
            'session_id':'fixture-'+stage,'answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),
            'operating_context_sha256':'8'*64}}
    disposition={'task':identity,'source':config['source'],'status':'DISPOSITION_RECORDED',
        'review_verdict':'APPROVE','acceptance_status':'APPROVED_PROPOSAL_ONLY',
        'reviewer':{'session_id':'fixture-review','model':'claude-fable-5'},
        'disposition_actor':{'session_id':'fixture-disposition'},
        'disposition_sha256':hashlib.sha256(answers['disposition'].encode()).hexdigest(),
        'artifact_sha256':{'round-1/'+n:hashlib.sha256(x.encode()).hexdigest() for n,x in {**files,'review.json':review}.items()},
        'campaign_output':str((folder/'pipeline').relative_to(Path(config['state'])))}
    (folder/'packet.json').write_bytes(encoded(packet));(folder/'scientific-disposition.json').write_bytes(encoded(disposition))
    (folder/'pipeline/round-1').mkdir(parents=True)
    for n,x in {**files,'review.json':review}.items():(folder/'pipeline/round-1'/n).write_text(x)
    ref={'task':identity,'artifact':'round-1/interpretation.md','sha256':hashlib.sha256(files['interpretation.md'].encode()).hexdigest()}
    operations=[]
    def client(socket,operation,body):
        operations.append(operation)
        if operation=='stage_packet':return {'status':'COMPLETE','packet':packet,'packet_sha256':sha}
        if operation=='stage_status':return deepcopy(replies[body['stage']])
        return reader(socket,operation,body)
    request={**accept.prepare(config,ref,original_client=client),'schema':formal.SCHEMA,
        'source':config['source'],'workspace':None,'application':None,'change_request':change}
    path=Path(config['state'])/'formal-decisions/accept-fixture/round-1/decision.json'
    proof={'decision':'APPLY','_decision_sha256':'9'*64,
        'actor':{'family':'codex','model':'fixture-decision-model','session_id':'fixture-decision'},
        'policy':{'fixture':'delegated'},'transition':request['transition']}
    by={'kind':'agent','family':'codex','model':'fixture-applier','session_id':'fixture-applier'}
    monkeypatch.setattr(formal,'original_transport',lambda *a:{'packet':{'formal_request':request}})
    def verify(root,decision_path,**kw):
        assert decision_path==path
        for k in ('action','subject','bindings'):assert kw[k]==request[k]
        assert kw['source']==config['source']
        return deepcopy(proof)
    monkeypatch.setattr(formal,'verify_original_decision',verify)
    operations.clear();reads.clear()
    return SimpleNamespace(config=config,task=task,ref=ref,request=request,path=path,proof=proof,by=by,
        client=client,operations=operations,replies=replies,response=response,folder=folder)


def test_native_interpretation_and_validation_reach_distinct_formal_request(prepared):
    p=prepared
    request=accept.prepare(p.config,p.ref,original_client=p.client)
    assert request['action']=='accept_interpretation'
    assert request['transition']['to']=='AGENT_ACCEPTED'
    assert 'VALID is necessary but not sufficient' in request['request']
    assert 'Fixture interpretation' in request['evidence']['interpretation.md']
    assert 'Independent fixture' in request['evidence']['opposing-review.original.txt']
    assert 'Distinct validator explanation' in request['evidence']['semantic-validation.json']
    assert p.operations==['stage_packet','stage_status','stage_status','stage_status',
                          'scientific_job_result','scientific_validation_result']


def test_acceptance_is_separate_immutable_attributed_and_idempotent(prepared):
    p=prepared
    first=accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by)
    assert first['scientific_acceptance'] is True and first['adoption'] is False
    assert first['execution_authorized'] is False and first['model_calls']==0
    assert first['actor']==p.proof['actor'] and first['applied_by']==p.by
    state=Path(p.config['state'])
    before={str(x):x.read_bytes() for x in state.rglob('*') if x.is_file()}
    for _ in range(2):
        repeat=accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by)
        assert repeat=={**first,'duplicate':True}
        actual=accept.read_application(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by)
        assert actual=={k:v for k,v in first.items() if k!='duplicate'}
    assert before=={str(x):x.read_bytes() for x in state.rglob('*') if x.is_file()}
    assert set(p.operations)<={'stage_packet','stage_status','scientific_job_result','scientific_validation_result'}


def test_deferred_formal_decision_never_applies(prepared):
    p=prepared;p.proof['decision']='DEFER'
    with pytest.raises(ValueError,match='DEFERRED_RESULT'):accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by)
    assert not list(Path(p.config['state']).rglob('application.json'))


@pytest.mark.parametrize('status',['INVALID','DEFER'])
def test_nonvalid_semantic_output_cannot_be_accepted_even_by_wrong_apply(prepared,monkeypatch,status):
    p=prepared
    # Pure application guard independently rejects a contradictory APPLY. The
    # native context tamper tests separately ensure changed originals refuse.
    fresh={k:deepcopy(v) for k,v in p.request.items() if k not in ('schema','source','workspace','application','change_request')}
    value=json.loads(fresh['evidence']['semantic-validation.json']);value['receipt']['validator_status']=status
    fresh['evidence']['semantic-validation.json']=json.dumps(value)
    p.request['evidence']=fresh['evidence']
    monkeypatch.setattr(accept,'prepare',lambda *a,**k:fresh)
    with pytest.raises(ValueError,match='SEMANTIC_VALID'):accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by)


@pytest.mark.parametrize('damage',['review','disposition','interpretation','validation','source'])
def test_changed_originals_refuse_before_application(prepared,damage):
    p=prepared
    if damage in ('review','disposition'):p.replies[damage]['answer']+='changed'
    elif damage=='interpretation':(p.folder/'pipeline/round-1/interpretation.md').write_text('changed')
    elif damage=='validation':p.response['output']+='\n'
    else:p.config['source']='a'*40
    with pytest.raises(ValueError):accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by)
    assert not list(Path(p.config['state']).rglob('application.json'))


def test_current_criticism_and_human_stop_block_application(prepared,monkeypatch):
    p=prepared
    def refuse(*a):raise ValueError('RESEARCH_CHANGE_REVIEW_PENDING')
    monkeypatch.setattr('orchestrator.research_catalog.linked_change',refuse)
    with pytest.raises(ValueError,match='REVIEW_PENDING'):accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by)
    monkeypatch.setattr('orchestrator.research_catalog.linked_change',lambda *a:None)
    monkeypatch.setattr('orchestrator.campaign.require_no_human_stop',lambda *a:(_ for _ in ()).throw(ValueError('HUMAN_STOP')))
    with pytest.raises(ValueError,match='HUMAN_STOP'):accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by)


def test_explicit_partial_recovery_uses_same_intent_and_no_new_model(prepared,monkeypatch):
    p=prepared;native=accept.immutable
    def interrupted(path,data):
        if path.name=='application.json':raise OSError('simulated interruption before receipt')
        return native(path,data)
    monkeypatch.setattr(accept,'immutable',interrupted)
    with pytest.raises(OSError):accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by)
    monkeypatch.setattr(accept,'immutable',native)
    with pytest.raises(ValueError,match='PARTIAL_APPLICATION'):accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by)
    result=accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by,recover=True)
    assert result['status']==accept.STATUS
    assert len(list(Path(p.config['state']).rglob('application.json')))==1
    assert 'model_stage' not in p.operations


def test_optional_task_originals_do_not_expand_normal_wake(prepared):
    p=prepared
    usual=wakes._task(p.config,p.ref['task'],p.client)
    expanded=wakes._task(p.config,p.ref['task'],p.client,include_originals=True)
    assert 'original_answers' not in usual and 'original_receipts' not in usual
    assert {k:v for k,v in expanded.items() if k not in ('original_answers','original_receipts')}==usual


@pytest.mark.parametrize('empty_directory',[False,True])
def test_explicit_recovery_before_application_intent_is_idempotent(prepared,empty_directory):
    p=prepared
    if empty_directory:
        folder=Path(p.config['state'])/'scientific-results'/p.request['bindings']['completion']/'acceptance'/p.ref['task']
        folder.parent.mkdir(mode=0o700);folder.mkdir(mode=0o700)
    first=accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by,recover=True)
    second=accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by,recover=True)
    assert first['duplicate'] is False and second['duplicate'] is True
    assert 'model_stage' not in p.operations


def test_corrupt_partial_intent_is_preserved_and_refuses_recovery(prepared):
    p=prepared
    folder=Path(p.config['state'])/'scientific-results'/p.request['bindings']['completion']/'acceptance'/p.ref['task']
    folder.parent.mkdir(mode=0o700);folder.mkdir(mode=0o700);(folder/'intent.json').write_bytes(b'{"partial":')
    with pytest.raises(ValueError):
        accept.apply(p.config,p.ref,p.request,p.path,original_client=p.client,by=p.by,recover=True)
    assert (folder/'intent.json').read_bytes()==b'{"partial":'
    assert not (folder/'application.json').exists()
