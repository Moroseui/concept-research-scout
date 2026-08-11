You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/017
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
- **idea-017** [SHORTLISTED/CRITIQUED/baseline] -- A lung-cancer model may be reading a mechanically remodeled trachea
- **idea-018** [SHORTLISTED/SCOUTED/baseline] -- The brain-tumor prognosticator may be weighing the chewing muscle
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


===== ideas/017/README.md =====
# Idea 017: A lung-cancer model may be reading a mechanically remodeled trachea

Selected from scouting cycle 007, candidate 5.


===== ideas/017/critique.md =====
# Critique — Idea 017: A lung-cancer model may be reading a mechanically remodeled trachea

```
FATAL OBJECTION: The confirmatory arm rests on linear concept-direction erasure, a method shown to remove correlated non-concept features, applied to a sign the defining literature says occurs almost exclusively in men with COPD — so neither a positive nor a null "selective erasure" result identifies use of tracheal deformity.
EVIDENCE: Kumar, Tan & Sharma, NeurIPS 2022 (arXiv 2207.04153) on erasure unreliability; Greene 1978, AJR 130:441 (DOI 10.2214/ajr.130.3.441) on sex/COPD collinearity; Pompe et al. (PMC6052793) 5.5% saber-sheath prevalence even in a COPD-enriched cohort.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

---

## 1. What survives adversarial review

Before the demolition, the parts that held up under checking:

**Novelty (source-supported, bounded search).** I searched for prior work
connecting tracheal index or saber-sheath trachea to any lung-cancer risk
model and found none. The closest work is "Auditing Sybil: Explaining Deep
Lung Cancer Risk Prediction Through Generative Interventional Attributions"
(arXiv 2602.02560), which intervenes on *nodules* via generative editing and
reports artifact sensitivity and a radial bias; it does not measure the
trachea or any airway-shape quantity. I also found no study associating
tracheal index with lung cancer incidence at all — the sign's entire
literature is about COPD diagnosis. The gap is real as far as a bounded
search can establish. `NO_DUPLICATE_FOUND_LIMITED_SEARCH` is the honest
status.

**X qualifies under the charter (verified at the source).** Pompe et al.
(PMC6052793) is confirmed to describe a fully automated pipeline: −750 HU
lumen segmentation, centerline extraction, cross-sections perpendicular to
local tracheal direction, ray-cast diameters. Cohort: 200 COPDGene subjects,
40 per GOLD stage. The measurement needs no human judgment. This is exactly
the shape of X the charter demands.

**Data access is better than the card knew (verified).** The card scores
data readiness on "NLST pathway established in the repository record," which
idea-008's own card admits is only "described as obtainable." But this is now
moot for images: NLST CT images and a limited clinical dataset were made
publicly downloadable without restriction through TCIA/IDC (TCIA NLST
collection; CDAS approved project 3028, "Distribution of NLST imaging and
limited clinical data through NCI public image repositories"). No DUA gate
for the imaging and basic demographics. Full clinical variables still require
CDAS. This *strengthens* Stage 0 feasibility relative to the card's own
justification.

**The cross-domain analogy earns its keep.** The card's `if_analogy_dropped`
answer is genuine: the mechanics framing changes X from generic caliber to an
anisotropic ratio with a predicted direction and a stability requirement.
This is not free-energy decoration.

## 2. The central objection: the erasure arm cannot deliver the claim

The card's `use_vs_association` test is: learn a tracheal-index direction in
frozen Sybil embeddings on validation data, erase it, and call the effect
"selective use" if the risk change exceeds emphysema/sex/lung-volume
erasures. This inference is broken in both directions, and not for reasons
specific to this idea — it is a documented property of the method family.

- **Positive result is ambiguous.** Kumar, Tan & Sharma (NeurIPS 2022,
  arXiv 2207.04153) prove and demonstrate that probing-based removal uses
  correlated non-concept features even when the concept's own features
  suffice for perfect accuracy; erasure of the "tracheal index direction"
  removes shared variance with whatever co-varies with it. Elazar et al.'s
  own amnesic-probing work concedes collateral-damage concerns from iterated
  projection. LEACE (arXiv 2306.03819) guarantees only linear guarding of
  the target concept, not that correlated concepts are untouched. So "TI
  erasure moved the score more than emphysema erasure" does not localize the
  effect to tracheal shape — it measures geometry of an entangled embedding.
- **Null result is also ambiguous.** A nonlinear encoding survives linear
  erasure, and the low-index tail may be too thin for power (Section 3). So
  the card's `anticipated_negative.classification: "decisive"` and
  `negative_result_value: 5` are wrong *as designed*. The honest
  classification of the null is sensitivity-limited at best.

This matters doubly here because the collinearity is not incidental; it is
constitutive of the sign (next section). Erasure-vs-erasure comparison is at
its weakest exactly when concept directions are strongly correlated.

The record already encodes this standard elsewhere: idea-008's debate
concluded that only a validated in-distribution *input-space* edit separates
a model-use study from an association-only study. Idea 017's confirmatory arm
quietly adopts a weaker evidentiary standard for the same model. A revision
must either meet the idea-008 bar (a validated tracheal-reshaping edit — hard,
and it would inherit the edit-validity burden that stalled ideas 008/011/014)
or honestly retarget rung 1–2.

## 3. The collinearity is worse than the card admits (verified sources)

The card treats "the index is only a proxy for male sex" and "only
emphysema" as alternatives to be adjusted away. The founding literature says
the overlap is near-total at the deformity end:

- Greene 1978 (AJR 130:441): the defining case series is **60 male patients
  vs 60 male controls**; 95% of saber-sheath patients had clinical COPD vs
  18% of controls. Review literature (e.g., J Assoc Chest Physicians 2017;
  AJR CT reviews) repeats that the sign occurs "almost exclusively in men
  with COPD," generally after age 50.
- Trigaux et al. 1994 (Acta Radiol 35:310): as a COPD sign, sensitivity
  >90% but **specificity <40%** — the sign and the disease are not separable
  categories so much as overlapping definitions in the severe tail.
- Pompe et al.: even in COPDGene with 160/200 subjects at GOLD 1–4,
  saber-sheath prevalence was **5.5%** (11/200). NLST screenees (heavy
  smokers, but not GOLD-enriched) will plausibly sit at or below that. The
  "enough low-index cases independent of sex, emphysema, lung volume, and
  reconstruction" clause of the keystone is therefore not merely
  uninspected — the prior from the literature is that it is **false** for
  the categorical deformity. The viable version of the study lives on the
  *continuous* index (Pompe found TI decreases monotonically with GOLD
  stage), which the card gestures at but does not commit to.

Inference: a sex- and emphysema-matched analysis with adequate low-index
support may simply not exist in NLST at any obtainable n. Stage 0's
joint-distribution audit is the right test, and a negative there would be a
cheap, decisive feasibility result. But the card's identifiability score of 4
prices this risk as if adjustment were routine. It is not; this is exactly
the failure mode that killed idea-009 (IDENTIFIABILITY_FAILURE: mechanism
inseparable from a co-varying population factor in any obtainable cohort).

**`dies_like_prior` is aimed at the wrong prior.** The card compares itself
to ideas 006 and 007. The genuinely threatening precedent is **idea-009**
(Murray's-law departure): a beautiful mechanical quantity that could not be
separated from co-varying population factors. The revision must add this
comparison and make the Stage 0 partial-correlation audit the explicit test
of whether 017 dies the same way.

## 4. Additional design defects (each repairable)

**(a) The respiratory-stability gate cannot run on the study data.** NLST
LDCTs are single inspiratory breath-holds; there are no expiratory
companions. The card's "any available respiratory pairs" would mean the
idea-007 TCIA 4DCT/BHCT set (20 patients, diagnostic non-LDCT) pushed
through Sybil — a model validated on screening LDCT — which converts the gate
into its own out-of-distribution question. Two honest options: (i) drop the
claim of demonstrated respiratory stability and note that NLST's uniform
inspiratory protocol *reduces* (not eliminates) phase confounding within the
cohort; (ii) replace the gate with the natural experiment NLST actually
contains: **T0/T1/T2 annual repeats**. A fixed remodeling should behave as a
stable trait across years (high within-subject ICC) while inflation-sensitive
quantities vary; this is a cleaner test of "fixed, accumulated deformity"
than any 20-patient external set, uses the longitudinal-within-subject
template the portfolio underuses (×1), and needs no new data source.

**(b) Training-set leakage is unaddressed.** Sybil was trained on NLST
(15,000 participants, per PMC10419602). Any score–index association computed
on scans in Sybil's training set is contaminated by memorization. The card
says "untouched cases" but the recoverability of the published held-out split
is precisely idea-008's unresolved question ("Can the required held-out NLST
cohort and covariates actually be recovered?"). Idea 017 inherits that
problem and must say so; the released repo's split metadata inspection is a
Stage 0 item, not an assumption.

**(c) Threshold inconsistency.** The card calls <0.67 "the conventional
severe-deformity threshold." The literature uses <0.67 for saber-sheath in
some sources and ≤0.5 in others (Greene's original series; Radiopaedia/review
articles differ). Trivial fix: prespecify the continuous index as primary and
report both categorical thresholds as descriptive only. This also sidesteps
the prevalence problem in 3.

**(d) Score corrections implied.** Under the Mode C weighting:
identifiability 4 → **2** as currently designed (erasure logic + constitutive
collinearity); negative_result_value 5 → **2–3** (null is
sensitivity-limited, not decisive, until an equivalence margin and a
power analysis on the low-index support exist); the claimed
`anticipated_negative: decisive` must be reclassified. Mechanism clarity 5,
interest 5, clarity 5 stand. Recomputed Mode C priority ≈
0.30·5 + 0.25·2 + 0.20·5 + 0.15·4 + 0.10·5 = **4.10** — still above most of
the backlog, which is the honest signal: this is a good question wearing the
wrong confirmatory experiment.

**(e) Portfolio note.** Representation-erasure already appears ×3 in the
homogenization watch; this would be a fourth. And Sybil now anchors ideas
008, 012, 017, scout-008-c05, and scout-009-c05. Neither is disqualifying,
but the revision replacing the erasure arm would also relieve the template
concentration, and the eventual debate should weigh Sybil-portfolio
concentration explicitly.

## 5. What is *not* wrong

- No annotation-provenance risk: X is computed by algorithm from pixels; the
  dominant historical killer does not apply.
- No circularity: tracheal index is not an input label, not report-derived,
  and cancer outcome cannot be printed into tracheal geometry.
- No compute problem: segmentation + centerline + Sybil inference on
  hundreds of public scans is comfortably single-GPU.
- The keystone screen itself is honest work — it aimed at the load-bearing
  facts, quoted the real code, and correctly returned UNVERIFIABLE rather
  than inflating to INSPECTED_TRUE. The caps are properly applied.

## 6. Required revisions (summary)

1. Demote the confirmatory arm: either commit to the idea-008 evidentiary
   bar (validated in-distribution tracheal edit) or retarget rung 1–2 with
   the deliverable sentence retained as the *eventual* rung-3 target.
2. Make the continuous tracheal index primary; categorical saber-sheath
   descriptive only.
3. Replace the respiratory-pairs gate with NLST T0/T1/T2 within-subject
   trait-stability (ICC), plus reconstruction-pair repeatability where
   available.
4. Add training-set-contamination handling: inspect the released Sybil split
   metadata; all associations on held-out or external scans only.
5. Rewrite `dies_like_prior` against idea-009 and make the Stage 0
   sex/emphysema/volume partial-correlation audit the explicit
   lives-or-dies-like-009 test, with a prespecified minimum low-index
   support and equivalence margin.
6. Correct scores per 4(d); reclassify the anticipated negative.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: On publicly downloadable NLST scans outside Sybil's training set, does the automated continuous tracheal index (i) survive Sybil's preprocessing, (ii) behave as a stable within-subject trait across annual repeats, and (iii) carry association with Sybil's risk score beyond sex, LAA-950 emphysema, and lung volume — the three gates that decide whether the saber-sheath use question is answerable at all?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — the deliverable sentence is unchanged as the rung-3 target; under the claim-identity rule this is narrowing within the same claim, i.e., revision-in-place with Stage 0 gates, not supersession.
IS IT ACTUALLY WORTH DOING? YES — one week on now-public data with a published algorithm, and every outcome pays: preserved-and-independent index opens a novel use question nobody has asked; an index inseparable from sex+emphysema is a decisive idea-009-style feasibility negative that also prices the other pending Sybil-anatomy candidates; a preprocessing-destroyed index kills the idea for the cost of a geometry audit.
```


