"""Original-selection -> adoption -> eligibility/registration connection.

All model responses and authorities below are fixtures; no live admission occurs.
The adoption fixture verifies native original selection and acceptance readers.
"""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import hashlib
import json

import pytest
from orchestrator import scientific_adoption as adopt
from orchestrator import continuing_operations as ops, continuing_research as continuing
from orchestrator import investigator_wakes as wakes
from orchestrator.hosted_cycle import encoded
from test_scientific_acceptance import prepared
from test_scientific_adoption import adoption
from test_semantic_validation_contract import checked_import, validation_import

NATIVE_OPERATION_READER = wakes._operation


@pytest.fixture
def applied(adoption, monkeypatch):
    a = adoption
    result = adopt.apply(a.p.config, a.acceptance, a.selection, a.request, a.path,
                         original_client=a.client, by=a.p.by)
    ref = {'operation': '6'*64, 'result_sha256': '7'*64}
    original = wakes._operation
    def native(config, actual, client):
        if actual == ref:
            checked = adopt.read_application(config, a.acceptance, a.selection, a.request, a.path,
                                               original_client=client, by=a.p.by)
            return {'operation': {'kind': 'ADOPT_FOLLOWUP', 'result': checked}}
        return original(config, actual, client)
    monkeypatch.setattr(wakes, '_operation', native)
    runtime = SimpleNamespace(config=a.p.config)
    monkeypatch.setattr(ops, '_client', lambda runtime: a.client)
    return SimpleNamespace(a=a, ref=ref, result=result, runtime=runtime)


def test_actual_discovery_derivation_requires_adoption_before_authority(adoption, monkeypatch):
    a=adoption
    runtime=SimpleNamespace(config=a.p.config)
    monkeypatch.setattr(ops, '_client', lambda runtime:a.client)
    first=ops._derived_operation(runtime,a.selected,a.packet,a.selection)
    assert first['kind']=='ADOPT_FOLLOWUP'
    assert first['inputs']=={'acceptance':a.acceptance,'selection':a.selection}
    assert ops._derived_operation(runtime,a.selected,a.packet,a.selection)==first
    assert first['operation_id'] != a.selected['successor']['task_id']
    assert not (Path(a.p.config['state'])/'scientific-adoptions').exists()
    # Missing the declared relation is not a way to authorize the same accepted evidence.
    changed=deepcopy(a.selected);changed['successor'].pop('accepted_result')
    with pytest.raises(ValueError,match='EXACT_ACCEPTED_RESULT_DEPENDENCY'):
        ops._derived_operation(runtime,changed,a.packet,a.selection)


def test_unrelated_pre_result_analysis_keeps_existing_route(adoption, monkeypatch):
    a=adoption;selected=deepcopy(a.selected)
    selected['successor'].pop('accepted_result');selected['successor']['references']=[]
    runtime=SimpleNamespace(config=a.p.config)
    monkeypatch.setattr(ops,'_client',lambda runtime:a.client)
    value=ops._derived_operation(runtime,selected,a.packet,a.selection)
    assert value['kind']=='AUTHORIZE_TASK' and set(value['inputs'])=={'selection'}


@pytest.mark.parametrize('damage',['missing-context','changed-acceptance','missing-interpretation'])
def test_declared_dependency_cannot_be_an_unobserved_digest(adoption,damage):
    a=adoption;task=deepcopy(a.selected['successor']);packet=deepcopy(a.packet)
    if damage=='missing-context':packet['continuing_context']['continuing_operations']['completed']=[]
    elif damage=='changed-acceptance':task['accepted_result']['result_sha256']='9'*64
    else:task['references']=[]
    with pytest.raises(ValueError,match='EXACT_ACCEPTED_RESULT_DEPENDENCY'):
        adopt.accepted_dependency(a.p.config,task,packet,original_client=a.client)


