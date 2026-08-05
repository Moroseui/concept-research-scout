You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/003
Preserve existing files unless the task explicitly requires an update.
Do not claim novelty without verified primary sources.
Do not write code unless this is the probe_code stage and human approval exists.

===== CHARTER.md =====
# Research charter

## Central interest

Find clear, feasible, medically relevant research questions about **concepts in medical imaging**. Diagnosis, prognosis, representation analysis, concept reliability, concept intervention, and model auditing are all in scope. Concept-motivated segmentation correction remains a side project rather than the default main direction.

## Preferred opportunity pattern

Prioritize partially completed research stories where much of the groundwork already exists and one or two clean experiments could provide a meaningful conclusion. Examples:

- an existing method lacks an important evaluation;
- a claimed concept has not been causally validated;
- a public dataset already contains nearly all required labels;
- a paper leaves a precise future-work question;
- a simple baseline can test a widely assumed claim;
- a method has not been tested under a clinically relevant confound;
- a concept vocabulary exists but its faithfulness, leakage, stability, or utility is unknown.

## Desired project properties

- Easy to explain in one sentence.
- Interesting even to someone outside the immediate subfield.
- Publicly accessible data or already-confirmed access.
- Feasible for one researcher with Colab-class compute.
- Clear baselines and metrics.
- Positive and negative outcomes are both informative.
- Minimal need for new expert annotation.
- The first useful result can be obtained in days or a few weeks, not months.

## Current themes of interest

1. Reliability and causal validity of named concepts.
2. Specified versus discovered concepts in small medical datasets.
3. Concept leakage and hidden residual information.
4. Faithfulness of concept-mediated reasoning or explanations.
5. Concept stability across sites, modalities, acquisition shifts, and demographic groups.
6. Whether concept supervision improves calibration, robustness, or failure detection.
7. Low-cost audits of published concept-based models using existing datasets and checkpoints.

## Constraints

- Compute: Colab Pro+ or equivalent single-GPU sessions.
- No project should depend on unconfirmed DUA-gated data.
- No large-scale radiologist annotation campaign.
- Literature claims require primary-source verification.
- Do not treat report text, class labels, or segmentation labels as meaningful concepts without justification.
- Avoid architectural complexity unless the question requires it.
- Keep confirmatory and exploratory work separate.
- Never tune on the untouched test set.

## What counts as success

- A clear positive result.
- A clear negative result.
- Evidence that a popular assumption is unsupported.
- Identification of a decisive confound.
- A feasibility result that prevents wasted effort.
- A well-supported decision to advance, revise, pause, or reject an idea.


===== docs/COLLABORATOR_RULES.md =====
# Collaborator rules

## Role

Act as a critical research collaborator. Generate ideas, but spend at least as much effort trying to disprove or simplify them.

## Required distinctions

Always distinguish:

- verified fact;
- source-supported interpretation;
- inference;
- speculation;
- exploratory result;
- confirmatory result.

## Literature

- Use primary sources for medical, dataset, and method claims.
- Record DOI, PMID, arXiv ID, or official repository URL.
- Never claim novelty from memory alone.
- “I did not find it” is not proof that it does not exist.
- Identify the closest work and explain the exact delta.

## Idea generation

Prefer “one experiment away from a stronger story” over unconstrained novelty brainstorming.

For every idea, identify:

- the scientific uncertainty;
- the existing legwork already completed by others;
- the missing final step;
- why that step matters;
- the smallest decisive experiment;
- the most dangerous confound;
- why a negative result remains useful.

## Coding gate

Do not generate probe code until all are present:

- a reviewed idea card;
- a feasibility memo;
- a probe contract;
- explicit human approval.

## Experimental integrity

- Freeze splits before model comparison.
- Save configurations, seeds, environment, and per-case outputs.
- Use validation for development and preserve an untouched test set.
- Do not reinterpret an invalid run as a negative result.
- Report every authorized variant, not only the best one.
- Stop when the preregistered question is answered or the budget is exhausted.


===== docs/SCORING_RUBRIC.md =====
# Idea scoring rubric

Score each dimension from 1 to 5. Explain every score.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Clarity | vague | testable with refinement | one-sentence precise question |
| Medical relevance | cosmetic | plausible utility | clear meaningful consequence |
| Interest | routine | useful niche result | surprising or broadly compelling |
| Prior legwork | little exists | some reusable assets | data/code/labels/checkpoints largely ready |
| Feasibility | major barriers | manageable | first result in days |
| Data readiness | uncertain/restricted | accessible with work | public and directly usable |
| Evaluation readiness | unclear | custom metrics needed | accepted metrics and baselines exist |
| Negative-result value | low | diagnostic | directly resolves a live claim |
| Novelty confidence | likely covered | uncertain | precise verified gap |
| Regret | little concern | worth considering | obvious-in-hindsight opportunity |

