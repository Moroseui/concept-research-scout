# Feasibility memo — idea 004

**Question under audit:** Across geometry-matched alternative reconstructions of the
same CT-RATE acquisition, how much do the frozen ClassFine abnormality scores change?

**Date:** 2026-08-11. All web inspections performed today unless attributed to Stage 0
(2026-08-04) or the prior critique.

---

## 1. Keystone resolution: the checkpoint EXISTS (headline finding)

Stage 0 concluded the ClassFine checkpoint was unavailable after inspecting GitHub
v1.0.0 release assets and the authors' Hugging Face *model* account. Both were the
wrong places. Directly inspected today:

- **Verified fact:** The official CT-CLIP GitHub README
  (github.com/ibrahimethemhamamci/CT-CLIP) links model downloads hosted **inside the
  CT-RATE dataset repository**: "CT-CLIP (ClassFine): Download Here →
  `huggingface.co/datasets/ibrahimhamamci/CT-RATE/blob/main/models/CT-CLIP-Related/CT_LiPro_v2.pt`".
- **Verified fact:** The HF file-listing page for
  `datasets/ibrahimhamamci/CT-RATE/tree/main/models/CT-CLIP-Related` displays three
  files — `CT-CLIP_v2.pt`, `CT_VocabFine_v2.pt`, `CT_LiPro_v2.pt` — each **1.77 GB**,
  pickle format. The listing is visible without authentication ("You can list files
  but not access them"); downloads require accepting the gate.
- **Verified fact:** The HF API reports `gated: "auto"` — approval is automatic on
  agreeing to share contact information. No manual review, no DUA committee. This
  satisfies the charter's "no unconfirmed DUA-gated data" constraint once the user
  performs the one-time click-through.

**Naming caution (verified):** the file the README labels "CT-CLIP (ClassFine)" is
named `CT_LiPro_v2.pt` (linear-probing nomenclature). The load probe must confirm the
inference scripts (`run_forward_data.py` / `data_inference_nii.py`, identified in
Stage 0) consume this file for the 18-output ClassFine head.

**Keystone status: INSPECTED_TRUE for existence and obtainability** (official path,
file size, gate mechanics all directly inspected).

*"If I have only verified the nearest checkable thing, what am I still assuming?"*
I verified the file exists at an officially endorsed path. I am still assuming:
(a) the checkpoint **loads unchanged** with the released inference code and emits 18
scores; (b) the **v2** weights are the version corresponding to the current released
preprocessing and the published results (CT-RATE was corrected post-release; the
repo's main branch and the v2 checkpoints are the officially endorsed current
pairing, but paper-number correspondence is inferred, not inspected). Assumption (a)
is load-bearing and cheap to kill: it is the smallest probe (§9). Assumption (b) does
not threaten the primary readout, which compares the model with itself; it only
constrains how the result is attributed ("the released v2 ClassFine checkpoint",
not "the checkpoint behind Table N of the paper") until verified. Freeze the HF
commit hash and the LFS SHA-256 (displayed by HF) at download time.

## 2. Closest work and exact gap

Nearest works, all from the prior critique (primary sources inspected then), none
overturned by today's searches:

- Zuo et al., cross-domain feature-map consistency across paired LIDC kernels
  (PMCID PMC9503667) — segmentation, not CT-RATE, not ClassFine outputs.
- Hwang et al., kernel conversion for quantitative chest CT (PMID 35112080, DOI
  10.3389/frai.2021.769557) — quantitative measures, not abnormality heads.
- Liard et al., kernel variability vs segmentation consistency in low-dose thoracic
  CT (DOI 10.1117/12.3085743) — closest design vocabulary, segmentation endpoint.
- LDCT foundation-model feature robustness across kernels/thickness (PMID 42038169)
  — features, not CT-CLIP's 18 scan-level outputs.

Today's targeted searches (CT-CLIP/CT-RATE reconstruction sensitivity; CT-RATE
duplicate-reconstruction benchmark bias) surfaced **no** paper performing a paired,
within-acquisition, geometry-matched audit of ClassFine scores on CT-RATE, and none
exploiting the reconstruction duplication for evaluation-dependence analysis.
**"I did not find it" is not proof**: MICCAI/SPIE/MIDL proceedings and the full
CT-RATE citation graph remain unsearched at depth. Novelty confidence stays at 3.

**Exact gap:** paired reconstruction sensitivity of a released 3D chest-CT
foundation model's named abnormality outputs, on the corpus that model was trained
and benchmarked on, with preprocessing held byte-identical via geometry matching.

## 3. Dataset access and license

- CT-RATE: gated `auto`, CC-BY-NC-SA-4.0 (verified on dataset card today).
  Non-commercial research use is compliant. No redistribution of images.
- Total corpus 21.3 TB, but the study needs **850 validation volumes** (425 pairs,
  Stage 0 frozen list) plus one 1.77 GB checkpoint. Per-file HTTP download is
  supported, so the gated corpus size is irrelevant.
