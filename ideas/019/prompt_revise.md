You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/019
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

- **DATA_ACCESS** x2: Required data, checkpoints, or mappings are not obtainable in practice.
- **IDENTIFIABILITY_FAILURE** x2: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.
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
- **idea-018** [REJECTED/DEBATED/baseline] -- The brain-tumor prognosticator may be weighing the chewing muscle -- killed: DATA_ACCESS
- **idea-019** [SHORTLISTED/DEBATED/wide] -- The fibrosis model may be counting holes at the pleural edge
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


===== ideas/019/README.md =====
# Idea 019: The fibrosis model may be counting holes at the pleural edge

Selected from scouting cycle 007, candidate 7.


===== ideas/019/consensus.md =====
# Debate summary — idea 019

## Agreed

- The released CT-CLIP code names ClassFine output index 11 `Pulmonary fibrotic sequela`; it does not expose a pulmonary-fibrosis output. The endpoint must be renamed, and the UIP/prognosis framing must be reduced accordingly (Round 1).
- Honeycombing support in the obtainable evaluation partitions is not established. A report-text audit may be used only as a preregistered feasibility and prevalence gate, never as the confirmatory measurement of X. The proposed K1 floor is at least 30 honeycomb-mentioning, fibrotic-sequela-positive volumes, including at least 15 in the required thin-slice stratum; failure ends the study as `DATA_INSUFFICIENT` before image download (Round 1).
- Naive linear-direction erasure does not by itself demonstrate model use. Projection can damage off-manifold embeddings and remove correlated scar-severity information, so the card's claim that internal erasure avoids idea 006's OOD failure is incorrect (Round 2).
- An erasure-based rung-1 claim is conditional on validation-set gates established before test use: G2a must show native-neighborhood/density equivalence, and G2b must show an effect beyond case-matched sham projections equated for embedding displacement and local ClassFine-head sensitivity. If either gate fails, test-set erasure is cancelled and the remaining association and kernel-pair analyses are exploratory only (Round 2).
- Geometry-matched reconstruction pairs are complementary evidence, not a substitute causal instrument. They can reveal sensitivity to reconstruction-rendered wall topology while holding anatomy fixed, but kernel changes also alter noise and generic high-frequency texture (Round 2).
- Native-to-final-tensor repeatability establishes preservation, not semantic denotation. Without an independent construct-validity reference, the deterministic measurement cannot be called honeycombing because it may mix paraseptal emphysema, traction bronchiolectasis, and reconstruction-created wall closure (Round 3).
- Report mentions cannot supply that construct validity. The confirmatory X must therefore be named literally as the prespecified subpleural cyst-network topology index; “honeycombing” remains an out-of-scope rung-3 target (Round 3).
- The design does not presently die from annotation provenance because its primary analysis requires no reader labels, but it inherits that prior lesson: reader-derived report language cannot confer the missing clinical name on X (Round 3).

## Unresolved

### Does narrowing the confirmatory sentence to a topology index preserve the candidate's identity?

- **Proposer's position:** Yes. The same model, physical measurement, motivating question, and prohibited conclusions remain; only the rung that obtainable evidence can certify has been corrected. The candidate may be revised in place.
- **Critic's position:** The critic identifies a real boundary: the index-level study is sound, but replacing the physician-level honeycombing result with an unnamed computed index narrows the original claim. The critic leaves the governance classification to human review.
- **What evidence would settle it:** No empirical evidence settles this; it is an application of the portfolio's claim-identity governance rule. The human must decide whether demoting the original deliverable sentence from result to future target constitutes a changed claim identity requiring supersession.

### Can the topology index be validated as honeycombing and thereby reach rung 3?

- **Proposer's position:** Not with the current evidence. A bounded search should check the cited AJRCCM 2024 quantifier and other candidates, but failure to find one is not proof none exists.
- **Critic's position:** The name is justified only after either an obtainable, citable quantifier with released weights and external validation against the named mimics agrees with the frozen index on CT-RATE native and final tensors, or an independently adjudicated dataset validates the index and its frozen thresholds transport to CT-RATE.
- **What evidence would settle it:** Direct inspection and execution of such a released quantifier, including prespecified agreement and failure analysis on native and final tensors; alternatively, construct validation on an independent adjudicated honeycombing dataset followed by threshold transport to CT-RATE. Repeatability, report-term enrichment, and score association are insufficient.

### Will CT-RATE contain enough suitable cases for the proposed study?

- **Proposer's position:** This is an empirical kill gate, with a proposed minimum of 30 honeycomb-mentioning sequela-positive evaluation volumes and 15 thin-slice cases.
- **Critic's position:** The support must be demonstrated before image-level work; otherwise neither positive nor null evidence about the head's use of topology is interpretable.
- **What evidence would settle it:** A frozen audit of the obtainable CT-RATE evaluation reports, RadBERT labels, and slice-thickness metadata, followed by a documented power or precision calculation appropriate to the actual within-pair sample. The report audit establishes support only, not X.

### Can the latent intervention pass the agreed validity gates?

- **Proposer's position:** A minimal-displacement affine erasure in the LEACE family may pass G2a/G2b; if it does not, failure is a useful rung-0 feasibility result and no model-use claim will be made.
- **Critic's position:** Only the prespecified native-manifold and case-matched sham evidence can make the intervention interpretable; a low correlation among learned directions or ordinary random projections is inadequate.
- **What evidence would settle it:** Validation-only results showing the frozen intervention meets preregistered kNN/density-equivalence margins and exceeds displacement-and-local-sensitivity-matched sham effects, followed by locked test evaluation. Gate failure settles only that this intervention cannot support rung 1, not that the model does not use topology.

## Positions that moved

- **Proposer, Round 1:** Conceded the endpoint error after direct inspection of official CT-CLIP code and accepted the critic's argument that a broad fibrotic-sequela label weakens the medical interpretation. The proposer renamed the output, reduced medical relevance, and made prevalence a kill gate. This concession was earned by a factual objection and new primary-code inspection.
- **Critic, Round 2:** Conceded that the Round 1 endpoint correction and prevalence gate adequately repaired the endpoint/support objection while preserving the motivating question.
- **Proposer, Round 2:** Conceded that internal erasure is not inherently in-distribution and that the kernel-pair arm cannot replace a causal use test. In response to the critic's explicit validation conditions, the proposer adopted G2a/G2b and an automatic exploratory demotion branch. This was an earned amendment.
- **Critic, Round 3:** Conceded conditionally that G2a/G2b adequately answer the latent off-manifold objection when passed, while preserving the limitation that the evidence concerns a topology-derived direction.
- **Proposer, Round 3:** Conceded that the computed topology index lacks construct validity as honeycombing and that report mentions cannot supply it. The proposer demoted the confirmatory claim to the literal index and moved the physician-level term to a future rung-3 target. This was earned by the critic's concrete mimic and resampling arguments; it was not capitulation.
- No concession was UNEARNED. The debate required three rounds, raised substantive objections, and did not exhibit one-round rubber-stamping.

## Amendments made

At round zero, the card claimed that CT-CLIP's supposed pulmonary-fibrosis score uses honeycombing, targeted rung 3, treated linear topology-direction erasure as the primary use instrument, described its anticipated null as decisive, and asserted that latent erasure avoided idea 006's OOD problem.

The agreed design instead:

