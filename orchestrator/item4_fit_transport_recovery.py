"""Exact positively stopped fit recovery; immutable originals and normal admission."""
from pathlib import Path
import hashlib
import json

ROOT=Path('/opt/research-system/manual-repair-helpers/item4-fit-stdin-recovery-20261009')
CONTRACT_SHA='ac8460535f9572a5180f6f899bc18072c44fc6fd7de3f40d040fb67df08ba982'
ORIGINAL_ID='c361f596fc3ee541fd94aad7c3e68b8c0aebb5a6657ad48958df398f8cbecf86'
KEY='fit_transport_recovery'
SUFFIX=':fit-transport-stop'
DERIVED={'execution','code_sha256','spec_sha256','review_sha256','execution_plan_sha256'}


def encoded(value):return json.dumps(value,sort_keys=True,allow_nan=False).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('FIT_RECOVERY_'+why)
def authority():raise ValueError('FIT_RECOVERY_UNCONNECTED_AUTHORITY')


def contract():
    authority()
    from orchestrator.manual_host_guard import trusted
    from orchestrator import private_records as pr
    raw=pr.check(trusted(ROOT/'docs/ITEM4_FIT_TRANSPORT_RECOVERY_PRIVATE.json')).read_bytes()
    require(sha(raw)==CONTRACT_SHA,'CONTRACT_CHANGED')
    p=json.loads(raw);row=p['old_row'];old=json.loads(row['binding'])
    require(row['id']==ORIGINAL_ID==sha(encoded(old)) and row['status']=='UNCERTAIN'
        and row['reserved_micro_usd']==12_842_400 and old['resources']['gpu']=='A100-80GB'
        and old['experiment']['fit_id']=='benchmark-A100-80GB' and old['experiment']['segment']==1
        and old['experiment']['stage']=='SMOKE' and 'preprocessing' not in old,'ORIGINAL_SCOPE')
    event=p['event'];expected={**old,'fresh_start':{'previous_binding_sha256':row['id'],
        'terminal_event_sha256':sha(encoded(event))}}
    require(p['new_binding']==expected and p['new_initial_binding']=={k:v for k,v in expected.items() if k not in DERIVED}
        and sha(encoded(expected))==p['new_compute_id'],'EXACT_SUCCESSOR')
    require(sha(encoded(p['runtime']))==old['runtime_sha256']==p['runtime_ref']['sha256']
        and event['original_row']==row and event['evidence_files']==p['evidence_files']
        and event['original_state_sha256']==sha(p['old_state_raw'].encode())
        and event['terminal_exit_code']==137 and event['may_launch'] is False and event['progress_empty'] is True,
        'ORIGINAL_PROOF')
    return p


def validate_identity(binding):
    p=contract()
    require(binding in (p['new_initial_binding'],p['new_binding']),'ONE_EXACT_IDENTITY')


def retained(db,p,*,accounted=True):
    row=db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ORIGINAL_ID,)).fetchone()
    require(row is not None and dict(row)=={**p['old_row'],'status':'ACCOUNTED' if accounted else 'UNCERTAIN'},
        'ORIGINAL_ROW_CHANGED')
    return row


def originals(p):
    from orchestrator import private_records as pr
    result={}
    for name,pin in p['evidence_files'].items():
        raw=pr.check(name).read_bytes();require(sha(raw)==pin,'ORIGINAL_RECEIPT_CHANGED')
        result[Path(name).name]=json.loads(raw)
    require('launched.json' not in result,'LAUNCH_RECEIPT_PRESENT')
    work=Path(next(iter(p['evidence_files']))).parent
    require(not (work/'launched.json').exists(),'LAUNCH_RECEIPT_PRESENT')
    intent=result['create-intent.json'];stopped=result['operator-stopped.json'];created=result['created.json']
    pid=p['old_row']['provider_id']
    require(intent['binding_sha256']==ORIGINAL_ID and created['binding_sha256']==ORIGINAL_ID
        and created['provider_id']==pid and created['receipt']['entrypoint']=='idle-only'
        and stopped['before']['binding_sha256']==ORIGINAL_ID and stopped['before']['provider_id']==pid
        and stopped['before']['progress_entries']==[] and stopped['native_poll_after']==137
        and stopped['native_termination']=={'provider_id':pid,'terminated':True},'TERMINAL_PROOF')
    from orchestrator.item4_closed_attempt_billing import instant
    start,end=map(instant,p['billing_window'])
    require(start<=instant(intent['cost_clock']['observed_at'])<instant(stopped['at'])<end,'CLOSED_WINDOW')
    return result


