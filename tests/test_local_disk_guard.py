import json
from types import SimpleNamespace
import subprocess
import pytest
from tools import local_disk_guard as guard


@pytest.mark.parametrize('volume', ['windows_c', 'wsl'])
@pytest.mark.parametrize('free,status', [
    (0, 'STOP'), (8*guard.GIB-1, 'STOP'), (8*guard.GIB, 'WARN'),
    (15*guard.GIB-1, 'WARN'), (15*guard.GIB, 'OK')])
def test_either_real_filesystem_controls_admission(volume, free, status):
    values = {'windows_c': 800*guard.GIB, 'wsl': 800*guard.GIB}
    values[volume] = free
    result = guard.assess(values['windows_c'], values['wsl'])
    assert result['status'] == status
    assert result['proceed'] == (status != 'STOP')


@pytest.mark.parametrize('invalid', [None, True, -1, 8.0, '9000000000'])
def test_invalid_probe_values_never_pass(invalid):
    with pytest.raises(ValueError):
        guard.assess(invalid, 100*guard.GIB)


def test_windows_uses_actual_windows_drive_query(monkeypatch):
    captured = {}
    def run(argv, **kwargs):
        captured.update(argv=argv, **kwargs)
        return SimpleNamespace(stdout=b'15000000000\r\n', stderr=b'')
    monkeypatch.setattr(guard.subprocess, 'run', run)
    assert guard.windows_c_available() == 15000000000
    assert captured['argv'] == [guard.POWERSHELL, '-NoProfile', '-NonInteractive',
                                '-Command', "[System.IO.DriveInfo]::new('C:\\').AvailableFreeSpace"]
    assert captured['timeout'] == 15 and captured['check'] is True
    assert captured['capture_output'] is True
    assert captured['cwd'] == '/mnt/c'  # Windows executable must not inherit a long Linux-only cwd


@pytest.mark.parametrize('stdout,stderr', [(b'', b''), (b'error123', b''),
                                          (b'-1', b''), (b'123', b'error')])
def test_malformed_windows_output_fails_closed(monkeypatch, stdout, stderr):
    monkeypatch.setattr(guard.subprocess, 'run', lambda *a, **k:
                        SimpleNamespace(stdout=stdout, stderr=stderr))
    with pytest.raises(ValueError): guard.windows_c_available()


def test_wsl_available_not_total_or_root_reserved(monkeypatch, tmp_path):
    monkeypatch.setattr(guard.os, 'statvfs', lambda p:
        SimpleNamespace(f_bavail=7, f_bfree=999, f_blocks=99999, f_frsize=4096))
    assert guard.wsl_available(tmp_path) == 7*4096


@pytest.mark.parametrize('failure', [OSError('private path'),
    subprocess.TimeoutExpired('private command', 15), ValueError('private data')])
def test_unknown_blocks_even_when_other_volume_is_large(monkeypatch, failure, capsys):
    def fail(): raise failure
    monkeypatch.setattr(guard, 'windows_c_available', fail)
    monkeypatch.setattr(guard, 'wsl_available', lambda path: 1000*guard.GIB)
    assert guard.main([]) == 3
    text = capsys.readouterr()
    result = json.loads(text.out)
    assert result['status'] == 'UNKNOWN' and result['proceed'] is False
    assert 'private' not in text.out + text.err


def test_wsl_unknown_blocks(monkeypatch):
    monkeypatch.setattr(guard, 'windows_c_available', lambda: 100*guard.GIB)
    def fail(path): raise FileNotFoundError('private path')
    monkeypatch.setattr(guard, 'wsl_available', fail)
    assert guard.check('/unavailable')['status'] == 'UNKNOWN'


@pytest.mark.parametrize('free,code,status', [(7*guard.GIB,2,'STOP'),
    (10*guard.GIB,0,'WARN'), (16*guard.GIB,0,'OK')])
def test_cli_exit_code_is_usable_before_large_step(monkeypatch, capsys, free, code, status):
    monkeypatch.setattr(guard, 'windows_c_available', lambda: free)
    monkeypatch.setattr(guard, 'wsl_available', lambda path: 1000*guard.GIB)
    assert guard.main([]) == code
    text = capsys.readouterr()
    assert json.loads(text.out)['status'] == status
    assert bool(text.err) == (status != 'OK')
