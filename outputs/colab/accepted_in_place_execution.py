K_DJ='dataset.json'
K_AR='A1_repeat'
K_AZ='A1_zscore'
K_F='fallback'
K_AH='A1_histeq'
K_3F='3d_fullres'
K_MM='memory_mib'
K_P='preprocessing'
K_E='experiment'
K_ACMC='A1_ct_maps_cta'
K_SFJ='splits_final.json'
K_MJ='metrics.json'
K_NE='next_epoch'
K_AM='A1_multiwin'
K_R='resources'
K_AP='A1_pnormct'
K_EP='execution_plan'
K_V='validation'
K_LF='lesion_full'
K_MS='module_sha256'
K_BH='baseline_handoff'
K_BPJ='baseline/plans.json'
K_BHJ='baseline/handoff.json'
K_NS='normalization_schemes'
K_C='configurations'
K_N='NoNormalization'
K_ST='synthetic.txt'
K_DPPV='declared-preprocessing-partitions/v1'
K_EPS='execution_plan_sha256'
K_PCS='preprocessing_code_sha256'
K_DFJ='dataset_fingerprint.json'
K_LNB='loader_not_bottleneck'
K_PN='plans_name'
K_ICS='input_contract_sha256'
K_SS='split_sha256'
K_PI='preprocessing_id'
K_ES='environment_sha256'
K_SCS='source_capture_sha256'
K_LW='loader_wait'
K_PS='plans_sha256'
K_TS='timeout_seconds'
K_CS='cohort_sha256'
K_ERS='environment_requirements_sha256'
K_TI='training_iterations'
K_VI='validation_iterations'
K_ER='environment_requirements'
K_VC='validation_checks'
K_FIPPC='foreground_intensity_properties_per_channel'
from pathlib import Path
import hashlib,json,math,os,time,unittest,tempfile,copy,importlib
BASE_PLANS_SHA256='532aa8160bf0db6c83ceeb0c1456d3bf6f2f7b528cdb0a9586866ac724de92d0'
BASE_HANDOFF_SHA256='5a5649e12a568ce99c8c2b4abd88732d07a862d44c32da9f1ddfc599699ddb01'
RUN_ID='colab-1ad5fafc220b3d65f576ce08'
PARTITIONS_SHA256='2c197a9addf40af4d75dd220a095b62130b0ca58ffbe5dce8eb73dff570f64f8'
COHORT_SHA256='45c5746f60e2275383a2c4f4096295fe7a171da85a73737c5a35a8cc6fc9fe86'
SPLIT_SHA256='d339296ca3b1672fc744e14188b36c1860b379a38b807eca67d8b73038007c86'
ARMS_ORDER=(K_AR,'A1_repeat2',K_AZ,K_AH,K_AM,'A1_L',K_AP,'A1_pnorm_v2')
CANDIDATES=(K_AZ,K_AH,K_AM,'A1_L',K_AP)
WINDOWS={'ncct':(0,80),'cbf':(0,35),'cbv':(0,10),'mtt':(0,20),'tmax':(0,7),'cta':(0,90),'ncct_w2':(20,50),'cbf_w2':(0,100),'cbv_w2':(0,4),'mtt_w2':(0,12),'tmax_w2':(0,20),'cta_w2':(0,300)}
BASE6=('ncct','cbf','cbv','mtt','tmax','cta')
PERF_KINDS=('cbf','cbv','mtt','tmax')
ZSCORE_MIN_SD=0.01
HISTEQ_BINS=256
VOXEL_MM=(2.0,2.0,2.0)
PNORM_NN={'min_ref_voxels':20000,'min_scale':{'cbf':0.7,'cbv':0.2,'mtt':0.4,'tmax':0.14,'ncct':1.6},'clip_z':5.0}
FEATURE_CFG={'target_mm':2.0,'vessel_pct':98.0,'core_thr':0.3,'penumbra_tmax':6.0,'schema':'isles24-features-2mm-v2'}
import glob,traceback,uuid
CACHE_SCHEMA='isles24-features-2mm-v2'
FEATURE_NAMES=['cbf','cbv','mtt','tmax','ncct_hu','rel_cbf','rel_tmax','rel_hu','tissue_class','z_cbf','z_cbv','z_tmax','z_hu','dist_occlusion_mm','affected_side','core_rule','penumbra_rule','local_mean_tmax','local_std_tmax','local_mean_relcbf','slice_pos']
import os,json,time,glob,uuid,datetime
COLAB_RUN_ID='colab-1ad5fafc220b3d65f576ce08'
BASE_INPUT_SHA256='b84b5f872711720d16b6d7f8858b3bff65a0543ff0580195eaf228f20878c0b2'
import types
TRAINER_SOURCE_SHA256="7096efb2040135eb60df3c8bf39cdbcc373e299671fcee365b3aff2f4da4dfbd"

def config_hash(cfg: dict) -> str:
    """Short stable hash of the settings that change what a cache file contains."""
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:12]
def dice(a, b):
    a, b = a.astype(bool), b.astype(bool)
    s = a.sum() + b.sum()
    return 1.0 if s == 0 else float(2.0 * (a & b).sum() / s)
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
def _fx():
    z = lambda: np.zeros((6, 6, 3), bool); out = {}
    t = z(); p = z(); out["both_empty"] = official_lesion_metrics(t, p)[:2]
    t = z(); t[1:3, 1:3, 1] = 1; p = z(); out["truth_only"] = official_lesion_metrics(t, p)[:2]
    t = z(); t[0, 0, 0] = 1; t[1, 1, 1] = 1; p = z(); p[0, 0, 0] = 1; p[1, 1, 1] = 1; out["diagonal_contact_one_piece"] = official_lesion_metrics(t, p)[:2]
    t = z(); t[0:4, 0:4, 1] = 1; p = z(); p[0:2, 0:4, 1] = 1; p[3:4, 0:4, 1] = 1; out["truth_one_pred_two_split"] = official_lesion_metrics(t, p)[:2]
    t = z(); t[0:2, 0:6, 1] = 1; p = z(); p[0:2, 0:6, 1] = 1; p[3:5, 0:6, 1] = 1; out["one_matched_one_fp"] = official_lesion_metrics(t, p)[:2]
    t = z(); t[0:5, 0, 0] = 1; p = z(); p[0:1, 0, 0] = 1; out["iou_0.2_boundary"] = official_lesion_metrics(t, p)[:2]
    return out
def coverage_support(values,brain,coverage=None):
 values=np.asarray(values)
 brain=np.asarray(brain,dtype=bool)
 if values.shape!=brain.shape:
  raise ValueError('brain shape mismatch')
 support=brain&np.isfinite(values)
 if coverage is not None:
  coverage=np.asarray(coverage)
  if coverage.shape!=values.shape or not np.isfinite(coverage).all()or(not np.isin(coverage,[0,1]).all()):
   raise ValueError('invalid spatial coverage mask')
  support&=coverage.astype(bool)
 return(support,{'coverage_known':coverage is not None,'brain_n':int(brain.sum()),'support_n':int(support.sum()),'nonfinite_in_brain':int((brain&~np.isfinite(values)).sum())})
def zscore_in_brain(x,brain):
 x=np.asarray(x,dtype=float)
 support,_=coverage_support(x,brain)
 v=x[support]
 out=np.zeros_like(x,dtype=np.float32)
 m,s=(float(v.mean()),float(v.std()))if v.size else(0.0,0.0)
 su=max(s,ZSCORE_MIN_SD)
 rec={'mean':m,'sd':s,'sd_used':su,'n':int(v.size),'fallback':None}
 if not v.size or s<1e-06:
  rec['fallback']='empty support'if not v.size else'constant support'
  return(out,rec)
 out[support]=(v-m)/su
 rec.update({'fallback':'SD floored'if s<ZSCORE_MIN_SD else None,'z_min':float(out[support].min()),'z_max':float(out[support].max())})
 return(out,rec)
def histeq_in_brain(x,brain,nbins=None):
 x=np.asarray(x,dtype=float)
 support,_=coverage_support(x,brain)
 v=x[support]
 out=np.zeros_like(x,dtype=np.float32)
 if not v.size or float(v.std())<1e-06:
  return(out,{'fallback':'empty support'if not v.size else'constant support','n':int(v.size)})
 if np.any((v<0)|(v>1)):
  raise ValueError('histogram input must be windowed to [0,1]')
 bins=HISTEQ_BINS if nbins is None else nbins
 hist,edges=np.histogram(v,bins=bins,range=(0.0,1.0))
 cdf=np.cumsum(hist).astype(float)
 cdf/=cdf[-1]
 out[support]=np.interp(v,(edges[:-1]+edges[1:])/2,cdf)
 return(out,{'fallback':None,'n':int(v.size),'share_at_window_floor':float((v<=1e-06).mean()),'share_at_window_ceiling':float((v>=1-1e-06).mean())})

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
class PrerequisiteError(RuntimeError):
 pass
def canonical(obj):
 return(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('utf-8')
def sha_bytes(b):
 return hashlib.sha256(b).hexdigest()
def file_info(path):
 p=Path(path)
 h=hashlib.sha256()
 n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):
   h.update(b)
   n+=len(b)
 return{'sha256':h.hexdigest(),'bytes':n}
def need(test,message):
 if not test:
  raise PrerequisiteError(message)
def digest(value):
 return isinstance(value,str)and len(value)==64 and all((c in'0123456789abcdef'for c in value))
def rooted(root,relative):
 root=Path(root).resolve()
 r=Path(relative)
 need(not r.is_absolute()and r.parts and('..'not in r.parts),'E001')
 p=root/r
 need(p.resolve().is_relative_to(root),'E002')
 need(not any((x.is_symlink()for x in[p,*p.parents]if x!=root.parent)),'E003')
 return p
def read_verified(root,descriptor):
 need(set(descriptor)=={'path','sha256','bytes'},'E004')
 need(digest(descriptor['sha256'])and type(descriptor['bytes'])is int and(descriptor['bytes']>0),'E005')
 p=root.read(descriptor)if isinstance(root,DriveInputs)else rooted(root,descriptor['path'])
 need(file_info(p)=={k:descriptor[k]for k in('sha256','bytes')},'E006')
 return p
def write_once(root,rel,data):
 p=rooted(root,rel)
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:
  f.write(data)
 return file_info(p)
