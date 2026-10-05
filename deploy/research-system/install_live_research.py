#!/usr/bin/env python3
"""Install one reviewed supervised research proposal; start no research work.

Only the existing idle live broker is restarted. Original configuration, fixture,
ledger, credentials and partial installation evidence remain preserved. A completed
duplicate returns its original receipt; an incomplete intent requires reconciliation.
The supplied administrative review manifest binds evidence, not new authority.
"""
import argparse
import fcntl
import importlib.util
import io
import json
import os
from pathlib import Path
import pwd
import re
import sqlite3
import stat
import sys
import tarfile


def helper(name):
    path = Path(__file__).with_name(name+'.py')
    spec = importlib.util.spec_from_file_location('live_research_'+name, path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


admin = helper('install_live_handover')
archive_tools = helper('install_handover_fixture')
require, digest, encoded = admin.require, admin.digest, admin.encoded
read, immutable, command, protected = admin.read, admin.immutable, admin.command, admin.protected
SETUP = Path('/etc/research-system')
CONFIG = SETUP/'live-research'
STATE = Path('/var/lib/research-system/handover-live-controller')
UNIT_ROOT = Path('/etc/systemd/system')
LIVE = 'research-system-handover-live.service'
CONTROLLER = 'research-system-live-research.service'
WRAPPER = Path('/usr/local/bin/research-system-live-control')
FIXTURE_LINK = Path('/opt/research-system/handover')
SOCKET = Path('/run/research-system/handover-live.sock')
BASELINE = {
    'live_config': SETUP/'writer-setup-20260908/live-preparation-04d67a00/broker.proposed.json',
    'fixture_controller_config': SETUP/'handover-controller.json',
    'live_service': UNIT_ROOT/LIVE,
    'live_socket': UNIT_ROOT/'research-system-handover-live.socket',
    'fixture_service': UNIT_ROOT/'research-system-handover.service',
    'fixture_controller_service': UNIT_ROOT/'research-system-handover-controller.service',
    'fixture_wrapper': Path('/usr/local/bin/research-system-control'),
}
CONFIG_HASHES = {
    'live_config': '325cca0f4fa0b9ced2fe52d84ad944637bcf4900ed6be2b3446d1455829718cd',
    'fixture_controller_config': '4b67acfe868aacc5e4a5562d9fc59b18c63f92ab24d310615954a1fd859b671c',
}
REQUIRED_SOURCE = {
    'deploy/research-system/'+name+'.py' for name in (
        'install_live_research', 'install_live_handover', 'install_handover_fixture',
        'prepare_live_research')
} | {'orchestrator/remote_supervisor.py'}


def checked_manifest(manifest, source, proposal_raw, evidence, request_raw, review_raw, execution_raw, inputs):
    fields = {'source','archive_sha256','proposal_sha256','evidence_sha256',
              'source_review_request_sha256','source_review_sha256','source_review_execution_sha256','source_input_sha256',
              'before_sha256','ledger_pin','ledger_state_sha256','fixture_link'}
    require(set(manifest) == fields and manifest['source'] == source,
            'EXACT_LIVE_RESEARCH_REVIEW_MANIFEST_REQUIRED')
    require(re.fullmatch('[0-9a-f]{40}',source) is not None
            and re.fullmatch('[0-9a-f]{40}',manifest['ledger_pin']) is not None,
            'EXACT_SOURCE_AND_LEDGER_PINS_REQUIRED')
    for name in ('archive_sha256','proposal_sha256','evidence_sha256',
                 'source_review_request_sha256','source_review_sha256','source_review_execution_sha256','ledger_state_sha256'):
        require(isinstance(manifest[name],str) and re.fullmatch('[0-9a-f]{64}',manifest[name]),
                'EXACT_REVIEW_DIGEST_REQUIRED')
    for key,raw in [('proposal_sha256',proposal_raw),('evidence_sha256',evidence),
                    ('source_review_request_sha256',request_raw),('source_review_sha256',review_raw),
                    ('source_review_execution_sha256',execution_raw)]:
        require(digest(raw) == manifest[key], 'REVIEWED_INPUT_CHANGED')
    request = json.loads(request_raw); review = json.loads(review_raw); execution = json.loads(execution_raw)
    judgment = review.get('structured_output',{})
    require(review.get('subtype') == 'success' and review.get('is_error') is False
            and judgment.get('verdict') == 'APPROVE' and judgment.get('reviewed_commit') == source
            and judgment.get('scope') == request.get('scope') == 'human-controls'
            and request.get('reviewed_commit') == source
            and execution.get('reviewed_commit') == source and execution.get('returncode') == 0
            and execution.get('response_sha256') == digest(review_raw)
            and execution.get('request_sha256') == digest(request_raw)
            and execution.get('requested_model') == 'claude-fable-5'
            and execution.get('assistant_message_models') == ['claude-fable-5'],
            'COMPLETED_EXACT_SOURCE_REVIEW_REQUIRED')
    hashes = manifest['source_input_sha256']
    require(isinstance(hashes,dict) and REQUIRED_SOURCE <= set(hashes) and len(hashes) <= 128
            and set(inputs) == set(hashes), 'COMPLETE_INSTALLER_SOURCE_REVIEW_REQUIRED')
    for name,raw in inputs.items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts
                and digest(raw) == hashes[name]
                and execution.get('input_file_sha256',{}).get(name) == hashes[name]
                and request.get('input_file_sha256',{}).get(name) == hashes[name],
                'REVIEWED_SOURCE_BYTES_CHANGED')
    require(set(manifest['before_sha256']) == set(BASELINE)
            and all(manifest['before_sha256'][k] == v for k,v in CONFIG_HASHES.items()),
            'RECONCILED_ORIGINAL_CONFIGURATION_REQUIRED')


