"""Reviewed overlay: same lane, unchanged installed engine and all native controls."""
from pathlib import Path
import argparse, importlib.util, json, os, subprocess, sys

BASE=Path('/opt/research-system/manual-repair-helpers/colab-pnormct-question-20261012')
ROOT=Path('/opt/research-system/manual-repair-helpers/colab-pnormct-format-20261012')
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/colab-pnormct-format-20261012')
LANE=Path('/var/lib/research-system-manual-sprint10-deployment/colab-pnormct-question-20261012-work/lane')
UNIT='research-colab-pnormct-format-20261012.service'
OLD_UNIT='research-colab-pnormct-question-20261012.service'
CHANGE='colab-pnormct-format-20261012'
ENTRY='tools/colab_pnormct_format_runtime.py'
ADDED=('orchestrator/colab_pnormct_policy.py','tools/colab_pnormct_policy_runtime.py',
       'docs/COLAB_PNORMCT_POLICY_FAILURE_PRIVATE.json','tests/test_colab_pnormct_policy.py')
ADDED=(*ADDED,'orchestrator/colab_pnormct_format.py','tools/colab_pnormct_format_runtime.py',
       'docs/COLAB_PNORMCT_FORMAT_FAILURE_PRIVATE.json','tests/test_colab_pnormct_format.py')
BRANCH='astra/pnormct-format-correction-20261012'

def load(name,path):
    from orchestrator.manual_host_guard import trusted
    spec=importlib.util.spec_from_file_location(name,trusted(path))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def dependencies(root=ROOT):
    require(Path(__import__('orchestrator').__file__).resolve().parent==BASE/'orchestrator','BASE_IMPORT')
    parent=load('_pnormct_parent_runtime',BASE/'tools/colab_pnormct_runtime.py')
    result=parent.authority()
    require(result['source_sha']=='45c6b7deea7768df99b4c754d960444afc117cb5' and
            result['report_sha256']=='3f3a1a0e09641ecde9100ea1dd632434acd29e52bef2660738a522bb1938dc2c','BASE_APPROVAL')
    helper=load('_pnormct_format_helper',Path(root)/'orchestrator/colab_pnormct_format.py')
    return parent,helper


def require(ok,why):
    if not ok:raise ValueError('COLAB_STATIC_RUNTIME_'+why)

def sha(raw):
    import hashlib
    return hashlib.sha256(raw).hexdigest()

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()

def unit_bytes(parent):
    scope,_=parent.metadata()
    raw=parent.unit_bytes(scope)
    old='/usr/bin/python3 -s -B '+str(BASE)+'/tools/colab_pnormct_runtime.py run'
    new='/usr/bin/python3 -s -B '+str(ROOT/ENTRY)+' run'
    require(raw.count(('ExecStart='+old+'\n').encode())==1,'PARENT_COMMAND')
    return raw.replace(('ExecStart='+old+'\n').encode(),('ExecStart='+new+'\n').encode())

def held(parent):
    parent.held_prior()
    for unit in (OLD_UNIT,'research-colab-pnormct-policy-20261012.service',UNIT):
        v=dict(x.split('=',1)for x in subprocess.check_output(['systemctl','show',unit,'-p','MainPID','-p','ActiveState'],text=True).splitlines())
        require(v['MainPID']=='0' and v['ActiveState'] in {'inactive','failed'},'NATIVE_UNIT_LIVE')

def reviewed(folder):
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    folder=trusted(folder);result=verify_result(folder)
    manifest=json.loads(trusted(folder/'packet-manifest.json').read_bytes())
    require(result['verdict']=='APPROVE' and result['change_id']==CHANGE and
            json.loads(trusted(folder/'report.md').read_bytes())['findings']==[],'INDEPENDENT_APPROVE')
    require(set(ADDED)<=set(manifest['source_files']) and
            {'orchestrator/analysis_driver.py','orchestrator/manual_stage.py',
             'orchestrator/colab_preparation_scope.py','orchestrator/author_output_schema.py',
             'orchestrator/notebook_execution.py'}<=set(manifest['source_files']),'WHOLE_COMPONENT')
    return result,manifest

def authority():
    from orchestrator.manual_host_guard import trusted
    require(Path(__file__).resolve()==ROOT/ENTRY,'INSTALLED_ENTRY')
    result,manifest=reviewed(RECORD/'review')
    receipt=json.loads(trusted(RECORD/'INSTALLED.json').read_bytes())
    parent,helper=dependencies()
    require(receipt=={'source':result['source_sha'],'review_sha256':result['report_sha256'],
                      'files':manifest['source_files'],'unit_sha256':sha(unit_bytes(parent))},'INSTALL_RECEIPT')
    for name,pin in manifest['source_files'].items():
        require(sha(trusted((ROOT if name in ADDED else BASE)/name).read_bytes())==pin,'REVIEWED_SOURCE_CHANGED')
    require(trusted('/etc/systemd/system/'+UNIT).read_bytes()==unit_bytes(parent),'UNIT_CHANGED')
    return result,parent,helper

