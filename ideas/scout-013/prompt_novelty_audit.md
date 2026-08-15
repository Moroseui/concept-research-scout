You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-013
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

**Canonical shape (mandatory):** emit each score in the `scores` object as
`{"value": N, "why": "..."}` — the key is `value`, never `score`. Omit
`keystone_evidence` entirely when there is none; never emit `null` for it.
Cards violating the shape are rejected at merge.

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


## 2026-08-12 - Probe 004 exit-7 root cause (evidence-quoted) and revision spec

Diagnostic on the frozen revision (deeca4d8) of validation_metadata.csv:
ConvolutionKernel values are stringified lists - value_counts shows
"['Br40f', '3']": 425 and "['Br60f', '3']": 239 - while run.py matches
row['ConvolutionKernel'].strip() == 'Br40f', which matches zero rows. World
matches Stage 0 (239 Br60f volumes ~ frozen 237 pairs); only the predicate
drifted. Revision requirements, and ONLY these: (1) normalize the kernel
field before comparison - if it parses as a Python list literal take element
0, else use the stripped raw string - then compare to Br40f/Br60f; robust to
both formats. (2) Diagnosability: on any selection shortfall vs the frozen
count, dump top-10 distinct kernel values with counts, example VolumeNames,
and per-filter drop counts to the run log AND selection_audit.json in the
output dir. (3) Record the normalized kernel per selected volume in
input_manifest.csv. Geometry list-string columns compare same-format
row-vs-row and need no change. No other scope.


## 2026-08-12 - Probe 004 exit-5 root cause (evidence-quoted): transformers pin, not the checkpoint

Load failed on exactly one unexpected key, "trained_model.text_transformer.
embeddings.position_ids". Transformers 4.31.0 changed BERT position_ids
from a persistent to a non-persistent buffer, so checkpoints saved under
<=4.30.x carry the key and models instantiated under >=4.31 do not expect
it. The released repo own transformer_maskgit/setup.py line 17 contains
the commented pin "#transformers==4.30.1" - the authors environment.
Verdict: environment-alignment failure, not a checkpoint/code
incompatibility; exit 5 is provisionally reclassified as environment-class
pending a run under the released pin. Revision, and ONLY this: in
probes/004/requirements.txt set transformers==4.30.1 and cascade
tokenizers to a compatible 0.13.x (4.30.1 requires tokenizers<0.14);
no run.py changes. Process note for the floor-study contract: an exit-5
load classification is only final after the released environment pin has
been tested - version-semantics mismatches must not masquerade as
checkpoint facts.


## 2026-08-12 - Probe 004 r5 environment dead end; r6 pivot to enumerated-key-tolerant load

The r5 pin (transformers 4.30.1 / tokenizers 0.13.3) is uninstallable on
Colab Python 3.12: tokenizers <0.14 ships no cp312 wheels and the Rust
source build fails (pip error captured 2026-08-12). Pinning backward to the
authors 2023 environment is not viable on current runtimes. Revision r6,
and ONLY this: (1) revert requirements.txt to the r4 closure that installed
cleanly twice (transformers 4.38.2 / tokenizers 0.15.2). (2) In run.py,
before load_state_dict, remove state-dict keys matching
*.embeddings.position_ids - the non-learnable arange buffer that
transformers 4.31 made non-persistent; this replicates from_pretrained
documented cross-era behavior. Strictness otherwise preserved: assert the
removed set is exactly one key matching that pattern, log the removed
key(s) to provenance.json and the run log, and any OTHER unexpected or
missing key still exits 5. (3) Startup logs the installed transformers
version. Exit-5 semantics update: a load is "unchanged" modulo enumerated,
provenance-logged framework-era buffer keys only.


## 2026-08-12 — Probe 004 contract v1 ADVANCE (load probe passed)

The authorized real A/B/A run satisfied every load-probe contract gate. The frozen
`CT_LiPro_v2.pt` artifact (SHA-256
`9246d9c8a7e2cedaa115719699229fe0acb02f19488e8bd1ad1eff5f47ff1d7d`)
loaded strictly under CT-CLIP commit `a2a155c601987820433c01db69b64d701d3d229d`,
modulo exactly the single r6-authorized and provenance-recorded
`trained_model.text_transformer.embeddings.position_ids` buffer key. The selected
Stage-0-valid Br40f|Br60f pair produced 18 finite named scores for A, B, and repeated
A; the A repeat was bit-identical. All three executions completed at batch size one
without patch-size changes in 0.250 GPU minutes with 4.10 GB peak memory, under the
45-minute cap. All authorized variants are reported in `ideas/004/decision.md`.

Scope: this demonstrates checkpoint/pipeline compatibility, output shape,
determinism, and bounded single-pair inference only. The one-pair A-versus-B score
differences are diagnostic and scientifically uninterpretable; they establish
nothing about reconstruction sensitivity, equivalence, accuracy, or concept
validity. No validity failure occurred. ADVANCE means only that a separate 425-pair
floor-study contract may now be drafted and submitted for fresh human approval; no
bulk inference is authorized by this decision.

## 2026-08-14 - AMENDMENT to 2026-08-11 pin 2: CT-Scroll demoted from tier-2 equivalence margin to benchmark context

Pin 2 required the tier-2 AUROC margin to be fixed from the CT-Scroll
(arXiv 2503.20652) PDF tables before any paired score is seen. External
review (2026-08-14) found the margin estimand mismatched: the CT-Scroll
headline table reportedly gives CT-RATE TEST-set results averaged across
18 labels, while this study analyzes the VALIDATION split per head. A
formal per-head equivalence margin derived from an aggregate spread on a
different split would be worse than honest description.

Amended pin 2: CT-Scroll supplies benchmark CONTEXT, not a margin.
Tier 2 is a purely descriptive secondary endpoint - per-head paired
delta-AUROC with patient-cluster bootstrap confidence intervals,
contextualized against published between-model differences on the same
benchmark. Contract v2 must contain ZERO threshold language for tier 2
(no "meaningful", "material", or numeric cutoffs), or an implicit margin
re-enters at interpretation time. Tier 2 measures benchmark
discrimination against the released report-derived labels of CT-RATE,
never clinical diagnostic accuracy.

The extraction stage (context memo, formerly margin memo) must verify
the split claim of the reviewer from the primary source with quoted
table and page identifiers - checker-mode applies to reviewers too - and
must state on the record that the v1 load probe exposed the per-head
diagnostic scores of one pair (declared uninterpretable in the v1
contract), and why this does not compromise tier 2: context numbers
derive solely from published CT-Scroll tables, and tier 1 is label-free.

All other 2026-08-11 pins stand unchanged. The equivalence-margin
wording in the idea-004 card is updated to match in the commit following
this ratification. Preregistration discipline preserved: the analysis is
still frozen before the 425 pairs are scored; what changed is that no
external number now plays a pass/fail role.

## 2026-08-14 - A1 revision spec r1 (context memo, idea 004)

Ratification review found one internal inconsistency. Revision scope,
and ONLY this: section 5, caveat 6 says "the three ViViT-free pairwise
gaps" and then lists six values (0.57, 1.53, 2.10, 0.33, 1.86, 2.43).
The word and the list disagree. Resolve the inconsistency: either the
count is wrong and should match the list, or the word "three" reflects
an intended narrower meaning, in which case state that meaning
explicitly so the sentence and the list agree on their own terms.
Whichever way it resolves, the resolution must be internally consistent
and the six gap values themselves must not change unless the resolution
gives a stated reason. No other content, number, or quote may be
altered. Re-run of the context-memo stage authorized for this revision
only.

## 2026-08-14 - A1 RATIFIED: CT-Scroll context memo (idea 004, r1)

The context memo at ideas/004/context_memo.md (git blob
6668a313ae83779ef2a74d1982dd287d504a7e0d) is ratified after spot-check
of the load-bearing quotes against arXiv 2503.20652 v6 and v1, an
arithmetic audit of all derived gaps, and review of the r1 diff, which
contained the specified section-5.6 resolution and nothing beyond it.

Frozen as benchmark context, version-pinned to arXiv v6 (v1 for volume
counts): five trained-model 18-label-averaged AUROC values (ViViT 79.19,
CT-Net 79.37, Swin3D 79.94, 3D CNN 81.47, CT-Scroll 81.80), max-min
spread 2.61, all ten pairwise gaps as tabulated. Context only; no number
carries pass/fail semantics anywhere (amended pin 2).

Findings of record: (1) the external reviewer was half right - label
averaging confirmed by quote; the different-split premise refuted at the
volume level, with the papers test set almost certainly the official
validation split relabeled (source-supported inference from the exact
3,039-volume match; mapping never stated in the paper). (2) Version
instability: the v1 table gives a 7.88 spread vs v6s 2.61 - threefold -
because the baseline set changed between revisions; retroactive
vindication of the pin-2 amendment. (3) v6-internal ViViT inconsistency
(Table 1: 79.19 vs Table 2: 73.19) recorded for the interpret stage.
(4) The 1,314-vs-1,304 patient bookkeeping discrepancy remains
unresolved and non-blocking. (5) The mandated exposure statement is
present and its no-margin-to-steer argument is accepted. (6) Revision
r1 was specified in decisions.md and executed by the stage, not by
hand; the artifact remains machine-produced end to end.

Contract v2 drafting is now authorized as the next stage, to begin once
the v2 contract-drafting machinery lands; the current probe-plan prompt
is not to be used for the floor study.

## 2026-08-14 - A2 flagged questions resolved (contract v2, idea 004)

Both open questions in the v2 draft are resolved as drafted. (1)
Two-phase approval adopted: phase-1 approval authorizes only the
metadata-only manifest freeze; recording the manifest hash and
unique-volume count amends the contract; the hash-bound gate treats
the phase-1 approval as stale by construction; phase-2 approval
against the amended blob authorizes bulk execution; bulk activity
while placeholders remain is invalidating. (2) The v1-exposed anchor
pair is excluded from all confirmatory statistics (236 counted
Br40f|Br60f pairs), per the exposure argument in the ratified memo.


===== evidence/ledger_digest.md =====
# Ledger digest (auto-generated -- do not edit; run `python scout.py ledger digest`)

