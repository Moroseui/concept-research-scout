You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/045
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

## 2026-08-25 - Round-5 whole-2a review: intake and dispositions

Verdict accepted: approve architecture, fix semantics before consumers.
All five verified defects fixed in 2a-4 (tombstone parity; binding artifact
deps + launcher-as-DAG-edge + pre-run pin staleness + bundle uniqueness;
approval-bound terminal authority; fail-closed contract interface with
containment; receipt provenance restored with configured/effective family).
Coverage-honest verify commands + --require-all; source fingerprints;
honest nulls; AST suite hygiene; CI gates both runners. Deferred per the
reviewer own P1 gates, queued: structured core return (A7), stage-outcome
records (A8), immutable role maps (A10), ledger event ids (A12), forensic
failure checkpoints (A13), override-matrix telemetry, multi-axis diversity
stats. Pushback recorded: the ZIP-based 023 merge hazard dissolved under a
real git merge (performed first, frozen driver preserved byte-identical);
reviewer full-suite timeout was environmental. Merge order adopted:
023 record-result -> frozen-023 hash check -> merge 2a -> author 023
registry + driver_spec -> shadow soak -> read-only consumer flip -> 2b.

## 2026-08-25 - Round-5.5 re-review: intake and closeout (2a-5)

Adopted and shipped, actions 1-8 + 13 + the charter-hardening test:
CI now enforces state-verify --require-all and registry-validate over a
fully materialized 44-idea corpus; registry validation is schema-strict
and fail-closed (closed key sets, type guards, path containment -- a typo
like dependz_on can no longer silently drop a dependency); a pinned node
with a MISSING current contract is STALE, never COMPLETE; COMPLETE is
validation-aware (invalid bundles surface as RESULT_PRESENT); approve-probe
now binds registry_sha256 prospectively; git SHA is computed fresh per
receipt (tool versions stay cached); a receipt-write failure after a
successful invocation fails closed; a numbered idea directory without its
card fails closed; AST hygiene extended to top-level symbols and duplicate
dict keys -- and caught a real pre-existing duplicate (keystone_status) on
first run. Deferred on the reviewer own gates: structured RunResult (A9,
pre-2b), ROLE_BOUND role freezing (A10, pre-consumer-flip), node-addressed
launcher + driver_spec (A11/A12, with post-023 registry work), workflow
helper factoring (A14, cleanup). Adopted for 023: append-only
REGISTRY_RATIFIED retrospective binding; the historical approval is never
rewritten.
## 2026-08-25 - 023 take 6 receipt + staging second-opinion intake (take 7 v2)

Take-6, two layers: (1) the in-flight ~85% run died to a Colab VM recycle
(bare gate line -- a killed VM cannot print FAIL); no defect. (2) The fresh
VM Drive->local copy was size-exact (99022114670) but md5-wrong; run.py
exit-4d correctly. Classified as suspected DriveFS/FUSE read-path
corruption (mechanism not asserted); the stored Drive master is presumed
good from its historical gate pass and is NOT judged through the suspect
path.
External staging review (archived): adopted in full. Kept: generator-level
change, verify-before-extract, one bounded retry, loud refusal, regression
asserts. Changed per review: checksum resolved by exact archive filename;
missing record md5 is a driver-configuration error (fail closed); .part
transfer with atomic promotion; neutral corruption wording; FUSE-mediated
"Drive master arbitration" REMOVED (a suspect witness cannot acquit
itself) -- replaced by classified stop FUSE_LOCALIZATION_INTEGRITY_FAILURE
with origin_direct pre-authorized as the next sanctioned attempt.
Queued to driver_spec (post-023): drive_api_cache as preferred transport
(Drive stays the cache, FUSE leaves the input path), largest_local_scratch
working-volume policy, and a governed driver-revise route so operational
incidents flow to agent-proposed, cross-family-reviewed spec revisions
instead of external patches.

## 2026-08-26 - 023 take 7: FUSE casualty #7; pre-authorized origin_direct pivot executed

Take-7 receipt: on a brand-fresh VM, minutes old, the very first sequential
read of the archive died with OSError 107 (Transport endpoint is not
connected) inside shutil.copyfile -- the loud variant of the read-path
failure, on the simplest possible access pattern. Seven casualties now span
deep trees, empty views, pin re-resolution, silent size-exact corruption,
and outright transport death across four fresh VMs. Threshold met under the
recorded pre-authorization and the external staging review ruling: the big
input leaves FUSE entirely. Take 8 = origin_direct, now a declared
generator mode (--staging-mode): pin, record JSON, and archive all come
directly from the immutable Zenodo record to local scratch (16-way aria2c,
.part -> md5 -> atomic promote, one retry, classified
ORIGIN_DOWNLOAD_INTEGRITY_FAILURE stop). drive_fuse_cache remains available
but transitional; drive_api_cache stays the driver_spec target. The Drive
mount retains only small-file duties (Phase-S read, checkpoints, outputs).

## 2026-08-26 - 023 exit 8: pre-registered unit contingency executed; amendment directive

Take-8 receipt: staging fully solved (aria2c 14 min, checksum and census
passed); the probe stopped at its first scientific act per contract clause
66 -- CBV units are documented nowhere: zero JSON sidecars among the
archive 2,983 members, empty NIfTI descrip fields, and every dataset
descriptor (Zenodo record page, TU/e portal, challenge paper) lists
modalities without units; the icobrain-cva chain implies the convention
but states none. The contract said stop for amendment before outcomes are
read, and it did.

DIRECTIVE for the next probe-build round (amendment authorized, option B,
human gate retained): amend clause 66 so the sole unit-dependent rule
becomes unit-free -- vessel exclusion = voxels with CBV above the
per-patient 98th percentile of finite positive CBV in the map -- recording
in the clause WHY (the payload evidence above) and noting that under the
conventional scale this targets approximately the vessel fraction the
8 mL/100 g cap intended. Update kill-code 104 to mark the unit-failure
contingency executed and retired. Clause 72 is already unit-robust and
must not change. In run.py: implement the percentile exclusion; retire
confirm_cbv_units into a RECORDED finding (identity.json gains
units_documented: false with the evidence summary); change nothing else.
The amendment changes the contract blob: the standing approval goes stale
by design and re-approval follows human review of the diff.

## 2026-08-26 - 023 take 9: checkpoint-identity guard fired correctly; output dirs now blob-scoped

Take-9 receipt: gate passed on the amended blob 468974a7, staging and census
passed silently, and run.py refused at the checkpoint store: the shared
Drive dir 023_C still held take-8 phase_c_cache pinned to the OLD blob
349af5ad and old run.py hash. Fail-closed cache-poisoning prevention
working as designed -- a checkpoint written under one contract/code may
never be consumed under another. Driver fix (one line): OUTPUT_DIR is now
blob-scoped ({idea}_{phase}_{blob12}), mirroring the results-branch scheme,
so each contract era gets a pristine cache and console; superseded dirs
remain as untouched evidence. No probe or contract change; approval stands.

## 2026-08-26 - Pre-registered adjudication for the inf-ratio edge (committed before outcomes are seen)

During the take-10 map pass, two RuntimeWarning classes were observed:
all-NaN neighborhood windows (handled by design: excluded voxels, counted
per case in the checkpoint exclusions record) and overflow in the
rcbf/rcbv division (tiny positive mirror denominators pass valid_den, so
isolated infinite ratios can be admitted to stratum membership, where the
screen is only ratio > 0). Per-case selective repair is FORBIDDEN: the code
is deterministic and uniform, and mixed-provenance case sets are exactly
what the checkpoint identity mechanism prevents.
Pre-registered plan: (1) take 11 completes untouched; its bundle is the
primary result under the approved code. (2) A one-line finiteness
tightening (stratum admission additionally requires finite rcbf and rcbv)
is routed through probe-build with cross-family review, and the map pass
recomputes under the new identity. (3) Interpretation cites BOTH runs: if
they agree, immateriality is demonstrated and the primary stands with the
robustness check noted; if they diverge, the revised run is canonical and
the divergence is reported as a finding. This criterion is committed before
any stratum outcome has been inspected.

## 2026-08-26 - 023 take 10: truncated extracted member + the Drive-artifact mystery closed

Two findings. First, take-10 origin_direct incidentally settled take-6: the
TRUE Zenodo object is 99,014,629,647 bytes (md5-verified); the Drive-cached
wget artifact was 99,022,114,670 -- ~7.5 MB oversized, a Franken-file from
the record-drift era (wget -c declares fully-retrieved whenever local >=
remote), which is why its md5 could never match. origin_direct fully
vindicated. Second, take-10 receipt: staging verified, census passed, map
pass reached case 21 (sub-stroke0043, 20 cases checkpointed) and died on a
TRUNCATED extracted .nii.gz (gzip EOFError; run.py wrapped it honestly as
exit 13). Root cause class: the extraction 7z exit status was unchecked and
the file-count floor cannot see single-member truncation -- count is not
integrity. Driver fix (both staging modes): extraction is now rc-checked
and quiet; a per-member gzip -t sweep follows; bad members are deleted and
re-extracted individually once; a second failure refuses loudly as
EXTRACTION_INTEGRITY_FAILURE naming the files.

## 2026-08-26 - 023 take 11: SOURCE data defect proven; paired-run plan superseded; dual directive

Take-11 receipt: the integrity sweep worked exactly as designed and proved
the truncation is IN THE ARCHIVE: fresh VM, fresh md5-verified download,
rc-clean extraction, exactly one bad member -- sub-stroke0043 ses-01
space-ncct CBF, the same file that killed take 10 -- which failed gzip -t
AGAIN after targeted re-extraction from the verified archive. The member is
size-typical (7.70 MB) with an invalid gzip stream: corrupted before the
dataset creators archived it. Authority split: the driver guarantees
fidelity to the archive (achieved -- it reproduced the defect twice);
content validity is the contract domain. Driver upgraded: the sweep now
arbitrates via 7z t -- stored-CRC-valid members that fail gzip are
announced as SOURCE_MEMBER_DEFECT and tolerated; only true extraction
infidelity refuses.

SUPERSESSION (before any outcomes were seen): the pre-registered paired-run
plan assumed take 11 completes untouched as primary; it cannot -- case 21
blocks on the source defect under current code. Both revisions therefore
fold into ONE canonical run.

DIRECTIVE for the next probe-build round: (a) a case whose required input
is a source-defective member (unreadable gzip from the verified archive)
routes to exclusions.csv with reason source_corrupt_member naming the file,
and the map pass CONTINUES; the summary and interpretation must surface the
excluded count; (b) stratum admission additionally requires finite rcbf and
rcbv (the pre-registered finiteness tightening). Change nothing else. If
the reviewer judges (a) to require a contract amendment (cohort/selection
language), author the amendment in the same round; otherwise the standing
approval holds. Courtesy task queued: report the defective member upstream
to the ISLES 24 maintainers.

## 2026-08-26 - 023 take 12: COMPLETE map pass; pre-registered mirror gate stop (exit 7) with decision-grade evidence

Take-12 receipt: staging flawless (sweep tolerated the known source defect
live); the label-blind map pass completed 100/100 with sub-stroke0043
excluded per policy (99 computed); the run stopped at the frozen mirror
gate: 21/99 patients meet (registration_error <= 1.0 voxel AND
usable_brain_fraction >= 0.90); floor is 90. Evidence from mirror_qc.csv
(label-blind): registration errors are lattice-quantized (median 1.41,
q75 2.00, max 4.36 voxels) -- clinical positioning, not registration
failure; usable-fraction median 0.856 sits below the 0.90 floor; and
NMAE rises MONOTONICALLY with registration error (0.129 / 0.191 / 0.236 /
0.291 / 0.357 across buckets <=1.0 to >2.5), so displacement measurably
degrades mirror fidelity: the gate is doing real epistemics, not
cleanroom strictness. Threshold relaxation is therefore weakly justified;
the supported-subgroup path risks severity-correlated selection. Live
fork: (A) registration-robust redesign (region-level contralateral
reference; identity coordinate is mirror-free and survives) with new
Phase-S calibration and full re-run, or (B) kill with code
MIRROR_PRECONDITION_UNSUPPORTED and harvest (A) as successor idea.
DECISION DEFERRED to the human gate augmented by advisor input
(2026-08-27 meeting): voxelwise-vs-region reference is a domain call.
No PR opened; results-validate red on a stopped bundle is correct
behavior; the record-result and merge train wait on this fork.
Queue item (operator observation): the interpret stage decodes terminal
results only; pre-registered STOPS should generate their own briefing
artifact (gate context + relevant QC tables) -- a stop-report generator
joins the driver_spec-era work list.

## 2026-08-27 - Design queued: stop-report stage (failure-to-analysis routing)

Operator observation, validated by the 023 arc: three pre-registered stops
each produced decision-grade DATA but no decision-grade BRIEFING; all
forensics were ad hoc. Design: stops route to an interpret-variant stage
producing (1) an EXPLANATION record -- gate context + evidence tables,
citation mandate, inputs mechanically restricted to the label-blind
artifacts the stop certifies -- and optionally (2) a CHANGE_PROPOSAL from
a CLOSED vocabulary mapping to existing pipeline edges: AMEND_CONTRACT,
REVISE_PROBE, REDESIGN, KILL, or ESCALATE_ONLY (explicit deferral, a
first-class output -- the 023 mirror fork is the canonical case where any
machine recommendation would overstep a domain judgment). Explanations are
zero-authority; proposals carry base hashes, cannot modify targets,
re-enter every normal gate, and receive cross-family review. Sequencing:
first consumer of the 2b record envelope -- build it as 2b opening move,
after record-result -> 2a merge -> registry -> driver_spec.

## 2026-08-27 - Operator reframe AND DECISION: 023 goes mirror-free; directive for the amendment round

