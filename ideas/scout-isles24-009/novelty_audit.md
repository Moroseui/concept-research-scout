# Novelty audit — cycle isles24-009

Charter: isles24. Audited 2026-09-01 by web search (search-summary access;
no full-text retrieval; a PubMed fetch was blocked by a cookie wall and the
record was verified via secondary search instead). Reproducibility record:
`novelty_manifest.json` in this directory. Candidates numbered C1–C3 by
position in `candidates_all.json`.

Method note: every identifier the candidates cite as a novelty neighbor was
re-resolved by search rather than trusted. Two citation defects were found
and are flagged inline; neither changes a novelty verdict, but both should
be corrected before the cards advance.

---

## C1 — The keystone patients: ten cases may teach the model the reversal (wide)

### 1. Neighbors

1. **Park et al., "TRAK: Attributing Model Behavior at Scale," ICML 2023,
   arXiv 2303.14186** (verified; the card's OpenReview ID resolves to the
   same paper). Scalable training-data attribution via random projections of
   a linearized model; validated counterfactually on ImageNet classifiers,
   CLIP, and language models. Attributes generic predictions, not a
   physiological response, and contains no medical imaging.
2. **"Data Attribution for Segmentation Models," NeurIPS 2023 submission,
   OpenReview forum 13VkFDTKHH** (verified; the PDF blob in the card,
   e15a148b35fbb56da1af7d88c7c66add68615a6a, is this submission's PDF).
   Defines attributable behaviors for segmentation models, computes
   attributions efficiently, and validates by curation: a 50% MS COCO subset
   raised mIOU by 2.79% ± 0.49%. Closest methodological neighbor; natural
   images, generic mIOU-level behavior, no patient-level deletion design.
3. **Tang et al., "Data valuation for medical imaging using Shapley value
   and application to a large-scale chest X-ray dataset," Scientific
   Reports 2021, DOI 10.1038/s41598-021-87762-2, PMID 33863957**
   (audit-found; not in the card). The medical-imaging precedent for the
   deletion logic: removing high-Shapley training data degraded pneumonia
   detection and removing low-Shapley data improved it. Classification, not
   segmentation; value defined against aggregate accuracy, not a named
   within-patient physiological response.

Additional searches (influence functions + medical segmentation; training
data attribution + stroke) surfaced only generic influence-function
methodology and stroke-segmentation surveys; no stroke- or ISLES-specific
example-level attribution study was found.

### 2. Delta

The closest neighbor attributes and curates against aggregate segmentation
quality on natural images; C1 attributes a specific, pre-registered
within-patient physiological response (the frozen band-3-minus-band-2
contrast inherited from ideas 023/046) to individual training patients and
then tests the attribution causally by matched-deletion retraining against
an already-ratified head-dominated finite-population census — the target
behavior, the matched-control deletion design, and the census anchor are
all absent from prior work, so the delta is more than "a different
dataset," though the attribution machinery itself is imported unchanged.

### 3. Why not done

`NEW_CAPABILITY` — three assets only recently coexist: TRAK-class scalable
attribution (2023), the ISLES'24 release of registered acute perfusion
maps with follow-up-derived lesion masks (2024, Zenodo 16813698), and the
ratified idea-046 contribution census (2026-09) that supplies a frozen,
surprising target behavior worth attributing. The card's claim matches the
audit's finding.

### 4. Verdict

**NO_DUPLICATE_FOUND_HIGH_CONFIDENCE.** Multi-source search across the
attribution-methods, segmentation-attribution, medical data-valuation, and
stroke-segmentation literatures found the three neighbors above and
distinguished each; no work attributes a stroke model's physiological
response to training patients or validates by matched patient deletion.
The internal anchor (the 046 census) additionally makes an exact external
duplicate impossible; the generic-question search still stands behind the
verdict.

---

## C2 — The model's hidden disability map (wide)

### 1. Neighbors

1. **Ding et al., "Lesion Network Mapping for Neurological Deficit in Acute
   Ischemic Stroke," Annals of Neurology 2023;94(3):572–584, DOI
   10.1002/ana.26721, PMID 37314250** (verified — with a correction: the
   card attributes this paper to "Salvalaggio et al."; the PMID, title,
   venue, and 7,807-patient cohort check out, but the first author is Ding.
   Fix the attribution before advancing). Voxel-based lesion-symptom plus
   functional/structural disconnection mapping of NIHSS deficits; maps
   consequences of observed lesions, never model behavior.
2. **Kuceyeski et al., "Structural connectome disruption at baseline
   predicts 6-months post-stroke outcome," Human Brain Mapping 2016, DOI
   10.1002/hbm.23198, PMID 27016287** (verified; 40 patients, NeMo tool).
   Predicts functional outcomes from baseline disconnection — association,
   not model-use.
3. **"Connectomic stroke lesion measures provide no benefit over basic
   spatial lesion features in the prognosis of global stroke outcome
   measures," Brain Communications 2025;7(4):fcaf268** (verified; 21
   connectomic measures vs simple spatial features). Establishes that for
   global outcomes the network layer adds no predictive signal — which
   sharpens rather than duplicates C2: it concerns predictive benefit, not
   whether a trained forecaster's representation carries and uses the prior.
