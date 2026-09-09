"""Synthetic complete-return transport tests; never execute scientific validation."""
import hashlib
import json
import os
from pathlib import Path
import stat
import struct
from types import SimpleNamespace
import warnings
import zipfile

import pytest

from orchestrator import p001_return_intake as intake


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    tmp_path.chmod(0o700)
    cases = ['synthetic-' + str(i).zfill(3) for i in range(99)]
    names = {'bundle/' + name for name in intake.AGGREGATES} | {'console.log', 'private/binding.json', 'private/checkpoint_index.json'}
    names.update('private/checkpoints/' + case + '.json' for case in cases)
    names.update('private/predictions/' + case + '.npy' for case in cases)
    assert len(names) == 206
    monkeypatch.setattr(intake, 'expected_members', lambda snapshot: names)
    archive = tmp_path / 'original.zip'
    receipt = tmp_path / 'terminal.json'
    state = {'archive': archive, 'receipt': receipt, 'names': names, 'parent': tmp_path,
             'destination': tmp_path / 'extracted', 'snapshot': tmp_path / 'frozen',
             'max_extracted': 65536, 'request_id': 'p001-return-fixture', 'runtime': 'a' * 64,
             'manifest': 'b' * 64}
    def write(entries=None):
        entries = entries if entries is not None else [(name, b'synthetic-private-bytes') for name in sorted(names)]
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
                for name, raw in entries:
                    if isinstance(name, zipfile.ZipInfo):
                        name.compress_type = zipfile.ZIP_DEFLATED
                    z.writestr(name, raw)
        bind()
    def bind():
        raw = archive.read_bytes()
        value = {'schema': 'p001-full-return-terminal/v1', 'request_id': state['request_id'],
                 'runtime_fingerprint_sha256': state['runtime'], 'worker_status': 'VALIDATED',
                 'execution_snapshot': intake.EXECUTION_PIN, 'source_pin': intake.SOURCE_PIN,
                 'notebook_pin': intake.NOTEBOOK_PIN, 'zip_name': 'P001-private-return.zip',
                 'zip_bytes': len(raw), 'zip_sha256': hashlib.sha256(raw).hexdigest(),
                 'launch_manifest_sha256': state['manifest'], 'max_extracted_bytes': state['max_extracted']}
        receipt.write_text(json.dumps(value))
    state.update(write=write, bind=bind)
    write()
    return state


def extract(state):
    return intake.extract(state['archive'], state['receipt'], state['destination'], state['snapshot'],
                          request_id=state['request_id'], runtime_fingerprint=state['runtime'],
                          launch_manifest_sha256=state['manifest'], max_extracted_bytes=state['max_extracted'])


def test_complete206_extraction_preserves_originals_and_emits_unchanged_validator_argv(fixture, monkeypatch):
    original, terminal = fixture['archive'].read_bytes(), fixture['receipt'].read_bytes()
    monkeypatch.setattr('subprocess.run', lambda *a, **k: (_ for _ in ()).throw(AssertionError('science executed')))
    result = extract(fixture)
    assert result['status'] == 'EXTRACTED_PENDING_FROZEN_VALIDATION'
    assert result['member_count'] == 206
    assert result['validation_executed'] is False and result['scientific_acceptance'] is False
    assert result['transfer_authority_granted_by_intake'] is False
    assert result['validation_argv'][1].endswith('/campaigns/isles24-pilot/experiments/P001/validate_return.py')
    assert result['validation_argv'][2:] == ['--bundle', str(fixture['destination'] / 'bundle'),
        '--private', str(fixture['destination'] / 'private'), '--console', str(fixture['destination'] / 'console.log')]
    inventory = json.loads((fixture['destination'] / 'member-inventory.private.json').read_text())
    assert set(inventory) == fixture['names']
    assert fixture['archive'].read_bytes() == original
    assert fixture['receipt'].read_bytes() == terminal
    assert fixture['destination'].stat().st_mode & 0o077 == 0
    assert all((fixture['destination'] / name).stat().st_mode & 0o077 == 0 for name in fixture['names'])
    assert 'synthetic-000' not in json.dumps(result)


def test_existing_destination_never_retries_or_overwrites(fixture):
    fixture['destination'].mkdir(mode=0o700)
    marker = fixture['destination'] / 'preserve'
    marker.write_bytes(b'interrupted original')
    with pytest.raises(ValueError, match='EXISTING_DESTINATION_RECONCILE'):
        extract(fixture)
    assert marker.read_bytes() == b'interrupted original'
    assert sorted(p.name for p in fixture['destination'].iterdir()) == ['preserve']


