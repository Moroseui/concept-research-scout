"""Stop a positively failed item4 fit once; preserve its evidence and full cost.

No retry, completed result, refund, cause classification or scientific judgment.
An uncertain termination remains reconciliation-only, as in the fit monitor.
"""
import json
from orchestrator import private_records as pr
from orchestrator.modal_executor import canonical,item4_job
from orchestrator.manual_executor import read,digest
from orchestrator.manual_driver import write_once
from orchestrator.remote_supervisor import lock


@pr.private_umask
def reconcile(executor,job,work,binding,created,observation):
    if item4_job(binding)!=job:raise ValueError('MODAL_FAILURE_JOB_BINDING')
    ident=digest(canonical(binding));provider_id=created['provider_id']
    if created['binding_sha256']!=ident:raise ValueError('MODAL_FAILURE_CREATED_BINDING')
    with lock(work/'failed-cleanup.lock'):
        pr.check_tree(work)
        row=executor.costs.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
        if (row is None or row['provider_id']!=provider_id or row['binding']!=canonical(binding).decode()
                or row['status'] not in {'CREATED','RUNNING','UNCERTAIN'}):
            raise ValueError('MODAL_FAILURE_LEDGER_BINDING')
        path=work/'failed-outcome.json'
        base={'schema':'modal-failed-execution/v1','job':job,'binding_sha256':ident,'provider_id':provider_id}
        if path.exists():
            failure=read(path)
            if (not isinstance(failure,dict) or set(failure)!=set(base)|{'observation'}
                    or any(failure.get(k)!=v for k,v in base.items())):
                raise ValueError('MODAL_FAILURE_SAVED_BINDING')
            if observation is not None and failure['observation']!=observation:
                raise ValueError('MODAL_FAILURE_OBSERVATION_CHANGED')
            observation=failure['observation']
        else:
            failure={**base,'observation':observation}
        if (not isinstance(observation,dict) or observation.get('status')!='FAILED'
                or observation.get('provider_id')!=provider_id or observation.get('binding_sha256')!=ident):
            raise ValueError('MODAL_FAILURE_POSITIVE_OBSERVATION_REQUIRED')
        write_once(path,canonical(failure))
        # The original cost is retained; UNCERTAIN is conservative accounting,
        # not a claim that failed scientific work completed successfully.
        executor.costs.observe(ident,'UNCERTAIN',provider_id)
        executor.block(job,'MODAL_FAILED_EXECUTION_NO_RESUBMISSION')
        intent={'schema':'modal-failed-stop/v1','job':job,'provider_id':provider_id,
                'binding_sha256':ident,'failure_sha256':digest(path.read_bytes())}
        ip=work/'failed-stop-intent.json';receipt=work/'failed-stopped.json'
        result={**observation,'job':job,'may_resubmit':False,'charge':'full reservation retained'}
        if ip.exists():
            if read(ip)!=intent:raise ValueError('MODAL_FAILURE_STOP_INTENT_CHANGED')
            if not receipt.exists():
                return {**result,'cleanup':'STOP_INTENT_RECONCILIATION_REQUIRED'}
        else:
            if receipt.exists():raise ValueError('MODAL_FAILURE_STOP_RECEIPT_WITHOUT_INTENT')
            write_once(ip,canonical(intent))
            stopped=executor.provider.terminate(provider_id)
            if stopped.get('provider_id')!=provider_id or stopped.get('terminated') is not True:
                raise ValueError('MODAL_FAILURE_TERMINATION_UNVERIFIED')
            write_once(receipt,canonical({'intent_sha256':digest(ip.read_bytes()),'receipt':stopped}))
        saved=read(receipt)
        if (set(saved)!={'intent_sha256','receipt'} or saved['intent_sha256']!=digest(ip.read_bytes())
                or saved['receipt'].get('provider_id')!=provider_id or saved['receipt'].get('terminated') is not True):
            raise ValueError('MODAL_FAILURE_TERMINATION_RECEIPT_CHANGED')
        return {**result,'cleanup':'TERMINATED_FAILURE_PRESERVED'}
