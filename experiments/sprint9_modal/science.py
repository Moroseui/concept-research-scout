# Scientific definitions copied verbatim from the pinned Sprint9 notebook.
# See science-provenance.json. No top-level training or data loading.
import os, json, time, glob, uuid, hashlib, datetime
import numpy as np, pandas as pd, psutil
from scipy.ndimage import gaussian_filter, distance_transform_edt, binary_erosion, label as cc_label
from sklearn.metrics import roc_auc_score, average_precision_score

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

def vol_from_flat(pr, flat_bool):
    v = np.zeros(pr["shape"], dtype=bool); v[pr["mask"]] = flat_bool; return v

def expected_volume_ml(pr, p):
    """Score-derived volume estimate: the sum of scores; an expected volume only if the scores were calibrated, which is not established."""
    return float(p.sum() * pr["voxel_ml"])

def rank_order(p):
    """One truth-independent ordering used by BOTH the top-k rule and the prefix diagnostic: score descending, voxel index ascending."""
    return np.lexsort((np.arange(p.size), -p))

def rule_topk_lexsort(pr, p, target_ml):
    """Call dead exactly the k highest-scoring voxels under rank_order (k realises the target volume)."""
    k = int(round(max(target_ml, 0.0) / pr["voxel_ml"])); flat = np.zeros(p.size, dtype=bool)
    if k > 0: flat[rank_order(p)[:min(k, p.size)]] = True
    return vol_from_flat(pr, flat)

def feature_volume(c, norm, feature_idx, scale):
    """Dense (C+1, X, Y, Z) float16 volume from a cache: robust-scaled features inside the mask, zeros outside, plus a mask channel.
    scale = {'med': array(C), 'iqr': array(C)} from TRAINING patients only."""
    X = apply_normative(c["X"], norm)[:, feature_idx]; X = (X - scale["med"]) / scale["iqr"]; X = np.clip(X, -6, 6)
    vol = np.zeros((len(feature_idx) + 1,) + tuple(c["shape"]), np.float16); vol[:-1][:, c["mask"]] = X.T.astype(np.float16); vol[-1][c["mask"]] = 1
    return vol

def feature_scale(caches, norm, feature_idx, per_case=20000, seed=0):
    rng = np.random.default_rng(seed); rows = []
    for c in caches:
        idx = rng.choice(c["X"].shape[0], min(per_case, c["X"].shape[0]), replace=False); rows.append(apply_normative(c["X"][idx], norm)[:, feature_idx])
    A = np.concatenate(rows); med = np.median(A, axis=0); iqr = np.percentile(A, 75, axis=0) - np.percentile(A, 25, axis=0)
    return {"med": med.astype(np.float32), "iqr": np.where(iqr > 1e-6, iqr, 1.0).astype(np.float32)}

def pad_to(vol, patch):
    """Pad every spatial axis up to at least the patch size (zeros = outside support)."""
    pads = [(0, 0)] + [(0, max(0, p - s)) for s, p in zip(vol.shape[1:], patch)]
    return np.pad(vol, pads) if any(p[1] for p in pads) else vol

