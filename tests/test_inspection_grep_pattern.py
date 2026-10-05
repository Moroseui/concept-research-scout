"""Synthetic v2 regressions; fixtures never establish native canary success."""
import copy
import json
import uuid
import pytest
from orchestrator import inspection_model_policy as m
from orchestrator import inspection_review as r
from orchestrator import inspection_canary as c
from test_inspection_model_policy import fallback, plain, analyze
from test_inspection_fallback_integration import policy_manifest, policy_attempt, prospective_canary
from test_inspection_review import events, replace_events
from test_inspection_canary import events as canary_events, save_events

OLD_VERSION = 'direct-inspection-cyber-fallback/v1'


def grep_pair(e):
    """Replace only the synthetic malformed Glob pair with the observed input shape."""
    e = copy.deepcopy(e)
    use = e[1]['message']['content'][0]
    use['name'] = 'Grep'
    use['input'] = {'path': '/state/canary'}
    e[2]['message']['content'][0]['content'] = e[2]['message']['content'][0]['content'].replace(
        'Glob failed', 'Grep failed')
    return e


def test_exact_grep_pair_retains_both_originals_and_zero_coverage():
    e = grep_pair(fallback()); original = copy.deepcopy(e)
    answer = analyze(e)
    assert e == original and answer['policy_version'] == m.VERSION
    assert answer['provider_model'] == m.FALLBACK
    only = answer['unexecuted_retracted'][0]
    assert only['kind'] == 'NATIVE_UNEXECUTED_RETRACTED_GREP'
    assert only['tool_name'] == 'Grep' and only['coverage'] == []
    assert only['tool_use_event'] == e[1] and only['tool_result_event'] == e[2]
    assert answer['retracted_events'] == [
        {'event_index': 1, 'event': e[1]}, {'event_index': 2, 'event': e[2]}]


@pytest.mark.parametrize('value', [
    {}, None, [], {'path': '/review'}, {'path': '/state/canary/'},
    {'path': '//state/canary'}, {'path': '/state/./canary'},
    {'path': '/state/canary', 'pattern': None},
    {'path': '/state/canary', 'pattern': ''},
    {'path': '/state/canary', 'pattern': 'secret'},
    {'path': '/state/canary', 'glob': '*'},
    {'path': '/state/canary', 'hidden': True}, {'path': False},
    {'file_path': '/state/canary'}, {'path': '/state/canary', 'offset': 1},
])
def test_only_exact_path_only_input_is_unexecuted(value):
    e = grep_pair(fallback()); e[1]['message']['content'][0]['input'] = value
    with pytest.raises(ValueError): analyze(e)


@pytest.mark.parametrize('mutation', [
    'other_tool', 'wrong_rendered_tool', 'wrong_issue_path', 'permission_error',
    'not_error', 'partial_output', 'extra_user_content', 'extra_assistant_content',
    'raw_whitespace', 'permission_entry', 'protocol_hook', 'result_id',
    'tool_id_reused', 'wrong_request', 'missing_supersedes', 'wrong_cli',
])
def test_nearby_schema_denial_or_executed_evidence_is_never_exempted(mutation):
    e = grep_pair(fallback()); key = e[1]['message']['content'][0]['id']
    if mutation == 'other_tool': e[1]['message']['content'][0]['name'] = 'Read'
    elif mutation == 'wrong_rendered_tool':
        e[2]['message']['content'][0]['content'] = e[2]['message']['content'][0]['content'].replace('Grep', 'Glob')
    elif mutation == 'wrong_issue_path': e[2]['tool_use_result'] = e[2]['tool_use_result'].replace('pattern', 'path')
    elif mutation == 'permission_error':
        e[2]['message']['content'][0]['content'] = 'INSPECTION_ACCESS_REFUSED'
        e[2]['tool_use_result'] = 'Error: INSPECTION_ACCESS_REFUSED'
    elif mutation == 'not_error': e[2]['message']['content'][0]['is_error'] = False
    elif mutation == 'partial_output': e[2]['message']['content'][0]['partial_output'] = 'data'
    elif mutation == 'extra_user_content': e[2]['message']['content'].append({'type': 'text', 'text': 'output'})
    elif mutation == 'extra_assistant_content': e[1]['message']['content'].append({'type': 'text', 'text': 'output'})
    elif mutation == 'raw_whitespace': e[2]['tool_use_result'] += '\n'
    elif mutation == 'permission_entry': e[-1]['permission_denials'] = [{'tool_use_id': key}]
    elif mutation == 'protocol_hook':
        e.insert(3, {'uuid': str(uuid.UUID(int=100)), 'type': 'system',
            'subtype': 'hook_response', 'tool_use_id': key})
    elif mutation == 'result_id': e[2]['message']['content'][0]['tool_use_id'] = 'other'
    elif mutation == 'tool_id_reused':
        extra = copy.deepcopy(e[1]); extra['uuid'] = str(uuid.UUID(int=100))
        extra['message']['model'] = m.FALLBACK; e.insert(-1, extra)
    elif mutation == 'wrong_request': e[1]['request_id'] = 'different'
    elif mutation == 'missing_supersedes': e[4].pop('supersedes')
    elif mutation == 'wrong_cli':
        with pytest.raises(ValueError): m.analyze(e, session_id=e[0]['session_id'], runtime_cli_sha256='0'*64)
        return
    with pytest.raises(ValueError): analyze(e)


