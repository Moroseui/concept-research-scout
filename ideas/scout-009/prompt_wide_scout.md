You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-009
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

- **scout-007-c05** [NOVEL_VERIFIED, score 4.6, audited 2026-08-10] -- A lung-cancer model may be reading a mechanically remodeled trachea
- **scout-007-c07** [NOVEL_UNVERIFIED, score 4.3, audited 2026-08-10] -- The fibrosis model may be counting holes at the pleural edge
- **scout-006-c04** [NOVEL_UNVERIFIED, score 4.1, audited 2026-08-10] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-007-c06** [NOVEL_UNVERIFIED, score 3.9, audited 2026-08-10] -- The effusion model may be reading whether pleural fluid still obeys gravity
- **scout-008-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.9, audited 2026-08-11] -- The emphysema call may read the shape of the holes, not just how many
- **scout-008-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.9, audited 2026-08-11] -- The lung-cancer model may read the aorta as an ageing clock
- **scout-007-c08** [NOVEL_UNVERIFIED, score 3.6, audited 2026-08-10] -- The PE model may be reading how completely blood and contrast have mixed
- **scout-006-c05** [NOVEL_UNVERIFIED, score 3.4, audited 2026-08-10] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two
- **scout-007-c03** [NOVEL_UNVERIFIED, score 3.4, audited 2026-08-10] -- Merlin may be reading fatty kidney rather than kidney shape
- **scout-008-c02** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.1, audited 2026-08-11] -- The chest-CT model may see the heart by watching the airway splay
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


===== ideas/scout-009/README.md =====
# Scouting cycle 009

Tracks: baseline, wide, fiction


===== ideas/scout-009/run_provenance.json =====
{
  "timestamp": "2026-08-11T09:57:38+00:00",
  "git_commit": "ef71a4931bfec437b6904ea8c56d6843385eb2ad",
  "claude_cli": "2.1.197 (Claude Code)",
  "codex_cli": "codex-cli 0.147.0",
  "tracks": [
    "baseline",
    "wide",
    "fiction"
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
    "librarian.md": "3c5c129fe98b1717",
    "novelty_audit.md": "eb2b70b4159ab881",
    "probe_code.md": "766af76d5b22d687",
    "probe_plan.md": "51712f984817ef6b",
    "revise.md": "db7fab4a10c7c32b",
    "scout.md": "c5ae0f349d7a6d67",
    "wide_scout.md": "b21b441dba189d08"
  },
  "agents_toml_hash": "7e80bd12c967c003"
}


