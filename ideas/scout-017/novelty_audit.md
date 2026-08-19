# Novelty audit — cycle 017

Searched 2026-08-19 (see `novelty_manifest.json` for the full query log and
establishing passages). Five parallel web searches, one per candidate, 6–10
queries each, identifiers confirmed by fetch where accessible. Absence of a
found duplicate is a flag for human verification, never evidence of novelty.

---

## C1 — The crushed vertebra inside the mortality score (baseline, scout-017-c01)

**1. Neighbors.**

- **RadEdit** (arXiv:2312.12865; ECCV 2024, DOI 10.1007/978-3-031-73254-6_21) —
  mask-constrained diffusion editing of chest radiographs to stress-test
  biomedical vision models; establishes the edit-and-remeasure grammar but
  targets diagnostic classifiers, not mortality models, and adds/removes
  pathology rather than restoring pre-morbid bone shape.
- **Automatic AI tool for opportunistic VCF screening on chest frontal
  radiographs** (PMID 39549901; DOI 10.1016/j.bone.2024.117330; Bone 2025) —
  multicenter deep-learning detection of vertebral compression fractures on
  *frontal* CXR (fracture-level AUC 0.930/0.942); establishes that the
  candidate's X is detectable on the exact projection it needs.
- **AI-enabled chest X-ray classifies osteoporosis and identifies mortality
  risk** (DOI 10.1007/s10916-023-02030-2; J Med Syst) — a CXR osteoporosis
  classifier whose positive output carried all-cause mortality hazard
  (HR 2.59); the nearest conceptual bridge between CXR skeletal signal and
  mortality, but purely correlational — no mortality-model probing, no
  image intervention.

Also relevant: the anchor itself (PMID 31322692) did only Grad-CAM, which
highlighted mediastinum/aortic knob and soft tissue — vertebrae were never
named; and RoentMod (npj Digit Med 2026, s41746-026-02497-6), counterfactual
CXR pathology editing for shortcut detection in diagnostic models.

**2. Delta.** No prior work measures Genant-style vertebral height ratios on
chest radiographs and performs a restorative counterfactual edit (fracture
"undo") to quantify the paired response of a mortality/biological-age model;
the closest neighbor supplies detection only, and the closest editors target
diagnostic pathology models. Side finding that strengthens the card's
keystone: CXR-risk code **and weights are confirmed released** at
github.com/michaeltlu/cxr-risk (`cxr-risk_v1.pth`).

**3. Why not done.** `NEW_CAPABILITY` — validated frontal-CXR vertebral
fracture detection (Bone 2025) and anatomy-preserving CXR counterfactual
editors (RadEdit 2024, RoentMod 2026) both post-date the 2019 anchor;
before them the intervention arm was not buildable, and interpretation of
CXR-risk stopped at saliency.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — multi-angle search
(model interpretation, VCF detection, counterfactual editing, direct
fracture-to-mortality-model queries); neighbors found and distinguished.

---

## C2 — The plug inside the thickened-airway score (baseline, scout-017-c02)

**1. Neighbors.**

- **Simulation-driven annotation-free mucus-plug segmentation** (PMID
  41749693; DOI 10.3390/bioengineering13020153; Bioengineering 2026) — the
  candidate's anchor tool: nnU-Net trained purely on synthetic plugs,
  sensitivity 0.837 / 1.91 FP per scan on 200 COPD CTs; measures X, decodes
  no classifier.
- **Sparse concept channels in frozen 3D CT vision encoders**
  (arXiv:2607.20993) — finds ~10-channel encodings per radiological finding
  in frozen CT encoders and ablates them to collapse single finding scores;
  the same measure-the-logit logic, but via internal channels, not
  image-space physical edits, and not asking the wall-vs-lumen question.
- **AI quantification of airway-occlusive mucus plugs and all-cause
  mortality in COPD** (PMID 39638548; DOI 10.1136/thorax-2024-221928;
  Thorax 2025) — automated volumetric plug burden in ~4,165 patients tied to
  mortality; clinical precedent for plug burden as a measurable CT
  phenotype, no model decoding.

Also relevant: COIN counterfactual inpainting (arXiv:2404.12832, MICCAI
2024) and seamless pulmonary-nodule insertion (PMC5547756) — the removal and
insertion arms of the intervention grammar, applied to other targets.

**2. Delta.** No found work tests whether any report-supervised CT model's
peribronchial-thickening score is driven by intraluminal plug volume versus
wall thickness via bidirectional wall-preserving plug edits; the three
ingredient literatures (plug segmentation, CT-VLM probing, counterfactual CT
editing) exist separately and have not been connected. **Keystone-relevant
adverse finding:** the anchor paper's data-availability statement releases
neither weights nor code ("inquiries to the corresponding author"), so the
card's compute-today condition currently FAILS as stated — Stage 0 needs
author contact or reimplementation of the (fully described) synthetic-plug
training recipe.

