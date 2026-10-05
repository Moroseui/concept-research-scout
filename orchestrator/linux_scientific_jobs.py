"""Registered scientific Python jobs; completion is evidence, never acceptance.

The protected broker owns registration, live policy/control checks and systemd
start. Workers have no broker credentials. A durable attempt can execute once;
an uncertain interrupted attempt is retained for reconciliation, not retried.
"""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import stat
import subprocess
import sys
import time

from orchestrator.job_store import Store
from orchestrator.remote_supervisor import checked_source

CONFIG = Path('/etc/research-system/linux-scientific-jobs.json')
ACTION = 'launch_linux_job'
TRANSITION = {'from': 'REVIEWED_EXECUTION_PROPOSAL', 'to': 'LINUX_JOB_ELIGIBLE'}
UNIT = 'research-system-scientific-job@{}.service'
ARGUMENTS = ['--data-root', '@input', '--output-dir', '@output', '--settings', '@settings']
MAXIMUM = {'wall_seconds': 86400, 'cpu_seconds': 172800,
           'memory_bytes': 4294967296, 'output_bytes': 8589934592,
           'output_files': 2048}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,62}', value):
        raise ValueError('LINUX_JOB_ID_REQUIRED')
    return value


def relative(value):
    if (not isinstance(value, str) or not value or len(value) > 250 or
            Path(value).is_absolute() or any(p in ('', '.', '..') for p in value.split('/'))):
        raise ValueError('LINUX_JOB_RELATIVE_PATH_REQUIRED')
    return value


def pin(value, length=64):
    if not isinstance(value, str) or not re.fullmatch('[a-f0-9]{'+str(length)+'}', value):
        raise ValueError('LINUX_JOB_EXACT_DIGEST_REQUIRED')
    return value


def regular(path, limit=1000000):
    path = Path(path).absolute()
    if '..' in path.parts or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('LINUX_JOB_SYMLINK_REFUSED')
    st = path.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_size > limit:
        raise ValueError('LINUX_JOB_REGULAR_FILE_BOUND')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        actual = os.fstat(stream.fileno())
        if (actual.st_dev, actual.st_ino) != (st.st_dev, st.st_ino):
            raise ValueError('LINUX_JOB_FILE_IDENTITY_CHANGED')
        raw = stream.read(limit+1)
    if len(raw) > limit:
        raise ValueError('LINUX_JOB_REGULAR_FILE_BOUND')
    return raw


def file_digest(path):
    path = Path(path)
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError('LINUX_JOB_INPUT_REGULAR_FILE_REQUIRED')
    h = hashlib.sha256()
    with path.open('rb') as stream:
        before = os.fstat(stream.fileno())
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
        after = os.fstat(stream.fileno())
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('LINUX_JOB_INPUT_CHANGED_DURING_READ')
    return h.hexdigest()


def original(path, raw, mode=0o640):
    """Exclusive creation; an identical existing complete original is reusable."""
    path = Path(path)
    if path.exists() or path.is_symlink():
        if regular(path, max(1000000, len(raw))) != raw:
            raise ValueError('LINUX_JOB_ORIGINAL_CHANGED')
        return
    with path.open('xb') as stream:
        os.fchmod(stream.fileno(), mode)
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


@contextmanager
def lock(path):
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def protected(path):
    path = Path(path).absolute()
    for item in (path, *path.parents):
        st = item.lstat()
        if stat.S_ISLNK(st.st_mode) or st.st_uid != 0 or st.st_mode & 0o022:
            raise ValueError('LINUX_JOB_ROOT_PROTECTED_PATH_REQUIRED')
    return path


def interpreter(path):
    """Permit an administrator-owned venv symlink, retaining its invoked path."""
    path = Path(path).absolute(); protected(path.parent)
    st = path.lstat()
    if st.st_uid != 0 or not stat.S_ISLNK(st.st_mode) and st.st_mode & 0o022:
        raise ValueError('LINUX_JOB_FIXED_INTERPRETER_REQUIRED')
    protected(path.resolve(strict=True))
    return path


def configuration(path=CONFIG):
    value = json.loads(regular(protected(path)))
    if (set(value) != {'source', 'source_root', 'python', 'requests', 'outputs', 'database',
                      'worker_uid', 'worker_gid', 'maximum_parallel', 'input_roots', 'snapshots', 'proposals'} or
            type(value['maximum_parallel']) is not int or not 1 <= value['maximum_parallel'] <= 4 or
            any(type(value[k]) is not int or value[k] <= 0 for k in ('worker_uid', 'worker_gid'))):
        raise ValueError('LINUX_JOB_INSTALLED_CONFIGURATION_REQUIRED')
    pin(value['source'], 40)
    for key in ('source_root', 'python', 'requests', 'outputs', 'database', 'snapshots', 'proposals'):
        path = Path(value[key])
        if not path.is_absolute() or '..' in path.parts:
            raise ValueError('LINUX_JOB_FIXED_ABSOLUTE_PATH_REQUIRED')
    for key in ('source_root', 'requests', 'outputs', 'snapshots'):
        protected(value[key])
    interpreter(value['python'])
    if not isinstance(value['input_roots'], list) or not 1 <= len(value['input_roots']) <= 8:
        raise ValueError('LINUX_JOB_EXISTING_DATA_ROOTS_REQUIRED')
    for path in value['input_roots']:
        if not isinstance(path, str) or not Path(path).is_absolute():
            raise ValueError('LINUX_JOB_EXISTING_DATA_ROOTS_REQUIRED')
        protected(path)
    protected(Path(value['database']).parent)
    return value


