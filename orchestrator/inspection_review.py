"""Pure validation of source-bound, read-only formal inspection originals.

This module launches nothing. The runner must supply protected host originals;
hash consistency alone does not authenticate a host journal or authorize a call.
"""
import hashlib
import json
import re
from pathlib import PurePosixPath
from orchestrator import inspection_model_policy as model_policy

MANIFEST = 'formal-inspection-manifest/v1'
REQUEST = 'formal-inspection-request/v1'
INTENT = 'formal-inspection-intent/v1'
RESULT = 'formal-inspection-result/v1'
RECEIPT = 'formal-inspection-attempt/v1'
MODEL = 'claude-fable-5'
# The observed helper usage is not an additional reviewing assistant model.
# Unknown usage identities remain unqualified, as do all fallback events.
AUXILIARY_USAGE = 'claude-haiku-4-5-20251001'
TOOLS = frozenset(('Read', 'Glob', 'Grep', 'StructuredOutput'))
MAX_ORIGINAL_BYTES = 16_000_000
# Includes the fixed browsing view and all original per-Read journals.
MAX_EXPORT_FILES = 7000
MAX_ATTEMPTS = 32
# Prospective native material budgets; historical receipt ceiling stays unchanged.
NATIVE_MAX_ATTEMPTS = 16
MATERIAL_MAX_TOOL_TURNS = 32
MAX_TOOLS = 512
READ_VALIDATION_DENIAL_CLI_SHA256 = '10caae8f22b915c26bfff0e013a4d45608c4f1ae287583626569156f447730e5'


def usage_identity_matches(usage):
    """Known auxiliary accounting is not an additional reviewing assistant.

    Preserve the original dated key and its observed undated canonical label.
    No unknown key/alias or fallback is qualified by this pure usage check.
    """
    if not isinstance(usage, dict) or MODEL not in usage or not set(usage) <= {MODEL, AUXILIARY_USAGE}:
        return False
    for name, row in usage.items():
        allowed = (MODEL,) if name == MODEL else (AUXILIARY_USAGE, 'claude-haiku-4-5')
        if not isinstance(row, dict) or row.get('canonicalModel', name) not in allowed:
            return False
    return True



def native_read_input_validation_denied(use, result, tool_output, *, runtime_cli_sha256=None):
    """Recognize one pinned CLI's early Read denial; never establish read coverage.

    The caller authenticates the runtime and correlates these original protocol
    fields. Unknown CLI binaries and all other tool errors remain unqualified.
    """
    from orchestrator.inspection_access import DENIED_ROOTS
    if (runtime_cli_sha256 != READ_VALIDATION_DENIAL_CLI_SHA256 or
            not isinstance(use, dict) or not isinstance(result, dict) or
            use.get('type') != 'tool_use' or use.get('name') != 'Read' or
            not isinstance(use.get('id'), str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,200}', use['id']) or
            result.get('type') != 'tool_result' or result.get('tool_use_id') != use['id'] or
            result.get('is_error') is not True):
        return False
    value = use.get('input')
    if not isinstance(value, dict) or set(value) != {'file_path'}:
        return False
    path = value['file_path']
    if (not isinstance(path, str) or not 1 <= len(path) <= 4096 or
            any(ord(c) < 32 or ord(c) == 127 or c == '\\' for c in path)):
        return False
    parts = PurePosixPath(path).parts
    if (str(PurePosixPath(path)) != path or len(parts) < 2 or parts[0] != '/' or
            parts[1] not in DENIED_ROOTS or '..' in parts):
        return False
    message = 'File is in a directory that is denied by your permission settings.'
    return (result.get('content') == '<tool_use_error>' + message + '</tool_use_error>' and
            tool_output == 'Error: ' + message)


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode('utf-8')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _require(ok, reason):
    if not ok:
        raise ValueError(reason)


def _pairs(items):
    result = {}
    for key, value in items:
        _require(key not in result, 'DUPLICATE_JSON_KEY')
        result[key] = value
    return result


def _json(raw):
    _require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_ORIGINAL_BYTES,
             'BOUNDED_ORIGINAL_BYTES_REQUIRED')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('NONFINITE_JSON')))


def _keys(value, keys, reason):
    _require(isinstance(value, dict) and set(value) == set(keys.split()), reason)


def _pin(value, length=64):
    _require(isinstance(value, str) and re.fullmatch('[0-9a-f]{' + str(length) + '}', value), 'INVALID_PIN')


def _text(value):
    _require(isinstance(value, str) and value.strip() and len(value.encode()) <= 80_000, 'BOUNDED_TEXT_REQUIRED')


