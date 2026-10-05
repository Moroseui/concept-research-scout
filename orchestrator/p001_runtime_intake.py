"""Read-only P001 current-runtime evidence; never a launch or science decision.

prepare emits exact bounded cells for the existing supervised Colab Session route.
verify consumes its original protocol, not a model's claimed runtime result. This
collector does not mount Drive, install packages, invoke Git, read archive bytes,
or open patient outputs. Its observations apply only to the connected runtime.
"""
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import re

from orchestrator.colab_patient import CPU_CELL, streams, tool_exchanges, verify_cell_sources
from orchestrator.colab_worker import NOTEBOOK_PIN, SOURCE_PIN, git_bytes

PREPARATION_PIN = "687f826f451501eb3fd4aee34aba95c578eed327"
EXECUTION_PIN = "0770c7dcabe781cbfb87de505755e7aafa758f2e"
ARCHIVE = "/content/drive/MyDrive/isles-pilot/archive-preservation-ec3e76e9b91f40ca847b490f9b5f7bfa/train.7z"
OUTPUT = "/content/drive/MyDrive/isles-pilot/P001-v1"
PREFLIGHT = "/content/drive/MyDrive/isles-pilot/p001-preflight-0219db9669cf48fb8404b4e1c9c03540"
SOURCE_FILES = [
    "campaigns/isles24-pilot/experiments/P001/run.py",
    "campaigns/isles24-pilot/experiments/P001/requirements.txt",
    "campaigns/isles24-pilot/experiments/P001/validate_return.py",
    "campaigns/isles24-pilot/experiments/P001/review.json",
    "campaigns/isles24-pilot/experiments/P001/publication.json",
    "orchestrator/campaign.py", "orchestrator/publication.py",
]
SUPPORT_FILES = ["scripts/p001_input_preflight.py", "campaigns/isles24-pilot/prediction_selection.json"]