def split_document(partitions,expected_count=99):
 need(isinstance(partitions,dict),'E007')
 keys=[k for k in partitions if k.startswith('101_')]
 need(set(keys)=={f'101_{k}'for k in range(5)},'E008')
 out=[]
 held=[]
 for k in range(5):
  row=partitions[f'101_{k}']
  tr=row['train']
  va=row['held']
  need(isinstance(tr,list)and isinstance(va,list)and tr and va,'E026')
  need(all((isinstance(x,str)and x and('/'not in x)and('\\'not in x)and(x not in('.','..'))for x in tr+va)),'E027')
  need(len(tr)==len(set(tr))and len(va)==len(set(va))and(not set(tr)&set(va)),'E028')
  out.append({'train':sorted(tr),'val':sorted(va)})
  held+=va
 need(len(held)==len(set(held))==expected_count,'E009')
 for row in out:
  need(set(row['train'])==set(held)-set(row['val']),'E029')
 return out
def bound_plan(contract,preprocessing=False):
 plan=contract[K_EP]
 rt=contract['runtime']
 need(plan.get('operator_scope_sha256')=='101f869a822c4c713e71f7c9ce91514094978c11f2bf012234b9cab2c9971309','E010')
 need(plan['schema']=='scientific-execution-plan/v2'and plan['run_id']==RUN_ID and(plan['dispatch_mode']=='incremental'),'E011')
 need(sha_bytes(canonical(plan))==rt[K_EPS],'E012')
 need(rt['run_id']==RUN_ID and digest(rt['spec_sha256'])and(rt.get('execution',{}).get(K_MS)==sha_bytes(Path(__file__).read_bytes())),'E013')
 if preprocessing:
  supplied=contract.get(K_P)
  need(isinstance(supplied,dict)and isinstance(supplied.get('id'),str),'E030')
  eid=supplied['id']
 else:
  selected=[x for x in plan['fits']if x['fit_id']==rt[K_E]['fit_id']]
  need(len(selected)==1,'E031')
  eid=selected[0][K_PI]
 rows=[x for x in plan[K_P]if x.get('id')==eid]
 need(len(rows)==1,'E014')
 sel=rows[0]
 fields={'schema','id',K_ICS,K_ERS,K_SS,K_PN,K_CS,K_SCS,'partitions_sha256'}
 need(set(sel)==fields and sel['schema']==K_DPPV,'E015')
 missing=[k for k in(K_ICS,K_SCS,K_CS,K_SS,K_ERS)if not digest(sel.get(k))]
 need(not missing,'unavailable original prerequisite bindings: '+', '.join(missing))
 need(sel['partitions_sha256']==PARTITIONS_SHA256 and sel[K_CS]==COHORT_SHA256 and(sel[K_SS]==SPLIT_SHA256),'E016')
 need(sel[K_ERS]==sha_bytes(canonical(plan[K_ER])),'E017')
 if preprocessing:
  shared=fields-{'schema',K_ERS}
  need(all((supplied.get(k)==sel[k]for k in shared)),'E032')
  if supplied.get('schema')==K_DPPV:
   need(supplied==sel,'E035')
  else:
   need(supplied.get('schema')=='reviewed-preprocessing-partitions/v1','E036')
   need(set(supplied)==shared|{'schema',K_ES},'E037')
   need(digest(supplied.get(K_ES))and supplied[K_ES]==rt.get(K_P,{K_ES:rt.get(K_ES)}).get(K_ES),'E038')
 return(plan,rt,sel)
def environment_check(requirements):
 import sys
 from importlib.metadata import version
 need(f'{sys.version_info.major}.{sys.version_info.minor}'==requirements['python'],'E018')
 for package,wanted in requirements['packages'].items():
  need(version(package)==wanted,'package requirement mismatch: '+package)
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
   need(isinstance(info,dict)and set(info)=={'sha256','bytes'}and digest(info['sha256'])and(type(info['bytes'])is int)and(info['bytes']>0),'E039')
   need(rel not in known,'E040')
   need(file_info(rooted(output_root,rel))==info,'E041')
   known[rel]=info
 return known
def commit_step(root,contract,step,files):
 need(step not in contract.get('completed_steps',{}),'E020')
 old=verify_completed(root,contract.get('completed_steps',{}))
 need(files and(not set(files)&set(old)),'E021')
 records={r:file_info(rooted(root,r))for r in sorted(files)}
 contract['checkpoint'](step,records)
 contract.setdefault('completed_steps',{})[step]=records
 return records
def load_frozen_partitions(contract):
 f=contract['frozen_partitions']
 need(f['sha256']==PARTITIONS_SHA256,'E022')
 parts=metadata_file(contract,f)
 splits=split_document(parts)
 need(sha_bytes(canonical(splits))==SPLIT_SHA256,'E024')
 return splits
def derived_ctp_support(ctp,brain):
 raise PrerequisiteError('U3 coverage held: registered CTP padding/support not authenticated for the cohort')
def pnorm_reference(maps,brain):
 all_zero=np.logical_and.reduce([np.where(np.isfinite(maps[k]),maps[k],0)==0 for k in PERF_KINDS])
 t=maps['tmax']
 return([('brain with Tmax <= 6 s',brain&np.isfinite(t)&(t>=0)&(t<=6)&~all_zero),('whole brain',brain&~all_zero)],all_zero)
def normalize_channel(v,kind,levels,brain,invalid):
 out,rec=_pnorm_channel(v,kind,levels,brain)
 invalid=invalid|~np.isfinite(v)|(v<=0 if kind in('cbf','cbv','mtt')else v<0)
 return(np.where(brain&~invalid,out,0).astype(np.float32),rec)
def transform_case(arrays,arm):
 need(arm in ARMS_ORDER,'unknown arm')
 brain=arrays['brain']>0.5
 maps={k:arrays[k]for k in BASE6}
 outputs={}
 qc={}
 need(brain.any()and all((v.shape==brain.shape for v in maps.values())),'E025')
 coverage=None
 if arm in(K_AZ,K_AH):
  coverage=derived_ctp_support(arrays['ctp'],brain)
 pref=pnorm_reference(maps,brain)if arm in(K_AP,'A1_pnorm_v2')else None
 channels=BASE6+tuple((k+'_w2'for k in BASE6))if arm==K_AM else BASE6
 for ch in channels:
  k=ch.removesuffix('_w2')
  v=maps[k]
  support,record=coverage_support(v,brain,coverage if k in PERF_KINDS else None)
  x=window01(v,*WINDOWS[ch])
  raw=v[brain&np.isfinite(v)]
  record.update(clip_low=float(np.mean(raw<=WINDOWS[ch][0]))if raw.size else None,clip_high=float(np.mean(raw>=WINDOWS[ch][1]))if raw.size else None)
  if arm in(K_AZ,K_AH):
   x,r=zscore_in_brain(x,support)if arm==K_AZ else histeq_in_brain(x,support)
   record.update(r)
   need(r.get(K_F)not in('empty support','constant support'),'E042')
  elif pref is not None and(k in PERF_KINDS or(arm==K_AP and k=='ncct')):
   levels=pref[0]if k in PERF_KINDS else[('whole finite nonnegative brain',brain)]
   x,r=normalize_channel(v,k,levels,brain,pref[1]if k in PERF_KINDS else np.zeros(brain.shape,bool))
   record.update(r)
  x=(x*brain).astype(np.float32)
  need(np.isfinite(x).all()and float(x[brain].std())>=1e-06,'E034')
  outputs[ch]=x
  record['prepared_sd']=float(x[brain].std())
  qc[ch]=record
 return(outputs,qc)
def validate_full_folds(table,held):
 if set(held)!=set(range(5)):
  raise ValueError('expected frozen folds 0 through 4')
 expected=[(c,k,101)for k in range(5)for c in held[k]]
 if any((len(held[k])==0 for k in range(5)))or len(expected)!=99:
  raise ValueError('expected 99 members in five nonempty folds')
 members=[r[0]for r in expected]
 if len(set(members))!=99:
  raise ValueError('duplicate or overlapping frozen members')
 if not{'case','fold','shuffle'}.issubset(table.columns):
  raise ValueError('membership columns missing')
 keys=table[['case','fold','shuffle']]
 if len(keys)!=99 or keys.isna().any().any()or keys.case.duplicated().any():
  raise ValueError('missing, extra, null or duplicate rows')
 if set(keys.itertuples(index=False,name=None))!=set(expected):
  raise ValueError('row membership, fold or shuffle mismatch')
def verdict_from_intervals(base_ci,repeat_ci,complete=True):
 normalized=[]
 for ci in(base_ci,repeat_ci):
  try:
   if isinstance(ci,(str,bytes))or len(ci)!=3:
    raise ValueError('invalid interval')
   if any((hasattr(x,'__len__')and(not isinstance(x,(str,bytes)))for x in ci)):
    raise ValueError('invalid interval')
   arr=[float(x)for x in ci]
  except(ValueError,TypeError)as e:
   raise ValueError('invalid interval')from e
  if not all((math.isfinite(x)for x in arr))or not arr[1]<=arr[0]<=arr[2]:
   raise ValueError('malformed, reversed or nonfinite interval')
  normalized.append(arr)
 base_ci,repeat_ci=normalized
 if not complete:
  return'provisional'
 if base_ci[1]>0 and repeat_ci[1]>0:
  return'better'
 if base_ci[2]<0 and repeat_ci[2]<0:
  return'worse'
 return'no clear difference'
def source_paths(case,with_ctp=False):
 need(isinstance(case,str)and case and('/'not in case)and('\\'not in case)and(case not in('.','..')),'E043')
 d=f'train/derivatives/{case}'
 paths={k:f'{d}/ses-01/perfusion-maps/{case}_ses-01_space-ncct_{k}.nii.gz'for k in PERF_KINDS}
 paths.update(ncct=f'train/raw_data/{case}/ses-01/{case}_ses-01_ncct.nii.gz',cta=f'{d}/ses-01/{case}_ses-01_space-ncct_cta.nii.gz',lesion=f'{d}/ses-02/{case}_ses-02_space-ncct_lesion-msk.nii.gz',brain=f'brainmask/{case}_brainmask.nii.gz')
 if with_ctp:
  paths['ctp']=f'{d}/ses-01/{case}_ses-01_space-ncct_ctp.nii.gz'
 return paths
def source_inventory(input_root,cases,with_ctp,expected_sha256):
 need(isinstance(input_root,DriveInputs)and not with_ctp,'explicit in-place base inputs required')
 expected={c:dict(source_paths(c,False),cache=f'feature-cache-2mm-v2/{c}.npz')for c in cases}
 inventory=input_root.inventory
 need(sha_bytes(json.dumps(inventory,sort_keys=True,allow_nan=False).encode())==expected_sha256,'E045')
 need(set(inventory)=={rel for row in expected.values()for rel in row.values()}|{K_BPJ,K_BHJ},'E044')
 need(not input_root.verify()['missing'],'missing required file')
 return{'cases':{c:{k:dict(path=rel,**inventory[rel])for k,rel in row.items()}for c,row in expected.items()},'baseline_plans':dict(path=K_BPJ,**inventory[K_BPJ]),K_BH:dict(path=K_BHJ,**inventory[K_BHJ])}
