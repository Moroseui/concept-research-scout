You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/022
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
- **idea-022** [SHORTLISTED/CRITIQUED/wide] -- Does the model mistake the end of the scan for the end of the bolus?
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


===== ideas/022/README.md =====
# Idea 022: Does the model mistake the end of the scan for the end of the bolus?

Selected from scouting cycle isles24-001, candidate 7.


===== ideas/022/critique.md =====
# Critique: Does the model mistake the end of the scan for the end of the bolus? (idea 022)

```
FATAL OBJECTION: The study object — a frozen, performant ISLES'24 final-infarct model that consumes raw 4D CTP — does not exist as an obtainable artifact, and every substitute changes the question or breaks the card's own envelope.
EVIDENCE: arXiv:2505.18424v2 Table 1 (winner's inputs: CTA, CBF, CBV, MTT, Tmax — derived maps, not raw CTP); github.com/kimberly-amador/ISLES24-PrediCTP (only public raw-4D-CTP entry: training code, no released checkpoint, Dice 0.20, lesion-wise F1 0.02).
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: PAUSE
```

Unblock condition: an obtainable frozen raw-CTP final-infarct model with documented temporal-input semantics (padding/masking seen in training) and non-trivial performance — via a future challenge release, another team's checkpoint, or author correspondence with the PrediCTP group (the idea-002 unblock pattern). The nested-prefix design itself survives intact and should not be redrafted on unpause.

---

## 1. The fatal objection in full: there is no model to audit

The deliverable sentence is "The **raw-CTP final-infarct model** is using terminal-curve incompleteness…". The card never names the model, and the keystone screen (correctly returned `UNVERIFIABLE`) already showed the published winner cannot be it: Ren et al. (arXiv:2505.18424v2, Table 1) feed the final nnU-Net **CTA, CBF, CBV, MTT, and Tmax** — derived 3D maps, no raw time series.

New legwork for this critique found the closest thing to the required artifact: Amador et al., *Spatio-Temporal Deep Learning for Final Infarct Prediction using Acute Stroke CT Perfusion Data* (Springer, DOI 10.1007/978-3-031-81101-2_9; official repo `kimberly-amador/ISLES24-PrediCTP`). It genuinely consumes 4D CTP (CNN encoder + temporal Transformer + CNN decoder). But:

- **No released checkpoint.** The repository provides training and inference code only. The frozen artifact the card's estimand requires does not exist publicly.
- **Dice 0.20, absolute volume difference 17 ml, lesion-wise F1 0.02** on the 143-patient multicenter evaluation.
- Temporal padding/masking semantics are undocumented in the README, so the card's second keystone clause (prefixes in-distribution) cannot be inspected even for this architecture.

Every path around this damages the claim:

1. **Audit the winner instead.** Then the question becomes "does truncation propagate through deconvolution into the derived maps" — which Kasasbeh (PMID 25789631) and Copen (PMID 25500309) already established, with phantoms. The novelty delta collapses to prior work.
2. **Train a raw-CTP model yourself.** This violates the card's own compute envelope ("one frozen model, no retraining"), and — worse — it is quietly circular: whether short prefixes are in-distribution is decided by the *experimenter's* training-time augmentation choices. Train with temporal dropout and the model plausibly shrugs off censoring; train without and padding is OOD by construction. The experiment would measure a property you installed. The card's claim would degrade from "an ISLES'24 benchmark model has this failure mode" to "a model I trained can be given or denied this failure mode," which is a different and much less interesting sentence. Under the claim-identity rule (decisions.md, 2026-08-10), that is a successor, not a revision.
3. **Retrain PrediCTP from its released recipe.** Same circularity as (2), plus the weak-model problem below.

None of these preserve the question. Hence PAUSE, not ADVANCE TO REVISION.

## 2. The weak-model problem: entry point 2 requires a model that performs well

The charter's entry point 2 starts "from a model that merely performs well." Dice 0.20 with lesion-wise F1 0.02 is not that. There is no evidence this model family found *any* signal worth decoding; auditing what a barely-functioning model attends to has little medical consequence either way. Two card scores fail on this alone:

