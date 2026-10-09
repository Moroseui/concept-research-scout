from pathlib import Path
import hashlib, json, math, os, time, unittest, tempfile, copy, importlib
BASE_PLANS_SHA256 = '532aa8160bf0db6c83ceeb0c1456d3bf6f2f7b528cdb0a9586866ac724de92d0'
BASE_HANDOFF_SHA256 = '5a5649e12a568ce99c8c2b4abd88732d07a862d44c32da9f1ddfc599699ddb01'
RUN_ID = 'experiment-a74959ac4546a982af4ae137'
PARTITIONS_SHA256 = '2c197a9addf40af4d75dd220a095b62130b0ca58ffbe5dce8eb73dff570f64f8'
COHORT_SHA256 = '45c5746f60e2275383a2c4f4096295fe7a171da85a73737c5a35a8cc6fc9fe86'
SPLIT_SHA256 = 'd339296ca3b1672fc744e14188b36c1860b379a38b807eca67d8b73038007c86'
ARMS_ORDER = ('A1_repeat','A1_repeat2','A1_zscore','A1_histeq','A1_multiwin','A1_L','A1_pnormct','A1_pnorm_v2')
CANDIDATES = ('A1_zscore','A1_histeq','A1_multiwin','A1_L','A1_pnormct')
WINDOWS = {'ncct':(0,80),'cbf':(0,35),'cbv':(0,10),'mtt':(0,20),'tmax':(0,7),'cta':(0,90),
  'ncct_w2':(20,50),'cbf_w2':(0,100),'cbv_w2':(0,4),'mtt_w2':(0,12),'tmax_w2':(0,20),'cta_w2':(0,300)}
BASE6=('ncct','cbf','cbv','mtt','tmax','cta')
PERF_KINDS=('cbf','cbv','mtt','tmax')
ZSCORE_MIN_SD=0.01
HISTEQ_BINS=256
VOXEL_MM=(2.,2.,2.)
PNORM_NN={'min_ref_voxels':20000,'min_scale':{'cbf':.7,'cbv':.2,'mtt':.4,'tmax':.14,'ncct':1.6},'clip_z':5.}
FEATURE_CFG={'target_mm':2.0,'vessel_pct':98.0,'core_thr':.30,'penumbra_tmax':6.0,'schema':'isles24-features-2mm-v2'}
class PrerequisiteError(RuntimeError): pass
def canonical(obj):
 return (json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('utf-8')
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def file_info(path):
 p=Path(path); h=hashlib.sha256(); n=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b); n+=len(b)
 return {'sha256':h.hexdigest(),'bytes':n}
def require(test, message):
 if not test: raise PrerequisiteError(message)
def digest(value):
 return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)
def rooted(root, relative):
 root=Path(root).resolve(); r=Path(relative)
 require(not r.is_absolute() and r.parts and '..' not in r.parts,'invalid relative artifact path')
 p=root/r
 require(p.resolve().is_relative_to(root),'artifact escapes declared root')
 require(not any(x.is_symlink() for x in [p,*p.parents] if x!=root.parent),'symlink artifact refused')
 return p
def read_verified(root, descriptor):
 require(set(descriptor)=={'path','sha256','bytes'},'invalid source descriptor')
 require(digest(descriptor['sha256']) and type(descriptor['bytes']) is int and descriptor['bytes']>0,'missing source identity')
 p=rooted(root,descriptor['path']); require(file_info(p)=={k:descriptor[k] for k in ('sha256','bytes')},'source bytes changed')
 return p
def write_once(root, rel, data):
 p=rooted(root,rel); p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f: f.write(data)
 return file_info(p)
def split_document(partitions, expected_count=99):
 require(isinstance(partitions,dict),'invalid partitions')
 keys=[k for k in partitions if k.startswith('101_')]
 require(set(keys)=={f'101_{k}' for k in range(5)},'missing or extra shuffle-101 fold')
 out=[]; held=[]
 for k in range(5):
  row=partitions[f'101_{k}']; tr=row['train']; va=row['held']
  require(isinstance(tr,list) and isinstance(va,list) and tr and va,'empty partition')
  require(all(isinstance(x,str) and x and '/' not in x and '\\' not in x and x not in ('.','..') for x in tr+va),'invalid member token')
  require(len(tr)==len(set(tr)) and len(va)==len(set(va)) and not set(tr)&set(va),'duplicate or leaked split')
  out.append({'train':sorted(tr),'val':sorted(va)}); held+=va
 require(len(held)==len(set(held))==expected_count,'frozen cohort size or repeated holdout changed')
 for row in out: require(set(row['train'])==set(held)-set(row['val']),'training complement changed')
 return out
def bound_plan(contract, preprocessing=False):
 plan=contract['execution_plan']; rt=contract['runtime']
 require(plan.get('operator_scope_sha256')=='101f869a822c4c713e71f7c9ce91514094978c11f2bf012234b9cab2c9971309','operator scope mismatch')
 require(plan['schema']=='scientific-execution-plan/v2' and plan['run_id']==RUN_ID and plan['dispatch_mode']=='incremental','plan identity')
 require(sha_bytes(canonical(plan))==rt['execution_plan_sha256'],'plan bytes differ from reviewed canonical plan')
 require(rt['run_id']==RUN_ID and digest(rt['spec_sha256']) and rt.get('execution',{}).get('module_sha256')==sha_bytes(Path(__file__).read_bytes()),'run/spec/exported module identity')
 if preprocessing:
  supplied=contract.get('preprocessing')
  require(isinstance(supplied,dict) and isinstance(supplied.get('id'),str),'controller preprocessing selection missing')
  eid=supplied['id']
 else:
  selected=[x for x in plan['fits'] if x['fit_id']==rt['experiment']['fit_id']]
  require(len(selected)==1,'fit identity ambiguous')
  eid=selected[0]['preprocessing_id']
 rows=[x for x in plan['preprocessing'] if x.get('id')==eid]
 require(len(rows)==1,'preprocessing identity ambiguous'); sel=rows[0]
 fields={'schema','id','input_contract_sha256','environment_requirements_sha256','split_sha256','plans_name','cohort_sha256','source_capture_sha256','partitions_sha256'}
 require(set(sel)==fields and sel['schema']=='declared-preprocessing-partitions/v1','preprocessing selection schema mismatch')
 missing=[k for k in ('input_contract_sha256','source_capture_sha256','cohort_sha256','split_sha256','environment_requirements_sha256') if not digest(sel.get(k))]
 require(not missing,'unavailable original prerequisite bindings: '+', '.join(missing))
 require(sel['partitions_sha256']==PARTITIONS_SHA256 and sel['cohort_sha256']==COHORT_SHA256 and sel['split_sha256']==SPLIT_SHA256,'frozen cohort or split binding')
 require(sel['environment_requirements_sha256']==sha_bytes(canonical(plan['environment_requirements'])),'requirements identity')
 if preprocessing:
  shared=fields-{'schema','environment_requirements_sha256'}
  require(all(supplied.get(k)==sel[k] for k in shared),'controller preprocessing binding differs')
  if supplied.get('schema')=='declared-preprocessing-partitions/v1':
   require(supplied==sel,'declared preprocessing binding differs')
  else:
   require(supplied.get('schema')=='reviewed-preprocessing-partitions/v1','unreviewed native preprocessing schema')
   require(set(supplied)==shared|{'schema','environment_sha256'},'native preprocessing fields differ')
   require(digest(supplied.get('environment_sha256')) and supplied['environment_sha256']==rt.get('preprocessing',{'environment_sha256':rt.get('environment_sha256')}).get('environment_sha256'),'native environment binding differs')
 return plan,rt,sel
def environment_check(requirements):
 import sys
 from importlib.metadata import version
 require(f'{sys.version_info.major}.{sys.version_info.minor}'==requirements['python'],'Python requirement mismatch')
 for package,wanted in requirements['packages'].items(): require(version(package)==wanted,'package requirement mismatch: '+package)
 import torch
 require(torch.version.cuda==requirements['cuda'],'CUDA build requirement mismatch')
def _load_science():
 global np,pd,nib,resample_from_to,resample_to_output,gaussian_filter,uniform_filter,distance_transform_edt,cc_label,binary_fill_holes,binary_erosion,roc_auc_score,average_precision_score
 import numpy as np
 import pandas as pd
 import nibabel as nib
 from nibabel.processing import resample_from_to,resample_to_output
 from scipy.ndimage import gaussian_filter,uniform_filter,distance_transform_edt,label as cc_label,binary_fill_holes,binary_erosion
 from sklearn.metrics import roc_auc_score,average_precision_score
