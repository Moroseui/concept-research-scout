"""Synthetic model replies exercise negative scientific outcomes, never real models."""
import hashlib
import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from orchestrator import campaign_pipeline
from orchestrator import handover_runtime as runtime
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded
from orchestrator.operations_report import Queue
from test_installed_research_request import prepared, Broker


class ReviewBroker(Broker):
    criticism='Missing original criticism remains unresolved.\nDo not accept the comparison until corrected.'

    def __init__(self,verdict):
        super().__init__();self.verdict=verdict;self.prompts={}

    def __call__(self,socket,operation,body):
        result=super().__call__(socket,operation,body)
        if operation=='model_stage':
            stage=body['stage'];self.prompts[stage]=body['prompt']
            if stage!='review':result['receipt']['actual_model']=None  # Matches the actual Codex CLI evidence limit.
            if stage=='review':
                result['answer']=json.dumps({'review.json':json.dumps({'verdict':self.verdict,'rationale':self.criticism},indent=2)})
            elif stage=='disposition':
                result['answer']='Synthetic disposition: preserve the exact review and request the missing evidence; no execution.'
            result['receipt']['answer_sha256']=hashlib.sha256(result['answer'].encode()).hexdigest()
        return result


@pytest.mark.parametrize('verdict',['APPROVE','REVISE','REQUEST_CHANGES'])
def test_review_outcome_reaches_disposition_without_report_review_or_duplicate(prepared,monkeypatch,verdict):
    prepared.config.update(purpose='LIVE_APPROVED_HANDOVER',publication={'checkout':'unused','permission_sha256':'c'*64})
    r=runtime.Runtime(prepared.config);broker=ReviewBroker(verdict)
    monkeypatch.setattr(runtime,'request_broker',broker)
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        task=r.submit_research()['task']
        assert r.q.tick()['status']=='COMPLETE'
        r.bookkeeping();r.deliver_reports()
        folder=r.state/'tasks'/task
        record=json.loads((folder/'scientific-disposition.json').read_text())
        assert record['review_verdict']==verdict
        assert record['acceptance_status']==('APPROVED_PROPOSAL_ONLY' if verdict=='APPROVE' else 'NOT_ACCEPTED')
        assert record['campaign_status']==('REVIEWED_PROPOSAL_NOT_ADOPTED' if verdict=='APPROVE' else 'REVISION_REQUIRED')
        assert record['reviewer']['answer_sha256']==broker.saved['review']['receipt']['answer_sha256']
        assert record['disposition_sha256']==broker.saved['disposition']['receipt']['answer_sha256']
        assert record['disposition_actor']['requested_model']=='gpt-6-astra'
        assert record['disposition_actor']['actual_model'] is None
        assert record['disposition_actor']['model_identity_source']=='CLI request; provider actual model unavailable'
        assert 'model' not in record['disposition_actor']
        assert record['reviewer']['model']=='claude-fable-5'
        assert broker.saved['review']['answer'] in broker.prompts['disposition']
        assert 'Do not override a negative review' in broker.prompts['disposition']
        assert 'operational report has no report review' in broker.prompts['disposition']
        report=record['operational_report']['id']
        assert Queue(r.state/'reports').status(report)['status']=='QUEUED'
        assert not (r.state/'reports'/(report+'.claude-review.json')).exists()
        assert record['operational_report']['review_status']=='NOT_REVIEWED_BY_SCIENTIFIC_STAGE'
        assert r.status()['bookkeeping'][0]['status']=='COMPLETE'
        assert r.status()['report_delivery'][0]['status']=='PRIVATE_ONLY'
        assert [stage for op,stage in broker.calls if op=='model_stage']==['continuation','review','disposition']
        assert r.submit_research()['duplicate']
        r.q.tick();r.bookkeeping()
        assert len([op for op,stage in broker.calls if op=='model_stage'])==3
        # Original negative artifact is never an adoptable reviewed proposal.
        if verdict!='APPROVE':
            workspace=folder/'campaign-workspace'
            with pytest.raises(ValueError,match='REVIEWED_CAMPAIGN_PROPOSAL_REQUIRED'):
                campaign_pipeline.reviewed_proposal(workspace,record['campaign_output'].split('campaign-workspace/')[1],'P001')
        pipeline=folder/'campaign-workspace/campaigns/isles24-pilot/pipeline/hosted-original'
        original=(pipeline/'round-1/review.json').read_bytes()
        (pipeline/'receipt.json').unlink();(r.state/(task+'-0.json')).unlink()
        r.q.db.execute("UPDATE tasks SET status='BLOCKED' WHERE id=?",(task,))
        r.recover();assert r.q.tick()['status']=='COMPLETE'
        projection=pipeline.parent/'hosted-recovery'
        recovered=json.loads((projection/'receipt.json').read_text())
        assert recovered['review_verdict']==verdict and recovered['status']==record['campaign_status']
        assert (projection/'round-1/review.json').read_bytes()==original
        assert json.loads((projection/'recovery.json').read_text())['new_model_calls']==0
        assert len([op for op,stage in broker.calls if op=='model_stage'])==3


