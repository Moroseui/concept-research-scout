# Novelty audit — cycle isles24-005

Audited 2026-08-19. Candidates numbered C1–C8 by position in
`candidates_all.json` (merged across baseline and wide tracks). Search was
delegated to eight parallel search agents (one per candidate), each running
multi-angle web/PubMed/arXiv queries; the auditor independently re-verified
the four most recently dated (2026) load-bearing identifiers surfaced by the
agents (arXiv:2603.09359, arXiv:2607.03973, DOI 10.3389/fneur.2026.1872532,
DOI 10.1007/s12975-026-01465-2 via PMID 42412265) — all resolve and match.
Full query log in `novelty_manifest.json`. Absence of a found duplicate is
not verified novelty; verdicts use the calibrated vocabulary.

---

## C1 — What the winner's brain window revealed (baseline)

**1. Neighbors.**
- de la Rosa et al. (winning-team report), "How We Won the ISLES'24
  Challenge by Preprocessing" (arXiv:2505.18424) — shows skull stripping plus
  custom intensity windowing improves final-infarct segmentation, but never
  tests which tissue signal the trained model exploits.
- Tsai et al., Critical Care 2024;28:118 (DOI 10.1186/s13054-024-04895-2) —
  automated GWR measurement from brain CT for outcome prediction after
  cardiac arrest; measurement/association only, no model-use test.
- Ostmeier et al., Radiology: AI 2021 (DOI 10.1148/ryai.2021200127) —
  optimizes NCCT acute-infarct segmentation using simulated (inserted)
  hypoattenuating lesions; an intensity manipulation for training, not a
  within-case counterfactual probe of a trained model.

All card-claimed identifiers resolved (including Mallavarapu et al., Front
Neurol 2025, DOI 10.3389/fneur.2025.1629434, automated net-water-uptake
biomarker). A PubMed intersection query (GWR/NWU/hypoattenuation ×
DL × interpretability/counterfactual) returned six hits, none an
intervention test; closest interpretability finding is passive Layer-CAM
activation over hypoattenuated regions (DGA3-Net, PMC10225927).

**2. Delta.** The candidate performs a causal within-case erasure of
gray-white attenuation contrast (regional mean HU and texture preserved,
common-mode shams) on an ISLES'24 final-infarct model, where all located
prior work either measures GWR/NWU as a standalone biomarker or reports a
preprocessing gain without identifying the exploited signal — a solid
delta, not a weak one.

**3. Why not done.** `BLIND_SPOT` — every tool exists (nnU-Net, tissue
segmentation, HU manipulation); challenge culture rewards leaderboard Dice,
and stroke-CT interpretability has stayed at passive saliency maps rather
than physiology-grounded interventions.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — 13-query
multi-source search across the biomarker, preprocessing, and
interpretability literatures; neighbors found and clearly distinguished; no
model-use test of gray-white contrast located.

---

## C2 — The old stroke inside the new forecast (baseline)

**1. Neighbors.**
- Mah, Nachev, MacKinnon, Front Neurol 2020 (DOI 10.3389/fneur.2020.00015;
  read in full text) — automated chronic-lesion segmentation on admission
  NCCT in 1,704 patients feeding SVM outcome models (AUROC ~0.76-0.77);
  purely prognostic association, no intervention.
- IST-3 "brain frailty" line (IST-3 imaging secondary analysis, DOI
  10.1016/S1474-4422(15)00012-5; brain-frailty scores, DOI
  10.1161/STROKEAHA.120.029841) — old infarcts, atrophy, and leukoaraiosis
  on baseline CT independently associated with worse 90-day mRS; human-
  scored epidemiology, no learned model.
- Counterfactual-diffusion lesion editing: Durrer et al., MedEdit
  (arXiv:2407.15270) and Sanchez et al., MICCAI DGM4 2022 (DOI
  10.1007/978-3-031-18576-2_4) — supply lesion add/remove machinery on
  brain images, used for synthesis or anomaly localization, not to probe a
  trained infarct-prediction model.