def checked_proposal(source, proposal, files, originals, evidence, prepare):
    require(proposal.get('status') == 'PROPOSED_NOT_INSTALLED' and proposal.get('source') == source
            and proposal.get('unattended_activation') is False
            and proposal.get('new_credentials') is False and proposal.get('reset_or_initialize') is False,
            'BOUNDED_SUPERVISED_PROPOSAL_REQUIRED')
    live = json.loads(originals['live_config'])
    previous = json.loads(originals['fixture_controller_config'])
    controller = json.loads(files['controller.json'])
    request = controller['research_request']
    expected = prepare.plan(source,live,previous,request)
    expected = {name:value.encode() if isinstance(value,str) else encoded(value)
                for name,value in expected.items()}
    require(files == expected and proposal['file_sha256'] == {n:digest(v) for n,v in files.items()},
            'GENERATED_CONFIGURATION_CHANGED')
    require(proposal['input_sha256'] == {n:digest(encoded(v)) for n,v in (
        ('live_configuration',live),('previous_controller',previous),('research_request',request))}
        and request['evidence_sha256'] == digest(evidence), 'PROPOSAL_INPUT_BINDING_CHANGED')
    require(proposal['limits'] == {'research_tasks':1,'model_stages_per_task':3,
            'per_stage_seconds':240,'timer_enabled':False}, 'BOUNDED_RESEARCH_LIMITS_CHANGED')
    return live, previous, controller


def reviewed_private_inputs(request_raw, proposal_raw, evidence, files):
    """The actual immutable review request must include every prepared byte set."""
    observed=json.loads(request_raw).get('private_evidence_sha256')
    require(isinstance(observed,dict) and all(isinstance(value,str)
            and re.fullmatch('[0-9a-f]{64}',value) for value in observed.values()),
            'ACTUAL_PRIVATE_REVIEW_INPUTS_REQUIRED')
    required={digest(proposal_raw),digest(evidence),*(digest(raw) for raw in files.values())}
    require(required <= set(observed.values()), 'ACTUAL_REVIEW_PRIVATE_INPUT_MISSING')


def baseline():
    return {name:read(path,private=name == 'live_config') for name,path in BASELINE.items()}


def ledger(live):
    path = Path(live['ledger_repo']); protected(path,private=True,directory=True)
    pin = command(['git','-C',str(path),'rev-parse','refs/remotes/origin/automation/dispatch-state']).decode().strip()
    require(re.fullmatch('[0-9a-f]{40}',pin) is not None, 'RETAINED_LEDGER_PIN_REQUIRED')
    raw = command(['git','-C',str(path),'show',pin+':dispatch_state.json'])
    observed = command(['git','-c','credential.helper=','ls-remote',admin.REMOTE,admin.REF]).decode().split()
    require(observed == [pin,admin.REF], 'SHARED_REMOTE_LEDGER_MOVED_RECONCILE')
    return {'pin':pin,'state_sha256':digest(raw)}


