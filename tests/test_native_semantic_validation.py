"""Synthetic process fixtures, not scientific or live confinement evidence."""
from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from test_linux_scientific_jobs import LinuxScientificJobs
from orchestrator import linux_scientific_jobs as jobs
from orchestrator import scientific_validation as validation
from orchestrator import scientific_job_results as results

REAL_VERIFY_LAUNCH = validation.verify_launch_authority


@pytest.fixture
def harness():
    case = LinuxScientificJobs(methodName='run_fixture')
    case.setUp()
    def fixture_launch(config, binding, path, *, original_client):
        request = validation.decision_request(binding)
        return {'path': str(Path(path).absolute()), 'decision_sha256': '9'*64,
            'actor': {'synthetic_fixture': True}, 'policy': {'synthetic_fixture': True},
            'job_core_sha256': request['bindings']['job_core_sha256']}
    try:
        with patch.object(validation, 'verify_launch_authority', side_effect=fixture_launch):
            yield case
    finally:
        case.doCleanups()


def install_validator(h, *, status='VALID', defect=None, declared=True):
    policy = json.loads((h.workspace/(h.prefix+'publication.json')).read_text())
    if declared:
        policy['semantic_validation_interface'] = deepcopy(validation.INTERFACE)
    validator = """import argparse,json
from pathlib import Path
p=argparse.ArgumentParser()
for name in ('result-dir','data-root','settings','binding','output'):
    p.add_argument('--'+name,required=True)
a=p.parse_args()
binding=json.loads(Path(a.binding).read_text())
assert (Path(a.result_dir)/'value.txt').read_text()=='6'
value={'schema':'scientific-semantic-validation-output/v1','binding':binding,
       'status':STATUS,'reason':'Synthetic plumbing fixture only.','diagnostics':[]}
if DEFECT=='binding':value['binding']['completion']='e'*64
if DEFECT=='extra':value['authority']='APPROVE'
if DEFECT=='large':value['reason']='x'*31000
if DEFECT=='malformed':
    Path(a.output).write_text('{')
else:
    Path(a.output).write_text(json.dumps(value))
""".replace('STATUS', repr(status)).replace('DEFECT', repr(defect))
    for name, body in [('publication.json', json.dumps(policy)), ('validate_return.py', validator)]:
        relative = h.prefix+name
        (h.workspace/relative).write_text(body)
        h.core['files'][relative] = jobs.digest(body.encode())


def validator_calls(process):
    return [call for call in process.call_args_list
            if any(str(arg).endswith('/validate_return.py') for arg in call.args[0])]


def completed_experiment(h):
    request, receipt = h.run_fixture()
    assert receipt['status'] == 'COMPLETE'
    event = h.registry.observe()[0]
    return request, event['event']


def dispatch_validation(h, completion):
    with patch.object(jobs.os, 'getuid', return_value=0):
        registered = validation.register(h.registry, completion, h.base/'validation/round-1/decision.json', original_client=object())
        dispatched = h.registry.dispatch(registered['job'], original_client=object())
    return registered, dispatched


def exported(h, completion):
    with patch.object(jobs.os, 'getuid', return_value=0):
        return validation.export_result(h.registry, completion, original_client=object())


@pytest.mark.parametrize('status', ['VALID', 'INVALID', 'DEFER'])
def test_real_worker_and_original_reader_preserve_separate_semantics(harness, status):
    h = harness
    install_validator(h, status=status)
    original, completion = completed_experiment(h)
    original_folder = Path(h.config['outputs'])/original['attempt']
    preserved = {str(p.relative_to(original_folder)):p.read_bytes()
                 for p in original_folder.rglob('*') if p.is_file()}
    registered, attempt = dispatch_validation(h, completion)
    assert attempt['attempt'] != original['attempt']
    assert registered['scientific_acceptance'] is False
    receipt = jobs.run_worker(h.config, attempt['attempt'])
    assert receipt['status'] == 'COMPLETE'
    assert receipt['scientific_acceptance'] is False
    observed = h.registry.observe()
    assert len(observed) == 1  # Only the original experiment completion is published.
    assert observed[0]['event'] == completion
    value = exported(h, completion)
    with patch.object(jobs.os, 'getuid', return_value=0):
        imported = results.export_result(h.registry, completion, original_client=object())
    checked = results.checked_semantic_result(value, imported)
    assert checked['output']['status'] == status
    assert checked['scientific_acceptance'] is False
    assert checked['adoption'] is False
    assert {str(p.relative_to(original_folder)):p.read_bytes()
            for p in original_folder.rglob('*') if p.is_file()} == preserved


