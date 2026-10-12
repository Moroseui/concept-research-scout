"""Separately installed one-day policy; no immutable runtime is overwritten."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys
CHANGE='colab-tonight-cap-20261012'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
FILES=('tools/colab_tonight_cap.py','tools/temporary_daily_cap.py',
'orchestrator/autonomy_limits.py','orchestrator/autonomy_accounting.py',
'docs/COLAB_TONIGHT_ADMIN_ADMISSION_PRIVATE.py','docs/LIMIT_OPERATOR_DECISION.txt',
'docs/DAILY_LIMIT_OPERATOR_DECISION_20261007.txt','docs/OPERATOR_DIRECTION_20261010.txt',
'docs/COLAB_TONIGHT_OPERATOR_20261012.txt')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('COLAB_TONIGHT_CAP_'+why)
def trusted(path):
    path=Path(path)
    for p in (path,*path.parents):
        st=p.lstat();require(not p.is_symlink()and st.st_uid==0 and not st.st_mode&0o022,'TRUSTED_PATH')
    return path
def reviewed(folder):
    from orchestrator.autonomy_review import verify_result
    folder=trusted(folder);result=verify_result(folder)
    manifest=json.loads(trusted(folder/'packet-manifest.json').read_bytes())
    require(result['verdict']=='APPROVE'and result['change_id']==CHANGE
        and json.loads(trusted(folder/'report.md').read_bytes())['findings']==[]
        and set(FILES)<=set(manifest['source_files']),'GENUINE_APPROVAL')
    return result,manifest
def verified():
    result,manifest=reviewed(RECORD/'review')
    state=json.loads(trusted(RECORD/'INSTALLED.json').read_bytes())
    require(Path(__file__).resolve()==ROOT/'tools/colab_tonight_cap.py','INSTALLED_PATH')
    require(state=={'source':result['source_sha'],'review_sha256':result['report_sha256'],
        'files':{n:manifest['source_files'][n]for n in FILES},'status':'INSTALLED_NO_CALL'},'INSTALL_RECEIPT')
    for name,pin in state['files'].items():
        require(sha(trusted(ROOT/name).read_bytes())==pin,'INSTALLED_SOURCE')
    return result
def bind_administrative():
    verified()
    path=trusted(ROOT/'tools/temporary_daily_cap.py')
    spec=importlib.util.spec_from_file_location('_approved_tonight_cap_adapter',path)
    adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
    from orchestrator.autonomy_review_runner import ReviewQueue
    from orchestrator import autonomy_limits as limits
    require(adapter.method_pin(ReviewQueue.reserve)==adapter.PINS['administrative'],'ORIGINAL_ADMISSION_METHOD')
    require(limits.DAILY==50 and limits.SCIENTIFIC_BATCH==60 and limits.REVISE_ROUNDS==3,'BASE_LIMITS_CHANGED')
    policy=adapter.module('_tonight_daily_policy',ROOT/'orchestrator/autonomy_limits.py')
    require(policy.daily_allowance('2026-10-10')['limit']==100
            and policy.daily_allowance('2026-10-11')['limit']==50,'HISTORICAL_POLICY')
    candidate=adapter.module('_tonight_dated_admin',ROOT/'docs/COLAB_TONIGHT_ADMIN_ADMISSION_PRIVATE.py')
    require(candidate.limits is limits,'MODULE_IDENTITY')
    limits.daily_allowance=policy.daily_allowance
    method=candidate.ReviewQueue.reserve
    ReviewQueue.reserve=method
    from orchestrator import autonomy_limits as limits
    require(limits.daily_allowance('2026-10-12')=={'limit':100,
        'authority_sha256':'23a45f2fdf214ba69f808393973fb5b6bff38a72a50dd6601106647a919e4cbd'}
        and limits.daily_allowance('2026-10-13')['limit']==50,'DATED_POLICY')
    return method
def put(path,raw):
    path=Path(path)
    with path.open('xb')as out:out.write(raw)
    os.chown(path,0,1003);path.chmod(0o440)
def directory(path):
    path=Path(path);path.mkdir(mode=0o550);os.chown(path,0,1003);path.chmod(0o550)
def install(source,folder):
    require(os.getuid()==0 and sys.flags.no_user_site,'ROOT_ISOLATED')
    source=trusted(source);result,manifest=reviewed(folder)
    git=lambda *args:subprocess.check_output(['git',*args],cwd=source,text=True).strip()
    require(git('rev-parse','HEAD')==result['source_sha']and not git('status','--porcelain'),'CLEAN_REVIEWED_SOURCE')
    require((source/FILES[0]).read_bytes()==Path(__file__).read_bytes(),'EXACT_INSTALLER')
    for name in FILES:require(sha(trusted(source/name).read_bytes())==manifest['source_files'][name],'SOURCE_CHANGED')
    for dest in (ROOT,RECORD):
        trusted(dest.parent);require(not dest.exists()and not dest.is_symlink(),'EXISTING_INSTALL_RECONCILE')
    import shutil
    require(all(shutil.disk_usage(p.parent).free>8*2**30 for p in (ROOT,RECORD)),'DISK_STOP')
    sql="SELECT 1 FROM autonomy_calls WHERE status='RUNNING'"
    code="import sqlite3,os;assert os.getuid()==1003;d=sqlite3.connect('file:/var/lib/research-system-autonomy/reviews/jobs.sqlite?mode=ro',uri=True);assert not d.execute("+repr(sql)+").fetchone()"
    subprocess.run(['runuser','-u','partho','--','python3','-s','-B','-c',code],check=True)
    for dest in (ROOT,RECORD):directory(dest)
    put(RECORD/'INSTALL_INTENT.json',json.dumps({'source':result['source_sha'],'review':result['report_sha256']},sort_keys=True).encode())
    for name in FILES:
        target=ROOT/name
        if not target.parent.exists():directory(target.parent)
        put(target,trusted(source/name).read_bytes())
    directory(RECORD/'review')
    for p in Path(folder).iterdir():
        require(p.is_file()and not p.is_symlink(),'FLAT_REVIEW')
        put(RECORD/'review'/p.name,trusted(p).read_bytes())
    state={'source':result['source_sha'],'review_sha256':result['report_sha256'],
           'files':{n:manifest['source_files'][n]for n in FILES},'status':'INSTALLED_NO_CALL'}
    put(RECORD/'INSTALLED.json',json.dumps(state,sort_keys=True).encode())
    return state
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--review',type=Path,required=True)
    a=p.parse_args();os.umask(0o077);print(json.dumps(install(a.source,a.review),sort_keys=True))
