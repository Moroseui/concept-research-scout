"""Connect the existing checkpoint path after two exactly preserved pre-science stops."""
from pathlib import Path
import copy
import hashlib
import json
from orchestrator import private_records as pr
from orchestrator import preprocessing_recovery as recovery
from orchestrator.preprocessing_checkpoints import same_execution

ROOT=Path('/opt/research-system/manual-repair-helpers/item4-preprocessing-checkpoint-connection-20261009')
CONTRACT_SHA='6f4f494f87c9edb631c8107c05bb963f32839ccfd4a951700b878db3e95aeaa2'
KEY='preprocessing_private_staging'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return json.dumps(value,sort_keys=True,allow_nan=False).encode()
def require(ok,why):
    if not ok:raise ValueError('CHECKPOINT_CONNECTION_'+why)
def authority():raise ValueError('CHECKPOINT_CONNECTION_UNCONNECTED_AUTHORITY')

def contract():
    authority()
    from orchestrator import item4_private_staging_retry as staging
    prior=staging.contract()
    raw=(ROOT/'docs/ITEM4_CHECKPOINT_CONNECTION.json').read_bytes()
    require(sha(raw)==CONTRACT_SHA,'CONTRACT_CHANGED')
    cfg=json.loads(raw)
    observation=pr.check(cfg['observation']['path']).read_bytes()
    require(sha(observation)==cfg['observation']['sha256'],'OBSERVATION_CHANGED')
    saved=json.loads(observation);row=saved['row'];binding=json.loads(row['binding'])
    require(cfg['schema']=='fixed-preprocessing-checkpoint-connection/v1'
        and row['id']==cfg['current_id']==prior['new_compute_id']==sha(encoded(binding))
        and cfg['current_job']==prior['new_job'] and binding==prior['new_binding']
        and saved['initial_binding']==prior['new_initial_binding']
        and saved['runtime']==prior['new_runtime'] and row['status']=='RUNNING'
        and row['reserved_micro_usd']==10_342_400 and row['provider_id']==cfg['provider_id'],
        'EXACT_ORIGINAL')
    proof=recovery.validate_proof(binding,row['provider_id'],saved['terminal_proof'])
    require(proof['terminal_exit_code']==cfg['terminal_exit_code']==124
        and proof['steps_record_sha256']==cfg['steps_record_sha256']
        and len(proof['snapshot']['steps'])==cfg['completed_steps']==92,'TIMEOUT_CHECKPOINT')
    for path,record in saved['originals'].items():
        raw_file=pr.check(path).read_bytes()
        require(sha(raw_file)==record['sha256'] and raw_file.decode()==record['text'],'ORIGINAL_CHANGED')
    return cfg,saved,prior

def resolve(driver,value,selected,prior_resolve,native_resolve):
    if KEY not in value:return prior_resolve(driver,value,selected)
    cfg,saved,prior=contract()
    chains=value.get('preprocessing_continuations',{})
    require(isinstance(chains,dict) and set(chains)<={cfg['current_job']},'CHAIN_ORIGIN')
    if chains:
        links=chains[cfg['current_job']]
        require(isinstance(links,list) and len(links)==1
            and isinstance(links[0],dict) and links[0].get('previous_job')==cfg['current_job'],
            'ONE_NATIVE_CONTINUATION')
    # Existing fixed replacements authenticate every historical row and marker.
    # Only order changes: apply native continuation to their resulting job.
    initial=copy.deepcopy(value);initial.pop('preprocessing_continuations',None)
    selected=prior_resolve(driver,initial,selected)
    require([j['job'] for j in selected['jobs']]==[cfg['current_job']],'FIXED_SELECTION')
    resolved=native_resolve(driver,value,selected)
    resolved['all_jobs']=list(dict.fromkeys([*selected.get('all_jobs',[]),*resolved['all_jobs']]))
    return resolved

def predecessors(accounts,pairs,binding):
    """Exclude only the two approved pre-science attempts from segment numbering.
    The unmodified budget still counts every original row and effective charge.
    """
    cfg,saved,prior=contract()
    from orchestrator import item4_private_staging_retry as staging
    first=staging.previous().contract()
    historical={first['old_row']['id'],prior['old_row']['id']}
    require(binding.get('experiment',{}).get('segment')==2,'ONE_NATIVE_CONTINUATION')
    same_execution(json.loads(saved['row']['binding']),binding)
    require(len(pairs)==3 and {r['id'] for r,_ in pairs}==historical|{cfg['current_id']},
        'PREDECESSOR_MEMBERS')
    staging.retained(accounts.db,prior)
    current=[(row,data) for row,data in pairs if row['id']==cfg['current_id']]
    row,data=current[0]
    require(dict(row)=={**saved['row'],'status':'ACCOUNTED'}
        and data==json.loads(saved['row']['binding']),'CURRENT_ROW_CHANGED')
    # Native code independently authenticates the terminal event and resume link.
    recovery.validate_reservation(accounts.db,row,data,binding)
    return current

def reconcile(driver,value):
    cfg,saved,prior=contract()
    require(driver.config['run_id']==saved['row']['run'],'RUN_SCOPE')
    selected=__import__('orchestrator.experiment_preprocessing_dispatch',fromlist=['load']).load(driver,value)
    matches=[j for j in selected['jobs'] if j['job']==cfg['current_job']]
    require(len(matches)==1,'CURRENT_SELECTION')
    from orchestrator import experiment_dispatch as dispatch, preprocessing_continuation as continuation
    job=matches[0]
    executor=dispatch.executor(driver,job)
    try:
        binding=json.loads(saved['row']['binding'])
        fresh=executor.provider.terminal_preprocessing_steps(saved['row']['provider_id'],binding)
        # Observation timestamp may advance; every scientific/checkpoint field must match.
        require({k:v for k,v in fresh.items() if k!='observed_at'}==
            {k:v for k,v in saved['terminal_proof'].items() if k!='observed_at'},'TERMINAL_CHANGED')
    finally:executor.db.close()
    reason={'schema':'modal-interruption-cause/v1','segment_id':cfg['current_id'],
        'provider_id':cfg['provider_id'],'reason':'LIFETIME_TIMEOUT',
        'evidence':{'observation':cfg['observation'],'terminal_exit_code':124,
            'steps_record_sha256':cfg['steps_record_sha256']}}
    from orchestrator.manual_driver import write_once
    path=driver.state/'checkpoint-terminal-observation-20261009'/'CAUSE.json'
    write_once(path,encoded(reason))
    return continuation.reconcile(driver,value,cfg['current_job'],path)

def validate_identity(binding):
    """Only the exact stopped original can retain its fresh-start identity."""
    cfg,saved,prior=contract()
    from orchestrator.preprocessing_checkpoints import resume
    from orchestrator.item4_private_staging_retry import DERIVED
    link=resume(binding)
    require(binding['experiment']['segment']==2 and link is not None
        and link['previous_segment_id']==cfg['current_id']
        and link['steps_record_sha256']==cfg['steps_record_sha256'],'EXACT_RESUME_IDENTITY')
    base={k:v for k,v in binding.items() if k not in DERIVED}
    same_execution(prior['new_initial_binding'],base)
    if any(k in binding for k in DERIVED):
        same_execution(prior['new_binding'],binding)
