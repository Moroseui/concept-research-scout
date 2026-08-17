You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/021
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
- **idea-021** [SHORTLISTED/CRITIQUED/baseline] -- The healthy hemisphere is the ruler
- **idea-022** [SHORTLISTED/SCOUTED/wide] -- Does the model mistake the end of the scan for the end of the bolus?
- **idea-023** [SHORTLISTED/SCOUTED/wide] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
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


===== ideas/021/README.md =====
# Idea 021: The healthy hemisphere is the ruler

Selected from scouting cycle isles24-002, candidate 2.


===== ideas/021/critique.md =====
# Critique — Idea 021: The healthy hemisphere is the ruler

```
FATAL OBJECTION: The claimed edit/readout disjointness does not survive the pipeline's own
intensity normalization — under nnU-Net's default per-image z-score for non-CT channels, a
contralateral-only scaling deterministically changes the affected side's post-normalization
inputs before the model runs, and simultaneously deletes the "absolute values" null arm.
EVIDENCE: MIC-DKFZ/nnUNet documentation/explanation_normalization.md ("zscore ... separately
for each train case" for everything except CT).
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

---

## 1. The decisive objection: the preprocessing already couples the hemispheres

The card's identifiability argument rests on one sentence: *"no pathway from edit to
readout exists except through a learned cross-hemispheric reference."* That sentence is
false, or at best contingent on an uninspected fact, because a normalization step sits
between the edited NIfTI and the network.

The card's stand-in model is a self-trained nnU-Net ("same recipe family as the winner").
nnU-Net's own documentation states the default normalization is **CT-scheme (fixed,
dataset-level statistics) for channels declared CT, and per-image z-score — "z-scoring
(subtract mean and standard deviation) separately for each train case" — for everything
else** (verified 2026-08-17 at
https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/explanation_normalization.md).
Deconvolved perfusion maps are not CT-attenuation channels; under a default recipe they get
per-image z-score. Both horns of the dilemma damage the design as written:

**Horn A — per-image z-score (the default).** Scaling contralateral CBF/CBV by factor *s*
changes the whole-image mean and standard deviation. Every affected-side voxel's
post-normalization value therefore changes deterministically, with no learning involved.
A positive "affected-side response to contralateral-only edits" is manufactured by the
preprocessing arithmetic; the model could be doing zero cross-hemispheric computation and
the readout would still move. Worse, the artifact has exactly the signature the hypothesis
predicts (affected-side output depends on contralateral values), so no amount of
dose-response rescues it. And the null arm collapses: after per-image z-score the model
*cannot* see absolute perfusion values — the card's advertised two-sided answer ("null ⇒
the model reads absolute values") is unavailable by construction. The card's alternative
explanation #1 ("the model normalizes globally") gestures at this but locates it inside the
model, where partial-area edits could separate it; located in preprocessing it is a
deterministic function the partial-area control does not remove.

**Horn B — fixed dataset-level normalization (CT-scheme or custom).** Then edit/readout
disjointness holds and the design works as stated — but the experimenter *chose* the
normalization, and the choice largely predetermines which answer is available. Since
challenge submissions each froze their own preprocessing (the winning team's paper is
literally titled "How We Won the ISLES'24 Challenge by Preprocessing," arXiv:2505.18424,
and does not disclose its intensity-normalization details; its windowing thresholds are
quoted as relative clinical values such as "CBF < 30%"), the stand-in assumption (card
residual assumption 2) becomes much heavier: the study characterizes one recipe's answer,
and the reference frame may live in *preprocessing* for some submissions and in the
*network* for others.

This is the wrong-keystone pattern the charter warns about, in its fourth costume. The
keystone screen verified co-registration (the nearest checkable thing, and genuinely true).
The load-bearing fact for identifiability is different: **the frozen pipeline's intensity
normalization scheme, which determines whether the edit is disjoint from the readout at the
network's input.** It was never inspected — it could not be, because the "official baseline
recipe" the card lists as an existing asset does not exist (keystone screen already
established the official repo contains only evaluation utilities), and the winner released
no code or checkpoint (search 2026-08-17: none found).

**The repair, which preserves the question.** Because the model is self-trained, the
normalization is under the study's control. Pin it: either (a) use fixed, cohort-level
normalization constants for the perfusion channels, frozen before any edit, so that
per-image statistics cannot transmit the edit; or (b) compute per-image statistics on the
*unedited* image and apply them to the edited one, making preprocessing a fixed function
per case. Either pin restores true disjointness. The question then becomes, stated
honestly: *does the network compute a mirror-specific contralateral reference beyond
whatever global standardization preprocessing already provides?* That is still the
interesting question — per-image z-score is a whole-image reference contaminated by the
lesion itself, whereas the clinical rCBF convention (Campbell 2011, PMID 21980202, verified
2026-08-17: relative CBF < 31% of mean contralateral, AUC 0.79 vs 0.74 for absolute CBV)
is mirror-specific precisely because the healthy hemisphere is uncontaminated. Mirror vs
whole-image is a real, clinically meaningful distinction, and the partial-area and
hemisphere-specific controls in the card are the right instruments for it. A free bonus
contrast falls out: a *global* (both-hemisphere) scaling under pinned normalization tests
whole-image-reference behavior directly and costs nothing extra.

## 2. The null was overstated even before the normalization problem

With the positive control passing, a gated null licenses "the model does not use
contralateral values," not "the model reads absolute perfusion values." Ipsilateral spatial
context (lesion texture, gradients, Tmax topology on the affected side alone) is an
unconsidered third reading that survives any null. After the repair in §1 the null becomes:
no mirror-specific reference beyond global standardization — a type-1 decisive negative for
the *mirror* hypothesis, but the card's advertised consequence ("fragility to cardiac
output and injection variation") no longer follows, because global standardization already
removes global hemodynamic scale. `negative_result_value` 4 → 3; `anticipated_negative`
must be rewritten.

## 3. Prior work: the delta survives, but the framing does not

The card says interpretability work on hemispheric normalization in stroke models "was not
found." Targeted search (2026-08-17) confirms no intervention-grade audit of a trained
model's reference frame — the novelty claim survives narrowly. But an adjacent literature
the card ignores has to be engaged, because it changes the prior: the field extensively
**hand-engineers** the contralateral reference into stroke networks. Symmetric modality
augmentation — feeding the flipped contralateral hemisphere as an extra channel — improved
Dice by 9–13 points in brain lesion segmentation (arXiv:1907.08196); symmetry-sensitive
CNNs for CTA stroke detection and contralateral-feature LVO detectors are established
(e.g., Nature Communications 10.1038/s41467-023-40564-8 and the reviews at
PMC9678444). Two consequences. First, the exact delta must be restated against this
literature: *the field bolts the mirror on because it suspects plain models do not discover
it; nobody has tested the suspicion on a plain model with an intervention.* Second, the
hand-engineering gains are indirect evidence that the expected answer is "no mirror
reference" — which is fine (the null is decisive after §2's rewrite), but the card's
"a well-trained model has every incentive to discover it" prose leans the other way without
acknowledging this evidence.

## 4. Feasibility is overstated; power is unexamined

- **No recipe, no checkpoint.** The "official baseline recipe" asset is already refuted by
  the keystone screen; today's search confirms the winning team released neither code nor
  checkpoint. Training is from scratch, recipe self-assembled. `prior_legwork` 4 → 3.
- **The benchmark's signal is weak.** The winning model's hidden-test Dice is 0.285 ±
  0.213 (arXiv:2408.10966; confirmed in arXiv:2505.18424). Final-infarct prediction on
  ISLES'24 barely works. The paired within-case delta on predicted volume is the right
  readout for a noisy model, but the card contains no minimum-detectable-effect reasoning
  at n = 40 held-out cases against a model whose outputs have this much variance. The
  revision must add an MDE estimate (from validation-fold prediction variability) before
  the 40-case experiment is called decisive.
- **Compute** (2–3 days training shared with c01, ~10 GPU-hours of edits) is plausible on
  the Colab Pro+ constraint with checkpoint-resumable nnU-Net training; not an objection,
  but it is the *whole* budget — the discriminator gate and symmetry-QC tooling are
  additional unbudgeted work.

## 5. Edit realism: the physiologic cover story is wrong, and one alternative is missing

The card defends the edit as mimicking "natural cardiac-output variation." Cardiac output
varies **globally** — it scales both hemispheres. No physiologic process uniformly scales
one hemisphere's CBF with a sharp midsagittal boundary *except unilateral carotid or
proximal vessel disease* — which is common in exactly this cohort. That creates an
unlisted alternative explanation: scaling the contralateral hemisphere *down* into the
low-physiologic range may read to the model as **bilateral or contralateral ischemia**,
changing the affected-side prediction through lesion-detection competition or laterality
reassignment, not through a reference computation. This is diagnosable — up-scaling and
down-scaling arms should behave asymmetrically under this mechanism and symmetrically
under pure normalization — so the fix is to add the up/down asymmetry contrast to the
preregistered analysis and this alternative to the card's list. Relatedly, the edit
touches only perfusion channels while NCCT/CTA channels stay frozen; the resulting
cross-channel inconsistency (hemisphere hypoperfused on CTP, normal on CTA) is part of
what the real-vs-edited discriminator must be shown to pass, and should be named in the
gate's definition rather than left implicit.

## 6. Smaller defects

- **Bilateral-disease exclusion is underspecified.** Follow-up lesion masks cover the acute
  lesion only; chronic contralateral infarcts (which corrupt the mirror) are not in any
  released mask. The symmetry-quality flag needs a concrete, automatic definition (e.g.,
  contralateral CSF/encephalomalacia volume by threshold, or mirror-residual magnitude) or
  the exclusion is a hand-wave.
- **The midline exclusion margin does not address receptive fields.** At the 3D U-Net
  bottleneck the receptive field spans both hemispheres nearly everywhere; a margin around
  the plane removes edge artifacts, not cross-hemisphere information flow. That flow *is*
  the hypothesized mechanism, so this is not fatal — but the card should stop implying the
  margin localizes anything; the dose-by-area control is what does the discriminative work.
- **Dataset concentration.** This is one of two ISLES'24 candidates sharing a trained model
  (with c01) — within the charter's two-per-dataset limit, but the shared-model coupling
  means a training failure kills both; note it in planning.
- **License.** Zenodo release is public noncommercial; no DUA gate — acceptable, record the
  restriction.

## 7. Score adjustments

- `identifiability` 4 → **2 as written** (the §1 pathway is real and unmitigated); restored
  to 4 by the normalization pin, which is why the decision is revision, not rejection.
- `negative_result_value` 4 → 3 (§2).
- `prior_legwork` 4 → 3 (§4; nonexistent baseline recipe already flagged by the keystone
  screen but never propagated to scores).
- `feasibility` 4 → 3 until the MDE analysis exists; the INSPECTED_TRUE keystone
  (co-registration) is genuine, but the identifiability-load-bearing fact (normalization)
  was not part of it — under the charter's intent, the cap-lifting inspection should cover
  the fact the inference actually needs.
- `novelty_confidence` 3 stands (delta survives §3, restated).

## 8. The easier versions

- **Zero-GPU Stage 0 (do this regardless):** freeze the recipe and *state the normalization
  scheme in the card as a design pin*. Half the original question — "is the reference frame
  in the preprocessing?" — is answerable by inspection for any pipeline whose code exists,
  today, at zero cost. For the field's pipelines it is unanswerable only because winners
  did not release code; that fact (verified today) is itself worth one line in any
  write-up.
- **Cheapest decisive contrast:** under pinned normalization, three arms — global scaling
  (both hemispheres), contralateral-only scaling, partial-area contralateral scaling —
  separate "no reference," "whole-image reference," and "mirror reference" with the same
  machinery the card already specifies. This is not a different study; it is the card's
  study with one added (cheap) arm and the confound removed. There is no meaningfully
  smaller version that still answers the question: an observational correlation across
  patients (contralateral CBF vs error) would be confounded by everything the paired design
  exists to remove, and is not worth doing.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Under normalization pinned to the unedited image,
does the network's affected-side final-infarct prediction respond to mirror-specific
contralateral perfusion changes beyond whole-image standardization — i.e., has it learned
the rCBF convention's mirror reference, or only a global gain control?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — same deliverable sentence, sharpened; the
mirror-vs-global distinction was already implicit in the card's alternative #1.
IS IT ACTUALLY WORTH DOING? YES — the field hand-engineers the mirror reference on the
belief that plain models lack it, nobody has run the intervention that tests the belief,
and both answers change how ISLES'24-class models should be preprocessed and trusted.
```

