"""One accounted fit transition per driver tick; no scientific implementation here.

The root-preserved runtime selection is produced after preprocessing. It binds
existing assets to the exact reviewed scientific package and frozen fit list.
Missing preparation is a visible wait, never a fallback to another experiment.
"""
import json
from pathlib import Path
from orchestrator import experiment_package, experiment_modal_package as bridge
from orchestrator import private_records as pr
from orchestrator.manual_host_guard import trusted
from orchestrator.manual_executor import digest
from orchestrator.review_contract import strict_json
from orchestrator.modal_executor import ModalExecutor, canonical, item4_job
from orchestrator.modal_provider import ModalProvider
from orchestrator.modal_assets import prepare_package
from orchestrator.experiment_plan_validation import validate_fits


def checked_ref(ref):
    if (not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}
            or not isinstance(ref['path'], str) or not Path(ref['path']).is_absolute()):
        raise ValueError('EXPERIMENT_RUNTIME_REFERENCE')
    path = trusted(Path(ref['path']))
    pr.check(path)
    raw = path.read_bytes()
    if digest(raw) != ref['sha256']:
        raise ValueError('EXPERIMENT_RUNTIME_REFERENCE_CHANGED')
    return strict_json(raw)


def load(driver, value):
    sealed = experiment_package.verify(driver, value, driver.state/'experiment-package')
    if sealed['selection']['item_number'] != 4:
        raise ValueError('EXPERIMENT_MODAL_ITEM4_ONLY')
    directory = driver.config.get('execution_provisioning')
    if not directory:
        return None
    root = pr.check(trusted(Path(directory)))
    if not root.is_dir(): raise ValueError('EXPERIMENT_RUNTIME_DIRECTORY')
    from orchestrator import experiment_waves as waves
    if waves.enabled(driver):
        selected=waves.read(driver,value,root,'fit')['selected']
        if selected is None:return None
        from orchestrator.experiment_continuation import resolve
        from orchestrator.item4_fit_transport_recovery import resolve as fit_recovery
        return fit_recovery(driver,value,resolve(driver,value,selected))
    if value.get('fit_selection_waves'):raise ValueError('EXPERIMENT_INCREMENTAL_PLAN_REQUIRED')
    path = root/'READY.json'
    if not path.exists(): return None
    pr.check(trusted(path))
    raw = path.read_bytes()
    selected = validate_selection(driver, value, raw)
    from orchestrator.experiment_continuation import resolve
    from orchestrator.item4_fit_transport_recovery import resolve as fit_recovery
    return fit_recovery(driver,value,resolve(driver,value,selected))




