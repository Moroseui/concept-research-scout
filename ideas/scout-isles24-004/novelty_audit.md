# Novelty audit — scouting cycle isles24-004

## C1 — The ground truth remembers the algorithm that drafted it (baseline)

1. **Neighbors.** (i) de la Rosa et al., “DeepISLES: a clinically validated ischemic stroke segmentation model from the ISLES’22 challenge,” *Nature Communications* (2025), DOI `10.1038/s41467-025-62373-x`: describes and validates the public ensemble used to initialize ISLES’24 masks, but does not audit imprint in the later benchmark. (ii) Liao et al., “Modeling annotator preference and stochastic annotation error for medical image segmentation,” *Medical Image Analysis* 92 (2024) 103028, DOI `10.1016/j.media.2023.103028`: models human annotator preference and error, not machine-draft inheritance. (iii) Chlebus et al., “Rethinking Generalization: The Impact of Annotation Style on Medical Image Segmentation,” MELBA (2022), arXiv `2210.17398`: shows models learn annotation styles across datasets, without a recoverable AI-preannotation draft.
2. **Delta.** Re-run the named initializer on the released follow-up images, measure draft survival in the official labels, and test whether an acute-CT model sides with the draft specifically where the released mask disagrees.
3. **Why not done.** `NEW_CAPABILITY` — the 2026 public ISLES’24 release now pairs follow-up DWI/ADC and finalized masks with a runnable DeepISLES container and weights, making the latent draft approximately recoverable.
4. **Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — searches spanning the dataset/method, annotation-bias, annotation-style, and AI-assisted-labeling literatures found close components but no draft-recovery/imprint audit; version mismatch remains a scientific limitation.

## C2 — Does the model bring a vascular map to the scan? (baseline)

1. **Neighbors.** (i) Liu et al., “Digital 3D Brain MRI Arterial Territories Atlas,” *Scientific Data* 10 (2023), DOI `10.1038/s41597-022-01923-0`: releases the lesion-derived hierarchical vascular-territory atlas proposed as the measurement instrument. (ii) de la Rosa et al., “DeepISLES,” *Nature Communications* (2025), DOI `10.1038/s41467-025-62373-x`: maps predicted lesions to atlas territories to score territory identification, but does not test whether the model uses territory boundaries. (iii) Robben et al., “Prediction of final infarct volume from native CT perfusion and treatment parameters using deep learning,” *Medical Image Analysis* 59 (2020) 101589, DOI `10.1016/j.media.2019.101589`: predicts final infarct from native CTP and metadata without auditing an emergent anatomical prior.
2. **Delta.** Estimate a placebo-tested prediction discontinuity at externally registered arterial borders among voxels matched on local acute evidence; prior work either supplies the atlas, evaluates territorial correctness, or predicts infarct without this use test.
3. **Why not done.** `NEW_CAPABILITY` — the public deformable arterial atlas plus ISLES’24’s co-registered multimodal acute evidence makes a border-discontinuity audit practical.
4. **Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — targeted multi-source searches found deliberate territory use and territory-level evaluation, but no emergent-prior audit using boundary discontinuities.

## C3 — The heart’s signature in the head scan (baseline)

1. **Neighbors.** (i) Robben et al., “Prediction of final infarct volume from native CT perfusion and treatment parameters using deep learning,” *Medical Image Analysis* 59 (2020) 101589, DOI `10.1016/j.media.2019.101589`: demonstrates deconvolution-free prediction from native CTP, but does not isolate global arrival time. (ii) Winder et al., “Predicting the tissue outcome of acute ischemic stroke from acute 4D computed tomography perfusion imaging using temporal features and deep learning,” *Medical Image Analysis* 82 (2022) 102610, PMID `36408399`: compares learned temporal representations from source and residue curves, without a global time-shift intervention. (iii) “Contrast bolus timing in CT-angiography and CT-perfusion: insights from a large clinical dataset,” *European Radiology Experimental* (2025), PMCID `PMC12125062`: in 1,843 cases links CTP bolus timing to age and ejection fraction, but studies acquisition adequacy rather than downstream model use.
2. **Delta.** Apply a full-bolus-preserving within-case time translation and sham controls to ask whether a native-CTP final-infarct model uses absolute systemic arrival time rather than only local curve relationships.
3. **Why not done.** `NEW_CAPABILITY` — ISLES’24 publicly releases uniformly resampled 4D CTP with follow-up infarct masks, enabling controlled time-axis interventions on a benchmark cohort.
4. **Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — native-CTP models and bolus-timing physiology are established, but the searched literature contained no causal model-use audit of absolute arrival time.