## Sources

- nnU-Net normalization defaults: https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/explanation_normalization.md
- ISLES'24 winner ("How We Won the ISLES'24 Challenge by Preprocessing"): https://arxiv.org/html/2505.18424v1
- ISLES'24 challenge report (winner Dice 0.285 ± 0.213): https://arxiv.org/abs/2408.10966
- Campbell et al. 2011, rCBF < 31% of mean contralateral: https://pubmed.ncbi.nlm.nih.gov/21980202/ / https://www.ahajournals.org/doi/10.1161/strokeaha.111.618355
- Symmetric modality augmentation (+9–13 Dice): https://arxiv.org/pdf/1907.08196
- Contralateral-feature LVO detection: https://www.nature.com/articles/s41467-023-40564-8
- Deep learning stroke imaging review (contralateral-comparison approaches): https://pmc.ncbi.nlm.nih.gov/articles/PMC9678444/
- Official ISLES'24 repository (no training recipe): https://github.com/ezequieldlrosa/isles24


===== ideas/021/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The experiment as specified cannot identify a learned contralateral reference because the stand-in nnU-Net pipeline's likely per-case z-score normalization creates a deterministic edit-to-readout pathway before the network sees the image.

**Argument:** The card's central identifying claim is that scaling only contralateral CBF/CBV while reading affected-side predictions is spatially disjoint, so any response must reflect learned cross-hemispheric computation. That is false under nnU-Net's documented default for non-CT channels: each case is z-scored using its own image mean and standard deviation. Scaling contralateral voxels changes both statistics and therefore changes every affected-side voxel at the network input even though its raw value was untouched. A model using only ipsilateral features could consequently show the predicted dose-response, and the partial-area arm would not rescue identification because it also changes the normalization statistics as a function of edited area. This is the charter's wrong-keystone error: co-registration was inspected, but the load-bearing fact is the frozen model pipeline's normalization and whether edited contralateral values can alter ipsilateral normalized inputs. It also invalidates the proposed interpretation of a null as "absolute-value reliance," because per-case z-scoring has already removed absolute scale. The repair does not change candidate identity: freezing cohort-level normalization constants, or computing each case's constants once on the unedited image and reusing them for every edit, still tests the original question of whether the network learned a healthy-hemisphere reference. Adding a both-hemisphere scaling arm would then distinguish mirror-specific reference use from global gain control. By contrast, merely reframing the claim as sensitivity to the overall preprocessing pipeline would no longer answer the original learned-reference question and would require a separate candidate.

