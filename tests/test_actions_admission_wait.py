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
