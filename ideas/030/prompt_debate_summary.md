You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/030
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


===== evidence/ledger_digest_isles24.md =====
# Ledger digest -- charter: isles24 (auto-generated; scores are scoped to this charter only)

45 tracked ideas in this charter. Latest state per idea; full history in ledger.jsonl.

Work under other charters: evidence/cross_charter_index.md (facts, no scores).

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **IDENTIFIABILITY_FAILURE** x3: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_ACCESS** x2: Required data, checkpoints, or mappings are not obtainable in practice.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **isles24-scout-003-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.6, audited 2026-08-18] -- Did preprocessing teach the winner to read the disappearing insular ribbon?
- **isles24-scout-004-c07** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.6, audited 2026-08-18] -- The edge of the map: the benchmark scores terra incognita
- **isles24-scout-003-c08** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.5, audited 2026-08-18] -- The skull is a fixed-volume pressure vessel
- **isles24-scout-004-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.5, audited 2026-08-18] -- Does the model bring a vascular map to the scan?
- **isles24-scout-004-c06** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.5, audited 2026-08-18] -- The scan remembers which hospital took it
- **isles24-scout-003-c07** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.5, audited 2026-08-18] -- Does the model price the last mile of blood delivery?
- **isles24-scout-002-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.4, audited 2026-08-16] -- Two tissues, two death thresholds
- **isles24-scout-004-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.1, audited 2026-08-18] -- The heart's signature in the head scan
- **isles24-scout-004-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.3, audited 2026-08-18] -- The brain's odometer: calcification as the model's age gauge
- **isles24-scout-002-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.2, audited 2026-08-16] -- The clot that lets contrast through
- ... and 10 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- regional-substitution: 8
- counterfactual-synthesis: 8
- representation-erasure: 4
- cross-model-disagreement: 2
- conditional-observational: 2
- natural-paired: 1
- other:remote-perturbation: 1
- other:graph-edge-intervention: 1
- regional-removal: 1
- model-output-perturbation: 1
- other:temporal-reparameterization: 1
- other:noise-residual-transplant: 1
- other:label-geometry-audit: 1

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
- **idea-030** [SHORTLISTED/CRITIQUED/wide] -- The ground truth was drawn on a swollen brain
- **idea-031** [SHORTLISTED/SCOUTED/baseline] -- The vascular detour the segmentation model can see
- **idea-032** [SHORTLISTED/SCOUTED/baseline] -- The arterial network's spare route
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
- **isles24-scout-003-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Did preprocessing teach the winner to read the disappearing insular ribbon?
- **isles24-scout-003-c02** [SCOUT_ONLY/SCOUTED/baseline] -- How much artery did the clot occupy?
- **isles24-scout-003-c03** [SHORTLISTED/SCOUTED/baseline] -- The arterial network's spare route
- **isles24-scout-003-c04** [SHORTLISTED/SCOUTED/baseline] -- The blood's grayscale oxygen gauge
- **isles24-scout-003-c05** [SHORTLISTED/SCOUTED/baseline] -- When vanished sulci mean rescue, not death
- **isles24-scout-003-c06** [SCOUT_ONLY/SCOUTED/wide] -- The bolus spreads like dye in a river
- **isles24-scout-003-c07** [SCOUT_ONLY/SCOUTED/wide] -- Does the model price the last mile of blood delivery?
- **isles24-scout-003-c08** [SCOUT_ONLY/SCOUTED/wide] -- The skull is a fixed-volume pressure vessel
- **isles24-scout-004-c01** [SHORTLISTED/SCOUTED/baseline] -- The ground truth remembers the algorithm that drafted it
- **isles24-scout-004-c02** [SCOUT_ONLY/SCOUTED/baseline] -- Does the model bring a vascular map to the scan?
- **isles24-scout-004-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The heart's signature in the head scan
- **isles24-scout-004-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The model may be watching the patient's eyes
- **isles24-scout-004-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The brain's odometer: calcification as the model's age gauge
- **isles24-scout-004-c06** [SCOUT_ONLY/SCOUTED/wide] -- The scan remembers which hospital took it
- **isles24-scout-004-c07** [SCOUT_ONLY/SCOUTED/wide] -- The edge of the map: the benchmark scores terra incognita
- **isles24-scout-004-c08** [SHORTLISTED/SCOUTED/wide] -- The ground truth was drawn on a swollen brain


===== evidence/portfolio_brief.md =====
# Portfolio brief (auto-generated; run `python scout.py brief`)

Actionable ideas with debate verdicts. A revival/recombination
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



===== evidence/librarian_proposals.md =====


===== ideas/030/README.md =====
# Idea 030: The ground truth was drawn on a swollen brain

Selected from scouting cycle isles24-004, candidate 8.


===== ideas/030/critique.md =====
FATAL OBJECTION: The proposed stage-2 correlation cannot identify that a model learned affine-transfer error rather than ordinary lesion size/location priors, output smoothing, or acute predictors of severe infarction.
EVIDENCE: `ideas/030/idea_card.json` (`use_vs_association`, `smallest_decisive_experiment`); the proposed DeepISLES control consumes follow-up DWI/ADC in its own space and is not a matched acute final-infarct predictor.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION

# Adversarial critique

## Bottom line

The card contains a worthwhile, unusually concrete **dataset audit**, but it currently overclaims a **model-use mechanism**. Acute-CSF overlap can establish that some released labels occupy a conservative set of anatomically impossible acute-space voxels. It cannot, by correlation alone, establish why a final-infarct model predicts those voxels. The stage-1 and stage-2 claims must be separated, the stage-1 negative interpretation sharply weakened, and stage 2 replaced with a controlled label-construction experiment.

## 1. The fatal identifiability defect

The proposed evidence for model inheritance is: prediction overlap with acute CSF tracks ground-truth overlap, while a DeepISLES result has near-zero overlap. That comparison does not isolate inheritance.

