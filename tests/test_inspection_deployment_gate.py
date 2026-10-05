"""Private synthetic exports exercise gate boundaries; no live review or canary."""
import copy
import json
from pathlib import Path
import sys
import types

import pytest
from orchestrator import deployment_review as g, inspection_access as access
from orchestrator import inspection_bootstrap as bootstrap, inspection_review as review
from orchestrator import inspection_deployment as adapter, inspection_runtime as runtime_guard
from orchestrator import inspection_canary as native_canary
from inspection_confinement_fixtures import static_confinement, readback as confinement_readback
from test_inspection_bootstrap import inputs as bootstrap_inputs, originals as bootstrap_originals
from test_inspection_deployment import material_fixture
from test_deployment_review import fixture as legacy_fixture, SOURCE, write


def indexed(directory, files):
    for name, raw in files.items(): write(directory/name, raw)
    index = {'schema': 'inspection-deployment-file-index/v1', 'files': {
        name: {'sha256': g.digest(raw), 'bytes': len(raw)} for name, raw in files.items()}}
    return write(directory/'index.json', g.encoded(index))


def local_reads(monkeypatch):
    # Emulate UID0 only for these local synthetic bytes. O_NOFOLLOW and all
    # native read/index/hash checks remain active; no protected-host claim.
    monkeypatch.setattr(g, 'protected', lambda path, directory=False: Path(path).lstat())


def bootstrap_fixture(*, verdict='APPROVE', include_plan=True):
    files, context = bootstrap_inputs()
    files['tests/extra-reviewed-only.py'] = b'# Extra uninstalled test preserved in old named map.\n'
    permit = g.encoded({'operator_original_sha256': '7'*64})
    execution = {'settings_sha256': g.digest(g.encoded(access.access_settings())), 'files': {
        'hooks': {'sha256': g.digest(files['orchestrator/inspection_access.py'])},
        'runner': {'sha256': g.digest(files['orchestrator/inspection_runner.py'])}}}
    runtime = {'bootstrap_source': SOURCE, 'enabling_files': sorted(files), 'execution': execution}
    plan = g.encoded({'source': SOURCE, 'execution': execution})
    launch = g.encoded({'schema': 'inspection-canary-launch-plan/v1', 'source': SOURCE,
        'bootstrap_source': SOURCE, 'enabling_files': {name: g.digest(raw) for name, raw in files.items()},
        'expected_plan_sha256': g.digest(plan), 'permit_sha256': g.digest(permit)})
    private = {str(i): {'sha256': g.digest(raw), 'content': raw.decode()}
               for i, raw in enumerate((launch, plan, permit) if include_plan else (permit,))}
    old = bootstrap_originals(files, context, supplements=private, verdict=verdict)
    raw = {'bootstrap/'+name: value for name, value in old.items()}
    raw.update({'runtime.json': g.encoded(runtime), 'administrative-permit.json': permit,
        'canary/administrative-permit.json': permit, 'canary/plan.json': plan,
        'canary/canary-plan.json': launch})
    return raw, {name: value for name, value in files.items() if not name.startswith('tests/')}


def test_bootstrap_uses_full_original_map_but_only_mandatory_archive_subset():
    raw, files = bootstrap_fixture()
    result = g._inspection_bootstrap(raw, files)
    assert 'tests/extra-reviewed-only.py' in result['enabling_files']
    assert 'tests/extra-reviewed-only.py' not in files


@pytest.mark.parametrize('name', ['orchestrator/inspection_runner.py', 'orchestrator/deployment_review.py',
                                 'docs/test-direction.md', 'configs/test-authority.json'])
def test_changed_enabler_or_current_policy_cannot_approve_itself(name):
    raw, files = bootstrap_fixture()
    if name.endswith('.json'):
        changed = json.loads(files[name]); changed['direction_sha256'] = 'f'*64
        files[name] = g.encoded(changed)
    else:
        files[name] += b'changed\n'
    with pytest.raises(ValueError, match='UNREVIEWED_ENABLER_OR_POLICY'):
        g._inspection_bootstrap(raw, files)


