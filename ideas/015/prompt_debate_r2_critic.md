You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/015
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
- **idea-014** [PAUSED/DEBATED/baseline] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- **idea-015** [SHORTLISTED/CRITIQUED/baseline] -- A breast-cancer risk model may be reading the arteries as a vascular clock
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


===== ideas/015/README.md =====
# Idea 015: A breast-cancer risk model may be reading the arteries as a vascular clock

Selected from scouting cycle 007, candidate 2.


===== ideas/015/critique.md =====
# Critique — Idea 015: A breast-cancer risk model may be reading the arteries as a vascular clock

```
FATAL OBJECTION: NONE — but the card mis-states its keystone (it treats cohort/BAC-tool
  availability as the gate) and over-claims its endpoint ("vascular clock/vascular-age"),
  which the proposed design cannot reach.
EVIDENCE: Radiology:AI ryai.240417 (Mirai+EMBED feature-centric XAI, calcification features
  drive Mirai) — uncited; Mirai README (4-view Hologic "For Presentation" only); the "use"
  question needs no cancer-outcome labels, which the card never notices.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

## What the question actually is, and what survives

The interesting, physician-legible core is real: **does Mirai's risk output respond to
breast arterial calcification (BAC) — the coarse, linear, tram-track medial calcium in
mammary arteries — as opposed to only the fine clustered microcalcification that signals
malignancy?** That is a Mode-B "unasked question" in the true sense: the two things that
should connect (a cardiovascular-disease imaging marker and a breast-cancer risk score
computed on the same pixels) have not been connected in print.

I verified the surrounding literature and the core survives adversarial checks on novelty,
circularity, and data existence. It does **not** survive as currently written on
identifiability wording and endpoint honesty. Both are repairable inside the same question.

## Novelty — survives, but the card is missing its closest prior work

The card's three citations are thin and one is nearly the wrong warning. The genuinely
threatening prior work, **not cited**, is:

- **Using Explainable AI to Characterize Features in the Mirai Model**, *Radiology: AI*,
  DOI 10.1148/ryai.240417. A feature-centric XAI pipeline over Mirai's 512 features on
  **29,374 EMBED screening exams (2013–2020)**. It selected 18 calcification features
  ("CalcMirai") and 18 mass features ("MassMirai") and showed Mirai implicitly learned
  **calcification** features for risk. This is the same model *and* the same cohort (EMBED)
  the idea proposes, and it already establishes "Mirai keys on calcification."

- The card's own cite arXiv:2606.26431 (*Revealing Mammographic Phenotypes…*): I read the
  abstract. Its risk-linked phenotypes are **dense tissue, microcalcifications, and clip
  artifacts** — no arteries, no vascular/medial calcification. The card's fear that this
  preprint "may already touch BAC" is unfounded for the abstract-level phenotype inventory.

**Net:** neither ryai.240417 nor 2606.26431 distinguishes *arterial* macrocalcification from
*lesion* microcalcification. The BAC-specific question is open. But ryai.240417 **sharpens the
central confound**: Mirai demonstrably uses "calcification" broadly, so any BAC effect must be
shown to be more than "Mirai counts benign arterial calcium among its suspicious-calcification
pixels." The revision must cite ryai.240417 and frame the delta as *arterial-vs-lesion
calcification*, not *does Mirai use calcification* (answered: yes).

## The keystone is misidentified

The card names the keystone as "an executable BAC quantifier transfers to Mirai-compatible
four-view mammograms with enough BAC-positive cases and age/density overlap." Two problems.

1. **The BAC tool is less of a gate than claimed.** Public BAC segmenters with code/weights
   exist — e.g. `github.com/dominicmaguire/bac-model-code` (Maguire 2025) and SCU-Net
   (medRxiv 2021.07.30.21261406). So "a transferable BAC quantifier exists" is close to
   INSPECTED_TRUE; residual transfer risk is real but modest.

2. **The load-bearing fact the card walks past:** the question *"does Mirai use BAC"* is
   answered by measuring **Mirai's own risk-score change under a BAC intervention** — it does
   **not require future-cancer outcome labels at all.** The card imports EMBED-style outcome
   linkage and screening-cohort requirements it does not need for rung 1. This both relaxes
   data (any obtainable four-view FFDM set with BAC present suffices) and re-centres the true
   keystone:

   > **Mirai runs end-to-end on the same obtainable mammograms the BAC segmenter runs on.**
   > Mirai's README requires all four **"For Presentation" Hologic** views (L/R CC/MLO) and
   > "may not properly convert dicoms from other manufacturers." EMBED is the cohort *proven*
   > compatible (ryai.240417 ran Mirai on it); mixed-vendor public sets (VinDr-Mammo) are the
   > transfer risk. That DICOM-to-Mirai-tensor + BAC-mask join is the fact that, if false,
   > makes the study impossible — and it is `NOT_INSPECTED`.

The "if I only verified the nearest checkable thing, what am I still assuming?" answer is:
*that a BAC mask computed in one image space is spatially registered to the exact PNG16 tensor
Mirai consumes, so an intervention deletes the same pixels the model reads.* State that.

## Identifiability — the design leads with its weakest instrument

The confirmatory design leads with **learning a BAC direction in Mirai's frozen embedding and
erasing it**, comparing against age/density/device directions. This is the weak version:

- BAC is strongly age-correlated (prevalence ~13%, rises steeply with age). In embedding
  space BAC and age directions will overlap; linear erasure of one degrades the other, and the
  "incremental beyond age" contrast has low power — exactly the sensitivity-limited null the
  card concedes. Direction erasure also shows only that BAC info is *linearly present and
  downstream-influential*, not that the model reads an anatomical structure.

**The stronger, and available, instrument is an image-space intervention.** You already have a
BAC segmentation mask. Inpaint/attenuate the segmented arterial calcium to local background,
re-run frozen Mirai, and measure the **paired risk-score change** — with a **sham control** that
removes an equal-area, equal-intensity *non-arterial* structure. This is spatially localized,
causal, assumption-light, and it dodges BAC-age entanglement. It is the same structural move
that let the one surviving prior candidate (idea-004) avoid labels: intervene on the image and
compare the model to itself. Make this the primary readout; demote embedding-erasure to a
secondary triangulation.

Even with the image-space test, one alternative is hard and must be stated plainly:
**lesion-mimicry.** Because Mirai provably uses calcification pixels (ryai.240417), removing
BAC may lower risk simply because benign calcium was being scored as suspicious calcium — not
because Mirai extracts *systemic vascular age*. The sham control and morphology separation
(coarse parallel tram-track vs fine pleomorphic clusters) address whether the effect is
BAC-specific, but they **do not** establish "vascular clock."

## Endpoint honesty — the deliverable sentence over-claims by one rung

The deliverable — *"Mirai is using BAC as a **vascular-age signal**"* — bundles an
interpretation the design cannot reach. The intervention can establish, at most, that
**Mirai's risk output specifically responds to breast arterial calcification** (rung 1, and
rung 2 if device/site controls hold). Calling it a *vascular clock / vascular-age signal*
asserts the model extracts systemic ageing, which would require showing the BAC effect tracks
an independent vascular/CVD-age axis beyond lesion-mimicry and beyond chronological age. This
is the same over-reach that got idea-007 demoted rung 3 → rung 1. Revise the deliverable to the
rung-1/2 claim; keep "vascular age" only as the named rung-3 target with its explicit
additional evidence requirement.

## Other adversarial checks (pass)

- **Circularity / leakage:** BAC is not Mirai's target; the future-cancer label is not printed.
  Passes. One real shortcut: **biopsy clips / CAD overlays** — ryai.240417 and 2606.26431 both
  found clip artifacts as risk phenotypes, so exclusion of prior-intervention markers is
  mandatory, as the card notes.
- **Compute:** Mirai inference on hundreds–few-thousand exams is a single-GPU afternoon. Passes.
- **Dies-like-prior:** does not repeat the annotation-provenance kills (BAC is computed, not
  annotator-rated) nor CIRCULARITY. Correct.
- **Data DUA:** EMBED is the compatible cohort but is credentialed/registration-gated; the
  charter forbids *unconfirmed* DUA-gated dependence. Stage 0 must confirm access terms, or
  identify a four-view Hologic "For Presentation" public alternative — noting Mirai's
  manufacturer sensitivity rules out casual substitution.

## Negative-result value

The card's "sensitivity-limited (2)" is correct **for the erasure design**. The image-space
sham-controlled intervention raises it: if deleting BAC moves Mirai's risk no more than the
matched sham deletion, that is a reasonably **decisive** "Mirai does not specifically use BAC,"
provided the BAC-positive sample clears a prespecified minimum-detectable-effect. Power is the
only threat (BAC sparse), so a prespecified MDE / equivalence margin is required to earn a 3.

## Required revisions before advancement

1. Cite ryai.240417; reframe novelty delta as **arterial vs lesion calcification**.
2. Make the **image-space BAC-inpainting intervention with a matched sham** the primary
   readout; demote embedding-direction erasure to secondary.
3. Reset the keystone to **Mirai-DICOM compatibility + spatial registration of the BAC mask to
   Mirai's input tensor** on an *obtainable, confirmed-compatible* cohort; drop the unneeded
   cancer-outcome/screening-linkage requirements for the rung-1 question.
4. Rewrite the deliverable sentence to the rung-1/2 claim ("Mirai's risk responds specifically
   to breast arterial calcification"); keep "vascular-age" as the labelled rung-3 target only.
5. Stage 0: confirm EMBED (or alternative) access terms and BAC prevalence in the usable sample.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does inpainting the segmented breast arterial
calcification out of a four-view mammogram change frozen Mirai's five-year risk score more than
a matched sham deletion of equal-area non-arterial calcific structure?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — keeps "a breast-cancer model responds to a
cardiovascular imaging marker"; drops the unearned "reads systemic vascular age" interpretation.
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is the same question done more identifiably; it
is the revision, not a fork.
IS IT ACTUALLY WORTH DOING? Yes — a clean, label-free, single-GPU causal test on public tools
(Mirai + a public BAC segmenter) that would tell radiologists whether a widely evaluated risk
score is partly reading benign vascular calcium, provided Stage 0 confirms the Mirai-cohort and
BAC-mask registration join.
```


