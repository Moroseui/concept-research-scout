"""Synthetic original-receipt fixtures; no provider, filesystem read tools or admission."""
import copy
import json
import pytest
from orchestrator import inspection_review as r
from orchestrator.inspection_access import normalize_request


def fixture_probe():
    return r.encoded({'schema': 'inspection-permission-probe/v1', 'status': 'PASSED',
                      'baseline_permissions_verified': True, 'hooks_verified': True,
                      'native_denial_before_hooks_verified': True,
                      'read_boundary_version': 'native-read-size-and-crlf/v1',
                      'oversized_read_failure_verified': True, 'bounded_read_after_failure_verified': True,
                      'crlf_display_verified': True,
                      **{key + '_sha256': 'e' * 64 for key in ('runtime', 'settings', 'hooks')},
                      'qualification': 'SYNTHETIC_TEST_ONLY_NOT_ACTUAL_CANARY_EVIDENCE'})


def fixture_manifest():
    access = {'schema': 'inspection-access-manifest/v1', 'source': 'a' * 40, 'files': {'code.py': {
                  'sha256': r.digest(b'a\nb\n'), 'bytes': 4, 'line_count': 2}}}
    policy = {'status': 'RATIFIED', 'operator_approval': 'SYNTHETIC_NOT_REAL_PERMISSION',
              'state_write_permission': 'OPERATOR_AUTHORIZED', 'server_semantics': 'OPERATOR_AUTHORIZED_V1'}
    value = {'schema': r.MANIFEST, 'source': 'a' * 40, 'scope': 'synthetic-material-inspection',
             'session_id': '11111111-1111-1111-1111-111111111111', 'proposal_sha256': 'b' * 64,
             'current_request_sha256': 'c' * 64, 'context_sha256': 'd' * 64,
             'changes_sha256': '1' * 64, 'change_bindings_sha256': '2' * 64,
             'actor': {'kind': 'agent', 'identity': 'SYNTHETIC_FIXTURE'},
             'access_manifest_original': r.encoded(access).decode(), 'access_manifest_sha256': r.digest(r.encoded(access)),
             'pins': {name + '_sha256': 'e' * 64 for name in ('settings', 'hooks', 'runtime', 'runner')},
             'required_ranges': {'code.py': [[1, 2]]}, 'max_attempts': 3,
             'permission_probe_sha256': r.digest(fixture_probe()),
             'admission_binding': {'source': 'f' * 40, 'branch': 'astra/infrastructure-milestone-record',
                                   'kind': 'nightly_review', 'turn_id': '9' * 64,
                                   'policy_sha256': r.digest(r.encoded(policy))}}
    return r.encoded(value), r.encoded(policy)


