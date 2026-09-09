"""Setup-only tests: no model, Colab, package install or experiment invocation."""
import copy
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator import p001_runtime_setup as setup
from orchestrator import p001_runtime_intake as intake


@pytest.fixture
def inputs(monkeypatch):
    prior = intake.packet('runtime-observed-fixture')
    request = prior['request']
    absent = {'state': 'ABSENT_IN_VISIBLE_PARENT'}
    observed = {
        'schema': 'p001-current-runtime/v1', 'request_id': request['request_id'],
        'observed_at_unix_ns': 1000000000, 'observation_seconds': 1.0,
        'scope': 'CONNECTED_RUNTIME_ONLY_NOT_OTHER_OR_PRIOR_RUNTIMES',
        'launch_authorized': False, 'prediction_executed_by_collector': False,
        'cpu_guard': {'colab_runtime': True, 'nvidia_smi_absent': True},
        'runtime': {'fingerprint_sha256': 'a' * 64, 'boot_id_sha256': 'b' * 64,
                    'kernel_pid': 1, 'kernel_start_ticks': 1, 'provider_session_id': None,
                    'python_version': '3.12.0'},
        'drive': {'mounted': True, 'visible': True},
        'archive': {'state': 'PRESENT', 'kind': 'file', 'size_bytes': 99014629647, 'mtime_ns': 123},
        'source_files': [{'path': row['path'], 'expected_sha256': row['sha256'], **absent}
                         for row in request['source_files']],
        'checkout_heads': [{'expected_commit': pin, **absent} for root, pin in request['checkouts']],
        'dependencies': {'root': request['dependency_root'], 'root_metadata': absent,
                         'packages': [{'name': name, 'versions': [], 'scan_complete': False} for name in ['numpy', 'nibabel']],
                         'scope': 'DISTRIBUTION_METADATA_ONLY_NOT_IMPORT_OR_ENVIRONMENT_ATTESTATION'},
        'execution_paths': {name: copy.deepcopy(absent) for name in request['execution_paths']},
        'processes': {'scan_complete': True, 'scanned': 3, 'matches': [], 'historical_pid_record_verified': False},
    }
    receipt = {'status': 'READ_ONLY_RUNTIME_EVIDENCE_RECORDED', 'packet_sha256': setup.sha(setup.canonical(prior)),
               'observation': observed, 'scientific_acceptance': False, 'launch_authorized': False}
    # Keep real frozen notebook and existing capture bytes; avoid executing even the review
    # subprocess in unit tests. The live preparation separately verifies the full frozen review.
    notebook_raw = intake.git_bytes(intake.NOTEBOOK_PIN, 'campaigns/isles24-pilot/experiments/P001/colab_P001.ipynb')
    notebook = json.loads(notebook_raw)
    frozen = {'sources': [''.join(notebook['cells'][i]['source']) for i in [1, 3]],
              'notebook_sha256': setup.sha(notebook_raw), 'requirements_sha256': 'c' * 64,
              'capture_module_sha256': 'd' * 64, 'reviewed_commit': '465a0c3b1f2e8486a13e68dfd2179b3bfd16840d'}
    monkeypatch.setattr(setup, 'frozen_sources', lambda snapshot: frozen)
    return prior, receipt, frozen


def make_packet(inputs, request_id='setup-fixture'):
    prior, receipt, _ = inputs
    return setup.packet(Path('/synthetic/private/frozen'), prior, receipt, request_id)


def environment():
    inventory = [{'name': 'nibabel', 'version': '5.3.2'}, {'name': 'numpy', 'version': '2.3.3'}]
    return {'schema': 'p001-default-child-environment/v1', 'scope': setup.SCOPE,
            'python_version': '3.12.0', 'python_executable': '/usr/bin/python3.12',
            'source_root': setup.SOURCE_ROOT,
            'packages': [{'name': name, 'distribution_version': version, 'import_version': version,
                          'origin': '/usr/local/lib/python3.12/dist-packages/' + name + '/__init__.py'}
                         for name, version in [('numpy', '2.3.3'), ('nibabel', '5.3.2')]],
            'inventory': inventory, 'inventory_sha256': setup.sha(setup.canonical(inventory)),
            'seven_zip': {'path': '/usr/bin/7z', 'version': '16.02'},
            'patient_files_opened': False, 'prediction_executed': False,
            'limitations': 'Fresh child import probe; no scientific run, wheel-byte attestation or future environment immutability claim.'}