===== ideas/015/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed repair no longer answers the original question: BAC-pixel sensitivity is not evidence that Mirai uses BAC as a vascular-age signal independently of chronological age and breast density.

**Argument:** The card's original claim is mechanistic and conditional—Mirai reads medial arterial calcium *as systemic vascular age*, beyond age and density—whereas the revised primary experiment only compares frozen Mirai scores after BAC inpainting versus a matched sham. A positive paired score change would establish, at most, that pixels selected by a BAC segmenter affect the score. It cannot distinguish the original vascular-clock explanation from the closest prior-supported alternative: Mirai treats coarse arterial calcium as generic calcification evidence or lesion-like microcalcification. That alternative is especially live because the same-model EMBED study, *Using Explainable AI to Characterize Features in the Mirai Model* (Radiology: AI, DOI 10.1148/ryai.240417), already reports calcification-feature reliance. Age matching does not repair this identity break: it controls chronological age but supplies no independent measurement of vascular age, and an equal-area/equal-intensity non-arterial edit tests edit specificity rather than whether the BAC effect encodes systemic vascular ageing. The defensible replacement sentence—"Mirai's risk output responds specifically to breast arterial calcification"—is useful, but it is a different rung-1 question and should be spawned as a separate candidate unless the title, question, and claimed endpoint are formally narrowed.