71 tracked ideas. Latest state per idea; full history in ledger.jsonl.

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **DATA_ACCESS** x2: Required data, checkpoints, or mappings are not obtainable in practice.
- **IDENTIFIABILITY_FAILURE** x2: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.
- **ANNOTATION_PROVENANCE** x1: Inference depends on who assigned labels / what they could see, and that is undocumented or contaminated.
- **CIRCULARITY** x1: The endpoint is a re-encoding of the input or of the thing being tested.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **scout-012-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.1, audited 2026-08-15] -- The dilated esophagus inside the fibrosis score
- **scout-010-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.9, audited 2026-08-12] -- CXR-Age put back together from parts a radiologist can measure
- **scout-012-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.8, audited 2026-08-15] -- The race signal in chest CT: measure the bone density everyone names and nobody measured
- **scout-010-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.5, audited 2026-08-12] -- Merlin's cirrhosis signal may be the spleen
- **scout-011-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.3, audited 2026-08-13] -- Does Merlin read renal atrophy when it predicts future CKD?
- **scout-011-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.4, audited 2026-08-13] -- The air bronchogram as a topological cue
- **scout-010-c02** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.2, audited 2026-08-12] -- Atelectasis vs consolidation: has CT-CLIP learned the radiologist's volume-loss rule?
- **scout-006-c04** [NOVEL_UNVERIFIED, score 4.1, audited 2026-08-10] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-009-c08** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.1, audited 2026-08-11] -- The glioblastoma prognosticator may be reading the invasion front's roughness
- **scout-010-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.0, audited 2026-08-12] -- The inferior vena cava as a manometer: does the chest model read venous pressure?
- ... and 29 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- regional-substitution: 9
- conditional-observational: 8
- counterfactual-synthesis: 5
- representation-erasure: 3
- natural-paired: 3
- longitudinal-within-subject: 3
- model-output-perturbation: 2
- regional-removal: 1

## Ideas

