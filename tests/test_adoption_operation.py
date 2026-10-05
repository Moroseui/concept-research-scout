"""Saved H2 adoption lifecycle; simulated model outcomes are not real authority."""
import json
from pathlib import Path
import pytest
from orchestrator import continuing_operations as ops, scientific_adoption as adopt
from orchestrator.hosted_cycle import encoded
from test_continuing_operations import fixture


def selected(fixture, monkeypatch):
    runtime, choice, packet, selector = fixture
    from copy import deepcopy
    import hashlib
    native_selection = ops._selection
    _, parent_packet, predecessor, by, change = native_selection(runtime, selector)
    parent_selector = {**selector,'task':'8'*64}
    parent_operation = {'schema':ops.SCHEMA,'operation_id':'accepted-fixture',
        'kind':'ACCEPT_RESULT','inputs':{'interpretation':
            {'task':'9'*64,'artifact':'round-1/interpretation.md','sha256':'a'*64}}}
    # Preserve the selecting predecessor's own original context. The successor
    # below mutates packet; it must not retroactively replace these references.
    parent_packet = deepcopy(parent_packet)
    parent_packet['campaign_task']['references'] = [parent_operation['inputs']['interpretation']]
    core = {'source':runtime.config['source'],'operation':parent_operation,'selected_by':parent_selector,
        'predecessor':predecessor,'actor':by,'change_request':change}
    identity = ops.digest(core)
    folder = ops.private_root(ops.private_root(ops._directory(runtime.config))/identity)
    (folder/'request.json').write_bytes(encoded({**core,'identity':identity,'created_at_utc':'fixture'}))
    result = {'schema':ops.RESULT_SCHEMA,'operation':identity,'source':runtime.config['source'],
        'kind':'ACCEPT_RESULT','status':'COMPLETE','scientific_acceptance':True,'result':{'fixture':True}}
    (folder/'result.json').write_bytes(encoded(result))
    (folder/'step-1.json').write_bytes(encoded({'result':result['result']}))
    acceptance = {'operation':identity,'result_sha256':hashlib.sha256(encoded(result)).hexdigest()}
    parent_choice = {**deepcopy(choice),'successor':parent_operation}
    def selecting(actual,ref):
        if ref == parent_selector:
            return parent_choice,parent_packet,predecessor,by,change
        return native_selection(actual,ref)
    monkeypatch.setattr(ops,'_selection',selecting)
    selection = {'task':'f'*64,'artifact':'round-1/selection.json','sha256':'1'*64}
    choice['successor'] = {'schema':ops.SCHEMA,'operation_id':'adopt-fixture','kind':'ADOPT_FOLLOWUP',
        'inputs':{'acceptance':acceptance,'selection':selection}}
    packet['campaign_task']['references'] = [selection]
    packet['continuing_context'] = {'continuing_operations':{'completed':[{'reference':acceptance}]}}
    native = ops.read_operation_result;reads = []
    def checked(config,ref,**kwargs):
        if ref == acceptance: reads.append(ref)
        return native(config,ref,**kwargs)
    monkeypatch.setattr(ops,'read_operation_result',checked)
    return runtime,choice,packet,selector,reads


def applied():
    return {'status':adopt.STATUS,'adoption':True,'execution_authorized':False,
            'model_calls':0,'duplicate':False}


def test_both_observed_bindings_required_and_renaming_does_not_repeat(fixture, monkeypatch):
    runtime,choice,packet,selector,reads = selected(fixture,monkeypatch)
    observed = packet['continuing_context']
    packet['continuing_context'] = {}
    with pytest.raises(ValueError,match='RESULT_NOT_IN_ORIGINAL_CONTEXT'):
        ops.enqueue(runtime,selector)
    packet['continuing_context'] = observed
    packet['campaign_task']['references'] = []
    with pytest.raises(ValueError,match='NOT_IN_INVESTIGATOR_CONTEXT'):
        ops.enqueue(runtime,selector)
    packet['campaign_task']['references'] = [choice['successor']['inputs']['selection']]
    first = ops.enqueue(runtime,selector)
    choice['successor']['operation_id'] = 'renamed-same-adoption'
    second = ops.enqueue(runtime,selector)
    assert first['operation'] == second['operation'] and second['duplicate']
    assert len([r for r in ops.status(runtime.config)['operations'] if r['kind']=='ADOPT_FOLLOWUP']) == 1
    assert reads


