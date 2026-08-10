You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-007
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


===== evidence/ledger_digest.md =====
# Ledger digest (auto-generated -- do not edit; run `python scout.py ledger digest`)

18 tracked ideas. Latest state per idea; full history in ledger.jsonl.

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.
- **CIRCULARITY** x1: The endpoint is a re-encoding of the input or of the thing being tested.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **scout-006-c04** [NOVEL_UNVERIFIED, audited 2026-08-10] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-006-c05** [NOVEL_UNVERIFIED, audited 2026-08-10] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two
- **scout-006-c03** [INCREMENTAL, audited 2026-08-10] -- An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver

## Ideas

- **idea-001** [REJECTED/DEBATED/baseline] -- Have lung nodule concept models been validated against radiologist opinion rather than against disease? -- killed: DATA_INSUFFICIENT -- data: {"primary": "LIDC-IDRI via The Cancer Imaging Archive", "license": "CC BY 3.0", 
- **idea-002** [PAUSED/DEBATED/baseline] -- Dermoscopic concepts predicted from non-dermoscopic photographs: genuine visibility or shortcut? -- data: {"primary": "Derm7pt paired clinical/dermoscopic images", "source": "github.com/
- **idea-003** [ACTIVE/DEBATED/baseline] -- Does BI-RADS concept intervention survive realistic clinician behaviour, and does it beat simply reading the BI-RADS category? -- data: {"primary": "BUS-BRA (Zenodo 8231412, CC BY 4.0) for the external and baseline a
- **idea-004** [ACTIVE/DEBATED/baseline] -- The free test-retest experiment already inside CT-RATE: duplicate reconstructions of the same acquisition
- **idea-005** [PAUSED/DEBATED/baseline] -- Eight named characteristics, or three latent ones? Discriminant validity of the LIDC concept vocabulary
- **idea-006** [PAUSED/DEBATED/baseline] -- Ask the chest-CT foundation model to diagnose a volume with no patient in it
- **idea-007** [ACTIVE/DEBATED/baseline] -- The same patient, twice, ten minutes apart, differing only in how much air is in the lungs
- **idea-008** [ACTIVE/DEBATED/baseline] -- Two papers say Sybil's residual signal is the background, one of them names emphysema, and neither measured it
- **idea-009** [ACTIVE/DEBATED/baseline] -- Murray's cube law says how a branching tree should be built - ask whether the risk model is reading the lung's departure from it
- **idea-010** [REJECTED/DEBATED/baseline] -- Cardiomegaly on a CT report is admitted gestalt - ask whether the model has quietly turned it into millilitres -- killed: CIRCULARITY
- **idea-011** [PAUSED/DEBATED/baseline] -- Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock
- **idea-012** [PAUSED/DEBATED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **idea-013** [SHORTLISTED/DEBATED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **scout-006-c01** [SHORTLISTED/SCOUTED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **scout-006-c02** [SHORTLISTED/SCOUTED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **scout-006-c03** [SCOUT_ONLY/SCOUTED/baseline] -- An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver
- **scout-006-c04** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-006-c05** [SCOUT_ONLY/SCOUTED/baseline] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two


===== evidence/portfolio_brief.md =====
# Portfolio brief (auto-generated; run `python scout.py brief`)

Actionable ideas with debate verdicts. A revival/recombination
candidate MUST cite the specific condition below that has changed.

## idea-013 [SHORTLISTED] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity

**Verdict:** **REVISE.** Rewrite the idea card around the reduced rung-1 calibration and reconstruction-sensitivity audit, with localisation explicitly excluded and the keystone set to `NOT_INSPECTED`. The single most important thing for the human to inspect before deciding is whether a validated, annotation-free coronary target localiser for nongated noncontrast CT actually exists and runs on CT-RATE; that fact determines whether the high-value localisation question has a credible spin-off or whether idea 013 should remain only a modest robustness audit.

**Unresolved:** Is the reduced rung-1 audit worth running?; Can the localisation question be revived as a separate intervention study?; Would validated synthetic edits identify calcium location rather than edit artifacts?

## idea-012 [PAUSED] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan

**Verdict:** **PAUSE.** Before deciding otherwise, the human should inspect whether the MD.ai-derived scan-level exclusion membership has become available—and is joinable to a frozen obtainable Sybil evaluation split—because without it the study cannot test the specific residual that defines Idea 012.

## idea-011 [PAUSED] -- Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock

**Verdict:** **PAUSE.** The debate converged after a real, persistent objection; this was not a one-round rubber stamp. Before deciding whether to reopen, the human should look first for the missing identification instrument: a confirmed human chest CT resource with retained spectral base-material or dual-kV raw data and linkable age that can provide a measured, post-preprocessing-matched mineralized-to-soft-tissue contrast. Without that—or another genuinely matched real-tissue control—the current experiment cannot distinguish native use of costal cartilage mineralization from response to the deletion operation, regardless of improvements to masks, models, or supervision audits.

**Unresolved:** Can a measured, properly matched control separate mineralization use from the deletion signature?; Could registered longitudinal CT provide a natural contrast?; Is the editable cartilage mask sufficiently precise in the population where the experiment would run?; Are the other Stage-0 assets actually available and clean?

## idea-009 [ACTIVE] -- Murray's cube law says how a branching tree should be built - ask whether the risk model is reading the lung's departure from it

**Verdict:** **REJECT.** Before deciding, the human should look most closely at the estimand mismatch: neither association with a computable vascular phenotype nor sensitivity to synthetic vessel deletion identifies reliance on naturally occurring pruning and Murray-exponent departure. Revisit only if a dataset and validated design can isolate natural within-patient BV5 and exponent variation from acquisition and parenchymal change, with adequate exponent repeatability and a model-reliance test tied to that variation.

## idea-008 [ACTIVE] -- Two papers say Sybil's residual signal is the background, one of them names emphysema, and neither measured it

**Verdict:** **REVISE.** The debate produced a coherent conditional design, but the current `idea_card.json` still describes the superseded reconstruction arm, rung-3 observational logic, `INSPECTED_TRUE` keystone, and obsolete scores. Before deciding whether to advance, the human should look most closely at whether the proposed tissue-for-tissue edit can be validated as in-distribution with a prespecified sham-effect tolerance; that is now the single fact separating a model-use study from an association-only study.

**Unresolved:** Are the local parenchymal substitutions in-distribution for Sybil?; Does a score response isolate CT-emphysema geometry from remaining visible correlates?; Can the required held-out NLST cohort and covariates actually be recovered?

## idea-007 [ACTIVE] -- The same patient, twice, ten minutes apart, differing only in how much air is in the lungs

**Verdict:** **REVISE.** Update the idea card to the converged state-level claim and corrected scores, then require Stage 0 before a probe contract. The single most important thing for the human to inspect is the prespecified DICOM-to-final-tensor comparability gate: whether enough inhale/exhale pairs truly retain matched reconstruction, coordinates, physical scale, and thoracic coverage through the complete pinned CT-CLIP preprocessing pipeline.

**Unresolved:** Do enough actual pairs pass the reconstruction and framing gate?; Is a common physical box compatible with CT-CLIP preprocessing without state-dependent framing?; Is the optional matched-volume 4DCT jitter floor usable?

## idea-006 [PAUSED] -- Ask the chest-CT foundation model to diagnose a volume with no patient in it

**Verdict:** **PAUSE.** Before deciding whether the pause is reversible, the human should inspect the official CT-CLIP training data loader and augmentation configuration for large-region masking or cutout with a matching fill value. Absence would make the original intervention indefensible for this checkpoint; presence would justify distributional validation, not automatic advancement.

**Unresolved:** Did CT-CLIP training make large constant-filled occlusions sufficiently familiar?; Could the original question be valid for a different chest-CT model?

## idea-005 [PAUSED] -- Eight named characteristics, or three latent ones? Discriminant validity of the LIDC concept vocabulary

**Verdict:** **REJECT** the original idea as currently framed. The single most important thing for the human to inspect is whether to promote spin-off S2—the direct test of reader-slot exchangeability—into a fresh candidate, because it preserves the cheap public-data audit while avoiding the undefined dimension-count estimand.

**Unresolved:** Can a narrower pairwise latent-correlation audit be scientifically useful?; Can a global partition estimator recover a defensible dimension count?; Are LIDC reader slots empirically exchangeable?



===== evidence/librarian_proposals.md =====


===== ideas/scout-007/README.md =====
# Scouting cycle 007

Tracks: baseline, wide, fiction


===== ideas/scout-007/scout_candidates.json =====
{
  "cycle": "scout-007",
  "stage": "scout",
  "generated_on": "2026-08-10",
  "tracks": ["baseline", "wide", "fiction"],
  "records_read": [
    "evidence/decisions.md (injected in full)",
    "evidence/ledger_digest.md (injected in full)",
    "evidence/portfolio_brief.md (injected in full)",
    "ideas/scout-006/scout_candidates.json (schema and occupied-topic review)"
  ],
  "evidence_note": "Primary papers and official repositories were opened for the scientific and asset claims below. A searchable page is not treated as proof of a load-bearing cohort fact. No novelty claim is made: novelty_confidence describes only how crowded the immediate neighborhood appears after a bounded search.",
  "generation_checklist": {
    "prior_kill_codes": {
      "DATA_INSUFFICIENT": "Checked whether the subset needed for the inference, rather than merely the parent collection, is plausibly reachable; unresolved joins are keystones, not hidden assumptions.",
      "CIRCULARITY": "No candidate predicts a machine measurement from a target that is simply the same measurement re-encoded. C4 deliberately uses an RV-strain output and a different hemodynamic sign (IVC reflux)."
    },
    "annotation_provenance": "No X depends on a human annotation. Pain, cancer, CKD, and PE labels trained the frozen models but do not define X or enter the primary model-use readout.",
    "use_vs_association": "Every candidate distinguishes use from correlation with an explicit model intervention (concept-direction erasure with matched random/nuisance directions), a within-person contrast, or both. Observational score-versus-X association alone is labeled exploratory and never earns rung 1.",
    "portfolio_revivals": "Zero. None of the portfolio brief's blocking conditions has a newly verified fact that changes it. Re-proposing those ideas would violate the revival rule."
  },
  "all_questions": [
    {
      "n": 1,
      "question": "Is the knee-pain model of Pierson et al. using medial tibial subchondral trabecular texture that Kellgren-Lawrence grading discards?",
      "status": "DEVELOPED as C1"
    },
    {
      "n": 2,
      "question": "Is Mirai using breast arterial calcification as a vascular-age signal when it predicts five-year breast cancer risk?",
      "status": "DEVELOPED as C2"
    },
    {
      "n": 3,
      "question": "Is Merlin using renal sinus fat when its abdominal-CT representation predicts chronic kidney disease?",
      "status": "DEVELOPED as C3"
    },
    {
      "n": 4,
      "question": "Is a pulmonary-embolism CT model using contrast reflux into the inferior vena cava as a hydraulic back-pressure signal for right-heart strain?",
      "status": "DEVELOPED as C4"
    },
    {
      "n": 5,
      "question": "Is Sybil using saber-sheath tracheal shape as a mechanically accumulated record of chronic obstructive lung disease?",
      "status": "DEVELOPED as C5"
    },
    {
      "n": 6,
      "question": "Is a head-CT mortality model using temporalis muscle thickness as a measure of frailty?",
      "status": "DROPPED",
      "why": "The X is clean and radiologist-legible, but the available model/checkpoint and an open held-out outcome cohort were not identified; this would become a data scavenger hunt before it became a mechanism study."
    },
    {
      "n": 7,
      "question": "Is a chest-CT age model using aortic unfolding, measured as arch width and descending-aorta displacement?",
      "status": "DROPPED",
      "why": "No suitable frozen age model was verified, and aortic unfolding is so directly age-associated that an observational result would add little without a credible use intervention."
    },
    {
      "n": 8,
      "question": "Is a brain-MRI dementia model using ventricular surface-area-to-volume ratio as a geometric signature of periventricular tissue loss?",
      "status": "DROPPED",
      "why": "Interesting differential-geometry bridge, but FreeSurfer-derived ventricular geometry is likely dominated by segmentation and sequence variation; the artifact is not yet separable from the proposed biology."
    },
    {
      "n": 9,
      "question": "Is a lung-cancer CT model using the left-right asymmetry of diaphragmatic height as a sign of phrenic dysfunction?",
      "status": "DROPPED",
      "why": "This is the deliberately obviously-wrong question. It is computable, but positioning, breath hold, scoliosis, abdominal organ displacement, and scan framing provide too many equally plausible explanations for a positive result."
    },
    {
      "n": 10,
      "question": "Is an abdominal-CT mortality model using psoas radiodensity rather than psoas area as the image signature of muscle quality?",
      "status": "DROPPED",
      "why": "Radiodensity is a strong named candidate, but this exact opportunistic-CT sarcopenia question is already crowded and no precise model-specific unfinished story was found in the bounded search."
    }
  ],
  "quota_compliance": {
    "mode_A": ["C1"],
    "mode_B": ["C2", "C3"],
    "mode_C": ["C4", "C5"],
    "entry_point_1": ["C1"],
    "entry_point_2": ["C2", "C3", "C4", "C5"],
    "radiology_or_CT": "5/5",
    "CT_or_3D": "3/5 (C3-C5)",
    "dermatology": "0/5",
    "dataset_concentration": "OAI x1; EMBED/prospective mammography collection x1; Merlin-compatible abdominal CT x1; RSNA-STR PE x1; NLST x1.",
    "quota_note": "Met exactly. Mode C candidates are hard but name a specific measurable physical quantity and an intervention; neither is padded with a free-floating analogy."
  },
  "candidates": [
    {
      "id": "C1",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "A",
      "entry_point": 1,
      "title": "The knee-pain model may be reading trabecular stress architecture that KL grade throws away",
      "question": "Is the knee-pain model of Pierson et al. using directional medial tibial subchondral trabecular texture, rather than only joint-space narrowing and osteophytes, to recover pain that radiographic Kellgren-Lawrence grading misses?",
      "rung": {
        "target": 3,
        "current": 0,
        "move_up": "A validated texture measurement and score association are exploratory; a selective loss of pain prediction after erasing the texture direction, with matched nuisance-direction controls and bilateral/longitudinal replication, reaches rung 1. Acquisition harmonization and site-held-out replication gate rung 2; the named texture then supplies rung 3."
      },
      "deliverable_sentence": "The knee-pain model is using medial tibial subchondral trabecular texture—directional thickening and rarefaction of the load-bearing bone beneath the cartilage.",
      "X_measurement": {
        "X": "Directional fractal signature of medial tibial subchondral trabecular bone, summarized across horizontal and vertical scales in a landmark-defined ROI.",
        "how": "Locate tibial plateau landmarks with a released knee landmark model or deterministic geometry, place the published subchondral ROI, and compute variance-orientation-transform fractal signatures. Janvier et al. used this measurement on OAI radiographs (DOI 10.1016/j.joca.2017.09.004; PMID 28935435); the OARSI/FNIH consortium used validated semiautomated software (PMID 29024470).",
        "could_compute_today_without_asking_anyone": "Yes in principle: the formula is defined and requires pixels plus geometric landmarks, not a radiologist. The exact validated implementation and landmark model still need to be obtained or reproduced before a confirmatory run."
      },
      "suspected_signal": "Subchondral bone remodels along habitual load paths. Horizontal trabecular thickening and direction-dependent rarefaction alter radiographic texture at scales not represented by the coarse KL vocabulary and may track painful bone stress or marrow pathology.",
      "keystone_prerequisite": "The frozen Pierson pain model or exactly reproducible checkpoint can be run on OAI images that also support stable, automated directional fractal-signature measurement, and the measured texture has enough within-KL and within-person variation to identify a selective model-use effect.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest facts inspected: Pierson et al., Nature Medicine 2021, DOI 10.1038/s41591-020-01192-7, states that OAI images/clinical data reproduce the analysis; Janvier et al., DOI 10.1016/j.joca.2017.09.004, measured subchondral texture in OAI. The actual checkpoint-to-image pipeline and joint distribution were not inspected.",
      "keystone_residual_assumption": "The easy facts are that the pain model and texture literature both use OAI. I am still assuming the exact frozen model is runnable and that texture varies independently of joint-space width, osteophytes, alignment, and acquisition processing. That independence is load-bearing and is therefore included in the keystone.",
      "rung_reached": "No rung yet. Conditional rung 1 after selective internal concept erasure; rung 2 after site/acquisition and alignment controls; rung 3 only then.",
      "dies_like_prior": "It resembles idea-001 in using OAI clinical labels, but pain-label provenance is not the concept measurement and the primary readout is a frozen model's score change after an image-computable texture-direction intervention. It avoids DATA_INSUFFICIENT by gating on the actual model/OAI join and avoids CIRCULARITY because X is not the pain label or KL grade.",
      "closest_prior_work": [
        {
          "citation": "Pierson et al., Nature Medicine 2021",
          "identifier": "DOI 10.1038/s41591-020-01192-7",
          "verified_fact": "A deep model predicted knee pain from OAI radiographs and explained pain variation beyond radiologist-assigned severity.",
          "delta": "The paper did not name or measure directional subchondral trabecular texture as the model-used signal."
        },
        {
          "citation": "Janvier et al., Osteoarthritis and Cartilage 2017",
          "identifier": "DOI 10.1016/j.joca.2017.09.004; PMID 28935435",
          "verified_fact": "Directional trabecular texture on OAI radiographs predicted incident radiographic OA.",
          "delta": "It studied OA incidence, not what a pain-prediction network uses."
        }
      ],
      "existing_assets": ["OAI bilateral longitudinal knee radiographs and WOMAC pain data (registration-controlled access, not an unconfirmed DUA-gated dependency for the card)", "Published pain-model architecture/reproduction materials", "Published fractal-signature formula and OAI texture precedents"],
      "smallest_decisive_experiment": "Stage 0: verify checkpoint inference and texture repeatability, then quantify within-KL texture variation. Exploratory: fit a validation-only probe from frozen embeddings to X. Confirmatory: freeze that direction, erase only it from test embeddings, and compare the change in knee-specific pain score with equal-norm random directions, KL/joint-space directions, and left-right within-person contrasts. The model uses X only if texture erasure selectively harms prediction and the effect scales with measured X.",
      "use_vs_association": "A score-X regression is exploratory. The use claim requires selective frozen-representation erasure of the validation-learned X direction, with matched-direction controls, and must replicate within bilateral or longitudinal comparisons.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "Site-held-out evaluation and acquisition/processing strata; not fully ruled out until Stage 0 confirms metadata.",
        "positioning": "Alignment and flexion landmarks are explicit nuisance concepts and matched erasure controls.",
        "habitus": "Bilateral within-person contrasts hold BMI/habitus fixed; residual side-specific loading remains.",
        "prevalence_referral": "Single prospective OAI cohort limits spectrum; not ruled out externally.",
        "label_leakage": "Pain is self-report, not available in pixels or radiology annotations; laterality/joint identifiers must be stripped."
      },
      "alternative_explanations": [
        {"alternative": "Texture is a proxy for malalignment or joint-space narrowing.", "resolution": "Measure both, learn nuisance directions, and require texture erasure to add harm beyond them."},
        {"alternative": "Computed-radiography post-processing creates texture differences.", "resolution": "Site/acquisition strata and bilateral same-image contrasts address much, but external device replication remains necessary."},
        {"alternative": "Erasure removes generic image information rather than X.", "resolution": "Equal-norm random, landmark, and KL-direction erasures plus retained reconstruction performance test selectivity."}
      ],
      "anticipated_negative": {
        "classification": "sensitivity-limited",
        "reason": "A null erasure effect could mean the representation distributes texture nonlinearly. It becomes decisive only after a prespecified probe-reliability floor and minimum score-change equivalence margin are met."
      },
      "cross_domain": {
        "borrowed_construct": "Load-path adaptation from bone mechanobiology.",
        "measurement_implied": "Directional, scale-dependent trabecular fractal signature rather than generic image texture.",
        "if_analogy_dropped": "The experiment would otherwise test undirected texture. The analogy changes the preregistered X to horizontal-versus-vertical signatures and predicts the sign/scales of the effect."
      },
      "remaining_legwork": "2 days to inspect checkpoint/reproduction assets; 3-5 days for an OAI access and join audit; 1 week for texture repeatability and collinearity Stage 0. First scientific decision in about 2 weeks if access is active.",
      "scores": {
        "clarity": {"value": 5, "why": "One model, one named bone compartment, one defined texture measurement."},
        "identifiability": {"value": 3, "why": "Internal erasure and bilateral controls improve on association, but texture is entangled with alignment and erasure may not be specific."},
        "medical_relevance": {"value": 4, "why": "It could name the missing radiographic substrate behind clinically important pain discordance."},
        "interest": {"value": 5, "why": "It attempts to decode a documented model-human gap with a bone quantity clinicians can recognize."},
        "prior_legwork": {"value": 4, "why": "Both the gap and the exact measurement have OAI precedents."},
        "feasibility": {"value": 3, "why": "Capped: keystone not inspected; access and checkpoint reproducibility remain."},
        "data_readiness": {"value": 3, "why": "OAI is established but registration-controlled."},
        "evaluation_readiness": {"value": 3, "why": "Fractal metrics exist; selective-erasure calibration needs custom controls."},
        "negative_result_value": {"value": 2, "why": "The anticipated null is sensitivity-limited."},
        "novelty_confidence": {"value": 3, "why": "Capped and no exhaustive review; the precise model-to-texture link was not located."},
        "regret": {"value": 5, "why": "Two mature OAI literatures sit one model-use experiment apart."}
      },
      "priority_score": 3.65,
      "priority_arithmetic": "0.20*3 + 0.15*3 + 0.15*4 + 0.10*4 + 0.10*5 + 0.10*5 + 0.10*2 + 0.05*3 + 0.05*3 = 3.65",
      "unverified_claims": ["A runnable Pierson checkpoint is currently available", "Texture varies sufficiently within KL grade and acquisition strata", "The validation-learned concept direction is selectively erasable"]
    },
    {
      "id": "C2",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "B",
      "entry_point": 2,
      "title": "A breast-cancer risk model may be reading the arteries as a vascular clock",
      "question": "Is Mirai using breast arterial calcification as a vascular-age signal in its five-year breast-cancer risk prediction, independently of breast density and chronological age?",
      "rung": {"target": 3, "current": 0, "move_up": "Automated BAC association is exploratory; validation-learned BAC-direction erasure with age/density/device controls reaches rung 1; external-device replication gates rung 2 and the named BAC claim at rung 3."},
      "deliverable_sentence": "Mirai is using breast arterial calcification—the linear tram-track calcium in mammary arteries—as a vascular-age signal in breast-cancer risk prediction.",
      "X_measurement": {
        "X": "Total breast arterial calcification length or segmented pixel area across the four standard mammographic views.",
        "how": "Use an existing BAC segmentation network or a deterministic vessel-like high-intensity segmentation calibrated on a validation subset. Mobini et al. report automated BAC detection/quantification (primary paper summarized in the open review; direct model artifact still to inspect).",
        "could_compute_today_without_asking_anyone": "Not yet established for the chosen cohort. The quantity is computable without a human, but availability and transfer of an executable BAC segmenter is the keystone gate."
      },
      "suspected_signal": "Medial arterial calcification produces high-contrast, paired linear densities. It rises strongly with age and metabolic/vascular disease, so a risk model may exploit it as an image-derived systemic ageing marker even though it is not breast parenchymal biology.",
      "specific_artifact_confused_with_signal": "Detector/vendor processing and vascular-like skin folds can produce high-intensity linear structures; chronological age and breast density are biological confounds, not acquisition artifacts.",
      "keystone_prerequisite": "An executable, validated, annotation-free BAC quantifier transfers to the same four-view mammograms on which frozen Mirai can run, with enough BAC-positive cases and age/density overlap to separate BAC use from age, density, and device.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest inspected artifact: official MIT Mirai repository https://github.com/reginabarzilaygroup/Mirai states that trained model and code are MIT-licensed, gives the four-view inference command, and lists supported Hologic acquisition. BAC automation is supported by Mobini et al., Diagnostics 2024, PMCID PMC11247067, but an executable compatible quantifier and joint cohort were not inspected.",
      "keystone_residual_assumption": "Verifying that Mirai runs and BAC can be detected in someone else's cohort does not verify the join. I am still assuming a BAC tool transfers to Mirai-compatible presentation images and that BAC is not nearly deterministic from age in the usable sample. That is the real keystone.",
      "rung_reached": "No rung yet; conditional rung 1 after selective erasure, rung 2 after device/site and age-density controls, rung 3 thereafter.",
      "dies_like_prior": "It resembles idea-002 only in crossing concepts and a second image task; unlike Derm7pt, BAC is computed from the same mammogram and no undocumented annotator viewing condition is needed. It avoids CIRCULARITY because BAC is not Mirai's cancer-risk target.",
      "closest_prior_work": [
        {"citation": "Yala et al., Towards Robust Mammography-Based Models for Breast Cancer Risk", "identifier": "official code https://github.com/reginabarzilaygroup/Mirai; primary model paper linked there", "verified_fact": "Mirai predicts annual risk to five years and releases inference code/weights under MIT.", "delta": "The repository/paper does not establish whether BAC drives risk."},
        {"citation": "Mobini et al., Deep transfer learning for detection of breast arterial calcifications", "identifier": "PMCID PMC11247067", "verified_fact": "BAC is machine-detectable on four-view mammograms.", "delta": "It detects BAC; it does not test Mirai or breast-cancer risk-model reliance."},
        {"citation": "Revealing Mammographic Phenotypes in Deep Learning Breast Cancer Risk Models", "identifier": "arXiv:2606.26431", "verified_fact": "A 2026 preprint clusters Mirai patch embeddings into risk-linked phenotypes.", "delta": "This is the closest warning against novelty: the exact phenotype inventory must be inspected for BAC before advancement."}
      ],
      "existing_assets": ["Mirai code and weights (MIT)", "Four-view public mammography resources such as EMBED, subject to their actual access terms", "Published BAC segmentation methods"],
      "smallest_decisive_experiment": "Stage 0: inspect the 2026 phenotype paper for BAC, run Mirai and the BAC quantifier on 200 age/device-stratified exams, and verify BAC repeatability across views. Confirmatory: learn a BAC direction on validation embeddings, erase it on a locked test set, and compare five-year risk change against age-, density-, and device-direction erasures plus equal-norm random controls; exploit unilateral BAC burden as a within-woman check of view contributions.",
      "use_vs_association": "BAC-risk correlation is not enough. The claim requires selective loss or calibrated change of Mirai risk after frozen-representation BAC-direction erasure, beyond age, density, and device directions.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "Device direction and site-held-out analysis; Mirai's official repository warns its original devices were Hologic, so transfer is a gate.",
        "positioning": "Four standard views required; view-level BAC repeatability check.",
        "habitus": "Breast thickness/compression and density measured as nuisance concepts.",
        "prevalence_referral": "Screening-only cohorts; external screening site required.",
        "label_leakage": "Future cancer label is not visually printed; prior biopsy markers/CAD overlays must be excluded."
      },
      "alternative_explanations": [
        {"alternative": "BAC merely indexes chronological age.", "resolution": "Age-matched strata and separate age-direction erasure; require BAC-specific incremental effect."},
        {"alternative": "BAC pixels resemble suspicious calcifications.", "resolution": "Spatial BAC mask, morphology separation, and comparison with parenchymal-calcification direction."},
        {"alternative": "Vendor processing creates both BAC visibility and risk shifts.", "resolution": "Within-device analysis and external device replication; unresolved without both."}
      ],
      "anticipated_negative": {"classification": "sensitivity-limited", "reason": "BAC may be sparse and nonlinear in embeddings; a null is decisive only above preregistered BAC-probe AUROC/reliability and prevalence gates."},
      "cross_domain": null,
      "remaining_legwork": "1 day to inspect the 2026 phenotype preprint; 3 days to locate/test an executable BAC quantifier; up to 1 week for compatible mammography access. First go/no-go in 1-2 weeks.",
      "scores": {
        "clarity": {"value": 5, "why": "Specific model, visible quantity, and rival age/density explanations."},
        "identifiability": {"value": 3, "why": "Concept erasure plus age/device controls is plausible, but BAC-age entanglement and internal-intervention specificity remain."},
        "medical_relevance": {"value": 4, "why": "Changes interpretation of a widely evaluated risk score and may expose systemic rather than breast-specific signal."},
        "interest": {"value": 5, "why": "A breast model reading vascular disease is surprising and physician-legible."},
        "prior_legwork": {"value": 4, "why": "Open Mirai and mature BAC detection work exist."},
        "feasibility": {"value": 3, "why": "Capped; BAC tool/corpus join is uninspected."},
        "data_readiness": {"value": 3, "why": "Potential public resources exist but exact access and presentation-view compatibility need inspection."},
        "evaluation_readiness": {"value": 3, "why": "BAC metrics exist; erasure selectivity must be calibrated."},
        "negative_result_value": {"value": 2, "why": "Sensitivity-limited null."},
        "novelty_confidence": {"value": 2, "why": "A very recent Mirai phenotype preprint may already touch the signal and has not yet been fully inspected."},
        "regret": {"value": 4, "why": "Cheap once the BAC quantifier and compatible images are joined."}
      },
      "priority_score": 3.60,
      "priority_arithmetic": "0.20*3 + 0.15*3 + 0.15*4 + 0.10*4 + 0.10*5 + 0.10*5 + 0.10*2 + 0.05*3 + 0.05*2 = 3.60",
      "unverified_claims": ["An open BAC segmenter with weights transfers to Mirai inputs", "EMBED or another obtainable set has adequate BAC prevalence and outcomes", "arXiv:2606.26431 does not already test BAC"]
    },
    {
      "id": "C3",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "B",
      "entry_point": 2,
      "title": "Merlin may be reading fatty kidney rather than kidney shape",
      "question": "Is Merlin using renal sinus fat volume, independently of total visceral adipose tissue and kidney volume, when it scores chronic kidney disease on abdominal CT?",
      "rung": {"target": 3, "current": 0, "move_up": "A voxel measurement plus score association is exploratory. Selective concept erasure conditional on visceral fat and kidney volume reaches rung 1; protocol/site replication gates rung 2; renal sinus fat is already a named rung-3 quantity."},
      "deliverable_sentence": "Merlin is using renal sinus fat—the ectopic fat packed around the renal vessels—as an image marker of chronic kidney disease.",
      "X_measurement": {
        "X": "Renal sinus adipose-tissue volume in cubic centimeters, and renal-sinus-fat/total-visceral-fat ratio.",
        "how": "Segment both kidneys, define the renal sinus from the medial hilar concavity/renal parenchymal hull, and count voxels in a prespecified adipose HU interval (for example -195 to -45 HU), following Foster et al.'s CT measurement framework (DOI 10.1186/1471-2369-12-52).",
        "could_compute_today_without_asking_anyone": "Yes as a well-defined CT measurement once a kidney segmentation is available; no human rating is required. Automated sinus-boundary validity still needs Stage 0."
      },
      "suspected_signal": "Ectopic fat accumulates in the confined renal sinus around vessels, lymphatics, and the collecting system. It may reflect systemic metabolic disease and may mechanically compress low-pressure renal structures, so it is separable in principle from overall obesity and kidney size.",
      "specific_artifact_confused_with_signal": "Contrast phase changes renal parenchymal boundaries and HU; slice thickness and field-of-view truncation change partial volume and visceral-fat measurement.",
      "keystone_prerequisite": "A frozen Merlin CKD phenotype score is available on an obtainable, noncontrast or phase-harmonized abdominal-CT cohort in which automated renal sinus fat is valid and varies independently enough from total visceral fat for a selective-use test.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest primary evidence inspected: Merlin, arXiv:2406.06512, reports 692 phenotype classification tasks; Foster et al., DOI 10.1186/1471-2369-12-52, developed a reproducible CT renal-sinus-fat measurement; Foster et al., DOI 10.1161/HYPERTENSIONAHA.111.175315, quantified it in 2,923 Framingham participants and studied CKD/hypertension. The actual Merlin phenotype string/checkpoint output and compatible cohort were not directly inspected.",
      "keystone_residual_assumption": "The adjacent facts are that Merlin has many phenotypes and renal sinus fat is measurable. I am still assuming CKD is an exposed frozen output and that a usable cohort has a controlled contrast phase plus enough renal-sinus-fat variation beyond visceral fat. Those are load-bearing and remain unverified.",
      "rung_reached": "No rung yet; conditional progression 1 -> 2 -> 3 as above.",
      "dies_like_prior": "It resembles scout-006-c03 (Merlin diabetes/liver fat) in model and mediation structure, but asks a new organ/output/measurement question. It does not cure that design's use-versus-association problem by renaming the biomarker: the use claim is explicitly conditional on concept erasure. No prior annotation-provenance failure applies because X is HU-defined fat volume.",
      "closest_prior_work": [
        {"citation": "Blankemeier et al., Merlin", "identifier": "arXiv:2406.06512", "verified_fact": "Merlin is a 3D abdominal CT vision-language foundation model evaluated on hundreds of EHR phenotypes.", "delta": "The paper did not report renal sinus fat as the signal behind CKD."},
        {"citation": "Foster et al., Development and reproducibility of a CT-based measurement of renal sinus fat", "identifier": "DOI 10.1186/1471-2369-12-52; PMCID PMC3198884", "verified_fact": "It defines and evaluates a CT renal-sinus-fat measurement.", "delta": "No image foundation model was studied."},
        {"citation": "Foster et al., Fatty kidney, hypertension, and CKD", "identifier": "DOI 10.1161/HYPERTENSIONAHA.111.175315; PMID 21931075", "verified_fact": "Renal sinus fat was quantified in 2,923 participants and associated with renal/metabolic traits.", "delta": "Association with CKD is prior biology, not evidence Merlin uses it."}
      ],
      "existing_assets": ["Merlin paper and reportedly released model assets", "Kidney segmentation in common whole-body CT segmenters", "Published HU-based renal sinus fat methods"],
      "smallest_decisive_experiment": "Stage 0: inspect Merlin output vocabulary/checkpoint; validate automatic sinus-fat measurement against repeat scans or a small public reference, not new reader labels; quantify phase and collinearity with visceral fat. Confirmatory: validation-learned sinus-fat direction erasure in frozen embeddings, with kidney-volume, total-visceral-fat, liver-fat, age/sex (if available), and equal-norm random direction controls; test effect on CKD score only after freezing all choices.",
      "use_vs_association": "The observational score relation establishes only correlation. Selective internal erasure of the renal-sinus-fat direction, after orthogonalizing it to total visceral fat and kidney volume on validation data, is the proposed model-use test.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "Phase/kernel/site strata; external site replication required. Contrast phase is the dominant gate.",
        "positioning": "Minor after anatomical segmentation; truncation is excluded.",
        "habitus": "Total visceral and subcutaneous fat are measured controls, not merely BMI proxies.",
        "prevalence_referral": "Clinical abdominal CT referral remains a limitation and needs a second cohort.",
        "label_leakage": "Primary readout uses model score and voxels only; reports are not used."
      },
      "alternative_explanations": [
        {"alternative": "The model uses total obesity, not renal sinus fat.", "resolution": "Residualize X against total visceral/subcutaneous fat and compare selective erasures."},
        {"alternative": "The model uses atrophic or cystic kidney morphology.", "resolution": "Control kidney volume, cortical thickness, cyst burden, and hydronephrosis directions."},
        {"alternative": "Contrast phase creates apparent fat-boundary differences.", "resolution": "Use noncontrast scans or one tightly harmonized phase; otherwise the candidate fails Stage 0."}
      ],
      "anticipated_negative": {"classification": "sensitivity-limited", "reason": "A null after an unreliable sinus segmentation or weak concept probe says little; equivalence is interpreted only if repeatability and probe floors pass."},
      "cross_domain": null,
      "remaining_legwork": "1 day for Merlin vocabulary/checkpoint inspection, 3-5 days for a compatible cohort audit, and 1 week for automated sinus measurement validation. First go/no-go in about 2 weeks.",
      "scores": {
        "clarity": {"value": 5, "why": "Named model output, ectopic fat depot, and explicit obesity rival."},
        "identifiability": {"value": 3, "why": "Residualized erasure can separate local from total fat, but internal specificity and clinical referral remain."},
        "medical_relevance": {"value": 4, "why": "Could show that a CKD score reads a recognized opportunistic metabolic/renal biomarker."},
        "interest": {"value": 4, "why": "Fat around the renal hilum is a plausible but non-obvious cue."},
        "prior_legwork": {"value": 4, "why": "Model family, segmentation, and epidemiologic measurement all exist."},
        "feasibility": {"value": 3, "why": "Capped; CKD output and cohort join not inspected."},
        "data_readiness": {"value": 2, "why": "A compatible obtainable cohort has not been named and verified."},
        "evaluation_readiness": {"value": 3, "why": "Volume and partial regression are standard; sinus automation is custom."},
        "negative_result_value": {"value": 2, "why": "Sensitivity-limited."},
        "novelty_confidence": {"value": 3, "why": "Capped; no direct Merlin/renal-sinus-fat study found in a bounded search."},
        "regret": {"value": 4, "why": "Worth a fast vocabulary/data audit before more Merlin liver/bone work."
        }
      },
      "priority_score": 3.40,
      "priority_arithmetic": "0.20*3 + 0.15*3 + 0.15*4 + 0.10*4 + 0.10*4 + 0.10*5 + 0.10*2 + 0.05*2 + 0.05*3 = 3.40",
      "unverified_claims": ["Merlin exposes a usable CKD score", "Compatible CT and checkpoint are obtainable without unconfirmed DUA-gated data", "Automated sinus fat has adequate repeatability"]
    },
    {
      "id": "C4",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "C",
      "entry_point": 2,
      "title": "The PE model may read contrast flowing backward as a pressure gauge",
      "question": "Is a pulmonary-embolism CTPA model using contrast reflux into the inferior vena cava and hepatic veins as a hydraulic back-pressure signal when it predicts right-heart strain?",
      "rung": {"target": 3, "current": 0, "move_up": "A controlled reflux-direction erasure with bolus-timing and RV/LV controls reaches rung 1; cross-site/protocol replication gates rung 2; IVC/hepatic-vein reflux is already named at rung 3."},
      "deliverable_sentence": "The pulmonary-embolism model is using contrast reflux into the inferior vena cava and hepatic veins as a sign of elevated right-sided pressure.",
      "X_measurement": {
        "X": "IVC/hepatic-vein contrast reflux burden: contrast-enhanced volume or cranio-caudal extent below the right atrium, normalized by right-atrial or aortic blood-pool attenuation.",
        "how": "Segment right atrium, IVC, and hepatic veins on CTPA; threshold contrast relative to the right atrium and integrate enhanced venous volume/extent. This is a physical attenuation-and-geometry measurement rather than a reader grade.",
        "could_compute_today_without_asking_anyone": "Yes in definition, but an existing validated open segmentation stack covering hepatic veins on RSNA-STR CTPA was not inspected; feasibility is therefore capped."
      },
      "suspected_signal": "During contrast injection, elevated right-sided pressure and tricuspid regurgitant flow can drive contrast caudally into the IVC and hepatic veins. The visible reflux column is a transient fluid-dynamic readout of right-heart loading, distinct from ventricular enlargement.",
      "specific_artifact_confused_with_signal": "Injection rate, scan delay, saline chaser, cardiac output, and respiratory phase can produce reflux-like enhancement independent of pathologic pressure.",
      "keystone_prerequisite": "RSNA-STR CTPAs retain enough IVC/hepatic-vein coverage and bolus heterogeneity can be controlled well enough that automated reflux burden varies independently from RV/LV ratio and global contrast timing, while a frozen right-heart-strain model/checkpoint remains runnable.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest inspected primary artifact: Colak et al., The RSNA Pulmonary Embolism CT Dataset, Radiology: AI 2021, DOI 10.1148/ryai.2021200254, PMCID PMC8043364, confirms study-level RV/LV >=1 labels and QA-contrast labels. It does not prove adequate hepatic-vein coverage, injection metadata, or a particular frozen checkpoint.",
      "keystone_residual_assumption": "The easy fact is that the dataset labels right-heart strain. I am still assuming the voxels needed to measure reflux are consistently in frame and that bolus timing is recoverable or inferable independently. That, not label availability, is the keystone.",
      "rung_reached": "No rung yet; Mode C tolerates the uninspected gate but not a model-use claim before it passes.",
      "dies_like_prior": "It resembles idea-006 in proposing a model intervention, but does not delete the patient or create a constant-filled OOD image; it intervenes internally on a measured concept direction. It avoids CIRCULARITY because reflux is not RV/LV ratio, although both reflect the same hemodynamic state and must be dissociated.",
      "closest_prior_work": [
        {"citation": "Colak et al., RSNA Pulmonary Embolism CT Dataset", "identifier": "DOI 10.1148/ryai.2021200254; PMCID PMC8043364", "verified_fact": "The public CTPA dataset includes RV/LV and contrast-quality labels.", "delta": "It did not quantify IVC reflux or decode what an RV/LV classifier uses."},
        {"citation": "Prognostic Value of CT-Derived Indicators of Right-Heart Strain and Thrombus Burden", "identifier": "PMCID PMC12840362", "verified_fact": "IVC contrast reflux and RV/LV ratio were evaluated as separate CT indicators in acute PE.", "delta": "It is an outcome association study, not a model-use study."}
      ],
      "existing_assets": ["RSNA-STR CTPA dataset and labels", "Published PE multitask architectures, including DOI-linked open papers", "Generic cardiac/vascular CT segmentation models"],
      "smallest_decisive_experiment": "Stage 0: inspect 100 stratified scans for IVC/hepatic coverage, injection metadata, and automated reflux repeatability; quantify reflux-RV/LV-bolus collinearity. Then learn reflux, RV/LV, clot-burden, and contrast-timing directions on validation embeddings. On locked test embeddings erase each direction separately and jointly. The claim requires selective reduction of the model's RV-strain score after reflux erasure beyond RV/LV and timing directions, with no comparable effect on PE-location outputs.",
      "use_vs_association": "The model uses reflux only if selective reflux-direction erasure changes the frozen RV-strain output after RV/LV, clot, and bolus-timing directions are controlled; marginal correlation is explicitly insufficient.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "Site/vendor/protocol splits where metadata exist; injection protocol is the dominant unresolved confound.",
        "positioning": "Less important than inspiration and coverage; both measured.",
        "habitus": "May change bolus and noise; body diameter/SNR control.",
        "prevalence_referral": "All are clinically referred CTPA; PE prevalence strata do not remove referral bias.",
        "label_leakage": "RV/LV labels came from image reads but X is computed from voxels and primary readout is model self-change."
      },
      "alternative_explanations": [
        {"alternative": "Reflux is only a bolus-timing/injection artifact.", "resolution": "Normalize to blood pool, learn timing direction, stratify QA-contrast and protocol; absent metadata may remain fatal."},
        {"alternative": "The model uses visible RV dilation, with reflux merely correlated.", "resolution": "Separate and joint RV/LV versus reflux erasures."},
        {"alternative": "Erasure removes global contrast information.", "resolution": "Test PE localisation and contrast-QA outputs plus equal-norm global-contrast direction controls."}
      ],
      "anticipated_negative": {"classification": "decisive", "reason": "If reflux is reliably encoded yet its selective erasure has an equivalently near-zero effect while RV/LV erasure changes the score, the hydraulic-reflux mechanism is weakened directly."},
      "cross_domain": {
        "borrowed_construct": "Hydraulic back-pressure and transient tracer transport.",
        "measurement_implied": "Normalized retrograde contrast volume/extent, not a binary reflux label.",
        "if_analogy_dropped": "The experiment would likely collapse reflux to presence/absence. The fluid-mechanics account requires normalization to input bolus and predicts a dose-like relationship with retrograde extent."
      },
      "remaining_legwork": "2 days for coverage/metadata inspection, 3-5 days to validate segmentation and timing normalization, and 1 week to identify/reproduce a checkpoint. First kill/continue decision in one week.",
      "scores": {
        "mechanism_clarity": {"value": 5, "why": "A named retrograde contrast volume with an explicit pressure/transport mechanism and normalization."},
        "identifiability": {"value": 3, "why": "Separate erasures address RV dilation, but injection timing may remain inseparable."},
        "interest": {"value": 5, "why": "The model could be reading a fleeting fluid-dynamic sign rather than anatomy."},
        "medical_relevance": {"value": 4, "why": "Right-heart strain changes PE triage and prognosis."},
        "clarity": {"value": 5, "why": "Specific output, vessel compartment, and physical mechanism."},
        "feasibility": {"value": 2, "why": "Coverage, segmentation, metadata, and checkpoint are uninspected."},
        "novelty_confidence": {"value": 3, "why": "Capped; no direct model-use study found, but reflux prognostic studies are established."},
        "prior_legwork": {"value": 3, "why": "Public data and labels exist, but the decisive measurement pipeline does not yet."},
        "data_readiness": {"value": 3, "why": "RSNA data are public; required coverage remains unknown."},
        "evaluation_readiness": {"value": 3, "why": "The erasure comparison is clear; reflux normalization needs validation."},
        "negative_result_value": {"value": 5, "why": "With reliability gates met, RV/LV-positive/reflux-null erasure is a decisive mechanistic negative."},
        "regret": {"value": 4, "why": "A small coverage audit quickly determines whether a striking mechanism is real work or fantasy."}
      },
      "mode_c_priority_score": 4.35,
      "priority_arithmetic": "0.30*5 + 0.25*3 + 0.20*5 + 0.15*4 + 0.10*5 = 4.35",
      "unverified_claims": ["Hepatic veins are consistently covered", "Injection metadata or a valid timing proxy exists", "A frozen reproducible RV-strain checkpoint is available"]
    },
    {
      "id": "C5",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "C",
      "entry_point": 2,
      "title": "A lung-cancer model may be reading a mechanically remodeled trachea",
      "question": "Is Sybil using the minimum intrathoracic tracheal index—the transverse-to-anteroposterior ratio that defines saber-sheath trachea—as a mechanically accumulated sign of COPD and smoking injury?",
      "rung": {"target": 3, "current": 0, "move_up": "Selective tracheal-index erasure and paired inspiration/reconstruction stability reach rung 1; separation from emphysema, sex, lung volume, and kernel plus external replication gates rung 2; saber-sheath trachea is the rung-3 name."},
      "deliverable_sentence": "Sybil is using saber-sheath tracheal deformity—the fixed side-to-side narrowing of the intrathoracic trachea—as a record of chronic obstructive lung injury.",
      "X_measurement": {
        "X": "Minimum intrathoracic tracheal index: transverse lumen diameter divided by anteroposterior diameter on planes perpendicular to the tracheal centerline, with <0.67 as a conventional severe-deformity threshold.",
        "how": "Automatically segment the tracheal lumen by HU threshold/region growing, extract a centerline, reformat perpendicular planes from the lung apex to 2 cm above the carina, and take the minimum transverse/AP ratio. Pompe et al. describe this automatic procedure (PMCID PMC6052793).",
        "could_compute_today_without_asking_anyone": "Yes. The published algorithm uses voxel thresholding, centerline geometry, and a formula; it needs no human judgment."
      },
      "suspected_signal": "Repeated cough and elevated intrathoracic pressure cause chronic tracheal-cartilage remodeling: coronal narrowing with sagittal widening. Unlike instantaneous lung inflation, the shape may integrate years of obstructive mechanics and smoking injury.",
      "specific_artifact_confused_with_signal": "Respiratory phase, gantry angle, non-perpendicular axial measurement, tracheal secretions, intubation, and crop/resampling anisotropy can all change apparent index.",
      "keystone_prerequisite": "Sybil's final input tensor preserves tracheal cross-sectional geometry accurately enough for minimum tracheal index to be measured and encoded, and NLST contains enough low-index cases independent of sex, emphysema, lung volume, and reconstruction for a selective-use test.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest primary evidence inspected: Pompe et al., PMCID PMC6052793, specifies an automatic centerline/perpendicular-plane tracheal-index algorithm and reports that tracheal shape adds to emphysema for COPD severity assessment. Sybil/NLST availability is established in the ledger, but preservation of tracheal geometry through the final tensor and the NLST joint distribution were not inspected.",
      "keystone_residual_assumption": "The easy facts are that native CT supports tracheal index and Sybil accepts NLST CT. I am still assuming resampling/cropping preserves this ratio and that saber-sheath variation is not effectively a male-sex/emphysema indicator. Those are the real load-bearing facts.",
      "rung_reached": "No rung yet. Mode C score reflects mechanism quality, not accomplished evidence.",
      "dies_like_prior": "It resembles idea-007 because respiratory state can change geometry. The difference is that saber-sheath deformity is hypothesized as fixed chronic remodeling and is measured on perpendicular planes; nevertheless paired inspiration/expiration stability is an explicit gate. It differs from idea-006 by using no patient deletion. DATA_INSUFFICIENT is checked through the low-index prevalence gate.",
      "closest_prior_work": [
        {"citation": "Mikhael et al., Sybil", "identifier": "DOI 10.1200/JCO.22.01345; PMCID PMC10419602", "verified_fact": "Sybil predicts future lung cancer from a single low-dose chest CT and retains residual performance when visible nodules are removed.", "delta": "It did not measure tracheal index."},
        {"citation": "Pompe et al., CT quantification of tracheal abnormalities in COPD", "identifier": "PMCID PMC6052793", "verified_fact": "It defines an automated minimum tracheal index and found tracheal-shape information can add to emphysema in COPD severity assessment.", "delta": "It did not study a lung-cancer risk model or model reliance."}
      ],
      "existing_assets": ["Sybil code/weights and NLST pathway established in prior cycles", "Simple published automatic tracheal-index algorithm", "NLST acquisition metadata and repeat/reconstruction subsets"],
      "smallest_decisive_experiment": "Stage 0: measure native-DICOM versus final-tensor tracheal-index agreement; estimate prevalence and partial correlation with sex, LAA-950 emphysema, lung volume, BMI proxy, and kernel; test repeatability on paired reconstructions and any available respiratory pairs. Confirmatory: learn a validation-only tracheal-index direction, erase it from frozen Sybil embeddings, and compare risk-score change against emphysema, lung-volume, sex, and random-direction erasures on untouched cases.",
      "use_vs_association": "The model uses tracheal deformity only if its validated concept direction can be selectively removed and Sybil risk changes beyond emphysema/sex/lung-volume erasures. Score-index association alone remains exploratory.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "Paired reconstructions assess kernel sensitivity; scanner/vendor covariates possible; NLST site is masked and remains a limitation.",
        "positioning": "Centerline-perpendicular planes remove gantry/neck-angle bias; lung inflation remains an explicit control.",
        "habitus": "Body diameter/BMI proxy and thoracic cage ratio controls.",
        "prevalence_referral": "NLST uniform screening pathway addresses clinical referral but only in heavy smokers.",
        "label_leakage": "Cancer outcome is not used in X and cannot be printed into tracheal geometry."
      },
      "alternative_explanations": [
        {"alternative": "The index is only a proxy for male sex or body size.", "resolution": "Sex- and thoracic-ratio matched analysis plus separate concept erasures."},
        {"alternative": "The index is only emphysema/hyperinflation.", "resolution": "Joint LAA-950, lung-volume, and tracheal-index erasures; require incremental selective effect."},
        {"alternative": "Apparent shape is respiratory phase or preprocessing anisotropy.", "resolution": "Native-to-tensor agreement and paired respiratory/reconstruction repeatability gates."}
      ],
      "anticipated_negative": {"classification": "decisive", "reason": "If tracheal index is accurately encoded and reliably measurable, yet its erasure has an equivalently null effect while emphysema erasure changes Sybil, the specific chronic-remodeling hypothesis is weakened."},
      "cross_domain": {
        "borrowed_construct": "Fatigue/remodeling of a pressure-loaded cartilaginous tube.",
        "measurement_implied": "A fixed minimum transverse/AP ratio and its respiratory stability, rather than generic airway size.",
        "if_analogy_dropped": "The experiment would measure tracheal caliber. The mechanics analogy changes X to anisotropic shape, predicts a low transverse/AP ratio, and requires stability across respiratory state."
      },
      "remaining_legwork": "2 days for preprocessing geometry audit, 3 days for NLST prevalence/collinearity on a small sample, and 2 days for repeatability. First go/no-go in one week.",
      "scores": {
        "mechanism_clarity": {"value": 5, "why": "A precise ratio, anatomical level, predicted direction, and chronic mechanical cause."},
        "identifiability": {"value": 4, "why": "Internal erasure plus emphysema/sex/volume controls and real paired scans attack the main alternatives; masked site remains."},
        "interest": {"value": 5, "why": "An under-read tracheal shape as a long-term smoking mechanics recorder is surprising."},
        "medical_relevance": {"value": 4, "why": "It could explain risk as chronic obstructive injury rather than occult tumor signal."},
        "clarity": {"value": 5, "why": "The model-uses-X sentence is concrete and falsifiable."},
        "feasibility": {"value": 3, "why": "Capped; measurement is easy but tensor preservation and prevalence are uninspected."},
        "novelty_confidence": {"value": 3, "why": "Capped; no direct Sybil/tracheal-index study was found in a bounded search."},
        "prior_legwork": {"value": 4, "why": "Sybil assets and an automatic X algorithm already exist."},
        "data_readiness": {"value": 4, "why": "NLST/Sybil pathway is established in the repository record."},
        "evaluation_readiness": {"value": 4, "why": "Ratio, repeatability, partial association, and erasure controls are prespecifiable."},
        "negative_result_value": {"value": 5, "why": "After the encoding/reliability gate, a null erasure directly rejects the named mechanism."},
        "regret": {"value": 5, "why": "A one-week geometry audit could expose a simple overlooked signal."
        }
      },
      "mode_c_priority_score": 4.60,
      "priority_arithmetic": "0.30*5 + 0.25*4 + 0.20*5 + 0.15*4 + 0.10*5 = 4.60",
      "unverified_claims": ["Sybil preprocessing preserves tracheal aspect ratio", "Low tracheal index is prevalent enough in NLST", "The tracheal-index direction is separable from sex/emphysema/lung volume"]
    }
  ],
  "portfolio_ranking": {
    "mode_A_B": "C1 3.65, C2 3.60, C3 3.40 under the standard rubric.",
    "mode_C": "C5 4.60, C4 4.35 under the separate Mode C rubric; these numbers are not comparable with Mode A/B scores.",
    "recommendation": "Inspect C5 first because its keystone can be killed cheaply with native-to-tensor geometry and prevalence checks. If a more grounded program is preferred, inspect C1's checkpoint/OAI join; it is the only candidate anchored in a documented model-versus-radiologist gap.",
    "critical_caution": "All five are pre-keystone. None currently supports the deliverable sentence. C2 and C3 should be killed immediately if the executable measurement/model/data joins fail; C4 should be killed if injection timing or hepatic coverage cannot be controlled."
  }
}


===== STAGE TASK =====
<!-- stage: wide_scout -->
# Wide-mode scouting: raise the ceiling, keep the floor

This track exists because the baseline track selects for ideas that are safe by
sentence two. Here the *hypothesis space* is opened up while the *evidence
standards* stay exactly where the charter puts them. Ambitious in what is
claimed, conservative in how it would be shown.

## What is different from the baseline track

- Multi-step causal stories are allowed: "the model uses X, which it can only
  see because of Y, which implies Z about its failure mode" is eligible if each
  link is separately checkable.
- Cross-field transplants are mandatory, not optional: every candidate must
  borrow a construct, instrument, or law from a field outside medical imaging
  (physiology, physics, forensics, ecology, economics, materials, anything) and
  name the measurement the borrowed construct implies.
- Mechanistic surprise is the selection criterion. Ask: would a radiologist
  raise an eyebrow at the claim, and would they *change something* if it were
  true?

## What is NOT different

- The charter's hard constraint holds: X must be computable from an image
  today, by an existing tool or well-defined formula, with no human annotator.
- The deliverable sentence still has the form "the model is using X." Absence
  of a confound is still not X.
- The use-vs-association test still applies at generation time: for each
  candidate, state in one line how the design distinguishes "the model uses X"
  from "X is merely correlated with the label." If you cannot, the candidate is
  ineligible -- this single pattern killed nine of eleven ideas in cycle one.
- One compute envelope: the smallest decisive experiment must fit one Colab
  GPU session on public data. State the envelope explicitly per candidate.
- Read `evidence/ledger_digest.md` (in your context) before writing anything.
  Fill `dies_like_prior` against the kill-code table, per candidate.

## Keystone evidence rule

Any `keystone_status: INSPECTED_TRUE` claim MUST include a
`keystone_evidence` field quoting the artifact that proves it (URL,
file path, table row, or verbatim excerpt). A bare INSPECTED_TRUE
without evidence is mechanically demoted to NOT_INSPECTED at merge.

## Procedure

1. Write **eight** one-line questions. At least five must connect medical
   imaging to a distinct outside field (name the field in brackets). At least
   two should feel one step past what you believe defensible.
2. Develop **three**. For the five dropped, one line each on why.
3. For each developed candidate, produce the same fields as the baseline scout
   (deliverable_sentence, X_measurement, keystone_prerequisite / status /
   evidence, dies_like_prior, closest_prior_work, smallest_decisive_experiment,
   standing_confounds_addressed, scores, unverified_claims), **plus** a novelty
   triplet:
   - `novelty_neighbors`: the three closest prior works with identifiers,
     found by actually searching, not recalled;
   - `novelty_delta`: the precise difference in one sentence;
   - `why_not_done`: one of `NEW_CAPABILITY` (name the capability or dataset
     that only recently exists), `BLIND_SPOT` (state the reason the field
     missed it), or `TRIED_AND_FAILED` (cite it -- and treat this as a red
     flag, not a disqualifier).
   If you cannot find neighbors, write `NO_NEIGHBORS_FOUND` -- that is a flag
   for human verification, never proof of novelty.
4. Set `"track": "wide"` on every candidate.

Write `wide_candidates.json` with the shape `{"candidates": [...]}`.
Do not write code. Do not modify any other file.

