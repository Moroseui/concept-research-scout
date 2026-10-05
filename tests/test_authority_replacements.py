"""Synthetic providers only: immutable invalid originals and a fresh authority."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator import authority_replacements as replacement
from orchestrator import continuing_operations as ops, continuing_research as research
from orchestrator import handover_runtime as runtime_module, research_task_authority as task_authority
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded
from orchestrator.operations_report import private_root
from test_research_task_authority import OriginalBroker, setup


class InvalidBroker(OriginalBroker):
    def __call__(self, socket, operation, body):
        if operation == 'stage_status' and body['stage'] == 'review':
            self.calls.append(operation)
            return {'status': 'NOT_STARTED_RECONCILIATION_REQUIRED'}
        result = super().__call__(socket, operation, body)
        if operation == 'model_stage':
            outer = json.loads(result['answer'])
            judgment = json.loads(outer['judgment.json'])
            judgment['context_sha256'] = judgment['context_sha256'][:-1]
            outer['judgment.json'] = json.dumps(judgment)
            result['answer'] = json.dumps(outer)
            result['receipt']['answer_sha256'] = hashlib.sha256(result['answer'].encode()).hexdigest()
            self.originals['continuation'] = deepcopy(result)
        return result


@pytest.fixture
def case(setup, monkeypatch):
    config, entry, _ = setup
    # Synthetic authority boundary: input composition has independent tests.
    monkeypatch.setattr(task_authority, 'preflight', lambda *a, **kw: {'provider_calls':0,'admissions':0}, raising=False)
    monkeypatch.setattr(task_authority, 'evidence_for_packet',
        lambda root, packet, source: {'installed-request-and-evidence.json':json.dumps(packet,sort_keys=True)}, raising=False)
    from orchestrator import change_requests
    from orchestrator.handover_coordinator import Coordinator
    state = Path(config['state'])
    config['continuing_operations'] = {'enabled': True}
    old_source = config['source']
    by = {'kind': 'human', 'identity': 'synthetic-test-operator'}
    task_id = 'synthetic-comparison-discussion-v1'
    selection = {'task': 'f' * 64, 'artifact': 'round-1/selection.json', 'sha256': '1' * 64}
    predecessor = {'task': selection['task'], 'source': old_source,
                   'disposition_sha256': '2' * 64, 'requires': 'APPROVED_PROPOSAL_ONLY'}
    task = {'schema': research.TASK_SCHEMA, 'task_id': task_id, 'experiment': 'P001',
            'mode': 'discuss', 'request': 'Synthetic comparison discussion only.',
            'references': [], 'selected_by': selection}
    selected = {'status': 'PROPOSED_PENDING_ELIGIBILITY', 'task': task}
    operation = {'schema': ops.SCHEMA, 'operation_id': task_id, 'kind': 'AUTHORIZE_TASK',
                 'inputs': {'selection': selection}}
    core = {'source': old_source, 'operation': operation, 'selected_by': selection,
            'predecessor': predecessor, 'actor': by, 'change_request': entry['change_request']}
    identity = digest(core)
    saved = {**core, 'identity': identity, 'created_at_utc': '2026-09-12T00:00:00+00:00'}
    folder = private_root(private_root(state / 'continuing-operations') / identity)
    (folder / 'request.json').write_bytes(encoded(saved))
    evidence = research.preserve_evidence(config, {'selected_operation': saved,
        'original_selection': {'task': task}, 'prior_packet_evidence': {'unknown_science': 'UNAVAILABLE'}})
    entry['request'].update(task=task, **evidence)
    entry['predecessors'] = [predecessor]
    entry['eligibility']['path'] = str(folder / 'authority/round-1/decision.json')
    prepared = {'entry': entry}
    (folder / 'prepared.json').write_bytes(encoded(prepared))
    (folder / 'started-0.json').write_bytes(encoded({'operation': identity, 'position': 0,
        'step': 'AUTHORITY', 'prepared_sha256': hashlib.sha256(encoded(prepared)).hexdigest()}))
    broker = InvalidBroker()
    with pytest.raises(ValueError, match=replacement.FAILURE):
        task_authority.execute(config, entry, folder / 'authority', client=broker)
    (folder / 'failure-0.json').write_bytes(encoded({'status': 'PRESERVED_ATTEMPT_REQUIRES_RECONCILIATION',
        'exception': 'ValueError', 'reason': replacement.FAILURE, 'automatic_retry': False}))
    original = {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file()}
    config['source'] = 'a' * 40
    history = {'request': {'identity': 'c' * 64}, 'head_sha256': 'e' * 64,
        'events': [{'event': 'APPLIED', 'identity': 'd' * 64,
                    'payload': {'result_binding': {'source': config['source']}}},
                   {'event': 'REVIEW', 'identity': '3' * 64,
                    'payload': {'applied_event': 'd' * 64, 'verdict': 'APPROVE',
                                'review_evidence': 'Synthetic exact corrective implementation review; no science accepted.'}}]}
    monkeypatch.setattr(change_requests, 'load', lambda folder: deepcopy(history))
    monkeypatch.setattr(research, 'selected_successor', lambda *a, **kw: deepcopy(selected))
    monkeypatch.setattr(research, 'read_reference', lambda *a: encoded({'synthetic_selection': task}))
    monkeypatch.setattr(ops, '_predecessor', lambda *a, **kw: (deepcopy(predecessor), {}))
    catalog = {}
    monkeypatch.setattr('orchestrator.research_catalog.paths', lambda config: catalog)
    monkeypatch.setattr('orchestrator.campaign.require_no_human_stop', lambda *a: None)
    q = Coordinator(state, {}, None)
    q.db.execute('CREATE TABLE research_submissions(task_id TEXT PRIMARY KEY,request_identity TEXT,task TEXT)')
    runtime = SimpleNamespace(config=config, q=q, state=state, research_predecessors=lambda entry: None,
                              deployment_status=lambda: {'status': 'SYNTHETIC_REVIEW_PROOF'})
    fresh = OriginalBroker()
    old_event = json.loads((folder / 'authority/authority-transport.json').read_text())['event']
    def client(socket, operation, body):
        if body.get('event', body) == old_event:
            return broker(socket, operation, body)
        return fresh(socket, operation, body)
    monkeypatch.setattr(ops, '_client', lambda runtime: client)
    return SimpleNamespace(runtime=runtime, identity=identity, folder=folder, old_source=old_source,
        broker=broker, fresh=fresh, client=client, original=original, selected=selected, entry=entry,
        by=by, history=history, catalog=catalog, task_id=task_id)


def request(case, **changes):
    return replacement.request(case.runtime, case.identity, **{
        'by': case.by, 'reason': 'Fresh authority after reviewed source repair; old invalid judgment stays invalid.',
        'change_request': {'request_id': 'c' * 64, 'applied_event': 'd' * 64},
        'expected_source': case.runtime.config['source'], **changes})


def preserved(case):
    assert all((case.folder / name).read_bytes() == raw for name, raw in case.original.items())
    assert not (case.folder / 'step-0.json').exists()
    assert not (case.folder / 'result.json').exists()


def test_explicit_request_is_model_free_unique_attributed_and_visible(case):
    before = list(case.broker.calls)
    first = request(case)
    assert first['status'] == 'QUEUED' and first['models'] == first['admissions'] == 0
    assert first['operation'] == case.identity and first['replacement'] == 1
    assert first['requested_by'] == case.by and first['source'] != case.old_source
    assert case.broker.calls[len(before):] == ['stage_status', 'stage_status']
    assert case.fresh.calls == []
    assert request(case)['duplicate'] is True
    with pytest.raises(ValueError, match='ONE_EXPLICIT_REPLACEMENT'):
        request(case, reason='A second request is not another attempt.')
    status = ops.status(case.runtime.config)['operations'][0]
    assert status['status'] == 'RECONCILIATION_REQUIRED'
    assert status['linked_replacement']['request'] == first['request']
    assert len(list(case.folder.glob('replacement-*'))) == 1
    preserved(case)


@pytest.mark.parametrize('change', ['same-source', 'expected-source', 'timeout', 'accepted', 'registered', 'submitted',
                                  'selection', 'provider', 'packet', 'started-review', 'changed-review-source'])
def test_ineligible_originals_never_create_replacement(case, monkeypatch, change):
    if change == 'same-source': case.runtime.config['source'] = case.old_source
    elif change == 'expected-source':
        with pytest.raises(ValueError, match='EXPECTED_CURRENT_SOURCE'):
            request(case, expected_source='e' * 40)
        return
    elif change == 'timeout': case.broker.originals['continuation']['receipt']['returncode'] = -9
    elif change == 'accepted': (case.folder / 'authority/round-1/decision.json').write_text('{}')
    elif change == 'registered': case.catalog[case.task_id] = 'synthetic-catalog'
    elif change == 'submitted': case.runtime.q.db.execute('INSERT INTO research_submissions VALUES(?,?,?)', (case.task_id, 'x', 'y'))
    elif change == 'selection': case.selected['task']['request'] += ' changed'
    elif change == 'provider': case.broker.originals['continuation']['receipt']['session_id'] = 'different_session'
    elif change == 'packet': case.broker.originals['continuation']['packet_sha256'] = 'e' * 64
    elif change == 'started-review':
        prior = case.client
        monkeypatch.setattr(ops, '_client', lambda runtime: lambda s, op, b:
            {'status': 'UNCERTAIN_MODEL_RECONCILE_NO_RETRY'} if b.get('stage') == 'review' else prior(s, op, b))
    elif change == 'changed-review-source': case.history['events'][0]['payload']['result_binding']['source'] = case.old_source
    with pytest.raises(ValueError): request(case)
    assert not (case.folder / replacement.DIRECTORY).exists()
    assert case.fresh.calls == []


def test_both_fresh_roles_receive_invalid_original_and_exact_repair_context(case, monkeypatch):
    request(case)
    submitted = []
    monkeypatch.setattr(research, 'register_and_submit', lambda runtime, entry:
        submitted.append(deepcopy(entry)) or {'registration': {'status': 'REGISTERED'},
        'submission': {'status': 'QUEUED', 'task': '6' * 64}, 'new_model_calls': 0})
    first = replacement.advance(case.runtime)
    assert first['status'] == 'QUEUED' and first['models'] == 2
    assert case.fresh.calls.count('model_stage') == 2 and case.fresh.calls.count('admit_server') == 1
    assert not submitted
    old_judgment = json.loads((case.folder / 'authority/round-1/judgment.json').read_text())
    newfolder = case.folder / replacement.DIRECTORY
    newrequest = json.loads((newfolder / 'authority/request.json').read_text())
    oldrequest = json.loads((case.folder / 'authority/request.json').read_text())
    assert newrequest['context_sha256'] != oldrequest['context_sha256']
    for prompt in case.fresh.prompts:
        assert replacement.FAILURE in prompt and old_judgment['context_sha256'] in prompt
        assert 'Synthetic exact corrective implementation review' in prompt
        assert 'UNAVAILABLE' in prompt and 'DEFER' in prompt
    entry = json.loads((newfolder / 'prepared.json').read_text())['entry']
    assert entry['request']['task'] == case.entry['request']['task']
    assert entry['source'] == case.runtime.config['source']
    assert entry['predecessors'] == case.entry['predecessors']
    evidence = research.read_evidence(case.runtime.config, entry['request'])
    assert evidence['current_reviewed_repair'] == case.history
    assert evidence['preserved_invalid_original']['source'] == case.old_source
    assert replacement.advance(case.runtime)['status'] == 'COMPLETE'
    assert len(submitted) == 1 and submitted[0]['request']['task']['task_id'] == case.task_id
    assert replacement.advance(case.runtime)['status'] == 'NO_REPLACEMENT_WORK'
    assert case.fresh.calls.count('model_stage') == 2
    preserved(case)


def test_fresh_defer_is_reviewed_and_never_registers(case, monkeypatch):
    case.fresh.decision = 'DEFER'
    request(case)
    monkeypatch.setattr(research, 'register_and_submit', lambda *a: pytest.fail('DEFER cannot register'))
    assert replacement.advance(case.runtime)['status'] == 'DEFERRED'
    assert case.fresh.calls.count('model_stage') == 2
    assert replacement.advance(case.runtime)['status'] == 'NO_REPLACEMENT_WORK'
    preserved(case)


def test_pause_late_criticism_and_changed_original_block_before_admission(case):
    request(case)
    case.runtime.q.db.execute('UPDATE controls SET paused=1')
    assert replacement.advance(case.runtime)['status'] == 'PAUSED'
    case.runtime.q.db.execute('UPDATE controls SET paused=0')
    case.history['events'].append({'event': 'REVIEW', 'identity': '4' * 64,
        'payload': {'applied_event': 'd' * 64, 'verdict': 'REQUEST_CHANGES'}})
    with pytest.raises(ValueError, match='RESEARCH_CHANGE_REQUIRES_CORRECTION'):
        replacement.advance(case.runtime)
    assert case.fresh.calls == []
    case.history['events'].pop()
    path = case.folder / 'authority/round-1/judgment.json'
    path.write_text(path.read_text() + ' ')
    with pytest.raises(ValueError, match='PROTECTED_AUTHOR_ORIGINAL_CHANGED'):
        replacement.advance(case.runtime)
    assert case.fresh.calls == []


def test_rehashed_arbitrary_entry_cannot_change_scientific_predecessors(case):
    request(case)
    folder = case.folder / replacement.DIRECTORY
    prepared = json.loads((folder / 'prepared.json').read_text())
    prepared['entry']['predecessors'] = []
    raw = encoded(prepared); (folder / 'prepared.json').write_bytes(raw)
    saved = json.loads((folder / 'request.json').read_text())
    saved['prepared_sha256'] = hashlib.sha256(raw).hexdigest()
    saved['identity'] = digest({k: v for k, v in saved.items() if k != 'identity'})
    (folder / 'request.json').write_bytes(encoded(saved))
    with pytest.raises(ValueError, match='CURRENT_ENTRY_CHANGED'):
        replacement.advance(case.runtime)
    assert case.fresh.calls == []


def test_uncertain_new_attempt_is_preserved_and_never_polled_as_retry(case, monkeypatch):
    request(case)
    calls = []
    def fail(*a, **kw):
        calls.append('attempt'); raise TimeoutError('SYNTHETIC_UNCERTAIN')
    monkeypatch.setattr(task_authority, 'execute', fail)
    with pytest.raises(TimeoutError): replacement.advance(case.runtime)
    assert replacement.observed(case.folder)['status'] == 'RECONCILIATION_REQUIRED'
    assert replacement.advance(case.runtime)['status'] == 'NO_REPLACEMENT_WORK'
    assert request(case)['duplicate'] is True and calls == ['attempt']
    preserved(case)


def test_runtime_runs_only_the_replacement_work_item(case, monkeypatch):
    request(case)
    monkeypatch.setattr(ops, 'advance', lambda *a: pytest.fail('No second work item'))
    monkeypatch.setattr('orchestrator.investigator_wakes.advance', lambda *a: pytest.fail('No second work item'))
    result = runtime_module.Runtime.continuing_step(case.runtime)
    assert result['models'] == 2 and case.fresh.calls.count('model_stage') == 2


def test_original_recovery_source_guard_is_unchanged(case):
    with pytest.raises(ValueError, match='HISTORICAL_OPERATION_REQUIRES_ORIGINAL_INSTALLED_CONTEXT'):
        ops.recover(case.runtime, case.identity)
    assert case.fresh.calls == []


def test_known_deferral_finalization_uses_no_second_model_or_registration(case, monkeypatch):
    case.fresh.decision = 'DEFER'
    request(case)
    original_finish = replacement._finish
    monkeypatch.setattr(replacement, '_finish', lambda *a: (_ for _ in ()).throw(OSError('synthetic final marker interruption')))
    with pytest.raises(OSError): replacement.advance(case.runtime)
    assert replacement.observed(case.folder)['status'] == 'FINALIZATION_PENDING'
    monkeypatch.setattr(replacement, '_finish', original_finish)
    monkeypatch.setattr(research, 'register_and_submit', lambda *a: pytest.fail('No registration'))
    assert replacement.advance(case.runtime)['status'] == 'DEFERRED'
    assert case.fresh.calls.count('model_stage') == 2
    preserved(case)


def test_completed_registration_finalization_does_not_reapply_effect(case, monkeypatch):
    request(case)
    replacement.advance(case.runtime)
    registrations = []
    monkeypatch.setattr(research, 'register_and_submit', lambda *a:
        registrations.append('registered') or {'registration': {'status': 'REGISTERED'},
                                              'submission': {'task': '6' * 64}, 'new_model_calls': 0})
    original_finish = replacement._finish
    monkeypatch.setattr(replacement, '_finish', lambda *a: (_ for _ in ()).throw(OSError('synthetic final marker interruption')))
    with pytest.raises(OSError): replacement.advance(case.runtime)
    monkeypatch.setattr(replacement, '_finish', original_finish)
    assert replacement.advance(case.runtime)['status'] == 'COMPLETE'
    assert registrations == ['registered'] and case.fresh.calls.count('model_stage') == 2


def test_protected_reader_distinguishes_never_started_from_uncertain(tmp_path):
    from orchestrator.protected_handover import Broker
    broker = Broker.__new__(Broker)
    broker.config = {'sources': ['a' * 40], 'turn_root': str(tmp_path)}
    event = {'turn_id': 'b' * 64, 'source': 'a' * 40, 'attempt': '1',
             'kind': 'astra_turn', 'branch': 'astra/infrastructure-milestone-record'}
    folder = tmp_path / (event['turn_id'] + '-1'); folder.mkdir()
    (folder / 'binding.json').write_bytes(encoded({'event': event, 'packet_sha256': 'c' * 64}))
    assert broker.stage_status({'event': event, 'stage': 'review'}) == {'status': 'NOT_STARTED_RECONCILIATION_REQUIRED'}
    (folder / 'review.started.json').write_text('{}')
    assert broker.stage_status({'event': event, 'stage': 'review'}) == {'status': 'UNCERTAIN_MODEL_RECONCILE_NO_RETRY'}
    with pytest.raises(ValueError, match='TURN_BINDING_CHANGED'):
        broker.stage_status({'event': {**event, 'kind': 'nightly_review'}, 'stage': 'review'})


def test_fixed_root_control_transport_preserves_reason_identity_and_arguments(case, monkeypatch):
    import pwd
    monkeypatch.setattr(runtime_module.os, 'getuid', lambda: 0)
    monkeypatch.setattr(pwd, 'getpwuid', lambda uid: SimpleNamespace(pw_name='research-controller'))
    monkeypatch.setattr(runtime_module, 'checked_source', lambda *a: Path(case.runtime.config['source_root']))
    commands = []
    monkeypatch.setattr(runtime_module.subprocess, 'run', lambda argv, **kw:
        commands.append((argv, kw)) or SimpleNamespace(stdout=b'{"status":"QUEUED","models":0}'))
    reason = 'Fresh independently reviewed source; keep original output and DEFER available.'
    intent = {'reason': reason, 'expected_source': case.runtime.config['source'],
              'change_request': {'request_id': 'c' * 64, 'applied_event': 'd' * 64}}
    result = runtime_module.controller_command(case.runtime.config, 'operation-replace',
        '/etc/research-system/live-research/controller.json', case.identity, case.by, replacement=intent)
    assert result['models'] == 0
    argv, options = commands[0]
    assert argv[:4] == ['/usr/sbin/runuser', '-u', 'research-controller', '--']
    assert argv[argv.index('--reason') + 1] == reason
    assert argv[argv.index('operation-replace') + 1] == case.identity
    assert json.loads(argv[argv.index('--submitter') + 1]) == case.by
    assert options['timeout'] == 60 and options['capture_output'] and not options.get('shell')
    with pytest.raises(ValueError, match='REPLACEMENT_ARGUMENTS_REQUIRED'):
        runtime_module.controller_command(case.runtime.config, 'status', replacement=intent)
    assert len(commands) == 1


def test_public_cli_requests_and_returns_saved_identity_without_model_inline(case, monkeypatch, capsys):
    import sys
    configpath = Path(case.runtime.config['state']) / 'cli-config.json'
    configpath.write_bytes(encoded(case.runtime.config))
    monkeypatch.setattr(runtime_module, 'configuration', lambda path: case.runtime.config)
    monkeypatch.setattr(runtime_module, 'Runtime', lambda config: case.runtime)
    monkeypatch.setattr(sys, 'argv', ['handover_runtime', '--config', str(configpath),
        'operation-replace', case.identity, '--reason', 'Synthetic explicit replacement',
        '--expected-source', case.runtime.config['source'], '--change-request', 'c' * 64,
        '--applied-event', 'd' * 64, '--submitter', json.dumps(case.by)])
    runtime_module.main()
    result = json.loads(capsys.readouterr().out)
    assert result['operation'] == case.identity and result['status'] == 'QUEUED'
    assert result['requested_by'] == case.by and result['request']
    assert result['models'] == result['admissions'] == 0 and case.fresh.calls == []


def refusal_reply(event, packet):
    """Synthetic protected originals, including literal thread-only stdout."""
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    packet_sha = sha(encoded(packet))
    stdout = json.dumps({'type':'thread.started','thread_id':'synthetic_input_thread'}) + '\n'
    stderr = ('Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 '
              'characters. (code -32602), data: ' +
              json.dumps({'input_error_code':'input_too_large','max_chars':1048576,'actual_chars':1100000},
                         separators=(',',':')) + '\n')
    originals = {
        'binding.json':encoded({'event':event,'packet_sha256':packet_sha}).decode(),
        'continuation.request.json':encoded({'prompt_sha256':'1'*64}).decode(),
        'continuation.started.json':encoded({'stage':'continuation','requested_model':'gpt-6-astra',
            'started_utc':'2026-09-12T00:00:00+00:00'}).decode(),
        'continuation.ended.json':encoded({'returncode':1,'ended_utc':'2026-09-12T00:00:01+00:00'}).decode(),
        'continuation.process-identity.json':encoded({'pid':123,'process_group':123,'boot_id':'synthetic-boot'}).decode(),
        'continuation.stdout':stdout,'continuation.stderr':stderr}
    process={'returncode':1,'stage':'continuation','requested_model':'gpt-6-astra',
        'input_sha256':'2'*64,'operating_context_sha256':'3'*64,
        'stdout_sha256':sha(stdout.encode()),'stderr_sha256':sha(stderr.encode())}
    originals['continuation.process.json']=encoded(process).decode()
    hashes={name:sha(value.encode()) for name,value in originals.items()}
    hashes.update({'packet.json':packet_sha,'continuation.input.md':'2'*64,'continuation.operating-context.json':'3'*64})
    return {'status':'CONCLUSIVE_INPUT_REFUSAL','event':event,'packet':packet,'packet_sha256':packet_sha,
        'originals':originals,'file_sha256':hashes,'input_characters':1100000,
        'active':False,'answer_present':False,'receipt_present':False,'review_present':False,'disposition_present':False}


@pytest.fixture
def second(case, monkeypatch):
    first = request(case)
    first_folder = case.folder / replacement.DIRECTORY
    captured = {}
    old_client = case.client
    def refusing(socket, operation, body):
        if operation == 'model_stage':
            captured['reply'] = refusal_reply(body['event'], body['packet'])
            raise ValueError('MODEL_FAILED_RECONCILE_PRIVATE_EVIDENCE')
        return old_client(socket, operation, body)
    monkeypatch.setattr(ops, '_client', lambda runtime: refusing)
    with pytest.raises(ValueError, match='MODEL_FAILED_RECONCILE'):
        replacement.advance(case.runtime)
    prior_history = deepcopy(case.history)
    prior_source = case.runtime.config['source']
    original = {p.relative_to(case.folder).as_posix():p.read_bytes()
                for p in case.folder.rglob('*') if p.is_file()}
    case.runtime.config['source'] = 'e'*40
    case.history['events'][0]['identity'] = '6'*64
    case.history['events'][0]['payload']['result_binding']['source'] = case.runtime.config['source']
    case.history['events'][1]['payload']['applied_event'] = '6'*64
    case.history['head_sha256'] = '7'*64
    def client(socket, operation, body):
        if operation == 'stage_input_refusal':
            assert body == {'event':captured['reply']['event']}
            return deepcopy(captured['reply'])
        return old_client(socket, operation, body)
    monkeypatch.setattr(ops, '_client', lambda runtime: client)
    return SimpleNamespace(case=case, first=first, folder=first_folder, original=original,
        reply=captured['reply'], prior_history=prior_history, prior_source=prior_source)


def request_second(second, **changes):
    case=second.case
    values={'change_request':{'request_id':'c'*64,'applied_event':'6'*64},'previous_request':second.first['request']}
    values.update(changes)
    return request(case, **values)


def test_fixed_second_keeps_originals_and_current_task_then_normal_authority(second, monkeypatch):
    case=second.case
    saved=request_second(second)
    assert saved['replacement']==2 and saved['status']=='QUEUED'
    folder=case.folder/replacement.SECOND_DIRECTORY
    core=json.loads((folder/'request.json').read_text())
    proof=json.loads((folder/'original-proof.json').read_text())
    assert core['previous_request']==second.first['request']
    assert proof['previous_request']['source']==second.prior_source
    assert 'packet' not in proof['input_refusal']
    assert proof['base_original']['source']==case.old_source
    assert replacement.observed(case.folder)['prior_replacement']['status']=='RECONCILIATION_REQUIRED'
    first_result=replacement.advance(case.runtime)
    assert first_result['replacement']==2 and first_result['position']==1
    calls=[]
    monkeypatch.setattr(research,'register_and_submit',lambda runtime,entry:
        calls.append(deepcopy(entry)) or {'registration':{'status':'REGISTERED'},'new_model_calls':0})
    assert replacement.advance(case.runtime)['status']=='COMPLETE'
    assert calls[0]['request']['task']==case.entry['request']['task']
    assert calls[0]['predecessors']==case.entry['predecessors']
    assert calls[0]['source']==case.runtime.config['source']
    assert request_second(second)['duplicate'] is True
    with pytest.raises(ValueError,match='PREVIOUS_REQUEST_CHANGED'):
        replacement.request(case.runtime,case.identity,by=case.by,reason=core['reason'],
            change_request=core['change_request'],expected_source=core['source'],previous_request=core['identity'])
    assert len(list(case.folder.glob('replacement-*')))==2
    assert all((case.folder/name).read_bytes()==raw for name,raw in second.original.items())


@pytest.mark.parametrize('change',['same-source','wrong-prior','answer','receipt','review','active','stdout-extra',
                                   'stderr-generic','ended-timeout','process-rc','packet','history','registered'])
def test_second_refuses_unproven_input_rejection_before_creating_intent(second, change):
    case=second.case
    if change=='same-source': case.runtime.config['source']=second.prior_source
    elif change=='wrong-prior':
        with pytest.raises(ValueError):request_second(second,previous_request='9'*64)
        return
    elif change in ('answer','receipt','review','active'):
        second.reply[{'answer':'answer_present','receipt':'receipt_present','review':'review_present','active':'active'}[change]]=True
    elif change=='stdout-extra':
        second.reply['originals']['continuation.stdout']+='{"type":"turn.started"}\n'
    elif change=='stderr-generic':
        second.reply['originals']['continuation.stderr']='input_too_large\n'
    elif change=='ended-timeout':
        second.reply['originals']['continuation.ended.json']=encoded({'returncode':-9,'ended_utc':'2026-09-12T00:00:01+00:00'}).decode()
    elif change=='process-rc':
        process=json.loads(second.reply['originals']['continuation.process.json']);process['returncode']=0
        second.reply['originals']['continuation.process.json']=encoded(process).decode()
    elif change=='packet':
        second.reply['packet']=deepcopy(second.reply['packet']);second.reply['packet']['trigger']='altered'
    elif change=='history':
        case.history['events'].append({'event':'REVIEW','identity':'8'*64,'payload':{'applied_event':'6'*64,'verdict':'REQUEST_CHANGES'}})
    elif change=='registered':case.catalog[case.task_id]=Path('synthetic-existing')
    for name,value in second.reply['originals'].items():
        second.reply['file_sha256'][name]=hashlib.sha256(value.encode()).hexdigest()
    with pytest.raises(ValueError):request_second(second)
    assert not (case.folder/replacement.SECOND_DIRECTORY).exists()
    assert case.fresh.calls.count('model_stage')==0


@pytest.mark.parametrize('name',['step-0.json','authority/round-1/judgment.json','authority/round-1/decision.json'])
def test_second_rejects_existing_result_even_with_claimed_broker_refusal(second,name):
    path=second.folder/name;path.parent.mkdir(exist_ok=True,parents=True);path.write_text('{}')
    with pytest.raises(ValueError):request_second(second)
    assert not (second.case.folder/replacement.SECOND_DIRECTORY).exists()


def test_preflight_refusal_preserves_named_failure_without_started_or_admission(second, monkeypatch):
    request_second(second);case=second.case
    def refuse(*a,**kw):raise ValueError('HOSTED_INPUT_PREFLIGHT_TOO_LARGE')
    monkeypatch.setattr(task_authority,'preflight',refuse)
    before=list(case.fresh.calls)
    with pytest.raises(ValueError,match='HOSTED_INPUT_PREFLIGHT'):
        replacement.advance(case.runtime)
    folder=case.folder/replacement.SECOND_DIRECTORY
    assert (folder/'preflight-failure-0.json').exists() and not (folder/'started-0.json').exists()
    assert replacement.observed(case.folder)['status']=='RECONCILIATION_REQUIRED'
    assert replacement.advance(case.runtime)['status']=='NO_REPLACEMENT_WORK'
    assert case.fresh.calls==before
    assert request_second(second)['duplicate'] is True


def test_second_defer_is_terminal_without_registration(second,monkeypatch):
    request_second(second);second.case.fresh.decision='DEFER'
    monkeypatch.setattr(research,'register_and_submit',lambda *a:pytest.fail('No registration for DEFER'))
    assert replacement.advance(second.case.runtime)['status']=='DEFERRED'
    assert replacement.advance(second.case.runtime)['status']=='NO_REPLACEMENT_WORK'
    assert all((second.case.folder/name).read_bytes()==raw for name,raw in second.original.items())


def test_explicit_second_cli_transport_preserves_previous_identity(case,monkeypatch):
    import pwd
    monkeypatch.setattr(runtime_module.os,'getuid',lambda:0)
    monkeypatch.setattr(pwd,'getpwuid',lambda uid:SimpleNamespace(pw_name='research-controller'))
    monkeypatch.setattr(runtime_module,'checked_source',lambda *a:Path(case.runtime.config['source_root']))
    calls=[]
    monkeypatch.setattr(runtime_module.subprocess,'run',lambda argv,**kw:
        calls.append(argv) or SimpleNamespace(stdout=b'{"models":0}'))
    runtime_module.controller_command(case.runtime.config,'operation-replace',
        '/etc/research-system/live-research/controller.json',case.identity,case.by,replacement={
          'reason':'Synthetic fixed second','expected_source':case.runtime.config['source'],
          'change_request':{'request_id':'c'*64,'applied_event':'d'*64},'previous_request':'8'*64})
    assert calls[0][calls[0].index('--previous-request')+1]=='8'*64
