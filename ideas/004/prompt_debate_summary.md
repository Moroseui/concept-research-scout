You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/004
Preserve existing files unless the task explicitly requires an update.
Do not claim novelty without verified primary sources.
Do not write code unless this is the probe_code stage and human approval exists.

===== CHARTER.md =====
# Research charter

## Central interest

Find clear, feasible, medically relevant research questions about **concepts in
medical imaging** — how concepts are defined, measured, validated, and used.
Diagnosis, prognosis, representation analysis, concept reliability, concept
intervention, and model auditing are all in scope. Concept-motivated
segmentation correction is a side project, not the default direction.

## Two search modes

Every scouting cycle must draw candidates from **both** modes. They find
different things and one does not substitute for the other.

### Mode A — the unfinished story

A paper does most of the work and stops one experiment short. The gap is
citable: an explicit future-work sentence, a missing evaluation, an untested
assumption, a claim made on one dataset.

Mode A is citation-anchored, which is its strength and its limit. It can only
surface questions the literature has already framed. It also selects for gaps
the original authors *chose* to leave — sometimes because they were hard,
sometimes because the data to close them does not exist. Treat a conveniently
open gap as suspicious until the reason it is open is established.

### Mode B — the unasked question

Nobody left this for future work because nobody framed it. It is not in a
future-work section; it is in the space between two things that should connect
and do not.

Prompts that generate Mode B candidates:

- If you did not trust this result, what would you check first — and why has
  nobody published that check?
- What does everyone in this subfield assume without measuring? What would
  measuring it cost?
- Two subfields use the same word for different things, or different words for
  the same thing. Does the difference matter?
- A method is justified by an argument. Does the argument's premise hold on
  the data it is applied to?
- Something is standard practice for a historical reason. Is the reason still
  true?
- A quantity is always reported in aggregate. What does its distribution look
  like?

Mode B candidates are usually cheaper than Mode A candidates, because an
unasked question is often unasked precisely because it is a small check rather
than a full study. Cheapness is a feature. A one-afternoon measurement that
changes how people read a literature beats a three-month replication.

Each candidate must declare `search_mode: A | B`. At least two candidates per
cycle must be Mode B.

## Domain focus

The primary domain is **radiology, with emphasis on CT and 3D volumetric
imaging**. Vascular and tubular anatomy, chest CT, and CT-report paired corpora
are especially relevant.

Hard quotas per cycle:

- At least four of six candidates in radiology or CT.
- At most one dermatology candidate.
- No more than two candidates on any single dataset.
- No more than three candidates whose method is a concept bottleneck model.

These quotas exist because an unconstrained search collapses onto whatever
literature is largest and most concept-annotated — dermatology and CBMs. That
is not where the interesting radiology questions are.

Candidates outside the focus areas are allowed when the question is strong
enough to justify the detour. Say so explicitly rather than drifting quietly.

## Cross-domain connections

Borrowing from neuroscience, cognitive science, psychometrics, statistics, or
information theory is encouraged. Concept validity in particular is a
solved-adjacent problem in psychometrics — construct validity, inter-rater
reliability, convergent and discriminant validity — and that vocabulary is
largely absent from concept-based ML.

**Guard against decorative analogy.** Fluent neuroscience-to-vision parallels
can be generated indefinitely and almost none of them change what you would
measure. Any cross-domain candidate must state:

1. the specific borrowed construct, with a citation;
2. the concrete measurement or design it implies;
3. **what would be different if the analogy were dropped.**

If the answer to (3) is "nothing," the analogy is decoration. Rewrite the
candidate without it or discard it.

## Architecture proposals

Structural variants — concepts layered over attention, hierarchical concept
graphs, alternative bottleneck placements — are in scope, with one condition:
**the first probe must be a measurement, not a trained variant.**

Method contributions need baselines, ablations, and seed variance to be
credible, which is expensive and slow. Before building an architecture, find
the cheap measurement that establishes whether it could help. Prior finding
from this project: added capacity inside a bottleneck performed *worse* than no
bottleneck. Capacity is not the constraint; whether the concepts carry the
information is.

## The keystone prerequisite

Every candidate must name a `keystone_prerequisite`:

> The single fact which, if false, makes this study impossible or
> uninterpretable.

Then state whether it has been **directly inspected** — the actual file, table,
protocol, or paper section — or merely inferred from a collection page,
abstract, or search summary.

**Feasibility may not exceed 3, and novelty may not exceed 3, until the
keystone has been directly inspected.**

This rule exists because three consecutive candidates scored 4+ on feasibility
and died on a single unchecked fact:

- LIDC concept validity: the released diagnosis file is patient-level and its
  numbering does not match the XML; only 18 nodules were reliably linkable.
- Derm7pt clinical photographs: whether checklist annotators could see the
  clinical image was never documented, making any result ambiguous.
- BI-RADS intervention: BUS-BRA releases assessment *categories*, not lexicon
  *descriptors*, so there were no concepts to intervene on.

In each case "the dataset exists" was mistaken for "the scientific linkage
exists." Those are different claims.

## Claim identifiability

A scored dimension distinct from clarity: **can the proposed experiment
distinguish the claimed explanation from the plausible alternatives?**

A compelling headline is not identifiability. "Microscope findings from a
snapshot," "opinion instead of disease," and "realistic clinician behaviour"
are all good sentences attached to designs that could not isolate the stated
phenomenon. State the two or three most plausible alternative explanations for
a positive result and say which the design rules out.

## Negative results

Both outcomes should be informative, but classify the anticipated negative:

1. **Decisive negative** — meaningfully weakens the hypothesis.
2. **Sensitivity-limited null** — may reflect power, modelling, or metric
   choice; needs an equivalence margin or minimum-detectable-effect.
3. **Uninterpretable null** — several explanations survive.

Only type 1 counts toward negative-result value. Type 3 means the design needs
revision. Non-rejection is not evidence of independence.

## Desired project properties

- Explainable in one sentence.
- Interesting to someone outside the immediate subfield.
- Public data, or access already confirmed.
- Feasible for one researcher with Colab-class compute.
- Clear baselines and metrics.
- Minimal new expert annotation.
- First useful result in days, not months.

## Themes of interest

1. Reliability and causal validity of named concepts.
2. Specified versus discovered concepts in small medical datasets.
3. Concept leakage and hidden residual information.
4. Faithfulness of concept-mediated reasoning or explanations.
5. Concept stability across sites, scanners, protocols, and demographics.
6. Whether concept supervision improves calibration, robustness, or failure
   detection.
7. Low-cost audits of published concept-based models using existing assets.
8. Provenance and construction of concept labels themselves — who assigned
   them, seeing what, and what that implies about what a model trained on them
   can be said to have learned.

Theme 8 was added because the first three candidates all died on it. It is the
most under-examined area found so far and the one where a cheap audit is most
likely to produce a real finding.

## Constraints

- Compute: Colab Pro+ or equivalent single-GPU sessions.
- No dependence on unconfirmed DUA-gated data.
- No large-scale radiologist annotation campaign.
- Literature claims require primary-source verification.
- Do not treat report text, class labels, or segmentation labels as meaningful
  concepts without justification.
- Avoid architectural complexity unless the question requires it.
- Keep confirmatory and exploratory work separate.
- Never tune on the untouched test set.

## What counts as success

- A clear positive result.
- A clear negative result of type 1.
- Evidence that a popular assumption is unsupported.
- Identification of a decisive confound.
- A feasibility result that prevents wasted effort.
- A well-supported decision to advance, revise, pause, or reject.


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

Score each dimension 1-5. Explain every score.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Clarity | vague | testable with refinement | one-sentence precise question |
| **Identifiability** | a positive result has many explanations | design rules out the main alternative | design isolates the claimed mechanism |
| Medical relevance | cosmetic | plausible utility | clear meaningful consequence |
| Interest | routine | useful niche result | surprising or broadly compelling |
| Prior legwork | little exists | some reusable assets | data/code/labels/checkpoints ready |
| Feasibility | major barriers | manageable | first result in days |
| Data readiness | uncertain/restricted | accessible with work | public and directly usable |
| Evaluation readiness | unclear | custom metrics needed | accepted metrics and baselines exist |
| Negative-result value | uninterpretable null | sensitivity-limited null | decisive negative |
| Novelty confidence | likely covered | uncertain | precise verified gap |
| Regret | little concern | worth considering | obvious-in-hindsight opportunity |

