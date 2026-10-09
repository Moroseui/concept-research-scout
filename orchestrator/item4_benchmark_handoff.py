"""Bound asset setup for the three frozen real-epoch benchmarks.

No training here. Existing prepare/publish, package verifier, provider preflight
and normal per-fit compute admission remain the execution route.
"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import subprocess
from orchestrator import private_records as pr
from orchestrator.manual_executor import digest
from orchestrator.manual_host_guard import trusted
from orchestrator.modal_executor import canonical
from orchestrator.manual_driver import write_once
from orchestrator.review_contract import strict_json

CHANGE = 'item4-benchmark-handoff-20261009'
ROOT = Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD = Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
CONTRACT_SHA = '62c241b1e75372635f7a662245ad41437ee09a417b72de00cdd3496d59f07da4'
PURPOSE = 'M4_ITEM4_BENCHMARK_ASSETS'
GPUS = ('A100-80GB', 'H100', 'B200')
AMOUNT = 1000000


def require(ok, why):
    if not ok:
        raise ValueError('ITEM4_BENCHMARK_' + why)


def contract():
    raw = pr.check(trusted(ROOT/'docs/ITEM4_BENCHMARK_HANDOFF_PRIVATE.json')).read_bytes()
    require(digest(raw) == CONTRACT_SHA, 'CONTRACT_CHANGED')
    p = strict_json(raw)
    require(p['schema'] == 'item4-benchmark-handoff/v1' and
            [x['fit_id'] for x in p['fits']] == ['benchmark-'+g for g in GPUS] and
            all(x['stage']=='SMOKE' and x['arm']=='A1_repeat' and x['fold']==0 and
                x['preprocessing_id']=='prep-A1_repeat' for x in p['fits']) and
            p['preparation_micro_usd']==AMOUNT and p['maximum_package_bytes']==4*1024**2,
            'FROZEN_SCOPE')
    return p


def state(p):
    return Path(p['package_manifest']['path']).parent.parent/CHANGE


def checked_driver(driver, value, p):
    from orchestrator import experiment_package, experiment_approval
    from orchestrator import experiment_preprocessing_dispatch as pd
    require(driver.config['run_id']==p['run_id'] and driver.config['source']==p['source'] and
            value['phase']=='EXECUTE_EXPERIMENT', 'OWNER')
    require('validation_admission' in experiment_approval.verify(driver,value), 'VALIDATION_ONLY')
    package=driver.state/'experiment-package'
    experiment_package.verify(driver,value,package)
    require(digest((package/'manifest.json').read_bytes())==p['package_manifest']['sha256'],
            'SCIENTIFIC_PACKAGE_CHANGED')
    plan=strict_json((package/'execution-plan.json').read_bytes())
    require(plan['fits'][:3]==p['fits'], 'FROZEN_FITS_CHANGED')
    from orchestrator.modal_executor import item4_job
    job=item4_job(p['preprocessing_binding'])
    selected=pd.load(driver,value)
    actual=[x for x in selected['jobs'] if x['job']==job]
    require(len(actual)==1 and value['preprocessing_dispatch'][job]['phase']=='COMPLETE',
            'PREPROCESSING_NOT_COMPLETE')
    saved=pd.saved_collection(driver,actual[0],value['preprocessing_dispatch'][job])
    require(saved['binding_sha256']==digest(canonical(p['preprocessing_binding'])), 'PREPROCESSING_BINDING')
    for name,ref in p['preprocessing_records'].items():
        require(str(Path(saved['folder'])/name)==ref['path'] and saved['files'][name]==ref['sha256'] and
                digest(pr.check(ref['path']).read_bytes())==ref['sha256'], 'PREPROCESSING_CHANGED')
    from orchestrator import experiment_modal_package as bridge
    code={'run.py':bridge.WORKER.read_bytes(),'execution.py':(package/'code/execution.py').read_bytes(),
          **bridge.support_files()}
    require({k:digest(raw) for k,raw in code.items()}==p['code_hashes'],'CODE_CHANGED')
    metadata=['SPEC.md','review.json','execution-plan.json','approval.json']
    require(sum(len(v) for v in code.values()) + sum((package/k).stat().st_size for k in metadata)
            +(package/'manifest.json').stat().st_size <= p['maximum_package_bytes'],'PACKAGE_SIZE')
    return saved


def retention_ready():
    timer='research-'+CHANGE+'-retention.timer'
    values=dict(x.split('=',1) for x in subprocess.check_output(
        ['systemctl','show',timer,'-p','LoadState','-p','UnitFileState','-p','ActiveState'],text=True).splitlines())
    require(values=={'LoadState':'loaded','UnitFileState':'enabled','ActiveState':'active'},
            'RETENTION_TIMER_REQUIRED')
    return timer


def asset_binding(p):
    return {'purpose':PURPOSE,'run_id':p['run_id'],'contract_sha256':CONTRACT_SHA,
            'source':p['source'],'package_manifest_sha256':p['package_manifest']['sha256'],
            'preprocessing_binding_sha256':digest(canonical(p['preprocessing_binding'])),
            'fits':[x['fit_id'] for x in p['fits']], 'reserved_micro_usd':AMOUNT,
            'expires':p['preprocessing_runtime']['asset_expires_utc']}


def reserve(accounts,p,billing,now=None):
    """Reserve before any provider mutation, inside the same item4 caps."""
    from orchestrator import modal_terminal_cost as costs, item4_closed_asset_billing as closed
    from orchestrator.modal_billing import headroom, decimal
    from orchestrator.modal_item4_policy import SMOKE_CAP,TOTAL_CAP,USAGE_CEILING,SPEND_CEILING
    now=now or datetime.now(timezone.utc); binding=asset_binding(p);ident=digest(canonical(binding))
    require(now < datetime.fromisoformat(binding['expires']), 'ASSET_EXPIRED')
    require(decimal(billing['rates']['volume_storage_gib_month_cost'])==decimal('.09') and
            decimal(billing['rates']['egress_gib_cost'])==decimal('.04'), 'STORAGE_RATES_CHANGED')
    costs.observe_billing(accounts,billing,now)
    db=accounts.db;db.execute('BEGIN IMMEDIATE')
    try:
        require(not (accounts.batch.folder/'HALT').exists(), 'BATCH_HALTED')
        require(db.execute('SELECT 1 FROM autonomy_assets WHERE id=?',(ident,)).fetchone() is None,
                'EXISTING_PREPARATION_RECONCILE')
        owner=db.execute('SELECT * FROM autonomy_runs WHERE id=?',(p['run_id'],)).fetchone()
        require(owner is not None and owner['status']=='ACTIVE','ACTIVE_OWNER_REQUIRED')
        from orchestrator.experiment_owner import verify_item4
        verify_item4(accounts.batch,p['run_id'],strict_json(owner['binding']),p['preprocessing_binding'])
        from orchestrator.spending_continuation import closed_ids
        resolved_calls=closed_ids(accounts.batch,p['run_id'])
        require(all(r['id'] in resolved_calls for r in db.execute(
            "SELECT id FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')")), 'UNRESOLVED_CALL')
        from orchestrator.modal_direct_recovery import resolved_failure_ids
        from orchestrator.item4_validation_admission import retained_terminal
        resolved=resolved_failure_ids(accounts,root=accounts.batch.filesystem_root)
        ta,tc=retained_terminal(accounts,p['preprocessing_binding']);resolved|=ta
        assets=db.execute('SELECT * FROM autonomy_assets').fetchall()
        compute=db.execute('SELECT * FROM autonomy_compute').fetchall()
        require(all(r['status']=='READY' or r['id'] in resolved for r in assets), 'UNRESOLVED_ASSET')
        require(all(r['status'] in {'COLLECTED','ACCOUNTED'} or r['id'] in tc for r in compute),
                'ACTIVE_OR_UNCERTAIN_COMPUTE')
        require(not any(strict_json(r['binding']).get('purpose')==PURPOSE for r in assets),
                'EXISTING_PREPARATION_RECONCILE')
        amounts={r['id']:closed.effective(accounts,r,billing,now) for r in assets}
        from orchestrator.modal_direct_budget import selected_asset as direct
        from orchestrator.modal_environment_budget import selected_asset as environment
        assets_total=sum(amounts[r['id']] for r in assets if r['run']==p['run_id'] or direct(r) or environment(r))
        exposure=costs.exposure(db,compute,billing)
        require(not exposure['underestimated_apps'],'BILLING_EXCEEDS_BOUND')
        require(assets_total+exposure['smoke_cost'].get(p['run_id'],0)+AMOUNT<=SMOKE_CAP and
                assets_total+exposure['run_cost'].get(p['run_id'],0)+AMOUNT<=TOTAL_CAP,'HARD_COST_CAP')
        commitments=exposure['commitments']
        commitments.update({'asset-reservation:'+r['id']:amounts[r['id']] for r in assets})
        room=headroom(billing,now=now,usage_limit_micro=USAGE_CEILING,
                      spend_limit_micro=SPEND_CEILING,commitments=commitments)
        require(AMOUNT<=min(room['usage_headroom_micro'],room['spend_headroom_micro']), 'PROVIDER_HEADROOM')
        db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'RESERVED',?,NULL)",
                   (ident,p['run_id'],canonical(binding).decode(),AMOUNT))
        db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':assets-reserved',p['run_id'],
            canonical({'kind':PURPOSE,'binding':binding,'billing_snapshot':billing,'headroom':room,
                       'micro_usd':AMOUNT,'caps':{'smoke':SMOKE_CAP,'total':TOTAL_CAP}}).decode()))
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK');raise
    return ident



def asset_names(p, ident):
    prefix='research-bench-'+ident[:20]
    names={fit['fit_id']:prefix+'-'+fit['fit_id'] for fit in p['fits']}
    package=prefix+'-package'
    # Match the pinned provider SDK's object-name contract before reservation.
    for name in [package,*names.values(),*(x+'-progress' for x in names.values())]:
        require(len(name)<=64 and re.fullmatch('[a-zA-Z0-9-_.]+',name) is not None,
                'PROVIDER_OBJECT_NAME')
    return names,package


def fresh_volume(provider,name):
    try:provider.modal.Volume.from_name(name,version=2,create_if_missing=False,client=provider.client).hydrate(client=provider.client)
    except provider.modal.exception.NotFoundError:pass
    else:raise ValueError('ITEM4_BENCHMARK_EXISTING_VOLUME_RECONCILE')
    volume=provider.modal.Volume.from_name(name,version=2,create_if_missing=True,client=provider.client)
    volume.hydrate(client=provider.client)
    require(volume.listdir('/',recursive=True)==[], 'NEW_VOLUME_NOT_EMPTY')
    return {'name':name,'id':volume.object_id,'version':2}


@pr.private_umask
def prepare_assets(driver,value,accounts,provider):
    p=contract();checked_driver(driver,value,p);retention_ready()
    folder=state(p)
    require(not folder.exists() and not folder.is_symlink(), 'EXISTING_PREPARATION_RECONCILE')
    require(provider.config==p['preprocessing_runtime'],'PROVIDER_CONFIG')
    # Read-only, native SDK authentication and rates. No registry build.
    billing=provider.billing_snapshot()
    names,package_name=asset_names(p,digest(canonical(asset_binding(p))))
    pr.mkdir(folder)
    ident=reserve(accounts,p,billing)
    write_once(folder/'INTENT.json',canonical({'reservation_id':ident,'binding':asset_binding(p)}))
    try:
        result={'reservation_id':ident,'contract_sha256':CONTRACT_SHA,'fits':{},'billing_snapshot':billing}
        for fit in p['fits']:
            name=names[fit['fit_id']]
            write_once(folder/(fit['fit_id']+'-intent.json'),canonical({'name':name,'fit_id':fit['fit_id']}))
            try:provider.modal.App.lookup(name,create_if_missing=False,client=provider.client)
            except provider.modal.exception.NotFoundError:pass
            else:raise ValueError('ITEM4_BENCHMARK_EXISTING_APP_RECONCILE')
            app=provider.modal.App.lookup(name,create_if_missing=True,client=provider.client)
            write_once(folder/(fit['fit_id']+'-app.json'),canonical({'name':name,'id':app.app_id}))
            progress=fresh_volume(provider,name+'-progress')
            entry={'app_name':name,'app_id':app.app_id,'progress':progress}
            write_once(folder/(fit['fit_id']+'-assets.json'),canonical(entry))
            result['fits'][fit['fit_id']]=entry
        result['package']=fresh_volume(provider,package_name)
        write_once(folder/'package-volume.json',canonical(result['package']))
        result.update(status='READY',image_reused=p['preprocessing_runtime']['image_id'],
                      scientific_calls=0,new_compute=0,original_reservation_retained=True)
        write_once(folder/'READY.json',canonical(result))
        accounts.finish_assets(ident,'READY',result)
        return result
    except BaseException as error:
        outcome={'status':'UNCERTAIN','no_retry':True,'error_type':type(error).__name__}
        write_once(folder/'UNCERTAIN.json',canonical(outcome))
        accounts.finish_assets(ident,'UNCERTAIN',outcome)
        raise


def runtime_rows(p,ready,rates):
    """Pure binding construction; identities come from genuine preprocessing."""
    from orchestrator.modal_item4_policy import quote
    require(ready['status']=='READY' and ready['contract_sha256']==CONTRACT_SHA and
            ready['reservation_id']==digest(canonical(asset_binding(p))) and
            set(ready['fits'])=={f['fit_id'] for f in p['fits']}, 'ASSET_RECEIPT')
    rows=[]
    for fit,gpu in zip(p['fits'],GPUS):
        found=ready['fits'][fit['fit_id']]
        runtime=deepcopy(p['preprocessing_runtime']);source=runtime.pop('item4_preprocessing_assets')
        runtime['package_volume_id']=ready['package']['id'];runtime['app_name']=found['app_name']
        fb={k:fit[k] for k in ['arm','fold','realization']}
        fb.update(run_id=p['run_id'],spec_sha256=p['spec_sha256'],
                  code_sha256=digest(canonical(p['code_hashes'])),**p['preprocessing_identity'])
        progress={'volume_id':found['progress']['id'],'volume_name':found['progress']['name'],
                  'fit_id':fit['fit_id'],'fit_binding':fb}
        inputs=RECORD/'inputs'
        ref=lambda name:{'path':str(inputs/name),'sha256':p['preprocessing_records'][name]['sha256']}
        runtime['item4_assets']={'app_name':found['app_name'],'app_id':found['app_id'],'progress':progress,
            'preprocessed_volume_id':source['output_volume_id'],'preprocessing_receipt':str(inputs/'preprocessing.json'),
            'preprocessing_sha256':p['preprocessing_records']['preprocessing.json']['sha256'],
            'preprocessing_code_sha256':p['preprocessing_binding']['execution']['module_sha256'],
            'cohort_manifest':source['source_records']['cohort'],
            'plans_name':p['preprocessing_binding']['preprocessing']['plans_name'],
            'split_sha256':p['preprocessing_binding']['preprocessing']['split_sha256'],
            'preprocessing_job_sha256':digest(canonical(p['preprocessing_binding']))}
        runtime['item4_preprocessing_validation']=ref('validation.json')
        runtime['item4_preprocessing_execution']=ref('result.json')
        binding={k:deepcopy(v) for k,v in p['preprocessing_binding'].items() if k not in {
            'preprocessing','source_volume_id','preprocessing_output_volume_id','resume','fresh_start',
            'execution','code_sha256','spec_sha256','review_sha256','execution_plan_sha256'}}
        binding.update(runtime_sha256=digest(canonical(runtime)),package_volume_id=runtime['package_volume_id'],
            progress=progress,preprocessed_volume_id=source['output_volume_id'],
            preprocessing_sha256=runtime['item4_assets']['preprocessing_sha256'],
            preprocessing_job_sha256=runtime['item4_assets']['preprocessing_job_sha256'],outputs=fit['outputs'])
        binding['experiment'].update(fit_id=fit['fit_id'],billing_object_id=found['app_id'],segment=1)
        binding['resources']['gpu']=gpu
        require(binding['overhead_micro_usd']==5000000 and binding['resources']=={
            'gpu':gpu,'cpu':16,'memory_mib':131072,'timeout_seconds':3600},'UNCHANGED_RESOURCE_BOUND')
        binding['cost']=quote(binding['resources'],rates,binding['overhead_micro_usd'])
        rows.append({'fit':fit['fit_id'],'runtime':runtime,'binding':binding})
    return rows



def export_runtimes(driver,value,accounts):
    p=contract();checked_driver(driver,value,p)
    folder=state(p);require(not (folder/'UNCERTAIN.json').exists(),'UNCERTAIN_ASSETS')
    raw=pr.check(folder/'READY.json').read_bytes();ready=strict_json(raw)
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ready['reservation_id'],)).fetchone()
    require(row is not None and row['status']=='READY' and
            strict_json(row['receipt'])==ready and row['binding']==canonical(asset_binding(p)).decode() and
            row['reserved_micro_usd']==AMOUNT,'ASSET_LEDGER_CHANGED')
    from orchestrator.item4_closed_attempt_billing import snapshot
    snapshot(ready['billing_snapshot'])
    rows=runtime_rows(p,ready,ready['billing_snapshot']['rates'])
    return {'schema':'item4-benchmark-runtime-proposal/v1','contract_sha256':CONTRACT_SHA,
            'ready_sha256':digest(raw),'rows':rows,'provider_calls':0}


def cleanup_package(accounts,provider,now=None):
    """Existing input-copy cleanup only; never delete progress or checkpoints."""
    p=contract();now=now or datetime.now(timezone.utc)
    if now<datetime.fromisoformat(p['preprocessing_runtime']['asset_expires_utc']):
        return {'status':'NOT_DUE'}
    folder=state(p)
    if not folder.exists():return {'status':'NO_ASSETS'}
    require((folder/'READY.json').is_file() and not (folder/'UNCERTAIN.json').exists(),
            'PARTIAL_ASSETS_REQUIRE_RECONCILIATION')
    ready=strict_json(pr.check(folder/'READY.json').read_bytes())
    ident=digest(canonical(asset_binding(p)))
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
    require(row is not None and row['status']=='READY' and strict_json(row['receipt'])==ready,
            'ASSET_LEDGER_CHANGED')
    apps={v['app_id'] for v in ready['fits'].values()}
    require(all(r['status'] in {'COLLECTED','ACCOUNTED'} for r in
        accounts.db.execute('SELECT * FROM autonomy_compute')
        if strict_json(r['binding']).get('experiment',{}).get('billing_object_id') in apps),
        'ACTIVE_OR_UNCERTAIN_COMPUTE')
    from orchestrator.modal_executor import verify_package
    from orchestrator.manual_executor import inventory
    from orchestrator.modal_cleanup import remove_members
    # Real prepared package supplies exact original bytes. Never infer them
    # from a mutable remote listing or clear scientific progress objects.
    preparation=folder/'prepared'
    require((preparation/'preparation.json').is_file(),'PACKAGE_ORIGINAL_REQUIRED')
    record=strict_json(pr.check(preparation/'preparation.json').read_bytes())
    packages=[]
    for item in record['packages']:
        original=Path(item['manifest']['path']).parent
        raw=pr.check(original/'manifest.json').read_bytes()
        require(digest(raw)==item['manifest']['sha256'],'PACKAGE_MANIFEST_CHANGED')
        manifest=strict_json(raw);verify_package(original,manifest['binding'])
        files={name:{'sha256':pin,'bytes':(original/name).stat().st_size}
               for name,pin in inventory(original).items() if name!='manifest.json'}
        packages.append(files)
    require(len(packages)==3 and all(x==packages[0] for x in packages),'PACKAGE_SET_CHANGED')
    require(sum(x['bytes'] for x in packages[0].values())<=p['maximum_package_bytes'],'PACKAGE_SIZE')
    cleanup=folder/'cleanup';pr.mkdir(cleanup,exist_ok=True)
    remove_members(provider,ready['package']['id'],packages[0],cleanup,'benchmark-package')
    return {'status':'PACKAGE_CLEARED','scientific_progress_preserved':True,
            'originals_preserved':True,'reservation_retained':True}
