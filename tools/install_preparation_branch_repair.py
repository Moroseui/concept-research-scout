"""Install a separately approved held continuation; never reset existing lanes."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

CHANGE='preparation-branch-admission-repair-20261010'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
ORIGINAL_ROOT=Path('/opt/research-system/manual-repair-helpers/preparation-and-cap-repair-20261010')
ORIGINAL_RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/preparation-and-cap-repair-20261010')
ORIGINAL_SOURCE='304cae4aa12d53eb99254499950eec4e71df8075'
ENGINE=Path('/opt/research-system/autonomy-review/d08b91bdc1d0')
LANES=('aggregate_analysis','colab_preparation')
UNIT_DIR=Path('/etc/systemd/system')
RUNTIME=Path('/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json')

def require(ok,why):
    if not ok:raise ValueError('PREPARATION_BRANCH_INSTALL_'+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def trusted(path):
    p=Path(path)
    for q in [p,*p.parents]:
        s=q.lstat();require(not q.is_symlink() and s.st_uid==0 and not s.st_mode&0o022,'TRUSTED_PATH')
    return p

def relative(name):
    p=Path(name);require(isinstance(name,str) and name and not p.is_absolute() and '..' not in p.parts and str(p)==name,'RELATIVE_PATH');return p

def mkdir(path):
    Path(path).mkdir();os.chown(path,0,1003);Path(path).chmod(0o550)
def put(path,raw):
    path=Path(path);missing=[];parent=path.parent
    while not parent.exists():missing.append(parent);parent=parent.parent
    trusted(parent)
    for parent in reversed(missing):mkdir(parent)
    with path.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    os.chown(path,0,1003);path.chmod(0o440)

def unit_bytes(raw,key):
    require(key in LANES,'NAMED_LANE')
    original='ExecStart=/usr/bin/python3 -s -B '+str(ORIGINAL_ROOT/'tools/preparation_scientific_runtime.py')+' advance --scope '+str(ORIGINAL_RECORD/'preparation-interleaving.json')+' --review-report '+str(ORIGINAL_RECORD/'review/report.md')+' --lane '+key
    replacement='ExecStart=/usr/bin/python3 -s -B '+str(ROOT/'tools/preparation_branch_repair_runtime.py')+' advance --lane '+key
    lines=raw.decode().splitlines(keepends=True)
    require(lines.count(original+'\n')==1 and sum(x.startswith('ExecStart=') for x in lines)==1,'EXACT_PRIOR_ENTRY')
    changed=raw.replace((original+'\n').encode(),(replacement+'\n').encode())
    require(changed.replace((replacement+'\n').encode(),(original+'\n').encode())==raw,'ENTRY_ONLY_CHANGE')
    return changed

OWNER_CHECK="""import os,sqlite3,json
assert os.getuid()==os.getgid()==1003
with sqlite3.connect('file:/var/lib/research-system-autonomy/reviews/jobs.sqlite?mode=ro',uri=True) as db:
 assert not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone()