===== ideas/scout-009/scout_candidates.json =====
{
  "cycle": "scout-009",
  "stage": "scout",
  "generated_on": "2026-08-11",
  "tracks": ["baseline", "wide", "fiction"],
  "records_read": ["CHARTER.md", "docs/COLLABORATOR_RULES.md", "docs/SCORING_RUBRIC.md", "evidence/decisions.md", "evidence/ledger_digest.md", "evidence/portfolio_brief.md"],
  "evidence_note": "Primary papers, full-text methods where available, and official model repositories were used. NOT_INSPECTED means the load-bearing conjunction was not established even where adjacent facts were verified. No novelty claim is made; novelty confidence describes a bounded search only.",
  "all_questions": [
    {"n": 1, "question": "Is a chest-CT pulmonary-function model using Pi10, the standardized airway-wall thickness, when it predicts FEV1?", "status": "DEVELOPED as C1"},
    {"n": 2, "question": "Is Merlin using renal sinus fat fraction as a compressive metabolic cue when it predicts chronic kidney disease?", "status": "DEVELOPED as C2"},
    {"n": 3, "question": "Is a glioblastoma survival model using temporalis muscle thickness as a frailty cue rather than only tumor biology?", "status": "DEVELOPED as C3"},
    {"n": 4, "question": "Is Mirai using radial alignment of fibroglandular strands toward the nipple as a stromal-tension cue for future breast cancer?", "status": "DEVELOPED as C4"},
    {"n": 5, "question": "Is Sybil using vertebral marrow attenuation heterogeneity as an image signature of smoking-related marrow remodeling?", "status": "DEVELOPED as C5"},
    {"n": 6, "question": "Is a pulmonary-embolism outcome model using azygos-vein diameter as a venous-pressure gauge?", "status": "DROPPED", "why": "Azygos caliber is named and measurable, but contrast timing, respiration, and fluid status co-move with pressure so strongly that a positive perturbation would not identify venous pressure."},
    {"n": 7, "question": "Is a brain-age MRI model using choroid-plexus volume as an inflammaging clock?", "status": "DROPPED", "why": "Interesting named X, but ventricular volume is an overwhelmingly plausible co-edited alternative and a selective intervention is not yet credible."},
    {"n": 8, "question": "Is a kidney-stone composition model using internal lacunarity, borrowed from porous-material science, rather than mean stone attenuation?", "status": "DROPPED", "why": "The quantity is measurable, but voxel size and reconstruction dominate sub-voxel stone texture and no accessible fixed model was identified."},
    {"n": 9, "question": "Is a chest-radiograph sex classifier using clavicular cortical thickness as an androgen-linked skeletal cue?", "status": "DROPPED", "why": "This deliberately wrong-sounding question cannot yet separate cortical thickness from magnification, projection, and body size on a single radiograph."},
    {"n": 10, "question": "Is a liver-outcome CT model using portal-vein pulsatility encoded as alternating slice-to-slice caliber?", "status": "DROPPED", "why": "Routine helical CT does not sample a clean time series; the proposed measurement is more likely cardiac-motion artifact than physiology."}
  ],
  "generation_checklist": {
    "x_first": true,
    "ten_before_development": true,
    "outside_field_connections": [4, 5, 8],
    "obviously_wrong_but_not_immediately_refuted": 9,
    "radiologist_named_quantities": [1, 2, 3, 6, 7],
    "kill_codes_checked": ["IDENTIFIABILITY_FAILURE", "DATA_INSUFFICIENT", "DATA_ACCESS", "ANNOTATION_PROVENANCE", "CIRCULARITY", "USE_VS_ASSOCIATION"]
  },
  "quota_compliance": {"mode_A": 1, "mode_B": 2, "mode_C": 2, "radiology_or_CT": 5, "dermatology": 0, "maximum_per_dataset": 1, "revivals": 0, "quota_note": "All quotas met. No portfolio block had a verified new fact, so no revival was manufactured."},
  "candidates": [
    {
      "id": "C1", "parent_ids": [], "revival_basis": null, "search_mode": "A", "entry_point": 2,
      "design_template": "representation-erasure",
      "title": "The CT spirometer may be measuring remodeled airway walls",
      "question": "Is the Park et al. chest-CT pulmonary-function model using Pi10, the standardized airway-wall thickness, when it predicts FEV1?",
      "rung": {"target": 3, "current": 0, "move_up": "Validated selective erasure reaches rung 1; reconstruction/site replication gates rung 2; Pi10 supplies the named rung-3 vocabulary."},
      "deliverable_sentence": "The pulmonary-function model is using standardized airway-wall thickness (Pi10) as an image cue for airflow obstruction.",
      "X_measurement": {"X": "Pi10: the square root of airway wall area predicted for an airway with internal perimeter 10 mm.", "how": "Segment the airway tree, measure lumen and outer wall cross-sections orthogonal to branch centerlines, regress square-root wall area on internal perimeter, and evaluate at 10 mm. Automated airway/vessel morphometry was validated by Nardelli et al. (Med Image Anal 2020, arXiv:2002.05702).", "could_compute_today_without_asking_anyone": "Yes; it is a formula over automated airway masks and CT voxels, without reader labels."},
      "suspected_signal": "Chronic airway inflammation and remodeling thicken bronchial walls and narrow conducting airways, raising resistance and lowering FEV1.",
      "specific_artifact_confused_with_signal": "Sharp kernels, slice thickness, partial volume, and inspiration level alter apparent wall thickness.",
      "keystone_prerequisite": "The published Park pulmonary-function model (or a faithfully obtainable checkpoint) can be run on scans on which a Pi10 direction can be selectively removed without also erasing emphysema extent or lung volume.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Inspected primary methods/abstract: Park et al., Radiology 2023, DOI 10.1148/radiol.221488, PMID 36786699, trained on 16,148 same-day LDCT/spirometry examinations and reported test CCC 0.91 for FEV1. No public checkpoint or validated selective Pi10 erasure was established.",
      "keystone_residual_assumption": "The nearby verified fact is that CT predicts FEV1 and Pi10 is computable. I am still assuming the exact model is obtainable and that its Pi10 representation is separable from emphysema and lung size; that conjunction is the real keystone.",
      "rung_reached": "No rung yet; rung 1 requires a causal score change after validated selective erasure, rung 2 requires acquisition robustness, and rung 3 follows only if both hold.",
      "dies_like_prior": "It resembles idea-007 because respiratory state can change both airway caliber and framing. It differs by targeting fixed airway-wall remodeling and explicitly matching lung volume/inspiration; nevertheless preprocessing comparability remains a Stage-0 gate. Annotation provenance does not apply because Pi10 is voxel-computed.",
      "closest_prior_work": [
        {"citation": "Park et al., Deep Learning-based Approach to Predict Pulmonary Function at Chest CT", "identifier": "DOI 10.1148/radiol.221488; PMID 36786699", "verified_fact": "The CNN predicted FEV1 and FVC from LDCT.", "delta": "It did not establish that Pi10 was used."},
        {"citation": "Nardelli et al., Generative-based Airway and Vessel Morphology Quantification", "identifier": "arXiv:2002.05702", "verified_fact": "Automated cross-sectional airway wall and lumen measurements were related to Pi10 and FEV1%.", "delta": "It measured airways rather than decoding a pulmonary-function network."}
      ],
      "existing_assets": ["Published pulmonary-function architecture and cohort description", "Automated airway-tree and cross-sectional morphometry methods", "Accepted FEV1 and Pi10 endpoints"],
      "smallest_decisive_experiment": "First reproduce the frozen model. Fit a Pi10 probe on training data only, erase its validation-selected representation direction, and test paired FEV1-output change on an untouched test set while preserving total lung volume, emphysema percentage, airway count, and reconstruction strata. A matched random-direction erasure is the sham.",
      "use_vs_association": "A score-Pi10 correlation is exploratory; use requires a selective representation erasure that changes predicted FEV1 more than matched random erasures while leaving emphysema and volume decoding intact.",
      "standing_confounds_addressed": {"scanner_vendor_protocol_reconstruction_site": "Stratify and replicate; not ruled out at scout stage.", "positioning": "Match lung volume and supine position.", "habitus": "Adjust thoracic size and BMI where available.", "prevalence_referral": "Temporal external test helps but screening spectrum remains.", "label_leakage": "Same-day spirometry is not visible in the image/report; primary test is self-comparison."},
      "alternative_explanations": [
        {"alternative": "The erased direction is emphysema extent.", "resolution": "Require retained emphysema-percentage decoding and compare an emphysema-direction erasure."},
        {"alternative": "The model uses lung size/inspiration rather than wall thickness.", "resolution": "Match lung volume and require preserved lung-volume decoding."},
        {"alternative": "Kernel-dependent edge sharpness creates Pi10.", "resolution": "Kernel-stratified replication and within-kernel calibration; not fully excluded without multi-site data."}
      ],
      "anticipated_negative": {"classification": "sensitivity-limited", "reason": "A null erasure can reflect nonlinear or distributed encoding; it is decisive only after a preregistered probe-recovery floor."},
      "cross_domain": null,
      "remaining_legwork": "2 days to locate/verify checkpoint availability; 1 week for airway measurement and probe reliability; first go/no-go in 10 days.",
      "scores": {"clarity":{"value":5,"why":"One model output and one standardized measurement."},"identifiability":{"value":3,"why":"Selective erasure and retained-rival decoding address the main alternatives, but distributed encoding remains."},"medical_relevance":{"value":4,"why":"Would connect a black-box CT spirometer to airway remodeling."},"interest":{"value":4,"why":"Separates airway disease from the obvious lung-volume explanation."},"prior_legwork":{"value":4,"why":"Model study, endpoint, and airway measurement exist."},"feasibility":{"value":3,"why":"Capped because the runnable checkpoint/edit keystone is uninspected."},"data_readiness":{"value":2,"why":"The original cohort and checkpoint are not confirmed public."},"evaluation_readiness":{"value":4,"why":"FEV1, Pi10, and retained-decoding controls are defined."},"negative_result_value":{"value":2,"why":"Null is sensitivity-limited."},"novelty_confidence":{"value":3,"why":"Capped; bounded search found no causal Pi10 audit."},"regret":{"value":4,"why":"A modest audit could explain a high-performing physiological predictor."}},
      "priority_score": 3.4, "priority_arithmetic": "0.20*3 + 0.15*3 + 0.15*4 + 0.10*4 + 0.10*4 + 0.10*5 + 0.10*2 + 0.05*2 + 0.05*3 = 3.40",
      "unverified_claims": ["The Park checkpoint is obtainable", "Pi10 can be selectively erased", "No prior causal Pi10 audit exists"]
    },
    {
      "id": "C2", "parent_ids": [], "revival_basis": null, "search_mode": "B", "entry_point": 2,
      "design_template": "regional-substitution",
      "title": "The kidney model may be reading fat packed into the renal sinus",
      "question": "Is Merlin using renal sinus fat fraction as a compressive metabolic cue when it predicts chronic kidney disease?",
      "rung": {"target": 3, "current": 0, "move_up": "A renal-sinus-only substitution reaches rung 1; vendor/phase/site controls gate rung 2; renal sinus fat is already named for rung 3."},
      "deliverable_sentence": "Merlin is using renal sinus fat fraction as an image cue for chronic kidney disease.",
      "X_measurement": {"X": "Renal sinus fat volume divided by kidney volume.", "how": "Segment kidneys and renal sinus; classify fat voxels by calibrated CT attenuation (typically -190 to -30 HU), sum voxel volume, and normalize by kidney volume. Fujioka et al. used CT renal sinus fat volume in CKD (Clin Exp Nephrol 2023, DOI 10.1007/s10157-023-02350-0; PMID 37095344).", "could_compute_today_without_asking_anyone": "Yes; segmentation plus an HU threshold is independently executable on a new CT."},
      "suspected_signal": "Ectopic fat within the nonexpandable renal sinus may compress low-pressure veins and lymphatics and accompanies obesity, hypertension, and renal impairment.",
      "specific_artifact_confused_with_signal": "Contrast phase changes soft-tissue boundaries; thick slices and partial volume alter small sinus-fat pockets; visceral adiposity is the biological rival.",
      "keystone_prerequisite": "An obtainable Merlin CKD output and compatible abdominal CTs permit renal-sinus fat to be changed while preserving kidney parenchyma, collecting system, total visceral fat, and input distribution.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Inspected primary artifacts: Blankemeier et al., Nature 2026, DOI 10.1038/s41586-026-10181-8, PMID 41781626, reports 692 phenotypes and six 5-year chronic diseases; Fujioka et al. directly measured renal sinus fat in 56 CKD patients. The exact released CKD head and edit validity were not inspected.",
      "keystone_residual_assumption": "The easy facts are that Merlin predicts chronic disease and renal sinus fat is measurable. I am still assuming CKD is an exposed score and that a sinus-only tissue-for-tissue substitution can preserve surrounding anatomy and distribution; this is load-bearing.",
      "rung_reached": "No rung. A validated sinus-only substitution could reach rung 1; external protocol replication is required for rung 2 and hence the rung-3 sentence.",
      "dies_like_prior": "It resembles scout-006-c03 (Merlin diabetes/liver fat) but uses a different disease, organ compartment, and proposed compressive mechanism. It avoids association-only inference through sinus-only substitution and visceral-fat-matched controls. No annotation provenance is required.",
      "closest_prior_work": [
        {"citation":"Blankemeier et al., Merlin","identifier":"DOI 10.1038/s41586-026-10181-8; PMID 41781626","verified_fact":"Merlin was evaluated over 752 tasks including chronic-disease prediction.","delta":"The paper did not identify renal sinus fat as a CKD cue."},
        {"citation":"Fujioka et al., Prognostic impact of renal sinus fat accumulation in CKD","identifier":"DOI 10.1007/s10157-023-02350-0; PMID 37095344","verified_fact":"Normalized renal sinus fat was associated with hypertension and future eGFR decline in a small biopsy cohort.","delta":"It studied patient biology, not model use."}
      ],
      "existing_assets": ["Released Merlin code/models", "Whole-kidney segmentation tools", "HU-defined fat measurement", "Published CKD association"],
      "smallest_decisive_experiment": "On a frozen cohort, replace only renal-sinus fat voxels with anatomically registered, attenuation-matched sinus tissue from low-fat donors while holding kidney, perirenal fat, and total visceral fat fixed; compare paired CKD-score changes with equal-volume perirenal-fat and random-sinus shams.",
      "use_vs_association": "Observed CKD score versus sinus fat is exploratory. The use claim requires a dose-ordered paired response to sinus-only substitutions beyond perirenal and visceral-fat shams.",
      "standing_confounds_addressed": {"scanner_vendor_protocol_reconstruction_site":"Within-scan edits remove case-level factors; replicate by phase/vendor/site.","positioning":"Within-scan comparison largely rules it out.","habitus":"Hold total visceral and perirenal fat fixed; residual anatomy remains.","prevalence_referral":"Does not affect paired score change but limits generalization.","label_leakage":"No reports or CKD labels enter the primary paired readout."},
      "alternative_explanations": [
        {"alternative":"The model uses total visceral adiposity.","resolution":"Keep total fat constant and use equal-volume perirenal-fat controls."},
        {"alternative":"The edit disrupts renal-hilum anatomy.","resolution":"Registration, topology checks, discriminator equivalence, and random-sinus sham; remains the chief risk."},
        {"alternative":"Contrast phase, not fat, drives the score.","resolution":"Within-scan edit plus phase-stratified replication."}
      ],
      "anticipated_negative": {"classification":"sensitivity-limited","reason":"A null may mean failed realistic substitution; after edit-detectability and positive-control gates it becomes a meaningful rejection of appreciable use."},
      "cross_domain": {"borrowed_construct":"Fat packing in a constrained compartment from renal biomechanics.","measurement_implied":"Sinus-fat fraction normalized to kidney volume, not generic visceral fat.","if_analogy_dropped":"The experiment would measure general obesity; the packing mechanism dictates the confined renal-sinus compartment and perirenal-fat control."},
      "remaining_legwork":"1 day to inspect Merlin outputs; 3-5 days to test renal-sinus segmentation; about 2 weeks to validate substitutions.",
      "scores": {"clarity":{"value":5,"why":"Specific compartment, ratio, output, and intervention."},"identifiability":{"value":3,"why":"Within-scan compartment substitution separates general adiposity, but edit realism is uncertain."},"medical_relevance":{"value":4,"why":"Could expose an actionable ectopic-fat substrate of CKD prediction."},"interest":{"value":4,"why":"A kidney model reading fat inside the hilum is unexpected yet mechanistic."},"prior_legwork":{"value":3,"why":"Model and measurement exist; sinus segmentation/editing need work."},"feasibility":{"value":3,"why":"Capped; output and edit keystone uninspected."},"data_readiness":{"value":3,"why":"Merlin assets are released, compatible scoring cohort still needs audit."},"evaluation_readiness":{"value":3,"why":"X is defined but substitution validity metrics are custom."},"negative_result_value":{"value":2,"why":"Initially sensitivity-limited."},"novelty_confidence":{"value":3,"why":"Capped; no direct decoding study found in bounded search."},"regret":{"value":4,"why":"The compartment is routinely present and cheap to quantify."}},
      "priority_score": 3.35, "priority_arithmetic":"0.20*3 + 0.15*3 + 0.15*4 + 0.10*3 + 0.10*4 + 0.10*5 + 0.10*2 + 0.05*3 + 0.05*3 = 3.35",
      "unverified_claims":["Merlin exposes a CKD score", "A renal-sinus substitution can be in-distribution", "The effect is separable from total adiposity"]
    },
    {
      "id": "C3", "parent_ids": [], "revival_basis": null, "search_mode": "B", "entry_point": 2,
      "design_template": "longitudinal-within-subject",
      "title": "The brain-tumor prognosticator may be weighing the chewing muscle",
      "question": "Is a whole-head glioblastoma survival model using temporalis muscle thickness as a frailty cue rather than only tumor biology?",
      "rung": {"target":3,"current":0,"move_up":"Tumor-stable within-patient score tracking plus selective temporalis substitution reaches rung 1; acquisition/treatment controls gate rung 2; temporalis thickness provides rung 3."},
      "deliverable_sentence": "The glioblastoma survival model is using temporalis muscle thickness as an image marker of systemic frailty.",
      "X_measurement": {"X":"Bilateral temporalis muscle cross-sectional area and thickness on axial T1 MRI, normalized to cranial size.","how":"Automatically segment left and right temporalis at standardized orbital/temporal levels and compute area and maximum orthogonal thickness. A multi-dataset deep-learning implementation and prognostic validation were reported by Surov et al./Furtner-related work (Neurooncol Adv 2022, PMCID PMC8770629).","could_compute_today_without_asking_anyone":"Yes; an automated segmentation produces continuous geometry without a radiologist rating."},
      "suspected_signal":"Cancer cachexia, corticosteroid exposure, inactivity, and frailty reduce craniofacial skeletal muscle; whole-head models can see this extracranial tissue even when the tumor is stable.",
      "specific_artifact_confused_with_signal":"Head field-of-view cropping, coil bias, slice angulation, edema, and postsurgical change can alter apparent thickness or model framing.",
      "keystone_prerequisite":"A runnable whole-head survival model retains extracranial temporalis in its exact input tensor, and enough longitudinal MRIs have stable tumor burden but measurable temporalis change to separate frailty from tumor progression.",
      "keystone_status":"NOT_INSPECTED",
      "keystone_evidence":"Primary full text inspected: PMCID PMC8770629 reports automated temporalis segmentation across four datasets; GRASP, PMID 38285679, reports whole-brain post-radiotherapy MRI survival prediction. The exact GRASP preprocessing, checkpoint availability, and count of tumor-stable longitudinal pairs retaining temporalis were not established.",
      "keystone_residual_assumption":"The adjacent facts are that temporalis predicts prognosis and an MRI model predicts survival. I am still assuming the survival model actually sees extracranial muscle and an obtainable longitudinal subset decorrelates muscle loss from tumor change; that is the real keystone.",
      "rung_reached":"No rung; longitudinal association alone is insufficient. Rung 1 needs convergent within-subject and selective-substitution evidence.",
      "dies_like_prior":"No annotation-provenance failure applies because muscle geometry and tumor volume are automated. It risks the same use-versus-association error seen across early cycles, so longitudinal correlation is explicitly exploratory and regional substitution is required for the use claim.",
      "closest_prior_work":[
        {"citation":"Deep learning-based quantification of temporalis muscle has prognostic value in glioblastoma","identifier":"PMCID PMC8770629","verified_fact":"Automated temporalis quantification generalized across four datasets and was prognostic.","delta":"It did not test reliance by a whole-image survival model."},
        {"citation":"GRASP study","identifier":"PMID 38285679","verified_fact":"A whole-brain post-radiotherapy MRI model predicted glioblastoma survival.","delta":"It did not isolate extracranial muscle as a used signal."}
      ],
      "existing_assets":["Public brain-tumor MRI collections with serial imaging", "Automated tumor and temporalis segmentation methods", "Published survival-model recipes"],
      "smallest_decisive_experiment":"Freeze a survival model and identify serial scans with stable automated enhancing/nonenhancing tumor volume. Test whether score change tracks temporalis change, then substitute only extracranial temporalis patches between same-sequence scans with matched coil-field intensity. Require dose response, unchanged tumor embeddings, and null scalp/fat shams.",
      "use_vs_association":"The within-subject relationship is only triangulation; the use claim requires temporalis-only substitution to move survival score while brain/tumor tensors and tumor embeddings remain fixed.",
      "standing_confounds_addressed":{"scanner_vendor_protocol_reconstruction_site":"Same-sequence within-patient pairs and intensity-matched substitutions reduce them; coil/site replication remains.","positioning":"Rigid cranial registration and standardized planes.","habitus":"Within-subject design controls baseline habitus, not systemic treatment changes.","prevalence_referral":"Paired estimand is robust but GBM treatment cohort limits scope.","label_leakage":"No report text or survival label is used in the paired substitution readout."},
      "alternative_explanations":[
        {"alternative":"Tumor progression causes both score and wasting.","resolution":"Prespecified stable-tumor pairs plus tumor-fixed substitution."},
        {"alternative":"Steroid treatment changes both muscle and brain edema.","resolution":"Medication adjustment where available; substitution holds brain fixed but biological interpretation remains limited."},
        {"alternative":"The model responds to extracranial edit seams.","resolution":"Scalp/fat and left-right sham substitutions with distribution checks."}
      ],
      "anticipated_negative":{"classification":"sensitivity-limited","reason":"A null can reflect a tumor-cropped model or insufficient muscle change; becomes decisive only after confirmed visibility and positive-control sensitivity."},
      "cross_domain":null,
      "remaining_legwork":"2-3 days to inspect model input/preprocessing; 1 week for longitudinal pair counts; 2 weeks to first intervention result.",
      "scores":{"clarity":{"value":5,"why":"Named muscle metric and explicit whole-head outcome."},"identifiability":{"value":4,"why":"Tumor-fixed regional substitution directly separates muscle from tumor burden, subject to seam validity."},"medical_relevance":{"value":4,"why":"Would reveal frailty contamination or useful holistic prognostication."},"interest":{"value":4,"why":"A brain-tumor model using chewing muscle is surprising and clinically legible."},"prior_legwork":{"value":3,"why":"Both component literatures exist, but runnable convergence is unclear."},"feasibility":{"value":3,"why":"Capped; model visibility and longitudinal subset uninspected."},"data_readiness":{"value":2,"why":"Serial survival-linked MRI access and checkpoint need confirmation."},"evaluation_readiness":{"value":3,"why":"Muscle/tumor metrics exist; edit validation is custom."},"negative_result_value":{"value":2,"why":"Null is sensitivity-limited."},"novelty_confidence":{"value":3,"why":"Capped; bounded search found association studies but no use audit."},"regret":{"value":5,"why":"Extracranial tissue is easy to overlook and may dominate prognosis."}},
      "priority_score":3.45,"priority_arithmetic":"0.20*3 + 0.15*4 + 0.15*4 + 0.10*3 + 0.10*4 + 0.10*5 + 0.10*2 + 0.05*2 + 0.05*3 = 3.45",
      "unverified_claims":["An obtainable survival model retains temporalis", "Enough tumor-stable serial pairs exist", "Temporalis-only substitution can pass distribution checks"]
    },
    {
      "id":"C4","parent_ids":[],"revival_basis":null,"search_mode":"C","entry_point":2,
      "design_template":"model-output-perturbation",
      "title":"The risk model may be reading the breast's lines of force",
      "question":"Is Mirai using radial alignment of fibroglandular strands toward the nipple as a stromal-tension cue for future breast cancer?",
      "rung":{"target":3,"current":0,"move_up":"Orientation-selective perturbation reaches rung 1; vendor/compression replication gates rung 2; radial stromal alignment is the proposed rung-3 term."},
      "deliverable_sentence":"Mirai is using radial alignment of fibroglandular strands toward the nipple as an image marker of breast-cancer risk.",
      "X_measurement":{"X":"Radial alignment index: mean cosine-of-double-angle agreement between local ridge orientation and the pixel-to-nipple radial vector, within fibroglandular tissue.","how":"Segment breast and nipple, estimate ridge orientation using a multiscale Hessian/structure tensor, and average cos(2(delta angle)) weighted by ridge strength; compare with tangential and shuffled orientation controls.","could_compute_today_without_asking_anyone":"Yes; it is a deterministic image measurement requiring no semantic labels."},
      "suspected_signal":"Collagen and Cooper-ligament organization transmit mechanical tension through glandular tissue; persistent radial alignment could encode involution, stromal remodeling, or occult field effects before a mass is visible.",
      "specific_artifact_confused_with_signal":"Compression direction, pectoral edge, detector processing, view geometry, and nipple localization can manufacture radial line structure.",
      "keystone_prerequisite":"Radial alignment is reproducible across CC/MLO views and serial exams after controlling compression and detector processing, and can be perturbed without changing density, low-frequency anatomy, or creating line artifacts.",
      "keystone_status":"NOT_INSPECTED",
      "keystone_evidence":"Official Mirai repository inspected: https://github.com/reginabarzilaygroup/Mirai states released research code/model and external C-indices 0.76-0.81. Yala et al., J Clin Oncol 2022, 'Towards Robust Mammography-Based Models for Breast Cancer Risk' is the primary model report. No primary source establishing this radial-alignment keystone was found.",
      "keystone_residual_assumption":"The easy facts are that Mirai runs and mammographic texture predicts risk. I am still assuming radial orientation is a stable biological quantity rather than compression geometry and that an orientation-only edit is valid; that is the load-bearing keystone.",
      "rung_reached":"No rung. Because this is Mode C, a failed reproducibility gate is itself an early kill; only a validated orientation perturbation reaches rung 1.",
      "dies_like_prior":"It resembles idea-015 only by using Mirai; it does not revive BAC or vascular age and uses a different tensor-native measurement and mechanism. It avoids annotation provenance because alignment is computed, but could die by identifiability if compression cannot be separated from biology.",
      "closest_prior_work":[
        {"citation":"Yala et al., Towards Robust Mammography-Based Models for Breast Cancer Risk","identifier":"J Clin Oncol 2022; official repository https://github.com/reginabarzilaygroup/Mirai","verified_fact":"Mirai predicts 1-5-year risk and is released for research.","delta":"It did not name radial fibroglandular alignment."},
        {"citation":"Using Explainable AI to Characterize Features in Mirai","identifier":"DOI 10.1148/ryai.240417","verified_fact":"Feature-centric analysis linked Mirai features to calcifications, masses, and breast anatomy.","delta":"It did not causally test the defined radial-alignment index."},
        {"citation":"Automated percent density, texture variation, and breast cancer risk","identifier":"PMCID PMC8166859","verified_fact":"Automated texture variation contributed risk information beyond density.","delta":"It did not measure radial orientation or model reliance."}
      ],
      "existing_assets":["Released Mirai model", "Public mammograms sufficient for label-free score perturbation", "Structure-tensor and breast/nipple segmentation methods"],
      "smallest_decisive_experiment":"On frozen CC/MLO exams, phase-randomize only the high-frequency oriented fibroglandular component within local patches to reduce radial alignment while preserving power spectrum, density, breast outline, and nipple location. Compare Mirai risk change against tangentialized, orientation-shuffled, and fat-region shams; require consistent effects across both views and vendors.",
      "use_vs_association":"Risk-alignment correlation is not evidence of use. The claim requires dose-ordered Mirai score response to alignment-selective perturbation with density and spatial spectrum held fixed.",
      "standing_confounds_addressed":{"scanner_vendor_protocol_reconstruction_site":"Within-image perturbation holds them fixed; cross-vendor replication tests generality.","positioning":"CC/MLO concordance and nipple-relative coordinates; compression remains dangerous.","habitus":"Breast area and density held fixed.","prevalence_referral":"No labels needed for primary response; does not establish clinical causality.","label_leakage":"No reports or risk labels enter perturbation readout."},
      "alternative_explanations":[
        {"alternative":"Mirai reacts to generic high-frequency texture damage.","resolution":"Power-spectrum-matched tangential and shuffled controls."},
        {"alternative":"Radial alignment is compression geometry, not stroma.","resolution":"Cross-view/serial reproducibility and compression metadata where available; may remain fatal."},
        {"alternative":"The nipple detector leaks view position into X.","resolution":"Perturb nipple localization and repeat with independently defined breast centroid."}
      ],
      "anticipated_negative":{"classification":"decisive","reason":"If a powered, spectrum-preserving dose series changes X substantially but leaves Mirai risk within a prespecified equivalence margin, it directly weakens use of this X."},
      "cross_domain":{"borrowed_construct":"Principal stress-line alignment from soft-tissue mechanics and fiber-composite analysis.","measurement_implied":"A nipple-relative orientation order parameter, not generic texture entropy.","if_analogy_dropped":"The experiment would revert to undirected texture variation; the mechanics analogy uniquely dictates orientation, radial coordinates, and tangential controls."},
      "remaining_legwork":"3 days for repeatability screen; 1 week for perturbation validation; first decisive model result in about 2 weeks.",
      "mechanism_clarity":5,
      "scores":{"clarity":{"value":5,"why":"A formula, coordinate system, and perturbation are explicit."},"identifiability":{"value":3,"why":"Spectrum-matched controls isolate orientation, but compression may be inseparable."},"medical_relevance":{"value":3,"why":"Could reveal a preclinical stromal risk substrate, though biological interpretation is speculative."},"interest":{"value":5,"why":"A model reading tissue lines of force would be broadly compelling."},"prior_legwork":{"value":2,"why":"Model and texture tools exist; biological bridge is thin."},"feasibility":{"value":3,"why":"Capped; keystone not inspected."},"data_readiness":{"value":4,"why":"Primary readout needs only runnable Mirai and mammograms."},"evaluation_readiness":{"value":3,"why":"Alignment metric is defined but not standardized clinically."},"negative_result_value":{"value":5,"why":"A validated equivalence result is decisive for this X."},"novelty_confidence":{"value":3,"why":"Capped; bounded search only."},"regret":{"value":4,"why":"The experiment is inexpensive relative to the mechanism's interest."}},
      "priority_score":4.1,"priority_arithmetic":"Mode C: 0.30*5 + 0.25*3 + 0.20*5 + 0.15*3 + 0.10*5 = 4.10",
      "unverified_claims":["Radial alignment is biologically stable", "Orientation-only perturbations are in-distribution", "No prior study tested this exact X"]
    },
    {
      "id":"C5","parent_ids":[],"revival_basis":null,"search_mode":"C","entry_point":2,
      "design_template":"regional-substitution",
      "title":"The lung-cancer model may be reading the marrow as a smoking dosimeter",
      "question":"Is Sybil using vertebral marrow attenuation heterogeneity as an image signature of smoking-related marrow remodeling?",
      "rung":{"target":3,"current":0,"move_up":"Vertebra-only substitution reaches rung 1; reconstruction/site/smoking-stratum controls gate rung 2; marrow attenuation heterogeneity supplies rung 3."},
      "deliverable_sentence":"Sybil is using vertebral marrow attenuation heterogeneity as an image marker of smoking-related systemic remodeling.",
      "X_measurement":{"X":"Within-vertebral trabecular marrow HU distribution: median, interquartile range, and spatial variogram after excluding cortex, focal lesions, and vessels.","how":"Automatically segment T1-T12 vertebrae, erode cortex, exclude fracture/focal-lesion outliers, then compute calibrated HU histogram dispersion and a 3D semivariogram normalized by reconstruction noise.","could_compute_today_without_asking_anyone":"Yes; the measurement is fully specified over automated vertebral masks and CT voxels."},
      "suspected_signal":"Smoking, aging, inflammation, and altered hematopoiesis change marrow cellularity and fat conversion; the vertebral body could therefore carry a distributed exposure signature visible on LDCT.",
      "specific_artifact_confused_with_signal":"Kernel, dose, photon noise, beam hardening, vertebral level, osteoporosis, anemia, and occult metastasis all alter marrow HU heterogeneity.",
      "keystone_prerequisite":"After noise normalization and vertebral-level matching, marrow heterogeneity remains a reproducible patient property that can be substituted between LDCTs without changing bone cortex, reconstruction texture, or model input distribution.",
      "keystone_status":"NOT_INSPECTED",
      "keystone_evidence":"Primary Sybil full text inspected: Mikhael et al., J Clin Oncol 2023, DOI 10.1200/JCO.22.01345, PMCID PMC10419602, used whole-volume LDCT and no clinical variables, validated on 6,282 NLST, 8,821 MGH, and 12,280 CGMH scans. No primary evidence established the marrow-heterogeneity keystone or smoking mechanism.",
      "keystone_residual_assumption":"The verified nearby fact is that Sybil sees the whole CT and generalizes across cohorts. I am still assuming marrow texture exceeds reconstruction noise and that tissue substitution can isolate marrow from bone density and age; that is the real keystone.",
      "rung_reached":"No rung. Mode C Stage 0 first tests repeatability; rung 1 needs vertebra-only causal response, and the systemic-remodeling gloss waits for rung 2.",
      "dies_like_prior":"It resembles idea-011 in proposing a skeletal aging/exposure clock. It differs by using native within-marrow tissue substitution rather than deletion of mineralized cartilage, with cortex-preserving, level-matched donor tissue and explicit noise controls. It still dies if edit validity cannot be demonstrated. Annotation provenance does not apply.",
      "closest_prior_work":[
        {"citation":"Mikhael et al., Sybil","identifier":"DOI 10.1200/JCO.22.01345; PMCID PMC10419602","verified_fact":"Sybil predicts 1-6-year lung cancer risk from the entire LDCT without clinical variables.","delta":"It did not test vertebral marrow as a cue."},
        {"citation":"Auditing Sybil: Generative Interventional Attributions","identifier":"arXiv:2602.02560","verified_fact":"A 2026 preprint reports object-specific generative interventions and artifacts/radial bias.","delta":"The bounded search did not find a vertebral-marrow heterogeneity intervention; novelty remains unverified."}
      ],
      "existing_assets":["Released Sybil model", "TCIA/NLST application pathway and other LDCT cohorts", "Automated vertebral segmentation", "HU and noise measurements"],
      "smallest_decisive_experiment":"First estimate test-retest/reconstruction repeatability of marrow dispersion on same-acquisition pairs. If it passes, transplant eroded trabecular marrow texture between level-, sex-, age-, BMD-, and noise-matched vertebrae while leaving cortex and surrounding anatomy fixed. Test paired Sybil risk response against phase-scrambled same-HU, paraspinal-muscle, and cortical-bone shams.",
      "use_vs_association":"Smoking/marrow/risk correlations are exploratory only. Use requires a dose-ordered Sybil response to marrow-only substitution beyond noise- and HU-matched shams.",
      "standing_confounds_addressed":{"scanner_vendor_protocol_reconstruction_site":"Same-acquisition repeatability gate and within-image edits; cross-site replication remains required.","positioning":"Vertebral registration makes it minor.","habitus":"Match paraspinal muscle and body size; not fully ruled out.","prevalence_referral":"Paired response is label-free, but screening-cohort spectrum limits interpretation.","label_leakage":"No reports or outcomes enter primary substitution."},
      "alternative_explanations":[
        {"alternative":"Sybil uses osteoporosis/age rather than marrow remodeling.","resolution":"Match BMD, cortex, age and vertebral level; separately substitute mean HU versus spatial heterogeneity."},
        {"alternative":"It responds to reconstruction noise.","resolution":"Same-acquisition repeatability, local noise normalization, and noise-matched shams."},
        {"alternative":"Occult metastasis or focal lesion drives the signal.","resolution":"Automated focal-outlier exclusion and require diffuse multi-level consistency."}
      ],
      "anticipated_negative":{"classification":"decisive","reason":"If repeatability and substitution-sensitivity controls pass yet large marrow changes keep Sybil risk within an equivalence margin, appreciable use of this X is weakened."},
      "cross_domain":{"borrowed_construct":"A dosimeter/readout of cumulative exposure, borrowed from hematopoietic ecology and materials heterogeneity.","measurement_implied":"Diffuse level-normalized marrow HU dispersion and spatial correlation, not mean bone density.","if_analogy_dropped":"The experiment would test generic vertebral attenuation; the dosimeter idea dictates diffuse multilevel consistency, texture heterogeneity, and smoking-stratified validation."},
      "remaining_legwork":"3-5 days for repeatability on reconstruction pairs; 1 week for marrow masks/noise normalization; 2-3 weeks to first substitution result.",
      "mechanism_clarity":4,
      "scores":{"clarity":{"value":4,"why":"X and intervention are explicit, while the exact biological substrate remains composite."},"identifiability":{"value":3,"why":"Matching and component-wise substitution address age/BMD/noise, but marrow biology remains mixed."},"medical_relevance":{"value":4,"why":"Would reveal a systemic exposure cue behind cancer risk prediction."},"interest":{"value":5,"why":"A lung-risk model reading vertebral marrow would be genuinely surprising."},"prior_legwork":{"value":3,"why":"Model and vertebral tools exist; marrow validation is thin."},"feasibility":{"value":3,"why":"Capped; repeatability/edit keystone uninspected."},"data_readiness":{"value":3,"why":"Model is released; in-domain scans require an established access route."},"evaluation_readiness":{"value":3,"why":"HU/noise metrics are defined but no accepted marrow heterogeneity standard exists."},"negative_result_value":{"value":5,"why":"After repeatability gates, equivalence is decisive for this X."},"novelty_confidence":{"value":3,"why":"Capped; recent Sybil audits make novelty particularly uncertain."},"regret":{"value":4,"why":"Same-acquisition repeatability cheaply kills or licenses the idea."}},
      "priority_score":3.95,"priority_arithmetic":"Mode C: 0.30*4 + 0.25*3 + 0.20*5 + 0.15*4 + 0.10*4 = 3.95",
      "unverified_claims":["Marrow heterogeneity is repeatable on LDCT", "It reflects smoking-related remodeling", "Marrow substitution can be in-distribution", "No recent Sybil audit already tested it"]
    }
  ],
  "portfolio_ranking": [
    {"rank":1,"id":"C4","score":4.1,"reason":"Highest Mode C mechanism/interest and a cheap decisive negative, though compression identifiability is the kill gate."},
    {"rank":2,"id":"C5","score":3.95,"reason":"Surprising systemic signal with a cheap repeatability screen before harder edits."},
    {"rank":3,"id":"C3","score":3.45,"reason":"Strongest non-speculative identifiability through tumor-fixed regional substitution."},
    {"rank":4,"id":"C1","score":3.4,"reason":"Well-grounded unfinished story, limited by checkpoint access and distributed encoding."},
    {"rank":5,"id":"C2","score":3.35,"reason":"Mechanistically attractive but renal-hilum edit validity is harder than the score suggests."}
  ]
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

Write `wide_candidates.json` with the shape
`{"candidates": [...], "dropped": [{"question": "...", "why": "..."}]}`.
The `candidates` array contains ONLY the three fully developed candidates;
the one-line notes on dropped questions go under `dropped`, never as stub
entries in `candidates` (stubs are filtered out at merge and waste the slot).
Do not write code. Do not modify any other file.

## Design template (required field)

Set `design_template` to the experimental GRAMMAR of the candidate, one of:
natural-paired, cross-reconstruction, regional-removal,
regional-substitution, representation-erasure, counterfactual-synthesis,
conditional-observational, longitudinal-within-subject,
cross-model-disagreement, model-output-perturbation.
The digest counts these: homogenization is measured by repeated grammar,
not repeated nouns. Pick the closest; if truly none fits, use
`other:<short-name>` and justify it in the card.