def _strings(value):
    _require(isinstance(value, list) and len(value) <= 512, 'BOUNDED_STRING_LIST_REQUIRED')
    for item in value:
        _text(item)
    _require(len(value) == len(set(value)), 'DUPLICATE_LIST_ITEM')


def validate_manifest(raw):
    """Validate the fixed permission/coverage contract, not live file access."""
    value = _json(raw)
    model_policy.version(value.get('model_policy_version'))
    _require('model_policy_version' not in value or value['model_policy_version'] in (model_policy.VERSION, model_policy.DIRECT_VERSION),
             'MANIFEST_MODEL_POLICY_VERSION')
    _keys(value, 'schema source scope session_id proposal_sha256 current_request_sha256 '
          'context_sha256 actor access_manifest_original access_manifest_sha256 pins required_ranges '
          'max_attempts admission_binding permission_probe_sha256 changes_sha256 change_bindings_sha256'
          + (' model_policy_version' if 'model_policy_version' in value else ''), 'MANIFEST_SCHEMA')
    _require(value['schema'] == MANIFEST, 'MANIFEST_VERSION')
    _pin(value['source'], 40)
    _require(isinstance(value['session_id'], str) and re.fullmatch(
        '[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}', value['session_id']), 'SESSION_ID')
    _text(value['scope'])
    _require(type(value['max_attempts']) is int and 1 <= value['max_attempts'] <= MAX_ATTEMPTS, 'MAXIMUM_ATTEMPTS')
    admission = value['admission_binding']
    _keys(admission, 'source branch kind turn_id policy_sha256', 'ADMISSION_BINDING_SCHEMA')
    _pin(admission['source'], 40); _pin(admission['turn_id']); _pin(admission['policy_sha256'])
    _require(admission['branch'] == 'astra/infrastructure-milestone-record' and admission['kind'] == 'nightly_review', 'ADMISSION_EVENT_SCOPE')
    for key in ('proposal_sha256', 'current_request_sha256', 'context_sha256', 'access_manifest_sha256'):
        _pin(value[key])
    _pin(value['permission_probe_sha256'])
    _pin(value['changes_sha256']); _pin(value['change_bindings_sha256'])
    _keys(value['actor'], 'kind identity', 'ACTOR_SCHEMA')
    _require(value['actor']['kind'] in ('human', 'agent'), 'ACTOR_KIND')
    _text(value['actor']['identity'])
    _keys(value['pins'], 'settings_sha256 hooks_sha256 runtime_sha256 runner_sha256', 'RUNTIME_PINS')
    for pin in value['pins'].values():
        _pin(pin)
    _require(isinstance(value['access_manifest_original'], str), 'ACCESS_ORIGINAL_UTF8')
    access_raw = value['access_manifest_original'].encode('utf-8')
    from orchestrator.inspection_access import validate_access_manifest
    access = validate_access_manifest(access_raw)
    _require(access['source'] == value['source'], 'ACCESS_BINDING')
    _require(digest(access_raw) == value['access_manifest_sha256'], 'ACCESS_MANIFEST_DIGEST')
    required = value['required_ranges']
    _require(isinstance(required, dict) and required and set(required) <= set(access['files']), 'REQUIRED_COVERAGE')
    for name, ranges in required.items():
        previous = 0
        _require(isinstance(ranges, list) and len(ranges) <= 2000, 'REQUIRED_RANGES')
        for pair in ranges:
            _require(isinstance(pair, list) and len(pair) == 2 and all(type(n) is int for n in pair)
                     and previous < pair[0] <= pair[1] <= access['files'][name]['line_count'], 'REQUIRED_RANGE_BOUND')
            previous = pair[1]
        _require(bool(ranges) or access['files'][name]['line_count'] == 0, 'EMPTY_REQUIRED_RANGE')
    return value


def _coverage(required, reads):
    missing = {}
    for name, wanted in required.items():
        if not wanted and name not in reads:
            missing[name] = []  # Even an empty required file must have an actual Read.
        available = sorted(reads.get(name, []))
        for first, last in wanted:
            cursor = first
            for start, end in available:
                if end < cursor:
                    continue
                if start > cursor:
                    missing.setdefault(name, []).append([cursor, min(start - 1, last)])
                cursor = max(cursor, end + 1)
                if cursor > last:
                    break
            if cursor <= last:
                missing.setdefault(name, []).append([cursor, last])
    return missing