def validate_core(core):
    keys = {'schema', 'job_id', 'source', 'experiment', 'code', 'spec', 'settings',
            'requirements', 'input_manifest', 'files', 'arguments', 'environment', 'limits', 'protocol', 'proposal_id', 'scientific_version'}
    if set(core) != keys or core['schema'] != 'linux-scientific-job/v1':
        raise ValueError('LINUX_JOB_CORE_SCHEMA')
    identifier(core['job_id']); pin(core['source'], 40)
    pin(core['proposal_id'])
    if core['experiment'] not in ('P002', 'P003'):
        raise ValueError('LINUX_JOB_PROSPECTIVE_VERSION_REQUIRED_FROZEN_P001_UNCHANGED')
    prefix = 'campaigns/isles24-pilot/experiments/'+core['experiment']+'/'
    if core['code'] != prefix+'run.py' or core['spec'] != prefix+'SPEC.md':
        raise ValueError('LINUX_JOB_REVIEWED_CAMPAIGN_ENTRYPOINT_REQUIRED')
    if not isinstance(core['files'], dict) or not 5 <= len(core['files']) <= 128:
        raise ValueError('LINUX_JOB_BOUND_SOURCE_FILES_REQUIRED')
    for name, sha in core['files'].items(): relative(name); pin(sha)
    for key in ('code', 'spec', 'settings', 'requirements', 'input_manifest'):
        relative(core[key])
        if core[key] not in core['files']:
            raise ValueError('LINUX_JOB_EXECUTED_VERSION_BINDING_REQUIRED')
    if (not isinstance(core['arguments'], list) or len(core['arguments']) > 32 or
            any(not isinstance(a, str) or not a or len(a) > 512 or '\x00' in a or '\n' in a
                for a in core['arguments']) or '@output' not in core['arguments']):
        raise ValueError('LINUX_JOB_FIXED_ARGUMENTS_REQUIRED')
    # Only these exact placeholders receive installed paths; no formatting/eval.
    if any(a.startswith('@') and a not in ('@output', '@input', '@settings') for a in core['arguments']):
        raise ValueError('LINUX_JOB_UNKNOWN_ARGUMENT_PLACEHOLDER')
    if core['arguments'] != ARGUMENTS:
        raise ValueError('LINUX_JOB_STANDARD_REVIEWED_RUNNER_INTERFACE_REQUIRED')
    limits = core['limits']
    if (set(limits) != set(MAXIMUM) or any(type(v) is not int or not 1 <= v <= MAXIMUM[k]
                                         for k, v in limits.items())):
        raise ValueError('LINUX_JOB_RESOURCE_BOUND_REQUIRED')
    env = core['environment']
    if set(env) != {'python_version', 'executable_sha256', 'packages'} or not isinstance(env['packages'], dict):
        raise ValueError('LINUX_JOB_ENVIRONMENT_REQUIRED')
    pin(env['executable_sha256'])
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', env['python_version']) or len(env['packages']) > 100:
        raise ValueError('LINUX_JOB_ENVIRONMENT_BOUND')
    for name, version in env['packages'].items():
        if not re.fullmatch('[A-Za-z0-9_.-]{1,100}', name) or not re.fullmatch('[A-Za-z0-9_.+!-]{1,100}', version):
            raise ValueError('LINUX_JOB_PINNED_DEPENDENCIES_REQUIRED')
    protocol = core['protocol']
    if (set(protocol) != {'subject', 'bindings', 'decision_path', 'decision_sha256', 'artifacts'} or
            not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}', protocol['subject'])):
        raise ValueError('LINUX_JOB_REVIEWED_PROTOCOL_REQUIRED')
    pin(protocol['decision_sha256'])
    if (not Path(protocol['decision_path']).is_absolute() or '..' in Path(protocol['decision_path']).parts
            or len(protocol['decision_path']) > 1000):
        raise ValueError('LINUX_JOB_INSTALLED_PROTOCOL_DECISION_REQUIRED')
    bindings = protocol['bindings']
    artifacts = {'protocol_sha256', 'input_manifest_sha256', 'partition_registry_sha256',
                 'exposure_history_sha256', 'literature_review_sha256', 'methodology_review_sha256'}
    if (set(bindings) != artifacts | {'source', 'experiment', 'prior_protocol_sha256'} or
            bindings['source'] != core['source'] or bindings['experiment'] != core['experiment'] or
            bindings['input_manifest_sha256'] != core['files'][core['input_manifest']] or
            set(protocol['artifacts']) != artifacts):
        raise ValueError('LINUX_JOB_PROTOCOL_INPUT_VERSION_CHANGED')
    if bindings['prior_protocol_sha256'] is not None: pin(bindings['prior_protocol_sha256'])
    for key in artifacts:
        pin(bindings[key]); path = relative(protocol['artifacts'][key])
        if core['files'].get(path) != bindings[key]:
            raise ValueError('LINUX_JOB_PROTOCOL_ARTIFACT_BINDING_REQUIRED')
    version = core['scientific_version']
    if set(version) != {'core_path', 'core_sha256', 'decision_path', 'decision_sha256'}:
        raise ValueError('LINUX_JOB_REVIEWED_SCIENTIFIC_VERSION_REQUIRED')
    for key in ('core', 'decision'):
        path = relative(version[key+'_path']); pin(version[key+'_sha256'])
        if core['files'].get(path) != version[key+'_sha256']:
            raise ValueError('LINUX_JOB_SCIENTIFIC_VERSION_FILE_BINDING_REQUIRED')
    if version['core_path'] != 'scientific-version.json' or not re.fullmatch(
            r'scientific-authority/[a-z0-9][a-z0-9-]{0,79}/round-1/decision.json', version['decision_path']):
        raise ValueError('LINUX_JOB_SCIENTIFIC_VERSION_FIXED_LAYOUT_REQUIRED')
    round_dir = Path(version['decision_path']).parent
    for name in ('scientific_decision.provider-receipt.json', 'scientific_decision_review.provider-receipt.json'):
        if (round_dir/name).as_posix() not in core['files']:
            raise ValueError('LINUX_JOB_ORIGINAL_PROVIDER_RECEIPTS_REQUIRED')
    if (round_dir.parent/'authority-transport.json').as_posix() not in core['files']:
        raise ValueError('LINUX_JOB_ORIGINAL_PROVIDER_RECEIPTS_REQUIRED')
    return core


