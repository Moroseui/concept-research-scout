"""Offline provisioning guards; bootstrap/provider/host probes are explicit fixtures.

These tests do not establish actual bootstrap approval, kernel policy, or canary proof.
The loader is injected into an in-memory runner copy only when testing its private snippet.
"""
import copy
import json
import os
from pathlib import Path
import subprocess
import types
from unittest.mock import Mock

import pytest
from orchestrator import inspection_runner as original_runner
from orchestrator import inspection_bootstrap as bootstrap
from orchestrator import inspection_runtime as original_runtime
import orchestrator


@pytest.fixture
def case(tmp_path, monkeypatch):
    r = types.ModuleType('provision_fixture')
    r.__dict__.update(original_runner.__dict__)
    for name, function in list(r.__dict__.items()):
        if isinstance(function, types.FunctionType) and function.__module__ == original_runner.__name__:
            rebound = types.FunctionType(function.__code__, r.__dict__, function.__name__, function.__defaults__, function.__closure__)
            rebound.__kwdefaults__ = function.__kwdefaults__
            r.__dict__[name] = rebound
    snippet = os.environ.get('INSPECTION_PROVISION_SNIPPET')
    if snippet:
        exec(compile(Path(snippet).read_bytes(), snippet, 'exec'), r.__dict__)
    root = tmp_path/'sessions'; root.mkdir()
    directory = root/'c43fae59-944d-451a-8ee8-1c3f2a1d1dbb'; directory.mkdir(mode=0o700)
    source_root = tmp_path/'source'; (source_root/'orchestrator').mkdir(parents=True)
    source_file = source_root/'orchestrator/inspection_runner.py'; source_file.write_bytes(b'exact reviewed source\n')
    r.__file__ = str(source_file); r.ROOT = root
    source = 'a'*40
    profile = tmp_path/'staged-profile.txt'; profile.write_bytes(b'# exact synthetic profile\n')
    target_parent = tmp_path/'apparmor'; target_parent.mkdir(mode=0o755)
    target = target_parent/'bwrap-userns-restrict'
    profiles = tmp_path/'profiles'; profiles.write_bytes(b'existing-unrelated (enforce)\n')
    state = tmp_path/'controller'; state.mkdir(); (state/'admission.lock').touch(mode=0o600)
    policy = {'unchanged': True}; control = {'revision': 15, 'paused': 1, 'steering': [['stop', 'fixed']]}
    binding = {'source': 'b'*40, 'branch': 'approved-admin-branch', 'kind': 'nightly_review',
               'turn_id': 'c'*64, 'policy_sha256': r.sha(r.encoded(policy))}
    permit = {'operator_original_sha256': 'd'*64, 'control_snapshot': control}
    conf = {'profile': {'sha256': r.sha(profile.read_bytes()), 'bytes': profile.stat().st_size,
                       'uid': 0, 'gid': 0, 'mode': 0o644},
            'provision_receipt_path': str(directory/'confinement-load.json')}
    execution = {'confinement': conf, 'files': {'bwrap': {'sha256': 'e'*64}, 'claude': {'path': '/runtime/claude'}},
                 'reviewer': {'uid': 1002}}
    expected = {'source': source, 'execution': execution,
                'phases': {x: {'admission_binding': binding} for x in ('baseline', 'hooks')}}
    manifest = {'source': source, 'current_request_sha256': permit['operator_original_sha256'],
                'admission_binding': binding}
    launch = {'schema': 'inspection-canary-launch-plan/v1', 'source': source, 'bootstrap_source': source,
              'enabling_files': {'orchestrator/inspection_runner.py': r.sha(source_file.read_bytes())},
              'expected_plan_sha256': r.sha(r.encoded(expected)), 'permit_sha256': r.sha(r.encoded(permit)),
              'prepared_originals': {x: {'manifest.json': r.encoded(manifest).decode()} for x in ('baseline', 'hooks')}}
    for name, obj in [('canary-plan.json', launch), ('plan.json', expected), ('administrative-permit.json', permit)]:
        (directory/name).write_bytes(r.encoded(obj))
    originals = directory/'bootstrap'; originals.mkdir()
    for name in ('request.json', 'response.json', 'execution.json', 'protocol.jsonl', 'intent.json', 'returned.json'):
        (originals/name).write_bytes(b'preserved synthetic old original '+name.encode())
    # The runner now reads the presentation marker before calling the synthetic validator.
    (originals/'request.json').write_bytes(r.encoded({'input_presentation': bootstrap.codec.FORMAT_V2}))
    monkeypatch.setattr(bootstrap, 'read_policy_baseline', lambda path: {'synthetic-proof': b'offline fixture'})
    literals = [r.encoded(launch), r.encoded(expected), r.encoded(permit), profile.read_bytes()]
    approved = {'private_text': {r.sha(raw): raw for raw in literals}}
    validator = Mock(return_value=approved)
    monkeypatch.setattr(bootstrap, 'validate_bootstrap', validator)
    r.CONTROLLER_CONFIG = tmp_path/'controller.json'; r.BROKER_CONFIG = tmp_path/'broker.json'
    r.CONTROLLER_CONFIG.write_bytes(r.encoded({'state': str(state), 'source': binding['source']}))
    r.BROKER_CONFIG.write_bytes(r.encoded({'sources': [binding['source']], 'policy': policy}))
    r.current_control = Mock(return_value=control)
    r._confinement_process_census = Mock(return_value={'processes': [], 'fixture': True})
    monkeypatch.setattr(os, 'getuid', lambda: 0)
    # Only target temp-file chown is replaced; the real file is never privileged.
    chowns = []; monkeypatch.setattr(os, 'fchown', lambda fd, uid, gid: chowns.append((uid, gid)))
    real_stat = Path.stat
    def root_fixture_stat(path, *args, **kwargs):
        result = real_stat(path, *args, **kwargs)
        if path in (directory, target_parent):
            row = list(result); row[4] = 0; return os.stat_result(row)
        return result
    monkeypatch.setattr(Path, 'stat', root_fixture_stat)
    rt = types.SimpleNamespace(PROFILE_PATH=target, PROFILES_PATH=profiles,
        PROFILE_NAMES=['bwrap', 'unpriv_bwrap'], APPARMOR_BASE=target_parent,
        PARSER='/fixed/apparmor_parser', PROVISION_SCHEMA='inspection-apparmor-provision/v1')
    rt._execution = Mock(side_effect=lambda obj: obj['execution'])
    rt._confinement = Mock(side_effect=lambda e: e['confinement'])
    argv = [rt.PARSER, '--config-file=/dev/null', '--skip-cache', '--base='+str(target_parent),
            '--Include='+str(target_parent), '--warn=rule-not-enforced', '--Werror=rule-not-enforced', '--add', str(target)]
    rt._parser_argv = Mock(side_effect=lambda action: argv if action == 'load' else pytest.fail('unexpected parser mode'))
    def config(e):
        assert target.read_bytes() == profile.read_bytes()
        assert target.stat().st_mode & 0o777 == 0o644
        return {'status': 'VERIFIED_CONFIGURATION_NO_LOAD_CLAIM'}
    rt.actual_config_readback = Mock(side_effect=config)
    rt._active_protection = Mock(return_value={'loaded_profiles': ['bwrap (enforce)', 'unpriv_bwrap (enforce)']})
    rt._policy_inputs = Mock()
    def exact_receipt(raw, e):
        value = r.access.parsed(raw)
        assert set(value) == {'schema','status','confinement_sha256','bwrap_sha256','profile_sha256','load','loaded_profiles'}
        assert value['load'] == {'argv': argv, 'returncode': 0, 'stdout': '', 'stderr': ''}
        assert value['confinement_sha256'] == r.sha(r.encoded(e['confinement']))
    rt._provision = Mock(side_effect=exact_receipt)
    monkeypatch.setattr(orchestrator, 'inspection_runtime', rt)
    calls = []
    def run(argv_value, **kwargs):
        calls.append((argv_value, kwargs)); assert argv_value == argv
        return subprocess.CompletedProcess(argv_value, 0, b'', b'')
    monkeypatch.setattr(subprocess, 'run', run)
    monkeypatch.setattr(subprocess, 'Popen', lambda *a, **k: pytest.fail('unexpected provider/process launch'))
    return types.SimpleNamespace(r=r, rt=rt, root=root, directory=directory, source_file=source_file,
        profile=profile, target=target, profiles=profiles, approved=approved, validator=validator,
        expected=expected, launch=launch, permit=permit, control=control, calls=calls, chowns=chowns,
        execution=execution, argv=argv, plan=directory/'canary-plan.json')


