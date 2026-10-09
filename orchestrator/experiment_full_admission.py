"""Item4's conditional FULL admission; not a new scientific judgment.

The operator pre-authorized FULL after reviewed smoke criteria and a measured
projection <=1200 USD. Replay actual specification approval, original smoke
collections and measured evidence. No generic ACCEPTED record grants admission.
"""
import sqlite3
from pathlib import Path
from types import SimpleNamespace
from orchestrator import experiment_package,experiment_dispatch,experiment_projection
from orchestrator import private_records as pr
from orchestrator.experiment_result import strict
from orchestrator.manual_executor import digest
from orchestrator.manual_driver import write_once
from orchestrator.modal_executor import canonical
from orchestrator.modal_item4_policy import AUTHORITY,PROJECTION_LIMIT

SCHEMA='item4-full-admission/v1'


def inspect(driver,value):
    sealed=experiment_package.verify(driver,value,driver.state/'experiment-package')
    selected=experiment_dispatch.load(driver,value)
    if selected is None:raise ValueError('ITEM4_FULL_SMOKE_SELECTION_REQUIRED')
    measured=experiment_projection.verify(driver,value,selected,value.get('measured_projection'))
    hardware=experiment_projection.verify(driver,value,selected,value.get('measured_hardware'),kind='hardware')
    calculation=measured['calculation']
    if (not calculation['within_projection_limit'] or
            not 0<calculation['full_projection_micro_usd']<=PROJECTION_LIMIT):
        raise ValueError('ITEM4_FULL_PROJECTION_LIMIT')
    if calculation['selected_gpu']!=hardware['calculation']['selected_gpu']:
        raise ValueError('ITEM4_FULL_HARDWARE_CHANGED')
    # The spec/code review is genuine and independently requalified by verify,
    # not merely a flag on the timing record or a runtime validator verdict.
    approved=strict(pr.check(driver.state/'experiment-package/approval.json').read_bytes())
    code=approved['code_files']['execution.py']['sha256']
    return {'schema':SCHEMA,'status':'REVIEWED_SMOKE_CONDITIONS_VERIFIED',
        'run_id':driver.config['run_id'],'state':str(driver.state),
        'source':driver.config['source'],'authority_sha256':AUTHORITY,
        'reviewed_execution_sha256':sealed['reviewed_execution_sha256'],
        'package_manifest_sha256':digest(pr.check(driver.state/'experiment-package/manifest.json').read_bytes()),
        'spec_sha256':sealed['files']['SPEC.md'],'review_sha256':sealed['files']['review.json'],
        'module_sha256':code,'execution_plan_sha256':sealed['files']['execution-plan.json'],
        'projection':value['measured_projection'],'hardware':value['measured_hardware'],
        'full_projection_micro_usd':calculation['full_projection_micro_usd'],
        'full_fit_ids':[f['fit_id'] for f in calculation['fits']],
        'scientific_results_accepted':False,'new_allowance':False}


