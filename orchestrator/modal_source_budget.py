"""One frozen source-copy reservation inside the original item4 caps.

Reuses existing owner, cap, exposure, headroom and exact terminal-failure proofs.
No model allowance, reservation release, new compute worker or scientific claim.
"""
from datetime import datetime,timezone,timedelta
from decimal import Decimal,ROUND_CEILING
from pathlib import Path
import json,re
from orchestrator import modal_source_composition as source,private_records as pr
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from orchestrator.modal_billing import decimal,headroom
from orchestrator.modal_item4_policy import AUTHORITY,TEAM_AUTHORITY,SMOKE_CAP,TOTAL_CAP,USAGE_CEILING,SPEND_CEILING
from orchestrator.experiment_context import ITEM4_RUN as RUN

PURPOSE=source.PURPOSE
NATIVE_ID='40860aa053572ffc0571e45c89b950eaf813725b107f981ad18d5b9921cdb59c'
NATIVE_STATE=Path('/var/lib/research-system-manual-sprint10/environment-inventory/item4-author13-native-synthetic-v1')
DIRECT_ID='7a246711ff49fdcd7d9733b4ce18e276acb6ad0d52bbc46714a97fa5250b9975'
DIRECT_VOLUME='vo-uiRB7DAXuqsMGLRLZg7k1h'
MAX_RESERVATION=5_000_000

def require(ok,why):
    if not ok:raise ValueError('SOURCE_BUDGET_'+why)

def envelope(rates):
    keys=('volume_storage_gib_month_cost','egress_gib_cost')
    require(all(k in rates and decimal(rates[k])>=0 for k in keys),'RATES')
    # A single immutable destination, plus conservative upload/staging overhead.
    # Five full reads cover source transfer, verification and expiry checks.
    maximum=source.DATA_BYTES+2*1024**3
    storage=Decimal(maximum)/1024**3*decimal(rates[keys[0]])*Decimal(35)/28
    egress=Decimal(source.DATA_BYTES*5)/1024**3*decimal(rates[keys[1]])
    amount=int(((storage+egress+1)*1_000_000).to_integral_value(rounding=ROUND_CEILING))
    require(0<amount<=MAX_RESERVATION,'PREPARATION_BOUND')
    return {'reserved_micro_usd':amount,'rates':{k:str(decimal(rates[k])) for k in keys},
            'maximum_stored_bytes':maximum,'egress_bound_bytes':source.DATA_BYTES*5,
            'retention_days':30,'reserved_storage_days':35,'billing_month_days_floor':28,
            'headroom_micro_usd':1_000_000,'new_provider_compute':False}

def validate(binding):
    fields={'purpose','operation_id','run_id','authority_sha256','team_authority_sha256','source',
            'helper_source','owner_sha256','config_sha256','inventory_sha256','native_asset_id',
            'direct_asset_id','source_volume_id','envelope','created_at','expires_at'}
    require(isinstance(binding,dict) and set(binding)==fields,'BINDING_FIELDS')
    require(binding['purpose']==PURPOSE and binding['operation_id']==source.OPERATION
            and binding['run_id']==RUN and binding['authority_sha256']==AUTHORITY
            and binding['team_authority_sha256']==TEAM_AUTHORITY
            and binding['inventory_sha256']==source.INVENTORY and binding['native_asset_id']==NATIVE_ID
            and binding['direct_asset_id']==DIRECT_ID and binding['source_volume_id']==DIRECT_VOLUME,'FIXED_SCOPE')
    require(all(isinstance(binding[k],str) and re.fullmatch('[0-9a-f]{64}',binding[k]) for k in ('owner_sha256','config_sha256'))
            and all(isinstance(binding[k],str) and re.fullmatch('[0-9a-f]{40}',binding[k]) for k in ('source','helper_source')),'SOURCE_PINS')
    require(binding['envelope']==envelope(binding['envelope']['rates']),'ENVELOPE')
    start=datetime.fromisoformat(binding['created_at']);end=datetime.fromisoformat(binding['expires_at'])
    require(start.tzinfo is not None and end-start==timedelta(days=source.RETENTION_DAYS),'RETENTION')
    return binding

