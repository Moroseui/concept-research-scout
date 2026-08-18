# Feasibility memo — idea 023 (isles24-scout-002-c07)

**Question under feasibility review:** Does a specified map-input final-infarct
model use the joint CBV/MTT compensation state at matched CBF deficit when that
state has a precise outcome relationship in the training cohort?

**Authorized claim scope (binding, per decisions.md 2026-08-17):** the claim
language is fixed as an *outcome-associated joint CBV/MTT decision boundary*.
The phrase "autoregulatory blood-volume reserve" is prohibited; physiological
naming requires a successor with challenge-based validation. This memo assesses
feasibility of the reduced claim only.

**Mandated condition discharged in §3:** prior art on map-editing and
counterfactual-perturbation mechanisms, plus a concrete stay-in-distribution
edit strategy with numbers. Per the operator ruling, absence of workable
precedent would be a legitimate kill; §3 concludes precedent is sufficient.

Verification statuses used below: **VERIFIED** (primary source fetched and read
this stage, or inspected in a prior recorded stage), **SOURCE-SUPPORTED**
(quoted in the operator-commissioned external review brief of 2026-08-17, not
independently re-fetched), **UNVERIFIED** (stated by no inspected source; must
be resolved at Stage 0), **INFERENCE** (my reasoning from verified facts).

---

## 1. Closest work and exact gap

**Closest work, verified this stage:**

- Robben et al. 2020, *Medical Image Analysis* (PMID 31683091;
  arXiv:1812.02496): predicts final infarct volume from **native CTP** plus
  treatment metadata and analyzes the effect of varying treatment parameters
  (time, recanalization) — counterfactuals on *metadata*, not on map values.
  VERIFIED (PubMed record and arXiv abstract this stage; also verified during
  critique).
- Amador et al. 2024, *J Biomed Inform* (S1532046423002885): cross-attention
  model on 4D CTP + clinical metadata; explicitly "allows generating attention
  maps and counterfactual outcome scenarios to investigate the relevance of
  **clinical variables**." Again metadata counterfactuals. VERIFIED (publisher
  page this stage).
- Amador et al. 2022, *Medical Image Analysis* (S1361841522002389):
  treatment-specific lesion outcome prediction from 4D CTP — the
  treatment-arm-swap counterfactual in the same task family. VERIFIED
  (publisher listing this stage; abstract only).
- ISLES'24 challenge report (arXiv:2408.10966): the benchmark itself — 150
  train / 98 hidden test, top Dice 0.285, rCBF<30% clinical baseline Dice
  0.163, ground truth from follow-up DWI. VERIFIED this stage.

**Exact gap (unchanged from the debated card, now re-checked):** no located
work perturbs the *values of the released perfusion maps themselves* along the
native joint CBV/MTT conditional distribution at fixed CBF and Tmax, within
case, to test whether a final-infarct model responds to the compensation
state. Published counterfactuals in this task family perturb clinical/treatment
variables or ablate whole channels. This remains a targeted gap statement, not
a proof of novelty ("I did not find it" is not proof).

## 2. Dataset access, license, versioning

- **Access:** public Zenodo, no DUA, registration-free API access confirmed.
  VERIFIED this stage via the Zenodo REST API.
- **License:** CC BY-NC-SA 4.0 on both inspected versions. VERIFIED.
  Non-commercial research use is compliant with program constraints.
- **Version churn is real and must be pinned.** The version inspected at
  keystone screen (record 16731717 — the concept/parent DOI) now resolves
  through at least: record 16813698 ("version 2", train.7z ≈ 92.2 GB **plus a
  separately downloadable `clinical_data-description.xlsx`, ≈ 12 MB**) and a
  latest version, record **17652035 ("version 6", published 2025-11-20,
  train.7z = 99.0 GB as the only listed file)**. VERIFIED this stage (API).
  Consequences: (a) Stage 0 must pin one record id and its file MD5s before
  anything else; (b) the clinical-data description file is listed on v2 but
  was not returned in the v6 file listing — which record carries it must be
  established at pin time; (c) the critique's instruction to pin hashes is
  retroactively vindicated.
