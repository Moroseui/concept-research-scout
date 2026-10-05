"""Synthetic direct-profile contracts; no fixture is provider or canary evidence."""
import copy
import json
import pytest
from orchestrator import inspection_model_policy as model
from orchestrator import inspection_review as review
from orchestrator import inspection_access as access
from orchestrator import inspection_canary as canary
from orchestrator import inspection_deployment as deployment
from orchestrator import deployment_review as legacy
from test_inspection_review import fixture_manifest, fixture_probe, fixture_attempt, events, replace_events
from test_inspection_model_policy import SESSION, identify, plain, fallback


def direct_events(value=None):
    value = identify(copy.deepcopy(value if value is not None else plain()))
    value[0]['model'] = model.FALLBACK
    for event in value:
        if event.get('type') == 'assistant':
            event['message']['model'] = model.FALLBACK
    value[-1]['modelUsage'] = {model.FALLBACK: {'canonicalModel': model.FALLBACK, 'inputTokens': 1}}
    return value


def analyze(value, **kwargs):
    return model.analyze(value, session_id=SESSION, runtime_cli_sha256=model.CLI_SHA256,
                         policy_version=model.DIRECT_VERSION, **kwargs)


def direct_manifest():
    raw, policy = fixture_manifest()
    manifest = json.loads(raw); probe = json.loads(fixture_probe())
    probe.update(model_policy_version=model.DIRECT_VERSION, runtime_cli_sha256=model.CLI_SHA256)
    probe_raw = review.encoded(probe)
    manifest.update(model_policy_version=model.DIRECT_VERSION, permission_probe_sha256=review.digest(probe_raw))
    return review.encoded(manifest), policy, probe_raw


def direct_attempt(raw, policy, probe, **kwargs):
    attempt = fixture_attempt(raw, policy, **kwargs)
    attempt['permission_probe'] = probe
    replace_events(attempt, direct_events(events(attempt)))
    return attempt


def test_direct_identity_is_exact_and_originals_are_preserved():
    value = direct_events(); before = copy.deepcopy(value)
    result = analyze(value)
    assert value == before and result['policy_version'] == model.DIRECT_VERSION
    assert result['requested_model'] == result['provider_model'] == 'claude-opus-4-8'
    assert result['assistant_models'] == ['claude-opus-4-8']
    assert result['usage_models'] == value[-1]['modelUsage']
    assert result['fallback_events'] == result['retracted_events'] == result['unexecuted_retracted'] == []


@pytest.mark.parametrize('canonical', ['claude-haiku-4-5-20251001', 'claude-haiku-4-5', None])
def test_only_existing_dated_auxiliary_semantics_are_accepted(canonical):
    value = direct_events()
    value[-1]['modelUsage'][model.AUXILIARY] = {} if canonical is None else {'canonicalModel': canonical}
    assert analyze(value)['provider_model'] == model.FALLBACK


@pytest.mark.parametrize('change', [
    'init_fable', 'init_opus5', 'assistant_fable', 'assistant_opus5', 'mixed_assistants',
    'usage_fable', 'usage_opus5', 'usage_unknown', 'undated_auxiliary_key',
    'auxiliary_wrong_canonical', 'wrong_canonical', 'missing_primary_usage', 'terminal_error'])
def test_every_direct_identity_layer_and_terminal_must_match(change):
    value = direct_events()
    if change.startswith('init_'):
        value[0]['model'] = model.REQUESTED if change == 'init_fable' else 'claude-opus-5'
    elif change.startswith('assistant_'):
        value[1]['message']['model'] = model.REQUESTED if change == 'assistant_fable' else 'claude-opus-5'
    elif change == 'mixed_assistants':
        extra = copy.deepcopy(value[1]); extra['message']['model'] = model.REQUESTED
        value.insert(1, extra); identify(value)
    elif change.startswith('usage_'):
        key = {'usage_fable': model.REQUESTED, 'usage_opus5': 'claude-opus-5',
               'usage_unknown': 'unknown-reviewer'}[change]
        value[-1]['modelUsage'][key] = {'canonicalModel': key}
    elif change == 'undated_auxiliary_key': value[-1]['modelUsage']['claude-haiku-4-5'] = {}
    elif change == 'auxiliary_wrong_canonical':
        value[-1]['modelUsage'][model.AUXILIARY] = {'canonicalModel': model.FALLBACK}
    elif change == 'wrong_canonical':
        value[-1]['modelUsage'][model.FALLBACK]['canonicalModel'] = 'claude-opus-5'
    elif change == 'missing_primary_usage': value[-1]['modelUsage'] = {model.AUXILIARY: {}}
    elif change == 'terminal_error': value[-1]['is_error'] = True
    with pytest.raises(ValueError): analyze(value)


