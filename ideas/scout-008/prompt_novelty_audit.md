You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-008
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

## 2026-08-10 — Idea 015 REJECTED (superseded) + claim-identity governance rule

The narrowed BAC-response experiment survives on its merits, but removing the
vascular-age interpretation changed the deliverable claim's identity. Rule
going forward: revision-in-place is for narrowing scope or fixing design
within the same deliverable sentence; when the deliverable sentence or the
prohibited-conclusions set changes, the idea is REJECTED (superseded) and the
successor registers as a NEW candidate with parent_ids for lineage. The
successor re-enters through a normal scouting cycle, receives its own novelty
audit, and is re-ranked in the backlog on current merit — no inherited queue
position. For idea 015 specifically: the successor keeps the agreed
BAC-specific design and prohibited conclusions, and remains conditional on
Stage 0 confirming an obtainable Mirai-compatible cohort and spatial
registration between the BAC mask and Mirai's exact input tensor.


## 2026-08-10 — Idea 005 spin-off S2 (reader-slot exchangeability): deliberate wait

S2 is a legitimate successor under the claim-identity rule (different
estimand; parent idea-005) and should re-enter, if at all, through a normal
scout revival or librarian proposal with parent_ids — not manual
registration. This is also a live test of the revival machinery. If S2 has
not resurfaced within a few cycles despite this note, that is a finding
about the revival path, not about S2.


## 2026-08-10 — Idea 006 unblock check: FAILED (evidence-quoted)

Released CT-CLIP training uses deterministic preprocessing only (CTReportDataset,
scripts/data.py): rescale, resample, HU clip [-1000,1000], /1000, center
crop/pad (fill -1, data.py:156). No masking/cutout/erasing augmentation
exists; visual SSL is present in the library but disabled (use_visual_ssl
default False; not enabled in run_train.py). Body-excluded volumes are out-
of-distribution for this checkpoint; the deletion intervention is
indefensible per the debate's condition. Idea 006 stays PAUSED, hardened;
the exterior-swap spin-off (idea 004 pairs) is the only live path.
Side finding for idea 013 Stage 0: CT-CLIP clips at +1000 HU, so calcium
density saturates — compute the automated calcium measure on the same
clipped range.



===== evidence/ledger_digest.md =====
# Ledger digest (auto-generated -- do not edit; run `python scout.py ledger digest`)

39 tracked ideas. Latest state per idea; full history in ledger.jsonl.

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **IDENTIFIABILITY_FAILURE** x2: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.
- **DATA_ACCESS** x1: Required data, checkpoints, or mappings are not obtainable in practice.
- **ANNOTATION_PROVENANCE** x1: Inference depends on who assigned labels / what they could see, and that is undocumented or contaminated.
- **CIRCULARITY** x1: The endpoint is a re-encoding of the input or of the thing being tested.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **scout-007-c05** [NOVEL_VERIFIED, score 4.0, audited 2026-08-10] -- A lung-cancer model may be reading a mechanically remodeled trachea
- **scout-007-c07** [NOVEL_UNVERIFIED, score 4.3, audited 2026-08-10] -- The fibrosis model may be counting holes at the pleural edge
- **scout-006-c04** [NOVEL_UNVERIFIED, score 4.1, audited 2026-08-10] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-007-c06** [NOVEL_UNVERIFIED, score 3.9, audited 2026-08-10] -- The effusion model may be reading whether pleural fluid still obeys gravity
- **scout-007-c08** [NOVEL_UNVERIFIED, score 3.6, audited 2026-08-10] -- The PE model may be reading how completely blood and contrast have mixed
- **scout-006-c05** [NOVEL_UNVERIFIED, score 3.4, audited 2026-08-10] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two
- **scout-007-c03** [NOVEL_UNVERIFIED, score 3.4, audited 2026-08-10] -- Merlin may be reading fatty kidney rather than kidney shape
- **scout-008-c04** [UNAUDITED, score 3.8] -- The emphysema call may read the shape of the holes, not just how many
- **scout-008-c05** [UNAUDITED, score 3.8] -- The lung-cancer model may read the aorta as an ageing clock
- **scout-008-c03** [UNAUDITED, score 3.5] -- The model that 'predicts a blood count' may just be reading how bright the blood is
- ... and 3 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- counterfactual-synthesis: 2
- representation-erasure: 2
- natural-paired: 1

## Ideas

