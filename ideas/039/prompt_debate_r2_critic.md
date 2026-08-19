You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/039
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
- **idea-039** [SHORTLISTED/CRITIQUED/wide] -- Does the model trust tissue that obeys the flow equation?
- **idea-040** [SHORTLISTED/SCOUTED/baseline] -- The pressure history written in a winding artery
- **idea-041** [SHORTLISTED/SCOUTED/wide] -- The roughness of a heartbeat through starved tissue
- **idea-042** [SHORTLISTED/SCOUTED/wide] -- Delay is not dispersion
- **idea-043** [SHORTLISTED/SCOUTED/baseline] -- What the winner's brain window revealed
- **idea-044** [SHORTLISTED/SCOUTED/baseline] -- The old stroke inside the new forecast
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
- [isles24] **idea-040** [SHORTLISTED] -- The pressure history written in a winding artery
- [isles24] **idea-041** [SHORTLISTED] -- The roughness of a heartbeat through starved tissue
- [isles24] **idea-042** [SHORTLISTED] -- Delay is not dispersion
- [isles24] **idea-043** [SHORTLISTED] -- What the winner's brain window revealed
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


===== ideas/039/README.md =====
# Idea 039: Does the model trust tissue that obeys the flow equation?

Selected from scouting cycle isles24-005, candidate 6.


===== ideas/039/critique.md =====
# Critique — idea 039 (isles24-scout-005-c06): Does the model trust tissue that obeys the flow equation?