def fixture_attempt(raw, policy, *, number=1, previous=None, status='APPROVE', start=1, count=2, tools=True):
    m = r.validate_manifest(raw)
    request = {'schema': r.REQUEST, 'source': m['source'], 'scope': m['scope'],
               'manifest_sha256': r.digest(raw), 'session_id': m['session_id'], 'attempt': number,
               'previous_receipt_sha256': r.digest(r.encoded(previous)) if previous else None,
               'prompt': 'SYNTHETIC fixture, not a real review or admission.'}
    admission_event = {key: m['admission_binding'][key] for key in ('source', 'branch', 'kind', 'turn_id')}
    admission_event['attempt'] = str(number)
    admission = {'status': 'ADMITTED', 'duplicate_admission': False,
                 **{key: admission_event[key] for key in ('source', 'branch', 'kind')},
                 'day': '2026-09-12', 'count': number, 'state_before': 'synthetic',
                 'notification': None, 'halted': False, 'pending_notifications': []}
    originals = {'request': r.encoded(request), 'admission_policy': policy,
                 'admission_event': r.encoded(admission_event), 'admission_receipt': r.encoded(admission),
                 'process': r.encoded({'pid': 123, 'proc_stat': '123 (synthetic) Z fixture'}),
                 'returned': r.encoded({'returncode': 0, 'wall_seconds': 1.0}), 'timeout': None,
                 'permission_probe': fixture_probe(), 'reconciliation': None}
    intent = {'schema': r.INTENT, 'request_sha256': r.digest(originals['request']), 'source': m['source'],
              'manifest_sha256': r.digest(raw), 'session_id': m['session_id'], 'attempt': number,
              'previous_receipt_sha256': request['previous_receipt_sha256'], 'actor': m['actor'], 'pins': m['pins'],
              'maximum_invocations': 1, 'automatic_retry': False,
              **{name + '_sha256': r.digest(originals[name]) for name in ('admission_event', 'admission_receipt', 'admission_policy')}}
    originals['intent'] = r.encoded(intent)
    result = {'schema': r.RESULT, 'scope': m['scope'], 'reviewed_commit': m['source'],
              'manifest_sha256': r.digest(raw), 'status': status, 'findings': ['Synthetic fixture only.'],
              'questions': [], 'claimed_inspected_files': ['code.py'], 'remaining_obligations': [], 'resolved': []}
    events = [{'type': 'system', 'subtype': 'init', 'session_id': m['session_id'],
               'tools': sorted(r.TOOLS), 'mcp_servers': [], 'permissionMode': 'dontAsk', 'model': r.MODEL}]
    content, journal = [], []
    if tools:
        tool_id = 'read-' + str(number)
        tool_input = {'file_path': '/review/code.py', 'offset': start, 'limit': count}
        use = {'type': 'tool_use', 'id': tool_id, 'name': 'Read', 'input': tool_input}
        text = ''.join('a\nb\n'.splitlines(keepends=True)[start - 1:start - 1 + count])
        output = {'type': 'text', 'file': {'filePath': '/review/code.py', 'content': text,
                                          'numLines': count, 'startLine': start, 'totalLines': 2}}
        content.append(use)
        for phase in ('PreToolUse', 'PostToolUse'):
            hook = {'session_id': m['session_id'], 'tool_use_id': tool_id, 'tool_name': 'Read', 'tool_input': tool_input,
                    'hook_event_name': phase, 'cwd': '/review', 'permission_mode': 'dontAsk'}
            if phase == 'PostToolUse':
                hook['tool_response'] = output
            row = {'schema': 'inspection-tool-observation/v1', 'phase': phase, 'source': m['source'],
                   'access_manifest_sha256': m['access_manifest_sha256'], 'session_id': m['session_id'],
                   'attempt_id': str(number), 'tool_use_id': tool_id, 'tool_name': 'Read',
                   'request_sha256': r.digest(r.encoded(tool_input)), 'raw_input_sha256': r.digest(r.encoded(hook)),
                   'normalized_request': normalize_request(json.loads(m['access_manifest_original']), 'Read', tool_input),
                   'status': 'ALLOWED' if phase == 'PreToolUse' else 'OBSERVED',
                   'observed_files': {'code.py': json.loads(m['access_manifest_original'])['files']['code.py']}, 'actual_read': None}
            if phase == 'PostToolUse':
                row['tool_response_sha256'] = r.digest(r.encoded(output))
                row['pre_observation_sha256'] = r.digest(json.loads(journal[0])['observation_original'].encode())
                row['actual_read'] = {'path': 'code.py', 'start_line': start, 'end_line': start + count - 1,
                                      'returned_line_count': count, 'total_lines': 2, 'truncated_by_token_cap': False,
                                      'fragment_sha256': r.digest(text.encode()), 'returned_content_sha256': r.digest(text.encode())}
            journal.append(r.encoded({'observation_original': r.encoded(row).decode(), 'hook_input_original': r.encoded(hook).decode()}))
    events.append({'type': 'assistant', 'session_id': m['session_id'], 'message': {'model': r.MODEL, 'content': content}})
    if tools:
        events.append({'type': 'user', 'session_id': m['session_id'], 'message': {'content': [
            {'type': 'tool_result', 'tool_use_id': tool_id, 'content': 'Synthetic formatted tool response', 'is_error': False}]}})
    events.append({'type': 'result', 'subtype': 'success', 'is_error': False, 'session_id': m['session_id'],
                   'modelUsage': {r.MODEL: {'canonicalModel': r.MODEL, 'inputTokens': 1}}, 'structured_output': result})
    originals['protocol'] = b''.join((json.dumps(event) + '\n').encode() for event in events)
    originals['journal'] = journal
    return originals


def events(originals):
    return [json.loads(line) for line in originals['protocol'].splitlines()]


