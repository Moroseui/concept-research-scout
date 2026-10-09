"""Install/run the one reviewed item6 preparation helper; original engine intact."""
import argparse
import base64
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from orchestrator import private_records as pr, spending_continuation as sc
from orchestrator.manual_executor import digest, read
from orchestrator.manual_driver import write_once
from orchestrator.modal_executor import canonical
from orchestrator.manual_host_guard import trusted
from tools import manual_promotion as promotion
try:
    from tools import item6_input_preparation as prep
except ImportError:
    import item6_input_preparation as prep

ROOT='/opt/research-system/manual-repair-helpers/item6-input-provisioning-20261007'
RECORD='/var/lib/research-system-manual-sprint10-deployment/item6-input-provisioning-20261007'
CONFIG='/etc/research-system-manual-sprint10/item6-input-provisioning-20261007/config.json'
STATE=RECORD+'/state'
UNIT='research-item6-input-provisioning-20261007'
FILES=('tools/item6_input_preparation.py','tools/item6_input_service.py',
       'tools/environment_inventory_service.py','docs/ITEM6_INPUT_PROVISIONING_AUTHORITY_20261007.txt')
STATE_LANE='/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/lane'
SELECTION='/var/lib/research-system-manual-sprint10-deployment/directions-20261006/item6-execution-selection'
FROZEN_INPUT='/etc/research-system-manual-sprint10/item6-input-provisioning-20261007/inputs'
REQUIREMENTS={'python':'3.12','distributions':{'numpy':'2.1.3','scipy':'1.16.3','nibabel':'5.4.2'}}


def config_check(config):
    prep.require(set(config)=={'schema','state','batch_ledger','reviewed_requirements','provider',
        'contract_path','cohort_path','capture_path','split_path','data_root','selection_root'},'INPUT_SERVICE_FIELDS')
    prep.require(config['schema']=='item6-input-preparation/v1' and config['state']==STATE
        and config['batch_ledger']=='/var/lib/research-system-autonomy/reviews'
        and config['data_root']==STATE+'/data' and config['selection_root']==SELECTION,'INPUT_SERVICE_PATHS')
    p=config['provider']
    prep.require(set(p)=={'sdk_package','sdk_sha256','credential_file','workspace'}
        and p['credential_file']==prep.CREDENTIAL and p['workspace']=='moroseui','INPUT_SERVICE_PROVIDER')
    from tools.direct_storage_service import safe
    safe(p['sdk_package'])
    prep.require(re.fullmatch('[a-f0-9]{64}',p['sdk_sha256']),'INPUT_SERVICE_SDK_PIN')
    for k,filename in [('contract','input-contract.json'),('cohort','cohort.json'),('capture','capture.jsonl'),('split','split.csv')]:
        prep.require(config[k+'_path']==FROZEN_INPUT+'/'+filename,'INPUT_SERVICE_FROZEN_PATH')
    ref=prep.cpu.reference(config['reviewed_requirements'])
    prep.require(ref['state']==STATE_LANE and ref['source']==sc.SOURCE and ref['program_sha256']==prep.PROGRAM_SHA
        and ref['reviewed_execution_sha256']==prep.REVIEW_SHA and ref['requirements']==REQUIREMENTS,'INPUT_SERVICE_REVIEW_SCOPE')
    return config


def service(config,release,runtime,command):
    config_check(config)
    prep.require(command in {'allocate','finalize','cleanup'},'INPUT_SERVICE_COMMAND')
    return f"""[Unit]
Description=Bounded reviewed item6 private preparation ({command})
After=network-online.target
Wants=network-online.target
[Service]
Type=oneshot
User=partho
Group=partho
UMask=0077
WorkingDirectory={release}
Environment=PYTHONPATH={release}:{config['provider']['sdk_package']}
Environment=RESEARCH_MANUAL_RUNTIME_CONFIG={runtime}
ExecStart=/usr/bin/python3 -s -B {ROOT}/tools/item6_input_service.py {command}
TimeoutStartSec=7200
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=true
ReadWritePaths={STATE} {config['batch_ledger']} {STATE_LANE}
RestrictSUIDSGID=true
LockPersonality=true
""".encode()


