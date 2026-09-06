#!/usr/bin/env python3
"""Bounded root bootstrap: pinned sparse source, fixed synthetic units, no credentials."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import urllib.request

REPOSITORY='https://github.com/Moroseui/concept-research-scout.git'
BRANCH='refs/heads/astra/infrastructure-milestone-record'
NODE_VERSION='v22.23.2'
PATTERNS=['/.gitignore','/orchestrator/','/deploy/research-system/','/docs/operations/',
          '/campaigns/isles24-pilot/colab/smoke.py','/configs/pilot/dispatch-limiter.json']

def run(*args,**kw):return subprocess.run(args,check=True,**kw)
def output(*args,**kw):return subprocess.check_output(args,text=True,**kw).strip()

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--nonroot-access-verified',action='store_true');a=p.parse_args()
    if os.getuid()!=0 or not re.fullmatch('[0-9a-f]{40}',a.source):raise ValueError('ROOT_AND_EXACT_SOURCE_REQUIRED')
    if output('git','ls-remote',REPOSITORY,BRANCH).split()!=[a.source,BRANCH]:raise ValueError('PUBLIC_SOURCE_MOVED')
    root=Path('/opt/research-system');release=root/'releases'/a.source
    if release.exists():raise ValueError('RELEASE_ALREADY_EXISTS_RECONCILE_BEFORE_RETRY')
    release.mkdir(parents=True,mode=0o755)
    run('git','init','-q',str(release));run('git','-C',str(release),'remote','add','origin',REPOSITORY)
    run('git','-C',str(release),'fetch','--no-tags','--depth=1','--filter=blob:none','origin',a.source)
    run('git','-C',str(release),'sparse-checkout','init','--no-cone')
    run('git','-C',str(release),'sparse-checkout','set','--no-cone',*PATTERNS)
    run('git','-C',str(release),'checkout','--detach',a.source)
    # No patient paths, histories, credentials or entire results branch acquired.
    if (release/'probes').exists() or (release/'results').exists():raise ValueError('UNEXPECTED_PATIENT_TREE')
    current=root/'current'
    if current.exists() or current.is_symlink():raise ValueError('CURRENT_RELEASE_ALREADY_SET')
    current.symlink_to(release)
    # Ubuntu's default Node 18 does not satisfy the installed Claude >=22 engine.
    name='node-'+NODE_VERSION+'-linux-x64';tools=root/'tools';tools.mkdir(exist_ok=True)
    archive=tools/(name+'.tar.xz')
    base='https://nodejs.org/dist/'+NODE_VERSION+'/'
    sums=urllib.request.urlopen(base+'SHASUMS256.txt',timeout=60).read().decode()
    sha=next(line.split()[0] for line in sums.splitlines() if line.split()[-1]==archive.name)
    raw=urllib.request.urlopen(base+archive.name,timeout=120).read()
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('NODE_DOWNLOAD_IDENTITY')
    if archive.exists():raise ValueError('NODE_ARCHIVE_ALREADY_EXISTS')
    archive.write_bytes(raw)
    with tarfile.open(archive) as tar:tar.extractall(tools,filter='data')
    link=Path('/usr/local/bin/node')
    if link.exists() or link.is_symlink():raise ValueError('UNEXPECTED_LOCAL_NODE')
    link.symlink_to(tools/name/'bin/node')
    if output('node','--version')!=NODE_VERSION:raise ValueError('NODE_VERSION_MISMATCH')
    config=Path('/etc/research-system');config.mkdir(exist_ok=True)
    (config/'source.env').write_text('SOURCE='+a.source+'\n')
    (config/'bootstrap-policy.json').write_text(json.dumps({'mode':'SUPERVISED_SYNTHETIC_ONLY','source':a.source,'branch':BRANCH,'max_fixture_jobs':16,'patient_allowed':False,'model_dispatch_allowed':False,'limiter_active':False,'driver_model':'gpt-6-astra'},indent=2)+'\n')
    for unit in (release/'deploy/research-system').glob('research-system-*.service'):
        shutil.copyfile(unit,Path('/etc/systemd/system')/unit.name)
    for unit in (release/'deploy/research-system').glob('research-system-*.timer'):
        shutil.copyfile(unit,Path('/etc/systemd/system')/unit.name)
    for user in ['research-driver','research-reviewer']:
        home=Path('/home')/user
        if user=='research-driver':
            folder=home/'.codex';folder.mkdir(mode=0o700,exist_ok=True)
            f=folder/'config.toml'
            if not f.exists():f.write_text('model = "gpt-6-astra"\napproval_policy = "never"\nsandbox_mode = "workspace-write"\n')
            run('chown','-R',user+':'+user,str(folder))
    # No sudo rules for agents and no model/publication credentials installed.
    if a.nonroot_access_verified:
        (config/'nonroot-access-verified').write_text('Operator-key non-root login verified before firewall setup.\n')
        run('bash',str(release/'deploy/research-system/bootstrap.sh'),'firewall')
    run('systemd-analyze','verify','/etc/systemd/system/research-system-controller.service','/etc/systemd/system/research-system-worker.service')
    run('systemctl','daemon-reload')
    run('systemctl','enable','--now','research-system-controller.timer','research-system-worker.timer')
    print(json.dumps({'source':a.source,'sparse_patterns':PATTERNS,'node':NODE_VERSION,'node_archive_sha256':sha,'mode':'SUPERVISED_SYNTHETIC_ONLY','model_credentials_installed':False,'patient_data_transferred':False}))

if __name__=='__main__':main()