- **Monolithic archive confirmed:** the training data is a single `train.7z`
  (92–99 GB depending on version). **Derivative-only retrieval is not
  offered.** VERIFIED. Mitigation (INFERENCE, standard 7z behavior): 7z
  supports selective extraction by path, so the ~99 GB download is
  unavoidable but the uncompressed footprint can be limited to
  `derivatives/` (maps, registered NCCT, lesion masks) plus `phenotype/`,
  discarding the raw 4D CTP series, which dominates the archive. Uncompressed
  selective footprint is UNVERIFIED; estimate < 20 GB.
- **Case-count discrepancy, must resolve at Stage 0:** Zenodo descriptions say
  **149** training cases; the challenge paper says **150** (100 Munich, 50
  Zurich). VERIFIED that the discrepancy exists; its cause is UNVERIFIED
  (plausibly a withdrawn case). Non-blocking; affects only bookkeeping.

## 3. Prior art on map-editing and counterfactual perturbation (mandated section)

### 3a. Direct input-value perturbation in medical imaging models

- **Occlusion/perturbation sensitivity** is a standard, widely published probe
  family in medical imaging (Zeiler & Fergus occlusion, arXiv:1311.2901; Fong
  & Vedaldi meaningful perturbation, arXiv:1704.03296; both applied repeatedly
  to medical segmentation and classification). These methods *zero or blur*
  input regions — interventions far **more** out-of-distribution than the
  bounded value edits proposed here. SOURCE-SUPPORTED / method anchors
  VERIFIED as papers; their medical uptake is common ground in the critique
  and external brief.
- **Robben et al. and Amador et al.** (§1) establish the counterfactual-probing
  precedent *on this exact task* (CTP-based final-infarct prediction), though
  on metadata rather than map values. VERIFIED.

### 3b. Generative/causal counterfactual image editing

- Pawlowski, Castro & Glocker, *Deep Structural Causal Models for Tractable
  Counterfactual Inference*, NeurIPS 2020 (arXiv:2006.06485; code
  biomedia-mira/deepscm): do-interventions producing counterfactual **brain
  MRI** images. VERIFIED this stage.
- Sanchez & Tsaftaris, *Diffusion Causal Models for Counterfactual
  Estimation*, CLeaR 2022 (arXiv:2202.10166; code vios-s/Diff-SCM):
  diffusion-based counterfactual estimation demonstrated on imaging data.
  VERIFIED this stage.
- These show the field accepts model-probing via synthesized/edited medical
  images when validity is argued; our design is *more* conservative than
  generative synthesis because it edits released map values directly under
  empirical-support bounds rather than sampling from a learned generator.
  INFERENCE.

### 3c. Perfusion-map manipulation as an accepted measurement operation

- Kellner et al., AJNR 2024;45(3):277, "Reducing False-Positives in CT
  Perfusion Infarct Core Segmentation Using Contralateral Local
  Normalization": clinical-methods work that **arithmetically manipulates
  perfusion maps** (voxelwise division by a mirrored, clipped, smoothed copy)
  as a legitimate operation on clinical maps. SOURCE-SUPPORTED (quoted in the
  2026-08-17 external brief).
- The DEFUSE-3/DAWN rCBF<30%-of-contralateral core definition means
  ratio-transformed map values are the *clinical standard*, so mirror-ratio
  arithmetic on these maps is squarely inside accepted practice.
  SOURCE-SUPPORTED.

### 3d. What has no precedent

No located published work performs a **consistency-preserving joint edit along
a physiological identity** (CBV and MTT co-scaled at fixed CBF = CBV/MTT) on
clinical perfusion maps to probe a trained model. The nearest neighbors are
§3a–3c. This is the novelty delta *and* the residual risk: no external
calibration of expected effect sizes or of edit-realism failure modes exists.
The claim "no precedent" is a search result, not a proof.

### 3e. Concrete stay-in-distribution strategy (numbers are Stage-0 defaults, to be frozen before outcome inspection)

1. **Edit region:** deficit tissue defined as Tmax > 6 s (the DEFUSE-family
   penumbra threshold), eroded by 1 voxel; exclude voxels within 2 voxels of
   the estimated midline and vascular voxels (CBV above a frozen vessel cap,
   default 8 mL/100 g, to be checked against released map units at census).
2. **Strata:** mirror-normalized CBF (rCBF_mirror) bins [0.15, 0.30),
   [0.30, 0.45), [0.45, 0.60) — bracketing the clinically load-bearing
   rCBF ≈ 0.30 landmark.
