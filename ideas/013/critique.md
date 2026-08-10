FATAL OBJECTION: The proposed observational regressions cannot establish that CT-CLIP *uses* or localises coronary calcium; they can only show that its named output is associated with another model's calcium estimate.
EVIDENCE: CHARTER.md rung 1 requires ablation/probing/perturbation/occlusion with controls; the card's Stage 1 and Stage 2 contain none.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION

# Adversarial review

## Bottom line

The question is sharp and the two output names genuinely exist, but the current experiment does not identify the claimed mechanism. The sentence “a monotone dependence on measured Agatston is the model using calcium by definition” is false. Both CT-CLIP and AI-CAC can respond to common causes—age, protocol, cardiac motion, overall atherosclerotic burden, or correlated hyperdensities—without the CT-CLIP score depending on coronary calcium itself. Partial regression does not turn association into use, and a “double dissociation” between two observational regressions is not a localisation experiment.

This is repairable by making the primary estimand an anatomy-specific, within-volume intervention or an especially clean paired-reconstruction contrast. The observational calibration analysis can remain useful secondary evidence.

## Verified facts, interpretations, and inferences

### Verified facts

- CT-RATE contains 25,692 noncontrast chest CT scans from 21,304 patients, expanded to 50,188 volumes through reconstructions; the official release has a held-out validation cohort of 1,304 patients. Official dataset page and Hamamci et al., arXiv:2403.17834; subsequently Nature Biomedical Engineering (2026).
- “Arterial wall calcification” and “Coronary artery wall calcification” are distinct members of the released 18-class taxonomy. This supports the existence of the outputs, not their spatial semantics.
- AI-CAC was developed for full-field, nongated, noncontrast chest CT and releases weights and inference code under MIT. Hagopian et al. trained it from 446 expert segmentations and evaluated it against paired gated studies in 795 patients (DOI: 10.1056/AIoa2400937).
- The released AI-CAC inference path expects folders of DICOM instances, reads axial position and other DICOM information, selects a suitable series, and aggregates slice predictions. The official repository says this explicitly: https://github.com/Raffi-Hagopian/AI-CAC/.
- The CT-RATE release being proposed here is distributed as processed volumes rather than the original per-study DICOM series. Therefore “both measures run today” has not been demonstrated for the actual file format in hand.
- Prior literature independently shows that slice thickness changes automated CAC estimates and risk categorisation; this is not a nuisance that can safely be handled only by adding thickness as a linear covariate. For example, Yin et al. explicitly tested 1, 3, and 5 mm nongated reconstructions (PMID: 39144022), and van Velzen et al. validated automated calcium scoring across multiple protocols (DOI: 10.1148/radiol.2020191621).

### Source-supported interpretation

AI-CAC is a credible independent *measurement model*, but it is not ground truth on CT-RATE. In its primary publication, agreement of nongated AI-CAC with gated report categories was 68.6% with weighted kappa 0.72, while agreement with manual nongated segmentation on the smaller tuning set was 82.4% with kappa 0.81. That is useful performance, but it leaves substantial measurement error and domain-transfer uncertainty.

### Inference

The two CT-CLIP scores may largely reproduce two report-extraction conventions rather than two anatomically separate visual detectors. Distinct label names are insufficient evidence of distinct spatial computation. This is exactly what the proposed experiment must test, not assume.

## The real keystone was not inspected

The card marks `INSPECTED_TRUE`, but the inspected facts are only that two outputs, checkpoints, images, and measurement tools exist. The load-bearing prerequisite is:

> An anatomy-specific intervention can alter coronary calcium evidence while holding noncoronary calcium and other score-relevant image properties sufficiently fixed and remaining close enough to the model's input distribution that the score change is interpretable.

That has not been inspected or demonstrated.

“If I have only verified the nearest checkable thing, what am I still assuming?” The nearest checkable thing is that CT-CLIP and AI-CAC can emit numbers. The study still assumes that cross-sectional partial slopes identify which pixels or anatomy CT-CLIP uses, that CT-RATE can be passed through the released AI-CAC implementation without a consequential NIfTI-to-DICOM adaptation, that TotalSegmentator plus a 130-HU threshold is a valid aortic-wall calcium measure, and that coronary and noncoronary calcium have enough conditional support for stable estimation. Those are load-bearing. The correct status is `NOT_INSPECTED` until Stage 0 resolves them, so feasibility and novelty confidence should be capped at 3.

## Specific rejection attempts

### Concept-label circularity and leakage