def _input_manifest(input_root,contract,sel):
 splits=load_frozen_partitions(contract)
 cases=sorted((c for fold in splits for c in fold['val']))
 arms={f['arm']for f in contract[K_EP]['fits']if f[K_PI]==sel['id']}
 need(not arms&{K_AZ,K_AH},'U3 coverage held: no cohort-authenticated support definition')
 mapped=source_inventory(input_root,cases,False,sel[K_ICS])
 need(mapped['baseline_plans']['sha256']==BASE_PLANS_SHA256,'E046')
 need(mapped[K_BH]['sha256']==BASE_HANDOFF_SHA256,'E047')
 handoff=json.loads(read_verified(input_root,mapped[K_BH]).read_bytes())
 need(handoff['smoke']is False and sorted(handoff['cases'])==cases,'E048')
 need(handoff['arm']==K_ACMC and handoff['splits']==splits,'E049')
 need(handoff['source_inventory']=={'brain':'cad80ea68c35','cbf':'71905e6a3737','cbv':'678b1bfd5639','cta':'f3f200c85d00','lesion':'fbcfad347f52','mtt':'732e673174db','ncct':'b5137a3f1df6','tmax':'71fb01614363'},'E050')
 return mapped
def _native_paths(raw,pre,results):
 os.environ.update(nnUNet_raw=str(raw),nnUNet_preprocessed=str(pre),nnUNet_results=str(results),nnUNet_n_proc_DA=os.environ.get('COLAB_DA_WORKERS','2'))
def _load_case_sources(input_root,sources,arm):
 needed=set(BASE6)|{'brain','lesion','cache'}
 if arm in(K_AZ,K_AH):
  needed.add('ctp')
 need(set(sources)==needed,'E051')
 paths={k:read_verified(input_root,sources[k])for k in needed}
 ref=nib.load(str(paths['ncct']))
 arrays={}
 for k in needed-{'cache'}:
  img=nib.load(str(paths[k]))
  arr=np.asanyarray(img.dataobj)
  if k!='ctp'and arr.ndim==4 and(arr.shape[-1]==1):
   arr=arr[...,0]
  need(arr.shape[:3]==ref.shape[:3]and np.allclose(img.affine,ref.affine,atol=0.001,rtol=0),'E080')
  need(arr.ndim==(4 if k=='ctp'else 3),'E081')
  arrays[k]=arr
 brain=arrays['brain']>0.5
 ml=float(brain.sum()*np.prod(ref.header.get_zooms()[:3])/1000)
 need(400<=ml<=2500,'E052')
 need(np.isfinite(arrays['brain']).all()and np.isfinite(arrays['lesion']).all(),'E053')
 return(ref,arrays,paths)
def _dataset_name(arm):
 return f'Dataset{731+ARMS_ORDER.index(arm):03d}_ISLES24_{arm}'
def _prepared_paths(root,arm):
 ds=_dataset_name(arm)
 return(Path(root)/'raw'/ds,Path(root)/'preprocessed'/ds)
def _case_raw(input_root,output_root,contract,case,sources,arm):
 need(time.perf_counter()<globals().get('_COLAB_DEADLINE',math.inf),'preprocessing wall limit')
 ref,arrays,paths=_load_case_sources(input_root,sources,arm)
 x,qc=transform_case(arrays,arm)
 cache=load_cache(str(paths['cache']),config_hash(FEATURE_CFG),case)
 truth=arrays['lesion']>0.5
 mapped=resample_from_to(nib.Nifti1Image(truth.astype(np.uint8),ref.affine),(cache['shape'],cache['affine']),order=0).get_fdata()>0.5
 need(dice(mapped,cache[K_LF])>=0.999,'E054')
 raw,pre=_prepared_paths(output_root,arm)
 written=[]
 for i,(ch,arr)in enumerate(x.items()):
  p=raw/'imagesTr'/f'{case}_{i:04d}.nii.gz'
  p.parent.mkdir(parents=True,exist_ok=True)
  need(not p.exists(),'E082')
  nib.save(nib.Nifti1Image(arr,ref.affine),str(p))
  written.append(p)
 p=raw/'labelsTr'/f'{case}.nii.gz'
 p.parent.mkdir(parents=True,exist_ok=True)
 need(not p.exists(),'E055')
 nib.save(nib.Nifti1Image(truth.astype(np.uint8),ref.affine),str(p))
 written.append(p)
 q=Path(output_root)/'qc'/f'{case}.json'
 write_once(output_root,q.relative_to(output_root).as_posix(),canonical({'channels':qc,'source_cache_dice':float(dice(mapped,cache[K_LF])),'brain_ml':float((arrays['brain']>0.5).sum()*np.prod(ref.header.get_zooms()[:3])/1000),'infarct_in_brain':float((truth&(arrays['brain']>0.5)).sum()/truth.sum())if truth.any()else 1.0}))
 written.append(q)
 return written
def _prepare_shared(input_root,output_root,contract,manifest,arm,splits,sel):
 from nnunetv2 .experiment_planning.dataset_fingerprint.fingerprint_extractor import DatasetFingerprintExtractor
 raw,pre=_prepared_paths(output_root,arm)
 ds=raw.name
 n=12 if arm==K_AM else 6
 dataset={'channel_names':{str(i):'noNorm'for i in range(n)},'labels':{'background':0,'infarct':1},'numTraining':99,'file_ending':'.nii.gz'}
 write_once(output_root,(raw/K_DJ).relative_to(output_root).as_posix(),canonical(dataset))
 DatasetFingerprintExtractor(ds,num_processes=2,verbose=False).run(overwrite_existing=False)
 bp=read_verified(input_root,manifest['baseline_plans'])
 bh=read_verified(input_root,manifest[K_BH])
 base=json.loads(bp.read_bytes())
 handoff=json.loads(bh.read_bytes())
 need(handoff['arm']==K_ACMC and handoff['splits']==splits,'E056')
 need(handoff['plans']==base,'E057')
 need(all((handoff['windows'][k]==list(WINDOWS[k])for k in BASE6)),'E058')
 need(handoff['smoke']is False and len(handoff['cases'])==99,'E059')
 if arm=='A1_L':
  from nnunetv2 .utilities.find_class_by_name import recursive_find_python_class
  import nnunetv2
  cls=recursive_find_python_class(str(Path(nnunetv2 .__file__).parent/'experiment_planning'),'nnUNetPlannerResEncL','nnunetv2.experiment_planning')
  need(cls is not None,'E083')
  planner=cls(ds)
  plans=planner.plan_experiment()
  need(plans[K_PN]==sel[K_PN],'E084')
 else:
  plans=copy.deepcopy(base)
  plans['dataset_name']=ds
  for cfg in plans[K_C].values():
   if K_NS in cfg:
    need(set(cfg[K_NS])=={K_N},'E092')
    cfg[K_NS]=[K_N]*n
   if'use_mask_for_norm'in cfg:
    cfg['use_mask_for_norm']=[False]*n
  fp=json.loads((pre/K_DFJ).read_bytes())
  if K_FIPPC in plans:
   plans[K_FIPPC]=fp[K_FIPPC]
  write_once(output_root,(pre/(sel[K_PN]+'.json')).relative_to(output_root).as_posix(),canonical(plans))
  for key in('patch_size','spacing','batch_size','architecture'):
   need(plans[K_C][K_3F][key]==base[K_C][K_3F][key],'E090')
 if not(pre/K_DJ).exists():
  write_once(output_root,(pre/K_DJ).relative_to(output_root).as_posix(),canonical(dataset))
 write_once(output_root,(pre/K_SFJ).relative_to(output_root).as_posix(),canonical(splits))
 write_once(output_root,'preparation.json',canonical({'arm':arm,'dataset':ds,K_PN:sel[K_PN],K_PS:file_info(pre/(sel[K_PN]+'.json'))['sha256'],K_PI:sel['id'],K_SS:sel[K_SS]}))
 return None
def _native_case(output_root,contract,case,arm,sel):
 from nnunetv2 .utilities.plans_handling.plans_handler import PlansManager
 raw,pre=_prepared_paths(output_root,arm)
 pm=PlansManager(str(pre/(sel[K_PN]+'.json')))
 cfg=pm.get_configuration(K_3F)
 worker=cfg.preprocessor_class(verbose=False)
 folder=pre/cfg.data_identifier
 folder.mkdir(parents=True,exist_ok=True)
 images=sorted((str(p)for p in(raw/'imagesTr').glob(case+'_*.nii.gz')))
 worker.run_case_save(str(folder/case),images,str(raw/'labelsTr'/f'{case}.nii.gz'),pm,cfg,json.loads((raw/K_DJ).read_bytes()))
 files=[p.relative_to(output_root).as_posix()for p in folder.glob(case+'.*')if p.is_file()]
 files+=[p.relative_to(output_root).as_posix()for p in folder.glob(case+'_seg.*')if p.is_file()]
 need(len(files)>=2,'E060')
 return files
def _arm(plan,sel):
 arms={f['arm']for f in plan['fits']if f[K_PI]==sel['id']}
 if arms=={K_AR,'A1_repeat2'}:
  return K_AR
 need(len(arms)==1,'E061')
 arm=next(iter(arms))
 need(arm not in(K_AZ,K_AH),'U3 coverage held')
 return arm
def _shared_publish(input_root,root,contract,manifest,arm,splits,sel):
 import shutil
 with tempfile.TemporaryDirectory(prefix='.staging-',dir=root)as td:
  stage=Path(td)
  _native_paths(stage/'raw',stage/'preprocessed',stage/'native-work')
  for case,sources in manifest['cases'].items():
   _case_raw(input_root,stage,contract,case,sources,arm)
  _prepare_shared(input_root,stage,contract,manifest,arm,splits,sel)
  _,src=_prepared_paths(stage,arm)
  _,dest=_prepared_paths(root,arm)
  dataset=json.loads((src/K_DJ).read_bytes())
  dataset['item4_fingerprint']=json.loads((src/K_DFJ).read_bytes())
  dataset['item4']={'arm':arm,K_PI:sel['id'],K_ICS:sel[K_ICS],K_SCS:sel[K_SCS],K_SS:sel[K_SS]}
  files=[]
  for name,raw in[(K_DJ,canonical(dataset)),(sel[K_PN]+'.json',(src/(sel[K_PN]+'.json')).read_bytes()),(K_SFJ,canonical(splits))]:
   rel=(dest/name).relative_to(root).as_posix()
   write_once(root,rel,raw)
   files.append(rel)
 commit_step(root,contract,'shared',files)
