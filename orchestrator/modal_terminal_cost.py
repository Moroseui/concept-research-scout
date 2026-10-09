"""Conservative terminal exposure, not a refund or final provider invoice.

Original reservations and actual charges are immutable. A durable same-boot
window encloses provider creation through positive termination. Unknown or old
UTC-only receipts keep their full reservation. App billing is a lifetime floor,
counted once across continuation segments and preserved per billing cycle.
"""
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import json
import re
import time
from orchestrator import private_records as pr
from orchestrator.modal_billing import canonical, decimal, headroom, micros
from orchestrator.modal_item4_policy import quote, USAGE_CEILING, SPEND_CEILING
from orchestrator.manual_executor import digest
from orchestrator.review_contract import strict_json


def clock():
    return {'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'boottime_ns':time.clock_gettime_ns(time.CLOCK_BOOTTIME),
            'observed_at':datetime.now(timezone.utc).isoformat()}


def _stamp(value):
    if (not isinstance(value,dict) or set(value)!={'boot_id','boottime_ns','observed_at'}
            or not isinstance(value['boot_id'],str)
            or not re.fullmatch('[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}',value['boot_id'])
            or type(value['boottime_ns']) is not int or value['boottime_ns']<0):
        raise ValueError('ITEM4_EXPOSURE_CLOCK')
    instant=datetime.fromisoformat(value['observed_at'])
    if instant.tzinfo is None:raise ValueError('ITEM4_EXPOSURE_CLOCK')
    return value