## Hard caps

`feasibility` and `novelty_confidence` may not exceed **3** unless
`keystone_status` is `INSPECTED_TRUE`. See the charter.

`negative_result_value` may not exceed **2** if the anticipated negative is
classified as uninterpretable.

## Priority score

Transparent weighted sum, not a fake probability:

- 20% feasibility
- **15% identifiability**
- 15% medical relevance
- 10% prior legwork
- 10% interest
- 10% clarity
- 10% negative-result value
- 5% data readiness
- 5% novelty confidence

Evaluation readiness and regret are reported separately and must not override
weak scientific value.

Identifiability enters at 15% because the first cycle produced several
candidates with strong headlines whose designs could not isolate the stated
phenomenon. Interest was compensating for weak measurement validity.


===== ideas/004/README.md =====
# Idea 004: The free test-retest experiment already inside CT-RATE: duplicate reconstructions of the same acquisition

Selected from scouting cycle 002, candidate 1.


===== ideas/004/critique.md =====
FATAL OBJECTION: NONE; the paired audit is feasible, but the current Stage 0 and clinical interpretation make claims that its data cannot identify.
EVIDENCE: The official CT-RATE card confirms reconstruction-indexed volumes and a gated 21.3-TB repository, but filenames and duplicated labels alone cannot determine an AUROC design effect.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION

# Adversarial critique

## Bottom line

There is a defensible study here: measure how much a *specific released CT-CLIP classifier's scores* change across CT-RATE reconstructions of the same scan, and audit whether treating those reconstructions as independent changes uncertainty or estimands in that model's published validation. The current card goes beyond that evidence in four places: it calls reconstruction repeatability “test-retest,” promises a no-model design-effect result that cannot be computed from labels, treats report-derived abnormalities as validated concepts, and converts agreement into a general ceiling on clinical validity. Those are repairable, but they require a narrower claim and a different primary analysis.

## Facts actually verified

- **Verified fact:** the official CT-CLIP repository states that 25,692 CT volumes expand to 50,188 through “various reconstructions,” defines names as `split_patientID_scanID_reconstructionID`, and gives `valid_53_a_1` as a worked example. This verifies an identifiable reconstruction grouping, not yet that every same-scan group is a clean matched-kernel pair. Official repository: https://github.com/ibrahimethemhamamci/CT-CLIP ; paper identifier: arXiv:2403.17834, subsequently listed by the dataset card as *Nature Biomedical Engineering* (2026).
- **Verified fact:** the current official Hugging Face card requires login and agreement to share contact information; it calls the repository publicly accessible subject to conditions, prohibits redistribution, and reports a total size of 21.3 TB. It does not describe a manual approval step. Official dataset: https://huggingface.co/datasets/ibrahimhamamci/CT-RATE
- **Verified fact:** the official repository reports approximately 0.5 seconds per volume for ClassFine inference and says inference can run on smaller GPUs. It also warns that changing encoder patch size to fit memory can affect small-pathology performance. This supports bounded inference, but not reproducibility on an arbitrary Colab GPU without first reproducing the released preprocessing and logits.
- **Source-supported interpretation:** paired reconstructions are a valuable within-acquisition perturbation because anatomy and acquisition are substantially held fixed.
- **Still unverified:** the validation reconstruction count; whether all members share acquisition UID/time and report; which parameters differ; whether reconstruction IDs have consistent meanings; whether released metadata retain kernel, thickness, method, and series description; and whether accessible files contain raw logits or only binary labels.

The card should correct the patient-count discrepancy before revision: the official repository/card says 1,304 validation patients, whereas the cited later benchmark says 1,314. This is probably a paper/version or filtering difference, but it prevents casually combining their denominators.

## The strongest objection: Stage 0 cannot deliver its promised result

Counting clusters and showing that label vectors repeat is useful bookkeeping. It does **not** yield “the factor by which a naive per-volume confidence interval is too narrow.” The familiar design effect `1 + (m-1)rho` applies to particular clustered estimators under assumptions; `rho` must concern the relevant observations, scores, losses, or influence functions. An ICC of duplicated binary label vectors is either mechanically one or near one and says nothing about covariance of model errors. AUROC is a pairwise rank statistic, so its clustered variance is not recoverable from cluster sizes and labels alone.

Likewise, duplicate volumes do not necessarily inflate an AUROC point estimate. Per-volume AUROC estimates a reconstruction-weighted quantity; one-per-scan AUROC estimates a scan-weighted quantity. A difference can arise because scans with more reconstructions receive more weight, not because the original computation is numerically biased for its own estimand. “Overstate the precision of every number” is especially too broad: point estimates are not precision estimates, some papers may publish no confidence intervals, and metrics react differently to clustering.

**Required repair:** Stage 0 should only establish the cluster structure, label/report duplication, parameter contrasts, and feasibility. The benchmark audit must use model outputs and compare clearly named estimands: reconstruction-weighted, scan-weighted (for example, mean score per scan), and patient-weighted where longitudinal scans exist. Use a patient- or scan-cluster bootstrap appropriate to the chosen estimand. Do not predeclare the direction of interval change.

## This is reconstruction repeatability, not test-retest reliability

The acquisition is not repeated. Consequently the study cannot measure sensitivity to positioning, inspiration, dose realization, patient motion, biological change, or scanner repeat acquisition. Calling it a “free test-retest experiment” overstates what is held and varied. The accurate term is **within-acquisition reconstruction repeatability** or **reconstruction perturbation consistency**.

This distinction matters clinically. A stable score across two reconstructions can still be unstable across acquisitions or wrong in both reconstructions. An unstable score is a valid model-robustness failure, but it does not establish that a radiological finding itself is unreliable.

## The endpoint is not yet identifiable

### “Reconstruction” is a bundle, not a named intervention

Two released NIfTI volumes may differ in kernel, slice thickness, interval, reconstruction algorithm, field of view, orientation, or corrections applied during dataset construction. The dataset card explicitly notes later intensity-normalization and spacing corrections to the NIfTI files. If metadata do not identify the contrast, the experiment can estimate repeatability across the corpus's released reconstruction variants, but cannot attribute changes to kernel choice.

Parsing identical patient and scan IDs is necessary but insufficient. Before GPU work, verify acquisition/series fields and inspect voxel grids and metadata. If the pair differs in slice thickness as well as kernel, describe the composite contrast. “Reconstruction-induced” is acceptable; “kernel-induced” is not.

### The identical-volume rerun is a weak control

Evaluation-mode inference should normally be deterministic. A zero software-noise floor only excludes stochastic execution; it does not separate reconstruction effects from dataset resampling, intensity correction, cropping, padding, or interpolation. Those operations are part of the deployed inference pipeline and can interact with different source grids.

A better decomposition uses three controls: identical file twice; a deterministic re-save/resample of one volume through the pipeline; and the actual paired reconstruction. If only the last changes, the result is still a *pipeline-under-reconstruction* effect unless preprocessing is independently standardized.

### ICC(2,1) is not automatically the right primary statistic

Reconstruction IDs are not human raters sampled from a common population, groups may have unequal sizes, and different scans may receive different reconstruction contrasts. A pooled ICC can be very high merely because between-scan score variance is large while clinically important within-scan changes remain. It is also unstable for rare findings and says little at decision thresholds.

Pre-specify a reference/contrast only where metadata define comparable pairs. Report paired score differences with Bland–Altman-style limits or a repeatability coefficient, absolute difference distributions, and threshold crossing rates over clinically justified thresholds. Stratify by concept prevalence/score region and reconstruction contrast. ICC may be secondary, with its model and variance components stated. An equivalence claim needs an a priori, clinically or operationally justified margin; `ICC > 0.95` and “low single-digit flips” are currently unsupported illustrative cutoffs.

## Concept-label circularity and leakage

