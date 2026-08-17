# Novelty audit — cycle 015

Audited 2026-08-17. Method: five parallel search passes (one per candidate), each
running 7–11 distinct web searches across arXiv, PubMed/PMC, RSNA/Radiology
journals, Springer/ScienceDirect, Nature, PLOS, and Google-indexed scholarly
pages, with establishing passages taken from fetched pages where access allowed
and from search-engine abstracts otherwise (access level recorded per neighbor
in `novelty_manifest.json`). The two most load-bearing newly surfaced
identifiers (arXiv:2602.02560; PMID 41728282) were independently re-verified by
direct search before this file was written. Absence of a found duplicate is not
verified novelty; verdicts use the calibrated vocabulary.

---

## C1 — Measure the fluid behind the pleural-effusion score (scout-015-c01, baseline)

**1. Neighbors.**

- DOI 10.1148/ryai.240215 — "Accuracy of Fully Automated and Human-assisted
  AI-based CT Quantification of Pleural Effusion Changes after Thoracentesis,"
  *Radiology: Artificial Intelligence* 2025. Segments and quantifies pleural
  effusion volume change on pre/post-thoracentesis CT against drained-fluid
  volume as reference. Segmentation-based volumetry — no classifier score
  involved.
- arXiv:2510.03856 — "AI-Assisted Pleural Effusion Volume Estimation from
  Contrast-Enhanced CT Images," 2025. Semi-supervised segmentation framework
  (TTAS) estimating effusion volume via masks, benchmarked against nnU-Net.
- DOI 10.1186/s12880-022-00827-0 (PMID 35624426) — "Deep transfer learning to
  quantify pleural effusion severity in chest X-rays," *BMC Medical Imaging*
  2022. Ordinal 4-category severity grading on radiographs, not CT, not a
  score-versus-measured-volume regression.

Asset check performed during search: TotalSegmentator's
`pleural_pericard_effusion` task was confirmed to exist by fetching the
repository's `class_details.md` ("run task pleural_pericard_effusion and
subtract the resulting pleural effusion segmentation") — the candidate's
X-measurement tool is real, though its licensing/validation status still needs
the card's planned inspection.

**2. Delta.** No found work regresses a foundation-model abnormality score
against automatically measured effusion volume — the neighbors either measure
volume directly by segmentation or grade discrete severity — so treating
CT-CLIP's effusion score as a decoding target for a continuous physical
quantity, within-patient and longitudinally, is a genuine (not weak) delta.

**3. Why not done.** `NEW_CAPABILITY` — the score side (CT-CLIP/CT-RATE,
arXiv:2403.17834, 2024) and the annotation-free volume side (TotalSegmentator's
pleural-effusion task) only recently exist together; nobody has combined them
to ask whether the score encodes volume.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — 11 queries across
arXiv/PMC/RSNA/BMC/GitHub; neighbors found and distinguished. Caveat: the RSNA
and BMC establishing passages are search-summary level (paywall/403), recorded
as such in the manifest.

---

## C2 — The missing branches inside Sybil's risk score (scout-015-c02, baseline)

**1. Neighbors.**

- arXiv:2602.02560 — "Auditing Sybil: Explaining Deep Lung Cancer Risk
  Prediction Through Generative Interventional Attributions," ICML 2026
  (existence and venue independently re-verified). First interventional audit
  of Sybil: 3D diffusion-bridge counterfactuals add/remove pulmonary nodules
  and decompose the risk score via nodule-level attributions; finds
  radiologist-like malignant/benign discrimination plus failure modes
  (sensitivity to ECG-lead/metal artifacts, a radial spatial bias). Does not
  probe internal feature subspaces and does not examine airways.
- PMID 28886252 — "Total Airway Count on Computed Tomography and the Risk of
  COPD Progression," *Am J Respir Crit Care Med* 2018 (with method detail in
  PMC8225550). Defines TAC by automated branch-point counting and validates
  branch count as a smoking-injury CT biomarker — the exact quantity the
  candidate wants to decode, never connected to a risk model's representation.
- DOI 10.1148/radiol.11110542 — "Quantitative CT Assessment of Emphysema and
  Airways in Relation to Lung Cancer Risk," *Radiology* 2011. Associates
  hand-measured CT airway/emphysema metrics with lung-cancer risk — the
  correlational ancestor of the candidate's question, without any learned
  model in the loop.

Method neighbor noted: INLP/LEACE linear concept erasure (Ravfogel et al.;
Belrose et al.) is mature and off-the-shelf but was not found applied to any
LDCT risk model. Supporting feasibility neighbor: DOI 10.1148/ryct.210311 shows
deep-learning airway detection recovers ~90% of airways on low-dose CT, so
branch count is extractable from NLST-type scans.

**2. Delta.** The closest neighbor (Auditing Sybil) interrogates Sybil through
nodule-level generative counterfactuals in image space; this candidate instead
decodes and erases an airway-branch-count subspace in Sybil's frozen feature
space with matched random and emphysema-subspace controls — a different
mechanism target (airway morphology, not nodules) and a different instrument
(concept erasure, not image editing).

