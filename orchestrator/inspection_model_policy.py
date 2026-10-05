"""Prospective direct-inspection attribution; never rewrite original activity.

Only callers with authenticated originals and the explicit reviewed version may
use this pure predicate. A previous policy is internal state from revalidated
raw predecessor attempts, never a caller-supplied model grant.
"""
import copy
import hashlib
import json
import re

VERSION = 'direct-inspection-cyber-fallback/v2'
DIRECT_VERSION = 'direct-inspection-opus-4-8/v1'
CURRENT_VERSION = DIRECT_VERSION
DIRECT_MODEL = 'claude-opus-4-8'
REQUESTED = 'claude-fable-5'
FALLBACK = 'claude-opus-4-8'
AUXILIARY = 'claude-haiku-4-5-20251001'
CLI_SHA256 = '10caae8f22b915c26bfff0e013a4d45608c4f1ae287583626569156f447730e5'


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(value, reason):
    if not value:
        raise ValueError(reason)


def version(value):
    require(value in (None, VERSION, DIRECT_VERSION), 'INSPECTION_MODEL_POLICY_VERSION')
    return value


def requested_model(policy_version=None):
    """An immutable profile selects one model; there is no caller-selected name."""
    version(policy_version)
    return DIRECT_MODEL if policy_version == DIRECT_VERSION else REQUESTED


def _direct_activity(value):
    """Reject actual control/error metadata, not quoted source or review prose."""
    if isinstance(value, list):
        for item in value:
            _direct_activity(item)
    elif isinstance(value, dict):
        require(all(isinstance(key, str) for key in value), 'INSPECTION_POLICY_EVENTS')
        require(not any('retract' in key.lower() or key.lower() == 'supersedes' for key in value)
                and not any(isinstance(value.get(key), str)
                            and any(tag in value[key].lower() for tag in ('retract', 'tombstone', 'supersedes'))
                            for key in ('type', 'subtype')), 'INSPECTION_DIRECT_RETRACTION')
        require(not any('fallback' in key.lower() for key in value)
                and not any(isinstance(value.get(key), str) and 'fallback' in value[key].lower()
                            for key in ('type', 'subtype')), 'INSPECTION_DIRECT_FALLBACK')
        if 'model_policy_version' in value:
            require(value['model_policy_version'] == DIRECT_VERSION, 'INSPECTION_DIRECT_PROFILE')
        raw_error = value.get('tool_use_result')
        require(not (isinstance(raw_error, str) and raw_error.startswith('InputValidationError:'))
                and not any(isinstance(value.get(key), str) and value[key].startswith('InputValidationError')
                            for key in ('type', 'subtype', 'error', 'error_type', 'code')),
                'INSPECTION_DIRECT_INPUT_VALIDATION')
        if value.get('type') == 'tool_result':
            content = value.get('content')
            text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
            require(not (text.startswith('<tool_use_error>InputValidationError:')
                         or text.startswith('InputValidationError:')
                         or value.get('is_error') is True and 'InputValidationError' in text),
                    'INSPECTION_DIRECT_INPUT_VALIDATION')
        # File contents and findings remain opaque strings. They must be readable
        # even when documenting a previous fallback or InputValidationError.
        for item in value.values():
            if isinstance(item, (dict, list)):
                _direct_activity(item)


def _direct(events, session_id, runtime_cli_sha256, previous):
    require(runtime_cli_sha256 == CLI_SHA256, 'INSPECTION_POLICY_CLI_PIN')
    require(isinstance(events, list) and events and all(isinstance(e, dict) for e in events),
            'INSPECTION_POLICY_EVENTS')
    _direct_activity(events)
    require(events[0].get('type') == 'system' and events[0].get('subtype') == 'init'
            and events[0].get('model') == DIRECT_MODEL, 'INSPECTION_POLICY_REQUESTED_MODEL')
    require(all(e.get('session_id', session_id) == session_id for e in events),
            'INSPECTION_POLICY_SESSION')
    terminal = events[-1]
    require(terminal.get('type') == 'result' and terminal.get('subtype') == 'success'
            and terminal.get('is_error') is False, 'INSPECTION_POLICY_TERMINAL')
    identities = set()
    for event in events:
        identity = event.get('uuid')
        require(isinstance(identity, str) and re.fullmatch(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}', identity)
                and identity not in identities, 'INSPECTION_POLICY_EVENT_UUID')
        identities.add(identity)
    messages = [(i, e) for i, e in enumerate(events) if e.get('type') == 'assistant']
    require(messages and all(e.get('message', {}).get('model') == DIRECT_MODEL for _, e in messages),
            'INSPECTION_DIRECT_ASSISTANT_MODEL')
    _usage(terminal.get('modelUsage'), {DIRECT_MODEL})
    if previous is not None:
        require(previous.get('policy_version') == DIRECT_VERSION
                and previous.get('session_id') == session_id
                and previous.get('runtime_cli_sha256') == CLI_SHA256
                and previous.get('requested_model') == previous.get('provider_model') == DIRECT_MODEL
                and previous.get('assistant_models') == [DIRECT_MODEL]
                and previous.get('fallback_events') == [] and previous.get('session_fallback_event') is None
                and previous.get('retracted_events') == [] and previous.get('unexecuted_retracted') == [],
                'INSPECTION_POLICY_PREVIOUS_STATE')
    return {'policy_version': DIRECT_VERSION, 'session_id': session_id, 'runtime_cli_sha256': CLI_SHA256,
            'requested_model': DIRECT_MODEL, 'provider_model': DIRECT_MODEL,
            'assistant_models': [DIRECT_MODEL],
            'assistant_messages': [{'event_index': i, 'uuid': e['uuid'], 'model': DIRECT_MODEL}
                                   for i, e in messages],
            'fallback_events': [], 'session_fallback_event': None,
            'usage_models': copy.deepcopy(terminal['modelUsage']), 'retracted_events': [],
            'unexecuted_retracted': [],
            'previous_policy_sha256': digest(encoded(previous)) if previous else None}


