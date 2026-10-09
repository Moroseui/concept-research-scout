"""Two frozen base smoke fits through existing provisioning and accounting.

Reuses the unchanged benchmark package. The existing retention service calls
cleanup_shared, which adds all package consumers to the original cleanup guard.
No scientific changes, automatic launches, new timers or exception receipts.
"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import json
import re
from orchestrator import item4_benchmark_handoff as base
from orchestrator import item4_stage1_cap as cap
from orchestrator import private_records as pr
from orchestrator.manual_executor import digest
from orchestrator.modal_executor import canonical
from orchestrator.manual_driver import write_once
from orchestrator.review_contract import strict_json

CHANGE='item4-smoke-connection-20261009'
PURPOSE='M4_ITEM4_BASE_SMOKE_ASSETS'
AMOUNT=1000000
RECORD=base.RECORD  # unchanged protected preprocessing originals
require=base.require
fresh_volume=base.fresh_volume
retention_ready=base.retention_ready
FITS=[{'arm': 'A1_repeat', 'fit_id': 'smoke-A1_repeat', 'fold': 0, 'outputs': ['metrics.json', 'epoch-timing.json', 'validation.json'], 'preprocessing_id': 'prep-A1_repeat', 'realization': 'smoke-r1', 'stage': 'SMOKE', 'validation_checks': ['input-bindings', 'native-training', 'finite-loss', 'epoch-timing', 'heldout-scoring', 'private-output-boundary', 'native-resume']}, {'arm': 'A1_repeat2', 'fit_id': 'smoke-A1_repeat2', 'fold': 0, 'outputs': ['metrics.json', 'epoch-timing.json', 'validation.json'], 'preprocessing_id': 'prep-A1_repeat', 'realization': 'smoke-r2', 'stage': 'SMOKE', 'validation_checks': ['input-bindings', 'native-training', 'finite-loss', 'epoch-timing', 'heldout-scoring', 'private-output-boundary']}]


def validate_policy(p):
    original=base.contract()
    expected=deepcopy(original)
    expected.update(fits=FITS,selected_gpu=p.get('selected_gpu'),measured_hardware=p.get('measured_hardware'))
    ref=p.get('measured_hardware')
    require(p==expected and p['run_id']==cap.RUN and p['source']==cap.PINS['source']
        and p['preprocessing_runtime']['image_id']==cap.PINS['image_id']
        and p['selected_gpu'] in base.GPUS and isinstance(ref,dict)
        and set(ref)=={'path','sha256'} and isinstance(ref['sha256'],str)
        and len(ref['sha256'])==64 and all(c in '0123456789abcdef' for c in ref['sha256'])
        and ref['path']==str(Path(p['package_manifest']['path']).parent.parent/
            'measured-projections'/(ref['sha256']+'.json')), 'SMOKE_SCOPE')
    return original


def context(driver,value):
    from orchestrator import experiment_dispatch,experiment_projection
    p=deepcopy(base.contract())
    base.checked_driver(driver,value,p)
    plan=strict_json((driver.state/'experiment-package/execution-plan.json').read_bytes())
    require(plan['fits'][3:5]==FITS,'SMOKE_FITS_CHANGED')
    require(value.get('measured_hardware') is not None,'MEASURED_HARDWARE_REQUIRED')
    measured=experiment_projection.verify(driver,value,experiment_dispatch.load(driver,value),
        value['measured_hardware'],kind='hardware')
    p.update(fits=deepcopy(FITS),selected_gpu=measured['calculation']['selected_gpu'],
        measured_hardware=deepcopy(value['measured_hardware']))
    validate_policy(p)
    return p


def policy_sha(p):
    validate_policy(p)
    return digest(canonical(p))


def shared_package(accounts):
    p=base.contract();folder=base.state(p)
    require(not (folder/'UNCERTAIN.json').exists(),'UNCERTAIN_BENCHMARK_ASSETS')
    ready=strict_json(pr.check(folder/'READY.json').read_bytes())
    ident=digest(canonical(base.asset_binding(p)))
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
    require(row is not None and row['status']=='READY' and strict_json(row['receipt'])==ready
        and row['binding']==canonical(base.asset_binding(p)).decode()
        and ready['contract_sha256']==base.CONTRACT_SHA and ready['reservation_id']==ident,
        'SHARED_PACKAGE_LEDGER_CHANGED')
    return deepcopy(ready['package'])


def cleanup_shared(accounts,provider,now=None):
    # All original expiry, manifest membership and ledger checks still run.
    # Refuse any live/uncertain consumer, including continuation segments and
    # apps not in the original benchmark list, before any package deletion.
    p=base.contract();now=now or datetime.now(timezone.utc)
    if now<datetime.fromisoformat(p['preprocessing_runtime']['asset_expires_utc']):
        return {'status':'NOT_DUE'}
    if not base.state(p).exists():return {'status':'NO_ASSETS'}
    package=shared_package(accounts)
    require(all(r['status'] in {'COLLECTED','ACCOUNTED'} for r in
        accounts.db.execute('SELECT * FROM autonomy_compute')
        if strict_json(r['binding']).get('package_volume_id')==package['id']),
        'ACTIVE_OR_UNCERTAIN_SHARED_PACKAGE_CONSUMER')
    return base.cleanup_package(accounts,provider,now)

def state(p):
    return Path(p['package_manifest']['path']).parent.parent/CHANGE

def asset_binding(p):
    return {'purpose':PURPOSE,'run_id':p['run_id'],'contract_sha256':policy_sha(p),
            'source':p['source'],'package_manifest_sha256':p['package_manifest']['sha256'],
            'preprocessing_binding_sha256':digest(canonical(p['preprocessing_binding'])),
            'fits':[x['fit_id'] for x in p['fits']], 'reserved_micro_usd':AMOUNT,
            'expires':p['preprocessing_runtime']['asset_expires_utc']}

def reserve(accounts,p,billing,now=None):
    """Reserve before any provider mutation, inside the same item4 caps."""
    from orchestrator import modal_terminal_cost as costs, item4_closed_asset_billing as closed
    from orchestrator.modal_billing import headroom, decimal
    from orchestrator.modal_item4_policy import TOTAL_CAP,USAGE_CEILING,SPEND_CEILING
    SMOKE_CAP=cap.CAP
    validate_policy(p)
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
                       'micro_usd':AMOUNT,'operator_approval_sha256':cap.OPERATOR_SHA,'caps':{'smoke':SMOKE_CAP,'total':TOTAL_CAP}}).decode()))
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK');raise
    return ident

def asset_names(p, ident):
    prefix='research-smoke-'+ident[:20]
    names={fit['fit_id']:prefix+'-'+fit['fit_id'] for fit in p['fits']}
    package=prefix+'-package'
    # Match the pinned provider SDK's object-name contract before reservation.
    for name in [package,*names.values(),*(x+'-progress' for x in names.values())]:
        require(len(name)<=64 and re.fullmatch('[a-zA-Z0-9-_.]+',name) is not None,
                'PROVIDER_OBJECT_NAME')
    return names,package

@pr.private_umask
def prepare_assets(driver,value,accounts,provider):
    p=context(driver,value);retention_ready()
    package=shared_package(accounts)
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
        result={'reservation_id':ident,'contract_sha256':policy_sha(p),'fits':{},'billing_snapshot':billing}
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
        result['package']=package
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
    require(ready['status']=='READY' and ready['contract_sha256']==policy_sha(p) and
            ready['reservation_id']==digest(canonical(asset_binding(p))) and
            set(ready['fits'])=={f['fit_id'] for f in p['fits']}, 'ASSET_RECEIPT')
    rows=[]
    for fit,gpu in zip(p['fits'],[p['selected_gpu']]*len(FITS)):
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
    p=context(driver,value)
    folder=state(p);require(not (folder/'UNCERTAIN.json').exists(),'UNCERTAIN_ASSETS')
    raw=pr.check(folder/'READY.json').read_bytes();ready=strict_json(raw)
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ready['reservation_id'],)).fetchone()
    require(row is not None and row['status']=='READY' and
            strict_json(row['receipt'])==ready and row['binding']==canonical(asset_binding(p)).decode() and
            row['reserved_micro_usd']==AMOUNT,'ASSET_LEDGER_CHANGED')
    from orchestrator.item4_closed_attempt_billing import snapshot
    snapshot(ready['billing_snapshot'])
    rows=runtime_rows(p,ready,ready['billing_snapshot']['rates'])
    return {'schema':'item4-base-smoke-runtime-proposal/v1','contract_sha256':policy_sha(p),
            'ready_sha256':digest(raw),'rows':rows,'provider_calls':0}