def invoke(c):
    return c.r.provision_confinement(c.plan, c.profile)


def test_success_is_one_load_not_provider_or_admission(case):
    c = case; receipt = invoke(c)
    assert receipt['status'] == 'PROFILE_LOADED' and len(c.calls) == 1 and c.chowns == [(0, 0)]
    assert c.target.read_bytes() == c.profile.read_bytes()
    assert c.validator.call_args.args[1:] == ('a'*40, {'orchestrator/inspection_runner.py': b'exact reviewed source\n'})
    assert set(c.validator.call_args.args[0]) == {'request.json','response.json','execution.json','protocol.jsonl','intent.json','returned.json'}
    assert c.validator.call_args.kwargs == {'policy_baseline': {'synthetic-proof': b'offline fixture'}}
    names = {p.name for p in c.directory.iterdir()}
    assert {'confinement-load.json','confinement-config-readback.json','confinement-loaded-profiles.before.txt',
            'confinement-provision-intent.json','confinement-load-returned.json','confinement-recovery.json'} <= names
    assert not any(name.startswith('admission') for name in names)
    recovery = json.loads((c.directory/'confinement-recovery.json').read_bytes())
    assert recovery['remove_argv'][-2:] == ['--remove', str(c.target)] and not recovery['automatic']
    with pytest.raises(ValueError, match='ALREADY_ATTEMPTED'):
        invoke(c)
    assert len(c.calls) == 1


