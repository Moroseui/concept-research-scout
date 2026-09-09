"""Private extraction of the complete frozen P001 return; no scientific validation.

Only local files are read. The original ZIP and terminal receipt stay unchanged.
The trusted caller supplies the launch request/runtime binding and an operational
expansion cap. Presence of a return is not launch or transfer authorization.
After extraction, invoke the emitted unchanged frozen validator arguments.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import struct
import subprocess
import sys
import zipfile
import zlib

from orchestrator.p001_runtime_intake import EXECUTION_PIN, SOURCE_PIN, NOTEBOOK_PIN
from orchestrator.p001_runtime_setup import frozen_sources

TRANSFER_CAP = 32 * 1024 * 1024
RECEIPT_CAP = 16 * 1024
MEMBER_COUNT = 206
DIRECTORY_CAP = 64 * 1024
DISK_RESERVE = 256 * 1024 * 1024
AGGREGATES = ['summary.json', 'resolved_config.json', 'environment.json', 'execution_receipt.json', 'RESULT_CARD.md']
ROOT = Path(__file__).resolve().parents[1]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def private_write(path, value):
    with path.open('xb') as handle:
        os.chmod(handle.name, 0o600)
        handle.write(canonical(value) + b'\n')
        handle.flush()
        os.fsync(handle.fileno())


def regular_file(path):
    path = Path(path).absolute()
    for parent in reversed(path.parents):
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise ValueError('P001_RETURN_PATH_ANCESTOR')
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError('P001_RETURN_REGULAR_FILE_REQUIRED')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    handle = os.fdopen(fd, 'rb')
    after = os.fstat(handle.fileno())
    if not stat.S_ISREG(after.st_mode) or stat_identity(after) != stat_identity(before):
        handle.close()
        raise ValueError('P001_RETURN_FILE_CHANGED_BEFORE_OPEN')
    return handle


def stat_identity(value):
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def file_identity(handle):
    return stat_identity(os.fstat(handle.fileno()))


def hash_stream(handle):
    handle.seek(0)
    hashed = hashlib.sha256()
    for block in iter(lambda: handle.read(1 << 20), b''):
        hashed.update(block)
    handle.seek(0)
    return hashed.hexdigest()


def terminal_receipt(raw, *, request_id, runtime_fingerprint, launch_manifest_sha256, max_extracted_bytes):
    """A bounded transfer identity, never a substitute for the frozen validator."""
    if not 0 < len(raw) <= RECEIPT_CAP:
        raise ValueError('P001_RETURN_TERMINAL_RECEIPT_BOUND')
    try:
        def unique_fields(pairs):
            value = {}
            for key, item in pairs:
                if key in value:
                    raise ValueError('duplicate receipt key')
                value[key] = item
            return value
        value = json.loads(raw, object_pairs_hook=unique_fields)
    except (UnicodeDecodeError, ValueError):
        raise ValueError('P001_RETURN_TERMINAL_RECEIPT_SCHEMA') from None
    required = {'schema', 'request_id', 'runtime_fingerprint_sha256', 'worker_status',
                'execution_snapshot', 'source_pin', 'notebook_pin', 'zip_name', 'zip_bytes', 'zip_sha256',
                'launch_manifest_sha256', 'max_extracted_bytes'}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError('P001_RETURN_TERMINAL_RECEIPT_SCHEMA')
    expected = {'schema': 'p001-full-return-terminal/v1', 'request_id': request_id,
                'runtime_fingerprint_sha256': runtime_fingerprint, 'worker_status': 'VALIDATED',
                'execution_snapshot': EXECUTION_PIN, 'source_pin': SOURCE_PIN, 'notebook_pin': NOTEBOOK_PIN,
                'zip_name': 'P001-private-return.zip', 'launch_manifest_sha256': launch_manifest_sha256,
                'max_extracted_bytes': max_extracted_bytes}
    if any(value.get(key) != item for key, item in expected.items()):
        raise ValueError('P001_RETURN_TERMINAL_BINDING')
    if (type(value['max_extracted_bytes']) is not int or type(value['zip_bytes']) is not int or not 0 < value['zip_bytes'] <= TRANSFER_CAP or
            not isinstance(value['zip_sha256'], str) or not re.fullmatch('[0-9a-f]{64}', value['zip_sha256'])):
        raise ValueError('P001_RETURN_TERMINAL_RECEIPT_SCHEMA')
    return value


def expected_members(snapshot):
    """Use the frozen selection function; emit no cohort identity to model tools."""
    frozen_sources(snapshot)  # Existing full scientific/adapter review, no model call.
    script = """import importlib.util,json,sys
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root))
p=root/'campaigns/isles24-pilot/experiments/P001/run.py'
spec=importlib.util.spec_from_file_location('frozen_p001_return_selection',p)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
print(json.dumps(sorted(module.selection())))
"""
    result = subprocess.run([sys.executable, '-B', '-I', '-c', script, str(snapshot)],
                            cwd=Path(snapshot).parent, capture_output=True, timeout=60)
    if result.returncode or len(result.stdout) > 16384:
        raise ValueError('P001_RETURN_FROZEN_SELECTION_UNAVAILABLE')
    try:
        cases = json.loads(result.stdout)
    except (UnicodeDecodeError, ValueError):
        raise ValueError('P001_RETURN_FROZEN_SELECTION_SCHEMA') from None
    if (not isinstance(cases, list) or len(cases) != 99 or
            any(not isinstance(case, str) or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_-]{0,63}', case) for case in cases) or len(set(cases)) != 99):
        raise ValueError('P001_RETURN_FROZEN_SELECTION_SCHEMA')
    members = {'bundle/' + name for name in AGGREGATES} | {'console.log', 'private/binding.json', 'private/checkpoint_index.json'}
    members.update('private/checkpoints/' + case + '.json' for case in cases)
    members.update('private/predictions/' + case + '.npy' for case in cases)
    if len(members) != MEMBER_COUNT:
        raise ValueError('P001_RETURN_EXPECTED_MEMBER_COUNT')
    return members


def check_directory(handle, archive_bytes):
    """Bound central-directory allocation before the standard ZIP reader parses it.

    The frozen writer emits no archive comment, multipart archive or ZIP64 end
    record (206 members and a compressed size below 32 MiB). Member ZIP64 sizes
    remain supported and are checked against the explicit expansion cap.
    """
    if archive_bytes < 22:
        raise ValueError('P001_RETURN_ZIP_DIRECTORY')
    handle.seek(archive_bytes - 22)
    end = handle.read(22)
    try:
        signature, disk, start_disk, disk_count, count, size, offset, comment = struct.unpack('<4s4H2LH', end)
    except struct.error:
        raise ValueError('P001_RETURN_ZIP_DIRECTORY') from None
    if (signature != b'PK\x05\x06' or disk or start_disk or comment or
            disk_count != MEMBER_COUNT or count != MEMBER_COUNT or
            not 0 < size <= DIRECTORY_CAP or offset + size != archive_bytes - 22):
        raise ValueError('P001_RETURN_ZIP_DIRECTORY')
    handle.seek(0)
    if handle.read(4) != b'PK\x03\x04':
        raise ValueError('P001_RETURN_ZIP_DIRECTORY')
    handle.seek(0)


def inspect_members(archive, expected, max_extracted_bytes):
    infos = archive.infolist()
    if len(infos) != MEMBER_COUNT or len({info.filename for info in infos}) != MEMBER_COUNT:
        raise ValueError('P001_RETURN_MEMBER_SET')
    if {info.filename for info in infos} != expected:
        raise ValueError('P001_RETURN_MEMBER_SET')
    total = 0
    for info in infos:
        path = PurePosixPath(info.filename)
        mode = info.external_attr >> 16
        if (info.orig_filename != info.filename or len(info.filename.encode()) > 128 or
                path.is_absolute() or '..' in path.parts or '\\' in info.filename or
                info.is_dir() or stat.S_IFMT(mode) not in (0, stat.S_IFREG) or
                info.external_attr & 0x10 or info.flag_bits & 1 or info.comment or len(info.extra) > 64 or
                info.compress_type != zipfile.ZIP_DEFLATED):
            raise ValueError('P001_RETURN_MEMBER_TYPE_OR_PATH')
        if info.file_size < 0 or info.compress_size < 0:
            raise ValueError('P001_RETURN_MEMBER_SIZE')
        total += info.file_size
        if total > max_extracted_bytes:
            raise ValueError('P001_RETURN_EXPANSION_CAP')
    return infos, total


def destination_ready(destination, snapshot, required_bytes):
    destination = Path(destination).absolute()
    for parent in reversed(destination.parents):
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise ValueError('P001_RETURN_DESTINATION_ANCESTOR')
    if destination.is_relative_to(ROOT.resolve()) or destination.is_relative_to(Path(snapshot).resolve()):
        raise ValueError('P001_RETURN_DESTINATION_MUST_BE_PRIVATE_OUTSIDE_SOURCE')
    try:
        destination.lstat()
    except FileNotFoundError:
        pass
    else:
        raise ValueError('P001_RETURN_EXISTING_DESTINATION_RECONCILE')
    if destination.parent.stat().st_mode & 0o077:
        raise ValueError('P001_RETURN_PRIVATE_PARENT_REQUIRED')
    if shutil.disk_usage(destination.parent).free < required_bytes + DISK_RESERVE:
        raise ValueError('P001_RETURN_DISK_CAPACITY')
    return destination


def extract(zip_path, terminal_path, destination, snapshot, *, request_id,
            runtime_fingerprint, launch_manifest_sha256, max_extracted_bytes):
    """Extract exact members; preserve partial outcomes and never call science here."""
    if not isinstance(request_id, str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}', request_id):
        raise ValueError('P001_RETURN_REQUEST_ID')
    if not isinstance(runtime_fingerprint, str) or not re.fullmatch('[0-9a-f]{64}', runtime_fingerprint):
        raise ValueError('P001_RETURN_RUNTIME_IDENTITY')
    if not isinstance(launch_manifest_sha256, str) or not re.fullmatch('[0-9a-f]{64}', launch_manifest_sha256):
        raise ValueError('P001_RETURN_LAUNCH_MANIFEST_BINDING')
    if type(max_extracted_bytes) is not int or not 0 < max_extracted_bytes < 2**63:
        raise ValueError('P001_RETURN_EXPLICIT_EXPANSION_CAP_REQUIRED')
    expected = expected_members(snapshot)
    with regular_file(terminal_path) as terminal, regular_file(zip_path) as original:
        terminal_before, zip_before = file_identity(terminal), file_identity(original)
        if terminal_before[2] > RECEIPT_CAP or zip_before[2] + terminal_before[2] > TRANSFER_CAP:
            raise ValueError('P001_RETURN_COMBINED_TRANSFER_CAP')
        raw_receipt = terminal.read(RECEIPT_CAP + 1)
        binding = terminal_receipt(raw_receipt, request_id=request_id, runtime_fingerprint=runtime_fingerprint,
                                   launch_manifest_sha256=launch_manifest_sha256, max_extracted_bytes=max_extracted_bytes)
        if binding['zip_bytes'] != zip_before[2] or hash_stream(original) != binding['zip_sha256']:
            raise ValueError('P001_RETURN_ORIGINAL_ZIP_BINDING')
        check_directory(original, zip_before[2])
        destination = None if destination is None else Path(destination)
        claimed = False
        try:
            with zipfile.ZipFile(original) as archive:
                infos, declared = inspect_members(archive, expected, max_extracted_bytes)
                destination = destination_ready(destination, snapshot, declared + 65536)
                os.umask(0o077)
                destination.mkdir(mode=0o700)
                claimed = True
                private_write(destination / 'intake-intent.json', {
                    'schema': 'p001-full-return-intake-intent/v1', 'request_id': request_id,
                    'zip_sha256': binding['zip_sha256'], 'terminal_sha256': digest(raw_receipt),
                    'runtime_fingerprint_sha256': runtime_fingerprint, 'launch_manifest_sha256': launch_manifest_sha256,
                    'max_extracted_bytes': max_extracted_bytes,
                    'declared_extracted_bytes': declared, 'scientific_acceptance': False})
                inventory = {}
                written_total = 0
                for info in infos:
                    path = destination / info.filename
                    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                    hashed = hashlib.sha256()
                    written = 0
                    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                    with os.fdopen(fd, 'wb') as target, archive.open(info) as source:
                        for block in iter(lambda: source.read(1 << 20), b''):
                            written += len(block)
                            written_total += len(block)
                            if written > info.file_size or written_total > max_extracted_bytes:
                                raise ValueError('P001_RETURN_ACTUAL_EXPANSION_CAP')
                            target.write(block)
                            hashed.update(block)
                        target.flush()
                        os.fsync(target.fileno())
                    if written != info.file_size:
                        raise ValueError('P001_RETURN_MEMBER_SIZE_CHANGED')
                    inventory[info.filename] = {'bytes': written, 'sha256': hashed.hexdigest()}
                if written_total != declared:
                    raise ValueError('P001_RETURN_TOTAL_SIZE_CHANGED')
            if (file_identity(original) != zip_before or file_identity(terminal) != terminal_before or
                    hash_stream(original) != binding['zip_sha256'] or hash_stream(terminal) != digest(raw_receipt)):
                raise ValueError('P001_RETURN_ORIGINAL_CHANGED_DURING_EXTRACTION')
            private_write(destination / 'member-inventory.private.json', inventory)
            arguments = [sys.executable, str(Path(snapshot).absolute() / 'campaigns/isles24-pilot/experiments/P001/validate_return.py'),
                         '--bundle', str(destination / 'bundle'), '--private', str(destination / 'private'),
                         '--console', str(destination / 'console.log')]
            result = {'schema': 'p001-full-return-intake/v1', 'status': 'EXTRACTED_PENDING_FROZEN_VALIDATION',
                      'request_id': request_id, 'zip_sha256': binding['zip_sha256'],
                      'terminal_sha256': digest(raw_receipt), 'combined_transfer_bytes': zip_before[2] + terminal_before[2],
                      'member_count': MEMBER_COUNT, 'extracted_bytes': written_total,
                      'max_extracted_bytes': max_extracted_bytes, 'member_inventory_sha256': digest(canonical(inventory)),
                      'execution_snapshot': EXECUTION_PIN, 'source_pin': SOURCE_PIN, 'notebook_pin': NOTEBOOK_PIN,
                      'runtime_fingerprint_sha256': runtime_fingerprint, 'launch_manifest_sha256': launch_manifest_sha256,
                      'originals_preserved': True,
                      'validation_argv': arguments, 'validation_executed': False, 'scientific_acceptance': False,
                      'transfer_authority_granted_by_intake': False}
            private_write(destination / 'intake-receipt.json', result)
            return result
        except Exception as error:
            if claimed:
                code = str(error) if isinstance(error, ValueError) and re.fullmatch('P001_RETURN_[A-Z_]+', str(error)) else 'P001_RETURN_EXTRACTION_FAILED'
                private_write(destination / 'intake-failure.json', {'status': 'PRESERVED_PARTIAL_INTAKE_RECONCILE',
                    'failure_code': code, 'exception_type': type(error).__name__, 'scientific_acceptance': False})
            if isinstance(error, (zipfile.BadZipFile, zlib.error, EOFError, RuntimeError, NotImplementedError)):
                raise ValueError('P001_RETURN_ZIP_INVALID_OR_UNSUPPORTED') from None
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', dest='zip_path', type=Path, required=True)
    parser.add_argument('--terminal-receipt', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--frozen-snapshot', type=Path, required=True)
    parser.add_argument('--request-id', required=True)
    parser.add_argument('--runtime-fingerprint', required=True)
    parser.add_argument('--launch-manifest-sha256', required=True)
    parser.add_argument('--max-extracted-bytes', type=int, required=True)
    args = parser.parse_args()
    try:
        value = extract(args.zip_path, args.terminal_receipt, args.destination, args.frozen_snapshot,
                        request_id=args.request_id, runtime_fingerprint=args.runtime_fingerprint,
                        launch_manifest_sha256=args.launch_manifest_sha256, max_extracted_bytes=args.max_extracted_bytes)
    except Exception as error:
        code = str(error) if isinstance(error, ValueError) and re.fullmatch('P001_RETURN_[A-Z_]+', str(error)) else 'P001_RETURN_INTAKE_FAILED_PRIVATE_STATE_PRESERVED'
        print(json.dumps({'status': 'BLOCKED_RECONCILE', 'failure_code': code,
                          'exception_type': type(error).__name__, 'scientific_acceptance': False}))
        raise SystemExit(1) from None
    print(json.dumps({key: value[key] for key in ['status', 'member_count', 'combined_transfer_bytes',
        'extracted_bytes', 'originals_preserved', 'validation_executed', 'scientific_acceptance']}))


if __name__ == '__main__':
    main()
