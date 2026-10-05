"""Server pre-reservation proof. No credentials, model call or privileged command.

systemd's root ExecStartPre checks kernel policy once per one-transition service
invocation. Its root-owned receipt is bound to that invocation and runtime bytes.
The unprivileged driver then exercises the actual nested Codex sandbox itself.
"""
import json
import os
from pathlib import Path
from orchestrator import private_records
import subprocess
import tempfile
import time
from orchestrator import manual_runtime,manual_isolation as iso


def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        if p.is_symlink() or p.stat().st_uid!=0 or p.stat().st_mode&0o022:
            raise ValueError('HOST_PROOF_NOT_ROOT_OWNED')
    return path


def proof(config):
    path=trusted(config['receipt']);v=json.loads(path.read_text())
    runtime=trusted(os.environ['RESEARCH_MANUAL_RUNTIME_CONFIG'])
    if not os.environ.get('INVOCATION_ID') or v.get('invocation')!=os.environ['INVOCATION_ID']:
        raise ValueError('HOST_PROOF_WRONG_INVOCATION')
    if v.get('runtime_sha256')!=iso.sha(runtime) or v.get('status')!='PASS' or v.get('boot_id')!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():
        raise ValueError('HOST_PROOF_BINDING')
    if not 0<=time.time()-v['time']<180:raise ValueError('HOST_PROOF_EXPIRED')
    if v.get('profile_sha256')!=iso.sha(trusted(config['profile'])) or v.get('loaded')!='bwrap (unconfined)' or v.get('global_userns_restriction')!='1':
        raise ValueError('HOST_POLICY_DRIFT')
    return v


def nested_probe():
    # No credentials or native exec/model call. The native `sandbox` subcommand
    # exercises Codex's actual inner restriction inside our unchanged read jail.
    with tempfile.TemporaryDirectory(prefix='manual-nested-check-') as temp:
        work=Path(temp)/'workspace';home=Path(temp)/'home';private_records.mkdir(work);private_records.mkdir(home);private_records.mkdir(home/'.codex')
        script="from pathlib import Path; assert not Path('/mnt/c').exists(); Path('nested-ok').write_text('PASS')"
        cmd=['/tools/node','/tools/codex/bin/codex.js','sandbox','--config','sandbox_mode="workspace-write"','--','/usr/bin/python3','-c',script]
        result=subprocess.run(iso.command(work,home,'codex',cmd,mode='exec'),capture_output=True,text=True,timeout=45,close_fds=True)
        if result.returncode or not (work/'nested-ok').is_file() or (work/'nested-ok').read_text()!='PASS':
            raise ValueError('NESTED_SANDBOX_PREFLIGHT_FAILED')
    return {'status':'PASS','model_calls':0}


def before_call(workspace):
    config=manual_runtime.settings().get('host_guard')
    if not config:return {'status':'LOCAL_MODE_NO_SERVER_POLICY'}
    # Package and host checks MUST precede even the credential-free native probe.
    packages=manual_runtime.package_hashes();host=proof(config)
    result={'host':host,'packages':packages,'nested':nested_probe()}
    private_records.write_text(Path(workspace)/'host-pre-reservation.json',json.dumps(result,sort_keys=True,indent=2)+'\n')
    return result


def lane_status(lane):
    """Read root-owned operational evidence without opening credentials or DBs."""
    config=manual_runtime.settings().get('host_guard')
    if not config:return {'mode':'LOCAL','upgrade_timer_control':'REMOVED_BY_OPERATOR','legacy_hold_record':None,'last_refusal':None}
    directory=Path(config['receipt']).parent
    records={}
    for key,name in [('legacy_hold_record','upgrade-hold.json'),('last_refusal','host-refusal.json'),('last_check','host-check.json')]:
        path=directory/name
        try:
            value=json.loads(trusted(path).read_text())
        except FileNotFoundError:
            continue  # no current receipt, or an operator archived a legacy record
        if value.get('lane')==str(lane):records[key]=value
    refusal=records.get('last_refusal');check=records.get('last_check')
    if refusal:refusal['subsequent_check_passed']=bool(check and check.get('time',0)>refusal['time'])
    return {'mode':'SERVER','upgrade_timer_control':'REMOVED_BY_OPERATOR','legacy_hold_record':records.get('legacy_hold_record'),'last_refusal':refusal}


def report_status(lane):
    value=lane_status(lane)
    legacy=value['legacy_hold_record'];refusal=value['last_refusal']
    return ('Host controls (at report time): upgrade timer control removed by operator; '+
        'legacy hold record '+(legacy['status']+' (historical; not a current timer observation)' if legacy else 'none')+
        '; last host/AppArmor refusal: '+
        (refusal['reason']+'; subsequent check passed='+str(refusal['subsequent_check_passed']) if refusal else 'none')+'.')