4. **Audit-found addition — "Both Infarcted and Noninfarcted Brain Regions
   Contribute to Deep Learning-Based MRI Prediction of Acute Stroke
   Outcome," AJNR 2025, PMID 41198223.** The nearest model-use-adjacent
   work: contribution analysis of a deep outcome-prediction model showing
   noninfarcted regions carry predictive signal (full-brain input AUC 0.86
   vs 0.68 for infarct volume). Still an outcome model (not an
   infarct-mask forecaster), still attribution rather than a
   representation-level intervention, and eloquence/network impact is never
   the named variable. The card should add this neighbor.

Concept-erasure searches (linear adversarial concept erasure and successors)
found no application of subspace erasure to a medical segmentation model's
clinically meaningful concept.

### 2. Delta

All found prior work predicts symptoms or outcomes *from* observed lesions
or attributes an outcome model's inputs; C2 asks whether a pre-treatment
infarct forecaster's representation *encodes and uses* normative
functional-network impact, tested by selective linear erasure with
preservation gates rather than by any input-outcome association — a
question-type delta (model-use vs consequence-mapping), not a data delta.

### 3. Why not done

`BLIND_SPOT` — confirmed as framed by the card and reinforced by the
audit: stroke connectomics studies what lesions do to networks (and its
2025 null suggests the field is concluding the layer adds little
predictive value), while the infarct-forecasting literature evaluates
accuracy against masks; neither asks whether the forecaster imports a
disability prior. The AJNR 2025 paper shows the field beginning to probe
region-level contributions, making the specific eloquence question timely
rather than taken.

### 4. Verdict

**NO_DUPLICATE_FOUND_LIMITED_SEARCH.** Neighbors were found and
distinguished, but the adjacent literatures (lesion network mapping,
stroke XAI, concept erasure) are each large and only their intersections
were searched; the AJNR 2025 paper surfacing mid-audit shows the
model-use-adjacent space is actively moving. Consistent with the card's
own novelty_confidence of 3.

---

## C3 — The atlas prior hidden under the perfusion maps (wide)

### 1. Neighbors

1. **Audit-found, closer than any card citation — Kayhan & van Gemert, "On
   Translation Invariance in CNNs: Convolutional Layers Can Exploit
   Absolute Spatial Location," CVPR 2020, arXiv 2003.07064.** Demonstrates
   that ordinary convolutional layers can read absolute position (via
   boundary effects) and that exploiting or removing this changes behavior
   across detection, segmentation, and generation. This is the strongest
   prior evidence that C3's suspected mechanism exists; it does not test a
   medical model, a longitudinal forecast, or an ambiguity-localized
   prediction. The card should add this neighbor.
