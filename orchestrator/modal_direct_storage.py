"""Server-owned direct-input preparation in the existing ledger.

One immutable binding and one provider intent. Repeated ticks only reconcile
that attempt; they never create a replacement. No scientific allowance exists
for this administrative owner and no notebook or model is run here.
"""
from datetime import datetime,timezone,timedelta
from pathlib import Path
import json
import os
import subprocess
import sys
from orchestrator import private_records,connectivity
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest,read
from orchestrator.manual_driver import write_once
from orchestrator.remote_supervisor import lock
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_budget import ComputeAccounts
from orchestrator import modal_direct_budget as budget,modal_download_package as package,modal_download_provider as download


def utc():return datetime.now(timezone.utc)


def host_check(path):
    """Actual installed artifacts and live timer, before credential/provider use."""
    from orchestrator.manual_host_guard import trusted
    from tools.manual_promotion import manifest_check
    path=trusted(Path(path));config=read(path)
    if set(config)!={'schema','source','release','installation_record','installation_sha256',
                     'package','package_manifest_sha256','batch_ledger','state','provider','units'}:
        raise ValueError('DIRECT_STORAGE_CONFIG_FIELDS')
    if config['schema']!='direct-development-storage/v1':raise ValueError('DIRECT_STORAGE_SCHEMA')
    install=trusted(Path(config['installation_record'])/'installed.json')
    if digest(install.read_bytes())!=config['installation_sha256']:raise ValueError('DIRECT_STORAGE_INSTALL_CHANGED')
    receipt=manifest_check(Path('/'),config['installation_record'])
    if receipt['source']!=config['source'] or receipt['layout']['release']!=config['release']:
        raise ValueError('DIRECT_STORAGE_RELEASE_BINDING')
    if Path(__file__).resolve()!=Path(config['release'])/'orchestrator/modal_direct_storage.py':
        raise ValueError('DIRECT_STORAGE_WRONG_EXECUTABLE')
    if os.getuid()!=1003 or not sys.flags.no_user_site:raise ValueError('DIRECT_STORAGE_SERVICE_USER')
    for name,row in config['units'].items():
        unit=trusted(Path('/etc/systemd/system')/name)
        if set(row)!={'sha256'} or digest(unit.read_bytes())!=row['sha256']:
            raise ValueError('DIRECT_STORAGE_UNIT_CHANGED')
    timers=[n for n in config['units'] if n.endswith('.timer')]
    services=[n for n in config['units'] if n.endswith('.service')]
    if len(timers)!=1 or len(services)!=1 or len(config['units'])!=2:raise ValueError('DIRECT_STORAGE_UNIT_SET')
    expected={'LoadState':'loaded','ActiveState':'active','UnitFileState':'enabled'}
    observed=subprocess.check_output(['/usr/bin/systemctl','show',timers[0],'--property=LoadState,ActiveState,UnitFileState'],text=True)
    if dict(line.split('=',1) for line in observed.splitlines() if '=' in line)!=expected:
        raise ValueError('DIRECT_STORAGE_RETENTION_TIMER_REQUIRED')
    props={'User':'partho','NoNewPrivileges':'yes','ProtectSystem':'strict','PrivateTmp':'yes','ProtectHome':'read-only'}
    observed=subprocess.check_output(['/usr/bin/systemctl','show',services[0],'--property='+','.join(props)],text=True)
    if dict(line.split('=',1) for line in observed.splitlines() if '=' in line)!=props:
        raise ValueError('DIRECT_STORAGE_SERVICE_RESTRICTIONS')
    package.verify(config['package'],config['package_manifest_sha256'])
    return config,{'status':'PASS','source':config['source'],'config_sha256':digest(path.read_bytes()),
                   'installation_sha256':config['installation_sha256'],'timer':timers[0]}


