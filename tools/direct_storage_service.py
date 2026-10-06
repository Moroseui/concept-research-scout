"""Provision only new, source-bound direct-input supervisor files, disabled.

The versioned promoter installs/reviews code first. This additive provisioner
never touches old services, previous releases, credentials or ledger contents.
Daemon-reload and enabling remain explicit recorded deployment operations.
"""
from pathlib import Path
import hashlib
import json
import os
import pwd
import re
import stat
from orchestrator.modal_executor import canonical


def safe(value):
    if not isinstance(value,str) or not re.fullmatch('/(?:opt|etc|var/lib)/[A-Za-z0-9_./-]+',value) or '..' in Path(value).parts:
        raise ValueError('DIRECT_UNIT_PATH')
    return value


def rendered(config,config_path):
    for value in [config_path,config['release'],config['state'],config['batch_ledger'],config['provider']['sdk_package']]:safe(value)
    release,state,ledger,sdk=(config['release'],config['state'],config['batch_ledger'],config['provider']['sdk_package'])
    service=f"""[Unit]
Description=Verified development input retrieval and retention
After=network-online.target
Wants=network-online.target
[Service]
Type=oneshot
User=partho
Group=partho
UMask=0077
WorkingDirectory={release}
Environment=PYTHONPATH={release}:{sdk}
Environment=RESEARCH_MANUAL_RUNTIME_CONFIG=/etc/research-system-manual-sprint10/releases/{Path(release).name}/runtime.json
ExecStart=/usr/bin/python3 -s -B -m orchestrator.modal_direct_storage --config {config_path}
TimeoutStartSec=900
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=true
ReadWritePaths={state} {ledger}
RestrictSUIDSGID=true
LockPersonality=true
[Install]
WantedBy=multi-user.target
"""
    timer="""[Unit]
Description=Observe development input retrieval and enforce retention
[Timer]
OnBootSec=2min
OnUnitInactiveSec=5min
AccuracySec=15s
[Install]
WantedBy=timers.target
"""
    return service.encode(),timer.encode()


def install(root,config):
    """Scratch root uses the same file generation/refusal path; no systemctl."""
    root=Path(root).resolve()
    live=root==Path('/')
    if live and os.getuid()!=0:raise ValueError('DIRECT_INSTALL_ROOT_REQUIRED')
    # Account prerequisite before the first write, including scratch tests.
    user=pwd.getpwnam('partho')
    if live and (user.pw_uid,user.pw_gid)!=(1003,1003):raise ValueError('DIRECT_INSTALL_ACCOUNT')
    def at(value):
        safe(value);p=root/value.lstrip('/')
        if any(x.is_symlink() for x in [p,*p.parents]):raise ValueError('DIRECT_INSTALL_ALIAS')
        return p
    source=config['source']
    if not re.fullmatch('[0-9a-f]{40}',source):raise ValueError('DIRECT_INSTALL_SOURCE')
    name='research-manual-sprint10-direct-inputs-'+source[:12]
    directory='/etc/research-system-manual-sprint10/direct-inputs/'+source
    config_path=directory+'/config.json'
    state=config['state'];safe(state)
    if not state.startswith('/var/lib/research-system-manual-sprint10/direct-inputs/'):
        raise ValueError('DIRECT_INSTALL_STATE_SCOPE')
    if 'prepared_from' not in config and state!=('/var/lib/research-system-manual-sprint10/direct-inputs/'+source):raise ValueError('DIRECT_INSTALL_STATE_BINDING')
    if set(config)-{'prepared_from'}!={'schema','source','release','installation_record','installation_sha256','package',
                     'package_manifest_sha256','batch_ledger','state','provider'}:
        raise ValueError('DIRECT_INSTALL_CONFIG_FIELDS')
    if config['schema']!='direct-development-storage/v1':raise ValueError('DIRECT_INSTALL_SCHEMA')
    from tools.manual_promotion import manifest_check
    installed=at(config['installation_record'])/'installed.json'
    if hashlib.sha256(installed.read_bytes()).hexdigest()!=config['installation_sha256']:
        raise ValueError('DIRECT_INSTALL_RECEIPT_PIN')
    receipt=manifest_check(root,config['installation_record'])
    if receipt['source']!=source or receipt['layout']['release']!=config['release']:
        raise ValueError('DIRECT_INSTALL_RELEASE_BINDING')
    if not (at(config['release'])/'orchestrator/modal_direct_storage.py').is_file():raise ValueError('DIRECT_INSTALL_SOURCE_MISSING')
    # The real verified package is separately root-preserved after source review.
    from orchestrator.modal_download_package import verify
    verify(at(config['package']),config['package_manifest_sha256'])
    if not at(config['batch_ledger']).is_dir():raise ValueError('DIRECT_INSTALL_LEDGER_MISSING')
    services={name+'.service':None,name+'.timer':None}
    service,timer=rendered(config,config_path)
    values=dict(zip(services,(service,timer)))
    final={**config,'units':{n:{'sha256':hashlib.sha256(v).hexdigest()} for n,v in values.items()}}
    continuation=None
    if 'prepared_from' in config:
        from orchestrator.modal_direct_continuation import preflight
        continuation=preflight(config,root=root)
    destinations=[at(directory),*[at('/etc/systemd/system/'+n) for n in values]]
    if continuation is None:destinations.append(at(state))
    if any(p.exists() for p in destinations):raise ValueError('DIRECT_INSTALL_DESTINATION_EXISTS')
    # Every path and complete source/package pin has passed before any write.
    def mkdir(p,owner=False):
        if not p.parent.exists():mkdir(p.parent)
        if p.exists():return
        p.mkdir(mode=0o700)
        if live:
            os.chown(p,1003 if owner else 0,1003);os.chmod(p,0o700 if owner else 0o750)
    def write(p,raw):
        fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
        if live:os.chown(p,0,1003);os.chmod(p,0o440)
        from orchestrator.private_records import check
        check(p)
    mkdir(at(directory))
    if continuation is None:mkdir(at(state),owner=True)
    for name,raw in values.items():write(at('/etc/systemd/system/'+name),raw)
    write(at(config_path),canonical(final))
    hashes={str(p.relative_to(root)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
            for p in [at(config_path),*[at('/etc/systemd/system/'+n) for n in values]]}
    result={'source':source,'config':config_path,'state':state,'files':hashes,
            'units':list(values),'installed_disabled':True,'systemctl_operations':0,
            'preparation_continuation':continuation}
    write(at(directory+'/installation.json'),canonical(result))
    for name,item in hashes.items():
        p=root/name
        if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256'] or stat.S_IMODE(p.stat().st_mode)!=item['mode']:
            raise ValueError('DIRECT_INSTALL_POSTCHECK')
    return result