```
FATAL OBJECTION: The confirmatory contrast (residual-removal projection vs
equal-energy tangent shams) identifies directional sensitivity of a nonlinear
multichannel function, not use of the residual "as a hidden confidence map" —
the deliverable sentence is not identified by the stated design.
EVIDENCE: idea_card.json `use_vs_association` vs `deliverable_sentence`; a
residual-blind model reading raw MTT values can pass every stated gate (§1).
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

---

## 1. The decisive objection: anisotropy is not confidence

The card's use-versus-association move is: project the (CBF, CBV, MTT)
triplet onto the central-volume-consistent manifold, compare against
equal-per-channel-L2 perturbations tangent to the manifold, and read a
"selective, graded response to removing only the normal residual" as evidence
of use. The claimed estimand is stronger than that contrast can deliver.

Any smooth multichannel function responds anisotropically to input
perturbations. The normal direction to the constraint manifold is one
particular direction in input space, and — critically — the normal
*component* of a case's maps is a specific spatial pattern (concentrated
where noise, delay sensitivity, and regularization broke the identity).
A model with **no inconsistency computation of any kind** — say, one that
reads MTT values with a spatially varying learned weighting — will generically
respond more to the normal-direction edit than to a tangent sham, simply
because the normal component's spatial distribution differs from the sham's
and correlates differently with the lesion-relevant tissue. Matching
per-channel L2 energy equalizes edit *size*, not edit *placement* or
alignment with the model's local gradient. And monotone dose response is no
discriminator at all: a purely linear readout produces a perfectly monotone
response to graded removal of any fixed component.

So the experiment as designed licenses only: "the model's prediction depends
on the off-manifold component of the map triplet." That is the card's own
rung-1 wording ("selective use of the cross-map inconsistency residual"),
and it is a legitimate, testable claim. But the deliverable sentence — "using
violation of the central-volume identity **as a hidden confidence map** for
perfusion evidence" — asserts a functional role: that the model *discounts
perfusion evidence* where the residual is high. Nothing in the projection
contrast measures discounting. The deliverable sentence exceeds what the
design identifies, which is exactly the wrong-keystone/overclaim family this
pipeline has killed eleven candidates for.

**The repair, which preserves the question rather than changing it:** the
confidence-map claim is a claim about *interaction*, so test the interaction
directly. Add a confirmatory arm: at high-X and low-X locations matched on
perfusion severity (CBF, Tmax strata) and lesion distance, apply an identical,
small, fixed perfusion-evidence edit (e.g., a calibrated CBF-deficit
deepening) and compare the model's response magnitude. "Hidden confidence
map" predicts attenuated response at high-X sites; the anisotropy artifact of
§1 makes no such prediction. The projection/tangent contrast then demotes to
a supporting arm establishing residual dependence, and the interaction arm
carries the deliverable sentence. The question asked — is the model using
identity violation as a confidence signal for perfusion evidence? — is
unchanged; what changes is that the design now measures the "for perfusion
evidence" clause instead of assuming it. This stays revision-in-place under
the 2026-08-10 claim-identity rule: same deliverable sentence, strengthened
design.

## 2. Elevated triviality risk — flagged by the card's own citation

The card cites Konstas et al. (PMID 19270105) as supplying the invariant, and
its own `novelty_neighbors` relation text concedes the sting: the source
"explains that MTT is **calculated from** CBV/CBF." In common deconvolution
implementations CBV is the area and CBF the peak height of the flow-scaled
residue function, and MTT is then *defined* as CBV/CBF (area over height). If
icobrain cva 1.5.0 does this and stores the quotient, the residual X is
identically zero up to quantization, clipping, and any post-hoc per-map
smoothing — the candidate dies at Stage 0, as the card itself anticipates.
My search found no public documentation of icobrain cva's MTT derivation
(icometrix does not appear in the deconvolution-implementation literature I
could locate), so this cannot be resolved at critique time. Alternative
implementations (first moment of the residue function) would make MTT
genuinely independent, and post-processing applied per-map can break even a
by-construction identity; the keystone screen's UNVERIFIABLE verdict is
correct.

Not fatal — the card contains the kill gate — but the revision must sharpen
Stage 0 in two ways: (a) an **explicit algebraic-dependence test** (regress
stored MTT on stored CBV/CBF per case; near-perfect fit up to quantization =
kill), rather than only the rank-stability check; (b) a pre-committed ruling
that a residual dominated by quantization/rounding structure counts as
"collapses to a constant" and kills. Without (a), a residual that is 99%
rounding noise could pass a rank-correlation threshold across two masks and
launch a doomed intervention study.

## 3. A confound the card does not list: edit-induced cross-map incoherence

The projection edits CBF/CBV/MTT but leaves Tmax (and any other input
channels the surrogate sees, e.g. NCCT/CTA) untouched. MTT and Tmax are
strongly physiologically and algorithmically coupled. A residual-removal edit
that shifts MTT therefore *introduces* a new inconsistency — between edited
MTT and unedited Tmax — that did not exist in training data. A model
responding to that novel MTT–Tmax mismatch would masquerade as responding to
central-volume-residual removal. Tangent shams also perturb MTT, but there is
no reason their MTT–Tmax decorrelation is matched to the projection arm's.
The `alternative_explanations` list covers support/clipping artifacts and
generic edit sensitivity, but not this. Revision options, any one of which
suffices: report and match MTT–Tmax coherence disruption across arms; add a
sensitivity arm with a Tmax-free surrogate; or include Tmax in the projection
with its own consistency treatment. This must be addressed before the
projection arm is interpretable even at rung 1.

## 4. "The final-infarct model" is actually a Dice-0.20 2D surrogate

Verified: the ISLES'24 winning entry (Kurtlab, arXiv 2505.18424) is a
preprocessing pipeline plus 3D residual-encoder nnU-Net reaching **mean test
Dice 28.5 ± 21.27**, and neither the paper nor my search located a released
checkpoint or repository. So the card's fallback — a self-trained compact 2D
U-Net gated at held-out median Dice ≥ 0.20 — is not a fallback; it is the
plan. Two consequences:

- The deliverable sentence's definite article ("**The** final-infarct model")
  overstates. All rung-1 evidence will concern one weak self-trained
  surrogate. The winner's 28.5 Dice makes 0.20 for a compact 2D model a
  defensible performance floor, but the card and pitch must say "a
  representative multichannel surrogate," with model-family generalization
  explicitly deferred to rung 2 (the rung text already does this; the
  deliverable sentence and pitch do not).
- **Missing manipulation check:** a surrogate that has learned to ignore CBV
  or MTT (plausible — Tmax and CBF dominate clinical infarct prediction)
  cannot use their mutual residual, and every null becomes uninterpretable
  regardless of the sham positive control. The revision must add a frozen
  gate: per-channel occlusion/permutation reliance on the surrogate, with
  demonstrable reliance on at least two of the three identity-linked maps
  required before the intervention study proceeds.

## 5. Prior-work audit: citations check out; the gap survives a limited search

- **Kudo et al.** — verified exact: Radiology 2010;254(1):200-209, DOI
  10.1148/radiol.254082000, PMID 20032153; five commercial packages on
  identical acute-stroke source data produce significantly different maps.
  Supports the motivation (map values are implementation-contingent), though
  note it evidences *across-software* disagreement, not within-triplet
  identity violation (see §8).
- **ISP-Net** — verified exact: Comput Methods Programs Biomed 2022;215:106630;
  early fusion of native CTP, CBF, CBV, MTT, Tmax. The stated relation is
  accurate.
- **Konstas et al. Part 1** — verified (AJNR 2009, PMID 19270105); see §2 for
  the double edge.
- Adversarial search for the specific claim: the physics-informed-NN
  perfusion literature (e.g., arXiv 2011.12844, myocardial perfusion PINNs;
  arXiv 2410.19759, PINN CBF in infants) uses conservation laws as *fitting
  constraints during quantification* — the inverse direction. I found no work
  auditing whether a trained infarct-prediction model reads cross-map
  physical inconsistency as an uncertainty signal, and no ISLES'24
  map-consistency audit. "I did not find it" is not proof; novelty_confidence
  3 with NO_DUPLICATE_FOUND_LIMITED_SEARCH remains the honest ceiling, and
  the hard cap holds while the keystone is uninspected.

No prior-work rejection.

## 6. Data access and compute honesty

The keystone screen established the release is a single **99 GB `train.7z`**
archive (Zenodo record 16748089, files[0], 99,014,629,647 bytes). The card's
"modest download path" and data_readiness 4 ("with a modest download path")
are optimistic: the 10-case Stage 0 kill gate requires fetching and unpacking
the full archive first; on a Colab-class environment this is the dominant
cost and failure point of the whole card, ahead of the 10 GPU-hours. Not a
kill — the data are public and licensed for this — but the feasibility memo
must name the 99 GB up front and state where it will live. Data readiness is
better scored 3 than 4.

## 7. Endpoint discipline

Two gaps, both feasibility-memo-fixable:

- "Selective" and "residual-over-sham contrast" carry no frozen statistic or
  margin. This program has already been burned by threshold language left to
  interpretation time (idea-004, amended pin 2). The revision must commit
  that the memo freezes the exact paired statistic, the sham-comparison
  contrast, and pass/fail semantics before any model sees an edited map.
- Fitting k_case on "normal contralateral voxels" and reporting X inside the
  Tmax>6 s territory requires knowing the affected side per case. Say where
  laterality comes from (occlusion-site metadata vs the ground-truth mask).
  Using GT laterality is acceptable for an audit but must be declared; it is
  a mild endpoint dependence, not leakage, since no model training touches X.

## 8. Plain-pitch fidelity (opposite-family check) — two named defects

1. **"…yet stroke software can produce maps that locally disagree with it"**
   is stated as established fact. The card's verified support (Kudo) shows
   different *software packages* disagree with each other; local violation of
   the identity *within one package's released triplet* is precisely the
   unverified keystone (status NOT_INSPECTED, screen verdict UNVERIFIABLE,
   and §2's triviality risk runs the other way). The pitch asserts as
   background what the experiment's first gate exists to find out. It must
   hedge: "may locally disagree."
2. **"whether the prediction model notices"** mirrors the deliverable
   sentence's overclaim (§4): the tested object is a self-trained surrogate,
   not "the" model a reader will assume (a challenge winner or clinical
   tool). One added word fixes it ("a stroke prediction model trained on
   this data").

The remaining hedges survive translation ("asks whether," "could fail"), and
the software-change consequence is appropriately conditional.

## 9. What survives, and the revision bill

The kernel is genuinely good: an annotator-free, within-case, deterministic
invariant; a selectively removable signal; within-case interventions that
hold center/protocol/anatomy fixed; a designed sham positive control that
makes nulls meaningful; honest prohibited-conclusions. It is a real
differentiation from the dead site-signature ideas (037, 001-c08), because
the residual is computable and manipulable inside every case. The revision
must deliver, and only:

1. Interaction arm (matched-severity fixed perfusion-evidence edit at high-X
   vs low-X sites) as the carrier of the confidence-map deliverable; the
   projection/tangent contrast demoted to supporting evidence of residual
   dependence (§1).
2. Stage 0 algebraic-dependence test (stored MTT vs stored CBV/CBF) with a
   pre-committed quantization-only kill ruling (§2).
3. An MTT–Tmax (and other untouched channels) coherence treatment for the
   edit arms (§3).
4. Surrogate channel-reliance gate; "a representative surrogate" wording in
   card and pitch (§4).
5. 99 GB acquisition stated in feasibility; data_readiness 4 → 3 (§6).
6. Frozen selectivity statistic/margin commitment and declared laterality
   source (§7).
7. The two pitch hedges (§8).

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does a multichannel ISLES'24 infarct
surrogate's prediction depend on the off-manifold (identity-violating)
component of the perfusion triplet, and does that component modulate its
response to matched perfusion-evidence edits?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is idea 039 with the §1
interaction arm; splitting it would duplicate the card.
IS IT ACTUALLY WORTH DOING? YES — and its Stage 0 has a guaranteed floor:
whether ISLES'24's released MTT is algebraically dependent on CBF/CBV (three
channels, two degrees of freedom) is a publishable dataset-composition fact
for everyone fusing these maps, whichever way it comes out.
```