Both card-claimed identifiers resolved (10.1148/radiol.2021203964 =
ESCAPE-NA1 infarct-pattern analysis; 10.1148/ryai.250603 = ISLES'24 dataset
paper).

**2. Delta.** First sham-controlled, within-case inpainting audit of
whether a learned final-infarct model uses remote chronic cavities as a
reserve signal; the prognostic-association and inpainting-tooling
literatures exist separately and have never been combined into a
model-behavior test.

**3. Why not done.** `BLIND_SPOT` — both ingredients (brain-frailty
prognostics, lesion-inpainting tools) are mature but live in disjoint
communities; stroke-AI work optimizes Dice, not model-use questions.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — 12-query search
across PubMed/PMC, arXiv, RSNA, and general web including full-text reading
of the closest neighbor; adjacent literatures located and distinguished; no
intervention test of chronic/remote lesions on a learned stroke model
found.

---

## C3 — The bottleneck before the brain (baseline)

**1. Neighbors.**
- Nielsen et al., Stroke 2018 (PMID 29720437) — deep tissue-outcome model
  with counterfactual treatment-regime comparison (treated vs untreated
  networks); the intervention is a clinical covariate, not an image-level
  vessel edit.
- "Prediction of tissue and clinical thrombectomy outcome in acute
  ischaemic stroke using deep learning," Brain 2025;148(7):2348 —
  counterfactual reperfusion-status toggle on a stroke outcome model; again
  a covariate toggle, not a CTA stenosis edit.
- "Deep learning-based hemodynamic prediction of carotid artery stenosis
  before and after surgical treatments," Front Physiol 2023 (PMC9872942;
  read in full text) — 1,000 artificially modified stenosis geometries
  (virtual surgery) for CFD-surrogate hemodynamics; the lumen-editing move
  exists, but with no stroke-outcome or infarct model attached.

All four card-claimed identifiers resolved (White PMID 20724259; CarotidNet
PMID 33392012 / DOI 10.21037/qims-20-286; arXiv:2408.10966;
arXiv:2505.18424).

**2. Delta.** First anatomically constrained CTA lumen-restoration probe
(with contralateral and nonstenotic shams, perfusion maps frozen) of what a
final-infarct model uses; prior counterfactuals on stroke models toggle
clinical covariates, and prior lumen edits serve CFD, not model auditing.
The delta is genuine but the payoff is interpretability evidence, and it
hinges on enough high-grade-stenosis cases existing in the 149-case cohort
(the card's own uninspected keystone).

**3. Why not done.** `BLIND_SPOT` — interpretability work on stroke outcome
models toggles covariates rather than anatomy; virtual-surgery vessel
editing grew up in the CFD community with no contact with infarct
prediction.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — 12+ searches across
PubMed, arXiv, PMC, and general web covering vessel editing, virtual
stenting, counterfactual explanation, tandem occlusion, and ISLES'24
angles; strong neighbors in every adjacent literature, none combining
vessel editing with a model-use test.

---

## C4 — The pressure history written in a winding artery (baseline, Mode C)

**1. Neighbors.**
- Yoon, Oh, Kim, Brain Sciences 2023 (PMC10669197; read in full text) — ML
  regressors predict chronological age from intracranial vessel tortuosity
  and diameter on TOF-MRA (best r = 0.532); validates the tortuosity-age
  premise but builds a forward predictor, not an audit of a stroke model.
- "Quantitative Cerebrovascular Analysis for Improved Prediction of
  Post-Stroke Complications," Transl Stroke Res 2026 (DOI
  10.1007/s12975-026-01465-2; PMID 42412265; auditor-verified) — ML models
  feeding automated arterial morphology including tortuosity into post-EVT
  complication prediction (morphology-informed AUROC 0.81 vs clinical
  0.73); tortuosity as an explicit engineered input, not an audit of what
  an end-to-end model implicitly uses.