- Validation patient count on the card: **1,304** — matches Stage 0's count and
  resolves the 1,304-vs-1,314 discrepancy in favor of the official card (the 1,314
  figure belongs to the external benchmark paper's filtering, to be noted, not used).

## 4. Labels and concept validity

The primary readout is **label-free** (model vs itself on paired volumes). CT-RATE's
RadBERT-derived labels are used nowhere in the primary endpoint; the 18 outputs are
named report-derived heads, not validated concepts, and the card's prohibited
conclusions already enforce that language. No annotation-provenance exposure.

## 5. Sample structure and split unit

Stage 0 (directly inspected metadata): 3,039 validation volumes / 1,564 scans /
1,304 patients; 425 strict geometry-matched pairs; contrasts Br40f|Br60f (237),
Bl56f|Br40f (126), Bl57d|Br36d (58), Br40f|Br44f (4, exploratory). Patient is the
outer bootstrap unit (patients contribute multiple scans). The pair list is frozen
before any download. 462/464 audited volumes Siemens — vendor-specific scope stands.

## 6. Code and checkpoints

- Inference code: verified present in the official repo (Stage 0).
- Checkpoint: verified present and obtainable (§1).
- Preprocessing: deterministic, fully characterized in the idea-006 unblock check
  (fixed HU clip, fixed resample target, fixed crop/pad) — supports the
  geometry-matched identical-function argument.

## 7. Compute estimate

- Download: 850 volumes × ~0.42 GB average (21.3 TB / 50,188) ≈ **~360 GB** total,
  processed in chunks (download → preprocess → infer → delete) within Colab Pro+
  disk limits. This is the dominant cost: dozens of hours of transfer, days of
  wall-clock across sessions, not GPU-bound.
- Inference: ~0.5 s/volume (official README) → minutes of GPU. Preprocessing
  (trilinear resample to 0.75×0.75×1.5 mm, crop/pad to 480×480×240) dominates at
  maybe 10–30 s/volume CPU → single-digit hours.
- No patch-size modification permitted (official warning re small-pathology
  performance); released configuration at batch size 1.

## 8. Baselines, metrics, leakage, confounds

- Metrics: paired score differences (probability and logit scales), repeatability
  coefficient / upper |Δ| quantile per contrast stratum, patient-level bootstrap.
  All standard; no custom infrastructure.
- Equivalence margin: to be fixed from the CT-Scroll benchmark's between-method
  AUROC spread on CT-RATE validation (arXiv:2503.20652 — existence and CT-RATE
  evaluation verified today from the abstract; **tables not yet extracted**, PDF
  inspection required at margin-fixing time, before any paired score is seen).
- Leakage/confounds: within-pair design removes patient, anatomy, habitus,
  prevalence, referral, and report-leakage alternatives; strict geometry matching
  removes differential preprocessing; vendor (Siemens) and site remain scope
  limitations, already stated. Interpretive note, not leakage: ClassFine was
  trained on reconstruction-expanded data, so observed invariance is partly a
  learned property of this training policy — the claim is already restricted to
  this checkpoint.

## 9. Smallest probe of the riskiest assumption

Riskiest surviving assumption: **the checkpoint loads and runs unchanged with the
released code** (§1a). Probe, requiring human approval and gate acceptance, before
any bulk download:

1. Accept the CT-RATE gate (one click-through; user action).
2. Download `CT_LiPro_v2.pt` (1.77 GB); record HF commit hash and SHA-256.
3. Load with the released inference scripts; confirm an 18-output head.
4. Download **one** Br40f|Br60f pair (~1 GB); run inference; confirm scores emerge
   and that an identical-file rerun is bit-deterministic.

Total ≈ 3 GB and under an hour of session time. If step 3 or 4 fails, the idea
stops per the card's stop rule before any material cost.

## 10. Verification ledger

| Claim | Status |
|---|---|
| ClassFine checkpoint exists at official path, 1.77 GB | VERIFIED (file listing inspected) |
| Gate is automatic click-through | VERIFIED (API `gated:"auto"`) |
| License CC-BY-NC-SA-4.0 | VERIFIED (dataset card) |
| Checkpoint loads with released code | NOT VERIFIED — probe §9 |
| v2 weights ↔ published paper numbers | NOT VERIFIED — attribution constrained until checked |
| 425 geometry-matched pairs | VERIFIED (Stage 0 direct metadata audit) |
| CT-Scroll margin tables usable | PARTIALLY — paper exists, evaluates CT-RATE; tables not extracted |
| No exact prior audit exists | NOT PROVEN — limited search only; proceedings sweep outstanding |

## 11. Score implications (recommendation only; card not modified)

`keystone_status` should move to `INSPECTED_TRUE`, lifting the cap: feasibility
3 → 4 (bounded download, trivial GPU, frozen pair list; residual is the unprobed
load step), data readiness 3 → 4 (gate confirmed automatic). Novelty confidence
stays 3 pending the proceedings sweep. Priority recomputes to
0.20*4 + 0.15*4 + 0.15*3 + 0.10*4 + 0.10*3 + 0.10*5 + 0.10*4 + 0.05*4 + 0.05*3 = **3.90**.

## Decision

**GO** — conditional on the §9 load probe as the first gated step (needs human gate
acceptance and probe-contract approval), and on fixing the equivalence margin from
the CT-Scroll tables before any paired score is inspected. No blocking unknown
remains; the Stage-0 "checkpoint unavailable" finding is corrected by direct
inspection of the official download path.
