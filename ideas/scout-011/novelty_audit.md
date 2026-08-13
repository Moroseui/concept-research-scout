# Novelty audit — cycle 011

Audited 2026-08-13. Method: five parallel search passes (one per candidate),
each running 9–13 distinct queries across general web, PubMed-scoped, and
arXiv-scoped search, with full-text or abstract fetches where accessible.
Reproducibility record in `novelty_manifest.json`. Candidates numbered C1–C5
by position in `candidates_all.json` (single baseline track).

Calibration note: several key neighbors were paywalled (RoentMod npj version,
Radiology full texts, Merlin Nature supplement), so their establishing
passages rest on abstracts or search summaries. Verdicts are downgraded to
LIMITED_SEARCH wherever a load-bearing neighbor could not be read in primary
form.

---

## C1 — Name the bone phenotype hidden in a near-perfect hand-radiograph sex classifier (baseline)

**1. Neighbors.**

- **Yune et al., J Digit Imaging 2019, DOI 10.1007/s10278-018-0148-x (PMID
  30478479, PMC6646498).** The target paper itself and the closest anchor:
  CNN sex classification from hand radiographs at 95.9% vs radiologists at
  46–58%; CAMs localize to the 2nd/3rd metacarpal base, thumb sesamoid, and
  distal radioulnar structures; radiologists reviewing 70 cases "could not
  find any patterns that distinguish the two sexes." Stops at CAM
  localization; quantifies no deterministic bone measurement.
- **RoentMod, npj Digital Medicine 2026, DOI 10.1038/s41746-026-02497-6
  (arXiv:2509.08640).** Generative counterfactual editor for chest
  radiographs that inserts/removes user-specified pathology while preserving
  anatomy, used to expose and correct shortcut reliance in interpretation
  models. Method-class neighbor (targeted edits probing model reliance) —
  but 2D chest, pathology-presence edits, no bone metrics, no sex classifier.
- **"Sex Differentiation of Trabecular Bone Structure Based on Textural
  Analysis of Pelvic Radiographs," J Clin Med 2024;13(7):1904 (MDPI).**
  Sex determination from trabecular texture parameters on 343 pelvic
  radiographs. Establishes trabecular-texture sex dimorphism as a
  direct-measurement task, but pelvis not metacarpal, and no probe of a
  trained classifier's reliance.

Supporting context: the metacarpal cortical index / radiogrammetry literature
(e.g., PMID 11997884) confirms sex differences in second-metacarpal cortical
thickness — the proposed X is a real, established sex-dimorphic quantity.

**2. Delta.** No prior work connects the Yune classifier (or any hand-radiograph
sex classifier) to named deterministic bone measurements via
measurement-targeted edits with sham controls; the classifier+CAM work, the
cortical/trabecular measurement literatures, and the counterfactual-editing
toolchain exist in three separate communities and have never been joined.

**3. Why not done.** `BLIND_SPOT` — the interpretability community stopped at
saliency and treats radiograph sex signal as a shortcut to *remove* rather
than a mechanism to *decode*, while the radiogrammetry/anthropology community
quantifies sex-dimorphic bone measures with hand-crafted statistics and never
probes a black-box model. (Secondary enabler: RoentMod-class
anatomy-preserving editing is recent, but the core measurements and the
classifier have both existed since 2019 — the gap is framing, not tooling.)

