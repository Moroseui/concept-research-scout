"""Prospective policy integration with synthetic original receipts only."""
import copy
import importlib.util
import json
import pytest
from orchestrator import inspection_review as r
from orchestrator import inspection_model_policy as m
from test_inspection_review import fixture_manifest, fixture_probe, fixture_attempt, events, replace_events
from test_inspection_model_policy import fallback, identify


def policy_manifest():
    raw, policy = fixture_manifest()
    value = json.loads(raw); value['model_policy_version'] = m.VERSION
    probe = json.loads(fixture_probe())
    probe.update(model_policy_version=m.VERSION, runtime_cli_sha256=m.CLI_SHA256)
    probe_raw = r.encoded(probe)
    value['permission_probe_sha256'] = r.digest(probe_raw)
    return r.encoded(value), policy, probe_raw


def policy_attempt(raw, policy, probe, *, use_fallback=True, continued=False, **kwargs):
    a = fixture_attempt(raw, policy, **kwargs)
    a['permission_probe'] = probe
    e = events(a)
    if use_fallback:
        e = fallback(e)
    else:
        identify(e)
        if continued:
            for x in e:
                if x.get('type') == 'assistant': x['message']['model'] = m.FALLBACK
            e[-1]['modelUsage'] = {m.FALLBACK: {'canonicalModel': m.FALLBACK, 'inputTokens': 1}}
    replace_events(a, e)
    return a


def test_qualified_fallback_retains_original_pair_with_zero_coverage():
    raw, policy, probe = policy_manifest()
    a = policy_attempt(raw, policy, probe)
    before = copy.deepcopy(a)
    result = r.validate_session(raw, [a])
    assert result['status'] == 'APPROVE', result
    assert a == before and result['provider_model'] == m.FALLBACK
    receipt = result['attempts'][0]
    assert receipt['reads'] == {'code.py': [[1, 2]]}
    assert receipt['assistant_models'] == [m.REQUESTED, m.FALLBACK]
    assert receipt['denials'][0]['kind'] == 'NATIVE_UNEXECUTED_RETRACTED_GLOB'
    assert receipt['model_policy']['unexecuted_retracted'][0]['coverage'] == []


def test_raw_predecessors_establish_continuation_not_caller_model():
    raw, policy, probe = policy_manifest()
    first = policy_attempt(raw, policy, probe, status='IN_PROGRESS', start=1, count=1)
    prior = r.parse_attempt(raw, first)
    assert prior['status'] == 'IN_PROGRESS', prior
    second = policy_attempt(raw, policy, probe, use_fallback=False, continued=True,
                            number=2, previous=prior, start=2, count=1)
    result = r.validate_session(raw, [first, second])
    assert result['status'] == 'APPROVE', result
    assert result['provider_model'] == m.FALLBACK
    assert result['attempts'][1]['assistant_models'] == [m.FALLBACK]
    assert r.parse_attempt(raw, second)['status'] == 'RECONCILIATION_REQUIRED'
    assert r.parse_attempt(raw, second, prior_attempts=[first])['status'] == 'APPROVE'
    altered = copy.deepcopy(first)
    e = events(altered); e[-1]['modelUsage']['unknown'] = {}; replace_events(altered, e)
    with pytest.raises(ValueError):
        r.parse_attempt(raw, second, prior_attempts=[altered])


@pytest.mark.parametrize('change', ['model_reset', 'repeat_fallback', 'changed_previous_hash', 'init_opus'])
def test_continuation_mismatch_refuses(change):
    raw, policy, probe = policy_manifest()
    first = policy_attempt(raw, policy, probe, status='IN_PROGRESS')
    prior = r.parse_attempt(raw, first)
    second = policy_attempt(raw, policy, probe, use_fallback=change == 'repeat_fallback',
                            continued=change != 'model_reset', number=2, previous=prior)
    e = events(second)
    if change == 'init_opus': e[0]['model'] = m.FALLBACK
    replace_events(second, e)
    if change == 'changed_previous_hash':
        q = json.loads(second['request']); q['previous_receipt_sha256'] = '0'*64
        second['request'] = r.encoded(q)
    assert r.validate_session(raw, [first, second])['status'] == 'RECONCILIATION_REQUIRED'


@pytest.mark.parametrize('marker', [None, 'unknown', 1])
def test_explicit_invalid_marker_refuses(marker):
    raw, _ = fixture_manifest(); value = json.loads(raw); value['model_policy_version'] = marker
    with pytest.raises(ValueError): r.validate_manifest(r.encoded(value))


def test_old_probe_cannot_authorize_new_policy():
    raw, policy, probe = policy_manifest()
    value = json.loads(raw); value['permission_probe_sha256'] = r.digest(fixture_probe())
    raw = r.encoded(value)
    a = policy_attempt(raw, policy, fixture_probe())
    assert r.parse_attempt(raw, a)['reason'] == 'PERMISSION_PROBE_MODEL_POLICY'