**3. Why not done.** `BLIND_SPOT` — disciplinary boundary: the airway-count
community (TAC/COPDGene) works in radiomics/epidemiology and does not probe
learned representations; Sybil interpretability, which only began in 2026, went
the clinically framed nodule-counterfactual route; concept-erasure methods live
mostly in NLP. All ingredients are independently available.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — 8 multi-source queries;
the Sybil-interpretability space is now occupied but the specific
airway-concept probing/erasure question is not. The card's framing must be
updated: it can no longer imply Sybil is uninterrogated, and Auditing Sybil's
found artifact sensitivities are directly relevant context for any erasure
readout.

---

## C3 — The portal vein as the cirrhosis model's pressure gauge (scout-015-c03, baseline)

**1. Neighbors.**

- arXiv:2406.06512 (PMC11230513; Nature 2026) — Merlin itself. Beyond
  providing the target model, the authors already run counterfactual
  interpretability (Latent Shift) on Merlin's outputs: "the size of the spleen
  is reduced in the counterfactual relative to the original image, adding
  credence to the validity of imaging features used for classification." The
  genre "which anatomic feature drives Merlin's output, tested by
  counterfactual" is therefore already opened by the model's own paper.
- DOI 10.1007/s00330-025-12010-4 — "Deep-learning-based prediction of
  significant portal hypertension with single cross-sectional non-enhanced
  CT," *European Radiology* 2025. Trains CNNs on portal-vein-centered regions
  (umbilical portion, first right branch, splenoportal confluence, spleen) to
  predict HVPG-defined CSPH — the portal vein as model input is established;
  what a foundation model's cirrhosis head uses is not.
- PMC10591114 — CounterSynth, "Equitable modelling of brain imaging by
  counterfactual augmentation with morphologically constrained 3D deep
  generative models," *Medical Image Analysis* 2023. Diffeomorphic,
  label-driven, biologically plausible 3D morphological counterfactuals — the
  candidate's edit mechanism, existing in brain MRI, not applied to abdominal
  vessel calibre.

Premise-relevant finding (independently re-verified): "Portal Vein Diameter on
Routine Clinical CT: Establishing Normals and Disease Associations," medRxiv
2026, PMID 41728282, PMC12919146 (20,225 CTs). PV diameter is associated with
prevalent portal hypertension (OR 1.18/mm) and incident varices, but shows
**weak to no association with invasively measured hepatic venous pressures**.
The candidate's card already claims only "model uses calibre," not "calibre
measures pressure," but the "pressure gauge" title framing and part of the
medical-relevance case are weakened by this primary evidence.

**2. Delta.** Relative to Merlin's own Latent Shift analysis, the candidate
substitutes an anatomy-specific, sham-controlled diffeomorphic calibre edit
with a monotonic dose-response readout for a global latent-space shift — a
real methodological tightening and a new anatomic target, but the same
question-genre on the same model; the delta is honest-but-modest.

**3. Why not done.** `BLIND_SPOT` — the intersection (vessel-specific
diffeomorphic counterfactuals × foundation-model cirrhosis head) is
unexploited despite all components being released; a contributing reason may
be that the 2026 pressure-correlation evidence makes the headline hypothesis
look likely-negative, which reduces publication incentive.

**4. Verdict.** `INCREMENTAL` — no duplicate found (8 queries, four neighbor
strands), but the closest neighbor is the target model's own counterfactual
interpretability section, and the pressure-gauge premise is weakened by
verified primary evidence. If pursued, the card should drop the manometer
framing, cite PMID 41728282, and justify why the tighter edit instrument earns
the study beyond Latent Shift.

---

## C4 — The continuous air tunnel inside the hiatal-hernia score (scout-015-c04, baseline)

**1. Neighbors.**

- ScienceDirect S2667008923000071 (with Surg Endosc 2016, PMID 26304104) — CT
  esophageal hiatal surface area measurement for hiatal-hernia detection
  (~81% sensitivity / 88% specificity at 3.5 cm²). Closest automated CT
  quantification of the clinical object; keys on hiatal aperture size, not gas
  topology.
- DOI 10.1148/radiol.2021210198 — "Spatial Dependence of CT Emphysema...
  Join-Count Statistics," *Radiology* 2021 (with the low-attenuation-cluster
  literature). Connected low-attenuation-voxel topology as a chest-CT
  biomarker — the nearest precedent for gas connected-component analysis,
  applied to parenchyma, never to the trans-diaphragmatic air column.
  (Related strand: persistent-homology/Betti-number priors, arXiv:1901.10244.)
- arXiv:2312.14223 (ECCV 2024) — "Fast Diffusion-Based Counterfactuals for
  Shortcut Removal and Generation." Counterfactual editing with self-optimized
  masking to add/remove a suspected shortcut while holding the rest of the
  image fixed — the candidate's method family, targeting appearance/label
  shortcuts on 2D modalities, not a topology-defined cue on 3D CT.

