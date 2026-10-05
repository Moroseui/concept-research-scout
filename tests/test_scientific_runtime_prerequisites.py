"""Synthetic contracts; these checks do not establish live role retrieval."""
from copy import deepcopy
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from orchestrator import change_requests as changes
from orchestrator import scientific_evidence_access as access
from orchestrator import scientific_runtime_prerequisites as gate
from orchestrator import scientific_evidence_runtime as runtime
from orchestrator.hosted_cycle import encoded as packet_bytes

SOURCE = 'a' * 40
ACTOR = {'kind': 'human', 'identity': 'synthetic-test-operator'}


@pytest.fixture
def bundle(tmp_path):
    source = tmp_path/'source'; source.mkdir()
    store = tmp_path/'changes'
    request = changes.submit(store, source, 'system:runtime-prerequisite-test',
        'Bind the completed synthetic runtime proof before admission.', ACTOR,
        source=SOURCE, scope_limits=['Synthetic test, no model or execution authority.'])
    folder = store/request['identity']
    changes.record(folder, 'AUTHORIZED', ACTOR, {'rationale': 'Synthetic test only.',
        'authority_reference': {'fixture': True}, 'review_policy': 'No production use.'})
    event = {'turn_id': 'b'*64, 'attempt': '1', 'source': SOURCE,
             'branch': 'astra/infrastructure-milestone-record', 'kind': 'astra_turn'}
    proof = {'status': 'SYNTHETIC_COMPLETED', 'source': SOURCE, 'event': event,
             'scientific_authority': False, 'models_launched_by_check': 0}
    path = tmp_path/'proof.json'; path.write_bytes(changes.encoded(proof))
    ref = changes.preserve(folder, path)
    completed = {'source': SOURCE, 'authorization': 'c'*64, 'technical_event': event,
                 'status': proof['status'], 'completed_original': ref}
    disposition = changes.record(folder, 'DISPOSITION', ACTOR, {
        'rationale': 'Observed synthetic completion; no scientific acceptance.',
        'affected_results': ['fixture'], 'runtime_verification': completed})
    spec = {'request': request['identity'], 'event': disposition['identity'], **completed}
    app = changes.record(folder, 'APPLIED', ACTOR, {
        'modification': 'Synthetic expectation only.', 'checks': ['fixture'],
        'result_binding': {'source': SOURCE, gate.FIELD: [spec]}, 'review_status': 'PENDING'})
    packet = {'trigger': 'installed-research-eligibility', 'reviewer_evidence': {
        'catalog_core': {'change_request': {'request_id': request['identity'], 'applied_event': app['identity']}}}}
    capture = access.capture_changes(store, [request['identity']], source=SOURCE,
                                     task_binding=access.sha(packet_bytes(packet)))
    return SimpleNamespace(config={'change_request_store': str(store),
        'source_root': str(source)}, packet=packet,
        capture=capture, spec=spec, app=app, folder=folder)


def test_native_capture_contains_completed_original_without_embedding_it(bundle):
    b = bundle
    result = gate.verify(b.config, b.packet, SOURCE, b.capture)
    assert result == [{'name': 'change/'+b.spec['request']+'/'+b.spec['completed_original']['artifact'],
                      'sha256': b.spec['completed_original']['sha256'], 'event': b.spec['event']}]
    assert 'SYNTHETIC_COMPLETED' not in json.dumps(b.packet)


@pytest.mark.parametrize('failure', ['absent', 'artifact_absent', 'changed', 'wrong_source',
    'wrong_authorization', 'wrong_operation', 'wrong_task', 'wrong_status', 'missing_application'])
