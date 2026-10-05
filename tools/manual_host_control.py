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
            calls=[r[0] for r in db.execute('SELECT status FROM manual_calls LIMIT 9')] if 'manual_calls' in tables else []
    phase=json.loads(row[0]).get('phase') if row else None
    if (phase is not None and (not isinstance(phase,str) or len(phase)>64)) or len(calls)>8 or any(not isinstance(c,str) or len(c)>32 for c in calls):raise SystemExit('LANE_STATUS_SHAPE')
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



def selected(runtime,lane):
    from orchestrator.manual_host_guard import trusted
    pointer=trusted('/etc/research-system-manual-sprint10/selected-release.json')
    value=json.loads(pointer.read_text())
    if value['runtime']!=str(runtime) or str(lane)!=value['state']+'/lane' or value['runtime_sha256']!=sha(runtime):raise ValueError('UNSELECTED_MANUAL_RELEASE')
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
