"""Capture original Git stderr privately before returning or raising.

No retries or admission semantics live here. Exceptions expose an opaque local
receipt ID, never arguments, stdout or stderr. Configure RESEARCH_GIT_DIAGNOSTICS
outside Git for durable hosted retention; the supervised default is private /tmp.
The private directory must belong to the current identity and have mode 0700.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import time


def _root():
    path = Path(os.environ.get('RESEARCH_GIT_DIAGNOSTICS',
                             '/tmp/research-git-diagnostics-' + str(os.getuid())))
    if not path.is_absolute() or path.is_symlink():
        raise ValueError('PRIVATE_GIT_DIAGNOSTICS_PATH_REJECTED')
    path.mkdir(mode=0o700, parents=False, exist_ok=True)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise ValueError('PRIVATE_GIT_DIAGNOSTICS_PERMISSIONS_REJECTED')
    resolved = path.resolve()
    if any((parent / '.git').is_file() or (parent / '.git' / 'HEAD').is_file()
           for parent in (resolved, *resolved.parents)):
        raise ValueError('PRIVATE_GIT_DIAGNOSTICS_INSIDE_CHECKOUT')
    return resolved


def run(args, *, cwd=None, input=None, text=False, capture_output=False,
        check=False, timeout=None, **kwargs):
    """Compatible subset used by ledger, publication and provenance transports.

    Both streams are captured; stdout remains available to the caller. Stderr is
    available only in the private receipt, including check=False and timeouts.
    """
    if any(key in kwargs for key in ('stdout', 'stderr', 'shell')):
        raise ValueError('PRIVATE_GIT_CAPTURE_OVERRIDE_REJECTED')
    directory = Path(tempfile.mkdtemp(prefix='git-', dir=_root()))
    started = time.time()
    metadata = {'schema': 1, 'started_epoch': started,
                'argv_sha256': hashlib.sha256(json.dumps(list(args)).encode()).hexdigest()}
    result = None
    failure = None
    with (directory / 'stderr').open('xb') as stderr:
        os.chmod(directory / 'stderr', 0o600)
        try:
            result = subprocess.run(args, cwd=cwd, input=input, text=text,
                                    stdout=subprocess.PIPE, stderr=stderr,
                                    check=False, timeout=timeout, **kwargs)
            metadata['returncode'] = result.returncode
        except subprocess.TimeoutExpired:
            failure = 'TIMEOUT'
        except OSError:
            failure = 'PROCESS_START_FAILED'
        finally:
            stderr.flush()
            os.fsync(stderr.fileno())
    metadata.update({'elapsed_seconds': time.time() - started, 'failure': failure,
                     'stderr_sha256': hashlib.sha256((directory / 'stderr').read_bytes()).hexdigest()})
    with (directory / 'receipt.json').open('x') as out:
        os.chmod(directory / 'receipt.json', 0o600)
        json.dump(metadata, out)
        out.flush()
        os.fsync(out.fileno())
    safe_command = ['git', 'PRIVATE_DIAGNOSTIC=' + directory.name]
    if failure == 'TIMEOUT':
        raise subprocess.TimeoutExpired(safe_command, timeout) from None
    if failure:
        raise RuntimeError('GIT_PROCESS_START_FAILED ' + directory.name) from None
    if check and result.returncode:
        raise subprocess.CalledProcessError(result.returncode, safe_command) from None
    result.stderr = '' if text else b''
    return result


def output(args, *, cwd=None, **kwargs):
    return run(args, cwd=cwd, check=True, **kwargs).stdout
