#!/usr/bin/env python3
"""Install the reviewed Drive boundary only after a separate operator grant.

Fresh installation only. Does not enable/start the socket, fetch data, run a model,
change existing services, widen permissions or retry a partially completed setup.
All selected identities and original receipts remain private.
"""
import argparse
import grp
import hashlib
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess


def install(source_root, source, registration, consent, decision):
    if os.getuid()!=0:raise ValueError('SETUP_ADMIN_REQUIRED')
    from orchestrator.remote_supervisor import checked_source
    from orchestrator.phone_notifications import protected_read
    from orchestrator.drive_evidence import private_write,SCOPE
    root=checked_source(source_root,source)
    grant=json.loads(protected_read(decision))
    if (grant.get('status')!='OPERATOR_APPROVED' or grant.get('source')!=source
            or grant.get('scope')!=SCOPE or grant.get('capability')!='registered-drive-evidence-v1'):
        raise ValueError('EXACT_SEPARATE_DRIVE_PERMISSION_REQUIRED')
    registration,consent=Path(registration),Path(consent)
    config=json.loads(protected_read(registration/'config.json'))
    token=protected_read(consent/'oauth.json')
    if set(json.loads(token).get('scopes',[]))!={SCOPE}:raise ValueError('NARROW_TOKEN_REQUIRED')
    paths=[Path('/etc/research-system/drive'),Path('/var/lib/research-system/drive-evidence'),
           Path('/var/lib/research-system/drive-upload-spool'),Path('/opt/research-system/drive'),
           Path('/etc/systemd/system/research-system-drive.socket'),Path('/etc/systemd/system/research-system-drive.service')]
    if any(p.exists() or p.is_symlink() for p in paths):raise ValueError('EXISTING_INSTALLATION_RECONCILE_NO_RETRY')
    if not Path('/opt/research-system/drive-venv/bin/python').is_file():raise ValueError('PINNED_CLIENT_ENVIRONMENT_REQUIRED')
    for p in [root,*root.parents]:
        if p.stat().st_uid!=0 or p.stat().st_mode & 0o022:raise ValueError('ADMIN_OWNED_SOURCE_REQUIRED')
    # No sudo grant, supplementary administration groups, or interactive password.
    try: identity=pwd.getpwnam('research-drive')
    except KeyError:
        subprocess.run(['useradd','--system','--user-group','--no-create-home','--shell','/usr/sbin/nologin','research-drive'],check=True)
        identity=pwd.getpwnam('research-drive')
    if identity.pw_uid==0 or identity.pw_shell!='/usr/sbin/nologin':raise ValueError('DEDICATED_NONROOT_IDENTITY_REQUIRED')
    admin=paths[0];admin.mkdir(mode=0o700)
    private_write(admin/'installation-intent.json',{'source':source,'grant_sha256':hashlib.sha256(protected_read(decision)).hexdigest()})
    config['installed_source']=source
    private_write(admin/'config.json',config)
    with (admin/'oauth.json').open('xb') as out:os.chmod(out.name,0o600);out.write(token)
    paths[1].mkdir(mode=0o700);os.chown(paths[1],identity.pw_uid,identity.pw_gid)
    paths[2].mkdir(mode=0o750);os.chown(paths[2],pwd.getpwnam('research-controller').pw_uid,identity.pw_gid)
    paths[3].symlink_to(root,target_is_directory=True)
    for name in ('research-system-drive.socket','research-system-drive.service'):
        raw=(root/'deploy/research-system'/name).read_bytes()
        with (Path('/etc/systemd/system')/name).open('xb') as out:out.write(raw)
        (Path('/etc/systemd/system')/name).chmod(0o644)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    private_write(admin/'installation-receipt.json',{'status':'INSTALLED_NOT_STARTED','source':source,'uid':identity.pw_uid,
                  'socket_started':False,'data_transferred':False,'unattended_activation':False})
    print(json.dumps({'status':'INSTALLED_NOT_STARTED','source':source,'uid':identity.pw_uid}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source-root','source','registration','consent','decision'):p.add_argument('--'+name,required=True)
    a=p.parse_args();install(a.source_root,a.source,a.registration,a.consent,a.decision)
