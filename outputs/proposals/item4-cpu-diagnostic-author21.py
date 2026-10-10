K_DJ='dataset.json'
K_AR='A1_repeat'
K_AZ='A1_zscore'
K_F='fallback'
K_AH='A1_histeq'
K_3F='3d_fullres'
K_S='stability'
K_MM='memory_mib'
K_P='preprocessing'
K_E='experiment'
K_ACMC='A1_ct_maps_cta'
K_SFJ='splits_final.json'
K_CDJ='cpu-diagnostic.json'
K_MJ='metrics.json'
K_NE='next_epoch'
K_AM='A1_multiwin'
K_R='resources'
K_SF='synthetic-fit'
K_AP='A1_pnormct'
K_EP='execution_plan'
K_V='validation'
K_LF='lesion_full'
K_LH='lr_horizon'
K_MS='module_sha256'
K_BH='baseline_handoff'
K_BPJ='baseline/plans.json'
K_BHJ='baseline/handoff.json'
K_NS='normalization_schemes'
K_C='configurations'
K_N='NoNormalization'
K_ST='synthetic.txt'
K_NWS='native_write_seconds'
K_DPPV='declared-preprocessing-partitions/v1'
K_EPS='execution_plan_sha256'
K_PCS='preprocessing_code_sha256'
K_DFJ='dataset_fingerprint.json'
K_LNB='loader_not_bottleneck'
K_VW='validation_workers'
K_WSD='window_stability_demonstrated'
K_SSSPE='steady_state_seconds_per_epoch'
K_DOS='durable_overhead_seconds'
# Shared contract keys; values are unchanged. Error codes are listed in SPEC.
K_PN='plans_name'
K_ICS='input_contract_sha256'
K_SS='split_sha256'
K_PI='preprocessing_id'
K_ES='environment_sha256'
K_SCS='source_capture_sha256'
K_LW='loader_wait'
K_NNPD='nnUNet_n_proc_DA'
K_PS='plans_sha256'
K_TS='timeout_seconds'
K_CS='cohort_sha256'
K_ERS='environment_requirements_sha256'
K_TI='training_iterations'
K_VI='validation_iterations'
K_ER='environment_requirements'
K_VC='validation_checks'
K_MWS='module_wall_seconds'
K_MSS='module_stop_seconds'
K_FIPPC='foreground_intensity_properties_per_channel'
from pathlib import Path
import hashlib,json,math,os,time,unittest,tempfile,copy,importlib
BASE_PLANS_SHA256='532aa8160bf0db6c83ceeb0c1456d3bf6f2f7b528cdb0a9586866ac724de92d0'
BASE_HANDOFF_SHA256='5a5649e12a568ce99c8c2b4abd88732d07a862d44c32da9f1ddfc599699ddb01'
RUN_ID='experiment-a74959ac4546a982af4ae137'
PARTITIONS_SHA256='2c197a9addf40af4d75dd220a095b62130b0ca58ffbe5dce8eb73dff570f64f8'
COHORT_SHA256='45c5746f60e2275383a2c4f4096295fe7a171da85a73737c5a35a8cc6fc9fe86'
SPLIT_SHA256='d339296ca3b1672fc744e14188b36c1860b379a38b807eca67d8b73038007c86'
ARMS_ORDER= (K_AR,'A1_repeat2',K_AZ,K_AH,K_AM,'A1_L',K_AP,'A1_pnorm_v2')
CANDIDATES= (K_AZ,K_AH,K_AM,'A1_L',K_AP)
WINDOWS= {'ncct':(0,80),'cbf':(0,35),'cbv':(0,10),'mtt':(0,20),'tmax':(0,7),'cta':(0,90),
  'ncct_w2':(20,50),'cbf_w2':(0,100),'cbv_w2':(0,4),'mtt_w2':(0,12),'tmax_w2':(0,20),'cta_w2':(0,300)}
BASE6=('ncct','cbf','cbv','mtt','tmax','cta')
PERF_KINDS=('cbf','cbv','mtt','tmax')
ZSCORE_MIN_SD=0.01
HISTEQ_BINS=256
VOXEL_MM=(2.,2.,2.)
PNORM_NN={'min_ref_voxels':20000,'min_scale':{'cbf':.7,'cbv':.2,'mtt':.4,'tmax':.14,'ncct':1.6},'clip_z':5.}
FEATURE_CFG={'target_mm':2.0,'vessel_pct':98.0,'core_thr':.30,'penumbra_tmax':6.0,'schema':'isles24-features-2mm-v2'}
class PrerequisiteError(RuntimeError):pass
def canonical(obj):
 return(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('utf-8')
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def file_info(path):
 p=Path(path);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return{'sha256':h.hexdigest(),'bytes':n}
def need(test,message):
 if not test:raise PrerequisiteError(message)
def digest(value):
 return isinstance(value,str)and len(value)==64 and all(c in '0123456789abcdef' for c in value)
def rooted(root,relative):
 root=Path(root).resolve();r=Path(relative)
 need(not r.is_absolute()and r.parts and '..' not in r.parts,'E001')
 p=root/r
 need(p.resolve().is_relative_to(root),'E002')
 need(not any(x.is_symlink()for x in[p,*p.parents]if x!=root.parent),'E003')
 return p
def read_verified(root,descriptor):
 need(set(descriptor)=={'path','sha256','bytes'},'E004')
 need(digest(descriptor['sha256'])and type(descriptor['bytes'])is int and descriptor['bytes']>0,'E005')
 p=rooted(root,descriptor['path']);need(file_info(p)=={k:descriptor[k]for k in('sha256','bytes')},'E006')
 return p
def write_once(root,rel,data):
 p=rooted(root,rel);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(data)
 return file_info(p)
def split_document(partitions,expected_count=99):
 need(isinstance(partitions,dict),'E007')
 keys=[k for k in partitions if k.startswith('101_')]
 need(set(keys)=={f'101_{k}' for k in range(5)},'E008')
 out=[];held=[]
 for k in range(5):
  row=partitions[f'101_{k}'];tr=row['train'];va=row['held']
  need(isinstance(tr,list)and isinstance(va,list)and tr and va,'E026')
  need(all(isinstance(x,str)and x and '/' not in x and '\\' not in x and x not in('.','..')for x in tr+va),'E027')
  need(len(tr)==len(set(tr))and len(va)==len(set(va))and not set(tr)&set(va),'E028')
  out.append({'train':sorted(tr),'val':sorted(va)});held+=va
 need(len(held)==len(set(held))==expected_count,'E009')
 for row in out:need(set(row['train'])==set(held)-set(row['val']),'E029')
 return out
def bound_plan(contract,preprocessing=False):
 plan=contract[K_EP];rt=contract['runtime']
 need(plan.get('operator_scope_sha256')=='101f869a822c4c713e71f7c9ce91514094978c11f2bf012234b9cab2c9971309','E010')
 need(plan['schema']=='scientific-execution-plan/v2' and plan['run_id']==RUN_ID and plan['dispatch_mode']=='incremental','E011')
 need(sha_bytes(canonical(plan))==rt[K_EPS],'E012')
 need(rt['run_id']==RUN_ID and digest(rt['spec_sha256'])and rt.get('execution',{}).get(K_MS)==sha_bytes(Path(__file__).read_bytes()),'E013')
 if preprocessing:
  supplied=contract.get(K_P)
  need(isinstance(supplied,dict)and isinstance(supplied.get('id'),str),'E030')
  eid=supplied['id']
 else:
  selected=[x for x in plan['fits']if x['fit_id']==rt[K_E]['fit_id']]
  need(len(selected)==1,'E031')
  eid=selected[0][K_PI]
 rows=[x for x in plan[K_P]if x.get('id')==eid]
 need(len(rows)==1,'E014');sel=rows[0]
 fields={'schema','id',K_ICS,K_ERS,K_SS,K_PN,K_CS,K_SCS,'partitions_sha256'}
 need(set(sel)==fields and sel['schema']==K_DPPV,'E015')
 missing=[k for k in(K_ICS,K_SCS,K_CS,K_SS,K_ERS)if not digest(sel.get(k))]
 need(not missing,'unavailable original prerequisite bindings: '+', '.join(missing))
 need(sel['partitions_sha256']==PARTITIONS_SHA256 and sel[K_CS]==COHORT_SHA256 and sel[K_SS]==SPLIT_SHA256,'E016')
 need(sel[K_ERS]==sha_bytes(canonical(plan[K_ER])),'E017')
 if preprocessing:
  shared=fields-{'schema',K_ERS}
  need(all(supplied.get(k)==sel[k]for k in shared),'E032')
  if supplied.get('schema')==K_DPPV:
   need(supplied==sel,'E035')
  else:
   need(supplied.get('schema')=='reviewed-preprocessing-partitions/v1','E036')
   need(set(supplied)==shared|{'schema',K_ES},'E037')
   need(digest(supplied.get(K_ES))and supplied[K_ES]==rt.get(K_P,{K_ES:rt.get(K_ES)}).get(K_ES),'E038')
 return plan,rt,sel
def environment_check(requirements):
 import sys
 from importlib.metadata import version
 need(f'{sys.version_info.major}.{sys.version_info.minor}'==requirements['python'],'E018')
 for package,wanted in requirements['packages'].items():need(version(package)==wanted,'package requirement mismatch: '+package)
 import torch
 need(torch.version.cuda==requirements['cuda'],'E019')
def _load_science():
 global np,pd,nib,resample_from_to,resample_to_output,gaussian_filter,uniform_filter,distance_transform_edt,cc_label,binary_fill_holes,binary_erosion,roc_auc_score,average_precision_score
 import numpy as np
 import pandas as pd
 import nibabel as nib
 from nibabel.processing import resample_from_to,resample_to_output
 from scipy.ndimage import gaussian_filter,uniform_filter,distance_transform_edt,label as cc_label,binary_fill_holes,binary_erosion
 from sklearn.metrics import roc_auc_score,average_precision_score
def verify_completed(output_root,completed):
 known={}
 for step,files in completed.items():
  need(isinstance(step,str)and isinstance(files,dict)and files,'E033')
  for rel,info in files.items():
   need(isinstance(info,dict)and set(info)=={'sha256','bytes'}and digest(info['sha256'])and type(info['bytes'])is int and info['bytes']>0,'E039')
   need(rel not in known,'E040')
   need(file_info(rooted(output_root,rel))==info,'E041')
   known[rel]=info
 return known
def commit_step(root,contract,step,files):
 need(step not in contract.get('completed_steps',{}),'E020')
 old=verify_completed(root,contract.get('completed_steps',{}))
 need(files and not set(files)&set(old),'E021')
 records={r:file_info(rooted(root,r))for r in sorted(files)}
 contract['checkpoint'](step,records)
 contract.setdefault('completed_steps',{})[step]=records
 return records
def load_frozen_partitions(contract):
 f=contract['frozen_partitions'];need(f['sha256']==PARTITIONS_SHA256,'E022')
 b=Path(f['path']).read_bytes();need(sha_bytes(b)==PARTITIONS_SHA256,'E023')
 splits=split_document(json.loads(b));need(sha_bytes(canonical(splits))==SPLIT_SHA256,'E024')
 return splits
def derived_ctp_support(ctp,brain):
 raise PrerequisiteError('U3 coverage held: registered CTP padding/support not authenticated for the cohort')
def pnorm_reference(maps,brain):
 all_zero=np.logical_and.reduce([np.where(np.isfinite(maps[k]),maps[k],0)==0 for k in PERF_KINDS])
 t=maps['tmax']
 return[('brain with Tmax <= 6 s',brain&np.isfinite(t) & (t>=0) & (t<=6) & ~all_zero),('whole brain',brain& ~all_zero)],all_zero
def normalize_channel(v,kind,levels,brain,invalid):
 out,rec=_pnorm_channel(v,kind,levels,brain)
 invalid=invalid| ~np.isfinite(v) | ((v<=0)if kind in('cbf','cbv','mtt')else(v<0))
 return np.where(brain& ~invalid,out,0).astype(np.float32),rec
def transform_case(arrays,arm):
 need(arm in ARMS_ORDER,'unknown arm');brain=arrays['brain']>.5
 maps={k:arrays[k]for k in BASE6};outputs={};qc={}
 need(brain.any()and all(v.shape==brain.shape for v in maps.values()),'E025')
 coverage=None
 if arm in(K_AZ,K_AH):coverage=derived_ctp_support(arrays['ctp'],brain)
 pref=pnorm_reference(maps,brain)if arm in(K_AP,'A1_pnorm_v2')else None
 channels=BASE6+tuple(k+'_w2' for k in BASE6)if arm==K_AM else BASE6
 for ch in channels:
  k=ch.removesuffix('_w2');v=maps[k];support,record=coverage_support(v,brain,coverage if k in PERF_KINDS else None)
  x=window01(v,*WINDOWS[ch]);raw=v[brain&np.isfinite(v)]
  record.update(clip_low=float(np.mean(raw<=WINDOWS[ch][0]))if raw.size else None,clip_high=float(np.mean(raw>=WINDOWS[ch][1]))if raw.size else None)
  if arm in(K_AZ,K_AH):
   x,r=(zscore_in_brain(x,support)if arm==K_AZ else histeq_in_brain(x,support));record.update(r)
   need(r.get(K_F)not in('empty support','constant support'),'E042')
  elif pref is not None and(k in PERF_KINDS or(arm==K_AP and k=='ncct')):
   levels=pref[0]if k in PERF_KINDS else[('whole finite nonnegative brain',brain)]
   x,r=normalize_channel(v,k,levels,brain,pref[1]if k in PERF_KINDS else np.zeros(brain.shape,bool));record.update(r)
  x=(x*brain).astype(np.float32)
  need(np.isfinite(x).all()and float(x[brain].std())>=1e-6,'E034')
  outputs[ch]=x;record['prepared_sd']=float(x[brain].std());qc[ch]=record
 return outputs,qc
def validate_full_folds(table,held):
 if set(held) !=set(range(5)):
  raise ValueError("expected frozen folds 0 through 4")
 expected= [(c,k,101)for k in range(5)for c in held[k]]
 if any(len(held[k]) ==0 for k in range(5))or len(expected) !=99:
  raise ValueError("expected 99 members in five nonempty folds")
 members= [r[0]for r in expected]
 if len(set(members)) !=99:
  raise ValueError("duplicate or overlapping frozen members")
 if not{"case","fold","shuffle"}.issubset(table.columns):
  raise ValueError("membership columns missing")
 keys=table[["case","fold","shuffle"]]
 if len(keys) !=99 or keys.isna().any().any()or keys.case.duplicated().any():
  raise ValueError("missing, extra, null or duplicate rows")
 if set(keys.itertuples(index=False,name=None)) !=set(expected):
  raise ValueError("row membership, fold or shuffle mismatch")
def verdict_from_intervals(base_ci,repeat_ci,complete=True):
 normalized= []
 for ci in(base_ci,repeat_ci):
  try:
   if isinstance(ci,(str,bytes))or len(ci)!=3:raise ValueError("invalid interval")
   if any(hasattr(x,"__len__")and not isinstance(x,(str,bytes))for x in ci):raise ValueError("invalid interval")
   arr= [float(x)for x in ci]
  except(ValueError,TypeError)as e:
   raise ValueError("invalid interval")from e
  if not all(math.isfinite(x)for x in arr)or arr[1] >arr[2]:
   raise ValueError("malformed, reversed or nonfinite interval")
  normalized.append(arr)
 base_ci,repeat_ci=normalized
 if not complete:
  return "provisional"
 if base_ci[1] >0 and repeat_ci[1] >0:
  return "better"
 if base_ci[2] <0 and repeat_ci[2] <0:
  return "worse"
 return "no clear difference"
# ===================== Shared utilities v2 (plain numpy/scipy/nibabel; every function has a purpose line) =====================
# Repairs vs v1 (Astra review 2026-09-09): complete lesion truth is cached separately from the feature mask;
# caches are bound to a schema version + configuration hash and validated on load; float32 storage (no float16
# overflow); finite-value checks; unique temporary filenames.
import glob, traceback, uuid

CACHE_SCHEMA = "isles24-features-2mm-v2"

FEATURE_NAMES = [
    "cbf", "cbv", "mtt", "tmax", "ncct_hu",
    "rel_cbf", "rel_tmax", "rel_hu",
    "tissue_class",
    "z_cbf", "z_cbv", "z_tmax", "z_hu",
    "dist_occlusion_mm",
    "affected_side",
    "core_rule", "penumbra_rule",
    "local_mean_tmax", "local_std_tmax", "local_mean_relcbf",
    "slice_pos",
]
Z_COLUMNS = ["z_cbf", "z_cbv", "z_tmax", "z_hu"]

def config_hash(cfg: dict) -> str:
    """Short stable hash of the settings that change what a cache file contains."""
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:12]

def lr_flip_axis(affine):
    """Which voxel axis runs left-right? The one most aligned with world x (this is NOT hemisphere registration)."""
    return int(np.argmax(np.abs(affine[0, :3])))

def dice(a, b):
    a, b = a.astype(bool), b.astype(bool)
    s = a.sum() + b.sum()
    return 1.0 if s == 0 else float(2.0 * (a & b).sum() / s)

