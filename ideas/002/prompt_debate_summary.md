You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/002
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


===== ideas/002/README.md =====
# Idea 002: Dermoscopic concepts predicted from non-dermoscopic photographs: genuine visibility or shortcut?

Selected from scouting cycle 001, candidate 3.


===== ideas/002/critique.md =====
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


===== ideas/002/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The idea's claimed missing experiment is not missing: clinical-only and dermoscopic-only prediction of all seven Derm7pt checklist categories has already been reported, so the proposal as written is primarily a replication built on a false novelty premise.

**Argument:** Kawahara et al., the original Derm7pt dataset paper (DOI: 10.1109/JBHI.2018.2824327), explicitly evaluated separate clinical-only (`xc`) and dermoscopic-only (`xd`) models on the official split and reported accuracy for every checklist category in Table II; clinical-only mean checklist accuracy was 64.1% and dermoscopic-only mean accuracy was 72.5%. Zhang et al. (arXiv:2409.12390) subsequently reported clinical-only, dermoscopic-only, and metadata-only results for diagnosis and every checklist category in Table 6. Thus arms (a) and (b), which the card calls the missing per-concept, per-modality breakdown, repeat established experiments. The diagnosis-only arm is a potentially useful new predictive baseline, but it cannot rescue the stated question or its decision rule: exceeding an oracle-diagnosis predictor does not establish that the named dermoscopic structure is visible, because residual performance can arise from recorded or unrecorded correlates such as age, anatomical site, elevation, acquisition source, background, or disease subtype. The defensible remaining project is therefore a narrower audit of incremental label predictability conditional on diagnosis and metadata, not a test of genuine visibility.

**What would change my mind:** Show primary-source evidence that an existing study has not already tested the exact nested comparison of diagnosis-plus-recorded-metadata versus diagnosis-plus-recorded-metadata-plus-clinical-image on the untouched original Derm7pt cohort, then revise the primary question and endpoint to that incremental predictive value without interpreting it as proof of named-feature visibility.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card's declared missing step — a per-concept, per-modality breakdown — already exists in the primary literature, including in the dataset paper itself, so arms (a) and (b) are replication; and the proposed decision rule, "clinical-image performance above an oracle-diagnosis predictor means the named structure is genuinely visible," does not license that conclusion, because the residual can come from any correlate the diagnosis-only baseline omits.

**Response:** CONCEDE

**Argument:** Both parts of the objection are correct, and I have no counter-evidence.

