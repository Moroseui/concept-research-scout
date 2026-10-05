"""H2 untrusted validator boundary; no scientific program or live job is run."""
import copy
import hashlib
import json

import pytest

from orchestrator import scientific_job_results as results


@pytest.fixture
def original():
    binding = {name: ('a' * (40 if name == 'source' else 64))
               for name in results.SEMANTIC_BINDING_FIELDS}
    value = {'schema': results.SEMANTIC_OUTPUT_SCHEMA, 'binding': binding,
             'status': 'VALID', 'reason': 'All specified checks returned valid.',
             'diagnostics': []}
    return value, copy.deepcopy(binding)


def raw(value):
    return json.dumps(value, ensure_ascii=False).encode('utf-8')


@pytest.mark.parametrize('status', ['VALID', 'INVALID', 'DEFER'])
def test_validator_status_is_evidence_not_acceptance(original, status):
    value, binding = original
    value['status'] = status
    body = raw(value) + b'\n'
    checked = results.semantic_validation_output(body, binding)
    assert checked['output']['status'] == status
    assert checked['scientific_acceptance'] is checked['adoption'] is False
    assert checked['output_sha256'] == hashlib.sha256(body).hexdigest()
    assert checked['output_utf8_bytes'] == len(body)


@pytest.mark.parametrize('field', sorted(results.SEMANTIC_BINDING_FIELDS))
def test_each_executed_identity_must_match(original, field):
    value, binding = original
    value['binding'][field] = 'b' * len(binding[field])
    with pytest.raises(ValueError, match='EXECUTED_BINDING_CHANGED'):
        results.semantic_validation_output(raw(value), binding)


@pytest.mark.parametrize('key,value', [('scientific_acceptance', True),
                                     ('command', ['python', 'other.py']),
                                     ('path', '/tmp/result')])
def test_output_cannot_add_authority_or_instructions(original, key, value):
    body, binding = original
    body[key] = value
    with pytest.raises(ValueError, match='CLOSED_SCHEMA'):
        results.semantic_validation_output(raw(body), binding)


def test_duplicate_json_keys_are_not_last_value_wins(original):
    value, binding = original
    body = raw(value).replace(b'"status": "VALID"', b'"status": "INVALID", "status": "VALID"')
    with pytest.raises(ValueError, match='DUPLICATE_KEY'):
        results.semantic_validation_output(body, binding)


@pytest.mark.parametrize('body', [b'{', b'\xff', b'[]', b'{"status":NaN}', b'[' * 2000])
def test_malformed_or_ambiguous_output_cannot_qualify(original, body):
    with pytest.raises(ValueError):
        results.semantic_validation_output(body, original[1])


def test_utf8_bytes_are_bounded_before_json_decoding(original):
    value, binding = original
    value['reason'] = '\u00e9' * 16000
    body = raw(value)
    assert len(body.decode()) < results.SEMANTIC_OUTPUT_MAX_BYTES < len(body)
    with pytest.raises(ValueError, match='OUTPUT_BYTE_BOUND'):
        results.semantic_validation_output(body, binding)


@pytest.mark.parametrize('edit', ['reason', 'diagnostic_count', 'diagnostic_message', 'diagnostic_keys', 'boolean_status'])
def test_bounded_human_readable_diagnostics(original, edit):
    value, binding = original
    if edit == 'reason': value['reason'] = 'x' * 2001
    if edit == 'diagnostic_count': value['diagnostics'] = [{'code': 'X', 'message': 'Check'}] * 33
    if edit == 'diagnostic_message': value['diagnostics'] = [{'code': 'X', 'message': 'x' * 1025}]
    if edit == 'diagnostic_keys': value['diagnostics'] = [{'code': 'X', 'message': 'Check', 'accept': True}]
    if edit == 'boolean_status': value['status'] = True
    with pytest.raises(ValueError):
        results.semantic_validation_output(raw(value), binding)


def test_supplied_expected_binding_is_closed_and_typed(original):
    value, binding = original
    binding['completion'] = True
    with pytest.raises(ValueError, match='EXPECTED_BINDING_REQUIRED'):
        results.semantic_validation_output(raw(value), binding)