@pytest.mark.parametrize('defer',[False,True])
def test_reviewed_decision_then_adoption_or_durable_defer(fixture,monkeypatch,defer):
    runtime,choice,packet,selector,reads = selected(fixture,monkeypatch)
    identity = ops.enqueue(runtime,selector)['operation']; calls = []
    request = {'fixture':'exact-formal-adoption'}
    monkeypatch.setattr(ops,'_prepared',lambda *a:{'formal_request':request})
    monkeypatch.setattr(ops,'_client',lambda *a:None)
    def authority(config,actual,output,**kwargs):
        assert actual == request; calls.append('authority')
        return {'status':'AGENT_REVIEWED_DEFERRAL' if defer else 'AGENT_REVIEWED_DECISION_READY',
            'decision_path':str(output/'round-1/decision.json'),'new_model_calls':2}
    def application(config,acceptance,selection,actual,path,**kwargs):
        assert {'acceptance':acceptance,'selection':selection} == choice['successor']['inputs']
        assert actual == request;calls.append('application')
        return applied()
    monkeypatch.setattr('orchestrator.formal_decisions.execute_formal_decision',authority)
    monkeypatch.setattr(adopt,'apply',application)
    result = ops.advance(runtime)
    if defer:
        assert result['status'] == 'DEFERRED'
    else:
        assert result['status'] == 'STEP_COMPLETE'
        result = ops.advance(runtime)
        assert result['status'] == 'COMPLETE' and result['result']['adoption'] is True
        ref = next(r['reference'] for r in ops.status(runtime.config)['completed'] if r['kind']=='ADOPT_FOLLOWUP')
        assert ops.read_operation_result(runtime.config,ref,kinds=('ADOPT_FOLLOWUP',)) == result
    assert result['scientific_acceptance'] is False
    for _ in range(2): assert ops.advance(runtime)['status'] == 'AWAITING_REVIEWED_SELECTION'
    assert calls == (['authority'] if defer else ['authority','application'])


def test_interrupted_adoption_recovers_originals_without_authority_call(fixture,monkeypatch):
    runtime,choice,packet,selector,reads = selected(fixture,monkeypatch)
    identity = ops.enqueue(runtime,selector)['operation'];folder = ops._directory(runtime.config)/identity
    request = {'fixture':'original-adoption'}
    path = str(Path(runtime.config['state'])/'formal-decisions'/identity/'round-1/decision.json')
    (folder/'prepared.json').write_bytes(encoded({'formal_request':request}))
    (folder/'step-0.json').write_bytes(encoded({'result':{'decision_path':path}}))
    (folder/'started-1.json').write_bytes(encoded({'fixture':'interrupted'}))
    calls = []; monkeypatch.setattr(ops,'_client',lambda *a:None)
    def application(config,acceptance,selection,actual,decision,**kwargs):
        assert kwargs['recover'] is True and decision == path and actual == request
        assert {'acceptance':acceptance,'selection':selection} == choice['successor']['inputs']
        calls.append('original-only')
        return {**applied(),'duplicate':True}
    monkeypatch.setattr(adopt,'apply',application)
    monkeypatch.setattr('orchestrator.formal_decisions.execute_formal_decision',
        lambda *a,**k:pytest.fail('Adoption recovery must not repeat formal authority'))
    runtime.q.status = lambda:{'paused':True}
    assert ops.recover(runtime,identity)['status'] == 'PAUSED' and not calls
    runtime.q.status = lambda:{'paused':False}
    assert ops.recover(runtime,identity)['status'] == 'COMPLETE'
    assert ops.recover(runtime,identity)['models'] == 0 and calls == ['original-only']
    assert json.loads((folder/'recovery-1.json').read_text())['kind'] == 'ORIGINAL_ADOPTION_APPLICATION_RECONCILED'


def test_uncertain_authority_can_only_read_existing_stage_replies(fixture,monkeypatch):
    runtime,choice,packet,selector,reads = selected(fixture,monkeypatch)
    identity = ops.enqueue(runtime,selector)['operation'];folder = ops._directory(runtime.config)/identity
    (folder/'prepared.json').write_bytes(encoded({'formal_request':{'fixture':True}}))
    (folder/'started-0.json').write_bytes(encoded({'fixture':'uncertain'}))
    monkeypatch.setattr(ops,'_client',lambda *a:lambda socket,operation,body:{'status':'original'})
    def recover(config,request,output,*,recover_from,client):
        with pytest.raises(ValueError,match='FORBIDS_NEW_ADMISSION_OR_MODEL'):client('','model_stage',{})
        assert client('','stage_status',{}) == {'status':'original'}
        return {'status':'AGENT_REVIEWED_DEFERRAL','new_model_calls':0}
    monkeypatch.setattr('orchestrator.formal_decisions.execute_formal_decision',recover)
    result = ops.recover(runtime,identity)
    assert result['status'] == 'DEFERRED' and result['scientific_acceptance'] is False


@pytest.mark.parametrize('mutation',[{'adoption':False},{'execution_authorized':True},{'model_calls':1}])
def test_completion_cannot_smuggle_execution_or_replace_adoption_with_label(tmp_path,mutation):
    saved = {'operation':{'kind':'ADOPT_FOLLOWUP'},'identity':'a'*64,'source':'b'*40}
    with pytest.raises(ValueError,match='ADOPTION_APPLICATION_REQUIRED'):
        ops._finalize(saved,tmp_path,{**applied(),**mutation})
    assert not (tmp_path/'result.json').exists()