def verify_completed(output_root, completed):
 known={}
 for step,files in completed.items():
  require(isinstance(step,str) and isinstance(files,dict) and files,'empty checkpoint')
  for rel,info in files.items():
   require(isinstance(info,dict) and set(info)=={'sha256','bytes'} and digest(info['sha256']) and type(info['bytes']) is int and info['bytes']>0,'invalid committed file descriptor')
   require(rel not in known,'file belongs to two committed steps')
   require(file_info(rooted(output_root,rel))==info,'committed file changed')
   known[rel]=info
 return known
def commit_step(root,contract,step,files):
 require(step not in contract.get('completed_steps',{}),'cannot recommit a step')
 old=verify_completed(root,contract.get('completed_steps',{}))
 require(files and not set(files)&set(old),'cannot alter a committed artifact')
 records={r:file_info(rooted(root,r)) for r in sorted(files)}
 contract['checkpoint'](step,records)
 contract.setdefault('completed_steps',{})[step]=records
 return records
def load_frozen_partitions(contract):
 f=contract['frozen_partitions']; require(f['sha256']==PARTITIONS_SHA256,'partition descriptor mismatch')
 b=Path(f['path']).read_bytes(); require(sha_bytes(b)==PARTITIONS_SHA256,'partition bytes mismatch')
 splits=split_document(json.loads(b)); require(sha_bytes(canonical(splits))==SPLIT_SHA256,'emitted split hash changed')
 return splits
def derived_ctp_support(ctp, brain):
 raise PrerequisiteError('U3 coverage held: registered CTP padding/support not authenticated for the cohort')
def pnorm_reference(maps,brain):
 all_zero=np.logical_and.reduce([np.where(np.isfinite(maps[k]),maps[k],0)==0 for k in PERF_KINDS])
 t=maps['tmax']
 return [('brain with Tmax <= 6 s',brain & np.isfinite(t) & (t>=0) & (t<=6) & ~all_zero),('whole brain',brain & ~all_zero)],all_zero
def normalize_channel(v,kind,levels,brain,invalid):
 out,rec=_pnorm_channel(v,kind,levels,brain)
 invalid=invalid | ~np.isfinite(v) | ((v<=0) if kind in ('cbf','cbv','mtt') else (v<0))
 return np.where(brain & ~invalid,out,0).astype(np.float32),rec
def transform_case(arrays,arm):
 require(arm in ARMS_ORDER,'unknown arm'); brain=arrays['brain']>.5
 maps={k:arrays[k] for k in BASE6}; outputs={}; qc={}
 require(brain.any() and all(v.shape==brain.shape for v in maps.values()),'missing brain or incompatible arrays')
 coverage=None
 if arm in ('A1_zscore','A1_histeq'): coverage=derived_ctp_support(arrays['ctp'],brain)
 pref=pnorm_reference(maps,brain) if arm in ('A1_pnormct','A1_pnorm_v2') else None
 channels=BASE6+tuple(k+'_w2' for k in BASE6) if arm=='A1_multiwin' else BASE6
 for ch in channels:
  k=ch.removesuffix('_w2'); v=maps[k]; support,record=coverage_support(v,brain,coverage if k in PERF_KINDS else None)
  x=window01(v,*WINDOWS[ch]); raw=v[brain & np.isfinite(v)]
  record.update(clip_low=float(np.mean(raw<=WINDOWS[ch][0])) if raw.size else None,clip_high=float(np.mean(raw>=WINDOWS[ch][1])) if raw.size else None)
  if arm in ('A1_zscore','A1_histeq'):
   x,r=(zscore_in_brain(x,support) if arm=='A1_zscore' else histeq_in_brain(x,support)); record.update(r)
   require(r.get('fallback') not in ('empty support','constant support'),'degenerate transform support')
  elif pref is not None and (k in PERF_KINDS or (arm=='A1_pnormct' and k=='ncct')):
   levels=pref[0] if k in PERF_KINDS else [('whole finite nonnegative brain',brain)]
   x,r=normalize_channel(v,k,levels,brain,pref[1] if k in PERF_KINDS else np.zeros(brain.shape,bool)); record.update(r)
  x=(x*brain).astype(np.float32)
  require(np.isfinite(x).all() and float(x[brain].std())>=1e-6,'nonfinite or constant prepared channel')
  outputs[ch]=x; record['prepared_sd']=float(x[brain].std()); qc[ch]=record
 return outputs,qc
def validate_full_folds(table, held):
 if set(held) != set(range(5)):
  raise ValueError("expected frozen folds 0 through 4")
 expected = [(c, k, 101) for k in range(5) for c in held[k]]
 if any(len(held[k]) == 0 for k in range(5)) or len(expected) != 99:
  raise ValueError("expected 99 members in five nonempty folds")
 members = [r[0] for r in expected]
 if len(set(members)) != 99:
  raise ValueError("duplicate or overlapping frozen members")
 if not {"case", "fold", "shuffle"}.issubset(table.columns):
  raise ValueError("membership columns missing")
 keys = table[["case", "fold", "shuffle"]]
 if len(keys) != 99 or keys.isna().any().any() or keys.case.duplicated().any():
  raise ValueError("missing, extra, null or duplicate rows")
 if set(keys.itertuples(index=False, name=None)) != set(expected):
  raise ValueError("row membership, fold or shuffle mismatch")
def verdict_from_intervals(base_ci, repeat_ci, complete=True):
 normalized = []
 for ci in (base_ci, repeat_ci):
  try:
   arr = np.asarray(ci, dtype=float)
  except (ValueError, TypeError) as e:
   raise ValueError("invalid interval") from e
  if arr.shape != (3,) or not np.isfinite(arr).all() or arr[1] > arr[2]:
   raise ValueError("malformed, reversed or nonfinite interval")
  normalized.append(arr)
 base_ci, repeat_ci = normalized
 if not complete:
  return "provisional"
 if base_ci[1] > 0 and repeat_ci[1] > 0:
  return "better"
 if base_ci[2] < 0 and repeat_ci[2] < 0:
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
def source_paths(case, with_ctp=False):
 require(isinstance(case,str) and case and '/' not in case and '\\' not in case and case not in ('.','..'),'invalid source member')
 d=f'train/derivatives/{case}'
 paths={k:f'{d}/ses-01/perfusion-maps/{case}_ses-01_space-ncct_{k}.nii.gz' for k in PERF_KINDS}
 paths.update(ncct=f'train/raw_data/{case}/ses-01/{case}_ses-01_ncct.nii.gz',
    cta=f'{d}/ses-01/{case}_ses-01_space-ncct_cta.nii.gz',
    lesion=f'{d}/ses-02/{case}_ses-02_space-ncct_lesion-msk.nii.gz',
    brain=f'brainmask/{case}_brainmask.nii.gz')
 if with_ctp: paths['ctp']=f'{d}/ses-01/{case}_ses-01_space-ncct_ctp.nii.gz'
 return paths
def source_inventory(input_root,cases,with_ctp,expected_sha256):
 expected={c:dict(source_paths(c,with_ctp),cache=f'feature-cache-2mm-v2/{c}.npz') for c in cases}
 allowed={rel for row in expected.values() for rel in row.values()}|{'baseline/plans.json','baseline/handoff.json'}
 present={p.relative_to(input_root).as_posix() for p in Path(input_root).rglob('*') if p.is_file()}
 require(present==allowed,'source inventory has missing or extra paths')
 inventory={rel:file_info(rooted(input_root,rel)) for rel in sorted(allowed)}
 require(sha_bytes(json.dumps(inventory,sort_keys=True,allow_nan=False).encode())==expected_sha256,'original source inventory binding changed')
 return {'cases':{c:{k:dict(path=rel,**inventory[rel]) for k,rel in row.items()} for c,row in expected.items()},
   'baseline_plans':dict(path='baseline/plans.json',**inventory['baseline/plans.json']),
   'baseline_handoff':dict(path='baseline/handoff.json',**inventory['baseline/handoff.json'])}
