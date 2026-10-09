"""One deliberate interruption of the frozen five-epoch base smoke.

Runs immediately after ordinary submission under the existing driver lock.
Only authenticated partial checkpoints qualify; termination has a durable
exclusive intent and is never repeated after an uncertain response.
"""
import json
import math
import re
import time
from orchestrator import private_records as pr, item4_stage1_cap as cap
from orchestrator.manual_executor import digest, read, lock
from orchestrator.manual_driver import write_once
from orchestrator.modal_executor import canonical, item4_job
from orchestrator.modal_fit_progress import encoded

MAX_WAIT_SECONDS=1800
POLL_SECONDS=5
FIT='smoke-A1_repeat'


def require(ok,why):
    if not ok:raise ValueError('DELIBERATE_SMOKE_'+why)


def target(binding):
    scope=binding.get('experiment',{})
    return binding.get('run_id')==cap.RUN and scope.get('fit_id')==FIT and type(scope.get('segment')) is int and scope.get('segment')==1


def scope(binding):
    require(target(binding) and cap.limit(binding)==150000000
        and binding['experiment']['stage']=='SMOKE' and 'resume' not in binding
        and binding['resources']=={'gpu':'B200','cpu':16,'memory_mib':131072,'timeout_seconds':3600},
        'FROZEN_SCOPE')


def partial(proof):
    record=proof.get('checkpoint_record',{});meta=record.get('metadata',{})
    require(proof.get('mode')=='resume' and record.get('key')=='latest'
        and type(meta.get('next_epoch')) is int and 1<=meta['next_epoch']<=4
        and type(meta.get('total_epochs')) is int and meta['total_epochs']==5
        and proof.get('checkpoint_record_sha256')==digest(encoded(record)),
        'PARTIAL_TERMINAL_CHECKPOINT_REQUIRED')


def check_intent(value,ident,pid):
    require(set(value)=={'schema','segment_id','provider_id','observation','observation_sha256','completed_epoch'}
        and value.get('schema')=='deliberate-smoke-stop/v1'
        and value.get('segment_id')==ident and value.get('provider_id')==pid
        and isinstance(value.get('observation'),str)
        and re.fullmatch(r'observation-[0-9]{6}\.json',value['observation']) is not None
        and isinstance(value.get('observation_sha256'),str)
        and re.fullmatch('[0-9a-f]{64}',value['observation_sha256']) is not None
        and type(value.get('completed_epoch')) is int and 1<=value['completed_epoch']<=4,
        'STOP_INTENT_CHANGED')


def ready(observation,ident,pid):
    require(observation.get('schema')=='modal-fit-health/v1'
        and observation.get('provider_id')==pid and observation.get('binding_sha256')==ident
        and observation.get('may_launch') is False,'OBSERVATION_BINDING')
    require(observation.get('status') in {'STARTING','RUNNING'} and
        observation.get('terminal_exit_code') is None,'ALREADY_TERMINAL_RECONCILE')
    if observation['status']=='STARTING':return False
    cp=observation.get('checkpoint',{});log=observation.get('log',{})
    require(cp.get('key')=='latest' and type(cp.get('total_epochs')) is int
        and cp['total_epochs']==5 and type(cp.get('next_epoch')) is int
        and 0<=cp['next_epoch']<5 and log.get('training_done') is False,'WINDOW_OR_METADATA_CHANGED')
    return cp['next_epoch']>=1