Reframe (operator-caught): idea 023 claim is the joint CBV/MTT compensation
state AT MATCHED FLOW; hemispheric mirroring is idea 021 ("The healthy
hemisphere is the ruler") and entered 023 only as the operationalization of
matched flow. The exit-7 stop is a verdict on a borrowed ruler, not on the
claim, the signal, or the dataset (QC distributions describe ordinary
clinical positioning; neither clinical software nor models require
voxel-mirror symmetry). mirror_qc.csv is harvested as empirical
feasibility evidence FOR idea 021. The conflation passed agent authorship,
cross-family review, and twelve operator takes; caught at the human gate.

DECISION (human gate, 2026-08-27): mirror-free within-patient flow
matching. DIRECTIVE for the next probe-build round: amend the contract so
matched flow = per-patient CBF percentile bands WITHIN the eroded deficit
region (three fixed bands, 0-33 / 33-67 / 67-100 percentile of finite
deficit CBF; deterministic, label-blind, no external reference). REMOVE
the mirror machinery entirely: mirror construction, registration QC, the
exit-7 gate, and mirror-relative ratios; the region definition (Tmax>6s,
erosion, midline band, per-patient p98 vessel exclusion), the identity
coordinate u = log(CBF*MTT/CBV), the identity-residual gate, per-stratum
coverage floors, and the source-corrupt exclusion policy are UNCHANGED.
Phase S must be recalibrated for the new strata (synthetic planted effects
under percentile binning; same detectability-floor logic). Keep gates
minimal: coverage + identity only; introduce no new reference anatomy.
This de-couples 023 from 021 by construction.

## 2026-08-28 - Meeting outcome: dual-track sprint; HU audit ACTIVATED; clinical-scores secondary pre-registered

Advisor meeting (2026-08-27): system-refinement arc APPROVED, and a signal
read from idea 023 requested within the week -> dual track. The previously
drafted parked/strategic-pause entries were never committed and are
superseded by this plan; the refinement arc proceeds in parallel with a
bounded 023 signal sprint.

ACTIVATED DIRECTIVE (tissue-composition audit, previously drafted as
parked; an outcome-reading run is now scheduled, so it applies): before
take 13, a probe revision adds a label-blind per-bin per-style NCCT HU
audit -- during the map pass record, per case, per flow bin, per style
group, the median and IQR of NCCT attenuation over member voxels, into the
per-case cache and a bin_tissue_audit.csv. No estimator changes, no new
gates, run.py only (contract untouched; standing approval holds through
verify). Pre-registered interpretation rule: HU-balanced styles within
bins -> the compensation reading stands; systematic imbalance -> report as
conditional predictive information WITH a tissue-composition caveat and
design a tissue-normalized successor. Rationale: the retired contralateral
mirror was incidentally the tissue-type normalizer (gray-matter baseline
flow ~2-3x white matter); percentile bins do not restore this.

PRE-REGISTERED SECONDARY (advisor side-interest): after the take-13
outcome read and record-result, a patient-level join of census per-patient
aggregates against the dataset clinical outcome scores (phenotype
ses-02 outcome.csv, mRS/NIHSS-type). Clinical scores are outcome labels
and remain behind the same label-blind until that step; no take-13 scope
change; phenotype files staged separately when needed.

Sequence: audit revision -> verify -> mechanical amend-contract from the
mirror-free Phase-S bundle (status PHASE_S_COMPLETE_REQUIRES_AMENDMENT)
-> approve (new blob) -> package take 13 -> outcome read -> record-result
-> interpret -> signal answer.

## 2026-08-28 - Amender sentinel-quoting tolerance (fail-closed drift, resolved system-side)

The mechanical amend-contract refused on the mirror-free contract: the
agent rewrite left three numeric placeholders unquoted while the amender
demanded the quoted byte-form. Correct refusal, wrong rigidity: the
sentinel format is the amender own interface convention, so the tool (not
the contract) was fixed -- both quotings accepted, exactly-one-total and
single-shot semantics unchanged, tested for both styles. The contract was
never hand-edited.

## 2026-08-28 - 2a-state merged to main (gate disposition + refresh receipt)

The reviewer merge gate -- originally "after 023 record-result," re-scoped
to current-arc resolution -- is receipted as satisfied under the
advisor-approved dual-track plan: take 13 (blob 03d4545fe293) was packaged
and in flight at merge time; its record-result follows on landing and
retro-binds via the queued REGISTRY_RATIFIED design. results-validate.yml
is byte-identical across the merge, so the in-flight take is unaffected.

Refresh merge (main -> 2a-state): one conflict, evidence/decisions.md,
both-appended-at-tail; resolved by union (review-intake entries then the
023 arc entries; nothing dropped). scout.py and tests auto-merged. Both
runners green on the merged tree (152). State corpus re-materialized: 43
of 44 byte-identical, ideas/023/state.json alone updated (five
contract_blob pointers -> 03d4545fe293). state-verify --require-all and
registry-validate green. CI steps (compile incl. orchestrator modules,
doctor, both runners, state invariants) reproduced green pre-push.
Post-merge queue unchanged: 023 registry.yaml + REGISTRY_RATIFIED design,
driver_spec.yaml (operator-driver-patch era ends there), shadow soak,
read-only consumer flip.


## 2026-08-28 - Round-6 post-2a review: intake and dispositions

External review of main @ 2725262 plus the post-2a patch plan. Verdict
accepted: 2a stays merged; the plan is directionally sound; the P1
registry must not be authored until registry semantics and schema
containment are corrected. All findings independently re-verified against
the code before intake; every claim confirmed by direct reading, with one
divergence recorded below.

ACCEPTED P0 (blocks the 023 registry):
(1) Node contract semantics: derive_status stales ANY node whose pinned
contract_hash differs from the current idea contract, before consulting
bundle evidence -- so a historical Phase-S pin goes STALE and Phase-C
BLOCKED. Ruling: node.contract_hash means "the immutable approved
contract version governing this node." A node holding a terminal,
validated bundle is judged against its own pin: an approval record for
that hash must exist, the bundle's recorded executed-contract hash must
equal the pin, and consumed-artifact hashes must verify. Only nodes
without terminal evidence track the current contract for staleness.
Durable historical identity needs no new store: the pins are git blob
hashes, retrievable from the object store; approval + bundle provenance
are the proof.
(2) The plan's depends_on example used a bare list; the shipped schema
requires depends_on: {all_of: [{probe: ...}]}. Plan corrected; schema
syntax is henceforth bound from the validator, like every other value.

ACCEPTED P0/P1 (same patch): close the nested schema before the first
production registry -- schema_version == 1 enforced; produces and
artifact output validated as contained relative paths; nested key sets
(depends_on, all_of, artifacts, launcher, upstream_bundle) closed and
typed; contract_hash format-checked; canonical path normalization before
uniqueness; validation refuses BEFORE any status derivation consumes
registry paths. Reviewer-demonstrated traversal (produces/output with
..) and schema_version: 999 both currently pass -- confirmed in code.

ACCEPTED P1: (a) registry-status CLI omits the bundle validator that the
state-materialize path injects, so a terminal-looking invalid bundle can
print COMPLETE -- all status consumers route through one
validation-aware path; COMPLETE never derives from summary text alone.
(b) The state source fingerprint omits the result-status inputs that
determine registry node statuses -- fold summary/manifest and
consumed-artifact hashes into materialization.sources before
registry-backed state gains consumer authority. (c) approval.stale is
False when the current contract is MISSING -- missing current contract
plus historical approval becomes stale/invalid before the consumer flip.

RATIFICATION MECHANICS (accepted, strengthens the draft): ordering proof
is repository ancestry, not timestamps. REGISTRY_RATIFIED becomes a
dedicated append-only governance-event artifact (not a latest-wins
ledger row) binding idea, registry sha256, approval artifact sha256s,
covered contract hashes, operator decision identity, git commit, and a
stable event id; activation is a human-merged PR (same authority model
as record-result); record-result refuses unless the required
ratification artifact is present and valid in its checked-out tree.
Historical failed C takes stay OUT of the DAG: registry is the
scientific dependency graph; attempts and stops live in
receipts/results/decisions.

SEQUENCING (accepted): structured RunResult + stage-outcome records pull
forward from the 2b batch to land BEFORE stop-report/design-review --
new governance stages will not be built on LAST_RUN mutation and print
semantics. Soak becomes coverage-based (zero state-verify divergence
across the window; clean rematerialization on multiple independent
commits; several real lifecycle mutations across more than one idea; at
least one real registry-backed node transition; one synthetic
hand-edited-state refusal; ROLE_BOUND active) with seven green events as
a floor, not the definition. Advisory coupling confirmed at
approve-time, outcome-neutral; the minimal advisory/event schema lands
before design-review emits production advisories.

DRIVER-SPEC REVISIONS (accepted for P3): the spec references the
approved dataset identity (dataset_ref by hash) rather than restating
record/md5/bytes as a second editable authority; drive_api_cache is
implemented and tested before it may become preferred -- origin_direct
remains the proven heavy-input path; largest_local scratch with a
minimum-free-bytes floor; tool/prerequisite failures become a named
DRIVER_PREREQUISITE_FAILURE stop; staging tests move from
string-presence to executable policy/renderer tests; the audit packet
maps FINAL established incident explanations (e.g., the Drive master was
7.5 MB oversized -- the earlier same-size-corruption working diagnosis
is superseded and must not freeze into policy).

RECORDED WITH NUANCE:
(d) Full-suite certification: the reviewer's environment could not
complete the full runs or reach the public repo. On record here: both
runners green (152) locally on 2725262, and CI success for 2725262,
1f03e59, and 3be88ae confirmed via the Actions API.
(e) Isolated TestDebate: the reviewer's 1-failed reproduction did not
reproduce in this environment (4/4 pass) -- the defect is latent and
order/environment-dependent. The unhygienic mechanism (fixture
sys.path.insert + importlib.reload with rmtree-only teardown, no
sys.modules restoration) is confirmed in the test code and will be fixed
regardless: centralized fixture-import lifecycle plus an
isolated/shuffled selection gate.

TAKE-13 ORDERING RULE (adopted, per reviewer): the record-result path
for take 13 does NOT block on registry work. If a valid bundle lands
before ratification machinery exists, it imports through the existing
approved path and the DAG is ratified retrospectively afterward. Result
identity binding outranks governance ordering.

REVISED NEAR SEQUENCE: R1 registry semantic + schema hardening (with the
counterexample regression: historical-approved S remains COMPLETE while
current-approved C depends on it) -> R2 state-view fixes + test-fixture
hygiene + P2 cleanups (docstring, INVALID_ROW taxonomy note, action
pinning) -> R3 023 registry + PR-gated ancestry-bound REGISTRY_RATIFIED
-> M1 take-13 record-result/interpret whenever the bundle lands -> R4
structured RunResult + stage-outcome records -> driver_spec -> ROLE_BOUND
-> coverage-based soak -> consumer flip -> stop-report -> design-review
-> advisory register -> gate calibration -> 2b remainder -> 2c.


## 2026-08-28 - R1 landed: registry semantic + schema hardening (round-6 P0s)

contract_hash now means the immutable approved contract GOVERNING the
node. Nodes without terminal evidence track the current contract (pin
mismatch = STALE, unchanged). A node holding a terminal result is judged
against its own pin: the pin must be attested (HUMAN_APPROVED_PROBE or a
REGISTRY_RATIFIED row in the new append-only
ideas/NNN/governance_events.jsonl sidecar, v1 schema closed to that one
event), the bundle's provenance.contract_blob must equal it, and the
bundle must validate under that immutable contract -- validate_bundle
gained expected_blob, reading historical contract text from the git
object store; the default (current) import gate is byte-for-byte
unchanged. History no longer goes stale because an amendment moved the
current contract; the review counterexample (historical-approved S stays
COMPLETE while current-approved C depends on it) is a regression test.

Schema closed and contained: schema_version == 1 required; produces,
results_bundle, and artifact outputs must be canonical contained
relative paths; depends_on/all_of/artifacts/launcher/upstream_bundle key
sets closed (legacy upstream_bundle.probe retired); artifact sha256 now
REQUIRED 64-hex -- a binding dependency cannot be unhashed; contract_hash
must be 40-hex. Validation precedes derivation: derive_status raises on
an invalid registry, registry-status exits nonzero, and
terminal_statuses_if_approved / upstream_bundle_requirement refuse
invalid registries outright. One validation-aware status path: the CLI
now injects the same bundle validator as state materialization, and with
no validator a terminal summary is RESULT_PRESENT, never COMPLETE --
COMPLETE is unreachable without validation, everywhere.

Tightening note: a pinless terminal node whose bundle provenance does
not name the current contract is now STALE (previously COMPLETE-able
from summary text alone). Gates: 165/165 both runners (13 new tests),
state-verify --require-all 44/44 byte-identical, registry-validate and
doctor green. Next: R2 (state-view approval-staleness on missing
contract, fingerprint completeness, fixture import hygiene, P2
cleanups), then R3 authors the 023 registry with PR-gated ancestry-bound
ratification. Take-13 record-result remains not blocked on any of this.


## 2026-08-28 - R2 landed: state-view + hygiene pre-flip fixes (round-6 batch)

Approval staleness corrected: an approval whose CURRENT contract is
MISSING is now stale/invalid in materialized state (previously reported
fresh) -- an approved contract that no longer exists is not a fresh
approval. Source fingerprint made complete: when a registry exists,
materialization.sources gains registry_result_inputs -- per-node hashes
of summary.json, provenance.json, and every declared consumed-artifact
file (new experiment_registry.result_input_hashes, deterministic,
containment-guarded) -- so the watermark MOVES whenever a derivable node
status can move. MATERIALIZER_VERSION bumped 2 -> 3 and all 44 state
files re-materialized; the corpus delta is provably one line per file
(the version field), fingerprints and approval flags byte-unchanged for
every current idea (only 004 and 023 hold approvals; both contracts
present, so the staleness fix flips nothing retroactively).

Fixture-import hygiene centralized: Harness.tearDown now purges every
sys.path entry and loaded module rooted in the test's temp dir, and the
two debate tests use a single _import_fixture_scout helper instead of
inline insert+reload -- no later or isolated test can inherit a loader
bound to a deleted repository (the TestDebate order-dependence class
from external review; latent here, fixed regardless). check.yml gains an
isolation canary running the exact reviewer selection
(pytest ::TestDebate) so hermetic selection is CI-enforced.

Supply-chain pins: all six workflows now reference
actions/checkout, setup-python, setup-node by full commit sha (resolved
live from the upstream tags, comment-annotated with the major version);
CI pytest pinned to 9.1.1 to match the gated local runs; a hygiene test
asserts every workflow uses: line is sha-pinned. Taxonomy: ledger gains
TOMBSTONE_STATUS = INVALID_ROW, deliberately excluded from settable
STATUSES (repair-tool-only), with the load() exclusion referencing the
constant. The _digest_path docstring now states the fail-local behavior
the code always had.

Gates: 171/171 both runners (6 new tests); isolated-class runs hermetic
(TestDebate, R1, R2, StateMaterializer selections each pass alone);
state-verify --require-all 44/44 byte-identical under materializer v3;
registry-validate and doctor green. Patch verified by applying to a
pristine worktree of origin/main: applied tracked tree is git-identical
to the gated commit. Next: review packet (fresh main ZIP + R3 design:
draft 023 registry, REGISTRY_RATIFIED artifact spec, PR-gated
ancestry-bound ratification flow, and the four discretionary R1
decisions listed for ratify-or-object) BEFORE R3 lands. Take-13
record-result remains not blocked on any of this.


## 2026-08-28 - M1-pre landed: two-source bundle governance identity (F1)

Root cause, verified against the real Phase-S bundle on
results/probe-023-0e223c82f9eb: validate_bundle check #2 read
provenance.json:contract_blob, but the frozen driver's gate() has always
recorded the governing identity in resolved_config.json
(contract_blob + approval_blob); run.py's provenance.json is
run-environment provenance and never carried the field. Check #2 (E1,
2026-08-15) had therefore only ever been exercised by fixtures; on
landing, take-13's results-validate would have refused its own valid
bundle and no record-result PR would have opened.

Fix, applied identically in validate_bundle and in the registry status
path (_bundle_governing_blob, replacing the single-file reader): the
bundle's governing identity is provenance.json:contract_blob when
present, else resolved_config.json:contract_blob; if BOTH files carry a
value they must agree, and disagreement is a hard failure surfaced as
such (import refusal / node STALE), never a silent pick. Neither-source
still refuses exactly as before. resolved_config.json is a
contract-required output written by the frozen driver's own gate, so
reading the identity the run actually recorded strengthens evidence; no
gate is loosened, and bundle files are never mutated post-run.
Consequently, materialization.sources.registry_result_inputs (R2, v3,
not yet materialized anywhere -- zero live registries) now also
fingerprints resolved_config.json per node, since it co-determines
derived status; no corpus state bytes change and no version bump is
required for a pre-first-use field addition.

Shipped ahead of the pending external review round per the adopted
ordering rule (result-identity binding outranks governance ordering);
the review packet discloses the finding, the remedy, and this
possibility verbatim, and asks for retrospective ratification (Q2).
Gates: 176/176 both runners (5 new tests, including a fixture shaped
like the real S/take-13 bundle passing the import gate, a
disagreement hard-fail, and the registry-side COMPLETE via
resolved_config identity); isolated selections hermetic; state-verify
--require-all 44/44 byte-identical; registry-validate and doctor green;
patch verified git-identical against a pristine origin/main worktree.


## 2026-08-28 - Round-7 review intake + R3a landed (consolidation-close corrections)

Round-7 verdict accepted: architecture green, complexity yellow;
consolidate before expanding. Rulings recorded: D1, D2, D5, D6 and the
F1 fix RATIFIED; the historical-import doctrine refinement, ancestry
rule, and marker-untouchability CONFIRMED; results_v2-<blob12> accepted
as a migration convention with the future per-node
probes/NNN/results/<node>/<blob>/ layout noted for post-023 work. The
utility reframe is adopted as the standing success metric: decisive,
evidence-backed answers per hour of operator attention, with the
reviewer's metric table queued for the measurement window. Generation
automation moves to explicit maintenance mode in the P10 slot
(transition receipts on saturation entry/exit, no nightly same-fact
commits). Roadmap sequence adopted as ordered; blackboard arbiter,
meta-loop, third charter, and tournament selection stay deferred.
Structured RunResult gains consumed/produced artifact refs and the
common event envelope lands before any P5-P8 stage emits events. CSV
dual-write removal and the global scout-target charter bypass are
queued for the legacy-retirement window; coverage/durations as a
periodic diagnostic job and REVAMP.md reconciliation queued as P2.

R3a lands the three P0s the reviewer set for closing this round:

(1) Fixture-import isolation, mechanism-level. Honest reproduction
record: the reviewer's failing ordering did NOT reproduce here -- full
suite green under both pytest 9.1.1 and a dep-complete 9.0.2 venv.
The attempt instead surfaced a real adjacent finding: in a lean
environment three tests silently REQUIRED nbformat/jsonschema and read
as code failures (exactly the packages the reviewer's sandbox could not
install); they now skip explicitly with named reasons. The isolation
mechanism is hardened regardless, per standing rule for latent
environment-dependent defects: Harness temp dirs are resolved at
creation; the purge compares realpaths on both sides and invalidates
import caches; _import_fixture_scout no longer relies on path-priority
reload -- it evicts the fixture-sensitive namespace (scout, state_view,
experiment_registry, ledger), invalidates caches, imports fresh, and
self-checks the resolved origin loudly. The reviewer's sequence
(root import first, then fixture import) is codified as a regression,
and the CI canary is now the mixed three-class selection
(TestDebate + TestR2StateAndHygiene + TestM1PreGovernanceIdentity).

(2) Ratification binding schema finalized BEFORE the first live row
(D3 amendment). governance_events.jsonl v1 rows now carry structured
bindings -- a non-empty list of closed {contract_blob, approval_commit,
approval_sha256} mappings -- replacing the parallel
approvals/contract_hashes arrays that could not mechanically encode
which approval attested which contract. git_commit is renamed
base_commit (the authoring HEAD; a row cannot embed the sha of the
commit that will contain it), format-checked 7-40 hex. Attestation
reads binding contract_blobs. D4 is accepted as conditioned: a
syntactically valid row is necessary, never sufficient -- the R3b
ratify CLI must mechanically verify each binding (the marker bytes at
approval_commit hash to approval_sha256 AND that marker text binds the
contract_blob) with forgery regressions, and the ratification PR binds
the source results-branch commit and the imported bundle manifest
sha256 alongside the bindings.

(3) F2 resolved as ruled: a NARROW legacy rule, never generic
infrastructure. _HISTORICAL_RESULT_INTERFACES keys on
(governing blob, bundle phase); its single entry is the executed
Phase-S interface under 0e223c82f9eb (resolved_config,
simulation_operating_characteristics.csv, simulation_summary.json,
summary, provenance, environment.txt, run_log.txt), marked removable
after 023 ratifies. The historical contract text is not consulted on
that path (its top-level required_outputs describe the study-terminal
bundle); identity, provenance, and hashing checks bind unchanged, and
the phase-sanity gate accepts the table-keyed single-letter phase.
Regressions: the real-S-shaped bundle validates cleanly under its own
blob; an unlisted blob gets no skip; a terminal Phase-C bundle missing
a required output still hard-fails. Future contracts get phase-scoped
result_interfaces instead of table growth.

Gates: 180/180 on BOTH runners AND under the pytest 9.0.2 venv;
isolated and mixed-class selections hermetic; state-verify
--require-all 44/44 byte-identical; registry-validate and doctor green;
patch verified git-identical against a pristine origin/main worktree.
Next: R3b -- the real 023 registry, ratify-registry CLI with mechanical
binding verification and the three import bindings, record-result
ancestry refusal, and the OR-ratified extension of
terminal_statuses_if_approved.


## 2026-08-30 - Take-13 landing: two gate findings, M2-pre, operator import

Take 13 (Phase C, contract 03d4545fe293) completed 2026-08-28 07:28 UTC
and pushed results/probe-023-03d4545fe293 (tip eb6083e) with status
NEGATIVE_PATTERN, 99/100 census cases analyzed, all integrity gates
green, CI widths 0.039-0.065 against the frozen 0.15 bound. The
branch-side landing automation went red and no record-result PR opened.
Two distinct causes, both diagnosed before import:

FINDING (branch vintage of F1): push-triggered workflows execute the
pushed branch's own snapshot of the code, and the take-13 launcher was
packaged before M1-pre -- the branch's frozen validator read
provenance.json for a contract_blob the driver has always written to
resolved_config.json, refused the valid bundle, and the auto-PR step
never ran. The fix has been live on main since M1-pre; it cannot reach
a branch's frozen copy. The automation failed CLOSED: main untouched.
Old PR #1 (the idea-004 import, 2026-08-16) is unrelated; its ref
merely persists.

