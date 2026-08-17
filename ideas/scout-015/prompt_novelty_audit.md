You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-015
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

97 tracked ideas. Latest state per idea; full history in ledger.jsonl.

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **DATA_ACCESS** x2: Required data, checkpoints, or mappings are not obtainable in practice.
- **IDENTIFIABILITY_FAILURE** x2: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.
- **ANNOTATION_PROVENANCE** x1: Inference depends on who assigned labels / what they could see, and that is undocumented or contaminated.
- **CIRCULARITY** x1: The endpoint is a re-encoding of the input or of the thing being tested.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **scout-013-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.4, audited 2026-08-15] -- Collateral failure written in the cortical veins
- **scout-012-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.2, audited 2026-08-15] -- The dilated esophagus inside the fibrosis score
- **isles24-scout-001-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.1, audited 2026-08-16] -- A spreading front inside the perfusion deficit
- **scout-013-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.1, audited 2026-08-15] -- The vessel map inside the mosaic-attenuation score
- **isles24-scout-002-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.0, audited 2026-08-16] -- The healthy hemisphere is the ruler
- **isles24-scout-001-c07** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.0, audited 2026-08-16] -- Does the model mistake the end of the scan for the end of the bolus?
- **isles24-scout-002-c07** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.9, audited 2026-08-16] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
- **scout-010-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.9, audited 2026-08-12] -- CXR-Age put back together from parts a radiologist can measure
- **isles24-scout-001-c06** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.9, audited 2026-08-16] -- The capillary traffic jam hidden behind the same mean transit time
- **scout-014-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.8, audited 2026-08-16] -- Redraw the same airway walls with a sharper pencil: does the peribronchial-thickening score follow Pi10?
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


===== ideas/scout-015/README.md =====
# Scouting cycle 015

Tracks: baseline