def _input_manifest(input_root,contract,sel):
 splits=load_frozen_partitions(contract); cases=sorted(c for fold in splits for c in fold['val'])
 arms={f['arm'] for f in contract['execution_plan']['fits'] if f['preprocessing_id']==sel['id']}
 require(not arms & {'A1_zscore','A1_histeq'},'U3 coverage held: no cohort-authenticated support definition')
 mapped=source_inventory(input_root,cases,False,sel['input_contract_sha256'])
 require(mapped['baseline_plans']['sha256']==BASE_PLANS_SHA256,'baseline plans changed')
 require(mapped['baseline_handoff']['sha256']==BASE_HANDOFF_SHA256,'baseline handoff changed')
 handoff=json.loads(read_verified(input_root,mapped['baseline_handoff']).read_bytes())
 require(handoff['smoke'] is False and sorted(handoff['cases'])==cases,'baseline full99 identity')
 require(handoff['arm']=='A1_ct_maps_cta' and handoff['splits']==splits,'baseline arm/splits')
 require(handoff['source_inventory']=={'brain':'cad80ea68c35','cbf':'71905e6a3737','cbv':'678b1bfd5639','cta':'f3f200c85d00','lesion':'fbcfad347f52','mtt':'732e673174db','ncct':'b5137a3f1df6','tmax':'71fb01614363'},'historical source inventory changed')
 return mapped
def _native_paths(raw,pre,results):
 os.environ.update(nnUNet_raw=str(raw),nnUNet_preprocessed=str(pre),nnUNet_results=str(results),nnUNet_n_proc_DA='12')
def _load_case_sources(input_root,sources,arm):
 needed=set(BASE6)|{'brain','lesion','cache'}
 if arm in ('A1_zscore','A1_histeq'): needed.add('ctp')
 require(set(sources)==needed,'source set must match frozen arm, no extra files')
 paths={k:read_verified(input_root,sources[k]) for k in needed}
 ref=nib.load(str(paths['ncct'])); arrays={}
 for k in needed-{'cache'}:
  img=nib.load(str(paths[k])); arr=np.asanyarray(img.dataobj)
  if k!='ctp' and arr.ndim==4 and arr.shape[-1]==1: arr=arr[...,0]
  require(arr.shape[:3]==ref.shape[:3] and np.allclose(img.affine,ref.affine,atol=.001,rtol=0),'source geometry differs from NCCT')
  require(arr.ndim==(4 if k=='ctp' else 3),'source dimensionality')
  arrays[k]=arr
 brain=arrays['brain']>.5; ml=float(brain.sum()*np.prod(ref.header.get_zooms()[:3])/1000)
 require(400<=ml<=2500,'brain volume outside frozen range')
 require(np.isfinite(arrays['brain']).all() and np.isfinite(arrays['lesion']).all(),'nonfinite mask')
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
 require(dice(mapped,cache['lesion_full'])>=.999,'source lesion differs from frozen scoring truth')
 raw,pre=_prepared_paths(output_root,arm); written=[]
 for i,(ch,arr) in enumerate(x.items()):
  p=raw/'imagesTr'/f'{case}_{i:04d}.nii.gz'; p.parent.mkdir(parents=True,exist_ok=True)
  require(not p.exists(),'uncommitted existing case file'); nib.save(nib.Nifti1Image(arr,ref.affine),str(p)); written.append(p)
 p=raw/'labelsTr'/f'{case}.nii.gz'; p.parent.mkdir(parents=True,exist_ok=True)
 require(not p.exists(),'uncommitted existing label'); nib.save(nib.Nifti1Image(truth.astype(np.uint8),ref.affine),str(p)); written.append(p)
 q=Path(output_root)/'qc'/f'{case}.json'
 write_once(output_root,q.relative_to(output_root).as_posix(),canonical({'channels':qc,'source_cache_dice':float(dice(mapped,cache['lesion_full'])),'brain_ml':float((arrays['brain']>.5).sum()*np.prod(ref.header.get_zooms()[:3])/1000),'infarct_in_brain':float((truth & (arrays['brain']>.5)).sum()/truth.sum()) if truth.any() else 1.}))
 written.append(q)
 return written  
def _prepare_shared(input_root,output_root,contract,manifest,arm,splits,sel):
 from nnunetv2.experiment_planning.dataset_fingerprint.fingerprint_extractor import DatasetFingerprintExtractor
 raw,pre=_prepared_paths(output_root,arm); ds=raw.name
 n=12 if arm=='A1_multiwin' else 6
 dataset={'channel_names':{str(i):'noNorm' for i in range(n)},'labels':{'background':0,'infarct':1},'numTraining':99,'file_ending':'.nii.gz'}
 write_once(output_root,(raw/'dataset.json').relative_to(output_root).as_posix(),canonical(dataset))
 DatasetFingerprintExtractor(ds,num_processes=6,verbose=False).run(overwrite_existing=False)
 bp=read_verified(input_root,manifest['baseline_plans']); bh=read_verified(input_root,manifest['baseline_handoff'])
 base=json.loads(bp.read_bytes()); handoff=json.loads(bh.read_bytes())
 require(handoff['arm']=='A1_ct_maps_cta' and handoff['splits']==splits,'baseline handoff fold/arm mismatch')
 require(handoff['plans']==base,'baseline plan/handoff mismatch')
 require(all(handoff['windows'][k]==list(WINDOWS[k]) for k in BASE6),'baseline windows changed')
 require(handoff['smoke'] is False and len(handoff['cases'])==99,'baseline must be full99')
 if arm=='A1_L':
  from nnunetv2.utilities.find_class_by_name import recursive_find_python_class
  import nnunetv2
  cls=recursive_find_python_class(str(Path(nnunetv2.__file__).parent/'experiment_planning'),'nnUNetPlannerResEncL','nnunetv2.experiment_planning')
  require(cls is not None,'native L planner unavailable')
  planner=cls(ds); plans=planner.plan_experiment()
  require(plans['plans_name']==sel['plans_name'],'L whole preset name changed')
 else:
  plans=copy.deepcopy(base); plans['dataset_name']=ds
  for cfg in plans['configurations'].values():
   if 'normalization_schemes' in cfg:
    require(set(cfg['normalization_schemes'])=={'NoNormalization'},'baseline native normalization differs')
    cfg['normalization_schemes']=['NoNormalization']*n
   if 'use_mask_for_norm' in cfg: cfg['use_mask_for_norm']=[False]*n
  fp=json.loads((pre/'dataset_fingerprint.json').read_bytes())
  if 'foreground_intensity_properties_per_channel' in plans: plans['foreground_intensity_properties_per_channel']=fp['foreground_intensity_properties_per_channel']
  write_once(output_root,(pre/(sel['plans_name']+'.json')).relative_to(output_root).as_posix(),canonical(plans))
  for key in ('patch_size','spacing','batch_size','architecture'):
   require(plans['configurations']['3d_fullres'][key]==base['configurations']['3d_fullres'][key],'M comparator architecture changed')
 if not (pre/'dataset.json').exists(): write_once(output_root,(pre/'dataset.json').relative_to(output_root).as_posix(),canonical(dataset))
 write_once(output_root,(pre/'splits_final.json').relative_to(output_root).as_posix(),canonical(splits))
 write_once(output_root,'preparation.json',canonical({'arm':arm,'dataset':ds,'plans_name':sel['plans_name'],'plans_sha256':file_info(pre/(sel['plans_name']+'.json'))['sha256'],'preprocessing_id':sel['id'],'split_sha256':sel['split_sha256']}))
 return None
def _native_case(output_root,contract,case,arm,sel):
 from nnunetv2.utilities.plans_handling.plans_handler import PlansManager
 raw,pre=_prepared_paths(output_root,arm)
 pm=PlansManager(str(pre/(sel['plans_name']+'.json'))); cfg=pm.get_configuration('3d_fullres')
 worker=cfg.preprocessor_class(verbose=False); folder=pre/cfg.data_identifier; folder.mkdir(parents=True,exist_ok=True)
 images=sorted(str(p) for p in (raw/'imagesTr').glob(case+'_*.nii.gz'))
 worker.run_case_save(str(folder/case),images,str(raw/'labelsTr'/f'{case}.nii.gz'),pm,cfg,json.loads((raw/'dataset.json').read_bytes()))
 files=[p.relative_to(output_root).as_posix() for p in folder.glob(case+'.*') if p.is_file()]
 files += [p.relative_to(output_root).as_posix() for p in folder.glob(case+'_seg.*') if p.is_file()]
 require(len(files)>=2,'native preprocessor did not emit data and properties')
 return files
def _arm(plan,sel):
 arms={f['arm'] for f in plan['fits'] if f['preprocessing_id']==sel['id']}
 if arms=={'A1_repeat','A1_repeat2'}:return 'A1_repeat'
 require(len(arms)==1,'incompatible shared preparation')
 arm=next(iter(arms)); require(arm not in ('A1_zscore','A1_histeq'),'U3 coverage held')
 return arm