- "Deep Learning-Based Vascular Aging Prediction From Retinal Fundus
  Images," TVST 2024 (PMC11238877) — adjacent-field evidence that deep
  models already exploit vessel tortuosity as a vascular-aging signal in
  retinal imaging; forward prediction, not a reliance audit.

Both card-claimed identifiers resolved; note the card cites "Kim et al."
for DOI 10.13104/imri.2018.22.3.150 whose first author is Byun (Bum-soo Kim
is a co-author) — loose but not wrong attribution; content matches.

**2. Delta.** Moves from "tortuosity predicts age/outcomes" (well
established, including with ML) to "does a trained infarct model covertly
condition on tortuosity" via stratified residual-vs-ground-truth analysis —
a model-audit question not found asked anywhere; flagged weakness: the
Mode C observational design cannot support a use claim, and heavy
stratification may be underpowered at 149 cases.

**3. Why not done.** `BLIND_SPOT` — shortcut-learning audits in medical
imaging target site/scanner confounds, not physiologically meaningful
vascular-geometry constructs; the tortuosity literature stays on the
association side.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — multi-source search
(PubMed/PMC full texts, Springer, Frontiers, medRxiv, arXiv, shortcut-
learning literature) found close neighbors on every side and none auditing
a learned stroke model's use of tortuosity.

---

## C5 — Do sulci pin the predicted infarct edge? (baseline, Mode C)

**1. Neighbors.**
- "Anatomy-aided deep learning for medical image segmentation: a review,"
  Phys Med Biol 2021 (DOI 10.1088/1361-6560/abfbf4) — catalogs deliberate
  injection of anatomical priors to help segmentation; never asks whether a
  model spontaneously pins lesion edges to cortical geometry.
- "Boundary-aware and uncertainty-guided deep learning for multimodal MRI
  segmentation of stroke lesions," Front Neurol 2026 (DOI
  10.3389/fneur.2026.1872532; auditor-verified) — characterizes stroke-
  lesion boundary errors and uncertainty (ISLES-2022) as intensity/contrast
  phenomena; no relation of error localization to sulcal depth or
  curvature.
- Linear/nonlinear concept-erasure lineage: LEACE (arXiv:2306.03819), INLP
  (Ravfogel et al. 2020), MANCE (arXiv:2607.03973; auditor-verified) —
  supplies the erasure machinery, developed on NLP/vision representations,
  with no application to anatomical curvature in a medical segmentation
  network.

Card-claimed identifier 10.1148/radiol.2021203964 resolved (ESCAPE-NA1
infarct-pattern paper).

**2. Delta.** Uniquely frames predicted-edge placement as interface pinning
to cortical curvature and tests it with within-case matched-vertex
enrichment plus curvature-direction erasure, a pairing absent from the
boundary-error, anatomy-prior, and concept-erasure literatures.

**3. Why not done.** `BLIND_SPOT` — the community treats lesion-edge errors
as intensity/annotation artifacts and treats anatomy as a helpful prior to
be added, not a spurious scaffold to be probed.

