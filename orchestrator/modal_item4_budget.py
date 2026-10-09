"""Item4's explicitly selected budget in the existing compute ledger.

Legacy M3 reservations and limits are unchanged. Multiple fits may be reserved,
but a fit with an unresolved segment cannot be launched again. No function here
starts a provider job, infers a stopped job, or releases an old charge.
"""
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
import hashlib
import json
import re
from orchestrator.modal_billing import decimal, headroom

from orchestrator.modal_item4_policy import (AUTHORITY, TEAM_AUTHORITY, SMOKE_CAP, PROJECTION_LIMIT, TOTAL_CAP, CONCURRENCY, USAGE_CEILING, SPEND_CEILING, GPU_KEYS, quote)



def reserve(accounts, ident, run, binding, *, billing_snapshot, now=None):
    """Reserve atomically on ComputeAccounts' existing owner connection.

    A later segment needs the preceding terminal/checkpoint receipt and the
    same scientific identity. Observation timeout is never a terminal proof.
    """
    now = now or datetime.now(timezone.utc)
    raw = json.dumps(binding, sort_keys=True)
    if hashlib.sha256(raw.encode()).hexdigest() != ident:
        raise ValueError('ITEM4_RESERVATION_ID')
    scope = binding.get('experiment')
    if not isinstance(scope, dict) or set(scope) != {
        'backlog_item','authority_sha256','team_authority_sha256','fit_id','stage','segment','billing_object_id'}:
        raise ValueError('ITEM4_SCOPE_FIELDS')
    if (scope['backlog_item'] != 4 or scope['authority_sha256'] != AUTHORITY or
            scope['team_authority_sha256'] != TEAM_AUTHORITY or scope['stage'] not in {'SMOKE','FULL'} or
            type(scope['segment']) is not int or scope['segment'] < 1 or
            not isinstance(scope['fit_id'],str) or not re.fullmatch('[a-zA-Z0-9_-]{1,96}',scope['fit_id']) or
            not isinstance(scope['billing_object_id'],str) or not re.fullmatch('ap-[a-zA-Z0-9]+',scope['billing_object_id'])):
        raise ValueError('ITEM4_SCOPE_OR_CONTINUATION_REQUIRED')
    expected = quote(binding['resources'], billing_snapshot['rates'], binding['overhead_micro_usd'])
    if binding.get('cost') != expected or binding.get('run_id') != run:
        raise ValueError('ITEM4_COST_OR_RUN_BINDING')
    amount = expected['reserved_micro_usd']
    from orchestrator import modal_terminal_cost
    modal_terminal_cost.observe_billing(accounts,billing_snapshot,now)
    db = accounts.db
    db.execute('BEGIN IMMEDIATE')
    try:
        if (accounts.batch.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
        existing = db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
        if existing:
            if existing['binding'] != raw or existing['run'] != run:raise ValueError('ITEM4_RESERVATION_CHANGED')
            db.execute('COMMIT');return False
        active = db.execute('SELECT * FROM autonomy_runs WHERE id=?',(run,)).fetchone()
        if not active or active['status'] != 'ACTIVE':raise ValueError('BATCH_ACTIVE_RUN_REQUIRED')
        from orchestrator.experiment_owner import verify_item4
        verify_item4(accounts.batch, run, json.loads(active['binding']), binding)
        pending = db.execute("SELECT * FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')").fetchall()
        # Reuse scientific admission's exact operator-completed-run proof. This
        # closes only the sealed run's retained terminal rows, without editing
        # a row, releasing a charge or admitting an unrelated uncertain call.
        from orchestrator.spending_continuation import closed_ids
        closed = closed_ids(accounts.batch, run)
        if any(row['id'] not in closed for row in pending):
            raise ValueError('BATCH_UNCERTAIN_OR_RUNNING_CALL')
        rows = db.execute('SELECT * FROM autonomy_compute').fetchall()
        assets = db.execute('SELECT * FROM autonomy_assets').fetchall()
        from orchestrator.modal_direct_recovery import resolved_failure_ids
        resolved = resolved_failure_ids(accounts, root=accounts.batch.filesystem_root)
        from orchestrator.item4_validation_admission import retained_terminal
        terminal_assets,terminal_compute=retained_terminal(accounts,binding)
        resolved |= terminal_assets
        if any(row['status'] != 'READY' and row['id'] not in resolved for row in assets):
            raise ValueError('MODAL_UNCERTAIN_ASSET_PREPARATION')
        if any(row['status'] == 'UNCERTAIN' and row['id'] not in terminal_compute for row in rows):raise ValueError('MODAL_UNCERTAIN_COMPUTE')
        concurrent = 0; predecessors = []
        for row in rows:
            data = json.loads(row['binding']); other = data.get('experiment')
            if row['status'] not in {'COLLECTED','ACCOUNTED'} and row['id'] not in terminal_compute:
                if not other or row['run'] != run:raise ValueError('ITEM4_OTHER_EXECUTION_ACTIVE')
                if data['resources']['gpu'] is not None:concurrent += 1
            if other:
                if other['billing_object_id'] == scope['billing_object_id'] and (
                        row['run'] != run or other['fit_id'] != scope['fit_id']):
                    raise ValueError('ITEM4_BILLING_OBJECT_SHARED')
                if row['run'] == run:
                    if other['fit_id'] == scope['fit_id']:
                        predecessors.append((row, data))
        if scope['segment'] == 1:
            if 'fresh_start' in binding:
                if 'preprocessing' in binding:
                    from orchestrator.item4_preprocessing_fresh_start import validate_reservation
                else:
                    from orchestrator.item4_fit_transport_recovery import validate_reservation
                validate_reservation(accounts,predecessors,binding)
            elif predecessors:raise ValueError('ITEM4_FIT_ALREADY_EXISTS_NO_RESTART')
            if 'resume' in binding:raise ValueError('ITEM4_INITIAL_HAS_RESUME_BINDING')
        else:
            if 'preprocessing' in binding and 'fresh_start' in binding:
                from orchestrator.item4_checkpoint_connection import predecessors as checkpoint_predecessors
                predecessors = checkpoint_predecessors(accounts,predecessors,binding)
            if len(predecessors) != scope['segment'] - 1:
                raise ValueError('ITEM4_CONTIGUOUS_SEGMENTS_REQUIRED')
            previous = max(predecessors,key=lambda pair:pair[1]['experiment']['segment'])
            old, data = previous
            if sorted(d['experiment']['segment'] for _,d in predecessors) != list(range(1,scope['segment'])):
                raise ValueError('ITEM4_CONTIGUOUS_SEGMENTS_REQUIRED')
            if 'preprocessing' in binding:
                from orchestrator.preprocessing_recovery import validate_reservation
                validate_reservation(db,old,data,binding)
            else:
                if old['status'] != 'ACCOUNTED':raise ValueError('ITEM4_RESUME_TERMINAL_PROOF_REQUIRED')
                terminal = db.execute('SELECT payload FROM events WHERE id=?',(old['id']+':fit-interruption',)).fetchone()
                if terminal is None:raise ValueError('ITEM4_RESUME_TERMINAL_PROOF_REQUIRED')
                saved = json.loads(terminal['payload'])
                proof = saved['proof']
                expected_resume = {'previous_segment_id':old['id'],
                                   'terminal_receipt_sha256':hashlib.sha256(terminal['payload'].encode()).hexdigest(),
                                   'checkpoint_record_sha256':proof['checkpoint_record_sha256']}
                if binding.get('resume') != expected_resume:
                    raise ValueError('ITEM4_RESUME_BINDING')
                if (binding.get('progress') != data.get('progress') or
                        binding.get('spec_sha256') != data.get('spec_sha256') or
                        binding.get('code_sha256') != data.get('code_sha256') or
                        scope['billing_object_id'] != data['experiment']['billing_object_id'] or
                        scope['stage'] != data['experiment']['stage']):
                    raise ValueError('ITEM4_RESUME_SCIENTIFIC_IDENTITY_CHANGED')
                if saved.get('resume_reason') not in {'PROVIDER_LIMIT','LIFETIME_TIMEOUT','DELIBERATE_SMOKE_INTERRUPTION','OBSERVED_TRAINING_STALL'}:
                    raise ValueError('ITEM4_INTERRUPTION_NEEDS_DIAGNOSIS')
        if concurrent + int(binding['resources']['gpu'] is not None) > CONCURRENCY:
            raise ValueError('ITEM4_GPU_CONCURRENCY_LIMIT')
        from orchestrator.modal_direct_budget import selected_asset
        from orchestrator.modal_environment_budget import selected_asset as environment_asset
        from orchestrator.item4_closed_asset_billing import effective as asset_effective
        asset_amounts = {row['id']:asset_effective(accounts,row,billing_snapshot,now) for row in assets}
        asset_total = sum(asset_amounts[row['id']] for row in assets
                          if row['run']==run or selected_asset(row) or environment_asset(row))
        exposure = modal_terminal_cost.exposure(db,rows,billing_snapshot)
        commitments = exposure['commitments']
        total = asset_total + exposure['run_cost'].get(run,0)
        smoke = asset_total + exposure['smoke_cost'].get(run,0)
        from orchestrator import item4_stage1_cap
        smoke_cap = item4_stage1_cap.limit(binding)
        if total + amount > TOTAL_CAP or (scope['stage']=='SMOKE' and smoke + amount > smoke_cap):
            raise ValueError('ITEM4_HARD_COST_CAP')
        if exposure['underestimated_apps']:
            raise ValueError('ITEM4_COST_BOUND_BELOW_BILLING')
        full_admission=None
        if scope['stage']=='FULL':
            from orchestrator.experiment_full_admission import verify_reservation
            full_admission=verify_reservation(accounts,run,binding,billing_snapshot)
        for row in assets:
            commitments['asset-reservation:'+row['id']] = asset_amounts[row['id']]
        view = headroom(billing_snapshot, now=now,usage_limit_micro=USAGE_CEILING,
                        spend_limit_micro=SPEND_CEILING, commitments=commitments)
        if amount > min(view['usage_headroom_micro'],view['spend_headroom_micro']):
            raise ValueError('ITEM4_PROVIDER_HEADROOM_WAIT')
        db.execute("INSERT INTO autonomy_compute VALUES(?,?,?,'RESERVED',?,NULL,NULL,?)",
                   (ident,run,raw,amount,now.strftime('%Y-%m')))
        payload = {'kind':'ITEM4_COST_RESERVED','binding_sha256':ident,'micro_usd':amount,
                   'billing_snapshot':billing_snapshot,'headroom':view,
                   'caps':{'smoke':smoke_cap,'projection':PROJECTION_LIMIT,'total':TOTAL_CAP},
                   'stage1_operator_sha256':item4_stage1_cap.OPERATOR_SHA if smoke_cap>SMOKE_CAP else None,
                   'authority_sha256':AUTHORITY,'team_authority_sha256':TEAM_AUTHORITY,
                   'terminal_exposure':exposure}
        if full_admission is not None:payload['full_admission']=full_admission
        db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':gpu-reserved',run,json.dumps(payload,sort_keys=True)))
        db.execute('COMMIT');return True
    except BaseException:
        db.execute('ROLLBACK');raise