def _shared_publish(input_root,root,contract,manifest,arm,splits,sel):
 import shutil
 with tempfile.TemporaryDirectory(prefix='.staging-',dir=root) as td:
  stage=Path(td); _native_paths(stage/'raw',stage/'preprocessed',stage/'native-work')
  for case,sources in manifest['cases'].items():_case_raw(input_root,stage,contract,case,sources,arm)
  _prepare_shared(input_root,stage,contract,manifest,arm,splits,sel)
  _,src=_prepared_paths(stage,arm); _,dest=_prepared_paths(root,arm)
  dataset=json.loads((src/'dataset.json').read_bytes())
  dataset['item4_fingerprint']=json.loads((src/'dataset_fingerprint.json').read_bytes())
  dataset['item4']={'arm':arm,'preprocessing_id':sel['id'],'input_contract_sha256':sel['input_contract_sha256'],
      'source_capture_sha256':sel['source_capture_sha256'],'split_sha256':sel['split_sha256']}
  files=[]
  for name,raw in [('dataset.json',canonical(dataset)),(sel['plans_name']+'.json',(src/(sel['plans_name']+'.json')).read_bytes()),('splits_final.json',canonical(splits))]:
   rel=(dest/name).relative_to(root).as_posix();write_once(root,rel,raw);files.append(rel)
 commit_step(root,contract,'shared',files)
def _case_publish(input_root,root,contract,case,sources,arm,sel):
 import pickle
 with tempfile.TemporaryDirectory(prefix='.staging-',dir=root) as td:
  stage=Path(td);_native_paths(stage/'raw',stage/'preprocessed',stage/'native-work')
  _case_raw(input_root,stage,contract,case,sources,arm)
  raw,sp=_prepared_paths(stage,arm);_,pre=_prepared_paths(root,arm)
  for name in ('dataset.json',sel['plans_name']+'.json'):
   write_once(stage,(sp/name).relative_to(stage).as_posix(),(pre/name).read_bytes())
  write_once(stage,(raw/'dataset.json').relative_to(stage).as_posix(),(pre/'dataset.json').read_bytes())
  emitted=_native_case(stage,contract,case,arm,sel)
  require(len(emitted)==3,'native preprocessor must emit image, segmentation, properties')
  prop=next(stage/r for r in emitted if r.endswith('.pkl'))
  with prop.open('rb') as f:properties=pickle.load(f)
  require('item4' not in properties,'native properties key collision')
  properties['item4']={'schema':'item4-private-scoring/v1','cache_bytes':read_verified(input_root,sources['cache']).read_bytes(),
       'cache_info':{k:sources['cache'][k] for k in ('sha256','bytes')},
       'truth_nifti':(raw/'labelsTr'/f'{case}.nii.gz').read_bytes(),
       'qc':json.loads((stage/'qc'/f'{case}.json').read_bytes())}
  with prop.open('wb') as f:pickle.dump(properties,f,protocol=4)
  files=[]
  for rel in emitted:
   write_once(root,rel,(stage/rel).read_bytes());files.append(rel)
 commit_step(root,contract,'native-'+case,files)
def preprocess(input_root,output_root,contract):
 plan,rt,sel=bound_plan(contract,True)
 environment_check(plan['environment_requirements']);_load_science()
 arm=_arm(plan,sel);manifest=_input_manifest(input_root,contract,sel);splits=load_frozen_partitions(contract)
 cases=sorted(c for s in splits for c in s['val'])
 require(set(manifest['cases'])==set(cases),'source membership mismatch')
 root=Path(output_root).resolve();root.mkdir(parents=True,exist_ok=True)
 completed=contract.setdefault('completed_steps',{});known=verify_completed(root,completed)
 require({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}==set(known),'uncommitted preprocessing bytes present')
 require(set(completed)<={'shared'}|{'native-'+c for c in cases},'unknown completed step')
 require(not completed or 'shared' in completed,'case step without shared plans')
 if 'shared' not in completed:_shared_publish(input_root,root,contract,manifest,arm,splits,sel)
 for case in cases:
  if 'native-'+case not in completed:_case_publish(input_root,root,contract,case,manifest['cases'][case],arm,sel)
 return validate_preprocessing(root,contract)
def _private_scoring(properties):
 payload=properties.get('item4',{})
 require(payload.get('schema')=='item4-private-scoring/v1','private scoring provenance missing')
 b=payload['cache_bytes'];info=payload['cache_info']
 require(isinstance(b,bytes) and info=={'sha256':sha_bytes(b),'bytes':len(b)},'embedded original cache changed')
 qc=payload['qc']
 require(qc['source_cache_dice']>=.999 and 400<=qc['brain_ml']<=2500,'case QC failed')
 require(all(math.isfinite(x['prepared_sd']) and x['prepared_sd']>=1e-6 for x in qc['channels'].values()),'prepared channel QC failed')
 require(isinstance(payload['truth_nifti'],bytes) and payload['truth_nifti'],'source truth missing')
 return payload
def validate_preprocessing(output_root,contract):
 plan,rt,sel=bound_plan(contract,True);_load_science();arm=_arm(plan,sel)
 splits=load_frozen_partitions(contract);cases=sorted(c for s in splits for c in s['val'])
 files=verify_completed(output_root,contract.get('completed_steps',{}));root=Path(output_root).resolve()
 require(set(contract['completed_steps'])=={'shared'}|{'native-'+c for c in cases},'incomplete preprocessing steps')
 require(len(files)==300 and set(files)=={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()},'exact 300-file closure required')
 _,pre=_prepared_paths(root,arm)
 require((pre/'splits_final.json').read_bytes()==canonical(splits),'split bytes differ')
 metadata=json.loads((pre/'dataset.json').read_bytes())['item4']
 require(metadata=={'arm':arm,'preprocessing_id':sel['id'],'input_contract_sha256':sel['input_contract_sha256'],'source_capture_sha256':sel['source_capture_sha256'],'split_sha256':sel['split_sha256']},'preparation identity mismatch')
 from nnunetv2.utilities.plans_handling.plans_handler import PlansManager
 from nnunetv2.training.dataloading.nnunet_dataset import infer_dataset_class
 pm=PlansManager(str(pre/(sel['plans_name']+'.json')));cfg=pm.get_configuration('3d_fullres')
 require(list(cfg.normalization_schemes)==['NoNormalization']*(12 if arm=='A1_multiwin' else 6),'native normalization changed')
 folder=pre/cfg.data_identifier;dataset=infer_dataset_class(str(folder))(str(folder))
 require(len(dataset.identifiers)==len(cases) and set(dataset.identifiers)==set(cases),'native membership mismatch')
 for case in cases:
  loaded=dataset.load_case(case);data=np.asarray(loaded[0][:]);seg=np.asarray(loaded[1][:]);props=loaded[-1]
  require(data.ndim==4 and data.shape[0]==(12 if arm=='A1_multiwin' else 6),'native channels')
  require(seg.shape[1:]==data.shape[1:] and np.isfinite(data).all() and np.isfinite(seg).all(),'native arrays')
  require(np.isin(seg,[-1,0,1]).all() and 'class_locations' in props,'native labels/properties')
  _private_scoring(props)
 meta={'plans_sha256':file_info(pre/(sel['plans_name']+'.json'))['sha256']}
 return preprocessing_receipts(root,contract,sel,meta,cases,pre,folder,files)
def preprocessing_receipts(root,contract,sel,meta,cases,pre,folder,committed):
 rt=contract['runtime']; root=Path(root)
 case_files={}
 for case in cases:
  members={}
  for role,bases in {'image':[case+'.b2nd',case+'.npy',case+'.npz'],
      'segmentation':[case+'_seg.b2nd',case+'_seg.npy',case+'_seg.npz'],
      'properties':[case+'.pkl']}.items():
   matches=[folder/b for b in bases if (folder/b).is_file()]
   require(len(matches)==1,'native receipt member missing or ambiguous')
   q=matches[0];members[role]=dict(path=q.relative_to(root).as_posix(),**file_info(q))
  case_files[case]=members
 shared={k:dict(path=q.relative_to(root).as_posix(),**file_info(q)) for k,q in
   {'dataset':pre/'dataset.json','plans':pre/(sel['plans_name']+'.json'),'splits':pre/'splits_final.json'}.items()}
 files={d['path']:{k:d[k] for k in ('sha256','bytes')} for group in [*case_files.values(),shared] for d in group.values()}
 require(files==committed,'U2 native receipt excludes auxiliary outputs; packaging repair required')
 module_sha=rt['execution']['module_sha256']
 require(module_sha==sha_bytes(Path(__file__).read_bytes()),'validator module mismatch')
 require(shared['plans']['sha256']==meta['plans_sha256'] and shared['splits']['sha256']==sel['split_sha256'],'shared receipt hash mismatch')
 identities={'cohort_sha256':sel['cohort_sha256'],'input_contract_sha256':sel['input_contract_sha256'],'environment_sha256':contract['preprocessing']['environment_sha256'],'preprocessing_code_sha256':module_sha}
 proposed=dict(identities,schema='modal-item4-preprocessed/v1',status='VALIDATED',source_capture_sha256=sel['source_capture_sha256'],plans_sha256=meta['plans_sha256'],case_files=case_files,shared_files=shared)
 validation=dict(identities,schema='modal-preprocessing-validation/v1',status='PASS',errors=[],run_id=rt['run_id'],spec_sha256=rt['spec_sha256'],validator_sha256=module_sha,files=files)
 return {'proposed':proposed,'validation':validation}
