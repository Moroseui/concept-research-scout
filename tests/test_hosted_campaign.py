import hashlib
import json
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from orchestrator.hosted_campaign import BrokerStages, run_pipeline, recover_projection
from orchestrator.hosted_cycle import encoded


def client_for(answers):
    calls=[];packet_hashes={}
    def call(socket,op,body):
        calls.append(body['stage']);answer=answers[len(calls)-1]
        if 'packet' in body:packet_hashes['fixture']=hashlib.sha256(encoded(body['packet'])).hexdigest()
        model='claude-fable-5' if body['stage']=='review' else 'gpt-6-astra'
        return {'status':'COMPLETE','duplicate':False,'answer':answer,'packet_sha256':packet_hashes['fixture'],'receipt':{'requested_model':model,
            'actual_model':model if model.startswith('claude') else None,'returncode':0,
            'answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),'operating_context_sha256':'a'*64}}
    return call,calls


def test_real_pipeline_interface_uses_two_stages_and_preserves_proposals(tmp_path):
    client,calls=client_for([json.dumps({'discussion.md':'Exploratory proposal; no launch.'}),
                             json.dumps({'review.json':json.dumps({'verdict':'APPROVE','rationale':'Synthetic valid scope'})})])
    stages=BrokerStages('fixture',{}, {'campaign_artifacts':{'version':1,'experiment':'P001','mode':'discuss'}},client=client)
    output=tmp_path/'campaigns/isles24-pilot/pipeline/fixture'
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        receipt=run_pipeline(SimpleNamespace(ROOT=tmp_path),'discuss','Bounded question',output,stages)
    assert calls==['continuation','review'] and receipt['round']==1
    assert receipt['status']=='REVIEWED_PROPOSAL_NOT_ADOPTED'
    assert not list(output.rglob('*.stdout'))
    with pytest.raises(ValueError,match='AUTHOR_REVIEW_BOUND'):
        stages(None,output,'codex','campaign_discuss','repair',['discussion.md'])
    assert len(calls)==2


def test_bad_answer_hash_refuses_before_artifact_write(tmp_path):
    def bad(*args):return {'status':'COMPLETE','answer':'{}','receipt':{'requested_model':'gpt-6-astra','returncode':0,'answer_sha256':'b'*64,'operating_context_sha256':'a'*64}}
    stages=BrokerStages('fixture',{}, {},client=bad)
    with pytest.raises(ValueError,match='RECEIPT_BINDING'):
        stages(None,tmp_path,'codex','campaign_discuss','question',['discussion.md'])
    assert not list(tmp_path.iterdir())


def test_extra_artifact_is_rejected(tmp_path):
    client,_=client_for([json.dumps({'discussion.md':'Allowed','run.py':'Not allowed'})])
    with pytest.raises(ValueError,match='FILE_SCHEMA'):
        BrokerStages('fixture',{}, {},client=client)(None,tmp_path,'codex','campaign_discuss','question',['discussion.md'])
    assert not list(tmp_path.iterdir())


def test_campaign_json_format_is_explicit_and_legacy_unchanged():
    from orchestrator.protected_handover import model_output_format
    packet={'campaign_artifacts':{'version':1,'experiment':'P001','mode':'readiness'}}
    assert [model_output_format(packet,s) for s in ('continuation','review','disposition')]==['json','json','markdown']
    assert model_output_format({},'review')=='markdown'
    assert model_output_format({'execution_proposal':{}},'disposition')=='json'
    packet['campaign_artifacts']['experiment']='P002'
    with pytest.raises(ValueError,match='CAMPAIGN_ARTIFACT_CONTRACT'):model_output_format(packet,'review')


def test_nonstring_artifact_has_named_refusal(tmp_path):
    client,_=client_for([json.dumps({'discussion.md':{'bad':'object'}})])
    with pytest.raises(ValueError,match='FILE_SCHEMA'):
        BrokerStages('fixture',{}, {},client=client)(None,tmp_path,'codex','campaign_discuss','question',['discussion.md'])
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('reason,expected',[('SUPERVISED_MODEL_BUDGET_EXHAUSTED','SUPERVISED_MODEL_BUDGET_EXHAUSTED'),('private arbitrary diagnostic','BROKER_REFUSED_RECONCILE')])
def test_socket_refusal_preserves_only_named_public_reason(monkeypatch,reason,expected):
    from orchestrator.handover_runtime import request_broker
    class Socket:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def settimeout(self,*args):pass
        def connect(self,*args):pass
        def sendall(self,*args):pass
        def recv(self,*args):return (json.dumps({'status':'REFUSED','reason':reason})+'\n').encode()
    monkeypatch.setattr('orchestrator.handover_runtime.socket.socket',lambda *args:Socket())
    with pytest.raises(ValueError,match='^'+expected+'$'):request_broker('fixture','model_stage',{})


def test_recovery_reads_original_replies_and_never_calls_model(tmp_path):
    packet={'campaign_artifacts':{'version':1,'experiment':'P001','mode':'discuss'}}
    replies=[json.dumps({'discussion.md':'Original checked proposal'}),json.dumps({'review.json':json.dumps({'verdict':'APPROVE','rationale':'Original review'})})]
    responses={};base_client,_=client_for(replies)
    def capture(socket,op,body):
        response=base_client(socket,op,body);responses[body['stage']]=response;return response
    original=tmp_path/'campaigns/isles24-pilot/pipeline/original'
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        run_pipeline(SimpleNamespace(ROOT=tmp_path),'discuss','Question',original,BrokerStages('fixture',{},packet,client=capture))
        # Model review completed; emulate lost final pipeline bookkeeping.
        (original/'receipt.json').unlink()
        requests=[]
        def read(socket,op,body):
            requests.append(op);assert op=='stage_status'
            return dict(responses[body['stage']],duplicate=True)
        output=original.parent/'recovery'
        result=recover_projection(SimpleNamespace(ROOT=tmp_path),'discuss','Question',original,output,BrokerStages('fixture',{},packet,client=read,recovery=True))
    assert requests==['stage_status','stage_status']
    assert result['status']=='REVIEWED_PROPOSAL_NOT_ADOPTED'
    assert (original/'round-1/discussion.md').read_bytes()==(output/'round-1/discussion.md').read_bytes()
    assert json.loads((output/'recovery.json').read_text())['new_model_calls']==0
    assert not (original/'receipt.json').exists()
    (original/'round-1/discussion.md').write_text('Human correction awaiting review')
    conflicted=original.parent/'conflict-recovery'
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        with pytest.raises(ValueError,match='PRESERVES_CONFLICTING_ORIGINAL'):
            recover_projection(SimpleNamespace(ROOT=tmp_path),'discuss','Question',original,conflicted,BrokerStages('fixture',{},packet,client=read,recovery=True))
    assert not conflicted.exists()
    assert (original/'round-1/discussion.md').read_text()=='Human correction awaiting review'


def test_recovery_missing_completion_never_submits_model(tmp_path):
    original=tmp_path/'campaigns/isles24-pilot/pipeline/original';original.mkdir(parents=True)
    packet={'campaign_artifacts':{'version':1,'experiment':'P001','mode':'discuss'}}
    hashes={'related-evidence.json':hashlib.sha256(json.dumps({}).encode()).hexdigest()}
    (original/'request.json').write_text(json.dumps({'mode':'discuss','experiment':'P001','request':'Question','max_rounds':1,'input_sha256':hashes,'initiator':{'event':{},'packet_sha256':hashlib.sha256(encoded(packet)).hexdigest()}}))
    def missing(socket,operation,body):
        assert operation=='stage_status'
        return {'status':'NOT_OBSERVED_NO_RETRY'}
    output=original.parent/'recovery'
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        with pytest.raises(ValueError,match='BLOCKED_RECONCILE_NO_RETRY'):
            recover_projection(SimpleNamespace(ROOT=tmp_path),'discuss','Question',original,output,BrokerStages('fixture',{},packet,client=missing,recovery=True))
    assert not output.exists()


def test_packet_mismatch_refuses_recovered_reply_before_write(tmp_path):
    answer=json.dumps({'discussion.md':'Wrong binding'})
    def wrong(socket,operation,body):
        assert operation=='stage_status'
        return {'status':'COMPLETE','packet_sha256':'f'*64,'answer':answer,'receipt':{'returncode':0,'requested_model':'gpt-6-astra','answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),'operating_context_sha256':'a'*64}}
    with pytest.raises(ValueError,match='RECEIPT_BINDING'):
        BrokerStages('fixture',{}, {},client=wrong,recovery=True)(None,tmp_path,'codex','campaign_discuss','Question',['discussion.md'])
    assert not list(tmp_path.iterdir())


def test_recovery_cannot_turn_negative_review_into_approval(tmp_path):
    packet={'campaign_artifacts':{'version':1,'experiment':'P001','mode':'discuss'}}
    answers=[json.dumps({'discussion.md':'Proposal requiring revision'}),
             json.dumps({'review.json':json.dumps({'verdict':'REVISE','rationale':'Missing source evidence'})})]
    responses={};base,_=client_for(answers)
    def capture(socket,operation,body):
        response=base(socket,operation,body);responses[body['stage']]=response;return response
    original=tmp_path/'campaigns/isles24-pilot/pipeline/original'
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        with pytest.raises(ValueError,match='revision limit'):
            run_pipeline(SimpleNamespace(ROOT=tmp_path),'discuss','Question',original,BrokerStages('fixture',{},packet,client=capture))
        before={p.relative_to(original):p.read_bytes() for p in original.rglob('*') if p.is_file()}
        calls=[]
        def read(socket,operation,body):
            calls.append(operation);assert operation=='stage_status'
            return dict(responses[body['stage']],duplicate=True)
        output=original.parent/'recovery'
        with pytest.raises(ValueError,match='revision limit'):
            recover_projection(SimpleNamespace(ROOT=tmp_path),'discuss','Question',original,output,BrokerStages('fixture',{},packet,client=read,recovery=True))
    assert calls==['stage_status','stage_status']
    assert not (output/'receipt.json').exists()
    assert (output/'blocked.json').exists()
    assert {p.relative_to(original):p.read_bytes() for p in original.rglob('*') if p.is_file()}==before


def test_recovery_refuses_nested_destination_and_unbound_original(tmp_path):
    original=tmp_path/'campaigns/isles24-pilot/pipeline/original';original.mkdir(parents=True)
    stages=BrokerStages('fixture',{'turn_id':'a'*64},{},client=lambda *args:pytest.fail('No broker access allowed'),recovery=True)
    with pytest.raises(ValueError,match='FRESH_RECOVERY_PROJECTION_REQUIRED'):
        recover_projection(SimpleNamespace(ROOT=tmp_path),'discuss','Question',original,original/'nested',stages)
    assert not (original/'nested').exists()
    (original/'request.json').write_text('{}')
    with pytest.raises(ValueError,match='ORIGINAL_TURN_BINDING_REQUIRED'):
        recover_projection(SimpleNamespace(ROOT=tmp_path),'discuss','Question',original,original.parent/'projection',stages)
    assert not (original.parent/'projection').exists()


def test_escaped_response_budget_refuses_before_writing_artifacts(tmp_path):
    answer=json.dumps({'discussion.md':'\u4e00'*15000},ensure_ascii=False)
    client,_=client_for([answer])
    assert len(answer.encode())<80000
    with pytest.raises(ValueError,match='PUBLIC_TEXT_REJECTED'):
        BrokerStages('fixture',{}, {},client=client).call('continuation','Question')
    assert not list(tmp_path.iterdir())