3. **Edit operator:** multiply CBV and MTT voxelwise by the same factor
   f ∈ {0.70, 0.85, 1.15, 1.30} (CBF and Tmax untouched; CBF = CBV/MTT
   preserved by construction where the identity holds), plus f = 1.00
   zero-dose repeat.
4. **Support bounds:** post-edit rCBV_mirror must remain within the stratum's
   native [q05, q95] estimated from census-split patients only; voxels that
   would exceed bounds are clamped; any case-stratum cell with > 10% clamped
   voxels is excluded from that dose.
5. **In-distribution gate:** ≥ 99% of edited-voxel joint (rCBF_mirror,
   rCBV_mirror) values must fall inside the 99% highest-density region of the
   native joint distribution of the same stratum (census split); report the
   outside fraction per case and dose.
6. **Controls:** bit-identical zero-dose repeat; matched-magnitude sham (same
   |f| with spatially permuted direction); off-deficit edits in mirror-normal
   tissue; independently specified Tmax positive control (+2 s, +4 s within
   the deficit) as the channel-sensitivity floor.
7. **Identity residual:** the census measures the voxelwise residual of
   MTT − CBV/CBF on released maps; if the identity does not hold (large
   residual), the co-scaling rule is replaced by movement along the empirical
   conditional joint curve, per the card.

### 3f. Judgment on the operator's kill condition

Workable precedent **exists** at every layer the design actually needs:
input-perturbation probing on this exact task family (§3a), accepted
counterfactual image editing in neuroimaging (§3b), and routine arithmetic
manipulation of these exact map types in clinical methods work (§3c). The
genuinely unprecedented element — the identity-preserving joint edit — is a
*constraint added on top of* precedented operations that makes the
intervention strictly closer to the data manifold than published occlusion
probes, and §3e gives it a numeric, checkable realism budget. The
absence-of-precedent kill is therefore **not triggered**. What the missing
exact precedent does cost is effect-size calibration, which is why the
equivalence margin must come from sham variability (already in the card) and
why the census precedes all model work.

## 4. Labels, concept validity, annotation provenance

- **Ground truth:** final-infarct masks derived from follow-up MRI (DWI, 2–9
  days post-acute) using DeepISLES, with quality control and correction by
  medical students supervised by two neuroradiologists (>10 y experience).
  VERIFIED this stage (challenge paper). Provenance is documented — the
  program's dominant ANNOTATION_PROVENANCE failure mode does not apply to the
  primary readout, which is a label-free paired model-output delta; labels
  enter only the census (K2) and model training.
- **X is computable without an annotator:** rCBF_mirror and rCBV_mirror are
  deterministic arithmetic on released maps plus automatic midline
  estimation. Mirror-estimation quality is a Stage 0 gate (UNVERIFIED).
- **Clinical covariates:** the challenge paper promises "demographics,
  clinical history, laboratory results, neurological scores, and outcome
  measures" including admission NIHSS and 3-month mRS; a
  `clinical_data-description.xlsx` is separately downloadable from the v2
  Zenodo record. **Whether reperfusion status (mTICI) and treatment times are
  released is UNVERIFIED** — no inspected source names mTICI. This matters:
  the census's treatment-handling clause activates only if these fields
  exist; if absent, that absence is a recorded scope limit (per the card),
  not a blocker. Resolving this costs a 12 MB download and is the cheapest
  outstanding fact in the whole study.

## 5. Sample structure and split unit

- 149–150 cases, one acute session per patient; **split unit = patient**
  (equivalently case). VERIFIED structure via Zenodo/BIDS description.
- The challenge's 98-case test set is hidden; all work happens on the released
  training cases. The card's census/probe separation (census patients vs
  held-out toggle patients, frozen before outcome inspection) is the split
  that matters; with ~150 patients, a 100/50 or 110/40 census/probe split is
  the realistic envelope. INFERENCE.
- **Power is the honest weak point:** patient-clustered estimation of a
  continuous outcome–state relationship (and any change point) from ~100
  census patients across three strata may fail the precision gate. That is
  what the gate is for; it is a named, cheap death, not a hidden one.

## 6. Existing code and checkpoints (material update to the card)

The card assumed no released challenge weights. That is now **false in a
useful direction** (all VERIFIED this stage from the challenge paper §Code
Availability and the repos):