- targets the actual pulmonary-fibrotic-sequela output at ClassFine index 11;
- runs the free K1 prevalence/support gate before image download;
- uses the literal subpleural cyst-network topology index as confirmatory X;
- permits a conditional rung-1 claim only if the topology encoding and G2a/G2b intervention-validity gates pass;
- cancels confirmatory test erasure and reports rung 0/exploratory findings if those gates fail;
- keeps the reconstruction-pair analysis as complementary association evidence;
- classifies an erasure null as sensitivity-limited unless every prerequisite gate passes;
- treats independent construct validation as the required move from the index-level claim to the physician-legible honeycombing sentence.

What was lost is substantial: the endpoint is a general scarring-sequela score rather than an ILD/fibrosis score; the UIP and prognosis framing no longer follows; medical relevance, interest, identifiability, and negative-result value must be reduced; rung 1 is conditional rather than promised; and the physician-legible rung-3 sentence is not an output of the currently obtainable study. The current `idea_card.json` still contains the superseded endpoint, rung target, intervention logic, scores, priority arithmetic, `dies_like_prior` statement, and unverified-claims list and therefore cannot represent the converged design without revision.

## Recommendation

**REVISE.** The debate produced a coherent conditional rung-1 feasibility/use study, but the existing card is materially stale and the program's required physician-legible endpoint remains outside the evidence. Before deciding whether revision-in-place is permissible, the human should look most closely at the claim-identity boundary: whether replacing “the model uses honeycombing” with “the model uses a prespecified subpleural cyst-network topology index” is rung honesty within the same candidate or a new deliverable sentence that must be registered as a successor.

```json
{"verdict": "REVISE", "unblock": "Human resolves the claim-identity boundary, then the card is rewritten to the agreed index-level, K1-gated, G2a/G2b-conditional rung-1 design (or registered as a successor if the deliverable sentence is judged changed)."}
```


===== ideas/019/critique.md =====
# Critique — Idea 019: The fibrosis model may be counting holes at the pleural edge