**What would change my mind:** Show a frozen training-and-inference specification in which all perfusion-channel normalization constants are independent of each edited tensor (with a numerical A/B check that contralateral-only scaling leaves the affected-side network-input voxels bit-identical), and revise the null claim to "no mirror-specific reference beyond the pinned global standardization," with global, contralateral-only, and partial-contralateral scaling arms prespecified.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** Under nnU-Net's default per-case z-score for non-CT channels, a contralateral-only edit changes the whole-image mean and standard deviation and therefore deterministically changes every affected-side voxel at the network input. The card's identifying claim — that no pathway from edit to readout exists except through a learned cross-hemispheric reference — is false as written; the artifact even mimics the predicted dose-response, the partial-area control does not remove it, and the advertised null interpretation ("the model reads absolute values") is unavailable because per-case standardization has already destroyed absolute scale.

**Response:** AMEND

**Argument:** The objection is correct and I have no counter to its mechanism: whole-image per-case statistics are a function of the edited hemisphere, so the affected side's normalized inputs move with the edit through arithmetic alone. The card's keystone screen verified co-registration — genuinely load-bearing for constructing the edit — but the fact the identifiability inference actually needed was the frozen pipeline's normalization scheme, and that was assumed, not inspected. This is the wrong-keystone pattern, and I concede that diagnosis rather than defend the sentence as written.

The amendment adopts the critic's own repair, which is available precisely because the model is self-trained and the preprocessing is under the study's control:

1. **Normalization pin (design change, mandatory).** Perfusion-channel normalization constants are computed once per case on the *unedited* image and reused verbatim for every edited variant of that case (equivalently acceptable: frozen cohort-level constants fixed before any edit). Preprocessing becomes a fixed function per case, restoring true edit/readout disjointness at the network input.
2. **Verification gate.** Before any confirmatory run, a numerical A/B check on held-out cases must show that a contralateral-only edit leaves every affected-side network-input voxel bit-identical. This is now a preregistered pass/fail gate, not an assumption; the pinned normalization spec joins the keystone as an inspected fact rather than an inference.
3. **Third arm.** A global (both-hemisphere) scaling arm is added alongside contralateral-only and partial-area contralateral edits. The three arms separate no-reference, whole-image-reference, and mirror-specific-reference behavior — the mirror-vs-global distinction the card had buried in alternative explanation #1 becomes an explicit contrast, at negligible marginal cost.
4. **Null rewritten.** The gated null now licenses only: "the network computes no mirror-specific contralateral reference beyond the pinned global standardization." The "model reads absolute perfusion values" interpretation is withdrawn — the pinned standardization removes absolute scale by construction, so that claim was never reachable. `negative_result_value` drops 4 → 3 accordingly, and `anticipated_negative` must be rewritten in the card.