def drop_small_components(binary, min_vox):
    lab, n = cc_label(binary)
    if n == 0:
        return binary
    sizes = np.bincount(lab.ravel()); sizes[0] = 0
    return np.isin(lab, np.where(sizes >= min_vox)[0])

def largest_component(binary):
    lab, n = cc_label(binary)
    if n == 0:
        return binary
    sizes = np.bincount(lab.ravel()); sizes[0] = 0
    return lab == int(np.argmax(sizes))

def brain_mask_from_ncct(hu, cbf, cbv):
    """Cheap skull-strip: soft-tissue HU band, finite perfusion, largest blob, holes filled."""
    cand = np.isfinite(hu) & (hu > 0) & (hu < 80) & np.isfinite(cbf) & np.isfinite(cbv) & (cbf > 0)
    return binary_fill_holes(largest_component(cand))

def tissue_class_from_hu(hu, mask, sigma=1.0):
    """0 = CSF (<18 HU), 1 = white matter (18-33), 2 = gray matter (>33), after light smoothing."""
    sm = gaussian_filter(np.where(np.isfinite(hu), hu, 0.0), sigma)
    cls = np.full(hu.shape, -1, dtype=np.int8)
    cls[mask & (sm < 18)] = 0
    cls[mask & (sm >= 18) & (sm < 33)] = 1
    cls[mask & (sm >= 33)] = 2
    return cls

def mirror_relative(vol, flip_axis, mask, eps=1e-2, sigma=1.0):
    """Value / smoothed mirrored value. Approximates the opposite side; assumes rough midline symmetry."""
    mirrored = np.flip(vol, axis=flip_axis)
    denom = gaussian_filter(np.where(np.isfinite(mirrored), mirrored, 0.0), sigma) + eps
    rel = np.where(mask, vol / denom, 0.0)
    return np.clip(np.nan_to_num(rel), 0.0, 3.0).astype(np.float32)

def hemisphere_index(shape, flip_axis):
    idx = np.arange(shape[flip_axis]); half = idx >= shape[flip_axis] // 2
    reshape = [1, 1, 1]; reshape[flip_axis] = -1
    return np.broadcast_to(half.reshape(reshape), shape)

def affected_side_mask(shape, flip_axis, lvo, tmax, brain):
    """Stroke side: LVO-mask centroid when present (an annotation input, disclosed), else Tmax>6 asymmetry."""
    high = hemisphere_index(shape, flip_axis)
    if lvo is not None and lvo.sum() >= 5:
        centroid = np.argwhere(lvo).mean(axis=0)[flip_axis]
        side_high, method = centroid >= shape[flip_axis] / 2, "lvo_centroid"
    else:
        hot = (tmax > 6) & brain
        side_high, method = hot[high].sum() >= hot[~high].sum(), "tmax_asymmetry"
    return (high if side_high else ~high), method

def signed_distance_mm(lesion, voxel_mm, clip=40.0):
    """Positive outside the lesion, negative inside, in mm (Model-2 target), from the COMPLETE lesion."""
    if lesion.sum() == 0:
        return np.full(lesion.shape, clip, dtype=np.float32)
    outside = distance_transform_edt(~lesion, sampling=voxel_mm)
    inside = distance_transform_edt(lesion, sampling=voxel_mm)
    return np.clip(outside - inside, -clip, clip).astype(np.float32)

def find_member(extract_root, case, suffix):
    hits = glob.glob(f"{extract_root}/**/{case}*{suffix}", recursive=True)
    return hits[0] if len(hits) == 1 else None

def load_case_2mm(extract_root, case, target_mm=2.0):
    """Load every volume for one case, resampled onto a shared 2 mm grid built from its CBF map."""
    paths = {m: find_member(extract_root, case, f"_space-ncct_{m}.nii.gz") for m in ("cbf", "cbv", "mtt", "tmax")}
    paths["ncct"] = find_member(extract_root, case, "_ncct.nii.gz")
    paths["lesion"] = find_member(extract_root, case, "_space-ncct_lesion-msk.nii.gz")
    paths["lvo"] = find_member(extract_root, case, "_space-ncct_lvo-msk.nii.gz")
    paths["cow"] = find_member(extract_root, case, "_space-ncct_cow-msk.nii.gz")
    missing = [k for k in ("cbf", "cbv", "mtt", "tmax", "ncct", "lesion") if paths[k] is None]
    if missing:
        raise FileNotFoundError(f"{case}: missing {missing}")
    ref = resample_to_output(nib.load(paths["cbf"]), voxel_sizes=(target_mm,) * 3, order=1)
    out = {"affine": ref.affine, "shape": ref.shape, "voxel_mm": (target_mm,) * 3,
           "voxel_ml": target_mm ** 3 / 1000.0, "flip_axis": lr_flip_axis(ref.affine),
           "cbf": ref.get_fdata(dtype=np.float32)}
    for m in ("cbv", "mtt", "tmax", "ncct"):
        out[m] = resample_from_to(nib.load(paths[m]), ref, order=1).get_fdata(dtype=np.float32)
    out["lesion"] = resample_from_to(nib.load(paths["lesion"]), ref, order=0).get_fdata(dtype=np.float32) > 0.5
    out["lvo"] = (resample_from_to(nib.load(paths["lvo"]), ref, order=0).get_fdata(dtype=np.float32) > 0.5
                  if paths["lvo"] else None)
    out["cow"] = (resample_from_to(nib.load(paths["cow"]), ref, order=0).get_fdata(dtype=np.float32).round().astype(np.int16)
                  if paths["cow"] else None)
    return out

def compute_case_features(d, vessel_pct=98.0, core_thr=0.30, penumbra_tmax=6.0):
    """One loaded case -> per-voxel feature table (inside the tissue mask) + COMPLETE lesion truth + summary.
    z_* columns are left at zero here; they are filled per training fold later (never from held-out patients)."""
    cbf, cbv, mtt, tmax, hu = d["cbf"], d["cbv"], d["mtt"], d["tmax"], d["ncct"]
    brain = brain_mask_from_ncct(hu, cbf, cbv)
    pos_cbv = cbv[brain & np.isfinite(cbv) & (cbv > 0)]
    vessel_p98 = float(np.percentile(pos_cbv, vessel_pct)) if pos_cbv.size else np.inf
    tissue = brain & ~(np.isfinite(cbv) & (cbv > vessel_p98))
    fa = d["flip_axis"]
    rel_cbf, rel_tmax, rel_hu = (mirror_relative(v, fa, tissue) for v in (cbf, tmax, hu))
    cls = tissue_class_from_hu(hu, tissue)
    side, side_method = affected_side_mask(d["shape"], fa, d["lvo"], tmax, tissue)
    lvo_present = bool(d["lvo"] is not None and d["lvo"].sum() >= 5)
    dist_occ = (distance_transform_edt(~d["lvo"], sampling=d["voxel_mm"]).astype(np.float32)
                if lvo_present else np.full(d["shape"], 150.0, dtype=np.float32))
    core_rule = (rel_cbf < core_thr) & (rel_cbf > 0) & tissue
    penumbra_rule = (tmax > penumbra_tmax) & tissue & ~core_rule
    tmax_f = np.where(np.isfinite(tmax), tmax, 0.0)
    loc_mean_t = uniform_filter(tmax_f, size=5)
    loc_std_t = np.sqrt(np.maximum(uniform_filter(tmax_f ** 2, size=5) - loc_mean_t ** 2, 0))
    loc_mean_rc = uniform_filter(rel_cbf, size=5)
    z_axis = int(np.argmax(np.abs(d["affine"][2, :3])))
    slice_idx = np.arange(d["shape"][z_axis], dtype=np.float32) / max(d["shape"][z_axis] - 1, 1)
    reshape = [1, 1, 1]; reshape[z_axis] = -1
    slice_pos = np.broadcast_to(slice_idx.reshape(reshape), d["shape"])
    m = tissue
    zeros = np.zeros(m.sum(), dtype=np.float32)
    cols = [cbf[m], cbv[m], mtt[m], tmax[m], hu[m], rel_cbf[m], rel_tmax[m], rel_hu[m], cls[m].astype(np.float32),
            zeros, zeros, zeros, zeros, dist_occ[m], side[m].astype(np.float32),
            core_rule[m].astype(np.float32), penumbra_rule[m].astype(np.float32),
            loc_mean_t[m], loc_std_t[m], loc_mean_rc[m], slice_pos[m]]
    X = np.stack(cols, axis=1).astype(np.float32)
    nonfinite = int((~np.isfinite(X)).sum())
    X = np.nan_to_num(X, copy=False, nan=0.0, posinf=0.0, neginf=0.0)   # counted and reported, not silent
    lesion_full = d["lesion"]
    sdt = signed_distance_mm(lesion_full, d["voxel_mm"])
    covered = float((lesion_full & m).sum() / max(lesion_full.sum(), 1))
    cow_segments = 0
    if d["cow"] is not None:
        _, counts = np.unique(d["cow"][d["cow"] > 0], return_counts=True)
        cow_segments = int((counts >= 5).sum())
    summary = {"lesion_ml": float(lesion_full.sum() * d["voxel_ml"]),
               "lesion_fraction_inside_feature_mask": covered,
               "core_rule_ml": float(core_rule.sum() * d["voxel_ml"]),
               "penumbra_rule_ml": float(penumbra_rule.sum() * d["voxel_ml"]),
               "tissue_mask_ml": float(m.sum() * d["voxel_ml"]), "side_method": side_method,
               "lvo_present": lvo_present, "cow_segments_present": cow_segments,
               "vessel_cbv_p98": vessel_p98, "nonfinite_feature_values_zeroed": nonfinite}
    return {"X": X, "y": lesion_full[m].astype(np.uint8), "sdt": sdt[m], "mask": m, "lesion_full": lesion_full,
            "healthy_side": (~side)[m], "shape": d["shape"], "affine": d["affine"],
            "voxel_ml": d["voxel_ml"], "summary": summary}

def save_cache(path, feat, case, cfg_hash):
    """Atomic, schema- and config-tagged write (unique temp name, then rename)."""
    tmp = f"{path}.{uuid.uuid4().hex}.tmp.npz"
    np.savez_compressed(tmp, X=feat["X"].astype(np.float32), y=feat["y"], sdt=feat["sdt"].astype(np.float32),
                        mask=np.packbits(feat["mask"]), lesion_full=np.packbits(feat["lesion_full"]),
                        mask_shape=np.array(feat["shape"]), healthy_side=feat["healthy_side"], affine=feat["affine"],
                        voxel_ml=np.array(feat["voxel_ml"]), summary=json.dumps(feat["summary"]),
                        meta=json.dumps({"schema": CACHE_SCHEMA, "config_hash": cfg_hash, "case": case,
                                         "features": FEATURE_NAMES}))
    os.replace(tmp, path)

def load_cache(path, expect_hash, expect_case=None):
    """Load and VALIDATE a cache: schema, config hash, case, shapes, finite values. Raises on any mismatch."""
    z = np.load(path, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    if meta.get("schema") != CACHE_SCHEMA or meta.get("config_hash") != expect_hash or meta.get("features") != FEATURE_NAMES:
        raise ValueError(f"cache {os.path.basename(path)} does not match schema/config ({meta.get('schema')}, {meta.get('config_hash')})")
    if expect_case and meta.get("case") != expect_case:
        raise ValueError(f"cache {os.path.basename(path)} belongs to {meta.get('case')}, expected {expect_case}")
    shape = tuple(int(s) for s in z["mask_shape"]); n = int(np.prod(shape))
    mask = np.unpackbits(z["mask"])[:n].reshape(shape).astype(bool)
    lesion_full = np.unpackbits(z["lesion_full"])[:n].reshape(shape).astype(bool)
    X = z["X"].astype(np.float32)
    if X.shape != (int(mask.sum()), len(FEATURE_NAMES)) or not np.isfinite(X).all():
        raise ValueError(f"cache {os.path.basename(path)} has bad shape or non-finite values")
    return {"X": X, "y": z["y"], "sdt": z["sdt"].astype(np.float32), "mask": mask, "lesion_full": lesion_full,
            "shape": shape, "healthy_side": z["healthy_side"], "affine": z["affine"],
            "voxel_ml": float(z["voxel_ml"]), "summary": json.loads(str(z["summary"])), "meta": meta}

def apply_normative(X, norm):
    """Fill z_* columns from per-tissue-class robust stats (median, MAD) supplied by the caller."""
    X = X.copy()
    cls = X[:, FEATURE_NAMES.index("tissue_class")].astype(int)
    for feat, zname in (("cbf", "z_cbf"), ("cbv", "z_cbv"), ("tmax", "z_tmax"), ("ncct_hu", "z_hu")):
        src = X[:, FEATURE_NAMES.index(feat)]; zcol = np.zeros_like(src)
        for c in (0, 1, 2):
            med, mad = norm[feat][str(c)]; sel = cls == c
            zcol[sel] = (src[sel] - med) / (1.4826 * mad + 1e-3)
        X[:, FEATURE_NAMES.index(zname)] = np.clip(zcol, -10, 10)
    return X

def compute_normative(caches, per_case=20000, seed=0):
    """Healthy-hemisphere, non-lesion voxels of the GIVEN caches only (call it with training patients only)."""
    rng = np.random.default_rng(seed)
    pools = {f: {c: [] for c in (0, 1, 2)} for f in ("cbf", "cbv", "tmax", "ncct_hu")}
    for c in caches:
        healthy = c["healthy_side"] & (c["y"] == 0)
        idx = np.where(healthy)[0]
        if idx.size == 0:
            continue
        idx = rng.choice(idx, min(per_case, idx.size), replace=False)
        cls = c["X"][idx, FEATURE_NAMES.index("tissue_class")].astype(int)
        for f in pools:
            vals = c["X"][idx, FEATURE_NAMES.index(f)]
            for k in (0, 1, 2):
                pools[f][k].append(vals[cls == k])
    norm = {}
    for f in pools:
        norm[f] = {}
        for k in (0, 1, 2):
            v = np.concatenate(pools[f][k]) if pools[f][k] else np.array([])
            if v.size < 10:
                norm[f][str(k)] = (0.0, 1.0); continue
            med = float(np.median(v)); mad = float(np.median(np.abs(v - med)))
            norm[f][str(k)] = (med, mad if mad > 0 else float(np.std(v) + 1e-3))
    return norm

def bootstrap_mean_ci(values, reps=2000, seed=0):
    """Patient-level bootstrap 95% CI for a mean (P001 convention)."""
    v = np.asarray(values, dtype=float); rng = np.random.default_rng(seed)
    if v.size == 0:
        return (float("nan"), float("nan"))
    means = [rng.choice(v, v.size, replace=True).mean() for _ in range(reps)]
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))

# ===================== Notebook 3 stages (cache-only experiments) =====================
# Reuses the v2 cache format (core2) and adds: natural-prevalence ("calibrated") training, territory-restricted
# training, feature-subset ablations, the volume-matched hybrid decision rule, average surface distance, a
# size-floored primary metric, and a results ledger. Everything is resumable per experiment.
import os, json, time, glob, uuid, datetime

# ---------- models / device ----------
def xgb_device_probe(log=print):
    X = np.random.default_rng(0).normal(size=(2000, 4)).astype(np.float32); y = (X[:, 0] > 0).astype(int)
    import subprocess
    try: has_gpu = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).returncode == 0
    except FileNotFoundError: has_gpu = False
    if not has_gpu: log("no GPU visible; XGBoost will train on CPU (expect roughly 10x slower fits)")
    for dev in (("cuda", "cpu") if has_gpu else ("cpu",)):
        try:
            t0 = time.time(); m = make_classifier(dev, 0, n_estimators=20); m.fit(X, y); m.predict_proba(X[:10])
            log(f"XGBoost {xgb.__version__} preflight fit OK on {dev} ({time.time()-t0:.1f}s)"); return dev
        except Exception as e:
            log(f"XGBoost on {dev} failed: {e!r}")
    raise RuntimeError("XGBoost cannot train on any device")

def make_classifier(device, seed, n_estimators=400):
    common = dict(n_estimators=n_estimators, max_depth=6, learning_rate=0.08, subsample=0.8, colsample_bytree=0.8,
                  min_child_weight=20, random_state=seed, objective="binary:logistic")
    if int(xgb.__version__.split(".")[0]) >= 2: common.update(tree_method="hist", device=device)
    else: common.update(tree_method="gpu_hist" if device == "cuda" else "hist")
    return xgb.XGBClassifier(**common)

# ---------- sampling regimes ----------
def territory_mask(c):
    """The at-risk territory: clinical core OR penumbra flag."""
    X = c["X"]; return (X[:, FEATURE_NAMES.index("core_rule")] > 0.5) | (X[:, FEATURE_NAMES.index("penumbra_rule")] > 0.5)

