"""Exact-carry schema and unchanged raw-validator regressions; no provider or admission."""
import copy
import json
import os
from pathlib import Path
import shutil

import pytest
from jsonschema import Draft7Validator
from orchestrator import inspection_runner as runner, inspection_review as review
from orchestrator import inspection_runtime as runtime
from test_inspection_review import fixture_manifest, fixture_attempt, events, replace_events
from test_inspection_runner_offline import session, completed

E, H = runner.encoded, runner.sha
FIELDS = ('findings', 'questions', 'remaining_obligations')


def prior_fixture():
    raw, policy = fixture_manifest()
    first = fixture_attempt(raw, policy, status='IN_PROGRESS')
    rows = events(first)
    result = rows[-1]['structured_output']
    for field in FIELDS:
        result[field] = ['Exact '+field+' item: caf?\nline two.']
    replace_events(first, rows)
    previous = review.validate_session(raw, [first])['attempts'][-1]
    second = fixture_attempt(raw, policy, number=2, previous=previous, status='IN_PROGRESS')
    rows = events(second)
    for field in FIELDS:
        rows[-1]['structured_output'][field] = list(previous['result'][field])
    replace_events(second, rows)
    return raw, policy, first, previous, second


def result_of(originals):
    return events(originals)[-1]['structured_output']


def change_result(originals, result):
    rows = events(originals)
    rows[-1]['structured_output'] = result
    replace_events(originals, rows)


def schema_for(raw, previous):
    return runner.result_schema(json.loads(raw), H(raw), attempt=2, previous=previous)


@pytest.mark.parametrize('field', FIELDS)
@pytest.mark.parametrize('mutation', ['missing', 'reworded', 'wrong_field', 'empty_response', 'whitespace_response'])
def test_cli_schema_rejects_dropped_exact_prior_item(field, mutation):
    raw, _, first, previous, second = prior_fixture()
    result = copy.deepcopy(result_of(second))
    original = result[field].pop()
    if mutation == 'reworded':
        result[field].append(original.replace('Exact', 'Summarized'))
    elif mutation == 'wrong_field':
        result[FIELDS[(FIELDS.index(field)+1)%len(FIELDS)]].append(original)
    elif mutation.endswith('response'):
        result['resolved'].append({'field': field, 'original': original,
                                   'response': '' if mutation == 'empty_response' else ' \t\n'})
    assert not Draft7Validator(schema_for(raw, previous)).is_valid(result)
    change_result(second, result)
    # An individual receipt still is not the cumulative qualification authority.
    receipt = review.parse_attempt(raw, second, prior_attempts=[first])
    if mutation.endswith('response'):
        assert receipt['status'] == 'RECONCILIATION_REQUIRED'
    else:
        assert receipt['status'] == 'IN_PROGRESS'
        with pytest.raises(ValueError, match='PRIOR_OBLIGATION_DROPPED'):
            review.validate_session(raw, [first, second])


@pytest.mark.parametrize('mode', ['carry', 'resolve', 'both', 'carry_and_new_paraphrase'])
def test_valid_exact_carry_or_resolution_preserves_existing_host_semantics(mode):
    raw, _, first, previous, second = prior_fixture()
    result = copy.deepcopy(result_of(second))
    for field in FIELDS:
        original = result[field][0]
        if mode in ('resolve', 'both'):
            result['resolved'].append({'field': field, 'original': original,
                                      'response': 'Independent reason tied to this original item.'})
        if mode == 'resolve':
            result[field] = []
        if mode == 'carry_and_new_paraphrase':
            result[field].append('Additional explanation, without replacing the exact original.')
    schema = schema_for(raw, previous)
    Draft7Validator.check_schema(schema)
    assert Draft7Validator(schema).is_valid(result)
    change_result(second, result)
    assert review.validate_session(raw, [first, second])['status'] == 'IN_PROGRESS'


