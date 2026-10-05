"""Operation state tests; fake stages are not model/scientific approvals."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import pytest

from orchestrator import continuing_operations as ops
from orchestrator import continuing_research as continuing
from orchestrator.hosted_cycle import encoded


def reference(letter='a', name='proposal.md'):
    return {'task': letter * 64, 'artifact': 'round-1/' + name, 'sha256': 'b' * 64}


def investigator():
    return {'schema': continuing.TASK_SCHEMA, 'task_id': 'synthetic-investigator-v1', 'mode': 'investigate',
        'experiment': 'P001', 'request': 'Synthetic selection only.', 'references': [], 'selected_by': None}


def task():
    return {**investigator(), 'task_id': 'synthetic-next-v1', 'mode': 'propose'}


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    tmp_path.chmod(0o700)
    config = {'state': str(tmp_path), 'source': 'a' * 40, 'source_root': str(tmp_path),
        'controller_uid': os.getuid(), 'controller_gid': os.getgid(), 'broker_socket': 'synthetic',
        'continuing_operations': {'enabled': True}}
    by = {'kind': 'agent', 'family': 'codex', 'model': 'gpt-6-astra', 'actual_model': None,
          'session_id': 'synthetic-original'}
    predecessor = {'task': 'a' * 64, 'source': config['source'], 'disposition_sha256': 'c' * 64,
                   'requires': 'APPROVED_PROPOSAL_ONLY'}
    change = {'request_id': 'd' * 64, 'applied_event': 'e' * 64}
    selection = {'schema': continuing.SELECTION_SCHEMA, 'status': 'PROPOSE', 'rationale': 'Synthetic rationale',
                 'reconsideration': 'Synthetic reconsideration', 'successor': task()}
    packet = {'campaign_task': investigator(), 'reviewer_evidence': {}, 'continuing_context': {}}
    runtime = SimpleNamespace(config=config, q=SimpleNamespace(status=lambda: {'paused': False}))
    monkeypatch.setattr(ops, '_selection', lambda runtime, ref: (selection, packet, predecessor, by, change))
    monkeypatch.setattr('orchestrator.research_catalog.linked_change', lambda *args: None)
    return runtime, selection, packet, reference(name='selection.json')


def test_disabled_status_is_readonly_and_no_directory_is_created(tmp_path):
    assert ops.status({'state': str(tmp_path)})['status'] == 'DISABLED'
    assert not list(tmp_path.iterdir())
    with pytest.raises(ValueError, match='CONFIGURATION'):
        ops.enabled({'continuing_operations': {'enabled': 1}})


def test_operation_contract_has_no_raw_permission_command_or_generic_request():
    operation = {'schema': ops.SCHEMA, 'operation_id': 'synthetic-next', 'kind': 'AUTHORIZE_TASK',
                 'inputs': {'selection': reference(name='selection.json')}}
    assert ops.contract(operation) == operation
    for extra in ({'command': 'python'}, {'permissions': 'all'}, {'formal_request': {}}):
        with pytest.raises(ValueError, match='TYPED_OPERATION'):
            ops.contract({**operation, **extra})
    changed = deepcopy(operation); changed['kind'] = 'SHELL'
    with pytest.raises(ValueError, match='TYPED_OPERATION'): ops.contract(changed)
    changed = deepcopy(operation); changed['inputs']['selection']['artifact'] = '../../secret'
    with pytest.raises(ValueError, match='ARTIFACT_PATH'): ops.contract(changed)


def test_selected_artifacts_must_have_reached_the_actual_investigator():
    operation = {'schema': ops.SCHEMA, 'operation_id': 'synthetic-protocol', 'kind': 'AUTHORIZE_PROTOCOL',
        'inputs': {'experiment': 'P002', 'protocol_id': 'synthetic-protocol', 'prior_protocol': None,
                   'artifacts': {key: reference() for key in ops.PROTOCOL_ARTIFACTS}}}
    with pytest.raises(ValueError, match='NOT_IN_INVESTIGATOR_CONTEXT'):
        ops.validate_selection(investigator(), operation)
    assert ops.validate_selection({**investigator(), 'references': [reference()]}, operation) == operation
    operation['inputs']['experiment'] = 'P001'
    with pytest.raises(ValueError, match='PROSPECTIVE_EXPERIMENT'): ops.contract(operation)


def test_actual_selected_task_queues_authority_preparation_and_reuses_saved_work(fixture):
    runtime, selection, packet, ref = fixture
    first = ops.enqueue(runtime, ref)
    second = ops.enqueue(runtime, ref)
    assert second['operation'] == first['operation'] and second['duplicate']
    saved = ops._saved(ops._directory(runtime.config) / first['operation'])
    assert saved['operation']['kind'] == 'AUTHORIZE_TASK'
    assert saved['actor']['actual_model'] is None
    assert first['models'] == first['admissions'] == 0
    selection['successor']['request'] = 'Changed scientific proposal with same task version'
    # The authority-preparation identity refers to the original selection bytes;
    # actual selection byte verification lives in _selection, not this state fixture.
    assert len(ops.status(runtime.config)['operations']) == 1


def test_one_step_per_tick_then_original_completion_reused(fixture, monkeypatch):
    runtime, selection, packet, ref = fixture
    identity = ops.enqueue(runtime, ref)['operation']; calls = []
    monkeypatch.setattr(ops, '_prepared', lambda *args: {'synthetic': True})
    monkeypatch.setattr(ops, '_step', lambda *args: calls.append(args[3]) or {'status': 'SYNTHETIC_STEP'})
    assert ops.advance(runtime)['status'] == 'STEP_COMPLETE'
    assert calls == [0]
    complete = ops.advance(runtime)
    assert complete['status'] == 'COMPLETE' and calls == [0, 1]
    assert ops.advance(runtime)['status'] == 'AWAITING_REVIEWED_SELECTION'
    assert calls == [0, 1]
    status = ops.status(runtime.config)
    assert ops.read_operation_result(runtime.config, status['completed'][0]['reference']) == complete
    assert (ops._directory(runtime.config) / identity / 'started-0.json').is_file()


def test_pause_blocks_steps_but_status_remains_available(fixture, monkeypatch):
    runtime, _, _, ref = fixture
    ops.enqueue(runtime, ref)
    runtime.q.status = lambda: {'paused': True}
    monkeypatch.setattr(ops, '_step', lambda *args: pytest.fail('Paused operation must not run'))
    assert ops.advance(runtime)['status'] == 'PAUSED'
    assert ops.status(runtime.config)['operations'][0]['status'] == 'QUEUED'


def test_negative_authority_never_reaches_registration(fixture, monkeypatch):
    runtime, _, _, ref = fixture
    ops.enqueue(runtime, ref); calls = []
    monkeypatch.setattr(ops, '_prepared', lambda *args: {})
    monkeypatch.setattr(ops, '_step', lambda *args: calls.append(args[3]) or {'status': 'AGENT_REVIEWED_DEFERRAL'})
    assert ops.advance(runtime)['status'] == 'DEFERRED'
    assert ops.advance(runtime)['status'] == 'AWAITING_REVIEWED_SELECTION'
    assert calls == [0] and not ops.status(runtime.config)['completed']


def test_interrupted_attempt_is_visible_and_polling_cannot_retry(fixture, monkeypatch):
    runtime, _, _, ref = fixture
    identity = ops.enqueue(runtime, ref)['operation']; calls = []
    monkeypatch.setattr(ops, '_prepared', lambda *args: {})
    def failed(*args):
        calls.append('effect'); raise TimeoutError('SYNTHETIC_UNCERTAIN_OUTCOME')
    monkeypatch.setattr(ops, '_step', failed)
    with pytest.raises(TimeoutError): ops.advance(runtime)
    assert ops.status(runtime.config)['operations'][0]['status'] == 'RECONCILIATION_REQUIRED'
    assert (ops._directory(runtime.config) / identity / 'failure-0.json').is_file()
    ops.advance(runtime)
    assert calls == ['effect']


def test_locally_rewritten_operation_cannot_reuse_an_original_selection(fixture, monkeypatch):
    runtime, _, _, ref = fixture
    identity = ops.enqueue(runtime, ref)['operation']
    saved = ops._saved(ops._directory(runtime.config) / identity)
    saved['actor']['model'] = 'fabricated'
    with pytest.raises(ValueError, match='DIFFERS_FROM_ORIGINAL_SELECTION'):
        ops._check_saved(runtime, saved)


def test_changed_result_bytes_are_not_an_operation_reference(fixture, monkeypatch):
    runtime, _, _, ref = fixture
    ops.enqueue(runtime, ref)
    monkeypatch.setattr(ops, '_prepared', lambda *args: {})
    monkeypatch.setattr(ops, '_step', lambda *args: {'status': 'SYNTHETIC_STEP'})
    ops.advance(runtime); ops.advance(runtime)
    ref = ops.status(runtime.config)['completed'][0]['reference']
    path = ops._directory(runtime.config) / ref['operation'] / 'result.json'
    path.write_bytes(path.read_bytes() + b' ')
    with pytest.raises(ValueError, match='BINDING_REQUIRED'):
        ops.read_operation_result(runtime.config, ref)


def test_explicit_authority_recovery_reads_originals_and_never_calls_new_model(fixture, monkeypatch):
    from orchestrator import research_task_authority
    runtime, _, _, ref = fixture
    identity = ops.enqueue(runtime, ref)['operation']
    monkeypatch.setattr(ops, '_prepared', lambda *args: {'entry': {'synthetic': True}})
    monkeypatch.setattr(ops, '_step', lambda *args: (_ for _ in ()).throw(TimeoutError('SYNTHETIC_TIMEOUT')))
    with pytest.raises(TimeoutError): ops.advance(runtime)
    called = []
    monkeypatch.setattr(ops, '_client', lambda runtime: lambda socket, op, body: called.append(op) or {})
    def recovery(config, entry, output, *, recover_from, client):
        assert recover_from.name == 'authority'
        with pytest.raises(ValueError, match='FORBIDS_NEW_ADMISSION_OR_MODEL'):
            client('', 'admit_server', {})
        with pytest.raises(ValueError, match='FORBIDS_NEW_ADMISSION_OR_MODEL'):
            client('', 'model_stage', {})
        client('', 'stage_status', {})
        return {'new_model_calls': 0, 'status': 'AGENT_REVIEWED_DECISION_READY'}
    monkeypatch.setattr(research_task_authority, 'execute', recovery)
    assert ops.recover(runtime, identity)['status'] == 'ORIGINAL_AUTHORITY_RECOVERED'
    assert called == ['stage_status']
    assert ops.status(runtime.config)['operations'][0]['step'] == 'register_and_submit'


def test_partial_nonmodel_effect_is_not_replayed_by_authority_recovery(fixture, monkeypatch):
    runtime, _, _, ref = fixture
    identity = ops.enqueue(runtime, ref)['operation']
    monkeypatch.setattr(ops, '_prepared', lambda *args: {})
    monkeypatch.setattr(ops, '_step', lambda *args: {'status': 'SYNTHETIC_STEP'})
    ops.advance(runtime)
    monkeypatch.setattr(ops, '_step', lambda *args: (_ for _ in ()).throw(TimeoutError('SYNTHETIC_REGISTER_TIMEOUT')))
    with pytest.raises(TimeoutError): ops.advance(runtime)
    with pytest.raises(ValueError, match='ORIGINAL_ADAPTER_RECONCILIATION'):
        ops.recover(runtime, identity)


def test_already_eligible_task_reuses_actual_authority_without_another_judgment(fixture, monkeypatch):
    from orchestrator import research_task_authority
    runtime, _, _, ref = fixture
    identity = ops.enqueue(runtime, ref)['operation']
    folder = ops._directory(runtime.config) / identity
    entry = {'eligibility': {'path': '/synthetic/original-decision', 'sha256': 'f' * 64}}
    monkeypatch.setattr(research_task_authority, 'verify_eligibility',
                        lambda config, saved, **kwargs: {'status': 'ELIGIBLE'})
    monkeypatch.setattr(research_task_authority, 'execute', lambda *a, **k: pytest.fail('Original authority must be reused'))
    result = ops._step(runtime, ops._saved(folder), folder, 0, {'entry': entry, 'reuse_original_authority': True})
    assert result['new_model_calls'] == 0 and result['eligibility'] == entry['eligibility']


def test_failed_saved_submission_never_becomes_a_completed_successor(fixture, monkeypatch):
    runtime, _, _, ref = fixture
    ops.enqueue(runtime, ref)
    monkeypatch.setattr(ops, '_prepared', lambda *args: {})
    monkeypatch.setattr(ops, '_step', lambda *args: {'status': 'FAILED'})
    assert ops.advance(runtime)['status'] == 'BLOCKED'
    assert not ops.status(runtime.config)['completed']


def test_readonly_original_result_recovery_preserves_hash_checks_despite_later_criticism(fixture, monkeypatch):
    runtime, _, _, ref = fixture
    ops.enqueue(runtime, ref)
    monkeypatch.setattr(ops, '_prepared', lambda *args: {})
    monkeypatch.setattr(ops, '_step', lambda *args: {'status': 'SYNTHETIC_STEP'})
    ops.advance(runtime); ops.advance(runtime)
    ref = ops.status(runtime.config)['completed'][0]['reference']
    monkeypatch.setattr('orchestrator.research_catalog.linked_change',
        lambda *args: (_ for _ in ()).throw(ValueError('SYNTHETIC_LATER_CRITICISM')))
    with pytest.raises(ValueError, match='LATER_CRITICISM'):
        ops.read_operation_result(runtime.config, ref)
    assert ops.read_operation_result(runtime.config, ref, current_review=False)['status'] == 'COMPLETE'
    with pytest.raises(ValueError, match='REVIEW_MODE_REQUIRED'):
        ops.read_operation_result(runtime.config, ref, current_review=0)
    path = ops._directory(runtime.config) / ref['operation'] / 'result.json'
    path.write_bytes(path.read_bytes() + b' ')
    with pytest.raises(ValueError, match='BINDING_REQUIRED'):
        ops.read_operation_result(runtime.config, ref, current_review=False)


def test_imported_successor_requires_exact_import_shown_to_selecting_roles(fixture, monkeypatch):
    runtime, selected, packet, ref = fixture
    imported = {'operation': '1' * 64, 'result_sha256': '2' * 64}
    selected['successor']['import_result'] = imported
    observed = {'continuing_operations': {'completed': [{'reference': imported}]}}
    packet['reviewer_evidence'] = deepcopy(observed)
    with pytest.raises(ValueError, match='RESULT_NOT_IN_ORIGINAL_CONTEXT'):
        ops.enqueue(runtime, ref)
    calls = []
    def checked(config, value, *, kinds):
        calls.append((value, kinds)); return {'kind': 'IMPORT_RESULT'}
    monkeypatch.setattr(ops, 'read_operation_result', checked)
    packet['continuing_context'] = deepcopy(observed)
    assert ops.enqueue(runtime, ref)['models'] == 0
    assert calls == [(imported, ('IMPORT_RESULT',))]
    assert packet['reviewer_evidence'] == observed


def test_completion_selection_uses_separate_original_packet_snapshot(fixture):
    runtime, selected, packet, ref = fixture
    selected['successor'] = {'schema': ops.SCHEMA, 'operation_id': 'synthetic-import-v1',
        'kind': 'IMPORT_RESULT', 'inputs': {'completion': '1' * 64}}
    packet['reviewer_evidence'] = {'scientific_completions': [{'event': '1' * 64}]}
    with pytest.raises(ValueError, match='COMPLETION_NOT_IN_ORIGINAL_CONTEXT'):
        ops.enqueue(runtime, ref)
    packet['continuing_context'] = deepcopy(packet['reviewer_evidence'])
    assert ops.enqueue(runtime, ref)['status'] == 'QUEUED'


def test_protocol_proposal_successor_uses_separate_task_authority(fixture):
    from orchestrator.protocol_proposals import TASK_SCHEMA
    runtime, selected, packet, ref = fixture
    selected['successor'] = {**task(), 'schema': TASK_SCHEMA, 'experiment': 'P002', 'mode': 'protocol_proposal'}
    result = ops.enqueue(runtime, ref)
    saved = ops._saved(ops._directory(runtime.config) / result['operation'])
    assert saved['operation']['kind'] == 'AUTHORIZE_TASK'
    assert result['models'] == result['admissions'] == 0


def test_deferred_protocol_bundle_is_refused_before_authority_request(fixture, monkeypatch):
    from test_protocol_proposals import fixture as proposal_fixture, authority_inputs
    runtime, selected, packet, ref = fixture
    _, files, _ = proposal_fixture()
    refs, contents = authority_inputs(files)
    monkeypatch.setattr(ops, '_reviewed_artifact', lambda runtime, ref:
        files[ref['artifact'].removeprefix('round-1/')].encode())
    monkeypatch.setattr(ops, '_formal', lambda *args: pytest.fail('Missing evidence must not reach authority'))
    saved = {'operation': {'inputs': {'protocol_id': 'synthetic-protocol-v1', 'experiment': 'P002',
        'artifacts': refs, 'prior_protocol': None}}}
    with pytest.raises(ValueError, match='DEFERRED_MISSING_EVIDENCE'):
        ops._protocol_request(runtime, saved)


def test_enqueue_interruption_preserves_orphan_but_unrelated_work_advances(fixture, monkeypatch):
    runtime, selected, packet, ref = fixture
    write = ops.immutable
    def interrupted(path, raw):
        if path.name == 'request.json': raise KeyboardInterrupt('SYNTHETIC_ENQUEUE_CRASH')
        return write(path, raw)
    monkeypatch.setattr(ops, 'immutable', interrupted)
    with pytest.raises(KeyboardInterrupt): ops.enqueue(runtime, ref)
    root = ops._directory(runtime.config)
    orphan = next(p for p in root.iterdir() if p.is_dir())
    assert list(orphan.iterdir()) == []
    monkeypatch.setattr(ops, 'immutable', write)
    with pytest.raises(ValueError, match='ORIGINALS_REQUIRE_RECONCILIATION'):
        ops.enqueue(runtime, ref)
    row = ops.status(runtime.config)['operations'][0]
    assert row['status'] == 'RECONCILIATION_REQUIRED' and row['kind'] is None
    assert row['step'] is None and not ops.status(runtime.config)['completed']
    with pytest.raises(ValueError, match='ORIGINALS_REQUIRE_RECONCILIATION'):
        ops.recover(runtime, orphan.name)
    selected['successor']['task_id'] = 'synthetic-independent-v1'
    assert ops.enqueue(runtime, ref)['status'] == 'QUEUED'
    calls = []
    monkeypatch.setattr(ops, '_prepared', lambda *args: {})
    monkeypatch.setattr(ops, '_step', lambda *args: calls.append(args[3]) or {'status': 'SYNTHETIC_STEP'})
    assert ops.advance(runtime)['status'] == 'STEP_COMPLETE'
    assert ops.advance(runtime)['status'] == 'COMPLETE' and calls == [0, 1]
    assert list(orphan.iterdir()) == []
    assert ops.advance(runtime)['blocked_operations'] == [orphan.name]
    assert len(ops.status(runtime.config)['completed']) == 1


def test_discovery_reports_damaged_originals_and_continues_independent_selection(fixture, monkeypatch):
    runtime, selected, packet, ref = fixture
    bad, good = '1' * 64, '2' * 64
    runtime.q.db = SimpleNamespace(execute=lambda *args:
        SimpleNamespace(fetchall=lambda: [{'id': bad}, {'id': good}]))
    folder = Path(runtime.config['state']) / 'tasks' / good
    folder.mkdir(parents=True)
    (folder / 'packet.json').write_bytes(encoded({'campaign_task': investigator()}))
    (folder / 'scientific-disposition.json').write_bytes(encoded({
        'artifact_sha256': {'round-1/selection.json': 'b' * 64},
        'review_verdict': 'APPROVE', 'source': runtime.config['source']}))
    monkeypatch.setattr(continuing, 'read_reference', lambda *args: encoded(selected))
    orphan = ops._directory(runtime.config) / ('0' * 64); orphan.mkdir(parents=True)
    orphan.parent.chmod(0o700); orphan.chmod(0o700)
    found = ops.discover(runtime)
    assert found['status'] == 'DISCOVERED' and len(found['operations']) == 1
    assert found['blocked_tasks'][0]['task'] == bad
    assert found['blocked_operations'][0]['operation'] == orphan.name
    assert found['blocked_operations'][0]['kind'] is None
    assert list(orphan.iterdir()) == [] and found['models'] == 0


def protocol_finalization(tmp_path):
    """Synthetic seal-byte bookkeeping, not an actual scientific decision."""
    identity = 'a' * 64
    folder = tmp_path / 'continuing-operations' / identity; folder.mkdir(parents=True, mode=0o700)
    output = tmp_path / 'formal-decisions' / identity; (output / 'round-1').mkdir(parents=True)
    decision = output / 'round-1/decision.json'; decision.write_bytes(b'{"synthetic_seal":true}\n')
    sha = hashlib.sha256(decision.read_bytes()).hexdigest()
    (output / 'receipt.json').write_bytes(encoded({'decision': 'round-1/decision.json', 'decision_sha256': sha}))
    (folder / 'prepared.json').write_bytes(encoded({'formal_request': {'subject': 'synthetic-protocol', 'bindings': {}}}))
    saved = {'identity': identity, 'source': 'b' * 40, 'operation': {'kind': 'AUTHORIZE_PROTOCOL', 'inputs': {'artifacts': {}}}}
    result = {'status': 'AGENT_REVIEWED_DECISION_READY', 'decision_path': str(decision)}
    return saved, folder, result, decision, sha


def test_protocol_finalization_derives_actual_sealed_hash_without_optional_result_key(tmp_path):
    saved, folder, result, decision, sha = protocol_finalization(tmp_path)
    finalized = ops._finalize(saved, folder, result)
    assert finalized['result']['protocol']['decision_sha256'] == sha
    assert finalized['result']['protocol']['decision_path'] == str(decision)
    assert finalized['scientific_acceptance'] is False


@pytest.mark.parametrize('change', ['missing', 'changed', 'receipt', 'supplied_hash', 'path'])
def test_protocol_finalization_refuses_missing_or_changed_sealed_original(tmp_path, change):
    saved, folder, result, decision, sha = protocol_finalization(tmp_path)
    if change == 'missing': decision.unlink()
    elif change == 'changed': decision.write_bytes(decision.read_bytes() + b' ')
    elif change == 'receipt': (decision.parent.parent / 'receipt.json').write_bytes(b'{}')
    elif change == 'supplied_hash': result['decision_sha256'] = 'f' * 64
    else: result['decision_path'] = str(tmp_path / 'unrelated.json')
    with pytest.raises(ValueError, match='SEALED_ORIGINAL_MISSING_OR_CHANGED'):
        ops._finalize(saved, folder, result)
    assert not (folder / 'result.json').exists()