===== ideas/017/debate.md =====
# Debate transcript



===== ideas/017/idea_card.json =====
{
  "id": "C5",
  "parent_ids": [],
  "revival_basis": null,
  "search_mode": "C",
  "entry_point": 2,
  "title": "A lung-cancer model may be reading a mechanically remodeled trachea",
  "question": "Is Sybil using the minimum intrathoracic tracheal index\u2014the transverse-to-anteroposterior ratio that defines saber-sheath trachea\u2014as a mechanically accumulated sign of COPD and smoking injury?",
  "rung": {
    "target": 3,
    "current": 0,
    "move_up": "Selective tracheal-index erasure and paired inspiration/reconstruction stability reach rung 1; separation from emphysema, sex, lung volume, and kernel plus external replication gates rung 2; saber-sheath trachea is the rung-3 name."
  },
  "deliverable_sentence": "Sybil is using saber-sheath tracheal deformity\u2014the fixed side-to-side narrowing of the intrathoracic trachea\u2014as a record of chronic obstructive lung injury.",
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
    {
      "citation": "Mikhael et al., Sybil",
      "identifier": "DOI 10.1200/JCO.22.01345; PMCID PMC10419602",
      "verified_fact": "Sybil predicts future lung cancer from a single low-dose chest CT and retains residual performance when visible nodules are removed.",
      "delta": "It did not measure tracheal index."
    },
    {
      "citation": "Pompe et al., CT quantification of tracheal abnormalities in COPD",
      "identifier": "PMCID PMC6052793",
      "verified_fact": "It defines an automated minimum tracheal index and found tracheal-shape information can add to emphysema in COPD severity assessment.",
      "delta": "It did not study a lung-cancer risk model or model reliance."
    }
  ],
  "existing_assets": [
    "Sybil code/weights and NLST pathway established in prior cycles",
    "Simple published automatic tracheal-index algorithm",
    "NLST acquisition metadata and repeat/reconstruction subsets"
  ],
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
    {
      "alternative": "The index is only a proxy for male sex or body size.",
      "resolution": "Sex- and thoracic-ratio matched analysis plus separate concept erasures."
    },
    {
      "alternative": "The index is only emphysema/hyperinflation.",
      "resolution": "Joint LAA-950, lung-volume, and tracheal-index erasures; require incremental selective effect."
    },
    {
      "alternative": "Apparent shape is respiratory phase or preprocessing anisotropy.",
      "resolution": "Native-to-tensor agreement and paired respiratory/reconstruction repeatability gates."
    }
  ],
  "anticipated_negative": {
    "classification": "decisive",
    "reason": "If tracheal index is accurately encoded and reliably measurable, yet its erasure has an equivalently null effect while emphysema erasure changes Sybil, the specific chronic-remodeling hypothesis is weakened."
  },
  "cross_domain": {
    "borrowed_construct": "Fatigue/remodeling of a pressure-loaded cartilaginous tube.",
    "measurement_implied": "A fixed minimum transverse/AP ratio and its respiratory stability, rather than generic airway size.",
    "if_analogy_dropped": "The experiment would measure tracheal caliber. The mechanics analogy changes X to anisotropic shape, predicts a low transverse/AP ratio, and requires stability across respiratory state."
  },
  "remaining_legwork": "2 days for preprocessing geometry audit, 3 days for NLST prevalence/collinearity on a small sample, and 2 days for repeatability. First go/no-go in one week.",
  "scores": {
    "mechanism_clarity": {
      "value": 5,
      "why": "A precise ratio, anatomical level, predicted direction, and chronic mechanical cause."
    },
    "identifiability": {
      "value": 4,
      "why": "Internal erasure plus emphysema/sex/volume controls and real paired scans attack the main alternatives; masked site remains."
    },
    "interest": {
      "value": 5,
      "why": "An under-read tracheal shape as a long-term smoking mechanics recorder is surprising."
    },
    "medical_relevance": {
      "value": 4,
      "why": "It could explain risk as chronic obstructive injury rather than occult tumor signal."
    },
    "clarity": {
      "value": 5,
      "why": "The model-uses-X sentence is concrete and falsifiable."
    },
    "feasibility": {
      "value": 3,
      "why": "Capped; measurement is easy but tensor preservation and prevalence are uninspected."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Capped; no direct Sybil/tracheal-index study was found in a bounded search."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Sybil assets and an automatic X algorithm already exist."
    },
    "data_readiness": {
      "value": 4,
      "why": "NLST/Sybil pathway is established in the repository record."
    },
    "evaluation_readiness": {
      "value": 4,
      "why": "Ratio, repeatability, partial association, and erasure controls are prespecifiable."
    },
    "negative_result_value": {
      "value": 5,
      "why": "After the encoding/reliability gate, a null erasure directly rejects the named mechanism."
    },
    "regret": {
      "value": 5,
      "why": "A one-week geometry audit could expose a simple overlooked signal."
    }
  },
  "mode_c_priority_score": 4.6,
  "priority_arithmetic": "0.30*5 + 0.25*4 + 0.20*5 + 0.15*4 + 0.10*5 = 4.60",
  "unverified_claims": [
    "Sybil preprocessing preserves tracheal aspect ratio",
    "Low tracheal index is prevalent enough in NLST",
    "The tracheal-index direction is separable from sex/emphysema/lung volume"
  ],
  "track": "baseline"
}


