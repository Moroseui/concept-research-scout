# Derived scientific analysis view
Not the original executable notebook. Omitted spans are listed by hash and reason in the bound manifest. Original SHA256: 8d1b47833993ce908f0d22856c7f1aee95b337d2a26862a64375b72c270aa33a

## cells/0/source bytes 0:2148
# Sprint 13a: can a precise model and a sensitive model be combined? (post-processing only)

**What to do:** any Colab runtime works (no GPU needed; High-RAM helps). **Runtime -> Run all.** The first run resamples the nnU-Net probabilities onto the 2 mm scoring grid and caches them on Drive (roughly 20 to 40 minutes); later runs reuse the cache and take a few minutes.

**Why.** On the same 99 patients and folds, the Sprint 12 nnU-Net (with CTA) is more precise than the reference tree (mean precision 0.34 against 0.26) but finds less of the infarct (recall 0.18 against 0.27), with nearly the same Dice. This notebook asks two questions with saved held-out predictions only:

1. **How much of the gap comes from the final rule rather than the model?** The tree and small U-Net mark as much tissue as their scores add up to (the self-volume rule); nnU-Net marks voxels above 50%. Each model is rescored with the other model's kind of rule.
2. **Do the models make different mistakes, and does combining them raise Dice?** Descriptive overlap of their hits and false alarms, then fixed (untuned) averages of their probabilities, then a tuned combination whose weight and cut-off are chosen only on the other four folds (leave-one-fold-out), compared with tuning the cut-off of each model alone.

**Designated before any results (primary):** P1 = nnU-Net + CTA with the self-volume rule minus nnU-Net + CTA as reported (Dice); P2 = equal-weight average of the tree's and nnU-Net + CTA's probabilities with the self-volume rule, minus nnU-Net + CTA as reported (Dice). Both get 95% and Bonferroni 97.5% patient-bootstrap intervals. Everything else is exploratory.

**Safeguards.** Reads saved development results only (99 patients, split 101, first training run); trains no imaging model; never reads the reserved patients. Every input is checked against its run's saved identity, every displayed "as reported" mask is rebuilt or reloaded and compared with the saved result row, and the tuned combination never sees the fold it is scored on. The shareable zip holds aggregate tables and figures only; per-patient tables stay in the PRIVATE folder.

## cells/1/source bytes 0:11
## Settings

## cells/2/source bytes 0:323
# ---------------- settings (the only cell you might edit) ----------------
import os
DRIVE_BASE = os.environ.get("ISLES_BASE", "/content/drive/MyDrive/isles-pilot")
INCLUDE_EXTRA_NN = False        # True also analyses the no-CTA and normalized nnU-Net versions (their first run adds roughly 40 to 80 minutes of resampling)

## cells/3/source bytes 0:50
## Load, validate and rebuild the reported results

## cells/4/source bytes 0:15829
# ================= Sprint 13a: precision/recall complementarity (post-processing only; trains no imaging model) =================
import sys, glob, json, time, zipfile, hashlib, warnings, numpy as np, pandas as pd
warnings.filterwarnings("ignore", category=RuntimeWarning)
T0 = time.time()
def say(m): print(f"[{time.time() - T0:6.0f}s] {m}", flush=True)
try:
    from google.colab import drive, files
    drive.mount("/content/drive"); IN_COLAB = True
except ImportError:
    IN_COLAB = False
import nibabel as nib
from nibabel.processing import resample_from_to
from scipy.ndimage import gaussian_filter, label as cc_label
from scipy.stats import spearmanr
NOTEBOOK_VERSION = "sprint13a-complementarity-r1"
CACHE_DIR = f"{DRIVE_BASE}/feature-cache-2mm-v2"
S8 = f"{DRIVE_BASE}/sprint8-seeds-features-PRIVATE/run-875c56c278"
S9 = f"{DRIVE_BASE}/sprint9-unet-PRIVATE/run-0a60362503"
S12 = f"{DRIVE_BASE}/sprint12-nnunet-r8-PRIVATE"
OUT = f"{DRIVE_BASE}/sprint13a-complementarity-PRIVATE"; os.makedirs(OUT, exist_ok=True)
for rd in (CACHE_DIR, S8, S9, S12): assert not os.path.abspath(OUT).startswith(os.path.abspath(rd)), "must not write inside a read-only input folder"
SHUFFLE, SEED, NBOOT, BOOT_SEED = 101, 1, 2000, 0
EXPECTED_N = int(os.environ.get("ISLES_EXPECTED_N", 99))     # 99 development patients; the override exists only for a synthetic test folder
TOL = 1e-6
NN_ARMS = {"a1": ("A1_ct_maps_cta", "N_ct_maps_cta", "nnU-Net + CTA")}
if INCLUDE_EXTRA_NN: NN_ARMS.update({"a0": ("A0_ct_maps", "N_ct_maps", "nnU-Net, no CTA"), "pn": ("A1_pnorm_v2", "N_ct_maps_cta_pnorm", "nnU-Net + CTA + norm.")})
CHECKS = {}
def check(name, ok, detail=""):
    c = CHECKS.setdefault(name, {"passed": 0, "failed": 0}); c["passed" if ok else "failed"] += 1
    if not ok: raise AssertionError(f"CHECK FAILED [{name}]: {detail}")

# ---- shared rules and metrics, verbatim from the Sprint 8 utilities (so every number is computed exactly as in the saved tables) ----
def rank_order(p):
    """One truth-independent ordering: score descending, voxel index ascending."""
    return np.lexsort((np.arange(p.size), -p))