**4. Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH` — downgraded by the
auditor from the search agent's claimed high confidence: the search was
bounded (~10 queries, closest-neighbor access mostly search summaries, RSNA
fetch blocked), the located neighbors are generic rather than specific to
the sulcal-pinning question, and the claim territory (segmentation error
analysis) is broad enough with varied vocabulary that a near-duplicate
could plausibly hide under different terms. Human verification flag, not
evidence of novelty.

---

## C6 — Does the model trust tissue that obeys the flow equation? (wide)

**1. Neighbors.**
- Lee et al., "Evidential Perfusion Physics-Informed Neural Networks with
  Residual Uncertainty Quantification" (EPPINN), arXiv:2603.09359 (read in
  full text; auditor-verified) — places a distribution over the physics
  residual for uncertainty in CTP parameter estimation and enforces the
  central volume principle by construction (CBF = CBV/MTT); no intervention
  removing the residual and no downstream infarct-model audit.
- Kudo et al., Radiology 2010 (PMID 20032153; DOI 10.1148/radiol.254082000)
  — identical stroke source data produce significantly different maps
  across commercial software (tracer-delay sensitivity); establishes
  estimator-dependence of released maps, motivating but not testing a
  hidden inconsistency cue.
- Liu et al., ISP-Net, Comput Methods Programs Biomed 2022 (DOI
  10.1016/j.cmpb.2022.106630) — early-fusion network over native CTP + CBF
  + CBV + MTT + Tmax for infarct prediction; exactly the model class to be
  probed, with no examination of cross-map physical consistency.

Identifier note: the card's Kudo DOI 10.1148/radiol.254082000 resolves via
doi.org to the correct article, though Radiology's canonical rendering is
often 10.1148/radiol.2541082000; both point to PMID 20032153. Konstas PMID
19270105 consistent. PubMed article pages were cookie-blocked during this
search; resolution was confirmed via doi.org and publisher indexing.

**2. Delta.** No located work intervenes on the voxelwise CBV=CBF×MTT
residual (consistent-manifold projection vs equal-energy tangent shams) to
test whether a trained final-infarct model reads cross-map inconsistency as
a confidence signal; existing physics-consistency work enforces or
quantifies the identity during map estimation instead.

**3. Why not done.** `BLIND_SPOT` — physics-consistency research targets
map estimation and uncertainty; model papers treat the maps as independent
channels; nobody has reframed the residual as an audit instrument for a
downstream model.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — 14-query search
including full-text reading of the closest (2026 physics-informed) neighbor
and DOI-resolution checks; neighbors span all three adjacent literatures
and are clearly distinguished.

---

## C7 — The roughness of a heartbeat through starved tissue (wide)

**1. Neighbors.**
- Ichikawa, Kondo, Yokoyama, "Time series-derived fractal dimension of CT
  perfusion in acute ischemic stroke...," Int J Comput Assist Radiol Surg
  2025 (PMID 40824507; DOI 10.1007/s11548-025-03500-3) — Higuchi FD on
  voxelwise CTP time series in phantoms and all 149 public ISLES'24 cases;
  FD tracks true CBF (rho>0.9 phantom), separates core/penumbra/normal
  (AUC 0.732 penumbra-vs-normal); explicitly no deep learning, no trained
  model, no use test.
- Winder et al., Front Neurosci 2022 (DOI 10.3389/fnins.2022.1009654; read
  in full text) — raw concentration-time-curve UNet for tissue outcome
  (Dice 0.296) matching deconvolved inputs; learned temporal features
  probed only by Spearman correlation against CBF/CBV/MTT/Tmax — no fractal
  descriptors, no erasure.
- Klug et al., J Cereb Blood Flow Metab 2021 (PMID 32501132) — regional
  perfusion-CT context (cuboid receptive field) improves final-infarct
  prediction (AUC 0.89 vs 0.79); deconvolved maps and GLMs, no temporal
  fractal features, no model-internals analysis.

Identifier corrections of record (all three identifiers resolve and match
the card's content claims, but all three author attributions on the card
are wrong): PMID 40824507 is Ichikawa/Kondo/Yokoyama, not "Lim et al.";
DOI 10.3389/fnins.2022.1009654 is Winder et al., not "Robben et al."
(Robben's raw-CTP paper is Med Image Anal 2020, DOI
10.1016/j.media.2019.101589); PMID 32501132 is Klug et al., not "van Os."
The card's `keystone_evidence` content (149 ISLES'24 cases, FD findings) is
confirmed against the abstract via Europe PMC; only the author name needs
correcting. INSPECTED_TRUE substance stands.

**2. Delta.** Upgrades the Ichikawa association-level biomarker (exact
feature, exact dataset) and Winder's correlational feature probe to a
causal graded-erasure use test inside a trained raw-CTP model, with
CBF/curve-moment-matched controls — a clean, strong delta.

**3. Why not done.** `NEW_CAPABILITY` — the FD-on-ISLES'24 biomarker result
appeared in August 2025 and closed-form linear concept erasure
(LEACE-style, 2023) has not yet crossed into the CTP/stroke imaging
community; the prerequisites only recently coexist.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — 14-query search
including Europe PMC API retrieval of the keystone abstract and full-text
reading of the closest model-side neighbor; no model-use or erasure test of
temporal FD (or an equivalent roughness descriptor) located anywhere.

---

## C8 — Delay is not dispersion (wide)

**1. Neighbors.**
- Calamante et al., Magn Reson Med 2006 (PMID 16598717; DOI
  10.1002/mrm.20873) with the closer follow-up Willats et al., Stroke 2012
  (PMID 22343645; DOI 10.1161/STROKEAHA.111.635888) — explicitly separates
  delay from dispersion and assesses their effect on tissue predictor
  models, but in DSC-MRI with classical deconvolution/threshold predictors,
  treating dispersion mainly as a measurement error source.
- Lin et al., Stroke 2020 (PMID 31948385; DOI 10.1161/STROKEAHA.119.028284)
  — CTP collateral index validated against dynamic CTA, built entirely on
  delay-time thresholds; does not isolate dispersion/curve shape from
  delay, no learned model.
- Winder et al., Front Neurosci 2022 (DOI 10.3389/fnins.2022.1009654; read
  in full text) — raw-CTP causal temporal network for tissue outcome; full
  text confirmed to contain no perturbation, counterfactual, or curve-
  manipulation experiments.

Identifier note: two card identifiers resolve exactly; the Frontiers DOI
resolves but is misattributed to "Robben et al." — authors are Winder et
al. (same correction as C7).

**2. Delta.** Genuine: prior work established delay/dispersion as coupled
error sources or used delay alone as a collateral proxy; no located work
causally probes a trained raw-CTP model with transport-cost-matched,
factorized dispersion-only vs delay-only curve edits. The Willats 2012
finding that delay AND dispersion information matters for classical
predictor accuracy strengthens the motivation without preempting the
model-use question.

**3. Why not done.** `NEW_CAPABILITY` — end-to-end raw-4D-CTP models with
follow-up-DWI ground truth only became broadly trainable with ISLES'24-
style public data; the paired optimal-transport curve-edit methodology
postdates the delay/dispersion physics literature.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — 11-query search
across perfusion physics, collateral quantification, raw-CTP deep
learning, and counterfactual time-series ML, including full-text
verification that the nearest model paper contains no curve-perturbation
experiments; a closer neighbor than the card's (Willats 2012) was found
and distinguished.

---

## Summary

| Candidate | Title (short) | Verdict | Why-not-done |
|---|---|---|---|
| C1 | What the winner's brain window revealed | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C2 | The old stroke inside the new forecast | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C3 | The bottleneck before the brain | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C4 | The pressure history written in a winding artery | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C5 | Do sulci pin the predicted infarct edge? | NO_DUPLICATE_FOUND_LIMITED_SEARCH | BLIND_SPOT |
| C6 | Does the model trust tissue that obeys the flow equation? | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C7 | The roughness of a heartbeat through starved tissue | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C8 | Delay is not dispersion | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |

Cross-cutting findings for the ledger: (a) C7's card cites its
INSPECTED_TRUE keystone as "Lim et al." — the PMID and content are
confirmed, but the authors are Ichikawa, Kondo, Yokoyama (DOI
10.1007/s11548-025-03500-3); (b) C7 and C8 both cite DOI
10.3389/fnins.2022.1009654 as "Robben et al." — the authors are Winder et
al.; C7 also cites PMID 32501132 as "van Os" — the first author is Klug.
Content claims behind all three citations are accurate; author fields
should be corrected at the next card revision. (c) No duplicate was found
for any candidate; per the audit rules this is a flag for human
verification, never proof of novelty.
