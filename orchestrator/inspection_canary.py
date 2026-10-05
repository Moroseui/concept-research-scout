"""Pure verification of two original native synthetic boundary attempts.

The root runner authenticates and preserves originals; hashes alone do not prove
host provenance. This receipt confers no review approval or launch authority.
"""
import copy
import re
from pathlib import Path
from orchestrator import inspection_access as access
from orchestrator import inspection_review as review
from orchestrator import inspection_runtime as runtime
from orchestrator import inspection_model_policy as model_policy

encoded, digest, parsed, require = access.encoded, access.digest, review._json, access.require
PHASES = ('baseline', 'hooks')
READ_BOUNDARY_VERSION = 'native-read-size-and-crlf/v1'
TOKEN_READ_BOUNDARY_VERSION = 'native-read-token-limit-and-crlf/v2'
READ_BOUNDARY_VERSIONS = (READ_BOUNDARY_VERSION, TOKEN_READ_BOUNDARY_VERSION)
READ_BOUNDARY_NAME = 'READ_BOUNDARY.txt'


def read_boundary_literal(version=READ_BOUNDARY_VERSION):
    # Retain the original byte-limit fixture exactly. The prospective fixture
    # exercises the token limit with an explicit range and the same five calls.
    require(version in READ_BOUNDARY_VERSIONS, 'CANARY_READ_BOUNDARY_VERSION')
    prefix = b'Synthetic first CRLF.\r\nSynthetic middle LF.\nSynthetic final CRLF.\r\n'
    if version == TOKEN_READ_BOUNDARY_VERSION:
        return prefix + b''.join((digest(('synthetic-token-boundary-'+str(i)).encode())+'\n').encode()
                                 for i in range(4096))
    return prefix + (b'x' * 63 + b'\n') * 4096


def canary_calls(nonce, phase, *, read_boundary=False, read_boundary_version=READ_BOUNDARY_VERSION):
    require(phase in PHASES and type(read_boundary) is bool
            and read_boundary_version in READ_BOUNDARY_VERSIONS, 'CANARY_CALL_PHASE')
    calls = [('Read', {'file_path': '/state/canary/probe.txt'}),
             ('Glob', {'path': '/state/canary', 'pattern': 'probe.txt'}),
             ('Grep', {'path': '/state/canary', 'pattern': nonce})]
    if phase == 'hooks' and read_boundary:
        failed_read = {'file_path': '/review/' + READ_BOUNDARY_NAME}
        if read_boundary_version == TOKEN_READ_BOUNDARY_VERSION:
            failed_read.update(offset=1, limit=len(read_boundary_literal(read_boundary_version).splitlines()))
        calls += [('Read', failed_read),
                  ('Read', {'file_path': '/review/' + READ_BOUNDARY_NAME, 'offset': 1, 'limit': 3})]
    else:
        calls += [('Read', {'file_path': '/review/CANARY.txt'})]
    return calls


def require_read_boundary(proof, *, read_failure_policy=None):
    require(read_failure_policy in (None, access.READ_TOKEN_FAILURE_POLICY),
            'INSPECTION_READ_FAILURE_POLICY')
    version = TOKEN_READ_BOUNDARY_VERSION if read_failure_policy else READ_BOUNDARY_VERSION
    require(proof.get('read_boundary_version') == version
            and all(proof.get(key) is True for key in
                    ('oversized_read_failure_verified', 'bounded_read_after_failure_verified',
                      'crlf_display_verified')), 'INSPECTION_CURRENT_READ_BOUNDARY_REQUIRED')
    if read_failure_policy:
        require(proof.get('token_limit_failure_verified') is True,
                'INSPECTION_CURRENT_TOKEN_BOUNDARY_REQUIRED')


# Exact CLI whose Read.validateInput denial shape was independently inspected.
READ_VALIDATION_DENIAL_CLI_SHA256 = review.READ_VALIDATION_DENIAL_CLI_SHA256
RAW_NAMES = ('request.json', 'command.json', 'settings.json', 'execution.json',
             'intent.json', 'process.json', 'protocol.jsonl', 'admission_event.json',
             'admission_receipt.json', 'admission_policy.json', 'returned.json',
             'CANARY.txt.after', 'probe.txt.before', 'confinement-readback.json')