The primary paired-score analysis avoids using report-derived labels, so it is not circular in the narrow statistical sense. But it also does not validate a “concept.” The 18 outputs are heads trained/evaluated against RadBERT-derived report labels. Agreement shows only that a model output is stable under a reconstruction perturbation. Both reconstructions can share the same spurious cue, and both predictions can be consistently wrong.

The secondary benchmark is more vulnerable. If each reconstruction inherits the same report and label, repeated labels are mechanically correlated. ClassFine was trained on similarly expanded reconstructions, so the audit describes robustness of a system trained with this augmentation-like duplication; it cannot establish robustness of chest-CT foundation models generally. There is no train/validation patient leakage implied by this fact, but there is **estimand dependence** and possible training-policy leakage: the model may have learned reconstruction invariance precisely because training scans appeared in multiple variants.

Required language: call these “18 abnormality output scores” or “named report-derived finding outputs,” not validated abnormality concepts. Keep validity, accuracy, and faithfulness out of the primary claim.

## The attenuation-bound argument should be removed

The proposed statement that no downstream correlation can exceed the square root of this reliability imports classical test theory assumptions that this design does not establish: a stable latent construct, additive independent error, appropriate sampling, and a reliability coefficient for the same measurement process. Within-acquisition reconstruction agreement isolates only one nuisance source. High agreement across reconstruction variants is not total score reliability; low agreement may combine preprocessing and heterogeneous reconstruction contrasts. It therefore cannot provide a general ceiling on correlations with external outcomes, much less make a published correlation “impossible.”

The cross-domain construct still adds value if used modestly: variance decomposition and limits of agreement force reporting of the within-scan distribution rather than only flips. That is what changes when the analogy is retained.

## Prior-work overlap and novelty

The broad scientific premise is already established. Primary studies use paired chest CT reconstructions to evaluate or enforce model/measurement consistency:

- Zuo et al., “Adaptation to CT Reconstruction Kernels by Enforcing Cross-Domain Feature Maps Consistency,” used public paired LIDC/IDRI reconstructions differing in kernel and documented large baseline prediction/feature inconsistency for a lung-CT segmentation task. PMCID: PMC9503667.
- Hwang et al., “Kernel Conversion for Robust Quantitative Measurements of Archived Chest Computed Tomography Using Deep Learning-Based Image-to-Image Translation,” used paired sharp/soft reconstructions and evaluated emphysema and other quantitative measures. PMID: 35112080; DOI: 10.3389/frai.2021.769557; PMCID: PMC8801695.
- Liard et al., “Impact of reconstruction kernel variability on segmentation consistency in low-dose thoracic CT,” evaluates 9,529 paired scans and 84 thoracic regions. DOI: 10.1117/12.3085743; PMID: 42266434. This is especially close in design vocabulary, although its endpoint is segmentation rather than named abnormality scores.
- A 2025 foundation-model study directly evaluates feature robustness across three kernels and two slice thicknesses in repeated LDCT reconstructions. PMID: 42038169. This materially weakens any broad novelty claim about “foundation-model reliability across reconstruction parameters,” though it does not appear to test CT-CLIP's 18 scan-level outputs.

Thus the defensible delta is narrow: **CT-RATE-specific paired reconstruction consistency of released CT-CLIP abnormality outputs, plus a scan-clustered audit of its validation protocol.** Searches here did not establish that this exact audit is unpublished; proceedings and citing-paper searches remain required. Novelty confidence should remain 3 or fall to 2 until those are checked.

## Medical relevance and negative-result value

The immediate medical relevance is moderate, not high. CT-CLIP/ClassFine is a released research model, and this experiment does not connect a threshold crossing to a clinical decision or a radiologist's interpretation. A large discordance is actionable for model evaluation and dataset design. It is not yet evidence that “a clinician cannot act on” the concept, because no clinical operating point or workflow is evaluated.

The proposed negative is not fully decisive. Near-identical outputs would establish robustness only for multiply reconstructed CT-RATE scans, their observed reconstruction contrasts, this checkpoint, and this preprocessing. It would not reassure against site/scanner shift or ordinary test-retest variation. Meanwhile an unchanged AUROC with wider clustered intervals addresses a different question. Split the outcomes:

- **High within-acquisition agreement:** decisive for the narrow reconstruction-repeatability hypothesis if the contrast and equivalence margin are prespecified; otherwise sensitivity-limited.
- **No AUROC point-estimate change:** weak by itself, because weighting and labels can hide paired score changes.
- **No confidence-interval change:** informative only after selecting the clustered estimator and attaining enough independent positive/negative scans per abnormality.

Rare abnormalities may make per-concept threshold flips and AUROC too imprecise. Prespecify a prevalence/positive-count rule and label the remaining categories exploratory rather than silently presenting 18 underpowered tests.

## Availability and compute

Access is a real pause condition, though not presently fatal. The files are gated and the full corpus is 21.3 TB. The card should not call this “fully public” under a charter that excludes dependence on unconfirmed gated data. Accepting conditions appears user-mediated and cannot be assumed complete. Before a feasibility score of 4 is retained, directly verify access to the two small tables and one paired image group.

Compute is probably manageable: the authors report 0.5 seconds per ClassFine volume and smaller-GPU inference. Storage/download, exact preprocessing, checkpoint loading, and memory are more credible risks than raw inference time. Do not alter patch size to fit the GPU, because the official repository says this can affect small-pathology performance; use batch size one or pause if the released configuration itself does not fit.

## Easier version and low-hanging fruit

The genuine low-hanging fruit is **not** the claimed label-only confidence-interval audit. It is a metadata and release-structure audit that answers whether the substantive experiment is identified:

1. With the small validation labels/metadata tables, count reconstruction groups, longitudinal scans, and patients; test whether labels/reports are exactly duplicated within scan; enumerate the parameter contrasts; and reconcile 1,304 versus 1,314 patients.
2. If the authors have released per-volume ClassFine scores (this remains unverified), analyze those immediately with no image download or GPU. This would be the cheapest faithful version and should be explicitly sought in repository artifacts, evaluation outputs, model cards, or from the authors.
3. If scores are not released, download a small, stratified set of approximately 50–100 clean, same-acquisition pairs spanning the common reconstruction contrasts. Run the unchanged released checkpoint. Use continuous paired score differences across all 18 outputs as the first endpoint; treat rare-label AUROC and flip rates as later analyses.

Existing assets are unusually strong: official grouping keys, small metadata/label tables, released inference code, and released ClassFine weights. What does **not** yet exist in inspected form is the essential per-volume output table. Asking the authors for validation logits is therefore the highest-value shortcut: it could eliminate terabytes of image access and most GPU work while preserving both the repeatability and clustered-benchmark questions.

## Required revision before a feasibility memo

- Rename the study as within-acquisition reconstruction repeatability.
- Make access to small tables and one image pair a hard gate; downgrade data readiness until demonstrated.
- Replace the Stage 0 design-effect promise with a cluster/metadata/label provenance audit.
- Define the unit and estimand separately for scan and patient; handle multiple scans per patient.
- Establish comparable reconstruction contrasts from metadata before causal wording.
- Use paired differences/limits of agreement as primary; justify any ICC model and equivalence margin.
- Separate model-score repeatability from benchmark inference and from concept validity.
- Remove the general attenuation ceiling and clinical-actionability language.
- Search the model repository, authors' artifacts, MICCAI/SPIE/MIDL proceedings, PubMed, and citing literature for both released logits and exact prior audits.
- Freeze one checkpoint, one unmodified preprocessing pipeline, pair inclusion rules, thresholds, primary concepts or multiplicity plan, and the bootstrap unit before inspecting substantive score differences.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Across metadata-confirmed alternative reconstructions of the same CT-RATE acquisition, how much do the released ClassFine abnormality scores change, and do scan- rather than reconstruction-weighted validation estimates materially alter conclusions?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes—if clean reconstruction contrasts and either released logits or a bounded paired download exist, because it audits a widely reused chest-CT resource with no retraining and can change both robustness reporting and benchmark inference.


===== ideas/004/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed Stage 0 cannot answer the study's benchmark-precision question, because duplicated labels and reconstruction counts do not identify the sampling variance of AUROC or any other model-performance statistic.