**What would change my mind:** Show a design with an independently computed vascular-age endpoint (for example, a validated cardiovascular-risk or arterial-age measure unavailable to Mirai), demonstrate that the BAC-dependent component of Mirai's score tracks that endpoint within narrow chronological-age and density strata, and include an intervention that isolates arterial BAC from matched parenchymal calcification; otherwise re-register the project as the narrower BAC-sensitivity candidate.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The inpainting-vs-sham design can show that BAC pixels move Mirai's score, but it cannot show that Mirai reads them *as systemic vascular age* rather than as generic or lesion-like calcification — especially given ryai.240417 already established calcification-feature reliance. So either the candidate acquires an independent vascular-age endpoint, or it must formally narrow its title, question, and claimed endpoint to the BAC-sensitivity claim; and the critic leans toward the narrowed version being a separate candidate.

**Response:** AMEND

**Argument:** The critic is right that no design available here identifies vascular-age encoding, and I am not going to pretend one is. The independent endpoint the critic asks for — a cardiovascular-risk or arterial-age measure unavailable to Mirai, linked to the same mammograms — does not exist in any cohort we can currently confirm: EMBED has cancer outcomes and demographics, not cardiovascular linkage, and no public four-view FFDM set carries CAC scores or CVD outcomes. Rung 3 as originally worded is therefore out of reach on obtainable data, not merely unproven. I take the critic's second branch: formal narrowing, which the critic's own position statement allows ("unless the title, question, and claimed endpoint are formally narrowed").

