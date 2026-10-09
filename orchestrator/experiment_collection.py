"""Collect reviewed aggregate fit returns into the actual interpretation route.

One collection per tick; provider status is not scientific acceptance. Originals,
per-file hashes, validation and package identities stay available to both roles.
"""
import json
from pathlib import Path
from orchestrator import experiment_dispatch as dispatch, experiment_result as results
from orchestrator import private_records as pr
from orchestrator.experiment_continuation import complete_states
from orchestrator.manual_executor import digest
from orchestrator.manual_driver import write_once
from orchestrator.modal_executor import canonical
from orchestrator.git_publication import scan


def artifact(driver, value, kind, ident, name, raw):
    scan('context/current.txt', raw)
    relative='current/runs/'+digest(driver.config['run_id'].encode())+'/results/'+name
    write_once(driver.context/relative, raw)
    row={'id':ident,'type':kind,'version':1,'path':relative,'sha256':digest(raw)}
    old=[r for r in value['artifacts'] if r['id']==ident]
    if old and old != [row]: raise ValueError('EXPERIMENT_DELIVERY_CHANGED')
    if not old: value['artifacts'].append(row)


@pr.private_umask
def collect_ready(driver,value,selected):
    """Collect one completed fit while other frozen fits are pending.

    This preserves validated aggregate originals for benchmark/projection use;
    it never delivers a final interpretation or calls them scientifically accepted.
    """
    states=value.get('fit_dispatch',{})
    plan=results.strict((driver.state/'experiment-package/execution-plan.json').read_bytes())
    received=value.setdefault('fit_collections',{})
    if not isinstance(received,dict) or set(received)-{job['job'] for job in selected['jobs']}:
        raise ValueError('EXPERIMENT_COLLECTION_STATE')
    evidence_pins=value.setdefault('fit_collection_receipts',{})
    if not isinstance(evidence_pins,dict) or set(evidence_pins)!=set(received):
        raise ValueError('EXPERIMENT_COLLECTION_RECEIPT_STATE')
    for job in selected['jobs']:
        if states.get(job['job'],{}).get('phase')!='COMPLETE':continue
        ident=job['job'];folder=driver.state/'fit-packages'/ident
        manifest=dispatch.bridge.emit(driver,value,folder/'prepared',job['binding'])
        if digest(canonical(manifest)) != states[ident]['manifest_sha256']:
            raise ValueError('EXPERIMENT_COLLECTION_PACKAGE_CHANGED')
        destination=driver.state/'fit-results'/ident
        def validate(path):
            return {'status':'VALID','scientific_validation':results.validate(path,manifest['binding'],plan)}
        if ident in received:
            receipt=validate(destination)['scientific_validation']
            if receipt != received[ident]: raise ValueError('EXPERIMENT_SAVED_VALIDATION_CHANGED')
            continue
        pr.mkdir(destination.parent,parents=True,exist_ok=True)
        executor=dispatch.executor(driver,job)
        try:
            collected=executor.collect_remote(ident,folder/'prepared',destination,validate)
            native=pr.check(executor._paths(ident)/'collection-receipt.json').read_bytes()
            if results.strict(native).get('binding_sha256') != digest(canonical(manifest['binding'])):
                raise ValueError('EXPERIMENT_COLLECTION_RECEIPT_BINDING')
        finally: executor.db.close()
        if collected.get('status')!='VALID':
            raise ValueError('EXPERIMENT_COLLECTION_REFUSED')
        receipt=validate(destination)['scientific_validation']
        if collected.get('scientific_validation') != receipt:
            raise ValueError('EXPERIMENT_COLLECTION_VALIDATION_CHANGED')
        write_once(driver.state/'fit-validation'/(ident+'.json'),canonical(receipt))
        received[ident]=receipt
        evidence_pins[ident]=digest(native)
        driver.save(value)
        return True
    return False


