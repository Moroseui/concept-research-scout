"""Install exact genuinely approved author5 component, held; no model launch."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

CHANGE = 'item4-author-submission-20261008'
ROOT = Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD = Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
REVIEW_ENGINE = Path('/opt/research-system/autonomy-review/b71912e6cfbf')
SCIENCE = Path('/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
RUNTIME = Path('/etc/research-system-manual-sprint10/releases')/SCIENCE.name/'runtime.json'
OLD_UNIT = Path('/etc/systemd/system/research-daily50-and-image-probe-20261007-item4.service')
UNIT = Path('/etc/systemd/system')/('research-'+CHANGE+'.service')
AUTHORITY = '40b6529f29e9710bae217cfb84cf213caa601f99d84aa48b3259e3dba73f3fc7'
MODULES = ('experiment_plan_validation','experiment_plan_output','experiment_context','author_format_submission')
FILES = tuple('orchestrator/'+n+'.py' for n in MODULES) + (
    'tools/item4_author_submission_component.py','tools/install_item4_author_submission.py',
    'tools/ITEM4_AUTHOR5_BINDINGS.json','docs/ITEM4_AUTHOR5_OPERATOR_APPROVAL_20261008.txt')


def require(ok, why):
    if not ok: raise ValueError(why)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def trusted(path):
    path = Path(path)
    for p in [path,*path.parents]:
        st = p.lstat()
        require(not p.is_symlink() and st.st_uid == 0 and not st.st_mode & 0o022, 'AUTHOR_INSTALL_UNTRUSTED')
    return path


def unit_bytes(original):
    before = 'ExecStart=/usr/bin/python3 -s -B /opt/research-system/manual-repair-helpers/daily-limit-and-image-probe-20261007/tools/daily_limit_component.py 4'
    after = 'ExecStart=/usr/bin/python3 -s -B '+str(ROOT/'tools/item4_author_submission_component.py')+' run'
    require(original.count(before) == 1, 'AUTHOR_INSTALL_UNIT_SHAPE')
    return original.replace(before, after).encode()


def put(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open('xb') as f:f.write(raw)
    os.chown(path,0,1003);os.chmod(path,0o440)


def install(packet, review, source):
    require(os.getuid() == 0, 'AUTHOR_INSTALL_ROOT_REQUIRED')
    sys.path.insert(0,str(REVIEW_ENGINE))
    from orchestrator import autonomy_review as ar
    m=ar.verify_packet(packet);a=ar.verify_result(review)
    require(a['verdict']=='APPROVE' and a['source_sha']==m['source_sha']==source and
            a['change_id']==m['change_id']==CHANGE and a['runtime_sha256']==sha(trusted(RUNTIME).read_bytes()),
            'AUTHOR_INSTALL_GENUINE_APPROVAL_REQUIRED')
    require(ar.canonical(m)==ar.canonical(json.loads((Path(review)/'packet-manifest.json').read_bytes())), 'AUTHOR_INSTALL_REVIEW_PACKET_BINDING')
    require(not ROOT.exists() and not RECORD.exists() and not UNIT.exists(), 'AUTHOR_INSTALL_EXISTS_INSPECT')
    bodies={name:(Path(packet)/'source'/name).read_bytes() for name in FILES}
    require(all(sha(raw)==m['source_files'][name] for name,raw in bodies.items()), 'AUTHOR_INSTALL_SOURCE_CHANGED')
    require(bodies['tools/install_item4_author_submission.py']==Path(__file__).read_bytes(), 'AUTHOR_INSTALLER_NOT_REVIEWED')
    require(sha(bodies['docs/ITEM4_AUTHOR5_OPERATOR_APPROVAL_20261008.txt'])==AUTHORITY, 'AUTHOR_INSTALL_AUTHORITY')
    require(json.loads(bodies['tools/ITEM4_AUTHOR5_BINDINGS.json'])['authority_sha256']==AUTHORITY, 'AUTHOR_INSTALL_AUTHORITY_BINDING')
    properties=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',OLD_UNIT.name,
        '--property=ActiveState,MainPID,ControlGroup'],text=True).splitlines())
    require(properties=={'ActiveState':'inactive','MainPID':'0','ControlGroup':''}, 'AUTHOR_EXISTING_SERVICE_ACTIVE')
    original=trusted(OLD_UNIT).read_bytes();unit=unit_bytes(original.decode())
    daily=Path('/opt/research-system/manual-repair-helpers/daily-limit-and-image-probe-20261007/tools/daily_limit_component.py')
    baseline=[daily, *(SCIENCE/'orchestrator'/(name+'.py') for name in (
        'manual_stage','manual_isolation','manual_driver','manual_executor','experiment_driver',
        'experiment_plan_validation','experiment_plan_output','experiment_context'))]
    pins={str(p):sha(trusted(p).read_bytes()) for p in baseline}
    trusted(ROOT.parent);trusted(RECORD.parent);trusted(UNIT.parent)
    # Every original unit, file and credential remains unchanged.
    ROOT.mkdir(mode=0o700);RECORD.mkdir(mode=0o700)
    put(RECORD/'INSTALL_INTENT.json',json.dumps({'source':source,'review':a,'scope':'held author5 only; no model or provider launch'},sort_keys=True).encode())
    for name,raw in bodies.items():put(ROOT/name,raw)
    for path in Path(review).iterdir():
        require(path.is_file() and not path.is_symlink(), 'AUTHOR_REVIEW_ORIGINAL_FILE')
        put(RECORD/'review'/path.name,path.read_bytes())
    put(RECORD/'prior-unit.txt',original)
    put(UNIT,unit);os.chown(UNIT,0,0);os.chmod(UNIT,0o644)
    receipt={'schema':'reviewed-author5-component/v1','root':str(ROOT),'source':source,
        'review_folder':str(RECORD/'review'),'review_sha256':a['report_sha256'],
        'files':{n:sha(raw) for n,raw in bodies.items()},'base_files':pins,
        'units':{str(OLD_UNIT):sha(original),str(UNIT):sha(unit)}}
    put(RECORD/'installed.json',json.dumps(receipt,sort_keys=True).encode())
    for root in [ROOT,RECORD]:
        for path in [root,*[p for p in root.rglob('*') if p.is_dir()]]:os.chown(path,0,1003);os.chmod(path,0o550)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    command=['runuser','-u','partho','--','env','PYTHONPATH='+str(SCIENCE),
        'RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),'PYTHONDONTWRITEBYTECODE=1',
        'python3','-s','-B',str(ROOT/'tools/item4_author_submission_component.py')]
    # Qualification precedes recovery; neither action launches a model.
    for action in ['verify','apply']:
        result=subprocess.run(command+[action],capture_output=True,text=True,timeout=180)
        put(RECORD/(action+'.stdout'),result.stdout.encode());put(RECORD/(action+'.stderr'),result.stderr.encode())
        require(result.returncode==0, 'AUTHOR_INSTALL_POSTCHECK_'+action.upper())
    put(RECORD/'APPLIED.json',json.dumps({'status':'INSTALLED_HELD','source':source,'review_sha256':a['report_sha256'],'model_calls':0},sort_keys=True).encode())
    return {'status':'INSTALLED_HELD','model_calls':0,'unit':UNIT.name}


if __name__=='__main__':
    os.umask(0o077)
    p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--source',required=True);args=p.parse_args()
    print(json.dumps(install(args.packet,args.review,args.source),sort_keys=True))
