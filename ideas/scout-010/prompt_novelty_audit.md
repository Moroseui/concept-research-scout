You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-010
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


## 2026-08-11 — Idea 004 Stage 0: feasibility memo accepted with four contract pins

GO per feasibility.md, with the probe contract required to encode: (1) primary
readout is per-head (18) x per-stratum paired-difference distributions; no
cross-head averaging; the 4-pair Br40f|Br44f stratum is exploratory only.
(2) Two-tier readout: tier 1 label-free per-head deltas (the floor, primary,
no margin needed); tier 2 label-dependent AUROC shift judged against the
CT-Scroll between-method spread, margin fixed from the PDF tables BEFORE any
paired score is seen. (3) Probes are phased: contract v1 is exactly the
section-9 load probe (gate, checkpoint hash, 18-output load, one-pair
inference, bit-determinism); the bulk 425-pair floor study is a separate
later contract requiring fresh human approval. (4) Freeze HF commit hash and
checkpoint SHA-256 at download time; attribution limited to 'released v2
ClassFine checkpoint' until paper-number correspondence is checked.



===== evidence/ledger_digest.md =====
# Ledger digest (auto-generated -- do not edit; run `python scout.py ledger digest`)

56 tracked ideas. Latest state per idea; full history in ledger.jsonl.

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
- ... and 14 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- conditional-observational: 4
- counterfactual-synthesis: 3
- representation-erasure: 3
- regional-substitution: 3
- natural-paired: 2
- longitudinal-within-subject: 2
- model-output-perturbation: 2

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
- **scout-010-c01** [SCOUT_ONLY/SCOUTED/baseline] -- CXR-Age put back together from parts a radiologist can measure -- data: ChestX-ray8 (primary), PadChest (replication); CheXmask for both.
- **scout-010-c02** [SCOUT_ONLY/SCOUTED/baseline] -- Atelectasis vs consolidation: has CT-CLIP learned the radiologist's volume-loss rule? -- data: CT-RATE (validation split; established access and local pipeline).
- **scout-010-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin's cirrhosis signal may be the spleen -- data: Public abdominal CT (AMOS 2022, TotalSegmentator public dataset); Merlin checkpoint from HF.
- **scout-010-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The inferior vena cava as a manometer: does the chest model read venous pressure? -- data: CT-RATE (repeat-session subset; second and final CT-RATE candidate this cycle).
- **scout-010-c05** [SCOUT_ONLY/SCOUTED/baseline] -- Aortic tortuosity as a buckled column: is the hypertension head reading exceeded critical pressure? -- data: Public abdominal CT with age metadata (candidate cohorts: AMOS 2022, TotalSegmentator public dataset - metadata adequacy is Stage 0); Merlin checkpoint from HF. Second and final Merlin/public-abdominal candidate this cycle.


===== evidence/portfolio_brief.md =====
# Portfolio brief (auto-generated; run `python scout.py brief`)

Actionable ideas with debate verdicts. A revival/recombination
candidate MUST cite the specific condition below that has changed.

## idea-019 [SHORTLISTED] -- Does CT-CLIP use a subpleural cyst-network topology index?

**Verdict:** **REVISE.** The debate produced a coherent conditional rung-1 feasibility/use study, but the existing card is materially stale and the program's required physician-legible endpoint remains outside the evidence. Before deciding whether revision-in-place is permissible, the human should look most closely at the claim-identity boundary: whether replacing “the model uses honeycombing” with “the model uses a prespecified subpleural cyst-network topology index” is rung honesty within the same candidate or a new deliverable sentence that must be registered as a successor. ```json {"verdict": "REVISE", "unblock": "Human resolves the claim-identity boundary, then the card is rewritten to the agreed index-level, K1-gated, G2a/G2b-conditional rung-1 design (or registered as a successor if the deliverable sentence is judged changed)."} ```

**Unresolved:** Does narrowing the confirmatory sentence to a topology index preserve the candidate's identity?; Can the topology index be validated as honeycombing and thereby reach rung 3?; Will CT-RATE contain enough suitable cases for the proposed study?; Can the latent intervention pass the agreed validity gates?

## idea-017 [SHORTLISTED] -- Can Sybil's tracheal-deformity question be identified in NLST?

**Verdict:** **REVISE.** Rewrite `idea_card.json` to implement the converged Stage 0-only design before any feasibility memo or probe contract. The single most important thing for the human to inspect is whether the joint-support gate can be given a prespecified, adequately powered minimum-support criterion: if continuous tracheal index cannot be separated from sex, emphysema, lung volume, and reconstruction in a recoverable held-out cohort, idea 017 dies like idea 009 regardless of the attractiveness of its mechanism. ```json {"verdict":"REVISE","unblock":"Rewrite the idea card as a four-gate Stage 0-only study with no erasure or use claim, then prespecify and inspect adequate independent tracheal-index support in a recoverable Sybil-held-out or external cohort."} ```

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



===== evidence/librarian_proposals.md =====


===== ideas/scout-010/README.md =====
# Scouting cycle 010

Tracks: baseline


