"""Driver-owned preprocessing on the existing reviewed package and compute lane.

Preprocessing is a prerequisite, never a completed fit or scientific result.
Root selects the runtime once; ordinary driver ticks upload, admit, observe and
collect without granting another allowance or interpreting an uncertain attempt.
"""
from pathlib import Path
from types import SimpleNamespace
from orchestrator import private_records as pr, experiment_package
from orchestrator import experiment_dispatch as dispatch, experiment_modal_package as bridge
from orchestrator import modal_preprocessing_provider as provider
from orchestrator.experiment_preprocessing import scope as scientific_scope
from orchestrator.manual_executor import digest, inventory
from orchestrator.modal_executor import canonical, item4_job
from orchestrator.review_contract import strict_json

SCHEMA='experiment-preprocessing-dispatch/v1'


def directory(config):
    root=Path(config['execution_provisioning'])
    if not root.is_absolute() or root==root.parent:raise ValueError('EXPERIMENT_RUNTIME_DIRECTORY')
    return root.with_name(root.name+'-preprocessing')


def frozen(driver):
    plan=strict_json((driver.state/'experiment-package/execution-plan.json').read_bytes())
    rows=plan.get('preprocessing')
    if rows is None:return []
    if (not isinstance(rows,list) or not rows or any(not isinstance(r,dict) or not isinstance(r.get('id'),str) for r in rows)
            or len({r.get('id') for r in rows})!=len(rows)):
        raise ValueError('EXPERIMENT_PREPROCESSING_PLAN')
    return rows


def inputs(job):
    records=job['runtime']['item4_preprocessing_assets']['source_records']
    # Original source pins are validated by the existing authenticated readers.
    files=provider.input_files(job['runtime'],job['binding'])
    return {'cohort.json':pr.check(records['cohort']).read_bytes(),
            'input-inventory.json':canonical(files)}


def validate_selection(driver,value,raw,*,partial=False):
    selected=strict_json(raw)
    expected={'schema':SCHEMA,'source':driver.config['source'],'run_id':driver.config['run_id'],
        'package_manifest_sha256':digest((driver.state/'experiment-package/manifest.json').read_bytes())}
    if (not isinstance(selected,dict) or set(selected)!=set(expected)|{'jobs'}
            or any(selected.get(k)!=v for k,v in expected.items())
            or not isinstance(selected['jobs'],list) or not selected['jobs']):
        raise ValueError('EXPERIMENT_PREPROCESSING_SELECTION')
    if not partial and value.get('preprocessing_selection_sha256',digest(raw))!=digest(raw):
        raise ValueError('EXPERIMENT_PREPROCESSING_SELECTION_CHANGED')
    plan=strict_json((driver.state/'experiment-package/execution-plan.json').read_bytes())
    from orchestrator import experiment_waves as waves
    if partial and not waves.enabled(driver):raise ValueError('EXPERIMENT_INCREMENTAL_PLAN_REQUIRED')
    expected_steps=frozen(driver);steps=[];jobs=[];seen=set()
    for row in selected['jobs']:
        if not isinstance(row,dict) or set(row)!={'runtime','binding'}:
            raise ValueError('EXPERIMENT_DISPATCH_JOB_FIELDS')
        runtime=dispatch.checked_ref(row['runtime']);binding=row['binding']
        if (not isinstance(binding,dict) or binding.get('source')!=driver.config['source']
                or binding.get('run_id')!=driver.config['run_id']
                or binding.get('runtime_sha256')!=digest(canonical(runtime))
                or runtime.get('batch_ledger')!=driver.config['batch_ledger']
                or any(k in binding for k in ('execution','spec_sha256','review_sha256','execution_plan_sha256','code_sha256'))):
            raise ValueError('EXPERIMENT_DISPATCH_RUNTIME_BINDING')
        adapter=SimpleNamespace(config=runtime)
        assets=provider.scope(adapter,runtime,binding);provider.environment_scope(adapter,binding)
        for path in assets['source_records'].values():pr.check(dispatch.trusted(Path(path)))
        if binding['experiment']['segment']!=1 or 'resume' in binding:
            raise ValueError('EXPERIMENT_INITIAL_DISPATCH_ONLY')
        job={'job':item4_job(binding),'runtime':runtime,'binding':binding}
        files=inputs(job)
        scientific_scope(binding,plan,files['cohort.json'])
        if job['job'] in seen:raise ValueError('EXPERIMENT_DUPLICATE_PREPROCESSING')
        seen.add(job['job']);jobs.append(job)
        # scientific_scope already checked exact declared-to-native equality.
        # Selection membership/order is compared using the immutable plan row.
        steps.append(next(step for step in expected_steps
                          if step['id'] == binding['preprocessing']['id']))
    required=[s for s in expected_steps if s['id'] in {x['id'] for x in steps}] if partial else expected_steps
    if steps!=required:raise ValueError('EXPERIMENT_PREPROCESSING_FROZEN_SELECTION')
    return {'sha256':digest(raw),'jobs':jobs}