@pytest.mark.parametrize('mutation,reason', [('unbound','UNBOUND_RESOLUTION'),('duplicate','DUPLICATE_RESOLUTION')])
def test_existing_host_remains_authority_for_unbound_and_duplicate_resolutions(mutation, reason):
    raw, _, first, previous, second = prior_fixture()
    result = copy.deepcopy(result_of(second))
    row = {'field':'findings','original': previous['result']['findings'][0], 'response':'A reason.'}
    if mutation == 'unbound':
        row['original'] = 'Not an original predecessor item.'
    result['resolved'] = [row]
    if mutation == 'duplicate':
        result['resolved'].append({**row, 'response':'A second reason for the same pair.'})
    # Carry clauses are supplemental; they do not replace the raw host validator.
    assert Draft7Validator(schema_for(raw, previous)).is_valid(result)
    change_result(second, result)
    if mutation == 'unbound':
        with pytest.raises(ValueError, match=reason): review.validate_session(raw, [first, second])
    else:
        assert review.parse_attempt(raw, second, prior_attempts=[first])['reason'] == reason


@pytest.mark.parametrize('key,value', [('source','b'*40),('manifest_sha256','0'*64),
    ('session_id','22222222-2222-2222-2222-222222222222'),('attempt',2),('status','APPROVE')])
def test_schema_refuses_stale_or_unrelated_predecessor(key, value):
    raw, _, _, previous, _ = prior_fixture()
    previous[key] = value
    with pytest.raises(ValueError, match='PREDECESSOR_BINDING'): schema_for(raw, previous)


def test_first_and_unbound_continuation_schema():
    raw, _, _, previous, second = prior_fixture()
    manifest = json.loads(raw)
    first = runner.result_schema(manifest, H(raw), attempt=1)
    assert first['properties']['resolved']['maxItems'] == 0 and 'allOf' not in first
    with pytest.raises(ValueError, match='PREDECESSOR_BINDING'):
        runner.result_schema(manifest, H(raw), attempt=2)
    with pytest.raises(ValueError, match='UNEXPECTED_PREDECESSOR'):
        runner.result_schema(manifest, H(raw), attempt=1, previous=previous)


def test_runtime_command_transmits_exact_trusted_schema(tmp_path, monkeypatch):
    raw, _, _, previous, _ = prior_fixture()
    (tmp_path/'manifest.json').write_bytes(raw)
    captured = []
    monkeypatch.setattr(runtime, 'command', lambda *a, **k: captured.append(k['json_schema']) or ['synthetic'])
    runner.runtime_command(tmp_path, json.loads(raw), 2, {}, previous=previous)
    assert captured == [schema_for(raw, previous)]
    assert len(captured[0]['dependencies']['schema']['allOf']) == 3


def test_prepared_prompt_and_schema_are_exact_original_bound(tmp_path):
    directory, raw, policy, _ = session(tmp_path)
    runner.prepare_attempt(directory, 'First synthetic question.')
    completed(directory, raw, policy)
    previous = runner.status(directory)['attempts'][-1]
    request = runner.prepare_attempt(directory, 'Continue.', expected_receipt=H(E(previous)))
    assert 'verbatim into the SAME field' in request['prompt']
    assert json.loads(request['prompt'].split('SAVED ORIGINAL-BOUND PROGRESS:\n')[1]) == previous['result']
    schema = schema_for(raw, previous)
    preflight = json.loads((directory/'attempts/002/input-preflight.json').read_bytes())
    assert preflight == runner.input_preflight(request['prompt'], schema)
    assert preflight['schema_sha256'] == H(json.dumps(schema, sort_keys=True).encode())
    assert preflight['provider_constrained_decoding_claim'] is False
    assert not (directory/'attempts/002/intent.json').exists()


def test_cli_value_and_depth_count_includes_containers_scalars_not_names():
    measured = runner.input_preflight('p', {'a': [None, {'long_property_name':'x'*1000}]})
    assert measured['schema_values'] == 5 and measured['schema_depth'] == 3
    assert runner.input_preflight('p', {'longer_key': [None, {'x':'v'}]})['schema_values'] == 5


