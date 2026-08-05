# Debate summary — idea 002

## Agreed

- The original novelty premise is false: clinical-only and dermoscopic-only prediction of all seven Derm7pt checklist categories was already reported by Kawahara et al. and later by Zhang et al. Repeating those arms with AUROC would fill a metric-reporting gap, not the claimed scientific gap (round 1).
- An oracle diagnosis-only predictor is a predictive baseline, not a causal or mediator control. Clinical-image performance above it cannot prove that a named dermoscopic structure is visible, and performance at or below it cannot prove reliance on diagnosis alone (round 1).
- The original “genuine visibility or shortcut?” framing and its claim that imaging medium is the only manipulated factor are unsupported by this design (round 1).
- Novelty of the narrower diagnosis/metadata-conditional audit has not been established and would require a broader primary-source search (round 1).
- Annotation provenance is a material target-construction issue. The accessible sources inspected did not establish whether checklist annotators saw clinical photographs, clinical context, pathology, or diagnosis, and observed data within Derm7pt cannot distinguish annotation exposure from genuine cross-modality covariation (round 2).
- Without known modality-blinded annotation, a positive result cannot support the proposed teledermatology or named-feature-visibility interpretation. The constructive teledermatology claim and the original medical-relevance assessment must therefore be withdrawn or reduced (round 2).
- A failure to find image-related improvement cannot establish conditional independence: limited power, sparse classes, encoder weakness, or optimization failure remain possible explanations. In the absence of a defensible equivalence margin, non-rejection must be reported as inconclusive at the achieved sensitivity (round 3).
- Any surviving effect size should be described as model- and metric-conditional incremental predictive value. The surviving project is a single-cohort dataset-label audit, not a grounding study (round 3).
- The appropriate current disposition is to pause before image training while annotation provenance is pursued (rounds 2–3).

## Unresolved

### What information was available when checklist labels were assigned?

- **Question:** Were the seven checklist criteria scored from dermoscopic images alone under modality blinding, or could annotators see clinical photographs or other clinical information?
- **Proposer's position:** The accessible primary sources inspected do not answer this. The ambiguity cannot be resolved from Derm7pt's observed associations, so a written enquiry is a prerequisite. If the scorer saw both images, the image experiment should stop and the result should be limited to a documentation note.
- **Critic's position:** Image training should not proceed without provenance because a positive result otherwise has two materially different explanations. If provenance cannot be recovered, only a descriptive dataset-label audit or an independently blinded rescoring study is defensible.
- **What evidence would settle it:** A primary annotation manual, the original Atlas/database protocol, or written confirmation from the dataset or Atlas creators specifying the annotator's information access. A new blinded rescoring study could establish properties of newly constructed labels, but would not by itself recover the original annotation procedure.

### Is the narrower audit novel enough to justify a study?

- **Question:** Has prior work already compared diagnosis/metadata-only prediction with diagnosis/metadata-plus-clinical-image prediction for Derm7pt checklist labels?
- **Proposer's position:** Novelty is unverified and must not be claimed; the papers inspected do not settle the question.
- **Critic's position:** The narrower audit is potentially useful only if primary-source searching establishes that this exact nested comparison has not already been tested.
- **What evidence would settle it:** A documented primary-source search of Derm7pt multimodal, concept-bottleneck, and dataset-audit studies, with the closest experiments and their exact differences recorded. Failure to find a study would increase novelty confidence but would not prove absence.

### Does the proposed stratified permutation procedure validly test the stated null?

- **Question:** Can within-diagnosis permutation of images, using cross-validated log-loss improvement from frozen image features as the statistic, provide a valid finite-sample test of checklist-label–image conditional independence given grouped diagnosis?
- **Proposer's position:** Yes. Under the null, image assignments are exchangeable within discrete diagnosis strata; the model affects power but not type-I validity. The implementation should be checked with split-respecting null simulations and power characterized with planted effects.
- **Critic's position:** Before this repair was proposed, the critic held that a fitted-predictor comparison could establish only model- and metric-conditional improvement unless a valid conditional-independence test with demonstrated type-I control and useful power were supplied. The critic did not respond to the proposed repair, so acceptance cannot be inferred.
- **What evidence would settle it:** A preregistered statistical specification reviewed for its exchangeability assumptions, multiplicity handling, cross-validation/permutation nesting, and split integrity, followed by null simulations at the real stratum and class counts showing nominal type-I error and planted-effect simulations showing useful power. This would settle procedural validity and sensitivity, not the annotation-provenance interpretation.