def timer():
    return f"""[Unit]
Description=Bounded item6 private-copy retention
[Timer]
OnBootSec=2min
OnUnitInactiveSec=5min
Unit={UNIT}-cleanup.service
[Install]
WantedBy=timers.target
""".encode()


def verify_installed():
    from orchestrator.autonomy_review import verify_result
    old=sc.implementation()
    rec=promotion.manifest_check(Path('/'),RECORD)
    prep.require(rec['change']==prep.CHANGE and rec['base_receipt_sha256']==digest(Path(sc.RECORD+'/installed.json').read_bytes()),'INPUT_SERVICE_BASE_CHANGED')
    approved=verify_result(trusted(rec['review_folder']))
    prep.require((approved['change_id'],approved['verdict'],approved['source_sha'],approved['runtime_sha256'],approved['report_sha256'])==
        (prep.CHANGE,'APPROVE',rec['source'],sc.RUNTIME,rec['review_sha256']),'INPUT_SERVICE_IMPLEMENTATION_APPROVAL')
    manifest=read(Path(rec['review_folder'])/'packet-manifest.json')
    for name in FILES:
        prep.require(digest(trusted(Path(ROOT)/name).read_bytes())==manifest['source_files'][name],'INPUT_SERVICE_REVIEWED_SOURCE_CHANGED')
    prep.require(Path(__file__).resolve()==Path(ROOT)/'tools/item6_input_service.py'
        and Path(prep.__file__).resolve()==Path(ROOT)/'tools/item6_input_preparation.py','INPUT_SERVICE_IMPORTED_RUNTIME')
    prep.require(read(trusted(Path(RECORD)/'complete.json')).get('status')=='PASS','INPUT_SERVICE_INSTALL_INCOMPLETE')
    config=config_check(read(trusted(CONFIG)))
    prep.require(digest(trusted(CONFIG).read_bytes())==rec['config_sha256'],'INPUT_SERVICE_CONFIG_CHANGED')
    return config,old,rec


