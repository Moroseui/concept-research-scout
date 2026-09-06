#!/usr/bin/env python3
"""Exact-binary Ubuntu userns compatibility; no global disable, sudo or model call."""
import argparse
import grp
import hashlib
import json
import os
import pwd
from pathlib import Path
import subprocess
import uuid

BASE=Path('/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl')
BINARIES={BASE/'bin/codex':'56ef98ab4032d317ab26e9b5e5a175650717351edb16ed9cde0cb6d1734d62da',BASE/'codex-resources/bwrap':'77360cb751ccedc5971391444ac86a8a33c15b04d6b4a6fe45f5d25496e62c4c'}
PROFILE='/etc/apparmor.d/research-system-codex'
POLICY='profile research-system-codex '+str(BASE/'bin/codex')+' flags=(unconfined) {\n  userns,\n}\n'

def checked_binary(path,sha):
    for parent in path.parents:
        if parent.is_symlink() or parent.stat().st_uid!=0 or parent.stat().st_mode & 0o022:raise ValueError('UNPROTECTED_BINARY_PARENT')
    if path.is_symlink() or path.stat().st_uid!=0 or path.stat().st_mode & 0o022:raise ValueError('UNPROTECTED_BINARY')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=sha:raise ValueError('BINARY_IDENTITY_CHANGED')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');a=p.parse_args()
    if os.getuid()!=0:raise ValueError('BOUNDED_SETUP_ADMIN_REQUIRED')
    os.umask(0o077)
    for path,sha in BINARIES.items():checked_binary(path,sha)
    restriction=Path('/proc/sys/kernel/apparmor_restrict_unprivileged_userns')
    if restriction.read_text().strip()!='1':raise ValueError('EXPECTED_GLOBAL_RESTRICTION_REQUIRED')
    if not a.apply:
        print(json.dumps({'status':'PREPARED_NOT_APPLIED','profile':PROFILE,'binary_sha256':{str(k):v for k,v in BINARIES.items()},'global_restriction_changed':False}));return
    evidence=Path('/var/lib/research-system')/('codex-userns-'+uuid.uuid4().hex);evidence.mkdir(mode=0o700)
    def run(args,allowed=(0,),cwd=None):
        result=subprocess.run(args,capture_output=True,cwd=cwd,timeout=30)
        name=str(len(list(evidence.glob('*.exit'))))
        (evidence/(name+'.stdout')).write_bytes(result.stdout);(evidence/(name+'.stderr')).write_bytes(result.stderr);(evidence/(name+'.exit')).write_text(str(result.returncode))
        if result.returncode not in allowed:raise ValueError('PROFILE_STEP_FAILED_'+name)
        return result
    try:group=grp.getgrnam('research-model-clients')
    except KeyError:
        run(['groupadd','--system','research-model-clients']);group=grp.getgrnam('research-model-clients')
    members=set(group.gr_mem)|{u.pw_name for u in pwd.getpwall() if u.pw_gid==group.gr_gid}
    if members-{'research-driver','research-reviewer'}:raise ValueError('UNEXPECTED_MODEL_CLIENT_MEMBER')
    for user in ['research-driver','research-reviewer']:run(['usermod','-a','-G','research-model-clients',user])
    # Only model-client identities can invoke the program receiving this exception.
    for path in BINARIES:os.chown(path,0,group.gr_gid);os.chmod(path,0o750)
    profile=Path(PROFILE)
    if profile.exists() or profile.is_symlink():
        if profile.is_symlink() or profile.stat().st_uid!=0 or profile.stat().st_mode & 0o022 or profile.read_text()!=POLICY:raise ValueError('EXISTING_PROFILE_RECONCILE_REQUIRED')
    else:
        profile.write_text(POLICY);profile.chmod(0o644)
    run(['apparmor_parser','--skip-kernel-load',PROFILE])
    run(['apparmor_parser','--replace',PROFILE])
    if restriction.read_text().strip()!='1':raise ValueError('GLOBAL_RESTRICTION_CHANGED')
    run(['runuser','-u','research-driver','--','codex','sandbox','linux','--','/usr/bin/true'],cwd='/srv/research-system/work')
    run(['runuser','-u','research-driver','--','test','-w','/home/research-driver'])
    fixture=Path('/srv/research-system/work')/('sandbox-fixture-'+uuid.uuid4().hex);fixture.mkdir(mode=0o700)
    run(['chown','research-driver:research-driver',str(fixture)])
    outside=Path('/home/research-driver')/('outside-sandbox-'+uuid.uuid4().hex)
    code="from pathlib import Path; import json; Path('inside.txt').write_text('synthetic'); p=Path("+repr(str(outside))+"); denied=False\ntry: p.write_text('synthetic')\nexcept OSError: denied=True\nprint(json.dumps({'inside_written':True,'outside_denied':denied})); raise SystemExit(0 if denied else 3)"
    result=run(['runuser','-u','research-driver','--','codex','sandbox','linux','--full-auto','--','/usr/bin/python3','-c',code],cwd=fixture)
    if json.loads(result.stdout)!={'inside_written':True,'outside_denied':True} or outside.exists():raise ValueError('FILESYSTEM_BOUNDARY_FAILED')
    denied=run(['runuser','-u','research-worker','--','test','-x',str(BASE/'bin/codex')],allowed=(1,))
    print(json.dumps({'status':'CODEX_SANDBOX_VERIFIED','cli_version':'0.153.4','profile':PROFILE,'binary_sha256':{str(k):v for k,v in BINARIES.items()},'global_userns_restriction':1,'inside_write':True,'outside_write_denied':True,'scientific_worker_cli_denied':denied.returncode==1,'model_called':False,'sudo_granted':False}))

if __name__=='__main__':main()
