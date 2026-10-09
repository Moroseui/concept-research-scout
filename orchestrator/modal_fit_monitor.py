"""One external fit-health transition, using existing executor records and locks.

A stop requires several successful observations, an immediate progress recheck,
and an immutable intent. This function never launches or releases a charge.
"""
import json
from pathlib import Path
from orchestrator import private_records, modal_fit_health
from orchestrator.manual_executor import read, digest
from orchestrator.modal_executor import canonical, item4_job
from orchestrator.manual_driver import write_once
from orchestrator.remote_supervisor import lock


def _history(folder):
    private_records.check_tree(folder)
    files=sorted(folder.glob('observation-*.json'))
    state=None
    for index,path in enumerate(files,1):
        if path.name != 'observation-'+str(index).zfill(6)+'.json':
            raise ValueError('FIT_MONITOR_HISTORY_SEQUENCE')
        value=read(path)
        expected=modal_fit_health.assess(value['observation'],state)
        if value['assessment']!=expected:raise ValueError('FIT_MONITOR_HISTORY_CHANGED')
        state=expected.get('state',state)
    return len(files),state


@private_records.private_umask
def tick(executor, job, log_path=None):
    """Called periodically by the existing server executor, never from a fit.

    Read errors stop this transition without converting a missing observation to
    a stall. A stop intent left by a controller crash is reconciliation-only:
    another tick does not issue another termination request.
    """
    with lock(executor.path.parent/'modal-executor.lock'):
        executor._guard()
        record=executor.get(job);binding=json.loads(record['binding'])
        if item4_job(binding)!=job:raise ValueError('FIT_MONITOR_JOB_BINDING')
        work=executor._paths(job);created=read(work/'created.json')
        ident=digest(canonical(binding));provider_id=created['provider_id']
        if created['binding_sha256']!=ident:raise ValueError('FIT_MONITOR_CREATED_BINDING')
        row=executor.costs.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
        if row is None or row['provider_id']!=provider_id or row['binding']!=canonical(binding).decode():
            raise ValueError('FIT_MONITOR_LEDGER_BINDING')
        folder=work/'health';private_records.mkdir(folder,exist_ok=True)
        if (folder/'interruption.json').exists():
            result=read(folder/'interruption.json')
            old=executor.costs.db.execute('SELECT payload FROM events WHERE id=?',(ident+':fit-interruption',)).fetchone()
            if old is None or json.loads(old['payload'])!=result:
                raise ValueError('FIT_MONITOR_INTERRUPTION_CHANGED')
            return {'status':'INTERRUPTED_CHECKPOINT_PRESERVED','may_launch':False,'duplicate_observation':True}
        if (folder/'stop-intent.json').exists():
            return {'status':'STOP_INTENT_RECONCILIATION_REQUIRED','may_launch':False}
        if row['status']!='RUNNING':
            return {'status':'RECONCILE_TERMINAL_OR_UNCERTAIN','may_launch':False}
        count,state=_history(folder)
        def observe():
            nonlocal count,state
            observation=executor.provider.fit_health(provider_id,binding,log_path)
            if observation['status']=='STARTING' and state is not None:
                raise ValueError('FIT_MONITOR_PROGRESS_DISAPPEARED')
            assessment=modal_fit_health.assess(observation,state)
            count+=1
            path=folder/('observation-'+str(count).zfill(6)+'.json')
            write_once(path,canonical({'observation':observation,'assessment':assessment}))
            state=assessment.get('state',state)
            return path,assessment
        path,result=observe()
        if result['action']!='RECHECK_BEFORE_STOP':
            return {'status':result['action'],'may_launch':False}
        # A newly advanced epoch/checkpoint or terminal job cancels the stop.
        path,checked=observe()
        if checked['action']!='RECHECK_BEFORE_STOP':
            return {'status':checked['action'],'may_launch':False,'stop_cancelled':True}
        evidence={'last_observation':path.name,'sha256':digest(path.read_bytes()),
                  'idle_seconds':checked['idle_seconds'],'threshold_seconds':checked['threshold_seconds'],
                  'successful_overdue_observations':checked['state']['overdue_observations']}
        intent={'schema':'modal-stall-stop/v1','segment_id':ident,'provider_id':provider_id,
                'evidence':evidence,'same_realization_only':True,'may_launch':False}
        write_once(folder/'stop-intent.json',canonical(intent))
        stopped=executor.provider.terminate(provider_id)
        if stopped.get('provider_id')!=provider_id or stopped.get('terminated') is not True:
            raise ValueError('FIT_MONITOR_TERMINATION_UNVERIFIED')
        write_once(folder/'stopped.json',canonical(stopped))
        reason={'schema':'modal-interruption-cause/v1','segment_id':ident,'provider_id':provider_id,
                'reason':'OBSERVED_TRAINING_STALL','evidence':evidence}
        write_once(folder/'cause.json',canonical(reason))
        from orchestrator.modal_item4_budget import record_interruption
        result=record_interruption(executor.costs,ident,executor.provider,reason_record=folder/'cause.json')
        write_once(folder/'interruption.json',canonical(result))
        return {'status':'INTERRUPTED_CHECKPOINT_PRESERVED','may_launch':False,
                'checkpoint_record_sha256':result['proof']['checkpoint_record_sha256']}
