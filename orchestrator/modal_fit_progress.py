"""Durable, per-fit progress for the reviewed Modal nnU-Net worker.

One writer holds a fit lock for the complete worker lifetime. Immutable objects
and receipts precede the replaceable navigation pointer. No credentials, SDK,
training admission or automatic retry lives here. Modal Volume v2 is required:
its mountpoint sync commits data without giving the worker an API credential.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

from orchestrator import private_records


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def file_hash(path):
    result = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}', value):
        raise ValueError('FIT_IDENTIFIER')
    return value


def volume_commit(mount):
    """Commit an authenticated v2 mount using its mountpoint fsync operation.

    This is the same Linux operation as ``sync MOUNT`` without -f/-d. Use the
    already-pinned Python, so a minimal worker does not need an extra executable.
    Keep the bounded child process: a failed or stuck commit never succeeds.
    """
    script = ("import os,sys\n"
              "fd=os.open(sys.argv[1], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)\n"
              "try: os.fsync(fd)\n"
              "finally: os.close(fd)\n")
    subprocess.run([sys.executable, '-I', '-B', '-c', script, str(mount)],
                   check=True, timeout=120)


def validate_binding(binding):
    if not isinstance(binding, dict) or set(binding) != {
        'run_id', 'arm', 'fold', 'realization', 'spec_sha256', 'code_sha256',
        'input_contract_sha256', 'environment_sha256', 'plans_sha256'}:
        raise ValueError('FIT_BINDING_FIELDS')
    for key in ('run_id', 'arm', 'realization'):
        identifier(binding[key])
    if type(binding['fold']) is not int or not 0 <= binding['fold'] <= 98:
        raise ValueError('FIT_FOLD')
    for key, value in binding.items():
        if key.endswith('_sha256') and (not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value)):
            raise ValueError('FIT_BINDING_HASH')
    return binding


class FitProgress:
    def __init__(self, mount, fit, binding, *, commit=volume_commit):
        self.mount = Path(mount).absolute()
        private_records.check(self.mount)
        self.root = self.mount / 'fits' / identifier(fit)
        self.binding = binding
        validate_binding(binding)
        self.binding_sha256 = hashlib.sha256(encoded(binding)).hexdigest()
        self.commit = commit
        self.locked = False

    @contextmanager
    def writer(self, *, initial):
        """A RESUME can never create a new fit or fall back to fresh training."""
        if type(initial) is not bool:
            raise ValueError('FIT_INITIAL_BOOLEAN')
        if initial:
            private_records.mkdir(self.root, parents=True)
        elif not self.root.is_dir():
            raise ValueError('FIT_RESUME_MISSING')
        private_records.check(self.root)
        lock = self.root / '.writer.lock'
        if not initial and not lock.is_file():
            raise ValueError('FIT_LOCK_MISSING')
        with private_records.open_file(lock, 'ab') as stream:
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError('FIT_WRITER_ACTIVE') from None
            try:
                self.locked = True
                identity = self.root / 'identity.json'
                if initial:
                    self._new(identity, {'schema': 'modal-fit/v1', 'binding': self.binding})
                    private_records.mkdir(self.root / 'objects')
                    private_records.mkdir(self.root / 'receipts')
                    self.commit(self.mount)
                else:
                    private_records.check(identity)
                    if json.loads(identity.read_bytes()) != {'schema': 'modal-fit/v1', 'binding': self.binding}:
                        raise ValueError('FIT_IDENTITY_CHANGED')
                yield self
            finally:
                self.locked = False
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def _guard(self):
        if not self.locked:
            raise ValueError('FIT_WRITER_LOCK_REQUIRED')

    def _new(self, path, value):
        with private_records.open_file(path, 'xb') as out:
            out.write(encoded(value)); out.flush(); os.fsync(out.fileno())

    def publish(self, key, write, *, metadata):
        """write(path) finishes one checkpoint or preprocessing/scoring artifact.

        A killed/failed write leaves its unpublished object intact for diagnosis;
        it cannot replace the last verified object. A commit error stops work.
        """
        self._guard(); identifier(key)
        token = uuid.uuid4().hex
        folder = self.root / 'objects' / token
        private_records.mkdir(folder)
        data = folder / 'data'
        # Reserve a private regular file before the native writer opens it.
        with private_records.open_file(data, 'xb'):
            pass
        with private_records.umask():
            write(data)
        private_records.check(data)
        with data.open('rb') as stream:
            os.fsync(stream.fileno())
        record = {'schema': 'modal-fit-object/v1', 'key': key,
                  'binding_sha256': self.binding_sha256, 'object': token,
                  'sha256': file_hash(data), 'bytes': data.stat().st_size,
                  'metadata': metadata, 'at_utc': utc()}
        if record['bytes'] == 0:
            raise ValueError('FIT_EMPTY_OBJECT')
        self._new(folder / 'record.json', record)
        self.commit(self.mount)  # Data and its hash exist durably before pointer.
        private_records.atomic(self.root / (key + '.json'), record)
        self.commit(self.mount)  # Explicitly persist the new navigation pointer.
        return record

    def select(self, key):
        self._guard(); identifier(key)
        pointer = self.root / (key + '.json')
        if not pointer.exists():
            raise ValueError('FIT_PROGRESS_MISSING')
        private_records.check(pointer)
        record = json.loads(pointer.read_bytes())
        if not isinstance(record, dict) or set(record) != {
            'schema', 'key', 'binding_sha256', 'object', 'sha256', 'bytes', 'metadata', 'at_utc'}:
            raise ValueError('FIT_PROGRESS_SCHEMA')
        if (record['schema'] != 'modal-fit-object/v1' or record['key'] != key or
                record['binding_sha256'] != self.binding_sha256 or
                not isinstance(record['object'], str) or not re.fullmatch('[0-9a-f]{32}', record['object'])):
            raise ValueError('FIT_PROGRESS_BINDING')
        folder = self.root / 'objects' / record['object']
        private_records.check(folder / 'record.json')
        if json.loads((folder / 'record.json').read_bytes()) != record:
            raise ValueError('FIT_PROGRESS_RECORD_CHANGED')
        data = folder / 'data'; private_records.check(data)
        if data.stat().st_size != record['bytes'] or file_hash(data) != record['sha256']:
            raise ValueError('FIT_PROGRESS_HASH_CHANGED')
        return data, record

    def training_log(self, path, *, segment):
        """Commit the native log location once per segment, without copying it.

        The trainer creates this log under the same fit's work directory. A
        controller never guesses a filename or reads another fit's log.
        """
        self._guard()
        if type(segment) is not int or segment < 1:
            raise ValueError('FIT_LOG_SEGMENT')
        path = Path(path)
        if (not path.is_absolute() or not path.is_relative_to(self.root/'work')
                or '..' in path.parts or not re.fullmatch(r'training_log_[0-9_]+\.txt',path.name)):
            raise ValueError('FIT_LOG_PATH')
        private_records.check(path)
        if not path.is_file(): raise ValueError('FIT_LOG_FILE_REQUIRED')
        value = {'schema':'modal-fit-log/v1', 'binding_sha256':self.binding_sha256,
                 'segment':segment, 'path':'/'+path.relative_to(self.mount).as_posix()}
        self._new(self.root/('training-log-'+str(segment)+'.json'), value)
        self.commit(self.mount)
        return value

    def receipt(self, kind, detail):
        self._guard(); identifier(kind)
        value = {'schema': 'modal-fit-event/v1', 'kind': kind,
                 'binding_sha256': self.binding_sha256, 'at_utc': utc(), 'detail': detail}
        path = self.root / 'receipts' / (uuid.uuid4().hex + '.json')
        self._new(path, value); self.commit(self.mount)
        return value
