"""Item4 direct asset preparation in the existing asset ledger and dollar caps.

Administrative CPU download, no scientific-call allowance. It is accounted in
item4's smoke AND total budgets across the preparation and experiment owners.
"""
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
import json
from orchestrator.modal_billing import decimal, headroom
from orchestrator.modal_item4_policy import AUTHORITY, TEAM_AUTHORITY, SMOKE_CAP, TOTAL_CAP, USAGE_CEILING, SPEND_CEILING, quote
from orchestrator.modal_ctp_download import AUTHORITY as DOWNLOAD_AUTHORITY
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest

PURPOSE='M4_ITEM4_DIRECT_INPUTS'
RESOURCES={'gpu':None,'cpu':1,'memory_mib':2048,'timeout_seconds':21600}


def selected_asset(row):
    binding=json.loads(row['binding'])
    return (binding.get('purpose')==PURPOSE and binding.get('authority_sha256')==AUTHORITY
            and binding.get('download_authority_sha256')==DOWNLOAD_AUTHORITY)


def envelope(download_bytes,rates):
    if type(download_bytes) is not int or not 0<download_bytes<=72*1024**3:
        raise ValueError('DIRECT_ASSET_BYTE_BOUND')
    for k in ('volume_storage_gib_month_cost','egress_gib_cost'):
        if k not in rates or decimal(rates[k])<0:raise ValueError('DIRECT_ASSET_RATES')
    # Verified input copies plus bounded partials/package. Reserve thirty days plus five for deletion/billing lag;
    # the existing retention controller must remove only these input copies at
    # expiry. This is neither a checkpoint nor a scientific-result store.
    maximum=download_bytes+2*1024**3+4*1024**2
    storage=Decimal(maximum)/1024**3*decimal(rates['volume_storage_gib_month_cost'])*Decimal(35)/28
    receipts=Decimal(4)/1024*decimal(rates['egress_gib_cost'])
    overhead=int(((storage+receipts+1)*1000000).to_integral_value(rounding=ROUND_CEILING))
    cost=quote(RESOURCES,rates,overhead)
    return {'cost':cost,'resources':RESOURCES,'download_bytes':download_bytes,'maximum_stored_bytes':maximum,
            'retention_days':30,'reserved_storage_days':35,'billing_month_days_floor':28,
            'storage_micro_usd':int((storage*1000000).to_integral_value(rounding=ROUND_CEILING)),
            'registry_headroom_micro_usd':1000000,'receipt_egress_bound_bytes':4*1024**2}


def reserve(accounts,ident,run,binding,*,billing_snapshot,now=None,recovery=None):
    now=now or datetime.now(timezone.utc)
    expected=envelope(binding.get('download_bytes'),billing_snapshot['rates'])
    if (binding.get('purpose')!=PURPOSE or binding.get('authority_sha256')!=AUTHORITY or
            binding.get('download_authority_sha256')!=DOWNLOAD_AUTHORITY or
            binding.get('team_authority_sha256')!=TEAM_AUTHORITY or binding.get('run_id')!=run or
            binding.get('envelope')!=expected or digest(canonical(binding))!=ident):
        raise ValueError('DIRECT_ASSET_BINDING')
    db=accounts.db;raw=canonical(binding).decode();amount=expected['cost']['reserved_micro_usd']
    db.execute('BEGIN IMMEDIATE')
    try:
        if (accounts.batch.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
        old=db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
        if old:
            if old['binding']!=raw or old['run']!=run:raise ValueError('DIRECT_ASSET_EXISTING_BINDING')
            db.execute('COMMIT');return False
        owner=db.execute('SELECT * FROM autonomy_runs WHERE id=?',(run,)).fetchone()
        if owner is None or owner['status']!='ACTIVE':raise ValueError('BATCH_ACTIVE_RUN_REQUIRED')
        selected=json.loads(owner['binding'])
        if selected.get('purpose')!=PURPOSE or selected.get('authority_sha256')!=AUTHORITY:
            raise ValueError('DIRECT_ASSET_OWNER_REQUIRED')
        from orchestrator.completed_run import closed_ids
        closed=closed_ids(accounts.batch,run,root=accounts.batch.filesystem_root)
        pending=db.execute("SELECT * FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')").fetchall()
        if any(x['id'] not in closed for x in pending):raise ValueError('BATCH_UNCERTAIN_OR_RUNNING_CALL')
        predecessor_ids=set()
        if recovery is not None:
            from orchestrator import modal_direct_recovery as linked
            proof=linked.parent(accounts,recovery,root=accounts.batch.filesystem_root)
            linked.check_child(binding,proof)
            predecessor_ids=proof.get('ancestor_ids',{linked.PARENT})
        elif 'recovery' in binding:raise ValueError('DIRECT_RECOVERY_SELECTION_REQUIRED')
        assets=db.execute('SELECT * FROM autonomy_assets').fetchall()
        compute=db.execute('SELECT * FROM autonomy_compute').fetchall()
        if any(x['status']!='READY' and x['id'] not in predecessor_ids for x in assets):raise ValueError('MODAL_UNCERTAIN_ASSET_PREPARATION')
        if any(x['status'] not in ('COLLECTED','ACCOUNTED') for x in compute):raise ValueError('MODAL_ACTIVE_OR_UNCERTAIN_COMPUTE')
        if any(selected_asset(x) and x['id'] not in predecessor_ids for x in assets):raise ValueError('DIRECT_ASSET_ALREADY_PREPARED_NO_NEW_RESERVATION')
        item_compute=[x for x in compute if json.loads(x['binding']).get('experiment',{}).get('authority_sha256')==AUTHORITY]
        from orchestrator.modal_environment_budget import selected_asset as environment_asset
        old_assets=sum(x['reserved_micro_usd'] for x in assets if selected_asset(x) or environment_asset(x))
        total=old_assets+sum(max(x['reserved_micro_usd'],x['actual_micro_usd'] or 0) for x in item_compute)
        smoke=old_assets+sum(max(x['reserved_micro_usd'],x['actual_micro_usd'] or 0) for x in item_compute if json.loads(x['binding'])['experiment']['stage']=='SMOKE')
        if total+amount>TOTAL_CAP or smoke+amount>SMOKE_CAP:raise ValueError('ITEM4_HARD_COST_CAP')
        commitments={'asset-reservation:'+x['id']:x['reserved_micro_usd'] for x in assets}
        commitments.update({'compute-reservation:'+x['id']:max(x['reserved_micro_usd'],x['actual_micro_usd'] or 0) for x in compute})
        view=headroom(billing_snapshot,now=now,usage_limit_micro=USAGE_CEILING,spend_limit_micro=SPEND_CEILING,commitments=commitments)
        if amount>min(view['usage_headroom_micro'],view['spend_headroom_micro']):raise ValueError('ITEM4_PROVIDER_HEADROOM_WAIT')
        db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'RESERVED',?,NULL)",(ident,run,raw,amount))
        event={'kind':'ITEM4_DIRECT_ASSET_RESERVED','binding_sha256':ident,'micro_usd':amount,
               'billing_snapshot':billing_snapshot,'headroom':view,'scientific_calls':0,
               'scope':'Counts in item4 smoke and total caps; no experiment or scientific admission'}
        db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':assets-reserved',run,canonical(event).decode()))
        db.execute('COMMIT');return True
    except BaseException:
        db.execute('ROLLBACK');raise