def timing_record(fit_id,records,comparability_id):
 require(records,'no measured epochs')
 epochs=[r['epoch'] for r in records]
 require(len(epochs)==len(set(epochs)) and all(type(e) is int and e>=0 for e in epochs),'duplicate epoch measurements')
 require(epochs==list(range(epochs[0],epochs[0]+len(epochs))),'nonconsecutive epoch measurements')
 require(all(type(r.get('training_iterations')) is int and r['training_iterations']==250 and type(r.get('validation_iterations')) is int and r['validation_iterations']==50 for r in records),'actual completed epoch counts missing or wrong')
 require(all(math.isfinite(r['elapsed']) and r['elapsed']>0 and math.isfinite(r['loader_wait']) and 0<=r['loader_wait']<=r['elapsed'] for r in records),'invalid measured durations')
 wait=sum(r['loader_wait'] for r in records); elapsed=sum(r['elapsed'] for r in records)
 require(wait/elapsed<=.10,'loader bottleneck; comparable benchmark refused')
 return {'schema':'experiment-epoch-timing/v1','fit_id':fit_id,'completed_epochs':len(records),'elapsed_training_seconds':elapsed,'real_epoch':True,'loader_not_bottleneck':True,'comparability_id':comparability_id,'measured_loader_wait_seconds':wait,'epoch_records':records}
def _trainer_class():
 from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
 class TimedIterator:
  def __init__(self,inner,owner): self.inner=inner; self.owner=owner
  def __iter__(self): return self
  def __next__(self):
   t=time.perf_counter(); value=next(self.inner); self.owner._loader_wait+=time.perf_counter()-t; return value
  def __getattr__(self,k): return getattr(self.inner,k)
 class ReviewedTrainer(nnUNetTrainer):
  def __init__(self,plans,configuration,fold,dataset_json,device):
   super().__init__(plans,configuration,fold,dataset_json,device); self._measurements=[]; self._loader_wait=0.; self._loaded_epoch=None
  def get_dataloaders(self):
   a,b=super().get_dataloaders(); return TimedIterator(a,self),TimedIterator(b,self)
  def train_step(self,batch):
   result=super().train_step(batch); self._train_batches+=1; return result
  def validation_step(self,batch):
   result=super().validation_step(batch); self._val_batches+=1; return result
  def load_checkpoint(self,filename_or_checkpoint):
   super().load_checkpoint(filename_or_checkpoint)
   require(self.current_epoch>=0 and self.optimizer is not None,'resume did not restore native epoch/optimizer')
   require(self.current_epoch==0 or self.optimizer.state_dict()['state'],'trained checkpoint lacks optimizer state')
   self._loaded_epoch=int(self.current_epoch)
  def on_epoch_start(self):
   import torch
   torch.cuda.synchronize(); self._epoch_t=time.perf_counter(); self._loader_wait=0.
   self._measured_epoch=int(self.current_epoch); self._train_batches=0; self._val_batches=0; super().on_epoch_start()
  def on_epoch_end(self):
   import torch
   super().on_epoch_end()
   torch.cuda.synchronize(); elapsed=time.perf_counter()-self._epoch_t
   require(self._train_batches==250 and self._val_batches==50,'incomplete actual epoch work')
   rec={'epoch':self._measured_epoch,'elapsed':elapsed,'loader_wait':self._loader_wait,'training_iterations':self._train_batches,'validation_iterations':self._val_batches}
   self.print_to_log_file('ITEM4_EPOCH '+canonical(rec).decode().strip(),add_timestamp=False)
   self._measurements.append(rec)
 return ReviewedTrainer
def _score_native(input_root,trainer,arm,fold,splits,private_root):
 raw,pre=_prepared_paths(input_root,'A1_repeat' if arm=='A1_repeat2' else arm)
 plans=trainer.plans_manager.plans
 require(plans['image_reader_writer']=='SimpleITKIO','unreviewed probability axis order')
 records=[]; validation=Path(trainer.output_folder)/'validation'
 for case in splits[fold]['val']:
  segimg=nib.load(str(validation/f'{case}.nii.gz')); seg=np.asanyarray(segimg.dataobj)>.5
  with np.load(validation/f'{case}.npz',allow_pickle=False) as z:
   p=np.transpose(z['probabilities'][1].astype(np.float32),(2,1,0))
  require(p.shape==seg.shape and np.isfinite(p).all() and ((p>=0)&(p<=1)).all(),'native probability format invalid')
  require(dice(p>.5,seg)>=.99,'native probabilities disagree with segmentation')
  cc=_fit_cache(pre,trainer,case,private_root)
  pred=resample_from_to(nib.Nifti1Image(seg.astype(np.uint8),segimg.affine),(cc['shape'],cc['affine']),order=0).get_fdata()>.5
  prob=resample_from_to(nib.Nifti1Image(p,segimg.affine),(cc['shape'],cc['affine']),order=1).get_fdata().astype(np.float32)
  row=patient_scores(cc,prob[cc['mask']],pred)
  fp=int((pred & ~cc['lesion_full'] & cc['mask']).sum()); tn=int((~pred & ~cc['lesion_full'] & cc['mask']).sum())
  row['specificity']=tn/(tn+fp) if tn+fp else None
  row.update(case=case,fold=fold,shuffle=101)
  require(all(math.isfinite(row[k]) for k in ('dice','lesion_f1','abs_vol_err_ml','signed_vol_err_ml')),'nonfinite primary score')
  records.append({k:(None if isinstance(v,(float,np.floating)) and not math.isfinite(v) else v.item() if isinstance(v,np.generic) else v) for k,v in row.items()})
 require(len(records)==len(splits[fold]['val']),'incomplete heldout scoring')
 Path(private_root,'heldout-scores.json').write_bytes(canonical(records))
 metrics={}
 for k in ('dice','lesion_f1','abs_vol_err_ml','signed_vol_err_ml','precision','recall','specificity','asd_mm','fm_auroc','fm_avg_precision','lesion_ml_outside_mask'):
  vals=[float(r[k]) for r in records if r.get(k) is not None and math.isfinite(r[k])]
  metrics[k]={'n_defined':len(vals),'mean':sum(vals)/len(vals) if vals else None}
 return {'n_heldout':len(records),'fold':fold,'metrics':metrics,'exploratory':True,'uncertainty':'Per-fold means only; whole-cohort patient bootstrap requires all five frozen folds. No training variance estimate.'}
def _fit_payload(pre,trainer,case):
 import pickle
 folder=pre/trainer.configuration_manager.data_identifier
 with (folder/(case+'.pkl')).open('rb') as f:return _private_scoring(pickle.load(f))
def _fit_cache(pre,trainer,case,private_root):
 payload=_fit_payload(pre,trainer,case);p=Path(private_root)/'scoring'/f'{case}.npz'
 if p.exists():require(file_info(p)==payload['cache_info'],'private scoring cache changed')
 else:write_once(private_root,p.relative_to(private_root).as_posix(),payload['cache_bytes'])
 return load_cache(str(p),config_hash(FEATURE_CFG),case)
def _fit_truth(pre,trainer,cases,work):
 base=Path(work)/'native-inputs';base.mkdir(exist_ok=True)
 raw=(pre/'dataset.json').read_bytes();meta=json.loads(raw)
 fingerprint=meta['item4_fingerprint']
 require(isinstance(fingerprint,dict) and fingerprint,'native fingerprint missing')
 for name,b in [('dataset.json',raw),('splits_final.json',(pre/'splits_final.json').read_bytes()),('dataset_fingerprint.json',canonical(fingerprint))]:
  p=base/name
  if p.exists():require(p.read_bytes()==b,'private native input changed')
  else:write_once(base,name,b)
 trainer.preprocessed_dataset_folder_base=str(base)
 folder=base/'gt_segmentations';folder.mkdir(exist_ok=True)
 for case in cases:
  b=_fit_payload(pre,trainer,case)['truth_nifti'];p=folder/f'{case}.nii.gz'
  if p.exists():require(p.read_bytes()==b,'private truth changed')
  else:write_once(base,p.relative_to(base).as_posix(),b)
 trainer.gt_segmentations_folder=str(folder)