def phase_settings(normal, phase):
    """The only two reviewed deviations from the unchanged full-run settings."""
    require(normal == access.access_settings() and phase in PHASES, 'CANARY_NORMAL_SETTINGS')
    result = copy.deepcopy(normal)
    if phase == 'baseline':
        result['hooks'] = {}
    else:
        result['permissions']['deny'] = [item for item in result['permissions']['deny']
                                         if item not in ('Read(//state)', 'Read(//state/**)')]
        result['permissions']['allow'] = ['Read(//state/canary/**)']
    return result


def _protocol(raw, session, *, policy_version=None, runtime_cli_sha256=None, journal=(), expected_tools=4):
    require(isinstance(raw, bytes) and 0 < len(raw) <= 16000000, 'CANARY_PROTOCOL_BOUND')
    events = [parsed(line) for line in raw.splitlines() if line.strip()]
    require(all(isinstance(e, dict) for e in events), 'CANARY_EVENT_SCHEMA')
    init = [e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init']
    final = [e for e in events if e.get('type') == 'result']
    require(len(init) == len(final) == 1 and events[0] is init[0] and events[-1] is final[0], 'CANARY_TERMINAL')
    first, last = init[0], final[0]
    require(first.get('model') == model_policy.requested_model(policy_version) and first.get('permissionMode') == 'dontAsk'
            and first.get('mcp_servers') == [] and set(first.get('tools', [])) in
            ({'Read', 'Glob', 'Grep'}, set(review.TOOLS)), 'CANARY_NATIVE_PROFILE')
    require(first.get('session_id') == last.get('session_id') == session and
            all(e.get('session_id', session) == session for e in events), 'CANARY_SESSION')
    models = {e.get('message', {}).get('model') for e in events if e.get('type') == 'assistant'}
    usage = last.get('modelUsage')
    model_policy.version(policy_version)
    attribution = None
    if policy_version is not None:
        attribution = model_policy.analyze(events, session_id=session,
            runtime_cli_sha256=runtime_cli_sha256, journal=journal, policy_version=policy_version)
    else:
        require(models == {review.MODEL} and review.usage_identity_matches(usage), 'CANARY_MODEL_IDENTITY')
        require(not any(e.get('subtype') == 'model_refusal_fallback' for e in events), 'CANARY_PROVIDER_FALLBACK')
    require(last.get('subtype') == 'success' and last.get('is_error') is False
            and type(last.get('num_turns')) is int and 1 <= last['num_turns'] <= 8, 'CANARY_RESULT')
    uses, results, outputs = {}, {}, {}
    for e in events:
        content = e.get('message', {}).get('content', [])
        for item in content if isinstance(content, list) else []:
            if item.get('type') == 'tool_use':
                key = item.get('id')
                require(e.get('type') == 'assistant' and isinstance(key, str) and
                        re.fullmatch('[A-Za-z0-9_-]{1,128}', key) and key not in uses, 'CANARY_TOOL_ID')
                uses[key] = item
            elif item.get('type') == 'tool_result':
                key = item.get('tool_use_id')
                require(e.get('type') == 'user' and key in uses and key not in results, 'CANARY_RESULT_ID')
                results[key], outputs[key] = item, e.get('tool_use_result')
    require(set(uses) == set(results), 'CANARY_ALL_TOOL_RESULTS')
    structured = {k for k, u in uses.items() if u.get('name') == 'StructuredOutput'}
    require(len(structured) <= 1 and all(not results[k].get('is_error', False) for k in structured), 'CANARY_STRUCTURED_RESULT')
    classified = {row['tool_use_id'] for row in attribution['unexecuted_retracted']} if attribution else set()
    uses = {k: u for k, u in uses.items() if k not in structured and k not in classified}
    require(type(expected_tools) is int and expected_tools in (4, 5) and len(uses) == expected_tools,
            'CANARY_EXPECTED_COMPLETED_TOOLS')
    return events, last, uses, results, outputs, sorted(models)


def baseline_denials_match(terminal, uses, results, outputs, outside, cli_sha256):
    """Match native denial originals without treating arbitrary tool errors as denials.

    Read.validateInput can refuse a denied directory before the CLI's terminal
    denial collector. Only its exact paired error originals may stand in for
    the missing fixed outside-Read row. Glob/Grep still require their rows.
    """
    denials = terminal.get('permission_denials')
    if not isinstance(denials, list) or len(outside) != 3 or not all(
            results[k].get('is_error') is True for k in outside):
        return False
    expected = {k: {'tool_name': uses[k]['name'], 'tool_use_id': k,
                    'tool_input': uses[k]['input']} for k in outside}
    if sorted(encoded(d) for d in denials) == sorted(encoded(d) for d in expected.values()):
        return True
    if cli_sha256 != READ_VALIDATION_DENIAL_CLI_SHA256:
        return False
    reads = [k for k in outside if uses[k]['name'] == 'Read' and
             uses[k]['input'] == {'file_path': '/state/canary/probe.txt'}]
    if len(reads) != 1:
        return False
    key = reads[0]
    if sorted(encoded(d) for d in denials) != sorted(encoded(d) for k, d in expected.items() if k != key):
        return False
    return review.native_read_input_validation_denied(
        uses[key], results[key], outputs[key], runtime_cli_sha256=cli_sha256)


def validate_canary_mounts(command, execution, session_id, probe):
    """Check the exact native mount prefix, including the optional census mask.

    Reuse the auth renderer: a census canary directory is masked first, then
    only the fixed synthetic probe overlays it. No other mount may hide either
    the probe or a preceding auth mask. This is a pure argv check, not OS proof.
    """
    require(isinstance(command, list) and all(isinstance(v, str) for v in command)
            and command.count('/runtime/claude') == 1,
            'CANARY_REACHABLE_SYNTHETIC_MOUNT')
    require(execution['reviewer']['home'] == str(runtime.AUTH_HOME),
            'CANARY_REACHABLE_SYNTHETIC_MOUNT')
    require(isinstance(probe, (str, Path)) and Path(probe).is_absolute()
            and '..' not in Path(probe).parts and str(Path(probe)) == str(probe)
            and str(probe) != '/'
            and execution['auth_census']['home'].get('canary') in (None, {'kind': 'directory'}),
            'CANARY_REACHABLE_SYNTHETIC_MOUNT')
    directory = runtime.SESSION_ROOT/session_id
    target = directory/'attempts/001'
    native = access.sandbox_command(directory/'view', directory/'state',
        target/'runtime', session_id,
        read_only_mounts=[(r['host'], r['destination']) for r in execution['read_only_mounts']],
        auth_home=execution['reviewer']['home'], auth_census=execution['auth_census'])
    boundary = native.index('/runtime/claude')
    prefix = [runtime.RUNUSER, '-u', 'research-reviewer', '--', *native[:boundary],
        '--bind', str(target/'journal'), '/state/inspection-journal/1',
        '--ro-bind', str(probe), '/state/canary', '/runtime/claude']
    require(command[:command.index('/runtime/claude')+1] == prefix,
            'CANARY_REACHABLE_SYNTHETIC_MOUNT')


def _phase(name, raw, pins, expected, normal, manifest, literal):
    require('read_boundary_version' not in expected or expected['read_boundary_version'] in READ_BOUNDARY_VERSIONS,
            'CANARY_READ_BOUNDARY_VERSION')
    require('model_policy_version' not in expected or expected['model_policy_version'] in (model_policy.VERSION, model_policy.DIRECT_VERSION),
            'CANARY_MODEL_POLICY_VERSION')
    require(isinstance(raw, dict) and set(raw) == set(RAW_NAMES) | {'journal'}, 'CANARY_ORIGINALS')
    require(all(isinstance(raw[k], bytes) and 0 < len(raw[k]) <= 16000000 for k in RAW_NAMES), 'CANARY_ORIGINAL_BYTES')
    hashes = {k: digest(raw[k]) for k in RAW_NAMES}
    require(isinstance(raw['journal'], list) and len(raw['journal']) <= 8, 'CANARY_JOURNAL_BOUND')
    values = {k: parsed(raw[k]) for k in RAW_NAMES if k.endswith('.json')}
    for k in ('request', 'command'):
        require(hashes[k+'.json'] == pins[k+'_sha256'], 'CANARY_PREPARED_PIN')
    request = values['request.json']
    require(request.get('schema') == 'inspection-canary-request/v1' and request.get('source') == expected['source']
            and request.get('phase') == name and request.get('session_id') == pins['session_id'], 'CANARY_REQUEST')
    command = values['command.json']
    require(isinstance(command, list) and all(isinstance(s, str) for s in command), 'CANARY_COMMAND')
    for flag, value in (('--model', model_policy.requested_model(expected.get('model_policy_version'))), ('--permission-mode', 'dontAsk'), ('--tools', 'Read,Glob,Grep'),
                        ('--settings', '/runtime/inspection-settings.json'), ('--setting-sources', ''),
                        ('--mcp-config', '{"mcpServers":{}}'), ('--max-turns', '8'), ('--session-id', pins['session_id'])):
        require(command.count(flag) == 1 and command.index(flag)+1 < len(command)
                and command[command.index(flag)+1] == value, 'CANARY_COMMAND_PROFILE')
    validate_canary_mounts(command, expected['execution'], pins['session_id'],
                           expected['probe_directory'])
    require('--resume' not in command and all(k in command for k in
            ('--strict-mcp-config', '--include-hook-events', '--disable-slash-commands', '--no-chrome')), 'CANARY_COMMAND_PROFILE')
    require(values['settings.json'] == phase_settings(normal, name), 'CANARY_SETTINGS_DELTA')
    execution = copy.deepcopy(expected['execution'])
    execution['settings_sha256'] = hashes['settings.json']
    require(values['execution.json'] == execution, 'CANARY_RUNTIME_DELTA')
    protection = runtime.verify_confinement_readback(
        raw['confinement-readback.json'], execution, source=expected['source'],
        session_id=pins['session_id'], attempt=1)
    binding = pins['admission_binding']
    review._keys(binding, 'source branch kind turn_id policy_sha256', 'CANARY_ADMISSION_BINDING')
    access.pin(binding['source'], 40); access.pin(binding['turn_id']); access.pin(binding['policy_sha256'])
    require(binding['branch'] == 'astra/infrastructure-milestone-record' and binding['kind'] == 'nightly_review', 'CANARY_ACCOUNTING_CATEGORY')
    event = {k: binding[k] for k in ('source', 'branch', 'kind', 'turn_id')}
    require(values['admission_event.json'] == {**event, 'attempt': '1'}, 'CANARY_ADMISSION_EVENT')
    policy, admitted = values['admission_policy.json'], values['admission_receipt.json']
    require(hashes['admission_policy.json'] == binding['policy_sha256'] and policy.get('status') == 'RATIFIED'
            and policy.get('operator_approval') and policy.get('state_write_permission') == 'OPERATOR_AUTHORIZED'
            and policy.get('server_semantics') == 'OPERATOR_AUTHORIZED_V1', 'CANARY_ADMISSION_POLICY')
    require(admitted.get('status') == 'ADMITTED' and admitted.get('duplicate_admission') is False
            and all(admitted.get(k) == binding[k] for k in ('source', 'branch', 'kind'))
            and type(admitted.get('count')) is int and admitted['count'] > 0
            and isinstance(admitted.get('day'), str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', admitted['day']), 'CANARY_NORMAL_ADMISSION')
    require(values['intent.json'] == {'schema': 'inspection-canary-intent/v1', 'source': expected['source'],
            'phase': name, 'session_id': pins['session_id'], 'maximum_invocations': 1, 'automatic_retry': False,
            **{k+'_sha256': hashes[k+'.json'] for k in ('request', 'command', 'settings', 'execution',
                                                       'admission_event', 'admission_receipt', 'admission_policy', 'confinement-readback')}}, 'CANARY_INTENT')
    process, returned = values['process.json'], values['returned.json']
    require(type(process.get('pid')) is int and process['pid'] > 0 and isinstance(process.get('proc_stat'), str)
            and process['proc_stat'].startswith(str(process['pid'])+' '), 'CANARY_PROCESS')
    require(type(returned.get('returncode')) is int and returned['returncode'] == 0
            and type(returned.get('wall_seconds')) in (int, float) and returned['wall_seconds'] >= 0, 'CANARY_RETURN')
    boundary_version = expected.get('read_boundary_version', READ_BOUNDARY_VERSION)
    read_boundary = name == 'hooks' and 'read_boundary_version' in expected
    wanted = canary_calls(expected['nonce'], name, read_boundary=read_boundary,
                          read_boundary_version=boundary_version)
    events, terminal, uses, results, outputs, models = _protocol(raw['protocol.jsonl'], pins['session_id'],
        policy_version=expected.get('model_policy_version'),
        runtime_cli_sha256=execution['files']['claude']['sha256'], journal=raw['journal'],
        expected_tools=len(wanted))
    attribution = model_policy.analyze(events, session_id=pins['session_id'],
        runtime_cli_sha256=execution['files']['claude']['sha256'], journal=raw['journal'],
        policy_version=expected['model_policy_version']) if expected.get('model_policy_version') else None
    require(sorted(encoded([u.get('name'), u.get('input')]) for u in uses.values()) ==
            sorted(encoded(list(w)) for w in wanted), 'CANARY_EXACT_SYNTHETIC_CALLS')
    if attribution:
        require([(u['name'], u['input']) for u in uses.values()] == wanted,
                'CANARY_EXACT_SYNTHETIC_ORDER')
    inside = next(k for k, u in uses.items() if u['input'] == wanted[-1][1])
    outside = {k for k, u in uses.items() if (u['name'], u['input']) in wanted[:3]}
    failed = next((k for k, u in uses.items() if (u['name'], u['input']) == wanted[3]), None) if read_boundary else None
    require(not results[inside].get('is_error', False) and
            all(results[k].get('is_error') is True for k in outside)
            and (not read_boundary or results[failed].get('is_error') is True), 'CANARY_TOOL_OUTCOMES')
    require(raw['CANARY.txt.after'] == literal and raw['probe.txt.before'] == expected['probe_original'].encode(), 'CANARY_POST_READ_HASH')
    norm = access.normalize_request(manifest, 'Read', wanted[-1][1])
    read_literal = read_boundary_literal(boundary_version) if read_boundary else literal
    boundary_proof = None
    if name == 'baseline':
        require(not raw['journal'], 'CANARY_BASELINE_HOOKS_DISABLED')
        require(baseline_denials_match(terminal, uses, results, outputs, outside,
                                      execution['files']['claude']['sha256']),
                'CANARY_NATIVE_DENIAL_ORIGINALS')
        actual = access.verify_read_response(manifest, norm, outputs[inside], literal)
    else:
        context = {'source': expected['source'], 'session_id': pins['session_id'],
                   'access_manifest_original': expected['access_manifest_original'],
                   'access_manifest_sha256': digest(expected['access_manifest_original'].encode())}
        failures = []
        reads, denials = review._journal(context, 1, events, raw['journal'],
            runtime_cli_sha256=execution['files']['claude']['sha256'] if attribution or read_boundary else None,
            attribution=attribution, observed_failures=failures)
        hook_denials = [d for d in denials if d['kind'] not in
                        ('NATIVE_UNEXECUTED_RETRACTED_GLOB', 'NATIVE_UNEXECUTED_RETRACTED_GREP')]
        wanted_reads = {READ_BOUNDARY_NAME: [[1, 3]]} if read_boundary else {'CANARY.txt': [[1, manifest['files']['CANARY.txt']['line_count']]]}
        require(reads == wanted_reads
                and {d['tool_use_id'] for d in hook_denials} == outside
                and all(d['kind'] == 'HOOK_DENIED' for d in hook_denials), 'CANARY_ACTUAL_HOOK_DENIALS')
        rows = [(parsed(parsed(r)['observation_original'].encode()), parsed(parsed(r)['hook_input_original'].encode())) for r in raw['journal']]
        require(len(rows) == (7 if read_boundary else 5) and all(row.get('normalized_request') is None and row.get('reason') ==
                'INSPECTION_TOOL_OUTSIDE_VIEW' for row, _ in rows if row['tool_use_id'] in outside), 'CANARY_FIXED_OUTSIDE_HOOK_REASON')
        post, hook = next((r, h) for r, h in rows if r['tool_use_id'] == inside and r['phase'] == 'PostToolUse')
        actual = access.verify_read_response(manifest, norm, hook['tool_response'], read_literal)
        require(post['actual_read'] == actual, 'CANARY_ACTUAL_READ_ORIGINAL')
        if read_boundary:
            require(len(failures) == 1 and failures[0]['tool_use_id'] == failed
                    and failures[0]['kind'] == ('READ_TOKEN_EXECUTION_ERROR'
                        if boundary_version == TOKEN_READ_BOUNDARY_VERSION else 'READ_SIZE_EXECUTION_ERROR')
                    and failures[0]['path'] == READ_BOUNDARY_NAME and failures[0]['coverage'] == [],
                    'CANARY_ACTUAL_SIZE_FAILURE')
            order = list(uses)
            require(order.index(failed) < order.index(inside), 'CANARY_FAILURE_BEFORE_BOUNDED_READ')
            failure_result_event = next(i for i, e in enumerate(events) if e.get('type') == 'user'
                and any(x.get('type') == 'tool_result' and x.get('tool_use_id') == failed
                        for x in e.get('message', {}).get('content', []) if isinstance(x, dict)))
            bounded_use_event = next(i for i, e in enumerate(events) if e.get('type') == 'assistant'
                and any(x.get('type') == 'tool_use' and x.get('id') == inside
                        for x in e.get('message', {}).get('content', []) if isinstance(x, dict)))
            require(failure_result_event < bounded_use_event, 'CANARY_FAILURE_RESULT_BEFORE_BOUNDED_READ')
            require(actual['crlf_line_numbers'] == [1, 3]
                    and actual['fragment_sha256'] != actual['displayed_fragment_sha256']
                    and access.verify_read_fragment(actual, hook['tool_response']['file']['content'])
                        == b''.join(read_literal.splitlines(keepends=True)[:3]),
                    'CANARY_ACTUAL_CRLF_DISPLAY')
            boundary_proof = {'version': boundary_version, 'failed_read': failures[0],
                              'bounded_crlf_read': actual, 'bounded_tool_use_id': inside,
                              'whole_file_read_claim': False}
        else:
            require(not failures, 'CANARY_UNEXPECTED_TOOL_FAILURE')
    require(actual['start_line'] == 1 and actual['end_line'] == (3 if read_boundary else manifest['files']['CANARY.txt']['line_count'])
            and not actual['truncated_by_token_cap'] and not actual['empty'], 'CANARY_COMPLETE_LITERAL_READ')
    answer = {'original_sha256': hashes, 'journal_sha256': [digest(r) for r in raw['journal']],
            'session_id': pins['session_id'], 'assistant_models': models, 'model_usage': terminal['modelUsage'],
            'tool_use_ids': sorted(uses), 'outside_tool_use_ids': sorted(outside), 'actual_read': actual,
            'admission_event': values['admission_event.json'], 'admission_receipt': admitted,
            'confinement': protection}
    if boundary_proof is not None:
        answer['read_boundary'] = boundary_proof
    if attribution:
        answer.update(model_policy_version=expected['model_policy_version'], model_policy=attribution,
                      requested_model=model_policy.requested_model(expected['model_policy_version']),
                      provider_model=attribution['provider_model'])
    return answer


def verify_canary(original_bundle, expected_pins):
    """Require prepared pins plus both conclusive native attempts; raise on uncertainty."""
    require(isinstance(original_bundle, dict) and set(original_bundle) == set(PHASES), 'CANARY_TWO_PHASES')
    expected = expected_pins
    model_policy.version(expected.get('model_policy_version'))
    require('model_policy_version' not in expected or expected['model_policy_version'] in (model_policy.VERSION, model_policy.DIRECT_VERSION),
            'CANARY_MODEL_POLICY_VERSION')
    review._keys(expected, 'schema source execution runtime_sha256 settings_original settings_sha256 hooks_sha256 '
                 'access_manifest_original canary_original probe_original probe_directory nonce phases'
                 + (' model_policy_version' if 'model_policy_version' in expected else '')
                 + (' read_boundary_version' if 'read_boundary_version' in expected else ''), 'CANARY_PIN_SCHEMA')
    require(expected['schema'] == 'inspection-canary-plan/v1', 'CANARY_PLAN_VERSION')
    require('read_boundary_version' not in expected or expected['read_boundary_version'] in READ_BOUNDARY_VERSIONS,
            'CANARY_READ_BOUNDARY_VERSION')
    access.pin(expected['source'], 40)
    for name in ('settings_original', 'access_manifest_original', 'canary_original', 'probe_original', 'nonce'):
        require(isinstance(expected[name], str) and 0 < len(expected[name].encode()) <= 100000, 'CANARY_SYNTHETIC_TEXT_BOUND')
    require(re.fullmatch('[A-Za-z0-9_-]{16,128}', expected['nonce']) and expected['probe_original'] == expected['nonce']+'\n', 'CANARY_NONCE')
    require(isinstance(expected['probe_directory'], str) and expected['probe_directory'].startswith('/')
            and '..' not in expected['probe_directory'].split('/') and expected['probe_directory'] != '/', 'CANARY_PROBE_DIRECTORY')
    normal = parsed(expected['settings_original'].encode())
    require(normal == access.access_settings() and digest(expected['settings_original'].encode()) == expected['settings_sha256'], 'CANARY_NORMAL_SETTINGS_PIN')
    execution = expected['execution']
    require(digest(encoded(execution)) == expected['runtime_sha256'] and execution.get('schema') == 'inspection-runtime-spec/v1'
            and execution.get('settings_sha256') == expected['settings_sha256']
            and execution['files']['hooks']['sha256'] == expected['hooks_sha256'], 'CANARY_NORMAL_RUNTIME_PIN')
    manifest = access.validate_access_manifest(expected['access_manifest_original'].encode())
    expected_policy = (access.READ_TOKEN_FAILURE_POLICY
        if expected.get('read_boundary_version') == TOKEN_READ_BOUNDARY_VERSION else None)
    require(manifest.get('read_failure_policy') == expected_policy, 'CANARY_READ_FAILURE_POLICY_CHANGED')
    literal = expected['canary_original'].encode()
    expected_files = {'CANARY.txt': {
        'sha256': digest(literal), 'bytes': len(literal), 'line_count': len(literal.decode().splitlines())}}
    if 'read_boundary_version' in expected:
        boundary_literal = read_boundary_literal(expected['read_boundary_version'])
        expected_files[READ_BOUNDARY_NAME] = {'sha256': digest(boundary_literal), 'bytes': len(boundary_literal),
                                            'line_count': len(boundary_literal.decode().splitlines())}
    require(manifest['source'] == expected['source'] and manifest['files'] == expected_files, 'CANARY_SYNTHETIC_VIEW_ONLY')
    require(isinstance(expected['phases'], dict) and set(expected['phases']) == set(PHASES), 'CANARY_PHASE_PINS')
    for pins in expected['phases'].values():
        review._keys(pins, 'session_id request_sha256 command_sha256 admission_binding', 'CANARY_PHASE_BINDING')
        require(isinstance(pins['session_id'], str) and re.fullmatch('[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}', pins['session_id']), 'CANARY_SESSION_ID')
        for key in ('request_sha256', 'command_sha256'): access.pin(pins[key])
    require(expected['phases']['baseline']['session_id'] != expected['phases']['hooks']['session_id']
            and expected['phases']['baseline']['admission_binding']['turn_id'] != expected['phases']['hooks']['admission_binding']['turn_id'], 'CANARY_INDEPENDENT_ATTEMPTS')
    phases = {p: _phase(p, original_bundle[p], expected['phases'][p], expected, normal, manifest, literal) for p in PHASES}
    answer = {'schema': 'inspection-permission-probe/v1', 'status': 'PASSED', 'source': expected['source'],
            'baseline_permissions_verified': True, 'hooks_verified': True, 'native_denial_before_hooks_verified': True,
            **{k: expected[k] for k in ('runtime_sha256', 'settings_sha256', 'hooks_sha256')},
            'runtime_cli_sha256': execution['files']['claude']['sha256'],
            'plan_sha256': digest(encoded(expected)), 'phases': phases, 'approval_authority': False,
            'scope': 'Two original synthetic native boundary checks; no scientific or candidate evidence inspected.'}
    if 'read_boundary_version' in expected:
        require(phases['hooks']['read_boundary']['version'] == expected['read_boundary_version'],
                'CANARY_READ_BOUNDARY_PROOF')
        answer.update(read_boundary_version=expected['read_boundary_version'], oversized_read_failure_verified=True,
                      bounded_read_after_failure_verified=True, crlf_display_verified=True)
        if expected_policy:
            answer['token_limit_failure_verified'] = True
    if expected.get('model_policy_version') is not None:
        answer['model_policy_version'] = expected['model_policy_version']
    return answer
