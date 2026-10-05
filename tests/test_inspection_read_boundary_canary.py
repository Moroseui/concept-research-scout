"""Synthetic original-hook tests; these do not qualify a native canary."""
import copy
import json
import pytest
from orchestrator import inspection_access as access, inspection_canary as canary
from orchestrator import inspection_runner as runner
from test_inspection_direct_opus import direct_canary, direct_events
from test_inspection_canary import events, save_events

E, H = canary.encoded, canary.digest

def boundary_fixture(tmp_path, monkeypatch, *, token=False):
    bundle, expected = direct_canary(tmp_path, monkeypatch)
    version = canary.TOKEN_READ_BOUNDARY_VERSION if token else canary.READ_BOUNDARY_VERSION
    expected['read_boundary_version'] = version
    literal = canary.read_boundary_literal(version=version)
    manifest = json.loads(expected['access_manifest_original'])
    if token:
        manifest['read_failure_policy'] = access.READ_TOKEN_FAILURE_POLICY
    manifest['files'][canary.READ_BOUNDARY_NAME] = {
        'sha256': H(literal), 'bytes': len(literal), 'line_count': len(literal.decode().splitlines())}
    expected['access_manifest_original'] = E(manifest).decode()
    (tmp_path/'view'/canary.READ_BOUNDARY_NAME).write_bytes(literal)
    raw = bundle['hooks']; old = events(raw); session = expected['phases']['hooks']['session_id']
    calls = canary.canary_calls(expected['nonce'], 'hooks', read_boundary=True,
                                read_boundary_version=version)
    stream = [old[0]]; raw['journal'] = []
    journal = tmp_path/'boundary-journal'; journal.mkdir(mode=0o700)
    config = {'schema': access.CONFIG_SCHEMA, 'source': expected['source'],
        'access_manifest_sha256': H(E(manifest)), 'session_id': session,
        'attempt_id': '1', 'journal_root': '/state/inspection-journal/1'}
    error = ('File content ('+access._read_size_label(len(literal))+') exceeds maximum allowed size (256KB). '
        'Use offset and limit parameters to read specific portions of the file, '
        'or search for specific content instead of reading the whole file.')
    if token:
        from test_inspection_read_failures import TOKEN_ERROR
        error = TOKEN_ERROR
    displayed = b''.join(literal.splitlines(keepends=True)[:3]).replace(b'\r\n', b'\n').decode()
    response = {'type': 'text', 'file': {'filePath': '/review/'+canary.READ_BOUNDARY_NAME,
        'content': displayed, 'numLines': 3, 'startLine': 1,
        'totalLines': manifest['files'][canary.READ_BOUNDARY_NAME]['line_count']+1}}
    for index, (tool, args) in enumerate(calls):
        key = f'boundary_{index}'
        stream.append({'type': 'assistant', 'session_id': session, 'message': {
            'content': [{'type': 'tool_use', 'id': key, 'name': tool, 'input': args}]}})
        result = {'type': 'tool_result', 'tool_use_id': key, 'is_error': index != 4,
                  'content': 'denied' if index < 3 else error if index == 3 else displayed}
        event = {'type': 'user', 'session_id': session, 'message': {'content': [result]}}
        if index == 3: event['tool_use_result'] = 'Error: '+error
        if index == 4: event['tool_use_result'] = response
        stream.append(event)
        hook = {'session_id': session, 'hook_event_name': 'PreToolUse', 'cwd': '/review',
            'permission_mode': 'dontAsk', 'tool_use_id': key, 'tool_name': tool, 'tool_input': args}
        access.hook(config, E(manifest), E(hook), view_root=tmp_path/'view', journal_root=journal)
        suffixes = ['pre']
        if index == 3:
            hook.update(hook_event_name='PostToolUseFailure', error=error,
                        is_interrupt=False, duration_ms=1)
            suffixes.append('failure')
        if index == 4:
            hook.update(hook_event_name='PostToolUse', tool_response=response)
            suffixes.append('post')
        if len(suffixes) == 2:
            access.hook(config, E(manifest), E(hook), view_root=tmp_path/'view', journal_root=journal)
        for suffix in suffixes:
            raw['journal'].append(E({'observation_original': (journal/f'{key}.{suffix}.observation.json').read_text(),
                                    'hook_input_original': (journal/f'{key}.{suffix}.input.json').read_text()}))
    terminal = old[-1]; terminal['num_turns'] = 6; stream.append(terminal)
    save_events(raw, direct_events(stream))
    return bundle, expected, journal


def verify(bundle, expected):
    return canary.verify_canary(bundle, expected)