FINDING F3 (caught in operator-side rehearsal, before any command ran
on the operator machine): the frozen contract's single top-level
required_outputs list conflates BOTH phases' interfaces -- it names the
two Phase-S simulation artifacts, which the Phase-C bundle rightly does
not contain (it consumed the S csv via --phase-s-dir and re-verified it
by sha; summary.simulation_output_sha256 equals the contract's frozen
pin). No single-phase bundle can satisfy the list literally; this is
the exact mirror of F2 and the same class round-7 ruled on.

M2-PRE (landed with this import): the legacy result-interface table now
keys on the GOVERNING blob -- pinned or current alike -- and gains the
(03d4545fe293, 'C') entry: the contract's required_outputs minus the
two simulation artifacts. Narrow, blob+phase-bound, no generic
phase-skip rule, removable after 023 ratifies; regression proves an
unlisted blob still requires the full list. 181/181 both runners;
state-verify 44/44; the staged real bundle validates and record-result
was rehearsed end-to-end in a pristine worktree before handoff.

IMPORT RULING: the bundle totals 1030.1 MB, of which 1029.6 MB is
phase_c_cache/ per-case resume checkpoints -- operational scratch, not
claim-bearing output. The import carries the scientific bundle
byte-verbatim WITHOUT phase_c_cache (19 files); the checkpoints remain
verbatim on the results branch and on Drive as evidence.

AUTHORITY NOTE: the record-result PR exists to route AUTOMATED imports
through a human; with the branch-side automation failed closed, the
operator executes the import and push directly, satisfying the same
human-authority requirement by construction. Queued: flag F3 to the
external reviewer next round; future contracts get phase-scoped
result_interfaces (round-7 direction); P3 adds a launcher-vintage rule
so results branches carry current gate code or main-side revalidation;
R3b ratifies this import retrospectively per the adopted ordering rule.
Next: interpret stage, PAUSED transition per the pre-registered
negative_pattern ruling, the pre-registered clinical-outcome join, and
the signal writeup.


## 2026-08-30 - Correction: post-import state refresh missed in runbook

The take-13 import runbook omitted a step: record-result's PROBED
scrutiny event changes idea 023's ledger inputs, so the committed
ideas/023/state.json was no longer a faithful materialization and
state-verify --require-all correctly went red on main (one CI run).
This was a runbook/rehearsal gap on the assistant side -- the rehearsal
enumerated the import's side-effect files but did not re-run
state-verify on the post-import tree. No data issue; the invariant
refused hand-stale state exactly as designed (the R2 fingerprint moved:
event_count 6 -> 7, scrutiny DEBATED -> PROBED). Remedy: re-run
state-materialize --idea 23, commit the regenerated view, and push;
verified 44/44 byte-identical and 181/181 on both runners before
handoff. Standing runbook rule adopted: any operation that appends
ledger events (record-result, status transitions) is followed by
state-materialize + state-verify before push.


## 2026-08-30 - Interpret stage gains a phone-dispatch surface

interpret-build (cross-family adversarial interpretation: one family
writes interpretation.md under the hard citation mandate, the other
resolves every citation against the analysis files and checks claim
bounds, one revision maximum, verdict JSON) was laptop-only. A
workflow_dispatch surface (.github/workflows/interpret.yml) now exposes
it from the GitHub mobile app, mirroring the actioner's execution
pattern exactly: pinned actions, agent CLIs + existing secrets,
deterministic tests BEFORE any agent runs, scout-bot identity,
SCOUT_CI, serialized under the scout-cycle concurrency group, and a
fail-closed rebase-then-push that also preserves FAILED partial output
(interpret-build commits every leg). The stage moves no scientific
authority by itself: it produces interpretation.md /
interpret_review.md / decision.md for human ratification; the PAUSED
transition and any successor-contract proposal remain operator acts.
Gates: 181/181 both runners including the workflow sha-pin hygiene
scan; patch verified git-identical against a pristine origin/main
worktree.

## 2026-08-30 - Interpret run: codex auth rotation incident + resume capability

First dispatch of the interpret workflow: the generator leg (claude,
498s, exit ok) produced interpretation.md and decision.md -- committed
and preserved. The review leg (codex) failed in 3.5 seconds with
exit_class error: wall-to-wall 401s ending in refresh_token_reused
("Your refresh token has already been used"). Root cause: Codex refresh
tokens are SINGLE-USE; any local CLI refresh invalidates the chain the
CODEX_AUTH_JSON Actions secret snapshots, and the quiet nightlies let
the stale secret go unnoticed. The harness behaved exactly as designed:
partial output committed, receipts written for both legs, workflow red,
nothing ratified.

Ops rule adopted: export ~/.codex/auth.json to the CODEX_AUTH_JSON
secret IMMEDIATELY BEFORE dispatching any agent workflow, and avoid
local codex use until the run completes. Queued for the P10 ops batch:
a named auth-preflight step (fail fast with CODEX_AUTH_EXPIRED before
any leg runs, instead of a 3.9k-line 401 log).

M3-pre landed: interpret-build gains --resume-review (and the workflow
a matching boolean input) -- when a preserved round-1 interpretation
exists, the run skips the generator and proceeds directly to the
adversarial review; it refuses when no interpretation exists.
Rationale: an infrastructure failure must not burn a good leg, and a
regenerated round-1 would silently replace the exact text under review.
Two regressions prove the skip and the refusal; 183/183 both runners;
patch verified git-identical against a pristine origin/main worktree.
The round-1 interpretation remains UNRATIFIED pending the cross-family
review it was always owed.


## 2026-08-30 - Round-8 review intake: interaction is the frontier

Full-system audit absorbed (robustness, interaction, scientific
utility, path forward; literature-grounded against AI Scientist,
Co-Scientist, Agent Laboratory, Robin, ScientistOne, AutoGen,
LangGraph, multi-agent-debate and injection-security work). Verdict:
green scientific integrity, green-to-yellow failure containment,
yellow automation and maintainability, clearly yellow human<->system
interaction -- the system's biggest remaining weakness is not safety,
ideation, or execution; it is interaction. Standing goal reformulated
and adopted verbatim as the project's articulation: a human-directed
research instrument in which strong models do most of the cognitive
and mechanical work required to turn vague scientific possibilities
into falsifiable, evidence-traceable conclusions, while deterministic
infrastructure preserves identity, provenance, authority and
reproducibility.

CORRECTIONS RECORDED. (1) Milestone phrasing: idea 023 is the first
complete experimental-and-interpretive lifecycle; its final governance
transition awaits operator ratification (decision.md carries stale
pre-review prose; state remains SHORTLISTED while the decision
recommends PAUSE) -- our "first complete idea lifecycle" wording was
premature. (2) The 2026-08-30 manual state-refresh runbook rule is
itself exception-handling: authority-mutating commands must own their
derived-state transaction (append -> materialize -> verify -> succeed);
the manual rule is superseded by that design. (3) Our draft
note-blocking formulation ("every stage refuses on any open note") was
too broad -- an accidental denial-of-service; notes bind to explicitly
named response boundaries. (4) Packet said 181 tests; the reviewed ZIP
carries 183 (post-resume-review chronology), noted for the record.

Q0 RATIFIED: M2-pre as a narrow temporary compatibility mechanism with
an explicit retirement destination; the 1 GB phase_c_cache exclusion
(resume scratch is not claim-bearing output); the operator-executed
import as an exceptional equivalent human-authority path -- future
operator imports must emit the same structured authority receipt as the
automated route; the phone-dispatch interpret workflow. A1 resolved:
branch-vintage is eliminated by MAIN-OWNED revalidation
(repository_dispatch: current main as executable code, exact results
commit as data) -- never by copying orchestration into result branches.

ADOPTED ARCHITECTURAL RULINGS. Three-register input taxonomy becomes a
primitive: integrity-invalid -> hard refuse; well-formed but
semantically inconsistent -> dissent-and-clarify; ordinary -> proceed.
Division of labor: deterministic machinery answers "may this happen",
models answer "does this make scientific sense and what are we
missing", the human answers "which judgment do we authorize"; models
never waive integrity rules, hard code never adjudicates scientific
ambiguity a frontier model reasons about better. Semantic anomalies
route to an opposing-family clarification ("valid but conflicts with
X; interpretations A/B; which did you intend?"). ratify-interpretation
becomes a deterministic authority primitive (verify interpretation/
review/verdict/decision/contract/bundle identities, then one
transaction: ratification event + authorized status transition +
materialize + verify); lifecycle status is machine-derived from the
authority act, science prose is never rewritten. One symmetric
note/advisory schema on the R4 event envelope -- no pre-R4 interaction
file formats; responses required at named boundaries; a valid response
includes evidence-backed rebuttal; advisories never dictate the human,
notes never dictate the model. Adversarial reads of operator acts:
judgment-rich only (ratifications, overrides, kill/revive against
machine advice, approving over open advisories), returning
NO_MATERIAL_DISSENT or DISSENT{finding,evidence,why}; dissent is never
veto; health metric = material dissent that changed a decision / all
reads, plus operator minutes per useful catch; a reviewer producing no
useful dissent gets respecified. Interpretation gains a first-class
operator objection: distinct authored object, one bounded operator
reconsideration even after the machine revision is consumed, and the
agent may defend the original with citations. confer: read-only,
bounded, receipted, artifact-hash-bound single exchange, landed after
the substrate; conclusions promoted to notes, transcripts never enter
core context. Minority-dissent lifecycle telemetry (raised -> adopted/
rebutted/overruled -> vindicated/falsified) preferred over agreement
rate; never majority-vote truth. decisions.md remains the append-only
human authority log but STOPS being whole-file prompt context; R4
derives applicable-decision context per idea/charter/system. Security
doctrine: prompts explicitly separate TRUSTED INSTRUCTIONS from
UNTRUSTED EVIDENCE (results, transcripts, note bodies, external text);
evidence text is never executable instruction; judgment stages reading
untrusted text run least-privilege; citations and cross-family review
are scientific defenses, not sandboxes.

MULTISTEP (Q1): R3b proves the real S->C registry before any schema
expansion; phase-scoped result_interfaces enter NEW contracts (the
contract, not the registry, owns what counts as a valid result);
launcher upstream becomes an inputs LIST beside P3's node-addressed
driver; results converge on probes/NNN/results/<node>/<contract-blob>/
replacing results_v2 semantics; no any_of, quorums, dynamic branching,
or per-node contract documents absent demonstrated need -- the six-blob
amendment chain proved historical pinning works.

Q8 AUDIT TABLE ADOPTED with its classifications and retirements:
keep (baseline-charter fallback, tombstones, two-source governance,
contract-owned exclusions like sub-stroke0043); retire on trigger
(historical interface table after 023 ratifies + phase-scoped
interfaces; M/B legacy path after migration; phase-s source sniff and
results_v2 assumptions at P3; --resume-review absorbed into R4 generic
resumable stage outcomes; drive_fuse at P3; CSV dual-write and global
scout-target in the legacy window; whole-log prompt injection at R4;
manual codex refresh -> P10 preflight now, durable credential model
later; global-cycle roles -> ROLE_BOUND before flip). Transitional-debt
convention adopted: constructs marked # TRANSITIONAL with owner and
retire_when, indexed in a CI-checked transitional_debt.yaml -- a
transitional construct outliving its trigger fails CI. Verdict on the
discipline: mostly general mechanisms, close enough to the boundary
that mechanical retirement now matters.

REVISED SEQUENCE ADOPTED: M4 ratify-interpretation + transactional
authority mutations (immediate; closes 023 governance) -> R3b real 023
registry + ratification -> R4 typed RunResult + common event envelope +
generic resumption identity + decisions-context derivation -> P3
driver_spec + launcher inputs list + main-owned dispatch revalidation +
node-addressed results -> ROLE_BOUND -> derived-state soak + consumer
flip -> interaction substrate (symmetric notes/advisories, operator
reconsideration, confer) -> stop-report (successor-question generator
only; never amends the current experiment) -> design-review -> gate
calibration -> measured-need expansion. Blackboard arbiter, meta-loop,
third charter, tournaments remain deferred: the human plus this
repository already is the blackboard; first make it interactive and
typed. Consolidate-before-expanding remains binding. scout.py 2c split
after R4/P3 interfaces stabilize.


## 2026-08-30 - M4 landed: ratify-interpretation + transactional record-result

The round-8 authority primitive. ratify-interpretation IDEA --status S
verifies six identities -- interpretation.md, interpret_review.md, its
APPROVE verdict (ratification never bypasses the machine review;
operator reconsideration remains a distinct future path), decision.md,
the governing contract blob, and the validated results bundle -- then
performs ONE transaction: a ledger INTERPRETATION_RATIFIED event
carrying the authorized status transition plus all six identity hashes
(the existing append-only ledger is the substrate; no new event format
before R4) -> digest -> re-materialize the idea's state -> state-verify
-> single commit. Lifecycle status is machine-derived from the human
authority act; science prose is never rewritten. record-result gained
the same transactional tail (scrutiny event -> digest -> materialize ->
verify -> commit), so the 2026-08-30 manual state-refresh runbook rule
is now superseded by construction for both current authority mutators,
exactly as round-8 ruled. Shared _result_bundle_for helper replaces the
inline discovery in interpret-build. Four regressions: the full happy
transaction (event fields, hashes, PAUSED state, verify-clean, commit
message), refusal without machine APPROVE (no event lands), refusal on
unknown status and missing documents, and record-result owning its
state transaction end-to-end. Gates: 187/187 both runners (also re-run
green on the pristine-applied tree), state-verify 44/44, registry-
validate and doctor green; patch verified git-identical against a
pristine origin/main worktree. Next operator act: ratify idea 023 ->
PAUSED, closing the first experimental-and-interpretive lifecycle's
governance per the pre-registered negative_pattern ruling.


## 2026-08-30 - R5a landed: the Research Card (derived view)

Answering the operator's standing need -- "the idea is in one place, but
nothing describes results, position, and connections together" -- and
the context-window motivation behind it: ideas/NNN/CARD.md is a
deterministic derived VIEW (card-materialize IDEA; --check verifies
byte-identity, mirroring the state invariant) rendering an idea's
scattered authorities onto one compact, human- and model-readable page:
identity and ledger position; the question; DECLARED-vs-DERIVED status
with drift flagged and never silently reconciled (idea 023's card
immediately surfaced its own stale keystone_status: NOT_INSPECTED
against the ratified NEGATIVE -> PAUSED -- the first machine-generated
candidate operator update); the full contract-blob lineage recovered
from approval-marker history (023 renders its six-blob amendment
chain); experiment position and bundle identity; headline per-stratum
results verbatim from summary.json (every number already
citation-checked by the cross-family review); interpretation/review/
decision hashes and the ratification row; connections via a new
OPTIONAL related_ideas list on the existing idea_card.json (no new
authority, no new event format -- pure consolidation-doctrine view);
and document pointers. The card is the designated compact context
object for the coming confer primitive. ideas/023/CARD.md is committed
and check-verified cross-machine. Three regressions (lineage ordering,
drift flag, determinism, stale-byte refusal, related-ideas rendering);
190/190 both runners, also green on the pristine-applied tree;
state-verify 44/44; patch git-identical against pristine origin/main.
Next: R5b confer-v0 (read-only, receipted, trusted/untrusted prompt
separation, advisory-only suggestions) under a TRANSITIONAL marker with
a resequencing disclosure addendum to the external reviewer.

## 2026-08-30 - R5b landed: confer-v0, transitional-debt ledger, driving framework

confer IDEA "question" -- the read-only half of the interaction layer,
pulled forward under the ship-with-disclosure class (addendum authored
for the external reviewer; see below). Round-8 rulings implemented
verbatim: bounded single exchange; receipted via run_agent; READ-ONLY
(scope-guarded to ideas/, produces only ideas/NNN/confer/qXXXX.md plus
prompt, grounding, log); hash-grounded (qXXXX_grounding.json binds the
question to the exact sha256 of every context artifact -- the research
card and the idea's claim-bearing documents); three-register behavior
mandated in the prompt (ordinary -> answer; premise conflicts evidence
-> PREMISE CHECK with citations then best faithful answer, rebuttal
expected; unresolvable -> say so and name the resolving artifact);
citation mandate; SUGGESTED UPDATES rendered advisory-only, applied by
the operator through normal commands, never amendments to closed
experiments. First implementation of the round-8 security doctrine:
TRUSTED INSTRUCTIONS strictly precede UNTRUSTED EVIDENCE, evidence is
data, instruction-shaped evidence text is reported, never obeyed.
Family: explicit roles.confer override, else the interpret family
(claude -- codex credentials not required for confer). Phone surface:
.github/workflows/confer.yml (pinned, tests-first, fail-closed push).

transitional_debt.yaml bootstrapped with ten entries spanning the
round-8 audit table (confer_v0_pre_substrate, historical_result_
interfaces, resume_review_flag markered in code; seven more ledgered
with locations and triggers). TestTransitionalDebt enforces the
convention bidirectionally: a markered entry without its code marker,
or an in-code TRANSITIONAL token missing from the ledger, fails CI.
Retirement is now state, not intention.

DRIVING FRAMEWORK codified (operator+assistant, this evening's cadence
and standing policy): three concurrent lanes -- A build (patch ritual:
pristine-proof, both runners, echo, operator box), B external review
(async, batched, never blocking A except class 1), C live exercise
(real use on idea 023's lineage doubling as organic soak evidence).
Review-trigger classes: (1) design-before-code for authority semantics,
gate meaning, schemas, sequence changes; (2) ship-with-disclosure for
urgent landing-path fixes (M1-pre precedent) and disclosed
resequencings; (3) batch closeout after each coherent 2-4-patch
cluster or before first live use of new AUTHORITY machinery; (4) no
review for views, tests, docs, neutral refactors -- logged and audited
at the next batch. Tuesday night is a patch freeze ahead of the
Wednesday advisor meeting. Gates: 194/194 both runners (also green on
the pristine-applied tree); state-verify 44/44; patch git-identical
against pristine origin/main.

## 2026-08-30 - R5c landed: reviewed confer with role rotation + enforced docs

Operator directions, adopted verbatim. (1) The adversarial two-model
pattern is the accuracy mechanism, so confer answers do not run
unopposed: a second, opposing-family leg reviews five meat-level
properties -- thesis correctness against the evidence, OVERVIEW
fidelity (simplification must never become distortion; over- and
under-statement are findings), citation resolution, premise-check
appropriateness, claim bounds -- returning CONCUR or CONTEST; CONTEST
triggers ONE bounded revision, a second CONTEST stops for the
operator. (2) Clarity leads: the draft leg's trusted block mandates a
plain-language ## OVERVIEW any reader can understand -- carrying no
claim the ## DETAILS below do not support -- before the cited
reasoning; the reviewer deliberates on the OVERARCHING answer, not
line-by-line prose. (3) Diversity: the families SWAP roles across
exchanges (exchange 1 drafts with pair[0] and reviews with pair[1];
exchange 2 swaps; explicit roles.confer/confer_review override), so
neither family owns drafting or reviewing; cross-family holds in every
exchange, and the codex credential-freshness rule now applies to every
confer dispatch. Every leg committed and receipted; the final answer
carries the reviewer's verdict in-tree.

Documentation becomes state, not intention: README.md gains a complete
Operator Command Reference (all 35 CLI subcommands indexed; detailed
entries for confer, card-materialize, ratify-interpretation,
transactional record-result, interpret-build --resume-review; a phone-
surfaces section with the credential rule), and TestDocsHygiene fails
CI whenever any registered subcommand is missing from the README.
Driving framework gains rule 5: patches touching the operator surface
update the command reference in the same patch. Gates: 197/197 both
runners (green again on the pristine-applied tree, including the
family-swap and docs-coverage regressions); state-verify 44/44; patch
git-identical against pristine origin/main.

## 2026-08-30 - R5d landed: durable codex auth for Actions

The ChatGPT OAuth chain rotates its refresh token on every use, and an
Actions runner that rotates discards the successor when it dies -- so
the CODEX_AUTH_JSON snapshot was structurally a coin flip: any agent
run could silently consume the chain and strand the next one (the
2026-08-30 interpret incident was this class). Remedy, landing ahead of
the P10 durable-credential item: all six agent workflows (scout-cycle,
idea-pipeline, actioner, librarian, interpret, confer) now prefer an
OPENAI_API_KEY repository secret -- API keys do not rotate on use and
live until revoked -- with the OAuth snapshot kept as automatic
fallback when the key is absent. The auth step logs which mode it took;
scout-cycle's dry-run guard preserved; every workflow YAML-validated;
CI and local codex now hold fully independent credentials, retiring
the "no local codex during runs / re-export before dispatch" rule
whenever the key is set (the rule remains documented for fallback
mode). README phone-surfaces section updated per docs rule 5. Cost
note: API-key legs bill the platform account per token (CI review legs
are short); the ChatGPT subscription continues to cover local use.
Gates: 197/197 both runners, green again on the pristine-applied tree;
patch git-identical against pristine origin/main.

## 2026-08-30 - R5e landed: confer never vaporizes evidence

The first live confer dispatch failed with ZERO repository trace -- no
commits, no receipts, no logs. Root of the silence (root of the failure
itself pending the Actions log): run_agent raises on agent failure, and
cmd_confer, unlike interpret_build, did not wrap its legs in a
catch-and-commit-partial handler -- any leg-level raise discarded the
grounding, prompt, receipt, and log with the runner. Two invariants
land: (1) the question, grounding sidecar, and prompt are COMMITTED
before any agent leg runs ("question registered"), so a run that
reaches the command can never again disappear without trace and a
zero-commit failure now cleanly indicts the pre-command workflow steps;
(2) the entire leg loop is wrapped so ANY raise -- SystemExit or
otherwise -- commits partial evidence (receipts included) before
propagating, mirroring and strengthening the interpret pattern.
Regression proves both: a raising leg leaves the registration commit
and a FAILED(type) commit behind. 198/198 both runners, green again on
the pristine-applied tree; state-verify 44/44; patch git-identical
against pristine origin/main. Diagnosis of the actual trigger proceeds
from the Actions step log; the next dispatch self-documents either way.

## 2026-09-01 - R5f: codex API-key auth materialized (confer incident #2 closed)

R5e's evidence invariants worked on first contact: the re-dispatched
confer left the question-registered commit, the FAILED(SystemExit)
commit, the receipt (codex draft leg, error, 15.1s, model None -- also
documenting that AGENTS.toml's rotation pair orders codex first, so
odd exchanges draft with codex and claude reviews; cross-family holds),
and the verbatim log: 401 Unauthorized "Missing bearer or basic
authentication in header" at api.openai.com. Diagnosis: the API-key
branch correctly fired (the secret is set), but this codex CLI version
does not read OPENAI_API_KEY from the environment for auth -- with no
auth.json present it selected the API transport and sent no
credentials. Remedy across all six agent workflows: the API-key branch
now writes the key into codex's own auth store ({"OPENAI_API_KEY":
...} in ~/.codex/auth.json, chmod 600) and sets preferred_auth_method
= "apikey" in ~/.codex/config.toml; the OAuth-snapshot fallback branch
is unchanged. Queued for round 9 (operator direction): a question
funnel -- not every confer deserves the full adversarial treatment;
tiering simple/factual asks to a lighter path with escalation rules,
plus an open-source survey of routing/cascade precedents. All
workflows YAML-validated; 198/198; patch git-identical against
pristine origin/main.

## 2026-09-01 - Round-9 intake + S1 landed (round-9 immediates)

Round-9 full audit absorbed. Verdict: sound and increasingly useful;
not yet bloated but at the inflection where breadth must stop outrunning
production exercise. Standing strategic rule adopted verbatim: make what
already exists become unavoidable, generic, live-tested and boring; and
the architecture budget: no new persistent mechanism until the
preceding one has been exercised on at least one live scientific
lifecycle.

DISPOSITIONS RECEIVED: all six R5 patches RATIFIED (R5a with a
generality caveat -- the card's headline renderer knows 023-specific
fields; R5e strongly). Confer's artifact shape does not prejudice R4.
The five-property review mandate gains a SIXTH property. The credential
fork is DECIDED: (A) a non-rotating API credential for CI, subscription
OAuth strictly local/manual; the self-refreshing-PAT loop is rejected
as an endpoint (privilege increase, serialization-dependent mutable
chain) and acceptable only as an explicitly transitional mechanism if
cost blocks A. Auth preflight pulled forward from P10 to NOW. The
confer FUNNEL design is received and adopted for the post-R4 slot:
deterministic four tiers (local no-LLM; light single-model; reviewed
draft+review; authority-adjacent reviewed+operator-gate) with
auto-escalation on numerical claims, source contradictions, PREMISE
CHECK, SUGGESTED UPDATES, interpretation proposals, governance
consequences, unresolved evidence, or missing citation support;
learned routing (RouteLLM-class) only after real routing outcomes
accumulate; routes become receipted outcomes, hence post-R4.

ADOPTED ARCHITECTURE RULINGS: AiiDA's two-graph lesson shapes R4 --
data provenance (dataset -> run -> bundle -> interpretation) and
logical/governance provenance (approval -> contract -> registry ->
authorization; review -> ratification -> transition; note ->
acknowledgment) stay separate typed structures linked by ids/hashes,
never one giant ledger schema. The generic trusted/untrusted evidence
envelope extends confer's doctrine to ALL stage prompts (queued
immediately after R3b, with an injection-fixture regression). The
adversarial pre-read of operator acts is scoped to consequential acts
only (approvals, amendments, ratifications, overrides, registry
ratification, high-severity acknowledgments) with catch-rate
measurement. Two-A is declared merged-not-consolidated; the reviewer's
twelve-item checklist is adopted verbatim as the soak's acceptance
bar. driver_spec sketch, ten driver acceptance tests, and
drive_api_cache endpoint absorbed into P3. scout.py modularization by
authority boundary queued post-R4/P3. Roadmap sequence adopted: R3b ->
R4 (typed outcomes + envelope) -> multi-input launcher + phase-scoped
result_interfaces -> driver_spec -> ROLE_BOUND -> soak/flip ->
notes/advisories -> funnel -> scoped decisions context -> split ->
stop-report/design-review/calibration; arbiter, meta-loop, third
charter deferred until measured need.

