# Novelty audit — cycle 019

Audited 2026-08-25. Method: five parallel web-search sweeps (Google web search
plus Crossref/PubMed/arXiv fetches), one per candidate, each running 7–14
distinct queries; every neighbor below was located by search in this audit,
not recalled. Full query log and establishing passages are in
`novelty_manifest.json`. Candidates are numbered C1..C5 by their position in
`candidates_all.json` (all one track this cycle).

---

## C1 — Name the vessel-tree phenotype inside retinal sex prediction (baseline)

**1. Neighbors.**

- Kim et al., "Effects of Hypertension, Diabetes, and Smoking on Age and Sex
  Prediction from Retinal Fundus Images," *Scientific Reports* 2020, DOI
  10.1038/s41598-020-61519-9 — inpainted-out (a) the fovea and (b) the entire
  retinal vasculature from fundus images and measured the sex-prediction AUC
  drop on a trained classifier: 0.881 fovea-erased vs **0.682
  vessel-erased**, directly establishing that the classifier uses the
  vessels. **This paper is not cited in the candidate card.**
- Delavari et al., "Artificial intelligence as a gateway to scientific
  discovery: Uncovering features in retinal fundus images," arXiv:2301.06675
  (published PNAS Nexus 2(9):pgad290, 2023) — measured sex differences in the
  vessel graph (males: more branches, more nodes, greater total branch
  length); observational, no intervention on a classifier.
- Kim & Jang, "Quantifying regional contributions to sex classification from
  fundus photographs via a two-stage attention-based deep learning approach,"
  *Scientific Reports* 2026, DOI 10.1038/s41598-026-53485-5 — attention-based
  estimation of macula/disc/vasculature regional contribution weights; the
  DOI cited in the card is real (verified via Crossref; full text
  paywalled) and the card's characterization is consistent with the title.

**2. Delta.** Over Kim et al. 2020 the candidate adds branch-SELECTIVE,
vessel-area-matched, sham-controlled graded erasure (distal/terminal branches
vs proximal-segment and non-vessel curvilinear shams), dissociating branch
richness from total vessel area — but the coarse claim "the classifier uses
the vessels" is already published, so the open question is only the
richness-vs-area refinement, and the card's framing of "the missing
experiment is whether a frozen classifier uses the vessels" overstates the
gap.

**3. Why not done.** `BLIND_SPOT` — the interpretability arm of the
sex-prediction literature stopped at coarse whole-structure ablation (fovea
vs all vessels), while the vessel-graph sex differences were measured only
observationally in a separate line of work; nobody combined graph-level
selectivity with the ablation design because each community framed the
question at its own granularity.

**4. Verdict.** `INCREMENTAL` — Kim et al. 2020 is a partial duplicate of the
rung-1 claim (vessel erasure changes sex prediction, effect size already
published). The branch-richness-at-matched-area dissociation genuinely
survives as unclaimed, but the card must be rewritten to cite Kim 2020, and
its interest/regret scores were computed against a mystery that is
one-third solved. Not a kill; a mandatory reframing before shortlisting.

---

## C2 — The spleen as the fatty-liver model's calibration patch (baseline)

**1. Neighbors.**

- Blankemeier et al., "Merlin: a computed tomography vision-language
  foundation model and dataset," *Nature* 2026, DOI 10.1038/s41586-026-10181-8,
  PMID 41781626 (also arXiv 2406.06512) — the target model itself; includes a
  latent-shift counterfactual analysis (splenomegaly example) validating
  imaging features qualitatively, but no input-space organ-HU perturbation
  and nothing on steatosis or a liver-spleen rule. Weights confirmed publicly
  released (GitHub/HF StanfordMIMI, MIT license).
- "Sparse Concept Channels in Frozen 3D CT Vision Encoders," arXiv
  2607.20993 (2026) — ablates internal encoder channels of frozen Merlin (and
  Pillar-0) to collapse individual finding scores; representation-space only,
  no input perturbation, no steatosis/liver-spleen question.
- Pickhardt et al., "Liver Steatosis Categorization on Contrast-Enhanced CT
  Using a Fully Automated Deep Learning Volumetric Segmentation Tool," AJR
  2021, DOI 10.2214/AJR.20.24415 — deep-learning segmentation feeding a
  hand-coded liver-spleen difference/ratio rule; the spleen reference is
  engineered in by design, not tested as an emergent learned feature.
  (Supporting: occlusion-sensitivity splenomegaly work, PMID 36428569; Park
  et al. Radiology 2011, DOI 10.1148/radiol.10101233, verified as the
  biopsy-anchored liver-minus-spleen reference range 1–18 HU.)

