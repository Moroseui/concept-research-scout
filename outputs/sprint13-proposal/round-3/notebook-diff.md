# Unreviewed candidate notebook diff

Original diff SHA256: a67bb73a24409fae1277087c282d1f6b89a951a3563fb172b501d5441cb68435

Full diff below, unchanged; wrapped in Markdown for publication.

```diff
--- original-safe/cell-0
+++ revised/cell-0
@@ -1,41 +1,16 @@
-# Sprint 13b: nnU-Net input preparation variants and the larger "L" configuration
+# Sprint13B revised proposal: normalization screen
 
-**What to do:** Runtime → Change runtime type → **A100 GPU** (High-RAM if offered), then **Runtime → Run all**. The first run stops on purpose after the smoke gate (`PAUSE_AFTER_SMOKE = True`): check the gate printout and the overlay pictures, send them to Claude if anything looks off, then set `PAUSE_AFTER_SMOKE = False` and Run all again. When Colab disconnects, reconnect and **Run all**: finished stages are skipped from their receipts on Drive, and an interrupted stage resumes from its last checkpoint.
+Question: do post-window patient transforms improve exploratory follow-up infarct prediction?
+Evidence: Sprint12 normalization +0.003 [-0.015,+0.020]; repeated tree normalization overlaps Sprint12b. See SPEC.proposed.md for all eight answers, numeric sources, alternatives and costs.
+Limitations: same 99 exposed development patients; one unseeded realization per arm, patient bootstrap excludes training and selection uncertainty. No untouched-test, clinical-use or novelty claim. Keep 25 final-evaluation and 24 reserve untouched.
+Next decision: STOP FOR OPERATOR REVIEW. This new copy is not authorized for real execution. The original is unchanged. Only the controller may apply this patch and run the synthetic contract; passing those checks does not establish full pipeline execution.
 
-**Needs from Sprint 12 (read only, never changed):** the folder `sprint12-nnunet-r8-PRIVATE`, for A1's published plans (imported by four arms) and A1's results (the baseline every arm is compared with). Before anything starts, the driver checks that A1's full results passed and that its published plans belong to that run; A1_L, which plans its own configuration, is checked against A1's patients, folds, windows and source files. The gate prints any software or GPU difference from A1's run.
+Proposed order: A1_repeat, A1_zscore, A1_histeq, all five frozen folds. Defer multiwin, L and pnormct; the family remains four primary contrasts. Both candidate-minus-A1 and candidate-minus-repeat 98.75% intervals must exclude zero in the same direction for better/worse. Missing membership or repeat means no non-provisional verdict. No retraining ratio or variance claim.
 
-**The question.** Sprint 12's best nnU-Net (A1: plain CT, the four perfusion maps and the CT angiogram, each clipped to one fixed window and scaled to 0 to 1) used only part of the winning team's recipe. This notebook tests, one change at a time and against A1 on the same 99 patients and folds, whether the missing pieces or a bigger model help.
+The self-contained combined cell requires an independently reviewed partition digest; it is deliberately unset because no authenticated digest was supplied. It validates exactly 99 unique members, folds 0–4 and shuffle 101 independently of FOLDS_TO_RUN, and checks complete one-to-one outer joins. Invalid tables raise rather than silently shrink the cohort.
 
-| Arm | What changes from Sprint 12 A1 | Why |
-|---|---|---|
-| **A1_zscore** | after the window, each channel is z-scored over the patient's brain mask (mean 0, SD 1 inside the brain; SD floored at 0.01) | the winners' normalization step |
-| **A1_histeq** | after the window, each channel is histogram-equalized over the patient's brain mask (256 bins on the window range) | the winners' best ablation row added histogram equalization |
-| **A1_repeat** | nothing: A1 trained again | measures how much Dice moves from retraining alone, the yardstick for every other difference |
-| **A1_multiwin** | each scan enters twice, through its A1 window and a second window (12 channels) | the professor's idea: other window ranges may carry extra information |
-| **A1_L** | nnU-Net's larger ResEnc L preset, planned by nnU-Net for this dataset (bigger network and patch) | the winners used ResEnc L; tests a larger model |
-| A1_pnormct (optional, not in the default list) | the four maps and the plain CT rescaled against the patient's own reference tissue, as Sprint 12's A1_pnorm_v2 but now including the CT | asks whether per-patient normalization of the CT adds anything |
+Coverage is never inferred from all-zero maps. Pure helpers retain valid zeros and intersect raw finite values with supplied support. Actual perfusion transforms remain held until item4 supplies reviewed acquisition coverage and a bound loader. Structural transforms use finite brain support. Empty/constant supports produce finite helper fallbacks and stop the pipeline for review. Optional pnorm remains held.
 
-For the four perfusion maps, the z-score and histogram statistics use only the brain voxels the perfusion scan covers; uncovered voxels get the outside-brain value 0, so the transform does not depend on how much of the brain the perfusion scan covered. z-score and histogram equalization are not combined in one arm: z-scoring after histogram equalization only shifts and rescales an already uniform distribution, which a network absorbs in its first layer.
+Item4 conditions: independently reviewed revised bytes; authenticated membership/partition pin, baseline plans and environment receipts; actual coverage provenance and loader review; separately authorized smoke/recovery execution; measured per-arm timing, fit, disk and cost projection before full-run admission. Settings stop before mounting Drive. No patient work, GPU/Modal job, spending, 13A rerun or successor dispatch is authorized by this item2.
 
-**The second windows (multi-window arm), fixed before any results.** The first windows are A1's (plain CT 0 to 80 HU, CBF 0 to 35, CBV 0 to 10, MTT 0 to 20, Tmax 0 to 7 s, angiogram 0 to 90 HU).
-
-| Scan | Second window | Reason |
-|---|---|---|
-| plain CT | 20 to 50 HU | narrow stroke window: stretches the grey and white matter range where early infarct darkening is a few HU |
-| CBF | 0 to 100 | the first window saturates at 35, so normal and high flow look identical; the wider window keeps that contrast |
-| CBV | 0 to 4 | normal CBV is about 2 to 4; the narrow window spreads the low range where the infarct core sits |
-| MTT | 0 to 12 s | normal MTT is about 4 to 6 s; spreads the clinically relevant range |
-| Tmax | 0 to 20 s | 0 to 7 s saturates every delayed voxel; the wider window separates 6 to 10 s from over 10 s, the thresholds used clinically |
-| angiogram | 0 to 300 HU | 0 to 90 shows tissue; the wider window shows vessels and collaterals |
-
-**Comparisons, designated before any results.** Primary: each of A1_zscore, A1_histeq, A1_multiwin and A1_L minus Sprint 12 A1, on Dice, with Bonferroni 98.75% intervals over these four. Retraining yardstick: A1_repeat minus Sprint 12 A1. Secondary (only if run): A1_pnormct minus Sprint 12 A1_pnorm_v2. Everything else (each arm against the tree, the small U-Net and A1_repeat) is exploratory. Intervals come from resampling patients and do not capture training variability; that is what A1_repeat is for. **Verdict rule:** an arm is called better (or worse) only if its 98.75% interval against Sprint 12 A1 excludes 0 with all 99 patients scored; it counts as an improvement only if the same test against A1_repeat points the same way. The combined cell prints both, plus each difference as a multiple of the retraining change.
-
-**What it does, in order:** smoke stages (12 patients, 5 epochs) for every arm, each rehearsing recovery from a lost VM; the automatic gate (preflight geometry, recovery, plan import checked against Sprint 12's published plans, training statistics, every patient scored), which also prints the clipping of every window, the transform records, and a projected run time; then the full stages (99 patients, 5 folds) in the same order; then the combined results.
-
-**Time.** About 2 to 3 hours for the smoke stages. Full stages: about 13 GPU hours per ResEnc M arm (A1_zscore, A1_histeq, A1_repeat, A1_multiwin; the 12-channel arm may be somewhat slower) and roughly 35 to 45 hours for A1_L, so about 90 to 100 GPU hours for the default list. The gate prints a measured projection; check Colab compute units before the full runs. To cut cost, remove arms from `ARMS_ORDER` (A1_L last if compute is short). A1_L needs an A100 (40 or 80 GB) and stops with a message on a smaller GPU.
-
-**Disk.** The 12-channel arm doubles the preprocessed data. Free disk is logged at the start of each stage, and each passed stage clears its local working folder.
-
-**Known limitations.** SynthStrip's brain mask misses brain in some patients, and every channel is blanked outside it in all arms equally. One training run per arm. All results are development results on the same 99 patients used throughout; the 25 reserved patients are never read.
-
-**Unchanged from the reviewed Sprint 12 r9 notebook** apart from: the per-arm preparation step (z-score or histogram equalization after the window, second windows), the plan import from Sprint 12's folder (with the per-channel plan fields rebuilt for the arm's channel count), the per-arm nnU-Net preset for A1_L, the Sprint 12 baseline in the comparisons, and this driver and combined-results cell.
+The existing cell6 lesion-metric fixtures and their semantics are preserved. Controller compile/sandbox/test receipts and carried-conditions.json must accompany the actual revised diff to independent review. They are not invented by the author.
--- original-safe/cell-2
+++ revised/cell-2
@@ -1,16 +1,17 @@
 # ---------------- settings (the only cell you might edit) ----------------
 DRIVE_BASE = "/content/drive/MyDrive/isles-pilot"
-RUN_BASE = f"{DRIVE_BASE}/sprint13-nnunet-PRIVATE"                    # new folder for this sprint's arms
+RUN_BASE = f"{DRIVE_BASE}/sprint13-nnunet-r2-PRIVATE"                    # new folder for this sprint's arms
 S12_RUN_BASE = f"{DRIVE_BASE}/sprint12-nnunet-r8-PRIVATE"             # read-only: Sprint 12's published A1 plans (imported) and its results (the baseline)
-# Arms run in this order (cheapest and most informative first; A1_L, the most expensive, last); delete any you do not want.
+# Proposed screen order. Extensions require a new reviewed decision; no execution authority.
 # "A1_pnormct" is defined but optional: add it to test per-patient normalization of the plain CT inside nnU-Net.
-ARMS_ORDER = ["A1_zscore", "A1_histeq", "A1_repeat", "A1_multiwin", "A1_L"]
+ARMS_ORDER = ["A1_repeat", "A1_zscore", "A1_histeq"]
 PLANS_FROM = {"A1_zscore": "A1_ct_maps_cta", "A1_histeq": "A1_ct_maps_cta", "A1_multiwin": "A1_ct_maps_cta", "A1_pnormct": "A1_ct_maps_cta", "A1_repeat": "A1_ct_maps_cta"}   # Sprint 12 A1's plans; A1_L plans its own
 FOLDS_TO_RUN = [0, 1, 2, 3, 4]
 RUN_SMOKE_FIRST = True
 PAUSE_AFTER_SMOKE = True                                              # first run: stop once after a passed smoke gate to inspect the inputs; then set False and Run all
 EPOCHS_FULL = 250                                                     # used only for the time projection
 PIPELINE = "/content/sprint13_pipeline.py"
+raise SystemExit("Analysis-only proposed copy. STOP FOR OPERATOR REVIEW; item4 execution conditions unfulfilled.")
 try:
     from google.colab import drive; drive.mount("/content/drive")
 except ImportError:
--- original-safe/cell-4
+++ revised/cell-4
@@ -5,7 +5,7 @@
 SMOKE = bool(STAGE_SMOKE)                   # set by the driver: smoke stage (12 patients, 5 epochs) or full stage
 SMOKE_RECOVERY_TEST = True                  # smoke only: after fold 0 trains, simulate a lost VM and prove validation-only recovery
 ALLOW_ENV_CHANGE_ON_RESUME = False          # a fold resumed under different torch/nnU-Net versions stops unless this is set deliberately
-CODE_VERSION = "sprint13-nnunet-r1"
+CODE_VERSION = "sprint13-nnunet-r2-item2-proposal"
 DRIVE_BASE = STAGE_DRIVE_BASE
 MIRROR = f"{DRIVE_BASE}/source-extract-v1"                                             # read-only source scans (Sprint 6)
 CACHE_DIR = f"{DRIVE_BASE}/feature-cache-2mm-v2"                                       # read-only: each patient's 2 mm grid and true infarct, for scoring
@@ -18,7 +18,13 @@
 LOCAL = "/content/work-sprint13"                                                       # nnU-Net raw, preprocessed and results folders live on the Colab disk
 SHUFFLE = 101
 FEATURE_CFG = {"target_mm": 2.0, "vessel_pct": 98.0, "core_thr": 0.30, "penumbra_tmax": 6.0, "schema": "isles24-features-2mm-v2"}
-# OMITTED ORIGINAL SPAN SHA256 8ffa5399e3c59a3fee6bb8a4cca50b89b57fdcd62163dcbf20a5c289ffa0674c
+# Membership-only private input; never included in a model workspace.
+import hashlib as _membership_hashlib, json as _membership_json
+_membership_bytes = open('/content/drive/MyDrive/isles-pilot/sprint13-inputs-PRIVATE/excluded_cases.json', "rb").read()
+assert _membership_hashlib.sha256(_membership_bytes).hexdigest() == 'ee8d4f96b0c16620450c0e7e2e6a56993d2ee68e20913c78a1bb8fe7af0f1ab2', "Excluded membership hash changed"
+EXCLUDED = _membership_json.loads(_membership_bytes)
+assert isinstance(EXCLUDED, list) and len(EXCLUDED) == 1, "Excluded membership count changed"
+del _membership_bytes
 NN = {"version": "2.8.1", "planner": "nnUNetPlannerResEncM", "plans": "nnUNetResEncUNetMPlans", "configuration": "3d_fullres",
       "base_trainer": "nnUNetTrainer_250epochs", "trainer": "nnUNetTrainer_250epochs_ckpt10", "save_every": 10,
       "smoke_base_trainer": "nnUNetTrainer_5epochs", "smoke_trainer": "nnUNetTrainer_5epochs_ckpt1", "smoke_save_every": 1,
--- original-safe/cell-8
+++ revised/cell-8
@@ -7,19 +7,53 @@
        "dwi": "train/derivatives/{c}/ses-02/{c}_ses-02_space-ncct_dwi.nii.gz", "adc": "train/derivatives/{c}/ses-02/{c}_ses-02_space-ncct_adc.nii.gz",
        "lesion": "train/derivatives/{c}/ses-02/{c}_ses-02_space-ncct_lesion-msk.nii.gz", "brain": "brainmask/{c}_brainmask.nii.gz"}
 def src(c, kind): return f"{MIRROR}/{PAT[kind].format(c=c)}"
+def coverage_support(values, brain, coverage=None):
+    values = np.asarray(values)
+    brain = np.asarray(brain, dtype=bool)
+    if values.shape != brain.shape:
+        raise ValueError("brain shape mismatch")
+    support = brain & np.isfinite(values)
+    if coverage is not None:
+        coverage = np.asarray(coverage)
+        if coverage.shape != values.shape or not np.isfinite(coverage).all() or not np.isin(coverage, [0, 1]).all():
+            raise ValueError("invalid spatial coverage mask")
+        support &= coverage.astype(bool)
+    return support, {"coverage_known": coverage is not None, "brain_n": int(brain.sum()),
+                     "support_n": int(support.sum()), "nonfinite_in_brain": int((brain & ~np.isfinite(values)).sum())}
+
 def zscore_in_brain(x, brain):
-    # the winners' step after windowing: z-score of the windowed channel over this patient's brain-mask voxels (mean 0, SD 1 there); outside the brain 0
-    v = x[brain]; m, s = (float(v.mean()), float(v.std())) if v.size else (0.0, 0.0)
-    if not np.isfinite(s) or s < 1e-6: return np.zeros_like(x, dtype=np.float32), {"mean": m, "sd": s, "fallback": "constant inside the brain"}
-    su = max(s, ZSCORE_MIN_SD); z = ((x - m) / su).astype(np.float32)
-    return z, {"mean": m, "sd": s, "sd_used": su, "fallback": None if s >= ZSCORE_MIN_SD else "SD floored", "z_min": float(z[brain].min()), "z_max": float(z[brain].max())}
+    x = np.asarray(x, dtype=float)
+    support, _ = coverage_support(x, brain)
+    v = x[support]; out = np.zeros_like(x, dtype=np.float32)
+    m, s = (float(v.mean()), float(v.std())) if v.size else (0., 0.)
+    su = max(s, ZSCORE_MIN_SD)
+    rec = {"mean": m, "sd": s, "sd_used": su, "n": int(v.size), "fallback": None}
+    if not v.size or s < 1e-6:
+        rec["fallback"] = "empty support" if not v.size else "constant support"
+        return out, rec
+    out[support] = (v - m) / su
+    rec.update({"fallback": "SD floored" if s < ZSCORE_MIN_SD else None,
+                "z_min": float(out[support].min()), "z_max": float(out[support].max())})
+    return out, rec
+
 def histeq_in_brain(x, brain, nbins=None):
-    # histogram equalization of the windowed channel over this patient's brain-mask voxels: each value -> the share of brain voxels at or below its bin
-    # (scikit-image's definition, cumulative share at the bin centre, with the bins fixed to the window range [0, 1]); outside the brain 0
-    nbins = nbins or HISTEQ_BINS; v = x[brain]
-    if v.size == 0 or float(v.std()) < 1e-6: return np.zeros_like(x, dtype=np.float32), {"fallback": "constant inside the brain"}
-    hist, edges = np.histogram(v, bins=nbins, range=(0.0, 1.0)); cdf = np.cumsum(hist).astype(np.float64); cdf /= cdf[-1]; centres = (edges[:-1] + edges[1:]) / 2
-    return np.interp(x, centres, cdf).astype(np.float32), {"fallback": None, "share_at_window_floor": float((v <= 1e-6).mean()), "share_at_window_ceiling": float((v >= 1 - 1e-6).mean())}
+    x = np.asarray(x, dtype=float)
+    support, _ = coverage_support(x, brain)
+    v = x[support]; out = np.zeros_like(x, dtype=np.float32)
+    if not v.size or float(v.std()) < 1e-6:
+        return out, {"fallback": "empty support" if not v.size else "constant support", "n": int(v.size)}
+    if np.any((v < 0) | (v > 1)):
+        raise ValueError("histogram input must be windowed to [0,1]")
+    bins = HISTEQ_BINS if nbins is None else nbins
+    hist, edges = np.histogram(v, bins=bins, range=(0., 1.))
+    cdf = np.cumsum(hist).astype(float); cdf /= cdf[-1]
+    out[support] = np.interp(v, (edges[:-1] + edges[1:]) / 2, cdf)
+    return out, {"fallback": None, "n": int(v.size), "share_at_window_floor": float((v <= 1e-6).mean()), "share_at_window_ceiling": float((v >= 1-1e-6).mean())}
+
+# No authenticated spatial coverage input is supplied with this proposal.
+# Do not infer coverage from map intensities. Item4 must review the actual
+# mask loader, provenance and identity binding before releasing this hold.
+COVERAGE_PROVENANCE = None
 WSTAT = {}
 def window01(v, lo, hi):
     v = np.where(np.isfinite(v), v, lo); return ((np.clip(v, lo, hi) - lo) / (hi - lo)).astype(np.float32)
@@ -34,10 +68,7 @@
     assert v.ndim == 3, f"{path}: expected a single 3-D volume, found shape {v.shape}"
     return img, v
 def pnorm_levels(c, brain):
-    # reference tissue candidates, admission images only: brain with Tmax <= 6 s, then the whole brain; voxels whose four perfusion maps are all zero are never reference
-    maps = {k: load3d(src(c, k))[1].astype(np.float32) for k in ("cbf", "cbv", "mtt", "tmax")}
-    all_zero = np.all([np.nan_to_num(maps[k]) == 0 for k in maps], axis=0); t = maps["tmax"]
-    return [("brain with Tmax <= 6 s", brain & np.isfinite(t) & (t >= 0) & (t <= PNORM_NN["tmax_delayed_s"]) & ~all_zero), ("whole brain", brain & ~all_zero)], all_zero
+    raise RuntimeError("Item4 hold: optional pnorm reference coverage requires a separately reviewed input binding")
 def pnorm_channel(v, kind, pref, brain):
     # robust z-score for one channel, with per-channel validity, a fixed low-variation fallback, and a full record; no data and invalid values -> 0
     out, rec = _pnorm_channel(v, kind, pref[0], brain)
@@ -69,11 +100,15 @@
     elif ch in WINDOWS:
         out = window01(v, *WINDOWS[ch]); wb = out[brain]; WSTAT[ch] = {"clip_low": float((wb <= 1e-6).mean()), "clip_high": float((wb >= 1 - 1e-6).mean())}   # clipping measured on the windowed values, before any transform
         if A.get("prep", "window") != "window":
-            # statistics over the brain voxels this scan covers: for the perfusion maps, voxels where all four maps are zero (outside the perfusion coverage) are left out
-            # and get the outside-brain value 0, so the transform does not depend on how much of the brain the perfusion scan covered
-            cov = (brain & ~pref[1]) if kind in PERF_KINDS else brain
-            out, PREC[ch] = (zscore_in_brain if A["prep"] == "window_zscore" else histeq_in_brain)(out, cov)
-            out = np.where(cov, out, 0.0).astype(np.float32); PREC[ch]["no_coverage_share"] = float((brain & ~cov).sum() / max(int(brain.sum()), 1))
+            support, coverage_meta = coverage_support(v, brain, coverage=None)
+            # v is the raw channel, before window01 replaces non-finite values.
+            if kind in PERF_KINDS and not coverage_meta["coverage_known"]:
+                raise RuntimeError("Item4 hold: authenticated perfusion coverage and loader unavailable")
+            out, PREC[ch] = (zscore_in_brain if A["prep"] == "window_zscore" else histeq_in_brain)(out, support)
+            PREC[ch].update(coverage_meta)
+            PREC[ch]["coverage_provenance"] = "brain-mask-only structural channel" if kind not in PERF_KINDS else COVERAGE_PROVENANCE
+            if PREC[ch].get("fallback") in ("empty support", "constant support"):
+                raise RuntimeError("transform has empty/constant valid support; stop for review")
     else:
         fin = np.isfinite(v[brain]).mean(); sd = float(np.nanstd(np.where(brain, v, np.nan)))
         assert fin >= MRI_MIN_FINITE and sd > MRI_MIN_SD, f"{c}: {kind} unusable inside the brain (finite {fin:.1%}, sd {sd:.3g})"
@@ -92,7 +127,7 @@
 def write_case(c):
     ref, _ = load3d(src(c, "ncct")); bimg, b = load3d(src(c, "brain")); assert same_grid(bimg, ref), f"{c}: brain mask shape or affine differs from the plain CT"
     brain = b > 0.5; ml = float(brain.sum() * np.prod(ref.header.get_zooms()[:3]) / 1000); assert BRAIN_ML_RANGE[0] <= ml <= BRAIN_ML_RANGE[1], f"{c}: brain mask volume {ml:.0f} ml outside {BRAIN_ML_RANGE}"
-    stats = {}; PREC.clear(); pref = pnorm_levels(c, brain) if (A.get("pnorm") or A.get("prep", "window") != "window") else None   # perfusion coverage is also needed by the post-window transforms
+    stats = {}; PREC.clear(); pref = pnorm_levels(c, brain) if A.get("pnorm") else None   # perfusion coverage is also needed by the post-window transforms
     for i, k in enumerate(A["channels"]):
         arr = prep_channel(c, k, ref, brain, pref); save_nii(arr, ref, f"{RAW}/imagesTr/{c}_{i:04d}.nii.gz", np.float32); v = arr[brain]
         stats[k] = {**WSTAT.get(k, {"clip_low": float((v <= 1e-6).mean()), "clip_high": float((v >= 1 - 1e-6).mean())}), "sd": float(v.std())}
@@ -123,10 +158,10 @@
 SOURCE_STAMP = {c: {k: ([_sha(src(c, k))] if k in ("brain", "lesion") else _stat(src(c, k))) for k in sorted(set(KINDS))} for c in STUDY}   # masks by content; large images by size and modification time
 CHANNEL_STAMP = {k: hashlib.sha256(json.dumps({c: SOURCE_STAMP[c][k] for c in STUDY}, sort_keys=True).encode()).hexdigest()[:12] for k in sorted(set(KINDS))}
 CACHE_IDENTITY = hashlib.sha256(json.dumps({c: _sha(f"{CACHE_DIR}/{c}.npz") for c in STUDY}, sort_keys=True).encode()).hexdigest()[:12]
-IDENTITY = {"code_version": CODE_VERSION, "arm": ARM, "channels": A["channels"], "prep": A.get("prep", "window"), "channel_sources": {ch: src_kind(ch) for ch in A["channels"]}, "histeq_bins": HISTEQ_BINS if A.get("prep") == "window_histeq" else None, "zscore_min_sd": ZSCORE_MIN_SD if A.get("prep") == "window_zscore" else None, "transform_region": "brain; perfusion maps: brain covered by the perfusion scan" if A.get("prep", "window") != "window" else None, "windows": {k: WINDOWS[k] for k in A["channels"] if k in WINDOWS}, "mri_clip_z": MRI_CLIP_Z if any(k not in WINDOWS for k in A["channels"]) else None,
+IDENTITY = {"code_version": CODE_VERSION, "realization_id": "s13b-screen-r2-realization1", "training_rng": "unseeded; train_seed is pairing label only", "environment": ENV, "coverage_provenance": COVERAGE_PROVENANCE, "arm": ARM, "channels": A["channels"], "prep": A.get("prep", "window"), "channel_sources": {ch: src_kind(ch) for ch in A["channels"]}, "histeq_bins": HISTEQ_BINS if A.get("prep") == "window_histeq" else None, "zscore_min_sd": ZSCORE_MIN_SD if A.get("prep") == "window_zscore" else None, "transform_region": "finite brain; perfusion held pending authenticated spatial coverage" if A.get("prep", "window") != "window" else None, "windows": {k: WINDOWS[k] for k in A["channels"] if k in WINDOWS}, "mri_clip_z": MRI_CLIP_Z if any(k not in WINDOWS for k in A["channels"]) else None,
             "cases": STUDY, "splits": splits(), "nnunet": {k: NN[k] for k in ("version", "planner", "plans", "configuration")}, "trainer": TRAINER, "base_trainer": BASE_TRAINER, "plans_from": A["plans_from"], "smoke": SMOKE,
             "source_inventory": CHANNEL_STAMP, "scoring_cache_identity": CACHE_IDENTITY, "checks": {"brain_ml": BRAIN_ML_RANGE, "mri_min_finite": MRI_MIN_FINITE, "lesion_agree_min": LESION_AGREE_MIN, "affine_atol": AFFINE_ATOL},
-            "pnorm": ({"channels": A["pnorm"], **PNORM_NN, "reference": "brain with Tmax <= 6 s and not all-zero perfusion, then whole brain; admission images only"} if A.get("pnorm") else None)}
+            "pnorm": ({"channels": A["pnorm"], **PNORM_NN, "reference": "held pending authenticated coverage/reference policy; admission images only"} if A.get("pnorm") else None)}
 FINGERPRINT = hashlib.sha256(json.dumps(IDENTITY, sort_keys=True).encode()).hexdigest()[:10]
 # local working folders are named by the run identity, so a changed configuration never reuses old images, plans or weights
 LOCAL_RUN = f"{LOCAL}/{ARM}-{FINGERPRINT}"
--- original-safe/cell-20
+++ revised/cell-20
@@ -17,7 +17,7 @@
 S12_HANDOFF = lambda smoke: f"{S12_RUN_BASE}/plans_handoff/A1_ct_maps_cta{'_smoke' if smoke else ''}_nnUNetResEncUNetMPlans.json"
 missing = [S12_HANDOFF(s) for s in ((True, False) if RUN_SMOKE_FIRST else (False,)) if not os.path.exists(S12_HANDOFF(s))]
 assert not missing, f"Sprint 12 A1's published plans are missing, e.g. {missing[:2]}; check S12_RUN_BASE (nothing was started)"
-try: _base = json.load(open(f"{S12_RUN_BASE}/stages/A1_ct_maps_cta.json")); base_ok = bool(_base.get("passed")) and set(FOLDS_TO_RUN) <= set(_base.get("folds", []))
+try: _base = json.load(open(f"{S12_RUN_BASE}/stages/A1_ct_maps_cta.json")); base_ok = bool(_base.get("passed")) and sorted(_base.get("folds", [])) == list(range(5))
 except Exception: _base, base_ok = {}, False
 assert base_ok, "Sprint 12 A1's full stage receipt is missing or incomplete, so no arm could be compared with the baseline; check S12_RUN_BASE (nothing was started)"
 _H = json.load(open(S12_HANDOFF(False)))
--- original-safe/cell-22
+++ revised/cell-22
@@ -1,32 +1,90 @@
 # ---------------- combined results: Sprint 13 arms against the Sprint 12 baseline (self-contained: can be run on its own after the settings cell) ----------------
 import os, json, glob, hashlib
 import numpy as np, pandas as pd
-P8 = json.load(open(f"{DRIVE_BASE}/sprint8-seeds-features-PRIVATE/run-875c56c278/partitions.json")); SHUFFLE = 101
-HELD = {int(k.split("_")[1]): v["held"] for k, v in P8.items() if int(k.split("_")[0]) == SHUFFLE}
-N_ALL = len({c for k in FOLDS_TO_RUN for c in HELD[k]})                # every development patient in the planned folds (99)
+def validate_full_folds(table, held):
+    """Exact full-cohort contract, independent of the execution schedule."""
+    if set(held) != set(range(5)):
+        raise ValueError("expected frozen folds 0 through 4")
+    expected = [(c, k, 101) for k in range(5) for c in held[k]]
+    if any(len(held[k]) == 0 for k in range(5)) or len(expected) != 99:
+        raise ValueError("expected 99 members in five nonempty folds")
+    members = [r[0] for r in expected]
+    if len(set(members)) != 99:
+        raise ValueError("duplicate or overlapping frozen members")
+    if not {"case", "fold", "shuffle"}.issubset(table.columns):
+        raise ValueError("membership columns missing")
+    keys = table[["case", "fold", "shuffle"]]
+    if len(keys) != 99 or keys.isna().any().any() or keys.case.duplicated().any():
+        raise ValueError("missing, extra, null or duplicate rows")
+    if set(keys.itertuples(index=False, name=None)) != set(expected):
+        raise ValueError("row membership, fold or shuffle mismatch")
+
+def verdict_from_intervals(base_ci, repeat_ci, complete=True):
+    """Conjunctive exploratory screen; no retraining-noise estimate."""
+    normalized = []
+    for ci in (base_ci, repeat_ci):
+        try:
+            arr = np.asarray(ci, dtype=float)
+        except (ValueError, TypeError) as e:
+            raise ValueError("invalid interval") from e
+        if arr.shape != (3,) or not np.isfinite(arr).all() or arr[1] > arr[2]:
+            raise ValueError("malformed, reversed or nonfinite interval")
+        normalized.append(arr)
+    base_ci, repeat_ci = normalized
+    if not complete:
+        return "provisional"
+    if base_ci[1] > 0 and repeat_ci[1] > 0:
+        return "better"
+    if base_ci[2] < 0 and repeat_ci[2] < 0:
+        return "worse"
+    return "no clear difference"
+
+# Required pin is supplied by a separately reviewed item4 binding, never learned
+# from observed result rows or automatically set to the current file's hash.
+FROZEN_PARTITIONS_SHA256 = None
+partition_path = f"{DRIVE_BASE}/sprint8-seeds-features-PRIVATE/run-875c56c278/partitions.json"
+if not isinstance(FROZEN_PARTITIONS_SHA256, str) or len(FROZEN_PARTITIONS_SHA256) != 64:
+    raise RuntimeError("Item4 hold: independently reviewed partition digest is missing")
+partition_bytes = open(partition_path, "rb").read()
+if hashlib.sha256(partition_bytes).hexdigest() != FROZEN_PARTITIONS_SHA256:
+    raise ValueError("frozen partition identity mismatch")
+P8 = json.loads(partition_bytes); SHUFFLE = 101
+HELD = {int(k.split("_")[1]): tuple(v["held"]) for k, v in P8.items() if int(k.split("_")[0]) == 101}
+# Also validate the pinned partition itself, before opening result tables.
+validate_full_folds(pd.DataFrame([(c,k,101) for k in HELD for c in HELD[k]], columns=["case","fold","shuffle"]), HELD)
+N_ALL = 99
 LABEL = {"A1_ct_maps_cta": "S12 A1: windows, ResEnc M (baseline)", "A1_pnorm_v2": "S12 A1_pnorm_v2: per-patient normalization of the 4 maps",
          "A1_zscore": "A1_zscore: windows + z-score", "A1_histeq": "A1_histeq: windows + histogram equalization", "A1_multiwin": "A1_multiwin: two windows per scan (12 channels)",
          "A1_pnormct": "A1_pnormct: per-patient normalization of the 4 maps and the plain CT", "A1_repeat": "A1_repeat: the baseline retrained", "A1_L": "A1_L: windows, ResEnc L"}
 TREE, UNET = "reference tree (Sprint 8, seed 1)", "image-only U-Net (Sprint 9, seed 1)"
 def arm_table(base, arm):
-    # validated fold tables for a full stage: its receipt's identity, one row per expected held-out patient, every planned fold
+    # validated fold tables for a full stage: its receipt's identity, one row per expected held-out patient, all five frozen folds
     try: r = json.load(open(f"{base}/stages/{arm}.json"))
     except Exception: return None, None
     if not r.get("passed"): return None, r
+    folds = r.get("folds", [])
+    if len(folds) != len(set(folds)) or not set(folds) <= set(range(5)):
+        raise ValueError("duplicate or unexpected receipt folds")
     rows = []
-    for k in r["folds"]:
+    for k in folds:
         try:
             d = pd.read_csv(f"{r['run_dir']}/folds/{r['recipe']}_s{SHUFFLE}_f{k}.csv", dtype={"fingerprint": str, "plans_digest": str, "case": str, "recipe": str})
             ok = (sorted(d.case) == sorted(HELD[k]) and not d.case.duplicated().any() and (d.fingerprint.astype(str) == r["fingerprint"]).all() and (d.plans_digest.astype(str) == str(r["plans_digest"])).all()
-                  and (d.recipe == r["recipe"]).all() and np.isfinite(d[["dice", "lesion_f1", "abs_vol_err_ml"]].values.astype(float)).all() and os.path.exists(f"{r['run_dir']}/model_bundle/fold_{k}/fold_receipt.json"))
+                  and (d.fold == k).all() and (d.shuffle == 101).all() and (d.recipe == r["recipe"]).all() and np.isfinite(d[["dice", "lesion_f1", "abs_vol_err_ml"]].values.astype(float)).all() and os.path.exists(f"{r['run_dir']}/model_bundle/fold_{k}/fold_receipt.json"))
         except Exception: ok = False
         if ok: rows.append(d)
-    return (pd.concat(rows) if rows else None), r
+    if len(rows) != len(folds):
+        raise ValueError("receipt claims a missing or invalid fold table")
+    table = pd.concat(rows) if rows else None
+    if table is not None:
+        validate_full_folds(table, HELD)
+    return table, r
 def other(glob_, recipe):
     fs = sorted(glob.glob(glob_)); o = pd.concat([pd.read_csv(f, dtype={"fingerprint": str, "case": str, "recipe": str}) for f in fs]) if fs else pd.DataFrame()
     if not len(o): return None
     o = o[(o.recipe == recipe) & (o.shuffle == SHUFFLE) & (o.train_seed == 1)]
     if o.duplicated(["fold", "case"]).any() or ("fingerprint" in o and o.fingerprint.nunique() > 1): print(f"  {recipe}: duplicate rows or rows from more than one run; left out"); return None
+    validate_full_folds(o, HELD)
     return o
 def _seed(*a): return int(hashlib.sha256("|".join(map(str, a)).encode()).hexdigest()[:8], 16)
 def boot(v, stat, *key, level=95.0, n=2000):
@@ -41,7 +99,7 @@
 for base, arm in [(S12_RUN_BASE, "A1_ct_maps_cta"), (S12_RUN_BASE, "A1_pnorm_v2")] + [(RUN_BASE, a) for a in ARMS_ORDER]:
     d, r = arm_table(base, arm); REC[arm] = r
     done = sorted(d.fold.unique().tolist()) if d is not None else []
-    missing[arm] = [k for k in FOLDS_TO_RUN if k not in done]
+    missing[arm] = [k for k in range(5) if k not in done]
     if d is not None: TAB[arm] = d
 TAB[TREE] = other(f"{DRIVE_BASE}/sprint8-seeds-features-PRIVATE/run-875c56c278/folds/part1_s{SHUFFLE}_f*_t1.csv", "D_noslice_smoothed")
 TAB[UNET] = other(f"{DRIVE_BASE}/sprint9-unet-PRIVATE/run-0a60362503/folds/unet_U_base_s{SHUFFLE}_f*_t1.csv", "U_base_smoothed")
@@ -61,11 +119,14 @@
 PRIMARY = ["A1_zscore", "A1_histeq", "A1_multiwin", "A1_L"]          # designated before any results: each minus the Sprint 12 baseline, on Dice; the family stays 4 even if an arm is not run
 BONF = 100 - 5.0 / len(PRIMARY)                                      # 98.75% intervals for the primaries (Bonferroni over the 4), from 10,000 resamples
 def pair(a, b):
-    m = TAB[a].merge(TAB[b], on=["shuffle", "fold", "case"], suffixes=("_a", "_b"), validate="one_to_one")
+    validate_full_folds(TAB[a], HELD); validate_full_folds(TAB[b], HELD)
+    m = TAB[a].merge(TAB[b], on=["shuffle", "fold", "case"], how="outer", indicator=True, suffixes=("_a", "_b"), validate="one_to_one")
+    if len(m) != 99 or not (m["_merge"] == "both").all():
+        raise ValueError("incomplete outer join")
     return m.assign(d=m.dice_a - m.dice_b, l=m.lesion_f1_a - m.lesion_f1_b, v=m.abs_vol_err_ml_a - m.abs_vol_err_ml_b, p=m.precision_a - m.precision_b, r=m.recall_a - m.recall_b).groupby("case").agg(
         d=("d", "mean"), l=("l", "mean"), v=("v", "mean"), p=("p", "mean"), r=("r", "mean"))
 PAIRS = [(a, BASE, "PRIMARY") for a in PRIMARY]
-PAIRS += [("A1_repeat", BASE, "RETRAINING NOISE"), ("A1_pnormct", "A1_pnorm_v2", "SECONDARY")]
+PAIRS += [("A1_repeat", BASE, "RETRAINING SENSITIVITY"), ("A1_pnormct", "A1_pnorm_v2", "SECONDARY")]
 PAIRS += [(a, b, "exploratory") for a in ["A1_zscore", "A1_histeq", "A1_multiwin", "A1_pnormct", "A1_L"] for b in ("A1_repeat", TREE, UNET)]
 PAIRS += [("A1_pnormct", BASE, "exploratory")]
 crow = []
@@ -75,36 +136,44 @@
     if not len(g): continue
     dci = boot(g.d, np.mean, a, b, "d"); row = {"comparison": f"{name(a)}  minus  {name(b)}", "role": role, "patients": len(g), "Dice, 95%": fmt(dci)}
     if role == "PRIMARY":
-        # verdict (designated before results): the 98.75% interval against Sprint 12 A1 excludes 0; "holds against the retrained baseline" adds the same test against A1_repeat, same direction
-        bci = boot(g.d, np.mean, a, b, "d", level=BONF, n=10000); row[f"Dice, {BONF:g}% (Bonferroni)"] = fmt(bci); sig = int(np.sign(bci[1])) if (bci[1] > 0 or bci[2] < 0) else 0
-        if len(g) < N_ALL: row["verdict"] = f"provisional: {len(g)} of {N_ALL} patients"
-        else: row["verdict"] = {1: "better", -1: "worse", 0: "no clear difference"}[sig]
-        if "A1_repeat" in TAB and len(g) == N_ALL:
-            g2 = pair(a, "A1_repeat"); rci = boot(g2.d, np.mean, a, "A1_repeat", "d", level=BONF, n=10000); sig2 = int(np.sign(rci[1])) if (rci[1] > 0 or rci[2] < 0) else 0
-            row["vs A1_repeat, 98.75%"] = fmt(rci); row["holds against the retrained baseline"] = bool(sig != 0 and sig2 == sig) if len(g2) == N_ALL else "provisional"
+        bci = boot(g.d, np.mean, a, b, "d", level=BONF, n=10000)
+        row[f"Dice, {BONF:g}% (Bonferroni)"] = fmt(bci)
+        row.update(dict(zip(("base_estimate", "base_lower", "base_upper"), bci)))
+        if "A1_repeat" not in TAB:
+            row["verdict"] = verdict_from_intervals(bci, (0., 0., 0.), complete=False)
+            row["repeat_status"] = "missing; no joint verdict"
+        else:
+            # Membership and receipt identities must pass before a verdict.
+            for arm in (a, BASE, "A1_repeat"):
+                validate_full_folds(TAB[arm], HELD)
+                if not REC[arm].get("env") or not REC[arm].get("fingerprint") or not REC[arm].get("run_dir"):
+                    raise ValueError("missing run/environment identity")
+            if len({REC[x]["fingerprint"] for x in (a, BASE, "A1_repeat")}) != 3 or len({REC[x]["run_dir"] for x in (a, BASE, "A1_repeat")}) != 3:
+                raise ValueError("candidate, baseline and repeat must be distinct realizations")
+            g2 = pair(a, "A1_repeat")
+            rci = boot(g2.d, np.mean, a, "A1_repeat", "d", level=BONF, n=10000)
+            row["vs A1_repeat, 98.75%"] = fmt(rci)
+            row.update(dict(zip(("repeat_estimate", "repeat_lower", "repeat_upper"), rci)))
+            row["verdict"] = verdict_from_intervals(bci, rci)
     row.update({"better / worse / tied": f"{int((g.d > 0).sum())} / {int((g.d < 0).sum())} / {int((g.d == 0).sum())}", "lesion F1, 95%": fmt(boot(g.l, np.mean, a, b, "l")),
                 "precision (mean change)": fmt(boot(g.p, np.nanmean, a, b, "p")), "recall (mean change)": fmt(boot(g.r, np.mean, a, b, "r")),
                 "abs. volume error, median change, ml": fmt(boot(g.v, np.median, a, b, "v"), 1)})
     crow.append(row)
 CT = pd.DataFrame(crow)
 if len(CT):
-    order = {"PRIMARY": 0, "RETRAINING NOISE": 1, "SECONDARY": 2, "exploratory": 3}; CT = CT.sort_values("role", key=lambda s: s.map(order), kind="stable")
+    order = {"PRIMARY": 0, "RETRAINING SENSITIVITY": 1, "SECONDARY": 2, "exploratory": 3}; CT = CT.sort_values("role", key=lambda s: s.map(order), kind="stable")
     print(f"\nMatched differences (same patients and folds; first minus second; intervals from patient resampling, which do not capture training variability).")
     print(f"Primary, designated before results: each of {', '.join(PRIMARY)} minus the Sprint 12 baseline, on Dice, with {BONF:g}% intervals. Secondary: A1_pnormct minus A1_pnorm_v2 (only if A1_pnormct was run). All others exploratory.")
     pd.set_option("display.max_colwidth", 90); print(CT.fillna("").to_string(index=False))
     CT.to_csv(f"{RUN_BASE}/combined_paired_contrasts.csv", index=False)
 BY.to_csv(f"{RUN_BASE}/combined_by_model.csv", index=False)
-# ---- the retraining yardstick ----
+# ---- one descriptive retraining realization, not a variance estimate ----
 if "A1_repeat" in TAB and BASE in TAB:
-    m = TAB["A1_repeat"].merge(TAB[BASE], on=["shuffle", "fold", "case"], suffixes=("_a", "_b"), validate="one_to_one")
-    g = (m.dice_a - m.dice_b).groupby(m.case).mean(); y = abs(g.mean())
-    print(f"\nRetraining yardstick: training the identical baseline again changed mean Dice by {g.mean():+.3f} (one draw of retraining noise; individual patients moved by a median of {g.abs().median():.3f}).")
-    for a in PRIMARY:
-        if a in TAB:
-            dd = pair(a, BASE).d.mean(); print(f"    {name(a)}: mean Dice change {dd:+.3f} against Sprint 12 A1, {abs(dd) / y if y > 0 else float('inf'):.1f} times the retraining change")
-    print("    A primary counts as an improvement only if its verdict is 'better' and it holds against the retrained baseline (column above); a change no larger than the retraining change is reported as not distinguishable from retraining.")
-else:
-    print("\nRetraining yardstick: A1_repeat has no validated results, so the primary differences cannot be compared with retraining noise. Their intervals capture patient sampling only.")
+    g = pair("A1_repeat", BASE).d
+    print(f"Signed repeat-minus-A1 mean Dice: {g.mean():+.6f}. One unseeded realization; no noise ratio or equivalence inference.")
+print("Verdicts require both 98.75% intervals in the same direction. Four-arm family retained, even for unrun arms. Patient bootstrap conditions on fitted models and excludes training/selection uncertainty.")
+for arm in PRIMARY:
+    if arm not in TAB: print(f"{arm}: NOT RUN / no complete validated results; no verdict")
 # ---- software and GPU of each full run against Sprint 12 A1's (for inspection) ----
 b_env, b_gpu = (REC.get(BASE) or {}).get("env", {}), (REC.get(BASE) or {}).get("gpu")
 for a in ARMS_ORDER:
@@ -113,7 +182,7 @@
     diff = {k: (b_env.get(k), v) for k, v in r["env"].items() if k in b_env and b_env[k] != v}
     print(f"{a}: software {'identical to' if not diff else 'DIFFERENT from'} Sprint 12 A1's" + ("" if not diff else " (" + "; ".join(f"{k} {x} -> {y}" for k, (x, y) in diff.items()) + ")") + f"; GPU {r.get('gpu')} (baseline {b_gpu})")
 # ---- status ----
-if any(missing.get(a) for a in ARMS_ORDER + [BASE]): print("\nPROVISIONAL: validated results missing for " + "; ".join(f"{a} folds {m}" for a, m in missing.items() if m and (a in ARMS_ORDER or a == BASE)) + " (Run all again to recover or rescore)")
-else: print("\nAll arms, and the Sprint 12 baseline, have validated results for every planned fold.")
+if any(missing.get(a) for a in ARMS_ORDER + [BASE]): print("\nPROVISIONAL: validated results missing for " + "; ".join(f"{a} folds {m}" for a, m in missing.items() if m and (a in ARMS_ORDER or a == BASE)) + " (stop for review; do not rerun to fill gaps)")
+else: print("\nAll arms, and the Sprint 12 baseline, have validated results for all five frozen folds.")
 if missing.get("A1_pnorm_v2") and "A1_pnormct" in ARMS_ORDER: print("Note: Sprint 12's A1_pnorm_v2 has no validated results, so the secondary comparison is missing.")
 print(f"\nSaved {RUN_BASE}/combined_by_model.csv and combined_paired_contrasts.csv (aggregate only, no patient rows). Development results on the 99; the reserved 25 were not read.")

```
