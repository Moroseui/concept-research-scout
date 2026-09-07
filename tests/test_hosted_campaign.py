import hashlib
import json
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from orchestrator.hosted_campaign import BrokerStages, run_pipeline


def client_for(answers):
    calls=[]
    def call(socket,op,body):
        calls.append(body['stage']);answer=answers[len(calls)-1]
        model='claude-fable-5' if body['stage']=='review' else 'gpt-6-astra'
        return {'status':'COMPLETE','answer':answer,'receipt':{'requested_model':model,
            'actual_model':model if model.startswith('claude') else None,'returncode':0,
            'answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),'operating_context_sha256':'a'*64}}
    return call,calls


def test_real_pipeline_interface_uses_two_stages_and_preserves_proposals(tmp_path):
    client,calls=client_for([json.dumps({'discussion.md':'Exploratory proposal; no launch.'}),
                             json.dumps({'review.json':json.dumps({'verdict':'APPROVE','rationale':'Synthetic valid scope'})})])
    stages=BrokerStages('fixture',{}, {},client=client)
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