@pytest.mark.parametrize('kind', ['negative_bootstrap','profile_not_reviewed','plan_not_reviewed','changed_source',
    'profile_changed','symlink_profile','wrong_plan_source','changed_permit','control_changed','unpaused',
    'policy_changed','installed_source_changed','existing_target','target_symlink','existing_intent',
    'loaded_bwrap','loaded_unpriv_bwrap','loaded_child','active_process'])
def test_preconditions_never_copy_or_load(case, kind, monkeypatch):
    c = case
    if kind == 'negative_bootstrap': c.validator.side_effect = ValueError('actual legacy refusal')
    if kind == 'profile_not_reviewed': del c.approved['private_text'][c.r.sha(c.profile.read_bytes())]
    if kind == 'plan_not_reviewed': del c.approved['private_text'][c.r.sha(c.plan.read_bytes())]
    if kind == 'changed_source': c.source_file.write_bytes(b'changed source')
    if kind == 'profile_changed': c.profile.write_bytes(b'changed profile')
    if kind == 'symlink_profile':
        original = c.profile.with_name('regular-profile'); c.profile.rename(original); c.profile.symlink_to(original)
    if kind == 'wrong_plan_source':
        value = json.loads(c.plan.read_bytes()); value['source'] = 'f'*40; c.plan.write_bytes(c.r.encoded(value))
    if kind == 'changed_permit': (c.directory/'administrative-permit.json').write_bytes(b'{}')
    if kind == 'control_changed': c.r.current_control.return_value = {**c.control, 'revision': 16}
    if kind == 'unpaused': c.r.current_control.return_value = {**c.control, 'paused': 0}
    if kind in ('policy_changed','installed_source_changed'):
        path = c.r.BROKER_CONFIG if kind == 'policy_changed' else c.r.CONTROLLER_CONFIG
        value = json.loads(path.read_bytes())
        if kind == 'policy_changed': value['policy'] = {'changed': True}
        else: value['source'] = 'f'*40
        path.write_bytes(c.r.encoded(value))
    if kind == 'existing_target': c.target.write_bytes(b'unknown existing policy')
    if kind == 'target_symlink': c.target.symlink_to(c.profile)
    if kind == 'existing_intent': (c.directory/'confinement-provision-intent.json').write_bytes(b'old intent')
    if kind.startswith('loaded_'):
        name = {'loaded_bwrap': 'bwrap (complain)', 'loaded_unpriv_bwrap': 'unpriv_bwrap (enforce)',
                'loaded_child': 'bwrap//unexpected (enforce)'}[kind]
        c.profiles.write_text(name+'\n')
    if kind == 'active_process': c.r._confinement_process_census.side_effect = ValueError('active process')
    before = c.target.read_bytes() if c.target.exists() else None
    with pytest.raises((ValueError, KeyError)):
        invoke(c)
    assert not c.calls
    assert (c.target.read_bytes() if c.target.exists() else None) == before
    assert not (c.directory/'confinement-load.json').exists()


@pytest.mark.parametrize('failure', ['compile','late_process','late_control','loaded_change','parser_nonzero','timeout','not_enforced'])
def test_partial_install_preserves_intent_and_refuses_retry(case, failure, monkeypatch):
    c = case
    if failure == 'compile': c.rt.actual_config_readback.side_effect = ValueError('strict compile refused')
    if failure == 'late_process': c.r._confinement_process_census.side_effect = [{}, ValueError('active process')]
    if failure == 'late_control': c.r.current_control.side_effect = [c.control, {**c.control, 'revision': 16}]
    if failure == 'loaded_change':
        def change(e): c.profiles.write_bytes(b'new unrelated policy (enforce)\n'); return {}
        c.rt.actual_config_readback.side_effect = change
    if failure in ('parser_nonzero','timeout'):
        def run(argv, **kwargs):
            c.calls.append((argv, kwargs))
            if failure == 'timeout': raise subprocess.TimeoutExpired(argv, 30, output=b'partial stdout', stderr=b'partial stderr')
            return subprocess.CompletedProcess(argv, 1, b'out', b'compile refused')
        monkeypatch.setattr(subprocess, 'run', run)
    if failure == 'not_enforced': c.rt._active_protection.side_effect = ValueError('unenforced')
    with pytest.raises((ValueError, subprocess.TimeoutExpired)):
        invoke(c)
    assert c.target.read_bytes() == c.profile.read_bytes()
    assert (c.directory/'confinement-provision-intent.json').exists()
    assert (c.directory/'confinement-provision-failure.json').exists()
    assert not (c.directory/'confinement-load.json').exists()
    count = len(c.calls)
    with pytest.raises(ValueError, match='ALREADY_ATTEMPTED'): invoke(c)
    assert len(c.calls) == count
    if failure in ('parser_nonzero','timeout'):
        assert (c.directory/'confinement-load.stdout.txt').read_bytes() in (b'out', b'partial stdout')
        assert (c.directory/'confinement-load-returned.json').exists()


