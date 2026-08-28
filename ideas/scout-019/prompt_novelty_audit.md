You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-019
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

## Personal references in generated artifacts

Refer to people by role, never by name: "the operator", "the
supervising PI", "the lab". Direction is stated as program fact ("the
current focus is X"), not narrated as personal suggestion. Formal
attribution lives in the README and future citation files, not in
working documents.


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

## 2026-08-17 - Ideas 021 and 023: human inspection questions answered

Idea 021 (contralateral ruler): the debate question - can any
non-reference mechanism produce increased affected-side deficit under
healthy-side up-scaling while passing all gates - is answered NO for
the card as revised. The revised design freezes normalization
constants from each unedited case and verifies bit-for-bit identity
of affected-side network inputs, which excludes the strongest
candidate (per-instance normalization coupling) by construction; the
mirror-over-global margin and the monotone SIGNED dose-response
discriminate against real cross-hemisphere physiology (collateral
supply predicts the opposite sign) and generic nonlocal mechanisms.
Independent review:
evidence/external_reviews/2026-08-17_normalization_construct_validity_brief.md.
Operator notes: edits are perfusion-map value edits, not raw-image
brightness; half-masking and mirror-symmetrization are rejected as
confirmatory arms on distribution-realism grounds, with
mirror-symmetrization recorded as a possible exploratory successor.
Conditions forwarded to feasibility: verify the target model
normalization implementation, that it consumes finished maps rather
than re-deriving from 4D source, and its receptive-field span.
Feasibility is authorized.

Idea 023 (CBV/MTT compensation state): the debate question - can an
outcome-derived change point operationalize the phrase autoregulatory
blood-volume reserve - is answered NO. The construct is defined by a
vasodilatory challenge; baseline maps cannot reveal remaining
dilation capacity (operator-confirmed understanding: a snapshot
cannot show how much further vessels can open); ISLES24 contains no
challenge data. Claim language is fixed as an outcome-associated
joint CBV/MTT decision boundary; the card disclaimer is ratified as
binding; physiological naming requires a successor with
challenge-based validation. Additional condition forwarded to
feasibility: the memo MUST include a prior-art section on map-editing
and counterfactual-perturbation mechanisms in medical imaging and a
concrete stay-in-distribution edit strategy with numbers; absence of
workable precedent is a legitimate feasibility kill. Feasibility is
authorized under the reduced claim.

## 2026-08-17 - Redaction-forward policy

Personal names are generalized to roles (the operator, the supervising
PI, the lab) in all live documents: charters, prompts, README, rules.
Historical entries and git history retain original wording by design;
the audit chain is anchored in commit and blob hashes that rewriting
would sever. Attribution lives in the README Acknowledgments and any
future citation file. Generated artifacts use role language per
COLLABORATOR_RULES. A test enforces the ban in live documents.

## 2026-08-18 - Cross-charter corruption: found, repaired, marked

External code review found that charter isolation held at generation
and broke downstream; sandbox verification confirmed every claim.
Damage and repair are documented in the P0-charter-integrity commit
and executed by scripts/repair_charter_promotions.py (append-only).
Standing consequences: ideas 020-025 carry an evaluation-contamination
marker (their critique, debate, and feasibility ran under the baseline
charter text); their verdicts remain of record but a bounded
cross-family reconciliation review is queued to check each verdict
against the isles24 charter before any contract is drafted. Idea-026
is REJECTED as a duplicate promotion of the killed idea-020; zero
stages were spent on it. The six baseline candidates falsely retired
are restored. ISLES promotion was frozen during the repair and is now
unfrozen. The scored digest is per-charter from this date; facts cross
charters only through the score-free index.

## 2026-08-18 - Correction: the v1 ledger repair failed; tombstones supersede it

The entry of earlier today stated the six baseline rows were restored.
That was false: the v1 repair script read the wrong timestamp field,
found no corruption boundary, and re-appended the corrupt state with a
note claiming restoration. External re-review caught it; direct
history inspection then established that none of the six rows existed
before 2026-08-17 at all (cycle 001 had six real candidates, cycle 002
four; three rows are phantoms outright, three reference old candidates
never tracked in the ledger). All six are now tombstoned (INVALID_ROW)
by scripts/repair_charter_ledger_v2.py and excluded from current state
by ledger.load() itself, with an explicit include_invalid escape hatch
for audit code. Lesson recorded: a repair script is claim-bearing code
and gets verified against artifacts like everything else; a spot-check
that rationalizes an expected-looking value is not verification.

## 2026-08-24 - Reconciliation ruling: idea 023

The reconcile stage (Claude family) audited all six 023 artifacts against
the archived prompt context versus the current isles24 charter. All rulings
STANDS; recommendation CLEAR-TO-CONTRACT. Operator ruling: ACCEPTED. Idea
023 is cleared for contract drafting (probe-plan). Reconciliation of the
remaining 020-025 ideas stays queued; the scoped-to-023 requirement before
any 023 contract is satisfied. Artifact: ideas/023/reconciliation.md.

## 2026-08-24 - Probe 023 review ruling (round 2: REVISE, three Phase-C blockers)

Operator ruling: Phase S execution AUTHORIZED with the current run.py -- the
reviewer confirms Phase S is contract-faithful and all blocking findings
(B1 lesion filename, B2 compute plan, B3 missing secondary metrics) are
confined to Phase C, which is already locked behind the contract amendment
and fresh approval. B1-B3, the NaN-background finiteness ambiguity, and the
NCCT-location correction MUST be resolved before the Phase-C approval is
granted. Review rounds preserved in git.

Design note: the one-revision cap on probe-build review is provisionally too
tight relative to debate max_rounds=3; queue a configurable
probe_review.max_revisions knob with an ambiguity-escalation rule. B1/B3 are
agent-resolvable and go back through probe-build at amendment time; B2 and
the finiteness ambiguity are operator decisions.

## 2026-08-24 - Contract 023 amendment (Phase S -> Phase C gates)

Phase S completed on Colab (bundle on results/probe-023-4a46713d1b81,
simulation sha256 59069fa9...): 52/60 candidates eligible; the frozen
lexicographic rule selected N=20 patients/stratum, M=100 voxels/cell,
maximum CI width 0.15. Amendment applied deterministically via the new
amend-contract subcommand; no agent involvement. Prior approval is stale
by design; fresh approval required after the finiteness and NCCT clause
edits below.

Design requirement (queued, 2b-adjacent): an operator interrogation channel.
At any point the operator can put a question or new information to the
system about a specific artifact (verdict, contract, probe code, debate
position) and receive a justification or proposed revision as a reviewable
artifact -- generalizing the reconcile stage shape. Must answer/propose,
never silently edit; human gate on any resulting change. 2b issue-based
gates are the natural transport.

Clause rulings at amendment (probe_review.md N2 + NCCT finding): (1) the
finiteness gate is scoped to analyzed voxels -- nonfinite values outside the
analysis region are permitted, excluded, and counted, harmonizing grid_gate
with the invalidating-failure class; (2) required_inputs now includes the
rawdata NCCT, which the official release tree places under rawdata only --
the feasibility memo claim of a "registered NCCT" in derivatives is
corrected forward here, not edited; (3) brain_and_mirror_gate references the
rawdata NCCT on the common grid. probe-build must state the exact
extraction set in the probe README.

## 2026-08-25 - External review round 4 intake + 023 Phase-C execution receipt

Round-4 repo audit (ChatGPT, deep-research; evidence/external_reviews/
2026-08-25_round4_repo_audit.pdf) registered. Adopted: amended freeze
(science frozen; deterministic transport/validator fixes permitted with
synthetic-fixture tests); contract-declared result interface replacing the
004-era validator ontology; completion single-sourced via bundle-complete;
launcher must satisfy probe-declared dependencies (--phase-s-dir guard);
per-phase output dirs; state.json as materialized view never authority;
receipts inside run_agent; fail-closed git sync; privilege separation before
autonomy; meta-loop emits schema-validated proposals only, zero write
credentials; EXPLANATION vs CHANGE_PROPOSAL interrogation receipts; category
budgets over daily caps; reseeding before quotas; validated-reviewer-yield
telemetry; generation backpressure; prospective-only third charter. Elo
deferral endorsed.

Execution receipt, 023 Phase C attempt 1 (2026-08-25T00:54Z): committed
launcher invoked run.py --phase C with data-dir/archive/record on Drive but
WITHOUT --phase-s-dir; approval gate PASSED on blob 349af5ad, then run.py
refused with exit 2 before touching any data. Partial bundle (Phase-S
outputs + Phase-C provenance carrying the exact argv) pushed to
results/probe-023-349af5ad0b3e as the honest record. Archive and extracted
subset persist on Drive; rerun re-pays digests and census only. Root cause:
generator omitted the round-3-added dependency; fixed generically this
commit.

## 2026-08-25 - Round-4 checkpoint evaluation: dispositions

Reviewer verdict: proceed to 2a; immediates correctly targeted; do not
redesign. Fixed this commit: librarian.yml fail-closed rescue (plus an
invariant test scanning every workflow for swallowed rebases); _digest_path
fail-local for named charters (global-digest leak class closed, matching the
portfolio-brief fix); author-family label stripped from probe_review with a
content-only instruction -- recorded as label blinding only, since two-family
structural opposition makes true author blinding impossible. Routed to 2a:
registry-declared upstream-bundle dependencies retire the launcher run.py
string inspection; probe-spec-declared terminal statuses retire the
POSITIVE/NEGATIVE_PATTERN literals in bundle_complete; execution receipts
move inside run_agent; state.json as materialized view + registry.yaml per
the round-4 schema.

## 2026-08-25 - 023 Phase C attempt 2: exit 5, archive census 0 cases -- root cause and directive

Execution receipt: take-2 run (with --phase-s-dir) passed the approval gate
on blob 349af5ad, verified the Phase-S hash, completed both archive digest
passes, then FAILED loudly at the census: run.py line 229 globs
sub-strokecase*_ses-*_space-ncct_cbf.nii* but the archive contains ZERO
strokecase members. Bundle with archive_manifest.csv (2983 members) pushed
at 2026-08-25T02:00:48Z.

Ground truth from the archive manifest itself, one full case:
  train/derivatives/sub-stroke0001/ses-01/perfusion-maps/sub-stroke0001_ses-01_space-ncct_cbf.nii.gz (+cbv, mtt, tmax)
  train/derivatives/sub-stroke0001/ses-02/sub-stroke0001_ses-02_space-ncct_lesion-msk.nii.gz
  train/raw_data/sub-stroke0001/ses-01/sub-stroke0001_ses-01_ncct.nii.gz
Counts: 149 cbf, 149 rawdata NCCT (cohort = 149, settled from the payload);
150 lesion-msk rows for 149 cases -- one extra/duplicate exists and must be
named, not silently absorbed.

Correction (forward, append-only): round-2 review finding B1 and the
operator both verified filenames against the Zenodo record DESCRIPTION
(sub-strokecaseNNNN..., rawdata/). The payload uses sub-strokeNNNN and
raw_data/. Lesson: the archive member manifest outranks dataset
documentation; filename claims verify against payload, never prose.

Directive for the probe-code revision: derive case discovery from observed
archive members (tolerate sub-stroke\d+ and sub-strokecase\d+; handle
raw_data and rawdata); surface the 150th lesion row explicitly in
schema_census.csv and route it through exclusions.csv with a reason; change
nothing else -- the contract, gates, thresholds, and analysis are untouched
and the standing approval remains valid.

## 2026-08-25 - 023 attempts 3-4: Drive FUSE mount crash + Zenodo version-drift hazard

Attempt-3 receipt (02:35Z bundle): the Colab Drive mount died mid-session
(Transport endpoint is not connected). Three symptoms, one cause: extraction
find limped; run.py correctly exit-3d on the invisible extracted dir; and
the staging pin cell, seeing RECORD_JSON as missing, silently re-resolved
the concept to a NEWER child record (17652035) published since our
download -- old bytes, new record, a checksum failure waiting to happen.
Lesson: a pin that can re-resolve at runtime is not a pin. Fixed in the
generator: --staging-record declares the immutable child at packaging time;
existing pins are never silently re-resolved; drift is healed toward the
declaration with a loud warning. Take 4 declares record 16813698 (md5
36ae28b9... matches the held archive); run.py checksum gate arbitrates
definitively.

## 2026-08-25 - 023 take 5: exit 5 (census 0) -- third Drive-FUSE casualty; local-SSD strategy adopted

Take-5 receipt: gate passed on 349af5ad, tolerant census still found 0 cases,
and the session transport never landed a bundle. Third failure localized to
the same component: the 894-file extracted tree on the Drive FUSE mount
(attempt-3 transport-endpoint death; take-5 zero-visibility; same-session
repo-dir loss). Ruling: heavy inputs localize to session SSD -- one bounded
FUSE read copies the archive local; extraction, digests, and census run on
local disk with a fail-loud extraction floor (>=800 files) so a broken tree
can never reach the census again. Outputs/checkpoints remain on Drive.
Driver polish: clone cell cds to /content before rm -rf (same-session rerun
cwd death).


===== evidence/ledger_digest_baseline.md =====
# Ledger digest -- charter: baseline (auto-generated; scores are scoped to this charter only)

101 tracked ideas in this charter. Latest state per idea; full history in ledger.jsonl.

