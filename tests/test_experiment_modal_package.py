"""Real scientific seal -> real Modal verifier; no paid SDK or model calls.

The imported fixture labels its synthetic review/native/test evidence. Worker
execution below uses only trivial synthetic modules, never scientific code.
"""
import json
import subprocess
import sys
from pathlib import Path
import pytest
from orchestrator import experiment_modal_package as bridge, experiment_package as package
from orchestrator import private_records as pr, experiment_worker as worker
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import digest, inventory
from orchestrator.modal_executor import verify_package, canonical
from orchestrator.modal_item4_policy import AUTHORITY, TEAM_AUTHORITY
from test_experiment_approval import reviewed
from test_experiment_context import experiment, root
from test_modal_item4_provider import candidate


def emit(d,value):
    Driver._accept_completed(d,value);package.emit(d,value)
    binding={'purpose':'M4_ITEM4','run_id':d.config['run_id'],'source':d.config['source'],
             'experiment':{'backlog_item':4,'authority_sha256':AUTHORITY,'team_authority_sha256':TEAM_AUTHORITY}}
    return bridge.emit(d,value,d.state/'modal-package',binding),binding


def test_real_package_bridge_keeps_scientific_spec_review_and_module_exact(reviewed):
    d,value,work=reviewed
    if d.config['item_number']==6:
        with pytest.raises(ValueError,match='^EXPERIMENT_MODAL_ITEM4_ONLY$'):emit(d,value)
        assert not (d.state/'modal-package').exists()
        return
    manifest,binding=emit(d,value);folder=d.state/'modal-package'
    assert verify_package(folder,manifest['binding'])==manifest
    assert bridge.emit(d,value,folder,binding)==manifest
    for name in ('SPEC.md','review.json','execution-plan.json','approval.json'):
        assert (folder/name).read_bytes()==(d.state/'experiment-package'/name).read_bytes()
    assert (folder/'execution.py').read_bytes()==(d.state/'experiment-package/code/execution.py').read_bytes()
    assert 'notebook_code_sha256:' not in (folder/'SPEC.md').read_text()
    assert manifest['binding']['execution']['worker_sha256']==digest(bridge.WORKER.read_bytes())
    assert manifest['binding']['code_sha256']==digest(canonical({k:v for k,v in manifest['files'].items() if k.endswith('.py')}))


@pytest.mark.parametrize('damage',['module','worker','spec','approval','plan','extra','binding','partial','support'])
def test_package_reentry_never_overwrites_or_rebinds(reviewed,damage):
    d,value,work=reviewed
    if d.config['item_number']!=4:
        with pytest.raises(ValueError,match='^EXPERIMENT_MODAL_ITEM4_ONLY$'):emit(d,value)
        return
    manifest,binding=emit(d,value);folder=d.state/'modal-package'
    if damage=='binding':binding['source']='f'*40
    elif damage=='partial':(folder/'manifest.json').unlink()  # Disposable fixture.
    else:
        name={'module':'execution.py','worker':'run.py','spec':'SPEC.md','approval':'approval.json',
              'plan':'execution-plan.json','extra':'extra.py','support':'orchestrator/modal_fit_publication.py'}[damage]
        pr.write_bytes(folder/name,b'changed synthetic bytes')
    before={p:p.read_bytes() for p in folder.iterdir() if p.is_file()}
    with pytest.raises(ValueError):bridge.emit(d,value,folder,binding)
    assert before=={p:p.read_bytes() for p in folder.iterdir() if p.is_file()}


def test_modified_hashes_do_not_make_unreviewed_code_accepted(reviewed):
    d,value,work=reviewed
    if d.config['item_number']!=4:
        with pytest.raises(ValueError,match='^EXPERIMENT_MODAL_ITEM4_ONLY$'):emit(d,value)
        return
    manifest,_=emit(d,value);folder=d.state/'modal-package'
    pr.write_text(folder/'execution.py','# changed synthetic module')
    manifest['files']['execution.py']=digest((folder/'execution.py').read_bytes())
    manifest['binding']['execution']['module_sha256']=manifest['files']['execution.py']
    manifest['binding']['code_sha256']=digest(canonical({k:v for k,v in manifest['files'].items() if k.endswith('.py')}))
    pr.write_bytes(folder/'manifest.json',canonical(manifest))
    with pytest.raises(ValueError,match='^EXPERIMENT_MODAL_REVIEWED_BYTES_CHANGED$'):
        verify_package(folder,manifest['binding'])