S1 LANDED (the four smallest immediates; R3b is next and separate):
(1) load_agent_config fails CLOSED with AGENT_CONFIG_INVALID when
AGENTS.toml exists but cannot parse -- configuration corruption never
again degrades into default role identity; absence still means
defaults. (2) Every agent workflow gains a Codex auth preflight
BEFORE any scientific leg, with the reviewer's named failures:
CODEX_CREDENTIAL_MISSING (no key, no snapshot -> hard stop),
CODEX_CREDENTIAL_REJECTED (401 on a zero-cost models probe -> hard
stop), inconclusive HTTP -> proceed with notice. (3) run_agent's
receipt classifier names in-run credential/billing failures from the
leg log (CODEX_ACCOUNT_UNFUNDED, CODEX_CREDENTIAL_REJECTED prefixes on
exit_detail) -- a red leg is now diagnosable from the repository
alone, completing the arc the three confer failures began. (4) The
confer review gains property six: question coverage -- every part of
the operator's question answered or declared unanswerable, unresolved
assumptions named, never papered over (README updated per docs rule).
(5) The 023-specific card headline renderer is ledgered:
TRANSITIONAL(card_headline_023_fields), retiring when headline fields
become contract/registry-declared. Two regressions (config fail-closed
incl. absent-vs-malformed split; unfunded receipt naming end-to-end
through run_agent). Gates: 200/200 both runners, green again on the
pristine-applied tree; state-verify 44/44; all workflows
YAML-validated; patch git-identical against pristine origin/main.

OPERATOR ACTION PER THE RATIFIED FORK: fund the platform API balance
(~$10); the subscription OAuth remains local-only. Next build: R3b --
the production 023 registry and its ratification, the first live
exercise of the registry substrate. Tuesday night remains the patch
freeze before the Wednesday advisor meeting.

## 2026-09-01 - R3b landed: the production 023 registry and its ratification

The registry substrate carries real science for the first time.
ideas/023/registry.yaml declares the two-node DAG: phase_s pinned to
its historical contract 0e223c82f9eb..., phase_c to the current
03d4545fe293..., joined by an all_of edge, a BINDING artifact
dependency on the Phase-S operating-characteristics csv at its exact
sha (59069fa9...), and the launcher upstream_bundle plumbing bound to
that edge. Governance rows gain the round-7/8 IMPORT BINDINGS: a
closed `imports` list ({node, source_commit, manifest_sha256, bundle})
validated alongside bindings. Ratified rows now confer terminal
authority (ratified_binds_current extends the A3 interim: marker-bound
OR a well-formed REGISTRY_RATIFIED event binding the current bytes).

record-result gains the historical lane: --expected-blob validates the
bundle under its own immutable contract, --source-commit triggers the
ANCESTRY refusal (the source snapshot must carry the approval marker
binding that pin) and the VERBATIM check (every staged byte must equal
the source tree, compared blob-by-blob), the destination becomes
results_v2-<blob12>, and EVERY import now writes the structured
authority receipt round-9 required (<dest>.import.json: source commit,
byte-manifest sha256, file count).

ratify-registry IDEA --operator NAME is the authority transaction:
bindings are DERIVED from approval-marker history and each is
mechanically verified (marker bytes at the bound commit hash to the
recorded sha AND textually bind the pin); every pinned node's import
receipt is re-verified (manifest recomputed, ancestry re-checked);
refusals name their forgery class. Then one transaction: append the
REGISTRY_RATIFIED event -> registry-validate -> derive with the
validator injected, EVERY node required COMPLETE -> state-materialize
-> state-verify -> card re-render -> single commit.

The rehearsal (throwaway worktree, real repo, real S branch) executed
the whole arc: S bundle imported verbatim from 5aa8b5a1... (manifest
7248cd0f8551, receipt written), then ratification produced bindings
03d4545fe293@1ad4885 (sha 325703c888df) and 0e223c82f9eb@68057ec (sha
012e114d67ea), the phase_s import binding, and BOTH NODES DERIVED
COMPLETE -- each validated under its own immutable contract, the exact
counterexample class round 5 demanded, now production truth. The
rehearsal also CAUGHT a real regression before it shipped: with the S
import present, bundle discovery's alphabetical glob preferred the
historical directory; discovery now prefers the current-era fixed name
until P3's node-addressed layout (regression added). Pre-import, the
committed card honestly shows both nodes STALE (phase_c's declared
input missing) -- the operator's import + ratification visibly heal
the DAG. The F2/F3 historical-interface table's retirement trigger is
now armed (retires with phase-scoped result_interfaces, next batch).
Six new regressions (transaction end-to-end incl. OR-ratified;
pin-outside-lineage; receipt-manifest and ancestry forgeries;
historical lane incl. verbatim refusal; discovery preference) plus the
governance-schema imports coverage. Gates: 205/205 both runners;
state-verify and card --check green on BOTH the build tree and the
pristine-applied tree; patch git-identical against pristine
origin/main.


## 2026-09-01 - Operator ruling: idea-045 claim-identity gate (revise-in-place)

The 045 debate ended REVISE with an explicit human unblock: decide
whether stripping the "decisively refuses / lineage-terminal" negative
changes the candidate's identity under the claim-identity rule --
revise in place if not, supersede with a new registration if so.
RULING: identity preserved; the revision is ratified in place. The
question ("did tissue composition create idea-023's sign reversal?")
is unchanged; what moved is the epistemic ceiling of one answer arm --
nulls become sensitivity-limited because no external bound exists on
HU-by-outcome effect modification -- and a card must not be forced
into a new identity for becoming more honest about what a null can
mean. The surviving decisive arm is correctly scoped: a reversal that
persists under adjustment decisively shows attenuation imbalance does
not explain it. deliverable_original preserves the pre-revision claim
for lineage, per convention.

Governance observation recorded for round 10: the pipeline's
auto-revise executed the rewrite BEFORE this human gate was formally
resolved -- benign here (the rewrite implemented exactly the debate's
conditions and this ruling ratifies it), but the ordering inverts the
unblock's letter. This is a live specimen for the reconsideration /
notes-substrate design: machine revisions that a debate conditions on
a human ruling should be able to WAIT on that ruling. Also observed:
the idea-pipeline stages did not advance the ledger scrutiny ladder
(045 remains SCOUTED after keystone/critique/debate); queued as a
small fix. Idea 045 is now cleared to proceed to probe-plan ->
human contract approval -> probe-build under existing machinery.


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
- [isles24] **idea-023** [PAUSED] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
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
- [isles24] **idea-045** [SHORTLISTED] -- Tissue-normalized joint CBV/MTT compensation at matched flow
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
- [isles24] **isles24-scout-006-c01** [SHORTLISTED] -- 
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


===== ideas/045/CARD.md =====
# Research Card - idea-045

GENERATED VIEW (R5a). Never edit: regenerate with `python scout.py card-materialize 45`. Edits belong in the source artifacts this card renders.

## Identity
- title: Did tissue composition create idea-023's sign reversal?
- charter: ?   track: wide   card-id: isles24-scout-006-c01
- ledger status: SHORTLISTED   scrutiny: DEBATED   ledger events: 5

## Question
Does per-patient Q1-minus-Q4 NCCT median-attenuation imbalance account for idea-023's opposite-signed mean final-infarct contrasts in flow bands 2 and 3?

## Declared vs derived status
- idea_card.keystone_status: 'INSPECTED_TRUE'
- system-derived: no interpretation

## Contract lineage (approval marker history, oldest -> newest)
- (no approval marker history)

## Experiment position
- no imported results bundle

## Interpretation and authority
- interpretation.md: missing
- interpret_review.md: missing
- decision.md: missing
- ratified: no

## Connections
- (none recorded; add an optional related_ideas list to idea_card.json)

## Documents
- ideas/045/idea_card.json
- ideas/045/probe_contract.yaml  (absent)
- ideas/045/interpretation.md  (absent)
- ideas/045/interpret_review.md  (absent)
- ideas/045/decision.md  (absent)
- ideas/045/state.json


===== ideas/045/README.md =====
# Idea 045: Tissue-normalized joint CBV/MTT compensation at matched flow

Selected from scouting cycle isles24-006, candidate 1.


===== ideas/045/consensus.md =====
# Debate summary — idea 045

## Agreed

- The attenuation-selected population is a legitimate scoped estimand: the question concerns association within “viable-attenuation” tissue, not recovery of idea 023’s unconditional association (proposer round 1; critic round 2 accepted that the identity check passes).
- Admission NCCT attenuation is not a neutral filter. Because hypodensity relates to tissue injury and final infarction, excluding voxels by HU can preferentially remove outcome-bearing signal (critic round 1; proposer round 1 conceded the null-interpretation consequence).
- Voxel support, retained-event fraction, and post-gate infarct prevalence alone cannot prove that the Q1-versus-Q4 contrast remains detectable (critic rounds 1–2; proposer rounds 1–2 amended in response).
- Any sensitivity calibration must preserve patient clustering and the real covariate geometry, plant both signs of a fixed contrast upstream of selection, apply the frozen HU gate unchanged, and avoid using observed band directions to tune the simulation (critic round 2; proposer round 2 accepted and specified these conditions).
- The proposed round-2 generator is inadequate for the decisive-negative claim because it makes synthetic outcome independent of HU within CBV quartile. It therefore tests sample-size attrition, not selective removal of an HU-localized hemodynamic association (critic round 3; proposer round 3 conceded).
- Without an external, outcome-independent bound on HU-by-outcome effect modification, a post-gate null is sensitivity-limited and cannot terminate the lineage. A positive directional and precision-bounded association within the gated population remains interpretable as an association and could motivate a separately approved model-use study (round 3).
- The cheap Rung-0a analysis of the existing attenuation audit remains useful for testing whether tissue imbalance plausibly accounts for the parent’s band-2/band-3 reversal, although it is exploratory successor-design evidence because it joins already-open outcome-derived values (critique and proposer round 3).

## Unresolved

### Does weakening the negative claim change the candidate’s identity?

- **Question:** Can idea 045 be revised in place after replacing its lineage-terminal, “decisively refusing” negative with a sensitivity-limited, non-terminal null?
- **Proposer’s position:** The scientific question and positive estimand are unchanged, but the deliverable sentence loses a material promise; the proposer explicitly routes the identity determination to human governance.
- **Critic’s position:** The critic did not take a position on the governance boundary. The substantive criticism requires weakening the negative claim.
- **What would settle it:** A human application of the 2026-08-10 claim-identity rule to the old and revised deliverable sentences. This is a governance judgment, not a missing empirical fact.

### Can a future calibration restore a decisive conditional negative?

