"""Synthetic narrow native denial checks; no provider, admission or accepted canary."""
import copy
import json
import pytest
from orchestrator import inspection_review as r, inspection_canary as c
from orchestrator import inspection_runtime as runtime
from test_inspection_review import fixture_manifest, fixture_probe, fixture_attempt, events, replace_events
from test_inspection_canary import fixture, events as canary_events, save_events
from inspection_confinement_fixtures import FIXTURE_PROFILE, FIXTURE_PROFILE_SHA

CLI = '10caae8f22b915c26bfff0e013a4d45608c4f1ae287583626569156f447730e5'
MESSAGE = 'File is in a directory that is denied by your permission settings.'


def pair(path='/state/canary/probe.txt'):
    use = {'type': 'tool_use', 'id': 'toolu_synthetic', 'name': 'Read', 'input': {'file_path': path}}
    result = {'type': 'tool_result', 'tool_use_id': use['id'], 'is_error': True,
              'content': '<tool_use_error>' + MESSAGE + '</tool_use_error>'}
    return use, result, 'Error: ' + MESSAGE


def denial_attempt(pin=CLI, *, status='IN_PROGRESS', tools=False):
    raw, policy = fixture_manifest()
    manifest, probe = json.loads(raw), json.loads(fixture_probe())
    if pin is not None:
        probe['runtime_cli_sha256'] = pin
    probe_raw = r.encoded(probe)
    manifest['permission_probe_sha256'] = r.digest(probe_raw)
    raw = r.encoded(manifest)
    attempt = fixture_attempt(raw, policy, status=status, tools=tools)
    attempt['permission_probe'] = probe_raw
    use, result, output = pair()
    rows = events(attempt)
    rows.insert(-1, {'type': 'assistant', 'session_id': manifest['session_id'],
                    'message': {'model': r.MODEL, 'content': [use]}})
    rows.insert(-1, {'type': 'user', 'session_id': manifest['session_id'],
                    'message': {'role': 'user', 'content': [result]}, 'tool_use_result': output})
    replace_events(attempt, rows)
    return raw, attempt


def test_exact_denial_preserves_event_and_contributes_zero_read_coverage():
    raw, attempt = denial_attempt()
    session = r.validate_session(raw, [attempt])
    assert session['status'] == 'IN_PROGRESS'
    assert session['reads'] == {} and session['required_ranges_missing'] == {'code.py': [[1, 2]]}
    denial = session['attempts'][0]['denials'][0]
    event = events(attempt)[-2]
    assert denial == {'tool_use_id': 'toolu_synthetic', 'tool_name': 'Read',
        'kind': 'NATIVE_READ_INPUT_VALIDATION_DENIED', 'coverage': [], 'runtime_cli_sha256': CLI,
        'tool_result_sha256': r.digest(r.encoded(event['message']['content'][0])),
        'tool_result_event_sha256': r.digest(r.encoded(event))}


def test_denied_call_cannot_satisfy_approval_but_does_not_erase_genuine_reads():
    raw, attempt = denial_attempt(status='APPROVE')
    with pytest.raises(ValueError, match='UNRESOLVED_COVERAGE'):
        r.validate_session(raw, [attempt])
    raw, attempt = denial_attempt(status='APPROVE', tools=True)
    session = r.validate_session(raw, [attempt])
    assert session['status'] == 'APPROVE' and session['reads'] == {'code.py': [[1, 2]]}
    assert session['attempts'][0]['denials'][0]['coverage'] == []


@pytest.mark.parametrize('pin', [None, '0'*64, '2.1.222', '', 1])
def test_unbound_or_unknown_cli_never_enables_exception(pin):
    raw, attempt = denial_attempt(pin)
    assert r.parse_attempt(raw, attempt)['status'] == 'RECONCILIATION_REQUIRED'


def test_permission_pin_is_actual_hash_bound_original():
    raw, attempt = denial_attempt()
    probe = json.loads(attempt['permission_probe']); probe['runtime_cli_sha256'] = '0'*64
    attempt['permission_probe'] = r.encoded(probe)
    assert r.parse_attempt(raw, attempt)['reason'] == 'PERMISSION_PROBE_BINDING'


@pytest.mark.parametrize('path', ['/review/code.py', '/stateful/probe.txt', '/states/probe.txt',
    '/unknown/probe', 'state/x', '//state/x', '/state//x', '/state/./x', '/state/../review/x',
    '/state/x/..', '/state/x/', '/state/x\\y', '/state/x\n', '/state/x\x00', '/state/x\x7f',
    '/State/x', '/state\uff0fx'])
def test_inside_lookalike_and_noncanonical_paths_refuse(path):
    use, result, output = pair(path)
    assert not r.native_read_input_validation_denied(use, result, output, runtime_cli_sha256=CLI)


@pytest.mark.parametrize('path', ['/state', '/state/canary/probe.txt', '/etc/passwd', '/proc/self/status'])
def test_fixed_denied_roots_are_classified_without_reading_them(path):
    use, result, output = pair(path)
    assert r.native_read_input_validation_denied(use, result, output, runtime_cli_sha256=CLI)


@pytest.mark.parametrize('mutation', ['name', 'id', 'empty_id', 'type', 'result_type', 'success',
    'generic_error', 'changed_pair', 'missing_pair', 'content_list', 'extra_input', 'foreign_result'])
