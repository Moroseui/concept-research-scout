You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/044
Preserve existing files unless the task explicitly requires an update.
Do not claim novelty without verified primary sources.
Do not write code unless this is the probe_code stage and human approval exists.

===== charters/isles24/CHARTER.md =====
# Research charter — isles24

**Status:** human-authored governance document, drafted 2026-08-16 at the
operator's direction as a change of program focus.
Scores produced under this charter are scoped to it and are not
comparable with scores from any other charter.

## The driver

This program's current focus is the **ISLES'24 challenge dataset**
(Ischemic Stroke Lesion Segmentation, MICCAI challenge series). The
direction is exploratory rather than committed: the question is what
research ideas this dataset makes possible, judged by whether an expert
in AI for medical imaging would find them worth pursuing.

**The program under this charter: generate testable research ideas that
concretely use ISLES'24 and would interest a serious researcher in AI
for medical imaging.**

Breadth is deliberate. Segmentation methods, outcome prediction,
interpretability, benchmarking and evaluation critique, dataset-quality
findings, language-and-imaging connections, uncertainty, generalization
-- all admissible, provided the idea is testable and the dataset's role
in it is concrete rather than decorative.

## Verify before generating (hard rule)

Do not assume the dataset's composition. Before writing any candidate,
the scout MUST verify against primary sources (the ISLES'24 challenge
site, its publications, its data-hosting pages) at minimum: which
imaging modalities are provided per case, what the ground truth is and
how it was produced, cohort size and split structure, license and
access conditions, and what the official evaluation measures. Working
belief to be checked, not trusted: ISLES'24 concerns acute ischemic
stroke, provides acute-phase imaging (non-contrast CT and CT
angiography/perfusion-derived maps) with lesion ground truth derived
from follow-up imaging. Every candidate must cite what it verified.
A candidate premised on data the dataset does not contain is invalid
regardless of its other merits.

## What makes a candidate good here

1. **Testable kernel.** A specific question with a recognizable
   empirical answer, not a topic area.
2. **The dataset is load-bearing.** ISLES'24 specifically enables the
   test -- its modalities, its ground-truth construction, its cohort,
   or its role as a public benchmark.
3. **A researcher would care.** The candidate states, in one or two
   sentences, why a person who publishes in medical imaging AI would
   consider the answer worth having, whichever way it comes out.
4. **Honest cost.** Compute, data access, and annotation needs stated.

## Annotation rule (operator decision, 2026-08)

Ideas requiring annotator-dependent inputs are admissible. Apply a
scoring penalty ONLY when an idea requires NEW annotation burden on the
lab (fresh expert labeling beyond what the dataset or public sources
already provide). Using the dataset's existing annotations, or
published auxiliary labels, carries no penalty.

## Connections to the lab (bonus, not requirement)

Ideas that additionally connect to the lab's standing interests --
language as an interface to 3D medical images, interpretability of
what models use, evaluation and benchmarking rigor, clinician-in-the-
loop refinement -- earn their connection bonus per the rubric. But a
strong ISLES'24 idea with no such connection is still a strong idea
under this charter.

## Inherited discipline

All standing rules apply unchanged: verified primary sources for any
novelty claim; the use-versus-association distinction; feasibility
must name concrete numbers; kill weak candidates rather than decorate
them. The deliverable standard for this charter is a ranked set of
candidates each carrying its verified dataset facts, its testable
kernel, and its stated audience-relevance -- ready for human review
and, for survivors, the normal pipeline.


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


===== evidence/ledger_digest_isles24.md =====
# Ledger digest -- charter: isles24 (auto-generated; scores are scoped to this charter only)

65 tracked ideas in this charter. Latest state per idea; full history in ledger.jsonl.

Work under other charters: evidence/cross_charter_index.md (facts, no scores).

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **IDENTIFIABILITY_FAILURE** x11: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_ACCESS** x3: Required data, checkpoints, or mappings are not obtainable in practice.
- **EFFECT_UNREACHABLE** x1: The claimed effect cannot exceed a published bound / measurement floor.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **isles24-scout-002-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.4, audited 2026-08-16] -- Two tissues, two death thresholds
- **isles24-scout-004-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.1, audited 2026-08-18] -- The heart's signature in the head scan
- **isles24-scout-005-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 2.9, audited 2026-08-19] -- The bottleneck before the brain
- **isles24-scout-004-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.3, audited 2026-08-18] -- The brain's odometer: calcification as the model's age gauge
- **isles24-scout-002-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.2, audited 2026-08-16] -- The clot that lets contrast through
- **isles24-scout-002-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.0, audited 2026-08-16] -- The barrier is already leaking
- **isles24-scout-001-c01** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.6, audited 2026-08-16] -- Does the winning model rediscover the collateral clock?
- **isles24-scout-005-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.6, audited 2026-08-19] -- Do sulci pin the predicted infarct edge?
- **isles24-scout-001-c03** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.5, audited 2026-08-16] -- Read the stroke from the blood leaving, not only entering
- **isles24-scout-001-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.5, audited 2026-08-16] -- The frail brain around the threatened territory
- ... and 6 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- counterfactual-synthesis: 10
- regional-substitution: 9
- representation-erasure: 6
- conditional-observational: 3
- cross-model-disagreement: 2
- regional-removal: 2
- natural-paired: 1
- other:remote-perturbation: 1
- other:graph-edge-intervention: 1
- model-output-perturbation: 1
- other:temporal-reparameterization: 1
- other:noise-residual-transplant: 1
- other:label-geometry-audit: 1
- other:geometry-conditioned-boundary-test: 1

## Ideas

