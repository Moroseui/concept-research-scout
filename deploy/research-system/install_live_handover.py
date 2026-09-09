#!/usr/bin/env python3
"""Install the distinct model-disabled live broker socket; never start or enable.

Run only as the setup administrator with the exact source-review manifest. Reuse
04d source, its prepared configuration and completed canary state. Existing fixture,
original evidence and partial installations are preserved. No credential is read,
no admission/reset is performed, and no model or controller/timer is launched.
"""
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pwd
import grp
import re
import stat
import subprocess
import sys

SOURCE = '04d67a00422e862d62acf356bd9526a4af449fb1'
SOURCE_ROOT = Path('/opt/research-system/releases') / (SOURCE+'-writer-preparation/snapshot')
SETUP = Path('/etc/research-system/writer-setup-20260908')
STAGING = SETUP / 'live-install-04d67a00'
PREPARATION = SETUP / 'live-preparation-04d67a00'
CANARY = SETUP / 'live-canary-04d67a00'
LIVE_ROOT = Path('/var/lib/research-system/handover-broker/live-setup-04d67a00422e-f1574ec4f903')
FIXTURE_LINK = Path('/opt/research-system/handover')
UNIT_ROOT = Path('/etc/systemd/system')
SOCKET = Path('/run/research-system/handover-live.sock')
UNITS = ('research-system-handover-live.service', 'research-system-handover-live.socket')
INPUTS = ('install_live_handover.py', *UNITS)
CANARY_FILES = ('execution-intent.json', 'execution-receipt.json', 'direct-request-refusals.json',
                'initial-state.json', 'final-state.json',
                *(name+'.'+kind+'.json' for name in ('initialize','admit','duplicate','status')
                  for kind in ('intent','result','receipt')))
LEDGER_PIN = '2a32e9548ee4f82712ff010b888a8784cb78d178'
INITIAL_PIN = '10a0d437e86de3ed1d0d80346b186f2857fb5765'
POLICY_SHA = 'f1574ec4f9031f05cfe7b9279ca26114821678ed665b115b19a9dca3ac72bcdd'
EVENT = '93f735fa1b1a211b858f82c3dfd870def1d78c8b47b1f80e659a81367c2d0d35'
REMOTE = 'https://github.com/Moroseui/concept-research-scout.git'
REF = 'refs/heads/automation/dispatch-state'
ENV = {'PATH':'/usr/bin:/bin', 'LANG':'C.UTF-8', 'GIT_CONFIG_GLOBAL':'/dev/null',
       'GIT_CONFIG_NOSYSTEM':'1', 'GIT_TERMINAL_PROMPT':'0', 'GIT_OPTIONAL_LOCKS':'0',
       'GIT_HTTP_LOW_SPEED_LIMIT':'1', 'GIT_HTTP_LOW_SPEED_TIME':'30', 'PYTHONDONTWRITEBYTECODE':'1'}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def seal(info):
    return (info.st_dev, info.st_ino, info.st_uid, info.st_gid, info.st_mode,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def protected(path, *, private=False, directory=False):
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'ABSOLUTE_PROTECTED_PATH_REQUIRED')
    info = path.lstat()
    require((stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode))
            and info.st_uid == 0 and not info.st_mode & (0o077 if private else 0o022),
            'ROOT_PROTECTED_PATH_REQUIRED')
    for parent in path.parents:
        item = parent.lstat()
        require(stat.S_ISDIR(item.st_mode) and item.st_uid == 0 and not item.st_mode & 0o022,
                'ROOT_PROTECTED_ANCESTOR_REQUIRED')
    return seal(info)


def read(path, *, private=True, maximum=200000):
    before = protected(path, private=private)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        require(seal(os.fstat(stream.fileno())) == before and before[5] <= maximum,
                'PROTECTED_INPUT_CHANGED_OR_OVERSIZED')
        raw = stream.read(maximum+1)
        require(len(raw) <= maximum and seal(os.fstat(stream.fileno())) == before,
                'PROTECTED_INPUT_CHANGED_OR_OVERSIZED')
    return raw


def immutable(path, raw, mode=0o600):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, 'wb') as stream:
        os.fchmod(stream.fileno(), mode)
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def command(args, *, accepted=(0,)):
    result = subprocess.run(args, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=60, check=False)
    require(result.returncode in accepted and len(result.stdout) <= 200000,
            'BOUNDED_ADMIN_OBSERVATION_FAILED')
    return result.stdout


