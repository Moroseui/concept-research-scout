You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-017
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


===== evidence/ledger_digest_baseline.md =====
# Ledger digest -- charter: baseline (auto-generated; scores are scoped to this charter only)

91 tracked ideas in this charter. Latest state per idea; full history in ledger.jsonl.

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

- **scout-015-c04** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.5, audited 2026-08-17] -- The continuous air tunnel inside the hiatal-hernia score
- **scout-015-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.5, audited 2026-08-17] -- The lung-opacity score may be reading gravity
- **scout-013-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.4, audited 2026-08-15] -- Collateral failure written in the cortical veins
- **scout-012-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.2, audited 2026-08-15] -- The dilated esophagus inside the fibrosis score
- **scout-013-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.1, audited 2026-08-15] -- The vessel map inside the mosaic-attenuation score
- **scout-016-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.0, audited 2026-08-18] -- Name the noise the kernel writes: the mediator behind idea 004's reconstruction shifts
- **scout-010-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.9, audited 2026-08-12] -- CXR-Age put back together from parts a radiologist can measure
- **scout-014-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.8, audited 2026-08-16] -- Redraw the same airway walls with a sharper pencil: does the peribronchial-thickening score follow Pi10?
- **scout-012-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.7, audited 2026-08-15] -- The race signal in chest CT: measure the bone density everyone names and nobody measured
- **scout-016-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.7, audited 2026-08-18] -- The mortality model is wearing the patient's hardware
- ... and 49 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- regional-substitution: 12
- conditional-observational: 12
- counterfactual-synthesis: 8
- representation-erasure: 6
- longitudinal-within-subject: 5
- natural-paired: 3
- model-output-perturbation: 3
- regional-removal: 3
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


===== evidence/librarian_proposals.md =====


===== ideas/scout-017/README.md =====
# Scouting cycle 017

Tracks: baseline