def fit_resources(rt,fit):
 r=rt.get('resources')
 require(isinstance(r,dict) and set(r)=={'gpu','cpu','memory_mib','timeout_seconds'},'resource fields')
 require(all(type(r[k]) is int for k in ('cpu','memory_mib','timeout_seconds')),'resource types')
 require(r['cpu']==16 and r['memory_mib']==131072 and 1<=r['timeout_seconds']<=86400,'unmatched CPU/RAM/timeout')
 require(r['gpu'] in ('A100-80GB','H100','B200'),'unsupported GPU')
 if fit['fit_id'].startswith('benchmark-'):
  require(r['gpu']==fit['fit_id'].removeprefix('benchmark-'),'benchmark GPU mismatch')
 return r['gpu']
def main(input_root,output_root,contract):
 plan,rt,sel=bound_plan(contract); environment_check(plan['environment_requirements']); _load_science()
 fit=next(x for x in plan['fits'] if x['fit_id']==rt['experiment']['fit_id'])
 progress=contract['progress']; work=Path(progress.root).resolve()/'work'; work.mkdir(exist_ok=True)
 out=Path(output_root).resolve(); out.mkdir(parents=True,exist_ok=True)
 require(not list(out.iterdir()) and not work.is_relative_to(out) and not out.is_relative_to(work),'fresh aggregate output root required')
 segment=rt['experiment']['segment']; require(type(segment) is int and segment>=1,'invalid segment')
 require((segment==1 and not rt.get('resume')) or (segment>1 and rt.get('resume')),'linked resume evidence missing or unexpected')
 arm='A1_repeat' if fit['arm']=='A1_repeat2' else fit['arm']
 require(arm not in ('A1_zscore','A1_histeq'),'U3 coverage held')
 raw,pre=_prepared_paths(input_root,arm)
 meta=json.loads((pre/'dataset.json').read_bytes())['item4']
 fit_binding=rt['progress']['fit_binding']
 require(meta['preprocessing_id']==fit['preprocessing_id'] and meta['input_contract_sha256']==sel['input_contract_sha256'],'fit consumes different preprocessing')
 meta=dict(meta,plans_sha256=file_info(pre/(sel['plans_name']+'.json'))['sha256'])
 require(meta['plans_sha256']==fit_binding['plans_sha256'],'runtime plans not frozen to preprocessing')
 split_bytes=(pre/'splits_final.json').read_bytes(); require(sha_bytes(split_bytes)==sel['split_sha256'],'fit split bytes changed')
 splits=json.loads(split_bytes)
 _native_paths(Path(input_root)/'raw',Path(input_root)/'preprocessed',work/'native-results')
 import torch
 require(torch.cuda.is_available(),'native GPU required')
 trainer=_trainer_class()(dict(json.loads((pre/(sel['plans_name']+'.json')).read_bytes()),continue_training=segment>1),'3d_fullres',fit['fold'],json.loads((pre/'dataset.json').read_bytes()),device=torch.device('cuda',0))
 Path(trainer.output_folder).mkdir(parents=True,exist_ok=True)
 trainer.log_file=str(work/f'training_log_{segment}.txt')
 Path(trainer.log_file).touch(mode=0o600,exist_ok=False)
 trainer.num_epochs=1 if fit['fit_id'].startswith('benchmark-') else 5 if fit['stage']=='SMOKE' else 250
 require(trainer.num_iterations_per_epoch==250 and trainer.num_val_iterations_per_epoch==50,'native epoch workload changed')
 expected_gpu=fit_resources(rt,fit)
 name=torch.cuda.get_device_name(0)
 require(expected_gpu.split('-')[0] in name and (expected_gpu!='A100-80GB' or torch.cuda.get_device_properties(0).total_memory>=79*1024**3),'physical GPU differs from bound benchmark')
 _fit_truth(pre,trainer,splits[fit['fold']]['val'],work)
 from orchestrator.modal_nnunet import run_fit
 native_receipt=run_fit(trainer,progress,initial=(segment==1),save_every=1 if fit['stage']=='SMOKE' else 10,segment=segment,interruption=rt.get('resume'))
 require(trainer.current_epoch==trainer.num_epochs,'native training incomplete')
 final_path,final_record=progress.select('final')
 require(file_info(final_path)['sha256']==native_receipt['final_sha256']==final_record['sha256'],'durable native final checkpoint mismatch')
 require(final_record['metadata']['next_epoch']==trainer.num_epochs,'durable final epoch mismatch')
 losses=[trainer.logger.get_value('train_losses',step=i) for i in range(trainer.num_epochs)]
 require(len(losses)>=trainer.num_epochs and all(math.isfinite(float(x)) for x in losses),'missing/nonfinite native loss history')
 measured={}
 for log_path in sorted(work.glob('training_log_*.txt')):
  require(not log_path.is_symlink(),'native timing log symlink')
  for line in log_path.read_text().splitlines():
   if line.startswith('ITEM4_EPOCH '):
    rec=json.loads(line.removeprefix('ITEM4_EPOCH ')); epoch=rec['epoch']
    require(epoch not in measured,'duplicate durable epoch timing')
    measured[epoch]=rec
 require(set(measured)==set(range(trainer.num_epochs)),'missing durable timing for completed native epochs')
 trainer._measurements=[measured[k] for k in sorted(measured)]
 require(all(r['training_iterations']==250 and r['validation_iterations']==50 for r in trainer._measurements),'incomparable epoch work')
 comparable=plan['full_training']['benchmark_comparability_id'] if fit['fit_id'].startswith('benchmark-') else 'same-arm-selected-gpu-full99-fold0-v1'
 timing=timing_record(fit['fit_id'],trainer._measurements,comparable)
 timing.update(total_native_epochs=int(trainer.current_epoch),gpu=expected_gpu,physical_cpus=rt['resources']['cpu'],memory_gib=rt['resources']['memory_mib']/1024,segment=segment)
 if 'native-resume' in fit['validation_checks']:
  require(segment>1 and trainer._loaded_epoch is not None and 0<trainer._loaded_epoch<trainer.num_epochs,'smoke requires real interrupted linked native resume')
 summary=_score_native(input_root,trainer,fit['arm'],fit['fold'],splits,work)
 summary.update(run_id=RUN_ID,preprocessing_id=fit['preprocessing_id'],input_contract_sha256=sel['input_contract_sha256'],source_capture_sha256=sel['source_capture_sha256'],environment_sha256=fit_binding['environment_sha256'],aggregate_output_only=True,fit_id=fit['fit_id'],native_epochs=int(trainer.current_epoch),finite_loss_count=len(losses),plans_sha256=meta['plans_sha256'],split_sha256=sel['split_sha256'],loaded_native_epoch=trainer._loaded_epoch)
 files={}
 for rel,obj in [('metrics.json',summary),('epoch-timing.json',timing)]:
  b=canonical(obj); require(len(b)<=1500000,'aggregate file too large'); files[rel]=write_once(out,rel,b)
 evidence={'input-bindings':['metrics.json'],'native-training':['metrics.json'],'finite-loss':['metrics.json'],'epoch-timing':['epoch-timing.json'],'heldout-scoring':['metrics.json'],'private-output-boundary':['metrics.json'],'benchmark-comparability':['epoch-timing.json'],'native-resume':['metrics.json']}
 require(set(fit['validation_checks'])<=set(evidence) and len(fit['validation_checks'])==len(set(fit['validation_checks'])),'unknown/duplicate check')
 require(set(fit['outputs'])==set(files)|{'validation.json'},'output contract mismatch')
 validation={'schema':'experiment-validation/v1',**{k:rt[k] for k in ('run_id','spec_sha256','code_sha256','execution_plan_sha256')},'fit_id':rt['experiment']['fit_id'],'files':files,'checks':[{'id':k,'status':'PASS','evidence':evidence[k]} for k in fit['validation_checks']]}
 write_once(out,'validation.json',canonical(validation))
 require({p.name for p in out.iterdir()}==set(fit['outputs']),'extra output')
 return None