**4. Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH`. Eleven queries across
general web, PubMed, and arXiv; neighbors found and distinguished; no work
found testing classifier reliance on cortical proportion or trabecular
anisotropy. Downgraded from high confidence because two of three neighbors
(RoentMod, MDPI pelvic texture) were paywalled/403 and rest on search
summaries, and recent 2025–2026 hand-radiograph explainability preprints were
not exhaustively canvassed.

---

## C2 — Does Merlin read renal atrophy when it predicts future CKD? (baseline)

**1. Neighbors.**

- **"Opportunistic Detection of Chronic Kidney Disease Using CT-Based
  Measurements of Kidney Volume and Perirenal Fat," J Clin Med 2025, DOI
  10.3390/jcm14165888 (PMC12387138), full text read.** TotalSegmentator
  kidney volumes + perirenal fat thickness in 237 patients; two-variable
  logistic regression detects prevalent CKD (eGFR<60) at test AUC 0.894
  (kidney volume OR 0.249). Explicit-morphology CKD detection —
  cross-sectional, classical, no foundation model, no attribution.
- **"Association of quantitative renal surface nodularity with the renal
  dysfunction progression in patients with arterial hypertension," BMC Med
  Imaging 2025, DOI 10.1186/s12880-025-01995-5, full text read.** Automated
  pipeline (segmentation → edge extraction → surface-curve fitting) computing
  three CT surface-roughness metrics in 242 patients; RSN independently
  predicts ≥25% eGFR decline/RRT (HR 5.22) after adjusting for eGFR and renal
  volume. Exactly the automated surface-irregularity metric class C2
  proposes — never connected to any deep model's prediction.
- **Blankemeier et al., "Merlin: a computed tomography vision–language
  foundation model and dataset," Nature 2026, DOI 10.1038/s41586-026-10181-8
  (arXiv:2406.06512), article text read.** Defines the 5-year six-disease
  prediction task including CKD (mean AUROC ~0.757 fine-tuned); benchmarks
  performance across sites/architectures but contains no saliency, probing,
  mediation, or feature attribution for the CKD head in the retrieved text.

Runner-up: "Changes in CT-Based Morphological Features of the Kidney with
Declining GFR in CKD," Diagnostics 2023, DOI 10.3390/diagnostics13030402 —
pyRadiomics kidney shape features vs eGFR; surface-area-to-volume ratio the
strongest correlate.

**2. Delta.** Prior work establishes both halves separately — measured renal
morphology predicts CKD/eGFR decline, and Merlin predicts 5-year CKD — but no
work asks whether Merlin's learned CKD output is *driven by* that measured
morphology; the within-patient longitudinal mediation design is absent from
both literatures.

**3. Why not done.** `NEW_CAPABILITY` — the released Merlin weights with
five-year disease heads (StanfordMIMI, Nature 2026) only recently made a
third-party mechanism audit possible, and TotalSegmentator makes bilateral
kidney volumetry/surface metrics automatic. Secondary blind spot: the
foundation-model literature's evaluation culture is AUROC-table-oriented,
and nephro-imaging interpretability effort has gone to tabular/EHR models.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE`. Eleven queries across
four source classes; all three neighbors read in full text; targeted
Merlin+attribution queries returned nothing closer than generic
linear-probing papers. Residual caveat, noted not scored: the Nature
supplement was not inspected, so a buried saliency figure in Merlin's
supplementary material cannot be fully excluded.

---

## C3 — Cephalization in 3D: decode CT-CLIP's pulmonary-edema score (baseline)

**1. Neighbors.**

- **Cajigas et al., Pulmonary Circulation 2023, DOI 10.1002/pul2.12321
  (PMC10719487), full text read.** Automated CT pulmonary vascular volume
  distribution by vessel caliber (BV5, BV10%, fractal dimension) as a
  vascular-remodeling biomarker, in the Rahaghi BV5 lineage; small-vessel
  volumes also reduced in PH due to left heart disease. Distribution is by
  vessel *size* only — no cranial/caudal or upper/lower regional axis, and
  no link to any learned model's output.
- **Horng, Liao et al., "Deep Learning to Quantify Pulmonary Edema in Chest
  Radiographs," Radiology: AI 2021 (arXiv:2008.05975), abstract.** Models on
  369,071 MIMIC-CXR radiographs grade edema severity on a 4-level ordinal
  scale (level 1 = vascular congestion) at AUC up to 0.99. No analysis of
  which radiographic features (cephalization, redistribution) the models use.