```
FATAL OBJECTION: NONE that survives repair — but the card decodes a nonexistent
output: CT-CLIP has no "pulmonary fibrosis" score; the actual CT-RATE label is
"pulmonary fibrotic sequela," a report phrase dominated by post-infectious
scarring, and honeycombing-positive support in this cohort is unverified.
EVIDENCE: CT-RATE 18-label vocabulary (primary arXiv:2403.17834; exact list
quoted in arXiv:2603.06467 and arXiv:2607.02998); idea-007 precedent in evidence/decisions.md.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

---

## 1. The endpoint is mislabeled, and it matters (strongest objection)

**Verified fact.** The CT-RATE label vocabulary that CT-CLIP's ClassFine head
is trained on contains 18 findings: medical material, arterial wall
calcification, cardiomegaly, pericardial effusion, coronary artery wall
calcification, hiatal hernia, lymphadenopathy, emphysema, atelectasis, lung
nodule, lung opacity, **pulmonary fibrotic sequela**, pleural effusion, mosaic
attenuation pattern, peribronchial thickening, consolidation, bronchiectasis,
interlobular septal thickening. There is no "pulmonary fibrosis" label.
Verification status: I could not fetch the primary PDF (arXiv:2403.17834) in
this session; the list is quoted identically by two independent papers that use
CT-RATE ([arXiv:2603.06467](https://arxiv.org/pdf/2603.06467),
[arXiv:2607.02998](https://arxiv.org/pdf/2607.02998)). Revision must confirm
against the primary label CSV header after dataset gating is accepted.

**Source-supported interpretation.** "Fibrotic sequela" is report language for
the residue of prior disease — post-infectious/post-inflammatory bands, apical
scarring, post-TB change — in a general Turkish hospital population (CT-RATE
originates from Istanbul Medipol University Mega Hospital, per the
[HF dataset card acknowledgments](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE)).
That is a much broader and mostly *non-UIP* entity. The card's medical framing
(honeycombing changes UIP interpretation and prognosis; medical_relevance = 5)
presumes the score is an ILD/fibrosis score. It is not; it is a
"scarring-mentioned-in-report" score. Two consequences:

- **Prior plausibility drops.** If most positive labels are linear scarring
  without cysts, the model has little training pressure to encode honeycomb
  topology for this head. The hypothesis is not dead — honeycomb cases are a
  subset of label-positives and may be high-confidence ones — but the card's
  framing oversells it.
- **Prevalence/power is now the second keystone.** The 250-test-scan erasure
  plan assumes honeycombing-positive support. If honeycombing prevalence in a
  general hospital cohort is on the order of 1–3%, an unenriched 250-scan set
  contains a handful of positives. The card lists "enough thin-slice
  honeycombing" as an unverified claim; it is actually a gate that can be
  checked **for free** (section 6) and must be checked before any design work.

This is the exact error of idea 007 ("CT-CLIP has no mosaic attenuation head —
card claimed a nonexistent output," evidence/decisions.md 2026-08-05), which
was survivable there and is survivable here: the deliverable sentence names
CT-CLIP and honeycombing, not the phrase "fibrosis score," so renaming the
endpoint and downgrading the UIP framing repairs the card without changing the
question's identity under the 2026-08-10 claim-identity rule. But the repair is
mandatory, and medical_relevance = 5 does not survive it.

## 2. The primary rung-1 instrument (linear direction erasure) has weak causal semantics

Three distinct problems, none addressed by the card's nuisance-direction
controls:

- **Correlated-feature removal.** Erasing a linear direction removes everything
  correlated with it, not the concept alone; this is the standard critique of
  amnesic-probing/INLP-style interventions (Elazar et al., *Amnesic Probing*,
  TACL 2021; LEACE, arXiv:2306.03819 — both cited from memory, method-critique
  not medical claims). In a referral-enriched cohort, honeycomb topology is
  strongly correlated with overall fibrotic extent and severity. The learned
  "topology direction" will substantially overlap the severity axis, so
  "selective" erasure is likely ill-conditioned. Erasing matched nuisance
  directions *measures* the collinearity; it does not remove it.
- **Off-manifold embeddings.** A frozen classifier head applied to a
  projected-out embedding is being evaluated out of distribution. This is
  idea-006's fatal error (extreme intervention → OOD → neither direction
  identifies reliance) transplanted from voxel space into latent space. The
  portfolio has already rejected this move once; the card does not explain why
  latent-space OOD is more defensible than image-space OOD.
- **Consequence for the "decisive" negative.** The anticipated negative is
  classified decisive, with negative_result_value = 5. In the likely regime
  where topology and reticulation/severity directions are substantially
  collinear, a topology-null/reticulation-positive result is
  **sensitivity-limited, not decisive** — it may only mean the decomposition
  failed. Decisiveness requires prespecified encoding gates *and* a maximum
  admissible collinearity between frozen directions, neither of which is in
  the card. negative_result_value should be 3 pending those gates, and
  identifiability 4 → 3.

Portfolio note: representation-erasure is already at ×3 on the homogenization
watch. A revision that replaces or supplements erasure with a natural-paired
readout (section 6) is both scientifically and portfolio-wise better.

## 3. Mimic separability may be unverifiable even in Stage 0

The keystone screen honestly reports `UNVERIFIABLE`. But it treats the audit as
purely a preservation question. The harder half is the **reference problem**:
Stage 0 proposes to establish that the topology measure separates honeycombing
from paraseptal emphysema and traction bronchiolectasis "without human labels"
— separates it *against what ground truth*? With no reference standard, Stage 0
can show the measure is stable and non-degenerate, not that it measures
honeycombing. Two defensible escapes, both allowed by the charter's "existing,
citable tool" clause:

- An off-the-shelf honeycombing/fibrosis segmentation model with released
  weights (deep-learning honeycombing quantifiers exist, e.g. the AJRCCM 2024
  IPF progression work, [DOI 10.1164/rccm.202311-2185OC](https://www.atsjournals.org/doi/full/10.1164/rccm.202311-2185OC);
  CALIPER itself is proprietary/Imbio). Whether any has *public weights* is
  unverified and must be checked in revision — if one exists, it can serve as
  the convergent reference for the bespoke topology instrument, or replace it.
- Report-text mentions of "honeycomb" as an **exploratory-only** convergent
  check (reader-derived, so never the primary readout; see section 6).

Also unstated: excluding traction bronchiolectasis requires airway
segmentation, and distal airway segmentation on 0.75×0.75×1.5 mm resampled
routine CT of fibrotic lungs is exactly where such tools fail. The wall
completeness that distinguishes multilayer honeycombing from single-layer
paraseptal emphysema (~1 mm walls on 3–10 mm cysts) is the first casualty of
thick native slices; trilinear resampling to 1.5 mm cannot restore a wall a
5 mm native reconstruction never resolved. The thin-slice stratum is not a
robustness check — it is the only stratum where the instrument can work, and
its size is unknown.

## 4. Rung target 3 rests on unnamed external data

Rung 2 → 3 requires "external ILD replication" with no named, obtainable
dataset. OSIC (Kaggle) has fibrosis CTs but is a progression cohort with
domain shift for CT-CLIP; no other candidate is named. Under this program's
standards an unnamed replication resource is vapor: the honest target within
obtainable data is **rung 1** (the model uses subpleural cyst topology), with
rung 2 partially addressed by reconstruction-pair stability inside CT-RATE.
The card's `rung.move_up` should be rewritten accordingly.

## 5. Data access and compute — mostly fine, one stale ledger note corrected

**Verified fact.** Trained checkpoints are obtainable: the official CT-CLIP
README links `models/CT-CLIP-Related/CT-CLIP_v2.pt` inside the gated CT-RATE
HF repo, with CT-CLIP, VocabFine, and ClassFine variants. The 2026-08-04
ledger note "checkpoints are not on the authors HF account" is stale or
referred only to release assets; idea 004/013 planning already assumed local
inference, and the asset path is now confirmed. Gated-but-obtainable is
consistent with the standing treatment of CT-RATE (ideas 004, 006, 013).

Compute: 370 volumes ≈ 50–100 GB download plus inference plus cubical
persistence in "one Colab Pro+ session" is optimistic by maybe 2–3×, but this
is the same envelope class as approved ideas. Not a rejection ground.

## 6. The low-hanging fruit the card missed (and the easier version)

CT-RATE releases **English report text and per-volume RadBERT labels for free,
without downloading a single image**. That yields a Stage 0a that costs hours
and gates everything downstream:

- Regex the validation reports for honeycomb terms → direct measurement of
  honeycombing-mention prevalence, the power gate of section 1.
- Cross-tabulate honeycomb-mention against the fibrotic-sequela label →
  what fraction of label-positives are even candidate honeycomb cases.
- (Exploratory only, reader-derived, never the primary readout:) does the
  ClassFine fibrotic-sequela score separate honeycomb-mentioning fibrosis from
  fibrosis-without-honeycomb? A null here — score indifferent to the report's
  honeycomb mention — already substantially deflates the hypothesis before any
  topology instrument is built. Label-leakage caveat: this stratification uses
  report text, so it gates and motivates but cannot confirm.

Stage 0b is then the preservation audit on ~20 thin-slice honeycomb-mention
volumes (native vs final tensor), before committing to the 370-volume design.

**Easier rung-1 design that avoids erasure entirely:** idea 004 has already
identified 425 geometry-matched same-acquisition kernel pairs. Sharp vs soft
kernels change apparent wall completeness — the exact substrate of the topology
measure — while anatomy, patient, site, protocol, and positioning are held
fixed. Within pairs: does the change in fibrotic-sequela score track the change
in measured subpleural cyst topology beyond generic sharpness/noise metrics?
This is the charter's praised structural move (model compared to itself on
identical anatomy, no labels in the readout), reuses idea 004's Stage 0
inventory, and is a natural-paired design rather than a fourth
representation-erasure entry. Its limitation is honest: it identifies
sensitivity to reconstruction-rendered wall topology, not native honeycombing
use, so it complements rather than replaces a topology-association arm.

## 7. Checks that pass

- **Circularity:** X (deterministic voxel/graph topology) is not a re-encoding
  of the fibrotic-sequela label or of the score. Passes, unlike idea 010.
- **Annotation provenance:** the primary readout uses no reader labels; report
  text enters only as an exploratory gate. The dominant program failure mode
  does not apply — provided revision keeps the report-derived stratification
  out of the confirmatory claim.
- **Prior-work overlap:** bounded searches found no study testing a frozen
  foundation model's reliance on honeycomb topology. Closest new neighbor to
  add: persistent-homology analysis of longitudinal CT fibrotic features in
  COPD ([ERJ, early 2026](https://publications.ersnet.org/content/erj/early/2026/02/26/1399300301630-2025))
  — descriptive PH on lung CT, no model-reliance test; plus DL honeycombing
  quantification (section 3). The novelty delta survives; novelty_confidence
  stays capped at 3.
- **Keystone procedure:** the screen's `UNVERIFIABLE` verdict and
  residual-assumption check are honest and correctly identify preservation as
  the load-bearing fact. No wrong-keystone error here — though section 3 adds
  the reference-standard problem as a co-equal part of the same keystone.

## Required in revision

1. Rename the endpoint to the pulmonary-fibrotic-sequela score everywhere;
   verify the label list against the primary CSV; downgrade medical_relevance
   (5 → 3) and rewrite the UIP framing as conditional on honeycomb-positive
   support existing in CT-RATE.
2. Add free Stage 0a (report-text prevalence and stratification gate) before
   any image download; make its outcome a numbered kill condition.
3. Demote or replace linear erasure as the primary rung-1 instrument; if
   retained, prespecify encoding gates and a maximum admissible direction
   collinearity, and reclassify the anticipated negative as
   sensitivity-limited unless those gates pass (negative_result_value 5 → 3,
   identifiability 4 → 3).
4. Name the mimic-separability reference (released-weights honeycombing
   segmenter, verified, or convergent report-text check labeled exploratory).
5. Retarget rung 1 within CT-RATE; strike the unnamed external replication
   from the rung ladder.
6. Consider the kernel-pair natural-paired arm reusing idea 004's 425 pairs.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does CT-CLIP's pulmonary-fibrotic-
sequela score track measured subpleural cyst topology — gated first by a free
report-text prevalence check, and tested within geometry-matched kernel pairs
where anatomy is held fixed — rather than generic density or sharpness?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — honeycombing-vs-mimic remains
the payload, but the UIP/prognosis framing shrinks to what a scarring-sequela
score can support.
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — same deliverable sentence and
prohibited conclusions; this is narrowing and instrument repair, which is
revision-in-place under the 2026-08-10 claim-identity rule.
IS IT ACTUALLY WORTH DOING? YES — Stage 0a costs hours, uses already-released
text and labels, and either kills the idea cleanly (no honeycomb support) or
buys a genuinely novel, annotation-free model-decoding study; that
cost-to-decisiveness ratio is the best currently available in this idea.
```


===== ideas/019/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The experiment currently decodes a nonexistent pulmonary-fibrosis output, and the available pulmonary-fibrotic-sequela head is not an interpretable surrogate unless CT-RATE contains enough honeycombing-bearing positives to give that head training pressure to use honeycomb topology.