def official_lesion_metrics(truth, pred, empty_value=1.0):
    """Exact semantics of the pinned official `compute_dice_f1_instance_difference`: 26-connected components; overlapping pairs matched greedily by IoU >= 0.2;
    F1 = TP / (TP + 0.5 FP + 0.5 FN); both-empty -> empty_value."""
    truth = np.asarray(truth).astype(bool); pred = np.asarray(pred).astype(bool); s = np.ones((3, 3, 3), bool)
    lt, nt = cc_label(truth, structure=s) if truth.any() else (np.zeros(truth.shape, np.int32), 0); lp, npd = cc_label(pred, structure=s) if pred.any() else (np.zeros(pred.shape, np.int32), 0)
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
def metrics(pred, cc, lesion=True):
    t = cc["truth"]; tp = int((pred & t).sum()); fp = int((pred & ~t).sum()); fn = int((~pred & t).sum()); den = 2 * tp + fp + fn
    r = {"dice": 2 * tp / den if den else 1.0, "precision": tp / (tp + fp) if (tp + fp) else np.nan, "recall": tp / (tp + fn) if (tp + fn) else np.nan,
         "pred_ml": float(pred.sum() * cc["ml"]), "true_ml": float(t.sum() * cc["ml"]), "pred_empty": bool(pred.sum() == 0)}
    r["abs_vol_err_ml"] = abs(r["pred_ml"] - r["true_ml"]); r["signed_vol_err_ml"] = r["pred_ml"] - r["true_ml"]
    r["lesion_f1"] = official_lesion_metrics(t, pred, 1.0)[0] if lesion else np.nan
    return r
def scatter(cc, v):
    out = np.zeros(cc["shape"], np.float32); out[cc["mask"]] = v; return out
def topk_from(ordered_idx, k, shape):
    out = np.zeros(int(np.prod(shape)), bool)
    if k > 0: out[ordered_idx[:k]] = True
    return out.reshape(shape)
def rule_selfvol(rank_full, vol_full, support, ml, scale=1.0):
    """Self-volume rule (Sprint 8 rule_topk_lexsort): mark the k highest-ranked support voxels, k realising scale x the summed scores' volume."""
    idx = np.flatnonzero(support); target_ml = float(vol_full.ravel()[idx].sum() * ml) * scale
    k = int(round(max(target_ml, 0.0) / ml)); r = rank_full.ravel()[idx]
    return topk_from(idx[rank_order(r)], min(k, idx.size), support.shape)

# ---------------- cohort, partitions, run identities ----------------
P8 = json.load(open(f"{S8}/partitions.json"))
FOLD_OF = {c: int(k.split("_")[1]) for k, v in P8.items() if k.startswith(f"{SHUFFLE}_") for c in v["held"]}
CASES = sorted(FOLD_OF); FOLDS = sorted(set(FOLD_OF.values())); HELD = {k: sorted(c for c in CASES if FOLD_OF[c] == k) for k in FOLDS}
MAN8, MAN9 = json.load(open(f"{S8}/run_manifest.json")), json.load(open(f"{S9}/run_manifest.json"))
check("cohort: partition patients equal the Sprint 8 manifest's development cohort", sorted(MAN8.get("config", {}).get("cases", [])) == CASES, f"{len(CASES)} vs {len(MAN8.get('config', {}).get('cases', []))}")
check("cohort: expected size", len(CASES) == EXPECTED_N, f"{len(CASES)} patients, expected {EXPECTED_N}")
check("cohort: every patient held out exactly once in split 101", sum(len(v["held"]) for k, v in P8.items() if k.startswith(f"{SHUFFLE}_")) == len(CASES), "a patient is held out more than once")
IDENT = {"tree": str(MAN8.get("fingerprint")), "unet": str(MAN9.get("fingerprint"))}
check("identity: Sprint 8 and 9 fingerprints present", all(v not in ("", "None") for v in IDENT.values()), str(IDENT))
READER = {}
for key, (armdir, recipe, lab) in NN_ARMS.items():
    ref = json.load(open(f"{S12}/{armdir}/export/run_reference.json")); IDENT[key] = str(ref.get("fingerprint"))
    check("identity: Sprint 12 run reference lists all five folds", sorted(int(x) for x in ref.get("folds_scored", [])) == FOLDS, f"{lab}: {ref.get('folds_scored')}")
    for k in FOLDS:
        fr = json.load(open(f"{S12}/{armdir}/model_bundle/fold_{k}/fold_receipt.json"))
        check("identity: each fold's model bundle belongs to the run and holds exactly that fold's patients", str(fr.get("fingerprint")) == IDENT[key] and sorted(fr.get("cases", [])) == HELD[k], f"{lab} fold {k}")
    READER[key] = json.load(open(f"{S12}/{armdir}/model_bundle/plans.json")).get("image_reader_writer")
    check("nnU-Net: known image reader (sets the probability axis order)", READER[key] in ("SimpleITKIO",), f"{lab}: {READER[key]}")
READER_ORDER = {"SimpleITKIO": (2, 1, 0)}       # SimpleITK arrays are (z, y, x); nibabel arrays are (x, y, z)