@pytest.mark.parametrize('activity', [
    'system_fallback', 'inline_fallback', 'model_fallback', 'retraction_empty',
    'retraction_nonempty', 'supersedes_empty', 'nested_supersedes', 'tombstone',
    'raw_validation_error', 'rendered_validation_error', 'content_list_validation_error'])
def test_direct_profile_never_uses_a_fallback_or_schema_error_exclusion(activity):
    value = direct_events()
    if activity in ('system_fallback', 'model_fallback'):
        value.insert(1, {'type': 'system', 'subtype':
            'model_refusal_fallback' if activity == 'system_fallback' else 'model_fallback'})
    elif activity == 'inline_fallback':
        value[1]['message']['content'].append({'type': 'fallback',
            'from': {'model': model.REQUESTED}, 'to': {'model': model.FALLBACK}})
    elif activity.startswith('retraction_'):
        value[1]['retracted_message_uuids'] = [] if activity == 'retraction_empty' else [value[1]['uuid']]
    elif activity == 'supersedes_empty': value[1]['supersedes'] = []
    elif activity == 'nested_supersedes': value[1]['message']['supersedes'] = []
    elif activity == 'tombstone':
        value.insert(1, {'type': 'tombstone', 'message': copy.deepcopy(value[1])})
    else:
        result = {'type': 'user', 'message': {'content': [{'type': 'tool_result',
            'tool_use_id': 'synthetic-refused', 'is_error': True, 'content': 'synthetic error'}]}}
        error = 'InputValidationError: Grep failed: missing required pattern'
        if activity == 'raw_validation_error': result['tool_use_result'] = error
        elif activity == 'content_list_validation_error':
            result['message']['content'][0]['content'] = [{'type': 'text', 'text': error}]
        else:
            result['message']['content'][0]['content'] = '<tool_use_error>'+error+'</tool_use_error>'
        value.insert(-1, result)
    identify(value)
    with pytest.raises(ValueError): analyze(value)


def test_reviewing_literal_source_about_fallback_does_not_count_as_fallback_activity():
    value = direct_events()
    quoted = '{"type":"fallback","supersedes":[],"error":"InputValidationError"}'
    value[1]['message']['content'][0]['text'] = 'Reviewing literal source: '+quoted
    value.insert(-1, {'type': 'user', 'message': {'content': [{'type': 'tool_result',
        'tool_use_id': 'synthetic-read', 'is_error': False, 'content': quoted}]}})
    identify(value)
    assert analyze(value)['provider_model'] == model.FALLBACK


@pytest.mark.parametrize('version', ['direct-inspection-opus-4-8/v0', 'unknown', 1])
def test_unknown_profile_has_no_model_selection_fallback(version):
    with pytest.raises(ValueError): model.requested_model(version)


def test_changed_cli_invalidates_the_direct_profile():
    with pytest.raises(ValueError):
        model.analyze(direct_events(), session_id=SESSION, runtime_cli_sha256='0'*64,
                      policy_version=model.DIRECT_VERSION)


def test_unmarked_and_existing_v2_behavior_do_not_inherit_direct_opus():
    assert review.MODEL == legacy.MODEL == model.REQUESTED == 'claude-fable-5'
    assert model.VERSION == 'direct-inspection-cyber-fallback/v2'
    assert model.CURRENT_VERSION == model.DIRECT_VERSION == 'direct-inspection-opus-4-8/v1'
    assert model.requested_model(None) == model.requested_model(model.VERSION) == review.MODEL
    old = model.analyze(fallback(), session_id=SESSION, runtime_cli_sha256=model.CLI_SHA256)
    assert old['policy_version'] == model.VERSION and old['unexecuted_retracted']
    with pytest.raises(ValueError): model.version('direct-inspection-cyber-fallback/v1')
    raw, policy = fixture_manifest(); old_attempt = fixture_attempt(raw, policy)
    result = review.validate_session(raw, [old_attempt])
    assert result['status'] == 'APPROVE' and 'model_policy_version' not in result
    replace_events(old_attempt, direct_events(events(old_attempt)))
    assert review.validate_session(raw, [old_attempt])['status'] == 'RECONCILIATION_REQUIRED'


