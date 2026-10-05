"""Actual pipeline consumption of bounded validation evidence; no real science."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from orchestrator import continuing_research as c, scientific_job_results as results
from orchestrator import continuing_operations as ops
from orchestrator.hosted_cycle import encoded
from orchestrator.hosted_campaign import BrokerStages, run_pipeline, recover_projection
from orchestrator.hosted_campaign_task import completed_pipeline, task_contract
from test_prospective_interpretation import fixture
from test_semantic_validation_contract import checked_import, validation_import
from test_hosted_campaign import client_for


def setup(validation_import, monkeypatch, status='DEFER'):
    config, completion, client, by, response, calls = validation_import
    output = json.loads(response['output']); output['status'] = status
    output['reason'] = 'Distinct validator explanation: ' + status
    response['output'] = json.dumps(output) + '\n'
    receipt = results.import_semantic_validation(config, completion=completion, original_client=client, by=by)
    imported = results.import_result(config, completion=completion, original_client=client, by=by)
    task = fixture()[0]
    task['semantic_validation'] = {'operation': '3'*64, 'result_sha256': '4'*64}
    observed = []
    def saved(cfg, ref, *, kinds, current_review=True):
        observed.append((ref, kinds, current_review))
        if ref == task['semantic_validation']:
            assert kinds == ('VALIDATE_RESULT',)
            return {'result': receipt}
        assert ref == task['import_result'] and kinds == ('IMPORT_RESULT',)
        return {'result': imported}
    monkeypatch.setattr(ops, 'read_operation_result', saved)
    monkeypatch.setattr(c, 'read_protocol', lambda *a, **k: {
        'descriptor': task['protocol'], 'decision': {'decision': 'APPLY', '_decision_sha256': 'd'*64}})
    monkeypatch.setattr(c, 'require_code_inputs', lambda *a: None)
    calls.clear()
    return config, task, client, response, calls, observed


@pytest.mark.parametrize('status', ['VALID', 'INVALID', 'DEFER'])
def test_actual_interpretation_author_reviewer_and_recovery_receive_validation(
        validation_import, monkeypatch, tmp_path, status):
    config, task, reader, response, reads, observed = setup(validation_import, monkeypatch, status)
    supplement = c.supplemental_context(config, task, original_client=reader)
    assert reads == ['scientific_job_result', 'scientific_validation_result']
    c.checked_supplement(task, supplement)
    packet = {'campaign_task': task, 'campaign_artifacts': task_contract(task)}
    answers = [json.dumps({'interpretation.md': 'Fixture interpretation of validator '+status,
        'investigator_next_decision.json': json.dumps({'status':'PROPOSAL_ONLY','rationale':'Separate acceptance still required.'})}),
        json.dumps({'review.json': json.dumps({'verdict':'APPROVE','rationale':'Fixture opposing interpretation review only.'})})]
    provider, calls = client_for(answers); originals = {}; prompts = []
    def client(socket, operation, body):
        prompts.append(body['prompt']); reply = provider(socket, operation, body)
        originals[body['stage']] = reply; return reply
    output = tmp_path/'campaigns/isles24-pilot/pipeline/semantic'
    with patch('orchestrator.campaign_pipeline.grounding', return_value={}), patch(
            'orchestrator.research_context.evidence_context', return_value={}):
        receipt = run_pipeline(SimpleNamespace(ROOT=tmp_path), 'interpret', task['request'], output,
            BrokerStages('fixture', {}, packet, client=client), supplement=supplement)
        completed_pipeline(tmp_path, output, packet, {}, supplement=supplement)
        assert receipt['acceptance_status'] == 'APPROVED_PROPOSAL_ONLY'
        before = {str(p):p.read_bytes() for p in output.rglob('*') if p.is_file()}
        def recover(socket, operation, body):
            assert operation == 'stage_status'
            return {**originals[body['stage']], 'duplicate':True}
        recover_projection(SimpleNamespace(ROOT=tmp_path), 'interpret', task['request'], output,
            output.parent/'recovered', BrokerStages('fixture', {}, packet, client=recover, recovery=True),
            supplement=supplement)
        assert before == {str(p):p.read_bytes() for p in output.rglob('*') if p.is_file()}
    assert len(calls) == 2
    for prompt in prompts:
        assert 'Distinct validator explanation: '+status in prompt
        assert 'none is automatic acceptance or adoption' in prompt
        assert 'Do not claim the generated return validator ran' not in prompt


@pytest.mark.parametrize('damage',['completion','status','output','acceptance','reference','boolean_alias','model_count_type'])
def test_changed_semantic_context_refuses_before_model(validation_import, monkeypatch, damage):
    config, task, reader, _, _, _ = setup(validation_import, monkeypatch)
    value = json.loads(c.supplemental_context(config,task,original_client=reader)['continuing-research-inputs.json'])
    v=value['semantic_validation']
    if damage=='completion':v['receipt']['completion']='9'*64
    if damage=='status':v['receipt']['validator_status']='VALID'
    if damage=='output':v['original']['output']+='\n'
    if damage=='acceptance':v['receipt']['scientific_acceptance']=True
    if damage=='reference':v['reference']['operation']='9'*64
    if damage=='boolean_alias':v['receipt']['scientific_acceptance']=0
    if damage=='model_count_type':v['receipt']['model_calls']=False
    with pytest.raises(ValueError):
        c.checked_supplement(task,{'continuing-research-inputs.json':json.dumps(value)})


def test_read_only_recovery_checks_same_original_and_missing_saved_bytes(validation_import, monkeypatch):
    config,task,reader,response,reads,observed=setup(validation_import,monkeypatch)
    c.supplemental_context(config,task,original_client=reader,read_only=True)
    assert reads==['scientific_job_result','scientific_validation_result']
    assert [x[2] for x in observed]==[False,False]
    f=Path(config['state'])/'scientific-results'/response['binding']['completion']/'semantic-validation/validator-output.json'
    f.write_text('changed')
    with pytest.raises(ValueError,match='SAVED_VALIDATION_CHANGED'):
        c.supplemental_context(config,task,original_client=reader,read_only=True)


def test_typed_validation_requires_interpretation_and_import():
    task=fixture()[0];task['semantic_validation']={'operation':'3'*64,'result_sha256':'4'*64}
    assert c.task_contract(task)
    bad=deepcopy(task);bad['mode']='discuss'
    with pytest.raises(ValueError,match='REQUIRES_RESULT_INTERPRETATION'):c.task_contract(bad)
    bad=deepcopy(task);del bad['import_result']
    with pytest.raises(ValueError):c.task_contract(bad)


def test_selection_must_have_observed_validation_before_authorizing_task(monkeypatch):
    task=fixture()[0];task['semantic_validation']={'operation':'3'*64,'result_sha256':'4'*64}
    operation={'kind':'AUTHORIZE_TASK','inputs':{}}
    packet={'continuing_context':{'continuing_operations':{'completed':[{'reference':task['import_result']}]}}}
    calls=[]
    monkeypatch.setattr(ops,'read_operation_result',lambda cfg,ref,**kw:calls.append((ref,kw)))
    with pytest.raises(ValueError,match='NOT_IN_ORIGINAL_CONTEXT'):ops._observed_inputs({},packet,operation,task)
    packet['continuing_context']['continuing_operations']['completed'].append({'reference':task['semantic_validation']})
    ops._observed_inputs({},packet,operation,task)
    assert calls[-1][1]['kinds']==('VALIDATE_RESULT',)


def test_protected_child_can_read_only_captured_validation(monkeypatch):
    def check(config, entry, *, client):
        return client('', 'scientific_validation_result', {'completion':'a'*64})
    monkeypatch.setattr(c,'validate_registration',check)
    value={'config':{},'entry':{},'originals':{},'validation_originals':{'a'*64:{'original':True}}}
    assert c._validate_originals_input(value)=={'original':True}
    del value['validation_originals']['a'*64]
    with pytest.raises(ValueError,match='ORIGINAL_VALIDATION_UNAVAILABLE'):c._validate_originals_input(value)


def test_root_registration_captures_validation_for_actual_child_route(validation_import, monkeypatch, tmp_path):
    config,task,reader,response,reads,observed=setup(validation_import,monkeypatch)
    config.update(source='c'*40, source_root=str(tmp_path/'source'),controller_uid=1234,controller_gid=1234,
                  research_catalog={'directory':str(tmp_path/'catalog')})
    formal=Path(config['state'])/'formal-decisions'
    decision=formal/'eligibility/round-1/decision.json'
    task['protocol']['decision_path']=str(formal/'protocol/round-1/decision.json')
    for name in ('eligibility','protocol'):
        folder=formal/name;folder.mkdir(parents=True)
        (folder/'authority-transport.json').write_bytes(encoded({'event':{'turn_id':name}}))
    # This metadata is only used to locate the exact protected completion.
    folder=Path(config['state'])/'continuing-operations'/task['import_result']['operation']
    folder.mkdir(parents=True)
    raw=encoded({'result':{'completion':response['binding']['completion']}})
    (folder/'result.json').write_bytes(raw);task['import_result']['result_sha256']=hashlib.sha256(raw).hexdigest()
    entry={'request':{'task':task},'eligibility':{'path':str(decision)},'predecessors':[]}
    broker=SimpleNamespace(config={'research_controller_config':'/fixed/config','controller_uid':1234,'sources':['c'*40]},
        stage_status=lambda body:{'original':body})
    monkeypatch.setattr(c.os,'getuid',lambda:0)
    monkeypatch.setattr('orchestrator.handover_runtime.configuration',lambda path:config)
    monkeypatch.setattr('orchestrator.research_catalog.validate_entry',lambda *a:None)
    monkeypatch.setattr('orchestrator.research_catalog.paths',lambda *a:[])
    monkeypatch.setattr('orchestrator.remote_supervisor.checked_source',lambda *a:Path(config['source_root']))
    calls=[]
    def original(broker,operation,body):
        calls.append(operation)
        return reader('',operation,body)
    monkeypatch.setattr('orchestrator.protected_scientific_jobs.handle',original)
    captured=[]
    def child(argv,**kwargs):
        assert argv[-1]=='--verify-originals'
        assert callable(kwargs['preexec_fn'])
        value=json.loads(kwargs['input']);captured.append(value)
        assert value['validation_originals']=={response['binding']['completion']:response}
        assert value['result_originals'][response['binding']['completion']]['completion']==response['binding']['completion']
        return SimpleNamespace(returncode=0,stdout=encoded({'status':'VERIFIED_SUCCESSOR','entry_sha256':c.digest(entry)}))
    monkeypatch.setattr(c.subprocess,'run',child)
    monkeypatch.setattr(c,'_install_entry',lambda cfg,e,r:r)
    assert c.protected_register(broker,{'entry':entry})['status']=='VERIFIED_SUCCESSOR'
    assert calls==['scientific_job_result','scientific_validation_result']
    assert len(captured)==1