@pytest.fixture
def checked_import():
    # Reuse the actual original-result plumbing fixture; this is not science.
    from test_prospective_interpretation import fixture
    value = fixture()[1]['import']
    core = value['event']['execution_binding']
    core['input_manifest'] = 'campaigns/isles24-pilot/experiments/P002/inputs.json'
    core['files'][core['input_manifest']] = '8' * 64
    core['protocol']['bindings'] = {'input_manifest_sha256': '8' * 64}
    outcome = {'status': 'COMPLETE', 'scientific_acceptance': False,
               'result_manifest_sha256': value['result_manifest_sha256']}
    value['event']['outcome'] = outcome
    value['completion'] = value['event']['event'] = results.jobs.digest(results.jobs.encoded(outcome))
    return value


def test_expected_binding_uses_executed_original_descriptor(checked_import):
    binding = results.semantic_validation_binding(checked_import)
    version = checked_import['scientific_version']
    assert binding['scientific_version'] == hashlib.sha256(results.encoded(version)).hexdigest()
    assert binding['scientific_version'] != version['core_sha256']
    value = {'schema': results.SEMANTIC_OUTPUT_SCHEMA, 'binding': binding,
             'status': 'DEFER', 'reason': 'Missing clinical validation evidence.', 'diagnostics': []}
    receipt = results.semantic_validation_output(raw(value), binding)
    assert receipt['output']['status'] == 'DEFER'
    assert receipt['scientific_acceptance'] is receipt['adoption'] is False


def test_changed_version_decision_does_not_reuse_validator_result(checked_import):
    binding = results.semantic_validation_binding(checked_import)
    value = {'schema': results.SEMANTIC_OUTPUT_SCHEMA, 'binding': binding,
             'status': 'VALID', 'reason': 'Fixture evidence only.', 'diagnostics': []}
    changed = copy.deepcopy(checked_import)
    changed['scientific_version']['decision_sha256'] = '9' * 64
    changed['event']['execution_binding']['scientific_version'] = copy.deepcopy(changed['scientific_version'])
    new_binding = results.semantic_validation_binding(changed)
    assert new_binding != binding
    with pytest.raises(ValueError, match='EXECUTED_BINDING_CHANGED'):
        results.semantic_validation_output(raw(value), new_binding)


@pytest.mark.parametrize('damage', ['input', 'result', 'outcome', 'completion', 'validator', 'version'])
def test_inconsistent_executed_import_cannot_supply_expectations(checked_import, damage):
    value = copy.deepcopy(checked_import)
    if damage == 'input': value['event']['execution_binding']['protocol']['bindings']['input_manifest_sha256'] = '9' * 64
    if damage == 'result': value['result_manifest_sha256'] = '9' * 64
    if damage == 'outcome': value['event']['outcome']['status'] = 'FAILED'
    if damage == 'completion': value['completion'] = value['event']['event'] = '9' * 64
    if damage == 'validator': value['scientific_context']['campaigns/isles24-pilot/experiments/P002/validate_return.py'] += '\nchanged'
    if damage == 'version': value['scientific_version']['arbitrary_authority'] = True
    with pytest.raises(ValueError):
        results.semantic_validation_binding(value)


@pytest.fixture
def validation_import(tmp_path, checked_import):
    import os
    binding = results.semantic_validation_binding(checked_import)
    output = {'schema': results.SEMANTIC_OUTPUT_SCHEMA, 'binding': binding,
              'status': 'DEFER', 'reason': 'Missing validation input; no acceptance.',
              'diagnostics': []}
    reply = {'schema': results.SEMANTIC_RESULT_SCHEMA,
             'execution_status': 'COMPLETE', 'binding': binding,
             'attempt': 'b' * 64, 'request_sha256': 'c' * 64,
             'outcome_sha256': 'd' * 64, 'output': raw(output).decode() + '\n',
             'scientific_acceptance': False, 'model_calls': 0}
    calls = []
    def original_client(socket, operation, request):
        calls.append(operation)
        assert request == {'completion': checked_import['completion']}
        if operation == 'scientific_job_result': return copy.deepcopy(checked_import)
        assert operation == 'scientific_validation_result'
        return copy.deepcopy(reply)
    config = {'controller_uid': os.getuid(), 'state': str(tmp_path/'state'),
              'broker_socket': 'unused-fixture'}
    by = {'kind': 'agent', 'family': 'codex', 'model': 'fixture', 'session_id': 'fixture'}
    return config, checked_import['completion'], original_client, by, reply, calls