**2. Delta.** No published study perturbs spleen-only voxel attenuation (or
any organ-specific HU dose) of a frozen whole-volume model to test for an
emergent internal-reference rule; the closest works either ablate latent
channels, generate latent-space counterfactuals without controlled HU doses,
or build the spleen reference in explicitly.

**3. Why not done.** `NEW_CAPABILITY` — a frozen, publicly released,
whole-volume abdominal CT foundation model with a findings vocabulary
(Merlin, weights released with the 2026 Nature publication) is the asset that
only recently made an emergent-reference-rule test possible; before it there
was no obtainable black-box whose steatosis behavior could be interrogated.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — thorough multi-source
search; neighbors found and clearly distinguished. Side-findings for the
keystone: the steatosis vocabulary claim is supported indirectly (the CT-IDP
benchmark, arXiv 2605.09002, evaluates hepatic steatosis on the Merlin test
set) but the released finding/prompt vocabulary itself remains uninspected,
so `NOT_INSPECTED` stands correctly.

---

## C3 — The azygos vein inside the edema score (baseline)

**1. Neighbors.**

- "RoentMod: A Synthetic Chest X-Ray Modification Model to Identify and
  Correct Image Interpretation Model Shortcuts," arXiv:2509.08640 (npj
  Digital Medicine 2026, DOI 10.1038/s41746-026-02497-6) — counterfactual CXR
  editing that inserts/removes specified pathology and measures paired
  classifier response; edits pathology appearance, not a named vessel.
- "Segmentor-Guided Counterfactual Fine-Tuning for Locally Coherent and
  Targeted Image Synthesis," MICCAI 2025, DOI 10.1007/978-3-032-04937-7_50
  (arXiv:2509.24913) — structure-specific graded counterfactual edits on CXR
  anatomy (lung areas, heart area) on PadChest; the methodological analogue,
  but never applied to the azygos or any mediastinal vein.
- "Automated, Standardized, Quantitative Analysis of Cardiovascular Borders
  on Chest X-Rays Using Deep Learning," JACC: Advances 2025, DOI
  10.1016/j.jacadv.2025.101687 — automated delineation and width measurement
  of individual cardiovascular/mediastinal borders on CXR; the closest thing
  to an automated mediastinal-venous localizer, but does not isolate the
  azygos arch.

**2. Delta.** No study attributes an edema/CHF classifier's output to the
azygos arch (or performs any azygos-specific edit); the candidate combines
two separately established components — structure-targeted counterfactual
editing and automated mediastinal-border measurement — into a
vessel-specific, bidirectional, sham-controlled attribution experiment that
has no direct precedent.

**3. Why not done.** `BLIND_SPOT` — the quantitative azygos-width literature
is pre-digital (Preger et al., *Radiology* 1969, DOI 10.1148/93.3.521, PMID
4898452: azygos width vs central venous pressure, r≈0.8; Keats et al.
*Radiology* 1968, DOI 10.1148/90.5.990: normal arch mensuration), while
modern CXR interpretability concentrated on lung opacity and the cardiac
silhouette; the sign fell between classic mensuration radiology and deep
learning XAI, and no automated azygos localizer was ever built.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — neighbors found and
distinguished. Audit resolves two of the card's open items: the primary
quantitative azygos-congestion citation is now pinned (Preger 1969); the
automated-localizer claim is UNSUPPORTED — none exists, so the localizer
must be built or adapted, consistent with the card's already-low
feasibility score of 2.

---

## C4 — The meniscus inside the pleural-effusion score (baseline)

**1. Neighbors.**

- Sexauer et al., "Automated Detection, Segmentation, and Classification of
  Pleural Effusion From Computed Tomography Scans Using Machine Learning,"
  *Investigative Radiology* 2022;57(8):552-559, DOI
  10.1097/RLI.0000000000000869, PMID 35797580, PMCID PMC9390225 — nnU-Net
  effusion segmentation plus simple-vs-complex classification; shape
  radiomics were computed but largely NOT selected as informative; external
  validation on NLST and PleThora, not CT-RATE.
- "Explaining 3D Computed Tomography Classifiers with Counterfactuals,"
  arXiv:2502.07156 (2025) — latent-shift counterfactuals for 3D chest-CT
  classifiers including pleural effusion; counterfactuals reduce fluid
  amount itself — volume is not preserved.
- "COGENT: Counterfactual Gaussian Explanations for Volumetric Medical
  Images," arXiv:2608.11422 — counterfactual optimization over 3D Gaussian
  scene parameters against a frozen predictor (Sybil); general volumetric
  probing, no fixed-volume interface-geometry control.