def runtime_observation(request):
    """One snapshot of fixed metadata. No payload inspection or state changes."""
    import hashlib
    import importlib.metadata
    import json
    import os
    from pathlib import Path
    import platform
    import re
    import shutil
    import stat
    import sys
    import time

    started = time.monotonic()
    observed_at = time.time_ns()
    drive_mounted = os.path.ismount('/content/drive')
    drive_visible = False
    try:
        drive_visible = drive_mounted and stat.S_ISDIR(os.stat('/content/drive/MyDrive').st_mode)
    except OSError:
        pass

    def metadata(name, drive=False):
        if drive and not drive_visible:
            return {'state': 'NOT_VISIBLE'}
        path = Path(name)
        try:
            # Do not follow a symlink at any level, even for metadata or code.
            for part in [*reversed(path.parents), path]:
                value = part.lstat()
                if stat.S_ISLNK(value.st_mode):
                    return {'state': 'SYMLINK_REJECTED'}
            return {'state': 'PRESENT', 'kind': 'file' if stat.S_ISREG(value.st_mode) else
                    'directory' if stat.S_ISDIR(value.st_mode) else 'other',
                    'size_bytes': value.st_size, 'mtime_ns': value.st_mtime_ns}
        except FileNotFoundError:
            return {'state': 'ABSENT_IN_VISIBLE_PARENT'}
        except OSError:
            return {'state': 'NOT_VISIBLE'}

    def bounded_read(path, limit):
        # Only called on fixed source / process metadata, never archive/output files.
        info = metadata(path)
        if info.get('kind') != 'file':
            raise OSError('UNREADABLE_METADATA')
        with open(path, 'rb') as handle:
            raw = handle.read(limit + 1)
        if len(raw) > limit:
            raise OSError('METADATA_BOUND')
        return raw

    def proc_identity(pid):
        raw = bounded_read('/proc/' + str(pid) + '/stat', 4096)
        # comm may contain spaces/parentheses; fields after its final ')' are fixed.
        fields = raw[raw.rfind(b')') + 2:].split()
        if len(fields) < 20 or not fields[19].isdigit():
            raise OSError('PROCESS_IDENTITY_UNAVAILABLE')
        return int(fields[19])

    boot_sha = None
    kernel_start_ticks = None
    try:
        raw = bounded_read('/proc/sys/kernel/random/boot_id', 128).strip()
        if re.fullmatch(b'[0-9a-f-]{36}', raw):
            boot_sha = hashlib.sha256(raw).hexdigest()
        kernel_start_ticks = proc_identity(os.getpid())
    except OSError:
        pass
    runtime_fingerprint = None
    if boot_sha is not None and kernel_start_ticks is not None:
        runtime_fingerprint = hashlib.sha256(json.dumps(
            [boot_sha, os.getpid(), kernel_start_ticks], separators=(',', ':')).encode()).hexdigest()

    source_rows = []
    for item in request['source_files']:
        row = {'path': item['path'], 'expected_sha256': item['sha256'], **metadata(item['path'])}
        if row.get('kind') == 'file':
            try:
                raw = bounded_read(item['path'], 1048576)
                row['sha256'] = hashlib.sha256(raw).hexdigest()
                row['matches_expected'] = row['sha256'] == item['sha256']
            except OSError:
                row = {'path': item['path'], 'expected_sha256': item['sha256'], 'state': 'NOT_VISIBLE'}
        source_rows.append(row)
    heads = []
    for root, expected in request['checkouts']:
        row = {'expected_commit': expected, **metadata(root + '/.git/HEAD')}
        if row.get('kind') == 'file':
            try:
                raw = bounded_read(root + '/.git/HEAD', 256).strip()
                row['detached_head'] = raw.decode() if re.fullmatch(b'[0-9a-f]{40}', raw) else None
                row['matches_expected'] = row['detached_head'] == expected
            except OSError:
                row = {'expected_commit': expected, 'state': 'NOT_VISIBLE'}
        heads.append(row)

    dependencies = []
    dep_root = request['dependency_root']
    dep_info = metadata(dep_root)
    for package in ['numpy', 'nibabel']:
        versions = []
        complete = dep_info.get('kind') == 'directory'
        if complete:
            try:
                count = 0
                for dist in importlib.metadata.distributions(path=[dep_root]):
                    count += 1
                    if count > 256 or time.monotonic() - started > 20:
                        complete = False
                        break
                    if (dist.metadata.get('Name') or '').lower().replace('_', '-') == package:
                        version = dist.version
                        if not isinstance(version, str) or not re.fullmatch(r'[0-9][A-Za-z0-9.+!-]{0,63}', version):
                            complete = False
                            break
                        versions.append(version)
            except (OSError, ValueError, KeyError, TypeError):
                complete = False
        dependencies.append({'name': package, 'versions': sorted(versions), 'scan_complete': complete})

    path_rows = {label: metadata(path, drive=True) for label, path in request['execution_paths'].items()}
    archive = metadata(request['archive'], drive=True)
    process_rows = []
    scan_complete = True
    scanned = 0
    scan_started = time.monotonic()
    try:
        with os.scandir('/proc') as entries:
            for entry in entries:
                if not entry.name.isdigit():
                    continue
                scanned += 1
                if scanned > 8192 or time.monotonic() - scan_started > 5:
                    scan_complete = False
                    break
                try:
                    pid = int(entry.name)
                    before = proc_identity(pid)
                    args = bounded_read('/proc/' + entry.name + '/cmdline', 65536).split(b'\0')
                    kinds = []
                    for kind, markers in request['process_markers'].items():
                        if any(marker.encode() in arg for marker in markers for arg in args):
                            kinds.append(kind)
                    after = proc_identity(pid)
                    if before != after:
                        scan_complete = False
                        continue
                    if kinds:
                        if len(process_rows) >= 64:
                            scan_complete = False
                            break
                        process_rows.append({'pid': pid, 'start_ticks': before, 'kinds': kinds,
                                             'historical_identity': 'UNPROVEN_NO_HISTORICAL_START_TICKS'})
                except FileNotFoundError:
                    # Vanished during the scan; a historical scan cannot attest continued idleness.
                    scan_complete = False
                except OSError:
                    scan_complete = False
    except OSError:
        scan_complete = False
    result = {
        'schema': 'p001-current-runtime/v1', 'request_id': request['request_id'],
        'observed_at_unix_ns': observed_at, 'observation_seconds': round(time.monotonic() - started, 6),
        'scope': 'CONNECTED_RUNTIME_ONLY_NOT_OTHER_OR_PRIOR_RUNTIMES',
        'launch_authorized': False, 'prediction_executed_by_collector': False,
        'cpu_guard': {'colab_runtime': bool(os.environ.get('COLAB_RELEASE_TAG')),
                      'nvidia_smi_absent': shutil.which('nvidia-smi') is None},
        'runtime': {'fingerprint_sha256': runtime_fingerprint, 'boot_id_sha256': boot_sha,
                    'kernel_pid': os.getpid(), 'kernel_start_ticks': kernel_start_ticks,
                    'provider_session_id': None, 'python_version': platform.python_version()},
        'drive': {'mounted': drive_mounted, 'visible': drive_visible},
        'archive': archive, 'source_files': source_rows, 'checkout_heads': heads,
        'dependencies': {'root': dep_root, 'root_metadata': dep_info, 'packages': dependencies,
                         'scope': 'DISTRIBUTION_METADATA_ONLY_NOT_IMPORT_OR_ENVIRONMENT_ATTESTATION'},
        'execution_paths': path_rows,
        'processes': {'scan_complete': scan_complete, 'scanned': min(scanned, 8192),
                      'matches': sorted(process_rows, key=lambda row: row['pid']),
                      'historical_pid_record_verified': False},
    }
    return result