@pr.private_umask
def install(source,commit,review_folder,config_file,input_folder):
    from orchestrator.autonomy_review import verify_result
    from tools.spending_repair_service import owner_preflight,destination_parent,unit as execution_unit
    prep.require(os.getuid()==os.geteuid()==0,'INPUT_INSTALL_ROOT')
    old=sc.implementation();source=Path(source);folder=Path(review_folder)
    approved=verify_result(folder)
    prep.require((approved['change_id'],approved['verdict'],approved['source_sha'],approved['runtime_sha256'])==
        (prep.CHANGE,'APPROVE',commit,sc.RUNTIME),'INPUT_INSTALL_REVIEW_REQUIRED')
    manifest=read(folder/'packet-manifest.json');files={}
    for name in FILES:
        raw=subprocess.check_output(['git','show',commit+':'+name],cwd=source)
        prep.require(digest(raw)==manifest['source_files'][name],'INPUT_INSTALL_REVIEWED_SOURCE')
        files[name]=raw
    prep.require(digest(files['docs/ITEM6_INPUT_PROVISIONING_AUTHORITY_20261007.txt'])==prep.AUTHORITY,'INPUT_INSTALL_AUTHORITY')
    prep.require(Path(__file__).read_bytes()==files['tools/item6_input_service.py']
        and Path(prep.__file__).read_bytes()==files['tools/item6_input_preparation.py'],'INPUT_INSTALL_EXECUTED_SOURCE')
    config=config_check(read(config_file))
    from orchestrator.manual_runtime import settings
    runtime=settings(file=old['previous']['runtime'])
    prep.require(runtime.get('modal_sdk')=={'package':config['provider']['sdk_package'],'sha256':config['provider']['sdk_sha256']},'INPUT_INSTALL_EXISTING_SDK')
    prep.cpu.reviewed(config['reviewed_requirements'])
    copied={k:(Path(input_folder)/Path(config[k+'_path']).name).read_bytes() for k in ('contract','cohort','capture','split')}
    contract=json.loads(copied['contract']);prep.require(digest(copied['contract'])==prep.CONTRACT_SHA,'INPUT_INSTALL_CONTRACT')
    prep.input_contract(contract,copied['cohort'],copied['capture']);prep.patient_membership(contract,copied['cohort'],copied['split'])
    units={UNIT+'-'+cmd+'.service':service(config,old['layout']['release'],old['previous']['runtime'],cmd)
           for cmd in ('allocate','finalize','cleanup')}
    units[UNIT+'-cleanup.timer']=timer()
    original=trusted('/etc/systemd/system/'+old['previous']['units'][0]).read_text()
    execution=execution_unit(original,old['previous']['release'],old['layout']['release'],STATE_LANE)
    previous_command='-m tools.spending_repair_service advance --state '+STATE_LANE
    prep.require(execution.decode().count(previous_command)==1,'INPUT_EXECUTION_UNIT_TEMPLATE')
    units[UNIT+'-execute.service']=execution.replace(previous_command.encode(),
        (ROOT+'/tools/item6_input_service.py advance').encode())
    paths=[ROOT,RECORD,str(Path(CONFIG).parent),STATE,*['/etc/systemd/system/'+x for x in units]]
    prep.require(all(not Path(x).exists() and not Path(x).is_symlink() for x in paths),'INPUT_INSTALL_EXISTS_RECONCILE')
    for destination in paths:
        parent=Path(destination).parent
        while not parent.exists():parent=parent.parent
        trusted(parent)
    prep.require(Path(SELECTION).is_dir() and not any(Path(SELECTION).iterdir()),'INPUT_INSTALL_SELECTION_NOT_EMPTY')
    trusted(SELECTION)
    before=owner_preflight(old['layout']['release'],old['previous'],continued=True)
    pr.mkdir(RECORD,parents=True);promotion.private_new(Path(RECORD)/'intent.json',{'source':commit,'before':before,'no_retry':True})
    listing={}
    def put(path,raw):
        path=Path(path);destination_parent(path);promotion.private_new(path,raw)
        listing[str(path)]={'sha256':digest(raw),'mode':path.stat().st_mode&0o777}
    for name,raw in files.items():put(Path(ROOT)/name,raw)
    for k,raw in copied.items():put(config[k+'_path'],raw)
    put(CONFIG,canonical(config))
    for name,raw in units.items():put('/etc/systemd/system/'+name,raw)
    for root in [Path(ROOT),Path(CONFIG).parent]:
        for path in sorted([root,*[p for p in root.rglob('*') if p.is_dir()]],reverse=True):promotion.private_mode(path,directory=True)
    pr.mkdir(STATE,parents=True);os.chown(STATE,1003,1003);os.chmod(STATE,0o700)
    receipt={'status':'PASS','change':prep.CHANGE,'source':commit,
             'layout':{'release':ROOT,'state':STATE,'units':list(units)},
             'base_receipt_sha256':digest(Path(sc.RECORD+'/installed.json').read_bytes()),
             'review_folder':str(folder),'review_sha256':approved['report_sha256'],
             'config_sha256':digest(canonical(config)),'scope':'One item6 preparation; no engine or lane migration'}
    promotion.private_new(Path(RECORD)/'FILES.json',listing)
    receipt['files_sha256']=digest((Path(RECORD)/'FILES.json').read_bytes())
    promotion.private_new(Path(RECORD)/'installed.json',receipt)
    after=owner_preflight(old['layout']['release'],old['previous'],continued=True)
    prep.require(after==before,'INPUT_INSTALL_CHANGED_EXISTING_STATE')
    promotion.private_new(Path(RECORD)/'complete.json',{'status':'PASS','before':before,'after':after,'provider_calls':0,'model_calls':0})
    promotion.private_mode(Path(RECORD),directory=True)
    return receipt