**Argument:** CT-CLIP's CT-RATE vocabulary reportedly contains "pulmonary fibrotic sequela," not "pulmonary fibrosis." That distinction breaks the card's present endpoint and medical interpretation: a report-derived sequela label in a general hospital cohort can be driven by linear post-infectious or post-inflammatory scars, apical scarring, or other residual change without any connected multilayer subpleural cyst network. Even a technically clean topology perturbation would therefore be underidentified if honeycombing is rare: a null could mean the head was never trained on enough honeycombing, while a positive could reflect correlation with overall scar burden rather than the defining topology. The required identity check does not itself kill a repair—renaming the endpoint and conditionally asking whether that exact head uses honeycombing still tests the original deliverable sentence—but substituting a generic reconstruction-sensitivity claim would not. Before image-level work, the official label CSV/checkpoint schema must establish the exact output, and a frozen report-text audit must estimate honeycomb-mention prevalence and its overlap with fibrotic-sequela positives; report text may gate feasibility but cannot become the confirmatory X because it is reader-derived.

**What would change my mind:** Direct inspection of the released label CSV and checkpoint output mapping showing the pulmonary-fibrotic-sequela head, plus a prespecified report audit showing enough honeycomb-mentioning fibrotic-sequela-positive volumes in the obtainable validation/test partitions to meet a stated precision or power target for the planned within-pair analysis.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card decodes an output that does not exist. The real
head is "pulmonary fibrotic sequela" — report language for residual scarring
of any cause, mostly non-UIP in a general Turkish hospital cohort — and unless
CT-RATE demonstrably contains enough honeycombing-bearing sequela-positives,
the experiment is underidentified in both directions: a null could mean the
head never had training pressure to encode honeycomb topology, and a positive
could mean correlation with overall scar burden rather than the defining
topology. The endpoint identity and the prevalence audit must both be settled
before any image-level work.

**Response:** AMEND

**Argument:** The factual core of the objection is correct, and I have now
verified it by direct inspection rather than leaving it at the critic's
"reportedly." I cloned the official CT-CLIP repository at commit
`a2a155c601987820433c01db69b64d701d3d229d` — the same commit the keystone
screen inspected — and searched the released code:

- `scripts/CTCLIPTrainer.py:285` and `scripts/ct_lipro_inference.py:76` both
  hard-code the 18-item pathology list; it contains `'Pulmonary fibrotic
  sequela'` and no "pulmonary fibrosis" entry.
- `scripts/bootstrap_values.py:55-73` gives the explicit output-index mapping:
  `11: 'Pulmonary fibrotic sequela'`. This is the checkpoint output mapping
  the critic asked for, at the code level. The gated label CSV header remains
  to be confirmed after dataset access, but the released training and
  inference code is the authoritative statement of what the ClassFine head
  emits, and it settles the vocabulary question: the card's endpoint name was
  wrong. (Verified fact, this session.)

The amendment, in four parts:

1. **Endpoint rename, everywhere.** The decoded output is the
   pulmonary-fibrotic-sequela score (ClassFine index 11). The question
   becomes: *does CT-CLIP's pulmonary-fibrotic-sequela score use connected
   multilayer subpleural cyst topology, rather than generic peripheral
   high-frequency texture, on the subset of cases where that topology exists?*
   Identity check: the deliverable sentence named CT-CLIP and honeycombing,
   not the phrase "fibrosis score," so the amended design still answers the
   original one-sentence question about the same model, the same X, and the
   same prohibited conclusions. This is narrowing and instrument repair under
   the 2026-08-10 claim-identity rule, not a new study.

2. **What is lost — stated plainly.** The UIP/prognosis framing shrinks to
   what a scarring-sequela head can support: `medical_relevance` drops 5 → 3.
   A positive result no longer says "an ILD model reads honeycombing"; it says
   "a general-scarring head, when scored on honeycomb-bearing cases, uses the
   cyst network rather than scar burden alone." That is a weaker medical
   claim. It is still the physician-legible mechanism the idea was built on,
   and the conditional form is honest about the head's training distribution.

3. **Stage 0a becomes numbered kill condition K1, before any image
   download.** On the obtainable CT-RATE report text and RadBERT labels
   (released without image gating): (a) regex the validation/test partitions
   for honeycomb terms; (b) cross-tabulate mentions against
   fibrotic-sequela-positive labels. Prespecified floor: at least 30
   honeycomb-mentioning, sequela-positive volumes in the obtainable evaluation
   partitions, of which at least 15 fall in the thin-slice stratum the
   topology instrument requires. The floor of ~30 is chosen so a medium
   association (r ≥ 0.5) is detectable at 80% power, α = 0.05; the exact
   arithmetic for the within-pair arm goes in the revised card. Below the
   floor, the idea dies as DATA_INSUFFICIENT without a single volume
   downloaded. Report text gates and stratifies; it never becomes the
   confirmatory X — full agreement with the critic on that boundary.

4. **The positive-direction confound is absorbed, not dodged.** The critic's
   second horn — a positive could be scar-burden correlation — is the
   collinearity problem the critique round already flagged against linear
   erasure. The amended card adopts the corresponding repairs: prespecified
   encoding gates and a maximum admissible collinearity between the frozen
   topology and scar-burden/reticulation directions, with the anticipated
   negative reclassified as sensitivity-limited (`negative_result_value`
   5 → 3) unless those gates pass. A null on a head that Stage 0a has shown
   *does* have honeycomb-positive support, with encoding gates passed, is the
   only null the amended card counts as decisive.

Amendment count check: this is the first amendment, and it responds to a
verified factual error in the card, not to a feasibility squeeze. The
motivating question survives it intact; what does not survive is the inflated
medical framing, and that deflation is the repair working as intended.

**Status:** CONVERGED — the endpoint mapping is now directly inspected
(`bootstrap_values.py:67`, commit `a2a155c`), and the remaining half of the
critic's condition, the prevalence audit, is no longer a point of argument:
it is kill condition K1, prespecified with a floor and executed on free
report text before any image work. If K1 fails, the critic was right in the
strong sense and the idea dies cheaply.

## Round 2 — CRITIC

**Position:** The endpoint correction preserves the original question, but the proposed linear-direction erasure still cannot identify use of honeycomb topology because projection-induced score changes are inseparable from off-manifold embedding damage and removal of correlated scar severity.

**Argument:** I concede the Round 1 endpoint objection: direct inspection of the official CT-CLIP code establishes ClassFine index 11 as `Pulmonary fibrotic sequela`, and the conditional rename still asks the original question about whether CT-CLIP uses connected multilayer subpleural cyst topology. Making honeycomb prevalence a preregistered kill gate is also an adequate response to the support problem. The remaining causal instrument, however, is not repaired by promising an encoding gate and a maximum correlation between learned directions. A low pairwise correlation between linear topology and reticulation/scar-burden directions does not establish that subtracting one direction changes only topology information; nonlinear and distributed severity information can share the removed subspace, and the frozen ClassFine head has never been validated on projected embeddings. Thus a selective score decrease after projection can arise because the intervention moves honeycomb-bearing cases farther off the native embedding manifold, not because the head used X. Matched random or nuisance projections do not solve this unless they are matched for manifold displacement and local head sensitivity case by case. This is the latent-space version of idea 006's OOD-intervention failure, which the current `dies_like_prior` field incorrectly claims to avoid merely because erasure occurs internally. The geometry-matched kernel-pair arm is not a substitute for the claim either: it identifies sensitivity to reconstruction-rendered wall topology, while kernel changes also alter noise and generic high-frequency texture, so by itself it does not establish native honeycombing use. The idea remains scientifically plausible, but its primary rung-1 evidence is association plus an uninterpretable intervention.