- **idea-020** [REJECTED/DEBATED/baseline] -- A spreading front inside the perfusion deficit -- killed: IDENTIFIABILITY_FAILURE
- **idea-021** [SHORTLISTED/DEBATED/baseline] -- The healthy hemisphere is the ruler
- **idea-022** [PAUSED/DEBATED/wide] -- Does the model mistake the end of the scan for the end of the bolus?
- **idea-023** [SHORTLISTED/DEBATED/wide] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
- **idea-024** [REJECTED/DEBATED/wide] -- The capillary traffic jam hidden behind the same mean transit time -- killed: DATA_ACCESS
- **idea-025** [PAUSED/DEBATED/wide] -- The scan is also an actigraph: the model may be reading how much the patient moved
- **idea-026** [REJECTED/SCOUTED/baseline] -- A spreading front inside the perfusion deficit
- **idea-027** [REJECTED/DEBATED/baseline] -- When vanished sulci mean rescue, not death -- killed: DATA_ACCESS
- **idea-028** [REJECTED/DEBATED/baseline] -- The blood's grayscale oxygen gauge -- killed: IDENTIFIABILITY_FAILURE
- **idea-029** [REJECTED/DEBATED/baseline] -- The ground truth remembers the algorithm that drafted it -- killed: IDENTIFIABILITY_FAILURE
- **idea-030** [REJECTED/DEBATED/wide] -- The ground truth was drawn on a swollen brain -- killed: IDENTIFIABILITY_FAILURE
- **idea-031** [REJECTED/SCOUTED/baseline] -- The vascular detour the segmentation model can see -- killed: DATA_ACCESS
- **idea-032** [REJECTED/DEBATED/baseline] -- The arterial network's spare route -- killed: IDENTIFIABILITY_FAILURE
- **idea-033** [REJECTED/DEBATED/baseline] -- Did preprocessing teach the winner to read the disappearing insular ribbon? -- killed: IDENTIFIABILITY_FAILURE
- **idea-034** [REJECTED/DEBATED/wide] -- The edge of the map: the benchmark scores terra incognita -- killed: IDENTIFIABILITY_FAILURE
- **idea-035** [REJECTED/DEBATED/wide] -- The skull is a fixed-volume pressure vessel -- killed: IDENTIFIABILITY_FAILURE
- **idea-036** [REJECTED/DEBATED/baseline] -- Does the model bring a vascular map to the scan? -- killed: IDENTIFIABILITY_FAILURE
- **idea-037** [REJECTED/DEBATED/wide] -- The scan remembers which hospital took it -- killed: IDENTIFIABILITY_FAILURE
- **idea-038** [REJECTED/DEBATED/wide] -- Does the model price the last mile of blood delivery? -- killed: IDENTIFIABILITY_FAILURE
- **idea-039** [SHORTLISTED/DEBATED/wide] -- Does the model trust tissue that obeys the flow equation?
- **idea-040** [PAUSED/DEBATED/baseline] -- The pressure history written in a winding artery
- **idea-041** [SHORTLISTED/DEBATED/wide] -- The roughness of a heartbeat through starved tissue
- **idea-042** [SHORTLISTED/DEBATED/wide] -- Delay is not dispersion
- **idea-043** [REJECTED/SCOUTED/baseline] -- What the winner's brain window revealed -- killed: EFFECT_UNREACHABLE
- **idea-044** [SHORTLISTED/CRITIQUED/baseline] -- The old stroke inside the new forecast
- **isles24-scout-001-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Does the winning model rediscover the collateral clock?
- **isles24-scout-001-c02** [SHORTLISTED/SCOUTED/baseline] -- The vascular detour the segmentation model can see
- **isles24-scout-001-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Read the stroke from the blood leaving, not only entering
- **isles24-scout-001-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The frail brain around the threatened territory
- **isles24-scout-001-c05** [SHORTLISTED/SCOUTED/baseline] -- A spreading front inside the perfusion deficit
- **isles24-scout-001-c06** [SHORTLISTED/SCOUTED/wide] -- The capillary traffic jam hidden behind the same mean transit time
- **isles24-scout-001-c07** [SHORTLISTED/SCOUTED/wide] -- Does the model mistake the end of the scan for the end of the bolus?
- **isles24-scout-001-c08** [SCOUT_ONLY/SCOUTED/wide] -- The deconvolution algorithm may have signed the image
- **isles24-scout-002-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The water already in the tissue: does the model read the edema clock?
- **isles24-scout-002-c02** [SHORTLISTED/SCOUTED/baseline] -- The healthy hemisphere is the ruler
- **isles24-scout-002-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Two tissues, two death thresholds
- **isles24-scout-002-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The barrier is already leaking
- **isles24-scout-002-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The clot that lets contrast through
- **isles24-scout-002-c06** [SHORTLISTED/SCOUTED/wide] -- The scan is also an actigraph: the model may be reading how much the patient moved
- **isles24-scout-002-c07** [SHORTLISTED/SCOUTED/wide] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
- **isles24-scout-002-c08** [SCOUT_ONLY/SCOUTED/wide] -- Has the deficit percolated? Volume is what the metric sees; connectivity may be what the model uses
- **isles24-scout-003-c01** [SHORTLISTED/SCOUTED/baseline] -- Did preprocessing teach the winner to read the disappearing insular ribbon?
- **isles24-scout-003-c02** [SCOUT_ONLY/SCOUTED/baseline] -- How much artery did the clot occupy?
- **isles24-scout-003-c03** [SHORTLISTED/SCOUTED/baseline] -- The arterial network's spare route
- **isles24-scout-003-c04** [SHORTLISTED/SCOUTED/baseline] -- The blood's grayscale oxygen gauge
- **isles24-scout-003-c05** [SHORTLISTED/SCOUTED/baseline] -- When vanished sulci mean rescue, not death
- **isles24-scout-003-c06** [SCOUT_ONLY/SCOUTED/wide] -- The bolus spreads like dye in a river
- **isles24-scout-003-c07** [SHORTLISTED/SCOUTED/wide] -- Does the model price the last mile of blood delivery?
- **isles24-scout-003-c08** [SHORTLISTED/SCOUTED/wide] -- The skull is a fixed-volume pressure vessel
- **isles24-scout-004-c01** [SHORTLISTED/SCOUTED/baseline] -- The ground truth remembers the algorithm that drafted it
- **isles24-scout-004-c02** [SHORTLISTED/SCOUTED/baseline] -- Does the model bring a vascular map to the scan?
- **isles24-scout-004-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The heart's signature in the head scan
- **isles24-scout-004-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The model may be watching the patient's eyes
- **isles24-scout-004-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The brain's odometer: calcification as the model's age gauge
- **isles24-scout-004-c06** [SHORTLISTED/SCOUTED/wide] -- The scan remembers which hospital took it
- **isles24-scout-004-c07** [SHORTLISTED/SCOUTED/wide] -- The edge of the map: the benchmark scores terra incognita
- **isles24-scout-004-c08** [SHORTLISTED/SCOUTED/wide] -- The ground truth was drawn on a swollen brain
- **isles24-scout-005-c01** [SHORTLISTED/SCOUTED/baseline] -- What the winner's brain window revealed
- **isles24-scout-005-c02** [SHORTLISTED/SCOUTED/baseline] -- The old stroke inside the new forecast
- **isles24-scout-005-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The bottleneck before the brain
- **isles24-scout-005-c04** [SHORTLISTED/SCOUTED/baseline] -- The pressure history written in a winding artery
- **isles24-scout-005-c05** [SCOUT_ONLY/SCOUTED/baseline] -- Do sulci pin the predicted infarct edge?
- **isles24-scout-005-c06** [SHORTLISTED/SCOUTED/wide] -- Does the model trust tissue that obeys the flow equation?
- **isles24-scout-005-c07** [SHORTLISTED/SCOUTED/wide] -- The roughness of a heartbeat through starved tissue
- **isles24-scout-005-c08** [SHORTLISTED/SCOUTED/wide] -- Delay is not dispersion


===== evidence/portfolio_brief_isles24.md =====
# Portfolio brief -- charter: isles24 (auto-generated; run `python scout.py brief`)

Actionable ideas OF THIS CHARTER with debate verdicts (evaluative
framing never crosses charters; facts cross via
evidence/cross_charter_index.md). A revival/recombination
candidate MUST cite the specific condition below that has changed.

## idea-025 [PAUSED] -- The scan is also an actigraph: the model may be reading how much the patient moved

**Verdict:** **PAUSE.** The single most important thing for the human to inspect is whether paired pre-correction and icobrain cva 1.5.0-corrected CTP, with independent motion ground truth or retained validated transforms, can be obtained for a representative cohort. Without that bridge, the original behavioral attribution is not identifiable; the index-level audit is a distinct successor rather than a repair. ```json {"verdict": "PAUSE", "unblock": "Obtain paired pre-correction and icobrain cva 1.5.0-corrected CTP (or a source-verified bit-equivalent pipeline) with independent motion ground truth or retained validated transforms, and verify patient-motion rank recovery plus the real motion-to-residue mapping."} ```

**Unresolved:** Is skull-anchored registration on uncorrected CTP an adequate independent measure of acquisition-level patient motion?

## idea-023 [SHORTLISTED] -- The joint CBV/MTT compensation state at matched flow

**Verdict:** **REVISE.** Rewrite the card to the fully gated, cohort-anchored design before any feasibility memo or model work. The single most important thing for the human to examine is whether matching a model's edit-response change point to a change point estimated from its own training cohort's outcomes is sufficient evidence for the physician-legible phrase “autoregulatory blood-volume reserve,” or whether independent physiological validation is required. That decision controls both claim identity and whether G-shape can ever reach rung 3. ```json {"verdict": "REVISE", "unblock": "Rewrite the card with K2, G-label/G-shape, G-hyper, support-boundary indeterminacy, channel-attribution limits, and model-family scope, then obtain human agreement that the outcome-derived shape can validly operationalize autoregulatory reserve before Stage 0."} ```

**Unresolved:** Does an outcome-derived change point identify autoregulatory reserve rather than a learned nonlinear map pattern?; Is the revised deliverable still the same claim?; Are the necessary Stage 0 conditions present in ISLES'24?; Whose model can support the eventual wording?

## idea-022 [PAUSED] -- Does the model mistake the end of the scan for the end of the bolus?

