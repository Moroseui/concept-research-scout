# Adversarial critique: LIDC semantic concepts versus diagnosis

## Bottom line

The idea should **not advance in its current form**. Its motivating distinction is medically important, but the proposed experiment rests on three false or unverified premises:

1. the released diagnosis file is a clean nodule-level pathology endpoint;
2. enough diagnosed nodules can be unambiguously linked to the XML nodules for a paired AUC comparison; and
3. the comparison has not already been attempted.

A primary paper from 2012 directly used the released diagnosis data, compared a feature-based classifier and radiologists with that reference, and reported that it could reliably map only 18 nodules because the diagnosis-file numbering was inconsistent with the XML and lacked usable nodule identifiers. That is close prior work and, more importantly, direct evidence against the proposed feasibility story [Zinovev et al., 2012, DOI 10.1007/s10278-011-9445-3](https://doi.org/10.1007/s10278-011-9445-3). A revision is possible, but only after a data-linkage feasibility gate.

## Claim audit

### Verified facts

- LIDC-IDRI contains 1,018 cases representing 1,010 patients, with contours, a radiologist likelihood-of-malignancy rating, and eight other reader-rated nodule characteristics. The HSCNN paper explicitly acknowledges that its malignancy labels are suspicion levels rather than pathological diagnoses [Shen et al., 2019, PMCID PMC6623975](https://pmc.ncbi.nlm.nih.gov/articles/PMC6623975/).
- TCIA currently exposes the radiologist XML, a nodule-count spreadsheet, and a patient-diagnosis spreadsheet as separate downloads. It lists 1,010 subjects and a CC BY 3.0 license for the images and annotations; the displayed table does not show a license in the diagnosis-file row [official TCIA collection, DOI 10.7937/K9/TCIA.2015.LO9QL9SX](https://www.cancerimagingarchive.net/collection/lidc-idri/). Therefore the card's statement that *both endpoints* are explicitly CC BY 3.0 is not verified by the current collection table.
- Zinovev et al. state that the released diagnoses came from “follow-ups or biopsy procedures,” were supplied at patient level for nodules found in that patient's CT series, and could be reliably matched to only 18 XML nodules by restricting to patients with one nodule. Their resulting set contained 8 malignant, 9 benign, and 1 indeterminate nodule. They compared both radiologists and their classifier against those diagnoses [DOI 10.1007/s10278-011-9445-3](https://doi.org/10.1007/s10278-011-9445-3).
- Pathology-versus-reader-label mismatch is already an explicit limitation in the concept-model literature, not an unnoticed endpoint substitution. HSCNN says so directly, while Zhang et al. build an entire relabeling study around subjective LIDC ratings differing from pathological ground truth [arXiv:2207.14238](https://arxiv.org/abs/2207.14238).
- Existing work has already evaluated interpretable morphology against stronger outcomes. Choi et al. trained weak-label models on 811 LIDC nodules and tested on 72 strongly labelled LIDC nodules, and evaluated interpretable size, attachment, spiculation, and lobulation features [DOI 10.1016/j.cmpb.2020.105839](https://doi.org/10.1016/j.cmpb.2020.105839). The associated [CIR repository](https://github.com/nadeemlab/CIR) releases tooling/data for LIDC-IDRI and LUNGx.

### Source-supported interpretations

- The card overstates novelty. Zinovev et al. did not report the exact proposed eight-rating-to-two-endpoint paired AUC difference, but they did ask the broader opinion-versus-diagnosis question using radiologist characteristics and a classifier. The exact delta is therefore a different summary/model on a severely constrained cohort, not “the paired comparison has not been made.”
- “Pathology-confirmed malignancy” is too strong an endpoint description. The primary sources describe mixtures of biopsy/pathology and longitudinal confirmation. Even LUNGx, a better documented strong-label set, includes benign diagnoses established by stability or resolution and two test nodules only suspicious for malignancy [Armato et al., 2016, DOI 10.1117/1.JMI.3.4.044506](https://doi.org/10.1117/1.JMI.3.4.044506). The valid term is likely **confirmed clinical diagnosis**, with confirmation mechanism reported per case.
- The pathology spreadsheet's 157 subjects must not be equated with 157 linkable, pathology-proven nodules. The 2012 mapping result is evidence that those are very different denominators.

### Inferences requiring direct spreadsheet inspection

- Later authors may have reconstructed more than 18 matches using coordinates, nodule counts, or manual image review. Search results include studies claiming 72 strong-label nodules or 113 diagnosed patients, so the 18-nodule ceiling may no longer be absolute. However, no verified, released mapping from all eight XML concepts to a specific diagnosis row was established in this review.
- Some patient-level labels may be safe for single-nodule patients, but that selection changes the population and may preferentially exclude clinically complex cases.

## Rejection attempts

### 1. Prior-work overlap: serious

The closest work in the card omitted the most damaging paper. Zinovev et al. already:

- contrasted consensus/radiologist interpretation with diagnosis;
- used semantic/radiographic features in a classifier;
- evaluated radiologists and the classifier on the diagnosed subset; and
- identified the exact linkage failure that constrains this proposal.

Choi et al. further evaluated interpretable nodule morphology on a strongly labelled LIDC subset. The surviving delta is narrow: use the *eight released ordinal reader ratings themselves*, on the *same safely linked nodules*, and estimate a paired performance gap between reader suspicion and confirmed diagnosis. That delta may still be worthwhile, but novelty is uncertain and cannot support the current “whole literature has never checked” framing.

### 2. Endpoint clarity: currently unacceptable

The proposal mixes at least four targets:

- per-reader five-point suspicion;
- a consensus or averaged suspicion score;
- benign versus primary versus metastatic disease in the diagnosis sheet; and
- method of confirmation (pathology, follow-up, or possibly another clinical basis).

Primary and metastatic malignancy are not automatically interchangeable for a nodule-morphology question. Follow-up-confirmed benignity and pathology-confirmed malignancy also have asymmetric verification. Before analysis, the study needs a row-level endpoint dictionary, a binary target rule, handling of unknown/metastatic cases, and a sensitivity analysis restricted to tissue-confirmed cases if those fields exist.

### 3. Concept-label circularity: high for the opinion endpoint

The eight characteristics and the malignancy rating were assigned by the same reader in the same annotation session from the same image. Predicting that reader's malignancy rating from that reader's descriptors measures internal consistency of a rating form, not independent concept validity. Averaging both over readers does not remove the circularity; it can strengthen it by cancelling noise in both predictor and target.

This does not invalidate the comparison, but it changes its interpretation. A large opinion AUC is an expected positive control. The scientifically meaningful quantity is performance against an independently confirmed diagnosis, together with how much of any gap is explained by same-reader coupling. A better design would cross readers: predict reader B's suspicion from reader A's concepts, or use leave-one-reader-out aggregation, before comparing with diagnosis.

### 4. Leakage and unit-of-analysis risk: high

- Treating each reader annotation as an independent sample would duplicate the same nodule across folds.
- Multiple nodules from one patient must remain in one fold.
- If a patient-level diagnosis is copied to all nodules, the label is leaked/misattributed rather than merely noisy.
- Selecting or manually matching nodules after seeing their ratings or diagnoses would introduce adjudication bias.

Splits must be patient-grouped. Linkage must be frozen while blinded to concept values and malignancy ratings. Ambiguous patients cannot enter the confirmatory analysis.

### 5. Confounding: more severe than the card states

Verification bias is only one issue. Additional threats are:

- **spectrum restriction:** biopsied/resected nodules are enriched for difficult or suspicious cases;
- **incorporation bias:** clinical decisions leading to biopsy or follow-up may have used the same CT morphology represented by the concepts;
- **size and prevalence:** nodule size is clinically predictive but is absent from the proposed concept set, and a selected diagnosed cohort may differ strongly in size;
- **site/protocol:** LIDC combines screening and diagnostic scans from multiple sources;
- **reader dependence:** concepts and suspicion share readers and annotation context;
- **differential verification:** benign and malignant cases may be confirmed by different mechanisms;
- **label granularity:** calcification and internal structure are categorical codes, not ordinal quantities. Treating all eight as ordinal continuous variables is substantively wrong.

A useful analysis must encode nominal concepts appropriately and report size-only and size-plus-concept baselines. Otherwise “concept validity” may just be omitted-variable behavior.

### 6. Statistical power and negative-result value: weak as proposed

With 8 malignant and 9 benign safely mapped cases in the verified primary analysis, nested cross-validation, eight predictors, and a paired bootstrap AUC difference are not credible. Separation and unstable folds are likely; confidence intervals will be enormous. Penalization does not manufacture information.

Even if a later mapping yields roughly 72–113 usable nodules, a small observed gap will not “license the field's endpoint substitution.” It may simply be an imprecise estimate in a selected, verification-biased cohort. Therefore the card overstates negative-result value. A negative result is useful only if an a priori precision criterion is met—for example, the confidence interval excludes a clinically material AUC gap. Otherwise it is inconclusive, not reassuring.

### 7. Relevance and compute

Medical relevance is strong: distinguishing reproduction of reader suspicion from association with disease matters. Compute is not a concern for the tabular analysis. Data semantics and linkage, rather than compute, are the blocking feasibility issue.

## Smallest decisive feasibility gate

Before revising the scientific protocol, perform a no-model data audit:

1. Download and inspect the diagnosis and nodule-count spreadsheets directly.
2. Enumerate confirmation mechanisms and counts by diagnosis class.
3. Reproduce the 2012 18-nodule safe linkage using patient ID plus single-nodule restriction.
4. Locate and verify any published/released 72- or 113-case mapping, including its linkage method and whether all eight XML ratings are available.
5. Produce a blinded linkage flowchart: diagnosed patients → diagnosis rows → uniquely linked CT nodules → nodules with at least the prespecified number of readers → analyzable class counts.
6. Stop if the uniquely linked binary cohort cannot meet a prespecified precision target. Do not proceed merely because a classifier can be fit.

This gate is easier and more decisive than the proposed nested-CV experiment. It requires no images or GPU and prevents an invalid patient-to-nodule merge.

## Easier formulations

### Preferred low-hanging-fruit revision: one-concept external validity audit

**Question:** Does spiculation retain similar association with radiologist suspicion in LIDC and with confirmed diagnosis in the already curated strong-label LIDC/LUNGx cohorts?

Why this is easier:

- Choi et al. already define and evaluate an interpretable spiculation measure on 811 weak-label LIDC nodules, 72 strong-label LIDC nodules, and 73 LUNGx nodules.
- CIR releases relevant tooling and QA/QC'ed spiculation/lobulation assets.
- LUNGx publishes nodule locations and diagnoses through TCIA [dataset DOI 10.7937/K9/TCIA.2015.UZLSU3FL](https://doi.org/10.7937/K9/TCIA.2015.UZLSU3FL).
- The experiment can be a reanalysis of one concept with a size-only baseline, size-plus-spiculation model, confidence intervals, and explicit confirmation strata.

Limitations: this tests one computed/curated morphological concept rather than all eight original reader ratings; LUNGx's diagnoses are not uniformly pathology-confirmed; and Choi et al. make novelty overlap substantial. Its value would need to come from a precise weak-versus-strong endpoint comparison or a robustness audit absent from that paper, verified by reading its full methods and supplements. This is a feasible salvage, not yet a verified novel project.

### Lowest-cost non-model formulation: endpoint-practice audit

Systematically sample LIDC “concept-based” papers and record the true endpoint, whether it is described as cancer/pathology/malignancy suspicion, whether same-reader circularity is acknowledged, and whether any diagnosis-linked validation is performed. This directly tests the rhetoric-level claim that the literature conflates opinion with disease. It requires no linkage or compute, but it is a systematic review/methodological audit rather than an imaging experiment and needs a preregistered search and coding protocol.

### Conditional original formulation

Retain the eight-concept paired comparison only if the feasibility gate finds a released, auditable, uniquely linked cohort large enough to estimate the paired gap with useful precision. Reframe the outcome as confirmed clinical diagnosis, model categorical concepts correctly, use patient-grouped resampling, add cross-reader analyses, and make the primary estimand the difference with a prespecified equivalence/non-inferiority margin rather than two separately reported AUCs.

## Revised assessment

| Dimension | Score | Reason |
|---|---:|---|
| Clarity | 3/5 | The motivating contrast is clear, but diagnosis, confirmation, aggregation, and estimand are not. |
| Medical relevance | 4/5 | Clinically meaningful distinction, tempered by selected historical data. |
| Interest | 4/5 | Broadly interesting, but the strongest rhetoric overstates what the literature ignored. |
| Prior legwork | 3/5 | Data and prior analyses exist; the critical linkage table is not verified as usable. |
| Feasibility | 2/5 | CPU-cheap but likely blocked by linkage and precision. |
| Data readiness | 2/5 | Public files exist, but nodule-level truth and licensing of the diagnosis row are insufficiently established. |
| Evaluation readiness | 2/5 | AUC is standard, but the paired estimand, power target, categorical encodings, and confirmation strata need definition. |
| Negative-result value | 2/5 | An imprecise null cannot validate endpoint substitution. |
| Novelty confidence | 2/5 | Direct 2012 overlap plus later strong-label interpretable-feature work. |
| Regret | 3/5 | Worth checking, but the apparent obvious opportunity may be an artifact of unusable linkage. |

Weighted priority score using the charter rubric: **2.85/5**.

`0.20*2 + 0.15*3 + 0.15*4 + 0.15*4 + 0.10*3 + 0.10*2 + 0.05*2 + 0.05*2 + 0.05*2 = 2.85`

## Decision

**PAUSE**

Do not write a full feasibility memo or probe contract for the original experiment yet. Resume only after the no-model linkage audit establishes the actual uniquely linked sample, confirmation mechanisms, class balance, and a defensible precision target. If it fails, pivot to the one-concept CIR/LUNGx audit or the endpoint-practice review.