def sample_patch_origin(shape, patch, rng, center=None):
    """Origin of a patch inside `shape`; if `center` is given, the patch is placed around it (clipped to the volume)."""
    out = []
    for s, p, cc in zip(shape, patch, center if center is not None else [None] * 3):
        lo = 0 if cc is None else int(np.clip(cc - p // 2 + rng.integers(-p // 4, p // 4 + 1), 0, max(s - p, 0)))
        out.append(lo if cc is not None else int(rng.integers(0, max(s - p, 0) + 1)))
    return tuple(out)

def sliding_windows(shape, patch, stride):
    """Origins covering the whole volume with the given stride; the last window along each axis is flush with the edge."""
    axes = []
    for s, p, st in zip(shape, patch, stride):
        starts = list(range(0, max(s - p, 0) + 1, st))
        if starts[-1] != max(s - p, 0): starts.append(max(s - p, 0))
        axes.append(starts)
    return [(a, b, c) for a in axes[0] for b in axes[1] for c in axes[2]]

def assemble_windows(shape, patch, origins, outputs):
    """Average overlapping window outputs into a full volume (numpy)."""
    acc = np.zeros(shape, np.float32); cnt = np.zeros(shape, np.float32)
    for (a, b, c), out in zip(origins, outputs):
        acc[a:a + patch[0], b:b + patch[1], c:c + patch[2]] += out; cnt[a:a + patch[0], b:b + patch[1], c:c + patch[2]] += 1
    return acc / np.maximum(cnt, 1)

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


import torch, torch.nn as nn, torch.nn.functional as F
class Block(nn.Module):
    def __init__(self, i, o):
        super().__init__(); self.c1 = nn.Conv3d(i, o, 3, padding=1); self.n1 = nn.InstanceNorm3d(o, affine=True); self.c2 = nn.Conv3d(o, o, 3, padding=1); self.n2 = nn.InstanceNorm3d(o, affine=True)
    def forward(self, x): return F.leaky_relu(self.n2(self.c2(F.leaky_relu(self.n1(self.c1(x)), 0.1))), 0.1)
class SmallUNet3D(nn.Module):
    """Two-level 3D U-Net (about 0.4M parameters): enough context to test learned spatial coherence at 2 mm, small enough for 69 patients."""
    def __init__(self, in_ch, w=16):
        super().__init__(); self.e1 = Block(in_ch, w); self.e2 = Block(w, 2 * w); self.e3 = Block(2 * w, 4 * w)
        self.u2 = nn.ConvTranspose3d(4 * w, 2 * w, 2, stride=2); self.d2 = Block(4 * w, 2 * w); self.u1 = nn.ConvTranspose3d(2 * w, w, 2, stride=2); self.d1 = Block(2 * w, w); self.out = nn.Conv3d(w, 1, 1)
    def forward(self, x):
        e1 = self.e1(x); e2 = self.e2(F.max_pool3d(e1, 2)); e3 = self.e3(F.max_pool3d(e2, 2))
        d2 = self.d2(torch.cat([self.u2(e3), e2], 1)); d1 = self.d1(torch.cat([self.u1(d2), e1], 1)); return self.out(d1)
def dice_bce_loss(logits, y, mask):
    p = torch.sigmoid(logits) * mask; y = y * mask
    bce = F.binary_cross_entropy_with_logits(logits, y, reduction="none"); bce = (bce * mask).sum() / mask.sum().clamp(min=1)
    inter = (p * y).sum(); dice = 1 - (2 * inter + 1) / (p.sum() + y.sum() + 1); return bce + dice
def make_scaler(device):
    try: return torch.amp.GradScaler("cuda", enabled=(device.type == "cuda"))
    except Exception: return torch.cuda.amp.GradScaler(enabled=(device.type == "cuda"))
def smoke_step(in_ch, width, patch, batch, lr, weight_decay, device):
    """One configured-shape forward/backward/optimizer step under AMP + one sliding-window inference. Returns dict or raises."""
    model = SmallUNet3D(in_ch, width).to(device); opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay); scaler = make_scaler(device); t0 = time.time()
    x = torch.randn(batch, in_ch, *patch, device=device); y = (torch.rand(batch, 1, *patch, device=device) > 0.95).float(); mk = torch.ones_like(y)
    with torch.autocast(device_type=("cuda" if device.type == "cuda" else "cpu"), enabled=(device.type == "cuda")): loss = dice_bce_loss(model(x), y, mk)
    scaler.scale(loss).backward(); grads_finite = all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None); scaler.step(opt); scaler.update()
    assert torch.isfinite(loss) and grads_finite, "non-finite loss or gradients in the smoke step"
    vol = np.random.default_rng(0).normal(size=(in_ch, patch[0] + 5, patch[1] + 3, patch[2] + 2)).astype(np.float16); vol[-1] = 1
    out = predict_volume(model, vol, patch, tuple(p // 2 for p in patch), device, batch=batch); assert out.shape == vol.shape[1:] and np.isfinite(out).all() and 0 <= out.min() <= out.max() <= 1
    mem = torch.cuda.max_memory_allocated() / 1e9 if device.type == "cuda" else None
    return {"parameters": int(sum(p.numel() for p in model.parameters())), "loss": float(loss), "seconds": time.time() - t0, "batch": batch, "peak_gpu_gb": mem}
def predict_volume(model, vol, patch, stride, device, batch=8):
    """Sliding-window inference on one (C, X, Y, Z) float16 volume -> probability volume (mask channel zeroes the outside)."""
    model.eval(); shape = vol.shape[1:]; origins = sliding_windows(shape, patch, stride); outs = []
    with torch.no_grad():
        for i in range(0, len(origins), batch):
            chunk = origins[i:i + batch]; x = torch.from_numpy(np.stack([vol[:, a:a + patch[0], b:b + patch[1], c:c + patch[2]].astype(np.float32) for a, b, c in chunk])).to(device)
            with torch.autocast(device_type=("cuda" if device.type == "cuda" else "cpu"), enabled=(device.type == "cuda")):
                pr = torch.sigmoid(model(x)).float()[:, 0]
            outs.extend(list(pr.cpu().numpy()))
    return assemble_windows(shape, patch, origins, outs) * vol[-1].astype(np.float32)

class FiLMGen(nn.Module):
    """Generator: clinical vector -> per-block (scale, shift); initialized to the identity so the FiLM network starts as the base network."""
    def __init__(self, n_cond, widths, hidden=32):
        super().__init__(); self.h = nn.Linear(n_cond, hidden); self.outs = nn.ModuleList([nn.Linear(hidden, 2 * w) for w in widths])
        for o in self.outs: nn.init.zeros_(o.weight); nn.init.zeros_(o.bias)
    def forward(self, z): h = F.relu(self.h(z)); return [o(h) for o in self.outs]
class FiLMUNet3D(SmallUNet3D):
    """The same U-Net with feature-wise linear modulation after every block: y = (1 + gamma) * x + beta, gamma and beta from the clinical vector."""
    def __init__(self, in_ch, n_cond, w=16, hidden=32):
        super().__init__(in_ch, w); self.gen = FiLMGen(n_cond, [w, 2 * w, 4 * w, 2 * w, w], hidden)
    def forward(self, x, z):
        gb = self.gen(z)
        def film(t, i):
            g, b = gb[i].chunk(2, 1); return t * (1 + g[:, :, None, None, None]) + b[:, :, None, None, None]
        e1 = film(self.e1(x), 0); e2 = film(self.e2(F.max_pool3d(e1, 2)), 1); e3 = film(self.e3(F.max_pool3d(e2, 2)), 2)
        d2 = film(self.d2(torch.cat([self.u2(e3), e2], 1)), 3); d1 = film(self.d1(torch.cat([self.u1(d2), e1], 1)), 4); return self.out(d1)
def forward_any(model, x, z): return model(x, z) if z is not None else model(x)
def predict_volume_c(model, vol, patch, stride, device, batch=8, cond=None):
    """Sliding-window inference with an optional clinical vector (repeated per window)."""
    model.eval(); shape = vol.shape[1:]; origins = sliding_windows(shape, patch, stride); outs = []
    with torch.no_grad():
        for i in range(0, len(origins), batch):
            chunk = origins[i:i + batch]; x = torch.from_numpy(np.stack([vol[:, a:a + patch[0], b:b + patch[1], c:c + patch[2]].astype(np.float32) for a, b, c in chunk])).to(device)
            z = torch.from_numpy(np.tile(cond.astype(np.float32), (len(chunk), 1))).to(device) if cond is not None else None
            with torch.autocast(device_type=("cuda" if device.type == "cuda" else "cpu"), enabled=(device.type == "cuda")):
                pr = torch.sigmoid(forward_any(model, x, z)).float()[:, 0]
            outs.extend(list(pr.cpu().numpy()))
    return assemble_windows(shape, patch, origins, outs) * vol[-1].astype(np.float32)
def film_smoke_step(in_ch, n_cond, width, patch, batch, lr, weight_decay, device):
    model = FiLMUNet3D(in_ch, n_cond, width).to(device); opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay); scaler = make_scaler(device)
    x = torch.randn(batch, in_ch, *patch, device=device); z = torch.randn(batch, n_cond, device=device); y = (torch.rand(batch, 1, *patch, device=device) > 0.95).float(); mk = torch.ones_like(y)
    with torch.autocast(device_type=("cuda" if device.type == "cuda" else "cpu"), enabled=(device.type == "cuda")): loss = dice_bce_loss(model(x, z), y, mk)
    scaler.scale(loss).backward(); scaler.step(opt); scaler.update(); assert torch.isfinite(loss), "non-finite FiLM loss"
    return {"parameters": int(sum(p.numel() for p in model.parameters())), "loss": float(loss)}

def asd_mm(pred, truth, spacing):
    if pred.sum() == 0 or truth.sum() == 0: return np.nan
    def surface(m): return m & ~binary_erosion(m)
    sp, st = surface(pred), surface(truth); dt_t = distance_transform_edt(~st, sampling=spacing); dt_p = distance_transform_edt(~sp, sampling=spacing)
    return float(np.concatenate([dt_t[sp], dt_p[st]]).mean())

def patient_scores(c, p, pred):
    truth = c["lesion_full"]; mask = c["mask"]; ml = c["voxel_ml"]
    tp = int((pred & truth).sum()); fp = int((pred & ~truth).sum()); fn = int((~pred & truth).sum()); tn = int((~pred & ~truth & mask).sum())
    dsc = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 1.0
    tv, pv = float(truth.sum() * ml), float(pred.sum() * ml); lf1, cdiff, _ = official_lesion_metrics(truth, pred, empty_value=1.0)
    y = truth[mask].astype(int); mask_pos, mask_neg = int(y.sum()), int(y.size - y.sum()); auc = float(roc_auc_score(y, p)) if 0 < mask_pos < y.size else np.nan; ap = float(average_precision_score(y, p)) if 0 < mask_pos < y.size else np.nan
    cov = float((truth & mask).sum() / truth.sum()) if truth.sum() else np.nan; bound = 2 * cov / (1 + cov) if truth.sum() else np.nan
    return {"dice": dsc, "f1_voxel": dsc, "precision": tp / (tp + fp) if (tp + fp) else np.nan, "recall": tp / (tp + fn) if (tp + fn) else np.nan, "specificity": tn / (tn + fp) if (tn + fp) else np.nan,
            "lesion_ml": tv, "pred_ml": pv, "abs_vol_err_ml": abs(pv - tv), "signed_vol_err_ml": pv - tv, "lesion_ge5ml": tv >= 5.0, "pred_empty": bool(pred.sum() == 0), "truth_empty": bool(truth.sum() == 0),
            "lesion_f1": lf1, "lesion_count_diff": cdiff, "asd_mm": asd_mm(pred, truth, VOXEL_MM), "fm_auroc": auc, "fm_avg_precision": ap, "lesion_coverage_by_mask": cov, "lesion_ml_outside_mask": float((truth & ~mask).sum() * ml), "mask_dice_bound": bound, "mask_pos": mask_pos, "mask_neg": mask_neg, "tp": tp, "fp": fp, "fn": fn}

ALWAYS_FINITE = ["dice", "f1_voxel", "abs_vol_err_ml", "signed_vol_err_ml", "lesion_ml", "pred_ml", "lesion_f1", "lesion_count_diff", "lesion_ml_outside_mask", "mask_pos", "mask_neg", "tp", "fp", "fn"]

CONDITIONAL_NAN = {"recall": "truth_empty", "lesion_coverage_by_mask": "truth_empty", "mask_dice_bound": "truth_empty", "fm_auroc": "mask_one_class", "fm_avg_precision": "mask_one_class", "precision": "pred_empty", "specificity": "never", "asd_mm": "either_empty"}

ALL_METRIC_COLS = ALWAYS_FINITE + list(CONDITIONAL_NAN) + ["lesion_ge5ml", "pred_empty", "truth_empty"]

def fold_valid(path, recipes, held, shuffle=None, fold=None, train_seed=None):
    try: df = pd.read_csv(path)
    except Exception: return False
    need = ["fingerprint", "shuffle", "fold", "train_seed", "recipe", "case"] + ALL_METRIC_COLS
    if any(c not in df for c in need) or (df.fingerprint != FINGERPRINT).any(): return False
    if shuffle is not None and not ((df.shuffle == shuffle).all() and (df.fold == fold).all() and (df.train_seed == train_seed).all()): return False
    expected = {(r, c) for r in recipes for c in held}; got = list(zip(df.recipe, df.case))
    if len(got) != len(expected) or set(got) != expected or not np.isfinite(df[ALWAYS_FINITE].values).all(): return False
    for col, cond in CONDITIONAL_NAN.items():
        bad = df[col].isna() & ~({"truth_empty": df.truth_empty, "pred_empty": df.pred_empty, "either_empty": df.truth_empty | df.pred_empty, "mask_one_class": df.truth_empty | (df.mask_pos == 0) | (df.mask_neg == 0), "never": pd.Series(False, index=df.index)}[cond].astype(bool))
        if bad.any(): return False
    return True

def u_score_path(arm, seed_s, k, seed_t): return f"{RUN_DIR}/uscores/{arm}_s{seed_s}_f{k}_t{seed_t}.npz"

def save_u_scores(arm, seed_s, k, seed_t, width, best_epoch, per_case):
    tmp = f"{RUN_DIR}/uscores/tmp__{arm}_s{seed_s}_f{k}_t{seed_t}.npz"; np.savez_compressed(tmp, fingerprint=FINGERPRINT, arm=arm, width=width, best_epoch=best_epoch, cases=np.array(list(per_case)), **{f"raw__{c}": v for c, v in per_case.items()}); os.replace(tmp, u_score_path(arm, seed_s, k, seed_t)); assert u_scores_valid(arm, seed_s, k, seed_t)

def u_scores_valid(arm, seed_s, k, seed_t):
    p = u_score_path(arm, seed_s, k, seed_t)
    if not os.path.exists(p): return False
    try:
        z = np.load(p, allow_pickle=False); held = INNER[(seed_s, k)]["held"]
        if str(z["fingerprint"]) != FINGERPRINT or str(z["arm"]) != arm or float(z["width"]) not in SMOOTH_GRID_MM or sorted(z["cases"].tolist()) != sorted(held): return False
        return all(z[f"raw__{c}"].shape == (int(CACHE[c]["mask"].sum()),) and np.isfinite(z[f"raw__{c}"]).all() for c in held)
    except Exception: return False

def mask_path(recipe, seed_s, seed_t, case): return f"{RUN_DIR}/masks/{recipe}__s{seed_s}_t{seed_t}__{case}.npz"

def mask_valid(recipe, seed_s, k, seed_t, case):
    p = mask_path(recipe, seed_s, seed_t, case)
    if not os.path.exists(p): return False
    try:
        z = np.load(p, allow_pickle=False); shape = tuple(int(s) for s in z["shape"])
        return str(z["fingerprint"]) == FINGERPRINT and int(z["shuffle"]) == seed_s and int(z["fold"]) == k and int(z["train_seed"]) == seed_t and str(z["recipe"]) == recipe and shape == tuple(CACHE[case]["shape"])
    except Exception: return False

def save_mask(recipe, seed_s, k, seed_t, case, pred):
    if seed_s == MAP_SHUFFLE and seed_t == MAP_SEED:
        tmp = f"{RUN_DIR}/masks/tmp__{recipe}__s{seed_s}_t{seed_t}__{case}.npz"; np.savez_compressed(tmp, pred=np.packbits(pred), shape=np.array(pred.shape), fingerprint=FINGERPRINT, shuffle=seed_s, fold=k, train_seed=seed_t, recipe=recipe, voxel_mm=np.array(VOXEL_MM)); os.replace(tmp, mask_path(recipe, seed_s, seed_t, case))

def emit(rows, recipe, seed_s, k, seed_t, case, c, p, pred, note=""):
    save_mask(recipe, seed_s, k, seed_t, case, pred); rows.append(dict(fingerprint=FINGERPRINT, shuffle=seed_s, fold=k, train_seed=seed_t, case=case, recipe=recipe, note=note, **patient_scores(c, p, pred)))

def pr_of(c): return {"shape": c["shape"], "mask": c["mask"], "lesion_full": c["lesion_full"], "voxel_ml": c["voxel_ml"]}

def clinical_vectors(train_cases, fields):
    # standardized clinical vector per case: (value - mean)/std from the TRAINING patients, missing -> 0, plus one missing indicator per field
    if not fields: return None, 0, {}
    T = CLIN.loc[train_cases, fields].astype(float); mu, sd = T.mean(), T.std().replace(0, 1.0).fillna(1.0)
    def vec(case):
        v = CLIN.loc[case, fields].astype(float); z = ((v - mu) / sd).fillna(0.0).values; miss = v.isna().astype(float).values; return np.concatenate([z, miss]).astype(np.float32)
    return vec, 2 * len(fields), {"mean": mu.to_dict(), "std": sd.to_dict()}

def prepare(train_cases, keep_cases, seed, arm):
    spec = ACTIVE_ARMS[arm]; fields = GROUP_FIELDS.get(spec["group"], []) if spec["group"] else []
    caches = [CACHE[c] for c in train_cases]; norm = compute_normative(caches, seed=seed); scale = feature_scale(caches, norm, IDX20, seed=seed); vec, n_cond, stats = clinical_vectors(train_cases, fields)
    def make_vol(c):
        v = pad_to(feature_volume(CACHE[c], norm, IDX20, scale), PATCH)
        if spec["fusion"] == "broadcast":                                      # tiled constant channels inside the support mask, inserted before the mask channel
            z = vec(c); extra = np.zeros((len(z),) + v.shape[1:], np.float16); extra[:, v[-1] > 0] = z[:, None]; v = np.concatenate([v[:-1], extra, v[-1:]], 0)
        return v
    cond = (lambda c: vec(c)) if spec["fusion"] == "film" else None
    vols, labels, centres = {}, {}, {}
    for c in keep_cases:
        hc = CACHE[c]; vols[c] = make_vol(c); labels[c] = pad_to(hc["lesion_full"][None].astype(np.float16), PATCH)[0]; centres[c] = np.argwhere(hc["lesion_full"] & hc["mask"])
    in_ch = (next(iter(vols.values())) if vols else make_vol(train_cases[0])).shape[0]; return dict(norm=norm, scale=scale, vols=vols, labels=labels, centres=centres, make_vol=make_vol, cond=cond, n_cond=(n_cond if spec["fusion"] == "film" else 0), in_ch=in_ch, fields=fields, stats=stats)

def batch_from(cases, P, rng):
    xs, ys, ms, zs = [], [], [], []
    for _ in range(CNN["batch"]):
        c = cases[rng.integers(len(cases))]; v, y, pos = P["vols"][c], P["labels"][c], P["centres"][c]
        centre = pos[rng.integers(len(pos))] if (len(pos) and rng.random() < CNN["lesion_centred_fraction"]) else None
        a, b, d = sample_patch_origin(v.shape[1:], PATCH, rng, centre); xs.append(v[:, a:a + PATCH[0], b:b + PATCH[1], d:d + PATCH[2]].astype(np.float32)); ys.append(y[a:a + PATCH[0], b:b + PATCH[1], d:d + PATCH[2]].astype(np.float32)); ms.append(v[-1, a:a + PATCH[0], b:b + PATCH[1], d:d + PATCH[2]].astype(np.float32))
        if P["cond"] is not None: zs.append(P["cond"](c))
    z = torch.from_numpy(np.stack(zs)).to(TORCH_DEVICE) if zs else None
    return torch.from_numpy(np.stack(xs)).to(TORCH_DEVICE), torch.from_numpy(np.stack(ys))[:, None].to(TORCH_DEVICE), torch.from_numpy(np.stack(ms))[:, None].to(TORCH_DEVICE), z

def score_cases(model, cases, P):
    out = {}
    for c in cases:
        hc = CACHE[c]; v = P["vols"][c] if c in P["vols"] else P["make_vol"](c); full = predict_volume_c(model, v, PATCH, STRIDE, TORCH_DEVICE, batch=CNN["batch"], cond=(P["cond"](c) if P["cond"] is not None else None)); out[c] = full[:hc["shape"][0], :hc["shape"][1], :hc["shape"][2]][hc["mask"]].astype(np.float32)
    return out

def inner_dice(scores, cases, width):
    vals = []
    for c in cases:
        hc = CACHE[c]; pr = pr_of(hc); p = scores[c]; vals.append(dice(rule_topk_lexsort(pr, smooth_scores(pr, p, width), expected_volume_ml(pr, p)), hc["lesion_full"]))
    return float(np.mean(vals))

def save_ckpt(path, **state):
    tmp = f"{path}.{uuid.uuid4().hex}.tmp"; torch.save(state, tmp); os.replace(tmp, path)

def new_model(P, seed):
    torch.manual_seed(seed); return (FiLMUNet3D(P["in_ch"], P["n_cond"], CNN["width"], FILM_HIDDEN) if P["n_cond"] else SmallUNet3D(P["in_ch"], CNN["width"])).to(TORCH_DEVICE)

def train(train_cases, val_cases, P, epochs, tag, seed):
    model = new_model(P, seed); opt = torch.optim.AdamW(model.parameters(), lr=CNN["lr"], weight_decay=CNN["weight_decay"]); scaler = make_scaler(TORCH_DEVICE)
    rng_t = np.random.default_rng([seed, 7]); curve, best, best_epoch, wait, best_state, start = [], -1.0, 0, 0, None, 1; ck = f"{RUN_DIR}/ckpt/{tag}.pt"
    if os.path.exists(ck):
        s = torch.load(ck, map_location=TORCH_DEVICE, weights_only=False)
        if s.get("identity") == FINGERPRINT and s.get("tag") == tag:
            model.load_state_dict(s["model"]); opt.load_state_dict(s["optimizer"]); scaler.load_state_dict(s["scaler"]); rng_t.bit_generator.state = s["rng_state"]; curve, best, best_epoch, wait, best_state, start = s["curve"], s["best"], s["best_epoch"], s["wait"], s["best_state"], s["epoch"] + 1
            log(f"    [{tag}] resumed from epoch {s['epoch']}")
            if (val_cases and wait >= CNN["patience"]) or s["epoch"] >= epochs:
                if best_state is not None: model.load_state_dict(best_state)
                return model, curve, best_epoch, best
    for ep in range(start, epochs + 1):
        model.train(); t0 = time.time(); losses = []
        for _ in range(CNN["patches_per_epoch"] // CNN["batch"]):
            x, y, mk, z = batch_from(train_cases, P, rng_t); opt.zero_grad(set_to_none=True)
            with torch.autocast(device_type=("cuda" if TORCH_DEVICE.type == "cuda" else "cpu"), enabled=(TORCH_DEVICE.type == "cuda")): loss = dice_bce_loss(forward_any(model, x, z), y, mk)
            scaler.scale(loss).backward(); scaler.step(opt); scaler.update(); losses.append(float(loss))
        rec = {"epoch": ep, "train_loss": float(np.mean(losses)), "train_seconds": time.time() - t0}
        if val_cases and (ep % CNN["val_every"] == 0 or ep == epochs):
            sc = score_cases(model, val_cases, P); rec["val_dice_own_unsmoothed"] = inner_dice(sc, val_cases, 0.0)
            if rec["val_dice_own_unsmoothed"] > best: best, best_epoch, wait, best_state = rec["val_dice_own_unsmoothed"], ep, 0, {k_: v.detach().cpu().clone() for k_, v in model.state_dict().items()}
            else: wait += CNN["val_every"]
        rec["epoch_seconds_total"] = time.time() - t0; curve.append(rec)
        save_ckpt(ck, identity=FINGERPRINT, tag=tag, epoch=ep, model=model.state_dict(), optimizer=opt.state_dict(), scaler=scaler.state_dict(), rng_state=rng_t.bit_generator.state, curve=curve, best=best, best_epoch=best_epoch, wait=wait, best_state=best_state)
        if ep in (1, 2) or ep % 10 == 0: log(f"    [{tag}] epoch {ep}: loss {rec['train_loss']:.3f}" + (f", inner-val Dice {rec['val_dice_own_unsmoothed']:.3f} (best {best:.3f} @ {best_epoch})" if "val_dice_own_unsmoothed" in rec else "") + f" [{rec['epoch_seconds_total']:.0f}s]")
        if val_cases and wait >= CNN["patience"]: log(f"    [{tag}] early stop at epoch {ep}"); break
    if best_state is not None: model.load_state_dict(best_state)
    return model, curve, best_epoch, best

def train_predict(arm, seed_s, k, seed_t):
    # operation 1: validated raw scores for one arm, fold and seed; never repeated while the score file is valid
    P_ = INNER[(seed_s, k)]; train_cases, held = P_["train"], P_["held"]
    if u_scores_valid(arm, seed_s, k, seed_t): return
    t0 = time.time(); tag_i, tag_f = f"{arm}_inner_s{seed_s}_f{k}_t{seed_t}", f"{arm}_final_s{seed_s}_f{k}_t{seed_t}"
    Pi = prepare(P_["inner_train"], P_["inner_train"] + P_["inner_val"], seed_t, arm)
    model_i, curve_i, best_epoch, best_val = train(P_["inner_train"], P_["inner_val"], Pi, CNN["max_epochs"], tag_i, seed_t)
    sc_i = score_cases(model_i, P_["inner_val"], Pi); width = max(SMOOTH_GRID_MM, key=lambda w: inner_dice(sc_i, P_["inner_val"], w)); del Pi, model_i
    if best_epoch == 0: best_epoch = 1
    Pf = prepare(train_cases, train_cases, seed_t, arm); model_f, curve_f, _, _ = train(train_cases, [], Pf, best_epoch, tag_f, seed_t)
    scores = score_cases(model_f, held, Pf); save_u_scores(arm, seed_s, k, seed_t, width, best_epoch, scores)
    json.dump({"arm": arm, "fields": Pf["fields"], "fusion": ACTIVE_ARMS[arm]["fusion"], "in_channels": Pf["in_ch"], "n_cond": Pf["n_cond"], "clinical_stats": Pf["stats"], "inner_curve": curve_i, "final_curve": curve_f, "best_epoch": best_epoch, "best_inner_val": best_val, "width": width, "minutes": (time.time() - t0) / 60, "peak_gpu_gb": (torch.cuda.max_memory_allocated() / 1e9 if TORCH_DEVICE.type == "cuda" else None), "host_ram_free_gb": psutil.virtual_memory().available / 1e9}, open(f"{RUN_DIR}/ckpt/curves_{arm}_s{seed_s}_f{k}_t{seed_t}.json", "w"), indent=1, default=str)
    del Pf; [os.remove(f) for f in glob.glob(f"{RUN_DIR}/ckpt/{arm}_*_s{seed_s}_f{k}_t{seed_t}.pt")]
    log(f"TRAINED {arm} shuffle {seed_s} fold {k+1}/{N_FOLDS} seed {seed_t} in {(time.time()-t0)/60:.1f} min | best epoch {best_epoch} (inner Dice {best_val:.3f}) | smoothing {width} mm | host RAM free {psutil.virtual_memory().available/1e9:.0f} GB" + (f" | peak GPU {torch.cuda.max_memory_allocated()/1e9:.1f} GB" if TORCH_DEVICE.type == "cuda" else ""))

def postprocess(arm, seed_s, k, seed_t):
    # operation 2: fold CSV and masks from saved scores; never trains
    if not u_scores_valid(arm, seed_s, k, seed_t): return "no scores"
    held = INNER[(seed_s, k)]["held"]; z = np.load(u_score_path(arm, seed_s, k, seed_t), allow_pickle=False); width, best_epoch = float(z["width"]), int(z["best_epoch"]); scores = {c: z[f"raw__{c}"] for c in held}
    out = f"{RUN_DIR}/folds/unet_{arm}_s{seed_s}_f{k}_t{seed_t}.csv"; recs = [f"{arm}_raw", f"{arm}_smoothed"]; masks_ok = (seed_s != MAP_SHUFFLE or seed_t != MAP_SEED) or all(mask_valid(r, seed_s, k, seed_t, h) for r in recs for h in held)
    if fold_valid(out, recs, held, seed_s, k, seed_t) and masks_ok: return "complete"
    rows = []
    for h in held:
        c = CACHE[h]; pr = pr_of(c); p = scores[h]; ps = smooth_scores(pr, p, width); est = expected_volume_ml(pr, p)
        emit(rows, f"{arm}_raw", seed_s, k, seed_t, h, c, p, rule_topk_lexsort(pr, p, est), note=f"epochs {best_epoch}"); emit(rows, f"{arm}_smoothed", seed_s, k, seed_t, h, c, ps, rule_topk_lexsort(pr, ps, est), note=f"epochs {best_epoch}; smoothing {width} mm")
    df = pd.DataFrame(rows); df.to_csv(out + ".tmp", index=False); os.replace(out + ".tmp", out); assert fold_valid(out, recs, held, seed_s, k, seed_t); return "complete"