Also checked: CT-CLIP's own paper (arXiv:2403.17834) contains no head-level
interpretability for hiatal hernia; a deep-learning hiatal-hernia detector
exists on chest radiographs with LIME saliency (ResearchGate 378770178) but
not on CT and not topology-targeted.

**2. Delta.** No found work operationalizes trans-diaphragmatic gas-column
continuity as a measurement or tests any classifier against it; the
equal-volume displaced-gas control — isolating topology from gas volume — is
the specific move none of the neighbors makes.

**3. Why not done.** `NEW_CAPABILITY` — a promptable 3D chest-CT model with a
hiatal-hernia head (CT-CLIP, 2024) and mask-constrained counterfactual editing
methods (2024) only recently coexist; the gap between hernia detection,
gas-topology biomarkers, and counterfactual probing had no occupant before.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — 8 multi-source queries
covering all four strands; several establishing passages are abstract/search
-summary level behind paywalls (recorded in manifest), but the strands bracket
the idea tightly and the intersection is empty. Mode C caps on the card remain
appropriate; the editor-feasibility keystone is untouched by this audit.

---

## C5 — The lung-opacity score may be reading gravity (scout-015-c05, baseline)

**1. Neighbors.**

- Nature *Scientific Reports* s41598-024-72786-1 (2024) — lung attenuation
  gradients along the gravity axis compared between supine (conventional) and
  standing (upright CT) in healthy participants; the most direct quantitative
  primary for the candidate's X (HU gradient along gravity). (Classic
  physiology primary in the same strand: Petersson et al., *J Appl Physiol*
  2009, PMID 19589959, supine/prone regional density with constant lung
  shape; quantitative dependent-opacity HU ranges in PMC2713983.)
- PMC12707796 — "Opacity in ground glass: remember the gravity-dependent
  atelectasis" (2025). Documents gravity-dependent dorsal atelectasis mimicking
  ground-glass opacity as a standing human interpretive pitfall — exactly the
  confusion the candidate proposes to test as a machine shortcut; no model is
  tested.
- arXiv:2209.09844 — "Frequency Dropout: Feature-Level Regularization via
  Randomized Filtering" (with the shortcut-learning survey literature,
  arXiv:2403.06748). Establishes that medical-imaging CNNs preferentially
  exploit easy low-level/frequency-band cues and builds generic
  frequency-based defenses — but never a designed, physics-motivated gravity
  ramp, and never on a 3D CT opacity score.

**2. Delta.** The three strands — quantified gravitational density gradients,
gravity-dependent opacity as a diagnostic mimic, and low-frequency shortcut
exploitation — have never been combined into a causal perturbation of a chest
-CT classifier; injecting zero-mean, lung-confined gradient ramps with
reversed-axis and equal-energy controls against a named opacity score is a
genuine, well-controlled delta, not a dataset swap.

**3. Why not done.** `NEW_CAPABILITY` — an open, queryable 3D chest-CT
foundation model with an opacity head (CT-CLIP/CT-RATE, 2024) is the recent
enabling asset; shortcut-probing tooling predates it but was applied to 2D
radiographs and acquisition artifacts, not 3D physical gradients.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — 7 multi-source queries
across physiology, radiology, and ML-shortcut literatures; neighbors found and
distinguished in all strands. Access caveat for the card (not the verdict):
the two most direct human gradient quantifications (Petersson 2009; SciRep
2024) were reachable only at title/abstract level here, so the card's
"primary quantitative range for normal dependent HU gradients" remains an
unverified claim to be inspected at Stage 0, as the card already states.

---

## Summary

| # | Candidate | Verdict | Why-not-done |
|---|---|---|---|
| C1 | scout-015-c01 — Measure the fluid behind the pleural-effusion score | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C2 | scout-015-c02 — The missing branches inside Sybil's risk score | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C3 | scout-015-c03 — The portal vein as the cirrhosis model's pressure gauge | INCREMENTAL | BLIND_SPOT |
| C4 | scout-015-c04 — The continuous air tunnel inside the hiatal-hernia score | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C5 | scout-015-c05 — The lung-opacity score may be reading gravity | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |

Cross-cutting notes for the orchestrator: (1) C2's card framing needs revision
to acknowledge arXiv:2602.02560 before any shortlist decision — the audit found
no duplicate, but the "Sybil is unexamined" implication is now false. (2) C3's
INCREMENTAL verdict rests on two verified facts (Merlin's own Latent Shift
interpretability; PMID 41728282's weak PV-diameter/HVPG correlation) and is a
recommendation to reframe or deprioritize, not an outright kill. (3) All
establishing-passage access levels are recorded in `novelty_manifest.json`;
paywalled passages are search-summary paraphrases and should be re-verified
against full text before any of these citations becomes load-bearing in a
feasibility memo.
