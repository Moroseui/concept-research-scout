"""One item6 CPU cost owner, ordinary ledger and conservative retained charges."""
import json
from datetime import datetime,timezone
from orchestrator import diagnostics_policy as policy
from orchestrator.diagnostics_contract import PURPOSE,require,sha,encoded
from orchestrator.modal_item4_policy import quote,USAGE_CEILING,SPEND_CEILING
from orchestrator.modal_billing import headroom


def reserve(accounts,ident,run,binding,*,billing_snapshot,now=None):
    now=now or datetime.now(timezone.utc)
    require(run==policy.RUN_ID and binding['run_id']==run and binding.get('purpose')==PURPOSE and binding.get('authority_sha256')==policy.authority(),'DIAGNOSTICS_BUDGET_SCOPE')
    require(binding['resources'].get('gpu') is None,'DIAGNOSTICS_CPU_ONLY')
    expected=quote(binding['resources'],billing_snapshot['rates'],binding['overhead_micro_usd'])
    raw=encoded(binding).decode();require(sha(raw.encode())==ident and binding['cost']==expected,'DIAGNOSTICS_COST_BINDING')
    amount=expected['reserved_micro_usd'];db=accounts.db;db.execute('BEGIN IMMEDIATE')
    try:
        if (accounts.batch.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
        old=db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
        if old:
            require(old['run']==run and old['binding']==raw,'DIAGNOSTICS_EXISTING_BINDING_CHANGED')
            db.execute('COMMIT');return False
        owner=db.execute('SELECT * FROM autonomy_runs WHERE id=?',(run,)).fetchone()
        require(owner is not None and owner['status']=='ACTIVE','BATCH_ACTIVE_RUN_REQUIRED')
        own=json.loads(owner['binding']);scope=own.get('execution_scope',{})
        from orchestrator.spending_continuation import lane
        continued=lane(accounts.batch,run,own,binding['source'])
        selected_source=continued[1]['source'] if continued else own.get('source')
        require(sha(encoded(own))==binding['owner_sha256'] and selected_source==binding['source'] and scope.get('run_id')==run and scope.get('item_number')==6 and scope.get('authority_sha256')==policy.AUTHORITY and scope.get('plan_sha256')==binding['execution_plan_sha256'],'DIAGNOSTICS_OWNER_BINDING')
        from orchestrator.spending_continuation import closed_ids
        closed=closed_ids(accounts.batch,run)
        require(not any(row['id'] not in closed for row in db.execute("SELECT * FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')")),'BATCH_UNCERTAIN_OR_RUNNING_CALL')
        rows=db.execute('SELECT * FROM autonomy_compute').fetchall();assets=db.execute('SELECT * FROM autonomy_assets').fetchall()
        from orchestrator.modal_direct_recovery import resolved_failure_ids
        resolved=resolved_failure_ids(accounts,root=accounts.batch.filesystem_root)
        require(not any(row['status']!='READY' and row['id'] not in resolved for row in assets),'MODAL_UNCERTAIN_ASSET_PREPARATION')
        require(not any(row['status']=='UNCERTAIN' for row in rows),'MODAL_UNCERTAIN_COMPUTE')
        require(not any(row['run']==run for row in rows),'DIAGNOSTICS_ALREADY_SUBMITTED_NO_RESTART')
        require(not any(row['status'] not in {'COLLECTED','ACCOUNTED'} and json.loads(row['binding']).get('purpose')!='M4_ITEM4' for row in rows),'DIAGNOSTICS_OTHER_EXECUTION_ACTIVE')
        run_assets=sum(row['reserved_micro_usd'] for row in assets if row['run']==run)
        require(run_assets+amount<=policy.TOTAL_MICRO_USD,'DIAGNOSTICS_HARD_COST_CAP')
        commitments={'compute:'+row['id']:max(row['reserved_micro_usd'],row['actual_micro_usd'] or 0) for row in rows}
        commitments.update({'asset:'+row['id']:row['reserved_micro_usd'] for row in assets})
        view=headroom(billing_snapshot,now=now,usage_limit_micro=USAGE_CEILING,spend_limit_micro=SPEND_CEILING,commitments=commitments)
        require(amount<=min(view['usage_headroom_micro'],view['spend_headroom_micro']),'DIAGNOSTICS_PROVIDER_HEADROOM_WAIT')
        db.execute("INSERT INTO autonomy_compute VALUES(?,?,?,'RESERVED',?,NULL,NULL,?)",(ident,run,raw,amount,now.strftime('%Y-%m')))
        db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':cpu-reserved',run,encoded({'kind':'DIAGNOSTICS_CPU_COST_RESERVED','micro_usd':amount,'authority_sha256':policy.AUTHORITY,'billing_snapshot':billing_snapshot,'headroom':view,'cap_micro_usd':policy.TOTAL_MICRO_USD}).decode()))
        db.execute('COMMIT');return True
    except BaseException:db.execute('ROLLBACK');raise
