"""Fixed reviewed continuing upgrade and explicit restoration; starts no research.

Only root may execute this source from the inspected fixed staging snapshot.
The broker/socket restart is separate from worker/timer activation. An interrupted
upgrade never retries automatically or acquires a fabricated completion receipt.
"""
import argparse
from contextlib import ExitStack
import fcntl
import io
import json
import os
from pathlib import Path
import re
import shlex
import sqlite3
import stat
import subprocess
import sys
import tarfile

from orchestrator import deployment_review as gate
from orchestrator.remote_supervisor import checked_source

BASE = gate.BASE
CONTROLLER = Path('/var/lib/research-system/handover-live-controller')
CONFIG = Path('/etc/research-system/live-research')
REGISTRATION_LOCK = CONFIG/'research-catalog-registration.lock'
JOBS = Path('/var/lib/research-system/scientific-jobs')
UNITS = Path('/etc/systemd/system')
BROKER = 'research-system-handover-live.service'
SOCKET = 'research-system-handover-live.socket'
TEMPLATE = 'research-system-scientific-job@.service'
HELD = ('research-system-live-research.service', 'research-system-live-research.timer',
        'research-system-issue-intake.service', 'research-system-issue-intake.timer',
        'research-system-scientific-completion.service', 'research-system-scientific-completion.timer')
UNIT_NAMES = (BROKER, SOCKET, TEMPLATE, *HELD)
UNIT_FIELDS = ('LoadState','ActiveState','SubState','UnitFileState','FragmentPath','DropInPaths',
               'ExecStart','ExecStartPre','ExecStartPost','ExecStop','ExecStopPost','ExecCondition','WorkingDirectory',
               'User','Group','EnvironmentFiles','MainPID','ControlGroup')
DIRECTORIES = {str(JOBS): (0,987,0o750),
    **{str(JOBS/name):(0,987,0o750) for name in ('requests','outputs','snapshots','inputs')},
    str(CONTROLLER/'scientific-versions'):(997,987,0o700),
    str(CONTROLLER/'scientific-observation'):(0,987,0o750),
    '/var/lib/research-system/issue-intake':(0,0,0o700),
    str(CONFIG/'controls/issue-intake-attestations'):(0,987,0o750)}
PRESERVED_BROKER = ('repository','branch','controller_uid','operator_uids','ledger_repo',
    'publication_root','turn_root','writer_config','policy','notification_config')
PRESERVED_CONTROLLER = ('state','controller_uid','controller_gid','broker_socket','change_request_store',
    'control_inbox','publication','research_catalog','research_request')


def command(argv, *, cwd=None):
    result = subprocess.run(argv, cwd=cwd, env={'PATH':'/usr/sbin:/usr/bin:/bin', 'LANG':'C.UTF-8',
        'PYTHONDONTWRITEBYTECODE':'1','GIT_OPTIONAL_LOCKS':'0','GIT_NO_LAZY_FETCH':'1',
        'GIT_TERMINAL_PROMPT':'0','GIT_ALLOW_PROTOCOL':''}, capture_output=True, timeout=30)
    gate.require(result.returncode == 0, 'DEPLOYMENT_FIXED_COMMAND_FAILED')
    return result.stdout


# systemd255 may omit these empty arrays from systemctl show, even with --all.
# No missing service identity or execution entry point receives a default.
EMPTY_SERVICE_ARRAYS = {**{key: '(sasbttttuii)' for key in
    ('ExecStartPre','ExecStartPost','ExecStop','ExecStopPost','ExecCondition')},
    'EnvironmentFiles': '(sb)'}


def unit_fields(name):
    gate.require(name in UNIT_NAMES and name != TEMPLATE, 'DEPLOYMENT_FIXED_UNIT_REQUIRED')
    raw = command(['/usr/bin/systemctl','show',name,'--property='+','.join(UNIT_FIELDS)])
    return dict(line.split('=',1) for line in raw.decode().splitlines() if '=' in line)


def verify_empty_service_arrays(name, properties, observed):
    gate.require(name in UNIT_NAMES and name.endswith('.service') and name != TEMPLATE
        and properties and set(properties) <= set(EMPTY_SERVICE_ARRAYS),
        'DEPLOYMENT_KNOWN_EMPTY_SERVICE_ARRAY_REQUIRED')
    try:
        import dbus  # Existing OS package; only this administrative observer needs it.
    except ImportError as error:
        raise ValueError('DEPLOYMENT_DBUS_BINDING_REQUIRED') from error
    object_path = '/org/freedesktop/systemd1/unit/' + ''.join(
        char if char.isascii() and char.isalnum() else '_'+format(ord(char),'02x') for char in name)
    try:
        bus = dbus.SystemBus(private=True)
    except dbus.DBusException as error:
        raise ValueError('DEPLOYMENT_DBUS_OBSERVATION_FAILED') from error
    referenced = False
    try:
        manager = dbus.Interface(bus.get_object('org.freedesktop.systemd1',
            '/org/freedesktop/systemd1', introspect=False), 'org.freedesktop.systemd1.Manager')
        # RefUnit loads metadata and pins it to this connection, but enqueues no
        # service job. Keep it held while systemctl and typed reads inspect it.
        manager.RefUnit(name, timeout=10); referenced = True
        gate.require(str(manager.GetUnit(name, timeout=10)) == object_path,
                     'DEPLOYMENT_SERVICE_OBJECT_UNVERIFIED')
        gate.require(unit_fields(name) == observed, 'DEPLOYMENT_SERVICE_OBSERVATION_CHANGED')
        reader = dbus.Interface(bus.get_object('org.freedesktop.systemd1',object_path,
            introspect=False), 'org.freedesktop.DBus.Properties')
        for key in sorted(properties):
            value = reader.Get('org.freedesktop.systemd1.Service',key,timeout=10)
            gate.require(isinstance(value,dbus.Array) and str(value.signature)==EMPTY_SERVICE_ARRAYS[key]
                         and len(value)==0, 'DEPLOYMENT_EMPTY_SERVICE_ARRAY_UNVERIFIED')
    except dbus.DBusException as error:
        raise ValueError('DEPLOYMENT_DBUS_OBSERVATION_FAILED') from error
    finally:
        try:
            if referenced:
                try: manager.UnrefUnit(name, timeout=10)
                except dbus.DBusException as error:
                    raise ValueError('DEPLOYMENT_UNIT_REFERENCE_RELEASE_FAILED') from error
        finally:
            bus.close()  # Also releases any reference whose reply was interrupted.


def unit_state(name):
    gate.require(name in UNIT_NAMES and name != TEMPLATE, 'DEPLOYMENT_FIXED_UNIT_REQUIRED')
    fields = unit_fields(name)
    common={'LoadState','ActiveState','SubState','UnitFileState','FragmentPath','DropInPaths'}
    gate.require(common <= set(fields), 'DEPLOYMENT_UNIT_OBSERVATION_REQUIRED')
    if name.endswith('.service') and fields['LoadState']=='loaded':
        missing = set(UNIT_FIELDS)-set(fields)
        gate.require(missing <= set(EMPTY_SERVICE_ARRAYS), 'DEPLOYMENT_SERVICE_OBSERVATION_REQUIRED')
        if missing:
            verify_empty_service_arrays(name, missing, fields)
            fields.update({key: '' for key in missing})
    # Socket/timer interfaces do not have service execution or process properties.
    result={k:fields.get(k,'0' if k=='MainPID' else '') for k in UNIT_FIELDS}
    return result


def units_observation():
    result = {name:unit_state(name) for name in UNIT_NAMES if name != TEMPLATE}
    for name in UNIT_NAMES:
        for base in (Path('/etc/systemd/system'),Path('/run/systemd/system'),Path('/usr/lib/systemd/system')):
            gate.require(not (base/(name+'.d')).exists() and not (base/(name+'.d')).is_symlink(),
                         'DEPLOYMENT_UNREVIEWED_UNIT_DROPIN')
    for name, value in result.items():
        gate.require(not value['DropInPaths'] and not value['EnvironmentFiles']
            and not any(value[k] for k in ('ExecStartPre','ExecStartPost','ExecStop','ExecStopPost','ExecCondition')),
            'DEPLOYMENT_UNREVIEWED_UNIT_OVERRIDE')
        gate.require(value['LoadState']=='not-found' or value['FragmentPath']==str(UNITS/name),
                     'DEPLOYMENT_UNEXPECTED_UNIT_FRAGMENT')
    return result