The card changes as follows:

- **Title:** "A breast-cancer risk model may be reading the arteries" — the words "as a vascular clock" are deleted.
- **Question:** "Does frozen Mirai's five-year risk score respond specifically to breast arterial calcification — beyond matched benign parenchymal calcification, chronological age, and breast density — on the same four-view mammograms?"
- **Deliverable sentence:** "Mirai's breast-cancer risk output responds specifically to breast arterial calcification — the linear tram-track calcium in mammary arteries — and not merely to calcification in general."
- **Rung target:** 2, down from 3. "Vascular-age signal" moves to an explicitly labelled rung-3 extension with its named missing instrument: a cardiovascular endpoint (CAC, MESA-style arterial-age, or CVD outcome linkage) joined to a Mirai-compatible mammography cohort. Until such a linkage is confirmed to exist, that extension is aspirational and unclaimed.
- **Primary readout, sharpened to meet the critic's third demand:** paired BAC inpainting against *two* shams — (a) deletion of matched benign parenchymal calcification of equal conspicuity within the same age/density stratum, and (b) deletion of equal-area non-calcific linear structure. Sham (a) is precisely the intervention the critic asked for to isolate arterial from parenchymal calcification. One point of partial disagreement: the critic characterizes the sham arm as testing only "edit specificity." With sham (a) in place it does more — if BAC deletion moves the score significantly more than deletion of equally conspicuous benign parenchymal calcium, the "generic calcification evidence" alternative from ryai.240417 is directly weakened, which is exactly the arterial-vs-lesion delta the critique identified as the open novelty. That is a real discrimination, not just edit hygiene. What it still cannot do is elevate the finding to vascular age, and the amended endpoint no longer says it does.

**Identity check.** Does the amended design still answer the original one-sentence question? Not the full sentence: the clause "as a vascular-age signal" is abandoned, not deferred-and-answered. But the charter's deliverable requirement is "the model is using X, where X is a named anatomical, physiological, or physical thing" — and X = breast arterial calcification satisfies that in full. The vascular-clock wording was a mechanistic interpretation layered on top of the charter-level claim, and the card's own rung ladder already gated everything through BAC-specific erasure before any vascular-age assertion. This is the idea-007 situation (rung 3 → rung 1/2 demotion in place, same candidate), not the idea-003 situation (feasibility achieved by abandoning the motivating intervention). The motivating observation — a breast-cancer score and a cardiovascular imaging marker computed from the same pixels, never connected in print — survives intact.