def manifest_check(manifest, inputs, originals):
    require(set(manifest) == {'reviewed_source','source_review_sha256','input_sha256','canary_sha256'}
            and re.fullmatch('[0-9a-f]{40}', manifest['reviewed_source']) is not None
            and re.fullmatch('[0-9a-f]{64}', manifest['source_review_sha256']) is not None,
            'EXACT_SOURCE_REVIEW_MANIFEST_REQUIRED')
    for field, values, expected in [('input_sha256', inputs, set(INPUTS)),
                                     ('canary_sha256', originals, set(CANARY_FILES))]:
        require(set(manifest[field]) == set(values) == expected
                and all(digest(raw) == manifest[field][name] for name,raw in values.items()),
                'REVIEWED_BYTES_CHANGED')


def canary_check(originals):
    values = {name: json.loads(raw) for name,raw in originals.items()}
    receipt = values['execution-receipt.json']
    require(receipt['status'] == 'MODEL_DISABLED_DIRECT_BROKER_LIVE_CANARY_COMPLETE_PERSISTENT_INSTALLATION_PENDING'
            and receipt['source'] == SOURCE and receipt['initial_state_pin'] == INITIAL_PIN
            and receipt['final_state_pin'] == LEDGER_PIN and receipt['policy_sha256'] == POLICY_SHA
            and receipt['fixed_event'] == {'turn_id':EVENT,'attempt':'1','source':SOURCE,
                'branch':'astra/infrastructure-milestone-record','kind':'astra_turn'}
            and receipt['live_count_added'] == receipt['final_live_count'] == 1
            and receipt['duplicate_added_count'] == receipt['models_called'] == 0
            and receipt['fixture_state_untouched'] is True
            and all(receipt[name] is False for name in ('services_changed','active_configurations_changed',
                'source_links_changed','reset_executed','code_publication_executed','unattended_activated')),
            'COMPLETED_EXACT_CANARY_REQUIRED')
    for name in ('initialize','admit','duplicate','status'):
        row = values[name+'.receipt.json']
        returned = values[name+'.result.json']
        require(row['returned_result_sha256'] == digest(originals[name+'.result.json'])
                and row['result'] == returned['result']
                and returned['source'] == SOURCE and returned['operation'] == name
                and returned['policy_sha256'] == POLICY_SHA and returned['event'] == receipt['fixed_event']
                and returned['expected_ledger_pin'] == {'initialize':None,'admit':INITIAL_PIN,
                    'duplicate':LEDGER_PIN,'status':LEDGER_PIN}[name]
                and row['ledger_pin_after'] == (INITIAL_PIN if name == 'initialize' else LEDGER_PIN),
                'ORIGINAL_CANARY_RETURN_CHANGED')
    final = values['final-state.json']
    state = final['state']
    require(final['pin'] == LEDGER_PIN and state['policy_sha256'] == POLICY_SHA
            and type(state['count']) is int and state['count'] == 1
            and type(state['sequence']) is int and state['sequence'] == 1
            and state['halted'] is False and state['resets'] == [] and state['notifications'] == {}
            and state['events'] == {'server:'+EVENT+':1':{'source':SOURCE,
                'branch':'astra/infrastructure-milestone-record','kind':'astra_turn',
                'day':state['day'],'count':1,'notification':None,'halted':False}},
            'EXACT_RETAINED_CANARY_STATE_REQUIRED')
    return final


def source_check():
    protected(SOURCE_ROOT.parent, private=True, directory=True)
    # The root-private Git closure and executable imports must all stay protected.
    for path in [SOURCE_ROOT, *SOURCE_ROOT.rglob('*')]:
        protected(path, directory=path.is_dir())
    require(command(['git','-C',str(SOURCE_ROOT),'rev-parse','HEAD']).decode().strip() == SOURCE
            and not command(['git','-C',str(SOURCE_ROOT),'status','--porcelain']).strip(),
            'INSTALLED_SOURCE_CHANGED')
    sys.path.insert(0, str(SOURCE_ROOT))
    path = SOURCE_ROOT/'deploy/research-system/prepare_live_handover_setup.py'
    spec = importlib.util.spec_from_file_location('reviewed_live_preparation', path)
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    return helper


