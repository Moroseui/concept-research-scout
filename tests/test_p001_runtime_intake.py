"""Synthetic filesystem and MCP transcript risk tests; no live Colab/model calls."""
import copy
import io
import json
from pathlib import Path
from types import SimpleNamespace
import stat

import pytest

from orchestrator import p001_runtime_intake as intake


@pytest.fixture
def bound_packet():
    return intake.packet('p001-runtime-readonly-fixture')


@pytest.fixture
def runtime(monkeypatch, bound_packet):
    request = bound_packet['request']
    source = request['source_files'][0]['path']
    # No archive or output payload is supplied to this synthetic filesystem.
    files = {source: b'synthetic source differs from frozen hash',
             request['checkouts'][0][0] + '/.git/HEAD': (intake.SOURCE_PIN + '\n').encode(),
             '/proc/sys/kernel/random/boot_id': b'12345678-abcd-abcd-abcd-123456789abc\n'}
    def proc_stat(start):
        return b'321 (comm (spaces)) S ' + b'0 ' * 18 + str(start).encode() + b'\n'
    files.update({'/proc/999/stat': proc_stat(77), '/proc/321/stat': proc_stat(88),
                  '/proc/321/cmdline': (source + '\x00--archive\x00PRIVATE_ARGUMENT_MUST_NOT_ESCAPE').encode()})
    directories = {'/', '/content/drive/MyDrive', request['dependency_root'],
                   request['execution_paths']['private_root'], request['execution_paths']['output_root']}
    for path in [*files, *directories, request['archive']]:
        directories.update(str(parent) for parent in Path(path).parents)
    state = {'mounted': True, 'denied': set(), 'symlinks': set(), 'files': files,
             'opens': [], 'proc_entries': ['321'], 'stat_calls': 0, 'race': False}
    def info(path):
        path = str(path)
        if path in state['denied']:
            raise PermissionError(path)
        if path in state['symlinks']:
            return SimpleNamespace(st_mode=stat.S_IFLNK, st_size=1, st_mtime_ns=2)
        if path in directories:
            return SimpleNamespace(st_mode=stat.S_IFDIR, st_size=0, st_mtime_ns=2)
        if path in files or path == request['archive']:
            size = len(files[path]) if path in files else 99014629647
            return SimpleNamespace(st_mode=stat.S_IFREG, st_size=size, st_mtime_ns=2)
        raise FileNotFoundError(path)
    def read(path, mode='r', *args, **kwargs):
        assert mode == 'rb'
        path = str(path)
        state['opens'].append(path)
        assert path != request['archive'], 'archive payload opened'
        assert not path.startswith(intake.OUTPUT), 'execution payload opened'
        if path == '/proc/321/stat':
            state['stat_calls'] += 1
            if state['race'] and state['stat_calls'] % 2 == 0:
                return io.BytesIO(proc_stat(99))
        return io.BytesIO(files[path])
    class Scan:
        def __enter__(self):
            return iter(SimpleNamespace(name=name) for name in state['proc_entries'])
        def __exit__(self, *args):
            return False
    monkeypatch.setattr(Path, 'lstat', lambda self: info(self))
    monkeypatch.setattr('os.stat', lambda path, **kwargs: info(path))
    monkeypatch.setattr('os.path.ismount', lambda path: state['mounted'])
    monkeypatch.setattr('builtins.open', read)
    monkeypatch.setattr('os.scandir', lambda path: Scan())
    monkeypatch.setattr('os.getpid', lambda: 999)
    monkeypatch.setattr('shutil.which', lambda name: None)
    monkeypatch.setenv('COLAB_RELEASE_TAG', 'synthetic')
    monkeypatch.setattr('importlib.metadata.distributions', lambda path: iter([
        SimpleNamespace(metadata={'Name': 'numpy'}, version='2.3.3'),
        SimpleNamespace(metadata={'Name': 'nibabel'}, version='5.3.2')]))
    return state, request


def test_packet_is_frozen_compilable_and_does_not_contain_mutating_calls(bound_packet):
    for cell in bound_packet['cells']:
        compile(cell, 'collector', 'exec')
    collector = bound_packet['cells'][1]
    for forbidden in ['subprocess', 'drive.mount', 'pip install', 'git fetch', 'os.mkdir', '.write_text(', '.write_bytes(']:
        assert forbidden not in collector
    assert bound_packet['pins']['execution'] == '0770c7dcabe781cbfb87de505755e7aafa758f2e'
    assert len(bound_packet['request']['source_files']) == 9
    for bad in ['', '../escape', 'arbitrary\nrequest', 'x' * 81]:
        with pytest.raises(ValueError, match='REQUEST_ID'):
            intake.packet(bad)


def test_metadata_collection_never_opens_archive_or_outputs_and_never_attests_pid(runtime):
    state, request = runtime
    observed = intake.runtime_observation(request)
    assert observed['archive']['size_bytes'] == 99014629647
    assert observed['runtime']['fingerprint_sha256']
    assert observed['runtime']['provider_session_id'] is None
    assert observed['source_files'][0]['matches_expected'] is False
    assert observed['source_files'][1]['state'] == 'ABSENT_IN_VISIBLE_PARENT'
    assert observed['execution_paths']['private_root']['state'] == 'PRESENT'
    assert observed['execution_paths']['checkpoint_index']['state'] == 'ABSENT_IN_VISIBLE_PARENT'
    assert observed['processes']['matches'] == [{'pid': 321, 'start_ticks': 88, 'kinds': ['P001_EXECUTION'],
        'historical_identity': 'UNPROVEN_NO_HISTORICAL_START_TICKS'}]
    assert observed['processes']['historical_pid_record_verified'] is False
    assert observed['dependencies']['packages'][0]['versions'] == ['2.3.3']
    assert 'PRIVATE_ARGUMENT_MUST_NOT_ESCAPE' not in json.dumps(observed)
    assert observed['launch_authorized'] is False