def load(driver,value):
    if not frozen(driver):return None
    folder=directory(driver.config)
    if folder.exists() or folder.is_symlink():pr.check(dispatch.trusted(folder))
    from orchestrator import experiment_waves as waves
    if waves.enabled(driver):
        selected=waves.read(driver,value,folder,'preprocessing')['selected']
        if selected is None:return None
        from orchestrator.preprocessing_continuation import resolve
        return resolve(driver,value,selected)
    if value.get('preprocessing_selection_waves'):raise ValueError('EXPERIMENT_INCREMENTAL_PLAN_REQUIRED')
    path=folder/'READY.json'
    if not path.exists():
        if path.is_symlink():raise ValueError('EXPERIMENT_RUNTIME_REFERENCE')
        return None
    raw=pr.check(dispatch.trusted(path)).read_bytes()
    from orchestrator.preprocessing_continuation import resolve
    return resolve(driver,value,validate_selection(driver,value,raw))


def package(driver,value,job):
    folder=driver.state/'preprocessing-packages'/job['job']
    pr.mkdir(folder,parents=True,exist_ok=True)
    manifest=bridge.emit(driver,value,folder/'prepared',job['binding'],preprocessing_inputs=inputs(job))
    return folder,manifest


def saved_collection(driver,job,saved):
    folder=driver.state/'preprocessing-packages'/job['job']
    raw=pr.check(folder/'prepared/manifest.json').read_bytes();manifest=strict_json(raw)
    if saved.get('manifest_sha256')!=digest(raw):raise ValueError('EXPERIMENT_DISPATCH_PACKAGE_CHANGED')
    from orchestrator.modal_executor import verify_package
    verify_package(folder/'prepared',manifest['binding'])
    derived=manifest['binding'];removed={'execution','spec_sha256','review_sha256','execution_plan_sha256','code_sha256'}
    if {k:v for k,v in derived.items() if k not in removed}!=job['binding']:
        raise ValueError('EXPERIMENT_PREPARATION_RUNTIME_CHANGED')
    destination=folder/'collected'
    result=provider.validate_collection(job['runtime'],derived,destination)
    if saved.get('collection_sha256')!=digest(canonical(result['file_sha256'])):
        raise ValueError('EXPERIMENT_PREPROCESSING_COLLECTION_CHANGED')
    row=driver.store.db.execute('SELECT manifest FROM manual_collections WHERE job=?',(job['job'],)).fetchone()
    if row is None or strict_json(row['manifest'])!=result['file_sha256']:
        raise ValueError('EXPERIMENT_PREPROCESSING_COLLECTION_NOT_RECORDED')
    return {'binding_sha256':digest(canonical(derived)),'files':result['file_sha256'],
            'volume_id':derived['preprocessing_output_volume_id'],'folder':str(destination)}


