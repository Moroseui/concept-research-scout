You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/007
Preserve existing files unless the task explicitly requires an update.
Do not claim novelty without verified primary sources.
Do not write code unless this is the probe_code stage and human approval exists.

===== CHARTER.md =====
# Research charter

## The driver

Medical imaging models sometimes outperform physicians, or predict things
physicians cannot predict at all. When that happens the model is using signal
that is present in the image and that human readers do not knowingly use.
Sometimes that signal is a real biological or physical fact nobody had
articulated. Sometimes it is an artifact of how the data was made.

**The program: decode what medical imaging models have found, and determine
which kind of thing it is.**

Concepts enter here as the *readout language* — a way to say what the model
found — rather than as a supervision constraint imposed in advance. That is
the inverse of standard concept-bottleneck work and it is the more interesting
direction.

### The deliverable

**Every candidate must end in a sentence a radiologist could read and either
agree or disagree with.**

Of the form: *the model is using X*, where X is a named anatomical,
physiological, or physical thing. Not "the model is not using the scanner."
Not "performance drops when we ablate region R." A positive statement, in
words a physician already has.

That sentence is the point. Everything else is what makes it credible.

### The three rungs

State which rung the candidate reaches and what would move it up.

1. **The model uses signal X.** Ablation, probing, perturbation, occlusion
   with proper controls. Comparatively easy.
2. **X is not an artifact.** Not scanner, site, protocol, reconstruction,
   position, dose, habitus, referral pattern, or label leakage. This is the
   validity gate — necessary, and where most projects quietly fail.
3. **X is a named, human-legible thing.** The deliverable sentence.

Rung 2 is a **gate, not a destination.** A study that only eliminates
confounds tells a physician what the model is *not* doing, which does not help
them understand a decision. Confound elimination earns the right to make the
rung-3 claim; it is not the claim.

A candidate that can reach only rung 2 is allowed, but must say so and must
name what would be needed to reach rung 3. A candidate that reaches rung 1 and
asserts rung 3 is the standard failure of this literature.

### The hard constraint on X

**X must be independently measurable without a human annotator.**

This is the constraint that makes the program feasible for you, and it is not
optional. Six prior candidates died because they required knowing what a human
saw when they assigned a label, and that was undocumented, unavailable, or
contaminated. Do not walk back into that.

X qualifies if it can be computed from the image by an existing, citable tool
or a well-defined measurement. Examples of the right shape:

- parenchymal texture statistics, emphysema percentage, density histograms
- vessel blood volume by calibre, airway wall thickness, luminal area
- muscle or fat attenuation in Hounsfield units, sarcopenia indices
- cardiac chamber size, aortic diameter, coronary calcium
- bone mineral density, vertebral morphometry
- organ volumes from an off-the-shelf segmentation tool

X does **not** qualify if establishing it requires a radiologist to look at
images and agree, or if it exists only as a rating in a dataset whose
annotation conditions are undocumented.

The test: *could you compute X on a scan the model has never seen, today,
without asking anyone?* If not, pick a different X.

This constraint is what separates a concept the model found from a concept you
asserted.

### The two precedents to hold in mind

- Retinal fundus photographs predict patient sex at near-ceiling accuracy while
  ophthalmologists are at chance (Poplin et al. 2018). Real signal, previously
  unarticulated, and it opened a line of work. Related: histopathology slides
  predicting driver mutations, ECG predicting ventricular dysfunction.
- Chest radiographs predict self-reported race across modalities and
  preprocessing, robustly, and after years of investigation nobody can say what
  the signal is (Gichoya et al. 2022). Real, reproducible, and not a discovery.

Both are true. The difference between them is rung 2.

## Two entry points, both allowed

### Entry point 1 — a known gap

Start from a documented case where a model beats human readers, or predicts
something readers cannot. The gap is the evidence that signal exists; the
question is what it is. More grounded, easier to verify, less likely to be
vapor.

### Entry point 2 — looking for the unexpected

Start from a model that merely performs well and ask what it is using that
nobody expected. No documented gap to anchor on. This is where genuinely novel
findings would come from, and also where unfalsifiable speculation comes from.

Entry point 2 candidates carry a higher burden: name the specific measurement
that would detect the unexpected signal, and the specific artifact it would be
confused with. "Probe the representation and see what's there" is not a design.

## Search modes

Each candidate declares `search_mode`.

- **Mode A — the unfinished story.** A paper stops one experiment short.
  Citation-anchored: strong evidence, limited imagination. It can only surface
  questions the literature already framed, and it selects for gaps authors
  chose to leave — sometimes because the data to close them does not exist.
- **Mode B — the unasked question.** Nobody framed it. Found in the space
  between two things that should connect and do not. What would you check if
  you did not trust this result, and why has nobody published that check?
- **Mode C — speculative.** Explicitly permitted to be unlikely. Lower bar on
  feasibility and prior work; **higher** bar on mechanism. A Mode C candidate
  must name the physical or biological quantity it thinks the model is using,
  and the measurement that would show it. Cross-domain borrowing belongs here.

Per cycle: **1 Mode A, 2 Mode B, 2 Mode C.** Five candidates.

Mode C candidates are scored on interest, novelty, and mechanism clarity rather
than feasibility. Do not demote a Mode C candidate for being hard. Do demote it
for being untestable.

## Guard against fluent nonsense

The characteristic failure of speculative generation is a connection that reads
beautifully and implies no measurement. Free energy and diagnostic uncertainty.
Sparse coding and concept bottlenecks. Predictive processing and radiologist
priors. These produce excellent sentences and no experiment.

Every cross-domain or speculative candidate must answer:

**What would be different if the analogy were dropped?**

If the answer is "nothing" — if you would run the same code either way — the
analogy is decoration. Rewrite without it or discard.

## Learn from the record

`evidence/decisions.md` is injected into your context. It is the accumulated
record of what has been proposed, critiqued, and killed, with reasons.

**Read it before proposing, and state explicitly for each candidate whether it
dies the same way as a prior candidate.**

The dominant failure so far, five of six kills, is **annotation provenance**:
the study depended on knowing who assigned the labels and what they could see,
and that was undocumented, unavailable, or contaminated by peer exposure.
Specifically:

- LIDC diagnosis file: patient-level, numbering inconsistent with the XML, only
  18 nodules reliably linkable.
- Derm7pt: whether checklist annotators saw the clinical photograph is
  undocumented, making cross-modality results ambiguous.
- BUS-BRA: releases BI-RADS assessment categories, not lexicon descriptors —
  there were no concepts to intervene on.
- LIDC semantic ratings: released reads are from the unblinded phase after
  readers saw each other's marks, and reader IDs are not stable across scans,
  so they are not independent measurement methods.

The one candidate that survived did so by **not requiring labels at all** in
its primary readout — comparing a model to itself across two reconstructions of
identical anatomy. That structural move is available more often than it is
used. Look for it.

Required per candidate: `dies_like_prior` — either the prior candidate it
resembles and why this one is different, or an explicit "no prior failure mode
applies, because…"

## The keystone prerequisite

Name the single fact which, if false, makes the study impossible or
uninterpretable. State whether it has been **directly inspected** — the actual
file, table, schema, or methods section — or merely inferred from a collection
page, abstract, or search summary.

`feasibility` and `novelty_confidence` are capped at 3 unless
`keystone_status` is `INSPECTED_TRUE`. Mode C candidates may honestly report
`NOT_INSPECTED` and accept the cap; that is expected and not a defect.

**The wrong-keystone error has now occurred three times.** It is the dominant
failure of this loop, ahead of annotation provenance. In each case the easy
adjacent fact was verified and the load-bearing one assumed:

- idea 005: verified that multiple opinions exist per lesion (true); needed
  that they are independent measurement methods (false).
- idea 006: verified that exterior voxels survive preprocessing (true); needed
  that a body-excluded volume is in-distribution (unverified, and probably
  false).

Procedure, mandatory: write the keystone, then write the sentence *"if I have
only verified the nearest checkable thing, what am I still assuming?"* and
answer it. If the answer is load-bearing, that is the real keystone.

Watch for the same error: "Multiple opinions exist
per lesion" was inspected true. "Those opinions constitute independent
measurement methods" was the real keystone, and it was false. State the keystone
as the thing your inference needs, not the thing that is easy to check.

## Claim identifiability

Can the design distinguish the claimed explanation from the plausible
alternatives? A compelling headline is not identifiability. List the two or
three most plausible alternative explanations for a positive result and say
which ones the design rules out.

For this program specifically, the standing alternatives are: scanner or
vendor, acquisition protocol, reconstruction, site, patient positioning, body
habitus, disease prevalence in the sampled population, referral pathway, and
label leakage from the report. Address them by name.

## Negative results

Classify the anticipated negative:

1. **Decisive** — meaningfully weakens the hypothesis.
2. **Sensitivity-limited** — may reflect power, modelling, or metric choice;
   needs an equivalence margin or minimum-detectable-effect.
3. **Uninterpretable** — several explanations survive.

Only type 1 counts toward negative-result value. Non-rejection is not evidence
of independence.

## Domain focus

**Radiology, with emphasis on CT and 3D volumetric imaging.** Vascular and
tubular anatomy, chest CT, and CT-report paired corpora are especially
relevant. Retinal, ECG, and pathology precedents may be cited as motivation but
the experiment should land in radiology where possible.

Per cycle: at least three of five candidates in radiology or CT. At most one
dermatology candidate. No more than two on any single dataset.

## Constraints

- Compute: Colab Pro+ or equivalent single-GPU sessions.
- No dependence on unconfirmed DUA-gated data.
- No large-scale radiologist annotation campaign.
- Literature claims require primary-source verification.
- Keep confirmatory and exploratory work separate.
- Never tune on the untouched test set.
- Prefer designs whose primary readout does not depend on label quality.

## What counts as success

- A clear positive result.
- A decisive negative — including "the signal was an artifact."
- Evidence that a popular assumption is unsupported.
- Identification of a decisive confound.
- A feasibility result that prevents wasted effort.


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

## Mode C scoring

Mode C (speculative) candidates are scored differently. Do **not** demote a
Mode C candidate for low feasibility or thin prior legwork — that is what the
mode is for. Do demote it for being untestable.

For Mode C, replace the priority weighting with:

- 30% mechanism clarity (is the suspected physical/biological signal named?)
- 25% identifiability
- 20% interest
- 15% medical relevance
- 10% clarity

Report feasibility and novelty confidence for information, outside the score.
A Mode C candidate that would take three weeks is fine. One that could not be
falsified in three years is not.