The primary analysis avoids directly reusing RadBERT labels as outcomes, which is good. It does not avoid semantic circularity: a model output trained to match a report-derived “coronary calcification” label is compared with a second algorithm explicitly designed to detect coronary calcification. A positive association is an expected convergent-validity result, not evidence of a previously hidden model concept. It is worth doing only if the localisation test is genuinely causal or otherwise unusually well controlled.

Report leakage also remains relevant even though the report label is absent from the regression. CT-CLIP learned from reports, and report wording may encode age, prior CABG/stents, indication, or severity conventions correlated with AI-CAC. The image model can learn visual proxies for those reporting patterns. “N/A to primary” is therefore too strong.

### Confounding and identifiability

The proposed regression does not rule out:

- overall atherosclerotic age or disease burden causing coronary CAC, aortic CAC, and both scores;
- protocol, kernel, and thickness jointly changing CT-CLIP score and the automated measurements;
- cardiac hardware, valve calcium, mitral annular calcium, motion, or bone blooming acting as correlated hyperdensity cues;
- referral pathway and disease mix controlling which combinations of coronary and aortic calcium exist;
- the two heads being correlated readouts of a common representation rather than location-specific detectors.

Vendor, thickness, kernel, and habitus covariates do not isolate the mechanism. They reduce measured association with recorded covariates under modelling assumptions. Site is essentially not addressable within a predominantly single-institution cohort, and prevalence/referral pathway remain external-validity and support problems.

### Measurement validity

Calling “voxels >130 HU inside the TotalSegmentator aorta mask” aortic-*wall* calcium is premature. TotalSegmentator supplies an anatomical aorta segmentation; it is not validated in the cited paper as an aortic-wall calcium detector. Boundary placement, partial volume, vertebral contamination, contrast/noise, and whether calcified wall lies inside the produced mask all matter. This measurement requires direct visual QC on a frozen sample and preferably comparison with a dedicated calcium method. No radiologist campaign is necessary, but a deterministic measure still needs validation.

Likewise, the conventional Agatston construction is protocol-sensitive. CT-RATE includes reconstructions as thick as 6 mm, while the directly cited thickness study assessed up to 5 mm. Treating 6-mm AI-CAC output as interchangeable continuous Agatston is unsupported. Prespecified exclusion or stratification is safer than covariate adjustment alone.

### Data and compute

The data and checkpoints are available behind a click-through gate, so this is not a DUA failure. However, the card understates plumbing and storage. AI-CAC's released entry point is DICOM-based while CT-RATE provides processed volumes; adapting it and proving numerical equivalence is nontrivial method work. Running CT-CLIP, AI-CAC, and TotalSegmentator over a full validation set is plausible on single-GPU sessions, but “first decision in two days” is credible only for metadata, file-compatibility, prevalence, and a small QC sample—not for the asserted full double dissociation.

### Prior-work overlap and novelty

The precise CT-CLIP score-versus-CAC comparison was not found in the inspected primary sources, but that does not establish novelty. Automated opportunistic CAC on nongated chest CT is mature prior work; the new delta is only the audit of this particular foundation-model output and its anatomical specificity. That is a narrow but defensible methods contribution if localisation is established. Without a causal localisation test, it is a routine convergent-validity benchmark. Novelty confidence should be 3, not 4, pending a systematic primary-source search including 2025–2026 CT foundation-model interpretability work.

### Medical relevance

Coronary CAC is clinically important, but CT-CLIP is not the best available CAC quantifier. Showing that its generic label score correlates with AI-CAC does not itself improve patient risk stratification. The medical value is model auditing: whether a claimed anatomical output is faithful enough to trust or whether it is a generic vascular-calcium alarm. Score medical relevance 2–3 unless the result generalises to a broader claim about anatomically named foundation-model outputs.

### Endpoint and negative-result value

“Monotone gradient,” “partial independence,” and “double dissociation” need prespecified estimands and margins. At minimum, define rank correlation or an ordinal trend, the partial effects for both heads, a cross-head interaction contrast, acceptable measurement reliability, overlap criteria, and a minimum effect that counts as localisation. Otherwise many outcomes can be narrated as positive.

The primary fidelity null is sensitivity-limited: score saturation, AI-CAC transfer failure, thick slices, or restricted prevalence all survive. It merits negative-result value 2, not 3, unless measurement performance and score dynamic range pass preregistered gates. A well-powered *intervention* showing equivalent score response to coronary and aortic edits could be a decisive negative for localisation.

## Does it die like a prior candidate?