def install(source,review):
    from orchestrator.manual_host_guard import trusted
    from tools.install_preparation_branch_repair import put,mkdir,OWNER_CHECK
    from tools.install_preparation_runtime import standalone_git,verify_units
    require(os.getuid()==0 and sys.flags.no_user_site,'ROOT_INSTALL')
    source=trusted(source);review=trusted(review)
    result,manifest=reviewed(review);standalone_git(source)
    git=lambda *args:subprocess.check_output(['git',*args],cwd=source,text=True).strip()
    require(git('rev-parse','HEAD')==result['source_sha'] and git('branch','--show-current')==BRANCH
            and not git('status','--porcelain'),'CLEAN_REVIEWED_SOURCE')
    require((source/ENTRY).read_bytes()==Path(__file__).read_bytes(),'INSTALLER_BYTES')
    parent,helper=dependencies(source);held(parent)
    require(result['runtime_sha256']==sha(trusted(parent.metadata()[1]['runtime']).read_bytes()),'UNCHANGED_RUNTIME')
    for name,pin in manifest['source_files'].items():
        require(sha(trusted(source/name).read_bytes())==pin,'SOURCE_CHANGED')
        if name not in ADDED:require(trusted(source/name).read_bytes()==trusted(BASE/name).read_bytes(),'ONLY_ADDITIONS')
    for dest in (ROOT,RECORD,Path('/etc/systemd/system')/UNIT):
        trusted(dest.parent);require(not dest.exists() and not dest.is_symlink(),'INSTALL_ALREADY_ATTEMPTED')
    import shutil
    require(all(shutil.disk_usage(x.parent).free>=8*2**30 for x in (ROOT,RECORD)),'DISK_STOP')
    require(json.loads(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',OWNER_CHECK],text=True))['status']=='NO_RUNNING_CALL','LIVE_MODEL')
    unit=unit_bytes(parent);verify_units({Path('/etc/systemd/system')/UNIT:unit})
    mkdir(RECORD);put(RECORD/'INSTALL_INTENT.json',canonical({'source':result['source_sha'],'review_sha256':result['report_sha256']}))
    mkdir(ROOT)
    for name in ADDED:put(ROOT/name,trusted(source/name).read_bytes())
    for path in review.iterdir():
        require(path.is_file() and not path.is_symlink(),'FLAT_REVIEW')
        put(RECORD/'review'/path.name,trusted(path).read_bytes())
    put(Path('/etc/systemd/system')/UNIT,unit)
    put(RECORD/'INSTALLED.json',canonical({'source':result['source_sha'],'review_sha256':result['report_sha256'],
        'files':manifest['source_files'],'unit_sha256':sha(unit)}))
    subprocess.run(['systemctl','daemon-reload'],check=True)
    return {'status':'INSTALLED_HELD','new_calls':0,'new_allowance':0}

def connect():
    approval,parent,helper=authority()
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,'SERVICE_OWNER')
    prior=load('_installed_pnormct_policy',Path('/opt/research-system/manual-repair-helpers/colab-pnormct-policy-20261012')/'tools/colab_pnormct_policy_runtime.py')
    earlier,_,_,driver=prior.connect()
    require(earlier['source_sha']=='885c737b39b211236bd74158e09dbe4a45e29a0c' and
        earlier['report_sha256']=='cd575d73ac4fdf679d319b6ccc29de3eb0be9b3815569350b025dcb9c263d124','PRIOR_POLICY_APPROVAL')
    helper.check(driver,helper.document(ROOT))
    driver.__class__=helper.corrected(type(driver),ROOT,approval['report_sha256'])
    return approval,parent,helper,driver


def probe(driver,parent,helper,approval):
    from orchestrator import manual_stage,private_records as pr,manual_recovery
    from orchestrator.manual_executor import atomic
    frozen=helper.document(ROOT);helper.check(driver,frozen,initial=True)
    driver.guard();before=parent.snapshot(driver)
    folder=LANE/'format-qualification'
    require(not folder.exists() and not folder.is_symlink(),'PROBE_ALREADY_ATTEMPTED')
    pr.mkdir(folder);work=folder/'author'
    value=helper.restored(driver.current(),frozen)
    db=driver.store.db;require(not db.in_transaction,'CLEAN_PROBE')
    db.execute('BEGIN IMMEDIATE')
    try:
        db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value,sort_keys=True),))
        number=driver.model_round_number(value)
        require(number==2 and manual_recovery.role_limit(driver.store,driver.config['run_id'],'run_spec_author')==2
                and manual_recovery.role_limit(driver.store,driver.config['run_id'],'run_spec_review')==4,'NATIVE_REVIEW_ADMISSION')
        body,measurement=driver.prepare_input(value,'run_spec_author',work)
    finally:db.rollback()
    pr.write_text(work/'prompt.md',body);atomic(work/'input-measurement.json',measurement)
    manual_stage.data_access_guard(work,'run_spec_author')
    require(manual_stage.preflight()==driver.config['clients'],'CLIENTS_CHANGED')
    check=manual_stage.transport_check(work,'run_spec_author',sha(body.encode()))
    require(check['model_client_launched'] is False and parent.snapshot(driver)==before,'PROBE_MUTATION')
    helper.check(driver,frozen,initial=True)
    result={'status':'PASS','source':approval['source_sha'],'transition':before,
            'review_sha256':approval['report_sha256'],'model_calls':0,'author_attempt':2,
            'transport':check,'input_sha256':sha(body.encode()),'new_allowance':0}
    atomic(folder/'COMPLETE.json',result);return result