def _usage(usage, models):
    require(isinstance(usage, dict) and set(usage) - {AUXILIARY} == models
            and set(usage) <= models | {AUXILIARY}, 'INSPECTION_POLICY_USAGE_MODELS')
    for name, row in usage.items():
        canonical = (name, 'claude-haiku-4-5') if name == AUXILIARY else (name,)
        require(isinstance(row, dict) and row.get('canonicalModel', name) in canonical,
                'INSPECTION_POLICY_USAGE_IDENTITY')


def _retractions(fallback_index, event, by_uuid):
    """R2 linkage only; linked tool activity remains subject to every caller check."""
    ids = event.get('retracted_message_uuids')
    require(isinstance(ids, list) and ids
            and all(isinstance(v, str) and v in by_uuid for v in ids)
            and len(set(ids)) == len(ids), 'INSPECTION_POLICY_RETRACTION_LINK')
    rows = [by_uuid[v] for v in ids]
    indices = [i for i, _ in rows]
    require(indices == sorted(indices) and indices[-1] < fallback_index
            and rows[0][1].get('type') == 'assistant',
            'INSPECTION_POLICY_RETRACTION_ORDER')
    request = event.get('request_id')
    require(isinstance(request, str) and bool(request), 'INSPECTION_POLICY_FALLBACK_REQUEST')
    uses, results = {}, {}
    early_error = False
    for index, original in rows:
        content = original.get('message', {}).get('content')
        require(isinstance(content, list) and content
                and all(isinstance(item, dict) for item in content),
                'INSPECTION_POLICY_RETRACTION_CONTENT')
        if original.get('type') == 'assistant':
            require(original.get('request_id') == request,
                    'INSPECTION_POLICY_FALLBACK_REQUEST')
            for item in content:
                require(item.get('type') in ('text', 'thinking', 'redacted_thinking', 'tool_use'),
                        'INSPECTION_POLICY_RETRACTION_CONTENT')
                if item['type'] == 'tool_use':
                    key = item.get('id')
                    require(isinstance(key, str) and key not in uses,
                            'INSPECTION_POLICY_RETRACTION_TOOL_LINK')
                    uses[key] = index
                    early_error |= ((item.get('name') == 'Glob' and item.get('input') == {})
                                    or (item.get('name') == 'Grep'
                                        and item.get('input') == {'path': '/state/canary'}))
        elif original.get('type') == 'user':
            for item in content:
                key = item.get('tool_use_id')
                require(item.get('type') == 'tool_result' and isinstance(key, str)
                        and key in uses and key not in results and uses[key] < index,
                        'INSPECTION_POLICY_RETRACTION_TOOL_LINK')
                results[key] = index
                # An asserted native schema failure cannot silently become an
                # ordinary executed retraction when its exact R3 proof is wrong.
                raw = original.get('tool_use_result')
                rendered = item.get('content')
                early_error |= item.get('is_error') is True and (
                    isinstance(raw, str) and raw.startswith('InputValidationError:') or
                    isinstance(rendered, str) and rendered.startswith('<tool_use_error>InputValidationError:'))
        else:
            require(False, 'INSPECTION_POLICY_RETRACTION_CONTENT')
    require(set(uses) == set(results), 'INSPECTION_POLICY_RETRACTION_TOOL_LINK')
    return [{'event_index': i, 'event': copy.deepcopy(original)} for i, original in rows], early_error