def replace_events(originals, value):
    originals['protocol'] = b''.join((json.dumps(row) + '\n').encode() for row in value)


def mutate_json(originals, key, change):
    value = json.loads(originals[key]); change(value); originals[key] = r.encoded(value)


def test_complete_read_and_auxiliary_usage_are_separate_from_assistant_identity():
    m, p = fixture_manifest(); a = fixture_attempt(m, p)
    e = events(a); e[-1]['modelUsage'][r.AUXILIARY_USAGE] = {'canonicalModel': r.AUXILIARY_USAGE}; replace_events(a, e)
    result = r.validate_session(m, [a])
    assert result['status'] == 'APPROVE' and result['required_ranges_missing'] == {}
    assert result['attempts'][0]['provider_model'] == r.MODEL
    assert r.AUXILIARY_USAGE in result['attempts'][0]['usage_models']
    assert result['approval_confers_deployment_authority'] is False


@pytest.mark.parametrize('name', ['/etc/passwd', '../patient.csv', 'dir/../secret', 'dir//x', 'dir/./x', 'x\\y'])
def test_manifest_rejects_noncanonical_paths(name):
    raw, _ = fixture_manifest(); m = json.loads(raw); access = json.loads(m['access_manifest_original'])
    access['files'][name] = access['files'].pop('code.py')
    m['access_manifest_original'] = r.encoded(access).decode(); m['access_manifest_sha256'] = r.digest(r.encoded(access))
    with pytest.raises(ValueError): r.validate_manifest(r.encoded(m))


@pytest.mark.parametrize('field', ['source', 'scope', 'session_id', 'manifest_sha256'])
def test_changed_request_binding_never_progresses(field):
    m, p = fixture_manifest(); a = fixture_attempt(m, p)
    mutate_json(a, 'request', lambda q: q.__setitem__(field, 'changed'))
    assert r.parse_attempt(m, a)['status'] == 'RECONCILIATION_REQUIRED'


@pytest.mark.parametrize('mutation', ['timeout', 'missing_return', 'nonzero', 'partial', 'duplicate_result', 'wrong_session',
                                      'assistant_opus', 'usage_opus', 'unknown_auxiliary', 'fallback', 'extra_tool', 'mcp'])
def test_uncertain_identity_and_refusal_are_not_progress(mutation):
    m, p = fixture_manifest(); a = fixture_attempt(m, p, status='IN_PROGRESS'); e = events(a)
    if mutation == 'timeout': a['timeout'] = r.encoded({'status': 'RECONCILE_ORIGINAL_PROCESS'})
    if mutation == 'missing_return': a['returned'] = None
    if mutation == 'nonzero': mutate_json(a, 'returned', lambda q: q.__setitem__('returncode', 1))
    if mutation == 'partial': e.pop()
    if mutation == 'duplicate_result': e.append(copy.deepcopy(e[-1]))
    if mutation == 'wrong_session': e[-1]['session_id'] = '22222222-2222-2222-2222-222222222222'
    if mutation == 'assistant_opus': e[1]['message']['model'] = 'claude-opus-5'
    if mutation == 'usage_opus': e[-1]['modelUsage'] = {'claude-opus-5': {}}
    if mutation == 'unknown_auxiliary': e[-1]['modelUsage']['unknown-model'] = {}
    if mutation == 'fallback': e.insert(-1, {'type': 'system', 'subtype': 'model_refusal_fallback', 'session_id': json.loads(m)['session_id']})
    if mutation == 'extra_tool': e[0]['tools'].append('Bash')
    if mutation == 'mcp': e[0]['mcp_servers'] = [{'name': 'unexpected'}]
    replace_events(a, e)
    assert r.validate_session(m, [a])['status'] == 'RECONCILIATION_REQUIRED'


