# Protected one-use frozen-source preparation; no scientific dispatch.
from pathlib import Path
from datetime import datetime,timezone,timedelta
import importlib.util,json,os,sys,subprocess,stat,hashlib
CHANGE='item4-source-preparation-20261009'
REVIEW_CHANGE='item4-source-install-repair-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
CONFIG=Path('/etc/research-system-manual-sprint10')/CHANGE/'config.json'
STATE=RECORD/'state'
METADATA=CONFIG.parent/'inputs'
NATIVE_ROOT=Path('/opt/research-system/manual-repair-helpers/item4-native-cpu-rehearsal-20261008')
NATIVE_SOURCE='7e49eeb17f1fea1f8caa8709ec0422912bc17f3d'
NATIVE_REVIEW='8ceab8b02142b886ae3f5365aa696b9d4ca4f02be0c94b36adde923f7fa891b6'
DIRECT_STATE=Path('/var/lib/research-system-manual-sprint10/direct-inputs/fbb539893611cfab56c5a574313fc6b717b095e9')
DIRECT_CONFIG=Path('/etc/research-system-manual-sprint10/direct-inputs/fbb539893611cfab56c5a574313fc6b717b095e9/config.json')
DIRECT_CONFIG_SHA='b128ec14d1758f5ee4710f284515b6a6b97d357abb588eee2ed7798a29a4432b'
CACHE=Path('/var/lib/research-system-manual-sprint10-deployment/item6-input-provisioning-20261007/state/data/inputs/feature-cache-2mm-v2')
FILES=('orchestrator/modal_development_inputs.py','orchestrator/modal_source_composition.py','orchestrator/modal_source_budget.py',
       'tools/item4_source_preparation.py','tools/install_item4_source_preparation.py')
UNIT='research-item4-source-preparation.service'
CLEANUP='research-item4-source-retention.service'
TIMER='research-item4-source-retention.timer'
PROPS={'User':'partho','Group':'partho','UMask':'0077','NoNewPrivileges':'yes','ProtectSystem':'strict',
       'PrivateTmp':'yes','ProtectHome':'read-only','RestrictSUIDSGID':'yes','LockPersonality':'yes'}

def require(ok,why):
    if not ok:raise ValueError('SOURCE_SERVICE_'+why)

def native_helper():
    p=NATIVE_ROOT/'tools/item4_native_runtime.py'
    spec=importlib.util.spec_from_file_location('_source_native_helper',p);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    h.bootstrap();return h

def verify():
    h=native_helper();native,proof=h.verify(unit=False)
    require(proof['helper_source']==NATIVE_SOURCE and proof['helper_review_sha256']==NATIVE_REVIEW,'NATIVE_RELEASE')
    import orchestrator,tools
    orchestrator.__path__.insert(0,str(ROOT/'orchestrator'));tools.__path__.insert(0,str(ROOT/'tools'))
    from orchestrator.manual_host_guard import trusted
    from orchestrator.manual_executor import digest
    from orchestrator.autonomy_review import verify_result
    approval=verify_result(trusted(RECORD/'review'));record=json.loads(trusted(RECORD/'installed.json').read_bytes())
    manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes())
    require(approval['verdict']=='APPROVE' and approval['change_id']==REVIEW_CHANGE
            and approval['source_sha']==manifest['source_sha']==record['source']
            and approval['report_sha256']==record['review_sha256'],'GENUINE_APPROVAL')
    require(Path(__file__).resolve()==ROOT/'tools/item4_source_preparation.py','EXECUTED_SOURCE')
    for name in FILES:require(digest(trusted(ROOT/name).read_bytes())==manifest['source_files'][name],'SOURCE_HASH')
    from orchestrator import modal_source_composition as source,modal_source_budget as budget
    for m,name in [(source,'orchestrator/modal_source_composition.py'),(budget,'orchestrator/modal_source_budget.py')]:require(Path(m.__file__).resolve()==ROOT/name,'IMPORTED_SOURCE')
    raw=trusted(CONFIG).read_bytes();config=json.loads(raw)
    require(digest(raw)==record['config_sha256'] and config=={'schema':'item4-source-service/v1',
            'state':str(STATE),'metadata':str(METADATA),'provider':native['provider'],
            'batch_ledger':native['batch_ledger'],'base_source':native['source'],'owner_sha256':native['owner_sha256']},'CONFIG')
    source.contract(METADATA)
    for name,body in units(h.BASE,config).items():require(trusted(Path('/etc/systemd/system')/name).read_bytes()==body,'UNIT_BYTES')
    require(subprocess.check_output(['systemctl','is-active',TIMER],text=True).strip()=='active','RETENTION_TIMER')
    return h,native,config,record