## Priority score

Use a transparent weighted score, not a fake probability:

- 20% feasibility
- 15% prior legwork
- 15% medical relevance
- 15% interest
- 10% clarity
- 10% negative-result value
- 5% data readiness
- 5% evaluation readiness
- 5% novelty confidence

Regret is reported separately and must not override weak scientific value.


===== ideas/003/README.md =====
# Idea 003: Does BI-RADS concept intervention survive realistic clinician behaviour, and does it beat simply reading the BI-RADS category?

Selected from scouting cycle 001, candidate 4.


===== ideas/003/critique.md =====
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


===== ideas/003/debate.md =====
# Debate transcript



===== ideas/003/idea_card.json =====
{
  "id": "C4",
  "title": "Does BI-RADS concept intervention survive realistic clinician behaviour, and does it beat simply reading the BI-RADS category?",
  "question": "Does the reported gain from radiologist concept intervention in a breast ultrasound concept bottleneck model persist when interventions are partial, noisy, and clinician-selected rather than complete and oracle-correct, and does the intervened model outperform the trivial baseline of using the radiologist's own BI-RADS assessment directly?",
  "concept_definition": "A concept is a BI-RADS lexicon descriptor of a breast lesion as standardised by the American College of Radiology \u2014 shape, margin, orientation, echo pattern, posterior features and similar categorical descriptors. These are a formally defined, externally standardised clinical vocabulary with training and reporting requirements attached, which is a stronger justification for concept status than most vocabularies in this space. The final BI-RADS assessment category (2-5) is explicitly NOT a concept here; it is an outcome judgement and serves as the comparison baseline.",
  "medical_relevance": "Test-time intervention is the single most-cited clinical justification for concept bottleneck models: the radiologist can correct a wrong concept and improve the prediction. If the achievable gain is small, requires near-complete oracle correction, and is smaller than what the radiologist's unaided BI-RADS category already delivers, then the intervention argument does not support deployment and the field should stop offering it as one.",
  "closest_work": [
    {
      "citation": "Bunnell A., Glaser Y., Valdez D., Wolfgruber T., Altamirano A., Zamora Gonzalez C., Hernandez B.Y., Sadowski P., Shepherd J.A. Learning a Clinically-Relevant Concept Bottleneck for Lesion Detection in Breast Ultrasound.",
      "identifier": "arXiv:2407.00267; MICCAI 2024; code at https://github.com/hawaii-ai/bus-cbm; CC BY 4.0",
      "source_type": "conference paper + official repository",
      "verification": "verified_by_primary_fetch of the arXiv abstract page",
      "what_it_establishes": "A BI-RADS concept bottleneck model developed on 8,854 images from 994 women with expert annotations and histological cancer labels, and the specific headline claim that 'concept intervention is shown to increase performance from 0.876 to 0.885 area under the receiver operating characteristic curve'. Training and evaluation code is public.",
      "exact_delta": "The reported gain is 0.009 AUC. The paper demonstrates that intervention is possible and directionally positive under what is almost certainly an oracle protocol \u2014 all concepts replaced with ground truth. What is absent is any characterisation of the gain under the conditions a radiologist would actually create: correcting one or two descriptors they happen to disagree with, sometimes incorrectly, and choosing which to correct non-randomly. Also absent is a comparison against the clinician's own assessment, which is the real-world alternative to the model."
    },
    {
      "citation": "Gomez-Flores W., Gregorio-Calas M.J., de Albuquerque Pereira W.C. BUS-BRA: A breast ultrasound dataset for assessing computer-aided diagnosis systems.",
      "identifier": "Medical Physics 51:3110-3123 (2024); DOI 10.1002/mp.16812; data at Zenodo record 8231412; CC BY 4.0",
      "source_type": "journal + open data repository",
      "verification": "verified_by_search_summary_only (Zenodo record ID, DOI, and license consistently reported across multiple sources; the record itself was not opened)",
      "what_it_establishes": "1,875 anonymised images from 1,064 patients across four scanners, biopsy-proven tumours (722 benign, 342 malignant), BI-RADS categories 2-5, and ground-truth lesion delineations, under CC BY 4.0.",
      "exact_delta": "Supplies a public, biopsy-proven, multi-scanner evaluation set with the radiologist's BI-RADS category \u2014 precisely what is needed for the baseline comparison. Whether it also carries the per-lesion BI-RADS descriptors needed for the intervention arm is unresolved and is this candidate's main risk."
    },
    {
      "citation": "Post-Hoc Explainability of BI-RADS Descriptors in a Multi-task Framework for Breast Cancer Detection and Segmentation.",
      "identifier": "arXiv:2308.14213",
      "source_type": "preprint",
      "verification": "verified_by_search_summary_only",
      "what_it_establishes": "Related BI-RADS descriptor modelling in a multi-task rather than bottleneck framing.",
      "exact_delta": "Post-hoc rather than interventional; does not address intervention robustness."
    }
  ],
  "existing_legwork": [
    "Training and evaluation code for the target model is public under CC BY 4.0 (github.com/hawaii-ai/bus-cbm).",
    "The headline intervention number to be stress-tested is published and precise (0.876 to 0.885).",
    "A public, biopsy-proven, multi-scanner breast ultrasound dataset with BI-RADS categories exists under CC BY 4.0 with a permanent Zenodo record.",
    "Intervention protocols (random-order, uncertainty-ordered, group-wise) are established in the general CBM literature and need no invention."
  ],
  "missing_step": "An intervention-response curve rather than a single oracle point. Specifically: AUC as a function of the number of concepts corrected, under (i) random selection, (ii) clinician-plausible selection biased toward visually salient descriptors, and (iii) imperfect correction where the intervening reader is themselves wrong at a realistic rate; all plotted against the horizontal line representing the radiologist's own BI-RADS category performance.",
  "why_it_matters": "A 0.009 AUC oracle gain is the ceiling of the intervention benefit, not its expected value. If the realistic-conditions curve is flat or crosses below the clinician baseline, the central deployment argument for medical CBMs loses its main empirical support in the one modality where it has been most concretely demonstrated.",
  "dataset": {
    "primary": "BUS-BRA (Zenodo 8231412, CC BY 4.0) for the external and baseline arms",
    "secondary": "BUSI (public) as an additional external set",
    "unavailable": "The authors' own 8,854-image development cohort is not public, so their exact model cannot be reproduced end to end; only their released code and architecture can be reused with retraining.",
    "access_risk": "Moderate. The datasets are open, but the training cohort is not, so this becomes a retrain-and-replicate study rather than a checkpoint audit.",
    "blocking_uncertainty": "Whether BUS-BRA provides per-lesion BI-RADS descriptors or only the BI-RADS assessment category. Sources consistently describe 'BI-RADS categories 2, 3, 4, and 5', which suggests category only. If descriptors are absent, the intervention arm cannot run on BUS-BRA and this candidate must be rescoped."
  },
  "compute_readiness": "Retraining a BUS CBM on ~1,875 images is Colab-feasible. The intervention sweep is inference-only and cheap. Total well within a single-GPU budget.",
  "minimal_experiment": "Resolve the blocking uncertainty first by inspecting the BUS-BRA record for descriptor-level fields \u2014 this is a one-hour check that determines whether the candidate proceeds. If descriptors exist: retrain the released bus-cbm architecture on frozen BUS-BRA splits, then produce the intervention-response curve across the three protocols above with the clinician BI-RADS-category baseline overlaid, reporting every authorised protocol rather than the best. If descriptors do not exist: the candidate reduces to the baseline comparison alone (does the CBM beat the radiologist's recorded BI-RADS category on biopsy-proven outcomes), which is still worth something but is a materially weaker story and should be rescored.",
  "critical_confound": "Concept-set redundancy. If several BI-RADS descriptors carry overlapping information about malignancy, correcting any one of them moves the prediction very little, and a flat intervention curve would reflect vocabulary redundancy rather than a failure of the intervention mechanism. This must be measured directly \u2014 pairwise concept mutual information and a leave-one-concept-out analysis \u2014 and reported alongside the curve, or the negative result will be misattributed.",
  "secondary_confound": "Scanner and site shift. BUS-BRA spans four ultrasound scanners; a model retrained on it and evaluated across scanners may show intervention effects that are really domain-shift effects. Splits should be stratified by scanner and a per-scanner breakdown reported.",
  "risky_assumption": "That the original 0.876 to 0.885 gain was measured under an oracle full-replacement protocol. The abstract does not state the protocol. If the authors already used a partial or realistic protocol, the delta of this candidate shrinks substantially. This must be read from the full paper before committing.",
  "positive_interpretation": "A characterised intervention-response curve, showing how much correction is needed for how much benefit relative to the clinician's own judgement, is directly actionable for anyone designing a concept-based clinical interface.",
  "negative_interpretation": "If the gain is robust and exceeds the clinician baseline even under noisy partial intervention, that materially strengthens the deployment case for BI-RADS CBMs and is a useful confirmatory result.",
  "why_negative_is_useful": "The clinician-baseline comparison is informative regardless of the intervention findings, so the study yields something even if the intervention arm is inconclusive.",
  "scores": {
    "clarity": {
      "value": 4,
      "why": "The question is precise but has two parts (robustness and baseline comparison) that could be separated."
    },
    "medical_relevance": {
      "value": 5,
      "why": "Directly tests the main clinical selling point of concept bottleneck models, against a biopsy-proven endpoint."
    },
    "interest": {
      "value": 4,
      "why": "'The interpretability feature everyone advertises is worth 0.009 AUC under ideal conditions' is a pointed framing, though narrower than C2 or C3."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Public code, a precise published claim, and an open biopsy-proven evaluation set \u2014 but no public training cohort and no released checkpoint."
    },
    "feasibility": {
      "value": 3,
      "why": "Requires retraining rather than auditing, and is gated on an unresolved question about descriptor availability in BUS-BRA."
    },
    "data_readiness": {
      "value": 3,
      "why": "Both candidate datasets are openly licensed, but the specific labels the intervention arm needs are unconfirmed."
    },
    "evaluation_readiness": {
      "value": 4,
      "why": "AUC, intervention curves, and a clinician baseline are all standard; only the realistic-intervention protocol needs specification."
    },
    "negative_result_value": {
      "value": 5,
      "why": "A flat realistic-intervention curve would directly undercut a headline claim in a MICCAI paper and the field's general argument."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Intervention-robustness studies exist in the general CBM literature; whether one covers this medical setting was not checked."
    }
  },
  "priority_score": 3.95,
  "priority_arithmetic": "0.20*3 + 0.15*4 + 0.15*5 + 0.15*4 + 0.10*4 + 0.10*5 + 0.05*3 + 0.05*4 + 0.05*3 = 3.95",
  "regret": {
    "value": 3,
    "why": "Worth doing, but the retraining requirement and the descriptor uncertainty make it less of an obvious missed opportunity than C1-C3."
  },
  "unverified_claims": [
    "BLOCKING: whether BUS-BRA contains per-lesion BI-RADS descriptors or only the assessment category. All sources describe categories 2-5 only, which points toward category-only. Must be resolved by opening Zenodo record 8231412 before any other work.",
    "The intervention protocol used to produce 0.876 to 0.885 was not stated in the abstract and is assumed to be oracle full-replacement. This assumption underpins the entire candidate and must be read from the full MICCAI paper.",
    "The exact BI-RADS descriptors used in the bottleneck layer were not enumerated in the abstract.",
    "The BUS-BRA Zenodo record ID, DOI, license, and case counts are from search summaries; the record was not opened.",
    "Whether a released checkpoint exists in github.com/hawaii-ai/bus-cbm (as opposed to training code only) was not checked, and materially affects feasibility."
  ],
  "recommendation": "REVISE",
  "revision_note": "Resolve the BUS-BRA descriptor question and the original intervention protocol first. If descriptors are absent, rescope to the clinician-baseline comparison and rescore; if the original protocol was already realistic, drop the candidate."
}