def test_packet_reuses_frozen_cells_compiles_and_excludes_experiment_cells(inputs):
    packet = make_packet(inputs)
    for source in packet['cells']:
        compile(source, 'setup-packet', 'exec')
    for exact in inputs[2]['sources']:
        assert repr(exact) in packet['cells'][1]
    assert 'archive.open' not in packet['cells'][1]
    assert 'run_logged' not in packet['cells'][1]
    assert "'--output-dir'" not in packet['cells'][1]
    assert packet['patient_launch_authorized'] is False
    # Another request cannot gain a fresh setup directory on the same runtime.
    assert make_packet(inputs, 'second-request')['request']['setup_root'] == packet['request']['setup_root']


@pytest.mark.parametrize('mutation,error', [
    (lambda o: o['runtime'].update(fingerprint_sha256='e' * 64), 'RUNTIME_CHANGED'),
    (lambda o: o['drive'].update(visible=False), 'DRIVE_NOT_VISIBLE'),
    (lambda o: o['archive'].update(mtime_ns=124), 'ARCHIVE_METADATA_CHANGED'),
    (lambda o: o['processes'].update(scan_complete=False), 'UNCERTAIN_PROCESS'),
    (lambda o: o['processes'].update(matches=[{'pid': 3}]), 'UNCERTAIN_PROCESS'),
    (lambda o: o['execution_paths'].update(checkpoint_index={'state': 'NOT_VISIBLE'}), 'UNCERTAIN_PREDICTION_PATH'),
    (lambda o: o['source_files'][0].update(state='PRESENT'), 'UNCERTAIN_SOURCE'),
])
def test_pre_mutation_guard_refuses_stale_or_uncertain_state(inputs, mutation, error):
    packet = make_packet(inputs)
    changed = copy.deepcopy(inputs[1]['observation'])
    mutation(changed)
    with pytest.raises(ValueError, match=error):
        setup.check_observation(changed, packet['request'], source_absent=True)


def test_exclusive_intent_and_logs_preserve_collisions_without_creating_source(tmp_path):
    request = {'source_root': str(tmp_path / 'frozen-source'), 'setup_root': str(tmp_path / 'setup'),
               'request_id': 'fixture', 'runtime_fingerprint_sha256': 'a' * 64, 'binding_sha256': 'b' * 64}
    setup.claim_setup(request)
    destination = Path(request['setup_root'])
    original = (destination / 'intent.json').read_bytes()
    assert json.loads(original)['prediction_launch_authorized'] is False
    assert not Path(request['source_root']).exists()
    assert sorted(p.name for p in destination.iterdir()) == ['acquisition.console.log', 'dependencies.console.log', 'intent.json', 'seven-zip.console.log']
    with pytest.raises(ValueError, match='ALREADY_EXISTS_RECONCILE'):
        setup.claim_setup(request)
    assert (destination / 'intent.json').read_bytes() == original