def _unexecuted(events, fallback_index, event, by_uuid, journal, terminal):
    """Two fixed native missing-pattern shapes; never arbitrary schema failures."""
    ids = event.get('retracted_message_uuids')
    require(isinstance(ids, list) and len(ids) == 2
            and all(isinstance(v, str) and v in by_uuid for v in ids) and len(set(ids)) == 2,
            'INSPECTION_POLICY_RETRACTION_LINK')
    left, right = (by_uuid[v] for v in ids)
    ui, ue = left
    ri, revent = right
    require(ui + 1 == ri < fallback_index and ue.get('type') == 'assistant'
            and revent.get('type') == 'user', 'INSPECTION_POLICY_RETRACTION_ORDER')
    uc = ue.get('message', {}).get('content')
    rc = revent.get('message', {}).get('content')
    require(isinstance(uc, list) and len(uc) == 1 and isinstance(uc[0], dict)
            and isinstance(rc, list) and len(rc) == 1 and isinstance(rc[0], dict),
            'INSPECTION_POLICY_RETRACTION_PAIR')
    use, result = uc[0], rc[0]
    key = use.get('id')
    tool = use.get('name')
    shape = ((tool == 'Glob' and use.get('input') == {})
             or (tool == 'Grep' and use.get('input') == {'path': '/state/canary'}))
    require(use.get('type') == 'tool_use' and shape and isinstance(key, str)
            and re.fullmatch(r'[A-Za-z0-9_-]{1,128}', key)
            and result.get('type') == 'tool_result' and result.get('tool_use_id') == key
            and result.get('is_error') is True, 'INSPECTION_POLICY_RETRACTED_PATTERN_CALL')
    text = (tool+' failed due to the following issue:\n'
            'The required parameter '+chr(96)+'pattern'+chr(96)+' is missing')
    issues = [{'expected': 'string', 'code': 'invalid_type', 'path': ['pattern'],
               'message': 'Invalid input: expected string, received undefined'}]
    require(result == {'type': 'tool_result', 'tool_use_id': key, 'is_error': True,
                       'content': '<tool_use_error>InputValidationError: '+text+'</tool_use_error>'}
            and revent.get('tool_use_result') == 'InputValidationError: '+json.dumps(issues, indent=2),
            'INSPECTION_POLICY_EXACT_PATTERN_SCHEMA_REFUSAL')
    require(isinstance(event.get('request_id'), str) and bool(event['request_id'])
            and ue.get('request_id') == event['request_id'],
            'INSPECTION_POLICY_FALLBACK_REQUEST')
    # Uniqueness is global; neither a later successful use/result nor an orphan
    # hook can be hidden behind a retracted UUID.
    uses, results = [], []
    for i, original in enumerate(events):
        for item in original.get('message', {}).get('content', []):
            if item.get('type') == 'tool_use' and item.get('id') == key:
                uses.append(i)
            if item.get('type') == 'tool_result' and item.get('tool_use_id') == key:
                results.append(i)
        if original.get('subtype') in ('hook_started', 'hook_response'):
            require(original.get('tool_use_id', original.get('toolUseID')) != key,
                    'INSPECTION_POLICY_RETRACTED_HOOK_CONFLICT')
    require(uses == [ui] and results == [ri], 'INSPECTION_POLICY_RETRACTED_ID_REUSED')
    for raw in journal:
        wrapped = json.loads(raw)
        row = json.loads(wrapped['observation_original'])
        hook = json.loads(wrapped['hook_input_original'])
        require(row.get('tool_use_id') != key and hook.get('tool_use_id') != key,
                'INSPECTION_POLICY_RETRACTED_HOOK_CONFLICT')
    denials = terminal.get('permission_denials', [])
    require(isinstance(denials, list) and all(isinstance(d, dict) and d.get('tool_use_id') != key
                                            for d in denials),
            'INSPECTION_POLICY_RETRACTED_PERMISSION_CONFLICT')
    return {'kind': 'NATIVE_UNEXECUTED_RETRACTED_'+tool.upper(), 'tool_use_id': key,
            'tool_name': tool, 'coverage': [], 'runtime_cli_sha256': CLI_SHA256,
            'tool_use_event': copy.deepcopy(ue), 'tool_result_event': copy.deepcopy(revent),
            'retracted_message_uuids': list(ids), 'use_event_index': ui,
            'result_event_index': ri, 'fallback_event_index': fallback_index}


