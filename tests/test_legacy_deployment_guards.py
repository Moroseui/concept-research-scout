"""No administrator action is executed: only guarded refusal/fresh checks."""
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT/'deploy/research-system'
INSTALLERS = ['install_release', 'install_handover_fixture', 'update_consumed_handover_fixture',
              'install_live_handover', 'install_drive_connector']


def load(name, monkeypatch):
    monkeypatch.syspath_prepend(str(DIRECTORY))
    spec = importlib.util.spec_from_file_location('guard_test_'+name, DIRECTORY/(name+'.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('name', INSTALLERS)
def test_fresh_preparation_allowed_but_existing_or_broken_live_marker_refuses(tmp_path, monkeypatch, name):
    module = load(name, monkeypatch)
    monkeypatch.setattr(module, 'Path', lambda value: tmp_path if str(value) == '/etc/research-system/live-research' else Path(value))
    assert module.refuse_existing_live_installation() is None
    marker = tmp_path/'controller.json'; marker.write_text('{}')
    with pytest.raises(ValueError, match='EXISTING_LIVE_INSTALLATION_REQUIRES_REVIEWED_DEPLOYMENT'):
        module.refuse_existing_live_installation()
    marker.unlink(); marker.symlink_to(tmp_path/'absent-target')
    with pytest.raises(ValueError, match='EXISTING_LIVE_INSTALLATION_REQUIRES_REVIEWED_DEPLOYMENT'):
        module.refuse_existing_live_installation()


@pytest.mark.parametrize('name', INSTALLERS)
def test_material_entry_point_checks_before_subprocess_or_file_mutation(monkeypatch, name):
    module = load(name, monkeypatch)
    def guard(): raise ValueError('SYNTHETIC_GUARD_REACHED')
    monkeypatch.setattr(module, 'refuse_existing_live_installation', guard)
    monkeypatch.setattr(module.os, 'getuid', lambda: 0)
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: pytest.fail('subprocess before guard'))
    monkeypatch.setattr(subprocess, 'check_output', lambda *a, **k: pytest.fail('subprocess before guard'))
    with pytest.raises(ValueError, match='SYNTHETIC_GUARD_REACHED'):
        if name == 'install_release':
            monkeypatch.setattr(sys, 'argv', ['install_release.py', '--source', 'a'*40]); module.main()
        elif name == 'install_handover_fixture': module.install('a'*40, 'unused', 'b'*64)
        elif name == 'update_consumed_handover_fixture': module.update('a'*40, 'b'*40, 'unused', 'c'*64)
        elif name == 'install_live_handover': module.install()
        else: module.install('unused', 'a'*40, 'unused', 'unused', 'unused')


def test_bootstrap_guard_without_executing_bootstrap(tmp_path):
    source = (DIRECTORY/'bootstrap.sh').read_text()
    start = source.index('refuse_existing_live_installation() {')
    end = source.index('\n}\n', start)+3
    function = source[start:end].replace('/etc/research-system/live-research', str(tmp_path))
    # Run only the exact small guard function with a fixture path: no root check,
    # apt, npm, account, firewall or service command is included in this input.
    command = function+'\nrefuse_existing_live_installation\n'
    clean = subprocess.run(['bash', '-c', command], capture_output=True, text=True)
    assert clean.returncode == 0
    (tmp_path/'broker.json').write_text('{}')
    refused = subprocess.run(['bash', '-c', command], capture_output=True, text=True)
    assert refused.returncode != 0
    assert 'EXISTING_LIVE_INSTALLATION_REQUIRES_REVIEWED_DEPLOYMENT' in refused.stderr
    subprocess.run(['bash', '-n', str(DIRECTORY/'bootstrap.sh')], check=True)
