#!/usr/bin/env python3
"""Install one supervised synthetic service fixture; never enable its timer.

Run as the setup administrator after source review. Existing installations are
refused, not repaired or overwritten. There is no writer credential, live ledger,
patient input or model invocation in this installer. Preserve partial setup and
reconcile it before retrying.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import subprocess
import sys
import tarfile


def validate_members(bundle):
    members=bundle.getmembers()
    if len(members)>2000 or sum(item.size for item in members)>20000000:
        raise ValueError('SOURCE_ARCHIVE_EXPANSION_LIMIT')
    for item in members:
        parts=Path(item.name).parts
        if not parts or parts[0]!='snapshot' or '..' in parts or Path(item.name).is_absolute():
            raise ValueError('SOURCE_ARCHIVE_ROOT')
        if not (item.isfile() or item.isdir()):raise ValueError('SOURCE_ARCHIVE_TYPE')


def install(source, archive, expected_sha256):
    if os.getuid()!=0 or not re.fullmatch('[0-9a-f]{40}',source):
        raise ValueError('SETUP_ADMIN_AND_PIN_REQUIRED')
    archive=Path(archive)
    if archive.is_symlink() or archive.stat().st_size>10000000:
        raise ValueError('BOUNDED_SOURCE_ARCHIVE_REQUIRED')
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected_sha256:
        raise ValueError('SOURCE_ARCHIVE_CHANGED')
    with tarfile.open(archive) as bundle:validate_members(bundle)
    release=Path('/opt/research-system/releases')/(source+'-handover')
    link=Path('/opt/research-system/handover')
    base=Path('/var/lib/research-system/handover-broker')
    state=Path('/var/lib/research-system/handover-controller')
    configdir=Path('/etc/research-system')
    units=['research-system-handover.socket','research-system-handover.service',
           'research-system-handover-controller.service']
    targets=[release,link,base,state,configdir/'handover-broker.json',
             configdir/'handover-controller.json',configdir/'handover-fixture-evidence.json',
             configdir/'handover-controls']
    targets += [Path('/etc/systemd/system')/unit for unit in units]
    if any(p.exists() or p.is_symlink() for p in targets):
        raise ValueError('EXISTING_SETUP_RECONCILE_NO_OVERWRITE')
    account=pwd.getpwnam('research-controller')
    # Existing runtime group only; no accounts, sign-ins or privilege grants.
    import grp
    gid=grp.getgrnam('research-runtime').gr_gid
    release.mkdir(mode=0o755);os.chmod(release,0o755)
    with tarfile.open(archive) as bundle:
        validate_members(bundle)
        bundle.extractall(release,filter='data')
    root=release/'snapshot'
    sys.path.insert(0,str(root))
    from orchestrator.remote_supervisor import checked_source
    from orchestrator.hosted_context import build
    from orchestrator.dispatch_limiter import GitLedger,initial,REF
    checked_source(root,source)
    build(root,{'trigger':'supervised service acceptance, no scientific authority'})
    link.symlink_to(root)
    base.mkdir(mode=0o700)
    state.mkdir(mode=0o700);os.chown(state,account.pw_uid,gid)
    ledger=base/'ledger';ledger.mkdir(mode=0o700)
    subprocess.run(['git','init','-q',str(ledger)],check=True)
    if not GitLedger(ledger).cas(None,initial()):raise ValueError('FIXTURE_LEDGER_CREATION_FAILED')
    controls=configdir/'handover-controls';controls.mkdir(mode=0o750);os.chown(controls,0,gid);os.chmod(controls,0o750)
    policy={'status':'RATIFIED','operator_approval':'SYNTHETIC_FIXTURE_ONLY_NOT_LIVE',
            'state_write_permission':'OPERATOR_AUTHORIZED','n':48,'window':'UTC_CALENDAR_DAY',
            'state_ref':REF,'reset_operators':['ssh-uid:0'],'server_semantics':'OPERATOR_AUTHORIZED_V1'}
    broker={'mode':'SYNTHETIC_FIXTURE','repository':'https://github.com/Moroseui/concept-research-scout.git',
            'branch':'astra/infrastructure-milestone-record','controller_uid':account.pw_uid,
            'operator_uids':[0],'sources':[source],'ledger_repo':str(ledger),
            'publication_root':str(base/'publication-disabled'),'policy':policy,'writer_config':None,
            'model_mode':'SUPERVISED','turn_root':str(base/'turns'),'max_model_turns':1}
    runtime={'purpose':'SUPERVISED_SERVICE_ACCEPTANCE','source_root':str(root),'source':source,
             'controller_uid':account.pw_uid,'controller_gid':gid,'state':str(state),
             'control_inbox':str(controls),'broker_socket':'/run/research-system/handover.sock',
             'report_schedule':{'zone':'UTC','hour':0,'minute':0,
                                'evidence_file':str(configdir/'handover-fixture-evidence.json')}}
    evidence={'source':source,'receipts':[],
              'task_state':{'scope':'One supervised service recovery fixture. No patient launch or live activation.',
                            'next_task':'Verify retained disposition after synthetic response loss without model replay.',
                            'research_queue':'Prediction charter, 047b reconciliation and evidence propagation remain queued.'}}
    for name,value in [('handover-broker.json',broker),('handover-controller.json',runtime),
                       ('handover-fixture-evidence.json',evidence)]:
        path=configdir/name
        with path.open('x') as stream:json.dump(value,stream,indent=2)
        os.chown(path,0,gid);os.chmod(path,0o640 if name!='handover-broker.json' else 0o600)
    for unit in units:
        raw=(root/'deploy/research-system'/unit).read_bytes()
        target=Path('/etc/systemd/system')/unit
        with target.open('xb') as stream:stream.write(raw)
        os.chmod(target,0o644)
    subprocess.run(['systemd-analyze','verify',*(str(Path('/etc/systemd/system')/u) for u in units)],check=True)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    return {'status':'INSTALLED_NOT_STARTED','source':source,'models_invoked':0,
            'writer_credentials':False,'live_state':False,'timer_enabled':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True);parser.add_argument('--archive',required=True)
    parser.add_argument('--archive-sha256',required=True)
    args=parser.parse_args()
    print(json.dumps(install(args.source,args.archive,args.archive_sha256)))
