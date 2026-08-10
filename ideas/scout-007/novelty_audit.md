<!-- stage: novelty_audit -->
# Novelty audit — cycle scout-007

Scope: the eight developed candidates in `candidates_all.json` — baseline C1–C5
and wide W1–W3. Dropped wide candidates (W4–W8) and the fiction track
(`NO_TESTABLE_KERNEL`) carry no novelty claim and are not audited here.

Each candidate was audited by fresh web search (not recall) for its three
closest prior works, the delta against the nearest neighbor, why the field has
not done it, and a verdict. Verdicts are conservative: a `NOVEL_*` verdict
rests on the *absence* of a located duplicate, which is a flag for human
verification, never a proof of novelty. Identifiers below are as returned by
the searches; several should be dereferenced before any priority claim.

---

## C1 — The knee-pain model may be reading trabecular stress architecture that KL grade throws away
**Track: baseline (Mode A)**

**1. Neighbors.**
- Pierson et al., "An algorithmic approach to reducing unexplained pain
  disparities in underserved populations," *Nature Medicine* 27:136–140 (2021),
  DOI 10.1038/s41591-020-01192-7 (PMID 33442014). The target model (ALG-P);
  recovers pain variance that KL grading misses but explicitly leaves *what it
  reads* as future work.
- Commentary, "An Algorithmic Approach to Understanding Osteoarthritic Knee
  Pain," PMC10545400 (2023). States plainly that the field does not know what
  ALG-P "sees" in a KL 0–1 radiograph that flags pain; frames decoding as open.
- Janvier et al., "Subchondral tibial bone texture predicts the incidence of
  radiographic knee OA: data from the OAI," *Osteoarthritis and Cartilage*
  25(12):2047–2054 (2017), DOI 10.1016/j.joca.2017.09.004 (PMID 28935435).
  Directional fractal/VOT trabecular texture on OAI radiographs predicts OA
  *incidence/progression/TKR* — the review PMC8344203 confirms it is validated
  against structure, never against pain. (Distant: Guan et al. 2021, PMID
  33835240, GradCAM on a different pain-*progression* model attends to "bone,"
  no concept isolation.)

**2. Delta.** C1 is the first to test whether ALG-P's KL-invisible pain signal
is *causally carried* by a specific pre-registered feature — directional
subchondral trabecular fractal texture — via concept-direction erasure on the
frozen embedding, rather than leaving the model a black box or linking texture
only to OA structure.

**3. Why not done.** `BLIND_SPOT`. Two literatures that never met: the
pain-disparity/ALG-P side treats the model as a black box and names no feature;
the trabecular-texture side validated FSA/VOT exclusively against structural OA
endpoints, never pain. No one joined them with a causal-erasure probe.

**4. Verdict.** `NOVEL_VERIFIED`. Caveat: the mechanistic prior is only
moderate — Janvier's texture predicts *structure*, so a positive erasure result
could be a proxy for early structural change; the design must retain an explicit
KL/JSN-conditioned control.

---

## C2 — A breast-cancer risk model may be reading the arteries as a vascular clock
**Track: baseline (Mode B)**

**1. Neighbors.**
- Jia, Xu, Chen, Shen, Heacock, "Revealing Mammographic Phenotypes in Deep
  Learning Breast Cancer Risk Models," arXiv:2606.26431 (2026, MIDL under
  review). **The feared duplicate — verified real and confirmed NOT to cover
  BAC.** It clusters Mirai patch embeddings into phenotypes of dense tissue,
  microcalcifications, and clip/shortcut artifacts; no arterial/vascular
  phenotype.
- Klaneček et al., "Using Explainable AI to Characterize Features in the Mirai
  Mammographic Breast Cancer Risk Prediction Model," *Radiology: AI* (2025),
  DOI 10.1148/ryai.240417. Finds Mirai leans on *lesion* microcalcifications and
  masses — explicitly not arterial calcification.
- Bui et al., "Detection and quantification of breast arterial calcifications on
  mammograms: a deep learning approach," *European Radiology* (2023),
  DOI 10.1007/s00330-023-09668-z (PMC10511622). Automated BAC length/area — but
  exclusively for cardiovascular risk, never linked to a cancer-risk model.