def decision_request(core):
    validate_core(core)
    return {'action': ACTION, 'subject': core['job_id'],
            'bindings': {'job_core_sha256': digest(encoded(core)), 'source': core['source'],
                         'experiment': core['experiment'], 'spec_sha256': core['files'][core['spec']],
                         'code_sha256': core['files'][core['code']]}, 'transition': TRANSITION.copy()}


def verify_authority(config, core, decision_path, *, artifact_root=None, protocol_path=None, original_client=None):
    """Fixed existing scientific checks; no callable supplied by request consumers."""
    from orchestrator import formal_decisions, scientific_versions
    root = checked_source(config['source_root'], config['source'])
    if core['source'] != config['source']:
        raise ValueError('LINUX_JOB_CURRENT_SOURCE_REQUIRED')
    if original_client is None:
        raise ValueError('LINUX_JOB_PROTECTED_ORIGINAL_PROVENANCE_REQUIRED')
    version = scientific_versions.verify_authority(artifact_root or root, core['scientific_version'], original_client=original_client)
    validate_core(core)
    protocol = core['protocol']
    if version['protocol_decision_sha256'] != protocol['decision_sha256']:
        raise ValueError('LINUX_JOB_SCIENTIFIC_VERSION_PROTOCOL_CHANGED')
    protocol_decision = formal_decisions.verify_original_decision(root, protected(protocol_path or protocol['decision_path']),
        action='authorize_protocol', subject=protocol['subject'], bindings=protocol['bindings'],
        expected_transition={'from': 'REVIEWED_PROTOCOL_PROPOSAL', 'to': 'PROTOCOL_ELIGIBLE'},
        source=core['source'], original_client=original_client)
    if protocol_decision['_decision_sha256'] != protocol['decision_sha256'] or protocol_decision['decision'] != 'APPLY':
        raise ValueError('LINUX_JOB_PROTOCOL_DECISION_CHANGED')
    request = decision_request(core)
    decision = formal_decisions.verify_original_decision(root, decision_path, action=ACTION,
        subject=request['subject'], bindings=request['bindings'], expected_transition=TRANSITION,
        source=core['source'], original_client=original_client)
    if decision['decision'] != 'APPLY': raise ValueError('LINUX_JOB_LAUNCH_DECISION_DEFERRED')
    return {'decision_sha256': decision['_decision_sha256'], 'actor': decision['actor'],
            'policy': decision['policy'], 'scientific_version_authority': version,
            'job_core_sha256': request['bindings']['job_core_sha256'],
            'protocol_decision_sha256': protocol_decision['_decision_sha256']}


def environment(config, packages):
    """Read package metadata in the fixed interpreter; never install dependencies."""
    probe = ('import importlib.metadata,json,platform,sys; '
             'print(json.dumps({"python_version":platform.python_version(),'
             '"packages":{n:importlib.metadata.version(n) for n in json.loads(sys.argv[1])}},sort_keys=True))')
    result = subprocess.run([config['python'], '-I', '-B', '-c', probe, json.dumps(sorted(packages))],
        env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}, capture_output=True, timeout=30, check=True)
    if len(result.stdout) > 32768 or len(result.stderr) > 4096:
        raise ValueError('LINUX_JOB_ENVIRONMENT_PROBE_BOUND')
    return {**json.loads(result.stdout), 'executable_sha256': file_digest(Path(config['python']).resolve())}


def checked_inputs(config, core, *, payloads=True, artifact_root=None):
    validate_core(core)
    installed = checked_source(config['source_root'], config['source'])
    root = Path(artifact_root) if artifact_root is not None else installed
    if core['source'] != config['source']:
        raise ValueError('LINUX_JOB_CURRENT_SOURCE_REQUIRED')
    for name, sha in core['files'].items():
        if digest(regular(root/name)) != sha:
            raise ValueError('LINUX_JOB_SOURCE_ARTIFACT_CHANGED')
    requirements = {}
    for line in regular(root/core['requirements']).decode().splitlines():
        if not line.strip() or line.lstrip().startswith('#'): continue
        pair = line.strip().split('==')
        if len(pair) != 2 or pair[0] in requirements:
            raise ValueError('LINUX_JOB_EXACT_REQUIREMENTS_REQUIRED')
        requirements[pair[0]] = pair[1]
    if requirements != core['environment']['packages'] or environment(config, requirements) != core['environment']:
        raise ValueError('LINUX_JOB_EXECUTION_ENVIRONMENT_CHANGED')
    inputs = json.loads(regular(root/core['input_manifest']))
    if (set(inputs) != {'schema', 'root', 'files'} or inputs['schema'] != 'linux-scientific-inputs/v1' or
            not Path(inputs['root']).is_absolute() or '..' in Path(inputs['root']).parts or
            not isinstance(inputs['files'], dict) or len(inputs['files']) > 20000):
        raise ValueError('LINUX_JOB_INPUT_MANIFEST_SCHEMA')
    if inputs['root'] not in config['input_roots']:
        raise ValueError('LINUX_JOB_UNAUTHORIZED_DATA_ROOT')
    protected(inputs['root'])
    for name, sha in inputs['files'].items():
        relative(name); pin(sha)
        protected(Path(inputs['root'])/name)
        if payloads and file_digest(Path(inputs['root'])/name) != sha:
            raise ValueError('LINUX_JOB_INPUT_PAYLOAD_CHANGED')
    return inputs