@pr.private_umask
def seal(image_proof):
    prep.require(os.getuid()==os.geteuid()==0,'INPUT_SELECTION_ROOT')
    config,old,rec=verify_installed();state=Path(config['state'])
    allocation=read(pr.check(state/'ALLOCATED.json'));value=read(pr.check(state/'binding.json'))
    prep.require(allocation['binding_sha256']==digest(canonical(value)) and value['config_sha256']==digest(canonical(config)),
                 'INPUT_SELECTION_PREPARATION_BINDING')
    # Root does not open ledgers or credentials; the existing owner verifies the
    # retained reservation and captures fresh billing before root publication.
    owner_code="import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);import item6_input_service as s;print(json.dumps(s.owner_selection_preflight()))"
    done=subprocess.run(['/usr/sbin/runuser','-u','partho','--','/usr/bin/env',
        'PYTHONPATH='+old['layout']['release']+':'+config['provider']['sdk_package'],
        'RESEARCH_MANUAL_RUNTIME_CONFIG='+old['previous']['runtime'],
        '/usr/bin/python3','-s','-B','-c',owner_code,ROOT+'/tools'],capture_output=True,text=True,check=True,timeout=120)
    observed=json.loads(done.stdout);contract,raws,membership=prep.inputs(config)
    proof=observed['image_proof'];proof_path=Path(SELECTION)/'image-provenance.json'
    prep.require(image_proof is None or str(image_proof)==str(proof_path),'INPUT_SELECTION_PROOF_PATH')
    base={'schema':'diagnostics-environment/v1','image_id':proof['scientific_environment']['image_id'],
          'requirements':config['reviewed_requirements']['requirements']}
    environment=prep.cpu.environment(base,proof)
    prep.require(proof['binding']['reviewed_requirements']==config['reviewed_requirements'],'INPUT_SELECTION_REVIEW')
    prep.require(not proof_path.exists() and not proof_path.is_symlink(),'INPUT_SELECTION_PROOF_EXISTS')
    promotion.private_new(proof_path,canonical(proof))
    assets={'app_name':allocation['app_name'],'app_id':allocation['app_id'],'image_id':base['image_id'],
            'environment':environment,'pinned_image_provenance':{'path':str(proof_path),'sha256':digest(proof_path.read_bytes())},
            'data_volume_id':allocation['volumes']['data'],'data_subpath':'/inputs',
            'package_volume_id':allocation['volumes']['package'],'input_contract':contract,
            'cohort':base64.b64encode(raws['cohort']).decode(),'source_capture':base64.b64encode(raws['capture']).decode()}
    selected={'schema':'diagnostics-execution-selection/v1','source':sc.SOURCE,'run_id':prep.policy.RUN_ID,
              'reviewed_execution_sha256':prep.REVIEW_SHA,'provider':{**config['provider'],'diagnostics_assets':assets},
              'resources':dict(prep.RESOURCES),'overhead_micro_usd':1_000_000,
              'cost':prep.quote(prep.RESOURCES,observed['billing']['rates'],1_000_000)}
    from tools.spending_repair_service import destination_parent
    target=Path(config['selection_root'])/'selection.json'
    prep.require(not target.exists() and not target.is_symlink(),'INPUT_SELECTION_EXISTS_RECONCILE')
    trusted(target.parent);promotion.private_new(target,prep.encoded(selected));return {'status':'SEALED','selection_sha256':digest(target.read_bytes())}