**2. Delta.** No prior work tests whether Mirai's cancer-risk score encodes a
BAC/vascular-age signal, nor erases a BAC concept direction from frozen Mirai
embeddings to check independence from density and chronological age.

**3. Why not done.** `BLIND_SPOT`. Mirai-explainability converged on the
expected signals (density, lesion calcifications, age); the BAC-DL community
treats BAC purely as a cardiovascular endpoint. Caveat lowering the ceiling:
epidemiology holds BAC is *not* a breast-cancer risk factor, so the likely
answer is null — which makes this a valuable confound/shortcut audit, with a
*positive* result being the surprising, high-value outcome.

**4. Verdict.** `NOVEL_VERIFIED`. The single load-bearing check — that
arXiv:2606.26431 does not already isolate BAC in Mirai — was performed and
cleared. Pre-register that a null (Mirai ignores BAC) is itself informative.

---

## C3 — Merlin may be reading fatty kidney rather than kidney shape
**Track: baseline (Mode B)**

**1. Neighbors.**
- Białek et al., "Opportunistic Detection of CKD Using CT-Based Measurements of
  Kidney Volume and Perirenal Fat," *J. Clin. Med.* (2025),
  DOI 10.3390/jcm14165888 (PMID 40869714; PMC12387138). Closest on the
  *question*: tests kidney volume, visceral fat, renal-hilum/sinus fat, and
  perirenal fat against CKD — and finds renal *sinus* fat does **not** survive
  multivariate adjustment (volume + perirenal fat do). Hand-crafted, not
  embeddings.
- Aali, Johnston, Blankemeier, Van Veen et al., "Automated detection of
  underdiagnosed medical conditions via opportunistic imaging,"
  arXiv:2409.11686 (2024). Closest on the *model* (Merlin lab, opportunistic CT
  representations) but targets sarcopenia/steatosis/ascites, no CKD, no erasure.
- "Renal sinus fat is associated with intrarenal hemodynamic abnormalities
  independent of visceral fat in patients with CKD," *Nutr Metab Cardiovasc Dis*
  (2024), PMID 38555192 (companion: Foster et al., *BMC Nephrol* 2011,
  DOI 10.1186/1471-2369-12-52). Supplies the biomarker rationale; no ML.

**2. Delta.** No external work erases a renal-sinus-fat concept direction from
frozen Merlin embeddings to test whether its CKD score depends on that fat
independently of kidney volume and visceral fat — prior art does the
disentanglement on hand-crafted measurements or applies Merlin-family
embeddings to non-CKD conditions.

**3. Why not done.** `BLIND_SPOT` (with a NEW_CAPABILITY enabler: closed-form
concept erasure such as LEACE, arXiv:2306.03819, only recently pairs with a 3D
CT foundation model). The Merlin paper reports CKD AUROC but never audits its
internal features.

**4. Verdict.** `NOVEL_UNVERIFIED`. Downgraded from verified because (a) Białek
2025 already answers the underlying clinical disentanglement and finds renal
*sinus* fat is **not** independently predictive once perirenal fat/volume are
included — undercutting the hypothesis's payoff; (b) the Merlin-lab follow-on
full text could not be fully excluded; and (c) methodological novelty is low —
this is the same erasure template as internal scout-006-c03 on a new organ.
Recommendation: reframe toward *perirenal* fat / kidney volume (the actually
independent predictors), or position as a representation-level replication of
Białek's negative sinus-fat finding.

---

## C4 — The PE model may read contrast flowing backward as a pressure gauge
**Track: baseline (Mode C)**

**1. Neighbors.**
- Bailis et al., "Contrast reflux into the inferior vena cava on CT pulmonary
  angiography is a predictor of 24-hour and 30-day mortality in acute PE,"
  *Acta Radiologica* (2021), DOI 10.1177/0284185120912506. Establishes reflux as
  a validated human-read back-pressure/prognostic sign; no ML.
