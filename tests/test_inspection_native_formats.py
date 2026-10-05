"""Native-format compatibility is not a new assistant or arbitrary-error permission."""
import copy
import pytest
from orchestrator import inspection_canary as c, inspection_review as r
from orchestrator import inspection_runtime as runtime
from test_inspection_canary import fixture, events, save_events
from test_inspection_review import fixture_manifest, fixture_attempt, replace_events
from inspection_confinement_fixtures import FIXTURE_PROFILE, FIXTURE_PROFILE_SHA

MESSAGE = 'File is in a directory that is denied by your permission settings.'


def native_baseline(raw):
    e = events(raw)
    e[-1]['modelUsage'][r.AUXILIARY_USAGE] = {'canonicalModel': 'claude-haiku-4-5',
        'inputTokens': 754, 'outputTokens': 14, 'provider': 'firstParty'}
    read = next(item for row in e for item in row.get('message', {}).get('content', [])
        if item.get('type') == 'tool_use' and item.get('input') == {'file_path': '/state/canary/probe.txt'})
    key = read['id']
    e[-1]['permission_denials'] = [row for row in e[-1]['permission_denials'] if row['tool_use_id'] != key]
    for row in e:
        for item in row.get('message', {}).get('content', []):
            if item.get('type') == 'tool_result' and item.get('tool_use_id') == key:
                item['content'] = '<tool_use_error>'+MESSAGE+'</tool_use_error>'
                row['tool_use_result'] = 'Error: '+MESSAGE
    return e, key


@pytest.fixture(autouse=True)
def synthetic_profile(monkeypatch):
    monkeypatch.setattr(runtime, 'PROFILE_SHA256', FIXTURE_PROFILE_SHA)
    monkeypatch.setattr(runtime, 'PROFILE_BYTES', len(FIXTURE_PROFILE))
    # Synthetic runtime fixtures retain their synthetic binary identity.
    monkeypatch.setattr(c, 'READ_VALIDATION_DENIAL_CLI_SHA256', r.digest(b'claude'))
    monkeypatch.setattr(r, 'READ_VALIDATION_DENIAL_CLI_SHA256', r.digest(b'claude'))


def test_known_auxiliary_canonical_pair_preserves_formal_review():
    manifest, policy = fixture_manifest(); attempt = fixture_attempt(manifest, policy)
    e = events(attempt) if 'protocol.jsonl' in attempt else [r._json(x) for x in attempt['protocol'].splitlines()]
    e[-1]['modelUsage'][r.AUXILIARY_USAGE] = {'canonicalModel': 'claude-haiku-4-5', 'inputTokens': 754, 'outputTokens': 14}
    replace_events(attempt, e)
    result = r.validate_session(manifest, [attempt])
    assert result['status'] == 'APPROVE'
    assert result['attempts'][0]['usage_models'][r.AUXILIARY_USAGE]['canonicalModel'] == 'claude-haiku-4-5'


@pytest.mark.parametrize('canonical', [None, r.AUXILIARY_USAGE, 'claude-haiku-4-5'])
def test_only_known_auxiliary_pairs(canonical):
    row = {} if canonical is None else {'canonicalModel': canonical}
    assert r.usage_identity_matches({r.MODEL: {}, r.AUXILIARY_USAGE: row})


@pytest.mark.parametrize('usage', [None, [], {}, {r.AUXILIARY_USAGE: {}},
    {r.MODEL: {}, 'claude-haiku-4-5': {}}, {r.MODEL: {}, 'unknown': {}},
    {r.MODEL: {'canonicalModel': 'claude-opus-5'}},
    {r.MODEL: {}, r.AUXILIARY_USAGE: {'canonicalModel': r.MODEL}},
    {r.MODEL: {}, r.AUXILIARY_USAGE: {'canonicalModel': 'claude-haiku-3-5'}},
    {r.MODEL: {}, r.AUXILIARY_USAGE: None}])
def test_unknown_usage_or_alias_refuses(usage):
    assert not r.usage_identity_matches(usage)


def test_exact_read_validation_denial_without_terminal_row(tmp_path):
    bundle, expected = fixture(tmp_path)
    e, key = native_baseline(bundle['baseline']); save_events(bundle['baseline'], e)
    result = c.verify_canary(bundle, expected)
    assert result['status'] == 'PASSED' and result['approval_authority'] is False
    assert result['phases']['baseline']['model_usage'][r.AUXILIARY_USAGE]['canonicalModel'] == 'claude-haiku-4-5'
    assert key in result['phases']['baseline']['outside_tool_use_ids']