- **#1 Kurtlab** (Dice 0.285): github.com/KurtLabUW/ISLES2024 — inference
  Docker + preprocessing + nnU-Net folder; weights via a Google Drive link in
  `model weights.txt`. Exact input channels NOT stated in the paper
  (arXiv:2505.18424 describes NCCT-based skull-strip + windowing applied to
  co-registered scans); channels must be read off the repo/plans file at
  Stage 0. Link liveness UNVERIFIED.
- **#2 AMC-Axolotls** (Dice 0.263): github.com/Mahsa0M/isles2024_docker —
  nnU-Net v2 3d_fullres, **six declared input channels: NCCT, CTA, rCBF,
  rCBV, MTT, Tmax**, weights via Google Drive
  (drive.google.com/file/d/1i9GvcanpopV-M6omJ8w-NbNv4ZoLyKnM). The perfusion
  maps are input channels, so the proposed edits have a port of entry into a
  real benchmark submission. Multimodal (NCCT+CTA present), so per the card
  it is a *secondary* probe target, and the maps-only self-trained model
  remains primary. Link liveness and license of the weights UNVERIFIED.
- **#3 Ninjas**: github.com/jaymoz/ISLES-Challenge-2024 — not yet inspected.
- **kimberly-amador/ISLES24-PrediCTP**: takes 4D CTP, no released weights —
  no port of entry for map edits; excluded. VERIFIED.

Consequence: the model gate is stronger than the card assumed. The Stage 0
weight inventory has concrete targets, and the "benchmark model" framing can
be partially earned (scoped to the specific probed submissions) rather than
resting only on a self-trained family.

## 7. Compute estimate

- **Download:** one-time ~99 GB from Zenodo. Selective 7z extraction keeps
  disk below ~120 GB transient / ~20 GB persistent (estimate; UNVERIFIED).
- **Stage 0 census:** CPU-only, hours on the derivative subset once
  extracted; no GPU.
- **Self-trained maps-only model:** nnU-Net ResEnc M is the honest Colab
  target — documented at 9–11 GB VRAM and ~12 h per fold on an A100
  (VERIFIED, nnU-Net resenc_presets.md). ResEnc L (24 GB, ~35 h/fold) fits an
  A100-40GB Colab session budget only with checkpoint-resume across sessions;
  the winner's ResEnc-L-class recipe is therefore reproducible but expensive.
  Recommend freezing ResEnc M (or standard 3d_fullres), 1–2 folds on a frozen
  split, not 10-fold. Total: roughly 1–3 A100-days, resumable.
- **Probe inference:** ~40 held-out cases × (4 doses + zero-dose + sham +
  off-deficit + 2 Tmax-control variants ≈ 9 variants) ≈ 360–800 forward
  passes; nnU-Net 3D inference ~1–2 min/case-variant → ~10–25 GPU-hours.
  Fits single-GPU sessions. INFERENCE from standard nnU-Net behavior.

## 8. Baselines and accepted metrics

- Challenge metrics are established: Dice, absolute volume difference,
  lesion-wise F1, absolute lesion count difference (VERIFIED, official repo
  evaluation notebook + challenge paper).
- Published anchors for the model-performance gate: winner 0.285 ± 0.213
  Dice / 21.2 ± 37.2 mL AVD; #2 0.263; #3 0.255; **clinical rCBF<30%
  baseline 0.163 Dice**. A self-trained maps-only model must beat the
  rCBF<30% baseline on its own frozen validation split to be worth probing —
  a natural, externally anchored floor. Proposed gate (to freeze at Stage 0):
  cross-validated Dice ≥ 0.20 and above the rCBF<30% baseline computed on
  the same split. The primary endpoint (paired within-case output deltas)
  does not use these metrics; they gate model adequacy only.

## 9. Leakage and confounds

- **Within-case paired edits** hold scanner, vendor, site, protocol,
  reconstruction, positioning, habitus, prevalence, and referral pathway
  fixed by construction; mirror ratios kill global scaling. Unchanged from
  the debated card; still correct.
- **Vendor map-generation dependence** (icobrain cva 1.5.0 only —
  VERIFIED via challenge paper + SOURCE-SUPPORTED version number) is the
  admitted rung-2 limit; no released second-vendor map set exists in-cohort.
