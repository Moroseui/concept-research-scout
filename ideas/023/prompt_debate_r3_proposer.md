You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/023
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

## 2026-08-15 - A2 phase M complete: manifest frozen, contract amended

Phase M ran metadata-only under the phase-1 approval (marker and
contract both blob a84b617cd5a0...). The frozen Stage-0 selection was
reproduced EXACTLY from raw released metadata: 237/126/58/4 per
stratum, 425 pairs, 850 unique volumes (no volume participates in two
pairs). pair_manifest.csv frozen at SHA-256
5dc0f07fbc9aa01a30c3ad4f5bdfb6d7cd078db58392b7e4329bd37b38c12d38.
Anchor pair p001 flagged anchor_excluded per the resolved A2 question.
The contract amendment replaces the sha, count, and cap placeholders
with these values; the invalidating-failure rule line retains the
placeholder token by design (it is the rule that polices placeholders,
not a placeholder). The QA/retry allowance remains in formula form,
now fully resolvable from concrete in-file values (170); converting it
to the literal is out of the authorized amendment scope and deferred.
Per the two-phase design this amendment stales the phase-1 approval by
construction. Phase-2 approval is DEFERRED until the results-transport
machinery (E1/E2) lands; no bulk activity is authorized in the
interim, and the driver refuses phase B regardless.

## 2026-08-15 - A2 amendment 2: placeholder rule line reworded

Audit of run.py found the phase-B placeholder check is a full-file
scan (run.py:411). The invalidating-failure rule line retained the
literal token by design and would therefore refuse phase B forever.
Resolution on the contract side, zero code change: the rule line now
says "TO_BE_RECORDED placeholder token" instead of the full literal.
Rule meaning unchanged. Timed before phase-2 approval, so no extra
approval staleness is incurred (the phase-1 marker was already stale
from amendment 1). The naive scan itself goes on the run.py polish
list, not a revision: it is fail-safe in direction and now correct
in effect.

## 2026-08-15 - Probe 004 v2 revision spec r1 (harness fault, exit 12)

Observed in production (attempt 3, driver_console.log on the results
branch, commit da85a52): after anchor volume cache hits,
UNEXPECTED INTERNAL ERROR (exit 12): OSError(18, Invalid cross-device
link). Root cause class: a file relocation using rename semantics
between the Drive-mounted output directory and local scratch, which
are different filesystems; rename cannot cross devices. Attempt 2
died identically (silent, pre-console-log).

Revision requirements, and ONLY these:
1. Every file relocation that can cross the boundary between
   --output-dir and local working storage must use EXDEV-safe
   semantics (e.g. shutil.move, or copy-verify-delete); no bare
   os.rename / Path.rename across that boundary anywhere in run.py.
2. The exit-12 unexpected-error handler must emit the full traceback
   to stderr, not only the exception repr, so future harness faults
   are diagnosable from the persisted console log.
No scientific scope, endpoint, gate, cap, or analysis change of any
kind. The contract is untouched; exit 12 is a harness fault by the
taxonomy, so the phase-2 approval remains bound and valid.

## 2026-08-16 - RECORD-RESULT: idea 004 425-pair bundle merged (the gate)

The results PR from branch results/probe-004-8b68640183ee was merged
after deterministic validation (validate-bundle: core files, contract
blob, manifest pin, chunk manifests all pass) and operator-side audit.
Study facts of record: 425/425 pairs scored across 5 of 30 sessions;
anchor pair excluded from confirmatory statistics (236 counted
Br40f|Br60f); anchors in tolerance every session with dev 0.00e+00;
850 scientific volumes, 2 QA retries of a 170 allowance; all
spot-checks bit-identical. The auto-PR condition in results-validate
missed because run.py emits contract_satisfied/chunks_complete rather
than study_complete -- key-schema mismatch, polish list; the PR was
opened manually and the gate semantics are unchanged. Interpretation
is NOT made here: the interpret stage runs only after the
interpret-review machinery (cross-family checker-mode review of the
interpretation, mirroring probe-build) lands, per the operator
decision of this date. Until then the tables in
probes/004/results_v2/analysis/ are the deliverable and carry no
narrative.

## 2026-08-16 - IDEA 004 RATIFIED: interpretation approved and adopted

The interpretation at ideas/004/interpretation.md (git blob
ccd66870a240d04f66a13eb2f69e54cf6d75743e) and its cross-family review
at ideas/004/interpret_review.md (git blob
bb208dae52be559544cf2192eb3edc848d80fdd1) are ratified. The checker
approved on round 1 after resolving every citation against the
analysis files; an operator-side audit independently re-resolved five
citations spanning both tiers and the summary accounting, all
transcription-exact.

Finding of record (rung 1, vendor-scoped, this checkpoint, these
contrasts): the model is using reconstruction-dependent image content
when it produces some named chest-CT abnormality scores. Typical
signed shifts are small; direction and upper-tail magnitude depend on
head and contrast; pleural effusion shows directional medians with
patient-cluster intervals below zero under both cross-family
contrasts. Tier 2 is descriptive only; no threshold judgment exists;
CT-Scroll values remain context.

ADVANCE is adopted with its stated semantics: no further inference is
authorized under this idea; identifying the mediating
spatial-frequency or noise-texture quantity requires a successor idea
through the normal pipeline. Idea 004 is complete: contract v2
executed validly (425 pairs, 850 volumes, 5 sessions, anchors at zero
deviation), results merged via the record-result gate, interpretation
cross-family reviewed and here ratified.


===== evidence/ledger_digest.md =====
# Ledger digest (auto-generated -- do not edit; run `python scout.py ledger digest`)

109 tracked ideas. Latest state per idea; full history in ledger.jsonl.

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **IDENTIFIABILITY_FAILURE** x3: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_ACCESS** x2: Required data, checkpoints, or mappings are not obtainable in practice.
- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.
- **ANNOTATION_PROVENANCE** x1: Inference depends on who assigned labels / what they could see, and that is undocumented or contaminated.
- **CIRCULARITY** x1: The endpoint is a re-encoding of the input or of the thing being tested.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **scout-015-c04** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.5, audited 2026-08-17] -- The continuous air tunnel inside the hiatal-hernia score
- **scout-015-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.5, audited 2026-08-17] -- The lung-opacity score may be reading gravity
- **scout-013-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.4, audited 2026-08-15] -- Collateral failure written in the cortical veins
- **scout-012-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.2, audited 2026-08-15] -- The dilated esophagus inside the fibrosis score
- **isles24-scout-001-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.1, audited 2026-08-16] -- A spreading front inside the perfusion deficit
- **scout-013-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.1, audited 2026-08-15] -- The vessel map inside the mosaic-attenuation score
- **isles24-scout-002-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.0, audited 2026-08-16] -- The healthy hemisphere is the ruler
- **isles24-scout-001-c07** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.0, audited 2026-08-16] -- Does the model mistake the end of the scan for the end of the bolus?
- **isles24-scout-002-c07** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.9, audited 2026-08-16] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
- **scout-010-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.9, audited 2026-08-12] -- CXR-Age put back together from parts a radiologist can measure
- ... and 55 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- regional-substitution: 14
- counterfactual-synthesis: 12
- conditional-observational: 12
- representation-erasure: 7
- natural-paired: 4
- longitudinal-within-subject: 4
- model-output-perturbation: 3
- regional-removal: 1
- cross-reconstruction: 1
- cross-model-disagreement: 1
- other:remote-perturbation: 1

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
- **idea-020** [REJECTED/DEBATED/baseline] -- A spreading front inside the perfusion deficit -- killed: IDENTIFIABILITY_FAILURE
- **idea-021** [SHORTLISTED/DEBATED/baseline] -- The healthy hemisphere is the ruler
- **idea-022** [PAUSED/DEBATED/wide] -- Does the model mistake the end of the scan for the end of the bolus?
- **idea-023** [SHORTLISTED/CRITIQUED/wide] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
- **idea-024** [SHORTLISTED/SCOUTED/wide] -- The capillary traffic jam hidden behind the same mean transit time
- **idea-025** [SHORTLISTED/SCOUTED/wide] -- The scan is also an actigraph: the model may be reading how much the patient moved
- **isles24-scout-001-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Does the winning model rediscover the collateral clock?
- **isles24-scout-001-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The vascular detour the segmentation model can see
- **isles24-scout-001-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Read the stroke from the blood leaving, not only entering
- **isles24-scout-001-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The frail brain around the threatened territory
- **isles24-scout-001-c05** [SCOUT_ONLY/SCOUTED/baseline] -- A spreading front inside the perfusion deficit
- **isles24-scout-001-c06** [SCOUT_ONLY/SCOUTED/wide] -- The capillary traffic jam hidden behind the same mean transit time
- **isles24-scout-001-c07** [SCOUT_ONLY/SCOUTED/wide] -- Does the model mistake the end of the scan for the end of the bolus?
- **isles24-scout-001-c08** [SCOUT_ONLY/SCOUTED/wide] -- The deconvolution algorithm may have signed the image
- **isles24-scout-002-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The water already in the tissue: does the model read the edema clock?
- **isles24-scout-002-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The healthy hemisphere is the ruler
- **isles24-scout-002-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Two tissues, two death thresholds
- **isles24-scout-002-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The barrier is already leaking
- **isles24-scout-002-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The clot that lets contrast through
- **isles24-scout-002-c06** [SCOUT_ONLY/SCOUTED/wide] -- The scan is also an actigraph: the model may be reading how much the patient moved
- **isles24-scout-002-c07** [SCOUT_ONLY/SCOUTED/wide] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
- **isles24-scout-002-c08** [SCOUT_ONLY/SCOUTED/wide] -- Has the deficit percolated? Volume is what the metric sees; connectivity may be what the model uses
- **scout-001-c05** [SHORTLISTED/?/baseline] -- (untitled)
- **scout-001-c06** [SHORTLISTED/?/baseline] -- (untitled)
- **scout-001-c07** [SHORTLISTED/?/baseline] -- (untitled)
- **scout-002-c02** [SHORTLISTED/?/baseline] -- (untitled)
- **scout-002-c06** [SHORTLISTED/?/baseline] -- (untitled)
- **scout-002-c07** [SHORTLISTED/?/baseline] -- (untitled)
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
- **scout-014-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The fat around the heart inside the CVD-mortality score: finish the observation Chao et al. started
- **scout-014-c02** [SCOUT_ONLY/SCOUTED/baseline] -- Redraw the same airway walls with a sharper pencil: does the peribronchial-thickening score follow Pi10?
- **scout-014-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The cardiomegaly head may be reading the rib cage: Haller index beyond heart volume
- **scout-014-c04** [SCOUT_ONLY/SCOUTED/baseline] -- Sybil was never given the patient's age; the thymus wrote it down anyway
- **scout-014-c05** [SCOUT_ONLY/SCOUTED/baseline] -- Chronic anemia turns the marrow back on: is Merlin reading red marrow, not just pale blood?
- **scout-015-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Measure the fluid behind the pleural-effusion score
- **scout-015-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The missing branches inside Sybil's risk score
- **scout-015-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The portal vein as the cirrhosis model's pressure gauge
- **scout-015-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The continuous air tunnel inside the hiatal-hernia score
- **scout-015-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The lung-opacity score may be reading gravity


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