Note on the floor: the Stage 0 dependence audit is deliberately *not* spun
off as a separate candidate — it is this card's mandatory first gate, it
costs half a day plus the download, and registering it separately would spend
pipeline stages twice on the same measurement. If Stage 0 kills the
intervention (residual trivial), the dependence finding should then be
registered as a dataset-quality result under the charter's
benchmarking/dataset-quality lane rather than dying silently with the card.


===== ideas/039/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed projection-versus-tangent contrast does not identify the original claim that a surrogate uses central-volume-law violation as a confidence map for perfusion evidence.

**Argument:** Removing the normal component of the (CBF, CBV, MTT) triplet and comparing it with equal-L2 tangent shams measures directional sensitivity of a nonlinear multichannel predictor. A residual-blind model that responds directly to MTT, or to the particular spatial locations where the normal residual is concentrated, can show a larger and monotone response to residual removal while never discounting perfusion evidence according to inconsistency. Energy matching does not match edit placement or alignment with the model gradient. Thus even a fully positive result supports only “prediction depends on the off-manifold component,” not the deliverable sentence’s stronger functional claim that violation acts as a hidden confidence map. Narrowing the deliverable to residual dependence would change the original question and therefore require a successor candidate under the claim-identity rule.

**What would change my mind:** Add a preregistered interaction arm that applies the same small calibrated perfusion-evidence edit at high-residual and low-residual locations matched on baseline CBF/Tmax severity, lesion distance, anatomy, and edit support, and show that response to that identical evidence edit is selectively attenuated at high-residual locations, with spatially matched null shams and an explicit test ruling out direct MTT-value sensitivity.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The projection-versus-tangent contrast only shows that the
prediction depends on the off-manifold component of the map triplet. Any
smooth multichannel predictor is anisotropic, and the normal component has a
distinctive spatial placement, so a residual-blind model reading raw MTT (or
reading the locations where the residual happens to concentrate) can pass the
projection gates, the dose-response gate, and the equal-energy sham gate
without ever discounting perfusion evidence by inconsistency. The deliverable
sentence — violation used *as a hidden confidence map for perfusion evidence*
— asserts an interaction the design never measures.