**Verdict:** **PAUSE.** The single most important thing for the human to inspect is whether a frozen raw-4D-CTP final-infarct checkpoint with non-trivial held-out performance can actually be obtained together with its training-time temporal masking or padding semantics. Both parts are necessary; a checkpoint alone would not validate the prefix intervention. ```json {"verdict": "PAUSE", "unblock": "Obtain a frozen raw-4D-CTP final-infarct checkpoint with non-trivial held-out performance and directly inspect training-time temporal masking or padding semantics that support the nested-prefix intervention."} ```

## idea-021 [SHORTLISTED] -- The healthy hemisphere is the ruler

**Verdict:** **REVISE.** The round-three design may repair the remaining mechanism-family objection, but that repair was never tested by the critic and is not yet in the idea card. Before deciding, the human should look most closely at a prediction table for the signed up-scaling conjunction: can any plausible non-reference mechanism produce increased affected-side deficit under healthy-side up-scaling while passing the contralateral-emergence, global-arm, realism, and power gates? The card should not advance until an independent review answers that question and the actual card is rewritten to the agreed normalization pins, reduced claims, gates, power requirement, and fallback governance. ```json {"verdict": "REVISE", "unblock": "Independently validate that the signed up-scaling conjunction excludes the named non-reference mechanisms, then rewrite the card with frozen normalization, realism, emergence, margin, and power gates plus successor handling for the weaker fallback."} ```

**Unresolved:** Does the round-three conjunction identify reference-setting rather than generic cross-hemispheric use?; Can the discriminating up-scaling arm remain physiologically and cross-modally in distribution?; Is the weaker fallback a revision of idea 021 or a successor?; Is the study adequately powered within the available cohort and compute envelope?



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
- [isles24] **idea-044** [SHORTLISTED] -- The old stroke inside the new forecast
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


===== evidence/librarian_proposals.md =====


===== ideas/044/README.md =====
# Idea 044: The old stroke inside the new forecast

Selected from scouting cycle isles24-005, candidate 2.


===== ideas/044/critique.md =====
# Critique — Idea 044: The old stroke inside the new forecast

