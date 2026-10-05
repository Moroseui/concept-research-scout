"""Bounded P001 source/dependency setup on the already observed CPU Colab runtime.

This generates and verifies setup cells for the existing supervised Session route.
It never invokes a model, Colab, preflight, prediction or scientific assessment.
Frozen notebook cells and the approved private capture wrapper remain unchanged.
"""
import argparse
import ast
import hashlib
import inspect
import json
from pathlib import Path
import re
import subprocess
import sys

from orchestrator import p001_runtime_intake as intake
from orchestrator.colab_patient import CPU_CELL, streams, tool_exchanges, verify_cell_sources
from orchestrator.colab_worker import capture_cell

SOURCE_ROOT = '/content/scout-pilot-' + intake.SOURCE_PIN[:12]
SETUP_PARENT = '/content/drive/MyDrive/isles-pilot'
SCOPE = 'DEFAULT_CHILD_IMPORT_PROBE_AND_DISTRIBUTION_METADATA_NOT_SCIENTIFIC_EXECUTION'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def frozen_sources(snapshot):
    """Verify local immutable bytes before invoking the frozen review verifier."""
    snapshot = Path(snapshot).absolute()
    if snapshot.is_symlink() or any(p.is_symlink() for p in snapshot.parents):
        raise ValueError('SETUP_SNAPSHOT_SYMLINK')
    def git(*args):
        return subprocess.check_output(['git', '--no-optional-locks', *args], cwd=snapshot,
                                       stderr=subprocess.DEVNULL, timeout=30)
    if git('rev-parse', 'HEAD').decode().strip() != intake.EXECUTION_PIN:
        raise ValueError('SETUP_EXACT_FROZEN_EXECUTION_REQUIRED')
    if git('status', '--porcelain') or git('remote'):
        raise ValueError('SETUP_CLEAN_PRIVATE_SNAPSHOT_WITHOUT_REMOTES_REQUIRED')
    # These are the executable import closure of the frozen review check below.
    for name in ['orchestrator/colab_patient.py', 'orchestrator/colab_worker.py',
                 'orchestrator/campaign.py', 'orchestrator/campaign_review.py']:
        path = snapshot / name
        if path.is_symlink() or path.read_bytes() != git('show', intake.EXECUTION_PIN + ':' + name):
            raise ValueError('SETUP_FROZEN_IMPORT_BYTES_CHANGED')
    command = """import json,sys
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root))
from orchestrator.colab_patient import require_patient_review
print(json.dumps({'reviewed_commit':require_patient_review()}))
"""
    # -I avoids accidentally importing the current engineering checkout.
    result = subprocess.run([sys.executable, '-B', '-I', '-c', command, str(snapshot)],
                            cwd=snapshot.parent, capture_output=True, timeout=60)
    if result.returncode or json.loads(result.stdout) != {'reviewed_commit': '465a0c3b1f2e8486a13e68dfd2179b3bfd16840d'}:
        raise ValueError('SETUP_EXISTING_FROZEN_REVIEW_NOT_VERIFIED')
    raw = git('show', intake.NOTEBOOK_PIN + ':campaigns/isles24-pilot/experiments/P001/colab_P001.ipynb')
    notebook = json.loads(raw)
    sources = [''.join(notebook['cells'][i]['source']) for i in [1, 3]]
    requirements = git('show', intake.SOURCE_PIN + ':campaigns/isles24-pilot/experiments/P001/requirements.txt')
    if requirements != b'numpy==2.3.3\nnibabel==5.3.2\n':
        raise ValueError('SETUP_FROZEN_REQUIREMENTS_CHANGED')
    # Reuse this current function only if its complete module matches the frozen review.
    frozen_capture = git('show', intake.EXECUTION_PIN + ':orchestrator/colab_worker.py')
    if Path(inspect.getfile(capture_cell)).read_bytes() != frozen_capture:
        raise ValueError('SETUP_CAPTURE_DEPENDENCY_CHANGED')
    return {'sources': sources, 'notebook_sha256': sha(raw), 'requirements_sha256': sha(requirements),
            'capture_module_sha256': sha(frozen_capture), 'reviewed_commit': '465a0c3b1f2e8486a13e68dfd2179b3bfd16840d'}


