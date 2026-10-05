"""Material bridge checks against native coverage/selection helpers, no provider."""
import copy
import json
import pytest
from orchestrator import inspection_deployment as d
from orchestrator import inspection_review as r
from orchestrator import inspection_access as access
from orchestrator import deployment_review as g
from orchestrator import change_requests as cr
from test_inspection_review import fixture_manifest, fixture_attempt


def material_fixture(*, omit_reads=(), omit_required=(), status='APPROVE', bad_context=False, empty_recovery=False, old_plan=False):
    manifest_raw, policy = fixture_manifest(); m = json.loads(manifest_raw)
    names = set(g.REQUIRED_TEMPLATES) | set(g.PART_COMMON_FILES) | set(g.INTEGRATION_FILES)
    source_files = {name: b'# synthetic source fixture\n' for name in names}
    direction, guidance = b'Synthetic direction, no real permission.\n', b'Synthetic guidance.\n'
    authority = r.encoded({'direction_path': 'docs/fixture-direction.md', 'direction_sha256': r.digest(direction)})
    source_files.update({'docs/fixture-direction.md': direction, 'docs/fixture-guidance.md': guidance,
                         'configs/fixture-authority.json': authority,
                         'configs/scientific-operating-context.json': r.encoded({
                             'authority_policy': {'path': 'configs/fixture-authority.json', 'sha256': r.digest(authority)},
                             'documents': {'docs/fixture-guidance.md': r.digest(guidance)}})})
    installed = {name: raw for name, raw in source_files.items() if name not in g.REFERENCE_ONLY_FILES}
    current, old, recovery = b'current fixture config\n', b'previous fixture config\n', b'fixture recovery\n'
    if empty_recovery: recovery = b''
    selected = [{'request': '3' * 64, 'applied': '4' * 64}]
    proposal = {'source': m['source'], 'review_profile': d.PROFILE,
                'source_files': {name: r.digest(raw) for name, raw in installed.items()}, 'changes': selected,
                'targets': {'/etc/fixture.json': {'sha256': r.digest(current), 'uid': 0, 'gid': 987, 'mode': 384}},
                'previous_files': {'/etc/fixture.json': {'sha256': r.digest(old), 'uid': 0, 'gid': 987, 'mode': 384}},
                'recovery_sha256': r.digest(recovery)}
    if old_plan: proposal['review_plan_sha256'] = '8' * 64
    proposal_raw = r.encoded(proposal)
    binding_raw = r.encoded(cr.review_bindings(m['source'], r.digest(proposal_raw), selected))
    changes_raw = r.encoded([{'store': 'SYNTHETIC', 'projection': {'selected_applications': [{
        'request': selected[0]['request'], 'event': {'identity': selected[0]['applied'], 'event': 'APPLIED',
            'payload': {'result_binding': {'source': m['source']}}}}]}}])
    context_raw = b'{"qualification":"SYNTHETIC operating context"}\n'
    view = {'source/' + name: raw for name, raw in source_files.items()}
    view.update({'code.py': b'a\nb\n', 'evidence/proposal.json': proposal_raw, 'evidence/changes.json': changes_raw,
                 'evidence/change-bindings.json': binding_raw, 'evidence/current.txt': current,
                 'evidence/previous.txt': old, 'evidence/recovery.txt': recovery})
    required = {name: raw for name, raw in view.items() if name != 'code.py' and name not in omit_required}
    am = {'schema': 'inspection-access-manifest/v1', 'source': m['source'], 'files': {
        name: {'sha256': r.digest(raw), 'bytes': len(raw), 'line_count': len(raw.decode().splitlines(keepends=True))}
        for name, raw in view.items()}}
    m.update(scope='material-deployment', proposal_sha256=r.digest(proposal_raw), context_sha256=r.digest(context_raw),
             changes_sha256=r.digest(changes_raw), change_bindings_sha256=r.digest(binding_raw),
             access_manifest_original=r.encoded(am).decode(), access_manifest_sha256=r.digest(r.encoded(am)),
             required_ranges={name: ([[1, am['files'][name]['line_count']]] if am['files'][name]['line_count'] else [])
                              for name in required if name not in omit_reads})
    manifest_raw = r.encoded(m)
    originals = fixture_attempt(manifest_raw, policy, status=status)
    request = json.loads(originals['request'])
    request['prompt'] += d.CONTEXT_START + (b'wrong' if bad_context else context_raw).decode() + d.CONTEXT_END
    originals['request'] = r.encoded(request)
    intent = json.loads(originals['intent']); intent['request_sha256'] = r.digest(originals['request']); originals['intent'] = r.encoded(intent)
    initial = [json.loads(line) for line in originals['protocol'].splitlines()]
    events, journal = [initial[0]], []
    for index, (name, raw) in enumerate(view.items()):
        if name in omit_reads:
            continue
        key = 'read-' + str(index); lines = len(raw.decode().splitlines(keepends=True))
        inp = {'file_path': '/review/' + name, 'offset': 1, 'limit': max(1, lines)}
        use = {'type': 'tool_use', 'id': key, 'name': 'Read', 'input': inp}
        output = {'type': 'text', 'file': {'filePath': '/review/' + name, 'content': raw.decode(),
                                          'numLines': lines, 'startLine': 1, 'totalLines': lines}}
        events.append({'type': 'assistant', 'session_id': m['session_id'], 'message': {'model': r.MODEL, 'content': [use]}})
        events.append({'type': 'user', 'session_id': m['session_id'], 'message': {'content': [{
            'type': 'tool_result', 'tool_use_id': key, 'content': raw.decode(), 'is_error': False}]}})
        pre_raw = None
        for phase in ('PreToolUse', 'PostToolUse'):
            hook = {'session_id': m['session_id'], 'cwd': '/review', 'permission_mode': 'dontAsk',
                    'tool_use_id': key, 'tool_name': 'Read', 'tool_input': inp, 'hook_event_name': phase}
            if phase == 'PostToolUse': hook['tool_response'] = output
            row = {'schema': 'inspection-tool-observation/v1', 'phase': phase, 'source': m['source'],
                   'access_manifest_sha256': m['access_manifest_sha256'], 'session_id': m['session_id'], 'attempt_id': '1',
                   'tool_use_id': key, 'tool_name': 'Read', 'request_sha256': r.digest(r.encoded(inp)),
                   'raw_input_sha256': r.digest(r.encoded(hook)), 'normalized_request': access.normalize_request(am, 'Read', inp),
                   'status': 'ALLOWED' if phase == 'PreToolUse' else 'OBSERVED', 'observed_files': {}, 'actual_read': None}
            if phase == 'PostToolUse':
                row.update(pre_observation_sha256=r.digest(pre_raw), tool_response_sha256=r.digest(r.encoded(output)),
                           observed_files={name: am['files'][name]}, actual_read=access.verify_read_response(am, row['normalized_request'], output, raw))
            observation_raw = r.encoded(row)
            if phase == 'PreToolUse': pre_raw = observation_raw
            journal.append(r.encoded({'observation_original': observation_raw.decode(), 'hook_input_original': r.encoded(hook).decode()}))
    terminal = initial[-1]; terminal['structured_output']['claimed_inspected_files'] = [name for name in view if name not in omit_reads]
    events.append(terminal)
    originals['protocol'] = b''.join((json.dumps(event) + '\n').encode() for event in events); originals['journal'] = journal
    response_raw = r.encoded(terminal)
    execution = {'schema': 'formal-inspection-execution/v1', 'reviewed_commit': m['source'], 'requested_model': r.MODEL,
                 'assistant_message_models': [r.MODEL], 'actual_usage_models': [r.MODEL], 'returncode': 0,
                 'request_sha256': r.digest(originals['request']), 'response_sha256': r.digest(response_raw),
                 'protocol_sha256': r.digest(originals['protocol']), 'prompt_sha256': r.digest(request['prompt'].encode()),
                 'session_id': m['session_id'], 'runtime_sha256': m['pins']['runtime_sha256'],
                 'manifest_sha256': r.digest(manifest_raw), 'context_sha256': m['context_sha256']}
    return {'manifest_raw': manifest_raw, 'attempts': [{'originals': originals, 'response_raw': response_raw, 'execution_raw': r.encoded(execution)}],
            'view_files': view, 'required_files': required, 'source': m['source'], 'scope': m['scope'],
            'proposal_raw': proposal_raw, 'changes_raw': changes_raw, 'context_raw': context_raw}


