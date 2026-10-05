"""Synthetic protocols only: these fixtures are never provider evidence."""
import copy
import json
import uuid
import pytest
from orchestrator import inspection_model_policy as m

SESSION = '11111111-1111-1111-1111-111111111111'


def identify(events):
    session = events[0].get('session_id', SESSION)
    for i, e in enumerate(events):
        e['uuid'] = str(uuid.UUID(int=i + 1))
        e['session_id'] = session
    return events


def plain(model=m.REQUESTED):
    return identify([
        {'type': 'system', 'subtype': 'init', 'model': m.REQUESTED},
        {'type': 'assistant', 'message': {'model': model, 'content': [
            {'type': 'text', 'text': 'Synthetic protocol, not an actual review.'}]}},
        {'type': 'result', 'subtype': 'success', 'is_error': False,
         'modelUsage': {model: {'canonicalModel': model, 'inputTokens': 1}}}])


def fallback(events=None):
    """Add the exact synthetic unexecuted pair; preserve actual tool events."""
    events = copy.deepcopy(events if events is not None else plain())
    key = 'synthetic-unexecuted-glob'
    request = 'synthetic-provider-request'
    issue = [{'expected': 'string', 'code': 'invalid_type', 'path': ['pattern'],
              'message': 'Invalid input: expected string, received undefined'}]
    pair = [
        {'type': 'assistant', 'request_id': request,
         'message': {'model': m.REQUESTED, 'content': [
             {'type': 'tool_use', 'id': key, 'name': 'Glob', 'input': {}}]}},
        {'type': 'user', 'tool_use_result': 'InputValidationError: '+json.dumps(issue, indent=2),
         'message': {'content': [{'type': 'tool_result', 'tool_use_id': key, 'is_error': True,
          'content': '<tool_use_error>InputValidationError: Glob failed due to the following issue:\n'
                     'The required parameter '+chr(96)+'pattern'+chr(96)+' is missing</tool_use_error>'}]}},
        {'type': 'system', 'subtype': 'model_refusal_fallback', 'trigger': 'refusal',
         'direction': 'retry', 'scope': 'session', 'original_model': m.REQUESTED,
         'fallback_model': m.FALLBACK, 'api_refusal_category': 'cyber',
         'api_refusal_explanation': None, 'request_id': request}]
    events[1:1] = pair
    identify(events)
    ids = [events[1]['uuid'], events[2]['uuid']]
    events[3]['retracted_message_uuids'] = ids
    after = [e for e in events[4:] if e.get('type') == 'assistant']
    for e in after:
        e['message']['model'] = m.FALLBACK
    after[0]['supersedes'] = ids[:]
    events[-1]['modelUsage'] = {
        n: {'canonicalModel': n, 'inputTokens': 1} for n in (m.REQUESTED, m.FALLBACK)}
    return events


def analyze(events, **kwargs):
    return m.analyze(events, session_id=SESSION, runtime_cli_sha256=m.CLI_SHA256, **kwargs)


def test_exact_fallback_preserves_originals_and_zero_coverage():
    events = fallback(); original = copy.deepcopy(events)
    result = analyze(events)
    assert events == original
    assert result['provider_model'] == m.FALLBACK
    assert result['assistant_models'] == [m.REQUESTED, m.FALLBACK]
    assert result['fallback_events'] == [events[3]]
    assert result['usage_models'] == events[-1]['modelUsage']
    assert result['unexecuted_retracted'][0]['coverage'] == []
    assert result['unexecuted_retracted'][0]['tool_use_event'] == events[1]
    assert result['unexecuted_retracted'][0]['tool_result_event'] == events[2]


@pytest.mark.parametrize('explanation', [None, '', 'Synthetic native category explanation'])
def test_explanation_is_not_a_category_discriminator(explanation):
    events = fallback(); events[3]['api_refusal_explanation'] = explanation
    assert analyze(events)['provider_model'] == m.FALLBACK


@pytest.mark.parametrize('field,value', [
    ('type', 'assistant'), ('trigger', 'timeout'), ('direction', 'continue'),
    ('scope', 'request'), ('original_model', m.FALLBACK),
    ('fallback_model', 'claude-opus-5'), ('api_refusal_category', 'biology'),
    ('session_id', '22222222-2222-2222-2222-222222222222'),
    ('request_id', 'unrelated'), ('api_refusal_explanation', {}),
    ('retracted_message_uuids', []), ('retracted_message_uuids', [{}, {}])])
def test_fallback_field_near_miss_refuses(field, value):
    events = fallback(); events[3][field] = value
    with pytest.raises(ValueError): analyze(events)