def configuration_check(helper):
    preparation = json.loads(read(PREPARATION/'receipt.json'))
    require(preparation['status'] == 'LIVE_HANDOVER_SETUP_PREPARED_NOT_INSTALLED'
            and preparation['source'] == SOURCE and preparation['policy_sha256'] == POLICY_SHA,
            'EXACT_ROOT_PREPARATION_REQUIRED')
    for name, sha in preparation['artifact_sha256'].items():
        require(re.fullmatch('[A-Za-z0-9._-]+',name) is not None
                and digest(read(PREPARATION/name)) == sha, 'ROOT_PREPARATION_CHANGED')
    broker_raw = read(Path('/etc/research-system/handover-broker.json'))
    runtime_raw = read(Path('/etc/research-system/handover-controller.json'), private=False)
    writer_path = SETUP/'writer-config.proposed.json'
    writer_raw = read(writer_path)
    require(broker_raw == read(PREPARATION/'broker.original.bytes')
            and runtime_raw == read(PREPARATION/'runtime.original.bytes')
            and digest(writer_raw) == preparation['protected_input_sha256']['writer'],
            'EXISTING_SCIENCE_OR_WRITER_CONFIGURATION_CHANGED')
    writer = json.loads(writer_raw)
    proposed, plan = helper.plan(SOURCE, read(SOURCE_ROOT/helper.APPROVAL, private=False),
        json.loads(read(SOURCE_ROOT/helper.POLICY_FILE, private=False)),
        json.loads(read(SOURCE_ROOT/helper.IDENTITY_FILE, private=False)), writer,
        json.loads(broker_raw), json.loads(runtime_raw), PREPARATION, writer_path)
    proposed_raw = read(PREPARATION/'broker.proposed.json')
    require(json.loads(proposed_raw) == proposed and proposed['controller_uid'] == 997
            and proposed['mode'] == 'LIVE_APPROVED' and proposed['model_mode'] == 'DISABLED'
            and proposed['max_model_turns'] == 0 and proposed['sources'] == [SOURCE]
            and plan['state_root'] == str(LIVE_ROOT), 'EXACT_MODEL_DISABLED_CONFIGURATION_REQUIRED')
    for row in plan['directories']:
        protected(Path(row['path']), private=True, directory=True)
    # Key contents are never opened; the service keeps the existing credential boundary.
    key_seal = protected(Path(writer['private_key']), private=True)
    require(FIXTURE_LINK.is_symlink() and FIXTURE_LINK.resolve(strict=True) ==
            Path(json.loads(runtime_raw)['source_root']), 'EXISTING_FIXTURE_LINK_REQUIRED')
    fixture = (os.readlink(FIXTURE_LINK), seal(FIXTURE_LINK.lstat()))
    return {'broker_sha256':digest(broker_raw),'runtime_sha256':digest(runtime_raw),
            'writer_sha256':digest(writer_raw),'prepared_broker_sha256':digest(proposed_raw),
            'key_metadata':key_seal,'fixture_link':fixture}


def ledger_check(final):
    ledger = LIVE_ROOT/'ledger'
    require(command(['git','-C',str(ledger),'remote','get-url','origin']).decode().strip() == REMOTE,
            'LIVE_LEDGER_REMOTE_CHANGED')
    # Anonymous public observation, with all inherited authentication excluded.
    observed = command(['git','-c','credential.helper=','ls-remote',REMOTE,REF]).decode().split()
    require(observed == [LEDGER_PIN,REF], 'LIVE_LEDGER_MOVED_RECONCILE')
    entries = command(['git','-C',str(ledger),'ls-tree',LEDGER_PIN]).decode().splitlines()
    require(len(entries) == 1 and entries[0].split()[0:2] == ['100644','blob']
            and entries[0].split()[-1] == 'dispatch_state.json', 'LIVE_LEDGER_TREE_CHANGED')
    state = json.loads(command(['git','-C',str(ledger),'show',LEDGER_PIN+':dispatch_state.json']))
    require(state == final['state'], 'LIVE_LEDGER_STATE_CHANGED')


def unit_state(name):
    raw = command(['systemctl','show',name,'--property=LoadState,ActiveState,UnitFileState'], accepted=(0,4))
    fields = dict(line.split('=',1) for line in raw.decode().splitlines())
    require(set(fields) == {'LoadState','ActiveState','UnitFileState'}, 'UNIT_STATE_UNAVAILABLE')
    return fields


def targets_absent():
    for path in [*(UNIT_ROOT/name for name in UNITS), *(UNIT_ROOT/(name+'.d') for name in UNITS), SOCKET]:
        require(not path.exists() and not path.is_symlink(), 'EXISTING_LIVE_INSTALLATION_RECONCILE')
    for name in UNITS:
        state = unit_state(name)
        require(state['LoadState'] == 'not-found' and state['ActiveState'] == 'inactive'
                and state['UnitFileState'] in ('','not-found'), 'EXISTING_LIVE_UNIT_RECONCILE')