def sample_rows(c, rng, regime, per_case):
    """Which voxels of a training case enter the table.
    balanced  : v2 behaviour (all lesion up to cap, penumbra slice, background slice) -> inflated scores
    natural   : uniform random sample of tissue voxels at their natural dead/alive proportions -> calibrated scores
    territory : uniform sample restricted to the at-risk territory (stage 2 of territory-then-fate)"""
    n = c["y"].size
    if regime == "balanced":
        y = c["y"]; pen = c["X"][:, FEATURE_NAMES.index("penumbra_rule")] > 0.5
        pos = np.where(y == 1)[0]; bg = np.where((y == 0) & ~pen)[0]; pen_idx = np.where((y == 0) & pen)[0]
        take = []
        if pos.size: take.append(rng.choice(pos, min(30_000, pos.size), replace=False))
        if pen_idx.size: take.append(rng.choice(pen_idx, min(20_000, pen_idx.size), replace=False))
        if bg.size: take.append(rng.choice(bg, min(40_000, bg.size), replace=False))
        return np.concatenate(take) if take else np.array([], dtype=int)
    pool = np.where(territory_mask(c))[0] if regime == "territory" else np.arange(n)
    if pool.size == 0: return pool
    return rng.choice(pool, min(per_case, pool.size), replace=False)

def build_table(caches, norm, rng, regime, per_case, feature_idx, extra=None):
    """extra: optional dict case -> scalar appended as a patient-level column (used only by the explanatory TICI model)."""
    Xs, ys = [], []
    for c in caches:
        idx = sample_rows(c, rng, regime, per_case)
        if idx.size == 0: continue
        X = apply_normative(c["X"][idx], norm)[:, feature_idx]
        if extra is not None: X = np.hstack([X, np.full((X.shape[0], 1), extra[c["meta"]["case"]], np.float32)])
        Xs.append(X); ys.append(c["y"][idx])
    return np.concatenate(Xs), np.concatenate(ys)

def predict_scores(c, norm, model, feature_idx, regime, extra_value=None):
    X = apply_normative(c["X"], norm)[:, feature_idx]
    if extra_value is not None: X = np.hstack([X, np.full((X.shape[0], 1), extra_value, np.float32)])
    p = model.predict_proba(X)[:, 1].astype(np.float32)
    if regime == "territory": p = np.where(territory_mask(c), p, 0.0).astype(np.float32)   # outside the territory: never dead
    return p

# ---------- persistence ----------
def _scores_valid(path, cache_dir, cfg_hash, case):
    try:
        pr = load_scores(path); c = get_cache(cache_dir, cfg_hash, case)
        return bool(pr["case"] == case and pr["shape"] == c["shape"] and pr["mask"].sum() == c["mask"].sum()
                    and pr["p"].shape == (int(c["mask"].sum()),) and np.isfinite(pr["p"]).all())
    except Exception:
        return False

def save_scores(path, c, case, p):
    tmp = f"{path}.{uuid.uuid4().hex}.tmp.npz"
    np.savez_compressed(tmp, case=case, affine=c["affine"], mask_shape=np.array(c["shape"]), mask=np.packbits(c["mask"]),
                        lesion_full=np.packbits(c["lesion_full"]), voxel_ml=np.array(c["voxel_ml"]), p=p.astype(np.float32))
    os.replace(tmp, path)

def load_scores(path):
    z = np.load(path, allow_pickle=False); shape = tuple(int(v) for v in z["mask_shape"]); n = int(np.prod(shape))
    return {"case": str(z["case"]), "affine": z["affine"], "shape": shape, "voxel_ml": float(z["voxel_ml"]),
            "mask": np.unpackbits(z["mask"])[:n].reshape(shape).astype(bool),
            "lesion_full": np.unpackbits(z["lesion_full"])[:n].reshape(shape).astype(bool), "p": z["p"]}

def load_v2_prediction(path):
    """v2 prediction files hold m1_prob and m2_sdt; expose the same interface as load_scores."""
    z = np.load(path, allow_pickle=False); shape = tuple(int(v) for v in z["mask_shape"]); n = int(np.prod(shape))
    return {"case": str(z["case"]), "affine": z["affine"], "shape": shape, "voxel_ml": float(z["voxel_ml"]),
            "mask": np.unpackbits(z["mask"])[:n].reshape(shape).astype(bool),
            "lesion_full": np.unpackbits(z["lesion_full"])[:n].reshape(shape).astype(bool),
            "m1_prob": z["m1_prob"] if "m1_prob" in z else None, "m2_sdt": z["m2_sdt"] if "m2_sdt" in z else None}

# ---------- decision rules ----------
def vol_from_flat(pr, flat_bool):
    v = np.zeros(pr["shape"], dtype=bool); v[pr["mask"]] = flat_bool; return v

def rule_cutoff(pr, p, cutoff, min_vox):
    return drop_small_components(vol_from_flat(pr, p >= cutoff), min_vox)

def rule_volume_matched(pr, p, target_ml):
    """The hybrid: call dead exactly the k highest-scoring voxels, where k realises the target volume."""
    k = int(round(max(target_ml, 0.0) / pr["voxel_ml"]))
    flat = np.zeros(p.size, dtype=bool)
    if k > 0:
        flat[np.argpartition(-p, min(k, p.size) - 1)[:min(k, p.size)]] = True
    return vol_from_flat(pr, flat)

def expected_volume_ml(pr, p):
    """For calibrated scores, the sum of probabilities is the model's own volume estimate."""
    return float(p.sum() * pr["voxel_ml"])

def m2_volume_ml(pr2, offset, min_vox):
    """Model 2's volume AFTER the same small-component cleanup used when Model 2 is scored on its own."""
    if pr2["m2_sdt"] is None: return np.nan
    return float(drop_small_components(vol_from_flat(pr2, pr2["m2_sdt"] < offset), min_vox).sum() * pr2["voxel_ml"])

# ---------- metrics ----------
def surface_distance_mm(pred, truth, voxel_mm):
    """Average symmetric surface distance in mm; nan if either region is empty."""
    if pred.sum() == 0 or truth.sum() == 0: return np.nan
    ps = pred & ~binary_erosion(pred); ts = truth & ~binary_erosion(truth)
    d_to_t = distance_transform_edt(~ts, sampling=voxel_mm); d_to_p = distance_transform_edt(~ps, sampling=voxel_mm)
    return float((d_to_t[ps].sum() + d_to_p[ts].sum()) / (ps.sum() + ts.sum()))

def case_metrics(pr, pred_vol, p=None, c=None):
    truth = pr["lesion_full"]; ml = pr["voxel_ml"]; tv, pv = float(truth.sum() * ml), float(pred_vol.sum() * ml)
    row = {"lesion_ml": tv, "pred_ml": pv, "signed_vol_err_ml": pv - tv, "abs_vol_err_ml": abs(pv - tv),
           "dice": dice(pred_vol, truth), "asd_mm": surface_distance_mm(pred_vol, truth, (2.0, 2.0, 2.0)),
           "lesion_ge5ml": bool(tv >= 5.0)}
    if p is not None and c is not None:
        pen = c["X"][:, FEATURE_NAMES.index("penumbra_rule")] > 0.5; y = c["y"]
        if pen.sum() > 50 and 0 < y[pen].mean() < 1:
            from sklearn.metrics import roc_auc_score; row["penumbra_auc"] = float(roc_auc_score(y[pen], p[pen]))
        else: row["penumbra_auc"] = np.nan
        if 0 < y.mean() < 1:
            from sklearn.metrics import roc_auc_score; row["mask_auc"] = float(roc_auc_score(y, p))   # inside the feature mask only
    row["pred_empty"] = bool(pred_vol.sum() == 0)
    return row

def summarize(df):
    out = {"n_test": int(len(df))}
    for name, sub in (("all", df), ("ge5", df[df.lesion_ge5ml])):
        v = sub["dice"]; lo, hi = bootstrap_mean_ci(v); out[f"mean_dice_{name}"] = float(v.mean()) if len(v) else np.nan
        out[f"dice_{name}_ci_lo"], out[f"dice_{name}_ci_hi"], out[f"n_{name}"] = lo, hi, int(len(v))
    lt = df[~df.lesion_ge5ml]["dice"]; out["mean_dice_lt5"] = float(lt.mean()) if len(lt) else np.nan
    out["median_abs_vol_err_ml"] = float(df.abs_vol_err_ml.median()); out["median_signed_vol_err_ml"] = float(df.signed_vol_err_ml.median())
    out["mean_asd_mm"] = float(df.asd_mm.mean()) if df.asd_mm.notna().any() else np.nan
    out["n_asd_valid"] = int(df.asd_mm.notna().sum()); out["n_pred_empty"] = int(df.pred_empty.sum()) if "pred_empty" in df else 0
    if "penumbra_auc" in df: out["penumbra_auc_mean"] = float(df.penumbra_auc.mean())
    if "mask_auc" in df: out["mask_auc_mean"] = float(df.mask_auc.mean())
    return out

def tune_cutoff(preds, cutoffs, min_vox):
    """Cutoff maximising mean full-truth Dice over ALL supplied OOF cases (the primary metric)."""
    def score(t):
        vals = [dice(rule_cutoff(pr, pr["p"], t, min_vox), pr["lesion_full"]) for pr in preds]
        return np.mean(vals) if vals else -1
    best = max(cutoffs, key=score); return float(best), float(score(best))

# ---------- in-memory cache memo (validated once per session) ----------
CACHE_MEMO = {}
def get_cache(cache_dir, cfg_hash, case):
    if case not in CACHE_MEMO:
        CACHE_MEMO[case] = load_cache(f"{cache_dir}/{case}.npz", cfg_hash, case)
    return CACHE_MEMO[case]

# ---------- cross-validation for a training configuration ----------
def cross_validate(dev_cases, cache_dir, cfg_hash, out_dir, n_folds, seed, device, n_trees, regime, per_case,
                   feature_idx, extra=None, log=print, run_hash=None):
    """Patient-level K-fold producing out-of-fold scores for every dev case. Normative stats per fold from training
    patients only. Completed folds are reused when their marker matches this configuration and files validate."""
    os.makedirs(out_dir, exist_ok=True)
    order = list(dev_cases); np.random.default_rng(seed).shuffle(order)
    folds = [order[i::n_folds] for i in range(n_folds)]
    for k, held in enumerate(folds):
        marker = f"{out_dir}/fold_{k}.done.json"
        if os.path.exists(marker):
            m = json.load(open(marker))
            ok = m.get("run_hash") == run_hash and m.get("held") == held and all(_scores_valid(f"{out_dir}/{c}.npz", cache_dir, cfg_hash, c) for c in held)
            if ok: log(f"  fold {k+1}/{n_folds}: valid, reused"); continue
            log(f"  fold {k+1}/{n_folds}: marker or files invalid for this configuration -> recomputing"); os.remove(marker)
        t0 = time.time(); train = [c for c in order if c not in held]
        rng = np.random.default_rng([seed, k])                      # fold-local stream: independent of which folds ran before
        train_caches = [get_cache(cache_dir, cfg_hash, c) for c in train]
        norm = compute_normative(train_caches, seed=seed + k)
        X, y = build_table(train_caches, norm, rng, regime, per_case, feature_idx, extra)
        model = make_classifier(device, seed + k, n_trees); model.fit(X, y)
        for c in held:
            hc = get_cache(cache_dir, cfg_hash, c)
            save_scores(f"{out_dir}/{c}.npz", hc, c, predict_scores(hc, norm, model, feature_idx, regime, None if extra is None else extra[c]))
        json.dump({"fold": k, "held": held, "n_train_voxels": int(X.shape[0]), "positives": float(y.mean()), "seconds": time.time() - t0,
                   "run_hash": run_hash}, open(marker, "w"))
        log(f"  fold {k+1}/{n_folds}: {X.shape[0]:,} voxels ({y.mean():.1%} dead) -> {len(held)} held-out in {time.time()-t0:.0f}s")
        del X, y
    return folds

def fit_final(dev_cases, cache_dir, cfg_hash, seed, device, n_trees, regime, per_case, feature_idx, extra=None):
    caches = [get_cache(cache_dir, cfg_hash, c) for c in dev_cases]
    norm = compute_normative(caches, seed=seed); rng = np.random.default_rng(seed)
    X, y = build_table(caches, norm, rng, regime, per_case, feature_idx, extra)
    model = make_classifier(device, seed, n_trees); model.fit(X, y)
    return model, norm, {"n_train_voxels": int(X.shape[0]), "positives": float(y.mean())}

# ---------- ledger ----------
LEDGER_COLS = ["experiment", "variant", "training_regime", "decision_rule", "features", "n_test", "mean_dice_all", "dice_all_ci_lo", "dice_all_ci_hi",
               "median_abs_vol_err_ml", "median_signed_vol_err_ml", "n_ge5", "mean_dice_ge5", "dice_ge5_ci_lo", "dice_ge5_ci_hi", "mean_dice_lt5",
               "mean_asd_mm", "n_asd_valid", "n_pred_empty", "penumbra_auc_mean", "mask_auc_mean", "comparable", "note", "fingerprint", "utc"]
def ledger_append(path, row):
    """Append one row; a rerun of the same experiment+variant replaces its earlier row instead of duplicating it."""
    row = {k: row.get(k, np.nan) for k in LEDGER_COLS}; row["utc"] = datetime.datetime.utcnow().isoformat()
    old = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame(columns=LEDGER_COLS)
    old = old[~((old.experiment == row["experiment"]) & (old.variant == row["variant"]))]
    pd.concat([old, pd.DataFrame([row])], ignore_index=True).to_csv(path, index=False)

# ---------- phenotype (TICI) ----------
def read_case_phenotype(root, case):
    """All CSVs under a case folder (the PRIVATE copies) merged into one dict; keys prefixed by file stem."""
    merged = {}
    for path in sorted(glob.glob(f"{root}/**/{case}/**/*.csv", recursive=True)):
        df = pd.read_csv(path); stem = os.path.basename(path).split(f"{case}_")[-1].replace(".csv", "")
        rec = ({str(k): v for k, v in zip(df.iloc[:, 0], df.iloc[:, 1])} if (df.shape[1] == 2 and df.shape[0] > 1) else df.iloc[0].to_dict())
        merged.update({f"{stem}::{k}": v for k, v in rec.items()})
    return merged

def tici_grade(v):
    """mTICI reperfusion grade -> ordinal 0..5 (0, 1, 2a, 2b, 2c, 3). Accepts '2b', 'TICI 2c', '3', '3.0', 3.0."""
    if v is None or (isinstance(v, float) and np.isnan(v)): return np.nan
    s = str(v).strip().lower().replace("mtici", "").replace("tici", "").replace(" ", "")
    if s.endswith(".0"): s = s[:-2]
    table = {"0": 0, "1": 1, "2a": 2, "2b": 3, "2c": 4, "3": 5}
    return float(table[s]) if s in table else np.nan

def find_tici_column(rec):
    """Exactly the documented post-treatment field ('mTici postinterventional', 047 normalisation); None if absent."""
    import re
    norm = lambda h: re.sub(r"\s+", " ", str(h).split("::")[-1].replace("\ufeff", "").strip()).casefold()
    hits = [k for k in rec if norm(k) == "mtici postinterventional"]
    return hits[0] if len(hits) == 1 else None

# ---------- shared deterministic tie rule (Astra, sprint-5 review) ----------
def rank_order(p):
    """One truth-independent ordering used by BOTH the top-k rule and the prefix diagnostic: score descending, voxel index ascending."""
    return np.lexsort((np.arange(p.size), -p))

def rule_topk_lexsort(pr, p, target_ml):
    """Call dead exactly the k highest-scoring voxels under rank_order (k realises the target volume)."""
    k = int(round(max(target_ml, 0.0) / pr["voxel_ml"])); flat = np.zeros(p.size, dtype=bool)
    if k > 0: flat[rank_order(p)[:min(k, p.size)]] = True
    return vol_from_flat(pr, flat)

def percase_valid(path, expected_cases):
    try:
        df = pd.read_csv(path); return bool(set(df.case) == set(expected_cases) and df.case.is_unique and np.isfinite(df[["dice", "abs_vol_err_ml", "lesion_ml"]].values).all())
    except Exception:
        return False


def official_lesion_metrics(truth, pred, empty_value=1.0):
    """Exact semantics of the pinned official `compute_dice_f1_instance_difference`: 26-connected components (cc3d default) on truth and
    prediction; overlapping (truth, pred) component pairs scored by IoU, sorted descending, matched greedily one-to-one when IoU >= 0.2;
    F1 = TP / (TP + 0.5 FP + 0.5 FN); lesion-count difference = |n_truth - n_pred|; Dice = global binary Dice; both-empty -> empty_value."""
    from scipy.ndimage import label as _lab
    truth = np.asarray(truth).astype(bool); pred = np.asarray(pred).astype(bool); s = np.ones((3, 3, 3), bool)
    lt, nt = _lab(truth, structure=s) if truth.any() else (np.zeros(truth.shape, np.int32), 0); lp, npd = _lab(pred, structure=s) if pred.any() else (np.zeros(pred.shape, np.int32), 0)
    count_diff = abs(nt - npd)
    if nt == 0 and npd == 0: return float(empty_value), int(count_diff), float(empty_value)
    inter = float((truth & pred).sum()); dsc = 2 * inter / (truth.sum() + pred.sum()) if (truth.sum() + pred.sum()) > 0 else float(empty_value)
    pairs = []
    if nt and npd:
        both = truth & pred; rl, pl = lt[both], lp[both]; combos = np.unique(np.stack([rl, pl], 1), axis=0) if both.any() else np.zeros((0, 2), int)
        vt = np.bincount(lt.ravel()); vp = np.bincount(lp.ravel())
        for r, p in combos:
            i = float(((lt == r) & (lp == p)).sum()); u = float(vt[r] + vp[p] - i); pairs.append((i / u if u > 0 else 0.0, int(r), int(p)))
    pairs.sort(key=lambda x: -x[0]); mr, mp, tp = set(), set(), 0
    for iou, r, p in pairs:
        if r in mr or p in mp: continue
        if iou >= 0.2: mr.add(r); mp.add(p); tp += 1
    fp, fn = npd - tp, nt - tp; f1 = 0.0 if tp == 0 else tp / (tp + 0.5 * fp + 0.5 * fn)
    return float(f1), int(count_diff), float(dsc)