def test_reconciliation_does_not_launch_or_create_another_attempt(harness):
    h = harness
    install_validator(h)
    _, completion = completed_experiment(h)
    registered, attempt = dispatch_validation(h, completion)
    with patch.object(jobs.subprocess, 'Popen', wraps=jobs.subprocess.Popen) as process:
        outcome = jobs.run_worker(h.config, attempt['attempt'])
        assert jobs.run_worker(h.config, attempt['attempt']) == outcome
        first = exported(h, completion)
        assert exported(h, completion) == first
        h.registry.observe()
        _, repeated = dispatch_validation(h, completion)
        assert repeated['attempt'] == attempt['attempt']
        assert repeated['automatic_restart'] is False
        assert len(validator_calls(process)) == 1
    assert h.registry.db.execute('SELECT count(*) FROM scientific_attempts').fetchone()[0] == 2


def test_undeclared_old_validator_cannot_acquire_new_execution_authority(harness):
    h = harness
    install_validator(h, declared=False)
    _, completion = completed_experiment(h)
    with patch.object(jobs.os, 'getuid', return_value=0):
        with pytest.raises(ValueError, match='REVIEWED_INTERFACE_REQUIRED'):
            validation.register(h.registry, completion, h.base/'validation/round-1/decision.json', original_client=object())
    assert h.registry.db.execute('SELECT count(*) FROM scientific_attempts').fetchone()[0] == 1


@pytest.mark.parametrize('defect', ['binding', 'extra', 'large', 'malformed'])
def test_exit_zero_with_invalid_semantic_output_is_failed_not_accepted(harness, defect):
    h = harness
    install_validator(h, defect=defect)
    _, completion = completed_experiment(h)
    _, attempt = dispatch_validation(h, completion)
    outcome = jobs.run_worker(h.config, attempt['attempt'])
    assert outcome['exit_code'] == 0
    assert outcome['status'] == 'FAILED'
    assert outcome['reason'] == 'SEMANTIC_VALIDATION_FAILED'
    h.registry.observe()
    with pytest.raises(ValueError, match='FAILED_NO_RETRY'):
        exported(h, completion)
    with patch.object(jobs.subprocess, 'Popen', wraps=jobs.subprocess.Popen) as process:
        assert jobs.run_worker(h.config, attempt['attempt']) == outcome
        assert validator_calls(process) == []


def test_original_result_drift_before_validation_cannot_be_accepted(harness):
    h = harness
    install_validator(h)
    original, completion = completed_experiment(h)
    _, attempt = dispatch_validation(h, completion)
    (Path(h.config['outputs'])/original['attempt']/'artifacts/result/value.txt').write_text('changed')
    with patch.object(jobs.subprocess, 'Popen', wraps=jobs.subprocess.Popen) as process:
        outcome = jobs.run_worker(h.config, attempt['attempt'])
        assert validator_calls(process) == []
    assert outcome['status'] == 'FAILED'
    with pytest.raises(ValueError, match='LINUX_JOB_RESULT_CHANGED'):
        exported(h, completion)


def test_lost_started_validator_is_not_rerun(harness):
    h = harness
    install_validator(h)
    _, completion = completed_experiment(h)
    _, attempt = dispatch_validation(h, completion)
    folder = Path(h.config['outputs'])/attempt['attempt']
    (folder/'started.json').write_text('{}')
    with patch.object(jobs.subprocess, 'Popen', wraps=jobs.subprocess.Popen) as process:
        with pytest.raises(ValueError, match='UNCERTAIN_ORIGINAL_NO_RESTART'):
            jobs.run_worker(h.config, attempt['attempt'])
        assert validator_calls(process) == []
    h.registry.observe()
    assert h.registry.get(validation.job_id(completion))['status'] == 'RUNNING'
    assert h.registry.status()['attempts'][-1]['status'] == 'STARTED_OR_UNCERTAIN'


def test_bound_context_and_interface_drift_refuse_before_process(harness):
    h = harness
    install_validator(h)
    _, completion = completed_experiment(h)
    _, attempt = dispatch_validation(h, completion)
    context = validation.binding_path(h.config, attempt['attempt'])
    context.write_text('{}')
    with patch.object(jobs.subprocess, 'Popen', wraps=jobs.subprocess.Popen) as process:
        outcome = jobs.run_worker(h.config, attempt['attempt'])
        assert validator_calls(process) == []
    assert outcome['status'] == 'FAILED'


