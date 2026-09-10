"""Recorded steering requests and evidence, using the existing private/report helpers.

These operations preserve proposed and executed versions; they do not run changes,
models, or scientific work, and their authorization records do not replace any
execution gate. Actor attribution is supplied by the calling human/agent route.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import subprocess

from orchestrator.human_controls import DANGER, request as control_request
from orchestrator.operations_report import digest, immutable, pin, private_root
from orchestrator.public_export import text as permitted_text

SCHEMA = 'research-change-request/v1'
EVENT_SCHEMA = 'research-change-event/v1'
META = {'identity', 'status', 'submitted_at_utc', 'execution_status', 'review_status'}
EVENTS = {'AUTHORIZED', 'APPLIED', 'REVIEW', 'DISPOSITION'}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def now():
    return datetime.now(timezone.utc).isoformat()


def actor(value):
    if not isinstance(value, dict) or value.get('kind') not in {'human', 'agent'}:
        raise ValueError('CHANGE_ACTOR_REQUIRED')
    if value['kind'] == 'human':
        if not value.get('identity'):
            raise ValueError('CHANGE_HUMAN_IDENTITY_REQUIRED')
    elif not all(value.get(k) for k in ('family', 'model', 'session_id')):
        raise ValueError('CHANGE_AGENT_PROVENANCE_REQUIRED')
    permitted_text(encoded(value).decode(), limit=2000)
    return value


def _read(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('CHANGE_SYMLINK_REJECTED')
    st = path.stat()
    if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_mode & 0o077:
        raise ValueError('CHANGE_PRIVATE_FILE_REQUIRED')
    if st.st_size > 100000:
        raise ValueError('CHANGE_RECORD_TOO_LARGE')
    return path.read_bytes()


def _request(record):
    if record.get('schema') != SCHEMA or record.get('status') != 'SUBMITTED':
        raise ValueError('CHANGE_REQUEST_SCHEMA_REQUIRED')
    core = {k: v for k, v in record.items() if k not in META}
    if digest(encoded(core)) != record.get('identity'):
        raise ValueError('CHANGE_REQUEST_IDENTITY_MISMATCH')
    actor(record['submitter'])
    target = record['target']
    pin(target['source'], 40)
    if not isinstance(target.get('task'), str) or not target['task'] or len(target['task']) > 200:
        raise ValueError('CHANGE_TARGET_REQUIRED')
    if not isinstance(target.get('files'), dict):
        raise ValueError('CHANGE_TARGET_FILES_REQUIRED')
    for name, value in target['files'].items():
        if not name or Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('CHANGE_RELATIVE_TARGET_REQUIRED')
        pin(value, 64)
    if not record.get('requested_change') or len(record['requested_change']) > 2000:
        raise ValueError('CHANGE_PLAIN_REQUEST_REQUIRED')
    if not isinstance(record.get('scope_limits'), list) or not record['scope_limits']:
        raise ValueError('CHANGE_SCOPE_REQUIRED')
    permitted_text(encoded(record).decode())
    return record


def submit(store, root, task, plain, submitter, *, source=None, files=(), key='change',
           risk='UNASSESSED', scope_limits=()):
    """Save a plain-language proposal; no authorization or application follows."""
    root = Path(root)
    source = source or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    pin(source, 40)
    actor(submitter)
    if DANGER.search(plain) or len(plain) > 2000 or not plain.strip():
        raise ValueError('REQUEST_CONTENT_NOT_PERMITTED')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,40}', key):
        raise ValueError('INVALID_REQUEST_ID_OR_ACTOR')
    bound = {}
    for name in files:
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('CHANGE_RELATIVE_TARGET_REQUIRED')
        committed = subprocess.check_output(['git', 'show', source+':'+name], cwd=root)
        if (root/name).is_symlink() or (root/name).read_bytes() != committed:
            raise ValueError('CHANGE_TARGET_VERSION_MISMATCH')
        bound[name] = digest(committed)
    # Campaign requests reuse the existing steering constructor exactly. Other
    # ideas/notebooks/runs use the same request-only envelope and content guard.
    experiment = task.rsplit(':', 1)[-1]
    if experiment in {'P001', 'P002', 'P003'} and submitter.get('family', 'codex') == 'codex':
        req = control_request('actioner', 'brief', experiment, plain, source, 'actions-artifact', key,
                              'human' if submitter['kind'] == 'human' else 'codex')
    else:
        req = {'control': 'steering', 'request_id': key, 'request': plain,
               'source': source, 'authority': 'request_only'}
    core = {'schema': SCHEMA, 'request': req, 'target': {'task': task, 'source': source, 'files': bound},
            'submitter': submitter, 'origin': 'Recorded steering request', 'requested_change': plain,
            'risk': risk, 'scope_limits': list(scope_limits)}
    identity = digest(encoded(core))
    out = private_root(private_root(store)/identity)
    if (out/'request.json').exists():
        old = load(out)['request']
        if {k: v for k, v in old.items() if k not in META} != core:
            raise ValueError('CHANGE_REQUEST_CONFLICT')
        return old
    record = {**core, 'identity': identity, 'status': 'SUBMITTED', 'submitted_at_utc': now(),
              'execution_status': 'NOT_EXECUTED_BY_SUBMISSION', 'review_status': 'PENDING_PROPORTIONATE_REVIEW'}
    _request(record)
    immutable(out/'request.json', encoded(record)+b'\n')
    return record


def preserve(folder, path):
    """Copy permitted original evidence bytes to an immutable owner-only record."""
    folder = private_root(folder)
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('CHANGE_EVIDENCE_REGULAR_FILE_REQUIRED')
    raw = path.read_bytes()
    name = digest(raw)+'-'+path.name
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', name):
        raise ValueError('CHANGE_EVIDENCE_NAME_INVALID')
    out = private_root(folder/'evidence')/name
    immutable(out, raw)
    return {'artifact': 'evidence/'+name, 'sha256': digest(raw), 'size': len(raw)}


def _evidence(folder, value):
    if isinstance(value, dict):
        if 'artifact' in value and 'sha256' in value:
            name = value['artifact']
            if not isinstance(name, str) or not name.startswith('evidence/') or '..' in Path(name).parts:
                raise ValueError('CHANGE_EVIDENCE_PATH_INVALID')
            raw = _read(folder/name)
            if digest(raw) != value['sha256'] or len(raw) != value.get('size', len(raw)):
                raise ValueError('CHANGE_EVIDENCE_CHANGED')
        for item in value.values():
            _evidence(folder, item)
    elif isinstance(value, list):
        for item in value:
            _evidence(folder, item)


def _transition(history, event, payload):
    kinds = [e['event'] for e in history]
    if event == 'AUTHORIZED':
        if not payload.get('rationale') or not payload.get('authority_reference') or not payload.get('review_policy'):
            raise ValueError('CHANGE_AUTHORITY_AND_REVIEW_POLICY_REQUIRED')
    elif event == 'APPLIED':
        if 'AUTHORIZED' not in kinds:
            raise ValueError('CHANGE_AUTHORIZATION_RECORD_REQUIRED')
        if not all(payload.get(k) for k in ('modification', 'checks', 'result_binding')):
            raise ValueError('CHANGE_ACTUAL_MODIFICATION_CHECKS_BINDING_REQUIRED')
        if payload.get('review_status') != 'PENDING':
            raise ValueError('CHANGE_APPLIED_REVIEW_MUST_START_PENDING')
    elif event == 'REVIEW':
        reviewed = payload.get('applied_event')
        if reviewed not in {e['identity'] for e in history if e['event'] == 'APPLIED'}:
            raise ValueError('CHANGE_REVIEW_APPLIED_EVENT_REQUIRED')
        if payload.get('verdict') not in {'APPROVE', 'REQUEST_CHANGES'} or not payload.get('rationale') or not payload.get('review_evidence'):
            raise ValueError('CHANGE_REVIEW_OUTCOME_AND_EVIDENCE_REQUIRED')
        if payload['verdict'] == 'REQUEST_CHANGES' and not payload.get('affected_results'):
            raise ValueError('CHANGE_CRITICISM_RESULT_DISPOSITION_REQUIRED')
    elif event == 'DISPOSITION':
        if not payload.get('rationale') or not payload.get('affected_results'):
            raise ValueError('CHANGE_DISPOSITION_RESULTS_REQUIRED')
    else:
        raise ValueError('CHANGE_UNKNOWN_EVENT')


def load(folder):
    """Verify immutable proposal, ordered events, and retained evidence bytes."""
    folder = Path(folder)
    raw = _read(folder/'request.json')
    request = _request(json.loads(raw))
    if folder.name != request['identity']:
        raise ValueError('CHANGE_FOLDER_IDENTITY_MISMATCH')
    previous = digest(raw)
    events = []
    event_dir = folder/'events'
    if event_dir.exists():
        if event_dir.is_symlink():
            raise ValueError('CHANGE_SYMLINK_REJECTED')
        for path in sorted(event_dir.iterdir()):
            if path.name == '.lock':
                continue
            event_raw = _read(path)
            event = json.loads(event_raw)
            core = {k: v for k, v in event.items() if k != 'identity'}
            if (event.get('schema') != EVENT_SCHEMA or event.get('request_identity') != request['identity']
                    or event.get('sequence') != len(events)+1 or event.get('previous_sha256') != previous
                    or event.get('identity') != digest(encoded(core))
                    or path.name != f'{len(events)+1:04d}-{event["identity"]}.json'):
                raise ValueError('CHANGE_EVENT_CHAIN_INVALID')
            actor(event['actor'])
            _transition(events, event['event'], event['payload'])
            _evidence(folder, event['payload'])
            previous = digest(event_raw)
            events.append(event)
    return {'request': request, 'events': events, 'head_sha256': previous}


def record(folder, event, by, payload):
    """Record an observed operation/outcome; execute no operation or model."""
    folder = private_root(folder)
    actor(by)
    event_dir = private_root(folder/'events')
    lock = event_dir/'.lock'
    if lock.is_symlink():
        raise ValueError('CHANGE_SYMLINK_REJECTED')
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        state = load(folder)
        for prior in state['events']:
            if prior['event'] == event and prior['actor'] == by and prior['payload'] == payload:
                return prior
        _transition(state['events'], event, payload)
        _evidence(folder, payload)
        core = {'schema': EVENT_SCHEMA, 'request_identity': state['request']['identity'],
                'sequence': len(state['events'])+1, 'previous_sha256': state['head_sha256'],
                'event': event, 'actor': by, 'recorded_at_utc': now(), 'payload': payload}
        result = {**core, 'identity': digest(encoded(core))}
        immutable(event_dir/f'{result["sequence"]:04d}-{result["identity"]}.json', encoded(result)+b'\n')
        return result


def context(store, task=None):
    """Shared role/task/report projection; pending review remains visible."""
    store = Path(store)
    if not store.exists():
        return {'schema': SCHEMA, 'requests': []}
    if store.is_symlink():
        raise ValueError('CHANGE_SYMLINK_REJECTED')
    rows = []
    for folder in sorted(store.iterdir()):
        if not re.fullmatch(r'[0-9a-f]{64}', folder.name):
            continue
        state = load(folder)
        req, events = state['request'], state['events']
        if task is not None and req['target']['task'] != task:
            continue
        applied = [e for e in events if e['event'] == 'APPLIED']
        outcomes = {e['payload']['applied_event']: e['payload']['verdict'] for e in events if e['event'] == 'REVIEW'}
        pending = [e['identity'] for e in applied if e['identity'] not in outcomes]
        status = ('REQUEST_CHANGES' if 'REQUEST_CHANGES' in outcomes.values() else 'PENDING' if pending or not applied else 'APPROVE')
        rows.append({'identity': req['identity'], 'request': req['requested_change'], 'target': req['target'],
                     'submitter': req['submitter'], 'scope_limits': req['scope_limits'],
                     'actor_attribution': 'Recorded by the calling route; no human attestation or execution grant is inferred.',
                     'state': 'APPLIED' if applied else 'AUTHORIZED' if any(e['event'] == 'AUTHORIZED' for e in events) else 'SUBMITTED',
                     'review_status': status, 'pending_applied_events': pending,
                     'events': [{'identity': e['identity'], 'event': e['event'], 'actor': e['actor'], 'payload': e['payload']} for e in events],
                     'record_head_sha256': state['head_sha256']})
    result = {'schema': SCHEMA, 'requests': rows}
    permitted_text(encoded(result).decode(), limit=20000)
    return result


def context_text(store, task=None):
    value = context(store, task)
    return 'Recorded change requests (state and evidence, not new execution authority):\n'+json.dumps(value, sort_keys=True, indent=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    submit_parser = sub.add_parser('submit')
    submit_parser.add_argument('--store', type=Path, required=True)
    submit_parser.add_argument('--root', type=Path, default=Path.cwd())
    submit_parser.add_argument('--target', required=True)
    submit_parser.add_argument('--request', required=True)
    who = submit_parser.add_mutually_exclusive_group(required=True)
    who.add_argument('--actor-json', type=Path)
    who.add_argument('--human', help='Declared human operator name; not an authorization grant')
    submit_parser.add_argument('--source')
    submit_parser.add_argument('--file', action='append', default=[])
    submit_parser.add_argument('--key', default='change')
    submit_parser.add_argument('--risk', default='UNASSESSED')
    submit_parser.add_argument('--scope-limit', action='append', required=True)
    event_parser = sub.add_parser('record')
    event_parser.add_argument('--folder', type=Path, required=True)
    event_parser.add_argument('--event', choices=sorted(EVENTS), required=True)
    event_parser.add_argument('--actor-json', type=Path, required=True)
    event_parser.add_argument('--payload-json', type=Path, required=True)
    view_parser = sub.add_parser('inspect')
    view_parser.add_argument('--store', type=Path, required=True)
    view_parser.add_argument('--target')
    a = parser.parse_args()
    if a.operation == 'submit':
        by = ({'kind': 'human', 'identity': a.human, 'identity_source': 'cli_declared'}
              if a.human else json.loads(a.actor_json.read_text()))
        result = submit(a.store, a.root, a.target, a.request, by,
                        source=a.source, files=a.file, key=a.key, risk=a.risk, scope_limits=a.scope_limit)
    elif a.operation == 'record':
        result = record(a.folder, a.event, json.loads(a.actor_json.read_text()), json.loads(a.payload_json.read_text()))
    else:
        result = context(a.store, a.target)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()