**What would change my mind:** Show, before test-set use, a validated latent intervention whose projected embeddings remain within a prespecified native-neighborhood or density-equivalence margin and whose score effect is unchanged under case-matched sham projections equated for manifold displacement and local ClassFine-head sensitivity; alternatively, provide an image-space topology-specific edit that passes prespecified in-distribution and sham-effect gates while holding scar extent, density, emphysema, and reconstruction statistics fixed. Without one of those, demote the study to exploratory association and do not claim rung 1.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The linear-direction erasure cannot support a rung-1 use
claim as designed. A score drop after projection has two explanations the
current controls cannot separate: the intervention pushed honeycomb-bearing
cases off the native embedding manifold that the frozen ClassFine head was
trained on — the latent-space version of idea 006's OOD failure, which the
card's `dies_like_prior` field wrongly claims to have avoided — and the
removed subspace carries nonlinear, distributed scar-severity information that
a low pairwise correlation between learned directions does not exclude. Sham
projections only help if matched, case by case, for manifold displacement and
local head sensitivity. The kernel-pair arm is complementary, not a
substitute: it identifies sensitivity to reconstruction-rendered wall
topology, not native honeycombing use. Either validate the intervention
against these gates before test use, or demote to exploratory association and
do not claim rung 1.

**Response:** AMEND

**Argument:** The core of the objection is conceded, and the amendment adopts
the critic's own disjunction as the design rather than approximating it.

**Conceded outright.** First, an ungated projection is an unvalidated
intervention: off-manifold is a property of the training distribution of the
head, not of the space the intervention happens to live in, so "erasure occurs
internally" earns nothing by itself. The `dies_like_prior` field is wrong as
written and will be rewritten in revision: the card does *not* structurally
avoid idea 006's failure mode; it must buy its way out with validation gates,
case by case, or it inherits that failure. Second, I do not contest the
characterization of the kernel-pair arm. It stays in the design as a
complementary associational arm (with the paired score change regressed on the
paired topology-measure change controlling for measured noise and spectral
band-power changes, which sharpens but does not transform it), and it is never
offered as the rung-1 instrument.

**The amendment — the critic's condition becomes the gate structure.**

1. **Instrument choice.** Naive orthogonal projection is replaced by
   minimal-displacement affine concept erasure in the LEACE family
   (arXiv:2306.03819 — method citation from memory, to be verified in
   revision), selected precisely because it minimizes the embedding
   displacement that gate G2a polices. If no released implementation is
   usable, the naive projection may still be evaluated — but only through the
   same gates, which it is then likely to fail, and that failure is the
   finding.

2. **Gate G2a — manifold validity, prespecified.** On validation embeddings
   only: projected embeddings must remain within a prespecified
   native-neighborhood margin — kNN distance to the native validation
   embedding cloud within a fixed quantile of native-to-native distances, plus
   a density-equivalence margin, both frozen before any test-set scoring.
   Failure means no erasure-based claim of any kind is made.

3. **Gate G2b — case-matched shams, prespecified.** For each case, sham
   directions are constructed to match, case by case, (i) the embedding
   displacement norm produced by the topology erasure and (ii) the local
   ClassFine-head sensitivity along the removed direction, measured as the
   magnitude of the head's directional derivative — computable exactly because
   the head is frozen and differentiable. Rung-1 evidence requires the
   topology-erasure score effect to exceed the sham-effect distribution at a
   prespecified quantile, with the nuisance battery (reticulation, density,
   emphysema directions erased separately) retained on top. This is the
   displacement-and-sensitivity-equated sham the critic specified, adopted
   verbatim, not a matched-random approximation.

4. **Automatic demotion, prespecified.** If either gate fails on validation,
   the confirmatory erasure arm is cancelled before the test set is touched.
   The study then reports the topology-score association and the kernel-pair
   arm, both labeled exploratory, claims rung 0, and its headline deliverable
   becomes the feasibility finding "linear erasure cannot be validated as an
   in-distribution intervention for this head" — which the charter counts as
   success (a feasibility result that prevents wasted effort) and which the
   ledger records so no later candidate spends the same instrument on CT-CLIP
   unvalidated. The critic's "demote and do not claim rung 1" branch is thus
   not a concession I might be forced into later; it is the prespecified else-
   branch of the design.

5. **The image-space alternative is noted, not adopted.** A topology-specific
   wall-breaking edit with in-distribution and sham-effect gates is the
   critic's other escape. It is not taken as primary here: validating
   synthetic subvoxel wall edits on 1.5 mm resampled tensors is a strictly
   heavier lift than the latent gates, and the portfolio already carries an
   edit-validity debate of exactly this shape (idea 008). If the latent gates
   fail, that edit is the natural successor and should enter as a spin-off
   candidate under the claim-identity rule, not as amendment three of this
   card.

**What is lost.** Rung 1 is now conditional, not promised: the card's rung
target within obtainable data becomes "rung 1 if gates G2a and G2b pass,
otherwise exploratory association only." Identifiability drops 4 → 3 and the
anticipated negative remains sensitivity-limited unless all gates pass, as
already set in amendment one. A residual limitation goes into the card
verbatim: even a fully gated positive identifies use of the information
carried along the validated linear topology direction — nonlinear encodings
sharing that subspace are not excluded — so the deliverable sentence acquires
the qualifier "as linearly encoded in the model's representation," and the
nuisance battery is what earns "rather than scar burden alone."

**Identity check.** The revised design still answers the original one-sentence
question — does CT-CLIP's (fibrotic-sequela) score use connected multilayer
subpleural cyst topology — about the same model, the same X, and the same
prohibited conclusions. What changed is the burden of proof imposed on the
instrument before the claim may be made, and the prespecified fallback when
that burden is not met.

**Amendment count.** This is amendment two. Per the rules, a third structural
amendment should be read as evidence the original design was wrong; I flag
that now so the next round can hold me to it.

**Status:** CONVERGED — the proposer adopts the critic's disjunction as the
design itself: rung 1 is claimable only through the exact validated-
intervention gates the critic specified (manifold margin plus case-matched
displacement-and-sensitivity-equated shams, established on validation before
any test use), and on gate failure the study self-demotes to exploratory
association with no rung-1 claim. The nonlinear-residual limitation is not
contested; it is recorded as a scope qualifier on the deliverable sentence.

## Round 3 — CRITIC

**Position:** The revised gates may validate an intervention on a topology-derived latent direction, but they still cannot establish that the independently computed X is honeycombing rather than a mixture of paraseptal emphysema, traction bronchiolectasis, and reconstruction-created wall closure.

**Argument:** The Round 2 amendment adequately answers the off-manifold objection conditionally: G2a and G2b make failure of intervention validation an explicit rung-0 outcome, and the amended positive still addresses the original question rather than substituting the kernel-pair question. The strongest remaining defect is upstream of LEACE. The card's deterministic recipe—3–10 mm air components, complete walls, adjacency, stacking, pleural distance, and Betti/Euler summaries—has no inspected reference establishing semantic specificity on CT-RATE's native images or final tensors. Requiring no airway connection does not exclude traction bronchiolectasis when distal airway segmentation fails in fibrotic lung, and complete-wall or multilayer criteria do not exclude juxtaposed paraseptal emphysema when trilinear resampling creates or closes thin walls. Native-to-tensor repeatability only shows that the same measurement survives preprocessing; it cannot show that the measurement denotes honeycombing. Likewise, report-text honeycomb mentions are suitable for prevalence gating but, under the charter, cannot validate the primary X because they are reader-derived and their annotation conditions are not an independent measurement method. Therefore even if the latent intervention passes G2a/G2b, the identified claim is only that CT-CLIP uses information aligned with the bespoke subpleural-airspace topology index. Calling that index “honeycombing” makes an unsupported rung-3 semantic leap. This does not die exactly like the prior annotation-provenance candidates—the primary analysis does not require their labels—but it inherits their lesson if report mentions are quietly used to confer construct validity. A third structural amendment is unnecessary: the study can remain sound at rung 1 with the X named literally as the computed topology index; the physician-level honeycombing sentence must remain out of scope until independent construct validation exists. The identity check therefore creates a real boundary: renaming X to a topology index narrows the original honeycombing claim, while retaining “honeycombing” without validation overclaims it.