# Synthetic author-owned output contract; no patient computation.
VALIDATION_SOURCE = """
def validation(o, c):
    import json, hashlib
    b = c['runtime']; raw = (o/'result.txt').read_bytes()
    value = {'schema':'experiment-validation/v1','run_id':b['run_id'],
        'fit_id':b['experiment']['fit_id'], 'spec_sha256':b['spec_sha256'],
        'code_sha256':b['code_sha256'],'execution_plan_sha256':b['execution_plan_sha256'],
        'files':{'result.txt':{'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}},
        'checks':[{'id':'synthetic-check','status':'PASS','evidence':['result.txt']}]}
    (o/'validation.json').write_text(json.dumps(value))
"""


@pytest.fixture
def worker_files(tmp_path):
    package=tmp_path/'package';inputs=tmp_path/'inputs';progress=tmp_path/'progress'
    for p in (package,inputs,progress):pr.mkdir(p)
    pr.write_text(inputs/'synthetic.txt','synthetic payload')
    source=("def main(input_root, output_root, contract):\n"
            "    assert contract['execution_plan']['synthetic'] is True\n"
            "    (output_root/'result.txt').write_text((input_root/'synthetic.txt').read_text())\n"
            "    contract['progress'].publish('final', lambda p: p.write_bytes(b'synthetic final checkpoint'), "
            "metadata={'next_epoch':1,'total_epochs':1,'native_version':'2.8.1'})\n"
            "    validation(output_root, contract)\n" + VALIDATION_SOURCE)
    files={'execution.py':source.encode(),'run.py':bridge.WORKER.read_bytes(),
           'SPEC.md':b'synthetic only','review.json':b'{}','execution-plan.json':b'{"synthetic": true}',
           'approval.json':b'{"synthetic_fixture":true}', 'reviewed-package.json':b'{"synthetic_fixture":true}'}
    files.update(bridge.support_files())
    for name,raw in files.items():pr.write_bytes(package/name,raw)
    def seal(base=None, runtime_config=None):
        fit_id=(base or {}).get('experiment',{}).get('fit_id','fit')
        pr.write_bytes(package/'execution-plan.json',canonical({'synthetic':True,'fits':[{'fit_id':fit_id,
            'outputs':['result.txt','validation.json'],'validation_checks':['synthetic-check']}]}))
        pins={name:digest((package/name).read_bytes()) for name in files}
        binding={**(base or {}),'purpose':'M4_ITEM4','execution':{'schema':'reviewed-module/v1','module':'execution.py','module_sha256':pins['execution.py'],'worker_sha256':pins['run.py'],'approval_sha256':pins['approval.json'],
                 'package_manifest_sha256':pins['reviewed-package.json'],'support_sha256':{name:pins[name] for name in worker.SUPPORT_FILES}},
                 'code_sha256':digest(canonical({k:v for k,v in pins.items() if k.endswith('.py')})),
                 'spec_sha256':pins['SPEC.md'],'review_sha256':pins['review.json'],
                 'execution_plan_sha256':pins['execution-plan.json']}
        binding.setdefault('run_id','synthetic-run')
        binding.setdefault('experiment',{'fit_id':'fit','segment':1})
        binding.setdefault('outputs',['result.txt','validation.json'])
        fit={'run_id':binding['run_id'],'arm':'synthetic','fold':0,'realization':'one',
             'input_contract_sha256':'1'*64,'environment_sha256':'2'*64,'plans_sha256':'3'*64,
             'spec_sha256':binding['spec_sha256'],'code_sha256':binding['code_sha256']}
        binding.setdefault('progress',{'volume_id':'vo-progress','volume_name':'progress','fit_id':'fit','fit_binding':fit})
        binding['progress']['fit_binding'].update(spec_sha256=binding['spec_sha256'],code_sha256=binding['code_sha256'])
        if runtime_config is not None:
            runtime_config['item4_assets']['progress']=binding['progress']
            binding['runtime_sha256']=digest(canonical(runtime_config))
        pr.write_bytes(package/'manifest.json',canonical({'schema':'modal-run/v1','binding':binding,'files':pins}))
        return digest(canonical(binding))
    return package,inputs,progress,seal