- **idea-001** [REJECTED/DEBATED/baseline] -- Have lung nodule concept models been validated against radiologist opinion rather than against disease? -- killed: DATA_INSUFFICIENT -- data: {"primary": "LIDC-IDRI via The Cancer Imaging Archive", "license": "CC BY 3.0", 
- **idea-002** [PAUSED/DEBATED/baseline] -- Dermoscopic concepts predicted from non-dermoscopic photographs: genuine visibility or shortcut? -- data: {"primary": "Derm7pt paired clinical/dermoscopic images", "source": "github.com/
- **idea-003** [REJECTED/DEBATED/baseline] -- Does BI-RADS concept intervention survive realistic clinician behaviour, and does it beat simply reading the BI-RADS category? -- killed: DATA_ACCESS -- data: {"primary": "BUS-BRA (Zenodo 8231412, CC BY 4.0) for the external and baseline a
- **idea-004** [ACTIVE/PROBED/baseline] -- The free test-retest experiment already inside CT-RATE: duplicate reconstructions of the same acquisition
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
- **scout-011-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Name the bone phenotype hidden in a near-perfect hand-radiograph sex classifier
- **scout-011-c02** [SCOUT_ONLY/SCOUTED/baseline] -- Does Merlin read renal atrophy when it predicts future CKD?
- **scout-011-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Cephalization in 3D: decode CT-CLIP's pulmonary-edema score
- **scout-011-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The air bronchogram as a topological cue
- **scout-011-c05** [SCOUT_ONLY/SCOUTED/baseline] -- A pancreatic fat gauge inside Merlin's diabetes forecast
- **scout-012-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The race signal in chest CT: measure the bone density everyone names and nobody measured -- data: NLST (CDAS; same cohort the anchor paper trained on)
- **scout-012-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The dilated esophagus inside the fibrosis score -- data: CT-RATE (validation split; local inference pipeline already frozen and probe-verified)
- **scout-012-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin's COPD call may come from the lungs it wasn't asked to look at -- data: Public abdominal CT (AMOS 2022 / TotalSegmentator public dataset) + released Merlin checkpoint
- **scout-012-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The non-gated chest CT contains an ECG: heart rate written in motion banding -- data: CT-RATE (second and final CT-RATE candidate this cycle); TCIA gated collections only for validating the X-measurement
- **scout-012-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The prognosis model as a manometer: midline shift is pressure the skull wrote down -- data: Anchor model's cohort (single-institution + TRACK-TBI) - access is the declared rate-limiter; CQ500 (public, has MLS/mass-effect reads but no outcomes) for X-measurement development only
- **scout-013-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The vessel map inside the mosaic-attenuation score -- data: CT-RATE validation split
- **scout-013-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The open fissure inside lung-cancer risk -- data: NLST held-out scans scored by a reproduced or released Sybil model
- **scout-013-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Name the skeletal frailty inside mortality prediction -- data: Public chest-radiograph mortality anchor cohort if obtainable; external measurement development on MIMIC-CXR
- **scout-013-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The renal artery as a buckled pressure line -- data: Public contrast-enhanced abdominal CT compatible with released Merlin checkpoint
- **scout-013-c05** [SCOUT_ONLY/SCOUTED/baseline] -- Collateral failure written in the cortical veins -- data: Paired baseline NCCT and CTA/CTP or DWI stroke cohort from the anchor model; public CQ500 only for measurement robustness


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


===== ideas/scout-013/README.md =====
# Scouting cycle 013

Tracks: baseline


===== ideas/scout-013/candidates_all.json =====
{
  "cycle": 13,
  "tracks": [
    "baseline"
  ],
  "notes": {
    "mode_c_score_missing": 2
  },
  "candidates": [
    {
      "id": "scout-013-c01",
      "search_mode": "A",
      "entry_point": 2,
      "title": "The vessel map inside the mosaic-attenuation score",
      "question": "Does CT-CLIP's mosaic-attenuation score use regional pulmonary-vessel caliber contrast rather than attenuation heterogeneity alone?",
      "design_template": "regional-substitution",
      "dataset": "CT-RATE validation split",
      "entry_point_2_requirements": "Unexpected-signal measurement: within-lung correlation between local attenuation and local small-vessel volume, plus the difference in vessel caliber between matched lucent and dense regions. Confusable artifact: reconstruction kernel changes both apparent vessel caliber and texture; the primary intervention is within reconstruction and the established geometry-matched reconstruction pairs provide a sensitivity audit.",
      "rung": "Targets rung 1. It moves to rung 2 after reconstruction, protocol, and edit-validity controls; it reaches rung 3 only if vessel-caliber-preserving attenuation shams and attenuation-preserving vessel edits disagree in the predicted direction.",
      "deliverable_sentence": "The model's mosaic-attenuation score is using the regional reduction in pulmonary-vessel caliber within lucent lung.",
      "X_measurement": "Segment pulmonary vessels with a published automated vessel-segmentation method, skeletonize the tree, estimate local radius from the distance transform, and compute paired small-vessel volume density in locally lucent versus dense lung regions. Quantitative CT literature uses percent cross-sectional area of vessels below 5 mm2 (%CSA<5) and documents caliber differences in mosaic perfusion (Shahin et al., Pulmonary Circulation 2019, PMCID PMC6377046). Could it be computed on a new scan without asking anyone? YES, subject to a Stage-0 segmentation-quality gate.",
      "suspected_signal": "Occlusive pulmonary vascular disease produces hypoperfused, hypoattenuating secondary-lobule territories with fewer and narrower vessels; small-airway and infiltrative causes can produce similar attenuation patches but differ in vascular behavior. The model may have learned this radiologist-used discriminator from 3D context.",
      "use_vs_association": "Association is only the score-X curve. Use is tested by two factorial, within-scan edits: equalize vessel caliber across lucent/dense regions while preserving parenchymal HU, and equalize regional HU while preserving vessels. A selective score response to the first distinguishes vessel use from mere label correlation.",
      "keystone_prerequisite": "The released CT-CLIP v2 checkpoint exposes a stable, per-volume Mosaic attenuation pattern score on CT-RATE through a runnable deterministic pipeline.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "probes/004/run.py lines 226-244 include \"Mosaic attenuation pattern\" in EXPECTED_PATHOLOGIES; evidence/decisions.md (2026-08-12 load-probe decision) records 18 finite named scores, bit-identical A repeat, and the frozen checkpoint SHA-256 9246d9c8a7e2cedaa115719699229fe0acb02f19488e8bd1ad1eff5f47ff1d7d.",
      "keystone_residual_assumption": "The nearest verified fact is that the head runs. Still assumed, and load-bearing for interpretation, is that a vessel segmenter resolves peripheral caliber after CT-CLIP's 1.5-mm resampling and that localized caliber edits can be made without detectable nonvascular texture artifacts. Stage 0 must inspect both; otherwise this becomes association-only.",
      "rung_reached": "1 if the factorial intervention passes sham and realism gates; 2 after paired reconstruction sensitivity and acquisition-stratified replication; 3 is the deliverable sentence, conditional on those gates.",
      "dies_like_prior": "It inherits idea-006's OOD-intervention risk, but differs because anatomy is not deleted and the edit is localized, factorial, and sham-matched. It does not depend on annotation provenance: the primary endpoint is a score difference on the same scan. It also checks DATA_ACCESS (checkpoint already load-probed), DATA_INSUFFICIENT (Stage-0 support count), IDENTIFIABILITY_FAILURE (factorial edits), and CIRCULARITY (vessel caliber is not the mosaic label definition alone).",
      "closest_prior_work": "Hamamci et al., CT-CLIP/CT-RATE, arXiv:2403.17834, released the model and benchmark but did not decode this head. Shahin et al. quantified vessels, bronchi, emphysema, and mosaic attenuation across severe PH groups (PMCID PMC6377046) but did not study model behavior. The exact delta is a model-use intervention on vessel-caliber contrast.",
      "existing_assets": "Frozen CT-CLIP checkpoint and verified inference lineage; CT-RATE validation volumes and 425 geometry-matched reconstruction pairs; TotalSegmentator lung masks; published quantitative-vessel formulas.",
      "smallest_decisive_experiment": "Stage 0 on 30 scans: demonstrate stable peripheral vessel masks and enough cases with strong attenuation-vessel contrast. Then on 60 high-X scans, run preregistered A/B factorial edits plus equal-volume vessel-adjacent shams, reporting per-scan score deltas and edit discriminability. Confirmatory set is frozen before model scores are read.",
      "standing_confounds_addressed": "Scanner/vendor, site, protocol, reconstruction, positioning, and habitus are fixed within each edited scan. Reconstruction sensitivity is separately measured on geometry-matched pairs. Prevalence and referral pathway cannot create a within-image score delta. Report-label leakage may explain why the cue was learned but not the paired use result. Not ruled out: vessel editing may alter adjacent parenchymal texture; factorial and sham controls target but may not eliminate this.",
      "alternative_explanations": "(1) The model uses attenuation patches, not vessels: ruled out if attenuation-preserving vessel edits move the score and vessel-preserving HU edits do not. (2) It uses generic high-frequency edit artifacts: tested with equal-boundary shams and an edit detector. (3) Both features are jointly required: a factorial interaction is explicitly estimated and would narrow, not support, the simple sentence.",
      "anticipated_negative": "Decisive only if segmenter and edit-realism gates pass: score equivalence to a sham-derived margin under vessel equalization, while the model remains responsive to an attenuation positive control, weakens the vessel-use hypothesis. Gate failure is uninterpretable, not a negative.",
      "cross_domain": null,
      "remaining_legwork": "Vessel-tool selection and 30-case validation: 4-6 days; edit-realism pilot: about one week; first scientific decision: roughly 2-3 weeks on one GPU.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "One head, one quantitative vessel contrast, and a factorial test."
        },
        "identifiability": {
          "value": 4,
          "why": "Factorial edits separate vessels from attenuation, with residual edit-artifact risk."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Names whether a model applies a clinically important vascular discriminator."
        },
        "interest": {
          "value": 4,
          "why": "Turns a generic texture label into pulmonary perfusion anatomy."
        },
        "prior_legwork": {
          "value": 4,
          "why": "Model, data, inference, and quantitative measurement literature exist."
        },
        "feasibility": {
          "value": 4,
          "why": "Keystone inspected; vessel editing is the remaining substantial task."
        },
        "data_readiness": {
          "value": 5,
          "why": "CT-RATE pipeline and checkpoint are already verified locally."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "Paired factorial deltas and established vessel metrics are ready."
        },
        "negative_result_value": {
          "value": 4,
          "why": "Conditional on gates, the negative excludes a named discriminator."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Closest-work delta was checked, but no exhaustive interpretability search was completed."
        },
        "regret": {
          "value": 4,
          "why": "A direct, tractable decoding experiment on a verified head."
        }
      },
      "priority_score": 4.25,
      "unverified_claims": [
        "A validated vessel model performs adequately after CT-CLIP preprocessing.",
        "The required caliber edit can pass an image-realism discriminator.",
        "CT-RATE contains at least 60 scans with strong measurable mosaic vessel contrast."
      ],
      "track": "baseline"
    },
    {
      "id": "scout-013-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The open fissure inside lung-cancer risk",
      "question": "Does Sybil's lung-cancer risk score use incomplete interlobar fissures, independently of emphysema burden and nodule appearance?",
      "design_template": "conditional-observational",
      "dataset": "NLST held-out scans scored by a reproduced or released Sybil model",
      "entry_point_2_requirements": "Measurement: fissure completeness percentage from automated lobe/fissure segmentation. Confusable artifact: thick-slice reconstruction makes fissures appear incomplete and also degrades nodules; slice thickness and kernel must be exact-matched or conditioned.",
      "rung": "Reaches rung 1 only as a probe-plus-conditional-disagreement study; moves toward 2 with site/protocol matching; moves to 3 only after an in-distribution fissure-completion intervention or a natural longitudinal contrast.",
      "deliverable_sentence": "The lung-cancer risk model is using interlobar fissure incompleteness.",
      "X_measurement": "Fissure completeness is the proportion of the ideal lobar boundary occupied by visible fissure, computed from automated lobe masks and a fissure-enhancement/segmentation network; it is already used quantitatively for bronchoscopic lung-volume-reduction planning. Could it be computed today on a new scan without asking anyone? YES in principle with published automated CT fissure methods, but the exact maintained tool must be selected in Stage 0.",
      "suspected_signal": "Incomplete fissures permit collateral ventilation and may organize how emphysema and smoke injury spread across lobes. A longitudinal risk model could use this developmental lung architecture as a stable susceptibility marker rather than merely count present nodules.",
      "use_vs_association": "A raw correlation is insufficient. The smallest use evidence is cross-model disagreement plus representation probing: among scans exactly matched on nodule burden, emphysema %, age, smoking, and reconstruction, test whether Sybil-minus-nodule-model residual risk is predictable from fissure completeness on a frozen test set. This is still rung 1, not causal use; a validated fissure edit is required for the stronger claim.",
      "keystone_prerequisite": "An obtainable Sybil evaluation cohort retains enough variation in fissure completeness within exact reconstruction and emphysema/nodule strata to identify an independent fissure signal.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The easy adjacent facts are that NLST contains Sybil scans and automated lobe segmentation exists. Still assumed is the load-bearing joint support: fissure completeness is not nearly deterministic from emphysema, sex, slice thickness, or site. This is the idea-017 lesson and must be a metadata-only Stage-0 gate.",
      "rung_reached": "1 if frozen residual-risk and representation tests agree; 2 needs external/site replication; 3 requires a natural or validated counterfactual fissure contrast.",
      "dies_like_prior": "Most resembles idea-009 and idea-017: a beautiful anatomical measure may be inseparable from covariates. It differs only by making adequate joint support a kill gate before scoring. It avoids annotation provenance and label leakage in the primary score-to-X readout, but DATA_ACCESS to Sybil outputs and IDENTIFIABILITY_FAILURE remain live risks.",
      "closest_prior_work": "Mikhael et al., Sybil, J Clin Oncol 2023, DOI 10.1200/JCO.22.01345, established future lung-cancer prediction from one LDCT. Quantitative fissure completeness work supports the measurement, but I found no primary study connecting fissure completeness to Sybil or another lung-cancer risk representation. Absence is not proof of novelty.",
      "existing_assets": "NLST imaging and metadata through CDAS; published Sybil architecture/results; automated lobe segmentation; established emphysema percentage and nodule detectors.",
      "smallest_decisive_experiment": "Before model access, freeze 300 NLST scans with adequate overlap across fissure-completeness quartiles after exact matching on sex, smoking, emphysema %, nodule volume, slice thickness, kernel, and site. If support passes, compare fissure predictability of Sybil residual risk against a nodule-only model on untouched patients.",
      "standing_confounds_addressed": "Exact/propensity matching addresses site, scanner, protocol, reconstruction, sex, habitus proxies, smoking, and emphysema. NLST limits referral heterogeneity but does not erase it. Outcome prevalence is handled through frozen sampling. Report leakage is irrelevant to Sybil's future cancer endpoint. Residual unmeasured COPD severity and developmental anatomy remain.",
      "alternative_explanations": "(1) Fissure score is a slice-thickness artifact: exact reconstruction matching. (2) It proxies emphysema distribution: condition on global and lobar emphysema. (3) It proxies missed juxtapleural nodules: condition on nodule detector outputs and test nodule-free scans. None proves causal use; the card states that limitation.",
      "anticipated_negative": "Decisive for an independent observational signal only if joint support and measurement reliability pass and an equivalence margin is fixed; it is not decisive against causal use because a model may encode fissures nonlinearly.",
      "cross_domain": null,
      "remaining_legwork": "CDAS variable/file inspection and model-access check: 1-2 weeks; fissure tool benchmark: one week; first support decision before GPU inference: about 2 weeks.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "Named X and model; the residual-risk estimand needs careful explanation."
        },
        "identifiability": {
          "value": 2,
          "why": "Conditional observational evidence cannot prove use and joint support may fail."
        },
        "medical_relevance": {
          "value": 3,
          "why": "Could name a stable susceptibility phenotype, but clinical consequence is indirect."
        },
        "interest": {
          "value": 4,
          "why": "Developmental lung architecture as cancer-risk signal is unexpected."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Model and measurement literature exist; no joined pipeline is in hand."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped by NOT_INSPECTED and model/data access is unresolved."
        },
        "data_readiness": {
          "value": 2,
          "why": "NLST is gated and Sybil outputs/weights are not confirmed locally."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Matching and residual comparisons are standard, intervention is absent."
        },
        "negative_result_value": {
          "value": 3,
          "why": "Can decisively reject an independent fissure contribution under adequate support."
        },
        "novelty_confidence": {
          "value": 2,
          "why": "Limited search and keystone uninspected."
        },
        "regret": {
          "value": 3,
          "why": "Worth screening, but identification ceiling is real."
        }
      },
      "priority_score": 2.9,
      "unverified_claims": [
        "A maintained automated fissure-completeness tool is directly runnable on NLST.",
        "Sybil weights or per-scan outputs are obtainable.",
        "Adequate covariate overlap exists."
      ],
      "track": "baseline"
    },
    {
      "id": "scout-013-c03",
      "search_mode": "B",
      "entry_point": 1,
      "title": "Name the skeletal frailty inside mortality prediction",
      "question": "Does a chest-radiograph mortality model use vertebral compression-fracture burden as a named skeletal frailty signal?",
      "design_template": "regional-substitution",
      "dataset": "Public chest-radiograph mortality anchor cohort if obtainable; external measurement development on MIMIC-CXR",
      "rung": "Targets rung 1 through vertebral-region intervention, rung 2 through site/device replication, and rung 3 if morphometry-specific edits outperform matched texture shams.",
      "deliverable_sentence": "The mortality model is using vertebral compression-fracture burden.",
      "X_measurement": "Automated Genant-like vertebral morphometry from lateral or frontal radiographs: vertebral height ratios, wedge angle, and count of bodies exceeding prespecified deformity thresholds, using an automated spine/vertebral detector. Could it be computed on an unseen image without asking anyone? YES for a validated automated pipeline; applicability to frontal-only films is the Stage-0 measurement gate.",
      "suspected_signal": "Compression deformities integrate osteoporosis, falls, glucocorticoid exposure, malignancy, and frailty. Mortality models may exploit this cumulative skeletal history even when radiologists judging short-term image findings do not name it.",
      "use_vs_association": "Use is tested by replacing only vertebral-body shapes with age/sex/device-matched normal morphometry while preserving surrounding image statistics, compared with boundary-matched sham warps. Association with mortality or score is secondary.",
      "keystone_prerequisite": "The anchor mortality model and a test cohort with images and outcome horizon are obtainable for score-level intervention, rather than only published aggregate results.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearby verified literature fact is that chest-radiograph mortality prediction exists and radiologists can judge some mortality gestalt. Still assumed is the real keystone: scoreable images plus the exact model are obtainable. A re-trained substitute changes the claim and must be registered as such.",
      "rung_reached": "1 if morphometry edits selectively shift risk; 2 with external device/site replication; 3 is the stated named phenotype after edit validity.",
      "dies_like_prior": "Closest is idea-018 (DATA_ACCESS): an attractive prognosis model without obtainable weights/data. This candidate does not yet dodge it and may die immediately; that is why feasibility is capped and Stage 0 begins with asset inspection. Annotation provenance is irrelevant to the automated X and paired primary readout; CIRCULARITY is avoided because compression fracture is not the mortality label.",
      "closest_prior_work": "Lu et al., Scientific Reports 2021, PMCID PMC8486799, compared radiologist mortality gestalt with a deep model; other primary chest-radiograph longevity models establish the output. They did not measure or intervene on vertebral compression burden. Exact model artifact availability remains unverified.",
      "existing_assets": "Large public radiograph corpora, automated vertebral detection literature, and standard morphometric formulas. The required anchor artifact is not yet an asset.",
      "smallest_decisive_experiment": "Stage 0 is binary: obtain the exact model and linkable test images. Then validate automated morphometry on a small public labeled spine set; on 100 high-deformity anchor images run normalizing warps and matched sham warps, with risk-score delta as the label-free primary endpoint.",
      "standing_confounds_addressed": "Within-image edits fix site, device, protocol, positioning, habitus, prevalence, and referral pathway. Label leakage from reports is absent for mortality supervision. External replication addresses device/site. Remaining threat is that warps alter global projection geometry or reveal an editing signature.",
      "alternative_explanations": "(1) Model reads age-correlated aortic/rib features: fixed by localized edit. (2) It responds to warp artifacts: boundary/area-matched shams and edit detector. (3) Apparent compression on frontal images is rotation/positioning: exclude large rotation and validate repeatability.",
      "anticipated_negative": "Decisive only after model access, reliable morphometry, and sham-equivalent edits: then no score movement excludes compression burden above the prespecified detectable effect. Asset or measurement failure is uninterpretable.",
      "cross_domain": null,
      "remaining_legwork": "Asset audit: 1-2 days; likely author contact or rejection if unavailable; morphometry validation and edit pilot: 2-3 weeks after access.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "A familiar named lesion and direct paired intervention."
        },
        "identifiability": {
          "value": 4,
          "why": "Localized morphometry normalization can isolate X if shams pass."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Would turn opaque mortality gestalt into actionable skeletal frailty."
        },
        "interest": {
          "value": 4,
          "why": "Plausible, clinically legible, and one experiment beyond existing mortality work."
        },
        "prior_legwork": {
          "value": 2,
          "why": "Published anchor exists but executable artifact is unconfirmed."
        },
        "feasibility": {
          "value": 2,
          "why": "DATA_ACCESS may kill it and keystone is uninspected."
        },
        "data_readiness": {
          "value": 2,
          "why": "Development data are public; decisive anchor data/model are unconfirmed."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Morphometry and paired deltas are clear, edit validity custom."
        },
        "negative_result_value": {
          "value": 4,
          "why": "After gates, it decisively removes a concrete mortality explanation."
        },
        "novelty_confidence": {
          "value": 2,
          "why": "Limited search and cap applies."
        },
        "regret": {
          "value": 3,
          "why": "High value if assets exist, low cost to screen."
        }
      },
      "priority_score": 3.25,
      "unverified_claims": [
        "The exact anchor model is obtainable.",
        "Frontal-radiograph vertebral compression burden can be measured with adequate reliability.",
        "Localized shape normalization can be made in-distribution."
      ],
      "track": "baseline"
    },
    {
      "id": "scout-013-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The renal artery as a buckled pressure line",
      "question": "Does Merlin's hypertension phenotype use renal-artery tortuosity as an image-written history of chronic pressure and vascular remodeling?",
      "design_template": "conditional-observational",
      "dataset": "Public contrast-enhanced abdominal CT compatible with released Merlin checkpoint",
      "entry_point_2_requirements": "Measurement: renal-artery centerline tortuosity, curvature, and length/chord ratio from automated vessel segmentation. Confusable artifact: respiratory phase and oblique reconstruction change apparent curvature; compute in physical 3D coordinates and stratify contrast phase/protocol.",
      "rung": "Targets rung 1 as a frozen representation/score probe; moves up through natural longitudinal scans or a validated vessel-shape counterfactual.",
      "deliverable_sentence": "The model's hypertension score is using renal-artery tortuosity.",
      "X_measurement": "Segment the main renal arteries on contrast CT, extract centerlines, and compute arc-length/chord ratio plus integrated absolute curvature in mm-based coordinates. These are standard vessel-tortuosity formulas. Could it be computed today without an annotator? YES on suitable contrast CT, contingent on selecting a validated renal-artery segmenter.",
      "suspected_signal": "Chronic pressure, atherosclerotic remodeling, and tethered-vessel mechanics can lengthen a vessel relative to its endpoints, forcing curvature. A model supervised by diagnosis codes may exploit this stable vascular geometry rather than transient image appearance.",
      "use_vs_association": "The first experiment distinguishes association from representation use by testing whether tortuosity predicts the frozen hypertension logit and a linear probe of Merlin embeddings after conditioning on age, aortic calcium, renal volume, and phase. It cannot prove causal use; a natural paired or validated straightening intervention is explicitly required for rung 3.",
      "keystone_prerequisite": "A public, Merlin-compatible cohort contains contrast-enhanced arterial/portal-venous scans with renal arteries sufficiently visible and enough hypertension-score variance.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The easy fact is that Merlin weights and phenotype heads are public (Blankemeier et al., arXiv:2406.06512). Still assumed is the load-bearing imaging support: public scans both match preprocessing and show the renal arteries well enough. Without it, vessel tortuosity is measurement noise.",
      "rung_reached": "1 at most from score/representation dependence; 2 needs phase/site robustness; 3 needs a natural within-patient pressure change or credible shape edit.",
      "dies_like_prior": "It resembles scout-010-c05's aortic-tortuosity idea and idea-009's IDENTIFIABILITY_FAILURE. This is not a revival and does not claim novelty over that backlog grammar; the renal artery is a new, organ-specific hypothesis but may be too correlated with age/atherosclerosis. Annotation provenance does not enter the primary readout. DATA_ACCESS is reduced by public Merlin weights but cohort suitability is unverified.",
      "closest_prior_work": "Blankemeier et al., Merlin, arXiv:2406.06512, provides phenotype prediction and public weights but no anatomical decoding of hypertension. Vascular-tortuosity literature motivates the measurement; no verified primary study was found linking renal-artery tortuosity to Merlin. Novelty is explicitly low-confidence.",
      "existing_assets": "Released Merlin weights and single-GPU inference; public abdominal CT collections; centerline tortuosity formulas; TotalSegmentator for kidneys/aorta but not necessarily renal arteries.",
      "smallest_decisive_experiment": "Stage 0: inspect 50 candidate public scans and require prespecified renal-artery visibility/segmentation repeatability and hypertension-logit variance. Freeze 200 scans, compute tortuosity, and test incremental prediction of the logit beyond age proxy, aortic calcium, kidney volume, contrast phase, and scanner.",
      "standing_confounds_addressed": "Protocol/reconstruction/site/vendor enter stratified models; 3D physical coordinates reduce positioning artifacts; habitus and kidney size are conditioned. Disease prevalence/referral and diagnosis-code leakage remain population-level explanations for why the model learned the feature and are not eliminated. No report label is used in the primary analysis.",
      "alternative_explanations": "(1) Tortuosity proxies age/atherosclerosis: condition on automated aortic calcium and aortic tortuosity, but residual confounding remains. (2) Contrast timing drives segmentation and score: phase stratification and repeatability gate. (3) The model uses adjacent renal morphology: kidney volume/cortical thickness conditioning. A positive remains rung 1.",
      "anticipated_negative": "Sensitivity-limited: a null may reflect segmentation noise, restricted public-cohort range, or nonlinear encoding. Only a tightly powered equivalence result after repeatability gates would weaken the hypothesis.",
      "cross_domain": {
        "borrowed_construct": "Elastic-column buckling: a lengthening tethered vessel accommodates excess length by curvature.",
        "implied_measurement": "Arc-length/chord ratio and integrated curvature, compared with endpoint distance and vessel caliber.",
        "what_changes_if_dropped": "Without buckling mechanics the study becomes a generic radiomics correlation and loses the prespecified joint prediction that tortuosity should rise with excess centerline length at fixed endpoints; that interaction is the mechanism check."
      },
      "remaining_legwork": "Public-cohort and segmenter audit: about one week; 50-case repeatability gate: one week; first model result: 2-3 weeks.",
      "scores": {
        "mechanism_clarity": {
          "value": 4,
          "why": "Specific vessel geometry and formula; biological specificity remains uncertain."
        },
        "identifiability": {
          "value": 2,
          "why": "Age and atherosclerosis are powerful inseparable alternatives without intervention."
        },
        "interest": {
          "value": 3,
          "why": "Readable but shares a tortuosity grammar already in the backlog."
        },
        "medical_relevance": {
          "value": 3,
          "why": "Could explain a hypertension code, with modest direct consequence."
        },
        "clarity": {
          "value": 4,
          "why": "One model output and one quantitative X."
        },
        "feasibility": {
          "value": 3,
          "why": "Informational, capped by NOT_INSPECTED."
        },
        "data_readiness": {
          "value": 2,
          "why": "Weights are public; compatible vascular imaging is unconfirmed."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Standard tortuosity metrics, custom conditioning."
        },
        "negative_result_value": {
          "value": 2,
          "why": "Classified sensitivity-limited."
        },
        "novelty_confidence": {
          "value": 2,
          "why": "Limited search and close backlog analogue."
        },
        "regret": {
          "value": 2,
          "why": "Mechanistically neat but not a portfolio priority."
        }
      },
      "priority_score": 3.15,
      "priority_note": "Mode C: 0.30*4 + 0.25*2 + 0.20*3 + 0.15*3 + 0.10*4 = 3.15.",
      "unverified_claims": [
        "A suitable public contrast cohort is Merlin-compatible.",
        "Renal-artery segmentation is reliable at routine portal-venous timing.",
        "Renal-artery tortuosity has independent support beyond age and atherosclerosis."
      ],
      "track": "baseline"
    },
    {
      "id": "scout-013-c05",
      "search_mode": "C",
      "entry_point": 1,
      "title": "Collateral failure written in the cortical veins",
      "question": "Does an NCCT model that estimates early infarct use hemispheric cortical-vein density asymmetry as a hydraulic readout of collateral failure?",
      "design_template": "natural-paired",
      "dataset": "Paired baseline NCCT and CTA/CTP or DWI stroke cohort from the anchor model; public CQ500 only for measurement robustness",
      "rung": "Targets rung 1 using within-head hemispheric asymmetry and model disagreement; moves to rung 2 with scanner/protocol matching; rung 3 needs CTA/CTP collateral validation and a natural recanalization or serial-CT contrast.",
      "deliverable_sentence": "The infarct model is using reduced cortical-vein density in the affected hemisphere as a sign of collateral failure.",
      "X_measurement": "Register a reflected contralateral hemisphere, enhance tubular hyperdense structures in the cortical subarachnoid space with a multiscale vesselness filter, and compute affected/unaffected cortical-vein volume and mean HU ratios after excluding calcification and arteries by atlas/trajectory. Could it be computed today without an annotator? YES as a well-defined measurement, but whether NCCT distinguishes veins reliably is the keystone gate.",
      "suspected_signal": "In low-flow ischemia, delayed venous filling, deoxygenation-related attenuation changes, and reduced perfused blood volume could create a hemispheric venous-density asymmetry. A model trained against DWI infarct may exploit this diffuse vascular consequence when early parenchymal hypoattenuation is below human visibility.",
      "use_vs_association": "The within-head asymmetry is associated with the model's infarct map, but use requires a natural-paired test: among patients with baseline and short-interval post-recanalization NCCT at matched acquisition, ask whether vein asymmetry and model-estimated infarct change together while established infarct tissue cannot reverse. Without such pairs the result remains rung 1 association, not causal use.",
      "keystone_prerequisite": "Routine baseline NCCT contains a reproducible cortical-vein asymmetry that agrees directionally with independently measured collateral status or perfusion delay in the same patients.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearby verified fact is that NCCT models can estimate DWI infarct and outperform expert early reads (primary full text PMCID PMC9814956). Still assumed is the real keystone: the proposed venous measurement is physically present and separable from arteries, beam hardening, and hematocrit on routine NCCT. Phase 1 tests X before touching the model.",
      "rung_reached": "1 if X validates against collateral/perfusion imaging and predicts model output beyond parenchymal HU; 2 after acquisition robustness; 3 after natural paired support.",
      "dies_like_prior": "It risks idea-009 IDENTIFIABILITY_FAILURE because venous asymmetry covaries with the infarct itself, and idea-018 DATA_ACCESS because the exact model cohort may be unavailable. It differs by requiring independent CTA/CTP validation of X first and by using the contralateral hemisphere as a within-patient control. Annotation provenance is not used. The model-use claim remains deliberately conditional.",
      "closest_prior_work": "The NCCT-to-DWI infarct model in Radiology/Stroke imaging literature (PMCID PMC9814956) used 3,566 NCCT/MRI pairs and compared against expert neuroradiologists. Hyperdense cortical veins and venous signs have been studied diagnostically, but I did not verify a study decoding an infarct network with automated hemispheric cortical-vein density. This gap is search-limited.",
      "existing_assets": "Published anchor method; standard vesselness filters and symmetry registration; stroke cohorts often contain CTA/CTP/DWI, though access to the anchor cohort/model is unconfirmed.",
      "smallest_decisive_experiment": "Phase 1, independent of the model: on 50 NCCT cases with CTA/CTP collateral or Tmax maps, preregister direction and test repeatability of cortical-vein asymmetry. Stop if it fails. Phase 2 only with access: regress model infarct probability on vein asymmetry conditional on mirrored parenchymal HU and lesion volume; reserve serial post-recanalization pairs as confirmation.",
      "standing_confounds_addressed": "Within-head ratios control scanner, vendor, protocol, reconstruction, site, habitus, referral, and prevalence at the primary measurement level. Positioning and beam hardening may be asymmetric and require skull-base exclusion and mirrored sham regions. Hematocrit is systemic and cancels approximately within patient. Label leakage is impossible in image-only inference. Side-of-occlusion prevalence and true parenchymal injury remain coupled.",
      "alternative_explanations": "(1) Vesselness detects arteries or calcification: CTA registration and atlas exclusions test this. (2) Asymmetry is beam hardening or head rotation: reflected sham territories and superior-convexity restriction. (3) The model reads subtle parenchymal edema that also reduces vessel conspicuity: conditioning on mirrored HU cannot fully separate it; natural recanalization is the upgrade.",
      "anticipated_negative": "Decisive at Phase 1 for the physical mechanism if NCCT asymmetry has prespecified poor repeatability and no agreement with perfusion/collateral status. A Phase-2 null after Phase-1 success is sensitivity-limited unless the anchor model and effect margin are fixed.",
      "cross_domain": {
        "borrowed_construct": "Watershed hydraulics: downstream venous appearance integrates upstream inflow and collateral resistance across a vascular territory.",
        "implied_measurement": "Territory-level cortical-vein volume/HU asymmetry compared with perfusion delay, not generic image texture.",
        "what_changes_if_dropped": "Without hydraulics there is no prediction that venous asymmetry should track Tmax/collateral grade before it tracks irreversible DWI volume; that ordered validation is the reason Phase 1 exists."
      },
      "remaining_legwork": "Identify a genuinely accessible paired NCCT/CTA/CTP cohort and inspect schema: 1-2 weeks; measurement pilot: 1-2 weeks; model access may be terminal.",
      "scores": {
        "mechanism_clarity": {
          "value": 5,
          "why": "Named hemodynamic quantity, spatial measurement, and independent validation modality."
        },
        "identifiability": {
          "value": 3,
          "why": "Within-head control and perfusion validation help, but edema remains coupled."
        },
        "interest": {
          "value": 5,
          "why": "A hidden vascular signal could explain genuine model-over-reader early infarct performance."
        },
        "medical_relevance": {
          "value": 5,
          "why": "Early infarct extent directly affects acute stroke treatment."
        },
        "clarity": {
          "value": 4,
          "why": "Precise, though arterial/venous separation complicates X."
        },
        "feasibility": {
          "value": 2,
          "why": "Informational and capped; paired data/model access is uncertain."
        },
        "data_readiness": {
          "value": 1,
          "why": "No confirmed accessible linked cohort or checkpoint."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Collateral/perfusion validation is standard; NCCT measurement is custom."
        },
        "negative_result_value": {
          "value": 4,
          "why": "Phase 1 can decisively kill the proposed physical signal."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped and search-limited despite a precise checked delta."
        },
        "regret": {
          "value": 4,
          "why": "High-payoff mechanism worth a cheap physics-first screen."
        }
      },
      "priority_score": 4.4,
      "priority_note": "Mode C: 0.30*5 + 0.25*3 + 0.20*5 + 0.15*5 + 0.10*4 = 4.40.",
      "unverified_claims": [
        "Cortical veins are reproducibly separable on routine NCCT.",
        "Venous-density asymmetry tracks collateral failure in the proposed direction.",
        "The anchor model or per-case scores and linked multimodal data are obtainable."
      ],
      "track": "baseline"
    }
  ]
}