def test_cli_value_depth_and_host_serialization_bounds(monkeypatch):
    monkeypatch.setattr(runner, 'MAX_SCHEMA_VALUES', 5)
    runner.input_preflight('p', [1, 2, 3, 4])
    with pytest.raises(ValueError, match='CLI_COMPLEXITY_BOUND'):
        runner.input_preflight('p', [1, 2, 3, 4, 5])
    monkeypatch.setattr(runner, 'MAX_SCHEMA_VALUES', 100000)
    monkeypatch.setattr(runner, 'MAX_SCHEMA_DEPTH', 2)
    runner.input_preflight('p', [[0]])
    with pytest.raises(ValueError, match='CLI_COMPLEXITY_BOUND'):
        runner.input_preflight('p', [[[0]]])
    with pytest.raises(ValueError, match='SCHEMA_BYTE_BOUND'):
        runner.input_preflight('p', {'const': 'x'*runner.MAX_SCHEMA_BYTES})
    with pytest.raises(ValueError, match='COMPOSED_PROMPT_TOO_LARGE'):
        runner.input_preflight('x'*256001, {})


def test_actual_argv_exact_schema_and_operating_system_limits(monkeypatch):
    schema = {'const': '?'}
    argv = ['/synthetic', '--max-turns', '8', '--json-schema', json.dumps(schema, sort_keys=True)]
    measured = runner.input_preflight('p', schema, argv=argv)
    assert measured['argv_bytes_including_nuls'] == sum(len(os.fsencode(x))+1 for x in argv)
    assert measured['actual_argv_checked_before_admission']
    for changed in [argv[:-1]+['{}'], argv+['--json-schema','{}'], argv+['bad\0arg']]:
        with pytest.raises(ValueError, match='ARGV_SCHEMA_BINDING'):
            runner.input_preflight('p', schema, argv=changed)
    with pytest.raises(ValueError, match='ARGV_BYTE_BOUND'):
        runner.input_preflight('p', schema, argv=argv+['x'*runner.MAX_ARGV_BYTES])
    real = runner.os.sysconf
    monkeypatch.setattr(runner.os, 'sysconf', lambda name: 1000 if name=='SC_ARG_MAX' else real(name))
    with pytest.raises(ValueError, match='ARGV_BYTE_BOUND'):
        runner.input_preflight('p', schema, argv=argv)


@pytest.mark.parametrize('scope,turns', [
    ('material-deployment', '32'), ('inspection-native-canary/baseline', '8')])
@pytest.mark.parametrize('mutation', ['none', 'wrong', 'missing', 'missing-value', 'duplicate', 'equals'])
def test_actual_argv_iteration_limit_matches_exact_scope(scope,turns,mutation):
    schema = {'type':'object', 'properties':{'scope':{'const':scope}}}
    flags = ['--max-turns', turns]
    if mutation == 'wrong': flags[1] = '8' if turns == '32' else '32'
    elif mutation == 'missing': flags = []
    elif mutation == 'missing-value': flags = ['--max-turns']
    elif mutation == 'duplicate': flags += ['--max-turns', turns]
    elif mutation == 'equals': flags += ['--max-turns='+turns]
    argv = ['/synthetic', '--json-schema', json.dumps(schema, sort_keys=True), *flags]
    if mutation == 'none':
        measured = runner.input_preflight('p', schema, argv=argv)
        assert measured['maximum_native_model_turns'] == int(turns)
        assert measured['actual_argv_checked_before_admission']
    else:
        with pytest.raises(ValueError, match='INSPECTION_ARGV_TURN_BINDING'):
            runner.input_preflight('p', schema, argv=argv)


