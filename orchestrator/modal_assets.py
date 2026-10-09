"""One private M3 asset preparation, then one hash-bound package upload.

This module performs no scientific/model execution. Every mutating provider
operation follows a durable intent and cost reservation; an incomplete attempt
is reconciled, not repeated by rerunning this command.
"""
from decimal import Decimal,ROUND_CEILING
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
import re
import subprocess

from orchestrator import private_records,connectivity
from orchestrator.manual_driver import git,write_once
from orchestrator.manual_executor import read,digest,inventory,atomic
from orchestrator.modal_executor import canonical,verify_package
from orchestrator.modal_provider import ModalProvider,member_map
from orchestrator.modal_budget import ComputeAccounts,RATES,MICRO,estimate,SMOKE_CAP
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.remote_supervisor import lock
from experiments.sprint9_modal.worker import validate_config,CONTRACT

BASE_IMAGE='pytorch/pytorch@sha256:eee11b3b3872a8c838e35ef48f08b2d5def2080902c7f666831310ca1a0ef2be'


def require_supervisor(settings,state,record,source):
    """Installed, hash-bound housekeeping timer must exist before storing assets."""
    from orchestrator.manual_host_guard import trusted
    from tools import manual_promotion
    selected_path=trusted(Path(manual_promotion.POINTER));selected=read(selected_path)
    if selected['source']!=source or Path(selected['state'])!=Path(state).parent or Path(record)!=Path(selected['state'])/'modal-preparation':
        raise ValueError('MODAL_PREPARATION_DEPLOYMENT_BINDING')
    receipt=manual_promotion.manifest_check(Path('/'),str(Path(selected['hash_list']).parent))
    runtime=read(trusted(Path(selected['runtime'])))
    if digest(Path(selected['runtime']).read_bytes())!=selected['runtime_sha256'] or runtime.get('lane_backend')!='modal':raise ValueError('MODAL_PREPARATION_RUNTIME')
    if runtime.get('modal_sdk')!={'package':settings['sdk_package'],'sha256':settings['sdk_sha256']}:raise ValueError('MODAL_PREPARATION_SDK_BINDING')
    if receipt['source']!=source or receipt['layout']['units']!=selected['units']:raise ValueError('MODAL_PREPARATION_UNIT_BINDING')
    timer=next(u for u in selected['units'] if u.endswith('.timer'))
    observed=subprocess.check_output(['/usr/bin/systemctl','show',timer,'--property=LoadState,UnitFileState,ActiveState'],text=True)
    values=dict(line.split('=',1) for line in observed.splitlines() if '=' in line)
    if values!={'LoadState':'loaded','UnitFileState':'enabled','ActiveState':'active'}:raise ValueError('MODAL_RETENTION_TIMER_NOT_READY')
    return {'source':source,'timer':timer,'observed':values,'runtime_sha256':selected['runtime_sha256']}


def workspace_spend(provider):
    provider.client.hello();ws=provider.modal.Workspace.from_context(client=provider.client);ws.hydrate(client=provider.client)
    if ws.name!=provider.config['workspace']:raise ValueError('MODAL_AUTHENTICATED_WORKSPACE')
    rates=dict(ws.billing.rates())
    required={'gpu_hour_cost_a100_80gb':'2.5','cpu_hour_cost_sandbox':RATES['cpu_core_hour'],'mem_gib_hour_cost_sandbox':RATES['memory_gib_hour'],
              'volume_storage_gib_month_cost':'.09','egress_gib_cost':'.04'}
    if any(Decimal(str(rates.get(k,'-1')))!=Decimal(v) for k,v in required.items()):raise ValueError('MODAL_PREPARATION_RATE_CHANGED')
    summary=ws.billing.summary(cycle=datetime.now(timezone.utc).strftime('%Y-%m'))
    spent=max(Decimal(str(summary.metered_cost)),Decimal(str(summary.billed_cost)))
    if not spent.is_finite() or spent<0:raise ValueError('MODAL_BILLING_VALUE')
    return int((spent*1000000).to_integral_value(rounding=ROUND_CEILING))