- **idea-001** [REJECTED/DEBATED/baseline] -- Have lung nodule concept models been validated against radiologist opinion rather than against disease? -- killed: DATA_INSUFFICIENT -- data: {"primary": "LIDC-IDRI via The Cancer Imaging Archive", "license": "CC BY 3.0", 
- **idea-002** [PAUSED/DEBATED/baseline] -- Dermoscopic concepts predicted from non-dermoscopic photographs: genuine visibility or shortcut? -- data: {"primary": "Derm7pt paired clinical/dermoscopic images", "source": "github.com/
- **idea-003** [REJECTED/DEBATED/baseline] -- Does BI-RADS concept intervention survive realistic clinician behaviour, and does it beat simply reading the BI-RADS category? -- killed: DATA_ACCESS -- data: {"primary": "BUS-BRA (Zenodo 8231412, CC BY 4.0) for the external and baseline a
- **idea-004** [ACTIVE/DEBATED/baseline] -- The free test-retest experiment already inside CT-RATE: duplicate reconstructions of the same acquisition
- **idea-005** [REJECTED/DEBATED/baseline] -- Eight named characteristics, or three latent ones? Discriminant validity of the LIDC concept vocabulary -- killed: ANNOTATION_PROVENANCE
- **idea-006** [PAUSED/DEBATED/baseline] -- Ask the chest-CT foundation model to diagnose a volume with no patient in it
- **idea-007** [ACTIVE/DEBATED/baseline] -- The same patient, twice, ten minutes apart, differing only in how much air is in the lungs
- **idea-008** [ACTIVE/DEBATED/baseline] -- Two papers say Sybil's residual signal is the background, one of them names emphysema, and neither measured it
- **idea-009** [REJECTED/DEBATED/baseline] -- Murray's cube law says how a branching tree should be built - ask whether the risk model is reading the lung's departure from it -- killed: IDENTIFIABILITY_FAILURE
- **idea-010** [REJECTED/DEBATED/baseline] -- Cardiomegaly on a CT report is admitted gestalt - ask whether the model has quietly turned it into millilitres -- killed: CIRCULARITY
- **idea-011** [PAUSED/DEBATED/baseline] -- Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock
- **idea-012** [PAUSED/DEBATED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **idea-013** [SHORTLISTED/DEBATED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **idea-014** [PAUSED/DEBATED/baseline] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- **idea-015** [REJECTED/DEBATED/baseline] -- A breast-cancer risk model may be reading the arteries as a vascular clock
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
- **scout-008-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The cirrhosis model may be reading the bumpiness of the liver's edge
- **scout-008-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The chest-CT model may see the heart by watching the airway splay
- **scout-008-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The model that 'predicts a blood count' may just be reading how bright the blood is
- **scout-008-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The emphysema call may read the shape of the holes, not just how many
- **scout-008-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The lung-cancer model may read the aorta as an ageing clock


===== evidence/portfolio_brief.md =====
# Portfolio brief (auto-generated; run `python scout.py brief`)

Actionable ideas with debate verdicts. A revival/recombination
candidate MUST cite the specific condition below that has changed.

## idea-014 [PAUSED] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away

**Verdict:** **PAUSE.** The revised question remains scientifically coherent, but the rate-limiting model asset has not been reproduced, and the final edit-validity amendment has not been tested or answered by the critic. The single most important thing for the human to inspect before deciding is whether the released Pierson pipeline can, with available OAI access and the allowed compute, produce at least two independent models that pass preregistered better-than-KLG and disparity-signature gates on a frozen split. Without that, there is no model family to decode; editor validity is the next gate only after reproduction succeeds. ```json {"verdict": "PAUSE", "unblock": "Demonstrate at least two independently trained Pierson-recipe models that pass preregistered pain-performance and disparity reproduction gates on a frozen OAI split within the available access and compute constraints."} ```

**Unresolved:** Can the published model family be reproduced under the access and compute constraints?; Does the revised image edit identify use of the declared fractal-signature X rather than edit artifacts?; Is directional fractal signature a medically legitimate name for the model-used signal, and how much biological gloss may it carry?; Does discriminator equivalence adequately establish in-distribution editi

## idea-013 [SHORTLISTED] -- Does CT-CLIP's coronary-calcification score follow reconstruction-dependent changes in displayed coronary calcium?

**Verdict:** **REVISE.** Rewrite the idea card around the reduced rung-1 calibration and reconstruction-sensitivity audit, with localisation explicitly excluded and the keystone set to `NOT_INSPECTED`. The single most important thing for the human to inspect before deciding is whether a validated, annotation-free coronary target localiser for nongated noncontrast CT actually exists and runs on CT-RATE; that fact determines whether the high-value localisation question has a credible spin-off or whether idea 013 should remain only a modest robustness audit.

**Unresolved:** Is the reduced rung-1 audit worth running?; Can the localisation question be revived as a separate intervention study?; Would validated synthetic edits identify calcium location rather than edit artifacts?

## idea-012 [PAUSED] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan

**Verdict:** **PAUSE.** Before deciding otherwise, the human should inspect whether the MD.ai-derived scan-level exclusion membership has become available—and is joinable to a frozen obtainable Sybil evaluation split—because without it the study cannot test the specific residual that defines Idea 012.

## idea-011 [PAUSED] -- Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock

**Verdict:** **PAUSE.** The debate converged after a real, persistent objection; this was not a one-round rubber stamp. Before deciding whether to reopen, the human should look first for the missing identification instrument: a confirmed human chest CT resource with retained spectral base-material or dual-kV raw data and linkable age that can provide a measured, post-preprocessing-matched mineralized-to-soft-tissue contrast. Without that—or another genuinely matched real-tissue control—the current experiment cannot distinguish native use of costal cartilage mineralization from response to the deletion operation, regardless of improvements to masks, models, or supervision audits.

**Unresolved:** Can a measured, properly matched control separate mineralization use from the deletion signature?; Could registered longitudinal CT provide a natural contrast?; Is the editable cartilage mask sufficiently precise in the population where the experiment would run?; Are the other Stage-0 assets actually available and clean?

## idea-008 [ACTIVE] -- Does Sybil use CT-defined emphysema geometry?

**Verdict:** **REVISE.** The debate produced a coherent conditional design, but the current `idea_card.json` still describes the superseded reconstruction arm, rung-3 observational logic, `INSPECTED_TRUE` keystone, and obsolete scores. Before deciding whether to advance, the human should look most closely at whether the proposed tissue-for-tissue edit can be validated as in-distribution with a prespecified sham-effect tolerance; that is now the single fact separating a model-use study from an association-only study.

**Unresolved:** Are the local parenchymal substitutions in-distribution for Sybil?; Does a score response isolate CT-emphysema geometry from remaining visible correlates?; Can the required held-out NLST cohort and covariates actually be recovered?

## idea-007 [ACTIVE] -- The same patient at two degrees of inspiration

**Verdict:** **REVISE.** Update the idea card to the converged state-level claim and corrected scores, then require Stage 0 before a probe contract. The single most important thing for the human to inspect is the prespecified DICOM-to-final-tensor comparability gate: whether enough inhale/exhale pairs truly retain matched reconstruction, coordinates, physical scale, and thoracic coverage through the complete pinned CT-CLIP preprocessing pipeline.

**Unresolved:** Do enough actual pairs pass the reconstruction and framing gate?; Is a common physical box compatible with CT-CLIP preprocessing without state-dependent framing?; Is the optional matched-volume 4DCT jitter floor usable?

## idea-006 [PAUSED] -- Ask the chest-CT foundation model to diagnose a volume with no patient in it

**Verdict:** **PAUSE.** Before deciding whether the pause is reversible, the human should inspect the official CT-CLIP training data loader and augmentation configuration for large-region masking or cutout with a matching fill value. Absence would make the original intervention indefensible for this checkpoint; presence would justify distributional validation, not automatic advancement.

**Unresolved:** Did CT-CLIP training make large constant-filled occlusions sufficiently familiar?; Could the original question be valid for a different chest-CT model?

## idea-004 [ACTIVE] -- Within-acquisition reconstruction sensitivity of ClassFine abnormality scores

**Verdict:** **REVISE.** The debate converged on a defensible design, but the current idea card still contains claims and scores that the debate explicitly withdrew. Before deciding whether to advance to a feasibility memo, the human should look first at the direct Stage 0 metadata counts—especially the number and parameter makeup of geometry-matched same-acquisition pairs—because that single inspection determines whether the stronger reconstruction-content study exists or only the narrower composite pipeline audit remains.

**Unresolved:** Do enough geometry-matched same-acquisition pairs exist?; Are audit-independent thresholds estimable?; Are per-output analyses adequately powered?; Can the benchmark-precision arm be run without large-scale inference?; What equivalence margin is scientifically defensible?



===== evidence/librarian_proposals.md =====


===== ideas/scout-008/README.md =====
# Scouting cycle 008

Tracks: baseline


===== ideas/scout-008/candidates_all.json =====
{
  "cycle": 8,
  "tracks": [
    "baseline"
  ],
  "notes": {},
  "candidates": [
    {
      "id": "C1",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "A",
      "entry_point": 2,
      "design_template": "counterfactual-synthesis",
      "title": "The cirrhosis model may be reading the bumpiness of the liver's edge",
      "question": "Is Merlin using liver surface nodularity - the regenerative-nodule bumpiness of the hepatic capsule - rather than liver volume or parenchymal fat, when its abdominal-CT representation flags cirrhosis?",
      "rung": {
        "target": 3,
        "current": 0,
        "move_up": "An automated LSN score plus a Merlin-score association is exploratory. A selective drop in the cirrhosis score after erasing (or counterfactually smoothing) the surface-nodularity signal, beyond liver-volume and steatosis controls, reaches rung 1. Scanner/phase/site replication gates rung 2; liver surface nodularity is already a named, biopsy-validated rung-3 quantity."
      },
      "deliverable_sentence": "Merlin is using liver surface nodularity - the fine nodular irregularity of the hepatic capsule caused by regenerative nodules - as its image signature of cirrhosis.",
      "X_measurement": {
        "X": "Liver surface nodularity (LSN) score: the mean perpendicular distance between the detected liver margin and a smoothed polynomial reference margin, in millimetres.",
        "how": "Segment the liver, extract the anterior/lateral capsule contour on the relevant slices, fit a smoothed reference line, and take the mean margin-to-reference distance. Smith et al. defined and validated this on routine CT (Radiology 2016, DOI 10.1148/radiol.2016151542, PMID 27089026); an FDA-cleared semi-automated liver-boundary tool and a fully automated deep-learning Auto-LSN (Eur Radiol 2026, DOI 10.1007/s00330-026-12346-5) exist.",
        "could_compute_today_without_asking_anyone": "Yes. LSN is a published, reproducible pixel-and-geometry measurement with automated implementations; no radiologist rating is needed. Availability of a runnable Auto-LSN weight or the semi-automated tool for the exact cohort is a Stage-0 item, not a conceptual barrier."
      },
      "suspected_signal": "In cirrhosis, diffuse regenerative nodules and fibrous bridging deform the liver capsule into a finely undulating surface. This nodularity is a spatial-frequency property of the organ boundary, in principle separable from total liver volume, lobar redistribution, and parenchymal fat (steatosis attenuation).",
      "specific_artifact_confused_with_signal": "Reconstruction kernel and slice thickness change edge sharpness and therefore apparent nodularity; ascites, perihepatic fat, and adjacent bowel can distort the detected margin; contrast phase shifts capsule conspicuity.",
      "keystone_prerequisite": "Merlin exposes a usable cirrhosis / advanced-chronic-liver-disease phenotype score, on an obtainable abdominal-CT cohort where automated LSN is measurable and varies enough independently of liver volume and steatosis to identify a selective-use effect.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest inspected primary artifacts: Merlin (arXiv:2406.06512; Nature 2026, DOI 10.1038/s41586-026-10181-8) reports phenotype classification over 692 phenotypes and 5-year chronic-disease prediction; Smith et al. (DOI 10.1148/radiol.2016151542) validated LSN against fibrosis stage (AUROC ~0.93 for cirrhosis). The actual Merlin phenotype string for cirrhosis, the checkpoint output head, and a compatible cohort were not directly inspected.",
      "keystone_residual_assumption": "The easy facts are that LSN is real and Merlin has hundreds of phenotypes. I am still assuming a cirrhosis-relevant output is actually exposed and that LSN varies independently of liver volume and steatosis in the usable sample rather than being nearly collinear with them; that independence, not the existence of LSN, is load-bearing.",
      "rung_reached": "No rung yet. Conditional rung 1 after selective erasure / surface-smoothing counterfactual; rung 2 after kernel/phase/site controls; rung 3 only then.",
      "dies_like_prior": "It resembles scout-006-c03 (Merlin diabetes reading liver fat) in model and organ, but asks a different output (cirrhosis, not diabetes) and a different, non-metabolic X (capsule geometry, not parenchymal attenuation), and it does not repeat that design's use-vs-association weakness because the primary readout is an image counterfactual (surface smoothing), not a score-X regression. No annotation-provenance failure applies because LSN is tool-computed from voxels.",
      "closest_prior_work": [
        {
          "citation": "Blankemeier et al., Merlin: a CT vision-language foundation model",
          "identifier": "arXiv:2406.06512; Nature 2026 DOI 10.1038/s41586-026-10181-8",
          "verified_fact": "Merlin is a 3D abdominal-CT foundation model evaluated on 692 EHR phenotypes and 5-year chronic-disease prediction.",
          "delta": "It did not report liver surface nodularity as the signal behind any hepatic phenotype."
        },
        {
          "citation": "Smith AD et al., Liver Surface Nodularity Quantification from Routine CT Images as a Biomarker for Detection and Evaluation of Cirrhosis",
          "identifier": "Radiology 2016, DOI 10.1148/radiol.2016151542, PMID 27089026",
          "verified_fact": "An automated LSN score from routine CT differentiates cirrhosis with high accuracy and near-perfect reproducibility.",
          "delta": "No image foundation model was studied; it established the biomarker, not model reliance."
        },
        {
          "citation": "Auto-LSN: fully automated liver surface nodularity quantification in CT based on deep learning",
          "identifier": "Eur Radiol 2026, DOI 10.1007/s00330-026-12346-5",
          "verified_fact": "A deep-learning tool computes LSN automatically, non-inferior to the FDA-cleared semi-automated software.",
          "delta": "It quantifies LSN; it does not ask whether a foundation model uses it."
        }
      ],
      "existing_assets": [
        "Merlin paper and released model assets",
        "Liver segmentation in standard whole-body CT segmenters",
        "Published LSN algorithm, FDA-cleared semi-automated liver-boundary tool, and Auto-LSN"
      ],
      "smallest_decisive_experiment": "Stage 0: inspect Merlin's phenotype vocabulary/checkpoint for a cirrhosis output; validate automated LSN repeatability on a small public cohort and quantify LSN collinearity with liver volume and mean parenchymal HU. Confirmatory: build a validated surface-smoothing counterfactual (locally low-pass the capsule while preserving parenchyma and volume, discriminator-checked as in-distribution) and measure the paired change in Merlin's cirrhosis score; compare against volume-preserving and steatosis-preserving sham edits and an equal-magnitude random-boundary perturbation. Merlin uses X only if smoothing the surface selectively lowers the cirrhosis score.",
      "use_vs_association": "An LSN-versus-score regression is exploratory only. The use claim requires that a validated surface-smoothing counterfactual (or erasure of the validation-learned LSN direction) selectively changes Merlin's cirrhosis output beyond liver-volume and steatosis controls.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "Kernel/slice-thickness strata and site-held-out replication; kernel is the dominant residual because it changes edge sharpness. Not fully ruled out until Stage 0.",
        "positioning": "Minor after liver segmentation; margin detection restricted to reproducible anterolateral capsule.",
        "habitus": "Perihepatic fat aids margin detection but can bias it; measured as a nuisance.",
        "prevalence_referral": "Clinical abdominal-CT referral limits spectrum; second cohort needed.",
        "label_leakage": "Primary readout is the counterfactual score change from voxels; reports are not used."
      },
      "alternative_explanations": [
        {
          "alternative": "The model uses liver volume / lobar redistribution, not surface nodularity.",
          "resolution": "Hold volume fixed in the counterfactual and add a volume-direction control erasure."
        },
        {
          "alternative": "The model uses parenchymal steatosis (low attenuation), correlated with chronic liver disease.",
          "resolution": "Preserve parenchymal HU in the edit and add a steatosis-direction control."
        },
        {
          "alternative": "The counterfactual removes generic edge information rather than nodularity.",
          "resolution": "Discriminator in-distribution check, equal-magnitude random-boundary perturbation, and retained performance on unrelated hepatic outputs."
        }
      ],
      "anticipated_negative": {
        "classification": "sensitivity-limited",
        "reason": "A null smoothing effect could mean nodularity is encoded nonlinearly or that the edit was too weak; it becomes decisive only after a prespecified edit-magnitude and probe-reliability floor and an in-distribution check."
      },
      "cross_domain": {
        "borrowed_construct": "Surface roughness / spatial-frequency characterisation of a deformed boundary (morphometry).",
        "measurement_implied": "Mean margin-to-smooth-reference distance rather than any parenchymal statistic.",
        "if_analogy_dropped": "Without the roughness framing the experiment would test parenchymal texture or volume; the boundary-roughness construct fixes X as capsule undulation and dictates the smoothing counterfactual."
      },
      "remaining_legwork": "1 day to inspect Merlin's phenotype vocabulary and checkpoint; 3-5 days for a compatible cohort audit; ~1 week to validate automated LSN and build the smoothing counterfactual. First go/no-go in about 2 weeks.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "One model, one named boundary measurement, explicit volume/steatosis rivals."
        },
        "identifiability": {
          "value": 3,
          "why": "The volume/steatosis-preserving counterfactual separates surface geometry from the obvious rivals, but kernel-driven edge sharpness and edit specificity remain."
        },
        "medical_relevance": {
          "value": 4,
          "why": "It would name a biopsy-validated cirrhosis substrate as what a foundation model reads."
        },
        "interest": {
          "value": 3,
          "why": "The LSN-cirrhosis link is known; that a foundation model exploits it is a plausible but not startling finding."
        },
        "prior_legwork": {
          "value": 4,
          "why": "Merlin, liver segmentation, and validated/automated LSN tools all exist."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped: keystone not inspected; Merlin output and cohort join uninspected."
        },
        "data_readiness": {
          "value": 3,
          "why": "Merlin and abdominal CT are accessible with work."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "LSN metrics are standard and reproducible; the counterfactual controls are custom."
        },
        "negative_result_value": {
          "value": 2,
          "why": "The anticipated null is sensitivity-limited."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped; no direct Merlin/LSN study was found in a bounded search."
        },
        "regret": {
          "value": 4,
          "why": "A cheap vocabulary/tool audit could settle whether a validated biomarker is the model's substrate."
        }
      },
      "priority_score": 3.35,
      "priority_arithmetic": "0.20*3 + 0.15*3 + 0.15*4 + 0.10*4 + 0.10*3 + 0.10*5 + 0.10*2 + 0.05*3 + 0.05*3 = 3.35",
      "unverified_claims": [
        "Merlin exposes a usable cirrhosis/ACLD score",
        "A runnable automated LSN tool transfers to the compatible cohort",
        "LSN varies independently of liver volume and steatosis in the usable sample"
      ],
      "track": "baseline"
    },
    {
      "id": "C2",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "B",
      "entry_point": 2,
      "design_template": "representation-erasure",
      "title": "The chest-CT model may see the heart by watching the airway splay",
      "question": "Is CT-CLIP using the subcarinal angle - the widening of the tracheal bifurcation produced by left-atrial enlargement - rather than a direct read of cardiac silhouette size, when it calls cardiomegaly?",
      "rung": {
        "target": 3,
        "current": 0,
        "move_up": "A subcarinal-angle-versus-score association is exploratory. A selective drop in the cardiomegaly score after erasing the validation-learned subcarinal-angle direction, beyond cardiac-width, sex, and body-size controls, reaches rung 1. Scanner/site replication gates rung 2; the subcarinal angle is already a named radiographic sign at rung 3."
      },
      "deliverable_sentence": "CT-CLIP is using the subcarinal angle - the splaying of the carina caused by an enlarged left atrium - as part of how it detects cardiomegaly.",
      "X_measurement": {
        "X": "Subcarinal (interbronchial) angle in degrees, measured between the main-bronchial centerlines at the carina.",
        "how": "Segment the tracheobronchial tree (HU threshold / region growing), extract main-bronchus centerlines, and compute the angle at the bifurcation, as done on CT by Kubota et al. and Chen et al. (subcarinal angle 73+/-16 deg; positively correlated with left-atrial volume, r=0.34-0.40; BJR 2005, PMID 16110098). No reader grade is required.",
        "could_compute_today_without_asking_anyone": "Yes. Airway segmentation and centerline angle are deterministic geometry from voxels."
      },
      "suspected_signal": "The left atrium sits immediately below the carina; as it enlarges it pushes the two main bronchi apart, widening the subcarinal angle. A model taught 'cardiomegaly' from reports may pick up this airway splaying as a mediastinal proxy for cardiac enlargement rather than measuring the cardiac silhouette directly.",
      "specific_artifact_confused_with_signal": "The subcarinal angle also widens with female sex, obesity, and carina-to-spine position, and narrows with hyperinflation; these are biological/positional confounds, not scanner artifacts, and are the reason the angle's correlation with atrial size is only moderate.",
      "keystone_prerequisite": "CT-CLIP's preprocessing preserves carinal geometry well enough for the subcarinal angle to be encodable, AND, in CT-RATE, the subcarinal angle varies enough independently of overall cardiac width and of sex/habitus to identify a selective-use effect on the cardiomegaly output.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest inspected primary artifacts: the CT-RATE 18-label set includes 'Cardiomegaly' and CT-CLIP is released (arXiv:2403.17834); the subcarinal-angle-to-left-atrium link is established but modest and confounded (BJR 2005, PMID 16110098; AJR 1995, PMID 7717208). Neither the CT-CLIP preprocessing effect on airway geometry nor the CT-RATE joint distribution of angle, cardiac width, and sex was inspected.",
      "keystone_residual_assumption": "The easy fact is that the subcarinal angle correlates with left-atrial size. The load-bearing fact I am still assuming is that the angle carries information NOT already captured by gross cardiac width and sex - because if it is nearly collinear with cardiac width, no design can separate 'uses the airway angle' from 'uses heart size', and the whole point (an indirect airway cue) collapses.",
      "rung_reached": "No rung yet. Conditional rung 1 after selective erasure; rung 2 after acquisition/site controls; rung 3 thereafter.",
      "dies_like_prior": "It resembles idea-010 (cardiomegaly re-encoded as millilitres, killed CIRCULARITY), but crucially X is NOT the cardiac volume that defines the label - it is a distinct airway geometry that is a downstream mechanical consequence of only one cause of cardiomegaly (left-atrial enlargement). The endpoint is therefore not the label restated, and left-ventricular or pericardial causes of cardiomegaly would not move X, which is exactly the dissociation the design exploits.",
      "closest_prior_work": [
        {
          "citation": "Hamamci/Er/Simsar et al., CT-CLIP / CT-RATE foundation model",
          "identifier": "arXiv:2403.17834",
          "verified_fact": "CT-CLIP performs zero-shot multi-abnormality detection over 18 CT-RATE labels including Cardiomegaly.",
          "delta": "It did not ask which anatomical cue drives the cardiomegaly call."
        },
        {
          "citation": "CT assessment of tracheal carinal angle and its determinants",
          "identifier": "BJR 2005, PMID 16110098",
          "verified_fact": "On CT the subcarinal angle correlates with left-atrial volume but is also determined by sex, obesity, and carina position.",
          "delta": "It related geometry to anatomy, not to any model's use of it."
        },
        {
          "citation": "Widening of the tracheal bifurcation on chest radiographs as a sign of left atrial enlargement",
          "identifier": "AJR 1995, PMID 7717208, DOI 10.2214/ajr.164.5.7717208",
          "verified_fact": "Carinal widening is an accepted sign of left-atrial enlargement.",
          "delta": "Radiograph-era descriptive sign; no model decoded."
        }
      ],
      "existing_assets": [
        "CT-CLIP code/weights and CT-RATE with the Cardiomegaly label (non-contrast chest CT)",
        "Airway segmentation tools with carinal centerline extraction",
        "Published subcarinal-angle CT norms and determinants"
      ],
      "smallest_decisive_experiment": "Stage 0: measure native-to-CT-CLIP-tensor agreement of the subcarinal angle and its partial correlation with cardiac transverse width, sex, and thoracic width in CT-RATE. Confirmatory: learn a validation-only subcarinal-angle direction, erase it from frozen CT-CLIP embeddings on locked test cases, and compare the cardiomegaly-score change against cardiac-width, sex, and equal-norm random-direction erasures. The model uses X only if angle erasure adds harm beyond cardiac-width and sex directions.",
      "use_vs_association": "A subcarinal-angle-versus-score correlation is exploratory. The use claim requires selective erasure of the validation-learned angle direction to change the cardiomegaly output beyond cardiac-width and sex directions.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "CT-RATE acquisition strata and site-held-out evaluation; angle is fairly robust to kernel. Not fully ruled out until Stage 0.",
        "positioning": "Centerline geometry reduces gantry-angle effects; carina-to-spine position measured as a nuisance.",
        "habitus": "Thoracic width and body size measured as nuisance directions; obesity is a known angle determinant.",
        "prevalence_referral": "Single collection; external replication needed.",
        "label_leakage": "Cardiomegaly labels came from reports, but X is voxel-computed and the readout is the model's own score change."
      },
      "alternative_explanations": [
        {
          "alternative": "The angle is just a proxy for overall cardiac width.",
          "resolution": "Separate and joint cardiac-width vs angle erasures; requires angle to add incremental effect - the identifiability crux."
        },
        {
          "alternative": "The angle indexes sex/habitus, which independently drive the label.",
          "resolution": "Sex- and thoracic-width-matched analysis and a separate sex-direction erasure."
        },
        {
          "alternative": "Erasure removes generic mediastinal information.",
          "resolution": "Equal-norm random and unrelated-structure direction controls plus retained performance on non-cardiac outputs."
        }
      ],
      "anticipated_negative": {
        "classification": "sensitivity-limited",
        "reason": "Because the angle-atrium correlation is only moderate and entangled with cardiac width, a null could reflect low independent variance rather than non-use; it is decisive only if Stage 0 confirms adequate independent angle variance and probe reliability."
      },
      "cross_domain": null,
      "remaining_legwork": "2 days for the preprocessing-geometry and collinearity audit in CT-RATE; ~1 week for erasure calibration. First go/no-go in about 1.5 weeks; the collinearity check could kill it in days.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "One model, one named angle, explicit cardiac-width and sex rivals."
        },
        "identifiability": {
          "value": 2,
          "why": "The subcarinal angle is only moderately correlated with atrial size and is confounded by sex, obesity, and cardiac width; separating airway-cue use from heart-size use may be underpowered."
        },
        "medical_relevance": {
          "value": 3,
          "why": "It would explain that a cardiomegaly call rides partly on an indirect airway sign, a modest but real interpretability point."
        },
        "interest": {
          "value": 4,
          "why": "A model detecting heart enlargement by watching the airway splay is a surprising, physician-legible mechanism."
        },
        "prior_legwork": {
          "value": 3,
          "why": "CT-CLIP, airway segmentation, and subcarinal-angle norms exist; the specific join does not."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped; preprocessing geometry and collinearity uninspected."
        },
        "data_readiness": {
          "value": 4,
          "why": "CT-RATE is public and directly usable."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Angle metrics exist; erasure selectivity must be calibrated."
        },
        "negative_result_value": {
          "value": 2,
          "why": "Sensitivity-limited null given modest independent variance."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped; no direct CT-CLIP/subcarinal-angle study found."
        },
        "regret": {
          "value": 3,
          "why": "Cheap to check but identifiability may prove too weak to be worth more."
        }
      },
      "priority_score": 3.1,
      "priority_arithmetic": "0.20*3 + 0.15*2 + 0.15*3 + 0.10*3 + 0.10*4 + 0.10*5 + 0.10*2 + 0.05*4 + 0.05*3 = 3.10",
      "unverified_claims": [
        "CT-CLIP preprocessing preserves the subcarinal angle",
        "The angle carries variance independent of cardiac width and sex in CT-RATE",
        "The angle direction is selectively erasable"
      ],
      "track": "baseline"
    },
    {
      "id": "C3",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "B",
      "entry_point": 2,
      "design_template": "natural-paired",
      "title": "The model that 'predicts a blood count' may just be reading how bright the blood is",
      "question": "Is a CT foundation model that flags anemia using the CT attenuation of the blood pool - which scales with haematocrit - rather than any organ finding, as shown by whether the same patient's anemia readout swings when contrast is added within one session?",
      "rung": {
        "target": 3,
        "current": 0,
        "move_up": "A blood-HU-versus-score association is exploratory. Demonstrating that the anemia readout swings with the contrast-induced change in blood-pool attenuation, while haematocrit is fixed within the session, reaches rung 1 that the model reads blood-pool attenuation; showing the non-contrast blood HU is the operative variable (which is what encodes haematocrit) reaches rung 3."
      },
      "deliverable_sentence": "The model is using the CT attenuation of the blood pool - the radiodensity of blood, which rises and falls with haematocrit - to flag anemia.",
      "X_measurement": {
        "X": "Mean CT attenuation (HU) of the blood pool, sampled in the aorta / inferior vena cava / cardiac chambers, on non-contrast CT.",
        "how": "Segment the aorta and IVC (e.g., TotalSegmentator) and take the mean luminal HU. Blood attenuation correlates with haemoglobin (LV cavity r~0.59, aorta r~0.56; anemia threshold ~<=36.5 HU): Medicine 2021 (PMC9191293), unenhanced-thorax anemia prediction (PMID 12625080), and aorta/IVC correlation (PMC9816921). No reader input is required.",
        "could_compute_today_without_asking_anyone": "Yes. Mean luminal HU from an off-the-shelf vessel segmentation is trivial to compute."
      },
      "suspected_signal": "Beer-Lambert: X-ray attenuation of blood scales with its protein/iron content, so haematocrit sets blood radiodensity. Anemic blood is hypodense (a recognised 'flat', low-HU aorta), polycythaemic blood hyperdense. A model that appears to 'predict a blood count from an image' may simply be reading this physical attenuation, and adding iodinated contrast - which raises blood HU by hundreds of units while haematocrit is unchanged - should mislead it if that is the cue.",
      "specific_artifact_confused_with_signal": "Iodinated contrast, tube voltage (kVp), and beam-hardening all change blood HU independently of haematocrit; these are exactly the levers the natural-paired design uses, so the 'artifact' is deployed deliberately rather than merely feared.",
      "keystone_prerequisite": "The model exposes an anemia (or low-haemoglobin) output, AND an obtainable cohort contains same-session non-contrast and post-contrast abdominal CT of the same patients, so that blood-pool HU changes by a large known amount while haematocrit and anatomy are fixed.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest inspected primary artifacts: Merlin (arXiv:2406.06512) classifies 692 phenotypes (anemia is a standard phecode, but its presence in Merlin's exposed set was not confirmed); the blood-HU-to-haemoglobin physics is well validated (PMC9191293; PMID 12625080). The specific Merlin anemia head and a same-session paired-phase cohort were not inspected.",
      "keystone_residual_assumption": "The easy facts are that blood HU tracks haemoglobin and that many patients get pre- and post-contrast scans. The load-bearing facts I am still assuming are that an anemia output is actually exposed by the model and that haematocrit is truly unchanged over the minutes between phases (usually true, but acute haemorrhage/transfusion cases must be excluded).",
      "rung_reached": "No rung yet. The natural-paired swing gives rung 1/2 without labels; the non-contrast HU as the haematocrit encoder gives rung 3.",
      "dies_like_prior": "It uses the same structural move as the loop's one survivor, idea-004: comparing a model to itself across two acquisitions of identical anatomy so that no ground-truth label enters the primary measurement. Here the two acquisitions are non-contrast vs post-contrast rather than two reconstructions. No annotation-provenance failure applies because the primary readout is the label-free paired score swing.",
      "closest_prior_work": [
        {
          "citation": "Prediction of anemia on unenhanced CT of the thorax",
          "identifier": "PMID 12625080",
          "verified_fact": "Blood attenuation on unenhanced CT predicts anemia; a hyperattenuating aortic wall / dense septum signals it.",
          "delta": "It used simple HU thresholds read by humans, not a foundation model, and did not test whether a model relies on the attenuation."
        },
        {
          "citation": "Prediction of anemia on enhanced CT using virtual non-contrast reconstructions",
          "identifier": "Medicine 2021, PMC9191293",
          "verified_fact": "LV/aortic attenuation correlates with haemoglobin (r~0.56-0.59); ~<=36.5 HU thresholds anemia.",
          "delta": "Establishes the physics/threshold; no model-use question."
        },
        {
          "citation": "Merlin: a CT vision-language foundation model",
          "identifier": "arXiv:2406.06512",
          "verified_fact": "A CT foundation model classifies hundreds of EHR phenotypes off-the-shelf.",
          "delta": "Did not test whether an anemia phenotype is driven by blood-pool attenuation."
        }
      ],
      "existing_assets": [
        "A CT foundation model with a phenotype/finding head plausibly including anemia (Merlin candidate)",
        "Vessel segmentation (TotalSegmentator) for blood-pool HU",
        "Established blood-HU-haemoglobin literature and thresholds",
        "Routine same-session pre/post-contrast abdominal CT pairs in clinical archives"
      ],
      "smallest_decisive_experiment": "Stage 0: confirm an exposed anemia output and identify a set of patients with same-session non-contrast and post-contrast CT; verify blood-pool HU repeatability. Primary (label-free): run the frozen model on both phases of each patient and measure the paired change in the anemia score against the measured blood-pool HU change. If the anemia readout swings with the contrast-induced HU change, the model reads blood-pool attenuation. Confirmatory rung-3: restrict to the non-contrast arm and show the anemia score tracks non-contrast blood HU (the haematocrit encoder) beyond organ-based directions via erasure.",
      "use_vs_association": "The observational blood-HU-versus-score relation is exploratory. The use test is the within-patient paired swing: haematocrit is fixed but blood HU is forced to change by contrast, so a swing can only mean the model is reading blood-pool attenuation.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "Paired phases are same scanner/session, so scanner/site are held fixed within pair; kVp differences between phases are recorded.",
        "positioning": "Same session, near-identical positioning within pair.",
        "habitus": "Held fixed within patient.",
        "prevalence_referral": "Referral mix does not affect the within-patient contrast; external cohort still strengthens generality.",
        "label_leakage": "The primary readout uses no anemia label at all; only the optional rung-3 arm touches the haemoglobin value."
      },
      "alternative_explanations": [
        {
          "alternative": "The anemia score swings because contrast changes organ enhancement (kidney, spleen), not blood HU.",
          "resolution": "Regress the swing on measured blood-pool HU change while holding organ-enhancement measures fixed; add a blood-only local HU-shift counterfactual."
        },
        {
          "alternative": "The model reads bone-marrow or splenic attenuation as the anemia cue.",
          "resolution": "Measure marrow/splenic HU and include as competing directions in the confirmatory erasure."
        },
        {
          "alternative": "No swing because the model encodes anemia nonlinearly.",
          "resolution": "Probe-reliability floor and a magnitude check that the induced HU change exceeds the anemia HU threshold band."
        }
      ],
      "anticipated_negative": {
        "classification": "decisive",
        "reason": "If the induced blood-HU change is large (hundreds of HU, well past the anemia threshold band) yet the anemia readout does not swing, the model is not reading blood-pool attenuation - a decisive negative against this specific X, provided the encoding/reliability gate is met."
      },
      "cross_domain": {
        "borrowed_construct": "Beer-Lambert attenuation / densitometry from radiation physics.",
        "measurement_implied": "Mean luminal blood HU and its forced contrast-induced change, not any organ morphology.",
        "if_analogy_dropped": "Without the densitometry framing there is no reason to expect contrast to be a decisive probe; the physics predicts that a haematocrit reader must be fooled by contrast, which is the entire experiment."
      },
      "remaining_legwork": "1 day to confirm an exposed anemia output; 3-5 days to assemble same-session paired-phase cases; ~2 days for blood-pool HU pipeline. First go/no-go in about 1-1.5 weeks.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "One named physical quantity, one output, a decisive paired probe."
        },
        "identifiability": {
          "value": 4,
          "why": "The within-session contrast swing isolates blood-pool attenuation from anatomy with haematocrit fixed; residual is organ-enhancement co-variation, addressed by the blood-only counterfactual."
        },
        "medical_relevance": {
          "value": 3,
          "why": "It deflates or confirms 'AI reads blood counts from images' - a useful skeptical result, modest direct clinical utility."
        },
        "interest": {
          "value": 4,
          "why": "A foundation model secretly obeying Beer-Lambert is a clean, surprising story with a decisive test."
        },
        "prior_legwork": {
          "value": 4,
          "why": "Blood-HU physics is mature; vessel segmentation is off-the-shelf; paired scans are routine."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped; anemia output and paired-phase cohort uninspected."
        },
        "data_readiness": {
          "value": 3,
          "why": "Paired-phase CT is common but assembling a labelled, model-compatible set needs work."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "HU is trivial and the paired design needs no bespoke metric."
        },
        "negative_result_value": {
          "value": 3,
          "why": "A no-swing result is a decisive negative against blood-pool attenuation as the cue."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped; the physics is old but the model-use test appears unaddressed."
        },
        "regret": {
          "value": 4,
          "why": "Cheap, decisive, and re-usable across any CT model with a haematologic output."
        }
      },
      "priority_score": 3.55,
      "priority_arithmetic": "0.20*3 + 0.15*4 + 0.15*3 + 0.10*4 + 0.10*4 + 0.10*5 + 0.10*3 + 0.05*3 + 0.05*3 = 3.55",
      "unverified_claims": [
        "A CT foundation model exposes an anemia/low-haemoglobin output",
        "Same-session non-contrast+contrast pairs are obtainable at adequate number",
        "Haematocrit is stable across the paired scans (transfusion/haemorrhage excluded)"
      ],
      "track": "baseline"
    },
    {
      "id": "C4",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "C",
      "entry_point": 2,
      "design_template": "representation-erasure",
      "title": "The emphysema call may read the shape of the holes, not just how many",
      "question": "Is CT-CLIP's emphysema readout using the morphometric complexity of the low-attenuation clusters - the power-law size exponent that distinguishes many small holes from a few coalesced ones - rather than only their total extent?",
      "rung": {
        "target": 3,
        "current": 0,
        "move_up": "An association between the cluster-size exponent and the emphysema score is exploratory. A selective change in the emphysema score after erasing the validation-learned complexity direction, orthogonalised to LAA% extent, reaches rung 1. Reconstruction/site controls gate rung 2; the low-attenuation-cluster power-law exponent is a named quantity at rung 3."
      },
      "deliverable_sentence": "CT-CLIP is using the morphometric complexity of emphysema - the power-law size distribution of the low-attenuation clusters (few large coalesced holes versus many small ones) - not merely the fraction of lung below -950 HU.",
      "X_measurement": {
        "X": "The exponent D of the cumulative size distribution of low-attenuation-area (LAA, <-950 HU) clusters, and/or the 3D box-counting fractal dimension of the LAA mask; lower D means fewer, larger, coalesced holes.",
        "how": "Threshold the lung at -950 HU, label connected LAA clusters, fit the cumulative cluster-size distribution to a power law to get D (Mishima et al., PNAS 1999, DOI 10.1073/pnas.96.16.8829), or compute box-counting Dbox3D; complexity predicts COPD survival independent of extent (Eur Radiol 2018, PMID 29959456; Sci Rep 2023, s41598-023-40950-8). No reader input required.",
        "could_compute_today_without_asking_anyone": "Yes as a defined computation on the LAA mask - subject to the caveat that CT-CLIP's resampling/crop may alter fine cluster structure, which is the Mode-C keystone risk."
      },
      "suspected_signal": "Emphysema progresses by coalescence: destroyed alveolar walls merge small low-attenuation regions into large connected holes, a percolation-like transition. The cluster-size exponent captures this connectivity and is provably not the same as the total low-attenuation fraction, so a model could exploit hole topology beyond hole amount.",
      "specific_artifact_confused_with_signal": "Reconstruction kernel and image noise change small-cluster counts and therefore the exponent; slice thickness and CT-CLIP's isotropic resampling change 3D connectivity; motion/inspiration alter apparent LAA.",
      "keystone_prerequisite": "CT-CLIP's fixed preprocessing (HU clip to [-1000,1000], resample, centre crop, per the ledger) preserves the LAA cluster-size structure enough that the complexity exponent is encodable, AND complexity varies enough independently of LAA% extent in CT-RATE to identify a selective-use effect.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest inspected primary artifacts: CT-RATE's 18-label set includes 'Emphysema' and CT-CLIP is released (arXiv:2403.17834); the cluster-size power-law and its extent-independent prognostic value are established (Mishima PNAS 1999 DOI 10.1073/pnas.96.16.8829; Eur Radiol 2018 PMID 29959456). The ledger records CT-CLIP preprocessing (clip/resample/centre crop), but its effect on cluster structure and the CT-RATE complexity/extent joint distribution were not inspected.",
      "keystone_residual_assumption": "The easy fact is that cluster complexity is measurable and prognostic on native CT. The load-bearing fact I am still assuming is that it survives CT-CLIP's resampling and crop as encodable information and is not effectively collinear with LAA% after preprocessing; if resampling smears the small clusters, the exponent is gone before the model ever sees it.",
      "rung_reached": "No rung yet. Mode C: mechanism is strong but the encoding/preservation gate is uninspected.",
      "dies_like_prior": "It resembles idea-008 (does Sybil use emphysema geometry) and scout-007-c07 (fibrosis holes at the pleural edge), but differs on all three axes from idea-008 - different model (CT-CLIP), dataset (CT-RATE), and output (the emphysema label, not cancer risk) - and its estimand is specifically the complexity dimension orthogonalised to extent, not emphysema presence. Unlike scout-007-c07 it is whole-lung percolation of emphysema, not pleural-edge honeycombing of fibrosis. It is a brand-new question, not a revival of idea-008.",
      "closest_prior_work": [
        {
          "citation": "Mishima et al., Complexity of terminal airspace geometry assessed by CT",
          "identifier": "PNAS 1999, 96:8829-8834, DOI 10.1073/pnas.96.16.8829",
          "verified_fact": "LAA-cluster cumulative size distribution follows a power law whose exponent D measures terminal-airspace complexity, distinct from LAA%.",
          "delta": "It characterised the tissue, not what any model reads."
        },
        {
          "citation": "Low morphometric complexity of emphysematous lesions predicts survival in COPD",
          "identifier": "Eur Radiol 2018, DOI 10.1007/s00330-018-5551-7, PMID 29959456",
          "verified_fact": "Power-law exponent Dsize and box-counting Dbox3D independently predict COPD survival.",
          "delta": "Prognostic association; no foundation-model decoding."
        },
        {
          "citation": "CT-CLIP / CT-RATE foundation model",
          "identifier": "arXiv:2403.17834",
          "verified_fact": "CT-CLIP detects Emphysema zero-shot among 18 CT-RATE labels.",
          "delta": "It did not test whether the emphysema call uses cluster complexity vs extent."
        }
      ],
      "existing_assets": [
        "CT-CLIP weights and CT-RATE with the Emphysema label",
        "Standard LAA thresholding and connected-component/fractal tooling",
        "Published Dsize/Dbox3D methods with COPD validation"
      ],
      "smallest_decisive_experiment": "Stage 0: on CT-RATE, compute Dsize/Dbox3D and LAA% on native volumes and on CT-CLIP's exact input tensor, and check (a) native-to-tensor agreement of the exponent and (b) residual variance of complexity after regressing out LAA%. Confirmatory: learn a validation-only complexity direction orthogonal to the LAA%-extent direction, erase it from frozen embeddings on locked test cases, and compare the emphysema-score change against LAA%-direction and equal-norm random-direction erasures. The model uses complexity only if erasing it, but not extent, changes the emphysema call.",
      "use_vs_association": "A complexity-versus-score correlation is exploratory. The use test is selective erasure of the extent-orthogonalised complexity direction changing the emphysema output beyond the LAA%-extent direction.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "Kernel and noise strongly affect small-cluster counts; kernel strata and, if available, geometry-matched reconstruction pairs (CT-RATE has many) test robustness. Dominant residual.",
        "positioning": "Minor; inspiration state affects LAA and is measured as a nuisance.",
        "habitus": "Minor for lung LAA.",
        "prevalence_referral": "Single collection; external emphysema cohort needed.",
        "label_leakage": "Emphysema labels came from reports, but X is a voxel computation and the readout is the model's own score change."
      },
      "alternative_explanations": [
        {
          "alternative": "The model uses only LAA% extent; complexity is a passenger.",
          "resolution": "Orthogonalise complexity to extent and require the complexity-direction erasure to add effect beyond the extent direction."
        },
        {
          "alternative": "The exponent is a noise/kernel artifact.",
          "resolution": "Kernel strata and geometry-matched reconstruction pairs; require the effect to persist within kernel."
        },
        {
          "alternative": "Preprocessing destroys clusters, so any null is uninterpretable.",
          "resolution": "The Stage-0 native-to-tensor encoding gate must pass before the erasure result is interpreted."
        }
      ],
      "anticipated_negative": {
        "classification": "sensitivity-limited",
        "reason": "A null erasure effect could mean complexity was not preserved through preprocessing or was encoded nonlinearly; it is decisive only after the native-to-tensor encoding gate and a probe-reliability floor are met, otherwise uninterpretable."
      },
      "cross_domain": {
        "borrowed_construct": "Percolation / cluster-size scaling from statistical physics.",
        "measurement_implied": "The power-law exponent of the LAA cluster-size distribution, not the mean LAA%.",
        "if_analogy_dropped": "Without percolation the experiment would test emphysema extent, already a routine feature; the percolation construct changes X to the cluster-size exponent and predicts a coalescence (decreasing-exponent) signature the extent measure cannot express."
      },
      "remaining_legwork": "3-4 days for the native-to-tensor encoding and complexity/extent collinearity audit; ~1 week for erasure calibration. First go/no-go in about 1.5 weeks; the encoding gate can kill it early.",
      "scores": {
        "mechanism_clarity": {
          "value": 5,
          "why": "A specific named exponent (Dsize / Dbox3D) with an explicit coalescence/percolation mechanism and a measurement."
        },
        "identifiability": {
          "value": 3,
          "why": "Orthogonalising complexity to extent and using kernel strata attacks the main rivals, but preprocessing preservation and complexity/extent entanglement remain."
        },
        "interest": {
          "value": 4,
          "why": "A model reading the topology of emphysema rather than its amount would be a genuinely new statement about the emphysema label."
        },
        "medical_relevance": {
          "value": 3,
          "why": "Complexity carries extent-independent prognostic signal, but the immediate clinical consequence is modest."
        },
        "clarity": {
          "value": 4,
          "why": "Crisp, though 'complexity beyond extent' requires careful orthogonalisation to state precisely."
        }
      },
      "mode_c_priority_score": 3.9,
      "priority_arithmetic": "0.30*5 + 0.25*3 + 0.20*4 + 0.15*3 + 0.10*4 = 3.90",
      "feasibility_for_information": {
        "value": 3,
        "why": "Capped; the preprocessing-preservation keystone is uninspected and is the main risk."
      },
      "novelty_confidence_for_information": {
        "value": 3,
        "why": "Capped; no CT-CLIP/complexity study found, but emphysema-complexity is a mature literature and adjacency is real."
      },
      "unverified_claims": [
        "Cluster complexity survives CT-CLIP preprocessing as encodable information",
        "Complexity has adequate variance independent of LAA% in CT-RATE",
        "The complexity direction is selectively erasable"
      ],
      "track": "baseline"
    },
    {
      "id": "C5",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "C",
      "entry_point": 2,
      "design_template": "counterfactual-synthesis",
      "title": "The lung-cancer model may read the aorta as an ageing clock",
      "question": "Is Sybil using thoracic aortic tortuosity - the age- and degeneration-driven elongation and buckling of the aorta - as a systemic-ageing cue for future lung-cancer risk, separable from the lung parenchyma?",
      "rung": {
        "target": 3,
        "current": 0,
        "move_up": "A tortuosity-versus-risk association is exploratory. A selective change in Sybil's risk after a validated aortic-straightening counterfactual (or erasure of the tortuosity direction), beyond age, emphysema, and calcification controls, reaches rung 1. Scanner/site controls gate rung 2; aortic tortuosity is a named quantity at rung 3."
      },
      "deliverable_sentence": "Sybil is using thoracic aortic tortuosity - the elongated, buckled course an ageing, degenerating aorta takes - as a systemic-ageing cue when it predicts future lung cancer.",
      "X_measurement": {
        "X": "Thoracic aortic tortuosity index = (aortic centerline length / straight end-to-end chord) - 1, from the arch to the diaphragm.",
        "how": "Segment the thoracic aorta (e.g., TotalSegmentator), extract the centerline, and take the arc-to-chord ratio; tortuosity rises with age (centreline length ~191 cm <65y vs ~213 cm >=65y; PLOS One 2019, PMID 31013307, DOI 10.1371/journal.pone.0215549; Eur J Radiol 2018). No reader input required.",
        "could_compute_today_without_asking_anyone": "Yes. Aortic segmentation and centerline arc/chord are deterministic geometry from voxels."
      },
      "suspected_signal": "With age, elastin fragmentation lengthens and stiffens the aorta faster than the thorax grows, so the vessel buckles into a more tortuous course - mechanically like an axially-loaded column exceeding its buckling length. Because smoking and ageing drive both aortic degeneration and lung-cancer risk, Sybil's residual (nodule-independent) signal may partly be this vascular-ageing geometry rather than a lung finding.",
      "specific_artifact_confused_with_signal": "Chronological age itself, aortic wall calcification (a co-located degeneration marker), body height/thoracic length, and scan framing all move tortuosity; age and calcification are the biological confounds the design must beat.",
      "keystone_prerequisite": "Sybil's input tensor preserves aortic centerline geometry, AND, in NLST, aortic tortuosity carries enough variance independent of chronological age and emphysema to identify a selective-use effect on Sybil's risk score.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest inspected primary artifacts: Sybil is released and retains nodule-independent ('background') predictive performance (AUC 0.81 at 2y, 0.69 at 6y after removing nodule scans; Mikhael et al., JCO 2023, PMID 36634294; DOI 10.1200/JCO.22.01345); aortic tortuosity is a validated age-increasing centerline measure (PMID 31013307). Sybil's preprocessing effect on aortic geometry and the NLST tortuosity/age/emphysema joint distribution were not inspected.",
      "keystone_residual_assumption": "The easy facts are that tortuosity is measurable and rises with age, and that Sybil has residual signal. The load-bearing fact I am still assuming is that tortuosity has usable variance beyond age within NLST's narrow heavy-smoker age band - if tortuosity is nearly a deterministic function of age here, no design can separate 'uses the aorta' from 'uses age', which is the identifiability crux and the way idea-009's vascular geometry claim died.",
      "rung_reached": "No rung yet. Mode C: strong mechanism, uninspected encoding and age-independence gates.",
      "dies_like_prior": "It shares the 'vascular ageing clock' theme with scout-007-c02 / idea-015 (Mirai reading breast arterial calcification) and the vascular-geometry ambition of idea-009 (Murray tree law, killed IDENTIFIABILITY). It differs by using structural tortuosity (not calcification), the thoracic aorta (not breast arteries), and Sybil (not Mirai); against idea-009's failure it uses a single global centerline measure with a straightening counterfactual rather than a branching-ratio law across a tree, which gives a cleaner use-test - though age entanglement remains the primary risk and is scored as such.",
      "closest_prior_work": [
        {
          "citation": "Mikhael et al., Sybil: validated deep learning for future lung-cancer risk",
          "identifier": "JCO 2023, PMID 36634294, DOI 10.1200/JCO.22.01345",
          "verified_fact": "Sybil predicts 6-year lung-cancer risk from a single LDCT and keeps predictive power after nodule-bearing scans are removed.",
          "delta": "It did not attribute the residual signal to any specific vascular measurement."
        },
        {
          "citation": "Auditing Sybil: Explaining Deep Lung Cancer Risk Prediction Through Generative Interventional Attributions",
          "identifier": "arXiv:2602.02560 (2026)",
          "verified_fact": "A 2026 preprint applies generative interventional attribution to Sybil.",
          "delta": "This is the closest novelty warning: its attribution inventory must be inspected for aortic/vascular features before advancement; it is not known to test tortuosity specifically."
        },
        {
          "citation": "Tortuosity of the descending thoracic aorta: normal values by age",
          "identifier": "PLOS One 2019, PMID 31013307, DOI 10.1371/journal.pone.0215549",
          "verified_fact": "Aortic tortuosity index and centreline length increase significantly with age.",
          "delta": "Established the measurement and its age dependence; no model decoded."
        }
      ],
      "existing_assets": [
        "Sybil code/weights and the NLST pathway established in prior cycles",
        "Aortic segmentation and centerline tools (TotalSegmentator)",
        "Published aortic-tortuosity norms by age"
      ],
      "smallest_decisive_experiment": "Stage 0: inspect the 2026 Sybil-audit preprint for vascular features; measure native-to-Sybil-tensor agreement of the tortuosity index and its partial correlation with age and emphysema in NLST. Confirmatory: build a validated aortic-straightening counterfactual (warp the aorta toward a straighter centerline while preserving parenchyma, discriminator-checked in-distribution) and measure the paired change in Sybil's risk; compare against age-, emphysema-, and calcification-direction erasures and an equal-magnitude random-warp control. Sybil uses X only if straightening the aorta selectively lowers risk beyond age and emphysema.",
      "use_vs_association": "A tortuosity-versus-risk correlation is exploratory. The use test is a validated aortic-straightening counterfactual (or tortuosity-direction erasure) changing Sybil's risk beyond age, emphysema, and calcification directions.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "NLST kernel/scanner strata and paired reconstructions; site is masked and remains a limitation.",
        "positioning": "Centerline arc/chord is fairly framing-robust; thoracic coverage checked.",
        "habitus": "Body height / thoracic length measured as a nuisance (tortuosity scales with aortic length).",
        "prevalence_referral": "NLST uniform screening pathway addresses referral but only in heavy smokers, narrowing the age range - the key limitation for age-independence.",
        "label_leakage": "Cancer outcome cannot be printed into aortic geometry; X is voxel-computed and the readout is the model's score change."
      },
      "alternative_explanations": [
        {
          "alternative": "Tortuosity is a proxy for chronological age, which drives risk.",
          "resolution": "Age-matched analysis and a separate age-direction erasure; require tortuosity to add incremental effect - the crux."
        },
        {
          "alternative": "Tortuosity co-varies with aortic calcification, the real cue.",
          "resolution": "Measure aortic-wall calcium and include as a competing direction; straightening counterfactual leaves calcium in place."
        },
        {
          "alternative": "The straightening warp removes generic image information.",
          "resolution": "In-distribution discriminator check, equal-magnitude random-warp control, and retained performance on unrelated outputs."
        }
      ],
      "anticipated_negative": {
        "classification": "decisive",
        "reason": "If tortuosity is reliably encoded yet a validated straightening counterfactual leaves Sybil's risk unchanged while age erasure moves it, the vascular-ageing-geometry mechanism is directly weakened - conditional on the encoding and age-independence gates."
      },
      "cross_domain": {
        "borrowed_construct": "Euler buckling / axial elongation of a pressure-loaded elastic tube (mechanics).",
        "measurement_implied": "The centerline arc-to-chord tortuosity index and its response to a straightening warp, not vessel diameter or calcium.",
        "if_analogy_dropped": "Without the buckling framing the experiment would measure aortic diameter or calcification (already studied); the mechanics construct fixes X as tortuosity and motivates the straightening counterfactual as the decisive intervention."
      },
      "remaining_legwork": "1 day to inspect the 2026 Sybil-audit preprint; 2 days for native-to-tensor tortuosity agreement; 3-5 days for NLST tortuosity/age/emphysema collinearity; ~1 week to build and validate the straightening counterfactual. First go/no-go in about 2 weeks.",
      "scores": {
        "mechanism_clarity": {
          "value": 5,
          "why": "A specific tortuosity index with an explicit buckling/elongation mechanism and a straightening intervention."
        },
        "identifiability": {
          "value": 3,
          "why": "The straightening counterfactual plus age/emphysema/calcification controls attack the rivals, but NLST's narrow age band makes tortuosity-age separation the persistent threat."
        },
        "interest": {
          "value": 4,
          "why": "A lung-cancer model reading the aorta as an ageing clock is surprising and physician-legible."
        },
        "medical_relevance": {
          "value": 3,
          "why": "It would reframe part of Sybil's residual risk as systemic vascular ageing rather than occult tumour signal; modest immediate consequence."
        },
        "clarity": {
          "value": 4,
          "why": "The model-uses-X sentence is concrete; the age-independence caveat keeps it from a 5."
        }
      },
      "mode_c_priority_score": 3.9,
      "priority_arithmetic": "0.30*5 + 0.25*3 + 0.20*4 + 0.15*3 + 0.10*4 = 3.90",
      "feasibility_for_information": {
        "value": 3,
        "why": "Capped; preprocessing preservation and age-independence uninspected."
      },
      "novelty_confidence_for_information": {
        "value": 2,
        "why": "Capped and lowered: a 2026 Sybil interventional-attribution preprint (arXiv:2602.02560) is a near neighbour and must be inspected for vascular features before advancing."
      },
      "unverified_claims": [
        "Sybil preprocessing preserves aortic centerline geometry",
        "Aortic tortuosity has usable variance independent of age within NLST",
        "arXiv:2602.02560 does not already attribute Sybil risk to aortic/vascular geometry"
      ],
      "track": "baseline"
    }
  ]
}