@pytest.mark.parametrize('kind', ['negative', 'plan-omitted', 'map-omitted', 'runtime-changed', 'plan-changed'])
def test_independent_bootstrap_and_native_plan_are_not_status_assertions(kind):
    raw, files = bootstrap_fixture(verdict='REQUEST_CHANGES' if kind == 'negative' else 'APPROVE',
                                   include_plan=kind != 'plan-omitted')
    runtime = json.loads(raw['runtime.json'])
    if kind == 'map-omitted': runtime['enabling_files'].remove('tests/extra-reviewed-only.py')
    if kind == 'runtime-changed': runtime['execution']['files']['hooks']['sha256'] = 'f'*64
    if kind == 'plan-changed': raw['canary/plan.json'] += b' '
    raw['runtime.json'] = g.encoded(runtime)
    with pytest.raises(ValueError): g._inspection_bootstrap(raw, files)


@pytest.mark.parametrize('kind', ['hash', 'extra', 'missing', 'path', 'nul', 'size', 'symlink'])
def test_index_is_exact_bounded_regular_text_tree(tmp_path, monkeypatch, kind):
    local_reads(monkeypatch); folder = tmp_path/'inspection'
    indexed(folder, {'manifest.json': b'{}\n'})
    if kind == 'hash': (folder/'manifest.json').write_bytes(b'[]\n')
    if kind == 'extra': write(folder/'auth.json', b'{}\n')
    if kind == 'missing': (folder/'manifest.json').unlink()
    if kind in ('path', 'size'):
        index = json.loads((folder/'index.json').read_bytes())
        if kind == 'path': index['files']['../escaped.json'] = index['files'].pop('manifest.json')
        else: index['files']['manifest.json']['bytes'] = 16000001
        (folder/'index.json').write_bytes(g.encoded(index))
    if kind == 'nul': indexed(folder, {'manifest.json': b'a\0b'})
    if kind == 'symlink':
        (folder/'manifest.json').unlink(); target = tmp_path/'target'; target.write_bytes(b'{}\n')
        (folder/'manifest.json').symlink_to(target)
    with pytest.raises((ValueError, OSError)): g._inspection_inventory(folder)


def test_index_original_bytes_are_returned_without_normalization(tmp_path, monkeypatch):
    local_reads(monkeypatch); folder = tmp_path/'inspection'
    original = indexed(folder, {'manifest.json': b'{}\n'}) + b' '
    (folder/'index.json').write_bytes(original)
    assert g._inspection_inventory(folder) == (original, {'manifest.json': b'{}\n'})


def material_export(f):
    """Preserve synthetic native hook filenames, raw bytes and pre/post hashes."""
    original = f['attempts'][0]['originals']; raw = {}
    for name in ('request', 'intent', 'process', 'returned', 'protocol', 'admission_event', 'admission_receipt', 'admission_policy'):
        raw['attempts/001/'+name+('.jsonl' if name == 'protocol' else '.json')] = original[name]
    for name in ('response', 'execution'): raw['attempts/001/'+name+'.json'] = f['attempts'][0][name+'_raw']
    prior = {}
    for wrapped in original['journal']:
        pair = json.loads(wrapped); row = json.loads(pair['observation_original'])
        tool_id, phase = row['tool_use_id'], row['phase']
        stem = tool_id+('.pre' if phase == 'PreToolUse' else '.post')
        row['raw_input_file'] = stem+'.input.json'
        if phase == 'PostToolUse': row['pre_observation_sha256'] = g.digest(prior[tool_id])
        observed = g.encoded(row)
        if phase == 'PreToolUse': prior[tool_id] = observed
        raw['attempts/001/journal/'+stem+'.observation.json'] = observed
        raw['attempts/001/journal/'+stem+'.input.json'] = pair['hook_input_original'].encode()
    return raw


def test_exported_attempt_runs_actual_session_and_full_read_adapter():
    f = material_fixture(); raw = material_export(f)
    f['attempts'] = [g._inspection_attempt(raw, 1, f['attempts'][0]['originals']['permission_probe'])]
    result = adapter.validate_deployment_session(**f)
    assert result['inspection_session']['status'] == 'APPROVE'


