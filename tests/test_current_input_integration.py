"""Current storage -> native capture -> protected role originals, with fixed fixtures."""
from copy import deepcopy
from pathlib import Path
import json
import os
from types import SimpleNamespace

import pytest
from orchestrator import current_scientific_input as current, linked_disposition_input as linked
from orchestrator import disposition_context as dc, change_requests as changes
from orchestrator import scientific_evidence_access as access, scientific_evidence_runtime as runtime
from orchestrator import continuing_research as continuing, hosted_context
from test_linked_input_integration import integrated
from test_selected_scientific_history import captured, append, write_state, prompt_for
from test_campaign_grounding_presentation import example
from test_current_linked_storage import PLAN
from test_disposition_context import SOURCE


@pytest.fixture
def current_packet(integrated,tmp_path):
    e=integrated;store=Path(e.config['change_request_store'])
    # The older prefix fixture predates protected stage originals. Supply their
    # actual typed slots explicitly as synthetic data, then rebind the original.
    from orchestrator.hosted_cycle import encoded
    import hashlib
    e.linked_original=deepcopy(e.linked_original)
    e.linked_original['originals']['protected_original']={'stages':{
        'continuation':{'answer':'Synthetic original author output.'},
        'review':{'answer':'Synthetic original opposing review.'}}}
    e.linked_original['result']['answer']='Synthetic original disposition.'
    e.linked_original['result']['original_proof_sha256']=hashlib.sha256(encoded(e.linked_original['originals'])).hexdigest()
    e.linked_original['result_sha256']=hashlib.sha256(encoded(e.linked_original['result'])).hexdigest()

    state=changes.load(store/e.app['request_identity'])
    app=append(state,'APPLIED',{'modification':'Synthetic current storage integration.',
        'checks':['Synthetic'], 'review_status':'PENDING',
        'result_binding':{'source':SOURCE,'linked_disposition_input':PLAN},
        'supersedes_applied_events':[e.app['identity']]})
    write_state(store,state)
    packet=deepcopy(e.input)
    packet['recorded_changes']=state
    packet['reviewer_evidence']['catalog_core']['change_request']['applied_event']=app['identity']
    evidence=dc.reconstruct_evidence(packet['reviewer_evidence']['input_evidence'],SOURCE)
    evidence['verified_events'][0]['linked_disposition']=linked.reference_view(
        e.linked_original,PLAN,app['identity'],SOURCE)
    from orchestrator.handover_coordinator import digest
    evidence['verified_events'][0]['event']['original_sha256']=e.linked_original['result_sha256']
    core={k:v for k,v in evidence['investigator_wake'].items() if k!='identity'}
    core['events']=[r['event'] for r in evidence['verified_events']]
    evidence['investigator_wake']={**core,'identity':digest(core)}
    packet['reviewer_evidence']['input_evidence']=dc.encode_evidence(evidence,SOURCE)
    e.current_packet=dc.capture_current_history(e.config,packet)
    e.current_app=app
    e.original_input=packet
    return e


def test_native_snapshot_reconstructs_exact_saved_prefix_after_append(current_packet):
    e=current_packet;p=e.current_packet
    before=deepcopy(p)
    cap=access.capture_task_changes(e.config['change_request_store'],p,source=SOURCE)
    assert current.is_current(p)
    assert p==before
    assert 'Full original synthetic adverse finding.' in str(p)
    assert 'Complete external criticism.' in str(p)
    assert p['recorded_changes']['schema']=='current-change-state-location/v1'
    request=p['scientific_change_history']['primary']['request_id']
    state=changes.load(Path(e.config['change_request_store'])/request)
    append(state,'DISPOSITION',{'rationale':'New later criticism must not rewrite old receipts.',
                                'affected_results':['Synthetic']})
    write_state(Path(e.config['change_request_store']),state)
    assert access.capture_task_changes(e.config['change_request_store'],p,source=SOURCE)==cap


@pytest.mark.parametrize('fault',['criticism','prefix','application','response','scope','primary_location'])
def test_tampered_current_snapshot_refuses_native_capture(current_packet,fault):
    e=current_packet;p=deepcopy(e.current_packet);h=p['scientific_change_history']
    primary=h['primary']['request_id']
    if fault=='criticism':h['current_requests'][primary]['events']=[]
    elif fault=='prefix':h['native_prefixes'][primary]['head_sha256']='0'*64
    elif fault=='application':h['primary']['applied_event']='0'*64
    elif fault=='response':h['literal_response_originals']={}
    elif fault=='scope':h['native_prefixes'].pop(next(k for k in h['native_prefixes'] if k!=primary))
    else:p['recorded_changes']['request_id']='0'*64
    with pytest.raises((ValueError,KeyError)):
        access.capture_task_changes(e.config['change_request_store'],p,source=SOURCE)