## C4 — The model may be watching the patient’s eyes (baseline)

1. **Neighbors.** (i) Simon et al., “Bringing Prevost’s sign into the third dimension: Artificial intelligence estimation of conjugate gaze adjusted length (CGAL) and correlation with acute ischemic stroke,” *Medicine* 99 (2020), PMCID `PMC7717852`: automatically measures 3D gaze on CT and relates it to stroke and NIHSS. (ii) McKean et al., “Visual Determination of Conjugate Eye Deviation on Computed Tomography Scan Predicts Diagnosis of Stroke Code Patients,” *Journal of Stroke and Cerebrovascular Diseases* (2016), DOI `10.1016/j.jstrokecerebrovasdis.2016.07.039`: establishes CT-visible eye deviation as a diagnostic/NIHSS-correlated sign. (iii) “Using a Deep Learning-Based Decision Support System to Predict Emergent Large Vessel Occlusion Using Non-Contrast Computed Tomography,” *Journal of Clinical Medicine* (2025), PMCID `PMC12250463`: explicitly detects crystalline-lens eye deviation and includes it as a feature in an NCCT ELVO model.
2. **Delta.** The candidate intervenes on gaze alone to test causal use by a final-infarct segmentation model; the closest work already uses gaze in a stroke deep-learning system, so task and intervention—not the core cue—are the delta.
3. **Why not done.** `BLIND_SPOT` — interpretability studies rarely perturb extracranial bedside signs in tissue-outcome models, although gaze itself has already crossed into stroke AI.
4. **Verdict.** `INCREMENTAL` — the candidate’s causal intervention is useful, but “a stroke model watches the eyes” is already substantially realized by the ELVO system and cannot support a broad novelty claim.

## C5 — The brain’s odometer: calcification as the model’s age gauge (baseline)