def test_direct_profile_preserves_real_read_coverage_and_receipt_identity():
    raw, policy, probe = direct_manifest(); attempt = direct_attempt(raw, policy, probe)
    before = copy.deepcopy(attempt); result = review.validate_session(raw, [attempt])
    assert result['status'] == 'APPROVE', result
    assert attempt == before and result['reads'] == {'code.py': [[1, 2]]}
    assert result['requested_model'] == result['provider_model'] == model.FALLBACK
    assert result['attempts'][0]['assistant_models'] == [model.FALLBACK]
    assert result['attempts'][0]['denials'] == []


def test_fixed_profile_continuation_requires_complete_revalidated_raw_predecessors():
    raw, policy, probe = direct_manifest()
    first = direct_attempt(raw, policy, probe, status='IN_PROGRESS', start=1, count=1)
    prior = review.parse_attempt(raw, first)
    assert prior['status'] == 'IN_PROGRESS', prior
    second = direct_attempt(raw, policy, probe, number=2, previous=prior, start=2, count=1)
    result = review.validate_session(raw, [first, second])
    assert result['status'] == 'APPROVE' and result['reads'] == {'code.py': [[1, 1], [2, 2]]}, result
    assert result['provider_model'] == result['requested_model'] == model.FALLBACK
    assert review.parse_attempt(raw, second)['status'] == 'RECONCILIATION_REQUIRED'
    assert review.parse_attempt(raw, second, prior_attempts=[first])['status'] == 'APPROVE'
    altered = copy.deepcopy(first); stream = events(altered)
    stream[-1]['modelUsage']['claude-opus-5'] = {}; replace_events(altered, stream)
    with pytest.raises(ValueError): review.parse_attempt(raw, second, prior_attempts=[altered])


@pytest.mark.parametrize('change', ['profile', 'binary', 'previous_hash', 'second_init'])
def test_direct_continuation_cannot_change_probe_profile_binary_or_predecessor(change):
    raw, policy, probe = direct_manifest()
    first = direct_attempt(raw, policy, probe, status='IN_PROGRESS')
    prior = review.parse_attempt(raw, first)
    second = direct_attempt(raw, policy, probe, number=2, previous=prior)
    if change in ('profile', 'binary'):
        other = json.loads(probe)
        other['model_policy_version' if change == 'profile' else 'runtime_cli_sha256'] = (
            model.VERSION if change == 'profile' else '0'*64)
        second['permission_probe'] = review.encoded(other)
    elif change == 'previous_hash':
        request = json.loads(second['request']); request['previous_receipt_sha256'] = '0'*64
        second['request'] = review.encoded(request)
    else:
        stream = events(second); stream[0]['model'] = model.REQUESTED; replace_events(second, stream)
    assert review.validate_session(raw, [first, second])['status'] == 'RECONCILIATION_REQUIRED'


def test_native_sandbox_command_selection_is_fixed_without_other_capability_changes():
    args = ('/synthetic/view', '/synthetic/state', '/synthetic/runtime', SESSION)
    old = access.sandbox_command(*args)
    direct = access.sandbox_command(*args, model_policy_version=model.DIRECT_VERSION)
    assert old[old.index('--model')+1] == model.REQUESTED
    assert direct[direct.index('--model')+1] == model.FALLBACK
    normalized = direct[:]; normalized[normalized.index('--model')+1] = model.REQUESTED
    assert normalized == old
    resumed = access.sandbox_command(*args, resume=True, model_policy_version=model.DIRECT_VERSION)
    assert resumed[resumed.index('--model')+1] == model.FALLBACK
    assert '--resume' in resumed and '--session-id' not in resumed


@pytest.mark.parametrize('activity', ['fallback_model_field', 'server_fallback_event'])
def test_explicit_fallback_metadata_refuses_without_a_refusal_notice(activity):
    value = direct_events()
    if activity == 'fallback_model_field':
        value[1]['fallback_model'] = model.FALLBACK
    else:
        value.insert(1, {'type': 'server_fallback', 'fromModel': model.REQUESTED,
                         'toModel': model.FALLBACK})
    identify(value)
    with pytest.raises(ValueError): analyze(value)


