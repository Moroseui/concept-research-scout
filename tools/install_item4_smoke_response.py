"""Install the approved narrow host gate in its own held release; never launch."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

CHANGE='item4-diagnostic-native-harness-20261010'
REVIEW_CHANGE='item4-diagnostic-native-harness-20261010'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR_UNIT=Path('/etc/systemd/system/research-item4-diagnostic-scoped-review-20261010.service')
PRIOR_UNIT_SHA='d4460ff71c817dd4ada6eda2e3cb861284a07cf60045b5cb5913a999694561dc'
UNIT=Path('/etc/systemd/system')/('research-'+CHANGE+'.service')
ENGINE=Path('/opt/research-system/autonomy-review/d08b91bdc1d0')
RUNTIME='/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('EXECUTION_BILLING_INSTALL_'+why)


def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        st=p.lstat();require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'TRUSTED_SOURCE')
    return path


def unit_bytes(raw):
    require(sha(raw)==PRIOR_UNIT_SHA,'PRIOR_UNIT_CHANGED')
    before='ExecStart=/usr/bin/python3 -s -B /opt/research-system/manual-repair-helpers/item4-diagnostic-scoped-review-20261010/tools/item4_smoke_response_runtime.py run'
    after='ExecStart=/usr/bin/python3 -s -B '+str(ROOT/'tools/item4_smoke_response_runtime.py')+' run'
    body=raw.decode();require(body.count(before)==1,'PRIOR_UNIT_SHAPE')
    return body.replace(before,after).replace('Description=Reviewed experiment authoring (execution provisioning held)',
        'Description=Reviewed coverage-independent validation transition').encode()



def retention_units(rendered):
    # Existing R57 retention remains active; no duplicate watcher or timer.
    return {UNIT:rendered}


def verify_units(units):
    """Parse every exact rendered unit before the first installation write."""
    import tempfile
    with tempfile.TemporaryDirectory(prefix='item4-reviewed-unit-check-') as folder:
        files=[]
        for destination,raw in units.items():
            path=Path(folder)/destination.name
            with path.open('xb') as stream:stream.write(raw)
            path.chmod(0o600);files.append(str(path))
        result=subprocess.run(['systemd-analyze','verify',*files],text=True,capture_output=True)
        require(result.returncode==0,'RENDERED_UNIT_INVALID: '+result.stderr)


def put(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with path.open('xb') as f:f.write(raw)
    os.chown(path,0,1003);path.chmod(0o440)


def install(source,review,direction):
    require(os.geteuid()==0,'ROOT_REQUIRED')
    source=trusted(source);review=Path(review)
    retention_service=UNIT.with_name('research-'+CHANGE+'-retention.service')
    retention_timer=UNIT.with_name('research-'+CHANGE+'-retention.timer')
    require(not any(p.exists() or p.is_symlink() for p in (ROOT,RECORD,UNIT,retention_service,retention_timer)),'EXISTS_RECONCILE')
    sys.path.insert(0,str(ENGINE))
    from orchestrator.autonomy_review import verify_result
    delegated=verify_result(direction)
    require(delegated['verdict']=='APPROVE' and delegated['change_id']=='item4-author16-entrypoint-recovery-20261010'
        and delegated['source_sha']=='7dc3d1da418c0e7c53aae65ea14739e9b686221d'
        and delegated['report_sha256']=='ddcdc756df490d35c42784b8ede667be783ca72a2161bb938c4888745a43b9ca','RECOVERY_DIRECTION_APPROVE')
    approved=verify_result(review)
    require(approved['verdict']=='APPROVE' and approved['change_id']==REVIEW_CHANGE,'GENUINE_IMPLEMENTATION_APPROVE')
    manifest=json.loads((review/'packet-manifest.json').read_bytes())
    require(manifest['source_sha']==approved['source_sha'],'SOURCE_BINDING')
    policy_path=trusted(source/'tools/item4_smoke_response_runtime.py')
    require(sha(policy_path.read_bytes())==manifest['source_files']['tools/item4_smoke_response_runtime.py'],'POLICY_SOURCE')
    spec=importlib.util.spec_from_file_location('_validation_install_policy',policy_path)
    policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
    bodies={name:trusted(source/name).read_bytes() for name in policy.FILES}
    require(all(sha(raw)==manifest['source_files'][name] for name,raw in bodies.items()),'EXACT_REVIEWED_SOURCE')
    require(bodies['tools/install_item4_smoke_response.py']==Path(__file__).read_bytes(),'EXECUTED_INSTALLER')
    props=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',PRIOR_UNIT.name,
        '-p','ActiveState','-p','MainPID','-p','ControlGroup'],text=True).splitlines())
    require(props.get('MainPID')=='0' and props.get('ControlGroup')=='' and props.get('ActiveState') in {'inactive','failed'},'PRIOR_ACTIVE')
    rendered=unit_bytes(trusted(PRIOR_UNIT).read_bytes())
    units=retention_units(rendered)
    verify_units(units)
    inputs={}
    # No ledger is opened by root. The existing activated R45 seal stays intact;
    # this held installation does not activate or dispatch any work.
    put(RECORD/'INSTALL_INTENT.json',json.dumps({'source':approved['source_sha'],'review_sha256':approved['report_sha256']},sort_keys=True).encode())
    for name,raw in bodies.items():put(ROOT/name,raw)
    for dest,origin in [('review',review),('direction',Path(direction))]:
        for path in origin.iterdir():
            require(path.is_file() and not path.is_symlink(),'REVIEW_MEMBER')
            put(RECORD/dest/path.name,path.read_bytes())
    for path,raw in units.items():put(path,raw)
    for name,raw in inputs.items():put(RECORD/'inputs'/name,raw)
    installed={'schema':'item4-execution-billing-install/v1','source':approved['source_sha'],
        'review_sha256':approved['report_sha256'],'files':{name:sha(raw) for name,raw in bodies.items()},
        'units':{str(path):sha(raw) for path,raw in units.items()},'status':'INSTALLED_HELD'}
    put(RECORD/'installed.json',json.dumps(installed,sort_keys=True).encode())
    for root in (ROOT,RECORD):
        for path in [root,*[p for p in root.rglob('*') if p.is_dir()]]:
            os.chown(path,0,1003);path.chmod(0o550)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    cmd=['runuser','-u','partho','--','env','RESEARCH_MANUAL_RUNTIME_CONFIG='+RUNTIME,
        'PYTHONDONTWRITEBYTECODE=1','python3','-s','-B',str(ROOT/'tools/item4_smoke_response_runtime.py'),'verify']
    result=subprocess.run(cmd,capture_output=True,text=True)
    put(RECORD/'VERIFY.stdout',result.stdout.encode());put(RECORD/'VERIFY.stderr',result.stderr.encode())
    require(result.returncode==0,'POSTINSTALL_VERIFY')
    put(RECORD/'COMPLETE.json',b'{"status":"INSTALLED_HELD","model_calls":0,"provider_calls":0}')
    return {'status':'INSTALLED_HELD','model_calls':0,'provider_calls':0}

if __name__=='__main__':
    os.umask(0o077);p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--review',required=True);p.add_argument('--direction',required=True);a=p.parse_args()
    print(json.dumps(install(a.source,a.review,a.direction),sort_keys=True))