- DeepISLES is used to segment the realized lesion from **follow-up DWI/ADC**, whereas the audited model predicts future infarct from **acute CT-derived inputs**. It differs simultaneously in input modality, time point, task, coordinate frame, architecture, and training data. Its lower CSF overlap cannot serve as the counterfactual “same predictor, not trained on transferred labels.”
- Per-case ground-truth CSF overlap will co-vary with lesion volume, vascular territory, ventricular/sulcal proximity, and severity. Those same variables can increase a model's predicted volume and boundary smoothing. Adjusting or stratifying by lesion volume does not remove unmeasured geometry and territory differences.
- A prediction in acute CSF is evidence of an anatomically invalid output, but not evidence that the model *uses registration error*. The model does not observe the follow-up-to-acute transform. At most, it may reproduce a spatial label convention learned during supervision.

The repair is a paired training-label intervention: freeze split, inputs, architecture, augmentation, optimization budget, seeds, and postprocessing; train matched models on (A) released labels and (B) labels with only a preregistered, conservative acute-CSF intersection removed. On held-out cases, compare prediction probability specifically within the independently defined impossible set and in matched peri-lesional non-CSF control voxels. A repeatable A-minus-B difference localised to the edited set would identify the causal effect of those label voxels on model output. It would support “training on the released impossible voxels causes their reproduction,” not the broader claim that all affine-transfer displacement is learned.

## 2. Stage 1 is narrower than the card says

The “impossible-voxel” test is strong only as a **high-specificity subset audit**. Its computation adds no registration, but the tested ground truth is itself already registered; calling the endpoint simply “registration-free” risks hiding that distinction.

A positive conservative overlap is interpretable if the acute-CSF mask is valid. A near-zero overlap is not a “clean bill on geometry.” Affine error can move lesion labels from one acute tissue voxel to another without intersecting ventricles or sulci. The endpoint is therefore specific but insensitive to the general mass-effect displacement claimed in the title and deliverable. The anticipated negative-result value and score of 4 are overstated. A null says only that this CSF-intersection sentinel found little error above its detection threshold.