@pr.private_umask
def record(driver,value):
    if value.get('phase')!='EXECUTE_EXPERIMENT':raise ValueError('ITEM4_FULL_ADMISSION_PHASE')
    db=driver.store.batch.db
    if (driver.store.batch.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
    result=inspect(driver,value);raw=canonical(result)
    path=driver.state/'full-admission'/(digest(raw)+'.json')
    write_once(path,raw)
    event={'schema':SCHEMA,'record':{'path':str(path),'sha256':digest(raw)}}
    encoded=canonical(event).decode();ident=driver.config['run_id']+':full-projection-approved'
    db.execute('BEGIN IMMEDIATE')
    try:
        owner=db.execute('SELECT status,binding FROM autonomy_runs WHERE id=?',(driver.config['run_id'],)).fetchone()
        if (owner is None or owner['status']!='ACTIVE'
                or strict(owner['binding'])!=driver.config['owner_binding']):
            raise ValueError('ITEM4_FULL_OWNER_CHANGED')
        if (driver.store.batch.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
        if inspect(driver,value)!=result:raise ValueError('ITEM4_FULL_EVIDENCE_CHANGED')
        old=db.execute('SELECT job,payload FROM events WHERE id=?',(ident,)).fetchone()
        if old is not None:
            if old['job']!=driver.config['run_id'] or old['payload']!=encoded:
                raise ValueError('ITEM4_FULL_EXISTING_RECORD_CHANGED')
            db.execute('COMMIT');return event
        db.execute('INSERT INTO events VALUES(?,?,?)',(ident,driver.config['run_id'],encoded))
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK');raise
    return event


def _driver(accounts,run,event):
    """Read the actual owning lane without constructing a writer or client."""
    from tools.deploy_manual_lane import bound
    owner=accounts.db.execute('SELECT binding FROM autonomy_runs WHERE id=?',(run,)).fetchone()
    if owner is None:raise ValueError('ITEM4_FULL_OWNER_REQUIRED')
    owner=strict(owner['binding'])
    if not isinstance(owner,dict) or not isinstance(owner.get('state'),str):
        raise ValueError('ITEM4_FULL_BOUND_OWNER_REQUIRED')
    state=bound(accounts.batch.filesystem_root,owner['state'])
    config=strict(pr.check(state/'lane.json').read_bytes())
    if (config.get('run_id')!=run or config.get('owner_binding')!=owner
            or config.get('item_number')!=4):raise ValueError('ITEM4_FULL_OWNER_CHANGED')
    if (not isinstance(event,dict) or set(event)!={'schema','record'} or event['schema']!=SCHEMA
            or not isinstance(event['record'],dict) or set(event['record'])!={'path','sha256'}):
        raise ValueError('ITEM4_FULL_BOUND_PROJECTION_REQUIRED')
    ref=event['record'];record_path=state/'full-admission'/(ref['sha256']+'.json')
    if bound(accounts.batch.filesystem_root,ref['path'])!=record_path:
        raise ValueError('ITEM4_FULL_RECORD_SCOPE')
    raw=pr.check(record_path).read_bytes()
    if digest(raw)!=ref['sha256']:raise ValueError('ITEM4_FULL_RECORD_CHANGED')
    database=pr.check(state/'jobs.sqlite')
    db=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    try:
        row=db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()
        if row is None:raise ValueError('ITEM4_FULL_LANE_STATE_REQUIRED')
        value=strict(row['payload'])
        driver=SimpleNamespace(state=state,config=config,
            context=bound(accounts.batch.filesystem_root,config['context']),
            root=bound(accounts.batch.filesystem_root,config['root']),
            store=SimpleNamespace(path=database,db=db,batch=accounts.batch))
        preserved=strict(raw)
        if inspect(driver,value)!=preserved:raise ValueError('ITEM4_FULL_EVIDENCE_CHANGED')
        return driver,value,preserved,db
    except BaseException:
        db.close();raise


def verify_reservation(accounts,run,binding,billing_snapshot):
    """Called inside ordinary admission's transaction; never opens a writer."""
    row=accounts.db.execute('SELECT job,payload FROM events WHERE id=?',(run+':full-projection-approved',)).fetchone()
    if row is None:raise ValueError('ITEM4_ACCEPTED_SMOKE_PROJECTION_REQUIRED')
    if row['job']!=run:raise ValueError('ITEM4_FULL_RECORD_SCOPE')
    event=strict(row['payload'])
    # Refuse the previous loose format, including an otherwise plausible
    # ACCEPTED amount below the cap. It has no bound original evidence.
    if not isinstance(event,dict) or event.get('schema')!=SCHEMA:
        raise ValueError('ITEM4_FULL_BOUND_PROJECTION_REQUIRED')
    driver,value,record,db=_driver(accounts,run,event)
    try:
        if any(binding.get(k)!=record[k] for k in ('source','spec_sha256','review_sha256','execution_plan_sha256')):
            raise ValueError('ITEM4_FULL_SCIENTIFIC_BINDING')
        if binding.get('execution',{}).get('module_sha256')!=record['module_sha256']:
            raise ValueError('ITEM4_FULL_SCIENTIFIC_BINDING')
        selected=experiment_dispatch.load(driver,value)
        from orchestrator import experiment_modal_package as bridge
        jobs=[j for j in selected['jobs'] if j['binding']['experiment']['fit_id']==binding['experiment']['fit_id']]
        if len(jobs)!=1 or jobs[0]['binding']!=bridge.base_binding(binding):
            raise ValueError('ITEM4_FULL_UNSELECTED_RUNTIME')
        bridge.replay(driver,value,driver.state/'fit-packages'/jobs[0]['job']/'prepared',binding)
        plan,observations,_=experiment_projection.evidence(driver,value,selected)
        # Current prices must still satisfy the pre-authorized threshold; an
        # old estimate cannot admit work after a material price change.
        calculated=experiment_projection.calculate(plan,observations,billing_snapshot['rates'])
        hardware=experiment_projection.verify(driver,value,selected,record['hardware'],kind='hardware')
        if (not calculated['within_projection_limit'] or calculated['selected_gpu']!=hardware['calculation']['selected_gpu']):
            raise ValueError('ITEM4_FULL_CURRENT_PROJECTION_CHANGED')
        matches=[f for f in calculated['fits'] if f['fit_id']==binding['experiment']['fit_id']]
        if len(matches)!=1:raise ValueError('ITEM4_FULL_UNREVIEWED_FIT')
        fit=matches[0];resources=binding['resources']
        if (any(resources.get(k)!=fit['resources'][k] for k in ('gpu','cpu','memory_mib'))
                or resources['timeout_seconds']<min(fit['projected_seconds'],86400)
                or binding['overhead_micro_usd']!=fit['overhead_micro_usd']):
            raise ValueError('ITEM4_FULL_PROJECTED_RESOURCES_CHANGED')
        return {'record_sha256':event['record']['sha256'],
            'measured_projection_sha256':record['projection']['sha256'],
            'current_full_projection_micro_usd':calculated['full_projection_micro_usd'],
            'fit_id':fit['fit_id'],'scientific_results_accepted':False}
    finally:db.close()