def record_interruption(accounts, ident, provider, *, reason_record, expected_checkpoint_sha256=None):
    """Preserve a positive terminal checkpoint; retain the entire prior charge.

    reason_record is the existing controller's private provider-limit, lifetime,
    or deliberate-smoke-stop receipt. A generic exit code is not classified here.
    UNKNOWN remains diagnosis-only and cannot qualify a resumed segment.
    """
    from pathlib import Path
    from orchestrator import private_records
    if expected_checkpoint_sha256 is not None and (not isinstance(expected_checkpoint_sha256,str) or
            re.fullmatch('[0-9a-f]{64}',expected_checkpoint_sha256) is None):
        raise ValueError('ITEM4_INTERRUPTION_CHECKPOINT_PIN')
    row = accounts.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
    if row is None:raise ValueError('ITEM4_SEGMENT_MISSING')
    old = accounts.db.execute('SELECT payload FROM events WHERE id=?',(ident+':fit-interruption',)).fetchone()
    if old:
        saved = json.loads(old['payload'])
        if row['status'] != 'ACCOUNTED':raise ValueError('ITEM4_INTERRUPTION_RECONCILIATION')
        path = private_records.check(reason_record)
        if hashlib.sha256(path.read_bytes()).hexdigest() != saved['reason_record_sha256']:
            raise ValueError('ITEM4_INTERRUPTION_REASON_CHANGED')
        if expected_checkpoint_sha256 is not None and saved['proof']['checkpoint_record_sha256']!=expected_checkpoint_sha256:
            raise ValueError('ITEM4_INTERRUPTION_CHECKPOINT_CHANGED')
        return saved
    if row['status'] not in {'RUNNING','UNCERTAIN'} or not row['provider_id']:
        raise ValueError('ITEM4_NO_KNOWN_EXECUTION_TO_RECONCILE')
    binding = json.loads(row['binding'])
    if binding.get('experiment',{}).get('authority_sha256') != AUTHORITY:
        raise ValueError('ITEM4_INTERRUPTION_SCOPE')
    path = private_records.check(reason_record);raw = path.read_bytes();reason = json.loads(raw)
    if (not isinstance(reason,dict) or set(reason) != {'schema','segment_id','provider_id','reason','evidence'} or
            reason['schema']!='modal-interruption-cause/v1' or reason['segment_id']!=ident or
            reason['provider_id']!=row['provider_id'] or
            reason['reason'] not in {'PROVIDER_LIMIT','LIFETIME_TIMEOUT','DELIBERATE_SMOKE_INTERRUPTION','OBSERVED_TRAINING_STALL'} or
            not isinstance(reason['evidence'],dict) or not reason['evidence']):
        raise ValueError('ITEM4_INTERRUPTION_REASON_BINDING')
    proof = provider.terminal_fit_checkpoint(row['provider_id'],binding)
    if (proof.get('schema')!='modal-fit-terminal-proof/v1' or proof.get('provider_id')!=row['provider_id'] or
            proof.get('binding_sha256')!=ident or proof.get('fit_id')!=binding['experiment']['fit_id'] or
            type(proof.get('terminal_exit_code')) is not int or proof.get('may_launch') is not False):
        raise ValueError('ITEM4_INTERRUPTION_PROVIDER_PROOF')
    if expected_checkpoint_sha256 is not None and proof['checkpoint_record_sha256']!=expected_checkpoint_sha256:
        raise ValueError('ITEM4_INTERRUPTION_CHECKPOINT_CHANGED')
    result = {'kind':'FIT_INTERRUPTED_WITH_COMMITTED_CHECKPOINT','proof':proof,
              'resume_reason':reason['reason'],'reason_record_sha256':hashlib.sha256(raw).hexdigest(),
              'prior_status':row['status'],'prior_reserved_micro_usd':row['reserved_micro_usd'],
              'charge_disposition':'full reservation retained; ACCOUNTED describes cost, not scientific completion'}
    encoded = json.dumps(result,sort_keys=True)
    accounts.db.execute('BEGIN IMMEDIATE')
    try:
        current = accounts.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
        if dict(current)!=dict(row):raise ValueError('ITEM4_SEGMENT_CHANGED_DURING_OBSERVATION')
        accounts.db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':fit-interruption',row['run'],encoded))
        accounts.db.execute("UPDATE autonomy_compute SET status='ACCOUNTED' WHERE id=?",(ident,))
        accounts.db.execute('COMMIT')
    except BaseException:
        accounts.db.execute('ROLLBACK');raise
    return result
