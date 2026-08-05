You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/009
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


===== ideas/009/README.md =====
# Idea 009: Murray's cube law says how a branching tree should be built - ask whether the risk model is reading the lung's departure from it

Selected from scouting cycle 004, candidate 5.


===== ideas/009/critique.md =====
FATAL OBJECTION: The proposed observational partial associations cannot establish that Sybil uses vascular pruning, and the Murray-exponent arm has neither a validated LDCT measurement nor a disease-specific directional prediction.
EVIDENCE: Sobieski et al., arXiv:2602.02560; Altieri Correa et al., DOI 10.1115/1.4068886; idea_card.json `smallest_decisive_experiment` and `suspected_signal`.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial review

## Bottom line

There is a worthwhile descriptive analysis hiding here, but not the claimed model-decoding study. Stage 1 asks whether two quantities computed from the same CT covary: Sybil's risk score and BV5/TBV. Stage 2 adds another correlated CT phenotype, LAA%-950, to a regression. Neither varies vascular pruning independently of the rest of the image, probes the representation, occludes vessels with a valid control, or otherwise tests model reliance. A positive result is therefore compatible with Sybil completely ignoring vessels and reading any correlated smoking, airway, parenchymal, nodule, acquisition, or habitus signal. This fails rung 1 before the study reaches the rung-2 confound gate.

The card's own source makes the problem worse rather than solving it: San Jose Estepar et al. report that emphysema and vascular ratios are related (PMID 23656466; DOI 10.1164/rccm.201301-0162OC). Conditioning one noisy, reconstruction-sensitive image biomarker on another does not create independent variation. It can instead produce unstable coefficients, attenuation from differential measurement error, or collider/overadjustment effects among co-manifestations of smoking-related disease. The larger surviving coefficient cannot identify which feature the model uses.

This is the same estimand failure already established in the Idea 008 debate: association between a model output and a computable phenotype is not evidence of model use. It is not an annotation-provenance failure, but it does die like that prior candidate's unrepaired rung-1 objection. Calling the analysis a comparison of “competing mediators” is also incorrect without an exposure, an outcome-mediated causal estimand, and defensible mediator assumptions; these are correlated candidate readouts, not identified mediators.

## The Murray claim is not yet a hypothesis

The physical story is more specific than the evidence permits.

- Altieri Correa et al. analyzed seven healthy human pulmonary arterial geometries and reported a mean exponent of 2.31 ± 0.60; the human comparison with 3 was not significant (p=0.3721) (DOI 10.1115/1.4068886; PMID 40489106). Their data establish neither a normal individual-level reference nor a COPD, pruning, or cancer-risk shift.
- Dong et al. reported 2.92 ± 1.07 in 16 healthy subjects (PMID 32618514; DOI 10.1152/ajpheart.00127.2020). The disagreement and dispersion are large relative to the proposed effect, and both studies concern visible preacinar/angiographic anatomy rather than small vessels on NLST LDCT.
- “Remodeling changes the maintenance-to-dissipation cost ratio and therefore shifts the exponent” is speculation. The card gives no predicted direction, minimum effect, affected branch orders, or expected relationship between the fitted exponent and BV5/TBV. Without those, almost any exponent result can be narrated after the fact.
- Scale invariance under uniform multiplication of every radius does not imply invariance to breath hold. Inspiration changes vascular recruitment, distension, regional geometry, and which peripheral branches cross the visibility threshold. A segmentation-derived exponent can change even if the underlying branching law does not. The proposed C3 check is therefore a repeatability test, not proof of physiological invariance.

Dropping the analogy would indeed change the code, so the Murray framing is not merely verbal decoration. But extra code is not enough: it currently generates an unstable exploratory statistic without a validated biological interpretation. The compound deliverable is especially unsafe because a BV5-only positive cannot support the exponent clause, while an exponent-only positive is expressly declared unbelievable by the card.

## Measurement and data feasibility

The keystone is correctly marked `NOT_INSPECTED`, but Stage 0 as written cannot turn it true. “Consistent recovery depth” on 50 NLST and 50 diagnostic scans has no reference segmentation and therefore measures self-consistency or visual plausibility, not fidelity. Comparing low-dose with unmatched diagnostic cases additionally confounds dose with anatomy, disease, protocol, contrast, and reconstruction. No annotator-free statistic can reveal missed peripheral vessels when the reference tree is unknown.

There is closer prior work than the card acknowledges. Park et al. developed a noncontrast pulmonary-vessel segmentation model using matched virtual-noncontrast and contrast-enhanced vessel maps, tested it externally, and evaluated PVV5/%PVV5 on heterogeneous COPD LDCT with thin sections under 1.5 mm (Radiology: Cardiothoracic Imaging 2021; PMID 34036222; DOI 10.1148/ryct.2021200315). This shows that LDCT BV5 is not an untouched feasibility question. It does **not** rescue this study: that dedicated model and validation do not validate TotalSegmentator on NLST's 1–2.5 mm scans, and the reported implementation/weights are not established here as openly runnable.