**Identity check:** the revised design still answers the original one-sentence question — is the model using the contralateral hemisphere as the patient-specific reference for judging the affected side's deficit? — sharpened to "mirror-specific reference beyond whatever global standardization preprocessing provides." The deliverable sentence survives: mirror-specific normalization is exactly what the clinical rCBF convention is (Campbell 2011's reference is the mean *contralateral* CBF, not the whole-image mean, because the healthy hemisphere is uncontaminated by the lesion). This is a narrowing within the same deliverable, not a new study wearing the old title.

**What is lost, stated plainly:** (a) The two-sided answer is weakened — "reads absolute values" is gone as a possible finding, since the standardization choice is now a design pin rather than a discovery; the null's clinical consequence (fragility to cardiac output and injection variation) no longer follows, because pinned global standardization already removes global hemodynamic scale. (b) The stand-in caveat grows heavier: challenge submissions each froze their own undisclosed preprocessing, so the reference frame may live in *preprocessing* for some submissions and in the *network* for others; this study characterizes one pinned recipe's network and must say so. (c) One amendment in round one, adopted from the critic's stated conditions verbatim — the original identifiability argument was wrong, and the repair works only because the normalization was ours to pin.

**Status:** CONVERGED

## Round 2 — CRITIC

**Position:** The normalization amendment preserves the original question and closes my first objection, but the three-arm experiment still cannot identify the specific claim that the network computes the clinical rCBF-style contralateral denominator rather than merely reacting to an abnormal hemispheric mismatch.

**Argument:** I concede the preprocessing objection because reusing unedited-image constants plus the bit-identity gate removes the deterministic edit-to-readout path, and this amendment passes the identity check: it still asks whether the healthy hemisphere supplies the patient-specific reference. The remaining problem is downstream identifiability. A contralateral-only CBF/CBV scaling creates a new hemispheric asymmetry while CTA, NCCT, Tmax, and the affected-side perfusion remain fixed. A network that detects bilateral/contralateral hypoperfusion, compares left-right features for lesion laterality, or reallocates a finite lesion probability between hemispheres can change the affected-side prediction monotonically without ever dividing affected CBF by mean contralateral CBF. The global arm does not distinguish these mechanisms: global scaling creates no new asymmetry, so a mismatch detector predicts little response while a true ratio computation is likewise invariant. The partial-area arm also does not identify a denominator; both a spatial mismatch detector and a mirror reference can scale with edited area. Thus the proposed positive supports only “the model uses contralateral perfusion information,” not the card's stronger physician-legible sentence that it uses the healthy hemisphere as the same relative-to-mirror normalization clinicians apply. This distinction matters because Campbell et al. define a specific ratio to mean contralateral CBF, whereas the experiment currently tests a family of cross-hemispheric computations. The unilateral edit's real-vs-edited discriminator cannot solve this: even a visually in-distribution edit may represent genuine contralateral vascular disease, under which laterality competition is biological rather than an edit artifact.

**What would change my mind:** Prespecify a factorial response-surface test that makes the rCBF mechanism uniquely predictive: independently vary affected-side and contralateral CBF over an in-distribution grid, include common-gain transformations, and show that predictions collapse onto the affected/contralateral ratio (with a frozen equivalence margin) better than preregistered absolute-value, hemispheric-difference, minimum-value, and laterality-competition models; additionally require the cross-channel realism gate for every factorial arm. If direct affected-side edits make that comparison uninterpretable, narrow the deliverable to “the model uses contralateral perfusion information” and treat the rCBF-normalization claim as a separate successor rather than asserting rung 3.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** Even with the normalization pinned, a positive result in the three-arm design identifies only membership in a family of cross-hemispheric computations — mismatch detection, left-right feature comparison, laterality competition, minimum-taking — not the specific claim in the deliverable sentence that the network computes the clinical rCBF-style contralateral denominator. The global and partial-area arms cannot separate these mechanisms, and the deliverable sentence therefore asserts more than the experiment can show.

**Response:** AMEND

**Argument:** The gap is real and I will not paper over it: the deliverable sentence promised the ratio, and the three arms identify only "some mirror-specific contralateral computation." Worth stating plainly where the fault came from — the card's own `rung` field targeted rung 1 ("the model computes a cross-hemispheric reference"), while its deliverable sentence asserted the mechanism's identity with the clinical convention. That is the charter's named standard failure, rung-1 evidence under a rung-3 sentence, present in the card from the start; the critic has now made it undeniable. The amendment aligns the claim with the design rather than inflating the design to rescue the claim.

**The amendment — a two-tier claim structure:**

1. **Tier 1 (confirmatory, the machinery already agreed):** the three-arm paired design under the round-1 pins tests exactly "the network computes a mirror-specific contralateral reference beyond the pinned global standardization." The deliverable sentence is revised to assert exactly this and no more: *"The model is using the healthy hemisphere as the patient's personal perfusion baseline when judging the affected side's deficit."* The identification with Campbell's rCBF convention is demoted from asserted mechanism to motivating anchor — it explains why a physician cares about the answer; it is no longer claimed as what the network computes.

2. **Tier 2 (prespecified secondary signatures, no new arms required):** the critic's named mechanism family makes divergent predictions that are already observable in the planned arms plus the cohort's natural variation, without touching the affected side: (i) *dose-response shape* — a ratio mechanism predicts the response is a function of the scale factor s alone, case-independent; (ii) *baseline dependence* — a difference mechanism (a − c̄) predicts response magnitude proportional to c·(1−s), i.e., dependent on each case's absolute contralateral level, which a ratio mechanism predicts is irrelevant; this contrast is cross-case and therefore observational, and is labeled secondary for that reason; (iii) *up/down asymmetry* — laterality competition (the scaled hemisphere read as newly ischemic) predicts strong asymmetry between down- and up-scaling, while a normalization mechanism predicts approximate symmetry; (iv) *threshold behavior* — minimum-value mechanisms predict response only where scaled contralateral values cross affected-side levels. These are directional, preregistered signatures against named alternatives — not a claim that a frozen equivalence margin on ~40 noisy cases can adjudicate a full response-surface model comparison.