**Why not a fork:** the narrowed candidate shares the original's keystone (Mirai-tensor/BAC-mask registration on a compatible cohort), assets, cohort, confounds, and medical motivation; the critique already answered "SHOULD IT BECOME A SEPARATE CANDIDATE? NO." A fork would duplicate a ledger entry without changing a single experiment.

**What is lost, plainly:** the headline. "A breast model found a vascular clock" was a rung-3 mechanism claim and the most interesting sentence in the card; it is gone unless a cardiovascular linkage materializes. Interest drops from 5 to 4. What remains is still consequential and physician-legible: if a widely evaluated risk model's output is partly driven by benign arterial calcium, then women with vascular disease receive inflated breast-cancer risk estimates — a calibration and equity finding that stands on its own. Amendment count: one.

**Status:** OPEN


===== ideas/015/idea_card.json =====
{
  "id": "C2",
  "parent_ids": [],
  "revival_basis": null,
  "search_mode": "B",
  "entry_point": 2,
  "title": "A breast-cancer risk model may be reading the arteries as a vascular clock",
  "question": "Is Mirai using breast arterial calcification as a vascular-age signal in its five-year breast-cancer risk prediction, independently of breast density and chronological age?",
  "rung": {
    "target": 3,
    "current": 0,
    "move_up": "Automated BAC association is exploratory; validation-learned BAC-direction erasure with age/density/device controls reaches rung 1; external-device replication gates rung 2 and the named BAC claim at rung 3."
  },
  "deliverable_sentence": "Mirai is using breast arterial calcification\u2014the linear tram-track calcium in mammary arteries\u2014as a vascular-age signal in breast-cancer risk prediction.",
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
    {
      "citation": "Yala et al., Towards Robust Mammography-Based Models for Breast Cancer Risk",
      "identifier": "official code https://github.com/reginabarzilaygroup/Mirai; primary model paper linked there",
      "verified_fact": "Mirai predicts annual risk to five years and releases inference code/weights under MIT.",
      "delta": "The repository/paper does not establish whether BAC drives risk."
    },
    {
      "citation": "Mobini et al., Deep transfer learning for detection of breast arterial calcifications",
      "identifier": "PMCID PMC11247067",
      "verified_fact": "BAC is machine-detectable on four-view mammograms.",
      "delta": "It detects BAC; it does not test Mirai or breast-cancer risk-model reliance."
    },
    {
      "citation": "Revealing Mammographic Phenotypes in Deep Learning Breast Cancer Risk Models",
      "identifier": "arXiv:2606.26431",
      "verified_fact": "A 2026 preprint clusters Mirai patch embeddings into risk-linked phenotypes.",
      "delta": "This is the closest warning against novelty: the exact phenotype inventory must be inspected for BAC before advancement."
    }
  ],
  "existing_assets": [
    "Mirai code and weights (MIT)",
    "Four-view public mammography resources such as EMBED, subject to their actual access terms",
    "Published BAC segmentation methods"
  ],
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
    {
      "alternative": "BAC merely indexes chronological age.",
      "resolution": "Age-matched strata and separate age-direction erasure; require BAC-specific incremental effect."
    },
    {
      "alternative": "BAC pixels resemble suspicious calcifications.",
      "resolution": "Spatial BAC mask, morphology separation, and comparison with parenchymal-calcification direction."
    },
    {
      "alternative": "Vendor processing creates both BAC visibility and risk shifts.",
      "resolution": "Within-device analysis and external device replication; unresolved without both."
    }
  ],
  "anticipated_negative": {
    "classification": "sensitivity-limited",
    "reason": "BAC may be sparse and nonlinear in embeddings; a null is decisive only above preregistered BAC-probe AUROC/reliability and prevalence gates."
  },
  "cross_domain": null,
  "remaining_legwork": "1 day to inspect the 2026 phenotype preprint; 3 days to locate/test an executable BAC quantifier; up to 1 week for compatible mammography access. First go/no-go in 1-2 weeks.",
  "scores": {
    "clarity": {
      "value": 5,
      "why": "Specific model, visible quantity, and rival age/density explanations."
    },
    "identifiability": {
      "value": 3,
      "why": "Concept erasure plus age/device controls is plausible, but BAC-age entanglement and internal-intervention specificity remain."
    },
    "medical_relevance": {
      "value": 4,
      "why": "Changes interpretation of a widely evaluated risk score and may expose systemic rather than breast-specific signal."
    },
    "interest": {
      "value": 5,
      "why": "A breast model reading vascular disease is surprising and physician-legible."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Open Mirai and mature BAC detection work exist."
    },
    "feasibility": {
      "value": 3,
      "why": "Capped; BAC tool/corpus join is uninspected."
    },
    "data_readiness": {
      "value": 3,
      "why": "Potential public resources exist but exact access and presentation-view compatibility need inspection."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "BAC metrics exist; erasure selectivity must be calibrated."
    },
    "negative_result_value": {
      "value": 2,
      "why": "Sensitivity-limited null."
    },
    "novelty_confidence": {
      "value": 2,
      "why": "A very recent Mirai phenotype preprint may already touch the signal and has not yet been fully inspected."
    },
    "regret": {
      "value": 4,
      "why": "Cheap once the BAC quantifier and compatible images are joined."
    }
  },
  "priority_score": 3.6,
  "priority_arithmetic": "0.20*3 + 0.15*3 + 0.15*4 + 0.10*4 + 0.10*5 + 0.10*5 + 0.10*2 + 0.05*3 + 0.05*2 = 3.60",
  "unverified_claims": [
    "An open BAC segmenter with weights transfers to Mirai inputs",
    "EMBED or another obtainable set has adequate BAC prevalence and outcomes",
    "arXiv:2606.26431 does not already test BAC"
  ],
  "track": "baseline"
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
You are claude. Your interlocutor is codex.
This is round 2. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed repair no longer answers the original question: BAC-pixel sensitivity is not evidence that Mirai uses BAC as a vascular-age signal independently of chronological age and breast density.