@pytest.mark.parametrize('kind', ['unread', 'source', 'response', 'orphan'])
def test_export_does_not_cure_unread_or_altered_originals(kind):
    f = material_fixture(omit_reads=('source/orchestrator/hosted_context.py',) if kind == 'unread' else ())
    raw = material_export(f)
    if kind == 'response': raw['attempts/001/response.json'] = b'{}\n'
    if kind == 'orphan': raw['attempts/001/journal/orphan.pre.input.json'] = b'{}\n'
    if kind == 'source': f['source'] = 'c'*40
    with pytest.raises(ValueError):
        f['attempts'] = [g._inspection_attempt(raw, 1, f['attempts'][0]['originals']['permission_probe'])]
        adapter.validate_deployment_session(**f)


def loader_fixture(tmp_path, monkeypatch):
    local_reads(monkeypatch); f = material_fixture(); raw = material_export(f)
    manifest = json.loads(f['manifest_raw'])
    confinement = static_confinement()
    # Synthetic observations use the fixed candidate profile identity; no policy
    # file is created, loaded or treated as actual host/canary evidence.
    confinement['profile'].update(sha256=runtime_guard.PROFILE_SHA256, bytes=runtime_guard.PROFILE_BYTES)
    execution = {'settings_sha256': manifest['pins']['settings_sha256'], 'files': {
        'hooks': {'sha256': manifest['pins']['hooks_sha256']},
        'runner': {'sha256': manifest['pins']['runner_sha256']},
        'bwrap': {'sha256': g.digest(b'synthetic unprivileged bwrap identity')}},
        'confinement': confinement}
    raw['attempts/001/confinement-readback.json'] = g.encoded(confinement_readback(
        execution, manifest['source'], manifest['session_id']))
    # The full native bootstrap and canary validators have independent fixtures.
    # Only those two leaf verifiers and their pre-existing synthetic runtime-pin
    # mapping below are substituted. The confinement original/provision/parser
    # checks and session/parser/full-read adapter run their production validators.
    monkeypatch.setattr(g, '_inspection_bootstrap', lambda raw, files, **kwargs: {'execution': execution})
    original_digest = g.digest
    monkeypatch.setattr(g, 'digest', lambda raw: manifest['pins']['runtime_sha256'] if raw == g.encoded(execution) else original_digest(raw))
    probe_raw = f['attempts'][0]['originals']['permission_probe']
    runner = types.ModuleType('orchestrator.inspection_runner')
    runner.read_canary_proof = lambda path: ({}, {})
    canary = types.ModuleType('orchestrator.inspection_canary')
    canary.verify_canary = lambda originals, expected: json.loads(probe_raw)
    canary.require_read_boundary = native_canary.require_read_boundary
    monkeypatch.setitem(sys.modules, 'orchestrator.inspection_runner', runner)
    monkeypatch.setitem(sys.modules, 'orchestrator.inspection_canary', canary)
    import orchestrator
    monkeypatch.setattr(orchestrator, 'inspection_runner', runner, raising=False)
    monkeypatch.setattr(orchestrator, 'inspection_canary', canary, raising=False)
    raw.update({'manifest.json': f['manifest_raw'], 'context-original.json': f['context_raw'],
        'change-context.json': f['changes_raw'], 'change-bindings.json': f['view_files']['evidence/change-bindings.json'],
        'runtime.json': g.encoded({'execution': execution}), 'administrative-permit.json': g.encoded({'operator_original_sha256': manifest['current_request_sha256']}),
        'permission-probe.json': probe_raw, 'canary/permission-probe.json': probe_raw})
    raw.update({'bootstrap/'+name: b'{}\n' for name in g.ORIGINAL_NAMES})
    raw.update({'view/'+name: value for name, value in f['view_files'].items()})
    bundle = tmp_path/'bundle'; indexed(bundle/'inspection', raw)
    originals = {name: raw['attempts/001/'+name] for name in g.ORIGINAL_NAMES}
    source = {name: f['view_files']['source/'+name] for name in json.loads(f['proposal_raw'])['source_files']}
    return bundle, f, raw, originals, source