def _case_publish(input_root,root,contract,case,sources,arm,sel):
 import pickle
 with tempfile.TemporaryDirectory(prefix='.staging-',dir=root)as td:
  stage=Path(td)
  _native_paths(stage/'raw',stage/'preprocessed',stage/'native-work')
  _case_raw(input_root,stage,contract,case,sources,arm)
  raw,sp=_prepared_paths(stage,arm)
  _,pre=_prepared_paths(root,arm)
  for name in(K_DJ,sel[K_PN]+'.json'):
   write_once(stage,(sp/name).relative_to(stage).as_posix(),(pre/name).read_bytes())
  write_once(stage,(raw/K_DJ).relative_to(stage).as_posix(),(pre/K_DJ).read_bytes())
  emitted=_native_case(stage,contract,case,arm,sel)
  need(len(emitted)==3,'E085')
  prop=next((stage/r for r in emitted if r.endswith('.pkl')))
  with prop.open('rb')as f:
   properties=pickle.load(f)
  need('item4'not in properties,'E086')
  properties['item4']={'schema':'item4-private-scoring/v1','cache_bytes':read_verified(input_root,sources['cache']).read_bytes(),'cache_info':{k:sources['cache'][k]for k in('sha256','bytes')},'truth_nifti':(raw/'labelsTr'/f'{case}.nii.gz').read_bytes(),'qc':json.loads((stage/'qc'/f'{case}.json').read_bytes())}
  with prop.open('wb')as f:
   pickle.dump(properties,f,protocol=4)
  files=[]
  for rel in emitted:
   write_once(root,rel,(stage/rel).read_bytes())
   files.append(rel)
 commit_step(root,contract,'native-'+case,files)
def _preprocess(input_root,output_root,contract):
 plan,rt,sel=bound_plan(contract,True)
 environment_check(plan[K_ER])
 _load_science()
 arm=_arm(plan,sel)
 manifest=_input_manifest(input_root,contract,sel)
 splits=load_frozen_partitions(contract)
 cases=sorted((c for s in splits for c in s['val']))
 need(set(manifest['cases'])==set(cases),'E062')
 root=Path(output_root).resolve()
 root.mkdir(parents=True,exist_ok=True)
 completed=contract.setdefault('completed_steps',{})
 known=verify_completed(root,completed)
 need({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(known),'E063')
 need(set(completed)<={'shared'}|{'native-'+c for c in cases},'E064')
 need(not completed or'shared'in completed,'E065')
 if'shared'not in completed:
  _shared_publish(input_root,root,contract,manifest,arm,splits,sel)
 for case in cases:
  if'native-'+case not in completed:
   _case_publish(input_root,root,contract,case,manifest['cases'][case],arm,sel)
 return validate_preprocessing(root,contract)
def _private_scoring(properties):
 payload=properties.get('item4',{})
 need(payload.get('schema')=='item4-private-scoring/v1','E066')
 b=payload['cache_bytes']
 info=payload['cache_info']
 need(isinstance(b,bytes)and info=={'sha256':sha_bytes(b),'bytes':len(b)},'E067')
 qc=payload['qc']
 need(qc['source_cache_dice']>=0.999 and 400<=qc['brain_ml']<=2500,'E068')
 need(all((math.isfinite(x['prepared_sd'])and x['prepared_sd']>=1e-06 for x in qc['channels'].values())),'E069')
 need(isinstance(payload['truth_nifti'],bytes)and payload['truth_nifti'],'E070')
 return payload
def _validate_preprocessing(output_root,contract):
 plan,rt,sel=bound_plan(contract,True)
 _load_science()
 arm=_arm(plan,sel)
 splits=load_frozen_partitions(contract)
 cases=sorted((c for s in splits for c in s['val']))
 files=verify_completed(output_root,contract.get('completed_steps',{}))
 root=Path(output_root).resolve()
 need(set(contract['completed_steps'])=={'shared'}|{'native-'+c for c in cases},'E071')
 need(len(files)==300 and set(files)=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()},'E072')
 _,pre=_prepared_paths(root,arm)
 need((pre/K_SFJ).read_bytes()==canonical(splits),'E073')
 metadata=json.loads((pre/K_DJ).read_bytes())['item4']
 need(metadata=={'arm':arm,K_PI:sel['id'],K_ICS:sel[K_ICS],K_SCS:sel[K_SCS],K_SS:sel[K_SS]},'E074')
 from nnunetv2 .utilities.plans_handling.plans_handler import PlansManager
 from nnunetv2 .training.dataloading.nnunet_dataset import infer_dataset_class
 pm=PlansManager(str(pre/(sel[K_PN]+'.json')))
 cfg=pm.get_configuration(K_3F)
 need(list(cfg.normalization_schemes)==[K_N]*(12 if arm==K_AM else 6),'E075')
 folder=pre/cfg.data_identifier
 dataset=infer_dataset_class(str(folder))(str(folder))
 need(len(dataset.identifiers)==len(cases)and set(dataset.identifiers)==set(cases),'E076')
 for case in cases:
  loaded=dataset.load_case(case)
  data=np.asarray(loaded[0][:])
  seg=np.asarray(loaded[1][:])
  props=loaded[-1]
  need(data.ndim==4 and data.shape[0]==(12 if arm==K_AM else 6),'E087')
  need(seg.shape[1:]==data.shape[1:]and np.isfinite(data).all()and np.isfinite(seg).all(),'E088')
  need(np.isin(seg,[-1,0,1]).all()and'class_locations'in props,'E089')
  _private_scoring(props)
 meta={K_PS:file_info(pre/(sel[K_PN]+'.json'))['sha256']}
 return preprocessing_receipts(root,contract,sel,meta,cases,pre,folder,files)
def preprocessing_receipts(root,contract,sel,meta,cases,pre,folder,committed):
 rt=contract['runtime']
 root=Path(root)
 case_files={}
 for case in cases:
  members={}
  for role,bases in{'image':[case+'.b2nd',case+'.npy',case+'.npz'],'segmentation':[case+'_seg.b2nd',case+'_seg.npy',case+'_seg.npz'],'properties':[case+'.pkl']}.items():
   matches=[folder/b for b in bases if(folder/b).is_file()]
   need(len(matches)==1,'E091')
   q=matches[0]
   members[role]=dict(path=q.relative_to(root).as_posix(),**file_info(q))
  case_files[case]=members
 shared={k:dict(path=q.relative_to(root).as_posix(),**file_info(q))for k,q in{'dataset':pre/K_DJ,'plans':pre/(sel[K_PN]+'.json'),'splits':pre/K_SFJ}.items()}
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
 need(len(epochs)==len(set(epochs))and all((type(e)is int and e>=0 for e in epochs)),'E094')
 need(epochs==list(range(epochs[0],epochs[0]+len(epochs))),'E095')
 need(all((type(r.get(K_TI))is int and r[K_TI]==250 and(type(r.get(K_VI))is int)and(r[K_VI]==50)for r in records)),'E096')
 need(all((math.isfinite(r['elapsed'])and r['elapsed']>0 and math.isfinite(r[K_LW])and(0<=r[K_LW]<=r['elapsed'])for r in records)),'E097')
 wait=sum((r[K_LW]for r in records))
 elapsed=sum((r['elapsed']for r in records))
 need(wait/elapsed<=0.1,'E098')
 return{'schema':'experiment-epoch-timing/v1','fit_id':fit_id,'completed_epochs':len(records),'elapsed_training_seconds':elapsed,'real_epoch':True,K_LNB:True,'comparability_id':comparability_id,'measured_loader_wait_seconds':wait,'epoch_records':records}
def _trainer_class():
 from nnunetv2 .training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
 class TimedIterator:
  def __init__(s,inner,owner):
   s.inner=inner
   s.owner=owner
  def __iter__(s):
   return s
  def __next__(s):
   t=time.perf_counter()
   value=next(s.inner)
   s.owner._loader_wait+=time.perf_counter()-t
   return value
  def __getattr__(s,k):
   return getattr(s.inner,k)
 class ReviewedTrainer(nnUNetTrainer):
  def __init__(s,plans,configuration,fold,dataset_json,device):
   super().__init__(plans,configuration,fold,dataset_json,device)
   s._measurements=[]
   s._loader_wait=0.0
   s._loaded_epoch=None
  def get_dataloaders(s):
   a,b=super().get_dataloaders()
   return(TimedIterator(a,s),TimedIterator(b,s))
  def train_step(s,batch):
   need(time.perf_counter()<_COLAB_DEADLINE,'smoke wall limit')
   result=super().train_step(batch)
   s._train_batches+=1
   return result
  def validation_step(s,batch):
   need(time.perf_counter()<_COLAB_DEADLINE,'smoke wall limit')
   result=super().validation_step(batch)
   s._val_batches+=1
   return result
  def load_checkpoint(s,filename_or_checkpoint):
   super().load_checkpoint(filename_or_checkpoint)
   need(s.current_epoch>=0 and s.optimizer is not None,'E136')
   need(s.current_epoch==0 or s.optimizer.state_dict()['state'],'E137')
   s._loaded_epoch=int(s.current_epoch)
  def on_epoch_start(s):
   import torch
   need(time.perf_counter()<globals().get("_COLAB_DEADLINE",math.inf),"smoke wall limit")
   _synchronize_device(s.device)
   s._epoch_t=time.perf_counter()
   s._loader_wait=0.0
   s._measured_epoch=int(s.current_epoch)
   s._train_batches=0
   s._val_batches=0
   super().on_epoch_start()
  def on_epoch_end(s):
   import torch
   _synchronize_device(s.device)
   core=time.perf_counter()-s._epoch_t
   super().on_epoch_end()
   _synchronize_device(s.device)
   elapsed=time.perf_counter()-s._epoch_t
   need(s._train_batches==250 and s._val_batches==50,'E138')
   rec={'epoch':s._measured_epoch,'elapsed':elapsed,'core_synchronized_seconds':core,'native_seconds':float(s.logger.get_value('epoch_end_timestamps',step=-1)-s.logger.get_value('epoch_start_timestamps',step=-1)),K_LW:s._loader_wait,K_TI:s._train_batches,K_VI:s._val_batches}
   s.print_to_log_file('ITEM4_EPOCH '+canonical(rec).decode().strip(),add_timestamp=False)
   s._measurements.append(rec)
   if s.current_epoch==1 and os.environ.get("COLAB_SMOKE_INTERRUPT")=="1":raise SmokeInterruption("deliberate native checkpoint recovery test")
 return ReviewedTrainer