def test_actual_worker_imports_synthetic_module_once_and_does_not_claim_validation(worker_files):
    package,inputs,progress,seal=worker_files;pin=seal()
    result=worker.execute(package,inputs,progress,pin)
    assert result['status']=='EXECUTED' and result['scientifically_validated'] is False
    output=progress/'executions'/pin
    assert (output/'artifacts/result.txt').read_bytes()==(inputs/'synthetic.txt').read_bytes()
    before=inventory(progress)
    with pytest.raises(FileExistsError):worker.execute(package,inputs,progress,pin)
    assert inventory(progress)==before
    pr.check_tree(progress)


@pytest.mark.parametrize('damage',['hash','extra','alias','binding'])
def test_worker_checks_before_any_module_import_or_attempt(worker_files,damage):
    package,inputs,progress,seal=worker_files;pin=seal()
    if damage=='hash':pr.write_text(package/'execution.py',"raise AssertionError('must not import')")
    elif damage=='extra':pr.write_text(package/'unreviewed.py','extra')
    elif damage=='alias':(package/'execution.py').unlink();(package/'execution.py').symlink_to(inputs/'synthetic.txt')
    else:pin='f'*64
    with pytest.raises(ValueError):worker.execute(package,inputs,progress,pin)
    assert not list(progress.iterdir())


def test_worker_preserves_failed_program_and_refuses_execution_again(worker_files):
    package,inputs,progress,seal=worker_files
    pr.write_text(package/'execution.py',"def main(*args): raise RuntimeError('synthetic failure')\n")
    pin=seal()
    with pytest.raises(RuntimeError):worker.execute(package,inputs,progress,pin)
    outcome=json.loads((progress/'executions'/pin/'execution.json').read_bytes())
    assert outcome['status']=='FAILED' and outcome['error_type']=='RuntimeError'
    assert outcome['scientifically_validated'] is False
    with pytest.raises(FileExistsError):worker.execute(package,inputs,progress,pin)


@pytest.mark.skipif(not Path('/opt/research-system-cpu-tools/m2-python312-xgb341-v2').is_dir(),
                    reason='Pinned native CPU environment: run on server')
def test_worker_runs_in_native_network_disabled_sandbox(worker_files,tmp_path):
    from orchestrator import cpu_isolation
    from test_notebook_synthetic import ENVIRONMENT
    provider_package,data,_progress,seal=worker_files;pin=seal()
    package=tmp_path/'sandbox-package';workspace=tmp_path/'sandbox-workspace'
    pr.mkdir(package);pr.mkdir(workspace)
    pr.copytree(provider_package,package/'provider')
    pr.copyfile(bridge.WORKER,package/'worker.py')
    pr.write_text(package/'Sprint10.ipynb','{"synthetic_fixture":true}')
    pr.write_text(data/'development99.manifest.json','{"synthetic_fixture":true,"cases":[]}')
    from orchestrator import modal_input_guard
    payload={'binding_sha256':pin, 'guard_sha256':digest(Path(modal_input_guard.__file__).read_bytes()),
             'preprocessing_sha256':'f'*64,
             'files':{name:{'bytes':(data/name).stat().st_size,'sha256':sha} for name,sha in inventory(data).items()}}
    pr.copyfile(Path(modal_input_guard.__file__),package/'input_guard.py')
    pr.write_text(package/'launch_worker.py',"import sys\nsys.path.insert(0, '/package')\nimport worker\n"+
        "worker.execute('/package/provider','/content/drive/MyDrive/isles-pilot','/workspace',"+repr(pin)+")\n")
    pr.write_text(package/'run.py',"import runpy\nexecute=runpy.run_path('/package/input_guard.py')['execute']\n"+
        "execute('/content/drive/MyDrive/isles-pilot','/workspace','/package/launch_worker.py',"+repr(payload)+")\n")
    before=inventory(package)
    command=cpu_isolation.command(ENVIRONMENT,package,data,workspace)
    result=subprocess.run(command,capture_output=True,text=True,timeout=120)
    assert result.returncode==0,result.stderr
    receipt=json.loads((workspace/'cpu-isolation.json').read_bytes())
    assert receipt['status']=='ISOLATED' and receipt['network']=='UNSHARED'
    assert receipt['data_read_only'] and receipt['package_read_only']
    assert inventory(package)==before
    assert (workspace/'executions'/pin/'artifacts/result.txt').read_bytes()==(data/'synthetic.txt').read_bytes()
    execution=json.loads((workspace/'executions'/pin/'execution.json').read_bytes())
    assert execution['status']=='EXECUTED' and execution['scientifically_validated'] is False
    proof=json.loads((workspace/'input-verification'/(pin+'.json')).read_bytes())
    assert proof['status']=='VERIFIED' and proof['file_count']==len(payload['files'])
    assert proof['binding_sha256']==pin and proof['guard_sha256']==payload['guard_sha256']