@pr.private_umask
def advance(driver, value):
    selected=dispatch.load(driver,value)
    if selected is None or value.get('dispatch_sha256') != selected['sha256']:
        raise ValueError('EXPERIMENT_COLLECTION_SELECTION')
    states=value.get('fit_dispatch',{})
    if not selected.get('complete_selection',True) or not complete_states(selected,states):
        raise ValueError('EXPERIMENT_COLLECTION_NOT_COMPLETE')
    if collect_ready(driver,value,selected):return driver.status()
    received=value['fit_collections'];evidence_pins=value['fit_collection_receipts']
    # All actual returned bytes have passed remote and local checks. Keep each
    # original in a hash-checked workspace file, rather than concatenating tables
    # or old execution transcripts into the initial context.
    records=[];packages=[]
    for job in selected['jobs']:
        ident=job['job'];receipt=received[ident];folder=driver.state/'fit-results'/ident
        for name,pin in receipt['files'].items():
            raw=pr.check(folder/name).read_bytes()
            if digest(raw)!=pin['sha256'] or len(raw)!=pin['bytes']:
                raise ValueError('EXPERIMENT_DELIVERY_FILE_CHANGED')
            artifact(driver,value,'validation_result' if name=='validation.json' else 'result_tables',
                'experiment-result-'+ident+'-'+name,ident+'/'+name,raw)
        # ModalExecutor owns the authentic receipt location. Read via _paths,
        # without constructing a provider or making a new observation.
        from orchestrator.modal_executor import ModalExecutor
        work=ModalExecutor._paths(driver.store,ident)
        raw=pr.check(work/'collection-receipt.json').read_bytes();native=results.strict(raw)
        if digest(raw)!=evidence_pins[ident]:
            raise ValueError('EXPERIMENT_COLLECTION_RECEIPT_CHANGED')
        if native.get('file_sha256') != {name:item['sha256'] for name,item in receipt['files'].items()}:
            raise ValueError('EXPERIMENT_COLLECTION_RECEIPT_CHANGED')
        records.append({'fit_id':job['binding']['experiment']['fit_id'],
            'collection_receipt_sha256':digest(raw), 'validation_sha256':digest(canonical(receipt)),
            'files':receipt['files'], 'scientifically_accepted':False})
        package=driver.state/'fit-packages'/ident/'prepared/manifest.json'
        packages.append({'fit_id':job['binding']['experiment']['fit_id'],
            'manifest_sha256':digest(pr.check(package).read_bytes()),
            'source':driver.config['source'],'spec_sha256':receipt['spec_sha256'],
            'code_sha256':receipt['code_sha256'],'execution_plan_sha256':receipt['execution_plan_sha256']})
    validation={'schema':'experiment-collection/v1','status':'VALID','run_id':driver.config['run_id'],
        'dispatch_sha256':selected['sha256'],'fits':records,
        'continuations':selected.get('continuations',[]),'scientifically_accepted':False}
    from orchestrator.preprocessing_continuation import history
    pre_history=history(driver,value)
    if pre_history:validation['preprocessing_continuations']=pre_history
    write_once(driver.state/'validation.json',canonical(validation))
    artifact(driver,value,'validation_result','experiment-validation','validation.json',canonical(validation))
    artifact(driver,value,'execution_receipt','experiment-execution-receipt','execution-receipt.json',
        canonical({'run_id':driver.config['run_id'],'status':'EXECUTED_AND_VALIDATED','fits':records,
                   'continuations':selected.get('continuations',[]),
                   **({'preprocessing_continuations':pre_history} if pre_history else {})}))
    artifact(driver,value,'execution_manifest','experiment-execution-manifest','execution-manifest.json',
        canonical({'run_id':driver.config['run_id'],'source':driver.config['source'],
            'dispatch_sha256':selected['sha256'],'fit_count':len(records)}))
    artifact(driver,value,'package_manifest','experiment-package-manifests','package-manifests.json',canonical(packages))
    value.update(phase='result_interpretation_author')
    driver.save(value)
    return driver.status()


