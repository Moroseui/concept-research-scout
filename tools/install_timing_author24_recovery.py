"""Install one held author24 successor; preserve the failed unit and all usage."""
import argparse,hashlib,importlib.util,json,os,re,subprocess,sys
from pathlib import Path
CHANGE='timing-author24-preparation-recovery-20261010'
REVIEW_CHANGE='rotation-timing-direction-20261010'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
CAP=Path('/opt/research-system/manual-repair-helpers/temporary-daily-cap-20261010')
CAP_RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/temporary-daily-cap-20261010')
SCIENCE=Path('/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
ENGINE=Path('/opt/research-system/autonomy-review/d08b91bdc1d0')
RUNTIME=Path('/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json')
UNIT_DIR=Path('/etc/systemd/system')
OLD_UNIT='research-temporary-daily-cap-20261010-author.service'
PREPARATION=Path('/opt/research-system/manual-repair-helpers/preparation-branch-admission-repair-20261010')
ORIGINAL_PREPARATION=Path('/opt/research-system/manual-repair-helpers/preparation-and-cap-repair-20261010')
PREPARATION_RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/preparation-branch-admission-repair-20261010')
COLAB_OLD_UNIT='research-preparation-branch-admission-repair-20261010-colab_preparation.service'
COLAB_NEW_UNIT='research-'+CHANGE+'-colab_preparation.service'
NEW_UNIT='research-'+CHANGE+'.service'
REQUIRED={'tools/install_timing_author24_recovery.py','tools/timing_author24_host.py','tools/timing_author24_runtime.py','tools/timing_author24_preparation_recovery.py','docs/TIMING_AUTHOR24_PREPARATION_PRIVATE.json','tools/install_preparation_runtime.py','tools/preparation_mechanical_continuation.py'}
def require(ok,why):
    if not ok:raise ValueError('TIMING_INSTALL_'+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        st=p.lstat();require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'TRUSTED_PATH')
    return path
def relative(name):
    p=Path(name);require(isinstance(name,str) and name and not p.is_absolute() and '..' not in p.parts and str(p)==name,'RELATIVE_PATH');return p
def mkdir(path):
    Path(path).mkdir();os.chown(path,0,1003);Path(path).chmod(0o550)
def put(path,raw):
    path=Path(path);missing=[];parent=path.parent
    while not parent.exists():missing.append(parent);parent=parent.parent
    trusted(parent)
    for parent in reversed(missing):mkdir(parent)
    with path.open('xb') as fp:fp.write(raw);fp.flush();os.fsync(fp.fileno())
    os.chown(path,0,1003);path.chmod(0o440)
def load(name,path):
    s=importlib.util.spec_from_file_location(name,trusted(path));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def unit_bytes(raw):
    old='ExecStart=/usr/bin/python3 -s -B '+str(CAP/'tools/temporary_daily_cap.py')+' author run'
    new='ExecStart=/usr/bin/python3 -s -B '+str(ROOT/'tools/timing_author24_runtime.py')+' run'
    lines=raw.decode().splitlines(keepends=True)
    require(lines.count(old+'\n')==1 and sum(x.startswith('ExecStart=') for x in lines)==1,'EXACT_PRIOR_ENTRY')
    result=raw.replace((old+'\n').encode(),(new+'\n').encode())
    require(result.replace((new+'\n').encode(),(old+'\n').encode())==raw,'ENTRY_ONLY_CHANGE');return result

def colab_unit_bytes(raw):
    old='ExecStart=/usr/bin/python3 -s -B '+str(PREPARATION/'tools/preparation_branch_repair_runtime.py')+' advance --lane colab_preparation'
    new='ExecStart=/usr/bin/python3 -s -B '+str(ROOT/'tools/preparation_mechanical_continuation.py')+' advance-colab'
    lines=raw.decode().splitlines(keepends=True)
    require(lines.count(old+'\n')==1 and sum(x.startswith('ExecStart=') for x in lines)==1,'EXACT_COLAB_PRIOR_ENTRY')
    result=raw.replace((old+'\n').encode(),(new+'\n').encode())
    require(result.replace((new+'\n').encode(),(old+'\n').encode())==raw,'COLAB_ENTRY_ONLY_CHANGE');return result

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
    require(approval['verdict']=='APPROVE' and not approval.get('findings') and approval['change_id']==REVIEW_CHANGE,'GENUINE_APPROVAL')
    bodies={n:trusted(source/relative(n)).read_bytes() for n in manifest['source_files']}
    require(REQUIRED<=set(bodies),'WHOLE_COMPONENT')
    require(all(sha(raw)==manifest['source_files'][n] for n,raw in bodies.items()),'REVIEWED_SOURCE')
    require(bodies['tools/install_timing_author24_recovery.py']==Path(__file__).read_bytes(),'EXECUTED_INSTALLER')
    prior=load('_reviewed_install_checks',source/'tools/install_preparation_runtime.py');prior.standalone_git(source)
    git=lambda *args:subprocess.check_output(['git',*args],cwd=source,text=True).strip()
    require(git('rev-parse','HEAD')==approval['source_sha'] and re.fullmatch(r'astra/manual-[a-z0-9-]+',git('branch','--show-current')) and not git('status','--porcelain'),'CLEAN_SOURCE')
    cap=load('_genuine_installed_daily_cap',CAP/'tools/temporary_daily_cap.py');cap.verified()
    installed=json.loads(trusted(CAP_RECORD/'installed.json').read_bytes())
    oldpath=UNIT_DIR/OLD_UNIT;raw=trusted(oldpath).read_bytes()
    require(sha(raw)==installed['units'][str(oldpath)],'PRIOR_UNIT_CHANGED')
    binding=json.loads(bodies['docs/TIMING_AUTHOR24_PREPARATION_PRIVATE.json'])
    operation_run=trusted(CAP_RECORD/'operation/author/RUN.json').read_bytes()
    require(sha(operation_run)==binding['operation_run_sha256'],'ORIGINAL_OPERATION_CHANGED')
    fields=['MainPID','ActiveState','SubState','ExecMainStatus','InvocationID','ControlGroup']
    command=['systemctl','show',OLD_UNIT]
    for field in fields:command+=['-p',field]
    state=dict(line.split('=',1) for line in subprocess.check_output(command,text=True).splitlines())
    require(state=={k:binding['failed_unit'][k] for k in fields},'EXACT_FAILED_UNIT_REQUIRED')
    old_preparation=load('_genuine_preparation_authority',PREPARATION/'tools/preparation_branch_repair_runtime.py')
    old_preparation.authority()
    prep_receipt=json.loads(trusted(PREPARATION_RECORD/'installed.json').read_bytes())
    colab_old=UNIT_DIR/COLAB_OLD_UNIT;colab_raw=trusted(colab_old).read_bytes()
    require(sha(colab_raw)==prep_receipt['units'][str(colab_old)],'COLAB_PRIOR_UNIT_CHANGED')
    colab_state=dict(line.split('=',1) for line in subprocess.check_output(['systemctl','show',COLAB_OLD_UNIT,'-p','MainPID','-p','ActiveState','-p','ExecMainStatus'],text=True).splitlines())
    require(colab_state=={'MainPID':'0','ActiveState':'inactive','ExecMainStatus':'0'},'COLAB_UNIT_NOT_HELD')
    units={UNIT_DIR/NEW_UNIT:unit_bytes(raw),UNIT_DIR/COLAB_NEW_UNIT:colab_unit_bytes(colab_raw)}
    for path in [ROOT,RECORD,*units]:
        trusted(path.parent);require(not path.exists() and not path.is_symlink(),'DESTINATION_EXISTS')
    review_files={p.name:trusted(p).read_bytes() for p in review.iterdir() if p.is_file()}
    require(len(review_files)==len(list(review.iterdir())),'FLAT_REVIEW')
    check=json.loads(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',OWNER_CHECK],text=True));require(check['status']=='NO_RUNNING_CALL','LIVE_CALL')
    prior.verify_units(units)
    mkdir(RECORD);put(RECORD/'INSTALL_INTENT.json',json.dumps({'source':approval['source_sha'],'review_sha256':approval['report_sha256'],'preserved_failed_unit':sha(raw)},sort_keys=True).encode())
    mkdir(ROOT)
    for n,body in bodies.items():put(ROOT/relative(n),body)
    for n,body in review_files.items():put(RECORD/'review'/n,body)
    for target,changed in units.items():put(target,changed)
    receipt={'root':str(ROOT),'source':approval['source_sha'],'review_sha256':approval['report_sha256'],'files':manifest['source_files'],'units':{str(target):sha(changed) for target,changed in units.items()},'status':'INSTALLED_HELD','preserved_failed_unit':sha(raw),'preserved_operation_run_sha256':sha(operation_run)}
    put(RECORD/'installed.json',json.dumps(receipt,sort_keys=True).encode());subprocess.run(['systemctl','daemon-reload'],check=True)
    result=subprocess.run(['runuser','-u','partho','--','env','PYTHONPATH='+str(SCIENCE),'PYTHONDONTWRITEBYTECODE=1','RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),'python3','-s','-B',str(ROOT/'tools/timing_author24_runtime.py'),'verify'],capture_output=True)
    put(RECORD/'VERIFY.stdout',result.stdout);put(RECORD/'VERIFY.stderr',result.stderr);require(result.returncode==0,'SERVICE_ACCOUNT_VERIFY_FAILED')
    colab_check=subprocess.run(['runuser','-u','partho','--','env','PYTHONPATH='+str(ORIGINAL_PREPARATION),'PYTHONDONTWRITEBYTECODE=1','RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),'python3','-s','-B',str(ROOT/'tools/preparation_mechanical_continuation.py'),'verify-colab'],capture_output=True)
    put(RECORD/'VERIFY_COLAB.stdout',colab_check.stdout);put(RECORD/'VERIFY_COLAB.stderr',colab_check.stderr);require(colab_check.returncode==0,'COLAB_SERVICE_ACCOUNT_VERIFY_FAILED')
    complete={'status':'INSTALLED_HELD','source':approval['source_sha'],'scientific_calls':0,'provider_calls':0};put(RECORD/'COMPLETE.json',json.dumps(complete,sort_keys=True).encode());return complete

if __name__=='__main__':
    os.umask(0o077);p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--review',type=Path,required=True);a=p.parse_args();print(json.dumps(install(a.source,a.review),sort_keys=True))