3. **The factorial with affected-side edits is not adopted, and I will say why rather than quietly dropping it.** Editing the affected side edits the very tissue the model is asked to segment: intervention and readout coincide, the realism gate becomes "edit the pathology believably," and a response is interpretable only through a model of how the lesion edit itself should propagate — the disjointness that made this candidate identifiable is gone for that arm. This is the critic's own anticipated fallback: if tier-2 signatures are ambiguous, the rCBF-ratio identification becomes a **successor candidate** with the factorial as its design problem, and is not asserted here.

**Identity check:** the card's one-sentence question — is the model using the contralateral hemisphere's perfusion as the patient-specific reference against which the affected side's deficit is judged? — is precisely tier 1, unchanged. What moves is an elaborating clause inside the deliverable sentence: "the same relative-to-mirror normalization radiologists apply" shifts from asserted identity to conditional (tier 2 / successor). I read this as narrowing within the same deliverable under the claim-identity rule — the sentence's subject and predicate survive; a mechanism-identity appositive is demoted to match the declared rung. If the human adjudicates the sentence's identity as changed, the recorded fallback is the critic's: register the ratio claim as a successor and keep tier 1 as this candidate.

**What is lost, stated plainly:** (a) The physician-legible sentence gets its weaker form; the satisfying "the network rediscovered the clinicians' own convention" identity may never be claimable inside this study. (b) Tier-2's most discriminating contrast (baseline dependence) is cross-case observational — confoundable by whatever else correlates with absolute contralateral CBF — and cannot carry confirmatory weight. (c) This is the second amendment in two rounds, both adopting the critic's stated conditions; the original card overclaimed twice (edit/readout disjointness, and rung). What survives both rounds unchanged is the paired intervention machinery, the pins and gates, and a question both of whose answers still matter: a mirror-specific reference found means benchmark models recover the clinical frame from data alone; none found means the field's habit of hand-engineering the mirror (symmetric-modality augmentation, contralateral-feature detectors) is compensating for a real absence, now shown by intervention rather than suspected.

**Status:** CONVERGED

## Round 3 — CRITIC

**Position:** The amendment demotes the explicit rCBF ratio but still labels any cross-hemispheric response a “personal perfusion baseline,” so the confirmatory claim remains stronger than the experiment identifies.

**Argument:** The round-2 concession correctly withdraws identity with Campbell's mean-contralateral-CBF ratio, but changing “same relative-to-mirror normalization” to “healthy hemisphere as the patient's personal perfusion baseline” does not resolve the mechanism-family objection. “Baseline” is itself a functional claim: contralateral values must set the reference against which affected-side deficit is judged. Yet the three-arm result remains equally compatible with the alternatives already named in round 2—hemispheric-mismatch detection, lesion-laterality assignment, competition between bilateral candidate lesions, or any cross-hemispheric contextual feature. The proposed tier-2 signatures do not repair tier 1 because they are expressly secondary and non-adjudicating; moreover, approximate up/down symmetry is not unique to normalization, and case-independent response to a multiplicative scale factor is not guaranteed by a learned ratio once nonlinearities and local value distributions enter. Thus the strongest confirmatory sentence supported by the intervention is only: “The model uses contralateral perfusion information when producing affected-side predictions.” That is human-legible and rung-honest, but it no longer answers the original question of whether the contralateral hemisphere is used *as a patient-specific reference*. Under the program's claim-identity rule, deleting the reference function changes the deliverable predicate, not merely an appositive, so this reduced study should be registered as a successor rather than approved as Idea 021. The original reference question can remain Idea 021 only with an experiment that discriminates reference-setting from the named cross-hemispheric alternatives.

**What would change my mind:** Show a preregistered intervention or model-comparison test, with a frozen decision margin and adequate power, under which a personal-baseline computation makes a prediction that hemispheric mismatch, laterality competition, bilateral-lesion detection, and generic contralateral context do not; otherwise register the “uses contralateral perfusion information” experiment as a new successor and keep the original baseline-reference claim unresolved.

**Status:** OPEN

## Round 3 — PROPOSER

**Responding to:** "Personal perfusion baseline" is still a functional claim — that contralateral values set the reference against which the affected side's deficit is judged — and the three-arm design cannot separate that function from hemispheric-mismatch detection, laterality competition, bilateral-lesion detection, or generic contralateral context. The tier-2 signatures are expressly non-adjudicating and cannot repair tier 1. So either produce a preregistered, powered test under which the baseline computation makes a prediction none of those alternatives makes, or the study supports only "uses contralateral perfusion information" and must register as a successor.

**Response:** AMEND

**Argument:** One part of the objection I contest before amending, because it determines whether the demanded test is even constructible: the critic's alternative list mixes two different kinds of thing. Once the Campbell-ratio identity was withdrawn in round 2, "the healthy hemisphere is the patient's personal baseline" means, at the declared rung: *the model's judgment of the affected side's deficit is a function of the signed contrast between affected-side and contralateral perfusion, not of affected-side values alone.* A "hemispheric-mismatch detector" that judges the affected side by signed left-right comparison, and "left-right feature comparison" feeding the deficit estimate, are not alternatives to that claim — they are implementations of it. Ratio, difference, learned comparator: distinguishing among these is the round-2 tier-2/successor question, already conceded. Requiring the design to exclude "hemispheric mismatch" tout court is requiring it to exclude the predicate under another name, and no experiment can do that. The genuine alternatives — the ones under which the deliverable sentence would be *false* despite a positive result — are the non-reference pathways: (A) laterality competition / bilateral-lesion detection, where the edited hemisphere is read as itself pathological and the affected-side output moves through lesion-candidate reallocation; (B) unsigned anomaly detection plus independent laterality assignment; (C) generic contralateral context with no directional role in the deficit judgment. The amendment makes excluding (A)–(C) the confirmatory bar.