@pr.private_umask
def advance(driver,value):
    if not frozen(driver):return None
    experiment_package.verify(driver,value,driver.state/'experiment-package')
    selected=load(driver,value)
    if selected is None:
        return {**driver.status(),'next_action':'WAIT_PREPROCESSING_PREPARATION','provider_called':False,
            'execution_wait':'Reviewed preprocessing runtime selection is not ready.'}
    value['preprocessing_selection_sha256']=selected['sha256']
    if 'wave_pins' in selected:value['preprocessing_selection_waves']=selected['wave_pins']
    states=value.setdefault('preprocessing_dispatch',{})
    jobs={j['job']:j for j in selected['jobs']}
    if (not isinstance(states,dict) or set(states)-set(selected.get('all_jobs',jobs))
            or any(not isinstance(v,dict) or v.get('phase') not in {'PREPARE','UPLOAD','SUBMIT','RUNNING','COLLECT','COMPLETE','INTERRUPTED'} for v in states.values())):
        raise ValueError('EXPERIMENT_PREPROCESSING_STATE')
    # One transition per tick. Never apply training health/checkpoint semantics
    # to CPU preprocessing or infer success from a missing remote process.
    for job in selected['jobs']:
        saved=states.setdefault(job['job'],{'phase':'PREPARE'})
        if saved['phase']=='INTERRUPTED':
            from orchestrator.preprocessing_continuation import schedule
            return schedule(driver,value,job)
        if saved['phase']=='COMPLETE':saved_collection(driver,job,saved);continue
        folder,manifest=package(driver,value,job)
        if saved['phase']=='PREPARE':
            saved.update(phase='UPLOAD',manifest_sha256=digest(canonical(manifest)))
            driver.save(value);return driver.status()
        if saved.get('manifest_sha256')!=digest(canonical(manifest)):
            raise ValueError('EXPERIMENT_DISPATCH_PACKAGE_CHANGED')
        if saved['phase']=='RUNNING':
            ident=digest(canonical(manifest['binding']))
            event=driver.store.batch.db.execute('SELECT payload FROM events WHERE id=?',
                (ident+':preprocessing-interruption',)).fetchone()
            if event is not None:
                # Recover a crash after the owner ledger commit but before
                # saving lane state; do not overwrite terminal accounting by
                # observing the already-reconciled process again.
                from orchestrator.preprocessing_continuation import terminal
                terminal(driver,value,job)
                saved['phase']='INTERRUPTED';driver.save(value)
                return {**driver.status(),'next_action':'RECONCILE_PREPROCESSING_CONTINUATION',
                        'provider_called':False}
        store=dispatch.executor(driver,job)
        try:
            if saved['phase']=='UPLOAD':
                ready=dispatch.prepare_package(store.provider,manifest['binding'],folder/'prepared',folder/'upload')
                if (ready.get('status')!='READY' or ready.get('manifest_sha256')!=saved['manifest_sha256']
                        or ready.get('volume_id')!=job['runtime']['package_volume_id']):
                    raise ValueError('EXPERIMENT_UPLOAD_BINDING')
                saved['phase']='SUBMIT'
            elif saved['phase']=='SUBMIT':
                observed=store.submit(job['job'],manifest['binding'],folder/'prepared',folder/'submitted')
                saved['observation']=observed
                if observed['status']=='WAIT_PROVIDER_HEADROOM':
                    driver.save(value);return {**driver.status(),'execution_wait':observed}
                if observed['status'] not in {'SUBMITTED','RUNNING','COMPLETE'}:
                    driver.save(value);raise ValueError('EXPERIMENT_SUBMISSION_UNRESOLVED_NO_RETRY')
                saved['phase']='COLLECT' if observed['status']=='COMPLETE' else 'RUNNING'
            elif saved['phase']=='RUNNING':
                observed=store.remote_status(job['job']);saved['observation']=observed
                if observed['status']=='COMPLETE':saved['phase']='COLLECT'
                elif observed['status']=='FAILED':
                    driver.save(value);raise ValueError('EXPERIMENT_PREPROCESSING_FAILED_RECONCILE')
                elif observed['status'] not in {'RUNNING','UNKNOWN','OBSERVATION_UNAVAILABLE'}:
                    driver.save(value);raise ValueError('EXPERIMENT_PREPROCESSING_UNRESOLVED_NO_RESUBMISSION')
            elif saved['phase']=='COLLECT':
                result=store.collect_remote(job['job'],folder/'prepared',folder/'collected',
                    lambda target:provider.validate_collection(job['runtime'],manifest['binding'],target))
                if result.get('status')!='VALID':
                    saved['observation']=result;driver.save(value)
                    if result.get('status') not in {'RUNNING','UNKNOWN','OBSERVATION_UNAVAILABLE'}:
                        raise ValueError('EXPERIMENT_PREPROCESSING_FAILED_RECONCILE')
                    return {**driver.status(),'execution_wait':result}
                saved.update(phase='COMPLETE',collection_sha256=digest(canonical(result['file_sha256'])))
        finally:store.db.close()
        driver.save(value)
        # A live preprocessing observation must not starve independent fits.
        if saved['phase']=='RUNNING' and selected.get('wave_pins') and saved.get('observation',{}).get('status') in {'RUNNING','UNKNOWN','OBSERVATION_UNAVAILABLE'}:
            continue
        return driver.status()
    # Fit preparation is separate and must consume these exact original records.
    return None


def bind_fits(driver,value,selected):
    if not frozen(driver):return
    pre=load(driver,value)
    if pre is None:raise ValueError('EXPERIMENT_PREPROCESSING_REQUIRED')
    from orchestrator import experiment_waves as waves
    incremental=waves.enabled(driver)
    plan=waves.plan(driver)
    dependencies={row['fit_id']:row.get('preprocessing_id') for row in plan['fits']}
    required={dependencies[j['binding']['experiment']['fit_id']] for j in selected['jobs']} if incremental else None
    known={}
    for job in pre['jobs']:
        if required is not None and job['binding']['preprocessing']['id'] not in required:continue
        saved=value.get('preprocessing_dispatch',{}).get(job['job'],{})
        if saved.get('phase')!='COMPLETE':raise ValueError('EXPERIMENT_PREPROCESSING_REQUIRED')
        receipt=saved_collection(driver,job,saved)
        receipt['preprocessing_id']=job['binding']['preprocessing']['id']
        known[receipt['binding_sha256']]=receipt
    for fit in selected['jobs']:
        assets=fit['runtime'].get('item4_assets',{});pin=assets.get('preprocessing_job_sha256')
        receipt=known.get(pin)
        if (receipt is None or (incremental and receipt['preprocessing_id']!=dependencies[fit['binding']['experiment']['fit_id']])
                or fit['binding'].get('preprocessing_job_sha256')!=pin
                or assets.get('preprocessed_volume_id')!=receipt['volume_id']
                or assets.get('preprocessing_sha256')!=receipt['files']['preprocessing.json']):
            raise ValueError('EXPERIMENT_FIT_PREPROCESSING_CONNECTION')
        for field,name in [('item4_preprocessing_validation','validation.json'),('item4_preprocessing_execution','result.json')]:
            ref=fit['runtime'].get(field)
            if (not isinstance(ref,dict) or ref.get('sha256')!=receipt['files'][name]):
                raise ValueError('EXPERIMENT_FIT_PREPROCESSING_CONNECTION')
            dispatch.checked_ref(ref)