- **Question:** Is there a defensible quantitative bound on how much of the pre-gate Q1-versus-Q4 association may be concentrated in HU strata excluded by the gate?
- **Proposer’s position:** No such bound is currently available; an unrestricted worst case permits all signal to lie in excluded voxels, so every current post-gate null must remain sensitivity-limited.
- **Critic’s position:** A decisive negative would require an externally bounded effect-modification family and successful recovery of both signs in every band under that family.
- **What would settle it:** Primary external evidence or an independent, non-census-label measurement that quantitatively bounds HU-by-outcome effect modification in the deficit region. Without that evidence, the decisive-negative interpretation cannot be recovered.

### Should the reduced study still run?

- **Question:** Is a study with an interpretable positive but only a sensitivity-limited negative worth advancing beyond the existing Rung-0a CSV analysis?
- **Proposer’s position:** Yes. Rung 0a is cheap and decision-grade; a positive gated census remains useful, while a null must be reported with its limitation.
- **Critic’s position:** The critic established that the census cannot support the advertised decisive negative, but did not argue that the positive arm or Rung 0a is invalid.
- **What would settle it:** First run the prespecified Rung-0a attribution analysis. Its result can determine whether tissue imbalance plausibly explains the reversal and whether the cost of a gated census is justified. The ultimate willingness to fund a one-sided-informativeness study is a human value judgment.

## Positions that moved

- **Proposer, round 1:** Conceded that adequate voxel support alone cannot make a post-gate null decisive after the critic explained that the HU gate may remove outcome-bearing voxels. The proposer added outcome-retention and planted-effect gates plus a classification fork. This concession was earned.
- **Proposer, round 2:** Conceded that “recover planted effects” was underspecified after the critic showed that a generic or post-gate injection would not test the target estimand. The proposer specified a ±0.15 parent-anchored contrast, both signs, preserved patient/covariate structure, synthetic-label separation, and frozen ordering. This concession was earned.
- **Proposer, round 3:** Conceded the decisive-negative claim after the critic showed that the proposed generator assumed HU ignorability within CBV quartile and therefore assumed away the dangerous selection mechanism. The proposer withdrew lineage terminality and accepted a sensitivity-limited null absent an external effect-modification bound. This concession was earned.
- No unearned capitulation occurred.

## Amendments made

At round zero, the idea claimed that a tissue-gated census could either establish a directionally stable association or decisively refuse the Stage-0 prerequisite, with a negative terminating the lineage.

The debate first added outcome-retention checks, planted-effect recovery, a frozen HU window, and a rule that failed sensitivity gates prevent a decisive interpretation. It then made the proposed calibration more explicit: the minimum contrast was anchored to the parent’s 0.15 bound, both signs had to be recovered in every band, patient clustering and covariate geometry were preserved, and real labels were withheld from synthetic calibration.

The final concession supersedes the strongest part of those amendments. Because the generator cannot protect against unknown HU-by-outcome effect modification, the current idea may claim an interpretable positive association within the attenuation-selected population, but a null is sensitivity-limited, non-terminal, and cannot “decisively refuse” the parent formulation. Lost from round zero are the decisive-negative classification, negative-result-value claim of 5, and promised terminal closure. The card also still needs the critique’s earlier repairs: make Rung 0a an imbalance-versus-d attribution analysis with a frozen decision rule, acknowledge reuse of the opened census split, relabel the design as conditional-observational, and scope any positive sentence to equal-patient-weight means.

## Recommendation

**REVISE.** The substantive question retains a viable positive arm and a cheap, useful Rung-0a analysis, but the current card still asserts a decisive, lineage-terminal negative that both sides ultimately rejected. The single most important thing for the human to inspect is whether removing “decisively refusing” and making every null sensitivity-limited preserves the candidate’s identity under the claim-identity rule; if it does, revise the card and scores in place, and if it does not, supersede it with a newly registered successor.

## In plain terms

This idea asks whether a blood-flow pattern is related to later stroke damage after comparing only brain tissue with similar appearance on the admission CT. It first proposes a cheap check of existing data to see whether tissue differences plausibly caused the earlier study’s conflicting results.

The debate concluded that a positive result could still be meaningful, but a negative result would not settle the question: the CT-based filter might remove the very tissue carrying the association. No current external evidence bounds that problem well enough to make a negative decisive, so the written claim must be weakened before the study advances.

The human is being asked whether that weaker negative changes the identity of the idea or can be handled as a revision of the existing card.

```json
{"verdict": "REVISE", "unblock": "Human resolves the claim-identity boundary, then the card is rewritten to preserve only the positive association claim and classify every post-gate null as sensitivity-limited unless an external HU-by-outcome effect-modification bound is obtained."}
```


===== ideas/045/critique.md =====
# Critique — idea 045 (Tissue-normalized joint CBV/MTT compensation at matched flow)

```
FATAL OBJECTION: NONE
EVIDENCE: Leading repairable defect: the card's own motivating rows (bin_tissue_audit.csv
joined against per_patient.csv) do not show the simple tissue-inflation story, and the card
prespecifies no Rung-0a -> Rung-0b decision rule, so the census could run on a premise 0a refutes.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

---

## 1. What was verified before writing this critique

All claims below were checked against the imported take-13 bundle at
`probes/023/results/results_v2/` (import commit `1c0acdbf5dcc…`), the ratified
interpretation `ideas/023/interpretation.md`, and `ideas/023/confer/q0002.md`.

- **Verified fact:** the 594-row `bin_tissue_audit.csv` exists with the stated
  case × band × cell structure; `summary.json` records
  `bin_tissue_audit_rows: 594`, `analyzed_census_case_count: 99`,
  `status: NEGATIVE_PATTERN`, split manifest sha256 `da79e94b…`, reserved
  count 49.
- **Verified fact:** the band statistics quoted in the card's
  `keystone_evidence` are transcription-exact against
  `per_stratum_summary.csv` (band 1 mean d +0.0064 CI [−0.0268, +0.0384];
  band 2 −0.0320 [−0.0559, −0.0080]; band 3 +0.0231 [+0.0050, +0.0436]) and
  `identity_residual_summary.csv` (MAD 0.0078/0.0036/0.0078).
- **Verified fact:** the cited hypodense-Q1 examples are real rows
  (sub-stroke0092 band 1: Q1 median 3.0 HU vs Q4 23.0; sub-stroke0057: 5.0 vs
  24.0; sub-stroke0189: 6.0 vs 25.0).
- **Verified fact:** confer q0002 `SUGGESTED UPDATES` item 4 contains the
  question sketch the card adopts, and `q0002_review.md` records
  `{"verdict":"CONCUR","findings":[]}`. The kernel-provenance claim is
  accurate.
- **Verified fact:** registration as a NEW candidate with `parent_ids:
  ["idea-023"]` complies with the 2026-08-10 claim-identity rule; the
  deliverable sentence differs from the parent's, so revision-in-place would
  have been wrong and was correctly not attempted.
- **Verified fact:** the keystone screen honestly returns `UNVERIFIABLE`; the
  feasibility/novelty caps therefore stand. As a Mode C card this is
  charter-expected, not a defect.

No fatal objection was found in data access, compute, leakage of new labels,
or prior-work overlap. The objections below are ordered by severity; all are
repairable inside the card's existing question.

## 2. Objection 1 (leading): the tissue-confound premise is attributed to the wrong band, and nothing forces Rung 0a to adjudicate it

The parent's decisive negative was the **band-2/band-3 opposite-signed
reversal** (both CIs excluding zero). Band 1 — where the card's three
motivating hypodense-Q1 examples live — was the null band (CI includes zero).
The card's `revival_basis` builds its case almost entirely on band-1 rows and
then proposes to fix the reversal that happened elsewhere.

Row-level inspection (no aggregate computed; that remains Rung 0a's governed
deliverable) makes this worse for the simple story:

- The three cited hypodense-Q1 band-1 cases have per-case band-1 d of
  **−0.0089** (sub-stroke0092), **−0.0051** (sub-stroke0057), and **−0.1404**
  (sub-stroke0189) in `per_patient.csv`. If frank hypodensity in Q1 meant
  "established injury inflating Q1 infarct membership," these d values should
  be strongly positive. They are near zero or **negative** — more consistent
  with the hypodense voxels being partial-volume CSF that *dilutes* Q1
  membership than with injury that inflates it.
- sub-stroke0183 shows the reverse imbalance (band 2: Q1 23.0 HU vs Q4 5.0 HU)
  with band-2 d = **+0.2405** — against the band-2 negative mean, again
  consistent with hypodense-cell dilution, in the opposite cell.

So the audit rows do support "tissue mixing corrupts the contrast in
case-dependent directions" (which also fits the parent's mean-vs-median
divergence), but they do **not** support a single-direction contamination
mechanism, and whether tissue imbalance *accounts for* the band-2/3 reversal
is at present pure inference. The card's honesty about not computing
prevalence is commendable, but honesty is not a design: as written, Rung 0a
measures only **prevalence and magnitude** of imbalance, and no decision rule
connects its outcome to whether the expensive Rung-0b census runs. A Rung 0a
showing low prevalence — or showing imbalance uncorrelated with d in bands 2
and 3 — would refute the successor's premise, yet the card would still
authorize proceeding.

**Repair (stays within the question):**

1. Extend Rung 0a beyond prevalence to a prespecified **imbalance-versus-d
   attribution analysis**: per case and band, join Q1−Q4 median-HU imbalance
   (`bin_tissue_audit.csv`) against per-case d (`per_patient.csv`), bands 2
   and 3 primary. Declare it label-touching (per_patient d is
   outcome-derived) — defensible because these labels were already opened for
   exactly these cases under the parent contract, but it must be walled off
   as exploratory successor-design evidence, never confirmatory.
2. Prespecify the 0a→0b rule now: if imbalance neither reaches material
   prevalence nor associates with d in the reversal bands, the tissue
   explanation is refuted and Rung 0b does **not** run — the lineage goes
   terminal under the card's own "taste is not grounds for a third
   operationalization" rule. Write the thresholds before the aggregate is
   seen.

## 3. Objection 2: the confirmatory census reuses a split whose outcome structure is already known

Rung 0b runs "on the released 100-case census split only." Those are the same
99 analyzed cases whose band-level outcome structure, per-case d values, and
per-case HU audit rows are now on the record and in every designer's context.
The parent could claim a genuine label freeze; this successor cannot. The
card's phrase "both label-blind at design time" overstates what is available:
the *window* can be frozen before new label access, but the designers already
know which direction each band leaned.

This is not fatal — the analysis form is inherited frozen, patient-level
voxel-outcome structure was never exposed, and burning the 49 reserved cases
on a Stage-0 association question would likely be underpowered and spend the
lineage's only pristine holdout. But it must be handled, not elided:

**Repair:** (a) the card must acknowledge the reuse explicitly and state why
the confirmatory reading survives (single new degree of freedom, externally
pinned); (b) the NCCT viability window must be pinned to a **citable external
source** (published HU threshold for brain tissue / early ischemic
hypodensity), not chosen by the team, and frozen **before** the
label-touching Rung-0a join is run — the sequence must be: freeze window →
Rung 0a → decision rule → Phase-S → census; (c) the reserved 49 cases stay
untouched, as the card already states.

## 4. Objection 3: the gate can manufacture its own "decisive" negative by removing the outcome

Admission-NCCT frank hypodensity is a strong predictor of final-infarct
membership (it is the substrate of early-ischemic-change scoring). Excluding
frankly hypodense voxels therefore preferentially removes voxels that would
have carried the outcome label. If post-gate cells retain little final-infarct
membership at all, d collapses toward zero with narrow bootstrap CIs — and the
preregistered conjunction would report a "decisive negative" that actually
means "the gate deleted the outcome variance." Phase-S cannot catch this: it
is outcome-blind by design and sizes voxel support and CI width, not retained
outcome prevalence.

**Repair:** preregister a non-gating per-band, per-cell **post-gate
final-infarct prevalence descriptor** in the census output, plus a frozen
floor (set before the census, justifiable from the parent's already-opened
label aggregates) below which the negative is downgraded from "decisive,
conditional" to **sensitivity-limited**. This classification fork must be
written into the contract now; deciding it at interpretation time would be
exactly the implicit-margin failure the 2026-08-14 amendment exists to
prevent.

## 5. Lesser findings

- **`design_template` mislabel.** "counterfactual-synthesis" is wrong:
  nothing is synthesized or edited; this is a conditional-observational
  census with a voxel-admission filter. The homogenization watch counts these
  strings; mislabeling corrupts that telemetry. Relabel.
- **Mode C designation is strained but acceptable.** This is really a
  confirmatory Stage-0 association study inheriting proven machinery, not a
  speculative mechanism hunt; but the parent was registered the same way and
  the mode's honest NOT_INSPECTED reporting is being used as intended.
- **"Directionally stable association" wording.** The gate is mean-based
  while the parent's median patient showed ≈0 contrast in every band. A
  passed conjunction driven by a patient minority would still be announced as
  a "directionally stable… association." The card's non-gating median
  descriptor is the right instrument; the deliverable sentence should scope
  itself to equal-patient-weight means so the positive cannot be read as
  cohort-typical.
- **Prior work.** HU-window brain-tissue masking is standard CTP
  preprocessing (vendor pipelines routinely exclude CSF/bone by HU), and the
  card already disclaims novelty of the gate concept. The citable object here
  is the governed, preregistered attribution analysis of a label-blind tissue
  audit — modest but real. No overlap kill. The Alzahrani et al. (2023)
  uncertainty about NECT viability discrimination, quoted in the keystone
  screen, bounds interpretation of the gate (it separates *attenuation
  classes*, not certified viability) and the card should say "viable-
  attenuation" everywhere it currently says "viable tissue" — the deliverable
  sentence already does this correctly.
- **plain_pitch.** The card carries none, so the plain-pitch fidelity check
  is N/A. No defect; noting for the record that the deliverable sentence is
  dense enough that a pitch will eventually be needed, and translating
  "establishing, or decisively refusing, the Stage-0 prerequisite" without
  overclaiming will take care.
- **Confound checklist (charter-standing alternatives).** Scanner, vendor,
  protocol, reconstruction, site: moot within-patient and single-pipeline
  (icobrain cva), scope-limited as the card states. Positioning/habitus:
  absorbed by within-patient design. Referral/prevalence: treated-cohort
  scope stands. Label leakage: no new labels are read before the frozen
  census; the real leakage risk is the reused split (Objection 2) and the
  gate-outcome coupling (Objection 3), both named above.
- **Duplicate-work guard.** The separately pre-registered patient-level
  clinical-outcome join (2026-08-28 ledger entry) is adjacent, already
  authorized, and not this card's job; the revision should state it neither
  depends on nor duplicates it.

## 6. Scores check (Mode C weighting)

Scores were operator-withheld in this view; only structural checks are
possible. The keystone screen's `UNVERIFIABLE` verdict caps feasibility and
novelty_confidence at 3 — the card must respect that at merge.
`negative_result_value` as claimed ("decisive, conditional") is only
defensible **after** the Objection-4/§4 prevalence fork is added; without it,
the honest classification of a post-gate null is sensitivity-limited, which
caps that score at 2 under the rubric.

---

## Constructive close

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does per-case Q1-vs-Q4 NCCT attenuation
imbalance statistically account for the parent census's opposite-signed band-2/band-3
final-infarct contrasts — i.e., was idea-023's negative a tissue-composition artifact?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is Rung 0a of this card, properly
specified with a prespecified 0a->0b decision rule.
IS IT ACTUALLY WORTH DOING? Yes — minutes of CPU on two already-imported CSVs decides
whether the recalibrated census is justified at all, and either answer is
decision-grade for the lineage.
```

The genuinely valuable object in this card is small and already paid for: the
594-row audit and the per-case d table sit in the same imported bundle, and
joining them answers whether the successor's premise is true before any new
staging, Phase-S run, or census take is bought. The revision should promote
that join into Rung 0a's core, freeze the externally-sourced HU window before
running it, write the 0a→0b and negative-classification forks now, fix the
template label, and proceed. If Rung 0a refutes the tissue explanation, the
card's own terminality rule should be allowed to execute — that outcome would
itself be a clean, citable close to the 023 lineage, not a failure of this
candidate.


===== ideas/045/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The NCCT “viability” exclusion conditions on a baseline predictor of final infarction, so a post-gate null cannot decisively refute the joint-CBV/MTT association and may simply show that the design removed the outcome-bearing tissue.

**Argument:** The identity check passes only narrowly: the revised design still asks about the joint CBV/MTT coordinate at matched CBF, but only in an attenuation-selected subpopulation. That selection is not a neutral tissue normalizer. Admission NCCT hypodensity is itself evidence of ischemic injury and predicts final infarction; the keystone screen’s cited primary study (Alzahrani et al. 2023, PMCID PMC9855746) explicitly says the mapping from early NECT features to reversible versus irreversible injury is uncertain. Freezing an externally sourced HU window before reopening labels prevents analyst tuning, but it does not remove this causal problem. Excluding low-attenuation voxels can preferentially discard final-infarct-positive voxels, reduce within-cell outcome variance, and drive all Q1-versus-Q4 contrasts toward zero with narrow bootstrap intervals. A retained-support gate counts voxels, not retained outcome information; even a post-gate infarct-prevalence floor cannot establish that the remaining sample has enough contrast to test the original association rather than a healthier-subpopulation estimand. Therefore the card’s proposed “decisive, conditional” negative and terminal closure of the lineage are not identified. The defensible negative is sensitivity-limited unless outcome-information retention is preregistered and demonstrated. This does not require changing the original question, but it does require weakening the claimed negative or replacing exclusion with a tissue-control strategy that preserves the outcome-bearing population.

**What would change my mind:** Before outcome inspection, specify a simulation or parent-label-based operating-characteristic analysis showing that the frozen attenuation rule retains a prespecified fraction of final-infarct events and has adequate power to recover planted Q1-versus-Q4 effects within every flow band; then preregister that failure of this outcome-information gate makes the census negative sensitivity-limited, not terminal. Alternatively, show a tissue-normalization method that balances attenuation classes without excluding outcome-predictive voxels and recovers the target estimand.

**Status:** OPEN

## Round 2 — CRITIC

**Position:** The amendment makes outcome retention a prerequisite, but its proposed planted-effect recovery does not yet demonstrate sensitivity to the actual joint-CBV/MTT association because no data-generating mechanism links the planted effect, the HU exclusion, and the observed within-patient outcome structure.