def _score_native(input_root,tr,arm,fold,splits,private_root):
 raw,pre=_prepared_paths(input_root,K_AR if arm=='A1_repeat2'else arm)
 plans=tr.plans_manager.plans
 need(plans['image_reader_writer']=='SimpleITKIO','E099')
 records=[]
 validation=Path(tr.output_folder)/K_V
 for case in splits[fold]['val']:
  segimg=nib.load(str(validation/f'{case}.nii.gz'))
  seg=np.asanyarray(segimg.dataobj)>0.5
  with np.load(validation/f'{case}.npz',allow_pickle=False)as z:
   p=np.transpose(z['probabilities'][1].astype(np.float32),(2,1,0))
  need(p.shape==seg.shape and np.isfinite(p).all()and((p>=0)&(p<=1)).all(),'E124')
  need(dice(p>0.5,seg)>=0.99,'E125')
  cc=_fit_cache(pre,tr,case,private_root)
  pred=resample_from_to(nib.Nifti1Image(seg.astype(np.uint8),segimg.affine),(cc['shape'],cc['affine']),order=0).get_fdata()>0.5
  prob=resample_from_to(nib.Nifti1Image(p,segimg.affine),(cc['shape'],cc['affine']),order=1).get_fdata().astype(np.float32)
  row=patient_scores(cc,prob[cc['mask']],pred)
  fp=int((pred&~cc[K_LF]&cc['mask']).sum())
  tn=int((~pred&~cc[K_LF]&cc['mask']).sum())
  row['specificity']=tn/(tn+fp)if tn+fp else None
  row.update(case=case,fold=fold,shuffle=101)
  need(all((math.isfinite(row[k])for k in('dice','lesion_f1','abs_vol_err_ml','signed_vol_err_ml'))),'E126')
  records.append({k:None if isinstance(v,(float,np.floating))and(not math.isfinite(v))else v.item()if isinstance(v,np.generic)else v for k,v in row.items()})
 need(len(records)==len(splits[fold]['val']),'E100')
 Path(private_root,'heldout-scores.json').write_bytes(canonical(records))
 metrics={}
 for k in('dice','lesion_f1','abs_vol_err_ml','signed_vol_err_ml','precision','recall','specificity','asd_mm','fm_auroc','fm_avg_precision','lesion_ml_outside_mask'):
  vals=[float(r[k])for r in records if r.get(k)is not None and math.isfinite(r[k])]
  metrics[k]={'n_defined':len(vals),'mean':sum(vals)/len(vals)if vals else None}
 return{'n_heldout':len(records),'fold':fold,'metrics':metrics,'exploratory':True,'uncertainty':'Fold0 only; full-cohort and training-variance inference unavailable.'}
def _fit_payload(pre,tr,case):
 import pickle
 folder=pre/tr.configuration_manager.data_identifier
 with(folder/(case+'.pkl')).open('rb')as f:
  return _private_scoring(pickle.load(f))
def _fit_cache(pre,tr,case,private_root):
 payload=_fit_payload(pre,tr,case)
 p=Path(private_root)/'scoring'/f'{case}.npz'
 if p.exists():
  need(file_info(p)==payload['cache_info'],'E127')
 else:
  write_once(private_root,p.relative_to(private_root).as_posix(),payload['cache_bytes'])
 return load_cache(str(p),config_hash(FEATURE_CFG),case)
def _fit_truth(pre,tr,cases,work):
 base=Path(work)/'native-inputs'
 base.mkdir(exist_ok=True)
 raw=(pre/K_DJ).read_bytes()
 meta=json.loads(raw)
 fingerprint=meta['item4_fingerprint']
 need(isinstance(fingerprint,dict)and fingerprint,'E101')
 for name,b in[(K_DJ,raw),(K_SFJ,(pre/K_SFJ).read_bytes()),(K_DFJ,canonical(fingerprint))]:
  p=base/name
  if p.exists():
   need(p.read_bytes()==b,'E139')
  else:
   write_once(base,name,b)
 tr.preprocessed_dataset_folder_base=str(base)
 folder=base/'gt_segmentations'
 folder.mkdir(exist_ok=True)
 for case in cases:
  b=_fit_payload(pre,tr,case)['truth_nifti']
  p=folder/f'{case}.nii.gz'
  if p.exists():
   need(p.read_bytes()==b,'E140')
  else:
   write_once(base,p.relative_to(base).as_posix(),b)
 tr.gt_segmentations_folder=str(folder)
def fit_resources(rt,fit):
 r=rt.get(K_R)
 need(isinstance(r,dict)and set(r)=={'gpu','cpu',K_MM,K_TS},'E102')
 need(all((type(r[k])is int for k in('cpu',K_MM,K_TS))),'E103')
 need(r['cpu']>=2 and r[K_MM]>=16384 and(1<=r[K_TS]<=7200),'E104')
 need(r['gpu']=='A100','E105')
 return r['gpu']
def _execute_fit(input_root,output_root,contract,config=None,mon=None):
 need(config is None and mon is None,'Colab has no diagnostic dispatch')
 plan,rt,sel=bound_plan(contract)
 environment_check(plan[K_ER])
 _load_science()
 fit=next((x for x in plan['fits']if x['fit_id']==rt[K_E]['fit_id']))
 progress=contract['progress']
 work=Path(progress.root).resolve()/'work'
 work.mkdir(exist_ok=True)
 out=Path(output_root).resolve()
 out.mkdir(parents=True,exist_ok=True)
 need(not list(out.iterdir())and(not work.is_relative_to(out))and(not out.is_relative_to(work)),'E106')
 segment=rt[K_E]['segment']
 need(type(segment)is int and segment>=1,'E107')
 need(segment==1 and(not rt.get('resume'))or(segment>1 and rt.get('resume')),'E108')
 arm=K_AR if fit['arm']=='A1_repeat2'else fit['arm']
 need(arm not in(K_AZ,K_AH),'U3 coverage held')
 raw,pre=_prepared_paths(input_root,arm)
 meta=json.loads((pre/K_DJ).read_bytes())['item4']
 fit_binding=rt['progress']['fit_binding']
 need(meta[K_PI]==fit[K_PI]and meta[K_ICS]==sel[K_ICS],'E109')
 meta=dict(meta,plans_sha256=file_info(pre/(sel[K_PN]+'.json'))['sha256'])
 need(meta[K_PS]==fit_binding[K_PS],'E110')
 split_bytes=(pre/K_SFJ).read_bytes()
 need(sha_bytes(split_bytes)==sel[K_SS],'E111')
 splits=json.loads(split_bytes)
 _native_paths(Path(input_root)/'raw',Path(input_root)/'preprocessed',work/'native-results')
 import torch
 need(torch.cuda.is_available(),'E112')
 tr=_trainer_class()(dict(json.loads((pre/(sel[K_PN]+'.json')).read_bytes()),continue_training=segment>1),K_3F,fit['fold'],json.loads((pre/K_DJ).read_bytes()),device=torch.device('cuda',0))
 Path(tr.output_folder).mkdir(parents=True,exist_ok=True)
 tr.log_file=str(work/f'training_log_{segment}.txt')
 Path(tr.log_file).touch(mode=384,exist_ok=False)
 tr.num_epochs=1 if fit['fit_id'].startswith('benchmark-')else 5 if fit['stage']=='SMOKE'else 250
 need(tr.num_iterations_per_epoch==250 and tr.num_val_iterations_per_epoch==50,'E113')
 expected_gpu=fit_resources(rt,fit)
 name=torch.cuda.get_device_name(0)
 need(expected_gpu.split('-')[0]in name and(expected_gpu!='A100-80GB'or torch.cuda.get_device_properties(0).total_memory>=79*1024**3),'E114')
 _fit_truth(pre,tr,splits[fit['fold']]['val'],work)
 native_start=time.perf_counter()
 native_receipt=run_fit(tr,progress,initial=segment==1,save_every=1 if fit['stage']=='SMOKE'else 10,segment=segment,interruption=rt.get('resume'))
 need(tr.current_epoch==tr.num_epochs,'E115')
 final_path,final_record=progress.select('final')
 need(file_info(final_path)['sha256']==native_receipt['final_sha256']==final_record['sha256'],'E116')
 need(final_record['metadata'][K_NE]==tr.num_epochs,'E117')
 losses=[tr.logger.get_value('train_losses',step=i)for i in range(tr.num_epochs)]
 need(len(losses)>=tr.num_epochs and all((math.isfinite(float(x))for x in losses)),'E118')
 measured={}
 for log_path in sorted(work.glob('training_log_*.txt')):
  need(not log_path.is_symlink(),'E129')
  for line in log_path.read_text().splitlines():
   if line.startswith('ITEM4_EPOCH '):
    rec=json.loads(line.removeprefix('ITEM4_EPOCH '))
    epoch=rec['epoch']
    need(epoch not in measured,'E141')
    measured[epoch]=rec
 need(set(measured)==set(range(tr.num_epochs)),'E119')
 tr._measurements=[measured[k]for k in sorted(measured)]
 need(all((r[K_TI]==250 and r[K_VI]==50 for r in tr._measurements)),'E120')
 comparable=plan['full_training']['benchmark_comparability_id']if fit['fit_id'].startswith('benchmark-')else'same-arm-selected-gpu-full99-fold0-v1'
 timing=timing_record(fit['fit_id'],tr._measurements,comparable)
 timing.update(total_native_epochs=int(tr.current_epoch),gpu=torch.cuda.get_device_name(0),requested_cpus=rt[K_R]['cpu'],requested_memory_gib=rt[K_R][K_MM]/1024,observed_cpu=cpu_capacity(),segment=segment)
 if'native-resume'in fit[K_VC]:
  need(segment>1 and tr._loaded_epoch is not None and(0<tr._loaded_epoch<=tr.num_epochs),'E130')
 scoring_start=time.perf_counter()
 summary=_score_native(input_root,tr,fit['arm'],fit['fold'],splits,work)
 summary.update(scoring_seconds=time.perf_counter()-scoring_start,run_id=RUN_ID,preprocessing_id=fit[K_PI],input_contract_sha256=sel[K_ICS],source_capture_sha256=sel[K_SCS],contract_environment_sha256=fit_binding[K_ES],observed_environment_sha256=contract['_observed_environment_sha256'],aggregate_output_only=True,fit_id=fit['fit_id'],native_epochs=int(tr.current_epoch),finite_loss_count=len(losses),plans_sha256=meta[K_PS],split_sha256=sel[K_SS],loaded_native_epoch=tr._loaded_epoch)
 files={}
 for rel,obj in[(K_MJ,summary),('epoch-timing.json',timing)]:
  b=canonical(obj)
  need(len(b)<=1500000,'E133')
  files[rel]=write_once(out,rel,b)
 evidence={'input-bindings':[K_MJ],'native-training':[K_MJ],'finite-loss':[K_MJ],'epoch-timing':['epoch-timing.json'],'heldout-scoring':[K_MJ],'private-output-boundary':[K_MJ],'benchmark-comparability':['epoch-timing.json'],'native-resume':[K_MJ]}
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
 for table in tables.values():
  validate_full_folds(table,held)
 def contrast(a,b):
  x=tables[a][['case','fold','shuffle','dice']].merge(tables[b][['case','fold','shuffle','dice']],on=['case','fold','shuffle'],how='outer',validate='one_to_one',suffixes=('_a','_b')).sort_values(['fold','case'])
  need(len(x)==99 and(not x.isna().any().any()),'E134')
  d=(x.dice_a-x.dice_b).to_numpy(float)
  need(np.isfinite(d).all(),'E135')
  rng=np.random.default_rng(int(hashlib.sha256(('item4|'+a+'|'+b).encode()).hexdigest()[:8],16))
  means=d[rng.integers(0,99,size=(10000,99))].mean(axis=1)
  lo,hi=np.percentile(means,[0.5,99.5])
  return[float(d.mean()),float(lo),float(hi)]
 results={}
 for a in CANDIDATES:
  vsbase=contrast(a,K_ACMC)
  vsrepeat=contrast(a,K_AR)
  results[a]={'candidate_minus_original':vsbase,'candidate_minus_repeat1':vsrepeat,'verdict':verdict_from_intervals(vsbase,vsrepeat),'repeat2_sensitivity':contrast(a,'A1_repeat2')}
 return{'family_size':5,'confidence_level':99.0,'bootstrap_draws':10000,'primary':results,'noise_controls':{'repeat1_minus_original':contrast(K_AR,K_ACMC),'repeat2_minus_original':contrast('A1_repeat2',K_ACMC),'repeat2_minus_repeat1':contrast('A1_repeat2',K_AR)},'secondary_ct_increment':contrast(K_AP,'A1_pnorm_v2'),'limitations':'Exposed development data; patient resampling omits training variance. Repeat2 and secondary are exploratory.'}
