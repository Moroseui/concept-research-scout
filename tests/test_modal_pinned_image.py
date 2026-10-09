"""Synthetic provider only; real owner, budget, controller and receipt checks."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace as NS
import sys
import pytest
from orchestrator import modal_pinned_image as image
from orchestrator import modal_environment_budget as budget, modal_environment_provider as native
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from tools import pinned_image_builder as worker
from test_modal_environment_provider import fixture as inventory_fixture, Stream
from test_modal_direct_budget import billing,NOW
from test_experiment_context import experiment,root
from test_experiment_revisions import as_item4


def selected():
    names={'numpy','pandas','scipy','scikit-learn','torch','matplotlib','psutil','nibabel','xgboost','nnunetv2','simpleitk','dynamic-network-architectures','batchgeneratorsv2','acvl-utils','setuptools','wheel','packaging'}
    packages={n:'1.0' for n in names};packages.update(nnunetv2='2.8.1',torch='2.11.0+cu128')
    return {'schema':'pinned-modal-image-selection/v1','python_executable':'/opt/conda/bin/python',
        'python_version':'3.12.11','cuda':'12.8','packages':packages,'hashes':{n:['1'*64] for n in names}}


def view():
    from orchestrator.modal_billing import canonical as billing_bytes
    value=billing();value['rates'].update(cpu_hour_cost='0.04730',mem_gib_hour_cost='0.00800')
    value.pop('sha256');value['sha256']=digest(billing_bytes(value));return value


def result(binding):
    selection=binding['image_build']
    proof={'schema':'pinned-modal-image-native/v1','selection_sha256':digest(worker.encoded(selection)),
        'builder_sha256':image.worker_sha256(),'lock_sha256':digest(worker.selection(selection).encode()),
        'actual':{'python':'3.12.11 (synthetic native fixture)','cuda':'12.8','packages':selection['packages']},
        'imports':{n:n for n in worker.IMPORTS},'trainers':{n:worker.PARAMETERS for n in worker.TRAINERS},
        'reader':'SimpleITKIO','console_help':{n:{'exit_code':0,'stdout_sha256':'2'*64,'stderr_sha256':digest(b''),'usage_seen':True} for n in worker.CONSOLES},
        'patient_computation':False,'gpu_verified':False}
    return {'schema':'pinned-image-verified/v1','image_id':'im-Built','binding_sha256':digest(canonical(binding)),
        'native_sha256':digest(worker.encoded(proof)),'native':proof}


@pytest.fixture
def unreserved_fixture(inventory_fixture,experiment,monkeypatch):
    f=inventory_fixture
    # Replace only this disposable fixture's prior inventory setup, before use.
    for table in ('autonomy_assets','autonomy_runs','events'):f.accounts.db.execute('DELETE FROM '+table)
    f.binding.update(purpose=image.PURPOSE,operation_id=image.OPERATION,run_id=image.RUN,
        worker_sha256=image.worker_sha256(),image_build=selected(),envelope=image.envelope(view()['rates']))
    # Exact canonical scientific owner and private lane; only the scientific
    # content/provider judgment is synthetic, not the owner/accounting verifier.
    d,_=experiment;as_item4(d)
    d.config.update(source=f.binding['source'],context=str(d.context))
    owner={'state':str(d.state),'source':d.config['source'],'run_id':image.RUN,
        'plan_sha256':d.config['plan_sha256'],'review_sha256':'c'*64,'execution_scope':d.config['execution_scope']}
    d.config.update(owner_binding=owner,engine_review={'sha256':'c'*64})
    pr.atomic(d.state/'lane.json',d.config)
    f.accounts.batch.register_experiment_run(image.RUN,owner)
    f.binding['owner_sha256']=digest(canonical(owner));f.owner_driver=d;f.original_owner=owner
    f.sb.stdout=Stream([canonical(result(f.binding))]);f.provider.billing_snapshot=view
    def run_function(fn,**kw):
        f.calls.append(('build-function',fn,kw))
        return NS(object_id='im-Built',build=lambda app:f.calls.append(('build-image',app.app_id)))
    f.image.run_function=run_function
    # Only the paid SDK's source-info object is synthetic; controller checks the
    # real staged standalone file and verifies its bytes before this handoff.
    class SourceInfo:
        def __init__(self,fn):self.fn=fn;self._type=NS(name='FILE')
        def get_entrypoint_mount(self):return {'builder':NS(_entries=[NS(local_file=Path(self.fn.__code__.co_filename))])}
    monkeypatch.setitem(sys.modules,'modal._utils.function_utils',NS(FunctionSourceInfo=SourceInfo))
    return f


@pytest.fixture
def fixture(unreserved_fixture):
    f=unreserved_fixture
    assert budget.reserve(f.accounts,digest(canonical(f.binding)),image.RUN,f.binding,billing_snapshot=view(),now=NOW)
    return f


def test_real_reservation_to_build_to_proof_and_private_replay(fixture):
    f=fixture;handle=native.launch(f.provider,f.accounts,f.binding,f.root)
    built=next(x for x in f.calls if x[0]=='build-function');kw=built[2]
    assert kw['cpu']==(2,2) and kw['memory']==(8192,8192) and kw['timeout']==1800
    assert kw['secrets']==[] and kw['volumes']==kw['network_file_systems']=={} and kw['gpu'] is None
    assert built[1].__module__=='research_pinned_image_builder'
    intent=json.loads((f.root/'build-intent.json').read_bytes())
    assert set(intent['source_manifest']['files'])=={'pinned_image_builder.py'}
    create=next(x for x in f.calls if x[0]=='create');args,run=create[1:]
    assert args[0]==worker.TARGET+'/bin/python'
    assert run['block_network'] is True and run['volumes']=={} and run['secrets']==[]
    assert run['include_oidc_identity_token'] is False and run['gpu'] is None
    value=native.observe(f.provider,f.binding,handle,f.root)
    assert value['status']=='VERIFIED' and value['pinned_image']==result(f.binding)
    calls=list(f.calls);assert native.observe(None,f.binding,handle,f.root)==value;assert calls==f.calls
    spec=image.consumer_spec(value['pinned_image'],f.binding)
    assert spec['image_id']=='im-Built' and spec['expected']==value['pinned_image']['native']['actual']
    assert f.accounts.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    assert f.accounts.db.execute('SELECT reserved_micro_usd FROM autonomy_assets').fetchone()[0]==f.binding['envelope']['cost']['reserved_micro_usd']
    assert all(p.stat().st_mode&0o077==0 for p in f.root.rglob('*'))


def test_one_build_intent_uncertainty_never_rebuilds(fixture):
    f=fixture
    def fail(*a,**kw):raise RuntimeError('synthetic build lost transport')
    f.image.run_function=fail
    with pytest.raises(RuntimeError):native.launch(f.provider,f.accounts,f.binding,f.root)
    assert (f.root/'build-intent.json').is_file() and not (f.root/'sandbox.json').exists()
    calls=list(f.calls)
    with pytest.raises(ValueError,match='^ENVIRONMENT_EXISTING_INTENT_RECONCILE$'):native.launch(f.provider,f.accounts,f.binding,f.root)
    assert f.calls==calls


@pytest.mark.parametrize('part',['image_id','native_sha256','builder_sha256','selection_sha256','lock_sha256','cuda','packages','console','trainers'])
def test_bad_native_binding_refused(fixture,part):
    f=fixture;value=result(f.binding)
    if part in {'image_id','native_sha256'}:value[part]='bad'
    elif part in {'builder_sha256','selection_sha256','lock_sha256'}:value['native'][part]='3'*64
    elif part=='cuda':value['native']['actual']['cuda']='11.8'
    elif part=='packages':value['native']['actual']['packages']=dict(value['native']['actual']['packages'],nnunetv2='2.8.0')
    elif part=='console':value['native']['console_help'][worker.CONSOLES[0]]['usage_seen']=False
    else:value['native']['trainers']={}
    if part not in {'native_sha256'}:value['native_sha256']=digest(worker.encoded(value['native']))
    with pytest.raises(ValueError):image.validate_result(canonical(value),f.binding)


@pytest.mark.parametrize('bad',['missing','unpinned','url','extra','wrong_nnunet','python','alias'])
def test_selection_is_exact_and_non_executable(bad):
    v=selected()
    if bad=='missing':v['hashes'].pop('torch')
    elif bad=='unpinned':v['packages']['torch']='>=2.0'
    elif bad=='url':v['hashes']['torch']=['https://example.invalid/x']
    elif bad=='extra':v['command']='echo wrong'
    elif bad=='wrong_nnunet':v['packages']['nnunetv2']='2.8.0'
    elif bad=='python':v['python_version']='3.12'
    else:v['python_executable']='/opt/../private/bin/python'
    with pytest.raises(ValueError):image.validate(v)


def test_rate_envelope_uses_function_plus_sandbox_and_full_overhead():
    value=image.envelope(view()['rates']);cost=value['cost']
    assert cost['overhead_micro_usd']==1000000 and cost['reserved_micro_usd']==cost['compute_micro_usd']+1000000
    assert {'cpu_hour_cost','mem_gib_hour_cost','cpu_hour_cost_sandbox','mem_gib_hour_cost_sandbox'}==set(cost['rates'])
    rates=view()['rates'];del rates['cpu_hour_cost']
    with pytest.raises(ValueError,match='^PINNED_IMAGE_ACTUAL_BUILD_RATES_REQUIRED$'):image.envelope(rates)


def test_pip_and_probe_receive_no_ambient_credentials(monkeypatch):
    monkeypatch.setenv('SYNTHETIC_PRIVATE_TOKEN','never forwarded')
    env=worker.safe_environment();assert 'SYNTHETIC_PRIVATE_TOKEN' not in env
    assert not any('TOKEN' in k or 'KEY' in k for k in env)


from test_modal_item4_provider import candidate
from orchestrator import private_records as pr
from orchestrator import modal_scientific_environment as environment


def completed_proof(f):
    state=f.root.parent/'image-state';pr.mkdir(state);f.root=state/'provider'
    handle=native.launch(f.provider,f.accounts,f.binding,f.root)
    observed=native.observe(f.provider,f.binding,handle,f.root)
    complete={**observed,'binding_sha256':digest(canonical(f.binding)),'source':f.binding['source'],'scientific_calls':0,
              'scope':'Pinned image and CPU native checks only; no patient computation or GPU validation'}
    pr.write_bytes(state/'VERIFIED.json',canonical(complete))
    f.accounts.finish_assets(digest(canonical(f.binding)),'READY',complete)
    return state,image.consumer_proof(f.accounts,f.binding,state)


def install_synthetic_provenance(f,c,b,folder,monkeypatch):
    from orchestrator import manual_host_guard
    state,proof=completed_proof(f);path=folder/'image-provenance.json';pr.write_bytes(path,canonical(proof))
    # Only root ownership is simulated. Actual file, hash, complete proof, native
    # validation, config/spec and image binding all pass through real code.
    monkeypatch.setattr(manual_host_guard,'trusted',lambda p:pr.check(p))
    for item in (c,b):
        item.pop('wheel_volume_id',None);item.pop('wheel_files',None)
        item['image_id']=proof['scientific_environment']['image_id'];item['scientific_environment']=proof['scientific_environment']
    c['pinned_image_provenance']={'path':str(path),'sha256':digest(path.read_bytes())}
    b['runtime_sha256']=digest(canonical(c))
    return state,proof,path


def test_ready_producer_required_not_just_an_image_id(fixture):
    f=fixture
    with pytest.raises(ValueError,match='^PINNED_IMAGE_READY_PROVENANCE_REQUIRED$'):
        image.consumer_proof(f.accounts,f.binding,f.root)
    state,proof=completed_proof(f)
    assert proof['scientific_environment']['image_id']=='im-Built' and proof['gpu_verified'] is False
    f.accounts.db.execute("UPDATE autonomy_assets SET status='UNCERTAIN'")
    with pytest.raises(ValueError,match='^PINNED_IMAGE_READY_PROVENANCE_REQUIRED$'):
        image.consumer_proof(f.accounts,f.binding,state)


@pytest.mark.parametrize('damage',[None,'proof','image','wheel','versions'])
def test_actual_fit_create_checks_image_proof_and_uses_three_roles(fixture,candidate,monkeypatch,damage):
    f=fixture;p,c,b,package,volumes,created,app,receipt,folder,ws=candidate
    _,proof,path=install_synthetic_provenance(f,c,b,folder,monkeypatch)
    b['progress']['fit_binding']['environment_sha256']=digest(environment.environment_bytes(b['scientific_environment']['expected']))
    b['runtime_sha256']=digest(canonical(c))  # progress is shared with this synthetic runtime
    if damage=='proof':pr.write_bytes(path,b'{}')
    elif damage=='image':b['image_id']='im-Wrong'
    elif damage=='wheel':b['wheel_volume_id']='vo-Wrong'
    elif damage=='versions':b['scientific_environment']=copy.deepcopy(b['scientific_environment']);b['scientific_environment']['expected']['packages']['torch']='wrong'
    if damage:
        with pytest.raises(ValueError):p.create(c,b,package)
        assert created==[];return
    assert p.create(c,b,package)['provider_id']=='sb-synthetic'
    args,kw=created[0]
    assert set(kw['volumes'])=={'/preprocessed','/reviewed','/progress'}
    assert kw['block_network'] is True and kw['include_oidc_identity_token'] is False and kw['secrets']==[]
    assert volumes['vo-wheels'].reads==[] and volumes['vo-wheels'].read_only is None


@pytest.mark.parametrize('damage',[None,'version','native-hash'])
def test_native_job_records_actual_versions_without_wheels_or_install(tmp_path,damage):
    """Real bubblewrap/interpreter/metadata proof; packages are synthetic stubs."""
    import os,shutil,subprocess
    bwrap=shutil.which('bwrap')
    if not bwrap:pytest.skip('native bubblewrap unavailable')
    root=tmp_path/'synthetic-image';progress=tmp_path/'progress';pr.mkdir(root);pr.mkdir(progress)
    version=subprocess.check_output(['/usr/bin/python3','-I','-c','import sys;print(sys.version)'],text=True).strip()
    minor='.'.join(version.split(' ')[0].split('.')[:2])
    chosen=selected();chosen['python_version']=version.split(' ')[0]
    site=root/'lib'/('python'+minor)/'site-packages';pr.mkdir(site,parents=True);pr.mkdir(root/'bin')
    (root/'bin/python').symlink_to('/usr/bin/python3')
    pr.write_text(root/'pyvenv.cfg','home = /usr/bin\ninclude-system-site-packages = false\nversion = '+version.split(' ')[0]+'\n')
    for n,v in chosen['packages'].items():
        dist=site/(n.replace('-','_')+'-'+v+'.dist-info');pr.mkdir(dist)
        pr.write_text(dist/'METADATA','Metadata-Version: 2.1\nName: '+n+'\nVersion: '+v+'\n')
    pr.mkdir(site/'torch');pr.write_text(site/'torch/__init__.py',"from types import SimpleNamespace\nversion=SimpleNamespace(cuda='12.8')\n")
    native_raw=b'synthetic native image proof, not a real Modal result';pr.write_bytes(root/'native-proof.json',native_raw)
    spec={'schema':'modal-pinned-image/v1','python_executable':worker.TARGET+'/bin/python','image_id':'im-Synthetic',
        'base_image':fixture_base(),'builder_sha256':'a'*64,'selection_sha256':'b'*64,'native_sha256':digest(native_raw),
        'expected':{'python':version,'cuda':'12.8','packages':chosen['packages']}}
    if damage=='version':spec['expected']['packages']=dict(spec['expected']['packages'],torch='0.0')
    elif damage=='native-hash':spec['native_sha256']='0'*64
    code=Path(environment.__file__).read_text()+"\nspec=json.loads(sys.argv[1]);environment_prepare(spec,None,Path('/progress'),'a'*64,lambda *a:(_ for _ in ()).throw(RuntimeError('wheel access forbidden')))\n"
    args=[bwrap,'--unshare-all','--die-with-parent','--new-session','--ro-bind','/usr','/usr',
        '--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/opt','--ro-bind',str(root),worker.TARGET,'--bind',str(progress),'/progress']
    for lib in ('/lib','/lib64'):
        if Path(lib).exists():args+=['--ro-bind',str(Path(lib).resolve()),lib]
    args+=[worker.TARGET+'/bin/python','-I','-B','-c',code,json.dumps(spec)]
    run=subprocess.run(args,capture_output=True,text=True,timeout=30)
    if damage:
        assert run.returncode!=0 and not (progress/'environment.json').exists();return
    assert run.returncode==0,run.stderr
    assert not (progress/'environment-install.log').exists()
    receipt=json.loads((progress/'environment.json').read_bytes())
    assert receipt['actual']==spec['expected'] and receipt['image_id']=='im-Synthetic'
    assert receipt['native_sha256']==digest(native_raw) and receipt['offline'] is True
    binding={'scientific_environment':spec};receipt['binding_sha256']=digest(json.dumps(binding,sort_keys=True).encode())
    assert environment.environment_proof(json.dumps(receipt).encode(),binding)['actual']==spec['expected']


def fixture_base():
    from orchestrator.modal_assets import BASE_IMAGE
    return BASE_IMAGE


@pytest.mark.parametrize('damage',[None,'duplicate','trainer','console'])
def test_native_checks_execute_fixed_help_and_trainer_contract(tmp_path,monkeypatch,damage):
    """Real local console subprocesses; imports/metadata explicitly synthetic."""
    import subprocess
    chosen=selected();chosen['python_version']='.'.join(map(str,sys.version_info[:3]))
    target=tmp_path/'synthetic-native';pr.mkdir(target/'bin',parents=True)
    monkeypatch.setattr(worker,'TARGET',str(target))
    called=target/'called.txt'
    for n in worker.CONSOLES:
        code="#!/usr/bin/python3\nfrom pathlib import Path\nPath("+repr(str(called))+ ").open('a').write("+repr(n+'\n')+")\nprint('usage: synthetic help')\n"
        if damage=='console' and n==worker.CONSOLES[0]:code+='raise SystemExit(7)\n'
        path=target/'bin'/n;pr.write_text(path,code);path.chmod(0o700)
    class Trainer:
        def __init__(self,plans,configuration,fold,dataset_json,device):pass
    class Reader:
        def read_images(self):pass
        def read_seg(self):pass
    trainers=NS(**{n:Trainer for n in worker.TRAINERS})
    if damage=='trainer':trainers.nnUNetTrainer_5epochs=type('Wrong',(),{})
    def imported(n):
        if n=='torch':return NS(__name__=n,version=NS(cuda='12.8'))
        if n.endswith('nnUNetTrainer_Xepochs'):return trainers
        if n.endswith('simpleitk_reader_writer'):return NS(SimpleITKIO=Reader)
        return NS(__name__=n)
    monkeypatch.setattr(worker.importlib,'import_module',imported)
    monkeypatch.setattr(worker.metadata,'version',lambda n:chosen['packages'][n])
    rows=[NS(metadata={'Name':n},version=v) for n,v in chosen['packages'].items()]
    if damage=='duplicate':rows.append(rows[0])
    monkeypatch.setattr(worker.metadata,'distributions',lambda:rows)
    if damage:
        with pytest.raises((ValueError,subprocess.CalledProcessError)):worker.native(chosen)
    else:
        value=worker.native(chosen)
        assert called.read_text().splitlines()==list(worker.CONSOLES)
        assert value['trainers']=={n:worker.PARAMETERS for n in worker.TRAINERS}
        assert all(row['usage_seen'] for row in value['console_help'].values())


def test_build_installs_only_hash_pinned_tools_then_source_archive(tmp_path,monkeypatch):
    """Command graph only; does not install packages or claim native evidence."""
    target=tmp_path/'not-built';monkeypatch.setattr(worker,'TARGET',str(target));monkeypatch.setattr(worker,'PROOF',str(target/'native-proof.json'))
    chosen=selected();seen=[]
    def run(args,**kwargs):
        seen.append((args,kwargs))
        if 'venv' in args:pr.mkdir(target)
        if 'native' in args:
            proof={'actual':{'python':'synthetic','cuda':'12.8','packages':chosen['packages']},'imports':{},'trainers':{},'reader':'synthetic','console_help':{}}
            return NS(stdout=json.dumps(proof).encode(),stderr=b'')
        return NS(returncode=0,stdout=b'',stderr=b'')
    monkeypatch.setattr(worker.subprocess,'run',run)
    worker.build(chosen,digest(worker.encoded(chosen)),digest(Path(worker.__file__).read_bytes()))
    installs=[args for args,kw in seen if 'install' in args]
    assert len(installs)==2 and all('--require-hashes' in args and '--no-deps' in args for args in installs)
    assert '--only-binary=:all:' in installs[0]
    assert '--no-build-isolation' in installs[1] and '--no-binary=acvl-utils' in installs[1]
    assert (target/'build-tools.lock').read_text().count('==')==3
    assert all(not any('TOKEN' in k for k in kw['env']) for _,kw in seen)