def owner_selection_preflight():
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator.modal_budget import ComputeAccounts
    from orchestrator.modal_provider import ModalProvider
    from datetime import datetime,timezone
    prep.require(os.getuid()==os.geteuid()==1003,'INPUT_PREP_SERVICE_ACCOUNT')
    config,old,rec=verify_installed();batch=BatchAccounts(config['batch_ledger'])
    try:
        accounts=ComputeAccounts(batch);value,ident,row=prep.retained(accounts,config['state'],config)
        prep.require(row['status']=='RESERVED','INPUT_SELECTION_RESERVATION')
        prep.assert_lifetime(config['state'],datetime.now(timezone.utc));prep.cpu.reviewed(config['reviewed_requirements'])
        from orchestrator.modal_pinned_image import consumer_proof
        image_state=Path('/var/lib/research-system-manual-sprint10/environment-inventory/item6-reviewed-cpu-image-v1')
        image_binding=read(pr.check(image_state/'binding.json'))
        proof=consumer_proof(accounts,image_binding,image_state)
        snapshot=ModalProvider(config['provider']).billing_snapshot()
        prep.recheck(accounts,value,ident,snapshot,datetime.now(timezone.utc))
        return {'binding_sha256':ident,'billing':snapshot,'image_proof':proof}
    finally:batch.db.close()


def run(command):
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator.modal_budget import ComputeAccounts
    from orchestrator.modal_provider import ModalProvider
    from orchestrator.remote_supervisor import lock
    prep.require(os.getuid()==os.geteuid()==1003,'INPUT_PREP_SERVICE_ACCOUNT')
    config,old,rec=verify_installed()
    props=subprocess.check_output(['/usr/bin/systemctl','show',UNIT+'-cleanup.timer',
            '--property=LoadState,UnitFileState,ActiveState'],text=True)
    prep.require(dict(x.split('=',1) for x in props.splitlines() if '=' in x)==
        {'LoadState':'loaded','UnitFileState':'enabled','ActiveState':'active'},'INPUT_PREP_SERVER_RETENTION_REQUIRED')
    properties={'User':'partho','Group':'partho','UMask':'0077','NoNewPrivileges':'yes',
                'ProtectSystem':'strict','ProtectHome':'read-only','PrivateTmp':'yes',
                'RestrictSUIDSGID':'yes','LockPersonality':'yes'}
    observed=subprocess.check_output(['/usr/bin/systemctl','show',UNIT+'-'+('cleanup' if command=='stage' else command)+'.service',
            '--property='+','.join(properties)],text=True)
    prep.require(dict(x.split('=',1) for x in observed.splitlines() if '=' in x)==properties,
                 'INPUT_PREP_SERVICE_RESTRICTIONS')
    with lock(Path(config['state'])/'preparation.lock'),lock(Path(STATE_LANE)/'driver.lock'):
        if command=='stage':return prep.stage(config,sys.stdin.buffer)
        batch=BatchAccounts(config['batch_ledger'])
        try:
            accounts=ComputeAccounts(batch)
            if command=='cleanup' and not (Path(config['state'])/'allocate-intent.json').exists():
                from datetime import datetime,timezone
                return prep.clear_staging(config,datetime.now(timezone.utc))
            provider=ModalProvider(config['provider'])
            result={'allocate':prep.allocated,'finalize':prep.finalize,'cleanup':prep.cleanup}[command](config,provider,accounts)
            pr.atomic(Path(config['state'])/'STATUS.json',{'command':command,**result});return result
        finally:batch.db.close()



