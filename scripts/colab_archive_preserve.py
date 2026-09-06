"""Verify opaque archive bytes and preserve a fresh Drive copy; never extract or dispatch."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import time

SIZE = 99014629647
MD5 = '36ae28b9a17f7340b8bbef62b595cb57'
LOCAL = Path('/content/isles-p001-input-16813698/train.7z')
DRIVE = Path('/content/drive')
PROJECT = DRIVE/'MyDrive/isles-pilot'
IDENTITY = PROJECT/'input-acquisition-16813698/identity.json'
OUTPUT = PROJECT/'P001-v1'


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def regular(path):
    return not path.is_symlink() and path.is_file()


def inspect(path, expected_size=SIZE, expected_md5=MD5):
    result = {'path': str(path), 'exists': path.exists(), 'size_bytes': None,
              'md5': None, 'matches': False, 'verified_at': utc()}
    if not regular(path):
        return result
    before = path.stat()
    result['size_bytes'] = before.st_size
    if before.st_size != expected_size:
        return result
    digest = hashlib.md5()
    # No bytes, filenames inside the archive, or patient values are emitted.
    with path.open('rb') as stream:
        while block := stream.read(8 << 20):
            digest.update(block)
    after = path.stat()
    result['md5'] = digest.hexdigest()
    result['stable_during_read'] = (before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns)
    result['matches'] = result['stable_during_read'] and result['md5'] == expected_md5
    result['verified_at'] = utc()
    return result


def copy_verified(source, destination, expected_size=SIZE, expected_md5=MD5):
    """Caller verified source. Exclusive destination; preserve partial files on failure."""
    with source.open('rb') as src, destination.open('xb') as dst:
        shutil.copyfileobj(src, dst, length=8 << 20)
        dst.flush()
        os.fsync(dst.fileno())
    result = inspect(destination, expected_size, expected_md5)
    if not result['matches']:
        raise ValueError('destination checksum failed; preserve original and partial copy')
    return result


def reconcile():
    """Only fixed project paths and aggregate filesystem/process metadata leave this function."""
    paths = {}
    for label, path in [('worker', Path(str(OUTPUT)+'.worker')), ('outputs', OUTPUT),
                        ('checkpoints', Path(str(OUTPUT)+'.private')),
                        ('console', Path(str(OUTPUT)+'.console.log'))]:
        item = {'path': str(path), 'exists': path.exists(), 'files': 0, 'bytes': 0, 'scan_complete': True}
        try:
            if regular(path):
                item.update(files=1, bytes=path.stat().st_size)
            elif path.is_dir() and not path.is_symlink():
                for directory, dirs, files in os.walk(path, followlinks=False):
                    dirs[:] = [d for d in dirs if not (Path(directory)/d).is_symlink()]
                    for name in files:
                        p = Path(directory)/name
                        if regular(p):
                            item['files'] += 1; item['bytes'] += p.stat().st_size
            elif path.is_symlink(): item['scan_complete'] = False
        except OSError: item['scan_complete'] = False
        paths[label] = item
    active = []; complete = True
    needles = [str(OUTPUT)+'.worker/run.py', '/experiments/P001/run.py']
    for p in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            command = p.read_bytes().replace(b'\0', b' ').decode(errors='replace')
            if any(n in command for n in needles): active.append(int(p.parent.name))
        except FileNotFoundError: pass  # process exited during enumeration
        except OSError: complete = False
    state = {'status_file_present': False, 'recorded_status': None, 'recorded_pid': None, 'recorded_pid_exists': None}
    worker = Path(str(OUTPUT)+'.worker')
    for name in ['status.json', 'process.json']:
        path = worker/name
        if regular(path) and path.stat().st_size <= 4096:
            try:
                value = json.loads(path.read_text())
                if name == 'status.json':
                    state['status_file_present'] = True
                    status = value.get('status')
                    state['recorded_status'] = status if status in ['STARTING','RUNNING','VALIDATED','FAILED'] else 'INVALID_STATUS'
                else:
                    pid = value.get('pid')
                    if type(pid) is int and pid > 0:
                        state['recorded_pid'] = pid; state['recorded_pid_exists'] = Path('/proc', str(pid)).exists()
            except (ValueError, AttributeError, OSError): state['metadata_parse_failed'] = True
    return {'paths': paths, 'worker_state': state, 'matching_process_pids': active, 'process_scan_complete': complete,
            'interpretation': 'Metadata observation only; recorded PID may be reused. No launch, resume, deletion or inference from NOT_VISIBLE.'}


def candidates():
    found = []; complete = True; start = time.monotonic()
    def error(_):
        nonlocal complete
        complete = False
    for root in [DRIVE/'MyDrive', DRIVE/'Shareddrives']:
        if not root.exists(): continue
        for directory, dirs, files in os.walk(root, followlinks=False, onerror=error):
            dirs[:] = [d for d in dirs if not (Path(directory)/d).is_symlink()]
            if time.monotonic()-start > 180 or len(found) >= 20:
                return found, False
            if 'train.7z' in files:
                path = Path(directory)/'train.7z'
                if regular(path): found.append(path)
    return found, complete


def run(job):
    os.umask(0o077)
    receipt = {'expected': {'size_bytes': SIZE, 'md5': MD5}, 'started_at': utc(),
               'status': 'VERIFYING', 'persistence_status': 'UNVERIFIED', 'dispatch_performed': False}
    def save():
        receipt['updated_at'] = utc()
        temporary = job/'receipt.tmp'
        temporary.write_text(json.dumps(receipt, indent=2))
        os.replace(temporary, job/'receipt.json')
    try:
        if not os.environ.get('COLAB_RELEASE_TAG') or shutil.which('nvidia-smi'):
            raise RuntimeError('CPU Colab required')
        if not os.path.ismount(DRIVE): raise RuntimeError('Drive mount required')
        receipt['acquisition_identity'] = {'path': str(IDENTITY), 'exists': regular(IDENTITY), 'expected_binding_matches': False}
        if regular(IDENTITY) and IDENTITY.stat().st_size <= 8192:
            raw = IDENTITY.read_bytes()
            receipt['acquisition_identity']['sha256'] = hashlib.sha256(raw).hexdigest()
            try:
                identity = json.loads(raw)
                receipt['acquisition_identity']['expected_binding_matches'] = identity.get('size_bytes') == SIZE and identity.get('md5') == MD5
            except (ValueError, AttributeError):
                receipt['acquisition_identity']['parse_failed'] = True
        receipt['p001'] = reconcile()
        save()
        receipt['local'] = inspect(LOCAL); receipt['local']['storage_type'] = 'runtime_local'
        save()
        receipt['status'] = 'CHECKING_DRIVE'; save()
        paths, complete = candidates()
        receipt['drive_scan_complete'] = complete
        receipt['drive_candidates'] = []
        for path in paths:
            result = inspect(path); result['storage_type'] = 'mounted_google_drive'
            receipt['drive_candidates'].append(result); save()
        matching = [r for r in receipt['drive_candidates'] if r['matches']]
        if matching:
            receipt['persistent_copy'] = matching[0]
            receipt['persistence_status'] = 'EXISTING_DRIVE_COPY_VERIFIED'
        else:
            if not receipt['local']['matches']: raise RuntimeError('no verified local source or persistent copy')
            if not complete: raise RuntimeError('Drive search incomplete; no copy made')
            usage = shutil.disk_usage(PROJECT)
            receipt['drive_capacity'] = {'reported_free_bytes': usage.free, 'required_bytes': SIZE+(1<<30),
                'measurement': 'mounted filesystem statvfs; not an independent provider-quota guarantee'}
            if usage.free < SIZE+(1<<30): raise RuntimeError('insufficient reported Drive capacity')
            receipt['status'] = 'COPYING_TO_DRIVE'; receipt['destination'] = str(job/'train.7z'); save()
            receipt['persistent_copy'] = copy_verified(LOCAL, job/'train.7z')
            receipt['persistent_copy']['storage_type'] = 'mounted_google_drive'
            receipt['persistence_status'] = 'FRESH_DRIVE_COPY_VERIFIED'
        receipt['p001_after'] = reconcile()
        receipt['status'] = 'VERIFIED'
    except BaseException as error:
        receipt['status'] = 'BLOCKED_OR_FAILED'
        receipt['failure_type'] = type(error).__name__
        # Exception text/tracebacks stay in the private console, not the public receipt.
        import traceback
        traceback.print_exc()
    finally:
        save()


if __name__ == '__main__':
    import sys
    run(Path(sys.argv[1]))