def native_qualification(accounts,binding):
    """Recheck genuine completed native proof and exact retained predecessors."""
    from orchestrator import modal_native_successor as prior,modal_environment_provider as provider,modal_pinned_image as image
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(NATIVE_ID,)).fetchone()
    require(row is not None and row['status']=='READY','NATIVE_REQUIRED')
    native=json.loads(pr.check(NATIVE_STATE/'binding.json').read_bytes())
    require(digest(canonical(native))==NATIVE_ID and row['binding']==canonical(native).decode()
            and row['run']==RUN and row['reserved_micro_usd']==native['envelope']['cost']['reserved_micro_usd'],'NATIVE_BINDING')
    require(binding['source']==native['source'] and binding['owner_sha256']==native['owner_sha256'],'SAME_OWNER')
    image.item4_owner(accounts,native)
    handle=json.loads(pr.check(NATIVE_STATE/'provider/sandbox.json').read_bytes())
    require((NATIVE_STATE/'provider/outcome.json').is_file(),'NATIVE_TERMINAL_REQUIRED')
    original=provider.observe(None,native,handle,NATIVE_STATE/'provider')
    require(original['status']=='VERIFIED' and original['exit_code']==0,'NATIVE_PASS_REQUIRED')
    saved=json.loads(pr.check(NATIVE_STATE/'VERIFIED.json').read_bytes())
    require(json.loads(row['receipt'])==saved and all(saved[k]==v for k,v in original.items()),'NATIVE_RECEIPT')
    return prior.qualify(accounts,native)


SOURCE_PREDECESSOR_ID='450b6795685fe5b1d80986e64836f8f155d7953986cb32a05fd0d0a3266cb7e9'
SOURCE_PREDECESSOR_STATE=Path('/var/lib/research-system-manual-sprint10-deployment/item4-source-preparation-20261009/state')
SOURCE_PREDECESSOR_PROOF=Path(__file__).resolve().parents[1]/'docs/ITEM4_SOURCE_HYDRATION_PREDECESSOR_20261009.json'
SOURCE_PREDECESSOR_SHA='cf117f7f23c0285c1076a7748aaf980d539ed51583837969998f619291bf87d3'

def source_failure_proof():
    raw=pr.check(SOURCE_PREDECESSOR_PROOF).read_bytes()
    require(digest(raw)==SOURCE_PREDECESSOR_SHA,'PREDECESSOR_PROOF_CHANGED')
    value=json.loads(raw)
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    record=SOURCE_PREDECESSOR_STATE.parent
    approved=verify_result(trusted(record/'review'))
    require(approved['verdict']=='APPROVE' and approved['source_sha']==value['installed_source']=='f62f923b999aac56f7ae64826c6bbdc1e15b4669'
            and approved['report_sha256']==value['installed_review']=='a58f8e8a5f532cc624ab313e88df5eaa09972c55bec3da2c7359e1def7377837'
            and approved['change_id']=='item4-source-install-repair-20261009','PREDECESSOR_RELEASE')
    manifest=json.loads(trusted(record/'review/packet-manifest.json').read_bytes())
    root=Path('/opt/research-system/manual-repair-helpers/item4-source-preparation-20261009')
    for name in ('orchestrator/modal_development_inputs.py','orchestrator/modal_source_composition.py','orchestrator/modal_source_budget.py','tools/item4_source_preparation.py','tools/install_item4_source_preparation.py'):
        require(digest(trusted(root/name).read_bytes())==manifest['source_files'][name],'PREDECESSOR_CODE_CHANGED')
    return value

