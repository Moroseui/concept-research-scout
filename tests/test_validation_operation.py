"""Saved H2 operation integration; fake model stages confer no authority."""
from copy import deepcopy
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from test_continuing_operations import fixture
from orchestrator import continuing_operations as ops
from orchestrator import scientific_validation as semantic
from orchestrator import protected_scientific_jobs as route


def selected(fixture):
    runtime, selection, packet, ref = fixture
    completion = 'f'*64
    selection['successor'] = {'schema': ops.SCHEMA, 'operation_id': 'fixture-validation',
        'kind': 'VALIDATE_RESULT', 'inputs': {'completion': completion}}
    packet['continuing_context']['scientific_completions'] = [{'event': completion}]
    return runtime, selection, packet, ref


def test_validation_selection_requires_original_completion_and_no_command(fixture):
    runtime, selection, packet, ref = selected(fixture)
    assert ops.contract(selection['successor']) == selection['successor']
    packet['continuing_context']['scientific_completions'] = []
    with pytest.raises(ValueError, match='COMPLETION_NOT_IN_ORIGINAL_CONTEXT'):
        ops.enqueue(runtime, ref)
    selection['successor']['inputs']['command'] = 'arbitrary'
    with pytest.raises(ValueError):
        ops.contract(selection['successor'])


def test_same_completion_under_another_slug_does_not_create_another_authority_attempt(fixture):
    runtime, selection, packet, ref = selected(fixture)
    original = ops.enqueue(runtime, ref)
    selection['successor']['operation_id'] = 'a-different-label'
    repeated = ops.enqueue(runtime, ref)
    assert repeated['operation'] == original['operation']
    assert repeated['duplicate'] is True
    assert len(ops.status(runtime.config)['operations']) == 1


def test_wait_has_no_import_intent_and_terminal_import_preserves_defer_evidence(fixture, monkeypatch):
    runtime, selection, packet, ref = selected(fixture)
    identity = ops.enqueue(runtime, ref)['operation']
    folder = ops._directory(runtime.config)/identity
    calls = []
    monkeypatch.setattr(ops, '_prepared', lambda *args: {'fixture': True})
    def step(*args):
        position = args[3]; calls.append(position)
        return ({'validator_status':'DEFER', 'formal_decision_status':'PENDING',
                 'scientific_acceptance':False, 'adoption':False} if position == 3
                else {'status':'SYNTHETIC_STEP'})
    monkeypatch.setattr(ops, '_step', step)
    job = {'id': semantic.job_id('f'*64), 'phase':'scientific_validation', 'status':'RUNNING'}
    observed = []
    monkeypatch.setattr(ops, '_client', lambda runtime:
        lambda socket, operation, body: observed.append(operation) or {'jobs':[job]})
    for _ in range(3):
        assert ops.advance(runtime)['status'] == 'STEP_COMPLETE'
    for _ in range(3):
        assert ops.advance(runtime)['status'] == 'AWAITING_VALIDATION_COMPLETION'
        assert not (folder/'started-3.json').exists()
    assert calls == [0,1,2] and observed == ['scientific_job_status']*3
    job['status'] = 'COMPLETE'
    result = ops.advance(runtime)
    assert result['status'] == 'COMPLETE'  # Import completed; science remains pending.
    assert result['result']['validator_status'] == 'DEFER'
    assert result['result']['formal_decision_status'] == 'PENDING'
    assert result['scientific_acceptance'] is False
    assert ops.advance(runtime)['status'] == 'AWAITING_REVIEWED_SELECTION'
    assert calls == [0,1,2,3]


def test_formal_defer_is_persistent_and_never_dispatches(fixture, monkeypatch):
    runtime, selection, packet, ref = selected(fixture)
    ops.enqueue(runtime, ref)
    monkeypatch.setattr(ops, '_prepared', lambda *args: {})
    calls = []
    monkeypatch.setattr(ops, '_step', lambda *args:
        calls.append(args[3]) or {'status':'AGENT_REVIEWED_DEFERRAL'})
    assert ops.advance(runtime)['status'] == 'DEFERRED'
    assert ops.advance(runtime)['status'] == 'AWAITING_REVIEWED_SELECTION'
    assert calls == [0]


def test_fixed_steps_bind_separate_formal_authority_registration_and_dispatch(fixture, monkeypatch, tmp_path):
    runtime, selection, packet, ref = selected(fixture)
    identity = ops.enqueue(runtime, ref)['operation']
    folder = ops._directory(runtime.config)/identity
    saved = ops._saved(folder); calls = []
    formal = {'action':'launch_linux_job', 'subject':semantic.job_id('f'*64)}
    monkeypatch.setattr('orchestrator.formal_decisions.execute_formal_decision',
        lambda config, request, output, client: calls.append(('formal',request)) or
        {'status':'SYNTHETIC_AUTHORITY', 'decision_path':str(output/'round-1/decision.json')})
    def client(socket, operation, body):
        calls.append((operation,body))
        return {'status':'REGISTERED', 'job':semantic.job_id('f'*64)}
    monkeypatch.setattr(ops, '_client', lambda runtime: client)
    authority = ops._step(runtime,saved,folder,0,{'formal_request':formal})
    (folder/'step-0.json').write_text(json.dumps({'result':authority}))
    registered = ops._step(runtime,saved,folder,1,{'formal_request':formal})
    (folder/'step-1.json').write_text(json.dumps({'result':registered}))
    ops._step(runtime,saved,folder,2,{'formal_request':formal})
    assert calls[0] == ('formal',formal)
    assert calls[1] == ('register_scientific_validation', {
        'completion':'f'*64, 'decision_path':authority['decision_path']})
    assert calls[2] == ('dispatch_scientific_job', {'job':semantic.job_id('f'*64)})


def test_registration_remains_behind_deployed_review_gate():
    from orchestrator.protected_handover import Broker
    def held(): raise ValueError('HELD_DEPLOYMENT')
    broker = SimpleNamespace(config={'controller_uid':os.getuid()}, reviewed_deployment=held)
    with pytest.raises(ValueError, match='HELD_DEPLOYMENT'):
        Broker.handle(broker, {'operation':'register_scientific_validation',
            'body':{'completion':'f'*64,'decision_path':'/unused'}}, os.getuid())


def test_validator_registration_retains_pause_gate(tmp_path):
    from test_protected_scientific_jobs import fixture as controls
    import sqlite3
    broker, config = controls(tmp_path)
    db=sqlite3.connect(Path(config['state'])/'coordinator.sqlite')
    db.execute('UPDATE controls SET paused=1');db.commit();db.close()
    decision=Path(config['state'])/'formal-decisions/fixed/round-1/decision.json'
    with pytest.raises(ValueError, match='OPERATOR_PAUSED'):
        route.handle_registry(broker,config,None,'register_scientific_validation',
                              {'completion':'f'*64,'decision_path':str(decision)})
