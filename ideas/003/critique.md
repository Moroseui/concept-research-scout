# Adversarial critique: Idea 003

## Bottom line

The idea in its current form is not executable on BUS-BRA and overstates what synthetic interventions can establish about clinician behaviour. BUS-BRA has biopsy labels, BI-RADS **assessment categories**, masks, and predefined folds, but no released lesion-level BI-RADS lexicon descriptors. The original paper's intervention was also not merely “almost certainly” an oracle protocol: the full paper explicitly corrects **all incorrectly predicted concepts** to their ground-truth classes. It already reports a clinically important failure omitted from the idea card: strong (“maximal”) correction degraded AUROC for every architecture.

The interesting question survives, but it should be split. A small public dataset, BrEaST (256 patients), contains images, masks, seven BI-RADS descriptor fields, the radiologist's BI-RADS category, and benign/malignant outcome. It enables a cheap **descriptor-information and simulated-intervention upper-bound study**, not a study of real clinician behaviour. A genuine clinician-selected/noisy-intervention claim requires either existing multi-reader correction data or a reader study; neither is currently identified.

## Verified facts

1. **BUS-BRA does not supply the needed concept labels.** Its official Zenodo record describes 1,064 patients, biopsy-proven cases, BI-RADS categories 2–5, and tumor/normal delineations. The archive preview shows `bus_data.csv`, fold CSVs, images, and masks; neither the record nor the peer-reviewed data paper describes descriptor-level labels. The authors' official code repository says its classification tasks are pathology class and BI-RADS category. This is strong primary-source evidence that BUS-BRA cannot train or evaluate the proposed descriptor bottleneck. Sources: [Zenodo record 8231412](https://zenodo.org/records/8231412), [dataset paper, DOI 10.1002/mp.16812](https://doi.org/10.1002/mp.16812), [official BUS-BRA repository](https://github.com/wgomezf/BUS-BRA).