def verified_subset(driver,value,selected,fit_ids):
    """Replay real collected originals/ledgers for a frozen subset, without a provider.

    This makes early smoke/benchmark evidence usable while FULL fits are pending.
    A subset is never final execution completion or scientific acceptance.
    """
    if (not isinstance(fit_ids,list) or not fit_ids or any(not isinstance(x,str) for x in fit_ids)
            or len(set(fit_ids))!=len(fit_ids)):
        raise ValueError('EXPERIMENT_COLLECTION_SUBSET')
    jobs=[j for j in selected['jobs'] if j['binding']['experiment']['fit_id'] in fit_ids]
    if ([j['binding']['experiment']['fit_id'] for j in jobs]!=fit_ids):
        raise ValueError('EXPERIMENT_COLLECTION_SUBSET')
    states=value.get('fit_dispatch',{});received=value.get('fit_collections',{})
    pins=value.get('fit_collection_receipts',{})
    if any(states.get(j['job'],{}).get('phase')!='COMPLETE' or j['job'] not in received
           or j['job'] not in pins for j in jobs):
        raise ValueError('EXPERIMENT_COLLECTION_SUBSET_NOT_COMPLETE')
    plan=results.strict(pr.check(driver.state/'experiment-package/execution-plan.json').read_bytes())
    records=[]
    from orchestrator.modal_executor import ModalExecutor
    for job in jobs:
        ident=job['job'];folder=driver.state/'fit-results'/ident
        package=driver.state/'fit-packages'/ident/'prepared'
        if not package.is_dir():raise ValueError('EXPERIMENT_COLLECTION_PACKAGE_REQUIRED')
        pr.check_tree(package)
        manifest=dispatch.bridge.emit(driver,value,package,job['binding'])
        if digest(canonical(manifest))!=states[ident]['manifest_sha256']:
            raise ValueError('EXPERIMENT_COLLECTION_PACKAGE_CHANGED')
        validation=results.validate(folder,manifest['binding'],plan)
        if validation!=received[ident]:raise ValueError('EXPERIMENT_SAVED_VALIDATION_CHANGED')
        local=driver.store.db.execute('SELECT status,binding FROM jobs WHERE id=?',(ident,)).fetchone()
        if local is None or local['status']!='COMPLETE' or results.strict(local['binding'])!=manifest['binding']:
            raise ValueError('EXPERIMENT_COLLECTION_LEDGER_CHANGED')
        global_row=driver.store.batch.db.execute('SELECT status,binding FROM autonomy_compute WHERE id=?',
            (digest(canonical(manifest['binding'])),)).fetchone()
        collected=driver.store.db.execute('SELECT manifest FROM manual_collections WHERE job=?',(ident,)).fetchone()
        expected_files={n:v['sha256'] for n,v in validation['files'].items()}
        if (global_row is None or global_row['status']!='COLLECTED'
                or results.strict(global_row['binding'])!=manifest['binding']
                or collected is None or results.strict(collected['manifest'])!=expected_files):
            raise ValueError('EXPERIMENT_COLLECTION_LEDGER_CHANGED')
        native=pr.check(ModalExecutor._paths(driver.store,ident)/'collection-receipt.json').read_bytes()
        receipt=results.strict(native)
        if (digest(native)!=pins[ident] or receipt.get('binding_sha256')!=digest(canonical(manifest['binding']))
                or receipt.get('file_sha256')!={n:v['sha256'] for n,v in validation['files'].items()}):
            raise ValueError('EXPERIMENT_COLLECTION_RECEIPT_CHANGED')
        records.append({'fit_id':job['binding']['experiment']['fit_id'],
            'collection_receipt_sha256':digest(native),'validation_sha256':digest(canonical(validation)),
            'files':validation['files'],'scientifically_accepted':False})
    return records


def verified(driver,value):
    """Re-read original collections without provider calls or phase mutation."""
    selected=dispatch.load(driver,value)
    if selected is None or selected['sha256']!=value.get('dispatch_sha256'):
        raise ValueError('EXPERIMENT_COLLECTION_SELECTION')
    states=value.get('fit_dispatch',{});received=value.get('fit_collections',{})
    pins=value.get('fit_collection_receipts',{})
    ids={job['job'] for job in selected['jobs']}
    if (not selected.get('complete_selection',True) or not complete_states(selected,states) or set(received)!=ids or set(pins)!=ids):
        raise ValueError('EXPERIMENT_COLLECTION_NOT_COMPLETE')
    records=verified_subset(driver,value,selected,[j['binding']['experiment']['fit_id'] for j in selected['jobs']])
    expected={'schema':'experiment-collection/v1','status':'VALID','run_id':driver.config['run_id'],
        'dispatch_sha256':selected['sha256'],'fits':records,
        'continuations':selected.get('continuations',[]),'scientifically_accepted':False}
    from orchestrator.preprocessing_continuation import history
    pre_history=history(driver,value)
    if pre_history:expected['preprocessing_continuations']=pre_history
    raw=pr.check(driver.state/'validation.json').read_bytes()
    if raw!=canonical(expected):raise ValueError('EXPERIMENT_FINAL_VALIDATION_CHANGED')
    return expected
