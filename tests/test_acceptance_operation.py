"""Saved acceptance steps and recovery; model/application effects are fixtures."""
import json
from pathlib import Path
import pytest
from orchestrator import continuing_operations as ops, scientific_acceptance as accept
from orchestrator.hosted_cycle import encoded
from test_continuing_operations import fixture


def selected(fixture):
    runtime,choice,packet,selector=fixture
    interpretation={'task':'f'*64,'artifact':'round-1/interpretation.md','sha256':'1'*64}
    choice['successor']={'schema':ops.SCHEMA,'operation_id':'accept-fixture','kind':'ACCEPT_RESULT',
                         'inputs':{'interpretation':interpretation}}
    packet['campaign_task']['references']=[interpretation]
    return runtime,choice,packet,selector


def test_bound_observed_interpretation_required_and_duplicate_label_does_not_recharge(fixture):
    runtime,choice,packet,selector=selected(fixture)
    packet['campaign_task']['references']=[]
    with pytest.raises(ValueError,match='NOT_IN_INVESTIGATOR_CONTEXT'):ops.enqueue(runtime,selector)
    packet['campaign_task']['references']=[choice['successor']['inputs']['interpretation']]
    first=ops.enqueue(runtime,selector)
    choice['successor']['operation_id']='different-label'
    second=ops.enqueue(runtime,selector)
    assert first['operation']==second['operation'] and second['duplicate']
    assert len(ops.status(runtime.config)['operations'])==1
    choice['successor']['inputs']['execute']=True
    with pytest.raises(ValueError,match='FIXED_OPERATION_INPUTS'):ops.contract(choice['successor'])


@pytest.mark.parametrize('defer',[False,True])
def test_saved_authority_then_application_or_persistent_defer(fixture,monkeypatch,defer):
    runtime,choice,packet,selector=selected(fixture)
    identity=ops.enqueue(runtime,selector)['operation'];calls=[]
    request={'bindings':{},'fixture':True}
    monkeypatch.setattr(ops,'_prepared',lambda *a:{'formal_request':request})
    monkeypatch.setattr(ops,'_client',lambda *a:None)
    def authority(config,actual,output,**kw):
        assert actual==request;calls.append('authority')
        return {'status':'AGENT_REVIEWED_DEFERRAL' if defer else 'AGENT_REVIEWED_DECISION_READY',
                'decision_path':str(output/'round-1/decision.json'),'new_model_calls':2}
    def application(config,ref,actual,path,**kw):
        assert ref==choice['successor']['inputs']['interpretation']
        assert actual==request;calls.append('application')
        return {'status':accept.STATUS,'scientific_acceptance':True,'adoption':False,
                'execution_authorized':False,'model_calls':0,'duplicate':False}
    monkeypatch.setattr('orchestrator.formal_decisions.execute_formal_decision',authority)
    monkeypatch.setattr(accept,'apply',application)
    result=ops.advance(runtime)
    if defer:
        assert result['status']=='DEFERRED' and result['scientific_acceptance'] is False
    else:
        assert result['status']=='STEP_COMPLETE'
        result=ops.advance(runtime)
        assert result['status']=='COMPLETE' and result['scientific_acceptance'] is True
        ref=ops.status(runtime.config)['completed'][0]['reference']
        assert ops.read_operation_result(runtime.config,ref,kinds=('ACCEPT_RESULT',))==result
    for _ in range(2):assert ops.advance(runtime)['status']=='AWAITING_REVIEWED_SELECTION'
    assert calls==(['authority'] if defer else ['authority','application'])


def test_explicit_application_recovery_never_repeats_authority(fixture,monkeypatch):
    runtime,choice,packet,selector=selected(fixture)
    identity=ops.enqueue(runtime,selector)['operation'];folder=ops._directory(runtime.config)/identity
    request={'bindings':{}}
    (folder/'prepared.json').write_bytes(encoded({'formal_request':request}))
    path=str(Path(runtime.config['state'])/'formal-decisions'/identity/'round-1/decision.json')
    (folder/'step-0.json').write_bytes(encoded({'result':{'decision_path':path}}))
    (folder/'started-1.json').write_bytes(encoded({'fixture':'interrupted'}))
    calls=[]
    monkeypatch.setattr(ops,'_client',lambda *a:None)
    def apply(config,ref,actual,decision,**kw):
        assert kw['recover'] is True and decision==path;calls.append('original-only-apply')
        return {'status':accept.STATUS,'scientific_acceptance':True,'adoption':False,'execution_authorized':False,'model_calls':0,'duplicate':True}
    monkeypatch.setattr(accept,'apply',apply)
    monkeypatch.setattr('orchestrator.formal_decisions.execute_formal_decision',
        lambda *a,**k:pytest.fail('Recovery cannot repeat the authority call'))
    runtime.q.status=lambda:{'paused':True}
    assert ops.recover(runtime,identity)['status']=='PAUSED' and calls==[]
    runtime.q.status=lambda:{'paused':False}
    assert ops.recover(runtime,identity)['status']=='COMPLETE'
    assert ops.recover(runtime,identity)['models']==0 and calls==['original-only-apply']
    assert (folder/'recovery-1.json').is_file()


def test_formal_recovery_is_enabled_for_acceptance_without_model_submission(fixture,monkeypatch):
    runtime,choice,packet,selector=selected(fixture)
    identity=ops.enqueue(runtime,selector)['operation'];folder=ops._directory(runtime.config)/identity
    (folder/'prepared.json').write_bytes(encoded({'formal_request':{'fixture':True}}))
    (folder/'started-0.json').write_bytes(encoded({'fixture':'uncertain authority'}))
    monkeypatch.setattr(ops,'_client',lambda *a:lambda socket,operation,body:{'status':'original'})
    def original(config,request,output,*,recover_from,client):
        with pytest.raises(ValueError,match='FORBIDS_NEW_ADMISSION_OR_MODEL'):client('', 'model_stage',{})
        assert client('', 'stage_status',{})=={'status':'original'}
        return {'status':'AGENT_REVIEWED_DEFERRAL','new_model_calls':0}
    monkeypatch.setattr('orchestrator.formal_decisions.execute_formal_decision',original)
    value=ops.recover(runtime,identity)
    assert value['status']=='DEFERRED' and value['scientific_acceptance'] is False