def billed(db,p,snapshots):
    from orchestrator.item4_closed_attempt_billing import snapshot,instant
    from orchestrator.modal_billing import decimal,micros
    start,end=map(instant,p['billing_window']);app=p['new_binding']['experiment']['billing_object_id']
    require((end-start).total_seconds()==3600 and start.minute==start.second==start.microsecond==0,'BILLING_WINDOW')
    amounts=[]
    for view in snapshots:
        snapshot(view);require(view['workspace']==p['runtime']['workspace'],'BILLING_WORKSPACE')
        if instant(view['report_start'])<=start and instant(view['report_end_exclusive'])>=end:
            amounts.extend(decimal(r['cost']) for r in view['rows'] if r['object_id']==app and instant(r['interval_start'])==start)
    require(bool(amounts),'COMPLETED_BILLING_HOUR_REQUIRED')
    # The old app is reused only after the closed, billed hour. No uncertain
    # attempt or overlapping bill can receive this one exact credit.
    from orchestrator import private_records as pr
    from orchestrator.modal_executor import item4_job
    root=Path(next(iter(p['evidence_files']))).parent.parent
    for row in db.execute('SELECT * FROM autonomy_compute'):
        binding=json.loads(row['binding'])
        if row['id']==ORIGINAL_ID or binding.get('experiment',{}).get('billing_object_id')!=app:continue
        require(binding==p['new_binding'],'UNEXPECTED_APP_ATTEMPT')
        path=root/item4_job(binding)/'create-intent.json'
        if path.exists():
            intent=json.loads(pr.check(path).read_bytes())
            require(intent['binding_sha256']==row['id'] and instant(intent['cost_clock']['observed_at'])>=end,'BILLING_OVERLAP')
        else:
            require(row['status']=='RESERVED' and row['provider_id'] is None,'UNPROVEN_APP_ATTEMPT')
    return micros(max(amounts))


def saved_cost(db,p,current=None):
    retained(db,p);originals(p)
    row=db.execute('SELECT job,payload FROM events WHERE id=?',(ORIGINAL_ID+SUFFIX,)).fetchone()
    require(row is not None and row['job']==p['old_row']['run'],'TERMINAL_EVENT_MISSING')
    saved=json.loads(row['payload']);require(saved['proof']==p['event'] and saved['contract_sha256']==CONTRACT_SHA
        and saved['original_reserved_micro_usd']==p['old_row']['reserved_micro_usd']
        and saved['overhead_retained_micro_usd']==p['new_binding']['overhead_micro_usd'],'COST_RECORD_CHANGED')
    require(saved['actual_compute_micro_usd']==billed(db,p,[saved['billing_snapshot']]),'ACTUAL_CHANGED')
    views=[saved['billing_snapshot']]+([] if current is None else [current])
    from orchestrator import modal_terminal_cost
    modal_terminal_cost.highwater(db)
    for event in db.execute("SELECT payload FROM events WHERE id LIKE 'item4-billing:%'"):
        views.append(json.loads(event['payload'])['snapshot'])
    return saved,billed(db,p,views)+saved['overhead_retained_micro_usd']


def effective(db,row,current=None):
    if row['id']!=ORIGINAL_ID:return None
    event=db.execute('SELECT 1 FROM events WHERE id=?',(ORIGINAL_ID+SUFFIX,)).fetchone()
    if event is None:return None
    saved,amount=saved_cost(db,contract(),current)
    return max(amount,row['actual_micro_usd'] or 0)


def validate_reservation(accounts,predecessors,binding):
    p=contract();require(binding==p['new_binding'] and len(predecessors)==1,'ONE_EXACT_SUCCESSOR')
    row,data=predecessors[0]
    require(row['id']==ORIGINAL_ID and data==json.loads(p['old_row']['binding']),'PREDECESSOR_CHANGED')
    saved_cost(accounts.db,p) # Ordinary admission still counts every row and applies every cap.


def marker(p):
    return {'schema':'fixed-fit-transport-recovery/v1','contract_sha256':CONTRACT_SHA,
        'review_sha256':authority()['report_sha256'],'old_job':p['old_job'],'new_job':p['new_job']}