===== ideas/scout-015/candidates_all.json =====
{
  "cycle": 15,
  "charter": null,
  "tracks": [
    "baseline"
  ],
  "notes": {
    "mode_c_score_missing": 2
  },
  "candidates": [
    {
      "id": "scout-015-c01",
      "search_mode": "A",
      "entry_point": 2,
      "title": "Measure the fluid behind the pleural-effusion score",
      "question": "Does CT-CLIP's pleural-effusion score use automatically measured pleural-fluid volume rather than merely the presence of fluid?",
      "deliverable_sentence": "The pleural-effusion score is using pleural-fluid volume.",
      "rung": "Targets rung 1; longitudinal within-patient dose-response establishes use of the measured quantity. Rung 2 needs replication across vendors and protocols; X is already a named rung-3 radiologic quantity.",
      "rung_reached": "Rung 1 if within-patient score change follows independently measured volume change and the negative controls pass; rung 2 requires cross-vendor replication.",
      "unfinished_story": "Idea 004 established that this released checkpoint's pleural-effusion score shifts with reconstruction, but did not name the mediating image quantity. The unfinished step is to measure fluid itself on serial scans and ask whether score movement follows volume rather than acquisition change.",
      "X_measurement": "Pleural-fluid volume in millilitres from an automated pleural-effusion segmentation, or a reproducible HU-and-location rule inside the pleural cavity; TotalSegmentator is public (Wasserthal et al., Radiol Artif Intell 2023, DOI 10.1148/ryai.230024, PMID 37795137), but availability and licensing of its pleural-effusion task must be inspected. Compute-today test: YES only if the released task is confirmed; otherwise the card fails rather than requesting annotations.",
      "suspected_signal": "More fluid occupies more dependent pleural space, replaces aerated lung with water-density voxels, and creates a longer meniscus; these are monotonic physical consequences of volume.",
      "use_vs_association": "Within one patient, model-score change must scale with machine-measured fluid-volume change after excluding reconstruction/protocol changes; a stable patient trait or label correlation cannot create that paired dose-response.",
      "keystone_prerequisite": "CT-RATE contains enough serial same-patient scans with changing pleural-fluid volume and sufficiently matched acquisition to separate biological change from protocol change.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearest verified fact is that CT-RATE has multiple scans per some patients and a working score pipeline. Still assumed, and load-bearing, is joint support: enough effusion-changing serial pairs that are not simultaneously different protocols, sites, or clinical episodes in ways that dominate the score.",
      "dies_like_prior": "Closest is idea-016 (IDENTIFIABILITY_FAILURE from hemodynamics co-varying with protocol). Different in principle because the exposure is a directly segmented volume and the design is within-patient, but it still dies the same way if matched serial support is absent. Annotation provenance does not apply: primary readout uses scores and machine volumes, not report labels.",
      "closest_prior_work": "CT-CLIP/CT-RATE (Hamamci et al., arXiv:2403.17834) supplied the model/data; idea 004 supplied verified checkpoint behavior and local inference. TotalSegmentator (DOI 10.1148/ryai.230024) supplied automated anatomy. None of those sources tested longitudinal score-volume coupling; novelty remains unverified pending a focused audit.",
      "existing_assets": "Frozen CT-CLIP checkpoint and pipeline; CT-RATE metadata; idea-004 per-volume outputs for 850 reconstruction volumes; public segmentation tooling.",
      "smallest_decisive_experiment": "Metadata-only Stage 0 finds serial pairs, then segment 30 pairs spanning effusion decrease and increase. Freeze inclusion before scoring. Regress within-patient score delta on within-patient fluid-volume delta, with unchanged-volume serial pairs and unrelated heads as controls.",
      "standing_confounds_addressed": "Patient, habitus, chronic prevalence, and referral background are fixed within pair. Label leakage is absent because labels are unused. Scanner/vendor/site/protocol/reconstruction and positioning must be matched or adjusted and are not automatically ruled out. Intercurrent disease remains a temporal confound.",
      "alternative_explanations": [
        "Changing atelectasis rather than fluid volume; measure aerated-lung loss and include it jointly.",
        "Protocol or reconstruction change between visits; exclude unmatched pairs and stratify the remainder.",
        "The score reads meniscus extent, not volume; this is a related visible mediator and would narrow, not support, the exact volume claim."
      ],
      "anticipated_negative": "Sensitivity-limited: a null is decisive only if the retained pairs span a preregistered volume-change range and segmentation repeatability is small relative to it.",
      "remaining_legwork": "One day for metadata support counts, two days to inspect/install the segmentation task, then roughly one week for a 30-pair first decision.",
      "design_template": "longitudinal-within-subject",
      "data": {
        "primary": "CT-RATE serial validation scans",
        "model": "released v2 ClassFine checkpoint"
      },
      "scores": {
        "clarity": {
          "value": 5,
          "why": "One named quantity and one paired dose-response."
        },
        "identifiability": {
          "value": 4,
          "why": "Within-patient change removes stable alternatives, but simultaneous atelectasis and visit-level protocol changes survive."
        },
        "medical_relevance": {
          "value": 3,
          "why": "It would convert an opaque score into a quantitative burden measure, though no outcome benefit is claimed."
        },
        "interest": {
          "value": 3,
          "why": "Not exotic, but it completes a verified reconstruction-sensitivity story with a physician-legible X."
        },
        "prior_legwork": {
          "value": 5,
          "why": "Checkpoint, preprocessing, output names, and deterministic inference are already verified locally."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped because serial joint support is uninspected."
        },
        "data_readiness": {
          "value": 4,
          "why": "The dataset and pipeline are available; serial subset size is unknown."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "Paired change, segmentation repeatability, and negative-control heads are straightforward."
        },
        "negative_result_value": {
          "value": 3,
          "why": "A null is useful only after a volume-range and reliability gate."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped and no exhaustive novelty audit has run."
        },
        "regret": {
          "value": 4,
          "why": "It cheaply names a quantity behind an already ratified model behavior."
        }
      },
      "unverified_claims": [
        "CT-RATE serial matched-pair count",
        "Released pleural-effusion segmentation task availability",
        "Absence of prior CT-CLIP score-volume study"
      ],
      "track": "baseline",
      "charter": null
    },
    {
      "id": "scout-015-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The missing branches inside Sybil's risk score",
      "question": "Is Sybil using the number of visible airway branches as a smoking-injury signal for future lung cancer?",
      "deliverable_sentence": "Sybil is using airway branch loss.",
      "rung": "Targets rung 1 with a localized representation-erasure test; rung 2 requires showing the effect across reconstruction kernels and sites; rung 3 requires validating automated branch count as the clinical small-airway-loss phenotype rather than merely segmentation visibility.",
      "rung_reached": "Rung 1 only; promotion requires external-cohort and reconstruction robustness plus physiological validation against airway disease measures.",
      "X_measurement": "Visible airway branch count and total airway-tree length from an automated airway centerline graph, normalized by lung volume; the graph quantities are exactly defined after segmentation. Compute-today test: YES in principle with open airway segmentation, but the specific tool/checkpoint and Sybil preprocessing compatibility are uninspected.",
      "suspected_signal": "Smoking-related airway remodeling and loss of visible distal branches reduce the resolved airway tree. Sybil sees the whole LDCT and uses no clinical variables (Mikhael et al., J Clin Oncol 2023, DOI 10.1200/JCO.22.01345, PMID 36634294), so airway injury is a plausible image-written smoking-dose proxy.",
      "use_vs_association": "Train a probe for branch count, remove only its linear subspace from frozen Sybil features, and compare risk-score change with matched random-subspace and emphysema-subspace removals; selective loss establishes encoded use more strongly than branch-count correlation alone.",
      "keystone_prerequisite": "A branch-count direction can be decoded from frozen Sybil features while remaining separable from emphysema extent, lung volume, reconstruction, and sex on joint support.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The easy fact verified from the primary Sybil paper is whole-volume image-only prediction and public model availability. Still assumed is the real keystone: branch count is encoded independently enough that erasing its probe direction does not simply erase a broad smoking/emphysema manifold.",
      "dies_like_prior": "Most resembles idea-009, killed because vascular geometry could not be separated from age/emphysema/reconstruction. This candidate differs only by making separability an explicit Stage-0 gate and by using matched nuisance-subspace erasures; if that gate fails, it should receive the same IDENTIFIABILITY_FAILURE code. No annotation-provenance dependence exists.",
      "closest_prior_work": "Sybil (DOI 10.1200/JCO.22.01345) establishes image-only future-risk prediction and public assets, but does not identify airway branch loss. Airway-count work must be pinned in novelty audit; no novelty claim is made here.",
      "existing_assets": "Public Sybil model/annotations per the primary paper; NLST image access precedent; automated lung masks; graph metrics require no human labels.",
      "smallest_decisive_experiment": "On a frozen cancer-free NLST subset, compute branch count, emphysema percentage, lung volume, and acquisition variables; cross-fit probes on Sybil features. Proceed only if conditional decoding passes. Erase the branch-count subspace and compare per-case risk shifts with equal-rank random and nuisance erasures on untouched test cases.",
      "standing_confounds_addressed": "Site/referral/prevalence are controlled by frozen NLST testing but not generalized away. Scanner/vendor/protocol/reconstruction, sex, habitus, and lung volume enter the separability gate. Label leakage is absent from the primary readout. Smoking exposure remains an unmeasured common cause, but localized erasure targets model use rather than etiologic causality.",
      "alternative_explanations": [
        "The erased subspace is a generic emphysema/smoking direction; matched emphysema erasure and conditional decoding test this but may not eliminate it.",
        "Branch count reflects reconstruction visibility; kernel-stratified decoding and external replication address this.",
        "Score loss follows generic representation damage; equal-rank random erasures and preserved unrelated probes address it."
      ],
      "anticipated_negative": "Decisive if the branch-count probe is reliable and selective but its erasure has no excess effect; otherwise sensitivity-limited.",
      "remaining_legwork": "One week for tool and feature extraction feasibility; NLST access is the rate limiter; two to three weeks after data availability.",
      "design_template": "representation-erasure",
      "entry_point_2_requirements": "Detection measurement is normalized airway branch count; the named artifact is reconstruction-dependent distal-airway visibility.",
      "data": {
        "primary": "NLST held-out scans",
        "model": "Sybil"
      },
      "scores": {
        "clarity": {
          "value": 4,
          "why": "X is precise, although representation erasure needs careful operational detail."
        },
        "identifiability": {
          "value": 3,
          "why": "Controls target generic damage and emphysema, but correlated smoking manifolds may remain inseparable."
        },
        "medical_relevance": {
          "value": 4,
          "why": "It would identify chronic airway injury as a component of future cancer risk scoring."
        },
        "interest": {
          "value": 4,
          "why": "A risk model counting missing branches is a legible and surprising mechanism."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Model and cohort exist; the airway pipeline and feature interface are not verified."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped by an uninspected separability keystone and gated data."
        },
        "data_readiness": {
          "value": 2,
          "why": "NLST access is not confirmed for this cycle."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Cross-fit erasure controls exist, but selectivity margins must be custom."
        },
        "negative_result_value": {
          "value": 4,
          "why": "A valid selective-erasure null decisively rejects this encoded direction."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped; airway-risk interpretability literature is unaudited."
        },
        "regret": {
          "value": 4,
          "why": "It tests a common biological story with a direct model-use design."
        }
      },
      "unverified_claims": [
        "Current Sybil feature-hook compatibility",
        "Open airway tool performance on NLST LDCT",
        "Conditional separability from emphysema",
        "Novelty"
      ],
      "track": "baseline",
      "charter": null
    },
    {
      "id": "scout-015-c03",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The portal vein as the cirrhosis model's pressure gauge",
      "question": "Is Merlin's cirrhosis output using portal-vein calibre as a gauge of portal hypertension?",
      "deliverable_sentence": "Merlin's cirrhosis output is using portal-vein calibre.",
      "rung": "Targets rung 1 through a localized vessel edit; rung 2 requires contrast-phase and site robustness; rung 3 requires only the named anatomic quantity, not a claim that calibre accurately measures pressure.",
      "rung_reached": "Rung 1 if a validated edit yields a monotonic score response; moves to rung 2 with real paired phase controls and external data.",
      "X_measurement": "Maximum extrahepatic portal-vein diameter in millimetres perpendicular to its centerline, using an automated portal-vein mask and DICOM spacing. TotalSegmentator is public and segments major vessels (DOI 10.1148/ryai.230024); exact portal-vein class/tool performance must be inspected. Compute-today test: YES conditional on that class being present and licensed.",
      "suspected_signal": "Portal hypertension can dilate the portal venous system; calibre is a visible geometric cue adjacent to liver, spleen, and collaterals. The card claims model use of calibre, not that diameter alone diagnoses portal hypertension.",
      "use_vs_association": "Create paired, anatomy-preserving portal-vein dilations and contractions with a diffeomorphic local warp, then require a monotonic cirrhosis-score response exceeding sham warps; this changes X while holding population and label fixed.",
      "keystone_prerequisite": "A portal-vein-only geometric edit can change measured calibre while preserving local texture, contrast, adjacent ducts/arteries, and in-distribution appearance sufficiently for causal interpretation.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Verifying that Merlin and a portal-vein segmenter exist would only check adjacent facts. The real assumption is edit validity: a discriminator, radiomics equivalence, and sham neutrality can establish that the score responds to calibre rather than warp artifacts.",
      "dies_like_prior": "Closest is idea-006: an OOD intervention could masquerade as use. This differs by making edit validity the keystone and using small tissue-preserving diffeomorphic edits plus shams, but it dies like 006 if those gates fail. Annotation provenance is irrelevant to the paired primary endpoint.",
      "closest_prior_work": "Merlin (Blankemeier et al., arXiv:2406.06512) reports 3D abdominal CT representation learning and hundreds of phenotype tasks; TotalSegmentator provides automated anatomy. Neither source, as currently inspected, establishes portal-calibre use. Exact cirrhosis-output/checkpoint support and novelty are unverified.",
      "existing_assets": "Released Merlin code/checkpoints reported by its primary preprint; public abdominal CT candidates; TotalSegmentator; standard diffeomorphic registration software.",
      "smallest_decisive_experiment": "Stage 0 first confirms the output and portal mask on 20 scans. Generate three blinded edit levels and matched shams in 50 held-out scans; verify calibre change, local intensity preservation, and edit indistinguishability before opening Merlin score deltas. Test monotonic within-scan response.",
      "standing_confounds_addressed": "Within-scan edits fix scanner, vendor, protocol, site, positioning, habitus, prevalence, referral, and labels. Contrast phase remains encoded in the fixed image and may modify the effect, so stratify it. Label leakage cannot explain paired score changes. Edit artifacts are the dominant confound.",
      "alternative_explanations": [
        "Warp-boundary artifacts drive the score; sham warps and blinded edit detection address this.",
        "The edit changes adjacent bile duct or hepatic hilum geometry; mask-overlap audits exclude such cases.",
        "The model responds to vessel conspicuity rather than calibre; preserve HU and edge profile and report this residual honestly."
      ],
      "anticipated_negative": "Decisive only after the edit passes sensitivity and in-distribution gates; otherwise uninterpretable.",
      "remaining_legwork": "Two days to verify output and segmentation classes; one to two weeks to validate an editor; first scientific result in about three weeks if all gates pass.",
      "design_template": "regional-substitution",
      "entry_point_2_requirements": "Measurement is centerline-orthogonal portal diameter; the named artifact is contrast-phase-dependent vessel conspicuity and warp signature.",
      "data": {
        "primary": "Public abdominal CT compatible with Merlin",
        "model": "Merlin"
      },
      "scores": {
        "clarity": {
          "value": 4,
          "why": "Named vessel, measurement, and intervention; output support remains to verify."
        },
        "identifiability": {
          "value": 4,
          "why": "Paired localized edits remove population confounds, conditional on a stringent edit-validity gate."
        },
        "medical_relevance": {
          "value": 3,
          "why": "It names a classic portal-hypertension-associated cue but does not establish pressure measurement."
        },
        "interest": {
          "value": 4,
          "why": "A foundation model using a vein as a manometer is concrete and clinically debatable."
        },
        "prior_legwork": {
          "value": 3,
          "why": "General models and segmenters exist; the critical editor does not."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped; edit validity is uninspected."
        },
        "data_readiness": {
          "value": 3,
          "why": "Public CT exists, but exact model-compatible cohort is not frozen."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Monotonic paired response is simple; edit-validity metrics are custom."
        },
        "negative_result_value": {
          "value": 3,
          "why": "Potentially decisive after gates, otherwise sensitivity-limited."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped and unaudited."
        },
        "regret": {
          "value": 3,
          "why": "Worth testing if the editor is easy; otherwise not an obvious missed opportunity."
        }
      },
      "unverified_claims": [
        "Merlin exposes a usable cirrhosis output",
        "Portal-vein segmentation class and accuracy",
        "Compatible public cohort",
        "Edit validity",
        "Novelty"
      ],
      "track": "baseline",
      "charter": null
    },
    {
      "id": "scout-015-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The continuous air tunnel inside the hiatal-hernia score",
      "question": "Is CT-CLIP's hiatal-hernia score using continuity of the esophageal air column across the diaphragm?",
      "deliverable_sentence": "The hiatal-hernia score is using a continuous air column through the esophageal hiatus.",
      "rung": "Mode C target is rung 1; rung 2 needs reconstruction and gastric-distension controls; rung 3 requires showing that the topology corresponds to herniated stomach rather than ordinary swallowed air.",
      "rung_reached": "Rung 1 at best from controlled synthesis; clinical naming beyond an air-column topology needs independent stomach/hiatus geometry validation.",
      "X_measurement": "Binary connectivity: after segmenting the esophagus/hiatus corridor, threshold gas below -800 HU and ask whether one 3D connected component intersects both a supradiaphragmatic esophageal zone and the infradiaphragmatic gastric zone; also record bottleneck area. Compute-today test: YES as a well-defined image measurement if the corridor can be generated automatically from surrounding organ masks.",
      "suspected_signal": "A sliding hiatal hernia can move gas-containing gastric lumen above the diaphragm, turning two separated gas pockets into a continuous topological path. A 3D model may exploit connectivity more readily than a human reader explicitly names it.",
      "use_vs_association": "Counterfactual synthesis opens or closes only a narrow gas bridge while holding hernia anatomy and all labels fixed; a score response beyond sham bridges tests use of connectivity, not population association.",
      "keystone_prerequisite": "Physically plausible bridge-opening and bridge-closing counterfactuals can be generated without creating an obvious synthetic seam or changing stomach/diaphragm geometry.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The verified adjacent fact is only that the frozen checkpoint has a hiatal-hernia head. The real assumption is that topology can be edited independently of lumen shape and gas volume; this may be physically impossible, which would kill the causal claim.",
      "dies_like_prior": "Dies like idea-006 if the bridge images are OOD. It differs by using minimal local air-for-air/tissue-for-tissue edits and explicit seam/sham gates, but no rhetorical distinction rescues it if those gates fail. No annotation-provenance issue enters the paired endpoint.",
      "closest_prior_work": "CT-RATE/CT-CLIP (arXiv:2403.17834) supplies the head; no primary study linking its output to gas-column connectivity has been verified. This is explicitly speculative, not a novelty claim.",
      "existing_assets": "Frozen CT-CLIP inference stack; public CT-RATE validation data; automated diaphragm, stomach, and esophagus landmarks may be derivable from public segmenters but are unverified.",
      "smallest_decisive_experiment": "On 20 automatically selected gas-containing cases, create connectivity-open, connectivity-closed, equal-volume displaced-gas, and sham edits. Blind an edit discriminator. Only if indistinguishable, compare within-case hiatal-hernia score changes and unrelated-head controls.",
      "standing_confounds_addressed": "Paired edits fix scanner/vendor/protocol/reconstruction/site/position/habitus/prevalence/referral and report labels. Gastric distension and total gas volume are controlled by equal-volume displacement. Synthetic seam and anatomical implausibility remain the critical threats.",
      "alternative_explanations": [
        "The model detects an edit seam; discriminator and sham tests address it.",
        "It responds to total supradiaphragmatic gas volume rather than connectivity; equal-volume disconnected controls exclude this.",
        "It reads stomach displacement, which cannot truly be held fixed when changing topology; not fully excluded and limits the claim."
      ],
      "anticipated_negative": "Decisive if counterfactual sensitivity and sham neutrality are demonstrated; otherwise uninterpretable.",
      "cross_domain": {
        "borrowed_construct": "Percolation/topological connectivity",
        "implied_measurement": "Whether a gas component spans the diaphragm and its bottleneck area",
        "what_changes_if_dropped": "Without the analogy, the binary connected-component measurement and open/close intervention remain identical; therefore percolation language is decorative and should not appear in the deliverable claim."
      },
      "remaining_legwork": "Two weeks for segmentation and editor feasibility; a further week for the 20-case readout if the gate passes.",
      "design_template": "counterfactual-synthesis",
      "entry_point_2_requirements": "Measurement is transdiaphragmatic gas connectivity; the named artifact is swallowed-air/gastric-distension variation and synthetic seams.",
      "data": {
        "primary": "CT-RATE validation split",
        "model": "released v2 ClassFine checkpoint"
      },
      "scores": {
        "clarity": {
          "value": 5,
          "why": "A binary physical quantity with a direct open/close intervention."
        },
        "identifiability": {
          "value": 4,
          "why": "Equal-volume controls isolate topology, conditional on edit realism; coupled anatomy prevents a perfect 5."
        },
        "medical_relevance": {
          "value": 3,
          "why": "Explains a common finding head, though the cue could be brittle rather than beneficial."
        },
        "interest": {
          "value": 5,
          "why": "A 3D model reading connectivity rather than size is surprising and broadly interpretable."
        },
        "mechanism_clarity": {
          "value": 5,
          "why": "Specific gas connectivity, exact thresholded measurement, and causal toggle are named."
        },
        "prior_legwork": {
          "value": 2,
          "why": "Model side is ready; measurement/editor side is speculative."
        },
        "feasibility": {
          "value": 2,
          "why": "Uninspected and likely difficult, reported outside Mode C priority."
        },
        "data_readiness": {
          "value": 4,
          "why": "Data and checkpoint are local/public."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Paired score changes are easy; realism validation is custom."
        },
        "negative_result_value": {
          "value": 3,
          "why": "A valid editor yields a decisive scoped null; gate failure yields no scientific negative."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped; no audit completed."
        },
        "regret": {
          "value": 4,
          "why": "If feasible, it is an unusually clean test of a genuinely 3D cue."
        }
      },
      "unverified_claims": [
        "Automated esophagus/hiatus corridor viability",
        "Frequency of suitable gas-containing cases",
        "Counterfactual realism",
        "Novelty"
      ],
      "track": "baseline",
      "charter": null
    },
    {
      "id": "scout-015-c05",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The lung-opacity score may be reading gravity",
      "question": "Is a chest-CT lung-opacity score using the ventrodorsal lung-density gradient as a hydrostatic signature?",
      "deliverable_sentence": "The lung-opacity score is using the gravitational lung-density gradient.",
      "rung": "Mode C target is rung 1. Rung 2 requires real position-change or matched inspiratory controls; rung 3 is already a named physical/radiologic quantity once gravity direction is known.",
      "rung_reached": "Rung 1 only from a physics-preserving perturbation; a real prone/supine replication would move it toward rung 2.",
      "X_measurement": "Within each lung mask, regress HU on signed distance along the DICOM gravity axis, reporting HU per centimetre separately by lung and excluding vessels/airways; this is fully formulaic and computable on any scan today with an automated lung mask. Compute-today test: YES.",
      "suspected_signal": "Gravity creates a dependent increase in pulmonary blood/tissue fraction and reduced aeration. Edema, dependent atelectasis, and ordinary supine physiology can therefore write a smooth ventrodorsal HU gradient into CT that a lung-opacity classifier may use.",
      "use_vs_association": "Apply a smooth, lung-confined, zero-mean HU field that steepens or flattens the measured gradient without changing total lung density; monotonic score response relative to shuffled-axis and equal-energy texture controls identifies use of the gradient.",
      "keystone_prerequisite": "A smooth gradient perturbation can remain inside the model's training distribution while leaving total lung attenuation, visible lesions, and nonlung anatomy unchanged.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "It is easy to verify that gradients exist in supine lungs; that is not the keystone. The load-bearing assumption is intervention validity: a synthetic HU ramp is perceived as physiology rather than preprocessing or beam-hardening artifact.",
      "dies_like_prior": "Closest is idea-006: extreme image deletion was OOD. This uses a small zero-mean physical field and matched energy controls, but still dies the same way if edit detectability is high. It also learns from idea-007 by naming inspiration/coverage as controls. Labels are unused, so annotation provenance does not apply.",
      "closest_prior_work": "Primary CT physiology literature documents dependent density gradients, but exact identifiers have not yet been inspected; CT-CLIP/CT-RATE (arXiv:2403.17834) provides a lung-opacity output. No model-decoding precedent is asserted.",
      "existing_assets": "Public chest CT, lung segmentation, DICOM orientation, and an already verified CT-CLIP pipeline; the mathematical perturbation needs no learned generator.",
      "smallest_decisive_experiment": "Measure native gradients in 100 scans. On 30 mid-gradient cases, apply preregistered flatten/steepen ramps, reversed-axis ramps, and spatially shuffled equal-energy fields. Require discriminator equivalence and unchanged global HU histogram, then test monotonic lung-opacity score response.",
      "standing_confounds_addressed": "Within-scan perturbation fixes scanner/vendor/protocol/reconstruction/site/position/habitus/prevalence/referral and label leakage. Native inspiration and patient positioning are fixed. Beam hardening and edit signature remain; reversed-axis/equal-energy controls address but may not eliminate them.",
      "alternative_explanations": [
        "The model responds to any low-frequency HU ramp; reversed left-right and craniocaudal ramps test orientation specificity.",
        "The ramp changes lesion conspicuity; exclude lesion masks or stratify by opacity-free regions.",
        "Preprocessing normalization converts the edit into a global intensity cue; verify the final tensor and preserve its mean/histogram."
      ],
      "anticipated_negative": "Decisive only if the perturbation spans native physiological variation and passes realism/sensitivity controls; otherwise sensitivity-limited.",
      "cross_domain": {
        "borrowed_construct": "Hydrostatics in a deformable porous medium",
        "implied_measurement": "HU change per centimetre along gravity at fixed total lung attenuation",
        "what_changes_if_dropped": "The analogy determines the perturbation: preserve total mass while redistributing density along gravity. Dropping it would permit arbitrary brightness ramps and would change both controls and interpretation."
      },
      "remaining_legwork": "Several days to quantify the native range and inspect final-tensor effects; one week for the controlled 30-case probe, contingent on a fresh contract.",
      "design_template": "model-output-perturbation",
      "entry_point_2_requirements": "Measurement is HU/cm along gravity; the named artifact is beam hardening or a generic low-frequency intensity ramp.",
      "data": {
        "primary": "Public chest CT; not required to be CT-RATE",
        "model": "a frozen chest-CT lung-opacity classifier, CT-CLIP preferred"
      },
      "scores": {
        "clarity": {
          "value": 5,
          "why": "The physical quantity, axis, unit, and perturbation are explicit."
        },
        "identifiability": {
          "value": 4,
          "why": "Axis and equal-energy controls distinguish hydrostatic orientation from generic ramps; realism remains uncertain."
        },
        "medical_relevance": {
          "value": 3,
          "why": "It could explain false opacity calls in dependent lung and positioning sensitivity."
        },
        "interest": {
          "value": 5,
          "why": "The claim that a model reads gravity from lung density is surprising but physically grounded."
        },
        "mechanism_clarity": {
          "value": 5,
          "why": "A specific HU/cm quantity and mass-preserving intervention are named."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Pipeline and masks exist; physiological range and editor validity are not established."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped; the perturbation is cheap but its in-distribution status is uninspected."
        },
        "data_readiness": {
          "value": 4,
          "why": "Many public chest CTs suffice and labels are unnecessary."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "Paired monotonic response and matched controls are prespecifiable."
        },
        "negative_result_value": {
          "value": 4,
          "why": "With a validated native-range perturbation, a null directly weakens the hypothesis."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped; primary novelty search remains undone."
        },
        "regret": {
          "value": 4,
          "why": "It is cheap, label-free, and tests a cue that could matter across many thoracic heads."
        }
      },
      "unverified_claims": [
        "Primary quantitative range for normal dependent HU gradients",
        "Edit in-distribution status",
        "Availability of prone/supine replication data",
        "Novelty"
      ],
      "track": "baseline",
      "charter": null
    }
  ]
}


