"""Offline synthetic originals exercise the real legacy validator, never a provider."""
import copy
import json

import pytest
from orchestrator import deployment_review as legacy, review_input_codec as codec
from orchestrator import inspection_bootstrap as bootstrap

SOURCE = 'a' * 40
SESSION = 'synthetic-bootstrap-session'


def inputs():
    files = {name: b'# Offline synthetic source original.\n'
             for name in bootstrap.MANDATORY_SOURCE}
    direction = b'Synthetic independent reviewer policy.\n'
    files['docs/test-direction.md'] = direction
    policy = {'direction_path': 'docs/test-direction.md',
              'direction_sha256': legacy.digest(direction)}
    files['configs/test-authority.json'] = legacy.encoded(policy)
    binding = {'path': 'configs/test-authority.json',
               'sha256': legacy.digest(files['configs/test-authority.json']),
               'version': 'synthetic-only-v1'}
    operating = {'authority_policy': binding,
                 'documents': {'docs/test-direction.md': legacy.digest(direction)},
                 'roles': {'claude': 'Synthetic independent reviewer'}}
    files['configs/scientific-operating-context.json'] = legacy.encoded(operating)
    context = {'family': 'claude', 'role': operating['roles']['claude'],
               'recorded_changes': [], 'shared_policy': {
                   'binding': binding, 'policy': policy, 'direction': direction.decode(),
                   'operating_context': {'manifest': operating,
                       'manifest_sha256': legacy.digest(files['configs/scientific-operating-context.json']),
                       'documents': {'docs/test-direction.md': {
                           'sha256': legacy.digest(direction), 'text': direction.decode()}}}}}
    return files, codec.context_original(context)


def originals(files, context, *, scope=bootstrap.SCOPE, source=SOURCE,
              verdict='APPROVE', models=None, tools=None, runner=None,
              supplements=None):
    # All fields are openly synthetic. No permissive stub replaces old validation.
    text = {name: raw.decode() for name, raw in files.items()}
    supplements = supplements or {}
    prompt = codec.encode(scope, source, text, supplements, [], context)
    request = {'scope': scope, 'reviewed_commit': source, 'prompt': prompt,
               'input_presentation': codec.FORMAT,
               'shared_context_sha256': legacy.digest(context) if context else None,
               'input_file_sha256': {name: legacy.digest(raw) for name, raw in files.items()},
               'private_evidence_sha256': {name: row['sha256'] for name, row in supplements.items()},
               'runner_sha256': runner or legacy.digest(files['scripts/pilot_review.py']),
               'change_context_sha256': legacy.digest(json.dumps([], sort_keys=True).encode())}
    response = {'type': 'result', 'subtype': 'success', 'is_error': False,
                'session_id': SESSION, 'structured_output': {
                    'scope': scope, 'reviewed_commit': source, 'verdict': verdict,
                    'findings': ['Offline synthetic original fixture, not actual approval.']}}
    models = models or [legacy.MODEL]
    events = [{'type': 'system', 'subtype': 'init', 'session_id': SESSION,
               'tools': tools or ['StructuredOutput'], 'mcp_servers': [],
               'permissionMode': 'dontAsk'},
              *[{'type': 'assistant', 'session_id': SESSION,
                 'message': {'model': model}} for model in models], response]
    raw = {'request.json': legacy.encoded(request), 'response.json': legacy.encoded(response),
           'protocol.jsonl': b''.join(json.dumps(row).encode()+b'\n' for row in events)}
    execution = {'reviewed_commit': source, 'returncode': 0, 'requested_model': legacy.MODEL,
                 'assistant_message_models': sorted(models),
                 'request_sha256': legacy.digest(raw['request.json']),
                 'response_sha256': legacy.digest(raw['response.json']),
                 'protocol_sha256': legacy.digest(raw['protocol.jsonl']),
                 'prompt_sha256': legacy.digest(prompt.encode()),
                 'input_file_sha256': request['input_file_sha256']}
    raw.update({'execution.json': legacy.encoded(execution),
                'intent.json': legacy.encoded({'reviewed_commit': source,
                    'request_sha256': execution['request_sha256'],
                    'maximum_invocations': 1, 'automatic_retry': False}),
                'returned.json': legacy.encoded({'returncode': 0})})
    return raw


def test_returns_ordinary_legacy_review_for_exact_source():
    files, context = inputs()
    files['tests/explicit-extra-enabler-check.py'] = b'# Additional required original.\n'
    raw = originals(files, context)
    result = bootstrap.validate_bootstrap(raw, SOURCE, files)
    assert result == legacy._review_originals(raw, SOURCE, {bootstrap.SCOPE})
    assert result['source_text']['tests/explicit-extra-enabler-check.py'].encode() == files['tests/explicit-extra-enabler-check.py']