- **medical_relevance 4** is unsupportable for the only concretely available raw-CTP architecture. A duration shortcut in a Dice-0.20 model threatens nobody's deployment.
- **negative_result_value 4 / "decisive"** inverts. On a weak model, a null ("predictions stable under censoring") has a dominant boring explanation — the model uses little of the temporal signal, or little of anything. That is a type-3 uninterpretable null, which caps negative_result_value at 2 under the rubric.

The card's positive-control gate (a temporal shift must move predictions) partially defends against this, and deserves credit — but if the positive control fails on the only available model, the study returns "not runnable," which is a feasibility note, not science.

## 3. The OOD-intervention residual (the idea-006 pattern), confirmed unresolvable today

The card honestly names its own kill condition: if padding/masking cannot be shown in-distribution, the use claim is invalid — precisely the pattern that paused idea 006 (patient-deletion OOD). The card gates on "an explicit mask if supported and concordance across three padding conventions." But concordance across padding conventions is a weak substitute for training-time support: three padding styles can agree because all three are equally OOD in the same direction (all shrink late-time information mass). The idea-006 resolution required inspecting the training loader; here there is no training loader to inspect because there is no released model. The keystone screen's `UNVERIFIABLE` verdict is right, and clause (b) — model semantics — is indeed the load-bearing one.

## 4. Prior-work overlap: the delta is real but currently unexercisable

- Kasasbeh et al. (PMID 25789631) and Copen et al. (PMID 25500309): truncation corrupts *derived perfusion estimates*. Verified characterizations in the card.
- Bathla et al. — verified for this critique: *Computed Tomography Perfusion–Based Prediction of Core Infarct and Tissue at Risk: Can Artificial Intelligence Help Reduce Radiation Exposure?*, Stroke, DOI 10.1161/STROKEAHA.121.034266. The card's characterization (feasibility under partial data, radiation-reduction framing) is fair, and its `why_not_done` claim — raw-CTP AI papers emphasize radiation reduction, not the boundary as a learned feature — is corroborated by this title.
- Additional neighbor the card missed: *Detecting CTP truncation artifacts in acute stroke imaging from the arterial input and the vascular output functions* (PLOS ONE 2023, DOI 10.1371/journal.pone.0283610) — machine-learned truncation *detection* from AIF/VOF features. It does not audit an outcome model's use of the boundary, so the delta stands, but it belongs in `novelty_neighbors`, and its feature set is a citable, annotation-free instrument for the card's X. This strengthens the X-measurement clause and the spin-off below.

The model-use-under-nested-censoring question remains genuinely unasked. The overlap objection is *not* fatal; the missing artifact is.

## 5. Secondary objections (would matter if the fatal one fell)

- **Duration census unverified.** Riedel et al. report 1 frame/s resampling but no per-case durations or completeness; the "≥30 cases with both curves within 10% of baseline" gate is pure assumption. If ISLES'24 protocols were uniformly ~50–70 s (typical clinical CTP), severely delayed tissue essentially *never* returns to baseline and the eligible-case count could be near zero — DATA_INSUFFICIENT, the idea-001 death. This is Stage-0-checkable only after registration.
- **Access.** Data is registration-gated, one ~99 GB archive. Lightweight, but the charter requires no dependence on unconfirmed gated data; access is unconfirmed. data_readiness 4 is a notch high; 3 is defensible.
- **Eligibility selection bias.** Cases whose curves fully return to baseline are, by the card's own suspected mechanism, the *less severely delayed* ones. The complete-case subset systematically excludes the severe strata where the censoring cue would matter most, shrinking both the effect and its generalizability. The card's risk-set framing acknowledges conditioning on completeness but not this consequence.
- **What the card does well, for the record:** honest rung 0 and `NOT_INSPECTED`; the interior-frame-masking and tail-extrapolation controls are a genuinely good identification design; and the censoring analogy passes the charter's "what would be different if the analogy were dropped" test on its own terms (nested prefixes, conditioning on complete scans, boundary-vs-missingness separation are all consequences of it). The grammar is sound. The world lacks the artifact.

## 6. dies_like_prior, corrected

