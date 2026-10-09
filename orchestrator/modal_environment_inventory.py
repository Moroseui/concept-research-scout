"""One accounted no-patient image inventory; no model or scientific allowance.

A durable intent makes ambiguous provider creation non-retriable. Re-running
this service observes the same attempt, including after a controller restart.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import subprocess
import sys
import time
from orchestrator import private_records, connectivity
from orchestrator import modal_environment_budget as budget
from orchestrator import modal_environment_provider as native
from orchestrator import modal_pinned_image as image
from orchestrator import modal_diagnostics_image as cpu
from orchestrator import modal_native_synthetic as synthetic
from orchestrator.manual_executor import digest, read
from orchestrator.manual_driver import write_once
from orchestrator.modal_executor import canonical
from orchestrator.remote_supervisor import lock

SCHEMA='item4-environment-inventory/v1'
CONFIG_FIELDS={'schema','source','release','installation_record','installation_sha256',
               'batch_ledger','state','provider','operation_id','image_id','base_image','worker_sha256','units'}


def selection_profile(config):
    if config.get("schema")==synthetic.SCHEMA:
        synthetic.selected(config.get("native_synthetic"))
        return synthetic.PURPOSE,synthetic.OPERATION,synthetic.RUN,synthetic.envelope,synthetic.worker_sha256()
    if config.get('schema')==cpu.SCHEMA:
        cpu.validate_selection(config.get('image_build'),config.get('reviewed_requirements'))
        return cpu.PURPOSE,cpu.OPERATION,cpu.RUN,image.envelope,image.worker_sha256()
    if config.get('schema')==image.SCHEMA:
        image.validate(config.get('image_build'))
        return image.PURPOSE,image.OPERATION,image.RUN,image.envelope,image.worker_sha256()
    from orchestrator import modal_environment_closure_route as closure
    if config.get('schema')==closure.SCHEMA:
        closure.validate(config.get('closure'))
        return closure.PURPOSE,closure.OPERATION,closure.RUN,lambda rates:closure.envelope(rates,config['closure']['selection']['wheels']),closure.worker_sha256()
    return budget.PURPOSE,budget.OPERATION,budget.RUN,budget.envelope,native.WORKER_SHA256


def unit_name(config):
    prefix='native-synthetic' if selection_profile(config)[0]==synthetic.PURPOSE else 'cpu-image' if selection_profile(config)[0]==cpu.PURPOSE else 'image' if selection_profile(config)[0]==image.PURPOSE else 'closure' if selection_profile(config)[0]!=budget.PURPOSE else 'environment'
    return 'research-manual-sprint10-'+prefix+'-'+config['source'][:12]+'.service'


def result_scope(config):
    if selection_profile(config)[0]==synthetic.PURPOSE:return synthetic.worker.DURABILITY_SCOPE
    if image.is_build(selection_profile(config)[0]):return 'Pinned image and CPU native checks only; no patient computation or GPU validation'
    if selection_profile(config)[0]!=budget.PURPOSE:
        return 'Offline dependency closure only; no patient computation, scientific acceptance or GPU validation'
    return 'Environment inventory only; not scientific acceptance or dependency closure'


def selection(config):
    from orchestrator.modal_assets import BASE_IMAGE
    purpose,op,run,make_envelope,worker=selection_profile(config)
    fields=CONFIG_FIELDS|({'owner_sha256'} if purpose in {image.PURPOSE,synthetic.PURPOSE} else set())|({'reviewed_requirements'} if purpose==cpu.PURPOSE else set())|({'native_synthetic'} if purpose==synthetic.PURPOSE else {'image_build'} if image.is_build(purpose) else {'closure'} if purpose!=budget.PURPOSE else set())
    from orchestrator.modal_environment_closure_route import SCHEMA as CLOSURE_SCHEMA
    if purpose in {image.PURPOSE,synthetic.PURPOSE} and not re.fullmatch('[0-9a-f]{64}',str(config.get('owner_sha256'))):raise ValueError('ITEM4_IMAGE_OWNER_BINDING')
    if (set(config)!=fields or config['schema'] not in {SCHEMA,CLOSURE_SCHEMA,image.SCHEMA,cpu.SCHEMA,synthetic.SCHEMA} or
            config['operation_id']!=op or
            config['worker_sha256']!=worker or config['base_image']!=BASE_IMAGE or
            not isinstance(config['image_id'],str) or not re.fullmatch(r'im-[A-Za-z0-9]+',config['image_id']) or
            not isinstance(config['source'],str) or not re.fullmatch('[0-9a-f]{40}',config['source'])):
        raise ValueError('ENVIRONMENT_INVENTORY_SELECTION')
    return config


def host_check(path):
    """Real installed source, receipt, fixed worker and service restrictions."""
    from orchestrator.manual_host_guard import trusted
    from tools.manual_promotion import manifest_check
    config_path=trusted(Path(path));config_raw=config_path.read_bytes()
    config=selection(json.loads(config_raw))
    installed=trusted(Path(config['installation_record'])/'installed.json')
    if digest(installed.read_bytes())!=config['installation_sha256']:
        raise ValueError('ENVIRONMENT_INVENTORY_INSTALL_CHANGED')
    receipt=manifest_check(Path('/'),config['installation_record'])
    if (receipt['source']!=config['source'] or receipt['layout']['release']!=config['release'] or
            Path(__file__).resolve()!=Path(config['release'])/'orchestrator/modal_environment_inventory.py'):
        raise ValueError('ENVIRONMENT_INVENTORY_RELEASE_BINDING')
    if os.getuid()!=1003 or not sys.flags.no_user_site:
        raise ValueError('ENVIRONMENT_INVENTORY_SERVICE_USER')
    expected=unit_name(config)
    names={expected}
    if selection_profile(config)[0] not in {budget.PURPOSE,image.PURPOSE,cpu.PURPOSE,synthetic.PURPOSE}:names.add(expected.replace('.service','.timer'))
    if set(config['units'])!=names:raise ValueError('ENVIRONMENT_INVENTORY_UNIT_SET')
    for name in names:
        path=trusted(Path('/etc/systemd/system')/name);pin=config['units'][name]
        if set(pin)!={'sha256'} or digest(path.read_bytes())!=pin['sha256']:
            raise ValueError('ENVIRONMENT_INVENTORY_UNIT_CHANGED')
    if len(names)==2:
        timer=expected.replace('.service','.timer')
        actual=subprocess.check_output(['/usr/bin/systemctl','show',timer,'--property=LoadState,UnitFileState,ActiveState'],text=True)
        if dict(x.split('=',1) for x in actual.splitlines() if '=' in x)!={'LoadState':'loaded','UnitFileState':'enabled','ActiveState':'active'}:
            raise ValueError('CLOSURE_RETENTION_TIMER_NOT_READY')
    unit=trusted(Path('/etc/systemd/system')/expected);pin=config['units'][expected]
    if set(pin)!={'sha256'} or digest(unit.read_bytes())!=pin['sha256']:
        raise ValueError('ENVIRONMENT_INVENTORY_UNIT_CHANGED')
    props={'User':'partho','Group':'partho','UMask':'0077','NoNewPrivileges':'yes',
           'ProtectSystem':'strict','PrivateTmp':'yes','ProtectHome':'read-only',
           'RestrictSUIDSGID':'yes','LockPersonality':'yes'}
    observed=subprocess.check_output(['/usr/bin/systemctl','show',expected,'--property='+','.join(props)],text=True)
    if dict(line.split('=',1) for line in observed.splitlines() if '=' in line)!=props:
        raise ValueError('ENVIRONMENT_INVENTORY_SERVICE_RESTRICTIONS')
    return config,{'status':'PASS','source':config['source'],
        'config_sha256':digest(config_raw),'installation_sha256':config['installation_sha256']}


@private_records.private_umask
def tick(config,provider,accounts,*,host_proof,now=None):
    clock=(lambda:now) if now is not None else lambda:datetime.now(timezone.utc)
    selection(config);state=private_records.check(config['state'])
    purpose,op,run,make_envelope,worker=selection_profile(config)
    if (host_proof.get('status')!='PASS' or host_proof.get('source')!=config['source'] or
            host_proof.get('installation_sha256')!=config['installation_sha256'] or
            not re.fullmatch('[0-9a-f]{64}',host_proof.get('config_sha256',''))):
        raise ValueError('ENVIRONMENT_INVENTORY_HOST_PROOF')
    with lock(state/'tick.lock'):
        private_records.check(state/'tick.lock')
        bind_path=state/'binding.json'
        if not bind_path.exists():
            if (accounts.batch.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
            view=read(state/'initial-billing.json') if (state/'initial-billing.json').exists() else provider.billing_snapshot()
            binding={'purpose':purpose,'operation_id':op,
                'authority_sha256':cpu.policy.authority() if purpose==cpu.PURPOSE else budget.AUTHORITY,'team_authority_sha256':budget.TEAM_AUTHORITY,
                'run_id':run,'source':config['source'],
                'installed_config_sha256':host_proof['config_sha256'],
                'image_id':config['image_id'],'base_image':config['base_image'],
                'worker_sha256':worker,'envelope':make_envelope(view['rates'])}
            if purpose==synthetic.PURPOSE:binding['native_synthetic']=config['native_synthetic']
            if image.is_build(purpose):binding['image_build']=config['image_build']
            if purpose==cpu.PURPOSE:
                cpu.reviewed(config['reviewed_requirements']);binding['reviewed_requirements']=config['reviewed_requirements']
            elif purpose in {image.PURPOSE,synthetic.PURPOSE}:binding['owner_sha256']=config['owner_sha256'];image.item4_owner(accounts,binding)
            elif purpose!=budget.PURPOSE:
                binding['closure']=config['closure']
                from orchestrator.modal_environment_closure_route import local_wheels
                local_wheels(binding['closure'])
            budget.validate_binding(binding)
            write_once(state/'initial-billing.json',canonical(view));write_once(bind_path,canonical(binding))
        binding=read(private_records.check(bind_path));budget.validate_binding(binding)
        if (any(binding[k]!=config[k] for k in ('operation_id','source','image_id','base_image','worker_sha256')) or
                binding['installed_config_sha256']!=host_proof['config_sha256'] or
                binding.get('native_synthetic')!=config.get('native_synthetic') or binding.get('closure')!=config.get('closure') or binding.get('image_build')!=config.get('image_build') or binding.get('reviewed_requirements')!=config.get('reviewed_requirements') or binding.get('owner_sha256')!=config.get('owner_sha256')):
            raise ValueError('ENVIRONMENT_INVENTORY_EXISTING_BINDING_CHANGED')
        ident=digest(canonical(binding))
        row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
        if row is None:
            if purpose==cpu.PURPOSE:cpu.owner(accounts,binding)
            elif purpose in {image.PURPOSE,synthetic.PURPOSE}:image.item4_owner(accounts,binding)
            else:accounts.batch.register_run(run,budget.owner(binding))
            view=provider.billing_snapshot()
            if not budget.reserve(accounts,ident,run,binding,billing_snapshot=view,now=clock()):
                raise ValueError('ENVIRONMENT_INVENTORY_RESERVATION_RACE')
            row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
        if row['binding']!=canonical(binding).decode() or row['run']!=run or not budget.selected_operation(row):
            raise ValueError('ENVIRONMENT_INVENTORY_LEDGER_BINDING')
        from orchestrator.review_contract import strict_json
        owner=accounts.db.execute('SELECT * FROM autonomy_runs WHERE id=?',(run,)).fetchone()
        statuses={'ACTIVE','COMPLETE'} if row['status']=='READY' else {'ACTIVE'}
        if purpose==cpu.PURPOSE:cpu.owner(accounts,binding)
        elif purpose in {image.PURPOSE,synthetic.PURPOSE}:image.item4_owner(accounts,binding)
        elif owner is None or strict_json(owner['binding'])!=budget.owner(binding) or owner['status'] not in statuses:
            raise ValueError('ENVIRONMENT_INVENTORY_OWNER_CHANGED')
        if row['status']=='UNCERTAIN':return {'status':'BLOCKED_PRESERVED_FAILURE','no_automatic_retry':True,
            'storage_may_continue_accruing':(state/'provider/wheel-volume-intent.json').exists()}
        if row['status']=='READY':
            result=read(private_records.check(state/'VERIFIED.json'))
            handle=read(private_records.check(state/'provider/sandbox.json'))
            original=native.observe(None,binding,handle,state/'provider')
            expected={**original,'binding_sha256':ident,'source':config['source'],'scientific_calls':0,
                      'scope':result_scope(config)}
            if result!=expected or original['status']!='VERIFIED':
                raise ValueError('ENVIRONMENT_INVENTORY_RESULT_BINDING')
            accounts.finish_assets(ident,'READY',result)
            if purpose!=synthetic.PURPOSE and not image.is_build(purpose):accounts.batch.complete_run(run,result)
            if purpose not in {budget.PURPOSE,image.PURPOSE,cpu.PURPOSE,synthetic.PURPOSE}:
                from orchestrator.modal_environment_closure_route import expire
                retention=expire(provider,accounts,binding,handle,state,clock())
                if retention['status']!='NOT_DUE':return {**result,'retention':retention}
            return result
        if row['status']!='RESERVED':raise ValueError('ENVIRONMENT_INVENTORY_ASSET_STATUS')
        if (accounts.batch.folder/'HALT').exists():return {'status':'HALTED','preserved_reservation':True}
        operation=state/'provider'
        if not operation.exists():handle=native.launch(provider,accounts,binding,operation)
        elif (operation/'sandbox.json').is_file():handle=read(private_records.check(operation/'sandbox.json'))
        else:return {'status':'BLOCKED_CREATE_UNCERTAIN','no_automatic_retry':True,
                     'storage_may_continue_accruing':(operation/'wheel-volume-intent.json').exists()}
        result=native.observe(provider,binding,handle,operation)
        if result['status']=='VERIFIED':
            result={**result,'binding_sha256':ident,'source':config['source'],'scientific_calls':0,
                    'scope':result_scope(config)}
            write_once(state/'VERIFIED.json',canonical(result));accounts.finish_assets(ident,'READY',result)
            if purpose!=synthetic.PURPOSE and not image.is_build(purpose):accounts.batch.complete_run(run,result)
        elif result['status'] in {'FAILED','UNCERTAIN'}:
            write_once(state/'FAILED.json',canonical(result));accounts.finish_assets(ident,'UNCERTAIN',result)
        return result


def main():
    import argparse
    from orchestrator.modal_provider import ModalProvider
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator.modal_budget import ComputeAccounts
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True)
    args=parser.parse_args();config,proof=host_check(args.config)
    batch=BatchAccounts(config['batch_ledger']);provider=None
    deadline=time.monotonic()+(4200 if image.is_build(selection_profile(config)[0]) else 1920 if selection_profile(config)[0]!=budget.PURPOSE else 900)
    try:
        accounts=ComputeAccounts(batch)
        saved=Path(config['state'])/'binding.json'
        existing=read(saved) if saved.is_file() else None
        row=accounts.db.execute('SELECT status FROM autonomy_assets WHERE id=?',(digest(canonical(existing)),)).fetchone() if existing else None
        local_replay=row is not None and (row['status'] in {'READY','UNCERTAIN'} or
            (Path(config['state'])/'provider').exists() and not (Path(config['state'])/'provider/sandbox.json').exists())
        if not local_replay:
            connectivity.require(['modal'],Path(config['state'])/'connectivity.json')
            provider=ModalProvider(config['provider'])
        while True:
            result=tick(config,provider,accounts,host_proof=proof)
            if result.get('retention',{}).get('status')=='RETENTION_DUE':
                connectivity.require(['modal'],Path(config['state'])/'connectivity.json')
                provider=ModalProvider(config['provider'])
                result=tick(config,provider,accounts,host_proof=proof)
            private_records.atomic(Path(config['state'])/'STATUS.json',result)
            if result['status']!='RUNNING' or time.monotonic()>=deadline:break
            time.sleep(10)
        print(json.dumps({k:v for k,v in result.items() if k in ('status','scientific_calls','no_automatic_retry','retention','storage_may_continue_accruing')},sort_keys=True))
        if result['status']!='VERIFIED' or result.get('retention',{}).get('automatic_cleanup_retry') is False:raise SystemExit(1)
    finally:batch.db.close()

if __name__=='__main__':main()