def units(base,config):
    common=f'''[Unit]
Description=Bounded frozen development source copy
After=network-online.target
[Service]
Type=oneshot
User=partho
Group=partho
UMask=0077
WorkingDirectory={base}
Environment=PYTHONPATH={base}:{config['provider']['sdk_package']}
Environment=RESEARCH_MANUAL_RUNTIME_CONFIG=/etc/research-system-manual-sprint10/releases/{base.name}/runtime.json
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=true
ReadWritePaths={STATE} {config['batch_ledger']}
RestrictSUIDSGID=true
LockPersonality=true
'''
    return {UNIT:(common+f'ExecStart=/usr/bin/python3 -s -B {ROOT}/tools/item4_source_preparation.py prepare\nTimeoutStartSec=10800\n').encode(),
            CLEANUP:(common+f'ExecStart=/usr/bin/python3 -s -B {ROOT}/tools/item4_source_preparation.py cleanup\nTimeoutStartSec=10800\n').encode(),
            TIMER:f'[Unit]\nDescription=Frozen source retention\n[Timer]\nOnBootSec=2m\nOnUnitActiveSec=10m\nUnit={CLEANUP}\n[Install]\nWantedBy=timers.target\n'.encode()}

def intent(name,value):
    from orchestrator import private_records as pr
    from orchestrator.modal_executor import canonical
    with pr.open_file(STATE/(name+'.json'),'xb') as f:f.write(canonical(value))

def retained(accounts,config):
    from orchestrator import modal_source_budget as budget,private_records as pr
    from orchestrator.modal_executor import canonical
    from orchestrator.manual_executor import digest
    binding=json.loads(pr.check(STATE/'binding.json').read_bytes());budget.validate(binding)
    require(binding['config_sha256']==digest(canonical(config)),'RETAINED_CONFIG')
    ident=digest(canonical(binding));row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
    require(row is not None and row['binding']==canonical(binding).decode() and row['run']==budget.RUN
            and row['reserved_micro_usd']==binding['envelope']['reserved_micro_usd'],'RETAINED_RESERVATION')
    return binding,ident,row

def reserve(accounts,provider,config,record):
    from orchestrator import modal_source_composition as source,modal_source_budget as budget
    from orchestrator.modal_executor import canonical
    from orchestrator.manual_executor import digest
    source.contract(METADATA);require(not (STATE/'reservation-intent.json').exists(),'RESERVATION_EXISTS_RECONCILE')
    view=provider.billing_snapshot();now=datetime.now(timezone.utc)
    value={'purpose':budget.PURPOSE,'operation_id':source.OPERATION,'run_id':budget.RUN,
           'authority_sha256':budget.AUTHORITY,'team_authority_sha256':budget.TEAM_AUTHORITY,
           'source':config['base_source'],'helper_source':record['source'],'owner_sha256':config['owner_sha256'],
           'config_sha256':digest(canonical(config)),'inventory_sha256':source.INVENTORY,
           'native_asset_id':budget.NATIVE_ID,'direct_asset_id':budget.DIRECT_ID,'source_volume_id':budget.DIRECT_VOLUME,
           'envelope':budget.envelope(view['rates']),'created_at':now.isoformat(),
           'expires_at':(now+timedelta(days=source.RETENTION_DAYS)).isoformat()}
    intent('reservation-intent',value)
    require(budget.reserve(accounts,value,billing_snapshot=view,now=now),'NEW_RESERVATION_REQUIRED')
    intent('binding',value);intent('billing-before',view)
    return {'status':'RESERVED_NO_TRANSFER','reserved_micro_usd':value['envelope']['reserved_micro_usd']}