The card names IDENTIFIABILITY_FAILURE and DATA_INSUFFICIENT as its risks. The actual death today is **DATA_ACCESS** — "required data, checkpoints, or mappings are not obtainable in practice" — the idea-003/idea-018 pattern: the design is coherent and the decisive asset (here, a frozen performant raw-CTP checkpoint) is not obtainable. The keystone screen half-saw this; this critique confirms it with the PrediCTP repository inspection.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does the ISLES'24 benchmark itself contain a censoring–severity confound — across the 149 released 4D CTP cases, does the terminal completeness index (last-frame residual enhancement, AIF/VOF truncation features) correlate with final-infarct volume and with center?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — same duration-shortcut threat, but it is a dataset property, not a model-use claim; it reaches no rung, landing instead on the charter's "identification of a decisive confound" success mode.
SHOULD IT BECOME A SEPARATE CANDIDATE? YES — different estimand, so the claim-identity rule requires a new registration with parent_ids: [idea-022].
IS IT ACTUALLY WORTH DOING? Yes, conditionally: it is deterministic curve arithmetic on already-released data, needs no model and no labels beyond the released fate masks, has citable instrumentation (PLOS ONE 10.1371/journal.pone.0283610), and a positive result warns every team training on this benchmark — but only if registration-gated access is confirmed and the completeness census is non-degenerate; if nearly all curves are truncated (or none are), it yields a two-line data note, so it should run as a bounded Stage-0-style audit, not a full candidate build-out.
```

Two things follow from that audit for free. First, it *is* the missing duration census: it converts idea-022's unverified completeness assumption into inspected fact, so the paused card's keystone clause (a) resolves as a by-product. Second, if the census shows a real censoring–severity correlation in the training data, the paused model-use question gains urgency (models are demonstrably *exposed* to the shortcut), giving a concrete reason to pursue the checkpoint through author correspondence rather than letting the pause rot.


===== ideas/022/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The original model-use question is presently untestable because no obtainable, performant frozen ISLES'24 final-infarct model consumes raw 4D CTP with documented training-supported prefix semantics.

**Argument:** The published ISLES'24 winner cannot be the study object: Ren et al. (arXiv:2505.18424v2, Table 1) report CTA, CBF, CBV, MTT, and Tmax inputs to the final nnU-Net, not raw CTP. The closest public raw-CTP system, Amador et al. (DOI 10.1007/978-3-031-81101-2_9; `kimberly-amador/ISLES24-PrediCTP`), releases code but no frozen checkpoint and reports Dice 0.20 and lesion-wise F1 0.02. Retraining that recipe is not a repair: it changes the original audit of a model that has already learned useful benchmark signal into a study of a model whose response to prefixes is partly installed by the experimenter's own padding, masking, or temporal-dropout choices. That is a different deliverable sentence under the claim-identity rule and would require a successor candidate. Without the frozen artifact, the nested-prefix design cannot distinguish learned use of terminal incompleteness from an out-of-distribution tensor convention, the same unresolved intervention-validity failure that paused idea 006.

**What would change my mind:** Produce an obtainable frozen raw-4D-CTP final-infarct checkpoint with non-trivial held-out performance, plus its actual training loader or methods showing that the proposed shorter-prefix mask/padding representation occurred during training; then the existing nested-prefix experiment could test the original claim without retraining or changing its identity.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The study object does not exist as an obtainable artifact — no frozen, performant ISLES'24 final-infarct model consumes raw 4D CTP with training-supported prefix semantics, and every substitute (audit the derived-map winner, retrain PrediCTP, train my own) either collapses the novelty delta into known truncation-propagation results or installs the very prefix semantics the experiment is supposed to measure, changing the deliverable sentence.

**Response:** CONCEDE

**Argument:** The objection is correct, and I verified it independently rather than taking it on trust before conceding. (1) The `kimberly-amador/ISLES24-PrediCTP` repository, inspected 2026-08-17, has an empty Releases section, no pretrained weights or download link anywhere in the README, and no mention of temporal padding, masking, or variable-length input handling — so even the weak candidate model fails both the frozen-artifact clause and the documented-prefix-semantics clause. (2) A sweep for any other obtainable raw-4D-CTP infarct checkpoint (Hugging Face, Zenodo, challenge releases) found none. The nearest lineage — Robben et al., Med Image Anal 2020 (native-CTP final-infarct prediction, arXiv:1812.02496) and the Amador spatio-temporal CNN line (DOI 10.1016/j.media.2022.102610) — trained on MR CLEAN and single-center cohorts with no released weights, and using a non-ISLES model would in any case change the deliverable sentence, which names an ISLES'24 benchmark model. (3) The retraining path fails the identity check exactly as the critic argues: whether short prefixes are in-distribution would be decided by my own augmentation choices, so the experiment would measure a property I installed. That is the idea-006 intervention-validity failure with the additional defect that here I would be the one who created the distribution. I have no amendment that preserves the question: the design's identifying power comes from auditing a model that already learned benchmark signal, and no such model is obtainable. PAUSE is the right disposition, with the critique's unblock condition standing (a released performant raw-CTP checkpoint with documented temporal-input semantics, via future challenge release or author correspondence with the PrediCTP group). The nested-prefix design itself is sound and should be reused verbatim on unpause, not redrafted.

**Spin-off (already recorded in critique.md, endorsed here, no new idea introduced):** the dataset-side censoring–severity audit — does terminal completeness correlate with infarct volume and center across the 149 released cases — is model-free, resolves keystone clause (a) as a by-product, and if positive gives a concrete reason to pursue the checkpoint through correspondence. It should register as a separate candidate with parent_ids [idea-022] under the claim-identity rule.

**Status:** CONCEDED


===== ideas/022/idea_card.json =====
{
  "id": "isles24-scout-001-w02",
  "track": "wide",
  "parent_ids": [],
  "search_mode": "B",
  "entry_point": 2,
  "design_template": "natural-paired",
  "title": "Does the model mistake the end of the scan for the end of the bolus?",
  "question": "Is an ISLES'24 raw-CTP final-infarct model using terminal-curve incompleteness as a severity cue, creating a hidden dependence on acquisition duration?",
  "outside_field": "Survival analysis and missing-data theory: a curve cut off by the scanner is right-censored, and the censoring boundary must not be mistaken for a biological event.",
  "rung": {
    "target": 1,
    "current": 0,
    "move_up": "Nested prefixes of the same complete acquisition can establish use of the censoring margin; cross-center duration replication would show a benchmark failure mode, not biological mechanism."
  },
  "deliverable_sentence": "The raw-CTP final-infarct model is using terminal-curve incompleteness\u2014the distance between residual contrast washout and the scan boundary\u2014as an image cue for tissue fate.",
  "X_measurement": {
    "X": "A terminal completeness index: the affected-tissue attenuation above prebolus baseline at the final frame, divided by peak enhancement, together with the terminal fitted washout slope and seconds from estimated 90% washout to scan end.",
    "how": "Estimate baseline and peak per voxel from raw CTP, compute the normalized last-frame residual and a robust slope over the final five available seconds, then summarize within the fixed threatened region and contralateral homolog. Record acquisition duration directly from the fourth dimension and sidecar timing when available.",
    "could_compute_today_without_asking_anyone": "Yes. It is deterministic curve arithmetic on the released 4D CTP and requires no annotation."
  },
  "suspected_signal": "Severely delayed tissue is most likely still enhanced when a short acquisition stops, so a network may learn the coincidence between lesion severity and the dataset-specific temporal boundary rather than a duration-invariant hemodynamic property.",
  "specific_artifact_confused_with_signal": "True slow washout, poor cardiac output, delayed collateral arrival, differing injection timing, and simple zero-padding can all resemble truncation.",
  "keystone_prerequisite": "A sufficient subset of ISLES'24 cases has complete long acquisitions that can be shortened to multiple still-clinically-plausible prefixes without changing sampling rate or preprocessing, and the frozen model accepts variable-length series or a masking scheme seen during training.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_residual_assumption": "Raw CTP release is verified, but the public paper does not establish per-case acquisition durations, curve completeness, padding semantics, or a model architecture that permits a clean prefix experiment.",
  "rung_reached": "No rung. An association between last-frame residual and infarct merely recapitulates delayed flow; model use requires a within-acquisition censoring intervention.",
  "dies_like_prior": "It differs from idea-016 because the claim is explicitly acquisition-boundary use, not physiology, and nested prefixes hold patient, injection, anatomy, and the observed early bolus fixed. It still dies by IDENTIFIABILITY_FAILURE if padding/masking artifacts cannot be separated from loss of late information, or by DATA_INSUFFICIENT if few curves are complete enough to censor.",
  "closest_prior_work": [
    {
      "citation": "Kasasbeh et al., Effect of extended CT perfusion acquisition time on ischemic core and penumbra volume estimation",
      "identifier": "PMID 25789631",
      "verified_fact": "In 36 patients, 48-second acquisitions truncated core curves in 67% of cases; extended acquisitions yielded smaller estimated cores and larger penumbras, with phantom confirmation.",
      "delta": "The study evaluated conventional estimates, not whether a neural final-infarct model uses the censoring boundary."
    },
    {
      "citation": "Copen et al., Exposing hidden truncation-related errors in acute stroke perfusion imaging",
      "identifier": "PMID 25500309",
      "verified_fact": "Progressive deletion of late frames from 110-second perfusion MRI caused substantial duration-dependent changes and lesion reversals in hemodynamic maps.",
      "delta": "It established truncation error in postprocessing, not a controlled neural-model reliance test on CT."
    },
    {
      "citation": "Bathla et al., AI prediction from complete and partial CTP",
      "identifier": "DOI 10.1161/STROKEAHA.121.034266; PMID 34670412",
      "verified_fact": "The study tested neural prediction using complete and partial CTP data.",
      "delta": "It addressed feasibility under partial data, not whether terminal incompleteness itself becomes a learned severity cue."
    }
  ],
  "novelty_neighbors": [
    {
      "work": "Kasasbeh et al. extended-acquisition truncation study",
      "identifier": "PMID 25789631"
    },
    {
      "work": "Copen et al. progressive truncation experiment",
      "identifier": "PMID 25500309"
    },
    {
      "work": "Bathla et al. partial-CTP neural prediction",
      "identifier": "DOI 10.1161/STROKEAHA.121.034266; PMID 34670412"
    }
  ],
  "novelty_delta": "Prior work shows that truncation changes perfusion estimates and that networks can consume partial series; the proposed audit asks whether a frozen outcome model treats the censoring margin itself as fate evidence under nested prefixes from the same scan.",
  "novelty_verdict": "NO_DUPLICATE_FOUND_LIMITED_SEARCH",
  "why_not_done": {
    "category": "BLIND_SPOT",
    "detail": "Acquisition-duration studies usually evaluate derived perfusion maps, while raw-CTP AI papers emphasize accuracy or radiation reduction; the scan boundary is rarely treated as a candidate learned feature."
  },
  "existing_assets": [
    "Public ISLES'24 raw 4D CTP and delayed DWI fate masks",
    "A within-acquisition nested-prefix design needing no new labels",
    "Published human and phantom evidence that truncation changes conventional perfusion estimates"
  ],
  "smallest_decisive_experiment": "Stage 0 audits all 149 time axes and identifies at least 30 cases whose contralateral and affected curves both return within 10% of baseline before scan end. For one frozen raw-CTP model, evaluate each complete case at the full duration and at three nested prefixes ending 5, 10, and 15 seconds earlier. Use two controls: censor then extrapolate the tail with a preregistered gamma-variate fit, and mask the same number of interior frames while retaining the true terminal frames. Primary readout is the within-voxel lesion-probability slope per second removed inside the threatened territory, stratified by whether the removed tail contains residual enhancement.",
  "compute_envelope": "One Colab GPU session: at most 40 cases, five variants per case, one frozen model, no retraining, under 6 GPU-hours and 16 GB VRAM.",
  "use_vs_association": "Use is supported only if nested censoring changes predictions more when it removes residual washout and the effect is rescued by plausible tail extrapolation but not reproduced by equal-count interior-frame masking.",
  "standing_confounds_addressed": {
    "site_vendor_protocol": "The paired prefix comparison fixes the acquired scan; duration distributions and effects are still reported separately by center.",
    "injection_and_cardiac_output": "All prefixes share the same injection and early arterial input; terminal residual is additionally normalized to peak.",
    "padding_artifact": "Identical tensor length and an explicit temporal mask are required; synthetic padding styles are crossed as a nuisance factor.",
    "disease_severity": "Patient and true trajectory are fixed within scan; the estimand is response to hiding late observations.",
    "annotation_provenance": "The primary paired score-change endpoint is label-free; existing masks are used for spatial summaries only."
  },
  "alternative_explanations": [
    {
      "alternative": "Any missing frames reduce useful information.",
      "resolution": "Equal-count interior-frame masking distinguishes generic missingness from terminal censoring."
    },
    {
      "alternative": "The network responds to zeros or repeated-frame padding.",
      "resolution": "Use an explicit mask if supported and require concordance across three padding conventions; otherwise the use claim is invalid."
    },
    {
      "alternative": "Late frames contain genuine physiology, so sensitivity is appropriate.",
      "resolution": "Tail extrapolation separates dependence on approximate washout information from dependence on the abrupt boundary; the claim remains about censoring, not that all late-frame use is bad."
    }
  ],
  "anticipated_negative": {
    "classification": "decisive",
    "reason": "If adequately complete scans, validated masks, and a positive-control temporal shift are present, stable predictions across clinically plausible censoring weaken dependence on the acquisition boundary."
  },
  "cross_domain": {
    "borrowed_construct": "Right censoring from survival analysis and missing-data theory.",
    "measurement_implied": "Residual event-process mass at the observation boundary and sensitivity across nested censoring times.",
    "if_analogy_dropped": "The experiment would merely ablate frames; censoring theory dictates nested prefixes, risk-set-style conditioning on complete scans, and explicit separation of boundary loss from generic missingness."
  },
  "remaining_legwork": "One day for time-axis and completeness auditing; two days to inspect candidate raw-CTP architectures for masking/padding behavior; no experiment is valid until both pass.",
  "scores": {
    "clarity": {
      "value": 5,
      "why": "The acquisition-boundary X and nested-prefix intervention are one-sentence precise."
    },
    "identifiability": {
      "value": 4,
      "why": "Same-scan prefixes, tail rescue, and interior-frame controls isolate censoring better than an observational duration comparison."
    },
    "medical_relevance": {
      "value": 4,
      "why": "A duration shortcut would threaten deployment across stroke centers and scanning protocols."
    },
    "interest": {
      "value": 5,
      "why": "A model reading when the scanner stopped as tissue fate is a surprising and actionable failure mode."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Human, phantom, and partial-series evidence already establish the technical risk."
    },
    "feasibility": {
      "value": 3,
      "why": "Capped because long complete cases and clean model masking semantics are uninspected."
    },
    "data_readiness": {
      "value": 4,
      "why": "Raw time series are released, though access is registration-bound and duration adequacy is unknown."
    },
    "evaluation_readiness": {
      "value": 4,
      "why": "Nested paired slopes, rescue, missing-frame controls, and official spatial metrics are defined."
    },
    "negative_result_value": {
      "value": 4,
      "why": "A powered gated null directly supports duration robustness over the tested range."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "The exact model-use delta survived a bounded primary-source search, not an exhaustive review."
    },
    "regret": {
      "value": 5,
      "why": "The audit is cheap and could expose a clinically consequential benchmark shortcut."
    }
  },
  "priority_score": 3.95,
  "priority_arithmetic": "0.20*3 + 0.15*4 + 0.15*4 + 0.10*4 + 0.10*5 + 0.10*5 + 0.10*4 + 0.05*4 + 0.05*3 = 3.95",
  "unverified_claims": [
    "At least 30 sufficiently complete public acquisitions",
    "Reliable time metadata after the released 1-Hz resampling",
    "A performant model with clean temporal masking or padding semantics",
    "Tail extrapolation can pass physiological plausibility gates",
    "No prior model-use audit treated truncation as a learned feature"
  ],
  "charter": "isles24"
}


===== ideas/022/keystone_screen.md =====
# Keystone screen

## Keystone as stated

> A sufficient subset of ISLES'24 cases has complete long acquisitions that can be shortened to multiple still-clinically-plausible prefixes without changing sampling rate or preprocessing, and the frozen model accepts variable-length series or a masking scheme seen during training.

This is a compound prerequisite. Both the acquisition-duration/completeness clause and the model-input/masking clause must hold.

## What I inspected

1. **The primary dataset paper (full methods).** Riedel et al., *Radiology: Artificial Intelligence*, DOI [10.1148/ryai.250603](https://pubs.rsna.org/doi/full/10.1148/ryai.250603), “Data Preprocessing,” states:

   > “Four-dimensional CT perfusion series underwent image co-registration and temporal resampling (1 frame/sec)”

   This verifies a released, uniformly resampled 4D series. It does **not** report the number of frames per patient, acquisition durations, return-to-baseline/completeness, or how many cases could support 5-, 10-, and 15-second clinically plausible prefixes. The same paper's “Data Repository and Storage” reports a public training set of 149, but cohort size is not evidence of temporal completeness.

2. **The official data repository at the current commit.** The ISLES'24 repository, [`README.md` lines 8–22 at commit 94b34863a099a8aeae6cf9b989c78ff2c767b80e](https://github.com/ezequieldlrosa/isles24/blob/94b34863a099a8aeae6cf9b989c78ff2c767b80e/README.md#L8-L22), says:

   > “You can access the ISLES'24 data after registration to the challenge.”

   and lists `sub-strokecase0001_ses-0001_ctp.nii.gz`. This verifies release structure, not header-level time-axis adequacy. I also inspected the repository tree: it provides the evaluation notebook and metrics, but no frozen raw-CTP model loader, checkpoint, temporal-mask contract, or training augmentation showing that missing/padded prefixes were in distribution.

3. **The published winning-model methods.** Ren et al., arXiv:2505.18424v2, Table 1 and its caption, [“Intensity Windowing”](https://arxiv.org/html/2505.18424v2#S3.SS3), identify the inputs to the final nnU-Net:

   > “Windowing ranges for each CT modality used as input to the nnU-Net segmentation model for the final submission to the ISLES’24 challenge.”

   The table enumerates **CTA, CBF, CBV, MTT, and Tmax**. It does not enumerate raw 4D CTP. Thus the only readily identifiable published frozen winner cannot establish the card's raw-series variable-length/masking clause; its perfusion inputs are derived 3D maps.

4. **The official Zenodo record.** [Zenodo concept DOI 10.5281/zenodo.16731717](https://zenodo.org/records/17652035), description/Data structure, says:

   > “Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

   The current archive is a single approximately 99-GB `train.7z`; its public record does not expose per-case NIfTI dimensions or curve-completeness summaries. Therefore the required subset count cannot be verified from the release schema alone.

## Residual assumption check

**Mandatory question:** “if this card only verified the nearest checkable thing, what is it still assuming?”

It verified the nearest facts—raw 4D CTP exists and was resampled to 1 frame/sec—but still assumes (a) enough individual curves extend beyond washout to support all proposed censoring points, and (b) an obtainable frozen **raw-CTP** model has a training-supported way to represent shorter prefixes without introducing an out-of-distribution padding or mask cue.

Clause (b) is the more load-bearing residual assumption. Even a favorable header census would not identify acquisition-boundary use if the intervention changes the model's tensor convention in a way absent from training. No model is named in the card, the official repository supplies no such model contract, and the published winner consumes derived maps rather than raw 4D curves. This is not evidence that no suitable model can be trained or exists; it means the stated keystone cannot presently be verified or falsified from the inspected primary artifacts. The proper screen outcome is therefore `UNVERIFIABLE`, not `KILL`.

```json
{"verdict": "UNVERIFIABLE", "evidence": "Windowing ranges for each CT modality used as input to the nnU-Net segmentation model for the final submission to the ISLES’24 challenge.", "source": "https://arxiv.org/html/2505.18424v2#S3.SS3, Table 1 caption; the table lists CTA, CBF, CBV, MTT, and Tmax, not raw 4D CTP", "note": "Raw 4D CTP release and 1-frame/sec resampling are verified, but neither sufficient complete long curves nor a frozen raw-CTP model with training-supported prefix masking/padding is verified."}
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
This is round 2. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The original model-use question is presently untestable because no obtainable, performant frozen ISLES'24 final-infarct model consumes raw 4D CTP with documented training-supported prefix semantics.