2. **The target paper uses five binarized descriptors:** shape, orientation, margin, echo pattern, and posterior features. Each is collapsed into “indicative of benignity” versus “indicative of malignancy.” Thus the intervention is not correction of the full clinical lexicon but correction of five malignancy-oriented binary variables. Source: Bunnell et al., MICCAI 2024, [paper PDF](https://papers.miccai.org/miccai-2024/paper/4008_paper.pdf), arXiv:2407.00267.

3. **The published protocol is full error-aware oracle correction.** Every incorrectly predicted concept is identified using ground truth and adjusted; “minimal” sets the correct class to pseudo-probability 0.51 and “maximal” to 0.99. It is therefore stronger than any plausible clinician workflow both in knowing which concepts are wrong and in having the correct answer available. Source: [Bunnell et al.](https://papers.miccai.org/miccai-2024/paper/4008_paper.pdf).

4. **The headline in the idea card is imprecise.** The strict linear CBM moved from 0.863 to 0.885 AUROC at IoU 0.50 under minimal correction (a +0.022 point estimate), not from 0.876 to 0.885. The abstract's 0.876 appears inconsistent with Table 4. More importantly, maximal correction reduced the strict linear model to 0.839; the paper attributes this to distribution shift between soft predicted concepts used for training and strongly corrected concepts at test time. The failure is already demonstrated, not a new hypothesis. Source: Table 4 and discussion in [Bunnell et al.](https://papers.miccai.org/miccai-2024/paper/4008_paper.pdf).

5. **Relevant intervention analysis substantially predates this proposal.** Shin et al. study intervention selection, intervention count, granularity, reliability, and fairness, including “realistic settings.” This does not cover this breast-ultrasound model, but it means random/ordered partial-intervention curves alone are methodologically incremental. Source: Shin et al., ICML 2023, [PMLR paper](https://proceedings.mlr.press/v202/shin23a.html).

6. **BrEaST is a real low-hanging-fruit dataset.** Its primary data descriptor reports 256 patients (98 malignant, 154 benign, 4 normal), images and masks, seven BI-RADS feature fields, BI-RADS category, verification method, histologic diagnosis, and final benign/malignant classification. It is public through TCIA under CC BY 4.0. Source: Pawłowska et al., *Scientific Data* 2024, DOI [10.1038/s41597-024-02984-z](https://doi.org/10.1038/s41597-024-02984-z), PMID 38297002.

## Reasons to reject the current formulation

### 1. The primary experiment has no compatible public training data

BUS-BRA cannot support the descriptor arm, and BUSI is not documented here as having the required descriptor labels. The authors' 8,854-image/994-woman cohort is unavailable. The public repository provides training/evaluation code and a demo dataset, but the repository page does not establish that trained research weights are released; its “sample_data” is explicitly not representative of the study cohort. Consequently, “retrain the released architecture on BUS-BRA” is not a valid plan.

Even substituting BrEaST changes the project materially: 256 independent cases are far fewer than the target cohort, and the target model uses a ResNet-101 Mask R-CNN plus a three-stage procedure and 25 Optuna trials per stage. That is unnecessary for the scientific question and vulnerable to high variance on such a small dataset.

### 2. “Realistic clinician behaviour” is not identified by synthetic noise

Random flips at a chosen error rate are not clinician errors. Clinician mistakes are descriptor-specific, correlated, image-dependent, and affected by the displayed model suggestion. Likewise, “visually salient” selection is not clinician-selected unless clinicians make the selections. No primary source is supplied for a transition matrix, per-descriptor reader reliability, correction propensity, or automation-bias model that would make the simulation clinically calibrated.

Therefore a synthetic sweep can support only a conditional statement such as: *under prespecified corruption model X, intervention benefit disappears above error rate r*. It cannot answer whether the benefit “survives realistic clinician behaviour.” That endpoint is presently unclear and unvalidated.

### 3. The BI-RADS-category baseline is useful but partly circular

Comparing malignancy discrimination from descriptors with discrimination from BI-RADS category is clinically understandable, but both are usually produced by the same radiologist in one assessment. The category is downstream of the descriptors and may incorporate information not represented in the five binarized concepts. On BrEaST, the collecting radiologist supplied descriptors and category, so this is not an independent comparison of “model plus clinician” against “clinician unaided.” It is a comparison of two encodings of one retrospective assessment.

There is also potential outcome-related circularity: verification pathways depend strongly on BI-RADS category. BrEaST states that category 1–3 cases can be verified by follow-up whereas 4a–5 have histology; only 197/256 underwent biopsy. Thus “biopsy-proven endpoint” cannot be claimed for the whole dataset, and differential verification must be reported. BUS-BRA is biopsy-proven, but lacks the descriptors.

### 4. The proposed intervention has privileged leakage

Selecting only concepts known to be incorrectly predicted uses ground-truth concept labels to decide whether to act. This leaks oracle information into the intervention policy even before the correct value is inserted. A deployable policy must decide whether and where to intervene from observable variables. Uncertainty ordering is observable; error ordering is not. Any comparison must separate:

- a diagnostic oracle ceiling (wrong concepts known);
- an implementable selection policy (model uncertainty or fixed groups);
- a human policy (measured choices, not simulated labels).

The original model's side-channel variant is additionally unsuitable for strong claims about concept-mediated correction because the paper itself finds that the head can ignore the named concepts in favor of the learned non-clinical node.

### 5. The negative-result story is weaker than claimed

A flat curve could arise from poor concept prediction, redundant descriptors, an insensitive task head, train/intervention distribution shift, insufficient sample size, miscalibrated synthetic noise, or a strong BI-RADS-category baseline. These mechanisms imply different conclusions. It would not by itself show that “the intervention argument does not support deployment.”

Moreover, the paper already shows that maximal oracle correction harms performance. Merely reproducing fragility under stronger correction has low incremental value. The new contribution must isolate a mechanism or evaluate an observable intervention policy.

### 6. The endpoint needs tightening

AUROC alone does not capture the consequence of an interactive diagnostic tool. Prespecified endpoints should include paired change in AUROC with confidence intervals, sensitivity at a clinically chosen specificity (or vice versa), calibration/Brier score, and intervention burden. With only 98 malignant BrEaST cases, subgroup/scanner analyses and many policy variants will be exploratory and likely underpowered. “Crosses the clinician baseline” also needs a decision rule and uncertainty interval, not visual curve crossing.

## Prior-work delta after adversarial search

Source-supported interpretation: general CBM work already covers intervention counts, informed selection, granularity, and pitfalls (Shin et al., ICML 2023). Bunnell et al. already cover complete oracle correction at two strengths and demonstrate intervention distribution shift. The defensible delta is therefore narrow:

> In a public breast-ultrasound dataset with paired descriptor, category, and outcome labels, quantify whether an **observable** partial-intervention policy has any advantage over the recorded BI-RADS category, while separating oracle ceiling from simulated-noise sensitivity.

I did not verify a prior primary study performing exactly this paired analysis on BrEaST. That is not proof of novelty; a focused literature review remains required before a novelty claim.

## Easier version that preserves the question

### Recommended low-hanging-fruit formulation

**Question:** On BrEaST, how much malignancy information is available in the recorded BI-RADS descriptors relative to the recorded BI-RADS category, and how rapidly does that descriptor-based advantage degrade under explicitly synthetic partial/noisy replacement?

This is deliberately an **upper-bound and sensitivity analysis**, not a clinician-behaviour study.

Why it is easier:

- Data, descriptor labels, category, masks, outcome, and verification method already exist in one public table.
- No detector, segmentation model, GPU, or expert annotation is required for the first decisive result.
- A simple regularized concept-to-label model and an ordinal category baseline suffice; patient-level cases make the split unambiguous.
- The first result is the paired held-out comparison of ground-truth descriptor-only prediction versus category-only prediction. If descriptors cannot match category even at this oracle ceiling, an image-to-descriptor CBM is very unlikely to beat category through intervention.

Smallest decisive design:

1. Freeze patient-level development/test splits before comparison, stratified by malignancy and verification type. Do not use the published dataset as one undivided test set while tuning.
2. On development data only, fit a prespecified low-capacity descriptor-only model and category-only baseline. Treat the original multi-category descriptors as categorical; do not first collapse them into malignancy-indicative binaries unless that is a separate prespecified ablation.
3. On the untouched test set, compare AUROC, calibration/Brier score, and one fixed operating-point metric with paired bootstrap intervals.
4. Only if descriptor-only performance is competitive, run prespecified synthetic sensitivity curves: partial replacement and descriptor-specific corruption. Label these explicitly as simulations.
5. Report results separately for biopsy-verified and follow-up-verified cases as exploratory sensitivity analysis.

Decisive interpretations:

- **Descriptor-only is inferior to category-only even with recorded descriptors:** useful negative upper-bound result; stop before training an image CBM.
- **Descriptor-only matches/exceeds category-only:** justifies a later image-to-descriptor feasibility study, but does not validate human intervention.
- **Simulated corruption rapidly removes the advantage:** establishes sensitivity to stated assumptions, not observed clinician robustness.

Most dangerous confounds are small-sample optimism, differential verification, same-reader circularity, and label collapse that bakes malignancy direction into each “concept.” These should be primary limitations, not post hoc caveats.

### Slightly harder follow-up

If the upper-bound result is favorable, train a small image-to-descriptor model on BrEaST with frozen patient splits, compare an observable uncertainty-based intervention policy with random selection, and retain category-only as the baseline. This remains a feasibility experiment because 256 cases are unlikely to support a deployment claim. It should not reproduce the full Mask R-CNN pipeline unless lesion detection is itself part of the question.

### What would be required for the original claim

To restore “realistic clinician behaviour,” obtain either (a) a public multi-reader dataset containing descriptor disagreements/corrections, or (b) prospective reader-study data recording which model concepts readers inspect, change, and sometimes change incorrectly. Without that, revise the language to “simulated partial and noisy intervention.”

## Recommendation

Do not advance the BUS-BRA retraining plan. Revise around BrEaST as a cheap, confirmatory upper-bound study, explicitly separate observable policies from oracle diagnostics, and remove all claims about real clinician behaviour. Before a feasibility memo, verify TCIA access and conduct a focused primary-source novelty search for BrEaST descriptor/category prediction studies.

**ADVANCE TO REVISION**