@pytest.mark.parametrize('mutation', [
    'wrong_requested', 'wrong_cli', 'before_opus', 'after_fable', 'mixed_after',
    'extra_fallback', 'missing_usage', 'unknown_usage', 'opus5_usage', 'alias',
    'missing_uuid', 'duplicate_uuid', 'supersedes_missing', 'supersedes_extra',
    'reversed_pair', 'foreign_pair', 'extra_content', 'extra_result_content',
    'nonempty_glob', 'read_instead', 'not_error', 'human_error', 'raw_error_changed',
    'output_added', 'id_reused', 'permission_conflict', 'hook_protocol_conflict',
    'no_final_success', 'wrong_pair_request'])
def test_exact_pair_and_identity_near_misses_refuse(mutation):
    e = fallback()
    if mutation == 'wrong_requested': e[0]['model'] = m.FALLBACK
    elif mutation == 'wrong_cli':
        with pytest.raises(ValueError): m.analyze(e, session_id=SESSION, runtime_cli_sha256='0'*64)
        return
    elif mutation == 'before_opus': e[1]['message']['model'] = m.FALLBACK
    elif mutation == 'after_fable': e[4]['message']['model'] = m.REQUESTED
    elif mutation == 'mixed_after':
        x = copy.deepcopy(e[4]); x['uuid'] = str(uuid.UUID(int=100)); x.pop('supersedes')
        x['message']['model'] = m.REQUESTED; e.insert(-1, x)
    elif mutation == 'extra_fallback':
        x = copy.deepcopy(e[3]); x['uuid'] = str(uuid.UUID(int=100)); e.insert(-1, x)
    elif mutation == 'missing_usage': e[-1]['modelUsage'].pop(m.REQUESTED)
    elif mutation == 'unknown_usage': e[-1]['modelUsage']['unknown'] = {}
    elif mutation == 'opus5_usage': e[-1]['modelUsage']['claude-opus-5'] = {}
    elif mutation == 'alias': e[-1]['modelUsage'][m.FALLBACK]['canonicalModel'] = 'alias'
    elif mutation == 'missing_uuid': e[2].pop('uuid')
    elif mutation == 'duplicate_uuid': e[4]['uuid'] = e[1]['uuid']
    elif mutation == 'supersedes_missing': e[4].pop('supersedes')
    elif mutation == 'supersedes_extra': e[4]['supersedes'].append(str(uuid.UUID(int=100)))
    elif mutation == 'reversed_pair': e[3]['retracted_message_uuids'].reverse()
    elif mutation == 'foreign_pair': e[3]['retracted_message_uuids'][0] = e[0]['uuid']
    elif mutation == 'extra_content': e[1]['message']['content'].append({'type': 'text', 'text': 'unproved'})
    elif mutation == 'extra_result_content': e[2]['message']['content'].append({'type': 'text', 'text': 'unproved'})
    elif mutation == 'nonempty_glob': e[1]['message']['content'][0]['input'] = {'pattern': '**'}
    elif mutation == 'read_instead': e[1]['message']['content'][0]['name'] = 'Read'
    elif mutation == 'not_error': e[2]['message']['content'][0]['is_error'] = False
    elif mutation == 'human_error': e[2]['message']['content'][0]['content'] = 'Permission denied'
    elif mutation == 'raw_error_changed': e[2]['tool_use_result'] += ' '
    elif mutation == 'output_added': e[2]['message']['content'][0]['partial_output'] = 'x'
    elif mutation == 'id_reused':
        x = copy.deepcopy(e[1]); x['uuid'] = str(uuid.UUID(int=100))
        x['message']['model'] = m.FALLBACK; e.insert(-1, x)
    elif mutation == 'permission_conflict':
        e[-1]['permission_denials'] = [{'tool_use_id': 'synthetic-unexecuted-glob'}]
    elif mutation == 'hook_protocol_conflict':
        e.insert(3, {'uuid': str(uuid.UUID(int=100)), 'type': 'system', 'subtype': 'hook_started',
                     'tool_use_id': 'synthetic-unexecuted-glob', 'session_id': SESSION})
    elif mutation == 'no_final_success': e[-1]['is_error'] = True
    elif mutation == 'wrong_pair_request': e[1]['request_id'] = 'other'
    with pytest.raises(ValueError): analyze(e)


@pytest.mark.parametrize('side', ['observation_original', 'hook_input_original'])
def test_any_original_journal_link_prevents_unexecuted_classification(side):
    row = {'observation_original': '{}', 'hook_input_original': '{}'}
    row[side] = json.dumps({'tool_use_id': 'synthetic-unexecuted-glob'})
    with pytest.raises(ValueError): analyze(fallback(), journal=[json.dumps(row)])


