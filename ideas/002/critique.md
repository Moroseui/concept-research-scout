# Adversarial critique: Idea 002

## Bottom line

The idea card's central novelty premise is false. Clinical-only versus dermoscopic-only prediction of every Derm7pt checklist category was reported in the dataset's original paper and repeated more recently. The remaining diagnosis-control idea is potentially useful, but the proposed endpoint cannot support the stated conclusion that performance above the control is "genuinely visible" evidence. This should not advance unchanged.

A narrower, cheaper audit is salvageable: quantify how much checklist-label information a clinical photograph adds **conditional on diagnosis and recorded metadata**, without claiming that the residual is the named dermoscopic structure. That is a shortcut/conditional-predictability study, not a visibility or causal-grounding study.

## Decisive prior-work overlap

### Verified facts

- Kawahara et al. explicitly built separate single-modality clinical and dermoscopic classification layers and evaluated them on the official split. Table II reports clinical-only (`xc`) and dermoscopic-only (`xd`) accuracy for all seven checklist categories and diagnosis. Clinical-only average accuracy was 64.1%, versus 72.5% for dermoscopy-only; individual clinical-only checklist accuracies were also reported. The text explicitly interprets dermoscopy as better because the checklist was designed for features visible under dermoscopy. DOI: [10.1109/JBHI.2018.2824327](https://doi.org/10.1109/JBHI.2018.2824327); primary author-hosted [paper PDF](https://www.cs.sfu.ca/~hamarneh/ecopy/jbhi2018a.pdf).
- Zhang et al. again report a single-versus-multimodal breakdown in Table 6. Their clinical-only row contains results for diagnosis and every checklist category; their dermoscopic-only and metadata-only rows provide the corresponding comparisons. arXiv: [2409.12390](https://arxiv.org/abs/2409.12390).
- The original official repository supplies loading and classification examples, while the data are downloaded separately from the official dataset site. It does not establish that ready-to-use trained checkpoints or per-case predictions exist. Official repository: [jeremykawahara/derm7pt](https://github.com/jeremykawahara/derm7pt); official [dataset site](https://derm.cs.sfu.ca/).

### Source-supported interpretation

The card says that the literature reports fused performance and that isolating each modality is the missing step. That is contradicted by two primary papers, including the dataset paper itself. Consequently, the minimal experiment's arms (a) and (b) are replication, not the claimed gap. The only plausible delta is the proposed diagnosis-aware audit and stronger controls.

### What remains unverified

This search did not establish that nobody has already performed the exact diagnosis-conditional audit. Absence from the papers inspected is not proof of novelty. A broader primary-source search would still be required before making a novelty claim.

## Concept and causal problems

### The phrase "by definition not visible" is too strong

The seven checklist items are dermoscopic criteria, and the original paper describes dermoscopy as revealing detailed morphology and explicitly says the checklist was designed for features visible under dermoscopy. That does **not** imply that ordinary photographs contain zero correlates. Lesion colour, shape, elevation, ulceration, scale, and diagnosis-associated morphology can covary with a dermoscopic finding. Some clinical photographs may also be close, high-resolution views. Therefore:

- **Verified fact:** the named labels are dermoscopic checklist categories.
- **Inference:** a clinical photograph may contain correlates of those labels.
- **Unsupported claim:** performance above a diagnosis-only baseline proves the named dermoscopic structure itself is visible or grounded.

This distinction changes the scientific question. The dataset can test conditional predictability; it cannot, without a visibility reference standard, determine whether the model detected the dermoscopic structure itself.

### Annotation provenance is unresolved and material

The original paper says each case's diagnosis and checklist categories were assigned by a dermatologist, but it does not state in the inspected methods whether the annotator saw only the dermoscopic image, both images, clinical context, or pathology when assigning each criterion. The idea card correctly calls this risky, but it is not a minor detail. If both modalities/context were available, the labels may encode multimodal judgment. Until the Atlas/database annotation protocol is traced to a primary source or confirmed by the data owners, the strongest grounding story is not identified.

### The diagnosis-only control is not a causal control

Using the **true diagnosis label** to predict each concept answers: "How predictable is this checklist label from oracle diagnosis?" It does not answer how much of a clinical-image model's performance comes from an internally inferred diagnosis.

The proposed decision rule is invalid in both directions:

- Clinical-image performance above an oracle diagnosis baseline need not mean genuine structure visibility. The residual could reflect age, site, elevation, ruler/background, acquisition source, subtype, disease severity, or other correlates omitted from the baseline.
- Performance at or below that baseline need not mean the image model is merely using diagnosis. Oracle diagnosis is privileged information and can outperform a model even when the model uses real visual evidence.

Calling control (c) an absorber of concept-diagnosis correlation therefore overstates what it identifies. It is a useful predictive baseline, not a mediator test or shortcut proof.

### Concept-label circularity cuts both ways

The checklist criteria were designed to contribute to melanoma assessment, so diagnosis-concept association is expected rather than automatically spurious. Conversely, diagnosis may have been pathology-based while criteria were visually assigned, in which case neither direction is a simple cause of the other. Treating diagnosis as the shortcut-generating variable imposes a causal graph that the dataset alone does not establish.

## Data, leakage, and evaluation risks

### Verified facts

- Derm7pt contains 1,011 cases with paired clinical and dermoscopic images and fixed row-index train/validation/test lists. The published split sizes are 413/203/395. DOI: [10.1109/JBHI.2018.2824327](https://doi.org/10.1109/JBHI.2018.2824327).
- Four cases lacked clinical photographs in the original study; the authors replaced those missing clinical inputs with dermoscopic images. Those four must be excluded from any clinical-only audit, not silently inherited.
- The original split was chosen to preserve category distributions. Since there is one paired case per row, using those row indices keeps the two modalities of a case together. This addresses direct paired-image split leakage, but not source/provenance leakage.
- The newer Consistent-Derm7pt repository says it includes paired clinical and dermoscopic crops and metadata, but its supplied filtered splits are designed around diagnosis/concept consistency, not this question. Official repository: [gnapoles/Consistent-Derm7pt](https://github.com/gnapoles/Consistent-Derm7pt); DOI: [10.1038/s41598-026-56927-2](https://doi.org/10.1038/s41598-026-56927-2).

### Risks that remain

- **Acquisition/provenance:** background, ruler, framing, clinic, camera, or preprocessing may predict labels. Case-level splitting does not remove dataset-source effects when the same source appears across cases and splits.
- **Selection:** this is a curated/excised-lesion atlas, not a representative smartphone teledermatology cohort. A result does not directly validate consumer skin-check use.
- **Class imbalance and label form:** five criteria are multiclass after grouping and two are binary. "Per-concept AUC" is underspecified: one-vs-rest macro AUROC, weighted AUROC, and binary malignancy-associated collapse answer different questions. Rare classes make estimates unstable.
- **Small effective strata:** conditioning on five grouped diagnoses leaves very small groups (e.g. 42 BCC and 45 seborrheic keratosis cases overall), so per-diagnosis model comparisons will be noisy. Fine-grained diagnoses may help confounding control but worsen sample size.
- **Split optimization:** published models selected checkpoints using aggregate validation accuracy. Reusing their final test table for a newly selected per-concept hypothesis risks post-hoc endpoint selection. A revised study must preregister its primary labels/metrics or treat the official test-set analysis as exploratory and confirm elsewhere.
- **Paired design overclaim:** paired modalities control lesion identity when comparing predictions, but independently trained modality models still differ in learnability, image preprocessing, and resolution. The design does not make imaging medium the only manipulated factor in a causal sense.

## Medical relevance and negative-result value

The warning about unsupported named readouts in ordinary-photo systems is medically relevant. However, no inspected source establishes that a deployed teledermatology or consumer system emits Derm7pt criteria from ordinary photographs. The direct clinical relevance is therefore plausible but presently speculative.

The card also claims there is no uninformative outcome. There are several:

- no detectable residual because the sample is underpowered;
- residual predictability produced by unmeasured provenance;
- mixed results driven by metric choice or label imbalance;
- a result specific to this curated atlas and obsolete imaging pipeline.

A negative result is useful only with uncertainty intervals demonstrating that a clinically meaningful residual has been excluded. Failure to reject a difference is not evidence that the model uses diagnosis alone.

## Compute and implementation readiness

Compute is not the problem. A small pretrained backbone on about 1,000 images is compatible with a single GPU, though the proposed 2 modalities × 7 heads × 5 seeds need not mean 70 separate models: a multitask head can predict all criteria jointly. The larger practical risks are legacy dependencies, absence of verified checkpoints/per-case outputs for the most relevant published models, and statistical instability.

The claim that cropped images and frozen splits make the experiment immediately ready is partly supported. The newer repository provides cropped pairs, metadata, a notebook, and filtered splits, but filtering cases according to concept/diagnosis consistency would distort the very association being audited. The untouched original 1,011-case cohort and original split should be the primary cohort, with four missing-clinical cases excluded and documented.

## Easier version that preserves the interesting question

### Low-hanging-fruit gate: no GPU

First perform a tabular audit on the frozen training/validation portions only:

1. For each original multiclass checklist category, estimate predictions from diagnosis alone and from diagnosis plus recorded age/sex/location/elevation, using training data only.
2. Report macro one-vs-rest AUROC and macro F1 with bootstrap intervals, plus class prevalences. Do not use the untouched test set for design.
3. Compare these baselines descriptively with the already-published clinical-only results, while clearly noting that cross-paper metrics/models are not a confirmatory comparison.
4. Quantify within-diagnosis label variation. If a criterion is nearly determined by diagnosis, it is a poor target for testing residual image information. Select any later target using validation data and clinical rationale, not test results.

This reuses public metadata, official splits, published modality baselines, and existing loading code. It can reveal in hours whether the proposed confound is large enough to motivate image training. It cannot establish visibility.

### Smallest defensible image experiment

If the tabular gate supports continuation, revise the question to:

> Does a clinical photograph add out-of-sample predictive information about a Derm7pt checklist label beyond diagnosis and recorded metadata?

Use one shared pretrained clinical-image encoder with seven prespecified heads, and compare nested predictors trained under identical splits and tuning rules: covariates only versus covariates plus clinical image. Evaluate paired per-case loss improvement and prespecified macro AUROC/F1 with bootstrap confidence intervals. Include background-only and lesion-only crops if reliable crops already exist; these distinguish lesion-region signal from gross context but still do not prove the named structure is visible. Keep the dermoscopic model as a positive reference, not as the novelty claim.

The decisive endpoint should be incremental predictive value over the covariate baseline, not whether clinical AUROC exceeds an oracle diagnosis AUROC. The interpretation must remain "residual label information in the photograph." Demonstrating genuine named-feature visibility would require an independent dermatologist visibility assessment or localized annotation, which violates the desired low-annotation profile unless done on a very small validation subset.

## Required revision conditions

Before feasibility review, the revised card should:

1. Replace the novelty claim with the diagnosis/metadata-conditional delta and cite both prior modality ablations.
2. Remove "by definition not visible," "only manipulated factor," and the proposed above/below-control causal interpretations.
3. Verify annotation provenance from a primary source or record it as a hard interpretive limitation.
4. Define the exact label encodings and primary metric for binary and multiclass criteria.
5. Exclude and list the four cases without true clinical images.
6. Audit split indices and duplicate/near-duplicate cases, and test acquisition/background shortcuts.
7. Freeze the primary comparison before touching the official test set; attach uncertainty intervals and an equivalence margin for any negative conclusion.
8. Treat the zero-GPU tabular analysis as a feasibility gate and stop if there is too little within-diagnosis label variation or uncertainty is prohibitive.

ADVANCE TO REVISION
