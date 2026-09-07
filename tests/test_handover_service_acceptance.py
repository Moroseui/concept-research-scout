"""The supervised harness must refuse unsafe setup before a model request."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def harness(monkeypatch):
    path = Path(__file__).parents[1] / 'scripts/verify_handover_service.py'
    spec = importlib.util.spec_from_file_location('service_acceptance', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, 'os', SimpleNamespace(getuid=lambda: 997))
    monkeypatch.setattr(module, 'resources', lambda: {
        'no_new_privileges': '1',
        'cgroup': {'memory.max': '536870912', 'cpu.max': '100000 100000',
                   'pids.max': '32'},
    })
    return module


def test_wrong_resources_refuse_before_runtime(harness, monkeypatch):
    monkeypatch.setattr(harness, 'resources', lambda: {'no_new_privileges': '0'})
    monkeypatch.setattr(harness.runtime_module, 'Runtime',
                        lambda config: pytest.fail('runtime must not start'))
    with pytest.raises(ValueError, match='RESOURCE_BOUNDARY'):
        harness.run({'purpose': 'SUPERVISED_SERVICE_ACCEPTANCE'}, 'first')


def test_live_ledger_refuses_without_model_request(harness, monkeypatch):
    monkeypatch.setattr(harness.runtime_module, 'Runtime', lambda config: object())
    calls = []
    def request(path, operation, body):
        calls.append(operation)
        return {'mode': 'LIVE_APPROVED'}
    monkeypatch.setattr(harness.runtime_module, 'request_broker', request)
    with pytest.raises(ValueError, match='PRIVATE_FIXTURE_LEDGER'):
        harness.run({'purpose': 'SUPERVISED_SERVICE_ACCEPTANCE',
                     'broker_socket': 'fixture'}, 'first')
    assert calls == ['status']


def test_recovery_blocks_model_before_transport(harness, monkeypatch, tmp_path):
    class Runtime:
        state = tmp_path
        def tick(self):
            return harness.runtime_module.request_broker('fixture', 'model_stage', {})
    monkeypatch.setattr(harness.runtime_module, 'Runtime', lambda config: Runtime())
    calls = []
    def request(path, operation, body):
        calls.append(operation)
        return {'mode': 'SYNTHETIC_FIXTURE', 'count': 1}
    monkeypatch.setattr(harness.runtime_module, 'request_broker', request)
    (tmp_path / 'service-fixture-first.json').write_text('{}')
    with pytest.raises(ValueError, match='RECOVERY_MODEL_CALL_FORBIDDEN'):
        harness.run({'purpose': 'SUPERVISED_SERVICE_ACCEPTANCE',
                     'broker_socket': 'fixture'}, 'recover')
    assert calls == ['status']
    assert harness.runtime_module.request_broker is request