def run_fixture(tmp_path, monkeypatch, *, drop=False, changed_preflight=False, oversized_argv=False):
    """Real run ordering; only service/bootstrap/confinement/provider are synthetic."""
    from orchestrator import inspection_bootstrap
    directory, raw, policy, _ = session(tmp_path)
    runner.prepare_attempt(directory, 'First.')
    completed(directory, raw, policy)
    previous = runner.status(directory)['attempts'][-1]
    runner.prepare_attempt(directory, 'Second.', expected_receipt=H(E(previous)))
    target = directory/'attempts/002'
    originals = fixture_attempt(raw, policy, number=2, previous=previous, status='IN_PROGRESS')
    if drop:
        rows = events(originals); rows[-1]['structured_output']['findings'] = ['Reworded synthetic finding.']
        replace_events(originals, rows)
    # Real journal original filenames via the existing original fixture adapter.
    scratch = tmp_path/'synthetic-files'
    scratch.mkdir()
    donor, _ = completed(scratch, raw, policy, number=2, previous=previous)
    (directory/'runtime.json').write_bytes(E({'bootstrap_source':json.loads(raw)['source'], 'enabling_files':[]}))
    monkeypatch.setattr(runner.os, 'getuid', lambda:0)
    monkeypatch.setenv('INVOCATION_ID', 'a'*32)
    monkeypatch.setattr(runner, 'ROOT', directory.parent)
    monkeypatch.setattr(runner, 'service_readback', lambda unit:{'synthetic':True})
    monkeypatch.setattr(runner, 'require_service', lambda s:None)
    # Fresh calls require V2 even in this synthetic run-order fixture.
    # Approval validation remains a fixture boundary; no real authority is asserted.
    from orchestrator import review_input_codec as codec
    bootstrap_dir = directory/'bootstrap'
    (bootstrap_dir/'request.json').write_bytes(E({'input_presentation':codec.FORMAT_V2}))
    proof = {'baseline.json': E({'synthetic_run_order_only': True})}
    (bootstrap_dir/'policy-baseline').mkdir(exist_ok=True)
    for name, data in proof.items(): (bootstrap_dir/'policy-baseline'/name).write_bytes(data)
    def read_proof(path):
        assert path == bootstrap_dir/'policy-baseline'
        assert all((path/name).read_bytes() == data for name,data in proof.items())
        return proof
    monkeypatch.setattr(inspection_bootstrap, 'read_policy_baseline', read_proof)
    permit = (directory/'administrative-permit.json').read_bytes()
    expected_context = (directory/'context-original.json').read_bytes()
    synthetic_source = {'synthetic-context.json': expected_context.decode()}
    monkeypatch.setattr(inspection_bootstrap, 'validate_bootstrap',
        lambda *a, **kw:{'private_text':{H(permit):permit}, 'source_text':synthetic_source})
    def exact_synthetic_context(context, source_text):
        # This fixture tests run/carry ordering, not actual policy authorization.
        assert context == expected_context and source_text == synthetic_source
    monkeypatch.setattr(inspection_bootstrap, 'validate_context', exact_synthetic_context)
    monkeypatch.setattr(runner, 'verify_canary', lambda *a:None)
    monkeypatch.setattr(runner.access, 'verify_view', lambda *a:None)
    seen = []
    def command(*a, **kw):
        seen.append(('command', kw['previous']))
        schema = schema_for(raw, previous)
        return ['/synthetic', '--max-turns', '8', '--json-schema', json.dumps(schema,sort_keys=True)] + (['x'*120000] if oversized_argv else [])
    monkeypatch.setattr(runner, 'runtime_command', command)
    def admit(t, m, request, permit):
        seen.append(('admit', None))
        for name in ('admission_event','admission_receipt','admission_policy'):
            (t/(name+'.json')).write_bytes(originals[name])
        return {name:H(originals[name]) for name in ('admission_event','admission_receipt','admission_policy')}
    monkeypatch.setattr(runner, 'admit', admit)
    class Process:
        pid = os.getpid()
        returncode = 0
        def __init__(self, argv, **kw): self.out = kw['stdout']
        def communicate(self, prompt, timeout):
            self.out.write(originals['protocol']); self.out.flush()
            shutil.copytree(donor/'journal', target/'journal')
        def wait(self, **kw): return 0
    monkeypatch.setattr(runner.subprocess, 'Popen', Process)
    monkeypatch.setattr(runner.os, 'killpg', lambda *a:None)
    if changed_preflight:
        preflight = json.loads((target/'input-preflight.json').read_bytes())
        preflight['schema_sha256'] = '0'*64
        (target/'input-preflight.json').chmod(0o600)
        (target/'input-preflight.json').write_bytes(E(preflight))
    return directory, raw, previous, target, seen