def service(action):
    from orchestrator.manual_executor import lock
    approval,parent,helper,driver=connect()
    try:
        if action=='status':return {**driver.status(),'transition':parent.snapshot(driver)}
        if action=='recover':
            held(parent)
            with lock(LANE/'driver.lock'):
                q=json.loads((LANE/'format-qualification/COMPLETE.json').read_bytes())
                require(q['status']=='PASS' and q['source']==approval['source_sha'] and q['transition']==parent.snapshot(driver),'NATIVE_PROBE_REQUIRED')
                return helper.recover(driver,helper.document(ROOT),approval['report_sha256'])
        require(action=='run' and bool(os.environ.get('INVOCATION_ID')),'NATIVE_INVOCATION')
        operation=json.loads((RECORD/'OPERATION.json').read_bytes())
        require(operation['source']==approval['source_sha'] and operation['review_sha256']==approval['report_sha256']
                and operation['transition']==parent.snapshot(driver),'STATE_BOUND_OPERATION')
        if operation['mode']=='probe':
            with lock(LANE/'driver.lock'):return probe(driver,parent,helper,approval)
        require(operation['mode']=='advance','MODE')
        q=json.loads((LANE/'format-qualification/COMPLETE.json').read_bytes())
        require(q['status']=='PASS' and q['source']==approval['source_sha'],'NATIVE_PROBE_REQUIRED')
        value=driver.current()
        require(value['phase'] in {'run_spec_author','run_spec_review','MODEL_RUNNING'},'PREPARATION_STAGES_ONLY')
        return driver.advance()
    finally:
        driver.store.db.close();driver.store.batch.db.close()

def start(mode,transition):
    import fcntl
    from tools.install_preparation_branch_repair import put,OWNER_CHECK
    require(os.getuid()==0 and sys.flags.no_user_site and mode in {'probe','advance'},'ROOT_START')
    approval,parent,helper=authority()
    with (RECORD/'start.lock').open('a') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX);held(parent)
        runtime=parent.metadata()[1]['runtime']
        command=['runuser','-u','partho','--','env','RESEARCH_MANUAL_RUNTIME_CONFIG='+runtime,
                 'PYTHONPATH='+str(BASE),'python3','-s','-B',str(ROOT/ENTRY),'status']
        status=json.loads(subprocess.check_output(command,text=True))
        allowed={'BLOCKED'} if mode=='probe' else {'run_spec_author','run_spec_review','MODEL_RUNNING'}
        require(status['transition']==transition and status['phase'] in allowed,'STATE_CHANGED_OR_HELD')
        require(json.loads(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',OWNER_CHECK],text=True))['status']=='NO_RUNNING_CALL','LIVE_MODEL')
        intent=RECORD/'operations'/(mode+'-'+transition+'.json')
        require(not intent.exists() and not intent.is_symlink(),'START_ALREADY_ATTEMPTED')
        value={'mode':mode,'transition':transition,'source':approval['source_sha'],'review_sha256':approval['report_sha256']}
        put(intent,canonical(value));put(RECORD/'OPERATION.next',canonical(value));os.replace(RECORD/'OPERATION.next',RECORD/'OPERATION.json')
        subprocess.run(['systemctl','start','--no-block',UNIT],check=True)
        return {'status':'START_REQUESTED_RECONCILE','unit':UNIT,'mode':mode}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['install','status','recover','run','start'])
    parser.add_argument('--source',type=Path);parser.add_argument('--review',type=Path)
    parser.add_argument('--mode',choices=['probe','advance']);parser.add_argument('--transition');a=parser.parse_args()
    if a.action=='install':
        require(a.source is not None and a.review is not None and a.mode is None and a.transition is None,'INSTALL_ARGS')
        return install(a.source,a.review)
    require(a.source is None and a.review is None,'NO_SOURCE_OVERRIDE')
    if a.action=='start':return start(a.mode,a.transition)
    require(a.mode is None and a.transition is None,'NO_OPERATION_OVERRIDE')
    return service(a.action)

if __name__=='__main__':
    os.umask(0o077);sys.path.insert(0,str(BASE));print(json.dumps(main(),sort_keys=True))
