"""Synthetic bytes only; actual worker -> shared fit validator -> receipt sealer.

Only the fixed cohort hash is replaced by an explicitly synthetic 99-member
fixture. No validator, filesystem call or worker implementation is patched.
The environment proof is synthetic and labelled, not live dependency evidence.
"""
import json
import subprocess
import sys
import pytest
from orchestrator import experiment_preprocessing as prep, experiment_worker as worker
from orchestrator import experiment_modal_package as bridge, private_records as pr
from orchestrator import modal_item4_provider as fit
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest, inventory
from orchestrator.modal_scientific_environment import environment_bytes

SOURCE = r"""
def preprocess(input_root, output_root, contract):
    import hashlib, json
    b=contract['runtime'];s=contract['preprocessing']
    files={};cases={}
    def emit(path, raw):
        target=output_root/path;target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():target.write_bytes(raw)
        assert target.read_bytes()==raw
        item={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
        files[path]=item
        return {'path':path,**item}
    for case in contract['cohort']['cases']:
        cases[case]={role:emit('Dataset/plan/'+case+suffix,b'synthetic '+role.encode())
            for role,suffix in [('image','.b2nd'),('segmentation','_seg.b2nd'),('properties','.pkl')]}
        if case not in contract['completed_steps']:
            contract['checkpoint'](case,{v['path']:files[v['path']] for v in cases[case].values()})
    shared={role:emit('Dataset/'+name,b'synthetic '+role.encode()) for role,name in
        [('dataset','dataset.json'),('plans','plans.json'),('splits','splits_final.json')]}
    if 'shared' not in contract['completed_steps']:
        contract['checkpoint']('shared',{v['path']:files[v['path']] for v in shared.values()})
    proposed={'schema':'modal-item4-preprocessed/v1','status':'VALIDATED',
        'cohort_sha256':s['cohort_sha256'],'source_capture_sha256':s['source_capture_sha256'],
        'input_contract_sha256':s['input_contract_sha256'],'environment_sha256':s['environment_sha256'],
        'plans_sha256':shared['plans']['sha256'],'preprocessing_code_sha256':b['execution']['module_sha256'],
        'case_files':cases,'shared_files':shared}
    validation={'schema':'modal-preprocessing-validation/v1','status':'PASS','errors':[],
        'run_id':b['run_id'],'spec_sha256':b['spec_sha256'],
        'preprocessing_code_sha256':b['execution']['module_sha256'],'validator_sha256':b['execution']['module_sha256'],
        'cohort_sha256':s['cohort_sha256'],'input_contract_sha256':s['input_contract_sha256'],
        'environment_sha256':s['environment_sha256'],'files':files}
    contract['_synthetic_return']={'proposed':proposed,'validation':validation}

def validate_preprocessing(output_root, contract):
    return contract['_synthetic_return']
"""

@pytest.fixture
def prepared(tmp_path,monkeypatch):
    root=tmp_path/'private';pr.mkdir(root)
    package=root/'package';inputs=root/'inputs';progress=root/'progress'
    for p in (package,inputs,progress):pr.mkdir(p)
    pr.write_bytes(inputs/'synthetic.txt',b'synthetic source only')
    cohort=canonical({'cases':['sub-stroke'+str(n) for n in range(9000,9099)]})
    monkeypatch.setattr(prep,'COHORT',digest(cohort))
    monkeypatch.setattr(fit,'COHORT',digest(cohort))
    filemap={'synthetic.txt':{'sha256':digest((inputs/'synthetic.txt').read_bytes()),'bytes':len((inputs/'synthetic.txt').read_bytes())}}
    expected={'python':sys.version,'cuda':None,'packages':{'synthetic-fixture':'1.0'}}
    environment={'schema':'offline-scientific-python/v1','python_executable':'/usr/bin/python3',
        'expected':expected,'wheels':{'synthetic_fixture-1.0-py3-none-any.whl':{'sha256':'a'*64,'bytes':1}}}
    selection={'schema':'reviewed-preprocessing/v1','id':'synthetic-preprocessing',
        'input_contract_sha256':digest(canonical(filemap)),
        'environment_sha256':digest(environment_bytes(expected)),
        'split_sha256':digest(b'synthetic splits'),'plans_name':'plans',
        'cohort_sha256':digest(cohort),'source_capture_sha256':prep.SOURCE}
    plan={'preprocessing':[selection],'synthetic_fixture':True}
    files={'run.py':bridge.WORKER.read_bytes(),'execution.py':SOURCE.encode(),
        'SPEC.md':b'synthetic-only','review.json':b'{}','approval.json':b'{"synthetic_fixture":true}',
        'reviewed-package.json':b'{"synthetic_fixture":true}',
        'execution-plan.json':canonical(plan),'cohort.json':cohort,'input-inventory.json':canonical(filemap),
        **bridge.support_files()}
    for name,raw in files.items():pr.write_bytes(package/name,raw)
    def seal():
        pins={name:digest((package/name).read_bytes()) for name in files}
        binding={'purpose':'M4_ITEM4','run_id':'synthetic-preprocessing-run',
            'spec_sha256':pins['SPEC.md'],'review_sha256':pins['review.json'],
            'execution_plan_sha256':pins['execution-plan.json'],
            'code_sha256':digest(canonical({k:v for k,v in pins.items() if k.endswith('.py')})),
            'preprocessing':selection,'scientific_environment':environment,
            'resources':{'gpu':None},'experiment':{'stage':'SMOKE'},
            'execution':{'schema':'reviewed-module/v1','module':'execution.py',
                'module_sha256':pins['execution.py'],'worker_sha256':pins['run.py'],
                'approval_sha256':pins['approval.json'],'package_manifest_sha256':pins['reviewed-package.json'],
                'support_sha256':{name:pins[name] for name in worker.SUPPORT_FILES}}}
        ident=digest(canonical(binding))
        pr.write_bytes(package/'manifest.json',canonical({'schema':'modal-run/v1','binding':binding,'files':pins}))
        proof={'schema':'scientific-environment-proof/v1','binding_sha256':ident,
            'expected_sha256':digest(environment_bytes(expected)),'actual':expected,'offline':True}
        pr.write_bytes(progress/'environment-verification'/ident/'environment.json',environment_bytes(proof))
        return binding,ident
    return root,package,inputs,progress,seal