def test_run_reports_cumulative_refusal_preserving_individual_receipt(tmp_path, monkeypatch):
    directory, raw, previous, target, seen = run_fixture(tmp_path, monkeypatch, drop=True)
    answer = runner.run(directory, 2)
    assert answer['attempt_status'] == 'IN_PROGRESS'
    assert answer['status'] == answer['session_status'] == 'RECONCILIATION_REQUIRED'
    assert answer['session_reason'] == 'PRIOR_OBLIGATION_DROPPED'
    receipt = json.loads((target/'receipt.json').read_bytes())
    assert receipt['status'] == 'IN_PROGRESS' and H(E(receipt)) == answer['receipt_sha256']
    assert seen[0] == ('command', previous) and seen[1][0] == 'admit'
    assert json.loads((target/'command.json').read_bytes())['input_preflight']['actual_argv_checked_before_admission']
    with pytest.raises(ValueError, match='CANNOT_RESUME'):
        runner.prepare_attempt(directory, 'No revival.', expected_receipt=answer['receipt_sha256'])


@pytest.mark.parametrize('change,reason', [('changed_preflight','PREFLIGHT_CHANGED'),('oversized_argv','ARGV_BYTE_BOUND')])
def test_run_refuses_input_drift_or_argv_bound_before_admission(tmp_path, monkeypatch, change, reason):
    directory, _, _, target, seen = run_fixture(tmp_path, monkeypatch, **{change:True})
    with pytest.raises(ValueError, match=reason): runner.run(directory, 2)
    assert all(name != 'admit' for name, _ in seen)
    assert not (target/'intent.json').exists() and not (target/'admission_event.json').exists()


def test_run_valid_carry_uses_cumulative_status(tmp_path, monkeypatch):
    directory, _, _, target, _ = run_fixture(tmp_path, monkeypatch)
    answer = runner.run(directory, 2)
    assert answer['status'] == answer['session_status'] == answer['attempt_status'] == 'IN_PROGRESS'
    assert answer['session_reason'] is None


def test_run_revalidates_predecessor_before_command_or_admission(tmp_path, monkeypatch):
    directory, _, _, target, seen = run_fixture(tmp_path, monkeypatch)
    path = target/'request.json'
    request = json.loads(path.read_bytes())
    request['previous_receipt_sha256'] = '0'*64
    path.chmod(0o600); path.write_bytes(E(request))
    with pytest.raises(ValueError, match='PRIOR_PROGRESS_CHANGED'):
        runner.run(directory, 2)
    assert seen == [] and not (target/'intent.json').exists()


def test_run_reports_completed_prefix_when_next_attempt_is_prepared_concurrently(tmp_path, monkeypatch):
    directory, _, _, target, _ = run_fixture(tmp_path, monkeypatch)
    original_save = runner.save
    def concurrent_prepare(path, value):
        original_save(path, value)
        if Path(path) == target/'receipt.json':
            # Deterministic interleaving: prepare_attempt has no execution lock.
            runner.prepare_attempt(directory, 'Next synthetic question.', expected_receipt=H(E(value)))
    monkeypatch.setattr(runner, 'save', concurrent_prepare)
    answer = runner.run(directory, 2)
    assert answer['status'] == answer['session_status'] == answer['attempt_status'] == 'IN_PROGRESS'
    assert answer['session_reason'] is None
    assert runner.status(directory)['status'] == 'PREPARED_ATTEMPT_NO_MODEL_CALL'
    assert (directory/'attempts/003/request.json').is_file()
    assert not (directory/'attempts/003/intent.json').exists()
    assert not (directory/'attempts/003/admission_event.json').exists()


@pytest.mark.parametrize('key', ['allOf', 'anyOf', 'oneOf'])
def test_provider_root_combinator_refused_before_preparation(key):
    with pytest.raises(ValueError, match='INSPECTION_PROVIDER_TOP_LEVEL_COMBINATOR'):
        runner.input_preflight('p', {'type': 'object', key: [{'type': 'object'}]})