def test_real_worker_to_existing_provider_collection(worker_files,candidate,tmp_path):
    from test_modal_fit_result import Volume, proof_fixture
    from orchestrator.modal_provider import ModalProvider
    from types import SimpleNamespace as NS
    package,inputs,progress,seal=worker_files
    _,config,binding,*_=candidate
    binding['experiment']['segment']=1;binding['outputs']=['result.txt','validation.json']
    pin=seal(binding,config);bound=json.loads((package/'manifest.json').read_bytes())['binding']
    config['item4_assets']['progress']=bound['progress']
    # SDK/filesystem are synthetic; actual worker, contracts, publisher, provider
    # status and collection consumers run without patching their implementations.
    volume=Volume(progress);sandbox=NS(object_id='sb-fit',poll=lambda:0)
    provider=object.__new__(ModalProvider);provider.config=config;provider.client='synthetic'
    provider.modal=NS(Volume=NS(from_name=lambda *a,**k:volume))
    provider._sandbox=lambda ident:sandbox
    proof_fixture(provider,bound,progress)
    assert worker.execute(package,inputs,progress,pin)['status']=='EXECUTED'
    assert provider.status('sb-fit',bound)['status']=='COMPLETE'
    receipt=provider.collect('sb-fit',bound,tmp_path/'collected')
    assert (tmp_path/'collected/result.txt').read_bytes()==(inputs/'synthetic.txt').read_bytes()
    assert receipt['input_verification']['status']=='VERIFIED'
    before=inventory(progress)
    assert provider.status('sb-fit',bound)['status']=='COMPLETE'
    assert inventory(progress)==before


def test_return_without_complete_native_checkpoint_is_failed(worker_files):
    from orchestrator.modal_fit_result import _result_key
    package,inputs,progress,seal=worker_files
    pr.write_text(package/'execution.py',"def main(i,o,c):\n    (o/'result.txt').write_text('synthetic only')\n    validation(o,c)\n" + VALIDATION_SOURCE)
    pin=seal();binding=json.loads((package/'manifest.json').read_bytes())['binding']
    with pytest.raises(ValueError,match='^FIT_PROGRESS_MISSING$'):
        worker.execute(package,inputs,progress,pin)
    assert json.loads((progress/'executions'/pin/'execution.json').read_bytes())['status']=='FAILED'
    pointer=json.loads((progress/'fits/fit'/(_result_key(binding)+'.json')).read_bytes())
    result=json.loads((progress/'fits/fit/objects'/pointer['object']/'data').read_bytes())
    assert result['status']=='FAILED' and result['files']=={}


def test_support_modules_cannot_be_changed_by_rebinding_manifest(reviewed):
    d,value,_=reviewed
    if d.config['item_number']!=4:return
    manifest,_=emit(d,value);folder=d.state/'modal-package';name='orchestrator/modal_fit_publication.py'
    pr.write_text(folder/name,'# changed synthetic helper')
    manifest['files'][name]=digest((folder/name).read_bytes())
    manifest['binding']['execution']['support_sha256'][name]=manifest['files'][name]
    manifest['binding']['code_sha256']=digest(canonical({k:v for k,v in manifest['files'].items() if k.endswith('.py')}))
    pr.write_bytes(folder/'manifest.json',canonical(manifest))
    with pytest.raises(ValueError,match='^EXPERIMENT_MODAL_SUPPORT_CHANGED$'):
        verify_package(folder,manifest['binding'])


