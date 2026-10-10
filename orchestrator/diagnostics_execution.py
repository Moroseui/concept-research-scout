"""Item6 sealed program -> one CPU job -> aggregate interpretation, no science here."""
import base64
import json
from pathlib import Path
from orchestrator import diagnostics_policy as policy,private_records as pr
from orchestrator.diagnostics_contract import PURPOSE,require,sha,encoded,strict,program_contract,input_contract,validate_outputs
from orchestrator.manual_driver import write_once
from orchestrator.manual_executor import inventory


def selection(driver,value):
    from orchestrator.experiment_package import verify
    from orchestrator.experiment_approval import verify as approved
    require(driver.config['item_number']==6 and driver.config['run_id']==policy.RUN_ID,'DIAGNOSTICS_SELECTION')
    package=driver.state/'experiment-package'
    require(package.is_dir(),'DIAGNOSTICS_REVIEWED_PACKAGE_REQUIRED')
    verify(driver,value,package)
    review=approved(driver,value)
    raw=pr.check(package/'code/analysis.program.json').read_bytes();program=strict(raw)
    require(program.get('schema')=='scientific-program/v2','DIAGNOSTICS_EXECUTABLE_CONTRACT_REQUIRED')
    contract=program_contract(program['contract'])
    shown=next(r for r in review['artifacts'] if r['type']=='analysis_provenance')
    from orchestrator.context_budget import relative_file
    provenance=strict(pr.check(relative_file(driver.context,shown['path'])).read_bytes())
    require(provenance.get('program_contract')==contract,'DIAGNOSTICS_REVIEWED_CONTRACT_REQUIRED')
    folder=Path(driver.config['execution_provisioning']);path=folder/'selection.json'
    if not path.exists():return None
    from orchestrator.manual_host_guard import trusted
    pr.check(trusted(folder));raw=pr.check(trusted(path)).read_bytes();selected=strict(raw)
    require(isinstance(selected,dict) and set(selected)=={'schema','source','run_id','reviewed_execution_sha256','provider','resources','overhead_micro_usd','cost'},'DIAGNOSTICS_RUNTIME_SELECTION')
    require(selected['schema']=='diagnostics-execution-selection/v1' and selected['source']==driver.config['source'] and selected['run_id']==policy.RUN_ID and selected['reviewed_execution_sha256']==value['reviewed_execution']['sha256'],'DIAGNOSTICS_RUNTIME_BINDING')
    provider=selected['provider'];require(isinstance(provider,dict) and set(provider)=={'sdk_package','sdk_sha256','credential_file','workspace','diagnostics_assets'},'DIAGNOSTICS_PROVIDER_CONFIG')
    require(provider['workspace']=='moroseui' and selected['resources']['gpu'] is None,'DIAGNOSTICS_CPU_ONLY')
    a=provider['diagnostics_assets'];input_contract(a['input_contract'],base64.b64decode(a['cohort'],validate=True),base64.b64decode(a['source_capture'],validate=True))
    expected={'schema':'diagnostics-environment/v1','image_id':a['image_id'],'requirements':contract['requirements']}
    from orchestrator.modal_diagnostics_image import runtime_environment
    expected=runtime_environment(expected,a)
    require(a['environment']==expected,'DIAGNOSTICS_REVIEWED_REQUIREMENTS_CHANGED')
    binding={'purpose':PURPOSE,'run_id':policy.RUN_ID,'source':driver.config['source'],'authority_sha256':policy.authority(),
        'owner_sha256':sha(encoded(driver.config['owner_binding'])),'runtime_sha256':sha(encoded(provider)),
        'spec_sha256':sha((package/'SPEC.md').read_bytes()),'review_sha256':sha((package/'review.json').read_bytes()),
        'code_sha256':sha((package/'code/analysis.py').read_bytes()),'program_sha256':sha((package/'code/analysis.program.json').read_bytes()),
        'execution_plan_sha256':sha((package/'execution-plan.json').read_bytes()),'reviewed_execution_sha256':value['reviewed_execution']['sha256'],
        'input_contract':a['input_contract'],'input_contract_sha256':sha(encoded(a['input_contract'])),
        'environment_sha256':sha(encoded(expected)),'image_id':a['image_id'],'program_contract':contract,
        'outputs':contract['outputs'],'resources':selected['resources'],'overhead_micro_usd':selected['overhead_micro_usd'],'cost':selected['cost'],
        'provisioning_sha256':sha(raw)}
    from types import SimpleNamespace
    from orchestrator.diagnostics_modal import scope
    scope(SimpleNamespace(config=provider),provider,binding)
    return {'provider':provider,'binding':binding,'sha256':sha(raw)}