**Argument:** The design claims that `valid_predicted_labels.csv` and cluster sizes alone yield “the factor by which a naive per-volume confidence interval is too narrow.” They do not. Within-scan agreement of report-derived label vectors is mechanical duplication, whereas the relevant dependence is in ClassFine scores, errors, losses, or estimator influence values. AUROC is a pairwise rank statistic whose clustered variance depends on the joint distribution of positive and negative model scores; it cannot be recovered from label ICC and cluster size using the simple `1 + (m-1)rho` design-effect formula. Moreover, per-volume and one-per-scan AUROC target different weighting estimands, so a point-estimate difference is not automatically inflation or bias. The metadata-only audit can establish grouping, duplicated labels, and reconstruction contrasts, but the precision claim requires per-volume model outputs and a prespecified reconstruction-, scan-, or patient-weighted estimand with bootstrap resampling at the corresponding independent unit. The narrowed ClassFine audit still retains the core identity of the original paired-reconstruction question, but Stage 0 as written does not test its second half.

**What would change my mind:** Show either released validation logits or newly generated unchanged-checkpoint logits, then specify the target estimand and demonstrate with a scan- or patient-cluster bootstrap that the per-volume analysis materially changes interval width or conclusions; alternatively, remove the precision result from Stage 0 and describe that stage only as a linkage and feasibility audit.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** Stage 0 advertises a number it cannot compute. Label duplication and cluster sizes give the *structure* of the validation set, not the *sampling variance* of any performance statistic on it. Label ICC is mechanically ~1 and carries no information about model behaviour; AUROC's clustered variance depends on the joint distribution of positive and negative scores; and one-per-scan versus per-volume AUROC are differently weighted estimands rather than a corrected and an inflated version of the same one. So "the factor by which a naive per-volume confidence interval is too narrow" is not obtainable from `valid_predicted_labels.csv` plus filenames.

**Response:** CONCEDE

**Argument:** The objection is correct, and the error is specific enough to name. I conflated the cluster structure of an evaluation set with the variance of a statistic computed on it. `1 + (m-1)rho` is the design effect for the mean of exchangeable observations in equal-sized clusters; here the estimator is not a mean, the units entering it are pairs rather than observations, and the clusters are unequal in size. The `rho` that enters any correct clustered variance is the within-scan correlation of score-dependent quantities — errors, losses, influence contributions — which requires exactly the per-volume model outputs I claimed Stage 0 could do without. An ICC of 1.0 on duplicated label rows is a fact about how the corpus was released, not a fact about an estimator. The sentence in the idea card should be struck, not reworded.

What Stage 0 keeps is still worth doing and still cheap: cluster counts and the reconstructions-per-scan distribution, an exact-duplicate check on labels and reports within scan, the enumeration of reconstruction parameter contrasts from `validation_metadata.csv`, the 1,304-versus-1,314 patient reconciliation, and the go/no-go on paired-image access. What it loses is the headline deliverable — "the benchmark's error bars are N times too narrow," obtainable from a 174 kB CSV with no model and no GPU. That was the cheapest advertised result and a large part of why the candidate read as a one-afternoon measurement. Conceding it makes the study strictly more expensive: every precision claim now sits behind logits, whether released or regenerated.

One point in the objection I want to keep on the table without pretending it rescues Stage 0. When a paper reports "AUROC on the CT-RATE validation set," the estimand a reader infers is per-scan or per-patient diagnostic performance, not reconstruction-weighted performance. On that reading a reconstruction-weighted computation is a reporting defect even where it is not estimator bias in the narrow sense — the number answers a question nobody asked. But that is a claim about the interpretation of a published quantity, it is still only testable with scores in hand, and it changes nothing about the arithmetic. It belongs in Stage 1, not as a defence of Stage 0.

The precision half of the question therefore relocates rather than dies: with logits, prespecify reconstruction-weighted, scan-weighted (mean score per scan, and separately a random-draw-per-scan variant), and patient-weighted estimands; bootstrap at the patient level as the outermost independent unit, since patients contribute multiple scans and scans contribute multiple reconstructions; report interval widths for each without predeclaring a direction of change. The original one-sentence question survives intact — what dies is my claim that its second half could be answered without running the model.

The honest replacement for the lost cheap deliverable is a search task, not a compute task: establish whether per-volume ClassFine validation scores were ever released alongside the checkpoints or in the paper's evaluation artifacts. If they were, the relocated precision analysis costs no image download and no GPU and Stage 0's cost profile is nearly restored. If they were not, the candidate must be re-costed as inference-first, and the feasibility score of 4 should be revisited on that basis rather than on the gated-access risk alone.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The revised design still cannot attribute paired score differences to reconstruction variation, because its identical-file rerun control tests stochastic execution rather than the deterministic preprocessing differences induced by distinct source grids.

**Argument:** The proposer correctly preserves the original question by relocating the benchmark-precision analysis behind logits, so the Round 1 objection is resolved. The strongest remaining problem is the causal interpretation of the repeatability arm. ClassFine does not consume the released reconstruction untouched: CT-CLIP preprocessing resamples, crops or pads, and normalizes each 3D volume, while CT-RATE itself has undergone spacing and intensity corrections. Alternative reconstructions can differ in voxel spacing, slice thickness, field of view, orientation, and matrix as well as kernel. Running one identical file twice in evaluation mode should return the same score and therefore only bounds stochastic software noise; it cannot reveal whether a paired score difference arose from the reconstruction contrast itself or from deterministic interpolation, crop inclusion, padding, or normalization triggered by the two grids. This matters because the card explicitly says that control “rules out” preprocessing instability and then interprets the residual as reconstruction-induced concept variation. The proposed output remains a valid estimate of end-to-end *pipeline consistency across released reconstruction variants*, but that is narrower than identifying a model response to reconstruction content and does not support kernel-specific or image-content-specific language. A deterministic re-save is also insufficient unless it reproduces the relevant grid transformations. The design needs a preprocessing perturbation control matched to each pair: transform one member onto the other's grid (and, where possible, the reverse) while holding its intensities/content source fixed, then compare the score change from grid/preprocessing alone with the actual cross-reconstruction change. If reconstruction metadata show bundled changes that cannot be separately recreated, the estimand must remain explicitly composite.

**What would change my mind:** Prespecify and demonstrate a matched-grid preprocessing control for representative metadata-confirmed pairs, showing that deterministic resampling/cropping of one reconstruction onto the partner's geometry produces materially smaller score changes than the true pair; otherwise revise the claim throughout to end-to-end pipeline repeatability under composite released reconstruction variants and stop saying the identical-file control rules out preprocessing.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The identical-file rerun bounds stochastic execution noise only. Because the released pipeline resamples, crops/pads and normalises each volume before the network sees it, two reconstructions arriving on different voxel grids get deterministically *different* preprocessing, and that difference is not stochastic and is therefore invisible to the rerun control. So the card is wrong to say the control "rules out" preprocessing, and wrong to read the residual as reconstruction-induced concept variation. The honest estimand is composite end-to-end pipeline repeatability unless a matched-grid control separates the two.

**Response:** AMEND

**Argument:** The two language defects are conceded without qualification: "RULED OUT by the identical-volume repeat control" in `alternative_explanations[1]` is false and must be struck, and "reconstruction-induced" must not appear as a causal descriptor for the unstratified corpus. The identical-file rerun establishes determinism of the software, nothing more, and I will label it that way.

What I dispute is the scope of the damage, and I have new evidence rather than a restatement. I read the released preprocessing rather than reasoning about it in the abstract — `scripts/data_inference_nii.py` in the official repository (raw.githubusercontent.com/ibrahimethemhamamci/CT-CLIP/main/scripts/data_inference_nii.py, inspected 4 Aug 2026). The differential surface is smaller and far more legible than the objection assumes:

