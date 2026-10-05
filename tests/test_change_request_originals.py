import json
from pathlib import Path

import pytest

from orchestrator import change_requests as changes

AGENT = {'kind': 'agent', 'family': 'codex', 'model': 'fixture-only',
         'session_id': 'memory-originals-fixture'}
REVIEWER = {'kind': 'agent', 'family': 'claude', 'model': 'fixture-only',
            'session_id': 'memory-originals-review'}


def originals(folder):
    return ((folder/'request.json').read_bytes(),
            {p.name: p.read_bytes() for p in (folder/'events').glob('*.json')},
            {str(p.relative_to(folder)): p.read_bytes()
             for p in (folder/'evidence').iterdir()})


@pytest.fixture
def chain(tmp_path):
    # Explicit synthetic source and no source files avoid any Git/provider call.
    request = changes.submit(tmp_path/'store', tmp_path, 'notebook:memory-fixture',
                             'Preserve complete original chain bytes.', AGENT,
                             source='a'*40, scope_limits=['Synthetic records only'])
    folder = tmp_path/'store'/request['identity']
    evidence = tmp_path/'review.txt'
    evidence.write_bytes(b'Synthetic original evidence.\n')
    ref = changes.preserve(folder, evidence)
    snapshots = [changes.load(folder)]
    changes.record(folder, 'AUTHORIZED', AGENT, {
        'rationale': 'Synthetic authority, not real authorization.',
        'authority_reference': 'fixture', 'review_policy': 'SCOPED_REVIEW'})
    snapshots.append(changes.load(folder))
    applied = changes.record(folder, 'APPLIED', AGENT, {
        'modification': {'nested': [ref]}, 'checks': [ref],
        'result_binding': {'source': 'a'*40}, 'review_status': 'PENDING'})
    snapshots.append(changes.load(folder))
    changes.record(folder, 'REVIEW', REVIEWER, {
        'applied_event': applied['identity'], 'verdict': 'APPROVE',
        'rationale': 'Synthetic opposing review only.', 'review_evidence': [ref]})
    snapshots.append(changes.load(folder))
    return folder, snapshots


def test_memory_prefixes_equal_native_load_and_preserve_originals(chain, monkeypatch):
    folder, snapshots = chain
    request, events, evidence = originals(folder)
    before = (request, dict(events), dict(evidence))
    seen = []

    def reader(name):
        seen.append(name)
        return evidence[name]

    def forbidden(*args, **kwargs):
        raise AssertionError('Pure validation attempted a filesystem read')

    monkeypatch.setattr(changes, '_read', forbidden)
    monkeypatch.setattr(Path, 'read_bytes', forbidden)
    monkeypatch.setattr(Path, 'exists', forbidden)
    ordered = sorted(events)
    for count, expected in enumerate(snapshots):
        prefix = {name: events[name] for name in reversed(ordered[:count])}
        assert changes.validate_originals(request, prefix, reader) == expected
    assert seen and set(seen) == set(evidence)
    assert (request, events, evidence) == before


def test_load_calls_shared_validator_and_keeps_folder_identity_guard(chain, monkeypatch):
    folder, snapshots = chain
    real = changes.validate_originals
    calls = []

    def checked(raw, events, reader):
        calls.append((raw, tuple(sorted(events))))
        return real(raw, events, reader)

    monkeypatch.setattr(changes, 'validate_originals', checked)
    assert changes.load(folder) == snapshots[-1]
    assert len(calls) == 1 and '.lock' not in calls[0][1]
    wrong = folder.with_name('b'*64)
    folder.rename(wrong)
    with pytest.raises(ValueError, match='CHANGE_FOLDER_IDENTITY_MISMATCH'):
        changes.load(wrong)
    assert len(calls) == 1


