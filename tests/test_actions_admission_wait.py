import json
import pytest
from orchestrator.dispatch_limiter import initial
from orchestrator.actions_admission_wait import prepare,observe,wait


def record():
    return {'repository_id':1323461276,'run_id':'123','attempt':'2',
            'source':'a'*40,'branch':'main','workflow_sha256':'b'*64}


def test_checked_request_is_not_admission(tmp_path):
    path=tmp_path/'request'
    result=prepare(record(),path)
    assert result['status']=='REQUESTED_NOT_ADMITTED'
    assert json.loads((path/'admission.json').read_text())==record()
    with pytest.raises(ValueError,match='FRESH'):prepare(record(),path)


def test_previously_admitted_attempt_survives_halt_but_wrong_source_refuses():
    state=initial();state['policy_sha256']='c'*64;state['halted']=True
    assert observe(record(),state,'c'*64)['status']=='HALTED_OPERATOR_RESET_REQUIRED'
    state['events']['123:2']={'source':'a'*40,'branch':'main','day':'2026-09-07',
                            'count':96,'notification':'2N','halted':True}
    assert observe(record(),state,'c'*64)['status']=='ADMITTED'
    with pytest.raises(ValueError,match='BINDING_CHANGED'):
        observe({**record(),'source':'d'*40},state,'c'*64)


def test_timeout_cannot_admit_and_policy_drift_stops():
    state=initial();state['policy_sha256']='c'*64;now=[0]
    result=wait(record(),lambda:('a'*40,state),'c'*64,timeout=60,
                clock=lambda:now[0],sleep=lambda seconds:now.__setitem__(0,now[0]+seconds))
    assert result=={'status':'BLOCKED','reason':'ADMISSION_WAIT_TIMEOUT'}
    with pytest.raises(ValueError,match='POLICY_BINDING_CHANGED'):
        observe(record(),state,'d'*64)


def test_human_cli_prepares_same_checked_artifact(tmp_path,monkeypatch,capsys):
    import sys
    from orchestrator.actions_admission_wait import main
    request=tmp_path/'record.json';request.write_text(json.dumps(record()))
    monkeypatch.setattr(sys,'argv',['actions_admission_wait','prepare','--record',str(request),'--output',str(tmp_path/'artifact')])
    assert main()==0
    assert json.loads(capsys.readouterr().out)['status']=='REQUESTED_NOT_ADMITTED'
    assert json.loads((tmp_path/'artifact/admission.json').read_text())==record()


def test_proposed_policy_preserves_existing_controls_without_claiming_admission(tmp_path):
    from orchestrator.actions_admission_wait import workflow_prepare
    result=workflow_prepare({'status':'PROPOSED'}, {},tmp_path,tmp_path/'artifact')
    assert result=={'status':'PROPOSED_NOT_ACTIVE','active':False,'standing_dispatch_grant':False}
    assert not (tmp_path/'artifact').exists()


def test_workflow_request_binds_caller_not_reusable_workflow(tmp_path,monkeypatch):
    from orchestrator.actions_admission_wait import workflow_prepare
    from test_dispatch_limiter import config
    import orchestrator.remote_supervisor as module
    monkeypatch.setattr(module,'checked_source',lambda root,source:root)
    directory=tmp_path/'.github/workflows';directory.mkdir(parents=True)
    (directory/'confer.yml').write_text('name: Synthetic caller\n')
    env={'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':'Moroseui/concept-research-scout',
         'GITHUB_REF_NAME':'main','GITHUB_WORKFLOW_REF':'Moroseui/concept-research-scout/.github/workflows/confer.yml@refs/heads/main',
         'GITHUB_SHA':'a'*40,'GITHUB_RUN_ID':'123','GITHUB_RUN_ATTEMPT':'2'}
    result=workflow_prepare(config(48),env,tmp_path,tmp_path/'artifact')
    assert result['active'] is True
    actual=json.loads((tmp_path/'artifact/admission.json').read_text())
    import hashlib
    assert actual['workflow_sha256']==hashlib.sha256((directory/'confer.yml').read_bytes()).hexdigest()
    with pytest.raises(ValueError,match='CALLER_WORKFLOW_BINDING'):
        workflow_prepare(config(48),{**env,'GITHUB_REF_NAME':'unbound'},tmp_path,tmp_path/'other')
