"""Actual seal -> handoff -> root publication -> driver/package connection.

Scientific report, data bytes and SDK identities are synthetic fixtures. The
approval, schemas, package hashes, runtime/preprocessing validators and ledger
comparisons are real. Root provenance is simulated ONLY when not run as root;
the same tests can run under root in a private, root-owned scratch hierarchy.
"""
import copy
import json
import os
from pathlib import Path
import pytest
from orchestrator import experiment_provisioning as provisioning, experiment_dispatch as dispatch
from orchestrator import experiment_package, experiment_modal_package as bridge, private_records as pr
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import digest, inventory
from orchestrator.modal_executor import canonical, verify_package
from orchestrator.modal_scientific_environment import environment_bytes
from test_experiment_approval import reviewed
from test_experiment_context import experiment, root
from test_modal_item4_provider import candidate
from test_modal_scientific_environment import spec


@pytest.fixture
def connected(reviewed,candidate,monkeypatch):
    d,value,_=reviewed
    assert d.config['item_number']==4
    Driver._accept_completed(d,value);experiment_package.emit(d,value)
    package=d.state/'experiment-package'
    p,runtime,binding,_,volumes,created,_,receipt,private,_=candidate
    d.config.update(batch_ledger=str(d.store.batch.folder),execution_provisioning=str(private/'selected'))
    value['phase']='EXECUTE_EXPERIMENT'
    runtime['batch_ledger']=d.config['batch_ledger']
    selected_env=spec();selected_env['expected'].update(cuda='12.8')
    selected_env['expected']['packages'].update(nnunetv2='2.8.1',torch='2.8.0')
    runtime.update(scientific_environment=selected_env,wheel_files=selected_env['wheels'])
    source={**bridge.support_files(),'run.py':bridge.WORKER.read_bytes(),
            'execution.py':(package/'code/execution.py').read_bytes()}
    code=digest(canonical({name:digest(raw) for name,raw in source.items()}))
    binding.update(run_id=d.config['run_id'],source=d.config['source'],scientific_environment=selected_env,
        outputs=['synthetic-result.json','validation.json'])
    binding['experiment'].update(fit_id='fit-one',segment=1,stage='SMOKE')
    binding['progress']['fit_id']='fit-one'
    fit=binding['progress']['fit_binding']
    fit.update(run_id=d.config['run_id'],arm='synthetic-arm',spec_sha256=digest((package/'SPEC.md').read_bytes()),
        code_sha256=code,environment_sha256=digest(environment_bytes(selected_env['expected'])))
    receipt.update(environment_sha256=fit['environment_sha256'],
        preprocessing_code_sha256=digest(source['execution.py']))
    pr.write_bytes(private/'receipt.json',canonical(receipt))
    runtime['item4_assets'].update(preprocessing_code_sha256=receipt['preprocessing_code_sha256'],
        preprocessing_sha256=digest(canonical(receipt)))
    binding['preprocessing_sha256']=runtime['item4_assets']['preprocessing_sha256']
    for key in ('spec_sha256','code_sha256'):binding.pop(key)
    validation={'schema':'modal-preprocessing-validation/v1','status':'PASS',
        'run_id':d.config['run_id'],'spec_sha256':fit['spec_sha256'],
        'preprocessing_code_sha256':receipt['preprocessing_code_sha256'],
        'validator_sha256':receipt['preprocessing_code_sha256'],
        'cohort_sha256':receipt['cohort_sha256'],
        'input_contract_sha256':fit['input_contract_sha256'],
        'environment_sha256':fit['environment_sha256'],
        'files':{entry['path']:{k:entry[k] for k in ('sha256','bytes')}
            for group in [*receipt['case_files'].values(),receipt['shared_files']] for entry in group.values()},'errors':[]}
    pr.write_bytes(private/'validation.json',canonical(validation))
    runtime['item4_preprocessing_validation']=provisioning.reference(private/'validation.json')
    runtime_path=private/'runtime.json';pr.write_bytes(runtime_path,canonical(runtime))
    binding['runtime_sha256']=digest(canonical(runtime))
    if os.geteuid()!=0:
        # Only host ownership is simulated; byte/path/privacy checks still run.
        monkeypatch.setattr(dispatch,'trusted',lambda path:Path(path))
        monkeypatch.setattr(provisioning,'trusted',lambda path:Path(path))
    rows=[{'runtime':provisioning.reference(runtime_path),'binding':binding}]
    return d,value,rows,private,created