**3. Why not done.** `NEW_CAPABILITY` — the annotation-free plug segmenter is
a 2026 publication; before it, plug quantification required manual reads,
which the charter's measurability constraint (and this program's history)
rules out.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — thorough multi-source
search including full text of the anchor; neighbors found and distinguished.
The verdict is about novelty only; the weights finding must flow into the
feasibility gate.

---

## C3 — The detour veins inside the cirrhosis prediction (baseline, scout-017-c03)

**1. Neighbors.**

- **DL prediction of significant portal hypertension from single
  cross-sectional non-enhanced CT** (DOI 10.1007/s00330-025-12010-4; Eur
  Radiol 2025) — predicts portal hypertension from ROIs at the portal vein,
  splenoportal confluence, and spleen; links CT vascular/spleen anatomy to
  the signal but never asks what a cirrhosis model internally requires.
- **nnU-Net segmentation of perigastric varices in sinistral portal
  hypertension** (DOI 10.1007/s00261-026-05545-7; Abdom Radiol 2026) —
  multicenter automated collateral/varix segmentation on contrast CT;
  supplies exactly the measurement arm, no model decoding.
- **Merlin** (arXiv:2406.06512; Nature 2026, DOI 10.1038/s41586-026-10181-8)
  — the anchor model; 1,692 ICD-derived phenotype heads (cirrhosis-type
  outputs among them), weights public at HuggingFace `stanfordmimi/Merlin`.
  No published interpretability or concept-erasure work specific to Merlin
  was found.

Also relevant: TMF-LCNet cirrhosis-outcome model (PMID 40576670), CSPH
CT/MRI vascular model (DOI 10.1148/radiol.221648), and concept-erasure
methodology in medical imaging (PMID 37231202 — snippet-level access only).