@pytest.mark.parametrize('fault',['status','verdict','acceptance','missing_policy','round_type','artifact','original','coordinator'])
def test_negative_tamper_refused_before_disposition_model(prepared,monkeypatch,fault):
    r=runtime.Runtime(prepared.config);broker=ReviewBroker('REQUEST_CHANGES')
    monkeypatch.setattr(runtime,'request_broker',broker)
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        task=r.submit_research()['task']
        binding=json.loads(r.q.db.execute('SELECT binding FROM tasks WHERE id=?',(task,)).fetchone()[0])
        for position in (0,1):
            output=r.model(binding,position)
            (r.state/(task+'-'+str(position)+'.json')).write_bytes(encoded(
                {'binding':digest(binding),'position':position,'output':output,'output_sha256':digest(output)}))
        pipeline=r.state/'tasks'/task/'campaign-workspace/campaigns/isles24-pilot/pipeline/hosted-original'
        receipt_path=pipeline/'receipt.json';receipt=json.loads(receipt_path.read_text())
        error='CAMPAIGN_REVIEW_POLICY_BINDING'
        if fault=='status':receipt['status']='REVIEWED_PROPOSAL_NOT_ADOPTED';error='CAMPAIGN_REVIEW_STATUS_MISMATCH'
        elif fault=='verdict':receipt['review_verdict']='APPROVE'
        elif fault=='acceptance':receipt['acceptance_status']='APPROVED_PROPOSAL_ONLY'
        elif fault=='missing_policy':receipt.pop('review_completion_policy')
        elif fault=='round_type':receipt['round']=True;error='CAMPAIGN_REVIEWED_RESULT_REQUIRED'
        elif fault in ('artifact','original'):
            path=pipeline/'round-1/review.json'
            path.write_text(json.dumps({'verdict':'REQUEST_CHANGES','rationale':'Rewritten criticism'}))
            error='CAMPAIGN_RESULT_ARTIFACT_CHANGED'
            if fault=='original':
                receipt['artifact_sha256']['round-1/review.json']=hashlib.sha256(path.read_bytes()).hexdigest()
                error='CAMPAIGN_ARTIFACT_ORIGINAL_REPLY_MISMATCH'
        else:
            path=r.state/(task+'-1.json');value=json.loads(path.read_text())
            value['output']['answer']='Rewritten predecessor criticism'
            value['output_sha256']=digest(value['output']);path.write_bytes(encoded(value))
            error='CAMPAIGN_PREDECESSOR_ORIGINAL_REPLY_MISMATCH'
        receipt_path.write_text(json.dumps(receipt))
        with pytest.raises(ValueError,match=error):r.model(binding,2)
        assert [stage for op,stage in broker.calls if op=='model_stage']==['continuation','review']


def test_local_single_round_negative_still_blocks_and_option_is_bounded(tmp_path):
    def stage(sc,out,family,label,body,names):
        for name in names:
            (out/name).write_text(json.dumps({'verdict':'REVISE','rationale':'Synthetic correction'}) if name=='review.json' else 'Synthetic proposal')
        return {'family_effective':family,'exit_class':'ok','ci':False}
    sc=SimpleNamespace(ROOT=tmp_path)
    output=tmp_path/'campaigns/isles24-pilot/pipeline/local'
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        with pytest.raises(ValueError,match='revision limit'):
            campaign_pipeline.execute(sc,'discuss','P001','Question',output,max_rounds=1,stage_runner=stage)
    assert not (output/'receipt.json').exists()
    for options in ({'max_rounds':2,'stage_runner':stage},{'max_rounds':1},{'max_rounds':1,'stage_runner':stage,'complete_negative_review':'yes'}):
        with pytest.raises(ValueError,match='CAMPAIGN_NEGATIVE_COMPLETION_SCOPE'):
            campaign_pipeline.execute(sc,'discuss','P001','Question',output.parent/'invalid',**{'complete_negative_review':True,**options})


@pytest.mark.parametrize('review',[{'verdict':'REQUEST_CHANGE','rationale':'Typo is not a verdict'},
    {'verdict':'REQUEST_CHANGES','rationale':' '},
    {'verdict':'REQUEST_CHANGES','rationale':'Valid words','approved':True}])
def test_completed_negative_option_still_requires_exact_review_schema(tmp_path,review):
    def stage(sc,out,family,label,body,names):
        for name in names:(out/name).write_text(json.dumps(review) if name=='review.json' else 'Synthetic proposal')
        return {'family_effective':family,'exit_class':'ok','ci':False}
    output=tmp_path/'campaigns/isles24-pilot/pipeline/malformed'
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        with pytest.raises(ValueError,match='malformed review'):
            campaign_pipeline.execute(SimpleNamespace(ROOT=tmp_path),'discuss','P001','Question',output,
                max_rounds=1,stage_runner=stage,complete_negative_review=True)
    assert not (output/'receipt.json').exists()
    assert json.loads((output/'round-1/review.json').read_text())==review
