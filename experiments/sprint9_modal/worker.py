"""One reviewed U_base smoke; existing scientific definitions are unchanged.

This entry point is never used for a full run. It loads exactly the private,
review-bound development manifest, verifies inputs before reading cache arrays,
then performs the saved inner/final training and postprocessing once.
"""
import hashlib
import json
import math
from pathlib import Path
import time

CNN={'patch':[48,48,32],'stride':[24,24,16],'width':16,'batch':8,'patches_per_epoch':400,
     'max_epochs':2,'patience':4,'val_every':1,'lr':0.001,'weight_decay':0.0001,
     'lesion_centred_fraction':0.5,'clip_sigma':6.0}
FEATURE_CFG={'target_mm':2.0,'vessel_pct':98.0,'core_thr':0.3,'penumbra_tmax':6.0,'schema':'isles24-features-2mm-v2'}
CONTRACT={'scope':'DEVELOPMENT_99_ONLY','count':99,
          'cohort_sha256':'8af6645a310fc5bb20f4fc836b954ab0ed45087167f724dcaf786e3cd1956d8e',
          'cache_map_sha256':'43c34981463c7eacc96e2af86b8867d74dfb59ee16dea3fdbae4f70d2d45877f',
          'split_sha256':'c223b1c82004f9cdd01bd6a6e3a0784c77e0ea7ed772b27f7b6d411da5bc30bf'}
VERSIONS={'torch':'2.11.0+cu128','numpy':'2.1.3','pandas':'2.2.3','scipy':'1.16.3','sklearn':'1.6.1'}


def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True).encode()


def validate_config(config,contract):
    if contract!=CONTRACT:raise ValueError('SMOKE_KNOWN_COHORT_PIN')
    required={'cases','cache_file_hashes','partitions','cnn','feature_cfg','versions','source_notebook_sha256'}
    if set(config)!=required:raise ValueError('SMOKE_CONFIG_FIELDS')
    cases=config['cases'];hashes=config['cache_file_hashes'];part=config['partitions']
    if (len(cases)!=99 or len(set(cases))!=99 or cases!=sorted(cases) or set(hashes)!=set(cases) or
        config['cnn']!=CNN or config['feature_cfg']!=FEATURE_CFG or config['versions']!=VERSIONS or
        config['source_notebook_sha256']!='a519f3e0ed92850a9a39edf364b4415573f7a751cf06b89f2ff7de0dc6eb5c06'):
        raise ValueError('SMOKE_COHORT_OR_PROTOCOL')
    if sha(canonical(cases))!=contract['cohort_sha256'] or sha(canonical(hashes))!=contract['cache_map_sha256'] or sha(canonical(part))!=contract['split_sha256']:
        raise ValueError('SMOKE_INPUT_CONTRACT')
    if set(part)!={'train','held','inner_val','inner_train','vol_folds'}:raise ValueError('SMOKE_PARTITION_FIELDS')
    train,held,inner,valid=(part[x] for x in ('train','held','inner_train','inner_val'))
    for items in [train,held,inner,valid,*part['vol_folds']]:
        if len(set(items))!=len(items) or not set(items)<=set(cases):raise ValueError('SMOKE_PARTITION_MEMBERS')
    if (len(held)!=20 or set(train)&set(held) or set(train)|set(held)!=set(cases) or
        set(inner)&set(valid) or set(inner)|set(valid)!=set(train) or len(valid)!=16 or
        len(part['vol_folds'])!=3 or sum(map(len,part['vol_folds']))!=len(train) or
        set().union(*map(set,part['vol_folds']))!=set(train)):
        raise ValueError('SMOKE_PARTITION_LEAKAGE')
    return config