def load_table(pattern, recipe, fp, lab):
    fs = sorted(glob.glob(pattern)); check("tables: result files found", bool(fs), f"{lab}: none at {pattern}")
    d = pd.concat([pd.read_csv(f, dtype={"fingerprint": str, "plans_digest": str, "case": str, "recipe": str}) for f in fs], ignore_index=True)
    d = d[(d.recipe == recipe) & (d.shuffle.astype(int) == SHUFFLE) & (d.train_seed.astype(int) == SEED)].copy()
    check("identity: every table row matches the run's saved identity", len(d) > 0 and (d.fingerprint.astype(str) == fp).all(), f"{lab}")
    conflicts = [c for c in d.case[d.case.duplicated(keep=False)].unique() if len(d[d.case == c].astype(str).drop_duplicates()) > 1]
    check("tables: no conflicting duplicate patient rows", not conflicts, f"{lab}: {len(conflicts)} patients"); d = d.drop_duplicates()
    check("tables: one row per development patient", d.case.is_unique and sorted(d.case) == CASES, f"{lab}")
    check("folds: each patient's table fold matches the saved partition", all(FOLD_OF[c] == int(f) for c, f in zip(d.case, d.fold)), f"{lab}")
    return d.set_index("case").loc[CASES]
TAB = {"tree": load_table(f"{S8}/folds/part1_s{SHUFFLE}_f*_t{SEED}.csv", "D_noslice_smoothed", IDENT["tree"], "tree"),
       "unet": load_table(f"{S9}/folds/unet_U_base_s{SHUFFLE}_f*_t{SEED}.csv", "U_base_smoothed", IDENT["unet"], "small U-Net")}
for key, (armdir, recipe, lab) in NN_ARMS.items(): TAB[key] = load_table(f"{S12}/{armdir}/folds/{recipe}_s{SHUFFLE}_f*.csv", recipe, IDENT[key], lab)

def load_cache(c):
    z = np.load(f"{CACHE_DIR}/{c}.npz", allow_pickle=False); meta = json.loads(str(z["meta"]))
    check("cache: schema and patient", meta.get("schema") == "isles24-features-2mm-v2" and meta.get("case") == c, "cache does not match")
    shape = tuple(int(s) for s in z["mask_shape"]); n = int(np.prod(shape))
    return {"mask": np.unpackbits(z["mask"])[:n].reshape(shape).astype(bool), "truth": np.unpackbits(z["lesion_full"])[:n].reshape(shape).astype(bool),
            "shape": shape, "affine": np.asarray(z["affine"], float), "ml": float(z["voxel_ml"])}
DATA = {c: load_cache(c) for c in CASES}
for key in TAB:
    check("tables: true infarct volume matches the scoring cache", all(abs(float(TAB[key].loc[c, "lesion_ml"]) - DATA[c]["truth"].sum() * DATA[c]["ml"]) <= TOL for c in CASES), key)
say(f"{len(CASES)} patients, {len(FOLDS)} folds; tables validated for {', '.join(TAB)}")

# ---------------- held-out scores: tree (Sprint 8 D scores), small U-Net (Sprint 9), nnU-Net probabilities (Sprint 12) ----------------
P_TREE, SM_TREE, P_UNET, W_TREE, W_UNET = {}, {}, {}, {}, {}
for k in FOLDS:
    z = np.load(f"{S8}/dscores/D_s{SHUFFLE}_f{k}_t{SEED}.npz", allow_pickle=False)
    check("identity: tree scores belong to the Sprint 8 run and hold exactly the fold's patients", str(z["fingerprint"]) == IDENT["tree"] and sorted(str(x) for x in z["cases"]) == HELD[k], f"fold {k}")
    W_TREE[k] = float(z["width"])
    for c in HELD[k]: P_TREE[c], SM_TREE[c] = z[f"raw__{c}"].astype(np.float32), z[f"sm__{c}"].astype(np.float32)
    z = np.load(f"{S9}/uscores/U_base_s{SHUFFLE}_f{k}_t{SEED}.npz", allow_pickle=False)
    check("identity: U-Net scores belong to the Sprint 9 run and hold exactly the fold's patients", str(z["fingerprint"]) == IDENT["unet"] and sorted(str(x) for x in z["cases"]) == HELD[k], f"fold {k}")
    W_UNET[k] = float(z["width"])
    for c in HELD[k]: P_UNET[c] = z[f"raw__{c}"].astype(np.float32)
for c in CASES:
    n = int(DATA[c]["mask"].sum())
    check("scores: one finite score per tissue-mask voxel", P_TREE[c].shape == (n,) and SM_TREE[c].shape == (n,) and P_UNET[c].shape == (n,) and all(np.isfinite(a).all() for a in (P_TREE[c], SM_TREE[c], P_UNET[c])), "score vector")