**Mechanism clarity, 1-5:**

| 1 | 3 | 5 |
|---|---|---|
| "probe the representation and see what is there" | a named signal family, unclear how to isolate it | a specific physical or biological quantity, and the measurement that would show the model uses it |


===== evidence/decisions.md =====
# Decision ledger

Record decisions as evidence statements rather than broad permanent bans.

Format:

## YYYY-MM-DD — IDEA-ID — ADVANCE | REVISE | PAUSE | REJECT

**Question:**

**Evidence:**

**Scope of conclusion:**

**What this does not establish:**

**Revisit trigger:**

## 2026-08-04 — Idea 001 REJECTED (LIDC concepts vs diagnosis)
Zinovev et al. 2012, J Digit Imaging 25:423-436 (DOI 10.1007/s10278-011-9445-3)
VERIFIED by reading the paper: diagnosis file is patient-level, numbering
inconsistent with LIDC XML, only 18 nodules reliably linked (8 mal / 9 ben /
1 indet) via single-nodule-patient restriction. Too small for the proposed
paired AUC analysis.
Reopen only with a released, independently validated diagnosis-to-XML-nodule
mapping retaining all eight semantic ratings, meeting a prespecified CI-width
target before model fitting.
Separate unresolved objection, raised in critique but never debated: the eight
characteristics and the malignancy rating come from the same reader in the same
session, so concept-to-suspicion prediction measures rating-form consistency,
not concept validity.

## 2026-08-04 - Idea 004 Stage 0 COMPLETE
3,039 validation volumes / 1,564 scans / 1,304 patients.
1,432 of 1,564 scans multi-reconstruction (92%).
425 strictly clean geometry-matched kernel pairs after excluding slice-count,
position, and acquisition-parameter drift.
Contrasts: Br40f|Br60f 237, Bl56f|Br40f 126, Bl57d|Br36d 58, Br40f|Br44f 4.
462/464 Siemens - findings vendor-specific, state as limitation.
Labels identical across reconstructions: 1.00 (exact duplication).
No released per-volume ClassFine scores: CT-RATE has only RadBERT report
labels; CT-CLIP GitHub v1.0.0 has no release assets; checkpoints are not on
the authors HF account. Inference must be run locally.
Scope: download 850 volumes (425 pairs), not 3,039. Inference code exists at
scripts/data_inference_nii.py and run_forward_data.py.

## 2026-08-04 - Idea 002 PAUSE (Derm7pt clinical photo concepts)
Annotation provenance undocumented: unknown whether checklist annotators saw
the paired clinical photograph. A positive result would have two materially
different explanations. Unblocked only by author correspondence.

## 2026-08-04 - Idea 003 REJECT (BI-RADS intervention realism)
BUS-BRA releases BI-RADS assessment categories, not lexicon descriptors - no
concepts to intervene on. Debate ran six rounds; amendments achieved
feasibility by abandoning the intervention question entirely.

## 2026-08-04 - Idea 005 PAUSE (LIDC concept discriminant validity)
MTMM requires independent measurement methods. LIDC released reads are from the
unblinded phase after readers saw each others marks, and reader IDs are not
stable across scans. Keystone error: verified that multiple opinions exist
(true) rather than that they are independent measurement methods (false).

## 2026-08-05 - Idea 006 PAUSE (CT-CLIP non-tissue voxel prediction)
Patient-deletion is an extreme OOD intervention; neither direction identifies
exterior reliance during intact inference. Wrong-keystone error, third
occurrence: verified that exterior voxels survive preprocessing (true) when the
inference required that a body-excluded volume is in-distribution (unverified).
Reopening condition: inspect CT-CLIP training loader for large-region masking
or cutout with matching fill value.
SPIN-OFF, endorsed by both critique and debate: hold every voxel inside a
dilated patient contour fixed and substitute only the scan exterior between
geometry-matched scans; measure paired ClassFine score change. Separate
estimand, enter as a new candidate.


===== ideas/007/README.md =====
# Idea 007: The same patient, twice, ten minutes apart, differing only in how much air is in the lungs

Selected from scouting cycle 004, candidate 3.


===== ideas/007/critique.md =====
FATAL OBJECTION: The proposed volume slope cannot identify lung inflation as the model's cue because density, anatomy motion, field-of-view/resampling, and 4DCT reconstruction artifacts all change with measured lung volume.
EVIDENCE: TCIA collection DOI 10.7937/3ppx-7s22; CT-CLIP official preprocessing/inference repository; Yamamoto et al., DOI 10.1118/1.3488984.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION

# Adversarial review

## Bottom line

The paired breath-hold data are real, public, small, and unusually useful. The experiment is worth doing. The interpretation in the card is not yet earned.

The clean estimand is: **how much do CT-CLIP finding scores change between a real inspiratory and expiratory acquisition of the same patient in one session?** That is a clinically relevant robustness question. The present card instead claims the model is specifically using total lung volume and the attenuation it sets, and treats the ten 4DCT phases as a mechanism-identifying dose response. Neither move is valid. A score-volume association cannot separate volume from the many image properties that deterministically accompany breathing, and phase-binned 4DCT adds reconstruction artifacts rather than resolving that ambiguity.

This is a revision, not a rejection, because the paired breath-hold comparison remains unusually well controlled and needs no labels or invented counterfactuals. The claim must drop from “specific cue decoded” to “respiratory-state sensitivity measured,” unless an additional intervention separates the candidate cues.

## What is verified