def smooth_scores(pr, p, sigma_mm, voxel_mm=2.0):
    if sigma_mm <= 0: return p
    vol = np.zeros(pr["shape"], np.float32); vol[pr["mask"]] = p; m = pr["mask"].astype(np.float32); sg = sigma_mm / voxel_mm
    return np.clip((gaussian_filter(vol, sg) / (gaussian_filter(m, sg) + 1e-6))[pr["mask"]], 0, 1).astype(np.float32)
_MEMO = None

def asd_mm(pred, truth, spacing):
    # pooled bidirectional nearest-boundary distances; undefined when either mask is empty
    if pred.sum() == 0 or truth.sum() == 0: return np.nan
    def surface(m): return m & ~binary_erosion(m)
    sp, st = surface(pred), surface(truth); dt_t = distance_transform_edt(~st, sampling=spacing); dt_p = distance_transform_edt(~sp, sampling=spacing)
    return float(np.concatenate([dt_t[sp], dt_p[st]]).mean())
def patient_scores(c, p, pred):
    truth = c["lesion_full"]; mask = c["mask"]; ml = c["voxel_ml"]
    tp = int((pred & truth).sum()); fp = int((pred & ~truth).sum()); fn = int((~pred & truth).sum()); tn = int((~pred & ~truth & mask).sum())
    dsc = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 1.0
    tv, pv = float(truth.sum() * ml), float(pred.sum() * ml); lf1, cdiff, _ = official_lesion_metrics(truth, pred, empty_value=1.0)
    y = truth[mask].astype(int); mask_pos, mask_neg = int(y.sum()), int(y.size - y.sum()); auc = float(roc_auc_score(y, p)) if 0 < mask_pos < y.size else np.nan; ap = float(average_precision_score(y, p)) if 0 < mask_pos < y.size else np.nan   # undefined when the mask holds no lesion voxel (or no non-lesion voxel)
    cov = float((truth & mask).sum() / truth.sum()) if truth.sum() else np.nan; bound = 2 * cov / (1 + cov) if truth.sum() else np.nan
    return {"dice": dsc, "f1_voxel": dsc, "precision": tp / (tp + fp) if (tp + fp) else np.nan, "recall": tp / (tp + fn) if (tp + fn) else np.nan, "specificity": tn / (tn + fp) if (tn + fp) else np.nan,
            "lesion_ml": tv, "pred_ml": pv, "abs_vol_err_ml": abs(pv - tv), "signed_vol_err_ml": pv - tv, "lesion_ge5ml": tv >= 5.0, "pred_empty": bool(pred.sum() == 0), "truth_empty": bool(truth.sum() == 0),
            "lesion_f1": lf1, "lesion_count_diff": cdiff, "asd_mm": asd_mm(pred, truth, VOXEL_MM), "fm_auroc": auc, "fm_avg_precision": ap,
            "lesion_coverage_by_mask": cov, "lesion_ml_outside_mask": float((truth & ~mask).sum() * ml), "mask_dice_bound": bound, "mask_pos": mask_pos, "mask_neg": mask_neg, "tp": tp, "fp": fp, "fn": fn}
# fixture checks of the lesion-wise metric (empty masks, diagonal contact, one split prediction, one matched lesion plus one false positive, IoU exactly at the 0.2 threshold); ties and merges are not covered here
def _fx():
    z = lambda: np.zeros((6, 6, 3), bool); out = {}
    t = z(); p = z(); out["both_empty"] = official_lesion_metrics(t, p)[:2]
    t = z(); t[1:3, 1:3, 1] = 1; p = z(); out["truth_only"] = official_lesion_metrics(t, p)[:2]
    t = z(); t[0, 0, 0] = 1; t[1, 1, 1] = 1; p = z(); p[0, 0, 0] = 1; p[1, 1, 1] = 1; out["diagonal_contact_one_piece"] = official_lesion_metrics(t, p)[:2]
    t = z(); t[0:4, 0:4, 1] = 1; p = z(); p[0:2, 0:4, 1] = 1; p[3:4, 0:4, 1] = 1; out["truth_one_pred_two_split"] = official_lesion_metrics(t, p)[:2]
    t = z(); t[0:2, 0:6, 1] = 1; p = z(); p[0:2, 0:6, 1] = 1; p[3:5, 0:6, 1] = 1; out["one_matched_one_fp"] = official_lesion_metrics(t, p)[:2]
    t = z(); t[0:5, 0, 0] = 1; p = z(); p[0:1, 0, 0] = 1; out["iou_0.2_boundary"] = official_lesion_metrics(t, p)[:2]
    return out
def coverage_support(values, brain, coverage=None):
    values = np.asarray(values)
    brain = np.asarray(brain, dtype=bool)
    if values.shape != brain.shape:
        raise ValueError("brain shape mismatch")
    support = brain & np.isfinite(values)
    if coverage is not None:
        coverage = np.asarray(coverage)
        if coverage.shape != values.shape or not np.isfinite(coverage).all() or not np.isin(coverage, [0, 1]).all():
            raise ValueError("invalid spatial coverage mask")
        support &= coverage.astype(bool)
    return support, {"coverage_known": coverage is not None, "brain_n": int(brain.sum()),
                     "support_n": int(support.sum()), "nonfinite_in_brain": int((brain & ~np.isfinite(values)).sum())}
def zscore_in_brain(x, brain):
    x = np.asarray(x, dtype=float)
    support, _ = coverage_support(x, brain)
    v = x[support]; out = np.zeros_like(x, dtype=np.float32)
    m, s = (float(v.mean()), float(v.std())) if v.size else (0., 0.)
    su = max(s, ZSCORE_MIN_SD)
    rec = {"mean": m, "sd": s, "sd_used": su, "n": int(v.size), "fallback": None}
    if not v.size or s < 1e-6:
        rec["fallback"] = "empty support" if not v.size else "constant support"
        return out, rec
    out[support] = (v - m) / su
    rec.update({"fallback": "SD floored" if s < ZSCORE_MIN_SD else None,
                "z_min": float(out[support].min()), "z_max": float(out[support].max())})
    return out, rec
def histeq_in_brain(x, brain, nbins=None):
    x = np.asarray(x, dtype=float)
    support, _ = coverage_support(x, brain)
    v = x[support]; out = np.zeros_like(x, dtype=np.float32)
    if not v.size or float(v.std()) < 1e-6:
        return out, {"fallback": "empty support" if not v.size else "constant support", "n": int(v.size)}
    if np.any((v < 0) | (v > 1)):
        raise ValueError("histogram input must be windowed to [0,1]")
    bins = HISTEQ_BINS if nbins is None else nbins
    hist, edges = np.histogram(v, bins=bins, range=(0., 1.))
    cdf = np.cumsum(hist).astype(float); cdf /= cdf[-1]
    out[support] = np.interp(v, (edges[:-1] + edges[1:]) / 2, cdf)
    return out, {"fallback": None, "n": int(v.size), "share_at_window_floor": float((v <= 1e-6).mean()), "share_at_window_ceiling": float((v >= 1-1e-6).mean())}
def window01(v, lo, hi):
    v = np.where(np.isfinite(v), v, lo); return ((np.clip(v, lo, hi) - lo) / (hi - lo)).astype(np.float32)
def _pnorm_channel(v, kind, levels, brain):
    valid = np.isfinite(v) & ((v > 0) if kind in ("cbf", "cbv", "mtt") else (v >= 0))
    rec = {"level": None, "n": 0, "median": None, "mad": None, "sd": None, "scale": None, "fallback": "window", "clip_low": None, "clip_high": None}
    ref = None
    for level, base in levels:
        r_ = base & valid
        if int(r_.sum()) >= PNORM_NN["min_ref_voxels"]: ref = r_; rec["level"] = level; break
    if ref is not None:
        vals = v[ref]; med = float(np.median(vals)); mad = float(np.median(np.abs(vals - med))); sd = float(np.std(vals)); ms = PNORM_NN["min_scale"][kind]
        scale, fb = (1.4826 * mad, "MAD") if np.isfinite(mad) and 1.4826 * mad >= ms else ((sd, "SD") if np.isfinite(sd) and sd >= ms else (None, "window"))
        rec.update({"n": int(ref.sum()), "median": med if np.isfinite(med) else None, "mad": mad, "sd": sd, "scale": scale, "fallback": fb})
        if scale is not None and np.isfinite(med):
            z = (np.where(np.isfinite(v), v, med) - med) / scale; zc = PNORM_NN["clip_z"]; zb = z[brain]
            rec.update({"clip_low": float(np.mean(zb < -zc)), "clip_high": float(np.mean(zb > zc))})
            return ((np.clip(z, -zc, zc) + zc) / (2 * zc)).astype(np.float32), rec
        rec["fallback"] = "window"
    return window01(v, *WINDOWS[kind]), rec
def source_paths(case,with_ctp=False):
 need(isinstance(case,str)and case and '/' not in case and '\\' not in case and case not in('.','..'),'E043')
 d=f'train/derivatives/{case}'
 paths={k:f'{d}/ses-01/perfusion-maps/{case}_ses-01_space-ncct_{k}.nii.gz' for k in PERF_KINDS}
 paths.update(ncct=f'train/raw_data/{case}/ses-01/{case}_ses-01_ncct.nii.gz',
    cta=f'{d}/ses-01/{case}_ses-01_space-ncct_cta.nii.gz',
    lesion=f'{d}/ses-02/{case}_ses-02_space-ncct_lesion-msk.nii.gz',
    brain=f'brainmask/{case}_brainmask.nii.gz')
 if with_ctp:paths['ctp']=f'{d}/ses-01/{case}_ses-01_space-ncct_ctp.nii.gz'
 return paths
def source_inventory(input_root,cases,with_ctp,expected_sha256):
 expected={c:dict(source_paths(c,with_ctp),cache=f'feature-cache-2mm-v2/{c}.npz')for c in cases}
 allowed={rel for row in expected.values()for rel in row.values()}|{K_BPJ,K_BHJ}
 present={p.relative_to(input_root).as_posix()for p in Path(input_root).rglob('*')if p.is_file()}
 need(present==allowed,'E044')
 inventory={rel:file_info(rooted(input_root,rel))for rel in sorted(allowed)}
 need(sha_bytes(json.dumps(inventory,sort_keys=True,allow_nan=False).encode())==expected_sha256,'E045')
 return{'cases':{c:{k:dict(path=rel,**inventory[rel])for k,rel in row.items()}for c,row in expected.items()},
   'baseline_plans':dict(path=K_BPJ,**inventory[K_BPJ]),
   K_BH:dict(path=K_BHJ,**inventory[K_BHJ])}
def _input_manifest(input_root,contract,sel):
 splits=load_frozen_partitions(contract);cases=sorted(c for fold in splits for c in fold['val'])
 arms={f['arm']for f in contract[K_EP]['fits']if f[K_PI]==sel['id']}
 need(not arms& {K_AZ,K_AH},'U3 coverage held: no cohort-authenticated support definition')
 mapped=source_inventory(input_root,cases,False,sel[K_ICS])
 need(mapped['baseline_plans']['sha256']==BASE_PLANS_SHA256,'E046')
 need(mapped[K_BH]['sha256']==BASE_HANDOFF_SHA256,'E047')
 handoff=json.loads(read_verified(input_root,mapped[K_BH]).read_bytes())
 need(handoff['smoke']is False and sorted(handoff['cases'])==cases,'E048')
 need(handoff['arm']==K_ACMC and handoff['splits']==splits,'E049')
 need(handoff['source_inventory']=={'brain':'cad80ea68c35','cbf':'71905e6a3737','cbv':'678b1bfd5639','cta':'f3f200c85d00','lesion':'fbcfad347f52','mtt':'732e673174db','ncct':'b5137a3f1df6','tmax':'71fb01614363'},'E050')
 return mapped
def _native_paths(raw,pre,results):
 os.environ.update(nnUNet_raw=str(raw),nnUNet_preprocessed=str(pre),nnUNet_results=str(results),nnUNet_n_proc_DA='12')
def _load_case_sources(input_root,sources,arm):
 needed=set(BASE6)|{'brain','lesion','cache'}
 if arm in(K_AZ,K_AH):needed.add('ctp')
 need(set(sources)==needed,'E051')
 paths={k:read_verified(input_root,sources[k])for k in needed}
 ref=nib.load(str(paths['ncct']));arrays={}
 for k in needed-{'cache'}:
  img=nib.load(str(paths[k]));arr=np.asanyarray(img.dataobj)
  if k!='ctp' and arr.ndim==4 and arr.shape[-1]==1:arr=arr[...,0]
  need(arr.shape[:3]==ref.shape[:3]and np.allclose(img.affine,ref.affine,atol=.001,rtol=0),'E080')
  need(arr.ndim==(4 if k=='ctp' else 3),'E081')
  arrays[k]=arr
 brain=arrays['brain']>.5;ml=float(brain.sum()*np.prod(ref.header.get_zooms()[:3])/1000)
 need(400<=ml<=2500,'E052')
 need(np.isfinite(arrays['brain']).all()and np.isfinite(arrays['lesion']).all(),'E053')
 return ref,arrays,paths
def _dataset_name(arm):
 return f'Dataset{731+ARMS_ORDER.index(arm):03d}_ISLES24_{arm}'
def _prepared_paths(root,arm):
 ds=_dataset_name(arm)
 return Path(root)/'raw'/ds,Path(root)/'preprocessed'/ds
def _case_raw(input_root,output_root,contract,case,sources,arm):
 ref,arrays,paths=_load_case_sources(input_root,sources,arm)
 x,qc=transform_case(arrays,arm)
 cache=load_cache(str(paths['cache']),config_hash(FEATURE_CFG),case)
 truth=arrays['lesion']>.5
 mapped=resample_from_to(nib.Nifti1Image(truth.astype(np.uint8),ref.affine),(cache['shape'],cache['affine']),order=0).get_fdata()>.5
 need(dice(mapped,cache[K_LF])>=.999,'E054')
 raw,pre=_prepared_paths(output_root,arm);written=[]
 for i,(ch,arr)in enumerate(x.items()):
  p=raw/'imagesTr'/f'{case}_{i:04d}.nii.gz';p.parent.mkdir(parents=True,exist_ok=True)
  need(not p.exists(),'E082');nib.save(nib.Nifti1Image(arr,ref.affine),str(p));written.append(p)
 p=raw/'labelsTr'/f'{case}.nii.gz';p.parent.mkdir(parents=True,exist_ok=True)
 need(not p.exists(),'E055');nib.save(nib.Nifti1Image(truth.astype(np.uint8),ref.affine),str(p));written.append(p)
 q=Path(output_root)/'qc'/f'{case}.json'
 write_once(output_root,q.relative_to(output_root).as_posix(),canonical({'channels':qc,'source_cache_dice':float(dice(mapped,cache[K_LF])),'brain_ml':float((arrays['brain']>.5).sum()*np.prod(ref.header.get_zooms()[:3])/1000),'infarct_in_brain':float((truth& (arrays['brain']>.5)).sum()/truth.sum())if truth.any()else 1.}))
 written.append(q)
 return written  
def _prepare_shared(input_root,output_root,contract,manifest,arm,splits,sel):
 from nnunetv2.experiment_planning.dataset_fingerprint.fingerprint_extractor import DatasetFingerprintExtractor
 raw,pre=_prepared_paths(output_root,arm);ds=raw.name
 n=12 if arm==K_AM else 6
 dataset={'channel_names':{str(i):'noNorm' for i in range(n)},'labels':{'background':0,'infarct':1},'numTraining':99,'file_ending':'.nii.gz'}
 write_once(output_root,(raw/K_DJ).relative_to(output_root).as_posix(),canonical(dataset))
 DatasetFingerprintExtractor(ds,num_processes=6,verbose=False).run(overwrite_existing=False)
 bp=read_verified(input_root,manifest['baseline_plans']);bh=read_verified(input_root,manifest[K_BH])
 base=json.loads(bp.read_bytes());handoff=json.loads(bh.read_bytes())
 need(handoff['arm']==K_ACMC and handoff['splits']==splits,'E056')
 need(handoff['plans']==base,'E057')
 need(all(handoff['windows'][k]==list(WINDOWS[k])for k in BASE6),'E058')
 need(handoff['smoke']is False and len(handoff['cases'])==99,'E059')
 if arm=='A1_L':
  from nnunetv2.utilities.find_class_by_name import recursive_find_python_class
  import nnunetv2
  cls=recursive_find_python_class(str(Path(nnunetv2.__file__).parent/'experiment_planning'),'nnUNetPlannerResEncL','nnunetv2.experiment_planning')
  need(cls is not None,'E083')
  planner=cls(ds);plans=planner.plan_experiment()
  need(plans[K_PN]==sel[K_PN],'E084')
 else:
  plans=copy.deepcopy(base);plans['dataset_name']=ds
  for cfg in plans[K_C].values():
   if K_NS in cfg:
    need(set(cfg[K_NS])=={K_N},'E092')
    cfg[K_NS]=[K_N]*n
   if 'use_mask_for_norm' in cfg:cfg['use_mask_for_norm']=[False]*n
  fp=json.loads((pre/K_DFJ).read_bytes())
  if K_FIPPC in plans:plans[K_FIPPC]=fp[K_FIPPC]
  write_once(output_root,(pre/(sel[K_PN]+'.json')).relative_to(output_root).as_posix(),canonical(plans))
  for key in('patch_size','spacing','batch_size','architecture'):
   need(plans[K_C][K_3F][key]==base[K_C][K_3F][key],'E090')
 if not(pre/K_DJ).exists():write_once(output_root,(pre/K_DJ).relative_to(output_root).as_posix(),canonical(dataset))
 write_once(output_root,(pre/K_SFJ).relative_to(output_root).as_posix(),canonical(splits))
 write_once(output_root,'preparation.json',canonical({'arm':arm,'dataset':ds,K_PN:sel[K_PN],K_PS:file_info(pre/(sel[K_PN]+'.json'))['sha256'],K_PI:sel['id'],K_SS:sel[K_SS]}))
 return None