It does not repeat annotation-provenance failures 001, 002, 003, or 005 because the proposed biomarker readouts are computational. It does repeat the **wrong-keystone shape** of ideas 005 and 006: “the components emit measurements” was verified, while “their relationship identifies use/localisation” was assumed. It also approaches idea 006's OOD-intervention problem if the repair simply deletes calcium. A valid repair needs graded, local, realistic edits plus sham edits and QC; blanking or zeroing a coronary region would remain uninterpretable.

## Easier version and low-hanging fruit

The lowest-hanging *descriptive* version is a frozen validation-subset audit using the already released CT-CLIP checkpoint and AI-CAC output: test only whether the coronary score orders four AI-CAC risk strata (0, 1–100, 101–400, >400), with exclusions fixed by slice thickness and FOV. It drops TotalSegmentator and the unvalidated aortic-wall measure. This is easy and useful as a Stage 0 calibration check, but it is not worth publishing alone and cannot support “localises.”

The stronger low-hanging formulation exploits an asset already inspected in idea 004: 425 clean geometry-matched reconstruction pairs of identical CT-RATE acquisitions. Within each pair, anatomy, patient, referral pathway, site, and true calcium burden are fixed. Ask whether reconstruction-induced changes in a coronary calcium measurement selectively track changes in the coronary head, while changes in noncoronary vascular calcium selectively track the arterial head. This is much better controlled and avoids inventing synthetic anatomy, though it identifies sensitivity to the rendered calcium measurement rather than perfect voxel localisation. It also reuses a frozen cohort, geometry checks, CT-CLIP inference scripts, and an existing download plan.

For the full original claim, follow that with a small confirmatory perturbation set: use a coronary segmentation to apply graded, local calcium attenuation toward adjacent blood-pool/tissue values; use a matched aortic edit of equal changed volume, HU distribution, spatial smoothness, and distance from the volume centre; include sham edits in nearby noncalcified vessel voxels. The key endpoint is the head-by-location interaction in paired score changes. This directly tests reliance, but intervention realism must pass QC and sensitivity analyses; it should not be improvised after viewing results.

## Required revision

1. Demote the current regressions to convergent-validity/Stage 0 analyses and remove “use by definition.”
2. Set the present rung to 0 until a model score is actually produced and the measurement pipeline passes QC; a positive observational association reaches semantic calibration, not charter rung 1.
3. Replace `INSPECTED_TRUE` with `NOT_INSPECTED` and state the intervention-validity/file-compatibility keystone.
4. Inspect the exact CT-RATE file schema and demonstrate AI-CAC equivalence or choose a measurement tool that natively consumes the released format.
5. Validate the aortic-calcium measurement or drop it from the first experiment.
6. Prespecify conditional-support, dynamic-range, measurement-QC, and minimum-effect gates before fitting the localisation model.
7. Make the within-pair or anatomy-specific score-change contrast the primary endpoint; retain marginal correlations only as secondary calibration.

## Sources directly inspected

- Hamamci et al., *Developing Generalist Foundation Models from a Multimodal Dataset for 3D Computed Tomography*, arXiv:2403.17834; official CT-RATE repository: https://huggingface.co/datasets/ibrahimhamamci/CT-RATE.
- Hagopian et al., *AI Opportunistic Coronary Calcium Screening at Veterans Affairs Hospitals*, NEJM AI (2025), DOI: 10.1056/AIoa2400937; official code/weights: https://github.com/Raffi-Hagopian/AI-CAC/.
- Wasserthal et al., *TotalSegmentator: Robust Segmentation of 104 Anatomic Structures in CT Images*, Radiology: Artificial Intelligence 2023;5:e230024, DOI: 10.1148/ryai.230024.
- Yin et al., *Performance assessment of an artificial intelligence-based coronary artery calcium scoring algorithm in non-gated chest CT scans of different slice thickness*, Quantitative Imaging in Medicine and Surgery (2024), PMID: 39144022.
- van Velzen et al., *Deep learning for automatic calcium scoring in CT: validation using multiple cardiac CT and chest CT protocols*, Radiology (2020), DOI: 10.1148/radiol.2020191621.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Across geometry-matched reconstructions of identical CT-RATE acquisitions, do within-pair changes in measured coronary versus noncoronary vascular calcium selectively move CT-CLIP's coronary versus arterial calcification scores?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes—if Stage 0 confirms measurement dynamic range, because the paired design converts a routine calibration correlation into a stringent, low-confounding audit of whether anatomically named outputs behave anatomically.
