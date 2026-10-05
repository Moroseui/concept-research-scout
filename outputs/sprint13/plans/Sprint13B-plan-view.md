# Derived scientific analysis view
Not the original executable notebook. Omitted spans are listed by hash and reason in the bound manifest. Original SHA256: 73f656d542c033df30fdfca8a36d1bd2899fc1563d9d4effdf9ea634de164ef7

## cells/0/source bytes 0:6692
# Sprint 13b: nnU-Net input preparation variants and the larger "L" configuration

**What to do:** Runtime → Change runtime type → **A100 GPU** (High-RAM if offered), then **Runtime → Run all**. The first run stops on purpose after the smoke gate (`PAUSE_AFTER_SMOKE = True`): check the gate printout and the overlay pictures, send them to Claude if anything looks off, then set `PAUSE_AFTER_SMOKE = False` and Run all again. When Colab disconnects, reconnect and **Run all**: finished stages are skipped from their receipts on Drive, and an interrupted stage resumes from its last checkpoint.

**Needs from Sprint 12 (read only, never changed):** the folder `sprint12-nnunet-r8-PRIVATE`, for A1's published plans (imported by four arms) and A1's results (the baseline every arm is compared with). Before anything starts, the driver checks that A1's full results passed and that its published plans belong to that run; A1_L, which plans its own configuration, is checked against A1's patients, folds, windows and source files. The gate prints any software or GPU difference from A1's run.

**The question.** Sprint 12's best nnU-Net (A1: plain CT, the four perfusion maps and the CT angiogram, each clipped to one fixed window and scaled to 0 to 1) used only part of the winning team's recipe. This notebook tests, one change at a time and against A1 on the same 99 patients and folds, whether the missing pieces or a bigger model help.

| Arm | What changes from Sprint 12 A1 | Why |
|---|---|---|
| **A1_zscore** | after the window, each channel is z-scored over the patient's brain mask (mean 0, SD 1 inside the brain; SD floored at 0.01) | the winners' normalization step |
| **A1_histeq** | after the window, each channel is histogram-equalized over the patient's brain mask (256 bins on the window range) | the winners' best ablation row added histogram equalization |
| **A1_repeat** | nothing: A1 trained again | measures how much Dice moves from retraining alone, the yardstick for every other difference |
| **A1_multiwin** | each scan enters twice, through its A1 window and a second window (12 channels) | the professor's idea: other window ranges may carry extra information |
| **A1_L** | nnU-Net's larger ResEnc L preset, planned by nnU-Net for this dataset (bigger network and patch) | the winners used ResEnc L; tests a larger model |
| A1_pnormct (optional, not in the default list) | the four maps and the plain CT rescaled against the patient's own reference tissue, as Sprint 12's A1_pnorm_v2 but now including the CT | asks whether per-patient normalization of the CT adds anything |

For the four perfusion maps, the z-score and histogram statistics use only the brain voxels the perfusion scan covers; uncovered voxels get the outside-brain value 0, so the transform does not depend on how much of the brain the perfusion scan covered. z-score and histogram equalization are not combined in one arm: z-scoring after histogram equalization only shifts and rescales an already uniform distribution, which a network absorbs in its first layer.

**The second windows (multi-window arm), fixed before any results.** The first windows are A1's (plain CT 0 to 80 HU, CBF 0 to 35, CBV 0 to 10, MTT 0 to 20, Tmax 0 to 7 s, angiogram 0 to 90 HU).

| Scan | Second window | Reason |
|---|---|---|
| plain CT | 20 to 50 HU | narrow stroke window: stretches the grey and white matter range where early infarct darkening is a few HU |
| CBF | 0 to 100 | the first window saturates at 35, so normal and high flow look identical; the wider window keeps that contrast |
| CBV | 0 to 4 | normal CBV is about 2 to 4; the narrow window spreads the low range where the infarct core sits |
| MTT | 0 to 12 s | normal MTT is about 4 to 6 s; spreads the clinically relevant range |
| Tmax | 0 to 20 s | 0 to 7 s saturates every delayed voxel; the wider window separates 6 to 10 s from over 10 s, the thresholds used clinically |
| angiogram | 0 to 300 HU | 0 to 90 shows tissue; the wider window shows vessels and collaterals |

**Comparisons, designated before any results.** Primary: each of A1_zscore, A1_histeq, A1_multiwin and A1_L minus Sprint 12 A1, on Dice, with Bonferroni 98.75% intervals over these four. Retraining yardstick: A1_repeat minus Sprint 12 A1. Secondary (only if run): A1_pnormct minus Sprint 12 A1_pnorm_v2. Everything else (each arm against the tree, the small U-Net and A1_repeat) is exploratory. Intervals come from resampling patients and do not capture training variability; that is what A1_repeat is for. **Verdict rule:** an arm is called better (or worse) only if its 98.75% interval against Sprint 12 A1 excludes 0 with all 99 patients scored; it counts as an improvement only if the same test against A1_repeat points the same way. The combined cell prints both, plus each difference as a multiple of the retraining change.

**What it does, in order:** smoke stages (12 patients, 5 epochs) for every arm, each rehearsing recovery from a lost VM; the automatic gate (preflight geometry, recovery, plan import checked against Sprint 12's published plans, training statistics, every patient scored), which also prints the clipping of every window, the transform records, and a projected run time; then the full stages (99 patients, 5 folds) in the same order; then the combined results.

**Time.** About 2 to 3 hours for the smoke stages. Full stages: about 13 GPU hours per ResEnc M arm (A1_zscore, A1_histeq, A1_repeat, A1_multiwin; the 12-channel arm may be somewhat slower) and roughly 35 to 45 hours for A1_L, so about 90 to 100 GPU hours for the default list. The gate prints a measured projection; check Colab compute units before the full runs. To cut cost, remove arms from `ARMS_ORDER` (A1_L last if compute is short). A1_L needs an A100 (40 or 80 GB) and stops with a message on a smaller GPU.

**Disk.** The 12-channel arm doubles the preprocessed data. Free disk is logged at the start of each stage, and each passed stage clears its local working folder.

**Known limitations.** SynthStrip's brain mask misses brain in some patients, and every channel is blanked outside it in all arms equally. One training run per arm. All results are development results on the same 99 patients used throughout; the 25 reserved patients are never read.

**Unchanged from the reviewed Sprint 12 r9 notebook** apart from: the per-arm preparation step (z-score or histogram equalization after the window, second windows), the plan import from Sprint 12's folder (with the per-channel plan fields rebuilt for the arm's channel count), the per-arm nnU-Net preset for A1_L, the Sprint 12 baseline in the comparisons, and this driver and combined-results cell.


## cells/1/source bytes 0:11
## Settings

## cells/10/source bytes 0:1984
%%writefile -a /content/sprint13_pipeline.py
# ---------------- 0. checks before any building or training (headers, brain masks, lesion agreement with the scoring cache) ----------------
t0 = time.time(); bad = []; agree = {}; in_brain = {}
for c in STUDY:
    ref = nib.load(src(c, "ncct"))
    for k in sorted(set(KINDS)):
        img = nib.load(src(c, k)); shp = img.shape
        if not (len(shp) == 3 or (len(shp) == 4 and shp[3] == 1)): bad.append(f"{c}: {k} has shape {shp}")
        elif not same_grid(img, ref): bad.append(f"{c}: {k} shape or affine differs from the plain CT")
    if bad: continue
    b = load3d(src(c, "brain"))[1] > 0.5; ml = float(b.sum() * np.prod(ref.header.get_zooms()[:3]) / 1000)
    if not BRAIN_ML_RANGE[0] <= ml <= BRAIN_ML_RANGE[1]: bad.append(f"{c}: brain mask volume {ml:.0f} ml")
    cc = load_cache(f"{CACHE_DIR}/{c}.npz", FEATURE_HASH, c); limg, lv = load3d(src(c, "lesion"))
    l2 = resample_from_to(nib.Nifti1Image((lv > 0.5).astype(np.uint8), limg.affine), (cc["shape"], cc["affine"]), order=0).get_fdata() > 0.5
    t = cc["lesion_full"]; s_ = int(l2.sum() + t.sum()); d = 1.0 if s_ == 0 else 2 * int((l2 & t).sum()) / s_; agree[c] = d
    ln = lv > 0.5; in_brain[c] = float((ln & b).sum() / ln.sum()) if ln.any() else 1.0
    if d < LESION_AGREE_MIN: bad.append(f"{c}: source lesion on the 2 mm grid agrees with the cached true infarct only at Dice {d:.4f}")
assert not bad, "preflight failed:\n  " + "\n  ".join(bad[:20])
log(f"preflight passed for {len(STUDY)} patients in {(time.time()-t0)/60:.1f} min: every file on the plain-CT grid, brain masks {BRAIN_ML_RANGE[0]}-{BRAIN_ML_RANGE[1]} ml, lesion agreement with the scoring cache min Dice {min(agree.values()):.4f}")
json.dump({"lesion_agreement": agree, "lesion_in_brain": in_brain}, open(f"{RUN_DIR}/qc/preflight.json", "w"), indent=1)
log(f"true infarct inside the brain mask: min {min(in_brain.values()):.1%} of its voxels, median {np.median(list(in_brain.values())):.1%}")



## cells/11/source bytes 0:164
### Pipeline file: 1-2. dataset, plans and preprocessing  
*This cell only writes code to `/content/sprint13_pipeline.py`; the driver below runs it once per stage.*

## cells/12/source bytes 0:12565
%%writefile -a /content/sprint13_pipeline.py
# ---------------- 1. build the nnU-Net dataset in this run's local folder (resumable, receipts per case) ----------------
os.makedirs(f"{RAW}/imagesTr", exist_ok=True); os.makedirs(f"{RAW}/labelsTr", exist_ok=True)
todo = [c for c in STUDY if not case_done(c)]; t0 = time.time()
for i, c in enumerate(todo, 1):
    write_case(c)
    if i % 10 == 0 or i == len(todo): log(f"  wrote {i}/{len(todo)} patients ({(time.time()-t0)/60:.1f} min)")