def _seconds(start,end):
    _stamp(start);_stamp(end)
    if start['boot_id']!=end['boot_id']:return None
    delta=end['boottime_ns']-start['boottime_ns']
    if delta<0:raise ValueError('ITEM4_EXPOSURE_CLOCK_REVERSED')
    return max(1,(delta+999_999_999)//1_000_000_000)


def _evidence(db,row,work):
    binding=strict_json(row['binding']);ident=row['id'];work=Path(work)
    if (digest(json.dumps(binding,sort_keys=True).encode())!=ident
            or binding.get('purpose')!='M4_ITEM4' or binding.get('run_id')!=row['run']
            or row['status'] not in {'COLLECTED','ACCOUNTED'} or not row['provider_id']):
        raise ValueError('ITEM4_EXPOSURE_TERMINAL_BINDING')
    refs={}
    def original(name):
        path=pr.check(work/name);raw=path.read_bytes()
        refs[name]={'path':str(path),'sha256':digest(raw)}
        return strict_json(raw)
    intent=original('create-intent.json');created=original('created.json')
    if (intent.get('binding_sha256')!=ident or intent.get('run_id')!=row['run']
            or created.get('binding_sha256')!=ident or created.get('provider_id')!=row['provider_id']):
        raise ValueError('ITEM4_EXPOSURE_CREATION_BINDING')
    if row['status']=='COLLECTED':
        stopped=original('terminated.json');collected=original('collection-receipt.json')
        if (stopped.get('provider_id')!=row['provider_id'] or stopped.get('terminated') is not True
                or collected.get('binding_sha256')!=ident):
            raise ValueError('ITEM4_EXPOSURE_TERMINATION_REQUIRED')
        key=ident+':gpu-collected'
        event=db.execute('SELECT job,payload FROM events WHERE id=?',(key,)).fetchone()
        if event is None or strict_json(event['payload'])!={'status':'COLLECTED','provider_id':row['provider_id']}:
            raise ValueError('ITEM4_EXPOSURE_TERMINATION_REQUIRED')
    else:
        key=ident+(':preprocessing-interruption' if 'preprocessing' in binding else ':fit-interruption')
        event=db.execute('SELECT job,payload FROM events WHERE id=?',(key,)).fetchone()
        saved=strict_json(event['payload']) if event else {};proof=saved.get('proof',{})
        if (saved.get('prior_reserved_micro_usd')!=row['reserved_micro_usd']
                or proof.get('binding_sha256')!=ident or proof.get('provider_id')!=row['provider_id']
                or type(proof.get('terminal_exit_code')) is not int or proof.get('may_launch') is not False):
            raise ValueError('ITEM4_EXPOSURE_TERMINATION_REQUIRED')
        if 'preprocessing' in binding:
            from orchestrator.preprocessing_recovery import validate_proof
            validate_proof(binding,row['provider_id'],proof)
        elif (proof.get('schema')!='modal-fit-terminal-proof/v1'
                or proof.get('fit_id')!=binding['experiment']['fit_id']
                or saved.get('kind')!='FIT_INTERRUPTED_WITH_COMMITTED_CHECKPOINT'):
            raise ValueError('ITEM4_EXPOSURE_TERMINATION_REQUIRED')
    if event['job']!=row['run']:raise ValueError('ITEM4_EXPOSURE_TERMINATION_REQUIRED')
    return {'files':refs,'terminal_event':{'id':key,'sha256':digest(event['payload'].encode())},
            'start':intent.get('cost_clock'),'provider_id':row['provider_id'],
            'binding_sha256':ident,'original_reserved_micro_usd':row['reserved_micro_usd']}


def _record(evidence,work,end):
    seconds=_seconds(evidence['start'],end)
    if seconds is None:return None
    return {'schema':'item4-terminal-exposure/v1','evidence':evidence,'work':str(work),
            'end':end,'elapsed_upper_seconds':seconds,
            'basis':'same-boot BOOTTIME encloses creation through authenticated terminal observation',
            'actual_bill':False,'reservation_or_charge_changed':False}


def record(accounts,ident,work):
    """Append once, as the ledger owner. No provider call or new admission."""
    db=accounts.db;row=db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
    if row is None:raise ValueError('ITEM4_EXPOSURE_ROW_REQUIRED')
    # This fixed pre-science stop has no checkpoint and earns no exposure credit.
    # Requalify its independent authority and every original proof; keep the full
    # reservation. Missing/foreign/changed proofs still refuse, never fall back.
    if db.execute('SELECT 1 FROM events WHERE id=?',(ident+':pre-science-stop',)).fetchone():
        from orchestrator import item4_preprocessing_fresh_start as fresh
        p=fresh.contract()
        if ident!=p['old_row']['id']:
            from orchestrator.item4_private_staging_retry import terminal_contract
            p=terminal_contract(accounts,ident)
        fresh.require(ident==p['old_row']['id'],'COST_ORIGINAL_IDENTITY')
        fresh.retained(db,p)
        intent=Path(work)/'create-intent.json'
        fresh.require(str(intent) in p['evidence_files'] and not db.execute(
            'SELECT 1 FROM events WHERE id=?',(ident+':terminal-exposure',)).fetchone(),'COST_WORK_OR_EXPOSURE')
        for name,pin in p['evidence_files'].items():
            fresh.require(fresh.sha(pr.check(name).read_bytes())==pin,'COST_ORIGINAL_RECEIPT_CHANGED')
        return None
    key=ident+':terminal-exposure'
    old=db.execute('SELECT payload FROM events WHERE id=?',(key,)).fetchone()
    if old:
        saved=strict_json(old['payload'])
        if _record(_evidence(db,row,work),work,saved['end'])!=saved:
            raise ValueError('ITEM4_EXPOSURE_RECORD_CHANGED')
        return saved
    # Older executions have no trustworthy monotonic start. Never backfill one.
    intent=Path(work)/'create-intent.json'
    if not intent.exists():return None
    if 'cost_clock' not in strict_json(pr.check(intent).read_bytes()):return None
    evidence=_evidence(db,row,work);saved=_record(evidence,work,clock())
    if saved is None:return None
    db.execute('BEGIN IMMEDIATE')
    try:
        current=db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
        if dict(current)!=dict(row) or _evidence(db,current,work)!=evidence:
            raise ValueError('ITEM4_EXPOSURE_OBSERVATION_CHANGED')
        db.execute('INSERT INTO events VALUES(?,?,?)',(key,row['run'],json.dumps(saved,sort_keys=True)))
        db.execute('COMMIT')
    except BaseException:db.execute('ROLLBACK');raise
    return saved


def effective(db,row,rates,*,snapshot=None):
    from orchestrator.item4_closed_attempt_billing import effective as closed_billing
    reconciled=closed_billing(db,row,snapshot)
    if reconciled is not None:return max(reconciled,row['actual_micro_usd'] or 0)
    old=db.execute('SELECT job,payload FROM events WHERE id=?',(row['id']+':terminal-exposure',)).fetchone()
    if old is None:return max(row['reserved_micro_usd'],row['actual_micro_usd'] or 0)
    saved=strict_json(old['payload']);binding=strict_json(row['binding'])
    if old['job']!=row['run'] or _record(_evidence(db,row,saved['work']),saved['work'],saved['end'])!=saved:
        raise ValueError('ITEM4_EXPOSURE_RECORD_CHANGED')
    seconds=min(binding['resources']['timeout_seconds'],saved['elapsed_upper_seconds'])
    # Never take advantage of a later cheaper price. Observed billed excess is
    # applied again at app level, since hourly provider reporting may lag.
    prices={k:str(max(decimal(v),decimal(rates.get(k,v)))) for k,v in binding['cost']['rates'].items()}
    bound=quote({**binding['resources'],'timeout_seconds':seconds},prices,binding['overhead_micro_usd'])
    return max(bound['reserved_micro_usd'],row['actual_micro_usd'] or 0)


def _totals(snapshot):
    totals={}
    for row in snapshot['rows']:
        key=row['object_id'];totals[key]=totals.get(key,Decimal(0))+decimal(row['cost'])
    return {key:micros(value) for key,value in totals.items()}


def highwater(db):
    values={}
    for row in db.execute("SELECT id,payload FROM events WHERE id LIKE 'item4-billing:%'"):
        value=strict_json(row['payload']);snapshot=value['snapshot'];body=dict(snapshot);pin=body.pop('sha256',None)
        if (row['id']!='item4-billing:'+digest(row['payload'].encode()) or pin!=digest(canonical(body)) or value.get('schema')!='item4-billing-highwater/v1'
                or value['cycle']!=datetime.fromisoformat(snapshot['observed_at']).strftime('%Y-%m')
                or _totals(snapshot).get(value['object_id'])!=value['micro_usd']):
            raise ValueError('ITEM4_BILLING_HIGHWATER_CHANGED')
        key=(value['object_id'],value['cycle']);values[key]=max(values.get(key,0),value['micro_usd'])
    return values


def observe_billing(accounts,snapshot,now):
    """Preserve billed excess even if the following reservation refuses.

    This records provider observation only; it changes no call/job/charge row.
    """
    headroom(snapshot,now=now,usage_limit_micro=USAGE_CEILING,spend_limit_micro=SPEND_CEILING,commitments={})
    db=accounts.db;db.execute('BEGIN IMMEDIATE')
    try:
        objects={}
        for row in db.execute('SELECT run,binding FROM autonomy_compute'):
            scope=strict_json(row['binding']).get('experiment')
            if scope:objects[scope['billing_object_id']]=row['run']
        seen=highwater(db);cycle=now.strftime('%Y-%m')
        for key,amount in _totals(snapshot).items():
            if key not in objects or amount<=seen.get((key,cycle),0):continue
            value={'schema':'item4-billing-highwater/v1','object_id':key,'cycle':cycle,
                   'micro_usd':amount,'snapshot':snapshot}
            raw=json.dumps(value,sort_keys=True)
            db.execute('INSERT INTO events VALUES(?,?,?)',('item4-billing:'+digest(raw.encode()),objects[key],raw))
        db.execute('COMMIT')
    except BaseException:db.execute('ROLLBACK');raise


def exposure(db,rows,snapshot):
    groups={};by_run={};smoke={};commitments={};proofs={}
    for row in rows:
        binding=strict_json(row['binding']);scope=binding.get('experiment')
        cost=effective(db,row,snapshot['rates'],snapshot=snapshot)
        if scope:
            key=scope['billing_object_id'];identity=(row['run'],scope['fit_id'],scope['stage'])
            prior=groups.setdefault(key,{'identity':identity,'terminal':0,'active':0})
            if prior['identity']!=identity:raise ValueError('ITEM4_BILLING_OBJECT_SHARED')
            prior['terminal' if row['status'] in {'COLLECTED','ACCOUNTED'} else 'active']+=cost
        else:
            key='legacy-reservation:'+row['id'];commitments[key]=cost
            by_run[row['run']]=by_run.get(row['run'],0)+cost
        if (db.execute('SELECT 1 FROM events WHERE id=?',(row['id']+':terminal-exposure',)).fetchone() or
                db.execute('SELECT 1 FROM events WHERE id=?',(row['id']+':confirmed-closed-compute',)).fetchone()):
            proofs[row['id']]=cost
    seen=highwater(db);cycle=datetime.fromisoformat(snapshot['observed_at']).strftime('%Y-%m')
    underestimated=[]
    for key,group in groups.items():
        lifetime=sum(value for (obj,cycle),value in seen.items() if obj==key)
        # Cumulative billing may belong entirely to old segments. Never let it
        # consume the outstanding reservation of a currently active segment.
        cost=max(group['terminal'],lifetime)+group['active']
        if group['active']==0 and lifetime>group['terminal']:underestimated.append(key)
        previous=sum(value for (obj,month),value in seen.items() if obj==key and month<cycle)
        run,fit,stage=group['identity'];commitments[key]=max(0,cost-previous)
        by_run[run]=by_run.get(run,0)+cost
        if stage=='SMOKE':smoke[run]=smoke.get(run,0)+cost
    return {'commitments':commitments,'run_cost':by_run,'smoke_cost':smoke,
            'terminal_bounds_micro_usd':proofs,'underestimated_apps':underestimated,'not_final_invoices':True}
