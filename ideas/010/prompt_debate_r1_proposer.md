You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/010
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

## 2026-08-05 - Idea 007 ADVANCE TO REVISION (lung inflation, CT-CLIP)
Paired inhale/exhale BHCT + 4DCT confirmed: 20 patients, one session, one
scanner, TCIA DOI 10.7937/3ppx-7s22, ungated, 14.93 GB.
4DCT phases are NOT calibrated inflation levels - phase is time position, not
fraction of vital capacity; same amplitude occurs on both limbs; phase-sorting
artifacts. Dose-response arm demoted to exploratory.
Preprocessing confound is the live keystone residual: fixed-size crop may admit
different anatomy at different diaphragm positions. Stage 0 gate.
CT-CLIP has no mosaic attenuation head - card claimed a nonexistent output.
Claim demoted rung 3 -> rung 1: sensitivity to respiratory state, not
identification of total lung volume as the cue.


===== ideas/010/README.md =====
# Idea 010: Cardiomegaly on a CT report is admitted gestalt - ask whether the model has quietly turned it into millilitres

Selected from scouting cycle 004, candidate 2.


===== ideas/010/critique.md =====
FATAL OBJECTION: The proposed observational associations cannot distinguish use of heart volume in millilitres from use of correlated silhouette, diameter, shape, effusion, or body-size cues, and therefore cannot support the deliverable sentence or its claimed over/under-calling consequence.
EVIDENCE: CT-CLIP `scripts/data_inference_nii.py` lines 85–149; TotalSegmentator official README class/task tables; `ideas/010/idea_card.json` smallest experiment and keystone residual.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: PAUSE

# Adversarial review

## 1. The endpoint does not identify “uses millilitres”

The proposed primary result is an association between one output score and two image-derived measurements, heart volume (H) and (H/T), where (T) is thoracic volume. Even with abundant independent variation and a stable partial coefficient for (H), that result does not show that CT-CLIP uses volume. A model using maximum transverse heart diameter, cardiac silhouette area, chamber shape, contact with the diaphragm, pulmonary vascular changes, pericardial contour, or another correlate of heart size can produce the same result. Conditioning on (H/T) does not rule these alternatives out.

This is not merely the card's acknowledged collinearity/power problem. It is structural non-identifiability: (H) and (H/T) are deterministic functions of overlapping anatomy, while the alternative visual cues are also consequences of that anatomy. Matching or regression can separate which *measurement predicts the score better* in this cohort; it cannot establish which visual quantity the model uses. The proposed “matched-volume, varying-frame-fraction” comparison is especially weak because frame fraction is not the stated relative-anatomy quantity (H/T), and field of view is an acquisition/preprocessing property rather than patient habitus.

The official inference loader makes the distinction important. It converts metadata spacing to a common 0.75 × 0.75 × 1.5 mm grid and then center-crops or pads to 480 × 480 × 240 voxels. Thus the tensor has a common nominal physical scale, but the model is not passed an explicit millilitre value. A positive association is compatible with the model learning any size-correlated morphology on that normalized grid. Conversely, crop truncation and padding can make “fraction of frame” reflect positioning or coverage rather than thoracic size. These are verified facts from the authors' loader, not speculation ([official CT-CLIP inference loader](https://github.com/ibrahimethemhamamci/CT-CLIP/blob/main/scripts/data_inference_nii.py)).

The rung should therefore be 1 at best after a genuine intervention or mediation test, not rung 3 now. “Heart volume in millilitres” is human-legible, but naming a legible correlate does not establish that it is the used signal.

## 2. The clinical consequence is not measured

The sentence “which means it over-calls cardiomegaly in large patients and under-calls it in small ones” requires all of the following: a prespecified operating threshold, an independent reference standard for an erroneous call, a definition of “large patient,” and demonstrated error-rate differences across body size. None appears in the primary experiment. The primary arm deliberately excludes report labels, and no echocardiographic or chamber-specific reference is available. A continuous score association cannot establish an over-call or under-call.

This is also where concept-label circularity re-enters if the repair simply uses CT-RATE cardiomegaly labels: ClassFine was trained to reproduce report-derived categories, and CT-RATE's evaluation labels are extracted from the same report domain. Agreement with those labels measures reproduction of report semantics, not whether a call is medically wrong. The label can be a secondary descriptive endpoint, but not the reference needed for the claimed failure mode.

The clinical premise is less novel than the card implies. A recent primary study explicitly evaluates AI-derived total cardiac volume on non-gated chest CT for opportunistic cardiomegaly screening against echocardiography (PMID 41890626). That work does not answer what CT-CLIP uses, so it is not fatal prior-work overlap; it does mean that “turning gestalt into millilitres” is already an active clinical program, not the candidate's novelty. The exact delta is interpretation of a released report-trained classifier rather than development/validation of a volumetry system ([PubMed record](https://pubmed.ncbi.nlm.nih.gov/41890626/)).

## 3. The keystone is misclassified