```
FATAL OBJECTION: NONE
EVIDENCE: closest-to-fatal is the unnamed frozen model plus the verified weakness
  of the state of the art (top ISLES'24 model Dice 0.285 ± 0.213, arXiv 2408.10966);
  both are repairable by pins, not fatal to the question.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

## Scope of this review

Adversarial critique of `idea_card.json` (isles24-scout-005-c02) with the
keystone screen (`keystone_screen.md`, verdict UNVERIFIABLE from documentation)
taken as given. New primary-source checks performed this stage: the ISLES'24
challenge-results paper (arXiv 2408.10966), the challenge winner's method paper
(arXiv 2505.18424), and a targeted sweep of the NCCT "brain frailty"
association literature. Epistemic labels used throughout: **[VF]** verified
fact (read at source this stage or a prior stage), **[SS]** source-supported
interpretation (title/abstract-level only), **[INF]** inference, **[SPEC]**
speculation.

## 1. Prior-work overlap: the association literature is rich; the delta survives

The suspected signal is not novel as an *association*. Old infarcts,
leukoaraiosis, and atrophy on admission NCCT form the established "brain
frailty" triad, scored 0–3 and repeatedly shown to predict stroke outcome:
the IST-3 secondary analysis (Lancet Neurol 2015; PMC4513190) found old
infarct predicted symptomatic intracranial hemorrhage, and the brain-frailty
score literature (Neurology 2020, DOI 10.1212/WNL.0000000000008881, and
successors through 2025) ties the triad to functional outcome **[SS —
verified at title/abstract level this stage, not read in full]**.

Two consequences, one for and one against the card:

- **For:** the card's delta — an *intervention* test of whether a trained
  final-infarct model **uses** the cavity, rather than whether the cavity
  *predicts* outcome — is exactly the use-versus-association distinction the
  program requires, and no intervention-style precedent was found in this
  stage's searches or the scout's. "Not found" is not "does not exist"
  **[INF]**; novelty_confidence 3 with LIMITED_SEARCH remains the correct
  ceiling and is what the card claims.
- **Against:** within the frailty triad, old infarcts are the *weakest*
  member in several association studies (one cohort found old vascular
  lesions not independently associated with the cognitive outcome where
  leukoaraiosis and atrophy were) **[SS]**. The prior probability that a
  model trained on 149 cases learned to consult a minority-prevalence,
  weakly-predictive marker is not high. This does not invalidate the test —
  a clean null is claimed as informative — but it should temper `interest: 4`
  and it raises the stakes on the sensitivity gates (sections 3–5): a null
  produced by an insensitive design would be worthless precisely because the
  prior already leans null **[INF]**.

## 2. The deliverable sentence overclaims the mechanism (repair required)

The deliverable — "using remote chronic infarct cavities **as a
brain-reserve signal**" — claims an interpretation the design cannot
identify. The card concedes this itself twice: identifiability is scored 3
because the design shows "cavity use but not whether the model interprets it
as reserve or age," and alternative explanation 2 says the age-proxy
confound "cannot fully" be distinguished. The design demonstrates, at best,
*use of contralateral cavity-like tissue loss on NCCT*. "Brain reserve" is a
physiological construct sitting on top of that, exactly parallel to
"autoregulatory blood-volume reserve" in idea 023, where the ruling
(decisions.md, 2026-08-17) was that physiological naming requires
independent validation and the claim language was reduced in place under
REVISE.

**Repair:** deliverable sentence and question drop the reserve clause —
"The final-infarct model is using remote chronic-cavity-like tissue loss on
admission NCCT when forecasting new infarction." Reserve stays in
`suspected_signal` as motivation. Under the claim-identity rule (2026-08-10)
this is a narrowing within the same measured estimand, not a change of claim
identity — the intervention, endpoint, and prohibited conclusions are
unchanged; only an interpretive rider is deleted — so revision-in-place, not
a successor, is the correct vehicle **[INF, precedent-based]**.

## 3. Cross-channel inconsistency: the edit removes the cavity from one input channel only

The card pins: "holding all acute CT, CTA, perfusion, and affected-hemisphere
voxels fixed." So the cavity is filled **on NCCT only**. But a chronic
encephalomalacic cavity is CSF-filled tissue loss; it necessarily also
appears in the CTP-derived maps (near-zero CBV/CBF in the cavity) and in CTA
as an avascular region **[INF from physiology; not verified on ISLES'24
voxels]**. Three consequences:

1. **The positive-claim scope shrinks.** A supra-sham response demonstrates
   use of the *NCCT-channel* cavity appearance, not use of "the cavity."
   The card nowhere states this restriction.
2. **The null is biased toward insensitivity.** A model reading the cavity
   from the CBV map would show no NCCT-edit response, yielding a false
   "does not use" verdict. Combined with section 1's low prior, this is the
   single largest threat to the card's claimed negative-result value.
3. **The edited input is cross-modally inconsistent** — normal-appearing
   NCCT tissue over a perfusion void is a configuration absent from
   training data. The program has been burned by OOD interventions before
   (idea 006, PAUSED for exactly this class of error). Mitigation exists in
   the card, apparently by accident: the ventricle-adjacent CSF-fill sham
   *also* creates NCCT-tissue-over-perfusion-void mismatch, so the sham
   contrast partially cancels the pure-mismatch response **[INF]**. The
   random-parenchyma sham does not share this property. The card should
   claim this control explicitly rather than own it implicitly.

**Repair:** restate the estimand as NCCT-channel use; promote the CSF sham
to the designated mismatch control with that rationale written down; add a
pre-specified interpretation rule for the case where the model turns out to
ignore NCCT entirely (see section 5). A consistent all-channel edit would be
the stronger design but touches perfusion maps, which idea 021/023
precedent treats as requiring its own realism machinery — out of scope for
this card's question and correctly so.

## 4. The donor-tissue rule has a bug: the mirror of a contralateral cavity lies in the affected hemisphere

The edit fills the cavity "with texture sampled from mirrored homologous
tissue." The cavity is contralateral to the acute stroke by construction, so
its mirrored homolog is **in the affected hemisphere** — possibly inside the
Tmax>6 s territory or the ischemic core **[INF, geometric]**. The card's
exclusion of acute territory applies to cavity *detection*
(`X_measurement`), not to donor sampling. Failure mode: the fill imports
subtly hypodense acutely-ischemic texture into the contralateral hemisphere,
so the "cavity removed" image actually contains new-looking pathology —
attenuating or inverting the intended contrast, direction unknowable per
case **[INF]**.

**Repair (cheap, mandatory):** donor regions must be verified
normal-appearing — exclude any donor voxel inside the Tmax>6 s or CBF<30%
territory and require donor HU statistics within the normal-tissue band; on
cases where the homolog is contaminated, fall back to the second
(generative) fill method the card already requires. Two-method concordance,
already pinned, then also polices residual donor artifacts.

## 5. No frozen model is named, and the verified state of the art is weak

The experiment is priced "20 GPU-hours **once a model is frozen**," and
`existing_assets` lists no model. Checked this stage:

- The challenge-results paper (arXiv 2408.10966) reports the top method — a
  multimodal nnU-Net — at **Dice 0.285 ± 0.213, absolute volume difference
  21.2 ± 37.2 mL** on the 98-case hidden test set **[VF at abstract level]**.
- The winner's paper (arXiv 2505.18424, "How We Won the ISLES'24 Challenge
  by Preprocessing") describes skull-stripping + intensity windowing + a
  residual nnU-Net; **no code/weights availability statement was found** in
  the abstract-level content fetched. Absence of a statement is not absence
  of release **[SS]** — but it means model availability is currently
  UNVERIFIED, the same defect class that PAUSED ideas 022 and 025.

This is not fatal, unlike 022, because a final-infarct baseline is trainable
locally from the 149 public cases with standard tooling — the dataset exists
to enable exactly that — and the card's own rung ladder already scopes rung 1
to a single model with rung 2 requiring a separately trained model. But three
pins are required:

1. **Name the model path** in the card: verified public
   checkpoint/docker if one exists (Stage 0 checks the challenge site and
   winner repositories), else a locally trained nnU-Net with frozen
   configuration, and price the training compute honestly (the 20-GPU-hour
   figure covers inference only).
2. **Define the performance gate numerically before any edit is run.** The
   card's "model performance" gate is undefined while the verified SOTA is
   Dice 0.285. A gate that no obtainable model can pass kills the idea
   honestly; an undefined gate invites post-hoc rationalization. Note the
   paired design means low Dice does not add noise to the edit response
   (same frozen model, same case, deterministic inference) — the gate's
   real function is to ensure the model is good enough for its internal
   computations to be worth interrogating, and the card must say what
   "good enough" is **[INF]**.
3. **Add an NCCT-sensitivity gate.** If the frozen model effectively
   ignores its NCCT channel (checkable by channel ablation on unedited
   cases before any cavity edit), the intervention is vacuous and every
   null is uninterpretable. This gate must precede the paired experiment,
   and failing it is a kill, not a footnote. This interacts with section 3:
   an NCCT-insensitive model is plausible when perfusion maps carry most
   final-infarct signal **[SPEC, but cheap to check]**.

## 6. The prevalence gate is arbitrary and probably miscalibrated

The card demands ≥15 of the first 30 cases (50%) carry a stable remote
cavity ≥1 mL. No cited source supports 50% prevalence of *cavitated,
contralateral, ≥1 mL* chronic infarcts in an acute-LVO cohort; the frailty
literature reports old infarcts on NCCT in a minority-to-moderate fraction
of acute stroke cohorts **[SS]**, and the contralateral-only restriction
roughly halves whatever that number is **[INF]**. As written, the gate
likely fails even in a world where the experiment is viable — it confuses
"prevalence is high" with "enough editable cases exist."

**Repair:** census **all 149 public training cases** (the census is
automated; 30 was never a cost-driven cap), and gate on a pre-specified
minimum count of editable cases derived from a paired-test power sketch,
not on a prevalence fraction. Keystone-screen framing stands: this census
is the Stage 0 kill experiment and is genuinely cheap.

## 7. Leakage, circularity, compute, data access — checked, no objection

No concept labels exist, so no circularity. The paired within-case design
has no train/test leakage surface; the 149 census cases are training-split
cases, acceptable because the endpoint is model-behavior measurement, not
performance claims — though if the frozen model is locally trained, edited
cases must come from its validation fold, which the revision should pin
**[INF]**. Compute (≈20 GPU-hours inference + bounded training) is honest
once section 5's training cost is added. Data access is verified public
(keystone screen, Zenodo record 16813698). License CC BY-SA-NC 4.0 permits
this use **[VF, keystone screen]**.

## 8. Portfolio note: homogenization

`design_template: regional-removal` joins a portfolio already carrying
regional-substitution ×9 and counterfactual-synthesis ×10. This is another
edit-the-input-and-compare move with rotated nouns. It is also the cleanest
member of its family on this dataset — a discrete, remote, bounded lesion
rather than a diffuse field (contrast the "frail brain" backlog candidate
isles24-scout-001-c04, which this card correctly distinguishes). Acceptable,
but the shortlist as a whole is buying many tickets in one lottery
**[INF]**.

## 9. Plain-pitch fidelity (opposite-family check)

Two defects, one mild, one real:

1. **Etiology hedge partially dropped.** The card's residual assumption is
   explicit that a positive result supports "use of cavity-like tissue
   loss, **not proven prior infarction**." The pitch's operative sentence
   does say "the old-**looking** cavity" — the hedge survives there — but
   the opening ("An old stroke can leave a fluid-filled cavity… looks
   across the brain at that old damage") presents the etiology as settled.
   Mild; fix by one word ("old-looking damage" or equivalent).
2. **Reserve framing.** "Treats the patient as more vulnerable" asserts in
   plain language the brain-reserve interpretation that section 2 shows the
   design cannot identify. This is the same overclaim as the deliverable
   sentence, translated. It must be fixed jointly with section 2 — e.g.,
   "asks whether that old-looking damage changes the forecast," dropping
   the vulnerability gloss.

Also noted with approval: "leaving the new stroke and its blood-flow maps
untouched" states the single-channel edit plainly — the pitch is honest
about the very property section 3 critiques.

## Verdict

ADVANCE TO REVISION. Required revisions, in priority order: (1) reduce the
deliverable/question/pitch to cavity-appearance use, dropping "brain
reserve" (sections 2, 9); (2) restate the estimand as NCCT-channel use,
designate the CSF sham as the mismatch control, add the NCCT-sensitivity
ablation gate (sections 3, 5.3); (3) pin the donor-exclusion rule (section
4); (4) name the frozen-model path and define the performance gate
numerically (section 5); (5) recalibrate the prevalence gate to a
power-derived editable-case count over all 149 cases (section 6). None of
these changes the question; all of them change whether the answer would be
believed.

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does a frozen ISLES'24 final-infarct
model change its affected-hemisphere prediction, beyond matched CSF and
parenchyma shams, when contralateral chronic-cavity-like tissue loss is
inpainted out of the NCCT channel?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — the prior-damage question
survives intact; the brain-reserve interpretation is deferred to a successor
with independent physiological grounding.
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is this candidate after
revision-in-place; the estimand and endpoint are unchanged.
IS IT ACTUALLY WORTH DOING? YES, conditionally — the census-first design
means the world answers the killing questions (prevalence, separability,
NCCT sensitivity) for about two days of work before any expensive commitment,
and both the positive and the gated negative would be citable facts about
what final-infarct models consult; if the census or the NCCT-ablation gate
fails, kill it without regret.
```

## Sources checked this stage

- ISLES'24 challenge results: arXiv 2408.10966 (top model Dice 0.285 ± 0.213,
  AVD 21.2 ± 37.2 mL, hidden test n=98) — abstract-level fetch.
- ISLES'24 winner method: arXiv 2505.18424 (residual nnU-Net + preprocessing;
  no release statement found at abstract level) — abstract-level fetch.