def test_only_exact_correlated_original_pair_qualifies(mutation):
    use, result, output = pair()
    if mutation == 'name': use['name'] = 'Grep'
    elif mutation == 'id': use['id'] = '../bad'
    elif mutation == 'empty_id': use['id'] = ''
    elif mutation == 'type': use['type'] = 'text'
    elif mutation == 'result_type': result['type'] = 'text'
    elif mutation == 'success': result['is_error'] = False
    elif mutation == 'generic_error': result['content'] = 'Permission denied'
    elif mutation == 'changed_pair': output += ' '
    elif mutation == 'missing_pair': output = None
    elif mutation == 'content_list': result['content'] = [{'type': 'text', 'text': result['content']}]
    elif mutation == 'extra_input': use['input']['offset'] = 1
    elif mutation == 'foreign_result': result['tool_use_id'] = 'different'
    assert not r.native_read_input_validation_denied(use, result, output, runtime_cli_sha256=CLI)


@pytest.mark.parametrize('mutation', ['duplicate_result', 'duplicate_use', 'multiple_user_items',
    'missing_result', 'missing_output', 'foreign_native', 'duplicate_native', 'hook_conflict'])
def test_journal_conflicts_are_not_repaired(mutation):
    raw, attempt = denial_attempt(); rows = events(attempt)
    use, result = rows[-3]['message']['content'][0], rows[-2]['message']['content'][0]
    native = {'tool_name': 'Read', 'tool_use_id': use['id'], 'tool_input': use['input']}
    if mutation == 'duplicate_result': rows[-2]['message']['content'].append(copy.deepcopy(result))
    elif mutation == 'duplicate_use': rows[-3]['message']['content'].append(copy.deepcopy(use))
    elif mutation == 'multiple_user_items': rows[-2]['message']['content'].append({'type': 'text', 'text': 'other'})
    elif mutation == 'missing_result': rows.pop(-2)
    elif mutation == 'missing_output': rows[-2].pop('tool_use_result')
    elif mutation == 'foreign_native': native['tool_input'] = {'file_path': '/other'}; rows[-1]['permission_denials'] = [native]
    elif mutation == 'duplicate_native': rows[-1]['permission_denials'] = [native, copy.deepcopy(native)]
    elif mutation == 'hook_conflict':
        m = json.loads(raw)
        hook = {'session_id': m['session_id'], 'tool_use_id': use['id'], 'tool_name': 'Read',
                'tool_input': use['input'], 'hook_event_name': 'PreToolUse', 'cwd': '/review', 'permission_mode': 'dontAsk'}
        observation = {'schema': 'inspection-tool-observation/v1', 'phase': 'PreToolUse',
            'source': m['source'], 'access_manifest_sha256': m['access_manifest_sha256'],
            'session_id': m['session_id'], 'attempt_id': '1', 'tool_use_id': use['id'], 'tool_name': 'Read',
            'status': 'DENIED', 'raw_input_sha256': r.digest(r.encoded(hook)),
            'request_sha256': r.digest(r.encoded(use['input']))}
        attempt['journal'] = [r.encoded({'observation_original': r.encoded(observation).decode(),
                                       'hook_input_original': r.encoded(hook).decode()})]
    replace_events(attempt, rows)
    assert r.parse_attempt(raw, attempt)['status'] == 'RECONCILIATION_REQUIRED'


def test_existing_exact_terminal_denial_stays_on_ordinary_route():
    raw, attempt = denial_attempt(); rows = events(attempt); use = rows[-3]['message']['content'][0]
    rows[-1]['permission_denials'] = [{'tool_name': 'Read', 'tool_use_id': use['id'], 'tool_input': use['input']}]
    replace_events(attempt, rows)
    receipt = r.parse_attempt(raw, attempt)
    assert receipt['status'] == 'IN_PROGRESS'
    assert receipt['denials'][0]['kind'] == 'NATIVE_PERMISSION_DENIED' and receipt['denials'][0]['coverage'] == []


def test_permission_proof_exports_derived_runtime_cli_pin(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'PROFILE_SHA256', FIXTURE_PROFILE_SHA)
    monkeypatch.setattr(runtime, 'PROFILE_BYTES', len(FIXTURE_PROFILE))
    bundle, expected = fixture(tmp_path)
    proof = c.verify_canary(bundle, expected)
    assert proof['runtime_cli_sha256'] == expected['execution']['files']['claude']['sha256']


def test_hook_phase_cannot_substitute_early_native_denial(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'PROFILE_SHA256', FIXTURE_PROFILE_SHA)
    monkeypatch.setattr(runtime, 'PROFILE_BYTES', len(FIXTURE_PROFILE))
    monkeypatch.setattr(r, 'READ_VALIDATION_DENIAL_CLI_SHA256', r.digest(b'claude'))
    bundle, expected = fixture(tmp_path); raw = bundle['hooks']; rows = canary_events(raw)
    use = next(item for row in rows for item in row.get('message', {}).get('content', [])
               if item.get('type') == 'tool_use' and item.get('input') == {'file_path': '/state/canary/probe.txt'})
    for event in rows:
        for item in event.get('message', {}).get('content', []):
            if item.get('type') == 'tool_result' and item.get('tool_use_id') == use['id']:
                item['content'] = '<tool_use_error>' + MESSAGE + '</tool_use_error>'
                event['tool_use_result'] = 'Error: ' + MESSAGE
    raw['journal'] = [row for row in raw['journal']
        if json.loads(json.loads(row)['observation_original'])['tool_use_id'] != use['id']]
    save_events(raw, rows)
    with pytest.raises(ValueError, match='MISSING_ALLOWED_TOOL_HOOK_OR_RESULT'):
        c.verify_canary(bundle, expected)