===== ideas/scout-008/run_provenance.json =====
{
  "timestamp": "2026-08-11T06:48:44+00:00",
  "git_commit": "5007755e4b07a9bfb21dab3d218d5b67bb32f341",
  "claude_cli": "2.1.197 (Claude Code)",
  "codex_cli": "codex-cli 0.147.0",
  "tracks": [
    "baseline"
  ],
  "seed_concepts": null,
  "prompt_hashes": {
    "actioner.md": "263f5cce53cb0cee",
    "critique.md": "5c8ed5c43071eaeb",
    "debate_critic.md": "74f1e299e3c6db50",
    "debate_proposer.md": "6a41797dbc73796a",
    "debate_summary.md": "7243fe771e1f612d",
    "feasibility.md": "161deb087c24a45d",
    "fiction_extract.md": "8ada1a395c25072e",
    "fiction_refine.md": "8cf3d7183711f14f",
    "fiction_scout.md": "63b11687055c8624",
    "interpret.md": "ea213b1be9c3d178",
    "keystone_screen.md": "f6f206ca8577b47b",
    "librarian.md": "fda4243e93182828",
    "novelty_audit.md": "eb2b70b4159ab881",
    "probe_code.md": "766af76d5b22d687",
    "probe_plan.md": "51712f984817ef6b",
    "revise.md": "db7fab4a10c7c32b",
    "scout.md": "c5ae0f349d7a6d67",
    "wide_scout.md": "b21b441dba189d08"
  },
  "agents_toml_hash": "7e80bd12c967c003"
}