===== ideas/scout-013/run_provenance.json =====
{
  "timestamp": "2026-08-15T06:20:32+00:00",
  "git_commit": "382fbac2c84ff0ede1bcdae1b44a341ca74a36f4",
  "claude_cli": "2.1.197 (Claude Code)",
  "codex_cli": "codex-cli 0.147.0",
  "tracks": [
    "baseline"
  ],
  "seed_concepts": null,
  "prompt_hashes": {
    "actioner.md": "263f5cce53cb0cee",
    "context_memo.md": "4de103654cef2380",
    "critique.md": "5c8ed5c43071eaeb",
    "debate_critic.md": "74f1e299e3c6db50",
    "debate_proposer.md": "6a41797dbc73796a",
    "debate_summary.md": "7243fe771e1f612d",
    "feasibility.md": "48f4f111abfcd1eb",
    "fiction_extract.md": "8ada1a395c25072e",
    "fiction_refine.md": "ab92bb6c46fe0fbb",
    "fiction_scout.md": "63b11687055c8624",
    "interpret.md": "053a89726b66b8b4",
    "keystone_screen.md": "f6f206ca8577b47b",
    "librarian.md": "3c5c129fe98b1717",
    "novelty_audit.md": "eb2b70b4159ab881",
    "probe_code.md": "bc0c52c94d1af371",
    "probe_plan.md": "6249699cb2278e0e",
    "probe_review.md": "6b222a3f766009ea",
    "revise.md": "db7fab4a10c7c32b",
    "scout.md": "c5ae0f349d7a6d67",
    "wide_scout.md": "b21b441dba189d08"
  },
  "agents_toml_hash": "4b0d0da9640a634d"
}