@pytest.mark.parametrize('token', [False, True])
def test_original_failure_then_mixed_newline_read_qualifies_synthetic_boundary(tmp_path, monkeypatch, token):
    bundle, expected, _ = boundary_fixture(tmp_path, monkeypatch, token=token)
    result = verify(bundle, expected)
    canary.require_read_boundary(result, read_failure_policy=access.READ_TOKEN_FAILURE_POLICY if token else None)
    assert result.get('token_limit_failure_verified', False) is token
    proof = result['phases']['hooks']['read_boundary']
    assert proof['failed_read']['coverage'] == []
    assert proof['bounded_crlf_read']['crlf_line_numbers'] == [1, 3]
    assert proof['bounded_crlf_read']['fragment_sha256'] != proof['bounded_crlf_read']['displayed_fragment_sha256']
    assert proof['whole_file_read_claim'] is False
    assert len(bundle['hooks']['journal']) == 7
    assert len(result['phases']['hooks']['tool_use_ids']) == 5
    assert len(result['phases']['baseline']['tool_use_ids']) == 4
    assert bundle['baseline']['journal'] == []


def test_old_originals_still_parse_but_do_not_satisfy_current_boundary(tmp_path, monkeypatch):
    bundle, expected = direct_canary(tmp_path, monkeypatch)
    old = verify(bundle, expected)
    assert old['status'] == 'PASSED'
    with pytest.raises(ValueError, match='CURRENT_READ_BOUNDARY_REQUIRED'):
        canary.require_read_boundary(old)
    monkeypatch.setattr(runner, 'read_canary_proof', lambda _: (expected, bundle))
    from test_inspection_review import fixture_manifest
    (tmp_path/'manifest.json').write_bytes(fixture_manifest()[0])
    with pytest.raises(ValueError, match='CURRENT_READ_BOUNDARY_REQUIRED'):
        runner.verify_canary(tmp_path, {'execution': expected['execution']})


@pytest.mark.parametrize('fault', ['missing_failure', 'missing_post', 'unknown_marker',
    'changed_source_hash', 'changed_source_bytes', 'changed_crlf_map', 'changed_display_hash',
    'changed_original_hash', 'generic_error', 'failure_claims_coverage', 'post_claims_all_lines',
    'wrong_offset', 'wrong_limit', 'bounded_before_failure', 'bounded_before_failure_result', 'failure_result_not_error'])
@pytest.mark.parametrize('token', [False, True])
def test_boundary_requires_exact_originals(tmp_path, monkeypatch, fault, token):
    bundle, expected, _ = boundary_fixture(tmp_path, monkeypatch, token=token)
    raw = bundle['hooks']
    if fault in ('missing_failure', 'missing_post'):
        phase = 'PostToolUseFailure' if fault == 'missing_failure' else 'PostToolUse'
        raw['journal'] = [r for r in raw['journal'] if json.loads(json.loads(r)['observation_original'])['phase'] != phase]
    elif fault == 'unknown_marker': expected['read_boundary_version'] = 'unknown/v1'
    elif fault.startswith('changed_source_'):
        manifest = json.loads(expected['access_manifest_original'])
        manifest['files'][canary.READ_BOUNDARY_NAME]['sha256' if fault.endswith('hash') else 'bytes'] = '0'*64 if fault.endswith('hash') else 1
        expected['access_manifest_original'] = E(manifest).decode()
    elif fault in ('changed_crlf_map', 'changed_display_hash', 'changed_original_hash',
                    'failure_claims_coverage', 'post_claims_all_lines'):
        for i, wrapped in enumerate(raw['journal']):
            item = json.loads(wrapped); row = json.loads(item['observation_original'])
            if fault == 'failure_claims_coverage' and row['phase'] == 'PostToolUseFailure':
                row['native_failure']['coverage'] = [[1, 3]]
            elif row['phase'] == 'PostToolUse':
                if fault == 'changed_crlf_map': row['actual_read']['crlf_line_numbers'] = [1]
                if fault == 'changed_display_hash': row['actual_read']['displayed_fragment_sha256'] = '0'*64
                if fault == 'changed_original_hash': row['actual_read']['fragment_sha256'] = '0'*64
                if fault == 'post_claims_all_lines': row['actual_read']['end_line'] = 4099
            item['observation_original'] = E(row).decode(); raw['journal'][i] = E(item)
    else:
        value = events(raw)
        if fault == 'bounded_before_failure': value[7:11] = value[9:11]+value[7:9]
        elif fault == 'bounded_before_failure_result': value[8:10] = [value[9], value[8]]
        else:
            for event in value:
                for item in event.get('message', {}).get('content', []):
                    if item.get('id') == 'boundary_4':
                        if fault == 'wrong_offset': item['input']['offset'] = 2
                        if fault == 'wrong_limit': item['input']['limit'] = 2
                    if item.get('tool_use_id') == 'boundary_3':
                        if fault == 'generic_error': item['content'] = 'unrelated error'
                        if fault == 'failure_result_not_error': item['is_error'] = False
        save_events(raw, value)
    with pytest.raises(ValueError): verify(bundle, expected)


def test_failure_journal_loader_preserves_exact_input_and_order(tmp_path, monkeypatch):
    bundle, expected, journal = boundary_fixture(tmp_path, monkeypatch)
    directory = tmp_path/'loader'; directory.mkdir(); (directory/'journal').mkdir()
    for path in journal.iterdir(): (directory/'journal'/path.name).write_bytes(path.read_bytes())
    assert runner._canary_journal(directory) == bundle['hooks']['journal']
    rows = [json.loads(json.loads(row)['observation_original']) for row in runner._canary_journal(directory)]
    assert sum(row['phase'] == 'PostToolUseFailure' for row in rows) == 1