@pytest.mark.parametrize('comm,uid,exe,refused', [('python',0,'python',False),('bwrap',0,'bwrap',True),
    ('claude',0,'claude',True),('codex',997,'codex',True),('node',1002,'node',True),
    ('truncated-name',0,'claude (deleted)',True)])
def test_metadata_census_rejects_active_processes(case, tmp_path, monkeypatch, comm, uid, exe, refused):
    c = case; r = c.r
    root = tmp_path/'fake-proc'; (root/'123').mkdir(parents=True)
    (root/'123/status').write_text('Name:\t'+comm+'\nUid:\t'+'\t'.join([str(uid)]*4)+'\n')
    (root/'123/comm').write_text(comm+'\n'); (root/'123/exe').symlink_to('/runtime/'+exe)
    real_path = Path
    monkeypatch.setattr(r, 'Path', lambda value: root if str(value) == '/proc' else real_path(value))
    original = original_runner.__dict__.get('_confinement_process_census')
    if os.environ.get('INSPECTION_PROVISION_SNIPPET'):
        ns = r.__dict__.copy(); exec(Path(os.environ['INSPECTION_PROVISION_SNIPPET']).read_text(), ns); function = ns['_confinement_process_census']
    else: function = types.FunctionType(original.__code__, r.__dict__)
    if refused:
        with pytest.raises(ValueError, match='ACTIVE_REVIEWER_OR_BWRAP'): function(c.execution)
    else:
        result = function(c.execution); assert result['processes'][0]['pid'] == 123
        assert result['credential_content_reads'] == result['command_argument_reads'] == 0


@pytest.mark.parametrize('consumer',['confinement','canary'])
def test_v2_policy_proof_reaches_existing_bootstrap_validator_before_operation(case,monkeypatch,consumer):
    from orchestrator import review_input_codec as codec
    c=case
    (c.directory/'bootstrap/request.json').write_bytes(c.r.encoded({'input_presentation':codec.FORMAT_V2}))
    proof={'baseline.json':c.r.encoded({'synthetic_fixture_only':True})}
    def read_baseline(path):
        assert path==c.directory/'bootstrap/policy-baseline'
        return proof
    monkeypatch.setattr(bootstrap,'read_policy_baseline',read_baseline)
    def checked(*args,policy_baseline=None):
        assert policy_baseline==proof
        raise ValueError('SYNTHETIC_STOP_AFTER_V2_PROOF_BINDING')
    c.validator.side_effect=checked
    if consumer=='canary':
        monkeypatch.setenv('INVOCATION_ID','a'*32)
        c.r.service_readback=lambda unit: {'synthetic_service':True}
        c.r.require_service=lambda value:None
        action=lambda:c.r.run_canary(c.plan,'baseline')
    else:action=lambda:c.r._confinement_bootstrap(c.plan,c.profile,c.rt)
    with pytest.raises(ValueError,match='STOP_AFTER_V2_PROOF_BINDING'):action()
    assert c.validator.call_count==1
    assert c.calls==[] and not c.target.exists()
    assert not list(c.root.rglob('admission_event.json'))


@pytest.mark.parametrize('consumer', ['canary', 'confinement'])
@pytest.mark.parametrize('presentation', [None, bootstrap.codec.FORMAT, 'raw-text-review-envelope/v3'])
def test_legacy_bootstrap_refuses_before_canary_admission_or_profile_load(case, monkeypatch, consumer, presentation):
    c = case
    (c.directory/'bootstrap/request.json').write_bytes(c.r.encoded({'input_presentation': presentation}))
    if consumer == 'canary':
        monkeypatch.setenv('INVOCATION_ID', 'a'*32)
        c.r.service_readback = lambda unit: {}
        c.r.require_service = lambda value: None
        action = lambda: c.r.run_canary(c.plan, 'baseline')
    else:
        action = lambda: invoke(c)
    with pytest.raises(ValueError, match='REVIEW_PROSPECTIVE_V2_REQUIRED'):
        action()
    c.validator.assert_not_called()
    assert c.calls == [] and not c.target.exists()
    assert not list(c.root.rglob('admission_event.json'))
    assert not list(c.root.rglob('confinement-provision-intent.json'))