**Response:** AMEND

**Argument:** The objection is technically correct and I will not contest it:
energy matching equalizes edit size, not edit placement or gradient
alignment, and monotone dose response is produced by any linear readout of a
fixed component. The projection contrast, standing alone, identifies
residual *dependence*, not a confidence-map *role*. The amendment adopts the
critic's interaction arm as the confirmatory carrier of the deliverable
sentence, with these specifics:

1. **Interaction arm (new, primary).** Within each held-out case, select
   voxel-site pairs (high-X, low-X) matched on baseline CBF and Tmax strata,
   distance to the Tmax>6 s boundary and to the eroded support edge, and
   tissue laterality. At both sites apply the identical small, calibrated
   perfusion-evidence edit (a fixed CBF-deficit deepening at frozen dose,
   inside a fixed-radius patch). Primary readout: paired difference in
   prediction response between high-X and low-X sites. The confidence-map
   hypothesis predicts selective attenuation at high-X sites; the anisotropy
   artifact the critic names makes no such prediction, because the edit —
   not the residual — is what varies, and it is identical at both sites.
2. **Direct-value-sensitivity discriminator (the critic's explicit test).**
   High-X and low-X sites matched only on (CBF, Tmax) can still differ
   systematically in raw MTT or CBV values, so a model reading MTT values
   directly could mimic the interaction. Therefore two preregistered
   matching strata: (a) sites additionally matched on MTT (residual
   difference then carried by CBV), and (b) sites additionally matched on
   CBV (residual difference carried by MTT). The confidence-map hypothesis
   predicts attenuation in **both** strata, since X is the same construct in
   each; direct value-reading of any single channel predicts an interaction
   in at most one. Concordance across strata is a frozen confirmatory
   requirement, not a post-hoc check.
3. **Null shams.** The same matched site pairs receive a zero-dose sham pass
   and an off-site same-dose sham, establishing the paired noise floor and
   the locality of the response before the interaction statistic is read.
4. **Demotion of the projection arm.** The projection/tangent contrast
   becomes a supporting gate — it establishes that the residual is seen at
   all (a model with zero off-manifold sensitivity cannot be using X as
   anything), and remains a required precondition for interpreting the
   interaction arm. It no longer carries the deliverable sentence.

**Identity check:** The one-sentence question — is the model using voxelwise
violation of the central-volume identity as a hidden confidence map for the
released perfusion estimates? — is unchanged. The amendment strengthens the
design so that the "for perfusion evidence" clause is measured (response to
an identical evidence edit, stratified by X) instead of presumed from
directional sensitivity. Same claim, stronger instrument; this is
revision-in-place under the 2026-08-10 rule, not a successor.

**What is lost, stated plainly:** First, the original card's
use-versus-association section was insufficient as confirmatory evidence and
is hereby admitted to have overclaimed; a positive projection result alone
can no longer support the deliverable sentence. Second, the interaction arm
has a real feasibility cost: it requires an inventory of matched
(high-X, low-X) site pairs satisfying the double-matching strata within the
20 test cases, and that inventory depends on the empirical joint
distribution of X with CBF/Tmax/MTT/CBV, which nobody has seen yet. Stage 0
therefore gains a frozen count requirement — a minimum number of qualifying
matched pairs per stratum (to be fixed in the feasibility memo before any
model sees an edit) — and an insufficient inventory kills the confirmatory
arm honestly rather than degrading the matching. Third, if the two strata
disagree (attenuation under MTT-matching but not CBV-matching, or vice
versa), the confirmatory claim fails and the result demotes to rung-1
residual dependence with a channel-specific caveat; that outcome is
preregistered as a negative for the deliverable sentence, not as a partial
success.

**Status:** OPEN


===== ideas/039/idea_card.json =====
{
  "id": "isles24-scout-005-c06",
  "parent_ids": [],
  "track": "wide",
  "entry_point": 2,
  "title": "Does the model trust tissue that obeys the flow equation?",
  "question": "Is an ISLES'24 final-infarct model using voxelwise violation of the central-volume identity CBV = CBF x MTT as a hidden confidence map for the released perfusion estimates?",
  "rung": "Target rung 1: selective use of the cross-map inconsistency residual; rung 2 requires the response to replicate across model families and across independently regenerated perfusion maps.",
  "deliverable_sentence": "The final-infarct model is using violation of the central-volume identity as a hidden confidence map for perfusion evidence.",
  "X_measurement": "Inside brain tissue, fit the unit/scale constant on normal contralateral voxels and compute X = |log(CBV) - log(CBF) - log(MTT/60) - k_case|, with cerebral blood volume (CBV) in mL/100 g, cerebral blood flow (CBF) in mL/100 g/min, and mean transit time (MTT) in seconds. Report median X and connected high-X islands inside the acute Tmax>6 s territory. The formula is deterministic and annotator-free; the central-volume theorem is described in Konstas et al., AJNR 2009, PMID 19270105, and the three registered maps are in the official ISLES'24 release (Zenodo DOI 10.5281/zenodo.16731717).",
  "suspected_signal": "For an ideal indicator-dilution calculation the three maps are not independent: CBV equals CBF multiplied by MTT after unit conversion. Noise, delay sensitivity, regularization, map clipping, and implementation details can break that identity locally. A multichannel model could learn that high-residual tissue is an unreliable measurement region and discount or reinterpret its perfusion deficit, even though no explicit uncertainty map was supplied.",
  "use_vs_association": "Project each affected-region map triplet onto the nearest central-volume-consistent manifold while preserving the local CBF and Tmax ranks, then compare the prediction with equal-energy perturbations tangent to that manifold; a selective, graded response to removing only the normal residual is evidence of use rather than correlation.",
  "keystone_prerequisite": "The released CBF, CBV, and MTT maps have meaningful common support and scaling such that a stable, nontrivial central-volume residual can be computed rather than merely rediscovering zeros, support edges, or arbitrary normalization.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_residual_assumption": "The theorem is verified, and all three maps are verified as released, but the release's value units, clipping rules, and local algebraic consistency have not been inspected. Stage 0 must read headers and value distributions in 10 cases, exclude zero/support boundaries, and require residual rank correlation at least 0.8 under two defensible normal-tissue masks. If X collapses to a constant, a support mask, or a unit error, the candidate dies.",
  "rung_reached": "0; rung 1 only after measurement, manifold-projection realism, model-performance, dose-response, and tangent-sham gates.",
  "dies_like_prior": "This is adjacent to isles24-scout-001-c08 (the deconvolution algorithm may have signed the image) and idea-037 (site identity), both vulnerable to IDENTIFIABILITY_FAILURE. It differs by naming an invariant that is calculable within every case and selectively removable without swapping sites or algorithms. A positive result would establish use of cross-map inconsistency, not which vendor produced it or why it arose; that narrower claim avoids the unsupported provenance attribution.",
  "closest_prior_work": "Indicator-dilution theory fixes the algebraic relation among CBF, CBV, and MTT; commercial packages applied to identical stroke source data nevertheless produce materially different maps. Infarct networks fuse these maps, but the searched primary work does not test whether a network reads their internal physical inconsistency as uncertainty. No novelty claim beyond this targeted comparison is made.",
  "novelty_neighbors": [
    {
      "work": "Konstas et al., Theoretic Basis and Technical Implementations of CT Perfusion in Acute Ischemic Stroke, Part 1",
      "identifier": "PMID 19270105; AJNR 2009; official full text https://pmc.ncbi.nlm.nih.gov/articles/PMC7051780/",
      "relation": "Defines the central-volume theorem and explains that MTT is calculated from CBV/CBF; supplies the physical invariant but does not audit model use of its residual."
    },
    {
      "work": "Kudo et al., Differences in CT Perfusion Maps Generated by Different Commercial Software",
      "identifier": "DOI 10.1148/radiol.254082000; PMID 20032153",
      "relation": "Shows that identical acute-stroke source data produce significantly different maps across software, motivating a hidden map-quality cue; it does not study learned final-infarct models or the within-triplet residual."
    },
    {
      "work": "Liu et al., ISP-Net: Fusing features to predict ischemic stroke infarct core on CT perfusion maps",
      "identifier": "DOI 10.1016/j.cmpb.2022.106630",
      "relation": "A primary example of a network fusing native perfusion, CBF, CBV, MTT, and Tmax; it reports prediction performance, not a conservation-law intervention."
    }
  ],
  "novelty_delta": "The proposed experiment is the first located test that removes only the voxelwise violation of a known perfusion identity and asks whether a final-infarct model changes its forecast while physiology-preserving tangent shams do not.",
  "why_not_done": "BLIND_SPOT: perfusion papers treat disagreement as a software-validation problem and model papers treat registered maps as independent input channels, leaving the algebraic residual between those channels uninterrogated as a learned uncertainty signal.",
  "existing_assets": "Official registered CBF, CBV, MTT, and Tmax maps for 149 public training cases; raw CTP for later regeneration; final masks; official metrics; standard projection and paired-output arithmetic; a winner-style surrogate can be trained if no checkpoint is obtainable.",
  "smallest_decisive_experiment": "Stage 0 on 10 cases computes support, units, X stability, and whether X contains more than border/zero artifacts. Freeze a center-stratified split and one compact 2D multichannel U-Net; require held-out median Dice at least 0.20 and lesion-wise F1 above a frozen all-zero baseline. On 20 untouched cases run 25/50/75/100% residual removal, tangent shams matched in per-channel L2 energy, and a support-edge sham. Primary readout: paired change in predicted lesion probability within Tmax>6 s tissue, with monotone residual-dose response and residual-over-sham contrast. Compute envelope: one Colab GPU session, at most 10 GPU-hours, using 2D patches and the public registered maps; no new annotation.",
  "standing_confounds_addressed": "Within-case projections hold center, scanner, protocol, positioning, anatomy, treatment, and lesion prevalence fixed. Excluding zeros and eroding support edges prevents X from becoming a coverage mask. Tangent shams test generic sensitivity to map edits; fixed CBF/Tmax ranks protect the main perfusion ordering; two projection metrics test dependence on the chosen geometry. The experiment still cannot identify the source of inconsistency or prove calibrated uncertainty, so those conclusions are prohibited.",
  "alternative_explanations": [
    "The model responds to any violation-correction edit; equal-energy tangent shams and a monotone residual-specific contrast test this.",
    "X is only a map-support or clipping detector; eroded common support, clipped-voxel exclusion, and a support-edge sham test this.",
    "Projection moves cases off the training distribution; nearest-neighbor feature distance and two small-dose arms gate the confirmatory result but cannot prove perfect realism."
  ],
  "anticipated_negative": "Decisive if X is stable, the model passes its frozen performance gate, the small-dose edits remain in distribution, and shams produce detectable generic sensitivity; otherwise the null is sensitivity-limited.",
  "cross_domain": {
    "borrowed_construct": "Conservation-law residuals from process control: redundant sensors linked by a physical balance equation provide a residual that detects unreliable measurements without an external fault label.",
    "measurement_it_implies": "The absolute log residual of CBV = CBF x MTT and a projection that removes that residual while retaining the physiological coordinates along the constraint manifold.",
    "what_changes_if_dropped": "Without the process-control construct this becomes generic channel ablation, which cannot distinguish use of perfusion physiology from use of cross-map inconsistency."
  },
  "remaining_legwork": "Half a day for the 10-case algebra/support kill gate; one Colab session for the surrogate and 20-case intervention; a later raw-CTP regeneration study is outside this card.",
  "design_template": "counterfactual-synthesis",
  "entry_point_2_requirements": "Measurement: central-volume residual X. Confused artifacts: common-support edges, zeros, clipping, and generic multichannel perturbation; erosion, clipped-voxel exclusion, tangent shams, and dose response separate them.",
  "scores": {
    "clarity": {
      "value": 5,
      "why": "One physical identity, one residual, and a selective projection with explicit shams."
    },
    "identifiability": {
      "value": 4,
      "why": "The intervention isolates residual use, although it cannot identify the residual's technical cause or prove uncertainty calibration."
    },
    "medical_relevance": {
      "value": 4,
      "why": "A model silently discounting physically inconsistent perfusion could determine where it trusts the acute scan and how it transports across software."
    },
    "interest": {
      "value": 5,
      "why": "A stroke model acting as its own physics-based quality controller is surprising and directly actionable."
    },
    "prior_legwork": {
      "value": 4,
      "why": "The invariant, map inputs, software-variability evidence, and model family all exist."
    },
    "feasibility": {
      "value": 3,
      "why": "Capped because the released maps' units and residual stability have not been inspected."
    },
    "data_readiness": {
      "value": 4,
      "why": "All maps and outcomes are public and registered, with a modest download path."
    },
    "evaluation_readiness": {
      "value": 4,
      "why": "Paired probability response, dose response, shams, and official segmentation metrics are ready."
    },
    "negative_result_value": {
      "value": 4,
      "why": "After the algebra and model gates, a selective null rules out this specific hidden-confidence mechanism."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Three close primary neighbors were searched, but no systematic review was performed and the keystone remains uninspected."
    },
    "regret": {
      "value": 5,
      "why": "The required redundant maps are already in the benchmark, making this a cheap obvious-in-hindsight audit."
    }
  },
  "priority_score": 3.95,
  "unverified_claims": [
    "the released map units permit a stable central-volume residual",
    "the residual is not dominated by support or clipping",
    "a compact surrogate reaches the frozen performance gate in one session",
    "manifold projections remain in distribution",
    "the precise novelty gap beyond the targeted search"
  ],
  "plain_pitch": "Blood flow, blood volume, and transit time are tied by a simple physical equation, yet stroke software can produce maps that locally disagree with it. This study asks whether the prediction model notices those disagreements and quietly treats them as a warning that a region's blood-flow estimate is unreliable. If correcting only the disagreement changes the forecast while equally sized, physics-preserving edits do not, the model is using an accidental quality-control signal that could fail when the hospital changes software.",
  "charter": "isles24"
}


===== ideas/039/keystone_screen.md =====
# Keystone screen

Screened 2026-08-19 against the official ISLES'24 dataset record and the
primary dataset paper.

## Keystone as stated

> The released CBF, CBV, and MTT maps have meaningful common support and
> scaling such that a stable, nontrivial central-volume residual can be
> computed rather than merely rediscovering zeros, support edges, or arbitrary
> normalization.

This is a compound empirical prerequisite. It requires more than the three
maps being present and spatially registered: their stored voxel values must
have documented or inspectable scale, support, background, and clipping
semantics, and the proposed residual must be nontrivial away from excluded
artifacts.

## What I inspected

### Official dataset release

The Zenodo record confirms that the three maps are released alongside Tmax:

> “Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT
> perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

Source: official ISLES'24 Zenodo record 16748089, **Description**, admission
imaging bullet: https://zenodo.org/records/16748089 (concept DOI
10.5281/zenodo.16731717).