def aggregate_screen(tables,held):
 _load_science()
 required=set(CANDIDATES)|{'A1_ct_maps_cta','A1_repeat','A1_repeat2','A1_pnorm_v2'}
 require(set(tables)==required,'all prespecified arms and original baseline required; no selective report')
 for table in tables.values(): validate_full_folds(table,held)
 def contrast(a,b):
  x=tables[a][['case','fold','shuffle','dice']].merge(tables[b][['case','fold','shuffle','dice']],on=['case','fold','shuffle'],how='outer',validate='one_to_one',suffixes=('_a','_b')).sort_values(['fold','case'])
  require(len(x)==99 and not x.isna().any().any(),'incomplete paired cohort')
  d=(x.dice_a-x.dice_b).to_numpy(float); require(np.isfinite(d).all(),'nonfinite paired Dice')
  rng=np.random.default_rng(int(hashlib.sha256(('item4|'+a+'|'+b).encode()).hexdigest()[:8],16))
  means=d[rng.integers(0,99,size=(10000,99))].mean(axis=1)
  lo,hi=np.percentile(means,[.5,99.5])
  return [float(d.mean()),float(lo),float(hi)]
 results={}
 for a in CANDIDATES:
  vsbase=contrast(a,'A1_ct_maps_cta'); vsrepeat=contrast(a,'A1_repeat')
  results[a]={'candidate_minus_original':vsbase,'candidate_minus_repeat1':vsrepeat,'verdict':verdict_from_intervals(vsbase,vsrepeat),'repeat2_sensitivity':contrast(a,'A1_repeat2')}
 return {'family_size':5,'confidence_level':99.,'bootstrap_draws':10000,'primary':results,'noise_controls':{'repeat1_minus_original':contrast('A1_repeat','A1_ct_maps_cta'),'repeat2_minus_original':contrast('A1_repeat2','A1_ct_maps_cta'),'repeat2_minus_repeat1':contrast('A1_repeat2','A1_repeat')},'secondary_ct_increment':contrast('A1_pnormct','A1_pnorm_v2'),'limitations':'Exposed development cohort; intervals conditional on fitted models; shared training, model selection and unseeded training uncertainty omitted. Noise controls are not variance estimates. Secondary and repeat2 sensitivity intervals are exploratory.'}
def synthetic_tests():
 from unittest.mock import patch
 class ContractTests(unittest.TestCase):
  def partitions(self):
   members=[f'synthetic-{i:03d}' for i in range(99)]
   return {f'101_{k}':{'train':[x for i,x in enumerate(members) if i%5!=k],'held':[x for i,x in enumerate(members) if i%5==k]} for k in range(5)}
  def contract(self):
   p={'schema':'scientific-execution-plan/v2','run_id':RUN_ID,'dispatch_mode':'incremental','operator_scope_sha256':'101f869a822c4c713e71f7c9ce91514094978c11f2bf012234b9cab2c9971309','fits':[{'fit_id':'synthetic-fit','preprocessing_id':'synthetic-prep'}],'preprocessing':[{'schema':'declared-preprocessing-partitions/v1','id':'synthetic-prep','input_contract_sha256':None,'source_capture_sha256':None,'cohort_sha256':COHORT_SHA256,'split_sha256':SPLIT_SHA256,'partitions_sha256':PARTITIONS_SHA256,'environment_requirements_sha256':sha_bytes(canonical({})),'plans_name':'synthetic-only'}],'environment_requirements':{}}
   return {'execution_plan':p,'runtime':{'execution_plan_sha256':sha_bytes(canonical(p)),'run_id':RUN_ID,'spec_sha256':'a'*64,'code_sha256':'9'*64,'execution':{'module_sha256':sha_bytes(Path(__file__).read_bytes())},'experiment':{'fit_id':'synthetic-fit'}},'preprocessing':p['preprocessing'][0]}
  def test_native_private_inputs(self):
   import types
   with tempfile.TemporaryDirectory() as d:
    pre=Path(d)/'pre';work=Path(d)/'work';pre.mkdir();work.mkdir()
    for name,value in [('dataset.json',{'item4_fingerprint':{'synthetic':True}}),('splits_final.json',[{'train':['a'],'val':['b']}])]:write_once(pre,name,canonical(value))
    trainer=types.SimpleNamespace(preprocessed_dataset_folder='unchanged')
    with patch(__name__+'._fit_payload',return_value={'truth_nifti':b'synthetic truth'}):
     _fit_truth(pre,trainer,['b'],work);_fit_truth(pre,trainer,['b'],work)
     base=Path(trainer.preprocessed_dataset_folder_base)
     self.assertEqual((base/'gt_segmentations/b.nii.gz').read_bytes(),b'synthetic truth')
  def test_missing_each_original_binding(self):
   for key in ('input_contract_sha256','source_capture_sha256'):
    c=self.contract(); row=c['execution_plan']['preprocessing'][0]
    row['input_contract_sha256']='1'*64;row['source_capture_sha256']='2'*64;row[key]=None
    c['runtime']['execution_plan_sha256']=sha_bytes(canonical(c['execution_plan']))
    with self.subTest(key=key),self.assertRaisesRegex(PrerequisiteError,key):bound_plan(c,True)
  def test_native_selection_preserves_declared_plan(self):
   c=self.contract(); row=c['execution_plan']['preprocessing'][0]
   row['input_contract_sha256']='1'*64; row['source_capture_sha256']='2'*64
   c['runtime']['execution_plan_sha256']=sha_bytes(canonical(c['execution_plan']))
   native={k:v for k,v in row.items() if k!='environment_requirements_sha256'}
   native.update(schema='reviewed-preprocessing-partitions/v1',environment_sha256='3'*64)
   c['preprocessing']=native; c['runtime']['environment_sha256']='3'*64
   before=canonical(c['execution_plan'])
   self.assertEqual(bound_plan(c,True)[2],row)
   self.assertEqual(canonical(c['execution_plan']),before)
   native['split_sha256']='4'*64
   with self.assertRaisesRegex(PrerequisiteError,'binding differs'):bound_plan(c,True)
  def test_exact_source_mapping_and_inventory(self):
   case='synthetic-case'
   with tempfile.TemporaryDirectory() as d:
    inv={}
    paths=list(source_paths(case).values())+[f'feature-cache-2mm-v2/{case}.npz','baseline/plans.json','baseline/handoff.json']
    for rel in paths:inv[rel]=write_once(d,rel,b'synthetic-source')
    pin=sha_bytes(json.dumps(inv,sort_keys=True,allow_nan=False).encode())
    mapped=source_inventory(d,[case],False,pin)
    self.assertEqual(set(mapped['cases'][case]),set(BASE6)|{'brain','lesion','cache'})
    self.assertEqual(mapped['baseline_plans']['path'],'baseline/plans.json')
    with self.assertRaisesRegex(PrerequisiteError,'binding changed'):source_inventory(d,[case],False,'0'*64)
    Path(d,'baseline/plans.json').write_bytes(b'changed')
    with self.assertRaisesRegex(PrerequisiteError,'binding changed'):source_inventory(d,[case],False,pin)
    Path(d,'extra').write_bytes(b'x')
    with self.assertRaisesRegex(PrerequisiteError,'extra paths'):source_inventory(d,[case],False,pin)
  def test_coverage_independent_selection(self):
   for arm in ('A1_repeat','A1_multiwin','A1_L','A1_pnormct','A1_pnorm_v2'):
    self.assertEqual(_arm({'fits':[{'arm':arm,'preprocessing_id':'p'}]},{'id':'p'}),arm)
   for arm in ('A1_zscore','A1_histeq'):
    with self.assertRaisesRegex(PrerequisiteError,'U3 coverage held'):_arm({'fits':[{'arm':arm,'preprocessing_id':'p'}]},{'id':'p'})
  def test_coverage_hold_is_unconditional(self):
   for sentinel in (0,-1000,None):
    with self.assertRaisesRegex(PrerequisiteError,'U3 coverage held'):derived_ctp_support(sentinel,None)
  def test_split_complete(self):
   d=split_document(self.partitions()); self.assertEqual([len(x['val']) for x in d],[20,20,20,20,19]); self.assertEqual(canonical(d),canonical(split_document(self.partitions())))
  def test_path_refusals(self):
   with tempfile.TemporaryDirectory() as d:
    for p in ('../escape','/absolute','a/../../escape'):
     with self.assertRaises(PrerequisiteError):rooted(d,p)
    Path(d,'link').symlink_to('/tmp')
    with self.assertRaises(PrerequisiteError):rooted(d,'link/file')
  def test_preprocess_missing_original_pins(self):
   with tempfile.TemporaryDirectory() as d:
    with self.assertRaisesRegex(PrerequisiteError,'unavailable original'):preprocess(d,d,self.contract())
    self.assertEqual(list(Path(d).iterdir()),[])
  def test_validate_refuses_missing_pins(self):
   with tempfile.TemporaryDirectory() as d:
    with self.assertRaisesRegex(PrerequisiteError,'unavailable original'):validate_preprocessing(d,self.contract())
  def test_plan_mutation(self):
   c=self.contract(); c['execution_plan']['dispatch_mode']='batch'
   with self.assertRaises(PrerequisiteError):bound_plan(c,True)
  def test_checkpoint_success_and_reuse(self):
   with tempfile.TemporaryDirectory() as d:
    calls=[]; c={'completed_steps':{},'checkpoint':lambda s,f:calls.append((s,f))}
    write_once(d,'new.json',b'{}\n'); info=commit_step(d,c,'synthetic-step',['new.json'])
    before=Path(d,'new.json').stat().st_mtime_ns
    self.assertEqual(verify_completed(d,c['completed_steps']),info)
    self.assertEqual(Path(d,'new.json').stat().st_mtime_ns,before);self.assertEqual(len(calls),1)
    with self.assertRaises(PrerequisiteError):commit_step(d,c,'synthetic-step',['new.json'])
  def test_checkpoint_corruption(self):
   with tempfile.TemporaryDirectory() as d:
    c={'checkpoint':lambda s,f:None};write_once(d,'f',b'first');commit_step(d,c,'step',['f']);Path(d,'f').write_bytes(b'other')
    with self.assertRaises(PrerequisiteError):verify_completed(d,c['completed_steps'])
  def test_timing_requires_measured_epochs(self):
   with self.assertRaises(PrerequisiteError):timing_record('synthetic',[],'c')
   with self.assertRaises(PrerequisiteError):timing_record('synthetic',[{'epoch':0,'elapsed':10.,'loader_wait':2.}],'c')
   with self.assertRaises(PrerequisiteError):timing_record('synthetic',[{'epoch':0,'elapsed':float('nan'),'loader_wait':0.}],'c')
   r=timing_record('synthetic',[{'epoch':0,'elapsed':10.,'loader_wait':.1,'training_iterations':250,'validation_iterations':50}],'c');self.assertEqual(r['completed_epochs'],1)
  def test_timing_work_and_sequence(self):
   base={'epoch':0,'elapsed':10.,'loader_wait':.1,'training_iterations':250,'validation_iterations':50}
   for edits in ({'training_iterations':249},{'validation_iterations':49},{'loader_wait':2.},{'elapsed':0.},{'elapsed':float('inf')},{'epoch':True}):
    with self.subTest(edits=edits), self.assertRaises(PrerequisiteError):timing_record('synthetic',[dict(base,**edits)],'c')
   for epochs in ([0,0],[0,2],[1,0]):
    with self.subTest(epochs=epochs), self.assertRaises(PrerequisiteError):timing_record('synthetic',[dict(base,epoch=e) for e in epochs],'c')
  def test_private_cache_corruption(self):
   payload={'schema':'item4-private-scoring/v1','cache_bytes':b'original','cache_info':{'sha256':sha_bytes(b'original'),'bytes':8},'truth_nifti':b'synthetic truth','qc':{'source_cache_dice':1.,'brain_ml':1000,'channels':{'x':{'prepared_sd':1.}}}}
   self.assertEqual(_private_scoring({'item4':payload}),payload)
   payload['cache_bytes']=b'changed'
   with self.assertRaisesRegex(PrerequisiteError,'cache changed'):_private_scoring({'item4':payload})
 class ScientificHelpers(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
   try:_load_science()
   except ModuleNotFoundError as e:raise unittest.SkipTest('Scientific libraries unavailable locally: '+e.name)
  def test_lesion_fixtures_preserved(self):
   f=_fx();self.assertEqual(f['both_empty'],(1.,0));self.assertEqual(f['truth_only'][0],0.);self.assertEqual(f['diagonal_contact_one_piece'],(1.,0));self.assertEqual(f['truth_one_pred_two_split'][1],1);self.assertAlmostEqual(f['one_matched_one_fp'][0],2/3);self.assertEqual(f['iou_0.2_boundary'][0],1.)
  def test_unverified_padding_cannot_generate_mask(self):
   brain=np.ones((2,2,2),bool)
   for value in (0.,-1000.,20.):
    with self.assertRaisesRegex(PrerequisiteError,'U3 coverage held'):derived_ctp_support(np.full((2,2,2,3),value),brain)
  def test_invalid_ctp(self):
   with self.assertRaises(PrerequisiteError):derived_ctp_support(np.zeros((2,2,2)),np.ones((2,2,2),bool))
  def test_support_finite_before_coercion(self):
   v=np.array([0.,np.nan,2.]);m=np.ones(3,bool);s,r=coverage_support(v,m,np.ones(3));self.assertEqual(s.tolist(),[True,False,True])
   x,r=zscore_in_brain(window01(v,0,2),s);self.assertEqual(x[1],0);self.assertEqual(r['n'],2)
  def test_degenerate_transform(self):
   x,r=histeq_in_brain(np.zeros(4),np.ones(4,bool));self.assertEqual(r['fallback'],'constant support');self.assertTrue(np.isfinite(x).all())
  def test_conjunctive_rule(self):
   self.assertEqual(verdict_from_intervals([.1,.01,.2],[.2,.1,.3]),'better')
   self.assertEqual(verdict_from_intervals([-.1,-.2,-.01],[-.2,-.3,-.1]),'worse')
   self.assertEqual(verdict_from_intervals([.1,0,.2],[.2,.1,.3]),'no clear difference')
   self.assertEqual(verdict_from_intervals([.1,.01,.2],[.2,.1,.3],False),'provisional')
   with self.assertRaises(ValueError):verdict_from_intervals([.1,float('nan'),.2],[.2,.1,.3])
  def test_pnorm_ct_does_not_require_ctp(self):
   shape=(30,30,30); grid=np.linspace(1.,40.,np.prod(shape)).reshape(shape); a={k:grid.copy() for k in BASE6};a['brain']=np.ones(shape);a['tmax']=grid/6
   x,qc=transform_case(a,'A1_pnormct');y,_=transform_case(a,'A1_pnorm_v2')
   for k in PERF_KINDS:self.assertTrue(np.array_equal(x[k],y[k]))
   self.assertFalse(np.array_equal(x['ncct'],y['ncct']))
 suite=unittest.TestSuite()
 suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ContractTests))
 suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ScientificHelpers))
 return suite
