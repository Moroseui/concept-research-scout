FATAL OBJECTION: The historical pre-correction masks are unavailable, so rerun–ground-truth agreement cannot measure an “uncorrected fraction,” and predictions agreeing with the rerun where the released label rejected it cannot identify inheritance through the released label.
EVIDENCE: ISLES'24 paper, arXiv:2408.10966v1, Dataset section; DeepISLES, DOI 10.1038/s41467-025-62373-x; ideas/029/keystone_screen.md §4.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial critique

## 1. The keystone is true, but it is not the keystone the claim needs

The screen correctly verified a useful operational fact: a public DeepISLES implementation can be run on released follow-up DWI/ADC, and its output can be compared voxelwise with the released mask in `space-ncct`. That establishes that a **present-day surrogate output** is computable. It does not establish that the historical draft is recoverable.

The ISLES'24 paper says only that masks were “derived from DWI images using the ISLES'22 ensemble algorithm” and that quality control and correction were performed “when needed” (arXiv:2408.10966v1). It does not identify a commit, weights, input channels, inference settings, native-space preprocessing, threshold, postprocessing, or registration path. The screen itself found two material mismatches: the released follow-up images are already resampled into NCCT space, and follow-up FLAIR—used by the released full ensemble—is absent. The cited weights were published on 2024-11-01, after the ISLES'24 preprint and dataset construction. This does not prove that they differ from the historical weights, but it makes identity unverified.

Therefore `D` is not “the draft”; it is **a rerun of a related released system under a different observable input path**. Calling `D xor G` “the correction field” is false. It mixes human correction, model/version differences, missing FLAIR, resampling, registration, thresholding, and postprocessing. The card acknowledges most of these as depressing agreement, but asymmetric interpretation does not restore the missing estimand.

Most importantly, even a bitwise-identical `D` and `G` does not show that a mask was “uncorrected.” A reviewer may have inspected and accepted it, altered it and happened to produce the same raster, or corrected only regions on which the surrogate rerun also agrees. Conversely, disagreement does not show correction. The proposed “uncorrected fraction” is therefore not observable from the released artifacts. This is an identifiability failure, not merely reduced power.

## 2. Stage 2 reverses the causal logic of label inheritance

The card proposes restricting analysis to voxels where surrogate draft `D` and released label `G` disagree. It then says that an ISLES-trained model “siding with D” there indicates inherited draft conventions. But at precisely those voxels, the model's supervised target was `G`, not `D`. If the historical draft really was corrected from `D` to `G`, the draft signal was removed from the training label at those locations. Agreement with `D` against `G` is a held-out labeling error, not evidence that the model inherited `D` **through the labels**.

Several simpler explanations remain:

- `D` and the acute-CT model can share generic segmentation priors: smooth boundaries, minimum lesion sizes, connectedness, or class-imbalance behavior.
- `D` can be closer than `G` to the lesion geometry predictable from acute CT even when `G` is the more accurate follow-up-MRI delineation.
- `D-G` voxels are selected to be ambiguous or difficult; matching on local intensity, distance to boundary, or uncertainty cannot exhaust their biological and treatment-dependent differences.
- A prediction can agree with `D` after thresholding because of calibration or operating-point choice rather than a learned boundary convention.

The proposed external model does not solve this. It would need the same prediction task, acute modalities, preprocessing, thresholding, cohort support, and performance, while differing only in exposure to ISLES'24 labels. No such model is identified. A model trained on another cohort has different labels, case mix, treatment distribution, scanner distribution, and inductive biases; a difference in draft-siding is multiply confounded. A randomly initialized versus pretrained comparison would not isolate label exposure either.

The only region where label inheritance is mechanically plausible is where historical draft and final mask agree. There, however, draft convention, expert endorsement, and tissue truth are observationally inseparable. Without the actual draft plus an independent de-novo annotation or randomized annotation protocol, the proposed data cannot separate “algorithmic fingerprint” from correct lesion morphology.

## 3. The endpoint is undefined and partly circular

“Boundary conventions” is not operationalized. Dice, bitwise equality, and surface distance quantify agreement; they do not identify smoothness, small-lesion suppression, inclusion habits, or any other named convention. The card needs prespecified features with distinct predictions—for example curvature spectrum, component-size distribution, hole filling, or topology—and an analysis showing that these features are not simply consequences of lesion size, image resolution, or thresholding. At present, a high Dice would be relabeled as “fingerprint” after observing it.

There is also concept-label circularity in the proposed biological contrast. The study has no independent voxelwise “tissue-fate evidence” against which draft convention can be opposed: `G` is the very hybrid label under audit, and `D` is derived from the same follow-up DWI/ADC. Acute CT is not a voxelwise adjudicator of the final post-treatment lesion. Thus “conventions rather than tissue-fate evidence” is not an empirical contrast supplied by this design.

The rung definitions do not repair this. Replication across two acute-CT model families or centers reproduces an association; it does not identify its source. Rung 1 is therefore not reachable by the specified experiment, and rung 2 merely repeats the same non-identifying design.

## 4. Relevance, negative-result value, and cost are overstated