def test_unmounted_drive_is_not_absence_and_no_drive_paths_are_opened(runtime):
    state, request = runtime
    state['mounted'] = False
    observed = intake.runtime_observation(request)
    assert observed['archive'] == {'state': 'NOT_VISIBLE'}
    assert all(row == {'state': 'NOT_VISIBLE'} for row in observed['execution_paths'].values())
    assert not any(path.startswith('/content/drive') for path in state['opens'])


def test_denied_ancestor_and_symlink_are_never_absence(runtime):
    state, request = runtime
    state['denied'].add('/content/drive/MyDrive/isles-pilot')
    state['symlinks'].add(request['checkouts'][0][0])
    observed = intake.runtime_observation(request)
    assert observed['archive']['state'] == 'NOT_VISIBLE'
    assert observed['source_files'][0]['state'] == 'SYMLINK_REJECTED'
    assert not any(path.startswith(request['checkouts'][0][0]) for path in state['opens'])


def test_process_identity_race_and_unreadable_cmdline_make_scan_incomplete(runtime):
    state, request = runtime
    state['race'] = True
    observed = intake.runtime_observation(request)
    assert observed['processes']['scan_complete'] is False
    assert observed['processes']['matches'] == []
    state['race'] = False
    state['denied'].add('/proc/321/cmdline')
    observed = intake.runtime_observation(request)
    assert observed['processes']['scan_complete'] is False
    assert observed['processes']['matches'] == []


def test_worker_run_py_and_preflight_are_both_detected(runtime):
    state, request = runtime
    state['files']['/proc/321/cmdline'] = (intake.OUTPUT + '.worker/run.py\x00' + intake.PREFLIGHT).encode()
    matches = intake.runtime_observation(request)['processes']['matches']
    assert matches[0]['kinds'] == ['P001_EXECUTION', 'P001_PREFLIGHT']


def transcript(bound_packet, observed):
    events = []
    def exchange(name, args, result):
        identity = str(len(events))
        events.append({'type': 'assistant', 'message': {'content': [
            {'type': 'tool_use', 'id': identity, 'name': 'mcp__colab-worker__' + name, 'input': args}]}})
        events.append({'type': 'user', 'message': {'content': [
            {'type': 'tool_result', 'tool_use_id': identity, 'content': json.dumps(result)}]}})
    for index, source in enumerate(bound_packet['cells']):
        cell = str(index)
        exchange('add_code_cell', {'code': source}, {'newCellId': cell})
        exchange('get_cells', {'includeOutputs': False}, {'cells': [{'id': cell, 'source': [source]}]})
        output = {'cpu_only': True, 'colab_runtime': True} if index == 0 else observed
        exchange('run_code_cell', {'cellId': cell}, {'outputs': [{'output_type': 'stream', 'text': [json.dumps(output)]}]})
    return events


def test_actual_protocol_required_not_model_claim(runtime, bound_packet, monkeypatch):
    state, request = runtime
    observed = intake.runtime_observation(request)
    # Pin rebuilding is a local Git read and is separately exercised by packet fixture.
    monkeypatch.setattr(intake, 'packet', lambda request_id: bound_packet)
    events = transcript(bound_packet, observed)
    value = intake.verify_transcript(bound_packet, events)
    assert value['status'] == 'READ_ONLY_RUNTIME_EVIDENCE_RECORDED'
    assert value['scientific_acceptance'] is False
    with pytest.raises(ValueError, match='incomplete'):
        intake.verify_transcript(bound_packet, [{'type': 'result', 'structured_output': observed}])
    changed = copy.deepcopy(events)
    changed[2]['message']['content'][0]['input']['includeOutputs'] = True
    with pytest.raises(ValueError, match='must not be read'):
        intake.verify_transcript(bound_packet, changed)
    changed = copy.deepcopy(events)
    changed[0]['message']['content'][0]['input']['code'] += '\nprint("extra")'
    with pytest.raises(ValueError, match='executed source not bound'):
        intake.verify_transcript(bound_packet, changed)
    changed_observation = copy.deepcopy(observed)
    changed_observation['launch_authorized'] = True
    with pytest.raises(ValueError, match='OBSERVATION_BINDING'):
        intake.verify_transcript(bound_packet, transcript(bound_packet, changed_observation))
    changed_observation = copy.deepcopy(observed)
    changed_observation['patient_detail'] = 'injected'
    with pytest.raises(ValueError, match='OBSERVATION_SCHEMA'):
        intake.verify_transcript(bound_packet, transcript(bound_packet, changed_observation))

def test_generated_cell_executes_self_contained(runtime, bound_packet):
    import contextlib
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(bound_packet['cells'][1], 'generated-cell', 'exec'), {})
    observed = json.loads(output.getvalue())
    assert observed['schema'] == 'p001-current-runtime/v1'
    assert observed['request_id'] == bound_packet['request']['request_id']


def test_oversized_process_metadata_preserves_uncertainty(runtime):
    state, request = runtime
    state['files']['/proc/321/cmdline'] = b'x' * 65537
    observed = intake.runtime_observation(request)
    assert observed['processes']['scan_complete'] is False
    assert observed['processes']['matches'] == []


def test_nested_unrecognized_metadata_cannot_be_exported(runtime, bound_packet, monkeypatch):
    state, request = runtime
    observed = intake.runtime_observation(request)
    monkeypatch.setattr(intake, 'packet', lambda request_id: bound_packet)
    observed['runtime']['credential'] = 'private injected text'
    with pytest.raises(ValueError, match='OBSERVATION_FIELDS'):
        intake.verify_transcript(bound_packet, transcript(bound_packet, observed))
