def native_synthetic_integration(progress_factory):
 'Controller CPU rehearsal.'
 import types
 import torch
 from orchestrator.modal_fit_progress import FitProgress
 from orchestrator.modal_nnunet import run_fit
 from orchestrator.modal_preprocessed_contract import validate_preprocessed,validate_validation
 from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
 m=types.ModuleType('synthetic_item4');m.__file__=__file__
 exec(compile(Path(__file__).read_bytes(),__file__,'exec'),m.__dict__)
 m._load_science();n=m.np
 old=dict(os.environ)
 with tempfile.TemporaryDirectory(prefix='item4-native-synthetic-') as td:
  root=Path(td);inp=root/'inputs';prep=root/'prepared';inp.mkdir();prep.mkdir()
  try:
   os.environ.update(nnUNet_compile='false',nnUNet_n_proc_DA='0')
   torch.set_num_threads(1)
   cases=[f'synthetic-{i:03d}' for i in range(99)]
   partitions={f'101_{k}':{'held':cases[k::5],'train':[c for c in cases if c not in cases[k::5]]} for k in range(5)}
   splits=m.split_document(partitions);pb=m.canonical(partitions);part=root/'partitions.json';part.write_bytes(pb)
   cohort=m.canonical({'cases':cases});m.PARTITIONS_SHA256=m.sha_bytes(pb);m.COHORT_SHA256=m.sha_bytes(cohort);m.SPLIT_SHA256=m.sha_bytes(m.canonical(splits))
   plans,dataset=m._synthetic_plans();plans['plans_name']='SyntheticPlans'
   plans['configurations']['3d_fullres']['spacing']=[5.,5.,5.]
   handoff={'arm':'A1_ct_maps_cta','smoke':False,'cases':cases,'splits':splits,'plans':plans,'windows':{k:list(m.WINDOWS[k]) for k in m.BASE6},'source_inventory':{'brain':'cad80ea68c35','cbf':'71905e6a3737','cbv':'678b1bfd5639','cta':'f3f200c85d00','lesion':'fbcfad347f52','mtt':'732e673174db','ncct':'b5137a3f1df6','tmax':'71fb01614363'}}
   m.write_once(inp,'baseline/plans.json',m.canonical(plans));m.write_once(inp,'baseline/handoff.json',m.canonical(handoff))
   m.BASE_PLANS_SHA256=m.file_info(inp/'baseline/plans.json')['sha256'];m.BASE_HANDOFF_SHA256=m.file_info(inp/'baseline/handoff.json')['sha256']
   rng=n.random.default_rng(1301);aff=n.diag([5.,5.,5.,1.]);shape=(16,16,16)
   for case in cases:
    truth=n.zeros(shape,n.uint8);truth[5:10,5:10,5:10]=1
    arrays={k:rng.uniform(m.WINDOWS[k][0]+.1,m.WINDOWS[k][1]-.1,shape).astype('float32') for k in m.BASE6}
    arrays.update(brain=n.ones(shape,n.uint8),lesion=truth)
    for k,rel in m.source_paths(case).items():
     q=inp/rel;q.parent.mkdir(parents=True,exist_ok=True);m.nib.save(m.nib.Nifti1Image(arrays[k],aff),q)
    target=m.resample_to_output(m.nib.Nifti1Image(truth,aff),voxel_sizes=(2.,2.,2.),order=0)
    y=target.get_fdata()>.5;mask=n.ones(y.shape,bool);count=int(mask.sum())
    feat={'X':n.zeros((count,len(m.FEATURE_NAMES)),n.float32),'y':y[mask].astype('uint8'),'sdt':n.zeros(count,n.float32),'mask':mask,'lesion_full':y,'healthy_side':n.zeros(count,bool),'shape':y.shape,'affine':target.affine,'voxel_ml':.008,'summary':{}}
    q=inp/'feature-cache-2mm-v2'/f'{case}.npz';q.parent.mkdir(exist_ok=True);m.save_cache(str(q),feat,case,m.config_hash(m.FEATURE_CFG))
   inv={q.relative_to(inp).as_posix():m.file_info(q) for q in inp.rglob('*') if q.is_file()}
   from importlib.metadata import version
   import sys
   req={'schema':'scientific-environment-requirements/v1','python':f'{sys.version_info.major}.{sys.version_info.minor}','cuda':'12.8','packages':{k:version(k) for k in ('torch','nnunetv2','numpy','nibabel','pandas','scipy','scikit-learn','simpleitk')}}
   require(req['packages']['nnunetv2']=='2.8.1' and torch.version.cuda=='12.8','pinned native build required')
   sel={'schema':'declared-preprocessing-partitions/v1','id':'synthetic-prep','input_contract_sha256':m.sha_bytes(json.dumps(inv,sort_keys=True,allow_nan=False).encode()),'environment_requirements_sha256':m.sha_bytes(m.canonical(req)),'split_sha256':m.SPLIT_SHA256,'plans_name':'SyntheticPlans','cohort_sha256':m.COHORT_SHA256,'source_capture_sha256':m.sha_bytes(b'synthetic sources only'),'partitions_sha256':m.PARTITIONS_SHA256}
   plan={'schema':'scientific-execution-plan/v2','run_id':m.RUN_ID,'operator_scope_sha256':'101f869a822c4c713e71f7c9ce91514094978c11f2bf012234b9cab2c9971309','dispatch_mode':'incremental','fits':[{'fit_id':'synthetic-fit','arm':'A1_repeat','preprocessing_id':sel['id']}],'preprocessing':[sel],'environment_requirements':req}
   env=m.sha_bytes(m.canonical(req));native={k:v for k,v in sel.items() if k!='environment_requirements_sha256'};native.update(schema='reviewed-preprocessing-partitions/v1',environment_sha256=env)
   pin=m.sha_bytes(Path(__file__).read_bytes());rt={'run_id':m.RUN_ID,'spec_sha256':m.sha_bytes(b'synthetic rehearsal, no approval'),'execution_plan_sha256':m.sha_bytes(m.canonical(plan)),'execution':{'module_sha256':pin},'preprocessing':native}
   durable={}
   def checkpoint(step,files):
    require(step not in durable,'duplicate synthetic commit')
    for rel,info in files.items():require(m.file_info(prep/rel)==info,'synthetic commit bytes')
    q=root/'steps';q.mkdir(exist_ok=True);m.write_once(q,step+'.json',m.canonical(files));durable[step]=copy.deepcopy(files)
   contract={'execution_plan':plan,'runtime':rt,'preprocessing':native,'frozen_partitions':{'path':str(part),'sha256':m.PARTITIONS_SHA256},'completed_steps':{},'checkpoint':checkpoint}
   returned=m.preprocess(inp,prep,contract)
   stamps={rel:(info,(prep/rel).stat().st_mtime_ns) for files in durable.values() for rel,info in files.items()}
   linked=dict(contract,completed_steps={q.stem:json.loads(q.read_bytes()) for q in (root/'steps').glob('*.json')})
   require(m.preprocess(inp,prep,linked)==returned,'preprocessing linked reuse changed receipt')
   require(stamps=={rel:(m.file_info(prep/rel),(prep/rel).stat().st_mtime_ns) for rel in stamps},'committed preprocessing rewritten')
   assets={'preprocessing_code_sha256':pin,'plans_name':sel['plans_name'],'split_sha256':sel['split_sha256']}
   files=validate_preprocessed(returned['proposed'],cohort,assets,{k:native[k] for k in ('input_contract_sha256','environment_sha256')},cohort_sha256=m.COHORT_SHA256,source_sha256=sel['source_capture_sha256'])
   expected={k:returned['validation'][k] for k in ('run_id','spec_sha256','preprocessing_code_sha256','validator_sha256','cohort_sha256','input_contract_sha256','environment_sha256')}
   validate_validation(returned['validation'],expected,files)
   require(len(files)==300 and all(m.file_info(prep/k)==v for k,v in files.items()),'native file closure')
   bad=copy.deepcopy(returned['proposed']);bad['case_files'].pop(cases[0])
   try:validate_preprocessed(bad,cohort,assets,{k:native[k] for k in ('input_contract_sha256','environment_sha256')},cohort_sha256=m.COHORT_SHA256,source_sha256=sel['source_capture_sha256'])
   except ValueError:pass
   else:raise AssertionError('missing native member accepted')
   observed=returned['proposed']['plans_sha256']
   progress=progress_factory(root/'durable','synthetic-fit',observed,env)
   require(type(progress) is FitProgress,'genuine FitProgress required; mocks refused')
   class Interrupted(RuntimeError):pass
   class RehearsalTrainer(nnUNetTrainer):
    def on_epoch_end(self):
     super().on_epoch_end()
     if self.current_epoch==1 and self.stop_after_one:raise Interrupted('intentional synthetic interruption after epoch checkpoint')
   def trainer(segment):
    m._native_paths(root/'raw',prep/'preprocessed',progress.root/'work')
    os.environ['nnUNet_n_proc_DA']='0'
    _,pre=m._prepared_paths(prep,'A1_repeat')
    t=RehearsalTrainer(dict(json.loads((pre/'SyntheticPlans.json').read_bytes()),continue_training=segment>1),'3d_fullres',0,json.loads((pre/'dataset.json').read_bytes()),device=torch.device('cpu'))
    t.num_epochs=2;t.num_iterations_per_epoch=2;t.num_val_iterations_per_epoch=2;t.stop_after_one=segment==1
    t.log_file=str(progress.root/'work'/f'training_log_{segment}.txt')
    Path(t.log_file).touch(mode=0o600,exist_ok=False)
    m._fit_truth(pre,t,splits[0]['val'],progress.root/'work')
    return t
   with progress.writer(initial=True):
    (progress.root/'work').mkdir(exist_ok=True);a=trainer(1)
    try:run_fit(a,progress,initial=True,save_every=1,segment=1,interruption=None)
    except Interrupted:pass
    else:raise AssertionError('interruption not exercised')
    cp,record=progress.select('latest');require(record['metadata']['next_epoch']==1,'wrong interrupted epoch')
    interrupted_hash=m.file_info(cp)
   progress=progress_factory(root/'durable','synthetic-fit',observed,env)
   with progress.writer(initial=False):
    b=trainer(2);receipt=run_fit(b,progress,initial=False,save_every=1,segment=2,interruption={'synthetic':True,'checkpoint_sha256':interrupted_hash['sha256']})
    require(receipt['epoch_resumed_from']==1 and b.current_epoch==2 and b.optimizer.state_dict()['state'],'native optimizer/epoch resume')
    final,record=progress.select('final');require(record['sha256']==receipt['final_sha256']==m.file_info(final)['sha256'],'native final checkpoint')
    scores=m._score_native(prep,b,'A1_repeat',0,splits,progress.root/'work')
    require(scores['n_heldout']==20 and all(math.isfinite(float(v)) for v in [b.logger.get_value('train_losses',step=i) for i in range(b.num_epochs)]),'native scoring/loss')
   return {'schema':'item4-native-synthetic-integration/v1','scope':'CPU generated fixtures; reduced three-stage network and two epochs of two batches; no benchmark or efficacy','module_sha256':pin,'preprocessed_files':len(files),'preprocessing_reuse_verified':True,'resume':receipt,'aggregate_scores':scores,'gpu_verified':False,'production_main_verified':False,'scientific_approval':False}
  finally:
   os.environ.clear();os.environ.update(old)