**What would change my mind:** Directly inspect and run an obtainable, citable honeycombing quantifier with released weights that has external validation against the named mimics, then show prespecified agreement and failure-analysis results with the proposed topology measure on CT-RATE native and final tensors; alternatively, establish construct validity in an independent dataset with an existing adjudicated honeycombing reference and demonstrate transport of the frozen measurement thresholds to CT-RATE. Repeatability, report-term enrichment, or association with the fibrotic-sequela score alone would not suffice.

**Status:** OPEN

## Round 3 — PROPOSER

**Responding to:** Even with G2a/G2b passed, the study identifies use of
information aligned with the bespoke subpleural-airspace topology index — not
use of honeycombing. The index has no inspected reference establishing that it
separates honeycombing from paraseptal emphysema, traction bronchiolectasis,
and reconstruction-created wall closure on CT-RATE's native images or final
tensors; airway-exclusion fails exactly where distal airway segmentation fails,
and resampling can create or close the walls the criteria depend on.
Native-to-tensor repeatability shows survival, not denotation; report-text
mentions may gate prevalence but can never confer construct validity, because
they are reader-derived. Naming the index "honeycombing" is therefore an
unearned rung-3 semantic leap. No third structural amendment is needed: the
study is sound at rung 1 with X named literally, and the physician-level
honeycombing sentence stays out of scope until independent construct
validation exists.

**Response:** CONCEDE

**Argument:** The objection is correct, and I adopt the critic's own remedy —
which, as the critic says, is scope discipline rather than a structural
amendment. Every element of the design survives unchanged (K1 prevalence gate,
LEACE-family erasure, gates G2a/G2b, the nuisance battery, the automatic
demotion branch, the exploratory kernel-pair arm). What does not survive is
the name attached to a gated positive, and I concede each step of the
argument that removes it:

- **Repeatability is not denotation.** The Stage 0 native-to-tensor audit was
  the card's answer to the preservation keystone, and it answers only
  preservation: the same number computed twice. Nothing in the design ever
  checks what the number *means* against an independent reference, and I have
  no such reference to offer inside CT-RATE. The keystone screen's
  `UNVERIFIABLE` verdict already contained this — mimic separability was named
  as the unverifiable half — and the critic is right that no amount of latent
  gating downstream repairs a reference problem upstream.
- **The failure modes are concrete, not hypothetical.** Distal airway
  segmentation failing precisely in fibrotic lung (so "no airway connection"
  silently admits traction bronchiolectasis) and trilinear resampling to
  1.5 mm creating or closing ~1 mm walls (so "complete walls" tracks
  reconstruction as much as anatomy) are the two specific mechanisms by which
  the index becomes a mixture. Both were flagged in critique; neither has an
  in-design answer. At rung 1 that mixture is tolerable only because the claim
  is literally about the index, contamination included — which is exactly why
  the honeycombing name must come off the confirmatory claim.
- **Report mentions never validate X.** Full agreement, restated as a hard
  boundary: honeycomb-mention regexes gate prevalence (K1) and stratify, and
  appear nowhere in any construct-validity argument. This is the
  annotation-provenance lesson applied prospectively rather than learned
  retrospectively — the five prior kills happened because reader-derived
  language was load-bearing; here it is confined to feasibility gating.

**What this changes in the card (scope accounting, for the revision):**

1. **The confirmatory claim is restated at index level.** A fully gated
   positive supports: "CT-CLIP's pulmonary-fibrotic-sequela score uses
   information carried by the prespecified subpleural cyst-network topology
   index, as linearly encoded in its representation, beyond scar-burden,
   density, and emphysema nuisance directions." X is the index, named
   literally. It remains charter-compliant as an X — a deterministic, citable
   formula computable today on an unseen scan without asking anyone — but it
   is not yet a word a physician already has.
2. **Rung accounting.** `rung.target` within obtainable data drops 3 → 1.
   The honeycombing deliverable sentence is retained as the rung-3 *target*,
   explicitly out of scope for this study, per the charter's provision that a
   candidate may stop below rung 3 if it says so and names the move-up.
   `rung.move_up` is rewritten to the critic's disjunction verbatim: (a) an
   obtainable, citable honeycombing quantifier with released weights and
   external validation against the named mimics, run on CT-RATE native and
   final tensors with prespecified agreement and failure analysis against the
   index; or (b) construct validation in an independent dataset with an
   adjudicated honeycombing reference, plus transport of the frozen
   measurement thresholds to CT-RATE. Revision adds a bounded Stage 0c
   search for candidate (a) — the critique already named the AJRCCM 2024
   deep-learning honeycombing quantifier (DOI 10.1164/rccm.202311-2185OC) as
   a lead with released-weights status unverified; absence of a finding is
   recorded as absence, not as impossibility.
3. **Identity check, answered honestly.** The critic is right that this is a
   real boundary, and here is where I place the card relative to it: the
   original one-sentence question — does CT-CLIP use connected multilayer
   subpleural cyst topology — is still what the study asks, via the same
   measurement the card always specified; the deliverable sentence and
   prohibited conclusions are unchanged as targets. What changed is which
   rung the obtainable evidence can certify: the study now certifies "the
   model uses the topology index" (rung 1) and explicitly declines to certify
   "the index is honeycombing" (rung 3) until the named validation exists.
   That is rung honesty within the same claim, not a new deliverable
   sentence, so this remains revision-in-place under the 2026-08-10 rule. If
   the human reviewer reads the boundary the other way — that demoting the
   headline from result to target changes the claim's identity — the correct
   disposition is supersession with this design as the successor, and I flag
   that as the reviewer's call, not mine to preempt.
4. **`dies_like_prior` rewritten again.** The card inherits the
   annotation-provenance lesson in a precise form: the *name* honeycombing is
   unavailable without an independent reference standard, and no reader-derived
   surrogate may stand in for one. It does not die that way, because the
   primary analysis needs no reader labels — but the rung-3 sentence was
   priced as if the name came free, and it does not.
5. **What is lost, plainly.** The physician-legible headline — the entire
   point of the program's deliverable — is demoted from result to target.
   `interest` 5 → 4 and `regret` 5 → 4: a model shown to use a prespecified
   cyst-network topology index is still a physician-adjacent mechanism
   sentence, but it is one translation step short of the charter's deliverable,
   and that step is now owned by a validation module this study does not
   contain. `medical_relevance` stays 3 (already deflated in amendment one).
   The priority arithmetic must be recomputed in revision with these values
   and rung target 1.

**Status:** CONVERGED — the design stands as amended in rounds 1–2; the
confirmatory claim is stated at the level of the computed topology index; the
honeycombing sentence is out of scope until the critic's construct-validation
condition is met, and that condition is recorded verbatim as the rung-3
move-up. Three rounds produced two amendments and one concession, each
narrowing the claim toward what the instruments can actually certify; the
surviving study is smaller than the card promised and, for exactly that
reason, defensible.