@pytest.mark.parametrize('mutation', ['no_journal', 'no_pre', 'duplicate_post', 'denied', 'hash', 'range', 'source', 'tool_id', 'reorder', 'truncated'])
def test_host_journal_must_qualify_actual_read(mutation):
    m, p = fixture_manifest(); a = fixture_attempt(m, p)
    rows = [json.loads(raw) for raw in a['journal']]
    for row in rows:
        row['observation'] = json.loads(row.pop('observation_original'))
    if mutation == 'no_journal': rows = []
    elif mutation == 'no_pre': rows = rows[1:]
    elif mutation == 'duplicate_post': rows[0] = copy.deepcopy(rows[1])
    elif mutation == 'denied': rows[0]['observation']['status'] = 'DENIED'
    elif mutation == 'hash': rows[1]['observation']['tool_response_sha256'] = '0' * 64
    elif mutation == 'range': rows[1]['observation']['actual_read']['end_line'] = 99
    elif mutation == 'source': rows[1]['observation']['source'] = 'b' * 40
    elif mutation == 'tool_id': rows[1]['observation']['tool_use_id'] = 'orphan'
    elif mutation == 'reorder': rows.reverse()
    elif mutation == 'truncated':
        hook = json.loads(rows[1]['hook_input_original']); hook['tool_response']['file']['truncatedByTokenCap'] = True
        rows[1]['hook_input_original'] = r.encoded(hook).decode()
        rows[1]['observation']['raw_input_sha256'] = r.digest(r.encoded(hook))
        rows[1]['observation']['tool_response_sha256'] = r.digest(r.encoded(hook['tool_response']))
        # Claimed truncation flag is inconsistent with the unmodified actual-read journal.
    for row in rows:
        row['observation_original'] = r.encoded(row.pop('observation')).decode()
    a['journal'] = [r.encoded(row) for row in rows]
    assert r.parse_attempt(m, a)['status'] == 'RECONCILIATION_REQUIRED'


def test_model_claim_does_not_satisfy_required_read():
    m, p = fixture_manifest(); a = fixture_attempt(m, p, tools=False)
    with pytest.raises(ValueError, match='UNRESOLVED_COVERAGE'): r.validate_session(m, [a])


def test_two_explicit_attempts_accumulate_read_coverage_and_keep_obligations():
    m, p = fixture_manifest(); a = fixture_attempt(m, p, status='IN_PROGRESS', start=1, count=1)
    e = events(a); e[-1]['structured_output']['questions'] = ['Explain line2']; replace_events(a, e)
    first = r.parse_attempt(m, a)
    b = fixture_attempt(m, p, number=2, previous=first, start=2, count=1)
    e = events(b); e[-1]['structured_output']['resolved'] = [{'field': 'questions', 'original': 'Explain line2', 'response': 'Read line2; synthetic response.'}]; replace_events(b, e)
    assert r.validate_session(m, [a, b])['status'] == 'APPROVE'
    e[-1]['structured_output']['resolved'] = []; replace_events(b, e)
    with pytest.raises(ValueError, match='PRIOR_OBLIGATION_DROPPED'): r.validate_session(m, [a, b])


@pytest.mark.parametrize('status', ['APPROVE', 'REQUEST_CHANGES'])
def test_terminal_cannot_resume(status):
    m, p = fixture_manifest(); a = fixture_attempt(m, p, status=status)
    b = fixture_attempt(m, p, number=2, previous=r.parse_attempt(m, a))
    with pytest.raises(ValueError, match='TERMINAL_REVIEW'): r.validate_session(m, [a, b])


def test_fallback_in_first_attempt_cannot_be_cured_by_later_fable():
    m, p = fixture_manifest(); a = fixture_attempt(m, p, status='IN_PROGRESS')
    e = events(a); e.insert(-1, {'type': 'system', 'subtype': 'model_refusal_fallback'}); replace_events(a, e)
    b = fixture_attempt(m, p, number=2, previous=r.parse_attempt(m, a))
    assert r.validate_session(m, [a, b])['status'] == 'RECONCILIATION_REQUIRED'


@pytest.mark.parametrize('kind', ['missing', 'source', 'duplicate', 'policy', 'attempt'])
def test_admission_is_original_bound_per_attempt(kind):
    m, p = fixture_manifest(); a = fixture_attempt(m, p)
    if kind == 'missing': a['admission_receipt'] = None
    if kind == 'source': mutate_json(a, 'admission_receipt', lambda q: q.__setitem__('source', '0' * 40))
    if kind == 'duplicate': mutate_json(a, 'admission_receipt', lambda q: q.__setitem__('duplicate_admission', True))
    if kind == 'policy': a['admission_policy'] = r.encoded({'status': 'UNRATIFIED'})
    if kind == 'attempt': mutate_json(a, 'admission_event', lambda q: q.__setitem__('attempt', '2'))
    assert r.parse_attempt(m, a)['status'] == 'RECONCILIATION_REQUIRED'