The same record says what “derivatives” means and lists all three maps in the
same target space:

> “'Derivatives' include all modalities linearly co-registered to the NCCT
> space.”

Source: official ISLES'24 Zenodo record 16748089, **Data structure**, followed
by the derivative filenames
`space-ncct_mtt.nii.gz`, `space-ncct_cbf.nii.gz`, and
`space-ncct_cbv.nii.gz`: https://zenodo.org/records/16748089.

This verifies co-location in a common coordinate space. It does **not** verify
meaningful common numeric support or scaling.

The release does not expose per-map sidecars or sample maps as separately
inspectable files. Its file inventory consists of one archive:

> “train.7z”

Source: official Zenodo Records API, record 16748089, `files[0].key` (size
99,014,629,647 bytes): https://zenodo.org/api/records/16748089.

### Primary dataset paper

The paper identifies a common producing implementation:

> “perfusion maps (cerebral blood flow, cerebral blood volume, mean transit
> time, and time-to-maximum) were derived using the clinical, U.S. Food and
> Drug Administration–cleared software icobrain cva (version 1.5.0,
> icometrix).”

Source: Riedel et al., *Radiology: Artificial Intelligence* 2026,
DOI 10.1148/ryai.250603, **Materials and Methods — Image Acquisition**, PDF
p. 3: https://pubs.rsna.org/doi/pdf/10.1148/ryai.250603.