def test_existing_empty_source_or_symlink_refuses_before_any_setup_write(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    request = {'source_root': str(source), 'setup_root': str(tmp_path / 'setup')}
    with pytest.raises(ValueError, match='ALREADY_EXISTS'):
        setup.claim_setup(request)
    assert not (tmp_path / 'setup').exists()
    request['source_root'] = str(tmp_path / 'missing')
    link = tmp_path / 'link'
    link.symlink_to(tmp_path, target_is_directory=True)
    request['setup_root'] = str(link / 'setup')
    with pytest.raises(ValueError, match='SYMLINK'):
        setup.claim_setup(request)
    assert not (tmp_path / 'setup').exists()


def test_environment_nested_fields_and_import_domains_reject_private_paths():
    setup.validate_environment(environment())
    value = environment()
    value['packages'][0]['origin'] = '/content/drive/MyDrive/patient/numpy/__init__.py'
    with pytest.raises(ValueError, match='ENVIRONMENT_SCHEMA'):
        setup.validate_environment(value)
    value = environment()
    value['seven_zip']['private_log'] = 'untrusted details'
    with pytest.raises(ValueError, match='ENVIRONMENT_SCHEMA'):
        setup.validate_environment(value)
    value = environment()
    value['inventory'][0]['version'] = 'private\ntext'
    with pytest.raises(ValueError, match='ENVIRONMENT_SCHEMA'):
        setup.validate_environment(value)


def test_child_probe_checks_import_origin_before_importing(monkeypatch):
    monkeypatch.setattr('importlib.metadata.distribution', lambda name: SimpleNamespace(
        locate_file=lambda path: '/usr/local/lib/python3.12/dist-packages/' + path, version='2.3.3'))
    monkeypatch.setattr('importlib.util.find_spec', lambda name: SimpleNamespace(origin='/content/private/numpy/__init__.py'))
    monkeypatch.setattr('importlib.import_module', lambda name: (_ for _ in ()).throw(AssertionError('untrusted module imported')))
    with pytest.raises(ValueError, match='OUTSIDE_DEFAULT_PACKAGE_DOMAIN'):
        setup.child_environment(setup.SOURCE_ROOT)


def transcript(packet, env):
    events = []
    def exchange(name, args, result):
        identity = str(len(events))
        events.append({'type': 'assistant', 'message': {'content': [
            {'type': 'tool_use', 'id': identity, 'name': 'mcp__colab-worker__' + name, 'input': args}]}})
        events.append({'type': 'user', 'message': {'content': [
            {'type': 'tool_result', 'tool_use_id': identity, 'content': json.dumps(result)}]}})
    for index, source in enumerate(packet['cells']):
        cell = str(index)
        exchange('add_code_cell', {'code': source}, {'newCellId': cell})
        exchange('get_cells', {'includeOutputs': False}, {'cells': [{'id': cell, 'source': [source]}]})
        if index == 0:
            output = json.dumps({'cpu_only': True, 'colab_runtime': True})
        elif index == 1:
            output = '\n'.join([*[repr({'transport_status': 'COMPLETE', 'source_sha256': sha}) for sha in packet['request']['source_sha256']],
                json.dumps({'status': 'SOURCE_DEPENDENCY_SETUP_COMPLETE', 'binding_sha256': packet['request']['binding_sha256'], 'patient_launch_authorized': False})])
        else:
            output = json.dumps({'status': 'DEFAULT_CHILD_ENVIRONMENT_OBSERVED', 'binding_sha256': packet['request']['binding_sha256'], 'environment': env})
        exchange('run_code_cell', {'cellId': cell}, {'outputs': [{'output_type': 'stream', 'text': [output]}]})
    return events


def verify(packet, events, inputs):
    return setup.verify_transcript(packet, events, snapshot=Path('/synthetic/private/frozen'),
                                   runtime_packet=inputs[0], runtime_receipt=inputs[1])


def test_actual_transcript_source_readback_and_packet_required(inputs):
    packet = make_packet(inputs)
    events = transcript(packet, environment())
    result = verify(packet, events, inputs)
    assert result['status'] == 'SOURCE_DEPENDENCIES_AND_DEFAULT_CHILD_ENVIRONMENT_VERIFIED'
    assert result['patient_launch_authorized'] is False
    altered = copy.deepcopy(packet)
    altered['cells'][1] += '\nprint("extra")'
    with pytest.raises(ValueError, match='PACKET_NOT_EXACT'):
        verify(altered, transcript(altered, environment()), inputs)
    changed = copy.deepcopy(events)
    changed[2]['message']['content'][0]['input']['includeOutputs'] = True
    with pytest.raises(ValueError, match='must not be read'):
        verify(packet, changed, inputs)
    with pytest.raises(ValueError, match='incomplete'):
        verify(packet, [{'type': 'result', 'structured_output': result}], inputs)


def test_failed_original_setup_or_injected_environment_cannot_pass(inputs):
    packet = make_packet(inputs)
    events = transcript(packet, environment())
    event = events[11]['message']['content'][0]
    returned = json.loads(event['content'])
    returned['outputs'][0]['text'][0] = returned['outputs'][0]['text'][0].replace("'COMPLETE'", "'FAILED'", 1)
    event['content'] = json.dumps(returned)
    with pytest.raises(ValueError, match='DID_NOT_COMPLETE'):
        verify(packet, events, inputs)
    value = environment()
    value['credential'] = 'injected private text'
    with pytest.raises(ValueError, match='ENVIRONMENT_SCHEMA'):
        verify(packet, transcript(packet, value), inputs)

def test_child_environment_observes_default_imports_and_7z_without_any_payload(monkeypatch):
    import sys
    monkeypatch.setattr(sys, 'path', list(sys.path))
    monkeypatch.setattr(sys, 'executable', '/usr/bin/python3.12')
    monkeypatch.setattr('platform.python_version', lambda: '3.12.0')
    def distribution(name):
        version = {'numpy': '2.3.3', 'nibabel': '5.3.2'}[name]
        return SimpleNamespace(locate_file=lambda path: '/usr/local/lib/python3.12/dist-packages/' + path,
                               metadata={'Name': name}, version=version)
    monkeypatch.setattr('importlib.metadata.distribution', distribution)
    monkeypatch.setattr('importlib.metadata.distributions', lambda: iter([distribution('numpy'), distribution('nibabel')]))
    monkeypatch.setattr('importlib.util.find_spec', lambda name: SimpleNamespace(
        origin='/usr/local/lib/python3.12/dist-packages/' + name + '/__init__.py'))
    import importlib
    original_import = importlib.import_module
    monkeypatch.setattr(importlib, 'import_module', lambda name: SimpleNamespace(
        __version__=distribution(name).version, __file__='/usr/local/lib/python3.12/dist-packages/' + name + '/__init__.py')
        if name in ['numpy', 'nibabel'] else original_import(name))
    monkeypatch.setattr('shutil.which', lambda name: '/usr/bin/7z')
    monkeypatch.setattr(Path, 'resolve', lambda self: self)
    def command(args, **kwargs):
        assert args == ['/usr/bin/7z', 'i']
        assert kwargs['timeout'] == 15
        return SimpleNamespace(returncode=0, stdout=b'7-Zip [64] 16.02 : copyright\nPRIVATE_DIAGNOSTIC_NOT_EXPORTED', stderr=b'')
    monkeypatch.setattr('subprocess.run', command)
    monkeypatch.setattr('builtins.open', lambda *a, **k: (_ for _ in ()).throw(AssertionError('payload file opened')))
    value = setup.child_environment(setup.SOURCE_ROOT)
    setup.validate_environment(value)
    assert value['packages'][0]['import_version'] == '2.3.3'
    assert value['seven_zip']['version'] == '16.02'
    assert 'PRIVATE_DIAGNOSTIC' not in json.dumps(value)


def test_child_environment_failure_keeps_private_diagnostics_and_no_retry(tmp_path, monkeypatch):
    destination = tmp_path / 'owned-setup'
    destination.mkdir()
    request = {'setup_root': str(destination), 'request_id': 'fixture', 'source_root': setup.SOURCE_ROOT}
    def command(args, **kwargs):
        assert args[1:3] == ['-B', '-c']
        assert kwargs['timeout'] == 120
        kwargs['stdout'].write(b'PRIVATE_IMPORT_DIAGNOSTIC')
        return SimpleNamespace(returncode=1)
    monkeypatch.setattr('subprocess.run', command)
    with pytest.raises(ValueError, match='PRIVATE_DIAGNOSTIC_RETAINED'):
        setup.observe_environment(request, 'def child_environment(root): pass')
    assert (destination / 'environment.console.log').read_bytes() == b'PRIVATE_IMPORT_DIAGNOSTIC'
    intent = (destination / 'environment-intent.json').read_bytes()
    with pytest.raises(FileExistsError):
        setup.observe_environment(request, 'def child_environment(root): pass')
    assert (destination / 'environment-intent.json').read_bytes() == intent


def test_existing_helper_rejects_trailing_duplicate_wrong_cell_and_missing_runs(inputs):
    packet = make_packet(inputs)
    events = transcript(packet, environment())
    # These refusals are owned by the existing imported verify_cell_sources.
    with pytest.raises(ValueError, match='executed source not bound'):
        verify(packet, events + copy.deepcopy(events[-2:]), inputs)
    wrong_cell = copy.deepcopy(events)
    wrong_cell[10]['message']['content'][0]['input']['cellId'] = 'pre-existing-unbound-cell'
    with pytest.raises(ValueError, match='executed source not bound'):
        verify(packet, wrong_cell, inputs)
    with pytest.raises(ValueError, match='execution sequence incomplete'):
        verify(packet, events[:-2], inputs)


def test_repeated_connection_open_is_refused(inputs):
    packet = make_packet(inputs)
    events = transcript(packet, environment())
    def connection(identity):
        return [
            {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'id': identity,
                'name': 'mcp__colab-worker__open_colab_browser_connection', 'input': {}}]}},
            {'type': 'user', 'message': {'content': [{'type': 'tool_result', 'tool_use_id': identity,
                'content': '{}'}]}},
        ]
    assert verify(packet, connection('connection-1') + events, inputs)['patient_launch_authorized'] is False
    with pytest.raises(ValueError, match='CONNECTION_REOPEN_REFUSED'):
        verify(packet, connection('connection-1') + connection('connection-2') + events, inputs)


