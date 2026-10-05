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


def _read(path, *, owner=None):
    # Only privileged read-only callers may name another expected owner.
    # Writers retain the current-UID default and cannot acquire this privilege.
    uid = os.getuid()
    owner = uid if owner is None else owner
    if type(owner) is not int or owner < 0 or (uid != 0 and owner != uid):
        raise ValueError("CHANGE_READ_OWNER_NOT_PERMITTED")
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('CHANGE_SYMLINK_REJECTED')
    st = path.stat()
    if not stat.S_ISREG(st.st_mode) or st.st_uid != owner or st.st_mode & 0o077:
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


def _original_bytes(raw):
    if not isinstance(raw, bytes):
        raise ValueError('CHANGE_ORIGINAL_BYTES_REQUIRED')
    if len(raw) > 100000:
        raise ValueError('CHANGE_RECORD_TOO_LARGE')
    return raw


def _evidence(folder, value, read_evidence=None):
    if isinstance(value, dict):
        if 'artifact' in value and 'sha256' in value:
            name = value['artifact']
            if not isinstance(name, str) or not name.startswith('evidence/') or '..' in Path(name).parts:
                raise ValueError('CHANGE_EVIDENCE_PATH_INVALID')
            raw = _original_bytes(_read(folder/name) if read_evidence is None else read_evidence(name))
            if digest(raw) != value['sha256'] or len(raw) != value.get('size', len(raw)):
                raise ValueError('CHANGE_EVIDENCE_CHANGED')
        for item in value.values():
            _evidence(folder, item, read_evidence)
    elif isinstance(value, list):
        for item in value:
            _evidence(folder, item, read_evidence)


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
        superseded = payload.get('supersedes_applied_events', [])
        prior = {e['identity'] for e in history if e['event'] == 'APPLIED'}
        if (not isinstance(superseded, list) or any(not isinstance(x, str) for x in superseded)
                or len(set(superseded)) != len(superseded) or not set(superseded) <= prior):
            raise ValueError('CHANGE_SUPERSEDED_APPLICATION_REQUIRED')
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


def validate_originals(request_raw, events, read_evidence):
    """Validate exported originals without filesystem access.

    Event keys are exact basenames; the caller supplies retained evidence bytes
    by their original relative artifact names. This authenticates chain integrity,
    not the caller's authority to select this chain as an approved policy source.
    """
    request_raw = _original_bytes(request_raw)
    if (not isinstance(events, dict) or any(not isinstance(name, str) for name in events)
            or not callable(read_evidence)):
        raise ValueError('CHANGE_ORIGINAL_EVENTS_AND_READER_REQUIRED')
    request = _request(json.loads(request_raw))
    previous = digest(request_raw)
    verified = []
    for name in sorted(events):
        event_raw = _original_bytes(events[name])
        event = json.loads(event_raw)
        core = {k: v for k, v in event.items() if k != 'identity'}
        if (event.get('schema') != EVENT_SCHEMA or event.get('request_identity') != request['identity']
                or event.get('sequence') != len(verified)+1 or event.get('previous_sha256') != previous
                or event.get('identity') != digest(encoded(core))
                or name != f'{len(verified)+1:04d}-{event["identity"]}.json'):
            raise ValueError('CHANGE_EVENT_CHAIN_INVALID')
        actor(event['actor'])
        _transition(verified, event['event'], event['payload'])
        _evidence(None, event['payload'], read_evidence)
        previous = digest(event_raw)
        verified.append(event)
    return {'request': request, 'events': verified, 'head_sha256': previous}