The TotalSegmentator repository proves availability, not fitness for this endpoint. Its `lung_vessels` task now emits artery, vein, airway, and airway-wall classes, but the repository entry supplies no inspected NLST external validation, small-calibre recall curve, BV5 agreement, or bifurcation-radius accuracy. Moreover, separate artery/vein classification is not required for the original combined-vessel BV5 definition, so taking on A/V classification risk buys little for the primary endpoint. The 5 mm² boundary corresponds to about 2.52 mm diameter for a circular cross-section—precisely where slice thickness, partial volume, reconstruction kernel, denoising, and centerline/radius conventions can dominate.

The claimed low-hanging data are also less ready than stated. NLST images and Sybil weights are public, but “nodule-free” status depends on the Sybil team's radiologist annotations, and the repository record already notes unresolved held-out-ID reconciliation. Site is masked. Effective mAs adjustment cannot generally repair noise-dependent missed-branch bias, and DICOM dose fields plus body size do not identify the spatially varying noise texture after reconstruction.

Compute is not fatal on a single GPU for a small probe, but thousands of high-resolution vessel segmentations plus skeleton/radius processing are not a cheap add-on. The candidate should not inherit C1's data-readiness score of 5 when its decisive measurement pipeline, validation reference, and reliable branch scale are absent.

## Confounding, leakage, and circularity

There is no conventional concept-label circularity: BV5 is computed rather than assigned by the risk-label annotators, and the primary score-versus-phenotype analysis uses no cancer outcome. Report leakage is likewise irrelevant to Sybil's image-only input.

There is, however, measurement circularity of a different kind. Both BV5/TBV and LAA%-950 are functions of the same noisy reconstructed volume, and emphysema can make vessel boundaries harder for the segmenter. A “pruning” association may therefore be manufactured by disease-dependent segmentation failure. Adding recovery depth as a covariate does not fix this if recovery depth is itself estimated from the same segmentation.

The design does not rule out the standing alternatives:

- Scanner/vendor, kernel, slice thickness, dose/noise, and site can alter both model score and small-vessel recovery. Fixing or stratifying some fields reduces but does not isolate them.
- Inspiration, positioning, body habitus, and gravity-dependent vascular calibre remain plausible common causes or measurement modifiers.
- Smoking dose, airway disease, parenchymal texture, occult nodules, coronary calcium, and other cancer-risk phenotypes remain visible to Sybil and correlated with BV5.
- Disease prevalence and referral pathway are held relatively constant by the screening cohort, but that helps transport consistency, not within-cohort mechanism identification.

Partial regression rules out none of the unmeasured image alternatives. It only asks whether the chosen vascular summary contains residual linear information after chosen covariates, subject to overlap and measurement error.

## Endpoint and negative-result audit

The endpoint is underspecified. Sybil emits six horizon-specific risks, yet the card does not nominate one fixed horizon, a scale for the score, an effect form, an equivalence margin, multiplicity handling, or a minimum detectable partial association. “Estimate its association” invites horizon and model-form selection.

The anticipated negative is misclassified. A null partial BV5 coefficient after conditioning on LAA%-950 is **sensitivity-limited**, not decisive: it may reflect poor small-vessel recovery, multicollinearity, nonlinearity, range restriction in a single-kernel subset, inadequate overlap, or conditioning on a downstream co-phenotype. It does not strengthen the parenchymal hypothesis. The negative-result-value score should be at most 2 unless measurement agreement and an equivalence margin are established first. A Stage 0 failure is useful operational information, but it is not a negative answer about what Sybil uses and is unlikely to be publishable without a reference standard.

## Prior-work overlap and relevance

I did not verify a published BV5-versus-Sybil analysis. That is a search result, not a novelty claim; conference abstracts and active COPD vascular-imaging groups remain incompletely covered. The exact model link may be new, but novelty cannot compensate for an unidentified estimand.

Medical relevance is plausible but overstated. BV5/TBV has outcome and histology anchors in pulmonary disease, including the cited mortality association (PMID 32926788) and histologic comparison (PMID 34881020). Yet showing that a cancer-risk score correlates with it would not establish a causal cancer substrate, chronic hypoxia, immune surveillance, or a management implication. Those mechanistic bridges are speculative and should not motivate interpretation of the primary result.

## Easier formulation and existing assets

The genuinely low-hanging formulation is: on the already identified same-acquisition NLST reconstruction pairs, ask how repeatable **total intrapulmonary vessel volume and a provisional BV5/TBV estimate** are across kernels and slice thicknesses, and whether the corresponding within-pair Sybil score change covaries with the measurement change. The images, pair construction, Sybil code/checkpoint, and reconstruction metadata already exist in the repository's Idea 008/C1 legwork. No outcomes, nodule labels, or new cohort are required. The estimand is an acquisition-sensitivity audit: it can distinguish a shared reconstruction response from score stability while the vessel metric moves. It cannot establish biological pruning use.