Work under other charters: evidence/cross_charter_index.md (facts, no scores).

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **DATA_ACCESS** x2: Required data, checkpoints, or mappings are not obtainable in practice.
- **IDENTIFIABILITY_FAILURE** x2: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.
- **ANNOTATION_PROVENANCE** x1: Inference depends on who assigned labels / what they could see, and that is undocumented or contaminated.
- **CIRCULARITY** x1: The endpoint is a re-encoding of the input or of the thing being tested.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **scout-018-c04** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.6, audited 2026-08-20] -- The healed granulomas inside lung-cancer risk
- **scout-015-c04** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.5, audited 2026-08-17] -- The continuous air tunnel inside the hiatal-hernia score
- **scout-015-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.5, audited 2026-08-17] -- The lung-opacity score may be reading gravity
- **scout-013-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.4, audited 2026-08-15] -- Collateral failure written in the cortical veins
- **scout-012-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.2, audited 2026-08-15] -- The dilated esophagus inside the fibrosis score
- **scout-018-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.2, audited 2026-08-20] -- The dilated airways inside the fibrosis score
- **scout-013-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.1, audited 2026-08-15] -- The vessel map inside the mosaic-attenuation score
- **scout-016-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.0, audited 2026-08-18] -- Name the noise the kernel writes: the mediator behind idea 004's reconstruction shifts
- **scout-017-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.0, audited 2026-08-19] -- The plug inside the thickened-airway score
- **scout-017-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.0, audited 2026-08-19] -- The vascular street map inside lung-cancer risk
- ... and 59 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- regional-substitution: 14
- conditional-observational: 13
- counterfactual-synthesis: 10
- representation-erasure: 7
- longitudinal-within-subject: 7
- regional-removal: 5
- natural-paired: 3
- model-output-perturbation: 3
- cross-reconstruction: 2

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
- **scout-016-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Name the noise the kernel writes: the mediator behind idea 004's reconstruction shifts
- **scout-016-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The mortality model is wearing the patient's hardware
- **scout-016-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The fat inside the silhouette: epicardial adipose in the cardiomegaly score
- **scout-016-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The skeleton's tree rings: Harris lines inside the bone-age model
- **scout-016-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The cage remembers the hyperinflation: barrel chest inside the emphysema score
- **scout-017-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The crushed vertebra inside the mortality score
- **scout-017-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The plug inside the thickened-airway score
- **scout-017-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The detour veins inside the cirrhosis prediction
- **scout-017-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The spine's calendar inside chest-radiograph age
- **scout-017-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The vascular street map inside lung-cancer risk
- **scout-018-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Breast arterial calcification inside Mirai, re-entered on its own terms
- **scout-018-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The dilated airways inside the fibrosis score
- **scout-018-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The silhouette sign inside the consolidation score
- **scout-018-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The healed granulomas inside lung-cancer risk
- **scout-018-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The heart failure written on the body wall
- **scout-019-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Name the vessel-tree phenotype inside retinal sex prediction
- **scout-019-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The spleen as the fatty-liver model's calibration patch
- **scout-019-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The azygos vein inside the edema score
- **scout-019-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The meniscus inside the pleural-effusion score
- **scout-019-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The opening in the diaphragm inside the hiatal-hernia score


===== evidence/portfolio_brief_baseline.md =====
# Portfolio brief -- charter: baseline (auto-generated; run `python scout.py brief`)

Actionable ideas OF THIS CHARTER with debate verdicts (evaluative
framing never crosses charters; facts cross via
evidence/cross_charter_index.md). A revival/recombination
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



===== evidence/cross_charter_index.md =====
# Cross-charter index (facts only; scores are never comparable across charters)

- [baseline] **idea-001** [REJECTED] -- Have lung nodule concept models been validated against radiologist opinion rather than against disease?
- [baseline] **idea-002** [PAUSED] -- Dermoscopic concepts predicted from non-dermoscopic photographs: genuine visibility or shortcut?
- [baseline] **idea-003** [REJECTED] -- Does BI-RADS concept intervention survive realistic clinician behaviour, and does it beat simply reading the BI-RADS category?
- [baseline] **idea-004** [ACTIVE] -- The free test-retest experiment already inside CT-RATE: duplicate reconstructions of the same acquisition
- [baseline] **idea-005** [REJECTED] -- Eight named characteristics, or three latent ones? Discriminant validity of the LIDC concept vocabulary
- [baseline] **idea-006** [PAUSED] -- Ask the chest-CT foundation model to diagnose a volume with no patient in it
- [baseline] **idea-007** [ACTIVE] -- The same patient, twice, ten minutes apart, differing only in how much air is in the lungs
- [baseline] **idea-008** [ACTIVE] -- Two papers say Sybil's residual signal is the background, one of them names emphysema, and neither measured it
- [baseline] **idea-009** [REJECTED] -- Murray's cube law says how a branching tree should be built - ask whether the risk model is reading the lung's departure from it
- [baseline] **idea-010** [REJECTED] -- Cardiomegaly on a CT report is admitted gestalt - ask whether the model has quietly turned it into millilitres
- [baseline] **idea-011** [PAUSED] -- Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock
- [baseline] **idea-012** [PAUSED] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- [baseline] **idea-013** [SHORTLISTED] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- [baseline] **idea-014** [PAUSED] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- [baseline] **idea-015** [REJECTED] -- A breast-cancer risk model may be reading the arteries as a vascular clock
- [baseline] **idea-016** [REJECTED] -- The PE model may read contrast flowing backward as a pressure gauge
- [baseline] **idea-017** [SHORTLISTED] -- A lung-cancer model may be reading a mechanically remodeled trachea
- [baseline] **idea-018** [REJECTED] -- The brain-tumor prognosticator may be weighing the chewing muscle
- [baseline] **idea-019** [SHORTLISTED] -- The fibrosis model may be counting holes at the pleural edge
- [isles24] **idea-020** [REJECTED] -- A spreading front inside the perfusion deficit
- [isles24] **idea-021** [SHORTLISTED] -- The healthy hemisphere is the ruler
- [isles24] **idea-022** [PAUSED] -- Does the model mistake the end of the scan for the end of the bolus?
- [isles24] **idea-023** [SHORTLISTED] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
- [isles24] **idea-024** [REJECTED] -- The capillary traffic jam hidden behind the same mean transit time
- [isles24] **idea-025** [PAUSED] -- The scan is also an actigraph: the model may be reading how much the patient moved
- [isles24] **idea-026** [REJECTED] -- A spreading front inside the perfusion deficit
- [isles24] **idea-027** [REJECTED] -- When vanished sulci mean rescue, not death
- [isles24] **idea-028** [REJECTED] -- The blood's grayscale oxygen gauge
- [isles24] **idea-029** [REJECTED] -- The ground truth remembers the algorithm that drafted it
- [isles24] **idea-030** [REJECTED] -- The ground truth was drawn on a swollen brain
- [isles24] **idea-031** [REJECTED] -- The vascular detour the segmentation model can see
- [isles24] **idea-032** [REJECTED] -- The arterial network's spare route
- [isles24] **idea-033** [REJECTED] -- Did preprocessing teach the winner to read the disappearing insular ribbon?
- [isles24] **idea-034** [REJECTED] -- The edge of the map: the benchmark scores terra incognita
- [isles24] **idea-035** [REJECTED] -- The skull is a fixed-volume pressure vessel
- [isles24] **idea-036** [REJECTED] -- Does the model bring a vascular map to the scan?
- [isles24] **idea-037** [REJECTED] -- The scan remembers which hospital took it
- [isles24] **idea-038** [REJECTED] -- Does the model price the last mile of blood delivery?
- [isles24] **idea-039** [SHORTLISTED] -- Does the model trust tissue that obeys the flow equation?
- [isles24] **idea-040** [PAUSED] -- The pressure history written in a winding artery
- [isles24] **idea-041** [SHORTLISTED] -- The roughness of a heartbeat through starved tissue
- [isles24] **idea-042** [SHORTLISTED] -- Delay is not dispersion
- [isles24] **idea-043** [REJECTED] -- What the winner's brain window revealed
- [isles24] **idea-044** [REJECTED] -- The old stroke inside the new forecast
- [isles24] **isles24-scout-001-c01** [SCOUT_ONLY] -- Does the winning model rediscover the collateral clock?
- [isles24] **isles24-scout-001-c02** [SHORTLISTED] -- The vascular detour the segmentation model can see
- [isles24] **isles24-scout-001-c03** [SCOUT_ONLY] -- Read the stroke from the blood leaving, not only entering
- [isles24] **isles24-scout-001-c04** [SCOUT_ONLY] -- The frail brain around the threatened territory
- [isles24] **isles24-scout-001-c05** [SHORTLISTED] -- A spreading front inside the perfusion deficit
- [isles24] **isles24-scout-001-c06** [SHORTLISTED] -- The capillary traffic jam hidden behind the same mean transit time
- [isles24] **isles24-scout-001-c07** [SHORTLISTED] -- Does the model mistake the end of the scan for the end of the bolus?
- [isles24] **isles24-scout-001-c08** [SCOUT_ONLY] -- The deconvolution algorithm may have signed the image
- [isles24] **isles24-scout-002-c01** [SCOUT_ONLY] -- The water already in the tissue: does the model read the edema clock?
- [isles24] **isles24-scout-002-c02** [SHORTLISTED] -- The healthy hemisphere is the ruler
- [isles24] **isles24-scout-002-c03** [SCOUT_ONLY] -- Two tissues, two death thresholds
- [isles24] **isles24-scout-002-c04** [SCOUT_ONLY] -- The barrier is already leaking
- [isles24] **isles24-scout-002-c05** [SCOUT_ONLY] -- The clot that lets contrast through
- [isles24] **isles24-scout-002-c06** [SHORTLISTED] -- The scan is also an actigraph: the model may be reading how much the patient moved
- [isles24] **isles24-scout-002-c07** [SHORTLISTED] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
- [isles24] **isles24-scout-002-c08** [SCOUT_ONLY] -- Has the deficit percolated? Volume is what the metric sees; connectivity may be what the model uses
- [isles24] **isles24-scout-003-c01** [SHORTLISTED] -- Did preprocessing teach the winner to read the disappearing insular ribbon?
- [isles24] **isles24-scout-003-c02** [SCOUT_ONLY] -- How much artery did the clot occupy?
- [isles24] **isles24-scout-003-c03** [SHORTLISTED] -- The arterial network's spare route
- [isles24] **isles24-scout-003-c04** [SHORTLISTED] -- The blood's grayscale oxygen gauge
- [isles24] **isles24-scout-003-c05** [SHORTLISTED] -- When vanished sulci mean rescue, not death
- [isles24] **isles24-scout-003-c06** [SCOUT_ONLY] -- The bolus spreads like dye in a river
- [isles24] **isles24-scout-003-c07** [SHORTLISTED] -- Does the model price the last mile of blood delivery?
- [isles24] **isles24-scout-003-c08** [SHORTLISTED] -- The skull is a fixed-volume pressure vessel
- [isles24] **isles24-scout-004-c01** [SHORTLISTED] -- The ground truth remembers the algorithm that drafted it
- [isles24] **isles24-scout-004-c02** [SHORTLISTED] -- Does the model bring a vascular map to the scan?
- [isles24] **isles24-scout-004-c03** [SCOUT_ONLY] -- The heart's signature in the head scan
- [isles24] **isles24-scout-004-c04** [SCOUT_ONLY] -- The model may be watching the patient's eyes
- [isles24] **isles24-scout-004-c05** [SCOUT_ONLY] -- The brain's odometer: calcification as the model's age gauge
- [isles24] **isles24-scout-004-c06** [SHORTLISTED] -- The scan remembers which hospital took it
- [isles24] **isles24-scout-004-c07** [SHORTLISTED] -- The edge of the map: the benchmark scores terra incognita
- [isles24] **isles24-scout-004-c08** [SHORTLISTED] -- The ground truth was drawn on a swollen brain
- [isles24] **isles24-scout-005-c01** [SHORTLISTED] -- What the winner's brain window revealed
- [isles24] **isles24-scout-005-c02** [SHORTLISTED] -- The old stroke inside the new forecast
- [isles24] **isles24-scout-005-c03** [SCOUT_ONLY] -- The bottleneck before the brain
- [isles24] **isles24-scout-005-c04** [SHORTLISTED] -- The pressure history written in a winding artery
- [isles24] **isles24-scout-005-c05** [SCOUT_ONLY] -- Do sulci pin the predicted infarct edge?
- [isles24] **isles24-scout-005-c06** [SHORTLISTED] -- Does the model trust tissue that obeys the flow equation?
- [isles24] **isles24-scout-005-c07** [SHORTLISTED] -- The roughness of a heartbeat through starved tissue
- [isles24] **isles24-scout-005-c08** [SHORTLISTED] -- Delay is not dispersion
- [baseline] **scout-006-c01** [SHORTLISTED] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- [baseline] **scout-006-c02** [SHORTLISTED] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- [baseline] **scout-006-c03** [SCOUT_ONLY] -- An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver
- [baseline] **scout-006-c04** [SCOUT_ONLY] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- [baseline] **scout-006-c05** [SCOUT_ONLY] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two
- [baseline] **scout-007-c01** [SHORTLISTED] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- [baseline] **scout-007-c02** [SHORTLISTED] -- A breast-cancer risk model may be reading the arteries as a vascular clock
- [baseline] **scout-007-c03** [SCOUT_ONLY] -- Merlin may be reading fatty kidney rather than kidney shape
- [baseline] **scout-007-c04** [SHORTLISTED] -- The PE model may read contrast flowing backward as a pressure gauge
- [baseline] **scout-007-c05** [SHORTLISTED] -- A lung-cancer model may be reading a mechanically remodeled trachea
- [baseline] **scout-007-c06** [SCOUT_ONLY] -- The effusion model may be reading whether pleural fluid still obeys gravity
- [baseline] **scout-007-c07** [SHORTLISTED] -- The fibrosis model may be counting holes at the pleural edge
- [baseline] **scout-007-c08** [SCOUT_ONLY] -- The PE model may be reading how completely blood and contrast have mixed
- [baseline] **scout-007-c09** [REJECTED] -- 
- [baseline] **scout-007-c10** [REJECTED] -- 
- [baseline] **scout-007-c11** [REJECTED] -- 
- [baseline] **scout-007-c12** [REJECTED] -- 
- [baseline] **scout-007-c13** [REJECTED] -- 
- [baseline] **scout-008-c01** [SCOUT_ONLY] -- The cirrhosis model may be reading the bumpiness of the liver's edge
- [baseline] **scout-008-c02** [SCOUT_ONLY] -- The chest-CT model may see the heart by watching the airway splay
- [baseline] **scout-008-c03** [SCOUT_ONLY] -- The model that 'predicts a blood count' may just be reading how bright the blood is
- [baseline] **scout-008-c04** [SCOUT_ONLY] -- The emphysema call may read the shape of the holes, not just how many
- [baseline] **scout-008-c05** [SCOUT_ONLY] -- The lung-cancer model may read the aorta as an ageing clock
- [baseline] **scout-009-c01** [SCOUT_ONLY] -- The CT spirometer may be measuring remodeled airway walls
- [baseline] **scout-009-c02** [SCOUT_ONLY] -- The kidney model may be reading fat packed into the renal sinus
- [baseline] **scout-009-c03** [SHORTLISTED] -- The brain-tumor prognosticator may be weighing the chewing muscle
- [baseline] **scout-009-c04** [SCOUT_ONLY] -- The risk model may be reading the breast's lines of force
- [baseline] **scout-009-c05** [SCOUT_ONLY] -- The lung-cancer model may be reading the marrow as a smoking dosimeter
- [baseline] **scout-009-c06** [SCOUT_ONLY] -- The CT spirometer may be reading the diaphragm as a pressure-loaded membrane
- [baseline] **scout-009-c07** [SCOUT_ONLY] -- Mirai may be detecting broken bilateral symmetry before a lesion exists
- [baseline] **scout-009-c08** [SCOUT_ONLY] -- The glioblastoma prognosticator may be reading the invasion front's roughness
- [baseline] **scout-009-c09** [SCOUT_ONLY] -- The arterial-calcification score may be reading inspiratory depth
- [baseline] **scout-010-c01** [SCOUT_ONLY] -- CXR-Age put back together from parts a radiologist can measure
- [baseline] **scout-010-c02** [SCOUT_ONLY] -- Atelectasis vs consolidation: has CT-CLIP learned the radiologist's volume-loss rule?
- [baseline] **scout-010-c03** [SCOUT_ONLY] -- Merlin's cirrhosis signal may be the spleen
- [baseline] **scout-010-c04** [SCOUT_ONLY] -- The inferior vena cava as a manometer: does the chest model read venous pressure?
- [baseline] **scout-010-c05** [SCOUT_ONLY] -- Aortic tortuosity as a buckled column: is the hypertension head reading exceeded critical pressure?
- [baseline] **scout-011-c01** [SCOUT_ONLY] -- Name the bone phenotype hidden in a near-perfect hand-radiograph sex classifier
- [baseline] **scout-011-c02** [SCOUT_ONLY] -- Does Merlin read renal atrophy when it predicts future CKD?
- [baseline] **scout-011-c03** [SCOUT_ONLY] -- Cephalization in 3D: decode CT-CLIP's pulmonary-edema score
- [baseline] **scout-011-c04** [SCOUT_ONLY] -- The air bronchogram as a topological cue
- [baseline] **scout-011-c05** [SCOUT_ONLY] -- A pancreatic fat gauge inside Merlin's diabetes forecast
- [baseline] **scout-012-c01** [SCOUT_ONLY] -- The race signal in chest CT: measure the bone density everyone names and nobody measured
- [baseline] **scout-012-c02** [SCOUT_ONLY] -- The dilated esophagus inside the fibrosis score
- [baseline] **scout-012-c03** [SCOUT_ONLY] -- Merlin's COPD call may come from the lungs it wasn't asked to look at
- [baseline] **scout-012-c04** [SCOUT_ONLY] -- The non-gated chest CT contains an ECG: heart rate written in motion banding
- [baseline] **scout-012-c05** [SCOUT_ONLY] -- The prognosis model as a manometer: midline shift is pressure the skull wrote down
- [baseline] **scout-013-c01** [SCOUT_ONLY] -- The vessel map inside the mosaic-attenuation score
- [baseline] **scout-013-c02** [SCOUT_ONLY] -- The open fissure inside lung-cancer risk
- [baseline] **scout-013-c03** [SCOUT_ONLY] -- Name the skeletal frailty inside mortality prediction
- [baseline] **scout-013-c04** [SCOUT_ONLY] -- The renal artery as a buckled pressure line
- [baseline] **scout-013-c05** [SCOUT_ONLY] -- Collateral failure written in the cortical veins
- [baseline] **scout-014-c01** [SCOUT_ONLY] -- The fat around the heart inside the CVD-mortality score: finish the observation Chao et al. started
- [baseline] **scout-014-c02** [SCOUT_ONLY] -- Redraw the same airway walls with a sharper pencil: does the peribronchial-thickening score follow Pi10?
- [baseline] **scout-014-c03** [SCOUT_ONLY] -- The cardiomegaly head may be reading the rib cage: Haller index beyond heart volume
- [baseline] **scout-014-c04** [SCOUT_ONLY] -- Sybil was never given the patient's age; the thymus wrote it down anyway
- [baseline] **scout-014-c05** [SCOUT_ONLY] -- Chronic anemia turns the marrow back on: is Merlin reading red marrow, not just pale blood?
- [baseline] **scout-015-c01** [SCOUT_ONLY] -- Measure the fluid behind the pleural-effusion score
- [baseline] **scout-015-c02** [SCOUT_ONLY] -- The missing branches inside Sybil's risk score
- [baseline] **scout-015-c03** [SCOUT_ONLY] -- The portal vein as the cirrhosis model's pressure gauge
- [baseline] **scout-015-c04** [SCOUT_ONLY] -- The continuous air tunnel inside the hiatal-hernia score
- [baseline] **scout-015-c05** [SCOUT_ONLY] -- The lung-opacity score may be reading gravity
- [baseline] **scout-016-c01** [SCOUT_ONLY] -- Name the noise the kernel writes: the mediator behind idea 004's reconstruction shifts
- [baseline] **scout-016-c02** [SCOUT_ONLY] -- The mortality model is wearing the patient's hardware
- [baseline] **scout-016-c03** [SCOUT_ONLY] -- The fat inside the silhouette: epicardial adipose in the cardiomegaly score
- [baseline] **scout-016-c04** [SCOUT_ONLY] -- The skeleton's tree rings: Harris lines inside the bone-age model
- [baseline] **scout-016-c05** [SCOUT_ONLY] -- The cage remembers the hyperinflation: barrel chest inside the emphysema score
- [baseline] **scout-017-c01** [SCOUT_ONLY] -- The crushed vertebra inside the mortality score
- [baseline] **scout-017-c02** [SCOUT_ONLY] -- The plug inside the thickened-airway score
- [baseline] **scout-017-c03** [SCOUT_ONLY] -- The detour veins inside the cirrhosis prediction
- [baseline] **scout-017-c04** [SCOUT_ONLY] -- The spine's calendar inside chest-radiograph age
- [baseline] **scout-017-c05** [SCOUT_ONLY] -- The vascular street map inside lung-cancer risk
- [baseline] **scout-018-c01** [SCOUT_ONLY] -- Breast arterial calcification inside Mirai, re-entered on its own terms
- [baseline] **scout-018-c02** [SCOUT_ONLY] -- The dilated airways inside the fibrosis score
- [baseline] **scout-018-c03** [SCOUT_ONLY] -- The silhouette sign inside the consolidation score
- [baseline] **scout-018-c04** [SCOUT_ONLY] -- The healed granulomas inside lung-cancer risk
- [baseline] **scout-018-c05** [SCOUT_ONLY] -- The heart failure written on the body wall
- [baseline] **scout-019-c01** [SCOUT_ONLY] -- Name the vessel-tree phenotype inside retinal sex prediction
- [baseline] **scout-019-c02** [SCOUT_ONLY] -- The spleen as the fatty-liver model's calibration patch
- [baseline] **scout-019-c03** [SCOUT_ONLY] -- The azygos vein inside the edema score
- [baseline] **scout-019-c04** [SCOUT_ONLY] -- The meniscus inside the pleural-effusion score
- [baseline] **scout-019-c05** [SCOUT_ONLY] -- The opening in the diaphragm inside the hiatal-hernia score