===== ideas/023/README.md =====
# Idea 023: Little's law in the penumbra: the model may be reading the vasodilatory counterattack

Selected from scouting cycle isles24-002, candidate 7.


===== ideas/023/critique.md =====
# Critique — Idea 023 (isles24-scout-002-c07): Little's law in the penumbra

```
FATAL OBJECTION: NONE
EVIDENCE: ISLES'24 report arXiv:2408.10966 (maps from icobrain cva tracer-kinetics
deconvolution); Zenodo 16731717/16813698; winning-solution paper arXiv:2505.18424
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

No single objection kills this card. But three repairs are mandatory before a
feasibility memo, and one of them (the CBV/MTT degeneracy, §2) quietly narrows
what the deliverable sentence is allowed to mean. The card is unusually honest
about its residual assumptions; the problems below are the ones it did not list.

---

## 1. What I verified (sources checked this stage)

- **Map provenance.** The ISLES'24 report states CTP preprocessing used the
  FDA-cleared clinical software **icobrain cva**: motion correction, temporal
  resampling to 1 frame/s, then perfusion maps "generated using a conventional
  tracer-kinetics deconvolution algorithm" (arXiv:2408.10966). This is the fact
  that drives §2 below. The card never asks how the maps were made; it should.
- **Dataset schema.** Confirmed independently of the keystone screen: the Zenodo
  release contains 149 training cases with per-case Tmax/CBF/CBV/MTT derivatives
  co-registered to NCCT space, CC BY-NC-SA 4.0. **Version churn exists**: the
  record the keystone screen inspected (16731717) is one of several versions;
  16813698 is "v3" (2025-08-12) and itself points to a newer version. Schema is
  stable across the two versions inspected, so the keystone stands, but the
  record/version and file hashes must be pinned at Stage 0.
- **Winning solution.** arXiv:2505.18424: a residual-encoder nnU-Net with
  SynthStrip skull-stripping and custom intensity windowing. The paper does not
  state its exact input-channel configuration and releases no code or checkpoint
  I could find. The card's "self-trained nnU-Net stands in" assumption is
  therefore load-bearing (§4).
- **Prior work / novelty.** The counterfactual literature in this niche perturbs
  *clinical/treatment* variables (Robben et al. 2020, PMID 31683091; Amador et
  al., ScienceDirect S1532046423002885) or ablates whole input channels. I found
  no work that toggles the physiological state jointly encoded by the perfusion
  maps while preserving inter-map consistency. The novelty delta survives this
  critique. Amador's clinical-counterfactual line should be added to
  `novelty_neighbors` as the nearest methodological relative.

## 2. Principal objection: at fixed CBF, CBV and MTT are one channel, not two

A conventional tracer-kinetics deconvolution pipeline derives MTT from the
central volume theorem — MTT := CBV/CBF is typically an algebraic step of the
software, not an independent measurement. icobrain cva's internals are
proprietary, so Stage 0's identity-residual census is the right check, but the
card must face the dilemma it creates, because **both horns cost something**:

- **If the residual is ~0 (identity holds by construction):** the "Little's-law
  identity" is a tautology of the vendor pipeline, not a physiological manifold.
  Two consequences. (a) The "does the model check inter-map consistency" probe
  loses its physiological framing — it is a pure never-seen-input OOD probe
  (idea-006 shape; the card correctly quarantines it, but the "does the model
  know Little's law" interest hook deflates to nothing). (b) More important: the
  confirmatory co-edit moves CBV and MTT **in lockstep at fixed CBF — they carry
  identical information**. A positive result cannot attribute the response to
  "blood volume held up" versus "transit time prolonged." The deliverable
  sentence names the *blood-volume* reserve; the experiment can only ever
  establish use of the *compensation state* (the joint CBV/MTT configuration at
  matched flow deficit). These coincide physiologically but not as
  channel-attribution claims, and a reviewer will read the current sentence as
  the latter.
- **If the residual is large:** the maps do not live on the claimed manifold,
  the co-scaling rule is wrong, and the card's own fallback (edit along the
  empirical joint distribution) applies — which is fine, but then the entire
  Little's-law apparatus contributed nothing (see §6).

**Repair (within the same question):** keep the sentence's own definition —
"capillary volume held at or above mirror-normal while flow falls" is a *state*
description and can stand — but add an explicit prohibited-conclusion: no claim
that the model reads the CBV channel as opposed to the MTT channel; at matched
CBF they are not separable in principle when the identity holds. This is wording
honesty, not a new deliverable, so the claim-identity rule is not triggered.

## 3. The two-sided discriminator is under-designed for its main job

Alternative explanation 1 (the card's own) is the crux: reserve-construct reader
vs. generic monotone-CBV-severity reader. Work the signs through:

- Toggle compensated→collapsed (CBV↓, MTT↓, CBF and Tmax fixed): the construct
  reader predicts infarct probability **rises**. A monotone "low CBV = bad"
  channel reader predicts it **rises too**. Same sign. The toggles as listed in
  `smallest_decisive_experiment` (compensated↔collapsed at three magnitudes)
  therefore do **not** separate the two hypotheses — they separate both from
  "ignores CBV/MTT entirely."
- The separation the card gestures at ("including above-mirror values") requires
  an **explicit above-mirror arm**: push CBV *above* mirror-level at matched
  CBF. The construct reader predicts saturation (already compensated; no further
  benefit), the monotone reader predicts a continued response. That arm is
  mentioned in the alternatives list but absent from the experiment description,
  and it is the only part of the design that earns the word "construct" in the
  deliverable. It is also the arm with the weakest physiological cover story
  (post-ischemic hyperperfusion does occur in infarcted tissue) and the greatest
  OOD risk, so it needs its own empirical-support gate in Stage 0.
- One incidental gain: a monotone-MTT-severity reader ("long MTT = bad")
  predicts the *opposite* sign under the joint toggle, so the basic arm does
  falsify that particular generic reader. Worth stating — it is the one clean
  discrimination the basic toggles do achieve.

**Repair:** promote the above-mirror saturation arm into the confirmatory
design with a prespecified dose-response shape readout (response flattens above
rCBV_mirror = 1 vs. continues), or demote the claim from "uses the reserve
construct" to "uses the compensation state," which is still a finding but a
smaller one. Identifiability at 4 is not defensible until one of these happens;
as written it is a 3.

## 4. The missing Stage 0 gate: does the *label* even carry the interaction?

The card's premise is that "every training case showed the model the
consequence" of the compensated/collapsed difference. That is an assumption
about the ground truth, and it is checkable on CPU before any model exists: at
matched CBF decrement, do final-infarct membership rates actually differ
between compensated and collapsed voxels in the 149 released cases? This is
simultaneously (a) a re-litigation of Wintermark-vs-Campbell on a modern,
reperfusion-treated cohort — a citable side result on its own — and (b) the
precondition for the whole study: **if the labels do not encode the state's
prognostic value at matched CBF, the toggle null is preordained and
uninterpretable as a model finding.** Two aggravating factors make this gate
non-optional: the cohort is all-treated with heterogeneous reperfusion success
(penumbra fate is partly stochastic from the image alone), and n=149. Add it to
Stage 0 alongside the identity-residual and joint-support censuses. The
`anticipated_negative` classification ("decisive") is conditional on this gate
passing and should say so.

## 5. Scope honesty: whose model is being audited?

The deliverable and the anticipated negative speak of "the final-infarct model"
and "what benchmark models internalized." What will actually be probed is a
self-trained nnU-Net, because no challenge checkpoint is confirmed released
(§1). Three consequences:

1. The quotable-negative claim ("siding with the rCBF camp") must be scoped to
   *this model family under this training recipe*, not "benchmark models."
2. The shared-model input specification is silently load-bearing: the edits
   enter through the perfusion-map channels, so the cycle-shared model **must**
   take the four maps as inputs. A raw-4D-CTP model (Amador-style) or an
   NCCT/CTA-dominant model gives the probe no port of entry. This is
   controllable (we train it) but must be prespecified, and it couples c07 to
   every other candidate sharing that checkpoint.
3. With a multimodal input (NCCT+CTA+maps), a weak toggle response is ambiguous
   between "ignores the state" and "NCCT evidence dominates" — established
   hypodensity on NCCT will rationally cap how far a CBV edit can move the
   prediction. Cheap fix, worth adopting: train the maps-only configuration as
   well and run the probe on both; divergence between them is itself
   informative. The Tmax positive control calibrates channel sensitivity but
   not cross-channel dominance.

Stage 0 should also inventory released ISLES'24 participant repositories
(e.g., the official docker template, kimberly-amador/ISLES24-PrediCTP,
Mahsa0M/isles2024_docker) for released *weights*; if any trained submission is
public, probing it alongside the self-trained model materially strengthens the
"benchmark" framing at near-zero cost.

## 6. Analogy audit (charter test: what changes if dropped?)

The card's own answer is half-right. The two-sided deviation-from-mirror
prediction is genuinely load-bearing — but it comes from classical stroke
physiology (Wintermark's autoregulation account), not from control engineering.
Little's law adds nothing beyond the central volume principle, which the CTP
literature has cited under that name since the 1990s; and if §2's first horn
holds, the "manifold constraint" it supplies is the vendor pipeline's algebra.
The experiment would be identical with the queueing/control vocabulary deleted
and "autoregulatory compensation (Wintermark 2006) vs. flow-only (Campbell
2011)" put in its place. This is decoration on top of a real mechanism, not
fluent nonsense — the named quantity and measurement survive the deletion — so
the charter's remedy is rewrite-without-analogy, not discard. The revision
should do that; it will also make the card more legible to the stroke-imaging
reviewer the deliverable sentence is aimed at.

## 7. Kill-attempts that failed (recorded so they are not re-run)

- **Prior-work overlap:** searched; nearest neighbors are channel ablations and
  clinical-variable counterfactuals; no consistency-preserving state toggle
  found (§1). Novelty delta stands.
- **Circularity (idea-010 shape):** X is computed from the model's inputs, but
  the endpoint is output change under input intervention, not a re-encoding of
  the input. Not circular.
- **Label leakage:** ground truth from follow-up MRI; inputs are acute-phase
  only. No path.
- **Annotation provenance:** primary readout is label-free paired deltas; the
  GT enters only through the §4 gate and training, both with documented
  provenance (DOI 10.1148/ryai.250603). The dominant program failure mode does
  not apply.
- **Confounding (scanner/protocol/site):** within-case paired edits hold all of
  it fixed; the mirror ratio kills global scaling. The card's treatment is
  correct.
- **Excessive compute:** ~320 forward passes is trivial; the real costs are the
  one-time ~100 GB archive download (the 99 GB train.7z is monolithic — check
  at Stage 0 whether derivatives can be fetched separately) and the shared
  nnU-Net training, which is a cycle-level cost amortized across the ISLES
  candidates but should stop being invisible in this card's "cheapest wide
  candidate" claim.
- **Unavailable data:** public, CC BY-NC-SA 4.0, no DUA. Fine for this program.
- **idea-016 and idea-006 resemblance:** the card's `dies_like_prior` answers
  are adequate; the mirror ratio and empirical-range bounds are real structural
  differences, and the OOD-flavored identity-violating probe is quarantined.

## 8. Easier versions (low-hanging fruit, in ascending cost)

1. **Model-free, CPU-only (§4 gate as a result):** the GT-interaction census on
   149 cases. Data and labels already exist; no training. If it fails, the
   candidate dies for ~zero cost; if it passes, it is a citable observation
   about the Wintermark/Campbell debate in a treated cohort either way.
2. **Observational stratification (no edits):** once the shared model exists,
   compare its predicted-infarct probability for compensated vs. collapsed
   voxels at matched CBF. Confounded (state correlates with everything), so it
   cannot replace the toggles, but it costs one inference pass over held-out
   cases and yields the effect-size estimate the toggle arm needs for power.
3. **Released-submission probe:** if the Stage 0 checkpoint inventory (§5)
   finds any public trained ISLES'24 submission, run arms 1–2 on it before
   training anything.

These are stages of the same candidate, not separate candidates.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does a map-input final-infarct model
trained on ISLES'24 respond to the autoregulatory compensation state — the
joint CBV/MTT configuration at matched CBF decrement, with an explicit
above-mirror saturation arm — and does the cohort's ground truth even encode
that state's prognostic value at matched flow?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — same deliverable sentence, narrowed
attribution; revision-in-place under the claim-identity rule.
IS IT ACTUALLY WORTH DOING? YES — the §8.1 census alone is worth running this
week on existing public data, and it decides for free whether the rest deserves
GPU time; the full study is worth doing only conditional on that gate.
```


