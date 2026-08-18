FATAL OBJECTION: The proposed stage-2 correlation cannot identify that a model learned affine-transfer error rather than ordinary lesion size/location priors, output smoothing, or acute predictors of severe infarction.
EVIDENCE: `ideas/030/idea_card.json` (`use_vs_association`, `smallest_decisive_experiment`); the proposed DeepISLES control consumes follow-up DWI/ADC in its own space and is not a matched acute final-infarct predictor.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION

# Adversarial critique

## Bottom line

The card contains a worthwhile, unusually concrete **dataset audit**, but it currently overclaims a **model-use mechanism**. Acute-CSF overlap can establish that some released labels occupy a conservative set of anatomically impossible acute-space voxels. It cannot, by correlation alone, establish why a final-infarct model predicts those voxels. The stage-1 and stage-2 claims must be separated, the stage-1 negative interpretation sharply weakened, and stage 2 replaced with a controlled label-construction experiment.

## 1. The fatal identifiability defect

The proposed evidence for model inheritance is: prediction overlap with acute CSF tracks ground-truth overlap, while a DeepISLES result has near-zero overlap. That comparison does not isolate inheritance.

- DeepISLES is used to segment the realized lesion from **follow-up DWI/ADC**, whereas the audited model predicts future infarct from **acute CT-derived inputs**. It differs simultaneously in input modality, time point, task, coordinate frame, architecture, and training data. Its lower CSF overlap cannot serve as the counterfactual “same predictor, not trained on transferred labels.”
- Per-case ground-truth CSF overlap will co-vary with lesion volume, vascular territory, ventricular/sulcal proximity, and severity. Those same variables can increase a model's predicted volume and boundary smoothing. Adjusting or stratifying by lesion volume does not remove unmeasured geometry and territory differences.
- A prediction in acute CSF is evidence of an anatomically invalid output, but not evidence that the model *uses registration error*. The model does not observe the follow-up-to-acute transform. At most, it may reproduce a spatial label convention learned during supervision.

The repair is a paired training-label intervention: freeze split, inputs, architecture, augmentation, optimization budget, seeds, and postprocessing; train matched models on (A) released labels and (B) labels with only a preregistered, conservative acute-CSF intersection removed. On held-out cases, compare prediction probability specifically within the independently defined impossible set and in matched peri-lesional non-CSF control voxels. A repeatable A-minus-B difference localised to the edited set would identify the causal effect of those label voxels on model output. It would support “training on the released impossible voxels causes their reproduction,” not the broader claim that all affine-transfer displacement is learned.

## 2. Stage 1 is narrower than the card says

The “impossible-voxel” test is strong only as a **high-specificity subset audit**. Its computation adds no registration, but the tested ground truth is itself already registered; calling the endpoint simply “registration-free” risks hiding that distinction.

A positive conservative overlap is interpretable if the acute-CSF mask is valid. A near-zero overlap is not a “clean bill on geometry.” Affine error can move lesion labels from one acute tissue voxel to another without intersecting ventricles or sulci. The endpoint is therefore specific but insensitive to the general mass-effect displacement claimed in the title and deliverable. The anticipated negative-result value and score of 4 are overstated. A null says only that this CSF-intersection sentinel found little error above its detection threshold.