def _synthetic_plans():
 cfg={'data_identifier':'synthetic','preprocessor_name':'DefaultPreprocessor','batch_size':2,
  'patch_size':[16,16,16],'median_image_size_in_voxels':[16,16,16],'spacing':[1.,1.,1.],
  'normalization_schemes':['NoNormalization']*6,'use_mask_for_norm':[False]*6,
  'resampling_fn_data':'resample_data_or_seg_to_shape','resampling_fn_seg':'resample_data_or_seg_to_shape',
  'resampling_fn_probabilities':'resample_data_or_seg_to_shape','resampling_fn_data_kwargs':{'is_seg':False,'order':3,'order_z':0,'force_separate_z':None},
  'resampling_fn_seg_kwargs':{'is_seg':True,'order':1,'order_z':0,'force_separate_z':None},
  'resampling_fn_probabilities_kwargs':{'is_seg':False,'order':1,'order_z':0,'force_separate_z':None},'batch_dice':False,
  'architecture':{'network_class_name':'dynamic_network_architectures.architectures.unet.ResidualEncoderUNet',
  'arch_kwargs':{'n_stages':3,'features_per_stage':[4,8,16],'conv_op':'torch.nn.modules.conv.Conv3d',
   'kernel_sizes':[[3,3,3]]*3,'strides':[[1,1,1],[2,2,2],[2,2,2]],'n_blocks_per_stage':[1,1,1],
   'n_conv_per_stage_decoder':[1,1],'conv_bias':True,'norm_op':'torch.nn.modules.instancenorm.InstanceNorm3d',
   'norm_op_kwargs':{'eps':1e-5,'affine':True},'dropout_op':None,'dropout_op_kwargs':None,
   'nonlin':'torch.nn.LeakyReLU','nonlin_kwargs':{'inplace':True}},
  '_kw_requires_import':['conv_op','norm_op','dropout_op','nonlin']}}
 plans={'dataset_name':'Dataset999_Synthetic','plans_name':'SyntheticPlans','image_reader_writer':'SimpleITKIO',
  'transpose_forward':[0,1,2],'transpose_backward':[0,1,2],'configurations':{'3d_fullres':cfg},
  'label_manager':'LabelManager','foreground_intensity_properties_per_channel':{}}
 dataset={'channel_names':{str(i):'noNorm' for i in range(6)},'labels':{'background':0,'infarct':1},'numTraining':2,'file_ending':'.nii.gz'}
 return plans,dataset
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