===== ideas/scout-008/scout_candidates.json =====
{
  "cycle": "scout-008",
  "stage": "scout",
  "generated_on": "2026-08-11",
  "tracks": ["baseline"],
  "records_read": [
    "evidence/decisions.md (injected in full)",
    "evidence/ledger_digest.md (injected in full)",
    "evidence/portfolio_brief.md (injected in full)",
    "ideas/scout-007/scout_candidates.json (schema and occupied-topic review)"
  ],
  "evidence_note": "Primary papers and tool descriptions were opened by web search for every scientific and asset claim quoted below (see keystone_evidence and closest_prior_work identifiers). A searchable page is not treated as proof of a load-bearing cohort or checkpoint fact: every model-to-image or tool-to-cohort join is left as an explicit keystone, not an assumed background. No novelty claim is asserted; novelty_confidence describes only how crowded the immediate neighborhood looked after a bounded search, and where a near-neighbor preprint exists it is named.",
  "generation_checklist": {
    "prior_kill_codes": {
      "USE_VS_ASSOCIATION": "Every candidate separates 'the model uses X' from 'X is correlated with the label' with an explicit intervention (validation-learned concept-direction erasure, image counterfactual, or a within-session natural-paired contrast that changes X while biology is fixed). Observational score-versus-X association is always labelled exploratory and never earns rung 1. C3's primary readout needs no label at all.",
      "ANNOTATION_PROVENANCE": "No X is a human rating. LSN, subcarinal angle, blood-pool attenuation, emphysema-cluster complexity, and aortic tortuosity are all computed from voxels by a citable tool or formula. Model training labels (cirrhosis, cardiomegaly, anemia, emphysema, cancer) do not define X and, for C3, do not enter the primary measurement.",
      "IDENTIFIABILITY_FAILURE": "This killed idea-009 (Murray tree law) and idea-016 (PE reflux). Each candidate lists the standing acquisition/biology alternatives by name and states which the design excludes; C2 is honestly scored low on identifiability because the subcarinal angle is only modestly correlated with left-atrial size and is confounded by sex and habitus.",
      "CIRCULARITY": "This killed idea-010 (cardiomegaly re-encoded as millilitres). C2 deliberately uses the subcarinal ANGLE, a downstream airway consequence distinct from the heart-volume label, not a re-encoding of it. C4 orthogonalises cluster complexity against emphysema extent so the endpoint is not the label restated.",
      "DATA_INSUFFICIENT": "Each candidate names the subset that actually supports the inference (e.g., anemia-labelled same-session contrast/non-contrast pairs; low-subcarinal-angle cases independent of sex) as a Stage-0 prevalence gate rather than a hidden assumption.",
      "WRONG_KEYSTONE": "For each candidate the nearest easily-checkable fact (the biomarker is real and measurable) is separated from the load-bearing fact (the model output exists AND X varies independently of the dominant confound in an obtainable cohort). The load-bearing fact is written as the keystone; keystone_residual_assumption states what remains assumed after the easy check."
    },
    "portfolio_revivals": "Zero. None of the portfolio brief's blocking conditions has a newly verified fact that changes it. idea-008 (Sybil emphysema geometry) remains active and blocked on an in-distribution tissue edit; C4 does not revive it (different model CT-CLIP, different dataset CT-RATE, different output, and a distinct complexity estimand), and is registered as a brand-new question, not a revival. Re-proposing paused ideas against unchanged objections would violate the revival rule."
  },
  "all_questions": [
    {"n": 1, "question": "Is Merlin using liver surface nodularity - the fine bumpiness of the hepatic capsule produced by regenerative nodules - when its abdominal-CT representation flags cirrhosis?", "status": "DEVELOPED as C1"},
    {"n": 2, "question": "Is CT-CLIP using the subcarinal (carinal) angle - airway splaying driven by left-atrial enlargement - when it calls cardiomegaly on chest CT?", "status": "DEVELOPED as C2"},
    {"n": 3, "question": "Is a CT foundation model using the CT attenuation of the blood pool, which scales with haematocrit, rather than any organ finding when it flags anemia?", "status": "DEVELOPED as C3"},
    {"n": 4, "question": "Is CT-CLIP's emphysema readout using the morphometric complexity - the power-law size exponent of the low-attenuation clusters - rather than only their extent?", "status": "DEVELOPED as C4"},
    {"n": 5, "question": "Is Sybil using thoracic aortic tortuosity - the age- and degeneration-driven elongation-buckling of the aorta - as a systemic-ageing cue for future lung-cancer risk?", "status": "DEVELOPED as C5"},
    {"n": 6, "question": "Is a chest-CT model using diaphragm dome flattening (dome curvature) as a hyperinflation signal for COPD?", "status": "DROPPED", "why": "Strong, measurable X, but it sits inside the emphysema/hyperinflation cluster already occupied by idea-007, idea-008, and C4; diaphragm curvature is also more sensitive to inspiration state than the fixed-remodelling X favoured this cycle."},
    {"n": 7, "question": "Is Merlin using the renal corticomedullary attenuation difference as a glomerular-filtration / perfusion proxy when it scores chronic kidney disease?", "status": "DROPPED", "why": "Corticomedullary differentiation is only visible with contrast and is dominated by injection phase and timing; the artifact (phase) and the signal (perfusion) are nearly inseparable without per-scan bolus metadata, and it would be a third Merlin candidate, breaking the dataset cap."},
    {"n": 8, "question": "Is a chest-CT lung-cancer model using pectoral / anterior chest-wall adipose thickness as a sex- and hormone-linked risk proxy?", "status": "DROPPED", "why": "This is the deliberately-wrong-sounding question and it is computable, but a positive result has too many equally plausible readings (sex, habitus, positioning, breast-tissue attenuation) for the design to isolate the claimed adipose signal - it would land at rung 1 with no path to rung 2."},
    {"n": 9, "question": "Is Merlin using the fractal dimension of the intrahepatic portal-venous branching tree as a portal-hypertension signal?", "status": "DROPPED", "why": "Cross-domain and appealing, but robust automated portal-tree segmentation on routine (often single-phase) abdominal CT is not reliable enough for a fractal measure, and the tree geometry co-varies with contrast phase and vessel opacification - identifiability would collapse like idea-009's Murray-law tree."},
    {"n": 10, "question": "Is CT-CLIP using the pulmonary-artery-to-aorta diameter ratio (PA:A) as a pulmonary-hypertension cue behind its cardiomegaly and pericardial-effusion calls?", "status": "DROPPED", "why": "Good named X, but it overlaps C2's cardio-mediastinal geometry theme and CT-RATE has no direct pulmonary-hypertension label, so the output the ratio would drive is ambiguous; kept C2 (subcarinal angle) because its target label is explicit."}
  ],
  "quota_compliance": {
    "mode_A": ["C1"],
    "mode_B": ["C2", "C3"],
    "mode_C": ["C4", "C5"],
    "entry_point_1": [],
    "entry_point_2": ["C1", "C2", "C3", "C4", "C5"],
    "radiology_or_CT": "5/5",
    "CT_or_3D": "5/5",
    "dermatology": "0/5",
    "dataset_concentration": "Merlin/abdominal CT x2 (C1, C3); CT-RATE/CT-CLIP x2 (C2, C4); NLST/Sybil x1 (C5). No dataset exceeds two.",
    "design_grammar_spread": "natural-paired (C3), counterfactual-synthesis (C1, C5), representation-erasure (C2, C4). Deliberately diversified after scout-007 used representation-erasure for all five; the label-free natural-paired grammar (the only survivor structure in this loop) is used for C3.",
    "quota_note": "Met exactly for modes and datasets. All five are entry_point 2 (a well-performing model, an unconfirmed signal); each names the specific measurement and the specific artifact it would be confused with, as the entry-2 rule requires. No entry_point-1 candidate is included because no documented model-beats-radiologist gap with an obtainable checkpoint surfaced this cycle that was not already occupied by the backlog (knee pain, Mirai). Rather than pad with a weak gap, the honest short list is all entry-2; see quota_note limitation."
  },
  "candidates": [
    {
      "id": "C1",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "A",
      "entry_point": 2,
      "design_template": "counterfactual-synthesis",
      "title": "The cirrhosis model may be reading the bumpiness of the liver's edge",
      "question": "Is Merlin using liver surface nodularity - the regenerative-nodule bumpiness of the hepatic capsule - rather than liver volume or parenchymal fat, when its abdominal-CT representation flags cirrhosis?",
      "rung": {"target": 3, "current": 0, "move_up": "An automated LSN score plus a Merlin-score association is exploratory. A selective drop in the cirrhosis score after erasing (or counterfactually smoothing) the surface-nodularity signal, beyond liver-volume and steatosis controls, reaches rung 1. Scanner/phase/site replication gates rung 2; liver surface nodularity is already a named, biopsy-validated rung-3 quantity."},
      "deliverable_sentence": "Merlin is using liver surface nodularity - the fine nodular irregularity of the hepatic capsule caused by regenerative nodules - as its image signature of cirrhosis.",
      "X_measurement": {
        "X": "Liver surface nodularity (LSN) score: the mean perpendicular distance between the detected liver margin and a smoothed polynomial reference margin, in millimetres.",
        "how": "Segment the liver, extract the anterior/lateral capsule contour on the relevant slices, fit a smoothed reference line, and take the mean margin-to-reference distance. Smith et al. defined and validated this on routine CT (Radiology 2016, DOI 10.1148/radiol.2016151542, PMID 27089026); an FDA-cleared semi-automated liver-boundary tool and a fully automated deep-learning Auto-LSN (Eur Radiol 2026, DOI 10.1007/s00330-026-12346-5) exist.",
        "could_compute_today_without_asking_anyone": "Yes. LSN is a published, reproducible pixel-and-geometry measurement with automated implementations; no radiologist rating is needed. Availability of a runnable Auto-LSN weight or the semi-automated tool for the exact cohort is a Stage-0 item, not a conceptual barrier."
      },
      "suspected_signal": "In cirrhosis, diffuse regenerative nodules and fibrous bridging deform the liver capsule into a finely undulating surface. This nodularity is a spatial-frequency property of the organ boundary, in principle separable from total liver volume, lobar redistribution, and parenchymal fat (steatosis attenuation).",
      "specific_artifact_confused_with_signal": "Reconstruction kernel and slice thickness change edge sharpness and therefore apparent nodularity; ascites, perihepatic fat, and adjacent bowel can distort the detected margin; contrast phase shifts capsule conspicuity.",
      "keystone_prerequisite": "Merlin exposes a usable cirrhosis / advanced-chronic-liver-disease phenotype score, on an obtainable abdominal-CT cohort where automated LSN is measurable and varies enough independently of liver volume and steatosis to identify a selective-use effect.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest inspected primary artifacts: Merlin (arXiv:2406.06512; Nature 2026, DOI 10.1038/s41586-026-10181-8) reports phenotype classification over 692 phenotypes and 5-year chronic-disease prediction; Smith et al. (DOI 10.1148/radiol.2016151542) validated LSN against fibrosis stage (AUROC ~0.93 for cirrhosis). The actual Merlin phenotype string for cirrhosis, the checkpoint output head, and a compatible cohort were not directly inspected.",
      "keystone_residual_assumption": "The easy facts are that LSN is real and Merlin has hundreds of phenotypes. I am still assuming a cirrhosis-relevant output is actually exposed and that LSN varies independently of liver volume and steatosis in the usable sample rather than being nearly collinear with them; that independence, not the existence of LSN, is load-bearing.",
      "rung_reached": "No rung yet. Conditional rung 1 after selective erasure / surface-smoothing counterfactual; rung 2 after kernel/phase/site controls; rung 3 only then.",
      "dies_like_prior": "It resembles scout-006-c03 (Merlin diabetes reading liver fat) in model and organ, but asks a different output (cirrhosis, not diabetes) and a different, non-metabolic X (capsule geometry, not parenchymal attenuation), and it does not repeat that design's use-vs-association weakness because the primary readout is an image counterfactual (surface smoothing), not a score-X regression. No annotation-provenance failure applies because LSN is tool-computed from voxels.",
      "closest_prior_work": [
        {"citation": "Blankemeier et al., Merlin: a CT vision-language foundation model", "identifier": "arXiv:2406.06512; Nature 2026 DOI 10.1038/s41586-026-10181-8", "verified_fact": "Merlin is a 3D abdominal-CT foundation model evaluated on 692 EHR phenotypes and 5-year chronic-disease prediction.", "delta": "It did not report liver surface nodularity as the signal behind any hepatic phenotype."},
        {"citation": "Smith AD et al., Liver Surface Nodularity Quantification from Routine CT Images as a Biomarker for Detection and Evaluation of Cirrhosis", "identifier": "Radiology 2016, DOI 10.1148/radiol.2016151542, PMID 27089026", "verified_fact": "An automated LSN score from routine CT differentiates cirrhosis with high accuracy and near-perfect reproducibility.", "delta": "No image foundation model was studied; it established the biomarker, not model reliance."},
        {"citation": "Auto-LSN: fully automated liver surface nodularity quantification in CT based on deep learning", "identifier": "Eur Radiol 2026, DOI 10.1007/s00330-026-12346-5", "verified_fact": "A deep-learning tool computes LSN automatically, non-inferior to the FDA-cleared semi-automated software.", "delta": "It quantifies LSN; it does not ask whether a foundation model uses it."}
      ],
      "existing_assets": ["Merlin paper and released model assets", "Liver segmentation in standard whole-body CT segmenters", "Published LSN algorithm, FDA-cleared semi-automated liver-boundary tool, and Auto-LSN"],
      "smallest_decisive_experiment": "Stage 0: inspect Merlin's phenotype vocabulary/checkpoint for a cirrhosis output; validate automated LSN repeatability on a small public cohort and quantify LSN collinearity with liver volume and mean parenchymal HU. Confirmatory: build a validated surface-smoothing counterfactual (locally low-pass the capsule while preserving parenchyma and volume, discriminator-checked as in-distribution) and measure the paired change in Merlin's cirrhosis score; compare against volume-preserving and steatosis-preserving sham edits and an equal-magnitude random-boundary perturbation. Merlin uses X only if smoothing the surface selectively lowers the cirrhosis score.",
      "use_vs_association": "An LSN-versus-score regression is exploratory only. The use claim requires that a validated surface-smoothing counterfactual (or erasure of the validation-learned LSN direction) selectively changes Merlin's cirrhosis output beyond liver-volume and steatosis controls.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "Kernel/slice-thickness strata and site-held-out replication; kernel is the dominant residual because it changes edge sharpness. Not fully ruled out until Stage 0.",
        "positioning": "Minor after liver segmentation; margin detection restricted to reproducible anterolateral capsule.",
        "habitus": "Perihepatic fat aids margin detection but can bias it; measured as a nuisance.",
        "prevalence_referral": "Clinical abdominal-CT referral limits spectrum; second cohort needed.",
        "label_leakage": "Primary readout is the counterfactual score change from voxels; reports are not used."
      },
      "alternative_explanations": [
        {"alternative": "The model uses liver volume / lobar redistribution, not surface nodularity.", "resolution": "Hold volume fixed in the counterfactual and add a volume-direction control erasure."},
        {"alternative": "The model uses parenchymal steatosis (low attenuation), correlated with chronic liver disease.", "resolution": "Preserve parenchymal HU in the edit and add a steatosis-direction control."},
        {"alternative": "The counterfactual removes generic edge information rather than nodularity.", "resolution": "Discriminator in-distribution check, equal-magnitude random-boundary perturbation, and retained performance on unrelated hepatic outputs."}
      ],
      "anticipated_negative": {"classification": "sensitivity-limited", "reason": "A null smoothing effect could mean nodularity is encoded nonlinearly or that the edit was too weak; it becomes decisive only after a prespecified edit-magnitude and probe-reliability floor and an in-distribution check."},
      "cross_domain": {
        "borrowed_construct": "Surface roughness / spatial-frequency characterisation of a deformed boundary (morphometry).",
        "measurement_implied": "Mean margin-to-smooth-reference distance rather than any parenchymal statistic.",
        "if_analogy_dropped": "Without the roughness framing the experiment would test parenchymal texture or volume; the boundary-roughness construct fixes X as capsule undulation and dictates the smoothing counterfactual."
      },
      "remaining_legwork": "1 day to inspect Merlin's phenotype vocabulary and checkpoint; 3-5 days for a compatible cohort audit; ~1 week to validate automated LSN and build the smoothing counterfactual. First go/no-go in about 2 weeks.",
      "scores": {
        "clarity": {"value": 5, "why": "One model, one named boundary measurement, explicit volume/steatosis rivals."},
        "identifiability": {"value": 3, "why": "The volume/steatosis-preserving counterfactual separates surface geometry from the obvious rivals, but kernel-driven edge sharpness and edit specificity remain."},
        "medical_relevance": {"value": 4, "why": "It would name a biopsy-validated cirrhosis substrate as what a foundation model reads."},
        "interest": {"value": 3, "why": "The LSN-cirrhosis link is known; that a foundation model exploits it is a plausible but not startling finding."},
        "prior_legwork": {"value": 4, "why": "Merlin, liver segmentation, and validated/automated LSN tools all exist."},
        "feasibility": {"value": 3, "why": "Capped: keystone not inspected; Merlin output and cohort join uninspected."},
        "data_readiness": {"value": 3, "why": "Merlin and abdominal CT are accessible with work."},
        "evaluation_readiness": {"value": 4, "why": "LSN metrics are standard and reproducible; the counterfactual controls are custom."},
        "negative_result_value": {"value": 2, "why": "The anticipated null is sensitivity-limited."},
        "novelty_confidence": {"value": 3, "why": "Capped; no direct Merlin/LSN study was found in a bounded search."},
        "regret": {"value": 4, "why": "A cheap vocabulary/tool audit could settle whether a validated biomarker is the model's substrate."}
      },
      "priority_score": 3.35,
      "priority_arithmetic": "0.20*3 + 0.15*3 + 0.15*4 + 0.10*4 + 0.10*3 + 0.10*5 + 0.10*2 + 0.05*3 + 0.05*3 = 3.35",
      "unverified_claims": ["Merlin exposes a usable cirrhosis/ACLD score", "A runnable automated LSN tool transfers to the compatible cohort", "LSN varies independently of liver volume and steatosis in the usable sample"]
    },
    {
      "id": "C2",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "B",
      "entry_point": 2,
      "design_template": "representation-erasure",
      "title": "The chest-CT model may see the heart by watching the airway splay",
      "question": "Is CT-CLIP using the subcarinal angle - the widening of the tracheal bifurcation produced by left-atrial enlargement - rather than a direct read of cardiac silhouette size, when it calls cardiomegaly?",
      "rung": {"target": 3, "current": 0, "move_up": "A subcarinal-angle-versus-score association is exploratory. A selective drop in the cardiomegaly score after erasing the validation-learned subcarinal-angle direction, beyond cardiac-width, sex, and body-size controls, reaches rung 1. Scanner/site replication gates rung 2; the subcarinal angle is already a named radiographic sign at rung 3."},
      "deliverable_sentence": "CT-CLIP is using the subcarinal angle - the splaying of the carina caused by an enlarged left atrium - as part of how it detects cardiomegaly.",
      "X_measurement": {
        "X": "Subcarinal (interbronchial) angle in degrees, measured between the main-bronchial centerlines at the carina.",
        "how": "Segment the tracheobronchial tree (HU threshold / region growing), extract main-bronchus centerlines, and compute the angle at the bifurcation, as done on CT by Kubota et al. and Chen et al. (subcarinal angle 73+/-16 deg; positively correlated with left-atrial volume, r=0.34-0.40; BJR 2005, PMID 16110098). No reader grade is required.",
        "could_compute_today_without_asking_anyone": "Yes. Airway segmentation and centerline angle are deterministic geometry from voxels."
      },
      "suspected_signal": "The left atrium sits immediately below the carina; as it enlarges it pushes the two main bronchi apart, widening the subcarinal angle. A model taught 'cardiomegaly' from reports may pick up this airway splaying as a mediastinal proxy for cardiac enlargement rather than measuring the cardiac silhouette directly.",
      "specific_artifact_confused_with_signal": "The subcarinal angle also widens with female sex, obesity, and carina-to-spine position, and narrows with hyperinflation; these are biological/positional confounds, not scanner artifacts, and are the reason the angle's correlation with atrial size is only moderate.",
      "keystone_prerequisite": "CT-CLIP's preprocessing preserves carinal geometry well enough for the subcarinal angle to be encodable, AND, in CT-RATE, the subcarinal angle varies enough independently of overall cardiac width and of sex/habitus to identify a selective-use effect on the cardiomegaly output.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest inspected primary artifacts: the CT-RATE 18-label set includes 'Cardiomegaly' and CT-CLIP is released (arXiv:2403.17834); the subcarinal-angle-to-left-atrium link is established but modest and confounded (BJR 2005, PMID 16110098; AJR 1995, PMID 7717208). Neither the CT-CLIP preprocessing effect on airway geometry nor the CT-RATE joint distribution of angle, cardiac width, and sex was inspected.",
      "keystone_residual_assumption": "The easy fact is that the subcarinal angle correlates with left-atrial size. The load-bearing fact I am still assuming is that the angle carries information NOT already captured by gross cardiac width and sex - because if it is nearly collinear with cardiac width, no design can separate 'uses the airway angle' from 'uses heart size', and the whole point (an indirect airway cue) collapses.",
      "rung_reached": "No rung yet. Conditional rung 1 after selective erasure; rung 2 after acquisition/site controls; rung 3 thereafter.",
      "dies_like_prior": "It resembles idea-010 (cardiomegaly re-encoded as millilitres, killed CIRCULARITY), but crucially X is NOT the cardiac volume that defines the label - it is a distinct airway geometry that is a downstream mechanical consequence of only one cause of cardiomegaly (left-atrial enlargement). The endpoint is therefore not the label restated, and left-ventricular or pericardial causes of cardiomegaly would not move X, which is exactly the dissociation the design exploits.",
      "closest_prior_work": [
        {"citation": "Hamamci/Er/Simsar et al., CT-CLIP / CT-RATE foundation model", "identifier": "arXiv:2403.17834", "verified_fact": "CT-CLIP performs zero-shot multi-abnormality detection over 18 CT-RATE labels including Cardiomegaly.", "delta": "It did not ask which anatomical cue drives the cardiomegaly call."},
        {"citation": "CT assessment of tracheal carinal angle and its determinants", "identifier": "BJR 2005, PMID 16110098", "verified_fact": "On CT the subcarinal angle correlates with left-atrial volume but is also determined by sex, obesity, and carina position.", "delta": "It related geometry to anatomy, not to any model's use of it."},
        {"citation": "Widening of the tracheal bifurcation on chest radiographs as a sign of left atrial enlargement", "identifier": "AJR 1995, PMID 7717208, DOI 10.2214/ajr.164.5.7717208", "verified_fact": "Carinal widening is an accepted sign of left-atrial enlargement.", "delta": "Radiograph-era descriptive sign; no model decoded."}
      ],
      "existing_assets": ["CT-CLIP code/weights and CT-RATE with the Cardiomegaly label (non-contrast chest CT)", "Airway segmentation tools with carinal centerline extraction", "Published subcarinal-angle CT norms and determinants"],
      "smallest_decisive_experiment": "Stage 0: measure native-to-CT-CLIP-tensor agreement of the subcarinal angle and its partial correlation with cardiac transverse width, sex, and thoracic width in CT-RATE. Confirmatory: learn a validation-only subcarinal-angle direction, erase it from frozen CT-CLIP embeddings on locked test cases, and compare the cardiomegaly-score change against cardiac-width, sex, and equal-norm random-direction erasures. The model uses X only if angle erasure adds harm beyond cardiac-width and sex directions.",
      "use_vs_association": "A subcarinal-angle-versus-score correlation is exploratory. The use claim requires selective erasure of the validation-learned angle direction to change the cardiomegaly output beyond cardiac-width and sex directions.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "CT-RATE acquisition strata and site-held-out evaluation; angle is fairly robust to kernel. Not fully ruled out until Stage 0.",
        "positioning": "Centerline geometry reduces gantry-angle effects; carina-to-spine position measured as a nuisance.",
        "habitus": "Thoracic width and body size measured as nuisance directions; obesity is a known angle determinant.",
        "prevalence_referral": "Single collection; external replication needed.",
        "label_leakage": "Cardiomegaly labels came from reports, but X is voxel-computed and the readout is the model's own score change."
      },
      "alternative_explanations": [
        {"alternative": "The angle is just a proxy for overall cardiac width.", "resolution": "Separate and joint cardiac-width vs angle erasures; requires angle to add incremental effect - the identifiability crux."},
        {"alternative": "The angle indexes sex/habitus, which independently drive the label.", "resolution": "Sex- and thoracic-width-matched analysis and a separate sex-direction erasure."},
        {"alternative": "Erasure removes generic mediastinal information.", "resolution": "Equal-norm random and unrelated-structure direction controls plus retained performance on non-cardiac outputs."}
      ],
      "anticipated_negative": {"classification": "sensitivity-limited", "reason": "Because the angle-atrium correlation is only moderate and entangled with cardiac width, a null could reflect low independent variance rather than non-use; it is decisive only if Stage 0 confirms adequate independent angle variance and probe reliability."},
      "cross_domain": null,
      "remaining_legwork": "2 days for the preprocessing-geometry and collinearity audit in CT-RATE; ~1 week for erasure calibration. First go/no-go in about 1.5 weeks; the collinearity check could kill it in days.",
      "scores": {
        "clarity": {"value": 5, "why": "One model, one named angle, explicit cardiac-width and sex rivals."},
        "identifiability": {"value": 2, "why": "The subcarinal angle is only moderately correlated with atrial size and is confounded by sex, obesity, and cardiac width; separating airway-cue use from heart-size use may be underpowered."},
        "medical_relevance": {"value": 3, "why": "It would explain that a cardiomegaly call rides partly on an indirect airway sign, a modest but real interpretability point."},
        "interest": {"value": 4, "why": "A model detecting heart enlargement by watching the airway splay is a surprising, physician-legible mechanism."},
        "prior_legwork": {"value": 3, "why": "CT-CLIP, airway segmentation, and subcarinal-angle norms exist; the specific join does not."},
        "feasibility": {"value": 3, "why": "Capped; preprocessing geometry and collinearity uninspected."},
        "data_readiness": {"value": 4, "why": "CT-RATE is public and directly usable."},
        "evaluation_readiness": {"value": 3, "why": "Angle metrics exist; erasure selectivity must be calibrated."},
        "negative_result_value": {"value": 2, "why": "Sensitivity-limited null given modest independent variance."},
        "novelty_confidence": {"value": 3, "why": "Capped; no direct CT-CLIP/subcarinal-angle study found."},
        "regret": {"value": 3, "why": "Cheap to check but identifiability may prove too weak to be worth more."}
      },
      "priority_score": 3.10,
      "priority_arithmetic": "0.20*3 + 0.15*2 + 0.15*3 + 0.10*3 + 0.10*4 + 0.10*5 + 0.10*2 + 0.05*4 + 0.05*3 = 3.10",
      "unverified_claims": ["CT-CLIP preprocessing preserves the subcarinal angle", "The angle carries variance independent of cardiac width and sex in CT-RATE", "The angle direction is selectively erasable"]
    },
    {
      "id": "C3",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "B",
      "entry_point": 2,
      "design_template": "natural-paired",
      "title": "The model that 'predicts a blood count' may just be reading how bright the blood is",
      "question": "Is a CT foundation model that flags anemia using the CT attenuation of the blood pool - which scales with haematocrit - rather than any organ finding, as shown by whether the same patient's anemia readout swings when contrast is added within one session?",
      "rung": {"target": 3, "current": 0, "move_up": "A blood-HU-versus-score association is exploratory. Demonstrating that the anemia readout swings with the contrast-induced change in blood-pool attenuation, while haematocrit is fixed within the session, reaches rung 1 that the model reads blood-pool attenuation; showing the non-contrast blood HU is the operative variable (which is what encodes haematocrit) reaches rung 3."},
      "deliverable_sentence": "The model is using the CT attenuation of the blood pool - the radiodensity of blood, which rises and falls with haematocrit - to flag anemia.",
      "X_measurement": {
        "X": "Mean CT attenuation (HU) of the blood pool, sampled in the aorta / inferior vena cava / cardiac chambers, on non-contrast CT.",
        "how": "Segment the aorta and IVC (e.g., TotalSegmentator) and take the mean luminal HU. Blood attenuation correlates with haemoglobin (LV cavity r~0.59, aorta r~0.56; anemia threshold ~<=36.5 HU): Medicine 2021 (PMC9191293), unenhanced-thorax anemia prediction (PMID 12625080), and aorta/IVC correlation (PMC9816921). No reader input is required.",
        "could_compute_today_without_asking_anyone": "Yes. Mean luminal HU from an off-the-shelf vessel segmentation is trivial to compute."
      },
      "suspected_signal": "Beer-Lambert: X-ray attenuation of blood scales with its protein/iron content, so haematocrit sets blood radiodensity. Anemic blood is hypodense (a recognised 'flat', low-HU aorta), polycythaemic blood hyperdense. A model that appears to 'predict a blood count from an image' may simply be reading this physical attenuation, and adding iodinated contrast - which raises blood HU by hundreds of units while haematocrit is unchanged - should mislead it if that is the cue.",
      "specific_artifact_confused_with_signal": "Iodinated contrast, tube voltage (kVp), and beam-hardening all change blood HU independently of haematocrit; these are exactly the levers the natural-paired design uses, so the 'artifact' is deployed deliberately rather than merely feared.",
      "keystone_prerequisite": "The model exposes an anemia (or low-haemoglobin) output, AND an obtainable cohort contains same-session non-contrast and post-contrast abdominal CT of the same patients, so that blood-pool HU changes by a large known amount while haematocrit and anatomy are fixed.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest inspected primary artifacts: Merlin (arXiv:2406.06512) classifies 692 phenotypes (anemia is a standard phecode, but its presence in Merlin's exposed set was not confirmed); the blood-HU-to-haemoglobin physics is well validated (PMC9191293; PMID 12625080). The specific Merlin anemia head and a same-session paired-phase cohort were not inspected.",
      "keystone_residual_assumption": "The easy facts are that blood HU tracks haemoglobin and that many patients get pre- and post-contrast scans. The load-bearing facts I am still assuming are that an anemia output is actually exposed by the model and that haematocrit is truly unchanged over the minutes between phases (usually true, but acute haemorrhage/transfusion cases must be excluded).",
      "rung_reached": "No rung yet. The natural-paired swing gives rung 1/2 without labels; the non-contrast HU as the haematocrit encoder gives rung 3.",
      "dies_like_prior": "It uses the same structural move as the loop's one survivor, idea-004: comparing a model to itself across two acquisitions of identical anatomy so that no ground-truth label enters the primary measurement. Here the two acquisitions are non-contrast vs post-contrast rather than two reconstructions. No annotation-provenance failure applies because the primary readout is the label-free paired score swing.",
      "closest_prior_work": [
        {"citation": "Prediction of anemia on unenhanced CT of the thorax", "identifier": "PMID 12625080", "verified_fact": "Blood attenuation on unenhanced CT predicts anemia; a hyperattenuating aortic wall / dense septum signals it.", "delta": "It used simple HU thresholds read by humans, not a foundation model, and did not test whether a model relies on the attenuation."},
        {"citation": "Prediction of anemia on enhanced CT using virtual non-contrast reconstructions", "identifier": "Medicine 2021, PMC9191293", "verified_fact": "LV/aortic attenuation correlates with haemoglobin (r~0.56-0.59); ~<=36.5 HU thresholds anemia.", "delta": "Establishes the physics/threshold; no model-use question."},
        {"citation": "Merlin: a CT vision-language foundation model", "identifier": "arXiv:2406.06512", "verified_fact": "A CT foundation model classifies hundreds of EHR phenotypes off-the-shelf.", "delta": "Did not test whether an anemia phenotype is driven by blood-pool attenuation."}
      ],
      "existing_assets": ["A CT foundation model with a phenotype/finding head plausibly including anemia (Merlin candidate)", "Vessel segmentation (TotalSegmentator) for blood-pool HU", "Established blood-HU-haemoglobin literature and thresholds", "Routine same-session pre/post-contrast abdominal CT pairs in clinical archives"],
      "smallest_decisive_experiment": "Stage 0: confirm an exposed anemia output and identify a set of patients with same-session non-contrast and post-contrast CT; verify blood-pool HU repeatability. Primary (label-free): run the frozen model on both phases of each patient and measure the paired change in the anemia score against the measured blood-pool HU change. If the anemia readout swings with the contrast-induced HU change, the model reads blood-pool attenuation. Confirmatory rung-3: restrict to the non-contrast arm and show the anemia score tracks non-contrast blood HU (the haematocrit encoder) beyond organ-based directions via erasure.",
      "use_vs_association": "The observational blood-HU-versus-score relation is exploratory. The use test is the within-patient paired swing: haematocrit is fixed but blood HU is forced to change by contrast, so a swing can only mean the model is reading blood-pool attenuation.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "Paired phases are same scanner/session, so scanner/site are held fixed within pair; kVp differences between phases are recorded.",
        "positioning": "Same session, near-identical positioning within pair.",
        "habitus": "Held fixed within patient.",
        "prevalence_referral": "Referral mix does not affect the within-patient contrast; external cohort still strengthens generality.",
        "label_leakage": "The primary readout uses no anemia label at all; only the optional rung-3 arm touches the haemoglobin value."
      },
      "alternative_explanations": [
        {"alternative": "The anemia score swings because contrast changes organ enhancement (kidney, spleen), not blood HU.", "resolution": "Regress the swing on measured blood-pool HU change while holding organ-enhancement measures fixed; add a blood-only local HU-shift counterfactual."},
        {"alternative": "The model reads bone-marrow or splenic attenuation as the anemia cue.", "resolution": "Measure marrow/splenic HU and include as competing directions in the confirmatory erasure."},
        {"alternative": "No swing because the model encodes anemia nonlinearly.", "resolution": "Probe-reliability floor and a magnitude check that the induced HU change exceeds the anemia HU threshold band."}
      ],
      "anticipated_negative": {"classification": "decisive", "reason": "If the induced blood-HU change is large (hundreds of HU, well past the anemia threshold band) yet the anemia readout does not swing, the model is not reading blood-pool attenuation - a decisive negative against this specific X, provided the encoding/reliability gate is met."},
      "cross_domain": {
        "borrowed_construct": "Beer-Lambert attenuation / densitometry from radiation physics.",
        "measurement_implied": "Mean luminal blood HU and its forced contrast-induced change, not any organ morphology.",
        "if_analogy_dropped": "Without the densitometry framing there is no reason to expect contrast to be a decisive probe; the physics predicts that a haematocrit reader must be fooled by contrast, which is the entire experiment."
      },
      "remaining_legwork": "1 day to confirm an exposed anemia output; 3-5 days to assemble same-session paired-phase cases; ~2 days for blood-pool HU pipeline. First go/no-go in about 1-1.5 weeks.",
      "scores": {
        "clarity": {"value": 5, "why": "One named physical quantity, one output, a decisive paired probe."},
        "identifiability": {"value": 4, "why": "The within-session contrast swing isolates blood-pool attenuation from anatomy with haematocrit fixed; residual is organ-enhancement co-variation, addressed by the blood-only counterfactual."},
        "medical_relevance": {"value": 3, "why": "It deflates or confirms 'AI reads blood counts from images' - a useful skeptical result, modest direct clinical utility."},
        "interest": {"value": 4, "why": "A foundation model secretly obeying Beer-Lambert is a clean, surprising story with a decisive test."},
        "prior_legwork": {"value": 4, "why": "Blood-HU physics is mature; vessel segmentation is off-the-shelf; paired scans are routine."},
        "feasibility": {"value": 3, "why": "Capped; anemia output and paired-phase cohort uninspected."},
        "data_readiness": {"value": 3, "why": "Paired-phase CT is common but assembling a labelled, model-compatible set needs work."},
        "evaluation_readiness": {"value": 4, "why": "HU is trivial and the paired design needs no bespoke metric."},
        "negative_result_value": {"value": 3, "why": "A no-swing result is a decisive negative against blood-pool attenuation as the cue."},
        "novelty_confidence": {"value": 3, "why": "Capped; the physics is old but the model-use test appears unaddressed."},
        "regret": {"value": 4, "why": "Cheap, decisive, and re-usable across any CT model with a haematologic output."}
      },
      "priority_score": 3.55,
      "priority_arithmetic": "0.20*3 + 0.15*4 + 0.15*3 + 0.10*4 + 0.10*4 + 0.10*5 + 0.10*3 + 0.05*3 + 0.05*3 = 3.55",
      "unverified_claims": ["A CT foundation model exposes an anemia/low-haemoglobin output", "Same-session non-contrast+contrast pairs are obtainable at adequate number", "Haematocrit is stable across the paired scans (transfusion/haemorrhage excluded)"]
    },
    {
      "id": "C4",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "C",
      "entry_point": 2,
      "design_template": "representation-erasure",
      "title": "The emphysema call may read the shape of the holes, not just how many",
      "question": "Is CT-CLIP's emphysema readout using the morphometric complexity of the low-attenuation clusters - the power-law size exponent that distinguishes many small holes from a few coalesced ones - rather than only their total extent?",
      "rung": {"target": 3, "current": 0, "move_up": "An association between the cluster-size exponent and the emphysema score is exploratory. A selective change in the emphysema score after erasing the validation-learned complexity direction, orthogonalised to LAA% extent, reaches rung 1. Reconstruction/site controls gate rung 2; the low-attenuation-cluster power-law exponent is a named quantity at rung 3."},
      "deliverable_sentence": "CT-CLIP is using the morphometric complexity of emphysema - the power-law size distribution of the low-attenuation clusters (few large coalesced holes versus many small ones) - not merely the fraction of lung below -950 HU.",
      "X_measurement": {
        "X": "The exponent D of the cumulative size distribution of low-attenuation-area (LAA, <-950 HU) clusters, and/or the 3D box-counting fractal dimension of the LAA mask; lower D means fewer, larger, coalesced holes.",
        "how": "Threshold the lung at -950 HU, label connected LAA clusters, fit the cumulative cluster-size distribution to a power law to get D (Mishima et al., PNAS 1999, DOI 10.1073/pnas.96.16.8829), or compute box-counting Dbox3D; complexity predicts COPD survival independent of extent (Eur Radiol 2018, PMID 29959456; Sci Rep 2023, s41598-023-40950-8). No reader input required.",
        "could_compute_today_without_asking_anyone": "Yes as a defined computation on the LAA mask - subject to the caveat that CT-CLIP's resampling/crop may alter fine cluster structure, which is the Mode-C keystone risk."
      },
      "suspected_signal": "Emphysema progresses by coalescence: destroyed alveolar walls merge small low-attenuation regions into large connected holes, a percolation-like transition. The cluster-size exponent captures this connectivity and is provably not the same as the total low-attenuation fraction, so a model could exploit hole topology beyond hole amount.",
      "specific_artifact_confused_with_signal": "Reconstruction kernel and image noise change small-cluster counts and therefore the exponent; slice thickness and CT-CLIP's isotropic resampling change 3D connectivity; motion/inspiration alter apparent LAA.",
      "keystone_prerequisite": "CT-CLIP's fixed preprocessing (HU clip to [-1000,1000], resample, centre crop, per the ledger) preserves the LAA cluster-size structure enough that the complexity exponent is encodable, AND complexity varies enough independently of LAA% extent in CT-RATE to identify a selective-use effect.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest inspected primary artifacts: CT-RATE's 18-label set includes 'Emphysema' and CT-CLIP is released (arXiv:2403.17834); the cluster-size power-law and its extent-independent prognostic value are established (Mishima PNAS 1999 DOI 10.1073/pnas.96.16.8829; Eur Radiol 2018 PMID 29959456). The ledger records CT-CLIP preprocessing (clip/resample/centre crop), but its effect on cluster structure and the CT-RATE complexity/extent joint distribution were not inspected.",
      "keystone_residual_assumption": "The easy fact is that cluster complexity is measurable and prognostic on native CT. The load-bearing fact I am still assuming is that it survives CT-CLIP's resampling and crop as encodable information and is not effectively collinear with LAA% after preprocessing; if resampling smears the small clusters, the exponent is gone before the model ever sees it.",
      "rung_reached": "No rung yet. Mode C: mechanism is strong but the encoding/preservation gate is uninspected.",
      "dies_like_prior": "It resembles idea-008 (does Sybil use emphysema geometry) and scout-007-c07 (fibrosis holes at the pleural edge), but differs on all three axes from idea-008 - different model (CT-CLIP), dataset (CT-RATE), and output (the emphysema label, not cancer risk) - and its estimand is specifically the complexity dimension orthogonalised to extent, not emphysema presence. Unlike scout-007-c07 it is whole-lung percolation of emphysema, not pleural-edge honeycombing of fibrosis. It is a brand-new question, not a revival of idea-008.",
      "closest_prior_work": [
        {"citation": "Mishima et al., Complexity of terminal airspace geometry assessed by CT", "identifier": "PNAS 1999, 96:8829-8834, DOI 10.1073/pnas.96.16.8829", "verified_fact": "LAA-cluster cumulative size distribution follows a power law whose exponent D measures terminal-airspace complexity, distinct from LAA%.", "delta": "It characterised the tissue, not what any model reads."},
        {"citation": "Low morphometric complexity of emphysematous lesions predicts survival in COPD", "identifier": "Eur Radiol 2018, DOI 10.1007/s00330-018-5551-7, PMID 29959456", "verified_fact": "Power-law exponent Dsize and box-counting Dbox3D independently predict COPD survival.", "delta": "Prognostic association; no foundation-model decoding."},
        {"citation": "CT-CLIP / CT-RATE foundation model", "identifier": "arXiv:2403.17834", "verified_fact": "CT-CLIP detects Emphysema zero-shot among 18 CT-RATE labels.", "delta": "It did not test whether the emphysema call uses cluster complexity vs extent."}
      ],
      "existing_assets": ["CT-CLIP weights and CT-RATE with the Emphysema label", "Standard LAA thresholding and connected-component/fractal tooling", "Published Dsize/Dbox3D methods with COPD validation"],
      "smallest_decisive_experiment": "Stage 0: on CT-RATE, compute Dsize/Dbox3D and LAA% on native volumes and on CT-CLIP's exact input tensor, and check (a) native-to-tensor agreement of the exponent and (b) residual variance of complexity after regressing out LAA%. Confirmatory: learn a validation-only complexity direction orthogonal to the LAA%-extent direction, erase it from frozen embeddings on locked test cases, and compare the emphysema-score change against LAA%-direction and equal-norm random-direction erasures. The model uses complexity only if erasing it, but not extent, changes the emphysema call.",
      "use_vs_association": "A complexity-versus-score correlation is exploratory. The use test is selective erasure of the extent-orthogonalised complexity direction changing the emphysema output beyond the LAA%-extent direction.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "Kernel and noise strongly affect small-cluster counts; kernel strata and, if available, geometry-matched reconstruction pairs (CT-RATE has many) test robustness. Dominant residual.",
        "positioning": "Minor; inspiration state affects LAA and is measured as a nuisance.",
        "habitus": "Minor for lung LAA.",
        "prevalence_referral": "Single collection; external emphysema cohort needed.",
        "label_leakage": "Emphysema labels came from reports, but X is a voxel computation and the readout is the model's own score change."
      },
      "alternative_explanations": [
        {"alternative": "The model uses only LAA% extent; complexity is a passenger.", "resolution": "Orthogonalise complexity to extent and require the complexity-direction erasure to add effect beyond the extent direction."},
        {"alternative": "The exponent is a noise/kernel artifact.", "resolution": "Kernel strata and geometry-matched reconstruction pairs; require the effect to persist within kernel."},
        {"alternative": "Preprocessing destroys clusters, so any null is uninterpretable.", "resolution": "The Stage-0 native-to-tensor encoding gate must pass before the erasure result is interpreted."}
      ],
      "anticipated_negative": {"classification": "sensitivity-limited", "reason": "A null erasure effect could mean complexity was not preserved through preprocessing or was encoded nonlinearly; it is decisive only after the native-to-tensor encoding gate and a probe-reliability floor are met, otherwise uninterpretable."},
      "cross_domain": {
        "borrowed_construct": "Percolation / cluster-size scaling from statistical physics.",
        "measurement_implied": "The power-law exponent of the LAA cluster-size distribution, not the mean LAA%.",
        "if_analogy_dropped": "Without percolation the experiment would test emphysema extent, already a routine feature; the percolation construct changes X to the cluster-size exponent and predicts a coalescence (decreasing-exponent) signature the extent measure cannot express."
      },
      "remaining_legwork": "3-4 days for the native-to-tensor encoding and complexity/extent collinearity audit; ~1 week for erasure calibration. First go/no-go in about 1.5 weeks; the encoding gate can kill it early.",
      "scores": {
        "mechanism_clarity": {"value": 5, "why": "A specific named exponent (Dsize / Dbox3D) with an explicit coalescence/percolation mechanism and a measurement."},
        "identifiability": {"value": 3, "why": "Orthogonalising complexity to extent and using kernel strata attacks the main rivals, but preprocessing preservation and complexity/extent entanglement remain."},
        "interest": {"value": 4, "why": "A model reading the topology of emphysema rather than its amount would be a genuinely new statement about the emphysema label."},
        "medical_relevance": {"value": 3, "why": "Complexity carries extent-independent prognostic signal, but the immediate clinical consequence is modest."},
        "clarity": {"value": 4, "why": "Crisp, though 'complexity beyond extent' requires careful orthogonalisation to state precisely."}
      },
      "mode_c_priority_score": 3.90,
      "priority_arithmetic": "0.30*5 + 0.25*3 + 0.20*4 + 0.15*3 + 0.10*4 = 3.90",
      "feasibility_for_information": {"value": 3, "why": "Capped; the preprocessing-preservation keystone is uninspected and is the main risk."},
      "novelty_confidence_for_information": {"value": 3, "why": "Capped; no CT-CLIP/complexity study found, but emphysema-complexity is a mature literature and adjacency is real."},
      "unverified_claims": ["Cluster complexity survives CT-CLIP preprocessing as encodable information", "Complexity has adequate variance independent of LAA% in CT-RATE", "The complexity direction is selectively erasable"]
    },
    {
      "id": "C5",
      "parent_ids": [],
      "revival_basis": null,
      "search_mode": "C",
      "entry_point": 2,
      "design_template": "counterfactual-synthesis",
      "title": "The lung-cancer model may read the aorta as an ageing clock",
      "question": "Is Sybil using thoracic aortic tortuosity - the age- and degeneration-driven elongation and buckling of the aorta - as a systemic-ageing cue for future lung-cancer risk, separable from the lung parenchyma?",
      "rung": {"target": 3, "current": 0, "move_up": "A tortuosity-versus-risk association is exploratory. A selective change in Sybil's risk after a validated aortic-straightening counterfactual (or erasure of the tortuosity direction), beyond age, emphysema, and calcification controls, reaches rung 1. Scanner/site controls gate rung 2; aortic tortuosity is a named quantity at rung 3."},
      "deliverable_sentence": "Sybil is using thoracic aortic tortuosity - the elongated, buckled course an ageing, degenerating aorta takes - as a systemic-ageing cue when it predicts future lung cancer.",
      "X_measurement": {
        "X": "Thoracic aortic tortuosity index = (aortic centerline length / straight end-to-end chord) - 1, from the arch to the diaphragm.",
        "how": "Segment the thoracic aorta (e.g., TotalSegmentator), extract the centerline, and take the arc-to-chord ratio; tortuosity rises with age (centreline length ~191 cm <65y vs ~213 cm >=65y; PLOS One 2019, PMID 31013307, DOI 10.1371/journal.pone.0215549; Eur J Radiol 2018). No reader input required.",
        "could_compute_today_without_asking_anyone": "Yes. Aortic segmentation and centerline arc/chord are deterministic geometry from voxels."
      },
      "suspected_signal": "With age, elastin fragmentation lengthens and stiffens the aorta faster than the thorax grows, so the vessel buckles into a more tortuous course - mechanically like an axially-loaded column exceeding its buckling length. Because smoking and ageing drive both aortic degeneration and lung-cancer risk, Sybil's residual (nodule-independent) signal may partly be this vascular-ageing geometry rather than a lung finding.",
      "specific_artifact_confused_with_signal": "Chronological age itself, aortic wall calcification (a co-located degeneration marker), body height/thoracic length, and scan framing all move tortuosity; age and calcification are the biological confounds the design must beat.",
      "keystone_prerequisite": "Sybil's input tensor preserves aortic centerline geometry, AND, in NLST, aortic tortuosity carries enough variance independent of chronological age and emphysema to identify a selective-use effect on Sybil's risk score.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Nearest inspected primary artifacts: Sybil is released and retains nodule-independent ('background') predictive performance (AUC 0.81 at 2y, 0.69 at 6y after removing nodule scans; Mikhael et al., JCO 2023, PMID 36634294; DOI 10.1200/JCO.22.01345); aortic tortuosity is a validated age-increasing centerline measure (PMID 31013307). Sybil's preprocessing effect on aortic geometry and the NLST tortuosity/age/emphysema joint distribution were not inspected.",
      "keystone_residual_assumption": "The easy facts are that tortuosity is measurable and rises with age, and that Sybil has residual signal. The load-bearing fact I am still assuming is that tortuosity has usable variance beyond age within NLST's narrow heavy-smoker age band - if tortuosity is nearly a deterministic function of age here, no design can separate 'uses the aorta' from 'uses age', which is the identifiability crux and the way idea-009's vascular geometry claim died.",
      "rung_reached": "No rung yet. Mode C: strong mechanism, uninspected encoding and age-independence gates.",
      "dies_like_prior": "It shares the 'vascular ageing clock' theme with scout-007-c02 / idea-015 (Mirai reading breast arterial calcification) and the vascular-geometry ambition of idea-009 (Murray tree law, killed IDENTIFIABILITY). It differs by using structural tortuosity (not calcification), the thoracic aorta (not breast arteries), and Sybil (not Mirai); against idea-009's failure it uses a single global centerline measure with a straightening counterfactual rather than a branching-ratio law across a tree, which gives a cleaner use-test - though age entanglement remains the primary risk and is scored as such.",
      "closest_prior_work": [
        {"citation": "Mikhael et al., Sybil: validated deep learning for future lung-cancer risk", "identifier": "JCO 2023, PMID 36634294, DOI 10.1200/JCO.22.01345", "verified_fact": "Sybil predicts 6-year lung-cancer risk from a single LDCT and keeps predictive power after nodule-bearing scans are removed.", "delta": "It did not attribute the residual signal to any specific vascular measurement."},
        {"citation": "Auditing Sybil: Explaining Deep Lung Cancer Risk Prediction Through Generative Interventional Attributions", "identifier": "arXiv:2602.02560 (2026)", "verified_fact": "A 2026 preprint applies generative interventional attribution to Sybil.", "delta": "This is the closest novelty warning: its attribution inventory must be inspected for aortic/vascular features before advancement; it is not known to test tortuosity specifically."},
        {"citation": "Tortuosity of the descending thoracic aorta: normal values by age", "identifier": "PLOS One 2019, PMID 31013307, DOI 10.1371/journal.pone.0215549", "verified_fact": "Aortic tortuosity index and centreline length increase significantly with age.", "delta": "Established the measurement and its age dependence; no model decoded."}
      ],
      "existing_assets": ["Sybil code/weights and the NLST pathway established in prior cycles", "Aortic segmentation and centerline tools (TotalSegmentator)", "Published aortic-tortuosity norms by age"],
      "smallest_decisive_experiment": "Stage 0: inspect the 2026 Sybil-audit preprint for vascular features; measure native-to-Sybil-tensor agreement of the tortuosity index and its partial correlation with age and emphysema in NLST. Confirmatory: build a validated aortic-straightening counterfactual (warp the aorta toward a straighter centerline while preserving parenchyma, discriminator-checked in-distribution) and measure the paired change in Sybil's risk; compare against age-, emphysema-, and calcification-direction erasures and an equal-magnitude random-warp control. Sybil uses X only if straightening the aorta selectively lowers risk beyond age and emphysema.",
      "use_vs_association": "A tortuosity-versus-risk correlation is exploratory. The use test is a validated aortic-straightening counterfactual (or tortuosity-direction erasure) changing Sybil's risk beyond age, emphysema, and calcification directions.",
      "standing_confounds_addressed": {
        "scanner_vendor_protocol_reconstruction_site": "NLST kernel/scanner strata and paired reconstructions; site is masked and remains a limitation.",
        "positioning": "Centerline arc/chord is fairly framing-robust; thoracic coverage checked.",
        "habitus": "Body height / thoracic length measured as a nuisance (tortuosity scales with aortic length).",
        "prevalence_referral": "NLST uniform screening pathway addresses referral but only in heavy smokers, narrowing the age range - the key limitation for age-independence.",
        "label_leakage": "Cancer outcome cannot be printed into aortic geometry; X is voxel-computed and the readout is the model's score change."
      },
      "alternative_explanations": [
        {"alternative": "Tortuosity is a proxy for chronological age, which drives risk.", "resolution": "Age-matched analysis and a separate age-direction erasure; require tortuosity to add incremental effect - the crux."},
        {"alternative": "Tortuosity co-varies with aortic calcification, the real cue.", "resolution": "Measure aortic-wall calcium and include as a competing direction; straightening counterfactual leaves calcium in place."},
        {"alternative": "The straightening warp removes generic image information.", "resolution": "In-distribution discriminator check, equal-magnitude random-warp control, and retained performance on unrelated outputs."}
      ],
      "anticipated_negative": {"classification": "decisive", "reason": "If tortuosity is reliably encoded yet a validated straightening counterfactual leaves Sybil's risk unchanged while age erasure moves it, the vascular-ageing-geometry mechanism is directly weakened - conditional on the encoding and age-independence gates."},
      "cross_domain": {
        "borrowed_construct": "Euler buckling / axial elongation of a pressure-loaded elastic tube (mechanics).",
        "measurement_implied": "The centerline arc-to-chord tortuosity index and its response to a straightening warp, not vessel diameter or calcium.",
        "if_analogy_dropped": "Without the buckling framing the experiment would measure aortic diameter or calcification (already studied); the mechanics construct fixes X as tortuosity and motivates the straightening counterfactual as the decisive intervention."
      },
      "remaining_legwork": "1 day to inspect the 2026 Sybil-audit preprint; 2 days for native-to-tensor tortuosity agreement; 3-5 days for NLST tortuosity/age/emphysema collinearity; ~1 week to build and validate the straightening counterfactual. First go/no-go in about 2 weeks.",
      "scores": {
        "mechanism_clarity": {"value": 5, "why": "A specific tortuosity index with an explicit buckling/elongation mechanism and a straightening intervention."},
        "identifiability": {"value": 3, "why": "The straightening counterfactual plus age/emphysema/calcification controls attack the rivals, but NLST's narrow age band makes tortuosity-age separation the persistent threat."},
        "interest": {"value": 4, "why": "A lung-cancer model reading the aorta as an ageing clock is surprising and physician-legible."},
        "medical_relevance": {"value": 3, "why": "It would reframe part of Sybil's residual risk as systemic vascular ageing rather than occult tumour signal; modest immediate consequence."},
        "clarity": {"value": 4, "why": "The model-uses-X sentence is concrete; the age-independence caveat keeps it from a 5."}
      },
      "mode_c_priority_score": 3.90,
      "priority_arithmetic": "0.30*5 + 0.25*3 + 0.20*4 + 0.15*3 + 0.10*4 = 3.90",
      "feasibility_for_information": {"value": 3, "why": "Capped; preprocessing preservation and age-independence uninspected."},
      "novelty_confidence_for_information": {"value": 2, "why": "Capped and lowered: a 2026 Sybil interventional-attribution preprint (arXiv:2602.02560) is a near neighbour and must be inspected for vascular features before advancing."},
      "unverified_claims": ["Sybil preprocessing preserves aortic centerline geometry", "Aortic tortuosity has usable variance independent of age within NLST", "arXiv:2602.02560 does not already attribute Sybil risk to aortic/vascular geometry"]
    }
  ],
  "portfolio_ranking": {
    "mode_A_B": "C3 3.55, C1 3.35, C2 3.10 under the standard rubric. C3 ranks first because its primary readout is label-free (the within-session contrast swing) and its anticipated negative is decisive; C2 ranks last because the subcarinal angle's independence from cardiac width and sex is genuinely doubtful.",
    "mode_C": "C4 3.90, C5 3.90 under the separate Mode C rubric; these are not comparable to the Mode A/B scores. Both are keystone-gated on whether their measurable X survives the model's preprocessing.",
    "recommendation": "Inspect C3 first: it is the cheapest decisive test, needs no label in the primary readout, reuses the loop's only surviving structural move (model-vs-itself across two acquisitions of identical anatomy), and generalises to any CT model with a haematologic output. Among Mode C, inspect C4's preprocessing-preservation gate before C5's, because it can be settled with a purely computational native-to-tensor comparison and no cohort assembly.",
    "critical_caution": "All five are pre-keystone; none currently supports its deliverable sentence. C1, C3, and C4 hinge on whether the target model actually exposes the relevant output (cirrhosis, anemia, emphysema) - a one-day vocabulary inspection that should gate any further work. C2 should be killed immediately if Stage 0 shows the subcarinal angle is near-collinear with cardiac width. C5 should be paused if the 2026 Auditing-Sybil preprint already attributes risk to aortic geometry, or if NLST's age band leaves tortuosity with no age-independent variance."
  }
}