Before even that analysis, the smallest honest gate is a method-comparison benchmark on publicly obtainable thin-section noncontrast CT cases with a trustworthy vessel reference or paired contrast-derived reference. Compare TotalSegmentator with the closest validated/released vessel method at branch-level recall, volume agreement, and threshold-crossing stability. If no usable reference labels or runnable comparator can be confirmed, do not manufacture “fidelity” from visual depth. The new TotalSegmentator weights and the published Park et al. validation are existing legwork, but they are not yet a ready labeled benchmark.

This easier audit is worth doing only as a small arm of the emphysema/reconstruction project, because it directly tests whether a proposed readout is a reconstruction artifact and can prevent a false biological story. It is not worth a standalone Sybil-mechanism paper, and it should not include the Murray exponent until branch-radius repeatability is demonstrated against reference geometry.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: On same-acquisition NLST reconstruction pairs, are provisional BV5/TBV measurements and Sybil risk scores coupled in their within-patient response to kernel and slice thickness, after first establishing vessel-measurement agreement at the relevant calibre?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes, as a bounded acquisition-sensitivity arm that can kill a vascular-artifact story cheaply; no, as evidence that Sybil uses biological pruning or Murray-law departure.


===== ideas/009/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed experiment cannot establish the original claim that Sybil uses pulmonary vascular pruning, because residual association between Sybil scores and BV5/TBV is not a test of model reliance.

**Argument:** Stage 1 correlates two quantities derived from the same NLST LDCT, and Stage 2 conditions that correlation on LAA%-950; neither intervention varies vascular information while preserving the model's other inputs, nor does it probe or ablate a vascular representation. A positive partial BV5/TBV coefficient therefore remains compatible with Sybil ignoring vessels entirely and using correlated smoking-related parenchymal texture, airway disease, occult nodules, coronary calcium, habitus, or reconstruction artifacts. This is especially acute because San Jose Estepar et al. reported an association between emphysema and vascular ratios (PMID 23656466; DOI 10.1164/rccm.201301-0162OC), while both BV5/TBV and LAA%-950 are reconstruction-sensitive measurements from the same voxels. Measurement error and disease-dependent vessel-segmentation failure can leave or create a residual coefficient; partial regression does not turn correlated phenotypes into competing identified mechanisms. The proposed same-acquisition reconstruction-pair amendment is useful only as an acquisition-sensitivity audit: it asks whether the provisional vessel metric and Sybil score respond together to kernel or slice thickness. That no longer answers the original biological-use question, so under the identity check it cannot rescue Idea 009 and should remain a bounded arm of the reconstruction project rather than be treated as evidence that Sybil reads pruning. The branching-exponent analysis has the same reliance problem even if its measurement becomes feasible.

**What would change my mind:** Show a validated, in-distribution intervention or representation test that selectively changes or removes pulmonary vascular calibre/tree information while preserving parenchyma, nodules, acquisition statistics, and gross anatomy, with sham interventions and same-patient controls, and demonstrate a preregistered Sybil score effect beyond the sham; alternatively, narrow the claim and deliverable explicitly to reconstruction-coupled covariance and treat it as a separate candidate rather than an explanation of what Sybil uses.

**Status:** OPEN