@pytest.mark.parametrize('change', ['duplicate', 'traversal', 'extra', 'symlink', 'directory'])
def test_unsafe_or_unexpected_member_sets_refuse_before_extraction(fixture, change):
    entries = [(name, b'x') for name in sorted(fixture['names'])]
    if change == 'duplicate':
        entries[-1] = entries[0]
    elif change == 'traversal':
        entries[-1] = ('../outside', b'x')
    elif change == 'extra':
        entries[-1] = ('unexpected.py', b'x')
    elif change == 'symlink':
        info = zipfile.ZipInfo(entries[0][0])
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        entries[0] = (info, b'../../outside')
    else:
        info = zipfile.ZipInfo(entries[0][0])
        info.external_attr = (stat.S_IFDIR | 0o700) << 16
        entries[0] = (info, b'')
    fixture['write'](entries)
    with pytest.raises(ValueError, match='P001_RETURN_MEMBER_'):
        extract(fixture)
    assert not fixture['destination'].exists()
    assert not (fixture['parent'] / 'outside').exists()


def test_bomb_like_expansion_refuses_before_writing(fixture):
    entries = [(name, b'x') for name in sorted(fixture['names'])]
    entries[0] = (entries[0][0], b'0' * (1 << 20))
    fixture['write'](entries)
    assert fixture['archive'].stat().st_size < fixture['max_extracted']
    with pytest.raises(ValueError, match='EXPANSION_CAP'):
        extract(fixture)
    assert not fixture['destination'].exists()


def test_disk_capacity_and_private_parent_are_checked_before_writing(fixture, monkeypatch):
    monkeypatch.setattr('shutil.disk_usage', lambda path: SimpleNamespace(free=1))
    with pytest.raises(ValueError, match='DISK_CAPACITY'):
        extract(fixture)
    fixture['parent'].chmod(0o755)
    with pytest.raises(ValueError, match='PRIVATE_PARENT_REQUIRED'):
        extract(fixture)
    assert not fixture['destination'].exists()


def test_combined_cap_counts_zip_and_receipt_not_individual_sizes(fixture, monkeypatch):
    monkeypatch.setattr(intake, 'TRANSFER_CAP', fixture['archive'].stat().st_size + fixture['receipt'].stat().st_size - 1)
    with pytest.raises(ValueError, match='COMBINED_TRANSFER_CAP'):
        extract(fixture)
    assert not fixture['destination'].exists()


@pytest.mark.parametrize('field', ['request_id', 'runtime_fingerprint_sha256', 'launch_manifest_sha256', 'max_extracted_bytes', 'worker_status'])
def test_launch_attempt_runtime_and_operational_cap_are_bound(fixture, field):
    value = json.loads(fixture['receipt'].read_text())
    value[field] = 1 if field == 'max_extracted_bytes' else 'different'
    fixture['receipt'].write_text(json.dumps(value))
    with pytest.raises(ValueError, match='TERMINAL_BINDING'):
        extract(fixture)
    assert not fixture['destination'].exists()


def test_input_symlink_and_destination_parent_symlink_refuse(fixture):
    link = fixture['parent'] / 'link.zip'
    link.symlink_to(fixture['archive'])
    original = fixture['archive']
    fixture['archive'] = link
    with pytest.raises(ValueError, match='REGULAR_FILE_REQUIRED'):
        extract(fixture)
    fixture['archive'] = original
    folder = fixture['parent'] / 'linked-parent'
    folder.symlink_to(fixture['parent'], target_is_directory=True)
    fixture['destination'] = folder / 'extracted'
    with pytest.raises(ValueError, match='DESTINATION_ANCESTOR'):
        extract(fixture)
    assert not (fixture['parent'] / 'extracted').exists()


def test_central_directory_entry_count_is_bounded_before_zip_reader(fixture, monkeypatch):
    raw = bytearray(fixture['archive'].read_bytes())
    struct.pack_into('<HH', raw, len(raw) - 22 + 8, 65535, 65535)
    fixture['archive'].write_bytes(raw)
    fixture['bind']()
    monkeypatch.setattr(zipfile, 'ZipFile', lambda *a, **k: (_ for _ in ()).throw(AssertionError('unbounded directory parsed')))
    with pytest.raises(ValueError, match='ZIP_DIRECTORY'):
        extract(fixture)