def test_fable_only_and_known_auxiliary():
    e = plain(); e[-1]['modelUsage'][m.AUXILIARY] = {'canonicalModel': 'claude-haiku-4-5'}
    value = analyze(e)
    assert value['provider_model'] == m.REQUESTED and value['unexecuted_retracted'] == []


def test_continuation_requires_original_fallback_state_and_rejects_reset():
    previous = analyze(fallback())
    e = plain(m.FALLBACK)
    result = analyze(e, previous=previous)
    assert result['provider_model'] == m.FALLBACK and result['fallback_events'] == []
    assert result['session_fallback_event'] == previous['session_fallback_event']
    assert result['previous_policy_sha256'] == m.digest(m.encoded(previous))
    with pytest.raises(ValueError): analyze(e)
    with pytest.raises(ValueError): analyze(plain(), previous=previous)
    with pytest.raises(ValueError): analyze(fallback(), previous=previous)
    e[0]['model'] = m.FALLBACK
    with pytest.raises(ValueError): analyze(e, previous=previous)


def thinking_fallback(events=None):
    """Synthetic coherent R2 case, not the historically unqualified old stream."""
    e = fallback(events)
    e[1]['message']['content'] = [{'type': 'thinking', 'thinking': '', 'signature': 'synthetic'}]
    del e[2]
    identify(e)
    e[2]['retracted_message_uuids'] = [e[1]['uuid']]
    after = next(x for x in e[3:] if x.get('type') == 'assistant')
    after['supersedes'] = e[2]['retracted_message_uuids'][:]
    return e


def executed_fallback(events):
    """Retract the first existing completed call; every normal check still applies."""
    e = copy.deepcopy(events)
    use, result = e[1:3]
    use['request_id'] = 'synthetic-provider-request'
    event = copy.deepcopy(fallback()[3])
    e.insert(3, event)
    if not any(x.get('type') == 'assistant' for x in e[4:]):
        e.insert(4, {'type': 'assistant', 'message': {'model': m.FALLBACK,
            'content': [{'type': 'text', 'text': 'Synthetic continuing review.'}]}})
    identify(e)
    event['retracted_message_uuids'] = [use['uuid'], result['uuid']]
    after = [x for x in e[4:] if x.get('type') == 'assistant']
    for x in after: x['message']['model'] = m.FALLBACK
    after[0]['supersedes'] = event['retracted_message_uuids'][:]
    e[-1]['modelUsage'] = {n: {'canonicalModel': n, 'inputTokens': 1}
                          for n in (m.REQUESTED, m.FALLBACK)}
    return e


def test_thinking_retraction_qualifies_identity_without_inventing_an_exemption():
    e = thinking_fallback(); original = copy.deepcopy(e)
    result = analyze(e)
    assert e == original
    assert result['provider_model'] == m.FALLBACK and result['unexecuted_retracted'] == []
    assert result['retracted_events'] == [{'event_index': 1, 'event': e[1]}]


@pytest.mark.parametrize('case', ['missing_supersedes', 'wrong_request', 'duplicate_retraction',
    'future_retraction', 'system_retraction', 'result_without_use', 'wrong_usage',
    'tool_without_result', 'unknown_content', 'empty_retraction'])
def test_non_tool_retraction_still_requires_complete_r2_links(case):
    e = thinking_fallback()
    if case == 'missing_supersedes': e[3].pop('supersedes')
    elif case == 'wrong_request': e[1]['request_id'] = 'unrelated'
    elif case == 'duplicate_retraction': e[2]['retracted_message_uuids'] *= 2
    elif case == 'future_retraction': e[2]['retracted_message_uuids'] = [e[3]['uuid']]
    elif case == 'system_retraction': e[2]['retracted_message_uuids'] = [e[0]['uuid']]
    elif case == 'result_without_use': e[1]['message']['content'][0]['type'] = 'tool_result'
    elif case == 'wrong_usage': e[-1]['modelUsage']['claude-opus-5'] = {}
    elif case == 'tool_without_result':
        e[1]['message']['content'] = [{'type': 'tool_use', 'id': 'unmatched', 'name': 'Read',
                                      'input': {'file_path': '/review/synthetic.txt'}}]
    elif case == 'unknown_content': e[1]['message']['content'][0]['type'] = 'unknown'
    elif case == 'empty_retraction': e[2]['retracted_message_uuids'] = []
    with pytest.raises(ValueError): analyze(e)