write_dataset_json(len(STUDY)); assert all(case_done(c) for c in STUDY)
try:                                                         # overlay images for a visual check: smallest, median and largest lesion
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    vols = {c: float((np.asanyarray(nib.load(f"{RAW}/labelsTr/{c}.nii.gz").dataobj) > 0).sum()) for c in STUDY}; order = sorted(vols, key=vols.get)
    for tag, c in (("smallest", order[0]), ("median", order[len(order) // 2]), ("largest", order[-1])):
        lab = np.asanyarray(nib.load(f"{RAW}/labelsTr/{c}.nii.gz").dataobj) > 0; z = int(np.argmax(lab.sum((0, 1)))) if lab.any() else lab.shape[2] // 2
        br = load3d(src(c, "brain"))[1][..., z] > 0.5
        fig, ax = plt.subplots(1, len(A["channels"]), figsize=(3 * len(A["channels"]), 3.2))
        for i, k in enumerate(A["channels"]):
            a = np.atleast_1d(ax)[i]; sl_ = np.asanyarray(nib.load(f"{RAW}/imagesTr/{c}_{i:04d}.nii.gz").dataobj)[..., z]; lo_, hi_ = (np.percentile(sl_[br], [1, 99]) if br.any() else (0.0, 1.0)); a.imshow(sl_.T, cmap="gray", origin="lower", vmin=lo_, vmax=max(hi_, lo_ + 1e-6))
            a.contour(br.T, [0.5], colors="c", linewidths=0.6); a.contour(lab[..., z].T, [0.5], colors="y", linewidths=0.8); a.set_title(k, fontsize=9); a.axis("off")
        fig.suptitle(f"{tag} lesion ({vols[c] * np.prod(nib.load(src(c, 'ncct')).header.get_zooms()[:3]) / 1000:.1f} ml): brain mask cyan, true infarct yellow", fontsize=9)
        fig.savefig(f"{RUN_DIR}/qc/overlay_{tag}.png", dpi=110, bbox_inches="tight"); plt.close(fig)
    log(f"overlays for a visual check saved in {RUN_DIR}/qc (smallest, median, largest lesion)")
except Exception as e: log(f"overlay images skipped: {e!r}")
# ---------------- input checks, before any planning or training ----------------
chan = {}; blank = []
for c in STUDY:
    for k, v in (json.load(open(case_receipt(c))).get("channel_stats") or {}).items():
        chan.setdefault(k, []).append(v)
        if v["sd"] < GATE["channel_sd_block"]: blank.append(f"{c}: {k}")
pf = json.load(open(f"{RUN_DIR}/qc/preflight.json")); lib_min = float(min(pf["lesion_in_brain"].values()))
clip_report = {k: {"median_clip_low": float(np.median([v["clip_low"] for v in vs])), "median_clip_high": float(np.median([v["clip_high"] for v in vs])), "median_sd": float(np.median([v["sd"] for v in vs])),
                   "patients_over_98pct_clipped": int(sum(1 for v in vs if max(v["clip_low"], v["clip_high"]) > GATE["clip_report"]))} for k, vs in chan.items()}
input_problems = [f"channel constant inside the brain: {', '.join(blank[:5])}"] if blank else []
log(f"true infarct inside the brain mask (reported only, not a rule): min {lib_min:.1%}")
if A.get("pnorm"):
    recs_ = {c: json.load(open(case_receipt(c))).get("pnorm") or {} for c in STUDY}
    for k in A["pnorm"]:
        lv = collections.Counter(f"{r.get(k, {}).get('level')} / {r.get(k, {}).get('fallback')}" for r in recs_.values())
        cl = [r[k]["clip_high"] for r in recs_.values() if r.get(k, {}).get("clip_high") is not None]; nd = [r[k]["nodata_share"] for r in recs_.values() if r.get(k, {}).get("nodata_share") is not None]
        log(f"per-patient normalization, {k}: reference / scale used {dict(lv)}; median share clipped high {np.median(cl) if cl else float('nan'):.2%}; median share no data or invalid (encoded 0) {np.median(nd) if nd else float('nan'):.1%}")
    json.dump(recs_, open(f"{RUN_DIR}/qc/pnorm_stats.json", "w"), indent=1)
if A.get("prep", "window") != "window":
    recs_ = {c: json.load(open(case_receipt(c))).get("prep") or {} for c in STUDY}
    for k in A["channels"]:
        fb = collections.Counter(str(r.get(k, {}).get("fallback")) for r in recs_.values())
        log(f"{A['prep']}, {k}: fallbacks {dict(fb)} (None = transform applied)")
    json.dump(recs_, open(f"{RUN_DIR}/qc/prep_stats.json", "w"), indent=1)
json.dump({"problems": input_problems, "clipping_report": clip_report, "lesion_in_brain_min": lib_min}, open(f"{RUN_DIR}/qc/input_check.json", "w"), indent=1)
log("input check (clipping reported for inspection, not a rule): " + "; ".join(f"{k} clipped low {v['median_clip_low']:.0%} / high {v['median_clip_high']:.0%} (median), {v['patients_over_98pct_clipped']} patients >98% clipped" for k, v in clip_report.items()))
if input_problems:
    json.dump({"arm": ARM, "smoke": SMOKE, "passed": False, "problems": ["input check before training: " + p for p in input_problems], "fingerprint": FINGERPRINT, "folds": STAGE_FOLDS_PLANNED,
               "run_dir": RUN_DIR, "checks": {"input_check": {"problems": input_problems, "clipping_report": clip_report}}, "utc": datetime.datetime.utcnow().isoformat()}, open(STAGE_RECEIPT, "w"), indent=1)
    raise RuntimeError(f"input check failed before training ({ARM}{' smoke' if SMOKE else ''}): {input_problems}; nothing was trained")
# ---------------- 2. plans: own planning (A1, C), or A1's plans reused exactly (A0) ----------------
plans_file = f"{PRE}/{NN['plans']}.json"; handoff_name = lambda arm: f"{HANDOFF}/{arm}{'_smoke' if SMOKE else ''}_{NN['plans']}.json"; handoff_file = handoff_name(ARM)
def plans_digest(p): return hashlib.sha256(json.dumps(json.load(open(p)) if isinstance(p, str) else p, sort_keys=True).encode()).hexdigest()[:12]
def data_ready():
    try: r = json.load(open(f"{PRE}/preprocess_done.json"))
    except Exception: return False
    return os.path.exists(plans_file) and os.path.exists(f"{PRE}/splits_final.json") and r.get("fingerprint") == FINGERPRINT and r.get("plans_digest") == plans_digest(plans_file)
def check_same_inputs(h):
    # same patients, folds, source scans, first windows, brain masks and labels as the published run h (Sprint 12 A1);
    # the channels' preparation (and, for the multi-window arm, their number) differs by design and is recorded in this run's identity
    problems = []; src_kinds = sorted(set(src_kind(ch) for ch in A["channels"]))
    if h.get("smoke") != SMOKE: problems.append("smoke flag")
    if h.get("cases") != STUDY or h.get("splits") != splits(): problems.append("patients or folds")
    if not set(src_kinds) <= set(h.get("channels", [])): problems.append(f"source scans {src_kinds} not all used by {h.get('arm')} ({h.get('channels')})")
    if any(h.get("windows", {}).get(k) != WINDOWS.get(k) for k in src_kinds): problems.append("first windows of the source scans")
    if any(h.get("source_inventory", {}).get(k) != CHANNEL_STAMP.get(k) for k in src_kinds + ["brain", "lesion", "ncct"]): problems.append("source files of shared scans")
    return problems
def check_handoff(h):
    # the imported plans must come from the intended source arm, with the same inputs (above), nnU-Net settings and an intact plans digest
    problems = check_same_inputs(h)
    if h.get("arm") != A["plans_from"]: problems.append(f"arm {h.get('arm')}")
    if h.get("nnunet") != IDENTITY["nnunet"]: problems.append("nnU-Net settings")
    if h.get("plans_digest") != plans_digest(h["plans"]): problems.append("plans digest")
    return problems
if A["plans_from"] is None:                                  # an arm that plans its own configuration (A1_L) must still use Sprint 12 A1's patients, folds, windows and source files
    probs_ = check_same_inputs(json.load(open(BASELINE_HANDOFF)))
    assert not probs_, f"{ARM} would not be comparable with Sprint 12 A1: {probs_}"
    log("  inputs match Sprint 12 A1's: patients, folds, first windows, source files")
IMPORTED = None
if not data_ready():
    shutil.rmtree(PRE, ignore_errors=True); t0 = time.time()
    if A["plans_from"] is None:
        sh(["nnUNetv2_plan_and_preprocess", "-d", str(DID), "-pl", NN["planner"], "-c", NN["configuration"], "-np", str(NP), "--verify_dataset_integrity"], f"{RUN_DIR}/nnunet_prep.log", env=NN_ENV)
    else:
        src_handoff = f"{HANDOFF_SRC.get(A['plans_from'], HANDOFF)}/{A['plans_from']}{'_smoke' if SMOKE else ''}_{NN['plans']}.json"
        sh(["nnUNetv2_extract_fingerprint", "-d", str(DID), "-np", str(NP), "--verify_dataset_integrity"], f"{RUN_DIR}/nnunet_prep.log", env=NN_ENV)
        waited = 0.0
        while not os.path.exists(src_handoff):
            assert waited < PLANS_WAIT_H * 60, f"{A['plans_from']}'s plans did not appear at {src_handoff} within {PLANS_WAIT_H} h; run that arm first (in the same SMOKE mode)"
            if waited % 30 == 0: log(f"  waiting for {A['plans_from']}'s plans on Drive ({waited:.0f} min so far)")
            time.sleep(120); waited += 2
        H = json.load(open(src_handoff)); probs_ = check_handoff(H)
        assert not probs_, f"{A['plans_from']}'s published plans do not match this run: {probs_}; re-run {A['plans_from']} with the same patients, folds, software and source files"
        IMPORTED = {"source_arm": H["arm"], "source_fingerprint": H["fingerprint"], "plans_digest": H["plans_digest"]}
        src_plans = H["plans"]; plans = json.loads(json.dumps(src_plans)); plans["dataset_name"] = DS_NAME
        # per-channel plan fields follow this dataset (its channel count can differ from the source arm's): no nnU-Net normalisation for any channel, intensity statistics from this dataset's fingerprint
        n_ch = len(A["channels"]); fpj = json.load(open(f"{PRE}/dataset_fingerprint.json"))
        for cname_, cfg_ in plans.get("configurations", {}).items():
            if "normalization_schemes" in cfg_:
                assert set(cfg_["normalization_schemes"]) <= {"NoNormalization"}, f"source plans use {set(cfg_['normalization_schemes'])} in {cname_}; expected NoNormalization only"
                cfg_["normalization_schemes"] = ["NoNormalization"] * n_ch
            if "use_mask_for_norm" in cfg_: cfg_["use_mask_for_norm"] = [False] * n_ch
        if "foreground_intensity_properties_per_channel" in plans: plans["foreground_intensity_properties_per_channel"] = fpj["foreground_intensity_properties_per_channel"]
        os.makedirs(PRE, exist_ok=True); shutil.copyfile(f"{RAW}/dataset.json", f"{PRE}/dataset.json"); json.dump(plans, open(plans_file, "w"), indent=1)
        sh(["nnUNetv2_preprocess", "-d", str(DID), "-plans_name", NN["plans"], "-c", NN["configuration"], "-np", str(NP)], f"{RUN_DIR}/nnunet_prep.log", env=NN_ENV)
        mine, theirs = json.load(open(plans_file))["configurations"][NN["configuration"]], src_plans["configurations"][NN["configuration"]]
        diff = [k for k in ("patch_size", "spacing", "batch_size", "architecture") if mine.get(k) != theirs.get(k)]
        assert not diff, f"plans differ from {A['plans_from']} in {diff}"; log(f"  plans reused from {A['plans_from']}: patch, spacing, batch size and architecture identical")
    json.dump(splits(), open(f"{PRE}/splits_final.json", "w"), indent=1)
    json.dump({"fingerprint": FINGERPRINT, "plans_digest": plans_digest(plans_file), "imported_from": IMPORTED, "utc": datetime.datetime.utcnow().isoformat()}, open(f"{PRE}/preprocess_done.json", "w"))
    if IMPORTED: log(f"  imported plans from {IMPORTED['source_arm']} run {IMPORTED['source_fingerprint']} (plans digest {IMPORTED['plans_digest']})")
    log(f"  planned and preprocessed in {(time.time()-t0)/60:.0f} min")
cfgp = json.load(open(plans_file))["configurations"][NN["configuration"]]
log(f"realised plan: spacing {cfgp.get('spacing')}, patch {cfgp.get('patch_size')}, batch {cfgp.get('batch_size')}")
PLANS_DIGEST = plans_digest(plans_file)
if A["plans_from"] is None:                                  # publish plans, with their provenance, for any arm that reuses them (atomic)
    tmp = handoff_file + ".tmp"; json.dump({"arm": ARM, "fingerprint": FINGERPRINT, "smoke": SMOKE, "cases": STUDY, "splits": splits(), "nnunet": IDENTITY["nnunet"], "channels": A["channels"], "windows": {k: WINDOWS.get(k) for k in A["channels"]},
                                             "source_inventory": CHANNEL_STAMP, "plans": json.load(open(plans_file)), "plans_digest": PLANS_DIGEST, "utc": datetime.datetime.utcnow().isoformat()}, open(tmp, "w")); os.replace(tmp, handoff_file)
    log(f"  plans published for reuse: {handoff_file}")



## cells/13/source bytes 0:138
### Pipeline file: 3. training  
*This cell only writes code to `/content/sprint13_pipeline.py`; the driver below runs it once per stage.*

## cells/14/source bytes 0:9059
%%writefile -a /content/sprint13_pipeline.py
# ---------------- 3. train each fold (resumable; final weights mirrored at once; validation-only recovery) ----------------
KEEP = ("checkpoint_final.pth", "checkpoint_latest.pth", "progress.png", "debug.json")
class Sync:
    # copy checkpoints and logs to Drive every NN['sync_s'] seconds, only once a file has stopped changing
    def __init__(self, local, remote): self.local, self.remote, self.stop_ev, self.peak_gb = local, remote, threading.Event(), None; os.makedirs(remote, exist_ok=True)
    def sample_gpu(self):
        try:
            out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20).stdout.split()
            if out: self.peak_gb = max(self.peak_gb or 0.0, max(float(x) for x in out) / 1024)
        except Exception: pass
    def once(self):
        self.sample_gpu()
        for f in list(KEEP) + [os.path.basename(p) for p in glob.glob(f"{self.local}/training_log*.txt")]:
            p = f"{self.local}/{f}"
            if not os.path.exists(p): continue
            s1 = (os.path.getsize(p), os.path.getmtime(p)); time.sleep(5)
            if not os.path.exists(p) or (os.path.getsize(p), os.path.getmtime(p)) != s1: continue
            q = f"{self.remote}/{f}"
            if os.path.exists(q) and os.path.getmtime(q) >= s1[1] and os.path.getsize(q) == s1[0]: continue
            shutil.copy2(p, q + ".tmp"); os.replace(q + ".tmp", q)
    def final_now(self):
        # copy checkpoint_final.pth as soon as it exists and has stopped changing (nnU-Net writes it just before validation starts)
        p, q = f"{self.local}/checkpoint_final.pth", f"{self.remote}/checkpoint_final.pth"
        if not os.path.exists(p) or (os.path.exists(q) and os.path.getsize(q) == os.path.getsize(p) and os.path.getmtime(q) >= os.path.getmtime(p)): return
        s1 = (os.path.getsize(p), os.path.getmtime(p)); time.sleep(5)
        if os.path.exists(p) and (os.path.getsize(p), os.path.getmtime(p)) == s1: shutil.copy2(p, q + ".tmp"); os.replace(q + ".tmp", q); log("    final checkpoint mirrored to Drive")
    def run(self):
        last = time.time()
        while not self.stop_ev.wait(min(60, NN["sync_s"])):
            self.sample_gpu()
            try: self.final_now()
            except Exception as e: log(f"    final-checkpoint mirror skipped once: {e!r}")
            if time.time() - last < NN["sync_s"]: continue
            try: self.once()
            except Exception as e: log(f"    checkpoint sync skipped once: {e!r}")
            last = time.time()
    def start(self): self.t = threading.Thread(target=self.run, daemon=True); self.t.start()
    def stop(self): self.stop_ev.set(); self.t.join(timeout=60); self.once()
def fold_complete_on_drive(k): return bundle_ok(k, PLANS_DIGEST)
def record_train_stats(k, fd, peak=None):
    # epochs, losses and peak memory from every training log for this fold: local, mirrored checkpoints folder and model bundle (so a lost VM does not lose them)
    logs = {}
    for folder in (bundle_dir(k), f"{RUN_DIR}/checkpoints/fold_{k}", fd):
        for p in glob.glob(f"{folder}/training_log*.txt"): logs[os.path.basename(p)] = p
    txt = "".join(open(p).read() for p in logs.values())
    ep = [float(x) for x in re.findall(r"Epoch time: ([0-9.]+) s", txt)]
    losses = [float(x) for x in re.findall(r"train_loss (-?[0-9.]+(?:e-?[0-9]+)?|nan|inf|-inf)", txt)]
    if not ep: return None
    st = json.load(open(STATS_PATH)) if os.path.exists(STATS_PATH) else {}; prev = st.get(str(k), {})
    peaks = [x for x in (prev.get("peak_gpu_gb"), peak) if x is not None]
    st[str(k)] = {"epochs_logged": len(ep), "median_epoch_s": float(np.median(ep)), "losses_logged": len(losses), "losses_finite": bool(losses) and bool(np.all(np.isfinite(losses))), "peak_gpu_gb": max(peaks) if peaks else None}
    json.dump(st, open(STATS_PATH + ".tmp", "w"), indent=1); os.replace(STATS_PATH + ".tmp", STATS_PATH)
    return st[str(k)]
def env_guard(k):
    p = f"{RUN_DIR}/checkpoints/fold_{k}/env.json"
    if os.path.exists(p):
        old = json.load(open(p))
        if {x: old.get(x) for x in ("nnunetv2", "torch")} != {x: ENV.get(x) for x in ("nnunetv2", "torch")}:
            assert ALLOW_ENV_CHANGE_ON_RESUME, f"fold {k} was started under {old}, now {ENV}; start a new run or set ALLOW_ENV_CHANGE_ON_RESUME deliberately"
            log(f"fold {k}: resuming under a different environment (allowed explicitly): {old} -> {ENV}")
    else: os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(ENV, open(p, "w"))
def publish_bundle(k, fd):
    # write to a temporary folder on Drive, verify every artifact, then move into place and write the receipt last
    b, tmpb = bundle_dir(k), bundle_dir(k) + ".tmp"; shutil.rmtree(tmpb, ignore_errors=True); os.makedirs(f"{tmpb}/validation")
    for f in ["checkpoint_final.pth", "progress.png", "debug.json"] + [os.path.basename(p) for p in glob.glob(f"{fd}/training_log*.txt")]:
        if os.path.exists(f"{fd}/{f}"): shutil.copy2(f"{fd}/{f}", f"{tmpb}/{f}")
    for p in glob.glob(f"{fd}/validation/*"): shutil.copy2(p, f"{tmpb}/validation/{os.path.basename(p)}")
    val = splits()[k]["val"]; bad = [c for c in val if not (readable_nii(f"{tmpb}/validation/{c}.nii.gz") and readable_npz(f"{tmpb}/validation/{c}.npz"))]
    assert not bad and os.path.getsize(f"{tmpb}/checkpoint_final.pth") > 0, f"fold {k}: unreadable or missing validation outputs {bad[:5]}"
    shutil.rmtree(b, ignore_errors=True); shutil.move(tmpb, b)
    json.dump({"fingerprint": FINGERPRINT, "plans_digest": PLANS_DIGEST, "cases": val, "env": ENV, "utc": datetime.datetime.utcnow().isoformat()}, open(f"{b}/fold_receipt.json.tmp", "w")); os.replace(f"{b}/fold_receipt.json.tmp", f"{b}/fold_receipt.json")
    for f in ("plans.json", "dataset.json", "dataset_fingerprint.json"):
        if os.path.exists(f"{MODEL_ROOT}/{f}"): shutil.copy2(f"{MODEL_ROOT}/{f}", f"{RUN_DIR}/model_bundle/{f}")
def run_fold(k):
    if fold_complete_on_drive(k):
        if not stats_ok([k]): record_train_stats(k, f"{MODEL_ROOT}/fold_{k}")          # rebuild missing statistics from the saved logs
        log(f"fold {k}: already complete on Drive; not retrained"); return "skipped"
    fd = f"{MODEL_ROOT}/fold_{k}"; os.makedirs(fd, exist_ok=True); ck = f"{RUN_DIR}/checkpoints/fold_{k}"; env_guard(k)
    for f in ("checkpoint_final.pth", "checkpoint_latest.pth"):                  # restore from Drive what the local disk has lost
        if not os.path.exists(f"{fd}/{f}") and os.path.exists(f"{ck}/{f}"): shutil.copy2(f"{ck}/{f}", f"{fd}/{f}")
    if os.path.exists(f"{fd}/checkpoint_final.pth"): mode, extra = "validation-only (training already finished)", ["--val"]
    elif os.path.exists(f"{fd}/checkpoint_latest.pth"): mode, extra = "resuming unfinished training", ["--c"]
    else: mode, extra = "training from scratch", []
    log(f"fold {k}: {mode} ({TRAINER})"); sync = Sync(fd, ck); sync.start(); t0 = time.time()
    try: sh(["nnUNetv2_train", str(DID), NN["configuration"], str(k), "-p", NN["plans"], "-tr", TRAINER, "--npz"] + extra, f"{RUN_DIR}/nnunet_train_fold{k}.log", env=NN_ENV)
    finally:
        sync.stop()
        try: record_train_stats(k, fd, sync.peak_gb)                                   # recorded whether the command succeeded or failed
        except Exception as e: log(f"    training statistics not recorded this time: {e!r}")
    assert os.path.exists(f"{fd}/checkpoint_final.pth"), f"fold {k} did not finish; the latest checkpoint is on Drive and a re-run resumes"
    publish_bundle(k, fd); assert fold_complete_on_drive(k), f"fold {k}: bundle failed verification"
    stk = record_train_stats(k, fd, sync.peak_gb) or {}; ep = [stk.get("median_epoch_s")] * stk.get("epochs_logged", 0) if stk else []
    log(f"fold {k}: done in {(time.time()-t0)/3600:.2f} h ({mode}); {len(ep)} epochs in the local logs, median {np.median(ep) if ep else float('nan'):.0f} s per epoch; peak GPU memory used {sync.peak_gb if sync.peak_gb is not None else float('nan'):.1f} GB (nvidia-smi, sampled each minute)")
    return mode
folds = [0] if SMOKE else FOLDS_TO_RUN
for k in folds: run_fold(k)
if SMOKE and SMOKE_RECOVERY_TEST:
    # simulate a lost VM after training finished: local folder gone, Drive bundle gone, only the mirrored final checkpoint left
    k = 0; shutil.rmtree(f"{MODEL_ROOT}/fold_{k}", ignore_errors=True); shutil.rmtree(bundle_dir(k), ignore_errors=True)
    assert os.path.exists(f"{RUN_DIR}/checkpoints/fold_{k}/checkpoint_final.pth"), "recovery test: the final checkpoint was not mirrored to Drive"
    mode = run_fold(k); ok = mode.startswith("validation-only") and fold_complete_on_drive(k)
    json.dump({"passed": ok, "mode": mode, "utc": datetime.datetime.utcnow().isoformat()}, open(f"{RUN_DIR}/qc/recovery_test.json", "w"))
    assert ok, f"recovery test failed: mode {mode}"; log("recovery test passed: after a simulated lost VM, the mirrored final weights were restored and only validation was run")



## cells/15/source bytes 0:137
### Pipeline file: 4. scoring  
*This cell only writes code to `/content/sprint13_pipeline.py`; the driver below runs it once per stage.*

## cells/16/source bytes 0:3767
%%writefile -a /content/sprint13_pipeline.py


# ---------------- 4. score every held-out prediction on the 2 mm grid, exactly as the trees ----------------
VOXEL_MM = (2.0, 2.0, 2.0)
def mask_path(recipe, seed_s, seed_t, case): return f"{RUN_DIR}/masks/{recipe}__s{seed_s}_t{seed_t}__{case}.npz"
READER = json.load(open(plans_file)).get("image_reader_writer")
READER_ORDER = {"SimpleITKIO": (2, 1, 0)}                     # SimpleITK arrays are (z, y, x); nibabel arrays are (x, y, z)
assert READER in READER_ORDER, f"unexpected nnU-Net reader {READER}; the probability axis order must be derived for it before scoring"
def native_prob(npz_path, seg_native):
    # axis order derived from the plans' reader, then verified: foreground Dice with the saved segmentation (or all-background agreement if it is empty)
    p = np.transpose(np.load(npz_path)["probabilities"][1].astype(np.float32), READER_ORDER[READER]); seg = seg_native > 0
    assert p.shape == seg.shape, f"{npz_path}: probability shape {p.shape} does not match the segmentation {seg.shape} after {READER} reordering"
    q = p > 0.5
    if seg.any():
        d = 2 * (q & seg).sum() / (q.sum() + seg.sum()); assert d >= 0.99, f"{npz_path}: probabilities disagree with the saved segmentation (foreground Dice {d:.3f})"
    else: assert not q.any(), f"{npz_path}: empty segmentation but probabilities above 0.5"
    return p
def score_case(c, k):
    b = f"{RUN_DIR}/model_bundle/fold_{k}/validation"; seg_img, sv = load3d(f"{b}/{c}.nii.gz"); seg = sv > 0.5
    cc = load_cache(f"{CACHE_DIR}/{c}.npz", FEATURE_HASH, c); grid = (cc["shape"], cc["affine"])
    pred = resample_from_to(nib.Nifti1Image(seg.astype(np.uint8), seg_img.affine), grid, order=0).get_fdata() > 0.5        # nearest neighbour, as the true infarct
    prob = resample_from_to(nib.Nifti1Image(native_prob(f"{b}/{c}.npz", seg), seg_img.affine), grid, order=1).get_fdata().astype(np.float32)
    truth_native = load3d(src(c, "lesion"))[1] > 0.5; tn = int(truth_native.sum()); sn = int(seg.sum())
    dice_native = 2 * int((seg & truth_native).sum()) / (tn + sn) if (tn + sn) else 1.0
    return cc, prob[cc["mask"]], pred, dice_native
def table_valid(k): return table_ok(k, PLANS_DIGEST)
for k in ([0] if SMOKE else range(N_FOLDS)):
    if not fold_complete_on_drive(k) or table_valid(k) is not None: continue
    rows = []
    for c in splits()[k]["val"]:
        cc, p, pred, dn = score_case(c, k)
        tmp = mask_path(RECIPE, SHUFFLE, MAP_SEED, c).replace("/masks/", "/masks/tmp__")
        np.savez_compressed(tmp, pred=np.packbits(pred), shape=np.array(pred.shape), fingerprint=FINGERPRINT, shuffle=SHUFFLE, fold=k, train_seed=MAP_SEED, recipe=RECIPE, voxel_mm=np.array(VOXEL_MM)); os.replace(tmp, mask_path(RECIPE, SHUFFLE, MAP_SEED, c))
        row = patient_scores(cc, p, pred); m_ = cc["mask"]; t_ = cc["lesion_full"]
        fp_in, tn_in = int((pred & ~t_ & m_).sum()), int((~pred & ~t_ & m_).sum()); row["specificity"] = tn_in / (tn_in + fp_in) if (tn_in + fp_in) else np.nan   # same support as the trees: the eligible tissue mask
        rows.append(dict(fingerprint=FINGERPRINT, plans_digest=PLANS_DIGEST, shuffle=SHUFFLE, fold=k, train_seed=1, case=c, recipe=RECIPE, specificity_support="eligible mask",
                         note=f"nnU-Net {ARM}; one training run; train_seed=1 is a pairing label only (nnU-Net training was not seeded)", dice_native=dn, pred_ml_outside_mask=float((pred & ~m_).sum() * cc["voxel_ml"]), **row))
    df = pd.DataFrame(rows); df.to_csv(fold_table_path(k) + ".tmp", index=False); os.replace(fold_table_path(k) + ".tmp", fold_table_path(k))
    log(f"fold {k}: scored {len(df)} held-out patients; mean Dice {df.dice.mean():.3f} (2 mm grid), {df.dice_native.mean():.3f} (native grid)")



## cells/17/source bytes 0:155
### Pipeline file: 5. results and stage receipt  
*This cell only writes code to `/content/sprint13_pipeline.py`; the driver below runs it once per stage.*

## cells/18/source bytes 0:7972
%%writefile -a /content/sprint13_pipeline.py
# ---------------- 5. results: this arm on its own, and matched comparisons ----------------
tabs = [t for t in (table_valid(k) for k in ([0] if SMOKE else range(N_FOLDS))) if t is not None]
assert tabs, "no validated fold tables yet"
DF = pd.concat(tabs); done = sorted(DF.fold.unique()); log(f"scored folds: {done} ({DF.case.nunique()} patients)")
if (SMOKE and len(done) < 1) or (not SMOKE and len(done) < N_FOLDS): print("PROVISIONAL: not every planned fold is scored yet")
def _seed(*a): return int(hashlib.sha256("|".join(map(str, a)).encode()).hexdigest()[:8], 16)
def boot(v, stat, *key):
    v = np.asarray(v, float); v = v[np.isfinite(v)]; idx = np.random.default_rng(_seed(*key)).integers(0, v.size, size=(2000, v.size)); b = stat(v[idx], axis=1)
    return float(stat(v)), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
fmt = lambda t, d=3: f"{t[0]:.{d}f} ({t[1]:.{d}f} to {t[2]:.{d}f})"
per = DF.groupby("case").agg(dice=("dice", "mean"), lf1=("lesion_f1", "mean"), vol=("abs_vol_err_ml", "mean"), signed=("signed_vol_err_ml", "mean"), prec=("precision", "mean"), rec=("recall", "mean"), dn=("dice_native", "mean"))
print(f"\n{RECIPE} on its own ({len(per)} patients):" + ("  FOLLOW-UP MRI DIAGNOSTIC BENCHMARK: the model sees the MRI the infarct was traced on; not a prediction and not a proven upper bound" if ARM == "C_mri_ceiling" else ""))
print(pd.DataFrame([{"Dice (95% CI)": fmt(boot(per.dice, np.mean, RECIPE, "d")), "Lesion F1 (95% CI)": fmt(boot(per.lf1, np.mean, RECIPE, "l")), "Abs. volume error, ml (95% CI)": fmt(boot(per.vol, np.median, RECIPE, "v"), 1),
                     "median signed, ml": round(float(per.signed.median()), 2), "precision": round(float(per.prec.mean()), 3), "recall": round(float(per.rec.mean()), 3), "Dice on native grid": round(float(per.dn.mean()), 3)}]).to_string(index=False))
def other(path_glob, recipe):
    fs = sorted(glob.glob(path_glob)); o = pd.concat([pd.read_csv(f, dtype={"fingerprint": str, "case": str, "recipe": str}) for f in fs]) if fs else pd.DataFrame()
    if not len(o): return o
    o = o[(o.recipe == recipe) & (o.shuffle == SHUFFLE) & (o.train_seed == 1)]
    if o.duplicated(["fold", "case"]).any(): print(f"  {recipe}: duplicate rows found; comparison skipped"); return o.iloc[0:0]
    if "fingerprint" in o and o.fingerprint.nunique() > 1: print(f"  {recipe}: rows from more than one run; comparison skipped"); return o.iloc[0:0]
    return o
COMP = [("reference tree (Sprint 8, seed 1)", other(f"{SPRINT8_RUN_DIR}/folds/part1_s{SHUFFLE}_f*_t1.csv", "D_noslice_smoothed")),
        ("image-only U-Net (Sprint 9, seed 1)", other(f"{SPRINT9_RUN_DIR}/folds/unet_U_base_s{SHUFFLE}_f*_t1.csv", "U_base_smoothed"))]
if not SMOKE: COMP.append(("Sprint 12 A1: windows only, M (baseline)", other(f"{S12_RUN_BASE}/A1_ct_maps_cta/folds/N_ct_maps_cta_s{SHUFFLE}_f*.csv", "N_ct_maps_cta")))   # a 5-epoch smoke model is not compared with it
for arm2, a2 in ARMS.items():
    if arm2 != ARM: COMP.append((f"{a2['recipe']} (this sprint)", other(f"{RUN_BASE}/{arm2}{'-SMOKE' if SMOKE else ''}/folds/{a2['recipe']}_s{SHUFFLE}_f*.csv", a2["recipe"])))
rows = []
for name, o in COMP:
    if not len(o): print(f"  {name}: no results available yet"); continue
    m = DF.merge(o, on=["shuffle", "fold", "case"], suffixes=("_a", "_b"), validate="one_to_one")
    if not len(m): continue
    g = m.assign(d=m.dice_a - m.dice_b, l=m.lesion_f1_a - m.lesion_f1_b, v=m.abs_vol_err_ml_a - m.abs_vol_err_ml_b).groupby("case").agg(d=("d", "mean"), l=("l", "mean"), v=("v", "mean"))
    rows.append({"comparison": f"{RECIPE} − {name}", "patients": len(g), "Dice": fmt(boot(g.d, np.mean, RECIPE, name, "d")), "better / worse / tied": f"{int((g.d > 0).sum())} / {int((g.d < 0).sum())} / {int((g.d == 0).sum())}",
                 "lesion F1": fmt(boot(g.l, np.mean, RECIPE, name, "l")), "median per-patient change in abs. volume error, ml": fmt(boot(g.v, np.median, RECIPE, name, "v"), 1)})
if rows:
    CON = pd.DataFrame(rows); CON.to_csv(f"{EXPORT_DIR}/paired_contrasts.csv", index=False); print("\nMatched differences (same patients and folds; first minus second; exploratory 95% intervals):"); print(CON.to_string(index=False))
per.to_csv(f"{EXPORT_DIR}/per_patient.csv"); json.dump({"fingerprint": FINGERPRINT, "arm": ARM, "folds_scored": [int(x) for x in done], "utc": datetime.datetime.utcnow().isoformat()}, open(f"{EXPORT_DIR}/run_reference.json", "w"), indent=1)
print(f"\nExports in {EXPORT_DIR}. Masks for the map cell: {RUN_DIR}/masks (recipe {RECIPE}). Specificity uses the eligible tissue mask for both pipelines; nnU-Net is otherwise not limited to that mask (see pred_ml_outside_mask). Whole-pipeline comparisons: inputs, resolution, loss, architecture and the eligible mask all differ from the trees. Development results on the 99; the reserved 25 were not read.")

# ---------------- stage receipt: the checks the driver's gate reads ----------------
st = json.load(open(f"{RUN_DIR}/qc/train_stats.json")) if os.path.exists(f"{RUN_DIR}/qc/train_stats.json") else {}
pf = json.load(open(f"{RUN_DIR}/qc/preflight.json"))
ic = json.load(open(f"{RUN_DIR}/qc/input_check.json"))
for k in STAGE_FOLDS_PLANNED:
    if not stats_ok([k]): record_train_stats(k, f"{MODEL_ROOT}/fold_{k}")              # last chance: rebuild from the mirrored logs
st = json.load(open(STATS_PATH)) if os.path.exists(STATS_PATH) else {}
imported = json.load(open(f"{PRE}/preprocess_done.json")).get("imported_from") if os.path.exists(f"{PRE}/preprocess_done.json") else None
peaks = [v["peak_gpu_gb"] for v in st.values() if v.get("peak_gpu_gb") is not None]
checks = {"folds_scored": all(table_valid(k) is not None for k in STAGE_FOLDS_PLANNED),
          "recovery_test": (json.load(open(f"{RUN_DIR}/qc/recovery_test.json")).get("passed") if os.path.exists(f"{RUN_DIR}/qc/recovery_test.json") else False) if (SMOKE and SMOKE_RECOVERY_TEST) else None,
          "plans_imported": imported if A["plans_from"] else None,
          "training_stats_all_folds": stats_ok(STAGE_FOLDS_PLANNED), "losses_finite": all(st.get(str(k), {}).get("losses_finite") for k in STAGE_FOLDS_PLANNED),
          "median_epoch_s": float(np.median([v["median_epoch_s"] for v in st.values()])) if st else None,
          "peak_gpu_gb": max(peaks) if peaks else None, "gpu_total_gb": GPU_TOTAL_GB,
          "lesion_in_brain_min": float(min(pf["lesion_in_brain"].values())), "input_problems": ic["problems"], "clipping_report": ic["clipping_report"],
          "memory_note": "smoke measurement is an estimate for the full run, whose dataset is planned separately" if SMOKE else "measured on this run"}
problems = []
if not checks["folds_scored"]: problems.append("not every planned fold was scored")
if SMOKE and SMOKE_RECOVERY_TEST and not checks["recovery_test"]: problems.append("recovery rehearsal did not pass")
if A["plans_from"] and not checks["plans_imported"]: problems.append("plans were not imported from the source arm")
if not checks["training_stats_all_folds"]: problems.append("training statistics missing for a planned fold")
elif not checks["losses_finite"]: problems.append("training losses not finite")
if ic["problems"]: problems.append("input check: " + "; ".join(ic["problems"]))
receipt = {"arm": ARM, "smoke": SMOKE, "passed": not problems, "problems": problems, "fingerprint": FINGERPRINT, "plans_digest": PLANS_DIGEST, "recipe": RECIPE,
           "folds": STAGE_FOLDS_PLANNED, "run_dir": RUN_DIR, "checks": checks, "env": ENV, "gpu": GPU, "utc": datetime.datetime.utcnow().isoformat()}
json.dump(receipt, open(STAGE_RECEIPT + ".tmp", "w"), indent=1); os.replace(STAGE_RECEIPT + ".tmp", STAGE_RECEIPT)
log(f"stage {ARM} {'smoke' if SMOKE else 'full'}: {'PASSED' if not problems else 'FAILED: ' + '; '.join(problems)}")
if not problems or SMOKE: shutil.rmtree(LOCAL_RUN, ignore_errors=True)      # everything needed is on Drive; free the Colab disk for the next stage



## cells/19/source bytes 0:43
## Driver: smoke stages, gate, full stages


## cells/2/source bytes 0:1390
# ---------------- settings (the only cell you might edit) ----------------
DRIVE_BASE = "/content/drive/MyDrive/isles-pilot"
RUN_BASE = f"{DRIVE_BASE}/sprint13-nnunet-PRIVATE"                    # new folder for this sprint's arms
S12_RUN_BASE = f"{DRIVE_BASE}/sprint12-nnunet-r8-PRIVATE"             # read-only: Sprint 12's published A1 plans (imported) and its results (the baseline)
# Arms run in this order (cheapest and most informative first; A1_L, the most expensive, last); delete any you do not want.
# "A1_pnormct" is defined but optional: add it to test per-patient normalization of the plain CT inside nnU-Net.
ARMS_ORDER = ["A1_zscore", "A1_histeq", "A1_repeat", "A1_multiwin", "A1_L"]
PLANS_FROM = {"A1_zscore": "A1_ct_maps_cta", "A1_histeq": "A1_ct_maps_cta", "A1_multiwin": "A1_ct_maps_cta", "A1_pnormct": "A1_ct_maps_cta", "A1_repeat": "A1_ct_maps_cta"}   # Sprint 12 A1's plans; A1_L plans its own
FOLDS_TO_RUN = [0, 1, 2, 3, 4]
RUN_SMOKE_FIRST = True
PAUSE_AFTER_SMOKE = True                                              # first run: stop once after a passed smoke gate to inspect the inputs; then set False and Run all
EPOCHS_FULL = 250                                                     # used only for the time projection
PIPELINE = "/content/sprint13_pipeline.py"
try:
    from google.colab import drive; drive.mount("/content/drive")
except ImportError:
    pass


## cells/20/source bytes 0:8605
# ---------------- driver: smoke stages, gate, full stages ----------------
import os, json, runpy, datetime, collections, subprocess
import numpy as np
class StageSkip(Exception): pass
def stage_receipt(arm, smoke): return f"{RUN_BASE}/stages/{arm}{'-SMOKE' if smoke else ''}.json"
def source_handoff(arm, smoke): return f"{S12_RUN_BASE}/plans_handoff/{PLANS_FROM[arm]}{'_smoke' if smoke else ''}_nnUNetResEncUNetMPlans.json"   # only ResEnc M arms import plans
def run_stage(arm, smoke):
    print(f"\n{'=' * 24} {arm}: {'SMOKE' if smoke else 'FULL'} {'=' * 24}", flush=True)
    try: runpy.run_path(PIPELINE, init_globals={"STAGE_ARM": arm, "STAGE_SMOKE": smoke, "STAGE_FOLDS": FOLDS_TO_RUN, "STAGE_DRIVE_BASE": DRIVE_BASE, "STAGE_RUN_BASE": RUN_BASE,
                                                "STAGE_S12_RUN_BASE": S12_RUN_BASE, "STAGE_PLANS_FROM": PLANS_FROM, "StageSkip": StageSkip}, run_name="__main__")
    except StageSkip: pass
    except RuntimeError as e:
        if "input check failed before training" in str(e) and smoke: print(f"  {e}")          # reported by the gate together with the other smoke stages
        else: raise
    return json.load(open(stage_receipt(arm, smoke)))
# ---- before anything expensive: Sprint 12 A1 (the baseline) must be complete, and its published plans must be the ones its results came from ----
S12_HANDOFF = lambda smoke: f"{S12_RUN_BASE}/plans_handoff/A1_ct_maps_cta{'_smoke' if smoke else ''}_nnUNetResEncUNetMPlans.json"
missing = [S12_HANDOFF(s) for s in ((True, False) if RUN_SMOKE_FIRST else (False,)) if not os.path.exists(S12_HANDOFF(s))]
assert not missing, f"Sprint 12 A1's published plans are missing, e.g. {missing[:2]}; check S12_RUN_BASE (nothing was started)"
try: _base = json.load(open(f"{S12_RUN_BASE}/stages/A1_ct_maps_cta.json")); base_ok = bool(_base.get("passed")) and set(FOLDS_TO_RUN) <= set(_base.get("folds", []))
except Exception: _base, base_ok = {}, False
assert base_ok, "Sprint 12 A1's full stage receipt is missing or incomplete, so no arm could be compared with the baseline; check S12_RUN_BASE (nothing was started)"
_H = json.load(open(S12_HANDOFF(False)))
assert _H.get("fingerprint") == _base.get("fingerprint") and _H.get("plans_digest") == _base.get("plans_digest"), "Sprint 12 A1's published plans do not belong to its reported run (fingerprint or plans digest differ); nothing was started"
print(f"Sprint 12 A1 baseline: full results passed for folds {_base['folds']}; its published plans belong to that run (plans digest {_base['plans_digest']})")
if "A1_L" in ARMS_ORDER:                                                       # the L preset needs a large GPU: stop now rather than hours in
    try: _gpu = max(float(x) for x in subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20).stdout.split()) / 1024
    except Exception: _gpu = None
    assert _gpu is None or _gpu >= 32, f"A1_L needs an A100 (40 or 80 GB); this runtime has {_gpu:.0f} GB. Change the runtime type or remove A1_L from ARMS_ORDER (nothing was started)"
def gate(recs):
    print("\n" + "=" * 24 + " SMOKE GATE " + "=" * 24)
    ok = True
    for arm, r in recs.items():
        c = r["checks"]
        if "recovery_test" not in c:
            print(f"{arm}: FAILED before training"); [print(f"    problem: {p}") for p in r["problems"]]; ok = False; continue
        print(f"{arm}: {'PASSED' if r['passed'] else 'FAILED'} | recovery {c['recovery_test']} | plans imported {bool(c['plans_imported']) if c['plans_imported'] is not None else 'n/a (own plans)'} | training statistics {c['training_stats_all_folds']}, losses finite {c['losses_finite']} | "
              f"median epoch {c['median_epoch_s']} s | infarct in brain min {c['lesion_in_brain_min']:.0%}")
        print(f"    for inspection (not rules): peak GPU {c['peak_gpu_gb']} of {c['gpu_total_gb']} GB ({c['memory_note']}); clipping of the windowed values " + "; ".join(f"{k} low {v['median_clip_low']:.0%} / high {v['median_clip_high']:.0%}, {v['patients_over_98pct_clipped']} patients >98%" for k, v in c["clipping_report"].items()))
        for p in r["problems"]: print(f"    problem: {p}")
        ok &= r["passed"]
    for arm in recs:                                                            # imported plans must be exactly the source's published smoke plans
        if arm in PLANS_FROM and recs[arm].get("passed"):
            imp = recs[arm]["checks"].get("plans_imported") or {}; src_ = PLANS_FROM[arm]
            if src_ in recs: ref_digest, ref_fp = recs[src_].get("plans_digest"), recs[src_].get("fingerprint")
            else: H = json.load(open(source_handoff(arm, True))); ref_digest, ref_fp = H.get("plans_digest"), H.get("fingerprint")
            same = imp.get("plans_digest") == ref_digest and imp.get("source_fingerprint") == ref_fp
            print(f"{arm} imported exactly {src_}'s smoke plans: {same}"); ok &= same
    for arm, r in recs.items():                                                 # post-window transform and per-patient normalization records, to inspect before the full runs
        for fname, what in (("prep_stats.json", "post-window transform"), ("pnorm_stats.json", "per-patient normalization")):
            p = f"{r.get('run_dir', '')}/qc/{fname}"
            if not (r.get("run_dir") and os.path.exists(p)): continue
            S = json.load(open(p)); print(f"{arm}: {what} records on the smoke patients (full records in {p})")
            for k in sorted({k for v in S.values() for k in (v or {})}):
                rows = [v[k] for v in S.values() if v and k in v]; fb = collections.Counter(str(x.get("fallback", x.get("level"))) for x in rows)
                print(f"    {k}: {dict(fb)}")
    envs = {a: r.get("env") for a, r in recs.items() if r.get("env")}               # software and GPU against Sprint 12 A1's full run (for inspection, not a rule)
    if envs:
        e0 = next(iter(envs.values())); diff = {k: (_base.get("env", {}).get(k), v) for k, v in e0.items() if k in _base.get("env", {}) and _base["env"][k] != v}
        g0 = next((r.get("gpu") for r in recs.values() if r.get("gpu")), None)
        print("software against Sprint 12 A1's full run: " + ("identical for " + ", ".join(k for k in e0 if k in _base.get("env", {})) if not diff else "DIFFERENT " + "; ".join(f"{k} {a} -> {b}" for k, (a, b) in diff.items()))
              + f" | GPU {_base.get('gpu')} -> {g0}" + ("" if not diff else " (a software difference is part of every comparison with the baseline; A1_repeat measures it once)"))
    proj = {a: EPOCHS_FULL * r["checks"]["median_epoch_s"] * len(FOLDS_TO_RUN) / 3600 for a, r in recs.items() if r["checks"].get("median_epoch_s")}
    if proj: print("projected training time for the full runs: " + ", ".join(f"{a} about {h:.0f} h" for a, h in proj.items()) + f"; total about {sum(proj.values()):.0f} h plus roughly 1 h of preparation per arm")
    json.dump({"passed": ok, "arms": {a: r["passed"] for a, r in recs.items()}, "projection_h": proj, "utc": datetime.datetime.utcnow().isoformat()}, open(f"{RUN_BASE}/stages/smoke_gate.json", "w"), indent=1)
    if not ok: raise RuntimeError("smoke gate failed: send the output above to Claude; nothing expensive was started")
    print("smoke gate passed")
os.makedirs(f"{RUN_BASE}/stages", exist_ok=True)
assert all(ARMS_ORDER.index(src_) < ARMS_ORDER.index(a) for a, src_ in PLANS_FROM.items() if a in ARMS_ORDER and src_ in ARMS_ORDER), "an arm that imports plans must run after its source"
if RUN_SMOKE_FIRST:
    smoke = {}
    for arm in ARMS_ORDER:
        src_ = PLANS_FROM.get(arm)
        if src_ in ARMS_ORDER and not smoke.get(src_, {}).get("passed", True):
            smoke[arm] = {"arm": arm, "passed": False, "problems": [f"not run: {src_}'s smoke stage failed, so there are no plans to import"], "checks": {}}; print(f"\n{arm}: SMOKE not run ({src_}'s smoke stage failed)"); continue
        smoke[arm] = run_stage(arm, True)
    gate(smoke)
    if PAUSE_AFTER_SMOKE:
        raise SystemExit("Planned pause after a passed smoke gate (not a failure). Check the gate block above (clipping of the new windows, the transform records) and qc/overlay_*.png in each arm's -SMOKE folder; "
                         "send them to Claude if anything looks off. Then set PAUSE_AFTER_SMOKE = False and Run all: the smoke stages are skipped and the full runs start.")
for arm in ARMS_ORDER:
    r = run_stage(arm, False)
    assert r["passed"], f"{arm} full stage did not pass: {r['problems']}; send the output to Claude"
print("\nall stages complete")


## cells/21/source bytes 0:68
## Combined results (Sprint 13 arms against the Sprint 12 baseline)


## cells/22/source bytes 0:11196
# ---------------- combined results: Sprint 13 arms against the Sprint 12 baseline (self-contained: can be run on its own after the settings cell) ----------------
import os, json, glob, hashlib
import numpy as np, pandas as pd
P8 = json.load(open(f"{DRIVE_BASE}/sprint8-seeds-features-PRIVATE/run-875c56c278/partitions.json")); SHUFFLE = 101
HELD = {int(k.split("_")[1]): v["held"] for k, v in P8.items() if int(k.split("_")[0]) == SHUFFLE}
N_ALL = len({c for k in FOLDS_TO_RUN for c in HELD[k]})                # every development patient in the planned folds (99)
LABEL = {"A1_ct_maps_cta": "S12 A1: windows, ResEnc M (baseline)", "A1_pnorm_v2": "S12 A1_pnorm_v2: per-patient normalization of the 4 maps",
         "A1_zscore": "A1_zscore: windows + z-score", "A1_histeq": "A1_histeq: windows + histogram equalization", "A1_multiwin": "A1_multiwin: two windows per scan (12 channels)",
         "A1_pnormct": "A1_pnormct: per-patient normalization of the 4 maps and the plain CT", "A1_repeat": "A1_repeat: the baseline retrained", "A1_L": "A1_L: windows, ResEnc L"}
TREE, UNET = "reference tree (Sprint 8, seed 1)", "image-only U-Net (Sprint 9, seed 1)"
def arm_table(base, arm):
    # validated fold tables for a full stage: its receipt's identity, one row per expected held-out patient, every planned fold
    try: r = json.load(open(f"{base}/stages/{arm}.json"))
    except Exception: return None, None
    if not r.get("passed"): return None, r
    rows = []
    for k in r["folds"]:
        try:
            d = pd.read_csv(f"{r['run_dir']}/folds/{r['recipe']}_s{SHUFFLE}_f{k}.csv", dtype={"fingerprint": str, "plans_digest": str, "case": str, "recipe": str})
            ok = (sorted(d.case) == sorted(HELD[k]) and not d.case.duplicated().any() and (d.fingerprint.astype(str) == r["fingerprint"]).all() and (d.plans_digest.astype(str) == str(r["plans_digest"])).all()
                  and (d.recipe == r["recipe"]).all() and np.isfinite(d[["dice", "lesion_f1", "abs_vol_err_ml"]].values.astype(float)).all() and os.path.exists(f"{r['run_dir']}/model_bundle/fold_{k}/fold_receipt.json"))
        except Exception: ok = False
        if ok: rows.append(d)
    return (pd.concat(rows) if rows else None), r
def other(glob_, recipe):
    fs = sorted(glob.glob(glob_)); o = pd.concat([pd.read_csv(f, dtype={"fingerprint": str, "case": str, "recipe": str}) for f in fs]) if fs else pd.DataFrame()
    if not len(o): return None
    o = o[(o.recipe == recipe) & (o.shuffle == SHUFFLE) & (o.train_seed == 1)]
    if o.duplicated(["fold", "case"]).any() or ("fingerprint" in o and o.fingerprint.nunique() > 1): print(f"  {recipe}: duplicate rows or rows from more than one run; left out"); return None
    return o
def _seed(*a): return int(hashlib.sha256("|".join(map(str, a)).encode()).hexdigest()[:8], 16)
def boot(v, stat, *key, level=95.0, n=2000):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    if v.size == 0: return float("nan"), float("nan"), float("nan")
    idx = np.random.default_rng(_seed(*key)).integers(0, v.size, size=(n, v.size)); b = stat(v[idx], axis=1); t = (100 - level) / 2
    return float(stat(v)), float(np.percentile(b, t)), float(np.percentile(b, 100 - t))
fmt = lambda t, d=3: f"{t[0]:+.{d}f} ({t[1]:+.{d}f} to {t[2]:+.{d}f})" if np.isfinite(t[0]) else "n/a"
fmt0 = lambda t, d=3: f"{t[0]:.{d}f} ({t[1]:.{d}f} to {t[2]:.{d}f})" if np.isfinite(t[0]) else "n/a"
# ---- tables: Sprint 12 baseline arms (read-only), this sprint's arms, the tree and the U-Net ----
TAB, REC, missing = {}, {}, {}
for base, arm in [(S12_RUN_BASE, "A1_ct_maps_cta"), (S12_RUN_BASE, "A1_pnorm_v2")] + [(RUN_BASE, a) for a in ARMS_ORDER]:
    d, r = arm_table(base, arm); REC[arm] = r
    done = sorted(d.fold.unique().tolist()) if d is not None else []
    missing[arm] = [k for k in FOLDS_TO_RUN if k not in done]
    if d is not None: TAB[arm] = d
TAB[TREE] = other(f"{DRIVE_BASE}/sprint8-seeds-features-PRIVATE/run-875c56c278/folds/part1_s{SHUFFLE}_f*_t1.csv", "D_noslice_smoothed")
TAB[UNET] = other(f"{DRIVE_BASE}/sprint9-unet-PRIVATE/run-0a60362503/folds/unet_U_base_s{SHUFFLE}_f*_t1.csv", "U_base_smoothed")
TAB = {k: v for k, v in TAB.items() if v is not None and len(v)}
name = lambda a: LABEL.get(a, a)
# ---- each model on its own ----
rows = []
for a, d in TAB.items():
    per = d.groupby("case").agg(dice=("dice", "mean"), lf1=("lesion_f1", "mean"), vol=("abs_vol_err_ml", "mean"), prec=("precision", "mean"), rec=("recall", "mean"))
    rows.append({"model": name(a), "patients": len(per), "Dice (95% CI)": fmt0(boot(per.dice, np.mean, a, "d")), "Lesion F1 (95% CI)": fmt0(boot(per.lf1, np.mean, a, "l")),
                 "Abs. volume error, ml, median (95% CI)": fmt0(boot(per.vol, np.median, a, "v"), 1), "precision (mean)": round(float(per.prec.mean()), 3), "recall (mean)": round(float(per.rec.mean()), 3)})
BY = pd.DataFrame(rows)
print("Each model on its own (shuffle 101, the same 99 patients and 5 folds; one training run per nnU-Net arm; seed 1 for the tree and the U-Net; precision is averaged over patients where it is defined):")
print(BY.to_string(index=False))
# ---- matched comparisons ----
BASE = "A1_ct_maps_cta"
PRIMARY = ["A1_zscore", "A1_histeq", "A1_multiwin", "A1_L"]          # designated before any results: each minus the Sprint 12 baseline, on Dice; the family stays 4 even if an arm is not run
BONF = 100 - 5.0 / len(PRIMARY)                                      # 98.75% intervals for the primaries (Bonferroni over the 4), from 10,000 resamples
def pair(a, b):
    m = TAB[a].merge(TAB[b], on=["shuffle", "fold", "case"], suffixes=("_a", "_b"), validate="one_to_one")
    return m.assign(d=m.dice_a - m.dice_b, l=m.lesion_f1_a - m.lesion_f1_b, v=m.abs_vol_err_ml_a - m.abs_vol_err_ml_b, p=m.precision_a - m.precision_b, r=m.recall_a - m.recall_b).groupby("case").agg(
        d=("d", "mean"), l=("l", "mean"), v=("v", "mean"), p=("p", "mean"), r=("r", "mean"))
PAIRS = [(a, BASE, "PRIMARY") for a in PRIMARY]
PAIRS += [("A1_repeat", BASE, "RETRAINING NOISE"), ("A1_pnormct", "A1_pnorm_v2", "SECONDARY")]
PAIRS += [(a, b, "exploratory") for a in ["A1_zscore", "A1_histeq", "A1_multiwin", "A1_pnormct", "A1_L"] for b in ("A1_repeat", TREE, UNET)]
PAIRS += [("A1_pnormct", BASE, "exploratory")]
crow = []
for a, b, role in PAIRS:
    if a not in TAB or b not in TAB: continue
    g = pair(a, b)
    if not len(g): continue
    dci = boot(g.d, np.mean, a, b, "d"); row = {"comparison": f"{name(a)}  minus  {name(b)}", "role": role, "patients": len(g), "Dice, 95%": fmt(dci)}
    if role == "PRIMARY":
        # verdict (designated before results): the 98.75% interval against Sprint 12 A1 excludes 0; "holds against the retrained baseline" adds the same test against A1_repeat, same direction
        bci = boot(g.d, np.mean, a, b, "d", level=BONF, n=10000); row[f"Dice, {BONF:g}% (Bonferroni)"] = fmt(bci); sig = int(np.sign(bci[1])) if (bci[1] > 0 or bci[2] < 0) else 0
        if len(g) < N_ALL: row["verdict"] = f"provisional: {len(g)} of {N_ALL} patients"
        else: row["verdict"] = {1: "better", -1: "worse", 0: "no clear difference"}[sig]
        if "A1_repeat" in TAB and len(g) == N_ALL:
            g2 = pair(a, "A1_repeat"); rci = boot(g2.d, np.mean, a, "A1_repeat", "d", level=BONF, n=10000); sig2 = int(np.sign(rci[1])) if (rci[1] > 0 or rci[2] < 0) else 0
            row["vs A1_repeat, 98.75%"] = fmt(rci); row["holds against the retrained baseline"] = bool(sig != 0 and sig2 == sig) if len(g2) == N_ALL else "provisional"
    row.update({"better / worse / tied": f"{int((g.d > 0).sum())} / {int((g.d < 0).sum())} / {int((g.d == 0).sum())}", "lesion F1, 95%": fmt(boot(g.l, np.mean, a, b, "l")),
                "precision (mean change)": fmt(boot(g.p, np.nanmean, a, b, "p")), "recall (mean change)": fmt(boot(g.r, np.mean, a, b, "r")),
                "abs. volume error, median change, ml": fmt(boot(g.v, np.median, a, b, "v"), 1)})
    crow.append(row)
CT = pd.DataFrame(crow)
if len(CT):
    order = {"PRIMARY": 0, "RETRAINING NOISE": 1, "SECONDARY": 2, "exploratory": 3}; CT = CT.sort_values("role", key=lambda s: s.map(order), kind="stable")
    print(f"\nMatched differences (same patients and folds; first minus second; intervals from patient resampling, which do not capture training variability).")
    print(f"Primary, designated before results: each of {', '.join(PRIMARY)} minus the Sprint 12 baseline, on Dice, with {BONF:g}% intervals. Secondary: A1_pnormct minus A1_pnorm_v2 (only if A1_pnormct was run). All others exploratory.")
    pd.set_option("display.max_colwidth", 90); print(CT.fillna("").to_string(index=False))
    CT.to_csv(f"{RUN_BASE}/combined_paired_contrasts.csv", index=False)
BY.to_csv(f"{RUN_BASE}/combined_by_model.csv", index=False)
# ---- the retraining yardstick ----
if "A1_repeat" in TAB and BASE in TAB:
    m = TAB["A1_repeat"].merge(TAB[BASE], on=["shuffle", "fold", "case"], suffixes=("_a", "_b"), validate="one_to_one")
    g = (m.dice_a - m.dice_b).groupby(m.case).mean(); y = abs(g.mean())
    print(f"\nRetraining yardstick: training the identical baseline again changed mean Dice by {g.mean():+.3f} (one draw of retraining noise; individual patients moved by a median of {g.abs().median():.3f}).")
    for a in PRIMARY:
        if a in TAB:
            dd = pair(a, BASE).d.mean(); print(f"    {name(a)}: mean Dice change {dd:+.3f} against Sprint 12 A1, {abs(dd) / y if y > 0 else float('inf'):.1f} times the retraining change")
    print("    A primary counts as an improvement only if its verdict is 'better' and it holds against the retrained baseline (column above); a change no larger than the retraining change is reported as not distinguishable from retraining.")
else:
    print("\nRetraining yardstick: A1_repeat has no validated results, so the primary differences cannot be compared with retraining noise. Their intervals capture patient sampling only.")
# ---- software and GPU of each full run against Sprint 12 A1's (for inspection) ----
b_env, b_gpu = (REC.get(BASE) or {}).get("env", {}), (REC.get(BASE) or {}).get("gpu")
for a in ARMS_ORDER:
    r = REC.get(a)
    if not r or not r.get("env"): continue
    diff = {k: (b_env.get(k), v) for k, v in r["env"].items() if k in b_env and b_env[k] != v}
    print(f"{a}: software {'identical to' if not diff else 'DIFFERENT from'} Sprint 12 A1's" + ("" if not diff else " (" + "; ".join(f"{k} {x} -> {y}" for k, (x, y) in diff.items()) + ")") + f"; GPU {r.get('gpu')} (baseline {b_gpu})")
# ---- status ----
if any(missing.get(a) for a in ARMS_ORDER + [BASE]): print("\nPROVISIONAL: validated results missing for " + "; ".join(f"{a} folds {m}" for a, m in missing.items() if m and (a in ARMS_ORDER or a == BASE)) + " (Run all again to recover or rescore)")
else: print("\nAll arms, and the Sprint 12 baseline, have validated results for every planned fold.")
if missing.get("A1_pnorm_v2") and "A1_pnormct" in ARMS_ORDER: print("Note: Sprint 12's A1_pnorm_v2 has no validated results, so the secondary comparison is missing.")
print(f"\nSaved {RUN_BASE}/combined_by_model.csv and combined_paired_contrasts.csv (aggregate only, no patient rows). Development results on the 99; the reserved 25 were not read.")


## cells/3/source bytes 0:132
### Pipeline file: setup  
*This cell only writes code to `/content/sprint13_pipeline.py`; the driver below runs it once per stage.*

## cells/4/source bytes 0:2090
%%writefile /content/sprint13_pipeline.py
# ---------------- CONFIG ----------------
ARM = STAGE_ARM                             # set by the driver for each stage
FOLDS_TO_RUN = list(STAGE_FOLDS)            # set by the driver
SMOKE = bool(STAGE_SMOKE)                   # set by the driver: smoke stage (12 patients, 5 epochs) or full stage
SMOKE_RECOVERY_TEST = True                  # smoke only: after fold 0 trains, simulate a lost VM and prove validation-only recovery
ALLOW_ENV_CHANGE_ON_RESUME = False          # a fold resumed under different torch/nnU-Net versions stops unless this is set deliberately
CODE_VERSION = "sprint13-nnunet-r1"
DRIVE_BASE = STAGE_DRIVE_BASE
MIRROR = f"{DRIVE_BASE}/source-extract-v1"                                             # read-only source scans (Sprint 6)
CACHE_DIR = f"{DRIVE_BASE}/feature-cache-2mm-v2"                                       # read-only: each patient's 2 mm grid and true infarct, for scoring
SPRINT8_RUN_DIR = f"{DRIVE_BASE}/sprint8-seeds-features-PRIVATE/run-875c56c278"        # read-only: case list, partitions, reference-tree results
SPRINT9_RUN_DIR = f"{DRIVE_BASE}/sprint9-unet-PRIVATE/run-0a60362503"                  # read-only: image-only U-Net results (for comparison only)
RUN_BASE = STAGE_RUN_BASE
S12_RUN_BASE = STAGE_S12_RUN_BASE                                                     # read-only: Sprint 12 A1's published plans (imported) and its results (the baseline)
HANDOFF_SRC = {"A1_ct_maps_cta": f"{S12_RUN_BASE}/plans_handoff"}                     # where an imported arm's plans were published
BASELINE_HANDOFF = f"{S12_RUN_BASE}/plans_handoff/A1_ct_maps_cta{'_smoke' if SMOKE else ''}_nnUNetResEncUNetMPlans.json"   # Sprint 12 A1: every arm must match its patients, folds, windows and source files
LOCAL = "/content/work-sprint13"                                                       # nnU-Net raw, preprocessed and results folders live on the Colab disk
SHUFFLE = 101
FEATURE_CFG = {"target_mm": 2.0, "vessel_pct": 98.0, "core_thr": 0.30, "penumbra_tmax": 6.0, "schema": "isles24-features-2mm-v2"}


## cells/4/source bytes 2120:13513
NN = {"version": "2.8.1", "planner": "nnUNetPlannerResEncM", "plans": "nnUNetResEncUNetMPlans", "configuration": "3d_fullres",
      "base_trainer": "nnUNetTrainer_250epochs", "trainer": "nnUNetTrainer_250epochs_ckpt10", "save_every": 10,
      "smoke_base_trainer": "nnUNetTrainer_5epochs", "smoke_trainer": "nnUNetTrainer_5epochs_ckpt1", "smoke_save_every": 1,
      "sync_s": 300, "np_max": 6, "n_proc_da_max": 10, "ram_gb_per_worker": 8}
WINDOWS = {"ncct": [0, 80], "cbf": [0, 35], "cbv": [0, 10], "mtt": [0, 20], "tmax": [0, 7], "cta": [0, 90],   # Sprint 6/12 windows (the winners' for CTA and the four maps; 0-80 HU brain window for the plain CT)
           # second windows, multi-window arm only; fixed here before any results: narrower for NCCT, CBV and MTT, wider for CBF, Tmax and CTA (rationale in the notebook's introduction)
           "ncct_w2": [20, 50], "cbf_w2": [0, 100], "cbv_w2": [0, 4], "mtt_w2": [0, 12], "tmax_w2": [0, 20], "cta_w2": [0, 300]}
CH_SRC = {f"{k}_w2": k for k in ("ncct", "cbf", "cbv", "mtt", "tmax", "cta")}          # channel name -> source scan (default: the channel name itself)
def src_kind(ch): return CH_SRC.get(ch, ch)
BASE6 = ["ncct", "cbf", "cbv", "mtt", "tmax", "cta"]
PREP_KINDS = ("window", "window_zscore", "window_histeq")
HISTEQ_BINS = 256
ZSCORE_MIN_SD = 0.01                                                                 # z-score: SD floor (1% of the window width), so a nearly constant channel cannot blow up
PERF_KINDS = ("cbf", "cbv", "mtt", "tmax")                                           # z-score and histogram statistics for these use only brain voxels the perfusion scan covers
MRI_CLIP_Z = 5.0                                                                       # MRI: z-score within the brain, clipped to +-5, rescaled to [0, 1]
ARMS = {
    # every arm uses Sprint 12 A1's six channels and folds; only the preparation (or, for A1_L, the nnU-Net configuration) changes
    "A1_zscore":   {"id": 731, "channels": BASE6, "recipe": "N13_cta_window_zscore", "plans_from": "A1_ct_maps_cta", "prep": "window_zscore"},
    "A1_histeq":   {"id": 732, "channels": BASE6, "recipe": "N13_cta_window_histeq", "plans_from": "A1_ct_maps_cta", "prep": "window_histeq"},
    "A1_multiwin": {"id": 733, "channels": BASE6 + [f"{k}_w2" for k in BASE6], "recipe": "N13_cta_multiwindow", "plans_from": "A1_ct_maps_cta", "prep": "window"},
    "A1_pnormct":  {"id": 734, "channels": BASE6, "recipe": "N13_cta_pnorm_ct", "plans_from": "A1_ct_maps_cta", "prep": "window", "pnorm": ["ncct", "cbf", "cbv", "mtt", "tmax"]},
    "A1_repeat":   {"id": 735, "channels": BASE6, "recipe": "N13_cta_repeat", "plans_from": "A1_ct_maps_cta", "prep": "window"},
    "A1_L":        {"id": 736, "channels": BASE6, "recipe": "N13_cta_resencL", "plans_from": None, "prep": "window", "planner": "nnUNetPlannerResEncL", "plans": "nnUNetResEncUNetLPlans", "min_gpu_gb": 32},
}
PLANS_WAIT_H = 8                                                                       # A0 waits up to this long for A1's plans to appear on Drive
BRAIN_ML_RANGE = (400, 2500)                                                           # plausible brain-mask volume (Sprint 6)
MRI_MIN_FINITE, MRI_MIN_SD = 0.95, 1e-6                                                # usable MRI inside the brain
LESION_AGREE_MIN = 0.999                                                               # source lesion on the 2 mm grid must match the cached true infarct
AFFINE_ATOL = 1e-3
MAP_SHUFFLE, MAP_SEED = 101, 1

# ---- stage checks recorded for the driver's gate ----
GATE = {"channel_sd_block": 1e-6, "clip_report": 0.98}   # blocking: a channel constant inside the brain; clipping and the true infarct's share inside the brain mask are reported only
# per-patient normalization (arm A1_pnorm): each perfusion map as a robust z-score against the patient's own reference tissue, clipped and rescaled to [0, 1]
# reference = brain tissue with Tmax <= 6 s whose perfusion values are not all zero: ADMISSION IMAGES ONLY (no stroke-side rule, no occlusion annotation)
# per channel: values must be finite (and above zero for CBF, CBV, MTT); scale = 1.4826 x MAD, else the reference SD, else that channel falls back to the fixed window
# min_scale = 2% of the window widths (CBF 0-35, CBV 0-10, MTT 0-20, Tmax 0-7, plain CT 0-80)
# no data (all four maps zero) and invalid values (CBF, CBV or MTT <= 0; Tmax < 0; non-finite) are encoded as 0, the same floor the fixed windows give them in A1,
# so A1_pnorm_v2 - A1 differs only in how valid values are scaled
PNORM_NN = {"tmax_delayed_s": 6.0, "min_ref_voxels": 20000, "clip_z": 5.0, "min_scale": {"cbf": 0.7, "cbv": 0.2, "mtt": 0.4, "tmax": 0.14, "ncct": 1.6},
            "nodata_rule": "all-zero perfusion or invalid value (CBF/CBV/MTT <= 0, Tmax < 0, non-finite) -> 0, the fixed-window floor"}

import os, sys, json, time, hashlib, glob, subprocess, datetime, re, collections, shutil, threading, warnings
try:
    from google.colab import drive; drive.mount("/content/drive"); IN_COLAB = True
except ImportError:
    IN_COLAB = False
assert ARM in ARMS, f"ARM must be one of {list(ARMS)}"
A = ARMS[ARM]; RECIPE = A["recipe"]; DID = A["id"] + (50 if SMOKE else 0); DS_NAME = f"Dataset{DID}_ISLES24_{ARM}{'_smoke' if SMOKE else ''}"
NN = dict(NN, planner=A.get("planner", NN["planner"]), plans=A.get("plans", NN["plans"]))       # per-arm configuration: A1_L plans nnU-Net's larger "L" preset
assert A.get("prep", "window") in PREP_KINDS, f"unknown preparation {A.get('prep')}"
assert not (A.get("pnorm") and A.get("prep", "window") != "window"), "per-patient normalization and a post-window transform are not combined"
assert A["plans_from"] == STAGE_PLANS_FROM.get(ARM), f"{ARM}: plans source in the settings cell ({STAGE_PLANS_FROM.get(ARM)}) differs from the arm definition ({A['plans_from']})"
TRAINER = NN["smoke_trainer"] if SMOKE else NN["trainer"]; BASE_TRAINER = NN["smoke_base_trainer"] if SMOKE else NN["base_trainer"]; SAVE_EVERY = NN["smoke_save_every"] if SMOKE else NN["save_every"]
RUN_DIR = f"{RUN_BASE}/{ARM}{'-SMOKE' if SMOKE else ''}"; EXPORT_DIR = f"{RUN_DIR}/export"; HANDOFF = f"{RUN_BASE}/plans_handoff"
for d in (RUN_DIR, EXPORT_DIR, HANDOFF, f"{RUN_DIR}/folds", f"{RUN_DIR}/masks", f"{RUN_DIR}/checkpoints", f"{RUN_DIR}/model_bundle", f"{RUN_DIR}/qc"): os.makedirs(d, exist_ok=True)
for rd in (MIRROR, CACHE_DIR, SPRINT8_RUN_DIR, SPRINT9_RUN_DIR, S12_RUN_BASE): assert not os.path.abspath(RUN_DIR).startswith(os.path.abspath(rd)), "this notebook must not write inside a read-only input folder"
T0 = time.time(); _LOG = []
def log(m):
    line = f"[+{(time.time()-T0)/60:6.1f} min] {m}"; print(line); _LOG.append(line); open(f"{RUN_DIR}/console.log", "a").write(line + "\n")
def sh(cmd, logfile=None, check=True, env=None):
    # run a command, streaming its output to a log file on Drive; raise with the tail of the log on failure
    lf = logfile or f"{RUN_DIR}/commands.log"
    with open(lf, "a") as f:
        f.write(f"\n$ {cmd if isinstance(cmd, str) else ' '.join(cmd)}\n"); f.flush()
        r = subprocess.run(cmd, shell=isinstance(cmd, str), stdout=f, stderr=subprocess.STDOUT, env=env)
    if check and r.returncode:
        tail = open(lf).read()[-3000:]; raise RuntimeError(f"command failed (exit {r.returncode}); full log: {lf}\n{tail}")
    return r.returncode
sh(f"{sys.executable} -m pip -q install 'nnunetv2=={NN['version']}' 'nibabel>=5.2,<6' 'xgboost>=2.0'")
import numpy as np, pandas as pd, nibabel as nib, xgboost as xgb
from nibabel.processing import resample_from_to
from scipy.ndimage import gaussian_filter, distance_transform_edt, binary_erosion
from sklearn.metrics import roc_auc_score, average_precision_score
import torch
GPU = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
from importlib.metadata import version as _ver
def _v(p):
    try: return _ver(p)
    except Exception: return None
ENV = {"nnunetv2": _v("nnunetv2"), "torch": getattr(torch, "__version__", None), "cuda": getattr(getattr(torch, "version", None), "cuda", None), "numpy": np.__version__, "nibabel": nib.__version__, "dynamic_network_architectures": _v("dynamic_network_architectures"), "batchgeneratorsv2": _v("batchgeneratorsv2")}
assert ENV["nnunetv2"] in (NN["version"], None) or not IN_COLAB, f"nnunetv2 {ENV['nnunetv2']} installed, {NN['version']} pinned"
try:
    import psutil; RAM_GB = psutil.virtual_memory().total / 1e9
except Exception: RAM_GB = 32.0
CPUS = os.cpu_count() or 2
NP = max(1, min(NN["np_max"], CPUS, int(RAM_GB // NN["ram_gb_per_worker"]))); NPROC_DA = max(1, min(NN["n_proc_da_max"], CPUS))
try: GPU_TOTAL_GB = max(float(x) for x in subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20).stdout.split()) / 1024
except Exception: GPU_TOTAL_GB = None
if A.get("min_gpu_gb") and IN_COLAB:
    assert GPU_TOTAL_GB is not None and GPU_TOTAL_GB >= A["min_gpu_gb"], f"{ARM} plans nnU-Net's 'L' configuration, which targets about 24 GB of GPU memory; this runtime has {GPU_TOTAL_GB} GB. Switch to an A100 (40 or 80 GB) or remove {ARM} from ARMS_ORDER."
try: DISK_FREE_GB = shutil.disk_usage("/content" if os.path.exists("/content") else "/").free / 1e9
except Exception: DISK_FREE_GB = None
FEATURE_HASH = hashlib.sha256(json.dumps(FEATURE_CFG, sort_keys=True).encode()).hexdigest()[:12]
CASES = json.load(open(f"{SPRINT8_RUN_DIR}/run_manifest.json"))["config"]["cases"]; assert len(CASES) == 99 and not set(CASES) & set(EXCLUDED)
P8 = json.load(open(f"{SPRINT8_RUN_DIR}/partitions.json")); INNER = {tuple(int(x) for x in k.split("_")): v for k, v in P8.items()}
N_FOLDS = sum(1 for (s_, k_) in INNER if s_ == SHUFFLE); assert N_FOLDS >= 2, f"no partitions for shuffle {SHUFFLE}"
log(f"arm {ARM} ({RECIPE}) | dataset {DS_NAME} | trainer {TRAINER} | GPU {GPU} | RAM {RAM_GB:.0f} GB, {CPUS} CPUs -> {NP} preprocessing and {NPROC_DA} augmentation workers | {'SMOKE' if SMOKE else 'full run'} | env {ENV}")
# ---- trainer variant: the pinned base trainer, checkpointing every SAVE_EVERY epochs (Sprint 6 method: explicit base signature) ----
def write_trainer_variant(name, base_name, save_every):
    import importlib, inspect
    mod = importlib.import_module("nnunetv2.training.nnUNetTrainer.variants.training_length.nnUNetTrainer_Xepochs"); base = getattr(mod, base_name)
    params = list(inspect.signature(base.__init__).parameters); assert params == ["self", "plans", "configuration", "fold", "dataset_json", "device"], f"unexpected base trainer signature {params}"
    src = ("import torch\nfrom nnunetv2.training.nnUNetTrainer.variants.training_length.nnUNetTrainer_Xepochs import " + base_name + "\n"
           "class " + name + "(" + base_name + "):\n    def __init__(self, plans: dict, configuration: str, fold: int, dataset_json: dict, device: torch.device = torch.device('cuda')):\n"
           "        super().__init__(plans, configuration, fold, dataset_json, device)\n        self.save_every = " + str(int(save_every)) + "\n")
    path = f"{os.path.dirname(mod.__file__)}/{name}.py"; open(path, "w").write(src); importlib.invalidate_caches()
    cls = getattr(importlib.import_module(f"nnunetv2.training.nnUNetTrainer.variants.training_length.{name}"), name); assert list(inspect.signature(cls.__init__).parameters) == params
write_trainer_variant(TRAINER, BASE_TRAINER, SAVE_EVERY)



## cells/5/source bytes 0:168
### Pipeline file: sprint 8 utilities and scoring (verbatim)  
*This cell only writes code to `/content/sprint13_pipeline.py`; the driver below runs it once per stage.*

## cells/6/source bytes 0:36488
%%writefile -a /content/sprint13_pipeline.py
# ===================== Shared utilities v2 (plain numpy/scipy/nibabel; every function has a purpose line) =====================
# Repairs vs v1 (Astra review 2026-09-09): complete lesion truth is cached separately from the feature mask;
# caches are bound to a schema version + configuration hash and validated on load; float32 storage (no float16
# overflow); finite-value checks; unique temporary filenames.
import os, json, glob, time, traceback, uuid, hashlib
import numpy as np
import nibabel as nib
from nibabel.processing import resample_from_to, resample_to_output
from scipy.ndimage import (gaussian_filter, uniform_filter, distance_transform_edt,
                           label as cc_label, binary_fill_holes)

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
import numpy as np, pandas as pd
import xgboost as xgb
from scipy.ndimage import distance_transform_edt, binary_erosion

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
FIXTURES = _fx(); log(f"lesion-wise metric fixtures (F1, count difference): {FIXTURES}")
assert FIXTURES["both_empty"] == (1.0, 0) and FIXTURES["truth_only"][0] == 0.0 and FIXTURES["diagonal_contact_one_piece"] == (1.0, 0) and FIXTURES["truth_one_pred_two_split"][1] == 1 and abs(FIXTURES["one_matched_one_fp"][0] - 0.6667) < 1e-3 and FIXTURES["iou_0.2_boundary"][0] == 1.0


## cells/7/source bytes 0:151
### Pipeline file: library and run identity  
*This cell only writes code to `/content/sprint13_pipeline.py`; the driver below runs it once per stage.*

## cells/8/source bytes 0:18421
%%writefile -a /content/sprint13_pipeline.py
# ---------------- source files, channel preparation, dataset writing ----------------
PAT = {"ncct": "train/raw_data/{c}/ses-01/{c}_ses-01_ncct.nii.gz",
       "cbf": "train/derivatives/{c}/ses-01/perfusion-maps/{c}_ses-01_space-ncct_cbf.nii.gz", "cbv": "train/derivatives/{c}/ses-01/perfusion-maps/{c}_ses-01_space-ncct_cbv.nii.gz",
       "mtt": "train/derivatives/{c}/ses-01/perfusion-maps/{c}_ses-01_space-ncct_mtt.nii.gz", "tmax": "train/derivatives/{c}/ses-01/perfusion-maps/{c}_ses-01_space-ncct_tmax.nii.gz",
       "cta": "train/derivatives/{c}/ses-01/{c}_ses-01_space-ncct_cta.nii.gz",
       "dwi": "train/derivatives/{c}/ses-02/{c}_ses-02_space-ncct_dwi.nii.gz", "adc": "train/derivatives/{c}/ses-02/{c}_ses-02_space-ncct_adc.nii.gz",
       "lesion": "train/derivatives/{c}/ses-02/{c}_ses-02_space-ncct_lesion-msk.nii.gz", "brain": "brainmask/{c}_brainmask.nii.gz"}
def src(c, kind): return f"{MIRROR}/{PAT[kind].format(c=c)}"
def zscore_in_brain(x, brain):
    # the winners' step after windowing: z-score of the windowed channel over this patient's brain-mask voxels (mean 0, SD 1 there); outside the brain 0
    v = x[brain]; m, s = (float(v.mean()), float(v.std())) if v.size else (0.0, 0.0)
    if not np.isfinite(s) or s < 1e-6: return np.zeros_like(x, dtype=np.float32), {"mean": m, "sd": s, "fallback": "constant inside the brain"}
    su = max(s, ZSCORE_MIN_SD); z = ((x - m) / su).astype(np.float32)
    return z, {"mean": m, "sd": s, "sd_used": su, "fallback": None if s >= ZSCORE_MIN_SD else "SD floored", "z_min": float(z[brain].min()), "z_max": float(z[brain].max())}
def histeq_in_brain(x, brain, nbins=None):
    # histogram equalization of the windowed channel over this patient's brain-mask voxels: each value -> the share of brain voxels at or below its bin
    # (scikit-image's definition, cumulative share at the bin centre, with the bins fixed to the window range [0, 1]); outside the brain 0
    nbins = nbins or HISTEQ_BINS; v = x[brain]
    if v.size == 0 or float(v.std()) < 1e-6: return np.zeros_like(x, dtype=np.float32), {"fallback": "constant inside the brain"}
    hist, edges = np.histogram(v, bins=nbins, range=(0.0, 1.0)); cdf = np.cumsum(hist).astype(np.float64); cdf /= cdf[-1]; centres = (edges[:-1] + edges[1:]) / 2
    return np.interp(x, centres, cdf).astype(np.float32), {"fallback": None, "share_at_window_floor": float((v <= 1e-6).mean()), "share_at_window_ceiling": float((v >= 1 - 1e-6).mean())}
WSTAT = {}
def window01(v, lo, hi):
    v = np.where(np.isfinite(v), v, lo); return ((np.clip(v, lo, hi) - lo) / (hi - lo)).astype(np.float32)
def mri01(v, brain):
    # z-score within the brain (finite voxels), clipped to +-MRI_CLIP_Z, rescaled to [0, 1]; outside the brain 0
    ok = brain & np.isfinite(v); m, s = float(v[ok].mean()), float(v[ok].std()) + 1e-6
    z = np.where(np.isfinite(v), (v - m) / s, 0.0); return ((np.clip(z, -MRI_CLIP_Z, MRI_CLIP_Z) + MRI_CLIP_Z) / (2 * MRI_CLIP_Z)).astype(np.float32)
def same_grid(img, ref): return img.shape[:3] == ref.shape[:3] and np.allclose(img.affine, ref.affine, atol=AFFINE_ATOL)
def load3d(path):
    img = nib.load(path); v = np.asanyarray(img.dataobj)
    if v.ndim == 4 and v.shape[3] == 1: v = v[..., 0]
    assert v.ndim == 3, f"{path}: expected a single 3-D volume, found shape {v.shape}"
    return img, v
def pnorm_levels(c, brain):
    # reference tissue candidates, admission images only: brain with Tmax <= 6 s, then the whole brain; voxels whose four perfusion maps are all zero are never reference
    maps = {k: load3d(src(c, k))[1].astype(np.float32) for k in ("cbf", "cbv", "mtt", "tmax")}
    all_zero = np.all([np.nan_to_num(maps[k]) == 0 for k in maps], axis=0); t = maps["tmax"]
    return [("brain with Tmax <= 6 s", brain & np.isfinite(t) & (t >= 0) & (t <= PNORM_NN["tmax_delayed_s"]) & ~all_zero), ("whole brain", brain & ~all_zero)], all_zero
def pnorm_channel(v, kind, pref, brain):
    # robust z-score for one channel, with per-channel validity, a fixed low-variation fallback, and a full record; no data and invalid values -> 0
    out, rec = _pnorm_channel(v, kind, pref[0], brain)
    invalid = (pref[1] if kind in ("cbf", "cbv", "mtt", "tmax") else False) | ~np.isfinite(v) | ((v <= 0) if kind in ("cbf", "cbv", "mtt") else (v < 0))   # the plain CT keeps its values outside the perfusion coverage
    rec["nodata_share"] = float(invalid[brain].mean()) if brain.any() else None
    return np.where(invalid, 0.0, out).astype(np.float32), rec
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
PREC = {}
def prep_channel(c, ch, ref, brain, pref=None):
    kind = src_kind(ch); img, v = load3d(src(c, kind)); assert same_grid(img, ref), f"{c}: {kind} shape or affine differs from the plain CT"
    v = v.astype(np.float32); WSTAT.pop(ch, None)
    if ch in A.get("pnorm", []): out, PREC[ch] = pnorm_channel(v, ch, pref, brain)
    elif ch in WINDOWS:
        out = window01(v, *WINDOWS[ch]); wb = out[brain]; WSTAT[ch] = {"clip_low": float((wb <= 1e-6).mean()), "clip_high": float((wb >= 1 - 1e-6).mean())}   # clipping measured on the windowed values, before any transform
        if A.get("prep", "window") != "window":
            # statistics over the brain voxels this scan covers: for the perfusion maps, voxels where all four maps are zero (outside the perfusion coverage) are left out
            # and get the outside-brain value 0, so the transform does not depend on how much of the brain the perfusion scan covered
            cov = (brain & ~pref[1]) if kind in PERF_KINDS else brain
            out, PREC[ch] = (zscore_in_brain if A["prep"] == "window_zscore" else histeq_in_brain)(out, cov)
            out = np.where(cov, out, 0.0).astype(np.float32); PREC[ch]["no_coverage_share"] = float((brain & ~cov).sum() / max(int(brain.sum()), 1))
    else:
        fin = np.isfinite(v[brain]).mean(); sd = float(np.nanstd(np.where(brain, v, np.nan)))
        assert fin >= MRI_MIN_FINITE and sd > MRI_MIN_SD, f"{c}: {kind} unusable inside the brain (finite {fin:.1%}, sd {sd:.3g})"
        out = mri01(v, brain)
    return out * brain
def save_nii(arr, ref, path, dtype):
    hdr = ref.header.copy(); hdr.set_data_dtype(dtype); tmp = path.replace(".nii.gz", ".tmp.nii.gz")
    nib.save(nib.Nifti1Image(arr.astype(dtype), ref.affine, hdr), tmp); os.replace(tmp, path)
def case_receipt(c): return f"{RAW}/receipts/{c}.json"
def case_done(c):
    # a case counts as written only with a receipt bound to this run's identity and that case's source stamp
    try: r = json.load(open(case_receipt(c)))
    except Exception: return False
    files = [f"{RAW}/imagesTr/{c}_{i:04d}.nii.gz" for i in range(len(A["channels"]))] + [f"{RAW}/labelsTr/{c}.nii.gz"]
    return r.get("fingerprint") == FINGERPRINT and r.get("source") == SOURCE_STAMP[c] and all(os.path.exists(f) and os.path.getsize(f) == r["sizes"].get(os.path.basename(f)) for f in files)
def write_case(c):
    ref, _ = load3d(src(c, "ncct")); bimg, b = load3d(src(c, "brain")); assert same_grid(bimg, ref), f"{c}: brain mask shape or affine differs from the plain CT"
    brain = b > 0.5; ml = float(brain.sum() * np.prod(ref.header.get_zooms()[:3]) / 1000); assert BRAIN_ML_RANGE[0] <= ml <= BRAIN_ML_RANGE[1], f"{c}: brain mask volume {ml:.0f} ml outside {BRAIN_ML_RANGE}"
    stats = {}; PREC.clear(); pref = pnorm_levels(c, brain) if (A.get("pnorm") or A.get("prep", "window") != "window") else None   # perfusion coverage is also needed by the post-window transforms
    for i, k in enumerate(A["channels"]):
        arr = prep_channel(c, k, ref, brain, pref); save_nii(arr, ref, f"{RAW}/imagesTr/{c}_{i:04d}.nii.gz", np.float32); v = arr[brain]
        stats[k] = {**WSTAT.get(k, {"clip_low": float((v <= 1e-6).mean()), "clip_high": float((v >= 1 - 1e-6).mean())}), "sd": float(v.std())}
    limg, l = load3d(src(c, "lesion")); assert same_grid(limg, ref), f"{c}: lesion mask shape or affine differs from the plain CT"
    save_nii((l > 0.5).astype(np.uint8), ref, f"{RAW}/labelsTr/{c}.nii.gz", np.uint8)
    files = [f"{RAW}/imagesTr/{c}_{i:04d}.nii.gz" for i in range(len(A["channels"]))] + [f"{RAW}/labelsTr/{c}.nii.gz"]
    os.makedirs(f"{RAW}/receipts", exist_ok=True); json.dump({"fingerprint": FINGERPRINT, "source": SOURCE_STAMP[c], "sizes": {os.path.basename(f): os.path.getsize(f) for f in files}, "channel_stats": stats, "pnorm": dict(PREC) if A.get("pnorm") else None, "prep": dict(PREC) if A.get("prep", "window") != "window" else None}, open(case_receipt(c), "w"))
def write_dataset_json(n):
    json.dump({"channel_names": {str(i): "noNorm" for i in range(len(A["channels"]))}, "channel_descriptions": {str(i): k for i, k in enumerate(A["channels"])},
               "labels": {"background": 0, "infarct": 1}, "numTraining": n, "file_ending": ".nii.gz",
               "note": f"channels prepared outside nnU-Net ({A.get('prep', 'window')}{', per-patient normalization of ' + ', '.join(A['pnorm']) if A.get('pnorm') else ''}) and brain-masked; nnU-Net normalisation off (noNorm)"}, open(f"{RAW}/dataset.json", "w"), indent=1)
def splits():
    # one entry per fold: train = that fold's training patients, val = its held-out patients (predicted with the final weights)
    if SMOKE:
        P = INNER[(SHUFFLE, 0)]; return [{"train": sorted(P["train"][:8]), "val": sorted(P["held"][:4])}]
    return [{"train": sorted(INNER[(SHUFFLE, k)]["train"]), "val": sorted(INNER[(SHUFFLE, k)]["held"])} for k in range(N_FOLDS)]
STUDY = sorted({c for sp in splits() for part in ("train", "val") for c in sp[part]})
def _sha(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(chunk), b""): h.update(blk)
    return h.hexdigest()
def _stat(path): st = os.stat(path); return [st.st_size, int(st.st_mtime)]
KINDS = sorted(set(src_kind(ch) for ch in A["channels"])) + ["ncct", "brain", "lesion"]
missing = [(c, k) for c in STUDY for k in KINDS if not os.path.exists(src(c, k))]
assert not missing, f"missing source files, e.g. {missing[:5]}"
# source inventory: size and modification time of every consumed image, content hashes of the small masks
SOURCE_STAMP = {c: {k: ([_sha(src(c, k))] if k in ("brain", "lesion") else _stat(src(c, k))) for k in sorted(set(KINDS))} for c in STUDY}   # masks by content; large images by size and modification time
CHANNEL_STAMP = {k: hashlib.sha256(json.dumps({c: SOURCE_STAMP[c][k] for c in STUDY}, sort_keys=True).encode()).hexdigest()[:12] for k in sorted(set(KINDS))}
CACHE_IDENTITY = hashlib.sha256(json.dumps({c: _sha(f"{CACHE_DIR}/{c}.npz") for c in STUDY}, sort_keys=True).encode()).hexdigest()[:12]
IDENTITY = {"code_version": CODE_VERSION, "arm": ARM, "channels": A["channels"], "prep": A.get("prep", "window"), "channel_sources": {ch: src_kind(ch) for ch in A["channels"]}, "histeq_bins": HISTEQ_BINS if A.get("prep") == "window_histeq" else None, "zscore_min_sd": ZSCORE_MIN_SD if A.get("prep") == "window_zscore" else None, "transform_region": "brain; perfusion maps: brain covered by the perfusion scan" if A.get("prep", "window") != "window" else None, "windows": {k: WINDOWS[k] for k in A["channels"] if k in WINDOWS}, "mri_clip_z": MRI_CLIP_Z if any(k not in WINDOWS for k in A["channels"]) else None,
            "cases": STUDY, "splits": splits(), "nnunet": {k: NN[k] for k in ("version", "planner", "plans", "configuration")}, "trainer": TRAINER, "base_trainer": BASE_TRAINER, "plans_from": A["plans_from"], "smoke": SMOKE,
            "source_inventory": CHANNEL_STAMP, "scoring_cache_identity": CACHE_IDENTITY, "checks": {"brain_ml": BRAIN_ML_RANGE, "mri_min_finite": MRI_MIN_FINITE, "lesion_agree_min": LESION_AGREE_MIN, "affine_atol": AFFINE_ATOL},
            "pnorm": ({"channels": A["pnorm"], **PNORM_NN, "reference": "brain with Tmax <= 6 s and not all-zero perfusion, then whole brain; admission images only"} if A.get("pnorm") else None)}
FINGERPRINT = hashlib.sha256(json.dumps(IDENTITY, sort_keys=True).encode()).hexdigest()[:10]
# local working folders are named by the run identity, so a changed configuration never reuses old images, plans or weights
LOCAL_RUN = f"{LOCAL}/{ARM}-{FINGERPRINT}"
for d in ("raw", "preprocessed", "results"): os.makedirs(f"{LOCAL_RUN}/{d}", exist_ok=True)
NN_ENV = dict(os.environ, nnUNet_raw=f"{LOCAL_RUN}/raw", nnUNet_preprocessed=f"{LOCAL_RUN}/preprocessed", nnUNet_results=f"{LOCAL_RUN}/results", nnUNet_n_proc_DA=str(NPROC_DA))
os.environ.update({k: v for k, v in NN_ENV.items() if k.startswith("nnUNet")})
RAW = f"{LOCAL_RUN}/raw/{DS_NAME}"; PRE = f"{LOCAL_RUN}/preprocessed/{DS_NAME}"
MODEL_ROOT = f"{LOCAL_RUN}/results/{DS_NAME}/{TRAINER}__{NN['plans']}__{NN['configuration']}"
man = f"{RUN_DIR}/run_manifest.json"
if os.path.exists(man):
    old = json.load(open(man))["identity"]; now = json.loads(json.dumps(IDENTITY))          # compare in JSON form (tuples are stored as lists)
    changed = sorted(k for k in set(old) | set(now) if old.get(k) != now.get(k))
    assert not changed, f"this arm's folder holds a run with a different configuration ({changed}); move it aside or change RUN_BASE before continuing"
else: json.dump({"fingerprint": FINGERPRINT, "identity": IDENTITY, "created_utc": datetime.datetime.utcnow().isoformat(), "gpu": GPU}, open(man, "w"), indent=1)
log(f"run identity {FINGERPRINT}: {len(STUDY)} patients, {len(splits())} fold(s); {len(A['channels'])} channels, preparation {A.get('prep', 'window')}; nnU-Net {NN['plans']}; local working folder {LOCAL_RUN}; free disk {DISK_FREE_GB if DISK_FREE_GB is None else round(DISK_FREE_GB)} GB")
json.dump({"fingerprint": FINGERPRINT, "per_case_source": SOURCE_STAMP}, open(f"{RUN_DIR}/source_inventory.json", "w"))

# ---- saved-output validators (shared by training, scoring, stage skipping and the combined results) ----
def bundle_dir(k): return f"{RUN_DIR}/model_bundle/fold_{k}"
def readable_npz(p):
    try: z = np.load(p); return "probabilities" in z.files and z["probabilities"].ndim == 4
    except Exception: return False
def readable_nii(p):
    try: return np.asanyarray(nib.load(p).dataobj).size > 0
    except Exception: return False
def bundle_ok(k, plans_digest):
    try:
        b = bundle_dir(k); r = json.load(open(f"{b}/fold_receipt.json")); val = splits()[k]["val"]
        return bool(r.get("fingerprint") == FINGERPRINT and r.get("plans_digest") == plans_digest and r.get("cases") == val and os.path.getsize(f"{b}/checkpoint_final.pth") > 0
                    and all(readable_nii(f"{b}/validation/{c}.nii.gz") and readable_npz(f"{b}/validation/{c}.npz") for c in val))
    except Exception: return False
def fold_table_path(k): return f"{RUN_DIR}/folds/{RECIPE}_s{SHUFFLE}_f{k}.csv"
ID_DTYPES = {"fingerprint": str, "plans_digest": str, "case": str, "recipe": str}   # identifiers stay text: a hash like 9544e19592 must not be read as a number
def table_ok(k, plans_digest):
    try:
        df = pd.read_csv(fold_table_path(k), dtype=ID_DTYPES); val = splits()[k]["val"]
        ok = (len(df) == len(val) and sorted(df.case) == sorted(val) and not df.case.duplicated().any() and (df.fingerprint.astype(str) == FINGERPRINT).all()
              and (df.plans_digest.astype(str) == str(plans_digest)).all() and (df.fold == k).all() and np.isfinite(df[["dice", "lesion_f1", "abs_vol_err_ml", "signed_vol_err_ml"]].values.astype(float)).all())
        return df if ok else None
    except Exception: return None
STATS_PATH = f"{RUN_DIR}/qc/train_stats.json"
def stats_ok(folds):
    try: st = json.load(open(STATS_PATH)); return all(st.get(str(k), {}).get("epochs_logged", 0) > 0 and st[str(k)].get("losses_finite") for k in folds)
    except Exception: return False
def stage_outputs_ok(r):
    # a stage counts as complete only if every planned fold's model bundle, results table and training statistics are valid (and, for smoke, the recovery rehearsal passed)
    try:
        folds = r.get("folds") or []; pdg = r.get("plans_digest")
        ok = bool(folds) and all(bundle_ok(k, pdg) and table_ok(k, pdg) is not None for k in folds) and stats_ok(folds)
        if SMOKE and SMOKE_RECOVERY_TEST: ok = ok and bool(json.load(open(f"{RUN_DIR}/qc/recovery_test.json")).get("passed"))
        return ok
    except Exception: return False
# ---- a stage already completed under this exact identity, with valid saved outputs, is skipped (the driver catches StageSkip) ----
STAGE_FOLDS_PLANNED = [0] if SMOKE else sorted(FOLDS_TO_RUN)
STAGE_RECEIPT = f"{RUN_BASE}/stages/{ARM}{'-SMOKE' if SMOKE else ''}.json"; os.makedirs(os.path.dirname(STAGE_RECEIPT), exist_ok=True)
try: _r = json.load(open(STAGE_RECEIPT))
except Exception: _r = {}
if _r.get("passed") and _r.get("fingerprint") == FINGERPRINT and _r.get("folds") == STAGE_FOLDS_PLANNED:
    if stage_outputs_ok(_r):
        log(f"stage {ARM} {'smoke' if SMOKE else 'full'} already complete under this identity, saved outputs verified ({STAGE_RECEIPT}); skipping")
        raise StageSkip(STAGE_RECEIPT)
    log(f"stage {ARM} {'smoke' if SMOKE else 'full'}: a receipt exists but some saved outputs are missing or invalid; recovering through the normal path")



## cells/9/source bytes 0:164
### Pipeline file: 0. checks before building or training  
*This cell only writes code to `/content/sprint13_pipeline.py`; the driver below runs it once per stage.*