def packet(request_id):
    if not isinstance(request_id, str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}', request_id):
        raise ValueError('RUNTIME_REQUEST_ID')
    source_root = '/content/scout-pilot-' + SOURCE_PIN[:12]
    support_root = '/content/p001-preflight-support-' + PREPARATION_PIN[:12]
    expected = []
    for pin, root, names in [(SOURCE_PIN, source_root, SOURCE_FILES),
                             (PREPARATION_PIN, support_root, SUPPORT_FILES)]:
        for name in names:
            expected.append({'path': root + '/' + name, 'sha256': hashlib.sha256(git_bytes(pin, name)).hexdigest()})
    request = {
        'request_id': request_id, 'archive': ARCHIVE,
        'source_files': expected, 'checkouts': [[source_root, SOURCE_PIN], [support_root, PREPARATION_PIN]],
        'dependency_root': support_root + '/dependencies',
        'execution_paths': {
            'output_root': OUTPUT, 'private_root': OUTPUT + '.private',
            'checkpoint_directory': OUTPUT + '.private/checkpoints',
            'checkpoint_index': OUTPUT + '.private/checkpoint_index.json',
            'private_binding': OUTPUT + '.private/binding.json',
            'worker_root': OUTPUT + '.worker', 'worker_process_record': OUTPUT + '.worker/process.json',
            'worker_status': OUTPUT + '.worker/status.json', 'original_console': OUTPUT + '.console.log',
            'launch_console': OUTPUT + '.launch.console.log',
            'preflight_root': PREFLIGHT, 'preflight_process_record': PREFLIGHT + '/process.json',
        },
        'process_markers': {
            'P001_EXECUTION': ['/experiments/P001/run.py', OUTPUT + '.worker/run.py', OUTPUT + '.worker/launch.py'],
            'P001_PREFLIGHT': [support_root + '/scripts/p001_input_preflight.py', PREFLIGHT],
        },
    }
    cell = inspect.getsource(runtime_observation) + '\nimport json\nprint(json.dumps(runtime_observation(' + repr(request) + '), sort_keys=True, allow_nan=False))\n'
    compile(cell, 'p001-current-runtime-cell', 'exec')
    return {'task': 'p001_current_runtime_read_only', 'request': request,
            'pins': {'source': SOURCE_PIN, 'notebook': NOTEBOOK_PIN, 'execution': EXECUTION_PIN,
                     'preparation': PREPARATION_PIN},
            'cells': [CPU_CELL, cell],
            'authority': 'READ_ONLY_METADATA_NO_LAUNCH_NO_AUTHENTICATION_NO_PATIENT_PAYLOAD',
            'worker_instructions': 'Reuse the existing connected Colab notebook and runtime. '
                'Never create, restart or replace a notebook or runtime. If the existing connection '
                'is unavailable, return BLOCKED_EXISTING_COLAB_CONNECTION_UNAVAILABLE without reconnecting '
                'to a new runtime. Read cell sources only with includeOutputs=false. Append only these '
                'two exact collector cells and read back their sources. Never execute or edit existing '
                'cells. Execute the appended CPU cell once; proceed only for CPU and Colab true. '
                'Execute the appended collector once. No mount, login, install, Git, experiment '
                'execution, retries, other cells or output reads. Preserve the original protocol; '
                'a model response is not runtime evidence.'}


