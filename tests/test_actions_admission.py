import hashlib,io,json,zipfile
import pytest
from orchestrator.actions_admission import verify


def fixture():
    workflow=b'name: synthetic admission\n'
    expected={'run_id':'123','attempt':'2','source':'a'*40,'branch':'main',
              'workflow_path':'.github/workflows/research-control.yml',
              'workflow_sha256':hashlib.sha256(workflow).hexdigest()}
    run={'repository':{'id':1323461276},'id':123,'run_attempt':2,'head_sha':'a'*40,
         'head_branch':'main','path':expected['workflow_path'],'event':'workflow_dispatch'}
    artifact={'name':'research-admission-123-2','expired':False,'workflow_run':{'id':123},'size_in_bytes':400}
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w') as z:
        z.writestr('admission.json',json.dumps({'repository_id':1323461276,**{k:expected[k] for k in ('run_id','attempt','source','branch','workflow_sha256')}}))
    return run,artifact,output.getvalue(),workflow,expected


def test_actual_identity_fields_and_replay_binding():
    args=fixture();assert verify(*args)['attempt']=='2'
    assert verify(*args)==verify(*args)
    for field,value in [('run_attempt',3),('head_sha','b'*40),('head_branch','unbound'),('event','pull_request')]:
        run={**args[0],field:value}
        with pytest.raises(ValueError,match='RUN_BINDING'):verify(run,*args[1:])
    with pytest.raises(ValueError,match='WORKFLOW_CHANGED'):verify(*args[:3],b'changed',args[4])


def test_extra_archive_members_and_cross_run_artifact_refused():
    args=fixture();out=io.BytesIO(args[2])
    with zipfile.ZipFile(out,'a') as z:z.writestr('extra.txt','unexpected')
    with pytest.raises(ValueError,match='MEMBERS'):verify(*args[:2],out.getvalue(),*args[3:])
    with pytest.raises(ValueError,match='ARTIFACT_BINDING'):verify(args[0],{**args[1],'workflow_run':{'id':456}},*args[2:])



def test_malformed_archive_is_a_named_recoverable_refusal():
    args=fixture()
    with pytest.raises(ValueError,match='ACTIONS_ARCHIVE_INVALID'):
        verify(*args[:2],b'not a zip archive',*args[3:])