def test_actual_controller_and_protected_capture_share_authentic_original(current_packet,tmp_path,monkeypatch):
    e=current_packet;p=e.current_packet
    calls=[]
    def read(cfg,ref,client):
        calls.append(ref)
        return deepcopy(e.linked_original)
    monkeypatch.setattr('orchestrator.disposition_successors.read_result_reference',read)
    monkeypatch.setattr(runtime,'enabled',lambda *args,**kw:True)
    config={**e.config,'state':str(tmp_path/'state'),'broker_socket':'synthetic', 'controller_uid':os.getuid()}
    monkeypatch.setattr('orchestrator.protected_scientific_jobs.controller_configuration',lambda broker:config)
    # Native protected-reader proof validation is separately tested. This seam
    # supplies its fixed authenticated original; all capture/view checks are real.
    expected=runtime.controller_options(config,e.root,SOURCE,p,'review')
    actual=runtime.broker_capture(SimpleNamespace(),p,source=SOURCE,folder=tmp_path/'attempt',stage='review')
    assert expected['evidence_access']['descriptor']==actual['descriptor']
    assert len(calls)==2  # each consumes its capture; no extra fake post-call retrieval
    reader=access.Reader(actual['directory'],actual['descriptor']['manifest_sha256'],
        source=SOURCE,task_binding=actual['descriptor']['task_binding'],owner=os.getuid())
    names={r['name'] for r in reader.records}
    assert any(name.endswith('/author.original.txt') for name in names)
    assert any(name.endswith('/reviewer.original.txt') for name in names)
    assert any(name.endswith('/disposition.original.txt') for name in names)


def test_changed_literal_science_refuses_even_with_valid_original_reference(current_packet,monkeypatch):
    e=current_packet;p=deepcopy(e.current_packet)
    p['reviewer_evidence']['input_evidence']['verified_events'][0]['linked_disposition']['originals']['scientific_input_context']['pending']='tampered'
    monkeypatch.setattr('orchestrator.disposition_successors.read_result_reference',
                        lambda *args,**kw:deepcopy(e.linked_original))
    monkeypatch.setattr(runtime,'enabled',lambda *args,**kw:True)
    with pytest.raises(ValueError):
        runtime._capture(e.config,p,SOURCE,root=e.root,original_client=lambda *a:None)


def test_new_format_cannot_run_with_old_no_retrieval_profile(current_packet,monkeypatch):
    e=current_packet
    monkeypatch.setattr(runtime,'enabled',lambda *args,**kw:False)
    with pytest.raises(ValueError,match='NATIVE_RETRIEVAL_REQUIRED'):
        runtime._capture(e.config,e.current_packet,SOURCE,root=e.root,original_client=lambda *a:None)


def test_composer_requires_actual_role_capture(current_packet):
    e=current_packet
    from orchestrator.hosted_cycle import encoded
    with pytest.raises(ValueError,match='AUTHENTICATED_ROLE_CAPTURE_REQUIRED'):
        hosted_context.compose_input(e.root,encoded(e.current_packet),'Synthetic',verified_source=SOURCE,
                                     family='claude')



def test_saved_snapshot_cannot_be_recaptured_against_live_history(current_packet):
    e=current_packet
    with pytest.raises(ValueError,match='ALREADY_CAPTURED'):
        dc.capture_current_history(e.config,e.current_packet)


@pytest.mark.parametrize('family',['codex','claude'])
def test_real_composer_keeps_open_criticism_and_task_bound_retrieval(current_packet,monkeypatch,family):
    e=current_packet;p=e.current_packet
    from orchestrator.hosted_cycle import encoded
    monkeypatch.setattr('orchestrator.disposition_successors.read_result_reference',
                        lambda *args,**kw:deepcopy(e.linked_original))
    monkeypatch.setattr(runtime,'enabled',lambda *args,**kw:True)
    config={**e.config,'state':str(e.root.parent/'compose-state'),'broker_socket':'synthetic'}
    options=runtime.controller_options(config,e.root,SOURCE,p,
                                      'continuation' if family=='codex' else 'review')
    body,context=hosted_context.compose_input(e.root,encoded(p),prompt_for(e,p),
        verified_source=SOURCE,family=family,prepared_prompt=True,**options)
    assert 'Complete external criticism.' in body
    assert 'Synthetic original opposing review.' in body
    assert 'scientific_evidence_read' in body
    assert context['task_state']['scientific_change_history']==p['scientific_change_history']
    assert hosted_context.context_bytes(e.root,context,SOURCE)