@pytest.mark.parametrize('mutation', ['generic-error','wrong-paired-output','missing-output','not-error',
    'foreign-path','inside-path','foreign-id','denied-row-extra','denied-row-duplicate',
    'denied-row-missing-glob','denied-row-missing-grep','denied-row-wrong-tool',
    'denied-row-wrong-input','foreign-assistant','fallback','unknown-usage-alias'])
def test_partial_denial_and_identity_ambiguity_refuse(tmp_path, mutation):
    bundle, expected = fixture(tmp_path); e, key = native_baseline(bundle['baseline'])
    read_result_event = next(row for row in e if any(item.get('type') == 'tool_result' and
        item.get('tool_use_id') == key for item in row.get('message', {}).get('content', [])))
    read_result = next(item for item in read_result_event['message']['content'] if item.get('tool_use_id') == key)
    read_use = next(item for row in e for item in row.get('message', {}).get('content', []) if item.get('id') == key)
    denials = e[-1]['permission_denials']
    if mutation == 'generic-error': read_result['content'] = '<tool_use_error>File not found</tool_use_error>'
    elif mutation == 'wrong-paired-output': read_result_event['tool_use_result'] = 'Error: File not found'
    elif mutation == 'missing-output': read_result_event.pop('tool_use_result')
    elif mutation == 'not-error': read_result['is_error'] = False
    elif mutation == 'foreign-path': read_use['input'] = {'file_path': '/state/private.txt'}
    elif mutation == 'inside-path': read_use['input'] = {'file_path': '/review/CANARY.txt'}
    elif mutation == 'foreign-id': read_result['tool_use_id'] = 'unknown'
    elif mutation == 'denied-row-extra': denials.append({'tool_name':'Read','tool_use_id':'unknown','tool_input':{}})
    elif mutation == 'denied-row-duplicate': denials.append(copy.deepcopy(denials[0]))
    elif mutation.startswith('denied-row-missing-'):
        wanted = 'Glob' if mutation.endswith('glob') else 'Grep'
        e[-1]['permission_denials'] = [row for row in denials if row['tool_name'] != wanted]
    elif mutation == 'denied-row-wrong-tool': denials[0]['tool_name'] = 'Read'
    elif mutation == 'denied-row-wrong-input': denials[0]['tool_input']['path'] = '/unrelated'
    elif mutation == 'foreign-assistant': next(row for row in e if row.get('type') == 'assistant')['message']['model'] = r.AUXILIARY_USAGE
    elif mutation == 'fallback': e.insert(-1, {'type':'system','subtype':'model_refusal_fallback','session_id':e[0]['session_id']})
    elif mutation == 'unknown-usage-alias': e[-1]['modelUsage'][r.AUXILIARY_USAGE]['canonicalModel'] = 'claude-opus-5'
    save_events(bundle['baseline'], e)
    with pytest.raises((ValueError, KeyError, StopIteration)): c.verify_canary(bundle, expected)


def test_formal_review_assistant_identity_not_relaxed():
    manifest, policy = fixture_manifest(); attempt = fixture_attempt(manifest, policy)
    e = [r._json(x) for x in attempt['protocol'].splitlines()]
    e[-1]['modelUsage'][r.AUXILIARY_USAGE] = {'canonicalModel':'claude-haiku-4-5'}
    next(row for row in e if row.get('type') == 'assistant')['message']['model'] = r.AUXILIARY_USAGE
    replace_events(attempt, e)
    assert r.validate_session(manifest, [attempt])['status'] == 'RECONCILIATION_REQUIRED'


def test_unknown_cli_cannot_use_missing_read_denial_row(tmp_path, monkeypatch):
    bundle, expected = fixture(tmp_path)
    e, _ = native_baseline(bundle['baseline']); save_events(bundle['baseline'], e)
    monkeypatch.setattr(c, 'READ_VALIDATION_DENIAL_CLI_SHA256', '0'*64)
    with pytest.raises(ValueError, match='CANARY_NATIVE_DENIAL_ORIGINALS'):
        c.verify_canary(bundle, expected)


def test_existing_complete_terminal_denials_do_not_need_new_cli_alias(tmp_path, monkeypatch):
    bundle, expected = fixture(tmp_path)
    monkeypatch.setattr(c, 'READ_VALIDATION_DENIAL_CLI_SHA256', '0'*64)
    assert c.verify_canary(bundle, expected)['status'] == 'PASSED'