@pytest.fixture
def root_identity(monkeypatch):
    if os.geteuid()==0:return
    # Unprivileged portable suites exercise identical publication I/O. A
    # separately recorded root scratch run uses the real chown/fchmod/trusted.
    monkeypatch.setattr(provisioning.os,'geteuid',lambda:0)
    monkeypatch.setattr(provisioning.os,'fchown',lambda *a:None)
    monkeypatch.setattr(provisioning.os,'chown',lambda *a,**k:None)
    monkeypatch.setattr(pr,'SERVICE_GID',os.getgid())


@pytest.mark.parametrize('reviewed',[4],indirect=True)
@pytest.mark.skipif(os.geteuid()!=0,reason='Native root publication verified separately in private root scratch')
def test_real_approval_preprocessing_handoff_publication_and_driver(connected,root_identity):
    d,value,rows,private,created=connected
    calls=[tuple(row) for row in d.store.db.execute('SELECT * FROM manual_calls')]
    ref=provisioning.prepare(d,value,rows,private/'preparation')
    before=inventory(d.state/'experiment-package')
    assert not Path(d.config['execution_provisioning']).exists()
    published=provisioning.publish(ref['path'],expected_sha256=ref['sha256'])
    assert published['status']=='PROVISIONED'
    dest=Path(d.config['execution_provisioning'])
    assert dest.stat().st_mode&0o777==0o550
    assert all(f.stat().st_mode&0o777==0o440 for f in dest.iterdir())
    selected=dispatch.load(d,value)
    assert selected['sha256']==published['ready_sha256']
    dispatch.advance(d,value) # PREPARE only; actual approval+provider-package validators.
    job=selected['jobs'][0]['job'];prepared=d.state/'fit-packages'/job/'prepared'
    result=json.loads((prepared/'manifest.json').read_bytes())
    assert verify_package(prepared,result['binding'])==result
    assert value['fit_dispatch'][job]['phase']=='UPLOAD'
    assert not created and inventory(d.state/'experiment-package')==before
    assert [tuple(row) for row in d.store.db.execute('SELECT * FROM manual_calls')]==calls
    same=inventory(dest)
    assert provisioning.publish(ref['path'],expected_sha256=ref['sha256'])['status']=='ALREADY_PROVISIONED'
    assert inventory(dest)==same and not created


@pytest.mark.parametrize('reviewed',[4],indirect=True)
@pytest.mark.parametrize('damage',['receipt','cohort','environment','scientific-code','fit','source','alias','overlap','permission','phase','validator','validation-failure','validation-files'])
def test_preparation_refuses_without_ready_or_provider(connected,damage):
    d,value,rows,private,created=connected
    runtime=json.loads((private/'runtime.json').read_bytes());binding=rows[0]['binding']
    if damage=='receipt':pr.write_text(private/'receipt.json','{}')
    elif damage=='cohort':pr.write_text(private/'cohort.json','{}')
    elif damage=='environment':runtime['scientific_environment']['expected']['python']='different'
    elif damage=='scientific-code':
        runtime['item4_assets']['preprocessing_code_sha256']='f'*64
    elif damage=='fit':binding['progress']['fit_binding']['arm']='different'
    elif damage=='source':binding['source']='b'*40
    elif damage=='alias':
        (private/'runtime-alias.json').symlink_to(private/'runtime.json')
        rows[0]['runtime']['path']=str(private/'runtime-alias.json')
    elif damage=='overlap':
        runtime['wheel_volume_id']=binding['wheel_volume_id']=runtime['package_volume_id']
    elif damage=='permission':(private/'receipt.json').chmod(0o644)
    elif damage=='phase':value['phase']='run_spec_review'
    elif damage in {'validator','validation-failure','validation-files'}:
        validation=json.loads((private/'validation.json').read_bytes())
        if damage=='validator':validation['validator_sha256']='f'*64
        elif damage=='validation-failure':validation['status']='FAIL'
        else:validation['files']={}
        pr.write_bytes(private/'validation.json',canonical(validation))
        runtime['item4_preprocessing_validation']=provisioning.reference(private/'validation.json')
    if damage in {'environment','scientific-code','overlap','validator','validation-failure','validation-files'}:
        pr.write_bytes(private/'runtime.json',canonical(runtime))
        rows[0]['runtime']=provisioning.reference(private/'runtime.json')
        binding['runtime_sha256']=digest(canonical(runtime))
    with pytest.raises(ValueError):provisioning.prepare(d,value,rows,private/'preparation')
    assert not Path(d.config['execution_provisioning']).exists() and not created