def stage(accounts,config):
    from orchestrator import modal_source_composition as source,private_records as pr
    binding,ident,row=retained(accounts,config);require(row['status']=='RESERVED','STAGE_NOT_RESERVED')
    require(datetime.now(timezone.utc)<datetime.fromisoformat(binding['expires_at']),'EXPIRED')
    files,_=source.contract(METADATA);_,brain,_,baseline=source.partitions(files)
    intent('stage-intent',{'binding_sha256':ident});root=STATE/'incoming';pr.mkdir(root)
    result=source.ingest_tar(sys.stdin.buffer,root,{**brain,**baseline});intent('STAGED',dict(result,binding_sha256=ident))
    return {'status':'STAGED','files':result['files'],'bytes':result['bytes']}


def direct_proof(provider,accounts):
    from orchestrator import modal_source_budget as budget,private_records as pr
    from orchestrator.manual_host_guard import trusted
    from orchestrator.manual_executor import digest
    from orchestrator.modal_executor import canonical
    from orchestrator.modal_download_provider import observe
    raw=trusted(DIRECT_CONFIG).read_bytes();require(digest(raw)==DIRECT_CONFIG_SHA,'DIRECT_CONFIG')
    config=json.loads(raw);binding=json.loads(pr.check(DIRECT_STATE/'binding.json').read_bytes())
    require(digest(canonical(binding))==budget.DIRECT_ID,'DIRECT_BINDING')
    require(datetime.now(timezone.utc)<datetime.fromisoformat(binding['asset_expires_utc']),'DIRECT_EXPIRED')
    handle=json.loads(pr.check(DIRECT_STATE/'provider/sandbox.json').read_bytes())
    require(handle['data_volume_id']==budget.DIRECT_VOLUME and handle['binding_sha256']==budget.DIRECT_ID,'DIRECT_VOLUME')
    result=observe(provider,binding,config['package'],handle)
    saved=json.loads(pr.check(DIRECT_STATE/'VERIFIED.json').read_bytes())
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(budget.DIRECT_ID,)).fetchone()
    require(result['status']=='VERIFIED' and all(saved[k]==v for k,v in result.items())
            and row is not None and row['status']=='READY' and json.loads(row['receipt'])==saved,'DIRECT_PROOF')
    return {'status':'VERIFIED','source_volume_id':budget.DIRECT_VOLUME,'binding_sha256':budget.DIRECT_ID}

