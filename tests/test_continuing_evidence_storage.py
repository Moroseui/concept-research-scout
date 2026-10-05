"""Synthetic private evidence fixtures; no model, admission or scientific result."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator import continuing_research as continuing
from orchestrator import investigator_wakes as wakes
from orchestrator import research_task_authority as authority
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded, immutable


@pytest.fixture
def config(tmp_path):
    tmp_path.chmod(0o700)
    return {'state': str(tmp_path), 'controller_uid': os.getuid(),
            'controller_gid': os.getgid(), 'source': 'a' * 40,
            'source_root': str(tmp_path)}


def original_store(config, raw):
    folder = Path(config['state']) / 'continuing-evidence'
    folder.mkdir(mode=0o700, exist_ok=True)
    sha = hashlib.sha256(raw).hexdigest()
    path = folder / (sha + '.json')
    immutable(path, raw)
    return {'evidence_file': str(path), 'evidence_sha256': sha}


def test_large_nested_evidence_preserves_every_original_and_object_identity(config):
    # Indented object overhead, not lost fields, accounts for the original refusal.
    literals = ['First\r\nSecond\n', 'Quoted "text" and \\ path', 'Cafe \u00e9 \U0001f680']
    value = {'events': [{'sequence': i, 'state': 'PENDING', 'data': [True, None, i]}
                        for i in range(9000)],
             'originals': {str(i): {'text': s, 'sha256': hashlib.sha256(s.encode()).hexdigest()}
                           for i, s in enumerate(literals)}}
    before = deepcopy(value)
    old = encoded(value)
    assert len(old) > 750000
    record = continuing.preserve_evidence(config, value)
    path = Path(record['evidence_file'])
    raw = path.read_bytes()
    assert len(raw) < 750000
    assert hashlib.sha256(raw).hexdigest() == record['evidence_sha256'] == path.stem
    assert continuing.read_evidence(config, record) == before == value
    assert encoded(json.loads(raw)) == old
    for item in continuing.read_evidence(config, record)['originals'].values():
        assert hashlib.sha256(item['text'].encode()).hexdigest() == item['sha256']
    assert continuing.preserve_evidence(config, dict(reversed(list(value.items())))) == record
    assert path.stat().st_mode & 0o777 == 0o600


def test_existing_pretty_original_remains_readable_and_immutable(config):
    value = {'original': 'Mixed\r\nlines\n and \u00e9', 'result': {'accepted': False}}
    old_raw = encoded(value)
    old_record = original_store(config, old_raw)
    old_path = Path(old_record['evidence_file'])
    old_inode = old_path.stat().st_ino
    new_record = continuing.preserve_evidence(config, value)
    assert new_record != old_record
    assert continuing.read_evidence(config, old_record) == continuing.read_evidence(config, new_record) == value
    assert old_path.read_bytes() == old_raw and old_path.stat().st_ino == old_inode
    # An object's equal meaning cannot substitute for the exact saved raw digest.
    Path(new_record['evidence_file']).write_bytes(old_raw)
    with pytest.raises(ValueError, match='CONTINUING_EVIDENCE_CHANGED'):
        continuing.read_evidence(config, new_record)


@pytest.mark.parametrize('character,unit', [('x', 1), ('\u00e9', 6)])
def test_unchanged_byte_cap_accepts_exact_boundary_and_refuses_one_over(config, character, unit):
    overhead = len(b'{"body":""}\n')
    count, padding = divmod(750000 - overhead, unit)
    value = {'body': character * count + 'x' * padding}
    record = continuing.preserve_evidence(config, value)
    assert len(Path(record['evidence_file']).read_bytes()) == 750000
    assert continuing.read_evidence(config, record) == value
    value['body'] += 'x'
    before = sorted(Path(record['evidence_file']).parent.iterdir())
    with pytest.raises(ValueError, match='PUBLIC_TEXT_REJECTED'):
        continuing.preserve_evidence(config, value)
    assert sorted(Path(record['evidence_file']).parent.iterdir()) == before
    # The unchanged reader independently refuses a content-addressed oversized file.
    raw = Path(record['evidence_file']).read_bytes().replace(b'"}\n', b'x"}\n')
    oversized = original_store(config, raw)
    with pytest.raises(ValueError, match='CONTINUING_ORIGINAL_FILE_BOUND'):
        continuing.read_evidence(config, oversized)


def test_scanner_and_public_text_guards_still_apply_to_compact_bytes(config):
    unsafe = 'sub' + '_' + 'stroke' + '123'
    with pytest.raises(ValueError, match='PUBLIC_TEXT_REJECTED'):
        continuing.preserve_evidence(config, {'body': unsafe})
    assert not (Path(config['state']) / 'continuing-evidence').exists()
    # Write a synthetic refused file directly, then exercise the real read scanner.
    raw = json.dumps({'body': unsafe}, separators=(',', ':')).encode() + b'\n'
    folder = Path(config['state']) / 'continuing-evidence'
    folder.mkdir(mode=0o700)
    sha = hashlib.sha256(raw).hexdigest()
    path = folder / (sha + '.json')
    path.write_bytes(raw)
    path.chmod(0o600)
    with pytest.raises(ValueError, match='CASE_LEVEL_RECORD_REJECTED'):
        continuing.read_evidence(config, {'evidence_file': str(path), 'evidence_sha256': sha})


def test_native_entry_and_authority_consume_returned_raw_hash(config, monkeypatch, tmp_path):
    value = {'originals': {'text': 'Exact\r\nsynthetic \u00e9\n'}, 'events': []}
    task = {'schema': 'investigator-task/v1', 'task_id': 'synthetic-investigator-v1'}
    derived = {'task': task, 'evidence': value, 'predecessors': []}
    monkeypatch.setattr(wakes, 'regenerate', lambda cfg, manifest, client: derived)
    monkeypatch.setattr(wakes, '_client', lambda runtime: None)
    actor = {'kind': 'agent', 'identity': 'synthetic-service'}
    monkeypatch.setattr(wakes, 'service', lambda cfg: actor)
    change = {'request_id': 'b' * 64, 'applied_event': 'c' * 64}
    monkeypatch.setattr(wakes, 'setting', lambda cfg: {'template': {'change_request': change}})
    # Only wake derivation/identity are synthetic seams; real entry intake,
    # content-addressed storage, authority reader and digest functions run.
    entry = wakes._entry(SimpleNamespace(config=config), tmp_path / 'wake',
                         {'day': '2026-01-01'})
    request = entry['request']
    raw = Path(request['evidence_file']).read_bytes()
    assert request['evidence_sha256'] == hashlib.sha256(raw).hexdigest()
    assert request['evidence_sha256'] != hashlib.sha256(encoded(value)).hexdigest()
    assert authority._evidence(config, entry) == value
    assert entry['change_request'] == change
    identity = digest(entry)
    restored = json.loads(encoded(entry))
    assert digest(restored) == identity
    restored['request']['evidence_sha256'] = hashlib.sha256(encoded(value)).hexdigest()
    assert digest(restored) != identity
    with pytest.raises(ValueError, match='CONTINUING_EVIDENCE_CONTENT_ADDRESS_REQUIRED'):
        authority._evidence(config, restored)
