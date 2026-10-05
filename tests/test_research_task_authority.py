"""Synthetic transport tests; no provider call or scientific approval occurs."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

import pytest

from orchestrator import research_task_authority as task_authority
from orchestrator import scientific_authority as authority
from orchestrator.hosted_cycle import encoded
from orchestrator.protected_handover import model_output_format

SOURCE = Path(__file__).resolve().parents[1]


def test_investigator_seal_binds_template_and_checks_reserved_origin_before_admission(setup, monkeypatch):
    """Actual decision serializer with a synthetic protected-origin/provider seam."""
    config, entry, output = setup
    task = {'schema':'investigator-task/v1','task_id':'investigator-'+'a'*64,'experiment':'P002',
        'mode':'investigate','request':'Synthetic current charter selection.','references':[],
        'selected_by':None,'template_sha256':'b'*64,'wake_sha256':'a'*64,'purpose':'CHARTER_SELECTION'}
    entry['request']['task'] = task
    checked=[]
    monkeypatch.setattr('orchestrator.investigator_wakes.verify_entry',lambda *args:checked.append('reserved-origin'))
    monkeypatch.setattr('orchestrator.continuing_research.read_evidence',lambda *args:{'synthetic':'original-evidence'})
    broker=OriginalBroker()
    result=task_authority.execute(config,entry,output,client=broker)
    assert checked==['reserved-origin']
    decision=json.loads((output/result['decision']).read_text())
    assert decision['bindings']['template_sha256']=='b'*64
    assert decision['bindings']['operation_sha256']==task_authority.digest(task)
    assert broker.calls.count('model_stage')==2
    entry['eligibility']=result['eligibility']
    assert task_authority.verify_eligibility(config,entry,client=broker)['status']=='ELIGIBLE'
    entry['request']['task']['template_sha256']='c'*64
    with pytest.raises(ValueError):task_authority.verify_eligibility(config,entry,client=broker)
    bindings=dict(decision['bindings']);bindings['mode']='propose'
    with pytest.raises(ValueError,match='EXACT_REVIEWED_RESEARCH_OPERATION'):
        authority.decision_context(config['source_root'],action='authorize_research_task',subject=task['task_id'],bindings=bindings)


class OriginalBroker:
    """Clearly synthetic provider boundary with immutable original replies."""
    def __init__(self, decision='APPLY', verdict='APPROVE'):
        self.decision = decision
        self.verdict = verdict
        self.originals = {}
        self.calls = []
        self.prompts = []
        self.packets = []

    def __call__(self, socket, operation, body):
        self.calls.append(operation)
        if operation == 'admit_server':
            return {'status': 'ADMITTED', 'duplicate_admission': False}
        stage = body['stage']
        if operation == 'model_stage':
            assert stage not in self.originals, 'Synthetic test refuses duplicate model execution'
            assert model_output_format(body['packet'], stage) == 'json'
            self.prompts.append(body['prompt'])
            self.packets.append(deepcopy(body['packet']))
            if stage == 'continuation':
                value = {'context_sha256': re.search(r'CONTEXT SHA256: ([0-9a-f]{64})', body['prompt'])[1],
                         'decision': self.decision, 'rationale': 'Synthetic bounded preparation judgment.',
                         'transition': {'from': 'PROPOSED', 'to': 'ELIGIBLE' if self.decision == 'APPLY' else 'DEFERRED'},
                         'reconsideration': 'Reassess with a changed installed question or evidence.'}
                name = 'judgment.json'
            else:
                author = json.loads(self.originals['continuation']['answer'])['judgment.json']
                value = {'verdict': self.verdict, 'rationale': 'Synthetic independent review.',
                         'judgment_sha256': hashlib.sha256(author.encode()).hexdigest()}
                name = 'review.json'
            answer = json.dumps({name: json.dumps(value)})
            model = 'claude-fable-5' if stage == 'review' else 'gpt-6-astra'
            receipt = {'requested_model': model, 'actual_model': model if stage == 'review' else None,
                       'model_evidence': 'Synthetic fixture; actual Astra model unreported.',
                       'returncode': 0, 'stage': stage, 'session_id': 'fixture_' + stage,
                       'answer_sha256': hashlib.sha256(answer.encode()).hexdigest(),
                       'operating_context_sha256': 'a' * 64}
            self.originals[stage] = {'status': 'COMPLETE', 'answer': answer, 'receipt': receipt,
                'packet_sha256': hashlib.sha256(encoded(body['packet'])).hexdigest()}
        assert operation in ('model_stage', 'stage_status')
        return {**deepcopy(self.originals[stage]), 'duplicate': operation == 'stage_status'}


@pytest.fixture
def setup(tmp_path, monkeypatch):
    from orchestrator import remote_supervisor, change_requests
    tmp_path.chmod(0o700)
    root = tmp_path / 'source'
    direction = getattr(authority, 'DIRECTION_PATH', 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md')
    for name in (authority.POLICY_PATH, direction):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / name, path)
    monkeypatch.setattr(remote_supervisor, 'checked_source', lambda path, pin: root)
    module = root / 'orchestrator/research_task_authority.py'
    module.parent.mkdir(parents=True, exist_ok=True)
    # This fixture deliberately omits hosted policy/input receipts; keep its legacy wire profile.
    # The current source presentation and exact receipt recovery have dedicated tests.
    module.write_text((SOURCE / 'orchestrator/research_task_authority.py').read_text().replace(
        'HOSTED_PRESENTATION_VERSION = 1\n', ''))
    module.with_name('hosted_context.py').write_text('"""Synthetic original-only hosted source; no outer document view."""\n')
    from orchestrator import hosted_context
    monkeypatch.setattr(hosted_context, 'build', lambda root, state: {'task_state': state,
        'fixture_scope': 'Synthetic transport fixture; complete envelope coverage is checked separately.'})
    evidence_file = tmp_path / 'evidence.json'
    evidence_file.write_text('{"status":"SYNTHETIC_TEST_EVIDENCE_ONLY"}\n')
    sha = hashlib.sha256(evidence_file.read_bytes()).hexdigest()
    def configuration(path, **kw):
        assert path == str(evidence_file)
        assert kw['expected_sha256'] == hashlib.sha256(evidence_file.read_bytes()).hexdigest()
        return json.loads(evidence_file.read_text())
    monkeypatch.setattr(task_authority, 'configuration', configuration)
    monkeypatch.setattr(change_requests, 'load', lambda folder: {
        'request': {'identity': 'c' * 64},
        'events': [{'event': 'APPLIED', 'identity': 'd' * 64}], 'head_sha256': 'e' * 64})
    config = {'source': 'b' * 40, 'source_root': str(root), 'controller_gid': 1000,
              'controller_uid': os.getuid(), 'state': str(tmp_path / 'state'),
              'broker_socket': 'synthetic-test-socket', 'change_request_store': str(tmp_path / 'changes')}
    from orchestrator.handover_coordinator import Coordinator
    coordinator = Coordinator(config['state'], {}, None)
    coordinator.db.close()
    entry = {'schema': 'installed-research-catalog-entry/v1', **{k: config[k] for k in ('source', 'source_root')},
             'request': {'task': {'task_id': 'finite-p001-discussion-v1', 'mode': 'discuss',
                                 'request': 'Discuss only the retained preparation evidence.'},
                         'evidence_file': str(evidence_file), 'evidence_sha256': sha, 'day': '2026-09-10',
                         'initiator': {'kind': 'human', 'identity': 'synthetic-test-operator'}},
             'eligibility': {'path': str(tmp_path / 'decision/round-1/decision.json'), 'sha256': '0' * 64},
             'predecessors': [], 'change_request': {'request_id': 'c' * 64, 'applied_event': 'd' * 64}}
    return config, entry, tmp_path / 'decision'


def run(setup, broker=None):
    config, entry, output = setup
    broker = broker or OriginalBroker()
    result = task_authority.execute(config, entry, output, client=broker)
    entry['eligibility'] = result['eligibility']
    return config, entry, output, broker, result


def test_actual_boundary_contract_and_completed_recovery_keep_attribution(setup):
    config, entry, output, broker, first = run(setup)
    checked = task_authority.verify_eligibility(config, entry, client=broker)
    assert checked['status'] == 'ELIGIBLE' and checked['review_status'] == 'APPROVE'
    assert checked['actor']['model'] == checked['actor']['requested_model'] == 'gpt-6-astra'
    assert checked['actor']['actual_model'] is None
    assert checked['actor']['session_id'] == 'fixture_continuation'
    assert checked['actor']['session_id_source'] == 'original_provider_receipt'
    assert first['disposition_kind'] == 'EXISTING_REVIEWED_DECISION_SEAL'
    assert not first['catalog_installed'] and not first['research_dispatched']
    originals = {p: p.read_bytes() for p in output.rglob('*') if p.is_file()}
    second = task_authority.execute(config, entry, output, client=broker)
    assert second['new_model_calls'] == 0 and broker.calls.count('model_stage') == 2
    assert broker.calls.count('admit_server') == 1
    assert all(p.read_bytes() == raw for p, raw in originals.items())
    for prompt in broker.prompts:
        assert authority.POLICY_VERSION in prompt
        assert 'authorize_research_task' in prompt and 'same-prompt-hosted-task-reference/v2' in prompt
    for packet in broker.packets:
        assert entry['change_request']['applied_event'] in json.dumps(packet['recorded_changes'])


def test_local_retargeting_cannot_reuse_original_model_authority(setup):
    config, entry, output, broker, _ = run(setup)
    for field, replacement in [('predecessors', [{'task': 'f' * 64, 'source': 'b' * 40,
            'disposition_sha256': 'e' * 64, 'requires': 'DISPOSITION_RECORDED'}]),
            ('change_request', {'request_id': 'c' * 64, 'applied_event': 'f' * 64})]:
        changed = deepcopy(entry)
        changed[field] = replacement
        with pytest.raises(ValueError, match='EXACT_DELEGATED|CONTEXT_CHANGED'):
            task_authority.verify_eligibility(config, changed, client=broker)
    entry['eligibility']['sha256'] = 'f' * 64
    with pytest.raises(ValueError, match='EXACT_DECISION'):
        task_authority.verify_eligibility(config, entry, client=broker)
    assert broker.calls.count('model_stage') == 2


def test_local_fabricated_receipt_does_not_replace_original_provider_reply(setup):
    config, entry, output, broker, _ = run(setup)
    path = output / 'round-1/scientific_decision.provider-receipt.json'
    value = json.loads(path.read_text());value['actual_model'] = 'gpt-6-astra'
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match='ORIGINAL_RECEIPT_CHANGED'):
        task_authority.verify_eligibility(config, entry, client=broker)


def test_even_consistently_resealed_local_judgment_refuses_provider_mismatch(setup):
    config, entry, output, broker, _ = run(setup)
    folder = output / 'round-1'
    judgment = json.loads((folder / 'judgment.json').read_text())
    judgment['rationale'] = 'Fabricated local conclusion in a synthetic tampering test.'
    (folder / 'judgment.json').write_bytes(authority.encoded(judgment))
    review = json.loads((folder / 'review.json').read_text())
    review['judgment_sha256'] = hashlib.sha256((folder / 'judgment.json').read_bytes()).hexdigest()
    (folder / 'review.json').write_bytes(authority.encoded(review))
    decision = json.loads((folder / 'decision.json').read_text())
    decision.update(judgment)
    for key in ('judgment', 'review'):
        decision[key]['sha256'] = hashlib.sha256((folder / (key + '.json')).read_bytes()).hexdigest()
    (folder / 'decision.json').write_bytes(authority.encoded(decision))
    entry['eligibility']['sha256'] = hashlib.sha256((folder / 'decision.json').read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='ORIGINAL_REPLY_MISMATCH'):
        task_authority.verify_eligibility(config, entry, client=broker)


def test_negative_review_never_seals_or_retries(setup):
    config, entry, output = setup
    broker = OriginalBroker(verdict='REVISE')
    with pytest.raises(ValueError, match='REVISION_LIMIT'):
        task_authority.execute(config, entry, output, client=broker)
    assert not (output / 'round-1/decision.json').exists()
    with pytest.raises(ValueError, match='PARTIAL_AUTHORITY_OUTPUT_REQUIRES_EXPLICIT_ORIGINAL_RECOVERY'):
        task_authority.execute(config, entry, output, client=broker)
    assert broker.calls.count('model_stage') == 2
    assert json.loads((output / 'round-1/review.json').read_text())['verdict'] == 'REVISE'


def test_deferral_has_review_but_does_not_become_eligibility(setup):
    config, entry, _, broker, _ = run(setup, OriginalBroker(decision='DEFER'))
    checked = task_authority.verify_eligibility(config, entry, client=broker)
    assert checked['status'] == 'DEFERRED'
    assert checked['review_status'] == 'APPROVE'


def test_lost_local_completion_projects_originals_without_new_models(setup):
    config, entry, original, broker, _ = run(setup)
    (original / 'receipt.json').rename(original / 'retained-lost-receipt.json')
    preserved = {p: p.read_bytes() for p in original.rglob('*') if p.is_file()}
    result = task_authority.execute(config, entry, original.parent / 'projection',
                                    recover_from=original, client=broker)
    assert result['new_model_calls'] == 0 and broker.calls.count('model_stage') == 2
    assert all(p.read_bytes() == raw for p, raw in preserved.items())
    marker = json.loads((original.parent / 'projection/recovery.json').read_text())
    assert not marker['new_review'] and marker['original_preserved']


def test_recovery_preserves_but_refuses_changed_original_request(setup):
    config, entry, original, broker, _ = run(setup)
    path = original / 'request.json'
    request = json.loads(path.read_text());request['request'] = 'Unexpected local edit.'
    path.write_text(json.dumps(request))
    with pytest.raises(ValueError, match='ORIGINAL_REQUEST_CHANGED'):
        task_authority.execute(config, entry, original.parent / 'projection',
                               recover_from=original, client=broker)
    assert json.loads(path.read_text())['request'] == 'Unexpected local edit.'
    assert broker.calls.count('model_stage') == 2


def test_later_change_criticism_does_not_rewrite_or_block_original_recovery(setup, monkeypatch):
    from orchestrator import change_requests
    config, entry, original, broker, _ = run(setup)
    def later_history(folder):
        pytest.fail('Original recovery must not replace historical inputs with current change state')
    monkeypatch.setattr(change_requests, 'load', later_history)
    repeated = task_authority.execute(config, entry, original, client=broker)
    projected = task_authority.execute(config, entry, original.parent / 'projection',
                                       recover_from=original, client=broker)
    assert repeated['new_model_calls'] == projected['new_model_calls'] == 0
    assert broker.calls.count('model_stage') == 2


def test_scope_does_not_expand_to_patient_or_general_actions(setup):
    config, entry, output = setup
    entry['request']['task']['mode'] = 'launch'
    broker = OriginalBroker()
    with pytest.raises(ValueError, match='TASK_CONTRACT'):
        task_authority.execute(config, entry, output, client=broker)
    assert broker.calls == []
    contract = {'version': 1, 'action': 'authorize_research_task', 'experiment': 'P001', 'mode': 'readiness'}
    for stage in ('continuation', 'review'):
        assert model_output_format({'scientific_decision_artifacts': contract}, stage) == 'json'
    with pytest.raises(ValueError, match='TWO_STAGES_AND_SEAL'):
        model_output_format({'scientific_decision_artifacts': contract}, 'disposition')
    for mutation in ({'action': 'launch_p001'}, {'experiment': 'P002'}, {'mode': 'execute'}, {'version': True}):
        with pytest.raises(ValueError, match='FINITE_SCIENTIFIC_DECISION_CONTRACT'):
            model_output_format({'scientific_decision_artifacts': contract | mutation}, 'continuation')


def test_v1_policy_remains_original_and_cannot_authorize_new_action(setup):
    config, entry, _ = setup
    root = Path(config['source_root'])
    path = root / authority.POLICY_PATH
    current = json.loads(path.read_text())
    historical = {k: v for k, v in current.items() if k not in
                  ('research_task_scope', 'methodology_scope', 'runtime_scope')}
    historical['version'] = authority.LEGACY_POLICY_VERSION
    historical['actions'] = sorted(authority.LEGACY_ACTIONS)
    historical['scope'] = authority.LEGACY_SCOPE
    historical['direction_path'] = 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md'
    historical['direction_sha256'] = authority.LEGACY_DIRECTION_SHA
    shutil.copyfile(SOURCE / historical['direction_path'], root / historical['direction_path'])
    path.write_text(json.dumps(historical))
    old = authority.decision_context(root, action='accept_interpretation', subject='idea:047', bindings={})
    assert old['policy']['version'] == authority.LEGACY_POLICY_VERSION
    with pytest.raises(ValueError, match='ACTION_OR_SUBJECT'):
        task_authority._identity(config, entry)
    assert historical == json.loads(path.read_text())


def test_wrong_controller_uid_refuses_before_creating_private_output(setup, monkeypatch):
    config, entry, output = setup
    monkeypatch.setattr(task_authority.os, 'getuid', lambda: config['controller_uid'] + 1)
    broker = OriginalBroker()
    with pytest.raises(ValueError, match='CONTROLLER_IDENTITY'):
        task_authority.execute(config, entry, output, client=broker)
    assert not output.exists() and broker.calls == []


def pause(config):
    from orchestrator.handover_coordinator import Coordinator
    coordinator = Coordinator(config['state'], {}, None)
    try:
        coordinator.control({'id': 'synthetic-pause', 'expected_revision': 0, 'action': 'pause'},
                            authenticated_operator=True)
    finally:
        coordinator.db.close()


def test_saved_pause_blocks_new_admission_before_output_creation(setup):
    config, entry, output = setup
    pause(config)
    broker = OriginalBroker()
    with pytest.raises(ValueError, match='SYSTEM_PAUSED'):
        task_authority.execute(config, entry, output, client=broker)
    assert not output.exists() and broker.calls == []


def test_admitted_turn_can_finish_opposing_review_after_pause(setup):
    config, entry, output = setup
    broker = OriginalBroker()
    def client(socket, operation, body):
        result = broker(socket, operation, body)
        if operation == 'model_stage' and body['stage'] == 'continuation':
            # This obtains the real shared admission lock during model handling;
            # authority must release that lock before waiting on provider output.
            pause(config)
        return result
    result = task_authority.execute(config, entry, output, client=client)
    assert result['status'] == 'AGENT_REVIEWED_DECISION_READY'
    assert broker.calls.count('admit_server') == 1 and broker.calls.count('model_stage') == 2


def test_saved_pause_does_not_block_original_read_only_recovery(setup):
    config, entry, original, broker, _ = run(setup)
    pause(config)
    repeated = task_authority.execute(config, entry, original, client=broker)
    recovered = task_authority.execute(config, entry, original.parent / 'paused-projection',
                                       recover_from=original, client=broker)
    assert repeated['new_model_calls'] == recovered['new_model_calls'] == 0
    assert broker.calls.count('admit_server') == 1 and broker.calls.count('model_stage') == 2


def test_shared_writer_and_admission_refusal_prevent_a_new_authority_turn(setup):
    import fcntl
    config, entry, output = setup
    broker = OriginalBroker()
    with (Path(config['state']) / 'branch.lock').open('a') as writer:
        fcntl.flock(writer, fcntl.LOCK_EX)
        with pytest.raises(ValueError, match='CONTROLLER_WRITER_BUSY'):
            task_authority.execute(config, entry, output, client=broker)
    assert not output.exists() and broker.calls == []
    def halted(socket, operation, body):
        assert operation == 'admit_server'
        return {'status': 'HALTED_OPERATOR_RESET_REQUIRED'}
    with pytest.raises(ValueError, match='ADMISSION_BLOCKED'):
        task_authority.execute(config, entry, output, client=halted)
    assert not output.exists()


def test_interruption_before_first_provider_stage_requires_explicit_recovery(setup):
    config, entry, output = setup
    output.mkdir(mode=0o700)
    (output/'authority-transport.json').write_text('{}')
    broker=OriginalBroker()
    with pytest.raises(ValueError,match='PARTIAL_AUTHORITY_OUTPUT_REQUIRES_EXPLICIT_ORIGINAL_RECOVERY'):
        task_authority.execute(config,entry,output,client=broker)
    assert broker.calls == []
    assert (output/'authority-transport.json').read_text() == '{}'


def test_eligibility_reports_original_byte_verified_opposing_verdict(setup):
    config, entry, output, broker, _ = run(setup)
    reviewed=json.loads((output/'round-1/review.json').read_text())
    proof=task_authority.verify_eligibility(config,entry,client=broker)
    assert proof['review_status'] == reviewed['verdict'] == 'APPROVE'
    assert broker.calls.count('model_stage') == 2