===== ideas/019/idea_card.json =====
{
  "id": "W2",
  "track": "wide",
  "status": "DEVELOPED",
  "outside_field": "algebraic topology and fracture mechanics",
  "question": "Is CT-CLIP's pulmonary-fibrosis score using the connected, multilayer subpleural cyst topology of honeycombing rather than generic peripheral high-frequency texture?",
  "title": "The fibrosis model may be counting holes at the pleural edge",
  "deliverable_sentence": "CT-CLIP is using honeycombing\u2014the connected multilayer subpleural cyst network of end-stage fibrotic lung\u2014rather than generic coarse lung texture.",
  "rung": {
    "current": 0,
    "target": 3,
    "move_up": "Automated topology association is exploratory; selective topology-direction erasure with emphysema, reticulation, density, and kernel controls reaches rung 1; reconstruction and external-site replication gate rung 2; the named honeycombing claim then reaches rung 3."
  },
  "X_measurement": {
    "X": "Subpleural honeycomb topology: count and volume of 3-10 mm air components with complete walls, adjacency/stacking depth, distance to pleura, and persistent Betti-1/Euler-characteristic summaries across HU and wall-thickness thresholds.",
    "how": "Segment lungs, define a 15-mm subpleural shell, identify wall-bounded air components across prespecified HU thresholds, remove components connected to the airway tree, and compute connected components, loops, stacking depth, and persistence. These are deterministic voxel/graph measurements; no reader label defines X.",
    "could_compute_today_without_asking_anyone": "Yes as a well-defined formula using a lung mask and connected-component/persistent-homology operations, although its agreement with true honeycombing on routine thick-slice CT is uninspected."
  },
  "borrowed_construct": {
    "field": "algebraic topology and fracture mechanics",
    "construct": "End-stage remodeling creates a connected cellular void network at a stressed boundary; topology distinguishes that network from isolated low-density holes.",
    "measurement_implied": "Persistent component/loop counts, wall completeness, adjacency, and multilayer depth in the subpleural shell.",
    "if_analogy_dropped": "The study would use generic radiomics. The transplant forces threshold-persistent topology and a direct dissociation from isolated paraseptal emphysema."
  },
  "use_vs_association": "Use requires that erasing a validation-learned honeycomb-topology direction selectively lowers the frozen fibrosis score beyond erasing matched density, reticulation, emphysema, kernel, and random directions; score-topology correlation alone is not evidence of use.",
  "keystone_prerequisite": "Routine CT-RATE resolution and CT-CLIP preprocessing preserve enough wall completeness and cyst adjacency to distinguish honeycombing topology from paraseptal emphysema and traction bronchiolectasis without human labels.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_evidence": "Primary neighbors establish the adjacent facts: official Pulmonary Fibrosis Foundation recommendations define honeycomb cysts as contiguous subpleural cysts with complete walls and distinguish them from paraseptal emphysema (PMCID PMC7977697); topological ILD texture classification exists (arXiv:1005.5086); CT-CLIP/CT-RATE is arXiv:2403.17834. No native-to-final-tensor topology audit was inspected.",
  "keystone_residual_assumption": "If I have only verified the nearest checkable thing, what am I still assuming? A clinical definition and an old topology classifier do not show that CT-RATE slice thickness or CT-CLIP resampling preserves 3-10 mm cyst walls. Preservation, not formula availability, is the real keystone.",
  "dies_like_prior": "It resembles idea-008 only in the Sybil/fibrosis neighborhood, but uses a different frozen output and a positive named structure. It avoids idea-006's OOD deletion by internal direction erasure. It avoids CIRCULARITY because the model output is broad fibrosis while X is a dissociated morphologic component. DATA_INSUFFICIENT is an explicit prevalence/resolution gate.",
  "closest_prior_work": [
    {
      "citation": "Sluimer et al., Classification of Interstitial Lung Disease Patterns with Topological Texture Features",
      "identifier": "arXiv:1005.5086",
      "verified_fact": "Euler/topological texture features were used to classify ILD patterns, including honeycombing.",
      "delta": "It classified texture patches rather than testing reliance of a frozen report-supervised fibrosis model."
    },
    {
      "citation": "Lynch et al., Practical Imaging Interpretation in Patients Suspected of IPF",
      "identifier": "PMCID PMC7977697",
      "verified_fact": "It defines honeycomb cysts by subpleural contiguity, wall completeness, and frequent multilayering, and names emphysema as a mimic.",
      "delta": "It is a clinical definition, not an automated model-use experiment."
    },
    {
      "citation": "Hamada et al., Deep-Learning Reconstruction of HRCT Improves Interobserver Agreement for Pulmonary Fibrosis",
      "identifier": "DOI 10.1177/08465371241228468",
      "verified_fact": "Reconstruction method changes agreement for honeycombing assessment.",
      "delta": "It highlights the reconstruction threat but does not decode a fibrosis network."
    }
  ],
  "novelty_neighbors": [
    "arXiv:1005.5086",
    "PMCID PMC7977697",
    "DOI 10.1177/08465371241228468"
  ],
  "novelty_delta": "The proposed study asks whether a frozen volumetric foundation model relies on threshold-persistent honeycomb topology, not whether topology can classify ILD patches or readers can see honeycombing.",
  "why_not_done": {
    "category": "BLIND_SPOT",
    "reason": "Fibrosis explainability usually maps saliency or predicts reader lexicon labels; topology provides an annotation-free morphologic instrument but has rarely been used as the readout language for a foundation model."
  },
  "smallest_decisive_experiment": "Stage 0 on 120 validation scans spanning slice thickness/kernel strata: test native-to-model-tensor stability and separability from automated emphysema, airway connectivity, lung density, and reticulation proxies. Freeze all directions. On 250 test scans erase topology and nuisance directions separately/jointly; require a fibrosis-score effect specific to topology and stable across thin-slice reconstruction strata.",
  "compute_envelope": "One Colab Pro+ session: frozen CT-CLIP inference on at most 370 volumes; CPU connected components and cubical persistence on downsampled subpleural shells; linear probes only.",
  "standing_confounds_addressed": {
    "scanner_vendor_protocol_reconstruction": "Thin-slice confirmatory stratum, explicit kernel/slice-thickness directions, and reconstruction-pair repeatability; failure to preserve topology kills the study.",
    "site": "Single/institution-concentrated CT-RATE cannot eliminate site; external ILD replication is needed for rung 2.",
    "positioning": "Subpleural coordinates are anatomy-relative; dependent atelectasis is measured and prone scans handled separately.",
    "body_habitus": "Noise and dose proxies enter nuisance directions.",
    "disease_prevalence_referral": "Clinical referral enriches ILD and emphysema; spectrum is reported and external screening replication is required.",
    "label_leakage": "Reports do not define X or the primary self-change readout; visible text is excluded."
  },
  "alternative_explanations": [
    {
      "alternative": "The topology measure is paraseptal emphysema.",
      "resolution": "Require complete walls, multilayer adjacency, no airway connection, and separate emphysema-direction erasure."
    },
    {
      "alternative": "The model uses generic reticulation or density.",
      "resolution": "Erase density and high-frequency reticulation directions separately and require an incremental topology effect."
    },
    {
      "alternative": "Reconstruction creates or removes apparent cyst walls.",
      "resolution": "Native/tensor and paired-reconstruction stability are keystone gates, not post hoc covariates."
    }
  ],
  "anticipated_negative": {
    "classification": "decisive",
    "reason": "If topology is reliably encoded and separable, yet its erasure has an equivalently null effect while reticulation erasure changes the fibrosis score, the honeycombing-use hypothesis is directly weakened."
  },
  "scores": {
    "clarity": {
      "value": 5,
      "why": "The claim names honeycombing and the competing generic textures."
    },
    "identifiability": {
      "value": 4,
      "why": "Topology, emphysema, reticulation, density, and reconstruction are explicitly dissociated; erasure specificity is still imperfect."
    },
    "medical_relevance": {
      "value": 5,
      "why": "Honeycombing changes UIP interpretation and prognosis, and confusion with emphysema is clinically consequential."
    },
    "interest": {
      "value": 5,
      "why": "A model effectively counting connected subpleural holes is a surprising physician-legible mechanism."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Definitions, topology precedent, model, and public data family exist."
    },
    "feasibility": {
      "value": 3,
      "why": "Capped; routine-CT and final-tensor topology preservation is uninspected."
    },
    "data_readiness": {
      "value": 3,
      "why": "CT-RATE is obtainable but gated; thin-slice positive support is unknown."
    },
    "evaluation_readiness": {
      "value": 4,
      "why": "Persistent features and nuisance dissociations are prespecifiable, though validation floors are custom."
    },
    "negative_result_value": {
      "value": 5,
      "why": "After encoding gates, a topology-null/reticulation-positive result is decisive."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Capped; no direct foundation-model reliance study was found in a bounded search."
    },
    "regret": {
      "value": 5,
      "why": "The relevant topology is cheap to compute and could explain an important model output."
    }
  },
  "priority_score": 4.3,
  "priority_arithmetic": "0.20*3 + 0.15*4 + 0.15*5 + 0.10*4 + 0.10*5 + 0.10*5 + 0.10*5 + 0.05*3 + 0.05*3 = 4.30",
  "unverified_claims": [
    "CT-CLIP exposes a stable pulmonary-fibrosis score in the obtainable checkpoint",
    "CT-RATE has enough thin-slice honeycombing",
    "The proposed topology distinguishes honeycombing from emphysema without annotations",
    "Topology is linearly and selectively erasable"
  ]
}