def asset_estimate(data,wheels):
    # Package/output maximums are enforced by member_map at their consumers.
    # Reserve a full month even though successful collection clears copies.
    member_map(data,maximum=2*1024**3);member_map(wheels)
    stored=sum(x['bytes'] for x in data.values())+sum(x['bytes'] for x in wheels.values())+256*1024**2
    storage=int((Decimal(stored)/1024**3*Decimal('.09')*Decimal(31)/28*1000000).to_integral_value(rounding=ROUND_CEILING))
    transfer=int((Decimal(256*1024**2)/1024**3*Decimal('.04')*1000000).to_integral_value(rounding=ROUND_CEILING))
    if storage+transfer>500000:raise ValueError('MODAL_ASSET_OVERHEAD_BOUND')
    return {'maximum_stored_bytes':stored,'retention_days':30,'reserved_storage_days':31,'billing_month_days_floor':28,'storage_micro_usd':storage,
            'output_transfer_micro_usd':transfer,'preparation_reservation_micro_usd':MICRO,
            'registry_and_other_headroom_micro_usd':MICRO-storage-transfer,
            'assumptions':'FROM-only registry import; no custom build compute; Volume IO excluded from egress; full reservation retained'}


def local_files(folder,expected):
    folder=Path(folder);private_records.check_tree(folder)
    actual=inventory(folder)
    if actual!={name:item['sha256'] for name,item in expected.items()}:raise ValueError('MODAL_LOCAL_ASSET_MEMBERS_OR_HASH')
    if any((folder/name).stat().st_size!=item['bytes'] for name,item in expected.items()):raise ValueError('MODAL_LOCAL_ASSET_SIZE')
    return actual


def upload(provider,volume_id,folder,expected):
    local_files(folder,expected)
    volume=provider._volume(volume_id)
    if volume.listdir('/',recursive=True):raise ValueError('MODAL_DESTINATION_NOT_EMPTY')
    with volume.batch_upload(force=False) as batch:
        for name in sorted(expected):batch.put_file(Path(folder)/name,'/'+name,mode=0o440)
    local_files(folder,expected)
    provider._verify_volume(volume_id,expected)