def quiescent(units, broker, blocked, *, running=True):
    for name in HELD:
        value=units[name]
        gate.require(value['ActiveState']=='inactive' and value['MainPID']=='0'
            and value['UnitFileState'] in ('','disabled','static','not-found'),
            'DEPLOYMENT_RESEARCH_OR_TIMER_ACTIVE')
    scientific = json.loads(command(['/usr/bin/systemctl','list-units',
        'research-system-scientific-job@*.service','--all','--output=json','--no-pager']))
    gate.require(all(row.get('active')=='inactive' for row in scientific),
                 'DEPLOYMENT_SCIENTIFIC_JOB_ACTIVE')
    if running:
        live=units[BROKER]
        gate.require(live['ActiveState']=='active' and live['SubState']=='running'
                     and re.fullmatch('[1-9][0-9]*',live['MainPID']), 'DEPLOYMENT_IDLE_BROKER_REQUIRED')
        group=Path(live['ControlGroup'])
        gate.require(group.is_absolute() and '..' not in group.parts, 'DEPLOYMENT_BROKER_CGROUP_REQUIRED')
        pids=(Path('/sys/fs/cgroup')/str(group).lstrip('/')/'cgroup.procs').read_text().split()
        gate.require(pids==[live['MainPID']], 'DEPLOYMENT_BROKER_CHILD_WORK_ACTIVE')
    else:
        live=units[BROKER]
        gate.require(live['ActiveState'] in ('inactive','failed') and live['MainPID']=='0',
                     'DEPLOYMENT_BROKER_NOT_IDLE')
        if live['ControlGroup']:
            group=Path(live['ControlGroup'])
            gate.require(group.is_absolute() and '..' not in group.parts, 'DEPLOYMENT_BROKER_CGROUP_REQUIRED')
            processes=Path('/sys/fs/cgroup')/str(group).lstrip('/')/'cgroup.procs'
            gate.require(not processes.exists() or not processes.read_text().strip(),
                         'DEPLOYMENT_BROKER_CHILD_WORK_ACTIVE')
    with sqlite3.connect((CONTROLLER/'coordinator.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        control=db.execute('SELECT revision,paused FROM controls').fetchone()
        gate.require(control is not None and control[1]==1, 'DEPLOYMENT_RECORDED_PAUSE_REQUIRED')
        rows=db.execute("SELECT id,binding,status,reason FROM tasks WHERE status != 'COMPLETE'").fetchall()
        gate.require(all(row[2]=='BLOCKED' for row in rows), 'DEPLOYMENT_COORDINATOR_WORK_PENDING')
        actual={row[0]:{'reason':row[3],'binding_sha256':gate.digest(row[1].encode())} for row in rows}
        gate.require(actual==blocked, 'DEPLOYMENT_UNREVIEWED_BLOCKED_TASK')
    if (JOBS/'jobs.sqlite').exists():
        with sqlite3.connect((JOBS/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as db:
            tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            # Existing scientific state is preserved; never guess another schema.
            gate.require('jobs' in tables, 'DEPLOYMENT_SCIENTIFIC_DATABASE_RECONCILE')
            gate.require(db.execute("SELECT count(*) FROM jobs WHERE status NOT IN ('COMPLETE','FAILED')").fetchone()[0]==0,
                         'DEPLOYMENT_SCIENTIFIC_WORK_PENDING')
    return {'revision':control[0],'paused':True}


def state_inventory(broker):
    """Original full preserved-file inventory; no ledger exclusion here."""
    roots=[CONTROLLER, Path(broker['turn_root']).parent]
    if JOBS.exists(): roots.append(JOBS)
    result={}
    for root in roots:
        gate.require(root.is_dir() and not root.is_symlink(), 'DEPLOYMENT_STATE_ROOT_REQUIRED')
        for path in sorted(root.rglob('*')):
            info=path.lstat()
            gate.require(not stat.S_ISLNK(info.st_mode), 'DEPLOYMENT_STATE_SYMLINK_RECONCILE')
            if stat.S_ISDIR(info.st_mode): continue
            gate.require(stat.S_ISREG(info.st_mode), 'DEPLOYMENT_STATE_FILE_RECONCILE')
            if path.name.endswith(('.lock','-wal','-shm')): continue
            metadata={'uid':info.st_uid,'gid':info.st_gid,'mode':stat.S_IMODE(info.st_mode),'inode':info.st_ino}
            if path.suffix=='.sqlite':
                import hashlib
                value=hashlib.sha256()
                with sqlite3.connect(path.as_uri()+'?mode=ro',uri=True) as db:
                    for line in db.iterdump(): value.update(line.encode()+b'\n')
                metadata['logical_sha256']=value.hexdigest()
            else:
                gate.require(info.st_size<=50000000, 'DEPLOYMENT_PRESERVED_FILE_LIMIT')
                metadata['sha256']=gate.digest(path.read_bytes())
            result[str(path)]=metadata
    return result


def inventory_fingerprint(result):
    return {'sha256':gate.digest(gate.encoded(result)),'files':len(result)}


def state_fingerprint(broker):
    return inventory_fingerprint(state_inventory(broker))



RECOVERY_KEYS = {'schema','instructions','directories','units_before','previous_active',
                 'preserved_state_sha256','preserved_blocked_tasks'}
DIRECT_RECOVERY = 'reviewed-deployment-recovery/direct-inspection-v1'
TERMINAL_RECOVERY = 'reviewed-deployment-recovery/operator-terminal-v1'


def _ledger_path(broker):
    repo = Path(broker['ledger_repo'])
    parent = Path(broker['turn_root']).parent
    gate.require(repo.is_absolute() and '..' not in repo.parts and repo == parent/'ledger',
                 'DEPLOYMENT_FIXED_LEDGER_PATH_REQUIRED')
    return repo


def _non_ledger(files, broker):
    repo = _ledger_path(broker)
    return {name: value for name, value in files.items() if not Path(name).is_relative_to(repo)}


def validate_recovery(recovery, proposal):
    """Keep strict recovery and explicit native/terminal ledger-only variants."""
    direct = recovery.get('schema') == DIRECT_RECOVERY
    terminal = recovery.get('schema') == TERMINAL_RECOVERY
    if proposal.get('review_profile') in ('operator-terminal-review/v1', 'server-terminal-review/v1'):
        gate.require(recovery.get('schema') in ('reviewed-deployment-recovery/v1', TERMINAL_RECOVERY),
                     'DEPLOYMENT_TERMINAL_STRICT_RECOVERY_REQUIRED')
    if terminal:
        gate.require(proposal.get('review_profile') in ('operator-terminal-review/v1', 'server-terminal-review/v1')
                     and 'review_plan_sha256' not in proposal,
                     'DEPLOYMENT_TERMINAL_RECOVERY_PROFILE_REQUIRED')
    extension = {'inspection_admissions'} if direct else ({'terminal_admissions'} if terminal else set())
    gate.require(set(recovery) == RECOVERY_KEYS | extension
        and (direct or terminal or recovery['schema'] == 'reviewed-deployment-recovery/v1')
        and isinstance(recovery['instructions'], str), 'DEPLOYMENT_REVIEWED_RECOVERY_PLAN_REQUIRED')
    gate.pin(recovery['preserved_state_sha256'])
    gate.require(isinstance(recovery['preserved_blocked_tasks'], dict), 'DEPLOYMENT_PRESERVED_BLOCKS_REQUIRED')
    for task, item in recovery['preserved_blocked_tasks'].items():
        gate.pin(task)
        gate.require(set(item) == {'reason','binding_sha256'}, 'DEPLOYMENT_PRESERVED_BLOCKS_REQUIRED')
        gate.pin(item['binding_sha256'])
    if not (direct or terminal):
        return
    from orchestrator import inspection_admission_recovery as ledger
    if terminal:
        value = recovery['terminal_admissions']
        gate.require(isinstance(value, dict) and set(value) in ({
            'ledger','policy_sha256','non_ledger_files','control_snapshot'}, {
            'ledger','policy_sha256','non_ledger_files','control_snapshot','preserved_admissions'}),
            'DEPLOYMENT_TERMINAL_BASELINE_REQUIRED')
        gate.pin(value['policy_sha256'])
        preserved_admission_cases(value.get('preserved_admissions', []),
            server_profile=proposal.get('review_profile') == 'server-terminal-review/v1')
    else:
        gate.require(proposal.get('review_profile') == 'direct-inspection/v1'
                     and 'review_plan_sha256' not in proposal, 'DEPLOYMENT_DIRECT_RECOVERY_PROFILE_REQUIRED')
        value = recovery['inspection_admissions']
        gate.require(isinstance(value, dict) and set(value) == {'schema','ledger','policy_sha256',
            'canary_proof_sha256','non_ledger_files','control_snapshot'}
            and value['schema'] == 'reviewed-inspection-baseline/v1', 'DEPLOYMENT_INSPECTION_BASELINE_REQUIRED')
        for key in ('policy_sha256','canary_proof_sha256'): gate.pin(value[key])
    gate.require(isinstance(value['non_ledger_files'], dict) and value['non_ledger_files']
                 and isinstance(value['control_snapshot'], dict)
                 and value['control_snapshot'].get('paused') in (True, 1),
                 'DEPLOYMENT_INSPECTION_PRESERVED_BASELINE_REQUIRED')
    for name, row in value['non_ledger_files'].items():
        gate.require(isinstance(name, str) and Path(name).is_absolute() and '..' not in Path(name).parts
            and isinstance(row, dict) and set(row) in ({'uid','gid','mode','inode','sha256'},
                {'uid','gid','mode','inode','logical_sha256'}), 'DEPLOYMENT_INSPECTION_FILE_BASELINE_REQUIRED')
        for key in ('uid','gid','mode','inode'):
            gate.require(type(row[key]) is int and row[key] >= 0, 'DEPLOYMENT_INSPECTION_FILE_METADATA_REQUIRED')
        gate.pin(row.get('sha256', row.get('logical_sha256')))
    ledger.validate_baseline(value['ledger'])
    gate.require(value['ledger']['policy_sha256'] == value['policy_sha256'],
                 'DEPLOYMENT_INSPECTION_POLICY_CHANGED')
    snapshot = value['ledger']['snapshot']; repo = Path(snapshot['repository'])
    full = dict(value['non_ledger_files'])
    gate.require(not any(Path(name).is_relative_to(repo) for name in full),
                 'DEPLOYMENT_INSPECTION_LEDGER_OVERLAP')
    for name, row in snapshot['files'].items():
        path = repo/name
        if path.name.endswith(('.lock','-wal','-shm')): continue
        gate.require(path.suffix != '.sqlite', 'DEPLOYMENT_INSPECTION_UNKNOWN_LEDGER_DATABASE')
        full[str(path)] = {key:row[key] for key in ('uid','gid','mode','inode','sha256')}
    gate.require(inventory_fingerprint(full)['sha256'] == recovery['preserved_state_sha256'],
                 'DEPLOYMENT_ORIGINAL_FULL_BASELINE_CHANGED')


def authenticated_ledger_status(broker):
    """Existing UID997 status request may fetch; always precedes final inventory."""
    controller = json.loads(gate.read(CONFIG/'controller.json'))
    actual = json.loads(gate.read(CONFIG/'broker.json'))
    gate.require(all(actual.get(key) == broker.get(key) for key in PRESERVED_BROKER)
        and controller['state'] == str(CONTROLLER) and controller['controller_uid'] == 997
        and controller['controller_gid'] == 987 and controller['source'] in actual['sources'],
        'DEPLOYMENT_INSPECTION_BROKER_BOUNDARY_CHANGED')
    checked_source(controller['source_root'], controller['source'])
    script = ('import json,sys; from orchestrator.handover_runtime import request_broker; '
              'print(json.dumps(request_broker(sys.argv[1],"status",{})))')
    # A reviewed successor may be installing over the earlier object-group
    # producer. Its authenticated fetch can atomically replace bookkeeping even
    # without an admission. Preserve those existing owners at this caller too;
    # do not repair preexisting drift or skip the subsequent native inventory.
    from orchestrator.dispatch_limiter import GitLedger
    protected_ledger = GitLedger(_ledger_path(broker), protected_owner_group=True)
    protected_ledger._git_credentials()
    bookkeeping = protected_ledger._bookkeeping_before()
    try:
        raw = command(['/usr/sbin/runuser','-u','research-controller','--','env','-i',
            'PATH=/usr/bin:/bin','PYTHONDONTWRITEBYTECODE=1','/usr/bin/python3','-B','-c',script,
            controller['broker_socket']], cwd=controller['source_root'])
    finally:
        protected_ledger._bookkeeping_after(bookkeeping)
    gate.require(len(raw) <= 100000, 'DEPLOYMENT_LEDGER_STATUS_BOUND')
    return json.loads(raw)


def _inspection_control():
    from orchestrator.inspection_runner import current_control
    controller = json.loads(gate.read(CONFIG/'controller.json'))
    gate.require(controller['state'] == str(CONTROLLER) and controller['controller_uid'] == 997
                 and controller['controller_gid'] == 987, 'DEPLOYMENT_INSPECTION_CONTROL_BOUNDARY_CHANGED')
    return current_control(controller)


def capture_inspection_state(broker, canary_directory):
    """Root-only post-canary baseline capture, no admission or research operation.

    Merge these two returned fields into the existing exact recovery observation.
    The two canaries must already be conclusive; the material gate later verifies
    the same originals and their independent bootstrap approval again.
    """
    from orchestrator import inspection_admission_recovery as ledger
    from orchestrator import inspection_runner as runner, inspection_canary as canary
    gate.require(os.getuid() == 0 and sys.dont_write_bytecode, 'DEPLOYMENT_ROOT_PYTHON_B_REQUIRED')
    with ExitStack() as stack:
        for path in (CONTROLLER/'branch.lock', CONTROLLER/'admission.lock'):
            fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW)
            stream = stack.enter_context(os.fdopen(fd, 'r+'))
            try: fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError: raise ValueError('DEPLOYMENT_CONCURRENT_WORK_RECONCILE') from None
        expected, originals = runner.read_canary_proof(canary_directory)
        proof = canary.verify_canary(originals, expected)
        admissions = [{'event_original': originals[phase]['admission_event.json'].decode(),
                       'receipt_original': originals[phase]['admission_receipt.json'].decode()}
                      for phase in ('baseline','hooks')]
        policy = broker['policy']
        gate.require(all(json.loads(originals[phase]['admission_policy.json']) == policy
                         for phase in ('baseline','hooks')), 'DEPLOYMENT_CANARY_POLICY_CHANGED')
        control = _inspection_control()
        gate.require(control.get('paused') in (True, 1), 'DEPLOYMENT_RECORDED_PAUSE_REQUIRED')
        status = authenticated_ledger_status(broker)
        baseline = ledger.capture_ledger(_ledger_path(broker), policy, status, admissions)
        inventory = state_inventory(broker)
        preserved = inventory_fingerprint(inventory)
        gate.require(state_fingerprint(broker) == preserved, 'DEPLOYMENT_BASELINE_CHANGED_DURING_CAPTURE')
        return {'preserved_state_sha256': preserved['sha256'], 'inspection_admissions': {
            'schema':'reviewed-inspection-baseline/v1','ledger':baseline,
            'policy_sha256':gate.digest(gate.encoded(policy)),
            'canary_proof_sha256':gate.digest(gate.encoded(proof)),
            'non_ledger_files':_non_ledger(inventory, broker), 'control_snapshot':control}}


def _inspection_admissions(bundle, proposal):
    """Read only the exact attempts accepted by the unchanged native full gate."""
    proposal_raw = gate.read(bundle/'proposal.json')
    gate.require(json.loads(proposal_raw) == proposal, 'DEPLOYMENT_INSPECTION_PROPOSAL_CHANGED')
    files = gate.archive_inventory(gate.read(bundle/'source.tar.gz', maximum=10000000))
    originals = {name: gate.read(bundle/name, maximum=16000000) for name in gate.ORIGINAL_NAMES}
    review, proof = gate.inspection_review(bundle, proposal_raw, files, originals)
    session = review['inspection_session']
    gate.require(session['status'] == 'APPROVE' and session['source'] == proposal['source'],
                 'DEPLOYMENT_CONCLUSIVE_INSPECTION_REQUIRED')
    index_raw, raw = gate._inspection_inventory(bundle/'inspection')
    gate.require(gate.digest(index_raw) == proof['inspection_index_sha256'],
                 'DEPLOYMENT_INSPECTION_EXPORT_CHANGED_DURING_VERIFY')
    admissions = []
    for number, attempt in enumerate(session['attempts'], 1):
        prefix = 'attempts/'+f'{number:03d}'+'/'
        gate.require(prefix+'timeout.json' not in raw and prefix+'reconciliation.json' not in raw,
                     'DEPLOYMENT_ABANDONED_INSPECTION_REQUIRES_NEW_BASELINE')
        event, receipt = raw[prefix+'admission_event.json'], raw[prefix+'admission_receipt.json']
        gate.require(json.loads(receipt) == attempt['admission'], 'DEPLOYMENT_INSPECTION_ADMISSION_CHANGED')
        admissions.append({'event_original':event.decode(), 'receipt_original':receipt.decode()})
    return proof, admissions, raw['permission-probe.json']


def inspection_preserved_state(bundle, proposal, recovery, broker):
    from orchestrator import inspection_admission_recovery as ledger
    baseline = recovery['inspection_admissions']
    policy = broker['policy']
    ledger.validate_baseline(baseline['ledger'], policy)
    gate.require(baseline['policy_sha256'] == gate.digest(gate.encoded(policy)),
                 'DEPLOYMENT_INSPECTION_POLICY_CHANGED')
    proof, admissions, canary_raw = _inspection_admissions(bundle, proposal)
    gate.require(gate.digest(canary_raw) == baseline['canary_proof_sha256'],
                 'DEPLOYMENT_BASELINE_CANARIES_CHANGED')
    gate.require(_inspection_control() == baseline['control_snapshot'], 'DEPLOYMENT_INSPECTION_CONTROL_CHANGED')
    # This authenticated status can fetch the cache. All helper reads follow it,
    # and all remaining install/restore checks use the complete final inventory.
    status = authenticated_ledger_status(broker)
    transition = ledger.verify_transition(_ledger_path(broker), baseline['ledger'], policy, admissions, status,
        preserved_admissions_count=len(baseline.get('preserved_admissions', [])),
        **({'server_profile': True} if proposal.get('review_profile') == 'server-terminal-review/v1' else {}))
    inventory = state_inventory(broker)
    gate.require(_non_ledger(inventory, broker) == baseline['non_ledger_files'],
                 'DEPLOYMENT_NON_LEDGER_STATE_CHANGED')
    preserved = inventory_fingerprint(inventory)
    gate.require(state_fingerprint(broker) == preserved, 'DEPLOYMENT_STATE_CHANGED_DURING_TRANSITION')
    return preserved, {'schema':'reviewed-inspection-admission-transition/v1',
        'recovery_sha256':proposal['recovery_sha256'],
        'original_preserved_state_sha256':recovery['preserved_state_sha256'],
        'post_review_state':preserved, 'inspection_proof':proof,
        'admissions_sha256':gate.digest(gate.encoded(admissions)),
        'canary_proof_sha256':baseline['canary_proof_sha256'], 'ledger_transition':transition}


def validate_inspection_intent(bundle, proposal, recovery, intent):
    """Restore uses the original post-review snapshot, never a second suffix."""
    baseline = recovery['inspection_admissions']
    value = intent.get('inspection_admission_transition')
    gate.require(isinstance(value, dict) and set(value) == {'schema','recovery_sha256',
        'original_preserved_state_sha256','post_review_state','inspection_proof','admissions_sha256',
        'canary_proof_sha256','ledger_transition'} and value['schema'] == 'reviewed-inspection-admission-transition/v1'
        and value['recovery_sha256'] == proposal['recovery_sha256']
        and value['original_preserved_state_sha256'] == recovery['preserved_state_sha256']
        and value['post_review_state'] == intent['preserved_state']
        and value['canary_proof_sha256'] == baseline['canary_proof_sha256'],
        'DEPLOYMENT_ORIGINAL_ADMISSION_TRANSITION_CHANGED')
    proof, admissions, canary_raw = _inspection_admissions(bundle, proposal)
    gate.require(value['inspection_proof'] == proof and value['admissions_sha256'] == gate.digest(gate.encoded(admissions))
        and gate.digest(canary_raw) == baseline['canary_proof_sha256']
        and value['ledger_transition']['baseline_sha256'] == gate.digest(gate.encoded(baseline['ledger']))
        and value['ledger_transition']['admissions_sha256'] == value['admissions_sha256'],
        'DEPLOYMENT_ORIGINAL_ADMISSION_TRANSITION_CHANGED')



def preserved_admission_cases(values, *, server_profile=False):
    """Exact prior ordinary admissions, pinned in the independently reviewed plan.

    These are not manual review units and never enter terminal_review's billing
    coverage. Their bound event/receipt/state pins must survive full native
    ledger replay; a derived receipt is explicitly labeled and receives no
    original broker-reply or provider-evidence credit; this is preservation, not retrospective scientific authority.
    """
    from orchestrator import inspection_admission_recovery as ledger
    gate.require(type(server_profile) is bool and isinstance(values, list) and len(values) <= ledger.MAX_OBJECTS,
                 'DEPLOYMENT_BOUNDED_PRESERVED_ADMISSIONS_REQUIRED')
    for value in values:
        gate.require(isinstance(value, dict) and set(value) == {'event','receipt','state_after','receipt_origin'}
            and value['receipt_origin'] in ('RECORDED_BROKER_REPLY', 'DERIVED_FROM_AUTHENTICATED_LEDGER'),
                     'DEPLOYMENT_PRIOR_ADMISSION_PROVENANCE_REQUIRED')
        gate.pin(value['state_after'], 40)
    if values:
        checked = ledger._admissions([{'event_original': gate.encoded(v['event']).decode(),
            'receipt_original': gate.encoded(v['receipt']).decode()} for v in values],
            ledger.MAX_OBJECTS, kind='astra_turn',
            preserved_nightly=[{'event_original': gate.encoded(v['event']).decode(),
                'receipt_original': gate.encoded(v['receipt']).decode()} for v in values
                if v['event'].get('kind') == 'nightly_review'])
        gate.require(all(event['attempt'] == '1' or server_profile
            and event['attempt'].isdigit() and 1 <= int(event['attempt']) <= 16 for event, _ in checked),
                     'DEPLOYMENT_ORIGINAL_PRIOR_ADMISSION_REQUIRED')
    return values


def terminal_admission_cases(account, baseline):
    """Order every pinned prior admission and validated manual unit by parents.

    No sorting by count/date (UTC rollover is legitimate), no extra ledger rows,
    and no fabricated manual unit for an already completed research operation.
    """
    preserved = preserved_admission_cases(baseline.get('preserved_admissions', []),
        server_profile=account.get('schema') == 'server-terminal-accounting/v1')
    if not preserved:
        return account['cases']  # Preserve the existing strict manual-only route.
    gate.require(all(case['event'].get('kind') == 'astra_turn' for case in account['cases']),
                 'DEPLOYMENT_TERMINAL_REVIEW_UNIT_KIND_REQUIRED')
    values = [*account['cases'], *preserved]
    from orchestrator import inspection_admission_recovery as ledger
    gate.require(len(values) <= ledger.MAX_OBJECTS,
                 'DEPLOYMENT_BOUNDED_TERMINAL_TRANSITION_REQUIRED')
    gate.require(len({(v['event']['turn_id'],v['event']['attempt']) for v in values}) == len(values)
        and len({v['state_after'] for v in values}) == len(values)
        and len({v['receipt']['state_before'] for v in values}) == len(values),
        'DEPLOYMENT_DUPLICATE_PRESERVED_ADMISSION')
    pending = {v['receipt']['state_before']: v for v in values}
    pin = baseline['ledger']['original_head']; ordered = []
    for _ in values:
        gate.require(pin in pending, 'DEPLOYMENT_PRIOR_ADMISSION_PARENT_GAP')
        value = pending.pop(pin); ordered.append(value); pin = value['state_after']
    gate.require(not pending and pin == account['ledger_pin'],
                 'DEPLOYMENT_PRIOR_ADMISSION_HEAD_CHANGED')
    return ordered


def _terminal_accounting_admissions(bundle, accounting, recovery=None):
    """Serialize values from the already-verified original accounting record."""
    from orchestrator import inspection_admission_recovery as ledger
    raw = gate.read(Path(bundle)/'terminal-accounting.json', maximum=4000000)
    gate.require(gate.digest(raw) == accounting['accounting_sha256'],
                 'DEPLOYMENT_TERMINAL_ACCOUNTING_ORIGINAL_CHANGED')
    value = ledger.parsed(raw)
    gate.require(isinstance(value['cases'], list) and 0 < len(value['cases']) <= ledger.MAX_OBJECTS,
                 'DEPLOYMENT_TERMINAL_ACCOUNTING_CASES_REQUIRED')
    cases = terminal_admission_cases(value, recovery['terminal_admissions']) if recovery else value['cases']
    admissions = [{'event_original': gate.encoded(case['event']).decode(),
                   'receipt_original': gate.encoded(case['receipt']).decode()} for case in cases]
    return value, admissions


def terminal_preserved_state(bundle, proposal, recovery, broker, accounting):
    """Allow only recorded accounting since an already-authenticated old capture."""
    from orchestrator import inspection_admission_recovery as ledger
    baseline = recovery['terminal_admissions']; policy = broker['policy']
    ledger.validate_baseline(baseline['ledger'], policy)
    gate.require(baseline['policy_sha256'] == gate.digest(gate.encoded(policy)),
                 'DEPLOYMENT_INSPECTION_POLICY_CHANGED')
    account, admissions = _terminal_accounting_admissions(bundle, accounting, recovery)
    gate.require(_inspection_control() == baseline['control_snapshot'],
                 'DEPLOYMENT_INSPECTION_CONTROL_CHANGED')
    status = authenticated_ledger_status(broker)
    gate.require(status['pin'] == accounting['ledger_pin'] == account['ledger_pin'],
                 'DEPLOYMENT_TERMINAL_ACCOUNTING_STATE_MOVED')
    transition = ledger.verify_terminal_transition(_ledger_path(broker), baseline['ledger'],
                                                   policy, admissions, status,
        preserved_admissions_count=len(baseline.get('preserved_admissions', [])),
        preserved_nightly_admissions=[{'event_original': gate.encoded(v['event']).decode(),
            'receipt_original': gate.encoded(v['receipt']).decode()}
            for v in baseline.get('preserved_admissions', [])
            if v['event']['kind'] == 'nightly_review'],
        **({'server_profile': True} if proposal.get('review_profile') == 'server-terminal-review/v1' else {}))
    inventory = state_inventory(broker)
    gate.require(_non_ledger(inventory, broker) == baseline['non_ledger_files'],
                 'DEPLOYMENT_NON_LEDGER_STATE_CHANGED')
    preserved = inventory_fingerprint(inventory)
    gate.require(state_fingerprint(broker) == preserved, 'DEPLOYMENT_STATE_CHANGED_DURING_TRANSITION')
    return preserved, {'schema': 'reviewed-terminal-accounting-transition/v1',
        'recovery_sha256': proposal['recovery_sha256'],
        'original_preserved_state_sha256': recovery['preserved_state_sha256'],
        'post_review_state': preserved, 'accounting': accounting,
        'admissions_sha256': gate.digest(gate.encoded(admissions)), 'ledger_transition': transition}


def validate_terminal_intent(bundle, proposal, recovery, intent):
    """Restore binds the original post-accounting snapshot; no fresh status/charge."""
    from orchestrator import terminal_review
    baseline = recovery['terminal_admissions']; value = intent.get('terminal_admission_transition')
    gate.require(isinstance(value, dict) and set(value) == {'schema','recovery_sha256',
        'original_preserved_state_sha256','post_review_state','accounting','admissions_sha256',
        'ledger_transition'} and value['schema'] == 'reviewed-terminal-accounting-transition/v1'
        and value['recovery_sha256'] == proposal['recovery_sha256']
        and value['original_preserved_state_sha256'] == recovery['preserved_state_sha256']
        and value['post_review_state'] == intent['preserved_state']
        and value['accounting'] == intent.get('terminal_accounting'),
        'DEPLOYMENT_ORIGINAL_TERMINAL_TRANSITION_CHANGED')
    account, admissions = _terminal_accounting_admissions(bundle, value['accounting'], recovery)
    proposal_raw = gate.read(Path(bundle)/'proposal.json')
    archive = gate.read(Path(bundle)/'source.tar.gz', maximum=10000000)
    review, _ = terminal_review.load(bundle, proposal_raw, gate.archive_inventory(archive))
    execution = review['execution']
    prepaid = review.get('terminal_profile') == 'server-terminal-review/v1'
    unit_key = 'prepaid_units' if prepaid else 'manual_units'
    gate.require(value['accounting']['late_charge'] is (not prepaid),
                 'DEPLOYMENT_ORIGINAL_ACCOUNTING_ROUTE_CHANGED')
    gate.require(all(account[key] == execution[field] for key, field in {
        'manifest_sha256': 'request_sha256', 'report_sha256': 'response_sha256',
        'journal_sha256': 'protocol_sha256'}.items())
        and sorted(case['unit_sha256'] for case in account['cases'])
            == sorted(review['terminal_session'][unit_key])
        and value['accounting'][unit_key] == sorted(review['terminal_session'][unit_key])
        and value['accounting']['usage_original_sha256'] == execution['protocol_sha256'],
        'DEPLOYMENT_ORIGINAL_TERMINAL_ACCOUNTING_CHANGED')
    proof = value['ledger_transition']
    cases = terminal_admission_cases(account, baseline)
    prior_count = len(baseline.get('preserved_admissions', []))
    expected_status = ('VERIFIED_TERMINAL_AND_PINNED_PRIOR_ADMISSIONS' if prior_count
                       else 'VERIFIED_ONLY_TERMINAL_ACCOUNTING_ADMISSIONS')
    gate.require(proof.get('preserved_admissions_count', 0) == prior_count,
                 'DEPLOYMENT_PRIOR_ADMISSION_COUNT_CHANGED')
    gate.require(proof.get('server_profile', False) is prepaid
        and proof['schema'] == 'terminal-accounting-ledger-transition/v1'
        and proof['status'] == expected_status
        and proof['original_head'] == baseline['ledger']['original_head']
        and proof['current_head'] == account['ledger_pin'] == value['accounting']['ledger_pin']
        and proof['baseline_sha256'] == gate.digest(gate.encoded(baseline['ledger']))
        and proof['admissions_sha256'] == value['admissions_sha256'] == gate.digest(gate.encoded(admissions))
        and value['accounting']['policy_sha256'] == account['policy_sha256']
        and len(proof['suffix']) == len(cases)
        and all(row['pin'] == case['state_after'] and row['parent'] == case['receipt']['state_before']
                for row, case in zip(proof['suffix'], cases)),
        'DEPLOYMENT_ORIGINAL_TERMINAL_TRANSITION_CHANGED')


def directories(plan, *, installed=False):
    gate.require(isinstance(plan,dict) and set(plan)==set(DIRECTORIES), 'DEPLOYMENT_DIRECTORY_PROFILE_REQUIRED')
    for name, expected in DIRECTORIES.items():
        item=plan[name]; path=Path(name)
        gate.require(set(item)=={'uid','gid','mode','before'} and item['before'] in ('ABSENT','EXISTING')
            and tuple(item[k] for k in ('uid','gid','mode'))==expected, 'DEPLOYMENT_DIRECTORY_ACCESS_REQUIRED')
        if installed or item['before']=='EXISTING':
            info=path.lstat()
            gate.require(stat.S_ISDIR(info.st_mode) and gate.access(path)==expected,
                         'DEPLOYMENT_DIRECTORY_ACCESS_CHANGED')
        else:
            gate.require(not path.exists() and not path.is_symlink(), 'DEPLOYMENT_NEW_DIRECTORY_ALREADY_EXISTS')
        # Parent may be the other explicitly approved new directory; otherwise protect it now.
        if path.parent==CONTROLLER:
            info=CONTROLLER.lstat()
            gate.require(stat.S_ISDIR(info.st_mode) and gate.access(CONTROLLER)==(997,987,0o700),
                         'DEPLOYMENT_EXISTING_CONTROLLER_DIRECTORY_CHANGED')
        elif str(path.parent) not in DIRECTORIES: gate.protected(path.parent,directory=True)
    inputs=JOBS/'inputs'
    gate.require(not inputs.exists() or not any(inputs.iterdir()), 'DEPLOYMENT_UNREVIEWED_INPUT_CONNECTOR')


def source_inventory(root, expected, source):
    observed={};gate.protected(root,directory=True)
    for path in Path(root).rglob('*'):
        if path.is_dir():gate.protected(path,directory=True)
        else:
            gate.protected(path)
            if '.git' not in path.relative_to(root).parts:
                observed[path.relative_to(root).as_posix()]=gate.digest(gate.read(path))
    gate.require(observed==expected, 'DEPLOYMENT_EXECUTING_SOURCE_INVENTORY_CHANGED')
    checked_source(root,source)


def registration_lock_plan(bundle, proposal, controller_gid):
    """Preserve the original lock when the reviewed optional config is present."""
    name=str(REGISTRATION_LOCK);targets=set(proposal['targets'])
    gate.require(targets in (gate.REQUIRED_TARGETS,gate.REQUIRED_TARGETS|{name}),
                 'DEPLOYMENT_EXACT_FIXED_BUNDLE_REQUIRED')
    if name not in targets:
        gate.require(not REGISTRATION_LOCK.exists() and not REGISTRATION_LOCK.is_symlink(),
                     'DEPLOYMENT_EXISTING_REGISTRATION_LOCK_NOT_REVIEWED')
        return
    expected={'sha256':gate.digest(b''),'uid':0,'gid':controller_gid,'mode':0o600}
    gate.require(proposal['targets'][name]==expected
        and proposal['previous_files'].get(name)==expected,
        'DEPLOYMENT_UNCHANGED_REGISTRATION_LOCK_REQUIRED')
    gate.require(gate.read(bundle/'literals'/expected['sha256'])==b'',
                 'DEPLOYMENT_EMPTY_REGISTRATION_LOCK_REQUIRED')


def registration_lock_identity(proposal, *, descriptor=None):
    """Check the fixed original inode and bytes, including a locked descriptor."""
    name=str(REGISTRATION_LOCK)
    if name not in proposal['targets']:return None
    expected=proposal['targets'][name]
    try:info=REGISTRATION_LOCK.lstat()
    except OSError:raise ValueError('DEPLOYMENT_REGISTRATION_LOCK_MISSING') from None
    gate.require(stat.S_ISREG(info.st_mode)
        and (info.st_uid,info.st_gid,stat.S_IMODE(info.st_mode),info.st_size)
            ==(expected['uid'],expected['gid'],expected['mode'],0)
        and expected['sha256']==gate.digest(b''),
        'DEPLOYMENT_REGISTRATION_LOCK_CHANGED')
    if descriptor is not None:
        held=os.fstat(descriptor)
        gate.require((held.st_dev,held.st_ino)==(info.st_dev,info.st_ino)
            and os.pread(descriptor,1,0)==b'', 'DEPLOYMENT_REGISTRATION_LOCK_CHANGED')
    return {'path':name,'device':info.st_dev,'inode':info.st_ino,
            'uid':info.st_uid,'gid':info.st_gid,'mode':stat.S_IMODE(info.st_mode),
            'bytes':0,'sha256':expected['sha256']}


def hold_registration_lock(stack, proposal):
    original=registration_lock_identity(proposal)
    if original is None:return None
    # No O_CREAT/O_TRUNC: the reviewed upgrade cannot establish a new lock.
    fd=os.open(REGISTRATION_LOCK,os.O_RDWR|os.O_NOFOLLOW)
    stream=stack.enter_context(os.fdopen(fd,'r+b'))
    try:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise ValueError('DEPLOYMENT_REGISTRATION_WORK_ACTIVE') from None
    gate.require(registration_lock_identity(proposal,descriptor=fd)==original,
                 'DEPLOYMENT_REGISTRATION_LOCK_CHANGED')
    return original


def unchanged_registration_lock(proposal, original):
    gate.require(registration_lock_identity(proposal)==original,
                 'DEPLOYMENT_REGISTRATION_LOCK_CHANGED')


def source_transition(previous, proposed, source):
    """Check reviewed fresh-execution lists; historical originals stay in place.

    The exact previous/proposed files are independently review-bound by inputs().
    Requiring an ever-growing subset here made the seventeenth release impossible.
    Historical reads/accounting instead authenticate their original saved event.
    """
    for pins in (previous, proposed):
        gate.require(isinstance(pins, list) and 1 <= len(pins) <= 16,
                     'DEPLOYMENT_BOUNDED_EXECUTION_SOURCES_REQUIRED')
        for pin in pins:
            gate.pin(pin, 40)
    gate.require(source in proposed, 'DEPLOYMENT_CURRENT_EXECUTION_SOURCE_REQUIRED')


def load_recovery(bundle, proposal):
    """Resolve reviewed literals to the unchanged strict preservation contract."""
    recovery_raw = gate.read(bundle/'literals'/gate.pin(proposal['recovery_sha256']))
    gate.require(gate.digest(recovery_raw) == proposal['recovery_sha256'],
                 'DEPLOYMENT_RECOVERY_LITERAL_CHANGED')
    from orchestrator import recovery_inventory
    recovery, _ = recovery_inventory.resolve(json.loads(recovery_raw),
        lambda sha: gate.read(bundle/'literals'/sha, maximum=recovery_inventory.MAX_PAGE_BYTES))
    validate_recovery(recovery, proposal)
    return recovery


def inputs(bundle_sha, source):
    gate.require(os.getuid()==0 and sys.dont_write_bytecode, 'DEPLOYMENT_ROOT_PYTHON_B_REQUIRED')
    gate.pin(bundle_sha);gate.pin(source,40)
    bundle=BASE/'bundles'/bundle_sha; gate.protected(bundle,directory=True)
    proposal_raw=gate.read(bundle/'proposal.json');proposal=json.loads(proposal_raw)
    gate.require(gate.digest(proposal_raw)==bundle_sha and proposal['source']==source
        and set(proposal['targets']) in (gate.REQUIRED_TARGETS,gate.REQUIRED_TARGETS|{str(REGISTRATION_LOCK)}),
                 'DEPLOYMENT_EXACT_FIXED_BUNDLE_REQUIRED')
    expected_root=Path('/opt/research-system/releases')/(source+'-research-handover')/'snapshot'
    gate.require(proposal['source_root']==str(expected_root), 'DEPLOYMENT_FIXED_RELEASE_REQUIRED')
    executing=Path(__file__).resolve().parents[1]
    gate.require(executing==BASE/'staging'/bundle_sha/'snapshot', 'DEPLOYMENT_FIXED_EXECUTING_STAGING_REQUIRED')
    source_inventory(executing,proposal['source_files'],source)
    recovery = load_recovery(bundle, proposal)
    target=lambda name:json.loads(gate.read(bundle/'literals'/proposal['targets'][str(CONFIG/name)]['sha256']))
    previous=lambda name:json.loads(gate.read(bundle/'literals'/proposal['previous_files'][str(CONFIG/name)]['sha256']))
    broker,controller=target('broker.json'),target('controller.json')
    old_broker,old_controller=previous('broker.json'),previous('controller.json')
    source_transition(old_broker['sources'], broker['sources'], source)
    gate.require(all(broker.get(k)==old_broker.get(k) for k in PRESERVED_BROKER)
        and source in broker['sources'],
        'DEPLOYMENT_EXISTING_BROKER_BOUNDARY_CHANGED')
    gate.require(all(controller.get(k)==old_controller.get(k) for k in PRESERVED_CONTROLLER)
        and controller['state']==str(CONTROLLER) and controller['controller_uid']==997
        and controller['controller_gid']==987, 'DEPLOYMENT_EXISTING_CONTROLLER_STATE_CHANGED')
    registration_lock_plan(bundle,proposal,controller['controller_gid'])
    jobs=json.loads(gate.read(bundle/'literals'/proposal['targets']['/etc/research-system/linux-scientific-jobs.json']['sha256']))
    gate.require(all(jobs.get(k)==str(JOBS/name) for k,name in
        [('requests','requests'),('outputs','outputs'),('snapshots','snapshots'),('database','jobs.sqlite')])
        and jobs.get('input_roots')==[str(JOBS/'inputs')]
        and jobs.get('proposals')==str(CONTROLLER/'scientific-versions')
        and jobs.get('worker_uid')==995 and jobs.get('worker_gid')==987,
        'DEPLOYMENT_FIXED_SCIENTIFIC_DIRECTORIES_REQUIRED')
    intake=json.loads(gate.read(bundle/'literals'/proposal['targets']['/etc/research-system/issue-intake.json']['sha256']))
    gate.require(intake.get('state')=='/var/lib/research-system/issue-intake'
        and intake.get('controller_config')==str(CONFIG/'controller.json'), 'DEPLOYMENT_FIXED_INTAKE_REQUIRED')
    return bundle,proposal,recovery,broker


def unit_definition(unit, raw, root):
    values={}
    for line in raw.decode().splitlines():
        if '=' in line and not line.lstrip().startswith(('#',';')):
            key,value=line.split('=',1);values.setdefault(key,[]).append(value)
    forbidden=('ExecStartPre','ExecStartPost','ExecStop','ExecStopPost','ExecCondition','ExecReload','EnvironmentFile')
    gate.require(not any(key in values for key in forbidden), 'DEPLOYMENT_SERVICE_SIDE_COMMAND_REFUSED')
    expected=None
    if unit.endswith('.service'):
        gate.require(len(values.get('ExecStart',[]))==1, 'DEPLOYMENT_SINGLE_EXECSTART_REQUIRED')
        expected=shlex.split(values['ExecStart'][0])
        prefix=['/usr/bin/python3','-B','-m']
        fixed={BROKER:prefix+['orchestrator.protected_handover','--config',str(CONFIG/'broker.json'),
                    'serve','--socket','/run/research-system/handover-live.sock'],
            'research-system-live-research.service':prefix+['orchestrator.handover_runtime',
                    '--config',str(CONFIG/'controller.json'),'tick'],
            'research-system-issue-intake.service':prefix+['orchestrator.issue_intake_service',
                    '--config','/etc/research-system/issue-intake.json','poll'],
            'research-system-scientific-completion.service':prefix+['orchestrator.protected_scientific_jobs',
                    '--poll-completions','--controller-config',str(CONFIG/'controller.json')],
            TEMPLATE:prefix+['orchestrator.linux_scientific_jobs','worker','--attempt','%i']}
        if unit in fixed:
            gate.require(expected==fixed[unit], 'DEPLOYMENT_FIXED_SERVICE_COMMAND_REQUIRED')
            if unit!='research-system-issue-intake.service':
                gate.require(values.get('WorkingDirectory')==[str(root)], 'DEPLOYMENT_FIXED_SERVICE_SOURCE_REQUIRED')
    elif unit.endswith('.timer'):
        gate.require(values.get('Unit')==[unit.replace('.timer','.service')], 'DEPLOYMENT_FIXED_TIMER_TARGET_REQUIRED')
    elif unit==SOCKET:
        gate.require(all(values.get(key)==[value] for key,value in {
            'ListenStream':'/run/research-system/handover-live.sock','Service':BROKER,
            'SocketUser':'root','SocketGroup':'research-runtime','SocketMode':'0660'}.items()),
            'DEPLOYMENT_FIXED_SOCKET_REQUIRED')
    return values,expected


def effective_service(unit, raw, state, root):
    values,expected=unit_definition(unit,raw,root)
    if expected is not None:
        match=re.search(r'path=([^;]+); argv\[\]=(.*?); ignore_errors=',state['ExecStart'])
        gate.require(match is not None and match.group(1).strip()==expected[0]
            and shlex.split(match.group(2).strip())==expected, 'DEPLOYMENT_EFFECTIVE_EXECSTART_CHANGED')
        for key in ('WorkingDirectory','User','Group'):
            gate.require(state[key]==values.get(key,[''])[0], 'DEPLOYMENT_EFFECTIVE_SERVICE_CHANGED')


def installed_units(bundle, proposal):
    observed=units_observation()
    for name,state in observed.items():
        gate.require(state['LoadState']=='loaded', 'DEPLOYMENT_INSTALLED_UNIT_NOT_LOADED')
        raw=gate.read(bundle/'literals'/proposal['targets'][str(UNITS/name)]['sha256'])
        effective_service(name,raw,state,proposal['source_root'])
    return observed


def pointer_observation():
    if not gate.ACTIVE.exists() and not gate.ACTIVE.is_symlink():return {'state':'ABSENT'}
    raw=gate.read(gate.ACTIVE,maximum=10000)
    return {'state':'EXISTING','sha256':gate.digest(raw),'raw':raw.decode()}


def atomic(path,raw,metadata):
    path=Path(path);gate.protected(path.parent,directory=True)
    temporary=path.parent/(path.name+'.reviewed-deployment-new')
    fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,metadata['mode'])
    with os.fdopen(fd,'wb') as stream:
        os.fchmod(stream.fileno(),metadata['mode']);os.fchown(stream.fileno(),metadata['uid'],metadata['gid'])
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,path)
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)