===== ideas/scout-013/scout_candidates.json =====
{
  "cycle": "scout-013",
  "date": "2026-08-15",
  "track": "baseline",
  "quota_note": "Quotas met: 1 Mode A, 2 Mode B, 2 Mode C; all five are radiology and four are CT; CT-RATE is used twice and no dataset more than twice. Zero revivals: no new checkable fact was found that changes a portfolio-brief unblock condition. The five designs use four grammars; regional-substitution appears twice because both use claims require localized interventions, but one edits vascular caliber contrast and the other vertebral deformity.",
  "revivals": [],
  "all_questions": [
    {"q": "Does CT-CLIP's mosaic-attenuation score use the regional pulmonary-vessel caliber contrast that distinguishes mosaic perfusion from infiltrative ground glass?", "status": "DEVELOPED (c01, Mode A)"},
    {"q": "Does Sybil's lung-cancer risk score use incomplete interlobar fissures, a developmental route for collateral ventilation and cross-lobar emphysema spread?", "status": "DEVELOPED (c02, Mode B)"},
    {"q": "Does a chest-radiograph mortality model use vertebral compression-fracture burden as its named skeletal frailty signal?", "status": "DEVELOPED (c03, Mode B)"},
    {"q": "Does Merlin's hypertension phenotype use renal-artery tortuosity as a pressure-buckling signature? (cross-domain: elastic-column buckling)", "status": "DEVELOPED (c04, Mode C)"},
    {"q": "Does an NCCT infarct model use cortical-vein density asymmetry as a hydraulic readout of collateral failure? (cross-domain: watershed hydraulics; sounds probably wrong)", "status": "DEVELOPED (c05, Mode C)"},
    {"q": "Does CT-CLIP's lymphadenopathy score use the azygos-vein diameter rather than lymph-node size?", "status": "DROPPED - the anatomical coincidence is interesting but the use intervention cannot separate venous-pressure anatomy from a mediastinal edit artifact without contrast-aware vessel segmentation."},
    {"q": "Does a pulmonary-edema model use cranio-caudal redistribution of vessel blood volume (3D cephalization)?", "status": "DROPPED - duplicates backlog scout-011-c03."},
    {"q": "Does a COPD model use the diaphragm's radius of curvature as a pressure-loaded membrane?", "status": "DROPPED - duplicates backlog scout-009-c06."},
    {"q": "Does a cirrhosis model use portal-vein pulsatility written as helical-CT banding?", "status": "DROPPED - no primary evidence yet that the proposed pulsatility measurement survives routine abdominal CT sampling; weaker mechanism than c05."},
    {"q": "Does a head-CT age model use pineal-calcification volume as a biological clock?", "status": "DROPPED - X is measurable, but age prediction from head CT is crowded and the question lacks a model-beats-human or clinically meaningful unexplained output anchor."}
  ],
  "candidates": [
    {
      "id": "scout-013-c01",
      "search_mode": "A",
      "entry_point": 2,
      "title": "The vessel map inside the mosaic-attenuation score",
      "question": "Does CT-CLIP's mosaic-attenuation score use regional pulmonary-vessel caliber contrast rather than attenuation heterogeneity alone?",
      "design_template": "regional-substitution",
      "dataset": "CT-RATE validation split",
      "entry_point_2_requirements": "Unexpected-signal measurement: within-lung correlation between local attenuation and local small-vessel volume, plus the difference in vessel caliber between matched lucent and dense regions. Confusable artifact: reconstruction kernel changes both apparent vessel caliber and texture; the primary intervention is within reconstruction and the established geometry-matched reconstruction pairs provide a sensitivity audit.",
      "rung": "Targets rung 1. It moves to rung 2 after reconstruction, protocol, and edit-validity controls; it reaches rung 3 only if vessel-caliber-preserving attenuation shams and attenuation-preserving vessel edits disagree in the predicted direction.",
      "deliverable_sentence": "The model's mosaic-attenuation score is using the regional reduction in pulmonary-vessel caliber within lucent lung.",
      "X_measurement": "Segment pulmonary vessels with a published automated vessel-segmentation method, skeletonize the tree, estimate local radius from the distance transform, and compute paired small-vessel volume density in locally lucent versus dense lung regions. Quantitative CT literature uses percent cross-sectional area of vessels below 5 mm2 (%CSA<5) and documents caliber differences in mosaic perfusion (Shahin et al., Pulmonary Circulation 2019, PMCID PMC6377046). Could it be computed on a new scan without asking anyone? YES, subject to a Stage-0 segmentation-quality gate.",
      "suspected_signal": "Occlusive pulmonary vascular disease produces hypoperfused, hypoattenuating secondary-lobule territories with fewer and narrower vessels; small-airway and infiltrative causes can produce similar attenuation patches but differ in vascular behavior. The model may have learned this radiologist-used discriminator from 3D context.",
      "use_vs_association": "Association is only the score-X curve. Use is tested by two factorial, within-scan edits: equalize vessel caliber across lucent/dense regions while preserving parenchymal HU, and equalize regional HU while preserving vessels. A selective score response to the first distinguishes vessel use from mere label correlation.",
      "keystone_prerequisite": "The released CT-CLIP v2 checkpoint exposes a stable, per-volume Mosaic attenuation pattern score on CT-RATE through a runnable deterministic pipeline.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "probes/004/run.py lines 226-244 include \"Mosaic attenuation pattern\" in EXPECTED_PATHOLOGIES; evidence/decisions.md (2026-08-12 load-probe decision) records 18 finite named scores, bit-identical A repeat, and the frozen checkpoint SHA-256 9246d9c8a7e2cedaa115719699229fe0acb02f19488e8bd1ad1eff5f47ff1d7d.",
      "keystone_residual_assumption": "The nearest verified fact is that the head runs. Still assumed, and load-bearing for interpretation, is that a vessel segmenter resolves peripheral caliber after CT-CLIP's 1.5-mm resampling and that localized caliber edits can be made without detectable nonvascular texture artifacts. Stage 0 must inspect both; otherwise this becomes association-only.",
      "rung_reached": "1 if the factorial intervention passes sham and realism gates; 2 after paired reconstruction sensitivity and acquisition-stratified replication; 3 is the deliverable sentence, conditional on those gates.",
      "dies_like_prior": "It inherits idea-006's OOD-intervention risk, but differs because anatomy is not deleted and the edit is localized, factorial, and sham-matched. It does not depend on annotation provenance: the primary endpoint is a score difference on the same scan. It also checks DATA_ACCESS (checkpoint already load-probed), DATA_INSUFFICIENT (Stage-0 support count), IDENTIFIABILITY_FAILURE (factorial edits), and CIRCULARITY (vessel caliber is not the mosaic label definition alone).",
      "closest_prior_work": "Hamamci et al., CT-CLIP/CT-RATE, arXiv:2403.17834, released the model and benchmark but did not decode this head. Shahin et al. quantified vessels, bronchi, emphysema, and mosaic attenuation across severe PH groups (PMCID PMC6377046) but did not study model behavior. The exact delta is a model-use intervention on vessel-caliber contrast.",
      "existing_assets": "Frozen CT-CLIP checkpoint and verified inference lineage; CT-RATE validation volumes and 425 geometry-matched reconstruction pairs; TotalSegmentator lung masks; published quantitative-vessel formulas.",
      "smallest_decisive_experiment": "Stage 0 on 30 scans: demonstrate stable peripheral vessel masks and enough cases with strong attenuation-vessel contrast. Then on 60 high-X scans, run preregistered A/B factorial edits plus equal-volume vessel-adjacent shams, reporting per-scan score deltas and edit discriminability. Confirmatory set is frozen before model scores are read.",
      "standing_confounds_addressed": "Scanner/vendor, site, protocol, reconstruction, positioning, and habitus are fixed within each edited scan. Reconstruction sensitivity is separately measured on geometry-matched pairs. Prevalence and referral pathway cannot create a within-image score delta. Report-label leakage may explain why the cue was learned but not the paired use result. Not ruled out: vessel editing may alter adjacent parenchymal texture; factorial and sham controls target but may not eliminate this.",
      "alternative_explanations": "(1) The model uses attenuation patches, not vessels: ruled out if attenuation-preserving vessel edits move the score and vessel-preserving HU edits do not. (2) It uses generic high-frequency edit artifacts: tested with equal-boundary shams and an edit detector. (3) Both features are jointly required: a factorial interaction is explicitly estimated and would narrow, not support, the simple sentence.",
      "anticipated_negative": "Decisive only if segmenter and edit-realism gates pass: score equivalence to a sham-derived margin under vessel equalization, while the model remains responsive to an attenuation positive control, weakens the vessel-use hypothesis. Gate failure is uninterpretable, not a negative.",
      "cross_domain": null,
      "remaining_legwork": "Vessel-tool selection and 30-case validation: 4-6 days; edit-realism pilot: about one week; first scientific decision: roughly 2-3 weeks on one GPU.",
      "scores": {
        "clarity": {"value": 5, "why": "One head, one quantitative vessel contrast, and a factorial test."},
        "identifiability": {"value": 4, "why": "Factorial edits separate vessels from attenuation, with residual edit-artifact risk."},
        "medical_relevance": {"value": 4, "why": "Names whether a model applies a clinically important vascular discriminator."},
        "interest": {"value": 4, "why": "Turns a generic texture label into pulmonary perfusion anatomy."},
        "prior_legwork": {"value": 4, "why": "Model, data, inference, and quantitative measurement literature exist."},
        "feasibility": {"value": 4, "why": "Keystone inspected; vessel editing is the remaining substantial task."},
        "data_readiness": {"value": 5, "why": "CT-RATE pipeline and checkpoint are already verified locally."},
        "evaluation_readiness": {"value": 4, "why": "Paired factorial deltas and established vessel metrics are ready."},
        "negative_result_value": {"value": 4, "why": "Conditional on gates, the negative excludes a named discriminator."},
        "novelty_confidence": {"value": 3, "why": "Closest-work delta was checked, but no exhaustive interpretability search was completed."},
        "regret": {"value": 4, "why": "A direct, tractable decoding experiment on a verified head."}
      },
      "priority_score": 4.25,
      "unverified_claims": ["A validated vessel model performs adequately after CT-CLIP preprocessing.", "The required caliber edit can pass an image-realism discriminator.", "CT-RATE contains at least 60 scans with strong measurable mosaic vessel contrast."]
    },
    {
      "id": "scout-013-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The open fissure inside lung-cancer risk",
      "question": "Does Sybil's lung-cancer risk score use incomplete interlobar fissures, independently of emphysema burden and nodule appearance?",
      "design_template": "conditional-observational",
      "dataset": "NLST held-out scans scored by a reproduced or released Sybil model",
      "entry_point_2_requirements": "Measurement: fissure completeness percentage from automated lobe/fissure segmentation. Confusable artifact: thick-slice reconstruction makes fissures appear incomplete and also degrades nodules; slice thickness and kernel must be exact-matched or conditioned.",
      "rung": "Reaches rung 1 only as a probe-plus-conditional-disagreement study; moves toward 2 with site/protocol matching; moves to 3 only after an in-distribution fissure-completion intervention or a natural longitudinal contrast.",
      "deliverable_sentence": "The lung-cancer risk model is using interlobar fissure incompleteness.",
      "X_measurement": "Fissure completeness is the proportion of the ideal lobar boundary occupied by visible fissure, computed from automated lobe masks and a fissure-enhancement/segmentation network; it is already used quantitatively for bronchoscopic lung-volume-reduction planning. Could it be computed today on a new scan without asking anyone? YES in principle with published automated CT fissure methods, but the exact maintained tool must be selected in Stage 0.",
      "suspected_signal": "Incomplete fissures permit collateral ventilation and may organize how emphysema and smoke injury spread across lobes. A longitudinal risk model could use this developmental lung architecture as a stable susceptibility marker rather than merely count present nodules.",
      "use_vs_association": "A raw correlation is insufficient. The smallest use evidence is cross-model disagreement plus representation probing: among scans exactly matched on nodule burden, emphysema %, age, smoking, and reconstruction, test whether Sybil-minus-nodule-model residual risk is predictable from fissure completeness on a frozen test set. This is still rung 1, not causal use; a validated fissure edit is required for the stronger claim.",
      "keystone_prerequisite": "An obtainable Sybil evaluation cohort retains enough variation in fissure completeness within exact reconstruction and emphysema/nodule strata to identify an independent fissure signal.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The easy adjacent facts are that NLST contains Sybil scans and automated lobe segmentation exists. Still assumed is the load-bearing joint support: fissure completeness is not nearly deterministic from emphysema, sex, slice thickness, or site. This is the idea-017 lesson and must be a metadata-only Stage-0 gate.",
      "rung_reached": "1 if frozen residual-risk and representation tests agree; 2 needs external/site replication; 3 requires a natural or validated counterfactual fissure contrast.",
      "dies_like_prior": "Most resembles idea-009 and idea-017: a beautiful anatomical measure may be inseparable from covariates. It differs only by making adequate joint support a kill gate before scoring. It avoids annotation provenance and label leakage in the primary score-to-X readout, but DATA_ACCESS to Sybil outputs and IDENTIFIABILITY_FAILURE remain live risks.",
      "closest_prior_work": "Mikhael et al., Sybil, J Clin Oncol 2023, DOI 10.1200/JCO.22.01345, established future lung-cancer prediction from one LDCT. Quantitative fissure completeness work supports the measurement, but I found no primary study connecting fissure completeness to Sybil or another lung-cancer risk representation. Absence is not proof of novelty.",
      "existing_assets": "NLST imaging and metadata through CDAS; published Sybil architecture/results; automated lobe segmentation; established emphysema percentage and nodule detectors.",
      "smallest_decisive_experiment": "Before model access, freeze 300 NLST scans with adequate overlap across fissure-completeness quartiles after exact matching on sex, smoking, emphysema %, nodule volume, slice thickness, kernel, and site. If support passes, compare fissure predictability of Sybil residual risk against a nodule-only model on untouched patients.",
      "standing_confounds_addressed": "Exact/propensity matching addresses site, scanner, protocol, reconstruction, sex, habitus proxies, smoking, and emphysema. NLST limits referral heterogeneity but does not erase it. Outcome prevalence is handled through frozen sampling. Report leakage is irrelevant to Sybil's future cancer endpoint. Residual unmeasured COPD severity and developmental anatomy remain.",
      "alternative_explanations": "(1) Fissure score is a slice-thickness artifact: exact reconstruction matching. (2) It proxies emphysema distribution: condition on global and lobar emphysema. (3) It proxies missed juxtapleural nodules: condition on nodule detector outputs and test nodule-free scans. None proves causal use; the card states that limitation.",
      "anticipated_negative": "Decisive for an independent observational signal only if joint support and measurement reliability pass and an equivalence margin is fixed; it is not decisive against causal use because a model may encode fissures nonlinearly.",
      "cross_domain": null,
      "remaining_legwork": "CDAS variable/file inspection and model-access check: 1-2 weeks; fissure tool benchmark: one week; first support decision before GPU inference: about 2 weeks.",
      "scores": {
        "clarity": {"value": 4, "why": "Named X and model; the residual-risk estimand needs careful explanation."},
        "identifiability": {"value": 2, "why": "Conditional observational evidence cannot prove use and joint support may fail."},
        "medical_relevance": {"value": 3, "why": "Could name a stable susceptibility phenotype, but clinical consequence is indirect."},
        "interest": {"value": 4, "why": "Developmental lung architecture as cancer-risk signal is unexpected."},
        "prior_legwork": {"value": 3, "why": "Model and measurement literature exist; no joined pipeline is in hand."},
        "feasibility": {"value": 3, "why": "Capped by NOT_INSPECTED and model/data access is unresolved."},
        "data_readiness": {"value": 2, "why": "NLST is gated and Sybil outputs/weights are not confirmed locally."},
        "evaluation_readiness": {"value": 3, "why": "Matching and residual comparisons are standard, intervention is absent."},
        "negative_result_value": {"value": 3, "why": "Can decisively reject an independent fissure contribution under adequate support."},
        "novelty_confidence": {"value": 2, "why": "Limited search and keystone uninspected."},
        "regret": {"value": 3, "why": "Worth screening, but identification ceiling is real."}
      },
      "priority_score": 2.9,
      "unverified_claims": ["A maintained automated fissure-completeness tool is directly runnable on NLST.", "Sybil weights or per-scan outputs are obtainable.", "Adequate covariate overlap exists."]
    },
    {
      "id": "scout-013-c03",
      "search_mode": "B",
      "entry_point": 1,
      "title": "Name the skeletal frailty inside mortality prediction",
      "question": "Does a chest-radiograph mortality model use vertebral compression-fracture burden as a named skeletal frailty signal?",
      "design_template": "regional-substitution",
      "dataset": "Public chest-radiograph mortality anchor cohort if obtainable; external measurement development on MIMIC-CXR",
      "rung": "Targets rung 1 through vertebral-region intervention, rung 2 through site/device replication, and rung 3 if morphometry-specific edits outperform matched texture shams.",
      "deliverable_sentence": "The mortality model is using vertebral compression-fracture burden.",
      "X_measurement": "Automated Genant-like vertebral morphometry from lateral or frontal radiographs: vertebral height ratios, wedge angle, and count of bodies exceeding prespecified deformity thresholds, using an automated spine/vertebral detector. Could it be computed on an unseen image without asking anyone? YES for a validated automated pipeline; applicability to frontal-only films is the Stage-0 measurement gate.",
      "suspected_signal": "Compression deformities integrate osteoporosis, falls, glucocorticoid exposure, malignancy, and frailty. Mortality models may exploit this cumulative skeletal history even when radiologists judging short-term image findings do not name it.",
      "use_vs_association": "Use is tested by replacing only vertebral-body shapes with age/sex/device-matched normal morphometry while preserving surrounding image statistics, compared with boundary-matched sham warps. Association with mortality or score is secondary.",
      "keystone_prerequisite": "The anchor mortality model and a test cohort with images and outcome horizon are obtainable for score-level intervention, rather than only published aggregate results.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearby verified literature fact is that chest-radiograph mortality prediction exists and radiologists can judge some mortality gestalt. Still assumed is the real keystone: scoreable images plus the exact model are obtainable. A re-trained substitute changes the claim and must be registered as such.",
      "rung_reached": "1 if morphometry edits selectively shift risk; 2 with external device/site replication; 3 is the stated named phenotype after edit validity.",
      "dies_like_prior": "Closest is idea-018 (DATA_ACCESS): an attractive prognosis model without obtainable weights/data. This candidate does not yet dodge it and may die immediately; that is why feasibility is capped and Stage 0 begins with asset inspection. Annotation provenance is irrelevant to the automated X and paired primary readout; CIRCULARITY is avoided because compression fracture is not the mortality label.",
      "closest_prior_work": "Lu et al., Scientific Reports 2021, PMCID PMC8486799, compared radiologist mortality gestalt with a deep model; other primary chest-radiograph longevity models establish the output. They did not measure or intervene on vertebral compression burden. Exact model artifact availability remains unverified.",
      "existing_assets": "Large public radiograph corpora, automated vertebral detection literature, and standard morphometric formulas. The required anchor artifact is not yet an asset.",
      "smallest_decisive_experiment": "Stage 0 is binary: obtain the exact model and linkable test images. Then validate automated morphometry on a small public labeled spine set; on 100 high-deformity anchor images run normalizing warps and matched sham warps, with risk-score delta as the label-free primary endpoint.",
      "standing_confounds_addressed": "Within-image edits fix site, device, protocol, positioning, habitus, prevalence, and referral pathway. Label leakage from reports is absent for mortality supervision. External replication addresses device/site. Remaining threat is that warps alter global projection geometry or reveal an editing signature.",
      "alternative_explanations": "(1) Model reads age-correlated aortic/rib features: fixed by localized edit. (2) It responds to warp artifacts: boundary/area-matched shams and edit detector. (3) Apparent compression on frontal images is rotation/positioning: exclude large rotation and validate repeatability.",
      "anticipated_negative": "Decisive only after model access, reliable morphometry, and sham-equivalent edits: then no score movement excludes compression burden above the prespecified detectable effect. Asset or measurement failure is uninterpretable.",
      "cross_domain": null,
      "remaining_legwork": "Asset audit: 1-2 days; likely author contact or rejection if unavailable; morphometry validation and edit pilot: 2-3 weeks after access.",
      "scores": {
        "clarity": {"value": 5, "why": "A familiar named lesion and direct paired intervention."},
        "identifiability": {"value": 4, "why": "Localized morphometry normalization can isolate X if shams pass."},
        "medical_relevance": {"value": 4, "why": "Would turn opaque mortality gestalt into actionable skeletal frailty."},
        "interest": {"value": 4, "why": "Plausible, clinically legible, and one experiment beyond existing mortality work."},
        "prior_legwork": {"value": 2, "why": "Published anchor exists but executable artifact is unconfirmed."},
        "feasibility": {"value": 2, "why": "DATA_ACCESS may kill it and keystone is uninspected."},
        "data_readiness": {"value": 2, "why": "Development data are public; decisive anchor data/model are unconfirmed."},
        "evaluation_readiness": {"value": 3, "why": "Morphometry and paired deltas are clear, edit validity custom."},
        "negative_result_value": {"value": 4, "why": "After gates, it decisively removes a concrete mortality explanation."},
        "novelty_confidence": {"value": 2, "why": "Limited search and cap applies."},
        "regret": {"value": 3, "why": "High value if assets exist, low cost to screen."}
      },
      "priority_score": 3.25,
      "unverified_claims": ["The exact anchor model is obtainable.", "Frontal-radiograph vertebral compression burden can be measured with adequate reliability.", "Localized shape normalization can be made in-distribution."]
    },
    {
      "id": "scout-013-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The renal artery as a buckled pressure line",
      "question": "Does Merlin's hypertension phenotype use renal-artery tortuosity as an image-written history of chronic pressure and vascular remodeling?",
      "design_template": "conditional-observational",
      "dataset": "Public contrast-enhanced abdominal CT compatible with released Merlin checkpoint",
      "entry_point_2_requirements": "Measurement: renal-artery centerline tortuosity, curvature, and length/chord ratio from automated vessel segmentation. Confusable artifact: respiratory phase and oblique reconstruction change apparent curvature; compute in physical 3D coordinates and stratify contrast phase/protocol.",
      "rung": "Targets rung 1 as a frozen representation/score probe; moves up through natural longitudinal scans or a validated vessel-shape counterfactual.",
      "deliverable_sentence": "The model's hypertension score is using renal-artery tortuosity.",
      "X_measurement": "Segment the main renal arteries on contrast CT, extract centerlines, and compute arc-length/chord ratio plus integrated absolute curvature in mm-based coordinates. These are standard vessel-tortuosity formulas. Could it be computed today without an annotator? YES on suitable contrast CT, contingent on selecting a validated renal-artery segmenter.",
      "suspected_signal": "Chronic pressure, atherosclerotic remodeling, and tethered-vessel mechanics can lengthen a vessel relative to its endpoints, forcing curvature. A model supervised by diagnosis codes may exploit this stable vascular geometry rather than transient image appearance.",
      "use_vs_association": "The first experiment distinguishes association from representation use by testing whether tortuosity predicts the frozen hypertension logit and a linear probe of Merlin embeddings after conditioning on age, aortic calcium, renal volume, and phase. It cannot prove causal use; a natural paired or validated straightening intervention is explicitly required for rung 3.",
      "keystone_prerequisite": "A public, Merlin-compatible cohort contains contrast-enhanced arterial/portal-venous scans with renal arteries sufficiently visible and enough hypertension-score variance.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The easy fact is that Merlin weights and phenotype heads are public (Blankemeier et al., arXiv:2406.06512). Still assumed is the load-bearing imaging support: public scans both match preprocessing and show the renal arteries well enough. Without it, vessel tortuosity is measurement noise.",
      "rung_reached": "1 at most from score/representation dependence; 2 needs phase/site robustness; 3 needs a natural within-patient pressure change or credible shape edit.",
      "dies_like_prior": "It resembles scout-010-c05's aortic-tortuosity idea and idea-009's IDENTIFIABILITY_FAILURE. This is not a revival and does not claim novelty over that backlog grammar; the renal artery is a new, organ-specific hypothesis but may be too correlated with age/atherosclerosis. Annotation provenance does not enter the primary readout. DATA_ACCESS is reduced by public Merlin weights but cohort suitability is unverified.",
      "closest_prior_work": "Blankemeier et al., Merlin, arXiv:2406.06512, provides phenotype prediction and public weights but no anatomical decoding of hypertension. Vascular-tortuosity literature motivates the measurement; no verified primary study was found linking renal-artery tortuosity to Merlin. Novelty is explicitly low-confidence.",
      "existing_assets": "Released Merlin weights and single-GPU inference; public abdominal CT collections; centerline tortuosity formulas; TotalSegmentator for kidneys/aorta but not necessarily renal arteries.",
      "smallest_decisive_experiment": "Stage 0: inspect 50 candidate public scans and require prespecified renal-artery visibility/segmentation repeatability and hypertension-logit variance. Freeze 200 scans, compute tortuosity, and test incremental prediction of the logit beyond age proxy, aortic calcium, kidney volume, contrast phase, and scanner.",
      "standing_confounds_addressed": "Protocol/reconstruction/site/vendor enter stratified models; 3D physical coordinates reduce positioning artifacts; habitus and kidney size are conditioned. Disease prevalence/referral and diagnosis-code leakage remain population-level explanations for why the model learned the feature and are not eliminated. No report label is used in the primary analysis.",
      "alternative_explanations": "(1) Tortuosity proxies age/atherosclerosis: condition on automated aortic calcium and aortic tortuosity, but residual confounding remains. (2) Contrast timing drives segmentation and score: phase stratification and repeatability gate. (3) The model uses adjacent renal morphology: kidney volume/cortical thickness conditioning. A positive remains rung 1.",
      "anticipated_negative": "Sensitivity-limited: a null may reflect segmentation noise, restricted public-cohort range, or nonlinear encoding. Only a tightly powered equivalence result after repeatability gates would weaken the hypothesis.",
      "cross_domain": {"borrowed_construct": "Elastic-column buckling: a lengthening tethered vessel accommodates excess length by curvature.", "implied_measurement": "Arc-length/chord ratio and integrated curvature, compared with endpoint distance and vessel caliber.", "what_changes_if_dropped": "Without buckling mechanics the study becomes a generic radiomics correlation and loses the prespecified joint prediction that tortuosity should rise with excess centerline length at fixed endpoints; that interaction is the mechanism check."},
      "remaining_legwork": "Public-cohort and segmenter audit: about one week; 50-case repeatability gate: one week; first model result: 2-3 weeks.",
      "scores": {
        "mechanism_clarity": {"value": 4, "why": "Specific vessel geometry and formula; biological specificity remains uncertain."},
        "identifiability": {"value": 2, "why": "Age and atherosclerosis are powerful inseparable alternatives without intervention."},
        "interest": {"value": 3, "why": "Readable but shares a tortuosity grammar already in the backlog."},
        "medical_relevance": {"value": 3, "why": "Could explain a hypertension code, with modest direct consequence."},
        "clarity": {"value": 4, "why": "One model output and one quantitative X."},
        "feasibility": {"value": 3, "why": "Informational, capped by NOT_INSPECTED."},
        "data_readiness": {"value": 2, "why": "Weights are public; compatible vascular imaging is unconfirmed."},
        "evaluation_readiness": {"value": 3, "why": "Standard tortuosity metrics, custom conditioning."},
        "negative_result_value": {"value": 2, "why": "Classified sensitivity-limited."},
        "novelty_confidence": {"value": 2, "why": "Limited search and close backlog analogue."},
        "regret": {"value": 2, "why": "Mechanistically neat but not a portfolio priority."}
      },
      "priority_score": 3.15,
      "priority_note": "Mode C: 0.30*4 + 0.25*2 + 0.20*3 + 0.15*3 + 0.10*4 = 3.15.",
      "unverified_claims": ["A suitable public contrast cohort is Merlin-compatible.", "Renal-artery segmentation is reliable at routine portal-venous timing.", "Renal-artery tortuosity has independent support beyond age and atherosclerosis."]
    },
    {
      "id": "scout-013-c05",
      "search_mode": "C",
      "entry_point": 1,
      "title": "Collateral failure written in the cortical veins",
      "question": "Does an NCCT model that estimates early infarct use hemispheric cortical-vein density asymmetry as a hydraulic readout of collateral failure?",
      "design_template": "natural-paired",
      "dataset": "Paired baseline NCCT and CTA/CTP or DWI stroke cohort from the anchor model; public CQ500 only for measurement robustness",
      "rung": "Targets rung 1 using within-head hemispheric asymmetry and model disagreement; moves to rung 2 with scanner/protocol matching; rung 3 needs CTA/CTP collateral validation and a natural recanalization or serial-CT contrast.",
      "deliverable_sentence": "The infarct model is using reduced cortical-vein density in the affected hemisphere as a sign of collateral failure.",
      "X_measurement": "Register a reflected contralateral hemisphere, enhance tubular hyperdense structures in the cortical subarachnoid space with a multiscale vesselness filter, and compute affected/unaffected cortical-vein volume and mean HU ratios after excluding calcification and arteries by atlas/trajectory. Could it be computed today without an annotator? YES as a well-defined measurement, but whether NCCT distinguishes veins reliably is the keystone gate.",
      "suspected_signal": "In low-flow ischemia, delayed venous filling, deoxygenation-related attenuation changes, and reduced perfused blood volume could create a hemispheric venous-density asymmetry. A model trained against DWI infarct may exploit this diffuse vascular consequence when early parenchymal hypoattenuation is below human visibility.",
      "use_vs_association": "The within-head asymmetry is associated with the model's infarct map, but use requires a natural-paired test: among patients with baseline and short-interval post-recanalization NCCT at matched acquisition, ask whether vein asymmetry and model-estimated infarct change together while established infarct tissue cannot reverse. Without such pairs the result remains rung 1 association, not causal use.",
      "keystone_prerequisite": "Routine baseline NCCT contains a reproducible cortical-vein asymmetry that agrees directionally with independently measured collateral status or perfusion delay in the same patients.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearby verified fact is that NCCT models can estimate DWI infarct and outperform expert early reads (primary full text PMCID PMC9814956). Still assumed is the real keystone: the proposed venous measurement is physically present and separable from arteries, beam hardening, and hematocrit on routine NCCT. Phase 1 tests X before touching the model.",
      "rung_reached": "1 if X validates against collateral/perfusion imaging and predicts model output beyond parenchymal HU; 2 after acquisition robustness; 3 after natural paired support.",
      "dies_like_prior": "It risks idea-009 IDENTIFIABILITY_FAILURE because venous asymmetry covaries with the infarct itself, and idea-018 DATA_ACCESS because the exact model cohort may be unavailable. It differs by requiring independent CTA/CTP validation of X first and by using the contralateral hemisphere as a within-patient control. Annotation provenance is not used. The model-use claim remains deliberately conditional.",
      "closest_prior_work": "The NCCT-to-DWI infarct model in Radiology/Stroke imaging literature (PMCID PMC9814956) used 3,566 NCCT/MRI pairs and compared against expert neuroradiologists. Hyperdense cortical veins and venous signs have been studied diagnostically, but I did not verify a study decoding an infarct network with automated hemispheric cortical-vein density. This gap is search-limited.",
      "existing_assets": "Published anchor method; standard vesselness filters and symmetry registration; stroke cohorts often contain CTA/CTP/DWI, though access to the anchor cohort/model is unconfirmed.",
      "smallest_decisive_experiment": "Phase 1, independent of the model: on 50 NCCT cases with CTA/CTP collateral or Tmax maps, preregister direction and test repeatability of cortical-vein asymmetry. Stop if it fails. Phase 2 only with access: regress model infarct probability on vein asymmetry conditional on mirrored parenchymal HU and lesion volume; reserve serial post-recanalization pairs as confirmation.",
      "standing_confounds_addressed": "Within-head ratios control scanner, vendor, protocol, reconstruction, site, habitus, referral, and prevalence at the primary measurement level. Positioning and beam hardening may be asymmetric and require skull-base exclusion and mirrored sham regions. Hematocrit is systemic and cancels approximately within patient. Label leakage is impossible in image-only inference. Side-of-occlusion prevalence and true parenchymal injury remain coupled.",
      "alternative_explanations": "(1) Vesselness detects arteries or calcification: CTA registration and atlas exclusions test this. (2) Asymmetry is beam hardening or head rotation: reflected sham territories and superior-convexity restriction. (3) The model reads subtle parenchymal edema that also reduces vessel conspicuity: conditioning on mirrored HU cannot fully separate it; natural recanalization is the upgrade.",
      "anticipated_negative": "Decisive at Phase 1 for the physical mechanism if NCCT asymmetry has prespecified poor repeatability and no agreement with perfusion/collateral status. A Phase-2 null after Phase-1 success is sensitivity-limited unless the anchor model and effect margin are fixed.",
      "cross_domain": {"borrowed_construct": "Watershed hydraulics: downstream venous appearance integrates upstream inflow and collateral resistance across a vascular territory.", "implied_measurement": "Territory-level cortical-vein volume/HU asymmetry compared with perfusion delay, not generic image texture.", "what_changes_if_dropped": "Without hydraulics there is no prediction that venous asymmetry should track Tmax/collateral grade before it tracks irreversible DWI volume; that ordered validation is the reason Phase 1 exists."},
      "remaining_legwork": "Identify a genuinely accessible paired NCCT/CTA/CTP cohort and inspect schema: 1-2 weeks; measurement pilot: 1-2 weeks; model access may be terminal.",
      "scores": {
        "mechanism_clarity": {"value": 5, "why": "Named hemodynamic quantity, spatial measurement, and independent validation modality."},
        "identifiability": {"value": 3, "why": "Within-head control and perfusion validation help, but edema remains coupled."},
        "interest": {"value": 5, "why": "A hidden vascular signal could explain genuine model-over-reader early infarct performance."},
        "medical_relevance": {"value": 5, "why": "Early infarct extent directly affects acute stroke treatment."},
        "clarity": {"value": 4, "why": "Precise, though arterial/venous separation complicates X."},
        "feasibility": {"value": 2, "why": "Informational and capped; paired data/model access is uncertain."},
        "data_readiness": {"value": 1, "why": "No confirmed accessible linked cohort or checkpoint."},
        "evaluation_readiness": {"value": 3, "why": "Collateral/perfusion validation is standard; NCCT measurement is custom."},
        "negative_result_value": {"value": 4, "why": "Phase 1 can decisively kill the proposed physical signal."},
        "novelty_confidence": {"value": 3, "why": "Capped and search-limited despite a precise checked delta."},
        "regret": {"value": 4, "why": "High-payoff mechanism worth a cheap physics-first screen."}
      },
      "priority_score": 4.4,
      "priority_note": "Mode C: 0.30*5 + 0.25*3 + 0.20*5 + 0.15*5 + 0.10*4 = 4.40.",
      "unverified_claims": ["Cortical veins are reproducibly separable on routine NCCT.", "Venous-density asymmetry tracks collateral failure in the proposed direction.", "The anchor model or per-case scores and linked multimodal data are obtainable."]
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

