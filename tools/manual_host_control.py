#!/usr/bin/env python3
"""Bound root preflight for the new manual lane; no timer/service mutation.

Run by systemd (+ prefix) before one transition, not from a model. Upgrade
scheduling is left to the host under the recorded operator risk decision.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import sys
import pwd
import time

RUN=Path('/run/research-manual-sprint10')
NEEDRESTART=Path('/etc/needrestart/conf.d/research-manual-sprint10.conf')
EXCLUSION=b"# Reviewed manual lane: do not restart an in-flight client.\n$nrconf{override_rc}{qr(^research-manual-sprint10(?:-|\\.))} = 0;\n"
PROFILE=Path('/etc/apparmor.d/research-manual-bwrap')
VENDOR=Path('/etc/apparmor.d/bwrap-userns-restrict')
DISABLE=Path('/etc/apparmor.d/disable/bwrap-userns-restrict')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path,value,mode=0o644):
    path=Path(path);raw=value if isinstance(value,bytes) else (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
    try:
        os.fchmod(fd,mode)
        with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
        os.replace(name,path)
        d=os.open(path.parent,os.O_DIRECTORY)
        try:os.fsync(d)
        finally:os.close(d)
    finally:
        if Path(name).exists():Path(name).unlink()


def policy(runtime):
    from orchestrator.manual_host_guard import trusted
    config=json.loads(trusted(runtime).read_text());g=config['host_guard']
    if Path(g['profile'])!=PROFILE or Path(g['receipt'])!=RUN/'host-check.json':raise ValueError('HOST_GUARD_PATH')
    if sha(trusted(PROFILE))!=g['profile_sha256']:raise ValueError('APPARMOR_PROFILE_DRIFT')
    if not DISABLE.is_symlink() or DISABLE.resolve()!=VENDOR:raise ValueError('VENDOR_PROFILE_NOT_DISABLED')
    if sha(trusted(VENDOR))!=g['vendor_sha256']:raise ValueError('VENDOR_PROFILE_CHANGED_RECONCILE')
    if trusted(NEEDRESTART).read_bytes()!=EXCLUSION:raise ValueError('NEEDRESTART_EXCLUSION_DRIFT')
    profiles=Path('/sys/kernel/security/apparmor/profiles').read_text().splitlines()
    if 'bwrap (unconfined)' not in profiles or 'bwrap (enforce)' in profiles or 'unpriv_bwrap (enforce)' not in profiles:raise ValueError('EXPECTED_APPARMOR_PROFILE_NOT_LOADED')
    if Path('/proc/sys/kernel/apparmor_restrict_unprivileged_userns').read_text().strip()!='1':raise ValueError('GLOBAL_USERNS_CONTROL_CHANGED')
    return g


# This constant is run only after setuid/setgid, with isolated Python. Root
# neither reads database bytes nor imports SQLite to interpret lane-owned data.
STATE_READER = r"""import hashlib,json,os,sqlite3,sys,tempfile
from pathlib import Path
if os.geteuid()==0:raise SystemExit('ROOT_DATABASE_READ_FORBIDDEN')
database=Path(sys.argv[1])/'jobs.sqlite';wal=Path(str(database)+'-wal')
result={'uid':os.geteuid(),'state':{},'calls':[]}
if database.exists():
    if database.is_symlink() or wal.is_symlink():raise SystemExit('LANE_DATABASE_ALIAS')
    captured={database:database.read_bytes()}
    if wal.exists():captured[wal]=wal.read_bytes()
    if wal.exists()!=(wal in captured) or any(hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(raw).digest() for p,raw in captured.items()):raise SystemExit('LANE_DATABASE_MOVED_DURING_CAPTURE')
    with tempfile.TemporaryDirectory(prefix='manual-unprivileged-state-') as temp:
        copy=Path(temp)/'jobs.sqlite'
        for original,raw in captured.items():(copy if original==database else Path(str(copy)+'-wal')).write_bytes(raw)
        with sqlite3.connect(copy) as db:
            row=db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()
            tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            calls=[r[0] for r in db.execute('SELECT status FROM manual_calls LIMIT 31')] if 'manual_calls' in tables else []
    phase=json.loads(row[0]).get('phase') if row else None
    if (phase is not None and (not isinstance(phase,str) or len(phase)>64)) or len(calls)>30 or any(not isinstance(c,str) or len(c)>32 for c in calls):raise SystemExit('LANE_STATUS_SHAPE')
    result.update(state={'phase':phase} if row else {},calls=calls)
