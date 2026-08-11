You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/018
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

51 tracked ideas. Latest state per idea; full history in ledger.jsonl.

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **IDENTIFIABILITY_FAILURE** x2: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.
- **DATA_ACCESS** x1: Required data, checkpoints, or mappings are not obtainable in practice.
- **ANNOTATION_PROVENANCE** x1: Inference depends on who assigned labels / what they could see, and that is undocumented or contaminated.
- **CIRCULARITY** x1: The endpoint is a re-encoding of the input or of the thing being tested.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **scout-006-c04** [NOVEL_UNVERIFIED, score 4.1, audited 2026-08-10] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-009-c08** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.1, audited 2026-08-11] -- The glioblastoma prognosticator may be reading the invasion front's roughness
- **scout-009-c06** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.0, audited 2026-08-11] -- The CT spirometer may be reading the diaphragm as a pressure-loaded membrane
- **scout-007-c06** [NOVEL_UNVERIFIED, score 3.9, audited 2026-08-10] -- The effusion model may be reading whether pleural fluid still obeys gravity
- **scout-008-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.9, audited 2026-08-11] -- The emphysema call may read the shape of the holes, not just how many
- **scout-008-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.9, audited 2026-08-11] -- The lung-cancer model may read the aorta as an ageing clock
- **scout-009-c09** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.8, audited 2026-08-11] -- The arterial-calcification score may be reading inspiratory depth
- **scout-009-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.6, audited 2026-08-11] -- The risk model may be reading the breast's lines of force
- **scout-007-c08** [NOVEL_UNVERIFIED, score 3.6, audited 2026-08-10] -- The PE model may be reading how completely blood and contrast have mixed
- **scout-006-c05** [NOVEL_UNVERIFIED, score 3.4, audited 2026-08-10] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two
- ... and 9 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- counterfactual-synthesis: 3
- representation-erasure: 3
- regional-substitution: 3
- natural-paired: 2
- model-output-perturbation: 2
- longitudinal-within-subject: 1

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
- **idea-017** [SHORTLISTED/DEBATED/baseline] -- A lung-cancer model may be reading a mechanically remodeled trachea
- **idea-018** [SHORTLISTED/CRITIQUED/baseline] -- The brain-tumor prognosticator may be weighing the chewing muscle
- **idea-019** [SHORTLISTED/SCOUTED/wide] -- The fibrosis model may be counting holes at the pleural edge
- **scout-006-c01** [SHORTLISTED/SCOUTED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **scout-006-c02** [SHORTLISTED/SCOUTED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **scout-006-c03** [SCOUT_ONLY/SCOUTED/baseline] -- An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver
- **scout-006-c04** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-006-c05** [SCOUT_ONLY/SCOUTED/baseline] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two
- **scout-007-c01** [SHORTLISTED/SCOUTED/baseline] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- **scout-007-c02** [SHORTLISTED/SCOUTED/baseline] -- A breast-cancer risk model may be reading the arteries as a vascular clock
- **scout-007-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin may be reading fatty kidney rather than kidney shape
- **scout-007-c04** [SHORTLISTED/SCOUTED/baseline] -- The PE model may read contrast flowing backward as a pressure gauge
- **scout-007-c05** [SHORTLISTED/SCOUTED/baseline] -- A lung-cancer model may be reading a mechanically remodeled trachea
- **scout-007-c06** [SCOUT_ONLY/SCOUTED/wide] -- The effusion model may be reading whether pleural fluid still obeys gravity
- **scout-007-c07** [SHORTLISTED/SCOUTED/wide] -- The fibrosis model may be counting holes at the pleural edge
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
- **scout-009-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The CT spirometer may be measuring remodeled airway walls
- **scout-009-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The kidney model may be reading fat packed into the renal sinus
- **scout-009-c03** [SHORTLISTED/SCOUTED/baseline] -- The brain-tumor prognosticator may be weighing the chewing muscle
- **scout-009-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The risk model may be reading the breast's lines of force
- **scout-009-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The lung-cancer model may be reading the marrow as a smoking dosimeter
- **scout-009-c06** [SCOUT_ONLY/SCOUTED/wide] -- The CT spirometer may be reading the diaphragm as a pressure-loaded membrane
- **scout-009-c07** [SCOUT_ONLY/SCOUTED/wide] -- Mirai may be detecting broken bilateral symmetry before a lesion exists
- **scout-009-c08** [SCOUT_ONLY/SCOUTED/wide] -- The glioblastoma prognosticator may be reading the invasion front's roughness
- **scout-009-c09** [SCOUT_ONLY/SCOUTED/fiction] -- The arterial-calcification score may be reading inspiratory depth


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


===== ideas/018/README.md =====
# Idea 018: The brain-tumor prognosticator may be weighing the chewing muscle

Selected from scouting cycle 009, candidate 3.


===== ideas/018/critique.md =====
# Critique — Idea 018: The brain-tumor prognosticator may be weighing the chewing muscle

```
FATAL OBJECTION: Both assets the design requires — a runnable frozen whole-head
GBM survival model, and an obtainable tumor-stable serial cohort that retains
the temporalis — fail direct inspection: GRASP released no weights or inference
code and its data is by-request, and every public longitudinal GBM MRI resource
is either skull-stripped (LUMIERE) or anti-selected against tumor stability
(UPenn-GBM follow-ups are re-resections for progression).
EVIDENCE: keystone_screen.md (GRASP repo commit ba0a1ca, Data Availability of
PMC11145448); LUMIERE Sci Data 2022 (10.1038/s41597-022-01881-7, skull-stripped
for anonymization); UPenn-GBM Sci Data 2022 (PMC9338035, 60 follow-ups, all at
second resection for progressive changes).
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT
```

REJECT is under the claim-identity rule (ledger 2026-08-10, idea 015): the only
viable repair replaces the audited object (GRASP → a self-trained model) and
deletes the longitudinal-within-subject arm, which changes the deliverable's
identity. A specific, well-evidenced successor exists and should enter as a new
candidate with `parent_ids: ["idea-018"]` — see the constructive section.

---

## 1. The audited model does not exist as an obtainable artifact

This is not a prediction; it was inspected. The keystone screen cloned the
publication-linked GRASP repository (commit `ba0a1ca0`) and found training code
only: no checkpoint, no pretrained weights, no inference entry point, and
configuration paths pointing at local files (`pretrained_weights/t1_weights.pt`,
`data/input_data/training_data.npz`) that were never released. The paper's data
availability is "available from the corresponding author by request"
(PMC11145448, Data Availability). The charter forbids dependence on unconfirmed
gated data, so the GRASP route fails twice over: the model cannot be run, and
the recipe cannot be retrained without by-request data.

This is the idea-014 failure mode realized, not merely risked. Idea 014 was
PAUSED because "the rate-limiting model asset has not been reproduced." Here
the asset is not merely unreproduced — the ingredients to reproduce it are
confirmed absent. The card's `dies_like_prior` field claimed only that no
annotation-provenance failure applies (true) and missed this resemblance
entirely. The keystone screen's verdict of UNVERIFIABLE was, if anything,
generous: for the specific GRASP route the conjunctive keystone is now
INSPECTED_FALSE in its second and third conjuncts (obtainable weights;
obtainable serial cohort).

## 2. The longitudinal arm is unexecutable on any public cohort — verified

The card's design leans on "serial scans with stable automated tumor volume"
to decorrelate muscle loss from tumor change. I checked the candidate cohorts:

- **LUMIERE** (91 GBM patients, 638 study dates, OS for a subset; Sci Data
  2022, DOI 10.1038/s41597-022-01881-7) is the one public longitudinal GBM MRI
  dataset — and every study was skull-stripped, with skull-stripping visually
  verified "to ensure patient anonymization." The temporalis is removed by
  construction. Dead.
- **UPenn-GBM** (PMC9338035) includes 60 follow-up scans, but all are from
  patients "who have undergone a second resection due to progressive
  radiographic changes" — the follow-up subset is selected *for* progression,
  i.e., anti-selected against the tumor-stable pairs the design needs. Dead
  for this arm (though decisive for the successor; see below).
- **BraTS-family data** (including UCSF-PDGM) is skull-stripped as a matter of
  pipeline definition. Dead.

So even if GRASP weights materialized tomorrow, the within-patient
tumor-stable tracking arm has no data to run on. Half the "smallest decisive
experiment" cannot be purchased at any effort level with public data.

## 3. A confound the card missed: age (and sex)

The card's alternative-explanations list covers tumor progression, steroids,
and edit seams. It omits the strongest one. Age is the dominant clinical
predictor of GBM survival — in the BraTS survival-prediction task era, simple
age-based models were competitive with imaging pipelines — and temporalis
cross-sectional area declines with age and differs by sex. A whole-head model
that has learned cortical atrophy, ventricular size, or any other age
correlate will co-vary with temporalis without using it; conversely, a model
that *does* use temporalis pixels may be using them as an age/sex readout, not
a frailty readout. Substitution can establish that the pixels are used (rung
1); it cannot arbitrate "frailty" versus "age proxy" as the meaning.

This bears directly on the deliverable sentence. "…as an image marker of
systemic frailty" is interpretive gloss of exactly the kind the ledger already
ruled against when idea 015 lost "vascular age." The defensible rung-3
sentence is "the model is using temporalis muscle bulk" — temporalis
thickness/CSA is the named, tool-measurable X, and it qualifies on its own.
The frailty mechanism is a discussion-section hypothesis, not part of the
claim. Any successor card must make this cut up front, and must carry an
age-adjusted analysis (does temporalis substitution move the score *beyond*
what the model's age estimate explains) if it wants to gesture at frailty.

## 4. Prior-work overlap: real but survivable

- The GRASP authors already knew extracranial tissue carries signal — they
  kept whole-brain inputs partly because "extracranial information is linked
  with overall survival" (PMC11145448, Discussion). The *motivation* is
  pre-articulated in the primary source; the use-audit is not performed there.
  The delta claimed by the card (association exists, use untested) survives,
  but a successor's novelty audit should specifically check whether GRASP or
  its citing literature published saliency/occlusion maps highlighting the
  temporal region — that would narrow the delta from "unasked" to
  "informally observed, never measured."
- The temporalis prognostic literature (Furtner et al.; An et al., BJC 2021,
  DOI 10.1038/s41416-021-01590-9) is association-with-outcome, not
  model-use. No overlap with the audit question.
- No concept-label circularity: X is geometry from an automated tool, the
  model consumes raw images, and no report text enters. The
  annotation-provenance failure family genuinely does not apply.

## 5. What inspection *supports* — the assets for an easier version

The adversarial search turned up genuinely good news, all primary-source:

1. **The temporalis measurement tool is public and proven on public data.**
   The BJC 2021 pipeline (PMC8770629) releases code at
   `gitlab.com/computational.oncology/temporalissegmentation`, and was
   trained/validated on TCGA-GBM (n=31), IVY-GAP (n=23), and REMBRANDT (n=38)
   — public TCIA collections — plus one in-house set. Dice 0.893. This
   *proves* the temporalis survives in standard public GBM T1c imaging and is
   segmentable there without asking anyone. X passes the charter's hard
   constraint cleanly.
2. **A large, open, survival-linked, non-skull-stripped GBM cohort exists.**
   UPenn-GBM (TCIA, CC BY 4.0; Sci Data PMC9338035): 630 patients, 611
   preoperative mpMRI studies, overall survival in a released CSV, and —
   decisively — the release includes "unstripped-structural" scans: defaced
   but with skull and extracranial tissue intact, in original DICOM and
   NIfTI. Defacing removes facial-surface features, and skull-stripping (the
   step that would delete the temporalis) is a *separate* released derivative,
   not the only form.
3. **Compute fits the charter.** A GRASP-style 130³ single-sequence 3D model
   on ~600 patients trains in single-GPU sessions; the temporalis tool is a
   2D segmentation at defined slice levels.

The one load-bearing unknown for this route: whether the CaPTk defacing mask
spares the temporalis at the standardized measurement levels (superior orbital
roof / Sylvian fissure). That is directly inspectable by downloading a handful
of UPenn-GBM unstripped cases and running the GitLab tool — an afternoon of
Stage 0, with a binary answer. That is what a keystone should look like.

## 6. Remaining weaknesses of the successor, stated honestly

- **It audits a model you trained, not a model the field deployed.** The
  program's driver is decoding what models found; a self-trained
  standard-recipe model is a legitimate object (the race-detection literature
  did exactly this), but the finding becomes "whole-head survival training
  discovers sarcopenia" rather than "GRASP uses sarcopenia." Weaker headline,
  same scientific content, and honest.
- **The model must be worth decoding.** If the self-trained model cannot beat
  an age+sex-only baseline on a frozen split, there is no interesting signal
  to decode and the study should stop. This must be a preregistered gate
  (idea-014's lesson applied prospectively). The gate is cheap — days, not
  weeks — which is what makes the successor runnable where idea 014 stalled.
- **Single site.** UPenn-GBM is one health system; scanner/protocol confounds
  are largely neutralized by the within-cohort substitution design, but any
  positive finding is a single-site finding and must say so.
- **Cross-patient substitution replaces within-patient substitution.** With
  no serial arm, the edit source is a sequence- and intensity-matched other
  patient. Seam and bias-field validity checks (scalp/fat shams, left-right
  shams, distribution checks) carry more weight than in the card's
  within-patient version. This is the successor's main identifiability risk.
- **Negative-result value stays capped.** A null remains sensitivity-limited
  until visibility (temporalis in tensor post-defacing) and a positive
  control (tumor-region substitution moves the score) are confirmed; after
  both, a null is a reasonably decisive "this model family does not use it."

## 7. Scoring corrections implied (for the record)

The card's feasibility 3 and novelty 3 caps were correct. Data readiness 2 was
correct for the card as written; the successor on UPenn-GBM would honestly be
a 4 (public, CC BY, direct download) — one of the few cases where the easier
version scores *higher* on data. Identifiability 4 was too generous for the
card given the omitted age confound; the successor should re-score after the
age-adjusted arm is specified.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Train a whole-head 3D survival model on
UPenn-GBM's unstripped defaced scans, gate on beating an age+sex-only baseline
on a frozen split, and test by temporalis-only cross-patient substitution
(with scalp/fat and left-right shams) whether it uses temporalis muscle bulk.
RETAINS ORIGINAL MEDICAL MOTIVATION? YES — frailty contamination of imaging
prognosticators is still the stake; only the audited object changes.
SHOULD IT BECOME A SEPARATE CANDIDATE? YES — claim identity changes (GRASP →
self-trained model; longitudinal arm dropped), so per the 2026-08-10 rule it
re-enters scouting with parent_ids: ["idea-018"], not revision-in-place.
IS IT ACTUALLY WORTH DOING? Yes, conditionally: the age-baseline gate and the
defacing-spares-temporalis check together cost under a week and are decisive
either way — if both pass, this is the rare candidate where the model, the
cohort, the survival labels, and the X-measurement tool are all public today;
if either fails, stop having spent days, not weeks.
```


===== ideas/018/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The original study is not executable with obtainable assets, and the proposed feasible repair changes the audited model and estimand enough that it must be a separate successor rather than an amendment to Idea 018.

**Argument:** Idea 018 asks whether the published whole-head GRASP glioblastoma survival model uses temporalis thickness, with tumor-stable longitudinal tracking as convergent evidence. Direct inspection defeats both load-bearing assets: the publication-linked GRASP repository at commit `ba0a1ca0` contains training code but no checkpoint, pretrained weights, inference entry point, or released training cohort, while the paper makes its data available only by request; this violates the charter's prohibition on dependence on unconfirmed gated data. The longitudinal arm also has no suitable public cohort: LUMIERE is skull-stripped and therefore removes temporalis (DOI 10.1038/s41597-022-01881-7), whereas all 60 UPenn-GBM follow-ups were obtained at second resection for progressive radiographic change (PMCID PMC9338035), making that subset anti-selected against the required tumor-stable pairs. Training a new model on UPenn-GBM unstripped baseline scans and using cross-patient temporalis substitution could be feasible, but it would answer whether a newly trained model family uses temporalis, not whether GRASP does, and it drops the original longitudinal estimand. Under the ledger's claim-identity rule, that is a new candidate with `parent_ids: ["idea-018"]`, not a repair. This is the realized form of idea 014's missing-model-asset failure, which the card's `dies_like_prior` assessment omitted.

**What would change my mind:** Show an openly obtainable, runnable frozen GRASP checkpoint together with its exact preprocessing and an obtainable survival-linked serial cohort retaining bilateral temporalis that contains a prespecified adequate number of same-patient, tumor-stable pairs; otherwise reject Idea 018 and register the UPenn-GBM self-trained design as a separate successor.

**Status:** OPEN


===== ideas/018/idea_card.json =====
{
  "id": "C3",
  "parent_ids": [],
  "revival_basis": null,
  "search_mode": "B",
  "entry_point": 2,
  "design_template": "longitudinal-within-subject",
  "title": "The brain-tumor prognosticator may be weighing the chewing muscle",
  "question": "Is a whole-head glioblastoma survival model using temporalis muscle thickness as a frailty cue rather than only tumor biology?",
  "rung": {
    "target": 3,
    "current": 0,
    "move_up": "Tumor-stable within-patient score tracking plus selective temporalis substitution reaches rung 1; acquisition/treatment controls gate rung 2; temporalis thickness provides rung 3."
  },
  "deliverable_sentence": "The glioblastoma survival model is using temporalis muscle thickness as an image marker of systemic frailty.",
  "X_measurement": {
    "X": "Bilateral temporalis muscle cross-sectional area and thickness on axial T1 MRI, normalized to cranial size.",
    "how": "Automatically segment left and right temporalis at standardized orbital/temporal levels and compute area and maximum orthogonal thickness. A multi-dataset deep-learning implementation and prognostic validation were reported by Surov et al./Furtner-related work (Neurooncol Adv 2022, PMCID PMC8770629).",
    "could_compute_today_without_asking_anyone": "Yes; an automated segmentation produces continuous geometry without a radiologist rating."
  },
  "suspected_signal": "Cancer cachexia, corticosteroid exposure, inactivity, and frailty reduce craniofacial skeletal muscle; whole-head models can see this extracranial tissue even when the tumor is stable.",
  "specific_artifact_confused_with_signal": "Head field-of-view cropping, coil bias, slice angulation, edema, and postsurgical change can alter apparent thickness or model framing.",
  "keystone_prerequisite": "A runnable whole-head survival model retains extracranial temporalis in its exact input tensor, and enough longitudinal MRIs have stable tumor burden but measurable temporalis change to separate frailty from tumor progression.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_evidence": "Primary full text inspected: PMCID PMC8770629 reports automated temporalis segmentation across four datasets; GRASP, PMID 38285679, reports whole-brain post-radiotherapy MRI survival prediction. The exact GRASP preprocessing, checkpoint availability, and count of tumor-stable longitudinal pairs retaining temporalis were not established.",
  "keystone_residual_assumption": "The adjacent facts are that temporalis predicts prognosis and an MRI model predicts survival. I am still assuming the survival model actually sees extracranial muscle and an obtainable longitudinal subset decorrelates muscle loss from tumor change; that is the real keystone.",
  "rung_reached": "No rung; longitudinal association alone is insufficient. Rung 1 needs convergent within-subject and selective-substitution evidence.",
  "dies_like_prior": "No annotation-provenance failure applies because muscle geometry and tumor volume are automated. It risks the same use-versus-association error seen across early cycles, so longitudinal correlation is explicitly exploratory and regional substitution is required for the use claim.",
  "closest_prior_work": [
    {
      "citation": "Deep learning-based quantification of temporalis muscle has prognostic value in glioblastoma",
      "identifier": "PMCID PMC8770629",
      "verified_fact": "Automated temporalis quantification generalized across four datasets and was prognostic.",
      "delta": "It did not test reliance by a whole-image survival model."
    },
    {
      "citation": "GRASP study",
      "identifier": "PMID 38285679",
      "verified_fact": "A whole-brain post-radiotherapy MRI model predicted glioblastoma survival.",
      "delta": "It did not isolate extracranial muscle as a used signal."
    }
  ],
  "existing_assets": [
    "Public brain-tumor MRI collections with serial imaging",
    "Automated tumor and temporalis segmentation methods",
    "Published survival-model recipes"
  ],
  "smallest_decisive_experiment": "Freeze a survival model and identify serial scans with stable automated enhancing/nonenhancing tumor volume. Test whether score change tracks temporalis change, then substitute only extracranial temporalis patches between same-sequence scans with matched coil-field intensity. Require dose response, unchanged tumor embeddings, and null scalp/fat shams.",
  "use_vs_association": "The within-subject relationship is only triangulation; the use claim requires temporalis-only substitution to move survival score while brain/tumor tensors and tumor embeddings remain fixed.",
  "standing_confounds_addressed": {
    "scanner_vendor_protocol_reconstruction_site": "Same-sequence within-patient pairs and intensity-matched substitutions reduce them; coil/site replication remains.",
    "positioning": "Rigid cranial registration and standardized planes.",
    "habitus": "Within-subject design controls baseline habitus, not systemic treatment changes.",
    "prevalence_referral": "Paired estimand is robust but GBM treatment cohort limits scope.",
    "label_leakage": "No report text or survival label is used in the paired substitution readout."
  },
  "alternative_explanations": [
    {
      "alternative": "Tumor progression causes both score and wasting.",
      "resolution": "Prespecified stable-tumor pairs plus tumor-fixed substitution."
    },
    {
      "alternative": "Steroid treatment changes both muscle and brain edema.",
      "resolution": "Medication adjustment where available; substitution holds brain fixed but biological interpretation remains limited."
    },
    {
      "alternative": "The model responds to extracranial edit seams.",
      "resolution": "Scalp/fat and left-right sham substitutions with distribution checks."
    }
  ],
  "anticipated_negative": {
    "classification": "sensitivity-limited",
    "reason": "A null can reflect a tumor-cropped model or insufficient muscle change; becomes decisive only after confirmed visibility and positive-control sensitivity."
  },
  "cross_domain": null,
  "remaining_legwork": "2-3 days to inspect model input/preprocessing; 1 week for longitudinal pair counts; 2 weeks to first intervention result.",
  "scores": {
    "clarity": {
      "value": 5,
      "why": "Named muscle metric and explicit whole-head outcome."
    },
    "identifiability": {
      "value": 4,
      "why": "Tumor-fixed regional substitution directly separates muscle from tumor burden, subject to seam validity."
    },
    "medical_relevance": {
      "value": 4,
      "why": "Would reveal frailty contamination or useful holistic prognostication."
    },
    "interest": {
      "value": 4,
      "why": "A brain-tumor model using chewing muscle is surprising and clinically legible."
    },
    "prior_legwork": {
      "value": 3,
      "why": "Both component literatures exist, but runnable convergence is unclear."
    },
    "feasibility": {
      "value": 3,
      "why": "Capped; model visibility and longitudinal subset uninspected."
    },
    "data_readiness": {
      "value": 2,
      "why": "Serial survival-linked MRI access and checkpoint need confirmation."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "Muscle/tumor metrics exist; edit validation is custom."
    },
    "negative_result_value": {
      "value": 2,
      "why": "Null is sensitivity-limited."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Capped; bounded search found association studies but no use audit."
    },
    "regret": {
      "value": 5,
      "why": "Extracranial tissue is easy to overlook and may dominate prognosis."
    }
  },
  "priority_score": 3.45,
  "priority_arithmetic": "0.20*3 + 0.15*4 + 0.15*4 + 0.10*3 + 0.10*4 + 0.10*5 + 0.10*2 + 0.05*2 + 0.05*3 = 3.45",
  "unverified_claims": [
    "An obtainable survival model retains temporalis",
    "Enough tumor-stable serial pairs exist",
    "Temporalis-only substitution can pass distribution checks"
  ],
  "track": "baseline"
}


===== ideas/018/keystone_screen.md =====
# Keystone screen

## Keystone as stated

> A runnable whole-head survival model retains extracranial temporalis in its exact input tensor, and enough longitudinal MRIs have stable tumor burden but measurable temporalis change to separate frailty from tumor progression.

This is a conjunctive prerequisite. I inspected both the GRASP model/input side and the longitudinal-cohort side. The first is only partly established; the second is not established.

## What I inspected

### GRASP primary paper: input and preprocessing

I inspected the full text of Chelliah et al., *Neuro-Oncology* 2024, DOI 10.1093/neuonc/noae017 (PMCID PMC11145448), especially **Methods → Imaging and Combined Models**. It states:

> “Whole-brain T1c and T2 images were coregistered and minimally preprocessed … Images were resampled to common voxel sizes (1 mm3), and subsequently cropped or padded to a final 3D array of shape 130 × 130 × 130 for inputs to deep learning models.”

Source: [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11145448/fullTextXML), **Methods → Imaging and Combined Models**.

The paper also explains why tumor-only bounding boxes were not used:

> “This was not pursued because (i) extracranial information is linked with overall survival; (ii) contrast-enhancing masses remote to the initial site signal recurrence (and shorter survival); (iii) data preprocessing that aligned with pretraining preprocessing was favored; and (iv) whole-brain images require minimal preprocessing (plausibly reducing barriers to translation).”

Source: [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11145448/fullTextXML), **Discussion**, paragraph beginning “Another limitation is that we used a small dataset.”

These quotes verify a whole-volume 130-cubed input and deliberate avoidance of tumor-only cropping. They do **not** directly verify that the bilateral temporalis survives the crop in the exact tensors used for inference. No example preprocessed tensor, crop-coordinate rule, or per-case field-of-view audit was released.

### Official GRASP repository: runnability and released assets

I cloned and inspected the publication-linked repository at commit `ba0a1ca0acba5467a3c24b127f39024c78c57bb7`. Its README describes only training:

> “Usage to train the model:”

followed by:

> “python train.py -m train_model/model_params.json -e train_model/environment.json -g 1”

Source: [official GitHub repository README, lines 16–20](https://github.com/lyshc/glioblastoma-survival-classifier/blob/ba0a1ca0acba5467a3c24b127f39024c78c57bb7/README.md#L16-L20).

The checked repository tree contains training code and configuration, but no model checkpoint, pretrained weights, inference entry point, image data, or `.npz` cohort file. The configuration instead expects local paths such as `pretrained_weights/t1_weights.pt`, `pretrained_weights/t2_weights.pt`, and `data/input_data/training_data.npz`. Thus a published recipe exists, but an obtainable frozen GRASP model was not verified as runnable.

### GRASP primary paper: longitudinal data availability

The study used the first post-radiotherapy MRI, not a released serial cohort. The discussion explicitly contrasts its intended approach with longitudinal imaging:

> “For now, a model that could translate most easily across centers would likely benefit from a pragmatic approach that requires collecting widely available nonimaging features and cross-sectional (rather than longitudinal) imaging.”

Source: [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11145448/fullTextXML), **Discussion**, paragraph beginning “While predictions did not improve.”

The data-availability statement is:

> “Data generated or analyzed during the study are available from the corresponding author by request.”

Source: [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11145448/fullTextXML), **Data Availability**.

Therefore, the primary GRASP source does not establish an openly obtainable longitudinal cohort, any count of serial pairs, stable automated tumor burden, measurable temporalis change, or linkage of such pairs to a runnable frozen model. “By request” also does not satisfy the charter’s requirement to avoid dependence on unconfirmed gated data.

## Residual-assumption check

**If this card only verified the nearest checkable thing, what is it still assuming?**

The nearest checkable facts are that GRASP consumes minimally processed whole-volume MRI arrays and that temporalis size has an automated prognostic literature. The card is still assuming three load-bearing facts: (1) the exact 130-cubed GRASP tensors retain enough bilateral temporalis for measurement/intervention; (2) the trained survival weights are obtainable and runnable; and (3) an obtainable serial, survival-linked cohort contains enough same-patient scans with stable automated tumor burden but meaningful temporalis change. None was directly established by the paper, repository, released files, or cohort schema inspected here.

The stated keystone is therefore the correct load-bearing keystone, but it remains unresolved rather than demonstrably false. The primary paper’s cross-sectional design and by-request data weaken the proposed route; they do not prove that no suitable model or independent public serial cohort can exist.

```json
{"verdict": "UNVERIFIABLE", "evidence": "Data generated or analyzed during the study are available from the corresponding author by request.", "source": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11145448/fullTextXML — Data Availability", "note": "Whole-volume inputs are verified, but exact temporalis retention, released runnable weights, and a sufficiently large obtainable tumor-stable longitudinal cohort are not."}
```


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
This is round 1. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The original study is not executable with obtainable assets, and the proposed feasible repair changes the audited model and estimand enough that it must be a separate successor rather than an amendment to Idea 018.

**Argument:** Idea 018 asks whether the published whole-head GRASP glioblastoma survival model uses temporalis thickness, with tumor-stable longitudinal tracking as convergent evidence. Direct inspection defeats both load-bearing assets: the publication-linked GRASP repository at commit `ba0a1ca0` contains training code but no checkpoint, pretrained weights, inference entry point, or released training cohort, while the paper makes its data available only by request; this violates the charter's prohibition on dependence on unconfirmed gated data. The longitudinal arm also has no suitable public cohort: LUMIERE is skull-stripped and therefore removes temporalis (DOI 10.1038/s41597-022-01881-7), whereas all 60 UPenn-GBM follow-ups were obtained at second resection for progressive radiographic change (PMCID PMC9338035), making that subset anti-selected against the required tumor-stable pairs. Training a new model on UPenn-GBM unstripped baseline scans and using cross-patient temporalis substitution could be feasible, but it would answer whether a newly trained model family uses temporalis, not whether GRASP does, and it drops the original longitudinal estimand. Under the ledger's claim-identity rule, that is a new candidate with `parent_ids: ["idea-018"]`, not a repair. This is the realized form of idea 014's missing-model-asset failure, which the card's `dies_like_prior` assessment omitted.

**What would change my mind:** Show an openly obtainable, runnable frozen GRASP checkpoint together with its exact preprocessing and an obtainable survival-linked serial cohort retaining bilateral temporalis that contains a prespecified adequate number of same-patient, tumor-stable pairs; otherwise reject Idea 018 and register the UPenn-GBM self-trained design as a separate successor.

**Status:** OPEN

