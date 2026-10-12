"""Held item6 follow-up entry point, using the unchanged native model clients.

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

from orchestrator import item6_idea2_followup as f
from orchestrator.manual_host_guard import trusted

ENTRY='tools/item6_idea2_runtime.py'
BRANCH='astra/manual-item6-smoothing-terminal-20261012'
CHANGE='item6-smoothing-terminal-route-20261012'


def metadata():
    scope=f.document()
    return scope,scope['native']


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,trusted(path))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def unit_bytes(scope):
    n=scope['native'];raw=n['template_bytes']
    f.require(f.sha(raw.encode())==n['template_sha256'],'NATIVE_TEMPLATE_PIN')
    lines=raw.splitlines();root=n['root'];work=n['work'];parent=scope['prior']['parent_lane']
    replacements={
        'Description':'Reviewed item6 follow-up specification only; execution held',
        'ConditionPathExists':scope['new_lane']+'/lane.json',
        'WorkingDirectory':root,
        'ExecStart':'/usr/bin/python3 -s -B '+root+'/'+ENTRY+' run',
    }
    for key,value in replacements.items():
        found=[i for i,line in enumerate(lines)if line.startswith(key+'=')]
        f.require(len(found)==1,'EXACT_TEMPLATE_FIELD');lines[found[0]]=key+'='+value
    py=[i for i,line in enumerate(lines)if line.startswith('Environment=PYTHONPATH=')]
    f.require(len(py)==1,'EXACT_TEMPLATE_PYTHONPATH')
    old=lines[py[0]].split('=',2)[2];extra=old.split(':')[1:]
    lines[py[0]]='Environment=PYTHONPATH='+':'.join([root,*extra])
    writable=[i for i,line in enumerate(lines)if line.startswith('ReadWritePaths=')]
    f.require(len(writable)==1,'EXACT_TEMPLATE_WRITES')
    old_paths=lines[writable[0]].split('=',1)[1].split()
    old_state=n['template_state']
    f.require(old_paths.count(old_state)==1,'EXACT_PRIOR_STATE_MOUNT')
    # Replace, never extend, the writable research state. Old accepted lanes and
    # the installed source remain read-only under ProtectSystem=strict.
    lines[writable[0]]='ReadWritePaths='+' '.join(work if x==old_state else x for x in old_paths)
    for required in ['User=partho','Group=partho','Restart=no','TimeoutStartSec=3700',
                     'KillMode=control-group','UMask=0077','NoNewPrivileges=true',
                     'ProtectSystem=strict','PrivateTmp=true']:
        f.require(lines.count(required)==1,'NATIVE_PROTECTION_CHANGED')
    f.require([x for x in lines if x.startswith('ExecStartPre=')]==
              [x for x in raw.splitlines()if x.startswith('ExecStartPre=')],'EXISTING_HOST_ATTESTATION_CHANGED')
    return ('\n'.join(lines)+'\n').encode()


def reviewed(folder):
    from orchestrator.autonomy_review import verify_result
    scope,n=metadata();folder=trusted(folder);result=verify_result(folder)
    manifest=json.loads(trusted(folder/'packet-manifest.json').read_bytes())
    report=json.loads(trusted(folder/'report.md').read_bytes())
    f.require(result['verdict']=='APPROVE' and result['change_id']==CHANGE and report['findings']==[]
              and result['runtime_sha256']==f.sha(trusted(n['runtime']).read_bytes()),'INDEPENDENT_NATIVE_APPROVAL')
    for name in [ENTRY,f.DOCUMENT,'orchestrator/item6_idea2_followup.py',
                 'orchestrator/autonomy_accounting.py','orchestrator/manual_driver.py',
                 'orchestrator/manual_stage.py','tests/test_item6_idea2_followup.py']:
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
    scope,n=metadata();units=n['held_units']
    for selected in [part for unit in units for part in (unit,unit.removesuffix('.service')+'.timer')]:
        fields=dict(line.split('=',1)for line in subprocess.check_output(
            ['systemctl','show',selected,'-p','MainPID','-p','ActiveState'],text=True).splitlines())
        f.require(fields.get('MainPID','0')=='0' and fields['ActiveState'] in {'inactive','failed'},'PRIOR_UNIT_LIVE')
        enabled=subprocess.run(['systemctl','is-enabled',selected],capture_output=True,text=True)
        f.require(enabled.stdout.strip() in {'disabled','static','not-found'},'PRIOR_UNIT_ENABLED')


def connect_qualifier():
    """Reuse installed, independently approved classifiers; do not relaunch them."""
    f.require(f._TERMINAL_QUALIFIER is None,'QUALIFIER_ALREADY_CONNECTED')
    from orchestrator import administrative_terminal as terminal
    drive=Path('/opt/research-system/manual-repair-helpers/colab-drive-in-place-20261011')
    route=load('_idea2_prior_drive_authority',drive/'tools/colab_intake_identity_runtime.py')
    approved=route.authority()
    f.require(approved['source_sha']=='e0394b8b8fd94a2d9feca3ffb88c917aed55936b'
              and approved['report_sha256']=='6d5689352510f3dda16edf084da1901c8121deec88af11a0b204685fe5e0d34d',
              'HISTORICAL_DRIVE_APPROVAL')
    history=load('_idea2_drive_history',drive/'orchestrator/colab_drive_in_place.py')
    proof=load('_idea2_colab_terminal',drive/'orchestrator/colab_author_terminal.py')
    frozen=history.frozen();binding=proof.frozen()
    sender=load('_idea2_sender_terminal',Path('/opt/research-system/manual-repair-helpers/item4-author24-delivery-20261010/tools/item4_smoke_response_runtime.py'))
    # Its authority verifies every installed byte before its standalone terminal
    # function is used. connect(), recovery and model entry points are not called.
    sender.authority()
    def qualify(accounts,row):
        if row['id']=='af4547778fe7e1f35698089607ab524d08346618131512c232670b7ccbf02ab8':
            return sender.sender_qualification(row)
        if row['id']!=proof.CALL:return terminal.verify(row)
        # Reuse the same strict historical verifier already used by the
        # installed Colab preparation route; preserve all later rows/charges.
        from orchestrator.colab_premodel_terminal import historical_read
        return proof.qualify(row,binding,read_local=lambda value:historical_read(accounts.db,value,frozen))
    f._TERMINAL_QUALIFIER=qualify


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
    os.environ['GIT_CONFIG_COUNT']='1'
    os.environ['GIT_CONFIG_KEY_0']='safe.directory'
    os.environ['GIT_CONFIG_VALUE_0']=n['root']
    from orchestrator import manual_stage
    f.require(manual_stage.scientific_stage_timeout('run_spec_author')==1800,'AUTHOR_TIMEOUT')
    connect_qualifier()
    if action=='prepare':return f.prepare(Path(n['root']))
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    driver=ExperimentDriver(scope['new_lane'])
    try:
        if action=='run':
            f.require(bool(os.environ.get('INVOCATION_ID')),'NATIVE_INVOCATION_REQUIRED')
            operation=json.loads(trusted(Path(n['record'])/'OPERATION.json').read_bytes())
            f.require(operation['source']==approval['source_sha'] and operation['review_sha256']==approval['report_sha256']
                      and operation['transition']==snapshot(driver),'NATIVE_OPERATION_BINDING')
            f.validate(driver.store,f.RUN)
            if operation['mode']=='probe':return probe(driver)
            f.require(operation['mode']=='advance','NATIVE_OPERATION_MODE')
            receipt=json.loads((driver.state.parent/'qualification'/'COMPLETE.json').read_bytes())
            f.require(receipt['source']==approval['source_sha'] and receipt['status']=='PASS'
                      and receipt['model_calls']==0,'NATIVE_PROBE_REQUIRED')
            return driver.advance()
        with lock(driver.state/'driver.lock'):
            if action=='activate':
                f.terminal_ids(driver.store.batch,scope)
                return f.activate(driver.store,f.RUN)
            if action=='verify':
                selected=f._configuration(driver.store,f.RUN)
                f.require(selected is not None,'PREPARED_LANE_REQUIRED')
                f.terminal_ids(driver.store.batch,scope)
                f.batch_allowance(driver.store.batch,scope) if driver.store.batch.db.execute('SELECT 1 FROM events WHERE id=?',(f.EVENT,)).fetchone() else None
                return {'status':'VERIFIED_HELD','scientific_calls':0,'provider_calls':0}
            if action=='status':return {**driver.status(),'transition':snapshot(driver)}
            raise ValueError('IDEA2_NATIVE_ACTION')
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
        f.require(value['phase']=='run_spec_author' and value['rounds']==f.document()['offsets'],'INITIAL_PROBE_PHASE')
        from orchestrator.manual_recovery import role_limit
        next_round=driver.model_round_number(value)
        f.require(next_round==f.document()['offsets']['run_spec_author']+1,
                  'EXACT_NEXT_AUTHOR_ROUND')
        f.require(next_round <= role_limit(driver.store,f.RUN,'run_spec_author'), 'ACTUAL_AUTHOR_ROLE_ADMISSION')
        folder=driver.state.parent/'qualification';f.require(not folder.exists(),'PROBE_EXISTS_RECONCILE')
        pr.mkdir(folder);work=folder/'author'
        body,measurement=driver.prepare_input(value,'run_spec_author',work)
        pr.write_text(work/'prompt.md',body);atomic(work/'input-measurement.json',measurement)
        manual_stage.data_access_guard(work,'run_spec_author')
        f.require(manual_stage.preflight()==driver.config['clients'],'UNCHANGED_NATIVE_CLIENTS')
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
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['install','prepare','activate','verify','run','status','start'])
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