- Colak et al., "The RSNA Pulmonary Embolism CT Dataset," *Radiology: AI*
  (2021), DOI 10.1148/ryai.2021200254 (defines the RV/LV≥1 strain label), with
  downstream RV-strain DL (e.g., *Emergency Radiology* 2025,
  DOI 10.1007/s10140-025-02404-8) attributing performance to RV/LV geometry, not
  reflux.
- Concept-erasure on frozen medical embeddings — "Sparse Concept Channels in
  Frozen 3D CT Vision Encoders," arXiv:2607.20993; joint-subspace concept
  removal, arXiv:2310.11991. The machinery, never pointed at reflux in a PE
  model (PE interpretability to date is saliency/attention only).

**2. Delta.** No prior work operationalizes IVC/hepatic-vein reflux burden as a
named concept direction and erases it from frozen PE-model embeddings to
causally test whether an RV-strain predictor exploits hydraulic back-pressure —
the clinical, model, and method literatures do not intersect.

**3. Why not done.** `BLIND_SPOT`. DL RV-strain work frames the signal as
ventricular geometry, so no one hypothesized reflux as the model's cue; the
erasure tooling matured independently. A minor NEW_CAPABILITY element applies.

**4. Verdict.** `NOVEL_VERIFIED`. Every component returned hits; the combination
returned none. The remaining caveat is feasibility, not novelty — reflux
quantification (X) is not native to RSNA-STR and must be derived.

---

## C5 — A lung-cancer model may be reading a mechanically remodeled trachea
**Track: baseline (Mode C)**

**1. Neighbors.**
- "Auditing Sybil: Explaining Deep Lung Cancer Risk Prediction Through
  Generative Interventional Attributions (S(H)NAP)," arXiv:2602.02560 (2026).
  The only work auditing Sybil's *non-nodule* signals; finds background/artifact
  cues (bone-density age, ECG electrodes, gown snaps, goiters) but does **not**
  examine trachea, airway remodeling, or COPD structure, and uses generative
  attribution, not embedding erasure.
- Gallardo Estrella / Pompe et al., "CT quantification of tracheal abnormalities
  in COPD and their influence on airflow limitation," *Med Phys* 44(7):3594–3603
  (2017), PMCID PMC6052793. The candidate's automated minimum-tracheal-index /
  saber-sheath method; QCT biomarker, no deep model.
- "Sparse Concept Channels in Frozen 3D CT Vision Encoders," arXiv:2607.20993
  (2026). Closest on method — causal channel ablation of a concept in frozen
  chest-CT embeddings — but targets a VLM for finding-detection, not Sybil, not
  a tracheal confound.

**2. Delta.** No prior work tests whether Sybil's score carries a specific
saber-sheath / minimum-tracheal-index direction, nor removes such a direction
from frozen Sybil embeddings on NLST; existing audits stop at nodules/generic
artifacts and tracheal-index work never touches cancer-risk models.

**3. Why not done.** `BLIND_SPOT` (sliver of NEW_CAPABILITY). The audit
literature framed Sybil as nodule-plus-coarse-artifact, so a structured
airway-geometry confound was never hypothesized; concept erasure on frozen 3D-CT
embeddings is freshly available.

**4. Verdict.** `NOVEL_VERIFIED`. Caveat: S(H)NAP (arXiv:2602.02560) is very
recent and actively probing Sybil's non-nodule signals — confirm its
camera-ready version excludes tracheal analysis before any priority claim.

---

## W1 — The effusion model may be reading whether pleural fluid still obeys gravity
**Track: wide (capillarity / hydrostatics)**

**1. Neighbors.**
- "Interpreting CT-Scans with CLIP: An Explorative Study of Attribution Methods
  for 3D Vision-Language Models," Springer LNCS (2025),
  DOI 10.1007/978-3-032-05479-1_10. Probes CT-CLIP with attribution methods and
  shows spatially localized effusion signals — but does not decompose the score
  into gravity-conforming shape vs volume, and uses no concept erasure.
- Jungblut et al., "Automated Detection, Segmentation, and Classification of
  Pleural Effusion From CT," *Investigative Radiology* (2022), PMCID PMC9390225,
  DOI 10.1097/RLI.0000000000000869. The candidate's own segmenter; uses shape
  radiomics + loculation angle to split simple vs complex fluid, but explicitly
  does not model gravity-conforming sheet/meniscus geometry and does not probe a
  foundation model.