def test_explicit_authority_must_consume_exact_later_adoption(applied,monkeypatch):
    x=applied;a=x.a
    operation={'schema':ops.SCHEMA,'operation_id':'fixture-authorize-adopted',
        'kind':'AUTHORIZE_TASK','inputs':{'selection':a.selection,'adoption':x.ref}}
    current={'campaign_task':{'mode':'investigate','references':[a.selection]}}
    monkeypatch.setattr(ops,'_selection',lambda runtime,ref:
        (a.selected,a.packet,{},a.p.by,{}))
    chosen={'successor':operation}
    result=ops._derived_operation(x.runtime,chosen,current,{'task':'8'*64,'artifact':'round-1/selection.json','sha256':'9'*64})
    assert result==operation
    assert 'adoption' not in a.packet['continuing_context']['continuing_operations']['completed'][0]
    plain=deepcopy(chosen);plain['successor']['inputs'].pop('adoption')
    with pytest.raises(ValueError,match='APPLIED_ADOPTION_REQUIRED'):
        ops._derived_operation(x.runtime,plain,current,a.selection)


@pytest.mark.parametrize('damage',['task','protocol','selection','source','completion','defer','missing-application'])
def test_current_native_adoption_changes_refuse_before_dependent_use(applied,monkeypatch,damage):
    x=applied;a=x.a;task=deepcopy(a.selected['successor']);selection=deepcopy(a.selection)
    if damage=='task':task['request']+=' changed'
    elif damage=='protocol':task['protocol']['decision_sha256']='8'*64
    elif damage=='selection':selection['sha256']='8'*64
    elif damage=='source':
        changed=deepcopy(x.result);changed['source']='8'*40
        monkeypatch.setattr(wakes,'_operation',lambda cfg,ref,client:
            {'operation':{'kind':'ADOPT_FOLLOWUP','result':changed}} if ref==x.ref else a.accepted_operation(cfg,ref,client))
    elif damage=='completion':
        # Preserve the forged marker; native acceptance revalidation must reject it.
        target=next((Path(a.p.config['state'])/'scientific-adoptions').rglob('application.json'))
        value=json.loads(target.read_bytes());value['compatibility']['accepted_completion']='8'*64
        target.write_bytes(encoded(value))
    elif damage=='defer':a.proof['decision']='DEFER'
    else:next((Path(a.p.config['state'])/'scientific-adoptions').rglob('application.json')).unlink()
    with pytest.raises((ValueError,FileNotFoundError)):
        adopt.require_applied(a.p.config,task,a.packet,selection,x.ref,original_client=a.client)


def test_registration_reads_same_saved_operation_and_original_selection(applied):
    x=applied;a=x.a
    operation={'schema':ops.SCHEMA,'operation_id':'fixture-authorize-adopted',
        'kind':'AUTHORIZE_TASK','inputs':{'selection':a.selection,'adoption':x.ref}}
    core={'source':a.p.config['source'],'operation':operation,'selected_by':a.selection,
          'predecessor':{},'actor':a.p.by,'change_request':a.p.request['change_request']}
    identity=ops.digest(core)
    saved={**core,'identity':identity,'created_at_utc':'2026-09-19T21:00:00+00:00'}
    folder=ops._directory(a.p.config)/identity;folder.mkdir(parents=True)
    (folder/'request.json').write_bytes(encoded(saved))
    task=deepcopy(a.selected['successor']);task['selected_by']=a.selection
    Path(a.p.config['state']).chmod(0o700)
    proof=continuing.preserve_evidence(a.p.config,{'selected_operation':saved})
    entry={'request':{'task':task,**proof}}
    before=(a.folder/'packet.json').read_bytes()
    first=adopt.require_registration(a.p.config,entry,original_client=a.client)
    assert first['reference']==x.ref
    assert adopt.require_registration(a.p.config,entry,original_client=a.client)==first
    assert (a.folder/'packet.json').read_bytes()==before
    forged=deepcopy(saved);forged['operation']['inputs'].pop('adoption')
    changed=continuing.preserve_evidence(a.p.config,{'selected_operation':forged})
    with pytest.raises(ValueError,match='ORIGINAL_AUTHORITY_OPERATION_CHANGED'):
        adopt.require_registration(a.p.config,{'request':{'task':task,**changed}},original_client=a.client)