===== ideas/scout-017/candidates_all.json =====
{
  "cycle": 17,
  "charter": null,
  "tracks": [
    "baseline"
  ],
  "notes": {
    "mode_c_score_missing": 2
  },
  "candidates": [
    {
      "id": "scout-017-c01",
      "search_mode": "A",
      "entry_point": 1,
      "title": "The crushed vertebra inside the mortality score",
      "question": "Is a chest-radiograph mortality model using vertebral compression fractures as a visible record of skeletal frailty?",
      "deliverable_sentence": "The mortality model is using vertebral compression fractures as a visible record of skeletal frailty.",
      "rung": "Targets rung 1 by controlled fracture-shape restoration; rung 2 requires edit-realism and acquisition/site controls; rung 3 requires replication across a second mortality model.",
      "rung_reached": "Rung 1 if fracture restoration changes risk beyond matched sham edits; replication and subtype specificity would move it toward rung 3.",
      "unfinished_story": "The primary CXR-risk study established long-term mortality stratification from one radiograph but stopped before testing whether a named, automatically measurable frailty lesion mediates that behavior. Vertebral deformity is the missing physician-legible measurement and paired intervention.",
      "X_measurement": "Automatically segment visible thoracic vertebral bodies, measure anterior, middle, and posterior height, and compute Genant-style height ratios; a compression phenotype is a prespecified continuous wedge/biconcavity/crush deformity score. This is a geometric measurement requiring no reader. Compute-today test: YES on any radiograph with adequately visible vertebrae, subject to a visibility gate. Anchor: CXR-risk primary study, PMID 31322692, DOI 10.1001/jamanetworkopen.2019.7416, https://pubmed.ncbi.nlm.nih.gov/31322692/.",
      "suspected_signal": "Vertebral collapse records osteoporosis, falls, cancer, glucocorticoid exposure, and frailty. A long-term mortality network can exploit this high-contrast, persistent skeletal record even when its clinical target is ostensibly global health.",
      "use_vs_association": "Fracture carriers having higher risk is only association. The confirmatory comparison restores only the collapsed vertebral contour and trabecular texture, then compares risk change with equal-area sham restoration in intact vertebrae; the within-image response is the use test.",
      "keystone_prerequisite": "A frozen, obtainable CXR-risk checkpoint or faithful released implementation can produce continuous mortality scores on a public cohort containing enough adequately exposed thoracic vertebrae.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The paper verifies the model and performance, not obtainable weights or vertebral visibility in its released images. Those two facts jointly constitute the real keystone and require direct repository and image inspection.",
      "dies_like_prior": "It risks DATA_ACCESS like idea-018 if the checkpoint is not obtainable, but differs because that failure is made the first Stage-0 stop. Annotation provenance does not enter the paired readout. Edit validity resembles idea-006, but the intervention is local and must pass matched-sham and discriminator gates rather than deleting a patient.",
      "closest_prior_work": "Lu et al. established long-term mortality prediction from one chest radiograph (PMID 31322692; DOI 10.1001/jamanetworkopen.2019.7416) but did not test vertebral morphometry as the used signal. Automated vertebral-fracture work establishes measurability; exact detector and licensing remain to be audited. No novelty claim is made before that audit.",
      "existing_assets": "Published CXR-risk architecture and cohort description; public chest-radiograph corpora; established vertebral morphometry formulas; 2D inference and editing fit a single GPU.",
      "smallest_decisive_experiment": "Stage 0 verifies checkpoint loading and identifies at least 80 fracture-positive, adequately exposed cases automatically. On a frozen subset, restore fracture geometry with a structure-preserving editor, reject edits detectable above a prespecified margin, and compare paired mortality-score changes against intact-vertebra shams.",
      "standing_confounds_addressed": "Within-image pairing fixes scanner, vendor, protocol, site, positioning, habitus, prevalence, referral pathway, and label leakage. It does not automatically exclude a generic response to spine edits; matched intact-vertebra shams and fracture-subtype dose response address that. External validity across sites remains unresolved.",
      "alternative_explanations": [
        "The model reacts to any vertebral edit; intact-vertebra shams test this.",
        "The edited region changes overlying lung texture; a lung-preservation checksum and spine-only alpha mask test this.",
        "Fracture score is actually a proxy for kyphosis; conditioning on global spinal curvature separates them observationally, but complete separation may remain difficult."
      ],
      "anticipated_negative": "Decisive if the checkpoint, measurement, and editor all pass gates and fracture restoration stays within the sham distribution; otherwise sensitivity-limited.",
      "remaining_legwork": "Two days for checkpoint/visibility inspection; roughly one week for morphometry and editor gates; first scientific decision in two weeks.",
      "design_template": "regional-substitution",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "One named lesion, one geometric measurement, and one paired intervention."
        },
        "identifiability": {
          "value": 4,
          "why": "Local paired restoration removes cohort confounding, though kyphosis and edit effects remain controls rather than impossibilities."
        },
        "medical_relevance": {
          "value": 4,
          "why": "It would explain a mortality score through a familiar frailty marker with deployment implications."
        },
        "interest": {
          "value": 4,
          "why": "A hidden skeletal frailty readout inside a chest model is both plausible and surprising."
        },
        "prior_legwork": {
          "value": 3,
          "why": "The anchor model and morphometry literature exist, but the runnable checkpoint is unverified."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped because the checkpoint/visibility keystone is uninspected."
        },
        "data_readiness": {
          "value": 3,
          "why": "Public images exist; exact compatibility and weights need inspection."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "Paired score shifts, edit discrimination, and geometric preservation are directly measurable."
        },
        "negative_result_value": {
          "value": 4,
          "why": "A gated paired null rejects use of this named lesion for the frozen model."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped and held pending a formal audit of mortality-model interpretation and fracture editing."
        },
        "regret": {
          "value": 4,
          "why": "It is a compact test of an obvious-in-hindsight frailty marker."
        }
      },
      "unverified_claims": [
        "Public runnable CXR-risk weights",
        "Adequate vertebral visibility and fracture prevalence",
        "A validated automatic lateralized vertebral morphometry tool for frontal radiographs",
        "Novelty of the intervention"
      ],
      "plain_pitch": "A single chest X-ray can predict who is more likely to die years later, even though that is not a judgment radiologists normally make from the image. This study asks whether the model is reading crushed vertebrae, a visible sign of osteoporosis and frailty. We would automatically measure those deformities, digitally restore them while leaving the rest of the image fixed, and see whether the model's risk score falls.",
      "track": "baseline",
      "charter": null
    },
    {
      "id": "scout-017-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The plug inside the thickened-airway score",
      "question": "Is CT-CLIP's peribronchial-thickening score using airway mucus-plug volume rather than airway-wall thickness?",
      "deliverable_sentence": "The peribronchial-thickening score is using airway mucus-plug burden.",
      "rung": "Targets rung 1 by selective plug removal and insertion; rung 2 requires separation from wall thickness, kernel, and disease severity; rung 3 follows only if the automatic plug masks generalize to the target scans.",
      "rung_reached": "Rung 1 conditionally; independent validation of the mucus measurement on CT-RATE-like scans would support rung 3 naming.",
      "unasked_question": "The classifier supplies a wall-thickening score and the new measurement paper supplies annotation-free plug masks, but the two literatures have not been connected to ask whether the score's physical referent is wall or lumen.",
      "X_measurement": "Use the simulation-trained annotation-free nnU-Net to segment plugs and compute total plug volume, count, airway-generation distribution, and occluded-lumen fraction. The 2026 primary paper reports an expert-test sensitivity of 0.837 and explicitly limits validation beyond thin-slice noncontrast chronic-obstructive-lung-disease scans: PMID 41749693, https://pubmed.ncbi.nlm.nih.gov/41749693/. Compute-today test: YES only if weights are released and the protocol gate passes; otherwise the card stops.",
      "suspected_signal": "A mucus-filled airway creates a tubular or branching soft-tissue opacity adjacent to a bronchial wall. A report-supervised model may map that appearance to peribronchial thickening even though the physical quantity is intraluminal secretion, not wall thickening.",
      "use_vs_association": "Plug burden correlating with the score is inadequate. Remove segmented plugs by lumen-consistent inpainting while preserving walls, and separately insert synthetic plugs into clear airways while preserving wall geometry; a signed bidirectional dose response distinguishes use from association.",
      "keystone_prerequisite": "The published annotation-free plug segmenter has obtainable weights and retains adequate precision on CT-RATE-like thickness and reconstruction after a protocol-stratified external gate.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearest verified fact is published performance on 200 chronic-obstructive-lung-disease scans. I am still assuming weight release and transfer to CT-RATE; the paper itself warns generalizability is unestablished, so this is the real keystone.",
      "dies_like_prior": "It resembles BUS-BRA idea-003 only superficially: CT-CLIP has a real named output and X is generated independently, not extracted from missing lexicon labels. It could die DATA_ACCESS if the plug weights are absent, or IDENTIFIABILITY_FAILURE if wall and lumen cannot be edited independently; both are explicit gates.",
      "closest_prior_work": "The plug-segmentation paper (PMID 41749693) measures X but does not decode a report-supervised classifier. Scout-014-c02 asks whether the same score follows Pi10 wall thickness; this candidate is a deliberate competing-mechanism test, with lumen content rather than wall geometry as X. The exact delta is a bidirectional plug intervention with wall preservation.",
      "existing_assets": "Frozen CT-CLIP v2 ClassFine pipeline and public CT-RATE validation volumes; published synthetic-plug generation procedure; public airway segmentation tooling.",
      "smallest_decisive_experiment": "Stage 0 inspects weights and evaluates detector stability across slice thickness/kernel strata without using report labels. If passed, take 40 high-burden and 40 clear-airway scans, create graded removal/insertion pairs, verify wall-thickness invariance and edit realism, and measure the frozen peribronchial-thickening logit response.",
      "standing_confounds_addressed": "Within-scan edits fix scanner, vendor, site, protocol, reconstruction, position, habitus, prevalence, referral, and labels. Kernel and thickness still affect plug detection and are handled by a stratified Stage-0 gate. Wall-thickness change is checked directly on edited tensors. Label leakage cannot explain a bidirectional within-image response.",
      "alternative_explanations": [
        "The editor changes airway-wall edges; wall-thickness and edge-energy checks test this.",
        "The model responds to generic added soft tissue; vessel-shaped and non-airway tubular shams test specificity.",
        "Detector errors select severe chronic lung disease; confirmatory inference is within-image, but detector failure can still invalidate the study."
      ],
      "anticipated_negative": "Decisive after detector and edit gates: no signed response rejects mucus-plug use by this head. Failure of transfer or realism is uninterpretable and stops before science.",
      "remaining_legwork": "One to three days for repository and transfer inspection; one week for editor gates; decision in about two weeks.",
      "design_template": "counterfactual-synthesis",
      "entry_point_2_requirements": "Measurement is automated plug volume and occluded-lumen fraction. The confusable artifact is airway-wall thickness and kernel-dependent edge sharpness, measured and held fixed.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "Two competing named airway quantities are separated by bidirectional edits."
        },
        "identifiability": {
          "value": 4,
          "why": "Removal plus insertion and wall-preservation controls isolate lumen content if the editor passes."
        },
        "medical_relevance": {
          "value": 4,
          "why": "It changes the clinical meaning of a named abnormality score and may reveal systematic mislabeling."
        },
        "interest": {
          "value": 5,
          "why": "A wall-thickening head reading secretions is a crisp and consequential category error."
        },
        "prior_legwork": {
          "value": 4,
          "why": "The classifier pipeline and a new annotation-free measurement method exist."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped because weight release and target-domain transfer are uninspected."
        },
        "data_readiness": {
          "value": 4,
          "why": "CT-RATE and CT-CLIP are already operational locally; the segmenter is the only open asset."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "Signed dose response and wall-preservation metrics are straightforward."
        },
        "negative_result_value": {
          "value": 4,
          "why": "A valid bidirectional null sharply favors the competing wall-thickness story."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped pending search for plug-aware classifier interpretation."
        },
        "regret": {
          "value": 5,
          "why": "A newly available annotation-free X closes a previously difficult measurement gap."
        }
      },
      "unverified_claims": [
        "Public segmenter weights",
        "Transfer to CT-RATE",
        "Adequate thin-slice subset size",
        "Novelty of decoding mucus plugs in this head"
      ],
      "plain_pitch": "A chest-CT model produces a score that sounds like thickened airway walls. But mucus stuck inside an airway can look very similar. A new automatic tool can measure mucus plugs without asking a radiologist, so we can remove plugs while preserving the wall, add them back in graded amounts, and see which physical thing the score follows.",
      "track": "baseline",
      "charter": null
    },
    {
      "id": "scout-017-c03",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The detour veins inside the cirrhosis prediction",
      "question": "Is an abdominal-CT cirrhosis model using portosystemic collateral-vein volume as a record of portal hypertension?",
      "deliverable_sentence": "The cirrhosis model is using portosystemic collateral-vein burden.",
      "rung": "Targets rung 1 with selective representation erasure; rung 2 requires separation from contrast phase, splenomegaly, ascites, and liver morphology; rung 3 requires validated automatic collateral segmentation.",
      "rung_reached": "Rung 1 if a separable collateral representation is causally necessary for the score; physiological interpretation remains portal-hypertension-associated until pressure validation exists.",
      "unasked_question": "Abdominal foundation-model work reports cirrhosis performance, while portal-hypertension imaging quantifies collateral vessels; neither asks whether those detour veins are a necessary internal feature of the model's decision.",
      "X_measurement": "Segment the portal vein and predefined collateral territories, skeletonize vessels, and compute collateral vessel volume, total centerline length, maximum caliber, and paraumbilical/recanalized-umbilical continuity. These are deterministic image quantities. Compute-today test: YES in contrast-enhanced CT if an open vessel segmenter passes a held-out anatomy gate; otherwise stop. Model anchor is Merlin, arXiv:2407.11399 (official preprint identifier; checkpoint availability must be inspected).",
      "suspected_signal": "Portal hypertension opens and enlarges venous bypass routes around the esophagus, stomach, spleen, and abdominal wall. Those vessels are a physical record of pressure-driven rerouting and may be more specific to clinically consequential cirrhosis than liver texture alone.",
      "use_vs_association": "Conditional association is only Stage 0. Cross-fit a collateral subspace conditional on liver shape, spleen volume, ascites volume, body habitus, and contrast phase, then erase that subspace and compare the cirrhosis-logit drop with equal-rank random and nuisance erasures on untouched patients.",
      "keystone_prerequisite": "Collateral burden is independently decodable from frozen Merlin features after conditioning on contrast phase and the major cirrhosis correlates; without joint support and separability, erasure cannot identify collateral use.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Checking only that Merlin and vessel segmenters exist would repeat the wrong-keystone error. The load-bearing fact is conditional separability on a sufficiently large joint-support cohort, which can only be established in Stage 0.",
      "dies_like_prior": "It most resembles idea-009, killed because anatomy and disease covaried without support. This card differs by making conditional feature separability the keystone and a stopping gate, not an assumed premise. It also resembles scout-015-c03 (portal-vein caliber); the new X is collateral detour volume, a different vascular compartment and representation-erasure grammar.",
      "closest_prior_work": "Merlin establishes a generalist 3D abdominal-CT model (arXiv:2407.11399). Portal-hypertension imaging literature measures varices/collaterals but, to current knowledge, does not test their necessity in a cirrhosis model. Scout-015-c03 asks about portal-vein caliber, not collateral networks. No novelty conclusion is asserted before audit.",
      "existing_assets": "Released Merlin materials reported by the primary preprint; public contrast-enhanced abdominal CT candidates; TotalSegmentator-style organ masks for nuisance measures; standard vessel centerline formulas.",
      "smallest_decisive_experiment": "On 300 contrast-enhanced scans, freeze patients and compute X plus nuisance measures, then cross-fit conditional collateral probes from Merlin features. Stop if support or incremental decoding fails. If passed, erase the collateral subspace and compare the cirrhosis score with random, portal-vein, spleen, and liver-shape erasures.",
      "standing_confounds_addressed": "Contrast phase, protocol, vendor, and reconstruction enter stratified probes; site is held out; positioning and habitus enter normalization; splenomegaly, ascites, and liver shape are explicit nuisance directions. Disease prevalence and referral affect external validity but not held-out erasure comparisons. Label leakage remains possible in how Merlin learned cirrhosis, but cannot by itself explain selective dependence on an independently measured collateral direction.",
      "alternative_explanations": [
        "The direction encodes contrast phase; phase probes and erasure controls address this.",
        "It encodes global vascular enhancement or body habitus; portal-vein and random vascular directions test that.",
        "Collateral segmentation mistakes bowel wall or nodes for vessels; anatomy and connectivity gates are mandatory."
      ],
      "anticipated_negative": "A conditional-decoding failure is decisive that the model does not separately encode this X on the available support. An erasure null after a passed gate is decisive against use; a failed segmentation gate is uninterpretable.",
      "remaining_legwork": "Three days to inspect checkpoint and compatible cohorts; about two weeks for segmentation and conditional-support gate.",
      "design_template": "representation-erasure",
      "entry_point_2_requirements": "Measurement is collateral-vessel volume and centerline length. The confusable artifacts are contrast phase and global vascular enhancement, explicitly modeled and erased as controls.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "The X is precise, though the eligible collateral territories need freezing."
        },
        "identifiability": {
          "value": 3,
          "why": "Conditional separability is an honest gate, but portal-hypertension features may lack joint support."
        },
        "medical_relevance": {
          "value": 5,
          "why": "Collateralization is a clinically consequential sign linked to portal hypertension."
        },
        "interest": {
          "value": 4,
          "why": "It asks whether the model reads the vascular consequence rather than the liver surface."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Model and segmentation ingredients exist but have not been assembled or inspected."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped by the uninspected separability keystone."
        },
        "data_readiness": {
          "value": 3,
          "why": "Candidate public cohorts exist; contrast-phase and model compatibility remain uncertain."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Conditional probing is standard, but collateral segmentation needs custom gates."
        },
        "negative_result_value": {
          "value": 4,
          "why": "The staged gate yields a clean model-level negative if separability or use fails."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped pending dedicated portal-hypertension AI search."
        },
        "regret": {
          "value": 4,
          "why": "The vascular detour is a more physician-legible mechanism than generic liver texture."
        }
      },
      "unverified_claims": [
        "Merlin cirrhosis output and checkpoint usability",
        "Open collateral-vessel segmentation on compatible CT",
        "Adequate joint support across contrast and morphology",
        "Novelty"
      ],
      "plain_pitch": "When pressure rises behind a scarred liver, blood opens detour veins around the abdomen. Those enlarged veins are a concrete, measurable sign of advanced disease. This study asks whether an abdominal-CT model recognizes cirrhosis by reading those detours, after separating them from liver shape, spleen size, fluid, and contrast timing.",
      "track": "baseline",
      "charter": null
    },
    {
      "id": "scout-017-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The spine's calendar inside chest-radiograph age",
      "question": "Is a chest-radiograph age model using thoracic intervertebral-disc narrowing as a calendar written in the spine?",
      "deliverable_sentence": "The chest-radiograph age model is using thoracic intervertebral-disc narrowing.",
      "rung": "Mode C target is rung 1 through regional removal plus preservation controls; rung 2 requires separation from vertebral osteophytes, projection, and body size; rung 3 requires replication across age models.",
      "rung_reached": "Rung 1 at best in this cycle; replication and a validated disc-height measurement would move it to rung 3.",
      "X_measurement": "Automatically localize thoracic vertebral endplates and compute each intervertebral projected disc-height ratio normalized by adjacent vertebral-body height, then summarize median height and cranio-caudal slope. It is a deterministic geometric measurement on a new scan. Compute-today test: YES where endplates are visible; no annotator is required. A primary age-model study reports age prediction from healthy adult chest radiographs with mean absolute error 2.1 years: PMID 34640449, https://pubmed.ncbi.nlm.nih.gov/34640449/.",
      "suspected_signal": "Disc desiccation and degeneration reduce intervertebral height over decades. The thoracic spine occupies a stable central strip in every chest radiograph, so a network may use its repeated spacing pattern as a high-signal biological clock.",
      "use_vs_association": "Age association is guaranteed. Mask or synthesize only the intervertebral spaces while preserving vertebral bodies, then compare the age shift with matched rib-space and vertebral-body shams; a monotone response to graded height restoration is the use signature.",
      "keystone_prerequisite": "Projected thoracic disc-height ratios are measured reproducibly enough on frontal chest radiographs, despite overlap and magnification, to support a graded intervention independent of projection.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearby fact is that a chest-radiograph age model performs well. The real assumption is that frontal projected disc spaces are a stable measurement rather than a positioning artifact; if Stage 0 repeat-view reliability is poor, the candidate dies.",
      "dies_like_prior": "It does not depend on annotation provenance. It could die IDENTIFIABILITY_FAILURE like idea-009 if disc height cannot be separated from global degenerative change; the bidirectional localized edit and shams reduce but may not eliminate that. It overlaps scout-010-c01 conceptually, but that candidate decomposes CXR-Age broadly; this card makes a new, single-X causal claim and should be rejected as duplicate if the novelty audit shows disc spacing was already one of its frozen components.",
      "closest_prior_work": "The age-model primary paper (PMID 34640449) establishes the behavior, not disc-height use. CXR-Age decomposition is already in the backlog as scout-010-c01; exact overlap is the mandatory first novelty check. Degenerative-disc measurement literature motivates X but identifiers remain unpinned.",
      "existing_assets": "Public chest radiographs, reported age-model methods, vertebral localization tooling, cheap 2D measurements and inference.",
      "smallest_decisive_experiment": "First audit scout-010-c01 for duplication. If distinct, verify repeat-view disc-height reliability on paired radiographs. Then on 60 high-narrowing cases, apply three graded disc-space restorations, preserve bone pixels exactly, and compare model-age shifts with rib-space and vertebral-body shams.",
      "standing_confounds_addressed": "Paired edits fix scanner, vendor, site, protocol, position, habitus, prevalence, referral, and labels. Projection remains a measurement confound and is tested through repeat views. Osteophytes and vertebral density remain correlated alternatives addressed by pixel-preservation and separate shams.",
      "alternative_explanations": [
        "The model uses osteophytes, not disc height; bone pixels are frozen.",
        "The edit changes generic horizontal spacing; rib-space shams test this.",
        "Disc height is a projection artifact; repeat-view reliability is the keystone gate."
      ],
      "anticipated_negative": "Decisive only after repeatability and editor gates; otherwise sensitivity-limited.",
      "cross_domain": {
        "borrowed_construct": "Dendrochronology and mechanical wear: repeated spacings serve as a cumulative load calendar",
        "implied_measurement": "The multilevel disc-height vector and its cranio-caudal pattern, not a single disc",
        "what_changes_if_dropped": "Without the calendar analogy the multilevel pattern and graded age-restoration prediction disappear; the study would become a generic spine ablation. The analogy therefore dictates the dose variable, though it is not evidence."
      },
      "remaining_legwork": "One day for duplicate audit; three days for repeat-view reliability; two weeks to a paired result if both gates pass.",
      "design_template": "regional-removal",
      "entry_point_2_requirements": "Measurement is normalized multilevel disc height. The confusable artifact is projection and magnification, checked with repeat views and vertebral normalization.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "A specific multilevel geometry and intervention are named."
        },
        "identifiability": {
          "value": 3,
          "why": "Projection and co-located degeneration remain meaningful risks."
        },
        "medical_relevance": {
          "value": 3,
          "why": "It clarifies biological-age models but has indirect clinical consequence."
        },
        "interest": {
          "value": 4,
          "why": "A spine-spacing clock is intuitive and testable."
        },
        "mechanism_clarity": {
          "value": 5,
          "why": "Disc degeneration, normalized height, and graded restoration form a complete physical mechanism."
        },
        "prior_legwork": {
          "value": 2,
          "why": "The model behavior exists, but checkpoint, duplicate status, and measurement reliability are unverified."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped; 2D work is cheap but the keystone is uninspected."
        },
        "data_readiness": {
          "value": 3,
          "why": "Images are available but model assets are uncertain."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Paired response is simple; projection reliability needs a custom threshold."
        },
        "negative_result_value": {
          "value": 3,
          "why": "A valid null closes this X for a model, but does not explain what replaces it."
        },
        "novelty_confidence": {
          "value": 2,
          "why": "A nearby backlog candidate creates substantial duplicate risk."
        },
        "regret": {
          "value": 2,
          "why": "Interesting, but the portfolio may already contain the broader version."
        }
      },
      "unverified_claims": [
        "Runnable age checkpoint",
        "Frontal disc-height reliability",
        "Non-duplication with scout-010-c01",
        "Adequate intervention realism"
      ],
      "plain_pitch": "The spaces between spinal bones tend to narrow over decades. Because the spine is visible down the middle of every chest X-ray, an age-predicting model may be using those repeated spaces as a calendar. We would automatically measure them, digitally restore their height in small steps, and ask whether the predicted age moves backward.",
      "track": "baseline",
      "charter": null
    },
    {
      "id": "scout-017-c05",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The vascular street map inside lung-cancer risk",
      "question": "Is a lung-cancer risk model using pulmonary-vessel branch-point density as a measure of vascular pruning?",
      "deliverable_sentence": "The lung-cancer risk model is using pulmonary-vessel branch-point density.",
      "rung": "Mode C targets rung 1 with longitudinal within-subject change and conditional feature tests; rung 2 requires separating pruning from emphysema, inspiration, kernel, and smoking; rung 3 requires causal replication or a valid vessel-preserving intervention.",
      "rung_reached": "Rung 1 only if within-person vessel-network change predicts within-person model-score change beyond emphysema and nodule burden.",
      "X_measurement": "Segment the pulmonary vasculature, skeletonize it, and compute branch points per liter of lung, total vessel length by caliber, and fractal dimension, excluding a fixed perinodular radius. These are deterministic measurements on a new CT. Compute-today test: YES using public vessel segmentation methods, conditional on a segmentation quality gate.",
      "suspected_signal": "Smoking and emphysema destroy distal pulmonary vessels; tumor-associated angiogenesis can reorganize local vessels. A risk model may integrate this lung-wide vascular pruning signal even when nodules are removed, making the vascular tree a biological exposure and susceptibility record.",
      "use_vs_association": "A cross-sectional correlation would repeat idea-009's failure. Use a frozen longitudinal screening cohort: ask whether within-person change in vessel branch density tracks within-person Sybil risk change after conditioning on emphysema percentage, lung volume, nodule burden, kernel, and interval; then test whether vessel-network features are decodable from risk-model representations conditional on those variables. This reaches rung 1 only weakly; a causal vessel edit is required to move higher.",
      "keystone_prerequisite": "There is enough within-person change in vessel branch density independent of emphysema, inspiration, reconstruction, and nodule evolution to identify its relation to risk-score change.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Verifying longitudinal scans and a vessel segmenter would be adjacent facts. The real keystone is independent within-person support after nuisance conditioning; this is unknown and is the Stage-0 decision.",
      "dies_like_prior": "It deliberately resembles idea-009, killed for IDENTIFIABILITY_FAILURE around pulmonary branching geometry. The difference is that this uses longitudinal within-person deltas, excludes perinodular vessels, and declares the independent-change support as a stopping keystone. If the support is absent, it dies the same way and must not be rescued rhetorically.",
      "closest_prior_work": "Sybil established lung-cancer prediction from low-dose CT (Mikhael et al., J Clin Oncol 2023, DOI 10.1200/JCO.22.01345; identifier to verify in audit). Pulmonary vascular pruning is measured in chronic obstructive lung disease, but its use by lung-cancer risk models is unverified. Idea-009 is the closest internal prior and is an explicit warning, not evidence of novelty.",
      "existing_assets": "Longitudinal screening CT cohorts used by Sybil; pulmonary-vessel segmentation and skeletonization methods; formulaic network measures; model inference fits available compute.",
      "smallest_decisive_experiment": "On 150 people with two protocol-compatible screening scans, freeze preprocessing and compute within-person deltas for branch density, emphysema percentage, lung volume, nodule burden, and Sybil risk. Require a prespecified residual variance and effective-sample-size gate before estimating the conditional association; stop if it fails.",
      "standing_confounds_addressed": "Within-person design removes fixed sex, ancestry, chronic habitus, site tendency, and referral pathway. Explicit delta covariates address kernel, protocol, reconstruction, inspiration, emphysema, and nodule evolution. Scanner/vendor changes remain stratification variables. Label leakage is absent from the primary score-to-self delta, but prevalence and smoking trajectory remain possible time-varying explanations.",
      "alternative_explanations": [
        "Emphysema causes both pruning and risk change; emphysema delta is conditioned on but measurement error remains.",
        "Inspiration changes apparent branch density; normalize by lung volume and require matched inspiration proxies.",
        "Nodule angiogenesis changes local vessels; exclude perinodular regions and analyze them separately."
      ],
      "anticipated_negative": "A failed independent-support gate decisively kills the obtainable design, not the biological hypothesis. A conditional null after passing the gate is sensitivity-limited because observational measurement error remains.",
      "cross_domain": {
        "borrowed_construct": "Network science: branch-point density and fractal dimension quantify the complexity of a transport network",
        "implied_measurement": "Lung-volume-normalized branch counts, length by caliber, and fractal dimension",
        "what_changes_if_dropped": "Without network science the X collapses to total vessel volume, losing the explicit pruning/topology hypothesis and the per-caliber branch analysis. The analogy changes the measured variable and is therefore operational."
      },
      "remaining_legwork": "Two days for cohort and checkpoint inspection; about one week for a 30-person support pilot; full first decision in three weeks.",
      "design_template": "longitudinal-within-subject",
      "entry_point_2_requirements": "Measurement is pulmonary branch-point density and vessel length by caliber. The confusable artifacts are emphysema, inspiration, reconstruction, and nodule angiogenesis, all measured explicitly.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "The X and delta design are precise, though several network summaries compete."
        },
        "identifiability": {
          "value": 3,
          "why": "Within-person deltas are stronger than cross-section, but emphysema measurement error may survive."
        },
        "medical_relevance": {
          "value": 4,
          "why": "It could name a lung-wide biological risk signal rather than a nodule shortcut."
        },
        "interest": {
          "value": 5,
          "why": "A vascular pruning map inside cancer risk is unexpected and mechanistically rich."
        },
        "mechanism_clarity": {
          "value": 4,
          "why": "A named transport-network quantity and biological pathway are specified; causal isolation is incomplete."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Models, cohorts, and vessel methods exist, but joint support is unknown."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped by the uninspected independent-change keystone."
        },
        "data_readiness": {
          "value": 2,
          "why": "Sybil-compatible longitudinal access and checkpoint execution require inspection."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Delta models are standard, but support thresholds must be prespecified."
        },
        "negative_result_value": {
          "value": 3,
          "why": "A support failure kills this design decisively; a scientific null is only sensitivity-limited."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Capped; the vascular-radiomics literature has not been fully audited."
        },
        "regret": {
          "value": 4,
          "why": "The mechanism is strong enough to justify a cheap support pilot despite the prior warning."
        }
      },
      "unverified_claims": [
        "Sybil checkpoint and longitudinal cohort compatibility",
        "Independent within-person vessel change",
        "Vessel segmentation stability across low-dose kernels",
        "Exact Sybil DOI and novelty"
      ],
      "plain_pitch": "The lung's blood vessels form a branching transport network. Smoking-related damage can prune its smallest branches, leaving a measurable record across the whole lung. This study asks whether a lung-cancer risk model uses that vascular street map, by following the same people over time and checking whether changes in branch density track changes in model risk after accounting for emphysema, breathing depth, scan settings, and nodules.",
      "track": "baseline",
      "charter": null
    }
  ]
}