def _decision_files(path, *, providers=False):
    """Retain the actual sealed judgment/review/provenance, never re-seal copies."""
    path = Path(path)
    raw = regular(path); value = json.loads(raw)
    files = {'decision.json': raw}
    for key in ('author_provenance', 'reviewer_provenance', 'judgment', 'review'):
        descriptor = value[key]; name = relative(descriptor['path'])
        body = regular(path.parent/name)
        if digest(body) != descriptor['sha256']:
            raise ValueError('LINUX_JOB_ORIGINAL_AUTHORITY_CHANGED')
        files[name] = body
    if providers:
        for name in ('scientific_decision.provider-receipt.json', 'scientific_decision_review.provider-receipt.json'):
            files[name] = regular(path.parent/name)
    return files


def capture(config, core, decision_path, *, original_client=None):
    """Broker captures one declared reviewed workspace; no per-job operator copy.

    Caller first verifies these original stage records with the protected broker.
    Only campaign scientific artifacts may differ from the installed Git source.
    Runtime/policy files supplied as review evidence must match the source's blob
    identities even when that reference file is absent from the sparse release.
    """
    if os.getuid() != 0: raise ValueError('LINUX_JOB_PROTECTED_BROKER_REQUIRED')
    validate_core(core)
    source = checked_source(config['source_root'], config['source'])
    if core['source'] != config['source']: raise ValueError('LINUX_JOB_CURRENT_SOURCE_REQUIRED')
    workspace = Path(config['proposals'])/core['proposal_id']/'workspace'
    launch = Path(decision_path).absolute()
    saved_formal = (launch.name == 'decision.json' and launch.parent.name == 'round-1' and
        launch.parent.parent.parent == Path(config['proposals']).parent/'formal-decisions' and
        re.fullmatch('[A-Za-z0-9_-]{1,100}', launch.parent.parent.name))
    if ('..' in Path(decision_path).parts or
            not (launch.is_relative_to(workspace) or saved_formal) or
            not Path(core['protocol']['decision_path']).absolute().is_relative_to(workspace)):
        raise ValueError('LINUX_JOB_DECISIONS_REQUIRE_REGISTERED_WORKSPACE')
    package = Path(config['snapshots'])/digest(encoded(core)); snapshot = package/'snapshot'
    if package.exists():
        if not (package/'capture.json').exists():
            raise ValueError('LINUX_JOB_PARTIAL_CAPTURE_RECONCILIATION_REQUIRED')
        receipt = json.loads(regular(package/'capture.json'))
        if receipt['core_sha256'] != digest(encoded(core)):
            raise ValueError('LINUX_JOB_CAPTURE_CORE_CHANGED')
        for name, sha in receipt['files'].items():
            if file_digest(package/name) != sha: raise ValueError('LINUX_JOB_CAPTURE_CHANGED')
        return receipt
    tree = subprocess.check_output(['git', '-c', 'safe.directory='+str(source), 'ls-tree', '-r', '--full-tree', core['source']],
        cwd=source, env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'GIT_NO_LAZY_FETCH': '1', 'GIT_OPTIONAL_LOCKS': '0'}, timeout=30)
    blobs = {}
    for line in tree.decode().splitlines():
        metadata, name = line.split('\t', 1); mode, kind, sha = metadata.split()
        if kind == 'blob' and mode in ('100644', '100755'): blobs[name] = sha
    files = {}; total = 0
    def add(name, raw):
        nonlocal total
        total += len(raw)-len(files.get(name, b''))
        if len(files) >= 5000 or total > 32000000:
            raise ValueError('LINUX_JOB_CAPTURE_BOUND')
        files[name] = raw
    # Copy only physical tracked release files; no .git, patient export or network.
    for name in blobs:
        path = source/name
        if path.exists(): add('snapshot/'+name, regular(path, 2000000))
    mutable = ('campaigns/isles24-pilot/experiments/'+core['experiment']+'/',
               'campaigns/isles24-pilot/protocols/', 'docs/isles-pilot/reviews/',
               Path(core['scientific_version']['decision_path']).parent.parent.as_posix()+'/')
    for name, sha in core['files'].items():
        raw = regular(workspace/name, 2000000)
        if digest(raw) != sha: raise ValueError('LINUX_JOB_PROPOSED_ARTIFACT_CHANGED')
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        science_test = 'tests/test_prediction_'+core['experiment'].lower()+'.py'
        if name not in ('scientific-version.json', science_test) and not name.startswith(mutable) and blobs.get(name) != blob:
            raise ValueError('LINUX_JOB_IMPLEMENTATION_OR_POLICY_OVERRIDE_REFUSED')
        add('snapshot/'+name, raw)
    for lane, path in [('launch', decision_path), ('protocol', core['protocol']['decision_path'])]:
        for name, raw in _decision_files(path, providers=True).items(): add('authority/'+lane+'/round-1/'+name, raw)
        add('authority/'+lane+'/authority-transport.json', regular(Path(path).parent.parent/'authority-transport.json'))
    if len(files) > 5000 or sum(map(len, files.values())) > 32000000:
        raise ValueError('LINUX_JOB_CAPTURE_BOUND')
    # Prospective capture may fail validation; preserve its exact partial forever.
    package.mkdir(mode=0o750); package.chmod(0o750); os.chown(package, 0, config['worker_gid'])
    original(package/'capture-intent.json', encoded({'core_sha256': digest(encoded(core)),
             'files': {name: digest(raw) for name, raw in files.items()}})+b'\n')
    os.chown(package/'capture-intent.json', 0, config['worker_gid'])
    for name, raw in sorted(files.items()):
        path = package/name
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o750)
        for parent in (path.parent, *path.parent.parents):
            if parent == package: break
            parent.chmod(0o750); os.chown(parent, 0, config['worker_gid'])
        original(path, raw); os.chown(path, 0, config['worker_gid'])
    proof = verify_authority(config, core, package/'authority/launch/round-1/decision.json',
                             artifact_root=snapshot, protocol_path=package/'authority/protocol/round-1/decision.json',
                             original_client=original_client)
    checked_inputs(config, core, payloads=False, artifact_root=snapshot)
    receipt = {'schema': 'linux-scientific-capture/v1', 'core_sha256': digest(encoded(core)),
               'implementation_source': config['source'], 'artifact_root': str(snapshot),
               'launch_decision': str(package/'authority/launch/round-1/decision.json'),
               'protocol_decision': str(package/'authority/protocol/round-1/decision.json'),
               'files': {name: digest(raw) for name, raw in files.items()}, 'authority': proof}
    original(package/'capture.json', encoded(receipt)+b'\n')
    os.chown(package/'capture.json', 0, config['worker_gid'])
    return receipt