print(json.dumps(result))
"""


def lane_state(lane):
    options={};uid=os.geteuid()
    if uid==0:
        account=pwd.getpwnam('partho');uid=account.pw_uid
        options.update(user=uid,group=account.pw_gid,extra_groups=[])
    result=subprocess.run(['/usr/bin/python3','-I','-c',STATE_READER,str(lane)],
        cwd='/',env={'PATH':'/usr/bin:/bin'},capture_output=True,text=True,
        timeout=30,close_fds=True,**options)
    if result.returncode:raise ValueError('UNPRIVILEGED_LANE_READ_FAILED')
    value=json.loads(result.stdout)
    if value['uid']!=uid or uid==0:raise ValueError('LANE_READER_PRIVILEGES')
    return value['state'],value['calls']


def require_no_user_site():
    if not sys.flags.no_user_site:raise ValueError('PYTHON_USER_SITE_MUST_BE_DISABLED')



def release_lanes(value, *, filesystem_root=Path('/')):
    """Read the exact root-preserved companion binding, never arbitrary descendants.

    The default one-lane layout is unchanged. A second lane requires its plan,
    source, runtime, service bytes and path in the selected immutable hash list.
    filesystem_root is a disposable test boundary; live callers use /.
    """
    from orchestrator.manual_host_guard import trusted
    root=Path(filesystem_root).absolute()
    def path(name):
        p=Path(name)
        if not p.is_absolute() or '..' in p.parts or str(p)!=name:raise ValueError('SELECTED_LANE_PATH')
        q=root/name.lstrip('/')
        if any(x.is_symlink() for x in [q,*q.parents]):raise ValueError('SELECTED_LANE_ALIAS')
        return q
    state=value['state'];tag=Path(value['release']).name
    primary={'state':state,'lane':state+'/lane','repository':state+'/repository',
             'units':[tag+'.service',tag+'.timer']}
    record=str(Path(value['hash_list']).parent);mapping=record+'/experiment-lanes.json'
    if len(value['units'])==2:
        if path(mapping).exists():raise ValueError('UNREGISTERED_SELECTED_LANES')
        return [{**primary,'units':value['units']}]
    hash_path=trusted(path(value['hash_list']))
    if sha(hash_path)!=value['hash_list_sha256']:raise ValueError('SELECTED_LANE_HASHLIST_CHANGED')
    files=json.loads(hash_path.read_text())
    if mapping not in files:
        if value['units']!=primary['units'] or path(mapping).exists():raise ValueError('UNREGISTERED_SELECTED_LANES')
        return [primary]
    def bound(name):
        item=files.get(name)
        if not isinstance(item,dict) or set(item)!={'sha256','mode'}:raise ValueError('SELECTED_LANE_FILE_UNBOUND')
        p=trusted(path(name))
        if not p.is_file() or p.stat().st_nlink!=1 or sha(p)!=item['sha256'] or p.stat().st_mode&0o777!=item['mode']:
            raise ValueError('SELECTED_LANE_FILE_CHANGED')
        return p
    proof=json.loads(bound(mapping).read_text())
    if (set(proof)!={'schema','source','runtime_sha256','review_sha256','lanes'}
            or proof['schema']!='explicit-experiment-lanes/v1'
            or proof['source']!=value['source'] or proof['runtime_sha256']!=value['runtime_sha256']
            or sha(trusted(path(value['runtime'])))!=value['runtime_sha256']
            or sha(trusted(path(record+'/review.md')))!=proof['review_sha256']):
        raise ValueError('SELECTED_LANE_RELEASE_BINDING')
    expected=[]
    for item,suffix in [(6,''),(4,'/item4')]:
        unit_tag=tag+('-item4' if suffix else '')
        plan=record+('/experiment-plan-item4.json' if suffix else '/experiment-plan.json')
        raw=bound(plan).read_bytes();plan_value=json.loads(raw)
        if plan_value.get('schema')!='experiment-lane/v1' or type(plan_value.get('item_number')) is not int or plan_value['item_number']!=item:
            raise ValueError('SELECTED_LANE_PLAN_ITEM')
        row={'item_number':item,'state':state+suffix,'lane':state+suffix+'/lane',
             'repository':state+suffix+'/repository','units':[unit_tag+'.service',unit_tag+'.timer'],
             'plan':plan,'plan_sha256':hashlib.sha256(raw).hexdigest()}
        expected.append(row)
        # Root service definitions must actually address the mapped lane.
        service=bound('/etc/systemd/system/'+row['units'][0]).read_text().splitlines()
        checks={'WorkingDirectory':row['repository'],
            'ConditionPathExists':row['lane']+'/lane.json',
            'ExecStartPre':'+/usr/bin/env PYTHONPATH='+value['release']+' /usr/bin/python3 -s -B '+value['release']+'/tools/manual_host_control.py before --runtime '+value['runtime']+' --lane '+row['lane'],
            'ExecStart':'/usr/bin/python3 -s -B -m orchestrator.experiment_driver advance --state '+row['lane']}
        for key,wanted in checks.items():
            if [line for line in service if line.startswith(key+'=')]!=[key+'='+wanted]:raise ValueError('SELECTED_LANE_SERVICE_BINDING')
        timer=bound('/etc/systemd/system/'+row['units'][1]).read_text().splitlines()
        if [line for line in timer if line.startswith('Unit=')]!=['Unit='+row['units'][0]]:raise ValueError('SELECTED_LANE_SERVICE_BINDING')
        for name in ('state','lane','repository'):path(row[name])
    if proof['lanes']!=expected or value['units']!=[unit for row in expected for unit in row['units']]:
        raise ValueError('SELECTED_LANE_MAP_BINDING')
    return expected


def selected(runtime,lane, *, filesystem_root=Path('/')):
    from orchestrator.manual_host_guard import trusted
    root=Path(filesystem_root).absolute()
    pointer=trusted(root/'etc/research-system-manual-sprint10/selected-release.json')
    value=json.loads(pointer.read_text());runtime=Path(runtime);lane=Path(lane)
    if value['runtime']!=str(runtime) or value['runtime_sha256']!=sha(root/str(runtime).lstrip('/')):
        raise ValueError('UNSELECTED_MANUAL_RELEASE')
    # Keep the historical single-lane control path; no descendant exemption.
    if 'units' not in value:
        if str(lane)!=value['state']+'/lane':raise ValueError('UNSELECTED_MANUAL_RELEASE')
    elif str(lane) not in {row['lane'] for row in release_lanes(value,filesystem_root=root)}:
        raise ValueError('UNSELECTED_MANUAL_RELEASE')
    return value


def hook(action,runtime,lane):
    require_no_user_site()
    if action!='before':raise ValueError('HOST_PREFLIGHT_ONLY')
    from orchestrator.manual_host_guard import trusted
    runtime=trusted(runtime);lane=Path(lane);selected(runtime,lane)
    if not RUN.exists():
        RUN.mkdir(mode=0o755);RUN.chmod(0o755)
    trusted(RUN)
    with (RUN/'control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        try:
            # All transitions receive the same policy attestation. Phase/DB
            # inspection was only needed to acquire/release the removed hold.
            g=policy(runtime)
            invocation=os.environ.get('INVOCATION_ID')
            if not invocation:raise ValueError('SYSTEMD_INVOCATION_REQUIRED')
            atomic(RUN/'host-check.json',{'status':'PASS','lane':str(lane),
                'invocation':invocation,'time':time.time(),
                'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                'runtime_sha256':sha(runtime),'profile_sha256':g['profile_sha256'],
                'loaded':'bwrap (unconfined)','global_userns_restriction':'1'})
        except Exception as error:
            record={'status':'REFUSED','lane':str(lane),'action':action,'time':time.time(),
                'reason':str(error)[:240],'error_type':type(error).__name__}
            key=hashlib.sha256(json.dumps({k:v for k,v in record.items() if k!='time'},sort_keys=True).encode()).hexdigest()
            original=RUN/('host-refusal-'+key+'.json')
            if not original.exists():atomic(original,record)
            atomic(RUN/'host-refusal.json',record)
            raise


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['before']);p.add_argument('--runtime',required=True);p.add_argument('--lane',required=True);a=p.parse_args()
    if os.geteuid()!=0:raise SystemExit('ROOT_SYSTEMD_HOOK_REQUIRED')
    hook(a.action,a.runtime,a.lane)

if __name__=='__main__':main()