def prepare(accounts,provider,config):
    from orchestrator import modal_source_composition as source,modal_source_budget as budget,private_records as pr
    from orchestrator.modal_assets import local_files,upload
    from orchestrator.modal_executor import canonical
    binding,ident,row=retained(accounts,config)
    require(row['status']=='RESERVED' and not (STATE/'prepare-intent.json').exists(),'EXISTING_ATTEMPT_NO_RETRY')
    require(datetime.now(timezone.utc)<datetime.fromisoformat(binding['expires_at']),'EXPIRED')
    require(not accounts.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'MODEL_RUNNING')
    budget.native_qualification(accounts,binding)
    files,membership=source.contract(METADATA);images,brain,cache,baseline=source.partitions(files)
    staged=json.loads(pr.check(STATE/'STAGED.json').read_bytes());require(staged['binding_sha256']==ident,'STAGE_BINDING')
    local_files(STATE/'incoming',{**brain,**baseline})
    import shutil
    require(shutil.disk_usage(STATE).free>source.DATA_BYTES+2*1024**3,'DISK_HEADROOM')
    intent('prepare-intent',{'binding_sha256':ident,'expires_at':binding['expires_at']})
    try:
        before=direct_proof(provider,accounts);intent('direct-before',before)
        root=STATE/'data';pr.mkdir(root)
        for name,item in {**brain,**baseline}.items():source.copy_local(STATE/'incoming'/name,root,name,item)
        for name,item in cache.items():source.copy_local(CACHE/Path(name).name,root,name,item)
        source.copy_images(provider,budget.DIRECT_VOLUME,root,images)
        local_files(root,files);after=direct_proof(provider,accounts);require(after==before,'DIRECT_CHANGED')
        intent('LOCAL_VERIFIED',{'binding_sha256':ident,**membership})
        require(datetime.now(timezone.utc)<datetime.fromisoformat(binding['expires_at']),'EXPIRED')
        name='research-item4-base-source-'+ident[:24]
        intent('volume-create-intent',{'binding_sha256':ident,'name':name,'version':2})
        try:provider.modal.Volume.from_name(name,create_if_missing=False,version=2,client=provider.client).hydrate(client=provider.client)
        except provider.modal.exception.NotFoundError:pass
        else:raise ValueError('SOURCE_SERVICE_VOLUME_EXISTS_RECONCILE')
        volume=provider.modal.Volume.from_name(name,create_if_missing=True,version=2,client=provider.client).hydrate(client=provider.client)
        import re
        require(re.fullmatch('vo-[A-Za-z0-9]+',volume.object_id),'VOLUME_ID')
        require(volume.object_id!=budget.DIRECT_VOLUME and not volume.listdir('/',recursive=True),'DESTINATION_EMPTY')
        handle={'binding_sha256':ident,'name':name,'volume_id':volume.object_id,'version':2};intent('volume',handle)
        intent('upload-intent',{'binding_sha256':ident,'volume_id':volume.object_id,'inventory_sha256':source.INVENTORY})
        # Existing uploader hashes the complete local tree before/after and reads
        # every remote byte back. Membership is rechecked after that hash pass.
        upload(provider,volume.object_id,root,files)
        checked=provider._verify_volume_members(volume.object_id,files)
        require(checked.object_id==volume.object_id,'REMOTE_ID_CHANGED')
        local_files(root,files)
        result={'status':'VERIFIED','binding_sha256':ident,'source_volume_id':budget.DIRECT_VOLUME,
                'volume_id':volume.object_id,'inventory_sha256':source.INVENTORY,'membership':membership,
                'reserved_micro_usd':binding['envelope']['reserved_micro_usd'],'expires_at':binding['expires_at'],
                'scientific_approval':False,'patient_analysis':False,'new_provider_compute':False,
                'originals_preserved':True,'completed_at':datetime.now(timezone.utc).isoformat()}
        intent('VERIFIED',result);accounts.finish_assets(ident,'READY',result);return result
    except BaseException as error:
        failure={'status':'UNCERTAIN','binding_sha256':ident,'error_type':type(error).__name__,
                 'no_automatic_retry':True,'reservation_retained':True}
        intent('FAILED',failure);accounts.finish_assets(ident,'UNCERTAIN',failure)
        raise ValueError('SOURCE_SERVICE_PREPARATION_FAILED_RECONCILE') from error

def clear_local(root,expected):
    from orchestrator import private_records as pr
    if not root.exists():return
    pr.check_tree(root);require(root in {STATE/'data',STATE/'incoming'},'CLEANUP_LOCAL_SCOPE')
    dirs={p.as_posix() for name in expected for p in Path(name).parents if p.as_posix()!='.'}
    paths=list(root.rglob('*'))
    for p in paths:
        mode=p.lstat().st_mode;name=p.relative_to(root).as_posix()
        require(not stat.S_ISLNK(mode) and ((stat.S_ISDIR(mode) and name in dirs) or
            (stat.S_ISREG(mode) and name in expected and p.stat().st_nlink==1 and p.stat().st_size<=expected[name]['bytes'])),'CLEANUP_UNKNOWN_LOCAL')
    for p in sorted(paths,key=lambda x:len(x.parts),reverse=True):
        if p.is_dir():p.rmdir()
        else:p.unlink()
    root.rmdir()