def checked_capture(config, binding):
    package = protected(Path(config['snapshots'])/digest(encoded(binding['core'])))
    receipt = json.loads(regular(package/'capture.json'))
    if (digest(encoded(receipt)) != binding['capture_sha256'] or
            receipt['artifact_root'] != binding['artifact_root'] or
            receipt['core_sha256'] != digest(encoded(binding['core'])) or
            receipt['authority'] != binding['authority']):
        raise ValueError('LINUX_JOB_CAPTURE_BINDING_CHANGED')
    for name, sha in receipt['files'].items():
        relative(name)
        if file_digest(package/name) != sha: raise ValueError('LINUX_JOB_CAPTURE_CHANGED')
    return receipt


def render_unit(config):
    """Return the exact reviewed template with only two installed path bindings."""
    for key in ('source_root', 'outputs'):
        if not re.fullmatch(r'/[A-Za-z0-9_./-]+', config[key]) or '..' in Path(config[key]).parts:
            raise ValueError('LINUX_JOB_SYSTEMD_FIXED_PATH_REQUIRED')
    template = (Path(__file__).resolve().parents[1]/'deploy/research-system/research-system-scientific-job@.service.in').read_text()
    return template.replace('@SOURCE_ROOT@', config['source_root']).replace('@OUTPUTS@', config['outputs'])


