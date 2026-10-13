"""Narrow reviewed overlay for one preserved author output; no author or GPU launch."""
from pathlib import Path
import argparse,importlib.util,json,os,subprocess,sys
BASE=Path('/opt/research-system/manual-repair-helpers/colab-simple-admission-20261012')
PRIOR=Path('/opt/research-system/manual-repair-helpers/multiwin-returned-provenance-20261013')
CHANGE='multiwin-output-boundary-20261013'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
UNIT='research-'+CHANGE+'.service'
ENTRY='tools/multiwin_preserved_runtime.py'
BRANCH='astra/multiwin-output-boundary-20261013'
FILES=(ENTRY,'orchestrator/multiwin_preserved_output.py','docs/MULTIWIN_OUTPUT_BOUNDARY_PRIVATE.json')
def require(ok,why):
    if not ok:raise ValueError('MULTIWIN_PRESERVED_RUNTIME_'+why)
def sha(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def load(name,path):
    from orchestrator.manual_host_guard import trusted
    spec=importlib.util.spec_from_file_location(name,trusted(path));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def previous():
    require(Path(__import__('orchestrator').__file__).resolve().parent==BASE/'orchestrator','BASE_IMPORT')
    old=load('_preserved_previous_runtime',PRIOR/'tools/multiwin_returned_runtime.py')
    approval,_,_=old.authority()
    require(approval['source_sha']=='9fa7b3160330cbe73dc213ad3dcb8ec5089a8fe6' and
        approval['report_sha256']=='16608358134791c21ab70e9948931f442ea9eb483d1dbbca1637defdeadb3403','PRIOR_APPROVAL')
    return old
def unit_bytes(old):
    from orchestrator.manual_host_guard import trusted
    raw=trusted('/etc/systemd/system/'+old.UNIT).read_bytes()
    before=('ExecStart=/usr/bin/python3 -s -B '+str(PRIOR/old.ENTRY)+' run\n').encode()
    after=('ExecStart=/usr/bin/python3 -s -B '+str(ROOT/ENTRY)+' run\n').encode()
    require(raw.count(before)==1,'EXACT_ENTRY')
    return raw.replace(before,after)
def held(old):
    _,parent,_=old.authority();old.held(parent)
    v=dict(x.split('=',1)for x in subprocess.check_output(['systemctl','show',UNIT,'-p','MainPID','-p','ActiveState'],text=True).splitlines())
    require(v['MainPID']=='0'and v['ActiveState']in{'inactive','failed'},'LIVE_UNIT')
def reviewed(folder):
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    result=verify_result(trusted(folder));m=json.loads(trusted(Path(folder)/'packet-manifest.json').read_bytes())
    require(result['change_id']==CHANGE and result['verdict']=='APPROVE'and
        json.loads(trusted(Path(folder)/'report.md').read_bytes())['findings']==[],'GENUINE_APPROVE')
    require(set(FILES)|{'tests/test_multiwin_preserved_output.py','orchestrator/analysis_driver.py',
        'orchestrator/colab_preparation_scope.py','orchestrator/colab_notebook_delivery.py',
        'orchestrator/notebook_revision.py','orchestrator/multiwin_returned.py'}<=set(m['source_files']),'WHOLE_COMPONENT')
    return result,m
def authority():
    from orchestrator.manual_host_guard import trusted
    require(Path(__file__).resolve()==ROOT/ENTRY,'INSTALLED_ENTRY')
    result,m=reviewed(RECORD/'review');old=previous()
    receipt=json.loads(trusted(RECORD/'INSTALLED.json').read_bytes())
    require(receipt=={'source':result['source_sha'],'review_sha256':result['report_sha256'],
        'files':{n:m['source_files'][n]for n in FILES},'unit_sha256':sha(unit_bytes(old))},'INSTALL_RECEIPT')
    for n in FILES:require(sha(trusted(ROOT/n).read_bytes())==m['source_files'][n],'SOURCE_CHANGED')
    require(trusted('/etc/systemd/system/'+UNIT).read_bytes()==unit_bytes(old),'UNIT_CHANGED')
    return result,old
def install(source,review):
    from orchestrator.manual_host_guard import trusted
    from tools.install_preparation_branch_repair import put,mkdir,OWNER_CHECK
    from tools.install_preparation_runtime import standalone_git,verify_units
    require(os.getuid()==0 and sys.flags.no_user_site,'ROOT_INSTALL')
    source=trusted(source);review=trusted(review);result,m=reviewed(review);standalone_git(source)
    git=lambda *args:subprocess.check_output(['git',*args],cwd=source,text=True).strip()
    require(git('rev-parse','HEAD')==result['source_sha']and git('branch','--show-current')==BRANCH
        and not git('status','--porcelain')and trusted(source/ENTRY).read_bytes()==Path(__file__).read_bytes(),'CLEAN_SOURCE')
    old=previous();held(old)
    _,parent,_=old.authority()
    require(result['runtime_sha256']==sha(trusted(parent.metadata()[1]['runtime']).read_bytes()),'RUNTIME')
    for n,pin in m['source_files'].items():require(sha(trusted(source/n).read_bytes())==pin,'SOURCE_CHANGED')
    for dest in (ROOT,RECORD,Path('/etc/systemd/system')/UNIT):
        trusted(dest.parent);require(not dest.exists()and not dest.is_symlink(),'ALREADY_ATTEMPTED')
    import shutil
    require(all(shutil.disk_usage(x.parent).free>=8*2**30 for x in (ROOT,RECORD)),'DISK_STOP')
    require(json.loads(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',OWNER_CHECK],text=True))['status']=='NO_RUNNING_CALL','LIVE_MODEL')
    unit=unit_bytes(old);verify_units({Path('/etc/systemd/system')/UNIT:unit})
    mkdir(RECORD);put(RECORD/'INTENT.json',canonical({'source':result['source_sha'],'review_sha256':result['report_sha256']}));mkdir(ROOT)
    for n in FILES:put(ROOT/n,trusted(source/n).read_bytes())
    for p in review.iterdir():
        require(p.is_file()and not p.is_symlink(),'FLAT_REVIEW');put(RECORD/'review'/p.name,trusted(p).read_bytes())
    put(Path('/etc/systemd/system')/UNIT,unit)
    put(RECORD/'INSTALLED.json',canonical({'source':result['source_sha'],'review_sha256':result['report_sha256'],
        'files':{n:m['source_files'][n]for n in FILES},'unit_sha256':sha(unit)}))
    subprocess.run(['systemctl','daemon-reload'],check=True)
    return {'status':'INSTALLED_HELD','new_calls':0,'new_allowance':0}
def service(action):
    from orchestrator.manual_executor import lock
    approval,old=authority();prior,parent,helper,driver=old.connect()
    repair=load('_preserved_recovery',ROOT/'orchestrator/multiwin_preserved_output.py');b=repair.document(ROOT)
    undo=None
    try:
        if action=='status':
            repair.check(driver,b)
            return {**driver.status(),'transition':parent.snapshot(driver)}
        require(action=='run'and bool(os.environ.get('INVOCATION_ID')),'NATIVE_INVOCATION')
        operation=json.loads((RECORD/'OPERATION.json').read_bytes())
        require(operation['source']==approval['source_sha']and operation['review_sha256']==approval['report_sha256']
            and operation['transition']==parent.snapshot(driver),'STATE_BOUND_OPERATION')
        if operation['mode']=='recover':
            with lock(driver.state/'driver.lock'):
                driver.guard()
                return repair.apply(driver,b,approval['report_sha256'])
        require(operation['mode']=='review','ONE_REVIEW_ONLY')
        repair.grant(driver,b,approval['report_sha256'])
        value=driver.current()
        require(value['phase']=='run_spec_review'and value['rounds']['run_spec_review']==11
            and not value.get('pending'),'EXACT_REVIEW12')
        undo=repair.bind(driver,b,approval['report_sha256'])
        return driver.advance()
    finally:
        if undo:undo()
        driver._returned_restore();driver.store.db.close();driver.store.batch.db.close()
def start(mode,transition):
    import fcntl
    from tools.install_preparation_branch_repair import put,OWNER_CHECK
    require(os.getuid()==0 and sys.flags.no_user_site and mode in {'recover','review'},'ROOT_START')
    approval,old=authority()
    with (RECORD/'start.lock').open('a') as out:
        fcntl.flock(out,fcntl.LOCK_EX);held(old)
        _,parent,_=old.authority();runtime=parent.metadata()[1]['runtime']
        status=json.loads(subprocess.check_output(['runuser','-u','partho','--','env','RESEARCH_MANUAL_RUNTIME_CONFIG='+runtime,
            'PYTHONPATH='+str(BASE),'python3','-s','-B',str(ROOT/ENTRY),'status'],text=True))
        require(status['transition']==transition and status['phase']==('BLOCKED'if mode=='recover'else'run_spec_review'),'STATE_OR_MODE')
        require(json.loads(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',OWNER_CHECK],text=True))['status']=='NO_RUNNING_CALL','LIVE_MODEL')
        intent=RECORD/(mode+'-START.json');require(not intent.exists()and not intent.is_symlink(),'ONE_START_ONLY')
        value={'mode':mode,'transition':transition,'source':approval['source_sha'],'review_sha256':approval['report_sha256']}
        put(intent,canonical(value));put(RECORD/'OPERATION.next',canonical(value));os.replace(RECORD/'OPERATION.next',RECORD/'OPERATION.json')
        subprocess.run(['systemctl','start','--no-block',UNIT],check=True)
        return {'status':'START_REQUESTED_RECONCILE','mode':mode}
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['install','status','run','start'])
    p.add_argument('--source',type=Path);p.add_argument('--review',type=Path);p.add_argument('--mode',choices=['recover','review']);p.add_argument('--transition');a=p.parse_args()
    if a.action=='install':
        require(a.source is not None and a.review is not None and a.mode is None and a.transition is None,'INSTALL_ARGS')
        return install(a.source,a.review)
    require(a.source is None and a.review is None,'NO_SOURCE_OVERRIDE')
    if a.action=='start':return start(a.mode,a.transition)
    require(a.mode is None and a.transition is None,'NO_OPERATION_OVERRIDE')
    return service(a.action)
if __name__=='__main__':
    os.umask(0o077);sys.path.insert(0,str(BASE));print(json.dumps(main(),sort_keys=True))