- Hamamci et al. (CT-RATE / CT-CLIP), arXiv:2403.17834 (2024). The audited
  target; reports an effusion score with no analysis of its geometric substrate.

**2. Delta.** No prior work isolates whether CT-CLIP's effusion score is driven
by gravity-conforming free-fluid geometry rather than total fluid volume, via
concept-direction erasure on frozen embeddings with volume held fixed.

**3. Why not done.** `BLIND_SPOT`. The effusion-shape literature treats geometry
as an etiology classifier, not as a shortcut concept inside a foundation model;
the CT-CLIP interpretability literature tests localization but not
volume-controlled concept isolation. Segmenter and erasure tooling both already
exist, so it is not NEW_CAPABILITY-blocked.

**4. Verdict.** `NOVEL_UNVERIFIED`. The specific test is unclaimed, but each
component is precedented (targeted composition, not new primitive), and the
supporting evidence rests on abstract/summary-level reads: the Springer paper
(N1) was paywalled and Jungblut (N2) was read via PMC extraction. Confirm
against full texts — if N2's loculation/shape features already predict the
CT-CLIP score, this becomes `INCREMENTAL`.

---

## W2 — The fibrosis model may be counting holes at the pleural edge
**Track: wide (algebraic topology / fracture mechanics)**

**1. Neighbors.**
- Tanabe et al., "A homological approach to a mathematical definition of
  pulmonary fibrosis and emphysema on CT," *J. Appl. Physiol.* (2021),
  DOI 10.1152/japplphysiol.00150.2021 (PMID 34138650). Uses persistent homology
  (voids/components, birth–death lifetimes) to separate fibrosis from
  emphysema — the exact topological honeycomb-vs-emphysema distinction proposed
  as X, but as a direct voxel classifier, not a probe of a learned model.
- Huber, Nagarajan, Leinsinger, Ray, Wismüller, "Classification of interstitial
  lung disease patterns with topological texture features," *SPIE Medical
  Imaging 2010*, arXiv:1005.5086. Minkowski Functionals / Euler characteristic
  separate honeycombing ROIs; no persistent homology, no subpleural constraint,
  no deep model.
- "Persistent homology of longitudinal CT fibrotic features in COPD," *Eur.
  Respir. J.* early view (Feb 2026) (related: PMC12350597, 2025). Most recent
  PH fibrosis quantification; a hand-built biomarker, not a model probe. (No
  concept-erasure interpretability of CT-CLIP's fibrosis score was found; CT-CLIP
  interpretability to date is saliency-based, e.g. EXACT arXiv:2604.24146.)

**2. Delta.** Prior work builds topological honeycomb biomarkers as standalone
classifiers or applies generic saliency to CT-CLIP; the candidate is first to
use concept-direction erasure on frozen CT-CLIP embeddings with a topological
honeycomb summary as the causal probe to test topology vs generic peripheral
texture.

**3. Why not done.** `NEW_CAPABILITY`. CT-CLIP (2024) only recently exposed
usable frozen embeddings at scale, and concept-erasure tooling matured in the
diffusion/CLIP-safety literature (2024–2026) without being ported to 3D CT
models; the topological-fibrosis biomarker and the interpretability method lived
in separate literatures.

**4. Verdict.** `NOVEL_UNVERIFIED`. Each component is well-precedented (Tanabe
supplies the exact feature; erasure is mature), so this is a method-transfer with
`INCREMENTAL` risk if the erasure result is negative; and the Feb-2026 ERJ paper
could not be read in full (403). Recommend a full-text check of the ERJ 2026
paper and a scan of 2026 CT-CLIP interpretability preprints before a priority
claim.

---

## W3 — The PE model may be reading how completely blood and contrast have mixed
**Track: wide (tracer transport / fluid mixing)**