def test_missing_or_changed_prerequisites_refuse(bundle, failure):
    b = bundle; cap = deepcopy(b.capture); spec = deepcopy(b.spec)
    if failure == 'absent':
        cap['manifest']['records'] = [r for r in cap['manifest']['records']
            if r['provenance'].get('event') != spec['event']]
    if failure == 'artifact_absent':
        cap['manifest']['records'] = [r for r in cap['manifest']['records'] if r['kind'] != 'change_artifact']
    if failure == 'changed': cap['payloads'][spec['completed_original']['sha256']] += b' '
    if failure == 'wrong_source': spec['source'] = 'd'*40; spec['technical_event']['source'] = 'd'*40
    if failure == 'wrong_authorization': spec['authorization'] = 'd'*64
    if failure == 'wrong_operation': spec['technical_event']['turn_id'] = 'd'*64
    if failure == 'wrong_task': cap['manifest']['task_binding'] = 'd'*64
    if failure == 'wrong_status': spec['status'] = 'NOT_COMPLETED'
    if failure == 'missing_application':
        cap['manifest']['records'] = [r for r in cap['manifest']['records']
            if r['provenance'].get('event') != b.app['identity']]
        with pytest.raises(ValueError, match='SCIENTIFIC_PREREQUISITE'): gate.verify(b.config,b.packet,SOURCE,cap)
        return
    with pytest.raises(ValueError, match='SCIENTIFIC_PREREQUISITE'):
        gate.verify_capture(cap,[spec],source=SOURCE,task_binding=access.sha(packet_bytes(b.packet)))


def test_prefix_before_completion_cannot_substitute_for_current_read(bundle):
    b=bundle; old=deepcopy(b.capture)
    old['manifest']['records']=[r for r in old['manifest']['records']
        if r['provenance'].get('sequence',0) < 2]
    with pytest.raises(ValueError,match='NOT_IN_CAPTURE'): gate.verify(b.config,b.packet,SOURCE,old)


def test_controller_and_protected_capture_call_the_same_guard(bundle, monkeypatch):
    b=bundle
    monkeypatch.setattr(runtime,'_capture_originals',lambda *a,**kw:b.capture)
    for owner in (None,):
        assert runtime._capture(b.config,b.packet,SOURCE,change_owner=owner) is b.capture
    b.capture['payloads'].pop(b.spec['completed_original']['sha256'])
    with pytest.raises(ValueError,match='CAPTURE_BYTES_CHANGED'):
        runtime._capture(b.config,b.packet,SOURCE)


def test_failure_occurs_before_admission_or_model_execution(tmp_path, monkeypatch):
    from orchestrator import research_task_authority as authority
    client=Mock(side_effect=AssertionError('No provider or admission call permitted'))
    monkeypatch.setattr(authority,'_identity',lambda *a:(tmp_path,'synthetic',{}))
    monkeypatch.setattr(authority,'_event',lambda *a:{'source':SOURCE})
    monkeypatch.setattr(authority,'_packet',lambda *a:{'synthetic':True})
    monkeypatch.setattr(authority,'DecisionStages',lambda *a,**kw:object())
    def fail(*args): raise ValueError('SCIENTIFIC_PREREQUISITE_COMPLETION_NOT_IN_CAPTURE')
    monkeypatch.setattr(authority,'_preflight',fail)
    with pytest.raises(ValueError,match='COMPLETION_NOT_IN_CAPTURE'):
        authority.execute({'controller_uid':authority.os.getuid(),'broker_socket':'unused'},
            {'source':SOURCE,'request':{'task':{'schema':'synthetic'}}},tmp_path/'authority',client=client)
    client.assert_not_called()
    refusal=json.loads((tmp_path/'authority.input-preflight-failure.json').read_bytes())
    assert refusal['admissions']==refusal['provider_calls']==0


def test_no_self_selected_paths_or_duplicate_or_unbounded_selection(bundle):
    for mutation in ['path','duplicate','many','empty']:
        items=[deepcopy(bundle.spec)]
        if mutation=='path':items[0]['completed_original']['artifact']='evidence/../../secret'
        if mutation=='duplicate':items*=2
        if mutation=='many':items*=9
        if mutation=='empty':items=[]
        with pytest.raises(ValueError,match='SCIENTIFIC_PREREQUISITE'):gate.validate(items)


def test_record_canonical_json_is_not_the_scientific_packet_binding(bundle):
    b=bundle
    assert changes.encoded(b.packet) != packet_bytes(b.packet)
    assert b.capture['manifest']['task_binding']==access.sha(packet_bytes(b.packet))
    assert gate.verify(b.config,b.packet,SOURCE,b.capture)
    wrong=deepcopy(b.capture)
    wrong['manifest']['task_binding']=access.sha(changes.encoded(b.packet))
    with pytest.raises(ValueError,match='TASK_CAPTURE_CHANGED'):
        gate.verify(b.config,b.packet,SOURCE,wrong)