===== ideas/009/idea_card.json =====
{
  "id": "C5",
  "search_mode": "C",
  "entry_point": 2,
  "title": "Murray's cube law says how a branching tree should be built - ask whether the risk model is reading the lung's departure from it",
  "question": "Is the non-nodular part of Sybil's risk signal carried by pulmonary vascular pruning - small-vessel blood volume, and the departure of the arterial tree's caliber-ratio exponent from Murray's cube law - rather than by the parenchymal destruction that C1 proposes?",
  "deliverable_sentence": "The model is using pulmonary vascular pruning - the loss of blood volume in vessels below 5 square millimetres in cross-section, and the shift in the branching exponent away from the cube law that accompanies it - not parenchymal destruction.",
  "rung": {
    "current": 3,
    "why": "Vascular pruning is a named phenomenon with a named measurement that a thoracic radiologist recognizes, and the branching exponent is a physical quantity with a derivation.",
    "what_would_move_it_up": "Nothing above rung 3. What the claim needs to be credible rather than higher: the exponent measurement validated against something, which currently does not exist at cohort scale - see the honest assessment below."
  },
  "X_measurement": {
    "X": "Two quantities, deliberately ordered by how much weight each can bear. PRIMARY, because it is validated: BV5, the aggregate blood vessel volume in vessels under 5 square millimetres cross-section, normalized to total blood vessel volume. SECONDARY, because it is the mechanism but the measurement is immature: the caliber-ratio exponent k fitted from parent and daughter radii at detected bifurcations, r_parent^k = sum of r_daughter^k.",
    "how": "TotalSegmentator's free lung_vessels task gives lung_arteries, lung_veins, lung_airways and lung_airways_wall - confirmed Apache-2.0 and free, and the README cites Sci Data 2025 s41597-025-06074-6 and arXiv:2404.03010 for it. Cross-sectional area binning for BV5 is not provided off the shelf and must be implemented, or ChestImagingPlatform used, which is source-build only with no pip or conda package and a custom non-OSI license. The exponent additionally requires skeletonization, bifurcation detection and per-branch radius estimation.",
    "citations": "BV5 definition and original: San Jose Estepar R, Washko GR et al., Am J Respir Crit Care Med 2013;188(2):231-239, PMID 23656466, PMC3778757, defining it as 'the aggregate vessel volume for vessels less than 5 mm2' and concluding that 'Smoking-related chronic obstructive pulmonary disease is characterized by distal pruning of the small blood vessels (<5 mm2) and loss of tissue in excess of the vasculature.' Mortality anchor: Synn AJ, Rice MB et al., Am J Respir Crit Care Med 2021;203(2):251-254, PMID 32926788, Framingham n=2,470: 'Each SD lower BV5/TBV (i.e., more severe pruning) was associated with a 35% greater rate of death (HR, 1.35; 95% CI, 1.09-1.68; P = 0.006).' Histologic validation: Synn AJ et al., Pulm Circ 2021, PMID 34881020, n=138, correlation of BV5/TBV with vessel wall area percent of minus 0.41. Exponent reference: Altieri Correa S, Chesler NC et al., J Biomech Eng 2025;147(8):081006, PMID 40489106.",
    "could_I_compute_it_today_without_asking_anyone": "BV5, yes with implementation work - the segmentation is free and the binning is geometry. The exponent, yes in principle and not reliably in practice at the vessel calibres that matter on low-dose screening CT. That distinction is the candidate's central feasibility problem and it is why BV5 is primary."
  },
  "suspected_signal": "Murray's law follows from minimizing the sum of two costs: the viscous power dissipated driving flow through a tube, which falls steeply with radius, and the metabolic cost of maintaining the blood it contains, which rises with radius. Minimizing the total gives flow proportional to radius cubed, hence a conserved cube of radius across a bifurcation. Smoking-related vascular remodeling destroys and narrows the distal small vessels first - the pruning that BV5 measures directly - which changes the ratio of maintenance cost to dissipation cost the tree is optimizing, and therefore shifts the exponent away from the healthy value. So the exponent is not a redescription of pruning; it is a scale-free summary of the same remodeling that is invariant to overall lung size and to inflation level, where BV5 is a bulk volume that is not. Pruning is in turn a plausible substrate for cancer risk through chronic hypoxia, impaired immune surveillance in underperfused parenchyma, and its established association with mortality.",
  "keystone_prerequisite": "Pulmonary arterial and venous trees can be segmented from NLST low-dose screening CT by a free tool at sufficient fidelity that per-vessel cross-sectional area can be binned, and bifurcations resolved, in the calibre range where pruning occurs.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_evidence": "What is established: TotalSegmentator's lung_vessels task exists, is free under Apache-2.0, and outputs lung_arteries and lung_veins as separate classes - read directly from map_to_binary.py. What is NOT established, and is exactly what the inference needs: its performance on LOW-DOSE screening CT at 1 to 2.5 mm slice thickness, in vessels around and below 2 mm diameter, which is at the resolution limit. No off-the-shelf calibre binning exists in that tool. ChestImagingPlatform, the public descendant of the software the BV5 literature actually used, has no pip or conda package and no tagged releases - the README defers dependency resolution to an external link - and the original BV5 paper used 'in-house software' rather than CIP. Mode C permits this status and I am reporting it rather than working around it.",
  "keystone_residual_assumption": "Having established that a free vessel segmenter exists, I am still assuming the entire measurement chain downstream of it: that cross-sectional area can be estimated per vessel segment accurately enough to bin at a 5 square millimetre boundary on low-dose data, and - for the secondary quantity - that radii at bifurcations can be estimated well enough to fit an exponent. The second assumption is almost certainly too optimistic, and the literature says so implicitly: the ENTIRE human evidence base for a pulmonary Murray exponent is about 23 subjects across two papers, reporting 2.31 +/- 0.60 and 2.92 +/- 1.07. Those standard deviations exclude essentially nothing, on hand-curated angiographic geometries, which is a strong signal that the measurement is hard even under favourable conditions. I would rather state that the exponent is the mechanism and BV5 is the measurement than pretend both are equally available.",
  "rung_reached": {
    "value": 3,
    "conditional_on": "BV5 carrying the result. If only the exponent moves and BV5 does not, the finding should be treated as a measurement artifact until independently replicated, given how underpowered the exponent literature is."
  },
  "dies_like_prior": "No annotation-provenance failure applies - both quantities are computed from voxels by tools, and the model score is a checkpoint output. No intervention-validity failure applies, because nothing is edited. The candidate's own most likely death is neither of those: it is that the measurement is not achievable at the resolution of low-dose screening CT, which is a feasibility death rather than a validity death, and Mode C exists to permit exactly that risk. The one prior pattern it does share is scout-003's dropped question 7, which died because a pulmonary vascular class could not be confirmed in a released segmentation output. That specific blocker is now resolved - lung_vessels exists and is free - so the vascular question has advanced one step in two cycles, from 'no tool confirmed' to 'tool confirmed, fidelity unknown'.",
  "closest_prior_work": [
    {
      "citation": "San Jose Estepar R, Washko GR et al. Computed Tomographic Measures of Pulmonary Vascular Morphology in Smokers and Their Clinical Implications.",
      "identifier": "Am J Respir Crit Care Med 2013;188(2):231-239, PMID 23656466, PMC3778757",
      "verification": "INSPECTED",
      "what_it_did": "Defined BV5, established distal pruning in smoking-related COPD in 359 smokers and 82 never-smoker controls.",
      "what_it_did_not_do": "Relates the measurement to disease, not to any model. Critically for this cycle, it also reports that '%LAA-950 was inversely related to all calculated vascular ratios' - which is the single most important sentence for the C1-versus-C5 comparison, because it means the two candidates' named explanations move together and a positive for either is weak evidence against the other. Any design that runs both must report partial associations, not marginal ones."
    },
    {
      "citation": "Altieri Correa S, Kachabi A, Colebank MJ, Miles CE, Chesler NC. Revisiting Murray's Law in Pulmonary Arteries.",
      "identifier": "J Biomech Eng 2025;147(8):081006, PMID 40489106, DOI 10.1115/1.4068886",
      "verification": "INSPECTED (abstract; the human-cohort modality detail is SEARCH_SUMMARY_ONLY)",
      "what_it_did": "Measured the exponent across four species: 'an average exponent value of 2.31(+/-0.60) in human... all lower than the predicted value of 3.0 from Murray's Law.' Human n=7, on geometries reported by a search summary to be mixed CT and MR angiography.",
      "what_it_did_not_do": "n=7 humans on curated angiographic geometries. It gives the candidate a reference value and simultaneously warns that the measurement is imprecise. Corroborating and diverging: Dong M, Marsden AL, Feinstein JA et al., Am J Physiol Heart Circ Physiol 2020, PMID 32618514, n=16, reports 2.92 +/- 1.07. Theory permits the departure - Kassab GS, 2006, PMID 16143652: 'The exponent of the diameter-flow rate relation is not necessarily equal to 3.0 as required by Murray's law but depends on the ratio of metabolic to viscous power dissipation.' NOT_FOUND across four queries: any human study measuring a pulmonary Murray exponent in COPD, smoking, pulmonary hypertension or fibrosis. The only disease-related shift is ovine - Ghorishi Z, Eldridge MW et al., 2007, PMID 17308003, where shunt-hypertensive lambs retain the fetal exponent."
    },
    {
      "citation": "Helmberger M, Olschewski H, Balint Z et al. Quantification of Tortuosity and Fractal Dimension of the Lung Vessels in Pulmonary Hypertension Patients.",
      "identifier": "PLoS One 2014;9(1):e87515, PMID 24498123",
      "verification": "INSPECTED",
      "what_it_did": "Measured 3D fractal dimension and tortuosity of the pulmonary vascular tree on contrast CT.",
      "what_it_did_not_do": "Found 3D fractal dimension NOT significantly different in pulmonary hypertension, with only tortuosity tracking mean pulmonary artery pressure. This directly contradicts a 2D fractal dimension result - Sun H et al., Korean J Radiol 2011, PMID 21603288, reporting 1.64 versus 1.54 - and the inconsistency is a warning that geometric summaries of this tree are unstable across methods. It is the reason the exponent is secondary here."
    },
    {
      "citation": "Mikhael et al. JCO 2023 and Sobieski et al. arXiv:2602.02560, as detailed under C1.",
      "identifier": "PMID 36634294; arXiv:2602.02560",
      "verification": "INSPECTED",
      "what_it_did": "Established the non-nodular residual signal and audited nodule contributions.",
      "what_it_did_not_do": "Neither paper measures anything vascular. The audit paper's speculation names emphysema, not pruning - so this candidate is proposing an explanation nobody has put in print, which is the point of Mode C and also the reason it carries more risk than C1."
    }
  ],
  "existing_assets": [
    "TotalSegmentator lung_vessels, free and Apache-2.0, with separate artery and vein classes - the blocker that killed this question in the previous cycle.",
    "Sybil weights under MIT and NLST imaging under CC BY 4.0, shared with C1, so the model and data cost nothing beyond what C1 already pays.",
    "A mature outcome-anchored literature for BV5 including a Framingham mortality hazard ratio and histologic validation, so the biomarker's meaning does not have to be argued from scratch.",
    "A published human reference value for the exponent, with honest uncertainty attached.",
    "If C1 runs, the entire pipeline except the vessel analysis already exists, which is the strongest practical argument for running this as an arm of C1 rather than as a separate study."
  ],
  "smallest_decisive_experiment": "Stage 0 is a pure feasibility probe and it decides everything: run TotalSegmentator lung_vessels on 50 NLST low-dose scans and 50 matched diagnostic-quality chest CTs, and measure whether the artery and vein trees are recovered to a consistent depth and whether cross-sectional areas can be estimated stably around the 5 square millimetre boundary. Report the calibre at which recovery degrades. If the tree is only reliable above 5 square millimetres, BV5 is not measurable on this data and the candidate stops - a feasibility result the charter counts as success, and one that would also tell the vascular-imaging community something useful about applying a free tool to screening CT. Stage 1, if Stage 0 passes: compute BV5 normalized to total blood vessel volume on held-out nodule-free NLST scans at fixed kernel, and estimate its association with Sybil's score. Stage 2 is the only analysis that distinguishes this candidate from C1 and it must be pre-registered as the primary comparison rather than an add-on: compute LAA%-950 on the same scans and report the PARTIAL association of the score with each, conditional on the other. Given that the two are known to be inversely related, marginal associations would produce two positives and no answer. Stage 3, exploratory and labelled as such: fit the branching exponent on the subset where the tree is recovered deeply enough, and ask whether it adds anything after BV5 - with the pre-registered expectation that it probably will not, and that a positive here without a BV5 positive should be disbelieved.",
  "standing_confounds_addressed": {
    "scanner_and_vendor": "PARTLY ADDRESSED by stratification. Vessel segmentation fidelity varies with scanner and reconstruction more than a bulk density measure does, which makes this worse here than in C1.",
    "acquisition_protocol": "NOT ADDRESSED beyond stratification. NLST is non-contrast, which is a genuine limitation for vessel work - most of the BV5 literature and all of the exponent literature uses better-contrasted or contrast-enhanced data.",
    "reconstruction": "PARTLY ADDRESSED by fixing the kernel, and the same paired-kernel manipulation available to C1 applies here and should be used - if BV5 shifts across kernels the way LAA-950 does, the same discipline is required.",
    "site": "NOT ADDRESSED AND NOT ADDRESSABLE, per the masked screening centre.",
    "positioning": "PARTLY ADDRESSED - the measurement is defined on a segmented tree rather than on fixed coordinates. But gravity-dependent perfusion differences between dependent and non-dependent lung are real and are not removed.",
    "habitus": "NOT ADDRESSED. Body size affects both vessel volume and image noise, and noise affects small-vessel recovery. Mitigated by normalizing BV5 to total blood vessel volume, which is the convention the source literature uses for exactly this reason.",
    "prevalence": "ADDRESSED by construction, single screening cohort.",
    "referral_pathway": "ADDRESSED by construction, trial enrollment.",
    "label_leakage": "NOT APPLICABLE - no labels in the primary readout.",
    "inflation_level": "NOT ADDRESSED and specific to this candidate: bulk vessel volume depends on how inflated the lung is, which C3 shows is uncontrolled in any single-scan corpus. The exponent is scale-free and therefore immune, which is the one respect in which the secondary quantity is better than the primary one - and it is the concrete reason the Murray framing is not decorative."
  },
  "alternative_explanations": [
    "Parenchymal destruction, i.e. C1's explanation. NOT EXCLUDED by design, only by partial association, because the two quantities are inversely correlated by the source literature's own report. This is the candidate's central identifiability problem and it is why C1 and C5 should probably be run as one study with two named mediators rather than as two studies.",
    "Vessel segmentation fidelity varying with disease severity. Emphysematous lung has less contrast around vessels, so the segmenter may recover fewer small vessels in exactly the patients who are sickest - which would manufacture the pruning association from a tool artifact. This is the same shape of failure as C4's segmenter risk and it is at least as likely here. PARTLY EXCLUDED by reporting recovery depth as a covariate and by the Stage 0 calibre-degradation curve.",
    "Noise. Small-vessel recovery on low-dose CT is noise-limited, and noise scales with body size and with automatic exposure control. PARTLY EXCLUDED by including effective mAs as a covariate.",
    "Honest self-assessment. Murray's law is the most attractive-sounding idea in this portfolio and the one most at risk of being decoration. The charter's test is what would change if the analogy were dropped, and the answer is given under cross_domain below - it is a real answer, involving different code and a specific invariance property. But I want to be plain that the exponent is very unlikely to be measurable at NLST resolution, that its human evidence base is 23 subjects, and that if this candidate produces a result it will almost certainly be a BV5 result with the exponent as an unfalsified aside. Anyone reading the title should read that sentence too."
  ],
  "anticipated_negative": {
    "classification": "decisive",
    "reasoning": "Conditional on Stage 0 passing, a null in Stage 2 - BV5 showing no partial association with Sybil's score once LAA%-950 is conditioned on - is decisive for the vascular hypothesis and simultaneously strengthens C1's parenchymal one, because the two are tested against each other on the same scans in the same model. That is the value of running competing named explanations jointly: neither can produce an uninterpretable null, because the alternative is measured in the same breath. If Stage 0 fails the result is a feasibility finding about applying free vessel segmentation to low-dose screening CT, which is useful and publishable but is not an answer to the question asked."
  },
  "cross_domain": {
    "borrowed_construct": "Optimal-transport scaling laws for biological distribution networks - Murray's 1926 minimization of viscous dissipation plus metabolic maintenance cost, and its descendants in allometric scaling theory - which predict a conserved power of radius across every bifurcation of a well-built tree.",
    "measurement_it_implies": "Do not measure how much vasculature there is. Measure the RATIO between parent and daughter calibres at bifurcations, and fit the exponent that makes it conserved. That is a scale-free quantity: it does not change if the lung is bigger, and it does not change if the patient inhaled more deeply.",
    "what_changes_if_the_analogy_is_dropped": "You measure BV5 and stop. BV5 is a bulk volume, so it inherits every problem that C3 exists to demonstrate: it depends on how inflated the lung was, on body size, and on total lung volume, and none of those are controlled in a single-scan corpus. The scaling-law framing says the informative quantity is a ratio at a junction, which is invariant to all three by construction, and it supplies a predicted value - 3 for laminar flow - that the measurement can be checked against rather than merely reported. Concretely different code: skeletonize the segmented tree, detect bifurcations, estimate radii on both sides, fit an exponent - none of which appears in a BV5 pipeline. It also generates a falsifiable prediction the bulk measure cannot: the exponent should be stable across C3's inflation states while BV5 should not, which is a test that can actually be run on the CT-vs-PET breath-hold pairs. That test is the strongest evidence that the analogy is load-bearing rather than ornamental, and it costs one extra analysis on data another candidate is already downloading."
  },
  "remaining_legwork": [
    "Stage 0 vessel-recovery feasibility probe on 50 low-dose and 50 diagnostic scans. Two weeks including segmentation time, and it is a hard go/no-go.",
    "Implement calibre binning, since no free tool provides it. Two to three weeks.",
    "Decide whether to build ChestImagingPlatform from source as a reference implementation, given no pip package and a custom license. One week, possibly wasted.",
    "If Stage 3 is attempted: skeletonization and bifurcation radius estimation. A month, with a high chance of producing a number nobody should believe.",
    "Time to first decision: Stage 0 in about two weeks, and it is likely to be the decision."
  ],
  "scores": {
    "mechanism_clarity": {
      "value": 4,
      "why": "Two specifically named physical quantities with derivations and measurement definitions, one of them - BV5 - validated against histology and anchored to a mortality hazard ratio in Framingham. Held below 5 because the quantity that carries the MECHANISM, the exponent, does not have a usable measurement at this resolution, and the quantity that has a usable measurement is a bulk volume whose mechanistic story is thinner. A candidate whose mechanism and whose measurement sit on different variables is not at the top of this scale."
    },
    "identifiability": {
      "value": 3,
      "why": "The partial-association design against C1's named alternative is genuinely discriminating, and the inflation-invariance prediction is a real test that can be run on C3's data. But BV5 and LAA-950 are known to be inversely correlated, segmentation fidelity plausibly varies with the disease being measured, and the whole thing is observational. Three."
    },
    "interest": {
      "value": 4,
      "why": "Proposing a vascular rather than parenchymal explanation for a documented gap is a genuine claim nobody has published, and it serves the charter's named vascular emphasis, which has gone unfilled for two cycles. Held below 5 because the likely outcome is a feasibility wall rather than an answer."
    },
    "medical_relevance": {
      "value": 4,
      "why": "Pruning is outcome-anchored - a 35 percent higher death rate per standard deviation in Framingham - and unlike emphysema it is not something a radiologist reads off a screening CT today, so a positive would point at a finding that is currently invisible in practice. Held below 5 because nothing in management changes on this result alone."
    },
    "clarity": {
      "value": 4,
      "why": "The question names two quantities, the competing explanation, and the comparison. Held below 5 because carrying a primary and a secondary X makes the claim compound, and a result that splits between them will be harder to state in one sentence than the deliverable implies."
    }
  },
  "mode_c_priority_score": 3.75,
  "mode_c_priority_arithmetic": "0.30*4 (mechanism) + 0.25*3 (ident) + 0.20*4 (interest) + 0.15*4 (med) + 0.10*4 (clarity) = 1.20+0.75+0.80+0.60+0.40 = 3.75",
  "reported_outside_the_score": {
    "feasibility": {
      "value": 2,
      "why": "CAPPED at 3, scored 2 on the evidence. Vessel segmentation on non-contrast low-dose screening CT at the calibres that matter is the hardest measurement in the portfolio, no free tool does calibre binning, and the reference implementation has no installable package. Mode C explicitly forbids demoting the candidate for this, and the score here is reported outside the priority calculation for that reason."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "CAPPED at 3, and 3 is also the honest estimate. No human study measures a pulmonary Murray exponent in disease, and no study relates vascular pruning to a lung cancer risk model. But BV5 is a well-worked field with an active group, and a pruning-versus-Sybil analysis is a natural thing for that group to do next."
    },
    "data_readiness": {
      "value": 5,
      "why": "Shared with C1: CC BY 4.0 imaging, MIT weights, public outcomes, no gate."
    },
    "evaluation_readiness": {
      "value": 2,
      "why": "BV5 has published conventions but no accessible reference implementation; the exponent has no accepted CT measurement protocol at all. Unclear, and much would have to be invented."
    },
    "negative_result_value": {
      "value": 4,
      "why": "Decisive conditional on Stage 0, because the competing explanation is measured simultaneously on the same scans."
    }
  },
  "sibling_disclosure": "C5 and C1 share Sybil, NLST, the held-out split, the kernel discipline and the nodule-free population, and they propose COMPETING explanations for the same residual signal. They are not independent bets and a reviewer should not count them as two. My recommendation is explicit: do not fund them separately. Run C1, and add BV5 as a second pre-registered mediator inside it, with the partial-association analysis as the primary comparison. That gets the scientific benefit of the competition - neither explanation can produce an uninterpretable null when the other is measured alongside it - at a fraction of the cost, and it removes the temptation to report whichever marginal association came out larger.",
  "regret": {
    "value": 4,
    "why": "If the answer is vascular and everyone spends five years measuring parenchyma because one ICML paper wrote the word emphysema in a speculative sentence, that would be a costly and avoidable wrong turn. The regret is real; the probability of getting to an answer is what is low."
  },
  "recommendation": "DO NOT SHORTLIST AS A STANDALONE STUDY. Run Stage 0 as a two-week feasibility probe, and if it passes, fold BV5 into C1 as a competing mediator rather than running this separately. The Murray exponent should be carried as an explicitly exploratory arm and reported as such however it comes out.",
  "unverified_claims": [
    "That TotalSegmentator lung_vessels recovers vessels at the calibres BV5 requires, on non-contrast low-dose screening CT. Completely untested and it is the keystone.",
    "That cross-sectional area can be estimated stably enough to bin at 5 square millimetres on this data.",
    "That the branching exponent is measurable at all from NLST-quality data. I doubt it, and I have said so rather than letting the title imply otherwise.",
    "The modality of the human geometries in Altieri Correa et al. A search summary indicates mixed CT and MR angiography; the methods section could not be opened.",
    "That ChestImagingPlatform builds from source in a reasonable time. No pip package, no tagged releases, custom license.",
    "That vessel segmentation fidelity does not itself vary with emphysema severity. Untested, and it is the most plausible route to a false positive.",
    "That no BV5-versus-risk-model analysis exists. The BV5 literature is concentrated in a small number of groups and searches did not cover ATS or thoracic society abstracts, where that community publishes first."
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

**Position:** The proposed experiment cannot establish the original claim that Sybil uses pulmonary vascular pruning, because residual association between Sybil scores and BV5/TBV is not a test of model reliance.

**Argument:** Stage 1 correlates two quantities derived from the same NLST LDCT, and Stage 2 conditions that correlation on LAA%-950; neither intervention varies vascular information while preserving the model's other inputs, nor does it probe or ablate a vascular representation. A positive partial BV5/TBV coefficient therefore remains compatible with Sybil ignoring vessels entirely and using correlated smoking-related parenchymal texture, airway disease, occult nodules, coronary calcium, habitus, or reconstruction artifacts. This is especially acute because San Jose Estepar et al. reported an association between emphysema and vascular ratios (PMID 23656466; DOI 10.1164/rccm.201301-0162OC), while both BV5/TBV and LAA%-950 are reconstruction-sensitive measurements from the same voxels. Measurement error and disease-dependent vessel-segmentation failure can leave or create a residual coefficient; partial regression does not turn correlated phenotypes into competing identified mechanisms. The proposed same-acquisition reconstruction-pair amendment is useful only as an acquisition-sensitivity audit: it asks whether the provisional vessel metric and Sybil score respond together to kernel or slice thickness. That no longer answers the original biological-use question, so under the identity check it cannot rescue Idea 009 and should remain a bounded arm of the reconstruction project rather than be treated as evidence that Sybil reads pruning. The branching-exponent analysis has the same reliance problem even if its measurement becomes feasible.

**What would change my mind:** Show a validated, in-distribution intervention or representation test that selectively changes or removes pulmonary vascular calibre/tree information while preserving parenchyma, nodules, acquisition statistics, and gross anatomy, with sham interventions and same-patient controls, and demonstrate a preregistered Sybil score effect beyond the sham; alternatively, narrow the claim and deliverable explicitly to reconstruction-coupled covariance and treat it as a separate candidate rather than an explanation of what Sybil uses.

**Status:** OPEN