def source_predecessor(accounts,binding):
    # Only the one diagnosed pre-create failure qualifies. Nothing is relabeled,
    # deleted, overwritten or released; the new attempt gets a fresh reservation.
    import subprocess
    from orchestrator.modal_assets import local_files
    value=source_failure_proof();root=SOURCE_PREDECESSOR_STATE
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(SOURCE_PREDECESSOR_ID,)).fetchone()
    require(row is not None and dict(row)==value['asset'] and digest(canonical(dict(row)))==value['asset_sha256']
            and row['status']=='UNCERTAIN' and row['reserved_micro_usd']==3321330,'PREDECESSOR_ROW_CHANGED')
    old=json.loads(row['binding'])
    require(digest(canonical(old))==SOURCE_PREDECESSOR_ID and old['operation_id']=='item4-frozen-base-source-v1'
            and binding['operation_id']=='item4-frozen-base-source-hydrated-v2','FIXED_SOURCE_SUCCESSOR')
    require(all(binding[k]==old[k] for k in ('purpose','run_id','authority_sha256','team_authority_sha256','source','owner_sha256','inventory_sha256','native_asset_id','direct_asset_id','source_volume_id')),'PREDECESSOR_SCOPE_CHANGED')
    props=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show','research-item4-source-preparation.service','-p','ActiveState','-p','MainPID','-p','ExecMainStatus','-p','InvocationID'],text=True).splitlines())
    require(props==value['unit'] and props['ActiveState']=='failed' and props['MainPID']=='0' and props['ExecMainStatus']=='1','PREDECESSOR_NOT_TERMINAL')
    pr.check_tree(root)
    require({p.name for p in root.iterdir() if p.is_dir()}=={'data','incoming'},'PREDECESSOR_UNKNOWN_DIRECTORY')
    require(all(not (root/n).exists() and not (root/n).is_symlink() for n in ('volume-create-intent.json','volume.json','upload-intent.json','VERIFIED.json','LOCAL_VERIFIED.json')),'PREDECESSOR_CREATE_OR_OUTCOME')
    actual={p.name:{'bytes':p.stat().st_size,'sha256':digest(pr.check(p).read_bytes())} for p in root.iterdir() if p.is_file() and p.name not in {'cleanup-status.json','operation.lock'}}
    require(actual==value['records'],'PREDECESSOR_RECORD_CHANGED')
    failure=json.loads(pr.check(root/'FAILED.json').read_bytes())
    require(json.loads(row['receipt'])==failure and failure=={'status':'UNCERTAIN','binding_sha256':SOURCE_PREDECESSOR_ID,'error_type':'AttributeError','no_automatic_retry':True,'reservation_retained':True},'PREDECESSOR_FAILURE')
    metadata=Path('/etc/research-system-manual-sprint10/item4-source-preparation-20261009/inputs')
    files,proof=source.contract(metadata);_,brain,cache,baseline=source.partitions(files)
    require(proof==value['membership'],'PREDECESSOR_FROZEN_MEMBERSHIP')
    local_files(root/'incoming',{**brain,**baseline});local_files(root/'data',{**brain,**cache,**baseline})
    return SOURCE_PREDECESSOR_ID