@private_records.private_umask
def prepare(root,state,engine_review,settings,record,*,provider_factory=ModalProvider):
    root,state,engine_review,record=map(Path,(root,state,engine_review,record));source=git(root,'rev-parse','HEAD')
    if git(root,'status','--porcelain'):raise ValueError('CLEAN_REVIEWED_SOURCE_REQUIRED')
    report=engine_review.read_text()
    if source not in report or re.findall(r'^## Verdict: (.+?)\s*$',report,re.M)!=['APPROVE']:raise ValueError('EXACT_ENGINE_REVIEW_REQUIRED')
    if record.exists():raise ValueError('EXISTING_MODAL_PREPARATION_RECONCILE')
    if state.exists():raise ValueError('EXISTING_MODAL_LANE_RECONCILE')
    supervisor=require_supervisor(settings,state,record,source)
    smoke=read(settings['smoke_path']);validate_config(smoke,CONTRACT)
    if estimate(settings['resources'],settings['overhead_micro_usd'])['reserved_micro_usd']+MICRO>SMOKE_CAP:raise ValueError('M3_PREPARATION_AND_RUN_COST_CAP')
    data=Path(settings['data_root']);wheels=Path(settings['wheel_root'])
    expected_data={case+'.npz':{'sha256':sha,'bytes':(data/(case+'.npz')).stat().st_size} for case,sha in smoke['cache_file_hashes'].items()}
    expected_wheels={name:{'sha256':item['sha256'],'bytes':item['bytes']} for name,item in read(root/'experiments/sprint9_modal/wheels.json')['files'].items()}
    member_map(expected_data,maximum=2*1024**3);member_map(expected_wheels)
    envelope=asset_estimate(expected_data,expected_wheels)
    local_files(data,expected_data);local_files(wheels,expected_wheels)
    base={k:settings[k] for k in ['sdk_package','sdk_sha256','credential_file','workspace','batch_ledger']}
    if base['workspace']!='moroseui':raise ValueError('MODAL_APPROVED_WORKSPACE')
    connectivity.require(['modal'],record.parent/'connectivity.json')
    provider=provider_factory(base);spent=workspace_spend(provider)
    run='sprint9-modal-'+digest((source+digest(engine_review.read_bytes())).encode())[:16]
    owner={'state':str(state.resolve()),'source':source,'review_sha256':digest(engine_review.read_bytes())}
    batch=BatchAccounts(base['batch_ledger']);batch.register_run(run,owner);accounts=ComputeAccounts(batch)
    binding={'run_id':run,'source':source,'owner':owner,'base_image':BASE_IMAGE,'data_files':expected_data,'wheel_files':expected_wheels,
             'asset_cost_envelope':envelope,'supervisor':supervisor,'settings_sha256':digest(canonical(settings)),'smoke_sha256':digest(canonical(smoke)),'scope':'M3_PRIVATE_ASSETS_ONLY'}
    ident=digest(canonical(binding))
    private_records.mkdir(record.parent,parents=True,exist_ok=True)
    lock_path=record.parent/'modal-preparation.lock'
    if lock_path.exists():private_records.check(lock_path)
    with lock(lock_path):
        private_records.check(lock_path)
        private_records.mkdir(record,parents=True)
        write_once(record/'binding.json',canonical(binding))
        if not accounts.reserve_assets(ident,run,binding,workspace_spent_micro=spent):raise ValueError('EXISTING_ASSET_RESERVATION_NO_RETRY')
        write_once(record/'intent.json',canonical({'id':ident,'run_id':run,'workspace_spent_micro_before':spent,'reserved_micro_usd':MICRO}))
        try:
            name='research-'+run
            # This is a new application, not an existing deployed research route.
            try:provider.modal.App.lookup(name,create_if_missing=False,client=provider.client)
            except provider.modal.exception.NotFoundError:pass
            else:raise ValueError('MODAL_APP_ALREADY_EXISTS_RECONCILE')
            app=provider.modal.App.lookup(name,create_if_missing=True,client=provider.client)
            write_once(record/'app.json',canonical({'app_id':app.app_id,'name':name}))
            # Registry import only: no custom RUN layer, GPU build, package
            # install or project code in the image builder. Dependencies install
            # offline inside the later hard-lifetime, hard-resource Sandbox.
            image=provider.build_registry_image(app,BASE_IMAGE)
            write_once(record/'image.json',canonical({'image_id':image.object_id,'registry':BASE_IMAGE,'builder':'2025.06','commands':['FROM '+BASE_IMAGE]}))
            volumes={}
            for kind in ['data','wheels','package']:
                vname=name+'-'+kind
                try:provider.modal.Volume.from_name(vname,create_if_missing=False).hydrate(client=provider.client)
                except provider.modal.exception.NotFoundError:pass
                else:raise ValueError('MODAL_VOLUME_ALREADY_EXISTS_RECONCILE')
                volume=provider.modal.Volume.from_name(vname,create_if_missing=True).hydrate(client=provider.client)
                volumes[kind]=volume.object_id
                write_once(record/(kind+'-volume.json'),canonical({'name':vname,'id':volume.object_id}))
            upload(provider,volumes['data'],data,expected_data);upload(provider,volumes['wheels'],wheels,expected_wheels)
            after=workspace_spend(provider)
            if after-spent>MICRO:raise ValueError('MODAL_PREPARATION_COST_EXCEEDED')
            runtime={**base,'image_id':image.object_id,'app_name':name,'data_volume_id':volumes['data'],'wheel_volume_id':volumes['wheels'],
                     'package_volume_id':volumes['package'],'input_contract':CONTRACT,'data_files':expected_data,'wheel_files':expected_wheels,
                     'local_assets':{'data':str(data.resolve()),'wheels':str(wheels.resolve()),'package':str((state/'prepared-package').resolve())},
                     'asset_created_utc':datetime.now(timezone.utc).isoformat(),'asset_expires_utc':(datetime.now(timezone.utc)+timedelta(days=30)).isoformat(),
                     'asset_cost_envelope':asset_estimate(expected_data,expected_wheels)}
            ready={'status':'READY','source':source,'run_id':run,'reservation_id':ident,'runtime_sha256':digest(canonical(runtime)),
                   'workspace_spent_micro_before':spent,'workspace_spent_micro_after':after,'cost_accounting':'full preparation reservation retained; provider billing can be delayed',
                   'registry':BASE_IMAGE,'data_count':99,'wheel_count':len(expected_wheels)}
            write_once(record/'runtime.json',canonical(runtime));write_once(record/'READY.json',canonical(ready))
            plan={'runtime':runtime,'smoke_path':settings['smoke_path'],'preparation_receipt':str(record/'READY.json'),
                  'preparation_sha256':digest((record/'READY.json').read_bytes()),'resources':settings['resources'],'overhead_micro_usd':settings['overhead_micro_usd']}
            write_once(record/'lane-plan.json',canonical(plan))
            # Publish the accounting outcome last. A partial local record can
            # never qualify a lane, and failure cannot relabel READY as uncertain.
            accounts.finish_assets(ident,'READY',ready)
            return plan
        except BaseException as error:
            outcome={'status':'UNCERTAIN','run_id':run,'error_type':type(error).__name__,'no_retry':True}
            write_once(record/'UNCERTAIN.json',canonical(outcome));accounts.finish_assets(ident,'UNCERTAIN',outcome)
            raise ValueError('MODAL_ASSET_PREPARATION_UNCERTAIN_RECONCILE') from None