def test_native_coverage_and_actual_originals_produce_labeled_metadata_only():
    f = material_fixture(); result = d.validate_deployment_session(**f)
    last = f['attempts'][-1]
    assert result['actual_request'] == json.loads(last['originals']['request'])
    assert 'metadata_projection' not in result['actual_request']
    assert result['request']['metadata_projection'] == 'DERIVED_FROM_VALIDATED_INSPECTION_ORIGINALS'
    assert result['response'] == json.loads(last['response_raw'])
    assert result['execution']['response_sha256'] == r.digest(last['response_raw'])
    assert result['changes'] == json.loads(f['changes_raw'])
    assert result['full_original_wrapper_index_sha256'] == r.digest(r.encoded(result['original_attempt_file_sha256']))
    assert result['approval_confers_deployment_authority'] is False


@pytest.mark.parametrize('name', ['source/orchestrator/hosted_context.py', 'evidence/changes.json',
                                 'evidence/change-bindings.json', 'evidence/proposal.json',
                                 'evidence/current.txt', 'evidence/previous.txt', 'evidence/recovery.txt'])
def test_available_but_unread_required_content_cannot_be_approval_evidence(name):
    f = material_fixture(omit_reads=(name,))
    with pytest.raises(ValueError): d.validate_deployment_session(**f)