===== STAGE TASK =====
Attack the idea. Append one round to `debate.md` in the idea folder.

Format your append exactly as:

```
## Round N — CRITIC

**Position:** [one sentence: what you think is wrong]

**Argument:** [the reasoning, with specifics — dataset, metric, prior paper,
mechanism. Not "this may be difficult."]

**What would change my mind:** [a concrete thing the proposer could show]

**Status:** OPEN | CONCEDED | IRREDUCIBLE DISAGREEMENT | CONVERGED
```

Rules:

- Read every prior round. Do not repeat an objection already answered — if
  the proposer's rebuttal was adequate, write CONCEDED and say which argument
  moved you and why.
- Concede only in response to an *argument*, never to insistence or repetition.
  If the proposer restated their claim more confidently without new evidence,
  say so and hold your position.
- One objection per round, your strongest remaining one. Do not spray.
- If you and the proposer have a real difference of judgement that no
  available evidence can settle, write IRREDUCIBLE DISAGREEMENT and name the
  experiment or fact that *would* settle it. This is a good outcome, not a
  failure.
- Write CONVERGED only if you now think the idea is sound AND you have no
  remaining objection worth stating.
- Append only. Never edit earlier rounds.



===== DEBATE STATE =====
You are codex. Your interlocutor is claude.
This is round 1. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript


