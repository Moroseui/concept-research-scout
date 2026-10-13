"""Distinct L preparation entry point, using the unchanged native model clients.

No provider or data executor is exposed. Installation, lane preparation and
activation are separate explicit steps. Each service start consumes one durable
state-bound intent; an uncertain start is never replayed automatically.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from orchestrator import colab_arm_question as f
from orchestrator.manual_host_guard import trusted

ENTRY='tools/colab_l_runtime.py'
BRANCH='astra/manual-colab-L-question-20261013'
CHANGE='colab-l-reader-retry-20261013'


def metadata():
    scope=f.document()
    path=Path(__file__).resolve().parents[1]/'docs/COLAB_L_NATIVE_PRIVATE.json'
    raw=trusted(path).read_bytes()
    f.require(f.sha(raw)=='08d20c68d7185ac5b31f0af288102a3ce5ad97d220cd0b4c5a0f83a78850027f','NATIVE_BINDING')
    return scope,json.loads(raw)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,trusted(path))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def unit_bytes(scope):
    _,n=metadata()
    raw=n['template_bytes']
    f.require(f.sha(raw.encode())==n['template_sha256'],'NATIVE_TEMPLATE_PIN')
    lines=raw.splitlines()
    changes={'Description':'Reviewed L arm notebook preparation; data execution held',
             'ConditionPathExists':scope['new_lane']+'/lane.json',
             'WorkingDirectory':n['root'],
             'ExecStart':'/usr/bin/python3 -s -B '+n['root']+'/'+ENTRY}
    changes['ExecStart']+=' run'
    for key,value in changes.items():
        positions=[i for i,line in enumerate(lines) if line.startswith(key+'=')]
        f.require(len(positions)==1,'EXACT_TEMPLATE_FIELD')
        lines[positions[0]]=key+'='+value
    positions=[i for i,line in enumerate(lines) if line.startswith('Environment=PYTHONPATH=')]
    f.require(len(positions)==1,'EXACT_TEMPLATE_PYTHONPATH')
    i=positions[0];parts=lines[i].split('=',2)[2].split(':')
    f.require(parts[0]==n['template_root'],'ORIGINAL_SOURCE_ROOT')
    lines[i]='Environment=PYTHONPATH='+':'.join([n['root'],*parts[1:]])
    positions=[i for i,line in enumerate(lines) if line.startswith('ReadWritePaths=')]
    f.require(len(positions)==1,'EXACT_TEMPLATE_WRITES')
    i=positions[0];paths=lines[i].split('=',1)[1].split()
    f.require(paths.count(n['template_work'])==1,'ORIGINAL_WORK_ROOT')
    lines[i]='ReadWritePaths='+' '.join(n['work'] if p==n['template_work'] else p for p in paths)
    for required in ['User=partho','Group=partho','Restart=no','TimeoutStartSec=3700',
                     'KillMode=control-group','UMask=0077','NoNewPrivileges=true',
                     'ProtectSystem=strict','PrivateTmp=true']:
        f.require(lines.count(required)==1,'NATIVE_PROTECTION_CHANGED')
    f.require([x for x in lines if x.startswith(('ExecStartPre=','ExecStopPost='))]==
              [x for x in raw.splitlines() if x.startswith(('ExecStartPre=','ExecStopPost='))],
              'HOST_HOOKS_CHANGED')
    return ('\n'.join(lines)+'\n').encode()


def reviewed(folder):
    from orchestrator.autonomy_review import verify_result
    scope,n=metadata();folder=trusted(folder);result=verify_result(folder)
    manifest=json.loads(trusted(folder/'packet-manifest.json').read_bytes())
    report=json.loads(trusted(folder/'report.md').read_bytes())
    f.require(result['verdict']=='APPROVE' and result['change_id']==CHANGE and report['findings']==[]
              and result['runtime_sha256']==f.sha(trusted(n['runtime']).read_bytes()),'INDEPENDENT_NATIVE_APPROVAL')
    for name in [ENTRY,f.DOCUMENT,'orchestrator/colab_arm_question.py','docs/COLAB_L_NATIVE_PRIVATE.json',
                 'orchestrator/autonomy_accounting.py','orchestrator/manual_driver.py',
                 'orchestrator/manual_stage.py','tests/test_colab_arm_question.py']:
        f.require(name in manifest['source_files'],'WHOLE_NATIVE_COMPONENT_REQUIRED')
    return result,manifest


def authority():
    scope,n=metadata();root=Path(n['root']);record=Path(n['record'])
    f.require(Path(__file__).resolve()==root/ENTRY,'INSTALLED_NATIVE_PATH')
    result,manifest=reviewed(record/'review')
    installed=json.loads(trusted(record/'INSTALLED.json').read_bytes())
    f.require(installed=={'source':result['source_sha'],'review_sha256':result['report_sha256'],
              'files':manifest['source_files'],'unit_sha256':f.sha(unit_bytes(scope)),
              'status':'INSTALLED_HELD'},'INSTALL_RECEIPT_CHANGED')
    for name,pin in installed['files'].items():
        f.require(f.sha(trusted(root/name).read_bytes())==pin,'INSTALLED_SOURCE_CHANGED')
    f.require(trusted('/etc/systemd/system/'+n['unit']).read_bytes()==unit_bytes(scope),'INSTALLED_UNIT_CHANGED')
    return result


def held_prior():
    for unit in ['research-colab-simple-admission-20261012.service',
                 'research-colab-multiwin-runtime-recovery-20261012.service',
                 'research-colab-patch-reading-recovery-20261012.service',
                 'research-colab-pnorm-v2-question-20261012.service',
                 'research-colab-pnorm-v2-feedback-import-20261012.service',
                 'research-pnorm-v2-review-turns-20261012.service']:
        fields=dict(line.split('=',1)for line in subprocess.check_output(
            ['systemctl','show',unit,'-p','MainPID','-p','ActiveState'],text=True).splitlines())
        f.require(fields['MainPID']=='0' and fields['ActiveState'] in {'inactive','failed'},'PRIOR_UNIT_LIVE')


def connect_qualifier():
    prior=load('_pnormct_existing_terminal_qualifier',
        Path('/opt/research-system/manual-repair-helpers/colab-simple-admission-20261012/tools/colab_simple_runtime.py'))
    approved=prior.authority()
    f.require(approved['source_sha']=='0770e23ac2bf257edc819b2e3f6e2a2693e12095' and
              approved['report_sha256']=='93871cd5a9ccae13b9d68f5cd01457cff20b80aad3c55d457cbaa30777c7210d','PRIOR_APPROVAL')
    prior.connect_qualifier()


def install(source,review):
    f.require(os.getuid()==0 and sys.flags.no_user_site,'ROOT_INSTALL_REQUIRED')
    from tools.install_preparation_branch_repair import mkdir,put,relative,OWNER_CHECK
    from tools.install_preparation_runtime import standalone_git,verify_units
    scope,n=metadata();source=trusted(source);review=trusted(review)
    result,manifest=reviewed(review);standalone_git(source)
    git=lambda *args:subprocess.check_output(['git',*args],cwd=source,text=True).strip()
    f.require(git('rev-parse','HEAD')==result['source_sha'] and git('branch','--show-current')==BRANCH
              and not git('status','--porcelain'),'CLEAN_NATIVE_SOURCE')
    for name,pin in manifest['source_files'].items():
        f.require(f.sha(trusted(source/relative(name)).read_bytes())==pin,'REVIEWED_SOURCE_CHANGED')
    f.require((source/ENTRY).read_bytes()==Path(__file__).read_bytes(),'EXECUTED_INSTALLER_CHANGED')
    held_prior()
    f.require(f.sha(trusted(n['template_unit']).read_bytes())==n['template_sha256'],'PRIOR_UNIT_CHANGED')
    root,record,work=map(Path,(n['root'],n['record'],n['work']));unit=Path('/etc/systemd/system')/n['unit']
    for dest in (root,record,work,unit):
        trusted(dest.parent);f.require(not dest.exists() and not dest.is_symlink(),'EXISTING_INSTALL_RECONCILE')
    import shutil
    f.require(all(shutil.disk_usage(path.parent).free>8*2**30 for path in (root,record,work)),'DISK_STOP')
    f.require(json.loads(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',OWNER_CHECK],text=True))['status']=='NO_RUNNING_CALL','LIVE_MODEL_CALL')
    verify_units({unit:unit_bytes(scope)})
    mkdir(record);put(record/'INSTALL_INTENT.json',f.encoded({'source':result['source_sha'],'review_sha256':result['report_sha256']}))
    subprocess.run(['git','clone','--no-local','--depth','1','--single-branch','--branch',BRANCH,str(source),str(root)],check=True,capture_output=True)
    for path in [root,*root.rglob('*')]:
        f.require(not path.is_symlink(),'INSTALLED_SOURCE_ALIAS');os.chown(path,0,1003)
        path.chmod(0o550 if path.is_dir() or path.stat().st_mode&0o111 else 0o440)
    for path in review.iterdir():
        f.require(path.is_file() and not path.is_symlink(),'FLAT_REVIEW_REQUIRED');put(record/'review'/path.name,trusted(path).read_bytes())
    work.mkdir(mode=0o700);os.chown(work,1003,1003)
    put(unit,unit_bytes(scope))
    put(record/'INSTALLED.json',f.encoded({'source':result['source_sha'],'review_sha256':result['report_sha256'],
        'files':manifest['source_files'],'unit_sha256':f.sha(unit_bytes(scope)),'status':'INSTALLED_HELD'}))
    subprocess.run(['systemctl','daemon-reload'],check=True)
    return {'status':'INSTALLED_HELD','scientific_calls':0,'provider_calls':0}


def service(action):
    f.require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,'SERVICE_OWNER_REQUIRED')
    approval=authority();scope,n=metadata();held_prior()
    f.require(os.environ.get('RESEARCH_MANUAL_RUNTIME_CONFIG')==n['runtime'],'EXACT_RUNTIME_REQUIRED')
    os.environ.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=n['root'])
    from orchestrator import manual_stage, private_records as pr
    from orchestrator.analysis_driver import AnalysisDriver,initialize
    from orchestrator.manual_executor import lock
    connect_qualifier()
    from orchestrator import colab_pnormct_policy
    colab_pnormct_policy.connect()
    if action=='prepare':
        from orchestrator import autonomy_review as review
        packet=trusted(n['packet']);manifest=review.verify_packet(packet)
        frozen=json.loads(trusted(Path(n['record'])/'review/packet-manifest.json').read_bytes())
        f.require(manifest==frozen,'QUALIFIED_CONTEXT_PACKET')
        plan_path=trusted(packet/'evidence/colab-preparation-plan.json')
        plan=json.loads(plan_path.read_bytes())
        context=Path(n['work'])/'protected-context'
        f.require(plan['context']==str(context) and not context.exists() and
                  not Path(scope['new_lane']).exists(),'EXCLUSIVE_NEW_PREPARATION')
        f.validate_scope(plan)
        inputs={}
        for name,pin in plan['context_files'].items():
            f.require(not Path(name).is_absolute() and '..' not in Path(name).parts,'CONTEXT_PATH')
            candidate=packet/'evidence/context'/name
            if candidate.exists():
                raw=trusted(candidate).read_bytes()
            else:
                # Unchanged private cohort metadata stays outside model packets.
                # Its exact bytes were already frozen by the operator.
                f.require(scope['prior']['context_files'].get(name)==pin,'UNREVIEWED_NEW_CONTEXT')
                raw=pr.check(Path(scope['prior']['config']['context'])/name).read_bytes()
            f.require(f.sha(raw)==pin,'FROZEN_CONTEXT_CHANGED')
            inputs[name]=raw
        intent=Path(n['work'])/'PREPARE_INTENT.json'
        f.require(not intent.exists() and not intent.is_symlink(),'PREPARATION_ALREADY_ATTEMPTED')
        pr.write_bytes(intent,f.encoded({'plan_sha256':f.sha(plan_path.read_bytes()),
            'scope_sha256':f.DOCUMENT_SHA,'model_calls':0,'provider_calls':0}))
        pr.mkdir(context)
        for name,raw in inputs.items():pr.write_bytes(context/name,raw)
        result=initialize(n['root'],scope['new_lane'],Path(n['record'])/'review/report.md',plan_path)
        pr.write_bytes(Path(n['work'])/'PREPARED.json',f.encoded(result))
        return result
    from orchestrator.colab_pnorm_v2_feedback import prepared
    driver=prepared(AnalysisDriver)(scope['new_lane'])
    try:
        f.validate(driver.store,f.RUN)
        f.require(manual_stage.scientific_stage_timeout('run_spec_author')==1800,'AUTHOR_TIMEOUT')
        if action=='status':return {**driver.status(),'transition':snapshot(driver)}
        f.require(action=='run' and bool(os.environ.get('INVOCATION_ID')),'NATIVE_INVOCATION_REQUIRED')
        operation=json.loads(trusted(Path(n['record'])/'OPERATION.json').read_bytes())
        f.require(operation['source']==approval['source_sha'] and operation['review_sha256']==approval['report_sha256']
                  and operation['transition']==snapshot(driver),'NATIVE_OPERATION_BINDING')
        if operation['mode']=='probe':return probe(driver)
        f.require(operation['mode']=='advance','NATIVE_OPERATION_MODE')
        receipt=json.loads((driver.state.parent/'qualification'/'COMPLETE.json').read_bytes())
        f.require(receipt['source']==approval['source_sha'] and receipt['status']=='PASS'
                  and receipt['model_calls']==0,'NATIVE_PROBE_REQUIRED')
        f.require(driver.current()['phase'] in f.STAGES|{'MODEL_RUNNING'},'PREPARATION_STAGES_ONLY')
        return driver.advance()
    finally:driver.store.db.close();driver.store.batch.db.close()



def snapshot(driver):
    return f.sha(f.encoded({'source':driver.config['source'],'state':driver.current(),
        'calls':[dict(row) for row in driver.store.db.execute('SELECT * FROM manual_calls ORDER BY id')]}))


def probe(driver):
    """Run the actual isolated sender's hash sink, with no model reservation."""
    from orchestrator import manual_stage,private_records as pr
    from orchestrator.manual_executor import lock,atomic
    with lock(driver.state/'driver.lock'):
        driver.guard();before=snapshot(driver);value=driver.current()
        from orchestrator import manual_recovery
        f.require(driver.model_round_number(value)==1 and
                  manual_recovery.role_limit(driver.store,f.RUN,'run_spec_author')==1 and
                  manual_recovery.role_limit(driver.store,f.RUN,'run_spec_review')==4,
                  'INITIAL_AUTHOR_POLICY')
        allowance=f.batch_allowance(driver.store.batch,f.document())
        f.require(allowance['colab_allocation_used']==12,'EXACT_REMAINING_COLAB_ALLOCATION')
        f.require(value['phase']=='run_spec_author' and value['rounds']=={},'INITIAL_PROBE_PHASE')
        folder=driver.state.parent/'qualification';f.require(not folder.exists(),'PROBE_EXISTS_RECONCILE')
        pr.mkdir(folder);work=folder/'author'
        body,measurement=driver.prepare_input(value,'run_spec_author',work)
        pr.write_text(work/'prompt.md',body);atomic(work/'input-measurement.json',measurement)
        manual_stage.data_access_guard(work,'run_spec_author')
        f.require(manual_stage.preflight()==driver.config['clients'],'UNCHANGED_NATIVE_CLIENTS')
        from orchestrator import review_submission as rs
        rs.prepare(work,'scientific',{'call_id':f.sha((f.RUN+':run_spec_review:1').encode()),
            'run_id':f.RUN,'stage':'run_spec_review','source_sha':driver.config['source'],
            'runtime_sha256':driver.config['clients']['runtime_config_sha256'],
            'input_sha256':f.sha(body.encode())})
        argv=manual_stage.reviewer_command(work,'run_spec_review')
        f.require(argv[argv.index('--max-turns')+1]=='60','L_REVIEW_TURN_QUALIFICATION')
        atomic(work/'review-command-qualification.json',{'argv':argv,'model_calls':0})
        receipts=[manual_stage.transport_check(work,stage,f.sha(body.encode()))
                  for stage in ('run_spec_author','run_spec_review')]
        f.require(all(r['model_client_launched'] is False for r in receipts) and snapshot(driver)==before,
                  'NATIVE_PROBE_MUTATION')
        result={'status':'PASS','source':driver.config['source'],'transition':before,
                'model_calls':0,'provider_calls':0,'transport':receipts}
        atomic(folder/'COMPLETE.json',result);return result


def start(mode,transition):
    import fcntl
    f.require(os.getuid()==0 and sys.flags.no_user_site and mode in {'probe','advance'},'ROOT_START_REQUIRED')
    approval=authority();scope,n=metadata();held_prior()
    f.require(isinstance(transition,str) and len(transition)==64 and all(c in '0123456789abcdef'for c in transition),
              'EXACT_TRANSITION_REQUIRED')
    record=Path(n['record'])
    with (record/'start.lock').open('a') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        state=dict(line.split('=',1)for line in subprocess.check_output(
            ['systemctl','show',n['unit'],'-p','MainPID','-p','ActiveState'],text=True).splitlines())
        f.require(state['MainPID']=='0' and state['ActiveState'] in {'inactive','failed'},'NATIVE_UNIT_LIVE')
        command=['runuser','-u','partho','--','env','RESEARCH_MANUAL_RUNTIME_CONFIG='+n['runtime'],
                 'PYTHONPATH='+n['root'],'python3','-s','-B',n['root']+'/'+ENTRY,'status']
        current=json.loads(subprocess.check_output(command,text=True))
        f.require(current['transition']==transition and current['phase'] in f.STAGES|{'MODEL_RUNNING'},'STATE_CHANGED_OR_HELD')
        from tools.install_preparation_branch_repair import put,OWNER_CHECK
        f.require(json.loads(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',OWNER_CHECK],text=True))['status']=='NO_RUNNING_CALL','LIVE_MODEL_CALL')
        intent=record/'operations'/(mode+'-'+transition+'.json')
        f.require(not intent.exists() and not intent.is_symlink(),'START_ALREADY_ATTEMPTED_RECONCILE')
        value={'mode':mode,'transition':transition,'source':approval['source_sha'],
               'review_sha256':approval['report_sha256'],'unit':n['unit']}
        put(intent,f.encoded(value))
        # The selector contains no command: only these two reviewed modes.
        temp=record/'OPERATION.next'
        put(temp,f.encoded(value));os.replace(temp,record/'OPERATION.json')
        subprocess.run(['systemctl','start','--no-block',n['unit']],check=True)
        return {'status':'START_REQUESTED_RECONCILE_SAME_UNIT','unit':n['unit'],'mode':mode,'transition':transition}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['install','prepare','run','status','start'])
    parser.add_argument('--source',type=Path);parser.add_argument('--review',type=Path)
    parser.add_argument('--mode',choices=['probe','advance']);parser.add_argument('--transition');args=parser.parse_args()
    if args.action=='install':
        f.require(args.source is not None and args.review is not None and args.mode is None and args.transition is None,'INSTALL_ARGUMENTS')
        return install(args.source,args.review)
    f.require(args.source is None and args.review is None,'NO_SOURCE_OVERRIDE')
    if args.action=='start':return start(args.mode,args.transition)
    f.require(args.mode is None and args.transition is None,'NO_TRANSITION_OVERRIDE')
    return service(args.action)

if __name__=='__main__':
    os.umask(0o077);print(json.dumps(main(),sort_keys=True))