def test_caller_cannot_shorten_native_required_source_map():
    f = material_fixture(omit_required=('source/orchestrator/hosted_context.py',))
    with pytest.raises(ValueError, match='NATIVE_REQUIRED_SOURCE_OMITTED'): d.validate_deployment_session(**f)


@pytest.mark.parametrize('kind', ['missing', 'bytes', 'extra'])
def test_exact_view_inventory_and_raw_bytes_are_bound(kind):
    f = material_fixture()
    if kind == 'missing': f['view_files'].pop('evidence/current.txt')
    if kind == 'bytes': f['view_files']['evidence/current.txt'] = b'changed\n'
    if kind == 'extra': f['view_files']['unlisted-secret'] = b'never permitted'
    with pytest.raises(ValueError): d.validate_deployment_session(**f)


@pytest.mark.parametrize('kind', ['response', 'execution', 'context', 'changes', 'proposal', 'source', 'scope'])
def test_altered_original_or_scope_is_not_reconstructed_into_approval(kind):
    f = material_fixture()
    if kind == 'response': f['attempts'][0]['response_raw'] = r.encoded({'structured_output': {'status': 'APPROVE'}})
    if kind == 'execution':
        ex = json.loads(f['attempts'][0]['execution_raw']); ex['response_sha256'] = '0' * 64
        f['attempts'][0]['execution_raw'] = r.encoded(ex)
    if kind in ('context', 'changes', 'proposal'): f[kind + '_raw'] += b' '
    if kind == 'source': f['source'] = 'b' * 40
    if kind == 'scope': f['scope'] = 'human-controls'
    with pytest.raises(ValueError): d.validate_deployment_session(**f)


def test_context_hash_or_read_availability_does_not_replace_actual_first_prompt():
    with pytest.raises(ValueError, match='CONTEXT_NOT_IN_FIRST_ACTUAL_PROMPT'):
        d.validate_deployment_session(**material_fixture(bad_context=True))


def test_terminal_request_changes_is_never_material_approval():
    with pytest.raises(ValueError, match='FULL_TERMINAL_APPROVAL_REQUIRED'):
        d.validate_deployment_session(**material_fixture(status='REQUEST_CHANGES'))


def test_empty_required_file_needs_an_actual_empty_read():
    result = d.validate_deployment_session(**material_fixture(empty_recovery=True))
    assert result['private_text'][r.digest(b'')] == b''
    with pytest.raises(ValueError):
        d.validate_deployment_session(**material_fixture(empty_recovery=True, omit_reads=('evidence/recovery.txt',)))


def test_new_profile_does_not_reinterpret_a_two_part_plan():
    with pytest.raises(ValueError, match='EXPLICIT_PROFILE_REQUIRED'):
        d.validate_deployment_session(**material_fixture(old_plan=True))