def test_campaign_author_review_and_disposition_use_current_capture(current_packet,monkeypatch):
    e=current_packet
    from orchestrator import hosted_campaign as campaign, campaign_disposition as disposition
    packet=deepcopy(e.campaign);packet.pop('scientific_change_history')
    packet['reviewer_evidence']=deepcopy(e.current_packet['reviewer_evidence']['input_evidence'])
    packet['research_catalog_entry']['change_request']={
        'request_id':e.current_app['request_identity'],'applied_event':e.current_app['identity']}
    packet=dc.capture_current_history(e.config,packet)
    monkeypatch.setattr('orchestrator.disposition_successors.read_result_reference',
                        lambda *args,**kw:deepcopy(e.linked_original))
    monkeypatch.setattr(runtime,'enabled',lambda *args,**kw:True)
    config={**e.config,'state':str(e.root.parent/'campaign-state'),'broker_socket':'synthetic'}
    first=campaign.campaign_preflight(e.root,SOURCE,packet,supplement=e.supplement,evidence_config=config)
    third=disposition.preflight(e.root,SOURCE,packet,'Synthetic report projection only.',evidence_config=config)
    assert [row['stage'] for row in first['stages']]==['continuation','review']
    assert third['stage']=='disposition'
    assert all(row['characters']>0 for row in first['stages']+[third])
    assert first['models']==first['admissions']==third['admissions']==0


def test_native_authentication_uses_supplied_reader_without_nested_socket(current_packet, monkeypatch):
    e = current_packet
    config = {**e.config, 'state': str(e.root.parent/'state'), 'broker_socket': 'must-not-connect'}
    calls = []
    def protected_reader(socket, operation, body):
        assert operation == 'stage_status'
        calls.append(body)
        return {'synthetic_original': True}
    def linked_original(cfg, reference, client):
        assert client is protected_reader
        assert client('', 'stage_status', {'original': reference}) == {'synthetic_original': True}
        return deepcopy(e.linked_original)
    monkeypatch.setattr('orchestrator.disposition_successors.read_result_reference', linked_original)
    monkeypatch.setattr('orchestrator.handover_runtime.request_broker',
                        lambda *a, **kw: pytest.fail('Protected verification must not reconnect to its serving broker'))
    monkeypatch.setattr(runtime, 'enabled', lambda *a, **kw: True)
    proof = dc.authenticate_report_references(config, e.current_packet, SOURCE,
                                               original_client=protected_reader)
    assert len(calls) == 1
    for stage in ('continuation', 'review'):
        actual = runtime._captured_options(config, SOURCE, e.current_packet, stage, proof['capture'])
        assert actual['evidence_access']['descriptor'] == proof['capture']
    assert len(calls) == 1  # role projections are not extra original retrievals
    # A separate invocation must reauthenticate; there is no persistent cache.
    repeated = dc.authenticate_report_references(config, e.current_packet, SOURCE,
                                                  original_client=protected_reader)
    assert repeated == proof and len(calls) == 2
    actual = runtime.controller_options(config, e.root, SOURCE, e.current_packet, 'review',
                                        original_client=protected_reader)
    assert actual['evidence_access']['descriptor'] == proof['capture'] and len(calls) == 3
    changed = deepcopy(e.current_packet)
    changed['scientific_change_history']['primary']['applied_event'] = '0'*64
    with pytest.raises((ValueError, KeyError)):
        dc.authenticate_report_references(config, changed, SOURCE, original_client=protected_reader)
    with pytest.raises(ValueError, match='EXACT_TASK_CAPTURE_REQUIRED'):
        runtime._captured_options(config, SOURCE, changed, 'review', proof['capture'])
    wrong = deepcopy(proof['capture']); wrong['source'] = 'f'*40
    with pytest.raises(ValueError, match='SOURCE_BOUND_CAPTURE_REQUIRED'):
        runtime._captured_options(config, SOURCE, e.current_packet, 'review', wrong)