- **Seah et al., "Chest Radiographs in Congestive Heart Failure: Visualizing
  Neural Network Learning," Radiology 2019, search summary.** The closest
  attempt to decode which anatomical features a CHF imaging model uses:
  GAN-based generative visual rationales on CXR found cardiomegaly (75%) and
  pleural effusions (23.5%) — cephalization/vascular redistribution not
  identified, 2D pixel-space counterfactuals, no vessel segmentation or
  volume-preserving intervention.

**2. Delta.** No prior work combines regional (upper/lower) vessel-volume
distribution measurement with a causal probe of any CT model's edema score;
the caliber-based BV5 literature never used a spatial axis, and the CXR
counterfactual work never isolated vessels as a variable.

**3. Why not done.** `NEW_CAPABILITY` — CT-CLIP/CT-RATE public weights (2024)
provided the first open chest-CT model with an interrogable edema head, and
automatic lung-vessel segmentation at scale (TotalSegmentator lung_vessels,
PARSE 2022) made region- and caliber-stratified vessel volume feasible
without manual tracking.

**Scientific risk flag (record for revision/critique):** retrieved physiology
literature (upright-vs-supine CT, Sci Rep 2024, DOI 10.1038/s41598-024-72786-1
lineage) states the upright craniocaudal perfusion gradient is largely
abolished supine and replaced by a ventrodorsal gradient. This is plausibly
*why* nobody quantified an upper/lower vessel ratio on supine CT — and it
means the candidate's primary axis may be wrong: an anterior–posterior
redistribution axis must be considered as the leading alternative
operationalization, not a footnote. This weakens the "obvious in hindsight"
regret framing and should be addressed before any design freeze.

**4. Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH`. Twelve queries, one
full-text neighbor; PubMed and RSNA fetches were cookie/403-blocked, so two
neighbors rest on abstracts/secondary summaries, and recent MICCAI/SPIE
workshop probing of CT-CLIP could sit below search visibility.

---

## C4 — The air bronchogram as a topological cue (baseline)

**1. Neighbors.**

- **RoentMod, npj Digital Medicine 2026, DOI 10.1038/s41746-026-02497-6
  (arXiv:2509.08640), abstract/search summary.** Counterfactual pathology
  editing of chest radiographs to reveal shortcut reliance in multi-task and
  foundation classifiers; counterfactual-augmented training improved
  specificity. Closest methodological neighbor — but 2D CXR, edits pathology
  *presence*, never airway topology inside opacity, never CT.
- **"The value of the air bronchogram sign on CT image in the identification
  of different solitary pulmonary consolidation lesions," Medicine
  (Baltimore) 2018, search summary (paywalled).** Manual measurement of
  involved-bronchus length, lesion length, and their ratio within
  consolidation to distinguish cancer/TB/pneumonia. Closest *metric*
  neighbor — a manual analogue of the proposed centerline-per-opacity burden,
  for human diagnosis, with no automation and no model-facing component.
- **ATM'22 airway benchmark, Medical Image Analysis 2023, DOI
  10.1016/j.media.2023.102957 (arXiv:2303.05745), abstract.** Public
  500-CT airway-segmentation benchmark explicitly including COVID-19 CTs
  with GGO/consolidation; topological-continuity-enhanced methods performed
  best. Establishes the enabling asset (airway segmentation inside opacity);
  purely a segmentation benchmark.

**2. Delta.** No prior work computes an automatic air-bronchogram burden
(airway centerline ∩ opacity mask) or tests any trained model's consolidation
output against connected-airway topology with burden-matched counterfactuals;
the sign has been measured only manually and the editing toolchain only
applied to CXR pathology presence.

**3. Why not done.** `NEW_CAPABILITY` — the co-existence of (a) an open 3D
chest-CT model with a consolidation head (CT-CLIP, 2024) and (b) airway
segmentation reliable inside consolidation (ATM'22 2023; Garcia-Uceda 2021)
is recent; before both existed the probe could not be built. Secondary blind
spot: interpretability work treats consolidation as a monolithic opacity
label and has not decomposed it into constituent radiologic sub-signs.

**4. Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH`. Ten searches plus
verification fetches across all three sub-areas; no duplicate found; both
most on-point neighbors (RoentMod, Medicine 2018) were paywalled so their
non-overlap could not be verified against full text (RoentMod supplements in
particular could not be checked for CT experiments).