===== ideas/023/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The card names the wrong keystone: co-registered maps make the experiment executable, but the study is uninterpretable unless ISLES'24 final-infarct labels actually encode a prognostic difference between compensated and collapsed tissue at matched CBF deficit.

**Argument:** The claimed mechanism is learned use of an autoregulatory compensation state for tissue salvageability. Yet the 149-case cohort is reperfusion-treated, and final infarct depends on treatment timing and success as well as baseline perfusion; map availability does not establish that voxels with rCBV at or above mirror-normal have different final-infarct membership from low-rCBV voxels after matching on rCBF. If that conditional association is absent, a null toggle response cannot be called a decisive finding that the model “sides with the rCBF camp”: the training target supplied no detectable compensation-state lesson, so failure to learn it is preordained or sensitivity-limited. Conversely, a positive toggle response could reflect a model exploiting a channel pattern without that pattern being outcome-relevant in this cohort. This is the charter's wrong-keystone error: the inspected adjacent fact is that all maps coexist in NCCT space; the load-bearing fact is that the outcome supports the interaction the deliverable attributes to salvageability. The repair remains the original question and does not trigger a claim-identity change: before model training or edits, prespecify a patient-clustered, held-out model-free census testing final-infarct risk across compensated versus collapsed states within matched-rCBF strata, with treatment/reperfusion variables handled if released, an effect-size precision requirement, and a minimum joint-support gate. Until that passes, the proposed negative is not decisive and `negative_result_value` cannot remain 4.

**What would change my mind:** Show a frozen Stage 0 analysis plan and results on the released ISLES'24 cases demonstrating adequate joint support and a precisely estimated, directionally consistent difference in final-infarct membership between compensated and collapsed voxels at matched rCBF, robust to patient clustering and available reperfusion/treatment covariates; or narrow the claim to model use of an input-map state without calling it a salvageability signal, which would be a different candidate under the claim-identity rule.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card verified the executability fact (four maps coexist in NCCT space) but the load-bearing fact is different: unless the released final-infarct labels themselves show, at matched rCBF decrement, a prognostic difference between compensated and collapsed voxels, the toggle experiment is uninterpretable — the "decisive" negative is preordained, and `negative_result_value: 4` and `keystone_status: INSPECTED_TRUE` overstate the card's position.

**Response:** AMEND

**Argument:** The objection is substantially correct and I adopt its repair in full; critique §4 identified the same missing gate independently, so this amendment discharges both. One narrow point is rebutted at the end.

What changes in the card, exactly:

1. **The keystone is split into two named parts.** K1 (executability): per-case CBV/CBF/MTT/Tmax maps co-registered in NCCT space — remains `INSPECTED_TRUE` on the Zenodo/GitHub schema evidence. K2 (interpretability, the load-bearing one the critic names): *final-infarct membership differs, directionally and with adequate precision, between compensated (rCBV_mirror ≥ 1) and collapsed (rCBV_mirror < 1) voxels within matched rCBF-decrement strata in the released 149-case cohort.* K2 becomes the card's `keystone_prerequisite`; its status is `NOT_INSPECTED`. Per the charter's caps, **feasibility drops 4 → 3** until K2 is measured. The mitigating fact — and the reason this is an amendment rather than a concession — is that K2 is directly measurable on CPU from released public data with no annotator, before any training or download of model machinery. This is the rare instance where the wrong-keystone trap is escapable by measurement rather than by assumption, and the card should have said so itself.