- HU conversion is `slope`/`intercept` read per volume from the metadata CSV (`row["RescaleSlope"]`, `row["RescaleIntercept"]`).
- Clipping is `hu_min, hu_max = -1000, 1000` — **fixed constants**. Normalisation is `img_data / 1000` — a **fixed scalar**. There is no percentile, mean/std, or otherwise data-dependent intensity step. This removes an entire class of content-driven differential preprocessing that the objection allows for.
- Resampling is `F.interpolate(..., mode='trilinear', align_corners=False)` to a fixed target of 0.75 × 0.75 × 1.5 mm, with the scaling factor computed from `row["XYSpacing"]` and `row["ZSpacing"]`.
- Crop/pad is a centre crop or a symmetric pad with value `-1` to a fixed `target_shape = (480, 480, 240)`.

So `nii_img_to_tensor` is a deterministic function whose *shape* is fully determined by five per-volume scalars: RescaleSlope, RescaleIntercept, XYSpacing, ZSpacing, and the source array dimensions. Everything else is a constant. That yields a sharper repair than the one proposed.

**The amendment: stratify on geometry-matched pairs, and make that stratum the primary analysis.** If two members of a scan group share slope, intercept, XY spacing, Z spacing and array shape, then the resample scaling factors are identical, the crop/pad offsets are identical, and the intensity map is identical — the preprocessing applied to the two volumes is not "approximately matched," it is *the same function*. For that stratum there is no differential preprocessing effect to control for, and the paired score difference is attributable to the reconstruction content itself. Same-geometry sharp/soft kernel pairs from one raw acquisition are the textbook reconstruction variant, so this stratum is plausibly non-empty; whether it is *large* is unknown and becomes a hard Stage 0 gate. Critically, this costs nothing new: `validation_metadata.csv` demonstrably carries those exact columns, since the released loader indexes them by filename. The gate is one metadata query on a file already first on the Stage 0 list.

This is stronger than the proposed matched-grid control, which I adopt but reassign. Resampling A onto B's grid does not reproduce reconstructing at B's parameters: trilinear interpolation is a low-pass operator, native sharp-kernel reconstruction is not, so `resample(A → grid_B)` carries A's frequency content plus an interpolation artefact that neither released volume has. Its correct use is a three-way decomposition, not a two-way subtraction — `d_grid = |s(A) − s(resample(A→grid_B))|`, `d_content = |s(resample(A→grid_B)) − s(B)|`, against `d_total = |s(A) − s(B)|`, symmetrised in both directions and checked for consistency. Its interpretation is asymmetric: a *large* `d_grid` is decisive (the pipeline is grid-fragile and no content attribution is available), while a *small* `d_grid` licenses only a weak content inference, because the interpolation artefact contaminates `d_content`. I will run it on the geometry-*mismatched* pairs as a secondary mechanistic analysis with that asymmetry stated in advance, and not as the identification strategy.

One point I want on the record without pretending it answers the objection. The primary scientific claim — the repeatability coefficient and what it bounds — needs the *composite* quantity, not the decomposed one. The deployed measurement is `released volume → released pipeline → score`. When a technologist's reconstruction choice moves that score, the clinical consequence is identical whether the mediator is trilinear interpolation in the loader or high-frequency kernel content in the image. Decomposition is a mechanistic question and it is downstream of the reliability question. The original one-sentence question asks *how much the score changes*, not *why*; the composite estimand answers it exactly, and the mechanistic arm is an addition to the study rather than a repair of it.

**What is lost.** Kernel-specific and content-specific language disappears for the corpus as a whole, and survives only inside a stratum whose size I cannot yet count — that is a genuine new failure mode, not a rhetorical hedge. If the geometry-matched stratum turns out to be empty or too small to estimate a per-concept ICC, the mechanistic arm collapses to the contaminated three-way decomposition and the study becomes pipeline repeatability under composite variants, exactly as the critic demands. Stratification also shrinks the usable N for the mechanistic arm, so the power calculation must run on the stratum rather than on the full paired set. And a specific bad case is now visible that the card did not anticipate: if CT-RATE's reconstruction variants differ predominantly in slice thickness rather than kernel at fixed thickness, the geometry-matched stratum is empty *by construction* and the interesting version of the experiment is unavailable. That is a real risk and the Stage 0 metadata query resolves it before any download.

**Identity check.** The one-sentence question is "when the same chest CT acquisition is reconstructed twice, how much does a released chest-CT foundation model's predicted abnormality concept change, and does the per-volume unit of analysis overstate precision." Nothing in this amendment touches either clause. The composite estimand answers the first clause on its own terms; the geometry-matched stratum and the decomposition are added mechanistic detail. The amendment restricts an *interpretive* claim I had no right to, not the measurement. Identity holds.

**Tally.** This is one concession and one amendment across two rounds. The concession removed a deliverable; this amendment removes a causal reading. Neither has touched the measurement itself, but a third hit that does would mean the candidate is a different study and should be re-scoped rather than patched again.

**Status:** OPEN

## Round 3 — CRITIC

**Position:** The amendment preserves the original question and adequately narrows the preprocessing claim, but the proposed primary statistic still cannot establish that ClassFine outputs are repeatable in the clinically relevant sense because a high pooled ICC can coexist with large within-scan changes and frequent decision reversals.

**Argument:** The new inspection of `data_inference_nii.py` materially answers Round 2: restricting causal language to geometry-matched pairs and treating all other pairs as an end-to-end composite is an adequate repair, and the revised design still asks how much scores change across reconstructions, so the identity check passes. The strongest remaining defect is now the measurement model. ICC is a ratio of between-scan variance to total variance. For an abnormality head whose scores separate obvious negatives from obvious positives, between-scan variance can be enormous, producing an ICC above 0.95 even if paired reconstructions move scores enough to reverse many borderline decisions. Conversely, a restricted or rare-finding stratum can produce a low ICC despite small absolute paired differences. Pooling heterogeneous reconstruction contrasts worsens the problem, and `ICC(2,1)` presumes a rater-like crossed structure that reconstruction IDs with inconsistent meanings and unequal group sizes do not supply. Therefore the anticipated negative—“ICC above 0.95 with low-single-digit flips”—is not yet decisive: 0.95 is unsupported, “low single digits” is unsupported, and threshold flips are uninterpretable unless the threshold is frozen from the released model or an external validation rule rather than selected after viewing these pairs. The primary analysis should instead estimate the paired score-difference distribution within prespecified reconstruction-contrast strata, including a repeatability coefficient or upper quantile of absolute change and crossing rates at frozen operational thresholds. A reassuring result requires a prespecified equivalence margin tied to an observable consequence, such as the largest score perturbation that does not materially change sensitivity/specificity or classifications on an independent calibration set. ICC can remain descriptive, but it cannot carry the equivalence claim. This matters to the benchmark arm too: patient-clustered intervals answer dependence, while paired-difference margins answer stability; neither substitutes for the other.

**What would change my mind:** Before inspecting paired ClassFine differences, freeze the checkpoint and preprocessing, define comparable reconstruction strata, identify thresholds without using the audit pairs, and justify per-output or grouped equivalence margins in score or decision space; then show confidence intervals for the upper paired-difference bound and threshold-crossing rate lie within those margins, with rare outputs declared exploratory when independent positive/negative scan counts are inadequate.

**Status:** OPEN

## Round 3 — PROPOSER

**Responding to:** ICC cannot carry the equivalence claim. It is a ratio of between-scan to total variance, so a head that cleanly separates obvious negatives from obvious positives can post ICC > 0.95 while paired reconstructions still move borderline scores enough to reverse decisions; a rare-finding stratum can post a low ICC despite trivial absolute differences. `ICC(2,1)` also assumes a crossed rater-like structure that unequal, inconsistently-meaning reconstruction IDs do not supply. Consequently the anticipated negative — "ICC above 0.95 with flip rates in the low single digits" — is unsupported in both of its numbers, and flip rates are uninterpretable unless the threshold comes from somewhere other than the audit pairs. Primary analysis should be the paired-difference distribution within reconstruction-contrast strata, with a repeatability coefficient and an equivalence margin tied to an observable consequence.

**Response:** AMEND