def _native_case(output_root,contract,case,arm,sel):
 from nnunetv2.utilities.plans_handling.plans_handler import PlansManager
 raw,pre=_prepared_paths(output_root,arm)
 pm=PlansManager(str(pre/(sel[K_PN]+'.json')));cfg=pm.get_configuration(K_3F)
 worker=cfg.preprocessor_class(verbose=False);folder=pre/cfg.data_identifier;folder.mkdir(parents=True,exist_ok=True)
 images=sorted(str(p)for p in(raw/'imagesTr').glob(case+'_*.nii.gz'))
 worker.run_case_save(str(folder/case),images,str(raw/'labelsTr'/f'{case}.nii.gz'),pm,cfg,json.loads((raw/K_DJ).read_bytes()))
 files=[p.relative_to(output_root).as_posix()for p in folder.glob(case+'.*')if p.is_file()]
 files+= [p.relative_to(output_root).as_posix()for p in folder.glob(case+'_seg.*')if p.is_file()]
 need(len(files)>=2,'E060')
 return files
def _arm(plan,sel):
 arms={f['arm']for f in plan['fits']if f[K_PI]==sel['id']}
 if arms=={K_AR,'A1_repeat2'}:return K_AR
 need(len(arms)==1,'E061')
 arm=next(iter(arms));need(arm not in(K_AZ,K_AH),'U3 coverage held')
 return arm
def _shared_publish(input_root,root,contract,manifest,arm,splits,sel):
 import shutil
 with tempfile.TemporaryDirectory(prefix='.staging-',dir=root)as td:
  stage=Path(td);_native_paths(stage/'raw',stage/'preprocessed',stage/'native-work')
  for case,sources in manifest['cases'].items():_case_raw(input_root,stage,contract,case,sources,arm)
  _prepare_shared(input_root,stage,contract,manifest,arm,splits,sel)
  _,src=_prepared_paths(stage,arm);_,dest=_prepared_paths(root,arm)
  dataset=json.loads((src/K_DJ).read_bytes())
  dataset['item4_fingerprint']=json.loads((src/K_DFJ).read_bytes())
  dataset['item4']={'arm':arm,K_PI:sel['id'],K_ICS:sel[K_ICS],
      K_SCS:sel[K_SCS],K_SS:sel[K_SS]}
  files=[]
  for name,raw in[(K_DJ,canonical(dataset)),(sel[K_PN]+'.json',(src/(sel[K_PN]+'.json')).read_bytes()),(K_SFJ,canonical(splits))]:
   rel=(dest/name).relative_to(root).as_posix();write_once(root,rel,raw);files.append(rel)
 commit_step(root,contract,'shared',files)
def _case_publish(input_root,root,contract,case,sources,arm,sel):
 import pickle
 with tempfile.TemporaryDirectory(prefix='.staging-',dir=root)as td:
  stage=Path(td);_native_paths(stage/'raw',stage/'preprocessed',stage/'native-work')
  _case_raw(input_root,stage,contract,case,sources,arm)
  raw,sp=_prepared_paths(stage,arm);_,pre=_prepared_paths(root,arm)
  for name in(K_DJ,sel[K_PN]+'.json'):
   write_once(stage,(sp/name).relative_to(stage).as_posix(),(pre/name).read_bytes())
  write_once(stage,(raw/K_DJ).relative_to(stage).as_posix(),(pre/K_DJ).read_bytes())
  emitted=_native_case(stage,contract,case,arm,sel)
  need(len(emitted)==3,'E085')
  prop=next(stage/r for r in emitted if r.endswith('.pkl'))
  with prop.open('rb')as f:properties=pickle.load(f)
  need('item4' not in properties,'E086')
  properties['item4']={'schema':'item4-private-scoring/v1','cache_bytes':read_verified(input_root,sources['cache']).read_bytes(),
       'cache_info':{k:sources['cache'][k]for k in('sha256','bytes')},
       'truth_nifti':(raw/'labelsTr'/f'{case}.nii.gz').read_bytes(),
       'qc':json.loads((stage/'qc'/f'{case}.json').read_bytes())}
  with prop.open('wb')as f:pickle.dump(properties,f,protocol=4)
  files=[]
  for rel in emitted:
   write_once(root,rel,(stage/rel).read_bytes());files.append(rel)
 commit_step(root,contract,'native-'+case,files)
def preprocess(input_root,output_root,contract):
 plan,rt,sel=bound_plan(contract,True)
 environment_check(plan[K_ER]);_load_science()
 arm=_arm(plan,sel);manifest=_input_manifest(input_root,contract,sel);splits=load_frozen_partitions(contract)
 cases=sorted(c for s in splits for c in s['val'])
 need(set(manifest['cases'])==set(cases),'E062')
 root=Path(output_root).resolve();root.mkdir(parents=True,exist_ok=True)
 completed=contract.setdefault('completed_steps',{});known=verify_completed(root,completed)
 need({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(known),'E063')
 need(set(completed)<={'shared'}|{'native-'+c for c in cases},'E064')
 need(not completed or 'shared' in completed,'E065')
 if 'shared' not in completed:_shared_publish(input_root,root,contract,manifest,arm,splits,sel)
 for case in cases:
  if 'native-'+case not in completed:_case_publish(input_root,root,contract,case,manifest['cases'][case],arm,sel)
 return validate_preprocessing(root,contract)
def _private_scoring(properties):
 payload=properties.get('item4',{})
 need(payload.get('schema')=='item4-private-scoring/v1','E066')
 b=payload['cache_bytes'];info=payload['cache_info']
 need(isinstance(b,bytes)and info=={'sha256':sha_bytes(b),'bytes':len(b)},'E067')
 qc=payload['qc']
 need(qc['source_cache_dice']>=.999 and 400<=qc['brain_ml']<=2500,'E068')
 need(all(math.isfinite(x['prepared_sd'])and x['prepared_sd']>=1e-6 for x in qc['channels'].values()),'E069')
 need(isinstance(payload['truth_nifti'],bytes)and payload['truth_nifti'],'E070')
 return payload
def validate_preprocessing(output_root,contract):
 plan,rt,sel=bound_plan(contract,True);_load_science();arm=_arm(plan,sel)
 splits=load_frozen_partitions(contract);cases=sorted(c for s in splits for c in s['val'])
 files=verify_completed(output_root,contract.get('completed_steps',{}));root=Path(output_root).resolve()
 need(set(contract['completed_steps'])=={'shared'}|{'native-'+c for c in cases},'E071')
 need(len(files)==300 and set(files)=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()},'E072')
 _,pre=_prepared_paths(root,arm)
 need((pre/K_SFJ).read_bytes()==canonical(splits),'E073')
 metadata=json.loads((pre/K_DJ).read_bytes())['item4']
 need(metadata=={'arm':arm,K_PI:sel['id'],K_ICS:sel[K_ICS],K_SCS:sel[K_SCS],K_SS:sel[K_SS]},'E074')
 from nnunetv2.utilities.plans_handling.plans_handler import PlansManager
 from nnunetv2.training.dataloading.nnunet_dataset import infer_dataset_class
 pm=PlansManager(str(pre/(sel[K_PN]+'.json')));cfg=pm.get_configuration(K_3F)
 need(list(cfg.normalization_schemes)==[K_N]*(12 if arm==K_AM else 6),'E075')
 folder=pre/cfg.data_identifier;dataset=infer_dataset_class(str(folder))(str(folder))
 need(len(dataset.identifiers)==len(cases)and set(dataset.identifiers)==set(cases),'E076')
 for case in cases:
  loaded=dataset.load_case(case);data=np.asarray(loaded[0][:]);seg=np.asarray(loaded[1][:]);props=loaded[-1]
  need(data.ndim==4 and data.shape[0]==(12 if arm==K_AM else 6),'E087')
  need(seg.shape[1:]==data.shape[1:]and np.isfinite(data).all()and np.isfinite(seg).all(),'E088')
  need(np.isin(seg,[-1,0,1]).all()and 'class_locations' in props,'E089')
  _private_scoring(props)
 meta={K_PS:file_info(pre/(sel[K_PN]+'.json'))['sha256']}
 return preprocessing_receipts(root,contract,sel,meta,cases,pre,folder,files)
def preprocessing_receipts(root,contract,sel,meta,cases,pre,folder,committed):
 rt=contract['runtime'];root=Path(root)
 case_files={}
 for case in cases:
  members={}
  for role,bases in{'image':[case+'.b2nd',case+'.npy',case+'.npz'],
      'segmentation':[case+'_seg.b2nd',case+'_seg.npy',case+'_seg.npz'],
      'properties':[case+'.pkl']}.items():
   matches=[folder/b for b in bases if(folder/b).is_file()]
   need(len(matches)==1,'E091')
   q=matches[0];members[role]=dict(path=q.relative_to(root).as_posix(),**file_info(q))
  case_files[case]=members
 shared={k:dict(path=q.relative_to(root).as_posix(),**file_info(q))for k,q in
   {'dataset':pre/K_DJ,'plans':pre/(sel[K_PN]+'.json'),'splits':pre/K_SFJ}.items()}
 files={d['path']:{k:d[k]for k in('sha256','bytes')}for group in[*case_files.values(),shared]for d in group.values()}
 need(files==committed,'E077')
 module_sha=rt['execution'][K_MS]
 need(module_sha==sha_bytes(Path(__file__).read_bytes()),'E078')
 need(shared['plans']['sha256']==meta[K_PS]and shared['splits']['sha256']==sel[K_SS],'E079')
 identities={K_CS:sel[K_CS],K_ICS:sel[K_ICS],K_ES:contract[K_P][K_ES],K_PCS:module_sha}
 proposed=dict(identities,schema='modal-item4-preprocessed/v1',status='VALIDATED',source_capture_sha256=sel[K_SCS],plans_sha256=meta[K_PS],case_files=case_files,shared_files=shared)
 validation=dict(identities,schema='modal-preprocessing-validation/v1',status='PASS',errors=[],run_id=rt['run_id'],spec_sha256=rt['spec_sha256'],validator_sha256=module_sha,files=files)
 return{'proposed':proposed,K_V:validation}
def timing_record(fit_id,records,comparability_id):
 need(records,'E093')
 epochs=[r['epoch']for r in records]
 need(len(epochs)==len(set(epochs))and all(type(e)is int and e>=0 for e in epochs),'E094')
 need(epochs==list(range(epochs[0],epochs[0]+len(epochs))),'E095')
 need(all(type(r.get(K_TI))is int and r[K_TI]==250 and type(r.get(K_VI))is int and r[K_VI]==50 for r in records),'E096')
 need(all(math.isfinite(r['elapsed'])and r['elapsed']>0 and math.isfinite(r[K_LW])and 0<=r[K_LW]<=r['elapsed']for r in records),'E097')
 wait=sum(r[K_LW]for r in records);elapsed=sum(r['elapsed']for r in records)
 need(wait/elapsed<=.10,'E098')
 return{'schema':'experiment-epoch-timing/v1','fit_id':fit_id,'completed_epochs':len(records),'elapsed_training_seconds':elapsed,'real_epoch':True,K_LNB:True,'comparability_id':comparability_id,'measured_loader_wait_seconds':wait,'epoch_records':records}
def _trainer_class():
 from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
 class TimedIterator:
  def __init__(s,inner,owner):s.inner=inner;s.owner=owner
  def __iter__(s):return s
  def __next__(s):
   t=time.perf_counter();value=next(s.inner);s.owner._loader_wait+=time.perf_counter()-t;return value
  def __getattr__(s,k):return getattr(s.inner,k)
 class ReviewedTrainer(nnUNetTrainer):
  def __init__(s,plans,configuration,fold,dataset_json,device):
   super().__init__(plans,configuration,fold,dataset_json,device);s._measurements=[];s._loader_wait=0.;s._loaded_epoch=None
  def get_dataloaders(s):
   a,b=super().get_dataloaders();return TimedIterator(a,s),TimedIterator(b,s)
  def train_step(s,batch):
   result=super().train_step(batch);s._train_batches+=1;return result
  def validation_step(s,batch):
   result=super().validation_step(batch);s._val_batches+=1;return result
  def load_checkpoint(s,filename_or_checkpoint):
   super().load_checkpoint(filename_or_checkpoint)
   need(s.current_epoch>=0 and s.optimizer is not None,'E136')
   need(s.current_epoch==0 or s.optimizer.state_dict()['state'],'E137')
   s._loaded_epoch=int(s.current_epoch)
  def on_epoch_start(s):
   import torch
   _synchronize_device(s.device);s._epoch_t=time.perf_counter();s._loader_wait=0.
   s._measured_epoch=int(s.current_epoch);s._train_batches=0;s._val_batches=0;super().on_epoch_start()
  def on_epoch_end(s):
   import torch
   super().on_epoch_end()
   _synchronize_device(s.device);elapsed=time.perf_counter()-s._epoch_t
   need(s._train_batches==250 and s._val_batches==50,'E138')
   rec={'epoch':s._measured_epoch,'elapsed':elapsed,K_LW:s._loader_wait,K_TI:s._train_batches,K_VI:s._val_batches}
   s.print_to_log_file('ITEM4_EPOCH '+canonical(rec).decode().strip(),add_timestamp=False)
   s._measurements.append(rec)
 return ReviewedTrainer
def _score_native(input_root,tr,arm,fold,splits,private_root):
 raw,pre=_prepared_paths(input_root,K_AR if arm=='A1_repeat2' else arm)
 plans=tr.plans_manager.plans
 need(plans['image_reader_writer']=='SimpleITKIO','E099')
 records=[];validation=Path(tr.output_folder)/K_V
 for case in splits[fold]['val']:
  segimg=nib.load(str(validation/f'{case}.nii.gz'));seg=np.asanyarray(segimg.dataobj)>.5
  with np.load(validation/f'{case}.npz',allow_pickle=False)as z:
   p=np.transpose(z['probabilities'][1].astype(np.float32),(2,1,0))
  need(p.shape==seg.shape and np.isfinite(p).all()and((p>=0)&(p<=1)).all(),'E124')
  need(dice(p>.5,seg)>=.99,'E125')
  cc=_fit_cache(pre,tr,case,private_root)
  pred=resample_from_to(nib.Nifti1Image(seg.astype(np.uint8),segimg.affine),(cc['shape'],cc['affine']),order=0).get_fdata()>.5
  prob=resample_from_to(nib.Nifti1Image(p,segimg.affine),(cc['shape'],cc['affine']),order=1).get_fdata().astype(np.float32)
  row=patient_scores(cc,prob[cc['mask']],pred)
  fp=int((pred& ~cc[K_LF] &cc['mask']).sum());tn=int((~pred& ~cc[K_LF] &cc['mask']).sum())
  row['specificity']=tn/(tn+fp)if tn+fp else None
  row.update(case=case,fold=fold,shuffle=101)
  need(all(math.isfinite(row[k])for k in('dice','lesion_f1','abs_vol_err_ml','signed_vol_err_ml')),'E126')
  records.append({k:(None if isinstance(v,(float,np.floating))and not math.isfinite(v)else v.item()if isinstance(v,np.generic)else v)for k,v in row.items()})
 need(len(records)==len(splits[fold]['val']),'E100')
 Path(private_root,'heldout-scores.json').write_bytes(canonical(records))
 metrics={}
 for k in('dice','lesion_f1','abs_vol_err_ml','signed_vol_err_ml','precision','recall','specificity','asd_mm','fm_auroc','fm_avg_precision','lesion_ml_outside_mask'):
  vals=[float(r[k])for r in records if r.get(k)is not None and math.isfinite(r[k])]
  metrics[k]={'n_defined':len(vals),'mean':sum(vals)/len(vals)if vals else None}
 return{'n_heldout':len(records),'fold':fold,'metrics':metrics,'exploratory':True,'uncertainty':'Per-fold means only; whole-cohort patient bootstrap requires all five frozen folds. No training variance estimate.'}