@private_records.private_umask
def tick(config,provider,accounts,*,host_proof,now=None):
    """Deterministic controller; injected provider is the only external boundary."""
    now=now or utc();state=Path(config['state'])
    private_records.check(state)
    if (host_proof.get('status')!='PASS' or host_proof.get('source')!=config['source'] or
            host_proof.get('installation_sha256')!=config['installation_sha256']):
        raise ValueError('DIRECT_STORAGE_HOST_PROOF')
    with lock(state/'tick.lock'):
        private_records.check(state/'tick.lock')
        manifest=package.verify(config['package'],config['package_manifest_sha256'])
        bind_path=state/'binding.json'
        if not bind_path.exists():
            if (accounts.batch.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
            view=read(state/'initial-billing.json') if (state/'initial-billing.json').exists() else provider.billing_snapshot()
            size=sum(row['bytes'] for ref in manifest['plans'].values()
                     for row in read(Path(config['package'])/ref['path'])['files'].values())
            run='sprint13b-inputs-'+digest(canonical({'source':config['source'],'package':config['package_manifest_sha256']}))[:24]
            binding={'purpose':budget.PURPOSE,'authority_sha256':budget.AUTHORITY,
                'download_authority_sha256':budget.DOWNLOAD_AUTHORITY,'team_authority_sha256':budget.TEAM_AUTHORITY,
                'run_id':run,'source':config['source'],'download_bytes':size,'envelope':budget.envelope(size,view['rates']),
                'package_manifest_sha256':config['package_manifest_sha256'],
                'installed_config_sha256':host_proof['config_sha256'],
                'asset_expires_utc':(now+timedelta(days=30)).isoformat()}
            write_once(state/'initial-billing.json',canonical(view))
            write_once(bind_path,canonical(binding))
        binding=read(bind_path);ident=digest(canonical(binding))
        if (binding['source']!=config['source'] or binding['package_manifest_sha256']!=config['package_manifest_sha256'] or
                binding['installed_config_sha256']!=host_proof['config_sha256']):
            raise ValueError('DIRECT_STORAGE_EXISTING_BINDING_CHANGED')
        if now>=datetime.fromisoformat(binding['asset_expires_utc']):
            from orchestrator.modal_direct_retention import expire
            return expire(provider,accounts,binding,config['package'],state,now=now)
        row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
        if row is None:
            owner={'purpose':budget.PURPOSE,'authority_sha256':budget.AUTHORITY,'source':config['source'],
                   'binding_sha256':ident,'no_scientific_allowance':True}
            accounts.batch.register_run(binding['run_id'],owner)
            if not budget.reserve(accounts,ident,binding['run_id'],binding,billing_snapshot=provider.billing_snapshot(),now=now):
                raise ValueError('DIRECT_STORAGE_RESERVATION_RACE')
            row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
        if row['binding']!=canonical(binding).decode():raise ValueError('DIRECT_STORAGE_LEDGER_BINDING')
        if row['status']=='UNCERTAIN':return {'status':'BLOCKED_PRESERVED_FAILURE','no_automatic_retry':True}
        operation=state/'provider'
        if row['status']=='READY':
            result=read(state/'VERIFIED.json')
            accounts.finish_assets(ident,'READY',result)
            accounts.batch.complete_run(binding['run_id'],result)
            return result
        if row['status']!='RESERVED':raise ValueError('DIRECT_STORAGE_ASSET_STATUS')
        if (accounts.batch.folder/'HALT').exists():return {'status':'HALTED','preserved_reservation':True}
        if not operation.exists():
            handle=download.launch(provider,accounts,binding,config['package'],operation)
        elif (operation/'sandbox.json').is_file():handle=read(operation/'sandbox.json')
        else:return {'status':'BLOCKED_CREATE_UNCERTAIN','no_automatic_retry':True}
        result=download.observe(provider,binding,config['package'],handle)
        if result['status']=='VERIFIED':
            result={**result,'binding_sha256':ident,'source':config['source'],'asset_expires_utc':binding['asset_expires_utc'],
                    'data_volume_id':handle['data_volume_id'],'package_volume_id':handle['package_volume_id']}
            write_once(state/'VERIFIED.json',canonical(result))
            accounts.finish_assets(ident,'READY',result)
            accounts.batch.complete_run(binding['run_id'],result)
        elif result['status']=='FAILED':
            write_once(state/'FAILED.json',canonical(result));accounts.finish_assets(ident,'UNCERTAIN',result)
        return result


def main():
    import argparse
    from orchestrator.modal_provider import ModalProvider
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True)
    args=parser.parse_args();config,proof=host_check(args.config)
    # This connection check precedes registration, reservation and any create.
    connectivity.require(['modal'],Path(config['state'])/'connectivity.json')
    provider=ModalProvider(config['provider'])
    batch=BatchAccounts(config['batch_ledger']);accounts=ComputeAccounts(batch)
    try:
        result=tick(config,provider,accounts,host_proof=proof)
        private_records.atomic(Path(config['state'])/'STATUS.json',result)
        print(json.dumps({k:v for k,v in result.items() if k in ('status','files','bytes','no_automatic_retry')},sort_keys=True))
    finally:batch.db.close()

if __name__=='__main__':main()