===== ideas/017/keystone_screen.md =====
# Keystone screen

## Keystone as stated

> Sybil's final input tensor preserves tracheal cross-sectional geometry accurately enough for minimum tracheal index to be measured and encoded, and NLST contains enough low-index cases independent of sex, emphysema, lung volume, and reconstruction for a selective-use test.

This is a conjunction. Both tensor-level measurement fidelity and an adequate, non-collinear NLST subgroup must be true. Failure of either part makes the proposed selective-use experiment impossible or uninterpretable.

## What I inspected

### Official Sybil inference preprocessing

I inspected the official `reginabarzilaygroup/Sybil` repository at commit `d9fc81b93c1c6239a570c1c570c1f2a2e6266a4a`.

The released inference path explicitly resamples and then crops or pads:

> `x = self.resample_transform(x)`
>
> `x = self.padding_transform(x)`

Source: [official Sybil repository, `sybil/serie.py`, lines 161–167](https://github.com/reginabarzilaygroup/Sybil/blob/d9fc81b93c1c6239a570c1c570c1f2a2e6266a4a/sybil/serie.py#L161-L167).

The target physical spacing is explicitly isotropic in-plane:

> `VOXEL_SPACING = (0.703125, 0.703125, 2.5)`

Source: [official Sybil repository, `sybil/datasets/utils.py`, line 9](https://github.com/reginabarzilaygroup/Sybil/blob/d9fc81b93c1c6239a570c1c570c1f2a2e6266a4a/sybil/datasets/utils.py#L9).

The final tensor dimensions are fixed at 256×256×200:

> `"img_size": [256, 256],`
>
> `"num_images": 200,`

Source: [official Sybil repository, `sybil/serie.py`, lines 239–250](https://github.com/reginabarzilaygroup/Sybil/blob/d9fc81b93c1c6239a570c1c570c1f2a2e6266a4a/sybil/serie.py#L239-L250).

These quoted facts show that the pipeline uses physical-spacing-aware resampling with equal row and column target spacing. They do **not** directly show native-DICOM versus final-tensor agreement for minimum tracheal index, retention of the relevant intrathoracic tracheal segment after crop/pad, or that Sybil encodes the ratio.

### Primary Sybil cohort report

The primary paper states:

> “We applied for and were granted access to the radiologic and clinical data from a sample of 15,000 NLST participants”

Source: [Mikhael et al., *Journal of Clinical Oncology*, Materials and Methods, “NLST Data”](https://pmc.ncbi.nlm.nih.gov/articles/PMC10419602/#sec2).

This establishes the broad cohort size, not the number of low-index cases or their joint distribution with sex, emphysema, lung volume, and reconstruction. I found no primary-source table or released schema containing the automatically measured tracheal index needed to verify that part without running the proposed Stage 0 measurement on accessible images.

## Residual assumption check

Mandatory question: **If this card only verified the nearest checkable thing, what is it still assuming?**

It verified the adjacent fact that Sybil resamples scans to equal in-plane physical spacing. It still assumes that interpolation and center crop/pad preserve the *minimum* centerline-perpendicular transverse/AP ratio with acceptable error on actual NLST scans, that the relevant tracheal segment remains in-frame, and that enough low-index cases remain after matching or adjustment for sex, emphysema, lung volume, and reconstruction. Those are the load-bearing facts, and neither the implementation alone nor the published sample size verifies them.

The stated keystone is therefore correctly aimed at the real assumptions, but it cannot be resolved from the inspected primary sources. It requires direct paired measurement on native DICOM and final tensors plus a joint-distribution audit on obtainable NLST cases.

```json
{"verdict": "UNVERIFIABLE", "evidence": "x = self.resample_transform(x) / x = self.padding_transform(x)", "source": "https://github.com/reginabarzilaygroup/Sybil/blob/d9fc81b93c1c6239a570c1c570c1f2a2e6266a4a/sybil/serie.py#L161-L167", "note": "Official code verifies physical resampling and crop/pad, but no inspected primary source establishes final-tensor tracheal-index agreement or an adequate non-collinear NLST low-index subgroup."}
```


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
This is round 1. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript


