import copy
import json
import socket

import pytest

from orchestrator.continuing_research import task_contract
from orchestrator.protected_handover import model_output_format, scientific_timeout
from orchestrator.handover_runtime import request_broker
from orchestrator.hosted_cycle import model_call


def task():
    return {'schema': 'continuing-research-task/v1', 'task_id': 'reviewed-next',
            'experiment': 'P001', 'mode': 'investigate', 'request': 'Assess saved evidence.',
            'references': [], 'selected_by': None}


def test_actual_continuing_contract_rejects_changed_task_and_combined_authority():
    original = task()
    packet = {'campaign_task': original, 'campaign_artifacts': task_contract(original)}
    assert model_output_format(packet, 'continuation') == 'json'
    assert model_output_format(packet, 'review') == 'json'
    assert model_output_format(packet, 'disposition') == 'markdown'
    changed = copy.deepcopy(packet)
    changed['campaign_task']['request'] = 'A different proposal.'
    with pytest.raises(ValueError, match='CONTRACT_CHANGED'):
        model_output_format(changed, 'continuation')
    mixed = {**packet, 'scientific_decision_artifacts':
             {'version': 3, 'action': 'authorize_protocol', 'subject': 'prospective-protocol',
              'bindings_sha256': 'a'*64}}
    with pytest.raises(ValueError, match='SCIENTIFIC_DECISION_CONTRACT'):
        model_output_format(mixed, 'continuation')


def test_formal_judgment_has_two_actual_roles_and_no_third_seal_model():
    contracts = [
        {'version': 1, 'action': 'authorize_research_task', 'experiment': 'P001', 'mode': 'readiness'},
        {**task_contract(task()), 'action': 'authorize_research_task'},
        {'version': 3, 'action': 'approve_scientific_version', 'subject': 'prospective-version',
         'bindings_sha256': 'a'*64}]
    for contract in contracts:
        packet = {'scientific_decision_artifacts': contract}
        for stage in ('continuation', 'review'):
            assert model_output_format(packet, stage) == 'json'
        with pytest.raises(ValueError, match='TWO_STAGES_AND_SEAL'):
            model_output_format(packet, 'disposition')
    with pytest.raises(ValueError):
        model_output_format({'scientific_decision_artifacts': {**contracts[-1], 'action': 'activate'}}, 'review')


def test_reviewed_scientific_timeout_cannot_be_raised_by_a_request():
    packet = {'campaign_artifacts': task_contract(task()), 'timeout_seconds': 86400}
    assert scientific_timeout({}, packet) == 240
    assert scientific_timeout({'scientific_model_timeout_seconds': 600}, packet) == 600
    assert scientific_timeout({'scientific_model_timeout_seconds': 600}, {}) == 240
    for invalid in (True, 600.0, 601, 86400):
        with pytest.raises(ValueError, match='BOUNDED_SCIENTIFIC_MODEL_TIMEOUT_REQUIRED'):
            scientific_timeout({'scientific_model_timeout_seconds': invalid}, packet)
        with pytest.raises(ValueError, match='BOUNDED_SCIENTIFIC_MODEL_TIMEOUT_REQUIRED'):
            model_call(None, 'continuation', 'astra', '', timeout_seconds=invalid)


def test_client_wait_covers_reviewed_model_and_registration_bounds(monkeypatch):
    observed = []
    class Client:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def settimeout(self, value): observed.append(value)
        def connect(self, path): assert path == '/fixed/broker.sock'
        def sendall(self, raw): json.loads(raw)
        def recv(self, maximum): return b'{"status":"COMPLETE"}\n'
    monkeypatch.setattr(socket, 'socket', lambda *args: Client())
    for operation in ('model_stage', 'register_research', 'stage_status'):
        assert request_broker('/fixed/broker.sock', operation, {})['status'] == 'COMPLETE'
    assert observed == [660, 120, 300]


def test_original_packet_proof_rejects_later_controller_claims(tmp_path):
    import hashlib
    from orchestrator.hosted_cycle import encoded
    from test_protected_handover import broker
    from test_server_admission import server
    b = broker(tmp_path)
    event = server(1)
    body = {'event': event}
    assert b.stage_packet(body)['status'] == 'NOT_OBSERVED_NO_RETRY'
    folder = tmp_path/'turns'/(event['turn_id']+'-'+event['attempt'])
    folder.mkdir(parents=True)
    original = {'campaign_task': task(), 'scientific_acceptance': False}
    raw = encoded(original)
    sha = hashlib.sha256(raw).hexdigest()
    (folder/'binding.json').write_bytes(encoded({'event': event, 'packet_sha256': sha}))
    (folder/'packet.json').write_bytes(raw)
    assert b.stage_packet(body) == {'status': 'COMPLETE', 'packet_sha256': sha, 'packet': original}
    (folder/'packet.json').write_bytes(encoded({**original, 'scientific_acceptance': True}))
    with pytest.raises(ValueError, match='MODEL_PACKET_BINDING_CHANGED'):
        b.stage_packet(body)
    with pytest.raises(ValueError, match='STAGE_PACKET_SCHEMA'):
        b.stage_packet({**body, 'path': '/caller/selected'})
    with pytest.raises(ValueError, match='SERVER_IDENTITY'):
        b.stage_packet({'event': {**event, 'turn_id': '../outside'}})


def test_material_broker_use_requires_review_but_original_status_survives(tmp_path, monkeypatch):
    from test_protected_handover import broker
    from test_server_admission import server
    b = broker(tmp_path)
    b.config['mode'] = 'LIVE_APPROVED'
    called = []
    monkeypatch.setattr(b, 'model_stage', lambda body: called.append('model'))
    with pytest.raises(ValueError, match='FIXED_LIVE_DEPLOYMENT_CONFIGURATION_REQUIRED'):
        b.handle({'operation': 'model_stage', 'body': {}}, 10001)
    with pytest.raises(ValueError, match='FIXED_LIVE_DEPLOYMENT_CONFIGURATION_REQUIRED'):
        b.handle({'operation': 'admit_server', 'body': server(1)}, 10001)
    assert called == []
    assert b.handle({'operation': 'stage_status', 'body': {'event': server(1), 'stage': 'review'}}, 10001)['status'] == 'NOT_OBSERVED_NO_RETRY'
    assert b.handle({'operation': 'stage_packet', 'body': {'event': server(1)}}, 10001)['status'] == 'NOT_OBSERVED_NO_RETRY'


def test_controller_proof_must_match_its_actual_configuration(monkeypatch):
    import hashlib
    from types import SimpleNamespace
    from orchestrator import handover_runtime
    config = {'source': 'a'*40, 'broker_socket': '/fixed/broker.sock',
              'continuing_operations': {'enabled': True}}
    runtime = SimpleNamespace(config=config)
    actual = {'status': 'INSTALLED_REVIEW_VERIFIED', 'source': 'a'*40,
              'controller_config_sha256': hashlib.sha256(json.dumps(config, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}
    monkeypatch.setattr(handover_runtime, 'request_broker', lambda *args: actual)
    assert handover_runtime.Runtime.deployment_status(runtime) == actual
    config['source'] = 'b'*40
    with pytest.raises(ValueError, match='CURRENT_DEPLOYMENT_REVIEW_PROOF_REQUIRED'):
        handover_runtime.Runtime.deployment_status(runtime)