def main():
    # Standard-library identity checks happen before importing scientific code.
    package=Path('/reviewed');manifest=json.loads((package/'manifest.json').read_text());binding=manifest['binding']
    if binding['input_contract']!=CONTRACT:raise ValueError('SMOKE_KNOWN_COHORT_PIN')
    config=validate_config(json.loads((package/'smoke.json').read_text()),binding['input_contract'])
    data=Path('/data')
    expected={case+'.npz':v for case,v in config['cache_file_hashes'].items()}
    if {p.name for p in data.iterdir()}!=set(expected):raise ValueError('SMOKE_DATA_MEMBER_SET')
    for name,identity in expected.items():
        path=data/name
        if path.is_symlink() or not path.is_file() or sha(path.read_bytes())!=identity:raise ValueError('SMOKE_CACHE_HASH')
    import science as s
    import scipy, sklearn
    actual={'torch':s.torch.__version__,'numpy':s.np.__version__,'pandas':s.pd.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__}
    if actual!=VERSIONS or not s.torch.cuda.is_available():raise ValueError('SMOKE_ENVIRONMENT_PIN')
    # Recompute the original shuffled partitions and require literal list order,
    # not just set membership; training sampling depends on that order.
    order=list(config['cases']);s.np.random.default_rng(101).shuffle(order);held=order[0::5]
    train=[c for c in config['cases'] if c not in held];inner=list(train);s.np.random.default_rng([101,0,9]).shuffle(inner)
    vo=list(train);s.np.random.default_rng([101,0,77]).shuffle(vo)
    generated={'train':train,'held':held,'inner_val':inner[:16],'inner_train':inner[16:],'vol_folds':[vo[j::3] for j in range(3)]}
    if generated!=config['partitions']:raise ValueError('SMOKE_PARTITION_REPRODUCTION')
    out=Path('/tmp/outputs');out.mkdir(mode=0o700)
    for name in ('ckpt','uscores','masks','folds'):(out/name).mkdir(mode=0o700)
    s.RUN_DIR=str(out);s.FINGERPRINT=binding['run_id'];s.N_FOLDS=5;s.MAP_SHUFFLE=101;s.MAP_SEED=1
    s.CNN=dict(CNN);s.PATCH=tuple(CNN['patch']);s.STRIDE=tuple(CNN['stride']);s.FILM_HIDDEN=32
    s.SMOOTH_GRID_MM=[0.0,1.0,2.0,3.0,4.0];s.ACTIVE_ARMS={'U_base':{'group':None,'fusion':None,'seeds':[1]}};s.GROUP_FIELDS={}
    s.TORCH_DEVICE=s.torch.device('cuda');s.IDX20=[i for i,f in enumerate(s.FEATURE_NAMES) if f!='slice_pos']
    s.INNER={(101,0):config['partitions']}
    start=time.time()
    def log(message):print('[+%.1f min] %s'%((time.time()-start)/60,message),flush=True)
    s.log=log
    feature_hash=sha(canonical(FEATURE_CFG))[:12]
    s.CACHE={case:s.load_cache(str(data/(case+'.npz')),feature_hash,case) for case in config['cases']}
    s.VOXEL_MM=(2.0,2.0,2.0)
    for cache in s.CACHE.values():
        if not s.np.allclose(s.np.abs(s.np.diag(cache['affine'])[:3]),s.VOXEL_MM,atol=1e-3) or abs(cache['voxel_ml']-.008)>1e-6:
            raise ValueError('SMOKE_CACHE_GEOMETRY')
    s.train_predict('U_base',101,0,1)
    if s.postprocess('U_base',101,0,1)!='complete':raise ValueError('SMOKE_POSTPROCESS_INCOMPLETE')
    table=out/'folds/unet_U_base_s101_f0_t1.csv'
    if not s.fold_valid(str(table),['U_base_raw','U_base_smoothed'],held,101,0,1):raise ValueError('SMOKE_METRIC_VALIDATION')
    df=s.pd.read_csv(table);means={name:float(group.dice.mean()) for name,group in df.groupby('recipe')}
    if not all(math.isfinite(v) for v in means.values()):raise ValueError('SMOKE_NONFINITE_SUMMARY')
    receipt={'run_id':binding['run_id'],'versions':actual,'device':s.torch.cuda.get_device_name(0),
             'input_contract':binding['input_contract'],'arm':'U_base','shuffle':101,'fold':0,'training_seed':1,
             'maximum_epochs':2,'held_count':len(held),'mean_dice':means,'elapsed_seconds':time.time()-start}
    (out/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'summary.json').write_text(json.dumps({'scope':'development smoke reproduction','mean_dice':means,'patients':len(held)},indent=2)+'\n')


if __name__=='__main__':main()