def test_full_loader_binds_index_and_last_actual_six(tmp_path, monkeypatch):
    bundle, f, raw, originals, files = loader_fixture(tmp_path, monkeypatch)
    result, proof = g.inspection_review(bundle, f['proposal_raw'], files, originals)
    assert result['inspection_session']['status'] == 'APPROVE'
    assert proof['inspection_index_sha256'] == g.digest((bundle/'inspection/index.json').read_bytes())
    assert proof['inspection_original_wrapper_index_sha256'] == result['full_original_wrapper_index_sha256']


def test_reindexed_mutated_normal_confinement_is_rejected_by_real_verifier(tmp_path, monkeypatch):
    bundle, f, raw, originals, files = loader_fixture(tmp_path, monkeypatch)
    # First prove this otherwise-identical synthetic export passes the full gate.
    assert g.inspection_review(bundle, f['proposal_raw'], files, originals)[0]['inspection_session']['status'] == 'APPROVE'
    name = 'attempts/001/confinement-readback.json'
    changed = json.loads(raw[name])
    changed['loaded_profiles'] = ['bwrap (enforce)', 'unpriv_bwrap (complain)']
    raw[name] = g.encoded(changed)
    indexed(bundle/'inspection', raw)  # Rehashing the wrapper must not cure this.
    with pytest.raises(ValueError, match='INSPECTION_CONFINEMENT_READBACK_PROTECTION'):
        g.inspection_review(bundle, f['proposal_raw'], files, originals)


@pytest.mark.parametrize('name', g.ORIGINAL_NAMES)
def test_root_six_must_be_last_exact_attempt_originals(tmp_path, monkeypatch, name):
    bundle, f, raw, originals, files = loader_fixture(tmp_path, monkeypatch); originals[name] += b' '
    with pytest.raises(ValueError, match='BUNDLE_LAST_ORIGINALS_CHANGED'):
        g.inspection_review(bundle, f['proposal_raw'], files, originals)


def test_index_cannot_authorize_extra_runtime_auth_or_native_session_cache(tmp_path, monkeypatch):
    bundle, f, raw, originals, files = loader_fixture(tmp_path, monkeypatch)
    raw['native-session-cache/token.json'] = b'{}\n'; indexed(bundle/'inspection', raw)
    with pytest.raises(ValueError, match='UNEXPECTED_EXPORT_FILE'):
        g.inspection_review(bundle, f['proposal_raw'], files, originals)


@pytest.mark.parametrize('profile', ['unknown', 'direct-inspection/v2', None])
def test_unknown_explicit_profile_does_not_fall_back_to_legacy(tmp_path, monkeypatch, profile):
    f = legacy_fixture(tmp_path, monkeypatch); p = json.loads((f['bundle']/'proposal.json').read_bytes())
    p['review_profile'] = profile; write(f['bundle']/'proposal.json', g.encoded(p))
    with pytest.raises(ValueError, match='EXPLICIT_REVIEW_PROFILE_REQUIRED'):
        g.verify_bundle(f['bundle'], f['root'], SOURCE)


def test_direct_profile_and_old_plan_are_mutually_exclusive(tmp_path, monkeypatch):
    f = legacy_fixture(tmp_path, monkeypatch); p = json.loads((f['bundle']/'proposal.json').read_bytes())
    p.update(review_profile=adapter.PROFILE, review_plan_sha256='c'*64)
    write(f['bundle']/'proposal.json', g.encoded(p))
    with pytest.raises(ValueError, match='EXPLICIT_REVIEW_PROFILE_REQUIRED'):
        g.verify_bundle(f['bundle'], f['root'], SOURCE)