def test_dependency_applies_to_whole_result_with_required_trigger():
    raw, _, _, previous, second = prior_fixture()
    schema = schema_for(raw, previous)
    assert not {'allOf', 'anyOf', 'oneOf'} & set(schema)
    assert 'schema' in schema['required']
    result = copy.deepcopy(result_of(second))
    # Removing or changing the trigger cannot disable the exact carry contract.
    for mutation in ('absent', 'changed'):
        invalid = copy.deepcopy(result)
        if mutation == 'absent':
            del invalid['schema']
        else:
            invalid['schema'] = 'unbound-marker'
        invalid['findings'] = []
        assert not Draft7Validator(schema).is_valid(invalid)
    assert runner.input_preflight('p', schema)['schema_bytes'] > 0


@pytest.mark.parametrize('completed', [True, False])
def test_existing_canary_exercises_provider_envelope_without_new_semantics(completed):
    raw, _, _, _, _ = prior_fixture()
    manifest = json.loads(raw)
    schema = runner._canary_schema(manifest, H(raw))
    result = {'reviewed_commit': manifest['source'], 'scope': manifest['scope'],
              'manifest_sha256': H(raw), 'completed': completed}
    assert Draft7Validator(schema).is_valid(result)
    assert 'scope' in schema['required'] and 'scope' in schema['dependencies']
    assert not {'allOf', 'anyOf', 'oneOf'} & set(schema)
    invalid = {**result, 'completed': 'true'}
    assert not Draft7Validator(schema).is_valid(invalid)
    del result['scope']
    assert not Draft7Validator(schema).is_valid(result)
    runner.input_preflight('p', schema)


@pytest.mark.parametrize('defect', ['approved_closure', 'context_original', 'first_prompt', 'external_proof'])
def test_run_policy_provenance_refuses_under_lock_before_any_admission(tmp_path, monkeypatch, defect):
    from orchestrator import inspection_bootstrap, review_input_codec
    directory, raw, previous, target, seen = run_fixture(tmp_path, monkeypatch)
    reached = []
    def lock_is_held():
        with (directory/'execution.lock').open('a') as separate:
            with pytest.raises(BlockingIOError):
                runner.fcntl.flock(separate, runner.fcntl.LOCK_EX | runner.fcntl.LOCK_NB)
        reached.append('locked')
    if defect == 'approved_closure':
        def reject_context(*args):
            lock_is_held()
            raise ValueError('SYNTHETIC_UNAPPROVED_POLICY_CONTEXT')
        monkeypatch.setattr(inspection_bootstrap, 'validate_context', reject_context)
        reason = 'UNAPPROVED_POLICY_CONTEXT'
    elif defect == 'context_original':
        path=directory/'context-original.json';path.chmod(0o600);path.write_bytes(path.read_bytes()+b' ')
        reason = 'SHARED_CONTEXT_CHANGED'
    elif defect == 'first_prompt':
        path=directory/'attempts/001/request.json';value=json.loads(path.read_bytes())
        value['prompt']='Substituted operating context.\n'+value['prompt']
        path.chmod(0o600);path.write_bytes(E(value))
        reason = 'APPROVED_CONTEXT_PROMPT_CHANGED'
    else:
        path=directory/'bootstrap/request.json';path.write_bytes(E({'input_presentation':review_input_codec.FORMAT_V2}))
        def reject_proof(path):
            lock_is_held()
            raise ValueError('SYNTHETIC_POLICY_BASELINE_PROOF_CHANGED')
        monkeypatch.setattr(inspection_bootstrap, 'read_policy_baseline', reject_proof)
        reason = 'POLICY_BASELINE_PROOF_CHANGED'
    with pytest.raises(ValueError, match=reason):runner.run(directory,2)
    assert seen == []  # Neither runtime_command nor admit nor provider was reached.
    assert not (target/'intent.json').exists()
    assert not (target/'admission_event.json').exists()
    assert not (target/'protocol.jsonl').exists()
    if defect in {'approved_closure','external_proof'}:assert reached == ['locked']