def stop_broker():
    command(['/usr/bin/systemctl','stop',SOCKET])
    command(['/usr/bin/systemctl','stop',BROKER])


def start_broker():
    command(['/usr/bin/systemctl','daemon-reload'])
    command(['/usr/bin/systemctl','start',SOCKET])
    command(['/usr/bin/systemctl','start',BROKER])


def actual_installed(root,source):
    # Use the new installed module, not a staging import pretending to be it.
    code=('import json,sys; from orchestrator.deployment_review import verify_installed; '
          'print(json.dumps(verify_installed(sys.argv[1],sys.argv[2],'
          'config_path="/etc/research-system/live-research/broker.json")))')
    return json.loads(command(['/usr/bin/python3','-B','-c',code,str(root),source],cwd=root))


def acquire(stack,bundle):
    for path in (bundle/'upgrade.lock',CONTROLLER/'branch.lock',CONTROLLER/'admission.lock'):
        if path.parent!=bundle:gate.require(path.exists(), 'DEPLOYMENT_EXISTING_CONTROL_LOCK_REQUIRED')
        fd=os.open(path,os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
        stream=stack.enter_context(os.fdopen(fd,'r+'))
        try:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError('DEPLOYMENT_CONCURRENT_WORK_RECONCILE') from None


def _terminal_accounting_commit(repo, commit):
    """Read hash-authenticated original objects; use the existing ledger parser."""
    import hashlib
    from orchestrator import inspection_admission_recovery as ledger
    from orchestrator import dispatch_limiter as limiter
    objects = {}

    def original(kind, identity):
        ledger.pin(identity)
        raw = ledger._git(repo, ['cat-file', kind, identity])
        header = (kind + ' ' + str(len(raw)) + '\0').encode()
        gate.require(hashlib.sha1(header + raw).hexdigest() == identity,
                     'DEPLOYMENT_TERMINAL_LEDGER_OBJECT_CHANGED')
        objects[identity] = (kind, raw)
        return raw

    raw = original('commit', commit)
    first = raw.split(b'\n', 1)[0]
    gate.require(re.fullmatch(rb'tree [0-9a-f]{40}', first) is not None,
                 'DEPLOYMENT_TERMINAL_LEDGER_TREE_REQUIRED')
    tree = original('tree', first[5:].decode('ascii'))
    prefix = b'100644 ' + limiter.FILE.encode() + b'\0'
    gate.require(tree.startswith(prefix) and len(tree) == len(prefix) + 20,
                 'DEPLOYMENT_TERMINAL_LEDGER_SINGLE_STATE_REQUIRED')
    original('blob', tree[len(prefix):].hex())
    row = ledger._state(objects, commit)
    return {'parents': [] if row['parent'] is None else [row['parent']],
            'state': row['state']}


def require_terminal_accounting(bundle, proof):
    """Authenticate completed manual accounting before prospective install only.

    This reads actual ordinary ledger originals. It neither charges a call nor
    manufactures a native admission or accepts a caller's reconciliation flag.
    """
    if proof.get('terminal_profile') not in ('operator-terminal-review/v1', 'server-terminal-review/v1'):
        return None
    from orchestrator import terminal_review
    from orchestrator import dispatch_limiter as limiter
    from orchestrator import inspection_admission_recovery as ledger
    bundle = Path(bundle)
    accounting_raw = gate.read(bundle/'terminal-accounting.json', maximum=4000000)
    proposal_raw = gate.read(bundle/'proposal.json')
    archive = gate.read(bundle/'source.tar.gz', maximum=10000000)
    gate.require(gate.digest(proposal_raw) == proof['proposal_sha256']
                 and gate.digest(archive) == proof['archive_sha256'],
                 'DEPLOYMENT_TERMINAL_ACCOUNTING_BUNDLE_CHANGED')
    review, repeated = terminal_review.load(bundle, proposal_raw, gate.archive_inventory(archive))
    gate.require(all(repeated[key] == proof[key] for key in (
        'terminal_review_index_sha256', 'terminal_review_manifest_sha256',
        'terminal_review_report_sha256', 'terminal_review_session_sha256')),
        'DEPLOYMENT_TERMINAL_ACCOUNTING_REVIEW_CHANGED')
    broker = json.loads(gate.read(CONFIG/'broker.json'))
    policy = broker['policy']; limiter.policy(policy)
    repo = _ledger_path(broker)
    status = authenticated_ledger_status(broker)
    cache = {}

    def read_commit(identity):
        ledger.pin(identity)
        if identity not in cache:
            gate.require(len(cache) < ledger.MAX_OBJECTS,
                         'DEPLOYMENT_TERMINAL_ACCOUNTING_OBJECT_BOUND')
            cache[identity] = _terminal_accounting_commit(repo, identity)
        return cache[identity]

    pin = ledger.pin(status.get('pin'))
    state = read_commit(pin)['state']
    ledger._status(status, {'pin': pin, 'state': state})
    result = terminal_review.validate_accounting(accounting_raw, review, status,
        pin, state, policy, broker['sources'], read_commit)
    gate.require(authenticated_ledger_status(broker) == status,
                 'DEPLOYMENT_TERMINAL_ACCOUNTING_STATE_MOVED')
    return result


def apply(bundle_sha,source):
    bundle,proposal,recovery,broker=inputs(bundle_sha,source);root=Path(proposal['source_root'])
    with ExitStack() as stack:
        acquire(stack,bundle)
        registration_lock=hold_registration_lock(stack,proposal)
        if (bundle/'restore-receipt.json').exists():raise ValueError('DEPLOYMENT_RESTORED_REQUIRES_NEW_PROPOSAL')
        completed=bundle/'upgrade-receipt.json'
        if completed.exists():
            receipt=json.loads(gate.read(completed));proof=actual_installed(root,source)
            gate.require(receipt['proposal_sha256']==bundle_sha and receipt['install_receipt_sha256']==proof_receipt(bundle),
                         'DEPLOYMENT_ORIGINAL_UPGRADE_RECEIPT_CHANGED')
            if registration_lock is not None:
                gate.require(receipt.get('registration_lock_preserved')==registration_lock,
                             'DEPLOYMENT_REGISTRATION_LOCK_CHANGED')
            return {**receipt,'duplicate':True,'restart_performed':False}
        gate.require(not (bundle/'install-intent.json').exists()
            and not (bundle/'upgrade-intent.json').exists(), 'DEPLOYMENT_PARTIAL_UPGRADE_REQUIRES_RECONCILIATION')
        terminal = proposal.get('review_profile') in ('operator-terminal-review/v1', 'server-terminal-review/v1')
        accounting = None
        if terminal:
            review, accounting = gate._preinstall_review(bundle, root, source)
        else:
            gate.verify_bundle(bundle,root,source,installed=False,prospective=True)
        for name in UNIT_NAMES:
            item=proposal['targets'][str(UNITS/name)]
            unit_definition(name,gate.read(bundle/'literals'/item['sha256']),root)
        units=units_observation();pause=quiescent(units,broker,recovery['preserved_blocked_tasks'])
        gate.require(units==recovery['units_before'], 'DEPLOYMENT_ORIGINAL_UNITS_CHANGED')
        pointer=pointer_observation()
        gate.require(pointer==recovery['previous_active'], 'DEPLOYMENT_ORIGINAL_ACTIVE_SELECTION_CHANGED')
        directories(recovery['directories'])
        transition = None
        if recovery.get('schema') == DIRECT_RECOVERY:
            preserved, transition = inspection_preserved_state(bundle, proposal, recovery, broker)
        elif recovery.get('schema') == TERMINAL_RECOVERY:
            preserved, transition = terminal_preserved_state(bundle, proposal, recovery, broker, accounting)
        else:
            preserved=state_fingerprint(broker)
            gate.require(preserved['sha256']==recovery['preserved_state_sha256'], 'DEPLOYMENT_PRESERVED_STATE_MOVED')
        gate.require(not root.parent.exists() and not root.parent.is_symlink(), 'DEPLOYMENT_NEW_RELEASE_ALREADY_EXISTS')
        gate.protected(root.parent.parent,directory=True)
        for path in proposal['targets']:
            gate.protected(Path(path).parent,directory=True)
            gate.require(not Path(path+'.reviewed-deployment-new').exists(), 'DEPLOYMENT_PARTIAL_ATOMIC_WRITE_RECONCILE')
        if terminal:
            # Recheck source/config/originals without a second broker cache fetch
            # after the strict preserved-state inventory has been accepted.
            gate.require(gate.verify_bundle(bundle, root, source, installed=False, prospective=True)
                         == review, 'DEPLOYMENT_TERMINAL_REVIEW_CHANGED_BEFORE_INTENT')
            gate._save_once(bundle, 'install-intent.json',
                            {'status': 'PREPARED_REVIEW_VERIFIED', **review})
        else:
            gate.begin_install(bundle,root,source)
        intent={'schema':'reviewed-upgrade/v1','source':source,'proposal_sha256':bundle_sha,
                'units_before':units,'previous_active':pointer,'preserved_state':preserved,'pause':pause}
        if transition is not None:
            intent['terminal_admission_transition' if terminal else 'inspection_admission_transition'] = transition
        if accounting is not None:intent['terminal_accounting']=accounting
        if registration_lock is not None:intent['registration_lock_preserved']=registration_lock
        gate._save_once(bundle,'upgrade-intent.json',intent)
        try:
            stop_broker()
            unchanged_registration_lock(proposal,registration_lock)
            gate.require(state_fingerprint(broker)==preserved, 'DEPLOYMENT_STATE_CHANGED_BEFORE_MUTATION')
            root.parent.mkdir(mode=0o755);os.chmod(root.parent,0o755)
            with tarfile.open(fileobj=io.BytesIO(gate.read(bundle/'source.tar.gz',maximum=10000000))) as archive:
                archive.extractall(root.parent,filter='data')
            for path in [root,*root.rglob('*')]:
                gate.require(not path.is_symlink(), 'DEPLOYMENT_EXTRACTED_SYMLINK_REFUSED')
                os.chown(path,0,0);os.chmod(path,0o755 if path.is_dir() else 0o644)
            source_inventory(root,proposal['source_files'],source)
            for name,item in sorted(recovery['directories'].items(),key=lambda x:len(Path(x[0]).parts)):
                if item['before']=='ABSENT':
                    Path(name).mkdir(mode=item['mode']);os.chown(name,item['uid'],item['gid']);os.chmod(name,item['mode'])
            for name,item in proposal['targets'].items():
                if name==str(REGISTRATION_LOCK):
                    unchanged_registration_lock(proposal,registration_lock)
                    continue
                atomic(name,gate.read(bundle/'literals'/item['sha256']),item)
            directories(recovery['directories'],installed=True)
            gate.require(state_fingerprint(broker)==preserved, 'DEPLOYMENT_PRESERVED_STATE_CHANGED')
            gate.record_install(bundle,root,source)
            selection={'schema':gate.SCHEMA,'source':source,'proposal_sha256':bundle_sha,
                       'install_receipt_sha256':proof_receipt(bundle)}
            atomic(gate.ACTIVE,gate.encoded(selection),{'uid':0,'gid':bundle.stat().st_gid,'mode':0o640})
            start_broker();after=installed_units(bundle,proposal);quiescent(after,broker,recovery['preserved_blocked_tasks'])
            proof=actual_installed(root,source)
            unchanged_registration_lock(proposal,registration_lock)
            gate.require(proof['proposal_sha256']==bundle_sha, 'DEPLOYMENT_RUNNING_PROOF_CHANGED')
            gate.require(state_fingerprint(broker)==preserved, 'DEPLOYMENT_PRESERVED_STATE_CHANGED')
            receipt={'schema':'reviewed-upgrade/v1','status':'REVIEWED_UPGRADE_INSTALLED_WORKERS_HELD',
                'source':source,'proposal_sha256':bundle_sha,'install_receipt_sha256':proof_receipt(bundle),
                'upgrade_intent_sha256':gate.digest(gate.read(bundle/'upgrade-intent.json')),
                'preserved_state':preserved,'running_broker':proof['running_broker'],
                'units_after':after,'models_started':0,'timers_enabled':False,
                'research_activated':False,'restart_performed':True}
            if transition is not None:
                receipt['terminal_admission_transition' if terminal else 'inspection_admission_transition'] = transition
            if registration_lock is not None:receipt['registration_lock_preserved']=registration_lock
            return gate._save_once(bundle,'upgrade-receipt.json',receipt)
        except BaseException as error:
            gate._save_once(bundle,'upgrade-failure.json',{'status':'PARTIAL_UPGRADE_PRESERVED_RECONCILE',
                'error_type':type(error).__name__,'automatic_retry':False,'source':source})
            raise


def proof_receipt(bundle):return gate.digest(gate.read(bundle/'install-receipt.json'))


def broker_cwd(pid):return (Path('/proc')/pid/'cwd').resolve(strict=True)


def restore(bundle_sha,source):
    bundle,proposal,recovery,broker=inputs(bundle_sha,source)
    with ExitStack() as stack:
        acquire(stack,bundle)
        registration_lock=hold_registration_lock(stack,proposal)
        # Retain every original-review gate; mixed old/new readback is checked below.
        gate.verify_bundle(bundle,proposal['source_root'],source,check_current=False)
        gate.require((bundle/'upgrade-intent.json').exists(), 'DEPLOYMENT_ORIGINAL_UPGRADE_INTENT_REQUIRED')
        intent=json.loads(gate.read(bundle/'upgrade-intent.json'))
        gate.require(intent['proposal_sha256']==bundle_sha and intent['source']==source
            and intent['units_before']==recovery['units_before']
            and intent['previous_active']==recovery['previous_active']
            and (recovery.get('schema') in (DIRECT_RECOVERY, TERMINAL_RECOVERY)
                 or intent['preserved_state']['sha256']==recovery['preserved_state_sha256']),
            'DEPLOYMENT_ORIGINAL_UPGRADE_INTENT_CHANGED')
        if recovery.get('schema') == DIRECT_RECOVERY:
            validate_inspection_intent(bundle, proposal, recovery, intent)
        elif recovery.get('schema') == TERMINAL_RECOVERY:
            validate_terminal_intent(bundle, proposal, recovery, intent)
        if registration_lock is not None:
            gate.require(intent.get('registration_lock_preserved')==registration_lock,
                         'DEPLOYMENT_REGISTRATION_LOCK_CHANGED')
        current_pointer=pointer_observation()
        if current_pointer!=intent['previous_active']:
            gate.require(current_pointer['state']=='EXISTING' and json.loads(current_pointer['raw'])=={
                'schema':gate.SCHEMA,'source':source,'proposal_sha256':bundle_sha,
                'install_receipt_sha256':proof_receipt(bundle)}, 'DEPLOYMENT_UNKNOWN_ACTIVE_SELECTION')
        if (bundle/'restore-receipt.json').exists():
            receipt=json.loads(gate.read(bundle/'restore-receipt.json'))
            gate.require(receipt['proposal_sha256']==bundle_sha
                and receipt['previous_source']==proposal['previous_source']
                and pointer_observation()==intent['previous_active'], 'DEPLOYMENT_ORIGINAL_RESTORE_CHANGED')
            for name,item in proposal['targets'].items():
                if name in proposal['previous_files']:
                    old=proposal['previous_files'][name]
                    gate.require(gate.digest(gate.read(name))==old['sha256']
                        and gate.access(name)==(old['uid'],old['gid'],old['mode']), 'DEPLOYMENT_RESTORED_TARGET_CHANGED')
                else:gate.require(not Path(name).exists() and not Path(name).is_symlink(), 'DEPLOYMENT_RESTORED_TARGET_CHANGED')
            return {**receipt,'duplicate':True,'restart_performed':False}
        gate.require(not (bundle/'restore-intent.json').exists(), 'DEPLOYMENT_PARTIAL_RESTORE_REQUIRES_RECONCILIATION')
        units=units_observation();quiescent(units,broker,recovery['preserved_blocked_tasks'],running=units[BROKER]['ActiveState']=='active')
        gate.require(state_fingerprint(broker)==intent['preserved_state'], 'DEPLOYMENT_RESULTS_CHANGED_RESTORE_REFUSED')
        # Every current target must still be either reviewed old or reviewed new bytes.
        for name,item in proposal['targets'].items():
            path=Path(name)
            if not path.exists() and not path.is_symlink():
                gate.require(name not in proposal['previous_files'], 'DEPLOYMENT_ORIGINAL_TARGET_MISSING');continue
            raw=gate.read(path);current=(gate.digest(raw),*gate.access(path))
            options=[(item['sha256'],item['uid'],item['gid'],item['mode'])]
            if name in proposal['previous_files']:
                old=proposal['previous_files'][name];options.append((old['sha256'],old['uid'],old['gid'],old['mode']))
            gate.require(current in options, 'DEPLOYMENT_CHANGED_TARGET_RESTORE_REFUSED')
        partials=[]
        for name,item in proposal['targets'].items():
            temporary=Path(name+'.reviewed-deployment-new')
            if temporary.exists() or temporary.is_symlink():
                observed=(gate.digest(gate.read(temporary)),*gate.access(temporary))
                variants=[(item['sha256'],item['uid'],item['gid'],item['mode'])]
                if name in proposal['previous_files']:
                    old=proposal['previous_files'][name]
                    variants.append((old['sha256'],old['uid'],old['gid'],old['mode']))
                gate.require(observed in variants, 'DEPLOYMENT_UNKNOWN_PARTIAL_WRITE_RESTORE_REFUSED')
                partials.append(temporary)
        checked_source(proposal['previous_source_root'],proposal['previous_source'])
        gate._save_once(bundle,'restore-intent.json',{'status':'EXPLICIT_RESTORE_STARTED','source':source,
            'proposal_sha256':bundle_sha,'upgrade_intent_sha256':gate.digest(gate.read(bundle/'upgrade-intent.json'))})
        stop_broker()
        if partials:
            saved=bundle/'restored-temporary-files';saved.mkdir(mode=0o700)
            for temporary in partials:os.replace(temporary,saved/gate.digest(str(temporary).encode()))
        for name,item in proposal['targets'].items():
            if name==str(REGISTRATION_LOCK):
                unchanged_registration_lock(proposal,registration_lock)
                continue
            if name in proposal['previous_files']:
                old=proposal['previous_files'][name];atomic(name,gate.read(bundle/'literals'/old['sha256']),old)
            elif Path(name).exists():
                saved=bundle/'restored-new-targets';saved.mkdir(mode=0o700,exist_ok=True)
                os.replace(name,saved/gate.digest(name.encode()))
        previous=intent['previous_active']
        if previous['state']=='ABSENT':
            if gate.ACTIVE.exists():os.replace(gate.ACTIVE,bundle/'restored-new-active.json')
        else:atomic(gate.ACTIVE,previous['raw'].encode(),{'uid':0,'gid':bundle.stat().st_gid,'mode':0o640})
        start_broker();after=units_observation();quiescent(after,broker,recovery['preserved_blocked_tasks'])
        unchanged_registration_lock(proposal,registration_lock)
        for name,item in proposal['previous_files'].items():
            gate.require(gate.digest(gate.read(name))==item['sha256']
                and gate.access(name)==(item['uid'],item['gid'],item['mode']), 'DEPLOYMENT_RESTORE_READBACK_CHANGED')
        pid=after[BROKER]['MainPID']
        gate.require(broker_cwd(pid)==Path(proposal['previous_source_root']),
                     'DEPLOYMENT_RESTORED_BROKER_SOURCE_CHANGED')
        for name,state in after.items():
            target=str(UNITS/name)
            if target in proposal['previous_files']:
                old=proposal['previous_files'][target]
                effective_service(name,gate.read(bundle/'literals'/old['sha256']),state,proposal['previous_source_root'])
        gate.require(state_fingerprint(broker)==intent['preserved_state'], 'DEPLOYMENT_RESTORE_STATE_CHANGED')
        receipt={'status':'PREVIOUS_DEPLOYMENT_RESTORED_WORKERS_HELD',
            'proposal_sha256':bundle_sha,'previous_source':proposal['previous_source'],
            'preserved_state':intent['preserved_state'],'models_started':0,'research_activated':False}
        if registration_lock is not None:receipt['registration_lock_preserved']=registration_lock
        return gate._save_once(bundle,'restore-receipt.json',receipt)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['apply','restore'])
    parser.add_argument('--bundle-sha256',required=True);parser.add_argument('--source',required=True)
    args=parser.parse_args()
    try:result=(apply if args.operation=='apply' else restore)(args.bundle_sha256,args.source)
    except Exception as error:
        reason=str(error)
        if not re.fullmatch('[A-Z][A-Z0-9_]{1,100}',reason):reason='DEPLOYMENT_FAILED_PRESERVE_AND_RECONCILE'
        print(json.dumps({'status':'REFUSED_OR_PARTIAL_DEPLOYMENT','reason':reason}));raise SystemExit(2) from None
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
