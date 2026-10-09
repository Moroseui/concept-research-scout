"""Same-fit continuation derived from the existing terminal/checkpoint ledger.

No allowance, new scientific identity, resource change or provider creation is
made here. The ordinary executor still checks current billing, every prior
segment and all caps before submitting the derived successor.
"""
import copy
from orchestrator.modal_fit_progress import encoded
from orchestrator.manual_executor import digest
from orchestrator.modal_executor import canonical, item4_job
from orchestrator.review_contract import strict_json

REASONS={'PROVIDER_LIMIT','LIFETIME_TIMEOUT','DELIBERATE_SMOKE_INTERRUPTION','OBSERVED_TRAINING_STALL'}


def terminal(driver, value, job):
    from orchestrator import experiment_modal_package as bridge
    package=driver.state/'fit-packages'/job['job']/'prepared'
    if not package.is_dir():raise ValueError('EXPERIMENT_RESUME_PACKAGE_REQUIRED')
    manifest=bridge.emit(driver,value,package,job['binding']) # Existing exact bytes only.
    binding=manifest['binding'];ident=digest(canonical(binding))
    row=driver.store.batch.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
    event=driver.store.batch.db.execute('SELECT job,payload FROM events WHERE id=?',(ident+':fit-interruption',)).fetchone()
    if (row is None or row['status']!='ACCOUNTED' or strict_json(row['binding'])!=binding
            or row['run']!=driver.config['run_id'] or event is None or event['job']!=row['run']):
        raise ValueError('EXPERIMENT_RESUME_ACCOUNTED_TERMINAL_REQUIRED')
    raw=event['payload'];record=strict_json(raw)
    if not isinstance(record,dict) or not isinstance(record.get('proof'),dict):
        raise ValueError('EXPERIMENT_RESUME_TERMINAL_BINDING')
    proof=record['proof']
    if (record.get('kind')!='FIT_INTERRUPTED_WITH_COMMITTED_CHECKPOINT'
            or record.get('resume_reason') not in REASONS
            or record.get('prior_reserved_micro_usd')!=row['reserved_micro_usd']
            or proof.get('schema')!='modal-fit-terminal-proof/v1'
            or proof.get('provider_id')!=row['provider_id'] or proof.get('binding_sha256')!=ident
            or proof.get('fit_id')!=binding['experiment']['fit_id']
            or type(proof.get('terminal_exit_code')) is not int or proof.get('may_launch') is not False
            or proof.get('checkpoint_record_sha256')!=digest(encoded(proof.get('checkpoint_record')))):
        raise ValueError('EXPERIMENT_RESUME_TERMINAL_BINDING')
    return {'event_sha256':digest(raw.encode()),'segment_id':ident,'record':record}


def successor(job, proof):
    binding=copy.deepcopy(job['binding'])
    binding['experiment']['segment']+=1
    binding['resume']={'previous_segment_id':proof['segment_id'],
        'terminal_receipt_sha256':proof['event_sha256'],
        'checkpoint_record_sha256':proof['record']['proof']['checkpoint_record_sha256']}
    return {'job':item4_job(binding),'runtime':job['runtime'],'binding':binding,
            'initial_job':job.get('initial_job',job['job'])}


def resolve(driver, value, selected):
    """Replay saved links against immutable packages and real ledger events."""
    chains=value.get('fit_continuations',{})
    if not isinstance(chains,dict) or set(chains)-{j['job'] for j in selected['jobs']}:
        raise ValueError('EXPERIMENT_RESUME_CHAIN_FIELDS')
    active=[];all_jobs=[];history=[]
    for first in selected['jobs']:
        job={**first,'initial_job':first['job']};links=chains.get(first['job'],[])
        if not isinstance(links,list):raise ValueError('EXPERIMENT_RESUME_CHAIN_FIELDS')
        all_jobs.append(job['job'])
        for link in links:
            if (not isinstance(link,dict) or set(link)!={'previous_job','event_sha256'}
                    or link['previous_job']!=job['job']
                    or value.get('fit_dispatch',{}).get(job['job'],{}).get('phase')!='INTERRUPTED'):
                raise ValueError('EXPERIMENT_RESUME_CHAIN_BINDING')
            proof=terminal(driver,value,job)
            if link['event_sha256']!=proof['event_sha256']:
                raise ValueError('EXPERIMENT_RESUME_EVENT_CHANGED')
            original=proof['record']['proof'];meta=original['checkpoint_record']['metadata']
            history.append({'fit_id':job['binding']['experiment']['fit_id'],
                'segment':job['binding']['experiment']['segment'],'reason':proof['record']['resume_reason'],
                'terminal_receipt_sha256':proof['event_sha256'],
                'checkpoint_record_sha256':original['checkpoint_record_sha256'],
                'epoch_resumed_from':meta['next_epoch'],'terminal_observed_at':original['observed_at'],
                'environment_sha256':job['binding']['progress']['fit_binding']['environment_sha256'],
                'prior_reserved_micro_usd':proof['record']['prior_reserved_micro_usd']})
            job=successor(job,proof);all_jobs.append(job['job'])
        active.append(job)
    return {**selected,'jobs':active,'all_jobs':all_jobs,'continuations':history}


def schedule(driver, value, job):
    """One deterministic link, then return; never submit inside reconciliation."""
    proof=terminal(driver,value,job)
    chains=value.setdefault('fit_continuations',{})
    key=job.get('initial_job',job['job']);links=chains.setdefault(key,[])
    link={'previous_job':job['job'],'event_sha256':proof['event_sha256']}
    if any(row['previous_job']==job['job'] for row in links):
        raise ValueError('EXPERIMENT_RESUME_LINK_ALREADY_RECONCILE')
    links.append(link)
    driver.save(value)
    return {**driver.status(),'next_action':'PREPARE_CHECKPOINT_CONTINUATION',
            'same_realization':True,'provider_called':False}


def complete_states(selected, states):
    active={j['job'] for j in selected['jobs']};all_ids=set(selected.get('all_jobs',active))
    return (set(states)==all_ids and all(row.get('phase')==('COMPLETE' if key in active else 'INTERRUPTED')
                                       for key,row in states.items()))