def apply_validation(fixture):
    config, completion, client, by, _, _ = fixture
    return results.import_semantic_validation(config, completion=completion,
                                               original_client=client, by=by)


def test_validation_import_is_idempotent_and_defer_stays_pending(validation_import):
    from pathlib import Path
    config, completion, _, _, _, calls = validation_import
    first = apply_validation(validation_import)
    root = Path(config['state'])/'scientific-results'/completion
    before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
    second = apply_validation(validation_import)
    after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
    assert first['duplicate'] is False and second == {**first, 'duplicate': True}
    assert before == after
    assert first['validator_status'] == 'DEFER' and first['formal_decision_status'] == 'PENDING'
    assert first['scientific_acceptance'] is first['adoption'] is False
    assert calls == ['scientific_job_result', 'scientific_validation_result'] * 2


@pytest.mark.parametrize('damage', ['changed_output', 'different_attempt', 'forged_acceptance',
                                   'missing_output', 'changed_original'])
def test_saved_validation_cannot_be_replaced_or_promoted(validation_import, damage):
    from pathlib import Path
    config, completion, _, _, reply, _ = validation_import
    apply_validation(validation_import)
    root = Path(config['state'])/'scientific-results'/completion/'semantic-validation'
    original = (root/'import.json').read_bytes()
    if damage == 'changed_output': reply['output'] = reply['output'].replace('DEFER', 'VALID')
    if damage == 'different_attempt': reply['attempt'] = 'e' * 64
    if damage == 'forged_acceptance':
        receipt = json.loads(original); receipt['scientific_acceptance'] = True
        (root/'import.json').write_bytes(raw(receipt))
    if damage == 'missing_output': (root/'validator-output.json').unlink()
    if damage == 'changed_original': (root/'original-response.json').write_bytes(b'{}')
    with pytest.raises((ValueError, OSError)):
        apply_validation(validation_import)
    if damage != 'forged_acceptance': assert (root/'import.json').read_bytes() == original


def test_interrupted_import_never_reexecutes_validation(validation_import, monkeypatch):
    from pathlib import Path
    config, completion, _, _, _, calls = validation_import
    original = results.immutable
    def fail(path, data):
        if Path(path).name == 'validator-output.json': raise OSError('fixture interrupted write')
        return original(path, data)
    monkeypatch.setattr(results, 'immutable', fail)
    with pytest.raises(OSError): apply_validation(validation_import)
    monkeypatch.setattr(results, 'immutable', original)
    root = Path(config['state'])/'scientific-results'/completion/'semantic-validation'
    before = {p.name: p.read_bytes() for p in root.iterdir() if p.is_file()}
    with pytest.raises(ValueError, match='PARTIAL_IMPORT_RECONCILE_NO_RETRY'):
        apply_validation(validation_import)
    assert {p.name: p.read_bytes() for p in root.iterdir() if p.is_file()} == before
    assert set(calls) == {'scientific_job_result', 'scientific_validation_result'}


@pytest.mark.parametrize('damage', ['running', 'failure', 'grant', 'bill', 'extra', 'binding', 'output'])
def test_protected_validation_envelope_refuses_false_completion(validation_import, damage):
    config, completion, _, _, reply, _ = validation_import
    if damage == 'running': reply['execution_status'] = 'RUNNING'
    if damage == 'failure': reply['execution_status'] = 'FAILED'
    if damage == 'grant': reply['scientific_acceptance'] = True
    if damage == 'bill': reply['model_calls'] = True
    if damage == 'extra': reply['command'] = 'execute'
    if damage == 'binding': reply['binding']['completion'] = '0' * 64
    if damage == 'output': reply['output'] += 'x' * 30001
    with pytest.raises(ValueError): apply_validation(validation_import)
    from pathlib import Path
    assert not (Path(config['state'])/'scientific-results'/completion/'semantic-validation').exists()