===== evidence/librarian_proposals.md =====


===== ideas/scout-019/README.md =====
# Scouting cycle 019

Tracks: baseline


===== ideas/scout-019/candidates_all.json =====
{
  "cycle": 19,
  "charter": null,
  "tracks": [
    "baseline"
  ],
  "notes": {},
  "candidates": [
    {
      "id": "scout-019-c01",
      "search_mode": "A",
      "entry_point": 1,
      "title": "Name the vessel-tree phenotype inside retinal sex prediction",
      "question": "Is a fundus-photograph sex classifier using the richness of the retinal vessel tree?",
      "deliverable_sentence": "The fundus sex classifier is using retinal vessel-tree richness.",
      "rung": "Targets rung 1 through structure-selective erasure; rung 2 requires camera- and pigmentation-stratified replication; rung 3 is available because vessel-tree richness is a named graph phenotype, but biological interpretation beyond that needs independent validation.",
      "rung_reached": "Rung 1 if selectively removing distal branches changes the frozen classifier beyond vessel-area-matched shams; rung 3 requires the result to replicate with independent vessel segmenters and cameras.",
      "unfinished_story": "Poplin et al. showed that fundus photographs predict sex at high accuracy and localized evidence broadly to retinal regions, while later work measured sex differences in vessel branches, nodes, length, caliber, tortuosity, and retinal regions. The missing experiment is whether a frozen high-performing classifier actually uses the measured branch-richness phenotype rather than merely coexisting with it.",
      "X_measurement": "Segment arteries and veins with a published fundus-vessel network, skeletonize the binary vessel mask, and compute branch-point count, terminal count, total skeleton length, and vessel-covered area within a fixed disc-centered field. The primary X is residual branch count after matching total vessel area and image field. Primary sources: Delavari et al., arXiv:2301.06675; macular geometry study PMID 34977079. Compute-today test: YES; it is deterministic after automated segmentation and requires no reader.",
      "suspected_signal": "Sex-associated developmental and vascular differences alter how many visible retinal branches and nodes occupy a standardized fundus field. Fine dark branches create a repeated local texture a convolutional classifier can aggregate even when no human recognizes the global phenotype.",
      "use_vs_association": "Measured sex differences alone show association; the confirmatory test erases distal vessel branches while holding field, background, and total removed pixel area fixed, then compares the paired sex-logit change with vessel-area-matched proximal-segment and non-vessel shams.",
      "keystone_prerequisite": "A frozen, obtainable fundus sex classifier retains its published discrimination on an obtainable image corpus and automated vessel masks remain accurate enough that distal-branch erasure can vary branch count without changing total vessel area or the optic-disc/macular background beyond prespecified tolerances.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearest verified facts are that sex prediction is strong and vessel geometry differs by sex. I am still assuming the load-bearing fact that branch count can be manipulated independently of vessel area and local inpainting signature in the exact classifier input; that is the real keystone and is not established by either paper.",
      "dies_like_prior": "It risks idea-009's IDENTIFIABILITY_FAILURE if branch richness cannot be separated from vessel area, caliber, pigmentation, and camera field. Unlike idea-009, the proposed intervention explicitly matches vessel area and includes proximal-vessel and non-vessel shams. Annotation provenance does not apply: sex is registry-derived and the primary readout is model-to-itself.",
      "closest_prior_work": "Poplin et al., Nature Biomedical Engineering 2018, DOI 10.1038/s41551-018-0195-0, established retinal sex prediction but did not name a causal image quantity. Korot et al., DOI 10.1038/s41598-021-89743-x, found poorer performance with foveal pathology. Delavari et al., arXiv:2301.06675, measured greater branch/node richness in male images but did not intervene on a frozen classifier. A 2026 region-weight study, DOI 10.1038/s41598-026-53485-5, estimates macula/disc/vasculature contributions but not use of branch richness. Exact delta: matched, branch-selective erasure on the original task.",
      "existing_assets": "Public fundus datasets with sex metadata, published vessel segmenters, deterministic graph measurements, and several reproducible sex-classification architectures; all fit one GPU.",
      "smallest_decisive_experiment": "Stage 0 reproduces a frozen classifier on a subject-held-out set and validates vessel masks without using the test set. On 300 correctly classified test images, remove terminal vessel segments in graded doses, inpaint from immediately adjacent retina, and compare sex-logit dose response against equal-area proximal-vessel removal and non-vessel curvilinear shams. Freeze all dose bins and masks before test inference.",
      "standing_confounds_addressed": "Within-image comparisons fix camera, site, field, pigmentation, age, disease prevalence, and referral pathway. Camera/vendor and ethnicity are further stratified in replication. The design does not fully rule out branch-dependent inpainting detectability; sham detectability and a held-out edit discriminator gate it. Scanner/protocol/reconstruction are not CT-relevant here. Label leakage is unlikely but corpus filenames and borders must be audited.",
      "alternative_explanations": [
        "The model uses total vessel area, not branch richness; area-matched branch versus proximal-segment edits distinguish them.",
        "The model reacts to many small inpaint patches; equal-count non-vessel curvilinear shams test this.",
        "Camera sharpening reveals more branches and also predicts sex through site imbalance; within-image editing plus camera-stratified replication excludes the primary version."
      ],
      "anticipated_negative": "Decisive if classifier reproduction, segmentation, independent manipulation, and edit-realism gates pass and branch erasure is no larger than matched shams. Otherwise it is a feasibility failure, not a biological null.",
      "cross_domain": {
        "borrowed_construct": "Graph theory: a vascular tree summarized by nodes, terminals, and total edge length.",
        "implied_measurement": "Residual branch/node count at fixed vessel area and field.",
        "what_changes_if_dropped": "Without graph language, the experiment loses its prespecified distinction between branching richness and simple vessel area; it would become generic vessel masking and could not support the deliverable sentence."
      },
      "remaining_legwork": "Two days to select and reproduce a model, three days for segmenter and edit gates, and about one week to first frozen test result.",
      "design_template": "representation-erasure",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "One measurable graph phenotype and one matched intervention."
        },
        "identifiability": {
          "value": 4,
          "why": "Area matching and two sham families isolate richness, subject to edit realism."
        },
        "medical_relevance": {
          "value": 3,
          "why": "It could reveal a real retinal sex phenotype, but the sex-prediction task itself has limited direct utility."
        },
        "interest": {
          "value": 5,
          "why": "It closes a canonical model-beats-human mystery with a concrete anatomical quantity."
        },
        "prior_legwork": {
          "value": 4,
          "why": "The prediction gap and the candidate vessel phenotype are both already published."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped because the independent-editability keystone is not inspected."
        },
        "data_readiness": {
          "value": 4,
          "why": "Public images, labels, and segmentation methods exist, though the exact frozen pairing is not selected."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "Paired logits and dose response have clear sham baselines."
        },
        "negative_result_value": {
          "value": 4,
          "why": "A gated null directly rejects a published candidate explanation."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped; a 2026 region-contribution paper makes a dedicated audit essential."
        },
        "regret": {
          "value": 5,
          "why": "The phenotype and canonical mystery are already adjacent in the literature."
        }
      },
      "priority_score": 3.8,
      "unverified_claims": [
        "An obtainable frozen classifier exactly reproduces published performance",
        "Branch count can be edited independently at classifier resolution",
        "No prior branch-selective causal intervention exists"
      ],
      "plain_pitch": "Artificial intelligence can tell a person's sex from a retinal photograph even though eye specialists cannot explain how. Men and women may differ slightly in how richly the tiny retinal vessels branch. This study removes only the finest branches while carefully matching the amount of vessel erased elsewhere. If the prediction changes specifically with branch loss, the model has exposed a measurable anatomical difference rather than an unnamed visual clue.",
      "track": "baseline",
      "charter": null
    },
    {
      "id": "scout-019-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The spleen as the fatty-liver model's calibration patch",
      "question": "Is Merlin's hepatic-steatosis score using the spleen as an internal attenuation reference?",
      "deliverable_sentence": "Merlin's hepatic-steatosis score is using splenic attenuation as an internal reference for liver attenuation.",
      "rung": "Targets rung 1 by changing spleen attenuation while holding liver voxels fixed; rung 2 requires contrast-phase and protocol controls; rung 3 follows if the score implements the named liver-minus-spleen comparison used in radiology.",
      "rung_reached": "Rung 1 if the steatosis score follows controlled spleen-only attenuation shifts with the sign predicted by the liver-spleen difference; replication on noncontrast scans and multiple sites would move it toward rung 3.",
      "unasked_question": "Quantitative radiology often judges hepatic fat relative to the spleen, and automated liver/spleen measurement is mature. Merlin was trained without an explicit rule, so it is unknown whether the foundation model independently learned the spleen as a calibration reference.",
      "X_measurement": "Use TotalSegmentator to segment liver and spleen, erode masks from vessels and boundaries, and compute mean liver minus mean spleen attenuation in Hounsfield units and the liver/spleen ratio. Primary validation: Park et al., Radiology 2011, DOI 10.1148/radiol.10101233 (biopsy-proven nonsteatotic reference range); automated contrast-enhanced measurement PMID 40095018. Compute-today test: YES on any CT with both organs in view.",
      "suspected_signal": "The spleen provides an internal tissue reference that cancels some patient- and acquisition-level intensity variation. A vision-language model trained from reports may discover that a dark liver is more meaningful when the spleen remains bright.",
      "use_vs_association": "Observational correlation between score and liver-spleen difference cannot show which organ the model reads. The experiment shifts only splenic voxels within the observed physiological distribution while keeping the liver and every other voxel bit-identical, then tests the predicted monotone score response.",
      "keystone_prerequisite": "The released Merlin checkpoint exposes a hepatic-steatosis or fatty-liver score on an obtainable cohort containing enough noncontrast or phase-homogeneous scans with both liver and spleen fully represented after the exact preprocessing.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The primary paper verifies released models/data and 30 zero-shot findings, and the liver-spleen measurement itself is validated. I have not inspected the released finding vocabulary or input manifests for the exact steatosis head and phase-homogeneous support. That exact model-output-and-cohort pairing, not merely Merlin's existence, is the keystone.",
      "dies_like_prior": "It resembles idea-010's CIRCULARITY risk because the proposed X is a standard diagnostic rule. It differs because the question is not whether X predicts the steatosis label; it intervenes on the reference organ while liver appearance is fixed, testing whether this particular model uses the comparison. Annotation provenance is absent from the primary paired readout.",
      "closest_prior_work": "Merlin, Blankemeier et al., Nature 2026, PMID 41781626, releases models and evaluates 30 findings but does not report a spleen-reference intervention. Park et al., DOI 10.1148/radiol.10101233, validates the liver-spleen difference against biopsy but studies the biomarker, not model behavior. The exact delta is spleen-only perturbation of a frozen whole-volume model.",
      "existing_assets": "Released Merlin code/models and dataset; TotalSegmentator liver and spleen masks; accepted attenuation formulas; single-GPU inference.",
      "smallest_decisive_experiment": "Stage 0 inspects Merlin's actual finding vocabulary, preprocessing, scan phases, and organ coverage. If it passes, select 200 test scans across the liver-spleen difference range. Apply graded spleen-only shifts of -15 to +15 HU, excluding vessels and lesions; use same-volume liver shifts as a positive control and kidney-cortex shifts matched for volume and baseline attenuation as a specificity sham. Primary endpoint: sign and slope of paired steatosis-logit change.",
      "standing_confounds_addressed": "Within-image editing fixes scanner, vendor, protocol, reconstruction, site, positioning, habitus, prevalence, referral pathway, and label leakage. Phase is fixed by cohort restriction. It does not automatically rule out generic response to any large-organ intensity shift; kidney shams do. Contrast timing limits generalization beyond the selected phase.",
      "alternative_explanations": [
        "The model responds to any organ-wide intensity shift; kidney-cortex shams test specificity.",
        "The model uses absolute liver attenuation only; a flat spleen arm with a responsive liver positive control supports that alternative.",
        "Spleen edits are out of distribution; bounded native-intensity substitution and a held-out edit discriminator gate this."
      ],
      "anticipated_negative": "Decisive after a responsive liver positive control and passed realism gate: Merlin does not use the spleen reference on this cohort. Without the positive control, a null is sensitivity-limited.",
      "remaining_legwork": "One day to inspect the released label vocabulary and preprocessing, two days for phase/coverage census, and one week for masks, controls, and first result.",
      "design_template": "regional-substitution",
      "entry_point_2_requirements": "Measurement: eroded-mask liver-minus-spleen attenuation and ratio. Confusable artifacts: contrast phase, global calibration drift, and generic organ-intensity edits; phase restriction and kidney shams address them.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "The reference organ, direction, and control are explicit."
        },
        "identifiability": {
          "value": 4,
          "why": "Spleen-only edits separate relative from absolute liver evidence."
        },
        "medical_relevance": {
          "value": 4,
          "why": "It determines whether a whole-volume model rediscovered a trusted quantitative rule and when contrast phase may break it."
        },
        "interest": {
          "value": 4,
          "why": "Independent rediscovery of an internal calibration organ is broadly interpretable."
        },
        "prior_legwork": {
          "value": 4,
          "why": "Model, segmenters, and measurement validation exist."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped until the exact output and phase-homogeneous cohort are inspected."
        },
        "data_readiness": {
          "value": 3,
          "why": "Released data exist but scan-phase suitability is unverified."
        },
        "evaluation_readiness": {
          "value": 5,
          "why": "The attenuation formula gives a signed dose response and clear positive control."
        },
        "negative_result_value": {
          "value": 4,
          "why": "A gated null distinguishes absolute-liver from relative-organ reasoning."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped pending a formal Merlin interpretability audit."
        },
        "regret": {
          "value": 4,
          "why": "It is a cheap, obvious-in-hindsight test of whole-volume context."
        }
      },
      "priority_score": 3.8,
      "unverified_claims": [
        "The released Merlin vocabulary includes hepatic steatosis",
        "Enough phase-homogeneous scans retain both organs after preprocessing",
        "No prior spleen-only Merlin intervention exists"
      ],
      "plain_pitch": "Radiologists often judge a fatty liver by comparing its brightness with the spleen, which acts like a built-in calibration patch. Merlin reads an entire abdominal CT scan and may have discovered the same trick without being taught it. We would leave the liver untouched, gently change only the spleen's brightness, and see whether the fatty-liver score moves in the predicted direction. A positive result would turn an opaque model decision into a familiar radiology rule.",
      "track": "baseline",
      "charter": null
    },
    {
      "id": "scout-019-c03",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The azygos vein inside the edema score",
      "question": "Is a chest-radiograph pulmonary-edema classifier using azygos-vein caliber as a venous-pressure gauge?",
      "deliverable_sentence": "The pulmonary-edema classifier is using azygos-vein enlargement.",
      "rung": "Targets rung 1 by vessel-specific removal and restoration; rung 2 requires projection, rotation, and line/tube controls; rung 3 is available because azygos-vein enlargement is a named radiographic sign of venous congestion.",
      "rung_reached": "Rung 1 if edema logits respond specifically and monotonically to azygos-caliber edits; external replication and independent segmentation would support rung 3.",
      "unasked_question": "Edema classifiers are usually explained by lung opacities and heart size. The azygos arch is a small but pressure-responsive mediastinal vein; whether a model uses this extra-pulmonary sign has not been isolated.",
      "X_measurement": "Automatically localize the trachea/right main bronchus and right paratracheal mediastinum, segment the azygos arch shadow, and measure its maximum transverse diameter normalized by thoracic width in millimetres. The method must be validated against a small, pre-existing annotated development set or CT-projected synthetic radiographs; no test-set reader labels enter the primary endpoint. Compute-today test: YES as a well-defined geometric measurement, conditional on the segmentation gate.",
      "suspected_signal": "Raised right-sided and systemic venous pressure distends the azygos arch. Its rounded right paratracheal shadow can therefore accompany congestion even when alveolar opacity is subtle.",
      "use_vs_association": "Azygos width correlates with heart failure and edema, so regression is inadequate. The confirmatory design removes the localized shadow while preserving surrounding mediastinal texture and separately inserts graded, anatomically plausible widths, with lung fields and cardiac silhouette fixed.",
      "keystone_prerequisite": "The azygos arch is visible and automatically localizable at sufficient prevalence and fidelity in the exact public chest-radiograph test distribution to support bounded edits that do not alter adjacent superior vena cava, lymph nodes, or lines.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearest fact is the established radiographic association between azygos enlargement and venous congestion. I am still assuming the load-bearing imaging fact: that a distinct editable azygos shadow can be recovered from frontal radiographs often enough. A bounding box around the expected location would not satisfy this keystone.",
      "dies_like_prior": "It resembles idea-016's IDENTIFIABILITY_FAILURE (a pressure gauge co-varying with disease). The difference is a within-image, vessel-specific bidirectional intervention rather than observational anatomy. It dies the same way if the azygos shadow cannot be separated from neighboring mediastinum. Annotation provenance is irrelevant to the paired primary readout; report labels are used only to select a frozen pretrained model.",
      "closest_prior_work": "Public chest-radiograph classifiers such as CheXNet (Rajpurkar et al., arXiv:1711.05225) establish edema classification but do not test azygos caliber. The radiology literature describes azygos enlargement in congestion, but a primary quantitative anchor and automated-localization precedent must be pinned in novelty audit. No absence claim is made here.",
      "existing_assets": "Public radiographs and edema classifiers; rib/lung/mediastinal landmark segmenters; CT volumes that can generate digitally reconstructed radiographs for segmentation development.",
      "smallest_decisive_experiment": "Stage 0 estimates visible-azygos prevalence and segmentation repeatability on development data and stops if fewer than 100 clean test-eligible cases are projected. On frozen test cases, erase the azygos shadow with local mediastinal texture and insert three width doses; use matched edits at the left paratracheal border and line/tube-shaped shams. Require opposite signed responses for narrowing versus widening and a flat sham distribution.",
      "standing_confounds_addressed": "Within-image edits fix site, vendor, projection, protocol, habitus, prevalence, referral, and labels. Rotation and inspiration are fixed within each pair but limit mask reliability, so they are development gates. It does not fully rule out generic right-mediastinal contour sensitivity; contralateral and adjacent-border shams address this. Reconstruction is not applicable to radiographs.",
      "alternative_explanations": [
        "The model uses generic right-mediastinal widening; adjacent-border shams test it.",
        "It reacts to line-like edits; catheter-shaped shams test this.",
        "Azygos width is inseparable from rotation; a strict clavicular-rotation gate restricts the estimand rather than statistically wishing rotation away."
      ],
      "anticipated_negative": "Decisive only after localization, positive-dose visibility, and realism gates pass. Failure to localize the vein is an interpretable feasibility kill but not a negative about model use.",
      "remaining_legwork": "Three days for a visibility census, one week for localization/edit validation, and one additional week to a first test result.",
      "design_template": "regional-removal",
      "entry_point_2_requirements": "Measurement: normalized azygos-arch diameter. Confusable artifacts: patient rotation, inspiration, adjacent mediastinal contours, and central lines; all receive explicit gates or shams.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "The sign and intervention are clear; localization is the weak joint."
        },
        "identifiability": {
          "value": 4,
          "why": "Bidirectional edits and adjacent-border shams isolate the named vessel if segmentation passes."
        },
        "medical_relevance": {
          "value": 4,
          "why": "It would reveal whether edema AI reads a real extra-pulmonary congestion sign."
        },
        "interest": {
          "value": 4,
          "why": "A small mediastinal vein serving as a pressure gauge is surprising and physician-legible."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Models and data exist; the required vein localizer is not ready."
        },
        "feasibility": {
          "value": 2,
          "why": "Visibility and separable localization are substantial uninspected barriers."
        },
        "data_readiness": {
          "value": 4,
          "why": "Public radiographs and frozen classifiers are abundant."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Paired logits are simple, but edit-validity metrics need freezing."
        },
        "negative_result_value": {
          "value": 4,
          "why": "A gated null cleanly rejects a specific extra-pulmonary cue."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped; the closest automated azygos work is not yet audited."
        },
        "regret": {
          "value": 3,
          "why": "Worth a cheap visibility gate before investing in an editor."
        }
      },
      "priority_score": 3.45,
      "unverified_claims": [
        "Azygos visibility prevalence in the chosen corpus",
        "Availability of a suitable automatic localizer",
        "Novelty of azygos-specific classifier intervention",
        "Primary quantitative azygos-congestion citation"
      ],
      "plain_pitch": "When venous pressure rises, a small vein beside the upper right lung called the azygos vein can widen on a chest X-ray. An artificial-intelligence system asked to detect fluid in the lungs might quietly use that vein as a pressure gauge. We would narrow and widen only that shadow while leaving the lungs and heart unchanged. If the edema score follows the vein, radiologists gain a concrete explanation for part of the model's decision.",
      "track": "baseline",
      "charter": null
    },
    {
      "id": "scout-019-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The meniscus inside the pleural-effusion score",
      "question": "Is CT-CLIP's pleural-effusion score using the curvature of the pleural-fluid meniscus rather than fluid volume alone?",
      "deliverable_sentence": "CT-CLIP's pleural-effusion score is using pleural-fluid meniscus curvature.",
      "rung": "Targets rung 1 with volume-preserving shape counterfactuals; rung 2 requires fluid-density, positioning, reconstruction, and synthesis controls; rung 3 follows if curvature use replicates in real positional pairs.",
      "rung_reached": "Rung 1 if the score changes with meniscus curvature at fixed segmented fluid volume and density; real prone/supine replication would move it toward rung 3.",
      "X_measurement": "Segment pleural fluid with an automated CT effusion segmenter, fit the superior fluid-air interface in a gravity-aligned coordinate system, and compute mean/maximum principal curvature plus the vertical height-to-basal-area ratio at fixed volume. CT effusion segmentation precedent: PMID 35923880 / PMCID PMC9390225. Compute-today test: YES once a mask is available; no reader rating is required.",
      "suspected_signal": "Free pleural fluid forms a smooth gravity-dependent upper meniscus, whereas loculated fluid and many soft-tissue mimics do not. The curved boundary may be a higher-contrast and more stable cue than absolute fluid volume after CT-CLIP's resampling.",
      "use_vs_association": "Large effusions have both more volume and a more conspicuous meniscus. The counterfactual preserves voxel count, attenuation distribution, pleural contact area, and surrounding anatomy while redistributing only the superior interface curvature; therefore volume cannot explain a positive result.",
      "keystone_prerequisite": "A volume-preserving deformation can vary the superior meniscus curvature across a physiologically observed range without changing pleural contact, introducing interpolation signatures, or producing shapes detectable as synthetic by a held-out model.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Existing work proves effusions can be segmented, not that curvature can be independently and realistically edited. That edit identifiability is the real keystone; the easy adjacent fact of segmentation availability does not establish it.",
      "dies_like_prior": "The main analogue is idea-006: an extreme edit could be out of distribution. This design uses small volume-preserving boundary transport and requires native-shape and discriminator gates, but it still dies like idea-006 if synthesis realism fails. It is distinct from scout-015-c01 (fluid volume) because volume is explicitly fixed and curvature is the claimed X.",
      "closest_prior_work": "CT-CLIP/CT-RATE supplies the released pleural-effusion head; idea-004 has already verified the checkpoint pipeline. Ebert et al., PMCID PMC9390225, automate effusion segmentation and complexity classification but do not test a report-supervised model's use of meniscus curvature. The formal audit must search pleural shape radiomics and classifier attribution; no novelty claim is made yet.",
      "existing_assets": "Frozen CT-CLIP inference from idea-004; CT-RATE validation volumes; published CT effusion segmenters; geometry operations feasible on one GPU/CPU.",
      "smallest_decisive_experiment": "Stage 0 segments 100 effusions and estimates the native joint distribution of volume, interface curvature, density, and pleural contact. Build two counterfactuals per scan that increase or decrease curvature while preserving volume, density histogram, contact area, and every non-fluid voxel. Compare paired effusion-score slopes with equal-energy internal fluid rearrangements that leave curvature fixed. The untouched test set is scored once after all realism gates freeze.",
      "standing_confounds_addressed": "Within-image counterfactuals fix scanner, vendor, protocol, reconstruction, site, positioning, habitus, prevalence, referral, and label leakage. Density and volume are preserved. It does not rule out response to interpolation at the moved boundary unless sham and discriminator gates pass; real positional replication would address synthesis external validity.",
      "alternative_explanations": [
        "The model responds to any moved fluid boundary; curvature-fixed boundary-jitter shams test this.",
        "Pleural contact area changes despite volume preservation; it is constrained and audited voxelwise.",
        "The edit creates implausible loculations; native-shape support and a blinded discriminator gate reject such cases."
      ],
      "anticipated_negative": "Decisive after passed manipulation and sensitivity controls: meniscus curvature is not used by this checkpoint over the tested native range. A failed synthesis gate is uninterpretable scientifically but cheaply kills the design.",
      "cross_domain": {
        "borrowed_construct": "Capillarity and free-surface geometry: a fluid interface described by curvature under gravity.",
        "implied_measurement": "Principal curvature of the superior pleural-fluid interface at fixed fluid volume.",
        "what_changes_if_dropped": "Without the free-surface construct, the intervention would vary arbitrary shape radiomics. The analogy supplies the specific gravity-aligned interface, curvature statistic, fixed-volume constraint, and signed deformation."
      },
      "remaining_legwork": "Three days for segmentation/native-support audit and roughly two weeks for a validated deformation and first decision.",
      "design_template": "counterfactual-synthesis",
      "entry_point_2_requirements": "Measurement: gravity-aligned interface curvature. Confusable artifacts: volume, attenuation, positioning, reconstruction, interpolation, and loculation; the design fixes or gates each.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "The claimed physical quantity and fixed-volume contrast are precise."
        },
        "identifiability": {
          "value": 4,
          "why": "The construction isolates curvature if the demanding realism gate passes."
        },
        "medical_relevance": {
          "value": 3,
          "why": "It explains a common finding score but has indirect immediate clinical consequence."
        },
        "interest": {
          "value": 5,
          "why": "A model reading fluid physics rather than amount is surprising and generalizable."
        },
        "mechanism_clarity": {
          "value": 5,
          "why": "Curvature, gravity-aligned interface, and measurement are fully named."
        },
        "prior_legwork": {
          "value": 4,
          "why": "The model pipeline and segmentation precedents already exist."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped; independent realistic curvature editing is uninspected."
        },
        "data_readiness": {
          "value": 4,
          "why": "The exact model and CT cohort are already operational in the program."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "Signed paired slopes and geometry invariants are explicit."
        },
        "negative_result_value": {
          "value": 4,
          "why": "A gated null decisively separates volume from interface shape use."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped pending shape-radiomics audit."
        },
        "regret": {
          "value": 4,
          "why": "Existing inference makes the hard geometry gate worth testing."
        }
      },
      "mode_c_priority_score": 4.45,
      "unverified_claims": [
        "A CT effusion segmenter transfers to CT-RATE",
        "Curvature is independently editable in native support",
        "No prior fixed-volume meniscus intervention exists"
      ],
      "plain_pitch": "Fluid around the lung does not just occupy space; gravity gives its upper surface a smooth curved edge called a meniscus. The model may recognize that edge rather than simply measuring how much fluid is present. We would reshape the same number of fluid voxels to make the meniscus flatter or steeper while leaving density and the rest of the scan unchanged. If the score follows curvature, the model is using a recognizable piece of fluid physics.",
      "track": "baseline",
      "charter": null
    },
    {
      "id": "scout-019-c05",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The opening in the diaphragm inside the hiatal-hernia score",
      "question": "Is CT-CLIP's hiatal-hernia score using diaphragmatic crural separation rather than herniated stomach volume?",
      "deliverable_sentence": "CT-CLIP's hiatal-hernia score is using widening of the esophageal hiatus between the diaphragmatic crura.",
      "rung": "Targets rung 1 with within-patient state changes that separate aperture width from herniated volume; rung 2 requires phase, gastric distension, positioning, reconstruction, and crop controls; rung 3 needs a confirmatory aperture-specific intervention or naturally discordant pairs.",
      "rung_reached": "At most rung 1 from longitudinal discordant pairs; an aperture-specific, realism-gated intervention is required to move to rung 3.",
      "X_measurement": "Segment diaphragm/crura and esophagus/stomach, define the esophageal-hiatus plane, and measure transverse intercrural distance, hiatus area, and crural thickness in millimetres. These are direct geometric quantities. Compute-today test: YES in principle with automatic organ/diaphragm segmentation, without reader judgment; robust crural segmentation on low-dose chest CT is the keystone gate.",
      "suspected_signal": "The right and left diaphragmatic crura form a muscular aperture. Chronic widening and thinning reduce the mechanical barrier to trans-hiatal stomach migration. A whole-volume model may read the fixed anatomical aperture even when herniated stomach volume changes with respiration or gastric filling.",
      "use_vs_association": "Wider hiatus and larger hernia usually co-occur, so cross-sectional regression is insufficient. The primary screen seeks same-patient scans where herniated stomach volume changes substantially but crural separation is stable, and the converse; score changes across those discordant natural states distinguish aperture use from sac-volume use.",
      "keystone_prerequisite": "CT-RATE contains enough same-patient repeat scans with full diaphragmatic coverage and naturally discordant changes in intercrural distance versus herniated-stomach volume, without simultaneous protocol/crop changes that reproduce the same discordance.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The ledger verifies repeat patients in CT-RATE, and the hiatal-hernia head exists. I am still assuming the load-bearing fact that the repeats contain adequate natural discordance and crural coverage. Repeat scans alone are only the nearest easy fact and do not establish the design.",
      "dies_like_prior": "It risks idea-009's IDENTIFIABILITY_FAILURE because aperture width and hernia volume are mechanically coupled. Unlike idea-009, it requires prespecified within-patient discordant support before inference. It is distinct from scout-015-c04, which asks whether the score uses a continuous air tunnel; this candidate names the muscular aperture and tests it against stomach volume. Annotation provenance does not enter the primary readout.",
      "closest_prior_work": "CT-CLIP/CT-RATE and the frozen ClassFine checkpoint are verified locally through idea-004. Quantitative hiatus/crural measurements exist in surgical and CT literature, but the exact primary measurement citation and any AI attribution work require formal audit. Scout-015-c04 is the closest internal candidate and tests luminal air continuity, not crural separation.",
      "existing_assets": "Operational CT-CLIP pipeline; CT-RATE repeat-session metadata; TotalSegmentator stomach/esophagus context masks; deterministic geometry once crura are segmented.",
      "smallest_decisive_experiment": "Stage 0 runs crural/upper-stomach segmentation on all repeat patients, audits crop coverage, and counts pairs in four prespecified cells: stable aperture/changing hernia volume, changing aperture/stable volume, concordant change, and stable/stable. Freeze minimum support and measurement repeatability before scores. Only if both discordant cells pass support, compare within-patient hiatal-hernia score changes using a two-predictor errors-in-variables model; stable/stable pairs estimate the noise floor.",
      "standing_confounds_addressed": "Within-patient analysis removes fixed site, habitus, prevalence, and referral pathway. Metadata matching/stratification addresses vendor, protocol, reconstruction, and positioning; tensor-coverage audits address cropping. Label leakage cannot vary within a model-to-itself pair. Gastric distension and inspiration remain plausible time-varying alternatives and are measured via stomach gas volume and lung volume rather than assumed away.",
      "alternative_explanations": [
        "The score follows herniated stomach volume, not aperture width; the discordant cells are designed to distinguish them.",
        "Inspiration changes both crural geometry and model framing; lung volume and final-tensor coverage are explicit gates/covariates.",
        "Gastric gas, not anatomy, drives the score; gas volume is measured and stable-gas sensitivity analysis is prespecified."
      ],
      "anticipated_negative": "If adequate discordant support exists and score changes follow only hernia volume, that is a decisive negative for aperture use and a positive competing explanation. Absence of discordant support is an interpretable feasibility kill, not a biological negative.",
      "cross_domain": {
        "borrowed_construct": "Structural mechanics: a muscular aperture whose span and thickness govern resistance to organ passage.",
        "implied_measurement": "Intercrural distance, hiatus area, and crural thickness contrasted with trans-hiatal stomach volume.",
        "what_changes_if_dropped": "Without the aperture-mechanics framing, there is no reason to measure crural span separately from hernia size or demand discordant natural states; the study would collapse into routine severity correlation."
      },
      "remaining_legwork": "About one week for segmentation/coverage and discordance census; if support passes, one further week to the paired score analysis.",
      "design_template": "longitudinal-within-subject",
      "entry_point_2_requirements": "Measurement: intercrural distance/hiatus area. Confusable artifacts: herniated volume, inspiration, gastric gas, positioning, protocol, and final-tensor crop; all are measured or gated.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "The competing quantities are clear; the natural-discordance estimand needs sufficient support."
        },
        "identifiability": {
          "value": 3,
          "why": "Discordant within-patient states help, but time-varying anatomy and measurement error remain."
        },
        "medical_relevance": {
          "value": 3,
          "why": "It explains a common score and could distinguish structural susceptibility from transient herniation."
        },
        "interest": {
          "value": 4,
          "why": "A model reading the muscular gateway rather than the herniated organ is unexpected."
        },
        "mechanism_clarity": {
          "value": 5,
          "why": "Aperture span, thickness, organ passage, and measurements are specific."
        },
        "prior_legwork": {
          "value": 4,
          "why": "Model, repeated scans, and contextual segmenters already exist."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped; natural discordance and crural segmentation are not inspected."
        },
        "data_readiness": {
          "value": 4,
          "why": "The CT-RATE repeat cohort and model pipeline are program assets."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "The geometry is clear but measurement-error modeling and support thresholds need freezing."
        },
        "negative_result_value": {
          "value": 4,
          "why": "Following volume rather than aperture is a decisive competing explanation if support passes."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped pending hiatus-measurement and attribution audit."
        },
        "regret": {
          "value": 3,
          "why": "The Stage-0 census is cheap on existing repeats, though success is uncertain."
        }
      },
      "mode_c_priority_score": 3.9,
      "unverified_claims": [
        "Robust automatic crural segmentation on CT-RATE",
        "Adequate natural discordance in repeat scans",
        "Primary validation citation for automated hiatus measurement",
        "No prior model attribution to crural separation"
      ],
      "plain_pitch": "A hiatal hernia occurs when the opening in the diaphragm around the food pipe becomes wide enough for stomach to pass upward. The visible amount of stomach above the diaphragm can change with breathing and filling, while the muscular opening may remain wide. By comparing repeat scans from the same person where these two quantities change differently, we can ask whether the model reads the opening itself or merely the amount of displaced stomach. A positive result would name the anatomical gateway behind the score.",
      "track": "baseline",
      "charter": null
    }
  ]
}