def _boundary_tests():
 class PreservedBoundaryTests(unittest.TestCase):
  def test_partitions(s):
   members=[f'synthetic-{i}'for i in range(99)]
   parts={f'101_{k}':{'train':[x for i,x in enumerate(members)if i%5!=k],'held':[x for i,x in enumerate(members)if i%5==k]}for k in range(5)}
   s.assertEqual(len(split_document(parts)),5)
   parts['101_0']['train'].append(parts['101_0']['held'][0])
   with s.assertRaises(PrerequisiteError):
    split_document(parts)
  def test_reuse_tamper(s):
   with tempfile.TemporaryDirectory()as d:
    info=write_once(d,K_ST,b'synthetic')
    complete={'shared':{K_ST:info}}
    s.assertEqual(verify_completed(d,complete),{K_ST:info})
    Path(d,K_ST).write_bytes(b'changed')
    with s.assertRaises(PrerequisiteError):
     verify_completed(d,complete)
  def test_paths(s):
   with tempfile.TemporaryDirectory()as d:
    for p in('../escape','/absolute'):
     with s.assertRaises(PrerequisiteError):
      rooted(d,p)
    write_once(d,'one',b'synthetic')
    with s.assertRaises(FileExistsError):
     write_once(d,'one',b'rewrite')
  def test_holds(s):
   with s.assertRaises(PrerequisiteError):
    derived_ctp_support(None,None)
   with s.assertRaises(PrerequisiteError):
    timing_record('synthetic',[],'synthetic')
  def test_verdict(s):
   s.assertEqual(verdict_from_intervals([0.1,0.01,0.2],[0.2,0.1,0.3]),'better')
   s.assertEqual(verdict_from_intervals([0.1,0.01,0.2],[-0.1,-0.2,0.1]),'no clear difference')
   s.assertEqual(verdict_from_intervals([0.1,0.01,0.2],[0.2,0.1,0.3],False),'provisional')
 return unittest.defaultTestLoader.loadTestsFromTestCase(PreservedBoundaryTests)
def cpu_capacity():
 count=os.cpu_count()
 affinity=len(os.sched_getaffinity(0))
 quota=None
 source=None
 p=Path('/sys/fs/cgroup/cpu.max')
 if p.is_file():
  q,period=p.read_text().split()
  quota=None if q=='max'else int(q)/int(period)
  source='cgroup-v2'
 else:
  p=Path('/sys/fs/cgroup/cpu/cpu.cfs_quota_us')
  q=Path('/sys/fs/cgroup/cpu/cpu.cfs_period_us')
  if p.is_file()and q.is_file():
   a=int(p.read_text())
   quota=None if a<0 else a/int(q.read_text())
   source='cgroup-v1'
 need(source is not None and count is not None and(affinity>0),'E146')
 return{'logical_cpu_count':count,'affinity_logical_cpus':affinity,'quota_cpu_equivalents':quota,'quota_source':source,'effective_logical_capacity':min(affinity,quota)if quota is not None else affinity}
def _synchronize_device(device):
 import torch
 if device.type=='cuda':
  torch.cuda.synchronize(device)
 else:
  need(device.type=='cpu','E163')
def colab_guard(contract):
 need(contract['runtime']['run_id']==COLAB_RUN_ID,'wrong Colab run')
 fit=next(x for x in contract[K_EP]['fits']if x['fit_id']==contract['runtime'][K_E]['fit_id'])
 need((fit['fit_id'],fit['arm'],fit['stage'],fit['fold'])==('smoke-A1_repeat','A1_repeat','SMOKE',0),'SMOKE_ONLY: full/other arms held')
 need(contract['runtime']['execution'][K_MS]==sha_bytes(Path(__file__).read_bytes()),'module changed')
 need(contract[K_EP][K_P][0][K_ICS]==BASE_INPUT_SHA256,'base inventory changed')
 full=[f for f in contract[K_EP]['fits']if f['stage']=='FULL']
 need(len(full)==40 and{(f['arm'],f['fold'])for f in full}=={(a,k)for a in ARMS_ORDER for k in range(5)},'full research plan changed')
 need(contract['colab']['seed']==101 and contract['colab']['epochs']==5 and contract['colab']['workers']==2,'smoke settings changed')
 need(contract['colab']['stage1_usd']==150 and contract['colab']['projection_usd']==1200 and contract['colab']['total_usd']==1275,'budget changed')
 need(contract['colab']['reviewed_package_sha256']==contract['colab']['expected_package_sha256']and digest(contract['colab']['expected_package_sha256']),'reviewed package unavailable')
 return fit
def membership_guard(contract):
 splits=load_frozen_partitions(contract)
 members={c for row in splits for c in row['val']}
 need(contract['colab']['development_manifest']['sha256']==COHORT_SHA256,'development manifest binding')
 dev=metadata_file(contract,contract['colab']['development_manifest'])
 excluded=metadata_file(contract,contract['colab']['exclusions'])
 need(len(dev['cases'])==len(set(dev['cases']))==99 and set(dev['cases'])==members,'positive membership failed')
 need(len(excluded['cases'])==len(set(excluded['cases']))==49 and not members&set(excluded['cases']),'exclusion membership failed')
 return splits
def preprocess(input_root,output_root,contract):
 colab_guard(contract);membership_guard(contract)
 need(str(input_root)==contract['colab']['metadata_root'],'input_root must be the metadata package, never a flat input copy')
 return _preprocess(in_place_inputs(contract),output_root,contract)
def validate_preprocessing(output_root,contract):
 colab_guard(contract);membership_guard(contract)
 return _validate_preprocessing(output_root,contract)
def main(input_root,output_root,contract):
 colab_guard(contract);membership_guard(contract);accounting_guard(contract)
 need(not in_place_inputs(contract).verify()['missing'],'inputs missing before training')
 validate_preprocessing(input_root,contract)
 import random,numpy as np,torch
 random.seed(101);np.random.seed(101);torch.manual_seed(101);torch.cuda.manual_seed_all(101)
 os.environ['COLAB_DA_WORKERS']='2'
 global _COLAB_DEADLINE
 started=time.perf_counter();_COLAB_DEADLINE=min(globals().get('_COLAB_DEADLINE',math.inf),started+7200)
 try:
  return _execute_fit(input_root,output_root,contract)
 finally:
  contract['progress'].receipt('colab-wall',{'seconds':time.perf_counter()-started,'cu_per_hour':None,'scientific_acceptance':False})
def synthetic_tests():
 class ColabChecks(unittest.TestCase):
  def test_full_refused(self):
   c={'runtime':{'run_id':COLAB_RUN_ID,K_E:{'fit_id':'full'}},K_EP:{'fits':[{'fit_id':'full','arm':'A1_repeat','stage':'FULL','fold':0}]}}
   with self.assertRaises(PrerequisiteError):main('/unavailable','/unavailable',c)
  def test_metric_fixtures(self):
   global np
   import numpy as np
   v=_fx()
   self.assertEqual(v['both_empty'],(1.,0));self.assertEqual(v['truth_only'][0],0.)
   self.assertEqual(v['diagonal_contact_one_piece'],(1.,0));self.assertEqual(v['truth_one_pred_two_split'][1],1)
   self.assertAlmostEqual(v['one_matched_one_fp'][0],2/3);self.assertEqual(v['iou_0.2_boundary'][0],1.)
 return unittest.TestSuite([_boundary_tests(),unittest.defaultTestLoader.loadTestsFromTestCase(ColabChecks),_drive_tests()])
class SmokeInterruption(RuntimeError):
 pass