def test_direct_profile_keeps_native_dependency_and_configuration_checks(tmp_path, monkeypatch):
    f = legacy_fixture(tmp_path, monkeypatch); p = json.loads((f['bundle']/'proposal.json').read_bytes())
    p['review_profile'] = adapter.PROFILE; raw = write(f['bundle']/'proposal.json', g.encoded(p))
    actual = g.review_originals(f['raw'], SOURCE)
    actual['private_text'][g.digest(raw)] = raw
    calls = []
    limits = {}
    original_read = g.read
    def tracked_read(path, *, maximum=4000000):
        if Path(path).parent == f['bundle'] and Path(path).name in g.ORIGINAL_NAMES:
            limits[Path(path).name] = maximum
        return original_read(path, maximum=maximum)
    monkeypatch.setattr(g, 'read', tracked_read)
    def checked_loader(*args, prospective=False):
        calls.append((args, prospective))
        return actual, {'review_profile': adapter.PROFILE, 'inspection_index_sha256': 'd'*64}
    monkeypatch.setattr(g, 'inspection_review', checked_loader)
    result = g.verify_bundle(f['bundle'], f['root'], SOURCE)
    assert calls and result['inspection_index_sha256'] == 'd'*64
    assert limits == {name: 16000000 for name in g.ORIGINAL_NAMES}
    monkeypatch.setattr(g, 'dependency_metadata', lambda name: {'sha256': 'changed'})
    with pytest.raises(ValueError, match='LAUNCHER_IDENTITY_CHANGED'):
        g.verify_bundle(f['bundle'], f['root'], SOURCE)


@pytest.mark.parametrize('mutation', [None, 'declared_7001', 'unindexed_7001', 'changed_bytes'])
def test_inventory_7000_member_boundary_keeps_exact_tree_and_hash_checks(
        tmp_path, monkeypatch, mutation):
    local_reads(monkeypatch)
    folder = tmp_path/'inspection'
    files = {f'view/synthetic/{number:05d}.txt':
             f'Synthetic exact export member {number}.\n'.encode()
             for number in range(7000)}
    index_raw = indexed(folder, files)
    if mutation is None:
        assert g._inspection_inventory(folder) == (index_raw, files)
        return
    if mutation == 'declared_7001':
        index = json.loads(index_raw)
        extra = b'Synthetic declared extra.\n'
        index['files']['view/synthetic/extra.txt'] = {
            'sha256': g.digest(extra), 'bytes': len(extra)}
        (folder/'index.json').write_bytes(g.encoded(index))
        reason = 'DEPLOYMENT_INSPECTION_INDEX_REQUIRED'
    elif mutation == 'unindexed_7001':
        write(folder/'view/synthetic/extra.txt', b'Synthetic unindexed extra.\n')
        reason = 'DEPLOYMENT_INSPECTION_EXPORT_TOO_LARGE'
    else:
        name = 'view/synthetic/06999.txt'
        # Preserve the byte count so only exact digest verification catches it.
        (folder/name).write_bytes(files[name][:-1] + b'!')
        reason = 'DEPLOYMENT_INSPECTION_FILE_CHANGED'
    with pytest.raises(ValueError, match=reason):
        g._inspection_inventory(folder)

def test_bootstrap_accepts_exact_enabling_hash_map_and_retains_legacy_list():
    raw,files=bootstrap_fixture()
    legacy=g._inspection_bootstrap(raw,files)
    value=json.loads(raw['runtime.json'])
    pins=json.loads(raw['canary/canary-plan.json'])['enabling_files']
    value['enabling_files']=pins
    raw['runtime.json']=g.encoded(value)
    current=g._inspection_bootstrap(raw,files)
    assert current['enabling_files']==pins
    assert set(legacy['enabling_files'])==set(current['enabling_files'])


@pytest.mark.parametrize('mutation',['hash','missing','extra','nonstring-value'])
def test_bootstrap_enabling_hash_map_requires_every_exact_approved_pin(mutation):
    raw,files=bootstrap_fixture()
    value=json.loads(raw['runtime.json'])
    pins=json.loads(raw['canary/canary-plan.json'])['enabling_files']
    name='orchestrator/inspection_runner.py'
    if mutation=='hash':pins[name]='f'*64
    elif mutation=='missing':pins.pop(name)
    elif mutation=='extra':pins['unreviewed.py']='f'*64
    else:pins[name]=123
    value['enabling_files']=pins
    raw['runtime.json']=g.encoded(value)
    with pytest.raises(ValueError,match='DEPLOYMENT_INSPECTION_COMPLETE_BOOTSTRAP_MAP_REQUIRED'):
        g._inspection_bootstrap(raw,files)


def test_legacy_enabling_list_still_rejects_duplicate_names():
    raw,files=bootstrap_fixture()
    value=json.loads(raw['runtime.json'])
    value['enabling_files'].append(value['enabling_files'][0])
    raw['runtime.json']=g.encoded(value)
    with pytest.raises(ValueError,match='DEPLOYMENT_INSPECTION_COMPLETE_BOOTSTRAP_MAP_REQUIRED'):
        g._inspection_bootstrap(raw,files)