===== STAGE TASK =====
<!-- stage: novelty_audit -->
# Novelty audit

`candidates_all.json` (in your context) is this cycle's merged candidate pool
across all tracks. Audit every candidate's novelty claim by *searching*, not
recalling. A model asserting "this is novel" is worthless; the audit is the
verification path.

For each candidate, in order:

1. **Neighbors.** Search for the three closest prior works. Cite each with an
   identifier (DOI, arXiv ID, or exact title + venue + year) and one line on
   what it did. If after a genuine search you find fewer than three, list what
   you found and mark the candidate `NO_NEIGHBORS_FOUND` -- this is a flag for
   human verification, never evidence of novelty.
2. **Delta.** One sentence: precisely what this candidate does that the
   closest neighbor did not. "More data" or "a different dataset" is a weak
   delta; say so if it is one.
3. **Why not done.** Exactly one of:
   - `NEW_CAPABILITY` -- name the tool, dataset, or model that only recently
     made this testable;
   - `BLIND_SPOT` -- state the concrete reason the field missed it (framing,
     incentive, disciplinary boundary);
   - `TRIED_AND_FAILED` -- cite the attempt. Red flag: explain what would be
     different this time or recommend the kill.
4. **Verdict.** Calibrated vocabulary -- absence of a found duplicate is NOT
   verified novelty: `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` (thorough
   multi-source search, neighbors found and distinguished),
   `NO_DUPLICATE_FOUND_LIMITED_SEARCH` (search bounded or access-limited),
   `INCREMENTAL`, or `DUPLICATE_FOUND` (recommend kill with the citation).

Also write `novelty_manifest.json` -- the reproducibility record:
`{"searched_at": "...", "queries": [{"query": "...", "source": "..."}],
"neighbors": [{"candidate": "C1", "identifier": "...", "access":
"full_text|abstract|search_summary", "establishing_passage": "..."}]}`.

Write `novelty_audit.md` in the assigned output directory: one section per
candidate, headed by the candidate's title and track, containing exactly the
four items above. Close the file with a summary table: candidate / verdict /
why-not-done code. Number candidates by their position in
`candidates_all.json` as C1..Cn across ALL tracks -- do not renumber per
track (no W1/F1); the orchestrator maps the summary table back to the ledger
by these merged indices.

Do not write code. Do not modify any other file.