def validate_fields(observed, request):
    """Keep transport evidence a bounded metadata schema, including nested values."""
    def require(condition):
        if not condition:
            raise ValueError('RUNTIME_OBSERVATION_FIELDS')
    def integer(value, nullable=False):
        return (nullable and value is None) or (type(value) is int and value >= 0)
    def sha(value, nullable=False):
        return (nullable and value is None) or (isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value))
    def metadata(row, extra=()):
        require(isinstance(row, dict))
        state = row.get('state')
        require(state in ['PRESENT', 'NOT_VISIBLE', 'SYMLINK_REJECTED', 'ABSENT_IN_VISIBLE_PARENT'])
        keys = {'state', 'kind', 'size_bytes', 'mtime_ns'} if state == 'PRESENT' else {'state'}
        require(set(row) == keys | set(extra))
        if state == 'PRESENT':
            require(row['kind'] in ['file', 'directory', 'other'])
            require(integer(row['size_bytes']) and integer(row['mtime_ns']))
    require(all(type(value) is bool for value in observed['cpu_guard'].values()))
    drive = observed['drive']
    require(set(drive) == {'mounted', 'visible'} and all(type(v) is bool for v in drive.values()))
    require(not drive['visible'] or drive['mounted'])
    metadata(observed['archive'])
    for row in observed['execution_paths'].values():
        metadata(row)
    if not drive['visible']:
        require(observed['archive'] == {'state': 'NOT_VISIBLE'})
        require(all(row == {'state': 'NOT_VISIBLE'} for row in observed['execution_paths'].values()))
    for row in observed['source_files']:
        extra = ['path', 'expected_sha256']
        if 'sha256' in row:
            extra += ['sha256', 'matches_expected']
            require(row.get('kind') == 'file' and sha(row['sha256']))
            require(type(row['matches_expected']) is bool)
            require(row['matches_expected'] == (row['sha256'] == row['expected_sha256']))
        metadata(row, extra)
    require(len(observed['checkout_heads']) == len(request['checkouts']))
    for row, (_, expected) in zip(observed['checkout_heads'], request['checkouts']):
        require(row['expected_commit'] == expected)
        extra = ['expected_commit']
        if 'detached_head' in row:
            extra += ['detached_head', 'matches_expected']
            require(row.get('kind') == 'file')
            require(row['detached_head'] is None or re.fullmatch('[0-9a-f]{40}', row['detached_head']))
            require(type(row['matches_expected']) is bool)
            require(row['matches_expected'] == (row['detached_head'] == expected))
        metadata(row, extra)
    runtime = observed['runtime']
    require(set(runtime) == {'fingerprint_sha256', 'boot_id_sha256', 'kernel_pid', 'kernel_start_ticks',
                             'provider_session_id', 'python_version'})
    require(sha(runtime['fingerprint_sha256'], True) and sha(runtime['boot_id_sha256'], True))
    require(integer(runtime['kernel_pid']) and integer(runtime['kernel_start_ticks'], True))
    require(runtime['provider_session_id'] is None and
            re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', runtime['python_version']))
    deps = observed['dependencies']
    require(set(deps) == {'root', 'root_metadata', 'packages', 'scope'})
    require(deps['root'] == request['dependency_root'] and
            deps['scope'] == 'DISTRIBUTION_METADATA_ONLY_NOT_IMPORT_OR_ENVIRONMENT_ATTESTATION')
    metadata(deps['root_metadata'])
    require(len(deps['packages']) == 2)
    for row, name in zip(deps['packages'], ['numpy', 'nibabel']):
        require(set(row) == {'name', 'versions', 'scan_complete'} and row['name'] == name)
        require(type(row['scan_complete']) is bool and isinstance(row['versions'], list) and len(row['versions']) <= 256)
        require(all(isinstance(v, str) and re.fullmatch(r'[0-9][A-Za-z0-9.+!-]{0,63}', v) for v in row['versions']))
    processes = observed['processes']
    require(set(processes) == {'scan_complete', 'scanned', 'matches', 'historical_pid_record_verified'})
    require(type(processes['scan_complete']) is bool and integer(processes['scanned']) and processes['scanned'] <= 8192)
    require(processes['historical_pid_record_verified'] is False and len(processes['matches']) <= 64)
    for row in processes['matches']:
        require(set(row) == {'pid', 'start_ticks', 'kinds', 'historical_identity'})
        require(integer(row['pid']) and integer(row['start_ticks']))
        require(isinstance(row['kinds'], list) and 1 <= len(row['kinds']) <= 2)
        require(all(kind in request['process_markers'] for kind in row['kinds']))
        require(row['historical_identity'] == 'UNPROVEN_NO_HISTORICAL_START_TICKS')


def verify_transcript(bound_packet, events):
    """Validate actual readback/run exchanges. Does not interpret scientific readiness."""
    rebuilt = packet(bound_packet['request']['request_id'])
    if bound_packet != rebuilt:
        raise ValueError('RUNTIME_PACKET_NOT_EXACT')
    verify_cell_sources(events, bound_packet['cells'])
    calls, results = tool_exchanges(events)
    allowed = ('__open_colab_browser_connection', '__get_cells', '__add_code_cell', '__run_code_cell')
    if any(not call['name'].endswith(allowed) for call in calls):
        raise ValueError('RUNTIME_UNEXPECTED_TOOL')
    added = [call['input']['code'] for call in calls if call['name'].endswith('__add_code_cell')]
    if added != bound_packet['cells']:
        raise ValueError('RUNTIME_UNEXPECTED_CELL')
    runs = [call for call in calls if call['name'].endswith('__run_code_cell')]
    if json.loads(streams(results[runs[0]['id']])) != {'cpu_only': True, 'colab_runtime': True}:
        raise ValueError('RUNTIME_CPU_COLAB_REQUIRED')
    raw = streams(results[runs[1]['id']])
    if len(raw.encode()) > 65536:
        raise ValueError('RUNTIME_OUTPUT_BOUND')
    observed = json.loads(raw)
    # The exact executed collector fixes structure. Additionally reject payload injection,
    # missing visibility fields, impossible values and omitted immutable request bindings.
    expected_keys = {'schema', 'request_id', 'observed_at_unix_ns', 'observation_seconds', 'scope',
                     'launch_authorized', 'prediction_executed_by_collector', 'cpu_guard', 'runtime',
                     'drive', 'archive', 'source_files', 'checkout_heads', 'dependencies',
                     'execution_paths', 'processes'}
    if not isinstance(observed, dict) or set(observed) != expected_keys:
        raise ValueError('RUNTIME_OBSERVATION_SCHEMA')
    if (observed['schema'] != 'p001-current-runtime/v1' or
            observed['request_id'] != bound_packet['request']['request_id'] or
            observed['scope'] != 'CONNECTED_RUNTIME_ONLY_NOT_OTHER_OR_PRIOR_RUNTIMES' or
            observed['launch_authorized'] is not False or observed['prediction_executed_by_collector'] is not False or
            observed['cpu_guard'] != {'colab_runtime': True, 'nvidia_smi_absent': True}):
        raise ValueError('RUNTIME_OBSERVATION_BINDING')
    if type(observed['observed_at_unix_ns']) is not int or observed['observed_at_unix_ns'] <= 0:
        raise ValueError('RUNTIME_OBSERVATION_TIME')
    if (type(observed['observation_seconds']) not in (int, float) or
            not 0 <= observed['observation_seconds'] <= 120):
        raise ValueError('RUNTIME_OBSERVATION_TIME')
    if [(r['path'], r['expected_sha256']) for r in observed['source_files']] != [
            (r['path'], r['sha256']) for r in bound_packet['request']['source_files']]:
        raise ValueError('RUNTIME_SOURCE_BINDING')
    if set(observed['execution_paths']) != set(bound_packet['request']['execution_paths']):
        raise ValueError('RUNTIME_PATH_BINDING')
    validate_fields(observed, bound_packet['request'])
    return {'status': 'READ_ONLY_RUNTIME_EVIDENCE_RECORDED', 'scientific_acceptance': False,
            'launch_authorized': False, 'packet_sha256': hashlib.sha256(json.dumps(
                bound_packet, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'observed_stream_sha256': hashlib.sha256(raw.encode()).hexdigest(), 'observation': observed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'verify'])
    parser.add_argument('--request-id')
    parser.add_argument('--packet', type=Path)
    parser.add_argument('--protocol', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.mode == 'prepare':
        value = packet(args.request_id)
    else:
        if args.packet is None or args.protocol is None:
            parser.error('verify requires --packet and --protocol')
        value = verify_transcript(json.loads(args.packet.read_text()), [json.loads(line)
            for line in args.protocol.read_text().splitlines() if line.strip()])
    import os
    with args.output.open('x') as handle:
        os.chmod(args.output, 0o600)
        json.dump(value, handle, indent=2, allow_nan=False)
    print(json.dumps({'status': 'PACKET_PREPARED' if args.mode == 'prepare' else value['status'],
                      'launch_authorized': False}))


if __name__ == '__main__':
    main()