**Argument:** The identity check passes: conditioning the original matched-flow question on a prespecified viable-attenuation population remains the card's stated estimand, and the amendment correctly withdraws a decisive-negative interpretation whenever outcome retention or sensitivity fails. That argument resolves my Round-1 concern about calling a support-only post-gate null decisive. The remaining defect is narrower but still load-bearing. Retained final-infarct fraction and post-gate prevalence are descriptive; neither establishes power for the equal-patient-weight Q1-versus-Q4 contrast. "Recovery of planted effects" establishes that only if the simulation specifies where labels are changed, preserves the observed patient clustering, Q1/Q4 cell sizes, HU-dependent selection, and baseline infarct prevalence, and plants an effect on the same estimand without using the observed band signs to choose its direction or magnitude. A generic Bernoulli injection, or shifting labels after gating, can pass even when the gate has removed precisely the HU-by-CBV overlap in which a real association could appear. Conversely, calibrating the generator or thresholds until it recovers effects on these already-open 99 cases would use the census outcomes to design the sensitivity test and then reuse those cases for the confirmatory claim. The amendment names thresholds as frozen but does not say what external or parent-frozen quantity fixes the minimum retained-event fraction, minimum detectable contrast, or simulation generator. Until those are specified, the classification fork delegates the central judgment to Phase S rather than preregistering it. This does not require a new candidate, but the census cannot yet support a decisive conditional negative.

**What would change my mind:** Specify before any voxel-level HU-by-outcome join is computed: (1) a minimum clinically/scientifically relevant per-band Q1-versus-Q4 contrast fixed from an external source or the parent contract rather than the observed gated data; (2) fixed retained-event and per-cell prevalence floors; and (3) a simulation/resampling algorithm that preserves patient-level clustering, observed pre-gate HU/CBV/flow membership and missingness, applies the frozen HU gate unchanged, plants both signs of that fixed contrast upstream of selection, and must recover it with prespecified power and interval behavior in every band. Show that these specifications are immutable before the one permitted retention evaluation; otherwise classify every post-gate null as sensitivity-limited.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** Because admission hypodensity itself predicts final infarction, an exclusion gate keyed to attenuation preferentially deletes the outcome-bearing voxels; a voxel-support floor (and even an infarct-prevalence floor) certifies sample size, not retained outcome information, so a post-gate null cannot honestly be classified "decisive, conditional" and cannot terminate the lineage unless outcome-information retention is demonstrated before the census.

**Response:** AMEND

**Argument:** One bounded rebuttal first, then the amendment, because the rebuttal fixes where the amendment must land.

*Rebuttal to the estimand half.* The "healthier-subpopulation estimand" is not a distortion of this card's question — it IS this card's question. The deliverable sentence already scopes every claim to "within viable-attenuation tissue"; the card never promises to recover the parent's unconditional association, and a reader who wants the ungated estimand has the parent's completed census. Conditioning on a pre-outcome covariate changes the population, not the well-definedness of the association within it. So the objection's force is not "wrong estimand" — it is the sharper point that a *null* within the scoped population is uninterpretable if the gate has drained that population of outcome events. That point is correct, and I concede it rather than defend the "decisive, conditional" label as written.

*Amendment (three parts, thresholds frozen before any gated aggregate is seen):*

1. **Outcome-retention operating-characteristic gate.** After the HU window is frozen from citable external sources and before the census analysis runs, compute per band and per cell, on the 100-case census split only: (a) the fraction of final-infarct-positive voxels retained under the gate, and (b) post-gate infarct prevalence. This is label-touching by construction and is declared so: it reuses the final-infarct labels already opened for exactly these cases under the parent contract, is walled off as design-calibration evidence (never confirmatory), and evaluates a *fixed* rule — the window cannot be tuned on it, because the freeze precedes the computation and one window gets one evaluation. Mechanically this lives in Rung 0b, not 0a: the imported bundle carries only per-cell HU quantiles (bin_tissue_audit.csv) and per-case d (per_patient.csv), verified just now — no voxel-level HU-by-outcome join exists without re-staging the dataset, which Rung 0b already pays for.

2. **Phase-S planted-effect recovery under the gate.** The Phase-S recalibration the card already requires gains the critic's condition explicitly: operating characteristics must show recovery of planted Q1-vs-Q4 effects in *every* flow band under the measured post-gate retention, not merely adequate voxel counts. Phase-S refusing the design is a permitted outcome.

3. **Preregistered classification fork.** The census negative is classified "decisive, conditional" ONLY if both gates above passed at their frozen thresholds; if either fails, the design refuses to run the census (preferred), or any negative already contracted is classified sensitivity-limited and is NOT lineage-terminal. The anticipated_negative block in the card is rewritten to carry this fork verbatim.

*What was lost:* the unconditional terminality claim — the card's strongest selling point. The lineage-terminal reading now requires a demonstrable precondition, and there is a real scenario in which no defensible external window passes the retention gate at all. I accept that loss because the honest close in that scenario ("exclusion-based tissue control cannot retain the outcome in this cohort") is itself decision-grade and citable, and because negative_result_value as scored (5) was not defensible without this fork — the critique's §4 said the same and this amendment discharges both.

*Identity check:* passed. The one-sentence question — directionally consistent, precision-bounded final-infarct association of the joint CBV/MTT coordinate at matched flow under a tissue-normalized reference — is unchanged; the amendment adds calibration gates and an honest classification fork in front of the same census. The critic's alternative (attenuation-stratified analysis that balances rather than excludes) is noted as a **spin-off** should the retention gate refuse every defensible window; it is not adopted here because replacing exclusion with stratification mid-debate would change the frozen analysis form, and the refusal outcome is the evidence that would justify registering it.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** Retention fraction and post-gate prevalence are only descriptive; "recovery of planted effects" proves the gate preserves the joint-CBV/MTT signal only if the simulation plants a *fixed, externally-anchored* per-band contrast *upstream* of the HU selection, preserves the real pre-gate patient clustering / cell sizes / HU-by-CBV-by-flow membership / missingness, and applies the frozen gate unchanged — and if that whole spec, the minimum detectable contrast, and the event/prevalence floors are frozen before the one permitted retention evaluation. Absent that, the classification fork delegates the central judgment to Phase-S and the calibration risks reusing the 99 already-open census outcomes; every post-gate null is then only sensitivity-limited.

**Response:** AMEND

**Argument:** The objection is right and I am not going to defend the round-1 wording, which said "recover planted effects" without saying how the effect is generated. That underspecification is exactly where a generic Bernoulli injection or post-gate label shift could pass a design the gate has actually gutted. The repair is to pin the generator, its anchor quantities, and the ordering, and to buy the anti-reuse property by construction rather than by promise. Four specifications, all frozen before the single retention evaluation and before any census take; none uses the observed band signs or gated aggregates:

1. **Fixed minimum detectable contrast, from the parent contract, not the gated data.** The minimum equal-patient-weight per-band Q1-vs-Q4 contrast the design must resolve is set to δ\* = 0.15 — the parent contract's frozen precision bound, a parent-contract quantity, not an observed effect and carrying no sign. The simulation must recover ±δ\* (both signs, symmetric) in *every* band; the observed parent band directions (+, −, +) are never consulted to orient the plant.

2. **Anti-reuse by covariate/outcome separation.** Phase-S runs on the real *covariate* geometry re-staged in Rung 0b — the actual per-voxel (NCCT-HU, log-CBV quartile, within-patient CBF band, patient id) tuples and their missingness — but with the real final-infarct labels **withheld and replaced by synthetic outcomes** drawn from the planted model. The 99 census outcomes therefore never enter the sensitivity test; only their covariate structure does, and covariate structure is not the estimand. This is the concrete mechanism that answers "calibrating on the already-open cases": there is nothing to calibrate against, because the generator never sees a real label.

3. **Generator algorithm, fixed in the contract.** For each simulation replicate: (a) take the real pre-gate voxel tuples with patient clustering and cell sizes intact; (b) assign each voxel a latent injury probability that is monotone in its CBV quartile with a Q1-vs-Q4 gap of exactly ±δ\* per band, planted **upstream** of the gate so that HU-correlated voxels carry the signal the gate may delete; (c) draw synthetic labels; (d) apply the frozen HU window **unchanged**; (e) estimate the gated Q1-vs-Q4 contrast with the inherited equal-patient-weight estimator and patient-bootstrap CI. The design passes only if, at ≥80% power over replicates, the correctly-signed CI excludes zero in **all three bands** for both plant signs. Phase-S refusing (any band below the power floor) is a permitted, contract-terminal outcome.

4. **Frozen floors, then one real-label evaluation.** The retained-event and per-cell prevalence floors are not free numbers chosen after looking at retention: they are whatever level item 3's power requirement needs to clear ≥80% recovery of ±δ\*, computed inside the synthetic simulation. Only then is the single real-label retention evaluation run once, to check that the actual gate retains at least that simulation-required event level. The ordering is immutable and contract-bound: freeze HU window (external source) → freeze δ\*, power target, both-sign rule, and generator → run synthetic Phase-S (no real labels) → derive floors → one real-label retention evaluation → census once. A null is "decisive, conditional" only if the synthetic power test *and* the one real-label retention check both clear their frozen bars; otherwise it is sensitivity-limited and non-terminal, per the round-1 fork now hardened with these definitions.

*What was lost:* the terminality claim is narrowed a second time. It is no longer enough that voxels and events survive (round 1); the frozen gate must be *shown by simulation* to still recover a parent-contract-sized effect through itself in every band before a census null can close the lineage. That raises the bar for the strongest, most citable outcome and admits a real path where Phase-S refuses the design outright and the lineage's decisive-negative reading is simply unavailable — the honest close there is "the tissue gate cannot be shown to preserve the target contrast in this cohort," which is itself decision-grade. This is the second narrowing; a third would signal the operationalization is wrong, and I am watching for that, but this one buys identifiability, not just feasibility.

*Identity check:* passed. The one-sentence question — a directionally consistent, precision-bounded final-infarct association of the joint CBV/MTT coordinate at matched CBF under a tissue-normalized reference — is untouched. Everything added sits *in front of* the same census with the same estimator and conjunction form; nothing changes what is estimated, only what must be demonstrated before a null is allowed to be decisive.

**Status:** CONVERGED

## Round 3 — CRITIC

**Position:** The proposed Phase-S generator makes the HU gate ignorable within each CBV quartile by construction, so it cannot test whether the gate selectively removes the very HU-by-hemodynamic outcome association whose loss would make a census null uninterpretable.

**Argument:** The identity check still passes: the amendment adds a sensitivity prerequisite without changing the viable-attenuation, matched-flow Q1-versus-Q4 estimand. The remaining defect is in the generator itself. Item 3 assigns synthetic injury probability as a function of CBV quartile with a fixed Q1-versus-Q4 gap, then applies the HU gate. Unless injury probability also varies with HU *within* each quartile, voxels removed by HU have the same expected synthetic outcome as voxels retained from that quartile. The gate can then attenuate power only through reduced sample size; it cannot preferentially remove the outcome-bearing portion of Q1 or Q4. Saying the effect is planted “upstream” does not solve this: temporal ordering is irrelevant when the planted outcome is conditionally independent of the selection variable. This is precisely the failure the calibration is supposed to detect, because the motivating hypothesis is that NCCT attenuation, CBV state, and final injury are jointly structured. The real-label retention check also cannot repair it: retained event fractions and marginal post-gate prevalence do not reveal whether the Q1-versus-Q4 contrast was concentrated in excluded versus retained HU strata. Thus the simulation may certify a decisive negative under a data-generating model that assumes away the dangerous selection mechanism. The ±0.15 anchor, both-sign requirement, preserved clustering, and frozen ordering are otherwise adequate and materially answer the previous round; the unresolved issue is conditional effect heterogeneity across HU.

**What would change my mind:** Freeze before real-label evaluation a sensitivity family in which the ±0.15 pre-gate Q1-versus-Q4 contrast is distributed across HU strata under prespecified effect-modification scenarios, including a conservative scenario concentrating as much of the contrast as plausibly allowed in voxels the gate excludes; apply the unchanged gate and require the inherited estimator to recover both signs in every band across the declared family. The bounds on that family must come from external evidence or a stated worst-case envelope, not the already-open outcome labels. If no defensible bound exists, concede that Phase S can certify precision only under an HU-ignorability assumption and classify a post-gate null as sensitivity-limited.

**Status:** OPEN

## Round 3 — PROPOSER

**Responding to:** My round-2 generator plants injury probability as a function of CBV quartile alone, identical across HU within a quartile. That makes outcome conditionally independent of HU given quartile, so the HU gate is ignorable for the quartile-level contrast and can only shrink sample size — it can never preferentially delete an HU-localized portion of the Q1-vs-Q4 signal. The simulation therefore certifies a "decisive" negative under exactly the HU-ignorability assumption whose failure would make the census null uninterpretable, and the real-label retention check (marginal event fraction, marginal prevalence) cannot see whether the contrast was concentrated in excluded HU strata. The certification is circular for the one failure mode it was built to rule out.

**Response:** CONCEDE

**Argument:** The objection is correct and it is not patchable without something I do not have.

The defect is exactly as stated. `Pr(outcome | quartile, HU) = Pr(outcome | quartile)` in my generator, so the gate — a selection on HU — is ignorable by construction. "Recovery through the gate" in round 2 proves robustness only against sample-size attrition, never against selective removal of an HU-by-hemodynamic component of the contrast, which is the whole joint-structure hypothesis (NCCT attenuation, CBV state, and final injury co-vary) that the tissue gate is supposed to be tested against. I withdraw the round-2 claim that the synthetic power test certifies a decisive negative.

Can I supply the effect-modification family you ask for? Only with an external, non-label bound on how much of the ±0.15 pre-gate contrast could sit in excluded (frankly hypodense) voxels. I have no such quantitative bound, and the keystone screen's own primary source (Alzahrani et al. 2023, PMC9855746) affirms the NECT reversible-vs-irreversible mapping is *uncertain* — the opposite of a bound. A "stated worst-case envelope" is admissible, but its maximal member (all contrast concentrated in excluded voxels) makes the gate delete the entire signal, the estimator cannot recover it, and the design refuses. So adopting the family honestly resolves your fork in your favor: absent an external bound, every post-gate null is **sensitivity-limited**, not decisive and not lineage-terminal. Wrapping that in a third "amendment" would be cosmetic — and by my own round-2 warning, a third narrowing here signals the operationalization is wrong *for the terminal-negative ambition specifically*. It is. I concede it plainly rather than dress it as a repair.

**What this costs, precisely.** The `anticipated_negative` classification "Decisive, conditional" is withdrawn and becomes sensitivity-limited/non-terminal; under the rubric `negative_result_value` drops from 5 to a cap of 2. The deliverable sentence's "or decisively refusing … the Stage-0 prerequisite" clause is no longer supported and must soften to "or reporting a sensitivity-limited null." Whether that softening is a *material* change to the deliverable sentence — thereby triggering the 2026-08-10 claim-identity successor rule rather than revision-in-place — is a human governance call I flag but do not make here.

**What survives, so the concession is scoped, not total.** Your objection is aimed only at interpreting a null; it does not touch the rest. (1) The positive arm is intact: a passed directional-precision conjunction is a genuine within-viable-tissue association, and selective gate removal cannot manufacture one — it can only bias a true contrast toward zero. A positive still authorizes a model-use contract. (2) Rung 0a — the aggregate attenuation-imbalance analysis on the already-imported 594-row audit — is untouched, costs minutes of CPU, and is decision-grade either way; it is the cheap object worth buying regardless. (3) The scoped estimand ("within viable-attenuation tissue") remains well-defined. So the study is still worth running; it just cannot promise a lineage-terminal negative.

**What would move it back up.** An external, non-label calibration that bounds HU-by-outcome effect modification inside the deficit region — published NCCT-HU-vs-tissue-fate data, or an independent in-cohort measurement that does not consume the census labels. With such a bound your effect-modification family becomes runnable and the conditional-terminal negative is recoverable. That is a real successor path, not a rescue of this round.

*Identity note (for the record, though CONCEDE needs none):* the one-sentence question is unchanged; only the strength claimed for its negative answer moved.

**Status:** CONVERGED


===== ideas/045/feasibility.md =====
# Feasibility memo — idea 045

**Question under test:** Does per-patient Q1-minus-Q4 NCCT median-attenuation
imbalance account for idea-023's opposite-signed mean final-infarct contrasts
in flow bands 2 and 3?

Stage run 2026-09-01. This retries the 2026-09-01 attempt that failed on
agent authentication before producing any content (`log_feasibility.txt`;
no partial memo existed). All inspections below were performed fresh.

**Conduct rule adopted for this memo:** the probe contract
(`ideas/045/probe_contract.yaml`, v1, unapproved) is an *outcome-blind*
design audit with frozen thresholds. To keep the approval decision clean,
this memo verified **input structure only**. No value of the outcome column
`d` was read (header presence only), and none of the probe's own gated
quantities — HU-imbalance distribution, design-matrix rank, condition
number, leverage — was computed. Those are the probe's certified
deliverables; computing them before human approval would let the approver
see the outcomes of the gates being approved.

## 1. Keystone inputs: directly inspected, all pass