The secondary affine-versus-deformable comparison does not automatically close that gap. Nonlinear multimodal registration between acute NCCT and abnormal follow-up DWI is itself underidentified without landmarks or independent expert review. Brett et al. established cost-function masking for focal-lesion normalization (DOI 10.1006/nimg.2001.0845), but that does not validate ANTs SyN or SynthMorph as truth for this cross-modality, cross-time problem. The primary stroke-registration literature already treats edema and anatomical distortion as a central obstacle and reports nonlinear-versus-linear registration as a methodological question, not a solved reference standard (O'Brien et al., *Optimizing image registration and infarct definition in stroke research*, PMCID PMC5338168).

## 3. The mass-effect signature is confounded

“Overlap grows with lesion volume and midline shift” is not a unique fingerprint of affine failure.

- Larger lesions have larger surfaces, are more likely to reach sulci or ventricles, and generally induce smoother/larger model outputs.
- Midline shift is not operationally defined: the acute scan may precede substantial swelling, while follow-up shift is measured in the same deformed image that motivates the hypothesis.
- Mask interpolation, anisotropic resampling, and topology can also scale with lesion size. Calling interpolation error a thin shell does not make its aggregate fraction independent of lesion geometry.

At minimum, the revision needs a voxel-shell analysis by signed distance to the acute CSF boundary, lesion territory and surface area controls, explicit definitions and time point for mass-effect measures, and sensitivity to label interpolation conventions. These analyses can characterize alternatives; they still do not make the correlation mechanistically unique.

## 4. Endpoint validity needs a real gate

The proposed `0–15 HU` rule plus SynthSeg agreement is not yet a validated acute-CSF reference for these released, resampled NCCT derivatives. Low-attenuation infarct, partial volume, beam-hardening, chronic cavities, and preprocessing interpolation can enter the window. Erosion helps specificity but may sharply reduce sensitivity, especially in narrow sulci.

Before any benchmark claim, a blinded visual audit of a prespecified sample of candidate impossible voxels is warranted. This is fresh annotation burden and must be stated as such under the charter. A cheaper alternative is to restrict the confirmatory set to deeply eroded ventricular CSF and treat sulcal CSF and automated segmenter agreement as sensitivity analyses. That is less comprehensive but substantially more defensible.

The official challenge evaluates Dice, absolute volume difference, absolute lesion-count difference, and lesion-wise F1 (ISLES'24 official repository, https://github.com/ezequieldlrosa/isles24; dataset/challenge paper arXiv:2408.10966). The card proposes metric shifts only for Dice and absolute volume difference. That is acceptable if explicitly scoped, but it does not bound the effect on the full official ranking; clipping even tiny disconnected components could disproportionately change lesion-count and lesion-wise F1.

## 5. Prior-work and novelty calibration

The broad scientific problem is not novel. Edema distorting follow-up infarct measurement and the need for nonlinear coregistration/CSF exclusion are established. O'Brien et al. explicitly frame edema and atrophy as causes of anatomical distortion in final-infarct definition (PMCID PMC5338168). Prior final-infarct studies report attempts to correct edema with nonrigid registration and CSF exclusion, and edema-corrected infarct-volume methods have quantified clinically meaningful differences (Boers et al., PMID 29668493; DOI 10.1161/STROKEAHA.117.020072).

The defensible delta is narrower: an audit of the **released ISLES'24 NCCT-space masks**, using an acute-CSF sentinel and reporting consequences for official metrics. The search does not verify that nobody has done this; it supports only “no duplicate located in the targeted search.” The card's “blind spot” explanation and “no one has measured” rhetoric are speculation and should be removed unless a systematic novelty audit verifies them.

## 6. Data and compute realism

The inputs are obtainable under the public noncommercial release, so data access is not fatal. However, the card's `~10–15 GB download` estimate conflicts with the repository's own inspected dataset record: `evidence/datasets.csv` records a monolithic approximately 99 GB `train.7z` in the inspected Zenodo release and says derivative-only retrieval is unverified. The full public cohort is 149 cases in the release, with a 149-versus-150 paper discrepancy already recorded. Feasibility must budget the actual archive transfer/storage and pin a Zenodo version and checksum.

No suitable frozen acute final-infarct checkpoint is identified. “The shared audit model materializes” is an acknowledged dependency, not an asset. The low-hanging stage-1 audit needs no checkpoint and, if restricted to ventricular CSF, likely no GPU. A causal stage-2 repair probably requires matched training runs rather than inference only, so the stated five-GPU-hour envelope is unsupported.

## 7. Relevance and negative results

A positive stage-1 result matters: it would quantify a concrete failure in benchmark labels and show its effect on evaluation. Its medical relevance is greatest if errors concentrate in severe strokes or change rankings, but neither is yet established.

A negative 30-case result is sensitivity-limited, not decisive. Stratification by lesion volume does not ensure enough cases with ventricular/sulcal adjacency or visible mass effect. The card needs a precision target for the prevalence or voxel-fraction estimate and a support gate based on the number of cases whose lesions lie near confidently segmented CSF. If that support is absent, the study cannot validate the geometry pipeline; it can only report that the chosen sentinel rarely had an opportunity to fire.

## 8. Plain-pitch fidelity

The plain pitch fails fidelity in three places.

1. “Copied ... using a simple global alignment” is faithful to the documented affine transfer, but “That would smear each answer's position” turns a plausible consequence into certainty. The technical card explicitly says the surviving halo magnitude is unverified and may be near zero after correction.
2. “Using fluid spaces as tamper-proof landmarks” overstates the unvalidated NCCT CSF measurement and suppresses partial-volume, chronic-cavity, and resampling limitations named in the card.
3. “Models ... have learned to copy the error” states the stage-2 causal conclusion more strongly than the proposed observational overlap comparison can support.

The pitch must preserve “may,” call CSF a conservative sentinel rather than tamper-proof, and describe model inheritance as a question requiring a controlled label experiment.

## 9. Easier version and existing assets

The easiest worthwhile experiment is a model-free, CPU-first ventricular-CSF sentinel audit on the released training labels:

1. Use the released NCCT and `space-ncct` lesion mask.
2. Define only deeply eroded ventricular CSF as confirmatory; visually verify a small blinded sample.
3. Report per-case impossible-voxel count/fraction with confidence intervals and opportunity-to-overlap support (lesion distance to ventricular CSF).
4. Recompute all four official metrics after removing only verified impossible components, using the already released evaluation code.
5. Treat sulcal CSF, deformable registration, edema correlations, and any model analysis as later modules.

The data, labels, and official metric code already exist. This version eliminates learned registration, GPU dependence, the unavailable checkpoint, and most of the reference-registration dispute. It does **not** answer whether a model learned the error, so under the program's claim-identity rule it should be a separate dataset-quality candidate if the current card keeps its model-use deliverable.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: How often do released ISLES'24 final-infarct masks include conservatively verified acute ventricular-CSF voxels, and how much does removing only those voxels change all four official evaluation measures?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—the audit is cheap, falsifiable, directly benchmark-relevant, and a positive result would justify the more expensive paired-label model experiment.