def support_files():
    from orchestrator.diagnostics_modal import WORKER
    root=Path(__file__).parent
    names=('diagnostics_contract.py','experiment_result.py','private_records.py','scientific_view_scan.py','privacy_patterns.py')
    return {'run.py':WORKER.encode(),'orchestrator/__init__.py':b'',**{'orchestrator/'+name:(root/name).read_bytes() for name in names}}


def prepared_contents(driver,value,binding):
    from orchestrator.experiment_package import verify
    package=driver.state/'experiment-package';m=verify(driver,value,package)
    files={name:(package/name).read_bytes() for name in m['files']}
    require(not set(files)&set(support_files()),'DIAGNOSTICS_SUPPORT_COLLISION')
    files.update(support_files())
    return files,{'schema':'modal-run/v1','binding':binding,'files':{k:sha(v) for k,v in files.items()}}


def verify_prepared(folder,binding):
    require(binding.get('purpose')==PURPOSE and binding.get('run_id')==policy.RUN_ID and binding.get('authority_sha256')==policy.authority(),'DIAGNOSTICS_PACKAGE_SCOPE')
    program_contract(binding['program_contract'])
    folder=Path(folder);pr.check_tree(folder);manifest=strict((folder/'manifest.json').read_bytes())
    require(manifest=={'schema':'modal-run/v1','binding':binding,'files':manifest.get('files')},'DIAGNOSTICS_PACKAGE_SCHEMA')
    require(inventory(folder)=={**manifest['files'],'manifest.json':sha((folder/'manifest.json').read_bytes())},'DIAGNOSTICS_PACKAGE_HASH')
    from orchestrator.review_contract import scientific
    review=scientific((folder/'review.json').read_bytes());require(review['verdict']=='APPROVE' and not review['findings'],'DIAGNOSTICS_SPEC_APPROVAL')
    for path,key in [('SPEC.md','spec_sha256'),('review.json','review_sha256'),('code/analysis.py','code_sha256'),('code/analysis.program.json','program_sha256'),('execution-plan.json','execution_plan_sha256'),('approval.json','reviewed_execution_sha256')]:
        require(sha((folder/path).read_bytes())==binding[key],'DIAGNOSTICS_PACKAGE_BINDING')
    program=strict((folder/'code/analysis.program.json').read_bytes())
    require(program.get('schema')=='scientific-program/v2' and program['contract']==binding['program_contract'],'DIAGNOSTICS_PROGRAM_BINDING')
    require(program['run_id']==binding['run_id'] and program['execution_plan_sha256']==binding['execution_plan_sha256'],'DIAGNOSTICS_PROGRAM_BINDING')
    require(isinstance(program.get('files'),dict) and set(program['files'])=={'analysis.py','test_analysis.py'},'DIAGNOSTICS_PROGRAM_FILES')
    for name,text in program['files'].items():require((folder/'code'/name).read_bytes()==text.encode(),'DIAGNOSTICS_PROGRAM_SOURCE_CHANGED')
    for name,raw in support_files().items():require((folder/name).read_bytes()==raw,'DIAGNOSTICS_FIXED_WORKER_CHANGED')
    return manifest


@pr.private_umask
def prepare(driver,value):
    selected=selection(driver,value)
    if selected is None:return None
    folder=driver.state/'diagnostics-package';files,manifest=prepared_contents(driver,value,selected['binding'])
    if folder.exists():
        require((folder/'manifest.json').is_file(),'DIAGNOSTICS_PARTIAL_PACKAGE')
    else:
        pr.mkdir(folder)
        for name,raw in files.items():write_once(folder/name,raw)
        write_once(folder/'manifest.json',encoded(manifest))
    verify_prepared(folder,selected['binding'])
    require(inventory(folder)=={**manifest['files'],'manifest.json':sha(encoded(manifest))},'DIAGNOSTICS_PREPARED_CHANGED')
    return selected


def executor(driver,selected):
    from orchestrator.modal_executor import ModalExecutor
    from orchestrator.modal_provider import ModalProvider
    provider=driver.provider_factory(selected['provider']) if driver.provider_factory else ModalProvider(selected['provider'])
    return ModalExecutor(driver.store.path,selected['provider'],provider,driver.store.batch)


@pr.private_umask
def advance(driver,value):
    selected=prepare(driver,value)
    if selected is None:return {**driver.status(),'status':'WAIT_CPU_PROVISIONING','reason':'Reviewed program ready; genuine immutable image and exact development-only data/package selections are required. No execution admitted.'}
    job=policy.RUN_ID;folder=driver.state/'diagnostics-package';exe=executor(driver,selected)
    try:
        outcome=exe.submit(job,selected['binding'],folder,driver.state/'diagnostics-emitted')
        if outcome['status']=='COMPLETE':value.update(phase='COLLECT_EXPERIMENT',diagnostics_selection_sha256=selected['sha256']);driver.save(value)
        elif outcome['status'] in {'FAILED','UNKNOWN','UNRESOLVED_SUBMISSION'}:raise ValueError('DIAGNOSTICS_EXECUTION_BLOCKED_NO_RETRY')
        return {**driver.status(),'execution':outcome}
    finally:exe.db.close()