- Brain frailty association family (title/abstract level only): IST-3
  secondary analysis, Lancet Neurol 2015 (PMC4513190); Neurology 2020,
  DOI 10.1212/WNL.0000000000008881; brain-frailty/thrombolysis 2025
  (PMID 41026485).
- Prior stages relied on: ideas/044/keystone_screen.md (Riedel et al.,
  DOI 10.1148/ryai.250603; Zenodo 16813698; clinical dictionary has no
  prior-stroke variable).


===== ideas/044/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed intervention cannot answer the original question because a response to removing a contralateral cavity does not identify reduced brain reserve as the model's interpretation of that cue.

**Argument:** The card asks whether chronic infarct cavities are used "as a marker of reduced brain reserve," yet its own identifiability score and confound list concede that the same paired response could arise because the cavity is an age proxy, a generic marker of prior vascular disease, or simply a learned NCCT morphology associated with final-infarct labels. Holding the acute lesion and perfusion inputs fixed isolates sensitivity to the edited NCCT appearance; the CSF and parenchyma shams can rule out generic filling or boundary effects. Neither operation distinguishes reserve from those other patient-level meanings. ISLES'24 supplies admission imaging and follow-up-infarct ground truth, but no independent reserve measurement or perturbation, so even a clean positive result supports only use of contralateral chronic-cavity-like appearance. The proposed critique repair that drops "brain reserve" remains the same operational estimand and is a defensible narrowing, but until the actual question, deliverable, suspected-signal claim, and pitch are narrowed together, the live study overclaims what it tests.

**What would change my mind:** Either revise the card consistently so its claim is limited to NCCT-channel use of contralateral chronic-cavity-like tissue loss, with reserve explicitly left unestablished, or add an independently validated reserve measurement or intervention and a prespecified contrast that separates reserve-mediated responses from age and prior-vascular-disease proxy responses.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The design measures whether the model's affected-hemisphere forecast responds to editing out contralateral cavity-like tissue loss in the NCCT channel — nothing more. It cannot distinguish a reserve interpretation from an age proxy, a prior-vascular-disease proxy, or a bare learned morphology-label association, and ISLES'24 contains no independent reserve measurement that could supply that discrimination. Yet the live card carries "brain reserve" in the question, the deliverable sentence, the suspected-signal claim, and the pitch, so the study as registered overclaims what its own intervention tests.

**Response:** AMEND

**Argument:** The objection is correct on the substance and I will not defend the reserve wording; the card's own identifiability rationale ("cavity use but not whether the model interprets it as reserve or age") already concedes it, and the critique reached the same verdict independently. The second branch of the critic's resolution — adding an independently validated reserve measurement — is not available inside ISLES'24 and would be a different study; per the idea-023 precedent (decisions.md, 2026-08-17), physiological naming on top of an operational estimand requires challenge- or validation-based grounding in a successor, not a rider on this card. So I take the first branch, in full and jointly across every surface the critic listed:

1. **Question** becomes: "Is the frozen final-infarct model using contralateral chronic-cavity-like tissue loss in the admission-NCCT channel when forecasting new infarction?"
2. **Deliverable sentence** becomes: "The final-infarct model is using remote chronic-cavity-like tissue loss on admission NCCT when forecasting new infarction." No reserve clause.
3. **Suspected signal** retains the reserve physiology only as motivation for why such a cue could exist, with an explicit sentence that reserve, age-proxy, and prior-vascular-disease readings are observationally equivalent under this design and none is established by any outcome.
4. **Prohibited conclusions** gain an entry: a positive result may not be described as evidence that the model measures brain reserve, patient age, or vascular-disease burden; it demonstrates NCCT-channel use of contralateral cavity-like appearance only.
5. **Plain pitch** drops "treats the patient as more vulnerable" in favor of "asks whether that old-looking damage changes the forecast," and "that old damage" becomes "that old-looking damage" so the etiology hedge survives translation.

