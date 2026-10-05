"""Protected per-original-event reservation for the fixed investigator template.

The existing broker runs one fixed validator as its controller UID. Its pipe
supports only original evidence reads, avoiding a root broker self-socket call.
No process, model, configuration path or verifier is selected by request data.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
import selectors
import sqlite3
import stat
import subprocess
import sys
import time

from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded
from orchestrator import investigator_wakes as wakes

OPERATIONS = frozenset(('reserve_investigator', 'read_investigator_wake',
                       'list_recorded_steering', 'read_recorded_steering', 'stage_failure', 'stage_input_refusal'))


def message(value):
    """One bounded JSON line; persisted original-file encoding stays unchanged."""
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()+b'\n'


def stage_failure(broker, body):
    """Read an ended, unvalidated attempt; never infer a scientific outcome."""
    if set(body) != {'event'}: raise ValueError('STAGE_FAILURE_SCHEMA')
    packet = broker.stage_packet(body)
    if packet.get('status') != 'COMPLETE': return {'status':'ORIGINAL_PACKET_UNAVAILABLE_NO_RETRY'}
    event = body['event']; root = Path(broker.config['turn_root'])
    folder = root/(event['turn_id']+'-'+event['attempt'])
    gate = root/'branch.lock'
    if gate.is_symlink() or not gate.is_file(): raise ValueError('MODEL_WRITER_LOCK_ORIGINAL_REQUIRED')
    # ended.json precedes final receipt construction. A shared lock prevents
    # mistaking that short in-flight interval for terminal transport evidence.
    with gate.open('rb') as stream:
        try: fcntl.flock(stream,fcntl.LOCK_SH|fcntl.LOCK_NB)
        except BlockingIOError: return {'status':'MODEL_WRITER_ACTIVE_RECONCILE_NO_RETRY'}
        for stage in ('continuation','review','disposition'):
            if broker.stage_status({'event':event,'stage':stage})['status'] == 'COMPLETE': continue
            names = (stage+'.started.json',stage+'.ended.json')
            if any(not (folder/name).exists() for name in names):
                return {'status':'ORIGINAL_END_RECORD_UNAVAILABLE_NO_RETRY','stage':stage}
            hashes = {}
            for name in (*names,stage+'.input.md',stage+'.stdout',stage+'.stderr',stage+'.operating-context.json'):
                path=folder/name
                if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
                    raise ValueError('MODEL_FAILURE_ORIGINAL_FILE_REQUIRED')
                with path.open('rb') as original: hashes[name]=hashlib.file_digest(original,'sha256').hexdigest()
            started=json.loads((folder/names[0]).read_bytes());ended=json.loads((folder/names[1]).read_bytes())
            if (set(started) != {'stage','requested_model','started_utc','timeout_seconds'}
                    or started['stage'] != stage or set(ended) != {'returncode','ended_utc'}
                    or type(ended['returncode']) is not int):
                raise ValueError('MODEL_FAILURE_ORIGINAL_RECORD_CHANGED')
            return {'status':'ENDED_WITHOUT_VALIDATED_STAGE','event':event,'stage':stage,
                'packet_sha256':packet['packet_sha256'],'started':started,'ended':ended,
                'original_sha256':hashes,'actual_model':None,'scientific_acceptance':False,
                'retry_authorized':False,'scientific_outcome':'UNKNOWN'}
    return {'status':'ALL_STAGES_HAVE_VALIDATED_ORIGINALS','retry_authorized':False}


def _refusal_original(path, limit=1500000):
    """Fixed broker-owned original, opened without following a replacement link."""
    path = Path(path)
    info = path.lstat()
    if (any(p.is_symlink() for p in (path, *path.parents))
            or not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or info.st_mode & 0o077 or info.st_size > limit):
        raise ValueError('INPUT_REFUSAL_PROTECTED_ORIGINAL_REQUIRED')
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as stream:
        start = os.fstat(stream.fileno())
        if (start.st_dev, start.st_ino) != (info.st_dev, info.st_ino):
            raise ValueError('INPUT_REFUSAL_ORIGINAL_MOVED')
        raw = stream.read(limit + 1); end = os.fstat(stream.fileno())
        if (len(raw) > limit or (start.st_size, start.st_mtime_ns, start.st_ctime_ns) !=
                (end.st_size, end.st_mtime_ns, end.st_ctime_ns)):
            raise ValueError('INPUT_REFUSAL_ORIGINAL_MOVED')
    return raw


def stage_input_refusal(broker, body):
    """Prove one ended CLI input refusal; this read grants no retry or science."""
    if set(body) != {'event'}:
        raise ValueError('INPUT_REFUSAL_EVENT_ONLY')
    # Reuse the authenticated fixed-event/source/packet route, not caller paths.
    packet = broker.stage_packet(body)
    if packet.get('status') != 'COMPLETE':
        raise ValueError('INPUT_REFUSAL_ORIGINAL_PACKET_REQUIRED')
    event = body['event']; root = Path(broker.config['turn_root'])
    folder = root / (event['turn_id'] + '-' + event['attempt'])
    for directory in (root, folder):
        info = directory.lstat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
                or info.st_mode & 0o077 or any(p.is_symlink() for p in (directory, *directory.parents))):
            raise ValueError('INPUT_REFUSAL_PROTECTED_DIRECTORY_REQUIRED')
    gate = root / 'branch.lock'
    _refusal_original(gate, 1000)
    with os.fdopen(os.open(gate, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as lock_file:
        try: fcntl.flock(lock_file, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('INPUT_REFUSAL_MODEL_WRITER_ACTIVE')
        absent = ('continuation.md', 'continuation.receipt.json')
        if any((folder / n).exists() or (folder / n).is_symlink() for n in absent):
            raise ValueError('INPUT_REFUSAL_ANSWER_OR_RECEIPT_EXISTS')
        if any(p.name.startswith(('review.', 'disposition.')) for p in folder.iterdir()):
            raise ValueError('INPUT_REFUSAL_LATER_STAGE_EXISTS')
        names = ('binding.json', 'packet.json', 'continuation.request.json',
                 'continuation.started.json', 'continuation.ended.json',
                 'continuation.process.json', 'continuation.process-identity.json',
                 'continuation.stdout', 'continuation.stderr',
                 'continuation.input.md', 'continuation.operating-context.json')
        originals = {n: _refusal_original(folder / n,
            1500000 if n in ('packet.json', 'continuation.input.md', 'continuation.operating-context.json')
            else 20000) for n in names}
        values = {n: json.loads(originals[n]) for n in names if n.endswith('.json')}
        binding = values['binding.json']; started = values['continuation.started.json']
        ended = values['continuation.ended.json']; process = values['continuation.process.json']
        identity = values['continuation.process-identity.json']; request = values['continuation.request.json']
        hashes = {n: hashlib.sha256(raw).hexdigest() for n, raw in originals.items()}
        if (binding != {'event': event, 'packet_sha256': packet['packet_sha256']}
                or hashes['packet.json'] != packet['packet_sha256']
                or originals['packet.json'] != encoded(packet['packet'])):
            raise ValueError('INPUT_REFUSAL_PACKET_CHANGED')
        if (set(started) != {'stage', 'requested_model', 'started_utc', 'timeout_seconds'}
                or started['stage'] != 'continuation' or started['requested_model'] != 'gpt-6-astra'
                or type(started['timeout_seconds']) is not int or started['timeout_seconds'] not in (240, 600)
                or set(ended) != {'returncode', 'ended_utc'} or type(ended['returncode']) is not int
                or ended['returncode'] != 1 or process.get('stage') != 'continuation'
                or process.get('requested_model') != started['requested_model']
                or type(process.get('returncode')) is not int or process['returncode'] != 1
                or process.get('timeout_seconds') != started['timeout_seconds']
                or process.get('actual_model') is not None or process.get('usage') is not None
                or 'actual_model' not in process or 'usage' not in process
                or process.get('session_id') is not None or process.get('answer_sha256') is not None):
            raise ValueError('INPUT_REFUSAL_EXACT_ENDED_PROCESS_REQUIRED')
        start_time = datetime.fromisoformat(started['started_utc'])
        end_time = datetime.fromisoformat(ended['ended_utc'])
        if start_time.tzinfo is None or end_time.tzinfo is None or end_time < start_time:
            raise ValueError('INPUT_REFUSAL_ORIGINAL_TIME_CHANGED')
        for name, field in [('continuation.stdout', 'stdout_sha256'), ('continuation.stderr', 'stderr_sha256'),
                            ('continuation.input.md', 'input_sha256'),
                            ('continuation.operating-context.json', 'operating_context_sha256')]:
            if process.get(field) != hashes[name]:
                raise ValueError('INPUT_REFUSAL_PROCESS_HASH_CHANGED')
        context = values['continuation.operating-context.json']
        if (context.get('verified_source_commit') != event['source']
                or context.get('task_packet') != {'name': 'packet.json', 'sha256': packet['packet_sha256']}
                or set(request) != {'prompt_sha256'}
                or not re.fullmatch('[0-9a-f]{64}', request['prompt_sha256'])):
            raise ValueError('INPUT_REFUSAL_CONTEXT_BINDING_CHANGED')
        # Parse every stdout byte. An answer/error/additional event is not this proof.
        lines = originals['continuation.stdout'].decode('utf-8').splitlines()
        if len(lines) != 1:
            raise ValueError('INPUT_REFUSAL_THREAD_ONLY_REQUIRED')
        if re.fullmatch(r'\{"type":"thread.started","thread_id":"[A-Za-z0-9_-]{6,128}"\}\n', originals['continuation.stdout'].decode('utf-8')) is None:
            raise ValueError('INPUT_REFUSAL_THREAD_ONLY_REQUIRED')
        thread = json.loads(lines[0])
        if (set(thread) != {'type', 'thread_id'} or thread['type'] != 'thread.started'
                or not isinstance(thread['thread_id'], str)
                or not re.fullmatch('[A-Za-z0-9_-]{6,128}', thread['thread_id'])):
            raise ValueError('INPUT_REFUSAL_THREAD_ONLY_REQUIRED')
        text = originals['continuation.input.md'].decode('utf-8')
        error = originals['continuation.stderr'].decode('utf-8')
        match = re.fullmatch(r'Error: turn/start: turn/start failed: Input exceeds the maximum length of '
            r'1048576 characters\. \(code -32602\), data: (\{[^\n]+\})\n', error)
        if match is None:
            raise ValueError('INPUT_REFUSAL_EXACT_PROVIDER_ERROR_REQUIRED')
        details = json.loads(match.group(1))
        if match.group(1) != json.dumps({'input_error_code': 'input_too_large', 'max_chars': 1048576, 'actual_chars': len(text)}, separators=(',', ':')):
            raise ValueError('INPUT_REFUSAL_EXACT_PROVIDER_ERROR_REQUIRED')
        if (details != {'input_error_code': 'input_too_large', 'max_chars': 1048576,
                        'actual_chars': len(text)} or type(details.get('actual_chars')) is not int
                or len(text) <= 1048576):
            raise ValueError('INPUT_REFUSAL_CHARACTER_COUNT_CHANGED')
        if (set(identity) != {'pid', 'boot_id', 'process_group'}
                or type(identity['pid']) is not int or identity['pid'] <= 1
                or type(identity['process_group']) is not int or identity['process_group'] != identity['pid']
                or not isinstance(identity['boot_id'], str)
                or not re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', identity['boot_id'])):
            raise ValueError('INPUT_REFUSAL_PROCESS_IDENTITY_REQUIRED')
        boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        if not re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', boot):
            raise ValueError('INPUT_REFUSAL_BOOT_UNAVAILABLE')
        if boot == identity['boot_id']:
            try: os.killpg(identity['process_group'], 0)
            except ProcessLookupError: pass
            except OSError as error:
                raise ValueError('INPUT_REFUSAL_PROCESS_STATE_UNAVAILABLE') from error
            else: raise ValueError('INPUT_REFUSAL_ORIGINAL_PROCESS_ACTIVE')
        # Re-read each bounded original while the broker writer lock is still held.
        if any(hashlib.sha256(_refusal_original(folder / n)).hexdigest() != digest
               for n, digest in hashes.items()):
            raise ValueError('INPUT_REFUSAL_ORIGINAL_MOVED')
        small = {n: raw.decode('utf-8') for n, raw in originals.items()
                 if n not in ('packet.json', 'continuation.input.md', 'continuation.operating-context.json')}
        return {'schema': 'protected-input-refusal/v1', 'status': 'CONCLUSIVE_INPUT_REFUSAL',
            'event': event, 'packet_sha256': packet['packet_sha256'], 'packet': packet['packet'],
            'originals': small, 'file_sha256': hashes, 'input_characters': len(text),
            'limit_chars': 1048576, 'active': False, 'answer_present': False,
            'receipt_present': False, 'review_present': False, 'disposition_present': False,
            'scientific_acceptance': False, 'retry_authorized': False, 'admissions': 0}


def _database(broker, *, create=True):
    parent = Path(broker.config['turn_root']).parent
    if any(p.is_symlink() for p in (parent, *parent.parents)) or parent.stat().st_uid != 0:
        raise ValueError('INVESTIGATOR_PROTECTED_STATE_REQUIRED')
    root = parent/'investigator-wakes'
    if create: root.mkdir(mode=0o700, exist_ok=True)
    if root.is_symlink() or root.stat().st_uid != 0 or root.stat().st_mode & 0o077:
        raise ValueError('INVESTIGATOR_PROTECTED_STATE_REQUIRED')
    path = root/'reservations.sqlite'
    if path.is_symlink(): raise ValueError('INVESTIGATOR_PROTECTED_STATE_REQUIRED')
    if create and not path.exists():
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        os.close(fd)
    if path.stat().st_uid != 0 or path.stat().st_mode & 0o077:
        raise ValueError('INVESTIGATOR_PROTECTED_STATE_REQUIRED')
    db = sqlite3.connect(path if create else path.absolute().as_uri()+'?mode=ro',
                         uri=not create, isolation_level=None, timeout=5)
    db.row_factory = sqlite3.Row
    if create:
        db.execute('PRAGMA synchronous=FULL')
        db.executescript('''CREATE TABLE IF NOT EXISTS wakes(identity TEXT PRIMARY KEY, original BLOB NOT NULL);
            CREATE TABLE IF NOT EXISTS events(identity TEXT PRIMARY KEY, original BLOB NOT NULL, wake TEXT NOT NULL REFERENCES wakes(identity));''')
    return db


def _read(broker, identity):
    wakes.pin(identity)
    db = _database(broker, create=False)
    try:
        row = db.execute('SELECT original FROM wakes WHERE identity=?', (identity,)).fetchone()
        if row is None: raise ValueError('INVESTIGATOR_ORIGINAL_RESERVATION_UNAVAILABLE')
        manifest = json.loads(row['original'])
        if manifest['identity'] != identity or digest({k:v for k,v in manifest.items() if k != 'identity'}) != identity:
            raise ValueError('INVESTIGATOR_PROTECTED_WAKE_CHANGED')
        for value in manifest['events']:
            claimed = db.execute('SELECT original,wake FROM events WHERE identity=?', (wakes.event_key(value),)).fetchone()
            if claimed is None or claimed['wake'] != identity or claimed['original'] != encoded(value):
                raise ValueError('INVESTIGATOR_PROTECTED_EVENT_RESERVATION_CHANGED')
        return {'status': 'RESERVED', 'wake': manifest, 'models': 0, 'admissions': 0}
    finally: db.close()


def original(broker, operation, body, *, disposition_lock=None):
    if operation == 'disposition_unstarted':
        from orchestrator.protected_disposition import disposition_unstarted, _locked_unstarted
        return (disposition_unstarted(broker,body) if disposition_lock is None
                else _locked_unstarted(broker,body,disposition_lock))
    if operation == 'disposition_refusal':
        from orchestrator.protected_disposition import disposition_refusal, _locked_refusal
        return (disposition_refusal(broker, body) if disposition_lock is None
                else _locked_refusal(broker, body, disposition_lock))
    if operation == 'stage_status': return broker.stage_status(body)
    if operation == 'stage_packet': return broker.stage_packet(body)
    if operation == 'stage_failure': return stage_failure(broker, body)
    if operation == 'stage_input_refusal': return stage_input_refusal(broker, body)
    if operation == 'read_investigator_wake' and set(body) == {'wake'}: return _read(broker, body['wake'])
    if operation in ('scientific_job_result', 'scientific_validation_result'):
        from orchestrator.protected_scientific_jobs import handle
        return handle(broker, operation, body)
    if operation == 'read_recorded_steering': return handle(broker, operation, body)
    raise ValueError('INVESTIGATOR_VERIFIER_ORIGINAL_READ_ONLY')


def verify_subprocess(broker, config, mode, value, *, disposition_lock=None):
    """Fixed bounded UID boundary, with read-only proof served by this broker."""
    if mode not in ('events', 'entry', 'disposition_launch') or os.getuid() != 0:
        raise ValueError('INVESTIGATOR_PROTECTED_VERIFIER_REQUIRED')
    from orchestrator.remote_supervisor import checked_source
    root = checked_source(config['source_root'], config['source'])
    def identity():
        os.setgroups([]); os.setgid(config['controller_gid']); os.setuid(config['controller_uid'])
    payload = message({'config': config, 'mode': mode, 'value': value})
    if len(payload) > 2000000: raise ValueError('INVESTIGATOR_VERIFIER_INPUT_BOUND')
    process = subprocess.Popen([sys.executable, '-B', '-m', 'orchestrator.protected_investigator', '--verify'],
        cwd=root, env={'PATH':'/usr/bin:/bin', 'PYTHONPATH':str(root), 'GIT_NO_LAZY_FETCH':'1',
            'PYTHONDONTWRITEBYTECODE':'1'}, preexec_fn=identity,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    selector = selectors.DefaultSelector(); selector.register(process.stdout, selectors.EVENT_READ)
    deadline = time.monotonic()+60; total = 0; buffer = b''; queries = 0
    try:
        process.stdin.write(payload)
        process.stdin.flush()
        while time.monotonic() < deadline:
            ready = selector.select(max(0, deadline-time.monotonic()))
            if not ready: break
            data = os.read(process.stdout.fileno(), 65536)
            if not data: break
            buffer += data
            if len(buffer) > 2000000: raise ValueError('INVESTIGATOR_VERIFIER_RESPONSE_BOUND')
            if b'\n' not in buffer: continue
            raw, buffer = buffer.split(b'\n', 1)
            frame = json.loads(raw)
            if set(frame) == {'verified'}:
                process.stdin.close()
                if process.wait(timeout=max(.1, deadline-time.monotonic())) != 0:
                    raise ValueError('INVESTIGATOR_PROTECTED_VERIFICATION_FAILED')
                return frame['verified']
            if set(frame) != {'operation','body'} or queries >= 128:
                raise ValueError('INVESTIGATOR_VERIFIER_READ_CONTRACT')
            if mode == 'disposition_launch' and frame['operation'] not in ('disposition_refusal', 'disposition_unstarted', 'stage_packet', 'stage_status'):
                raise ValueError('DISPOSITION_VERIFIER_ORIGINAL_READ_ONLY')
            response = message(original(broker, frame['operation'], frame['body'], disposition_lock=disposition_lock)
                if mode == 'disposition_launch' else original(broker, frame['operation'], frame['body']))
            queries += 1; total += len(response)
            if len(response) > 2000000 or total > 32000000:
                raise ValueError('INVESTIGATOR_ORIGINAL_PROOF_BOUND')
            process.stdin.write(response)
            process.stdin.flush()
        raise ValueError('INVESTIGATOR_PROTECTED_VERIFICATION_FAILED')
    finally:
        selector.close()
        if process.poll() is None: process.kill()
        process.wait(timeout=5)
        process.stdout.close()
        if not process.stdin.closed: process.stdin.close()


def handle(broker, operation, body):
    if os.getuid() != 0 or operation not in OPERATIONS:
        raise ValueError('INVESTIGATOR_PROTECTED_ROUTE_REQUIRED')
    from orchestrator.protected_scientific_jobs import controller_configuration, admission_guard
    config = controller_configuration(broker)
    if operation == 'stage_failure': return stage_failure(broker, body)
    if operation == 'stage_input_refusal': return stage_input_refusal(broker, body)
    if operation == 'read_investigator_wake':
        if set(body) != {'wake'}: raise ValueError('INVESTIGATOR_READ_WAKE_CONTRACT')
        return _read(broker, body['wake'])
    if operation in ('list_recorded_steering','read_recorded_steering'):
        from orchestrator import recorded_steering
        if operation == 'list_recorded_steering' and body == {}:
            return recorded_steering.list_recorded_steering(config)
        if operation == 'read_recorded_steering' and set(body) == {'request_id'}:
            return recorded_steering.read_recorded_steering(config, wakes.pin(body['request_id']))
        raise ValueError('INVESTIGATOR_RECORDED_STEERING_SCHEMA')
    installed = wakes.setting(config)
    if installed is None: raise ValueError('INVESTIGATOR_DISABLED')
    if set(body) != {'events'} or not isinstance(body['events'], list) or not 1 <= len(body['events']) <= wakes.MAX_EVENTS:
        raise ValueError('INVESTIGATOR_RESERVATION_CONTRACT')
    if len({wakes.event_key(value) for value in body['events']}) != len(body['events']):
        raise ValueError('INVESTIGATOR_DUPLICATE_EVENT')
    # Already reserved exact originals are read-only dedup, even if their later
    # review changed. Any dependent fresh eligibility still rechecks originals.
    fresh = []; existing = set()
    try: prior = _database(broker, create=False)
    except FileNotFoundError: prior = None
    try:
        for value in body['events']:
            row = None if prior is None else prior.execute('SELECT original,wake FROM events WHERE identity=?',
                (wakes.event_key(value),)).fetchone()
            if row is None: fresh.append(value)
            elif row['original'] != encoded(value): raise ValueError('INVESTIGATOR_CONSUMED_EVENT_CHANGED')
            else: existing.add(row['wake'])
    finally:
        if prior is not None: prior.close()
    if not fresh:
        return {'status':'NO_NEW_EVENTS','existing_wakes':sorted(existing),'models':0,'admissions':0}
    # Each new candidate is original-verified before it can consume an event.
    proof = verify_subprocess(broker, config, 'events', fresh)
    if proof != {'status':'VERIFIED_EVENTS', 'source':config['source'],
            'template_sha256':installed['template_sha256'], 'events':fresh}:
        raise ValueError('INVESTIGATOR_PROTECTED_VERIFICATION_CHANGED')
    with admission_guard(broker, config):
        db = _database(broker)
        try:
            db.execute('BEGIN IMMEDIATE'); new = []; old = set()
            for value in body['events']:
                row = db.execute('SELECT original,wake FROM events WHERE identity=?', (wakes.event_key(value),)).fetchone()
                if row is None: new.append(value)
                elif row['original'] != encoded(value): raise ValueError('INVESTIGATOR_CONSUMED_EVENT_CHANGED')
                else: old.add(row['wake'])
            if not new:
                db.execute('COMMIT')
                return {'status':'NO_NEW_EVENTS', 'existing_wakes':sorted(old), 'models':0, 'admissions':0}
            core = {'schema':wakes.WAKE, 'source':config['source'], 'template_sha256':installed['template_sha256'],
                'events':sorted(new,key=wakes.event_key), 'day':datetime.now(timezone.utc).date().isoformat()}
            manifest = {**core, 'identity':digest(core)}
            db.execute('INSERT INTO wakes VALUES(?,?)', (manifest['identity'],encoded(manifest)))
            for value in new:
                db.execute('INSERT INTO events VALUES(?,?,?)', (wakes.event_key(value),encoded(value),manifest['identity']))
            db.execute('COMMIT')
            return {'status':'RESERVED', 'wake':manifest, 'existing_wakes':sorted(old), 'models':0, 'admissions':0}
        except BaseException:
            if db.in_transaction: db.execute('ROLLBACK')
            raise
        finally: db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', required=True); parser.parse_args()
    data = json.loads(sys.stdin.buffer.readline(2000001))
    config = data['config']
    if os.getuid() != config['controller_uid'] or config['controller_uid'] <= 0:
        raise ValueError('INVESTIGATOR_CONTROLLER_VERIFIER_REQUIRED')
    cache = {}
    def reader(_socket, operation, body):
        request = {'operation':operation,'body':body}; key = digest(request)
        if key not in cache:
            sys.stdout.buffer.write(message(request)); sys.stdout.buffer.flush()
            raw = sys.stdin.buffer.readline(2000001)
            if len(raw) > 2000000: raise ValueError('INVESTIGATOR_ORIGINAL_RESPONSE_BOUND')
            cache[key] = json.loads(raw)
        return cache[key]
    if data['mode'] == 'events':
        wakes.verify_events(config, data['value'], reader)
        result = {'status':'VERIFIED_EVENTS','source':config['source'],
            'template_sha256':wakes.setting(config)['template_sha256'],'events':data['value']}
    elif data['mode'] == 'entry':
        from orchestrator.continuing_research import validate_registration
        result = validate_registration(config, data['value'], client=reader)
    elif data['mode'] == 'disposition_launch':
        from orchestrator.disposition_successors import verify_launch
        result = verify_launch(config, data['value'], reader)
    else: raise ValueError('INVESTIGATOR_FIXED_VERIFIER_MODE_REQUIRED')
    sys.stdout.buffer.write(message({'verified':result})); sys.stdout.buffer.flush()


if __name__ == '__main__': main()