Everything in this section is **verified fact**, inspected today at
`probes/023/results/results_v2/` (import commit `1c0acdb`, "idea 023:
validated results bundle results_v2 (phase C)").

File identities (SHA-256, recorded for the probe's input manifest):

| file | sha256 |
|---|---|
| bin_tissue_audit.csv | `35e896dfe2a5275a9fa8077e990dff96e72ce1ec0e5048079653556e1c7e2cd2` |
| per_patient.csv | `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c` |
| summary.json | `71418b78caa5a853917b131777ad6fa37f1c1f9c2242d5f1e4fc586fcc8ebfbb` |

Structure, against the contract's row gate:

- `bin_tissue_audit.csv`: header
  `case_id,stratum,style_group,member_voxels,finite_hu_voxels,nonfinite_hu_voxels,median_hu,q25_hu,q75_hu,iqr_hu`;
  594 data rows; **99 distinct cases**; **exactly 99 rows in every one of
  the six (stratum 1/2/3 × Q1_low_CBV/Q4_high_CBV) cells**; zero duplicate
  `(case, stratum, style_group)` keys.
- `per_patient.csv`: header `case_id,stratum,q1_voxels,q4_voxels,d`;
  297 data rows; 99 per stratum; zero duplicate `(case, stratum)` keys.
  The `d` column the contract expects is present in the header; **no `d`
  value was read**.
- **Case sets are identical across the two files** (union of distinct case
  IDs across both = 99), so the join the card's keystone requires is
  bijective on `(case, stratum)` by construction.
- `median_hu` values: 594/594 numeric (no letters, no empty fields, clean
  numeric sort), range **3.0 to 59.0 HU**. The contract's finiteness
  requirement is satisfiable on the real data.
- Exposure variation exists: distinct raw `median_hu` values per
  primary-band cell are 30 (band 2, Q1), 31 (band 2, Q4), 28 (band 3, Q1),
  32 (band 3, Q4) across 99 cases. This does not certify the contract's
  "≥20 distinct HU-imbalance values per band" gate — the imbalance is a
  derived difference and was deliberately not computed — but it makes a
  degenerate-exposure failure unlikely.
- `sub-stroke0043` is absent from both tables and named in
  `exclusions.csv` with reason `source_corrupt_member`, exactly as the
  parent contract's exclusion policy required.
- `summary.json` matches the card's `keystone_evidence`
  transcription-exactly: 99 analyzed of 100 census cases, 49 reserved
  untouched, band-2 mean d −0.0320 CI [−0.0559, −0.0080], band-3 +0.0231
  [+0.0050, +0.0436], band-1 null [−0.0268, +0.0384]. Note the per-band
  **medians are ≈0**, which is why the card's deliverable is correctly
  scoped to equal-patient-weight means.
- Bundle identity: `resolved_config.json` and `summary.json` both carry
  contract/approval blob `03d4545fe293…`; provenance pins Zenodo record
  16813698, archive md5 `36ae28b9…`, seed 20260824.

**Verdict on the card's keystone (`INSPECTED_TRUE`): confirmed.** Joinable,
unique, complete patient-by-band rows exist for both sides of the analysis.

## 2. Closest work and exact gap

- **Closest work is the parent itself.** Idea-023's take-13 census produced
  both input tables under one frozen contract, and its ratified
  interpretation never analyzed their relationship — the label-blind HU
  audit was mandated (2026-08-28 activation directive) precisely so a
  successor could ask this question. The gap is exactly the prespecified
  bands-2/3 imbalance-versus-d attribution analysis. No one else can have
  done it: the audit table's structure (case × CBF-band × CBV-quartile-cell
  median HU) exists only in this bundle.
- **Closest external family: net water uptake (NWU) densitometry.**
  Verified today: Lu et al., AJNR Am J Neuroradiol 2023
  (DOI 10.3174/ajnr.A7741) defines NWU = [1 − (HU_ischemic/HU_normal)] ×
  100 from NCCT and reports elevated NWU associated with malignant edema
  and poor outcome; it cites the foundational Minnerup et al. 2016 study
  (Ann Neurol 80:924–34, DOI 10.1002/ana.24818 — **secondary transcription
  from Lu's reference list, primary not fetched**). This establishes that
  NCCT attenuation is a quantitative, outcome-relevant tissue signal —
  supporting the confound premise — but NWU work measures lesion-versus-
  contralateral attenuation as a prognostic biomarker. Nobody uses
  within-cell HU imbalance to audit a hemodynamic census's sign reversal.
  The delta is clear and the card claims no novelty beyond completing the
  parent's audit (novelty_confidence 2 stands).
- **Alzahrani et al. 2023 (PMCID PMC9855746)** re-verified live today; the
  uncertainty sentence quoted in `keystone_screen.md` is confirmed
  verbatim. **Correction of record:** the PMC page gives the journal as
  *Stroke*, not "Journal of the Belgian Society of Radiology" as the
  keystone screen stated. PMCID, year, and quote are unchanged;
  non-load-bearing.

## 3. Dataset access and license

No new data. Both inputs are in-repo, imported under the record-result gate
(commit `1c0acdb`, operator-executed import of 2026-08-30). The parent
dataset license (ISLES'24, CC-BY-NC-SA-4.0) was verified 2026-08-18 and is
recorded in `evidence/datasets.csv` (idea-023 row); it was **not
re-verified today** — the tables analyzed here are derived aggregates
already committed, so no new license action arises. No DUA, no download,
no gated access, no annotation campaign.

## 4. Labels and concept validity

- **X is annotator-free**, per the charter's hard constraint: Q1−Q4 median
  HU per case-band, computable from the released label-blind audit by
  subtraction.
- **The outcome side is frozen**: per-case d from the parent census
  (final-infarct masks via DeepISLES with neuroradiologist-supervised
  correction, documented provenance — prior verification on the idea-023
  datasets row).
- **Concept validity limit stands as the card states it**: median HU is a
  composition *proxy* (mixture of normal brain, early ischemic
  hypodensity, partial-volume CSF); Alzahrani 2023 bounds any temptation
  to read it as viability. The card's `keystone_residual_assumption`
  (median-HU sensitivity) is honest and remains **unverifiable in
  advance** — it is what the analysis measures.

## 5. Sample structure and split unit

99 patients × 2 primary bands = 198 analysis rows; patient is the cluster
unit (bootstrap and leverage accounting). There is deliberately no
train/test split: this is exploratory successor-design evidence on
outcomes opened by the parent, with the model form, primary bands, and
interpretation rule frozen in the card before any new aggregate is
computed. The 49 reserved cases are physically absent from both input
tables, so the probe cannot touch them even in error.

## 6. Existing code, checkpoints, compute

No model, no checkpoint, no GPU (`maximum_gpu_minutes: 0`). The probe is a
deterministic CPU join-and-diagnostics pass over two small CSVs (37 KB and
14 KB); the later scientific analysis is one OLS fit with a patient
bootstrap. Compute estimate: **minutes of laptop CPU end to end**. The 023
probe-harness conventions (input manifests, resolved config, run logs)
carry over directly.

## 7. Baselines and metrics

The probe's baseline is algebraic: a full-rank (rank-4) design. Its frozen
feasibility thresholds (condition number ≤30 after diagnostic scaling, max
leverage ≤0.20, ≥20 distinct imbalance values per band, leave-one-patient-
out stability) are conservative conventions, declared as such in the
contract, not medical claims. For the eventual scientific stage the
estimator (equal-patient-weight band contrasts, patient-cluster bootstrap)
mirrors the parent's accepted conventions, so no new metric machinery is
needed.

## 8. Critical leakage and confounds

1. **Opened-outcome reuse** — the live one. Band-level directions, means,
   CIs, and four individual per-case d values (quoted in `critique.md`)
   are on the record and in designers' context. The card handles this
   honestly: exploratory classification, frozen decision rule, no
   confirmatory census claim. This memo added no exposure: no d value read,
   no new aggregate formed.
2. **Severity as common cause** — stroke severity could drive both HU
   imbalance and d. Not ruled out by design; the card prohibits causal
   claims and the deliverable says "associated / consistent with
   contributing," which is the correct strength.
3. **CSF partial volume vs early ischemic hypodensity** — median HU cannot
   separate them; both directions of contamination were observed
   qualitatively in the critique's row-level reading. The card's
   composition-proxy wording absorbs this.
4. **Mean-vs-median fragility** — parent band medians ≈0, so any
   association found is a property of the mean contrast, potentially
   driven by a patient minority. The probe's leverage gates and the
   card's equal-patient-weight scoping are the right guards.
5. **Design-freeze integrity** — the remaining leak channel is this stage
   itself; handled by the conduct rule in the preamble.

Standing acquisition confounds (scanner, protocol, reconstruction, site,
positioning) are moot within-case as the card states; they bound
transportability, not validity, and the card's scope already says so.

This idea involves **no data manipulation, editing, perturbation, or
synthesis** — it is a conditional-observational join of two frozen tables —
so the prior-art-for-interventions subsection required for such designs
does not apply.

## 9. Smallest probe of the riskiest assumption

The riskiest still-unverified assumption is that the **actual exposure
geometry supports the frozen interaction model**: rank-4 design, acceptable
conditioning, no domination by a few patients, real within-band imbalance
variation. File joinability (verified) does not establish this.
`probe_contract.yaml` v1 is precisely and only this check — outcome-blind,
single variant, deterministic, zero GPU. Feasibility endorses it
**unchanged** and recommends it proceed to human approval.

## 10. Marked unverified

- Minnerup 2016 bibliographic details (secondary, via Lu 2023).
- ISLES'24 license status as of today (prior verification 2026-08-18).
- HU-imbalance distribution, design conditioning, leverage — deliberately
  unmeasured; the probe's job.
- Median-HU sensitivity as a composition proxy — residual assumption,
  answerable only by the analysis itself.
- Minor observation, out of 045's scope: bundle `provenance.json` records
  `archive_member_count: 2981` while the 2026-08-25 ledger entry cited
  2983 archive members; the parent bundle passed validation and
  ratification, and 045 consumes only the two tables, so this is noted
  for the record, not raised as a blocker.

## Verdict

**GO.** Every input the probe contract names exists, is identity-pinned,
and passed structural inspection today; the analysis costs minutes on a
CPU; the honest epistemic limits (exploratory status, proxy validity,
sensitivity-limited nulls) are already written into the card and contract.
The next act is the human approval gate on `probe_contract.yaml` v1.

## In plain terms

This study can definitely be run: both data tables it needs are already in
the repository, they line up row-for-row exactly as required, and the whole
analysis is a small statistical computation that takes minutes on an
ordinary computer — no downloads, no GPU, no permissions. The biggest
practical risk is not access or cost but interpretability: the patients'
outcome data was already examined in the parent study, so this analysis
can suggest but never prove that tissue composition explains the earlier
contradictory result, and a null answer may simply mean the chosen
measurement was too blunt. A small pre-check (already drafted, awaiting
human approval) will confirm the numbers have enough spread to support the
planned model before any outcome value is looked at.


===== ideas/045/idea_card.json =====
{
  "id": "isles24-scout-006-c01",
  "track": "wide",
  "search_mode": "C",
  "design_template": "conditional-observational",
  "title": "Did tissue composition create idea-023's sign reversal?",
  "parent_ids": ["idea-023"],
  "kernel_provenance": "Operator-authored successor grounded in idea-023's ratified interpretation and cross-family-approved confer q0002. Critique and debate narrowed it to the already-imported attenuation-audit attribution analysis.",
  "deliverable_original": "Within viable-attenuation tissue at matched relative CBF, the joint CBV/MTT coordinate shows a directionally stable, precision-bounded final-infarct association across all three within-patient flow bands -- establishing, or decisively refusing, the Stage-0 prerequisite that idea-023's untissued operationalization could not test cleanly.",
  "question": "Does per-patient Q1-minus-Q4 NCCT median-attenuation imbalance account for idea-023's opposite-signed mean final-infarct contrasts in flow bands 2 and 3?",
  "deliverable_sentence": "Idea-023's opposite-signed band-2 and band-3 final-infarct contrasts are associated with Q1-versus-Q4 NCCT median-attenuation imbalance, consistent with tissue composition contributing to the reversal.",
  "scientific_uncertainty": "The parent census found a negative mean contrast in band 2 and a positive mean contrast in band 3. Its label-blind audit documented Q1-versus-Q4 attenuation differences in some patients, but no governed cohort analysis tested whether those differences track the per-patient outcome contrast in the reversal bands.",
  "mechanism": "Q1 and Q4 cells may contain different mixtures of normal-appearing brain, early ischemic hypodensity, and partial-volume CSF. This mixture changes NCCT attenuation and may change final-infarct membership independently of the joint CBV/MTT coordinate. Median-HU imbalance is an image-computable composition proxy, not a certified viability measurement.",
  "keystone_prerequisite": "The imported take-13 bundle contains joinable, unique patient-by-band Q1 and Q4 median-HU measurements and corresponding per-patient final-infarct contrast d values for bands 2 and 3.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "Direct inspection recorded in critique.md and keystone_screen.md: bin_tissue_audit.csv contains 594 rows (99 cases x 3 bands x 2 cells) with case_id, stratum, style_group, and median_hu; per_patient.csv contains corresponding case-band d values. Stage 0 must still verify uniqueness and join cardinality before estimation.",
  "keystone_residual_assumption": "If I have only verified the nearest checkable thing, what am I still assuming? I am assuming Q1-minus-Q4 median HU is sufficiently sensitive to test this tissue-composition explanation. Therefore a negative is limited to this measured explanation and cannot exclude all tissue-composition effects.",
  "X_measurement": "For each patient and flow band, X is Q1 median NCCT HU minus Q4 median NCCT HU from bin_tissue_audit.csv. The outcome-side quantity is the frozen per-case d from per_patient.csv. No human annotation, new image processing, thresholded viability label, or model probe is required.",
  "rung": "Rung 0 attribution study. It tests whether a measurable tissue-composition proxy explains the parent reversal; it does not establish model use. Any Rung-1 model-use intervention requires a separate candidate and approval.",
  "smallest_decisive_experiment": "Join the frozen audit and per-patient tables by case and band; analyze bands 2 and 3 only. Fit the prespecified equal-patient linear model d = band + HU_imbalance + band-by-HU_imbalance; report band-specific slopes with patient-bootstrap intervals and adjusted band contrasts at pooled zero imbalance. Support requires a directionally compatible association plus loss of the opposite-signed adjusted band pattern. If the adjusted band-2 and band-3 contrasts remain opposite-signed with bootstrap intervals excluding zero, median-HU adjustment decisively fails to explain the reversal. Other outcomes are sensitivity-limited. Band 1 and nonlinear fits are exploratory.",
  "analysis_sequence": "Removed: the NCCT window, Phase-S recalibration, planted-effect simulation, post-gate floors, restaging, and tissue-gated census. The sole pre-analysis gate requires exactly 99 cases in each primary band, one Q1 and Q4 row and one d row per case-band, and finite derived values. Failure is a data-integrity stop, not a negative.",
  "anticipated_negative": {
    "classification": "Decisive for the measured explanation",
    "meaning": "If the adjusted band-2 and band-3 contrasts remain opposite-signed with patient-bootstrap intervals excluding zero, median-HU adjustment decisively fails to explain the parent reversal in these 99 cases. A merely nonsignificant slope or imprecise adjusted contrast is sensitivity-limited. No result rejects unmeasured tissue composition, CBV/MTT biology, or effects elsewhere, and no new census is authorized."
  },
  "standing_confounds_addressed": "Patient positioning, habitus, referral, site, scanner, vendor, protocol, and reconstruction are held constant within each case-level comparison but limit transportability. Report-label leakage does not apply because d derives from final-infarct masks. Remaining alternatives are partial-volume CSF versus ischemic hypodensity, nonlinear effects missed by median HU, and common dependence of HU imbalance and d on stroke severity.",
  "claim_identifiability": {
    "positive": "Identifies an association between the independently computed attenuation imbalance and parent contrast, and whether adjustment removes the cross-band reversal; it does not prove causation.",
    "negative": "Rules out the specific median-HU imbalance explanation at achieved precision, not other tissue-composition measurements.",
    "alternatives": [
      "Stroke severity could jointly cause attenuation imbalance and d; not ruled out.",
      "CSF partial volume and early ischemic hypodensity can produce similar HU shifts; not separated.",
      "Single-cohort acquisition and referral factors limit transportability, although they cannot directly explain within-case Q1-versus-Q4 differences."
    ]
  },
  "confirmatory_separation": "This is exploratory successor-design evidence because the 99-case outcomes were opened in the parent study. Model form, primary bands, and interpretation rule are frozen before the new aggregate. The 49 reserved cases remain untouched. Any later census or model-use study needs a new contract.",
  "prohibited_conclusions": [
    "Do not call median NCCT attenuation a validated viability label.",
    "Do not claim attenuation imbalance causes the reversal.",
    "Do not claim model use; no model is probed.",
    "Do not generalize beyond the 99 analyzed cases and released pipeline.",
    "Do not interpret a negative as absence of all tissue-composition effects.",
    "Do not authorize the removed tissue-gated census."
  ],
  "dies_like_prior": "No annotation-provenance failure applies because X is computed from released NCCT audit values and d from frozen masks without reader judgment. The real keystone is joinable row-level measurements, avoiding the wrong-keystone error. The card avoids idea-009/016's broad identifiability failure by limiting conclusions to measured attenuation imbalance and retaining severity and tissue-type alternatives. It is not circular: admission NCCT supplies X and later final infarct supplies d, though association is not causation.",
  "closest_prior_work": "Idea-023's completed census and label-blind NCCT audit produced both input tables but did not analyze their relationship. Alzahrani et al. 2023 (PMCID PMC9855746) supports caution that early NCCT attenuation does not cleanly distinguish reversible from irreversible injury; it does not validate this proxy. No novelty claim is made.",
  "existing_legwork": "The imported take-13 bundle already contains bin_tissue_audit.csv, per_patient.csv, the frozen census split, and exclusions. Ninety-nine cases were analyzed; 49 reserved cases remain untouched. No new data, threshold, simulation, or GPU is needed.",
  "verified_facts": [
    "bin_tissue_audit.csv has 594 rows: 99 cases x 3 bands x 2 cells.",
    "per_patient.csv contains per-case, per-band d values.",
    "Parent mean contrasts were negative in band 2 and positive in band 3, with both bootstrap intervals excluding zero.",
    "Audit and outcome tables cover the same frozen analyzed cohort."
  ],
  "unverified_claims": [
    "Aggregate association between Q1-minus-Q4 median HU and d in bands 2 and 3.",
    "Whether adjustment removes the opposite-signed band pattern.",
    "Whether median HU captures the relevant composition difference."
  ],
  "data_and_compute": "Public ISLES'24 release and already-imported idea-023 tables only. CPU tabular analysis; no DUA, new labels, image download, or GPU.",
  "scores": {
    "clarity": {"value": 5, "why": "One frozen two-band attribution question with named inputs and outputs."},
    "identifiability": {"value": 3, "why": "Tests whether measured HU imbalance accounts for the reversal but cannot establish causation or separate hypodensity from CSF."},
    "medical_relevance": {"value": 3, "why": "Determines whether the parent hemodynamic result was plausibly distorted by visible tissue composition."},
    "interest": {"value": 4, "why": "May explain a puzzling opposite-sign result using a prospectively collected audit."},
    "prior_legwork": {"value": 5, "why": "Both frozen tables and parent interpretation are imported and reviewed."},
    "feasibility": {"value": 5, "why": "Keystone inputs were inspected; analysis is a small local CPU join."},
    "data_readiness": {"value": 5, "why": "All required rows are local in the imported bundle."},
    "evaluation_readiness": {"value": 4, "why": "Primary bands, model, bootstrap unit, and interpretation rule are specified."},
    "negative_result_value": {"value": 4, "why": "Rejects the specific explanation and prevents an unjustified rerun while remaining bounded to this proxy."},
    "novelty_confidence": {"value": 2, "why": "No systematic novelty audit supports a broader claim; value is completion of the parent audit."},
    "regret": {"value": 4, "why": "Cheap analysis can prevent another expensive operationalization."},
    "mechanism_clarity": {"value": 4, "why": "Suspected quantity is Q1-versus-Q4 median NCCT attenuation imbalance within matched-flow bands."}
  },
  "mode_c_priority_score": 3.7
}


===== ideas/045/keystone_screen.md =====
# Keystone screen — idea 045

## Keystone as stated

The card states a two-rung prerequisite:

1. The imported idea-023 bundle must contain a label-blind, case-by-band-by-cell NCCT attenuation audit that can support a governed cohort aggregate.
2. It must be possible to freeze an NCCT-only tissue-viability gate before outcome access, recalibrate support and precision under that gate, and run a tissue-gated census with adequate support.

This is not one presently verifiable fact. Rung 0a is an extant-artifact question; rung 0b combines an unvalidated measurement assumption with future empirical gates.

## What was inspected

### 1. The nearest checkable prerequisite is true

I directly inspected the imported scientific bundle at commit-local path `probes/023/results/results_v2/`.

`summary.json`, line 7, states verbatim:

> `"bin_tissue_audit_rows": 594,`

The header and first data row of `bin_tissue_audit.csv` state verbatim:

> `case_id,stratum,style_group,member_voxels,finite_hu_voxels,nonfinite_hu_voxels,median_hu,q25_hu,q75_hu,iqr_hu`
>
> `sub-stroke0002,1,Q1_low_CBV,3969,3969,0,16.0,11.0,18.0,7.0`

The cited motivating example is also present verbatim at lines 254–255:

> `sub-stroke0092,1,Q1_low_CBV,3371,3371,0,3.0,2.0,4.0,2.0`
>
> `sub-stroke0092,1,Q4_high_CBV,3374,3374,0,23.0,8.0,24.0,16.0`

Thus the 594-row input needed for Rung 0a exists and has the stated 99 × 3 × 2 structure. The cross-family interpretation review independently records: “I checked ... all 594 HU audit rows” (`ideas/023/interpret_review.md`, section 3). This establishes availability and prior validation of the artifact, not the validity of a viability threshold.

### 2. The primary dataset supports the required modality linkage

The official ISLES'24 release page says:

> “Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

It also says:

> “Derivatives include all modalities linearly co-registered to the NCCT space.”

Source: official ISLES'24 Zenodo record 16813698, **Description → Data structure**, DOI 10.5281/zenodo.16813698: https://zenodo.org/records/16813698

This verifies that an NCCT-based voxel filter can be applied to the released perfusion-map coordinate system. It does not show that such a filter identifies viable tissue.

## Mandatory residual-assumption check

**If this card only verified the nearest checkable thing, what is it still assuming?**

It is still assuming that a prespecified absolute NCCT-HU window can separate established injury or partial-volume CSF from “viable-attenuation tissue” without becoming an outcome-proxy selection rule, and that enough voxels and patients will survive in every flow band for the recalibrated analysis.

That is the real load-bearing keystone. The file's existence, row count, co-registration, and selected case examples are only adjacent facts.

The primary clinical study *Assessing Brain Tissue Viability on Nonenhanced Computed Tomography After Ischemic Stroke* states in its Introduction:

> “There is, however, uncertainty in how early ischemic features on NECT translate to the different pathophysiological processes of acute ischemic brain injury. Specifically, whether NECT can be used to differentiate reversible from irreversible ischemic injury in the acute stroke phase...”

Source: Alzahrani et al., *Journal of the Belgian Society of Radiology* (2023), **Introduction**, PMCID PMC9855746: https://pmc.ncbi.nlm.nih.gov/articles/PMC9855746/

This evidence does not demonstrate that the proposed gate is impossible, so `KILL` would overstate the source. It does show that the gate's biological interpretation is not a settled property that can be certified from modality availability or a few HU examples. Adequate post-gate support is likewise a future Phase-S/census result. The load-bearing prerequisite therefore remains unverified at this screen.

```json
{"verdict": "UNVERIFIABLE", "evidence": "There is, however, uncertainty in how early ischemic features on NECT translate to the different pathophysiological processes of acute ischemic brain injury. Specifically, whether NECT can be used to differentiate reversible from irreversible ischemic injury in the acute stroke phase...", "source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9855746/ — Introduction", "note": "The 594-row audit and NCCT-space linkage are inspected true, but the real keystone—an outcome-independent viability gate with adequate retained support—requires prospective calibration and cannot be certified from current primary evidence."}
```


===== ideas/045/probe_contract.yaml =====
# Probe contract v1 -- idea 045, outcome-blind design-matrix feasibility only.
# Drafted at probe_plan on 2026-08-31. No probe code or execution is
# authorized until the human approval gate is satisfied.

idea_id: "idea-045"
contract_version: 1
track: exploratory

authorities:
  charter: "CHARTER.md"
  collaborator_rules: "docs/COLLABORATOR_RULES.md"
  idea_card: "ideas/045/idea_card.json"
  critique: "ideas/045/critique.md"
  debate: "ideas/045/debate.md"
  consensus: "ideas/045/consensus.md"
  revision: "ideas/045/revision.md"
  decision_entries:
    - "2026-09-01 -- Operator ruling: idea-045 claim-identity gate (revise-in-place)"

question: "Before reading the observed final-infarct contrasts, does the frozen 99-case attenuation-audit geometry support an estimable band-by-HU-imbalance model without rank failure, near-degenerate within-band exposure, or domination by a few patients?"
risky_assumption_tested: "The proposed primary model can distinguish band-specific HU-imbalance associations and adjusted band contrasts on the actual 99-case design. File joinability alone does not establish adequate exposure variation or a well-conditioned interaction design."

scope:
  included: "CPU-only validation of input identity, join cardinality, derived Q1-minus-Q4 median-HU geometry, design-matrix rank/conditioning, and patient leverage for bands 2 and 3."
  excluded:
    - "Reading, parsing, summarizing, logging, or modeling the observed d column from per_patient.csv."
    - "Fitting the scientific outcome model, estimating HU slopes, computing adjusted observed band contrasts, or deciding whether tissue composition explains the parent reversal."
    - "Band 1, nonlinear alternatives, threshold search, subgroup analysis, image restaging, model inference, or access to the 49 reserved cases."

dataset:
  name: "Imported idea-023 take-13 analysis tables"
  source: "probes/023/results/results_v2/bin_tissue_audit.csv and probes/023/results/results_v2/per_patient.csv from the imported Phase-C bundle governed by idea 023."
  required_columns:
    bin_tissue_audit.csv: [case_id, stratum, style_group, median_hu]
    per_patient.csv: [case_id, stratum]
  forbidden_column_values: "The implementation may inspect the per_patient.csv header to confirm that d exists, but must not parse or retain any d value. Read only case_id and stratum from that file."
split_policy: "Use only the 99 already-analyzed idea-023 census cases and only strata 2 and 3. The 49 reserved cases remain untouched. This probe has no train/test split because it is outcome-blind design validation, not model development or effect estimation."

preprocessing:
  row_gate: "Require exactly one Q1_low_CBV and one Q4_high_CBV audit row for each case-stratum and exactly one matching per_patient key, with 99 unique cases in each of strata 2 and 3. Reject duplicate or unmatched keys."
  exposure: "For each case-stratum, compute HU_imbalance = median_hu(Q1_low_CBV) - median_hu(Q4_high_CBV). Require both source medians and the derived value to be finite."
  design_matrix: "Create 198 rows with columns intercept, I[stratum=3], centered_HU_imbalance, and I[stratum=3] times centered_HU_imbalance. Center HU_imbalance once at the pooled mean across the 198 primary rows; do not scale, trim, winsorize, transform, or choose another centering rule."

analysis:
  analysis_unit: "Patient-by-band row, with patient identity retained for influence accounting."
  primary_metric: "Singular-value condition number of the four-column frozen design matrix after scaling each non-intercept column to unit L2 norm solely for the conditioning calculation."
  secondary_metrics:
    - "Matrix rank and all four singular values."
    - "Within each primary band: HU-imbalance minimum, maximum, median, IQR, number of distinct values, and number of cases."
    - "Diagonal hat-matrix leverage per row, maximum leverage overall, and the number of distinct patients among the ten highest-leverage rows."
    - "Leave-one-patient-out condition-number range, recomputing the same fixed centering and diagnostic scaling rule within each deletion solely as a sensitivity diagnostic."
  positive_rule: "Feasibility passes only if the matrix has rank 4; its primary condition number is <=30; each band has nonzero HU-imbalance IQR and at least 20 distinct HU-imbalance values among exactly 99 cases; maximum row leverage is <=0.20; the ten highest-leverage rows contain at least five distinct patients; and every leave-one-patient-out matrix remains rank 4 with condition number <=30. These are design-feasibility thresholds, not medical effect thresholds."
  interpretation: "A pass supports drafting the later exploratory attribution analysis because the frozen linear interaction is numerically estimable on the observed exposure geometry. It provides no evidence that either slope is nonzero or that adjustment changes the reversal."

primary_metric: "Condition number of the frozen, diagnostically scaled four-column bands-2/3 design matrix."
secondary_metrics:
  - "Rank and singular values."
  - "Band-specific HU-imbalance support and distinct-value counts."
  - "Hat leverage and leave-one-patient-out conditioning."

baselines:
  - "Full-rank four-column design is the minimum algebraic baseline."
  - "A condition number of 30, maximum row leverage of 0.20, and 20 distinct values per band are frozen conservative feasibility boundaries; they are not claims of universal statistical standards."

maximum_variants: 1
maximum_gpu_minutes: 0
maximum_seeds: 1
randomness: "None. All calculations are deterministic; no bootstrap or synthetic outcome is authorized in this probe."
stopping_rule: "Stop after the single frozen design audit completes, immediately on an invalidating failure, or before any observed d value would be read. Do not proceed to the scientific attribution analysis regardless of result."

positive_pattern: "All integrity gates pass and the frozen interaction design meets every rank, conditioning, variation, and leverage threshold. This means only that the proposed model is computationally estimable on the actual exposure geometry."
negative_pattern: "The valid joined exposure geometry fails one or more prespecified rank, conditioning, within-band variation, or leverage thresholds. This is a decisive feasibility negative for the current linear interaction specification and requires revision before any outcome analysis; it is not evidence against tissue composition or the parent association."

invalidating_failures:
  - "Outcome-access breach: any observed d value is parsed, retained, summarized, logged, or used by the probe."
  - "Input-identity failure: either required imported file is absent, its SHA-256 is not recorded, or its header lacks the required columns and expected d column."
  - "Join failure: duplicate keys, unmatched case-stratum keys, missing Q1/Q4 cells, a count other than 99 cases in either primary band, or any reserved/non-census case is encountered."
  - "Value failure: a required median HU or derived imbalance is nonfinite."
  - "Analysis deviation: band 1 is included; exposure is transformed, trimmed, or selected post hoc; another variant is run; or thresholds are changed after inspection."
  - "Output failure: a required artifact, input hash, per-row diagnostic, resolved configuration, or environment record is missing or nonfinite where finiteness is required."

claim_discipline:
  permitted: "The frozen bands-2/3 attenuation-imbalance design is, or is not, sufficiently conditioned and distributed across patients for the prespecified linear interaction analysis."
  prohibited:
    - "The HU imbalance is associated with final infarction."
    - "Tissue composition explains, contributes to, or fails to explain idea-023's reversal."
    - "Median HU is a validated tissue-type or viability measurement."
    - "Any model uses HU imbalance, CBV, MTT, or tissue composition."
    - "An invalid run or data-integrity failure is a scientific negative."

required_outputs:
  - resolved_config.json
  - input_manifest.csv
  - per_row_design.csv
  - design_diagnostics.json
  - summary.json
  - environment.txt
  - run_log.txt

open_questions_for_human: []
human_approved: false


===== ideas/045/revision.md =====
# Revision — idea 045

## Outcome

The candidate is narrowed to one already-supported analysis: test whether per-patient Q1-versus-Q4 median NCCT attenuation imbalance accounts for the opposite-signed final-infarct contrasts in flow bands 2 and 3.

The proposed viability gate and tissue-gated census are removed. The debate established that HU selection can remove outcome-bearing tissue, so a post-gate null cannot decisively reject the underlying joint-CBV/MTT association without an unavailable external bound on HU-by-outcome effect modification.

## Material changes

1. `deliverable_original` preserves the ledger sentence verbatim. The revised deliverable reports only an association consistent with tissue composition contributing to the reversal; it no longer promises a stable gated association or lineage-level refusal.
2. The question now concerns only whether the already-measured attenuation imbalance accounts for the parent reversal. This promotes the critique's Rung-0a analysis to the whole candidate.
3. Removed the absolute-HU window, Phase-S recalibration, planted-effect simulations, retention/support floors, restaging, and tissue-gated census.
4. Corrected `design_template` from `counterfactual-synthesis` to `conditional-observational`; no image is synthesized or edited.
5. Specified the primary analysis: join the frozen tables, restrict primary inference to bands 2 and 3, fit `d = band + HU_imbalance + band × HU_imbalance`, and report band-specific slopes and adjusted contrasts with patient-bootstrap intervals. Band 1 and nonlinear fits are exploratory.
6. Corrected the keystone to unique, joinable audit and outcome rows. These were directly inspected, so status is `INSPECTED_TRUE`. Median HU's sensitivity as a composition proxy remains an explicit residual assumption.
7. Acknowledged that these 99 outcomes were opened in the parent study. This is exploratory successor-design evidence, not a fresh confirmatory census; the 49 reserved cases remain untouched.
8. Preserved a bounded decisive negative: persistence of opposite-signed adjusted band contrasts with bootstrap intervals excluding zero decisively shows that median-HU adjustment did not explain the reversal. A nonsignificant slope or imprecise adjusted result is sensitivity-limited. No outcome rejects all tissue composition, CBV/MTT biology, or another cohort.
9. Tightened the positive: it is observational and consistent with contribution, not causal. Severity, ischemic hypodensity, and partial-volume CSF remain alternatives.
10. Updated scores: feasibility rises because inputs are inspected and local; negative-result value falls from 5 to 4 and is bounded to this proxy; novelty confidence falls to 2 because no broad novelty audit exists.

## Claim identity

This is a narrowing. The original rationale was that tissue imbalance might explain idea-023's cross-band reversal; the revision tests that prerequisite directly and removes the unsupported downstream census promise. The parent result, named measurements, cohort, and tissue-confound hypothesis remain unchanged.

```json
{"claim_retention": "narrowed"}
```


===== ideas/045/state.json =====
{
  "approval": null,
  "charter": null,
  "claim": "Within viable-attenuation tissue at matched relative CBF, the joint CBV/MTT coordinate shows a directionally stable, precision-bounded final-infarct association across all three within-patient flow bands -- establishing, or decisively refusing, the Stage-0 prerequisite that idea-023's untissued operationalization could not test cleanly.",
  "contract_blob": null,
  "corrections": null,
  "idea_id": "idea-045",
  "idea_no": "045",
  "kill_code": null,
  "materialization": {
    "event_count": 5,
    "materializer_version": 3,
    "source_fingerprint_sha256": "1b29dc6aea8ce3c8ff949c0bc0f36de95b64d8aac45cac4efc4834d45f9d893e",
    "sources": {
      "approval_sha256": null,
      "contract_blob": null,
      "idea_card_sha256": "ba783b6d64772f6000937d9642ff619e26bd4fd015bf295630378e9e0c6c3570",
      "ledger_events_sha256": "17569243d40229ffef027e11c04f5b377fed8f622857278da651e1dbfd6b9f7b",
      "registry_sha256": null
    }
  },
  "pending_decisions": null,
  "registry": null,
  "schema_version": 1,
  "scrutiny": "DEBATED",
  "status": "SHORTLISTED",
  "title": "Tissue-normalized joint CBV/MTT compensation at matched flow"
}


===== STAGE TASK =====
<!-- stage: probe_code -->
Human approval has been granted. Implement only the approved `probe_contract.yaml` in probes/IDEA_ID/.

Requirements:
- minimal dependencies;
- one command to run;
- fixed seed;
- deterministic split manifest;
- assertions against split overlap;
- synthetic or tiny smoke mode;
- per-sample outputs;
- resolved configuration and environment capture;
- no test-set access;
- no unapproved variants;
- clear failure exit codes.

Run local non-expensive checks and write `verification.json`. Do not launch expensive compute.

## Readability (the human runs and reads this code personally)

Write for a researcher reviewing results the next morning, not for a machine:
- Open run.py with a module docstring: what experiment this is, the idea id,
  the contract's primary metric and stopping rule in one plain-English
  paragraph, and what a positive vs negative result will look like.
- Structure the file into clearly named phases (load, validate, measure,
  summarize) with a short plain-language comment block ABOVE each phase
  explaining what is about to happen and why it is part of the contract.
- Comment the non-obvious lines: every threshold, every filter, every unit
  conversion gets one line saying what it is and where the number came from.
- Print progress as it runs (which pair, which variant, running counts) and
  end by printing the summary.json content with a one-paragraph plain-English
  interpretation template that names the contract's positive_pattern or
  negative_pattern -- never a stronger claim.
- No cleverness: prefer three obvious lines over one dense one.

## Hard code standards (review-blocking)

The cross-family reviewer treats each unmet item as a blocking finding:

1. Determinism manifest: print AND write a manifest at start and end --
   input paths with content hashes, row/case counts, and the seed. The two
   must agree.
2. Exclusions log: every dropped case/row/voxel-group emits one line to an
   exclusions file with the reason; totals appear in the summary.
3. Assertions: at least one assertion per data transformation step
   (shape/count/range/units), so silent corruption fails loudly.
4. Declared state: all seeds and input/output paths are top-level constants
   or CLI arguments; no hidden mid-function state; no network calls during
   analysis.
5. Split-before-outcome: when any census/reserve or train/eval split exists,
   its manifest is written and hashed BEFORE any outcome or label file is
   opened.
6. Harness smoke: `--smoke` runs under the verify harness (accepting
   `--output-dir`, which may be a temp directory), finishes in under 60
   seconds, and can never satisfy a contractual gate.