**Argument:** The card's original claim is mechanistic and conditional—Mirai reads medial arterial calcium *as systemic vascular age*, beyond age and density—whereas the revised primary experiment only compares frozen Mirai scores after BAC inpainting versus a matched sham. A positive paired score change would establish, at most, that pixels selected by a BAC segmenter affect the score. It cannot distinguish the original vascular-clock explanation from the closest prior-supported alternative: Mirai treats coarse arterial calcium as generic calcification evidence or lesion-like microcalcification. That alternative is especially live because the same-model EMBED study, *Using Explainable AI to Characterize Features in the Mirai Model* (Radiology: AI, DOI 10.1148/ryai.240417), already reports calcification-feature reliance. Age matching does not repair this identity break: it controls chronological age but supplies no independent measurement of vascular age, and an equal-area/equal-intensity non-arterial edit tests edit specificity rather than whether the BAC effect encodes systemic vascular ageing. The defensible replacement sentence—"Mirai's risk output responds specifically to breast arterial calcification"—is useful, but it is a different rung-1 question and should be spawned as a separate candidate unless the title, question, and claimed endpoint are formally narrowed.

**What would change my mind:** Show a design with an independently computed vascular-age endpoint (for example, a validated cardiovascular-risk or arterial-age measure unavailable to Mirai), demonstrate that the BAC-dependent component of Mirai's score tracks that endpoint within narrow chronological-age and density strata, and include an intervention that isolates arterial BAC from matched parenchymal calcification; otherwise re-register the project as the narrower BAC-sensitivity candidate.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The inpainting-vs-sham design can show that BAC pixels move Mirai's score, but it cannot show that Mirai reads them *as systemic vascular age* rather than as generic or lesion-like calcification — especially given ryai.240417 already established calcification-feature reliance. So either the candidate acquires an independent vascular-age endpoint, or it must formally narrow its title, question, and claimed endpoint to the BAC-sensitivity claim; and the critic leans toward the narrowed version being a separate candidate.

