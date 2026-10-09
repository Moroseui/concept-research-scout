"""One fixed, positively stopped pre-science attempt; never a checkpoint."""
from pathlib import Path
import hashlib
import json

ROOT=Path('/opt/research-system/manual-repair-helpers/item4-preprocessing-root-repair-20261009')
CHECKPOINT_SHA='3f87416e8da8758872faadc660a5e20a5d1cee7bbe8fcff326a09031e4f38563'
DERIVED={'execution','code_sha256','spec_sha256','review_sha256','execution_plan_sha256'}


def encoded(value):return json.dumps(value,sort_keys=True,allow_nan=False).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('FRESH_PREPROCESSING_'+why)
def authority():raise ValueError('FRESH_PREPROCESSING_UNCONNECTED_AUTHORITY')


def contract():
    authority()  # Installed source, actual independent APPROVE and unit pins.
    raw=(ROOT/'docs/ITEM4_FRESH_START_CHECKPOINT.json').read_bytes()
    require(sha(raw)==CHECKPOINT_SHA,'CHECKPOINT_CHANGED')
    p=json.loads(raw);old=json.loads(p['old_row']['binding']);new=p['new_binding']
    require(p['old_row']['id']==sha(encoded(old)) and p['old_row']['status']=='RUNNING'
        and p['old_row']['reserved_micro_usd']==10_342_400,'ORIGINAL_IDENTITY')
    expected=dict(old);expected.update(package_volume_id=p['new_runtime']['package_volume_id'],
        runtime_sha256=sha(encoded(p['new_runtime'])),fresh_start={
        'previous_binding_sha256':p['old_row']['id'],'terminal_event_sha256':sha(encoded(p['event']))})
    require(new==expected and p['new_initial_binding']=={k:v for k,v in new.items() if k not in DERIVED}
        and p['new_compute_id']==sha(encoded(new)),'EXACT_TARGET')
    require(p['event']['original_row']==p['old_row'] and p['event']['evidence_files']==p['evidence_files']
        and p['event']['terminal_exit_code']==137 and p['event']['output_volume_empty'] is True
        and p['event']['may_launch'] is False,'ORIGINAL_PROOF')
    runtime=(ROOT/'docs/ITEM4_FRESH_RUNTIME.json').read_bytes()
    require(sha(runtime)==p['new_runtime_sha256']==new['runtime_sha256'] and json.loads(runtime)==p['new_runtime'],'RUNTIME_CHANGED')
    return p


def retained(db,p,*,accounted=True):
    row=db.execute('SELECT * FROM autonomy_compute WHERE id=?',(p['old_row']['id'],)).fetchone()
    expected=dict(p['old_row'])
    if accounted:expected['status']='ACCOUNTED'
    require(row is not None and dict(row)==expected,'ORIGINAL_ROW_CHANGED')
    if accounted:
        event=db.execute('SELECT job,payload FROM events WHERE id=?',(p['old_row']['id']+':pre-science-stop',)).fetchone()
        require(event is not None and event['job']==p['old_row']['run'] and event['payload']==encoded(p['event']).decode(),'TERMINAL_EVENT_CHANGED')
    return row


def validate_reservation(accounts,predecessors,binding):
    p=contract()
    require(binding==p['new_binding'] and len(predecessors)==1,'ONE_EXACT_SUCCESSOR')
    row,data=predecessors[0]
    require(row['id']==p['old_row']['id'] and data==json.loads(p['old_row']['binding']),'PREDECESSOR_CHANGED')
    retained(accounts.db,p)
    # Ordinary reservation continues with all rows/charges, caps and headroom.
    # No limit, exposure, reservation amount or original binding is changed.


def marker(p):
    return {'schema':'fixed-preprocessing-fresh-start/v1','checkpoint_sha256':CHECKPOINT_SHA,
        'implementation_review_sha256':authority()['report_sha256'],'old_job':p['old_job'],
        'new_job':p['new_job'],'terminal_event_sha256':sha(encoded(p['event']))}