@pytest.mark.parametrize('target', ['request', 'event', 'evidence'])
def test_corrupt_original_refused_by_memory_and_load(chain, target):
    folder, _ = chain
    request, events, evidence = originals(folder)
    if target == 'request':
        path = folder/'request.json'
        bad = request.replace(b'Preserve complete', b'Corrupt complete')
        request = bad
        expected = 'CHANGE_REQUEST_IDENTITY_MISMATCH'
    elif target == 'event':
        name = sorted(events)[0]
        path = folder/'events'/name
        bad = events[name].replace(b'Synthetic authority', b'Corrupted authority')
        events[name] = bad
        expected = 'CHANGE_EVENT_CHAIN_INVALID'
    else:
        name = next(iter(evidence))
        path = folder/name
        bad = b'Changed original evidence'
        evidence[name] = bad
        expected = 'CHANGE_EVIDENCE_CHANGED'
    path.write_bytes(bad)
    with pytest.raises(ValueError, match=expected):
        changes.validate_originals(request, events, evidence.__getitem__)
    with pytest.raises(ValueError, match=expected):
        changes.load(folder)


@pytest.mark.parametrize('change', ['filename', 'missing_first', 'request_raw_spacing'])
def test_exact_event_names_and_raw_previous_hash_required(chain, change):
    folder, _ = chain
    request, events, evidence = originals(folder)
    first = sorted(events)[0]
    if change == 'filename':
        events['events/'+first] = events.pop(first)
    elif change == 'missing_first':
        events.pop(first)
    else:
        request += b' '
    with pytest.raises(ValueError, match='CHANGE_EVENT_CHAIN_INVALID'):
        changes.validate_originals(request, events, evidence.__getitem__)


def test_rehashed_application_without_authorization_still_refuses(chain):
    folder, _ = chain
    request, events, evidence = originals(folder)
    event = json.loads(events[sorted(events)[1]])
    event.update(sequence=1, previous_sha256=changes.digest(request))
    core = {k: v for k, v in event.items() if k != 'identity'}
    event['identity'] = changes.digest(changes.encoded(core))
    altered = {f'0001-{event["identity"]}.json': changes.encoded(event)+b'\n'}
    with pytest.raises(ValueError, match='CHANGE_AUTHORIZATION_RECORD_REQUIRED'):
        changes.validate_originals(request, altered, evidence.__getitem__)


@pytest.mark.parametrize('kind', ['request', 'event', 'evidence'])
def test_memory_original_size_and_type_bounds(chain, kind):
    folder, _ = chain
    request, events, evidence = originals(folder)
    for bad, error in [(b'x'*100001, 'CHANGE_RECORD_TOO_LARGE'),
                       ('not bytes', 'CHANGE_ORIGINAL_BYTES_REQUIRED')]:
        r, e, v = request, dict(events), dict(evidence)
        if kind == 'request':
            r = bad
        elif kind == 'event':
            e[sorted(e)[0]] = bad
        else:
            v[next(iter(v))] = bad
        with pytest.raises(ValueError, match=error):
            changes.validate_originals(r, e, v.__getitem__)


def test_request_exact_size_boundary_and_missing_evidence_fail_closed(chain):
    folder, _ = chain
    request, events, evidence = originals(folder)
    padded = request+b' '*(100000-len(request))
    empty = changes.validate_originals(padded, {}, evidence.__getitem__)
    assert empty['head_sha256'] == changes.digest(padded)
    with pytest.raises(KeyError):
        changes.validate_originals(request, events, {}.__getitem__)


@pytest.mark.parametrize('target', ['request', 'event', 'evidence'])
def test_load_preserves_private_file_checks(chain, target):
    folder, _ = chain
    if target == 'request':
        path = folder/'request.json'
    elif target == 'event':
        path = next((folder/'events').glob('*.json'))
    else:
        path = next((folder/'evidence').iterdir())
    path.chmod(0o644)
    with pytest.raises(ValueError, match='CHANGE_PRIVATE_FILE_REQUIRED'):
        changes.load(folder)


def test_load_keeps_symlink_guard(chain, tmp_path):
    folder, _ = chain
    link = tmp_path/'linked'
    link.symlink_to(folder, target_is_directory=True)
    with pytest.raises(ValueError, match='CHANGE_SYMLINK_REJECTED'):
        changes.load(link)