def _fit_payload(pre,tr,case):
 import pickle
 folder=pre/tr.configuration_manager.data_identifier
 with(folder/(case+'.pkl')).open('rb')as f:return _private_scoring(pickle.load(f))
def _fit_cache(pre,tr,case,private_root):
 payload=_fit_payload(pre,tr,case);p=Path(private_root)/'scoring'/f'{case}.npz'
 if p.exists():need(file_info(p)==payload['cache_info'],'E127')
 else:write_once(private_root,p.relative_to(private_root).as_posix(),payload['cache_bytes'])
 return load_cache(str(p),config_hash(FEATURE_CFG),case)
def _fit_truth(pre,tr,cases,work):
 base=Path(work)/'native-inputs';base.mkdir(exist_ok=True)
 raw=(pre/K_DJ).read_bytes();meta=json.loads(raw)
 fingerprint=meta['item4_fingerprint']
 need(isinstance(fingerprint,dict)and fingerprint,'E101')
 for name,b in[(K_DJ,raw),(K_SFJ,(pre/K_SFJ).read_bytes()),(K_DFJ,canonical(fingerprint))]:
  p=base/name
  if p.exists():need(p.read_bytes()==b,'E139')
  else:write_once(base,name,b)
 tr.preprocessed_dataset_folder_base=str(base)
 folder=base/'gt_segmentations';folder.mkdir(exist_ok=True)
 for case in cases:
  b=_fit_payload(pre,tr,case)['truth_nifti'];p=folder/f'{case}.nii.gz'
  if p.exists():need(p.read_bytes()==b,'E140')
  else:write_once(base,p.relative_to(base).as_posix(),b)
 tr.gt_segmentations_folder=str(folder)
def fit_resources(rt,fit):
 r=rt.get(K_R)
 need(isinstance(r,dict)and set(r)=={'gpu','cpu',K_MM,K_TS},'E102')
 need(all(type(r[k])is int for k in('cpu',K_MM,K_TS)),'E103')
 need(r['cpu']==16 and r[K_MM]==131072 and 1<=r[K_TS]<=86400,'E104')
 need(r['gpu']in('A100-80GB','H100','B200'),'E105')
 if fit['fit_id'].startswith('benchmark-'):
  need(r['gpu']==fit['fit_id'].removeprefix('benchmark-'),'E128')
 return r['gpu']
def _execute_fit(input_root,output_root,contract,config=None,mon=None):
 plan,rt,sel=bound_plan(contract);environment_check(plan[K_ER]);_load_science()
 fit=next(x for x in plan['fits']if x['fit_id']==rt[K_E]['fit_id'])
 progress=DiagnosticProgress(contract['progress'],mon)if config else contract['progress'];work=Path(progress.root).resolve()/'work';work.mkdir(exist_ok=True)
 out=Path(output_root).resolve();out.mkdir(parents=True,exist_ok=True)
 need(not list(out.iterdir())and not work.is_relative_to(out)and not out.is_relative_to(work),'E106')
 segment=rt[K_E]['segment'];need(type(segment)is int and segment>=1,'E107')
 need((segment==1 and not rt.get('resume'))or(segment>1 and rt.get('resume')),'E108')
 arm=K_AR if fit['arm']=='A1_repeat2' else fit['arm']
 need(arm not in(K_AZ,K_AH),'U3 coverage held')
 raw,pre=_prepared_paths(input_root,arm)
 meta=json.loads((pre/K_DJ).read_bytes())['item4']
 fit_binding=rt['progress']['fit_binding']
 need(meta[K_PI]==fit[K_PI]and meta[K_ICS]==sel[K_ICS],'E109')
 meta=dict(meta,plans_sha256=file_info(pre/(sel[K_PN]+'.json'))['sha256'])
 need(meta[K_PS]==fit_binding[K_PS],'E110')
 split_bytes=(pre/K_SFJ).read_bytes();need(sha_bytes(split_bytes)==sel[K_SS],'E111')
 splits=json.loads(split_bytes)
 _native_paths(Path(input_root)/'raw',Path(input_root)/'preprocessed',work/'native-results')
 import torch
 need(torch.cuda.is_available(),'E112')
 tr=(diagnostic_trainer_class(config,mon)if config else _trainer_class())(dict(json.loads((pre/(sel[K_PN]+'.json')).read_bytes()),continue_training=segment>1),K_3F,fit['fold'],json.loads((pre/K_DJ).read_bytes()),device=torch.device('cuda',0))
 Path(tr.output_folder).mkdir(parents=True,exist_ok=True)
 tr.log_file=str(work/f'training_log_{segment}.txt')
 Path(tr.log_file).touch(mode=0o600,exist_ok=False)
 tr.num_epochs=config['epochs']if config else(1 if fit['fit_id'].startswith('benchmark-')else 5 if fit['stage']=='SMOKE' else 250)
 need(tr.num_iterations_per_epoch==250 and tr.num_val_iterations_per_epoch==50,'E113')
 expected_gpu=config['gpu']if config else fit_resources(rt,fit)
 name=torch.cuda.get_device_name(0)
 need(expected_gpu.split('-')[0]in name and(expected_gpu!='A100-80GB' or torch.cuda.get_device_properties(0).total_memory>=79*1024**3),'E114')
 _fit_truth(pre,tr,splits[fit['fold']]['val'],work)
 from orchestrator.modal_nnunet import run_fit
 native_start=time.perf_counter()
 native_receipt=run_fit(tr,progress,initial=(segment==1),save_every=config['save_every']if config else(1 if fit['stage']=='SMOKE' else 10),segment=segment,interruption=rt.get('resume'))
 if config:mon.native_seconds=time.perf_counter()-native_start
 need(tr.current_epoch==tr.num_epochs,'E115')
 final_path,final_record=progress.select('final')
 need(file_info(final_path)['sha256']==native_receipt['final_sha256']==final_record['sha256'],'E116')
 need(final_record['metadata'][K_NE]==tr.num_epochs,'E117')
 losses=[tr.logger.get_value('train_losses',step=i)for i in range(tr.num_epochs)]
 need(len(losses)>=tr.num_epochs and all(math.isfinite(float(x))for x in losses),'E118')
 measured={}
 for log_path in sorted(work.glob('training_log_*.txt')):
  need(not log_path.is_symlink(),'E129')
  for line in log_path.read_text().splitlines():
   if line.startswith('ITEM4_EPOCH '):
    rec=json.loads(line.removeprefix('ITEM4_EPOCH '));epoch=rec['epoch']
    need(epoch not in measured,'E141')
    measured[epoch]=rec
 need(set(measured)==set(range(tr.num_epochs)),'E119')
 tr._measurements=[measured[k]for k in sorted(measured)]
 need(all(r[K_TI]==250 and r[K_VI]==50 for r in tr._measurements),'E120')
 comparable=plan['full_training']['benchmark_comparability_id']if fit['fit_id'].startswith('benchmark-')else 'same-arm-selected-gpu-full99-fold0-v1'
 timing=diagnostic_timing(fit,tr._measurements)if config else timing_record(fit['fit_id'],tr._measurements,comparable)
 timing.update(total_native_epochs=int(tr.current_epoch),gpu=expected_gpu,physical_cpus=rt[K_R]['cpu'],memory_gib=rt[K_R][K_MM]/1024,segment=segment)
 if 'native-resume' in fit[K_VC]:
  need(segment>1 and tr._loaded_epoch is not None and 0<tr._loaded_epoch<tr.num_epochs,'E130')
 scoring_start=time.perf_counter()
 summary=_score_native(input_root,tr,fit['arm'],fit['fold'],splits,work)
 if config:mon.scoring_seconds=time.perf_counter()-scoring_start
 summary.update(run_id=RUN_ID,preprocessing_id=fit[K_PI],input_contract_sha256=sel[K_ICS],source_capture_sha256=sel[K_SCS],environment_sha256=fit_binding[K_ES],aggregate_output_only=True,fit_id=fit['fit_id'],native_epochs=int(tr.current_epoch),finite_loss_count=len(losses),plans_sha256=meta[K_PS],split_sha256=sel[K_SS],loaded_native_epoch=tr._loaded_epoch)
 files={}
 if config:
  mon.close()
  cpu_end=cpu_capacity();need(cpu_end==mon.cpu_start,'E131')
  completeness=mon.completeness()
  report={'schema':'cpu-starvation-diagnostic/v1','fit_id':fit['fit_id'],'configuration':config,'requested_resources':rt[K_R],'observed_cpu_start':mon.cpu_start,'observed_cpu_end':cpu_end,'workers':tr._diagnostic_workers,'gpu_samples':mon.samples,'sampling':completeness,'checkpoint_events':mon.events,K_S:timing[K_S],K_MWS:mon.ended-mon.started,'epoch_wall_seconds':sum(r['wall_seconds']for r in tr._measurements),'native_run_seconds':mon.native_seconds,'scoring_seconds':mon.scoring_seconds,'cost_status':'PENDING_CONTROLLER_WHOLE_JOB_BILLING','cost_micro_usd':None,'whole_job_seconds':None,'limits':['Module duration excludes provider startup, wrapper final publication and teardown. Reconcile whole-job receipt and genuine GPU+CPU+RAM rates with diagnostic_cost before accepting cost comparison.','No full-plan projection or efficacy. Stochastic worker streams differ with worker count; matching master seed is not bitwise replay.']}
  report['outside_epoch_module_seconds']=report[K_MWS]-report['epoch_wall_seconds']
  progress.receipt('cpu-diagnostic-telemetry',report)
  need(completeness['status']=='PASS','E132')
  files[K_CDJ]=write_once(out,K_CDJ,canonical(report))
 for rel,obj in[(K_MJ,summary),('epoch-timing.json',timing)]:
  b=canonical(obj);need(len(b)<=1500000,'E133');files[rel]=write_once(out,rel,b)
 evidence={'input-bindings':[K_MJ],'native-training':[K_MJ],'finite-loss':[K_MJ],'epoch-timing':['epoch-timing.json'],'heldout-scoring':[K_MJ],'private-output-boundary':[K_MJ],'benchmark-comparability':['epoch-timing.json'],'native-resume':[K_MJ]}
 if config:evidence['cpu-diagnostic']=[K_CDJ]
 need(set(fit[K_VC])<=set(evidence)and len(fit[K_VC])==len(set(fit[K_VC])),'E121')
 need(set(fit['outputs'])==set(files)|{'validation.json'},'E122')
 validation={'schema':'experiment-validation/v1',**{k:rt[k]for k in('run_id','spec_sha256','code_sha256',K_EPS)},'fit_id':rt[K_E]['fit_id'],'files':files,'checks':[{'id':k,'status':'PASS','evidence':evidence[k]}for k in fit[K_VC]]}
 write_once(out,'validation.json',canonical(validation))
 need({p.name for p in out.iterdir()}==set(fit['outputs']),'extra output')
 return None
def aggregate_screen(tables,held):
 _load_science()
 required=set(CANDIDATES)|{K_ACMC,K_AR,'A1_repeat2','A1_pnorm_v2'}
 need(set(tables)==required,'E123')
 for table in tables.values():validate_full_folds(table,held)
 def contrast(a,b):
  x=tables[a][['case','fold','shuffle','dice']].merge(tables[b][['case','fold','shuffle','dice']],on=['case','fold','shuffle'],how='outer',validate='one_to_one',suffixes=('_a','_b')).sort_values(['fold','case'])
  need(len(x)==99 and not x.isna().any().any(),'E134')
  d=(x.dice_a-x.dice_b).to_numpy(float);need(np.isfinite(d).all(),'E135')
  rng=np.random.default_rng(int(hashlib.sha256(('item4|'+a+'|'+b).encode()).hexdigest()[:8],16))
  means=d[rng.integers(0,99,size=(10000,99))].mean(axis=1)
  lo,hi=np.percentile(means,[.5,99.5])
  return[float(d.mean()),float(lo),float(hi)]
 results={}
 for a in CANDIDATES:
  vsbase=contrast(a,K_ACMC);vsrepeat=contrast(a,K_AR)
  results[a]={'candidate_minus_original':vsbase,'candidate_minus_repeat1':vsrepeat,'verdict':verdict_from_intervals(vsbase,vsrepeat),'repeat2_sensitivity':contrast(a,'A1_repeat2')}
 return{'family_size':5,'confidence_level':99.,'bootstrap_draws':10000,'primary':results,'noise_controls':{'repeat1_minus_original':contrast(K_AR,K_ACMC),'repeat2_minus_original':contrast('A1_repeat2',K_ACMC),'repeat2_minus_repeat1':contrast('A1_repeat2',K_AR)},'secondary_ct_increment':contrast(K_AP,'A1_pnorm_v2'),'limitations':'Exposed development cohort; intervals conditional on fitted models; shared training, model selection and unseeded training uncertainty omitted. Noise controls are not variance estimates. Secondary and repeat2 sensitivity intervals are exploratory.'}
def _boundary_tests():
 class PreservedBoundaryTests(unittest.TestCase):
  def test_partition_completeness_and_leakage(s):
   members=[f'synthetic-{i}' for i in range(99)]
   parts={f'101_{k}':{'train':[x for i,x in enumerate(members)if i%5!=k],'held':[x for i,x in enumerate(members)if i%5==k]}for k in range(5)}
   s.assertEqual(len(split_document(parts)),5)
   parts['101_0']['train'].append(parts['101_0']['held'][0])
   with s.assertRaises(PrerequisiteError):split_document(parts)
  def test_committed_preprocessing_reuse_and_tamper(s):
   with tempfile.TemporaryDirectory()as d:
    info=write_once(d,K_ST,b'synthetic')
    complete={'shared':{K_ST:info}}
    s.assertEqual(verify_completed(d,complete),{K_ST:info})
    Path(d,K_ST).write_bytes(b'changed')
    with s.assertRaises(PrerequisiteError):verify_completed(d,complete)
  def test_paths_and_existing_outputs_refuse(s):
   with tempfile.TemporaryDirectory()as d:
    for p in('../escape','/absolute'):
     with s.assertRaises(PrerequisiteError):rooted(d,p)
    write_once(d,'one',b'synthetic')
    with s.assertRaises(FileExistsError):write_once(d,'one',b'rewrite')
  def test_coverage_and_unmeasured_timing_remain_held(s):
   with s.assertRaises(PrerequisiteError):derived_ctp_support(None,None)
   with s.assertRaises(PrerequisiteError):timing_record('synthetic',[],'synthetic')
  def test_conjunctive_verdict(s):
   s.assertEqual(verdict_from_intervals([.1,.01,.2],[.2,.1,.3]),'better')
   s.assertEqual(verdict_from_intervals([.1,.01,.2],[-.1,-.2,.1]),'no clear difference')
   s.assertEqual(verdict_from_intervals([.1,.01,.2],[.2,.1,.3],False),'provisional')
 return unittest.defaultTestLoader.loadTestsFromTestCase(PreservedBoundaryTests)