2. **A prespecified, frozen Stage 0 gate (G-label) is added ahead of all model work.** Frozen before any voxel of the label data is examined: (a) prespecified rCBF_mirror-decrement bins; (b) within each bin, compare final-infarct membership rates for compensated vs. collapsed voxels; (c) patient-clustered inference (cluster bootstrap over the 149 patients), never pooled-voxel CIs; (d) a minimum joint-support requirement — at least N patients each contributing at least M voxels of *both* states within the same bin, N and M fixed in the frozen plan before data touch; (e) a precision requirement on the stratum-wise risk difference (maximum CI width), not merely a significance test; (f) directional consistency across bins; (g) a prior inventory of released clinical variables — if reperfusion status (e.g., mTICI) or treatment-timing fields are in the release, the census stratifies or adjusts on them; if they are absent, that absence is recorded as a scope limit on the salvageability wording, not silently ignored. Holding out cases from the census for the later toggle arm (the critic's "held-out" condition) is adopted: the census freezes on a split, and the toggle arm's 40 cases come from the complement.

3. **Consequences are reclassified as conditional.** `anticipated_negative` = decisive holds **only conditional on G-label passing**; the card now says so in the field itself. If G-label fails, the toggle experiment is not run, the candidate PAUSEs, and the census result stands alone as the deliverable — which has independent worth either way: it is a direct re-litigation of the Wintermark-2006 vs. Campbell-2011 core-definition debate on a modern, reperfusion-treated cohort, a citable observation under the charter's "evidence that a popular assumption is unsupported" success class. `negative_result_value` stays 4 only as a conditional score with the condition printed in the `why`; unconditionally it is the census, not the toggle null, that carries guaranteed value.

4. **What was lost.** This is not free. The negative's decisiveness is now conditional rather than intrinsic; feasibility drops a point until Stage 0 runs; the "cheapest wide candidate this cycle" claim must absorb a mandatory CPU census and the ~100 GB archive download earlier in the critical path; and there is now a named, prespecified way for the candidate to die before any model exists. I consider that last item a feature, but it is honestly a narrowing of what the card promised.

**Partial rebuttal — the positive arm.** The critic writes that a positive toggle response "could reflect a model exploiting a channel pattern without that pattern being outcome-relevant in this cohort," implying the positive is also hostage to K2. Half of that is right and already handled: the salvageability *wording* of the deliverable sentence is conditional on G-label, and with the §2 critique repair the confirmatory claim is about the compensation *state*, with channel-level attribution prohibited. But the rung-1 content of a positive — *this model's output responds, signed and paired, to the compensation state at matched CBF* — is a fact about the model that no property of the labels can retroactively falsify. If G-label failed and a toggle response nonetheless existed, that would be a learned reliance the training target does not support — a shortcut-flavored finding with a different, weaker sentence. The amended design orders the stages so this ambiguity never arises (census first; toggles only on pass), but the asymmetry matters for scoring: K2 gates the *interpretation* and the *negative*, not the existence of the rung-1 positive. That is why the amendment conditions the wording and the negative's classification on G-label rather than making the whole candidate's meaning contingent on it.

**Identity check:** the one-sentence question — is the model using the blood-volume reserve, read against CBF, to separate salvageable from lost tissue — is unchanged; the deliverable sentence is unchanged; the gate is a precondition inserted before the same experiment. The critic's own round states the repair "remains the original question and does not trigger a claim-identity change." Revision-in-place.

**Spin-off (noted, not debated):** if G-label *fails*, the census itself — "in a treated 2024 cohort, the CBV/CBF interaction the pre-2011 literature built core definitions on is absent from final-infarct outcomes" — could re-enter as a standalone model-free candidate.

**Status:** OPEN

## Round 2 — CRITIC

**Position:** The G-label amendment preserves the original question and resolves the keystone objection, but the proposed toggle still cannot distinguish use of an autoregulatory compensation construct from a generic monotone response to CBV/MTT.

**Argument:** I concede Round 1 because the proposer adopted the load-bearing K2, made it `NOT_INSPECTED`, capped feasibility at 3, and conditioned both the salvageability interpretation and decisive-negative claim on a prespecified patient-clustered outcome census; those are substantive arguments and gates, not restatement. The identity check also passes: G-label is a prerequisite for the same question, not a substitute endpoint. The strongest remaining defect is identifiability. In the stated compensated-to-collapsed edit, CBV falls and MTT is co-scaled downward while CBF and Tmax are fixed. Both the claimed construct reader (loss of reserve means greater infarct probability) and a generic monotone low-CBV severity reader predict the same signed increase. Reversing that edit adds no discrimination; it merely reverses both predictions. Because conventional deconvolution may make MTT algebraically dependent on CBV/CBF, the design also cannot attribute the effect to CBV rather than MTT, as the critique already notes. The card gestures toward “including above-mirror values,” but neither the amended Stage 0 plan nor `smallest_decisive_experiment` makes an above-mirror saturation arm confirmatory or gives it an empirical-support gate and a prespecified response-shape contrast. Without that arm, a positive result supports only “the model uses the joint CBV/MTT compensation-state channels at matched CBF,” not the deliverable’s stronger claim that it uses blood-volume reserve as a tissue-salvageability construct. This is not an identity-changing repair: explicitly testing saturation once rCBV reaches mirror-normal directly operationalizes the original reserve question. If that arm is infeasible or unsupported, the weaker channel-state sentence must become a separate successor because it changes the deliverable claim.

**What would change my mind:** Amend the confirmatory design to include an empirically supported above-mirror arm, gated in Stage 0, with a frozen dose-response contrast that distinguishes saturation at rCBV_mirror approximately 1 from a continuing monotone CBV/MTT response, plus the explicit prohibited conclusion that the experiment cannot separate CBV-channel use from MTT-channel use when the central-volume identity holds.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** With the G-label gate settled, the surviving defect is identifiability of the *construct*: the compensated-to-collapsed toggle (and its reverse) produces the same signed prediction from a reserve-construct reader and from a generic monotone low-CBV/short-MTT severity reader, so as designed the confirmatory arm cannot earn the word "reserve." The only discriminating test — saturation of the response above rCBV_mirror ≈ 1 — is currently a gesture in the alternatives list, not a gated confirmatory arm; and when the central-volume identity holds, CBV and MTT carry identical information at fixed CBF, so channel-level attribution is impossible in principle.

**Response:** AMEND

**Argument:** The sign analysis is correct and I will not relitigate it: below mirror level, both hypotheses predict the same direction, and reversing the edit reverses both predictions together. Critique §3 reached the identical conclusion independently. The two-sided toggle separates "uses the CBV/MTT state at matched CBF" from "ignores it," and separates a monotone-MTT reader (which predicts the opposite sign under the joint co-scaled edit — the one clean discrimination the basic arm does achieve, now stated in the card); it does not separate construct from monotone-CBV reader. The amendment adopts the critic's change-my-mind conditions in full, item by item:

1. **The above-mirror saturation arm becomes confirmatory.** Third toggle family, same within-case paired machinery: at matched CBF and Tmax, CBV is moved *above* mirror level (MTT co-scaled to stay on the manifold), in steps spanning the empirically observed above-mirror range in cohort deficit tissue. The frozen, prespecified readout is a **dose-response shape contrast**, not a threshold on any single delta: the construct hypothesis predicts the response flattens at rCBV_mirror ≈ 1 (below-mirror segment slope large, above-mirror segment slope compatible with the sham-derived noise floor); the monotone hypothesis predicts the above-mirror slope continues with the same sign as below. The contrast statistic (ratio of segment slopes with patient-clustered CIs, segments and step grid fixed in advance) is frozen in the probe contract before any model inference. A monotone continuation is itself reportable: "the model treats CBV as unbounded severity, not as a reserve with a ceiling" — a directional finding either way, which is what makes this arm confirmatory rather than exploratory.

2. **The arm gets its own Stage 0 empirical-support gate (G-hyper).** The same CPU census that runs G-label counts, per patient and per rCBF-decrement bin, deficit-tissue voxels with rCBV_mirror > 1 natively present in the cohort (post-ischemic hyperperfusion and luxury-perfusion states make this plausible, but plausibility is not support). Edit bounds are capped at the observed above-mirror quantiles; the discriminator/in-distribution gate applies to this arm separately, because it is the arm with the weakest physiological cover story and the greatest OOD risk. If G-hyper fails — insufficient native above-mirror support at matched CBF — the arm does not run.

3. **The prohibited conclusion is added to the card verbatim.** No claim that the model reads the CBV channel as opposed to the MTT channel: when the released maps satisfy the central-volume identity, CBV and MTT at fixed CBF are one degree of freedom, and the Stage 0 identity-residual census determines whether that degeneracy holds by construction. The deliverable sentence already names a *state* ("capillary volume held at or above mirror-normal while flow falls"), and the card now says explicitly that this is a state claim, never a channel-attribution claim.

4. **Scores follow the design as written, not as promised.** `identifiability` drops 4 → 3 in the card now, with the `why` stating it returns to 4 only if G-hyper passes and the saturation arm runs as confirmatory. This mirrors the feasibility 4 → 3 cap from round 1: the score reflects what has been gated, not what is hoped.

**What was lost.** More than round 1's amendment. (a) The strong claim — "uses the reserve as a construct" — is now hostage to the single most OOD-fragile arm of the design; the card acquires a second named death path (G-hyper) alongside G-label. (b) If G-hyper fails, the candidate cannot silently narrow to "uses the joint CBV/MTT compensation-state channels": the critic is right, and I accept, that this weaker sentence is a *different deliverable* under the claim-identity rule. In that world the candidate PAUSEs and the channel-state question registers as a successor with parent_id, re-entering through a normal cycle — no inherited queue position. That is the honest price: the original question now has two prespecified ways to die before its decisive arm runs, and one of them demotes rather than kills, into a successor I do not get to keep. (c) This is amendment two of two rounds. The standing rule says three amendments usually means the idea was wrong; I note the trajectory. My defense of stopping at two: both amendments installed gates *in front of* the original experiment demanded by two independent reviews (critique §§3–4 and both critic rounds converge on the same repairs); neither changed the question, the deliverable sentence, or the toggle machinery itself. If the next objection requires changing what the sentence claims, the idea was wrong and I will say so.

**Identity check:** the one-sentence question — is the model using the blood-volume reserve, read against CBF, to separate salvageable from lost tissue — is unchanged. The saturation arm does not replace that question; it is the part of the design that finally *operationalizes* the word "reserve" (a reserve is exactly the thing whose marginal value vanishes once replenished — flattening above mirror level is what "reserve" means in prediction space). The critic's own round states this repair is not identity-changing. Revision-in-place.

**Status:** OPEN

## Round 3 — CRITIC

**Position:** The saturation amendment preserves the original question but assumes, rather than establishes, that autoregulatory blood-volume reserve must produce a prediction kink at `rCBV_mirror = 1`, so its confirmatory contrast still does not identify the claimed construct.

**Argument:** Round 2's amendment adequately accepts the channel-degeneracy limit, makes the above-mirror arm confirmatory, and correctly pauses rather than silently changing the deliverable if G-hyper fails; those are substantive repairs, and the identity check passes. The remaining problem is the discriminator's physiological premise. Mirror-normal CBV is a reference value, not a demonstrated ceiling on autoregulatory vasodilation or on the prognostic value of blood volume. The card's own Wintermark framing permits normal-to-*increased* CBV in penumbra, and G-hyper explicitly expects native deficit tissue above 1. A genuine reserve reader could therefore continue changing its output above `rCBV_mirror = 1` because progressively elevated CBV may encode greater vasodilation, collateral filling, delay, or reperfusion state; conversely, a generic nonlinear CBV/MTT reader could flatten near 1 because of training-density saturation or network calibration. Thus the proposed slope ratio has no unique mapping: continuation does not refute construct use, and flattening does not establish it. G-label only tests compensated-versus-collapsed outcome association after dichotomizing at the same assumed boundary, while G-hyper only establishes support, so neither validates the kink prediction. This matters at rung 3: the design can identify use of a nonlinear joint CBV/MTT state at matched CBF, but it cannot call that nonlinearity “autoregulatory reserve” without an independently justified physiological response shape. The amendment therefore operationalizes the original words but not yet the original mechanism.

**What would change my mind:** Show primary-source or independent cohort evidence that, at matched CBF deficit and relevant reperfusion status, tissue outcome or a separately measured autoregulatory endpoint has a prespecified plateau or change point at (or estimably near) mirror-normal CBV; then freeze that externally derived shape before probing the model. Alternatively, measure an independent autoregulatory quantity available in the cases and show that the proposed CBV/MTT dose-response discriminates it from flexible monotone and saturating channel-only baselines. Without one of those facts, the weaker joint-state claim must be a successor candidate.

**Status:** OPEN


===== ideas/023/idea_card.json =====
{
  "id": "isles24-scout-002-c07",
  "track": "wide",
  "title": "Little's law in the penumbra: the model may be reading the vasodilatory counterattack",
  "question": "Is an ISLES'24 model using the autoregulatory blood-volume reserve -- capillary beds held open while flow falls, CBV read against CBF -- to separate tissue that will survive reperfusion from tissue already lost?",
  "cross_field": {
    "borrowed_construct": "Control engineering: cerebral autoregulation is a feedback controller that defends delivery (CBF) by actuating vessel caliber; controller state is read from the ACTUATOR signal (CBV), not the controlled variable. Queueing theory supplies the bookkeeping: the central volume principle CBV = CBF x MTT is literally Little's law (L = lambda x W) -- a compensating region is a queue that lengthened to preserve throughput; a collapsed region has lost both.",
    "instrument_it_implies": "A voxelwise actuator-state index: CBV relative to its mirror-homologous voxel, stratified by CBF decrement -- 'compensating' (rCBV_mirror >= 1 at reduced CBF) versus 'collapsed' (rCBV_mirror < 1) -- plus a Little's-law identity residual (does CBV = CBF x MTT hold in the released maps?) that both gates and disciplines the edits.",
    "what_changes_if_dropped": "The measurement survives (CBV/CBF thresholds are classical stroke imaging), but the controller framing supplies the two-sided prediction (deviation-from-mirror sign, not CBV level) that separates construct use from generic channel use, and Little's law supplies the manifold constraint that keeps edits physiological."
  },
  "deliverable_sentence": "The final-infarct model is using the autoregulatory blood-volume reserve -- capillary volume held at or above mirror-normal while flow falls -- as its tissue-salvageability signal, distinguishing the still-compensating penumbra from the collapsed core at matched flow deficit.",
  "X_measurement": "rCBV_mirror = CBV / CBV_mirror per voxel from the released CBV maps registered to NCCT space, mirror via automatic midsagittal symmetry estimation, stratified by rCBF_mirror decrement. Clinical anchors: preserved autoregulation in penumbra produces vasodilation and normal-to-increased CBV while the core loses autoregulation and CBV collapses (Wintermark et al., Stroke 2006, DOI 10.1161/01.STR.0000209238.61459.39; review PMC2686422); the field later pivoted to rCBF<31% as the better core definition (Campbell et al., Stroke 2011, DOI 10.1161/STROKEAHA.111.618355), and a porcine CTP-PET study found the CBV infarction threshold varies with CBF -- the interaction beats either alone (PMC4922566). Compute-today test: YES -- released registered maps plus automatic mirroring; no annotator.",
  "suspected_signal": "Whether tissue is still defending itself is written in the actuator: at equal flow deficit, tissue with dilated, filled capillary beds is physiologically salvageable, while tissue whose blood volume has collapsed has lost microvascular integrity. Every training case -- final infarct conditioned on reperfusion -- showed the model the consequence of this difference.",
  "use_vs_association": "Within-case counterfactual that toggles the controller state: at fixed CBF and Tmax, move CBV inside the perfusion deficit between compensated (mirror-level) and collapsed (core-like) values, co-scaling MTT to preserve the Little's-law identity so edits stay on the physiological manifold; a paired, signed change in predicted final infarct under compensated-to-collapsed toggles, absent under off-deficit shams, distinguishes use of the reserve from CBV merely covarying with severity. A deliberate identity-VIOLATING probe (CBV moved without MTT) is run separately to ask whether the model even checks inter-map consistency -- informative either way, never pooled with the confirmatory arm.",
  "keystone_prerequisite": "Per-case CBV, CBF, MTT, and Tmax maps coexist co-registered in a common (NCCT) space so mirror indices and joint channel edits run automatically on every case.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "Official repository (github.com/ezequieldlrosa/isles24, fetched 2026-08-16): derivatives contain 'Perfusion maps registered to NCCT space'; Zenodo record 16731717 (DOI 10.5281/zenodo.16731717, fetched 2026-08-16) lists perfusion parametric maps (Tmax, CBF, CBV, MTT) per case with 'separate raw and co-registered derivative versions'.",
  "keystone_residual_assumption": "Still assumed: (1) the released maps approximately satisfy CBV = CBF x MTT -- vendor scaling can break the analytic identity, so Stage 0 measures the identity residual and, if it fails, co-edits follow the empirical joint (CBF,CBV,MTT) distribution instead; (2) mirror integrity (bilateral chronic disease, midline shift) -- per-case symmetry-quality flags, machinery shared with baseline c02; (3) a self-trained nnU-Net stands in for challenge submissions.",
  "dies_like_prior": "Closest kill is idea-016 (IDENTIFIABILITY_FAILURE via protocol): absolute CBV moves with injection protocol and cardiac output, but the mirror ratio and the within-case edits remove protocol by construction. idea-006 (OOD intervention) is answered by bounding toggles to the empirically observed rCBV_mirror range within cohort penumbra and core, manifold-consistent co-editing, and a discriminator gate. Adjacencies disclosed: baseline c02 asks what REFERENCE FRAME the model computes (contralateral normalization); c07 asks whether a specific physiological STATE read in that frame is used -- different X, shared mirroring machinery. isles24-scout-001-c01 (collateral clock) is upstream physiology: the CBV reserve is partly filled by collaterals, so the deliverable names the map-level signature (volume held up at low flow) and stays agnostic about whether autoregulatory dilation or collateral inflow fills it -- rung-honest wording, stated now.",
  "closest_prior_work": "The CBV-versus-CBF war for defining core was fought entirely with hand-set thresholds on patients (Wintermark 2006 for CBV; Campbell 2011 for rCBF; interaction evidence in PMC4922566) and then the field moved to end-to-end models (Robben et al., Med Image Anal 2020, PMID 31683091, arXiv:1812.02496 -- deconvolution-free prediction with metadata ablations; ISLES'24 report arXiv:2408.10966) without ever asking which side of its own debate the models internalized. Exact delta: channel-ablation studies remove whole input maps; nobody has toggled the physiological state the maps jointly encode while preserving their internal consistency.",
  "novelty_neighbors": [
    "Wintermark M et al., 'Perfusion-CT assessment of infarct core and penumbra', Stroke 2006 (DOI 10.1161/01.STR.0000209238.61459.39) -- CBV-based core definition; human thresholds, no learned model.",
    "Campbell BCV et al., 'Cerebral blood flow is the optimal CT perfusion parameter for assessing infarct core', Stroke 2011 (DOI 10.1161/STROKEAHA.111.618355) -- the debate's other side; still human thresholds.",
    "Robben D et al., 'Prediction of final infarct volume from native CT perfusion and treatment parameters using deep learning', Med Image Anal 2020 (PMID 31683091, arXiv:1812.02496) -- end-to-end model with input/metadata ablations; no physiological-state manipulation within inputs."
  ],
  "novelty_delta": "No found work tests whether an end-to-end final-infarct model uses the autoregulation-reserve construct -- CBV read against CBF at matched flow deficit -- as opposed to using CBV as one more severity channel; the two-sided mirror-referenced toggle is the new move.",
  "why_not_done": "BLIND_SPOT: the field litigated CBV-versus-CBF for human-defined core masks, declared rCBF the winner, and switched to end-to-end learning -- leaving unasked whether the models quietly re-adopted the losing (or a richer, interaction-form) construct.",
  "existing_assets": "Registered CBV/CBF/MTT/Tmax maps for 149 public cases; automatic symmetry-plane tools shared with baseline c02; exact published threshold numbers (CBV core, rCBF<31%, CBFxCBV interaction) to compare the model's behavior against; the cycle-shared baseline model.",
  "smallest_decisive_experiment": "Stage 0 (CPU): Little's-law identity-residual census and empirical joint (CBF,CBV,MTT) distributions in deficit versus mirror tissue on all 149 cases, plus a joint-support census (do both controller states occur at matched CBF decrement?). Decisive arm: 40 held-out cases, compensated-to-collapsed and collapsed-to-compensated toggles at three magnitudes plus off-deficit shams plus the identity-violating probe (~40 x 8 forward passes); primary readout is the paired, label-free, signed change in predicted lesion probability mass at matched CBF.",
  "compute_envelope": "Fits one Colab GPU session given the cycle-shared checkpoint: map arithmetic and mirroring are CPU-trivial; ~320 forward passes are under 2 GPU-hours. Cheapest wide candidate this cycle.",
  "standing_confounds_addressed": "Within-case edits hold patient, protocol, scanner, and site fixed; the mirror ratio removes global scaling (cardiac output, injection); matched-CBF stratification carries the observational arm; manifold co-editing preserves inter-channel consistency so the model cannot respond merely to a broken identity. Not ruled out: the reserve signature does not distinguish autoregulatory dilation from collateral inflow (deliberately absorbed into the claim's wording); perfusion-map smoothing across the deficit boundary (eroded ROIs); Tmax is held fixed although delay physiology is entangled with both states.",
  "alternative_explanations": [
    "The model reads CBV as a generic monotone severity channel, not a reserve: a construct reader responds to the sign of deviation-from-mirror at matched CBF, a generic reader responds monotonically to CBV level including above-mirror values -- the two-sided toggle separates them.",
    "The response is an edit artifact: discriminator gate, off-deficit shams, and physiologic-range bounds.",
    "The model derives its prediction from Tmax alone and ignores the CBV/CBF/MTT triplet: then toggles do nothing while the Tmax positive control still moves the output -- itself a crisp channel-use finding."
  ],
  "anticipated_negative": "With gates and the positive control passing, a null is a positive claim: the model's salvageability estimate ignores the blood-volume reserve, siding entirely with the rCBF camp of the field's oldest CTP debate -- a quotable statement about what benchmark models internalized, and a caution for anyone proposing CBV-derived inputs.",
  "verified_dataset_facts": "Relies on (verified 2026-08-16, scout_candidates.json dataset_verification): perfusion parametric maps (Tmax, CBF, CBV, MTT) per case with co-registered derivative versions in NCCT space (Zenodo 16731717 description; official repository derivatives listing); 149 public training cases, CC BY-NC-SA 4.0; final-infarct ground truth from follow-up MRI conditioned on reperfusion (DOI 10.1148/ryai.250603, carried).",
  "design_template": "counterfactual-synthesis",
  "scores": {
    "clarity": {
      "value": 4,
      "why": "One construct, one signed two-sided test; 'reserve' requires the matched-CBF qualifier to be stated every time, which costs it the 5."
    },
    "identifiability": {
      "value": 4,
      "why": "Within-case toggles on the physiological manifold with sign predictions separate construct use from channel use; the collateral-versus-autoregulation ambiguity is absorbed into honest wording rather than resolved."
    },
    "medical_relevance": {
      "value": 4,
      "why": "Which tissue-fate construct the models internalize decides how their outputs should be trusted under hemodynamic variation, and speaks directly to the still-live CBV/CBF debate in core definition."
    },
    "interest": {
      "value": 4,
      "why": "Re-opens the field's foundational CTP debate inside its own benchmark models; the identity-checking probe (does the model know Little's law?) is a bonus hook."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Thresholds, physiology, registered maps, and mirroring machinery all exist; only the shared model must be trained."
    },
    "feasibility": {
      "value": 4,
      "why": "Keystone INSPECTED_TRUE; parametric map edits and a few hundred forward passes -- the cheapest decisive arm this cycle."
    },
    "data_readiness": {
      "value": 4,
      "why": "Everything needed is in the public co-registered derivatives; noncommercial license."
    },
    "evaluation_readiness": {
      "value": 4,
      "why": "Label-free paired signed deltas with standard gates; published threshold numbers provide external comparison points."
    },
    "negative_result_value": {
      "value": 4,
      "why": "A gated null is a directional claim (pure-flow reliance) with a named consequence for CBV-derived input proposals."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Targeted search found the threshold literature and ablation studies but no state-toggle audit; held at 3 pending the novelty stage."
    },
    "regret": {
      "value": 4,
      "why": "The debate's numbers and the benchmark's models are one experiment apart; obvious in hindsight once stated."
    }
  },
  "unverified_claims": [
    "Little's-law identity residual in the released maps (vendor scaling)",
    "joint support of both controller states at matched CBF in this cohort",
    "in-distribution validity of state toggles",
    "mirror integrity rates in this cohort"
  ],
  "charter": "isles24"
}


===== ideas/023/keystone_screen.md =====
# Keystone screen

## Keystone as stated

> Per-case CBV, CBF, MTT, and Tmax maps coexist co-registered in a common (NCCT) space so mirror indices and joint channel edits run automatically on every case.

## What I inspected

I inspected the official ISLES'24 GitHub repository's data schema and the official Zenodo release record for the public training archive, rather than relying on an abstract or search result.

The official Zenodo record states that the release contains 149 training cases and then makes the per-case completeness claim explicitly:

> “For each case, the following data are included: Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

Source: https://zenodo.org/records/16731717, **Description**, opening paragraph and first bullet under the case contents (record metadata inspected through https://zenodo.org/api/records/16731717 on 2026-08-17).

The same record defines the derivative-space relationship:

> “'Derivatives' include all modalities linearly co-registered to the NCCT space.”

Source: https://zenodo.org/records/16731717, **Data structure** paragraph.

Its displayed derivative schema places all four files under the same subject, acute session, and `perfusion-maps` directory, with `space-ncct` in every filename:

> “sub-strokecase0001_ses-0001_space-ncct_tmax.nii.gz”  
> “sub-strokecase0001_ses-0001_space-ncct_mtt.nii.gz”  
> “sub-strokecase0001_ses-0001_space-ncct_cbf.nii.gz”  
> “sub-strokecase0001_ses-0001_space-ncct_cbv.nii.gz”

Source: https://zenodo.org/records/16731717, **Data structure**, `derivatives/sub-strokecase0001/ses-0001/perfusion-maps/` listing. The same four-file layout is independently reproduced in the official repository at https://github.com/ezequieldlrosa/isles24/blob/main/README.md, lines 26–35.

These statements jointly verify the stated prerequisite: the four named maps coexist per case and derivative versions are in NCCT space. This is schema-level inspection of the official release, not a census of the headers inside the 99 GB `train.7z` archive.

## Residual-assumption check

**Mandatory question:** If this card only verified the nearest checkable thing, what is it still assuming?

The nearest fact would have been merely that the release contains four map *types*. The additional load-bearing facts are that they coexist for each case and that the derivative copies share NCCT physical space. The official release description explicitly verifies both, so the card did not stop at the nearest fact.

One narrower implementation assumption remains: “co-registered to NCCT space” does not verbatim promise byte-identical NIfTI dimensions, voxel sizes, or affine matrices across the four files. That does not overturn the stated keystone because common NCCT physical space permits deterministic resampling before voxelwise measurement or editing. A header census should nevertheless gate later work; missing files or irreconcilable affine/coverage differences would be a release-integrity exception, not evidence currently contradicting the official per-case schema.

The card also assumes that mirror estimation will be reliable and that the map values have usable joint support and scaling. Those are explicitly listed Stage 0 validity gates. They affect interpretability of the proposed experiment but are not substitutes for the present data-existence/co-registration keystone.

```json
{"verdict": "PASS", "evidence": "For each case, the following data are included: Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).", "source": "https://zenodo.org/records/16731717 — Description, first case-contents bullet; paired with Data structure statement that derivatives include all modalities linearly co-registered to NCCT space", "note": "Official release schema verifies per-case coexistence and common NCCT space; exact NIfTI grid/header compatibility remains a cheap Stage 0 census."}
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
This is round 3. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The card names the wrong keystone: co-registered maps make the experiment executable, but the study is uninterpretable unless ISLES'24 final-infarct labels actually encode a prognostic difference between compensated and collapsed tissue at matched CBF deficit.

**Argument:** The claimed mechanism is learned use of an autoregulatory compensation state for tissue salvageability. Yet the 149-case cohort is reperfusion-treated, and final infarct depends on treatment timing and success as well as baseline perfusion; map availability does not establish that voxels with rCBV at or above mirror-normal have different final-infarct membership from low-rCBV voxels after matching on rCBF. If that conditional association is absent, a null toggle response cannot be called a decisive finding that the model “sides with the rCBF camp”: the training target supplied no detectable compensation-state lesson, so failure to learn it is preordained or sensitivity-limited. Conversely, a positive toggle response could reflect a model exploiting a channel pattern without that pattern being outcome-relevant in this cohort. This is the charter's wrong-keystone error: the inspected adjacent fact is that all maps coexist in NCCT space; the load-bearing fact is that the outcome supports the interaction the deliverable attributes to salvageability. The repair remains the original question and does not trigger a claim-identity change: before model training or edits, prespecify a patient-clustered, held-out model-free census testing final-infarct risk across compensated versus collapsed states within matched-rCBF strata, with treatment/reperfusion variables handled if released, an effect-size precision requirement, and a minimum joint-support gate. Until that passes, the proposed negative is not decisive and `negative_result_value` cannot remain 4.

**What would change my mind:** Show a frozen Stage 0 analysis plan and results on the released ISLES'24 cases demonstrating adequate joint support and a precisely estimated, directionally consistent difference in final-infarct membership between compensated and collapsed voxels at matched rCBF, robust to patient clustering and available reperfusion/treatment covariates; or narrow the claim to model use of an input-map state without calling it a salvageability signal, which would be a different candidate under the claim-identity rule.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card verified the executability fact (four maps coexist in NCCT space) but the load-bearing fact is different: unless the released final-infarct labels themselves show, at matched rCBF decrement, a prognostic difference between compensated and collapsed voxels, the toggle experiment is uninterpretable — the "decisive" negative is preordained, and `negative_result_value: 4` and `keystone_status: INSPECTED_TRUE` overstate the card's position.

**Response:** AMEND

**Argument:** The objection is substantially correct and I adopt its repair in full; critique §4 identified the same missing gate independently, so this amendment discharges both. One narrow point is rebutted at the end.

What changes in the card, exactly:

1. **The keystone is split into two named parts.** K1 (executability): per-case CBV/CBF/MTT/Tmax maps co-registered in NCCT space — remains `INSPECTED_TRUE` on the Zenodo/GitHub schema evidence. K2 (interpretability, the load-bearing one the critic names): *final-infarct membership differs, directionally and with adequate precision, between compensated (rCBV_mirror ≥ 1) and collapsed (rCBV_mirror < 1) voxels within matched rCBF-decrement strata in the released 149-case cohort.* K2 becomes the card's `keystone_prerequisite`; its status is `NOT_INSPECTED`. Per the charter's caps, **feasibility drops 4 → 3** until K2 is measured. The mitigating fact — and the reason this is an amendment rather than a concession — is that K2 is directly measurable on CPU from released public data with no annotator, before any training or download of model machinery. This is the rare instance where the wrong-keystone trap is escapable by measurement rather than by assumption, and the card should have said so itself.

2. **A prespecified, frozen Stage 0 gate (G-label) is added ahead of all model work.** Frozen before any voxel of the label data is examined: (a) prespecified rCBF_mirror-decrement bins; (b) within each bin, compare final-infarct membership rates for compensated vs. collapsed voxels; (c) patient-clustered inference (cluster bootstrap over the 149 patients), never pooled-voxel CIs; (d) a minimum joint-support requirement — at least N patients each contributing at least M voxels of *both* states within the same bin, N and M fixed in the frozen plan before data touch; (e) a precision requirement on the stratum-wise risk difference (maximum CI width), not merely a significance test; (f) directional consistency across bins; (g) a prior inventory of released clinical variables — if reperfusion status (e.g., mTICI) or treatment-timing fields are in the release, the census stratifies or adjusts on them; if they are absent, that absence is recorded as a scope limit on the salvageability wording, not silently ignored. Holding out cases from the census for the later toggle arm (the critic's "held-out" condition) is adopted: the census freezes on a split, and the toggle arm's 40 cases come from the complement.

3. **Consequences are reclassified as conditional.** `anticipated_negative` = decisive holds **only conditional on G-label passing**; the card now says so in the field itself. If G-label fails, the toggle experiment is not run, the candidate PAUSEs, and the census result stands alone as the deliverable — which has independent worth either way: it is a direct re-litigation of the Wintermark-2006 vs. Campbell-2011 core-definition debate on a modern, reperfusion-treated cohort, a citable observation under the charter's "evidence that a popular assumption is unsupported" success class. `negative_result_value` stays 4 only as a conditional score with the condition printed in the `why`; unconditionally it is the census, not the toggle null, that carries guaranteed value.

4. **What was lost.** This is not free. The negative's decisiveness is now conditional rather than intrinsic; feasibility drops a point until Stage 0 runs; the "cheapest wide candidate this cycle" claim must absorb a mandatory CPU census and the ~100 GB archive download earlier in the critical path; and there is now a named, prespecified way for the candidate to die before any model exists. I consider that last item a feature, but it is honestly a narrowing of what the card promised.

**Partial rebuttal — the positive arm.** The critic writes that a positive toggle response "could reflect a model exploiting a channel pattern without that pattern being outcome-relevant in this cohort," implying the positive is also hostage to K2. Half of that is right and already handled: the salvageability *wording* of the deliverable sentence is conditional on G-label, and with the §2 critique repair the confirmatory claim is about the compensation *state*, with channel-level attribution prohibited. But the rung-1 content of a positive — *this model's output responds, signed and paired, to the compensation state at matched CBF* — is a fact about the model that no property of the labels can retroactively falsify. If G-label failed and a toggle response nonetheless existed, that would be a learned reliance the training target does not support — a shortcut-flavored finding with a different, weaker sentence. The amended design orders the stages so this ambiguity never arises (census first; toggles only on pass), but the asymmetry matters for scoring: K2 gates the *interpretation* and the *negative*, not the existence of the rung-1 positive. That is why the amendment conditions the wording and the negative's classification on G-label rather than making the whole candidate's meaning contingent on it.

**Identity check:** the one-sentence question — is the model using the blood-volume reserve, read against CBF, to separate salvageable from lost tissue — is unchanged; the deliverable sentence is unchanged; the gate is a precondition inserted before the same experiment. The critic's own round states the repair "remains the original question and does not trigger a claim-identity change." Revision-in-place.

**Spin-off (noted, not debated):** if G-label *fails*, the census itself — "in a treated 2024 cohort, the CBV/CBF interaction the pre-2011 literature built core definitions on is absent from final-infarct outcomes" — could re-enter as a standalone model-free candidate.

**Status:** OPEN

## Round 2 — CRITIC

**Position:** The G-label amendment preserves the original question and resolves the keystone objection, but the proposed toggle still cannot distinguish use of an autoregulatory compensation construct from a generic monotone response to CBV/MTT.

**Argument:** I concede Round 1 because the proposer adopted the load-bearing K2, made it `NOT_INSPECTED`, capped feasibility at 3, and conditioned both the salvageability interpretation and decisive-negative claim on a prespecified patient-clustered outcome census; those are substantive arguments and gates, not restatement. The identity check also passes: G-label is a prerequisite for the same question, not a substitute endpoint. The strongest remaining defect is identifiability. In the stated compensated-to-collapsed edit, CBV falls and MTT is co-scaled downward while CBF and Tmax are fixed. Both the claimed construct reader (loss of reserve means greater infarct probability) and a generic monotone low-CBV severity reader predict the same signed increase. Reversing that edit adds no discrimination; it merely reverses both predictions. Because conventional deconvolution may make MTT algebraically dependent on CBV/CBF, the design also cannot attribute the effect to CBV rather than MTT, as the critique already notes. The card gestures toward “including above-mirror values,” but neither the amended Stage 0 plan nor `smallest_decisive_experiment` makes an above-mirror saturation arm confirmatory or gives it an empirical-support gate and a prespecified response-shape contrast. Without that arm, a positive result supports only “the model uses the joint CBV/MTT compensation-state channels at matched CBF,” not the deliverable’s stronger claim that it uses blood-volume reserve as a tissue-salvageability construct. This is not an identity-changing repair: explicitly testing saturation once rCBV reaches mirror-normal directly operationalizes the original reserve question. If that arm is infeasible or unsupported, the weaker channel-state sentence must become a separate successor because it changes the deliverable claim.

**What would change my mind:** Amend the confirmatory design to include an empirically supported above-mirror arm, gated in Stage 0, with a frozen dose-response contrast that distinguishes saturation at rCBV_mirror approximately 1 from a continuing monotone CBV/MTT response, plus the explicit prohibited conclusion that the experiment cannot separate CBV-channel use from MTT-channel use when the central-volume identity holds.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** With the G-label gate settled, the surviving defect is identifiability of the *construct*: the compensated-to-collapsed toggle (and its reverse) produces the same signed prediction from a reserve-construct reader and from a generic monotone low-CBV/short-MTT severity reader, so as designed the confirmatory arm cannot earn the word "reserve." The only discriminating test — saturation of the response above rCBV_mirror ≈ 1 — is currently a gesture in the alternatives list, not a gated confirmatory arm; and when the central-volume identity holds, CBV and MTT carry identical information at fixed CBF, so channel-level attribution is impossible in principle.

**Response:** AMEND

**Argument:** The sign analysis is correct and I will not relitigate it: below mirror level, both hypotheses predict the same direction, and reversing the edit reverses both predictions together. Critique §3 reached the identical conclusion independently. The two-sided toggle separates "uses the CBV/MTT state at matched CBF" from "ignores it," and separates a monotone-MTT reader (which predicts the opposite sign under the joint co-scaled edit — the one clean discrimination the basic arm does achieve, now stated in the card); it does not separate construct from monotone-CBV reader. The amendment adopts the critic's change-my-mind conditions in full, item by item:

1. **The above-mirror saturation arm becomes confirmatory.** Third toggle family, same within-case paired machinery: at matched CBF and Tmax, CBV is moved *above* mirror level (MTT co-scaled to stay on the manifold), in steps spanning the empirically observed above-mirror range in cohort deficit tissue. The frozen, prespecified readout is a **dose-response shape contrast**, not a threshold on any single delta: the construct hypothesis predicts the response flattens at rCBV_mirror ≈ 1 (below-mirror segment slope large, above-mirror segment slope compatible with the sham-derived noise floor); the monotone hypothesis predicts the above-mirror slope continues with the same sign as below. The contrast statistic (ratio of segment slopes with patient-clustered CIs, segments and step grid fixed in advance) is frozen in the probe contract before any model inference. A monotone continuation is itself reportable: "the model treats CBV as unbounded severity, not as a reserve with a ceiling" — a directional finding either way, which is what makes this arm confirmatory rather than exploratory.

2. **The arm gets its own Stage 0 empirical-support gate (G-hyper).** The same CPU census that runs G-label counts, per patient and per rCBF-decrement bin, deficit-tissue voxels with rCBV_mirror > 1 natively present in the cohort (post-ischemic hyperperfusion and luxury-perfusion states make this plausible, but plausibility is not support). Edit bounds are capped at the observed above-mirror quantiles; the discriminator/in-distribution gate applies to this arm separately, because it is the arm with the weakest physiological cover story and the greatest OOD risk. If G-hyper fails — insufficient native above-mirror support at matched CBF — the arm does not run.

3. **The prohibited conclusion is added to the card verbatim.** No claim that the model reads the CBV channel as opposed to the MTT channel: when the released maps satisfy the central-volume identity, CBV and MTT at fixed CBF are one degree of freedom, and the Stage 0 identity-residual census determines whether that degeneracy holds by construction. The deliverable sentence already names a *state* ("capillary volume held at or above mirror-normal while flow falls"), and the card now says explicitly that this is a state claim, never a channel-attribution claim.

4. **Scores follow the design as written, not as promised.** `identifiability` drops 4 → 3 in the card now, with the `why` stating it returns to 4 only if G-hyper passes and the saturation arm runs as confirmatory. This mirrors the feasibility 4 → 3 cap from round 1: the score reflects what has been gated, not what is hoped.

**What was lost.** More than round 1's amendment. (a) The strong claim — "uses the reserve as a construct" — is now hostage to the single most OOD-fragile arm of the design; the card acquires a second named death path (G-hyper) alongside G-label. (b) If G-hyper fails, the candidate cannot silently narrow to "uses the joint CBV/MTT compensation-state channels": the critic is right, and I accept, that this weaker sentence is a *different deliverable* under the claim-identity rule. In that world the candidate PAUSEs and the channel-state question registers as a successor with parent_id, re-entering through a normal cycle — no inherited queue position. That is the honest price: the original question now has two prespecified ways to die before its decisive arm runs, and one of them demotes rather than kills, into a successor I do not get to keep. (c) This is amendment two of two rounds. The standing rule says three amendments usually means the idea was wrong; I note the trajectory. My defense of stopping at two: both amendments installed gates *in front of* the original experiment demanded by two independent reviews (critique §§3–4 and both critic rounds converge on the same repairs); neither changed the question, the deliverable sentence, or the toggle machinery itself. If the next objection requires changing what the sentence claims, the idea was wrong and I will say so.

**Identity check:** the one-sentence question — is the model using the blood-volume reserve, read against CBF, to separate salvageable from lost tissue — is unchanged. The saturation arm does not replace that question; it is the part of the design that finally *operationalizes* the word "reserve" (a reserve is exactly the thing whose marginal value vanishes once replenished — flattening above mirror level is what "reserve" means in prediction space). The critic's own round states this repair is not identity-changing. Revision-in-place.

**Status:** OPEN

## Round 3 — CRITIC

**Position:** The saturation amendment preserves the original question but assumes, rather than establishes, that autoregulatory blood-volume reserve must produce a prediction kink at `rCBV_mirror = 1`, so its confirmatory contrast still does not identify the claimed construct.

**Argument:** Round 2's amendment adequately accepts the channel-degeneracy limit, makes the above-mirror arm confirmatory, and correctly pauses rather than silently changing the deliverable if G-hyper fails; those are substantive repairs, and the identity check passes. The remaining problem is the discriminator's physiological premise. Mirror-normal CBV is a reference value, not a demonstrated ceiling on autoregulatory vasodilation or on the prognostic value of blood volume. The card's own Wintermark framing permits normal-to-*increased* CBV in penumbra, and G-hyper explicitly expects native deficit tissue above 1. A genuine reserve reader could therefore continue changing its output above `rCBV_mirror = 1` because progressively elevated CBV may encode greater vasodilation, collateral filling, delay, or reperfusion state; conversely, a generic nonlinear CBV/MTT reader could flatten near 1 because of training-density saturation or network calibration. Thus the proposed slope ratio has no unique mapping: continuation does not refute construct use, and flattening does not establish it. G-label only tests compensated-versus-collapsed outcome association after dichotomizing at the same assumed boundary, while G-hyper only establishes support, so neither validates the kink prediction. This matters at rung 3: the design can identify use of a nonlinear joint CBV/MTT state at matched CBF, but it cannot call that nonlinearity “autoregulatory reserve” without an independently justified physiological response shape. The amendment therefore operationalizes the original words but not yet the original mechanism.

**What would change my mind:** Show primary-source or independent cohort evidence that, at matched CBF deficit and relevant reperfusion status, tissue outcome or a separately measured autoregulatory endpoint has a prespecified plateau or change point at (or estimably near) mirror-normal CBV; then freeze that externally derived shape before probing the model. Alternatively, measure an independent autoregulatory quantity available in the cases and show that the proposed CBV/MTT dose-response discriminates it from flexible monotone and saturating channel-only baselines. Without one of those facts, the weaker joint-state claim must be a successor candidate.

**Status:** OPEN