def _journal(manifest, number, events, raw_records, *, runtime_cli_sha256=None, attribution=None,
             observed_failures=None):
    """Correlate trusted hook originals with actual tool-use IDs, not claims."""
    _require(observed_failures is None or isinstance(observed_failures, list) and not observed_failures,
             'JOURNAL_FAILURE_COLLECTOR')
    excluded = {}
    if attribution is not None:
        _require(attribution.get('policy_version') in (model_policy.VERSION, model_policy.DIRECT_VERSION),
                 'JOURNAL_MODEL_POLICY')
        _require(attribution['policy_version'] != model_policy.DIRECT_VERSION
                 or attribution['unexecuted_retracted'] == [], 'JOURNAL_DIRECT_RETRACTION')
        if attribution.get('unexecuted_retracted'):
            checked = model_policy.analyze(events, session_id=manifest['session_id'],
                runtime_cli_sha256=runtime_cli_sha256, journal=raw_records)
            _require(checked['unexecuted_retracted'] == attribution['unexecuted_retracted'],
                     'JOURNAL_UNEXECUTED_CLASSIFICATION_CHANGED')
            excluded = {row['tool_use_id']: row for row in checked['unexecuted_retracted']}
    uses, results, result_events, all_tool_ids = {}, {}, {}, set()
    access = _json(manifest['access_manifest_original'].encode())
    from orchestrator.inspection_access import normalize_request
    for event in events:
        message = event.get('message', {})
        for item in message.get('content', []) if isinstance(message.get('content'), list) else []:
            if item.get('type') == 'tool_use' and event.get('type') == 'assistant':
                _require(item.get('name') in TOOLS and isinstance(item.get('id'), str)
                         and item['id'] not in all_tool_ids, 'UNEXPECTED_OR_DUPLICATE_TOOL')
                all_tool_ids.add(item['id'])
                if item['name'] != 'StructuredOutput':
                    uses[item['id']] = item
            elif item.get('type') == 'tool_result' and event.get('type') == 'user':
                key = item.get('tool_use_id')
                _require(key in all_tool_ids and key not in results, 'ORPHAN_OR_DUPLICATE_TOOL_RESULT')
                results[key] = item
                result_events[key] = event
    _require(len(uses) <= MAX_TOOLS and isinstance(raw_records, list) and len(raw_records) <= 2 * len(uses), 'JOURNAL_COUNT')
    records, observations, reads, denials = {}, {}, {}, []
    for raw in raw_records:
        original = _json(raw)
        _keys(original, 'observation_original hook_input_original', 'HOOK_ORIGINAL_SCHEMA')
        _require(isinstance(original['hook_input_original'], str), 'HOOK_ORIGINAL_UTF8')
        hook_raw = original['hook_input_original'].encode()
        _require(isinstance(original['observation_original'], str), 'OBSERVATION_ORIGINAL_UTF8')
        observation_raw = original['observation_original'].encode()
        row, hook = _json(observation_raw), _json(hook_raw)
        _require(isinstance(row, dict) and isinstance(hook, dict), 'HOOK_ORIGINAL_REQUIRED')
        key, phase = row.get('tool_use_id'), row.get('phase')
        _require(key in uses and phase in ('PreToolUse', 'PostToolUse', 'PostToolUseFailure') and (key, phase) not in records, 'ORPHAN_OR_DUPLICATE_HOOK')
        use = uses[key]
        _require(row.get('schema') == 'inspection-tool-observation/v1' and row.get('source') == manifest['source']
                 and row.get('access_manifest_sha256') == manifest['access_manifest_sha256']
                 and row.get('session_id') == manifest['session_id'] and row.get('attempt_id') == str(number)
                 and row.get('tool_name') == use['name'] and hook.get('tool_use_id') == key
                 and hook.get('tool_name') == use['name'] and hook.get('tool_input') == use.get('input')
                 and hook.get('session_id') == manifest['session_id'] and hook.get('hook_event_name') == phase
                 and hook.get('cwd') == '/review' and hook.get('permission_mode') == 'dontAsk', 'HOOK_IDENTITY')
        _require(row.get('request_sha256') == digest(encoded(use.get('input'))), 'TOOL_INPUT_DIGEST')
        _require(row.get('raw_input_sha256') == digest(hook_raw), 'HOOK_INPUT_DIGEST')
        _require(row.get('status') in (('ALLOWED', 'DENIED') if phase == 'PreToolUse' else
                 ('OBSERVED',) if phase == 'PostToolUse' else ('OBSERVED_FAILURE',)), 'UNQUALIFIED_TOOL')
        if row['status'] != 'DENIED':
            _require(row.get('normalized_request') == normalize_request(access, use['name'], use.get('input')), 'NORMALIZED_TOOL_REQUEST')
        if phase == 'PostToolUseFailure':
            from orchestrator.inspection_access import verify_read_failure, READ_SIZE_ERROR_CLI_SHA256
            _require(observed_failures is not None and runtime_cli_sha256 == READ_SIZE_ERROR_CLI_SHA256,
                     'NATIVE_READ_SIZE_RUNTIME_OR_COLLECTOR')
            _require((key, 'PreToolUse') in records and (key, 'PostToolUse') not in records
                     and observations[key, 'PreToolUse']['status'] == 'ALLOWED'
                     and row.get('pre_observation_sha256') == records[key, 'PreToolUse'],
                     'NATIVE_READ_SIZE_PRE_BINDING')
            failure = verify_read_failure(access, use.get('input'), hook)
            _require(row.get('native_failure') == failure and row.get('actual_read') is None
                     and row.get('observed_files') == {} and row.get('tool_response_sha256') is None,
                     'NATIVE_READ_SIZE_FAILURE_BINDING')
            result, event = results.get(key), result_events.get(key, {})
            _require(isinstance(result, dict) and result.get('is_error') is True
                     and result.get('content') == hook['error']
                     and event.get('tool_use_result') == 'Error: '+hook['error']
                     and event.get('message', {}).get('content') == [result],
                     'NATIVE_READ_SIZE_RESULT_BINDING')
        if phase == 'PostToolUse':
            _require((key, 'PostToolUseFailure') not in records, 'POST_AND_FAILURE_CONFLICT')
            _require((key, 'PreToolUse') in records and row.get('pre_observation_sha256') == records[key, 'PreToolUse'], 'PRE_HOOK_REQUIRED_BEFORE_POST')
            _require(observations[key, 'PreToolUse']['status'] == 'ALLOWED', 'POST_AFTER_DENIED_PRE')
            _require(key in results and not results[key].get('is_error', False), 'TOOL_RESULT_NOT_SUCCESSFUL')
            output = hook.get('tool_response')
            _require(row.get('tool_response_sha256') == digest(encoded(output)), 'TOOL_OUTPUT_DIGEST')
            if use['name'] == 'Read':
                _require(isinstance(output, dict) and output.get('type') == 'text', 'UNQUALIFIED_READ_TYPE')
                file = output.get('file', {})
                actual = row.get('actual_read', {})
                name = actual.get('path')
                _require(name in access['files'] and
                         file.get('filePath') == '/review/' + name and isinstance(file.get('content'), str), 'READ_FILE_BINDING')
                first, count = file.get('startLine'), file.get('numLines')
                total = access['files'][name]['line_count']
                normalized = row['normalized_request']
                _require(name == normalized['path'], 'READ_REQUEST_FILE_CHANGED')
                _require(type(first) is int and type(count) is int and count >= 0
                         and file.get('totalLines') in (total, total + 1) and first == normalized['start_line']
                         and 1 <= first <= total + 1 and first + count - 1 <= file['totalLines']
                         and (normalized['limit'] is None or count <= normalized['limit']), 'ACTUAL_READ_RANGE')
                end = min(first + count - 1, total)
                _require(actual.get('start_line') == first and actual.get('end_line') == end
                         and actual.get('returned_line_count') == count and actual.get('total_lines') == total
                         and actual.get('truncated_by_token_cap') is file.get('truncatedByTokenCap', False)
                         and actual.get('returned_content_sha256') == digest(file['content'].encode()), 'READ_COVERAGE_DIGEST')
                from orchestrator.inspection_access import verify_read_fragment
                # Validate the exact native display relation while retaining the
                # original fragment hash for full-source identity below.
                verify_read_fragment(actual, file['content'])
                files = row.get('observed_files')
                _require(files == {name: access['files'][name]}, 'READ_SOURCE_DIGEST')
                if first == 1 and end == total:
                    _require(actual['fragment_sha256'] == access['files'][name]['sha256'], 'FULL_READ_SOURCE_DIGEST')
                reads.setdefault(name, [])
                if first <= end:
                    reads[name].append([first, end])
            else:
                _require(row.get('actual_read') is None, 'DISCOVERY_IS_NOT_FULL_READ')
        records[key, phase] = digest(observation_raw)
        observations[key, phase] = row
    terminal = next(event for event in events if event.get('type') == 'result')
    native = terminal.get('permission_denials', [])
    _require(isinstance(native, list) and len(native) <= MAX_TOOLS, 'NATIVE_DENIAL_LIST')
    native_by_id = {}
    for entry in native:
        _keys(entry, 'tool_name tool_use_id tool_input', 'NATIVE_DENIAL_SCHEMA')
        key = entry['tool_use_id']
        _require(key in uses and key not in native_by_id and entry['tool_name'] == uses[key]['name']
                 and entry['tool_input'] == uses[key]['input'], 'NATIVE_DENIAL_BINDING')
        native_by_id[key] = entry
    for key, use in uses.items():
        pre, post = observations.get((key, 'PreToolUse')), observations.get((key, 'PostToolUse'))
        failure = observations.get((key, 'PostToolUseFailure'))
        if failure is not None:
            _require(key not in excluded and post is None and key not in native_by_id,
                     'NATIVE_READ_SIZE_TERMINAL_CONFLICT')
            observed_failures.append({**failure['native_failure'], 'tool_use_id': key, 'tool_name': 'Read',
                'pre_observation_sha256': failure['pre_observation_sha256'],
                'failure_observation_sha256': records[key, 'PostToolUseFailure'],
                'failure_hook_input_sha256': failure['raw_input_sha256'],
                'tool_result_sha256': digest(encoded(results[key])),
                'tool_result_event_sha256': digest(encoded(result_events[key])),
                'runtime_cli_sha256': runtime_cli_sha256})
            continue
        if key in excluded:
            _require(pre is None and post is None and key not in native_by_id,
                     'NATIVE_RETRACTED_GLOB_HOOK_CONFLICT')
            denials.append(excluded[key])
            continue
        original_event = result_events.get(key, {})
        original_result = results.get(key)
        early_read_denial = (original_event.get('message', {}).get('content') == [original_result] and
                             native_read_input_validation_denied(
                                 use, original_result, original_event.get('tool_use_result'),
                                 runtime_cli_sha256=runtime_cli_sha256))
        _require(not early_read_denial or (pre is None and post is None), 'NATIVE_READ_VALIDATION_HOOK_CONFLICT')
        if post:
            _require(key not in native_by_id, 'READ_AND_NATIVE_DENIAL_CONFLICT')
            continue
        if early_read_denial and key not in native_by_id:
            denials.append({'tool_use_id': key, 'tool_name': 'Read',
                            'kind': 'NATIVE_READ_INPUT_VALIDATION_DENIED',
                            'tool_result_sha256': digest(encoded(original_result)),
                            'tool_result_event_sha256': digest(encoded(original_event)),
                            'runtime_cli_sha256': runtime_cli_sha256, 'coverage': []})
            continue
        known_denial = (pre is not None and pre['status'] == 'DENIED') or key in native_by_id
        _require(known_denial and key in results and results[key].get('is_error') is True, 'MISSING_ALLOWED_TOOL_HOOK_OR_RESULT')
        denials.append({'tool_use_id': key, 'tool_name': use['name'],
                       'kind': 'HOOK_DENIED' if pre and pre['status'] == 'DENIED' else 'NATIVE_PERMISSION_DENIED',
                       'tool_result_sha256': digest(encoded(results[key])), 'coverage': []})
    return reads, denials


