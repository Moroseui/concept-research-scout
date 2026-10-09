"""Replay a positively reconciled preprocessing segment through ordinary ticks."""
import copy
from orchestrator import experiment_preprocessing_dispatch as dispatch
from orchestrator import preprocessing_recovery as recovery
from orchestrator.preprocessing_checkpoints import sha,hash_value
from orchestrator.review_contract import strict_json
from orchestrator.modal_executor import item4_job


def terminal(driver,value,job):
    _,manifest=dispatch.package(driver,value,job)
    binding=manifest['binding'];ident=hash_value(binding)
    row=driver.store.batch.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
    event=driver.store.batch.db.execute('SELECT job,payload FROM events WHERE id=?',(ident+':preprocessing-interruption',)).fetchone()
    if (row is None or row['status']!='ACCOUNTED' or row['run']!=driver.config['run_id']
            or strict_json(row['binding'])!=binding or event is None or event['job']!=row['run']):
        raise ValueError('PREPROCESSING_ACCOUNTED_TERMINAL_REQUIRED')
    record=strict_json(event['payload']);proof=recovery.validate_proof(binding,row['provider_id'],record.get('proof'))
    if (record.get('kind')!='PREPROCESSING_INTERRUPTED_WITH_COMMITTED_STEPS'
            or record.get('resume_reason') not in recovery.REASONS
            or record.get('prior_reserved_micro_usd')!=row['reserved_micro_usd']):
        raise ValueError('PREPROCESSING_TERMINAL_PROOF_BINDING')
    return {'ident':ident,'event_sha256':sha(event['payload'].encode()),'proof':proof}


def successor(job,proof):
    binding=copy.deepcopy(job['binding']);binding['experiment']['segment']+=1
    binding['resume']={'previous_segment_id':proof['ident'],'terminal_receipt_sha256':proof['event_sha256'],
                      'steps_record_sha256':proof['proof']['steps_record_sha256']}
    return {'job':item4_job(binding),'binding':binding,'runtime':job['runtime'],
            'initial_job':job.get('initial_job',job['job'])}


def resolve(driver,value,selected):
    chains=value.get('preprocessing_continuations',{})
    if not isinstance(chains,dict) or set(chains)-{j['job'] for j in selected['jobs']}:
        raise ValueError('PREPROCESSING_CONTINUATION_CHAIN')
    jobs=[];all_jobs=[];history=[]
    for first in selected['jobs']:
        job={**first,'initial_job':first['job']};links=chains.get(first['job'],[])
        if not isinstance(links,list):raise ValueError('PREPROCESSING_CONTINUATION_CHAIN')
        all_jobs.append(job['job'])
        for link in links:
            if (not isinstance(link,dict) or set(link)!={'previous_job','event_sha256'}
                    or link['previous_job']!=job['job']
                    or value.get('preprocessing_dispatch',{}).get(job['job'],{}).get('phase')!='INTERRUPTED'):
                raise ValueError('PREPROCESSING_CONTINUATION_CHAIN')
            proof=terminal(driver,value,job)
            if link['event_sha256']!=proof['event_sha256']:raise ValueError('PREPROCESSING_CONTINUATION_CHANGED')
            history.append({'preprocessing_id':job['binding']['preprocessing']['id'],
                'segment':job['binding']['experiment']['segment'],'previous_binding_sha256':proof['ident'],
                'terminal_receipt_sha256':proof['event_sha256'],
                'steps_record_sha256':proof['proof']['steps_record_sha256'],
                'completed_steps':len(proof['proof']['snapshot']['steps']),
                'observed_at':proof['proof']['observed_at'],
                'environment_sha256':job['binding']['preprocessing']['environment_sha256']})
            job=successor(job,proof);all_jobs.append(job['job'])
        jobs.append(job)
    return {**selected,'jobs':jobs,'all_jobs':all_jobs,'continuations':history}


def schedule(driver,value,job):
    proof=terminal(driver,value,job);key=job.get('initial_job',job['job'])
    links=value.setdefault('preprocessing_continuations',{}).setdefault(key,[])
    if any(link['previous_job']==job['job'] for link in links):raise ValueError('PREPROCESSING_CONTINUATION_ALREADY_LINKED')
    links.append({'previous_job':job['job'],'event_sha256':proof['event_sha256']})
    driver.save(value)
    return {**driver.status(),'next_action':'PREPARE_PREPROCESSING_CONTINUATION','provider_called':False}


def reconcile(driver,value,job_id,reason_record):
    if value.get('phase')!='EXECUTE_EXPERIMENT':raise ValueError('PREPROCESSING_RECONCILIATION_PHASE')
    selected=dispatch.load(driver,value)
    matches=[j for j in selected['jobs'] if j['job']==job_id] if selected else []
    if len(matches)!=1 or value.get('preprocessing_dispatch',{}).get(job_id,{}).get('phase') not in {'RUNNING','INTERRUPTED'}:
        raise ValueError('PREPROCESSING_RECONCILIATION_SELECTION')
    job=matches[0];_,manifest=dispatch.package(driver,value,job);store=dispatch.dispatch.executor(driver,job)
    try:receipt=recovery.record(store.costs,hash_value(manifest['binding']),store.provider,reason_record=reason_record)
    finally:store.db.close()
    value['preprocessing_dispatch'][job_id]['phase']='INTERRUPTED';driver.save(value)
    return {'status':'INTERRUPTED_STEPS_PRESERVED','job':job_id,'may_launch':False,
            'steps_record_sha256':receipt['proof']['steps_record_sha256']}


def history(driver,value):
    if not dispatch.frozen(driver):return []
    selected=dispatch.load(driver,value)
    if selected is None:raise ValueError('EXPERIMENT_PREPROCESSING_REQUIRED')
    return selected['continuations']