@private_records.private_umask
def prepare_package(provider,binding,package,record):
    package,record=Path(package),Path(record);manifest=verify_package(package,binding)
    expected={k:{'sha256':v,'bytes':(package/k).stat().st_size} for k,v in inventory(package).items()}
    static = binding.get('purpose')=='M4_ITEM4' and binding.get('execution',{}).get('schema')=='reviewed-module/v1'
    if static:
        # The admitted manifest is delivered by the exact launch transport.
        # A resume reuses the same reviewed bytes, never overwrites a Volume.
        expected.pop('manifest.json')
    member_map(expected)
    if record.exists():
        ready=record/'READY.json'
        if not ready.exists():raise ValueError('MODAL_PACKAGE_UPLOAD_UNCERTAIN_RECONCILE')
        saved=read(ready)
        if saved.get('manifest_sha256')!=digest(canonical(manifest)) or saved.get('volume_id')!=binding['package_volume_id']:raise ValueError('MODAL_PACKAGE_UPLOAD_BINDING')
        provider._verify_volume(binding['package_volume_id'],expected);return saved
    connectivity.require(['modal'],record.parent/'connectivity.json')
    private_records.mkdir(record,parents=True)
    write_once(record/'intent.json',canonical({'manifest_sha256':digest(canonical(manifest)),'volume_id':binding['package_volume_id']}))
    if static:
        volume=provider._volume(binding['package_volume_id'])
        if volume.listdir('/',recursive=True):
            provider._verify_volume(binding['package_volume_id'],expected)
        else:
            # Local package includes its preserved admitted manifest; only its
            # immutable reviewed payload belongs in the read-only Volume.
            before=inventory(package)
            with volume.batch_upload(force=False) as batch:
                for name in sorted(expected):batch.put_file(package/name,'/'+name,mode=0o440)
            if inventory(package)!=before:raise ValueError('MODAL_LOCAL_ASSET_MEMBERS_OR_HASH')
            provider._verify_volume(binding['package_volume_id'],expected)
    else:
        upload(provider,binding['package_volume_id'],package,expected)
    ready={'status':'READY','manifest_sha256':digest(canonical(manifest)),'volume_id':binding['package_volume_id']}
    write_once(record/'READY.json',canonical(ready));return ready


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--state',required=True)
    parser.add_argument('--engine-review',required=True);parser.add_argument('--settings',required=True);parser.add_argument('--record',required=True)
    args=parser.parse_args();prepare(args.root,args.state,args.engine_review,read(args.settings),args.record)
    print(json.dumps({'status':'READY','plan':str(Path(args.record)/'lane-plan.json')}))

if __name__=='__main__':main()
