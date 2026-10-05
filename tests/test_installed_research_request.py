"""Configured human/agent submission; model responses and root ownership are fixtures."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from orchestrator.hosted_cycle import encoded
from orchestrator.hosted_campaign_task import task_contract
import orchestrator.handover_runtime as module


@pytest.fixture
def prepared(tmp_path,monkeypatch):
    root=tmp_path/'source';root.mkdir()
    subprocess.run(['git','init','-q',str(root)],check=True)
    (root/'source.md').write_text('Reviewed source fixture')
    legacy = root/'orchestrator/hosted_context.py'
    legacy.parent.mkdir()
    legacy.write_text('# Explicit original-only presentation fixture.\n')
    subprocess.run(['git','-C',str(root),'add','source.md'],check=True)
    parent=tmp_path/'installed';parent.mkdir(mode=0o750);parent.chmod(0o750)
    evidence=parent/'research-evidence.json'
    evidence.write_bytes(encoded({'qualified_aggregate':'Reviewed exploratory context; originals retained.'}))
    evidence.chmod(0o640)
    # Exercise actual descriptor reads, permissions, hashes and O_NOFOLLOW. Only
    # root ownership is simulated because the test runner is an ordinary user.
    real_stat=Path.stat;real_fstat=os.fstat
    def root_stat(value):
        fields=list(value);fields[4]=0
        return os.stat_result(fields)
    def observed_stat(path,*args,**kwargs):
        value=real_stat(path,*args,**kwargs)
        return root_stat(value) if path==parent else value
    def observed_fstat(fd):
        value=real_fstat(fd)
        try:target=Path(os.readlink('/proc/self/fd/'+str(fd)))
        except OSError:return value
        return root_stat(value) if target==evidence else value
    monkeypatch.setattr(Path,'stat',observed_stat)
    monkeypatch.setattr(module.os,'fstat',observed_fstat)
    monkeypatch.setattr(module,'checked_source',lambda path,pin:Path(path))
    # Input presentation imports this reader at call time; bind the same
    # synthetic source instead of accidentally inspecting an empty Git HEAD.
    def fixture_source(path, pin):
        assert Path(path) == root and pin == 'a'*40
        return root
    monkeypatch.setattr('orchestrator.remote_supervisor.checked_source', fixture_source)
    monkeypatch.setattr('orchestrator.disposition_successors.checked_source', fixture_source)
    # Queue/recovery fixtures have no installed policy tree. Keep the actual
    # preflight/size measurement, but supply the same explicit synthetic context
    # used by catalogue tests. Dedicated context tests exercise real documents.
    monkeypatch.setattr('orchestrator.hosted_context.build',
        lambda root,state: {'task_state':state,'policy':'Synthetic fixed policy.'})
    config={'source_root':str(root),'source':'a'*40,'controller_uid':os.getuid(),
        'controller_gid':os.getgid(),'state':str(tmp_path/'state'),'broker_socket':'fixture',
        'research_request':{'task':{'mode':'discuss','request':'Assess this bounded comparison question.',
            'task_id':'external-comparison-fixture'},'day':'2026-09-10',
            'evidence_file':str(evidence),'evidence_sha256':hashlib.sha256(evidence.read_bytes()).hexdigest(),
            'initiator':{'kind':'agent','family':'codex','model':'gpt-6-astra','session_id':'synthetic-fixture'}}}
    return SimpleNamespace(config=config,root=root,evidence=evidence,parent=parent)


class Broker:
    def __init__(self):self.calls=[];self.saved={}

    def __call__(self,socket,operation,body):
        stage=body.get('stage');self.calls.append((operation,stage))
        if operation=='admit_server':return {'status':'ADMITTED'}
        if operation=='stage_status':return dict(self.saved[stage],duplicate=True)
        assert operation=='model_stage' and stage not in self.saved
        answer={'continuation':json.dumps({'discussion.md':'Qualified exploratory comparison limitations.'}),
            'review':json.dumps({'review.json':json.dumps({'verdict':'APPROVE','rationale':'Retain the evidence limitations.'})}),
            'disposition':'Accept the bounded discussion; preserve the missing-original dependency.'}[stage]
        model='claude-fable-5' if stage=='review' else 'gpt-6-astra'
        response={'status':'COMPLETE','duplicate':False,'answer':answer,
            'packet_sha256':hashlib.sha256(encoded(body['packet'])).hexdigest(),
            'receipt':{'returncode':0,'requested_model':model,'actual_model':model,'session_id':'synthetic-fixture',
                'answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),'operating_context_sha256':'b'*64}}
        self.saved[stage]=response
        return response


def test_direct_submission_is_shared_saved_work_without_models_or_synthetic_job(prepared,monkeypatch):
    r=module.Runtime(prepared.config)
    monkeypatch.setattr(module,'request_broker',lambda *args:pytest.fail('submission must not admit or call models'))
    first=r.submit_research()
    assert first['status']=='QUEUED' and first['model_calls']==first['admissions']==0
    assert first['request_initiator']==prepared.config['research_request']['initiator']
    assert r.completions is None and r.status()['execution_jobs']==[]
    assert r.status()['report_directory']==str(r.state/'reports')
    folder=r.state/'tasks'/first['task'];original=(folder/'packet.json').read_bytes()
    packet=json.loads(original)
    assert packet['campaign_task']['task_id']=='external-comparison-fixture'
    assert packet['reviewer_evidence']==json.loads(prepared.evidence.read_bytes())
    assert packet['research_request_binding']['evidence_sha256']==prepared.config['research_request']['evidence_sha256']
    report=json.loads((folder/'report.json').read_text())
    assert 'Reviewed exploratory context' not in (r.state/'reports'/(report['id']+'.md')).read_text()
    # A new controller instance recovers the same submission. It must not rebuild
    # its identity from mutable report/change context or enqueue a second task.
    resumed=module.Runtime(prepared.config)
    monkeypatch.setattr(resumed,'enqueue_report',lambda *args,**kwargs:pytest.fail('must reuse saved submission'))
    again=resumed.submit_research()
    assert again['duplicate'] is True and again['task']==first['task']
    assert len(resumed.q.status()['tasks'])==1 and (folder/'packet.json').read_bytes()==original


def test_submission_survives_transaction_failure_without_duplicate_task(prepared,monkeypatch):
    r=module.Runtime(prepared.config);submit=r.q.submit
    def fail_after_insert(binding):
        submit(binding)
        raise RuntimeError('Simulated lost submission transaction')
    monkeypatch.setattr(r.q,'submit',fail_after_insert)
    with pytest.raises(RuntimeError,match='Simulated'):r.submit_research()
    assert r.q.status()['tasks']==[] and r.status()['research_submissions']==[]
    preserved=list((r.state/'tasks').glob('*/packet.json'))
    assert len(preserved)==1
    original=preserved[0].read_bytes()
    monkeypatch.setattr(r.q,'submit',submit)
    result=r.submit_research()
    assert len(r.q.status()['tasks'])==1 and preserved[0].read_bytes()==original
    assert r.submit_research()['task']==result['task']


def test_pause_blocks_admission_but_keeps_inspectable_submission(prepared,monkeypatch):
    r=module.Runtime(prepared.config)
    r.q.control({'id':'pause','expected_revision':0,'action':'pause'},authenticated_operator=True)
    monkeypatch.setattr(module,'request_broker',lambda *args:pytest.fail('paused work must not admit'))
    result=r.submit_research()
    assert result['paused'] and r.q.tick()=={'status':'PAUSED'}
    assert r.submit_research()['duplicate'] and r.q.status()['tasks'][0]['status']=='QUEUED'


def test_direct_task_runs_existing_pipeline_once_recovers_and_stays_private(prepared,monkeypatch):
    import orchestrator.report_delivery as delivery
    prepared.config.update(purpose='LIVE_APPROVED_HANDOVER',publication={'checkout':'fixed','permission_sha256':'c'*64})
    r=module.Runtime(prepared.config);broker=Broker()
    monkeypatch.setattr(module,'request_broker',broker)
    monkeypatch.setattr(delivery,'deliver',lambda *args,**kwargs:pytest.fail('research artifacts must remain private'))
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        result=r.submit_research();task=result['task']
        assert r.q.tick()['status']=='COMPLETE'
        r.bookkeeping();r.deliver_reports()
        assert [stage for op,stage in broker.calls if op=='model_stage']==['continuation','review','disposition']
        assert r.status()['report_delivery'][0]['status']=='PRIVATE_ONLY'
        assert r.submit_research()['duplicate'] is True
        assert r.q.tick()['status']=='WAITING_FOR_ELIGIBLE_WORK'
        # Lost derived pipeline/coordinator receipts recover from protected
        # original replies through the same existing campaign recovery path.
        folder=r.state/'tasks'/task/'campaign-workspace/campaigns/isles24-pilot/pipeline/hosted-original'
        (folder/'receipt.json').unlink();(r.state/(task+'-0.json')).unlink()
        r.q.db.execute("UPDATE tasks SET status='BLOCKED' WHERE id=?",(task,))
        r.recover();assert r.q.tick()['status']=='COMPLETE'
        assert json.loads((folder.parent/'hosted-recovery/recovery.json').read_text())['new_model_calls']==0
        assert len([op for op,stage in broker.calls if op=='model_stage'])==3


def test_changed_input_or_bound_request_refuses_before_models(prepared,monkeypatch):
    r=module.Runtime(prepared.config);result=r.submit_research()
    monkeypatch.setattr(module,'request_broker',lambda *args:pytest.fail('changed input must not reach broker'))
    prepared.evidence.write_bytes(encoded({'changed':'input'}))
    with pytest.raises(ValueError,match='RESEARCH_INPUT_BINDING_CHANGED'):r.submit_research()
    binding=json.loads(r.q.db.execute('SELECT binding FROM tasks WHERE id=?',(result['task'],)).fetchone()[0])
    with pytest.raises(ValueError,match='RESEARCH_INPUT_BINDING_CHANGED'):r.admit(binding)
    r.config['research_request']['evidence_sha256']=hashlib.sha256(prepared.evidence.read_bytes()).hexdigest()
    with pytest.raises(ValueError,match='RESEARCH_REQUEST_IDENTITY_CONFLICT'):r.submit_research()
    with pytest.raises(ValueError,match='INSTALLED_RESEARCH_PACKET_CHANGED'):r.model(binding,0)
    assert len(r.q.status()['tasks'])==1


def test_existing_scientific_human_stop_still_blocks_the_shared_pipeline(prepared,monkeypatch):
    stopped=prepared.root/'campaigns/isles24-pilot/experiments/P001/lifecycle.jsonl'
    stopped.parent.mkdir(parents=True)
    stopped.write_bytes(encoded({'actor_type':'human','action':'STOP','experiment':'P001'}))
    stopped.chmod(0o600)
    subprocess.run(['git','-C',str(prepared.root),'add',str(stopped.relative_to(prepared.root))],check=True)
    r=module.Runtime(prepared.config);broker=Broker()
    monkeypatch.setattr(module,'request_broker',broker)
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        r.submit_research()
        assert r.q.tick()['status']=='BLOCKED'
    assert not [op for op,stage in broker.calls if op=='model_stage']
    assert json.loads(stopped.read_text())['action']=='STOP'


@pytest.mark.parametrize('fault',['world_file','group_write','world_parent','symlink'])
def test_research_input_requires_protected_private_file(prepared,fault):
    if fault=='world_file':prepared.evidence.chmod(0o644)
    elif fault=='group_write':prepared.evidence.chmod(0o660)
    elif fault=='world_parent':prepared.parent.chmod(0o755)
    else:
        other=prepared.evidence.with_name('other.json');prepared.evidence.rename(other)
        prepared.evidence.symlink_to(other)
    with pytest.raises(ValueError,match='REQUIRED'):module.Runtime(prepared.config)
    assert not Path(prepared.config['state']).exists()


def test_only_one_installed_bounded_route_and_attributed_request(prepared):
    assert task_contract(prepared.config['research_request']['task'])['experiment']=='P001'
    bad=copy.deepcopy(prepared.config)
    bad['research_request']['task']['mode']='code'
    with pytest.raises(ValueError,match='TASK_CONTRACT'):module.Runtime(bad)
    bad=copy.deepcopy(prepared.config);bad['campaign_preparation']={'mode':'discuss','request':'Legacy','trigger_job':'old'}
    with pytest.raises(ValueError,match='ONE_INSTALLED_CAMPAIGN'):module.Runtime(bad)
    bad=copy.deepcopy(prepared.config);bad['research_request']['initiator']={'kind':'human'}
    with pytest.raises(ValueError,match='CHANGE_HUMAN_IDENTITY_REQUIRED'):module.Runtime(bad)
    bad=copy.deepcopy(prepared.config);bad['research_request']['day']='invalid-input'
    with pytest.raises(ValueError,match='^INSTALLED_RESEARCH_INPUT_BINDING_REQUIRED$'):module.Runtime(bad)


def test_operator_transport_preserves_separate_installed_config(prepared,monkeypatch):
    import pwd
    monkeypatch.setattr(module.os,'getuid',lambda:0)
    monkeypatch.setattr(pwd,'getpwuid',lambda uid:SimpleNamespace(pw_name='research-controller'))
    def execute(command,**kwargs):
        assert command[0]=='/usr/sbin/runuser'
        assert command[-3:]==['--config','/etc/research-system/live-research/controller.json','submit-research']
        return SimpleNamespace(stdout=b'{"status":"QUEUED","model_calls":0}')
    monkeypatch.setattr(module.subprocess,'run',execute)
    result=module.controller_command(prepared.config,'submit-research','/etc/research-system/live-research/controller.json')
    assert result['model_calls']==0
    with pytest.raises(ValueError,match='OPERATOR_CONTROL_TRANSPORT_REQUIRED'):
        module.controller_command(prepared.config,'arbitrary-command')