def _parse_attempt(manifest_raw, originals, *, previous=None):
    """Return an original-bound receipt; invalid/uncertain attempts never progress."""
    manifest = validate_manifest(manifest_raw)
    hashes = {key: digest(raw) for key, raw in originals.items() if isinstance(raw, bytes)}
    journal = originals.get('journal', [])
    receipt = {'schema': RECEIPT, 'status': 'RECONCILIATION_REQUIRED', 'source': manifest['source'],
               'manifest_sha256': digest(manifest_raw), 'session_id': manifest['session_id'],
               'original_sha256': hashes, 'journal_sha256': [digest(raw) for raw in journal if isinstance(raw, bytes)],
               'automatic_retry': False, 'independent_execution_claim': False}
    try:
        _require(set(originals) == {'request', 'intent', 'process', 'returned', 'protocol', 'journal', 'timeout',
                                    'admission_event', 'admission_receipt', 'admission_policy', 'permission_probe',
                                    'reconciliation'}, 'ATTEMPT_ORIGINALS_SCHEMA')
        request, intent = _json(originals['request']), _json(originals['intent'])
        _keys(request, 'schema source scope manifest_sha256 session_id attempt previous_receipt_sha256 prompt', 'REQUEST_SCHEMA')
        number = request['attempt']
        _require(type(number) is int and 1 <= number <= manifest['max_attempts'], 'ATTEMPT_NUMBER')
        previous_hash = request['previous_receipt_sha256']
        _require((number == 1 and previous_hash is None) or (number > 1 and isinstance(previous_hash, str)), 'PREVIOUS_RECEIPT')
        if previous_hash is not None:
            _pin(previous_hash)
        policy_version = manifest.get('model_policy_version')
        prospective = policy_version is not None
        requested = model_policy.requested_model(policy_version)
        if prospective:
            _require((number == 1 and previous is None) or
                     (number > 1 and previous is not None and previous['status'] == 'IN_PROGRESS'
                      and previous['attempt'] == number - 1
                      and previous['source'] == manifest['source']
                      and previous['session_id'] == manifest['session_id']
                      and previous['manifest_sha256'] == digest(manifest_raw)
                      and digest(encoded(previous)) == previous_hash), 'MODEL_POLICY_PREDECESSOR_ORIGINALS')

        _require(isinstance(request['prompt'], str) and 0 < len(request['prompt'].encode()) <= 4_000_000, 'REQUEST_PROMPT_BOUND')
        _require(request['schema'] == REQUEST and request['source'] == manifest['source']
                 and request['scope'] == manifest['scope'] and request['manifest_sha256'] == digest(manifest_raw)
                 and request['session_id'] == manifest['session_id'], 'REQUEST_BINDING')
        expected = {'schema': INTENT, 'request_sha256': hashes['request'], 'source': manifest['source'],
                    'manifest_sha256': digest(manifest_raw), 'session_id': manifest['session_id'], 'attempt': number,
                    'previous_receipt_sha256': previous_hash, 'actor': manifest['actor'], 'pins': manifest['pins'],
                    'admission_event_sha256': hashes['admission_event'], 'admission_receipt_sha256': hashes['admission_receipt'],
                    'admission_policy_sha256': hashes['admission_policy'],
                    'maximum_invocations': 1, 'automatic_retry': False}
        _require(intent == expected, 'INTENT_BINDING')
        if originals['timeout'] is not None:
            _json(originals['timeout'])
            reconciliation = _json(originals['reconciliation'])
            _require(reconciliation == {
                'schema': 'formal-inspection-reconciliation/v1', 'status': 'ORIGINAL_PROCESS_ENDED_VERIFIED',
                'source': manifest['source'], 'manifest_sha256': digest(manifest_raw),
                'session_id': manifest['session_id'], 'attempt': number, 'actor': manifest['actor'],
                'provider_invocations': 0,
                **{key + '_sha256': hashes[key] for key in ('request', 'process', 'timeout', 'returned', 'protocol')}
            }, 'ORIGINAL_TIMEOUT_RECONCILIATION_BINDING')
        else:
            _require(originals['reconciliation'] is None, 'RECONCILIATION_WITHOUT_TIMEOUT')
        probe = _json(originals['permission_probe'])
        _require(hashes['permission_probe'] == manifest['permission_probe_sha256']
                 and probe.get('schema') == 'inspection-permission-probe/v1' and probe.get('status') == 'PASSED'
                 and all(probe.get(key) is True for key in ('baseline_permissions_verified', 'hooks_verified', 'native_denial_before_hooks_verified'))
                 and all(probe.get(key) == manifest['pins'][key] for key in ('runtime_sha256', 'settings_sha256', 'hooks_sha256')), 'PERMISSION_PROBE_BINDING')
        _require(probe.get('model_policy_version') == manifest.get('model_policy_version'),
                 'PERMISSION_PROBE_MODEL_POLICY')
        binding = manifest['admission_binding']
        event = _json(originals['admission_event'])
        _require(event == {**{key: binding[key] for key in ('source', 'branch', 'kind', 'turn_id')},
                           'attempt': str(number)}, 'ADMISSION_EVENT_BINDING')
        policy = _json(originals['admission_policy'])
        _require(hashes['admission_policy'] == binding['policy_sha256'] and policy.get('status') == 'RATIFIED'
                 and policy.get('operator_approval') and policy.get('state_write_permission') == 'OPERATOR_AUTHORIZED'
                 and policy.get('server_semantics') == 'OPERATOR_AUTHORIZED_V1', 'ADMISSION_POLICY_BINDING')
        admission = _json(originals['admission_receipt'])
        _require(admission.get('status') == 'ADMITTED' and admission.get('duplicate_admission') is False
                 and all(admission.get(key) == binding[key] for key in ('source', 'branch', 'kind'))
                 and type(admission.get('count')) is int and admission['count'] > 0
                 and isinstance(admission.get('day'), str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', admission['day']), 'ADMISSION_ORIGINAL_NOT_ADMITTED')
        process, returned = _json(originals['process']), _json(originals['returned'])
        _require(type(process.get('pid')) is int and process['pid'] > 0 and isinstance(process.get('proc_stat'), str)
                 and process['proc_stat'].startswith(str(process['pid']) + ' '), 'PROCESS_ORIGINAL')
        _require(type(returned.get('returncode')) is int and returned['returncode'] == 0 and
                 type(returned.get('wall_seconds')) in (int, float) and returned['wall_seconds'] >= 0, 'INCONCLUSIVE_RETURN')
        protocol = originals['protocol']
        _require(isinstance(protocol, bytes) and 0 < len(protocol) <= MAX_ORIGINAL_BYTES, 'PROTOCOL_BOUND')
        events = [_json(line) for line in protocol.splitlines() if line.strip()]
        _require(all(isinstance(event, dict) for event in events), 'PROTOCOL_EVENT')
        init = [event for event in events if event.get('type') == 'system' and event.get('subtype') == 'init']
        terminal = [event for event in events if event.get('type') == 'result']
        _require(len(init) == len(terminal) == 1, 'CONCLUSIVE_ORIGINAL_RESULT_REQUIRED')
        first, last = init[0], terminal[0]
        _require(events[0] is first and events[-1] is last, 'ORIGINAL_PROTOCOL_ORDER')
        _require(set(first.get('tools', [])) == TOOLS and len(first['tools']) == len(TOOLS)
                 and first.get('mcp_servers') == [] and first.get('permissionMode') == 'dontAsk'
                 and first.get('model') == requested, 'FIXED_INSPECTION_TOOL_AND_MODEL_PROFILE')
        _require(all(event.get('session_id', manifest['session_id']) == manifest['session_id'] for event in events)
                 and first.get('session_id') == manifest['session_id'] and last.get('session_id') == manifest['session_id'], 'SESSION_CHANGED')
        models = {event.get('message', {}).get('model') for event in events if event.get('type') == 'assistant'}
        usage = last.get('modelUsage')
        attribution = None
        if prospective:
            _require(originals['timeout'] is None, 'MODEL_POLICY_TIMEOUT_UNQUALIFIED')
            attribution = model_policy.analyze(events, session_id=manifest['session_id'],
                runtime_cli_sha256=probe.get('runtime_cli_sha256'), journal=journal,
                previous=previous['model_policy'] if previous else None, policy_version=policy_version)
        else:
            _require(models == {MODEL} and isinstance(usage, dict) and MODEL in usage
                     and set(usage) <= {MODEL, AUXILIARY_USAGE}, 'MODEL_IDENTITY_CHANGED')
            _require(usage_identity_matches(usage), 'USAGE_IDENTITY_CHANGED')
            _require(not any(event.get('subtype') == 'model_refusal_fallback' for event in events), 'PROVIDER_REFUSAL_PRESERVED')
        _require(last.get('subtype') == 'success' and last.get('is_error') is False, 'PROVIDER_RESULT_NOT_SUCCESSFUL')
        result = last.get('structured_output')
        _keys(result, 'schema scope reviewed_commit manifest_sha256 status findings questions claimed_inspected_files remaining_obligations resolved', 'RESULT_SCHEMA')
        _require(result['schema'] == RESULT and result['scope'] == manifest['scope']
                 and result['reviewed_commit'] == manifest['source'] and result['manifest_sha256'] == digest(manifest_raw)
                 and result['status'] in ('IN_PROGRESS', 'APPROVE', 'REQUEST_CHANGES'), 'RESULT_BINDING')
        for name in ('findings', 'questions', 'claimed_inspected_files', 'remaining_obligations'):
            _strings(result[name])
        access = _json(manifest['access_manifest_original'].encode())
        _require(set(result['claimed_inspected_files']) <= set(access['files']), 'CLAIM_OUTSIDE_VIEW')
        _require(isinstance(result['resolved'], list) and len(result['resolved']) <= 512, 'RESOLUTION_LIST')
        for resolution in result['resolved']:
            _keys(resolution, 'field original response', 'RESOLUTION_SCHEMA')
            _require(resolution['field'] in ('findings', 'questions', 'remaining_obligations'), 'RESOLUTION_FIELD')
            _text(resolution['original']); _text(resolution['response'])
        _require(len({(row['field'], row['original']) for row in result['resolved']}) == len(result['resolved']), 'DUPLICATE_RESOLUTION')
        tool_failures = []
        reads, denials = _journal(manifest, number, events, journal,
                                  runtime_cli_sha256=probe.get('runtime_cli_sha256'), attribution=attribution,
                                  observed_failures=tool_failures)
        if tool_failures:
            receipt['tool_failures'] = tool_failures
        receipt.update(attempt=number, previous_receipt_sha256=previous_hash, status=result['status'], result=result,
                       reads=reads, required_ranges_missing=_coverage(manifest['required_ranges'], reads),
                       provider_model=attribution['provider_model'] if attribution else MODEL,
                       usage_models=usage, admission=admission, denials=denials,
                       host_reads_require_protected_original_authentication=True,
                       admission_requires_protected_original_authentication=True)
        if attribution:
            receipt.update(requested_model=requested, assistant_models=attribution['assistant_models'],
                           model_policy_version=policy_version, model_policy=attribution)
        # Session validation checks cumulative coverage and cross-turn obligations.
    except (ValueError, TypeError, KeyError, UnicodeError, AttributeError) as error:
        receipt['reason'] = str(error)
    return receipt


def parse_attempt(manifest_raw, originals, *, prior_attempts=None):
    """Continuations establish state only by revalidating full raw predecessors."""
    previous = None
    if prior_attempts is not None:
        chain = validate_session(manifest_raw, prior_attempts)
        _require(chain['status'] == 'IN_PROGRESS', 'MODEL_POLICY_PRIOR_NOT_PROGRESS')
        previous = chain['attempts'][-1]
    return _parse_attempt(manifest_raw, originals, previous=previous)


def validate_session(manifest_raw, attempts):
    """Validate every preserved attempt; a terminal verdict cannot be resumed."""
    manifest = validate_manifest(manifest_raw)
    _require(isinstance(attempts, list) and 0 < len(attempts) <= manifest['max_attempts'], 'SESSION_ATTEMPTS')
    receipts, reads, previous = [], {}, None
    for number, originals in enumerate(attempts, 1):
        receipt = _parse_attempt(manifest_raw, originals, previous=previous)
        if receipt['status'] == 'RECONCILIATION_REQUIRED':
            return {'status': 'RECONCILIATION_REQUIRED', 'attempts': receipts + [receipt], 'automatic_retry': False}
        _require(receipt['attempt'] == number and receipt['previous_receipt_sha256'] ==
                 (digest(encoded(previous)) if previous else None), 'BROKEN_ATTEMPT_CHAIN')
        if previous:
            _require(previous['status'] == 'IN_PROGRESS', 'TERMINAL_REVIEW_CANNOT_RESUME')
            old_admission, new_admission = previous['admission'], receipt['admission']
            _require(new_admission['day'] > old_admission['day'] or
                     (new_admission['day'] == old_admission['day'] and new_admission['count'] > old_admission['count']), 'ADMISSION_NOT_ADVANCED')
            old, new = previous['result'], receipt['result']
            resolved = {(item['field'], item['original']) for item in new['resolved']}
            for field in ('findings', 'questions', 'remaining_obligations'):
                _require(all(item in new[field] or (field, item) in resolved for item in old[field]), 'PRIOR_OBLIGATION_DROPPED')
            _require(all(item['original'] in old[item['field']] for item in new['resolved']), 'UNBOUND_RESOLUTION')
        else:
            _require(not receipt['result']['resolved'], 'RESOLUTION_WITHOUT_PREVIOUS_ATTEMPT')
        for name, intervals in receipt['reads'].items():
            reads.setdefault(name, []).extend(intervals)
        receipts.append(receipt)
        previous = receipt
    missing = _coverage(manifest['required_ranges'], reads)
    result = previous['result']
    if previous['status'] == 'APPROVE':
        _require(not missing and not result['questions'] and not result['remaining_obligations'], 'APPROVAL_WITH_UNRESOLVED_COVERAGE_OR_QUESTIONS')
    answer = {'schema': 'formal-inspection-session/v1', 'status': previous['status'], 'source': manifest['source'],
            'session_id': manifest['session_id'], 'manifest_sha256': digest(manifest_raw), 'attempts': receipts,
            'reads': reads, 'required_ranges_missing': missing, 'result': result,
            'automatic_retry': False, 'approval_confers_deployment_authority': False,
            'output_private_until_existing_publication_scan': True}
    if manifest.get('model_policy_version') is not None:
        answer.update(provider_model=previous['provider_model'],
                      requested_model=model_policy.requested_model(manifest['model_policy_version']),
                      model_policy_version=manifest['model_policy_version'])
    return answer