def test_maximum_attempts_bound_and_duplicate_json_reject():
    m, p = fixture_manifest(); value = json.loads(m); value['max_attempts'] = 0
    with pytest.raises(ValueError, match='MAXIMUM_ATTEMPTS'): r.validate_manifest(r.encoded(value))
    with pytest.raises(ValueError, match='DUPLICATE_JSON_KEY'): r.validate_manifest(b'{"schema":1,"schema":2}')


def test_exact_access_original_bytes_are_not_canonicalized():
    m, p = fixture_manifest(); value = json.loads(m)
    value['access_manifest_original'] = json.dumps(json.loads(value['access_manifest_original']), separators=(',', ':'))
    with pytest.raises(ValueError, match='ACCESS_MANIFEST_DIGEST'): r.validate_manifest(r.encoded(value))
    value['access_manifest_sha256'] = r.digest(value['access_manifest_original'].encode())
    assert r.validate_manifest(r.encoded(value))['access_manifest_sha256'] == value['access_manifest_sha256']


@pytest.mark.parametrize('kind', ['hook', 'native_without_hooks', 'native_after_allowed_pre'])
def test_genuine_denial_needs_no_invented_post_and_does_not_claim_coverage(kind):
    m, p = fixture_manifest(); a = fixture_attempt(m, p, status='IN_PROGRESS')
    e = events(a); e[2]['message']['content'][0]['is_error'] = True
    use = e[1]['message']['content'][0]
    a['journal'] = a['journal'][:1]
    if kind == 'hook':
        wrapper = json.loads(a['journal'][0]); row = json.loads(wrapper['observation_original'])
        row['status'] = 'DENIED'; wrapper['observation_original'] = r.encoded(row).decode()
        a['journal'] = [r.encoded(wrapper)]
    else:
        if kind == 'native_without_hooks': a['journal'] = []
        e[-1]['permission_denials'] = [{'tool_name': use['name'], 'tool_use_id': use['id'], 'tool_input': use['input']}]
    replace_events(a, e)
    result = r.validate_session(m, [a])
    assert result['status'] == 'IN_PROGRESS'
    assert result['reads'] == {} and result['required_ranges_missing'] == {'code.py': [[1, 2]]}
    assert len(result['attempts'][0]['denials']) == 1


def test_unexplained_tool_error_without_hooks_is_not_native_permission_denial():
    m, p = fixture_manifest(); a = fixture_attempt(m, p, status='IN_PROGRESS'); a['journal'] = []
    e = events(a); e[2]['message']['content'][0]['is_error'] = True; replace_events(a, e)
    assert r.parse_attempt(m, a)['status'] == 'RECONCILIATION_REQUIRED'


def test_partial_truncated_read_only_covers_actual_returned_lines():
    m, p = fixture_manifest(); a = fixture_attempt(m, p, status='IN_PROGRESS', count=1)
    wrapper = json.loads(a['journal'][1]); row = json.loads(wrapper['observation_original']); hook = json.loads(wrapper['hook_input_original'])
    hook['tool_response']['file']['truncatedByTokenCap'] = True
    row['actual_read']['truncated_by_token_cap'] = True
    row['raw_input_sha256'] = r.digest(r.encoded(hook)); row['tool_response_sha256'] = r.digest(r.encoded(hook['tool_response']))
    wrapper['observation_original'] = r.encoded(row).decode(); wrapper['hook_input_original'] = r.encoded(hook).decode()
    a['journal'][1] = r.encoded(wrapper)
    result = r.validate_session(m, [a])
    assert result['status'] == 'IN_PROGRESS' and result['required_ranges_missing'] == {'code.py': [[2, 2]]}


def test_fragment_hash_is_not_an_unverified_coverage_assertion():
    m, p = fixture_manifest(); a = fixture_attempt(m, p)
    wrapper = json.loads(a['journal'][1]); row = json.loads(wrapper['observation_original'])
    row['actual_read']['fragment_sha256'] = '0' * 64
    wrapper['observation_original'] = r.encoded(row).decode(); a['journal'][1] = r.encoded(wrapper)
    assert r.parse_attempt(m, a)['status'] == 'RECONCILIATION_REQUIRED'