**1. Neighbors.**
- Oliveros et al., "Novel CT Angiography Parameter Is Associated with Low
  Cardiac Index in CTEPH," *J. Cardiovasc. Dev. Dis.* 11(9):281 (2024),
  DOI 10.3390/jcdd11090281. Closest: a contrast-dispersion metric (MPA−LA/LV
  HU gradient) as a surrogate for low cardiac index — same mixing∝flow intuition,
  but an *inter-chamber gradient*, not *intraluminal* HU heterogeneity, and a
  human-read biomarker.
- Chaturvedi et al., "Contrast opacification on thoracic CT angiography:
  challenges and solutions," *Insights Imaging* (2017),
  DOI 10.1007/s13244-016-0524-3 (PMID 27858323). Qualitative review of the
  mixing↔low-output phenomenon; no quantitative intraluminal metric, no ML.
- Colak et al., "The RSNA Pulmonary Embolism CT Dataset," *Radiology: AI*
  (2021), DOI 10.1148/ryai.2021200254. The model substrate; downstream challenge
  models (DOI 10.1148/ryai.2021210068) offer only Grad-CAM/attention, no concept
  erasure and no contrast-mixing analysis.

**2. Delta.** No prior work computes intraluminal pulmonary-artery contrast-mixing
heterogeneity (normalized HU CoV / entropy / autocorrelation, emboli-excluded,
mean-normalized) and erases it from frozen PE-model embeddings to test whether
the strain head exploits a transient low-flow signal — prior art uses
inter-chamber gradients or qualitative reads.

**3. Why not done.** `BLIND_SPOT` (with NEW_CAPABILITY enabler). The
mixing↔low-output phenomenon is clinically known and heterogeneity/entropy
metrics are mature elsewhere, but framing intraluminal mixing as a *spurious
concept a strain model might latch onto* has not been posed; frozen-embedding
concept erasure has only recently matured.

**4. Verdict.** `NOVEL_UNVERIFIED`. The combination is unclaimed but rests on an
unproven premise: the closest neighbor (Oliveros) validates only the
*inter-chamber gradient* form of mixing∝output, not the *intraluminal*
heterogeneity form the candidate needs. Pre-register that the intraluminal signal
exists and is emboli/mean-enhancement-robust before claiming the erasure result.
Distinct from sibling C4 (retrograde IVC reflux vs forward arterial mixing).

---

## Summary table

| Candidate | Track | Verdict | Why-not-done |
|---|---|---|---|
| C1 — knee-pain / subchondral trabecular texture | baseline (A) | NOVEL_VERIFIED | BLIND_SPOT |
| C2 — Mirai / breast arterial calcification | baseline (B) | NOVEL_VERIFIED | BLIND_SPOT |
| C3 — Merlin / renal sinus fat | baseline (B) | NOVEL_UNVERIFIED | BLIND_SPOT (+NEW_CAPABILITY) |
| C4 — PE model / IVC contrast reflux | baseline (C) | NOVEL_VERIFIED | BLIND_SPOT |
| C5 — Sybil / saber-sheath trachea | baseline (C) | NOVEL_VERIFIED | BLIND_SPOT |
| W1 — CT-CLIP effusion / gravity conformity | wide | NOVEL_UNVERIFIED | BLIND_SPOT |
| W2 — CT-CLIP fibrosis / honeycomb topology | wide | NOVEL_UNVERIFIED | NEW_CAPABILITY |
| W3 — PE model / contrast mixing entropy | wide | NOVEL_UNVERIFIED | BLIND_SPOT (+NEW_CAPABILITY) |

**Audit notes.** No candidate was found to duplicate a prior work
(`DUPLICATE_PRIOR`), so none is recommended for a novelty kill. The strongest
provenance caution is C3: an already-published clinical study (Białek 2025)
finds the candidate's target signal — renal *sinus* fat — is not independently
predictive of CKD, which undercuts the hypothesis's payoff even though the
representation-level test is unclaimed. Three `NOVEL_UNVERIFIED` verdicts (W1,
W2, C3) turn on full-text access that was blocked or summary-level during the
audit; the flagged full texts should be dereferenced before priority is
asserted. All eight verdicts rest on the absence of a located duplicate and are
flags for human verification, not evidence of novelty; every candidate remains
pre-keystone, so novelty here does not by itself justify advancement.