The estimand is scoped to the NCCT channel explicitly (the critic's own phrase "NCCT-channel use" is adopted), which also aligns the claim with the critique's separate cross-channel finding: the cavity persists in the perfusion maps, so a null licenses "does not use the NCCT-channel appearance," never "does not use the cavity."

**Identity check:** the revised design answers the revised question with the identical intervention, shams, endpoint, gates, and paired analysis; nothing operational changes. Under the claim-identity rule (2026-08-10) this is a narrowing that deletes an interpretive rider while the measured contrast and the prohibited-conclusions direction are preserved and strengthened — revision-in-place, not a successor. The rule's REJECT trigger is a change of deliverable identity; here the deliverable sentence loses an adjective phrase the design never had the right to assert.

**What is lost:** real value, and it should be priced. The reserve interpretation was the bridge from this experiment to a physician-legible vulnerability story, and it carried part of `medical_relevance: 4` and `interest: 4`; both scores should be re-argued at revision (interest also owes a debit to the critique's low-prior finding). What survives is the load-bearing part: whether a final-infarct model consults remote old-looking damage at all is a citable fact about model behavior — for transportability across cohorts with differing chronic-lesion prevalence and for auditing what these models actually read — whichever interpretation later wins. Reserve-as-mechanism is recorded as a potential successor requiring independent physiological grounding (e.g., a cohort with a validated reserve construct), not as a spin-off registered now.

This is amendment 1 of this debate; it converges with, and does not substitute for, the critique's other required revisions (frozen-model pin, NCCT-sensitivity ablation gate, donor-exclusion rule, power-derived census gate), which stand for the revision stage.

**Status:** CONVERGED

## Round 3 — CRITIC

**Position:** The amendment changes the claim's identity: NCCT-channel sensitivity to cavity-like appearance does not answer the original question of whether the model uses chronic infarct cavities as a reduced-brain-reserve signal.

**Argument:** The proposer's operational concession is scientifically correct but its governance conclusion is not. The 2026-08-10 claim-identity rule in `evidence/decisions.md` states that revision-in-place is allowed only when the deliverable claim remains the same, and that changing the deliverable sentence or the prohibited-conclusions set requires rejecting the original idea as superseded and registering a new candidate. This amendment does both: it removes the causal/physiological predicate "as a brain-reserve signal" from the deliverable and newly prohibits precisely that conclusion. That phrase is not an expendable adjective; it distinguishes the original mechanism claim from the replacement's morphology-sensitivity claim. The unchanged intervention cannot rescue identity, because the critic's first round established that this intervention never identified reserve in the first place. The replacement is worth considering, but approving it in place would make idea 044 appear to have survived debate after abandoning the question that defined it.

**What would change my mind:** Either show an independently validated reserve measurement or intervention that makes the paired contrast distinguish reserve use from age, vascular-disease burden, and bare morphology-label association while retaining idea 044, or reject idea 044 as superseded and register the NCCT-channel cavity-appearance study as a new candidate with `parent_ids` linking it to idea 044.

**Status:** OPEN

## Round 4 — PROPOSER

**Responding to:** My round-2 amendment changed both the deliverable sentence and the prohibited-conclusions set — exactly the two triggers the 2026-08-10 claim-identity rule names for REJECTED (superseded) plus registration of a new candidate with `parent_ids`. Calling that a revision-in-place would let idea 044 appear to survive debate while abandoning the reserve question that defined its registration.

**Response:** CONCEDE

**Argument:** The critic is right, and my round-2 identity check was wrong. Two points settle it against me:

1. **The letter of the rule, and its founding case.** The 2026-08-10 rule triggers on "when the deliverable sentence or the prohibited-conclusions set changes." Round 2 did both and itemized the changes. My defense was that the deleted phrase is "an adjective phrase the design never had the right to assert" — but that is an argument the rule's founding case already heard and rejected. Idea 015 lost precisely an interpretive physiological rider (the vascular-age reading) sitting on top of an operational contrast (the BAC-response experiment) that survived unchanged, and the ruling was REJECTED (superseded), with the successor re-entering through a normal scouting cycle, receiving its own novelty audit, and holding no inherited queue position. Reserve-on-top-of-cavity-edit is structurally identical to vascular-age-on-top-of-BAC-response. Relitigating the rule's founding case from inside a debate is not a rebuttal.

2. **The precedent I leaned on does not carry the weight I put on it.** Idea 023's claim-language reduction (decisions.md, 2026-08-17) happened at a human-inspection stage: the operator answered the debate's question, fixed the claim language, and ratified the binding disclaimer. Whatever tension exists between that disposition and the 2026-08-10 rule is the operator's to resolve, not a proposer's to exploit; the debate cannot self-award a dispensation the operator granted case-specifically elsewhere. For its own disposition the debate has only the written rule, and the written rule says supersede. I flag the tension explicitly for the decision stage: if the operator regards 023-style language reduction as legitimate revision-in-place, they may overrule this concession; the default disposition follows the rule.

**Recommended disposition:** idea 044 REJECTED (superseded). This is not a defect of the experiment — no fatal objection was found; the intervention, shams, endpoint, gates, and census-first economics all stand — but of the claim the card was registered to deliver, which round 1 established the design never could deliver.

**Spin-off (recorded, not registered):** the NCCT-channel cavity-appearance study, exactly as specified in round 2 items 1–5 (narrowed question and deliverable, reserve demoted to suspected-signal motivation with the observational-equivalence sentence, expanded prohibited conclusions, corrected plain pitch), carrying the critique's five revision pins (frozen-model path with a numeric performance gate; NCCT-sensitivity ablation gate preceding any paired run; donor-exclusion rule for mirrored sampling; power-derived editable-case census over all 149 public cases replacing the 15-of-30 prevalence fraction; CSF sham designated as the cross-channel mismatch control), with `parent_ids: ["isles24-scout-005-c02"]`. Per the 2026-08-10 rule and the S2 note of the same date, it re-enters through a normal scout cycle or librarian proposal — not manual registration here — and is re-ranked on current merit. The reserve-mechanism question itself remains a further, distinct successor requiring a cohort with an independently validated reserve construct.

**What is lost:** the shortlist slot and queue position. The successor competes fresh against a backlog in which the critique's low-prior finding will rightly count against it. That is the rule working as intended, and conceding now — one round after the governance objection — costs less than defending a disposition the ledger already forecloses.

**Status:** CONCEDED

## Round 5 — CRITIC

**Position:** The proposer has resolved my objection by conceding that idea 044 must be rejected as superseded rather than revised in place.

**Argument:** The concession is supported by a governance argument, not mere agreement: it applies the explicit 2026-08-10 claim-identity triggers to the amendment's changed deliverable sentence and prohibited-conclusions set, and it identifies the founding idea-015 disposition as structurally analogous. The proposer also correctly withdraws the attempted reliance on idea 023 because that was a case-specific human ruling, not authority for this debate to waive the standing rule. The resulting disposition preserves the scientific distinction established in round 1: ISLES'24 has no independent reserve measurement, so the registered brain-reserve claim remains untestable by the proposed NCCT edit, while the narrower cavity-appearance experiment is a different candidate that may re-enter with lineage and fresh review. I have no remaining objection to that disposition; the successor's frozen-model, sensitivity, donor, census, and mismatch-control requirements are appropriately recorded for its own pipeline rather than used to rehabilitate idea 044.

**What would change my mind:** Only an independently validated reserve measurement or intervention that distinguishes reserve-mediated model behavior from age, vascular-disease burden, and bare cavity-morphology association would justify retaining the original idea 044 claim.

**Status:** CONCEDED


===== ideas/044/idea_card.json =====
{
  "id": "isles24-scout-005-c02",
  "parent_ids": [],
  "search_mode": "B",
  "entry_point": 2,
  "title": "The old stroke inside the new forecast",
  "question": "Is the model using contralateral chronic infarct cavities as a marker of reduced brain reserve when forecasting new infarction?",
  "rung": "Target rung 1: use of remote chronic-infarct appearance; rung 2 requires replication with a separately trained model and an external acute-stroke cohort.",
  "deliverable_sentence": "The final-infarct model is using remote chronic infarct cavities as a brain-reserve signal when forecasting new infarction.",
  "X_measurement": "Within brain parenchyma outside ventricles and the acute Tmax>6 s territory, X is connected CSF-like hypodensity (0-30 HU) with a surrounding gliotic low-attenuation rim and atlas-inconsistent tissue loss; quantify volume and surface area, with contralateral lesions primary. A deterministic threshold/connected-component measurement can be run today on unseen NCCT after automated brain/ventricle segmentation, without an annotator; measurement validity is a gate rather than assumed diagnosis.",
  "suspected_signal": "Chronic infarcts leave encephalomalacic cavities and volume loss. They encode prior vascular injury and reduced reserve, which may lead a model to enlarge expected tissue loss even when the old lesion is remote from the current perfusion deficit.",
  "use_vs_association": "Within each case, fill only contralateral remote cavities with texture sampled from mirrored homologous tissue, while holding all acute CT, CTA, perfusion, and affected-hemisphere voxels fixed. A predicted-lesion change in the affected hemisphere, exceeding equal-volume normal-CSF and random-parenchyma shams, demonstrates use; cross-sectional correlation alone is supporting only.",
  "keystone_prerequisite": "A nontrivial subset of admission NCCTs contains automatically separable remote chronic infarct cavities rather than only nonspecific low attenuation.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_residual_assumption": "The 0-30 HU morphology rule may confuse enlarged perivascular spaces, arachnoid cysts, surgical cavities, and severe leukoaraiosis. The first 20 cases require blinded algorithmic stability checks across thresholds; without released chronic-lesion labels, a positive use result supports use of cavity-like tissue loss, not proven prior infarction.",
  "rung_reached": "0; rung 1 after prevalence, stability, remoteness, realism, and sham gates.",
  "dies_like_prior": "Closest to isles24-scout-001-c04 (frail brain) but differs in a discrete, remotely editable lesion rather than diffuse correlated frailty. It avoids idea-020's geometry confounding by editing contralateral tissue while freezing the affected input. Annotation provenance is not load-bearing because the primary endpoint is paired model output.",
  "closest_prior_work": "Prior-infarct burden is a recognized imaging marker, while infarct pattern predicts function independent of volume (Radiology 2021, DOI 10.1148/radiol.2021203964). The ISLES'24 dataset paper includes patient history but does not report a model-use test for old cavities (DOI 10.1148/ryai.250603). No verified prior intervention study on this question was found; that is not proof of novelty.",
  "existing_assets": "Raw NCCT, registered acute maps, automatic brain/ventricle segmentation tools, mirrored tissue donor regions, and label-free paired output comparison.",
  "smallest_decisive_experiment": "Census the first 30 cases; proceed only if at least 15 have stable remote cavity volume of at least 1 mL. On those cases perform cavity fill, ventricle-adjacent CSF fill, and random-parenchyma shams. About 2 days measurement work and 20 GPU-hours once a model is frozen.",
  "standing_confounds_addressed": "Paired edits fix scanner, vendor, protocol, site, positioning, habitus, prevalence, referral, and all acute pathology. Contralateral remoteness prevents direct lesion overlap. Shams address generic filling and CSF-boundary effects. It does not prove the cavity's etiology or distinguish prior-injury reserve from a learned age proxy.",
  "alternative_explanations": [
    "The response is to any CSF boundary; ventricle and arachnoid-space shams test this.",
    "The cavity is a proxy for age, not reserve; age-stratified response is reported but cannot fully distinguish the two.",
    "Inpainting artifacts drive the response; use two independent fill methods and require concordance."
  ],
  "anticipated_negative": "Decisive only if prevalence, segmentation stability, model performance, and two-method edit realism gates pass; otherwise sensitivity-limited.",
  "remaining_legwork": "2 days to the prevalence kill decision; 4-6 days to paired results; under 20 GPU-hours; no new labels requested.",
  "design_template": "regional-removal",
  "entry_point_2_requirements": "Measurement: remote CSF-like cavity burden. Confused artifacts: ventricles/other CSF spaces and inpainting seams; anatomic shams and two fill methods address them.",
  "scores": {
    "clarity": {
      "value": 4,
      "why": "The cue and paired edit are clear, though lesion classification needs a gate."
    },
    "identifiability": {
      "value": 3,
      "why": "Remote editing identifies cavity use but not whether the model interprets it as reserve or age."
    },
    "medical_relevance": {
      "value": 4,
      "why": "Prior injury is clinically meaningful context for tissue vulnerability and transportability."
    },
    "interest": {
      "value": 4,
      "why": "A new-lesion model consulting old damage is plausible but not routinely measured."
    },
    "prior_legwork": {
      "value": 3,
      "why": "Segmentation ingredients exist, but no released chronic-lesion labels."
    },
    "feasibility": {
      "value": 3,
      "why": "Capped because the prevalence and separability keystone is uninspected."
    },
    "data_readiness": {
      "value": 4,
      "why": "All images are public and no external outcomes are needed."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "Paired output is direct; cavity-validity metrics are custom."
    },
    "negative_result_value": {
      "value": 3,
      "why": "Useful after stringent prevalence and realism gates."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Limited primary-source search only."
    },
    "regret": {
      "value": 3,
      "why": "Worth a cheap census before more elaborate reserve experiments."
    }
  },
  "priority_score": 3.4,
  "unverified_claims": [
    "remote chronic-cavity prevalence",
    "automatic specificity",
    "edit realism",
    "novelty"
  ],
  "plain_pitch": "An old stroke can leave a fluid-filled cavity in the brain. This study asks whether a model predicting a new stroke looks across the brain at that old damage and treats the patient as more vulnerable. Filling only the old-looking cavity in a copy of the scan, while leaving the new stroke and its blood-flow maps untouched, would reveal whether that remote history changes the forecast.",
  "track": "baseline",
  "charter": "isles24"
}


===== ideas/044/keystone_screen.md =====
# Keystone screen — Idea 044

## Keystone as stated

> A nontrivial subset of admission NCCTs contains automatically separable remote chronic infarct cavities rather than only nonspecific low attenuation.

The card operationalizes “nontrivial” more strongly in its smallest decisive experiment: among the first 30 cases, at least 15 must have a stable remote cavity volume of at least 1 mL.

## What was inspected

1. **Primary dataset publication.** Riedel et al., *Radiology: Artificial Intelligence* (2026), DOI 10.1148/ryai.250603, full text, “Data Repository and Storage” and “Data Structure.” The paper establishes the inspectable cohort and admission imaging:

   > “The training dataset (n = 149) is publicly available under the CC BY-SA-NC 4.0 license via Zenodo.”

   Source: https://pubs.rsna.org/doi/full/10.1148/ryai.250603, “Data Repository and Storage,” lines 120–124 in the HTML full text.

   The paper’s Table 1 reports atrial fibrillation, hypertension, diabetes, dyslipidemia, medications, and premorbid mRS, but it does not report prior-stroke history, chronic infarct cavities, encephalomalacia, or a cavity census. Its lesion statistics concern the follow-up DWI final infarct reference, not pre-existing lesions on admission NCCT.

2. **Primary dataset release page.** The official Zenodo record describes each case as including:

   > “Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

   Source: https://zenodo.org/records/16813698, “Description,” list of data included for each case.

   This verifies that the images needed for a census exist. It does not establish that any admission NCCT contains a remote chronic cavity, much less that at least 15 of 30 do or that a deterministic rule separates those cavities from mimics.

3. **Released clinical-data dictionary.** The 12.1-kB `clinical_data-description.xlsx` was downloaded from the official Zenodo record and inspected. Its history fields describe atrial fibrillation, hypertension, diabetes, hyperlipidemia, anticoagulation, statins, and platelet aggregation inhibitors; it provides no prior-stroke or chronic-infarct variable. The closest potentially relevant entry is:

   > “mRS premorbid as stated by patient or relatives.”

   Source: https://zenodo.org/records/16813698/files/clinical_data-description.xlsx?download=1, “Supplementary Table 1,” `mRS premorbid` row.

   Premorbid disability is not evidence of a chronic infarct cavity and cannot supply the missing prevalence or imaging-specificity fact.

## Residual-assumption check

The nearest checkable fact is only that 149 public training cases contain admission NCCT. The load-bearing assumption remains two-part and unverified: (1) sufficiently many NCCTs contain contralateral remote cavity-like tissue loss of the card’s required size, and (2) the proposed automatic morphology rule distinguishes that phenotype from ventricles, enlarged perivascular spaces, arachnoid or surgical cavities, and severe leukoaraiosis. Neither the dataset paper, its cohort tables, the release description, nor the released clinical dictionary provides a chronic-lesion annotation or census. Verifying the actual keystone therefore requires inspection of the released NCCT voxels (and the card’s separability criterion requires a defensible reference assessment); the primary documentation alone cannot settle it.

```json
{"verdict": "UNVERIFIABLE", "evidence": "The training dataset (n = 149) is publicly available under the CC BY-SA-NC 4.0 license via Zenodo.", "source": "https://pubs.rsna.org/doi/full/10.1148/ryai.250603 — Data Repository and Storage, lines 120–124", "note": "Primary sources verify an inspectable NCCT cohort but provide no chronic-cavity prevalence or separability evidence; an image-level census remains necessary."}
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

**Position:** The proposed intervention cannot answer the original question because a response to removing a contralateral cavity does not identify reduced brain reserve as the model's interpretation of that cue.

**Argument:** The card asks whether chronic infarct cavities are used "as a marker of reduced brain reserve," yet its own identifiability score and confound list concede that the same paired response could arise because the cavity is an age proxy, a generic marker of prior vascular disease, or simply a learned NCCT morphology associated with final-infarct labels. Holding the acute lesion and perfusion inputs fixed isolates sensitivity to the edited NCCT appearance; the CSF and parenchyma shams can rule out generic filling or boundary effects. Neither operation distinguishes reserve from those other patient-level meanings. ISLES'24 supplies admission imaging and follow-up-infarct ground truth, but no independent reserve measurement or perturbation, so even a clean positive result supports only use of contralateral chronic-cavity-like appearance. The proposed critique repair that drops "brain reserve" remains the same operational estimand and is a defensible narrowing, but until the actual question, deliverable, suspected-signal claim, and pitch are narrowed together, the live study overclaims what it tests.

**What would change my mind:** Either revise the card consistently so its claim is limited to NCCT-channel use of contralateral chronic-cavity-like tissue loss, with reserve explicitly left unestablished, or add an independently validated reserve measurement or intervention and a prespecified contrast that separates reserve-mediated responses from age and prior-vascular-disease proxy responses.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The design measures whether the model's affected-hemisphere forecast responds to editing out contralateral cavity-like tissue loss in the NCCT channel — nothing more. It cannot distinguish a reserve interpretation from an age proxy, a prior-vascular-disease proxy, or a bare learned morphology-label association, and ISLES'24 contains no independent reserve measurement that could supply that discrimination. Yet the live card carries "brain reserve" in the question, the deliverable sentence, the suspected-signal claim, and the pitch, so the study as registered overclaims what its own intervention tests.

**Response:** AMEND

**Argument:** The objection is correct on the substance and I will not defend the reserve wording; the card's own identifiability rationale ("cavity use but not whether the model interprets it as reserve or age") already concedes it, and the critique reached the same verdict independently. The second branch of the critic's resolution — adding an independently validated reserve measurement — is not available inside ISLES'24 and would be a different study; per the idea-023 precedent (decisions.md, 2026-08-17), physiological naming on top of an operational estimand requires challenge- or validation-based grounding in a successor, not a rider on this card. So I take the first branch, in full and jointly across every surface the critic listed:

1. **Question** becomes: "Is the frozen final-infarct model using contralateral chronic-cavity-like tissue loss in the admission-NCCT channel when forecasting new infarction?"
2. **Deliverable sentence** becomes: "The final-infarct model is using remote chronic-cavity-like tissue loss on admission NCCT when forecasting new infarction." No reserve clause.
3. **Suspected signal** retains the reserve physiology only as motivation for why such a cue could exist, with an explicit sentence that reserve, age-proxy, and prior-vascular-disease readings are observationally equivalent under this design and none is established by any outcome.
4. **Prohibited conclusions** gain an entry: a positive result may not be described as evidence that the model measures brain reserve, patient age, or vascular-disease burden; it demonstrates NCCT-channel use of contralateral cavity-like appearance only.
5. **Plain pitch** drops "treats the patient as more vulnerable" in favor of "asks whether that old-looking damage changes the forecast," and "that old damage" becomes "that old-looking damage" so the etiology hedge survives translation.

The estimand is scoped to the NCCT channel explicitly (the critic's own phrase "NCCT-channel use" is adopted), which also aligns the claim with the critique's separate cross-channel finding: the cavity persists in the perfusion maps, so a null licenses "does not use the NCCT-channel appearance," never "does not use the cavity."

**Identity check:** the revised design answers the revised question with the identical intervention, shams, endpoint, gates, and paired analysis; nothing operational changes. Under the claim-identity rule (2026-08-10) this is a narrowing that deletes an interpretive rider while the measured contrast and the prohibited-conclusions direction are preserved and strengthened — revision-in-place, not a successor. The rule's REJECT trigger is a change of deliverable identity; here the deliverable sentence loses an adjective phrase the design never had the right to assert.

**What is lost:** real value, and it should be priced. The reserve interpretation was the bridge from this experiment to a physician-legible vulnerability story, and it carried part of `medical_relevance: 4` and `interest: 4`; both scores should be re-argued at revision (interest also owes a debit to the critique's low-prior finding). What survives is the load-bearing part: whether a final-infarct model consults remote old-looking damage at all is a citable fact about model behavior — for transportability across cohorts with differing chronic-lesion prevalence and for auditing what these models actually read — whichever interpretation later wins. Reserve-as-mechanism is recorded as a potential successor requiring independent physiological grounding (e.g., a cohort with a validated reserve construct), not as a spin-off registered now.

This is amendment 1 of this debate; it converges with, and does not substitute for, the critique's other required revisions (frozen-model pin, NCCT-sensitivity ablation gate, donor-exclusion rule, power-derived census gate), which stand for the revision stage.

**Status:** CONVERGED

## Round 3 — CRITIC

**Position:** The amendment changes the claim's identity: NCCT-channel sensitivity to cavity-like appearance does not answer the original question of whether the model uses chronic infarct cavities as a reduced-brain-reserve signal.

**Argument:** The proposer's operational concession is scientifically correct but its governance conclusion is not. The 2026-08-10 claim-identity rule in `evidence/decisions.md` states that revision-in-place is allowed only when the deliverable claim remains the same, and that changing the deliverable sentence or the prohibited-conclusions set requires rejecting the original idea as superseded and registering a new candidate. This amendment does both: it removes the causal/physiological predicate "as a brain-reserve signal" from the deliverable and newly prohibits precisely that conclusion. That phrase is not an expendable adjective; it distinguishes the original mechanism claim from the replacement's morphology-sensitivity claim. The unchanged intervention cannot rescue identity, because the critic's first round established that this intervention never identified reserve in the first place. The replacement is worth considering, but approving it in place would make idea 044 appear to have survived debate after abandoning the question that defined it.

**What would change my mind:** Either show an independently validated reserve measurement or intervention that makes the paired contrast distinguish reserve use from age, vascular-disease burden, and bare morphology-label association while retaining idea 044, or reject idea 044 as superseded and register the NCCT-channel cavity-appearance study as a new candidate with `parent_ids` linking it to idea 044.

**Status:** OPEN

## Round 4 — PROPOSER

**Responding to:** My round-2 amendment changed both the deliverable sentence and the prohibited-conclusions set — exactly the two triggers the 2026-08-10 claim-identity rule names for REJECTED (superseded) plus registration of a new candidate with `parent_ids`. Calling that a revision-in-place would let idea 044 appear to survive debate while abandoning the reserve question that defined its registration.

**Response:** CONCEDE

**Argument:** The critic is right, and my round-2 identity check was wrong. Two points settle it against me:

1. **The letter of the rule, and its founding case.** The 2026-08-10 rule triggers on "when the deliverable sentence or the prohibited-conclusions set changes." Round 2 did both and itemized the changes. My defense was that the deleted phrase is "an adjective phrase the design never had the right to assert" — but that is an argument the rule's founding case already heard and rejected. Idea 015 lost precisely an interpretive physiological rider (the vascular-age reading) sitting on top of an operational contrast (the BAC-response experiment) that survived unchanged, and the ruling was REJECTED (superseded), with the successor re-entering through a normal scouting cycle, receiving its own novelty audit, and holding no inherited queue position. Reserve-on-top-of-cavity-edit is structurally identical to vascular-age-on-top-of-BAC-response. Relitigating the rule's founding case from inside a debate is not a rebuttal.

2. **The precedent I leaned on does not carry the weight I put on it.** Idea 023's claim-language reduction (decisions.md, 2026-08-17) happened at a human-inspection stage: the operator answered the debate's question, fixed the claim language, and ratified the binding disclaimer. Whatever tension exists between that disposition and the 2026-08-10 rule is the operator's to resolve, not a proposer's to exploit; the debate cannot self-award a dispensation the operator granted case-specifically elsewhere. For its own disposition the debate has only the written rule, and the written rule says supersede. I flag the tension explicitly for the decision stage: if the operator regards 023-style language reduction as legitimate revision-in-place, they may overrule this concession; the default disposition follows the rule.

**Recommended disposition:** idea 044 REJECTED (superseded). This is not a defect of the experiment — no fatal objection was found; the intervention, shams, endpoint, gates, and census-first economics all stand — but of the claim the card was registered to deliver, which round 1 established the design never could deliver.

**Spin-off (recorded, not registered):** the NCCT-channel cavity-appearance study, exactly as specified in round 2 items 1–5 (narrowed question and deliverable, reserve demoted to suspected-signal motivation with the observational-equivalence sentence, expanded prohibited conclusions, corrected plain pitch), carrying the critique's five revision pins (frozen-model path with a numeric performance gate; NCCT-sensitivity ablation gate preceding any paired run; donor-exclusion rule for mirrored sampling; power-derived editable-case census over all 149 public cases replacing the 15-of-30 prevalence fraction; CSF sham designated as the cross-channel mismatch control), with `parent_ids: ["isles24-scout-005-c02"]`. Per the 2026-08-10 rule and the S2 note of the same date, it re-enters through a normal scout cycle or librarian proposal — not manual registration here — and is re-ranked on current merit. The reserve-mechanism question itself remains a further, distinct successor requiring a cohort with an independently validated reserve construct.

**What is lost:** the shortlist slot and queue position. The successor competes fresh against a backlog in which the critique's low-prior finding will rightly count against it. That is the rule working as intended, and conceding now — one round after the governance objection — costs less than defending a disposition the ledger already forecloses.

**Status:** CONCEDED

## Round 5 — CRITIC

**Position:** The proposer has resolved my objection by conceding that idea 044 must be rejected as superseded rather than revised in place.

**Argument:** The concession is supported by a governance argument, not mere agreement: it applies the explicit 2026-08-10 claim-identity triggers to the amendment's changed deliverable sentence and prohibited-conclusions set, and it identifies the founding idea-015 disposition as structurally analogous. The proposer also correctly withdraws the attempted reliance on idea 023 because that was a case-specific human ruling, not authority for this debate to waive the standing rule. The resulting disposition preserves the scientific distinction established in round 1: ISLES'24 has no independent reserve measurement, so the registered brain-reserve claim remains untestable by the proposed NCCT edit, while the narrower cavity-appearance experiment is a different candidate that may re-enter with lineage and fresh review. I have no remaining objection to that disposition; the successor's frozen-model, sensitivity, donor, census, and mismatch-control requirements are appropriately recorded for its own pipeline rather than used to rehabilitate idea 044.

**What would change my mind:** Only an independently validated reserve measurement or intervention that distinguishes reserve-mediated model behavior from age, vascular-disease burden, and bare cavity-morphology association would justify retaining the original idea 044 claim.

**Status:** CONCEDED