===== ideas/scout-015/run_provenance.json =====
{
  "timestamp": "2026-08-17T06:33:19+00:00",
  "git_commit": "ac3905a776ec2301f30a2cd6647ec64d8b73d5df",
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
    "fiction_refine.md": "f2e140a70980fa95",
    "fiction_scout.md": "63b11687055c8624",
    "interpret.md": "7ce78a736a0ae412",
    "interpret_review.md": "c02c16dabab5446d",
    "keystone_screen.md": "f6f206ca8577b47b",
    "librarian.md": "e6977370921ff990",
    "novelty_audit.md": "3139addc91205b1e",
    "probe_code.md": "bc0c52c94d1af371",
    "probe_plan.md": "6249699cb2278e0e",
    "probe_review.md": "6b222a3f766009ea",
    "revise.md": "db7fab4a10c7c32b",
    "scout.md": "c5ae0f349d7a6d67",
    "wide_scout.md": "6f59a27366e2f4a1"
  },
  "agents_toml_hash": "4b0d0da9640a634d"
}


===== ideas/scout-015/scout_candidates.json =====
{
  "cycle": "scout-015",
  "date": "2026-08-17",
  "track": "baseline",
  "all_questions": [
    {"n": 1, "question": "Does CT-CLIP's pleural-effusion score use pleural-fluid volume rather than merely the presence of fluid?", "disposition": "DEVELOPED as scout-015-c01"},
    {"n": 2, "question": "Is Sybil using the number of visible airway branches as a smoking-injury signal for future lung cancer?", "disposition": "DEVELOPED as scout-015-c02"},
    {"n": 3, "question": "Is Merlin's cirrhosis representation using portal-vein calibre as a pressure gauge?", "disposition": "DEVELOPED as scout-015-c03"},
    {"n": 4, "question": "Is CT-CLIP's hiatal-hernia score using continuity of the esophageal air column across the diaphragm?", "disposition": "DEVELOPED as scout-015-c04"},
    {"n": 5, "question": "Is CT-CLIP's lung-opacity score using the gravitational ventrodorsal density gradient as a hydrostatic signature?", "disposition": "DEVELOPED as scout-015-c05"},
    {"n": 6, "question": "Is a chest-CT mortality model using splenic crenulation as a record of repeated respiratory traction?", "disposition": "DROPPED: the proposed boundary-frequency measure is computable, but no credible biological mechanism or use-identifying perturbation survived first principles."},
    {"n": 7, "question": "Does a mammography risk model use the graph centrality of Cooper ligaments?", "disposition": "DROPPED (cross-domain): the vessel-versus-ligament separation needed to compute X is not available without new annotations."},
    {"n": 8, "question": "Does an osteoporosis model use vertebral endplate concavity, the radiologic equivalent of a buckling mode?", "disposition": "DROPPED (radiologist-word quantity): overlaps scout-006-c04's vertebral-shape question and adds no new identification instrument."},
    {"n": 9, "question": "Does a pulmonary-embolism model use the iodine-density difference between the right and left heart as a contrast-transit clock?", "disposition": "DROPPED: overlaps rejected idea-016 and scout-007-c08; injection timing remains inseparable from hemodynamics in obtainable data."},
    {"n": 10, "question": "Does a lung-cancer model use the handedness of bronchial branching, like a chiral molecule?", "disposition": "DROPPED (obviously-wrong and cross-domain): chirality is computable from airway centerlines, but laterality, situs, and preprocessing orientation provide easier explanations and no plausible cancer mechanism."}
  ],
  "quota_note": "Filled exactly 1 Mode A, 2 Mode B, and 2 Mode C; all five are CT/radiology, zero dermatology, and only c01/c04 use CT-RATE. Zero revivals: no portfolio-brief unblock condition has a newly verified fact. The five developed cards deliberately use five different design grammars to counter the portfolio's regional-substitution/conditional-observational concentration.",
  "candidates": [
    {
      "id": "scout-015-c01",
      "search_mode": "A",
      "entry_point": 2,
      "title": "Measure the fluid behind the pleural-effusion score",
      "question": "Does CT-CLIP's pleural-effusion score use automatically measured pleural-fluid volume rather than merely the presence of fluid?",
      "deliverable_sentence": "The pleural-effusion score is using pleural-fluid volume.",
      "rung": "Targets rung 1; longitudinal within-patient dose-response establishes use of the measured quantity. Rung 2 needs replication across vendors and protocols; X is already a named rung-3 radiologic quantity.",
      "rung_reached": "Rung 1 if within-patient score change follows independently measured volume change and the negative controls pass; rung 2 requires cross-vendor replication.",
      "unfinished_story": "Idea 004 established that this released checkpoint's pleural-effusion score shifts with reconstruction, but did not name the mediating image quantity. The unfinished step is to measure fluid itself on serial scans and ask whether score movement follows volume rather than acquisition change.",
      "X_measurement": "Pleural-fluid volume in millilitres from an automated pleural-effusion segmentation, or a reproducible HU-and-location rule inside the pleural cavity; TotalSegmentator is public (Wasserthal et al., Radiol Artif Intell 2023, DOI 10.1148/ryai.230024, PMID 37795137), but availability and licensing of its pleural-effusion task must be inspected. Compute-today test: YES only if the released task is confirmed; otherwise the card fails rather than requesting annotations.",
      "suspected_signal": "More fluid occupies more dependent pleural space, replaces aerated lung with water-density voxels, and creates a longer meniscus; these are monotonic physical consequences of volume.",
      "use_vs_association": "Within one patient, model-score change must scale with machine-measured fluid-volume change after excluding reconstruction/protocol changes; a stable patient trait or label correlation cannot create that paired dose-response.",
      "keystone_prerequisite": "CT-RATE contains enough serial same-patient scans with changing pleural-fluid volume and sufficiently matched acquisition to separate biological change from protocol change.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearest verified fact is that CT-RATE has multiple scans per some patients and a working score pipeline. Still assumed, and load-bearing, is joint support: enough effusion-changing serial pairs that are not simultaneously different protocols, sites, or clinical episodes in ways that dominate the score.",
      "dies_like_prior": "Closest is idea-016 (IDENTIFIABILITY_FAILURE from hemodynamics co-varying with protocol). Different in principle because the exposure is a directly segmented volume and the design is within-patient, but it still dies the same way if matched serial support is absent. Annotation provenance does not apply: primary readout uses scores and machine volumes, not report labels.",
      "closest_prior_work": "CT-CLIP/CT-RATE (Hamamci et al., arXiv:2403.17834) supplied the model/data; idea 004 supplied verified checkpoint behavior and local inference. TotalSegmentator (DOI 10.1148/ryai.230024) supplied automated anatomy. None of those sources tested longitudinal score-volume coupling; novelty remains unverified pending a focused audit.",
      "existing_assets": "Frozen CT-CLIP checkpoint and pipeline; CT-RATE metadata; idea-004 per-volume outputs for 850 reconstruction volumes; public segmentation tooling.",
      "smallest_decisive_experiment": "Metadata-only Stage 0 finds serial pairs, then segment 30 pairs spanning effusion decrease and increase. Freeze inclusion before scoring. Regress within-patient score delta on within-patient fluid-volume delta, with unchanged-volume serial pairs and unrelated heads as controls.",
      "standing_confounds_addressed": "Patient, habitus, chronic prevalence, and referral background are fixed within pair. Label leakage is absent because labels are unused. Scanner/vendor/site/protocol/reconstruction and positioning must be matched or adjusted and are not automatically ruled out. Intercurrent disease remains a temporal confound.",
      "alternative_explanations": [
        "Changing atelectasis rather than fluid volume; measure aerated-lung loss and include it jointly.",
        "Protocol or reconstruction change between visits; exclude unmatched pairs and stratify the remainder.",
        "The score reads meniscus extent, not volume; this is a related visible mediator and would narrow, not support, the exact volume claim."
      ],
      "anticipated_negative": "Sensitivity-limited: a null is decisive only if the retained pairs span a preregistered volume-change range and segmentation repeatability is small relative to it.",
      "remaining_legwork": "One day for metadata support counts, two days to inspect/install the segmentation task, then roughly one week for a 30-pair first decision.",
      "design_template": "longitudinal-within-subject",
      "data": {"primary": "CT-RATE serial validation scans", "model": "released v2 ClassFine checkpoint"},
      "scores": {
        "clarity": {"value": 5, "why": "One named quantity and one paired dose-response."},
        "identifiability": {"value": 4, "why": "Within-patient change removes stable alternatives, but simultaneous atelectasis and visit-level protocol changes survive."},
        "medical_relevance": {"value": 3, "why": "It would convert an opaque score into a quantitative burden measure, though no outcome benefit is claimed."},
        "interest": {"value": 3, "why": "Not exotic, but it completes a verified reconstruction-sensitivity story with a physician-legible X."},
        "prior_legwork": {"value": 5, "why": "Checkpoint, preprocessing, output names, and deterministic inference are already verified locally."},
        "feasibility": {"value": 3, "why": "Capped because serial joint support is uninspected."},
        "data_readiness": {"value": 4, "why": "The dataset and pipeline are available; serial subset size is unknown."},
        "evaluation_readiness": {"value": 4, "why": "Paired change, segmentation repeatability, and negative-control heads are straightforward."},
        "negative_result_value": {"value": 3, "why": "A null is useful only after a volume-range and reliability gate."},
        "novelty_confidence": {"value": 3, "why": "Capped and no exhaustive novelty audit has run."},
        "regret": {"value": 4, "why": "It cheaply names a quantity behind an already ratified model behavior."}
      },
      "unverified_claims": ["CT-RATE serial matched-pair count", "Released pleural-effusion segmentation task availability", "Absence of prior CT-CLIP score-volume study"]
    },
    {
      "id": "scout-015-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The missing branches inside Sybil's risk score",
      "question": "Is Sybil using the number of visible airway branches as a smoking-injury signal for future lung cancer?",
      "deliverable_sentence": "Sybil is using airway branch loss.",
      "rung": "Targets rung 1 with a localized representation-erasure test; rung 2 requires showing the effect across reconstruction kernels and sites; rung 3 requires validating automated branch count as the clinical small-airway-loss phenotype rather than merely segmentation visibility.",
      "rung_reached": "Rung 1 only; promotion requires external-cohort and reconstruction robustness plus physiological validation against airway disease measures.",
      "X_measurement": "Visible airway branch count and total airway-tree length from an automated airway centerline graph, normalized by lung volume; the graph quantities are exactly defined after segmentation. Compute-today test: YES in principle with open airway segmentation, but the specific tool/checkpoint and Sybil preprocessing compatibility are uninspected.",
      "suspected_signal": "Smoking-related airway remodeling and loss of visible distal branches reduce the resolved airway tree. Sybil sees the whole LDCT and uses no clinical variables (Mikhael et al., J Clin Oncol 2023, DOI 10.1200/JCO.22.01345, PMID 36634294), so airway injury is a plausible image-written smoking-dose proxy.",
      "use_vs_association": "Train a probe for branch count, remove only its linear subspace from frozen Sybil features, and compare risk-score change with matched random-subspace and emphysema-subspace removals; selective loss establishes encoded use more strongly than branch-count correlation alone.",
      "keystone_prerequisite": "A branch-count direction can be decoded from frozen Sybil features while remaining separable from emphysema extent, lung volume, reconstruction, and sex on joint support.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The easy fact verified from the primary Sybil paper is whole-volume image-only prediction and public model availability. Still assumed is the real keystone: branch count is encoded independently enough that erasing its probe direction does not simply erase a broad smoking/emphysema manifold.",
      "dies_like_prior": "Most resembles idea-009, killed because vascular geometry could not be separated from age/emphysema/reconstruction. This candidate differs only by making separability an explicit Stage-0 gate and by using matched nuisance-subspace erasures; if that gate fails, it should receive the same IDENTIFIABILITY_FAILURE code. No annotation-provenance dependence exists.",
      "closest_prior_work": "Sybil (DOI 10.1200/JCO.22.01345) establishes image-only future-risk prediction and public assets, but does not identify airway branch loss. Airway-count work must be pinned in novelty audit; no novelty claim is made here.",
      "existing_assets": "Public Sybil model/annotations per the primary paper; NLST image access precedent; automated lung masks; graph metrics require no human labels.",
      "smallest_decisive_experiment": "On a frozen cancer-free NLST subset, compute branch count, emphysema percentage, lung volume, and acquisition variables; cross-fit probes on Sybil features. Proceed only if conditional decoding passes. Erase the branch-count subspace and compare per-case risk shifts with equal-rank random and nuisance erasures on untouched test cases.",
      "standing_confounds_addressed": "Site/referral/prevalence are controlled by frozen NLST testing but not generalized away. Scanner/vendor/protocol/reconstruction, sex, habitus, and lung volume enter the separability gate. Label leakage is absent from the primary readout. Smoking exposure remains an unmeasured common cause, but localized erasure targets model use rather than etiologic causality.",
      "alternative_explanations": [
        "The erased subspace is a generic emphysema/smoking direction; matched emphysema erasure and conditional decoding test this but may not eliminate it.",
        "Branch count reflects reconstruction visibility; kernel-stratified decoding and external replication address this.",
        "Score loss follows generic representation damage; equal-rank random erasures and preserved unrelated probes address it."
      ],
      "anticipated_negative": "Decisive if the branch-count probe is reliable and selective but its erasure has no excess effect; otherwise sensitivity-limited.",
      "remaining_legwork": "One week for tool and feature extraction feasibility; NLST access is the rate limiter; two to three weeks after data availability.",
      "design_template": "representation-erasure",
      "entry_point_2_requirements": "Detection measurement is normalized airway branch count; the named artifact is reconstruction-dependent distal-airway visibility.",
      "data": {"primary": "NLST held-out scans", "model": "Sybil"},
      "scores": {
        "clarity": {"value": 4, "why": "X is precise, although representation erasure needs careful operational detail."},
        "identifiability": {"value": 3, "why": "Controls target generic damage and emphysema, but correlated smoking manifolds may remain inseparable."},
        "medical_relevance": {"value": 4, "why": "It would identify chronic airway injury as a component of future cancer risk scoring."},
        "interest": {"value": 4, "why": "A risk model counting missing branches is a legible and surprising mechanism."},
        "prior_legwork": {"value": 3, "why": "Model and cohort exist; the airway pipeline and feature interface are not verified."},
        "feasibility": {"value": 3, "why": "Capped by an uninspected separability keystone and gated data."},
        "data_readiness": {"value": 2, "why": "NLST access is not confirmed for this cycle."},
        "evaluation_readiness": {"value": 3, "why": "Cross-fit erasure controls exist, but selectivity margins must be custom."},
        "negative_result_value": {"value": 4, "why": "A valid selective-erasure null decisively rejects this encoded direction."},
        "novelty_confidence": {"value": 3, "why": "Capped; airway-risk interpretability literature is unaudited."},
        "regret": {"value": 4, "why": "It tests a common biological story with a direct model-use design."}
      },
      "unverified_claims": ["Current Sybil feature-hook compatibility", "Open airway tool performance on NLST LDCT", "Conditional separability from emphysema", "Novelty"]
    },
    {
      "id": "scout-015-c03",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The portal vein as the cirrhosis model's pressure gauge",
      "question": "Is Merlin's cirrhosis output using portal-vein calibre as a gauge of portal hypertension?",
      "deliverable_sentence": "Merlin's cirrhosis output is using portal-vein calibre.",
      "rung": "Targets rung 1 through a localized vessel edit; rung 2 requires contrast-phase and site robustness; rung 3 requires only the named anatomic quantity, not a claim that calibre accurately measures pressure.",
      "rung_reached": "Rung 1 if a validated edit yields a monotonic score response; moves to rung 2 with real paired phase controls and external data.",
      "X_measurement": "Maximum extrahepatic portal-vein diameter in millimetres perpendicular to its centerline, using an automated portal-vein mask and DICOM spacing. TotalSegmentator is public and segments major vessels (DOI 10.1148/ryai.230024); exact portal-vein class/tool performance must be inspected. Compute-today test: YES conditional on that class being present and licensed.",
      "suspected_signal": "Portal hypertension can dilate the portal venous system; calibre is a visible geometric cue adjacent to liver, spleen, and collaterals. The card claims model use of calibre, not that diameter alone diagnoses portal hypertension.",
      "use_vs_association": "Create paired, anatomy-preserving portal-vein dilations and contractions with a diffeomorphic local warp, then require a monotonic cirrhosis-score response exceeding sham warps; this changes X while holding population and label fixed.",
      "keystone_prerequisite": "A portal-vein-only geometric edit can change measured calibre while preserving local texture, contrast, adjacent ducts/arteries, and in-distribution appearance sufficiently for causal interpretation.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Verifying that Merlin and a portal-vein segmenter exist would only check adjacent facts. The real assumption is edit validity: a discriminator, radiomics equivalence, and sham neutrality can establish that the score responds to calibre rather than warp artifacts.",
      "dies_like_prior": "Closest is idea-006: an OOD intervention could masquerade as use. This differs by making edit validity the keystone and using small tissue-preserving diffeomorphic edits plus shams, but it dies like 006 if those gates fail. Annotation provenance is irrelevant to the paired primary endpoint.",
      "closest_prior_work": "Merlin (Blankemeier et al., arXiv:2406.06512) reports 3D abdominal CT representation learning and hundreds of phenotype tasks; TotalSegmentator provides automated anatomy. Neither source, as currently inspected, establishes portal-calibre use. Exact cirrhosis-output/checkpoint support and novelty are unverified.",
      "existing_assets": "Released Merlin code/checkpoints reported by its primary preprint; public abdominal CT candidates; TotalSegmentator; standard diffeomorphic registration software.",
      "smallest_decisive_experiment": "Stage 0 first confirms the output and portal mask on 20 scans. Generate three blinded edit levels and matched shams in 50 held-out scans; verify calibre change, local intensity preservation, and edit indistinguishability before opening Merlin score deltas. Test monotonic within-scan response.",
      "standing_confounds_addressed": "Within-scan edits fix scanner, vendor, protocol, site, positioning, habitus, prevalence, referral, and labels. Contrast phase remains encoded in the fixed image and may modify the effect, so stratify it. Label leakage cannot explain paired score changes. Edit artifacts are the dominant confound.",
      "alternative_explanations": [
        "Warp-boundary artifacts drive the score; sham warps and blinded edit detection address this.",
        "The edit changes adjacent bile duct or hepatic hilum geometry; mask-overlap audits exclude such cases.",
        "The model responds to vessel conspicuity rather than calibre; preserve HU and edge profile and report this residual honestly."
      ],
      "anticipated_negative": "Decisive only after the edit passes sensitivity and in-distribution gates; otherwise uninterpretable.",
      "remaining_legwork": "Two days to verify output and segmentation classes; one to two weeks to validate an editor; first scientific result in about three weeks if all gates pass.",
      "design_template": "regional-substitution",
      "entry_point_2_requirements": "Measurement is centerline-orthogonal portal diameter; the named artifact is contrast-phase-dependent vessel conspicuity and warp signature.",
      "data": {"primary": "Public abdominal CT compatible with Merlin", "model": "Merlin"},
      "scores": {
        "clarity": {"value": 4, "why": "Named vessel, measurement, and intervention; output support remains to verify."},
        "identifiability": {"value": 4, "why": "Paired localized edits remove population confounds, conditional on a stringent edit-validity gate."},
        "medical_relevance": {"value": 3, "why": "It names a classic portal-hypertension-associated cue but does not establish pressure measurement."},
        "interest": {"value": 4, "why": "A foundation model using a vein as a manometer is concrete and clinically debatable."},
        "prior_legwork": {"value": 3, "why": "General models and segmenters exist; the critical editor does not."},
        "feasibility": {"value": 3, "why": "Capped; edit validity is uninspected."},
        "data_readiness": {"value": 3, "why": "Public CT exists, but exact model-compatible cohort is not frozen."},
        "evaluation_readiness": {"value": 3, "why": "Monotonic paired response is simple; edit-validity metrics are custom."},
        "negative_result_value": {"value": 3, "why": "Potentially decisive after gates, otherwise sensitivity-limited."},
        "novelty_confidence": {"value": 3, "why": "Capped and unaudited."},
        "regret": {"value": 3, "why": "Worth testing if the editor is easy; otherwise not an obvious missed opportunity."}
      },
      "unverified_claims": ["Merlin exposes a usable cirrhosis output", "Portal-vein segmentation class and accuracy", "Compatible public cohort", "Edit validity", "Novelty"]
    },
    {
      "id": "scout-015-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The continuous air tunnel inside the hiatal-hernia score",
      "question": "Is CT-CLIP's hiatal-hernia score using continuity of the esophageal air column across the diaphragm?",
      "deliverable_sentence": "The hiatal-hernia score is using a continuous air column through the esophageal hiatus.",
      "rung": "Mode C target is rung 1; rung 2 needs reconstruction and gastric-distension controls; rung 3 requires showing that the topology corresponds to herniated stomach rather than ordinary swallowed air.",
      "rung_reached": "Rung 1 at best from controlled synthesis; clinical naming beyond an air-column topology needs independent stomach/hiatus geometry validation.",
      "X_measurement": "Binary connectivity: after segmenting the esophagus/hiatus corridor, threshold gas below -800 HU and ask whether one 3D connected component intersects both a supradiaphragmatic esophageal zone and the infradiaphragmatic gastric zone; also record bottleneck area. Compute-today test: YES as a well-defined image measurement if the corridor can be generated automatically from surrounding organ masks.",
      "suspected_signal": "A sliding hiatal hernia can move gas-containing gastric lumen above the diaphragm, turning two separated gas pockets into a continuous topological path. A 3D model may exploit connectivity more readily than a human reader explicitly names it.",
      "use_vs_association": "Counterfactual synthesis opens or closes only a narrow gas bridge while holding hernia anatomy and all labels fixed; a score response beyond sham bridges tests use of connectivity, not population association.",
      "keystone_prerequisite": "Physically plausible bridge-opening and bridge-closing counterfactuals can be generated without creating an obvious synthetic seam or changing stomach/diaphragm geometry.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The verified adjacent fact is only that the frozen checkpoint has a hiatal-hernia head. The real assumption is that topology can be edited independently of lumen shape and gas volume; this may be physically impossible, which would kill the causal claim.",
      "dies_like_prior": "Dies like idea-006 if the bridge images are OOD. It differs by using minimal local air-for-air/tissue-for-tissue edits and explicit seam/sham gates, but no rhetorical distinction rescues it if those gates fail. No annotation-provenance issue enters the paired endpoint.",
      "closest_prior_work": "CT-RATE/CT-CLIP (arXiv:2403.17834) supplies the head; no primary study linking its output to gas-column connectivity has been verified. This is explicitly speculative, not a novelty claim.",
      "existing_assets": "Frozen CT-CLIP inference stack; public CT-RATE validation data; automated diaphragm, stomach, and esophagus landmarks may be derivable from public segmenters but are unverified.",
      "smallest_decisive_experiment": "On 20 automatically selected gas-containing cases, create connectivity-open, connectivity-closed, equal-volume displaced-gas, and sham edits. Blind an edit discriminator. Only if indistinguishable, compare within-case hiatal-hernia score changes and unrelated-head controls.",
      "standing_confounds_addressed": "Paired edits fix scanner/vendor/protocol/reconstruction/site/position/habitus/prevalence/referral and report labels. Gastric distension and total gas volume are controlled by equal-volume displacement. Synthetic seam and anatomical implausibility remain the critical threats.",
      "alternative_explanations": [
        "The model detects an edit seam; discriminator and sham tests address it.",
        "It responds to total supradiaphragmatic gas volume rather than connectivity; equal-volume disconnected controls exclude this.",
        "It reads stomach displacement, which cannot truly be held fixed when changing topology; not fully excluded and limits the claim."
      ],
      "anticipated_negative": "Decisive if counterfactual sensitivity and sham neutrality are demonstrated; otherwise uninterpretable.",
      "cross_domain": {"borrowed_construct": "Percolation/topological connectivity", "implied_measurement": "Whether a gas component spans the diaphragm and its bottleneck area", "what_changes_if_dropped": "Without the analogy, the binary connected-component measurement and open/close intervention remain identical; therefore percolation language is decorative and should not appear in the deliverable claim."},
      "remaining_legwork": "Two weeks for segmentation and editor feasibility; a further week for the 20-case readout if the gate passes.",
      "design_template": "counterfactual-synthesis",
      "entry_point_2_requirements": "Measurement is transdiaphragmatic gas connectivity; the named artifact is swallowed-air/gastric-distension variation and synthetic seams.",
      "data": {"primary": "CT-RATE validation split", "model": "released v2 ClassFine checkpoint"},
      "scores": {
        "clarity": {"value": 5, "why": "A binary physical quantity with a direct open/close intervention."},
        "identifiability": {"value": 4, "why": "Equal-volume controls isolate topology, conditional on edit realism; coupled anatomy prevents a perfect 5."},
        "medical_relevance": {"value": 3, "why": "Explains a common finding head, though the cue could be brittle rather than beneficial."},
        "interest": {"value": 5, "why": "A 3D model reading connectivity rather than size is surprising and broadly interpretable."},
        "mechanism_clarity": {"value": 5, "why": "Specific gas connectivity, exact thresholded measurement, and causal toggle are named."},
        "prior_legwork": {"value": 2, "why": "Model side is ready; measurement/editor side is speculative."},
        "feasibility": {"value": 2, "why": "Uninspected and likely difficult, reported outside Mode C priority."},
        "data_readiness": {"value": 4, "why": "Data and checkpoint are local/public."},
        "evaluation_readiness": {"value": 3, "why": "Paired score changes are easy; realism validation is custom."},
        "negative_result_value": {"value": 3, "why": "A valid editor yields a decisive scoped null; gate failure yields no scientific negative."},
        "novelty_confidence": {"value": 3, "why": "Capped; no audit completed."},
        "regret": {"value": 4, "why": "If feasible, it is an unusually clean test of a genuinely 3D cue."}
      },
      "unverified_claims": ["Automated esophagus/hiatus corridor viability", "Frequency of suitable gas-containing cases", "Counterfactual realism", "Novelty"]
    },
    {
      "id": "scout-015-c05",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The lung-opacity score may be reading gravity",
      "question": "Is a chest-CT lung-opacity score using the ventrodorsal lung-density gradient as a hydrostatic signature?",
      "deliverable_sentence": "The lung-opacity score is using the gravitational lung-density gradient.",
      "rung": "Mode C target is rung 1. Rung 2 requires real position-change or matched inspiratory controls; rung 3 is already a named physical/radiologic quantity once gravity direction is known.",
      "rung_reached": "Rung 1 only from a physics-preserving perturbation; a real prone/supine replication would move it toward rung 2.",
      "X_measurement": "Within each lung mask, regress HU on signed distance along the DICOM gravity axis, reporting HU per centimetre separately by lung and excluding vessels/airways; this is fully formulaic and computable on any scan today with an automated lung mask. Compute-today test: YES.",
      "suspected_signal": "Gravity creates a dependent increase in pulmonary blood/tissue fraction and reduced aeration. Edema, dependent atelectasis, and ordinary supine physiology can therefore write a smooth ventrodorsal HU gradient into CT that a lung-opacity classifier may use.",
      "use_vs_association": "Apply a smooth, lung-confined, zero-mean HU field that steepens or flattens the measured gradient without changing total lung density; monotonic score response relative to shuffled-axis and equal-energy texture controls identifies use of the gradient.",
      "keystone_prerequisite": "A smooth gradient perturbation can remain inside the model's training distribution while leaving total lung attenuation, visible lesions, and nonlung anatomy unchanged.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "It is easy to verify that gradients exist in supine lungs; that is not the keystone. The load-bearing assumption is intervention validity: a synthetic HU ramp is perceived as physiology rather than preprocessing or beam-hardening artifact.",
      "dies_like_prior": "Closest is idea-006: extreme image deletion was OOD. This uses a small zero-mean physical field and matched energy controls, but still dies the same way if edit detectability is high. It also learns from idea-007 by naming inspiration/coverage as controls. Labels are unused, so annotation provenance does not apply.",
      "closest_prior_work": "Primary CT physiology literature documents dependent density gradients, but exact identifiers have not yet been inspected; CT-CLIP/CT-RATE (arXiv:2403.17834) provides a lung-opacity output. No model-decoding precedent is asserted.",
      "existing_assets": "Public chest CT, lung segmentation, DICOM orientation, and an already verified CT-CLIP pipeline; the mathematical perturbation needs no learned generator.",
      "smallest_decisive_experiment": "Measure native gradients in 100 scans. On 30 mid-gradient cases, apply preregistered flatten/steepen ramps, reversed-axis ramps, and spatially shuffled equal-energy fields. Require discriminator equivalence and unchanged global HU histogram, then test monotonic lung-opacity score response.",
      "standing_confounds_addressed": "Within-scan perturbation fixes scanner/vendor/protocol/reconstruction/site/position/habitus/prevalence/referral and label leakage. Native inspiration and patient positioning are fixed. Beam hardening and edit signature remain; reversed-axis/equal-energy controls address but may not eliminate them.",
      "alternative_explanations": [
        "The model responds to any low-frequency HU ramp; reversed left-right and craniocaudal ramps test orientation specificity.",
        "The ramp changes lesion conspicuity; exclude lesion masks or stratify by opacity-free regions.",
        "Preprocessing normalization converts the edit into a global intensity cue; verify the final tensor and preserve its mean/histogram."
      ],
      "anticipated_negative": "Decisive only if the perturbation spans native physiological variation and passes realism/sensitivity controls; otherwise sensitivity-limited.",
      "cross_domain": {"borrowed_construct": "Hydrostatics in a deformable porous medium", "implied_measurement": "HU change per centimetre along gravity at fixed total lung attenuation", "what_changes_if_dropped": "The analogy determines the perturbation: preserve total mass while redistributing density along gravity. Dropping it would permit arbitrary brightness ramps and would change both controls and interpretation."},
      "remaining_legwork": "Several days to quantify the native range and inspect final-tensor effects; one week for the controlled 30-case probe, contingent on a fresh contract.",
      "design_template": "model-output-perturbation",
      "entry_point_2_requirements": "Measurement is HU/cm along gravity; the named artifact is beam hardening or a generic low-frequency intensity ramp.",
      "data": {"primary": "Public chest CT; not required to be CT-RATE", "model": "a frozen chest-CT lung-opacity classifier, CT-CLIP preferred"},
      "scores": {
        "clarity": {"value": 5, "why": "The physical quantity, axis, unit, and perturbation are explicit."},
        "identifiability": {"value": 4, "why": "Axis and equal-energy controls distinguish hydrostatic orientation from generic ramps; realism remains uncertain."},
        "medical_relevance": {"value": 3, "why": "It could explain false opacity calls in dependent lung and positioning sensitivity."},
        "interest": {"value": 5, "why": "The claim that a model reads gravity from lung density is surprising but physically grounded."},
        "mechanism_clarity": {"value": 5, "why": "A specific HU/cm quantity and mass-preserving intervention are named."},
        "prior_legwork": {"value": 3, "why": "Pipeline and masks exist; physiological range and editor validity are not established."},
        "feasibility": {"value": 3, "why": "Capped; the perturbation is cheap but its in-distribution status is uninspected."},
        "data_readiness": {"value": 4, "why": "Many public chest CTs suffice and labels are unnecessary."},
        "evaluation_readiness": {"value": 4, "why": "Paired monotonic response and matched controls are prespecifiable."},
        "negative_result_value": {"value": 4, "why": "With a validated native-range perturbation, a null directly weakens the hypothesis."},
        "novelty_confidence": {"value": 3, "why": "Capped; primary novelty search remains undone."},
        "regret": {"value": 4, "why": "It is cheap, label-free, and tests a cue that could matter across many thoracic heads."}
      },
      "unverified_claims": ["Primary quantitative range for normal dependent HU gradients", "Edit in-distribution status", "Availability of prone/supine replication data", "Novelty"]
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
   you found and record that no neighbors were found and use the calibrated verdict
   vocabulary of step 4 (`NO_DUPLICATE_FOUND_LIMITED_SEARCH` unless the
   search was genuinely exhaustive) -- this is a flag for
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