def nn_prob_2mm(key, c):
    # the fold model's saved probabilities, axis order from the plans' reader and verified against the saved segmentation, resampled linearly onto the 2 mm scoring grid (as Sprint 12 scoring); cached
    armdir = NN_ARMS[key][0]; cc = DATA[c]; cpath = f"{OUT}/nn_prob_2mm/{armdir}/{c}.npz"
    if os.path.exists(cpath):
        z = np.load(cpath, allow_pickle=False)
        if str(z["fingerprint"]) == IDENT[key] and tuple(int(s) for s in z["shape"]) == cc["shape"]: return z["prob"].astype(np.float32)
    b = f"{S12}/{armdir}/model_bundle/fold_{FOLD_OF[c]}/validation"; img = nib.load(f"{b}/{c}.nii.gz"); seg = np.asanyarray(img.dataobj)
    seg = (seg[..., 0] if seg.ndim == 4 else seg) > 0.5
    p = np.transpose(np.load(f"{b}/{c}.npz")["probabilities"][1].astype(np.float32), READER_ORDER[READER[key]])
    check("nnU-Net: probability grid matches the saved segmentation", p.shape == seg.shape, f"{p.shape} vs {seg.shape}")
    q = p > 0.5; s_ = int(q.sum() + seg.sum()); d = 2 * int((q & seg).sum()) / s_ if s_ else 1.0
    check("nnU-Net: probabilities agree with the saved segmentation (Dice >= 0.99)", d >= 0.99, f"Dice {d:.3f}")
    prob = np.clip(resample_from_to(nib.Nifti1Image(p, img.affine), (cc["shape"], cc["affine"]), order=1).get_fdata(), 0, 1).astype(np.float16)
    os.makedirs(os.path.dirname(cpath), exist_ok=True); tmp = cpath[:-4] + ".tmp.npz"
    np.savez_compressed(tmp, prob=prob, shape=np.array(cc["shape"]), fingerprint=IDENT[key]); os.replace(tmp, cpath)
    return prob.astype(np.float32)                       # float16 on first use too, so a rerun from the cache ranks voxels identically
P_NN = {key: {} for key in NN_ARMS}
for key in NN_ARMS:
    for i, c in enumerate(CASES, 1):
        P_NN[key][c] = nn_prob_2mm(key, c)
        if i % 20 == 0 or i == len(CASES): say(f"  {NN_ARMS[key][2]}: probabilities on the 2 mm grid for {i}/{len(CASES)} patients")

# ---------------- rebuild or reload every "as reported" mask and check it against the saved result row ----------------
def load_mask(path, fp, recipe, c):
    z = np.load(path, allow_pickle=False); s = tuple(int(x) for x in z["shape"])
    check("masks: identity, fold and grid match", str(z["fingerprint"]) == fp and str(z["recipe"]) == recipe and int(z["shuffle"]) == SHUFFLE and int(z["train_seed"]) == SEED and int(z["fold"]) == FOLD_OF[c] and s == DATA[c]["shape"], f"{recipe} {path[-60:]}")
    return np.unpackbits(z["pred"])[:int(np.prod(s))].reshape(s).astype(bool)
REPORTED = {key: {} for key in TAB}
for c in CASES:
    cc = DATA[c]; pr = {"shape": cc["shape"], "mask": cc["mask"]}; k = FOLD_OF[c]
    t_mask = rule_selfvol(scatter(cc, SM_TREE[c]), scatter(cc, P_TREE[c]), cc["mask"], cc["ml"])
    check("rebuild: tree mask from saved scores equals the saved mask", np.array_equal(t_mask, load_mask(f"{S8}/masks/D_noslice_smoothed__s{SHUFFLE}_t{SEED}__{c}.npz", IDENT["tree"], "D_noslice_smoothed", c)), "tree")
    u_mask = rule_selfvol(scatter(cc, smooth_scores(pr, P_UNET[c], W_UNET[k])), scatter(cc, P_UNET[c]), cc["mask"], cc["ml"])
    check("rebuild: U-Net mask from saved scores equals the saved mask", np.array_equal(u_mask, load_mask(f"{S9}/masks/U_base_smoothed__s{SHUFFLE}_t{SEED}__{c}.npz", IDENT["unet"], "U_base_smoothed", c)), "U-Net")
    REPORTED["tree"][c], REPORTED["unet"][c] = t_mask, u_mask
    for key, (armdir, recipe, lab) in NN_ARMS.items(): REPORTED[key][c] = load_mask(f"{S12}/{armdir}/masks/{recipe}__s{SHUFFLE}_t{SEED}__{c}.npz", IDENT[key], recipe, c)
    for key in TAB:
        m, row = metrics(REPORTED[key][c], cc), TAB[key].loc[c]
        check("rebuild: Dice, predicted volume and lesion F1 match the saved row", abs(m["dice"] - float(row.dice)) <= TOL and abs(m["pred_ml"] - float(row.pred_ml)) <= TOL and abs(m["lesion_f1"] - float(row.lesion_f1)) <= TOL,
              f"{key}: Dice {m['dice']:.6f} vs {float(row.dice):.6f}, ml {m['pred_ml']:.4f} vs {float(row.pred_ml):.4f}, lesion F1 {m['lesion_f1']:.4f} vs {float(row.lesion_f1):.4f}")
def agreement(a, b): n = int(a.sum() + b.sum()); return 1.0 if n == 0 else 2 * int((a & b).sum()) / n
AGREE = {key: round(float(np.mean([agreement(P_NN[key][c] > 0.5, REPORTED[key][c]) for c in CASES])), 4) for key in NN_ARMS}
say("reported masks rebuilt or reloaded and matched to the saved rows for every patient; nnU-Net probability above 0.5 on the 2 mm grid agrees with the reported (nearest-neighbour) mask at mean Dice " + ", ".join(f"{NN_ARMS[k][2]} {v:.3f}" for k, v in AGREE.items()))

## cells/5/source bytes 0:69
## Analyses: rule swap, complementarity, fixed and tuned combinations

