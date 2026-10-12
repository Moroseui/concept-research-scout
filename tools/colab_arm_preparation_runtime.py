"""Reviewed overlay: same lane, unchanged installed engine and all native controls."""
from pathlib import Path
import argparse, importlib.util, json, os, subprocess, sys

BASE=Path('/opt/research-system/manual-repair-helpers/colab-simple-admission-20261012')
ROOT=Path('/opt/research-system/manual-repair-helpers/colab-multiwin-runtime-recovery-20261012')
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/colab-multiwin-runtime-recovery-20261012')
LANE=Path('/var/lib/research-system-manual-sprint10-deployment/colab-simple-admission-20261012-work/lane')
UNIT='research-colab-multiwin-runtime-recovery-20261012.service'
PREVIOUS_UNIT='research-colab-multiwin-20261012.service'
OLD_UNIT='research-colab-simple-admission-20261012.service'
CHANGE='colab-multiwin-runtime-recovery-20261012'
ENTRY='tools/colab_arm_preparation_runtime.py'
ADDED=('orchestrator/colab_static_feedback.py', 'tools/colab_static_feedback_runtime.py', 'docs/COLAB_AUTHOR5_STATIC_PRIVATE.json', 'docs/COLAB_STATIC_FEEDBACK_SCOPE.md', 'tests/test_colab_static_feedback.py', 'orchestrator/colab_bound_revision.py', 'tools/colab_bound_revision_runtime.py', 'docs/COLAB_REVIEW5_BOUND_PRIVATE.json', 'docs/COLAB_BOUND_ADMISSION_PRIVATE.json', 'docs/COLAB_REVIEW5_OPERATOR_DISPOSITION.json', 'docs/COLAB_REVIEW5_OPERATOR_DECISION_20261012.txt', 'docs/OVERNIGHT_AUTONOMY_OPERATOR_DECISION_20261008.txt', 'docs/COLAB_ACCEPTED_INPUT_REFERENCE_PRIVATE.json', 'docs/COLAB_BOUND_REVISION_SCOPE.md', 'tests/test_colab_bound_revision.py', 'orchestrator/notebook_revision.py', 'orchestrator/author_output_schema.py', 'orchestrator/analysis_revisions.py', 'docs/SCIENTIFIC_REVISE_OPERATOR_DECISION_20261012.txt', 'docs/COLAB_REVIEW6_DELETE_PRIVATE.json', 'tests/test_colab_omission_delete.py', 'tests/test_author_revision_accounting.py', 'tests/test_experiment_revisions.py', 'tests/test_scoped_revisions_limits.py', 'tests/test_item4_review4_continuation.py', 'tests/test_item4_review5_continuation.py', 'tests/test_item4_review6_continuation.py', 'orchestrator/colab_arm_preparation.py', 'orchestrator/colab_notebook_delivery.py', 'tools/colab_arm_preparation_runtime.py', 'docs/COLAB_MULTIWIN_PRIVATE.json', 'docs/COLAB_MULTIWIN_AUTHOR_TASK.md', 'docs/COLAB_ARM_ORDER_OPERATOR_20261012.txt', 'docs/COLAB_MULTIWIN_INPUT_REFERENCE_PRIVATE.json', 'tests/test_colab_arm_delivery.py', 'tests/test_colab_arm_preparation.py')
ADDED=(*ADDED,'docs/COLAB_MULTIWIN_RECOVERY_PRIVATE.json','docs/COLAB_ARM_LEVEL_OPERATOR_20261012.txt','docs/SCIENTIFIC_BATCH128_OPERATOR_APPROVAL.txt','docs/SCIENTIFIC_BATCH128_OPERATOR_QUESTION.txt','docs/COLAB_MULTIWIN_RECOVERY_AUTHOR_TASK.md','docs/COLAB_NNUNET281_UPSTREAM_TRAINER.py','docs/COLAB_RUNTIME_FAILURES_PRIVATE.json')
ADDED=(*ADDED,'tests/test_colab_simple_full.py')
BRANCH='astra/manual-colab-runtime-recovery-20261012'

def load(name,path):
    from orchestrator.manual_host_guard import trusted
    spec=importlib.util.spec_from_file_location(name,trusted(path))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def dependencies(root=ROOT):
    # Original engine package is used unchanged, including its source/config guards.
    require(Path(__import__('orchestrator').__file__).resolve().parent==BASE/'orchestrator','BASE_IMPORT')
    parent=load('_colab_parent_runtime',BASE/'tools/colab_simple_runtime.py')
    result=parent.authority()
    require(result['source_sha']=='0770e23ac2bf257edc819b2e3f6e2a2693e12095' and
            result['report_sha256']=='93871cd5a9ccae13b9d68f5cd01457cff20b80aad3c55d457cbaa30777c7210d','BASE_APPROVAL')
    helper=load('_colab_static_feedback',Path(root)/'orchestrator/colab_arm_preparation.py')
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
    old='/usr/bin/python3 -s -B '+str(BASE)+'/tools/colab_simple_runtime.py run'
    new='/usr/bin/python3 -s -B '+str(ROOT/ENTRY)+' run'
    require(raw.count(('ExecStart='+old+'\n').encode())==1,'PARENT_COMMAND')
    return raw.replace(('ExecStart='+old+'\n').encode(),('ExecStart='+new+'\n').encode())