def test_question_keeps_limits_and_exact_cases():
    prompt = runner._canary_question('x'*32, 'hooks', read_boundary=True)
    assert 'five' in prompt and 'offset' in prompt and 'limit' in prompt
    assert len(canary.canary_calls('x'*32, 'hooks', read_boundary=True)) == 5
    assert len(canary.canary_calls('x'*32, 'baseline', read_boundary=True)) == 4
    assert len(canary.read_boundary_literal()) > access.READ_SIZE_ERROR_LIMIT


def test_material_rejects_older_probe_without_new_boundary(tmp_path, monkeypatch):
    import test_inspection_review as fixture
    from test_inspection_deployment import material_fixture
    from orchestrator import inspection_deployment as deployment
    original = fixture.fixture_probe
    def old_probe(*args, **kwargs):
        value = json.loads(original(*args, **kwargs))
        # Rebind this synthetic old proof consistently in all fixture originals.
        for key in ('read_boundary_version', 'oversized_read_failure_verified',
                    'bounded_read_after_failure_verified', 'crlf_display_verified'):
            value.pop(key, None)
        return E(value)
    monkeypatch.setattr(fixture, 'fixture_probe', old_probe)
    args = material_fixture()
    with pytest.raises(ValueError, match='CURRENT_READ_BOUNDARY_REQUIRED'):
        deployment.validate_deployment_session(**args)


def test_export_roundtrip_retains_failure_and_display_originals(tmp_path, monkeypatch):
    bundle, expected, _ = boundary_fixture(tmp_path, monkeypatch)
    proof = verify(bundle, expected)
    plan = tmp_path/'export-plan'; plan.mkdir()
    (plan/'plan.json').write_bytes(E(expected))
    (plan/'canary-plan.json').write_bytes(E({'synthetic': True}))
    (plan/'administrative-permit.json').write_bytes(E({'synthetic': True}))
    sessions = tmp_path/'sessions'
    for pins in expected['phases'].values():
        target = sessions/pins['session_id']/'attempts/001'; target.mkdir(parents=True)
        for name in ('control-readback.json', 'runtime-readback.json', 'invocation.json'):
            (target/name).write_bytes(E({'synthetic': name}))
    monkeypatch.setattr(runner, 'session_path', lambda session: sessions/session)
    result = runner._export_canary_proof(plan, expected, bundle, proof)
    again_expected, again_bundle = runner.read_canary_proof(result['path'])
    assert again_expected == expected and again_bundle == bundle
    assert E(verify(again_bundle, again_expected)) == E(proof)
    assert any(name.endswith('.failure.input.json') for name in result['files'])


@pytest.mark.parametrize('token', [False, True])
def test_read_boundary_policy_requires_exact_matching_proof(tmp_path, monkeypatch, token):
    bundle, expected, _ = boundary_fixture(tmp_path, monkeypatch, token=token)
    proof = verify(bundle, expected)
    matching = access.READ_TOKEN_FAILURE_POLICY if token else None
    canary.require_read_boundary(proof, read_failure_policy=matching)
    with pytest.raises(ValueError):
        canary.require_read_boundary(proof, read_failure_policy=None if token else access.READ_TOKEN_FAILURE_POLICY)
    with pytest.raises(ValueError):
        canary.require_read_boundary(proof, read_failure_policy='native-read-token-limit/unknown')
    if token:
        proof['token_limit_failure_verified'] = False
        with pytest.raises(ValueError):
            canary.require_read_boundary(proof, read_failure_policy=matching)


def test_token_canary_keeps_exact_five_calls_and_legacy_bytes():
    legacy = canary.read_boundary_literal()
    assert legacy == canary.read_boundary_literal(version=canary.READ_BOUNDARY_VERSION)
    assert len(legacy) > access.READ_SIZE_ERROR_LIMIT
    version = canary.TOKEN_READ_BOUNDARY_VERSION
    token = canary.read_boundary_literal(version=version)
    assert len(token.decode().splitlines()) == 4099
    assert token.splitlines(keepends=True)[:3] == legacy.splitlines(keepends=True)[:3]
    calls = canary.canary_calls('x'*32, 'hooks', read_boundary=True, read_boundary_version=version)
    assert len(calls) == 5
    assert calls[3] == ('Read', {'file_path': '/review/'+canary.READ_BOUNDARY_NAME,
                                'offset': 1, 'limit': 4099})
    assert calls[4] == ('Read', {'file_path': '/review/'+canary.READ_BOUNDARY_NAME,
                                'offset': 1, 'limit': 3})
    assert canary.canary_calls('x'*32, 'hooks', read_boundary=True)[3] == (
        'Read', {'file_path': '/review/'+canary.READ_BOUNDARY_NAME})