**The amendment — tier 1 becomes a preregistered conjunction, with the up-scaling arm carrying the discriminating weight:**

1. **Signed monotone dose-response, both directions required.** Affected-side predicted deficit must increase monotonically in the contralateral scale factor s — in particular, *up-scaling* the healthy hemisphere (more blood in the untouched-normal side) must *increase* the predicted infarct on the affected side. This direction is the reference mechanism's signature and belongs to none of the genuine alternatives: laterality competition and bilateral-lesion detection require a new hypoperfused lesion candidate, which up-scaling removes rather than creates; unsigned anomaly detection predicts response to |asymmetry| with no basis for the affected-side deficit to *grow* when the other hemisphere becomes healthier; generic context predicts no specific sign. Under the clinical frame the prediction is automatic: raising the denominator's side pushes rCBF down and more tissue below threshold. Down-scaling arms are retained but are confirmatory only in conjunction, since competition and reference predict the same sign there.
2. **Contralateral-emergence gate, promoted from tier-2 signature to hard gate.** In every arm, contralateral predicted lesion volume is monitored against a threshold frozen before any edited case is scored. A breach marks the competition/bilateral-detection pathway (or OOD behavior) as active and invalidates that arm at that dose — it does not get reinterpreted.
3. **Mirror-specificity margin.** The contralateral-only response must exceed the global-arm response, margin frozen with the rest.
4. **Power, before any confirmatory scoring.** A minimum-detectable-effect analysis from validation-fold prediction variability (the critique's §4 demand, now binding) fixes whether the paired trend test at 40 cases can detect the frozen slope margin; if not, the case count is raised or the study reports itself unpowered rather than running to an uninterpretable null.

**Preregistered fallback, adopting the critic's otherwise-branch:** if the conjunction is unreachable — the up-scaling arm fails the realism/discriminator gate (hyperperfused-hemisphere edits may have a narrow in-distribution envelope), the emergence gate trips, or power fails — the reported claim is exactly "the model uses contralateral perfusion information," recorded as *not resolving* the baseline-reference question, and the human adjudicates successor registration under the claim-identity rule at that point. The weaker sentence is the failure-path report, not a quiet rebadging of this candidate.

**Identity check:** the one-sentence question — is the model using the contralateral hemisphere's perfusion as the patient-specific reference against which the affected side's deficit is judged? — is unchanged, and the predicate ("as the reference") is now what the confirmatory conjunction operationalizes, not a label applied to any cross-hemispheric response. This amendment raises the bar for saying yes; it does not move the question.

**What is lost, stated plainly:** (a) This is the third amendment, and the rule says three amendments usually means the original idea was wrong. Partly true here: the card as written overclaimed twice (disjointness, rung) and underspecified tier 1 once. What has never changed is the question sentence, the paired contralateral-edit machinery, and the readout; each amendment narrowed claims to match the design rather than swapping the design to rescue a claim. The human should weigh that history, not my characterization of it. (b) The discriminating arm is the most fragile one: up-scaling has the narrowest physiologic envelope, and if it dies at the realism gate the study can no longer answer its own question — the fallback outcome ("uses contralateral information, reference unresolved") is now a live and perhaps likely result. (c) The conjunction plus frozen margins plus MDE gate makes the positive finding harder to reach at n = 40; the cheap one-week sketch in the card is gone, and `feasibility` must reflect the added gates and power work. (d) Within-family mechanism identity (ratio vs difference vs learned comparator) remains outside this study, permanently — that concession from round 2 stands.

**Status:** CONVERGED — the critic's stated condition was a preregistered intervention test under which the baseline computation predicts something mismatch-as-implementation aside, competition, bilateral detection, and generic context do not; the signed up-scaling response with the emergence gate and frozen margins is that test, and the critic's otherwise-branch is adopted verbatim as the preregistered failure path. If the critic holds that signed left-right comparison feeding the deficit judgment must *also* be excluded, that is the irreducible point for the human: on my reading it is the claim itself, not an alternative to it.


===== ideas/021/idea_card.json =====
{
  "id": "isles24-scout-002-c02",
  "search_mode": "B",
  "entry_point": 2,
  "title": "The healthy hemisphere is the ruler",
  "question": "Is an ISLES'24 final-infarct model using the contralateral hemisphere's perfusion as the patient-specific reference against which the affected side's deficit is judged?",
  "rung": "Target rung 1: the model computes a cross-hemispheric reference; rung 2 with center-held-out replication and dose-response in the scaling factor.",
  "deliverable_sentence": "The model is using the healthy hemisphere as the patient's personal perfusion baseline -- the same relative-to-mirror normalization radiologists apply when they read relative CBF -- rather than absolute map values.",
  "X_measurement": "Mirror-reference perfusion: mean contralateral CBF (and Tmax) in reflected ROIs about the automatically estimated midsagittal plane, giving rCBF = CBF / mean contralateral CBF. The clinical anchor is Campbell et al., Stroke 2011 (DOI 10.1161/STROKEAHA.111.618355, PMID 21980202): relative CBF, optimally <31% of mean contralateral, is the best CTP core definition -- the normalization itself is the established clinical practice. Compute-today test: YES; symmetry-plane estimation and mirroring are standard automatic operations.",
  "suspected_signal": "Deconvolved CTP values are semi-quantitative -- they move with cardiac output, injection protocol, and AIF selection -- so the physiologically meaningful quantity is the deficit relative to the same brain's normal tissue; the intact hemisphere is the only in-image source of that baseline, and a well-trained model has every incentive to discover it.",
  "use_vs_association": "The intervention region and the readout region are disjoint: scale perfusion values only in the contralateral hemisphere (within the observed inter-patient physiologic range), leave the affected side untouched, and measure the change in the affected-side prediction; no pathway from edit to readout exists except through a learned cross-hemispheric reference.",
  "keystone_prerequisite": "Per-case perfusion maps are co-registered into a common space where a hemisphere-restricted edit and an affected-side readout can be constructed automatically.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "Official repository (github.com/ezequieldlrosa/isles24, fetched 2026-08-16): derivatives contain 'Perfusion maps registered to NCCT space'; Zenodo record 16731717 lists CBF/CBV/MTT/Tmax per case with co-registered derivative versions.",
  "keystone_residual_assumption": "Still assumed: (1) hemisphere-scaled inputs remain in-distribution -- gated by restricting scale factors to the empirical inter-patient range and by a held-out real-vs-edited discriminator; (2) the trained model is a fair stand-in for challenge submissions (self-trained nnU-Net, same recipe family as the winner); (3) midline estimation is reliable in cases with mass effect -- hyperacute cases rarely have large shifts, but each case gets a symmetry-quality flag.",
  "rung_reached": "0 now; rung 1 after a systematic affected-side response to contralateral-only edits with shams passing; rung 2 after dose-response and cross-center replication.",
  "dies_like_prior": "Closest is idea-006 (extreme OOD deletion made the intervention indefensible). Different because the edit is a parametric scaling inside the physiologic envelope -- it mimics natural cardiac-output variation rather than deleting content -- and carries an explicit in-distribution gate. No annotation-provenance exposure: the primary readout is label-free.",
  "closest_prior_work": "Campbell et al. 2011 (PMID 21980202) established contralateral normalization as clinical practice in patients; ISLES'24 reports (arXiv:2408.10966) rank models without asking what reference frame they compute. Interpretability work on stroke CTP models addressing hemispheric normalization was not found in today's search -- recorded as a search result, not proof of absence. Exact delta: an intervention-grade test of whether a learned model reproduces, or ignores, the field's own normalization convention.",
  "existing_assets": "Registered perfusion maps for 149 cases; automatic symmetry-plane tools; the empirical distribution of contralateral CBF across the cohort (defines the physiologic edit range); official baseline recipe.",
  "smallest_decisive_experiment": "One frozen model; 40 held-out cases; scale contralateral-hemisphere CBF and CBV jointly by factors spanning the middle 90% of the observed inter-patient ratio range; readout is the paired change in affected-side predicted lesion volume. Controls: partial-area contralateral edits (dose by area), affected-side positive control (must respond), noise-matched sham. Under 10 GPU-hours after model training.",
  "standing_confounds_addressed": "Within-case paired design holds patient, scanner, site, protocol, habitus, and prevalence fixed by construction; the disjoint edit/readout geometry excludes direct leakage. Not ruled out: bilateral chronic disease or prior contralateral infarcts corrupt the mirror -- such cases are flagged and excluded via the lesion masks and symmetry check; boundary effects at the midline are handled by an exclusion margin around the plane.",
  "alternative_explanations": [
    "The model normalizes globally (whole-brain mean) rather than contralaterally: partial-area and hemisphere-specific edits separate these two references.",
    "Convolutional receptive fields straddle the midline and the response is local leakage, not normalization: the exclusion margin and the dose-by-area control address this.",
    "The response is an artifact of edited-input distribution shift: the discriminator gate and physiologic-range restriction bound it."
  ],
  "anticipated_negative": "Decisive and valuable: with the positive control passing, a null says the model reads absolute perfusion values -- which implies fragility to cardiac output and injection variation that the field's own normalization convention exists to remove. Both outcomes are publishable statements about benchmark models.",
  "remaining_legwork": "2-3 days model training (shared with c01), 1 day edit construction and gates, 2 days runs and analysis: about one week to first decision.",
  "design_template": "other:remote-perturbation",
  "design_template_justification": "The identifying structure is that the intervention region and the readout region are spatially disjoint, so the effect can only travel through a learned reference computation; none of the ten named grammars encodes intervention-readout disjointness, and mislabeling it regional-substitution would hide exactly the property that makes it identifiable.",
  "entry_point_2_requirements": "Measurement: mirror-normalized rCBF per Campbell et al. Artifact it would be confused with: midline-estimation error and bilateral chronic disease breaking mirror symmetry; both receive per-case quality flags and exclusions.",
  "scores": {
    "clarity": {
      "value": 5,
      "why": "One-sentence question with a single named reference quantity and a mechanical test."
    },
    "identifiability": {
      "value": 4,
      "why": "Disjoint intervention/readout is structurally strong; residual risk is edit realism and midline leakage, both gated."
    },
    "medical_relevance": {
      "value": 4,
      "why": "Whether AI reproduces the rCBF convention determines its robustness to hemodynamic and protocol variation -- a deployment-relevant property clinicians can reason about."
    },
    "interest": {
      "value": 4,
      "why": "A crisp question about the model's internal frame of reference with a genuinely two-sided answer."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Clinical anchor, registered maps, and edit machinery all exist; only model training remains."
    },
    "feasibility": {
      "value": 4,
      "why": "Keystone INSPECTED_TRUE; the cheapest candidate this cycle -- parametric edits, no segmentation dependencies."
    },
    "data_readiness": {
      "value": 4,
      "why": "Public noncommercial release contains everything needed."
    },
    "evaluation_readiness": {
      "value": 4,
      "why": "Label-free paired deltas with standard gates; no custom metrics beyond the discriminator."
    },
    "negative_result_value": {
      "value": 4,
      "why": "A gated null is a positive claim (absolute-value reliance) with a named clinical consequence."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "No exhaustive search; today's targeted search found no hemispheric-normalization audit of stroke models."
    },
    "regret": {
      "value": 4,
      "why": "Obvious in hindsight: the field's own normalization convention has never been checked against its own benchmark models."
    }
  },
  "unverified_claims": [
    "In-distribution validity of hemisphere scaling",
    "midline estimation reliability in this cohort",
    "absence of prior normalization audits beyond today's search"
  ],
  "track": "baseline",
  "charter": "isles24"
}


===== ideas/021/keystone_screen.md =====
# Keystone screen

## Keystone as stated

> Per-case perfusion maps are co-registered into a common space where a hemisphere-restricted edit and an affected-side readout can be constructed automatically.

## What was inspected

I inspected the authors' official dataset record, the full methods section of the primary dataset paper, and a local clone of the authors' official challenge repository at commit `94b34863a099a8aeae6cf9b989c78ff2c767b80e`.

The official Zenodo record states, verbatim:

> “'Derivatives' include all modalities linearly co-registered to the NCCT space.”

Source: https://zenodo.org/records/16813698, **Data structure** (lines 53–55 in the rendered record). The same record enumerates NCCT-space derivative CBF, CBV, MTT, and Tmax files and an NCCT-space follow-up lesion mask (lines 67–82). This directly establishes that the released derivative perfusion maps and outcome mask have a shared named reference space within each case.

The primary dataset paper independently describes the processing:

> “CTA, CT perfusion (including derived perfusion maps), and DWI and/or apparent diffusion coefficient scans were linearly co-registered to the noncontrast CT space using rigid transformations for CT and affine transformations for MRI using Elastix (version 5.3.0; elastix.lumc.nl) and NiftyReg (version 1.5.69.6; github.com/KCL-BMEIS/niftyreg).”

Source: https://pubs.rsna.org/doi/full/10.1148/ryai.250603, **Data Preprocessing** (DOI `10.1148/ryai.250603`; paragraph beginning at rendered line 102).

The official repository provides a consistent file-level statement. Its README lists `space-ncct` CBF, CBV, MTT, and Tmax derivatives under the same per-subject session directory. Source: https://github.com/ezequieldlrosa/isles24/blob/94b34863a099a8aeae6cf9b989c78ff2c767b80e/README.md#L26-L37.

These are primary-source statements about the released data, not an inference from a search result. They verify the load-bearing availability of within-case, NCCT-referenced perfusion maps needed to define spatially disjoint hemisphere edits and readouts.

## Mandatory residual-assumption check

**If this card only verified the nearest checkable thing, what is it still assuming?**

The nearest checkable fact is that files named as NCCT-space derivatives exist. The inference additionally assumes that the actual NIfTI headers/arrays are mutually compatible after the eventual model's frozen preprocessing, that left-right orientation is preserved, and that a usable midsagittal plane and hemisphere masks can be derived case by case. I did not inspect the 99 GB `train.7z` archive's NIfTI headers, so exact voxel-grid congruence is not directly verified here. This is a real Stage-0 implementation/quality-control residual, but it is not a different cohort-level keystone: the authors explicitly say all modalities were co-registered to NCCT space, and exact grids can be resampled within that common physical coordinate system.

A separate nearby claim does **not** survive inspection: the card says an “official baseline recipe” exists, but the official repository at the inspected commit contains only the README, evaluation utilities, and an evaluation notebook—no training loader, model configuration, or nnU-Net recipe. That omission weakens the card's `existing_assets` and feasibility language, but it does not make the proposed study impossible because the card already specifies training a model rather than requiring a released checkpoint. It should not be mistaken for evidence about the registration keystone.

The edit's in-distribution validity and midsagittal-plane reliability remain empirical gates, as the card itself acknowledges. They are not established by co-registration and must not be treated as already verified.

```json
{"verdict": "PASS", "evidence": "'Derivatives' include all modalities linearly co-registered to the NCCT space.", "source": "https://zenodo.org/records/16813698, Data structure, lines 53-55", "note": "The common-space prerequisite is directly supported; exact header congruence, orientation QC, and automatic midline reliability remain Stage-0 checks, and no official training recipe was found."}
```


===== STAGE TASK =====
Read the full `debate.md` and write `consensus.md`. You are summarizing, not
adjudicating: do not declare a winner.

```markdown
# Debate summary — idea NNN

## Agreed
- [points both sides accept, with the round where agreement occurred]

## Unresolved
For each: the question, the proposer's position, the critic's position, and
**what evidence would settle it**. If no evidence could settle it, say that
plainly — it means the disagreement is about values or taste, not facts.

## Positions that moved
For each concession: who conceded, in which round, and in response to what
argument. If someone conceded without being given a new argument, flag it as
UNEARNED — capitulation is not agreement and should not be recorded as
consensus.

## Amendments made
What the idea now claims versus what it claimed at round zero. Note anything
lost.

## Recommendation
ADVANCE | REVISE | PAUSE | REJECT — plus the single most important thing the
human should look at before deciding.
```

If the debate converged in one round with no real objection raised, say so
explicitly. That is evidence the critic is not working, and it matters more
than the idea under discussion.


## Machine-readable verdict (required)

End `consensus.md` with exactly one fenced json block encoding the verdict so
the orchestrator can update the ledger:

```json
{"verdict": "PAUSE|REVISE|KILL|PROCEED", "kill_code": "<taxonomy code, only for KILL>", "unblock": "<one line: the condition that would change the verdict>"}
```


===== KILL CODE TAXONOMY (use one of these in the verdict block) =====
USE_VS_ASSOCIATION: Studies what a model associates with X, not whether it causally uses X.
ANNOTATION_PROVENANCE: Inference depends on who assigned labels / what they could see, and that is undocumented or contaminated.
CIRCULARITY: The endpoint is a re-encoding of the input or of the thing being tested.
DATA_INSUFFICIENT: The subset that actually supports the inference is too small or unreachable.
DATA_ACCESS: Required data, checkpoints, or mappings are not obtainable in practice.
EFFECT_UNREACHABLE: The claimed effect cannot exceed a published bound / measurement floor.
FREE_BASELINE_WINS: A ground-truth-free structural baseline plausibly matches the learned approach.
COMPUTE_INFEASIBLE: Cannot be tested inside one compute envelope (one Colab GPU session).
DUPLICATE_PRIOR: Already done; no defensible delta to the closest prior work.
NO_TESTABLE_KERNEL: No measurable quantity survives translation from the source idea (fiction-track exit).
IDENTIFIABILITY_FAILURE: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
UNCLASSIFIED: Kill reason recorded free-text only; classify when pattern recurs.