def held(parent):
    parent.held_prior()
    for unit in (OLD_UNIT,PREVIOUS_UNIT,'research-colab-bound-revision-20261012.service','research-colab-bound-state-20261012.service',UNIT):
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
    require(os.environ.get('RESEARCH_MANUAL_RUNTIME_CONFIG')==parent.metadata()[1]['runtime'],'RUNTIME')
    os.environ.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(BASE))
    parent.connect_qualifier()
    from orchestrator.analysis_driver import AnalysisDriver
    return approval,parent,helper,helper.install_hook(AnalysisDriver,ROOT,approval['report_sha256'])(LANE)

def probe(driver,parent,helper,approval):
    from orchestrator import manual_stage,private_records as pr
    from orchestrator.manual_executor import atomic
    helper.check_originals(driver,helper.frozen(ROOT),initial=True)
    admission=helper.probe_admission(driver,ROOT,approval['report_sha256'])
    driver.guard();before=parent.snapshot(driver)
    folder=LANE/'multiwin-runtime-qualification'
    require(not folder.exists() and not folder.is_symlink(),'PROBE_ALREADY_ATTEMPTED')
    pr.mkdir(folder);work=folder/'author'
    value=helper.restored(driver.current(),approval['report_sha256'])
    # Only input preparation is qualified. No grant is forged for this probe.
    cls=type(driver);base=cls.__bases__[0]
    files=helper.feedback_files(driver,helper.frozen(ROOT),ROOT)
    driver._static_feedback=files
    try:body,measurement=base.prepare_input(driver,value,'run_spec_author',work)
    finally:driver.__dict__.pop('_static_feedback',None)
    for name,raw in files.items():
        target=work/name;pr.mkdir(target.parent,parents=True,exist_ok=True);pr.write_bytes(target,raw);target.chmod(0o400)
    pr.write_text(work/'prompt.md',body);atomic(work/'input-measurement.json',measurement)
    manual_stage.data_access_guard(work,'run_spec_author')
    require(manual_stage.preflight()==driver.config['clients'],'CLIENTS_CHANGED')
    checks=[manual_stage.transport_check(work,stage,sha(body.encode()))for stage in ('run_spec_author','run_spec_review')]
    require(all(x['model_client_launched'] is False for x in checks) and parent.snapshot(driver)==before,'PROBE_MUTATION')
    result={'status':'PASS','source':approval['source_sha'],'transition':before,'review_sha256':approval['report_sha256'],'model_calls':0,'transport':checks,'author_admission':admission}
    atomic(folder/'COMPLETE.json',result);return result

def service(action):
    from orchestrator.manual_executor import lock
    approval,parent,helper,driver=connect()
    try:
        if action=='status':return {**driver.status(),'transition':parent.snapshot(driver)}
        if action=='recover':
            held(parent)
            with lock(LANE/'driver.lock'):
                q=json.loads((LANE/'multiwin-runtime-qualification/COMPLETE.json').read_bytes())
                require(q['status']=='PASS' and q['source']==approval['source_sha'] and q['transition']==parent.snapshot(driver),'NATIVE_PROBE_REQUIRED')
                return helper.resume(driver,helper.frozen(ROOT),approval['report_sha256'])
        require(action=='run' and bool(os.environ.get('INVOCATION_ID')),'NATIVE_INVOCATION')
        operation=json.loads((RECORD/'OPERATION.json').read_bytes())
        require(operation['source']==approval['source_sha'] and operation['review_sha256']==approval['report_sha256']
                and operation['transition']==parent.snapshot(driver),'STATE_BOUND_OPERATION')
        if operation['mode']=='probe':
            with lock(LANE/'driver.lock'):return probe(driver,parent,helper,approval)
        require(operation['mode']=='advance','MODE')
        q=json.loads((LANE/'multiwin-runtime-qualification/COMPLETE.json').read_bytes())
        require(q['status']=='PASS' and q['source']==approval['source_sha'],'NATIVE_PROBE_REQUIRED')
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
        allowed={'COMMIT_SPEC'} if mode=='probe' else {'run_spec_author','run_spec_review','MODEL_RUNNING'}
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
