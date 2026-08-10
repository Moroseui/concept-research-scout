You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/014
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

34 tracked ideas. Latest state per idea; full history in ledger.jsonl.

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.
- **CIRCULARITY** x1: The endpoint is a re-encoding of the input or of the thing being tested.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **scout-007-c05** [NOVEL_VERIFIED, audited 2026-08-10] -- A lung-cancer model may be reading a mechanically remodeled trachea
- **scout-006-c04** [NOVEL_UNVERIFIED, audited 2026-08-10] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-006-c05** [NOVEL_UNVERIFIED, audited 2026-08-10] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two
- **scout-007-c03** [NOVEL_UNVERIFIED, audited 2026-08-10] -- Merlin may be reading fatty kidney rather than kidney shape
- **scout-007-c06** [NOVEL_UNVERIFIED, audited 2026-08-10] -- The effusion model may be reading whether pleural fluid still obeys gravity
- **scout-007-c07** [NOVEL_UNVERIFIED, audited 2026-08-10] -- The fibrosis model may be counting holes at the pleural edge
- **scout-007-c08** [NOVEL_UNVERIFIED, audited 2026-08-10] -- The PE model may be reading how completely blood and contrast have mixed
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
- **idea-014** [SHORTLISTED/CRITIQUED/baseline] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- **idea-015** [SHORTLISTED/SCOUTED/baseline] -- A breast-cancer risk model may be reading the arteries as a vascular clock
- **idea-016** [SHORTLISTED/SCOUTED/baseline] -- The PE model may read contrast flowing backward as a pressure gauge
- **scout-006-c01** [SHORTLISTED/SCOUTED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **scout-006-c02** [SHORTLISTED/SCOUTED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **scout-006-c03** [SCOUT_ONLY/SCOUTED/baseline] -- An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver
- **scout-006-c04** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-006-c05** [SCOUT_ONLY/SCOUTED/baseline] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two
- **scout-007-c01** [SHORTLISTED/SCOUTED/baseline] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- **scout-007-c02** [SHORTLISTED/SCOUTED/baseline] -- A breast-cancer risk model may be reading the arteries as a vascular clock
- **scout-007-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin may be reading fatty kidney rather than kidney shape
- **scout-007-c04** [SHORTLISTED/SCOUTED/baseline] -- The PE model may read contrast flowing backward as a pressure gauge
- **scout-007-c05** [SCOUT_ONLY/SCOUTED/baseline] -- A lung-cancer model may be reading a mechanically remodeled trachea
- **scout-007-c06** [SCOUT_ONLY/SCOUTED/wide] -- The effusion model may be reading whether pleural fluid still obeys gravity
- **scout-007-c07** [SCOUT_ONLY/SCOUTED/wide] -- The fibrosis model may be counting holes at the pleural edge
- **scout-007-c08** [SCOUT_ONLY/SCOUTED/wide] -- The PE model may be reading how completely blood and contrast have mixed
- **scout-007-c09** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-007-c10** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-007-c11** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-007-c12** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-007-c13** [REJECTED/SCOUTED/wide] -- (untitled)


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


===== ideas/014/README.md =====
# Idea 014: The knee-pain model may be reading trabecular stress architecture that KL grade throws away

Selected from scouting cycle 007, candidate 1.


===== ideas/014/critique.md =====
# Adversarial critique — Idea 014

## The knee-pain model may be reading trabecular stress architecture that KL grade throws away

```
FATAL OBJECTION: The design freezes and erases "the Pierson pain model," but no trained
  checkpoint exists — the repo ships training code only (Python 3.5.2, raw registration-
  gated OAI, reported terabyte-RAM preprocessing), so the frozen representation the entire
  readout depends on has to be reproduced from scratch, and that reproduction is unverified.
EVIDENCE: github.com/epierson9/pain-disparities README — only `train_models.py`
  (`train_best_model_continuous`), no weights; raw data at nda.nih.gov/oai/ is gated.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES (reproduce the model) — but feasibility unverified.
DECISION: PAUSE
```

The idea is genuinely interesting — it tries to decode a famous, real model-versus-human
gap (ALG-P predicts osteoarthritis pain beyond Kellgren–Lawrence and shrinks a racial pain
disparity) into a bone quantity a clinician recognizes, and two mature OAI literatures do sit
one experiment apart. That is why the header says PAUSE, not REJECT. But two things must be
settled before a probe contract, and the card currently under-states both.

---

## 1. The keystone is now partially inspected — and it fails as written

The card's keystone is: *"The frozen Pierson pain model or exactly reproducible checkpoint
can be run on OAI images…"* with `keystone_status: NOT_INSPECTED` and, in `unverified_claims`,
*"A runnable Pierson checkpoint is currently available."*

**Verified fact (inspected today):** it is not available. `github.com/epierson9/pain-disparities`
releases training code and analysis notebooks only. There is no weights file; reproduction is
`python train_models.py train_best_model_continuous` against raw OAI DICOMs downloaded from
`nda.nih.gov/oai/`, on a Python 3.5.2 environment, with preprocessing the authors say ran on
"a computer with several terabytes of RAM and hundreds of cores."

This changes the card in three ways the revision must absorb:

- **"Frozen Pierson model" is a misnomer.** Every downstream step — fit a probe from *frozen
  embeddings*, freeze the *validation-learned X direction*, *erase only it* — presumes a fixed
  published network. There is none. You would be probing *your* re-trained network. That is
  allowed, but then the deliverable sentence is about a reproduction, and its validity is
  gated on the reproduction reproducing the published ALG-P behaviour (better-than-KLG pain
  prediction; disparity reduction) on a frozen split. That equivalence check is a Stage-0 gate
  the card does not list.
- **Feasibility is below the current 3, not at it.** A legacy Python 3.5.2 stack, raw-DICOM
  reprocessing at the reported scale, and gated OAI access together exceed "first result in
  days" and strain the Colab-Pro+/single-GPU constraint for the *training* half (inference and
  the texture work are fine on a single GPU; the retraining and full-OAI preprocessing are the
  problem). The card's own `remaining_legwork` ("2 days to inspect checkpoint") is written as
  if a checkpoint were downloadable; it is not.
- **This is the loop's recurring wrong-keystone shape.** The easy adjacent fact ("Pierson and
  the texture literature both use OAI") was verified; the load-bearing fact ("there is a
  runnable frozen model to erase directions from") was assumed and is false as stated. Answer
  to the mandated question — *"if I have only verified the nearest checkable thing, what am I
  still assuming?"* — is: *that the model can be reproduced and will match the published gap.*
  That, not "texture varies within KL," is the real keystone.

Repairable? Yes — reproduce and validate the model. But until a reproduction is confirmed to
run and to recover ALG-P behaviour on a frozen split, there is literally nothing to erase, so
the study is blocked, not merely imperfect. Hence PAUSE.

## 2. Even granting a working model, the design does not identify the *directional* claim

The deliverable sentence is specifically *directional* — "directional thickening and
rarefaction," horizontal-versus-vertical fractal signatures, the load-path story from bone
mechanobiology. That directionality is the entire cross-domain content. The experiment as
written does not isolate it.

- **The readout erases one texture direction and compares to random / KL / JSN directions.**
  Subchondral trabecular texture, subchondral sclerosis, BMD, and joint-space narrowing are
  co-varying bone changes; the medial compartment darkens, scleroses, and narrows together.
  A KL/JSN "nuisance direction" is a coarse ordinal proxy and will not span the continuous
  sclerosis/density variation that rides along with texture. So a positive erasure effect that
  survives the JSN control still supports only *"the model uses medial subchondral bone
  texture/density"* — a named thing, but **a different named thing** than "directional
  load-path architecture," and one entangled with the disease severity the model is *expected*
  to read. That is the idea-009 estimand mismatch (REJECTED): a synthetic/representational
  deletion that does not map onto the specific naturally-occurring quantity named.
- **Apply the charter's own test — "what would be different if the analogy were dropped?"**
  As written: nothing. You would fit a probe to a fractal-signature scalar and erase it whether
  or not you believed the mechanobiology story. To make the analogy load-bearing, the *primary*
  readout must be directional specificity: erasing the **horizontal** signature harms pain
  prediction more than erasing an equal-norm **vertical** (or isotropic mean-density) signature.
  The card mentions horizontal-vs-vertical in `cross_domain` but does not commit it as the
  registered primary contrast, and does not list an isotropic-density nuisance direction among
  its controls. Without that, the directional claim is decoration on a generic-texture result.

## 3. The confound the card underweights: the measurement X is itself acquisition-sensitive

Fractal-signature / texture analysis of subchondral trabecular bone on **plain radiographs** is
well known to move with detector type (CR vs DR), pixel spacing, exposure, and focal-spot blur
(the OAI-adjacent literature the card leans on — e.g. tibial subchondral structure on plain
films, PMC5635082 — operates under exactly these constraints). OAI radiographs were acquired
across multiple clinical centres over years with fixed-flexion positioning but non-identical
equipment. So site/scanner leaks into **X itself**, contaminating both the probe target and,
potentially, what the network reads (echo of Gichoya: a bone-texture channel is exactly where a
site/race proxy could hide). The card's "site-held-out strata + external device replication"
is stated but not budgeted, and external device replication is not obviously available.

**The one strong structural move the card has, and should promote.** OAI's PA fixed-flexion
film images **both knees in a single exposure**; ALG-P is scored per knee. A **within-person,
within-film left-vs-right** contrast holds acquisition, exposure, habitus, and the patient's
systemic pain-reporting tendency fixed by construction, and asks whether the knee with the
greater directional subchondral texture asymmetry carries the higher ALG-P. This is the
"compare the model to itself" survivor move that the ledger explicitly says is under-used. It
is a cleaner identifier than embedding erasure and is nearly acquisition-immune. **Caveat to
verify in Stage 0:** it only works if the Pierson network scores single-knee crops from the
bilateral film (so left/right share one exposure). If the model ingests a differently framed
input, the acquisition-matching is lost. This should be inspected in the repo's
`image_processing.py`, not assumed.

## 4. Smaller marks (not decisive individually)

- **Domain fit.** The charter's emphasis is CT / 3D volumetric imaging; this is a 2D knee
  radiograph. Explicitly allowed as radiology, but off the stated centre of gravity. Minor.
- **Negative-result value is genuinely weak (score 2 is right).** A null erasure is
  sensitivity-limited (nonlinear coding survives); a positive erasure is ambiguous (collinear
  severity removed). Neither tail is a decisive type-1 negative. The bilateral-asymmetry
  association arm (below) has a cleaner negative: no KLG-independent texture-pain association ⇒
  the flagship is dead.
- **`dies_like_prior` is fair.** It does not repeat DATA_INSUFFICIENT (X is image-computable,
  not the sparse LIDC diagnosis join) or CIRCULARITY (X is neither the pain label nor KL). The
  provenance failure mode does not apply because X needs no annotator. Agreed. Its real risk is
  the idea-009 identifiability mismatch, which is a different, live danger.
- **"Fractal signature" is not off-the-shelf.** Janvier's variance-orientation-transform /
  validated semiautomated FNIH software is not a `pip install`. Reproducing a *stable,
  repeatable* directional signature (Stage-0 repeatability floor) is real, non-trivial legwork
  the card correctly flags but should not under-budget.

---

## Verdict rationale

PAUSE, not REJECT: the medical premise is real and the question is high-regret. PAUSE, not
ADVANCE-TO-REVISION: the load-bearing asset (a runnable frozen model) is verified-absent, and
the design's directional claim is not yet identifiable — both must be resolved before a probe
contract, and the first is an external feasibility fact the human should confirm rather than a
prose fix.

**Reopening conditions (all three):**
1. A reproduced Pierson model runs on a frozen OAI split and recovers the published ALG-P
   behaviour (better-than-KLG pain prediction; the disparity signature). Until then there is no
   representation to erase.
2. The primary readout is redesigned to test **directional** specificity (horizontal-vs-vertical /
   vs isotropic-density erasure), so the mechanobiology analogy is load-bearing, not decoration.
3. The **within-film left-vs-right** contrast is promoted to the primary identifying design, and
   `image_processing.py` is inspected to confirm the network scores acquisition-matched
   single-knee crops.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: In OAI, does directional medial-tibial subchondral
  fractal signature explain osteoarthritis pain that Kellgren–Lawrence misses — tested as a
  within-person, within-film left-vs-right asymmetry against the WOMAC/KLG-residual — using only
  OAI images, published FSA, and pain labels, with no neural network and no retraining?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — it tests the substrate premise (does this bone
  texture carry KLG-independent pain signal at all) but drops the charter's core "what is the
  MODEL using" framing; it is a premise gate, not a model-decode.
SHOULD IT BECOME A SEPARATE CANDIDATE? YES — it needs no checkpoint, no legacy stack, and no
  concept-erasure calibration, so it is unblocked while Idea 014 waits on reproduction.
IS IT ACTUALLY WORTH DOING? Yes: it is a cheap, decisive gate — a null KLG-adjusted texture-pain
  association within person kills the flagship before anyone retrains a 2021 model, and a
  positive one is the strongest possible motivator for the harder model-decode study; the only
  real cost is reproducing a repeatable directional FSA, which is needed for Idea 014 regardless.
```


===== ideas/014/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The study cannot presently answer its original question because the published Pierson pain model is not available as a frozen checkpoint, and substituting a newly trained reproduction changes the object whose mechanism is being claimed.

**Argument:** The question and deliverable sentence concern “the knee-pain model of Pierson et al.,” but the authors' repository releases training and analysis code rather than trained weights, while the required raw OAI inputs are registration-gated and the documented preprocessing depends on a legacy Python 3.5.2 stack and unusually large compute. Thus the card's decisive operation—learning and erasing a texture direction in frozen embeddings—has no verified representation on which to operate. Retraining is not a neutral implementation detail: a reproduction can reach a similar aggregate pain metric while encoding a different solution because of initialization, preprocessing, cohort construction, or shortcut use. It would therefore support only “our reproduction uses X,” not the stated claim about the published model. This is the recurring wrong-keystone error: verifying that both literatures use OAI does not verify that the specific model whose behavior motivates the study is runnable or reproducible. The proposed checkpoint-free within-film left-versus-right texture analysis is scientifically useful, but the identity check fails—it tests whether X carries KL-independent pain information, not whether any model uses X, so it belongs as a separate premise-gate candidate rather than as a repair that advances Idea 014.

**What would change my mind:** Show either (1) an authenticated frozen checkpoint with its exact preprocessing that reproduces the published better-than-KLG pain result on a frozen OAI evaluation set, or (2) a preregistered reproduction criterion followed by at least two independently trained models that each recover the published performance/disparity behavior and the same selective horizontal-versus-vertical texture-use effect; the claim must then be explicitly narrowed to the reproduced model family.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** No frozen Pierson checkpoint exists — the repository releases training code only, the raw OAI inputs are registration-gated, and the documented preprocessing ran on a legacy large-memory stack. A retrained reproduction is a different object: it could match the aggregate pain metric while encoding a different solution, so erasure results would establish only "our reproduction uses X," not the card's stated claim about the published model.

**Response:** AMEND

**Argument:** The factual core is conceded without reservation: the checkpoint does not exist, `unverified_claims` item 1 is now verified false, and the card's phrase "frozen Pierson model" was a misnomer resting on exactly the wrong-keystone pattern the charter warns about. I will not relitigate that.

The amendment adopts the critic's own second condition, and I want to argue it is a repair rather than a retreat — with one substantive point the critic's framing undersells. The scientific object that motivates this card was never the particular weight file on Pierson's disk. The evidence that signal exists (entry point 1) is a *behavioral gap*: models trained this way predict pain beyond KLG and shrink the racial pain disparity. Any mechanism claim of the form "the model uses X" is scientifically durable only at the level of the model family that exhibits that gap — a single checkpoint is one draw from a training distribution, and a mechanism found in one draw and absent in the next was never an explanation of the gap. The critic's worry ("a reproduction can reach a similar aggregate metric while encoding a different solution") is real, but it cuts equally against the published checkpoint had it existed. The multi-seed design does not merely patch the missing artifact; it upgrades the claim from "this network uses X" to "networks that close this gap use X," which is the version a radiologist should care about. And if independently trained gap-reproducing models do *not* share the texture-use effect — the failure mode the critic predicts — that is itself a decisive, informative finding: the ALG-P gap is not explained by a stable image substrate at the family level, and single-model mechanism claims about it are unfounded. That converts the critic's objection into one of the study's interpretable outcomes rather than a reason it cannot run.

Concretely, the card changes as follows:

1. **Object of the claim.** "The knee-pain model of Pierson et al." becomes "models trained by the published Pierson recipe that pass a preregistered reproduction gate." The gate, frozen before any texture work: better-than-KLG knee-pain prediction and the disparity-reduction signature, on a frozen OAI evaluation split, within prespecified tolerances of the published values. At least two independent seeds must pass, and the confirmatory erasure effect must replicate across seeds. Identity check: the one-sentence question survives with its referent read at the family level — same gap, same recipe, same OAI substrate, same X, same erasure readout. It does not become a different study; it becomes the version of the study whose conclusion could ever have generalized.
2. **New keystone, honestly downgraded.** The keystone becomes: *a reproduction passing the behavioral gate can actually be trained under our access and compute.* Status: NOT_INSPECTED, and genuinely uncertain — OAI access is registration-gated (permitted under the charter, but unconfirmed for us), and the authors' reported preprocessing scale strains the single-GPU constraint. Whether preprocessing can be restructured to stream rather than hold terabytes in RAM is an inference, not a verified fact. Stage 0 is therefore: obtain access, reproduce, hit the gate — before any probe contract.
3. **Scores drop.** Feasibility 3 → 2 (gated access plus retraining precede the first scientific readout; weeks, not days). `remaining_legwork` is rewritten: the "2 days to inspect checkpoint" line is void. Priority falls accordingly; that is the price of the misnomer and I am not disputing it.
4. **What is lost.** (a) Any claim about the exact published artifact — if Pierson's specific run used a shortcut our reproductions do not, this design cannot see it. (b) If no reproduction passes the gate, the idea dies at Stage 0; per the charter that is a legitimate feasibility result, but it is a real risk of total loss. (c) The deliverable sentence weakens from "the knee-pain model is using X" to "models that reproduce the published pain-prediction gap are using X."

**Spin-off, agreed, not folded in:** the checkpoint-free within-film left-versus-right texture-versus-pain premise gate. The critic is right that it fails the identity check as a repair — it tests whether X carries KL-independent pain signal, not whether any model uses it. It should enter the backlog as its own candidate, and its result gates whether the expensive reproduction in (2) is worth attempting at all: a null within-person KLG-adjusted texture-pain association kills this card before anyone trains anything.

**Status:** OPEN — the amendment implements the critic's stated condition (2); it stands or falls on whether the critic accepts the family-level reading of the original question and the honestly-uncertain reproduction keystone.

## Round 2 — CRITIC

**Position:** The family-level amendment preserves the original model-decoding question, but the proposed concept-direction erasure still cannot identify the claimed directional trabecular mechanism rather than correlated subchondral density and structural disease severity.

**Argument:** I concede the Round 1 identity objection because the proposer supplied a substantive restriction, not merely a relabeling: at least two independently trained models must first reproduce the published better-than-KLG pain behavior and disparity signature, and the deliverable is explicitly narrowed to that reproducible model family. That still asks what models exhibiting the original gap use. The strongest remaining objection is now the intervention estimand. A validation-learned embedding direction predictive of horizontal or vertical fractal signature will generally also encode continuous sclerosis/mineral density, joint-space width, alignment, osteophyte burden, and acquisition-dependent sharpness, because these quantities co-vary in medial tibial subchondral bone. Erasing a KL or joint-space direction does not solve this: coarse ordinal KLG/JSN labels cannot be expected to span their continuous image variation, and equal-norm random-direction controls test generic damage, not biological specificity. Consequently, even a replicated selective score loss would support at most “gap-reproducing models use information correlated with the measured subchondral texture,” not the rung-3 sentence that they use directional thickening and rarefaction along load paths. This is the idea-009 estimand-mismatch failure in a new representation: association of a direction with X plus sensitivity to deleting that direction does not establish reliance on naturally occurring X when the direction is not separable from its principal correlates. The mechanobiology analogy becomes load-bearing only if the confirmatory contrast isolates orientation while holding isotropic density and other local image content fixed; merely comparing separately learned horizontal and vertical probe directions does not guarantee that isolation.

**What would change my mind:** Show, before outcome testing, a validated intervention or natural contrast that changes the horizontal-versus-vertical fractal-signature ratio while preserving mean attenuation/intensity, power spectrum or matched non-directional texture, joint geometry, and acquisition characteristics within prespecified tolerances; then show that the frozen model responds selectively to the orientation change across every reproduction-gate-passing seed and not to matched isotropic-density or sham changes. Alternatively, demonstrate on held-out images that an orthogonalized directional probe predicts X with a prespecified reliability floor after conditioning on continuous BMD/sclerosis, JSW, alignment, osteophytes, site, detector, and pixel spacing, and that erasing it leaves those nuisance quantities decodable within equivalence margins.

**Status:** OPEN

## Round 3 — PROPOSER

**Responding to:** A validation-learned embedding direction predictive of the horizontal or vertical fractal signature will co-encode continuous sclerosis/mineral density, joint-space width, alignment, osteophyte burden, and acquisition sharpness, because these co-vary in medial tibial subchondral bone. Erasing that direction — even with KL/JSN and equal-norm random controls — therefore identifies at most "gap-reproducing models use information correlated with subchondral texture," not the rung-3 directional sentence. The mechanobiology analogy is load-bearing only if the contrast isolates orientation while holding isotropic density, geometry, and acquisition fixed; comparing separately learned horizontal and vertical probe directions does not guarantee that isolation.

**Response:** AMEND

**Argument:** I concede the narrow, decisive part first: the erasure-only readout as written cannot reach rung 3, and comparing separately-learned horizontal and vertical probe directions does not isolate orientation. The critic is correct that a learned direction is not separable from its principal correlates by construction, and that random/KL/JSN controls test generic damage or coarse ordinal severity, not biological specificity. Defending representational erasure as the *primary* identifier would be exactly the idea-009 mistake in new clothes. So I drop it as the primary readout rather than restate it.

But the critic's first "change-my-mind" condition is not a bar I have to clear by luck — it is constructible, and it converts the study into the ledger's endorsed survivor move (compare the model to itself across two versions of *identical* anatomy). Orientation anisotropy of a texture *is* the angular distribution of its 2-D power spectrum; the isotropic content the critic wants held fixed *is* the radially-averaged power profile plus the DC term. Those are separable coordinates of the same spectrum. So the isolating intervention is well-defined:

1. **Primary confirmatory readout — a band-limited anisotropy swap on the subchondral ROI.** Inside the landmark-placed ROI, restrict to the trabecular spatial-frequency band (frequencies matching trabecular spacing), leaving the low-frequency band that carries joint geometry, cortical outline, osteophyte edges, and JSW untouched. Within that band, reallocate angular power to raise or lower the horizontal-versus-vertical ratio while holding the *radial* power profile and the DC/mean attenuation fixed to prescribed tolerances. Measure the paired change in the frozen model's knee-specific pain score, on the same anatomy, across every gate-passing seed. This is not "erase a learned direction and hope it was X"; it is a physical edit whose held-fixed and varied quantities are specified in image space before any outcome is read.

2. **The matched sham that makes orientation the estimand.** The control is an **isotropic-density edit of equal image-space L2 norm**: change the radial power profile in the same band (add/remove mean subchondral density/sclerosis) while holding the angular ratio fixed. The rung-3 claim survives only if the anisotropy edit moves the pain score and the norm-matched isotropic-density edit does not, across all seeds. This directly answers the collinearity objection: density and orientation are now varied one at a time with matched perturbation magnitude, so a differential response cannot be attributed to "generic subchondral change."

3. **The in-distribution gate that answers the OOD-artifact alternative (Stage 0, hard).** An edit the network has never seen could move the score because it is unfamiliar, not because of its orientation content. So both edits must pass: (a) edited ROIs' anisotropy ratio and radial power stay inside the empirical range measured across real OAI subchondral ROIs; (b) an identity edit (round-trip through the pipeline with zero net change) leaves the score unchanged within a sham tolerance. If no orientation edit can be made that stays in-distribution, rung 3 is unreachable and the study reports that as a decisive feasibility limit — it does not get to assert the directional claim anyway.

4. **The erasure apparatus is demoted to exploratory corroboration**, and the probe is rewritten to the critic's second condition: an orthogonalized directional probe must predict the fractal signature above a prespecified reliability floor *after conditioning on continuous mean-ROI attenuation (density/sclerosis surrogate), JSW, alignment, osteophyte score, site, detector, and pixel spacing*, with the nuisance quantities still decodable after erasure within equivalence margins. This is corroboration, not the identifier.

**Identity check.** The one-sentence question is unchanged: do gap-reproducing models use directional medial tibial subchondral trabecular texture — directional thickening and rarefaction — that KL grade throws away? Same X, same model family, same anatomy. Only the readout changes: from erasing a learned direction to an orientation-isolating image intervention on the same scan. It still answers the original question; it now answers it identifiably.

**What is lost.** (a) Feasibility drops again — building and validating a band-limited, radial-power-and-DC-preserving anisotropy editor with prescribed tolerances is real signal-processing work on top of the reproduction burden; the first confirmatory readout is now well past "days," and `feasibility` should sit at 2 with `evaluation_readiness` dropped to 2 (the isolating intervention and its in-distribution gate are bespoke, not off-the-shelf). (b) A new total-loss branch: if the in-distribution gate cannot be met, the directional claim is simply unreachable for this substrate — a legitimate but real risk. (c) The negative-result value improves in one tail: a within-anatomy anisotropy edit that moves no score across all seeds, while the matched isotropic-density edit does, is now a *decisive* type-1 negative against the directional hypothesis, not a sensitivity-limited null — so `negative_result_value` rises from 2 to 3 for the intervention arm. This is the first amendment that buys back scientific value rather than only paying for feasibility.

That is two amendments now (family-level object in Round 1, orientation-isolating intervention here). Per the rules I flag that a third would signal the original framing was wrong. I do not think we are there: the object survived unchanged and the readout is now identifiable by construction. But the reproduction keystone remains NOT_INSPECTED and genuinely uncertain, and I am not claiming otherwise.

**Status:** OPEN — the amendment implements the critic's stated first condition (orientation isolation with a norm-matched isotropic-density sham and an in-distribution gate). It stands or falls on whether the critic accepts that band-limited angular/radial spectral separation genuinely isolates orientation from isotropic density and geometry, and that the in-distribution gate adequately blocks the OOD-artifact alternative.

## Round 3 — CRITIC

**Position:** The spectral amendment preserves the original question in words, but its intervention manipulates angular Fourier power rather than validated trabecular thickening and rarefaction, so a positive response still would not identify the named biological architecture.

**Argument:** Holding the DC term and radially averaged power fixed does separate one image statistic—angular spectral anisotropy—from isotropic spectral energy, and that is a real improvement over concept-direction erasure. It does not, however, make the edited image a counterfactual of the same bone with altered load-path architecture. Fourier power discards phase and therefore does not determine trabecular connectivity, plate/rod organization, thickness, spacing, or where oriented structures meet the cortical boundary; reallocating angular power can introduce coherent ringing, directional blur, or boundary discontinuities while matching the proposed anisotropy ratio and radial profile. The Stage-0 gates do not close this gap: falling inside the marginal empirical ranges of two summary statistics is not evidence that their joint spatial realization is anatomically plausible, and a zero-change round trip tests pipeline fidelity rather than artifacts created by a nonzero angular reallocation. Nor is an equal-L2 isotropic edit a sufficient sham, because CNN responses depend strongly on perturbation morphology and frequency orientation, not only norm. Thus a selective score change would establish at most that the reproduced models respond to angular power in the medial-tibial ROI. It would not support the deliverable sentence that they use “directional thickening and rarefaction of the load-bearing bone,” which is the independently measurable X defined by fractal-signature bone literature. The identity check therefore fails at the estimand level: the revised experiment answers a narrower synthetic spectral-cue question unless angular-power edits are independently shown to track genuine trabecular architectural changes. This is not a repetition of the Round 2 collinearity objection; density and geometry may be numerically held fixed while the manipulated object still lacks biological validity.

**What would change my mind:** On an independent paired radiograph–3D bone-imaging dataset (micro-CT, HR-pQCT, or another validated structural reference), show that the exact edit produces prescribed changes in orientation-specific trabecular thickness/spacing or fractal signature while preserving connectivity, non-directional texture, cortical boundaries, and acquisition appearance within preregistered tolerances; additionally, show that blinded real-versus-edited discrimination by an acquisition-matched detector is at chance or within an equivalence margin for every edit magnitude used. A validated generative counterfactual conditioned on those same structural measurements could satisfy the same requirement. Without such validation, narrow the rung-3 sentence to “the models use angular band-power anisotropy in the subchondral ROI,” which would be a separate, weaker candidate.

**Status:** OPEN


===== ideas/014/idea_card.json =====
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
  "deliverable_sentence": "The knee-pain model is using medial tibial subchondral trabecular texture\u2014directional thickening and rarefaction of the load-bearing bone beneath the cartilage.",
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
  "existing_assets": [
    "OAI bilateral longitudinal knee radiographs and WOMAC pain data (registration-controlled access, not an unconfirmed DUA-gated dependency for the card)",
    "Published pain-model architecture/reproduction materials",
    "Published fractal-signature formula and OAI texture precedents"
  ],
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
    {
      "alternative": "Texture is a proxy for malalignment or joint-space narrowing.",
      "resolution": "Measure both, learn nuisance directions, and require texture erasure to add harm beyond them."
    },
    {
      "alternative": "Computed-radiography post-processing creates texture differences.",
      "resolution": "Site/acquisition strata and bilateral same-image contrasts address much, but external device replication remains necessary."
    },
    {
      "alternative": "Erasure removes generic image information rather than X.",
      "resolution": "Equal-norm random, landmark, and KL-direction erasures plus retained reconstruction performance test selectivity."
    }
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
    "clarity": {
      "value": 5,
      "why": "One model, one named bone compartment, one defined texture measurement."
    },
    "identifiability": {
      "value": 3,
      "why": "Internal erasure and bilateral controls improve on association, but texture is entangled with alignment and erasure may not be specific."
    },
    "medical_relevance": {
      "value": 4,
      "why": "It could name the missing radiographic substrate behind clinically important pain discordance."
    },
    "interest": {
      "value": 5,
      "why": "It attempts to decode a documented model-human gap with a bone quantity clinicians can recognize."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Both the gap and the exact measurement have OAI precedents."
    },
    "feasibility": {
      "value": 3,
      "why": "Capped: keystone not inspected; access and checkpoint reproducibility remain."
    },
    "data_readiness": {
      "value": 3,
      "why": "OAI is established but registration-controlled."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "Fractal metrics exist; selective-erasure calibration needs custom controls."
    },
    "negative_result_value": {
      "value": 2,
      "why": "The anticipated null is sensitivity-limited."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Capped and no exhaustive review; the precise model-to-texture link was not located."
    },
    "regret": {
      "value": 5,
      "why": "Two mature OAI literatures sit one model-use experiment apart."
    }
  },
  "priority_score": 3.65,
  "priority_arithmetic": "0.20*3 + 0.15*3 + 0.15*4 + 0.10*4 + 0.10*5 + 0.10*5 + 0.10*2 + 0.05*3 + 0.05*3 = 3.65",
  "unverified_claims": [
    "A runnable Pierson checkpoint is currently available",
    "Texture varies sufficiently within KL grade and acquisition strata",
    "The validation-learned concept direction is selectively erasable"
  ],
  "track": "baseline"
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
You are codex. Your interlocutor is claude.
This is round 3. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The study cannot presently answer its original question because the published Pierson pain model is not available as a frozen checkpoint, and substituting a newly trained reproduction changes the object whose mechanism is being claimed.

**Argument:** The question and deliverable sentence concern “the knee-pain model of Pierson et al.,” but the authors' repository releases training and analysis code rather than trained weights, while the required raw OAI inputs are registration-gated and the documented preprocessing depends on a legacy Python 3.5.2 stack and unusually large compute. Thus the card's decisive operation—learning and erasing a texture direction in frozen embeddings—has no verified representation on which to operate. Retraining is not a neutral implementation detail: a reproduction can reach a similar aggregate pain metric while encoding a different solution because of initialization, preprocessing, cohort construction, or shortcut use. It would therefore support only “our reproduction uses X,” not the stated claim about the published model. This is the recurring wrong-keystone error: verifying that both literatures use OAI does not verify that the specific model whose behavior motivates the study is runnable or reproducible. The proposed checkpoint-free within-film left-versus-right texture analysis is scientifically useful, but the identity check fails—it tests whether X carries KL-independent pain information, not whether any model uses X, so it belongs as a separate premise-gate candidate rather than as a repair that advances Idea 014.

**What would change my mind:** Show either (1) an authenticated frozen checkpoint with its exact preprocessing that reproduces the published better-than-KLG pain result on a frozen OAI evaluation set, or (2) a preregistered reproduction criterion followed by at least two independently trained models that each recover the published performance/disparity behavior and the same selective horizontal-versus-vertical texture-use effect; the claim must then be explicitly narrowed to the reproduced model family.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** No frozen Pierson checkpoint exists — the repository releases training code only, the raw OAI inputs are registration-gated, and the documented preprocessing ran on a legacy large-memory stack. A retrained reproduction is a different object: it could match the aggregate pain metric while encoding a different solution, so erasure results would establish only "our reproduction uses X," not the card's stated claim about the published model.

**Response:** AMEND

**Argument:** The factual core is conceded without reservation: the checkpoint does not exist, `unverified_claims` item 1 is now verified false, and the card's phrase "frozen Pierson model" was a misnomer resting on exactly the wrong-keystone pattern the charter warns about. I will not relitigate that.

The amendment adopts the critic's own second condition, and I want to argue it is a repair rather than a retreat — with one substantive point the critic's framing undersells. The scientific object that motivates this card was never the particular weight file on Pierson's disk. The evidence that signal exists (entry point 1) is a *behavioral gap*: models trained this way predict pain beyond KLG and shrink the racial pain disparity. Any mechanism claim of the form "the model uses X" is scientifically durable only at the level of the model family that exhibits that gap — a single checkpoint is one draw from a training distribution, and a mechanism found in one draw and absent in the next was never an explanation of the gap. The critic's worry ("a reproduction can reach a similar aggregate metric while encoding a different solution") is real, but it cuts equally against the published checkpoint had it existed. The multi-seed design does not merely patch the missing artifact; it upgrades the claim from "this network uses X" to "networks that close this gap use X," which is the version a radiologist should care about. And if independently trained gap-reproducing models do *not* share the texture-use effect — the failure mode the critic predicts — that is itself a decisive, informative finding: the ALG-P gap is not explained by a stable image substrate at the family level, and single-model mechanism claims about it are unfounded. That converts the critic's objection into one of the study's interpretable outcomes rather than a reason it cannot run.

Concretely, the card changes as follows:

1. **Object of the claim.** "The knee-pain model of Pierson et al." becomes "models trained by the published Pierson recipe that pass a preregistered reproduction gate." The gate, frozen before any texture work: better-than-KLG knee-pain prediction and the disparity-reduction signature, on a frozen OAI evaluation split, within prespecified tolerances of the published values. At least two independent seeds must pass, and the confirmatory erasure effect must replicate across seeds. Identity check: the one-sentence question survives with its referent read at the family level — same gap, same recipe, same OAI substrate, same X, same erasure readout. It does not become a different study; it becomes the version of the study whose conclusion could ever have generalized.
2. **New keystone, honestly downgraded.** The keystone becomes: *a reproduction passing the behavioral gate can actually be trained under our access and compute.* Status: NOT_INSPECTED, and genuinely uncertain — OAI access is registration-gated (permitted under the charter, but unconfirmed for us), and the authors' reported preprocessing scale strains the single-GPU constraint. Whether preprocessing can be restructured to stream rather than hold terabytes in RAM is an inference, not a verified fact. Stage 0 is therefore: obtain access, reproduce, hit the gate — before any probe contract.
3. **Scores drop.** Feasibility 3 → 2 (gated access plus retraining precede the first scientific readout; weeks, not days). `remaining_legwork` is rewritten: the "2 days to inspect checkpoint" line is void. Priority falls accordingly; that is the price of the misnomer and I am not disputing it.
4. **What is lost.** (a) Any claim about the exact published artifact — if Pierson's specific run used a shortcut our reproductions do not, this design cannot see it. (b) If no reproduction passes the gate, the idea dies at Stage 0; per the charter that is a legitimate feasibility result, but it is a real risk of total loss. (c) The deliverable sentence weakens from "the knee-pain model is using X" to "models that reproduce the published pain-prediction gap are using X."

**Spin-off, agreed, not folded in:** the checkpoint-free within-film left-versus-right texture-versus-pain premise gate. The critic is right that it fails the identity check as a repair — it tests whether X carries KL-independent pain signal, not whether any model uses it. It should enter the backlog as its own candidate, and its result gates whether the expensive reproduction in (2) is worth attempting at all: a null within-person KLG-adjusted texture-pain association kills this card before anyone trains anything.

**Status:** OPEN — the amendment implements the critic's stated condition (2); it stands or falls on whether the critic accepts the family-level reading of the original question and the honestly-uncertain reproduction keystone.

## Round 2 — CRITIC

**Position:** The family-level amendment preserves the original model-decoding question, but the proposed concept-direction erasure still cannot identify the claimed directional trabecular mechanism rather than correlated subchondral density and structural disease severity.

**Argument:** I concede the Round 1 identity objection because the proposer supplied a substantive restriction, not merely a relabeling: at least two independently trained models must first reproduce the published better-than-KLG pain behavior and disparity signature, and the deliverable is explicitly narrowed to that reproducible model family. That still asks what models exhibiting the original gap use. The strongest remaining objection is now the intervention estimand. A validation-learned embedding direction predictive of horizontal or vertical fractal signature will generally also encode continuous sclerosis/mineral density, joint-space width, alignment, osteophyte burden, and acquisition-dependent sharpness, because these quantities co-vary in medial tibial subchondral bone. Erasing a KL or joint-space direction does not solve this: coarse ordinal KLG/JSN labels cannot be expected to span their continuous image variation, and equal-norm random-direction controls test generic damage, not biological specificity. Consequently, even a replicated selective score loss would support at most “gap-reproducing models use information correlated with the measured subchondral texture,” not the rung-3 sentence that they use directional thickening and rarefaction along load paths. This is the idea-009 estimand-mismatch failure in a new representation: association of a direction with X plus sensitivity to deleting that direction does not establish reliance on naturally occurring X when the direction is not separable from its principal correlates. The mechanobiology analogy becomes load-bearing only if the confirmatory contrast isolates orientation while holding isotropic density and other local image content fixed; merely comparing separately learned horizontal and vertical probe directions does not guarantee that isolation.

**What would change my mind:** Show, before outcome testing, a validated intervention or natural contrast that changes the horizontal-versus-vertical fractal-signature ratio while preserving mean attenuation/intensity, power spectrum or matched non-directional texture, joint geometry, and acquisition characteristics within prespecified tolerances; then show that the frozen model responds selectively to the orientation change across every reproduction-gate-passing seed and not to matched isotropic-density or sham changes. Alternatively, demonstrate on held-out images that an orthogonalized directional probe predicts X with a prespecified reliability floor after conditioning on continuous BMD/sclerosis, JSW, alignment, osteophytes, site, detector, and pixel spacing, and that erasing it leaves those nuisance quantities decodable within equivalence margins.

**Status:** OPEN

## Round 3 — PROPOSER

**Responding to:** A validation-learned embedding direction predictive of the horizontal or vertical fractal signature will co-encode continuous sclerosis/mineral density, joint-space width, alignment, osteophyte burden, and acquisition sharpness, because these co-vary in medial tibial subchondral bone. Erasing that direction — even with KL/JSN and equal-norm random controls — therefore identifies at most "gap-reproducing models use information correlated with subchondral texture," not the rung-3 directional sentence. The mechanobiology analogy is load-bearing only if the contrast isolates orientation while holding isotropic density, geometry, and acquisition fixed; comparing separately learned horizontal and vertical probe directions does not guarantee that isolation.

**Response:** AMEND

**Argument:** I concede the narrow, decisive part first: the erasure-only readout as written cannot reach rung 3, and comparing separately-learned horizontal and vertical probe directions does not isolate orientation. The critic is correct that a learned direction is not separable from its principal correlates by construction, and that random/KL/JSN controls test generic damage or coarse ordinal severity, not biological specificity. Defending representational erasure as the *primary* identifier would be exactly the idea-009 mistake in new clothes. So I drop it as the primary readout rather than restate it.

But the critic's first "change-my-mind" condition is not a bar I have to clear by luck — it is constructible, and it converts the study into the ledger's endorsed survivor move (compare the model to itself across two versions of *identical* anatomy). Orientation anisotropy of a texture *is* the angular distribution of its 2-D power spectrum; the isotropic content the critic wants held fixed *is* the radially-averaged power profile plus the DC term. Those are separable coordinates of the same spectrum. So the isolating intervention is well-defined:

1. **Primary confirmatory readout — a band-limited anisotropy swap on the subchondral ROI.** Inside the landmark-placed ROI, restrict to the trabecular spatial-frequency band (frequencies matching trabecular spacing), leaving the low-frequency band that carries joint geometry, cortical outline, osteophyte edges, and JSW untouched. Within that band, reallocate angular power to raise or lower the horizontal-versus-vertical ratio while holding the *radial* power profile and the DC/mean attenuation fixed to prescribed tolerances. Measure the paired change in the frozen model's knee-specific pain score, on the same anatomy, across every gate-passing seed. This is not "erase a learned direction and hope it was X"; it is a physical edit whose held-fixed and varied quantities are specified in image space before any outcome is read.

2. **The matched sham that makes orientation the estimand.** The control is an **isotropic-density edit of equal image-space L2 norm**: change the radial power profile in the same band (add/remove mean subchondral density/sclerosis) while holding the angular ratio fixed. The rung-3 claim survives only if the anisotropy edit moves the pain score and the norm-matched isotropic-density edit does not, across all seeds. This directly answers the collinearity objection: density and orientation are now varied one at a time with matched perturbation magnitude, so a differential response cannot be attributed to "generic subchondral change."

3. **The in-distribution gate that answers the OOD-artifact alternative (Stage 0, hard).** An edit the network has never seen could move the score because it is unfamiliar, not because of its orientation content. So both edits must pass: (a) edited ROIs' anisotropy ratio and radial power stay inside the empirical range measured across real OAI subchondral ROIs; (b) an identity edit (round-trip through the pipeline with zero net change) leaves the score unchanged within a sham tolerance. If no orientation edit can be made that stays in-distribution, rung 3 is unreachable and the study reports that as a decisive feasibility limit — it does not get to assert the directional claim anyway.

4. **The erasure apparatus is demoted to exploratory corroboration**, and the probe is rewritten to the critic's second condition: an orthogonalized directional probe must predict the fractal signature above a prespecified reliability floor *after conditioning on continuous mean-ROI attenuation (density/sclerosis surrogate), JSW, alignment, osteophyte score, site, detector, and pixel spacing*, with the nuisance quantities still decodable after erasure within equivalence margins. This is corroboration, not the identifier.

**Identity check.** The one-sentence question is unchanged: do gap-reproducing models use directional medial tibial subchondral trabecular texture — directional thickening and rarefaction — that KL grade throws away? Same X, same model family, same anatomy. Only the readout changes: from erasing a learned direction to an orientation-isolating image intervention on the same scan. It still answers the original question; it now answers it identifiably.

**What is lost.** (a) Feasibility drops again — building and validating a band-limited, radial-power-and-DC-preserving anisotropy editor with prescribed tolerances is real signal-processing work on top of the reproduction burden; the first confirmatory readout is now well past "days," and `feasibility` should sit at 2 with `evaluation_readiness` dropped to 2 (the isolating intervention and its in-distribution gate are bespoke, not off-the-shelf). (b) A new total-loss branch: if the in-distribution gate cannot be met, the directional claim is simply unreachable for this substrate — a legitimate but real risk. (c) The negative-result value improves in one tail: a within-anatomy anisotropy edit that moves no score across all seeds, while the matched isotropic-density edit does, is now a *decisive* type-1 negative against the directional hypothesis, not a sensitivity-limited null — so `negative_result_value` rises from 2 to 3 for the intervention arm. This is the first amendment that buys back scientific value rather than only paying for feasibility.

That is two amendments now (family-level object in Round 1, orientation-isolating intervention here). Per the rules I flag that a third would signal the original framing was wrong. I do not think we are there: the object survived unchanged and the readout is now identifiable by construction. But the reproduction keystone remains NOT_INSPECTED and genuinely uncertain, and I am not claiming otherwise.

**Status:** OPEN — the amendment implements the critic's stated first condition (orientation isolation with a norm-matched isotropic-density sham and an in-distribution gate). It stands or falls on whether the critic accepts that band-limited angular/radial spectral separation genuinely isolates orientation from isotropic density and geometry, and that the in-distribution gate adequately blocks the OOD-artifact alternative.

## Round 3 — CRITIC

**Position:** The spectral amendment preserves the original question in words, but its intervention manipulates angular Fourier power rather than validated trabecular thickening and rarefaction, so a positive response still would not identify the named biological architecture.

**Argument:** Holding the DC term and radially averaged power fixed does separate one image statistic—angular spectral anisotropy—from isotropic spectral energy, and that is a real improvement over concept-direction erasure. It does not, however, make the edited image a counterfactual of the same bone with altered load-path architecture. Fourier power discards phase and therefore does not determine trabecular connectivity, plate/rod organization, thickness, spacing, or where oriented structures meet the cortical boundary; reallocating angular power can introduce coherent ringing, directional blur, or boundary discontinuities while matching the proposed anisotropy ratio and radial profile. The Stage-0 gates do not close this gap: falling inside the marginal empirical ranges of two summary statistics is not evidence that their joint spatial realization is anatomically plausible, and a zero-change round trip tests pipeline fidelity rather than artifacts created by a nonzero angular reallocation. Nor is an equal-L2 isotropic edit a sufficient sham, because CNN responses depend strongly on perturbation morphology and frequency orientation, not only norm. Thus a selective score change would establish at most that the reproduced models respond to angular power in the medial-tibial ROI. It would not support the deliverable sentence that they use “directional thickening and rarefaction of the load-bearing bone,” which is the independently measurable X defined by fractal-signature bone literature. The identity check therefore fails at the estimand level: the revised experiment answers a narrower synthetic spectral-cue question unless angular-power edits are independently shown to track genuine trabecular architectural changes. This is not a repetition of the Round 2 collinearity objection; density and geometry may be numerically held fixed while the manipulated object still lacks biological validity.

**What would change my mind:** On an independent paired radiograph–3D bone-imaging dataset (micro-CT, HR-pQCT, or another validated structural reference), show that the exact edit produces prescribed changes in orientation-specific trabecular thickness/spacing or fractal signature while preserving connectivity, non-directional texture, cortical boundaries, and acquisition appearance within preregistered tolerances; additionally, show that blinded real-versus-edited discrimination by an acquisition-matched detector is at chance or within an equivalence margin for every edit magnitude used. A validated generative counterfactual conditioned on those same structural measurements could satisfy the same requirement. Without such validation, narrow the rung-3 sentence to “the models use angular band-power anisotropy in the subchondral ROI,” which would be a separate, weaker candidate.

**Status:** OPEN