def test_reader_does_not_dispatch_missing_validation(harness):
    h = harness
    install_validator(h)
    _, completion = completed_experiment(h)
    with patch.object(jobs.subprocess, 'Popen', wraps=jobs.subprocess.Popen) as process:
        with pytest.raises(ValueError, match='ORIGINAL_ATTEMPT_REQUIRED'):
            exported(h, completion)
        assert validator_calls(process) == []
    assert h.registry.db.execute('SELECT count(*) FROM scientific_attempts').fetchone()[0] == 1

def test_native_reader_to_controller_import_preserves_exact_once_receipt(harness):
    h = harness
    install_validator(h, status='DEFER')
    _, completion = completed_experiment(h)
    _, attempt = dispatch_validation(h, completion)
    assert jobs.run_worker(h.config, attempt['attempt'])['status'] == 'COMPLETE'
    state = h.base/'controller'
    state.mkdir(mode=0o700)
    config = {'state': str(state), 'controller_uid': h.real_uid, 'broker_socket': 'fixture'}
    calls = []
    def original_client(socket, operation, body):
        calls.append(operation)
        with patch.object(jobs.os, 'getuid', return_value=0):
            if operation == 'scientific_job_result':
                return results.export_result(h.registry, body['completion'], original_client=object())
            if operation == 'scientific_validation_result':
                return validation.export_result(h.registry, body['completion'], original_client=object())
        raise AssertionError(operation)
    by = {'kind':'human', 'identity':'synthetic-test-operator'}
    first = results.import_semantic_validation(config, completion=completion, original_client=original_client, by=by)
    folder = state/'scientific-results'/completion/'semantic-validation'
    original_bytes = {p.name:p.read_bytes() for p in folder.iterdir() if p.is_file()}
    other = {'kind':'agent', 'family':'codex', 'model':'synthetic-fixture', 'session_id':'fixture'}
    second = results.import_semantic_validation(config, completion=completion, original_client=original_client, by=other)
    assert first['duplicate'] is False and second['duplicate'] is True
    assert first['validator_status'] == 'DEFER'
    assert second['formal_decision_status'] == 'PENDING'
    assert second['applied_by'] == by
    assert second['scientific_acceptance'] is False and second['adoption'] is False
    assert {p.name:p.read_bytes() for p in folder.iterdir() if p.is_file()} == original_bytes
    assert calls == ['scientific_job_result', 'scientific_validation_result'] * 2

@pytest.mark.parametrize('decision', ['APPLY', 'DEFER'])
def test_distinct_native_formal_launch_requirement(harness, decision):
    h = harness
    install_validator(h)
    _, completion = completed_experiment(h)
    with patch.object(jobs.os, 'getuid', return_value=0):
        binding = validation.execution_binding(h.registry, completion, original_client=object())
    expected = validation.decision_request(binding)
    assert expected['subject'] != h.core['job_id']
    assert expected['bindings']['job_core_sha256'] != jobs.digest(jobs.encoded(h.core))
    assert expected['bindings']['code_sha256'] == h.core['files'][h.prefix+'validate_return.py']
    with patch('orchestrator.formal_decisions.verify_original_decision', return_value={
            'decision':decision, '_decision_sha256':'9'*64, 'actor':{}, 'policy':{}}) as verify:
        if decision == 'APPLY':
            result = REAL_VERIFY_LAUNCH(h.config, binding, h.base/'validation/round-1/decision.json',
                                       original_client=object())
            assert result['job_core_sha256'] == expected['bindings']['job_core_sha256']
        else:
            with pytest.raises(ValueError, match='LAUNCH_DEFERRED'):
                REAL_VERIFY_LAUNCH(h.config, binding, h.base/'validation/round-1/decision.json',
                                   original_client=object())
        assert verify.call_args.kwargs['bindings'] == expected['bindings']
        assert verify.call_args.kwargs['expected_transition'] == jobs.TRANSITION
        assert verify.call_args.kwargs['source'] == h.config['source']


