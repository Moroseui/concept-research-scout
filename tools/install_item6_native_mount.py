"""Install one approved item6 component held; no model/provider/ledger writes."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
from orchestrator import autonomy_review as review
from orchestrator.manual_host_guard import trusted
from tools import item6_native_mount_service as service
from orchestrator import diagnostics_mount_retry as retry

RUNTIME='/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json'
RUNTIME_SHA='dbd849b9267ece5ff231ca7d45710d1bdb24e9294caa8f2e0d694e7394dd595d'
SDK='/var/lib/research-system-autonomy/preparation/m3-modal-sdk-1.6.0/venv/lib/python3.12/site-packages'
BASE_UNITS={'execute':'research-item6-input-provisioning-20261007-execute.service',
            'science':'research-daily50-and-image-probe-20261007-item6.service'}
UNIT_PREFIX='research-'+retry.CHANGE+'-'

def require(ok,why):
    if not ok:raise ValueError(why)
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()

def unit_text(original,mode):
    require(mode in {'execute','science','state'},'MOUNT_INSTALL_UNIT_MODE')
    lines=original.splitlines();old=[x for x in lines if x.startswith('ExecStart=')]
    expected=('ExecStart=/usr/bin/python3 -s -B '+str(service.INPUT_ROOT)+'/tools/item6_input_service.py advance'
        if mode=='execute' else 'ExecStart=/usr/bin/python3 -s -B '+str(service.DAILY)+'/tools/daily_limit_component.py 6')
    require(old==[expected],'MOUNT_INSTALL_ORIGINAL_COMMAND')
    # All confinement, account, preflight, timeout and write paths stay byte-for-byte.
    return original.replace(expected,'ExecStart=/usr/bin/python3 -s -B '+str(service.ROOT)+'/tools/item6_native_mount_service.py '+mode)


def owner_snapshot():
    code=r"""import os,json,sqlite3,hashlib
from pathlib import Path
assert os.getuid()==1003
root=Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339')
result={}
for name,path in [('item6',root/'lane/jobs.sqlite'),('item4',root/'item4/lane/jobs.sqlite'),('global',Path('/var/lib/research-system-autonomy/reviews/jobs.sqlite'))]:
 with sqlite3.connect(path.as_uri()+'?mode=ro',uri=True) as db:
  db.row_factory=sqlite3.Row
  if name=='global':
   assert db.execute("SELECT count(*) FROM autonomy_calls WHERE status='RUNNING'").fetchone()[0]==0
   parent=db.execute('SELECT * FROM autonomy_compute WHERE id=?',('d9bd52cf0b27045e1e23ba018ac44d9ed25cb2ab8ccf81f8c22cf33b4fb264e3',)).fetchone()
   assert parent['status']=='RUNNING' and parent['reserved_micro_usd']==1951600 and parent['provider_id']=='sb-01M4CJFPRC3SJ1ZXPXG6APJA5H'
   assert db.execute("SELECT count(*) FROM autonomy_compute WHERE status='UNCERTAIN'").fetchone()[0]==0
  else:
   value=json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
   assert value['phase']!='MODEL_RUNNING'
   if name=='item6':assert value['phase']=='EXECUTE_EXPERIMENT'
  tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
  rows={t:[tuple(r) for r in db.execute('SELECT * FROM "'+t.replace('"','""')+'" ORDER BY rowid')] for t in tables}
  result[name]=hashlib.sha256(json.dumps(rows,sort_keys=True,default=str).encode()).hexdigest()