def direct_canary(tmp_path, monkeypatch, *, cli=None):
    from orchestrator import inspection_runtime as runtime
    from test_inspection_canary import fixture, events as stream, save_events
    from inspection_confinement_fixtures import readback, FIXTURE_PROFILE, FIXTURE_PROFILE_SHA
    monkeypatch.setattr(runtime, 'PROFILE_SHA256', FIXTURE_PROFILE_SHA)
    monkeypatch.setattr(runtime, 'PROFILE_BYTES', len(FIXTURE_PROFILE))
    bundle, expected = fixture(tmp_path)
    cli = model.CLI_SHA256 if cli is None else cli
    expected['model_policy_version'] = model.DIRECT_VERSION
    expected['execution']['files']['claude']['sha256'] = cli
    expected['runtime_sha256'] = canary.digest(canary.encoded(expected['execution']))
    for phase, originals in bundle.items():
        execution = json.loads(originals['execution.json'])
        execution['files']['claude']['sha256'] = cli
        originals['execution.json'] = canary.encoded(execution)
        originals['confinement-readback.json'] = canary.encoded(readback(
            execution, expected['source'], expected['phases'][phase]['session_id']))
        command = json.loads(originals['command.json'])
        command[command.index('--model')+1] = model.FALLBACK
        originals['command.json'] = canary.encoded(command)
        expected['phases'][phase]['command_sha256'] = canary.digest(originals['command.json'])
        intent = json.loads(originals['intent.json'])
        for name in ('command', 'execution', 'confinement-readback'):
            intent[name+'_sha256'] = canary.digest(originals[name+'.json'])
        originals['intent.json'] = canary.encoded(intent)
        save_events(originals, direct_events(stream(originals)))
    return bundle, expected


def test_both_direct_canary_phases_still_require_four_tools_and_original_boundary_proof(tmp_path, monkeypatch):
    bundle, expected = direct_canary(tmp_path, monkeypatch)
    before = copy.deepcopy(bundle)
    proof = canary.verify_canary(bundle, expected)
    assert bundle == before and proof['status'] == 'PASSED'
    assert proof['model_policy_version'] == model.DIRECT_VERSION
    for phase in ('baseline', 'hooks'):
        receipt = proof['phases'][phase]
        assert receipt['requested_model'] == receipt['provider_model'] == model.FALLBACK
        assert len(receipt['tool_use_ids']) == 4 and len(receipt['outside_tool_use_ids']) == 3
        assert receipt['model_policy']['unexecuted_retracted'] == []
    assert len(bundle['hooks']['journal']) == 5


@pytest.mark.parametrize('change', ['command_fable', 'init_fable', 'assistant_fable',
                                   'usage_opus5', 'missing_hook', 'fallback', 'profile'])
def test_direct_canary_rejects_identity_and_boundary_mismatches(tmp_path, monkeypatch, change):
    from test_inspection_canary import events as stream, save_events
    bundle, expected = direct_canary(tmp_path, monkeypatch)
    raw = bundle['hooks']; value = stream(raw)
    if change == 'command_fable':
        command = json.loads(raw['command.json'])
        command[command.index('--model')+1] = model.REQUESTED
        raw['command.json'] = canary.encoded(command)
        expected['phases']['hooks']['command_sha256'] = canary.digest(raw['command.json'])
        intent = json.loads(raw['intent.json'])
        intent['command_sha256'] = canary.digest(raw['command.json'])
        raw['intent.json'] = canary.encoded(intent)
    elif change == 'init_fable': value[0]['model'] = model.REQUESTED
    elif change == 'assistant_fable':
        next(e for e in value if e.get('type') == 'assistant')['message']['model'] = model.REQUESTED
    elif change == 'usage_opus5': value[-1]['modelUsage']['claude-opus-5'] = {}
    elif change == 'missing_hook': raw['journal'].pop()
    elif change == 'fallback':
        value.insert(1, {'type': 'system', 'subtype': 'model_refusal_fallback'})
    elif change == 'profile': expected['model_policy_version'] = model.VERSION
    save_events(raw, identify(value))
    with pytest.raises(ValueError): canary.verify_canary(bundle, expected)


def test_direct_canary_rejects_unknown_binary_even_when_all_synthetic_pins_agree(tmp_path, monkeypatch):
    bundle, expected = direct_canary(tmp_path, monkeypatch, cli='0'*64)
    with pytest.raises(ValueError): canary.verify_canary(bundle, expected)