def test_new_native_install_refuses_valid_legacy_bootstrap_without_rewriting_history():
    raw, files = bootstrap_fixture()
    originals = dict(raw)
    historical = g._inspection_bootstrap(raw, files)
    with pytest.raises(ValueError, match='REVIEW_PROSPECTIVE_V2_REQUIRED'):
        g._inspection_bootstrap(raw, files, prospective=True)
    assert raw == originals
    assert g._inspection_bootstrap(raw, files) == historical


def test_indexed_native_install_propagates_prospective_gate(tmp_path, monkeypatch):
    bundle, f, raw, originals, files = loader_fixture(tmp_path, monkeypatch)
    def checked(actual, candidate, *, prospective=False):
        assert prospective is True
        assert actual == raw
        bootstrap.require_v2_review({name: actual['bootstrap/'+name] for name in g.ORIGINAL_NAMES})
        raise AssertionError('Historical native bootstrap passed fresh installation')
    monkeypatch.setattr(g, '_inspection_bootstrap', checked)
    with pytest.raises(ValueError, match='REVIEW_PROSPECTIVE_V2_REQUIRED'):
        g.inspection_review(bundle, f['proposal_raw'], files, originals, prospective=True)


def test_prospective_native_bootstrap_accepts_exact_v2_policy_context_and_plan():
    from orchestrator import review_input_codec as codec
    from test_review_policy_baseline import synthetic_proof
    proof, _, context = synthetic_proof()
    baseline = bootstrap.validate_policy_baseline(proof)
    raw, files = bootstrap_fixture()
    old = {name: raw['bootstrap/'+name] for name in g.ORIGINAL_NAMES}
    complete = {name: body.encode() for name, body in
                g._review_originals(old, SOURCE, {bootstrap.SCOPE})['source_text'].items()}
    complete['orchestrator/change_requests.py'] = b'# Synthetic V2 validator literal.\n'
    pins = {name: g.digest(body) for name, body in complete.items()}
    runtime = json.loads(raw['runtime.json']); runtime['enabling_files'] = pins
    launch = json.loads(raw['canary/canary-plan.json']); launch['enabling_files'] = pins
    raw['runtime.json'] = g.encoded(runtime)
    raw['canary/canary-plan.json'] = g.encoded(launch)
    private = {name: {'sha256': g.digest(raw[name]), 'content': raw[name].decode()}
               for name in ('canary/canary-plan.json', 'canary/plan.json', 'administrative-permit.json')}
    originals = bootstrap_originals(complete, context, supplements=private)
    request = json.loads(originals['request.json'])
    request.update(input_presentation=codec.FORMAT_V2, policy_baseline=baseline['descriptor'])
    request['prompt'] = codec.encode_v2(bootstrap.SCOPE, SOURCE,
        {name: body.decode() for name, body in complete.items()}, private, [], context, baseline['descriptor'])
    originals['request.json'] = g.encoded(request)
    execution = json.loads(originals['execution.json'])
    execution.update(request_sha256=g.digest(originals['request.json']),
        prompt_sha256=g.digest(request['prompt'].encode()), policy_baseline=baseline['descriptor'])
    originals['execution.json'] = g.encoded(execution)
    intent = json.loads(originals['intent.json']); intent['request_sha256'] = execution['request_sha256']
    originals['intent.json'] = g.encoded(intent)
    raw.update({'bootstrap/'+name: body for name, body in originals.items()})
    raw.update({'bootstrap/policy-baseline/'+name: body for name, body in proof.items()})
    raw['context-original.json'] = context
    files = {name: body for name, body in complete.items() if not name.startswith('tests/')}
    assert g._inspection_bootstrap(raw, files, prospective=True) == runtime
    assert g._inspection_bootstrap(raw, files) == runtime
    changed = json.loads(context); changed['role'] = 'Unapproved replacement role'
    raw['context-original.json'] = codec.context_original(changed)
    with pytest.raises(ValueError):
        g._inspection_bootstrap(raw, files, prospective=True)