print(json.dumps(result))
"""
    return json.loads(subprocess.check_output(['runuser','-u','partho','--','/usr/bin/python3','-s','-B','-c',code],text=True))


def idle():
    active=subprocess.check_output(['systemctl','list-units','--all','--type=service','--state=active,activating','--no-legend','--no-pager','research-*'],text=True)
    require(not active.strip(),'MOUNT_INSTALL_RESEARCH_SERVICE_ACTIVE')
    for unit in BASE_UNITS.values():
        props=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',unit,'--property=ActiveState,MainPID,ControlGroup'],text=True).splitlines())
        require(props['ActiveState'] in {'inactive','failed'} and props['MainPID']=='0' and not props['ControlGroup'],'MOUNT_INSTALL_UNIT_ACTIVE')
    require(subprocess.check_output(['systemctl','is-active','research-item6-input-provisioning-20261007-cleanup.timer'],text=True).strip()=='active','MOUNT_INSTALL_RETENTION_REQUIRED')


def install(source,commit,folder):
    require(os.getuid()==os.geteuid()==0,'MOUNT_INSTALL_ROOT_ONLY')
    require(service.CHANGE==retry.CHANGE and service.ROOT==retry.ROOT and service.RECORD==retry.RECORD,
        'MOUNT_INSTALL_COMPONENT_IDENTITY')
    source=trusted(Path(source));folder=trusted(Path(folder));root=service.ROOT;record=service.RECORD
    require(not root.exists() and not record.exists(),'MOUNT_INSTALL_EXISTS_RECONCILE')
    trusted(root.parent);trusted(record.parent)
    require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()==commit
        and not subprocess.check_output(['git','status','--porcelain'],cwd=source),'MOUNT_INSTALL_CLEAN_SOURCE')
    require(Path(__file__).read_bytes()==(source/'tools/install_item6_native_mount.py').read_bytes(),'MOUNT_INSTALL_EXECUTED_SOURCE')
    approved=review.verify_result(folder);manifest=json.loads((folder/'packet-manifest.json').read_bytes())
    report=json.loads((folder/'report.md').read_bytes())
    require(approved['verdict']==report['verdict']=='APPROVE' and report['findings']==[]
        and approved['change_id']==retry.CHANGE and approved['source_sha']==commit
        and approved['runtime_sha256']==RUNTIME_SHA,'MOUNT_INSTALL_GENUINE_APPROVAL')
    bodies={name:(source/name).read_bytes() for name in service.FILES}
    require(all(sha(raw)==manifest['source_files'][n] for n,raw in bodies.items()),'MOUNT_INSTALL_REVIEWED_BYTES')
    require(sha(bodies['docs/ITEM6_NATIVE_MOUNT_AUTHORITY_20261008.txt'])==retry.AUTHORITY and sha(bodies['docs/ITEM6_CONTRACT_RETRY_OPERATOR_APPROVAL_20261008.txt'])==retry.REPAIR_AUTHORITY,'MOUNT_INSTALL_AUTHORITY')
    require(sha(trusted(RUNTIME).read_bytes())==RUNTIME_SHA,'MOUNT_INSTALL_RUNTIME_CHANGED')
    idle();before=owner_snapshot()
    parent=service.STATE/'modal-executions'/retry.PRIOR_JOB/'failed-stop-20261008.json'
    # Existing service-owned positive result/termination record is root sealed
    # only after exact contents and the fresh owner ledger have been reconciled.
    st=parent.lstat();require(not parent.is_symlink() and st.st_uid==1003 and not st.st_mode&0o077,'MOUNT_INSTALL_PARENT_RECORD_OWNER')
    stopped=parent.read_bytes();value=json.loads(stopped)
    require(sha(stopped)==retry.FAILED_SHA,'MOUNT_INSTALL_FAILED_PARENT_CHANGED')
    controls=(parent.parent/'native-mount-controls.json').read_bytes()
    require(sha(controls)==retry.CONTROLS_SHA,'MOUNT_INSTALL_ORIGINAL_CONTROLS_CHANGED')
    retry.prior_permit()
    require(value['result']=={'binding_sha256':retry.PARENT,'files':{},'schema':'modal-result/v1','status':'FAILED'}
        and value['stop']=={'provider_id':retry.PROVIDER_ID,'terminated':True} and value['reservation_retained'] is True,'MOUNT_INSTALL_PARENT_NOT_TERMINAL')
    templates={mode:trusted(Path('/etc/systemd/system')/name).read_text() for mode,name in BASE_UNITS.items()}
    units={str(Path('/etc/systemd/system')/(UNIT_PREFIX+mode+'.service')):unit_text(templates['execute' if mode=='execute' else 'science'],mode).encode() for mode in ('execute','science','state')}
    require(not any(Path(p).exists() for p in units),'MOUNT_INSTALL_UNIT_EXISTS')
    base={RUNTIME:RUNTIME_SHA}
    for release in (service.SCIENCE,service.SPENDING):
        for name in ('diagnostics_contract','diagnostics_modal','modal_volume_path','experiment_result','private_records','scientific_view_scan','privacy_patterns'):
            rel='orchestrator/'+name+'.py';path=trusted(Path(release)/rel);pin=sha(path.read_bytes())
            require(pin==manifest['source_files'][rel],'MOUNT_INSTALL_BASE_SOURCE_CHANGED');base[str(path)]=pin
    for mode,name in BASE_UNITS.items():base[str(Path('/etc/systemd/system')/name)]=sha(templates[mode].encode())
    root.mkdir(mode=0o750);record.mkdir(mode=0o750)
    def put(path,raw,mode=0o440):
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o750)
        with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        os.chown(path,0,1003);path.chmod(mode)
    put(record/'intent.json',encoded({'source':commit,'review':approved,'before':before,'held':True,'model_calls':0,'provider_calls':0}))
    for name,raw in bodies.items():put(root/name,raw)
    for p in folder.iterdir():
        require(p.is_file() and not p.is_symlink(),'MOUNT_INSTALL_REVIEW_MEMBER')
        put(record/'review'/p.name,p.read_bytes())
    put(record/'parent-failed-stop.json',stopped)
    put(record/'native-mount-controls.json',controls)
    permit={'schema':'item6-native-mount-permit/v1','parent':retry.PARENT,'provider_id':retry.PROVIDER_ID,
        'base_selection_sha256':retry.BASE_SELECTION,'original_reserved_micro_usd':3903200,'repair_authority_sha256':retry.REPAIR_AUTHORITY,
        'authority_sha256':retry.AUTHORITY,'descriptor':retry.descriptor(approved['report_sha256'])}
    put(record/'permit.json',encoded(permit))
    for p,raw in units.items():put(Path(p),raw,0o644)
    files={str(p):{'sha256':sha(p.read_bytes()),'mode':p.stat().st_mode&0o777} for p in [*root.rglob('*'),*record.rglob('*'),*[Path(x) for x in units]] if p.is_file()}
    put(record/'FILES.json',encoded(files))
    installed={'change':retry.CHANGE,'source':commit,'review_sha256':approved['report_sha256'],'authority_sha256':retry.AUTHORITY,
        'component_files':list(service.FILES),'layout':{'release':str(root)},'base_files':base,
        'units':{p:sha(raw) for p,raw in units.items()},'files_sha256':sha(encoded(files))}
    put(record/'installed.json',encoded(installed))
    for directory in [root,record,*[p for p in root.rglob('*') if p.is_dir()],*[p for p in record.rglob('*') if p.is_dir()]]:
        os.chown(directory,0,1003);directory.chmod(0o550)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    subprocess.run(['systemd-analyze','verify',*units],check=True,capture_output=True)
    require(owner_snapshot()==before,'MOUNT_INSTALL_LEDGER_CHANGED');idle()
    put(record/'complete.json',encoded({'status':'PASS','held':True,'provider_calls':0,'model_calls':0}))
    try:
        checks={}
        for mode,release in [('verify-execute',service.SPENDING),('verify-science',service.SCIENCE)]:
            cmd=['runuser','-u','partho','--','env','PYTHONPATH='+release+':'+SDK,'RESEARCH_MANUAL_RUNTIME_CONFIG='+RUNTIME,
                '/usr/bin/python3','-s','-B',str(root/'tools/item6_native_mount_service.py'),mode]
            checks[mode]=json.loads(subprocess.check_output(cmd,text=True,timeout=90))
            require(checks[mode]=={'status':'PASS','mode':mode,'model_calls':0,'provider_calls':0},'MOUNT_INSTALL_OWNER_POSTCHECK')
        require(owner_snapshot()==before,'MOUNT_INSTALL_LEDGER_CHANGED');idle()
    except BaseException:
        temp=record/'complete.failed.json';put(temp,encoded({'status':'FAILED_POSTCHECK','held':True}));os.replace(temp,record/'complete.json');raise
    put(record/'APPLIED.json',encoded({'status':'INSTALLED_HELD','checks':checks,'before':before,'after':owner_snapshot(),'original_charge_preserved':True}))
    return {'status':'INSTALLED_HELD','source':commit,'model_calls':0,'provider_calls':0}


def main():
    p=argparse.ArgumentParser()
    for name in ('source','commit','review-folder'):p.add_argument('--'+name,required=True)
    a=p.parse_args();print(json.dumps(install(a.source,a.commit,a.review_folder),sort_keys=True))
if __name__=='__main__':main()