---

## C5 — A pancreatic fat gauge inside Merlin's diabetes forecast (baseline)

**1. Neighbors.**

- **Tallam et al., "Fully Automated Abdominal CT Biomarkers for Type 2
  Diabetes Using Deep Learning," Radiology 2022, DOI 10.1148/radiol.211914,
  search summary (403 on full text).** Automated pancreas segmentation with
  attenuation, volume, intrapancreatic fat, and fractal dimension across
  8,992 patients; "the best predictors... included intrapancreatic fat
  percentage, pancreatic fractal dimension, ... average liver CT
  attenuation, and body mass index." Already predicts diabetes from
  automated pancreas CT features with pancreatic fat as the top-ranked
  predictor.
- **"CT Quantitation and Prediction of the Risk of Type 2 Diabetes Mellitus
  in Non-Obese Patients with Pancreatic Fatty Infiltration," DMSO 2024,
  PMID 38974951 (PMC11226987), full text read.** Pancreas-to-spleen
  attenuation ratio stratifies T2DM risk (ORs 3.98–12.94 across strata) —
  directly validates the exact P/S HU measure the candidate proposes,
  cross-sectionally.
- **"Assessing the Reliability of Pancreatic CT Imaging Biomarkers for
  Diabetes Prediction: A Dual Center Retrospective Study," Academic
  Radiology 2025, S1076-6332(25)00191-6, abstract.** Pancreatic
  attenuation/fat-fraction/fractal/volume biomarkers computed via three
  automated segmenters *including TotalSegmentator*, tested for robustness
  in diabetes prediction — the candidate's exact mask source, already used
  for this substrate.

Runner-up: arXiv:2511.10484, pancreas surface lobularity as an opportunistic
T2DM CT biomarker.

**2. Delta.** The only new element is attribution: asking whether *Merlin's
learned* five-year diabetes output re-derives the already-established
pancreatic-fat biomarker — the association substrate (automated pancreas CT
features → diabetes, including the P/S ratio and TotalSegmentator masks) is
thoroughly published, so the delta is the foundation-model-decoding step
alone, and it is a narrow one.

**3. Why not done.** `BLIND_SPOT` — the opportunistic-CT/radiomics community
engineers explicit pancreas-fat features and does not probe black-box
embeddings, while the foundation-model group reports aggregate AUROCs and
defers interpretability to "future biomarker discovery"; the released Merlin
weights (NEW_CAPABILITY enabler) only recently made the bridge testable.

**4. Verdict.** `INCREMENTAL`. Not a duplicate — no work attributes a
foundation model's diabetes forecast to pancreatic fat — but the measurement,
the substrate association, the segmentation tool, and even the
diabetes-prediction framing are all published (Tallam 2022 being a strong
near-duplicate that additionally already includes liver-fat and visceral-fat
context, i.e., the candidate's planned controls). A positive result would
confirm a model rediscovered a known biomarker; the candidate's own
`novelty_confidence_info_only` of 2 is consistent with this finding.

---

## Summary table

| # | Candidate | Verdict | Why-not-done |
|---|-----------|---------|--------------|
| C1 | Name the bone phenotype hidden in a near-perfect hand-radiograph sex classifier | NO_DUPLICATE_FOUND_LIMITED_SEARCH | BLIND_SPOT |
| C2 | Does Merlin read renal atrophy when it predicts future CKD? | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C3 | Cephalization in 3D: decode CT-CLIP's pulmonary-edema score | NO_DUPLICATE_FOUND_LIMITED_SEARCH | NEW_CAPABILITY |
| C4 | The air bronchogram as a topological cue | NO_DUPLICATE_FOUND_LIMITED_SEARCH | NEW_CAPABILITY |
| C5 | A pancreatic fat gauge inside Merlin's diabetes forecast | INCREMENTAL | BLIND_SPOT |