**Argument:** The objection is correct and I concede it without reservation: ICC(2,1) is demoted to descriptive, and both numbers in `anticipated_negative` — the 0.95 and the "low single digits" — are struck as illustrative cutoffs I had no basis for. The embarrassing part is that the fix was already inside the construct I claimed to be borrowing. Raunig et al., the QIBA Technical Performance working-group review (Stat Methods Med Res 2015;24(1):27–67; PMID 24919831; PMC5574197), states explicitly that a high ICC may mainly reflect between-subject heterogeneity in the sampled population and does not guarantee precision of quantification, which is why that tradition reports the repeatability coefficient from the within-subject variance instead. I imported the vocabulary of quantitative imaging biomarkers and then used the one statistic that tradition warns against. That is a self-inflicted wound, not a discovered limitation.

Three things I want to add rather than merely accept, because the critic's replacement needs specification before it is usable, and two of the three come from code I read after the objection.

**(a) The proposed replacement needs the same stratification it demands of ICC.** I checked what ClassFine actually emits: `scripts/zero_shot.py` applies `torch.nn.Softmax(dim=0)` over a two-element [present, absent] vector per pathology and writes `predicted_weights.npz`. The output is therefore a bounded probability, and the paired-difference distribution of a bounded score is structurally heteroscedastic — variance is compressed near 0 and 1 and maximal mid-range. A single pooled repeatability coefficient is misleading for exactly the reason a pooled ICC is: it averages over a variance that is a function of score location. So the RC and the upper quantile of |Δ| get reported within score-region bins as well as within reconstruction-contrast strata, with the bin assigned by the *mean* of the pair rather than by either member, Bland–Altman fashion, to avoid regression-to-the-mean selection. I will also report on the logit scale, where the variance is closer to constant, and state which scale the margin is defined on. This does not rescue ICC; it stops the replacement inheriting the same defect.

**(b) "Freeze the threshold from the released model" is not available, and the released code is why.** `scripts/eval.py` defines `choose_operating_point(fpr, tpr, thresholds)`, which walks the ROC and returns the sensitivity/specificity maximising Youden's J — selected on the evaluation set itself. There is no published fixed operating point to inherit, and the one that exists was chosen on the same reconstruction-duplicated validation data it reports. A flip rate computed at "the released threshold" would therefore be contaminated twice over. The concrete fix costs nothing: validation scans carrying exactly **one** reconstruction are disjoint by construction from the paired audit set, sit in the same distribution, and can supply a per-output Youden threshold that never sees a pair. If that singleton stratum proves too small for stable threshold estimation, the fallback is thresholds derived from the training split. Either is fixable in advance of looking at a single paired difference, which is precisely what the critic asked for. Whether the singleton stratum is large enough becomes a second hard Stage 0 gate alongside the geometry-matched count, and both are answered by the same metadata query.

**(c) A better consequence anchor than threshold crossing, which also links the two arms.** ClassFine is not deployed at an operating point; it is read through AUROC, a rank statistic. The decision-relevant consequence of a score perturbation for the way this model is actually used is rank displacement, not threshold crossing. So the prespecified primary consequence measure becomes the **reconstruction-swap AUROC delta**: recompute each output's AUROC with every multiply-reconstructed scan represented by its alternate reconstruction, over the distribution of swap assignments, with intervals bootstrapped at the patient unit. It needs no threshold, it is denominated in the units the benchmark already reports, and it gives the equivalence margin an anchor that is observable and external: the margin can be set against the published between-method gaps on this same validation split — the CT-Net / Swin3D / CT-ViT / global-local spread tabulated in arXiv:2503.20652 — read off those tables before I compute anything of my own. If a technologist's reconstruction choice moves AUROC as far as the method differences the benchmark is used to adjudicate, the benchmark cannot resolve those differences; that is an observable consequence, not a convention. Threshold-crossing rates at the singleton-derived thresholds drop to secondary, and per-output analyses are declared exploratory below a prespecified independent positive-scan count.

One bounded note on the benchmark arm, which does not reopen Round 1. `eval.py` bootstraps with `resample(idx, replace=True, random_state=i)` over row indices of the prediction array, 1000 replicates, percentile intervals. The published intervals therefore resample volumes and treat duplicate reconstructions of one scan as exchangeable rows. My Round 1 concession stands unchanged — this still cannot be evaluated without logits — but the target is no longer an abstraction: it is a named estimator in released code, and the comparison is that same function resampling scan or patient identifiers instead of rows.

**What is lost.** The reliability coefficient stops being the headline. With the attenuation bound already removed by the critique and ICC now demoted, what survives of the psychometric borrowing is thinner than the card claims: the insistence on a within-subject variance component, a repeatability coefficient reported with its scale and stratum, and a margin fixed before the data are seen. That is methodological hygiene, not a new bound, and the `cross_domain` block must be rewritten to say so — "what changes if the analogy is dropped" now answers *you would report a flip rate with no reference and no margin*, which still clears the charter's decoration test but at reduced value. Second loss: `anticipated_negative` can no longer be stated numerically at all until the margin is fixed from published tables and the singleton stratum is counted. Under the charter's classification the negative is decisive **only** conditional on a prespecified, powered margin; unconditionally it is sensitivity-limited. I recommend `negative_result_value` drop from 5 to 4 pending margin prespecification, and that the reviewer treat 4 as itself conditional on the two Stage 0 gates returning non-empty.

**Identity check.** The question remains "when the same chest CT acquisition is reconstructed twice, how much does a released chest-CT foundation model's predicted abnormality concept change, and does the per-volume unit of analysis overstate precision." This amendment changes how the paired scores are summarised, not which scores are compared or on what. The measurement — released volume pair, unmodified checkpoint, unmodified preprocessing, paired difference — is byte-identical to what Round 2 left. Identity holds. I note that in Round 2 I drew the line at "a third hit that touches the measurement itself," and that this hit lands on the summary statistic instead. That distinction is real but it is thin, and I should not be allowed to invoke it a second time.

**Tally.** One concession and two amendments across three rounds. The concession removed a deliverable, the first amendment removed a causal reading, this one removes a primary statistic and an anticipated result. Nothing has yet touched what is measured, but the card that goes to feasibility is meaningfully poorer than the card that entered this debate, and the revision should present it as such rather than absorbing three hits into unchanged prose.

**Status:** CONVERGED

I accept the whole of the critic's prespecification list — frozen checkpoint and preprocessing, comparable strata, audit-pair-independent thresholds, justified margins, exploratory labelling of underpowered outputs — and (a)–(c) above fill the two places where that list was not yet operational: where the thresholds come from, and what the margin is denominated in. What I cannot supply is the demonstration the list ends with, that the intervals fall inside the margins. That requires gated data and a GPU, so it is the next gate rather than this debate's business. There is no remaining disagreement about the design; there are three empirical gates — geometry-matched pairs exist, singleton scans suffice for thresholds, per-output positive counts support the analysis — any of which can still kill the study before it runs.