def test_legacy_receipt_and_session_shapes_remain_unchanged():
    raw, policy = fixture_manifest(); a = fixture_attempt(raw, policy)
    result = r.validate_session(raw, [a])
    assert result['status'] == 'APPROVE'
    assert 'provider_model' not in result
    assert 'model_policy_version' not in result['attempts'][0]
    assert 'requested_model' not in result['attempts'][0]
    bad = copy.deepcopy(a); replace_events(bad, fallback(events(bad)))
    assert r.validate_session(raw, [bad])['status'] == 'RECONCILIATION_REQUIRED'


def test_current_policy_timeout_and_conflicting_journal_never_qualify():
    raw, policy, probe = policy_manifest()
    a = policy_attempt(raw, policy, probe)
    a['timeout'] = r.encoded({'status': 'RECONCILE_ORIGINAL_PROCESS'})
    assert r.parse_attempt(raw, a)['status'] == 'RECONCILIATION_REQUIRED'
    a = policy_attempt(raw, policy, probe)
    row = {'observation_original': json.dumps({'tool_use_id': 'synthetic-unexecuted-glob'}),
           'hook_input_original': '{}'}
    a['journal'].append(r.encoded(row))
    assert r.parse_attempt(raw, a)['status'] == 'RECONCILIATION_REQUIRED'


def prospective_canary(tmp_path, monkeypatch):
    from orchestrator import inspection_canary as c, inspection_runtime as runtime
    from test_inspection_canary import fixture, events as canary_events, save_events
    from inspection_confinement_fixtures import readback, FIXTURE_PROFILE, FIXTURE_PROFILE_SHA
    monkeypatch.setattr(runtime, 'PROFILE_SHA256', FIXTURE_PROFILE_SHA)
    monkeypatch.setattr(runtime, 'PROFILE_BYTES', len(FIXTURE_PROFILE))
    bundle, expected = fixture(tmp_path)
    expected['model_policy_version'] = m.VERSION
    expected['execution']['files']['claude']['sha256'] = m.CLI_SHA256
    expected['runtime_sha256'] = c.digest(c.encoded(expected['execution']))
    for phase, raw in bundle.items():
        execution = json.loads(raw['execution.json'])
        execution['files']['claude']['sha256'] = m.CLI_SHA256
        raw['execution.json'] = c.encoded(execution)
        raw['confinement-readback.json'] = c.encoded(readback(
            execution, expected['source'], expected['phases'][phase]['session_id']))
        intent = json.loads(raw['intent.json'])
        for key in ('execution', 'confinement-readback'):
            intent[key+'_sha256'] = c.digest(raw[key+'.json'])
        raw['intent.json'] = c.encoded(intent)
        e = canary_events(raw)
        save_events(raw, fallback(e) if phase == 'hooks' else identify(e))
    return bundle, expected


def test_prospective_canary_preserves_fifth_call_but_qualifies_only_four(tmp_path, monkeypatch):
    from orchestrator import inspection_canary as c
    from test_inspection_canary import events as canary_events
    bundle, expected = prospective_canary(tmp_path, monkeypatch)
    originals = copy.deepcopy(bundle)
    proof = c.verify_canary(bundle, expected)
    assert bundle == originals
    assert proof['model_policy_version'] == m.VERSION and proof['status'] == 'PASSED'
    result = proof['phases']['hooks']
    assert result['provider_model'] == m.FALLBACK and len(result['tool_use_ids']) == 4
    assert len(result['outside_tool_use_ids']) == 3
    assert result['model_policy']['unexecuted_retracted'][0]['coverage'] == []
    calls = [item for event in canary_events(bundle['hooks'])
             for item in event.get('message', {}).get('content', []) if item.get('type') == 'tool_use']
    assert len(calls) == 5 and len(bundle['hooks']['journal']) == 5
    assert result['original_sha256']['protocol.jsonl'] == c.digest(bundle['hooks']['protocol.jsonl'])


@pytest.mark.parametrize('change', ['unmarked', 'unknown_marker', 'reorder', 'extra_call', 'altered_error', 'hook_conflict'])
def test_prospective_canary_cannot_filter_unproved_activity(tmp_path, monkeypatch, change):
    from orchestrator import inspection_canary as c
    from test_inspection_canary import events as canary_events, save_events
    bundle, expected = prospective_canary(tmp_path, monkeypatch)
    raw = bundle['hooks']; e = canary_events(raw)
    if change == 'unmarked': expected.pop('model_policy_version')
    elif change == 'unknown_marker': expected['model_policy_version'] = 'unknown'
    elif change == 'reorder':
        e[4:8] = e[6:8]+e[4:6]
        e[4]['supersedes'] = e[3]['retracted_message_uuids'][:]
        e[6].pop('supersedes', None)
    elif change == 'extra_call':
        extra = copy.deepcopy(e[4:6])
        extra[0].pop('supersedes')
        extra[0]['uuid'] = '99999999-9999-4999-8999-999999999991'
        extra[1]['uuid'] = '99999999-9999-4999-8999-999999999992'
        extra[0]['message']['content'][0]['id'] = 'unproved-extra'
        extra[1]['message']['content'][0]['tool_use_id'] = 'unproved-extra'
        e[-1:-1] = extra
    elif change == 'altered_error': e[2]['tool_use_result'] += '\n'
    elif change == 'hook_conflict':
        raw['journal'].append(r.encoded({
            'observation_original': json.dumps({'tool_use_id': 'synthetic-unexecuted-glob'}),
            'hook_input_original': '{}'}))
    save_events(raw, e)
    with pytest.raises(ValueError): c.verify_canary(bundle, expected)