===== ideas/scout-010/candidates_all.json =====
{
  "cycle": 10,
  "tracks": [
    "baseline"
  ],
  "notes": {
    "mode_c_score_missing": 2
  },
  "candidates": [
    {
      "id": "scout-010-c01",
      "search_mode": "A",
      "entry_point": 1,
      "title": "CXR-Age put back together from parts a radiologist can measure",
      "question": "Is CXR-Age's biological-age output assembled from automatically measurable chest-film geometry - cardiothoracic ratio and projected lung area - or does the mortality signal live in a residual those measurements miss?",
      "rung": "Targets rung 1 (CXR-Age uses thoracic geometry) with an explicit path to rung 3, because X is already a named clinical quantity (cardiothoracic ratio). Moves up to a use-claim via the prespecified dissociation-strata arm and, conditional on a training-distribution check, a PA/AP projection natural experiment.",
      "deliverable_sentence": "CXR-Age is using the cardiothoracic ratio and projected lung area - the measurable geometry of the chest film - as principal drivers of its biological-age output.",
      "X_measurement": "CTR = maximal horizontal cardiac width / maximal inner thoracic width, and projected lung area, both computed from CheXmask heart and lung masks (HybridGNet; PhysioNet 'chexmask-cxr-segmentation-data', open access, CC BY 4.0, precomputed for ChestX-ray8, CheXpert, MIMIC-CXR-JPG, PadChest, VinDr-CXR; masks for 'Left Lung', 'Right Lung', 'Heart' - quoted from the PhysioNet page, fetched 2026-08-12). Could I compute X on a new film today without asking anyone? Yes - masks are precomputed for the public datasets, and HybridGNet code is public for new images.",
      "suspected_signal": "Aging remodels chest geometry in ways visible on a frontal film: LV remodeling and aortic unfolding raise CTR; hyperinflation and kyphosis change projected lung area; both carry independent mortality risk. The hypothesis is that CXR-Age's phenotypic-age head largely re-derives this geometry rather than a texture-level signal.",
      "keystone_prerequisite": "The inference needs: the released checkpoint IS the published CXR-Age model, runs with documented preprocessing, and produces the published output semantics (a number in years reflecting mortality risk). If the checkpoint is not faithful or not runnable, every downstream decomposition is uninterpretable.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "github.com/circ-ml/CXR-Age README (fetched 2026-08-12): 'Weights for the CXR-Age model are in development/models/PLCO_Fine_Tuned_120419.pth' and 'CXR-Age outputs a number (in years) reflecting all-cause mortality risk based on only a single chest radiograph image.' MIT license, 'not for clinical care or commercial use'.",
      "keystone_residual_assumption": "Having verified the weights exist with documented output semantics, I am still assuming the checkpoint reproduces published behavior (e.g., high correlation with chronological age in healthy subsets) and that repo preprocessing is complete enough to run it unambiguously. This is load-bearing and is therefore Stage 0 gate #1: run the checkpoint on a public dataset with age metadata (ChestX-ray8 has ages) and require the published-magnitude age correlation before any decomposition is interpreted. Second residual: CheXmask mask quality bounds the attainable R-squared - a measurement-noise ceiling must be estimated (mask test-retest across near-duplicate films) and prespecified before the decomposition is read.",
      "rung_reached": "Rung 1 if the variance decomposition plus dissociation strata show CXR-Age tracking geometry within chronological-age-and-sex-matched strata. Moves to rung 2/3 because X is artifact-checkable (geometry is measured, not annotated) and already physician-named; the main rung-2 residual is inspiration depth, which is partially self-controlling (deep inspiration lowers CTR but raises lung area, so the two X's dissociate under it).",
      "dies_like_prior": "Closest prior failure is USE_VS_ASSOCIATION (cycle-one kills): a decomposition is an association. Difference: the design prespecifies dissociation strata (films matched on chronological age, sex, and view where CTR differs materially) so the claim is conditional tracking, not raw correlation; and the quasi-interventional PA/AP arm is available but explicitly gated on verifying AP views are in CXR-Age's training distribution - stated up front to avoid the idea-006 OOD-intervention trap rather than discovering it in critique. No annotation-provenance exposure: no human label enters the primary readout.",
      "closest_prior_work": "qCXR-bioage (Radiology: Cardiothoracic Imaging, DOI 10.1148/ryct.250327): builds its OWN explainable biological age from automated CXR quantifications (lung area, emphysema probability, aortic diameter, heart area, bone density) and shows it predicts mortality. It does NOT decode the existing CXR-Age checkpoint - it shows the vocabulary suffices, not that Lu/Raghu's model uses it. Raghu et al., CXR-Age, JACC Cardiovasc Imaging 2021 (DOI 10.1016/j.jcmg.2021.01.008, unverified-from-memory): built the model, published saliency only. Project Baseline preprint (medrxiv 2025.01.02.24319734): CXR-Age vs epigenetic clocks, associations only. The exact delta: nobody has published a variance decomposition + dissociation analysis of the released CXR-Age checkpoint against automatically measured film geometry.",
      "existing_assets": "CXR-Age weights (MIT, path verified); CheXmask precomputed masks for the exact public datasets (CC BY 4.0, verified open); ChestX-ray8 and PadChest fully public with age/sex/view metadata; qCXR-bioage as the published biomarker vocabulary to decompose against.",
      "smallest_decisive_experiment": "Run the checkpoint on ~10k ChestX-ray8 films with CheXmask masks. Gate 1: reproduce published age correlation. Then: (a) R-squared of CXR-Age on {CTR, lung area, chronological age, sex}; (b) within strata matched on chronological age/sex/view, test whether CXR-Age monotonically tracks CTR. Decision: if conditional tracking is strong and R-squared approaches the mask-noise ceiling, the deliverable sentence stands at rung 1; if R-squared is low with tracking absent, the geometry hypothesis is dead and the residual (texture/bone) becomes the finding.",
      "standing_confounds_addressed": "Scanner/site/protocol: analysis is within-dataset and within-view; site enters only if geometry measurement itself is site-biased (masks are geometric, not intensity-based - low risk). Positioning/inspiration: named residual; partially separable because inspiration moves CTR and lung area in opposite directions. Habitus: a real correlate of both geometry and mortality - the claim is about what the model uses, so habitus driving geometry does not confound rung 1, only the rung-3 gloss. Label leakage/prevalence/referral: no labels in the primary readout. NOT ruled out: inspiration depth as a shared cause of score and CTR within strata.",
      "alternative_explanations": "(1) CXR-Age uses fine texture (bone density, vascular markings) that merely correlates with geometry - addressed by the dissociation strata and by reporting the residual's mortality-relevant correlates; (2) mask errors correlate with disease severity, inflating apparent tracking - addressed by the prespecified noise ceiling and QC subset; (3) the appeal of this candidate is partly that it sounds like a tidy accounting exercise - the honest risk is a mushy middle result (R-squared ~ 0.4) that neither confirms nor kills; the margin structure below is designed for exactly that.",
      "anticipated_negative": "Sensitivity-limited unless the mask-noise ceiling is estimated first; with the ceiling prespecified, a low conditional R-squared with an equivalence margin is decisive AGAINST geometry-as-principal-driver and is itself publishable (the mortality signal is not the geometry radiologists would first name).",
      "cross_domain": null,
      "remaining_legwork": "Download weights + verify runnable (half a day); pull CheXmask + join to ChestX-ray8 metadata (half a day); noise-ceiling estimation (1 day); decomposition + strata (1-2 days). First decision in under a week on Colab-class compute.",
      "design_template": "conditional-observational",
      "use_vs_association": "Distinguishes use from correlation by (a) conditioning on chronological age/sex/view so geometry cannot ride on demographics, (b) dissociation strata where CTR and lung area decouple, and (c) a gated PA/AP projection arm in which apparent CTR changes while anatomy is fixed - a natural intervention on X, run only if AP is verified in-distribution.",
      "dataset": "ChestX-ray8 (primary), PadChest (replication); CheXmask for both.",
      "scores": {
        "clarity": {
          "value": 4,
          "reason": "One-sentence question with a named X; loses a point because 'principal drivers' needs a prespecified threshold to be fully crisp."
        },
        "identifiability": {
          "value": 3,
          "reason": "Conditional tracking + dissociation strata rule out demographics and dataset mix; texture-correlated-with-geometry survives unless the PA/AP arm clears its distribution gate."
        },
        "medical_relevance": {
          "value": 4,
          "reason": "CXR-Age is proposed for mortality triage; whether it is CTR-plus-lung-area in a trench coat determines both trust and whether a transparent two-measurement surrogate suffices."
        },
        "interest": {
          "value": 4,
          "reason": "Either answer is compelling: a famous black-box clock reduced to two classroom measurements, or a demonstrated residual that geometry cannot explain."
        },
        "prior_legwork": {
          "value": 5,
          "reason": "Weights public, masks precomputed for the exact datasets, biomarker vocabulary published (qCXR-bioage); nothing needs annotation."
        },
        "feasibility": {
          "value": 4,
          "reason": "Keystone INSPECTED_TRUE lifts the cap; all assets verified open; days-scale on single-GPU."
        },
        "data_readiness": {
          "value": 5,
          "reason": "Everything is public and directly usable (CC BY 4.0 masks, public CXR sets, MIT weights)."
        },
        "evaluation_readiness": {
          "value": 4,
          "reason": "R-squared decomposition and matched-strata analysis are standard; the noise ceiling requires custom but well-defined work."
        },
        "negative_result_value": {
          "value": 3,
          "reason": "Sensitivity-limited without the noise ceiling; decisive with it - scored at the honest midpoint since the ceiling is planned but not yet estimated."
        },
        "novelty_confidence": {
          "value": 3,
          "reason": "qCXR-bioage is adjacent and recent; the decode-the-existing-checkpoint delta is real but the space is active - capped by my own uncertainty, not the rule."
        },
        "regret": {
          "value": 4,
          "reason": "If someone else publishes the CXR-Age decomposition with these exact public assets, it will look obvious in hindsight."
        }
      },
      "priority_score": 3.85,
      "unverified_claims": [
        "Raghu et al. CXR-Age DOI (10.1016/j.jcmg.2021.01.008) and Lu et al. CXR-risk DOI cited from memory - verify before the idea card.",
        "That ChestX-ray8 metadata age fields are reliable enough for the Stage 0 faithfulness gate (known to contain some noise).",
        "That CXR-Age pretraining included AP views (determines whether the PA/AP arm is in-distribution).",
        "qCXR-bioage seen via search result and abstract only; full methods not read."
      ],
      "track": "baseline"
    },
    {
      "id": "scout-010-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "Atelectasis vs consolidation: has CT-CLIP learned the radiologist's volume-loss rule?",
      "question": "When CT-CLIP scores atelectasis above consolidation on the same scan, is it using measured lobar volume loss to make that separation?",
      "rung": "Targets rung 1 (the model uses lobar volume loss for the atelectasis/consolidation contrast). Moves toward rung 3 cheaply because X is the textbook criterion radiologists themselves use - if rung 1 and the rung 2 checks hold, the deliverable sentence is immediate.",
      "deliverable_sentence": "CT-CLIP is using lobar volume loss to separate atelectasis from consolidation.",
      "X_measurement": "Lobar volumes from TotalSegmentator lung-lobe classes ('lung_upper_lobe_left', 'lung_lower_lobe_left', 'lung_upper_lobe_right', 'lung_middle_lobe_right', 'lung_lower_lobe_right' - verbatim from totalsegmentator/map_to_binary.py, fetched 2026-08-12). Volume-loss index: affected-lobe fractional volume relative to the scan's remaining lobes, plus fissure-shift proxy (lobe centroid displacement). Competing signal measured in the same pass: opacity burden = volume of intra-lobar voxels above -300 HU. Computable today on any chest CT without asking anyone: yes; the closest published validation is nnU-Net-based lobar volumetry of postoperative atelectasis (npj Digital Medicine, nature.com/articles/s41746-026-02683-6).",
      "suspected_signal": "The physiologic distinction itself: atelectasis is collapse (volume loss, fissure displacement, crowding), consolidation is alveolar filling with volume preserved. A report-supervised model could learn either the real volumetric criterion or a co-occurrence shortcut (tubes, effusions, basal location). The question is which.",
      "keystone_prerequisite": "The inference needs: the released CT-CLIP/ClassFine checkpoint exposes SEPARATE atelectasis and consolidation outputs whose within-scan contrast is non-degenerate (not near-duplicate scores).",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "ideas/004/log_probe_code.txt, EXPECTED_PATHOLOGIES ('The 18 head names in released order. Source: scripts/ct_lipro_inference.py in the official CT-CLIP repository (fetched 2026-08-11)') lists 'Atelectasis' and 'Consolidation' as distinct heads, alongside 'Pleural effusion' and 'Cardiomegaly'. The idea-004 probe contract already verified 18-output load and one-pair inference on this checkpoint (decisions.md 2026-08-11).",
      "keystone_residual_assumption": "Verified that two distinct heads exist; I am still assuming (a) their scores are not collapsed in practice (within-scan correlation must be checked and bounded at Stage 0 - if the heads are near-duplicates the contrast carries no information), and (b) TotalSegmentator lobar segmentation does not fail exactly where volume loss is largest - collapsed lobes are the known hard case for lobe tools, and this is the genuinely load-bearing assumption. Mitigation is prespecified: restrict primary analysis to mild-to-moderate volume loss with a fissure-completeness QC gate, and treat severe collapse as exploratory.",
      "rung_reached": "Rung 1 via the conditional contrast analysis. Rung 2 is unusually cheap here because the primary readout is within-scan (scanner, protocol, reconstruction, positioning, habitus all shared between the two head scores); the remaining rung-2 item is measurement validity of lobar volumetry in diseased lungs. Rung 3 is the same sentence as rung 1 since X is already the physician's own criterion.",
      "dies_like_prior": "Closest risk is USE_VS_ASSOCIATION. Difference: the readout is the within-scan two-head CONTRAST - every scan-level confound is differenced out by construction - and the main rival cue (opacity burden) is measured and conditioned on rather than left as an unnamed alternative. A representation-erasure upgrade (project the lobar-volume direction out of the shared embedding, watch the contrast collapse) is prespecified as phase 2 but not required for the screen. No annotation-provenance exposure: report-derived labels are used only for exploratory case enrichment, never in the primary readout.",
      "closest_prior_work": "Hamamci et al., CT-RATE/CT-CLIP (arXiv 2403.17834): built the model, reported per-label AUCs, never asked how any two labels are separated. npj Digital Medicine postoperative-atelectasis paper (s41746-026-02683-6): validates automated lobar volume-loss quantification as a measurement, does not connect it to any foundation model's decision. Draelos et al. RAD-ChestCT (DOI 10.1016/j.media.2020.101857, unverified-from-memory): multi-abnormality CT prediction, same silence on mechanism. Exact delta: nobody has tested whether a report-supervised chest-CT model's atelectasis/consolidation separation tracks the volumetric criterion that defines the distinction clinically.",
      "existing_assets": "Local, verified CT-CLIP inference pipeline from idea-004 (scripts, checkpoint hash procedure, bit-determinism check); CT-RATE validation-split inventory already characterized (3,039 volumes / 1,564 scans); TotalSegmentator public and verified to include lobe classes; published validation that lobar volumetry of atelectasis is measurable.",
      "smallest_decisive_experiment": "On ~300 CT-RATE validation scans enriched for report-labeled atelectasis and/or consolidation (enrichment only; labels not in the readout): compute per-scan head contrast (atelectasis minus consolidation logit), lobar volume-loss index, and opacity burden. Decision rule: partial association of contrast with volume-loss conditional on opacity burden, against a prespecified minimum effect. Positive = deliverable sentence at rung 1. Null with adequate power = the model does not use the radiologist's rule, which is a decisive and publishable negative for a deployed report-generation model.",
      "standing_confounds_addressed": "Scanner, vendor, protocol, reconstruction, site, positioning, habitus: all shared within scan, differenced out of the contrast. Prevalence/referral: affects the enrichment set's composition, not the within-scan readout; reported as scope limitation. Label leakage: no labels in the readout. NOT ruled out by design: cues that co-vary with volume loss inside the same scan (fissure shift, crowding - these are the volume-loss family and refine rather than refute X; air bronchograms - a consolidation-side cue that is genuinely distinct and is named as the open alternative).",
      "alternative_explanations": "(1) The model separates via air bronchograms or bronchial patency rather than volume - not excluded; named as the residual, and a bronchogram proxy (air-filled airway voxels inside opacity) can be added exploratorily; (2) heads are near-duplicates and the contrast is noise - Stage 0 gate; (3) TotalSegmentator errors correlate with collapse severity, manufacturing the association - handled by the QC gate and severity restriction.",
      "anticipated_negative": "Decisive: with the contrast design, adequate power, and a prespecified minimum effect, a null says the model's separation of these two labels does not use the criterion that defines them - a finding radiologists reading CT-CLIP-family reports would want to know.",
      "cross_domain": null,
      "remaining_legwork": "Volume download for the enriched subset (~300 scans, within established CT-RATE access); TotalSegmentator pass (GPU-days: ~1); head-correlation Stage 0 gate (hours, pipeline exists). First decision in roughly one week.",
      "design_template": "conditional-observational",
      "use_vs_association": "The within-scan two-head contrast differences out everything the scan shares; conditioning on measured opacity burden separates 'reads volume loss' from 'sees dense tissue'; the prespecified erasure arm upgrades the conditional association to a use claim if the screen is positive.",
      "dataset": "CT-RATE (validation split; established access and local pipeline).",
      "scores": {
        "clarity": {
          "value": 5,
          "reason": "One precise question, a named X that is the clinical definition itself, and a single prespecified decision rule."
        },
        "identifiability": {
          "value": 4,
          "reason": "Within-scan contrast is the strongest observational identification available; the air-bronchogram alternative and segmentation-error pathway keep it from 5."
        },
        "medical_relevance": {
          "value": 4,
          "reason": "Atelectasis-vs-consolidation drives different management (suction/bronchoscopy vs antibiotics); whether a deployed report generator makes the distinction for the right reason is directly consequential."
        },
        "interest": {
          "value": 4,
          "reason": "Either outcome informs the whole report-supervision paradigm: the model learned the physician's rule from text alone, or it fakes the distinction via co-occurrence."
        },
        "prior_legwork": {
          "value": 5,
          "reason": "The idea-004 pipeline, checkpoint verification, and dataset inventory already exist in this repo; the measurement tool is public and validated for this exact clinical problem."
        },
        "feasibility": {
          "value": 4,
          "reason": "Keystone INSPECTED_TRUE; the one real risk (lobe segmentation on collapse) has a prespecified mitigation and cheap Stage 0 check."
        },
        "data_readiness": {
          "value": 4,
          "reason": "CT-RATE is click-gated but program-established; volumes still need downloading."
        },
        "evaluation_readiness": {
          "value": 4,
          "reason": "Partial-association analysis with a minimum effect is standard; the fissure-QC gate needs definition."
        },
        "negative_result_value": {
          "value": 4,
          "reason": "Decisive under the powered contrast design; not 5 because the severe-collapse exclusion narrows the negative's scope."
        },
        "novelty_confidence": {
          "value": 3,
          "reason": "Limited search found measurement papers and model papers but not the connection; the space is active enough that 3 is the honest ceiling without a full audit."
        },
        "regret": {
          "value": 4,
          "reason": "The assets are sitting in this repo; if another group publishes it first with the same public pieces, that is a pure execution loss."
        }
      },
      "priority_score": 4.15,
      "unverified_claims": [
        "Draelos RAD-ChestCT DOI cited from memory.",
        "That atelectasis/consolidation label co-occurrence in CT-RATE leaves enough dissociated cases for enrichment (checkable from the released label CSVs before any download).",
        "That the two heads are not score-collapsed (Stage 0 gate).",
        "npj Digital Medicine atelectasis-volumetry paper seen via search snippet; full methods not read."
      ],
      "track": "baseline"
    },
    {
      "id": "scout-010-c03",
      "search_mode": "B",
      "entry_point": 2,
      "title": "Merlin's cirrhosis signal may be the spleen",
      "question": "Is Merlin's chronic-liver-disease score using splenic volume - congestive splenomegaly, the portal-pressure gauge - rather than the liver itself?",
      "rung": "Targets rung 1 (the model uses splenic volume in its liver-disease output). Rung 3 is close behind because splenomegaly is already the physician's word; rung 2 requires the non-hepatic-splenomegaly dissociation cases described below.",
      "deliverable_sentence": "Merlin is using splenic volume - congestive splenomegaly - in its chronic-liver-disease prediction.",
      "X_measurement": "Spleen volume from TotalSegmentator 'spleen' class (verbatim in map_to_binary.py, task 'total'; fetched 2026-08-12), in cm3. Competing liver-side signals measured in the same pass: liver volume, liver-to-spleen mean attenuation ratio, and liver-contour irregularity (surface-to-volume ratio of the TS liver mask as a nodularity proxy). Computable today on any abdominal CT without asking anyone: yes.",
      "suspected_signal": "Portal hypertension produces congestive splenomegaly; spleen volume is a validated correlate of cirrhosis severity and varices. A model trained with ICD-code supervision may have latched onto the spleen - a large, high-contrast, easily represented organ - rather than the subtler liver morphology a hepatologist would name.",
      "keystone_prerequisite": "The inference needs: a released Merlin output that produces a per-scan cirrhosis/chronic-liver-disease score on new abdominal CTs - either an exposed phecode-phenotype output or a zero-shot text-prompt score via the released image+text towers.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Supporting but not sufficient: huggingface.co/stanfordmimi/Merlin (fetched 2026-08-12) lists downloadable weights including 'i3_resnet_clinical_longformer_best_clip_04-02-2024_23-21-36_epoch_99.pt' (an image+text CLIP-style checkpoint), MIT license, with inference demos; the paper (arXiv 2406.06512) maps '16,553 ICD-9 and ICD-10 codes to 1,692 hierarchical phenotypes' via PheWAS Phecodes. NOT yet inspected: whether chronic liver disease is among the evaluable phenotypes with an exposed head, or whether zero-shot prompting is a documented usage mode producing calibrated-enough scores.",
      "keystone_residual_assumption": "Even after confirming a cirrhosis score exists, I am still assuming the score has enough dynamic range on public evaluation CTs (AMOS / TotalSegmentator-dataset populations are not hepatology cohorts; if almost no scan moves the score, the regression is uninformative). That prevalence-of-signal check is Stage 0 gate #2 and could be the real killer.",
      "rung_reached": "Rung 1 via conditional association plus dissociation cases. The rung-2 lever is specific and natural: splenomegaly WITHOUT liver disease (hematologic, thrombotic) versus cirrhotic-morphology liver WITHOUT splenomegaly - if the score follows the spleen in the first group, the model is using the spleen, not the liver.",
      "dies_like_prior": "Closest prior kill is DATA_ACCESS (idea-018, chewing muscle: required model/data not obtainable). Difference: Merlin weights are verified downloadable under MIT and evaluation CTs are public; the unverified piece is a single output-head question answerable in about an hour once weights are pulled, and it is declared as the keystone rather than assumed. USE_VS_ASSOCIATION is the second resemblance; the dissociation-case design is the stated answer.",
      "closest_prior_work": "Blankemeier et al., Merlin (arXiv 2406.06512): built and evaluated the model; no per-phenotype mechanism analysis. Backlog neighbors: scout-006-c03 (Merlin/diabetes/liver fat) and scout-008-c01 (cirrhosis model reading liver-edge bumpiness) - this candidate differs from both in X (spleen, not liver fat or liver edge) and in that it names the specific wrong-patient failure mode (non-hepatic splenomegaly) that makes the question clinically urgent. Spleen-volume-in-cirrhosis clinical literature is extensive (unverified specific citations; to be pinned in the idea card).",
      "existing_assets": "Merlin weights (MIT, HF, verified listed); TotalSegmentator (spleen class verified); AMOS 2022 and the public TotalSegmentator CT dataset (CC BY) as label-free evaluation cohorts; no annotation needed anywhere.",
      "smallest_decisive_experiment": "Run Merlin's liver-disease score and TotalSegmentator on ~500 public abdominal CTs. Decision: partial association of score with spleen volume conditional on liver volume, attenuation ratio, and contour irregularity - plus the dissociation read: in scans in the top spleen-volume decile with liver measures normal, does the score rise? Positive on both = deliverable at rung 1. Requires Stage 0 gates: (1) a usable cirrhosis output exists; (2) score dynamic range on public cohorts.",
      "standing_confounds_addressed": "Contrast phase: spleen VOLUME is phase-robust but the model's score may not be - analysis stratified by phase (phase classifiable from aortic/portal HU). Habitus: spleen scales with body size - normalize by an L3 body-cross-section from the same segmentation pass. Scanner/site: public multi-site cohorts, within-dataset analyses. Prevalence/referral: the readout is label-free, so cohort mix affects power, not validity. Label leakage: no labels used. NOT ruled out: liver texture the chosen liver measures miss (named as the open alternative - a positive spleen result does not exclude additional liver signal).",
      "alternative_explanations": "(1) Score tracks spleen only because spleen tracks unmeasured liver texture - partially addressed by the non-hepatic-splenomegaly dissociation cases, which break that path; (2) contrast-phase artifacts move both score and apparent organ boundaries - phase stratification; (3) low score dynamic range on healthy public cohorts makes everything null - Stage 0 gate, and the honest reason feasibility is capped.",
      "anticipated_negative": "Sensitivity-limited: a null needs a prespecified minimum detectable partial correlation and the dynamic-range gate passed; without those it is uninterpretable, and the card says so rather than promising a decisive negative it cannot deliver.",
      "cross_domain": null,
      "remaining_legwork": "Pull weights, answer the keystone (1 day); assemble public cohort + segmentation pass (2 days); association + dissociation analysis (2 days). First decision inside two weeks, with two explicit Stage 0 kill switches before any heavy compute.",
      "design_template": "conditional-observational",
      "use_vs_association": "Distinguishes use from correlation via natural wrong-cause cases: splenomegaly of non-hepatic origin. If the model's liver-disease score follows the spleen where the liver is normal, spleen size is being used, not merely correlated with liver disease.",
      "dataset": "Public abdominal CT (AMOS 2022, TotalSegmentator public dataset); Merlin checkpoint from HF.",
      "scores": {
        "clarity": {
          "value": 4,
          "reason": "Named X, named rival (liver morphology), named dissociation lever; slightly below 5 because 'chronic-liver-disease score' awaits the keystone's answer on which output exactly."
        },
        "identifiability": {
          "value": 3,
          "reason": "Spleen-liver collinearity is severe in true cirrhosis; identification rests on the non-hepatic-splenomegaly cases, whose frequency in public cohorts is unknown."
        },
        "medical_relevance": {
          "value": 4,
          "reason": "If the answer is spleen, Merlin-style opportunistic liver screening systematically misfires on hematologic and thrombotic splenomegaly - an actionable, testable deployment warning."
        },
        "interest": {
          "value": 4,
          "reason": "A foundation model reading the neighbor organ rather than the named one is exactly the program's motivating phenomenon."
        },
        "prior_legwork": {
          "value": 4,
          "reason": "Weights, tools, and cohorts exist and are open; no local pipeline for Merlin yet, unlike CT-CLIP."
        },
        "feasibility": {
          "value": 3,
          "reason": "Capped: keystone NOT_INSPECTED (which output exposes the score), plus the dynamic-range risk on healthy public cohorts."
        },
        "data_readiness": {
          "value": 4,
          "reason": "All public or MIT; nothing gated beyond HF click-through."
        },
        "evaluation_readiness": {
          "value": 3,
          "reason": "Partial-correlation framework is standard but the dissociation-case definition and phase stratification need custom, prespecified work."
        },
        "negative_result_value": {
          "value": 3,
          "reason": "Sensitivity-limited by construction; honest margin machinery is specified but a null will not kill the broader question."
        },
        "novelty_confidence": {
          "value": 3,
          "reason": "Capped by rule and by honesty: Merlin-mechanism work is young but moving fast; no full audit yet."
        },
        "regret": {
          "value": 3,
          "reason": "Worth doing while Merlin is the reference abdominal model; moderate regret if scooped since the assets are public."
        }
      },
      "priority_score": 3.5,
      "unverified_claims": [
        "That chronic liver disease / cirrhosis is among Merlin's evaluable phenotypes with >20 positives (paper subset criterion) - the keystone.",
        "That zero-shot text prompting is a supported Merlin usage mode.",
        "Spleen-volume/cirrhosis clinical correlation citations - from general knowledge, to be pinned to primary sources at idea-card stage.",
        "That AMOS/TotalSegmentator-dataset metadata suffice for phase stratification.",
        "TotalSegmentator paper DOI (10.1148/ryai.230024) cited from memory."
      ],
      "track": "baseline"
    },
    {
      "id": "scout-010-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The inferior vena cava as a manometer: does the chest model read venous pressure?",
      "question": "Are CT-CLIP's pleural-effusion and cardiomegaly heads using the distension and roundness of the intrahepatic inferior vena cava as a central-venous-pressure gauge?",
      "rung": "Targets rung 1 (the heads use IVC geometry). Rung 3 is unusually reachable for a Mode C because the X is already physician-named ('distended IVC', 'flat IVC') and mechanistically understood; what moves it up is the within-patient conditional analysis showing score movement with IVC geometry when fluid and heart size are held fixed.",
      "deliverable_sentence": "CT-CLIP is using the distension and roundness of the intrahepatic inferior vena cava - a central-venous-pressure gauge - in its pleural-effusion and cardiomegaly scores.",
      "X_measurement": "IVC cross-sectional area and flatness index (short/long axis ratio) on the axial slab between the diaphragm and the hepatic-vein confluence, from the TotalSegmentator 'inferior_vena_cava' class (verbatim in map_to_binary.py, task 'total'; fetched 2026-08-12). Both are established bedside quantities: the flat-IVC sign of hypovolemia and the ultrasound IVC distension/collapsibility index for right-atrial pressure (ASE guideline lineage; primary citations to be pinned). Computable today on any chest CT that includes the upper abdomen, without asking anyone: yes, if segmentation holds on non-contrast (see residual).",
      "suspected_signal": "Hydrostatics: the IVC is a thin-walled capacitance vessel whose cross-section and roundness track transmural pressure. Elevated right-heart pressure - the same physiology that produces transudative pleural effusions and cardiomegaly - distends and rounds it. Radiologists read this on ultrasound daily but rarely quantify it on chest CT; a report-supervised model exposed to thousands of heart-failure chests could have learned the gauge.",
      "keystone_prerequisite": "The inference needs: (a) the intrahepatic IVC is inside the CT-RATE field of view and segmentable on non-contrast volumes at usable reliability, and (b) enough patients have >=2 separate scan sessions for a within-patient design.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Parts inspected: repeat sessions exist - decisions.md (2026-08-04, directly inspected counts) records '3,039 validation volumes / 1,564 scans / 1,304 patients', implying ~260 extra scan-sessions in validation alone, with the far larger train split unexamined; TotalSegmentator includes 'inferior_vena_cava' (verbatim, map_to_binary.py). NOT inspected, and load-bearing: IVC in-FOV rate in CT-RATE and non-contrast IVC segmentation reliability (low vessel-liver contrast is exactly where it could fail).",
      "keystone_residual_assumption": "Having verified repeats exist and the tool has the class, I am still assuming the tool's IVC mask on NON-CONTRAST chest-CT bases is accurate enough that area/flatness changes are signal rather than segmentation noise. That is the real keystone; Stage 0 is therefore a 30-scan manual-free QC: test-retest IVC geometry across the idea-004 geometry-matched reconstruction pairs, which gives a segmentation noise floor WITHOUT any human annotation - the same self-comparison move that saved idea 004.",
      "rung_reached": "Rung 1 if within-patient score changes track IVC geometry changes conditional on measured effusion and heart size. The design borrows rung-2 strength from the within-patient structure (habitus, sex, site, referral fixed); the named residual is respiratory state, which is conditioned on via measured lung volume from the same segmentation pass.",
      "dies_like_prior": "Closest prior kill is idea-016 (contrast reflux as pressure gauge - IDENTIFIABILITY_FAILURE because reflux was inseparable from injection protocol). Difference: CT-RATE is non-contrast, so the entire injection-protocol axis is absent by construction; IVC geometry is anatomy, not contrast dynamics; and the within-patient longitudinal design removes the population covariates that idea-016 could not. The wrong-keystone error (charter, three occurrences) is guarded by naming segmentation-on-non-contrast as the real keystone rather than the easy adjacent facts already verified.",
      "closest_prior_work": "Idea-016's debate record (this repo) for the pressure-gauge framing and its failure mode. Clinical literature on CT IVC flatness/distension as volume-status markers (trauma flat-cava sign; unverified primary citations). CT-CLIP papers: no mechanism analysis of the effusion/cardiomegaly heads. No work found connecting a chest-CT foundation model's outputs to quantified IVC geometry - unverified negative, limited search.",
      "existing_assets": "The complete idea-004 apparatus: local CT-CLIP inference, checkpoint verification, geometry-matched reconstruction pairs (the free test-retest noise floor for BOTH the model scores and the IVC measurement), CT-RATE inventory with patient-level linkage ('split_patientID_scanID_reconstructionID' folder structure, HF dataset page). TotalSegmentator public.",
      "smallest_decisive_experiment": "Stage 0: IVC segmentation noise floor on 30 reconstruction pairs (no annotation needed). Then: identify patients with >=2 sessions (start with the ~200-260 in validation), compute within-patient deltas of effusion/cardiomegaly scores vs deltas of IVC area/flatness, conditional on delta-effusion-proxy (dependent pleural HU volume), delta-heart cross-section, and delta-lung volume (respiratory state). Decision: conditional within-patient association exceeding the reconstruction-pair noise floor. The most interesting prespecified cell: scans with NO visible effusion in either session, where a score-IVC association cannot be 'the model sees the fluid'.",
      "standing_confounds_addressed": "Habitus, sex, site, referral pathway, prevalence: fixed within patient. Scanner/protocol/reconstruction: CT-RATE repeats are same-center; reconstruction handled by using the idea-004 noise floor and matching kernels where possible. Positioning and respiratory state: the named residuals - respiration moves IVC caliber directly; conditioned via measured lung volume, and reported as the limiting alternative if conditioning is weak. Label leakage: no labels in the readout.",
      "alternative_explanations": "(1) Respiratory state drives both IVC caliber and apparent lung base appearance the model reads - the serious one; lung-volume conditioning is the answer and its adequacy is reportable; (2) segmentation noise on non-contrast manufactures or masks the effect - Stage 0 noise floor; (3) the model reads right-heart chamber enlargement directly and IVC merely co-varies - conditioning on heart cross-section addresses the crude version, and a positive should honestly be stated as 'venous-congestion geometry including the IVC' if heart conditioning is imperfect.",
      "anticipated_negative": "Sensitivity-limited, honestly: the within-patient n is modest and two noise floors (model score, segmentation) stack. The card inherits a real mitigation - the idea-004 reconstruction pairs quantify both floors before the main analysis, so the minimum detectable effect is estimable in advance rather than post hoc.",
      "cross_domain": "Borrowed construct: pressure-vessel mechanics / fluid statics - a compliant tube's cross-section is a transmural-pressure readout. The measurement it implies: IVC area plus roundness (not area alone - roundness is the pressurization signature). What would change if the analogy were dropped: there would be no reason to select IVC geometry as X at all, no prediction that ROUNDNESS carries signal beyond area, and no prediction that the association should persist in effusion-free scans (the gauge reads pressure before fluid appears). The analogy dictates the feature set, the direction, and the most interesting analysis cell; it is not decoration.",
      "remaining_legwork": "Stage 0 noise floor (2-3 days, assets local); repeat-session inventory of train split (1 day, metadata only); main within-patient analysis (3-4 days). Mode C: feasibility reported for information, not scored.",
      "design_template": "longitudinal-within-subject",
      "use_vs_association": "Within-patient change decouples the claim from every stable patient-level correlate; conditioning on measured fluid, heart size, and lung volume separates 'reads the venous gauge' from 'sees the effusion, which co-varies with the gauge'; the effusion-free cell makes the association impossible to attribute to visible fluid.",
      "dataset": "CT-RATE (repeat-session subset; second and final CT-RATE candidate this cycle).",
      "scores": {
        "mechanism_clarity": {
          "value": 5,
          "reason": "A specific physical quantity (transmural venous pressure) read through two named geometric measurements (IVC area, roundness), with the measurement that would show the model uses it fully specified."
        },
        "identifiability": {
          "value": 3,
          "reason": "Within-subject design plus conditioning is strong for an observational study, but respiratory state is a genuine common cause that conditioning may only partially remove."
        },
        "interest": {
          "value": 4,
          "reason": "A model quietly performing bedside hemodynamic assessment on every chest CT would be a genuinely new capability claim; a clean negative also matters for the 'foundation models read physiology' narrative."
        },
        "medical_relevance": {
          "value": 4,
          "reason": "If true, effusion/cardiomegaly scores partly encode volume status - both an explanation of false positives and a free hemodynamic signal clinicians do not currently get from chest CT."
        },
        "clarity": {
          "value": 4,
          "reason": "Precise X and design; slightly held back because the deliverable spans two heads and the claim may need narrowing to one."
        },
        "feasibility_info_only": {
          "value": 3,
          "reason": "Reported outside the Mode C score: assets are local and the design is cheap, but the non-contrast segmentation keystone is uninspected."
        },
        "novelty_confidence_info_only": {
          "value": 3,
          "reason": "Limited search found no model-IVC connection; capped and reported outside the score."
        }
      },
      "priority_score": 4.05,
      "priority_note": "Mode C weighting: 0.3*mechanism_clarity + 0.25*identifiability + 0.2*interest + 0.15*medical_relevance + 0.1*clarity = 1.5+0.75+0.8+0.6+0.4 = 4.05.",
      "unverified_claims": [
        "IVC in-FOV rate in CT-RATE volumes (keystone half a).",
        "Non-contrast IVC segmentation reliability of TotalSegmentator (keystone half b).",
        "Flat-cava / IVC-distension clinical citations from general knowledge; primary sources to be pinned.",
        "That train-split repeat sessions are numerous enough if validation's ~200-260 prove insufficient."
      ],
      "track": "baseline"
    },
    {
      "id": "scout-010-c05",
      "search_mode": "C",
      "entry_point": 2,
      "title": "Aortic tortuosity as a buckled column: is the hypertension head reading exceeded critical pressure?",
      "question": "Is Merlin's five-year hypertension prediction using abdominal aortic tortuosity - the buckled geometry of a chronically over-pressurized elastic tube - as its cue?",
      "rung": "Targets rung 1 (the model uses aortic tortuosity). Rung 2 hinges on separating tortuosity from age; rung 3 is available because 'tortuous aorta' is already a report phrase - the buckling frame adds the mechanism, not the vocabulary.",
      "deliverable_sentence": "Merlin is using abdominal aortic tortuosity - the buckled shape of a vessel whose critical buckling pressure has been exceeded - in its five-year hypertension prediction.",
      "X_measurement": "Tortuosity index = centerline arc length / straight-line chord of the abdominal aorta (diaphragmatic hiatus to bifurcation), centerline by skeletonization of the TotalSegmentator 'aorta' mask (verbatim class, map_to_binary.py; fetched 2026-08-12), plus undulation wavelength and amplitude from the centerline's curvature spectrum. Arterial tortuosity indices are established measurements (review literature in Hypertension; primary citations to be pinned). Computable today on any abdominal CT without asking anyone: yes.",
      "suspected_signal": "Elastic stability: a pressurized tube with axial pre-stretch buckles when transmural pressure exceeds a critical value set by wall stiffness and tethering; sustained hypertension plus elastin fragmentation lowers that threshold, and the buckled (tortuous) shape is permanent. Tortuosity is therefore a manometer with memory - a geometric record of chronic pressure load, distinct from the instantaneous pressure at scan time. Biomechanical theory: Han's artery-buckling work (J Vasc Res, circa 2012; to be pinned).",
      "keystone_prerequisite": "The inference needs: Merlin's released five-year disease-prediction assets include a hypertension output that can be run on new abdominal CTs.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "Two artifacts, both fetched 2026-08-12: (1) arXiv 2406.06512 (HTML full text) names the five-year targets verbatim: 'chronic kidney disease, osteoporosis, cardiovascular disease, ischemic heart disease, hypertension, and diabetes'; (2) huggingface.co/stanfordmimi/Merlin lists downloadable weights explicitly including 'Five Year Disease Prediction' alongside the main checkpoint, MIT license, with inference demos referenced.",
      "keystone_residual_assumption": "Having verified the head exists and its weights are listed, I am still assuming (a) the released five-year weights load and their output ordering/documentation identifies the hypertension logit, and (b) the evaluation cohort problem is solvable: separating tortuosity from AGE requires age metadata on public abdominal CTs, and whether AMOS or the TotalSegmentator dataset expose usable age fields is unverified. Assumption (b) is load-bearing for identifiability, not just convenience, and is Stage 0 gate #1.",
      "rung_reached": "Rung 1 via conditional association (score vs tortuosity, conditional on age, aortic diameter, and calcification burden). What moves it up is the buckling-specific signature: theory predicts onset nonlinearity and an undulation wavelength scaling with vessel radius - signatures that age-driven uniform elongation does not produce, giving the design a way to distinguish 'reads pressure-buckled geometry' from 'reads age'.",
      "dies_like_prior": "Dies, if it dies, exactly like idea-009 (Murray's law - IDENTIFIABILITY_FAILURE: the geometric quantity was inseparable from co-varying acquisition and population factors). Stated differences: tortuosity is a centimeter-scale, voxel-size-robust measurement where Murray exponents needed sub-voxel calibre precision; the dominant rival (age) is named up front with the design conditional on it rather than discovering the collinearity in debate; and the buckling wavelength signature provides a discriminating prediction Murray's-law candidate never had. If age metadata cannot be obtained, this candidate should be killed at Stage 0 for the same reason as idea-009 - the card says so explicitly.",
      "closest_prior_work": "Han HC, biomechanics of artery buckling (J Vasc Res ~2012, unverified from memory): theory and bench validation, never connected to a learned model. Clinical tortuosity-hypertension association literature (Hypertension review, unverified): establishes the correlation in humans, does not involve any imaging model. Merlin (arXiv 2406.06512): reports hypertension AUC, no mechanism. Exact delta: nobody has asked whether a CT foundation model's hypertension output is mediated by measured aortic geometry, nor tested buckling-theory signatures in a model's learned cue.",
      "existing_assets": "Merlin weights incl. five-year head (verified listed, MIT); TotalSegmentator aorta class (verified); public abdominal CT cohorts; established tortuosity metrics; buckling theory with quantitative predictions.",
      "smallest_decisive_experiment": "Stage 0: confirm the hypertension logit loads and identify a public cohort with age fields (kill if none). Then on ~500 public abdominal CTs: score vs tortuosity index conditional on age, aortic diameter, and calcification burden (calcium measured on the same clipped HU range noted in decisions.md 2026-08-10 if Merlin preprocessing clips similarly - check). Decision: conditional partial association with a prespecified minimum effect; exploratory second read: onset nonlinearity and radius-scaled wavelength as the buckling signature.",
      "standing_confounds_addressed": "Age: THE confound - conditioned on directly; candidate dies at Stage 0 without age metadata. Aortic calcification: measured and conditioned (the rival cue a model would plausibly use for hypertension). Scanner/site/protocol/reconstruction: geometry measurement is robust to kernel; within-dataset analyses. Habitus: weakly linked to tortuosity; body-cross-section covariate available from the same pass. Prevalence/referral/label leakage: label-free readout, unaffected.",
      "alternative_explanations": "(1) The model reads age (from bone, organs, everything) and age drives tortuosity - the design's central rival, handled by conditioning plus the buckling-signature analysis; residual confounding by age is the honest limit and is why identifiability is not scored higher; (2) the model reads aortic calcification which co-travels with tortuosity - measured and conditioned; (3) the model reads aortic diameter (ectasia) - measured, conditioned, and geometrically separable from tortuosity.",
      "anticipated_negative": "Sensitivity-limited: conditioning on age absorbs much of the real signal's variance, so a null needs the prespecified minimum-detectable-effect framework; a null on the buckling SIGNATURE with a positive plain association degrades gracefully to 'uses tortuosity, mechanism unresolved' and the card claims no more.",
      "cross_domain": "Borrowed construct: elastic stability / column buckling from structural engineering. The measurement it implies: not just a tortuosity index but its decomposition - onset nonlinearity in the score-tortuosity relation and undulation wavelength scaling with vessel radius, the fingerprints of a buckling instability. What would change if the analogy were dropped: the analysis would collapse to a linear score-vs-tortuosity regression; the theory is what licenses the wavelength and threshold analyses that can separate pressure-buckling from uniform age-related elongation. The analogy changes the experiment, so it stays.",
      "remaining_legwork": "Stage 0 gates (weights load + age metadata: 1-2 days); segmentation and centerline pipeline (2-3 days); analysis (2-3 days). Mode C: feasibility reported for information.",
      "design_template": "conditional-observational",
      "use_vs_association": "Distinguishes use from correlation by conditioning on the named common causes (age, diameter, calcification) and by the buckling-signature analysis: a model merely correlated with tortuosity through age should show neither onset nonlinearity nor radius-scaled wavelength dependence in its score response.",
      "dataset": "Public abdominal CT with age metadata (candidate cohorts: AMOS 2022, TotalSegmentator public dataset - metadata adequacy is Stage 0); Merlin checkpoint from HF. Second and final Merlin/public-abdominal candidate this cycle.",
      "scores": {
        "mechanism_clarity": {
          "value": 5,
          "reason": "A specific physical quantity (critical transmural buckling pressure of an elastic tube) with a specific geometric readout (tortuosity index plus wavelength scaling) and quantitative theory behind it."
        },
        "identifiability": {
          "value": 3,
          "reason": "Age collinearity is severe and conditioning is imperfect; the buckling signature is a genuine discriminator but exploratory - without it this would be a 2."
        },
        "interest": {
          "value": 4,
          "reason": "A learned model rediscovering an elastic-stability threshold would be a striking instance of the program's thesis; the wavelength test is the kind of analysis nobody runs on foundation models."
        },
        "medical_relevance": {
          "value": 3,
          "reason": "Opportunistic hypertension flagging from abdominal CT is plausible but not yet a clinical pathway; knowing the cue is tortuosity would matter mainly for trust and for vascular-aging research."
        },
        "clarity": {
          "value": 4,
          "reason": "Precise question and X; the two-layer claim (uses tortuosity; tortuosity is buckling) needs the card to keep the layers separate, which costs a point."
        },
        "feasibility_info_only": {
          "value": 3,
          "reason": "Reported outside the Mode C score: keystone inspected, but the age-metadata gate and centerline pipeline are real work."
        },
        "novelty_confidence_info_only": {
          "value": 3,
          "reason": "No audit yet; vascular-aging imaging is an active field and a tortuosity-model connection may exist somewhere."
        }
      },
      "priority_score": 3.9,
      "priority_note": "Mode C weighting: 0.3*5 + 0.25*3 + 0.2*4 + 0.15*3 + 0.1*4 = 1.5+0.75+0.8+0.45+0.4 = 3.9.",
      "unverified_claims": [
        "Han artery-buckling citation and Hypertension tortuosity review cited from memory - pin before idea card.",
        "Age metadata availability in AMOS / TotalSegmentator public dataset (Stage 0 gate).",
        "That the released five-year weights expose an identifiable hypertension logit.",
        "Whether Merlin preprocessing clips HU in a way that affects the calcification covariate (check per decisions.md 2026-08-10 side finding)."
      ],
      "track": "baseline"
    }
  ]
}