def check_observation(observed, request, *, source_absent):
    """Metadata gate only: preserves unknown states and all historical evidence."""
    if (observed['runtime']['fingerprint_sha256'] != request['runtime_fingerprint_sha256'] or
            observed['cpu_guard'] != {'colab_runtime': True, 'nvidia_smi_absent': True}):
        raise ValueError('SETUP_CURRENT_CPU_RUNTIME_CHANGED')
    if observed['drive'] != {'mounted': True, 'visible': True}:
        raise ValueError('SETUP_DRIVE_NOT_VISIBLE')
    if observed['archive'] != request['archive_metadata']:
        raise ValueError('SETUP_ARCHIVE_METADATA_CHANGED_OR_NOT_VISIBLE')
    if observed['processes']['scan_complete'] is not True or observed['processes']['matches']:
        raise ValueError('SETUP_EXISTING_OR_UNCERTAIN_PROCESS')
    for name, row in observed['execution_paths'].items():
        if not name.startswith('preflight_') and row != {'state': 'ABSENT_IN_VISIBLE_PARENT'}:
            raise ValueError('SETUP_EXISTING_OR_UNCERTAIN_PREDICTION_PATH')
    frozen_rows = [row for row in observed['source_files'] if row['path'].startswith(request['source_root'] + '/')]
    if source_absent:
        if any(row['state'] != 'ABSENT_IN_VISIBLE_PARENT' for row in frozen_rows):
            raise ValueError('SETUP_EXISTING_OR_UNCERTAIN_SOURCE')
    elif any(row.get('matches_expected') is not True for row in frozen_rows):
        raise ValueError('SETUP_FROZEN_SOURCE_BYTES_NOT_VERIFIED')


def claim_setup(request):
    """Exclusive intent before source/dependency changes. Never retry an existing attempt."""
    import json
    import os
    from pathlib import Path
    import stat

    def absent(path):
        for parent in reversed(path.parents):
            if stat.S_ISLNK(parent.lstat().st_mode):
                raise ValueError('SETUP_PATH_SYMLINK')
        try:
            path.lstat()
        except FileNotFoundError:
            return
        raise ValueError('SETUP_PATH_ALREADY_EXISTS_RECONCILE')
    source = Path(request['source_root'])
    destination = Path(request['setup_root'])
    # These fixed parents must already be visible; no recursive parent creation.
    absent(source)
    absent(destination)
    os.umask(0o077)
    destination.mkdir(mode=0o700)
    with (destination / 'intent.json').open('x') as handle:
        json.dump({'status': 'SETUP_INTENT_NO_AUTOMATIC_RETRY',
                   'request_id': request['request_id'],
                   'runtime_fingerprint_sha256': request['runtime_fingerprint_sha256'],
                   'binding_sha256': request['binding_sha256'],
                   'prediction_launch_authorized': False}, handle)
        handle.flush()
        os.fsync(handle.fileno())
    for name in ['acquisition.console.log', 'dependencies.console.log', 'seven-zip.console.log']:
        # The unchanged capture wrapper appends only to these exclusively owned logs.
        with (destination / name).open('x'):
            pass