print(json.dumps({'status':'NO_RUNNING_CALL','ledger_writes':0}))
"""

def install(source,review):
    require(os.getuid()==0 and sys.flags.no_user_site,'ROOT_ISOLATED_REQUIRED')
    source,review=map(trusted,(source,review));sys.path.insert(0,str(ENGINE))
    from orchestrator.autonomy_review import verify_result
    approval=verify_result(review);manifest=json.loads(trusted(review/'packet-manifest.json').read_bytes())
    require(approval['verdict']=='APPROVE' and not approval.get('findings') and approval['change_id']==CHANGE,'GENUINE_APPROVAL')
    bodies={name:trusted(source/relative(name)).read_bytes() for name in manifest['source_files']}
    require(all(sha(raw)==manifest['source_files'][name] for name,raw in bodies.items()),'REVIEWED_SOURCE')
    require(bodies['tools/install_preparation_branch_repair.py']==Path(__file__).read_bytes(),'EXECUTED_INSTALLER')
    for name in ['tools/preparation_branch_repair_runtime.py','tools/preparation_branch_repair_host.py','tools/preparation_premodel_recovery.py','orchestrator/preparation_interleaving.py']:
        require(name in bodies,'WHOLE_CONTINUATION_COMPONENT')
    old=verify_result(trusted(ORIGINAL_RECORD/'review'))
    require(old['source_sha']==ORIGINAL_SOURCE and old['verdict']=='APPROVE','ORIGINAL_APPROVAL')
    old_manifest=json.loads(trusted(ORIGINAL_RECORD/'review/packet-manifest.json').read_bytes())
    old_receipt=json.loads(trusted(ORIGINAL_RECORD/'installed.json').read_bytes())
    require(old_receipt['source']==ORIGINAL_SOURCE and old_receipt['review_sha256']==old['report_sha256'] and old_receipt['root']==str(ORIGINAL_ROOT),'ORIGINAL_INSTALL_BINDING')
    for name,pin in old_manifest['source_files'].items():require(sha(trusted(ORIGINAL_ROOT/name).read_bytes())==pin,'ORIGINAL_SOURCE_CHANGED')
    spec=importlib.util.spec_from_file_location('_original_preparation_installer',trusted(ORIGINAL_ROOT/'tools/install_preparation_runtime.py'))
    prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior);prior.standalone_git(source)
    git=lambda *args:subprocess.check_output(['git',*args],cwd=source,text=True).strip()
    require(git('rev-parse','HEAD')==approval['source_sha'] and re.fullmatch(r'astra/manual-[a-z0-9-]+',git('branch','--show-current')) is not None and not git('status','--porcelain'),'CLEAN_SOURCE')
    units={}
    for key in LANES:
        path=UNIT_DIR/('research-preparation-and-cap-repair-20261010-'+key+'.service')
        raw=trusted(path).read_bytes();require(sha(raw)==old_receipt['units'][str(path)],'ORIGINAL_UNIT_CHANGED')
        state=dict(line.split('=',1) for line in subprocess.check_output(['systemctl','show',path.name,'-p','MainPID','-p','ActiveState'],text=True).splitlines())
        require(state=={'MainPID':'0','ActiveState':'inactive'},'ORIGINAL_UNIT_NOT_HELD')
        units[path.with_name('research-'+CHANGE+'-'+key+'.service')]=unit_bytes(raw,key)
    for target in [ROOT,RECORD,*units]:
        trusted(target.parent);require(not target.exists() and not target.is_symlink(),'DESTINATION_EXISTS')
    review_files={p.name:trusted(p).read_bytes() for p in review.iterdir() if p.is_file()}
    require(len(review_files)==len(list(review.iterdir())),'FLAT_REVIEW')
    check=json.loads(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',OWNER_CHECK],text=True));require(check['status']=='NO_RUNNING_CALL','LIVE_CALL')
    prior.verify_units(units)
    mkdir(RECORD);put(RECORD/'INSTALL_INTENT.json',json.dumps({'source':approval['source_sha'],'review_sha256':approval['report_sha256'],'original_source':ORIGINAL_SOURCE},sort_keys=True).encode())
    mkdir(ROOT)
    for name,raw in bodies.items():put(ROOT/relative(name),raw)
    for name,raw in review_files.items():put(RECORD/'review'/name,raw)
    for path,raw in units.items():put(path,raw)
    installed={'root':str(ROOT),'source':approval['source_sha'],'review_sha256':approval['report_sha256'],'files':manifest['source_files'],'units':{str(p):sha(raw) for p,raw in units.items()},'status':'INSTALLED_HELD'}
    put(RECORD/'installed.json',json.dumps(installed,sort_keys=True).encode());subprocess.run(['systemctl','daemon-reload'],check=True)
    result=subprocess.run(['runuser','-u','partho','--','env','PYTHONPATH='+str(ORIGINAL_ROOT),'PYTHONDONTWRITEBYTECODE=1','RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),'python3','-s','-B',str(ROOT/'tools/preparation_branch_repair_runtime.py'),'verify'],capture_output=True)
    put(RECORD/'VERIFY.stdout',result.stdout);put(RECORD/'VERIFY.stderr',result.stderr);require(result.returncode==0,'SERVICE_ACCOUNT_VERIFY_FAILED')
    complete={'status':'INSTALLED_HELD','source':approval['source_sha'],'scientific_calls':0,'provider_calls':0};put(RECORD/'COMPLETE.json',json.dumps(complete,sort_keys=True).encode());return complete

if __name__=='__main__':
    os.umask(0o077);parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--review',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(install(args.source,args.review),sort_keys=True))