## cells/6/source bytes 0:12664
# ---------------- candidate support and fused scores (every combined rule uses this one definition) ----------------
CAND_EPS = 1e-4                                   # voxels outside the tissue mask whose nnU-Net probability is below this are never marked by a combined rule
def tree_full(c): return scatter(DATA[c], P_TREE[c])
def unet_full(c): return scatter(DATA[c], P_UNET[c])
def fused_rule(c, w, rule, param, key="a1", third=None):
    # score = w * nnU-Net + (1 - w) * tree (or an equal three-way average when third == "unet"); rule "selfvol": top-k with k = param x summed scores over the full grid; rule "thresh": score > param
    cc = DATA[c]; pn = P_NN[key][c]; pt = tree_full(c)
    s = (pn + pt + unet_full(c)) / 3.0 if third == "unet" else w * pn + (1 - w) * pt
    cand = np.flatnonzero(cc["mask"] | (pn > CAND_EPS)); sc = s.ravel()[cand]
    if rule == "selfvol":
        k = int(round(max(float(s.sum()) * param, 0.0))); return topk_from(cand[rank_order(sc)], min(k, cand.size), cc["shape"])
    out = np.zeros(int(np.prod(cc["shape"])), bool); out[cand[sc > param]] = True; return out.reshape(cc["shape"])

# ---------------- every method on every patient (pre-specified list; tuned methods are added below) ----------------
METHODS = {}                                       # name -> (role, description, function(c) -> mask)
METHODS["tree, as reported"] = ("reference", "self-volume rule on smoothed tree scores inside the tissue mask", lambda c: REPORTED["tree"][c])
METHODS["small U-Net, as reported"] = ("reference", "self-volume rule on smoothed U-Net scores inside the tissue mask", lambda c: REPORTED["unet"][c])
for key, (armdir, recipe, lab) in NN_ARMS.items():
    METHODS[f"{lab}, as reported"] = ("reference", "probability above 50% on the scan grid, nearest-neighbour to 2 mm", (lambda c, key=key: REPORTED[key][c]))
METHODS["tree, 50% rule"] = ("rule swap", "tree probability above 0.5 inside the tissue mask", lambda c: DATA[c]["mask"] & (tree_full(c) > 0.5))
METHODS["nnU-Net + CTA, self-volume rule"] = ("PRIMARY P1", "top-k nnU-Net probabilities, k from their sum (no smoothing, not limited to the tissue mask)", lambda c: fused_rule(c, 1.0, "selfvol", 1.0))
METHODS["nnU-Net + CTA, full tree rule"] = ("rule swap", "the tree's rule applied to nnU-Net probabilities: smoothed at the tree's fold width, top-k inside the tissue mask",
    lambda c: rule_selfvol(scatter(DATA[c], smooth_scores({"shape": DATA[c]["shape"], "mask": DATA[c]["mask"]}, P_NN["a1"][c][DATA[c]["mask"]], W_TREE[FOLD_OF[c]])), P_NN["a1"][c], DATA[c]["mask"], DATA[c]["ml"]))
METHODS["average tree + nnU-Net, self-volume"] = ("PRIMARY P2", "equal-weight average of the two probabilities, self-volume rule", lambda c: fused_rule(c, 0.5, "selfvol", 1.0))
METHODS["average tree + nnU-Net, 50% rule"] = ("fixed combination", "equal-weight average above 0.5", lambda c: fused_rule(c, 0.5, "thresh", 0.5))
METHODS["average tree + U-Net + nnU-Net, self-volume"] = ("fixed combination", "equal three-way average, self-volume rule", lambda c: fused_rule(c, None, "selfvol", 1.0, third="unet"))
METHODS["union of reported tree and nnU-Net"] = ("set operation", "voxels marked by either reported mask", lambda c: REPORTED["tree"][c] | REPORTED["a1"][c])
METHODS["intersection of reported tree and nnU-Net"] = ("set operation", "voxels marked by both reported masks", lambda c: REPORTED["tree"][c] & REPORTED["a1"][c])

# ---------------- tuned combination, leave-one-fold-out (weight and cut-off chosen on the other four folds only) ----------------
W_GRID = [round(x, 1) for x in np.linspace(0, 1, 11)]
RULES = [("selfvol", s) for s in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0)] + [("thresh", t) for t in (0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)]
CONFIGS = [(w, r, p) for w in W_GRID for (r, p) in RULES]
def dice_curve(c):
    # Dice of every configuration for one patient, from one ranking per weight (identical to fused_rule's masks)
    cc = DATA[c]; pn, pt = P_NN["a1"][c], tree_full(c); T = int(cc["truth"].sum())
    cand = np.flatnonzero(cc["mask"] | (pn > CAND_EPS)); truth_c = cc["truth"].ravel()[cand]; out = {}
    for w in W_GRID:
        s = w * pn + (1 - w) * pt; sc = s.ravel()[cand]; o = rank_order(sc); tpc = np.concatenate([[0], np.cumsum(truth_c[o])]); ss = sc[o]; total = float(s.sum())
        for r, p in RULES:
            k = min(int(round(max(total * p, 0.0))), cand.size) if r == "selfvol" else int(np.sum(sc > p))
            tp = int(tpc[k]) if r == "selfvol" else int(truth_c[sc > p].sum())
            out[(w, r, p)] = 2 * tp / (k + T) if (k + T) else 1.0
    return out
t0 = time.time(); DC = {c: dice_curve(c) for c in CASES}; say(f"configuration grid ({len(CONFIGS)} weight and rule combinations) scored for every patient in {time.time() - t0:.0f} s")
def pick(train_cases, allowed):
    best, best_v = None, -1.0
    for cfg in CONFIGS:                                   # fixed order: ties go to the earlier (lower nnU-Net weight, then self-volume before threshold, then smaller parameter)
        if cfg[0] not in allowed: continue
        v = float(np.mean([DC[c][cfg] for c in train_cases]))
        if v > best_v + 1e-12: best, best_v = cfg, v
    return best, best_v