The card assigns `INSPECTED_TRUE` to a compound prerequisite: a runnable checkpoint and a same-volume physical measurement. What was inspected was that files/folders appear in repository trees and that relevant class names exist. The checkpoint has not been fetched or executed, the segmentation files and their coverage have not been opened, and the card itself identifies sufficient independent heart/thorax variation as load-bearing and uninspected. Under the charter's mandatory nearest-checkable-fact test, the real keystone is:

> CT-RATE contains enough valid, same-volume heart and thoracic measurements with sufficient conditional variation—and a runnable score—to distinguish the prespecified absolute and relative models.

That is `NOT_INSPECTED`, not `INSPECTED_TRUE`. Feasibility and novelty confidence are therefore capped at 3 until Stage 0 is complete; feasibility 4 is currently impermissible.

There is a second concrete asset error. In the current official TotalSegmentator class table, `heart` is class 51 of the default `total` task, but `thoracic_cavity` belongs to the separate `trunk_cavities` task. It does not “come from the same run” of `total` ([official TotalSegmentator README](https://github.com/wasserth/TotalSegmentator#class-details)). The official tool can compute volumes with `--statistics`, but directory presence does not establish that CT-RATE shipped that statistics output or the separate cavity mask. This is repairable by inspecting the gated files and, if necessary, running `trunk_cavities`; it removes the claimed zero-cost co-primary comparator. TotalSegmentator's original publication validates broad multi-organ segmentation, not this exact whole-heart/thoracic ratio or exclusion of pericardial fluid (Wasserthal et al., DOI 10.1148/ryai.230024).

## 4. Confounds and alternatives surviving a positive result

The current design does not rule out the main alternatives:

- **Pericardial effusion:** excluding cases using an automatic effusion mask helps, but correlated error between two TotalSegmentator tasks is possible and absence of a released mask has not been inspected. A whole-heart contour may also capture different anatomy than chamber-sum volume.
- **Positioning, coverage, and reconstruction:** the fixed physical crop can exclude anatomy differently with table position, scan length, and reconstruction grid. Natural “frame fraction” variation is therefore not a clean intervention on apparent size.
- **Protocol and contrast:** CT-RATE is described by the authors as non-contrast, so “contrast phase” should not be listed as the central live confound. Slice spacing, kernel, dose, motion, and inspiratory state remain live. The official repository describes CT-RATE as 25,692 non-contrast scans expanded to 50,188 reconstructions ([official CT-CLIP repository](https://github.com/ibrahimethemhamamci/CT-CLIP)).
- **Scanner/vendor and site:** stratification can show heterogeneity but cannot remove vendor-correlated scale, reconstruction, or referral patterns. A single institution reduces site heterogeneity internally while preventing a site-general rung-2 claim.
- **Body habitus and sex:** these are not simply “the hypothesis.” They can create the association between absolute cardiac volume and learned demographic/anatomic cues without the model using cardiac volume. They must be treated as alternative pathways even if the clinical question concerns indexing.
- **Disease and referral pathway:** heart failure, pulmonary edema, vascular congestion, pleural effusion, and cardiomyopathy can jointly affect the score and volume. Conditional correlations do not isolate the geometric cue.

Thus a positive observational result rules out only “the score is unrelated to the chosen measurements.” It does not rule out the most plausible mechanisms named above.

## 5. Leakage, data, compute, and prior overlap

There is no conventional train/test leakage in the label-free score–measurement association if the held-out validation patients are genuinely separate and all analysis choices are frozen before an untouched confirmatory subset. There is, however, **target-semantic dependence**: the ClassFine head was trained on report-derived cardiomegaly labels. Interpreting its score as a detector with a clinical decision boundary imports those report semantics even when labels are omitted from analysis.

Compute is not the objection. The official repository reports approximately 0.5 seconds per ClassFine volume and says inference can run on smaller GPUs, although changing encoder patch size can affect performance. Storage, gated access, checkpoint reproducibility, exact segmentation contents, and crop validity are more credible barriers. No patch-size change should be allowed for a confirmatory run.

The closest verified overlap found is automated CT cardiac volumetry and cardiomegaly validation, plus extensive segmentation-derived cardiothoracic-ratio work in radiography. Those studies establish that absolute and indexed cardiac size are obvious competing measurements; they do not appear to test what a frozen report-trained 3D classifier uses. I did not verify a primary study performing this exact CT-CLIP score audit, but failure to find one is not evidence of novelty. Novelty confidence remains at most 3.

This candidate does **not** die like the prior annotation-provenance failures because the primary measurement can remain automatic. It does repeat the ledger's wrong-keystone pattern: repository adjacency was inspected while same-case usable outputs and the variation needed for the inference were assumed. It also risks an idea-006-style intervention error if an eventual repair changes spacing headers or resizes anatomy so extremely that the input becomes out of distribution.

## 6. Negative-result value and endpoint clarity

The card correctly calls the anticipated null sensitivity-limited, but the claimed value of 3 is optimistic. A null partial association can arise from collinearity, noisy/incorrect heart contours, an invalid cavity denominator, crop truncation, score saturation, inadequate positive-case range, or a model using another legitimate heart-size cue. Unless Stage 0 prespecifies acceptable segmentation quality, conditional spread, score range, and a minimum detectable partial effect, the null is uninterpretable (type 3), forcing `negative_result_value <= 2` under the rubric.

The endpoint also mixes three different questions:

1. Does score monotonically associate with whole-heart volume?
2. Does absolute volume predict score better than an indexed measurement?
3. Does reliance on absolute size cause body-size-dependent diagnostic errors?

Only the first is answered by the proposed cheap analysis. The second needs a defensible thoracic/BSA proxy and a design that compares non-nested but prespecified explanations. The third needs an independent clinical reference and calibration study unavailable in CT-RATE. They must not share one deliverable sentence.

## 7. Repair and low-hanging fruit

The cheapest faithful first step is a **screening audit**, not a rung-3 study:

- Inspect the gated `ts_seg` manifests and the two summary spreadsheets before downloading images. Establish whether same-volume heart masks or volumes exist, which TotalSegmentator version/task produced them, and whether any `trunk_cavities` result exists.
- Obtain or request the authors' validation logits. Released per-volume logits would eliminate image download and GPU inference; no such table has yet been inspected. This is the true low-hanging-fruit asset request.
- On one reconstruction per validation scan, estimate score–heart-volume monotonicity and compare prespecified predictors: heart volume, maximum axial heart width or area, thoracic width/area, and their ratio. Use patient-level splitting and reserve an untouched confirmatory subset. Exclude gross crop truncation and report effusion sensitivity analyses.
- Treat this only as model-selection evidence: “the score is better predicted by X than Y,” not “the model uses X.” Stop if conditional spread, mask validity, or score dynamic range fails prespecified gates.

This screening version is easy and worth doing only as a go/no-go because the shipped checkpoint and potentially shipped masks make it cheap. It is not a standalone high-value paper: a strong heart-size association is expected, and a null is weak.

To preserve the original mechanistic question, a later confirmatory test must vary physical heart scale relative to thorax while holding competing image content as fixed as possible and remain within the model's training distribution. A naive resize or spacing-header edit is not sufficient—it jointly changes interpolation, borders, and anatomy and may be OOD. A credible route would require naturally paired same-patient studies with materially changed cardiac volume but stable thoracic anatomy, or a validated anatomy-aware deformation with negative-control structures and explicit OOD checks. Neither asset is currently identified. Until then, the deliverable must be narrowed to association/encoding, and the deployment-error clause removed.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: On one reconstruction per CT-RATE validation scan, is the frozen ClassFine cardiomegaly score better explained by automatically measured whole-heart volume than by transverse heart size or a thorax-indexed size measure, after excluding crop truncation and pericardial effusion?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes as a cheap, preregistered screening gate that can justify a stronger scale intervention, but not as a standalone rung-3 claim or clinical bias study.


===== ideas/010/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The observational score–measurement analysis cannot identify that CT-CLIP uses absolute heart volume in millilitres, so it cannot support the original rung-3 deliverable or the claimed body-size-dependent over/under-calling.

**Argument:** Heart volume, transverse diameter, axial silhouette area, chamber shape, pericardial contour, diaphragm contact, pulmonary vascular changes, and thorax occupancy are correlated consequences of the same anatomy. A monotone association, partial regression, or matched-volume comparison can show only which automatic measurement predicts the frozen ClassFine cardiomegaly score better in CT-RATE; it cannot distinguish a model that uses volumetric extent from one that uses any correlated two-dimensional or morphological cue. The proposed natural variation in frame fraction is not a clean discriminator: the official CT-CLIP loader resamples to 0.75 x 0.75 x 1.5 mm and then center-crops or pads to 480 x 480 x 240, so frame occupancy also varies with coverage, table position, truncation, and preprocessing. Moreover, the clause that the model therefore over-calls large patients and under-calls small ones requires an independent clinical reference standard and a prespecified decision threshold; neither the label-free association nor CT-RATE's report-derived Cardiomegaly label supplies one. The repair suggested in the critique—asking whether score is better explained by whole-heart volume than by width, area, or an indexed measure—is a useful screening question, but the identity check fails: it replaces causal cue identification with comparative prediction and therefore no longer answers the original question, "is the model using millilitres?" It should remain a gate for a later intervention, not be accepted as the original candidate's result.

**What would change my mind:** Show a preregistered, in-distribution intervention or naturally paired same-patient design that changes physical heart volume relative to a stable thorax while holding the leading correlated cues and preprocessing artifacts fixed or measuring them as negative controls, and demonstrate a corresponding score change; separately, support the over/under-calling clause with an independent clinical reference and frozen operating threshold.

**Status:** OPEN


===== ideas/010/idea_card.json =====
{
  "id": "C2",
  "search_mode": "B",
  "entry_point": 2,
  "title": "Cardiomegaly on a CT report is admitted gestalt - ask whether the model has quietly turned it into millilitres",
  "question": "Is CT-CLIP's cardiomegaly score a monotone function of total heart volume in millilitres measured by TotalSegmentator on the same volume, and does it track absolute volume or volume relative to the thoracic cavity?",
  "deliverable_sentence": "CT-CLIP's cardiomegaly detector is using absolute heart volume in millilitres, not heart size relative to the chest, which means it over-calls cardiomegaly in large patients and under-calls it in small ones.",
  "why_unasked": "Because everyone assumes the answer is trivially yes and nobody has priced what 'yes' would cost. Two habits hide it. First, cardiomegaly is treated as a solved, boring finding - the model gets it right, move on - so no one asks WHICH quantity the model recovered. Second, and more interesting: there is no reference standard to compare against, so the question looks unanswerable. The radiology literature says so explicitly. Hota and Simpson, Radiol Cardiothorac Imaging 2019, PMID 33778499: 'a standardized method for evaluating and reporting cardiac chamber size does not exist. This has led to heterogeneity in the reporting of cardiac enlargement at routine multidetector CT with most readers often using gestalt assessment.' That absence is normally treated as a reason not to ask. It is actually the reason the question is worth asking: if the model's score is a clean function of a physical volume, the model has extracted a reproducible measurement from an unstandardized human impression.",
  "rung": {
    "current": 3,
    "why": "Heart volume in millilitres is as human-legible and as physical as this program gets, and a radiologist can disagree with the sentence immediately.",
    "what_would_move_it_up": "Nothing above rung 3. What would strengthen it: showing the score's implied decision boundary in millilitres is stable across manufacturers, since CT-RATE is 61.5% Philips and 30.1% Siemens, and comparing that boundary against the two incompatible published definitions of heart volume named below."
  },
  "X_measurement": {
    "X": "Total heart volume in millilitres - the voxel count of the TotalSegmentator 'heart' class times voxel volume. Co-primary comparator: the ratio of heart volume to thoracic cavity volume, which is the volumetric analogue of the cardiothoracic ratio.",
    "how": "TotalSegmentator v2 default task 'total' contains class 117 costal_cartilages and a single whole-organ class 'heart'; it is Apache-2.0 and needs no license key. Note that v2 collapsed the four chambers and myocardium of v1 into one 'heart' label, and chamber-level segmentation now sits in heartchambers_highres which DOES require a license key - so this candidate deliberately uses the whole-organ class that is free. Thoracic cavity volume comes from the same run.",
    "citations": "Wasserthal J et al., TotalSegmentator, Radiology: Artificial Intelligence 2023, DOI 10.1148/ryai.230024.",
    "could_I_compute_it_today_without_asking_anyone": "Yes, and possibly without even running it: CT-RATE ships precomputed outputs at dataset/ts_seg/ts_total, alongside ts_lung_nodules and ts_pleural_pericard_effusion, plus train_label_summary.xlsx and valid_label_summary.xlsx which may already contain per-structure volumes.",
    "known_weakness_of_X_stated_up_front": "There is no agreed definition of 'heart volume' on CT and the literature disagrees by a factor of two. A 2026 Radiology Advances study of non-gated non-contrast chest CT reports 'Median TCVAI was higher in patients with cardiomegaly than those without (1061.9 vs 798.4 mL; P < .001)', while a 2025 Diagnostics reference-subgroup study defining total heart volume as the sum of both atria and both ventricles with the septum reports females 405.3 +/- 73.0 mL and males 506.9 +/- 89.5 mL. Those are the same words for different quantities. The design is insulated because it never compares against a normative threshold - it asks whether the model's score is a function of a volume the design itself defines and reports."
  },
  "suspected_signal": "Cardiac enlargement displaces lung, flattens the left hemidiaphragm, alters the cardiac silhouette against adjacent low-attenuation lung, and shifts the position of the interface between blood-attenuation myocardium and air-attenuation parenchyma. All of it is geometry at a high-contrast boundary, which is the easiest kind of signal for a 3D encoder to pick up, and none of it requires the model to have learned anything about the ratio a human would use.",
  "keystone_prerequisite": "The released ClassFine checkpoint can be run to produce a per-volume cardiomegaly score, and a per-volume heart volume in millilitres exists for those same volumes - so that a score and a physical measurement can be paired on the identical image.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "The CT-CLIP GitHub README links ClassFine directly as models/CT-CLIP-Related/CT_LiPro_v2.pt inside the CT-RATE HuggingFace dataset repository, and the file tree confirms it exists at 1.77 GB alongside CT-CLIP_v2.pt and CT_VocabFine_v2.pt. The 18 abnormality labels were read from the authors' own scripts/zero_shot.py and 'Cardiomegaly' is the third entry. dataset/ts_seg/ contains ts_total, and TotalSegmentator's map_to_binary.py confirms 'heart' is in the free default 'total' class map. This overturns the prior ledger entry - see record_corrections.",
  "keystone_residual_assumption": "Having verified the file exists in the tree, I am still assuming it loads and runs, since anonymous fetches return HTTP 401 and nothing was downloaded. Three further assumptions are unverified and one of them is load-bearing for identifiability rather than existence. Not load-bearing: the ts_seg TotalSegmentator version, inferred from folder names matching v2-only subtasks rather than read from the gated ts_seg/README.md and requirements.txt. Not load-bearing: whether the metadata CSV carries Manufacturer and reconstruction fields - the paper reports per-scan manufacturer distributions so they were captured, but the column headers are gated and unread. LOAD-BEARING: that CT-RATE contains enough joint variation in heart volume and thoracic cavity volume to separate absolute size from relative size. If large hearts occur almost exclusively in large chests in this corpus, the two hypotheses are collinear and the headline question is unanswerable however good the segmentation is. That is the real keystone for the INTERESTING half of the candidate, it is not inspected, and it is the first thing to check after the gate.",
  "rung_reached": {
    "value": 3,
    "conditional_on": "Reaching the absolute-versus-relative distinction. If the joint variation is insufficient, the candidate degrades to 'the model is using heart size', which is true, uninteresting, and would not have been worth the download."
  },
  "dies_like_prior": "It does not die like ideas 001, 002, 003 or 005, because no human-assigned label enters the primary readout at all. This matters more here than elsewhere: CT-RATE's Cardiomegaly label is RadBERT-extracted from a free-text report whose author was, by the radiology literature's own admission, using gestalt. That label is exactly the kind of contaminated annotation that killed the earlier candidates - so the design keeps it out of the primary comparison entirely and uses it only in a clearly-labelled secondary arm asking a different question (does the model agree with the reporting radiologist more or less than volume does). It does not die like idea 006 either, because there is no intervention: every image is unmodified. The honest resemblance is to no prior candidate; the honest risk is collinearity, which is a power problem rather than a validity problem.",
  "closest_prior_work": [
    {
      "citation": "Hamamci IE et al. Developing Generalist Foundation Models from a Multimodal Dataset for 3D Computed Tomography.",
      "identifier": "arXiv:2403.17834; Nature Biomedical Engineering, DOI 10.1038/s41551-025-01599-y; PubMed 41680439",
      "verification": "INSPECTED (arXiv HTML v1 and v3; authors' zero_shot.py; HuggingFace file tree)",
      "what_it_did": "Released CT-RATE, the 18-label benchmark and the CT-CLIP, VocabFine and ClassFine checkpoints, plus precomputed TotalSegmentator outputs.",
      "what_it_did_not_do": "Reported performance per abnormality without asking what quantity any score corresponds to. Important reporting caveat found during verification: the published text gives only AUROC DELTAS against a CT-Net baseline - 'the zero-shot CT-CLIP model achieves a mean AUROC that is 0.102 higher and a mean F1 score that is 0.050 higher than the supervised baseline' - and the absolute per-abnormality numbers appear only in figures. Secondary sources quoting absolutes disagree with each other (0.704, 0.734, 0.900 all seen) and none is citable. Any baseline number for this candidate must come from the Nature source data or be re-measured."
    },
    {
      "citation": "Hota P, Simpson S. Going Beyond Cardiomegaly: Evaluation of Cardiac Chamber Enlargement at Non-Electrocardiographically Gated Multidetector CT.",
      "identifier": "Radiol Cardiothorac Imaging 2019, PMID 33778499, DOI 10.1148/ryct.2019180024",
      "verification": "INSPECTED",
      "what_it_did": "Documented that no standardized method exists and that most readers use gestalt.",
      "what_it_did_not_do": "Diagnosed the problem for humans and proposed human remedies. It never asks whether a model trained on those gestalt reports has converged on a physical quantity - which is the only reason this candidate is interesting rather than routine."
    },
    {
      "citation": "Kim et al. Cardiothoracic ratio measured on CT as a predictor of left ventricular systolic dysfunction.",
      "identifier": "Clin Exp Emerg Med 2023, PMID 36787898, DOI 10.15441/ceem.22.382",
      "verification": "INSPECTED",
      "what_it_did": "In 444 patients: 'The best cutoff value for a CT-measured cardiothoracic ratio suggestive of LVSD was 0.56, which is very different from the 0.50 value typically considered an abnormal cardiothoracic ratio', with AUCs of only 0.653 to 0.690 and a median CT-CTR of 0.54 in patients with normal ejection fraction.",
      "what_it_did_not_do": "Establishes that the ratio a radiologist would nominally use is itself poorly calibrated on CT, which is what makes the absolute-versus-relative question substantive rather than pedantic. Says nothing about models."
    },
    {
      "citation": "Whole heart volume and major adverse cardiac events.",
      "identifier": "Eur Radiol 2021, PMID 33501599, DOI 10.1007/s00330-021-07695-2",
      "verification": "INSPECTED",
      "what_it_did": "In 3,798 patients found that 'Small WHV was associated with over 4.4-fold risk of MACE (HR (per one standard deviation) = 0.221; 95% CI: 0.068-0.721; p = 0.012)'.",
      "what_it_did_not_do": "This is a direction warning rather than a competitor, and it should be carried into the write-up: bigger heart equals worse is NOT a safe prior for undifferentiated whole-heart volume. If the model's score rises monotonically with volume, that is a statement about what the model learned from reports, not an endorsement of the biomarker."
    },
    {
      "citation": "Kenia et al. Anatomy Contextualized Adaptation of CT Foundation Models.",
      "identifier": "arXiv:2607.27154",
      "verification": "INSPECTED",
      "what_it_did": "Uses TotalSegmentator masks to pool CT-CLIP and Merlin features into anatomy-level embeddings.",
      "what_it_did_not_do": "Uses segmentation to build better features, not to interrogate output scores. No volumetric correlation of any score. This is the nearest neighbour and it is doing the opposite thing - the closest work found in five queries, all of which returned NOT_FOUND for the specific link proposed here."
    }
  ],
  "existing_assets": [
    "ClassFine checkpoint, 1.77 GB, behind a free click-through under CC-BY-NC-SA 4.0.",
    "Precomputed TotalSegmentator outputs shipped with the corpus at dataset/ts_seg/ts_total, so the measurement may require no segmentation run at all.",
    "train_label_summary.xlsx and valid_label_summary.xlsx, which may already hold per-structure volumes - worth opening before writing any code.",
    "Idea 004 has already scoped a CT-RATE download of 850 validation volumes; if those are on disk the marginal data cost is near zero.",
    "TotalSegmentator's free whole-organ heart class as an independent check on the shipped segmentations."
  ],
  "smallest_decisive_experiment": "Accept the gate, then before anything else answer the collinearity question: extract heart volume and thoracic cavity volume from the shipped ts_total for the validation split and plot one against the other. If the joint distribution has no spread at fixed thoracic volume, stop - the interesting question is not identifiable in this corpus and the candidate should be re-scoped or dropped. If it does, run ClassFine over the same volumes and estimate the association between the cardiomegaly score and each of the two measurements, then the partial association of each conditional on the other. The design's discriminating move needs no intervention and no synthetic edit: CT-RATE has real, naturally occurring variation in reconstruction field of view and in-plane pixel spacing, so among patients matched on heart volume in millilitres the heart occupies materially different fractions of the frame. If the score follows millilitres and ignores the fraction, the model is using absolute volume; if it follows the fraction, it is using apparent size. Secondary, clearly separated: compare the score against the RadBERT Cardiomegaly label and against volume, to ask whether the model agrees with the reporting radiologist or with the ruler.",
  "standing_confounds_addressed": {
    "scanner_and_vendor": "PARTLY ADDRESSED by stratifying on manufacturer, which the paper reports as 61.5% Philips, 30.1% Siemens, 8.4% PNMS. Conditional on the metadata column existing, which is unverified.",
    "acquisition_protocol": "NOT ADDRESSED beyond stratification. Contrast phase in particular is unmeasured and materially affects the visibility of the cardiac border.",
    "reconstruction": "PARTLY ADDRESSED. Kernel affects the segmentation boundary less than it affects a density threshold, so this X is far more kernel-robust than C1's - which is a genuine advantage worth stating.",
    "site": "NOT ADDRESSED. CT-RATE is single-institution, which limits site variation but also means the result may not transfer.",
    "positioning": "NOT ADDRESSED. Arm position and table height shift the heart within the frame and would act through exactly the apparent-size channel the design is trying to isolate. This is the most under-controlled confound in the candidate and it should be measured, via body centroid and table position, even though it cannot be removed.",
    "habitus": "THIS IS THE HYPOTHESIS, not a nuisance. The absolute-versus-relative question is a question about habitus, and the design's whole point is to report it rather than adjust it away.",
    "prevalence": "NOT APPLICABLE to the primary readout, which is a within-corpus association rather than a comparison between populations.",
    "referral_pathway": "NOT ADDRESSED and live - sicker patients get scanned differently and also have bigger hearts.",
    "label_leakage": "NOT APPLICABLE to the primary readout, which uses no labels. In the secondary arm the label is RadBERT-extracted from the report and label noise attenuates toward the null, so it cannot manufacture a positive."
  },
  "alternative_explanations": [
    "Pericardial effusion. It is a separate label in the same 18 and it enlarges the cardiac silhouette without enlarging the heart. TotalSegmentator's whole-organ heart class may or may not include the effusion, which would make the measurement and the model wrong in the same direction and produce a spuriously clean association. PARTLY EXCLUDED by using the shipped ts_pleural_pericard_effusion output as a covariate and by reporting the analysis with effusion cases removed. This is the most dangerous confound in the candidate and it is specific to it.",
    "Collinearity of heart and thorax. Discussed as the keystone residual; if unresolved, a positive is uninterpretable between the two named hypotheses.",
    "The model tracks neither and the association is driven by whatever else correlates with body size in a single-institution corpus. PARTLY EXCLUDED by the matched-volume, varying-frame-fraction comparison.",
    "Honest self-assessment. 'The model turned a gestalt impression into millilitres' is a better sentence than the likely result deserves. The realistic outcome is a strong but unsurprising monotone association with volume plus an ambiguous partial association with the ratio, which is a modest finding. And the field has no gold standard here - two published definitions of heart volume differ by a factor of two - so a WEAK correlation would be genuinely uninterpretable between a bad model and a bad measurement. Identifiability is scored 3 for that reason and not only for collinearity."
  ],
  "anticipated_negative": {
    "classification": "sensitivity-limited",
    "reasoning": "A strong monotone association with volume is nearly certain and is not the finding. The finding is the absolute-versus-relative partial association, and a null THERE has several surviving explanations - insufficient joint variation, positioning noise acting through apparent size, or segmentation error correlated with body size. It is not uninterpretable, because the collinearity check is run first and reported, but it is not decisive either. Honest classification is type 2, and negative_result_value is scored accordingly rather than being talked up."
  },
  "remaining_legwork": [
    "Accept the CT-RATE gate; shared with idea 004 and already on that critical path.",
    "Open dataset/ts_seg/README.md and requirements.txt for the TotalSegmentator version, and the two label_summary.xlsx files to see whether volumes are precomputed. Hours, and it may remove a whole pipeline stage.",
    "Run head -1 on validation_metadata.csv for the acquisition columns. Minutes.",
    "The collinearity check. One day, and it is a genuine go/no-go for the interesting half.",
    "Validate the shipped heart segmentation against a local TotalSegmentator run on 30 volumes, with attention to whether pericardial fluid is included. Two days.",
    "Time to first decision: about a week after the gate, assuming idea 004's volumes are already on disk."
  ],
  "scores": {
    "clarity": {
      "value": 5,
      "why": "One model, one score, one measurement in millilitres, and a named binary alternative. Nothing about the question needs interpretation."
    },
    "identifiability": {
      "value": 3,
      "why": "The matched-volume varying-frame-fraction comparison genuinely separates absolute from relative size using existing variation rather than a synthetic edit, and pericardial effusion is controllable via a shipped segmentation. But there is no intervention anywhere, positioning is uncontrolled and acts through the very channel being isolated, referral pathway is unaddressed, and the collinearity that would make the question answerable is unverified. Three is the honest score."
    },
    "medical_relevance": {
      "value": 4,
      "why": "If the model is using absolute volume, it systematically over-calls cardiomegaly in large patients and under-calls it in small ones - a concrete, testable, correctable deployment failure in a finding that appears on a large share of chest CT reports. Held below 5 because cardiomegaly rarely drives management on its own."
    },
    "interest": {
      "value": 4,
      "why": "The framing - the model may have converted an admitted gestalt into a reproducible physical measurement - is genuinely surprising, and the inverted whole-heart-volume prognosis literature makes it less obvious than it first sounds. Held below 5 because the headline association is nearly certain and only the second-order question is uncertain."
    },
    "prior_legwork": {
      "value": 5,
      "why": "Checkpoint, labels, precomputed segmentations, possibly precomputed volumes, and a scoped download all in one gated repository."
    },
    "feasibility": {
      "value": 4,
      "why": "Cap lifted, keystone INSPECTED_TRUE. Inference-only on a released checkpoint with segmentations that may already exist. Held to 4 by the gate, by 3D download volume, and by the fact that nothing has actually been downloaded and run."
    },
    "data_readiness": {
      "value": 3,
      "why": "Public but behind a click-through contact-sharing agreement under CC-BY-NC-SA 4.0 with no redistribution, and the metadata columns the design wants are unread. Accessible with work."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "Rank correlation and partial association are standard, but there is no accepted normal range for heart volume on non-contrast CT and two published definitions differ by a factor of two, so any threshold-style claim needs its own justification. Custom metrics needed."
    },
    "negative_result_value": {
      "value": 3,
      "why": "Capped by the sensitivity-limited classification. A null on the second-order question has several surviving explanations, though the collinearity check being reported first keeps it out of uninterpretable territory."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Cap lifted but held at 3 on the evidence. The specific link was NOT_FOUND across four queries and the nearest work uses segmentation for feature pooling rather than score interrogation - but Regression Concept Vectors already formalize the general move, and this is the sort of quick analysis that could easily exist as a workshop paper in venues not searched."
    }
  },
  "priority_score": 3.85,
  "priority_arithmetic": "0.20*4 (feas) + 0.15*3 (ident) + 0.15*4 (med) + 0.10*5 (legwork) + 0.10*4 (interest) + 0.10*5 (clarity) + 0.10*3 (neg) + 0.05*3 (data) + 0.05*3 (novelty) = 0.80+0.45+0.60+0.50+0.40+0.50+0.30+0.15+0.15 = 3.85",
  "regret": {
    "value": 3,
    "why": "Worth considering rather than obvious-in-hindsight. If the model over-calls cardiomegaly in large patients, that will surface eventually in deployment; catching it first is useful but not the kind of finding that reframes a field."
  },
  "recommendation": "SHORTLIST CONDITIONAL - run the collinearity check first and re-score before committing to the full study.",
  "unverified_claims": [
    "That CT_LiPro_v2.pt loads and produces per-abnormality scores as expected. The file was seen in the tree at 1.77 GB; nothing was downloaded.",
    "That dataset/ts_seg/ts_total was produced by TotalSegmentator v2. Inferred from sibling folder names matching v2-only subtasks, not read from the gated README or requirements.txt.",
    "That the metadata CSVs contain Manufacturer, ManufacturerModelName, kernel, KVP and SliceThickness columns. Strongly implied by the paper reporting per-scan distributions, but the headers are gated and unread. Only VolumeName, RescaleSlope, RescaleIntercept, XYSpacing and ZSpacing are confirmed, from the authors' own inference script.",
    "That heart volume and thoracic cavity volume vary sufficiently independently in CT-RATE. Not checked, and load-bearing for the interesting half of the question.",
    "That the TotalSegmentator heart class excludes pericardial fluid. Not verified, and it is the candidate's most specific technical risk.",
    "Any absolute AUROC for CT-CLIP. The published text reports deltas only; three mutually inconsistent absolutes were seen in secondary sources and none is citable.",
    "That CT-RATE is single-institution. Assumed from prior cycles' notes rather than verified here."
  ]
}


===== STAGE TASK =====
Defend or amend the idea. Append one round to `debate.md` in the idea folder.

Format your append exactly as:

```
## Round N — PROPOSER

**Responding to:** [the critic's objection, restated in your own words]

**Response:** REBUT | AMEND | CONCEDE

**Argument:** [if rebutting: why the objection does not hold, with specifics.
If amending: exactly what changes in the idea, and whether that weakens the
contribution. If conceding: say plainly that the objection is correct.]

**Status:** OPEN | CONCEDED | IRREDUCIBLE DISAGREEMENT | CONVERGED
```

Rules:

- Restating your claim more confidently is not a rebuttal. If you have no new
  argument or evidence, CONCEDE.
- **Identity check on every AMEND.** Before submitting an amendment, answer:
  does the revised design still answer the original one-sentence question?
  If NO, do not submit the amendment. Concede, reject the current idea, and
  record the replacement under `spin-off` as a new candidate. An amendment
  that achieves feasibility by abandoning the motivating question is not a
  repair; it is a different study wearing the old title.

- AMEND is not free. Every amendment that dodges an objection by narrowing
  the claim must say what was lost. Three amendments usually means the
  original idea was wrong.
- If the critic is right, say so in round one. Speed of concession is a
  feature. Defending a dead idea across three rounds wastes the loop.
- Do not introduce a new idea mid-debate. If the discussion reveals a better
  question, note it under "spin-off" and keep defending the original.
- Append only. Never edit earlier rounds.



===== DEBATE STATE =====
You are claude. Your interlocutor is codex.
This is round 1. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The observational score–measurement analysis cannot identify that CT-CLIP uses absolute heart volume in millilitres, so it cannot support the original rung-3 deliverable or the claimed body-size-dependent over/under-calling.

**Argument:** Heart volume, transverse diameter, axial silhouette area, chamber shape, pericardial contour, diaphragm contact, pulmonary vascular changes, and thorax occupancy are correlated consequences of the same anatomy. A monotone association, partial regression, or matched-volume comparison can show only which automatic measurement predicts the frozen ClassFine cardiomegaly score better in CT-RATE; it cannot distinguish a model that uses volumetric extent from one that uses any correlated two-dimensional or morphological cue. The proposed natural variation in frame fraction is not a clean discriminator: the official CT-CLIP loader resamples to 0.75 x 0.75 x 1.5 mm and then center-crops or pads to 480 x 480 x 240, so frame occupancy also varies with coverage, table position, truncation, and preprocessing. Moreover, the clause that the model therefore over-calls large patients and under-calls small ones requires an independent clinical reference standard and a prespecified decision threshold; neither the label-free association nor CT-RATE's report-derived Cardiomegaly label supplies one. The repair suggested in the critique—asking whether score is better explained by whole-heart volume than by width, area, or an indexed measure—is a useful screening question, but the identity check fails: it replaces causal cue identification with comparative prediction and therefore no longer answers the original question, "is the model using millilitres?" It should remain a gate for a later intervention, not be accepted as the original candidate's result.

**What would change my mind:** Show a preregistered, in-distribution intervention or naturally paired same-patient design that changes physical heart volume relative to a stable thorax while holding the leading correlated cues and preprocessing artifacts fixed or measuring them as negative controls, and demonstrate a corresponding score change; separately, support the over/under-calling clause with an independent clinical reference and frozen operating threshold.

**Status:** OPEN