def activate(driver,provider):
    from orchestrator.manual_driver import write_once
    from orchestrator import private_records as pr
    from orchestrator.modal_fit_provider import progress_scope,progress_volume
    from datetime import datetime,timezone
    from orchestrator.item4_closed_attempt_billing import instant
    p=contract();db=driver.store.batch.db;value=driver.current()
    require(driver.config['run_id']==p['old_row']['run'] and value['phase']=='EXECUTE_EXPERIMENT','LANE_SCOPE')
    if KEY in value:
        require(value[KEY]==marker(p),'MARKER_CHANGED');saved_cost(db,p)
        return {'status':'ALREADY_ACTIVATED','provider_compute':False}
    raw=driver.store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    require(raw==p['old_state_raw'],'STATE_CHANGED');originals(p)
    local=driver.store.db.execute('SELECT * FROM jobs WHERE id=?',(p['old_job'],)).fetchone()
    require(local is not None and dict(local)==p['old_local_row'],'OLD_JOB_CHANGED')
    old=json.loads(p['old_row']['binding']);pid=p['old_row']['provider_id'];sandbox=provider._sandbox(pid)
    require(provider.config==p['runtime'] and sandbox.object_id==pid and sandbox.poll()==137,'NOT_TERMINAL')
    volume=progress_volume(provider,progress_scope(old))
    require(volume.object_id==old['progress']['volume_id'] and not volume.listdir('/',recursive=True)
        and sandbox.poll()==137,'PROGRESS_NOT_EMPTY')
    snapshot=provider.billing_snapshot()
    require(datetime.now(timezone.utc)>=instant(p['billing_window'][1]),'CLOSED_HOUR_WAIT')
    actual=billed(db,p,[snapshot])
    folder=driver.state/'fit-transport-recovery';pr.mkdir(folder,exist_ok=True)
    write_once(folder/'ORIGINAL_STATE.json',raw.encode());write_once(folder/'ORIGINAL_COMPUTE.json',encoded(p['old_row']))
    saved={'proof':p['event'],'contract_sha256':CONTRACT_SHA,'billing_snapshot':snapshot,
        'original_reserved_micro_usd':p['old_row']['reserved_micro_usd'],'actual_compute_micro_usd':actual,
        'overhead_retained_micro_usd':old['overhead_micro_usd'],'provider_invoice_final':False}
    db.execute('BEGIN IMMEDIATE')
    try:
        prior=db.execute('SELECT 1 FROM events WHERE id=?',(ORIGINAL_ID+SUFFIX,)).fetchone()
        if prior:saved_cost(db,p)
        else:
            retained(db,p,accounted=False)
            db.execute('INSERT INTO events VALUES(?,?,?)',(ORIGINAL_ID+SUFFIX,p['old_row']['run'],encoded(saved).decode()))
            db.execute("UPDATE autonomy_compute SET status='ACCOUNTED' WHERE id=?",(ORIGINAL_ID,))
        db.execute('COMMIT')
    except BaseException:db.execute('ROLLBACK');raise
    require(driver.store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'STATE_CHANGED')
    value[KEY]=marker(p);driver.save(value);write_once(folder/'ACTIVATED.json',encoded(marker(p)))
    return {'status':'EXACT_SUCCESSOR_SELECTED','new_job':p['new_job'],'original_reservation_preserved':True,
        'actual_compute_micro_usd':actual,'provider_compute':False}


def resolve(driver,value,selected):
    if KEY not in value:return selected
    from orchestrator import experiment_dispatch as dispatch
    p=contract();require(value[KEY]==marker(p) and selected is not None,'SELECTION_MARKER')
    saved_cost(driver.store.batch.db,p)
    matches=[j for j in selected['jobs'] if j['job']==p['old_job']]
    old=json.loads(p['old_row']['binding']);initial={k:v for k,v in old.items() if k not in DERIVED}
    require(len(matches)==1 and matches[0]['binding']==initial and matches[0]['runtime']==p['runtime'],'ORIGINAL_SELECTION')
    original=json.loads(p['old_state_raw'])
    require(value['fit_dispatch'][p['old_job']]==original['fit_dispatch'][p['old_job']],'OLD_DISPATCH_CHANGED')
    selection={'schema':'experiment-fit-dispatch/v1','source':driver.config['source'],'run_id':driver.config['run_id'],
        'package_manifest_sha256':sha((driver.state/'experiment-package/manifest.json').read_bytes()),
        'jobs':[{'runtime':p['runtime_ref'],'binding':p['new_initial_binding']}]}
    checked=dispatch.validate_selection(driver,value,encoded(selection),partial=True)
    require(len(checked['jobs'])==1 and checked['jobs'][0]['job']==p['new_job'],'SUCCESSOR_CHANGED')
    return {**selected,'jobs':[checked['jobs'][0] if j['job']==p['old_job'] else j for j in selected['jobs']],
        'all_jobs':list(dict.fromkeys([*selected.get('all_jobs',[]),*[j['job'] for j in selected['jobs']],p['new_job']]))}