def fixed_preserved(originals, live, previous, manifest, *, installed=False):
    current = baseline()
    for name,raw in originals.items():
        if installed and name == 'live_service':continue
        require(current[name] == raw, 'ORIGINAL_CONFIGURATION_OR_FIXTURE_CHANGED')
    require(FIXTURE_LINK.is_symlink() and os.readlink(FIXTURE_LINK) == manifest['fixture_link']
            and FIXTURE_LINK.resolve(strict=True) == Path(previous['source_root']),
            'ORIGINAL_FIXTURE_LINK_CHANGED')
    return ledger(live)


def completed_tasks(db):
    with sqlite3.connect(Path(db).as_uri()+'?mode=ro',uri=True) as connection:
        require(connection.execute("SELECT count(*) FROM tasks WHERE status != 'COMPLETE'").fetchone()[0] == 0,
                'EXISTING_COORDINATOR_WORK_RECONCILE')


def recovery_state(intent, receipt, manifest):
    if intent is None and receipt is None:return 'FRESH'
    require(intent is not None and receipt is not None, 'PARTIAL_INSTALL_PRESERVED_RECONCILE')
    # The original raw manifest digest is checked separately by the caller.
    require(intent['source'] == receipt['source'] == manifest['source']
            and intent['review_manifest_sha256'] == receipt['review_manifest_sha256']
            and receipt['original_sha256'] == manifest['before_sha256']
            and receipt['status'] == 'LIVE_RESEARCH_INSTALLED_BROKER_READY_TASK_NOT_SUBMITTED'
            and receipt['models_started'] == 0 and receipt['controller_started'] is False
            and receipt['timer_enabled'] is False and receipt['credentials_modified'] is False
            and receipt['unattended_activated'] is False,
            'ORIGINAL_INSTALL_RECEIPT_CHANGED')
    return 'COMPLETE'


def idle(live, previous):
    turns = Path(live['turn_root'])
    require(not turns.is_symlink(), 'LIVE_TURN_ROOT_CHANGED')
    if turns.exists():
        protected(turns,private=True,directory=True)
        require(not any(turns.iterdir()), 'EXISTING_LIVE_TURN_RECONCILE')
    state = admin.unit_state('research-system-handover-controller.service')
    require(state['ActiveState'] == 'inactive', 'EXISTING_CONTROLLER_ACTIVE_RECONCILE')
    db = Path(previous['state'])/'coordinator.sqlite'
    completed_tasks(db)
    raw = command(['systemctl','show',LIVE,'--property=ActiveState,SubState,MainPID,ControlGroup'])
    fields = dict(line.split('=',1) for line in raw.decode().splitlines())
    require(fields['ActiveState'] == 'active' and fields['SubState'] == 'running'
            and fields['MainPID'].isdigit() and int(fields['MainPID']) > 0,
            'RUNNING_IDLE_LIVE_BROKER_REQUIRED')
    group = Path(fields['ControlGroup'])
    require(group.is_absolute() and '..' not in group.parts, 'LIVE_BROKER_CGROUP_REQUIRED')
    processes = (Path('/sys/fs/cgroup')/str(group).lstrip('/')/'cgroup.procs').read_text().split()
    require(processes == [fields['MainPID']], 'LIVE_BROKER_CHILD_WORK_RECONCILE')
    require(stat.S_ISSOCK(SOCKET.lstat().st_mode), 'EXISTING_LIVE_SOCKET_REQUIRED')
    return fields