def validate_selection(driver, value, raw, *, partial=False):
    """Same exact selection checks before root publication and on every tick.

    Caller verifies the genuine scientific package; this pure half checks its
    selected fits and root-owned runtime references without admitting a job.
    """
    selected = strict_json(raw)
    expected = {'schema':'experiment-fit-dispatch/v1', 'source':driver.config['source'],
        'run_id':driver.config['run_id'], 'package_manifest_sha256':digest((driver.state/'experiment-package/manifest.json').read_bytes())}
    if (not isinstance(selected, dict) or set(selected) != set(expected)|{'jobs'}
            or any(selected.get(k) != v for k,v in expected.items())
            or not isinstance(selected['jobs'], list) or not selected['jobs']):
        raise ValueError('EXPERIMENT_DISPATCH_BINDING')
    old = value.get('dispatch_sha256')
    if not partial and old is not None and old != digest(raw):
        raise ValueError('EXPERIMENT_DISPATCH_SELECTION_CHANGED')
    plan = strict_json((driver.state/'experiment-package/execution-plan.json').read_bytes())
    from orchestrator import experiment_waves as waves
    if partial and not waves.enabled(driver):raise ValueError('EXPERIMENT_INCREMENTAL_PLAN_REQUIRED')
    fits = validate_fits(plan, incremental=waves.enabled(driver))
    from orchestrator.experiment_result import selected as result_selection
    jobs = []; seen = set(); identities = []
    for row in selected['jobs']:
        if not isinstance(row, dict) or set(row) != {'runtime', 'binding'}:
            raise ValueError('EXPERIMENT_DISPATCH_JOB_FIELDS')
        runtime = checked_ref(row['runtime']); binding = row['binding']
        if (not isinstance(binding, dict) or binding.get('source') != expected['source']
                or binding.get('run_id') != expected['run_id']
                or binding.get('runtime_sha256') != digest(canonical(runtime))
                or runtime.get('batch_ledger') != driver.config['batch_ledger']):
            raise ValueError('EXPERIMENT_DISPATCH_RUNTIME_BINDING')
        job = item4_job(binding)
        if job in seen: raise ValueError('EXPERIMENT_DUPLICATE_FIT_SEGMENT')
        seen.add(job)
        scope = binding['experiment']; fit = binding.get('progress', {}).get('fit_binding', {})
        identity = {k:fit.get(k) for k in ('arm', 'fold', 'realization')}
        if type(fit.get('fold')) is not int: raise ValueError('EXPERIMENT_RUNTIME_FOLD_TYPE')
        identity.update(fit_id=scope['fit_id'], stage=scope['stage'], outputs=binding.get('outputs'))
        result = result_selection(plan, binding)
        identity['validation_checks'] = result['validation_checks']
        if 'preprocessing_id' in result:
            identity['preprocessing_id']=result['preprocessing_id']
            known={p['id'] for p in plan.get('preprocessing',[])}
            if result['preprocessing_id'] not in known:raise ValueError('EXPERIMENT_FIT_PREPROCESSING_ID')
        identities.append(identity)
        # Segmented recovery is separately represented by the existing executor
        # and its terminal checkpoint proof. Initial dispatch cannot manufacture it.
        if scope['segment'] != 1 or 'resume' in binding:
            raise ValueError('EXPERIMENT_INITIAL_DISPATCH_ONLY')
        jobs.append({'job':job, 'runtime':runtime, 'binding':binding})
    required=[f for f in fits if f['fit_id'] in {i['fit_id'] for i in identities}] if partial else fits
    if identities != required:
        raise ValueError('EXPERIMENT_DISPATCH_FROZEN_FITS_CHANGED')
    return {'sha256':digest(raw), 'jobs':jobs}


def executor(driver, job):
    factory = getattr(driver, 'provider_factory', None) or ModalProvider
    provider = factory(job['runtime'])
    return ModalExecutor(driver.state/'jobs.sqlite', job['runtime'], provider, driver.store.batch)