def test_worker_preprocessing_to_exact_fit_consumer_and_original_receipt_seal(prepared):
    from orchestrator.modal_preprocessing_receipt import seal as seal_receipt
    root,package,inputs,progress,seal=prepared;binding,pin=seal()
    result=worker.execute(package,inputs,progress,pin)
    assert result['status']=='VALIDATED' and result['files']==300 and result['steps']==100
    assert result['scientifically_accepted'] is result['fit_completed'] is False
    attempt=progress/'preprocessing'/pin
    proposed=json.loads((attempt/'preprocessing.json').read_bytes())
    validation=json.loads((attempt/'validation.json').read_bytes())
    original=json.loads((attempt/'author-validation.json').read_bytes())
    assert original=={'proposed':proposed,'validation':validation}
    selected=binding['preprocessing']
    assets={'preprocessing_code_sha256':binding['execution']['module_sha256'],
        'split_sha256':selected['split_sha256'],'plans_name':selected['plans_name']}
    fit_binding={**binding,'experiment':{**binding['experiment'],'fit_id':'fit'},'progress':{'volume_id':'vo-progress','volume_name':'progress','fit_id':'fit',
        'fit_binding':{'run_id':binding['run_id'],'arm':'synthetic','fold':0,'realization':'one',
            'spec_sha256':binding['spec_sha256'],'code_sha256':binding['code_sha256'],
            **{k:proposed[k] for k in ('input_contract_sha256','environment_sha256','plans_sha256')}}}}
    assert fit.validate_inputs(proposed,(package/'cohort.json').read_bytes(),assets,fit_binding)==validation['files']
    receipt=seal_receipt(attempt/'artifacts',root/'sealed.json',proposed=proposed,
        cohort_raw=(package/'cohort.json').read_bytes(),assets=assets,binding=fit_binding,
        validator_path=package/'execution.py',validator_sha256=binding['execution']['module_sha256'],
        validation_path=attempt/'validation.json',validation_sha256=digest((attempt/'validation.json').read_bytes()))
    assert receipt['files']==300 and receipt['scientific_acceptance'] is False
    assert (root/'sealed.json').read_bytes()==(attempt/'preprocessing.json').read_bytes()
    before=inventory(progress)
    with pytest.raises(FileExistsError):worker.execute(package,inputs,progress,pin)
    assert inventory(progress)==before
    fit_binding['progress']['fit_binding']['plans_sha256']='f'*64
    with pytest.raises(ValueError,match='^ITEM4_PREPROCESSING_FIT_BINDING$'):
        fit.validate_inputs(proposed,(package/'cohort.json').read_bytes(),assets,fit_binding)


@pytest.mark.parametrize('damage,code',[
    ('invalid','ITEM4_PREPROCESSING_VALIDATOR_REFUSED'),
    ('wrong-run','ITEM4_PREPROCESSING_VALIDATOR_SCOPE'),
    ('missing-checkpoints','EXPERIMENT_PREPROCESSING_UNCOMMITTED_OUTPUTS'),
    ('changed-output','INPUT_GUARD_HASH'),
    ('unsafe','PRIVATE_RECORD_PERMISSIONS'),
    ('wrong-plan','ITEM4_PREPROCESSING_PLAN_OR_SPLIT'),
    ('overlap','EXPERIMENT_PREPROCESSING_STEP_OVERLAP')])