def install(source, staging):
    require(os.getuid() == 0 and sys.dont_write_bytecode, 'SETUP_ADMIN_PYTHON_B_REQUIRED')
    require(re.fullmatch('[0-9a-f]{40}',source) is not None, 'EXACT_SOURCE_REQUIRED')
    staging = Path(staging)
    require(staging == SETUP/('live-research-install-'+source[:12]), 'FIXED_INSTALL_STAGING_REQUIRED')
    protected(staging,private=True,directory=True); os.umask(0o077)
    fd = os.open(staging,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError('CONCURRENT_INSTALL_RECONCILE') from None
        manifest_raw = read(staging/'review-manifest.json'); manifest = json.loads(manifest_raw)
        proposal_raw = read(staging/'proposal/proposal.json'); proposal = json.loads(proposal_raw)
        evidence = read(staging/'research-evidence.json',maximum=65536)
        request_raw = read(staging/'source-review-request.json',maximum=2000000)
        review_raw = read(staging/'source-review.json',maximum=1000000)
        execution_raw = read(staging/'source-review-execution.json')
        protected(staging/'source.tar',private=True)
        archive = archive_tools.verified_archive(staging/'source.tar',manifest['archive_sha256'])
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            inputs = {name:bundle.extractfile('snapshot/'+name).read()
                      for name in manifest['source_input_sha256']}
        checked_manifest(manifest,source,proposal_raw,evidence,request_raw,review_raw,execution_raw,inputs)
        for name in REQUIRED_SOURCE:
            require(read(Path(__file__).parents[2]/name,private=False) == inputs[name],
                    'EXECUTING_INSTALLER_HELPER_CHANGED')
        files = {name:read(staging/'proposal'/name) for name in proposal['file_sha256']
                 if re.fullmatch('[a-z][a-z0-9.-]+',name)}
        receipt_path = staging/'install-receipt.json'
        original_dir = staging/'originals'
        intent_path=staging/'install-intent.json'
        intent=json.loads(read(intent_path)) if intent_path.exists() or intent_path.is_symlink() else None
        receipt=json.loads(read(receipt_path)) if receipt_path.exists() or receipt_path.is_symlink() else None
        completed = recovery_state(intent,receipt,manifest) == 'COMPLETE'
        originals = ({name:read(original_dir/name) for name in BASELINE} if completed else baseline())
        require({n:digest(v) for n,v in originals.items()} == manifest['before_sha256'],
                'EXACT_ORIGINAL_BYTES_REQUIRED')
        executing_root=Path(__file__).parents[2]
        sys.path.insert(0,str(executing_root))
        from orchestrator.remote_supervisor import checked_source
        checked_source(executing_root,source)
        prepare = helper('prepare_live_research')
        live, previous, controller = checked_proposal(source,proposal,files,originals,evidence,prepare)
        reviewed_private_inputs(request_raw,proposal_raw,evidence,files)
        account = pwd.getpwnam('research-controller'); gid = controller['controller_gid']
        require(account.pw_uid == controller['controller_uid'], 'EXISTING_CONTROLLER_IDENTITY_CHANGED')
        import grp
        require(grp.getgrnam('research-runtime').gr_gid == gid, 'EXISTING_RUNTIME_GROUP_CHANGED')
        release = Path(controller['source_root']).parent; root = release/'snapshot'
        targets = {CONFIG/'broker.json':(files['broker.json'],0o600,0,0),
            CONFIG/'controller.json':(files['controller.json'],0o640,0,gid),
            CONFIG/'research-evidence.json':(evidence,0o640,0,gid),
            UNIT_ROOT/LIVE:(files[LIVE],0o644,0,0),
            UNIT_ROOT/CONTROLLER:(files[CONTROLLER],0o644,0,0),
            WRAPPER:(files['research-system-live-control.sh'],0o755,0,0)}
        before_ledger = fixed_preserved(originals,live,previous,manifest,installed=completed)
        if completed:
            require(receipt['review_manifest_sha256'] == digest(manifest_raw)
                    and receipt['installed_sha256'] == {str(p):digest(v[0]) for p,v in targets.items()},
                    'ORIGINAL_INSTALL_RECEIPT_CHANGED')
            checked_source(root,source)
            for path,(raw,mode,uid,owner_gid) in targets.items():
                info=path.lstat()
                require(read(path,private=mode==0o600) == raw and stat.S_IMODE(info.st_mode)==mode
                        and info.st_uid==uid and info.st_gid==owner_gid, 'INSTALLED_BYTES_OR_ACCESS_CHANGED')
            return {**receipt,'duplicate':True,'current_ledger':before_ledger,'restart_performed':False}
        require(before_ledger == {'pin':manifest['ledger_pin'],'state_sha256':manifest['ledger_state_sha256']},
                'LIVE_LEDGER_MOVED_RECONCILE')
        idle_before = idle(live,previous)
        for path in (release,CONFIG,STATE,WRAPPER,UNIT_ROOT/CONTROLLER,original_dir,
                     UNIT_ROOT/(CONTROLLER+'.d'),UNIT_ROOT/(LIVE+'.d'),
                     UNIT_ROOT/'research-system-handover-live.socket.d'):
            require(not path.exists() and not path.is_symlink(), 'EXISTING_INSTALL_TARGET_RECONCILE')
            protected(path.parent,directory=True)
        for unit in (CONTROLLER,'research-system-live-research.timer'):
            require(admin.unit_state(unit)['LoadState']=='not-found', 'EXISTING_RESEARCH_UNIT_RECONCILE')
        immutable(staging/'install-intent.json',encoded({'status':'INSTALLING_ONE_SUPERVISED_RESEARCH_PROPOSAL',
            'source':source,'review_manifest_sha256':digest(manifest_raw),'ledger':before_ledger,
            'original_sha256':manifest['before_sha256'],'idle_broker':idle_before,
            'models_started':0,'controller_started':False,'timer_enabled':False}))
        try:
            original_dir.mkdir(mode=0o700)
            for name,raw in originals.items():immutable(original_dir/name,raw)
            require(fixed_preserved(originals,live,previous,manifest)==before_ledger,
                    'BASELINE_CHANGED_BEFORE_INSTALL')
            idle(live,previous)
            release.mkdir(mode=0o755);os.chmod(release,0o755)
            with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:bundle.extractall(release,filter='data')
            archive_tools.readable_source(root); checked_source(root,source)
            CONFIG.mkdir(mode=0o750);os.chown(CONFIG,0,gid);os.chmod(CONFIG,0o750)
            (CONFIG/'controls').mkdir(mode=0o750);os.chown(CONFIG/'controls',0,gid);os.chmod(CONFIG/'controls',0o750)
            STATE.mkdir(mode=0o700);os.chown(STATE,account.pw_uid,gid)
            (STATE/'changes').mkdir(mode=0o700);os.chown(STATE/'changes',account.pw_uid,gid)
            for path,(raw,mode,uid,owner_gid) in targets.items():
                if path==UNIT_ROOT/LIVE:continue
                immutable(path,raw,mode=mode);os.chown(path,uid,owner_gid)
            command(['systemd-analyze','verify',str(staging/'proposal'/LIVE),str(UNIT_ROOT/CONTROLLER)])
            require(fixed_preserved(originals,live,previous,manifest)==before_ledger,
                    'BASELINE_CHANGED_BEFORE_BROKER_RESTART')
            idle(live,previous)
            temporary=UNIT_ROOT/(LIVE+'.live-research-new')
            immutable(temporary,files[LIVE],mode=0o644);os.replace(temporary,UNIT_ROOT/LIVE)
            unit_fd=os.open(UNIT_ROOT,os.O_RDONLY|os.O_DIRECTORY)
            try:os.fsync(unit_fd)
            finally:os.close(unit_fd)
            command(['systemctl','daemon-reload']);command(['systemctl','restart',LIVE])
            after=idle(live,previous)
            require(Path('/proc/'+after['MainPID']+'/cwd').resolve(strict=True)==root,
                    'RESTARTED_BROKER_SOURCE_CHANGED')
            require(fixed_preserved(originals,live,previous,manifest,installed=True)==before_ledger,
                    'PRESERVED_STATE_CHANGED_DURING_INSTALL')
            require(admin.unit_state(CONTROLLER)['ActiveState']=='inactive', 'RESEARCH_CONTROLLER_UNEXPECTEDLY_STARTED')
            for path,(raw,mode,uid,owner_gid) in targets.items():
                info=path.lstat()
                require(read(path,private=mode==0o600)==raw and stat.S_IMODE(info.st_mode)==mode
                        and info.st_uid==uid and info.st_gid==owner_gid,'INSTALLED_BYTES_OR_ACCESS_CHANGED')
            receipt={'status':'LIVE_RESEARCH_INSTALLED_BROKER_READY_TASK_NOT_SUBMITTED','source':source,
                'review_manifest_sha256':digest(manifest_raw),'original_sha256':manifest['before_sha256'],
                'installed_sha256':{str(p):digest(v[0]) for p,v in targets.items()},
                'ledger_before':before_ledger,'ledger_after':before_ledger,'fixture_preserved':True,
                'restart_performed':True,'models_started':0,'controller_started':False,
                'timer_enabled':False,'credentials_modified':False,'unattended_activated':False}
            immutable(receipt_path,encoded(receipt));return receipt
        except BaseException as error:
            immutable(staging/'install-failure.json',encoded({'status':'PARTIAL_INSTALL_PRESERVED_RECONCILE',
                'error_type':type(error).__name__,'automatic_retry':False}))
            raise
    finally:os.close(fd)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True);parser.add_argument('--staging',required=True)
    args=parser.parse_args()
    try:print(json.dumps(install(args.source,args.staging)))
    except Exception as error:
        reason=str(error)
        if not re.fullmatch('[A-Z][A-Z0-9_]{1,100}',reason):reason='INSTALL_FAILED_PRESERVE_ORIGINALS_AND_RECONCILE'
        print(json.dumps({'status':'REFUSED_OR_PARTIAL_INSTALL_RECONCILE','reason':reason}),file=sys.stderr)
        raise SystemExit(2) from None