@pytest.mark.parametrize('replacement,error', [('x' * 4097, 'OUTPUT_BOUND'), ('{', 'OUTPUT_SCHEMA')])
def test_setup_stream_bound_and_literal_parse_failures_are_classified(inputs, replacement, error):
    packet = make_packet(inputs)
    events = transcript(packet, environment())
    event = events[11]['message']['content'][0]
    returned = json.loads(event['content'])
    lines = returned['outputs'][0]['text'][0].splitlines()
    lines[0] = replacement
    returned['outputs'][0]['text'][0] = '\n'.join(lines)
    event['content'] = json.dumps(returned)
    with pytest.raises(ValueError, match='SETUP_TRANSPORT_' + error):
        verify(packet, events, inputs)


@pytest.mark.parametrize('mode', ['prepare', 'verify'])
def test_cli_missing_mode_arguments_use_parser_error(tmp_path, monkeypatch, capsys, mode):
    import sys
    output = tmp_path / 'never-created.json'
    monkeypatch.setattr(sys, 'argv', ['p001_runtime_setup', mode, '--output', str(output)])
    with pytest.raises(SystemExit) as error:
        setup.main()
    assert error.value.code == 2
    assert mode + ' requires --snapshot' in capsys.readouterr().err
    assert not output.exists()