@pytest.mark.parametrize('reviewed',[4],indirect=True)
@pytest.mark.parametrize('damage',['selection','prepared-code','reviewed-original','runtime','receipt','hash','unsafe-existing','partial-existing'])
def test_changed_preparation_or_existing_record_never_publishes(connected,root_identity,damage):
    d,value,rows,private,created=connected
    ref=provisioning.prepare(d,value,rows,private/'preparation');record=json.loads(Path(ref['path']).read_bytes())
    dest=Path(d.config['execution_provisioning'])
    if damage=='selection':
        record['selection']['jobs'][0]['binding']['outputs'].append('unselected.csv')
        pr.write_bytes(ref['path'],canonical(record));ref['sha256']=digest(canonical(record))
    elif damage=='prepared-code':
        path=Path(record['packages'][0]['manifest']['path']).parent/'execution.py'
        pr.write_bytes(path,path.read_bytes()+b'\n# changed\n')
    elif damage=='reviewed-original':pr.write_bytes(d.state/'experiment-package/code/execution.py',b'changed')
    elif damage=='runtime':pr.write_text(private/'runtime.json','{}')
    elif damage=='receipt':pr.write_text(private/'receipt.json','{}')
    elif damage=='hash':ref['sha256']='f'*64
    else:
        pr.mkdir(dest);pr.write_text(dest/'unrelated','preserved')
        if damage=='unsafe-existing':(dest/'unrelated').chmod(0o644)
    old=inventory(dest) if dest.exists() else None
    with pytest.raises(ValueError):provisioning.publish(ref['path'],expected_sha256=ref['sha256'])
    assert not (dest/'READY.json').exists() and not created
    if old is not None:assert inventory(dest)==old


@pytest.mark.parametrize('reviewed',[4],indirect=True)
@pytest.mark.skipif(os.geteuid()!=0,reason='Native root publication verified separately in private root scratch')
def test_existing_empty_preallocated_directory_keeps_its_modes(connected,root_identity):
    d,value,rows,private,_=connected
    ref=provisioning.prepare(d,value,rows,private/'preparation')
    dest=Path(d.config['execution_provisioning']);pr.mkdir(dest)
    os.chown(dest,0,pr.SERVICE_GID);dest.chmod(0o550)
    before=dest.stat()
    provisioning.publish(ref['path'],expected_sha256=ref['sha256'])
    after=dest.stat()
    assert (before.st_uid,before.st_gid,before.st_mode)==(after.st_uid,after.st_gid,after.st_mode)
    assert dispatch.load(d,value)['jobs']


@pytest.mark.parametrize('reviewed',[4],indirect=True)
def test_publication_requires_root_and_never_opens_a_ledger(connected,monkeypatch):
    d,value,rows,private,_=connected
    ref=provisioning.prepare(d,value,rows,private/'preparation')
    monkeypatch.setattr(provisioning.os,'geteuid',lambda:1003)
    with pytest.raises(ValueError,match='^EXPERIMENT_PROVISIONING_ROOT_REQUIRED$'):
        provisioning.publish(ref['path'],expected_sha256=ref['sha256'])
    assert not Path(d.config['execution_provisioning']).exists()


@pytest.mark.parametrize("command",["prepare-execution","prepare-preprocessing"])
def test_prepare_command_refuses_root_before_driver_constructor(monkeypatch,tmp_path,command):
    from orchestrator import experiment_driver
    called=[]
    monkeypatch.setattr(experiment_driver.os,'geteuid',lambda:0)
    monkeypatch.setattr(experiment_driver,'ExperimentDriver',lambda *a:called.append(a))
    with pytest.raises(ValueError,match='^EXPERIMENT_PREPARATION_OWNER_REQUIRED$'):
        experiment_driver.main([command,'--state',str(tmp_path),'--jobs','unused','--destination','unused'])
    assert called==[]