@pr.private_umask
def advance(driver, value):
    from orchestrator import experiment_preprocessing_dispatch as preprocessing
    selected = load(driver, value)
    if selected is None:
        pending=preprocessing.advance(driver,value)
        if pending is not None:return pending
        return {**driver.status(), 'execution_wait':'Validated preprocessing and bound runtime selection are not ready.',
                'provider_called':False, 'next_action':'WAIT_EXECUTION_PREPARATION'}
    preprocessing.bind_fits(driver,value,selected)
    value['dispatch_sha256'] = selected['sha256']
    if 'wave_pins' in selected:value['fit_selection_waves']=selected['wave_pins']
    states = value.setdefault('fit_dispatch', {})
    if (not isinstance(states, dict) or set(states)-set(selected.get('all_jobs',[j['job'] for j in selected['jobs']]))
            or any(not isinstance(v, dict) or v.get('phase') not in {'PREPARE','UPLOAD','SUBMIT','RUNNING','INTERRUPTED','COMPLETE'}
                   for v in states.values())):
        raise ValueError('EXPERIMENT_DISPATCH_STATE')
    # Observe each running fit before the next launch; unavailable observation
    # never becomes a stopped fit or a fresh realization.
    for job in selected['jobs']:
        saved = states.get(job['job'], {})
        if saved.get('phase') == 'INTERRUPTED':
            from orchestrator.experiment_continuation import schedule
            return schedule(driver,value,job)
        if saved.get('phase') != 'RUNNING': continue
        store = executor(driver, job)
        try:
            observed = store.remote_status(job['job'])
            if observed['status']=='RUNNING':
                health = store.monitor_fit(job['job'])
                saved['health'] = health
                if health['status']=='INTERRUPTED_CHECKPOINT_PRESERVED':
                    saved['phase']='INTERRUPTED'
                    driver.save(value)
                    return {**driver.status(),'next_action':'RECONCILE_FIT_CONTINUATION',
                            'execution_wait':'Verified checkpoint preserved; a bound continuation is required.'}
                if health['status']=='STOP_INTENT_RECONCILIATION_REQUIRED':
                    driver.save(value)
                    raise ValueError('EXPERIMENT_STOP_INTENT_RECONCILIATION_REQUIRED')
        finally: store.db.close()
        saved['observation'] = observed
        if observed['status'] == 'COMPLETE': saved['phase'] = 'COMPLETE'
        elif observed['status'] == 'FAILED':
            driver.save(value)
            raise ValueError('EXPERIMENT_FIT_FAILED_RECONCILE')
        elif observed['status'] not in {'RUNNING', 'UNKNOWN', 'OBSERVATION_UNAVAILABLE'}:
            driver.save(value)
            raise ValueError('EXPERIMENT_FIT_UNRESOLVED_NO_RESUBMISSION')
    if 'wave_pins' in selected:
        from orchestrator.experiment_collection import collect_ready
        if collect_ready(driver,value,selected):
            return {**driver.status(),'next_action':'COLLECTED_FIT_RESULT','provider_called':True}
    # Check running fits before preprocessing or another fit consumes this tick.
    pending=preprocessing.advance(driver,value)
    if pending is not None and pending.get('next_action')!='WAIT_PREPROCESSING_PREPARATION':return pending
    for job in selected['jobs']:
        saved = states.setdefault(job['job'], {'phase':'PREPARE'})
        folder = driver.state/'fit-packages'/job['job']
        if saved['phase'] == 'PREPARE':
            pr.mkdir(folder, parents=True, exist_ok=True)
            manifest = bridge.emit(driver, value, folder/'prepared', job['binding'])
            saved.update(phase='UPLOAD', manifest_sha256=digest(canonical(manifest)))
            driver.save(value); return driver.status()
        if saved['phase'] not in {'UPLOAD', 'SUBMIT'}: continue
        manifest = bridge.emit(driver, value, folder/'prepared', job['binding'])
        if saved['manifest_sha256'] != digest(canonical(manifest)):
            raise ValueError('EXPERIMENT_DISPATCH_PACKAGE_CHANGED')
        store = executor(driver, job)
        try:
            if saved['phase'] == 'UPLOAD':
                ready = prepare_package(store.provider, manifest['binding'], folder/'prepared', folder/'upload')
                if (ready.get('status') != 'READY' or ready.get('manifest_sha256') != saved['manifest_sha256']
                        or ready.get('volume_id') != job['runtime']['package_volume_id']):
                    raise ValueError('EXPERIMENT_UPLOAD_BINDING')
                saved['phase'] = 'SUBMIT'
            else:
                result = store.submit(job['job'], manifest['binding'], folder/'prepared', folder/'submitted')
                saved['observation'] = result
                if result['status'] == 'WAIT_PROVIDER_HEADROOM':
                    driver.save(value); return {**driver.status(), 'execution_wait':result}
                if result['status'] not in {'SUBMITTED', 'RUNNING', 'COMPLETE'}:
                    driver.save(value)
                    raise ValueError('EXPERIMENT_SUBMISSION_UNRESOLVED_NO_RETRY')
                saved['phase'] = 'COMPLETE' if result['status']=='COMPLETE' else 'RUNNING'
        finally: store.db.close()
        driver.save(value); return driver.status()
    if all(states[j['job']]['phase']=='COMPLETE' for j in selected['jobs']):
        if not selected.get('complete_selection',True):
            driver.save(value)
            return {**driver.status(),'next_action':'WAIT_REMAINING_FIT_SELECTION',
                    'execution_wait':'Published fits finished; remaining frozen fits need their runtime and gates.',
                    'provider_called':False}
        # Execution completion is not validation or scientific acceptance.
        value['phase'] = 'COLLECT_EXPERIMENT'
    driver.save(value)
    return driver.status()