class Registry(Store):
    """Root broker operations; callers hold existing live controls/admission lock."""
    def __init__(self, config):
        if os.getuid() != 0:
            raise ValueError('LINUX_JOB_PROTECTED_BROKER_REQUIRED')
        self.config = config
        super().__init__(config['database'])
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS scientific_attempts
          (id TEXT PRIMARY KEY,job TEXT UNIQUE NOT NULL,request TEXT NOT NULL,status TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS scientific_analysis
          (event TEXT PRIMARY KEY,job TEXT UNIQUE NOT NULL,status TEXT NOT NULL);
        ''')

    def register_scientific(self, core, decision_path, *, original_client):
        captured = capture(self.config, core, decision_path, original_client=original_client)
        # Duplicate capture is read-only, but fresh registration must still check
        # current scientific authority and originals, including later criticism.
        current = verify_authority(self.config, core, captured['launch_decision'],
            artifact_root=captured['artifact_root'], protocol_path=captured['protocol_decision'],
            original_client=original_client)
        if current != captured['authority']: raise ValueError('LINUX_JOB_CAPTURE_AUTHORITY_CHANGED')
        binding = {'core': core, 'authority': captured['authority'],
                   'decision_path': captured['launch_decision'], 'protocol_path': captured['protocol_decision'],
                   'artifact_root': captured['artifact_root'], 'capture_sha256': digest(encoded(captured)),
                   'runtime_configuration': self.config}
        self.register(core['job_id'], binding)
        self.db.execute("UPDATE jobs SET phase='linux_scientific' WHERE id=? AND phase='acquisition'", (core['job_id'],))
        return {'job': core['job_id'], 'core_sha256': digest(encoded(core)), 'status': self.get(core['job_id'])['status']}

    def dispatch(self, job, *, original_client):
        """After protected caller's current stop/change/control checks; no model or shell."""
        identifier(job)
        with lock(Path(self.config['requests'])/'.dispatch.lock'):
            row = self.get(job); binding = json.loads(row['binding']); core = binding['core']
            prior = self.db.execute('SELECT * FROM scientific_attempts WHERE job=?', (job,)).fetchone()
            if prior:
                return {'status': prior['status'], 'unit': UNIT.format(prior['id']),
                        'attempt': prior['id'], 'automatic_restart': False}
            if row['status'] != 'READY' or row['phase'] not in ('linux_scientific', 'scientific_validation'):
                raise ValueError('LINUX_JOB_NOT_READY')
            if binding['runtime_configuration'] != self.config:
                raise ValueError('LINUX_JOB_REGISTERED_CONFIGURATION_CHANGED')
            if self.db.execute("SELECT count(*) FROM scientific_attempts WHERE status NOT IN ('COMPLETE','FAILED')").fetchone()[0] >= self.config['maximum_parallel']:
                raise ValueError('LINUX_JOB_PARALLEL_RESOURCE_LIMIT')
            checked_capture(self.config, binding)
            authority = verify_authority(self.config, core, binding['decision_path'],
                artifact_root=binding['artifact_root'], protocol_path=binding['protocol_path'], original_client=original_client)
            if authority != binding['authority']:
                raise ValueError('LINUX_JOB_AUTHORITY_VERSION_CHANGED')
            checked_inputs(self.config, core, payloads=False, artifact_root=binding['artifact_root'])
            validation = row['phase'] == 'scientific_validation'
            if validation:
                from orchestrator import scientific_validation as semantic
                semantic.check_registered(self, binding, original_client=original_client)
            elif 'semantic_validation' in binding:
                raise ValueError('SEMANTIC_VALIDATION_PHASE_CHANGED')
            attempt = digest(encoded(binding))
            request = {'schema': semantic.ATTEMPT if validation else 'linux-scientific-attempt/v1', 'attempt': attempt,
                       'binding': binding, 'registered_at_ns': time.time_ns()}
            # A missing request after this transaction is ambiguous, never a second attempt.
            self.db.execute('BEGIN IMMEDIATE')
            try:
                self.db.execute('INSERT INTO scientific_attempts VALUES(?,?,?,?)', (attempt, job, encoded(request).decode(), 'INTENT'))
                self.db.execute("UPDATE jobs SET status='RUNNING',lease=0 WHERE id=?", (job,))
                self.db.execute('COMMIT')
            except BaseException:
                self.db.execute('ROLLBACK'); raise
            folder = Path(self.config['outputs'])/attempt
            folder.mkdir(mode=0o700); os.chmod(folder, 0o700)
            os.chown(folder, self.config['worker_uid'], self.config['worker_gid'])
            path = Path(self.config['requests'])/(attempt+'.json')
            original(path, encoded(request)+b'\n'); os.chown(path, 0, self.config['worker_gid'])
            if validation:
                context = semantic.binding_path(self.config, attempt)
                from orchestrator.hosted_cycle import encoded as context_encoded
                original(context, context_encoded(binding['semantic_validation']['binding']))
                os.chown(context, 0, self.config['worker_gid'])
            self.db.execute("UPDATE scientific_attempts SET status='REGISTERED' WHERE id=?", (attempt,))
            return {'status': 'REGISTERED', 'attempt': attempt, 'unit': UNIT.format(attempt), 'automatic_restart': False}

    def observe(self):
        """Model-free polling. Repeated unchanged completion yields the same event."""
        events = []
        for row in self.db.execute('SELECT * FROM scientific_attempts ORDER BY rowid').fetchall():
            request = json.loads(row['request']); folder = Path(self.config['outputs'])/row['id']
            outcome_path = folder/'outcome.json'
            if not outcome_path.exists():
                if (folder/'started.json').exists():
                    self.db.execute("UPDATE scientific_attempts SET status='STARTED_OR_UNCERTAIN' WHERE id=?", (row['id'],))
                continue
            try:
                receipt = json.loads(regular(outcome_path))
                validate_outcome(request, folder, receipt)
                core = request['binding']['core']
                from orchestrator import scientific_validation as semantic
                if request['schema'] == semantic.ATTEMPT:
                    # A validator completion is not a new experiment completion or
                    # an accepted-result event. The protected reader exposes its
                    # bounded original to the distinct pending import path.
                    if receipt['status'] == 'COMPLETE':
                        semantic.checked_output(self.config, request, folder/'artifacts')
                    self.db.execute('BEGIN IMMEDIATE')
                    try:
                        self.db.execute('UPDATE scientific_attempts SET status=? WHERE id=?',
                                        (receipt['status'], row['id']))
                        self.db.execute('UPDATE jobs SET status=? WHERE id=?', (receipt['status'], row['job']))
                        self.db.execute('COMMIT')
                    except BaseException:
                        self.db.execute('ROLLBACK'); raise
                    continue
                event = {'schema': 'linux-scientific-completion/v1', 'event': digest(encoded(receipt)),
                    'kind': 'ANALYSIS_AVAILABLE', 'job': row['job'], 'attempt': row['id'],
                    'core_sha256': digest(encoded(core)), 'source': core['source'],
                    'execution_binding': core,
                    'runtime_configuration_sha256': digest(encoded(request['binding']['runtime_configuration'])),
                    'result_manifest_sha256': receipt['result_manifest_sha256'],
                    'authority': request['binding']['authority'], 'outcome': receipt,
                    'scientific_acceptance': False, 'model_calls': 0}
                raw = encoded(event).decode()
                old = self.db.execute('SELECT payload FROM events WHERE id=?', (event['event'],)).fetchone()
                if old and old[0] != raw: raise ValueError('LINUX_JOB_COMPLETION_IDENTITY_CHANGED')
                self.db.execute('BEGIN IMMEDIATE')
                try:
                    self.db.execute('INSERT OR IGNORE INTO events VALUES(?,?,?)', (event['event'], row['job'], raw))
                    self.db.execute('INSERT OR IGNORE INTO scientific_analysis VALUES(?,?,?)', (event['event'], row['job'], 'AVAILABLE'))
                    self.db.execute('UPDATE scientific_attempts SET status=? WHERE id=?', (receipt['status'], row['id']))
                    self.db.execute('UPDATE jobs SET status=? WHERE id=?', (receipt['status'], row['job']))
                    self.db.execute('COMMIT')
                except BaseException: self.db.execute('ROLLBACK'); raise
                events.append(event)
            except (ValueError, KeyError, OSError, TypeError):
                self.block(row['job'], 'SCIENTIFIC_COMPLETION_RECONCILIATION_REQUIRED')
        return events

    def status(self):
        return {'jobs': [dict(r) for r in self.db.execute('SELECT id,phase,status FROM jobs')],
                'attempts': [dict(r) for r in self.db.execute('SELECT id,job,status FROM scientific_attempts')],
                'analysis': [dict(r) for r in self.db.execute('SELECT * FROM scientific_analysis')],
                'inbox': self.inbox(), 'model_calls': 0, 'scientific_acceptance': False}


def inventory(folder, limits):
    rows = {}; total = 0
    for path in sorted(Path(folder).rglob('*')):
        st = path.lstat()
        if stat.S_ISDIR(st.st_mode): continue
        if not stat.S_ISREG(st.st_mode): raise ValueError('LINUX_JOB_OUTPUT_NOT_REGULAR')
        total += st.st_size
        if len(rows) >= limits['output_files'] or total > limits['output_bytes']:
            raise ValueError('LINUX_JOB_OUTPUT_LIMIT')
        rows[path.relative_to(folder).as_posix()] = {'bytes': st.st_size, 'sha256': file_digest(path)}
    return rows


def result_inventory(folder, limits):
    try:
        return {'status': 'COMPLETE_INVENTORY', 'files': inventory(folder, limits)}
    except ValueError:
        # No truncated result is admissible. Preserve originals, expose a failed
        # completion for formal diagnosis, and require explicit reconciliation.
        return {'status': 'OUTPUT_RECONCILIATION_REQUIRED', 'files': None}


def validate_outcome(request, folder, receipt):
    expected = {'schema', 'attempt', 'request_sha256', 'status', 'exit_code', 'reason', 'child_process_sha256',
                'started_sha256', 'wall_seconds', 'result_manifest_sha256', 'scientific_acceptance'}
    if (set(receipt) != expected or receipt['schema'] != 'linux-scientific-outcome/v1' or
            receipt['attempt'] != request['attempt'] or receipt['request_sha256'] != digest(encoded(request)) or
            receipt['status'] not in ('COMPLETE', 'FAILED') or receipt['scientific_acceptance'] is not False or
            type(receipt['wall_seconds']) not in (int, float) or not 0 <= receipt['wall_seconds'] <= 172900 or
            type(receipt['exit_code']) not in (int, type(None)) or
            (receipt['status'] == 'COMPLETE' and (receipt['exit_code'] != 0 or receipt['reason'] != 'EXIT_ZERO_REQUIRES_FORMAL_VALIDATION'))):
        raise ValueError('LINUX_JOB_OUTCOME_BINDING')
    started = regular(Path(folder)/'started.json')
    manifest = regular(Path(folder)/'result-manifest.json')
    if digest(started) != receipt['started_sha256'] or digest(manifest) != receipt['result_manifest_sha256']:
        raise ValueError('LINUX_JOB_ORIGINAL_COMPLETION_CHANGED')
    child = Path(folder)/'child-started.json'
    child_sha = digest(regular(child)) if child.exists() else None
    if child_sha != receipt['child_process_sha256'] or receipt['exit_code'] is not None and child_sha is None:
        raise ValueError('LINUX_JOB_ORIGINAL_CHILD_IDENTITY_CHANGED')
    observed = result_inventory(Path(folder)/'artifacts', request['binding']['core']['limits'])
    if json.loads(manifest) != observed or (receipt['status'] == 'COMPLETE' and observed['status'] != 'COMPLETE_INVENTORY'):
        raise ValueError('LINUX_JOB_RESULT_CHANGED')


def run_worker(config, attempt):
    """Executed only by the fixed unprivileged systemd instance; never retry."""
    pin(attempt)
    if os.getuid() != config['worker_uid']:
        raise ValueError('LINUX_JOB_WORKER_IDENTITY_REQUIRED')
    path = protected(Path(config['requests'])/(attempt+'.json'))
    request = json.loads(regular(path)); core = request['binding']['core']
    from orchestrator import scientific_validation as semantic
    validation = request.get('schema') == semantic.ATTEMPT
    if (request.get('schema') not in ('linux-scientific-attempt/v1', semantic.ATTEMPT)
            or ('semantic_validation' in request['binding']) != validation
            or request['attempt'] != attempt or digest(encoded(request['binding'])) != attempt):
        raise ValueError('LINUX_JOB_REGISTERED_ATTEMPT_REQUIRED')
    folder = Path(config['outputs'])/attempt
    st = folder.lstat()
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != config['worker_uid'] or stat.S_IMODE(st.st_mode) != 0o700:
        raise ValueError('LINUX_JOB_PRIVATE_OUTPUT_REQUIRED')
    with lock(folder/'.worker.lock'):
        if (folder/'outcome.json').exists():
            receipt = json.loads(regular(folder/'outcome.json')); validate_outcome(request, folder, receipt)
            return receipt
        if (folder/'started.json').exists() or (folder/'artifacts').exists():
            raise ValueError('LINUX_JOB_UNCERTAIN_ORIGINAL_NO_RESTART')
        # Durable identity precedes even preflight; failures retain an actual receipt.
        started = {'pid': os.getpid(), 'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                   'start_ticks': Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19],
                   'request_sha256': digest(encoded(request)), 'time_ns': time.time_ns()}
        raw = encoded(started)+b'\n'; original(folder/'started.json', raw, 0o600)
        artifacts = folder/'artifacts'; artifacts.mkdir(mode=0o700)
        start = time.monotonic(); code = None; reason = 'PREFLIGHT_FAILED'; child = None
        try:
            if request['binding']['runtime_configuration'] != config:
                raise ValueError('LINUX_JOB_REGISTERED_CONFIGURATION_CHANGED')
            checked_capture(config, request['binding'])
            artifact_root = request['binding']['artifact_root']
            inputs = checked_inputs(config, core, artifact_root=artifact_root)
            aliases = {'@output': str(artifacts/'result'), '@input': inputs['root'],
                       '@settings': str(Path(artifact_root)/core['settings'])}
            argv = (semantic.worker_argv(config, request, artifacts, inputs) if validation else
                    [config['python'], '-B', str(Path(artifact_root)/core['code']),
                     *[aliases.get(a, a) for a in core['arguments']]])
            def bounds():
                limits = core['limits']
                for resource_id, cap in ((resource.RLIMIT_AS, limits['memory_bytes']),
                        (resource.RLIMIT_CPU, limits['cpu_seconds']), (resource.RLIMIT_FSIZE, limits['output_bytes']),
                        (resource.RLIMIT_NOFILE, 64)):
                    resource.setrlimit(resource_id, (cap, cap))
            with (artifacts/'stdout.log').open('xb') as stdout, (artifacts/'stderr.log').open('xb') as stderr:
                child = subprocess.Popen(argv, cwd=artifact_root,
                    env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'HOME': str(artifacts),
                         'PYTHONNOUSERSITE': '1', 'PYTHONDONTWRITEBYTECODE': '1',
                         'OMP_NUM_THREADS': '2', 'OPENBLAS_NUM_THREADS': '2'},
                    stdout=stdout, stderr=stderr, start_new_session=True, preexec_fn=bounds)
                child_identity = {'pid': child.pid, 'boot_id': started['boot_id'],
                    'start_ticks': Path('/proc', str(child.pid), 'stat').read_text().rsplit(')', 1)[1].split()[19],
                    'argv_sha256': digest(encoded(argv)), 'environment': core['environment'],
                    'core_sha256': digest(encoded(core))}
                original(folder/'child-started.json', encoded(child_identity)+b'\n', 0o600)
                while child.poll() is None:
                    if time.monotonic()-start > core['limits']['wall_seconds']:
                        reason = 'WALL_TIME_LIMIT'; raise TimeoutError(reason)
                    # A bounded polling overshoot is possible; per-file OS and unit caps also apply.
                    total = 0; count = 0
                    for p in artifacts.rglob('*'):
                        st = p.lstat()
                        if stat.S_ISDIR(st.st_mode): continue
                        if not stat.S_ISREG(st.st_mode): raise ValueError('UNSAFE_OUTPUT')
                        total += st.st_size; count += 1
                        if total > core['limits']['output_bytes'] or count > core['limits']['output_files']:
                            reason = 'OUTPUT_LIMIT'; raise ValueError(reason)
                    time.sleep(0.1)
                code = child.returncode
                if validation and code == 0:
                    reason = 'SEMANTIC_VALIDATION_FAILED'
                    semantic.checked_output(config, request, artifacts)
                reason = 'EXIT_ZERO_REQUIRES_FORMAL_VALIDATION' if code == 0 else 'PROCESS_FAILED'
        except (OSError, ValueError, subprocess.SubprocessError, TimeoutError):
            if child is not None and child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL); child.wait(timeout=10)
                code = child.returncode
        finally:
            if child is not None:
                try: os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError: pass
        # Keep oversized/unsafe originals intact. No valid completion is invented.
        contents = result_inventory(artifacts, core['limits'])
        if contents['status'] != 'COMPLETE_INVENTORY':
            reason = 'OUTPUT_RECONCILIATION_REQUIRED'
        manifest = encoded(contents)+b'\n'
        original(folder/'result-manifest.json', manifest, 0o600)
        receipt = {'schema': 'linux-scientific-outcome/v1', 'attempt': attempt,
            'request_sha256': digest(encoded(request)), 'status': 'COMPLETE' if code == 0 and reason == 'EXIT_ZERO_REQUIRES_FORMAL_VALIDATION' else 'FAILED',
            'exit_code': code, 'reason': reason, 'started_sha256': digest(raw),
            'child_process_sha256': digest(regular(folder/'child-started.json')) if (folder/'child-started.json').exists() else None,
            'wall_seconds': time.monotonic()-start, 'result_manifest_sha256': digest(manifest),
            'scientific_acceptance': False}
        original(folder/'outcome.json', encoded(receipt)+b'\n', 0o600)
        return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['worker', 'poll', 'status'])
    parser.add_argument('--attempt')
    args = parser.parse_args()
    config = configuration()
    if args.operation == 'worker':
        pin(args.attempt); result = run_worker(config, args.attempt)
    else:
        if args.attempt is not None: parser.error('--attempt is worker-only')
        registry = Registry(config)
        result = registry.observe() if args.operation == 'poll' else registry.status()
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__': main()
