"""One native, reviewed execution of accepted Idea2 on existing server CPU.

No model calls, provider clients, allowance initialization, scientific edits or
automatic retries. Results remain private and unaccepted until interpretation.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, shutil, sqlite3, subprocess, sys
from types import SimpleNamespace

BASE=Path('/opt/research-system/manual-repair-helpers/item6-smoothing-execution-20261012-cpu')
ROOT=Path('/opt/research-system/manual-repair-helpers/item6-smoothing-execution-20261012-cpu')
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/item6-smoothing-execution-20261012-cpu')
WORK=Path('/var/lib/research-system-manual-sprint10-deployment/item6-smoothing-execution-20261012-cpu-work')
UNIT='research-item6-smoothing-cpu-20261012.service'
ENTRY='tools/idea2_cpu_runtime.py'
CHANGE='item6-smoothing-execution-20261012'
BRANCH='astra/manual-item6-smoothing-execution-20261012'
DOCUMENT='docs/IDEA2_CPU_RUNTIME_PRIVATE.json'
DOCUMENT_SHA='9ba023f3466b3015f204f40d966595887757a042c81a016b18839807ed723b79'
ADDED=('orchestrator/cpu_isolation.py','orchestrator/idea2_cpu_contract.py',
       'orchestrator/idea2_cpu_executor.py','orchestrator/idea2_cpu_lane.py',ENTRY,
       DOCUMENT,'docs/IDEA2_CPU_ACCEPTED_LANE_PRIVATE.json','docs/IDEA2_CPU_EXECUTION_DRAFT.md',
       'tests/test_cpu_diagnostics_profile.py','tests/test_idea2_cpu_contract.py',
       'tests/test_idea2_cpu_executor.py','tests/test_idea2_cpu_lane.py','tests/test_idea2_cpu_runtime.py')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
encoded=lambda v:json.dumps(v,sort_keys=True,allow_nan=False).encode()

def require(ok,reason):
    if not ok:raise ValueError('IDEA2_NATIVE_'+reason)

def metadata(root=ROOT):
    raw=(Path(root)/DOCUMENT).read_bytes()
    require(sha(raw)==DOCUMENT_SHA,'RUNTIME_SCOPE')
    v=json.loads(raw)
    require(v['incremental_micro_usd']==0 and v['hard_timeout_seconds']==3600
            and v['automatic_retry'] is False and v['model_calls'] is False
            and v['training'] is False and v['interpretation_remains_required'] is True,
            'FIXED_SCOPE')
    return v

def unit_bytes(scope):
    return ('[Unit]\nDescription=Reviewed private Idea2 saved-output CPU analysis\n'
        '[Service]\nType=oneshot\nUser=partho\nGroup=partho\nUMask=0077\n'
        'WorkingDirectory='+str(ROOT)+'\n'
        'Environment=PYTHONPATH='+str(BASE)+'\n'
        'Environment=RESEARCH_MANUAL_RUNTIME_CONFIG='+scope['runtime']+'\n'
        'ExecStart=/usr/bin/python3 -s -B '+str(ROOT/ENTRY)+' run\n'
        'Restart=no\nTimeoutStartSec=3900\nTimeoutStopSec=20\nKillMode=control-group\n'
        'SendSIGKILL=yes\nNoNewPrivileges=true\nProtectSystem=strict\nProtectHome=true\n'
        'PrivateTmp=true\nPrivateDevices=true\nPrivateNetwork=true\n'
        'ReadWritePaths='+str(WORK)+'\n').encode()

def reviewed(folder):
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    folder=trusted(folder);result=verify_result(folder)
    manifest=json.loads(trusted(folder/'packet-manifest.json').read_bytes())
    require(result['verdict']=='APPROVE' and result['change_id']==CHANGE
            and json.loads(trusted(folder/'report.md').read_bytes())['findings']==[],
            'INDEPENDENT_APPROVE')
    require(set(ADDED)<=set(manifest['source_files'])
            and {'orchestrator/manual_executor.py','orchestrator/job_store.py',
                 'orchestrator/diagnostics_contract.py','orchestrator/manual_runtime.py'}
                <=set(manifest['source_files']),'WHOLE_COMPONENT')
    return result,manifest

def authority():
    from orchestrator.manual_host_guard import trusted
    require(Path(__file__).resolve()==ROOT/ENTRY,'INSTALLED_ENTRY')
    result,manifest=reviewed(RECORD/'review');scope=metadata()
    expected={'source':result['source_sha'],'review_sha256':result['report_sha256'],
              'files':manifest['source_files'],'unit_sha256':sha(unit_bytes(scope))}
    require(json.loads(trusted(RECORD/'INSTALLED.json').read_bytes())==expected,'INSTALL_RECEIPT')
    for name,pin in manifest['source_files'].items():
        require(sha(trusted(ROOT/name).read_bytes())==pin,
                'INSTALLED_SOURCE_CHANGED')
    require(trusted('/etc/systemd/system/'+UNIT).read_bytes()==unit_bytes(scope),'UNIT_CHANGED')
    require(sha(trusted(scope['runtime']).read_bytes())==result['runtime_sha256'],'RUNTIME_CHANGED')
    return result,scope

def activate_modules():
    import orchestrator
    require(Path(orchestrator.__file__).resolve().parent==BASE/'orchestrator','BASE_IMPORT')
    for name in ('cpu_isolation','idea2_cpu_contract','idea2_cpu_lane','idea2_cpu_executor'):
        path=ROOT/'orchestrator'/(name+'.py')
        spec=importlib.util.spec_from_file_location('orchestrator.'+name,path)
        module=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=module;setattr(orchestrator,name,module);spec.loader.exec_module(module)

def held():
    props=dict(line.split('=',1)for line in subprocess.check_output(
        ['systemctl','show',UNIT,'-p','MainPID','-p','ActiveState'],text=True).splitlines())
    require(props['MainPID']=='0' and props['ActiveState'] in {'inactive','failed'},'LIVE_NATIVE_JOB')

def install(source,review):
    from orchestrator.manual_host_guard import trusted
    from tools.install_preparation_branch_repair import mkdir,put,OWNER_CHECK
    from tools.install_preparation_runtime import standalone_git,verify_units
    import shutil
    require(os.getuid()==0 and sys.flags.no_user_site,'ROOT_INSTALL')
    source,review=trusted(source),trusted(review)
    approval,manifest=reviewed(review);standalone_git(source);scope=metadata(source)
    git=lambda *a:subprocess.check_output(['git',*a],cwd=source,text=True).strip()
    require(git('rev-parse','HEAD')==approval['source_sha'] and git('branch','--show-current')==BRANCH
            and not git('status','--porcelain'),'REVIEWED_SOURCE')
    require((source/ENTRY).read_bytes()==Path(__file__).read_bytes(),'INSTALLER_BYTES')
    for name,pin in manifest['source_files'].items():
        raw=trusted(source/name).read_bytes();require(sha(raw)==pin,'SOURCE_CHANGED')
        # Every runtime byte is now copied from this exact reviewed source,
        # replacing the older overlay dependency with full immutable hash binding.
    require(sha(trusted(scope['runtime']).read_bytes())==approval['runtime_sha256'],'RUNTIME_CHANGED')
    for dest in (ROOT,RECORD,WORK,Path('/etc/systemd/system')/UNIT):
        trusted(dest.parent);require(not dest.exists() and not dest.is_symlink(),'EXISTING_INSTALL')
        require(shutil.disk_usage(dest.parent).free>=8*2**30,'DISK_STOP')
    require(json.loads(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B',
            '-c',OWNER_CHECK],text=True))['status']=='NO_RUNNING_CALL','LIVE_MODEL')
    unit=unit_bytes(scope);verify_units({Path('/etc/systemd/system')/UNIT:unit})
    mkdir(RECORD);put(RECORD/'INSTALL_INTENT.json',encoded({'source':approval['source_sha'],
        'review_sha256':approval['report_sha256'],'incremental_micro_usd':0}))
    mkdir(ROOT)
    for name in manifest['source_files']:put(ROOT/name,trusted(source/name).read_bytes())
    for path in review.iterdir():
        require(path.is_file() and not path.is_symlink(),'FLAT_REVIEW')
        put(RECORD/'review'/path.name,trusted(path).read_bytes())
    WORK.mkdir(mode=0o700);os.chown(WORK,1003,1003);os.chmod(WORK,0o700)
    put(Path('/etc/systemd/system')/UNIT,unit)
    put(RECORD/'INSTALLED.json',encoded({'source':approval['source_sha'],
        'review_sha256':approval['report_sha256'],'files':manifest['source_files'],
        'unit_sha256':sha(unit)}))
    subprocess.run(['systemctl','daemon-reload'],check=True)
    return {'status':'INSTALLED_HELD','model_calls':0,'incremental_micro_usd':0}

def read_batch(scope):
    from orchestrator import private_records as pr,idea2_cpu_lane as lane
    config=json.loads(pr.check(Path(scope['accepted_lane'])/'lane.json').read_bytes())
    path=pr.check(Path(scope['batch'])/'jobs.sqlite')
    require(not (path.parent/'HALT').exists(),'BATCH_HALT')
    db=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
    db.execute('PRAGMA query_only=ON')
    try:
        owner=db.execute('SELECT * FROM autonomy_runs WHERE id=?',(scope['run_id'],)).fetchone()
        require(owner is not None and owner['status']=='ACTIVE'
                and json.loads(owner['binding'])==config['owner_binding'],'EXISTING_OWNER')
        for ident in (lane.AUTHOR_CALL,lane.REVIEW_CALL):
            row=db.execute('SELECT status,change_id FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
            require(row is not None and row['status']=='COMPLETE' and row['change_id']==scope['run_id'],
                    'ACCEPTED_GLOBAL_CALL')
        require(not db.execute("SELECT 1 FROM autonomy_calls WHERE change_id=? AND status='RUNNING'",
                               (scope['run_id'],)).fetchone(),'ITEM_MODEL_RUNNING')
        return SimpleNamespace(db=db,filesystem_root=Path('/'))
    except BaseException:db.close();raise

def qualification(scope,approval):
    from orchestrator import private_records as pr,cpu_isolation
    folder=WORK/'qualification';require(not folder.exists(),'QUALIFICATION_REPLAY')
    pr.mkdir(folder);package=folder/'package';data=folder/'data'
    pr.mkdir(package);pr.mkdir(data)
    for name in ('analysis.py','run.py'):pr.write_text(package/name,'# Synthetic infrastructure fixture only\n')
    pr.write_text(package/'contract.json','{}');pr.write_text(data/'synthetic.txt','not patient data')
    receipts=[]
    for mode in ('readonly','deliberately-writable'):
        work=folder/mode;pr.mkdir(work)
        argv=cpu_isolation.command(scope['cpu'],package,data,work,probe=True,
            imports=('numpy','scipy','nibabel'),profile='diagnostics-fixed3x3')
        if mode=='deliberately-writable':
            indices=[i for i in range(len(argv)-2)if argv[i]=='--ro-bind' and argv[i+1]==str(data)]
            require(len(indices)==1,'NEGATIVE_CONTROL_MAPPING');argv[indices[0]]='--bind'
        result=subprocess.run(argv,capture_output=True,timeout=180)
        pr.write_bytes(work/'stdout',result.stdout);pr.write_bytes(work/'stderr',result.stderr)
        if mode=='readonly':require(result.returncode==0,'SYNTHETIC_READONLY_CONTROL')
        else:require(result.returncode!=0 and b'CPU_DIAGNOSTICS_INPUT_OR_PACKAGE_WRITABLE' in result.stderr,
                     'WRITABLE_NEGATIVE_CONTROL')
        receipts.append({'mode':mode,'exit':result.returncode,'stdout_sha256':sha(result.stdout),
                         'stderr_sha256':sha(result.stderr)})
    result={'status':'PASS','source':approval['source_sha'],'review_sha256':approval['report_sha256'],
            'controls':receipts,'patient_payloads_opened':0,'model_calls':0}
    pr.atomic(folder/'COMPLETE.json',result);return result

def execute(scope,approval):
    from orchestrator import private_records as pr,idea2_cpu_lane as lane,idea2_cpu_contract as contract
    from orchestrator.idea2_cpu_executor import Idea2CPUExecutor
    q=json.loads(pr.check(WORK/'qualification/COMPLETE.json').read_bytes())
    require(q['status']=='PASS' and q['source']==approval['source_sha']
            and q['review_sha256']==approval['report_sha256'],'NATIVE_CONTROLS_REQUIRED')
    lane.read_accepted_lane(scope['accepted_lane'],ROOT)
    metadata_bodies={name:pr.check(path).read_bytes()for name,path in scope['metadata'].items()}
    bodies={name:pr.check(path).read_bytes()for name,path in scope['scientific'].items()}
    # Authenticate metadata/program before opening any patient payload.
    contract.authenticate_metadata(metadata_bodies)
    contract.authenticate_program(bodies['program'],bodies['spec'],bodies['review'],bodies['approval'])
    batch=read_batch(scope)
    try:
        store=Idea2CPUExecutor(WORK/'jobs.sqlite',scope['cpu'],batch=batch)
        try:
            queued=store.submit(source=approval['source_sha'],implementation_review=approval['report_sha256'],
                metadata=metadata_bodies,**bodies,package=WORK/'package')
            result=store.execute(WORK/'package',WORK/'execution')
            lane.read_accepted_lane(scope['accepted_lane'],ROOT)
            pr.atomic(WORK/'EXECUTION_COMPLETE.json',{**result,'admission':queued,
                'source':approval['source_sha'],'review_sha256':approval['report_sha256'],
                'interpretation_required':True,'scientific_acceptance':False})
            return result
        finally:store.db.close()
    finally:batch.db.close()

def start(mode):
    import fcntl
    from tools.install_preparation_branch_repair import put
    require(os.getuid()==0 and sys.flags.no_user_site and mode in {'qualify','execute'},'ROOT_START')
    approval,scope=authority()
    require(shutil.disk_usage(WORK).free>=8*2**30,'DISK_STOP')
    with (RECORD/'start.lock').open('a')as stream:
        fcntl.flock(stream,fcntl.LOCK_EX);held()
        intent=RECORD/(mode+'.intent');require(not intent.exists(),'START_ALREADY_ATTEMPTED')
        value={'mode':mode,'source':approval['source_sha'],'review_sha256':approval['report_sha256']}
        put(intent,encoded(value));put(RECORD/'OPERATION.next',encoded(value))
        os.replace(RECORD/'OPERATION.next',RECORD/'OPERATION.json')
        subprocess.run(['systemctl','start','--no-block',UNIT],check=True)
        return {'status':'START_REQUESTED_RECONCILE','mode':mode,'unit':UNIT}

def run():
    import fcntl
    from orchestrator.manual_host_guard import trusted
    from orchestrator import private_records as pr
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,'SERVICE_OWNER')
    approval,scope=authority()
    require(shutil.disk_usage(WORK).free>=8*2**30,'DISK_STOP')
    require(os.environ.get('RESEARCH_MANUAL_RUNTIME_CONFIG')==scope['runtime'],'RUNTIME')
    props=dict(line.split('=',1)for line in subprocess.check_output(
        ['systemctl','show',UNIT,'-p','MainPID','-p','InvocationID'],text=True).splitlines())
    require(props['MainPID']==str(os.getpid()) and bool(os.environ.get('INVOCATION_ID'))
            and props['InvocationID']==os.environ['INVOCATION_ID'],'NATIVE_INVOCATION')
    operation=json.loads(trusted(RECORD/'OPERATION.json').read_bytes())
    require(operation['source']==approval['source_sha'] and operation['review_sha256']==approval['report_sha256']
            and operation['mode'] in {'qualify','execute'},'OPERATION_BINDING')
    activate_modules()
    with pr.open_file(WORK/(operation['mode']+'-started.json'),'xb')as stream:stream.write(encoded(operation))
    # Existing accepted lane remains read-only, including its lock contents.
    with pr.check(Path(scope['accepted_lane'])/'driver.lock').open('rb')as lockfile:
        fcntl.flock(lockfile,fcntl.LOCK_EX|fcntl.LOCK_NB)
        from orchestrator import idea2_cpu_lane
        idea2_cpu_lane.read_accepted_lane(scope['accepted_lane'],ROOT)
        return qualification(scope,approval)if operation['mode']=='qualify'else execute(scope,approval)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('install','start','run'))
    parser.add_argument('--source',type=Path);parser.add_argument('--review',type=Path)
    parser.add_argument('--mode',choices=('qualify','execute'));args=parser.parse_args()
    if args.action=='install':
        require(args.source is not None and args.review is not None and args.mode is None,'INSTALL_ARGS')
        return install(args.source,args.review)
    require(args.source is None and args.review is None,'NO_SOURCE_OVERRIDE')
    if args.action=='start':return start(args.mode)
    require(args.mode is None,'NATIVE_RUN_ARGS');return run()

if __name__=='__main__':
    os.umask(0o077);sys.path.insert(0,str(BASE));print(json.dumps(main(),sort_keys=True))