===== ideas/scout-019/run_provenance.json =====
{
  "timestamp": "2026-08-21T06:28:42+00:00",
  "git_commit": "d59d29792608cb5cb348a8066dc3308b4a4f2259",
  "claude_cli": "2.1.197 (Claude Code)",
  "codex_cli": "codex-cli 0.149.0",
  "tracks": [
    "baseline"
  ],
  "seed_concepts": null,
  "prompt_hashes": {
    "actioner.md": "263f5cce53cb0cee",
    "context_memo.md": "4de103654cef2380",
    "critique.md": "02e2bc57b59477a0",
    "debate_critic.md": "74f1e299e3c6db50",
    "debate_proposer.md": "6a41797dbc73796a",
    "debate_summary.md": "af554e8fd24b0579",
    "feasibility.md": "065590081e9c6367",
    "fiction_extract.md": "8ada1a395c25072e",
    "fiction_refine.md": "a547dbb2fc03b443",
    "fiction_scout.md": "63b11687055c8624",
    "interpret.md": "7ce78a736a0ae412",
    "interpret_review.md": "7907433221058558",
    "keystone_screen.md": "f6f206ca8577b47b",
    "librarian.md": "e6977370921ff990",
    "novelty_audit.md": "3139addc91205b1e",
    "probe_code.md": "bc0c52c94d1af371",
    "probe_plan.md": "6249699cb2278e0e",
    "probe_review.md": "6b222a3f766009ea",
    "revise.md": "db7fab4a10c7c32b",
    "scout.md": "7d943c7d48044a35",
    "wide_scout.md": "deb81c952f9b424f"
  },
  "agents_toml_hash": "4b0d0da9640a634d"
}