def load(folder, *, owner=None):
    """Verify originals; an explicit owner permits privileged reads, never writes."""
    folder = Path(folder)
    raw = _read(folder/'request.json', owner=owner)
    request = _request(json.loads(raw))
    if folder.name != request['identity']:
        raise ValueError('CHANGE_FOLDER_IDENTITY_MISMATCH')
    events = {}
    event_dir = folder/'events'
    if event_dir.exists():
        if event_dir.is_symlink():
            raise ValueError('CHANGE_SYMLINK_REJECTED')
        for path in sorted(event_dir.iterdir()):
            if path.name == '.lock':
                continue
            events[path.name] = _read(path, owner=owner)
    return validate_originals(raw, events, lambda name: _read(folder/name, owner=owner))

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
        outcomes = {}
        for event in events:
            if event['event'] == 'REVIEW':
                identity = event['payload']['applied_event']
                if outcomes.get(identity) != 'REQUEST_CHANGES':
                    outcomes[identity] = event['payload']['verdict']
        superseded = {identity for event in applied
                      for identity in event['payload'].get('supersedes_applied_events', [])}
        active = [event['identity'] for event in applied if event['identity'] not in superseded]
        pending = [identity for identity in active if identity not in outcomes]
        status = ('REQUEST_CHANGES' if any(outcomes.get(x) == 'REQUEST_CHANGES' for x in active)
                  else 'PENDING' if pending or not applied else 'APPROVE')
        rows.append({'identity': req['identity'], 'request': req['requested_change'], 'target': req['target'],
                     'submitter': req['submitter'], 'scope_limits': req['scope_limits'],
                     'actor_attribution': 'Recorded by the calling route; no human attestation or execution grant is inferred.',
                     'state': 'APPLIED' if applied else 'AUTHORIZED' if any(e['event'] == 'AUTHORIZED' for e in events) else 'SUBMITTED',
                     'review_status': status, 'pending_applied_events': pending,
                     'superseded_applied_events': sorted(superseded),
                     'events': [{'identity': e['identity'], 'event': e['event'], 'actor': e['actor'], 'payload': e['payload']} for e in events],
                     'record_head_sha256': state['head_sha256']})
    result = {'schema': SCHEMA, 'requests': rows}
    full = encoded(result)
    # Compact only the size: unsafe text in omitted history must still refuse.
    permitted_text(full.decode(), limit=max(20000, len(full)))
    if len(full) > 20000:
        result = _bounded_context(rows)
    permitted_text(encoded(result).decode(), limit=20000)
    return result


def _bounded_context(rows):
    """Keep growing history from blocking work; preserve explicit missing context."""
    result = {'schema': SCHEMA, 'requests': [], 'projection': {
        'kind': 'BOUNDED_SUMMARY', 'full_context_sha256': digest(encoded(rows)),
        'total_requests': len(rows), 'omitted_requests': 0,
        'omitted_review_status_counts': {},
        'notice': 'History is summarized. Omitted or pending records are not approval. '
                  'Inspect the same private store with inspect --request-id ID; '
                  'inspect --index lists every request identity.'}}
    priority = {'REQUEST_CHANGES': 0, 'PENDING': 1, 'APPROVE': 2}
    for row in sorted(rows, key=lambda r: (priority[r['review_status']], r['identity'])):
        criticism = [e for e in row['events'] if e['event'] == 'REVIEW'
                     and e['payload']['verdict'] == 'REQUEST_CHANGES']
        compact = {key: row[key] for key in ('identity', 'state', 'review_status', 'record_head_sha256')}
        compact.update({'request': row['request'][:500],
            'submitter': row['submitter'],
            'target': {k: row['target'][k] for k in ('task', 'source')},
            'pending_applied_count': len(row['pending_applied_events']),
            'superseded_applied_count': len(row['superseded_applied_events']),
            'event_count': len(row['events']), 'criticism_count': len(criticism),
            'details_omitted': True})
        if criticism:
            last = criticism[-1]
            compact['latest_criticism'] = {'event': last['identity'],
                'actor': last['actor'],
                'applied_event': last['payload']['applied_event'],
                'rationale_preview': last['payload']['rationale'][:500],
                'affected_results_preview': json.dumps(last['payload']['affected_results'])[:600],
                'full_record_required_before_acceptance': True}
        if len(encoded(result)) + len(encoded(compact)) < 18500:
            result['requests'].append(compact)
        else:
            meta = result['projection']; meta['omitted_requests'] += 1
            counts = meta['omitted_review_status_counts']; status = row['review_status']
            counts[status] = counts.get(status, 0) + 1
    return result


REVIEW_BINDINGS_SCHEMA = 'deployment-review-change-bindings/v1'
MAX_REVIEW_SELECTIONS = 32
MAX_SELECTED_REVIEW_BYTES = 250000


def _review_selections(value):
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_REVIEW_SELECTIONS:
        raise ValueError('BOUNDED_EXPLICIT_REVIEW_SELECTION_REQUIRED')
    seen = set()
    for item in value:
        if (not isinstance(item, dict) or set(item) != {'request', 'applied'}
                or any(not isinstance(x, str) or not re.fullmatch('[0-9a-f]{64}', x)
                       for x in item.values()) or item['request'] in seen):
            raise ValueError('EXACT_UNIQUE_REVIEW_SELECTION_REQUIRED')
        seen.add(item['request'])
    return value