- **Verified fact:** TCIA states that all 20 subjects have inhale/exhale breath-hold CT and a free-breathing 4DCT acquired in one session on one Siemens Biograph mCT.S/64. It also states that the breath holds targeted approximately 80% of maximum inhalation and exhalation. The collection is 14.93 GB and complete. Primary dataset record: [TCIA CT-vs-PET-Ventilation-Imaging](https://www.cancerimagingarchive.net/collection/ct-vs-pet-ventilation-imaging/), DOI 10.7937/3ppx-7s22.
- **Verified fact:** The collection record says 20 inhale/exhale BHCT scans were successfully acquired for 20 patients. This resolves the card's listed uncertainty about whether the pair exists for every subject at the collection level, although series-level usability still requires direct DICOM inspection.
- **Verified fact:** CT-CLIP's official repository provides inference code and links a ClassFine checkpoint; it reports inference on 18 abnormalities and says inference can run on smaller GPUs. [Official CT-CLIP repository](https://github.com/ibrahimethemhamamci/CT-CLIP); Hamamci et al., arXiv:2403.17834, DOI 10.1038/s41551-025-01599-y.
- **Verified fact:** The released 18-label vocabulary includes emphysema, atelectasis, lung opacity, and consolidation. It does **not** include mosaic attenuation. “Mosaic attenuation score” must be removed from the question and deliverable unless a different, explicitly validated model is introduced.
- **Verified fact:** The checkpoint is not literally ungated. It is linked inside the gated CT-RATE Hugging Face dataset repository and requires the click-through/contact-sharing access already noted elsewhere in this repository. The imaging corpus is ungated; the proposed model weights are not. This is a modest access dependency, not a fatal data barrier.
- **Source-supported interpretation:** The published Eslick study used these acquisitions for CT ventilation rather than diagnostic-model robustness. Eslick et al., *Radiotherapy and Oncology* 2018;127:267-273, PMID 29290405. I found no verified primary study that already reports CT-CLIP finding-score changes across this paired BHCT corpus.
- **Not established:** Novelty remains “not found,” not proven. The search did not exhaust conference proceedings, benchmark supplements, or analyses published after the CT-CLIP paper.

## Decisive identifiability problem

The card says that a monotone score relationship across ten phases would distinguish inflation from “something else that moved.” It would not.

Measured lung volume is jointly accompanied by:

- mean parenchymal HU and the entire density histogram;
- diaphragm position, mediastinal geometry, cardiac silhouette, vessel crowding, and dependent opacity;
- tumor and atelectasis position and apparent shape;
- the amount of anatomy admitted to or discarded by CT-CLIP's fixed input preprocessing;
- interpolation, duplication, discontinuity, and phase-sorting artifacts in 4DCT.

Most of those quantities move systematically with respiratory phase and can therefore produce the same monotone score-volume relationship. Tumor position in particular can be monotone with lung volume; the card's statement that it would not be is unsupported and physiologically implausible. A continuous covariate improves precision but does not identify which correlated visual variable the model uses.

The 4DCT series is also not a ten-level controlled-inflation experiment. Respiratory phase is a location in time within a cycle, not a calibrated percentage of vital capacity. Equal phase bins need not have equal amplitude increments, and the same amplitude may occur on inspiratory and expiratory limbs with different anatomy. Conventional respiratory-correlated CT is reconstructed from projections acquired across breathing cycles and is vulnerable to phase-sorting artifacts under irregular breathing. These are established properties of 4DCT, not theoretical edge cases: Yamamoto et al. directly studied spatial 4DCT artifacts (Medical Physics 2010, DOI [10.1118/1.3488984](https://doi.org/10.1118/1.3488984), PMID 20964215), and Abdelnour et al. compared phase and amplitude binning because phase binning produced respiration-related misalignments (Physics in Medicine & Biology 2007, DOI [10.1088/0031-9155/52/12/012](https://doi.org/10.1088/0031-9155/52/12/012)).

Consequently:

- The breath-hold pair identifies sensitivity to **respiratory acquisition state**, conditional on the protocol actually matching in the DICOM headers.
- The 4DCT phases can be an exploratory consistency analysis after image-quality control.
- Neither analysis alone identifies total lung volume rather than attenuation, motion, resampling, or reconstruction artifact as the cue.

The card currently scores identifiability as 5 and rung 3 as reached. Both are overstated. Before repair, identifiability is at most 3 and the result reaches rung 1: the model uses something that changes with respiratory state. A named rung-3 statement could be “the model's emphysema score is sensitive to inspiratory versus expiratory acquisition state,” but not “the model uses total lung volume and mean attenuation” as two independently isolated cues.

## The preprocessing confound is central, not a technical footnote

CT-CLIP consumes a fixed-size preprocessed volume. When the lungs expand and the diaphragm moves, converting both scans to that fixed representation can alter anatomical scale, superior-inferior coverage, padding, and crop boundaries. A score can therefore track measured litres even if the encoder is responding to scale or crop occupancy rather than parenchymal physiology.

This is the nearest-checkable-thing error to avoid here:

> If I have only verified that paired breath-hold scans and a fixed preprocessing pipeline exist, what am I still assuming?

The remaining load-bearing assumption is that the two respiratory states enter the model with comparable coverage and physical scale, such that the score difference reflects the acquired anatomy rather than preprocessing-induced framing. That assumption is not inspected. It must become a Stage 0 gate based on actual preprocessed volumes, not a post hoc caveat.

At minimum, the revision must report, by respiratory state, retained superior/inferior landmarks, crop loss, padding fraction, post-resampling lung-voxel count, physical voxel spacing before preprocessing, and whether either lung touches an input boundary. If these differ systematically, the experiment remains a valuable pipeline robustness test but cannot decode a physiological cue.

## Negative controls do not rescue the mechanism

Calcification findings are useful **process controls**, but they do not exclude general acquisition sensitivity:

- Different heads have different prevalences, calibration, and score variances. A flat calcification head is not evidence that an emphysema-head change arose specifically from inflation rather than head-specific sensitivity to resampling or motion.
- Arterial-wall and coronary calcification are not necessarily geometrically invariant in the fixed tensor: cardiac and mediastinal positions change with respiration, and partial-volume effects can change after resampling.
- Failure of the negative controls would be informative—the pipeline is globally unstable—but success does not identify the positive mechanism.

Better controls include every released output, standardized by each head's test-retest variability, rather than selecting a few “should be flat” heads. The primary contrast should test whether the prespecified parenchymal heads move more than the empirical background distribution across non-parenchymal heads. This is still a specificity analysis, not proof of the cue.

## Endpoint and medical-claim problems

The card mixes three distinct endpoints:

1. paired inhale-exhale score difference;
2. within-patient score-versus-volume slope across 4DCT phases;
3. comparison with a published LAA%-950 change per litre.

Only the first is presently clean enough to be primary. The second is confounded by phase reconstruction and pseudo-replication: ten phases do not create 200 independent patients. The third is dimensionally awkward. A neural-network probability/logit change per litre cannot be called “more or less robust” than a percentage-point change in LAA%-950 per litre without a clinically justified normalization or decision threshold. Those outputs have different units and purposes.

The sentence “a patient who cannot hold a full breath receives a different diagnosis” is not supported by a continuous score shift. It requires a validated clinical threshold, evidence that cases cross it, and evidence that the output is actually used as a diagnosis. CT-CLIP ClassFine is an abnormality classifier trained from report-derived labels, not a deployed diagnostic decision rule. The defensible consequence is narrower: breath-hold quality may alter model finding scores and therefore threatens score comparability.

There is no concept-label circularity in the primary analysis because it uses no reference labels. There is, however, **output-semantic dependence**: ClassFine heads inherit report-derived categories. A movement in an “emphysema” head does not prove the visual feature used is emphysema. That is exactly why the physical cue claim needs stronger identification.

## Statistical weakness and the null

The anticipated null is correctly classified as sensitivity-limited. The proposed comparison to 1.44 LAA percentage points per litre does not supply an equivalence margin for a model logit or probability. A revision needs a model-scale margin tied to a consequence, for example:

- a prespecified fraction of the score separation between positive and negative CT-RATE validation cases; or
- a prespecified probability/logit change based on ClassFine calibration and threshold-crossing behavior; or
- a standardized paired change relative to same-state repeatability on RIDER, treated cautiously because RIDER respiratory state is uncontrolled.

With 20 patients, confidence intervals and patient-level bootstrap or randomization inference matter more than nominal phase-level sample size. Phase volumes must remain clustered within patient. Multiplicity across 18 heads must be handled with a small confirmatory set and all others explicitly exploratory.

A null without a justified equivalence margin remains type 2. It cannot establish inflation invariance. A large paired effect, by contrast, would be a clear and useful robustness failure even before cue identification.

## Prior-work overlap

The closest verified overlap does not kill the project:

- Eslick et al. validate CT-derived ventilation against Galligas PET; they do not evaluate diagnostic-model scores.
- The RIDER foundation-model study tests embedding repeatability in 26 scan-rescan patients but does not control or measure respiratory state and does not report ClassFine head changes. The manuscript is “Foundation model embeddings for quantitative tumor imaging biomarkers,” Research Square rs-6630446; its methods state two scans within 15 minutes and embedding cosine similarity. This is meaningful overlap in **robustness framing**, not the same experiment.
- Quantitative emphysema studies already establish that inspiration changes density-based emphysema measures. This supports the medical premise but also means the biological direction is not novel. The novel delta, if retained cautiously, is the magnitude and head specificity of a released model's response.

The project should not claim discovery of the inflation-density relationship. It can claim a previously unreported model audit only after a final, documented search and direct inspection of the closest papers.

## Feasibility and compute

Compute is not a serious objection. The official repository reports sub-second ClassFine inference per volume under its setup and permits smaller-GPU inference. Even 20 pairs plus 200 phase volumes are modest. The real feasibility risks are:

- gated access to the 1.77 GB checkpoint;
- compatibility of radiotherapy CT coverage with CT-CLIP preprocessing;
- direct DICOM confirmation of slice thickness, reconstruction kernel, contrast status, pixel spacing, dose fields, series completeness, and breath-hold pair matching;
- lung segmentation reliability on expiratory and artifact-affected 4DCT volumes.

These are Stage 0 checks. No score should be interpreted before they pass.

## Easier version with existing assets

The low-hanging-fruit formulation is a paired **respiratory-state repeatability audit** using only the 40 breath-hold volumes. It uses the already released TCIA images, CT-CLIP code and ClassFine checkpoint, and a standard automatic lung mask. It needs no labels, no 4D registration, no 4DCT artifact adjudication, and no bespoke training.

Freeze emphysema as the sole confirmatory head because it has the clearest quantitative link to inflation. Treat atelectasis, lung opacity, and consolidation as ordered secondary hypotheses; remove mosaic attenuation because the head does not exist. Report the paired change from expiration to inspiration, its confidence interval, the fraction of cases crossing any **pre-existing author-defined** classification threshold if one exists, and descriptive associations with measured volume and mean HU. Call those associations explanatory evidence, not mechanism identification. Report all 18 heads as an exploratory specificity panel.

This preserves the clinically important question—whether breath-hold quality changes a model's output—while avoiding the false promise that ten correlated phase reconstructions reveal which pixels or physical quantity the model uses. If the paired effect is large, a later, separate mechanism study can use registered, tissue-mass-preserving transformations or a controlled-inflation acquisition with independently set volumes. Such interventions require their own in-distribution validation and should not be smuggled into this first audit.

## Required revision before a probe contract

1. Change the primary question to respiratory-state sensitivity of the emphysema score on the matched BHCT pair.
2. Downgrade the 4DCT analysis to exploratory and remove the claim that it identifies inflation or supplies ten calibrated dose levels.
3. Remove mosaic attenuation and verify the complete output vocabulary and score semantics directly from the pinned code revision.
4. Make preprocessing comparability an explicit Stage 0 go/no-go gate.
5. Separate score shift, measured-volume association, and diagnostic threshold crossing; do not translate the first into “different diagnosis.”
6. Define a model-scale equivalence margin before inference; otherwise preserve the null as sensitivity-limited.
7. Freeze one confirmatory head, a small ordered secondary set, and multiplicity handling. Keep all-head analysis exploratory.
8. Correct “no distribution shift” to the narrower fact that both images are real acquisitions. Relative to CT-RATE training, radiotherapy-planning patients, respiratory phase, coverage, and preprocessing may still be out of distribution.

## Decision rationale

Advance to revision because the data contrast is rare, real, and clinically interpretable, and the smallest experiment is cheap. Do not advance the present rung-3 mechanism claim. The study earns a strong robustness statement first; decoding total lung volume or mean attenuation requires a second design that breaks their collinearity with motion and preprocessing.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: In the same patient and session, how much does CT-CLIP's emphysema score change between real inspiratory and expiratory breath-hold CT after verifying matched acquisition and preprocessing coverage?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes—the paired public acquisition can reveal a clinically meaningful breath-hold robustness failure with almost no annotation or compute burden, even though it cannot by itself identify the exact visual cue.


===== ideas/007/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed repair fails the identity check: a paired respiratory-state robustness audit is worthwhile, but it no longer tests the original claim that CT-CLIP uses total lung volume and mean parenchymal attenuation as its cue.

**Argument:** The original deliverable is mechanistic and rung 3—“the model is using” measured inflation and the attenuation it sets—whereas the repaired primary estimand is only the change in the emphysema score between inspiratory and expiratory BHCT. In this TCIA acquisition, lung volume is inseparable from density-histogram shifts, diaphragm and mediastinal motion, vessel crowding, dependent opacity, lesion displacement, and fixed-tensor crop/scale changes. The ten 4DCT phases do not break those correlations and introduce phase-sorting and reconstruction artifacts documented by Yamamoto et al. (DOI 10.1118/1.3488984). All-head or calcification controls can show head specificity or global instability, but cannot identify which correlated respiratory feature drove an emphysema-head change. Therefore the repaired audit supports only “the model’s emphysema score is sensitive to respiratory acquisition state,” not the original named-cue sentence. That is a different scientific question and should be spawned as a separate candidate rather than treated as a revision that advances Idea 007.

**What would change my mind:** Show an in-distribution intervention or acquisition in which lung volume or mean parenchymal attenuation varies while the competing respiratory changes—anatomical motion, tissue configuration, reconstruction, and preprocessing framing—are held fixed or independently varied, and demonstrate that CT-CLIP’s score follows the targeted quantity under that factorial contrast.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The repaired design measures only that the model reacts to *something* about respiratory state. Because inflation, density, anatomical motion, tissue configuration, reconstruction and preprocessing framing all move together in this acquisition, and because the ten phases do not decouple them, the design cannot name lung inflation as the cue. It therefore answers a different question than the card's rung-3 sentence and should be spawned as a separate candidate.

**Response:** AMEND

**Argument:**

I concede three of the critic's premises outright and dispute the conclusion, on the strength of a contrast that exists in this data and that neither the card nor the critique used.

**Conceded.** (i) The ten phases are not a dose-response and I withdraw that claim; phase index is a position in time, not a calibrated inflation level. (ii) Total lung volume and mean parenchymal attenuation cannot be separated from each other by *any* breathing contrast, here or anywhere. Between two breath holds of one patient the parenchymal tissue mass is essentially conserved, so mean HU is a near-deterministic function of volume: they are one physical quantity — parenchymal air fraction — expressed in two units. The card's "co-primary" framing was wrong, and the deliverable must name one quantity, not two cues. (iii) Fixed-tensor crop and scale differences are a real differential between the two acquisitions and were not addressed.

**The new argument.** The critic asks for a contrast in which the target quantity is held fixed or varied independently of the nuisances. One direction of that factorial is physically unobtainable: you cannot change a patient's lung volume while holding tissue configuration fixed, and manufacturing it by warping images is exactly the off-manifold move that killed idea 006. But the *other* cell is obtainable, and it is the one that does the falsifying work: **hold lung volume fixed and let the nuisances vary.**

Respiratory motion is hysteretic. At the same total lung air volume, tissue position and regional volume differ between the inspiratory and expiratory limbs of the cycle. That is the operational definition used by Miyawaki, Choi, Hoffman & Lin, *J Comput Phys* 2016;326:76-90 (PMID 28260811, DOI 10.1016/j.jcp.2016.08.039), who measured relative hysteresis in human 4DCT as the difference in tissue position and regional volume at matched total lung volume between the two limbs — verified at abstract level, not yet full text. Tumour trajectories are hysteretic on the same principle: Seppenwoolde et al., *Int J Radiat Oncol Biol Phys* 2002;53:822-834, report 3D hysteresis in 10 of 21 lung tumours, 1-5 mm (search-summary level; full text not yet read).

In a 10-phase binned 4DCT, 0% is near maximum inhale and 50% near maximum exhale, so phases 10-40% descend the volume curve and 60-90% ascend it. Opposite-limb phases can therefore be matched on *measured* lung volume — the same machine-computable exposure the card already uses — giving within-patient, within-session pairs in which ΔV ≈ 0 and Δmean-HU ≈ 0 while tissue configuration, diaphragm and mediastinal position, vessel arrangement, tumour position, dependent opacity, phase-sorting artifact and noise realization all differ. That is the critic's requested cell, acquired rather than synthesized.

The identification then reads: score movement in the large-ΔV breath-hold pair, referenced against the score movement observed in the ΔV ≈ 0 matched-volume pairs. If the model is responding to co-moving anatomy, configuration or reconstruction, that response appears in the ΔV ≈ 0 arm. If it is responding to the air-fraction axis, that arm is flat and the breath-hold arm is not. The surviving alternative after such a result is a variable that is a deterministic function of lung volume with no configuration dependence — and hysteresis is precisely the evidence that motion, vessel crowding, and lesion position are *not* such functions.

Two properties of this arm are worth stating because they cut against me. The 4DCT reconstruction artifacts the critic cites (Yamamoto, DOI 10.1118/1.3488984) load onto the ΔV ≈ 0 arm and inflate its variance, which makes the reference band conservative — artifact makes it harder, not easier, to attribute movement to inflation. Conversely the configuration difference across the hysteresis gap is small, of order millimetres, whereas the breath-hold contrast spans a full excursion. So the arm bounds nuisance-driven score movement only over the hysteresis range, and the bound must be reported with the fraction of the nuisance range it actually spans, measured by machine-computable surrogates (diaphragm dome z-position, lung-mask Jaccard between pair members, tumour centroid shift) in the ΔV ≈ 0 pairs versus the breath-hold pair. If those surrogates show the matched-volume pairs are near-identical images, the arm is a null contrast and proves nothing; that must be checked before it is interpreted, not after.

**Also amended, addressing the framing confound directly.** Both breath holds are acquired in one session with no repositioning, so DICOM patient coordinates are comparable. Both volumes will be cropped to an *identical physical box in scanner coordinates* before CT-CLIP preprocessing, rather than to an anatomy-adaptive extent. Framing is then identical by construction for the primary pair, and the reported Stage 0 quantities (retained landmarks, padding fraction, boundary contact) become verification rather than caveat. This does not extend to any cross-session arm.

**What is lost.** The rung-3 sentence narrows to one quantity: *the model is using the degree of lung inflation — the parenchymal air fraction, measurable equivalently as total lung volume in litres or as mean parenchymal attenuation — as a component of its emphysema, atelectasis and lung opacity scores.* Mosaic attenuation goes, the head does not exist. The "different diagnosis" clause goes. The ten-point per-patient slope goes, so the comparison against LAA-950's 1.44%/L rests on a two-point contrast with phase points used descriptively, and is correspondingly less precise. Identifiability drops from 5 to 4: the design partially bounds rather than eliminates configuration effects, over the hysteresis range only. Rung 3 becomes conditional on the ΔV ≈ 0 arm being both non-degenerate and flat.

**New keystone, and I state it as the thing the inference needs.** Opposite-limb phase pairs matched on measured lung volume within a prespecified tolerance exist, in enough of the 20 patients, with reconstruction quality adequate to interpret, *and* with residual configuration difference large enough to constitute a real nuisance probe. Status: NOT_INSPECTED — hysteresis is established in the literature in other subjects under a different protocol, which is the nearest checkable thing. If I have only verified that, what am I still assuming? That it survives phase binning in *this* corpus at usable amplitude. That assumption is load-bearing and becomes a Stage 0 go/no-go with a prespecified demotion rule: if it fails, the mechanism arm is dead and the study is reported as the rung-1 respiratory-state robustness audit the critic describes — not quietly reinterpreted as one.

**Identity check.** The primary question is unchanged: how much do the finding scores move between the paired breath holds, and do they move as a function of measured lung volume. The amendment adds a control arm and removes a claim I could not support; it does not substitute a different estimand. Accordingly I do not spawn a separate candidate — the critic's audit is the prespecified fallback of this one, not a sibling of it. No spin-off is proposed.

**Status:** OPEN

## Round 3 — CRITIC

**Position:** The matched-volume 4DCT arm is not an exchangeable nuisance control for the breath-hold contrast, so a flat result in that arm still cannot identify parenchymal air fraction as the cue.

**Argument:** The amendment passes the identity check—it still asks whether scores follow measured inflation—but its new control does not supply the missing factorial contrast. Opposite-limb phases at equal total lung volume vary nuisances only over the small hysteresis gap, while the inhale-versus-exhale BHCT pair changes anatomy over the full respiratory excursion. The proposer explicitly acknowledges this scale mismatch. Measuring diaphragm displacement, mask Jaccard, and tumour-centroid shift does not repair it: these are incomplete surrogates, and there is no justified model that extrapolates a near-zero score response to millimetric hysteresis into a bound on the response to much larger diaphragm motion, vessel crowding, dependent opacity, lesion deformation, or partial-volume change. Those effects may be nonlinear or emerge only at expiration. Worse, the nuisance reference comes from phase-binned 4DCT whereas the target contrast comes from two BHCT acquisitions; Yamamoto et al. (DOI 10.1118/1.3488984) establishes that 4DCT has phase-sorting artifacts, but added artifact variance is not merely conservative: it changes the intervention and can widen a reference band until it is uninformative, while a flat mean can result from heterogeneous artifact directions. Thus “large BHCT score change plus flat matched-volume 4DCT change” remains compatible with the model using excursion-dependent anatomical configuration rather than air fraction. The design can establish respiratory-state sensitivity and provide suggestive explanatory evidence, but it still cannot support the proposed rung-3 sentence.

**What would change my mind:** Show, in the actual corpus, an acquired set of contrasts in which matched-volume configuration changes span the same range as the BHCT configuration changes (on prespecified, sufficiently comprehensive nuisance measurements), or provide a validated in-distribution intervention that varies parenchymal air fraction while holding those configuration changes fixed; then demonstrate that score change tracks air fraction after the nuisance contrasts are independently varied.

**Status:** OPEN

## Round 4 — PROPOSER

**Responding to:** The hysteresis arm varies the nuisances only across a millimetric gap while the breath-hold contrast varies them across a full excursion, and it does so in phase-binned 4DCT rather than in breath-hold acquisitions. Nothing licenses extrapolating a flat response over the small range into a bound on the large one, and artifact can flatten the arm's mean while widening its band. So "large BHCT change, flat matched-volume change" is still compatible with the model using excursion-dependent anatomical configuration rather than parenchymal air fraction, and the rung-3 sentence is not earned.

**Response:** AMEND

**Argument:**

**Conceded without reservation.** The hysteresis arm does not identify anything. The extrapolation from a millimetric configuration gap to a full-excursion one is unlicensed, I have no model that would license it, and the 4DCT-versus-BHCT mismatch means the arm is not even the same intervention as the target contrast. I withdraw it as an identification device. It survives in one much weaker role, stated below, and if the critic rejects that role too it can be deleted without touching the primary analysis.

**Where I now think the disagreement actually is.** The critic and I are not disagreeing about the data any more. We are disagreeing about what X is allowed to be. Round 3's alternative explanation — "excursion-dependent anatomical configuration" — is not a rival to inflation. It is inflation, described in constituent parts.

Within one patient in one session, diaphragm dome position, mediastinal shift, vessel crowding, dependent density gradient, lobar shape and parenchymal attenuation are not free variables. They are deterministic consequences of a single scalar: how much air is in the lungs. You cannot set any one of them independently in a breathing human. That is the operative test I propose for whether a co-moving quantity is a confound or part of the state: **a confound is something that can differ while the state is held fixed** — scanner, kernel, dose, table position, patient. Something that cannot be varied at fixed state in the target population is not a competing explanation; it is the state's own anatomy.

This matters because the charter's rung 3 asks for a named, human-legible thing a radiologist could agree or disagree with, and *degree of inspiration* is exactly that word. When a radiologist writes "suboptimal inspiration, apparent ground-glass is expiratory," they are not naming a density channel. They are naming the whole syndrome — high diaphragm, crowded vessels, dependent opacity, denser parenchyma — with one term, and they are asserting a causal story about all of it at once. The charter's artifact list for rung 2 is scanner, site, protocol, reconstruction, position, dose, habitus, referral pattern, label leakage. Every one of those is eliminated by construction for the breath-hold pair. Other physiological correlates of the same state are not on that list, and I do not think they should be, because a rung-3 sentence in physician words is necessarily a sentence about a state, not about a voxel-level channel.

**So the amendment is to X, not to the design.** X is the inflation state of the lung, a single physiological state variable, calibrated by total lung volume in litres. Deliverable sentence:

> *The model is using degree of inspiration — the lung's inflation state, measured as total lung volume in litres — as a component of its emphysema, atelectasis and lung opacity scores.*

What is explicitly **not** claimed, and this is the concession the critic has extracted over two rounds: the study cannot say which channel within that state carries the signal. It cannot distinguish "the parenchyma reads denser" from "the vessels are crowded" from "the diaphragm is high." Round 2's sentence named parenchymal air fraction as the operative quantity. That is withdrawn. Air fraction remains the *most plausible* channel, supported by the density literature (Eur Radiol 2002, PMID 12386770; Madani, Radiology 2010, PMID 20663967 — conclusion sentence inspected, per-step figures paywalled), but it is offered as interpretation, not as an identified mechanism, and the card must label it that way.

**Is the bundled X unfalsifiable?** No, and this is where the design still does work. The exposure is a measured scalar, not a categorical "respiratory state," so the claim predicts a graded relationship with litres and can be compared in magnitude against LAA-950's published 1.44 percentage points per litre (Kavuri, Acad Radiol 2025, PMID 40348708, inspected — a virtual imaging trial, so a magnitude anchor, not an empirical patient result). Three results would refute it: scores that move as much between two acquisitions at the *same* inflation state as between the two breath holds; scores whose movement does not order with the measured volume difference across patients; or movement concentrated in heads with no parenchymal referent while the parenchymal heads are flat. The first of those is what the matched-volume 4DCT pairs are now for — **a score-jitter floor at ΔV ≈ 0, not a nuisance bound.** Phase-sorting artifact inflates that floor, which is conservative for the only test it now serves: does the breath-hold movement exceed the movement seen when inflation barely changes. If the floor is as large as the breath-hold effect, the finding is jitter and the study says so.

**The critic's requested contrast does not exist, and I want to be precise about why rather than plead hardship.** Varying air fraction while holding tissue configuration fixed is not merely absent from public data; it is not a state a breathing thorax can occupy. Even a spirometrically gated ladder at set percentages of vital capacity — the Madani 2010 design, whose images were never released — changes configuration along with volume. The only route to channel-level decomposition is a simulation study in which attenuation is altered at fixed geometry and reprojected, which is the DukeSim class of design, and that is a different study on synthetic anatomy, not a repair to this one. I note it as the follow-up rather than as a spin-off candidate, because it is not something this program can execute on public data today.

**Keystone, restated and improved.** Round 2's keystone was the existence of usable opposite-limb matched-volume pairs, status NOT_INSPECTED. It is no longer load-bearing: with the arm demoted to a jitter floor, its failure degrades precision rather than killing the claim. The keystone reverts to the inspected one — two matched-exposure breath-hold acquisitions per patient in one session, INSPECTED_TRUE at the collection level — plus the framing gate carried forward from round 2: both volumes cropped to an identical physical box in scanner coordinates, with retained landmarks, padding fraction and boundary contact reported as Stage 0 verification. If I have only verified that the pair exists and the box is identical, what am I still assuming? That the identical box, sized to contain the *inspiratory* lung, does not itself introduce an asymmetry — the expiratory volume will have more non-lung tissue inside the same box. That is checkable in Stage 0 as lung-voxel fraction within the box by state, and it must be reported, not assumed away.

**What is lost, cumulatively across both amendments.** The channel-level mechanism claim, entirely. The ten-point dose-response. Mosaic attenuation. The "different diagnosis" clause. The claim that the model is or is not more inflation-robust than LAA-950 in any shared-mechanism sense — that comparison is now a magnitude analogy between two sensitivities, not a statement about the same quantity. Identifiability for the bundled X I would put at 4: acquisition confounds eliminated by construction, framing eliminated by the identical box, exposure measured and continuous, jitter floor available. Identifiability for the channel-level claim is 2, which is why that claim is gone.

**Identity check.** The card's question is "how much do the finding scores move between the paired breath holds, and do they move as a function of total lung volume in litres." Unchanged. The card's own X was already "the degree of lung inflation," with volume and HU given as its measures; this amendment drops the second measure's promotion to an independent cue and returns X to the card's original wording. No estimand substitution, no spin-off.

**Stated plainly: this is my last amendment.** Two amendments have each removed a claim. If the critic holds that a state-level X is not a legitimate rung-3 X — that the charter requires decomposition to the physical channel — then that is a standard this corpus cannot meet and no third amendment will change it, and I will concede to the rung-1/rung-2 respiratory-state audit the critique named, on the record, rather than defend further.

**Status:** OPEN


===== ideas/007/idea_card.json =====
{
  "id": "C3",
  "search_mode": "B",
  "entry_point": 2,
  "title": "The same patient, twice, ten minutes apart, differing only in how much air is in the lungs",
  "question": "When one patient receives an inhale and an exhale breath-hold CT in a single session on one scanner at matched exposure, how much do a chest-CT foundation model's finding scores move, and do they move as a function of total lung volume in litres?",
  "deliverable_sentence": "The model is using the degree of lung inflation - total lung volume and the mean parenchymal attenuation it sets - as a component of its emphysema, mosaic attenuation, atelectasis and lung opacity scores, so a patient who cannot hold a full breath receives a different diagnosis.",
  "why_unasked": "Radiologists correct for inspiratory effort constantly and without comment; it is one of the first things taught about reading a chest study, and an expiratory scan that looks like ground glass is a standing joke rather than a research question. Because the correction is so automatic in humans, nobody has asked whether the model does it. The benchmark cannot reveal it either: every corpus used to evaluate these models has ONE scan per patient, so inflation state is a fixed property of each case and is silently absorbed into the label. The confound is invisible by construction, and it becomes visible only when you have the same patient twice.",
  "rung": {
    "current": 3,
    "why": "Degree of inspiration is a named physiological state that every chest radiologist assesses on every study, and total lung volume is its calibrated measure in litres.",
    "what_would_move_it_up": "Nothing above rung 3. What would strengthen it: replication in a non-oncological population, since the available corpora are lung cancer and radiotherapy patients, and extension to a second foundation model to show the behaviour is not one checkpoint's quirk."
  },
  "X_measurement": {
    "X": "Total lung volume in litres, with mean lung attenuation in Hounsfield units as the co-primary because it is the channel through which inflation most plausibly acts.",
    "how": "lungmask (Apache-2.0, pip-installable) or TotalSegmentator's free lung lobe classes give the mask; volume is a voxel count times voxel volume and mean attenuation is an average inside it. LAA%-950 is reported alongside as the clinically named quantity that inflation is known to corrupt.",
    "citations": "Effect size anchored in real paired patients: Eur Radiol 2002, PMID 12386770, DOI 10.1007/s00330-002-1514-z, n=155 paired full-inspiration and full-expiration HRCT, reporting mean lung density of minus 813 HU at full inspiration and minus 736 HU at full expiration - a 77 HU shift. Controlled-inflation within-subject support: Madani, Van Muylem, Gevenois, Radiology 2010;257(1):260-268, PMID 20663967, imaging the same subjects at 100, 90, 80, 70 and 50 percent of vital capacity and concluding that 'submaximal inspiration induces underestimation of pulmonary emphysema'.",
    "could_I_compute_it_today_without_asking_anyone": "Yes. Lung segmentation and a voxel count, on a corpus that downloads without any agreement."
  },
  "suspected_signal": "Inflation is a physical dilution. At full inspiration the same tissue mass occupies more volume, so every parenchymal voxel contains proportionally more air and reads lower in Hounsfield units; at expiration the parenchyma is denser, vessels crowd together, dependent regions collapse, and the appearance converges on what ground glass, mosaic attenuation and atelectasis look like. A model trained on single-phase scans has no way to distinguish a patient with genuinely dense lung from a patient who exhaled, unless it has learned an inflation-invariant representation - and nothing in its training objective asked it to.",
  "keystone_prerequisite": "A public corpus, with no application or data transfer agreement, provides at least two breath-hold chest CT acquisitions of the same patient in one session at different inflation states, with matched acquisition parameters and whole-thorax coverage - so that inflation is the only thing that differs and both images are real full-dose reconstructions rather than phase bins.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "TCIA collection CT-vs-PET-Ventilation-Imaging, DOI 10.7937/3ppx-7s22, collection page inspected and quoted: 'For this study, 20 lung cancer patients underwent exhale/inhale breath hold CT (BHCT), free-breathing four-dimensional CT (4DCT) and Galligas PET ventilation scans in a single session on a combined 4DPET/CT scanner.' Breath holds were at 'approximately 80% of maximum inhalation and exhalation' with audiovisual biofeedback, at 120 kVp, 120 mAs, 0.8 pitch, 10 second breath-hold - so exposure is matched between the two arms. Coverage is 'approximately 50 cm from the pharynx to the stomach', which is whole-thorax rather than a radiotherapy crop. Non-contrast, DICOM, 14.93 GB, CC BY 4.0, fully public with no application. Scanner is a single Siemens Biograph mCT.S/64. The same session additionally provides a 10-phase 4DCT, giving a within-patient dose-response with ten points. Source paper Eslick et al., Radiother Oncol 2018;127:267-273, PMID 29290405. Every alternative was checked and gated: DIR-Lab requires a Qualtrics request form and an emailed Dropbox password; COPDGene requires an ancillary study proposal and a DUA with National Jewish Health; LTRC requires BioLINCC committee approval; EMPIRE10 is effectively defunct. Learn2Reg Task 2 is ungated but preprocessed and resampled with unverified HU retention.",
  "keystone_residual_assumption": "Having verified that two matched-exposure breath-hold acquisitions exist per patient, I am still assuming that the score difference between them is attributable to INFLATION rather than to everything else that moves when a patient breathes. Two things move: the tumour and any adjacent atelectasis change position and can change apparent size, and the diaphragm and mediastinum shift. This is load-bearing for the causal claim, and it is why the design does not rest on the paired difference alone. The mitigation is built in rather than bolted on: total lung volume is used as a CONTINUOUS exposure across the 10-phase 4DCT of the same patient in the same session, so the claim becomes a within-patient dose-response slope rather than a two-point difference, and a tumour-position artifact would not produce a monotone relationship with lung volume across ten phases. Also unverified: slice thickness is not stated on the collection page, and n is 20.",
  "rung_reached": {
    "value": 3,
    "conditional_on": "The dose-response holding across the 4DCT phases and not only between the two breath holds. A two-point difference alone would support rung 1 - the model is sensitive to something that changes with breathing - but not the named claim."
  },
  "dies_like_prior": "No prior failure mode applies. No annotation enters anywhere: the primary readout is the same model's score on the same patient under two acquisitions, compared to itself, which is the exact structural move that let idea 004 survive and it is used here in its purest form - there is no ground truth in this study at all. It does not die like idea 006 either, and the contrast is worth stating precisely, because this candidate is what idea 006 should have been: idea 006 tried to create a counterfactual image by deleting the patient, and died because the deleted image was off-manifold. Here the counterfactual was created by the scanner. Both images are real, both are full-dose, both are diagnostic-quality chest CT, and the intervention was performed by the patient's own diaphragm. There is no distribution-shift defence to make because there is no distribution shift.",
  "closest_prior_work": [
    {
      "citation": "Eslick EM et al. CT ventilation imaging derived from breath hold CT exhibits good regional accuracy with Galligas PET.",
      "identifier": "Radiother Oncol 2018;127:267-273, PMID 29290405; TCIA collection DOI 10.7937/3ppx-7s22",
      "verification": "INSPECTED (collection page; abstract-level for the paper)",
      "what_it_did": "Acquired the paired breath-hold CTs to derive regional ventilation maps and validate them against Galligas PET.",
      "what_it_did_not_do": "Used the inflation contrast as a physiological signal to be measured. It never runs a diagnostic model of any kind across the pair. The dataset was built for ventilation imaging and is being repurposed here as a natural experiment, which is the whole reason it is available and unclaimed."
    },
    {
      "citation": "Foundation model embeddings for quantitative tumor imaging biomarkers (test-retest stability on RIDER).",
      "identifier": "PMID 40502795, Research Square rs-6630446",
      "verification": "SEARCH_SUMMARY_ONLY",
      "what_it_did": "Measured embedding stability across two scans of the same patient 15 minutes apart in 26 patients, reporting cosine similarity of 0.97 to 1.00 for most models, with Merlin at 0.81 and CT-CLIP at 0.93.",
      "what_it_did_not_do": "This is the nearest existing measurement and it is a weak proxy. RIDER's repeat scans are free-breathing, so inflation varies uncontrolled and unmeasured - the variation is noise rather than a designed contrast, and the study reports embedding similarity rather than per-finding scores. It cannot say whether the instability it sees IS inflation. That CT-CLIP sits at 0.93 rather than 1.00 is a reason to expect this candidate to find something."
    },
    {
      "citation": "Kavuri et al. Effect of inspiration level on quantitative emphysema (virtual imaging trial).",
      "identifier": "Acad Radiol 2025;32(8):4913-4921, PMID 40348708, DOI 10.1016/j.acra.2025.04.042",
      "verification": "INSPECTED",
      "what_it_did": "Using DukeSim on 20 emphysema models at 70 to 100 percent of full inspiration: 'LAA-950 underestimat[es] the amount of emphysema by 1.44 +/- 0.32% (mean +/- standard error) for every 1-liter deviation from full inspiration.'",
      "what_it_did_not_do": "Quantifies the effect on the BIOMARKER, not on a model. It is simulation rather than patients, so it is cited as a magnitude expectation with the 2002 and 2010 papers as the empirical anchors. It also supplies the per-litre scaling this candidate's dose-response should be compared against - if the model's score moves less per litre than LAA-950 does, the model is more inflation-robust than the standard index."
    },
    {
      "citation": "Cardiothoracic ratio variation with respiration on CT.",
      "identifier": "PMID 26151361",
      "verification": "INSPECTED",
      "what_it_did": "Reports CT-CTR of 44.3 +/- 5.1 inspiratory versus 48.8 +/- 5.5 expiratory - a 4.5 point swing straddling the conventional 0.5 threshold.",
      "what_it_did_not_do": "Concerns humans and the heart rather than models and lungs, but it is the reason this candidate should also score CT-CLIP's Cardiomegaly output on the same pairs. That makes C3 a partial, free, within-patient probe of C2's question, and the overlap should be exploited rather than hidden."
    }
  ],
  "existing_assets": [
    "TCIA CT-vs-PET-Ventilation-Imaging: 20 patients, paired matched-exposure breath-hold CT plus 10-phase 4DCT in one session, CC BY 4.0, 14.93 GB, no gate whatsoever.",
    "TCIA 4D-Lung, DOI 10.7937/K9/TCIA.2016.ELN8YGLE, CC BY 3.0: 20 more patients, 10 phases, 82 4DCT sessions including weekly repeats in 14 subjects - a second, independent, ungated corpus, with the caveat that its phases share one binned acquisition so noise is not matched and coverage is a radiotherapy extent.",
    "The CT-CLIP ClassFine checkpoint, per C2's keystone.",
    "lungmask for the exposure measurement.",
    "Published per-litre and per-phase effect sizes for the biomarker, so the model's sensitivity has something to be compared against rather than being reported in a vacuum."
  ],
  "smallest_decisive_experiment": "One afternoon of inference on a 15 GB ungated download. For each patient compute total lung volume and mean lung attenuation on the inhale and exhale breath-hold scans, run ClassFine on both, and report the paired per-finding score change with the lung volume change as the exposure. The primary readout is entirely label-free: the within-patient slope of score against lung volume in litres, per finding, with the paired difference as a secondary summary. Then use the 10-phase 4DCT from the same session to convert the two-point contrast into a ten-point dose-response inside each patient, which is what separates 'inflation' from 'something else that moved'. Report the model's per-litre sensitivity next to the published per-litre sensitivity of LAA%-950 (1.44 percent per litre), so the result is expressed as whether the model is more or less inflation-robust than the standard quantitative index rather than as an uncalibrated number. Pre-register which findings are expected to move - emphysema, mosaic attenuation, atelectasis, lung opacity, consolidation - and which are not - medical material, arterial wall calcification, coronary artery wall calcification - because the calcification findings are an internal negative control that should be flat, and if they move too, the model is sensitive to the acquisition rather than to inflation specifically. That control costs nothing and it is what turns a suggestive result into an identified one.",
  "standing_confounds_addressed": {
    "scanner_and_vendor": "ELIMINATED BY CONSTRUCTION. One scanner, one patient, one session.",
    "acquisition_protocol": "ELIMINATED BY CONSTRUCTION for the breath-hold pair - 120 kVp, 120 mAs, 0.8 pitch on both arms.",
    "reconstruction": "ELIMINATED for the breath-hold pair. Not eliminated across the 4DCT phases, where each phase is reconstructed from a different subset of projections and therefore has a different noise realization - which is exactly why the breath-hold pair is primary and the phases are the dose-response.",
    "site": "ELIMINATED BY CONSTRUCTION.",
    "positioning": "ELIMINATED BY CONSTRUCTION - the patient does not move off the table between the two breath holds.",
    "habitus": "ELIMINATED BY CONSTRUCTION - the same body.",
    "prevalence": "ELIMINATED BY CONSTRUCTION - within-patient comparison, so there is no population to differ.",
    "referral_pathway": "ELIMINATED BY CONSTRUCTION.",
    "label_leakage": "NOT APPLICABLE - no labels are used anywhere in this study.",
    "what_is_left": "Exactly two things: tumour and atelectasis motion between the breath holds, handled by the ten-point dose-response and the calcification negative controls; and the generalizability of a 20-patient lung cancer and radiotherapy population. This is the shortest residual-confound list in the portfolio and it is the candidate's main argument."
  },
  "alternative_explanations": [
    "The score change reflects tumour and atelectasis displacement, not inflation. PARTLY EXCLUDED by the monotone dose-response across ten phases and by restricting a sensitivity analysis to the lung contralateral to the tumour.",
    "The score change reflects general acquisition sensitivity rather than inflation specifically - the model is simply jittery. EXCLUDED by the calcification negative controls, which have no physiological reason to move with inflation. If they move as much as the parenchymal findings, the finding is jitter and the candidate has produced a different and less interesting result, which the design will detect rather than hide.",
    "Breath-hold at 80 percent of maximum is a smaller contrast than the full-inspiration-to-full-expiration range that the 77 HU literature figure comes from, so the exposure may be weaker than the anchor implies. NOT EXCLUDED - it is a real reason a null could be underpowered, and it must enter the minimum-detectable-effect calculation rather than being discovered afterwards.",
    "Honest self-assessment. The appeal here is genuinely in the design rather than the sentence, which is unusual for this portfolio and is why identifiability is the highest score I have given. The weakness is not identification but SCALE: 20 patients is a small study, and a null would be argued about. The result that would matter most - a large, monotone, per-finding inflation sensitivity - is also the one this design is best powered to detect, which is a fortunate alignment but should be stated as a limitation of what the study can rule out rather than what it can find."
  ],
  "anticipated_negative": {
    "classification": "sensitivity-limited",
    "reasoning": "With 20 patients the paired design is well powered for large within-subject effects and poorly powered for small ones, and the breath-hold contrast is narrower than the full vital-capacity range. A null therefore needs an explicit equivalence margin expressed in the same units as the comparison - the model's score change per litre against LAA-950's published 1.44 percent per litre - and a minimum-detectable-effect computed before any inference is run. It is honestly type 2, not type 1, and I decline to upgrade it on the strength of the design's cleanliness: clean identification does not create statistical power. The 4D-Lung corpus adds 20 more patients and 82 sessions if more is needed, at the cost of matched noise."
  },
  "cross_domain": {
    "applicable": false,
    "note": "No borrowed construct. The design is native to radiology and the analogy budget is spent in C4 and C5."
  },
  "remaining_legwork": [
    "Download 14.93 GB from TCIA via NBIA Data Retriever. No agreement, no form. Hours.",
    "Confirm slice thickness and that both breath-hold series are present for all 20 patients - the collection page does not state thickness. Half a day.",
    "Accept the CT-RATE gate for the ClassFine checkpoint, shared with C2 and idea 004.",
    "Confirm the breath-hold volumes preprocess sanely through the CT-CLIP pipeline - they are 50 cm coverage against a pipeline that crops to 480x480x240 at 0.75 by 0.75 by 1.5 mm, so more of the abdomen and neck will be in frame than in CT-RATE. This is a real risk of exactly the kind this program keeps hitting, and it should be checked before any scores are interpreted. One day.",
    "Pre-register the expected-to-move and expected-not-to-move finding lists and the equivalence margin.",
    "Time to first decision: three to four days after the checkpoint is available, and the data itself is a same-day download."
  ],
  "scores": {
    "clarity": {
      "value": 5,
      "why": "One patient, two scans, one named exposure measured in litres, one score per finding. The comparison is stated completely in the question."
    },
    "identifiability": {
      "value": 5,
      "why": "Scanner, vendor, protocol, site, positioning, habitus, prevalence, referral pathway and label leakage are all eliminated by the acquisition itself rather than by statistical adjustment, and reconstruction is eliminated for the primary pair. The exposure is continuous and measured, the dose-response has ten points within each patient, and there are pre-registered negative-control findings that should not move. This is what isolating a mechanism looks like and I do not think the portfolio contains a cleaner design."
    },
    "medical_relevance": {
      "value": 5,
      "why": "A model whose finding scores move with breath-hold quality will systematically misread frail patients, the elderly, and anyone in pain - precisely the people most likely to be scanned. Radiologists already discount expiratory scans by hand; if the model does not, the failure is silent and clinically consequential."
    },
    "interest": {
      "value": 4,
      "why": "The design is elegant and the question is one every chest radiologist will immediately understand and have an opinion about. Held below 5 because a positive result confirms rather than overturns what an experienced reader would guess, and the surprise is in the magnitude rather than the direction."
    },
    "prior_legwork": {
      "value": 3,
      "why": "The corpus exists and is ungated, the model is released, and there are published biomarker effect sizes to calibrate against - but nothing has been done on this question, so there is no analysis protocol to inherit and the finding-level expectations must be written from scratch."
    },
    "feasibility": {
      "value": 4,
      "why": "Cap lifted, keystone INSPECTED_TRUE. A 15 GB ungated download and inference-only on a released checkpoint. Held to 4 by dependence on the CT-RATE gate for the weights and by the preprocessing-compatibility risk of a 50 cm field of view."
    },
    "data_readiness": {
      "value": 5,
      "why": "CC BY 4.0, no application, no form, no password, DICOM, 14.93 GB. The only genuinely unrestricted dataset in this portfolio."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "Paired within-subject slopes and dose-response regression are standard, but there is no accepted metric for per-finding inflation sensitivity and the comparison against LAA-950's per-litre figure has to be constructed. Custom metrics needed."
    },
    "negative_result_value": {
      "value": 3,
      "why": "Capped by the sensitivity-limited classification. A tight null would be a genuine and useful robustness result for a model the field is building on, but at n=20 with a sub-maximal breath-hold contrast, tightness is the thing in doubt."
    },
    "novelty_confidence": {
      "value": 4,
      "why": "Cap lifted. NOT_FOUND across seven distinct queries for any work applying a chest-CT foundation model across respiratory phases or measuring finding-sensitivity to inflation, and the nearest proxy does not control inflation at all. Held at 4 rather than 5 because robustness evaluations of foundation models are proliferating quickly and this is a natural thing for a benchmark paper to include as one panel."
    }
  },
  "priority_score": 4.25,
  "priority_arithmetic": "0.20*4 (feas) + 0.15*5 (ident) + 0.15*5 (med) + 0.10*3 (legwork) + 0.10*4 (interest) + 0.10*5 (clarity) + 0.10*3 (neg) + 0.05*5 (data) + 0.05*4 (novelty) = 0.80+0.75+0.75+0.30+0.40+0.50+0.30+0.25+0.20 = 4.25",
  "regret": {
    "value": 5,
    "why": "A free 15 GB download and an afternoon of inference, answering a question that bounds every finding score these models produce, on a dataset that has been sitting on TCIA under CC BY since 2022 for a completely different purpose."
  },
  "recommendation": "SHORTLIST - best identifiability in the portfolio, and the only candidate whose data has no gate at all.",
  "unverified_claims": [
    "Slice thickness of the breath-hold CTs. NOT_FOUND on the collection page.",
    "That both inhale and exhale breath-hold series are present and usable for all 20 patients. The collection describes the protocol; per-patient completeness was not checked.",
    "That 50 cm pharynx-to-stomach coverage passes through CT-CLIP's preprocessing without pathological cropping. This is the candidate's main technical risk and it is unverified.",
    "That the 4D-Lung collection has adequate thoracic coverage for a second cohort. NOT_FOUND on its collection page; radiotherapy planning extent is assumed, not verified.",
    "That the 4D-Lung and CT-vs-PET 4DCT phases are retrospectively binned from a single acquisition. Strongly supported by the collection descriptions quoting phase-based binning, but the source paper's methods section could not be opened.",
    "The RIDER test-retest embedding stability figures, including CT-CLIP at 0.93. SEARCH_SUMMARY_ONLY.",
    "The exact per-step effect sizes in Madani et al. 2010. The conclusion sentence is inspected; the per-vital-capacity-step numbers are paywalled."
  ]
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
- **Run the identity check on every amendment you receive.** Ask whether the
  revised design still answers the original question. If it does not, say so
  and make that your objection — it outranks any remaining technical point.
  A feasible study that no longer tests the original claim should be rejected
  and its replacement spawned as a separate candidate, not approved.

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
This is round 3. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed repair fails the identity check: a paired respiratory-state robustness audit is worthwhile, but it no longer tests the original claim that CT-CLIP uses total lung volume and mean parenchymal attenuation as its cue.

**Argument:** The original deliverable is mechanistic and rung 3—“the model is using” measured inflation and the attenuation it sets—whereas the repaired primary estimand is only the change in the emphysema score between inspiratory and expiratory BHCT. In this TCIA acquisition, lung volume is inseparable from density-histogram shifts, diaphragm and mediastinal motion, vessel crowding, dependent opacity, lesion displacement, and fixed-tensor crop/scale changes. The ten 4DCT phases do not break those correlations and introduce phase-sorting and reconstruction artifacts documented by Yamamoto et al. (DOI 10.1118/1.3488984). All-head or calcification controls can show head specificity or global instability, but cannot identify which correlated respiratory feature drove an emphysema-head change. Therefore the repaired audit supports only “the model’s emphysema score is sensitive to respiratory acquisition state,” not the original named-cue sentence. That is a different scientific question and should be spawned as a separate candidate rather than treated as a revision that advances Idea 007.

**What would change my mind:** Show an in-distribution intervention or acquisition in which lung volume or mean parenchymal attenuation varies while the competing respiratory changes—anatomical motion, tissue configuration, reconstruction, and preprocessing framing—are held fixed or independently varied, and demonstrate that CT-CLIP’s score follows the targeted quantity under that factorial contrast.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The repaired design measures only that the model reacts to *something* about respiratory state. Because inflation, density, anatomical motion, tissue configuration, reconstruction and preprocessing framing all move together in this acquisition, and because the ten phases do not decouple them, the design cannot name lung inflation as the cue. It therefore answers a different question than the card's rung-3 sentence and should be spawned as a separate candidate.

**Response:** AMEND

**Argument:**

I concede three of the critic's premises outright and dispute the conclusion, on the strength of a contrast that exists in this data and that neither the card nor the critique used.

**Conceded.** (i) The ten phases are not a dose-response and I withdraw that claim; phase index is a position in time, not a calibrated inflation level. (ii) Total lung volume and mean parenchymal attenuation cannot be separated from each other by *any* breathing contrast, here or anywhere. Between two breath holds of one patient the parenchymal tissue mass is essentially conserved, so mean HU is a near-deterministic function of volume: they are one physical quantity — parenchymal air fraction — expressed in two units. The card's "co-primary" framing was wrong, and the deliverable must name one quantity, not two cues. (iii) Fixed-tensor crop and scale differences are a real differential between the two acquisitions and were not addressed.

**The new argument.** The critic asks for a contrast in which the target quantity is held fixed or varied independently of the nuisances. One direction of that factorial is physically unobtainable: you cannot change a patient's lung volume while holding tissue configuration fixed, and manufacturing it by warping images is exactly the off-manifold move that killed idea 006. But the *other* cell is obtainable, and it is the one that does the falsifying work: **hold lung volume fixed and let the nuisances vary.**

Respiratory motion is hysteretic. At the same total lung air volume, tissue position and regional volume differ between the inspiratory and expiratory limbs of the cycle. That is the operational definition used by Miyawaki, Choi, Hoffman & Lin, *J Comput Phys* 2016;326:76-90 (PMID 28260811, DOI 10.1016/j.jcp.2016.08.039), who measured relative hysteresis in human 4DCT as the difference in tissue position and regional volume at matched total lung volume between the two limbs — verified at abstract level, not yet full text. Tumour trajectories are hysteretic on the same principle: Seppenwoolde et al., *Int J Radiat Oncol Biol Phys* 2002;53:822-834, report 3D hysteresis in 10 of 21 lung tumours, 1-5 mm (search-summary level; full text not yet read).

In a 10-phase binned 4DCT, 0% is near maximum inhale and 50% near maximum exhale, so phases 10-40% descend the volume curve and 60-90% ascend it. Opposite-limb phases can therefore be matched on *measured* lung volume — the same machine-computable exposure the card already uses — giving within-patient, within-session pairs in which ΔV ≈ 0 and Δmean-HU ≈ 0 while tissue configuration, diaphragm and mediastinal position, vessel arrangement, tumour position, dependent opacity, phase-sorting artifact and noise realization all differ. That is the critic's requested cell, acquired rather than synthesized.

The identification then reads: score movement in the large-ΔV breath-hold pair, referenced against the score movement observed in the ΔV ≈ 0 matched-volume pairs. If the model is responding to co-moving anatomy, configuration or reconstruction, that response appears in the ΔV ≈ 0 arm. If it is responding to the air-fraction axis, that arm is flat and the breath-hold arm is not. The surviving alternative after such a result is a variable that is a deterministic function of lung volume with no configuration dependence — and hysteresis is precisely the evidence that motion, vessel crowding, and lesion position are *not* such functions.

Two properties of this arm are worth stating because they cut against me. The 4DCT reconstruction artifacts the critic cites (Yamamoto, DOI 10.1118/1.3488984) load onto the ΔV ≈ 0 arm and inflate its variance, which makes the reference band conservative — artifact makes it harder, not easier, to attribute movement to inflation. Conversely the configuration difference across the hysteresis gap is small, of order millimetres, whereas the breath-hold contrast spans a full excursion. So the arm bounds nuisance-driven score movement only over the hysteresis range, and the bound must be reported with the fraction of the nuisance range it actually spans, measured by machine-computable surrogates (diaphragm dome z-position, lung-mask Jaccard between pair members, tumour centroid shift) in the ΔV ≈ 0 pairs versus the breath-hold pair. If those surrogates show the matched-volume pairs are near-identical images, the arm is a null contrast and proves nothing; that must be checked before it is interpreted, not after.

**Also amended, addressing the framing confound directly.** Both breath holds are acquired in one session with no repositioning, so DICOM patient coordinates are comparable. Both volumes will be cropped to an *identical physical box in scanner coordinates* before CT-CLIP preprocessing, rather than to an anatomy-adaptive extent. Framing is then identical by construction for the primary pair, and the reported Stage 0 quantities (retained landmarks, padding fraction, boundary contact) become verification rather than caveat. This does not extend to any cross-session arm.

**What is lost.** The rung-3 sentence narrows to one quantity: *the model is using the degree of lung inflation — the parenchymal air fraction, measurable equivalently as total lung volume in litres or as mean parenchymal attenuation — as a component of its emphysema, atelectasis and lung opacity scores.* Mosaic attenuation goes, the head does not exist. The "different diagnosis" clause goes. The ten-point per-patient slope goes, so the comparison against LAA-950's 1.44%/L rests on a two-point contrast with phase points used descriptively, and is correspondingly less precise. Identifiability drops from 5 to 4: the design partially bounds rather than eliminates configuration effects, over the hysteresis range only. Rung 3 becomes conditional on the ΔV ≈ 0 arm being both non-degenerate and flat.

**New keystone, and I state it as the thing the inference needs.** Opposite-limb phase pairs matched on measured lung volume within a prespecified tolerance exist, in enough of the 20 patients, with reconstruction quality adequate to interpret, *and* with residual configuration difference large enough to constitute a real nuisance probe. Status: NOT_INSPECTED — hysteresis is established in the literature in other subjects under a different protocol, which is the nearest checkable thing. If I have only verified that, what am I still assuming? That it survives phase binning in *this* corpus at usable amplitude. That assumption is load-bearing and becomes a Stage 0 go/no-go with a prespecified demotion rule: if it fails, the mechanism arm is dead and the study is reported as the rung-1 respiratory-state robustness audit the critic describes — not quietly reinterpreted as one.

**Identity check.** The primary question is unchanged: how much do the finding scores move between the paired breath holds, and do they move as a function of measured lung volume. The amendment adds a control arm and removes a claim I could not support; it does not substitute a different estimand. Accordingly I do not spawn a separate candidate — the critic's audit is the prespecified fallback of this one, not a sibling of it. No spin-off is proposed.

**Status:** OPEN

## Round 3 — CRITIC

**Position:** The matched-volume 4DCT arm is not an exchangeable nuisance control for the breath-hold contrast, so a flat result in that arm still cannot identify parenchymal air fraction as the cue.

**Argument:** The amendment passes the identity check—it still asks whether scores follow measured inflation—but its new control does not supply the missing factorial contrast. Opposite-limb phases at equal total lung volume vary nuisances only over the small hysteresis gap, while the inhale-versus-exhale BHCT pair changes anatomy over the full respiratory excursion. The proposer explicitly acknowledges this scale mismatch. Measuring diaphragm displacement, mask Jaccard, and tumour-centroid shift does not repair it: these are incomplete surrogates, and there is no justified model that extrapolates a near-zero score response to millimetric hysteresis into a bound on the response to much larger diaphragm motion, vessel crowding, dependent opacity, lesion deformation, or partial-volume change. Those effects may be nonlinear or emerge only at expiration. Worse, the nuisance reference comes from phase-binned 4DCT whereas the target contrast comes from two BHCT acquisitions; Yamamoto et al. (DOI 10.1118/1.3488984) establishes that 4DCT has phase-sorting artifacts, but added artifact variance is not merely conservative: it changes the intervention and can widen a reference band until it is uninformative, while a flat mean can result from heterogeneous artifact directions. Thus “large BHCT score change plus flat matched-volume 4DCT change” remains compatible with the model using excursion-dependent anatomical configuration rather than air fraction. The design can establish respiratory-state sensitivity and provide suggestive explanatory evidence, but it still cannot support the proposed rung-3 sentence.

**What would change my mind:** Show, in the actual corpus, an acquired set of contrasts in which matched-volume configuration changes span the same range as the BHCT configuration changes (on prespecified, sufficiently comprehensive nuisance measurements), or provide a validated in-distribution intervention that varies parenchymal air fraction while holding those configuration changes fixed; then demonstrate that score change tracks air fraction after the nuisance contrasts are independently varied.

**Status:** OPEN

## Round 4 — PROPOSER

**Responding to:** The hysteresis arm varies the nuisances only across a millimetric gap while the breath-hold contrast varies them across a full excursion, and it does so in phase-binned 4DCT rather than in breath-hold acquisitions. Nothing licenses extrapolating a flat response over the small range into a bound on the large one, and artifact can flatten the arm's mean while widening its band. So "large BHCT change, flat matched-volume change" is still compatible with the model using excursion-dependent anatomical configuration rather than parenchymal air fraction, and the rung-3 sentence is not earned.

**Response:** AMEND

**Argument:**

**Conceded without reservation.** The hysteresis arm does not identify anything. The extrapolation from a millimetric configuration gap to a full-excursion one is unlicensed, I have no model that would license it, and the 4DCT-versus-BHCT mismatch means the arm is not even the same intervention as the target contrast. I withdraw it as an identification device. It survives in one much weaker role, stated below, and if the critic rejects that role too it can be deleted without touching the primary analysis.

**Where I now think the disagreement actually is.** The critic and I are not disagreeing about the data any more. We are disagreeing about what X is allowed to be. Round 3's alternative explanation — "excursion-dependent anatomical configuration" — is not a rival to inflation. It is inflation, described in constituent parts.

Within one patient in one session, diaphragm dome position, mediastinal shift, vessel crowding, dependent density gradient, lobar shape and parenchymal attenuation are not free variables. They are deterministic consequences of a single scalar: how much air is in the lungs. You cannot set any one of them independently in a breathing human. That is the operative test I propose for whether a co-moving quantity is a confound or part of the state: **a confound is something that can differ while the state is held fixed** — scanner, kernel, dose, table position, patient. Something that cannot be varied at fixed state in the target population is not a competing explanation; it is the state's own anatomy.

This matters because the charter's rung 3 asks for a named, human-legible thing a radiologist could agree or disagree with, and *degree of inspiration* is exactly that word. When a radiologist writes "suboptimal inspiration, apparent ground-glass is expiratory," they are not naming a density channel. They are naming the whole syndrome — high diaphragm, crowded vessels, dependent opacity, denser parenchyma — with one term, and they are asserting a causal story about all of it at once. The charter's artifact list for rung 2 is scanner, site, protocol, reconstruction, position, dose, habitus, referral pattern, label leakage. Every one of those is eliminated by construction for the breath-hold pair. Other physiological correlates of the same state are not on that list, and I do not think they should be, because a rung-3 sentence in physician words is necessarily a sentence about a state, not about a voxel-level channel.

**So the amendment is to X, not to the design.** X is the inflation state of the lung, a single physiological state variable, calibrated by total lung volume in litres. Deliverable sentence:

> *The model is using degree of inspiration — the lung's inflation state, measured as total lung volume in litres — as a component of its emphysema, atelectasis and lung opacity scores.*

What is explicitly **not** claimed, and this is the concession the critic has extracted over two rounds: the study cannot say which channel within that state carries the signal. It cannot distinguish "the parenchyma reads denser" from "the vessels are crowded" from "the diaphragm is high." Round 2's sentence named parenchymal air fraction as the operative quantity. That is withdrawn. Air fraction remains the *most plausible* channel, supported by the density literature (Eur Radiol 2002, PMID 12386770; Madani, Radiology 2010, PMID 20663967 — conclusion sentence inspected, per-step figures paywalled), but it is offered as interpretation, not as an identified mechanism, and the card must label it that way.

**Is the bundled X unfalsifiable?** No, and this is where the design still does work. The exposure is a measured scalar, not a categorical "respiratory state," so the claim predicts a graded relationship with litres and can be compared in magnitude against LAA-950's published 1.44 percentage points per litre (Kavuri, Acad Radiol 2025, PMID 40348708, inspected — a virtual imaging trial, so a magnitude anchor, not an empirical patient result). Three results would refute it: scores that move as much between two acquisitions at the *same* inflation state as between the two breath holds; scores whose movement does not order with the measured volume difference across patients; or movement concentrated in heads with no parenchymal referent while the parenchymal heads are flat. The first of those is what the matched-volume 4DCT pairs are now for — **a score-jitter floor at ΔV ≈ 0, not a nuisance bound.** Phase-sorting artifact inflates that floor, which is conservative for the only test it now serves: does the breath-hold movement exceed the movement seen when inflation barely changes. If the floor is as large as the breath-hold effect, the finding is jitter and the study says so.

**The critic's requested contrast does not exist, and I want to be precise about why rather than plead hardship.** Varying air fraction while holding tissue configuration fixed is not merely absent from public data; it is not a state a breathing thorax can occupy. Even a spirometrically gated ladder at set percentages of vital capacity — the Madani 2010 design, whose images were never released — changes configuration along with volume. The only route to channel-level decomposition is a simulation study in which attenuation is altered at fixed geometry and reprojected, which is the DukeSim class of design, and that is a different study on synthetic anatomy, not a repair to this one. I note it as the follow-up rather than as a spin-off candidate, because it is not something this program can execute on public data today.

**Keystone, restated and improved.** Round 2's keystone was the existence of usable opposite-limb matched-volume pairs, status NOT_INSPECTED. It is no longer load-bearing: with the arm demoted to a jitter floor, its failure degrades precision rather than killing the claim. The keystone reverts to the inspected one — two matched-exposure breath-hold acquisitions per patient in one session, INSPECTED_TRUE at the collection level — plus the framing gate carried forward from round 2: both volumes cropped to an identical physical box in scanner coordinates, with retained landmarks, padding fraction and boundary contact reported as Stage 0 verification. If I have only verified that the pair exists and the box is identical, what am I still assuming? That the identical box, sized to contain the *inspiratory* lung, does not itself introduce an asymmetry — the expiratory volume will have more non-lung tissue inside the same box. That is checkable in Stage 0 as lung-voxel fraction within the box by state, and it must be reported, not assumed away.

**What is lost, cumulatively across both amendments.** The channel-level mechanism claim, entirely. The ten-point dose-response. Mosaic attenuation. The "different diagnosis" clause. The claim that the model is or is not more inflation-robust than LAA-950 in any shared-mechanism sense — that comparison is now a magnitude analogy between two sensitivities, not a statement about the same quantity. Identifiability for the bundled X I would put at 4: acquisition confounds eliminated by construction, framing eliminated by the identical box, exposure measured and continuous, jitter floor available. Identifiability for the channel-level claim is 2, which is why that claim is gone.

**Identity check.** The card's question is "how much do the finding scores move between the paired breath holds, and do they move as a function of total lung volume in litres." Unchanged. The card's own X was already "the degree of lung inflation," with volume and HU given as its measures; this amendment drops the second measure's promotion to an independent cue and returns X to the card's original wording. No estimand substitution, no spin-off.

**Stated plainly: this is my last amendment.** Two amendments have each removed a claim. If the critic holds that a state-level X is not a legitimate rung-3 X — that the charter requires decomposition to the physical channel — then that is a standard this corpus cannot meet and no third amendment will change it, and I will concede to the rung-1/rung-2 respiratory-state audit the critique named, on the record, rather than defend further.

**Status:** OPEN

