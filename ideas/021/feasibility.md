# Feasibility memo — Idea 021: The healthy hemisphere is the ruler

Date: 2026-08-18. Stage: feasibility, authorized by the 2026-08-17 operator
ruling. All web facts below were verified 2026-08-18 against the cited primary
source unless marked otherwise. Verification classes used: **verified fact**
(fetched source, quoted), **source-supported interpretation**, **inference**,
**unverified**.

## 0. What this memo must establish

The revised card poses one conditional question: under normalization frozen
from each unedited case, does a frozen ISLES'24 final-infarct model use
contralateral perfusion as a signed patient-specific reference. The operator
ruling of 2026-08-17 answered the mechanism-identifiability inspection (no
non-reference mechanism survives the revised gates, given the normalization
pin) and forwarded three conditions to this memo: verify the target model's
**normalization implementation**, that it **consumes finished maps** rather
than re-deriving from 4D source, and its **receptive-field span**. The stage
task additionally mandates a prior-art subsection on map-editing and
counterfactual-perturbation mechanisms with a concrete stay-in-distribution
strategy with numbers; absence of workable precedent is a legitimate kill.

## 1. Closest work and exact gap

**Closest works, all verified from primary sources:**

- **Öman et al. 2019** (Eur Radiol Exp, PMC6374492): 3D CNN for stroke
  detection on CTA; adding a flipped-and-registered "cerebral hemispheric
  comparison" input channel raised specificity from 0.40 to 0.81. Verbatim:
  "Utilizing information from the contralateral hemisphere appears to be
  beneficial for reducing false positive findings." This is *train-time
  input-channel ablation with retraining* — it shows contralateral information
  helps, not whether a plain trained model uses it.
- **Raina, Yahorau, Schmah, arXiv:1907.08196** ("Exploiting bilateral symmetry
  in brain lesion segmentation"): supplying a patch around the homologous
  contralateral voxel as extra features improved Dice by "13 percentage points
  over baseline for one architecture and 9 points for the other."
  **Correction to the record:** the critique (2026-08-17) attributed this
  arXiv ID to Clèrigues; the actual Clèrigues et al. work is Comput Biol Med
  2019 (DOI 10.1016/j.compbiomed.2019.103487), whose abstract confirms
  "symmetric modality augmentation" among its contributions (ISLES 2018 CTP
  core segmentation, Dice 49%).
- **Rau ... Kellner, AJNR 2024;45(3):277** (PMC11286109): clinical mirror
  normalization built in by construction — "voxelwise division of the original
  image ... by the mirrored one," mirrored image Gaussian-smoothed (σ =
  12×12×4 mm) and clipped at 150%. This is the field's strongest statement
  that the contralateral reference is *engineered in*, not discovered.
- **Ni et al., MICCAI 2022, arXiv:2206.15445** (Asymmetry Disentanglement
  Network): interpretability-by-design separation of pathological vs
  anatomical interhemispheric asymmetry for NCCT infarct segmentation.
- **Campbell et al. 2011** (Stroke, PMID 21980202, DOI
  10.1161/STROKEAHA.111.618355), the clinical anchor, abstract verified
  verbatim: "The optimal threshold was <31% of mean contralateral CBF";
  relative CBF AUC 0.79 (95% CI 0.77–0.81) vs absolute CBV 0.74 (0.73–0.76).