@pytest.mark.parametrize('name', sorted(bootstrap.MANDATORY_SOURCE))
def test_caller_cannot_drop_fixed_mandatory_dependency(name):
    files, context = inputs()
    raw = originals(files, context)
    files.pop(name)
    with pytest.raises(ValueError, match='MANDATORY_SOURCE_REQUIRED'):
        bootstrap.validate_bootstrap(raw, SOURCE, files)


@pytest.mark.parametrize('change', ['changed', 'omitted', 'private-only'])
def test_bootstrap_module_must_be_exact_named_literal(change):
    expected, context = inputs()
    supplied = dict(expected)
    name = 'orchestrator/inspection_runner.py'
    private = {}
    if change == 'changed':
        supplied[name] = b'# Different source, consistent synthetic metadata.\n'
    else:
        raw = supplied.pop(name)
        if change == 'private-only':
            private['indexed-in-private'] = {'sha256': legacy.digest(raw), 'content': raw.decode()}
    with pytest.raises(ValueError, match='SOURCE_BYTES_CHANGED'):
        bootstrap.validate_bootstrap(originals(supplied, context, supplements=private), SOURCE, expected)


@pytest.mark.parametrize('kwargs,reason', [
    ({'scope': 'material-deployment'}, 'EXACT_APPROVING_REVIEW_REQUIRED'),
    ({'scope': 'direct-inspection-review'}, 'EXACT_APPROVING_REVIEW_REQUIRED'),
    ({'verdict': 'REQUEST_CHANGES'}, 'EXACT_APPROVING_REVIEW_REQUIRED'),
    ({'models': ['claude-opus-4-8']}, 'ORIGINAL_CLAUDE_PROTOCOL_REQUIRED'),
    ({'models': ['claude-fable-5', 'claude-opus-4-8']}, 'ORIGINAL_CLAUDE_PROTOCOL_REQUIRED'),
    ({'tools': ['Read', 'StructuredOutput']}, 'ORIGINAL_CLAUDE_PROTOCOL_REQUIRED'),
    ({'runner': 'f' * 64}, 'ACTUAL_COURIER_SOURCE_REQUIRED'),
])
def test_does_not_accept_new_profile_negative_or_different_courier(kwargs, reason):
    files, context = inputs()
    with pytest.raises(ValueError, match=reason):
        bootstrap.validate_bootstrap(originals(files, context, **kwargs), SOURCE, files)


def test_does_not_rebind_bootstrap_to_later_candidate():
    files, context = inputs()
    with pytest.raises(ValueError, match='EXACT_APPROVING_REVIEW_REQUIRED'):
        bootstrap.validate_bootstrap(originals(files, context), 'b' * 40, files)


def test_requires_actual_shared_context():
    files, _ = inputs()
    with pytest.raises(ValueError, match='SHARED_CONTEXT_REQUIRED'):
        bootstrap.validate_bootstrap(originals(files, None), SOURCE, files)


@pytest.mark.parametrize('name', ['configs/test-authority.json', 'docs/test-direction.md'])
def test_policy_closure_missing_or_changed(name):
    files, context = inputs()
    raw = originals(files, context)
    for mutation in ('missing', 'changed'):
        expected = dict(files)
        if mutation == 'missing': expected.pop(name)
        else: expected[name] += b'Changed policy bytes.'
        with pytest.raises(ValueError, match='POLICY_CHANGED'):
            bootstrap.validate_bootstrap(raw, SOURCE, expected)


@pytest.mark.parametrize('name', legacy.ORIGINAL_NAMES)
def test_requires_complete_original_six_files(name):
    files, context = inputs()
    raw = originals(files, context)
    raw.pop(name)
    with pytest.raises(ValueError, match='ORIGINALS_REQUIRED'):
        bootstrap.validate_bootstrap(raw, SOURCE, files)


def test_original_response_and_protocol_must_remain_identical():
    files, context = inputs()
    raw = originals(files, context)
    response = json.loads(raw['response.json'])
    response['structured_output']['findings'] = ['Different original']
    raw['response.json'] = legacy.encoded(response)
    with pytest.raises(ValueError, match='ORIGINAL_CLAUDE_PROTOCOL_REQUIRED'):
        bootstrap.validate_bootstrap(raw, SOURCE, files)


def test_prospective_guard_keeps_complete_historical_receipts_readable():
    files, context = inputs()
    raw = originals(files, context)
    before = dict(raw)
    assert bootstrap.validate_bootstrap(raw, SOURCE, files)['source_text']
    with pytest.raises(ValueError, match='REVIEW_PROSPECTIVE_V2_REQUIRED'):
        bootstrap.require_v2_review(raw)
    assert raw == before
    assert bootstrap.validate_bootstrap(raw, SOURCE, files)['source_text']