===== ideas/scout-017/run_provenance.json =====
{
  "timestamp": "2026-08-19T06:26:07+00:00",
  "git_commit": "e9dd8dceaf62a9ee6a50d0aa272cc4a089e74099",
  "claude_cli": "2.1.197 (Claude Code)",
  "codex_cli": "codex-cli 0.148.0",
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


===== ideas/scout-017/scout_candidates.json =====
{
  "cycle": "scout-017",
  "date": "2026-08-19",
  "track": "baseline",
  "all_questions": [
    {"n": 1, "question": "Is a chest-radiograph mortality model using vertebral compression fractures as a visible record of skeletal frailty?", "disposition": "DEVELOPED as scout-017-c01"},
    {"n": 2, "question": "Is CT-CLIP's peribronchial-thickening score using airway mucus-plug volume rather than wall thickness?", "disposition": "DEVELOPED as scout-017-c02"},
    {"n": 3, "question": "Is an abdominal-CT cirrhosis model using the volume of portosystemic collateral veins as a pressure record?", "disposition": "DEVELOPED as scout-017-c03"},
    {"n": 4, "question": "Is a chest-radiograph age model using thoracic intervertebral-disc narrowing as a calendar written in the spine?", "disposition": "DEVELOPED as scout-017-c04"},
    {"n": 5, "question": "Is a lung-cancer risk model using pulmonary-vessel branch-point density as the lung's vascular street-map complexity?", "disposition": "DEVELOPED as scout-017-c05"},
    {"n": 6, "question": "Is a pulmonary-edema classifier using azygos-vein diameter as a venous-pressure gauge?", "disposition": "DROPPED: automatic azygos measurement is plausible, but this is too close to the existing inferior-vena-cava and cephalization candidates and adds little portfolio diversity."},
    {"n": 7, "question": "Is a mammography risk model using Cooper-ligament orientation as the breast's load-bearing fabric?", "disposition": "DROPPED (cross-domain mechanics): the X measurement is not yet well-defined independently of dense tissue segmentation, so the compute-today constraint is not met honestly."},
    {"n": 8, "question": "Is a head-CT age model using cranial-suture closure as a skeletal clock?", "disposition": "DROPPED: adult suture closure is measurable, but no frozen public head-CT age checkpoint was identified in the initial primary-source pass."},
    {"n": 9, "question": "Is a pneumonia model using lung heat itself, through the temperature dependence of X-ray attenuation?", "disposition": "DROPPED (obviously wrong but not immediately refutable): any febrile attenuation shift would be smaller than acquisition and hydration effects, making the positive claim unidentifiable."},
    {"n": 10, "question": "Is a pulmonary-embolism model using contrast-mixing entropy as if turbulent flow were dye spreading in a river?", "disposition": "DROPPED (cross-domain fluid mechanics): contrast timing and cardiac output are inseparable from the proposed entropy on ordinary single-phase angiography."}
  ],
  "quota_note": "Exactly 1 Mode A (c01), 2 Mode B (c02-c03), and 2 Mode C (c04-c05). All five are radiology; four use CT or volumetric imaging. No dataset is used more than twice. Zero revivals: no portfolio unblock condition was found to have changed. The set uses five different design templates. Every primary endpoint is a model-to-itself readout and does not require trustworthy clinical labels.",
  "candidates": [
    {
      "id": "scout-017-c01",
      "search_mode": "A",
      "entry_point": 1,
      "title": "The crushed vertebra inside the mortality score",
      "question": "Is a chest-radiograph mortality model using vertebral compression fractures as a visible record of skeletal frailty?",
      "deliverable_sentence": "The mortality model is using vertebral compression fractures as a visible record of skeletal frailty.",
      "rung": "Targets rung 1 by controlled fracture-shape restoration; rung 2 requires edit-realism and acquisition/site controls; rung 3 requires replication across a second mortality model.",
      "rung_reached": "Rung 1 if fracture restoration changes risk beyond matched sham edits; replication and subtype specificity would move it toward rung 3.",
      "unfinished_story": "The primary CXR-risk study established long-term mortality stratification from one radiograph but stopped before testing whether a named, automatically measurable frailty lesion mediates that behavior. Vertebral deformity is the missing physician-legible measurement and paired intervention.",
      "X_measurement": "Automatically segment visible thoracic vertebral bodies, measure anterior, middle, and posterior height, and compute Genant-style height ratios; a compression phenotype is a prespecified continuous wedge/biconcavity/crush deformity score. This is a geometric measurement requiring no reader. Compute-today test: YES on any radiograph with adequately visible vertebrae, subject to a visibility gate. Anchor: CXR-risk primary study, PMID 31322692, DOI 10.1001/jamanetworkopen.2019.7416, https://pubmed.ncbi.nlm.nih.gov/31322692/.",
      "suspected_signal": "Vertebral collapse records osteoporosis, falls, cancer, glucocorticoid exposure, and frailty. A long-term mortality network can exploit this high-contrast, persistent skeletal record even when its clinical target is ostensibly global health.",
      "use_vs_association": "Fracture carriers having higher risk is only association. The confirmatory comparison restores only the collapsed vertebral contour and trabecular texture, then compares risk change with equal-area sham restoration in intact vertebrae; the within-image response is the use test.",
      "keystone_prerequisite": "A frozen, obtainable CXR-risk checkpoint or faithful released implementation can produce continuous mortality scores on a public cohort containing enough adequately exposed thoracic vertebrae.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The paper verifies the model and performance, not obtainable weights or vertebral visibility in its released images. Those two facts jointly constitute the real keystone and require direct repository and image inspection.",
      "dies_like_prior": "It risks DATA_ACCESS like idea-018 if the checkpoint is not obtainable, but differs because that failure is made the first Stage-0 stop. Annotation provenance does not enter the paired readout. Edit validity resembles idea-006, but the intervention is local and must pass matched-sham and discriminator gates rather than deleting a patient.",
      "closest_prior_work": "Lu et al. established long-term mortality prediction from one chest radiograph (PMID 31322692; DOI 10.1001/jamanetworkopen.2019.7416) but did not test vertebral morphometry as the used signal. Automated vertebral-fracture work establishes measurability; exact detector and licensing remain to be audited. No novelty claim is made before that audit.",
      "existing_assets": "Published CXR-risk architecture and cohort description; public chest-radiograph corpora; established vertebral morphometry formulas; 2D inference and editing fit a single GPU.",
      "smallest_decisive_experiment": "Stage 0 verifies checkpoint loading and identifies at least 80 fracture-positive, adequately exposed cases automatically. On a frozen subset, restore fracture geometry with a structure-preserving editor, reject edits detectable above a prespecified margin, and compare paired mortality-score changes against intact-vertebra shams.",
      "standing_confounds_addressed": "Within-image pairing fixes scanner, vendor, protocol, site, positioning, habitus, prevalence, referral pathway, and label leakage. It does not automatically exclude a generic response to spine edits; matched intact-vertebra shams and fracture-subtype dose response address that. External validity across sites remains unresolved.",
      "alternative_explanations": ["The model reacts to any vertebral edit; intact-vertebra shams test this.", "The edited region changes overlying lung texture; a lung-preservation checksum and spine-only alpha mask test this.", "Fracture score is actually a proxy for kyphosis; conditioning on global spinal curvature separates them observationally, but complete separation may remain difficult."],
      "anticipated_negative": "Decisive if the checkpoint, measurement, and editor all pass gates and fracture restoration stays within the sham distribution; otherwise sensitivity-limited.",
      "remaining_legwork": "Two days for checkpoint/visibility inspection; roughly one week for morphometry and editor gates; first scientific decision in two weeks.",
      "design_template": "regional-substitution",
      "scores": {
        "clarity": {"value": 5, "why": "One named lesion, one geometric measurement, and one paired intervention."},
        "identifiability": {"value": 4, "why": "Local paired restoration removes cohort confounding, though kyphosis and edit effects remain controls rather than impossibilities."},
        "medical_relevance": {"value": 4, "why": "It would explain a mortality score through a familiar frailty marker with deployment implications."},
        "interest": {"value": 4, "why": "A hidden skeletal frailty readout inside a chest model is both plausible and surprising."},
        "prior_legwork": {"value": 3, "why": "The anchor model and morphometry literature exist, but the runnable checkpoint is unverified."},
        "feasibility": {"value": 3, "why": "Capped because the checkpoint/visibility keystone is uninspected."},
        "data_readiness": {"value": 3, "why": "Public images exist; exact compatibility and weights need inspection."},
        "evaluation_readiness": {"value": 4, "why": "Paired score shifts, edit discrimination, and geometric preservation are directly measurable."},
        "negative_result_value": {"value": 4, "why": "A gated paired null rejects use of this named lesion for the frozen model."},
        "novelty_confidence": {"value": 3, "why": "Capped and held pending a formal audit of mortality-model interpretation and fracture editing."},
        "regret": {"value": 4, "why": "It is a compact test of an obvious-in-hindsight frailty marker."}
      },
      "unverified_claims": ["Public runnable CXR-risk weights", "Adequate vertebral visibility and fracture prevalence", "A validated automatic lateralized vertebral morphometry tool for frontal radiographs", "Novelty of the intervention"],
      "plain_pitch": "A single chest X-ray can predict who is more likely to die years later, even though that is not a judgment radiologists normally make from the image. This study asks whether the model is reading crushed vertebrae, a visible sign of osteoporosis and frailty. We would automatically measure those deformities, digitally restore them while leaving the rest of the image fixed, and see whether the model's risk score falls."
    },
    {
      "id": "scout-017-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The plug inside the thickened-airway score",
      "question": "Is CT-CLIP's peribronchial-thickening score using airway mucus-plug volume rather than airway-wall thickness?",
      "deliverable_sentence": "The peribronchial-thickening score is using airway mucus-plug burden.",
      "rung": "Targets rung 1 by selective plug removal and insertion; rung 2 requires separation from wall thickness, kernel, and disease severity; rung 3 follows only if the automatic plug masks generalize to the target scans.",
      "rung_reached": "Rung 1 conditionally; independent validation of the mucus measurement on CT-RATE-like scans would support rung 3 naming.",
      "unasked_question": "The classifier supplies a wall-thickening score and the new measurement paper supplies annotation-free plug masks, but the two literatures have not been connected to ask whether the score's physical referent is wall or lumen.",
      "X_measurement": "Use the simulation-trained annotation-free nnU-Net to segment plugs and compute total plug volume, count, airway-generation distribution, and occluded-lumen fraction. The 2026 primary paper reports an expert-test sensitivity of 0.837 and explicitly limits validation beyond thin-slice noncontrast chronic-obstructive-lung-disease scans: PMID 41749693, https://pubmed.ncbi.nlm.nih.gov/41749693/. Compute-today test: YES only if weights are released and the protocol gate passes; otherwise the card stops.",
      "suspected_signal": "A mucus-filled airway creates a tubular or branching soft-tissue opacity adjacent to a bronchial wall. A report-supervised model may map that appearance to peribronchial thickening even though the physical quantity is intraluminal secretion, not wall thickening.",
      "use_vs_association": "Plug burden correlating with the score is inadequate. Remove segmented plugs by lumen-consistent inpainting while preserving walls, and separately insert synthetic plugs into clear airways while preserving wall geometry; a signed bidirectional dose response distinguishes use from association.",
      "keystone_prerequisite": "The published annotation-free plug segmenter has obtainable weights and retains adequate precision on CT-RATE-like thickness and reconstruction after a protocol-stratified external gate.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearest verified fact is published performance on 200 chronic-obstructive-lung-disease scans. I am still assuming weight release and transfer to CT-RATE; the paper itself warns generalizability is unestablished, so this is the real keystone.",
      "dies_like_prior": "It resembles BUS-BRA idea-003 only superficially: CT-CLIP has a real named output and X is generated independently, not extracted from missing lexicon labels. It could die DATA_ACCESS if the plug weights are absent, or IDENTIFIABILITY_FAILURE if wall and lumen cannot be edited independently; both are explicit gates.",
      "closest_prior_work": "The plug-segmentation paper (PMID 41749693) measures X but does not decode a report-supervised classifier. Scout-014-c02 asks whether the same score follows Pi10 wall thickness; this candidate is a deliberate competing-mechanism test, with lumen content rather than wall geometry as X. The exact delta is a bidirectional plug intervention with wall preservation.",
      "existing_assets": "Frozen CT-CLIP v2 ClassFine pipeline and public CT-RATE validation volumes; published synthetic-plug generation procedure; public airway segmentation tooling.",
      "smallest_decisive_experiment": "Stage 0 inspects weights and evaluates detector stability across slice thickness/kernel strata without using report labels. If passed, take 40 high-burden and 40 clear-airway scans, create graded removal/insertion pairs, verify wall-thickness invariance and edit realism, and measure the frozen peribronchial-thickening logit response.",
      "standing_confounds_addressed": "Within-scan edits fix scanner, vendor, site, protocol, reconstruction, position, habitus, prevalence, referral, and labels. Kernel and thickness still affect plug detection and are handled by a stratified Stage-0 gate. Wall-thickness change is checked directly on edited tensors. Label leakage cannot explain a bidirectional within-image response.",
      "alternative_explanations": ["The editor changes airway-wall edges; wall-thickness and edge-energy checks test this.", "The model responds to generic added soft tissue; vessel-shaped and non-airway tubular shams test specificity.", "Detector errors select severe chronic lung disease; confirmatory inference is within-image, but detector failure can still invalidate the study."],
      "anticipated_negative": "Decisive after detector and edit gates: no signed response rejects mucus-plug use by this head. Failure of transfer or realism is uninterpretable and stops before science.",
      "remaining_legwork": "One to three days for repository and transfer inspection; one week for editor gates; decision in about two weeks.",
      "design_template": "counterfactual-synthesis",
      "entry_point_2_requirements": "Measurement is automated plug volume and occluded-lumen fraction. The confusable artifact is airway-wall thickness and kernel-dependent edge sharpness, measured and held fixed.",
      "scores": {
        "clarity": {"value": 5, "why": "Two competing named airway quantities are separated by bidirectional edits."},
        "identifiability": {"value": 4, "why": "Removal plus insertion and wall-preservation controls isolate lumen content if the editor passes."},
        "medical_relevance": {"value": 4, "why": "It changes the clinical meaning of a named abnormality score and may reveal systematic mislabeling."},
        "interest": {"value": 5, "why": "A wall-thickening head reading secretions is a crisp and consequential category error."},
        "prior_legwork": {"value": 4, "why": "The classifier pipeline and a new annotation-free measurement method exist."},
        "feasibility": {"value": 3, "why": "Capped because weight release and target-domain transfer are uninspected."},
        "data_readiness": {"value": 4, "why": "CT-RATE and CT-CLIP are already operational locally; the segmenter is the only open asset."},
        "evaluation_readiness": {"value": 4, "why": "Signed dose response and wall-preservation metrics are straightforward."},
        "negative_result_value": {"value": 4, "why": "A valid bidirectional null sharply favors the competing wall-thickness story."},
        "novelty_confidence": {"value": 3, "why": "Capped pending search for plug-aware classifier interpretation."},
        "regret": {"value": 5, "why": "A newly available annotation-free X closes a previously difficult measurement gap."}
      },
      "unverified_claims": ["Public segmenter weights", "Transfer to CT-RATE", "Adequate thin-slice subset size", "Novelty of decoding mucus plugs in this head"],
      "plain_pitch": "A chest-CT model produces a score that sounds like thickened airway walls. But mucus stuck inside an airway can look very similar. A new automatic tool can measure mucus plugs without asking a radiologist, so we can remove plugs while preserving the wall, add them back in graded amounts, and see which physical thing the score follows."
    },
    {
      "id": "scout-017-c03",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The detour veins inside the cirrhosis prediction",
      "question": "Is an abdominal-CT cirrhosis model using portosystemic collateral-vein volume as a record of portal hypertension?",
      "deliverable_sentence": "The cirrhosis model is using portosystemic collateral-vein burden.",
      "rung": "Targets rung 1 with selective representation erasure; rung 2 requires separation from contrast phase, splenomegaly, ascites, and liver morphology; rung 3 requires validated automatic collateral segmentation.",
      "rung_reached": "Rung 1 if a separable collateral representation is causally necessary for the score; physiological interpretation remains portal-hypertension-associated until pressure validation exists.",
      "unasked_question": "Abdominal foundation-model work reports cirrhosis performance, while portal-hypertension imaging quantifies collateral vessels; neither asks whether those detour veins are a necessary internal feature of the model's decision.",
      "X_measurement": "Segment the portal vein and predefined collateral territories, skeletonize vessels, and compute collateral vessel volume, total centerline length, maximum caliber, and paraumbilical/recanalized-umbilical continuity. These are deterministic image quantities. Compute-today test: YES in contrast-enhanced CT if an open vessel segmenter passes a held-out anatomy gate; otherwise stop. Model anchor is Merlin, arXiv:2407.11399 (official preprint identifier; checkpoint availability must be inspected).",
      "suspected_signal": "Portal hypertension opens and enlarges venous bypass routes around the esophagus, stomach, spleen, and abdominal wall. Those vessels are a physical record of pressure-driven rerouting and may be more specific to clinically consequential cirrhosis than liver texture alone.",
      "use_vs_association": "Conditional association is only Stage 0. Cross-fit a collateral subspace conditional on liver shape, spleen volume, ascites volume, body habitus, and contrast phase, then erase that subspace and compare the cirrhosis-logit drop with equal-rank random and nuisance erasures on untouched patients.",
      "keystone_prerequisite": "Collateral burden is independently decodable from frozen Merlin features after conditioning on contrast phase and the major cirrhosis correlates; without joint support and separability, erasure cannot identify collateral use.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Checking only that Merlin and vessel segmenters exist would repeat the wrong-keystone error. The load-bearing fact is conditional separability on a sufficiently large joint-support cohort, which can only be established in Stage 0.",
      "dies_like_prior": "It most resembles idea-009, killed because anatomy and disease covaried without support. This card differs by making conditional feature separability the keystone and a stopping gate, not an assumed premise. It also resembles scout-015-c03 (portal-vein caliber); the new X is collateral detour volume, a different vascular compartment and representation-erasure grammar.",
      "closest_prior_work": "Merlin establishes a generalist 3D abdominal-CT model (arXiv:2407.11399). Portal-hypertension imaging literature measures varices/collaterals but, to current knowledge, does not test their necessity in a cirrhosis model. Scout-015-c03 asks about portal-vein caliber, not collateral networks. No novelty conclusion is asserted before audit.",
      "existing_assets": "Released Merlin materials reported by the primary preprint; public contrast-enhanced abdominal CT candidates; TotalSegmentator-style organ masks for nuisance measures; standard vessel centerline formulas.",
      "smallest_decisive_experiment": "On 300 contrast-enhanced scans, freeze patients and compute X plus nuisance measures, then cross-fit conditional collateral probes from Merlin features. Stop if support or incremental decoding fails. If passed, erase the collateral subspace and compare the cirrhosis score with random, portal-vein, spleen, and liver-shape erasures.",
      "standing_confounds_addressed": "Contrast phase, protocol, vendor, and reconstruction enter stratified probes; site is held out; positioning and habitus enter normalization; splenomegaly, ascites, and liver shape are explicit nuisance directions. Disease prevalence and referral affect external validity but not held-out erasure comparisons. Label leakage remains possible in how Merlin learned cirrhosis, but cannot by itself explain selective dependence on an independently measured collateral direction.",
      "alternative_explanations": ["The direction encodes contrast phase; phase probes and erasure controls address this.", "It encodes global vascular enhancement or body habitus; portal-vein and random vascular directions test that.", "Collateral segmentation mistakes bowel wall or nodes for vessels; anatomy and connectivity gates are mandatory."],
      "anticipated_negative": "A conditional-decoding failure is decisive that the model does not separately encode this X on the available support. An erasure null after a passed gate is decisive against use; a failed segmentation gate is uninterpretable.",
      "remaining_legwork": "Three days to inspect checkpoint and compatible cohorts; about two weeks for segmentation and conditional-support gate.",
      "design_template": "representation-erasure",
      "entry_point_2_requirements": "Measurement is collateral-vessel volume and centerline length. The confusable artifacts are contrast phase and global vascular enhancement, explicitly modeled and erased as controls.",
      "scores": {
        "clarity": {"value": 4, "why": "The X is precise, though the eligible collateral territories need freezing."},
        "identifiability": {"value": 3, "why": "Conditional separability is an honest gate, but portal-hypertension features may lack joint support."},
        "medical_relevance": {"value": 5, "why": "Collateralization is a clinically consequential sign linked to portal hypertension."},
        "interest": {"value": 4, "why": "It asks whether the model reads the vascular consequence rather than the liver surface."},
        "prior_legwork": {"value": 3, "why": "Model and segmentation ingredients exist but have not been assembled or inspected."},
        "feasibility": {"value": 3, "why": "Capped by the uninspected separability keystone."},
        "data_readiness": {"value": 3, "why": "Candidate public cohorts exist; contrast-phase and model compatibility remain uncertain."},
        "evaluation_readiness": {"value": 3, "why": "Conditional probing is standard, but collateral segmentation needs custom gates."},
        "negative_result_value": {"value": 4, "why": "The staged gate yields a clean model-level negative if separability or use fails."},
        "novelty_confidence": {"value": 3, "why": "Capped pending dedicated portal-hypertension AI search."},
        "regret": {"value": 4, "why": "The vascular detour is a more physician-legible mechanism than generic liver texture."}
      },
      "unverified_claims": ["Merlin cirrhosis output and checkpoint usability", "Open collateral-vessel segmentation on compatible CT", "Adequate joint support across contrast and morphology", "Novelty"],
      "plain_pitch": "When pressure rises behind a scarred liver, blood opens detour veins around the abdomen. Those enlarged veins are a concrete, measurable sign of advanced disease. This study asks whether an abdominal-CT model recognizes cirrhosis by reading those detours, after separating them from liver shape, spleen size, fluid, and contrast timing."
    },
    {
      "id": "scout-017-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The spine's calendar inside chest-radiograph age",
      "question": "Is a chest-radiograph age model using thoracic intervertebral-disc narrowing as a calendar written in the spine?",
      "deliverable_sentence": "The chest-radiograph age model is using thoracic intervertebral-disc narrowing.",
      "rung": "Mode C target is rung 1 through regional removal plus preservation controls; rung 2 requires separation from vertebral osteophytes, projection, and body size; rung 3 requires replication across age models.",
      "rung_reached": "Rung 1 at best in this cycle; replication and a validated disc-height measurement would move it to rung 3.",
      "X_measurement": "Automatically localize thoracic vertebral endplates and compute each intervertebral projected disc-height ratio normalized by adjacent vertebral-body height, then summarize median height and cranio-caudal slope. It is a deterministic geometric measurement on a new scan. Compute-today test: YES where endplates are visible; no annotator is required. A primary age-model study reports age prediction from healthy adult chest radiographs with mean absolute error 2.1 years: PMID 34640449, https://pubmed.ncbi.nlm.nih.gov/34640449/.",
      "suspected_signal": "Disc desiccation and degeneration reduce intervertebral height over decades. The thoracic spine occupies a stable central strip in every chest radiograph, so a network may use its repeated spacing pattern as a high-signal biological clock.",
      "use_vs_association": "Age association is guaranteed. Mask or synthesize only the intervertebral spaces while preserving vertebral bodies, then compare the age shift with matched rib-space and vertebral-body shams; a monotone response to graded height restoration is the use signature.",
      "keystone_prerequisite": "Projected thoracic disc-height ratios are measured reproducibly enough on frontal chest radiographs, despite overlap and magnification, to support a graded intervention independent of projection.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearby fact is that a chest-radiograph age model performs well. The real assumption is that frontal projected disc spaces are a stable measurement rather than a positioning artifact; if Stage 0 repeat-view reliability is poor, the candidate dies.",
      "dies_like_prior": "It does not depend on annotation provenance. It could die IDENTIFIABILITY_FAILURE like idea-009 if disc height cannot be separated from global degenerative change; the bidirectional localized edit and shams reduce but may not eliminate that. It overlaps scout-010-c01 conceptually, but that candidate decomposes CXR-Age broadly; this card makes a new, single-X causal claim and should be rejected as duplicate if the novelty audit shows disc spacing was already one of its frozen components.",
      "closest_prior_work": "The age-model primary paper (PMID 34640449) establishes the behavior, not disc-height use. CXR-Age decomposition is already in the backlog as scout-010-c01; exact overlap is the mandatory first novelty check. Degenerative-disc measurement literature motivates X but identifiers remain unpinned.",
      "existing_assets": "Public chest radiographs, reported age-model methods, vertebral localization tooling, cheap 2D measurements and inference.",
      "smallest_decisive_experiment": "First audit scout-010-c01 for duplication. If distinct, verify repeat-view disc-height reliability on paired radiographs. Then on 60 high-narrowing cases, apply three graded disc-space restorations, preserve bone pixels exactly, and compare model-age shifts with rib-space and vertebral-body shams.",
      "standing_confounds_addressed": "Paired edits fix scanner, vendor, site, protocol, position, habitus, prevalence, referral, and labels. Projection remains a measurement confound and is tested through repeat views. Osteophytes and vertebral density remain correlated alternatives addressed by pixel-preservation and separate shams.",
      "alternative_explanations": ["The model uses osteophytes, not disc height; bone pixels are frozen.", "The edit changes generic horizontal spacing; rib-space shams test this.", "Disc height is a projection artifact; repeat-view reliability is the keystone gate."],
      "anticipated_negative": "Decisive only after repeatability and editor gates; otherwise sensitivity-limited.",
      "cross_domain": {"borrowed_construct": "Dendrochronology and mechanical wear: repeated spacings serve as a cumulative load calendar", "implied_measurement": "The multilevel disc-height vector and its cranio-caudal pattern, not a single disc", "what_changes_if_dropped": "Without the calendar analogy the multilevel pattern and graded age-restoration prediction disappear; the study would become a generic spine ablation. The analogy therefore dictates the dose variable, though it is not evidence."},
      "remaining_legwork": "One day for duplicate audit; three days for repeat-view reliability; two weeks to a paired result if both gates pass.",
      "design_template": "regional-removal",
      "entry_point_2_requirements": "Measurement is normalized multilevel disc height. The confusable artifact is projection and magnification, checked with repeat views and vertebral normalization.",
      "scores": {
        "clarity": {"value": 4, "why": "A specific multilevel geometry and intervention are named."},
        "identifiability": {"value": 3, "why": "Projection and co-located degeneration remain meaningful risks."},
        "medical_relevance": {"value": 3, "why": "It clarifies biological-age models but has indirect clinical consequence."},
        "interest": {"value": 4, "why": "A spine-spacing clock is intuitive and testable."},
        "mechanism_clarity": {"value": 5, "why": "Disc degeneration, normalized height, and graded restoration form a complete physical mechanism."},
        "prior_legwork": {"value": 2, "why": "The model behavior exists, but checkpoint, duplicate status, and measurement reliability are unverified."},
        "feasibility": {"value": 3, "why": "Capped; 2D work is cheap but the keystone is uninspected."},
        "data_readiness": {"value": 3, "why": "Images are available but model assets are uncertain."},
        "evaluation_readiness": {"value": 3, "why": "Paired response is simple; projection reliability needs a custom threshold."},
        "negative_result_value": {"value": 3, "why": "A valid null closes this X for a model, but does not explain what replaces it."},
        "novelty_confidence": {"value": 2, "why": "A nearby backlog candidate creates substantial duplicate risk."},
        "regret": {"value": 2, "why": "Interesting, but the portfolio may already contain the broader version."}
      },
      "unverified_claims": ["Runnable age checkpoint", "Frontal disc-height reliability", "Non-duplication with scout-010-c01", "Adequate intervention realism"],
      "plain_pitch": "The spaces between spinal bones tend to narrow over decades. Because the spine is visible down the middle of every chest X-ray, an age-predicting model may be using those repeated spaces as a calendar. We would automatically measure them, digitally restore their height in small steps, and ask whether the predicted age moves backward."
    },
    {
      "id": "scout-017-c05",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The vascular street map inside lung-cancer risk",
      "question": "Is a lung-cancer risk model using pulmonary-vessel branch-point density as a measure of vascular pruning?",
      "deliverable_sentence": "The lung-cancer risk model is using pulmonary-vessel branch-point density.",
      "rung": "Mode C targets rung 1 with longitudinal within-subject change and conditional feature tests; rung 2 requires separating pruning from emphysema, inspiration, kernel, and smoking; rung 3 requires causal replication or a valid vessel-preserving intervention.",
      "rung_reached": "Rung 1 only if within-person vessel-network change predicts within-person model-score change beyond emphysema and nodule burden.",
      "X_measurement": "Segment the pulmonary vasculature, skeletonize it, and compute branch points per liter of lung, total vessel length by caliber, and fractal dimension, excluding a fixed perinodular radius. These are deterministic measurements on a new CT. Compute-today test: YES using public vessel segmentation methods, conditional on a segmentation quality gate.",
      "suspected_signal": "Smoking and emphysema destroy distal pulmonary vessels; tumor-associated angiogenesis can reorganize local vessels. A risk model may integrate this lung-wide vascular pruning signal even when nodules are removed, making the vascular tree a biological exposure and susceptibility record.",
      "use_vs_association": "A cross-sectional correlation would repeat idea-009's failure. Use a frozen longitudinal screening cohort: ask whether within-person change in vessel branch density tracks within-person Sybil risk change after conditioning on emphysema percentage, lung volume, nodule burden, kernel, and interval; then test whether vessel-network features are decodable from risk-model representations conditional on those variables. This reaches rung 1 only weakly; a causal vessel edit is required to move higher.",
      "keystone_prerequisite": "There is enough within-person change in vessel branch density independent of emphysema, inspiration, reconstruction, and nodule evolution to identify its relation to risk-score change.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Verifying longitudinal scans and a vessel segmenter would be adjacent facts. The real keystone is independent within-person support after nuisance conditioning; this is unknown and is the Stage-0 decision.",
      "dies_like_prior": "It deliberately resembles idea-009, killed for IDENTIFIABILITY_FAILURE around pulmonary branching geometry. The difference is that this uses longitudinal within-person deltas, excludes perinodular vessels, and declares the independent-change support as a stopping keystone. If the support is absent, it dies the same way and must not be rescued rhetorically.",
      "closest_prior_work": "Sybil established lung-cancer prediction from low-dose CT (Mikhael et al., J Clin Oncol 2023, DOI 10.1200/JCO.22.01345; identifier to verify in audit). Pulmonary vascular pruning is measured in chronic obstructive lung disease, but its use by lung-cancer risk models is unverified. Idea-009 is the closest internal prior and is an explicit warning, not evidence of novelty.",
      "existing_assets": "Longitudinal screening CT cohorts used by Sybil; pulmonary-vessel segmentation and skeletonization methods; formulaic network measures; model inference fits available compute.",
      "smallest_decisive_experiment": "On 150 people with two protocol-compatible screening scans, freeze preprocessing and compute within-person deltas for branch density, emphysema percentage, lung volume, nodule burden, and Sybil risk. Require a prespecified residual variance and effective-sample-size gate before estimating the conditional association; stop if it fails.",
      "standing_confounds_addressed": "Within-person design removes fixed sex, ancestry, chronic habitus, site tendency, and referral pathway. Explicit delta covariates address kernel, protocol, reconstruction, inspiration, emphysema, and nodule evolution. Scanner/vendor changes remain stratification variables. Label leakage is absent from the primary score-to-self delta, but prevalence and smoking trajectory remain possible time-varying explanations.",
      "alternative_explanations": ["Emphysema causes both pruning and risk change; emphysema delta is conditioned on but measurement error remains.", "Inspiration changes apparent branch density; normalize by lung volume and require matched inspiration proxies.", "Nodule angiogenesis changes local vessels; exclude perinodular regions and analyze them separately."],
      "anticipated_negative": "A failed independent-support gate decisively kills the obtainable design, not the biological hypothesis. A conditional null after passing the gate is sensitivity-limited because observational measurement error remains.",
      "cross_domain": {"borrowed_construct": "Network science: branch-point density and fractal dimension quantify the complexity of a transport network", "implied_measurement": "Lung-volume-normalized branch counts, length by caliber, and fractal dimension", "what_changes_if_dropped": "Without network science the X collapses to total vessel volume, losing the explicit pruning/topology hypothesis and the per-caliber branch analysis. The analogy changes the measured variable and is therefore operational."},
      "remaining_legwork": "Two days for cohort and checkpoint inspection; about one week for a 30-person support pilot; full first decision in three weeks.",
      "design_template": "longitudinal-within-subject",
      "entry_point_2_requirements": "Measurement is pulmonary branch-point density and vessel length by caliber. The confusable artifacts are emphysema, inspiration, reconstruction, and nodule angiogenesis, all measured explicitly.",
      "scores": {
        "clarity": {"value": 4, "why": "The X and delta design are precise, though several network summaries compete."},
        "identifiability": {"value": 3, "why": "Within-person deltas are stronger than cross-section, but emphysema measurement error may survive."},
        "medical_relevance": {"value": 4, "why": "It could name a lung-wide biological risk signal rather than a nodule shortcut."},
        "interest": {"value": 5, "why": "A vascular pruning map inside cancer risk is unexpected and mechanistically rich."},
        "mechanism_clarity": {"value": 4, "why": "A named transport-network quantity and biological pathway are specified; causal isolation is incomplete."},
        "prior_legwork": {"value": 3, "why": "Models, cohorts, and vessel methods exist, but joint support is unknown."},
        "feasibility": {"value": 3, "why": "Capped by the uninspected independent-change keystone."},
        "data_readiness": {"value": 2, "why": "Sybil-compatible longitudinal access and checkpoint execution require inspection."},
        "evaluation_readiness": {"value": 3, "why": "Delta models are standard, but support thresholds must be prespecified."},
        "negative_result_value": {"value": 3, "why": "A support failure kills this design decisively; a scientific null is only sensitivity-limited."},
        "novelty_confidence": {"value": 3, "why": "Capped; the vascular-radiomics literature has not been fully audited."},
        "regret": {"value": 4, "why": "The mechanism is strong enough to justify a cheap support pilot despite the prior warning."}
      },
      "unverified_claims": ["Sybil checkpoint and longitudinal cohort compatibility", "Independent within-person vessel change", "Vessel segmentation stability across low-dose kernels", "Exact Sybil DOI and novelty"],
      "plain_pitch": "The lung's blood vessels form a branching transport network. Smoking-related damage can prune its smallest branches, leaving a measurable record across the whole lung. This study asks whether a lung-cancer risk model uses that vascular street map, by following the same people over time and checking whether changes in branch density track changes in model risk after accounting for emphysema, breathing depth, scan settings, and nodules."
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