class ColabProgress:
 def __init__(self,root,binding):
  self.root=Path(root).resolve();self.binding=binding;self.locked=False
 def _guard(self):
  need(self.locked,'writer lock required')
 def receipt(self,kind,detail):
  import uuid
  self._guard()
  write_once(self.root,'receipts/'+uuid.uuid4().hex+'.json',canonical({'kind':kind,'detail':detail,'binding':self.binding}))
 def publish(self,key,write,*,metadata):
  import uuid
  self._guard();need(key in('latest','best','final'),'checkpoint kind')
  rel='objects/'+uuid.uuid4().hex+'.pth';p=rooted(self.root,rel);p.parent.mkdir(exist_ok=True)
  t=time.perf_counter();write(p);written=time.perf_counter()
  with p.open('rb')as f:os.fsync(f.fileno())
  record=dict(file_info(p),path=rel,metadata=metadata,binding=self.binding)
  write_once(self.root,rel+'.json',canonical(record))
  tmp=self.root/(key+'.tmp');tmp.write_bytes(canonical(record));os.replace(tmp,self.root/(key+'.json'))
  need(file_info(p)=={k:record[k]for k in('sha256','bytes')},'checkpoint readback failed')
  self.receipt('checkpoint',dict(key=key,seconds=time.perf_counter()-t,native_write_seconds=written-t,readback_and_publication_seconds=time.perf_counter()-written,record=record))
  return record
 def select(self,key):
  self._guard();r=json.loads(rooted(self.root,key+'.json').read_bytes())
  need(r['binding']==self.binding,'resume binding changed')
  p=rooted(self.root,r['path']);need(file_info(p)=={k:r[k]for k in('sha256','bytes')},'checkpoint changed')
  need(json.loads(Path(str(p)+'.json').read_bytes())==r,'checkpoint receipt changed')
  return p,r
 def training_log(self,path,*,segment):
  need(Path(path).resolve().is_relative_to(self.root/'work'),'private log path')
  self.receipt('log',dict(segment=segment,path=str(path)))
 def writer(self,initial):
  from contextlib import contextmanager
  import fcntl
  @contextmanager
  def hold():
   self.root.mkdir(parents=True,exist_ok=True)
   with(self.root/'writer.lock').open('a')as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);self.locked=True
    try:
     identity=self.root/'identity.json'
     if initial:write_once(self.root,'identity.json',canonical(self.binding))
     else:need(json.loads(identity.read_bytes())==self.binding,'resume identity mismatch')
     yield self
    finally:self.locked=False;fcntl.flock(lock,fcntl.LOCK_UN)
  return hold()
def run_colab(contract_path,contract_sha256,input_root,output_root,resume,preflight_only=False):
 need(digest(contract_sha256)and file_info(checked_path(contract_path))['sha256']==contract_sha256,'reviewed contract missing/changed')
 c=strict_json(Path(contract_path).read_bytes());colab_guard(c);membership_guard(c)
 need(input_root==c['colab']['metadata_root'],'metadata root mismatch')
 root=checked_path(output_root,missing=True)
 for r in[input_root,*c['colab']['authorized_input_roots'].values()]:
  r=checked_path(r);need(not root.is_relative_to(r)and not r.is_relative_to(root),'output overlaps input')
 root.mkdir(parents=True,exist_ok=True)
 input_preflight(c,root)
 if preflight_only:
  print('Inputs verified; no training.');return
 accounting_guard(c)
 segment=c['runtime'][K_E]['segment']
 need(type(segment)is int and segment>=1 and(segment>1)==resume,'segment mismatch')
 env=actual_environment();environment_check(c[K_EP][K_ER]);verify_native_source()
 write_once(root,'attempt-'+str(segment)+'.json',canonical({'contract_sha256':contract_sha256,'resume':resume,'source_notebook_sha256':c['colab']['notebook_sha256']}))
 write_once(root,f'environment-{segment}.json',canonical(env))
 c['_observed_environment_sha256']=sha_bytes(canonical(env))
 write_once(root,f'config-{segment}.json',canonical(c))
 for j,reference in enumerate(c['colab']['preprocessing_references']):
  metadata_file(c,reference)
  write_once(root,f'historical-preprocessing-{segment}-{j}.json',Path(reference['path']).read_bytes())
 write_once(root,f'execution-{segment}.py',Path(__file__).read_bytes())
 cu_start(root,segment)
 global _COLAB_DEADLINE
 start=time.perf_counter();_COLAB_DEADLINE=start+min(7200,c['runtime'][K_R][K_TS])
 status='FAILED'
 try:
  prep=root/'prepared';steps=root/'steps';steps.mkdir(exist_ok=True)
  c['completed_steps']={p.stem:strict_json(p.read_bytes())for p in steps.glob('*.json')}
  c['checkpoint']=lambda name,files:write_once(steps,name+'.json',canonical(files))
  t=time.perf_counter();preparation=preprocess(input_root,prep,c)
  write_once(root,f'preprocessing-{segment}.json',canonical({'elapsed_seconds':time.perf_counter()-t,'result':preparation,'mode':'revalidated-resume'if resume else'current-Colab-preprocessing','observed_environment_sha256':c['_observed_environment_sha256'],'historical_references_are_current_execution':False}))
  progress=ColabProgress(root/'progress',c['runtime']['progress']['fit_binding']);c['progress']=progress
  os.environ['COLAB_SMOKE_INTERRUPT']='0'if resume else'1'
  with progress.writer(initial=not resume):
   try:
    main(prep,root/('segment-'+str(segment)),c);status='COMPLETE'
   except SmokeInterruption:
    status='INTERRUPTED';progress.receipt('deliberate-interruption',{'after_epochs':1,'automatic_retry':False})
 finally:
  write_once(root,f'wall-{segment}.json',canonical({'schema':'colab-wall/v1','status':status,'segment':segment,'elapsed_seconds':time.perf_counter()-start,'end_unix':time.time(),'scientific_acceptance':False}))
  private_return(root,segment,status)
 print('Return private artifacts/CU. FULL held; bound resume only.')
def private_return(root,segment,status):
 root=Path(root);files={}
 for p in root.rglob('*'):
  checked_path(str(p))
  if p.is_file():files[p.relative_to(root).as_posix()]=file_info(p)
 write_once(root,f'private-return-{segment}-{uuid.uuid4().hex}.json',canonical({'schema':'colab-private-return/v1','run_id':COLAB_RUN_ID,'segment':segment,'status':status,'files':files,'public_export':False,'scientific_acceptance':False}))
def file_hash(path):return file_info(path)["sha256"]
def verify_native_source():
 from importlib.metadata import version
 import inspect
 from nnunetv2 .training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
 if version('nnunetv2')!='2.8.1'or file_hash(inspect.getfile(nnUNetTrainer))!=TRAINER_SOURCE_SHA256:
  raise ValueError('NNUNET_NATIVE_SOURCE_CHANGED')
def run_fit(trainer,progress,*,initial,save_every,segment,interruption=None):
 verify_native_source()
 progress._guard()
 if type(save_every)is not int or save_every not in{1,5,10}:
  raise ValueError('NNUNET_CHECKPOINT_INTERVAL')
 if trainer.is_ddp or trainer.local_rank!=0 or trainer.disable_checkpointing:
  raise ValueError('NNUNET_SINGLE_FIT_CHECKPOINT_REQUIRED')
 if type(trainer.num_epochs)is not int or trainer.num_epochs<1:
  raise ValueError('NNUNET_EPOCH_BOUND')
 trainer.save_every=save_every
 original_save=trainer.save_checkpoint
 def durable_save(self,filename):
  name=Path(filename).name
  kinds={'checkpoint_latest.pth':'latest','checkpoint_best.pth':'best','checkpoint_final.pth':'final'}
  if name not in kinds:
   raise ValueError('NNUNET_CHECKPOINT_NAME')
  epoch=self.current_epoch+1
  if type(epoch)is not int or not 0<=epoch<=self.num_epochs:
   raise ValueError('NNUNET_CHECKPOINT_EPOCH')
  return progress.publish(kinds[name],lambda path:original_save(str(path)),metadata={'next_epoch':epoch,'total_epochs':self.num_epochs,'native_version':'2.8.1'})
 trainer.save_checkpoint=types.MethodType(durable_save,trainer)
 try:
  if initial:
   if trainer.current_epoch!=0:
    raise ValueError('NNUNET_INITIAL_EPOCH')
   trainer.initialize()
   trainer.current_epoch=-1
   try:
    trainer.save_checkpoint('checkpoint_latest.pth')
   finally:
    trainer.current_epoch=0
   mode,epoch='initial',0
  else:
   key='final'if(progress.root/'final.json').exists()else'latest'
   path,record=progress.select(key)
   meta=record['metadata']
   if(not isinstance(meta,dict)or set(meta)!={'next_epoch','total_epochs','native_version'}or type(meta['next_epoch'])is not int or not 0<=meta['next_epoch']<=trainer.num_epochs or meta['total_epochs']!=trainer.num_epochs or meta['native_version']!='2.8.1'or(key=='final'and meta['next_epoch']!=trainer.num_epochs)):
    raise ValueError('NNUNET_RESUME_METADATA')
   trainer.load_checkpoint(str(path))
   epoch=trainer.current_epoch
   if epoch!=meta['next_epoch']:
    raise ValueError('NNUNET_LOADED_EPOCH_CHANGED')
   mode='validation-only'if key=='final'else'resume'
  progress.training_log(trainer.log_file,segment=segment)
  progress.receipt('segment-started',{'segment':segment,'mode':mode,'epoch_resumed_from':epoch,'interruption':interruption,'bitwise_replay_claimed':False})
  if mode!='validation-only':
   trainer.run_training()
  _,final=progress.select('final')
  if final['metadata']['next_epoch']!=trainer.num_epochs:
   raise ValueError('NNUNET_FINAL_EPOCH')
  trainer.perform_actual_validation(True)
  progress.receipt('training-and-validation-complete',{'segment':segment,'final_sha256':final['sha256'],'epoch':trainer.num_epochs})
  return{'mode':mode,'epoch_resumed_from':epoch,'final_sha256':final['sha256']}
 finally:
  trainer.save_checkpoint=original_save
def strict_json(raw):
 def pairs(items):
  out={}
  for key,value in items:
   need(key not in out,'duplicate JSON key');out[key]=value
  return out
 def invalid(value):raise PrerequisiteError('nonfinite JSON')
 def number(value):
  v=float(value);need(math.isfinite(v),'nonfinite JSON');return v
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid,parse_float=number)
def checked_path(value,missing=False):
 import stat
 p=Path(value)
 need(p.is_absolute()and str(p)==str(value)and'..'not in p.parts,'noncanonical absolute path')
 for q in reversed([p,*p.parents]):
  try:s=q.lstat()
  except FileNotFoundError:
   need(missing,'missing path');continue
  need(not stat.S_ISLNK(s.st_mode),'symlink refused')
  need(stat.S_ISDIR(s.st_mode)or stat.S_ISREG(s.st_mode),'special path refused')
  if stat.S_ISREG(s.st_mode):need(q==p and s.st_nlink==1,'file alias refused')
 return p
def metadata_file(contract,descriptor):
 need(set(descriptor)=={'path','sha256','bytes'},'metadata descriptor')
 p=checked_path(descriptor['path'])
 root=checked_path(contract['colab']['metadata_root'])
 need(p.is_relative_to(root)and p!=root,'metadata outside authorized root')
 need(digest(descriptor['sha256'])and type(descriptor['bytes'])is int and descriptor['bytes']>0,'metadata identity')
 raw=p.read_bytes()
 need({'sha256':sha_bytes(raw),'bytes':len(raw)}=={k:descriptor[k]for k in('sha256','bytes')},'metadata mismatch')
 return strict_json(raw)