**Argument:** The published ISLES'24 winner cannot be the study object: Ren et al. (arXiv:2505.18424v2, Table 1) report CTA, CBF, CBV, MTT, and Tmax inputs to the final nnU-Net, not raw CTP. The closest public raw-CTP system, Amador et al. (DOI 10.1007/978-3-031-81101-2_9; `kimberly-amador/ISLES24-PrediCTP`), releases code but no frozen checkpoint and reports Dice 0.20 and lesion-wise F1 0.02. Retraining that recipe is not a repair: it changes the original audit of a model that has already learned useful benchmark signal into a study of a model whose response to prefixes is partly installed by the experimenter's own padding, masking, or temporal-dropout choices. That is a different deliverable sentence under the claim-identity rule and would require a successor candidate. Without the frozen artifact, the nested-prefix design cannot distinguish learned use of terminal incompleteness from an out-of-distribution tensor convention, the same unresolved intervention-validity failure that paused idea 006.

**What would change my mind:** Produce an obtainable frozen raw-4D-CTP final-infarct checkpoint with non-trivial held-out performance, plus its actual training loader or methods showing that the proposed shorter-prefix mask/padding representation occurred during training; then the existing nested-prefix experiment could test the original claim without retraining or changing its identity.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The study object does not exist as an obtainable artifact — no frozen, performant ISLES'24 final-infarct model consumes raw 4D CTP with training-supported prefix semantics, and every substitute (audit the derived-map winner, retrain PrediCTP, train my own) either collapses the novelty delta into known truncation-propagation results or installs the very prefix semantics the experiment is supposed to measure, changing the deliverable sentence.