def test_missing_or_revoked_validation_authority_prevents_dispatch(harness):
    h = harness
    install_validator(h)
    _, completion = completed_experiment(h)
    with patch.object(jobs.os, 'getuid', return_value=0):
        with patch.object(validation, 'verify_launch_authority', side_effect=ValueError('NO_CURRENT_VALIDATION_AUTHORITY')):
            with pytest.raises(ValueError, match='NO_CURRENT_VALIDATION_AUTHORITY'):
                validation.register(h.registry, completion, h.base/'validation/round-1/decision.json',
                                    original_client=object())
        registered = validation.register(h.registry, completion, h.base/'validation/round-1/decision.json',
                                         original_client=object())
        with patch.object(validation, 'verify_launch_authority', side_effect=ValueError('NO_CURRENT_VALIDATION_AUTHORITY')):
            with pytest.raises(ValueError, match='NO_CURRENT_VALIDATION_AUTHORITY'):
                h.registry.dispatch(registered['job'], original_client=object())
    assert h.registry.db.execute('SELECT count(*) FROM scientific_attempts').fetchone()[0] == 1

def test_formal_input_uses_one_authenticated_capture_and_changed_binding_refuses(harness):
    h = harness
    install_validator(h)
    _, completion = completed_experiment(h)
    with patch.object(jobs.os, 'getuid', return_value=0):
        with patch.object(results, 'export_result', wraps=results.export_result) as original:
            specification = validation.launch_specification(h.registry, completion, original_client=object())
            assert original.call_count == 1
    checked = validation.checked_launch_specification(specification, h.config['source'], completion)
    assert checked['subject'] == validation.job_id(completion)
    assert 'validate_return.py' in checked['evidence']['original-completed-result.json']
    assert checked['bindings']['code_sha256'] == h.core['files'][h.prefix+'validate_return.py']
    changed = deepcopy(specification)
    changed['decision_request']['bindings']['code_sha256'] = 'e'*64
    with pytest.raises(ValueError, match='PROTECTED_SPECIFICATION_CHANGED'):
        validation.checked_launch_specification(changed, h.config['source'], completion)

def test_investigator_receives_authenticated_validator_reason_not_only_a_hash(harness, monkeypatch):
    from orchestrator import investigator_wakes as wakes, continuing_operations as ops
    from orchestrator.hosted_cycle import encoded
    h = harness
    install_validator(h, status='DEFER')
    _, completion = completed_experiment(h)
    _, attempt = dispatch_validation(h, completion)
    assert jobs.run_worker(h.config, attempt['attempt'])['status'] == 'COMPLETE'
    with patch.object(jobs.os, 'getuid', return_value=0):
        original = results.export_result(h.registry, completion, original_client=object())
    response = exported(h, completion)
    checked = results.checked_semantic_result(response, original)
    value = {'completion':completion,'original_import_sha256':jobs.digest(encoded(original)),
        'response_sha256':checked['response_sha256'],'output_sha256':checked['output_sha256'],
        'attempt':response['attempt'],'outcome_sha256':response['outcome_sha256'],
        'binding':checked['output']['binding'],'validator_status':'DEFER','scientific_acceptance':False,
        'adoption':False,'formal_decision_status':'PENDING','model_calls':0}
    operation = {'schema':ops.SCHEMA,'operation_id':'fixture-validation','kind':'VALIDATE_RESULT',
                 'inputs':{'completion':completion}}
    saved = {'operation':operation,'selected_by':{'task':'a'*64}}
    chosen = {'status':'PROPOSE','successor':operation}
    monkeypatch.setattr(ops,'read_operation_result',lambda *args,**kwargs:{'kind':'VALIDATE_RESULT','result':value})
    monkeypatch.setattr(ops,'_saved',lambda *args:saved)
    monkeypatch.setattr(wakes,'_task',lambda *args,**kwargs:{
        'disposition':{'acceptance_status':'APPROVED_PROPOSAL_ONLY'},'packet':{'campaign_task':{'references':[]}}})
    monkeypatch.setattr('orchestrator.continuing_research.selection',lambda *args,**kwargs:chosen)
    monkeypatch.setattr('orchestrator.continuing_research.read_reference',lambda *args:json.dumps(chosen).encode())
    def client(socket, op, body):
        assert body == {'completion':completion}
        return original if op=='scientific_job_result' else response
    ref={'operation':'b'*64,'result_sha256':'c'*64}
    observed=wakes._operation({'state':str(h.base)},ref,client)
    assert observed['operation']['semantic_validation']==checked['output']
    assert observed['operation']['semantic_validation']['reason']=='Synthetic plumbing fixture only.'
    assert observed['operation']['result']['formal_decision_status']=='PENDING'
    value['output_sha256']='d'*64
    with pytest.raises(ValueError,match='VALIDATION_ORIGINAL_CHANGED'):
        wakes._operation({'state':str(h.base)},ref,client)