@pytest.mark.parametrize('side', ['observation_original', 'hook_input_original'])
def test_any_correlated_original_hook_blocks_grep_exception(side):
    e = grep_pair(fallback()); key = e[1]['message']['content'][0]['id']
    record = {'observation_original': '{}', 'hook_input_original': '{}'}
    record[side] = json.dumps({'tool_use_id': key})
    with pytest.raises(ValueError): analyze(e, journal=[json.dumps(record)])


def test_full_material_receipt_preserves_original_protocol_and_real_read_coverage():
    raw, policy, probe = policy_manifest(); a = policy_attempt(raw, policy, probe)
    replace_events(a, grep_pair(events(a))); original = copy.deepcopy(a)
    answer = r.validate_session(raw, [a])
    assert answer['status'] == 'APPROVE', answer
    assert a == original and answer['reads'] == {'code.py': [[1, 2]]}
    receipt = answer['attempts'][0]
    assert receipt['denials'][0]['kind'] == 'NATIVE_UNEXECUTED_RETRACTED_GREP'
    assert receipt['model_policy']['unexecuted_retracted'][0]['coverage'] == []


def test_canary_keeps_exact_four_calls_and_all_five_hook_observations(tmp_path, monkeypatch):
    bundle, expected = prospective_canary(tmp_path, monkeypatch)
    save_events(bundle['hooks'], grep_pair(canary_events(bundle['hooks'])))
    original = copy.deepcopy(bundle); answer = c.verify_canary(bundle, expected)
    assert bundle == original and answer['model_policy_version'] == m.VERSION
    hooks = answer['phases']['hooks']
    assert len(hooks['tool_use_ids']) == 4 and len(hooks['outside_tool_use_ids']) == 3
    assert len(bundle['hooks']['journal']) == 5
    assert hooks['model_policy']['unexecuted_retracted'][0]['kind'] == 'NATIVE_UNEXECUTED_RETRACTED_GREP'
    assert hooks['model_policy']['unexecuted_retracted'][0]['coverage'] == []


@pytest.mark.parametrize('kind', ['canary', 'material', 'probe'])
def test_old_version_cannot_be_requalified_by_new_classifier(tmp_path, monkeypatch, kind):
    if kind == 'canary':
        bundle, expected = prospective_canary(tmp_path, monkeypatch)
        save_events(bundle['hooks'], grep_pair(canary_events(bundle['hooks'])))
        expected['model_policy_version'] = OLD_VERSION
        with pytest.raises(ValueError): c.verify_canary(bundle, expected)
    else:
        raw, policy, probe = policy_manifest(); value = json.loads(raw)
        if kind == 'material':
            value['model_policy_version'] = OLD_VERSION
            with pytest.raises(ValueError): r.validate_manifest(r.encoded(value))
        else:
            old = json.loads(probe); old['model_policy_version'] = OLD_VERSION
            probe = r.encoded(old); value['permission_probe_sha256'] = r.digest(probe)
            raw = r.encoded(value); a = policy_attempt(raw, policy, probe)
            replace_events(a, grep_pair(events(a)))
            assert r.parse_attempt(raw, a)['reason'] == 'PERMISSION_PROBE_MODEL_POLICY'


def test_prior_policy_state_cannot_cross_versions():
    previous = analyze(grep_pair(fallback())); previous['policy_version'] = OLD_VERSION
    with pytest.raises(ValueError): analyze(plain(m.FALLBACK), previous=previous)


def test_valid_denied_grep_is_retained_as_ordinary_tool_activity():
    e = grep_pair(fallback())
    e[1]['message']['content'][0]['input']['pattern'] = 'synthetic'
    e[2]['message']['content'][0]['content'] = 'INSPECTION_ACCESS_REFUSED'
    e[2]['tool_use_result'] = 'Error: INSPECTION_ACCESS_REFUSED'
    value = analyze(e)
    assert value['unexecuted_retracted'] == []
    assert len(value['retracted_events']) == 2
