"""Actual coordinator and campaign path, with explicitly synthetic model replies."""
import hashlib
import json
import subprocess
from pathlib import Path
from unittest.mock import patch
import pytest
from orchestrator.hosted_cycle import encoded
from orchestrator.hosted_campaign_task import preparation_workspace,task_contract


def source(tmp_path):
    root=tmp_path/'source';root.mkdir()
    subprocess.run(['git','init','-q',str(root)],check=True)
    (root/'source.md').write_text('Reviewed synthetic source')
    subprocess.run(['git','-C',str(root),'add','source.md'],check=True)
    return root


def test_workspace_copies_only_materialized_tracked_source_and_refuses_edits(tmp_path):
    root=source(tmp_path);(root/'private-untracked.txt').write_text('Not a source input')
    destination=tmp_path/'workspace'
    preparation_workspace(root,destination)
    assert not (destination/'private-untracked.txt').exists()
    assert not (destination/'.git').exists()
    (destination/'source.md').write_text('Human edit preserved')
    with pytest.raises(ValueError,match='INPUT_CHANGED'):preparation_workspace(root,destination)
    assert (destination/'source.md').read_text()=='Human edit preserved'


def test_request_contract_excludes_patient_and_other_pipeline_routes():
    assert task_contract({'mode':'readiness','request':'Assess bounded readiness','trigger_job':'fixture'})['experiment']=='P001'
    with pytest.raises(ValueError,match='TASK_CONTRACT'):
        task_contract({'mode':'code','request':'Run a patient','trigger_job':'fixture'})


def test_completion_task_runs_shared_pipeline_and_retrieves_review_once(tmp_path,monkeypatch):
    from orchestrator.handover_runtime import Runtime
    import orchestrator.handover_runtime as module
    root=source(tmp_path)
    monkeypatch.setattr(module,'checked_source',lambda root,pin:Path(root))
    config={'source_root':str(root),'source':'a'*40,'controller_uid':module.os.getuid(),
            'state':str(tmp_path/'state'),'broker_socket':'fixture',
            'campaign_preparation':{'mode':'discuss','request':'Assess next authorized readiness action.','trigger_job':'fixture'}}
    r=Runtime(config);calls=[];saved={}
    def broker(socket,operation,body):
        stage=body.get('stage');calls.append((operation,stage))
        if operation=='stage_status':return dict(saved[stage],duplicate=True)
        assert operation=='model_stage' and stage not in saved
        answer={'continuation':json.dumps({'discussion.md':'Exploratory baseline; launch remains reserved.'}),
                'review':json.dumps({'review.json':json.dumps({'verdict':'APPROVE','rationale':'Bounded preparation only.'})}),
                'disposition':'Keep launch blocked pending preflight evidence.'}[stage]
        model='claude-fable-5' if stage=='review' else 'gpt-6-astra'
        saved[stage]={'status':'COMPLETE','duplicate':False,'answer':answer,
            'packet_sha256':hashlib.sha256(encoded(body['packet'])).hexdigest(),
            'receipt':{'returncode':0,'requested_model':model,'actual_model':model,'session_id':'synthetic-fixture',
                       'answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),'operating_context_sha256':'b'*64}}
        return saved[stage]
    monkeypatch.setattr(module,'request_broker',broker)
    r.q.admission=lambda binding:{'status':'ADMITTED'}
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        binding=r.enqueue_report('2026-09-07',[],{'completed_job':'fixture'},trigger='verified-completion')
        r.q.submit(binding);r.q.tick();r.bookkeeping()
        assert r.q.status()['tasks'][0]['status']=='COMPLETE'
        assert [stage for op,stage in calls if op=='model_stage']==['continuation','review','disposition']
        assert r.q.submit(binding)['duplicate'] is True
        r.q.tick();r.bookkeeping()
        assert len([op for op,stage in calls if op=='model_stage'])==3
        folder=r.state/'tasks'/binding['id']/'campaign-workspace/campaigns/isles24-pilot/pipeline/hosted-original'
        assert json.loads((folder/'receipt.json').read_text())['status']=='REVIEWED_PROPOSAL_NOT_ADOPTED'
        assert r.status()['bookkeeping'][0]['status']=='COMPLETE'
        # Lost final pipeline/coordinator bookkeeping must reuse original models.
        (folder/'receipt.json').unlink()
        (r.state/(binding['id']+'-0.json')).unlink()
        r.q.db.execute("UPDATE tasks SET status='BLOCKED' WHERE id=?",(binding['id'],))
        r.recover();r.q.tick()
        assert r.q.status()['tasks'][0]['status']=='COMPLETE'
        projection=folder.parent/'hosted-recovery'
        assert json.loads((projection/'recovery.json').read_text())['new_model_calls']==0
        assert not (folder/'receipt.json').exists()
        assert len([op for op,stage in calls if op=='model_stage'])==3
        folder=projection
        # A completed model reply cannot mask subsequent artifact corruption.
        (folder/'round-1/discussion.md').write_text('Conflicting human correction')
        with pytest.raises(ValueError,match='ARTIFACT_CHANGED'):r.model(binding,1)
        assert len([op for op,stage in calls if op=='model_stage'])==3