def test_root_record_becomes_visible_only_after_complete_private_write(tmp_path,root_identity,monkeypatch):
    path=tmp_path/'READY.json';raw=canonical({'synthetic':'complete record'})
    if os.getuid()!=0:monkeypatch.setattr(provisioning,'trusted',lambda p:Path(p))
    observed=[];rename=os.rename
    def inspect_rename(source,destination):
        assert not path.exists()
        assert Path(source).read_bytes()==raw
        assert Path(source).stat().st_mode&0o777==0o440
        observed.append(True);rename(source,destination)
    monkeypatch.setattr(provisioning.os,'rename',inspect_rename)
    provisioning._root_file(path,raw)
    assert observed==[True] and path.read_bytes()==raw
    assert not path.with_name('READY.json.pending').exists()
    with pytest.raises(ValueError,match='^EXPERIMENT_PROVISIONING_EXISTING_FILE$'):
        provisioning._root_file(path,raw)
    assert path.read_bytes()==raw


@pytest.mark.parametrize('reviewed',[4],indirect=True)
def test_concurrent_root_publication_refuses_before_any_ready_write(connected,root_identity):
    import fcntl
    d,value,rows,private,_=connected
    ref=provisioning.prepare(d,value,rows,private/'preparation')
    descriptor=os.open(private,os.O_RDONLY|os.O_DIRECTORY)
    try:
        fcntl.flock(descriptor,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with pytest.raises(BlockingIOError):
            provisioning.publish(ref['path'],expected_sha256=ref['sha256'])
    finally:os.close(descriptor)
    assert not Path(d.config['execution_provisioning']).exists()


@pytest.mark.parametrize('reviewed',[4],indirect=True)
@pytest.mark.parametrize('damage',[None,'missing','hash','job','validation','receipt','count','accepted','unsafe'])
def test_preparation_binds_original_preprocessing_execution(connected,damage):
    d,value,rows,private,created=connected
    runtime=json.loads((private/'runtime.json').read_bytes());binding=rows[0]['binding']
    job='7'*64
    runtime['item4_assets']['preprocessing_job_sha256']=binding['preprocessing_job_sha256']=job
    validation=json.loads((private/'validation.json').read_bytes())
    record={'schema':'experiment-preprocessing-result/v1','status':'VALIDATED','binding_sha256':job,
        'preprocessing_sha256':runtime['item4_assets']['preprocessing_sha256'],
        'validation_sha256':runtime['item4_preprocessing_validation']['sha256'],
        'files':len(validation['files']),'bytes':sum(v['bytes'] for v in validation['files'].values()),
        'scientifically_accepted':False,'fit_completed':False,'steps':1,'elapsed_seconds':1.0}
    path=private/'preprocessing-execution.json'
    if damage=='job':record['binding_sha256']='8'*64
    elif damage=='validation':record['validation_sha256']='8'*64
    elif damage=='receipt':record['preprocessing_sha256']='8'*64
    elif damage=='count':record['files']+=1
    elif damage=='accepted':record['scientifically_accepted']=True
    pr.write_bytes(path,canonical(record))
    runtime['item4_preprocessing_execution']=provisioning.reference(path)
    if damage=='missing':runtime.pop('item4_preprocessing_execution')
    elif damage=='hash':runtime['item4_preprocessing_execution']['sha256']='8'*64
    elif damage=='unsafe':path.chmod(0o644) # Disposable planted-file refusal.
    pr.write_bytes(private/'runtime.json',canonical(runtime))
    binding['runtime_sha256']=digest(canonical(runtime))
    rows[0]['runtime']=provisioning.reference(private/'runtime.json')
    if damage is not None:
        with pytest.raises(ValueError):provisioning.prepare(d,value,rows,private/'preparation')
    else:
        prepared=provisioning.prepare(d,value,rows,private/'preparation')
        result=json.loads(Path(prepared['path']).read_bytes())
        assert result['packages'][0]['evidence']['preprocessing_execution']==runtime['item4_preprocessing_execution']
        assert provisioning.inspect(prepared['path']) is not None
    assert not created and not Path(d.config['execution_provisioning']).exists()