2. **Liu et al., "An Intriguing Failing of Convolutional Neural Networks
   and the CoordConv Solution," NeurIPS 2018, arXiv 1807.03247** (verified).
   Shows CNNs struggle to learn coordinate transforms and that explicit
   coordinate channels change behavior; capability-focused, natural
   images/RL, no reliance measurement in a trained clinical model.
3. **Payer et al., "Integrating spatial configuration into heatmap
   regression based CNNs for landmark localization," Medical Image Analysis
   2019, arXiv 1908.00748** (verified — with a correction: the card cites
   "MICCAI 2018, arXiv 1806.08732," which is a different paper; the SCN
   paper is arXiv 1908.00748, MedIA 2019, building on a MICCAI 2016
   version. Fix the identifier before advancing). Adds spatial-configuration
   priors to improve localization — the additive direction C3 inverts.
4. **Jeon et al., "Teaching AI the Anatomy Behind the Scan: Addressing
   Anatomical Flaws in Medical Image Segmentation with Learnable Prior,"
   arXiv 2403.18878** (verified). Learnable anatomical prior deformed to
   patient anatomy to guide segmentation; again additive, not subtractive.

Searches for per-case frame destruction, positional-shortcut evaluation in
lesion segmentation, and lesion-frequency-atlas reliance found no study
that removes the shared anatomical frame during training to measure a
stroke (or any medical) model's dependence on it; the nearest gesture is a
cephalometric ablation replacing anatomical priors with random-position
Gaussians (arXiv 2605.03358 context), which alters an explicit prior
module rather than the training data's coordinate frame.

### 2. Delta

Kayhan & van Gemert prove convolutional models *can* exploit absolute
location; every found medical neighbor *adds* spatial priors to help
segmentation; C3 instead subtracts the shared cross-patient frame from
training data — preserving each case's image-label pairing — in a
longitudinal infarct forecast, with the falsifiable localization
prediction that only evidence-ambiguous voxels should suffer. The
subtractive intervention, the clinical forecasting setting, and the
ambiguity-interaction endpoint are each absent from the neighbors.

### 3. Why not done

`BLIND_SPOT` — confirmed: the vision literature treats absolute-location
use as a property to characterize (Kayhan) or exploit (CoordConv), and the
medical literature treats spatial priors as helpful inductive bias to
inject (Payer, Jeon); nobody frames the shared atlas frame as a potential
source of illusory patient-specificity in a baseline-to-follow-up
forecast, where ISLES'24's task structure makes the distinction
consequential.

### 4. Verdict

**NO_DUPLICATE_FOUND_LIMITED_SEARCH.** Neighbors verified and a closer one
added, and no duplicate of frame-destruction-as-reliance-test surfaced;
but the augmentation/equivariance literature is vast and was searched only
at its intersections with reliance testing and medical segmentation, so a
buried ablation with this logic cannot be excluded. Consistent with the
card's own novelty_confidence of 3.

---

## Observations outside the four items (for the merge/human gate)

- **C2 citation fix:** PMID 37314250 is Ding et al. 2023, not Salvalaggio.
- **C3 citation fix:** the SCN paper is arXiv 1908.00748 (MedIA 2019), not
  arXiv 1806.08732 / MICCAI 2018.
- **Cohort-count version drift, all three cards:** the arXiv HTML of
  2408.10966 reports 150 train / 98 hidden test, while the cards state
  245 patients (149 public / 96 hidden) sourced to DOI 10.1148/ryai.250603.
  The local payload evidence (evidence/decisions.md, 2026-08-25) settles
  the public cohort at 149; the paper-version discrepancy is noted for the
  record, not adjudicated here — it echoes the version-instability pattern
  already on file for CT-Scroll.

## Summary table

| Candidate | Verdict | Why-not-done |
|---|---|---|
| C1 — The keystone patients | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C2 — The model's hidden disability map | NO_DUPLICATE_FOUND_LIMITED_SEARCH | BLIND_SPOT |
| C3 — The atlas prior hidden under the perfusion maps | NO_DUPLICATE_FOUND_LIMITED_SEARCH | BLIND_SPOT |