def test_real_worker_preserves_failed_validation_and_never_repeats(prepared,damage,code):
    root,package,inputs,progress,seal=prepared
    extra={'invalid':"contract['_synthetic_return']['validation']['status']='FAIL'",
        'wrong-run':"contract['_synthetic_return']['validation']['run_id']='other'",
        'changed-output':"(output_root/'Dataset/dataset.json').write_bytes(b'x'*len(b'synthetic dataset'))",
        'unsafe':"(output_root/'Dataset/dataset.json').chmod(0o644)",
        'wrong-plan':"contract['_synthetic_return']['proposed']['plans_sha256']='f'*64",
        'overlap':"contract['checkpoint']('overlap', contract['_synthetic_return']['validation']['files'])"}
    source=SOURCE
    if damage=='missing-checkpoints':
        source='\n'.join(line[:len(line)-len(line.lstrip())]+'pass' if "contract['checkpoint'](" in line else line for line in source.splitlines())
    else:source=source.replace("    return contract['_synthetic_return']",'    '+extra[damage]+"\n    return contract['_synthetic_return']")
    pr.write_text(package/'execution.py',source);binding,pin=seal()
    with pytest.raises(ValueError,match='^'+code+'$'):worker.execute(package,inputs,progress,pin)
    attempt=progress/'preprocessing'/pin
    assert not (attempt/'result.json').exists()
    failed=json.loads((attempt/'failed.json').read_bytes())
    assert failed['status']=='FAILED' and failed['may_retry'] is False
    before=inventory(progress)
    with pytest.raises(FileExistsError):worker.execute(package,inputs,progress,pin)
    assert inventory(progress)==before


@pytest.mark.parametrize('damage,code',[('source','INPUT_GUARD_HASH'),
    ('environment','SCIENTIFIC_ENVIRONMENT_PROOF'),('gpu','EXPERIMENT_PREPROCESSING_CPU_ONLY'),
    ('plan','EXPERIMENT_PREPROCESSING_PLAN_BINDING')])
def test_refusal_before_scientific_import(prepared,damage,code):
    root,package,inputs,progress,seal=prepared
    pr.write_text(package/'execution.py',"raise AssertionError('never import')")
    binding,pin=seal()
    if damage=='source':pr.write_bytes(inputs/'synthetic.txt',b'x'*len(b'synthetic source only'))
    if damage=='environment':
        path=progress/'environment-verification'/pin/'environment.json'
        proof=json.loads(path.read_bytes());proof['offline']=False;pr.write_bytes(path,canonical(proof))
    if damage in {'gpu','plan'}:
        manifest=json.loads((package/'manifest.json').read_bytes())
        if damage=='gpu':manifest['binding']['resources']['gpu']='H100'
        else:
            plan=json.loads((package/'execution-plan.json').read_bytes());plan['preprocessing'][0]['id']='different-selection'
            pr.write_bytes(package/'execution-plan.json',canonical(plan))
            manifest['files']['execution-plan.json']=manifest['binding']['execution_plan_sha256']=digest(canonical(plan))
        pin=digest(canonical(manifest['binding']));pr.write_bytes(package/'manifest.json',canonical(manifest))
    with pytest.raises(ValueError,match='^'+code+'$'):worker.execute(package,inputs,progress,pin)
    assert not (progress/'preprocessing').exists()


def test_packaged_module_closure_imports_without_controller_or_site_packages(prepared):
    _,package,*_=prepared
    code="import sys;sys.path.insert(0,sys.argv[1]);import orchestrator.experiment_preprocessing;assert 'orchestrator.manual_driver' not in sys.modules;assert 'modal' not in sys.modules"
    out=subprocess.run([sys.executable,'-I','-B','-c',code,str(package)],capture_output=True,text=True,timeout=20)
    assert out.returncode==0,out.stderr


@pytest.mark.parametrize('change,code',[
    ("contract['checkpoint']('shared',{})",'EXPERIMENT_PREPROCESSING_STEP'),
    ("contract['_synthetic_return']['validation']['errors']=['synthetic failure']",'ITEM4_PREPROCESSING_VALIDATOR_REFUSED'),
    ("contract['_synthetic_return']['extra']='unreviewed'",'EXPERIMENT_PREPROCESSING_RETURN'),
    ("contract['_synthetic_return']['validation']['files']={}",'ITEM4_PREPROCESSING_VALIDATOR_OUTPUTS')])