def direct_material_fixture():
    from test_inspection_deployment import material_fixture
    fixture = material_fixture()
    manifest = json.loads(fixture['manifest_raw'])
    wrapped = fixture['attempts'][0]; originals = wrapped['originals']
    probe = json.loads(originals['permission_probe'])
    probe.update(model_policy_version=model.DIRECT_VERSION, runtime_cli_sha256=model.CLI_SHA256)
    originals['permission_probe'] = review.encoded(probe)
    manifest.update(model_policy_version=model.DIRECT_VERSION,
                    permission_probe_sha256=review.digest(originals['permission_probe']))
    fixture['manifest_raw'] = review.encoded(manifest)
    manifest_sha = review.digest(fixture['manifest_raw'])
    request = json.loads(originals['request']); request['manifest_sha256'] = manifest_sha
    originals['request'] = review.encoded(request)
    intent = json.loads(originals['intent'])
    intent.update(manifest_sha256=manifest_sha, request_sha256=review.digest(originals['request']))
    originals['intent'] = review.encoded(intent)
    value = direct_events(events(originals))
    value[-1]['structured_output']['manifest_sha256'] = manifest_sha
    replace_events(originals, value)
    wrapped['response_raw'] = review.encoded(value[-1])
    execution = json.loads(wrapped['execution_raw'])
    execution.update(manifest_sha256=manifest_sha, requested_model=model.FALLBACK,
        request_sha256=review.digest(originals['request']),
        response_sha256=review.digest(wrapped['response_raw']),
        protocol_sha256=review.digest(originals['protocol']),
        assistant_message_models=[model.FALLBACK], actual_usage_models=[model.FALLBACK])
    wrapped['execution_raw'] = review.encoded(execution)
    return fixture


def test_direct_material_consumer_binds_full_originals_and_actual_final_attribution():
    fixture = direct_material_fixture(); before = copy.deepcopy(fixture)
    result = deployment.validate_deployment_session(**fixture)
    assert fixture == before and result['provider_model'] == model.FALLBACK
    assert result['execution_metadata_projection']['requested_model'] == model.FALLBACK
    assert result['execution_metadata_projection']['assistant_message_models'] == [model.FALLBACK]
    assert set(fixture['required_files']) <= set(result['inspection_session']['reads'])


@pytest.mark.parametrize('field,value', [('requested_model', 'claude-fable-5'),
    ('assistant_message_models', ['claude-fable-5']), ('actual_usage_models', ['claude-opus-5'])])
def test_direct_material_execution_cannot_relabel_protocol_identity(field, value):
    fixture = direct_material_fixture()
    wrapped = fixture['attempts'][0]; execution = json.loads(wrapped['execution_raw'])
    execution[field] = value; wrapped['execution_raw'] = review.encoded(execution)
    with pytest.raises(ValueError): deployment.validate_deployment_session(**fixture)


@pytest.mark.parametrize('field', ['error', 'error_type', 'code'])
def test_native_validation_error_metadata_is_refused(field):
    value = direct_events()
    value[1][field] = 'InputValidationError'
    with pytest.raises(ValueError): analyze(value)


def test_mixed_profile_metadata_does_not_inherit_the_direct_marker():
    value = direct_events()
    value[1]['model_policy_version'] = model.VERSION
    with pytest.raises(ValueError): analyze(value)


def _runtime_manifest(case, number):
    manifest, schema, target = case.manifest_and_attempt(number)
    manifest['model_policy_version'] = model.DIRECT_VERSION
    raw = access.encoded(manifest)
    (case.session/'manifest.json').write_bytes(raw)
    request = json.loads((target/'request.json').read_bytes())
    request['manifest_sha256'] = access.digest(raw)
    (target/'request.json').write_bytes(access.encoded(request))
    schema['properties']['manifest_sha256'] = {'const': access.digest(raw)}
    return manifest, schema, target


def test_runtime_renderer_propagates_manifest_profile_to_first_and_resumed_commands(monkeypatch):
    import test_inspection_runtime as fixtures
    case = fixtures.RuntimeTests()
    case.setUp()
    try:
        # Only the binary pin is a synthetic substitute; no provider executable is run.
        monkeypatch.setattr(model, 'CLI_SHA256', case.execution['files']['claude']['sha256'])
        case.prepare()
        for number in (1, 2):
            manifest, schema, target = _runtime_manifest(case, number)
            argv = case.call(manifest, schema, number)
            assert argv[argv.index('--model')+1] == model.FALLBACK
            assert ('--resume' in argv) is (number == 2)
            assert str(target/'journal') in argv
    finally:
        case.doCleanups()


def test_runtime_rejects_direct_profile_with_self_consistent_but_unrecognized_cli():
    import test_inspection_runtime as fixtures
    case = fixtures.RuntimeTests()
    case.setUp()
    try:
        case.prepare()
        manifest, schema, _ = _runtime_manifest(case, 1)
        assert case.execution['files']['claude']['sha256'] != model.CLI_SHA256
        with pytest.raises(ValueError):
            case.call(manifest, schema)
    finally:
        case.doCleanups()