===== ideas/scout-019/scout_candidates.json =====
{
  "cycle": "scout-019",
  "date": "2026-08-25",
  "track": "baseline",
  "all_questions": [
    {"n": 1, "question": "Is a fundus-photograph sex classifier using the richness of the retinal vessel tree?", "disposition": "DEVELOPED as scout-019-c01 (Mode A)."},
    {"n": 2, "question": "Is Merlin's hepatic-steatosis score using the spleen as an internal attenuation reference?", "disposition": "DEVELOPED as scout-019-c02 (Mode B)."},
    {"n": 3, "question": "Is a chest-radiograph pulmonary-edema classifier using azygos-vein caliber as a venous-pressure gauge?", "disposition": "DEVELOPED as scout-019-c03 (Mode B)."},
    {"n": 4, "question": "Is CT-CLIP's pleural-effusion score using the curvature of the pleural-fluid meniscus rather than fluid volume alone?", "disposition": "DEVELOPED as scout-019-c04 (Mode C; capillarity/geometry)."},
    {"n": 5, "question": "Is CT-CLIP's hiatal-hernia score using diaphragmatic crural separation rather than herniated stomach volume?", "disposition": "DEVELOPED as scout-019-c05 (Mode C; structural mechanics)."},
    {"n": 6, "question": "Is a brain-age magnetic-resonance model using the branching complexity of perivascular spaces as a glymphatic-aging marker?", "disposition": "DROPPED (cross-domain, network transport; too hard): an automated perivascular-space measurement exists, but no obtainable model-and-cohort pairing was identified and segmentation error would be entangled with scanner field strength."},
    {"n": 7, "question": "Is a lung-cancer CT model using the handedness of bronchial branching?", "disposition": "DROPPED (obviously wrong but not immediately refutable): handedness is measurable, but there is no credible biological route to cancer risk beyond anatomy/site imbalance, and a positive edit response would more likely be an impossible-geometry artifact."},
    {"n": 8, "question": "Is an abdominal mortality model using the fractal dimension of mesenteric fat stranding as a record of inflammatory history?", "disposition": "DROPPED (cross-domain, critical phenomena): the analogy does not change the proposed texture calculation, so it is decorative under the charter's analogy test."},
    {"n": 9, "question": "Is a chest-CT emphysema model using expiratory tracheal collapse?", "disposition": "DROPPED: routine inspiratory CT does not provide the dynamic denominator needed to name expiratory collapse, so X cannot be computed on every new scan today."},
    {"n": 10, "question": "Is a vertebral-fracture model using endplate concavity before height loss becomes visible?", "disposition": "DROPPED: too close to scout-006-c04's already-tracked density-versus-shape question and scout-017-c01's crushed-vertebra mortality question; no changed fact supports a recombination."}
  ],
  "quota_note": "Exactly 1 Mode A (c01), 2 Mode B (c02-c03), and 2 Mode C (c04-c05). Four of five are radiology and three are CT/3D. CT-RATE is used by exactly two candidates; Merlin, a public chest-radiograph corpus, and a fundus corpus are each used once. No dermatology. There are zero revivals because no portfolio blocking condition was shown to have changed. All five use different design templates; no clinical-costume reuse is hidden in the set.",
  "candidates": [
    {
      "id": "scout-019-c01",
      "search_mode": "A",
      "entry_point": 1,
      "title": "Name the vessel-tree phenotype inside retinal sex prediction",
      "question": "Is a fundus-photograph sex classifier using the richness of the retinal vessel tree?",
      "deliverable_sentence": "The fundus sex classifier is using retinal vessel-tree richness.",
      "rung": "Targets rung 1 through structure-selective erasure; rung 2 requires camera- and pigmentation-stratified replication; rung 3 is available because vessel-tree richness is a named graph phenotype, but biological interpretation beyond that needs independent validation.",
      "rung_reached": "Rung 1 if selectively removing distal branches changes the frozen classifier beyond vessel-area-matched shams; rung 3 requires the result to replicate with independent vessel segmenters and cameras.",
      "unfinished_story": "Poplin et al. showed that fundus photographs predict sex at high accuracy and localized evidence broadly to retinal regions, while later work measured sex differences in vessel branches, nodes, length, caliber, tortuosity, and retinal regions. The missing experiment is whether a frozen high-performing classifier actually uses the measured branch-richness phenotype rather than merely coexisting with it.",
      "X_measurement": "Segment arteries and veins with a published fundus-vessel network, skeletonize the binary vessel mask, and compute branch-point count, terminal count, total skeleton length, and vessel-covered area within a fixed disc-centered field. The primary X is residual branch count after matching total vessel area and image field. Primary sources: Delavari et al., arXiv:2301.06675; macular geometry study PMID 34977079. Compute-today test: YES; it is deterministic after automated segmentation and requires no reader.",
      "suspected_signal": "Sex-associated developmental and vascular differences alter how many visible retinal branches and nodes occupy a standardized fundus field. Fine dark branches create a repeated local texture a convolutional classifier can aggregate even when no human recognizes the global phenotype.",
      "use_vs_association": "Measured sex differences alone show association; the confirmatory test erases distal vessel branches while holding field, background, and total removed pixel area fixed, then compares the paired sex-logit change with vessel-area-matched proximal-segment and non-vessel shams.",
      "keystone_prerequisite": "A frozen, obtainable fundus sex classifier retains its published discrimination on an obtainable image corpus and automated vessel masks remain accurate enough that distal-branch erasure can vary branch count without changing total vessel area or the optic-disc/macular background beyond prespecified tolerances.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearest verified facts are that sex prediction is strong and vessel geometry differs by sex. I am still assuming the load-bearing fact that branch count can be manipulated independently of vessel area and local inpainting signature in the exact classifier input; that is the real keystone and is not established by either paper.",
      "dies_like_prior": "It risks idea-009's IDENTIFIABILITY_FAILURE if branch richness cannot be separated from vessel area, caliber, pigmentation, and camera field. Unlike idea-009, the proposed intervention explicitly matches vessel area and includes proximal-vessel and non-vessel shams. Annotation provenance does not apply: sex is registry-derived and the primary readout is model-to-itself.",
      "closest_prior_work": "Poplin et al., Nature Biomedical Engineering 2018, DOI 10.1038/s41551-018-0195-0, established retinal sex prediction but did not name a causal image quantity. Korot et al., DOI 10.1038/s41598-021-89743-x, found poorer performance with foveal pathology. Delavari et al., arXiv:2301.06675, measured greater branch/node richness in male images but did not intervene on a frozen classifier. A 2026 region-weight study, DOI 10.1038/s41598-026-53485-5, estimates macula/disc/vasculature contributions but not use of branch richness. Exact delta: matched, branch-selective erasure on the original task.",
      "existing_assets": "Public fundus datasets with sex metadata, published vessel segmenters, deterministic graph measurements, and several reproducible sex-classification architectures; all fit one GPU.",
      "smallest_decisive_experiment": "Stage 0 reproduces a frozen classifier on a subject-held-out set and validates vessel masks without using the test set. On 300 correctly classified test images, remove terminal vessel segments in graded doses, inpaint from immediately adjacent retina, and compare sex-logit dose response against equal-area proximal-vessel removal and non-vessel curvilinear shams. Freeze all dose bins and masks before test inference.",
      "standing_confounds_addressed": "Within-image comparisons fix camera, site, field, pigmentation, age, disease prevalence, and referral pathway. Camera/vendor and ethnicity are further stratified in replication. The design does not fully rule out branch-dependent inpainting detectability; sham detectability and a held-out edit discriminator gate it. Scanner/protocol/reconstruction are not CT-relevant here. Label leakage is unlikely but corpus filenames and borders must be audited.",
      "alternative_explanations": ["The model uses total vessel area, not branch richness; area-matched branch versus proximal-segment edits distinguish them.", "The model reacts to many small inpaint patches; equal-count non-vessel curvilinear shams test this.", "Camera sharpening reveals more branches and also predicts sex through site imbalance; within-image editing plus camera-stratified replication excludes the primary version."],
      "anticipated_negative": "Decisive if classifier reproduction, segmentation, independent manipulation, and edit-realism gates pass and branch erasure is no larger than matched shams. Otherwise it is a feasibility failure, not a biological null.",
      "cross_domain": {"borrowed_construct": "Graph theory: a vascular tree summarized by nodes, terminals, and total edge length.", "implied_measurement": "Residual branch/node count at fixed vessel area and field.", "what_changes_if_dropped": "Without graph language, the experiment loses its prespecified distinction between branching richness and simple vessel area; it would become generic vessel masking and could not support the deliverable sentence."},
      "remaining_legwork": "Two days to select and reproduce a model, three days for segmenter and edit gates, and about one week to first frozen test result.",
      "design_template": "representation-erasure",
      "scores": {
        "clarity": {"value": 5, "why": "One measurable graph phenotype and one matched intervention."},
        "identifiability": {"value": 4, "why": "Area matching and two sham families isolate richness, subject to edit realism."},
        "medical_relevance": {"value": 3, "why": "It could reveal a real retinal sex phenotype, but the sex-prediction task itself has limited direct utility."},
        "interest": {"value": 5, "why": "It closes a canonical model-beats-human mystery with a concrete anatomical quantity."},
        "prior_legwork": {"value": 4, "why": "The prediction gap and the candidate vessel phenotype are both already published."},
        "feasibility": {"value": 3, "why": "Capped because the independent-editability keystone is not inspected."},
        "data_readiness": {"value": 4, "why": "Public images, labels, and segmentation methods exist, though the exact frozen pairing is not selected."},
        "evaluation_readiness": {"value": 4, "why": "Paired logits and dose response have clear sham baselines."},
        "negative_result_value": {"value": 4, "why": "A gated null directly rejects a published candidate explanation."},
        "novelty_confidence": {"value": 3, "why": "Capped; a 2026 region-contribution paper makes a dedicated audit essential."},
        "regret": {"value": 5, "why": "The phenotype and canonical mystery are already adjacent in the literature."}
      },
      "priority_score": 3.8,
      "unverified_claims": ["An obtainable frozen classifier exactly reproduces published performance", "Branch count can be edited independently at classifier resolution", "No prior branch-selective causal intervention exists"],
      "plain_pitch": "Artificial intelligence can tell a person's sex from a retinal photograph even though eye specialists cannot explain how. Men and women may differ slightly in how richly the tiny retinal vessels branch. This study removes only the finest branches while carefully matching the amount of vessel erased elsewhere. If the prediction changes specifically with branch loss, the model has exposed a measurable anatomical difference rather than an unnamed visual clue."
    },
    {
      "id": "scout-019-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The spleen as the fatty-liver model's calibration patch",
      "question": "Is Merlin's hepatic-steatosis score using the spleen as an internal attenuation reference?",
      "deliverable_sentence": "Merlin's hepatic-steatosis score is using splenic attenuation as an internal reference for liver attenuation.",
      "rung": "Targets rung 1 by changing spleen attenuation while holding liver voxels fixed; rung 2 requires contrast-phase and protocol controls; rung 3 follows if the score implements the named liver-minus-spleen comparison used in radiology.",
      "rung_reached": "Rung 1 if the steatosis score follows controlled spleen-only attenuation shifts with the sign predicted by the liver-spleen difference; replication on noncontrast scans and multiple sites would move it toward rung 3.",
      "unasked_question": "Quantitative radiology often judges hepatic fat relative to the spleen, and automated liver/spleen measurement is mature. Merlin was trained without an explicit rule, so it is unknown whether the foundation model independently learned the spleen as a calibration reference.",
      "X_measurement": "Use TotalSegmentator to segment liver and spleen, erode masks from vessels and boundaries, and compute mean liver minus mean spleen attenuation in Hounsfield units and the liver/spleen ratio. Primary validation: Park et al., Radiology 2011, DOI 10.1148/radiol.10101233 (biopsy-proven nonsteatotic reference range); automated contrast-enhanced measurement PMID 40095018. Compute-today test: YES on any CT with both organs in view.",
      "suspected_signal": "The spleen provides an internal tissue reference that cancels some patient- and acquisition-level intensity variation. A vision-language model trained from reports may discover that a dark liver is more meaningful when the spleen remains bright.",
      "use_vs_association": "Observational correlation between score and liver-spleen difference cannot show which organ the model reads. The experiment shifts only splenic voxels within the observed physiological distribution while keeping the liver and every other voxel bit-identical, then tests the predicted monotone score response.",
      "keystone_prerequisite": "The released Merlin checkpoint exposes a hepatic-steatosis or fatty-liver score on an obtainable cohort containing enough noncontrast or phase-homogeneous scans with both liver and spleen fully represented after the exact preprocessing.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The primary paper verifies released models/data and 30 zero-shot findings, and the liver-spleen measurement itself is validated. I have not inspected the released finding vocabulary or input manifests for the exact steatosis head and phase-homogeneous support. That exact model-output-and-cohort pairing, not merely Merlin's existence, is the keystone.",
      "dies_like_prior": "It resembles idea-010's CIRCULARITY risk because the proposed X is a standard diagnostic rule. It differs because the question is not whether X predicts the steatosis label; it intervenes on the reference organ while liver appearance is fixed, testing whether this particular model uses the comparison. Annotation provenance is absent from the primary paired readout.",
      "closest_prior_work": "Merlin, Blankemeier et al., Nature 2026, PMID 41781626, releases models and evaluates 30 findings but does not report a spleen-reference intervention. Park et al., DOI 10.1148/radiol.10101233, validates the liver-spleen difference against biopsy but studies the biomarker, not model behavior. The exact delta is spleen-only perturbation of a frozen whole-volume model.",
      "existing_assets": "Released Merlin code/models and dataset; TotalSegmentator liver and spleen masks; accepted attenuation formulas; single-GPU inference.",
      "smallest_decisive_experiment": "Stage 0 inspects Merlin's actual finding vocabulary, preprocessing, scan phases, and organ coverage. If it passes, select 200 test scans across the liver-spleen difference range. Apply graded spleen-only shifts of -15 to +15 HU, excluding vessels and lesions; use same-volume liver shifts as a positive control and kidney-cortex shifts matched for volume and baseline attenuation as a specificity sham. Primary endpoint: sign and slope of paired steatosis-logit change.",
      "standing_confounds_addressed": "Within-image editing fixes scanner, vendor, protocol, reconstruction, site, positioning, habitus, prevalence, referral pathway, and label leakage. Phase is fixed by cohort restriction. It does not automatically rule out generic response to any large-organ intensity shift; kidney shams do. Contrast timing limits generalization beyond the selected phase.",
      "alternative_explanations": ["The model responds to any organ-wide intensity shift; kidney-cortex shams test specificity.", "The model uses absolute liver attenuation only; a flat spleen arm with a responsive liver positive control supports that alternative.", "Spleen edits are out of distribution; bounded native-intensity substitution and a held-out edit discriminator gate this."],
      "anticipated_negative": "Decisive after a responsive liver positive control and passed realism gate: Merlin does not use the spleen reference on this cohort. Without the positive control, a null is sensitivity-limited.",
      "remaining_legwork": "One day to inspect the released label vocabulary and preprocessing, two days for phase/coverage census, and one week for masks, controls, and first result.",
      "design_template": "regional-substitution",
      "entry_point_2_requirements": "Measurement: eroded-mask liver-minus-spleen attenuation and ratio. Confusable artifacts: contrast phase, global calibration drift, and generic organ-intensity edits; phase restriction and kidney shams address them.",
      "scores": {
        "clarity": {"value": 5, "why": "The reference organ, direction, and control are explicit."},
        "identifiability": {"value": 4, "why": "Spleen-only edits separate relative from absolute liver evidence."},
        "medical_relevance": {"value": 4, "why": "It determines whether a whole-volume model rediscovered a trusted quantitative rule and when contrast phase may break it."},
        "interest": {"value": 4, "why": "Independent rediscovery of an internal calibration organ is broadly interpretable."},
        "prior_legwork": {"value": 4, "why": "Model, segmenters, and measurement validation exist."},
        "feasibility": {"value": 3, "why": "Capped until the exact output and phase-homogeneous cohort are inspected."},
        "data_readiness": {"value": 3, "why": "Released data exist but scan-phase suitability is unverified."},
        "evaluation_readiness": {"value": 5, "why": "The attenuation formula gives a signed dose response and clear positive control."},
        "negative_result_value": {"value": 4, "why": "A gated null distinguishes absolute-liver from relative-organ reasoning."},
        "novelty_confidence": {"value": 3, "why": "Capped pending a formal Merlin interpretability audit."},
        "regret": {"value": 4, "why": "It is a cheap, obvious-in-hindsight test of whole-volume context."}
      },
      "priority_score": 3.8,
      "unverified_claims": ["The released Merlin vocabulary includes hepatic steatosis", "Enough phase-homogeneous scans retain both organs after preprocessing", "No prior spleen-only Merlin intervention exists"],
      "plain_pitch": "Radiologists often judge a fatty liver by comparing its brightness with the spleen, which acts like a built-in calibration patch. Merlin reads an entire abdominal CT scan and may have discovered the same trick without being taught it. We would leave the liver untouched, gently change only the spleen's brightness, and see whether the fatty-liver score moves in the predicted direction. A positive result would turn an opaque model decision into a familiar radiology rule."
    },
    {
      "id": "scout-019-c03",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The azygos vein inside the edema score",
      "question": "Is a chest-radiograph pulmonary-edema classifier using azygos-vein caliber as a venous-pressure gauge?",
      "deliverable_sentence": "The pulmonary-edema classifier is using azygos-vein enlargement.",
      "rung": "Targets rung 1 by vessel-specific removal and restoration; rung 2 requires projection, rotation, and line/tube controls; rung 3 is available because azygos-vein enlargement is a named radiographic sign of venous congestion.",
      "rung_reached": "Rung 1 if edema logits respond specifically and monotonically to azygos-caliber edits; external replication and independent segmentation would support rung 3.",
      "unasked_question": "Edema classifiers are usually explained by lung opacities and heart size. The azygos arch is a small but pressure-responsive mediastinal vein; whether a model uses this extra-pulmonary sign has not been isolated.",
      "X_measurement": "Automatically localize the trachea/right main bronchus and right paratracheal mediastinum, segment the azygos arch shadow, and measure its maximum transverse diameter normalized by thoracic width in millimetres. The method must be validated against a small, pre-existing annotated development set or CT-projected synthetic radiographs; no test-set reader labels enter the primary endpoint. Compute-today test: YES as a well-defined geometric measurement, conditional on the segmentation gate.",
      "suspected_signal": "Raised right-sided and systemic venous pressure distends the azygos arch. Its rounded right paratracheal shadow can therefore accompany congestion even when alveolar opacity is subtle.",
      "use_vs_association": "Azygos width correlates with heart failure and edema, so regression is inadequate. The confirmatory design removes the localized shadow while preserving surrounding mediastinal texture and separately inserts graded, anatomically plausible widths, with lung fields and cardiac silhouette fixed.",
      "keystone_prerequisite": "The azygos arch is visible and automatically localizable at sufficient prevalence and fidelity in the exact public chest-radiograph test distribution to support bounded edits that do not alter adjacent superior vena cava, lymph nodes, or lines.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearest fact is the established radiographic association between azygos enlargement and venous congestion. I am still assuming the load-bearing imaging fact: that a distinct editable azygos shadow can be recovered from frontal radiographs often enough. A bounding box around the expected location would not satisfy this keystone.",
      "dies_like_prior": "It resembles idea-016's IDENTIFIABILITY_FAILURE (a pressure gauge co-varying with disease). The difference is a within-image, vessel-specific bidirectional intervention rather than observational anatomy. It dies the same way if the azygos shadow cannot be separated from neighboring mediastinum. Annotation provenance is irrelevant to the paired primary readout; report labels are used only to select a frozen pretrained model.",
      "closest_prior_work": "Public chest-radiograph classifiers such as CheXNet (Rajpurkar et al., arXiv:1711.05225) establish edema classification but do not test azygos caliber. The radiology literature describes azygos enlargement in congestion, but a primary quantitative anchor and automated-localization precedent must be pinned in novelty audit. No absence claim is made here.",
      "existing_assets": "Public radiographs and edema classifiers; rib/lung/mediastinal landmark segmenters; CT volumes that can generate digitally reconstructed radiographs for segmentation development.",
      "smallest_decisive_experiment": "Stage 0 estimates visible-azygos prevalence and segmentation repeatability on development data and stops if fewer than 100 clean test-eligible cases are projected. On frozen test cases, erase the azygos shadow with local mediastinal texture and insert three width doses; use matched edits at the left paratracheal border and line/tube-shaped shams. Require opposite signed responses for narrowing versus widening and a flat sham distribution.",
      "standing_confounds_addressed": "Within-image edits fix site, vendor, projection, protocol, habitus, prevalence, referral, and labels. Rotation and inspiration are fixed within each pair but limit mask reliability, so they are development gates. It does not fully rule out generic right-mediastinal contour sensitivity; contralateral and adjacent-border shams address this. Reconstruction is not applicable to radiographs.",
      "alternative_explanations": ["The model uses generic right-mediastinal widening; adjacent-border shams test it.", "It reacts to line-like edits; catheter-shaped shams test this.", "Azygos width is inseparable from rotation; a strict clavicular-rotation gate restricts the estimand rather than statistically wishing rotation away."],
      "anticipated_negative": "Decisive only after localization, positive-dose visibility, and realism gates pass. Failure to localize the vein is an interpretable feasibility kill but not a negative about model use.",
      "remaining_legwork": "Three days for a visibility census, one week for localization/edit validation, and one additional week to a first test result.",
      "design_template": "regional-removal",
      "entry_point_2_requirements": "Measurement: normalized azygos-arch diameter. Confusable artifacts: patient rotation, inspiration, adjacent mediastinal contours, and central lines; all receive explicit gates or shams.",
      "scores": {
        "clarity": {"value": 4, "why": "The sign and intervention are clear; localization is the weak joint."},
        "identifiability": {"value": 4, "why": "Bidirectional edits and adjacent-border shams isolate the named vessel if segmentation passes."},
        "medical_relevance": {"value": 4, "why": "It would reveal whether edema AI reads a real extra-pulmonary congestion sign."},
        "interest": {"value": 4, "why": "A small mediastinal vein serving as a pressure gauge is surprising and physician-legible."},
        "prior_legwork": {"value": 3, "why": "Models and data exist; the required vein localizer is not ready."},
        "feasibility": {"value": 2, "why": "Visibility and separable localization are substantial uninspected barriers."},
        "data_readiness": {"value": 4, "why": "Public radiographs and frozen classifiers are abundant."},
        "evaluation_readiness": {"value": 3, "why": "Paired logits are simple, but edit-validity metrics need freezing."},
        "negative_result_value": {"value": 4, "why": "A gated null cleanly rejects a specific extra-pulmonary cue."},
        "novelty_confidence": {"value": 3, "why": "Capped; the closest automated azygos work is not yet audited."},
        "regret": {"value": 3, "why": "Worth a cheap visibility gate before investing in an editor."}
      },
      "priority_score": 3.45,
      "unverified_claims": ["Azygos visibility prevalence in the chosen corpus", "Availability of a suitable automatic localizer", "Novelty of azygos-specific classifier intervention", "Primary quantitative azygos-congestion citation"],
      "plain_pitch": "When venous pressure rises, a small vein beside the upper right lung called the azygos vein can widen on a chest X-ray. An artificial-intelligence system asked to detect fluid in the lungs might quietly use that vein as a pressure gauge. We would narrow and widen only that shadow while leaving the lungs and heart unchanged. If the edema score follows the vein, radiologists gain a concrete explanation for part of the model's decision."
    },
    {
      "id": "scout-019-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The meniscus inside the pleural-effusion score",
      "question": "Is CT-CLIP's pleural-effusion score using the curvature of the pleural-fluid meniscus rather than fluid volume alone?",
      "deliverable_sentence": "CT-CLIP's pleural-effusion score is using pleural-fluid meniscus curvature.",
      "rung": "Targets rung 1 with volume-preserving shape counterfactuals; rung 2 requires fluid-density, positioning, reconstruction, and synthesis controls; rung 3 follows if curvature use replicates in real positional pairs.",
      "rung_reached": "Rung 1 if the score changes with meniscus curvature at fixed segmented fluid volume and density; real prone/supine replication would move it toward rung 3.",
      "X_measurement": "Segment pleural fluid with an automated CT effusion segmenter, fit the superior fluid-air interface in a gravity-aligned coordinate system, and compute mean/maximum principal curvature plus the vertical height-to-basal-area ratio at fixed volume. CT effusion segmentation precedent: PMID 35923880 / PMCID PMC9390225. Compute-today test: YES once a mask is available; no reader rating is required.",
      "suspected_signal": "Free pleural fluid forms a smooth gravity-dependent upper meniscus, whereas loculated fluid and many soft-tissue mimics do not. The curved boundary may be a higher-contrast and more stable cue than absolute fluid volume after CT-CLIP's resampling.",
      "use_vs_association": "Large effusions have both more volume and a more conspicuous meniscus. The counterfactual preserves voxel count, attenuation distribution, pleural contact area, and surrounding anatomy while redistributing only the superior interface curvature; therefore volume cannot explain a positive result.",
      "keystone_prerequisite": "A volume-preserving deformation can vary the superior meniscus curvature across a physiologically observed range without changing pleural contact, introducing interpolation signatures, or producing shapes detectable as synthetic by a held-out model.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Existing work proves effusions can be segmented, not that curvature can be independently and realistically edited. That edit identifiability is the real keystone; the easy adjacent fact of segmentation availability does not establish it.",
      "dies_like_prior": "The main analogue is idea-006: an extreme edit could be out of distribution. This design uses small volume-preserving boundary transport and requires native-shape and discriminator gates, but it still dies like idea-006 if synthesis realism fails. It is distinct from scout-015-c01 (fluid volume) because volume is explicitly fixed and curvature is the claimed X.",
      "closest_prior_work": "CT-CLIP/CT-RATE supplies the released pleural-effusion head; idea-004 has already verified the checkpoint pipeline. Ebert et al., PMCID PMC9390225, automate effusion segmentation and complexity classification but do not test a report-supervised model's use of meniscus curvature. The formal audit must search pleural shape radiomics and classifier attribution; no novelty claim is made yet.",
      "existing_assets": "Frozen CT-CLIP inference from idea-004; CT-RATE validation volumes; published CT effusion segmenters; geometry operations feasible on one GPU/CPU.",
      "smallest_decisive_experiment": "Stage 0 segments 100 effusions and estimates the native joint distribution of volume, interface curvature, density, and pleural contact. Build two counterfactuals per scan that increase or decrease curvature while preserving volume, density histogram, contact area, and every non-fluid voxel. Compare paired effusion-score slopes with equal-energy internal fluid rearrangements that leave curvature fixed. The untouched test set is scored once after all realism gates freeze.",
      "standing_confounds_addressed": "Within-image counterfactuals fix scanner, vendor, protocol, reconstruction, site, positioning, habitus, prevalence, referral, and label leakage. Density and volume are preserved. It does not rule out response to interpolation at the moved boundary unless sham and discriminator gates pass; real positional replication would address synthesis external validity.",
      "alternative_explanations": ["The model responds to any moved fluid boundary; curvature-fixed boundary-jitter shams test this.", "Pleural contact area changes despite volume preservation; it is constrained and audited voxelwise.", "The edit creates implausible loculations; native-shape support and a blinded discriminator gate reject such cases."],
      "anticipated_negative": "Decisive after passed manipulation and sensitivity controls: meniscus curvature is not used by this checkpoint over the tested native range. A failed synthesis gate is uninterpretable scientifically but cheaply kills the design.",
      "cross_domain": {"borrowed_construct": "Capillarity and free-surface geometry: a fluid interface described by curvature under gravity.", "implied_measurement": "Principal curvature of the superior pleural-fluid interface at fixed fluid volume.", "what_changes_if_dropped": "Without the free-surface construct, the intervention would vary arbitrary shape radiomics. The analogy supplies the specific gravity-aligned interface, curvature statistic, fixed-volume constraint, and signed deformation."},
      "remaining_legwork": "Three days for segmentation/native-support audit and roughly two weeks for a validated deformation and first decision.",
      "design_template": "counterfactual-synthesis",
      "entry_point_2_requirements": "Measurement: gravity-aligned interface curvature. Confusable artifacts: volume, attenuation, positioning, reconstruction, interpolation, and loculation; the design fixes or gates each.",
      "scores": {
        "clarity": {"value": 5, "why": "The claimed physical quantity and fixed-volume contrast are precise."},
        "identifiability": {"value": 4, "why": "The construction isolates curvature if the demanding realism gate passes."},
        "medical_relevance": {"value": 3, "why": "It explains a common finding score but has indirect immediate clinical consequence."},
        "interest": {"value": 5, "why": "A model reading fluid physics rather than amount is surprising and generalizable."},
        "mechanism_clarity": {"value": 5, "why": "Curvature, gravity-aligned interface, and measurement are fully named."},
        "prior_legwork": {"value": 4, "why": "The model pipeline and segmentation precedents already exist."},
        "feasibility": {"value": 3, "why": "Capped; independent realistic curvature editing is uninspected."},
        "data_readiness": {"value": 4, "why": "The exact model and CT cohort are already operational in the program."},
        "evaluation_readiness": {"value": 4, "why": "Signed paired slopes and geometry invariants are explicit."},
        "negative_result_value": {"value": 4, "why": "A gated null decisively separates volume from interface shape use."},
        "novelty_confidence": {"value": 3, "why": "Capped pending shape-radiomics audit."},
        "regret": {"value": 4, "why": "Existing inference makes the hard geometry gate worth testing."}
      },
      "mode_c_priority_score": 4.45,
      "unverified_claims": ["A CT effusion segmenter transfers to CT-RATE", "Curvature is independently editable in native support", "No prior fixed-volume meniscus intervention exists"],
      "plain_pitch": "Fluid around the lung does not just occupy space; gravity gives its upper surface a smooth curved edge called a meniscus. The model may recognize that edge rather than simply measuring how much fluid is present. We would reshape the same number of fluid voxels to make the meniscus flatter or steeper while leaving density and the rest of the scan unchanged. If the score follows curvature, the model is using a recognizable piece of fluid physics."
    },
    {
      "id": "scout-019-c05",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The opening in the diaphragm inside the hiatal-hernia score",
      "question": "Is CT-CLIP's hiatal-hernia score using diaphragmatic crural separation rather than herniated stomach volume?",
      "deliverable_sentence": "CT-CLIP's hiatal-hernia score is using widening of the esophageal hiatus between the diaphragmatic crura.",
      "rung": "Targets rung 1 with within-patient state changes that separate aperture width from herniated volume; rung 2 requires phase, gastric distension, positioning, reconstruction, and crop controls; rung 3 needs a confirmatory aperture-specific intervention or naturally discordant pairs.",
      "rung_reached": "At most rung 1 from longitudinal discordant pairs; an aperture-specific, realism-gated intervention is required to move to rung 3.",
      "X_measurement": "Segment diaphragm/crura and esophagus/stomach, define the esophageal-hiatus plane, and measure transverse intercrural distance, hiatus area, and crural thickness in millimetres. These are direct geometric quantities. Compute-today test: YES in principle with automatic organ/diaphragm segmentation, without reader judgment; robust crural segmentation on low-dose chest CT is the keystone gate.",
      "suspected_signal": "The right and left diaphragmatic crura form a muscular aperture. Chronic widening and thinning reduce the mechanical barrier to trans-hiatal stomach migration. A whole-volume model may read the fixed anatomical aperture even when herniated stomach volume changes with respiration or gastric filling.",
      "use_vs_association": "Wider hiatus and larger hernia usually co-occur, so cross-sectional regression is insufficient. The primary screen seeks same-patient scans where herniated stomach volume changes substantially but crural separation is stable, and the converse; score changes across those discordant natural states distinguish aperture use from sac-volume use.",
      "keystone_prerequisite": "CT-RATE contains enough same-patient repeat scans with full diaphragmatic coverage and naturally discordant changes in intercrural distance versus herniated-stomach volume, without simultaneous protocol/crop changes that reproduce the same discordance.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The ledger verifies repeat patients in CT-RATE, and the hiatal-hernia head exists. I am still assuming the load-bearing fact that the repeats contain adequate natural discordance and crural coverage. Repeat scans alone are only the nearest easy fact and do not establish the design.",
      "dies_like_prior": "It risks idea-009's IDENTIFIABILITY_FAILURE because aperture width and hernia volume are mechanically coupled. Unlike idea-009, it requires prespecified within-patient discordant support before inference. It is distinct from scout-015-c04, which asks whether the score uses a continuous air tunnel; this candidate names the muscular aperture and tests it against stomach volume. Annotation provenance does not enter the primary readout.",
      "closest_prior_work": "CT-CLIP/CT-RATE and the frozen ClassFine checkpoint are verified locally through idea-004. Quantitative hiatus/crural measurements exist in surgical and CT literature, but the exact primary measurement citation and any AI attribution work require formal audit. Scout-015-c04 is the closest internal candidate and tests luminal air continuity, not crural separation.",
      "existing_assets": "Operational CT-CLIP pipeline; CT-RATE repeat-session metadata; TotalSegmentator stomach/esophagus context masks; deterministic geometry once crura are segmented.",
      "smallest_decisive_experiment": "Stage 0 runs crural/upper-stomach segmentation on all repeat patients, audits crop coverage, and counts pairs in four prespecified cells: stable aperture/changing hernia volume, changing aperture/stable volume, concordant change, and stable/stable. Freeze minimum support and measurement repeatability before scores. Only if both discordant cells pass support, compare within-patient hiatal-hernia score changes using a two-predictor errors-in-variables model; stable/stable pairs estimate the noise floor.",
      "standing_confounds_addressed": "Within-patient analysis removes fixed site, habitus, prevalence, and referral pathway. Metadata matching/stratification addresses vendor, protocol, reconstruction, and positioning; tensor-coverage audits address cropping. Label leakage cannot vary within a model-to-itself pair. Gastric distension and inspiration remain plausible time-varying alternatives and are measured via stomach gas volume and lung volume rather than assumed away.",
      "alternative_explanations": ["The score follows herniated stomach volume, not aperture width; the discordant cells are designed to distinguish them.", "Inspiration changes both crural geometry and model framing; lung volume and final-tensor coverage are explicit gates/covariates.", "Gastric gas, not anatomy, drives the score; gas volume is measured and stable-gas sensitivity analysis is prespecified."],
      "anticipated_negative": "If adequate discordant support exists and score changes follow only hernia volume, that is a decisive negative for aperture use and a positive competing explanation. Absence of discordant support is an interpretable feasibility kill, not a biological negative.",
      "cross_domain": {"borrowed_construct": "Structural mechanics: a muscular aperture whose span and thickness govern resistance to organ passage.", "implied_measurement": "Intercrural distance, hiatus area, and crural thickness contrasted with trans-hiatal stomach volume.", "what_changes_if_dropped": "Without the aperture-mechanics framing, there is no reason to measure crural span separately from hernia size or demand discordant natural states; the study would collapse into routine severity correlation."},
      "remaining_legwork": "About one week for segmentation/coverage and discordance census; if support passes, one further week to the paired score analysis.",
      "design_template": "longitudinal-within-subject",
      "entry_point_2_requirements": "Measurement: intercrural distance/hiatus area. Confusable artifacts: herniated volume, inspiration, gastric gas, positioning, protocol, and final-tensor crop; all are measured or gated.",
      "scores": {
        "clarity": {"value": 4, "why": "The competing quantities are clear; the natural-discordance estimand needs sufficient support."},
        "identifiability": {"value": 3, "why": "Discordant within-patient states help, but time-varying anatomy and measurement error remain."},
        "medical_relevance": {"value": 3, "why": "It explains a common score and could distinguish structural susceptibility from transient herniation."},
        "interest": {"value": 4, "why": "A model reading the muscular gateway rather than the herniated organ is unexpected."},
        "mechanism_clarity": {"value": 5, "why": "Aperture span, thickness, organ passage, and measurements are specific."},
        "prior_legwork": {"value": 4, "why": "Model, repeated scans, and contextual segmenters already exist."},
        "feasibility": {"value": 3, "why": "Capped; natural discordance and crural segmentation are not inspected."},
        "data_readiness": {"value": 4, "why": "The CT-RATE repeat cohort and model pipeline are program assets."},
        "evaluation_readiness": {"value": 3, "why": "The geometry is clear but measurement-error modeling and support thresholds need freezing."},
        "negative_result_value": {"value": 4, "why": "Following volume rather than aperture is a decisive competing explanation if support passes."},
        "novelty_confidence": {"value": 3, "why": "Capped pending hiatus-measurement and attribution audit."},
        "regret": {"value": 3, "why": "The Stage-0 census is cheap on existing repeats, though success is uncertain."}
      },
      "mode_c_priority_score": 3.9,
      "unverified_claims": ["Robust automatic crural segmentation on CT-RATE", "Adequate natural discordance in repeat scans", "Primary validation citation for automated hiatus measurement", "No prior model attribution to crural separation"],
      "plain_pitch": "A hiatal hernia occurs when the opening in the diaphragm around the food pipe becomes wide enough for stomach to pass upward. The visible amount of stomach above the diaphragm can change with breathing and filling, while the muscular opening may remain wide. By comparing repeat scans from the same person where these two quantities change differently, we can ask whether the model reads the opening itself or merely the amount of displaced stomach. A positive result would name the anatomical gateway behind the score."
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