**Response:** AMEND

**Argument:** The critic is right that no design available here identifies vascular-age encoding, and I am not going to pretend one is. The independent endpoint the critic asks for — a cardiovascular-risk or arterial-age measure unavailable to Mirai, linked to the same mammograms — does not exist in any cohort we can currently confirm: EMBED has cancer outcomes and demographics, not cardiovascular linkage, and no public four-view FFDM set carries CAC scores or CVD outcomes. Rung 3 as originally worded is therefore out of reach on obtainable data, not merely unproven. I take the critic's second branch: formal narrowing, which the critic's own position statement allows ("unless the title, question, and claimed endpoint are formally narrowed").

The card changes as follows:

- **Title:** "A breast-cancer risk model may be reading the arteries" — the words "as a vascular clock" are deleted.
- **Question:** "Does frozen Mirai's five-year risk score respond specifically to breast arterial calcification — beyond matched benign parenchymal calcification, chronological age, and breast density — on the same four-view mammograms?"
- **Deliverable sentence:** "Mirai's breast-cancer risk output responds specifically to breast arterial calcification — the linear tram-track calcium in mammary arteries — and not merely to calcification in general."
- **Rung target:** 2, down from 3. "Vascular-age signal" moves to an explicitly labelled rung-3 extension with its named missing instrument: a cardiovascular endpoint (CAC, MESA-style arterial-age, or CVD outcome linkage) joined to a Mirai-compatible mammography cohort. Until such a linkage is confirmed to exist, that extension is aspirational and unclaimed.
- **Primary readout, sharpened to meet the critic's third demand:** paired BAC inpainting against *two* shams — (a) deletion of matched benign parenchymal calcification of equal conspicuity within the same age/density stratum, and (b) deletion of equal-area non-calcific linear structure. Sham (a) is precisely the intervention the critic asked for to isolate arterial from parenchymal calcification. One point of partial disagreement: the critic characterizes the sham arm as testing only "edit specificity." With sham (a) in place it does more — if BAC deletion moves the score significantly more than deletion of equally conspicuous benign parenchymal calcium, the "generic calcification evidence" alternative from ryai.240417 is directly weakened, which is exactly the arterial-vs-lesion delta the critique identified as the open novelty. That is a real discrimination, not just edit hygiene. What it still cannot do is elevate the finding to vascular age, and the amended endpoint no longer says it does.

**Identity check.** Does the amended design still answer the original one-sentence question? Not the full sentence: the clause "as a vascular-age signal" is abandoned, not deferred-and-answered. But the charter's deliverable requirement is "the model is using X, where X is a named anatomical, physiological, or physical thing" — and X = breast arterial calcification satisfies that in full. The vascular-clock wording was a mechanistic interpretation layered on top of the charter-level claim, and the card's own rung ladder already gated everything through BAC-specific erasure before any vascular-age assertion. This is the idea-007 situation (rung 3 → rung 1/2 demotion in place, same candidate), not the idea-003 situation (feasibility achieved by abandoning the motivating intervention). The motivating observation — a breast-cancer score and a cardiovascular imaging marker computed from the same pixels, never connected in print — survives intact.

**Why not a fork:** the narrowed candidate shares the original's keystone (Mirai-tensor/BAC-mask registration on a compatible cohort), assets, cohort, confounds, and medical motivation; the critique already answered "SHOULD IT BECOME A SEPARATE CANDIDATE? NO." A fork would duplicate a ledger entry without changing a single experiment.

**What is lost, plainly:** the headline. "A breast model found a vascular clock" was a rung-3 mechanism claim and the most interesting sentence in the card; it is gone unless a cardiovascular linkage materializes. Interest drops from 5 to 4. What remains is still consequential and physician-legible: if a widely evaluated risk model's output is partly driven by benign arterial calcium, then women with vascular disease receive inflated breast-cancer risk estimates — a calibration and equity finding that stands on its own. Amendment count: one.

**Status:** OPEN

