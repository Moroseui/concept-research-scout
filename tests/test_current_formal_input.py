"""Formal prospective integration; synthetic authority never qualifies deployment."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import json
import os

import pytest
from orchestrator import formal_decisions as formal, formal_input
from orchestrator import current_scientific_input as current, scientific_evidence_access as access
from orchestrator import scientific_evidence_runtime as runtime, hosted_context as hosted
from orchestrator import scientific_authority as authority, scientific_decision as decision
from orchestrator.hosted_cycle import encoded
from test_current_input_integration import current_packet
from test_linked_input_integration import integrated
from test_selected_scientific_history import captured, append, write_state
from test_campaign_grounding_presentation import example
from test_current_successor_history import next_packet
from test_formal_scientific_versions import formal_request, formal_broker
from test_research_task_authority import setup as authority_setup
from test_disposition_context import SOURCE

NATIVE_ENABLED = runtime.enabled


@pytest.fixture
def current_formal(current_packet, monkeypatch):
    e = current_packet
    _, state, app = next_packet(e, 'TASK')
    request = formal_request(e.config)
    request['change_request'] = {'request_id':state['request']['identity'], 'applied_event':app['identity']}
    request['evidence'] = {'analysis.json': '{"finding":"Literal science, not accepted"}'}
    monkeypatch.setattr(runtime, 'enabled', lambda *a, **kw: True)
    packet = formal._packet(e.config, request)
    assert current.is_current(packet)
    e.formal_request, e.formal_packet, e.formal_state = request, packet, state
    return e


def prepare(e, monkeypatch):
    monkeypatch.setattr(authority, 'context', lambda root: hosted.shared_policy(root))
    monkeypatch.setattr(authority, 'decision_context', lambda root, **kw: {'exact_test_action':kw})
    evidence = formal_input.evidence_for_packet(e.root, e.formal_packet, SOURCE)
    request = e.formal_request
    return decision.prepare(e.root, action=request['action'], subject=request['subject'],
        bindings=request['bindings'], evidence=evidence, request=request['request'], max_rounds=1)


def test_current_formal_native_originals_both_roles_and_later_history(current_formal, tmp_path, monkeypatch):
    e = current_formal; p = e.formal_packet
    config = {**e.config, 'state':str(tmp_path/'state'), 'broker_socket':'synthetic', 'controller_uid':os.getuid()}
    monkeypatch.setattr('orchestrator.protected_scientific_jobs.controller_configuration',lambda broker:config)
    before = deepcopy(p)
    descriptors = []
    for stage, role in [('continuation','author'),('review','reviewer')]:
        expected = runtime.controller_options(config,e.root,SOURCE,p,stage)
        actual = runtime.broker_capture(SimpleNamespace(),p,source=SOURCE,folder=tmp_path/'broker',stage=stage)
        assert expected['evidence_access']['descriptor'] == actual['descriptor']
        assert actual['role'] == role
        reader = access.Reader(actual['directory'],actual['descriptor']['manifest_sha256'],
            source=SOURCE,task_binding=actual['descriptor']['task_binding'],owner=os.getuid())
        row=reader.rows['formal/evidence/analysis.json']
        reply=reader.call('read',{'capture':reader.identity,'name':row['name'],'sha256':row['sha256'],
                                  'offset':0,'characters':8192})
        assert reply['content'] == e.formal_request['evidence']['analysis.json']
        assert reader.call('search',{'capture':reader.identity,'cursor':0,'text':'REQUEST_CHANGES'})['matches']
        descriptors.append(actual['descriptor'])
    append(e.formal_state,'DISPOSITION',{'rationale':'New unresolved tail, not a rewritten old capture.',
                                       'affected_results':['Synthetic']})
    write_state(Path(e.config['change_request_store']),e.formal_state)
    assert access.describe_capture(access.capture_formal_changes(e.config['change_request_store'],p,source=SOURCE)) == descriptors[0]
    assert p == before


@pytest.mark.parametrize('family',['codex','claude'])
def test_formal_full_composition_literal_request_once_and_exact_policy(current_formal,monkeypatch,family):
    e=current_formal; p=e.formal_packet
    prepared=prepare(e,monkeypatch)
    stage='continuation' if family=='codex' else 'review'
    prompt=prepared['body'] if family=='codex' else decision.review_body(prepared['body'],b'J'*30000)
    config={**e.config,'state':str(e.root.parent/'state'),'broker_socket':'synthetic'}
    options=runtime.controller_options(config,e.root,SOURCE,p,stage)
    body,context=hosted.compose_input(e.root,encoded(p),prompt,verified_source=SOURCE,
                                     family=family,prepared_prompt=True,**options)
    hosted.measure_input(body,family,stage,task_state=p)
    assert body.count('Literal science, not accepted') == 1
    assert 'Full original synthetic adverse finding.' in body
    assert 'Complete external criticism.' in body
    assert context['task_state']['formal_request'] == e.formal_request
    assert hosted.TRUSTED_POLICY_MARKER in body
    assert hosted.EVIDENCE_MARKER in body
    assert 'scientific_evidence_read' in body
    assert 'PENDING' in body
    assert 'no approval is inferred' in body


@pytest.mark.parametrize('fault',['source','contract','application','namespace','criticism','prefix','response','scope','hybrid'])
def test_current_formal_changed_native_binding_refused(current_formal,fault):
    e=current_formal; p=deepcopy(e.formal_packet);h=p['scientific_change_history']
    if fault=='source':p['formal_request']['source']='f'*40
    elif fault=='contract':p['scientific_decision_artifacts']['subject']='Changed'
    elif fault=='application':p['formal_request']['change_request']['applied_event']='f'*64
    elif fault=='namespace':p['formal_request']['change_request']['request_id']='f'*64
    elif fault=='criticism':h['current_requests'][h['primary']['request_id']]['events']=[]
    elif fault=='prefix':h['native_prefixes'][h['primary']['request_id']]['head_sha256']='f'*64
    elif fault=='response':h['literal_response_originals']={}
    elif fault=='scope':h['native_prefixes'].pop(next(k for k in h['native_prefixes'] if k!=h['primary']['request_id']))
    else:p['extra']=True
    with pytest.raises((ValueError,KeyError,FileNotFoundError)):
        access.capture_formal_changes(e.config['change_request_store'],p,source=SOURCE)


@pytest.mark.parametrize('fault',['policy','evidence','double_policy','missing_policy'])
def test_formal_composer_does_not_accept_altered_policy_or_reference(current_formal,monkeypatch,fault):
    e=current_formal; prepared=prepare(e,monkeypatch); body=prepared['body']
    if fault=='policy':body=body.replace(json.dumps(hosted.shared_policy(e.root)),json.dumps({'changed':'policy'}))
    elif fault=='evidence':body=body.replace('"recorded-formal-request.json"','"changed.json"')
    elif fault=='double_policy':body+='\nCURRENT USER POLICY:\n{}'
    else:body=body.replace('CURRENT USER POLICY:','CHANGED POLICY:')
    context={**deepcopy(e.current),'task_state':e.formal_packet}
    with pytest.raises(ValueError):
        formal_input.presentation(e.root,e.formal_packet,context,body,SOURCE)


def test_current_formal_requires_source_profile_and_real_role_capture(current_formal,monkeypatch):
    e=current_formal
    with pytest.raises(ValueError,match='AUTHENTICATED_ROLE_CAPTURE_REQUIRED'):
        hosted.compose_input(e.root,encoded(e.formal_packet),'test',verified_source=SOURCE,family='claude')
    monkeypatch.setattr(runtime,'enabled',lambda *a,**kw:False)
    with pytest.raises(ValueError,match='CURRENT_FORMAL_SOURCE_PROFILE_REQUIRED'):
        runtime._capture(e.config,e.formal_packet,SOURCE,root=e.root)
    with pytest.raises(ValueError,match='CURRENT_FORMAL_SOURCE_PROFILE_REQUIRED'):
        formal_input.evidence_for_packet(e.root,e.formal_packet,SOURCE)


def test_formal_never_selects_eligibility_only_policy_mode(current_formal,monkeypatch):
    e=current_formal; prepared=prepare(e,monkeypatch)
    stages=formal.FormalDecisionStages('synthetic',formal.event(e.formal_request),e.formal_packet,
        source_root=e.root,source=SOURCE,evidence_config=e.config)
    assert stages.hosted_policy_source(e.root) is None
    request=e.formal_request
    again=decision.prepare(e.root,action=request['action'],subject=request['subject'],
        bindings=request['bindings'],evidence=formal_input.evidence_for_packet(e.root,e.formal_packet,SOURCE),
        request=request['request'],max_rounds=1,hosted_policy_source=stages.hosted_policy_source(e.root))
    assert again==prepared
    with pytest.raises(ValueError,match='HOSTED_POLICY_EXACT_AUTHORITY_SOURCE_REQUIRED'):
        decision.prepare(e.root,action=request['action'],subject=request['subject'],
            bindings=request['bindings'],evidence={'x':'x'},request='test',hosted_policy_source=SOURCE)


def test_formal_execution_with_current_eligibility_profile_preserves_recovery(authority_setup, monkeypatch):
    config, _, _ = authority_setup
    module = Path(config['source_root'])/'orchestrator/research_task_authority.py'
    module.write_text(module.read_text()+'\nHOSTED_PRESENTATION_VERSION = 1\n')
    request = formal_request(config)
    broker = formal_broker(monkeypatch)
    output = Path(config['state'])/'formal-decisions/policy-mode'
    first = formal.execute_formal_decision(config,request,output,client=broker)
    assert first['new_model_calls'] == 2 and first['application_status'] == 'NOT_APPLIED'
    original={p.relative_to(output):p.read_bytes() for p in output.rglob('*') if p.is_file()}
    again=formal.execute_formal_decision(config,request,output,client=broker)
    assert again['new_model_calls'] == 0
    assert broker.calls.count('admit_server') == 1 and broker.calls.count('model_stage') == 2
    assert {p.relative_to(output):p.read_bytes() for p in output.rglob('*') if p.is_file()} == original


def test_generated_workspace_uses_installed_profile_for_actual_preflight(current_formal,monkeypatch,tmp_path):
    e=current_formal; prepared=prepare(e,monkeypatch)
    workspace=tmp_path/'generated-no-git';workspace.mkdir()
    (e.root/'orchestrator/scientific_evidence_runtime.py').write_text('FORMAL_EVIDENCE_INPUT_VERSION = 1\nCURRENT_FORMAL_INPUT_VERSION = 1\n')
    monkeypatch.setattr(runtime,'enabled',NATIVE_ENABLED)
    config={**e.config,'state':str(tmp_path/'state'),'broker_socket':'synthetic'}
    stage=formal.FormalDecisionStages('synthetic',formal.event(e.formal_request),e.formal_packet,
        source_root=e.root,source=SOURCE,evidence_config=config)
    # The fixture checked_source accepts only e.root; passing workspace into
    # source-profile/composition validation must fail. Actual preflight uses the
    # installed source and both preserved workspace-bound decision bodies fit.
    rows=stage.preflight_bodies(workspace,prepared['body'],1)
    assert [row['stage'] for row in rows] == ['continuation','review']
    assert all(row['provider_calls'] == 0 for row in rows)
    with pytest.raises(ValueError,match='WRONG_IMMUTABLE_SOURCE'):
        formal_input.evidence_for_packet(workspace,e.formal_packet,SOURCE)