def analyze(events, *, session_id, runtime_cli_sha256, journal=(), previous=None, policy_version=VERSION):
    """Internal pure classifier. Previous comes only from validated raw history."""
    version(policy_version)
    require(policy_version is not None, 'INSPECTION_MODEL_POLICY_VERSION')
    if policy_version == DIRECT_VERSION:
        return _direct(events, session_id, runtime_cli_sha256, previous)
    require(runtime_cli_sha256 == CLI_SHA256, 'INSPECTION_POLICY_CLI_PIN')
    require(isinstance(events, list) and events and all(isinstance(e, dict) for e in events),
            'INSPECTION_POLICY_EVENTS')
    require(events[0].get('type') == 'system' and events[0].get('subtype') == 'init'
            and events[0].get('model') == REQUESTED, 'INSPECTION_POLICY_REQUESTED_MODEL')
    require(all(e.get('session_id', session_id) == session_id for e in events),
            'INSPECTION_POLICY_SESSION')
    terminal = events[-1]
    require(terminal.get('type') == 'result' and terminal.get('subtype') == 'success'
            and terminal.get('is_error') is False, 'INSPECTION_POLICY_TERMINAL')
    by_uuid = {}
    for i, event in enumerate(events):
        identity = event.get('uuid')
        require(isinstance(identity, str) and re.fullmatch(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}', identity)
                and identity not in by_uuid, 'INSPECTION_POLICY_EVENT_UUID')
        by_uuid[identity] = (i, event)
    messages = [(i, e) for i, e in enumerate(events) if e.get('type') == 'assistant']
    require(messages, 'INSPECTION_POLICY_ASSISTANT_MISSING')
    fallbacks = [(i, e) for i, e in enumerate(events) if e.get('subtype') == 'model_refusal_fallback']
    require(len(fallbacks) <= 1, 'INSPECTION_POLICY_MULTIPLE_FALLBACKS')
    inherited = previous is not None and previous.get('provider_model') == FALLBACK
    if previous is not None:
        require(previous.get('policy_version') == VERSION and previous.get('session_id') == session_id
                and previous.get('runtime_cli_sha256') == CLI_SHA256
                and previous.get('provider_model') in (REQUESTED, FALLBACK),
                'INSPECTION_POLICY_PREVIOUS_STATE')
    excluded, retracted = [], []
    origin = copy.deepcopy(previous.get('session_fallback_event')) if inherited else None
    if fallbacks:
        require(not inherited, 'INSPECTION_POLICY_SECOND_SESSION_FALLBACK')
        index, event = fallbacks[0]
        expected = {'type': 'system', 'subtype': 'model_refusal_fallback',
                    'trigger': 'refusal', 'direction': 'retry', 'scope': 'session',
                    'original_model': REQUESTED, 'fallback_model': FALLBACK,
                    'api_refusal_category': 'cyber', 'session_id': session_id}
        require(all(event.get(k) == v for k, v in expected.items())
                and 'api_refusal_explanation' in event
                and (event['api_refusal_explanation'] is None or isinstance(event['api_refusal_explanation'], str)),
                'INSPECTION_POLICY_FALLBACK_IDENTITY')
        before = [e for i, e in messages if i < index]
        after = [e for i, e in messages if i > index]
        require(before and after and all(e['message'].get('model') == REQUESTED for e in before)
                and all(e['message'].get('model') == FALLBACK for e in after),
                'INSPECTION_POLICY_TEMPORAL_MODELS')
        retracted, early_error = _retractions(index, event, by_uuid)
        if early_error:
            excluded = [_unexecuted(events, index, event, by_uuid, journal, terminal)]
        require(after[0].get('supersedes') == event['retracted_message_uuids'],
                'INSPECTION_POLICY_SUPERSEDES')
        require(all('supersedes' not in e for _, e in messages if e is not after[0]),
                'INSPECTION_POLICY_EXTRA_SUPERSEDES')
        origin = copy.deepcopy(event)
        provider = FALLBACK
        _usage(terminal.get('modelUsage'), {REQUESTED, FALLBACK})
    else:
        provider = FALLBACK if inherited else REQUESTED
        require(all(e['message'].get('model') == provider for _, e in messages)
                and all('supersedes' not in e for _, e in messages),
                'INSPECTION_POLICY_UNEXPLAINED_MODEL')
        _usage(terminal.get('modelUsage'), {provider})
        require(not inherited or isinstance(origin, dict), 'INSPECTION_POLICY_FALLBACK_ORIGIN')
    require(messages[-1][1]['message'].get('model') == provider,
            'INSPECTION_POLICY_FINAL_ATTRIBUTION')
    return {'policy_version': VERSION, 'session_id': session_id, 'runtime_cli_sha256': CLI_SHA256,
            'requested_model': REQUESTED, 'provider_model': provider,
            'assistant_models': sorted({e['message']['model'] for _, e in messages}),
            'assistant_messages': [{'event_index': i, 'uuid': e['uuid'], 'model': e['message']['model']}
                                   for i, e in messages],
            'fallback_events': [copy.deepcopy(e) for _, e in fallbacks],
            'session_fallback_event': origin, 'usage_models': copy.deepcopy(terminal['modelUsage']),
            'retracted_events': retracted, 'unexecuted_retracted': excluded,
            'previous_policy_sha256': digest(encoded(previous)) if previous else None}