def activate(driver,provider):
    """Reconcile one positive terminal proof, then select one new ordinary job."""
    from orchestrator import private_records as pr
    from orchestrator.manual_driver import write_once
    from orchestrator.modal_preprocessing_provider import output_volume,scope
    p=contract();db=driver.store.batch.db;value=driver.current()
    require(driver.config['run_id']==p['old_row']['run'] and value['phase']=='EXECUTE_EXPERIMENT','LANE_SCOPE')
    if value.get('preprocessing_fresh_start') is not None:
        require(value['preprocessing_fresh_start']==marker(p),'ACTIVE_MARKER_CHANGED')
        retained(db,p);return {'status':'ALREADY_ACTIVATED','provider_compute':False}
    raw=driver.store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    require(raw==p['old_state_raw'],'ORIGINAL_STATE_CHANGED')
    for name,pin in p['evidence_files'].items():
        require(sha(pr.check(name).read_bytes())==pin,'ORIGINAL_RECEIPT_CHANGED')
    old=json.loads(p['old_row']['binding']);pid=p['old_row']['provider_id']
    sandbox=provider._sandbox(pid)
    require(sandbox.object_id==pid and sandbox.poll()==137,'NOT_POSITIVELY_TERMINAL')
    volume=output_volume(provider,scope(provider,provider.config,old))
    require(volume.object_id==old['preprocessing_output_volume_id'] and not volume.listdir('/',recursive=True)
        and sandbox.poll()==137,'OUTPUT_NOT_EMPTY_OR_TERMINAL_CHANGED')
    folder=driver.state/'preprocessing-fresh-start';pr.mkdir(folder,exist_ok=True)
    write_once(folder/'ORIGINAL_STATE.json',raw.encode())
    write_once(folder/'ORIGINAL_COMPUTE.json',encoded(p['old_row']))
    db.execute('BEGIN IMMEDIATE')
    try:
        existing=db.execute('SELECT payload FROM events WHERE id=?',(p['old_row']['id']+':pre-science-stop',)).fetchone()
        if existing:retained(db,p)
        else:
            retained(db,p,accounted=False)
            db.execute('INSERT INTO events VALUES(?,?,?)',(p['old_row']['id']+':pre-science-stop',p['old_row']['run'],encoded(p['event']).decode()))
            db.execute("UPDATE autonomy_compute SET status='ACCOUNTED' WHERE id=?",(p['old_row']['id'],))
        db.execute('COMMIT')
    except BaseException:db.execute('ROLLBACK');raise
    # Cross-ledger crash recovery requalifies the same original state and exact
    # committed terminal event; no second computation or accounting charge.
    require(driver.store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'STATE_CHANGED')
    value['preprocessing_fresh_start']=marker(p);driver.save(value)
    write_once(folder/'ACTIVATED.json',encoded(marker(p)))
    return {'status':'FRESH_START_SELECTED','new_job':p['new_job'],'original_charge_retained':p['old_row']['reserved_micro_usd'],'provider_compute':False}


def resolve(driver,value,selected):
    """Replace only the exact root-selected old job; keep its historical entry."""
    if value.get('preprocessing_fresh_start') is None:return selected
    from orchestrator import experiment_preprocessing_dispatch as dispatch
    from orchestrator.modal_executor import canonical
    p=contract();require(value['preprocessing_fresh_start']==marker(p),'ACTIVE_MARKER_CHANGED')
    retained(driver.store.batch.db,p)
    require(selected is not None and not selected.get('continuations'),'UNEXPECTED_CONTINUATION')
    matches=[j for j in selected['jobs'] if j['job']==p['old_job']]
    old=json.loads(p['old_row']['binding']);initial={k:v for k,v in old.items() if k not in DERIVED}
    require(len(matches)==1 and matches[0]['binding']==initial,'ORIGINAL_SELECTION_CHANGED')
    old_runtime=dict(p['new_runtime']);old_runtime['package_volume_id']=old['package_volume_id']
    require(matches[0]['runtime']==old_runtime and sha(encoded(old_runtime))==old['runtime_sha256'],'RUNTIME_SCOPE')
    original_state=json.loads(p['old_state_raw'])
    require(value['preprocessing_dispatch'].get(p['old_job'])==original_state['preprocessing_dispatch'][p['old_job']],'OLD_DISPATCH_CHANGED')
    selection={'schema':dispatch.SCHEMA,'source':driver.config['source'],'run_id':driver.config['run_id'],
        'package_manifest_sha256':sha((driver.state/'experiment-package/manifest.json').read_bytes()),
        'jobs':[{'runtime':{'path':str(ROOT/'docs/ITEM4_FRESH_RUNTIME.json'),'sha256':p['new_runtime_sha256']},
                 'binding':p['new_initial_binding']}]}
    checked=dispatch.validate_selection(driver,value,canonical(selection),partial=True)
    require(len(checked['jobs'])==1 and checked['jobs'][0]['job']==p['new_job'],'NEW_SELECTION_CHANGED')
    return {**selected,'jobs':[checked['jobs'][0] if j['job']==p['old_job'] else j for j in selected['jobs']],
        'all_jobs':list(dict.fromkeys([*selected.get('all_jobs',[]),*[j['job'] for j in selected['jobs']],p['new_job']])),
        'fresh_start':marker(p)}