@pr.private_umask
def run(driver,value,job,executor):
    """No admission or launch here; the existing executor already submitted."""
    with lock(executor.path.parent/'modal-executor.lock'):
        executor._guard()
        record=executor.get(job['job']);binding=json.loads(record['binding']);scope(binding)
        ident=digest(canonical(binding));work=executor._paths(job['job'])
        require(item4_job(binding)==job['job'] and driver.config['run_id']==binding['run_id']
            and value['phase']=='EXECUTE_EXPERIMENT','OWNER')
        saved=value['fit_dispatch'][job['job']]
        raw=pr.check(driver.state/'fit-packages'/job['job']/'prepared/manifest.json').read_bytes()
        require(digest(raw)==saved['manifest_sha256'] and json.loads(raw)['binding']==binding,
            'PREPARED_BINDING')
        created=read(work/'created.json');pid=created['provider_id']
        require(created['binding_sha256']==ident,'CREATED_BINDING')
        row=executor.costs.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
        require(row is not None and row['binding']==canonical(binding).decode()
            and row['provider_id']==pid and row['status'] in {'RUNNING','ACCOUNTED'},'LEDGER_BINDING')
        folder=work/'deliberate-stop';pr.mkdir(folder,exist_ok=True)
        intent=folder/'stop-intent.json';stopped=folder/'stopped.json';cause=folder/'cause.json'
        if intent.exists():
            old=read(intent)
            check_intent(old,ident,pid)
            require(stopped.is_file(),'STOP_INTENT_RECONCILIATION_REQUIRED')
        else:
            require(row['status']=='RUNNING' and not stopped.exists() and not cause.exists(),
                'UNEXPECTED_TERMINAL_RECORD')
            watch=folder/'watch.json'
            if watch.exists():
                watched=read(watch)
                require(watched.get('segment_id')==ident and watched.get('provider_id')==pid
                    and set(watched)=={'segment_id','provider_id','started_at','deadline'}
                    and all(type(watched[k]) in (int,float) and math.isfinite(watched[k]) for k in ('started_at','deadline'))
                    and watched['deadline']-watched['started_at']==MAX_WAIT_SECONDS,'WATCH_CHANGED')
            else:
                now=time.time();watched={'segment_id':ident,'provider_id':pid,
                    'started_at':now,'deadline':now+MAX_WAIT_SECONDS}
                write_once(watch,canonical(watched))
            count=len(list(folder.glob('observation-*.json')))
            while True:
                executor._guard()
                require(watched['started_at']<=time.time()<watched['deadline'],'DEADLINE_RECONCILE')
                count+=1;path=folder/('observation-'+str(count).zfill(6)+'.json')
                try:observation=executor.provider.fit_health(pid,binding)
                except ValueError:raise # content/binding violations remain refusals
                except Exception as error:
                    write_once(path,canonical({'error_type':type(error).__name__,'at':time.time(),
                        'meaning':'observation unavailable; no stop or execution inference'}))
                    time.sleep(POLL_SECONDS);continue
                write_once(path,canonical(observation))
                if ready(observation,ident,pid):
                    # Checkpoint is durably committed; final payload hash is
                    # verified after positive termination, before any resume.
                    executor._guard()
                    write_once(intent,canonical({'schema':'deliberate-smoke-stop/v1',
                        'segment_id':ident,'provider_id':pid,'observation':path.name,
                        'observation_sha256':digest(path.read_bytes()),
                        'completed_epoch':observation['checkpoint']['next_epoch']}))
                    result=executor.provider.terminate(pid)
                    require(result.get('provider_id')==pid and result.get('terminated') is True,
                        'TERMINATION_UNVERIFIED')
                    write_once(stopped,canonical(result));break
                time.sleep(POLL_SECONDS)
        old=read(intent);check_intent(old,ident,pid);termination=read(stopped)
        require(termination.get('provider_id')==pid and termination.get('terminated') is True,
            'STOP_RECEIPT_CHANGED')
        observed=pr.check(folder/old['observation']).read_bytes()
        observation=json.loads(observed)
        require(digest(observed)==old['observation_sha256'] and ready(observation,ident,pid)
            and observation['checkpoint']['next_epoch']==old['completed_epoch'],
            'STOP_OBSERVATION_CHANGED')
        reason={'schema':'modal-interruption-cause/v1','segment_id':ident,'provider_id':pid,
            'reason':'DELIBERATE_SMOKE_INTERRUPTION','evidence':{
                'stop_intent_sha256':digest(intent.read_bytes()),'termination_sha256':digest(stopped.read_bytes()),
                'checkpoint_observation_sha256':old['observation_sha256']}}
        write_once(cause,canonical(reason))
        executor._guard()
        proof=executor.provider.terminal_fit_checkpoint(pid,binding);partial(proof)
        from orchestrator.modal_item4_budget import record_interruption
        result=record_interruption(executor.costs,ident,executor.provider,reason_record=cause,
            expected_checkpoint_sha256=proof['checkpoint_record_sha256'])
        partial(result['proof'])
        write_once(folder/'interruption.json',canonical(result))
        saved.update(phase='INTERRUPTED',deliberate_stop_sha256=digest(canonical(result)))
        driver.save(value)
        return {**driver.status(),'next_action':'RECONCILE_FIT_CONTINUATION',
            'execution_wait':'Real deliberate interruption and partial checkpoint verified; ordinary continuation required.',
            'epoch_resumed_from':result['proof']['checkpoint_record']['metadata']['next_epoch']}