def test_thinking_only_retraction_retains_real_read_coverage_and_exact_originals():
    from test_inspection_model_policy import thinking_fallback
    raw, policy, probe = policy_manifest()
    a = policy_attempt(raw, policy, probe, use_fallback=False)
    replace_events(a, thinking_fallback(events(a)))
    original = copy.deepcopy(a)
    result = r.validate_session(raw, [a])
    assert result['status'] == 'APPROVE', result
    assert a == original and result['reads'] == {'code.py': [[1, 2]]}
    receipt = result['attempts'][0]
    assert receipt['model_policy']['unexecuted_retracted'] == [] and receipt['denials'] == []
    assert receipt['model_policy']['retracted_events'][0]['event']['message']['content'][0]['type'] == 'thinking'


@pytest.mark.parametrize('missing_journal', [False, True])
def test_executed_retracted_read_keeps_ordinary_hook_and_coverage_checks(missing_journal):
    from test_inspection_model_policy import executed_fallback
    raw, policy, probe = policy_manifest()
    a = policy_attempt(raw, policy, probe, use_fallback=False)
    replace_events(a, executed_fallback(events(a)))
    if missing_journal: a['journal'].pop()
    result = r.validate_session(raw, [a])
    if missing_journal:
        assert result['status'] == 'RECONCILIATION_REQUIRED'
        assert 'MISSING_ALLOWED_TOOL_HOOK_OR_RESULT' in result['attempts'][0]['reason']
    else:
        assert result['status'] == 'APPROVE', result
        receipt = result['attempts'][0]
        assert receipt['model_policy']['unexecuted_retracted'] == []
        assert len(receipt['model_policy']['retracted_events']) == 2
        assert receipt['reads'] == {'code.py': [[1, 2]]}


@pytest.mark.parametrize('executed', [False, True])
def test_full_canary_non_tool_or_executed_retraction_keeps_all_four_calls(tmp_path, monkeypatch, executed):
    from orchestrator import inspection_canary as c
    from test_inspection_canary import events as canary_events, save_events
    from test_inspection_model_policy import thinking_fallback, executed_fallback
    bundle, expected = prospective_canary(tmp_path, monkeypatch)
    raw = bundle['hooks']; e = canary_events(raw)
    # Remove the earlier synthetic Glob exemption to construct a separate fresh fixture.
    del e[1:4]
    for item in e:
        if item.get('type') == 'assistant':
            item['message']['model'] = m.REQUESTED; item.pop('supersedes', None)
    e[-1]['modelUsage'] = {m.REQUESTED: {'canonicalModel': m.REQUESTED}}
    e = executed_fallback(e) if executed else thinking_fallback(e)
    save_events(raw, e)
    result = c.verify_canary(bundle, expected)['phases']['hooks']
    assert len(result['tool_use_ids']) == 4 and len(raw['journal']) == 5
    assert result['model_policy']['unexecuted_retracted'] == []
    assert result['provider_model'] == m.FALLBACK


def test_executed_retracted_extra_call_is_not_removed_from_canary_count(tmp_path, monkeypatch):
    from orchestrator import inspection_canary as c
    from test_inspection_canary import events as canary_events, save_events
    from test_inspection_model_policy import executed_fallback
    bundle, expected = prospective_canary(tmp_path, monkeypatch)
    raw = bundle['hooks']; e = canary_events(raw); del e[1:4]
    for item in e:
        if item.get('type') == 'assistant':
            item['message']['model'] = m.REQUESTED; item.pop('supersedes', None)
    # A fifth executed read cannot disappear just because its pair is retracted.
    extra = copy.deepcopy(e[-3:-1])
    extra[0]['message']['content'][0]['id'] = 'synthetic-extra-executed'
    extra[1]['message']['content'][0]['tool_use_id'] = 'synthetic-extra-executed'
    e[1:1] = extra
    save_events(raw, executed_fallback(e))
    with pytest.raises(ValueError, match='CANARY_EXPECTED_COMPLETED_TOOLS'):
        c.verify_canary(bundle, expected)