**2. Delta.** No prior work edits fluid (or lesion) shape at fixed volume —
preserving voxel count, attenuation histogram, and pleural contact while
varying only meniscus curvature — to probe a classifier; existing
counterfactual methods co-vary amount and shape, so the volume/shape
dissociation is unclaimed.

**3. Why not done.** `BLIND_SPOT` — counterfactual-explanation methods
operate in latent or parametric spaces where fluid amount and interface
shape cannot be held apart, and the effusion-segmentation literature treated
shape as a passive radiomic feature (and found it uninformative for its own
task); the fixed-volume free-surface control comes from a physics framing
outside standard XAI practice.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — with one mandatory
correction: **the card's citation is wrong.** PMID 35923880 is a plant
circadian-clock paper, and the author is Sexauer, not "Ebert." The correct
anchor is PMID 35797580 / PMCID PMC9390225 (the PMCID in the card was
right). Additionally, that segmenter was validated on NLST/PleThora, so the
CT-RATE-transfer claim is untested by any cited work — correctly listed as
unverified, but the Stage-0 gate should treat transfer as unestablished
rather than probable.

---

## C5 — The opening in the diaphragm inside the hiatal-hernia score (baseline)

**1. Neighbors.**

- Ouyang et al., "Multiplanar MDCT measurement of esophageal hiatus surface
  area: association with hiatal hernia and GERD," *Surgical Endoscopy*
  2016;30:2465-2472, DOI 10.1007/s00464-015-4499-9, PMID 26304104 — first
  in-vivo CT hiatal-surface-area quantification via manual double-oblique MPR
  tracing (hernia 6.9 vs control 2.5 cm², p<0.0001). This pins the card's
  requested primary measurement citation.
- "CT oesophageal hiatal surface area measurements: An objective and
  sensitive means of hiatal hernia detection," *Surgery in Practice and
  Science* 2023, DOI 10.1016/j.sipas.2023.100162 — validated HSA (computed
  from crural length and intercrural distance, cut-off ≥3.5 cm²; sensitivity
  94.6%); measurement still manual (radiologist MPR, ICC 1.00).
- "EXACT: an explainable anomaly-aware vision foundation model,"
  arXiv:2604.24146 (2026) — benchmarks CT-CLIP on the hiatal-hernia label
  (AUROC 0.66 on RAD-ChestCT) and notes its alignment objective preserves
  fine-grained spatial structure poorly for focal pathologies; generic
  benchmark/XAI, no anatomical attribution. (Supporting: IISE 2024
  LIME-on-CXR hernia classifier — generic saliency only.)

**2. Delta.** No work attributes any hernia classifier's score to crural
separation versus herniated-sac volume, and none uses within-patient
longitudinal discordance between the two as the attribution instrument; the
nearest neighbors are manual surgical morphometry on one side and generic
saliency on the other, never combined.

**3. Why not done.** `BLIND_SPOT` — quantitative hiatus morphometry lives in
the surgical-planning literature as a manual MPR tracing, and the model-
interpretability community never crossed that disciplinary boundary; no
automated crural/hiatus segmentation tool exists to make the crossing cheap.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — neighbors found and
distinguished. Feasibility flag confirmed and sharpened: the search found NO
published automatic diaphragmatic-crus or esophageal-hiatus segmentation
model (TotalSegmentator's class lists include esophagus and diaphragm-
adjacent structures but not the crura), so the card's measurement arm must
be built and validated de novo — the `NOT_INSPECTED` keystone cap is
correct and the crural-segmentation gate is the likely kill point. Also
noteworthy for design: CT-CLIP's hiatal-hernia head is reported weak (AUROC
0.66 on RAD-ChestCT per EXACT), which bears on whether there is enough
signal to attribute.

---

## Summary

| Candidate | Verdict | Why-not-done |
|---|---|---|
| C1 — Name the vessel-tree phenotype inside retinal sex prediction | INCREMENTAL (Kim 2020, DOI 10.1038/s41598-020-61519-9, already erased vessels wholesale; branch-richness delta survives but card needs reframing) | BLIND_SPOT |
| C2 — The spleen as the fatty-liver model's calibration patch | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C3 — The azygos vein inside the edema score | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C4 — The meniscus inside the pleural-effusion score | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE (citation error in card: PMID 35923880 wrong → PMID 35797580, Sexauer et al.) | BLIND_SPOT |
| C5 — The opening in the diaphragm inside the hiatal-hernia score | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE (no automated crural segmenter exists; measurement arm de novo) | BLIND_SPOT |

Absence of a found duplicate is not verified novelty; all verdicts above are
search-bounded to the queries recorded in `novelty_manifest.json`.