TUNED, CHOICES = {"tuned combination (weight and cut-off)": {}, "nnU-Net + CTA, tuned cut-off only": {}, "tree, tuned cut-off only": {}}, []
for name, allowed in (("tuned combination (weight and cut-off)", set(W_GRID)), ("nnU-Net + CTA, tuned cut-off only", {1.0}), ("tree, tuned cut-off only", {0.0})):
    for k in FOLDS:
        cfg, v = pick([c for c in CASES if FOLD_OF[c] != k], allowed)
        CHOICES.append({"method": name, "held-out fold": k, "nnU-Net weight": cfg[0], "rule": cfg[1], "parameter": cfg[2], "inner mean Dice (other four folds)": round(v, 4)})
        for c in HELD[k]: TUNED[name][c] = cfg
for name in TUNED:
    METHODS[name] = ("tuned (leave-one-fold-out)", "weight and rule chosen on the other four folds; raw tree scores (no smoothing)", (lambda c, name=name: fused_rule(c, *TUNED[name][c])))
for c in CASES:                                      # the fast grid and the mask builder must agree exactly
    for name in TUNED: check("tuning: grid Dice equals the rebuilt mask's Dice", abs(DC[c][TUNED[name][c]] - metrics(fused_rule(c, *TUNED[name][c]), DATA[c], lesion=False)["dice"]) <= 1e-9, name)
for name in ("nnU-Net + CTA, self-volume rule", "average tree + nnU-Net, self-volume", "average tree + nnU-Net, 50% rule"):
    cfg = {"nnU-Net + CTA, self-volume rule": (1.0, "selfvol", 1.0), "average tree + nnU-Net, self-volume": (0.5, "selfvol", 1.0), "average tree + nnU-Net, 50% rule": (0.5, "thresh", 0.5)}[name]
    for c in CASES: check("tuning: grid Dice equals the fixed method's Dice", abs(DC[c][cfg] - metrics(METHODS[name][2](c), DATA[c], lesion=False)["dice"]) <= 1e-9, name)

# ---------------- score every method on every patient ----------------
t0 = time.time(); ROWS = []
for name, (role, desc, fn) in METHODS.items():
    for c in CASES: ROWS.append({"method": name, "case": c, "fold": FOLD_OF[c], **metrics(fn(c), DATA[c])})
PER = pd.DataFrame(ROWS); say(f"{len(METHODS)} methods scored on {len(CASES)} patients in {time.time() - t0:.0f} s")
ORACLE = PER[PER.method.isin(["tree, as reported", "nnU-Net + CTA, as reported"])].sort_values(["case", "dice"]).groupby("case").tail(1).assign(method="per-patient best of tree and nnU-Net (uses the answers)")
PER = pd.concat([PER, ORACLE], ignore_index=True); METHODS["per-patient best of tree and nnU-Net (uses the answers)"] = ("upper bound, not achievable", "picks the better reported mask per patient using the true infarct", None)

# ---------------- summaries and paired comparisons (patient bootstrap, fixed resamples shared by all comparisons) ----------------
BOOT_IDX = np.random.default_rng(BOOT_SEED).integers(0, len(CASES), size=(NBOOT, len(CASES)))
def boot(x, stat=np.nanmean, q=(2.5, 97.5)):
    x = np.asarray(x, float); vals = np.array([stat(x[i]) for i in BOOT_IDX]); return (float(stat(x)), *[float(np.nanpercentile(vals, qq)) for qq in q])
def f3(t, d=3):
    if not np.isfinite(t[0]): return "n/a (undefined for these patients)"
    return f"{t[0]:+.{d}f} ({t[1]:+.{d}f} to {t[2]:+.{d}f})" if len(t) == 3 else f"{t[0]:+.{d}f} (95%: {t[1]:+.{d}f} to {t[2]:+.{d}f}; 97.5%: {t[3]:+.{d}f} to {t[4]:+.{d}f})"
def per_method(name): return PER[PER.method == name].set_index("case").loc[CASES]
SUMMARY = []
for name, (role, desc, _) in METHODS.items():
    t = per_method(name); d = boot(t.dice)
    SUMMARY.append({"method": name, "role": role, "rule": desc, "mean Dice (95% CI)": f"{d[0]:.3f} ({d[1]:.3f} to {d[2]:.3f})", "mean precision": round(float(t.precision.mean()), 3), "precision patients": int(t.precision.notna().sum()),
                    "mean recall": round(float(t.recall.mean()), 3), "mean lesion F1": round(float(t.lesion_f1.mean()), 3), "median abs. volume error, ml": round(float(t.abs_vol_err_ml.median()), 1),
                    "median signed volume error, ml": round(float(t.signed_vol_err_ml.median()), 1), "empty predictions": int(t.pred_empty.sum())})