class DriveInputs:
 def __init__(self,mapping,inventory,allowed):
  need(set(mapping)=={'schema','roots','files'}and mapping['schema']=='colab-in-place-inputs/v1','mapping schema')
  need(isinstance(mapping['files'],list)and mapping['files'],'mapping rows')
  need(mapping['roots']==allowed and allowed,'authorized roots changed')
  self.roots={k:checked_path(v)for k,v in allowed.items()}
  roots=list(self.roots.values())
  need(len(set(roots))==len(roots)and all(not a.is_relative_to(b)for i,a in enumerate(roots)for j,b in enumerate(roots)if i!=j),'ambiguous roots')
  self.rows={};self.inventory=inventory;physical=set()
  for row in mapping['files']:
   need(set(row)=={'logical_path','root','relative_path','sha256','bytes'},'mapping row schema')
   logical=row['logical_path'];relative=row['relative_path']
   need(logical in inventory and logical not in self.rows,'unexpected/duplicate logical path')
   need(row['root']in self.roots,'unauthorized root')
   need(isinstance(relative,str)and relative and not relative.startswith('/')and all(x not in('','.','..')for x in relative.split('/'))and'\\'not in relative,'noncanonical relative path')
   need(type(row['bytes'])is int and{k:row[k]for k in('sha256','bytes')}==inventory[logical],'mapping differs from frozen identity')
   p=self.roots[row['root']]/relative
   need(p not in physical,'duplicate physical mapping');physical.add(p)
   self.rows[logical]=row
  need(set(self.rows)==set(inventory),'incomplete mapping; not a missing-file observation')
 def path(self,logical):
  row=self.rows[logical];root=self.roots[row['root']]
  p=checked_path(str(root/row['relative_path']),missing=True)
  need(p.is_relative_to(root)and p!=root,'input outside authorized root')
  return p
 def verify(self):
  missing=[];observed={};inodes=set()
  for logical in sorted(self.rows):
   p=self.path(logical)
   try:s=p.stat()
   except FileNotFoundError:
    missing.append(dict(self.rows[logical]));continue
   import stat
   need(stat.S_ISREG(s.st_mode)and s.st_nlink==1,'input is not a unique regular file')
   inode=(s.st_dev,s.st_ino);need(inode not in inodes,'physical alias');inodes.add(inode)
   actual=file_info(p)
   need(actual==self.inventory[logical],'frozen input mismatch: '+logical)
   observed[logical]=actual
  return{'schema':'colab-input-check/v1','arm':'A1_repeat','status':'MISSING'if missing else'VERIFIED','missing':missing,'observed':observed,'ctp_required':False,'discovery_performed':False}
 def read(self,descriptor):
  logical=descriptor['path'];need(logical in self.rows,'unmapped read')
  need({k:descriptor[k]for k in('sha256','bytes')}==self.inventory[logical],'unfrozen read')
  p=self.path(logical);need(file_info(p)==self.inventory[logical],'input changed at read')
  return p
def in_place_inputs(contract):
 splits=membership_guard(contract)
 cases=sorted(c for row in splits for c in row['val'])
 cfg=contract['colab']
 inventory=metadata_file(contract,cfg['frozen_inventory'])
 need(sha_bytes(json.dumps(inventory,sort_keys=True,allow_nan=False).encode())==BASE_INPUT_SHA256,'frozen inventory mismatch')
 required={p for c in cases for p in dict(source_paths(c,False),cache=f'feature-cache-2mm-v2/{c}.npz').values()}|{K_BPJ,K_BHJ}
 need(set(inventory)==required and len(required)==893,'released-arm inventory mismatch')
 for item in inventory.values():
  need(set(item)=={'sha256','bytes'}and digest(item['sha256'])and type(item['bytes'])is int and item['bytes']>0,'frozen file identity')
 mapping=metadata_file(contract,cfg['input_mapping'])
 excluded=metadata_file(contract,cfg['exclusions'])['cases']
 need(all(not any(x in str(mapping['roots'][row['root']])+'/'+row['relative_path']for x in excluded)for row in mapping['files']),'excluded identifier in physical mapping')
 return DriveInputs(mapping,inventory,cfg['authorized_input_roots'])
def input_preflight(contract,report_root):
 inputs=in_place_inputs(contract);report=inputs.verify()
 report.update(mapping_sha256=contract['colab']['input_mapping']['sha256'],inventory_sha256=BASE_INPUT_SHA256,checked_unix=time.time(),membership_checked=True)
 write_once(report_root,'input-check-'+uuid.uuid4().hex+'.json',canonical(report))
 need(not report['missing'],'Missing released-arm files; return PRIVATE input-check, fill only listed gaps from existing server Drive access')
 return inputs
def accounting_guard(c):
 a=c['colab']['accounting']
 keys={'stage_spent_micro_usd','stage_other_reserved_micro_usd','total_spent_micro_usd','total_other_reserved_micro_usd','segment_reserved_micro_usd'}
 need(set(a)==keys and all(type(a[k])is int and a[k]>=0 for k in keys),'accounting unavailable')
 reserve=a['segment_reserved_micro_usd'];need(reserve>0,'segment reservation missing')
 need(a['stage_spent_micro_usd']+a['stage_other_reserved_micro_usd']+reserve<=150000000,'stage budget exhausted')
 need(a['total_spent_micro_usd']+a['total_other_reserved_micro_usd']+reserve<=1275000000,'total budget exhausted')
 return a
def actual_environment():
 import sys,platform,subprocess,importlib.metadata as md,torch
 packages={d.metadata['Name']:d.version for d in md.distributions()if d.metadata['Name']}
 ram=os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES')
 capacity=cpu_capacity()
 need(capacity['effective_logical_capacity']>=2 and ram>=16*1024**3,'insufficient observed CPU/RAM')
 need(torch.cuda.is_available()and'A100'in torch.cuda.get_device_name(0),'A100 required')
 gpu=torch.cuda.get_device_properties(0)
 need(gpu.total_memory>=39*1024**3,'A100 memory')
 driver=subprocess.run(['nvidia-smi','--id=0','--query-gpu=driver_version,name,memory.total','--format=csv,noheader'],capture_output=True,text=True,check=True,timeout=10).stdout.strip()
 return{'schema':'colab-environment-observation/v1','unix':time.time(),'python':sys.version,'platform':platform.platform(),'packages':packages,'torch_cuda':torch.version.cuda,'cudnn':torch.backends.cudnn.version(),'gpu':torch.cuda.get_device_name(0),'gpu_bytes':gpu.total_memory,'driver':driver,'cpu':capacity,'ram_bytes':ram,'augmentation_workers_requested':2,'module_sha256':file_info(__file__)['sha256']}
def cu_start(root,segment):
 balance=float(input('Current Colab CU balance from runtime/account display: '))
 rate=float(input('Current displayed CU/hour (observation, not full-plan projection): '))
 need(all(math.isfinite(x)and x>=0 for x in(balance,rate))and rate>0,'invalid runtime CU reading')
 record={'schema':'colab-cu-observation/v1','segment':segment,'start_unix':time.time(),'start_balance':balance,'displayed_cu_per_hour':rate,'source':'operator transcribed current Colab display','historical_balance':1001,'historical_displayed_cu_per_hour':6.77}
 write_once(root,f'cu-start-{segment}.json',canonical(record));return record
def cu_end(root,segment,balance,attributable):
 start=strict_json(rooted(root,f'cu-start-{segment}.json').read_bytes())
 end=time.time();need(type(balance)in(int,float)and math.isfinite(balance)and balance>=0 and type(attributable)is bool,'invalid CU end reading')
 hours=(end-start['start_unix'])/3600
 usage=start['start_balance']-balance
 valid=attributable and usage>=0 and hours>0
 record=dict(start,end_unix=end,end_balance=balance,elapsed_hours=hours,attributable=attributable,consumed_cu=usage if valid else None,actual_cu_per_hour=usage/hours if valid else None,status='OBSERVED'if valid else'UNATTRIBUTABLE',full_training_accepted=False)
 write_once(root,f'cu-end-{segment}.json',canonical(record));return record
def _drive_tests():
 class DriveChecks(unittest.TestCase):
  def test_mapping_boundaries(self):
   with tempfile.TemporaryDirectory()as d:
    root=Path(d)/'existing';root.mkdir();p=root/'one';p.write_bytes(b'synthetic')
    info=file_info(p);inventory={'one':info};roots={'source':str(root)}
    row=dict(logical_path='one',root='source',relative_path='one',**info)
    m=dict(schema='colab-in-place-inputs/v1',roots=roots,files=[row])
    (root/'UNRELATED').write_bytes(b'unused')
    r=DriveInputs(m,inventory,roots)
    self.assertEqual(r.verify()['observed'],inventory)
    self.assertEqual(r.read(dict(path='one',**info)),p)
    for change in({'relative_path':'../one'},{'root':'unknown'},{'sha256':'0'*64},{'logical_path':'extra'}):
     with self.assertRaises(PrerequisiteError):DriveInputs(dict(m,files=[dict(row,**change)]),inventory,roots)
    for rows in([],[row,row]):
     with self.assertRaises(PrerequisiteError):DriveInputs(dict(m,files=rows),inventory,roots)
    p.unlink();self.assertEqual(r.verify()['missing'],[row]);p.write_bytes(b'tampered')
    with self.assertRaises(PrerequisiteError):r.verify()
    target=Path(d)/'other';p.rename(target);p.symlink_to(target)
    with self.assertRaises(PrerequisiteError):r.verify()
    p.unlink();os.link(target,p)
    with self.assertRaises(PrerequisiteError):r.verify()
  def test_accounting_and_json(self):
   with self.assertRaises(PrerequisiteError):strict_json('{"a":1,"a":2}')
   a=dict(stage_spent_micro_usd=0,stage_other_reserved_micro_usd=0,total_spent_micro_usd=0,total_other_reserved_micro_usd=0,segment_reserved_micro_usd=1000000)
   c={'colab':{'accounting':a,'operator_units':2000}};self.assertEqual(accounting_guard(c),a)
   a['stage_spent_micro_usd']=150000000
   with self.assertRaises(PrerequisiteError):accounting_guard(c)
  def test_cu_observed_or_unattributable(self):
   from unittest.mock import patch
   with tempfile.TemporaryDirectory()as d:
    for segment,attributable in((1,True),(2,False)):
     write_once(d,f'cu-start-{segment}.json',canonical({'start_unix':1000,'start_balance':50}))
     with patch('time.time',return_value=4600):r=cu_end(d,segment,43.23,attributable)
     if attributable:self.assertAlmostEqual(r['actual_cu_per_hour'],6.77)
     else:self.assertIsNone(r['actual_cu_per_hour'])
 return unittest.defaultTestLoader.loadTestsFromTestCase(DriveChecks)