===== ideas/scout-010/run_provenance.json =====
{
  "timestamp": "2026-08-12T07:09:25+00:00",
  "git_commit": "6ed719545b60d4f4eaec50bf09f3e22148b39e2f",
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
    "feasibility.md": "48f4f111abfcd1eb",
    "fiction_extract.md": "8ada1a395c25072e",
    "fiction_refine.md": "ab92bb6c46fe0fbb",
    "fiction_scout.md": "63b11687055c8624",
    "interpret.md": "ea213b1be9c3d178",
    "keystone_screen.md": "f6f206ca8577b47b",
    "librarian.md": "3c5c129fe98b1717",
    "novelty_audit.md": "eb2b70b4159ab881",
    "probe_code.md": "bc0c52c94d1af371",
    "probe_plan.md": "a10441cab1b3d8e0",
    "probe_review.md": "0b420d600b32812f",
    "revise.md": "db7fab4a10c7c32b",
    "scout.md": "c5ae0f349d7a6d67",
    "wide_scout.md": "b21b441dba189d08"
  },
  "agents_toml_hash": "7e80bd12c967c003"
}


===== ideas/scout-010/scout_candidates.json =====
{
  "cycle": "scout-010",
  "track": "baseline",
  "date": "2026-08-12",
  "all_questions": [
    "Q1: Is CXR-Age's biological-age output assembled from the measurable geometry of the chest film - cardiothoracic ratio and projected lung area - or does the mortality signal live somewhere those numbers miss? [radiologist-word X: cardiothoracic ratio]",
    "Q2: When CT-CLIP scores atelectasis above consolidation on the same scan, is it using measured lobar volume loss to make the separation? [radiologist-word X: lobar volume loss / collapse]",
    "Q3: Is Merlin's chronic-liver-disease score using splenic volume - congestive splenomegaly, the portal-pressure gauge - rather than the liver itself? [radiologist-word X: splenomegaly]",
    "Q4: Do cardiomegaly classifiers use the cardiothoracic RATIO or just absolute heart area - did the model learn the normalization radiologists insist on? [radiologist-word X: cardiothoracic ratio]",
    "Q5: Is the chest-CT model reading the caliber and roundness of the inferior vena cava as a central-venous-pressure manometer? [radiologist-word X: IVC distension / flat IVC; possibly unanswerable: non-contrast IVC segmentation may not be reliable]",
    "Q6: Is Merlin's hypertension prediction reading the abdominal aorta as a buckled column - tortuosity as the geometric residue of exceeded critical buckling pressure? [cross-domain: structural engineering / elastic stability; suspect too hard: age collinearity]",
    "Q7: Is the lung-cancer model reading adrenal gland volume as a chronic-stress dosimeter? [the obviously-wrong-but-not-immediately-refutable one: adrenal hypertrophy under chronic HPA activation is documented, adrenals are in LDCT field of view and TotalSegmentator segments them]",
    "Q8: Do emphysema heads read the percolation statistics of the destroyed lung - the cluster-size power law near threshold - rather than the destroyed fraction? [cross-domain: statistical physics / percolation; suspect too hard]",
    "Q9: Is the nodule-malignancy model measuring lesions with the same Gini-M20 light-concentration statistics astronomers use to classify merging galaxies? [cross-domain: astronomy morphometrics]",
    "Q10: Does CT-CLIP read anything from the scan exterior - table, gown, arms - when every voxel inside the patient contour is held fixed? [the endorsed idea-006 spin-off, phrased positively]"
  ],
  "dropped_questions": [
    {
      "question": "Q4 (cardiomegaly: ratio vs absolute area)",
      "reason": "Answered largely as a byproduct of Q1's decomposition on the same masks and tool; carrying both would stake two of five candidates on one shared keystone (CheXmask/HybridGNet mask validity) without adding a second mechanism. If Q1 advances, this question falls out of its dissociation strata for free."
    },
    {
      "question": "Q7 (adrenal volume as stress dosimeter)",
      "reason": "Kept in the ten as the obviously-wrong slot; dropped at development because no obtainable host model's training population plausibly carries the signal at measurable strength, and adrenal volumetry on non-contrast LDCT sits at the segmentation tool's reliability floor - the study would be uninterpretable, not merely unlikely."
    },
    {
      "question": "Q8 (emphysema percolation statistics)",
      "reason": "Collides with backlog scout-008-c04 (the emphysema call may read the shape of the holes, not just how many) - same estimand family, low-attenuation-cluster morphology vs fraction. Proposing it again with percolation vocabulary would be the homogenization the digest warns about."
    },
    {
      "question": "Q9 (Gini-M20 galaxy morphometrics on nodules)",
      "reason": "Fails the charter's analogy-drop test: with the astronomy frame removed I would compute nodule heterogeneity/concentration statistics anyway, which is standard radiomics. The analogy is decoration, not a measurement."
    },
    {
      "question": "Q10 (scan-exterior substitution)",
      "reason": "Its deliverable names an acquisition object (table, gown), not an anatomical or physiological X, and this cycle explicitly requires physician-legible X-positive questions. It remains the endorsed idea-006 spin-off and should enter, if at all, via the librarian/revival path where its confound-audit value is scored on its own terms."
    }
  ],
  "quota_note": "Zero revivals this cycle: nothing in the portfolio brief has a genuinely NEW external fact (the idea-006 exterior-swap spin-off is endorsed but unchanged and is confound-shaped, excluded by this cycle's X-positive rule; idea-005's S2 spin-off is deliberately left to the revival machinery per the 2026-08-10 ledger note). Template concentration: four of five candidates declare conditional-observational as primary grammar. This is deliberate, not drift: the digest shows the interventional grammars (counterfactual-synthesis 3, representation-erasure 3, regional-substitution 3) are saturated and repeatedly die on edit-validity/OOD objections (ideas 006, 008, 011, 014), so this cycle leads with named-X observational screens whose use-claim upgrades are prespecified but deferred. Each card states its USE-vs-ASSOCIATION line explicitly; the two strongest use structural moves (within-scan head contrast, within-patient longitudinal change) that do not need trustworthy labels.",
  "revivals": [],
  "candidates": [
    {
      "id": "scout-010-c01",
      "search_mode": "A",
      "entry_point": 1,
      "title": "CXR-Age put back together from parts a radiologist can measure",
      "question": "Is CXR-Age's biological-age output assembled from automatically measurable chest-film geometry - cardiothoracic ratio and projected lung area - or does the mortality signal live in a residual those measurements miss?",
      "rung": "Targets rung 1 (CXR-Age uses thoracic geometry) with an explicit path to rung 3, because X is already a named clinical quantity (cardiothoracic ratio). Moves up to a use-claim via the prespecified dissociation-strata arm and, conditional on a training-distribution check, a PA/AP projection natural experiment.",
      "deliverable_sentence": "CXR-Age is using the cardiothoracic ratio and projected lung area - the measurable geometry of the chest film - as principal drivers of its biological-age output.",
      "X_measurement": "CTR = maximal horizontal cardiac width / maximal inner thoracic width, and projected lung area, both computed from CheXmask heart and lung masks (HybridGNet; PhysioNet 'chexmask-cxr-segmentation-data', open access, CC BY 4.0, precomputed for ChestX-ray8, CheXpert, MIMIC-CXR-JPG, PadChest, VinDr-CXR; masks for 'Left Lung', 'Right Lung', 'Heart' - quoted from the PhysioNet page, fetched 2026-08-12). Could I compute X on a new film today without asking anyone? Yes - masks are precomputed for the public datasets, and HybridGNet code is public for new images.",
      "suspected_signal": "Aging remodels chest geometry in ways visible on a frontal film: LV remodeling and aortic unfolding raise CTR; hyperinflation and kyphosis change projected lung area; both carry independent mortality risk. The hypothesis is that CXR-Age's phenotypic-age head largely re-derives this geometry rather than a texture-level signal.",
      "keystone_prerequisite": "The inference needs: the released checkpoint IS the published CXR-Age model, runs with documented preprocessing, and produces the published output semantics (a number in years reflecting mortality risk). If the checkpoint is not faithful or not runnable, every downstream decomposition is uninterpretable.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "github.com/circ-ml/CXR-Age README (fetched 2026-08-12): 'Weights for the CXR-Age model are in development/models/PLCO_Fine_Tuned_120419.pth' and 'CXR-Age outputs a number (in years) reflecting all-cause mortality risk based on only a single chest radiograph image.' MIT license, 'not for clinical care or commercial use'.",
      "keystone_residual_assumption": "Having verified the weights exist with documented output semantics, I am still assuming the checkpoint reproduces published behavior (e.g., high correlation with chronological age in healthy subsets) and that repo preprocessing is complete enough to run it unambiguously. This is load-bearing and is therefore Stage 0 gate #1: run the checkpoint on a public dataset with age metadata (ChestX-ray8 has ages) and require the published-magnitude age correlation before any decomposition is interpreted. Second residual: CheXmask mask quality bounds the attainable R-squared - a measurement-noise ceiling must be estimated (mask test-retest across near-duplicate films) and prespecified before the decomposition is read.",
      "rung_reached": "Rung 1 if the variance decomposition plus dissociation strata show CXR-Age tracking geometry within chronological-age-and-sex-matched strata. Moves to rung 2/3 because X is artifact-checkable (geometry is measured, not annotated) and already physician-named; the main rung-2 residual is inspiration depth, which is partially self-controlling (deep inspiration lowers CTR but raises lung area, so the two X's dissociate under it).",
      "dies_like_prior": "Closest prior failure is USE_VS_ASSOCIATION (cycle-one kills): a decomposition is an association. Difference: the design prespecifies dissociation strata (films matched on chronological age, sex, and view where CTR differs materially) so the claim is conditional tracking, not raw correlation; and the quasi-interventional PA/AP arm is available but explicitly gated on verifying AP views are in CXR-Age's training distribution - stated up front to avoid the idea-006 OOD-intervention trap rather than discovering it in critique. No annotation-provenance exposure: no human label enters the primary readout.",
      "closest_prior_work": "qCXR-bioage (Radiology: Cardiothoracic Imaging, DOI 10.1148/ryct.250327): builds its OWN explainable biological age from automated CXR quantifications (lung area, emphysema probability, aortic diameter, heart area, bone density) and shows it predicts mortality. It does NOT decode the existing CXR-Age checkpoint - it shows the vocabulary suffices, not that Lu/Raghu's model uses it. Raghu et al., CXR-Age, JACC Cardiovasc Imaging 2021 (DOI 10.1016/j.jcmg.2021.01.008, unverified-from-memory): built the model, published saliency only. Project Baseline preprint (medrxiv 2025.01.02.24319734): CXR-Age vs epigenetic clocks, associations only. The exact delta: nobody has published a variance decomposition + dissociation analysis of the released CXR-Age checkpoint against automatically measured film geometry.",
      "existing_assets": "CXR-Age weights (MIT, path verified); CheXmask precomputed masks for the exact public datasets (CC BY 4.0, verified open); ChestX-ray8 and PadChest fully public with age/sex/view metadata; qCXR-bioage as the published biomarker vocabulary to decompose against.",
      "smallest_decisive_experiment": "Run the checkpoint on ~10k ChestX-ray8 films with CheXmask masks. Gate 1: reproduce published age correlation. Then: (a) R-squared of CXR-Age on {CTR, lung area, chronological age, sex}; (b) within strata matched on chronological age/sex/view, test whether CXR-Age monotonically tracks CTR. Decision: if conditional tracking is strong and R-squared approaches the mask-noise ceiling, the deliverable sentence stands at rung 1; if R-squared is low with tracking absent, the geometry hypothesis is dead and the residual (texture/bone) becomes the finding.",
      "standing_confounds_addressed": "Scanner/site/protocol: analysis is within-dataset and within-view; site enters only if geometry measurement itself is site-biased (masks are geometric, not intensity-based - low risk). Positioning/inspiration: named residual; partially separable because inspiration moves CTR and lung area in opposite directions. Habitus: a real correlate of both geometry and mortality - the claim is about what the model uses, so habitus driving geometry does not confound rung 1, only the rung-3 gloss. Label leakage/prevalence/referral: no labels in the primary readout. NOT ruled out: inspiration depth as a shared cause of score and CTR within strata.",
      "alternative_explanations": "(1) CXR-Age uses fine texture (bone density, vascular markings) that merely correlates with geometry - addressed by the dissociation strata and by reporting the residual's mortality-relevant correlates; (2) mask errors correlate with disease severity, inflating apparent tracking - addressed by the prespecified noise ceiling and QC subset; (3) the appeal of this candidate is partly that it sounds like a tidy accounting exercise - the honest risk is a mushy middle result (R-squared ~ 0.4) that neither confirms nor kills; the margin structure below is designed for exactly that.",
      "anticipated_negative": "Sensitivity-limited unless the mask-noise ceiling is estimated first; with the ceiling prespecified, a low conditional R-squared with an equivalence margin is decisive AGAINST geometry-as-principal-driver and is itself publishable (the mortality signal is not the geometry radiologists would first name).",
      "cross_domain": null,
      "remaining_legwork": "Download weights + verify runnable (half a day); pull CheXmask + join to ChestX-ray8 metadata (half a day); noise-ceiling estimation (1 day); decomposition + strata (1-2 days). First decision in under a week on Colab-class compute.",
      "design_template": "conditional-observational",
      "use_vs_association": "Distinguishes use from correlation by (a) conditioning on chronological age/sex/view so geometry cannot ride on demographics, (b) dissociation strata where CTR and lung area decouple, and (c) a gated PA/AP projection arm in which apparent CTR changes while anatomy is fixed - a natural intervention on X, run only if AP is verified in-distribution.",
      "dataset": "ChestX-ray8 (primary), PadChest (replication); CheXmask for both.",
      "scores": {
        "clarity": {"value": 4, "reason": "One-sentence question with a named X; loses a point because 'principal drivers' needs a prespecified threshold to be fully crisp."},
        "identifiability": {"value": 3, "reason": "Conditional tracking + dissociation strata rule out demographics and dataset mix; texture-correlated-with-geometry survives unless the PA/AP arm clears its distribution gate."},
        "medical_relevance": {"value": 4, "reason": "CXR-Age is proposed for mortality triage; whether it is CTR-plus-lung-area in a trench coat determines both trust and whether a transparent two-measurement surrogate suffices."},
        "interest": {"value": 4, "reason": "Either answer is compelling: a famous black-box clock reduced to two classroom measurements, or a demonstrated residual that geometry cannot explain."},
        "prior_legwork": {"value": 5, "reason": "Weights public, masks precomputed for the exact datasets, biomarker vocabulary published (qCXR-bioage); nothing needs annotation."},
        "feasibility": {"value": 4, "reason": "Keystone INSPECTED_TRUE lifts the cap; all assets verified open; days-scale on single-GPU."},
        "data_readiness": {"value": 5, "reason": "Everything is public and directly usable (CC BY 4.0 masks, public CXR sets, MIT weights)."},
        "evaluation_readiness": {"value": 4, "reason": "R-squared decomposition and matched-strata analysis are standard; the noise ceiling requires custom but well-defined work."},
        "negative_result_value": {"value": 3, "reason": "Sensitivity-limited without the noise ceiling; decisive with it - scored at the honest midpoint since the ceiling is planned but not yet estimated."},
        "novelty_confidence": {"value": 3, "reason": "qCXR-bioage is adjacent and recent; the decode-the-existing-checkpoint delta is real but the space is active - capped by my own uncertainty, not the rule."},
        "regret": {"value": 4, "reason": "If someone else publishes the CXR-Age decomposition with these exact public assets, it will look obvious in hindsight."}
      },
      "priority_score": 3.85,
      "unverified_claims": [
        "Raghu et al. CXR-Age DOI (10.1016/j.jcmg.2021.01.008) and Lu et al. CXR-risk DOI cited from memory - verify before the idea card.",
        "That ChestX-ray8 metadata age fields are reliable enough for the Stage 0 faithfulness gate (known to contain some noise).",
        "That CXR-Age pretraining included AP views (determines whether the PA/AP arm is in-distribution).",
        "qCXR-bioage seen via search result and abstract only; full methods not read."
      ]
    },
    {
      "id": "scout-010-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "Atelectasis vs consolidation: has CT-CLIP learned the radiologist's volume-loss rule?",
      "question": "When CT-CLIP scores atelectasis above consolidation on the same scan, is it using measured lobar volume loss to make that separation?",
      "rung": "Targets rung 1 (the model uses lobar volume loss for the atelectasis/consolidation contrast). Moves toward rung 3 cheaply because X is the textbook criterion radiologists themselves use - if rung 1 and the rung 2 checks hold, the deliverable sentence is immediate.",
      "deliverable_sentence": "CT-CLIP is using lobar volume loss to separate atelectasis from consolidation.",
      "X_measurement": "Lobar volumes from TotalSegmentator lung-lobe classes ('lung_upper_lobe_left', 'lung_lower_lobe_left', 'lung_upper_lobe_right', 'lung_middle_lobe_right', 'lung_lower_lobe_right' - verbatim from totalsegmentator/map_to_binary.py, fetched 2026-08-12). Volume-loss index: affected-lobe fractional volume relative to the scan's remaining lobes, plus fissure-shift proxy (lobe centroid displacement). Competing signal measured in the same pass: opacity burden = volume of intra-lobar voxels above -300 HU. Computable today on any chest CT without asking anyone: yes; the closest published validation is nnU-Net-based lobar volumetry of postoperative atelectasis (npj Digital Medicine, nature.com/articles/s41746-026-02683-6).",
      "suspected_signal": "The physiologic distinction itself: atelectasis is collapse (volume loss, fissure displacement, crowding), consolidation is alveolar filling with volume preserved. A report-supervised model could learn either the real volumetric criterion or a co-occurrence shortcut (tubes, effusions, basal location). The question is which.",
      "keystone_prerequisite": "The inference needs: the released CT-CLIP/ClassFine checkpoint exposes SEPARATE atelectasis and consolidation outputs whose within-scan contrast is non-degenerate (not near-duplicate scores).",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "ideas/004/log_probe_code.txt, EXPECTED_PATHOLOGIES ('The 18 head names in released order. Source: scripts/ct_lipro_inference.py in the official CT-CLIP repository (fetched 2026-08-11)') lists 'Atelectasis' and 'Consolidation' as distinct heads, alongside 'Pleural effusion' and 'Cardiomegaly'. The idea-004 probe contract already verified 18-output load and one-pair inference on this checkpoint (decisions.md 2026-08-11).",
      "keystone_residual_assumption": "Verified that two distinct heads exist; I am still assuming (a) their scores are not collapsed in practice (within-scan correlation must be checked and bounded at Stage 0 - if the heads are near-duplicates the contrast carries no information), and (b) TotalSegmentator lobar segmentation does not fail exactly where volume loss is largest - collapsed lobes are the known hard case for lobe tools, and this is the genuinely load-bearing assumption. Mitigation is prespecified: restrict primary analysis to mild-to-moderate volume loss with a fissure-completeness QC gate, and treat severe collapse as exploratory.",
      "rung_reached": "Rung 1 via the conditional contrast analysis. Rung 2 is unusually cheap here because the primary readout is within-scan (scanner, protocol, reconstruction, positioning, habitus all shared between the two head scores); the remaining rung-2 item is measurement validity of lobar volumetry in diseased lungs. Rung 3 is the same sentence as rung 1 since X is already the physician's own criterion.",
      "dies_like_prior": "Closest risk is USE_VS_ASSOCIATION. Difference: the readout is the within-scan two-head CONTRAST - every scan-level confound is differenced out by construction - and the main rival cue (opacity burden) is measured and conditioned on rather than left as an unnamed alternative. A representation-erasure upgrade (project the lobar-volume direction out of the shared embedding, watch the contrast collapse) is prespecified as phase 2 but not required for the screen. No annotation-provenance exposure: report-derived labels are used only for exploratory case enrichment, never in the primary readout.",
      "closest_prior_work": "Hamamci et al., CT-RATE/CT-CLIP (arXiv 2403.17834): built the model, reported per-label AUCs, never asked how any two labels are separated. npj Digital Medicine postoperative-atelectasis paper (s41746-026-02683-6): validates automated lobar volume-loss quantification as a measurement, does not connect it to any foundation model's decision. Draelos et al. RAD-ChestCT (DOI 10.1016/j.media.2020.101857, unverified-from-memory): multi-abnormality CT prediction, same silence on mechanism. Exact delta: nobody has tested whether a report-supervised chest-CT model's atelectasis/consolidation separation tracks the volumetric criterion that defines the distinction clinically.",
      "existing_assets": "Local, verified CT-CLIP inference pipeline from idea-004 (scripts, checkpoint hash procedure, bit-determinism check); CT-RATE validation-split inventory already characterized (3,039 volumes / 1,564 scans); TotalSegmentator public and verified to include lobe classes; published validation that lobar volumetry of atelectasis is measurable.",
      "smallest_decisive_experiment": "On ~300 CT-RATE validation scans enriched for report-labeled atelectasis and/or consolidation (enrichment only; labels not in the readout): compute per-scan head contrast (atelectasis minus consolidation logit), lobar volume-loss index, and opacity burden. Decision rule: partial association of contrast with volume-loss conditional on opacity burden, against a prespecified minimum effect. Positive = deliverable sentence at rung 1. Null with adequate power = the model does not use the radiologist's rule, which is a decisive and publishable negative for a deployed report-generation model.",
      "standing_confounds_addressed": "Scanner, vendor, protocol, reconstruction, site, positioning, habitus: all shared within scan, differenced out of the contrast. Prevalence/referral: affects the enrichment set's composition, not the within-scan readout; reported as scope limitation. Label leakage: no labels in the readout. NOT ruled out by design: cues that co-vary with volume loss inside the same scan (fissure shift, crowding - these are the volume-loss family and refine rather than refute X; air bronchograms - a consolidation-side cue that is genuinely distinct and is named as the open alternative).",
      "alternative_explanations": "(1) The model separates via air bronchograms or bronchial patency rather than volume - not excluded; named as the residual, and a bronchogram proxy (air-filled airway voxels inside opacity) can be added exploratorily; (2) heads are near-duplicates and the contrast is noise - Stage 0 gate; (3) TotalSegmentator errors correlate with collapse severity, manufacturing the association - handled by the QC gate and severity restriction.",
      "anticipated_negative": "Decisive: with the contrast design, adequate power, and a prespecified minimum effect, a null says the model's separation of these two labels does not use the criterion that defines them - a finding radiologists reading CT-CLIP-family reports would want to know.",
      "cross_domain": null,
      "remaining_legwork": "Volume download for the enriched subset (~300 scans, within established CT-RATE access); TotalSegmentator pass (GPU-days: ~1); head-correlation Stage 0 gate (hours, pipeline exists). First decision in roughly one week.",
      "design_template": "conditional-observational",
      "use_vs_association": "The within-scan two-head contrast differences out everything the scan shares; conditioning on measured opacity burden separates 'reads volume loss' from 'sees dense tissue'; the prespecified erasure arm upgrades the conditional association to a use claim if the screen is positive.",
      "dataset": "CT-RATE (validation split; established access and local pipeline).",
      "scores": {
        "clarity": {"value": 5, "reason": "One precise question, a named X that is the clinical definition itself, and a single prespecified decision rule."},
        "identifiability": {"value": 4, "reason": "Within-scan contrast is the strongest observational identification available; the air-bronchogram alternative and segmentation-error pathway keep it from 5."},
        "medical_relevance": {"value": 4, "reason": "Atelectasis-vs-consolidation drives different management (suction/bronchoscopy vs antibiotics); whether a deployed report generator makes the distinction for the right reason is directly consequential."},
        "interest": {"value": 4, "reason": "Either outcome informs the whole report-supervision paradigm: the model learned the physician's rule from text alone, or it fakes the distinction via co-occurrence."},
        "prior_legwork": {"value": 5, "reason": "The idea-004 pipeline, checkpoint verification, and dataset inventory already exist in this repo; the measurement tool is public and validated for this exact clinical problem."},
        "feasibility": {"value": 4, "reason": "Keystone INSPECTED_TRUE; the one real risk (lobe segmentation on collapse) has a prespecified mitigation and cheap Stage 0 check."},
        "data_readiness": {"value": 4, "reason": "CT-RATE is click-gated but program-established; volumes still need downloading."},
        "evaluation_readiness": {"value": 4, "reason": "Partial-association analysis with a minimum effect is standard; the fissure-QC gate needs definition."},
        "negative_result_value": {"value": 4, "reason": "Decisive under the powered contrast design; not 5 because the severe-collapse exclusion narrows the negative's scope."},
        "novelty_confidence": {"value": 3, "reason": "Limited search found measurement papers and model papers but not the connection; the space is active enough that 3 is the honest ceiling without a full audit."},
        "regret": {"value": 4, "reason": "The assets are sitting in this repo; if another group publishes it first with the same public pieces, that is a pure execution loss."}
      },
      "priority_score": 4.15,
      "unverified_claims": [
        "Draelos RAD-ChestCT DOI cited from memory.",
        "That atelectasis/consolidation label co-occurrence in CT-RATE leaves enough dissociated cases for enrichment (checkable from the released label CSVs before any download).",
        "That the two heads are not score-collapsed (Stage 0 gate).",
        "npj Digital Medicine atelectasis-volumetry paper seen via search snippet; full methods not read."
      ]
    },
    {
      "id": "scout-010-c03",
      "search_mode": "B",
      "entry_point": 2,
      "title": "Merlin's cirrhosis signal may be the spleen",
      "question": "Is Merlin's chronic-liver-disease score using splenic volume - congestive splenomegaly, the portal-pressure gauge - rather than the liver itself?",
      "rung": "Targets rung 1 (the model uses splenic volume in its liver-disease output). Rung 3 is close behind because splenomegaly is already the physician's word; rung 2 requires the non-hepatic-splenomegaly dissociation cases described below.",
      "deliverable_sentence": "Merlin is using splenic volume - congestive splenomegaly - in its chronic-liver-disease prediction.",
      "X_measurement": "Spleen volume from TotalSegmentator 'spleen' class (verbatim in map_to_binary.py, task 'total'; fetched 2026-08-12), in cm3. Competing liver-side signals measured in the same pass: liver volume, liver-to-spleen mean attenuation ratio, and liver-contour irregularity (surface-to-volume ratio of the TS liver mask as a nodularity proxy). Computable today on any abdominal CT without asking anyone: yes.",
      "suspected_signal": "Portal hypertension produces congestive splenomegaly; spleen volume is a validated correlate of cirrhosis severity and varices. A model trained with ICD-code supervision may have latched onto the spleen - a large, high-contrast, easily represented organ - rather than the subtler liver morphology a hepatologist would name.",
      "keystone_prerequisite": "The inference needs: a released Merlin output that produces a per-scan cirrhosis/chronic-liver-disease score on new abdominal CTs - either an exposed phecode-phenotype output or a zero-shot text-prompt score via the released image+text towers.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Supporting but not sufficient: huggingface.co/stanfordmimi/Merlin (fetched 2026-08-12) lists downloadable weights including 'i3_resnet_clinical_longformer_best_clip_04-02-2024_23-21-36_epoch_99.pt' (an image+text CLIP-style checkpoint), MIT license, with inference demos; the paper (arXiv 2406.06512) maps '16,553 ICD-9 and ICD-10 codes to 1,692 hierarchical phenotypes' via PheWAS Phecodes. NOT yet inspected: whether chronic liver disease is among the evaluable phenotypes with an exposed head, or whether zero-shot prompting is a documented usage mode producing calibrated-enough scores.",
      "keystone_residual_assumption": "Even after confirming a cirrhosis score exists, I am still assuming the score has enough dynamic range on public evaluation CTs (AMOS / TotalSegmentator-dataset populations are not hepatology cohorts; if almost no scan moves the score, the regression is uninformative). That prevalence-of-signal check is Stage 0 gate #2 and could be the real killer.",
      "rung_reached": "Rung 1 via conditional association plus dissociation cases. The rung-2 lever is specific and natural: splenomegaly WITHOUT liver disease (hematologic, thrombotic) versus cirrhotic-morphology liver WITHOUT splenomegaly - if the score follows the spleen in the first group, the model is using the spleen, not the liver.",
      "dies_like_prior": "Closest prior kill is DATA_ACCESS (idea-018, chewing muscle: required model/data not obtainable). Difference: Merlin weights are verified downloadable under MIT and evaluation CTs are public; the unverified piece is a single output-head question answerable in about an hour once weights are pulled, and it is declared as the keystone rather than assumed. USE_VS_ASSOCIATION is the second resemblance; the dissociation-case design is the stated answer.",
      "closest_prior_work": "Blankemeier et al., Merlin (arXiv 2406.06512): built and evaluated the model; no per-phenotype mechanism analysis. Backlog neighbors: scout-006-c03 (Merlin/diabetes/liver fat) and scout-008-c01 (cirrhosis model reading liver-edge bumpiness) - this candidate differs from both in X (spleen, not liver fat or liver edge) and in that it names the specific wrong-patient failure mode (non-hepatic splenomegaly) that makes the question clinically urgent. Spleen-volume-in-cirrhosis clinical literature is extensive (unverified specific citations; to be pinned in the idea card).",
      "existing_assets": "Merlin weights (MIT, HF, verified listed); TotalSegmentator (spleen class verified); AMOS 2022 and the public TotalSegmentator CT dataset (CC BY) as label-free evaluation cohorts; no annotation needed anywhere.",
      "smallest_decisive_experiment": "Run Merlin's liver-disease score and TotalSegmentator on ~500 public abdominal CTs. Decision: partial association of score with spleen volume conditional on liver volume, attenuation ratio, and contour irregularity - plus the dissociation read: in scans in the top spleen-volume decile with liver measures normal, does the score rise? Positive on both = deliverable at rung 1. Requires Stage 0 gates: (1) a usable cirrhosis output exists; (2) score dynamic range on public cohorts.",
      "standing_confounds_addressed": "Contrast phase: spleen VOLUME is phase-robust but the model's score may not be - analysis stratified by phase (phase classifiable from aortic/portal HU). Habitus: spleen scales with body size - normalize by an L3 body-cross-section from the same segmentation pass. Scanner/site: public multi-site cohorts, within-dataset analyses. Prevalence/referral: the readout is label-free, so cohort mix affects power, not validity. Label leakage: no labels used. NOT ruled out: liver texture the chosen liver measures miss (named as the open alternative - a positive spleen result does not exclude additional liver signal).",
      "alternative_explanations": "(1) Score tracks spleen only because spleen tracks unmeasured liver texture - partially addressed by the non-hepatic-splenomegaly dissociation cases, which break that path; (2) contrast-phase artifacts move both score and apparent organ boundaries - phase stratification; (3) low score dynamic range on healthy public cohorts makes everything null - Stage 0 gate, and the honest reason feasibility is capped.",
      "anticipated_negative": "Sensitivity-limited: a null needs a prespecified minimum detectable partial correlation and the dynamic-range gate passed; without those it is uninterpretable, and the card says so rather than promising a decisive negative it cannot deliver.",
      "cross_domain": null,
      "remaining_legwork": "Pull weights, answer the keystone (1 day); assemble public cohort + segmentation pass (2 days); association + dissociation analysis (2 days). First decision inside two weeks, with two explicit Stage 0 kill switches before any heavy compute.",
      "design_template": "conditional-observational",
      "use_vs_association": "Distinguishes use from correlation via natural wrong-cause cases: splenomegaly of non-hepatic origin. If the model's liver-disease score follows the spleen where the liver is normal, spleen size is being used, not merely correlated with liver disease.",
      "dataset": "Public abdominal CT (AMOS 2022, TotalSegmentator public dataset); Merlin checkpoint from HF.",
      "scores": {
        "clarity": {"value": 4, "reason": "Named X, named rival (liver morphology), named dissociation lever; slightly below 5 because 'chronic-liver-disease score' awaits the keystone's answer on which output exactly."},
        "identifiability": {"value": 3, "reason": "Spleen-liver collinearity is severe in true cirrhosis; identification rests on the non-hepatic-splenomegaly cases, whose frequency in public cohorts is unknown."},
        "medical_relevance": {"value": 4, "reason": "If the answer is spleen, Merlin-style opportunistic liver screening systematically misfires on hematologic and thrombotic splenomegaly - an actionable, testable deployment warning."},
        "interest": {"value": 4, "reason": "A foundation model reading the neighbor organ rather than the named one is exactly the program's motivating phenomenon."},
        "prior_legwork": {"value": 4, "reason": "Weights, tools, and cohorts exist and are open; no local pipeline for Merlin yet, unlike CT-CLIP."},
        "feasibility": {"value": 3, "reason": "Capped: keystone NOT_INSPECTED (which output exposes the score), plus the dynamic-range risk on healthy public cohorts."},
        "data_readiness": {"value": 4, "reason": "All public or MIT; nothing gated beyond HF click-through."},
        "evaluation_readiness": {"value": 3, "reason": "Partial-correlation framework is standard but the dissociation-case definition and phase stratification need custom, prespecified work."},
        "negative_result_value": {"value": 3, "reason": "Sensitivity-limited by construction; honest margin machinery is specified but a null will not kill the broader question."},
        "novelty_confidence": {"value": 3, "reason": "Capped by rule and by honesty: Merlin-mechanism work is young but moving fast; no full audit yet."},
        "regret": {"value": 3, "reason": "Worth doing while Merlin is the reference abdominal model; moderate regret if scooped since the assets are public."}
      },
      "priority_score": 3.5,
      "unverified_claims": [
        "That chronic liver disease / cirrhosis is among Merlin's evaluable phenotypes with >20 positives (paper subset criterion) - the keystone.",
        "That zero-shot text prompting is a supported Merlin usage mode.",
        "Spleen-volume/cirrhosis clinical correlation citations - from general knowledge, to be pinned to primary sources at idea-card stage.",
        "That AMOS/TotalSegmentator-dataset metadata suffice for phase stratification.",
        "TotalSegmentator paper DOI (10.1148/ryai.230024) cited from memory."
      ]
    },
    {
      "id": "scout-010-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The inferior vena cava as a manometer: does the chest model read venous pressure?",
      "question": "Are CT-CLIP's pleural-effusion and cardiomegaly heads using the distension and roundness of the intrahepatic inferior vena cava as a central-venous-pressure gauge?",
      "rung": "Targets rung 1 (the heads use IVC geometry). Rung 3 is unusually reachable for a Mode C because the X is already physician-named ('distended IVC', 'flat IVC') and mechanistically understood; what moves it up is the within-patient conditional analysis showing score movement with IVC geometry when fluid and heart size are held fixed.",
      "deliverable_sentence": "CT-CLIP is using the distension and roundness of the intrahepatic inferior vena cava - a central-venous-pressure gauge - in its pleural-effusion and cardiomegaly scores.",
      "X_measurement": "IVC cross-sectional area and flatness index (short/long axis ratio) on the axial slab between the diaphragm and the hepatic-vein confluence, from the TotalSegmentator 'inferior_vena_cava' class (verbatim in map_to_binary.py, task 'total'; fetched 2026-08-12). Both are established bedside quantities: the flat-IVC sign of hypovolemia and the ultrasound IVC distension/collapsibility index for right-atrial pressure (ASE guideline lineage; primary citations to be pinned). Computable today on any chest CT that includes the upper abdomen, without asking anyone: yes, if segmentation holds on non-contrast (see residual).",
      "suspected_signal": "Hydrostatics: the IVC is a thin-walled capacitance vessel whose cross-section and roundness track transmural pressure. Elevated right-heart pressure - the same physiology that produces transudative pleural effusions and cardiomegaly - distends and rounds it. Radiologists read this on ultrasound daily but rarely quantify it on chest CT; a report-supervised model exposed to thousands of heart-failure chests could have learned the gauge.",
      "keystone_prerequisite": "The inference needs: (a) the intrahepatic IVC is inside the CT-RATE field of view and segmentable on non-contrast volumes at usable reliability, and (b) enough patients have >=2 separate scan sessions for a within-patient design.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Parts inspected: repeat sessions exist - decisions.md (2026-08-04, directly inspected counts) records '3,039 validation volumes / 1,564 scans / 1,304 patients', implying ~260 extra scan-sessions in validation alone, with the far larger train split unexamined; TotalSegmentator includes 'inferior_vena_cava' (verbatim, map_to_binary.py). NOT inspected, and load-bearing: IVC in-FOV rate in CT-RATE and non-contrast IVC segmentation reliability (low vessel-liver contrast is exactly where it could fail).",
      "keystone_residual_assumption": "Having verified repeats exist and the tool has the class, I am still assuming the tool's IVC mask on NON-CONTRAST chest-CT bases is accurate enough that area/flatness changes are signal rather than segmentation noise. That is the real keystone; Stage 0 is therefore a 30-scan manual-free QC: test-retest IVC geometry across the idea-004 geometry-matched reconstruction pairs, which gives a segmentation noise floor WITHOUT any human annotation - the same self-comparison move that saved idea 004.",
      "rung_reached": "Rung 1 if within-patient score changes track IVC geometry changes conditional on measured effusion and heart size. The design borrows rung-2 strength from the within-patient structure (habitus, sex, site, referral fixed); the named residual is respiratory state, which is conditioned on via measured lung volume from the same segmentation pass.",
      "dies_like_prior": "Closest prior kill is idea-016 (contrast reflux as pressure gauge - IDENTIFIABILITY_FAILURE because reflux was inseparable from injection protocol). Difference: CT-RATE is non-contrast, so the entire injection-protocol axis is absent by construction; IVC geometry is anatomy, not contrast dynamics; and the within-patient longitudinal design removes the population covariates that idea-016 could not. The wrong-keystone error (charter, three occurrences) is guarded by naming segmentation-on-non-contrast as the real keystone rather than the easy adjacent facts already verified.",
      "closest_prior_work": "Idea-016's debate record (this repo) for the pressure-gauge framing and its failure mode. Clinical literature on CT IVC flatness/distension as volume-status markers (trauma flat-cava sign; unverified primary citations). CT-CLIP papers: no mechanism analysis of the effusion/cardiomegaly heads. No work found connecting a chest-CT foundation model's outputs to quantified IVC geometry - unverified negative, limited search.",
      "existing_assets": "The complete idea-004 apparatus: local CT-CLIP inference, checkpoint verification, geometry-matched reconstruction pairs (the free test-retest noise floor for BOTH the model scores and the IVC measurement), CT-RATE inventory with patient-level linkage ('split_patientID_scanID_reconstructionID' folder structure, HF dataset page). TotalSegmentator public.",
      "smallest_decisive_experiment": "Stage 0: IVC segmentation noise floor on 30 reconstruction pairs (no annotation needed). Then: identify patients with >=2 sessions (start with the ~200-260 in validation), compute within-patient deltas of effusion/cardiomegaly scores vs deltas of IVC area/flatness, conditional on delta-effusion-proxy (dependent pleural HU volume), delta-heart cross-section, and delta-lung volume (respiratory state). Decision: conditional within-patient association exceeding the reconstruction-pair noise floor. The most interesting prespecified cell: scans with NO visible effusion in either session, where a score-IVC association cannot be 'the model sees the fluid'.",
      "standing_confounds_addressed": "Habitus, sex, site, referral pathway, prevalence: fixed within patient. Scanner/protocol/reconstruction: CT-RATE repeats are same-center; reconstruction handled by using the idea-004 noise floor and matching kernels where possible. Positioning and respiratory state: the named residuals - respiration moves IVC caliber directly; conditioned via measured lung volume, and reported as the limiting alternative if conditioning is weak. Label leakage: no labels in the readout.",
      "alternative_explanations": "(1) Respiratory state drives both IVC caliber and apparent lung base appearance the model reads - the serious one; lung-volume conditioning is the answer and its adequacy is reportable; (2) segmentation noise on non-contrast manufactures or masks the effect - Stage 0 noise floor; (3) the model reads right-heart chamber enlargement directly and IVC merely co-varies - conditioning on heart cross-section addresses the crude version, and a positive should honestly be stated as 'venous-congestion geometry including the IVC' if heart conditioning is imperfect.",
      "anticipated_negative": "Sensitivity-limited, honestly: the within-patient n is modest and two noise floors (model score, segmentation) stack. The card inherits a real mitigation - the idea-004 reconstruction pairs quantify both floors before the main analysis, so the minimum detectable effect is estimable in advance rather than post hoc.",
      "cross_domain": "Borrowed construct: pressure-vessel mechanics / fluid statics - a compliant tube's cross-section is a transmural-pressure readout. The measurement it implies: IVC area plus roundness (not area alone - roundness is the pressurization signature). What would change if the analogy were dropped: there would be no reason to select IVC geometry as X at all, no prediction that ROUNDNESS carries signal beyond area, and no prediction that the association should persist in effusion-free scans (the gauge reads pressure before fluid appears). The analogy dictates the feature set, the direction, and the most interesting analysis cell; it is not decoration.",
      "remaining_legwork": "Stage 0 noise floor (2-3 days, assets local); repeat-session inventory of train split (1 day, metadata only); main within-patient analysis (3-4 days). Mode C: feasibility reported for information, not scored.",
      "design_template": "longitudinal-within-subject",
      "use_vs_association": "Within-patient change decouples the claim from every stable patient-level correlate; conditioning on measured fluid, heart size, and lung volume separates 'reads the venous gauge' from 'sees the effusion, which co-varies with the gauge'; the effusion-free cell makes the association impossible to attribute to visible fluid.",
      "dataset": "CT-RATE (repeat-session subset; second and final CT-RATE candidate this cycle).",
      "scores": {
        "mechanism_clarity": {"value": 5, "reason": "A specific physical quantity (transmural venous pressure) read through two named geometric measurements (IVC area, roundness), with the measurement that would show the model uses it fully specified."},
        "identifiability": {"value": 3, "reason": "Within-subject design plus conditioning is strong for an observational study, but respiratory state is a genuine common cause that conditioning may only partially remove."},
        "interest": {"value": 4, "reason": "A model quietly performing bedside hemodynamic assessment on every chest CT would be a genuinely new capability claim; a clean negative also matters for the 'foundation models read physiology' narrative."},
        "medical_relevance": {"value": 4, "reason": "If true, effusion/cardiomegaly scores partly encode volume status - both an explanation of false positives and a free hemodynamic signal clinicians do not currently get from chest CT."},
        "clarity": {"value": 4, "reason": "Precise X and design; slightly held back because the deliverable spans two heads and the claim may need narrowing to one."},
        "feasibility_info_only": {"value": 3, "reason": "Reported outside the Mode C score: assets are local and the design is cheap, but the non-contrast segmentation keystone is uninspected."},
        "novelty_confidence_info_only": {"value": 3, "reason": "Limited search found no model-IVC connection; capped and reported outside the score."}
      },
      "priority_score": 4.05,
      "priority_note": "Mode C weighting: 0.3*mechanism_clarity + 0.25*identifiability + 0.2*interest + 0.15*medical_relevance + 0.1*clarity = 1.5+0.75+0.8+0.6+0.4 = 4.05.",
      "unverified_claims": [
        "IVC in-FOV rate in CT-RATE volumes (keystone half a).",
        "Non-contrast IVC segmentation reliability of TotalSegmentator (keystone half b).",
        "Flat-cava / IVC-distension clinical citations from general knowledge; primary sources to be pinned.",
        "That train-split repeat sessions are numerous enough if validation's ~200-260 prove insufficient."
      ]
    },
    {
      "id": "scout-010-c05",
      "search_mode": "C",
      "entry_point": 2,
      "title": "Aortic tortuosity as a buckled column: is the hypertension head reading exceeded critical pressure?",
      "question": "Is Merlin's five-year hypertension prediction using abdominal aortic tortuosity - the buckled geometry of a chronically over-pressurized elastic tube - as its cue?",
      "rung": "Targets rung 1 (the model uses aortic tortuosity). Rung 2 hinges on separating tortuosity from age; rung 3 is available because 'tortuous aorta' is already a report phrase - the buckling frame adds the mechanism, not the vocabulary.",
      "deliverable_sentence": "Merlin is using abdominal aortic tortuosity - the buckled shape of a vessel whose critical buckling pressure has been exceeded - in its five-year hypertension prediction.",
      "X_measurement": "Tortuosity index = centerline arc length / straight-line chord of the abdominal aorta (diaphragmatic hiatus to bifurcation), centerline by skeletonization of the TotalSegmentator 'aorta' mask (verbatim class, map_to_binary.py; fetched 2026-08-12), plus undulation wavelength and amplitude from the centerline's curvature spectrum. Arterial tortuosity indices are established measurements (review literature in Hypertension; primary citations to be pinned). Computable today on any abdominal CT without asking anyone: yes.",
      "suspected_signal": "Elastic stability: a pressurized tube with axial pre-stretch buckles when transmural pressure exceeds a critical value set by wall stiffness and tethering; sustained hypertension plus elastin fragmentation lowers that threshold, and the buckled (tortuous) shape is permanent. Tortuosity is therefore a manometer with memory - a geometric record of chronic pressure load, distinct from the instantaneous pressure at scan time. Biomechanical theory: Han's artery-buckling work (J Vasc Res, circa 2012; to be pinned).",
      "keystone_prerequisite": "The inference needs: Merlin's released five-year disease-prediction assets include a hypertension output that can be run on new abdominal CTs.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "Two artifacts, both fetched 2026-08-12: (1) arXiv 2406.06512 (HTML full text) names the five-year targets verbatim: 'chronic kidney disease, osteoporosis, cardiovascular disease, ischemic heart disease, hypertension, and diabetes'; (2) huggingface.co/stanfordmimi/Merlin lists downloadable weights explicitly including 'Five Year Disease Prediction' alongside the main checkpoint, MIT license, with inference demos referenced.",
      "keystone_residual_assumption": "Having verified the head exists and its weights are listed, I am still assuming (a) the released five-year weights load and their output ordering/documentation identifies the hypertension logit, and (b) the evaluation cohort problem is solvable: separating tortuosity from AGE requires age metadata on public abdominal CTs, and whether AMOS or the TotalSegmentator dataset expose usable age fields is unverified. Assumption (b) is load-bearing for identifiability, not just convenience, and is Stage 0 gate #1.",
      "rung_reached": "Rung 1 via conditional association (score vs tortuosity, conditional on age, aortic diameter, and calcification burden). What moves it up is the buckling-specific signature: theory predicts onset nonlinearity and an undulation wavelength scaling with vessel radius - signatures that age-driven uniform elongation does not produce, giving the design a way to distinguish 'reads pressure-buckled geometry' from 'reads age'.",
      "dies_like_prior": "Dies, if it dies, exactly like idea-009 (Murray's law - IDENTIFIABILITY_FAILURE: the geometric quantity was inseparable from co-varying acquisition and population factors). Stated differences: tortuosity is a centimeter-scale, voxel-size-robust measurement where Murray exponents needed sub-voxel calibre precision; the dominant rival (age) is named up front with the design conditional on it rather than discovering the collinearity in debate; and the buckling wavelength signature provides a discriminating prediction Murray's-law candidate never had. If age metadata cannot be obtained, this candidate should be killed at Stage 0 for the same reason as idea-009 - the card says so explicitly.",
      "closest_prior_work": "Han HC, biomechanics of artery buckling (J Vasc Res ~2012, unverified from memory): theory and bench validation, never connected to a learned model. Clinical tortuosity-hypertension association literature (Hypertension review, unverified): establishes the correlation in humans, does not involve any imaging model. Merlin (arXiv 2406.06512): reports hypertension AUC, no mechanism. Exact delta: nobody has asked whether a CT foundation model's hypertension output is mediated by measured aortic geometry, nor tested buckling-theory signatures in a model's learned cue.",
      "existing_assets": "Merlin weights incl. five-year head (verified listed, MIT); TotalSegmentator aorta class (verified); public abdominal CT cohorts; established tortuosity metrics; buckling theory with quantitative predictions.",
      "smallest_decisive_experiment": "Stage 0: confirm the hypertension logit loads and identify a public cohort with age fields (kill if none). Then on ~500 public abdominal CTs: score vs tortuosity index conditional on age, aortic diameter, and calcification burden (calcium measured on the same clipped HU range noted in decisions.md 2026-08-10 if Merlin preprocessing clips similarly - check). Decision: conditional partial association with a prespecified minimum effect; exploratory second read: onset nonlinearity and radius-scaled wavelength as the buckling signature.",
      "standing_confounds_addressed": "Age: THE confound - conditioned on directly; candidate dies at Stage 0 without age metadata. Aortic calcification: measured and conditioned (the rival cue a model would plausibly use for hypertension). Scanner/site/protocol/reconstruction: geometry measurement is robust to kernel; within-dataset analyses. Habitus: weakly linked to tortuosity; body-cross-section covariate available from the same pass. Prevalence/referral/label leakage: label-free readout, unaffected.",
      "alternative_explanations": "(1) The model reads age (from bone, organs, everything) and age drives tortuosity - the design's central rival, handled by conditioning plus the buckling-signature analysis; residual confounding by age is the honest limit and is why identifiability is not scored higher; (2) the model reads aortic calcification which co-travels with tortuosity - measured and conditioned; (3) the model reads aortic diameter (ectasia) - measured, conditioned, and geometrically separable from tortuosity.",
      "anticipated_negative": "Sensitivity-limited: conditioning on age absorbs much of the real signal's variance, so a null needs the prespecified minimum-detectable-effect framework; a null on the buckling SIGNATURE with a positive plain association degrades gracefully to 'uses tortuosity, mechanism unresolved' and the card claims no more.",
      "cross_domain": "Borrowed construct: elastic stability / column buckling from structural engineering. The measurement it implies: not just a tortuosity index but its decomposition - onset nonlinearity in the score-tortuosity relation and undulation wavelength scaling with vessel radius, the fingerprints of a buckling instability. What would change if the analogy were dropped: the analysis would collapse to a linear score-vs-tortuosity regression; the theory is what licenses the wavelength and threshold analyses that can separate pressure-buckling from uniform age-related elongation. The analogy changes the experiment, so it stays.",
      "remaining_legwork": "Stage 0 gates (weights load + age metadata: 1-2 days); segmentation and centerline pipeline (2-3 days); analysis (2-3 days). Mode C: feasibility reported for information.",
      "design_template": "conditional-observational",
      "use_vs_association": "Distinguishes use from correlation by conditioning on the named common causes (age, diameter, calcification) and by the buckling-signature analysis: a model merely correlated with tortuosity through age should show neither onset nonlinearity nor radius-scaled wavelength dependence in its score response.",
      "dataset": "Public abdominal CT with age metadata (candidate cohorts: AMOS 2022, TotalSegmentator public dataset - metadata adequacy is Stage 0); Merlin checkpoint from HF. Second and final Merlin/public-abdominal candidate this cycle.",
      "scores": {
        "mechanism_clarity": {"value": 5, "reason": "A specific physical quantity (critical transmural buckling pressure of an elastic tube) with a specific geometric readout (tortuosity index plus wavelength scaling) and quantitative theory behind it."},
        "identifiability": {"value": 3, "reason": "Age collinearity is severe and conditioning is imperfect; the buckling signature is a genuine discriminator but exploratory - without it this would be a 2."},
        "interest": {"value": 4, "reason": "A learned model rediscovering an elastic-stability threshold would be a striking instance of the program's thesis; the wavelength test is the kind of analysis nobody runs on foundation models."},
        "medical_relevance": {"value": 3, "reason": "Opportunistic hypertension flagging from abdominal CT is plausible but not yet a clinical pathway; knowing the cue is tortuosity would matter mainly for trust and for vascular-aging research."},
        "clarity": {"value": 4, "reason": "Precise question and X; the two-layer claim (uses tortuosity; tortuosity is buckling) needs the card to keep the layers separate, which costs a point."},
        "feasibility_info_only": {"value": 3, "reason": "Reported outside the Mode C score: keystone inspected, but the age-metadata gate and centerline pipeline are real work."},
        "novelty_confidence_info_only": {"value": 3, "reason": "No audit yet; vascular-aging imaging is an active field and a tortuosity-model connection may exist somewhere."}
      },
      "priority_score": 3.9,
      "priority_note": "Mode C weighting: 0.3*5 + 0.25*3 + 0.2*4 + 0.15*3 + 0.1*4 = 1.5+0.75+0.8+0.45+0.4 = 3.9.",
      "unverified_claims": [
        "Han artery-buckling citation and Hypertension tortuosity review cited from memory - pin before idea card.",
        "Age metadata availability in AMOS / TotalSegmentator public dataset (Stage 0 gate).",
        "That the released five-year weights expose an identifiable hypertension logit.",
        "Whether Merlin preprocessing clips HU in a way that affects the calcification covariate (check per decisions.md 2026-08-10 side finding)."
      ]
    }
  ]
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