def cleanup(accounts,provider,config):
    from orchestrator import modal_source_composition as source,modal_source_budget as budget,private_records as pr
    from orchestrator.modal_cleanup import remove_members
    if not (STATE/'binding.json').exists():return {'status':'NOT_STARTED'}
    binding,ident,row=retained(accounts,config)
    if datetime.now(timezone.utc)<datetime.fromisoformat(binding['expires_at']):return {'status':'NOT_DUE'}
    require(not accounts.db.execute("SELECT 1 FROM autonomy_compute WHERE run=? AND status NOT IN ('COLLECTED','ACCOUNTED')",(budget.RUN,)).fetchone(),'RETENTION_ACTIVE_OR_UNCERTAIN_EXECUTION')
    files,_=source.contract(METADATA);_,brain,_,baseline=source.partitions(files)
    folder=STATE/'cleanup';pr.mkdir(folder,exist_ok=True)
    if (folder/'COMPLETE.json').exists():return json.loads(pr.check(folder/'COMPLETE.json').read_bytes())
    if (STATE/'volume.json').exists():
        handle=json.loads(pr.check(STATE/'volume.json').read_bytes())
        expected={'binding_sha256':ident,'name':'research-item4-base-source-'+ident[:24],'version':2}
        require({k:handle[k] for k in expected}==expected
                and json.loads(pr.check(STATE/'volume-create-intent.json').read_bytes())==expected
                and handle['volume_id']!=budget.DIRECT_VOLUME,'RETENTION_HANDLE')
        record=folder/'members.json'
        if record.exists():members=json.loads(pr.check(record).read_bytes())
        else:
            entries=provider._volume(handle['volume_id']).listdir('/',recursive=True)
            names=[x.path.lstrip('/') for x in entries if x.type.name=='FILE']
            require(len(names)==len(set(names)) and set(names)<=set(files)
                    and all(x.type.name in {'FILE','DIRECTORY'} for x in entries),'RETENTION_UNKNOWN_REMOTE')
            members={n:files[n] for n in names};provider._verify_volume(handle['volume_id'],members)
            from orchestrator.manual_driver import write_once
            from orchestrator.modal_executor import canonical
            write_once(record,canonical(members))
        require(all(files.get(n)==v for n,v in members.items()),'RETENTION_INVENTORY')
        remove_members(provider,handle['volume_id'],members,folder,'frozen-source')
    else:require(not (STATE/'volume-create-intent.json').exists(),'UNKNOWN_CREATE_RECONCILE')
    clear_local(STATE/'data',files);clear_local(STATE/'incoming',{**brain,**baseline})
    result={'status':'CLEARED','binding_sha256':ident,'originals_preserved':True,'reservation_retained':True}
    from orchestrator.manual_driver import write_once
    from orchestrator.modal_executor import canonical
    write_once(folder/'COMPLETE.json',canonical(result));return result

def main():
    require(sys.argv[1:] in (['reserve'],['stage'],['prepare'],['cleanup']),'FIXED_ARGUMENTS')
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,'SERVICE_IDENTITY')
    os.umask(0o077);h,native,config,record=verify();operation=sys.argv[1]
    if operation in {'prepare','cleanup'}:
        unit=UNIT if operation=='prepare' else CLEANUP
        observed=subprocess.check_output(['systemctl','show',unit,'--property='+','.join(PROPS)],text=True)
        require(dict(x.split('=',1) for x in observed.splitlines() if '=' in x)==PROPS,'SERVICE_RESTRICTIONS')
    from orchestrator import spending_continuation,modal_environment_budget as shared,private_records as pr
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator.modal_budget import ComputeAccounts
    from orchestrator.modal_provider import ModalProvider
    from orchestrator.remote_supervisor import lock
    image=h.image_helper();original=spending_continuation.closed_ids
    spending_continuation.closed_ids=lambda batch,run:image.qualified_closed(original,batch,run)
    shared.terminal_failed_compute=image.stopped_item6
    batch=BatchAccounts(config['batch_ledger'])
    try:
        accounts=ComputeAccounts(batch)
        with lock(STATE/'operation.lock'):
            provider=None
            if operation!='stage':
                due=operation!='cleanup' or (STATE/'binding.json').exists() and datetime.now(timezone.utc)>=datetime.fromisoformat(json.loads(pr.check(STATE/'binding.json').read_bytes())['expires_at'])
                if due:provider=ModalProvider(config['provider'])
            if operation=='reserve':result=reserve(accounts,provider,config,record)
            elif operation=='stage':result=stage(accounts,config)
            elif operation=='prepare':result=prepare(accounts,provider,config)
            else:result=cleanup(accounts,provider,config)
            pr.atomic(STATE/(operation+'-status.json'),result)
            print(json.dumps({k:v for k,v in result.items() if k in {'status','files','bytes','reserved_micro_usd'}}))
    finally:batch.db.close()

if __name__=='__main__':main()