SUMMARY = pd.DataFrame(SUMMARY)
PAIRED = []
for base in ("nnU-Net + CTA, as reported", "tree, as reported"):
    b = per_method(base)
    for name, (role, desc, _) in METHODS.items():
        if name == base or role.startswith("upper bound"): continue
        t = per_method(name); dd = (t.dice - b.dice).values; primary = role.startswith("PRIMARY") and base == "nnU-Net + CTA, as reported"
        PAIRED.append({"comparison": f"{name} minus {base}", "role": role if primary else "exploratory", "patients": len(dd),
                       "Dice": f3(boot(dd, np.mean, (2.5, 97.5, 1.25, 98.75)) if primary else boot(dd, np.mean)), "better / worse / tied": f"{int((dd > 0).sum())} / {int((dd < 0).sum())} / {int((dd == 0).sum())}",
                       "precision": f3(boot((t.precision - b.precision).values)), "recall": f3(boot((t.recall - b.recall).values)), "lesion F1": f3(boot((t.lesion_f1 - b.lesion_f1).values)),
                       "median change in abs. volume error, ml": round(float(np.median((t.abs_vol_err_ml - b.abs_vol_err_ml).values)), 1)})
PAIRED = pd.DataFrame(PAIRED); PAIRED = pd.concat([PAIRED[PAIRED.role != "exploratory"], PAIRED[PAIRED.role == "exploratory"]], ignore_index=True)

# ---------------- complementarity: do the reported masks make different mistakes? (descriptive; no tuning) ----------------
def overlap(a_key, b_key):
    rows = []
    for c in CASES:
        T = DATA[c]["truth"]; A_, B_ = REPORTED[a_key][c], REPORTED[b_key][c]; nT = int(T.sum()); fpa, fpb = A_ & ~T, B_ & ~T; nfp = int((fpa | fpb).sum())
        rows.append({"found by both": (A_ & B_ & T).sum() / nT if nT else np.nan, "found only by first": (A_ & ~B_ & T).sum() / nT if nT else np.nan, "found only by second": (~A_ & B_ & T).sum() / nT if nT else np.nan,
                     "found by neither": (~A_ & ~B_ & T).sum() / nT if nT else np.nan, "false alarms shared": (fpa & fpb).sum() / nfp if nfp else np.nan})
    r = pd.DataFrame(rows).mean().round(3).to_dict()
    da, db = TAB[a_key].dice.astype(float).values, TAB[b_key].dice.astype(float).values
    r.update({"pair (first, second)": f"{a_key} vs {b_key}", "Spearman correlation of per-patient Dice": round(float(spearmanr(da, db).correlation), 3), "patients where first scores higher / second higher": f"{int((da > db).sum())} / {int((db > da).sum())}"})
    return r
COMP = pd.DataFrame([overlap("tree", "a1"), overlap("unet", "a1"), overlap("tree", "unet")])
COMP["pair (first, second)"] = COMP["pair (first, second)"].map({"tree vs a1": "tree vs nnU-Net + CTA", "unet vs a1": "small U-Net vs nnU-Net + CTA", "tree vs unet": "tree vs small U-Net"})
COMP = COMP[["pair (first, second)"] + [c for c in COMP.columns if c != "pair (first, second)"]]
CHOICES = pd.DataFrame(CHOICES)

pd.set_option("display.width", 260); pd.set_option("display.max_columns", 30); pd.set_option("display.max_colwidth", 70)
print("\nEvery method on its own (means over patients; precision undefined when nothing is marked; recall undefined for the patient with no infarct):"); print(SUMMARY.drop(columns=["rule"]).to_string(index=False))
print("\nPaired differences, first minus second (same patients and folds; 95% patient-bootstrap intervals, plus Bonferroni 97.5% for the two primaries):"); print(PAIRED.to_string(index=False))
print("\nComplementarity of the reported masks (shares of each patient's true infarct, averaged over patients with an infarct):"); print(COMP.to_string(index=False))
print("\nChosen weight and rule per held-out fold (chosen on the other four folds only):"); print(CHOICES.to_string(index=False))

## cells/7/source bytes 0:32
## Figures and the shareable zip

## cells/8/source bytes 0:6074
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
INK, MUTED, GRID = "#1F2937", "#5B6470", "#E5E7EB"
GROUP = {"reference": ("as reported", "#6B7280"), "rule swap": ("rule swap", "#2A78D6"), "PRIMARY P1": ("rule swap", "#2A78D6"), "PRIMARY P2": ("fixed combination or set operation", "#EB6834"),
         "fixed combination": ("fixed combination or set operation", "#EB6834"), "set operation": ("fixed combination or set operation", "#EB6834"), "tuned (leave-one-fold-out)": ("tuned on the other four folds", "#1BAF7A")}
fig = plt.figure(figsize=(12.5, 6.6)); ax = fig.add_axes([0.07, 0.10, 0.50, 0.80])
pts = [r for _, r in SUMMARY.iterrows() if not r.role.startswith("upper bound")]; key_lines = []
for i, r in enumerate(pts, 1):
    g, col = GROUP.get(r.role, ("other", "#6B7280")); prim = r.role.startswith("PRIMARY")
    ax.scatter(r["mean recall"], r["mean precision"], s=95 if prim else 60, color=col, edgecolor=INK if prim else "white", linewidth=2, zorder=3)
    ax.annotate(str(i), (r["mean recall"], r["mean precision"]), xytext=(5, 5), textcoords="offset points", fontsize=9, fontweight="bold", color=INK)
    key_lines.append(f"{i:>2}. {r.method}" + ("  [primary]" if prim else ""))