def test_ambiguous_author_results_never_become_validation(prepared,change,code):
    _,package,inputs,progress,seal=prepared
    source=SOURCE.replace("    return contract['_synthetic_return']",'    '+change+"\n    return contract['_synthetic_return']")
    pr.write_text(package/'execution.py',source);_,pin=seal()
    with pytest.raises(ValueError,match='^'+code+'$'):worker.execute(package,inputs,progress,pin)
    assert (progress/'preprocessing'/pin/'failed.json').is_file()
    assert not (progress/'preprocessing'/pin/'result.json').exists()


def test_execution_failure_preserves_completed_steps_without_fit_checkpoint(prepared):
    _,package,inputs,progress,seal=prepared
    source=SOURCE.replace("    shared={role:emit", "    raise RuntimeError('synthetic interruption after durable case outputs')\n    shared={role:emit")
    pr.write_text(package/'execution.py',source);_,pin=seal()
    with pytest.raises(RuntimeError,match='synthetic interruption'):worker.execute(package,inputs,progress,pin)
    attempt=progress/'preprocessing'/pin
    assert len(list((attempt/'steps').glob('*.json')))==99
    assert json.loads((attempt/'failed.json').read_bytes())['completed_steps']==99
    assert not (progress/'fits').exists()
    assert not (attempt/'validation.json').exists()


def test_full_worker_subprocess_uses_only_packaged_support(prepared):
    _,package,inputs,progress,seal=prepared;binding,pin=seal()
    # Synthetic cohort substitution only, identical to the portable fixture.
    # All worker and contract implementations run unchanged in a fresh process.
    script=("import sys;sys.path.insert(0,sys.argv[1]);"
        "from orchestrator import experiment_preprocessing as p;"
        "p.COHORT=sys.argv[5];import run;"
        "r=run.execute(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]);"
        "assert r['status']=='VALIDATED' and r['files']==300;"
        "assert 'orchestrator.manual_driver' not in sys.modules and 'modal' not in sys.modules")
    out=subprocess.run([sys.executable,'-I','-B','-c',script,str(package),str(inputs),str(progress),pin,
        binding['preprocessing']['cohort_sha256']],capture_output=True,text=True,timeout=60)
    assert out.returncode==0,out.stderr
    assert (progress/'preprocessing'/pin/'result.json').is_file()


def test_preprocessing_package_reconstruction_and_real_verifier(prepared):
    from orchestrator.modal_executor import verify_package
    _,package,_,progress,seal=prepared
    binding,_=seal()
    from orchestrator.modal_item4_budget import AUTHORITY,TEAM_AUTHORITY
    pr.write_bytes(package/'review.json',canonical({'verdict':'APPROVE','findings':[],
        'rationale':'Synthetic fixture only, not a scientific judgment.'}))
    binding['review_sha256']=digest((package/'review.json').read_bytes())
    source='a'*40
    selection={'item_number':4,'run_id':binding['run_id'],'plan_sha256':binding['execution_plan_sha256']}
    spec=('run_id: '+binding['run_id']+'\nexecution_plan_sha256: '+binding['execution_plan_sha256']+'\n').encode()
    pr.write_bytes(package/'SPEC.md',spec)
    approval={'selection':selection,'execution_admitted':False,
        'code_files':{'execution.py':{'sha256':binding['execution']['module_sha256']}},
        'review_sha256':binding['review_sha256'],'synthetic_fixture':True}
    pr.write_bytes(package/'approval.json',canonical(approval))
    sealed={'schema':'experiment-package/v1','source':source,'selection':selection,
        'reviewed_execution_sha256':digest(canonical(approval)),
        'files':{name:digest((package/name).read_bytes()) for name in
            ('SPEC.md','review.json','execution-plan.json','approval.json')},'synthetic_fixture':True}
    sealed['files']['code/execution.py']=binding['execution']['module_sha256']
    pr.write_bytes(package/'reviewed-package.json',canonical(sealed))
    binding,pin=seal();binding['source']=source
    binding['experiment'].update(backlog_item=4,authority_sha256=AUTHORITY,team_authority_sha256=TEAM_AUTHORITY)
    manifest=json.loads((package/'manifest.json').read_bytes());manifest['binding']=binding
    pr.write_bytes(package/'manifest.json',canonical(manifest))
    assert verify_package(package,binding)==manifest
    assert bridge.manifest_for(binding)==manifest
    # An internally rehashed map still cannot replace the reviewed plan's input identity.
    pr.write_bytes(package/'input-inventory.json',canonical({'unreviewed':{'bytes':1,'sha256':'f'*64}}))
    manifest['files']['input-inventory.json']=digest((package/'input-inventory.json').read_bytes())
    pr.write_bytes(package/'manifest.json',canonical(manifest))
    with pytest.raises(ValueError,match='^EXPERIMENT_PREPROCESSING_INPUT_BINDING$'):
        verify_package(package,binding)