def test_mutated_original_during_extraction_preserves_partial_state(fixture, monkeypatch):
    original_open = zipfile.ZipFile.open
    calls = []
    def changing_open(archive, *args, **kwargs):
        if not calls:
            with fixture['archive'].open('ab') as handle:
                handle.write(b'externally changed')
        calls.append(True)
        return original_open(archive, *args, **kwargs)
    monkeypatch.setattr(zipfile.ZipFile, 'open', changing_open)
    with pytest.raises(ValueError, match='ORIGINAL_CHANGED_DURING_EXTRACTION'):
        extract(fixture)
    assert (fixture['destination'] / 'intake-intent.json').is_file()
    failure = json.loads((fixture['destination'] / 'intake-failure.json').read_text())
    assert failure['status'] == 'PRESERVED_PARTIAL_INTAKE_RECONCILE'
    assert not (fixture['destination'] / 'intake-receipt.json').exists()
    assert fixture['archive'].read_bytes().endswith(b'externally changed')


def test_frozen_selection_is_reused_without_scientific_run(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(intake, 'frozen_sources', lambda snapshot: calls.append('review'))
    def run(command, **kwargs):
        assert 'module.selection()' in command[4]
        assert 'module.run(' not in command[4]
        return SimpleNamespace(returncode=0, stdout=json.dumps(['synthetic-' + str(i) for i in range(99)]).encode())
    monkeypatch.setattr('subprocess.run', run)
    assert len(intake.expected_members(tmp_path / 'snapshot')) == 206
    assert calls == ['review']


def test_cli_never_exposes_private_exception_paths(tmp_path, monkeypatch, capsys):
    import sys
    monkeypatch.setattr(sys, 'argv', ['p001_return_intake', '--zip', 'z', '--terminal-receipt', 'r',
        '--destination', 'd', '--frozen-snapshot', 's', '--request-id', 'fixture',
        '--runtime-fingerprint', 'a' * 64, '--launch-manifest-sha256', 'b' * 64, '--max-extracted-bytes', '1'])
    monkeypatch.setattr(intake, 'extract', lambda *a, **k: (_ for _ in ()).throw(OSError('PRIVATE_CASE_PATH_MUST_NOT_ESCAPE')))
    with pytest.raises(SystemExit) as error:
        intake.main()
    assert error.value.code == 1
    output = capsys.readouterr().out
    assert 'PRIVATE_CASE_PATH' not in output
    assert json.loads(output)['status'] == 'BLOCKED_RECONCILE'


def test_fifo_is_rejected_before_open(tmp_path, monkeypatch):
    fifo = tmp_path / 'input.fifo'
    os.mkfifo(fifo, mode=0o600)
    monkeypatch.setattr(intake.os, 'open', lambda *a, **k: (_ for _ in ()).throw(AssertionError('FIFO opened')))
    with pytest.raises(ValueError, match='REGULAR_FILE_REQUIRED'):
        intake.regular_file(fifo)


@pytest.mark.parametrize('replacement', ['fifo', 'regular'])
def test_file_replacement_race_uses_nonblocking_open_and_checks_identity(tmp_path, monkeypatch, replacement):
    path = tmp_path / 'input'
    path.write_bytes(b'original')
    original_open = os.open
    def replace_before_open(name, flags, *args):
        assert flags & os.O_NONBLOCK and flags & os.O_NOFOLLOW
        path.rename(tmp_path / 'preserved-original')
        if replacement == 'fifo':
            os.mkfifo(path, mode=0o600)
        else:
            path.write_bytes(b'different regular file')
        return original_open(name, flags, *args)
    monkeypatch.setattr(intake.os, 'open', replace_before_open)
    with pytest.raises(ValueError, match='FILE_CHANGED_BEFORE_OPEN'):
        intake.regular_file(path)
    assert (tmp_path / 'preserved-original').read_bytes() == b'original'


def test_duplicate_terminal_receipt_key_refuses_even_when_value_matches(fixture):
    raw = fixture['receipt'].read_text()
    fixture['receipt'].write_text(raw[:-1] + ', "worker_status": "VALIDATED"}')
    with pytest.raises(ValueError, match='TERMINAL_RECEIPT_SCHEMA'):
        extract(fixture)
    assert not fixture['destination'].exists()