A direct audit of machine-initialized benchmark labels would be relevant to medical-imaging AI. This design cannot deliver that audit. Its clean result is only agreement between one current DeepISLES execution and released masks. Given that the masks were derived using a related high-performing model on the same follow-up modalities, substantial agreement is expected and medically unsurprising. Low agreement is uninterpretable because of the documented execution-path drift. Neither result establishes benchmark contamination, annotation quality, automation bias, or consequences for deployment.

The negative-result language is especially too strong. A stage-2 null could arise from weak subject-model performance, few informative disagreement voxels, surrogate-draft drift, thresholding, insufficient power, or a mismatched external control. It would not reassure the community that the hybrid pipeline “did not measurably contaminate model behavior.” The anticipated negative is therefore sensitivity-limited to uninterpretable, not score 4 under the rubric.

The cost estimate also omits material work. The training archive is approximately 99 GB in the current repository evidence, the DeepISLES weights are about 9.1 GB, the full ensemble's required FLAIR is absent, and stage 2 requires training and selecting a model on only 149 released cases while preserving an untouched patient-level test set. “Nothing must be built except analysis” conflicts with the card's own requirement to train nnU-Net and locate, validate, and harmonize an external control. Stage 1 may fit the stated GPU envelope, but stage 2 is not a two-week plug-in analysis until the subject and control models, split, power, and pipeline are specified.

## 5. Prior work and novelty

The primary DeepISLES paper reports a strong, clinically validated ensemble and even that neuroradiologists preferred its segmentations to manual annotations in a Turing-like test (DOI 10.1038/s41467-025-62373-x). That makes agreement with a DeepISLES-derived label less diagnostic of a harmful “fingerprint”: it may reflect a good segmenter. General annotation-noise and annotator-preference methods are adjacent, as the card states, but they do not validate this causal design.

A bounded search found work on AI-assisted labeling and automation bias, including AI-collaborative voxelwise annotation with quality assurance (Radiology: Artificial Intelligence 2023, DOI 10.1148/ryai.220105) and prospective automation-bias experiments in mammography (Radiology 2023, DOI 10.1148/radiol.222176). These establish that machine assistance can affect human review and that machine prelabels are a legitimate governance concern. They do not establish that ISLES'24 corrections were anchored, nor did I locate a primary study auditing the historical ISLES'24 drafts. “Not located” is not proof of novelty. More importantly, the candidate fails on identifiability before novelty becomes decisive.

## 6. Leakage and split integrity

Stage 1 has no train/test leakage problem because it is a label-provenance description. Stage 2 does. The card proposes training on 149 cases and analyzing held-out disagreements but gives no frozen patient-level split, no minimum number of cases or disagreement voxels, and no rule for selecting the subject model without consuming the analysis set. Hyperparameters, thresholds, and convention definitions could easily be tuned toward `D-G` after viewing all masks. A revision would need a three-way split or nested cross-fitting, precomputed power based only on development data, and an untouched test set. Those safeguards still would not fix the causal objection above.

## 7. Plain-pitch fidelity

**Named defect: the pitch turns a surrogate-agreement study into direct recovery of annotation history.** “We can redraw every answer and measure exactly how much of the official truth is uncorrected machine output” is stronger than the technical card and contradicted by its residual assumption. The actual historical draft is not released; exact correction status is not inferable from equality with a later rerun. “Then test whether models … learn the drafting algorithm's habits instead of the biology” also drops the card's acknowledged shared-inductive-bias and anchoring limits and asserts a dichotomy the experiment cannot adjudicate. The pitch's “either result matters” likewise omits that low agreement is explicitly ambiguous. These are material overclaims, not harmless simplification.

## 8. Low-hanging fruit and the easiest defensible version

The low-hanging computation is a **reproducibility/agreement census**: run the available DWI/ADC-compatible DeepISLES path on the 149 public cases and report agreement with `G`, stratified by center, lesion size, and boundary distance. The data, labels, container/code, weights, and standard metrics already exist. It must be described only as agreement with a version-pinned surrogate, not an uncorrected fraction or correction field. Because high agreement is expected and low agreement is ambiguous, that census alone is probably too weak for a full candidate; it is useful Stage-0 evidence or a data note, not the card's high-value result.

The genuinely high-value, easier experiment becomes possible if the organizers release the **actual pre-correction masks and exact generation provenance**. Then no acute-CT model is needed initially. Directly quantify which voxels and lesions were changed; characterize edit types; and measure how official metrics and method rankings change when the reference is the draft versus the corrected mask. If archived participant outputs are unavailable, evaluate at least released top methods or frozen cross-validated baselines. An independently de-novo annotated subset would further separate accepted-correct draft from reviewer anchoring, but it is not required for the narrower descriptive question “what was changed and did it matter to benchmark scores?” This is cheaper, more identifiable, and more consequential than the proposed model-behavior stage.

It is worth asking the organizers for those artifacts. Until they exist, the high-value study is paused by data access; substituting a contemporary rerun changes the estimand and does not answer it.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Using the exact archived pre-correction DeepISLES masks, which lesion and boundary edits did supervised review make, and how much do those edits change ISLES'24 model scores and rankings?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—if the historical drafts and provenance are obtained, because it directly measures human correction and its benchmark consequence without pretending that surrogate agreement reveals annotation history.