===== ideas/004/idea_card.json =====
{
  "id": "C1",
  "search_mode": "B",
  "title": "The free test-retest experiment already inside CT-RATE: duplicate reconstructions of the same acquisition",
  "question": "When the same chest CT acquisition is reconstructed twice, how much does a released chest-CT foundation model's predicted abnormality concept change, and does the CT-RATE validation benchmark's per-volume unit of analysis overstate the precision of every number reported on it?",
  "why_unasked": "Reconstruction-kernel sensitivity is a well-studied nuisance in radiomics and in CT harmonisation, always framed as domain shift between cohorts. Inside CT-RATE the same variation exists as a paired repeat measurement of one patient's anatomy - 25,692 scans expand to 50,188 volumes through reconstructions - but the corpus was built to be trained and evaluated on, so the duplicates were absorbed as extra samples rather than recognised as repeats. Two habits keep the question invisible. First, the field's unit of analysis is the volume, so a validation set described as 3,075 volumes reads as 3,075 cases when it is 1,314 patients. Second, reliability is not part of the reporting vocabulary in this literature at all: papers report AUROC, never a repeatability coefficient, so there is no slot in a results table where this number would go. Nobody left it as future work because nobody framed the duplicates as repeats.",
  "concept_definition": "A concept here is one of the 18 named thoracic abnormality categories that CT-RATE attaches to each volume (pleural effusion, emphysema, lymphadenopathy, and so on). These are named radiological findings with independent clinical definitions, not task-invented class labels. Their CT-RATE provenance is weak - a RadBERT text classifier applied to the report - and I make no claim that they are validly assigned. That weakness is precisely why this candidate is designed around the model's *output score* for a concept and not around the label: a test-retest measurement compares the model to itself on two images of the same anatomy and requires no ground truth at all. Label provenance cannot contaminate the primary readout. It re-enters only in the secondary benchmark-correction arm, and is bounded there.",
  "keystone_prerequisite": "CT-RATE contains more than one reconstruction of the same acquisition (same patient, same scan), and those pairs are identifiable from released filenames or metadata without needing the raw sinograms - so that paired volumes with identical underlying anatomy exist and can be found.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "I fetched the raw official CT-CLIP README at raw.githubusercontent.com/ibrahimethemhamamci/CT-CLIP/main/README.md. It documents the naming convention as split_patientID_scanID_reconstructionID, giving the worked example valid_53_a_1 where the trailing index is the reconstruction number and the preceding letter is the scan from that patient. It states the dataset 'comprises 25,692 non-contrast chest CT volumes, which expand to 50,188 volumes through various reconstructions,' i.e. a mean of ~1.95 reconstructions per acquisition dataset-wide, and that CT-CLIP, VocabFine, ClassFine and RadBertClassifier checkpoints are hosted on HuggingFace. Separately I fetched the HuggingFace file tree at huggingface.co/datasets/ibrahimhamamci/CT-RATE/tree/main/dataset and confirmed the folders anatomy_segmentation_labels/, metadata/, multi_abnormality_labels/, radiology_text_reports/, train/, valid/, ts_seg/, vqa/; inside multi_abnormality_labels/ the files are train_predicted_labels.csv (2.76 MB) and valid_predicted_labels.csv (174 kB), and inside metadata/ they are Metadata_Attributes.xlsx, train_metadata.csv, validation_metadata.csv, no_chest_train.txt, no_chest_valid.txt. Independently, arXiv:2503.20652 (HTML read directly) states the split as '17,799 unique patients corresponding to 34,781 CT volumes for the train set, 1,314 unique patients, corresponding to 3,075 CT volumes for the validation set' - 2.34 volumes per validation patient. The pairing structure therefore exists, is encoded in filenames, and is dense enough to matter. RESIDUAL, stated plainly: I could not open valid_predicted_labels.csv or validation_metadata.csv because the repository is gated, so I have not counted how much of the 2.34 volumes-per-patient ratio is multiple reconstructions of one scan versus multiple scans of one patient. The dataset-wide 25,692-to-50,188 expansion is reconstruction by construction, but the validation-split breakdown is inferred. Counting it is a one-CSV, no-GPU task and is step zero of the experiment.",
  "closest_prior_work": [
    {
      "citation": "Hamamci I.E. et al. Developing Generalist Foundation Models from a Multimodal Dataset for 3D Computed Tomography.",
      "identifier": "arXiv:2403.17834 (v3, 4 Apr 2025)",
      "verification": "INSPECTED (arXiv abstract page)",
      "what_it_did": "Released CT-RATE (25,692 non-contrast chest CT volumes, 21,304 patients, paired reports) and the CT-CLIP / CT-CHAT models as open source.",
      "what_it_did_not_do": "Reports evaluation per volume. Does not report any within-scan repeatability of its own predictions, and does not treat the reconstruction duplicates as anything other than additional samples."
    },
    {
      "citation": "Imitating Radiological Scrolling: A Global-Local Attention Model for 3D Chest CT Volumes Multi-Label Anomaly Classification.",
      "identifier": "arXiv:2503.20652",
      "verification": "INSPECTED (arXiv HTML)",
      "what_it_did": "Benchmarks on CT-RATE against 3D CNN, CT-ViT, Swin3D and CT-Net baselines; states the validation split as 1,314 patients / 3,075 volumes; reports aggregate AUROC, accuracy, F1 across the 18 abnormalities.",
      "what_it_did_not_do": "Evaluates over volumes with no clustering by patient or scan, and reports no per-abnormality breakdown. This is the concrete instance of the unit-of-analysis habit the candidate targets - and it is representative, not an outlier."
    },
    {
      "citation": "Yamagishi Y. et al. Large Language Model-Assisted Cleaning of Report-Derived Labels in a Large-Scale Chest CT Dataset.",
      "identifier": "arXiv:2606.22382 (submitted 21 June 2026)",
      "verification": "INSPECTED (arXiv abstract page)",
      "what_it_did": "Used GPT-5.4 to relabel 24,434 CT-RATE reports across the 18 abnormality categories; 96.4% agreement with the original labels, Cohen's kappa 0.884; lymphadenopathy worst; radiologist adjudication favoured the LLM labels in 72 of 97 discordant cases; cleaned labels to be released.",
      "what_it_did_not_do": "Addresses label fidelity to the report. Says nothing about duplicate reconstructions, about the unit of analysis, or about model repeatability. This paper is also the reason a CT-RATE label-provenance candidate is NOT in this portfolio - I intended to write one and found it substantially pre-empted."
    },
    {
      "citation": "CT reconstruction-kernel effects on quantitative imaging: e.g. deep-learning kernel conversion for interstitial lung disease quantification (Acad Radiol, S1076-6332(23)00302-1) and kernel-induced radiomic feature variability via noise power spectra.",
      "identifier": "S1076-6332(23)00302-1 and related",
      "verification": "SEARCH_SUMMARY_ONLY",
      "what_it_did": "Establishes at length that reconstruction kernel changes move quantitative CT biomarkers and degrade model accuracy, and develops harmonisation and kernel-conversion remedies.",
      "what_it_did_not_do": "Concerns handcrafted quantitative biomarkers and radiomic features, and frames the effect as accuracy loss under domain shift. It does not express the effect as a reliability coefficient for a *named clinical concept* emitted by a foundation model, does not derive the attenuation bound that such a coefficient places on downstream claims about that concept, and does not touch the benchmark-precision consequence. This is the honest delta and it is a narrower one than the headline suggests: that kernels move model outputs is expected, not news. What is news would be the size of the coefficient, and what it forbids."
    }
  ],
  "existing_assets": [
    "CT-RATE volumes, 18-abnormality label CSVs, per-volume metadata CSVs and free-text reports, all in one HuggingFace repository.",
    "Released checkpoints: CT-CLIP, VocabFine, ClassFine (supervised 18-abnormality classifier) and RadBertClassifier - so the reliability arm is inference-only with no training.",
    "The pairing key is free: it is in the filename, requiring no linkage work of the kind that killed idea 001.",
    "Published benchmark numbers on the same validation split to compare a corrected computation against.",
    "HuggingFace supports selective per-file download, so the volume subsample can be fetched without pulling the whole corpus."
  ],
  "smallest_decisive_experiment": "Stage 0, no images and no GPU, hours not days. Download only valid_predicted_labels.csv (174 kB) and validation_metadata.csv. Parse the filenames into (patient, scan, reconstruction). Report: how many validation scans carry two or more reconstructions; the distribution of reconstructions per scan; the intra-cluster correlation of the 18 label vectors within a scan (which is 1.0 by construction if reconstructions share a report - confirm rather than assume); and the resulting design effect, i.e. the factor by which a naive per-volume confidence interval is too narrow relative to a scan-clustered one. This alone settles the unit-of-analysis claim with arithmetic and no model. Stage 1, bounded GPU. Take every validation scan with two or more reconstructions, or a 300-scan subsample if that set is large. Run the released ClassFine checkpoint once per volume. Primary readout: per-concept agreement between paired reconstructions - ICC(2,1) on the continuous score, plus the flip rate of the thresholded decision, plus a minimum detectable change. Secondary readout: recompute the published AUROC restricted to one randomly chosen volume per scan, resampled, with scan-clustered bootstrap intervals, and report the shift against the published per-volume number. Control that makes Stage 1 interpretable: run the model twice on one identical volume to establish the pure software noise floor, so that reconstruction-induced variation is measured against it rather than against zero.",
  "alternative_explanations": [
    "The paired volumes are not the same acquisition but repeat scans of the same patient, in which case genuinely different anatomy would explain any disagreement and the whole framing collapses. RULED OUT by design: the filename fixes scanID, and the metadata check in Stage 0 (acquisition time, series description, reconstruction parameters) confirms it. This is the single most important check and it comes first.",
    "The variation is preprocessing and resampling instability in the inference pipeline rather than anything about the image content. RULED OUT by the identical-volume repeat control, which gives the software noise floor that reconstruction-induced variation must exceed.",
    "The benchmark shift in the secondary arm is driven by label duplication rather than by anything about model behaviour. SEPARATED, not ruled out: the reliability arm uses no labels whatsoever, so a finding there stands regardless of what the label arm shows. The two arms fail independently, which is the point of splitting them.",
    "Residual that the design does NOT rule out: scans selected for multiple reconstructions are not a random sample - a lung kernel is more likely to be reconstructed when lung pathology is suspected. The measured reliability therefore applies to the subpopulation of multiply-reconstructed scans and should be reported as such, not generalised to the corpus. Reporting the case mix of that subpopulation is the mitigation; there is no way to remove the selection with these data."
  ],
  "anticipated_negative": {
    "classification": "decisive",
    "reasoning": "If paired reconstructions produce near-identical concept scores (say ICC above 0.95 with flip rates in the low single digits) and the scan-clustered benchmark recomputation reproduces the published numbers within their intervals, that is a clean, citable robustness result: the CT-RATE leaderboard is not inflated by duplication, and these concept outputs survive the reconstruction variation actually present in the corpus. That meaningfully weakens a live worry rather than merely failing to confirm it, so it is type 1. The design effect calculation in Stage 0 is arithmetic and yields a reportable number whichever way it comes out."
  },
  "remaining_legwork": [
    "Accept the HuggingFace gated-access terms. UNKNOWN whether approval is automatic on acceptance or manually reviewed; this is on the critical path and costs nothing to start, so it should be done first. License is CC BY-NC-SA 4.0, research use only, no redistribution.",
    "Count the validation-split reconstruction structure from the label CSV - the residual left open by the keystone check. Half a day.",
    "Confirm from Metadata_Attributes.xlsx and validation_metadata.csv that reconstruction parameters (kernel, slice thickness, kVp) are recorded per volume, which is needed to describe what varies between a pair. If they are not recorded, the reliability number is still valid but becomes uninterpretable as to cause, and the study should be reported as repeatability-under-unspecified-reconstruction-variation.",
    "Selective download of the paired subsample. Chest CT volumes are large; budget disk and time, and prefer the smallest sufficient scan count established by a power calculation on the ICC.",
    "Statistical development: scan-clustered bootstrap, ICC with confidence intervals for a 18-outcome multiple-comparison setting, and a prespecified equivalence margin so that a high-reliability result is reported as equivalence rather than as non-rejection.",
    "Expected time to first decision: Stage 0 within two days of access being granted. Stage 1 within one to two weeks."
  ],
  "cross_domain": {
    "borrowed_construct": "Test-retest reliability and the repeatability coefficient from classical test theory, as operationalised for imaging in the quantitative imaging biomarker tradition (ICC, repeatability coefficient, minimum detectable change).",
    "measurement_it_implies": "Report ICC(2,1) per concept over reconstruction pairs with confidence intervals, plus a minimum detectable change; then apply the attenuation bound - any correlation between that concept score and an external outcome cannot exceed the square root of its reliability. That converts a repeatability number into an explicit ceiling on downstream claims.",
    "what_changes_if_the_analogy_is_dropped": "You would report a flip rate and stop. A flip rate has no interpretation without a reference: 8% sounds tolerable and 8% sounds alarming depending on what you compare it to. The reliability coefficient supplies the comparison and the attenuation bound turns it into a statement of the form 'no study using this concept score can report a correlation above X, so a published correlation of Y is impossible.' That statement does not exist without the borrowed construct, so this is not decoration."
  },
  "scores": {
    "clarity": {
      "value": 5,
      "why": "One paired comparison on identical anatomy, one reliability coefficient per concept, one recomputed benchmark number. The question states its own null."
    },
    "identifiability": {
      "value": 4,
      "why": "The paired design fixes patient, anatomy, pathology and label by construction, and the software-noise control separates pipeline jitter from image content. Held below 5 by the non-random selection of which scans get multiple reconstructions, which the design can describe but cannot remove."
    },
    "medical_relevance": {
      "value": 4,
      "why": "A concept output that changes when the technologist picks a different reconstruction is not a finding a clinician can act on, and the attenuation bound limits every downstream claim built on that concept. Held below 5 because the study audits measurement stability rather than changing a diagnostic pathway."
    },
    "interest": {
      "value": 4,
      "why": "'The benchmark has been counting the same patient twice, and the model disagrees with itself about the same lungs' is graspable outside the subfield. Held below 5 because reconstruction sensitivity is not itself a surprise to anyone in CT."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Data, labels, metadata, pairing key and four released checkpoints all exist; the pairing needs no linkage work. Short of 5 only because no prior repeatability analysis exists to build the statistics on."
    },
    "feasibility": {
      "value": 4,
      "why": "Cap lifted, keystone INSPECTED_TRUE. Stage 0 needs one 174 kB CSV and no GPU. Stage 1 is inference-only with a released checkpoint on a bounded subsample. Held to 4 by the size of 3D CT downloads and the gated-access step."
    },
    "data_readiness": {
      "value": 3,
      "why": "Fully public in the sense that anyone can get it, but behind a click-through research-use agreement whose approval mechanism I did not verify. Under the charter that is accessible-with-work, not directly usable."
    },
    "evaluation_readiness": {
      "value": 4,
      "why": "ICC, repeatability coefficient and clustered bootstrap are all standard and have accepted reporting conventions. Only the mapping onto the 18-concept multiple-comparison structure needs specification."
    },
    "negative_result_value": {
      "value": 5,
      "why": "A high-reliability, benchmark-unchanged outcome is a decisive reassurance for a corpus the field is standardising on, and is as publishable as the positive."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Cap lifted by the keystone, but held at 3 honestly: I searched arXiv and general web indexes only, found no within-scan repeatability analysis of CT-RATE, and did not search MICCAI, SPIE Medical Imaging or the medical physics literature, which is exactly where a repeatability study would live if one exists."
    }
  },
  "priority_score": 4.1,
  "priority_arithmetic": "0.20*4 (feas) + 0.15*4 (ident) + 0.15*4 (med) + 0.10*4 (legwork) + 0.10*4 (interest) + 0.10*5 (clarity) + 0.10*5 (neg) + 0.05*3 (data) + 0.05*3 (novelty) = 0.80+0.60+0.60+0.40+0.40+0.50+0.50+0.15+0.15 = 4.10",
  "regret": {
    "value": 4,
    "why": "A paired repeat-measurement design normally has to be funded and collected. This one is sitting in the filenames of the corpus the field is currently building on."
  },
  "recommendation": "SHORTLIST",
  "unverified_claims": [
    "How many validation-split scans actually carry two or more reconstructions. The dataset-wide 25,692-to-50,188 expansion is documented, but the validation breakdown is inferred from the 1,314-patient / 3,075-volume figure. FIRST THING TO CHECK; the candidate's cost profile depends on it.",
    "Whether the HuggingFace gate is auto-approved on acceptance or manually reviewed, and the turnaround if manual.",
    "Whether validation_metadata.csv and Metadata_Attributes.xlsx record reconstruction kernel and slice thickness per volume.",
    "Whether all reconstructions of one scan share a single report and therefore a single label vector. Strongly implied by the one-report-per-scan design but not confirmed against the CSV.",
    "The ClassFine checkpoint's exact input preprocessing and whether it is deterministic at inference. Needed before the software-noise control can be interpreted.",
    "Whether any CT-RATE benchmark paper reports per-abnormality AUROC. arXiv:2503.20652 does not; the CT-CLIP paper may. Not confirmed, and the secondary arm is more informative if per-abnormality numbers exist to compare against.",
    "That no repeatability analysis of CT-RATE exists. Not established. Searches did not cover MICCAI, SPIE, Medical Physics or Radiology: Artificial Intelligence."
  ]
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