def test_native_protected_registration_uses_original_read_pipe_for_adopted_task(applied,monkeypatch,tmp_path):
    from orchestrator import handover_runtime, research_catalog, protected_investigator
    x=applied;a=x.a
    task=deepcopy(a.selected['successor']);task['selected_by']=a.selection
    entry={'request':{'task':task}}
    config={**a.p.config,'controller_uid':997,'controller_gid':997,
            'research_catalog':{'directory':str(tmp_path/'catalog')}}
    broker=SimpleNamespace(config={'research_controller_config':'/etc/fixture/controller.json',
                                  'controller_uid':997,'sources':[config['source']]})
    monkeypatch.setattr(continuing.os,'getuid',lambda:0)
    monkeypatch.setattr(handover_runtime,'configuration',lambda p:config)
    monkeypatch.setattr(research_catalog,'validate_entry',lambda *a:None)
    monkeypatch.setattr(research_catalog,'paths',lambda *a:{})
    calls=[]
    def verify(actual,cfg,mode,value):
        assert actual is broker and cfg is config and mode=='entry' and value==entry
        calls.append(mode)
        return {'status':'VERIFIED_SUCCESSOR','entry_sha256':continuing.digest(entry)}
    monkeypatch.setattr(protected_investigator,'verify_subprocess',verify)
    monkeypatch.setattr(continuing,'_install_entry',lambda cfg,value,receipt:{'fixture':'installed','receipt':receipt})
    assert continuing.protected_register(broker,{'entry':entry})['fixture']=='installed'
    assert calls==['entry']


def test_enqueue_saves_one_adoption_operation_and_reuses_it(adoption,monkeypatch):
    a=adoption
    config={**a.p.config,'continuing_operations':{'enabled':True}}
    runtime=SimpleNamespace(config=config)
    monkeypatch.setattr(ops,'_client',lambda runtime:a.client)
    monkeypatch.setattr(ops,'_selection',lambda runtime,ref:
        (a.selected,a.packet,{'task':a.selection['task']},a.p.by,a.p.request['change_request']))
    # Acceptance is still checked by the native fixture original reader.
    # _observed_inputs additionally requires the unchanged completed-result row.
    native_read=ops.read_operation_result
    monkeypatch.setattr(ops,'read_operation_result',lambda cfg,ref,**kw:
        {'kind':'ACCEPT_RESULT'} if ref==a.acceptance and kw.get('kinds')==('ACCEPT_RESULT',) else native_read(cfg,ref,**kw))
    ops._directory(config).chmod(0o700)
    first=ops.enqueue(runtime,a.selection)
    again=ops.enqueue(runtime,a.selection)
    assert first['operation']==again['operation'] and again['duplicate'] is True
    saved=ops._saved(ops._directory(config)/first['operation'])
    assert saved['operation']['kind']=='ADOPT_FOLLOWUP'
    assert saved['operation']['inputs']=={'acceptance':a.acceptance,'selection':a.selection}
    assert first['models']==again['models']==first['admissions']==again['admissions']==0
    assert not (Path(config['state'])/'scientific-adoptions').exists()


def test_native_operation_reader_reconstructs_derived_adoption_for_recovery(applied,monkeypatch):
    x=applied;a=x.a
    operation=adopt.selected_operation(a.p.config,a.selected['successor'],a.packet,a.selection,
                                       original_client=a.client)
    saved={'source':a.p.config['source'],'operation':operation,'selected_by':a.selection,
           'actor':a.p.by}
    result={'kind':'ADOPT_FOLLOWUP','result':x.result}
    # Preserve the native _task / selection / original application checks; only
    # the already-tested outer operation storage wrapper is supplied as fixture.
    monkeypatch.setattr(ops,'_saved',lambda folder:deepcopy(saved))
    prior=ops.read_operation_result
    monkeypatch.setattr(ops,'read_operation_result',lambda config,ref,**kw:
        deepcopy(result) if ref==x.ref else prior(config,ref,**kw))
    folder=ops._directory(a.p.config)/x.ref['operation'];folder.mkdir(parents=True)
    (folder/'prepared.json').write_bytes(encoded({'formal_request':a.request}))
    read=NATIVE_OPERATION_READER(a.p.config,x.ref,a.client)
    assert read['operation']['kind']=='ADOPT_FOLLOWUP'
    assert read['operation']['result']['adoption'] is True
    saved['operation']['inputs']['selection']['sha256']='9'*64
    with pytest.raises(ValueError):
        NATIVE_OPERATION_READER(a.p.config,x.ref,a.client)