def sdk_provider():
    """Use the installed provider, correcting only its App identity API call.

    The driver already supports an explicit provider factory. No installed
    module, package worker, credential loader, cost gate or sandbox is replaced.
    """
    from orchestrator.modal_provider import ModalProvider
    class Provider(ModalProvider):
        def preflight(self,config,binding,prepared):
            prep.require(binding.get('purpose')=='M4_ITEM6_CPU','INPUT_EXECUTION_ITEM6_ONLY')
            from orchestrator.diagnostics_execution import verify_prepared
            from orchestrator.diagnostics_modal import scope,verify_volume_members
            verify_prepared(prepared,binding);a=scope(self,config,binding)
            snapshot=self.billing_snapshot()
            prep.require(binding['cost']==prep.quote(binding['resources'],snapshot['rates'],binding['overhead_micro_usd']),
                         'DIAGNOSTICS_ACTUAL_RATE_CHANGED')
            files={k:{f:v[f] for f in ('sha256','bytes')} for k,v in a['input_contract']['files'].items()}
            verify_volume_members(self,a['data_volume_id'],files,prefix=a['data_subpath'])
            from orchestrator.manual_executor import inventory
            package={k:{'sha256':v,'bytes':(Path(prepared)/k).stat().st_size} for k,v in inventory(prepared).items()}
            self._verify_volume(a['package_volume_id'],package)
            app=self.modal.App.lookup(a['app_name'],create_if_missing=False,client=self.client)
            prep.require(app.app_id==a['app_id'],'DIAGNOSTICS_APP_BINDING')
            image=self.modal.Image.from_id(a['image_id'],client=self.client);image.build(app)
            prep.require(image.object_id==a['image_id'],'DIAGNOSTICS_IMAGE_BINDING')
            return {'status':'READY','billing_snapshot':snapshot,'image_id':image.object_id,
                    'input_contract_sha256':binding['input_contract_sha256'],
                    'package_inventory_sha256':digest(prep.encoded(package)),
                    'native_guard_required_before_analysis':True}
    return Provider


@pr.private_umask
def advance():
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    prep.require(os.getuid()==os.getgid()==1003,'INPUT_EXECUTION_OWNER')
    config,old,rec=verify_installed()
    state=Path(STATE_LANE)
    driver=ExperimentDriver(state)
    try:
        with lock(state/'driver.lock'):
            driver.guard();value=driver.current()
            prep.require(value['phase'] in {'EXECUTE_EXPERIMENT','COLLECT_EXPERIMENT'},'INPUT_EXECUTION_PHASE_ONLY')
            sc.lane(driver.store.batch,driver.config['run_id'],driver.config['owner_binding'],driver.config['source'])
            # The only behavioral substitution is the reviewed SDK App API fix.
            driver.provider_factory=sdk_provider()
            from orchestrator.experiment_package import advance as execute
            return execute(driver,value,None,None)
    finally:
        driver.store.db.close();driver.store.batch.db.close()


def image_install(config_file):
    prep.require(os.getuid()==os.geteuid()==0,'INPUT_IMAGE_INSTALL_ROOT')
    config,old,rec=verify_installed()
    spec=importlib.util.spec_from_file_location('reviewed_image_installer',ROOT+'/tools/environment_inventory_service.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    selected=read(config_file)
    prep.require(selected['source']==old['source'] and selected['release']==old['layout']['release']
        and selected['installation_record']==sc.RECORD and selected['installation_sha256']==rec['base_receipt_sha256']
        and selected['provider']==config['provider'] and selected['reviewed_requirements']==config['reviewed_requirements'],
        'INPUT_IMAGE_INSTALLED_BINDING')
    return module.install('/',selected)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['install','image-install','seal','stage','allocate','finalize','cleanup','advance'])
    for name in ('source','commit','review-folder','config-file','input-folder','image-proof'):parser.add_argument('--'+name)
    a=parser.parse_args()
    if a.command=='install':result=install(a.source,a.commit,a.review_folder,a.config_file,a.input_folder)
    elif a.command=='seal':result=seal(a.image_proof)
    elif a.command=='advance':result=advance()
    elif a.command=='image-install':result=image_install(a.config_file)
    else:result=run(a.command)
    print(json.dumps({k:v for k,v in result.items() if k in {'status','reserved_micro_usd','selection_sha256','spend'}},sort_keys=True))

if __name__=='__main__':main()