ax.set_xlabel("mean recall (share of each infarct that was marked)", color=INK); ax.set_ylabel("mean precision (share of the marked tissue that is infarct)", color=INK)
ax.grid(color=GRID, linewidth=0.8); ax.set_axisbelow(True); [s_.set_color(GRID) for s_ in ax.spines.values()]; ax.tick_params(colors=MUTED)
ax.set_title("Precision and recall of each rule and combination (patient-level means)", fontsize=11, color=INK, loc="left")
from matplotlib.lines import Line2D
groups = list(dict.fromkeys(GROUP[r.role] for r in pts if r.role in GROUP))
handles = [Line2D([], [], marker="o", linestyle="", markersize=8, color=col, markeredgecolor="white", label=g) for g, col in groups] + [Line2D([], [], marker="o", linestyle="", markersize=9, color="white", markeredgecolor=INK, markeredgewidth=2, label="ringed: designated primary")]
ax.legend(handles=handles, frameon=False, fontsize=8.5, loc="best")
fig.text(0.60, 0.90, "Key", fontsize=10, fontweight="bold", color=INK, va="top"); fig.text(0.60, 0.86, "\n".join(key_lines), fontsize=8.5, color=INK, va="top", family="DejaVu Sans")
fig.savefig(f"{OUT}/sprint13a_precision_recall.png", dpi=150); plt.close(fig)
fig, ax = plt.subplots(figsize=(5.6, 5.4)); da, db = TAB["tree"].dice.astype(float).values, TAB["a1"].dice.astype(float).values
ax.plot([0, 1], [0, 1], color=GRID, linewidth=1.5, zorder=1); ax.scatter(da, db, s=36, color="#2A78D6", edgecolor="white", linewidth=1.5, zorder=3)
ax.set_xlabel("tree, as reported: Dice per patient", color=INK); ax.set_ylabel("nnU-Net + CTA, as reported: Dice per patient", color=INK); ax.set_xlim(-0.02, 1.0); ax.set_ylim(-0.02, 1.0)
ax.grid(color=GRID, linewidth=0.8); ax.set_axisbelow(True); [s_.set_color(GRID) for s_ in ax.spines.values()]; ax.tick_params(colors=MUTED)
ax.set_title("Same patients, two models: points off the diagonal are\nwhere one model does better", fontsize=10, color=INK, loc="left")
fig.tight_layout(); fig.savefig(f"{OUT}/sprint13a_dice_tree_vs_nnunet.png", dpi=150); plt.close(fig)

VALID = {"notebook_version": NOTEBOOK_VERSION, "all_checks_passed": all(v["failed"] == 0 for v in CHECKS.values()), "checks": CHECKS,
         "note": "every check stops the notebook on its first failure, so a saved summary means every listed check passed",
         "nnunet_prob_above_half_vs_reported_mask_mean_dice": AGREE, "tolerance": TOL}
PROV = {"notebook_version": NOTEBOOK_VERSION, "cohort": "99 development patients, split 101; reserved patients not read", "inputs": {"tree": "Sprint 8 D scores and masks (seed 1)", "small U-Net": "Sprint 9 U_base scores and masks (seed 1)",
        "nnU-Net": {NN_ARMS[k][2]: f"Sprint 12 {NN_ARMS[k][0]}: fold-model probabilities, resampled linearly to the 2 mm grid; reported masks reloaded" for k in NN_ARMS}},
        "primary": {"P1": "nnU-Net + CTA, self-volume rule minus nnU-Net + CTA as reported (Dice)", "P2": "equal-weight average of tree and nnU-Net + CTA probabilities, self-volume rule, minus nnU-Net + CTA as reported (Dice)"},
        "bootstrap": {"resamples": NBOOT, "rng": "numpy default_rng", "seed": BOOT_SEED, "intervals": "percentile, patient resampling; primaries also Bonferroni 97.5%"},
        "tuning": "leave-one-fold-out over the other four folds' held-out predictions; those predictions come from models trained partly on the scored fold's patients, a small second-order dependence that is standard for stacking but not zero",
        "grid": {"nnU-Net weights": W_GRID, "rules": [list(r) for r in RULES], "candidate support": f"tissue mask plus voxels with nnU-Net probability above {CAND_EPS}"},
        "metrics": "patient-level values averaged over patients; Dice, precision, recall and lesion F1 computed exactly as in the saved tables (official lesion matching, IoU >= 0.2)"}
PER.to_csv(f"{OUT}/sprint13a_per_patient_PRIVATE.csv", index=False)
SUMMARY.to_csv(f"{OUT}/sprint13a_methods.csv", index=False); PAIRED.to_csv(f"{OUT}/sprint13a_paired.csv", index=False); COMP.to_csv(f"{OUT}/sprint13a_complementarity.csv", index=False); CHOICES.to_csv(f"{OUT}/sprint13a_tuned_choices.csv", index=False)
json.dump(VALID, open(f"{OUT}/sprint13a_validation_summary.json", "w"), indent=1, default=str); json.dump(PROV, open(f"{OUT}/sprint13a_provenance.json", "w"), indent=1)
print("\nValidation summary:"); [print(f"  {k}: {v['passed']} passed, {v['failed']} failed") for k, v in CHECKS.items()]
SHARE = ["sprint13a_methods.csv", "sprint13a_paired.csv", "sprint13a_complementarity.csv", "sprint13a_tuned_choices.csv", "sprint13a_validation_summary.json", "sprint13a_provenance.json", "sprint13a_precision_recall.png", "sprint13a_dice_tree_vs_nnunet.png"]
ZIP = f"{OUT}/sprint13a_share.zip"
with zipfile.ZipFile(ZIP, "w") as zf:
    for f in SHARE: zf.write(f"{OUT}/{f}", f)
say(f"done ({NOTEBOOK_VERSION}). Shareable zip, no patient identifiers: {ZIP}")
if IN_COLAB: files.download(ZIP)