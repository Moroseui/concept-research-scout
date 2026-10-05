"""Pure mount and pre-admission checks; no native isolation or provider claims."""
import copy
from pathlib import Path
import pytest
from orchestrator import inspection_access as access
from orchestrator import inspection_canary as canary
from orchestrator import inspection_runner as runner
from orchestrator import inspection_runtime as runtime
from test_inspection_canary import fixture

SESSION = '00000000-0000-4000-8000-000000000001'
PROBE = '/var/lib/research-system/inspection-reviews/00000000-0000-4000-8000-000000000009/probe'


def command_fixture(mask=True, session=SESSION):
    execution = {'reviewer': {'home': str(runtime.AUTH_HOME)}, 'read_only_mounts': [],
        'auth_census': {'home': {'.claude': {'kind': 'directory'},
            '.claude.json': {'kind': 'file'}, 'inspection-journal': {'kind': 'directory'},
            '.bashrc': {'kind': 'file'}, 'other-private': {'kind': 'directory'}},
            'claude': {'.credentials.json': {'kind': 'file'}, 'projects': {'kind': 'directory'},
                       'sessions': {'kind': 'directory'}}}}
    if mask:
        execution['auth_census']['home']['canary'] = {'kind': 'directory'}
    directory = runtime.SESSION_ROOT/session
    native = access.sandbox_command(directory/'view', directory/'state',
        directory/'attempts/001/runtime', session,
        auth_home=execution['reviewer']['home'], auth_census=execution['auth_census'])
    i = native.index('/runtime/claude')
    native[i:i] = ['--bind', str(directory/'attempts/001/journal'),
                  '/state/inspection-journal/1', '--ro-bind', PROBE, '/state/canary']
    return [runtime.RUNUSER, '-u', 'research-reviewer', '--', *native], execution


@pytest.mark.parametrize('mask', [False, True])
@pytest.mark.parametrize('session', [SESSION, '00000000-0000-4000-8000-000000000002'])
def test_exact_native_old_and_rebased_commands(mask, session):
    command, execution = command_fixture(mask, session)
    assert canary.validate_canary_mounts(command, execution, session, PROBE) is None


@pytest.mark.parametrize('mutation', [
    'swapped', 'mask-writable', 'probe-writable', 'mask-other-session', 'unexpected-probe',
    'extra-probe', 'missing-mask', 'missing-census', 'file-census', 'wrong-session',
    'hide-state', 'hide-probe-child', 'other-mask-writable', 'other-mask-source',
    'journal-writable-target', 'root-remount', 'after-claude', 'duplicate-claude',
    'wrong-user', 'unconfined-prefix'])
def test_changed_mounts_refused(mutation):
    command, execution = command_fixture()
    positions = [i for i, v in enumerate(command) if v == '/state/canary']
    a, b = positions
    if mutation == 'swapped': command[a-1], command[b-1] = command[b-1], command[a-1]
    elif mutation == 'mask-writable': command[a-2] = '--bind'
    elif mutation == 'probe-writable': command[b-2] = '--bind'
    elif mutation == 'mask-other-session': command[a-1] = command[a-1].replace(SESSION, '00000000-0000-4000-8000-000000000002')
    elif mutation == 'unexpected-probe': command[b-1] = '/unrelated-private'
    elif mutation == 'extra-probe': command[b+1:b+1] = ['--ro-bind', PROBE, '/state/canary']
    elif mutation == 'missing-mask': del command[a-2:a+1]
    elif mutation == 'missing-census': del execution['auth_census']['home']['canary']
    elif mutation == 'file-census': execution['auth_census']['home']['canary'] = {'kind': 'file'}
    elif mutation == 'wrong-session':
        with pytest.raises(ValueError): canary.validate_canary_mounts(command, execution, '00000000-0000-4000-8000-000000000002', PROBE)
        return
    elif mutation in ('hide-state', 'hide-probe-child', 'root-remount'):
        destination = {'hide-state': '/state', 'hide-probe-child': '/state/canary/probe.txt', 'root-remount': '/'}[mutation]
        command[b+1:b+1] = ['--ro-bind', '/unrelated-private', destination]
    elif mutation == 'other-mask-writable': command[command.index('/state/.bashrc')-2] = '--bind'
    elif mutation == 'other-mask-source': command[command.index('/state/.bashrc')-1] = '/unrelated-private'
    elif mutation == 'journal-writable-target': command[command.index('/state/inspection-journal/1')] = '/state/canary/1'
    elif mutation == 'after-claude':
        triple = command[b-2:b+1]; del command[b-2:b+1]; command.extend(triple)
    elif mutation == 'duplicate-claude': command.append('/runtime/claude')
    elif mutation == 'wrong-user': command[2] = 'root'
    elif mutation == 'unconfined-prefix': command[4:4] = ['--unshare-cgroup']
    with pytest.raises(ValueError): canary.validate_canary_mounts(command, execution, SESSION, PROBE)


@pytest.mark.parametrize('probe', ['/', 'relative/probe', '/fixed/../probe', '/fixed//probe'])
def test_noncanonical_probe_refused(probe):
    command, execution = command_fixture()
    with pytest.raises(ValueError): canary.validate_canary_mounts(command, execution, SESSION, probe)


@pytest.mark.parametrize('preparation_only', [False, True])
@pytest.mark.parametrize('broken', [False, True])
def test_runner_checks_before_returning_prepared_or_launch_command(monkeypatch, preparation_only, broken):
    command, execution = command_fixture()
    # runtime.command provides the native prefix before the final probe overlay.
    i = command.index('/runtime/claude'); del command[i-3:i]
    if broken: command[command.index('/state/.bashrc')-2] = '--bind'
    observed = []
    def runtime_command(*args, **kwargs):
        observed.append(kwargs['preparation_only']); return command
    monkeypatch.setattr(runtime, 'command', runtime_command)
    monkeypatch.setattr(runner, 'read', lambda path: b'{}')
    monkeypatch.setattr(runner, '_canary_schema', lambda *args: {})
    manifest = {'session_id': SESSION}
    call = lambda: runner._canary_command(runtime.SESSION_ROOT/SESSION, manifest,
        {'execution': execution}, Path(PROBE), preparation_only=preparation_only)
    if broken:
        with pytest.raises(ValueError, match='CANARY_REACHABLE_SYNTHETIC_MOUNT'): call()
    else:
        assert call().count('/state/canary') == 2
    assert observed == [preparation_only]


def test_rebased_full_synthetic_original_verifier(tmp_path, monkeypatch):
    from inspection_confinement_fixtures import FIXTURE_PROFILE, FIXTURE_PROFILE_SHA
    monkeypatch.setattr(runtime, 'PROFILE_SHA256', FIXTURE_PROFILE_SHA)
    monkeypatch.setattr(runtime, 'PROFILE_BYTES', len(FIXTURE_PROFILE))
    bundle, expected = fixture(tmp_path, canary_directory=True)
    assert canary.verify_canary(bundle, expected)['status'] == 'PASSED'
