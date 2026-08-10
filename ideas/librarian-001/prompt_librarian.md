You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/librarian-001
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
- **IDENTIFIABILITY_FAILURE** x1: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.

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
- **idea-015** [SHORTLISTED/DEBATED/baseline] -- A breast-cancer risk model may be reading the arteries as a vascular clock
- **idea-016** [REJECTED/DEBATED/baseline] -- The PE model may read contrast flowing backward as a pressure gauge -- killed: IDENTIFIABILITY_FAILURE
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


===== ideas/librarian-001/dossier.md =====
# Librarian dossier (auto-generated)

## idea-001 [REJECTED/DEBATED]
- title: Have lung nodule concept models been validated against radiologist opinion rather than against disease?
- question: Do the nine LIDC-IDRI semantic nodule attributes predict pathology-confirmed malignancy as well as they predict the radiologist-assigned malignancy rating that the entire LIDC concept literature uses as its endpoint?
- dataset: {"primary": "LIDC-IDRI via The Cancer Imaging Archive", "license": "CC BY 3.0", "access": "Public download via TCIA Data Retriever. No DUA identified on the collection page.", "key_files": ["LIDC-XML-only.zip (per-reader nodule characteristic ratings)", "tcia-diagnosis-data-2012-04-20.xls (patient- and nodule-level diagnosis, ~45 KB)"], "size_constraint": "The pathology-confirmed subset
- KILLED: DATA_INSUFFICIENT -- Zinovev et al. 2012, J Digit Imaging 25:423-436 (DOI 10.1007/s10278-011-9445-3) VERIFIED by reading the paper: diagnosis file is patient-level, numbering inconsistent with LIDC XML, only 18 nodules reliably linked (8 mal / 9 ben / 1 indet) via single-nodule-patient restriction. Too small for the pro
### Recommendation
**REJECT** — before deciding whether to reopen, the human should look for a publicly released or independently validated diagnosis-to-XML-nodule mapping that retains all eight semantic ratings, then verify *before model fitting* that its independently confirmed benign and malignant counts meet a prespecified CI-width target. Without that artifact, the proposed experiment cannot support its intended inference.
### Unresolved
### Does a suitable diagnosis-to-XML-nodule mapping already exist? - **Proposer's position:** No suitable mapping was verified in the search performed, but failure to find one is not evidence that none exists. - **Critic's position:** Claims of larger strongly labelled cohorts do not resolve feasibility unless they supply an auditable nodule-level mapping that retains all eight XML ratings. - **Evidence that would settle it:** A publicly released or independently validated mapping, accompanied by an auditable linkage method and independently verified benign and malignant counts. Its counts must satisfy a prespecified confidence-interval-width target before modeling. There is no remaining disagreement about the present disposition. The empirical question—whether the eight LIDC semantic attributes predict independently confirmed disease as well as radiologist malignancy suspicion—remains unanswered because both sides agree that the currently verified linkage cannot test it.
### Amendments made
At round zero, the idea claimed that a public LIDC pathology endpoint could be linked to the same nodules carrying eight semantic ratings, enabling a quick paired comparison between prediction of radiologist suspicion and prediction of disease. It described the endpoint as pathology-confirmed malignancy, proposed nested cross-validation and paired AUCs, treated a small gap as evidence licensing endpoint substitution, assigned a 4.45/5 priority score, and recommended `SHORTLIST`. The final position withdraws that study. The endpoint is more accurately “confirmed clinical diagnosis,” but the released records have no verified, sufficiently large, auditable mapping to specific XML nodules. A recount under one rule is not a linkage ceiling, manual matching lacks adequate validation, and an imprecise null cannot validate endpoint substitution. The linkage check survives only as an internal reopening gate, not as the scientific deliverable. Lost from the original idea are the one-experiment concept-validity story, the claimed high value of either outcome, the strong novelty framing, and the expectation of an immediately feasible CPU-only study. The agreed card updates are `recommendation: REJECT`, priority score 2.85/5, reduced negative-result value and novelty confidence, and an unverified-claims entry recording Zinovev et al.'s 18-nodule result as the governing prior evidence. The underlying medical question and the unpromoted endpoint-practice spin-off remain, but neither is an active revision of this idea.

## idea-002 [PAUSED/DEBATED]
- title: Dermoscopic concepts predicted from non-dermoscopic photographs: genuine visibility or shortcut?
- question: Can a model predict the seven dermoscopic checklist criteria from Derm7pt's paired clinical photographs — where those criteria are by definition not visible — and if it can, does the ability survive controls that remove lesion-identity shortcuts?
- dataset: {"primary": "Derm7pt paired clinical/dermoscopic images", "source": "github.com/gnapoles/Consistent-Derm7pt (bundled) or github.com/jeremykawahara/derm7pt (original)", "access": "Public; metadata MIT, images CC BY-NC-ND 4.0", "access_risk": "Low", "verification": "verified_by_primary_fetch of the repository page"}
### Recommendation
**PAUSE** — the single most important thing for the human to inspect is the original annotation protocol, specifically whether checklist scorers could see the paired clinical photograph or other clinical information. Until that is resolved, the surviving experiment has irreducibly ambiguous value; if exposure to both images is confirmed, stop at a short documentation finding rather than train an image model.
### Unresolved
### What information was available when checklist labels were assigned? - **Question:** Were the seven checklist criteria scored from dermoscopic images alone under modality blinding, or could annotators see clinical photographs or other clinical information? - **Proposer's position:** The accessible primary sources inspected do not answer this. The ambiguity cannot be resolved from Derm7pt's observed associations, so a written enquiry is a prerequisite. If the scorer saw both images, the image experiment should stop and the result should be limited to a documentation note. - **Critic's position:** Image training should not proceed without provenance because a positive result otherwise has two materially different explanations. If provenance cannot be recovered, only a descriptive dataset-label audit or an independently blinded rescoring study is defensible. - **What evidence would settle it:** A primary annotation manual, the original Atlas/database protocol, or written confirmation from the dataset or Atlas creators specifying the annotator's information access. A new blinded rescoring study could establish properties of newly constructed labels, but would not by itself recover the original annotation procedure. ### Is the narrower audit novel enough to justify a study? - **Question:** Has prior work already compared diagnosis/metadata-only prediction with diagnosis/metadata-plus-clinical-image prediction for Derm7pt checklist labels? - **Proposer's position:** Novelty is unverified and must not be claimed; the papers inspected do not settle the question. - **Critic's pos
### Amendments made
At round zero, the idea claimed that a missing clinical-versus-dermoscopic ablation could decide whether named dermoscopic criteria predicted from clinical photographs were genuinely visible or merely diagnosis shortcuts. It treated the paired design as isolating imaging medium, used diagnosis-only performance as the decisive causal control, asserted useful interpretations in either direction, and scored the project at 4.25. The amended idea is a much narrower Derm7pt dataset-label audit. Its one-directional question is whether clinical photographs show evidence of dependence with recorded checklist labels after conditioning primarily on grouped diagnosis. The proposed statistic is cross-validated log-loss improvement from adding frozen, label-free image features to a locked diagnosis model, calibrated by within-diagnosis image permutations. Diagnosis × coarsened site is only a secondary analysis because richer metadata strata become too sparse. A rejection would establish dependence under the test's assumptions, while the reported magnitude remains model- and metric-conditional; non-rejection is inconclusive and must be accompanied by achieved-power or minimum-detectable-effect results. Lost from the original idea are the modality-ablation novelty, causal shortcut diagnosis, proof of named-feature visibility or grounding, the teledermatology payoff, conditioning on the full recorded metadata set, an informative interpretation for both outcome directions, and the original priority score. Even a valid rejection remains compatible with annotation exposure, age/site/provenance

## idea-003 [ACTIVE/DEBATED]
- title: Does BI-RADS concept intervention survive realistic clinician behaviour, and does it beat simply reading the BI-RADS category?
- question: Does the reported gain from radiologist concept intervention in a breast ultrasound concept bottleneck model persist when interventions are partial, noisy, and clinician-selected rather than complete and oracle-correct, and does the intervened model outperform the trivial baseline of using the radiologist's own BI-RADS assessment directly?
- dataset: {"primary": "BUS-BRA (Zenodo 8231412, CC BY 4.0) for the external and baseline arms", "secondary": "BUSI (public) as an additional external set", "unavailable": "The authors' own 8,854-image development cohort is not public, so their exact model cannot be reproduced end to end; only their released code and architecture can be reused with retraining.", "access_risk": "Moderate. The datas
### Recommendation
**REJECT.** The current public-data plan cannot answer the motivating intervention question, and the successive defensible amendments produced a different prediction-rule benchmark. Before deciding whether to revive the intervention idea, the human should look first for a directly verified public dataset or checkpoint that supports image-predicted BI-RADS descriptors and observable pre/post-intervention evaluation; without that asset, further design refinement will not repair the core feasibility gap.
### Unresolved
### Does a suitable public intervention dataset or checkpoint exist but remain unidentified? - **Question:** Is there a public resource with image-level BI-RADS descriptors and adequate outcomes that supports image-predicted concepts and observable pre/post-intervention policies, ideally with reader corrections or disagreements? - **Proposer's position:** No such resource was identified, so the original question is not presently answerable; this is explicitly not a claim that no such resource exists (round 6). - **Critic's position:** The intervention claim could be restored if such a feasible public-data experiment were identified and its sample size and concept-label quality shown adequate (round 5). - **What evidence would settle it:** A focused primary-source and repository search yielding a publicly accessible dataset, usable checkpoint, or reader study with the required descriptor, outcome, and intervention/correction information, followed by direct inspection of its files, license, patient independence, label provenance, and sample counts. A search finding nothing would justify pausing on current evidence, but would not prove global nonexistence. ### Are the factual prerequisites for the separate BrEaST benchmark satisfied? - **Question:** Does the released case table confirm that every malignant case is biopsy verified, and is the relevant Bunnell concept-to-label head actually linear as assumed in round 4? - **Proposer's position:** The primary data descriptor supports the claimed counts and verification pattern, but the released XLSX cross-tabulation and exact hea
### Amendments made
At round zero, Idea 003 claimed it could test whether BI-RADS concept intervention remains useful under partial, noisy, clinician-selected correction and whether it beats the radiologist's BI-RADS category, using a retrained breast-ultrasound CBM and public data. The first amendment replaced that intervention experiment with a BrEaST descriptor-versus-category analysis centered on the biopsy-verified subset, with the mixed-reference full cohort relegated to sensitivity analysis. This lost applicability to an unselected diagnostic population, reduced power, and abandoned the claim of a decisive upper bound. The second amendment further narrowed the study to a comparison of prespecified prediction rules on BrEaST. It removed claims about representation information, added multiple decoders and learning-curve safeguards, and made any downstream stopping rule difficult to trigger. This lost most of the original screening power and broader generalizability. The final concession recognized that even this amended study does not evaluate intervention. The original idea is therefore not merely revised: it is rejected. The remaining BrEaST benchmark is a different candidate and must not inherit Idea 003's title, intervention rationale, scores, or claimed negative-result value.

## idea-004 [ACTIVE/DEBATED]
- title: The free test-retest experiment already inside CT-RATE: duplicate reconstructions of the same acquisition
- question: When the same chest CT acquisition is reconstructed twice, how much does a released chest-CT foundation model's predicted abnormality concept change, and does the CT-RATE validation benchmark's per-volume unit of analysis overstate the precision of every number reported on it?
- keystone_prerequisite: CT-RATE contains more than one reconstruction of the same acquisition (same patient, same scan), and those pairs are identifiable from released filenames or metadata without needing the raw sinograms - so that paired volumes with identical underlying anatomy exist and can be found.
- keystone_status: INSPECTED_TRUE
### Recommendation
**REVISE.** The debate converged on a defensible design, but the current idea card still contains claims and scores that the debate explicitly withdrew. Before deciding whether to advance to a feasibility memo, the human should look first at the direct Stage 0 metadata counts—especially the number and parameter makeup of geometry-matched same-acquisition pairs—because that single inspection determines whether the stronger reconstruction-content study exists or only the narrower composite pipeline audit remains.
### Unresolved
There is no remaining proposer–critic disagreement about the revised design. The unresolved items are empirical gates accepted by both sides: ### Do enough geometry-matched same-acquisition pairs exist? - **Question:** Are there enough pairs sharing slope, intercept, XY spacing, Z spacing, and array shape—and carrying interpretable reconstruction contrasts—to support the primary mechanistic stratum? - **Proposer's position:** Make this stratum primary for reconstruction-content attribution; if it is empty or too small, retain only the composite end-to-end pipeline analysis. - **Critic's position:** Accepted in Round 3 as an adequate repair to the preprocessing objection. - **Evidence that would settle it:** Direct counts and parameter comparisons in `validation_metadata.csv`, followed by a power or precision calculation for the paired endpoints. ### Are audit-independent thresholds estimable? - **Question:** Are singleton validation scans numerous enough, per output, to estimate stable operating thresholds without using the paired audit cases? - **Proposer's position:** Use singleton validation scans; fall back to training-split thresholds if the singleton group is inadequate. - **Critic's position:** Thresholds must be fixed independently of the audit pairs; this repair satisfies that requirement in principle. - **Evidence that would settle it:** Counts of singleton scans and independent positive/negative cases per output, plus prespecified threshold-estimation precision criteria. ### Are per-output analyses adequately powered? - **Question:** Do the paired data contain en
### Amendments made
- **Stage 0:** Now a metadata, linkage, provenance, access, and feasibility audit. It no longer promises a label-only design effect or a no-model estimate of confidence-interval narrowing. - **Benchmark arm:** Now requires per-volume scores, explicitly separates reconstruction-, scan-, and patient-weighted estimands, and compares row-level resampling with scan- or patient-clustered inference without prespecifying the direction of change. - **Repeatability claim:** Now concerns within-acquisition reconstruction or end-to-end pipeline repeatability, not test-retest reliability across repeated acquisitions and not general concept validity. - **Causal interpretation:** Reconstruction-content attribution is limited to adequately sized geometry-matched strata. Geometry-mismatched pairs retain a composite pipeline estimand; matched-grid transformations are secondary, asymmetrically interpreted mechanistic checks rather than definitive subtraction controls. - **Primary statistics:** Paired score-difference distributions, repeatability coefficients or upper absolute-difference quantiles, and reconstruction-swap AUROC deltas replace pooled ICC as the main evidence. Analyses are stratified by reconstruction contrast and score region and reported on declared probability/logit scales. - **Threshold analysis:** Crossing rates are secondary, with thresholds estimated away from audit pairs and outputs failing minimum-count criteria labelled exploratory. - **Negative result:** No fixed reassuring cutoff is claimed. A negative is decisive only if confidence bounds fall within a prespecified,

## idea-005 [PAUSED/DEBATED]
- title: Eight named characteristics, or three latent ones? Discriminant validity of the LIDC concept vocabulary
- question: In the radiologists' own ratings, do the eight LIDC semantic characteristics agree with themselves across readers more than they correlate with each other within a reader - and if not, how many distinct dimensions does a concept model that reports eight separate concept predictions actually have?
- keystone_prerequisite: The released XML supplies, for the same nodule, multiple readers' ratings AND multiple characteristics per reader - so that the same-characteristic-across-readers cells and the different-characteristic-within-reader cells of the matrix can both be filled from the same nodules.
- keystone_status: INSPECTED_TRUE
### Recommendation
**REJECT** the original idea as currently framed. The single most important thing for the human to inspect is whether to promote spin-off S2—the direct test of reader-slot exchangeability—into a fresh candidate, because it preserves the cheap public-data audit while avoiding the undefined dimension-count estimand.
### Unresolved
### Can a narrower pairwise latent-correlation audit be scientifically useful? - **Question:** Can the 28 characteristic pairs be classified as distinct, not distinct, or undecidable at a prespecified latent-correlation margin using exchangeable, peer-exposed LIDC ratings? - **Proposer's position:** Round 6 records this as spin-off S1. A directional equivalence procedure with simultaneous intervals and multiplicity control might answer only the pairwise half of the original question. - **Critic's position:** The critic required a mutually exclusive rule with an explicit null, direction, interval, margin, and multiplicity control, plus realistic simulations of its operating behavior (Round 5). The critic never reviewed the Round 6 sketch. - **What evidence would settle it:** Verify the primary methodological basis for the equivalence rule; directly inspect LIDC cell counts, missingness, and marginal distributions; then preregister and simulate coverage, type-I error/false declarations, power, convergence, and misspecification sensitivity for the exact ordinal correlated-uniqueness model. This would establish statistical adequacy, not the substantive truth of a chosen margin. The margin itself is partly a value judgment and requires a clinically or model-evaluation-relevant justification. ### Can a global partition estimator recover a defensible dimension count? - **Question:** Can selection over the 4,140 partitions of eight characteristics provide a validated global estimate of vocabulary dimensionality under ordinal exchangeable-rater data? - **Proposer's position:** Round
### Amendments made
At round zero, the idea claimed that a classical MTMM matrix over four reader slots could test discriminant validity, that cross-reader/cross-characteristic cells controlled within-reader halo, and that polychoric factor analysis plus parallel analysis could yield a decisive number of latent dimensions in hours. It scored feasibility 5, identifiability 4, clarity 4, and negative-result value 4. Round 2 replaced fixed readers with exchangeable raters, abandoned method-specific variance claims, and weakened the peer-exposure analysis from identification to an asymmetric falsification check. This lost causal attribution, reduced identifiability to at most 3, and made the causal negative sensitivity-limited. Round 4 replaced the erroneous reliability cutoff and factor-retention approach with a categorical correlated-uniqueness CFA, cutoff-relative latent correlations, and nested merges. This increased the expected work from hours to roughly a week, made some characteristics potentially undecidable, and made any verdict cutoff-relative. Round 6 withdrew that operationalization rather than amending it again. Consequently, **there is no surviving amended version of the original two-part study**. The pairwise equivalence audit, reader-slot exchangeability test, and partition-selection methods project are spin-offs only; each requires a fresh card and fresh scoring. The original dimension-count headline, decisive-negative claim, feasibility score, clarity score, and priority score are lost.

## idea-006 [PAUSED/DEBATED]
- title: Ask the chest-CT foundation model to diagnose a volume with no patient in it
- question: When every voxel inside the body contour is replaced with a constant and only the air, table, positioning aids and reconstruction field-of-view boundary are left, how much of the released chest-CT foundation model's abnormality AUROC survives?
- keystone_prerequisite: The released CT-RATE volumes retain the region outside the patient's body, AND the released checkpoint's own preprocessing pipeline neither masks nor crops that region away - so that a body-excluded input is both constructible and in-distribution for the model rather than an out-of-distribution image whose score means nothing. The second clause is what my inference needs: 
- keystone_status: INSPECTED_TRUE
### Recommendation
**PAUSE.** Before deciding whether the pause is reversible, the human should inspect the official CT-CLIP training data loader and augmentation configuration for large-region masking or cutout with a matching fill value. Absence would make the original intervention indefensible for this checkpoint; presence would justify distributional validation, not automatic advancement.
### Unresolved
### Did CT-CLIP training make large constant-filled occlusions sufficiently familiar? - **Question:** Did the official CT-CLIP training pipeline use large-region masking, cutout, or comparable augmentation with the same fill convention, such that body exclusion is materially less off-manifold for this checkpoint? - **Proposer's position:** This is an uninspected, concrete reopening possibility. If such augmentation was used, the keystone becomes an empirical question of degree rather than automatically false; if it was not used, the pause is effectively permanent for CT-CLIP. - **Critic's position:** The critic requires a validated intervention supported by a primary-source training rationale or direct distributional validation. The critic did not separately evaluate the newly raised possibility because it appeared after convergence. - **What evidence would settle it:** Direct inspection of the official training loader, augmentation configuration, and training methods, followed—if relevant augmentation exists—by direct validation that the proposed body-excluded inputs fall within the checkpoint's supported input distribution. Code inspection alone could rule the possibility out but would not by itself prove the intervention valid. ### Could the original question be valid for a different chest-CT model? - **Question:** Would a model pretrained with sufficiently similar large blanked regions make the original patient-removal estimand interpretable? - **Proposer's position:** Possibly; a masked-reconstruction or suitably augmented encoder may already incorporate the remedy dur
### Amendments made
The transcript identifies required changes to the card, although `idea_card.json` had not yet been updated during the debate: - Recommendation changes from `SHORTLIST` to `PAUSE`. - `keystone_status` changes from `INSPECTED_TRUE` to `NOT_INSPECTED`; the evidence now supports only exterior retention by inference preprocessing, not in-distribution body deletion. - Feasibility and novelty confidence are capped at 3 pending an inspected true keystone. - The anticipated negative changes from decisive to uninterpretable for the motivating claim, and negative-result value is capped at 2. - `dies_like_prior` no longer claims immunity from prior failure modes; it acknowledges the same wrong-keystone structure as idea 005, although the substantive issue here is intervention validity rather than annotation provenance. - The 4.10 priority score must be recomputed from the revised scores. - Claims that the primary readout establishes exterior use, that the secondary AUROC is a lower bound on artifact, and that the controls isolate signal from prior or mask leakage are withdrawn for the original intervention. What is lost is the card's central estimand and headline: the debate found no in-scope way to interpret “diagnose a volume with no patient in it” as evidence about normal CT-CLIP inference. The exterior-swap study retains the medical motivation but is explicitly a separate question, not an amendment. The only retained path for this card is a checkpoint-specific reopening based on previously uninspected training augmentation or a future reformulation around another appropriately trai

## idea-007 [ACTIVE/DEBATED]
- title: The same patient, twice, ten minutes apart, differing only in how much air is in the lungs
- question: When one patient receives an inhale and an exhale breath-hold CT in a single session on one scanner at matched exposure, how much do a chest-CT foundation model's finding scores move, and do they move as a function of total lung volume in litres?
- deliverable_sentence: The model is using the degree of lung inflation - total lung volume and the mean parenchymal attenuation it sets - as a component of its emphysema, mosaic attenuation, atelectasis and lung opacity scores, so a patient who cannot hold a full breath receives a different diagnosis.
- keystone_prerequisite: A public corpus, with no application or data transfer agreement, provides at least two breath-hold chest CT acquisitions of the same patient in one session at different inflation states, with matched acquisition parameters and whole-thorax coverage - so that inflation is the only thing that differs and both images are real full-dose reconstructions rather than phase bins.
- keystone_status: INSPECTED_TRUE
### Recommendation
**REVISE.** Update the idea card to the converged state-level claim and corrected scores, then require Stage 0 before a probe contract. The single most important thing for the human to inspect is the prespecified DICOM-to-final-tensor comparability gate: whether enough inhale/exhale pairs truly retain matched reconstruction, coordinates, physical scale, and thoracic coverage through the complete pinned CT-CLIP preprocessing pipeline.
### Unresolved
There is no remaining stated disagreement between proposer and critic; the debate converged in round 6. The following empirical questions remain open and must not be mistaken for consensus that their answers are favorable. ### Do enough actual pairs pass the reconstruction and framing gate? - **Proposer's position:** The keystone is `NOT_INSPECTED`; NBIA index evidence suggests 18 clean candidate pairs and two flagged pairs, but full DICOM and tensor inspection is still required. - **Critic's position:** Same. Collection- and index-level evidence cannot establish reconstruction matching, coordinate consistency, or comparable inputs after pinned preprocessing. - **What evidence would settle it:** Download and inspect every candidate pair. Before inspection, specify the minimum usable-pair count and tolerances for convolution kernel, slice thickness and increment, reconstruction diameter, contrast status, FrameOfReferenceUID, ImagePositionPatient, retained superior/inferior landmarks, physical scale, crop loss, padding fraction, lung boundary contact, and state-dependent resizing/cropping. Inspect the final preprocessed tensors as well as DICOM headers. ### Is a common physical box compatible with CT-CLIP preprocessing without state-dependent framing? - **Proposer's position:** It is a Stage 0 hypothesis, not an eliminated confound. Expiratory scans may contain a different lung-voxel fraction and may be padded differently. - **Critic's position:** Same; a common upstream box guarantees nothing if downstream preprocessing adapts crop, resize, or padding to anatomy. - **What ev
### Amendments made
At round zero, the idea claimed that CT-CLIP used total lung volume and mean parenchymal attenuation as co-primary cues for emphysema, mosaic attenuation, atelectasis, and lung opacity; that ten 4DCT phases identified a within-patient dose response; and that breath-hold differences could give a patient a different diagnosis. It asserted rung 3, identifiability 5, an `INSPECTED_TRUE` keystone, feasibility 4, and novelty confidence 4. The converged idea claims only a state-level X: degree of inspiration, measured as total lung volume in litres, as a component of emphysema, atelectasis, and lung-opacity scores. The breath-hold pair is primary. Individual visual channels are not identified; mean HU and LAA%-950 are explanatory or magnitude context only. The 4DCT series is optional and exploratory, with matched-volume pairs serving at most as a jitter floor. Mosaic attenuation, ten-phase dose-response identification, “different diagnosis,” and any shared-mechanism robustness comparison with LAA%-950 are lost. The idea is conditional rather than ready: the keystone is `NOT_INSPECTED`; feasibility and novelty confidence are capped at 3; identical framing is a testable Stage 0 hypothesis; and external validity is limited by sharp B70f reconstruction and the radiotherapy-planning population. The existing `idea_card.json` has not yet been updated to reflect these amendments.

## idea-008 [ACTIVE/DEBATED]
- title: Two papers say Sybil's residual signal is the background, one of them names emphysema, and neither measured it
- question: On low-dose CT scans with no visible nodule at the site of the subsequent cancer, where Sybil still reaches a 2-year AUC of 0.81, is its risk score a function of quantitative emphysema - the percentage of lung voxels below minus 950 Hounsfield units - measured on the same scan?
- deliverable_sentence: Sybil is using emphysema, and it reads it in a way that survives a change of reconstruction kernel that moves the standard quantitative emphysema index by about ten percentage points.
- keystone_prerequisite: Sybil's risk score and LAA%-950 can be placed side by side, per scan, on NLST series that (a) Sybil did not train on and (b) share a single reconstruction kernel - because the kernel moves LAA%-950 by more than the disease does, so a mixed-kernel sample would measure the kernel and call it emphysema.
- keystone_status: INSPECTED_TRUE
### Recommendation
**REVISE.** The debate produced a coherent conditional design, but the current `idea_card.json` still describes the superseded reconstruction arm, rung-3 observational logic, `INSPECTED_TRUE` keystone, and obsolete scores. Before deciding whether to advance, the human should look most closely at whether the proposed tissue-for-tissue edit can be validated as in-distribution with a prespecified sham-effect tolerance; that is now the single fact separating a model-use study from an association-only study.
### Unresolved
### Are the local parenchymal substitutions in-distribution for Sybil? - **Question:** Can coherent <−950 HU clusters be removed or inserted without producing an edit artifact or an anatomically implausible image that independently changes Sybil's score? - **Proposer's position:** This is unverified and must be a Stage 0 gate. Proposed checks are preservation of competitor summaries within tolerance, an edited-versus-unedited discriminator, and a dose-matched normal-parenchyma sham whose Sybil effect is small relative to the targeted edit. Existing generative nodule-edit work is encouragement, not validation of this operator. - **Critic's position:** Only a prespecified, validated, in-distribution perturbation with reciprocal insertion, matched shams, and anatomy-preservation checks can support “use.” Without it, only the association statement is licensed. - **What evidence would settle it:** Direct Stage 0 inspection and validation of the actual operator on held-out scans, using prespecified tolerances and failure rules. A sham effect comparable to the targeted effect settles it negatively for this operator. Passing the listed checks would support proceeding, although the debate did not define numerical tolerances or establish that those diagnostics are sufficient to detect every form of distribution shift. ### Does a score response isolate CT-emphysema geometry from remaining visible correlates? - **Question:** If Sybil responds directionally to removal and reciprocal insertion, does that identify coherent low-attenuation geometry rather than regional hypoperfusion, vascu
### Amendments made
At round zero, the card claimed rung 3 from a fixed-kernel score association plus reconstruction-pair behavior: “Sybil is using emphysema” in a reconstruction-invariant way. It treated LAA%-950 and Perc15 as co-primary, made the radiologist-defined no-visible-future-cancer-nodule subgroup primary, assigned `INSPECTED_TRUE`, and described the work as short and highly feasible. The final debated version instead claims: - The reconstruction audit is a separate candidate and contributes no evidence that Sybil uses emphysema. - “CT-defined emphysema” is operationalized as spatially coherent <−950 HU clusters, with isolated-voxel, cluster-geometry, and zonal measurements used to distinguish noise-like from lesion-like signal. - The fixed-kernel observational analysis is only a prerequisite and effect-sizing step. Even a positive matched result licenses association, not use. - The confirmatory use test is a four-arm within-image intervention: graded cluster removal, dose-matched sham replacement, reciprocal insertion, and coherent-versus-diffuse form contrast with equal voxel count and HU deficit. - Rung 3 is conditional on the intervention passing an edit-validity gate and producing directional, reciprocal, dose-responsive, sham-separated results while competing anatomy remains within tolerance. If the gate fails, the precommitted fallback is the association-only sentence and no rung-1 use claim. - `keystone_status` is `NOT_INSPECTED`. Split linkage, cohort overlap, and especially edit validity remain go/no-go prerequisites. What was lost: the reconstruction-invariance clause; th

## idea-009 [ACTIVE/DEBATED]
- title: Murray's cube law says how a branching tree should be built - ask whether the risk model is reading the lung's departure from it
- question: Is the non-nodular part of Sybil's risk signal carried by pulmonary vascular pruning - small-vessel blood volume, and the departure of the arterial tree's caliber-ratio exponent from Murray's cube law - rather than by the parenchymal destruction that C1 proposes?
- deliverable_sentence: The model is using pulmonary vascular pruning - the loss of blood volume in vessels below 5 square millimetres in cross-section, and the shift in the branching exponent away from the cube law that accompanies it - not parenchymal destruction.
- keystone_prerequisite: Pulmonary arterial and venous trees can be segmented from NLST low-dose screening CT by a free tool at sufficient fidelity that per-vessel cross-sectional area can be binned, and bifurcations resolved, in the calibre range where pruning occurs.
- keystone_status: NOT_INSPECTED
### Recommendation
**REJECT.** Before deciding, the human should look most closely at the estimand mismatch: neither association with a computable vascular phenotype nor sensitivity to synthetic vessel deletion identifies reliance on naturally occurring pruning and Murray-exponent departure. Revisit only if a dataset and validated design can isolate natural within-patient BV5 and exponent variation from acquisition and parenchymal change, with adequate exponent repeatability and a model-reliance test tied to that variation.
### Unresolved
There is no unresolved disagreement about the disposition of Idea 009 as titled. Two empirical questions remain for possible future candidates, but neither was disputed as a basis for rescuing this one: - **Could a narrower calibre-band ablation yield an interpretable rung-1 result?** The proposer considers the controlled ablation potentially valid if artifact exchangeability across calibre bands is supported by a non-vessel artifact floor and a preregistered calibre dose-response. The critic considers it a separate candidate whose claim must be limited to sensitivity to synthetic removal. Evidence that would settle intervention validity includes matched sham results showing that score changes are specific to vessel-like structures rather than patch scale or inpainting artifacts. Even favorable evidence would not settle the natural-pruning claim. - **Could the Murray-exponent question ever be reopened on CT?** Both sides require a newly identified dataset with natural within-patient BV5 and exponent variation, sufficiently fixed acquisition and parenchymal state, and a model-reliance test tied to those changes. The proposer additionally requires a same-session repeatability study establishing that within-patient exponent changes exceed the measurement precision floor. Those data would determine whether reopening is technically defensible; they are not currently identified.
### Amendments made
At round zero, the idea claimed that Sybil uses natural pulmonary vascular pruning—both reduced BV5/TBV and a departure of the arterial branching exponent from Murray's cube law—rather than parenchymal destruction. It proposed observational partial associations as the decisive test and classified the anticipated null as decisive. In round 1, the proposer replaced the primary analysis with within-patient, volume-matched calibre-band ablation and shams, retained regression only as descriptive, changed the negative classification to sensitivity-limited, dropped the Murray-exponent clause, and proposed a symmetric LAA%-950 intervention for the comparison with parenchymal destruction. This amendment lost the title's defining physical mechanism, reduced the claim to rung-1 edit sensitivity, added an artifact-exchangeability keystone, and increased compute and feasibility burdens. In round 2, that amendment was withdrawn as a repair. The narrower ablation was retained only as a possible separate candidate with the deliverable: *Sybil's score responds to removal of sub-5 mm² vessel-like structures beyond a volume- and geometry-matched sham.* It must not be described as evidence that Sybil uses natural pruning. Idea 009 itself has no surviving amended claim or experiment.

## idea-010 [REJECTED/DEBATED]
- title: Cardiomegaly on a CT report is admitted gestalt - ask whether the model has quietly turned it into millilitres
- question: Is CT-CLIP's cardiomegaly score a monotone function of total heart volume in millilitres measured by TotalSegmentator on the same volume, and does it track absolute volume or volume relative to the thoracic cavity?
- deliverable_sentence: CT-CLIP's cardiomegaly detector is using absolute heart volume in millilitres, not heart size relative to the chest, which means it over-calls cardiomegaly in large patients and under-calls it in small ones.
- keystone_prerequisite: The released ClassFine checkpoint can be run to produce a per-volume cardiomegaly score, and a per-volume heart volume in millilitres exists for those same volumes - so that a score and a physical measurement can be paired on the identical image.
- keystone_status: INSPECTED_TRUE
- KILLED: CIRCULARITY -- loader collapse: occupancy proportional to volume, no independent contrast
### Recommendation
**REJECT.** The single most important fact for the human to inspect is the loader-based collapse of the proposed discriminator: after fixed-spacing resampling into a fixed physical box, heart voxel occupancy is proportional to heart volume, so the study has no independent millilitres-versus-frame-fraction contrast. Reconsider only if a credible heart-specific, in-distribution intervention or paired natural experiment is identified.
### Unresolved
There is no remaining disagreement about the original candidate. Both sides agree that the recorded design and deliverable are unsupported. Reopening would require new evidence rather than resolution of a current dispute: an independently validated, in-distribution heart-specific intervention or a verified natural same-patient asset that changes three-dimensional cardiac volume while holding thoracic scale, leading silhouette and shape cues, preprocessing artifacts, and noncardiac anatomy fixed. Restoring any over/under-calling claim would additionally require an independent clinical reference and a frozen operating threshold. The scientific value of the proposed global-scale spin-off was not debated to resolution because both sides classified it as outside Idea 010. It would need a separate idea card and adversarial review.
### Amendments made
No amended version of Idea 010 was defended. At round zero, the idea claimed that CT-CLIP uses absolute heart volume in millilitres rather than heart size relative to the chest, reached rung 3, and consequently over-calls cardiomegaly in large patients and under-calls it in small patients. By convergence, all of those claims were withdrawn. The surviving observational audit can say only which automatic heart-size measurement best predicts the score in this corpus; it cannot say which signal the model uses and is not a rung-1 result. What was lost is the candidate's mechanistic deliverable, its clinical error claim, its rung-3 status, and its asserted inspected keystone. The proposed global physical-scale perturbation was explicitly separated as a new candidate with a narrower claim.

## idea-011 [PAUSED/DEBATED]
- title: Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock
- question: Does a chest-CT age model that was never told where to look recover the costal cartilage calcification clock, such that conditioning on calcified cartilage volume attenuates its age prediction more than conditioning on the aging markers a radiologist would name first?
- deliverable_sentence: The chest-CT age model is using calcified costal cartilage volume - the same structure a forensic anthropologist scores to age an unidentified body - rather than aortic calcification, vertebral bone density or emphysema.
- keystone_prerequisite: Costal cartilage can be segmented on ordinary ungated chest CT by a free tool, AND a public chest-CT corpus provides per-scan patient age across a range wide enough to fit an age model - so that a model's age prediction and a cartilage calcification volume exist for the same scans.
- keystone_status: NOT_INSPECTED
### Recommendation
**PAUSE.** The debate converged after a real, persistent objection; this was not a one-round rubber stamp. Before deciding whether to reopen, the human should look first for the missing identification instrument: a confirmed human chest CT resource with retained spectral base-material or dual-kV raw data and linkable age that can provide a measured, post-preprocessing-matched mineralized-to-soft-tissue contrast. Without that—or another genuinely matched real-tissue control—the current experiment cannot distinguish native use of costal cartilage mineralization from response to the deletion operation, regardless of improvements to masks, models, or supervision audits.
### Unresolved
There is no remaining disagreement between proposer and critic about the present disposition or the present design's claim ceiling. The following are unresolved empirical prerequisites for any future reopening: ### Can a measured, properly matched control separate mineralization use from the deletion signature? - **Proposer's position:** The current synthetic shams cannot do so. A plausible repair would use the same acquisition's retained spectral/base-material or dual-kV data so that the de-mineralized appearance is measured rather than synthesized. A matched real-tissue control might also work, but the proposed tracheobronchial-cartilage and internal-thoracic-artery controls each introduce a different location or tissue confound (Rounds 12 and 14). - **Critic's position:** Reopening requires a measured contrast matched after preprocessing on calcium-component loss, attenuation distribution, edge energy, topology, and location while leaving the claimed costal-cartilage quantity intact (Rounds 8, 11, and 13). - **Evidence that would settle it:** Inspect and confirm a human chest CT corpus retaining spectral base-material or dual-kV raw data, with linkable per-scan age, then prospectively demonstrate that its measured contrast satisfies the matching criteria. No suitable public resource was found in the Round-14 collection-level search, but that search was not systematic and does not establish nonexistence. ### Could registered longitudinal CT provide a natural contrast? - **Proposer's position:** This route is probably sensitivity-limited. Published cross-sectional gradient
### Amendments made
At round zero, the card claimed that an “unguided” CT-CLIP age probe used **calcified costal cartilage volume above 180 HU**, based primarily on observational mediation against aortic calcification, vertebral density, emphysema, and heart volume. It placed the idea conditionally at rung 3, treated MESA-slope recovery and a landmark-box measurement as extractor validation, classified a negative as decisive, and proposed a frozen linear probe as the target model. Across the debate, the proposed study changed as follows: - Primary endpoint: observational mediation → localized dose-response intervention with removal, permutation, and subthreshold-sham arms. - X: thresholded calcified volume → the broader, radiologist-legible phenomenon of costal cartilage mineralization, measured as a vector rather than one cutoff statistic. - Comparator set: aorta, vertebrae, emphysema, and heart → only calcium-family intervention controls, chiefly aortic calcium; diffuse markers became descriptive. - Target models: one report-supervised frozen CT-CLIP probe → CT-CLIP plus a second age regressor trained from scratch using chronological age alone, conditional on a supervision audit. - Instrument validation: MESA-slope recovery and a landmark box → ordered kill gates culminating in edited-voxel precision against CCSeg and a small older-adult CT-RATE reference. - Population and direction: all chest CT and a symmetric “uses” claim → older scans with measurable calcification and a one-sided removal operation. - Claim ceiling: native use of a forensic cartilage clock at rung 3 → sensitivity to a par

## idea-012 [PAUSED/DEBATED]
- title: Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- question: On low-dose CT scans with no visible nodule at the site of the subsequent cancer, where Sybil still reaches a 2-year AUC of 0.81, is its risk score a function of coronary artery calcium - the automated Agatston score computed by AI-CAC on the same scan - after adjustment for the emphysema and vascular measures that are its two rival explanations?
- deliverable_sentence: Sybil is using coronary artery calcium: on nodule-free screening scans its risk score rises with the automated Agatston score, and it does so over and above quantitative emphysema and small-vessel blood volume.
- keystone_prerequisite: Sybil's per-scan risk score and a per-scan automated CAC score can be placed side by side on the SAME held-out, nodule-free NLST scans, AND the CAC contribution can be estimated separately from emphysema and small-vessel blood volume - because all three are smoking-driven and mutually correlated, so a design that measures only CAC would attribute shared variance to it.
- keystone_status: INSPECTED_TRUE
### Recommendation
**PAUSE.** Before deciding otherwise, the human should inspect whether the MD.ai-derived scan-level exclusion membership has become available—and is joinable to a frozen obtainable Sybil evaluation split—because without it the study cannot test the specific residual that defines Idea 012.
### Unresolved
No substantive disagreement remained after the proposer's round-2 concession. The factual unblock condition is clear: obtain either (a) the scan-level future-cancer-site-nodule-exclusion membership used by Mikhael et al., joinable to a frozen obtainable Sybil evaluation split, or (b) a public, prospectively specified machine-computable rule validated against that membership with sufficient agreement to preserve the cohort estimand. Even after that evidence appears, the CAC-use claim would still require the fidelity-gated intervention and matched controls accepted in round 1.
### Amendments made
At round zero, Idea 012 claimed that partial association of Sybil score with automated Agatston-equivalent CAC—after adjustment for pack-years, emphysema, and BV5, supplemented by a paired-kernel arm—could explain Sybil's published residual performance in scans without a visible nodule at the future cancer site. In round 1, the proposer temporarily replaced that design with realistic within-scan inpainting of AI-CAC-segmented coronary lesions, compared against size- and attenuation-matched aortic-calcium edits and calcium-free coronary-territory sham edits. The proposal added HU-space and post-Sybil-transform fidelity checks, AI-CAC suppression as a positive control, and restated X as calcium presence and extent surviving Sybil's preprocessing. It dropped partial regression, mediation, the cancer endpoint, and the exact residual cohort; the 0.81 residual became motivation only. Negative-result value became conditional on intervention fidelity and a prespecified detectable-effect threshold. In round 2, that amendment was withdrawn from Idea 012 because it changed the estimand. The controlled-inpainting design survives only as a proposed separate Mode B candidate. Idea 012 retains its original Mode A question but makes no current feature-use claim and is paused. Lost from the executable idea are the published-residual venue, its quantified 0.81 anchor as a directly testable cohort result, and the original high-regret claim that this residual can presently be decoded from public assets.

## idea-013 [SHORTLISTED/DEBATED]
- title: CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- question: When CT-CLIP fires its 'Coronary artery wall calcification' label, is the score a monotone function of automated coronary Agatston, and does it dissociate from aortic-wall calcium measured in the same volume - so that the coronary label tracks coronary calcium specifically rather than total vascular calcium?
- deliverable_sentence: CT-CLIP is using coronary artery calcium as a localised quantity: its coronary-calcification score rises with automated coronary Agatston and is not merely a readout of total calcium load, because it separates from aortic-wall calcium in the same scan.
- keystone_prerequisite: CT-CLIP's coronary-calcification score can be regressed against a per-scan automated coronary Agatston on CT-RATE volumes (primary), AND coronary and aortic calcium vary independently ENOUGH in the CT-RATE population for the localisation dissociation to be identifiable (secondary) - because if the two calcium loads are nearly collinear, the dissociation cannot be estimated
- keystone_status: INSPECTED_TRUE
### Recommendation
**REVISE.** Rewrite the idea card around the reduced rung-1 calibration and reconstruction-sensitivity audit, with localisation explicitly excluded and the keystone set to `NOT_INSPECTED`. The single most important thing for the human to inspect before deciding is whether a validated, annotation-free coronary target localiser for nongated noncontrast CT actually exists and runs on CT-RATE; that fact determines whether the high-value localisation question has a credible spin-off or whether idea 013 should remain only a modest robustness audit.
### Unresolved
### Is the reduced rung-1 audit worth running? - **Question:** Does the modest calibration and reconstruction-sensitivity audit have enough standalone scientific value to justify the roughly two-week inference effort? - **Proposer's position:** It is worth running only because it is relatively cheap and produces score dynamic-range, AI-CAC compatibility, and reconstruction-variability assets needed by a possible later intervention study. - **Critic's position:** The critic accepted the reconstruction analysis as a valuable robustness audit but did not explicitly endorse its standalone priority after the localisation claim was removed. - **What evidence would settle it:** A Stage 0 feasibility result showing that AI-CAC operates validly on the released CT-RATE volumes, that both CT-CLIP heads have adequate dynamic range, that the calcium measurements have usable prevalence and reliability, and that the 425 reconstruction pairs yield sufficient measurement variation for a prespecified minimum detectable effect. Scientific priority after those gates remains partly a human value judgment. ### Can the localisation question be revived as a separate intervention study? - **Question:** Can coronary and aortic intervention targets be located with comparable, independently validated anatomical accuracy on nongated noncontrast CT without a new annotation campaign? - **Proposer's position:** A spin-off could use either within-volume relocation between observable native coronary and aortic calcifications or donor insertion gated by a validated coronary localiser, while retaining the rou
### Amendments made
- **Round zero claim:** Cross-sectional monotone and partial regressions of CT-CLIP's coronary score against AI-CAC and thresholded aortic calcium would establish that the model uses localised coronary calcium and reach rung 3. - **Round 1 amendment:** The regressions were demoted to descriptive convergent validity. A reciprocal coronary/aortic attenuation intervention with matched shams and a head-by-location interaction became confirmatory; reconstruction pairs became a robustness and edit-validity reference. Feasibility fell from 4 to 3 and the keystone became uninspected. - **Round 2 amendment:** Transplantation into calcium-free recipients replaced erasure as the primary intervention; erasure became an independent secondary generator. Local patch statistics, a held-out real-versus-edited discriminator, and cross-generator agreement were added. The project expanded from an approximately two-week inference audit to a five-to-six-week editing-and-validation methods study. - **Round 3 retreat:** The intervention amendments were not adopted into the current candidate because their coronary-target prerequisite was unsupported and a third structural repair would violate the proposer's prespecified stopping rule. The candidate now claims only rung-1 use of displayed vascular-calcium signal through calibration descriptives and a reconstruction-sensitivity audit. The anatomy-specific localisation question is separated as a gated spin-off. - **Lost:** The original deliverable sentence that CT-CLIP's coronary label specifically tracks coronary calcium, the rung-3 status, the `INSP

## idea-014 [PAUSED/DEBATED]
- title: The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- question: Is the knee-pain model of Pierson et al. using directional medial tibial subchondral trabecular texture, rather than only joint-space narrowing and osteophytes, to recover pain that radiographic Kellgren-Lawrence grading misses?
- deliverable_sentence: The knee-pain model is using medial tibial subchondral trabecular texture—directional thickening and rarefaction of the load-bearing bone beneath the cartilage.
- keystone_prerequisite: The frozen Pierson pain model or exactly reproducible checkpoint can be run on OAI images that also support stable, automated directional fractal-signature measurement, and the measured texture has enough within-KL and within-person variation to identify a selective model-use effect.
- keystone_status: NOT_INSPECTED
### Recommendation
**PAUSE.** The revised question remains scientifically coherent, but the rate-limiting model asset has not been reproduced, and the final edit-validity amendment has not been tested or answered by the critic. The single most important thing for the human to inspect before deciding is whether the released Pierson pipeline can, with available OAI access and the allowed compute, produce at least two independent models that pass preregistered better-than-KLG and disparity-signature gates on a frozen split. Without that, there is no model family to decode; editor validity is the next gate only after reproduction succeeds. ```json {"verdict": "PAUSE", "unblock": "Demonstrate at least two independently trained Pierson-recipe models that pass preregistered pain-performance and disparity reproduction gates on a frozen OAI split within the available access and compute constraints."} ```
### Unresolved
### Can the published model family be reproduced under the access and compute constraints? - **Question:** Can at least two independent models trained from the released Pierson recipe on OAI pass preregistered gates for better-than-KLG pain prediction and the published disparity-reduction signature on a frozen evaluation split? - **Proposer's position:** Yes in principle; a multi-seed, behavior-gated reproduction is a scientifically stronger object than one checkpoint and preserves the original gap-decoding question at the model-family level. The proposer nevertheless treats this as an uncertain Stage-0 gate. - **Critic's position:** The family-level reformulation is legitimate, but no representation exists to study until reproduction is actually demonstrated; matching aggregate performance alone would not suffice unless the specified behavioral signatures and cross-seed mechanism replication are recovered. - **What evidence would settle it:** Active OAI access; an executable, resource-accounted preprocessing and training pipeline; frozen split and tolerances registered before texture analysis; and at least two independent seeds that pass both behavioral reproduction gates. Failure to obtain access, train within the compute envelope, or pass the gates pauses or ends the model-decode study. ### Does the revised image edit identify use of the declared fractal-signature X rather than edit artifacts? - **Question:** Does an FSA-calibrated, band-limited angular edit under radial-power/DC constraints and matched shams selectively change model pain scores because it changes direct
### Amendments made
At round zero, the card claimed that the specific frozen Pierson pain model could be probed; that a validation-learned texture direction could be erased to establish model use; and that the result could support a direct sentence about directional thickening and rarefaction of load-bearing trabecular bone. The amended idea instead claims: - The object is a family of at least two independently trained models following the published recipe and passing preregistered better-than-KLG and disparity-signature reproduction gates. It makes no claim about Pierson's unreleased weights. - Reproduction and resource feasibility are Stage 0, with `NOT_INSPECTED` keystone status. No texture probe or outcome-dependent editor development begins unless the behavioral gate passes. - The primary proposed identifier is an image-space, band-limited anisotropy intervention calibrated by achieved change in the measured directional fractal signature. DC, radial power, low-frequency joint geometry, and prescribed nuisance quantities are held within tolerances. - Controls now include an isotropic-density edit, a spectrum-preserving phase perturbation, zero/identity processing controls, and an acquisition-matched real-versus-edited discriminator equivalence gate at every used magnitude. Representation probing and erasure are exploratory corroboration only. - The direct rung-3 claim is limited to use of directional medial tibial subchondral radiographic texture/fractal signature. “Thickening and rarefaction along load paths” is only a source-supported interpretation if primary literature directly validat

## idea-015 [SHORTLISTED/DEBATED]
- title: A breast-cancer risk model may be reading the arteries as a vascular clock
- question: Is Mirai using breast arterial calcification as a vascular-age signal in its five-year breast-cancer risk prediction, independently of breast density and chronological age?
- deliverable_sentence: Mirai is using breast arterial calcification—the linear tram-track calcium in mammary arteries—as a vascular-age signal in breast-cancer risk prediction.
- keystone_prerequisite: An executable, validated, annotation-free BAC quantifier transfers to the same four-view mammograms on which frozen Mirai can run, with enough BAC-positive cases and age/density overlap to separate BAC use from age, density, and device.
- keystone_status: NOT_INSPECTED
### Recommendation
**REVISE.** The scientific design has converged, but the card has not been updated and the candidate-registration dispute remains irreducible. Before deciding, the human should make one explicit portfolio-governance choice: whether removal of the original vascular-age interpretation is an allowed rung demotion within Idea 015 or requires the agreed BAC-response experiment to be registered as a new candidate. Either choice should preserve the same narrowed experiment and prohibited conclusions; advancement should then remain conditional on Stage 0 confirming an obtainable Mirai-compatible cohort and spatial registration between the BAC mask and Mirai's exact input tensor. ```json {"verdict":"REVISE","unblock":"Choose revision-in-place versus re-registration, then update the card to the agreed BAC-specific claim and verify the Mirai-input/BAC-mask join on an obtainable compatible cohort."} ```
### Unresolved
### Should the narrowed BAC-response study remain Idea 015 or be registered separately? - **Proposer's position:** It is a revision in place. Mirai, the named X (breast arterial calcification), assets, keystone, confounds, and intervention remain the same; only an unearned rung-3 interpretation has been removed. The charter expressly permits a candidate to stop at rung 2 while naming what would be needed for rung 3, and Idea 007 supplies a precedent for demotion without a fork. - **Critic's position:** It is a replacement. The original distinguishing question was whether Mirai uses BAC *as vascular age*; the proposer conceded that the revised experiment cannot answer that question. Shared assets and motivation do not preserve candidate identity after removal of the defining causal interpretation. - **What evidence would settle it:** No empirical result would settle this registration dispute. It is a governance question about whether candidate identity follows the model and named X or the original mechanistic interpretation. The human must apply a consistent portfolio rule, with the charter's rung-demotion language and the Idea 007 precedent weighed against the rule that abandoning a defining question requires a new candidate. ### What would restore the original vascular-age claim? - **Proposer's position:** The claim is an aspirational rung-3 extension and cannot be tested with any currently confirmed cohort. - **Critic's position:** It can remain Idea 015 only if a Mirai-compatible cohort supplies an independently measured cardiovascular-age endpoint and supports analysis 
### Amendments made
At round zero, Idea 015 claimed that Mirai uses BAC as a vascular-age signal independently of chronological age and breast density, targeted rung 3, and proposed validation-learned embedding-direction erasure as its confirmatory test. The amended study claims only that Mirai's risk output responds specifically to breast arterial calcification—the linear tram-track calcium in mammary arteries—and not merely to calcification in general. It targets rung 2 and uses paired image-space BAC inpainting as the primary readout, compared with matched benign parenchymal-calcification deletion and equal-area non-calcific linear-structure deletion. Representation erasure is no longer the primary identifying instrument. The amended study expressly does not claim vascular-age encoding, inflated risk, miscalibration, or an equity effect. Vascular age would require an independent cardiovascular endpoint; calibration would require cancer outcomes and calibration analysis. What was lost is the original high-interest mechanistic headline: “a breast-cancer model found a vascular clock.” The remaining claim is narrower but still physician-legible and tests a precise delta left open by prior work on Mirai's general calcification reliance. The repository's current `idea_card.json` still contains the superseded round-zero title, question, rung, deliverable, embedding-erasure primary experiment, calibration implication, and scores; it therefore requires revision before advancement regardless of the registration decision.

## idea-016 [REJECTED/DEBATED]
- title: The PE model may read contrast flowing backward as a pressure gauge
- question: Is a pulmonary-embolism CTPA model using contrast reflux into the inferior vena cava and hepatic veins as a hydraulic back-pressure signal when it predicts right-heart strain?
- deliverable_sentence: The pulmonary-embolism model is using contrast reflux into the inferior vena cava and hepatic veins as a sign of elevated right-sided pressure.
- keystone_prerequisite: RSNA-STR CTPAs retain enough IVC/hepatic-vein coverage and bolus heterogeneity can be controlled well enough that automated reflux burden varies independently from RV/LV ratio and global contrast timing, while a frozen right-heart-strain model/checkpoint remains runnable.
- keystone_status: NOT_INSPECTED
- KILLED: IDENTIFIABILITY_FAILURE -- cannot separate right-heart physiology from power-injector protocol in any obtainable CTPA cohort
### Recommendation
REJECT Idea 016 on RSNA-STR. The single most important thing for the human to examine before reconsidering the broader question is whether a directly inspected alternative CTPA cohort jointly contains complete per-scan injection/timing metadata and an independent right-sided-pressure or TR-velocity measurement under enough fixed-protocol variation to identify physiology separately from the power-injector effect. ```json {"verdict": "KILL", "kill_code": "IDENTIFIABILITY_FAILURE", "unblock": "Locate and directly inspect a CTPA cohort with per-scan injection protocol metadata, an independent pressure or TR-velocity readout, fixed-protocol reflux variation, and a runnable frozen strain model."} ```
### Unresolved
There is no remaining disagreement between proposer and critic. The open empirical question is whether a suitable alternative cohort exists. Both sides require a directly inspected CTPA cohort with per-scan injection rate, saline-chaser, and scan-delay metadata; an independent right-sided-pressure or tricuspid-regurgitant-velocity measurement; sufficient reflux variation within a fixed-protocol design; and a runnable frozen strain model. Direct inspection of such a cohort's files, schema, and methods would settle whether the original question can be revived. It would not make RSNA-STR suitable.
### Amendments made
At round zero, Idea 016 claimed that an RSNA-STR pulmonary-embolism model might use IVC/hepatic-vein reflux as a hydraulic gauge of elevated right-sided pressure, with reflux-direction erasure proposed as a path toward that claim. After debate, that claim is withdrawn for RSNA-STR. The idea is not amended into a weaker rung-1 study because doing so would remove the defining pressure mechanism and materially reduce its interest and mechanism-clarity basis. Two separate future candidates were identified instead: 1. A sham-controlled image-space inpainting study asking only whether a frozen RV/LV-strain output depends on retrograde venous contrast, with no pressure interpretation and with new scores and Stage-0 gates. 2. A resurrection of the original pressure-gauge question only if a different cohort supplies injection-protocol metadata, an independent pressure or TR-velocity readout, fixed-protocol variation, and a runnable frozen model. What was lost is the central deliverable sentence on the named dataset: RSNA-STR cannot support the claim that the model uses reflux *as a sign of elevated right-sided pressure*.

# Backlog candidates
- scout-006-c01 [SHORTLISTED] verdict=NOVEL_UNVERIFIED audited=2026-08-10 score= -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the 
- scout-006-c02 [SHORTLISTED] verdict=NOVEL_UNVERIFIED audited=2026-08-10 score= -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just s
- scout-006-c03 [SCOUT_ONLY] verdict=INCREMENTAL audited=2026-08-10 score= -- An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver
- scout-006-c04 [SCOUT_ONLY] verdict=NOVEL_UNVERIFIED audited=2026-08-10 score= -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to b
- scout-006-c05 [SCOUT_ONLY] verdict=NOVEL_UNVERIFIED audited=2026-08-10 score= -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the brok
- scout-007-c01 [SHORTLISTED] verdict=NOVEL_VERIFIED audited=2026-08-10 score=0.0 -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- scout-007-c02 [SHORTLISTED] verdict=NOVEL_VERIFIED audited=2026-08-10 score=0.0 -- A breast-cancer risk model may be reading the arteries as a vascular clock
- scout-007-c03 [SCOUT_ONLY] verdict=NOVEL_UNVERIFIED audited=2026-08-10 score=0.0 -- Merlin may be reading fatty kidney rather than kidney shape
- scout-007-c04 [SHORTLISTED] verdict=NOVEL_VERIFIED audited=2026-08-10 score=0.0 -- The PE model may read contrast flowing backward as a pressure gauge
- scout-007-c05 [SCOUT_ONLY] verdict=NOVEL_VERIFIED audited=2026-08-10 score=0.0 -- A lung-cancer model may be reading a mechanically remodeled trachea
- scout-007-c06 [SCOUT_ONLY] verdict=NOVEL_UNVERIFIED audited=2026-08-10 score=0.0 -- The effusion model may be reading whether pleural fluid still obeys gravity
- scout-007-c07 [SCOUT_ONLY] verdict=NOVEL_UNVERIFIED audited=2026-08-10 score=0.0 -- The fibrosis model may be counting holes at the pleural edge
- scout-007-c08 [SCOUT_ONLY] verdict=NOVEL_UNVERIFIED audited=2026-08-10 score=0.0 -- The PE model may be reading how completely blood and contrast have mixed
- scout-007-c09 [REJECTED] verdict=UNAUDITED audited= score=0.0 -- 
- scout-007-c10 [REJECTED] verdict=UNAUDITED audited= score=0.0 -- 
- scout-007-c11 [REJECTED] verdict=UNAUDITED audited= score=0.0 -- 
- scout-007-c12 [REJECTED] verdict=UNAUDITED audited= score=0.0 -- 
- scout-007-c13 [REJECTED] verdict=UNAUDITED audited= score=0.0 -- 


===== STAGE TASK =====
<!-- stage: librarian -->
# Librarian pass

`dossier.md` (in your context) is the full-detail corpus: every idea and
backlog candidate with its card, status, kill code, debate verdict, unblock
conditions, and unresolved questions. You are the only stage that ever reads
the whole corpus at this depth. You have three duties. Work from the dossier
and from actual searches; cite sources for any claim that the world changed.

## Duty 1 -- Connection map
Find non-obvious relations across entries: shared mechanisms, shared datasets
where one idea's validated asset unblocks another, ideas that are secretly the
same question, and ideas whose findings would be mutually constraining. Write
these as a section of `librarian_report.md`: one short paragraph per
connection, naming the ledger ids involved and what the relation implies.

## Duty 2 -- Stale-verdict re-audit
For backlog candidates whose `audited_at` is old or whose verdict is
NOVEL_UNVERIFIED, re-search the literature. Where the verdict should change,
record it in `verdict_updates.json` as
`{"updates": [{"ledger_id": "...", "novelty_verdict": "...", "reason": "... (citation)"}]}`
using only NOVEL_VERIFIED, NOVEL_UNVERIFIED, INCREMENTAL, or DUPLICATE_PRIOR.
Only include entries whose verdict actually changes; an empty list is normal.

## Duty 3 -- Revival scan and proposals
Check killed and paused entries against what now exists: new datasets, model
checkpoints, released assets, new papers. Where a blocking condition has
genuinely lifted, or where a recombination of two entries dodges what blocked
both, write a proposal to `librarian_proposals.json` as
`{"proposals": [{"title": "...", "question": "...", "parent_ids": ["..."],
"revival_basis": "quoted blocking condition -> new fact with source",
"sketch": "2-3 sentences on the design"}]}`.
These are NOT candidates -- they are suggestions the next scouting cycle may
adopt (adoption still counts against the scout's revival quota and gets the
full filter treatment). Zero proposals is the correct number when nothing has
changed; never manufacture one.

Write `librarian_report.md` (duties 1-3 in prose, with a one-line summary of
any verdict updates and proposals). Write the two JSON files only if they have
content. Do not write code. Do not modify any other file.