On the novelty premise: the card asserts that "the literature reports fused performance" and that isolating each modality per concept is missing. That assertion is false against the primary source it cites. Kawahara et al. trained separate single-modality inference paths and report clinical-only and dermoscopic-only accuracy for every checklist category on the official split (DOI: [10.1109/JBHI.2018.2824327](https://doi.org/10.1109/JBHI.2018.2824327), Table II; author-hosted [PDF](https://www.cs.sfu.ca/~hamarneh/ecopy/jbhi2018a.pdf)), and Zhang et al. report the same breakdown plus a metadata-only row (arXiv: [2409.12390](https://arxiv.org/abs/2409.12390), Table 6). The card itself listed this as its decisive unverified claim; verification came back against it. The only defence available to me is that Kawahara reports accuracy rather than per-concept AUROC, which under this label imbalance is a weak discriminator. That is a metric-reporting gap, not a scientific one — the experiment was run and the qualitative answer (clinical photographs carry substantial checklist-label signal, less than dermoscopy) is already on record. Recomputing it in AUROC does not constitute the missing final step the charter asks for.

On the decision rule: an oracle-diagnosis predictor is privileged information, not a mediator. Exceeding it does not isolate visible dermoscopic structure, and failing to exceed it does not show the image model is running on diagnosis. Since the card designates control (c) as the decisive readout and states that any version lacking it "is not worth running," the failure of the rule removes the endpoint, not a detail. Combined with the false novelty premise, nothing of the original question — "genuine visibility or shortcut?" — survives as stated. What is lost is the entire framing: the paired design still controls lesion identity, but it never gave grounding evidence, only a cleaner predictive comparison.

Two further points, offered against my own idea rather than in its defence. First, the salvage the critic allows — incremental predictive value of the clinical image over diagnosis plus recorded metadata — is not established as novel either. Neither of us has searched for it; "I did not find it" would not be evidence, and no novelty claim should be attached to it without a primary-source search. Second, that salvage inherits the card's unresolved annotation-provenance risk: if the annotating dermatologist saw the clinical image or clinical context when assigning checklist criteria, a non-zero residual is expected by construction and the audit measures annotation practice as much as image content. That must be traced to a primary source or recorded as a hard interpretive limit before the narrower version is worth costing.

**Spin-off (not a defence of the original, recorded only so it is not lost):** the metric gap noted above suggests a separate, cheaper question — whether published Derm7pt per-concept accuracies are distinguishable from majority-class prediction for the rarer criteria, i.e. whether the modality comparison in the literature rests on a metric that hides class imbalance. That is an audit of existing reported numbers, not a new training run, and it does not rescue this card.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposed conditional-predictability salvage is not interpretable until the checklist-label annotation protocol is established, because the clinical image may have been part of the process that produced the target labels.

**Argument:** The revised nested comparison would estimate whether a clinical image improves prediction of the recorded checklist label beyond diagnosis and metadata, but its scientific meaning depends on how that label was assigned. Kawahara et al. state that a dermatologist assigned diagnosis and checklist categories, yet the inspected methods do not establish whether checklist scoring was blinded to the paired clinical photograph, clinical context, pathology, or diagnosis. If the scorer saw the clinical photograph or contextual information, then incremental clinical-image signal can reflect information deliberately or inadvertently incorporated into the annotation rather than an independently defined dermoscopic criterion; the experiment would partly recover the annotation workflow it is supposed to audit. Conversely, if criteria were scored from dermoscopy alone under modality blinding, the same residual is substantially more informative as cross-modality covariation. Adjusting for diagnosis, age, sex, location, and elevation cannot repair this ambiguity because annotation exposure is a target-construction issue, not an observed confound. Thus even the narrowed study should not proceed to image training merely because the tabular gate shows within-diagnosis variation: without provenance, a positive result has two materially different explanations that Derm7pt itself cannot separate.

**What would change my mind:** Provide a primary-source annotation manual, Atlas/database protocol, or written confirmation from the dataset creators showing which images and clinical variables the checklist annotator could see when assigning each criterion; if that cannot be obtained, add an independent blinded rescoring study on a small prespecified subset or restrict the project to a descriptive dataset-label audit with no grounding or cross-modality-visibility interpretation.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The salvage measures whether a clinical photograph adds information about the *recorded* checklist label, and the meaning of any residual depends on whether the person who recorded that label could see the clinical photograph. If they could, the residual is partly annotation practice rather than cross-modality covariation; adjusting for diagnosis and metadata cannot fix this because it is a property of how the target was constructed, not an observed confound. Derm7pt cannot separate the two explanations, so the narrowed study should not proceed to image training.

**Response:** AMEND

**Argument:** I accept the premise and the first conclusion, and I contest only the last clause.

**On the premise — I tried to resolve it and failed.** I attempted primary-source verification during this round. The dataset site's welcome page states only that the database "includes over 2000 clinical and dermoscopy color images, along with corresponding structured metadata" and contains no annotator, modality-exposure, or blinding statement ([derm.cs.sfu.ca](https://derm.cs.sfu.ca/Welcome.html)). Secondary dataset-index pages likewise carry no annotation methodology. The cases derive from the Interactive Atlas of Dermoscopy (Argenziano et al., 2000, EDRA), a book-plus-CD-ROM product whose per-case scoring protocol I could not obtain in any open primary form; the accessible literature about it is review coverage of the CD-ROM's contents, not a methods section. Text extraction from the author-hosted JBHI PDF failed in this environment, so I cannot add anything beyond the single sentence the critique already records — a dermatologist assigned diagnosis and checklist categories, with no stated blinding. **Verified fact:** the annotation protocol is not documented in any openly accessible primary source I could reach. **Not established:** that it is undocumented anywhere; the Atlas CD-ROM itself and the dataset creators remain unqueried. That distinction matters, because a single email to the derm7pt authors is a cheap, non-speculative way to close this, and it should be an explicit prerequisite rather than a background hope.

**What I concede.** The two explanations — annotation exposure versus genuine cross-modality covariation — are not separable inside Derm7pt, and I have no discriminating test. I looked for one and found nothing usable: both hypotheses predict the same pattern across criteria, background-versus-lesion crops separate provenance from lesion signal but not annotation from covariation, and there is no second cohort with 7-point checklist criteria scored under known modality blinding to test transfer against (the clinical-photo concept datasets — SkinCon over Fitzpatrick17k/DDI — use clinical descriptors, not the dermoscopic checklist). The only in-house separator is blinded rescoring of a prespecified subset by a dermatologist who sees the dermoscopic image alone, which is exactly the expert-annotation cost the charter asks me to avoid, and which would also be measuring a different annotator than the original one.

**What this costs the idea, stated plainly.** The card's stated positive-direction payoff — "it identifies which dermoscopic criteria have clinical-photograph correlates, which is directly relevant to teledermatology triage design" — does not survive. Under the annotation-exposure explanation, an apparent correlate is an artifact of how one atlas was scored and gives no reason to expect it in a new cohort, so the constructive teledermatology reading is withdrawn, not weakened. Combined with round 1, the card retains neither its original framing nor its constructive alternative. That is the second structural loss, and I am not going to dress it up: this is now a dataset-label audit, and its medical-relevance and negative-result-value scores (4 and 4) are no longer defensible at those values.

**Where I still differ, and why it is not a restatement.** The critic's objection bars an *interpretation*; it does not bar the *measurement*, and the critic's own fallback concedes this by permitting "a descriptive dataset-label audit." The amended endpoint is a property of the dataset, not of visibility:

> Are the recorded Derm7pt checklist labels conditionally independent of the paired clinical photograph given diagnosis and recorded metadata?

Measuring that requires the image arm — the image is the variable being conditioned on — so "do not proceed to image training" is the one clause I reject. What the tabular gate licenses is not an interpretation, it is a power check: whether enough within-diagnosis label variation exists for the conditional-independence test to be estimable at all. And a rejection of conditional independence is decision-relevant to the Derm7pt concept-bottleneck literature under *both* explanations, which is why the unresolved ambiguity does not void it: if the labels carry clinical-photo information, then papers training dermoscopic concept bottlenecks on them and reporting concept faithfulness are working with targets of uncertain modality provenance either way. The two explanations then partition the follow-up (fix the dataset's documentation, or study the cross-modality correlate), not the finding.

**Concrete amendment.** (1) Primary question replaced by the conditional-independence statement above. (2) Both explanations reported as jointly exhaustive and unseparated, in the results, not the limitations. (3) Teledermatology triage-design interpretation deleted. (4) Written provenance enquiry to the derm7pt authors and, if reachable, the Atlas authors, recorded as a prerequisite with its outcome logged either way; if it returns "scorer saw both images," the audit becomes a documentation finding and the image arm is not worth running. (5) If provenance is unobtainable and the tabular gate shows adequate within-diagnosis variation, the honest recommendation is PAUSE rather than advance — the measurement is estimable but its value is contingent on an answer only the dataset owners hold.

**Status:** CONVERGED

## Round 3 — CRITIC

**Position:** The amended endpoint overclaims what the proposed nested prediction experiment can establish: with roughly 1,000 cases and a high-dimensional image, it cannot test conditional independence, only whether one prespecified image model improves prediction over one prespecified covariate model.

**Argument:** The hypothesis written as “the recorded Derm7pt checklist labels are conditionally independent of the paired clinical photograph given diagnosis and recorded metadata” is a distributional claim, but the proposed evidence is a comparison between fitted predictors. If covariates-only and covariates-plus-image models perform similarly, that may reflect low power, optimization failure, inappropriate image inductive bias, rare checklist classes, or an overly strong/weak covariate learner rather than conditional independence. If the image model improves, the result supports incremental predictive value only relative to that model class and evaluation loss; it still does not constitute a general rejection of conditional independence unless the test has controlled type-I error and adequate power against prespecified alternatives. Derm7pt makes this distinction consequential: after excluding four missing clinical photographs, the fixed split leaves only about 400 test cases, while five checklist criteria are multiclass and some classes and diagnosis-conditioned strata are sparse. Macro AUROC/F1 differences with bootstrap intervals do not solve this identification problem, and “no improvement” cannot support independence without a prespecified equivalence margin tied to a medically or scientifically meaningful effect. The defensible question is therefore narrower: whether adding the clinical image improves out-of-sample log loss (or another prespecified proper score) over a locked diagnosis-plus-metadata baseline by at least a prespecified margin. That remains a useful dataset audit, but it is not a conditional-independence test as currently stated.

**What would change my mind:** Specify a statistically valid conditional-independence testing procedure for mixed categorical covariates and high-dimensional images, demonstrate by split-respecting simulations calibrated to Derm7pt’s class counts that it controls type-I error and has useful power for prespecified effect sizes, and define an equivalence margin for any independence-like negative conclusion; otherwise rename the endpoint as model- and metric-conditional incremental predictive value.

**Status:** OPEN

## Round 3 — PROPOSER

**Responding to:** The endpoint is written as a distributional claim — conditional independence of the checklist label and the clinical photograph given diagnosis and metadata — but the proposed evidence is a difference between two fitted predictors. Similar performance can come from low power, a bad encoder, sparse classes, or a mis-specified covariate learner rather than independence; better performance licenses only "this model class improves this loss." With ~400 test cases, sparse multiclass criteria, and small diagnosis-conditioned strata, bootstrap intervals on macro AUROC do not repair this, and no independence-like negative conclusion is admissible without a prespecified equivalence margin. Either supply a valid test with demonstrated type-I control and power, or rename the endpoint model- and metric-conditional incremental predictive value.

**Response:** AMEND

**Argument:** The objection is right about the negative direction and about my evaluation plan. It is wrong about one thing, and that thing is the crux: a valid finite-sample conditional-independence test does exist here, because the conditioning set is **low-dimensional and discrete**. The high-dimensional variable is the one being conditioned *on* as a predictor, not the one whose conditional law must be modelled.

**The procedure.** Let Y be one prespecified checklist criterion, X the clinical photograph, Z a discrete conditioning vector. Under H₀: Y ⟂ X | Z, the case-to-image assignment is exchangeable **within each level of Z**. So: permute clinical images among cases inside each Z-stratum, recompute any statistic, and compare the observed value to its permutation distribution. This is the standard stratified/conditional permutation test for discrete Z. It requires no asymptotics, no model of X | Z, and no assumption that the predictor is well specified — type-I error is controlled **by construction** at any sample size, because exchangeability under H₀ is exact rather than estimated. The rule I need is the one the critic implicitly separates and I should have separated in round 2:

- **Validity is model-free.** Any statistic is admissible; the model is only the statistic. Because encoder features are a deterministic function of the image, permuting cases permutes images, so a rejection rejects the hypothesis about the *photograph*, not merely about a feature vector.
- **Power is model-dependent.** A weak encoder, an over-strong covariate learner, or a rare class costs sensitivity only. Every failure mode the critic lists — optimisation failure, wrong inductive bias, sparse classes — lands entirely on power. None of them can manufacture a false rejection.

**Making it affordable, which matters because permutation needs B refits.** Use a label-free pretrained encoder, extract features once for all 1,007 cases (the encoder never sees Y, so no refitting per permutation and no leakage), and let the statistic be the cross-validated log-loss improvement of a penalised head on [Z, features] over the same head on [Z] alone, with folds and hyperparameter grid frozen before unblinding. Then B = 2,000 permutations is seconds of CPU, not GPU-hours. This also removes the "~400 test cases" bottleneck: the permutation test is run once on the development portion under a preregistered specification, with the official test set touched only for a single confirmatory replication of an already-frozen statistic, if at all.

**The calibration check I commit to, and why it is a check rather than a derivation.** I will run split-respecting null simulations at Derm7pt's real class counts — synthetic Y drawn from Z alone, real images attached — and verify the rejection rate is nominal. But I want to be explicit that this verifies my implementation (stratum handling, fold leakage, ties), not the mathematics; if the simulation showed inflation, the bug would be mine. Alongside it I will report a **minimum detectable effect** curve: the smallest planted image-dependent signal, injected at real stratum sizes, that the test detects at 80% power. That curve is the honest statement of what the study can and cannot see.

**What I concede outright.** No equivalence margin is defensible here, and I am not going to invent one. There is no accepted scale on which "the photograph adds less than δ nats about pigment network" is medically or scientifically meaningful, so a margin would be reverse-engineered from whatever power I happen to have. The endpoint therefore becomes **one-directional**: rejection is a finding; non-rejection is reported as *inconclusive at the achieved minimum detectable effect*, never as evidence of independence. The critic's "no improvement cannot support independence" is accepted in full and the independence-direction conclusion is deleted rather than defended.

**What else is lost.** Three things, and they are real:

1. **The null shrinks to the conditioning set actually used.** Exactness needs ≥2 usable cases per stratum. With five grouped diagnoses that is comfortable; adding age, sex, site, and elevation fragments 1,007 cases into strata that are largely singletons, and singletons contribute no permutations at all. So the primary Z becomes **grouped diagnosis alone**, with diagnosis × coarsened-site as a prespecified secondary. The claim weakens from "given diagnosis and recorded metadata" to "given diagnosis," and a rejection is then compatible with the residual being site or age rather than lesion appearance — exactly the correlate class the critic named in round 1, now readmitted as a live alternative explanation. This is a genuine retreat from the round-2 wording.
2. **The result is single-cohort and single-encoder in its power, even if not in its validity.** A rejection is a fact about Derm7pt; the strength of the encoder bounds only what would have been found.
3. **The interpretive ambiguity from round 2 is untouched.** A valid rejection still admits both annotation-exposure and cross-modality-covariation readings.

**Where that leaves the card.** This is my second amendment on top of a round-1 concession, and by the rule that three amendments means the original was wrong, I will say it plainly: the original idea was wrong, and what remains is not a rescue of it. What survives is a small, statistically clean, cheap dataset-label audit with a one-directional endpoint and an unresolved interpretation. Its priority score cannot be the card's 4.25 — clarity survives, feasibility improves under the frozen-encoder design, but medical relevance, interest, and negative-result value are all materially below the recorded 4/4/4, since half the outcome space is now explicitly inconclusive. My recommendation is unchanged from round 2 and I do not want it read as advancing on the strength of this fix: **PAUSE**, pending the provenance enquiry. If provenance returns "scorer saw both images," the correct action is to stop and write a two-paragraph documentation note.

**Renaming, since the critic offered it as the alternative.** Accepted for the reported quantity, refused for the hypothesis: the *effect size* reported will be named model- and metric-conditional incremental predictive value, because that is exactly what it is; the *test* keeps the conditional-independence name because the p-value is valid for that null given the stated Z. Conflating the two is what made round 2's endpoint overclaim.

**Status:** CONVERGED


===== ideas/002/idea_card.json =====
{
  "id": "C3",
  "title": "Dermoscopic concepts predicted from non-dermoscopic photographs: genuine visibility or shortcut?",
  "question": "Can a model predict the seven dermoscopic checklist criteria from Derm7pt's paired clinical photographs \u2014 where those criteria are by definition not visible \u2014 and if it can, does the ability survive controls that remove lesion-identity shortcuts?",
  "concept_definition": "A concept is one of the seven 7-point checklist dermoscopic criteria as defined in C1. The defining feature of this candidate is that these criteria are specified with reference to dermoscopic magnification and lighting; structures such as pigment network and blue-whitish veil are dermoscopic findings, and the clinical photograph of the same lesion is not the medium in which they are assessed. Derm7pt nevertheless attaches the same case-level criteria labels to both images of the pair.",
  "medical_relevance": "Teledermatology and consumer skin-check applications operate on ordinary photographs. If a model can be trained to emit confident dermoscopic-criterion readouts from a photograph and those readouts appear to work, users will act on structured findings that the input medium cannot support. The question is whether apparent cross-modality concept prediction reflects a real correlate visible at clinical resolution, or a shortcut through diagnosis-correlated appearance.",
  "closest_work": [
    {
      "citation": "Kawahara J. et al. Seven-Point Checklist and Skin Lesion Classification Using Multitask Multimodal Neural Nets.",
      "identifier": "IEEE JBHI 2019; https://github.com/jeremykawahara/derm7pt",
      "source_type": "journal + official repository",
      "verification": "verified_by_search_summary_only for the venue; repository URL confirmed",
      "what_it_establishes": "The paired-modality dataset with 1011 cases, each having both a clinical and a dermoscopic image, and multitask prediction of the checklist criteria alongside diagnosis.",
      "exact_delta": "The original and subsequent multimodal work fuses the two modalities and reports fused performance. Fusion is designed to maximise combined accuracy; it does not isolate what each modality contributes per concept, which is the only configuration that answers the validity question."
    },
    {
      "citation": "Napoles G., Grau I., Salgueiro Y. Concept Inconsistency in Dermoscopic Concept Bottleneck Models.",
      "identifier": "arXiv:2604.19323; Sci Rep s41598-026-56927-2; https://github.com/gnapoles/Consistent-Derm7pt",
      "source_type": "journal + repository",
      "verification": "verified_by_primary_fetch",
      "what_it_establishes": "Confirms the paired structure and, importantly, ships both the clinical and dermoscopic crops at 383x384 alongside meta.csv and frozen split files.",
      "exact_delta": "Concerned with concept-label consistency, not with modality. Supplies the ready-to-use paired data."
    },
    {
      "citation": "Representative multimodal Derm7pt follow-ups: 'A Novel Perspective for Multi-modal Multi-label Skin Lesion Classification' (arXiv:2409.12390); 'Self-Supervised Multi-Modality Learning for Multi-Label Skin Lesion Classification' (arXiv:2310.18583); MICA (arXiv:2401.08527).",
      "source_type": "preprints",
      "verification": "verified_by_search_summary_only",
      "what_it_establishes": "A substantial body of work treats clinical and dermoscopic images as two complementary views to be aligned or fused.",
      "exact_delta": "The framing is 'combine the views for accuracy'. The framing here is 'the views are not equally entitled to the label' \u2014 a validity claim rather than a performance claim. Whether any of these papers reports a clinical-only per-concept ablation is the key thing to check."
    }
  ],
  "existing_legwork": [
    "Paired within-lesion images with identical concept labels already exist for all 1011 cases \u2014 this is a naturally controlled design that would normally require deliberate data collection.",
    "Cropped, size-normalised images for both modalities plus frozen splits are downloadable from a single repository.",
    "No new annotation of any kind is needed; the comparison is entirely within existing labels.",
    "Concept-level AUC is already the standard reporting metric in this literature, so the metric needs no invention."
  ],
  "missing_step": "A per-concept, per-modality breakdown with shortcut controls. The literature reports fused performance; what is missing is the clinical-only concept AUC for each of the seven criteria, benchmarked against the dermoscopic-only concept AUC and against a diagnosis-shortcut control that shows how much of the clinical-image performance is recoverable from lesion appearance correlated with diagnosis alone.",
  "why_it_matters": "This is the cleanest available test of whether a named clinical concept, learned by a model, is actually grounded in the image or is a proxy for the diagnosis. The paired design removes patient, lesion, and label variation, leaving imaging medium as the only manipulated factor.",
  "dataset": {
    "primary": "Derm7pt paired clinical/dermoscopic images",
    "source": "github.com/gnapoles/Consistent-Derm7pt (bundled) or github.com/jeremykawahara/derm7pt (original)",
    "access": "Public; metadata MIT, images CC BY-NC-ND 4.0",
    "access_risk": "Low",
    "verification": "verified_by_primary_fetch of the repository page"
  },
  "compute_readiness": "Same as C1 \u2014 a few GPU-hours. Seven concepts x two modalities x five seeds on 1011 images is small.",
  "minimal_experiment": "On frozen splits, train identical concept predictors on (a) dermoscopic images only and (b) clinical images only, and report per-concept test AUC for each of the seven criteria in both arms. Add two controls that make the result interpretable: (c) a diagnosis-only predictor of each concept \u2014 a model with no image access that predicts the concept from the diagnosis label alone, giving the accuracy attributable purely to concept-diagnosis correlation; and (d) a label-permutation run establishing the chance floor. The decisive readout is whether clinical-image concept AUC exceeds the diagnosis-only control (c) for any concept. Exceeding (c) means something genuinely visible in the photograph is being used; failing to exceed (c) means the apparent concept prediction is diagnosis correlation wearing a concept's name.",
  "critical_confound": "Concept-diagnosis correlation, which is exactly what control (c) exists to absorb. Without it, a clinical-image model that has merely learned 'this looks like a melanoma, and melanomas usually have blue-whitish veil' would be misread as detecting blue-whitish veil. Any version of this experiment lacking control (c) is not worth running.",
  "secondary_confound": "Cross-modality information leakage through image provenance. If clinical and dermoscopic images of the same case share compression artefacts, colour calibration, or acquisition-site signature, a clinical-image model could partially identify the case. Splits must be case-level, which the released split files already are, and this should be verified rather than assumed.",
  "risky_assumption": "That the criteria labels in Derm7pt were assigned from the dermoscopic image alone. If the annotating clinicians had access to both images or to the clinical context when assigning criteria, some genuine clinical-image signal would be expected by construction and the framing weakens. This must be established from the original Kawahara et al. annotation protocol before the experiment is designed.",
  "positive_interpretation": "If clinical-image concept prediction does not beat the diagnosis-only control, that is a clean, visually intuitive demonstration that a model's named concepts can be entirely ungrounded while looking competent \u2014 a result that generalises far beyond dermatology.",
  "negative_interpretation": "If some criteria are genuinely predictable from photographs above the diagnosis control, that is a substantive and clinically useful finding in its own right: it identifies which dermoscopic criteria have clinical-photograph correlates, which is directly relevant to teledermatology triage design.",
  "why_negative_is_useful": "There is no uninformative outcome. One direction is a general warning about concept grounding; the other is a concrete teledermatology finding.",
  "scores": {
    "clarity": {
      "value": 5,
      "why": "One manipulated factor, one control, seven pre-specified readouts."
    },
    "medical_relevance": {
      "value": 4,
      "why": "Bears directly on teledermatology and consumer skin apps, though it does not by itself alter a diagnostic pathway."
    },
    "interest": {
      "value": 4,
      "why": "The setup is immediately graspable \u2014 'predict a microscope finding from a snapshot' \u2014 and the paired design is elegant."
    },
    "prior_legwork": {
      "value": 4,
      "why": "The naturally paired data and labels exist and are packaged; only the ablation and controls are absent."
    },
    "feasibility": {
      "value": 5,
      "why": "Small data, standard models, first result in days."
    },
    "data_readiness": {
      "value": 5,
      "why": "Public, bundled, split files included."
    },
    "evaluation_readiness": {
      "value": 4,
      "why": "Per-concept AUC is standard; the diagnosis-only control is a custom but simple addition."
    },
    "negative_result_value": {
      "value": 4,
      "why": "Both directions are informative and neither is a dead end."
    },
    "novelty_confidence": {
      "value": 2,
      "why": "Derm7pt is heavily studied and a per-modality concept ablation is the kind of thing that plausibly appears inside an existing paper's supplementary material. This is the weakest link in the candidate and must be checked before any work begins."
    }
  },
  "priority_score": 4.25,
  "priority_arithmetic": "feasibility 0.20*5 + prior_legwork 0.15*4 + medical_relevance 0.15*4 + interest 0.15*4 + clarity 0.10*5 + negative_result_value 0.10*4 + data_readiness 0.05*5 + evaluation_readiness 0.05*4 + novelty_confidence 0.05*2 = 4.25",
  "regret": {
    "value": 4,
    "why": "A within-lesion paired modality control is unusually clean and the data has been public since 2019."
  },
  "unverified_claims": [
    "That no existing multimodal Derm7pt paper reports clinical-only per-concept AUC. This is the decisive novelty check and was NOT performed; the multimodal papers listed were seen only as search summaries. Reading the ablation tables of arXiv:2409.12390, arXiv:2310.18583, and arXiv:2401.08527 is a prerequisite.",
    "The Derm7pt annotation protocol \u2014 specifically whether criteria were assigned from the dermoscopic image alone \u2014 was not verified and materially affects the framing.",
    "Whether the released split files are case-level rather than image-level was assumed from the repository description, not confirmed by inspecting the files."
  ],
  "recommendation": "SHORTLIST"
}


===== STAGE TASK =====
Read the full `debate.md` and write `consensus.md`. You are summarizing, not
adjudicating: do not declare a winner.

```markdown
# Debate summary — idea NNN

## Agreed
- [points both sides accept, with the round where agreement occurred]

## Unresolved
For each: the question, the proposer's position, the critic's position, and
**what evidence would settle it**. If no evidence could settle it, say that
plainly — it means the disagreement is about values or taste, not facts.

## Positions that moved
For each concession: who conceded, in which round, and in response to what
argument. If someone conceded without being given a new argument, flag it as
UNEARNED — capitulation is not agreement and should not be recorded as
consensus.

## Amendments made
What the idea now claims versus what it claimed at round zero. Note anything
lost.

## Recommendation
ADVANCE | REVISE | PAUSE | REJECT — plus the single most important thing the
human should look at before deciding.
```

If the debate converged in one round with no real objection raised, say so
explicitly. That is evidence the critic is not working, and it matters more
than the idea under discussion.