def verified(driver,value):
    from orchestrator.modal_executor import ModalExecutor
    selected=prepare(driver,value);require(selected is not None,'DIAGNOSTICS_PROVISIONING_REQUIRED')
    require(value.get('diagnostics_selection_sha256')==selected['sha256'],'DIAGNOSTICS_COLLECTION_SELECTION')
    folder=driver.state/'diagnostics-results';result=validate_outputs(folder,selected['binding'])
    local=driver.store.db.execute('SELECT status,binding FROM jobs WHERE id=?',(policy.RUN_ID,)).fetchone()
    global_row=driver.store.batch.db.execute('SELECT status,binding FROM autonomy_compute WHERE id=?',(sha(encoded(selected['binding'])),)).fetchone()
    collection=driver.store.db.execute('SELECT manifest FROM manual_collections WHERE job=?',(policy.RUN_ID,)).fetchone()
    require(local is not None and local['status']=='COMPLETE' and strict(local['binding'])==selected['binding'] and global_row is not None and global_row['status']=='COLLECTED' and strict(global_row['binding'])==selected['binding'],'DIAGNOSTICS_COLLECTED_LEDGERS_REQUIRED')
    files={n:r['sha256'] for n,r in result['files'].items()}
    require(collection is not None and strict(collection['manifest'])==files,'DIAGNOSTICS_COLLECTION_HASHES')
    native=pr.check(ModalExecutor._paths(driver.store,policy.RUN_ID)/'collection-receipt.json').read_bytes();receipt=strict(native)
    require(sha(native)==value.get('diagnostics_collection_receipt_sha256') and receipt['binding_sha256']==sha(encoded(selected['binding'])) and receipt['file_sha256']==files,'DIAGNOSTICS_COLLECTION_RECEIPT')
    require(receipt.get('native_preflight',{}).get('status')=='PASS' and receipt['native_preflight']['binding_sha256']==receipt['binding_sha256'],'DIAGNOSTICS_NATIVE_PROOF_REQUIRED')
    require((driver.state/'validation.json').read_bytes()==encoded(result),'DIAGNOSTICS_FINAL_VALIDATION_CHANGED')
    return result


@pr.private_umask
def collect(driver,value):
    from orchestrator.experiment_collection import artifact
    selected=prepare(driver,value);require(selected is not None,'DIAGNOSTICS_PROVISIONING_REQUIRED')
    exe=executor(driver,selected);folder=driver.state/'diagnostics-results'
    def validate(path):return {'status':'VALID','scientific_validation':validate_outputs(path,selected['binding'])}
    try:
        result=exe.collect_remote(policy.RUN_ID,driver.state/'diagnostics-package',folder,validate)
        require(result.get('status')=='VALID','DIAGNOSTICS_COLLECTION_REFUSED')
        native=pr.check(exe._paths(policy.RUN_ID)/'collection-receipt.json').read_bytes()
    finally:exe.db.close()
    validation=validate_outputs(folder,selected['binding']);write_once(driver.state/'validation.json',encoded(validation))
    value['diagnostics_collection_receipt_sha256']=sha(native)
    for name,row in validation['files'].items():
        artifact(driver,value,'validation_result' if name=='validation.json' else 'result_tables','diagnostics-result-'+name,'diagnostics/'+name,(folder/name).read_bytes())
    artifact(driver,value,'execution_receipt','diagnostics-execution-receipt','diagnostics-execution-receipt.json',native)
    artifact(driver,value,'execution_manifest','diagnostics-execution-manifest','diagnostics-execution-manifest.json',encoded({'run_id':policy.RUN_ID,'source':driver.config['source'],'program_sha256':selected['binding']['program_sha256'],'environment_sha256':selected['binding']['environment_sha256'],'input_contract_sha256':selected['binding']['input_contract_sha256'],'cpu_only':True,'training':False}))
    artifact(driver,value,'package_manifest','diagnostics-package-manifest','diagnostics-package-manifest.json',encoded({'package_sha256':sha((driver.state/'diagnostics-package/manifest.json').read_bytes()),'reviewed_execution_sha256':value['reviewed_execution']['sha256']}))
    verified(driver,value);value.update(phase='result_interpretation_author');driver.save(value);return driver.status()