The secondary affine-versus-deformable comparison does not automatically close that gap. Nonlinear multimodal registration between acute NCCT and abnormal follow-up DWI is itself underidentified without landmarks or independent expert review. Brett et al. established cost-function masking for focal-lesion normalization (DOI 10.1006/nimg.2001.0845), but that does not validate ANTs SyN or SynthMorph as truth for this cross-modality, cross-time problem. The primary stroke-registration literature already treats edema and anatomical distortion as a central obstacle and reports nonlinear-versus-linear registration as a methodological question, not a solved reference standard (O'Brien et al., *Optimizing image registration and infarct definition in stroke research*, PMCID PMC5338168).

## 3. The mass-effect signature is confounded

“Overlap grows with lesion volume and midline shift” is not a unique fingerprint of affine failure.

- Larger lesions have larger surfaces, are more likely to reach sulci or ventricles, and generally induce smoother/larger model outputs.
- Midline shift is not operationally defined: the acute scan may precede substantial swelling, while follow-up shift is measured in the same deformed image that motivates the hypothesis.
- Mask interpolation, anisotropic resampling, and topology can also scale with lesion size. Calling interpolation error a thin shell does not make its aggregate fraction independent of lesion geometry.

At minimum, the revision needs a voxel-shell analysis by signed distance to the acute CSF boundary, lesion territory and surface area controls, explicit definitions and time point for mass-effect measures, and sensitivity to label interpolation conventions. These analyses can characterize alternatives; they still do not make the correlation mechanistically unique.

## 4. Endpoint validity needs a real gate

The proposed `0–15 HU` rule plus SynthSeg agreement is not yet a validated acute-CSF reference for these released, resampled NCCT derivatives. Low-attenuation infarct, partial volume, beam-hardening, chronic cavities, and preprocessing interpolation can enter the window. Erosion helps specificity but may sharply reduce sensitivity, especially in narrow sulci.

Before any benchmark claim, a blinded visual audit of a prespecified sample of candidate impossible voxels is warranted. This is fresh annotation burden and must be stated as such under the charter. A cheaper alternative is to restrict the confirmatory set to deeply eroded ventricular CSF and treat sulcal CSF and automated segmenter agreement as sensitivity analyses. That is less comprehensive but substantially more defensible.

The official challenge evaluates Dice, absolute volume difference, absolute lesion-count difference, and lesion-wise F1 (ISLES'24 official repository, https://github.com/ezequieldlrosa/isles24; dataset/challenge paper arXiv:2408.10966). The card proposes metric shifts only for Dice and absolute volume difference. That is acceptable if explicitly scoped, but it does not bound the effect on the full official ranking; clipping even tiny disconnected components could disproportionately change lesion-count and lesion-wise F1.

## 5. Prior-work and novelty calibration

The broad scientific problem is not novel. Edema distorting follow-up infarct measurement and the need for nonlinear coregistration/CSF exclusion are established. O'Brien et al. explicitly frame edema and atrophy as causes of anatomical distortion in final-infarct definition (PMCID PMC5338168). Prior final-infarct studies report attempts to correct edema with nonrigid registration and CSF exclusion, and edema-corrected infarct-volume methods have quantified clinically meaningful differences (Boers et al., PMID 29668493; DOI 10.1161/STROKEAHA.117.020072).

The defensible delta is narrower: an audit of the **released ISLES'24 NCCT-space masks**, using an acute-CSF sentinel and reporting consequences for official metrics. The search does not verify that nobody has done this; it supports only “no duplicate located in the targeted search.” The card's “blind spot” explanation and “no one has measured” rhetoric are speculation and should be removed unless a systematic novelty audit verifies them.

## 6. Data and compute realism

The inputs are obtainable under the public noncommercial release, so data access is not fatal. However, the card's `~10–15 GB download` estimate conflicts with the repository's own inspected dataset record: `evidence/datasets.csv` records a monolithic approximately 99 GB `train.7z` in the inspected Zenodo release and says derivative-only retrieval is unverified. The full public cohort is 149 cases in the release, with a 149-versus-150 paper discrepancy already recorded. Feasibility must budget the actual archive transfer/storage and pin a Zenodo version and checksum.

No suitable frozen acute final-infarct checkpoint is identified. “The shared audit model materializes” is an acknowledged dependency, not an asset. The low-hanging stage-1 audit needs no checkpoint and, if restricted to ventricular CSF, likely no GPU. A causal stage-2 repair probably requires matched training runs rather than inference only, so the stated five-GPU-hour envelope is unsupported.

## 7. Relevance and negative results

A positive stage-1 result matters: it would quantify a concrete failure in benchmark labels and show its effect on evaluation. Its medical relevance is greatest if errors concentrate in severe strokes or change rankings, but neither is yet established.

A negative 30-case result is sensitivity-limited, not decisive. Stratification by lesion volume does not ensure enough cases with ventricular/sulcal adjacency or visible mass effect. The card needs a precision target for the prevalence or voxel-fraction estimate and a support gate based on the number of cases whose lesions lie near confidently segmented CSF. If that support is absent, the study cannot validate the geometry pipeline; it can only report that the chosen sentinel rarely had an opportunity to fire.

## 8. Plain-pitch fidelity

The plain pitch fails fidelity in three places.

1. “Copied ... using a simple global alignment” is faithful to the documented affine transfer, but “That would smear each answer's position” turns a plausible consequence into certainty. The technical card explicitly says the surviving halo magnitude is unverified and may be near zero after correction.
2. “Using fluid spaces as tamper-proof landmarks” overstates the unvalidated NCCT CSF measurement and suppresses partial-volume, chronic-cavity, and resampling limitations named in the card.
3. “Models ... have learned to copy the error” states the stage-2 causal conclusion more strongly than the proposed observational overlap comparison can support.

The pitch must preserve “may,” call CSF a conservative sentinel rather than tamper-proof, and describe model inheritance as a question requiring a controlled label experiment.

## 9. Easier version and existing assets

The easiest worthwhile experiment is a model-free, CPU-first ventricular-CSF sentinel audit on the released training labels:

1. Use the released NCCT and `space-ncct` lesion mask.
2. Define only deeply eroded ventricular CSF as confirmatory; visually verify a small blinded sample.
3. Report per-case impossible-voxel count/fraction with confidence intervals and opportunity-to-overlap support (lesion distance to ventricular CSF).
4. Recompute all four official metrics after removing only verified impossible components, using the already released evaluation code.
5. Treat sulcal CSF, deformable registration, edema correlations, and any model analysis as later modules.

The data, labels, and official metric code already exist. This version eliminates learned registration, GPU dependence, the unavailable checkpoint, and most of the reference-registration dispute. It does **not** answer whether a model learned the error, so under the program's claim-identity rule it should be a separate dataset-quality candidate if the current card keeps its model-use deliverable.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: How often do released ISLES'24 final-infarct masks include conservatively verified acute ventricular-CSF voxels, and how much does removing only those voxels change all four official evaluation measures?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—the audit is cheap, falsifiable, directly benchmark-relevant, and a positive result would justify the more expensive paired-label model experiment.


===== ideas/030/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed evidence cannot identify the original claim that a model uses a mass-effect displacement halo from affine registration, and the obvious paired-label repair would answer a different, narrower question.

**Argument:** Acute-CSF overlap is a high-specificity sentinel for anatomically invalid released-label voxels, but neither its association with lesion size or midline shift nor a model's tendency to reproduce it identifies affine failure caused by swelling. Lesion territory, surface area, adjacency to ventricles or sulci, output smoothing, and severity-linked acute predictors can generate the same correlations; the proposed DeepISLES comparison is not a control because it uses follow-up DWI/ADC in its native task rather than the same acute inputs and final-infarct prediction setting. A matched training experiment using released labels versus labels with conservatively verified acute-CSF intersections removed would causally test whether those supervised voxels cause model output in that set. However, even a positive result would establish only that training on impossible label voxels causes their reproduction—not that those voxels are a mass-effect displacement halo, that affine transfer rather than interpolation or another construction step created them, or that the model places its broader infarct prediction according to swelling-displaced geometry “rather than acute tissue evidence alone.” Under the program's claim-identity rule, narrowing the deliverable to the causal effect of removing verified impossible label voxels changes the question and requires a successor; the model-free benchmark audit is likewise the separate candidate already identified in critique.

**What would change my mind:** Show a controlled design that varies only the affine mass-effect displacement component while holding acute inputs, label content, training, and evaluation fixed—for example, independently validated anatomically corrected labels that undo local swelling displacement beyond merely clipping CSF, paired against the released labels—and prespecify a spatially localized prediction contrast that distinguishes that correction from lesion geometry, smoothing, and severity; otherwise register the CSF-label intervention as a successor with the narrower deliverable.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card's stage-2 evidence (prediction CSF-overlap tracking the ground truth's rate, with DeepISLES as comparator) cannot identify use of a mass-effect displacement halo; even the paired-label training repair identifies only the causal reproduction of verified impossible label voxels, which is a narrower deliverable; under the claim-identity rule that narrowing requires a successor, not an amendment.

**Response:** CONCEDE

**Argument:** The objection is correct, and I checked whether the critic's own escape design could be honestly met before conceding. It cannot.

(1) The DeepISLES comparison has no defense. It differs from the audited setting in input modality, time point, task, coordinate frame, and training data simultaneously; its low CSF overlap discriminates nothing. I have no new argument, so this leg is conceded outright.

(2) The offered repair path — train paired models on released labels versus independently validated anatomically corrected labels, varying only the swelling-displacement component — cannot be executed with obtainable assets. Correcting tissue-to-tissue displacement requires a deformable follow-up-DWI-to-acute-NCCT reference accurate enough to define "corrected," and the critique already established (O'Brien et al., PMC5338168; the limits of Brett 2001 cost-function masking) that cross-modality, cross-time lesioned-brain registration is underidentified without landmarks or independent expert review — i.e., without either solving the reference-registration research problem or taking on the fresh annotation burden of a validation read that would itself need its own validity case. Outside the acute-CSF-impossible set there is no sign convention: when models A and B disagree in a region where the two transforms disagree, nothing determines which one is reproducing error. A paired affine-versus-deformable training contrast therefore identifies "predictions follow the label-transfer method," not "the model uses the halo." The physical-impossibility criterion — the card's entire identifiability engine, and the stated reason its identifiability score was 4 — reaches only the CSF-intersecting subset of the halo. The moment the claim extends to the halo's tissue-to-tissue majority, the design re-enters exactly the "which registration is truth" dispute the card advertised sidestepping.

(3) What survives is the causal core the critic named: paired training on released labels versus labels with only the conservatively verified acute-CSF intersection removed, read out on held-out prediction probability inside the independently defined impossible set versus matched control voxels. Its positive deliverable is "training on the released anatomically impossible voxels causes their reproduction." That is not the card's deliverable sentence ("using the swelling-displaced lesion geometry ... rather than acute tissue evidence alone"): the mass-effect attribution drops from an identified mechanism to a dataset-level observational characterization, and "rather than acute tissue evidence alone" is unsupported outside the sentinel subset. Under the claim-identity rule (decision of 2026-08-10, idea 015), a changed deliverable sentence is a successor, not a revision in place. Defending the original across further rounds would waste the loop.

**Spin-off:** Two successors, both with parent idea-030 (isles24-scout-004-c08), to re-enter through the normal pipeline:
S1 — model-free benchmark audit (already named in critique §9): how often do released ISLES'24 final-infarct masks include conservatively verified acute ventricular-CSF voxels, and how much does removing only those voxels change all four official evaluation measures? The stage-1 mass-effect correlation signature survives inside S1 as characterization of the impossible voxels, explicitly not as unique mechanism proof.
S2 — paired-label causal experiment (the critic's identified repair, as its own claim): matched training on released versus impossible-voxel-clipped labels, localized readout in the verified impossible set; conditional on S1 finding non-trivial prevalence, and inheriting S1's verified voxel set.

What is lost: the mechanistic headline that a model reads swelling-displaced geometry. What is kept: a cheap falsifiable audit of the charter dataset's released ground truth and a well-posed causal test of label-error inheritance at the only place where "error" is provable without a reference registration.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposer has accepted that the original mass-effect-halo model-use claim is not identifiable with obtainable assets and must be rejected rather than repaired in place.

**Argument:** The concession resolves the identity check: neither acute-CSF overlap nor a paired impossible-voxel-clipping experiment answers the card's original question of whether a model uses swelling-displaced lesion geometry caused by affine transfer. The argument that moved me is the explicit recognition that tissue-to-tissue displacement has no independently validated sign convention in these cross-time, cross-modality data; consequently, affine-versus-deformable label training would show dependence on a transfer method, not which geometry is erroneous. The proposer also correctly separates the only identifiable causal claim—reproduction caused by training on conservatively verified impossible label voxels—from the original deliverable and assigns it to a successor, consistent with the 2026-08-10 claim-identity rule. S1 and S2 may be worth scouting, but their merits cannot rescue idea 030 under its present identity. There is no remaining disagreement about this idea's disposition.

**What would change my mind:** Independently validated acute-space corrected lesion labels that isolate local swelling displacement beyond CSF clipping, together with a matched training contrast holding inputs, model, split, optimization, and evaluation fixed; absent that new asset, only the separately registered S1 and S2 questions are defensible.

**Status:** CONVERGED

## Round 2 — PROPOSER

**Responding to:** The critic's confirmation that the round-1 concession settles this idea's disposition: idea 030 is rejected under its present identity, and only the separately registered successors S1 and S2 remain defensible.

**Response:** CONCEDE

**Argument:** Confirmed; I hold no residual position and add nothing on the merits. The critic's reopening condition — independently validated acute-space corrected labels that isolate swelling displacement beyond CSF clipping, in a matched training contrast — names exactly the asset shown unobtainable in round 1, so it is accepted as stated. For the decision record, the converged disposition is: idea 030 REJECTED, kill code IDENTIFIABILITY_FAILURE (the mass-effect-halo model-use claim cannot be identified with obtainable assets; the only identifiable causal claim carries a different deliverable sentence and is a successor under the 2026-08-10 claim-identity rule, not a revision in place). Successors S1 (model-free ventricular-CSF sentinel audit of the released masks with the official-metric shift bound, per critique §9) and S2 (paired training on released versus impossible-voxel-clipped labels, conditional on S1 finding non-trivial prevalence) carry parent idea-030 (isles24-scout-004-c08) and re-enter through the normal scouting pipeline with no inherited queue position. One preservation note for any future S1/S2 card: the keystone screen's verbatim-verified facts — affine-only MRI-to-NCCT mask transfer, the 2–9-day follow-up window, `space-ncct` mask provenance — remain true and reusable; what died here is the claim built on them, not the verification.

**Status:** CONVERGED


===== ideas/030/idea_card.json =====
{
  "id": "isles24-scout-004-c08",
  "parent_ids": [],
  "track": "wide",
  "entry_point": 2,
  "title": "The ground truth was drawn on a swollen brain",
  "question": "Is an ISLES'24 final-infarct model using the mass-effect displacement halo that affine-only registration of peak-edema follow-up MRI baked into the ground truth -- even predicting infarct on voxels that are unambiguously CSF on the acute scan?",
  "rung": "Target rung 1: the model reproduces the label-geometry error (predicts infarct where no infarctable tissue exists in acute space, tracking the ground truth's own impossible-voxel rate). The model-free stage 1 is a dataset-quality deliverable regardless of any model.",
  "deliverable_sentence": "The final-infarct model is using the swelling-displaced lesion geometry inherited from affine-only registration of 2-9-day follow-up MRI, rather than acute tissue evidence alone, when placing its predicted infarct.",
  "X_measurement": "Two computable quantities, no annotator. (a) The registration-discrepancy field: rerun deformable registration (SynthMorph or ANTs SyN) of each case's released follow-up DWI to its acute NCCT with lesion cost-function masking (Brett 2001), and take the voxelwise displacement magnitude between the deformable map and the organizers' affine, summarized in a peri-lesional band. (b) The impossible-voxel fraction: |ground-truth mask INTERSECT acute-CSF| / |ground-truth mask|, with acute CSF from an HU window (0-15) inside the brain mask cross-checked against a contrast-agnostic segmenter (SynthSeg), eroded 1-2 voxels against partial-volume effects. Compute-today test: YES -- public registration tools plus HU arithmetic on released volumes.",
  "suspected_signal": "Follow-up MRI is acquired 2-9 days post-stroke -- squarely overlapping the documented 3-5-day peak of space-occupying edema -- when the infarcted hemisphere is swollen, ventricles are compressed, and midline structures are shifted. An affine transform cannot represent this local deformation, so masks drawn on the swollen brain land displaced in acute NCCT space: a geometric halo that grows with lesion size and mass effect, systematically placing 'infarct' on acute-space voxels (including CSF) where no infarctable tissue exists. A model trained on these labels is rewarded for reproducing the halo -- learning the registration error, not tissue fate -- and the error is largest in exactly the severe cases that matter most.",
  "use_vs_association": "Infarct growth between acute and follow-up imaging is real biology and is the legitimate prediction target; the halo is geometric error. They are separated by physical impossibility: genuine growth is confined to tissue, so predicted infarct covering voxels that are unambiguously CSF on the acute scan cannot be growth. A model whose predictions cover acute CSF at a rate tracking the ground truth's own impossible-voxel rate -- versus near-zero for a predictor not trained on these labels (the DeepISLES draft from baseline c01 runs on follow-up MRI in its own space and provides the comparison) -- is using the label geometry, not the tissue evidence.",
  "keystone_prerequisite": "Ground-truth masks were transferred to acute NCCT space via affine-only registration of follow-up MRI acquired in the edema window, so mass-effect deformation is unmodeled by construction.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "arXiv html 2408.10966v1, fetched and quoted by this stage 2026-08-18: 'all remaining images are registered following rigid transformations. Registration is performed using the Elastix and NiftyReg toolboxes.' ... 'Except for the MRI scans, where affine transformations are used'; and 'Follow-up imaging data was acquired 2 to 9 days later and included DWI and ADC.' Zenodo record 16731717 (scout-stage verification this cycle): released 'binary infarct masks derived from follow-up MRI (lesion-msk.nii.gz)' in the NCCT-registered derivative space. Edema time course: peak brain edema at 3-5 days post-stroke (Stroke 2014, DOI 10.1161/STROKEAHA.114.006884; Stroke 2023, DOI 10.1161/STROKEAHA.123.045941) overlaps the 2-9-day follow-up window.",
  "keystone_residual_assumption": "Whether any manual mask correction happened after transfer to acute space (the documented QC was on DWI-space masks) is unknown; if organizers manually trimmed masks to acute anatomy, the halo would be reduced -- which the stage-1 census measures rather than assumes. Also assumed: the deformable re-registration with cost-function masking is accurate enough to serve as the discrepancy reference; this is why the impossible-voxel readout, which needs NO registration at all, is the primary stage-1 endpoint and the displacement field is secondary.",
  "rung_reached": "0; stage 1 (census) is decisive as a dataset-quality finding; rung 1 after the stage-2 model comparison.",
  "dies_like_prior": "Kill-code check: ideas 002 and 005 died on UNDOCUMENTED annotation provenance; here the geometric provenance is documented verbatim (affine-only, 2-9 days) and the error field is computable per case -- the provenance is the measurand, not an assumption. Sibling of this cycle's baseline c01 (the ground truth remembers the algorithm that drafted it): c01 audits label CONTENT provenance (who drew the boundary), c08 audits label GEOMETRY provenance (where the boundary landed after transfer); they share the audit-the-benchmark family but have disjoint mechanisms, disjoint readouts (draft-agreement statistics versus physically-impossible-voxel overlap), and compose -- c01's DeepISLES rerun doubles as c08's untrained-on-these-labels comparator. IDENTIFIABILITY_FAILURE (idea-020) is dodged by anchoring the primary claim to physical impossibility rather than to any registration being 'correct'.",
  "closest_prior_work": "The lesion-registration literature (cost-function masking, enantiomorphic normalization) established twenty years ago that focal lesions and deformation break standard registration, in the lesion-symptom-mapping context; final-infarct prediction reviews acknowledge edema-inflated follow-up volumes; no located work measures the geometric error baked into a public stroke benchmark's released ground truth or tests whether trained models reproduce it. See novelty_neighbors.",
  "novelty_neighbors": [
    {
      "work": "Brett, Leff, Rorden, Ashburner -- 'Spatial normalization of brain images with focal lesions using cost function masking' (NeuroImage 2001)",
      "identifier": "DOI 10.1006/nimg.2001.0845; found by search 2026-08-18",
      "relation": "Canonical demonstration that lesions corrupt registration and must be masked out of the cost function -- the exact instrument c08 reuses -- developed for template normalization in lesion-symptom mapping, never applied to auditing challenge ground truth."
    },
    {
      "work": "Nachev, Coulthard, Jaeger, Kennard, Husain -- 'Enantiomorphic normalization of focally lesioned brains' (NeuroImage 2008)",
      "identifier": "PMC2658465, DOI 10.1016/j.neuroimage.2007.10.002; found by search 2026-08-18",
      "relation": "Improves lesioned-brain registration using contralateral-hemisphere filling; again lesion-symptom-mapping methodology, quantifying that lesion-vicinity registration error grows with lesion size -- the same error family c08 measures in ISLES'24."
    },
    {
      "work": "Bertels, Robben, Vandermeulen, Lemmens -- 'Final infarct prediction in acute ischemic stroke' (review)",
      "identifier": "arXiv 2211.04850; found by search 2026-08-18, abstract fetched",
      "relation": "Review from the group behind native-CTP final-infarct prediction covering how follow-up imaging defines the target; the surrounding literature acknowledges edema-inflated follow-up volumes and attempted CSF exclusion, but neither this nor any located work measures the released ISLES'24 masks' geometric error or model inheritance of it."
    }
  ],
  "novelty_delta": "No located work quantifies the mass-effect registration error inside a public benchmark's RELEASED ground truth via a physically-impossible-voxel criterion, nor tests whether models trained on that benchmark reproduce the error.",
  "why_not_done": "BLIND_SPOT: the people who know lesioned-brain registration is fragile (lesion-symptom-mapping community, 2001-2012) and the people who build final-infarct benchmarks (segmentation-challenge community) are different communities; challenges treat registration as solved preprocessing, and the impossible-voxel criterion -- which sidesteps the 'which registration is correct' debate entirely -- appears in neither literature.",
  "existing_assets": "Released follow-up DWI/ADC, acute NCCT, ground-truth masks in the common derivative space (Zenodo 16731717); public registration tools (ANTs, SynthMorph) and the cost-function-masking recipe; SynthSeg and HU arithmetic for acute CSF; baseline c01's planned DeepISLES rerun as the untrained comparator; official evaluation code.",
  "smallest_decisive_experiment": "Stage 1 census on 30 cases stratified by lesion volume: compute the impossible-voxel fraction (primary, registration-free) and the affine-versus-deformable peri-lesional displacement (secondary, cost-function-masked), and correlate both with lesion volume and midline shift (mass-effect signature: error growing with severity is the fingerprint of unmodeled deformation, not random noise). Prespecified benchmark-relevance readout: recompute official Dice and absolute-volume-difference on the census cases with impossible voxels removed from the ground truth -- the metric shift bounds how much the halo moves scores. Compute envelope: one Colab GPU session (SynthMorph registration runs in seconds-to-minutes per pair; ~10-15 GB download). Full 149-case census: one further session. Stage 2 (conditional on the shared audit model): predicted-mask CSF-overlap rate versus the ground truth's own rate and versus the DeepISLES comparator, inference only, under 5 GPU-hours.",
  "standing_confounds_addressed": "Genuine infarct growth versus geometric error: separated by the physical-impossibility criterion (growth cannot occupy acute CSF), the primary endpoint. Partial volume and CSF-segmentation error: 1-2 voxel erosion, conservative HU window, two-tool cross-check, and a reported sensitivity band. Ventricular compression at follow-up cuts the OTHER way -- compressed ventricles make CSF overlap less likely, so the census is conservative. Deformable-reference circularity: the displacement field is secondary and direction-reported-both-ways; the primary endpoint uses no registration. Site and scanner: stratified by center. Labels are the object of study in stage 1; stage 2's readout is a comparison of overlap rates, not a Dice contest.",
  "alternative_explanations": [
    "Impossible voxels come from mask interpolation during resampling rather than affine failure -- distinguishable because interpolation error is thin-shell and uncorrelated with mass effect, while swelling displacement grows with lesion volume and midline shift; the correlation analysis is prespecified.",
    "The model predicts into CSF because of its own smoothing, not label inheritance -- the DeepISLES comparator (never trained on these transferred labels) and the tracking of per-case ground-truth impossible rates discriminate.",
    "Experts corrected masks in acute space, so the halo is small -- then the census returns a small number and the benchmark gets a documented clean bill on geometry; explicitly a valuable outcome."
  ],
  "anticipated_negative": "Decisive either way at stage 1: a large impossible-voxel fraction rising with mass effect is a benchmark-integrity finding with a computable metric bound; a near-zero fraction is citable evidence that the affine pipeline did not measurably corrupt the released masks. Stage 2's null (models ignore the halo and stay on tissue) is a genuinely reassuring property of the model family, interpretable because the stage-1 gate quantified the available halo first.",
  "cross_domain": {
    "borrowed_construct": "Datum shift from geodesy and surveying: coordinates are only meaningful relative to a reference frame, and transferring measurements between frames with an insufficient transformation model (e.g., a global affine for locally deformed terrain) produces systematic, spatially-structured position error that must be surveyed, not assumed away.",
    "measurement_it_implies": "The residual displacement field between the insufficient transform and a locally-adequate one, plus known-impossible landmark checks (the surveying practice of closing the traverse) -- here, CSF voxels as landmarks where infarct provably cannot be.",
    "what_changes_if_dropped": "Without the datum-error frame the study becomes 'registration is imperfect', a truism with no measurement discipline; the impossible-landmark check is what converts it into a falsifiable audit with a primary endpoint that needs no reference registration at all."
  },
  "remaining_legwork": "One session to the 30-case stage-1 decision; one further session for the full-cohort census and the metric-shift bound; stage 2 within a week once the shared audit model and the c01 DeepISLES rerun exist.",
  "design_template": "other:label-geometry-audit",
  "design_template_justification": "Nearest listed grammar is cross-model-disagreement, but the primary readout requires no second trained model: it is agreement of masks and predictions with a physically-impossible voxel set derived from the acute image itself. Counting it as cross-model-disagreement would overstate that template's concentration; the audit grammar (measure a documented provenance error, then test whether models inherit it) is shared with baseline c01 and is named the same way here for honest homogenization accounting.",
  "entry_point_2_requirements": "Measurement: impossible-voxel fraction of ground truth and predictions (acute-CSF overlap) and the affine-versus-deformable peri-lesional displacement field. Confused artifacts: partial volume, CSF-segmentation error, mask-interpolation shells, and deformable-reference error -- addressed by erosion margins, two-tool cross-check, the mass-effect correlation signature, and demoting all registration-dependent quantities to secondary endpoints.",
  "scores": {
    "clarity": {
      "value": 4,
      "why": "One documented mechanism, one registration-free primary endpoint, one prespecified correlation signature; the multi-tool CSF definition needs preregistration."
    },
    "identifiability": {
      "value": 4,
      "why": "The physical-impossibility criterion sidesteps the 'which registration is truth' debate that would otherwise sink the design; residual threats (partial volume, interpolation shells) are bounded and direction-signed."
    },
    "medical_relevance": {
      "value": 4,
      "why": "If voxel-level ground truth is geometrically wrong preferentially in severe strokes, every Dice- and volume-ranked conclusion from this benchmark inherits it, and 'model predicts infarct inside a ventricle' is a clinically legible defect."
    },
    "interest": {
      "value": 5,
      "why": "The ground truth being drawn on a swollen brain and transferred with a transform that cannot represent swelling -- during the documented edema peak -- is an obvious-once-said claim that no one has measured; both outcomes are tellable to the whole challenge community."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Twenty years of lesion-registration methodology supplies the instruments; all data and the comparator pipeline (via c01) are public or already planned."
    },
    "feasibility": {
      "value": 4,
      "why": "Keystone inspected true with verbatim quotes; the decisive census is one GPU session with modern learned registration, and the primary endpoint is registration-free arithmetic."
    },
    "data_readiness": {
      "value": 4,
      "why": "Follow-up DWI, acute NCCT, and masks are all in the public release; only a modest subset is needed for the decisive stage."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "The impossible-voxel and displacement metrics are custom (though simple); the metric-shift bound reuses official evaluation code."
    },
    "negative_result_value": {
      "value": 4,
      "why": "A near-zero halo is a clean, citable geometric validation of the benchmark's ground truth -- decisive, not sensitivity-limited, because the criterion is physical."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Strong adjacent literature on both sides with the specific audit unclaimed in every source found; capped by targeted-search scope despite the inspected keystone."
    },
    "regret": {
      "value": 5,
      "why": "Cheap, keystone-verified, composes with c01, and the question will eventually be asked of every follow-up-derived ground truth; being scooped on an obvious-in-hindsight audit of the program's own charter dataset would sting."
    }
  },
  "priority_score": 4.05,
  "unverified_claims": [
    "magnitude of the impossible-voxel fraction in the released masks (could be near zero if organizers corrected in acute space)",
    "acute-CSF segmentation reliability on the resampled derivative NCCT",
    "SynthMorph/ANTs with cost-function masking is adequate as the secondary displacement reference",
    "the shared audit model materializes for stage 2",
    "novelty beyond targeted search"
  ],
  "plain_pitch": "The 'correct answers' for this stroke benchmark were drawn on MRI scans taken 2 to 9 days after the stroke -- exactly when the injured brain is most swollen -- and then copied onto the earlier CT scans using a simple global alignment that cannot account for swelling. That would smear each answer's position, worst in the biggest strokes, sometimes marking 'dead brain tissue' on spots that are plainly fluid on the early scan, where there is no brain tissue to die. This study first measures that error directly on the public data, using fluid spaces as tamper-proof landmarks, and then asks whether prediction models trained on these answers have learned to copy the error -- forecasting damage in places where damage is physically impossible. Either way the benchmark community learns something it currently assumes: how much of the official ground truth is geometry gone wrong, or that the pipeline survived the swelling problem intact.",
  "charter": "isles24"
}


===== ideas/030/keystone_screen.md =====
# Keystone screen — idea 030 (isles24-scout-004-c08)

**Idea:** The ground truth was drawn on a swollen brain
**Screen date:** 2026-08-18
**Verdict: PASS** (keystone verified true from primary sources; one auxiliary
citation not independently re-quoted — see §4)

## 1. The keystone as stated on the card

> "Ground-truth masks were transferred to acute NCCT space via affine-only
> registration of follow-up MRI acquired in the edema window, so mass-effect
> deformation is unmodeled by construction."

Card status claimed: `INSPECTED_TRUE`. This screen re-inspected every leg
independently against primary sources, plus the mandatory
nearest-checkable-thing follow-up (§4).

The keystone decomposes into four checkable legs:
(a) the follow-up MRI → NCCT registration is affine (a linear map, which
cannot represent local mass-effect deformation);
(b) the follow-up MRI was acquired in a window overlapping post-stroke
space-occupying edema;
(c) the released ground-truth masks live in the NCCT-registered space, i.e.
they actually passed through that transform;
(d) the masks were drawn on the follow-up MRI (not natively on acute NCCT).

## 2. What was inspected, with verbatim evidence

### 2a. Registration to NCCT space is linear; MRI specifically is affine

Source: arXiv 2408.10966v1 (ISLES'24 dataset paper), Dataset section,
https://arxiv.org/html/2408.10966v1 (fetched 2026-08-18 by this screen):

> "Preprocessing of the images has been performed by linearly interpolating
> and registering all the imaging series to the NCCT scans."

> "Except for the MRI scans, where affine transformations are used, all
> remaining images are registered following rigid transformations."

> "Registration is performed using the Elastix [48] and NiftyReg [49]
> toolboxes."

Both quotes match the card's `keystone_evidence` character-for-character
where they overlap. An affine transform is global and linear; local
deformation from mass effect is outside its model class by definition. No
deformable step is mentioned anywhere in the preprocessing description.
Leg (a) verified.

### 2b. Follow-up acquisition window

Same source and section:

> "Follow-up imaging data was acquired 2 to 9 days later and included DWI
> and ADC."

Leg (b), timing half: verified. (The "edema window" characterization —
that this overlaps peak space-occupying edema — is assessed in §4.)

### 2c. Released masks are in NCCT space, produced by linear co-registration

Source: Zenodo record 16731717, "ISLES'24 - A Real-World Longitudinal
Multimodal Stroke Dataset", version v7, https://zenodo.org/records/16731717
(fetched 2026-08-18 by this screen):

> "Derivatives include all modalities linearly co-registered to the NCCT
> space."

and the release includes

> "binary infarct masks derived from follow-up MRI (lesion-msk.nii.gz)"

with the mask filename in the derivatives tree carrying the space tag
explicitly: `sub-strokecase0001_ses-02_space-ncct_lesion-msk.nii.gz`.
The follow-up scans likewise appear as `space-ncct_dwi.nii.gz` and
`space-ncct_adc.nii.gz`. Legs (c) verified: the deliverable ground truth is
the NCCT-space derivative, and the release itself states the co-registration
is linear.

### 2d. Masks were drawn on follow-up DWI, not natively on acute NCCT

Source: arXiv 2408.10966v1, Dataset section (same fetch):

> "Lesion masks are derived from DWI images using the ISLES'22 ensemble
> algorithm."

> "Quality control and correction of the lesion masks are performed when
> needed by medical students (TAB, HPM) supervised by two neuroradiologists
> (JSK, BW) with more than 10 years of experience."

Leg (d) verified: annotation provenance is DWI-side. The QC quote is the
anchor for the card's stated residual (see §3 — the paper does not say in
which space corrections were made).

## 3. The card's stated residual assumption

The card already names the right residual: whether any manual mask
correction happened *after* transfer to acute-NCCT space. The paper's QC
sentence (§2d) specifies who corrected but not in which space, and the
Zenodo page adds no methodological detail on the derivation. This screen
confirms the residual is genuinely open in the primary sources — and
confirms the card's handling is sound: the stage-1 census *measures* the
surviving halo rather than assuming its size, and "experts corrected in
acute space, halo is small" is listed as an anticipated, still-valuable
outcome. The keystone as stated does not require the halo to be large; it
requires the construction to be affine-only, which is documented.

## 4. Wrong-keystone check: what is the card still assuming?

**Q: if this card only verified the nearest checkable thing, what is it
still assuming?**

1. **That the released `space-ncct` mask is the product of the documented
   linear transform applied to the DWI-space mask, not an independent
   re-annotation in NCCT space.** No primary source describes a native
   acute-space annotation pass, and the release explicitly labels all
   derivatives as "linearly co-registered." An undocumented manual edit in
   NCCT space is the only escape hatch, and that is exactly the residual in
   §3, measured (not assumed) by the design. Not a wrong-keystone error.

2. **That the NCCT is acute (pre-swelling), so displacement between the
   sessions is real.** The dataset's own structure states acute imaging
   (ses-01: NCCT/CTA/CTP at presentation) versus follow-up (ses-02, "2 to 9
   days later"). Verified by construction of the release.

3. **That the 2–9-day window overlaps peak space-occupying edema.** The
   2–9-day acquisition window is verbatim-verified (§2b). The specific
   "3–5-day peak" literature anchor (Stroke 2014, DOI
   10.1161/STROKEAHA.114.006884; Stroke 2023, DOI
   10.1161/STROKEAHA.123.045941) could NOT be independently re-quoted by
   this screen: ahajournals.org returns HTTP 403 to this environment, and
   the PubMed abstract of the 2014 paper (PMID 25336512, "Brain Edema
   Predicts Outcome After Nonlacunar Ischemic Stroke") confirms serial-MRI
   swelling measurement but does not state the day range in the abstract.
   Classification: **source-supported interpretation, not re-verified
   verbatim here.** This is auxiliary, not load-bearing: the keystone's
   falsifiable core is the affine-only transfer of masks derived from
   follow-up MRI acquired days after stroke; post-stroke edema evolving
   over the first week is settled physiology, and any first-week peak
   placement is inside the verified 2–9-day window. If critique wants the
   day-range quote on record, it needs a non-AHA mirror of either citation.

4. **That "affine" in the paper means affine for the transform actually
   applied to the *masks*, not just the images.** The masks are derived
   from DWI (§2d) and released in `space-ncct` (§2c); a mask can only reach
   NCCT space via some transform, and the only documented MRI→NCCT
   transform is the affine one. The alternative (a second, undocumented,
   deformable mask-transfer pipeline alongside the documented linear one)
   has no support in either source and would contradict the release's own
   "linearly co-registered" description.

No load-bearing assumption differs from the stated keystone. The stated
keystone is the right keystone, and it is documented in two independent
primary sources (the dataset paper and the data release).

## 5. Verdict

All four legs of the keystone are verbatim-verified. The single genuinely
open question (post-transfer manual correction) is the card's declared
residual, and the design measures it rather than resting on it.

```json
{"verdict": "PASS", "evidence": "Except for the MRI scans, where affine transformations are used, all remaining images are registered following rigid transformations.", "source": "https://arxiv.org/html/2408.10966v1, Dataset section; corroborated by https://zenodo.org/records/16731717 (v7): 'Derivatives include all modalities linearly co-registered to the NCCT space', mask released as sub-strokecase0001_ses-02_space-ncct_lesion-msk.nii.gz", "note": "Affine-only MRI-to-NCCT transfer of DWI-derived masks acquired 2-9 days post-stroke is documented in both the paper and the release; the only escape hatch (undocumented manual correction in acute space) is the card's declared residual, measured by stage 1."}
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

## Closing section: "In plain terms" (required)

End consensus.md with a section titled `## In plain terms` written
for a reader with no background: what this idea asks (two sentences),
what the debate concluded and why (two or three sentences), and - if
the verdict routes a question to the human - what the human is
actually being asked to judge, in one plain sentence. Same fidelity
rule as everywhere: nothing stated more strongly than the verdict
itself states it. This section is a VIEW of the verdict, never the
record of it; the json verdict block remains authoritative.


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
