from contextlib import nullcontext
import json
import os
from pathlib import Path
import sqlite3
import subprocess
from types import SimpleNamespace

import pytest

from orchestrator import protected_scientific_jobs as route


def fixture(tmp_path):
    state = tmp_path/'controller'
    state.mkdir()
    (state/'admission.lock').touch()
    db = sqlite3.connect(state/'coordinator.sqlite')
    db.executescript("CREATE TABLE controls(singleton INTEGER,revision INTEGER,paused INTEGER); INSERT INTO controls VALUES(1,4,0); CREATE TABLE runtime_blocks(phase TEXT,reason TEXT);")
    db.commit(); db.close()
    config = {'state': str(state), 'controller_uid': os.getuid()}
    broker = SimpleNamespace(authentication=lambda: nullcontext(), ledger=SimpleNamespace(
        read=lambda: ('a'*40, {'halted': False, 'sequence': 5})))
    return broker, config


def test_dispatch_gate_uses_same_pause_and_halt_without_new_admission(tmp_path):
    broker, config = fixture(tmp_path)
    with route.admission_guard(broker, config) as proof:
        assert proof['control_revision'] == 4
        assert proof['new_model_admissions'] == 0
    db = sqlite3.connect(Path(config['state'])/'coordinator.sqlite')
    db.execute('UPDATE controls SET paused=1'); db.commit()
    with pytest.raises(ValueError, match='OPERATOR_PAUSED'):
        with route.admission_guard(broker, config): pass
    db.execute('UPDATE controls SET paused=0'); db.commit(); db.close()
    broker.ledger.read = lambda: ('b'*40, {'halted': True, 'sequence': 6})
    with pytest.raises(ValueError, match='ADMISSION_HALTED'):
        with route.admission_guard(broker, config): pass


def test_missing_or_blocked_control_observation_does_not_dispatch(tmp_path):
    broker, config = fixture(tmp_path)
    db = sqlite3.connect(Path(config['state'])/'coordinator.sqlite')
    db.execute("INSERT INTO runtime_blocks VALUES('controls','unavailable')"); db.commit(); db.close()
    with pytest.raises(ValueError, match='CONTROL_TRANSPORT_BLOCKED'):
        with route.admission_guard(broker, config): pass
    (Path(config['state'])/'admission.lock').unlink()
    with pytest.raises(FileNotFoundError):
        with route.admission_guard(broker, config): pass
    assert not (Path(config['state'])/'admission.lock').exists()


def test_service_start_preserves_ambiguous_intent_and_never_retries(tmp_path, monkeypatch):
    registry = SimpleNamespace(config={'requests': str(tmp_path)})
    proposal = {'status': 'REGISTERED', 'attempt': 'c'*64, 'unit': route.jobs.UNIT.format('c'*64)}
    calls = []
    def timed_out(argv, **kwargs):
        calls.append(argv)
        raise subprocess.TimeoutExpired(argv, 20)
    monkeypatch.setattr(subprocess, 'run', timed_out)
    with pytest.raises(subprocess.TimeoutExpired):
        route.start_once(registry, proposal, {'control_revision': 4})
    recovered = route.start_once(registry, proposal, {'control_revision': 4})
    assert recovered['status'] == 'SERVICE_START_UNCERTAIN_NO_RETRY'
    assert len(calls) == 1
    assert calls[0] == ['systemctl', 'start', '--no-block', proposal['unit']]


def test_start_receipt_recovery_does_not_repeat_systemctl(tmp_path, monkeypatch):
    registry = SimpleNamespace(config={'requests': str(tmp_path)})
    proposal = {'status': 'REGISTERED', 'attempt': 'c'*64, 'unit': route.jobs.UNIT.format('c'*64)}
    calls = []
    def started(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=0, stdout=b'', stderr=b'')
    monkeypatch.setattr(subprocess, 'run', started)
    actual = route.start_once(registry, proposal, {'control_revision': 4})
    assert actual['status'] == 'SERVICE_START_REQUEST_ACCEPTED'
    assert actual['scientific_acceptance'] is False
    assert route.start_once(registry, proposal, {'control_revision': 4}) == actual
    assert len(calls) == 1
    with pytest.raises(ValueError, match='FIXED_UNIT_REQUIRED'):
        route.start_once(registry, {**proposal, 'unit': 'unrelated.service'}, {})


def test_original_client_cannot_be_used_to_launch_models():
    broker = SimpleNamespace(stage_status=lambda body: {'status': 'COMPLETE'},
                             stage_packet=lambda body: {'status': 'COMPLETE'})
    client = route.original_client(broker)
    assert client('ignored', 'stage_packet', {})['status'] == 'COMPLETE'
    with pytest.raises(ValueError, match='ORIGINAL_READ_ONLY'):
        client('ignored', 'model_stage', {})


def test_current_change_reviewer_is_the_controller_not_a_root_bypass(tmp_path, monkeypatch):
    references = [{'request_id': 'a'*64, 'applied_event': 'b'*64}]
    config = {'controller_uid': os.getuid()+1}
    with pytest.raises(ValueError, match='VERIFIER_IDENTITY'):
        route.verify_current_changes(config, references)
    config['controller_uid'] = os.getuid()
    def refused(*args): raise ValueError('RESEARCH_CHANGE_REQUIRES_CORRECTION')
    monkeypatch.setattr('orchestrator.research_catalog.linked_change', refused)
    with pytest.raises(ValueError, match='REQUIRES_CORRECTION'):
        route.verify_current_changes(config, references)