It also confirms the registration operation:

> “CTA, CT perfusion (including derived perfusion maps), and DWI and/or
> apparent diffusion coefficient scans were linearly co-registered to the
> noncontrast CT space using rigid transformations for CT and affine
> transformations for MRI”

Source: same paper and section, PDF p. 3:
https://pubs.rsna.org/doi/pdf/10.1148/ryai.250603.

Neither the inspected release description nor the paper states the stored
units, scale factors, clipping bounds, background/invalid-voxel convention,
or whether icobrain cva stores MTT independently or as an algebraic derivative
of the stored CBF and CBV maps. No quoted primary-source evidence therefore
establishes that the proposed log residual is stable, spatially nontrivial, or
separable from support and clipping artifacts.

## Residual-assumption check (mandatory wrong-keystone question)

If the card only verified the nearest checkable thing, what is it still
assuming? The nearest checkable fact is that CBF, CBV, and MTT are all present,
were produced by one named software version, and have NCCT-space derivatives.
The load-bearing fact is different: actual released voxel arrays must overlap
on valid tissue and retain commensurate quantitative scales while exhibiting
a residual that is neither forced to zero by construction nor dominated by
invalid/background/clipped values.

That load-bearing fact remains unverified. It is not demonstrably false, so a
KILL would overstate the evidence. Resolving it requires inspecting headers and
voxel distributions from the released archive (including the proposed
10-case, two-mask stability check); publication-level modality and registration
statements cannot substitute for that measurement.