def review_bindings(source, proposal_sha256, selections):
    """Sidecar identity only; callers must compare it to the actual proposal."""
    if (not isinstance(source, str) or not re.fullmatch('[0-9a-f]{40}', source)
            or not isinstance(proposal_sha256, str) or not re.fullmatch('[0-9a-f]{64}', proposal_sha256)):
        raise ValueError('EXACT_REVIEW_PROPOSAL_BINDING_REQUIRED')
    return {'schema': REVIEW_BINDINGS_SCHEMA, 'source': source,
            'proposal_sha256': proposal_sha256, 'changes': _review_selections(selections)}


def review_context(store, selections, *, source):
    """Keep ordinary bounded history plus explicitly selected original applications.

    This is preparation for review, never approval. The separate bounded section
    prevents a growing history from hiding the exact actor/payload being reviewed.
    """
    selections = _review_selections(selections)
    if not isinstance(source, str) or not re.fullmatch('[0-9a-f]{40}', source):
        raise ValueError('EXACT_REVIEW_PROPOSAL_BINDING_REQUIRED')
    result = context(store)
    selected = []
    for binding in selections:
        folder = Path(store)/binding['request']; state = load(folder)
        events = state['events']
        applied = [e for e in events if e['event'] == 'APPLIED' and e['identity'] == binding['applied']]
        if len(applied) != 1:
            raise ValueError('ORIGINAL_SELECTED_APPLICATION_REQUIRED')
        if any(binding['applied'] in e['payload'].get('supersedes_applied_events', [])
               for e in events if e['event'] == 'APPLIED'):
            raise ValueError('SELECTED_APPLICATION_SUPERSEDED')
        result_binding = applied[0]['payload'].get('result_binding')
        if not isinstance(result_binding, dict) or result_binding.get('source') != source:
            raise ValueError('SELECTED_APPLICATION_SOURCE_CHANGED')
        req = state['request']
        selected.append({'request': binding['request'], 'request_sha256': digest(_read(folder/'request.json')),
            'target': req['target'], 'requested_change': req['requested_change'],
            'submitter': req['submitter'], 'scope_limits': req['scope_limits'],
            'record_head_sha256': state['head_sha256'], 'event': applied[0]})
    raw = encoded(selected)
    if len(raw) > MAX_SELECTED_REVIEW_BYTES:
        raise ValueError('SELECTED_REVIEW_APPLICATION_BYTES_EXCEEDED')
    permitted_text(raw.decode(), limit=MAX_SELECTED_REVIEW_BYTES)
    return {**result, 'selected_applications': selected, 'selected_application_notice':
        'Only these explicitly selected original APPLIED events are complete. The ordinary history '
        'projection and its pending/criticism/omission notices remain applicable. Selection is not '
        'approval; no original event or authority is changed.'}


def request_index(store, task=None):
    """Unabridged private CLI index for inspecting any omitted request."""
    rows = []
    for folder in sorted(Path(store).iterdir()) if Path(store).exists() else []:
        if re.fullmatch(r'[0-9a-f]{64}', folder.name):
            req = load(folder)['request']
            if task is None or req['target']['task'] == task:
                rows.append({'identity': req['identity'], 'target': req['target']['task']})
    return rows


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
    detail = view_parser.add_mutually_exclusive_group()
    detail.add_argument('--request-id', help='Inspect one complete verified private event chain')
    detail.add_argument('--index', action='store_true', help='List every saved request identity')
    a = parser.parse_args()
    if a.operation == 'submit':
        by = ({'kind': 'human', 'identity': a.human, 'identity_source': 'cli_declared'}
              if a.human else json.loads(a.actor_json.read_text()))
        result = submit(a.store, a.root, a.target, a.request, by,
                        source=a.source, files=a.file, key=a.key, risk=a.risk, scope_limits=a.scope_limit)
    elif a.operation == 'record':
        result = record(a.folder, a.event, json.loads(a.actor_json.read_text()), json.loads(a.payload_json.read_text()))
    elif a.request_id:
        pin(a.request_id, 64)
        result = load(a.store/a.request_id)
    elif a.index:
        result = request_index(a.store, a.target)
    else:
        result = context(a.store, a.target)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