- **Normalization coupling — imported lesson from idea 021 (external brief,
  2026-08-17):** nnU-Net applies per-channel normalization; whether the
  probed models use per-instance (per-case z-score) or dataset-level fixed
  statistics for the map channels determines whether an edit to deficit-ROI
  values shifts whole-volume statistics and produces a spurious global
  response. The edits here are regional (deficit ROI), so the coupling is
  smaller than 021's hemisphere-scale edits, but the memo adopts the same
  control: **verify the normalization scheme of every probed model
  (plans/preprocessing files) at Stage 0, and add a
  normalization-statistics-held-fixed variant** (reuse the unedited volume's
  normalization constants for the edited volume) as a required validity arm.
  This is a new, concrete Stage 0 item that the card's gate list should
  absorb into the model gate.
- **Label leakage:** none identified — inputs are acute-phase, ground truth
  from follow-up MRI; report text is not an input. Unchanged.
- **Census→probe leakage:** handled by the frozen patient split; the
  equivalence margin derives from sham variability on validation patients
  only.

## 10. Riskiest assumption and its smallest probe

**Riskiest assumption (K2, unchanged):** the released outcomes encode a
precise, directionally stable relationship with the continuous joint CBV/MTT
state within matched-rCBF strata, estimable with patient-clustered inference
from ~100 census patients, with an outcome feature separable from the support
boundary.

**Smallest probes, in ascending cost, all pre-authorized-shape (no model
work, no code beyond the census plan):**

1. **Zero-data probes (minutes):** (a) download
   `clinical_data-description.xlsx` from the pinned record and inventory
   reperfusion/treatment fields; (b) test the two Google Drive weight links
   for liveness and record hashes; (c) enumerate the pinned Zenodo record's
   file list and MD5s via API.
2. **Synthetic power check (CPU, no real data):** before freezing the census
   plan, simulate the planned patient-clustered estimator at n = 100 census
   patients under plausible effect sizes and within-patient voxel counts to
   fix the minimum-support and CI-width numbers in the freeze with known
   operating characteristics — this spends no real outcomes and prevents an
   avoidably underpowered freeze.
3. **The census itself (CPU, days):** the frozen G-label/G-shape analysis on
   the census split; it is simultaneously the keystone inspection and, either
   way it comes out, a citable observation on the CBV/CBF-interaction debate
   in a modern treated cohort.

## 11. Constraint and cap compliance

- Compute: fits Colab Pro+ single-GPU sessions (§7). No DUA. No radiologist
  annotation. Primary readout label-free. Confirmatory/exploratory separation
  and freeze-before-look are encoded in the card's Stage 0.
- `keystone_status` remains `NOT_INSPECTED`; feasibility and
  novelty_confidence stay capped at 3. Nothing in this memo lifts the cap —
  only the census can.

## 12. Verdict

**GO — scoped to Stage 0.** Authorized next steps: pin the Zenodo record and
hashes; the zero-data probes of §10.1; the synthetic power check of §10.2;
freeze the census plan; run the census on the census split. No model
training, no weight download beyond liveness checks, no edit inference is
authorized by this memo; those require the census to pass and a fresh
contract. Three Stage-0 additions beyond the card are recorded here and
should be carried into the contract: (a) the normalization-scheme inspection
and statistics-held-fixed variant (§9), (b) the released-weights inventory
now has two concrete targets with the #2 submission confirmed maps-in-channels
(§6), (c) the census freeze must be preceded by the simulation-based power
check (§10.2).

## In plain terms

This study can be done: the data is public, free, and licensed for research;
the perfusion maps the experiment would edit are confirmed present for every
patient; and — new since the card was written — the top two challenge teams
released their trained models, one of which verifiably takes the perfusion
maps as inputs, so there is a real benchmark model to probe as well as the
planned self-trained one. The cost is one ~99 GB download, a few days of
CPU analysis, and roughly one to three GPU-days of training that only happen
if the cheap analysis passes. Editing input maps to probe a model has
published precedent in this exact disease area (researchers have varied
treatment variables and routinely blank out image regions, which is a harsher
intervention than the bounded edits planned here), so the required
prior-art bar is met. The single biggest practical risk is statistical: with
only about 150 patients, the planned outcome analysis may be too imprecise to
establish the relationship the whole experiment depends on — in which case
the project stops early, cheaply, and with a small publishable observation
rather than a wasted model study.