**2. Delta.** No found work erases a collateral-vein concept subspace (or any
anatomical vascular subspace) inside a cirrhosis classifier or foundation
model and measures the logit drop against matched control erasures; the
segmentation, portal-hypertension-prediction, and concept-erasure literatures
are disjoint. **Card correction required:** the card cites Merlin as
arXiv:2407.11399, which resolves to an unrelated robotics paper ("Multi-Goal
Motion Memory", cs.RO); the correct identifier is arXiv:2406.06512. The
checkpoint-availability half of the card's unverified claims is now
positively resolved (public weights); the conditional-separability keystone
remains uninspected as declared.

**3. Why not done.** `NEW_CAPABILITY` — a publicly released 3D abdominal-CT
foundation model with phenotype heads (Merlin) and validated automated
varix/collateral segmentation on CT are both 2024–2026 arrivals; neither
community (hepatology imaging, representation-level interpretability) had
the other's asset before.

**4. Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH` — no duplicate surfaced
across nine queries, but several load-bearing passages come from search
snippets (Springer full texts paywalled), and the concept-erasure-in-medical-
imaging neighbor could not be verified beyond snippet level. Human spot-check
of the two 2025–2026 Springer neighbors recommended before shortlisting.

---

## C4 — The spine's calendar inside chest-radiograph age (baseline, scout-017-c04)

**1. Neighbors.**

- **The anchor itself: Yang et al., age/sex prediction from healthy adult
  CXR** (PMID 34640449; DOI 10.3390/jcm10194431; J Clin Med 2021, full text)
  — MAE 2.1 years; its class-activation maps **already name the cervical and
  thoracic spine among "the most crucial activated regions"** and the paper
  attributes this to degenerative spinal change with age.
- **Spine age from lateral spine radiographs / DXA VFA** (DOI
  10.1038/s41514-025-00271-8; npj Aging 2025) — deep-learning spine age
  whose gap predicts fracture and mortality; treats spinal aging morphology
  as a clock, but on lateral spine images with no counterfactual and no CXR
  model.
- **Automated vertebral-body and intervertebral-disc measurement on
  radiographs** (PMC11320507; Quant Imaging Med Surg 2024) — deep-learning
  disc-height measurement, validated on *lateral lumbar* projections only;
  frontal thoracic projected disc height remains unvalidated, which is the
  card's declared keystone.

Also relevant: CXR-Age saliency (Lancet Healthy Longevity 2023,
10.1016/S2666-7568(23)00133-2 — mediastinum/heart, not spine), qCXR-bioage
explainable decomposition (DOI 10.1148/ryct.250327 — includes bone density,
not disc space), RoentMod counterfactual CXR editing.

**2. Delta.** The delta over the closest neighbor is real but narrow: the
anchor already published the coarse attribution ("spine regions, likely
degeneration"); this candidate upgrades that from CAM correlation to a
controlled causal edit isolating disc *spaces* from vertebral bodies and
ribs. The deliverable sentence is therefore partially anticipated in print
by the anchor's own discussion section. Internal overlap: scout-010-c01
(CXR-Age decomposition) is a standing backlog neighbor; the card itself
mandates a duplication check against it before anything else.

**3. Why not done.** `BLIND_SPOT` — the field treated the 2021 saliency
observation as an endpoint rather than a hypothesis (framing), and disc
morphometry lives on lateral spine projections in a different literature
(disciplinary boundary), so nobody built the frontal-projection causal test.

**4. Verdict.** `INCREMENTAL` — no duplicate experiment found, but the core
attribution (spine degeneration drives CXR age) is already published by the
anchor itself at saliency level; what remains novel is the disc-space-
specific causal isolation. Consistent with the card's own novelty_confidence
of 2. Not a kill recommendation; the merge should weigh it as confirmatory-
refining rather than discovery, and enforce the scout-010-c01 overlap check.

---

## C5 — The vascular street map inside lung-cancer risk (baseline, scout-017-c05)

**1. Neighbors.**

- **Auditing Sybil: explaining deep lung cancer risk prediction through
  generative interventional attributions** (arXiv:2602.02560; ICML 2026) —
  approximates Sybil as main effects plus pairwise interactions over
  pulmonary nodules with an age/emphysema-linked background term; probes
  exactly this model but **never parameterizes vasculature**, leaving the
  vessel question explicitly open.
- **Relative loss of small pulmonary vessels and recurrence of resected
  lung adenocarcinoma** (PMID 37590317; DOI 10.1513/AnnalsATS.202303-191RL;
  Ann ATS 2023) — lower BV5/TBV (more pruning) associated with 49% higher
  recurrence per SD and higher mortality; direct clinical evidence that
  lung-wide pruning carries lung-cancer-relevant signal.
- **Pulmonary vascular pruning and risk of death, Framingham** (DOI
  10.1164/rccm.202005-1671LE; AJRCCM) — population-level BV5/TBV pruning
  predicts all-cause mortality (~35% per SD); establishes the measurement
  and its prognostic validity outside any DL model.

Also relevant: quantitative vessel tortuosity radiomics (PMID 30327507 —
nodule-local, not lung-wide), longitudinal pruning vs emphysema/lung-function
change (CHEST S0012-3692(21)00278-6 — the within-person design precedent,
no DL score), and the Sybil anchor (DOI 10.1200/JCO.22.01345, PMID 36634294;
code and checkpoints confirmed public under MIT at
github.com/reginabarzilaygroup/Sybil).

**2. Delta.** The candidate bridges two mature but disjoint literatures:
no found work relates within-person change in vessel-network measures to
within-person change in a DL lung-cancer risk score under the stated
conditioning set, or tests conditional decodability of vessel features from
Sybil's representations — and the newest Sybil audit (the closest neighbor)
explicitly stops short of vascular features, which both motivates the
candidate and confirms the gap is not yet closed.

**3. Why not done.** `BLIND_SPOT` — disciplinary boundary: pulmonary vascular
phenotyping (Estépar/Rahaghi/Washko lineage) and DL risk-model auditing are
separate communities; the ICML audit framed Sybil's feature space as
nodules-plus-background and never included the vasculature in its
intervention vocabulary.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — thorough search across
both parent literatures plus model-specific auditing; the closest neighbor
was read at full text and is complementary, not duplicative. Caveat carried
from the card: this shares idea-009's identifiability terrain and lives or
dies on the declared within-person support gate.

---

## Summary

| # | Candidate | Verdict | Why-not-done |
|---|-----------|---------|--------------|
| C1 | The crushed vertebra inside the mortality score | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C2 | The plug inside the thickened-airway score | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C3 | The detour veins inside the cirrhosis prediction | NO_DUPLICATE_FOUND_LIMITED_SEARCH | NEW_CAPABILITY |
| C4 | The spine's calendar inside chest-radiograph age | INCREMENTAL | BLIND_SPOT |
| C5 | The vascular street map inside lung-cancer risk | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |

Side findings the orchestrator should propagate to the cards:

1. **C2 keystone evidence (adverse):** PMID 41749693 releases no weights or
   code; the card's "YES only if weights are released" compute-today
   condition fails as written. Path forward is author contact or
   reimplementation from the published synthetic-plug recipe.
2. **C3 identifier error:** Merlin is arXiv:2406.06512 (Nature 2026,
   10.1038/s41586-026-10181-8), not arXiv:2407.11399 (an unrelated robotics
   paper). Weights confirmed public (HuggingFace stanfordmimi/Merlin).
3. **C1 keystone evidence (favorable):** CXR-risk weights confirmed released
   (github.com/michaeltlu/cxr-risk, cxr-risk_v1.pth).
4. **C5 keystone evidence (favorable):** Sybil checkpoints confirmed public
   under MIT (github.com/reginabarzilaygroup/Sybil).
5. **C4:** the anchor's own CAM analysis already names the thoracic spine;
   plus the mandated internal duplication check against scout-010-c01
   remains open.
