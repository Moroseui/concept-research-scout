#!/usr/bin/env python3
"""Prepare separate protected writer/admission setup; never install or initialize.

Run from an exact reviewed source as the setup administrator. Only private proposal
files are created. Existing science configuration, credentials, consumed turns and
Git refs are not changed. No key contents, tokens, APIs, models or services are used.
Preserve a partial destination and reconcile it; this helper never overwrites it.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[2]
APPROVAL = 'docs/operations/PROTECTED_HANDOVER_APPROVED_20260908.json'
APPROVAL_SHA256 = '0be99c7b0b4e5e9eb16d9ebf8b44e369f6ef07233b903173fcd5355536127d1a'
DECISION = ('03eb1d42ffc89e3e0c8b6697dd4037455f7a239d:' + APPROVAL +
            '#sha256=' + APPROVAL_SHA256)
POLICY_FILE = 'deploy/research-system/dispatch-limiter.approved.json'
IDENTITY_FILE = 'docs/operations/WRITER_APP_IDENTITY_20260908.json'
CONFIG_BASE = Path('/etc/research-system')
STATE_BASE = Path('/var/lib/research-system/handover-broker')
REPOSITORY = 'Moroseui/concept-research-scout'
REMOTE = 'https://github.com/' + REPOSITORY + '.git'
BRANCH = 'astra/infrastructure-milestone-record'
REF = 'refs/heads/automation/dispatch-state'
PERMISSIONS = {'contents': 'write', 'actions': 'read', 'metadata': 'read'}


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def policy_digest(value):
    # Exact existing broker and Actions waiter binding, including all fields.
    return digest(json.dumps(value, sort_keys=True).encode())


def approved_policy():
    return {'version': 1, 'status': 'RATIFIED', 'n': 48,
            'window': 'UTC_CALENDAR_DAY', 'state_ref': REF,
            'state_write_permission': 'OPERATOR_AUTHORIZED',
            'operator_approval': DECISION, 'reset_operators': ['ssh-uid:0'],
            'server_semantics': 'OPERATOR_AUTHORIZED_V1', 'repository': REPOSITORY}


def checked_path(path, base):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts or path == base or not path.is_relative_to(base):
        raise ValueError('PROTECTED_PATH_REQUIRED')
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('PROTECTED_PATH_SYMLINK')
    return path


def protected_metadata(path, *, private=False):
    info = Path(path).lstat()
    denied = 0o077 if private else 0o022
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & denied:
        raise ValueError('ROOT_PROTECTED_INPUT_REQUIRED')
    for parent in Path(path).parents:
        item = parent.lstat()
        if not stat.S_ISDIR(item.st_mode) or item.st_uid != 0 or item.st_mode & 0o022:
            raise ValueError('ROOT_PROTECTED_PARENT_REQUIRED')
    return info


def seal(info):
    return (info.st_dev, info.st_ino, info.st_uid, info.st_gid,
            info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def read_metadata_file(path, *, private=False):
    info = protected_metadata(path, private=private)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if seal(info) != seal(before) or before.st_size > 100000:
            raise ValueError('PROTECTED_INPUT_CHANGED_OR_OVERSIZED')
        raw = stream.read(100001)
        if len(raw) > 100000 or seal(before) != seal(os.fstat(stream.fileno())):
            raise ValueError('PROTECTED_INPUT_CHANGED_OR_OVERSIZED')
    return raw, seal(before)


def plan(source, approval_raw, policy, identity, writer, broker, runtime, destination, writer_path):
    """Pure plan/schema validation. Does not touch keys, state, Git or services."""
    if not isinstance(source, str) or not re.fullmatch('[0-9a-f]{40}', source):
        raise ValueError('EXACT_SOURCE_REQUIRED')
    if digest(approval_raw) != APPROVAL_SHA256:
        raise ValueError('EXACT_OPERATOR_APPROVAL_REQUIRED')
    if (policy != approved_policy() or type(policy.get('version')) is not int
            or type(policy.get('n')) is not int):
        raise ValueError('EXACT_APPROVED_SHARED_POLICY_REQUIRED')
    if (identity.get('status') != 'REPLACEMENT_KEY_AND_SELECTED_APP_VERIFIED_NOT_ACTIVATED'
            or identity.get('app_id') != 4879374 or identity.get('installation_id') != 160193942
            or identity.get('repository_id') != 1323461276
            or identity.get('repository') != REPOSITORY
            or identity.get('permissions') != PERMISSIONS
            or identity.get('repository_selection') != 'selected'
            or identity.get('total_repositories') != 1 or identity.get('key_root_only') is not True
            or identity.get('role_reads_denied') != {name: True for name in
                ('research-controller', 'research-driver', 'research-reviewer', 'research-worker')}):
        raise ValueError('VERIFIED_SELECTED_WRITER_IDENTITY_REQUIRED')
    if (set(writer) != {'app_id', 'installation_id', 'repository_id', 'private_key', 'permission_decision'}
            or any(type(writer[k]) is not int or writer[k] != identity[k]
                   for k in ('app_id', 'installation_id', 'repository_id'))
            or not isinstance(writer['permission_decision'], str) or not writer['permission_decision']):
        raise ValueError('EXACT_VERIFIED_WRITER_CONFIGURATION_REQUIRED')
    checked_path(writer['private_key'], CONFIG_BASE)
    checked_path(writer_path, CONFIG_BASE)
    destination = checked_path(destination, CONFIG_BASE)
    if (broker.get('mode') != 'SYNTHETIC_FIXTURE' or broker.get('writer_config') is not None
            or broker.get('model_mode') != 'SUPERVISED'
            or type(broker.get('max_model_turns')) is not int or not 1 <= broker['max_model_turns'] <= 4
            or broker.get('repository') != REMOTE or broker.get('branch') != BRANCH
            or type(broker.get('controller_uid')) is not int or broker['controller_uid'] <= 0
            or broker.get('operator_uids') != [0]
            or runtime.get('controller_uid') != broker['controller_uid']
            or runtime.get('source') not in broker.get('sources', [])
            or runtime.get('publication') is not None or runtime.get('report_schedule') is not None):
        raise ValueError('EXISTING_SCIENCE_CONFIGURATION_REQUIRED')
    root = STATE_BASE / ('live-setup-' + source[:12] + '-' + policy_digest(policy)[:12])
    roots = [root / name for name in ('publication', 'ledger', 'turns')]
    preserved = [Path(broker[k]) for k in ('publication_root', 'ledger_repo', 'turn_root')]
    preserved.append(Path(runtime['state']))
    if any(not p.is_absolute() or '..' in p.parts for p in preserved):
        raise ValueError('EXISTING_STATE_PATH_REQUIRED')
    if any(a.is_relative_to(b) or b.is_relative_to(a) for a in roots for b in preserved):
        raise ValueError('EXISTING_SCIENCE_STATE_OVERLAP')
    configured = {'mode': 'LIVE_APPROVED', 'repository': REMOTE, 'branch': BRANCH,
                  'controller_uid': broker['controller_uid'], 'operator_uids': [0],
                  'sources': [source], 'ledger_repo': str(roots[1]),
                  'publication_root': str(roots[0]), 'policy': policy,
                  'writer_config': str(writer_path), 'model_mode': 'DISABLED',
                  'turn_root': str(roots[2]), 'max_model_turns': 0}
    deployment = {'status': 'PREPARATION_ONLY_NOT_INSTALLED', 'source': source,
                  'decision_ref': DECISION, 'policy_sha256': policy_digest(policy),
                  'state_root': str(root), 'directories':
                      [{'path': str(p), 'uid': 0, 'mode': '0700'} for p in [root, *roots]],
                  'ledger': {'path': str(roots[1]), 'origin': REMOTE, 'state_ref': REF,
                             'initialization': 'SEPARATE_OPERATOR_ABSENT_REF_CAS'},
                  'publication': {'path': str(roots[0]), 'origin': REMOTE, 'branch': BRANCH,
                                  'baseline': 'RECONCILE_EXACT_REMOTE_BEFORE_SEPARATE_SETUP'},
                  'broker_proposal': str(destination / 'broker.proposed.json'),
                  'initialize_request': str(destination / 'initialize.request.proposed.json'),
                  'preserved_science_state_paths': [str(p) for p in preserved],
                  'required_before_install': ['SOURCE_REVIEW_AND_CURRENT_INPUT_RECONCILIATION',
                      'WRITER_IDENTITY_RECHECK_WITHOUT_LOGGING_CREDENTIALS',
                      'REMOTE_LEDGER_AND_PUBLICATION_REF_RECONCILIATION'],
                  'reserved': ['MAIN_MERGE', 'PATIENT_LAUNCH', 'UNATTENDED_ACTIVATION'],
                  'services_changed': False, 'timer_enabled': False,
                  'model_calls': 0, 'tokens_minted': 0, 'git_writes': 0}
    return configured, deployment


def write_new(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def prepare(source, writer_config, destination,
            broker_config='/etc/research-system/handover-broker.json',
            runtime_config='/etc/research-system/handover-controller.json'):
    if os.getuid() != 0:
        raise ValueError('SETUP_ADMIN_REQUIRED')
    sys.path.insert(0, str(ROOT))
    from orchestrator.remote_supervisor import checked_source
    checked_source(ROOT, source)
    destination = checked_path(destination, CONFIG_BASE)
    parent = destination.parent
    info = parent.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o077:
        raise ValueError('FRESH_ROOT_PRIVATE_PREPARATION_PARENT_REQUIRED')
    # Directory advisory lock creates no shared lock file and never touches science.
    lockfd = os.open(CONFIG_BASE, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        try:
            fcntl.flock(lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('CONCURRENT_SETUP_RECONCILE') from None
        if destination.exists() or destination.is_symlink():
            raise ValueError('EXISTING_OR_PARTIAL_SETUP_RECONCILE')
        paths = {'broker': (checked_path(broker_config, CONFIG_BASE), True),
                 'runtime': (checked_path(runtime_config, CONFIG_BASE), False),
                 'writer': (checked_path(writer_config, CONFIG_BASE), True)}
        snapshots = {name: read_metadata_file(path, private=private)
                     for name, (path, private) in paths.items()}
        source_inputs = {name: (ROOT / name).read_bytes()
                         for name in (APPROVAL, POLICY_FILE, IDENTITY_FILE)}
        objects = {name: json.loads(value[0]) for name, value in snapshots.items()}
        configured, deployment = plan(source, source_inputs[APPROVAL],
            json.loads(source_inputs[POLICY_FILE]), json.loads(source_inputs[IDENTITY_FILE]),
            objects['writer'], objects['broker'], objects['runtime'], destination, writer_config)
        # Stat-only ownership check: private-key contents are never opened here.
        key_path = objects['writer']['private_key']
        key_seal = seal(protected_metadata(key_path, private=True))
        targets = [Path(row['path']) for row in deployment['directories']]
        if any(p.exists() or p.is_symlink() for p in targets):
            raise ValueError('EXISTING_LIVE_STATE_RECONCILE')

        def unchanged():
            checked_source(ROOT, source)
            if any((ROOT / name).read_bytes() != raw for name, raw in source_inputs.items()):
                raise ValueError('SOURCE_INPUT_CHANGED')
            if any(read_metadata_file(path, private=private) != snapshots[name]
                   for name, (path, private) in paths.items()):
                raise ValueError('SCIENCE_OR_WRITER_CONFIGURATION_CHANGED')
            if seal(protected_metadata(key_path, private=True)) != key_seal:
                raise ValueError('WRITER_KEY_METADATA_CHANGED')
            if any(p.exists() or p.is_symlink() for p in targets):
                raise ValueError('LIVE_STATE_CREATED_DURING_PREPARATION')

        unchanged()
        destination.mkdir(mode=0o700)
        for name in ('broker', 'runtime'):
            write_new(destination / (name + '.original.bytes'), snapshots[name][0])
        write_new(destination / 'dispatch-limiter.approved.json', source_inputs[POLICY_FILE])
        write_new(destination / 'broker.proposed.json', encoded(configured))
        write_new(destination / 'initialize.request.proposed.json', encoded({'decision_ref': DECISION}))
        write_new(destination / 'deployment-plan.json', encoded(deployment))
        unchanged()
        receipt = {'status': 'LIVE_HANDOVER_SETUP_PREPARED_NOT_INSTALLED', 'source': source,
                   'operator_approval_sha256': APPROVAL_SHA256,
                   'policy_sha256': deployment['policy_sha256'],
                   'source_input_sha256': {k: digest(v) for k, v in source_inputs.items()},
                   'protected_input_sha256': {k: digest(v[0]) for k, v in snapshots.items()},
                   'artifact_sha256': {p.name: digest(p.read_bytes()) for p in sorted(destination.iterdir())},
                   'science_configuration_unchanged': True, 'consumed_turns_modified': False,
                   'writer_key_contents_read': False, 'remote_operations': 0,
                   'state_initialized': False, 'models_started': 0,
                   'services_changed': False, 'unattended_activated': False}
        write_new(destination / 'receipt.json', encoded(receipt))
        outfd = os.open(destination, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(outfd)
        finally:
            os.close(outfd)
        return receipt
    finally:
        os.close(lockfd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'writer-config', 'destination'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--broker-config', default='/etc/research-system/handover-broker.json')
    parser.add_argument('--runtime-config', default='/etc/research-system/handover-controller.json')
    try:
        print(json.dumps(prepare(**vars(parser.parse_args()))))
    except Exception as error:
        # Never echo arbitrary paths/configuration or credential-operation diagnostics.
        reason = str(error)
        if not re.fullmatch('[A-Z][A-Z0-9_]{1,100}', reason):
            reason = 'SETUP_PREPARATION_FAILED_PRESERVE_PARTIAL_DESTINATION'
        print(json.dumps({'status': 'REFUSED', 'reason': reason}), file=sys.stderr)
        raise SystemExit(2) from None