### Is an image audit worthwhile if provenance remains unobtainable?

- **Question:** Should the image arm run as a descriptive dataset audit even if the original annotation exposure cannot be established?
- **Proposer's position:** In principle the measurement remains estimable, but the recommendation is still to pause because its value depends on provenance; the image arm is not worthwhile if authors confirm exposure to both images.
- **Critic's position:** Without provenance, do not proceed to image training merely because a tabular gate indicates estimability; restrict the work to description unless labels are independently rescored under blinding.
- **What evidence would settle it:** Provenance evidence would resolve the factual barrier. If provenance remains unavailable, this becomes partly a judgment about whether a dataset-specific dependence finding justifies compute and publication effort despite irreducible interpretive ambiguity; no additional analysis of the existing data can separate the two explanations.

## Positions that moved

- **Proposer, round 1 — conceded:** In response to primary-source evidence of prior clinical-only and dermoscopic-only evaluations, the proposer abandoned the claimed modality-ablation novelty. The proposer also accepted that the diagnosis-only comparison cannot establish genuine visibility or diagnose a shortcut. This concession was earned by new, specific prior-work and causal-identification arguments.
- **Proposer, round 2 — amended:** In response to the annotation-provenance objection, the proposer accepted that annotation exposure and cross-modality covariation cannot be separated within Derm7pt, withdrew the teledermatology interpretation, reduced the claimed medical relevance and negative-result value, and made an author enquiry a prerequisite. The proposer retained only the possibility of a descriptive image-dependent dataset audit. This amendment was earned by a new target-construction argument and an unsuccessful provenance search.
- **Proposer, round 3 — amended:** In response to the distinction between predictor comparison and conditional independence, the proposer accepted that non-rejection cannot support independence, declined to invent an equivalence margin, restricted the primary conditioning set from diagnosis plus metadata to grouped diagnosis, and renamed the reported effect size as model- and metric-conditional incremental predictive value. The proposer proposed a stratified permutation test for the one-directional null rejection. The concessions were earned; the adequacy of the proposed test remains unconfirmed because the critic did not reply.
- No concession appears unearned.

## Amendments made

At round zero, the idea claimed that a missing clinical-versus-dermoscopic ablation could decide whether named dermoscopic criteria predicted from clinical photographs were genuinely visible or merely diagnosis shortcuts. It treated the paired design as isolating imaging medium, used diagnosis-only performance as the decisive causal control, asserted useful interpretations in either direction, and scored the project at 4.25.

The amended idea is a much narrower Derm7pt dataset-label audit. Its one-directional question is whether clinical photographs show evidence of dependence with recorded checklist labels after conditioning primarily on grouped diagnosis. The proposed statistic is cross-validated log-loss improvement from adding frozen, label-free image features to a locked diagnosis model, calibrated by within-diagnosis image permutations. Diagnosis × coarsened site is only a secondary analysis because richer metadata strata become too sparse. A rejection would establish dependence under the test's assumptions, while the reported magnitude remains model- and metric-conditional; non-rejection is inconclusive and must be accompanied by achieved-power or minimum-detectable-effect results.

Lost from the original idea are the modality-ablation novelty, causal shortcut diagnosis, proof of named-feature visibility or grounding, the teledermatology payoff, conditioning on the full recorded metadata set, an informative interpretation for both outcome directions, and the original priority score. Even a valid rejection remains compatible with annotation exposure, age/site/provenance correlates, and genuine cross-modality covariation.

## Recommendation

**PAUSE** — the single most important thing for the human to inspect is the original annotation protocol, specifically whether checklist scorers could see the paired clinical photograph or other clinical information. Until that is resolved, the surviving experiment has irreducibly ambiguous value; if exposure to both images is confirmed, stop at a short documentation finding rather than train an image model.