1. **Neighbors.** (i) Yalcin et al., “Age and gender related prevalence of intracranial calcifications in CT imaging; data from 12,000 healthy subjects,” *Journal of Chemical Neuroanatomy* 78 (2016), DOI `10.1016/j.jchemneu.2016.07.008`: quantifies age-related pineal, choroid-plexus, habenular, dural, basal-ganglia, and vascular calcifications. (ii) Kıroğlu et al., “Intracranial physiological calcifications evaluated with cone beam CT,” *Dentomaxillofacial Radiology* 41 (2012), PMCID `PMC3528191`: measures the distribution and morphology of physiologic calcifications across ages. (iii) Whitehead et al., “Physiologic Pineal Region, Choroid Plexus, and Dural Calcifications in the First Decade of Life,” *AJNR* 36 (2015), PMCID `PMC8013049`: shows calcification prevalence increases with age even in children.
2. **Delta.** Use graded, remote calcification edits and matched bright-voxel shams to test whether a final-infarct model uses these deposits; all located neighbors establish the age-linked measurement, not downstream model use.
3. **Why not done.** `BLIND_SPOT` — physiologic calcification is treated as an incidental radiology finding, while shortcut-learning audits usually probe explicit demographics or global image features rather than this manipulable proxy.
4. **Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH` — no use-test duplicate was found, but the very broad demographic-shortcut literature and sparse indexing of structure-specific attribution make high confidence unjustified.

## C6 — The scan remembers which hospital took it (wide)

1. **Neighbors.** (i) Kharboutly et al., “CT-Scanner Identification Based on Sensor Noise Analysis,” EUVIP (2014), HAL `lirmm-01379581`: extracts wavelet–Wiener noise residuals and identifies individual CT scanners. (ii) Kharboutly et al., “Computed Tomography Image Origin Identification Based on Original Sensor Pattern Noise and 3-D Image Reconstruction Algorithm Footprints,” *IEEE Journal of Biomedical and Health Informatics* (2017), PMID `27295695`: identifies 15 CT models from four manufacturers with at least 94% detection. (iii) Biondetti et al., “Name that manufacturer: Relating image acquisition bias with task complexity when training deep learning models: experiments on head CT,” MIDL (2020), arXiv `2008.08525`: shows CNNs learn head-CT manufacturer and that this bias affects classification and segmentation.
2. **Delta.** Spectrally transplant only the measured residual toward the other site and require a site-classifier flip plus matched-energy sham, directly testing whether a stroke outcome model uses that channel rather than merely detecting site or suffering domain shift.
3. **Why not done.** `BLIND_SPOT` — CT forensics isolates device fingerprints while medical-imaging bias work measures aggregate domain effects; the two literatures have not joined in a downstream use intervention.
4. **Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — searches covered forensic residual extraction, manufacturer classification, and scanner-domain effects; no residual-only downstream model intervention was located.

## C7 — The edge of the map: the benchmark scores terra incognita (wide)

1. **Neighbors.** (i) Christensen and Lansberg, “CT perfusion in acute stroke: Practical guidance for implementation in clinical practice,” *Journal of Cerebral Blood Flow & Metabolism* 39 (2019), DOI `10.1177/0271678X18805590`: explains detector-limited 4–16 cm z-coverage and recommends at least 8 cm because limited coverage misses ischemia. (ii) Ouyang et al., “Whole brain CT perfusion in acute anterior circulation ischemia: coverage size matters,” *Neuroradiology* 56 (2014), DOI `10.1007/s00234-014-1429-9`, PMID `25228451`: quantifies ischemic-volume underestimation at reduced coverage. (iii) “Optimal brain perfusion CT coverage in patients with acute middle cerebral artery stroke,” *AJNR* 31 (2010) 691–695, exact article URL `https://www.ajnr.org/content/31/4/691`: estimates the z-coverage needed to characterize MCA ischemia.
2. **Delta.** Measure follow-up ground-truth mass outside each released case’s acute CTP support and propagate that missing support through the official benchmark metrics; the neighbors study clinical acquisition coverage, not benchmark target observability.
3. **Why not done.** `NEW_CAPABILITY` — ISLES’24 newly exposes acute CTP/maps, whole-brain companion imaging, registered follow-up masks, and official evaluation code together.
4. **Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — multiple clinical coverage and infarct-underestimation searches found no public-benchmark overflow census or sensor-respecting performance ceiling.

## C8 — The ground truth was drawn on a swollen brain (wide)

1. **Neighbors.** (i) Harston et al., “Prediction of final infarct volume on subacute MRI by quantifying cerebral edema in ischemic stroke,” *Journal of Cerebral Blood Flow & Metabolism* 38 (2018), PMCID `PMC5536812`: shows day-5 lesion volume overestimates later infarct volume and corrects edema using displaced CSF. (ii) Harston et al., “Quantifying Infarct Growth and Secondary Injury Volumes: Comparing Multimodal Image Registration Measures,” *Stroke* 49 (2018), PMCID `PMC6023577`: compares linear and nonlinear registration and quantifies anatomical distortion from edema. (iii) Brett et al., “Spatial Normalization of Brain Images with Focal Lesions Using Cost Function Masking,” *NeuroImage* 14 (2001), DOI `10.1006/nimg.2001.0845`: establishes lesion cost-function masking to reduce registration distortion.
2. **Delta.** Audit the released ISLES’24 label geometry with acute-CSF “impossible voxels,” quantify official-metric sensitivity, and then test inheritance by trained models; neighbors establish edema/registration error but do not audit a benchmark or downstream model reproduction.
3. **Why not done.** `NEW_CAPABILITY` — ISLES’24 now releases acute NCCT, 2–9-day DWI-derived masks in NCCT space, and documented affine transfer, enabling a case-level physical-impossibility audit.
4. **Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — searches across edema correction, multimodal registration, lesion masking, final-infarct prediction, and ISLES’24 found no equivalent benchmark-label audit.

| Candidate | Verdict | Why-not-done code |
|---|---|---|
| C1 | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C2 | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C3 | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C4 | INCREMENTAL | BLIND_SPOT |
| C5 | NO_DUPLICATE_FOUND_LIMITED_SEARCH | BLIND_SPOT |
| C6 | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C7 | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C8 | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