def install():
    require(os.getuid() == 0 and sys.dont_write_bytecode, 'SETUP_ADMIN_PYTHON_B_REQUIRED')
    require(Path(__file__).resolve() == STAGING/'install_live_handover.py', 'EXACT_INSTALLER_STAGING_REQUIRED')
    os.umask(0o077)
    protected(STAGING, private=True, directory=True); protected(UNIT_ROOT, directory=True)
    fd = os.open(STAGING, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('CONCURRENT_INSTALL_RECONCILE') from None
        for name in ('install-intent.json','install-receipt.json','install-failure.json'):
            require(not (STAGING/name).exists() and not (STAGING/name).is_symlink(),
                    'EXISTING_PARTIAL_INSTALL_RECONCILE')
        manifest_raw = read(STAGING/'review-manifest.json')
        manifest = json.loads(manifest_raw)
        inputs = {name:read(STAGING/name) for name in INPUTS}
        originals = {name:read(CANARY/name) for name in CANARY_FILES}
        manifest_check(manifest,inputs,originals)
        final = canary_check(originals)
        helper = source_check()
        before = configuration_check(helper)
        require(pwd.getpwnam('research-controller').pw_uid == 997 and grp.getgrnam('research-runtime').gr_gid > 0,
                'EXISTING_CONTROLLER_ROLE_CHANGED')
        targets_absent(); ledger_check(final)
        command(['systemd-analyze','verify',*(str(STAGING/name) for name in UNITS)])
        immutable(STAGING/'install-intent.json',encoded({'status':'INSTALLING_DISABLED_LIVE_SOCKET',
            'review_manifest_sha256':digest(manifest_raw),'source':SOURCE,'ledger_pin':LEDGER_PIN,
            'preserved_configuration':before,'models_allowed':0,'initialize_allowed':False}))
        try:
            source_check()
            require(configuration_check(helper) == before, 'CONFIGURATION_CHANGED_BEFORE_INSTALL')
            for name in UNITS:
                immutable(UNIT_ROOT/name,inputs[name],mode=0o644)
            command(['systemctl','daemon-reload'])
            for name in UNITS:
                require(read(UNIT_ROOT/name, private=False) == inputs[name], 'INSTALLED_UNIT_CHANGED')
                state = unit_state(name)
                require(state['LoadState'] == 'loaded' and state['ActiveState'] == 'inactive'
                        and state['UnitFileState'] in ('disabled','static'), 'LIVE_UNIT_UNEXPECTEDLY_ACTIVE')
            require(not SOCKET.exists() and not SOCKET.is_symlink(), 'LIVE_SOCKET_UNEXPECTEDLY_CREATED')
            source_check()
            require(configuration_check(helper) == before, 'EXISTING_CONFIGURATION_CHANGED_DURING_INSTALL')
            ledger_check(final)
            receipt = {'status':'LIVE_BROKER_SOCKET_INSTALLED_STOPPED_DISABLED',
                'source':SOURCE,'reviewed_installer_source':manifest['reviewed_source'],
                'review_manifest_sha256':digest(manifest_raw),'unit_sha256':{n:digest(inputs[n]) for n in UNITS},
                'canary_final_ledger_pin':LEDGER_PIN,'fixture_configuration_and_link_unchanged':True,
                'fixture_consumed_turns_modified':False,'model_mode':'DISABLED','max_model_turns':0,
                'services_started':False,'socket_enabled':False,'timer_enabled':False,
                'models_called':0,'tokens_minted':0,'key_contents_read':False,
                'remote_refs_written':0,'ledger_initialized':False,'unattended_activated':False}
            immutable(STAGING/'install-receipt.json',encoded(receipt))
            return receipt
        except BaseException as error:
            immutable(STAGING/'install-failure.json',encoded({'status':'PARTIAL_INSTALL_PRESERVED_RECONCILE',
                'error_type':type(error).__name__,'automatic_retry':False,'models_allowed':0}))
            raise
    finally:
        os.close(fd)


if __name__ == '__main__':
    try:
        print(json.dumps(install()))
    except Exception as error:
        reason = str(error)
        if not re.fullmatch('[A-Z][A-Z0-9_]{1,100}',reason):
            reason = 'INSTALL_FAILED_PRESERVE_PARTIAL_FILES_AND_RECONCILE'
        print(json.dumps({'status':'REFUSED_OR_PARTIAL_INSTALL_RECONCILE','reason':reason}),file=sys.stderr)
        raise SystemExit(2) from None