===== ideas/019/keystone_screen.md =====
# Keystone screen

## Keystone as stated

> Routine CT-RATE resolution and CT-CLIP preprocessing preserve enough wall completeness and cyst adjacency to distinguish honeycombing topology from paraseptal emphysema and traction bronchiolectasis without human labels.

This is the load-bearing fact. It is not enough that CT-RATE contains chest CT, that metadata include voxel spacing, or that honeycombing has a clinical definition. The proposed measurement must remain separable from its two named mimics after the exact released preprocessing.

## What I inspected

I inspected the official CT-CLIP repository at commit `a2a155c601987820433c01db69b64d701d3d229d`, specifically the training loader and the training configuration.

The loader reads per-volume spacing and fixes the model-space resolution:

> `xy_spacing = float(row["XYSpacing"].iloc[0][1:][:-2].split(",")[0])`  
> `z_spacing = float(row["ZSpacing"].iloc[0])`

and then:

> `target_x_spacing = 0.75`  
> `target_y_spacing = 0.75`  
> `target_z_spacing = 1.5`

Source: [official CT-CLIP `scripts/data.py`, lines 96–109, commit `a2a155c`](https://github.com/ibrahimethemhamamci/CT-CLIP/blob/a2a155c601987820433c01db69b64d701d3d229d/scripts/data.py#L96-L109).

Resampling is trilinear:

> `resized_array = F.interpolate(array, size=new_shape, mode='trilinear', align_corners=False).cpu().numpy()`

Source: [official CT-CLIP `scripts/data.py`, lines 27–34, commit `a2a155c`](https://github.com/ibrahimethemhamamci/CT-CLIP/blob/a2a155c601987820433c01db69b64d701d3d229d/scripts/data.py#L27-L34).

The resampled tensor is forced to a fixed field of view:

> `target_shape = (480,480,240)`

followed by center cropping and constant-value padding:

> `tensor = tensor[h_start:h_end, w_start:w_end, d_start:d_end]`  
> `tensor = torch.nn.functional.pad(tensor, (pad_d_before, pad_d_after, pad_w_before, pad_w_after, pad_h_before, pad_h_after), value=-1)`

Source: [official CT-CLIP `scripts/data.py`, lines 128–156, commit `a2a155c`](https://github.com/ibrahimethemhamamci/CT-CLIP/blob/a2a155c601987820433c01db69b64d701d3d229d/scripts/data.py#L128-L156).

Finally, the released training configuration uses relatively coarse encoder patches:

> `image_size = 480,`  
> `patch_size = 20,`  
> `temporal_patch_size = 10,`

Source: [official CT-CLIP `scripts/run_train.py`, lines 17–26, commit `a2a155c`](https://github.com/ibrahimethemhamamci/CT-CLIP/blob/a2a155c601987820433c01db69b64d701d3d229d/scripts/run_train.py#L17-L26).

Thus the input tensor has nominal 0.75 × 0.75 × 1.5 mm sampling, while one first-stage token spans 15 × 15 × 15 mm. The latter does **not** by itself prove destruction of smaller structures: the learned linear patch embedding receives the constituent voxel values. Conversely, neither the loader nor the architecture demonstrates preservation of complete cyst walls, multilayer adjacency, or separability from paraseptal emphysema and traction bronchiolectasis.

I also inspected the official CT-RATE release page. It says access to the image files requires acceptance of the dataset terms:

> “This repository is publicly accessible, but you have to accept the conditions to access its files and content.”

Source: [official CT-RATE repository, gated-dataset notice](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE/tree/main).

No representative native volumes, corresponding final tensors, or topology/mimic separability results were available in the repository checkout. Therefore the actual preservation claim could not be directly tested in this screen.

## Residual-assumption check

**If this card only verified the nearest checkable thing, what is it still assuming?**

The nearest checkable facts are that physical-spacing metadata are read, volumes are resampled to a fixed nominal spacing, and the encoder consumes fixed-size patches. The card is still assuming that these operations preserve the wall closure and adjacency needed by its deterministic topology measure **and** that the resulting measure distinguishes honeycombing from the two named mimics on CT-RATE. That assumption is load-bearing and is the same as the stated keystone, not a different hidden keystone.

The quoted source code neither verifies nor falsifies that assumption. Verification requires the proposed native-to-final-tensor audit on actual CT-RATE cases, with an annotation-independent or otherwise defensible reference for mimic separability. Accordingly, the honest screen result is `UNVERIFIABLE`, not `PASS` and not `KILL`.

```json
{"verdict": "UNVERIFIABLE", "evidence": "resized_array = F.interpolate(array, size=new_shape, mode='trilinear', align_corners=False).cpu().numpy()", "source": "https://github.com/ibrahimethemhamamci/CT-CLIP/blob/a2a155c601987820433c01db69b64d701d3d229d/scripts/data.py#L27-L34", "note": "The exact preprocessing is inspected, but only an audit on actual native and final tensors can establish preservation and mimic separability."}
```


===== STAGE TASK =====
Revise the idea in response to `critique.md`. Narrow it to one clean question. Remove unnecessary architecture. Preserve a meaningful negative outcome. Update `idea_card.json` and write `revision.md` describing every material change. Do not write code.

## Claim retention (required)

End `revision.md` with one fenced json block classifying the revised
deliverable against the ORIGINAL deliverable sentence (ledger field
`deliverable_original`):

```json
{"claim_retention": "same|narrowed|different"}
```

`different` should be rare: under the claim-identity rule it normally
means supersede-and-re-register, not revise.