DIAGNOSTIC_IDS=('smoke-cpu-A16','smoke-cpu-B32')
DIAGNOSTIC_IMAGE='im-Yhslx2XCmdhO6U5ToJJi0C'
def diagnostic_selection(fit,rt):
 if fit['fit_id']not in DIAGNOSTIC_IDS:return None
 i=DIAGNOSTIC_IDS.index(fit['fit_id']);cpu=(16,32)[i];workers=(12,24)[i]
 need(fit['stage']=='SMOKE' and fit['arm']==K_AR and type(fit['fold'])is int and fit['fold']==0 and fit[K_PI]=='prep-A1_repeat','E142')
 r=rt[K_R]
 need(set(r)=={'gpu','cpu',K_MM,K_TS}and r=={'gpu':'B200','cpu':cpu,K_MM:131072,K_TS:2400},'E143')
 need(all(type(r[k])is int for k in('cpu',K_MM,K_TS)),'E144')
 need(rt[K_E]['segment']==1 and not rt.get('resume'),'E145')
 return{'cpu':cpu,'workers':workers,K_VW:workers//2,'epochs':15,'seed':101,K_LH:250,'save_every':10,'memory_gib':128,'gpu':'B200',K_TS:2400,K_MSS:2100}
def cpu_capacity():
 count=os.cpu_count();affinity=len(os.sched_getaffinity(0))
 quota=None;source=None
 p=Path('/sys/fs/cgroup/cpu.max')
 if p.is_file():
  q,period=p.read_text().split();quota=None if q=='max' else int(q)/int(period);source='cgroup-v2'
 else:
  p=Path('/sys/fs/cgroup/cpu/cpu.cfs_quota_us');q=Path('/sys/fs/cgroup/cpu/cpu.cfs_period_us')
  if p.is_file()and q.is_file():
   a=int(p.read_text());quota=None if a<0 else a/int(q.read_text());source='cgroup-v1'
 need(source is not None and count is not None and affinity>0,'E146')
 return{'logical_cpu_count':count,'affinity_logical_cpus':affinity,'quota_cpu_equivalents':quota,'quota_source':source,'effective_logical_capacity':min(affinity,quota)if quota is not None else affinity}
def gpu_sample():
 import subprocess
 result=subprocess.run(['nvidia-smi','--id=0','--query-gpu=utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=2,check=True)
 value=float(result.stdout.strip());need(math.isfinite(value)and 0<=value<=100,'E147')
 return value
class DiagnosticMonitor:
 def __init__(s,config,probe=gpu_sample,clock=time.perf_counter,wall=time.time):
  import threading
  s.config=config;s.probe=probe;s.clock=clock;s.wall=wall;s.samples=[];s.errors=[];s.events=[];s.stop_event=threading.Event();s.started=clock();s.ended=None;s.thread=None
 def sample(s):
  t=s.clock()
  try:s.samples.append({'monotonic_seconds':t-s.started,'unix_seconds':s.wall(),'gpu_utilization_percent':s.probe()})
  except Exception:s.errors.append('gpu-sample-unavailable')
 def start(s):
  import threading
  s.sample();need(not s.errors,'E160')
  def loop():
   while not s.stop_event.wait(1):
    if s.clock()-s.started>=s.config[K_MSS]:
     s.errors.append('diagnostic-time-limit');return
    s.sample()
  s.thread=threading.Thread(target=loop,daemon=True);s.thread.start()
 def guard(s):
  need(not s.errors and s.clock()-s.started<s.config[K_MSS],'E161')
 def close(s):
  s.stop_event.set()
  if s.thread is not None:s.thread.join(timeout=3)
  s.sample();s.ended=s.clock()
 def completeness(s):
  elapsed=(s.ended or s.clock())-s.started
  ts=[x['monotonic_seconds']for x in s.samples];gaps=[b-a for a,b in zip([0]+ts,ts+[elapsed])]
  expected=max(1,int(elapsed)+1)
  valid=not s.errors and len(ts)>=.9*expected and max(gaps,default=elapsed)<=3 and all(g>=0 for g in gaps)
  return{'status':'PASS' if valid else 'FAIL','period_seconds':1,'expected_samples':expected,'actual_samples':len(ts),'fraction':min(1,len(ts)/expected),'max_gap_seconds':max(gaps,default=elapsed),'errors':s.errors}
class DiagnosticProgress:
 def __init__(s,inner,mon):s.inner=inner;s.mon=mon
 def __getattr__(s,key):return getattr(s.inner,key)
 def publish(s,key,write,*,metadata):
  m=s.mon;t=m.clock();write_seconds=[]
  def measured(path):
   start=m.clock()
   try:return write(path)
   finally:write_seconds.append(m.clock()-start)
  try:return s.inner.publish(key,measured,metadata=metadata)
  finally:
   total=m.clock()-t;native=sum(write_seconds)
   m.events.append({'kind':key,K_NE:metadata.get(K_NE),'monotonic_start':t-m.started,'total_seconds':total,K_NWS:native,K_DOS:max(0,total-native)})
 def receipt(s,*args,**kwargs):
  t=s.mon.clock()
  try:return s.inner.receipt(*args,**kwargs)
  finally:s.mon.events.append({'kind':'receipt','total_seconds':s.mon.clock()-t})
 def training_log(s,*args,**kwargs):
  t=s.mon.clock()
  try:return s.inner.training_log(*args,**kwargs)
  finally:s.mon.events.append({'kind':'training-log-publication','total_seconds':s.mon.clock()-t})
def observed_workers(iterator):
 inner=getattr(iterator,'inner',iterator);configured=getattr(inner,'num_processes',None);processes=getattr(inner,'_processes',None)
 need(type(configured)is int and isinstance(processes,(list,tuple))and len(processes)==configured,'E148')
 live=sum(bool(p.is_alive())for p in processes)
 need(live==configured,'E149')
 return{'configured':configured,'observed_live':live}
def diagnostic_trainer_class(config,mon):
 import torch
 Base=_trainer_class()
 class DiagnosticTrainer(Base):
  def configure_optimizers(s):
   n=s.num_epochs;s.num_epochs=config[K_LH]
   try:return super().configure_optimizers()
   finally:s.num_epochs=n
  def get_dataloaders(s):
   a,b=super().get_dataloaders();s._diagnostic_workers={'training':observed_workers(a),K_V:observed_workers(b)}
   need(s._diagnostic_workers['training']['configured']==config['workers']and s._diagnostic_workers[K_V]['configured']==config[K_VW],'E164')
   return a,b
  def train_step(s,batch):mon.guard();return super().train_step(batch)
  def validation_step(s,batch):mon.guard();return super().validation_step(batch)
  def on_epoch_start(s):
   mon.guard();s._diag_wall=time.time();s._diag_start=time.perf_counter();s._diag_event_start=len(mon.events)
   super().on_epoch_start()
  def on_epoch_end(s):
   mon.guard();_synchronize_device(s.device);core=time.perf_counter()-s._epoch_t
   super(Base,s).on_epoch_end();_synchronize_device(s.device)
   elapsed=time.perf_counter()-s._epoch_t
   native=s.logger.get_value('epoch_end_timestamps',step=-1)-s.logger.get_value('epoch_start_timestamps',step=-1)
   need(s._train_batches==250 and s._val_batches==50,'E165')
   events=mon.events[s._diag_event_start:]
   rec={'epoch':s._measured_epoch,'elapsed':elapsed,'core_synchronized_seconds':core,'native_seconds':native,'wall_seconds':time.perf_counter()-s._diag_start,'unix_start':s._diag_wall,'unix_end':time.time(),K_LW:s._loader_wait,K_TI:s._train_batches,K_VI:s._val_batches,'checkpoint_seconds':sum(e['total_seconds']for e in events if K_NWS in e),'checkpoint_write_seconds':sum(e.get(K_NWS,0)for e in events),'durable_publication_seconds':sum(e.get(K_DOS,0)for e in events)}
   rec['other_epoch_end_seconds']=elapsed-core-rec['checkpoint_seconds']
   s.print_to_log_file('ITEM4_EPOCH '+canonical(rec).decode().strip(),add_timestamp=False);s._measurements.append(rec)
 return DiagnosticTrainer
def diagnostic_stability(records):
 need(len(records)==15 and[r['epoch']for r in records]==list(range(15)),'E150')
 values=[r['elapsed']for r in records]
 need(all(type(x)in(int,float)and math.isfinite(x)and x>0 for x in values),'E151')
 a=values[5:10];b=values[10:15];mean=lambda v:sum(v)/len(v)
 change=abs(mean(a)-mean(b))/mean(a)
 slope=(sum((i-2)*v for i,v in enumerate(b))/10)/mean(b)
 stable=change<=.10 and abs(slope)<=.02
 return{'warmup_epochs':[0,1,2,3,4],'comparison_epochs':[5,6,7,8,9],'tail_epochs':[10,11,12,13,14],'comparison_mean_seconds':mean(a),'tail_mean_seconds':mean(b),'relative_window_change':change,'tail_relative_slope_per_epoch':slope,K_WSD:stable,K_SSSPE:mean(b)if stable else None,'limitation':'Window-specific operational stability only; fifteen epochs and changing best-save frequency cannot establish an asymptotic plateau.'}
def diagnostic_timing(fit,records):
 stability=diagnostic_stability(records)
 elapsed=sum(r['elapsed']for r in records);wait=sum(r[K_LW]for r in records)
 need(all(r[K_TI]==250 and r[K_VI]==50 and math.isfinite(r[K_LW])and 0<=r[K_LW]<=r['elapsed']for r in records),'E152')
 return{'schema':'experiment-epoch-timing/v1','fit_id':fit['fit_id'],'completed_epochs':15,'elapsed_training_seconds':elapsed,'real_epoch':True,K_LNB:wait/elapsed<=.10,'comparability_id':'cpu-starvation-base-fold0-v1','measured_loader_wait_seconds':wait,'epoch_records':records,K_S:stability}
def diagnostic_cost(report,rates,billed_seconds,overhead_micro_usd):
 from decimal import Decimal,ROUND_CEILING
 need(set(rates)=={'gpu_hour_cost_b200','cpu_hour_cost_sandbox','mem_gib_hour_cost_sandbox'},'E153')
 rr={k:Decimal(str(v))for k,v in rates.items()}
 need(all(v.is_finite()and v>0 for v in rr.values()),'E154')
 need(type(billed_seconds)in(int,float)and math.isfinite(billed_seconds)and billed_seconds>=report[K_MWS],'E155')
 need(type(overhead_micro_usd)is int and overhead_micro_usd>=0,'E156')
 c=report['configuration'];hourly=rr['gpu_hour_cost_b200']+c['cpu']*rr['cpu_hour_cost_sandbox']+c['memory_gib']*rr['mem_gib_hour_cost_sandbox']
 cost=int((hourly*Decimal(str(billed_seconds))/3600*1000000).to_integral_value(rounding=ROUND_CEILING))+overhead_micro_usd
 return{'resource_rates':rates,'billed_seconds':billed_seconds,'whole_job_micro_usd':cost,'amortized_micro_usd_per_epoch':cost/15,'outside_module_seconds':billed_seconds-report[K_MWS],'steady_state_resource_micro_usd_per_epoch':None if report[K_S][K_SSSPE]is None else float(hourly)*report[K_S][K_SSSPE]/3600*1000000,'limitations':'Includes supplied whole-job overhead. Not a full-plan admission projection; all-arm timings still missing.'}
def diagnostic_admission_order(quotes,spent,open_reservations,stage_spent,stage_reserved,total_spent,total_reserved):
 values=[spent,open_reservations,stage_spent,stage_reserved,total_spent,total_reserved,*quotes.values()]
 need(set(quotes)==set(DIAGNOSTIC_IDS)and all(type(v)is int and v>=0 for v in values),'E157')
 room=min(25000000-spent-open_reservations,150000000-stage_spent-stage_reserved,1275000000-total_spent-total_reserved)
 need(room>=0,'E158')
 a,b=DIAGNOSTIC_IDS
 if quotes[a]+quotes[b]<=room:return[a,b]
 return[b]if quotes[b]<=room else[]
def synthetic_tests():
 from unittest.mock import patch,Mock
 import types,sys
 class Checks(unittest.TestCase):
  def fit(s,i=0):return dict(fit_id=DIAGNOSTIC_IDS[i],stage='SMOKE',arm=K_AR,fold=0,preprocessing_id='prep-A1_repeat')
  def rt(s,i=0):return dict(resources=dict(gpu='B200',cpu=(16,32)[i],memory_mib=131072,timeout_seconds=2400),experiment=dict(segment=1))
  def rows(s):return[dict(epoch=i,elapsed=100.,loader_wait=20.,training_iterations=250,validation_iterations=50)for i in range(15)]
  def test_resources(s):
   for i in(0,1):
    f=s.fit(i);r=s.rt(i);cfg=diagnostic_selection(f,r)
    s.assertEqual((cfg['workers'],cfg[K_LH]),(12*(i+1),250))
    for k,v in[('gpu','H100'),('cpu',True),(K_MM,65536),(K_TS,2401)]:
     bad=copy.deepcopy(r);bad[K_R][k]=v;_must_refuse(lambda:diagnostic_selection(f,bad))
    r[K_E]['segment']=2;r['resume']={};_must_refuse(lambda:diagnostic_selection(f,r))
  def test_timing(s):
   r=s.rows();t=diagnostic_timing(s.fit(),r);s.assertFalse(t[K_LNB]);s.assertTrue(t[K_S][K_WSD])
   for i,v in enumerate(r):v['elapsed']=200-8*i
   s.assertFalse(diagnostic_stability(r)[K_WSD]);_must_refuse(lambda:diagnostic_stability(r[:-1]))
  def test_sampling(s):
   m=DiagnosticMonitor({},clock=lambda:0);m.samples=[dict(monotonic_seconds=i)for i in range(11)];m.ended=10
   s.assertEqual(m.completeness()['status'],'PASS');m.samples=m.samples[:2];s.assertEqual(m.completeness()['status'],'FAIL')
   m.probe=Mock(side_effect=RuntimeError());m.sample();s.assertTrue(m.errors)
  def test_publication(s):
   ticks=iter([0.,1.,3.,7.]);m=types.SimpleNamespace(clock=lambda:next(ticks),started=0.,events=[])
   class P:
    locked=True
    def publish(s,key,write,*,metadata):write('fixture');return 'ok'
   p=DiagnosticProgress(P(),m);s.assertEqual(p.publish('latest',lambda _:None,metadata={K_NE:10}),'ok')
   s.assertEqual((m.events[0][K_NWS],m.events[0][K_DOS]),(2,5));s.assertTrue(p.locked)
  def test_workers(s):
   live=types.SimpleNamespace(is_alive=lambda:True);it=types.SimpleNamespace(num_processes=2,_processes=[live,live]);s.assertEqual(observed_workers(it)['observed_live'],2)
   _must_refuse(lambda:observed_workers(types.SimpleNamespace(num_processes=2)))
   it._processes=[types.SimpleNamespace(is_alive=lambda:False),live];_must_refuse(lambda:observed_workers(it))
  def test_budget(s):
   for quote,amounts,want in[(13,(0,0,0,0,0,0),[DIAGNOSTIC_IDS[1]]),(13,(0,13000000,0,0,0,0),[]),(10,(0,0,0,0,0,0),list(DIAGNOSTIC_IDS)),(10,(0,0,149000000,0,0,0),[]),(10,(0,0,0,0,1274999999,0),[])]:
    s.assertEqual(diagnostic_admission_order(dict.fromkeys(DIAGNOSTIC_IDS,quote*1000000),*amounts),want)
  def test_cost(s):
   r=dict(configuration=dict(cpu=32,memory_gib=128),module_wall_seconds=100,stability=dict(steady_state_seconds_per_epoch=None));rates=dict(gpu_hour_cost_b200='6',cpu_hour_cost_sandbox='.1',mem_gib_hour_cost_sandbox='.01')
   c=diagnostic_cost(r,rates,3600,1000000);s.assertEqual(c['whole_job_micro_usd'],11480000);s.assertIsNone(c['steady_state_resource_micro_usd_per_epoch']);_must_refuse(lambda:diagnostic_cost(r,rates,99,0))
  def test_routes(s):
   
   seed=Mock();np=types.SimpleNamespace(random=types.SimpleNamespace(seed=seed));torch=types.SimpleNamespace(manual_seed=seed,cuda=types.SimpleNamespace(manual_seed_all=seed))
   for i in(0,1):
    ctx=dict(execution_plan=dict(fits=[s.fit(i)],environment_requirements={}),runtime=dict(s.rt(i),experiment=dict(fit_id=DIAGNOSTIC_IDS[i],segment=1)),progress=Mock());mon=Mock();mon.ended=1
    def execute(a,b,c,config,observer):
     s.assertIs(c,ctx);s.assertIs(observer,mon);s.assertEqual(os.environ[K_NNPD],str((12,24)[i]));s.assertEqual(tuple(config[k]for k in('epochs',K_LH,'save_every')),(15,250,10))
    with patch.dict(sys.modules,dict(numpy=np,torch=torch)),patch.dict(os.environ,nnUNet_n_proc_DA='7'),patch.dict(globals(),dict(bound_plan=lambda c:None,environment_check=lambda r:None,cpu_capacity=lambda:dict(effective_logical_capacity=32),DiagnosticMonitor=lambda c:mon,_execute_fit=execute)):
     main('fixture','fixture',ctx);s.assertEqual(os.environ[K_NNPD],'7');mon.start.assert_called_once()
     with patch.dict(globals(),_execute_fit=Mock(side_effect=PrerequisiteError())):_must_refuse(lambda:main('fixture','fixture',ctx))
     s.assertFalse(ctx['progress'].receipt.call_args.args[1]['valid']);s.assertEqual(os.environ[K_NNPD],'7')
  def test_intervals(s):
   s.assertEqual(verdict_from_intervals([-.2,-.3,-.1],[-.3,-.4,-.2]),'worse')
   for ci in([0,1,-1],[0,float('nan'),1],[0,1],[[0],[1],[2]],'123'):_must_refuse(lambda:verdict_from_intervals(ci,[0,-1,1]),ValueError)
  def test_stop(s):
   m=DiagnosticMonitor({K_MSS:2100},clock=lambda:0);m.clock=lambda:2100;_must_refuse(m.guard)
  def test_fixture_io(s):
   import ast,inspect,threading
   m=Mock(DiagnosticMonitor=DiagnosticMonitor);d=globals()|locals()
   n=next(x for x in ast.walk(ast.parse(inspect.getsource(_native_diagnostic_fixture)))if type(x)is ast.ClassDef);exec(ast.unparse(n),d)
   o=d['C']({K_MSS:2},probe=Mock(side_effect=ValueError))
   o.start();o.close();s.assertTrue(not o.thread.is_alive()and o.completeness()['status']=='FAIL')
   s.assertRaises(AttributeError,lambda:threading.Thread(target=o._sampling_loop))
 return unittest.TestSuite([_boundary_tests(),unittest.defaultTestLoader.loadTestsFromTestCase(Checks)])

def main(input_root,output_root,contract):
 fit=next(x for x in contract[K_EP]['fits']if x['fit_id']==contract['runtime'][K_E]['fit_id'])
 config=diagnostic_selection(fit,contract['runtime'])
 if config is None:return _execute_fit(input_root,output_root,contract)
 bound_plan(contract);environment_check(contract[K_EP][K_ER])
 import random,numpy as np,torch
 random.seed(config['seed']);np.random.seed(config['seed']);torch.manual_seed(config['seed']);torch.cuda.manual_seed_all(config['seed'])
 previous=os.environ.get(K_NNPD);os.environ[K_NNPD]=str(config['workers'])
 mon=DiagnosticMonitor(config)
 try:
  mon.cpu_start=cpu_capacity()
  need(mon.cpu_start['effective_logical_capacity']>=config['cpu'],'E162')
  mon.start()
  return _execute_fit(input_root,output_root,contract,config,mon)
 except BaseException as error:
  contract['progress'].receipt('cpu-diagnostic-failed',{'fit_id':fit['fit_id'],'error_type':type(error).__name__,'valid':False,'retry_permitted':False,'sampling':mon.completeness()})
  raise
 finally:
  if mon.ended is None:mon.close()
  if previous is None:os.environ.pop(K_NNPD,None)
  else:os.environ[K_NNPD]=previous

def _synchronize_device(device):
 import torch
 if device.type=='cuda':torch.cuda.synchronize(device)
 else:need(device.type=='cpu','E163')

def _synthetic_plans():
 """Generated reduced fixture, never a production plan."""
 arch={'n_stages':3,'features_per_stage':[2,4,8],'conv_op':'torch.nn.modules.conv.Conv3d','kernel_sizes':[[3]*3]*3,'strides':[[1]*3,[2]*3,[2]*3],'n_blocks_per_stage':[1]*3,'n_conv_per_stage_decoder':[1]*2,'conv_bias':True,'norm_op':'torch.nn.modules.instancenorm.InstanceNorm3d','norm_op_kwargs':{'eps':1e-5,'affine':True},'dropout_op':None,'dropout_op_kwargs':None,'nonlin':'torch.nn.LeakyReLU','nonlin_kwargs':{'inplace':True}}
 cfg={'data_identifier':'nnUNetPlans_3d_fullres','preprocessor_name':'DefaultPreprocessor','batch_size':2,'patch_size':[8]*3,'median_image_size_in_voxels':[16]*3,'spacing':[5.]*3,K_NS:[K_N]*6,'use_mask_for_norm':[False]*6,'batch_dice':False,'architecture':{'network_class_name':'dynamic_network_architectures.architectures.unet.ResidualEncoderUNet','arch_kwargs':arch,'_kw_requires_import':['conv_op','norm_op','dropout_op','nonlin']}}
 for kind,seg,order in[('data',False,3),('seg',True,1),('probabilities',False,1)]:
  cfg['resampling_fn_'+kind]='resample_data_or_seg_to_shape'
  cfg['resampling_fn_'+kind+'_kwargs']={'is_seg':seg,'order':order,'order_z':0,'force_separate_z':None}
 return{'dataset_name':_dataset_name(K_AR),K_PN:'SyntheticPlans','original_median_spacing_after_transp':[5.]*3,'original_median_shape_after_transp':[16]*3,'image_reader_writer':'SimpleITKIO','transpose_forward':[0,1,2],'transpose_backward':[0,1,2],K_C:{K_3F:cfg},'experiment_planner_used':'nnUNetPlannerResEncM','label_manager':'LabelManager',K_FIPPC:{}}

def _must_refuse(call,error=PrerequisiteError):
 try:call()
 except error:return
 raise AssertionError('expected refusal')

def _finish_loaders(tr):
 for key in('dataloader_train','dataloader_val'):
  loader=getattr(tr,key,None);inner=getattr(loader,'inner',loader)
  if hasattr(inner,'_finish'):inner._finish()

def native_synthetic_integration(progress_factory):
 """Author-owned CPU fixture; execution and acceptance remain controller-held."""
 import importlib.util,sys,torch
 from importlib.metadata import version
 from orchestrator.modal_fit_progress import FitProgress
 from orchestrator.modal_nnunet import run_fit
 from orchestrator.modal_preprocessed_contract import validate_preprocessed,validate_validation
 from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
 
 spec=importlib.util.spec_from_file_location('synthetic_item4',__file__)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m._load_science();n=m.np
 need(not torch.cuda.is_available(),'E159')
 old=dict(os.environ);threads=torch.get_num_threads()
 with tempfile.TemporaryDirectory(prefix='item4-native-synthetic-')as td:
  root=Path(td);inp=root/'inputs';prep=root/'prepared';inp.mkdir();prep.mkdir()
  try:
   os.environ.update(nnUNet_compile='false',nnUNet_n_proc_DA='0');torch.set_num_threads(1)
   cases=[f'synthetic-{i:03d}' for i in range(99)]
   parts={f'101_{k}':{'held':cases[k::5],'train':[c for c in cases if c not in cases[k::5]]}for k in range(5)}
   splits=m.split_document(parts);part=root/'partitions.json';part.write_bytes(m.canonical(parts));cohort=m.canonical({'cases':cases})
   m.PARTITIONS_SHA256=m.file_info(part)['sha256'];m.COHORT_SHA256=m.sha_bytes(cohort);m.SPLIT_SHA256=m.sha_bytes(m.canonical(splits))
   plans=m._synthetic_plans()
   handoff={'arm':K_ACMC,'smoke':False,'cases':cases,'splits':splits,'plans':plans,'windows':{k:list(m.WINDOWS[k])for k in m.BASE6},'source_inventory':{'brain':'cad80ea68c35','cbf':'71905e6a3737','cbv':'678b1bfd5639','cta':'f3f200c85d00','lesion':'fbcfad347f52','mtt':'732e673174db','ncct':'b5137a3f1df6','tmax':'71fb01614363'}}
   for name,obj in[('plans',plans),('handoff',handoff)]:m.write_once(inp,'baseline/'+name+'.json',m.canonical(obj))
   m.BASE_PLANS_SHA256=m.file_info(inp/K_BPJ)['sha256'];m.BASE_HANDOFF_SHA256=m.file_info(inp/K_BHJ)['sha256']
   rng=n.random.default_rng(1301);aff=n.diag([5.,5.,5.,1.]);shape=(16,)*3
   for case in cases:
    truth=n.zeros(shape,n.uint8);truth[5:10,5:10,5:10]=1
    arrays={k:rng.uniform(m.WINDOWS[k][0]+.1,m.WINDOWS[k][1]-.1,shape).astype('float32')for k in m.BASE6};arrays.update(brain=n.ones(shape,n.uint8),lesion=truth)
    for k,rel in m.source_paths(case).items():
     q=inp/rel;q.parent.mkdir(parents=True,exist_ok=True);m.nib.save(m.nib.Nifti1Image(arrays[k],aff),q)
    target=m.resample_to_output(m.nib.Nifti1Image(truth,aff),voxel_sizes=(2.,)*3,order=0);y=target.get_fdata()>.5;mask=n.ones(y.shape,bool);count=int(mask.sum())
    feat={'X':n.zeros((count,len(m.FEATURE_NAMES)),n.float32),'y':y[mask].astype('uint8'),'sdt':n.zeros(count,n.float32),'mask':mask,K_LF:y,'healthy_side':n.zeros(count,bool),'shape':y.shape,'affine':target.affine,'voxel_ml':.008,'summary':{}}
    q=inp/'feature-cache-2mm-v2'/f'{case}.npz';q.parent.mkdir(exist_ok=True);m.save_cache(str(q),feat,case,m.config_hash(m.FEATURE_CFG))
   inv={q.relative_to(inp).as_posix():m.file_info(q)for q in inp.rglob('*')if q.is_file()}
   req={'schema':'scientific-environment-requirements/v1','python':f'{sys.version_info.major}.{sys.version_info.minor}','cuda':'12.8','packages':{k:version(k)for k in('torch','nnunetv2','numpy','nibabel','pandas','scipy','scikit-learn','simpleitk')}}
   need(req['packages']['nnunetv2']=='2.8.1' and torch.version.cuda=='12.8','E166')
   env=m.sha_bytes(m.canonical(req));pin=m.sha_bytes(Path(__file__).read_bytes())
   sel={'schema':K_DPPV,'id':'synthetic-prep',K_ICS:m.sha_bytes(json.dumps(inv,sort_keys=True,allow_nan=False).encode()),K_ERS:env,K_SS:m.SPLIT_SHA256,K_PN:'SyntheticPlans',K_CS:m.COHORT_SHA256,K_SCS:m.sha_bytes(b'synthetic sources only'),'partitions_sha256':m.PARTITIONS_SHA256}
   plan={'schema':'scientific-execution-plan/v2','run_id':m.RUN_ID,'operator_scope_sha256':'101f869a822c4c713e71f7c9ce91514094978c11f2bf012234b9cab2c9971309','dispatch_mode':'incremental','fits':[{'fit_id':K_SF,'arm':K_AR,K_PI:sel['id']}],K_P:[sel],K_ER:req}
   native={k:v for k,v in sel.items()if k!=K_ERS};native.update(schema='reviewed-preprocessing-partitions/v1',environment_sha256=env)
   rt={'run_id':m.RUN_ID,'spec_sha256':m.sha_bytes(b'synthetic rehearsal, no approval'),K_EPS:m.sha_bytes(m.canonical(plan)),'execution':{K_MS:pin},K_P:native};commits={}
   def checkpoint(step,files):
    need(step not in commits and all(m.file_info(prep/k)==v for k,v in files.items()),'E174')
    m.write_once(root/'steps',step+'.json',m.canonical(files));commits[step]=copy.deepcopy(files)
   ctx={K_EP:plan,'runtime':rt,K_P:native,'frozen_partitions':{'path':str(part),'sha256':m.PARTITIONS_SHA256},'completed_steps':{},'checkpoint':checkpoint}
   result=m.preprocess(inp,prep,ctx)
   stamps={k:(v,(prep/k).stat().st_mtime_ns)for files in commits.values()for k,v in files.items()}
   linked=dict(ctx,completed_steps={q.stem:json.loads(q.read_bytes())for q in(root/'steps').glob('*.json')})
   need(m.preprocess(inp,prep,linked)==result and stamps=={k:(m.file_info(prep/k),(prep/k).stat().st_mtime_ns)for k in stamps},'E167')
   assets={K_PCS:pin,K_PN:sel[K_PN],K_SS:sel[K_SS]};binding={k:native[k]for k in(K_ICS,K_ES)}
   def validate(r):return validate_preprocessed(r,cohort,assets,binding,cohort_sha256=m.COHORT_SHA256,source_sha256=sel[K_SCS])
   files=validate(result['proposed']);v=result[K_V];validate_validation(v,{k:v[k]for k in('run_id','spec_sha256',K_PCS,'validator_sha256',K_CS,K_ICS,K_ES)},files)
   need(len(files)==300 and all(m.file_info(prep/k)==v for k,v in files.items()),'E168')
   bad=copy.deepcopy(result['proposed']);bad['case_files'].pop(cases[0]);_must_refuse(lambda:validate(bad),ValueError)
   observed=result['proposed'][K_PS];progress=progress_factory(root/'durable',K_SF,observed,env)
   need(type(progress)is FitProgress,'E169')
   _,pre=m._prepared_paths(prep,K_AR)
   class Interrupted(RuntimeError):pass
   class RehearsalTrainer(nnUNetTrainer):
    def on_epoch_end(s):
     super().on_epoch_end()
     if s.current_epoch==1 and s.stop_after_one:raise Interrupted()
   def tr(segment):
    m._native_paths(root/'raw',prep/'preprocessed',progress.root/'work');os.environ[K_NNPD]='0'
    t=RehearsalTrainer(dict(json.loads((pre/'SyntheticPlans.json').read_bytes()),continue_training=segment>1),K_3F,0,json.loads((pre/K_DJ).read_bytes()),device=torch.device('cpu'))
    t.num_epochs=2;t.num_iterations_per_epoch=2;t.num_val_iterations_per_epoch=2;t.stop_after_one=segment==1
    t.log_file=str(progress.root/'work'/f'training_log_{segment}.txt');Path(t.log_file).touch(exist_ok=False);m._fit_truth(pre,t,splits[0]['val'],progress.root/'work');return t
   with progress.writer(initial=True):
    (progress.root/'work').mkdir(exist_ok=True);a=tr(1)
    _must_refuse(lambda:run_fit(a,progress,initial=True,save_every=1,segment=1),Interrupted)
    cp,rec=progress.select('latest');need(rec['metadata'][K_NE]==1,'E175');cp_hash=m.file_info(cp)['sha256']
   progress=progress_factory(root/'durable',K_SF,observed,env)
   with progress.writer(initial=False):
    b=tr(2);receipt=run_fit(b,progress,initial=False,save_every=1,segment=2,interruption={'synthetic':True,'checkpoint_sha256':cp_hash})
    need(receipt['epoch_resumed_from']==1 and b.current_epoch==2 and b.optimizer.state_dict()['state'],'E176')
    cp,rec=progress.select('final');need(rec['sha256']==receipt['final_sha256']==m.file_info(cp)['sha256'],'final hash')
    scores=m._score_native(prep,b,K_AR,0,splits,progress.root/'work')
    need(scores['n_heldout']==20 and all(math.isfinite(float(b.logger.get_value('train_losses',step=i)))for i in range(2)),'scoring/loss')
   diag=_native_diagnostic_fixture(m,root,prep,pre,splits,progress_factory,observed,env)
   return{'schema':'item4-native-synthetic-integration/v1',K_MS:pin,'preprocessed_files':300,'preprocessing_reuse_verified':True,'resume':receipt,'aggregate_scores':scores,'diagnostic':diag,'gpu_verified':False,'production_main_verified':False,'scientific_approval':False,'scope':'Generated CPU fixtures; reduced network/geometry/workers, base 2x2 steps and diagnostic 15x250/50; no benchmark or efficacy.'}
  finally:os.environ.clear();os.environ.update(old);torch.set_num_threads(threads)

def _native_diagnostic_fixture(m,root,prep,pre,splits,progress_factory,plans_hash,env):
 import torch,threading
 from orchestrator.modal_nnunet import run_fit
 c=dict(cpu=2,workers=2,epochs=15,seed=101,save_every=10,**{K_VW:1,K_LH:250,K_MSS:2100})
 class C(m.DiagnosticMonitor):
  def guard(s):
   need(s.clock()-s.started<s.config[K_MSS],'E170')
  def start(s):
   s.sample()
   def loop():
    while not s.stop_event.wait(1) and s.clock()-s.started<s.config[K_MSS]:s.sample()
   s.thread=threading.Thread(target=loop,daemon=True);s.thread.start()
 o=C(c);o.cpu_start=m.cpu_capacity()
 p=progress_factory(root/'diagnostic',K_SF,plans_hash,env);q=m.DiagnosticProgress(p,o)
 with p.writer(initial=True):
  w=p.root/'work';w.mkdir(exist_ok=True);m._native_paths(root/'raw',prep/'preprocessed',w/'results');os.environ[K_NNPD]='2';torch.manual_seed(101)
  t=m.diagnostic_trainer_class(c,o)(dict(json.loads((pre/'SyntheticPlans.json').read_bytes()),continue_training=False),K_3F,0,json.loads((pre/K_DJ).read_bytes()),device=torch.device('cpu'));t.num_epochs=15
  need((t.num_iterations_per_epoch,t.num_val_iterations_per_epoch)==(250,50),'E171')
  t.log_file=str(w/'training_log_1.txt');Path(t.log_file).touch(exist_ok=False);m._fit_truth(pre,t,splits[0]['val'],w)
  try:
   o.start();z=run_fit(t,q,initial=True,save_every=10,segment=1)
   need(t.current_epoch==15 and t.lr_scheduler.max_steps==250,'E177')
   a=t._measurements;g=m.diagnostic_timing({'fit_id':K_SF},a)
   need(len(a)==15 and all(r[K_LW]>0 for r in a),'E178')
   need([e[K_NE]for e in o.events if e['kind']=='latest']==[0,10]and any(e['kind']=='final' and e[K_NE]==15 for e in o.events),'E179')
   cp,rec=p.select('final');need(m.file_info(cp)['sha256']==rec['sha256']==z['final_sha256'],'E180')
   h=m._score_native(prep,t,K_AR,0,splits,w)
  finally:
   try:_finish_loaders(t)
   finally:o.close()
  need(not o.thread.is_alive()and o.completeness()['status']=='FAIL' and not o.samples,'E172')
  x=m.DiagnosticMonitor(c)
  try:_must_refuse(x.start,m.PrerequisiteError)
  finally:x.close()
  b=m.DiagnosticMonitor(c);b.started-=2101
  try:_must_refuse(b.guard,m.PrerequisiteError)
  finally:b.close()
  d=dict(schema='cpu-starvation-diagnostic/v1',fit_id=K_SF,valid=False,retry_permitted=False,configuration=c,observed_cpu_start=o.cpu_start,workers=t._diagnostic_workers,sampling=o.completeness(),gpu_samples=o.samples,checkpoint_events=o.events,epoch_records=a,**{K_S:g[K_S],K_MWS:o.ended-o.started},cost_micro_usd=None,whole_job_seconds=None)
  i=m.write_once(w,K_CDJ,m.canonical(d));q.receipt('cpu-diagnostic-failed',{'valid':False,'retry_permitted':False,'files':{K_CDJ:i}})
  need(m.file_info(w/K_CDJ)==i and json.loads((w/K_CDJ).read_bytes())==d,'E173')
  return dict(status='DURABLE_INVALID_GPU_TELEMETRY',file=i,report=d,native_receipt=z,aggregate_scores=h,thread_joined=True,production_gpu_output_closure_verified=False,stop_boundary_verified=True)