```json
{"verdict": "UNVERIFIABLE", "evidence": "'Derivatives' include all modalities linearly co-registered to the NCCT space.", "source": "https://zenodo.org/records/16748089, Data structure", "note": "Common coordinates are verified, but the released maps' units, valid support, clipping/background semantics, and nontrivial residual require direct voxel inspection of the monolithic archive."}
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

**Position:** The proposed projection-versus-tangent contrast does not identify the original claim that a surrogate uses central-volume-law violation as a confidence map for perfusion evidence.

**Argument:** Removing the normal component of the (CBF, CBV, MTT) triplet and comparing it with equal-L2 tangent shams measures directional sensitivity of a nonlinear multichannel predictor. A residual-blind model that responds directly to MTT, or to the particular spatial locations where the normal residual is concentrated, can show a larger and monotone response to residual removal while never discounting perfusion evidence according to inconsistency. Energy matching does not match edit placement or alignment with the model gradient. Thus even a fully positive result supports only “prediction depends on the off-manifold component,” not the deliverable sentence’s stronger functional claim that violation acts as a hidden confidence map. Narrowing the deliverable to residual dependence would change the original question and therefore require a successor candidate under the claim-identity rule.

**What would change my mind:** Add a preregistered interaction arm that applies the same small calibrated perfusion-evidence edit at high-residual and low-residual locations matched on baseline CBF/Tmax severity, lesion distance, anatomy, and edit support, and show that response to that identical evidence edit is selectively attenuated at high-residual locations, with spatially matched null shams and an explicit test ruling out direct MTT-value sensitivity.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The projection-versus-tangent contrast only shows that the
prediction depends on the off-manifold component of the map triplet. Any
smooth multichannel predictor is anisotropic, and the normal component has a
distinctive spatial placement, so a residual-blind model reading raw MTT (or
reading the locations where the residual happens to concentrate) can pass the
projection gates, the dose-response gate, and the equal-energy sham gate
without ever discounting perfusion evidence by inconsistency. The deliverable
sentence — violation used *as a hidden confidence map for perfusion evidence*
— asserts an interaction the design never measures.

**Response:** AMEND

**Argument:** The objection is technically correct and I will not contest it:
energy matching equalizes edit size, not edit placement or gradient
alignment, and monotone dose response is produced by any linear readout of a
fixed component. The projection contrast, standing alone, identifies
residual *dependence*, not a confidence-map *role*. The amendment adopts the
critic's interaction arm as the confirmatory carrier of the deliverable
sentence, with these specifics:

1. **Interaction arm (new, primary).** Within each held-out case, select
   voxel-site pairs (high-X, low-X) matched on baseline CBF and Tmax strata,
   distance to the Tmax>6 s boundary and to the eroded support edge, and
   tissue laterality. At both sites apply the identical small, calibrated
   perfusion-evidence edit (a fixed CBF-deficit deepening at frozen dose,
   inside a fixed-radius patch). Primary readout: paired difference in
   prediction response between high-X and low-X sites. The confidence-map
   hypothesis predicts selective attenuation at high-X sites; the anisotropy
   artifact the critic names makes no such prediction, because the edit —
   not the residual — is what varies, and it is identical at both sites.
2. **Direct-value-sensitivity discriminator (the critic's explicit test).**
   High-X and low-X sites matched only on (CBF, Tmax) can still differ
   systematically in raw MTT or CBV values, so a model reading MTT values
   directly could mimic the interaction. Therefore two preregistered
   matching strata: (a) sites additionally matched on MTT (residual
   difference then carried by CBV), and (b) sites additionally matched on
   CBV (residual difference carried by MTT). The confidence-map hypothesis
   predicts attenuation in **both** strata, since X is the same construct in
   each; direct value-reading of any single channel predicts an interaction
   in at most one. Concordance across strata is a frozen confirmatory
   requirement, not a post-hoc check.
3. **Null shams.** The same matched site pairs receive a zero-dose sham pass
   and an off-site same-dose sham, establishing the paired noise floor and
   the locality of the response before the interaction statistic is read.
4. **Demotion of the projection arm.** The projection/tangent contrast
   becomes a supporting gate — it establishes that the residual is seen at
   all (a model with zero off-manifold sensitivity cannot be using X as
   anything), and remains a required precondition for interpreting the
   interaction arm. It no longer carries the deliverable sentence.

**Identity check:** The one-sentence question — is the model using voxelwise
violation of the central-volume identity as a hidden confidence map for the
released perfusion estimates? — is unchanged. The amendment strengthens the
design so that the "for perfusion evidence" clause is measured (response to
an identical evidence edit, stratified by X) instead of presumed from
directional sensitivity. Same claim, stronger instrument; this is
revision-in-place under the 2026-08-10 rule, not a successor.

**What is lost, stated plainly:** First, the original card's
use-versus-association section was insufficient as confirmatory evidence and
is hereby admitted to have overclaimed; a positive projection result alone
can no longer support the deliverable sentence. Second, the interaction arm
has a real feasibility cost: it requires an inventory of matched
(high-X, low-X) site pairs satisfying the double-matching strata within the
20 test cases, and that inventory depends on the empirical joint
distribution of X with CBF/Tmax/MTT/CBV, which nobody has seen yet. Stage 0
therefore gains a frozen count requirement — a minimum number of qualifying
matched pairs per stratum (to be fixed in the feasibility memo before any
model sees an edit) — and an insufficient inventory kills the confirmatory
arm honestly rather than degrading the matching. Third, if the two strata
disagree (attenuation under MTT-matching but not CBV-matching, or vice
versa), the confirmatory claim fails and the result demotes to rung-1
residual dependence with a channel-specific caveat; that outcome is
preregistered as a negative for the deliverable sentence, not as a partial
success.

**Status:** OPEN