**Exact gap.** A targeted search (two independent agents, nine named query
families, 2026-08-18; queries recorded in section 12) found **no published
post-hoc intervention audit of a fixed trained stroke model's contralateral
reference use** — no study edits the healthy hemisphere of a held-fixed input
to test whether a trained model uses it as a reference. Everything adjacent
either engineers symmetry in at design time (Öman, Raina, Clèrigues, Rau,
DeepSymNet, ADN) or is clinical neuroscience of the contralesional
hemisphere. The gap the card claims is real as far as bounded search can
establish; per collaborator rules, "I did not find it" is not proof of
absence. The novelty statement in the card ("no novelty claim is made;
absence was not exhaustively established") remains the correct posture.

## 2. Dataset access and license

All verified 2026-08-18 directly from https://zenodo.org/records/16813698:

- **License: CC BY-NC-SA 4.0** ("Creative Commons Attribution Non Commercial
  Share Alike 4.0 International"). Noncommercial, share-alike. No DUA,
  registration, or click-through is stated on the record; the download is
  open. (The card and prior ledger said "public noncommercial" — now pinned
  to the exact license.) Source-supported interpretation, not legal advice:
  research use, model training, and publication are consistent with BY-NC-SA;
  ShareAlike plausibly obligates same-license release of derived artifacts
  (edited maps, possibly weights); flag to the operator before any artifact
  release.
- **149 released training cases**, verbatim: "This multi-center dataset
  consists of 149 acute ischemic stroke cases." The challenge *design* was
  150 train (100 Munich + 50 Zurich) + ~100 hidden test (challenge report
  arXiv:2408.10966, verbatim: "The train (test) set contains N = 100 (N = 50)
  scans from the University Hospital of Munich and N = 50 (N = 50) scans from
  the University Hospital of Zurich"; results reported on 98 hidden cases).
  The 149-vs-150 one-case discrepancy is unexplained in any fetched source
  (unverified why); the preprint abstract (arXiv:2408.11142) says 245 total
  vs the 250 implied by the split — also unreconciled. Neither discrepancy is
  load-bearing: the released cohort is what it is, and Stage 0 counts it.
- **Files:** `train.7z` (99.0 GB) + `clinical_data-description.xlsx`. The
  archive contains both `raw_data/` (including raw 4D CTP,
  `..._ctp.nii.gz`) and NCCT-space derivatives, verbatim: "'Derivatives'
  include all modalities linearly co-registered to the NCCT space" — CBF,
  CBV, MTT, Tmax maps, follow-up-MRI-derived infarct masks
  (`lesion-msk.nii.gz`), LVO masks. Perfusion maps were produced by
  "FDA-approved clinical software icobrain cva" (challenge report; version
  number unverified — the external brief's "1.5.0" was not found in fetched
  text).
- **The hidden test set is not public** (verbatim: "the test subset is hidden
  from the public"). All splits must come from the 149 released cases.

**No DUA-gated dependency exists.** The charter constraint is satisfied.

## 3. Label availability and concept validity

The primary readout is **label-free in the annotation sense**: paired
within-case deltas of the model's own predicted lesion volumes under edits.
The released follow-up infarct mask is used for (a) training the stand-in
model and (b) cohort construction (defining the affected side). Both uses
survive annotation-provenance scrutiny: the mask is derived from follow-up
DWI/ADC imaging registered to NCCT space, not from a reader's checklist, and
the intervention readout never compares to it as ground truth. X (mean
contralateral CBF/CBV after automatic midline estimation) is computable today
from released files with no human annotator — the charter's hard constraint
on X holds.

## 4. Sample structure and likely split unit

One case = one patient = one acute session (the "longitudinal" element is
follow-up MRI within each case, not repeat sessions). **Split unit: patient.**
Two sites (Munich, Zurich) with different scanner fleets; site should be a
stratification variable in the split and a robustness check, though the
within-case paired design means site cannot confound the causal contrast —
only transportability. Plausible structure given 149 cases: ~100–119
development (model training + MDE estimation, cross-validated), ~30–49 frozen
held-out for confirmatory edited-arm scoring, exact numbers fixed by the
power memo before any confirmatory score is seen. After bilateral-disease and
midline-QC exclusions the confirmatory count will shrink; the power gate
decides whether what remains suffices.

## 5. Existing code and checkpoints — including a correction to the record

- **Official repo** (github.com/ezequieldlrosa/isles24): evaluation utilities
  and a demo notebook only — metrics code for Dice, absolute volume
  difference, lesion count difference, lesion-wise F1. No training code, no
  baseline recipe, no checkpoint. (Re-confirms the keystone screen.)
- **Correction:** the 2026-08-17 critique stated the winner "released neither
  code nor checkpoint" (search that day found none). A repository
  **github.com/KurtLabUW/ISLES2024** exists containing the winning team's
  Docker submission — `preprocessing.py`, `inference.py`, nnU-Net code — and
  a Google Drive link to trained model weights ("Download the model weights
  from the 'model weights.txt' file"). Authors of the winning paper
  (arXiv:2505.18424 — Ren, Heras Rivera, Oswal, Pan, Henry, Walters, Kurt;
  Kurt Lab, not "Riepe et al." as the external brief wrote) overlap with the
  repo owners. **Verified:** repo and weight link exist. **Inferred, not
  stated in the repo:** that these weights are the exact winning entry.
  **Unverified:** weight-file availability/integrity (Drive links rot),
  license of the weights, and their pipeline internals.
- **Winner recipe (verified from arXiv:2505.18424):** "large" 3D residual
  encoder nnU-Net (ResEnc L), patch size [56, 320, 256], Dice+CE loss, SGD
  lr 0.01; preprocessing = SynthStrip skull stripping + custom intensity
  windowing (exact numeric windows shown only in a figure — unverified as
  numbers); their cross-validation Dice: standard preprocessing 21.8%, custom
  windowing 31.0%, final 31.8%.
- **nnU-Net itself** is public, installable, and self-configuring; training
  resume via `--c` is code-verified.

**Design implication, flagged for the operator (no card change made here):**
the card specifies a self-trained model, chosen when no winner checkpoint was
believed to exist. A released winner checkpoint would let the study audit
*the actual winning system* — the normalization pin works at inference-time
preprocessing regardless of how the model was trained, since the constants
are computed from the unedited case at edit time. That would upgrade
relevance (characterizing the real challenge winner, not a stand-in) at zero
training cost. It is an option, not a requirement: it depends on unverified
facts (weights downloadable, pipeline inspectable, license permitting) and on
an operator decision, since the card's stand-in framing was debated and
frozen. Recommended handling: Stage 0 adds a bounded inspection of the
KurtLab repo/weights; if it passes, the operator chooses between self-trained
primary + winner replication arm, or winner-primary. The self-trained path
remains fully viable if the Drive link is dead.

## 6. The three operator-forwarded verifications

### 6a. Normalization implementation — VERIFIED at code level

From `nnunetv2/preprocessing/normalization/default_normalization_schemes.py`
and `documentation/explanation_normalization.md` (fetched 2026-08-18):

- `ZScoreNormalization.run` computes `mean = image.mean(); std = image.std()`
  on the image passed in — **per-image statistics, no dataset constants**.
  Docs: "zscore: Performs z-scoring separately for each training case." This
  confirms the critique's fatal-objection mechanism in the actual code.
- `CTNormalization` uses dataset-level fingerprint statistics
  (`intensityproperties['mean']`, `['std']`, percentile clip bounds) — fixed
  constants, edit-independent.
- Scheme selection is **per channel** via `channel_names` in `dataset.json`
  (`map_channel_name_to_normalization.py`), and the preprocessor loops
  channels independently (`DefaultPreprocessor._normalize`).
- **`NoNormalization` exists** (keyword `noNorm`, case-insensitive): `return
  image.astype(self.target_dtype, copy=False)` — a no-op.
- Caveat found in code: with `use_mask_for_norm`, z-score stats are computed
  only where `seg >= 0` (the nonzero-crop mask); either way the stats are a
  function of the edited tensor unless pinned.

**The normalization pin is therefore implementable by construction:** declare
every perfusion channel `noNorm` and apply the frozen normalization
externally — constants computed once from the unedited case (or frozen cohort
constants) and reused verbatim for every edited variant. NCCT/CTA channels
under the `CT` scheme are already edit-independent (dataset-level constants),
and they are never edited. The bit-identity gate (affected-side network-input
voxels identical after contralateral-only editing) becomes checkable by
diffing preprocessed arrays, with **no trained model and no GPU required** —
`nnUNetv2_plan_and_preprocess` output suffices.

Two inference-time facts that must go into the probe contract:

- **Test-time mirroring is ON by default** (`use_mirroring: bool = True`;
  CLI `--disable_tta`). Mirroring TTA averages predictions over
  left-right-flipped inputs. It does not break edit/readout disjointness (the
  full inference function is still deterministic in the pinned input), but it
  entangles the two hemispheres' *output* pathways in a way that complicates
  mechanism attribution. Pin: **disable TTA** in all confirmatory inference.
- Sliding-window inference is algorithmically deterministic (fixed step size,
  deterministic Gaussian weights, no RNG in the file) — verified; *bitwise*
  GPU run-to-run reproducibility is unverified and must be handled as in
  probe 004: an anchor-repeat gate with a frozen tolerance rather than an
  assumption.

### 6b. Finished maps, not re-derived from 4D source — VERIFIED as a design pin with precedent

The release contains both raw 4D CTP and finished NCCT-space maps. The
proposed model consumes **finished derivative maps only** — that is a design
pin under our control, so the external brief's AIF/VOF-contamination pathway
(healthy-side edits perturbing automatic arterial-input-function selection)
is excluded *by construction*, not by assumption. Precedent that this is the
performant configuration, verbatim from the challenge report: "All three
top-performing methods are based on nnU-Net. The first- and second-ranked
teams implemented similar approaches, utilizing nearly all image-data
modalities except for the 4D perfusion (CTP) sequence." If the winner
checkpoint option is taken, its `preprocessing.py` must be inspected at Stage
0 to confirm the same fact for their exact pipeline (unverified today).

### 6c. Receptive-field span — VERIFIED for the winner recipe; Stage-0 recorded for a self-trained plan

The winner's ResEnc L patch size is [56, 320, 256] (verified quote). At the
~1 mm-class in-plane NCCT-space resolution, a 320×256 in-plane patch covers
essentially the whole head cross-section — both hemispheres sit inside one
patch, so cross-hemisphere information flow to any output voxel is
architecturally available (source-supported interpretation; exact voxel
spacings must be read from the NIfTI headers at Stage 0). For a self-trained
model the planner chooses the patch from the dataset fingerprint, so the
Stage-0 gate must record the planned patch size and verify it spans the
midline for affected-side voxels; **if it does not, the question is not
well-posed for that configuration** (an output voxel cannot see the other
hemisphere at all) and the plan must be overridden to a midline-spanning
patch before training. This is a new, concrete Stage-0 check this memo adds.

## 7. Prior art: map-editing and intervention mechanisms (mandatory subsection)

### 7a. Named precedents for comparable manipulations

**Direct-perturbation interpretability (the mechanism family this study
uses):** Zeiler & Fergus, arXiv:1311.2901 — "systematically occluding
different portions of the input image with a grey square, and monitoring the
output of the classifier"; Fong & Vedaldi, arXiv:1704.03296 (ICCV 2017) —
optimized "explicit and interpretable image perturbations"; 3D medical
occlusion sensitivity on brain MRI (Chattopadhyay et al., PMC11429733 — 7³
voxel occlusion cubes swept through the volume). Established, citable, and
methodologically identical in kind (edit input region, read output change);
they differ in using destructive occlusion rather than in-distribution
scaling.

**Counterfactual/generative editing of medical images to probe models:**
Sanchez et al., arXiv:2207.12268 (DGM4MICCAI 2022) — healthy-counterfactual
diffusion ("How would a patient appear if X pathology was not present?");
Cohen et al., arXiv:2102.09475 (Gifsplanation/Latent Shift) — latent-space
edits that "exaggerate or curtail the features used for prediction"; Singla
et al., arXiv:1911.00483 (ICLR 2020) — progressive counterfactual
exaggeration. These establish the probe-a-model-by-editing-its-input
paradigm in medical imaging, with realism handled generatively.

**Perfusion-specific value manipulation:** no published study perturbs
*derived* CBF/CBV maps to probe a trained model (named searches in section
12). What exists at the source level: digital CTP phantoms with known truth —
Kudo et al., Radiology 2013 (PMID 23220899; CBF 2.5–87.5 mL/100g/min, CBV
1.0–5.0 mL/100g embedded and recovered across 13 CT algorithms); Uwano et
al., Neuroradiology 2012 (PMID 21739219); Divel et al., Med Phys 2021
(PMC8475013, first-principles CTP simulator). And a *clinical* manipulation
of maps in production use: the Rau/Kellner AJNR 2024 mirror-division
pipeline (voxelwise division by a smoothed, 150%-clipped mirrored map) —
evidence that arithmetic manipulation of finished perfusion maps is an
accepted, publishable operation in this exact modality.

**Assessment:** precedent for the *mechanism class* (edit input, read frozen
model) is abundant and named; precedent for the *specific object* (scaling
finished perfusion maps) exists only as clinical map arithmetic, not as a
model probe. That is the novelty, not a feasibility hole — but it means
**no external effect-size calibration exists**, which is why the power gate
cannot be waived (the external brief flagged the same).

### 7b. Concrete stay-in-distribution strategy, with numbers

The realism target is the model's *training input distribution* (149 cases
including diseased hemispheres), not healthy physiology. Published magnitudes
that bound what "plausible map values" means:

- **Measurement/processing variability of absolute CTP values is large.**
  Fiorella et al., AJNR 2004 (PMID 14729537), same source data re-processed:
  coefficients of variation "31%, 30%, and 14% for CBV, CBF, and MTT."
  Waaijer et al., AJNR 2007 (PMID 17494672): intra/interobserver variability
  "for absolute CTP values ... CBV (16%–17% ...) and CBF (18% ...)" vs 10–16%
  for ratios. A ±20% multiplicative change in one hemisphere's absolute
  CBF/CBV is inside the documented reprocessing spread of the measurement
  itself.
- **Systematic scale bias of CTP is even larger.** Grüner et al., EJNMMI Res
  2011 (PMC3251173): gray-matter CBF 71.8 ± 8.0 by perfusion CT vs 48.7 ± 5.0
  mL/min/100g by ¹⁵O-H₂O PET in the same healthy subjects — a ~1.5×
  modality-level calibration slack. Kudo et al., Radiology 2010 (PMID
  20032153): CBF/MTT values and abnormal areas "significantly varied among
  software" on identical source data (numeric spread is in the paywalled full
  text — unverified numbers; qualitative finding verified).
- **Physiological range markers.** Normal interhemispheric asymmetry is small
  — Catafau et al. 1996 (PMID 8781137, SPECT, healthy volunteers): "−1.01% to
  3.14%" — so a 10–20% asymmetry is *not* normal-healthy; it lives in the
  pathology tail (unilateral vascular disease), which the ISLES'24 cohort
  itself contains. Hematocrit variation alone produces CBF "between 140 and
  90%" of baseline (Muizelaar et al. 1992, PMID 1566914 — animal data,
  flagged as such).
- **Internal consistency comes free from the central volume principle.**
  MTT = CBV/CBF; scaling CBF and CBV jointly by the same factor s leaves
  their ratio — and hence consistency with the *unedited* MTT map — exactly
  preserved (inference from a standard identity). Tmax and CTA are untouched.
  The main cross-channel residual is CBF/CBV-vs-Tmax joint plausibility,
  which is gated empirically below.

**Proposed envelope (numbers provisional until frozen at Stage 0):**
confirmatory doses s ∈ {0.80, 0.90, 1.10, 1.20}, exploratory boundary probes
{0.70, 1.30}. Gates per retained dose: (i) post-edit contralateral
hemisphere-mean CBF and CBV must lie within the empirical [2.5th, 97.5th]
percentile band of unaffected-hemisphere means across the released cohort;
(ii) voxelwise: the fraction of edited-hemisphere voxels beyond the cohort's
per-map 99.5th percentile must not exceed the unedited cohort's own rate;
(iii) a held-out real-vs-edited discriminator at or below a frozen AUC
threshold; (iv) joint CBF–Tmax and CBV–Tmax 2D-histogram distance to the
cohort within the cohort's own leave-one-out spread; (v) the frozen
contralateral predicted-lesion emergence threshold. The down-scaling arm has
a natural cover distribution (contralateral hypoperfusion exists in the
cohort); the **up-scaling arm is the fragile one** — a hemisphere at 120% with
normal Tmax has thinner cohort support, and this is exactly the card's
declared kill path if no dose passes.

## 8. Compute estimate

- **Download/storage:** 99 GB archive. Only derivatives (+ NCCT/CTA) are
  needed; the raw 4D CTP dominates archive size. Selective 7z extraction
  should keep working storage well under the full unpacked size (inference;
  exact numbers are a Stage-0 measurement). Within Colab Pro+/Drive
  practice established by probe 004, but the 99 GB single-file download is
  itself a session-management task.
- **Training (self-trained path):** nnU-Net docs (resenc_presets.md,
  verified): ResEnc M "~12h on A100" (9–11 GB VRAM), ResEnc L "~35h on A100"
  (24 GB), default 1000 epochs, resumable with `--c`. ResEnc M or default
  3d_fullres over ~2–3 Colab sessions is realistic; ResEnc L (winner-scale)
  is feasible but triples the budget. One trained model is shared
  development infrastructure.
- **Winner-checkpoint path:** zero training; inference only.
- **Edits + inference:** ~40 confirmatory cases × (3 arms × ~4 doses + shams
  ≈ 15 variants) ≈ 600 single-case inferences; at minutes each (TTA
  disabled), roughly 10–30 GPU-hours, spread across sessions. Discriminator
  and QC tooling are additional small CPU/GPU jobs. Total study on the order
  of 50–90 GPU-hours — inside the charter's compute constraint, not a
  one-week sketch (the card already says so).

## 9. Accepted baselines and metrics

Verified from arXiv:2408.10966: the challenge metrics are Dice, absolute
volume difference, lesion-wise F1 (20% IoU matching), absolute lesion count
difference, rank-aggregated per case. Winner test performance Dice 0.285 ±
0.213, AVD 21.2 ± 37.2 mL (98 hidden cases); second and third teams Dice
0.263/0.255. These calibrate the *stand-in adequacy check* (our model should
sit in the published performance family on a held-out development fold) and
give context that per-case outputs are highly variable — reinforcing the MDE
gate. The intervention endpoints (paired volume deltas, signed slopes,
mirror-over-global margin) are custom by necessity; no external number plays
a pass/fail role (consistent with the program's amended pin-2 philosophy).

## 10. Critical leakage and confounds

- **Preprocessing coupling** (the critique's fatal objection): closed by
  construction via `noNorm` + external pinned normalization + bit-identity
  gate (section 6a). This is the load-bearing repair and it is code-verified.
- **Train-time mirroring augmentation:** nnU-Net default augmentation
  includes axis mirroring; per the external brief this is a *substrate of
  genuine reference use* (and an interpretation caveat: the symmetry prior
  may be augmentation-taught), not a validity confound. Report it; optionally
  train a no-mirror variant as exploratory.
- **Inference TTA mirroring:** disable (section 6a).
- **Emergent contralateral lesion / laterality competition:** frozen
  emergence threshold, per card; the down-scaling arm is where it bites.
- **Chronic contralateral disease corrupting the mirror:** released masks
  cover the acute lesion only; exclusions must come from automatic QC
  (contralateral CSF/encephalomalacia burden, mirror-residual magnitude) plus
  the clinical metadata sheet; definition frozen at Stage 0.
- **Site/scanner/protocol/habitus/prevalence/referral/report leakage:** fixed
  within-case by the paired design for the causal contrast; transportability
  across them is explicitly not claimed (card already states this).
- **Test-set integrity:** the hidden challenge test set is unavailable, so
  the study's held-out set is a frozen split of the 149; the development/
  confirmatory firewall (freeze before any confirmatory score) is the
  protection, per collaborator rules.

## 11. Smallest probe of the riskiest assumption

**Riskiest assumption:** an adequately powered up-scaling dose exists that
passes all realism gates (the card's keystone conjunction).

**Smallest probe — zero-GPU, no model, no training:**
1. Download the archive; selectively extract derivatives for all cases.
2. Inspect NIfTI headers (grids, spacings, orientation, L-R convention);
   estimate midlines; compute per-hemisphere CBF/CBV/Tmax summaries.
3. Build the empirical envelope of section 7b and compute, for each candidate
   dose s, the fraction of cases whose edited hemisphere stays inside the
   cohort band — that fraction × 149 is the maximum available confirmatory
   sample per dose, which feeds the MDE memo directly.
4. Run `nnUNetv2_plan_and_preprocess` with the pinned channel schemes; diff
   affected-side preprocessed arrays for an edited/unedited pair —
   bit-identity gate tested before any training exists. Record the planned
   patch size (midline-span check, section 6c).
5. Bounded KurtLab inspection: does the Drive link resolve; hash the weights;
   read `preprocessing.py` for normalization/windowing internals.

This probe converts every remaining unverified load-bearing fact into an
inspected one (or a kill) for roughly a day of CPU work plus a large
download, before any GPU training is authorized.

## 12. Negative-search documentation

Novelty/prior-art negative claims rest on these recorded queries (two
independent agents, 2026-08-18), each returning only design-time symmetry
engineering or clinical neuroscience: "contralateral hemisphere ablation deep
learning stroke lesion segmentation"; "interhemispheric asymmetry CNN stroke
segmentation interpretability"; "occlusion contralateral stroke model";
"symmetry-aware stroke segmentation interpretability attribution trained
model audit"; "hemisphere swap / replacing the contralateral / modifying the
contralateral input deep learning stroke"; "unaffected hemisphere
perturbation counterfactual segmentation perfusion stroke"; "perfusion map
perturbation deep learning"; "simulated perfusion deficit"; "lesion insertion
perfusion"; "CT perfusion digital phantom".

## 13. Corrections to the evidence record (for the ledger)

1. The ISLES'24 winner's team **has** released inference code and trained
   weights (github.com/KurtLabUW/ISLES2024 + Google Drive), contrary to the
   2026-08-17 critique's finding; entry-identity is inferred from author
   overlap, weights integrity unverified.
2. The winner paper arXiv:2505.18424 is by **Ren et al. (Kurt Lab)**, not
   "Riepe et al." as the external brief states.
3. arXiv:1907.08196 is **Raina, Yahorau, Schmah**, not Clèrigues; the +9–13
   Dice figure belongs to it. Clèrigues et al. is DOI
   10.1016/j.compbiomed.2019.103487.
4. Dataset license pinned: **CC BY-NC-SA 4.0**; 149 released cases; no DUA.

## 14. Verdict

**GO**, conditional on the Stage-0 probe of section 11 executing before any
probe contract, with these pins carried forward:

- Perfusion channels declared `noNorm`; frozen external normalization from
  the unedited case; bit-identity gate on affected-side preprocessed arrays.
- Finished derivative maps only as model input; raw 4D CTP never enters.
- Planned patch size recorded and midline-span verified (new gate).
- Inference TTA disabled; anchor-repeat determinism gate as in probe 004.
- Envelope, discriminator threshold, emergence threshold, margins, and MDE
  all frozen before any confirmatory edited-case score is seen; if no
  up-scaling dose passes with adequate power, the study stops and reports
  the fallback per the card's successor-governance clause.
- The KurtLab winner-checkpoint option goes to the operator as a design
  choice after its bounded Stage-0 inspection; it does not alter this
  verdict, which stands on the self-trained path alone.

## In plain terms

This study can be done. The data is free to download (99 GB, noncommercial
license, no application process), the software is standard and public, and
the one technical trap that previously threatened the whole design — the
model's preprocessing quietly transmitting the edit to the untouched side of
the brain — has a clean, code-verified fix: the pipeline has an official
switch to turn its internal normalization off, so we can normalize with
constants frozen from the unedited scan and prove the untouched hemisphere's
inputs are byte-for-byte identical. The cost is roughly one large download,
one to two days of GPU training (or none, if the newly discovered winning
team's released model checks out), and some tens of GPU-hours of scoring —
weeks of calendar work, not months. The single biggest practical risk is the
"turn the healthy hemisphere up" experiment at the heart of the question:
brightened perfusion maps may not look enough like real patients to pass the
prespecified realism checks in enough cases, and if that arm dies the study
can only report the weaker finding it has promised to hand back to the
operator rather than claim. A cheap one-day, no-GPU probe of the actual data
decides that risk before any training is spent.