def test_orphan_tool_result_is_not_accepted_as_unrelated_evidence():
    m, p = fixture_manifest(); a = fixture_attempt(m, p); e = events(a)
    e[2]['message']['content'].append({'type': 'tool_result', 'tool_use_id': 'unrecorded', 'content': 'invented'})
    replace_events(a, e)
    assert r.parse_attempt(m, a)['status'] == 'RECONCILIATION_REQUIRED'


def test_native_denial_needs_verified_permission_probe_not_an_error_string():
    m, p = fixture_manifest(); a = fixture_attempt(m, p, status='IN_PROGRESS'); a['journal'] = []
    e = events(a); use = e[1]['message']['content'][0]; e[2]['message']['content'][0]['is_error'] = True
    e[-1]['permission_denials'] = [{'tool_name': 'Read', 'tool_use_id': use['id'], 'tool_input': use['input']}]
    replace_events(a, e)
    a['permission_probe'] = r.encoded({'schema': 'inspection-permission-probe/v1', 'status': 'NOT_RUN'})
    assert r.parse_attempt(m, a)['status'] == 'RECONCILIATION_REQUIRED'


def test_required_coverage_cannot_be_silently_satisfied_by_partial_read():
    m, p = fixture_manifest(); a = fixture_attempt(m, p, count=1)
    with pytest.raises(ValueError, match='UNRESOLVED_COVERAGE'): r.validate_session(m, [a])


def test_terminal_request_changes_remains_terminal_with_no_file_coverage():
    m, p = fixture_manifest(); a = fixture_attempt(m, p, status='REQUEST_CHANGES', tools=False)
    result = r.validate_session(m, [a])
    assert result['status'] == 'REQUEST_CHANGES'
    assert result['required_ranges_missing'] == {'code.py': [[1, 2]]}


def test_explicit_original_only_reconciliation_can_validate_recovered_completion():
    m, p = fixture_manifest(); a = fixture_attempt(m, p)
    a['timeout'] = r.encoded({'status': 'RECONCILE_ORIGINAL_PROCESS', 'pid': 123, 'process_not_killed': True})
    assert r.parse_attempt(m, a)['status'] == 'RECONCILIATION_REQUIRED'
    manifest = json.loads(m)
    proof = {'schema': 'formal-inspection-reconciliation/v1', 'status': 'ORIGINAL_PROCESS_ENDED_VERIFIED',
             'source': manifest['source'], 'manifest_sha256': r.digest(m), 'session_id': manifest['session_id'],
             'attempt': 1, 'actor': manifest['actor'], 'provider_invocations': 0,
             **{key + '_sha256': r.digest(a[key]) for key in ('request', 'process', 'timeout', 'returned', 'protocol')}}
    a['reconciliation'] = r.encoded(proof)
    assert r.validate_session(m, [a])['status'] == 'APPROVE'
    proof['provider_invocations'] = 1; a['reconciliation'] = r.encoded(proof)
    assert r.parse_attempt(m, a)['status'] == 'RECONCILIATION_REQUIRED'


def test_reconciliation_does_not_cure_fallback_or_partial_protocol():
    m, p = fixture_manifest(); a = fixture_attempt(m, p); e = events(a)
    e.insert(-1, {'type': 'system', 'subtype': 'model_refusal_fallback'}); replace_events(a, e)
    a['timeout'] = r.encoded({'status': 'RECONCILE_ORIGINAL_PROCESS', 'pid': 123})
    manifest = json.loads(m)
    a['reconciliation'] = r.encoded({'schema': 'formal-inspection-reconciliation/v1',
        'status': 'ORIGINAL_PROCESS_ENDED_VERIFIED', 'source': manifest['source'], 'manifest_sha256': r.digest(m),
        'session_id': manifest['session_id'], 'attempt': 1, 'actor': manifest['actor'], 'provider_invocations': 0,
        **{key + '_sha256': r.digest(a[key]) for key in ('request', 'process', 'timeout', 'returned', 'protocol')}})
    assert r.parse_attempt(m, a)['status'] == 'RECONCILIATION_REQUIRED'