def test_scientific_approval_requires_same_tested_support(reviewed):
    from orchestrator import experiment_approval
    d,value,_=reviewed
    if d.config['item_number']!=4:return
    folder=Path(value['notebook_revision_result']['folder'])/'synthetic/package'
    pr.write_text(folder/'orchestrator/modal_fit_publication.py','# altered test-only helper')
    with pytest.raises(ValueError,match='^EXPERIMENT_TEST_EVIDENCE_CHANGED$'):
        experiment_approval.record(d,value,value['pending'])


@pytest.mark.parametrize('damage',['failed-check','identifier','unbound-file'])
def test_remote_validation_refuses_before_any_result_payload_published(worker_files,damage):
    from orchestrator.modal_fit_result import _result_key, _key
    package,inputs,progress,seal=worker_files
    text=(package/'execution.py').read_text()
    if damage=='failed-check':text=text.replace("'status':'PASS'", "'status':'FAIL'")
    elif damage=='identifier':pr.write_text(inputs/'synthetic.txt','sub-'+'stroke0000')
    else:text=text.replace("'bytes':len(raw)", "'bytes':len(raw)+1")
    pr.write_text(package/'execution.py',text)
    pin=seal();binding=json.loads((package/'manifest.json').read_bytes())['binding']
    with pytest.raises(ValueError):worker.execute(package,inputs,progress,pin)
    root=progress/'fits/fit'
    assert not (root/(_key('result.txt')+'.json')).exists()
    assert not (root/(_key('validation.json')+'.json')).exists()
    pointer=json.loads((root/(_result_key(binding)+'.json')).read_bytes())
    result=json.loads((root/'objects'/pointer['object']/'data').read_bytes())
    assert result['status']=='FAILED' and result['files']=={}


def test_static_volume_is_uploaded_once_and_reused_for_resumed_manifest(reviewed,tmp_path,monkeypatch):
    from test_modal_assets import UploadVolume,adapter
    from orchestrator import modal_assets,connectivity
    d,value,_=reviewed
    if d.config['item_number']!=4:return
    manifest,base=emit(d,value);folder=d.state/'modal-package'
    binding=manifest['binding'];binding['package_volume_id']='vo-static';binding['experiment']['segment']=1
    pr.write_bytes(folder/'manifest.json',canonical(manifest))
    monkeypatch.setattr(connectivity,'require',lambda *args,**kwargs:None)
    volume=UploadVolume();provider=adapter(volume)
    def private_upload(path,remote,mode):
        assert mode==0o400
        volume.files[remote.lstrip('/')]=Path(path).read_bytes()
    volume.put_file=private_upload
    first=modal_assets.prepare_package(provider,binding,folder,tmp_path/'upload-1')
    assert first['status']=='READY' and 'manifest.json' not in volume.files and volume.uploads==1
    original=dict(volume.files)
    second=tmp_path/'package-2';pr.copytree(folder,second)
    resumed=json.loads(canonical(binding));resumed['experiment']['segment']=2
    resumed['resume']={'previous_segment_id':digest(canonical(binding)),
        'terminal_receipt_sha256':'a'*64,'checkpoint_record_sha256':'b'*64} # Transport fixture, not admission proof.
    next_manifest={'schema':'modal-run/v1','binding':resumed,'files':manifest['files']}
    pr.write_bytes(second/'manifest.json',canonical(next_manifest))
    assert bridge.manifest_for(resumed)==next_manifest
    result=modal_assets.prepare_package(provider,resumed,second,tmp_path/'upload-2')
    assert result['status']=='READY' and result['manifest_sha256']!=first['manifest_sha256']
    assert volume.files==original and volume.uploads==1
    # No partial, changed or extra payload is ever silently overwritten.
    volume.files['execution.py']=b'changed synthetic source'
    with pytest.raises(ValueError):modal_assets.prepare_package(provider,resumed,second,tmp_path/'upload-3')
    assert volume.uploads==1