def child_environment(source_root):
    """Import only installed default-environment packages; return bounded metadata."""
    import hashlib
    import importlib
    import importlib.metadata
    import importlib.util
    import json
    import os
    from pathlib import Path
    import platform
    import re
    import shutil
    import subprocess
    import sys

    # Same scientific root precedence as the frozen child. Do not run scientific code.
    sys.path.insert(0, source_root)
    packages = []
    for name, expected in [('numpy', '2.3.3'), ('nibabel', '5.3.2')]:
        distribution = importlib.metadata.distribution(name)
        origin = importlib.util.find_spec(name).origin
        expected_origin = str(Path(distribution.locate_file(name + '/__init__.py')).resolve())
        origin = str(Path(origin).resolve())
        # Reject local/Drive source shadowing before importing the package.
        if origin != expected_origin or not re.fullmatch(
                r'/usr/(?:local/)?lib/python[0-9.]+/(?:dist|site)-packages/' + name + r'/__init__\.py', origin):
            raise ValueError('SETUP_IMPORT_ORIGIN_OUTSIDE_DEFAULT_PACKAGE_DOMAIN')
        module = importlib.import_module(name)
        if distribution.version != expected or module.__version__ != expected:
            raise ValueError('SETUP_DEFAULT_ENVIRONMENT_VERSION_MISMATCH')
        if str(Path(module.__file__).resolve()) != origin:
            raise ValueError('SETUP_RESOLVED_IMPORT_CHANGED')
        packages.append({'name': name, 'distribution_version': distribution.version,
                         'import_version': module.__version__, 'origin': origin})
    inventory = []
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get('Name')
        version = distribution.version
        if (len(inventory) >= 1024 or not isinstance(name, str) or
                not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', name) or
                not isinstance(version, str) or not re.fullmatch(r'[0-9][A-Za-z0-9.+!-]{0,63}', version)):
            raise ValueError('SETUP_DEPENDENCY_METADATA_DOMAIN')
        inventory.append({'name': name.lower().replace('_', '-'), 'version': version})
    inventory.sort(key=lambda row: (row['name'], row['version']))
    executable = str(Path(sys.executable).resolve())
    if not re.fullmatch(r'/usr/(?:local/)?bin/python[0-9.]*', executable):
        raise ValueError('SETUP_PYTHON_EXECUTABLE_DOMAIN')
    seven_zip = shutil.which('7z')
    if seven_zip not in ['/usr/bin/7z', '/usr/local/bin/7z']:
        raise ValueError('SETUP_7Z_EXECUTABLE_DOMAIN')
    result = subprocess.run([seven_zip, 'i'], capture_output=True, timeout=15)
    if result.returncode or len(result.stdout) > 65536 or len(result.stderr) > 65536:
        raise ValueError('SETUP_7Z_METADATA_FAILED')
    match = re.search(rb'7-Zip(?: \([a-z]\))?(?: \[[A-Za-z0-9_-]+\])? ([0-9]+(?:\.[0-9]+){1,3})', result.stdout)
    if match is None:
        raise ValueError('SETUP_7Z_VERSION_UNAVAILABLE')
    return {'schema': 'p001-default-child-environment/v1',
            'scope': 'DEFAULT_CHILD_IMPORT_PROBE_AND_DISTRIBUTION_METADATA_NOT_SCIENTIFIC_EXECUTION',
            'python_version': platform.python_version(), 'python_executable': executable,
            'source_root': source_root, 'packages': packages, 'inventory': inventory,
            'inventory_sha256': hashlib.sha256(json.dumps(inventory, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'seven_zip': {'path': seven_zip, 'version': match.group(1).decode()},
            'patient_files_opened': False, 'prediction_executed': False,
            'limitations': 'Fresh child import probe; no scientific run, wheel-byte attestation or future environment immutability claim.'}


def validate_environment(value):
    """No raw diagnostics, unknown nested fields or patient paths cross the interface."""
    def require(condition):
        if not condition:
            raise ValueError('SETUP_ENVIRONMENT_SCHEMA')
    require(isinstance(value, dict) and set(value) == {'schema', 'scope', 'python_version', 'python_executable',
        'source_root', 'packages', 'inventory', 'inventory_sha256', 'seven_zip', 'patient_files_opened',
        'prediction_executed', 'limitations'})
    require(value['schema'] == 'p001-default-child-environment/v1' and value['scope'] == SCOPE)
    require(value['source_root'] == SOURCE_ROOT and value['patient_files_opened'] is False and value['prediction_executed'] is False)
    require(re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', value['python_version']))
    require(re.fullmatch(r'/usr/(?:local/)?bin/python[0-9.]*', value['python_executable']))
    require(len(value['packages']) == 2)
    for row, name, version in zip(value['packages'], ['numpy', 'nibabel'], ['2.3.3', '5.3.2']):
        require(set(row) == {'name', 'distribution_version', 'import_version', 'origin'})
        require(row['name'] == name and row['distribution_version'] == version and row['import_version'] == version)
        require(re.fullmatch(r'/usr/(?:local/)?lib/python[0-9.]+/(?:dist|site)-packages/' + name + r'/__init__\.py', row['origin']))
    require(isinstance(value['inventory'], list) and 2 <= len(value['inventory']) <= 1024)
    for row in value['inventory']:
        require(set(row) == {'name', 'version'} and re.fullmatch(r'[a-z0-9][a-z0-9_.-]{0,79}', row['name']) and
                re.fullmatch(r'[0-9][A-Za-z0-9.+!-]{0,63}', row['version']))
    require(value['inventory'] == sorted(value['inventory'], key=lambda row: (row['name'], row['version'])))
    require(value['inventory_sha256'] == sha(canonical(value['inventory'])))
    for row in value['packages']:
        require({'name': row['name'], 'version': row['import_version']} in value['inventory'])
    require(set(value['seven_zip']) == {'path', 'version'} and value['seven_zip']['path'] in ['/usr/bin/7z', '/usr/local/bin/7z'])
    require(re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}', value['seven_zip']['version']))
    require(value['limitations'] == 'Fresh child import probe; no scientific run, wheel-byte attestation or future environment immutability claim.')
    require(len(canonical(value)) <= 131072)


def observe_environment(request, child_source):
    """One fresh child, private stdout/stderr, exclusive result and no automatic retry."""
    import json
    import os
    from pathlib import Path
    import subprocess
    import sys

    os.umask(0o077)
    destination = Path(request['setup_root'])
    with (destination / 'environment-intent.json').open('x') as handle:
        json.dump({'request_id': request['request_id'], 'status': 'ENVIRONMENT_OBSERVATION_INTENT'}, handle)
        handle.flush()
        os.fsync(handle.fileno())
    result_path = destination / 'environment.child.json'
    if result_path.exists() or result_path.is_symlink():
        raise ValueError('SETUP_ENVIRONMENT_EXISTING_RESULT_RECONCILE')
    source = child_source + '\nimport json,os\nwith open(' + repr(str(result_path)) + ", 'x') as result_handle:\n    os.chmod(result_handle.name,0o600)\n    json.dump(child_environment(" + repr(request['source_root']) + "),result_handle,sort_keys=True,allow_nan=False)\n"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    with (destination / 'environment.console.log').open('xb') as console:
        result = subprocess.run([sys.executable, '-B', '-c', source], cwd='/content',
                                env=env, stdout=console, stderr=subprocess.STDOUT, timeout=120)
    if result.returncode:
        raise ValueError('SETUP_ENVIRONMENT_PROBE_FAILED_PRIVATE_DIAGNOSTIC_RETAINED')
    if result_path.stat().st_size > 131072:
        raise ValueError('SETUP_ENVIRONMENT_RESULT_BOUND')
    return json.loads(result_path.read_text())


def packet(snapshot, prior_packet, prior_receipt, request_id):
    if not re.fullmatch('[a-z0-9][a-z0-9-]{0,63}', request_id):
        raise ValueError('SETUP_REQUEST_ID')
    if prior_packet != intake.packet(prior_packet['request']['request_id']):
        raise ValueError('SETUP_PRIOR_RUNTIME_PACKET_CHANGED')
    if (prior_receipt['status'] != 'READ_ONLY_RUNTIME_EVIDENCE_RECORDED' or
            prior_receipt['packet_sha256'] != sha(canonical(prior_packet)) or
            prior_receipt.get('scientific_acceptance') is not False or prior_receipt.get('launch_authorized') is not False or
            prior_receipt['observation']['request_id'] != prior_packet['request']['request_id']):
        raise ValueError('SETUP_VERIFIED_RUNTIME_RECEIPT_REQUIRED')
    observed = prior_receipt['observation']
    intake.validate_fields(observed, prior_packet['request'])
    fingerprint = observed['runtime']['fingerprint_sha256']
    if not isinstance(fingerprint, str) or not re.fullmatch('[0-9a-f]{64}', fingerprint):
        raise ValueError('SETUP_CURRENT_RUNTIME_FINGERPRINT_REQUIRED')
    request = {'request_id': request_id, 'runtime_fingerprint_sha256': fingerprint,
               'archive_metadata': observed['archive'], 'source_root': SOURCE_ROOT,
               'setup_root': SETUP_PARENT + '/p001-runtime-setup-0770c7dcabe7-' + fingerprint[:12],
               'runtime_request': prior_packet['request'],
               'prior_receipt_sha256': sha(canonical(prior_receipt))}
    if observed['archive'].get('size_bytes') != 99014629647 or observed['archive'].get('kind') != 'file':
        raise ValueError('SETUP_ARCHIVE_METADATA_REQUIRED')
    check_observation(observed, request, source_absent=True)
    frozen = frozen_sources(snapshot)
    # These exact operative lines were reviewed at preparation pin 687f826f.
    preflight_raw = intake.git_bytes(intake.PREPARATION_PIN, 'orchestrator/p001_preflight_transport.py')
    constants = [node.value for node in ast.walk(ast.parse(preflight_raw)) if isinstance(node, ast.Constant)]
    lines = ["if shutil.which('7z') is None:",
             "    subprocess.run(['apt-get','-qq','update'],check=True,timeout=180)",
             "    subprocess.run(['apt-get','-qq','install','-y','p7zip-full'],check=True,timeout=180)"]
    if any(line not in constants for line in lines):
        raise ValueError('SETUP_REVIEWED_7Z_STATEMENTS_CHANGED')
    seven_zip = 'import shutil, subprocess\n' + '\n'.join(lines) + '\n'
    sources = [*frozen['sources'], seven_zip]
    request['source_sha256'] = [sha(source.encode()) for source in sources]
    request['binding_sha256'] = sha(canonical(request))
    shared = '\n'.join([inspect.getsource(intake.runtime_observation), inspect.getsource(check_observation),
                         'request = ' + repr(request)])
    setup_cell = shared + '\n' + inspect.getsource(claim_setup) + '\n' + '\n'.join([
        "check_observation(runtime_observation(request['runtime_request']),request,source_absent=True)",
        'claim_setup(request)',
        *[capture_cell(source, request['setup_root'] + '/' + name + '.console.log')
          for source, name in zip(sources, ['acquisition', 'dependencies', 'seven-zip'])],
        "import json\nprint(json.dumps({'status':'SOURCE_DEPENDENCY_SETUP_COMPLETE','binding_sha256':request['binding_sha256'],'patient_launch_authorized':False}))",
    ])
    environment_cell = shared + '\n' + inspect.getsource(observe_environment) + '\n' + '\n'.join([
        'import hashlib, json, re', 'SOURCE_ROOT = ' + repr(SOURCE_ROOT), 'SCOPE = ' + repr(SCOPE),
        inspect.getsource(canonical), inspect.getsource(sha), inspect.getsource(validate_environment),
        "check_observation(runtime_observation(request['runtime_request']),request,source_absent=False)",
        'environment = observe_environment(request,' + repr(inspect.getsource(child_environment)) + ')',
        'validate_environment(environment)',
        "print(json.dumps({'status':'DEFAULT_CHILD_ENVIRONMENT_OBSERVED','binding_sha256':request['binding_sha256'],'environment':environment},sort_keys=True,allow_nan=False))",
    ])
    for cell in [setup_cell, environment_cell]:
        compile(cell, 'p001-runtime-setup', 'exec')
    return {'task': 'p001_runtime_source_and_dependency_setup_only', 'request': request,
            'setup_module_sha256': sha(Path(__file__).read_bytes()),
            'runtime_intake_module_sha256': sha(Path(intake.__file__).read_bytes()),
            'pins': {'execution': intake.EXECUTION_PIN, 'source': intake.SOURCE_PIN, 'notebook': intake.NOTEBOOK_PIN},
            'frozen_review': {key: value for key, value in frozen.items() if key != 'sources'},
            'cells': [CPU_CELL, setup_cell, environment_cell],
            'worker_instructions': 'Reuse the existing connected CPU Colab notebook/runtime. Never create, restart or replace either. '
                'Append only these three cells; read back exact sources with includeOutputs=false. Never edit or execute existing cells. '
                'Execute the CPU cell once, then setup once only for CPU/Colab true, then environment observation once only after setup succeeds. '
                'Stop on any failure or disconnect; preserve intent and do not retry. No mount, consent, other code, preflight, archive hashing, '
                'patient payloads, prediction launch, output/log reads or model interpretation. Execute only the supplied cells through the existing Session route.',
            'patient_launch_authorized': False}


def verify_transcript(bound_packet, events, *, snapshot, runtime_packet, runtime_receipt):
    """Only actual exact source/readback/run exchanges prove setup/observation."""
    if bound_packet != packet(snapshot, runtime_packet, runtime_receipt, bound_packet['request']['request_id']):
        raise ValueError('SETUP_PACKET_NOT_EXACT')
    verify_cell_sources(events, bound_packet['cells'])
    calls, results = tool_exchanges(events)
    allowed = ('__open_colab_browser_connection', '__get_cells', '__add_code_cell', '__run_code_cell')
    if any(not call['name'].endswith(allowed) for call in calls):
        raise ValueError('SETUP_UNEXPECTED_TOOL')
    if sum(call['name'].endswith('__open_colab_browser_connection') for call in calls) > 1:
        raise ValueError('SETUP_CONNECTION_REOPEN_REFUSED')
    if [call['input']['code'] for call in calls if call['name'].endswith('__add_code_cell')] != bound_packet['cells']:
        raise ValueError('SETUP_UNEXPECTED_CELL')
    runs = [call for call in calls if call['name'].endswith('__run_code_cell')]
    if json.loads(streams(results[runs[0]['id']])) != {'cpu_only': True, 'colab_runtime': True}:
        raise ValueError('SETUP_CPU_COLAB_REQUIRED')
    request = bound_packet['request']
    setup_stream = streams(results[runs[1]['id']])
    if len(setup_stream.encode()) > 4096:
        raise ValueError('SETUP_TRANSPORT_OUTPUT_BOUND')
    setup_lines = setup_stream.splitlines()
    if len(setup_lines) != 4:
        raise ValueError('SETUP_TRANSPORT_OUTPUT_SCHEMA')
    for line, expected in zip(setup_lines[:3], request['source_sha256']):
        try:
            transport = ast.literal_eval(line)
        except (ValueError, SyntaxError) as error:
            raise ValueError('SETUP_TRANSPORT_OUTPUT_SCHEMA') from error
        if transport != {'transport_status': 'COMPLETE', 'source_sha256': expected}:
            raise ValueError('SETUP_ORIGINAL_CELL_DID_NOT_COMPLETE')
    if json.loads(setup_lines[3]) != {'status': 'SOURCE_DEPENDENCY_SETUP_COMPLETE',
            'binding_sha256': request['binding_sha256'], 'patient_launch_authorized': False}:
        raise ValueError('SETUP_COMPLETION_BINDING')
    raw = streams(results[runs[2]['id']])
    if len(raw.encode()) > 132096:
        raise ValueError('SETUP_OBSERVATION_OUTPUT_BOUND')
    observation = json.loads(raw)
    if set(observation) != {'status', 'binding_sha256', 'environment'} or observation['status'] != 'DEFAULT_CHILD_ENVIRONMENT_OBSERVED' or observation['binding_sha256'] != request['binding_sha256']:
        raise ValueError('SETUP_OBSERVATION_BINDING')
    validate_environment(observation['environment'])
    return {'status': 'SOURCE_DEPENDENCIES_AND_DEFAULT_CHILD_ENVIRONMENT_VERIFIED',
            'binding_sha256': request['binding_sha256'], 'packet_sha256': sha(canonical(bound_packet)),
            'runtime_fingerprint_sha256': request['runtime_fingerprint_sha256'],
            'environment_sha256': sha(canonical(observation['environment'])),
            'environment': observation['environment'], 'patient_launch_authorized': False,
            'scientific_acceptance': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'verify'])
    parser.add_argument('--snapshot', type=Path)
    parser.add_argument('--runtime-packet', type=Path)
    parser.add_argument('--runtime-receipt', type=Path)
    parser.add_argument('--request-id')
    parser.add_argument('--packet', type=Path)
    parser.add_argument('--protocol', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    required = ['snapshot', 'runtime_packet', 'runtime_receipt'] + (
        ['request_id'] if args.mode == 'prepare' else ['packet', 'protocol'])
    missing = [name for name in required if getattr(args, name) is None]
    if missing:
        parser.error(args.mode + ' requires ' + ', '.join('--' + name.replace('_', '-') for name in missing))
    if args.mode == 'prepare':
        value = packet(args.snapshot, json.loads(args.runtime_packet.read_text()),
                       json.loads(args.runtime_receipt.read_text()), args.request_id)
    else:
        value = verify_transcript(json.loads(args.packet.read_text()), [json.loads(line)
            for line in args.protocol.read_text().splitlines() if line.strip()], snapshot=args.snapshot,
            runtime_packet=json.loads(args.runtime_packet.read_text()), runtime_receipt=json.loads(args.runtime_receipt.read_text()))
    import os
    os.umask(0o077)
    with args.output.open('x') as handle:
        os.chmod(args.output, 0o600)
        json.dump(value, handle, indent=2, allow_nan=False)
    print(json.dumps({'status': 'SETUP_PACKET_PREPARED' if args.mode == 'prepare' else value['status'],
                      'patient_launch_authorized': False}))


if __name__ == '__main__':
    main()