def reserve(accounts,binding,*,billing_snapshot,now=None):
    """Normal transaction, full original liabilities retained; no provider calls."""
    from orchestrator import modal_environment_budget as shared,modal_terminal_cost
    from orchestrator.modal_direct_budget import selected_asset as download_asset
    from orchestrator.modal_direct_recovery import resolved_failure_ids
    from orchestrator.spending_continuation import closed_ids
    now=now or datetime.now(timezone.utc);validate(binding)
    require(billing_snapshot.get('workspace')=='moroseui' and binding['envelope']==envelope(billing_snapshot['rates']),'BILLING_BINDING')
    ident=digest(canonical(binding));raw=canonical(binding).decode();amount=binding['envelope']['reserved_micro_usd']
    modal_terminal_cost.observe_billing(accounts,billing_snapshot,now)
    db=accounts.db;db.execute('BEGIN IMMEDIATE')
    try:
        require(not (accounts.batch.folder/'HALT').exists(),'HALTED')
        old=db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
        if old:
            require(old['binding']==raw and old['run']==RUN and old['reserved_micro_usd']==amount,'EXISTING_BINDING')
            db.execute('COMMIT');return False
        require(abs((now-datetime.fromisoformat(binding['created_at'])).total_seconds())<=300,'FRESH_ADMISSION')
        owner=db.execute('SELECT * FROM autonomy_runs WHERE id=?',(RUN,)).fetchone()
        require(owner is not None and owner['status']=='ACTIVE','ACTIVE_OWNER')
        closed=closed_ids(accounts.batch,RUN)
        require(all(r['id'] in closed for r in db.execute("SELECT id FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')")),'MODEL_CALL_UNCERTAIN_OR_RUNNING')
        native_failures=native_qualification(accounts,binding)
        previous=source_predecessor(accounts,binding)
        assets=db.execute('SELECT * FROM autonomy_assets').fetchall();compute=db.execute('SELECT * FROM autonomy_compute').fetchall()
        require(not any(json.loads(r['binding']).get('purpose')==PURPOSE and r['id']!=previous for r in assets),'ALREADY_PREPARED_NO_RETRY')
        direct=next((r for r in assets if r['id']==DIRECT_ID),None)
        require(direct is not None and direct['status']=='READY' and download_asset(direct)
                and digest(canonical(json.loads(direct['binding'])))==DIRECT_ID
                and direct['reserved_micro_usd']==json.loads(direct['binding'])['envelope']['cost']['reserved_micro_usd'],'DIRECT_SOURCE_REQUIRED')
        resolved=resolved_failure_ids(accounts,root=accounts.batch.filesystem_root)|native_failures|{previous}
        require(all(r['status']=='READY' or r['id'] in resolved for r in assets),'UNCERTAIN_ASSET')
        stopped=shared.terminal_failed_compute(accounts)
        require(isinstance(stopped,set) and stopped<={r['id'] for r in compute},'STOPPED_SCOPE')
        require(all(r['id'] in stopped or r['status'] in {'COLLECTED','ACCOUNTED'} for r in compute),'ACTIVE_OR_UNCERTAIN_COMPUTE')
        require(all(type(r['reserved_micro_usd']) is int and r['reserved_micro_usd']>=0 for r in [*assets,*compute]),'COST_RECORD')
        runs=shared._item4_runs(db,compute);require(RUN in runs,'ITEM4_OWNER_SCOPE')
        old_assets=sum(r['reserved_micro_usd'] for r in assets if r['run'] in runs or download_asset(r) or shared.selected_asset(r))
        exposure=modal_terminal_cost.exposure(db,compute,billing_snapshot)
        total=old_assets+sum(exposure['run_cost'].get(r,0) for r in runs)
        smoke=old_assets+sum(exposure['smoke_cost'].get(r,0) for r in runs)
        require(total+amount<=TOTAL_CAP and smoke+amount<=SMOKE_CAP,'ITEM4_HARD_COST_CAP')
        require(not exposure['underestimated_apps'],'COST_BOUND_BELOW_BILLING')
        commitments=dict(exposure['commitments']);commitments.update({'asset-reservation:'+r['id']:r['reserved_micro_usd'] for r in assets})
        view=headroom(billing_snapshot,now=now,usage_limit_micro=USAGE_CEILING,spend_limit_micro=SPEND_CEILING,commitments=commitments)
        require(amount<=min(view['usage_headroom_micro'],view['spend_headroom_micro']),'PROVIDER_HEADROOM_WAIT')
        db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'RESERVED',?,NULL)",(ident,RUN,raw,amount))
        event={'kind':'ITEM4_FROZEN_SOURCE_RESERVED','binding_sha256':ident,'micro_usd':amount,
               'prior_item4_smoke_micro_usd':smoke,'prior_item4_total_micro_usd':total,'billing_snapshot':billing_snapshot,
               'headroom':view,'terminal_exposure':exposure,'scientific_calls':0,'new_provider_compute':False,
               'scope':'Private frozen99 source copies; counts in original smoke and total caps; no scientific admission'}
        db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':assets-reserved',RUN,canonical(event).decode()))
        db.execute('COMMIT');return True
    except BaseException:
        db.execute('ROLLBACK');raise