**Response:** CONCEDE

**Argument:** The objection is correct, and I verified it independently rather than taking it on trust before conceding. (1) The `kimberly-amador/ISLES24-PrediCTP` repository, inspected 2026-08-17, has an empty Releases section, no pretrained weights or download link anywhere in the README, and no mention of temporal padding, masking, or variable-length input handling — so even the weak candidate model fails both the frozen-artifact clause and the documented-prefix-semantics clause. (2) A sweep for any other obtainable raw-4D-CTP infarct checkpoint (Hugging Face, Zenodo, challenge releases) found none. The nearest lineage — Robben et al., Med Image Anal 2020 (native-CTP final-infarct prediction, arXiv:1812.02496) and the Amador spatio-temporal CNN line (DOI 10.1016/j.media.2022.102610) — trained on MR CLEAN and single-center cohorts with no released weights, and using a non-ISLES model would in any case change the deliverable sentence, which names an ISLES'24 benchmark model. (3) The retraining path fails the identity check exactly as the critic argues: whether short prefixes are in-distribution would be decided by my own augmentation choices, so the experiment would measure a property I installed. That is the idea-006 intervention-validity failure with the additional defect that here I would be the one who created the distribution. I have no amendment that preserves the question: the design's identifying power comes from auditing a model that already learned benchmark signal, and no such model is obtainable. PAUSE is the right disposition, with the critique's unblock condition standing (a released performant raw-CTP checkpoint with documented temporal-input semantics, via future challenge release or author correspondence with the PrediCTP group). The nested-prefix design itself is sound and should be reused verbatim on unpause, not redrafted.

**Spin-off (already recorded in critique.md, endorsed here, no new idea introduced):** the dataset-side censoring–severity audit — does terminal completeness correlate with infarct volume and center across the 149 released cases — is model-free, resolves keystone clause (a) as a by-product, and if positive gives a concrete reason to pursue the checkpoint through correspondence. It should register as a separate candidate with parent_ids [idea-022] under the claim-identity rule.

**Status:** CONCEDED

