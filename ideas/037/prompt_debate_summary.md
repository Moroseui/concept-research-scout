You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/037
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

51 tracked ideas in this charter. Latest state per idea; full history in ledger.jsonl.

Work under other charters: evidence/cross_charter_index.md (facts, no scores).

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **IDENTIFIABILITY_FAILURE** x9: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_ACCESS** x3: Required data, checkpoints, or mappings are not obtainable in practice.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **isles24-scout-002-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.4, audited 2026-08-16] -- Two tissues, two death thresholds
- **isles24-scout-004-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.1, audited 2026-08-18] -- The heart's signature in the head scan
- **isles24-scout-004-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.3, audited 2026-08-18] -- The brain's odometer: calcification as the model's age gauge
- **isles24-scout-002-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.2, audited 2026-08-16] -- The clot that lets contrast through
- **isles24-scout-002-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.0, audited 2026-08-16] -- The barrier is already leaking
- **isles24-scout-001-c01** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.6, audited 2026-08-16] -- Does the winning model rediscover the collateral clock?
- **isles24-scout-001-c03** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.5, audited 2026-08-16] -- Read the stroke from the blood leaving, not only entering
- **isles24-scout-001-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.5, audited 2026-08-16] -- The frail brain around the threatened territory
- **isles24-scout-002-c08** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.4, audited 2026-08-16] -- Has the deficit percolated? Volume is what the metric sees; connectivity may be what the model uses
- **isles24-scout-003-c02** [UNAUDITED, score 3.7] -- How much artery did the clot occupy?
- ... and 4 more (python scout.py backlog)

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
- **idea-030** [REJECTED/DEBATED/wide] -- The ground truth was drawn on a swollen brain -- killed: IDENTIFIABILITY_FAILURE
- **idea-031** [REJECTED/SCOUTED/baseline] -- The vascular detour the segmentation model can see -- killed: DATA_ACCESS
- **idea-032** [REJECTED/DEBATED/baseline] -- The arterial network's spare route -- killed: IDENTIFIABILITY_FAILURE
- **idea-033** [REJECTED/DEBATED/baseline] -- Did preprocessing teach the winner to read the disappearing insular ribbon? -- killed: IDENTIFIABILITY_FAILURE
- **idea-034** [REJECTED/DEBATED/wide] -- The edge of the map: the benchmark scores terra incognita -- killed: IDENTIFIABILITY_FAILURE
- **idea-035** [REJECTED/DEBATED/wide] -- The skull is a fixed-volume pressure vessel -- killed: IDENTIFIABILITY_FAILURE
- **idea-036** [REJECTED/DEBATED/baseline] -- Does the model bring a vascular map to the scan? -- killed: IDENTIFIABILITY_FAILURE
- **idea-037** [SHORTLISTED/CRITIQUED/wide] -- The scan remembers which hospital took it
- **idea-038** [SHORTLISTED/SCOUTED/wide] -- Does the model price the last mile of blood delivery?
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


===== ideas/037/README.md =====
# Idea 037: The scan remembers which hospital took it

Selected from scouting cycle isles24-004, candidate 6.


===== ideas/037/critique.md =====
FATAL OBJECTION: The proposed spectral edit cannot identify use of an acquisition-site noise fingerprint because its “noise residual” and NPS jointly encode reconstruction, dose, interpolation, object-dependent noise, and denoiser error, while no paired acquisition or validated generator shows that anatomy and all other model-readable evidence remain fixed.
EVIDENCE: Kharboutly et al., DOI 10.1109/EUVIP.2014.7018385 (eight 3D images from different scanners); Mackin et al., DOI 10.1002/mp.14208; ideas/037/idea_card.json.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Detailed critique

## 1. The intervention does not manipulate the claimed construct

The card's key inference is invalid:

> classifier-flipping, matched-energy spectral reshaping + a spectrally neutral sham -> only the site fingerprint changed -> any model response demonstrates use of that fingerprint.

The middle term is not established. In reconstructed CT, the noise power spectrum is a property of an acquisition-and-reconstruction chain, not a unique sensor identifier. It varies with reconstruction kernel, dose, pitch, reconstruction method, object size and position, and spatial location. Mackin et al. experimentally found that reconstruction kernel strongly shifts NPS peak frequency and CT texture features (PMCID PMC5729963; DOI 10.1002/mp.14208). Li et al. further showed that local NPS estimates depend on ROI size/location, background removal, windowing, and reconstruction method (PMCID PMC5690921; PMID 27167257). These are primary measurements, not a semantic objection.

A wavelet-Wiener residual is also not guaranteed to be anatomy-free. It is the difference between an image and an imperfect denoised estimate; edges, fine anatomy, partial volume, beam-hardening structure, and interpolation correlations can remain. “Homogeneous” ventricular CSF and white-matter patches reduce this problem but do not prove its absence, and extracranial air is especially vulnerable to defacing and padding signatures. A site classifier can exploit any of those residual differences. A successful classifier-flip manipulation check establishes that the edit crosses that classifier's decision boundary, not that it substitutes a physical scanner fingerprint.

The sham does not rescue identification. An equal-energy phase or spectrum permutation is merely a different artificial perturbation. If the target edit changes directional correlations, local stationarity, resolution/noise coupling, or residual anatomical structure while the sham does not, a larger response to the target remains compatible with generic sensitivity to those properties. Likewise, a monotone response along a constructed blend axis shows sensitivity to the construction, not to site identity as a causal variable.

The card therefore cannot deliver its rung-1 sentence. At best it can say that a particular model responds to a particular NPS-remapping operator. Replacing “uses the acquisition-site noise fingerprint” with that sentence changes the deliverable's identity under the repository's claim-identity rule.

## 2. The cited forensics instrument is not validation for this use

Kharboutly et al. is described too strongly as proving CT-scanner fingerprint readability. The 2014 primary paper reports experiments on only **eight 3D images of 100 slices from different scanners** and constructs reference noise patterns from 3D images before correlating test slices (DOI 10.1109/EUVIP.2014.7018385; author PDF: https://www.lirmm.fr/~subsol/WWW/EUVIP.1214.1.pdf). On the evidence reported, this does not demonstrate patient-independent, protocol-robust scanner identification: slices from one volume are not independent patients, and one volume per scanner leaves anatomy, protocol, and scanner perfectly bundled. It is a method precedent, not construct validation for a 149-patient multicenter clinical dataset.

The card's novelty claim is correspondingly too confident. “None anywhere uses” is universal language unsupported by a targeted search. The defensible statement is only that the recorded search did not locate a stroke-outcome-model use test of this form.

## 3. Site, scanner, protocol, and preprocessing remain inseparable

The keystone screen verified five scanner models across two manufacturers but found no device-to-center mapping. A Munich-versus-Zurich classifier therefore measures center decodability, not scanner identity. Center can be encoded by reconstruction kernel, voxel geometry, field of view, padding, defacing behavior, preprocessing success, or protocol—not necessarily stochastic sensor noise. Calling the result a “site fingerprint” does not solve the measurement problem because the deliverable immediately defines that fingerprint as “scanner-specific noise texture.”

Registration and resampling make the interpretation harder. Their interpolation kernels impose spatial correlations, and those correlations can depend on source voxel geometry and transform. A derivative-input classifier may thus read a preprocessing-by-geometry signature. Raw/derivative comparisons can localize when decodability appears or disappears, but cannot determine which physical source generated it.

There is no concept-label circularity in the ordinary sense—final-infarct labels are not used in the proposed paired response—but there is **instrument circularity**: the same site classifier defines whether the residual is site-like and certifies that the intervention became more site-like. Passing both checks validates agreement with that classifier, not the underlying physical construct. A second classifier family or held-out cases would reduce model overfitting but would not cure construct confounding.

## 4. The audited model and endpoint are not ready

The proposed “shared audit model” does not exist. The endpoint is consequently underspecified: which released or trained model, which input channels, which frozen preprocessing, what constitutes “non-trivial” held-out performance, and whether the model even consumes NCCT/CTA/CTP image channels that retain the proposed residual are all unresolved. This is not a minor feasibility detail because the winning ISLES'24 method used skull stripping and custom intensity windowing before a residual nnU-Net (Ren et al., arXiv:2505.18424). The relevant fingerprint may be removed, transformed, or absent from some input channels.

An easier codebase exists, but it is not a strong substitute model. The released PrediCTP repository provides training and inference code for a raw-4D-CTP model (https://github.com/kimberly-amador/ISLES24-PrediCTP), yet its reported performance is Dice 0.20 and lesion-wise F1 0.02. Auditing a weak model could yield an easy response curve but little medical value. The official ISLES repository provides data-loading and evaluation code, not a frozen high-performing checkpoint (https://github.com/ezequieldlrosa/isles24). Thus the card overstates “prior legwork” and “evaluation readiness.”

The primary response is also unclear. A segmentation has millions of probabilities: plausible summaries include lesion volume, mean probability, voxelwise logit change, soft Dice against the eventual label, or spatially localized change. Those answer different questions. A signed forecast shift cannot be prespecified without defining the sign of the other-center edit and a center-conditioned outcome direction; the card explicitly puts that outcome analysis out of scope. Without it, “signed output change” is not a single endpoint.

## 5. Feasibility and negative-result value are overstated

The public archive is approximately 99 GB according to the keystone screen, not the card's proposed 15–20 GB download. A 60-case subset might be smaller, but the subset bytes and required modalities have not been enumerated. More importantly, automated reliable homogeneous-ROI selection across NCCT and 4D CTP is not “no annotation” merely because no human labels are requested: ventricular CSF, periventricular white matter, and surviving extracranial air require segmentation, erosion, artifact exclusion, and quality control. CTP noise is time-, enhancement-, and motion-dependent, so baseline-frame residuals are not interchangeable with stationary NCCT noise.

The claimed negative is not decisive. Even after center decodability passes, a null edit response can mean that the model ignores site information, that the edit failed to alter the particular site feature the model uses, that preprocessing removed the cue before inference, that the selected summary cancels spatially mixed changes, or that the model is too weak. Decodability by an external shallow classifier does not guarantee alignment with the audited model's representation. The negative-result score should be at most 2 for the proposed intervention.

## 6. Medical relevance is conditional, not demonstrated

Site shortcuts are medically important, but this study does not test the clinically important consequence: performance or calibration failure at a new site. ISLES'24 has only two disclosed training centers, and its hidden test set is not an accessible third-center transfer cohort. A perturbation response on 30 held-out cases cannot support the card's predicted “failure mode at any third center.” That is speculation requiring external validation.

The most direct ISLES'24 question is whether held-out performance differs by center and whether a model trained without one center transfers to it. That does not identify a noise mechanism, but it measures the deployment risk that motivates the card.

## 7. Plain-pitch fidelity: failed

The pitch strengthens four unverified statements:

- “two hospitals with different scanners” is not verified because the dataset paper does not map devices to centers;
- “where you were treated is itself informative about how you will fare” is only a plausible hypothesis; no center-wise outcome analysis is in the card;
- “swaps only the invisible noise signature ... touching nothing about anatomy” presents an unvalidated intervention assumption as fact;
- “would matter anywhere ... at a hospital it never saw” generalizes beyond a two-center, no-third-site design.

These are not harmless simplifications. They remove the exact limitations that determine whether the result has a physical and clinical interpretation.

## 8. Low-hanging fruit and the easier defensible study

The genuine low-hanging fruit is a **site-stratified out-of-fold benchmark audit**. ISLES'24 already provides 149 public training cases, per-case center labels, final-infarct masks, official metrics (Dice, absolute volume difference, absolute lesion-count difference, lesion-wise F1), and official loading/evaluation code. A frozen nnU-Net recipe also exists in the winning-method publication/code ecosystem, although checkpoint availability must be verified before calling it ready.

Use nested patient-level evaluation with two complementary estimates:

1. fixed pooled training with strictly out-of-fold predictions, reporting every official metric and calibration/volume bias separately by center with patient-level uncertainty; and
2. train-on-Munich/test-on-Zurich versus appropriately size-matched within-Munich resampling, repeated with frozen splits, to distinguish ordinary small-training-set degradation from cross-center degradation.

With only 50 Zurich cases and no third site, this remains a two-center benchmark audit, not a general deployment guarantee. It also cannot attribute any gap to scanner noise. But it answers a clinically meaningful question using existing labels and accepted endpoints, and a null is interpretable within stated precision. Metadata-only site decodability from raw/derivative images is even cheaper, but by itself is routine and not worth a separate candidate; it should be diagnostic context inside the performance audit.

The original noise-use question would require a different dataset or new acquisition: repeated phantom/scans across devices and protocols, or traveling-subject/paired reconstruction data that independently validates a noise-transfer operator while holding anatomy fixed, followed by testing a competent final-infarct model. ISLES'24 does not contain that counterfactual support.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: On strictly out-of-fold ISLES'24 predictions, does final-infarct performance, calibration, or volume bias differ by center, and does train-on-one-center transfer degrade beyond a size-matched within-center baseline?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—unlike a site-decoding census, it directly measures the multicenter deployment risk using released center labels, lesion masks, accepted metrics, and reusable training/evaluation machinery, while remaining honest that it cannot identify scanner-noise use.


===== ideas/037/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed NPS-residual transplant does not isolate an acquisition-site noise fingerprint, so even a positive model response cannot support the original deliverable sentence.

**Argument:** In CT, the measured residual and noise-power spectrum jointly vary with reconstruction kernel, dose, interpolation, object size and position, reconstruction method, and denoiser error; residual fine anatomy and preprocessing correlations can also survive. Mackin et al. directly measured strong reconstruction-kernel effects on NPS and texture (DOI 10.1002/mp.14208), while the cited scanner-forensics precedent used only eight 3D images from different scanners, leaving patient, protocol, and scanner bundled (Kharboutly et al., DOI 10.1109/EUVIP.2014.7018385). ISLES'24 supplies neither paired acquisitions that hold anatomy and protocol fixed across devices nor a validated noise-transfer generator. Therefore, a classifier flip, matched total energy, monotone blend response, and spectrally neutral sham would show sensitivity to this particular synthetic operator, not use of a physical site fingerprint. Recasting the result as “the model responds to NPS remapping” fails the mandatory identity check: it no longer answers whether the model uses scanner-specific noise as a site prior and must be a separate candidate. The proposed site-stratified out-of-fold performance audit is likewise a defensible successor, not a repair, because it tests cross-center performance rather than the claimed mechanism.

**What would change my mind:** Show primary validation on repeated phantom, traveling-subject, or paired-reconstruction acquisitions demonstrating that the exact transfer operator changes independently recoverable device/site noise identity while preserving anatomy, resolution, dose/kernel information, and all other model-readable evidence, then apply that frozen operator to a competent, frozen ISLES'24 final-infarct model with a prespecified spatial output endpoint.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card's key inference — classifier-flipping, energy-matched spectral reshaping plus a neutral sham implies that only the site noise fingerprint changed, so any model response demonstrates use of that fingerprint — has an unestablished middle term. Within ISLES'24 there is no paired acquisition, phantom, or traveling-subject data that could validate the transfer operator, so a positive response shows sensitivity to this synthetic operator, not use of a physical site fingerprint; and the honest recast ("the model responds to NPS remapping") is a different deliverable sentence under the claim-identity rule.

**Response:** CONCEDE

**Argument:** The objection is correct, and no amendment available inside this dataset repairs it.

I checked the only two defenses the card could mount, and both fail:

1. *"The claim is about the site-labeled noise channel, not physical scanner identity, so operator physicality doesn't matter."* This fails twice over. The deliverable sentence itself commits to "scanner-specific noise texture," so the weaker channel reading is already an identity change. And even the weaker claim still requires that the edit changes nothing else model-readable — directional correlations, local stationarity, resolution-noise coupling, surviving fine anatomy in the residual — which is precisely what is unvalidated. The equal-energy sham gates one artifact family (generic spectral perturbation), not that enumeration; a larger response to the target than the sham is compatible with sensitivity to any of those co-varying properties.

2. *"The classifier-flip manipulation check ties the dose axis to site identity."* The critic's instrument-circularity point stands: the same classifier family defines what counts as site-like and certifies that the edit became more site-like. Passing both establishes agreement with that classifier's decision boundary, not substitution of the underlying construct. A second classifier family would reduce overfitting, not confounding, because every classifier is trained on the same two-center data in which noise statistics, kernel, dose, geometry, and preprocessing are perfectly bundled.

The critic's discharge condition — primary validation of the frozen operator on repeated-phantom, traveling-subject, or paired-reconstruction acquisitions — is the correct and only route to the original question, and that data is outside ISLES'24 by construction. This makes the failure an IDENTIFIABILITY_FAILURE of the same family as idea-020: the card's `dies_like_prior` entry claimed the within-case transplant was "precisely such an intervention" that separates the mechanism from co-varying factors, but an intervention whose own validity cannot be established in any obtainable cohort does not discharge that kill pattern; it relocates it from the cohort to the operator.

What is lost: the mechanism-isolating use test, which was the entire point of the candidate. The Stage-0 decodability census survives as a fact-finding exercise but is, as the critique says, routine detectability — prior art territory (Zech et al., arXiv 2008.08525) — and not worth a standalone candidate. The keystone screen's verified facts (per-case center labels released, raw plus derivative arms present, five scanner models across two vendors) remain of record and transfer to any successor.

**Spin-off** (for normal scout-cycle registration with `parent_ids: ["isles24-scout-004-c06"]`, not mid-debate adoption): the critique's site-stratified out-of-fold benchmark audit — does final-infarct performance, calibration, or volume bias differ by center on strictly out-of-fold predictions, and does train-on-one-center transfer degrade beyond a size-matched within-center baseline? It keeps the medical motivation (multicenter deployment risk), uses only released labels, center assignments, and official metrics, and is honest that it measures the consequence without identifying the noise mechanism. A second, conditional successor — the original use test gated on externally validated noise-transfer operators from phantom or paired-reconstruction data — should only be registered if such a validation dataset is actually located; it dies on DATA_ACCESS otherwise.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposer has substantively conceded the fatal identifiability objection, so the original candidate should be rejected and neither proposed spin-off should be treated as an amendment.

**Argument:** The concession is supported by argument rather than repetition: it accepts that the classifier-flip check is instrument-circular, that the matched-energy sham excludes only one artifact family, and that ISLES'24 contains no paired or phantom acquisition capable of validating the residual-transfer operator while holding the other model-readable acquisition properties fixed. It also passes the identity check correctly. A site-stratified out-of-fold performance audit asks whether performance or calibration differs by center, not whether the model uses scanner-specific noise texture; the conditional externally validated transfer study preserves the original question but depends on evidence outside the current dataset that has not been located. Thus neither is a repair to this card, and the verified ISLES'24 facts about center labels, raw and derivative images, and scanner heterogeneity do not rescue the causal use claim. There is no remaining factual dispute within the present design: the candidate dies by IDENTIFIABILITY_FAILURE, while any successor must enter separately under the stated parent ID and undergo its own novelty and feasibility review.

**What would change my mind:** Locate the previously specified repeated-phantom, traveling-subject, or paired-reconstruction primary evidence validating the exact frozen transfer operator, together with an obtainable competent final-infarct model; that would justify registering and evaluating the conditional successor, not reversing this candidate's rejection in place.

**Status:** CONCEDED

## Round 2 — PROPOSER

**Responding to:** The critic accepts the round-1 concession as substantive, rules that neither spin-off is an amendment to this card, and closes the candidate as an IDENTIFIABILITY_FAILURE, with any successor entering separately under `parent_ids: ["isles24-scout-004-c06"]` and subject to its own novelty and feasibility review.

**Response:** CONCEDE

**Argument:** The concession stands and nothing in the critic's round 2 is contested; I will not re-argue what both sides already accept. Two closing points of record, neither reopening the dispute:

1. **The critic's reversal condition and my registration gate for the conditional successor are the same condition.** Round 1 said that successor "should only be registered if such a validation dataset is actually located; it dies on DATA_ACCESS otherwise"; the critic's what-would-change-my-mind names the same evidence (validated frozen transfer operator plus an obtainable competent final-infarct model) and the same consequence (register and evaluate the successor, never reverse this rejection in place). The condition can be carried into the ledger entry verbatim with no interpretive gap.

2. **Proposed ledger disposition, for the human gate:** REJECT, kill code IDENTIFIABILITY_FAILURE, with the specific signature recorded so future candidates can be checked against it: the intervention's own construct validity — that the transfer operator changes site-noise identity while leaving everything else model-readable fixed — cannot be established in any obtainable cohort; the idea-020 kill pattern relocated from cohort to operator. Facts of record that transfer to successors: per-case center labels are released (arXiv 2408.11142v2, keystone screen), raw and derivative arms exist per case, five scanner models across two manufacturers with no device-to-center mapping, and the public train set is 149 cases (99 + 50), correcting the card's 100 + 50. The site-stratified out-of-fold benchmark audit enters through a normal scout cycle on its own merits, with no inherited queue position, per the 2026-08-10 claim-identity rule.

No factual dispute remains and no amendment is on the table.

**Status:** CONVERGED


===== ideas/037/idea_card.json =====
{
  "id": "isles24-scout-004-c06",
  "parent_ids": [],
  "track": "wide",
  "entry_point": 2,
  "title": "The scan remembers which hospital took it",
  "question": "Is an ISLES'24 final-infarct model using the acquisition-site noise fingerprint -- the scanner's stochastic signature readable in signal-free voxels, the CT analogue of camera-sensor forensics -- as a site-identity prior that shifts its infarct forecast?",
  "rung": "Target rung 1: use of the noise-residual channel. Rung 2 (the model treats site identity as an outcome prior, the 'rational expectations' reading) requires linking the response direction to center-wise outcome statistics and is explicitly out of scope for the first study.",
  "deliverable_sentence": "The final-infarct model is using the acquisition-site noise fingerprint -- scanner-specific noise texture readable in signal-free image regions -- when predicting final infarct.",
  "X_measurement": "X is site identity as decoded from the noise residual alone: extract the stochastic component with a wavelet-based Wiener denoising filter (the exact instrument of CT-scanner forensics, Kharboutly et al.) from homogeneous ROIs (ventricular CSF, periventricular white matter, extracranial air where defacing spared it) on raw and derivative NCCT and on CTP baseline frames; compute noise-power-spectrum features; train a patient-level cross-validated linear/shallow classifier for Munich-versus-Zurich on noise-only patches. Compute-today test: YES -- denoising filters, NPS estimation, and a logistic classifier on public data, no annotator.",
  "suspected_signal": "The two centers use different scanner fleets and protocols, so every image carries a hardware-and-protocol noise signature the way every photograph carries its camera's sensor pattern noise. The centers plausibly differ in population, treatment practice, and outcome mix, so site identity is prognostically loaded; a model that can read the fingerprint can silently condition its infarct forecast on where the patient was scanned. Multi-step story, each link separately checkable: the model uses the noise fingerprint (X, the use test), which it can only see because two fleets differ and the fingerprint survives organizer preprocessing (Y, the decodability census on model-facing derivative data), which implies center-conditional forecasts and a predictable failure mode at any third center (Z, out-of-scope rung 2).",
  "use_vs_association": "Association (site correlates with outcome) predicts no response to a within-case edit that changes only the noise residual; use predicts a signed output change when a case's residual is spectrally reshaped toward the other site's measured mean noise power spectrum (phase-preserving, dose-blended), with null response to an equal-energy spectrally-neutral sham permutation -- the anatomy, protocol, and population are held fixed by construction because the case is its own control.",
  "keystone_prerequisite": "Site identity is decodable from noise-only patches of the MODEL-FACING derivative inputs (registration and resampling may have attenuated the raw fingerprint), and the shared audit model reaches non-trivial held-out performance.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_residual_assumption": "Verified nearby facts: two-center composition is verbatim on record (100 Munich / 50 Zurich train, re-verified this stage from arXiv 2408.10966v1), raw scans are released 'in their original space, just defaced' (Zenodo 16731717, scout-stage verification), and CT-scanner identification from sensor noise is published forensics practice (Kharboutly et al.). The load-bearing fact -- decodability surviving the organizers' motion correction, registration, and resampling on derivative data -- is exactly the stage-0 census. A second residual: vendor/protocol identity was not verifiable from the papers (neither states scanner hardware, checked this stage), so fleet separation between the centers is assumed, not known; the classifier census answers this too.",
  "rung_reached": "0; rung 1 after the decodability gate, transplant dose-response, and sham gate on the shared audit model.",
  "dies_like_prior": "Kill-code check: IDENTIFIABILITY_FAILURE (idea-020) died because no intervention could separate the mechanism from co-varying factors -- here the within-case residual transplant with a classifier-flip manipulation check and an equal-energy sham is precisely such an intervention, and every gate is prespecified. DATA_ACCESS (idea-024) does not apply: all inputs are in the public release. Nearest living relative is backlog 001-c08 (the deconvolution algorithm may have signed the image): different X and different failure mode -- icobrain processed ALL cases, so its software signature cannot encode site, whereas scanner hardware noise can; c06 is about a between-center shortcut, 001-c08 about a uniform tool artifact. Cross-charter fact (score-free, via the index): the completed reconstruction-sensitivity study under the other charter established that a chest-CT model's outputs move with reconstruction-dependent noise content -- precedent that this cue class is readable by real models, on different data and task.",
  "closest_prior_work": "Scanner forensics proves fingerprint readability but never connects it to a downstream clinical model; the confounding literature shows site detectability and generalization gaps but never isolates the noise channel with a within-case intervention. See novelty_neighbors.",
  "novelty_neighbors": [
    {
      "work": "Kharboutly, Puech, Subsol, Hoa -- 'CT-Scanner identification based on sensor noise analysis' (EUVIP 2014) and 'Improving sensor noise analysis for CT-scanner identification' (EUSIPCO 2015)",
      "identifier": "HAL lirmm-01379581 and lirmm-01379558; EUSIPCO 2015 paper 1570103637; found by search 2026-08-18",
      "relation": "Establishes that individual CT scanners are identifiable from wavelet-Wiener noise residuals -- the measurement instrument this candidate borrows -- but is pure forensics: no clinical prediction model, no use test."
    },
    {
      "work": "Zech et al. -- 'Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs' (PLoS Medicine 2018)",
      "identifier": "DOI 10.1371/journal.pmed.1002683; found by search 2026-08-18",
      "relation": "Showed CNNs robustly identify hospital system and that this confounds disease prediction -- association and generalization-gap evidence on 2D radiographs, with no intervention isolating the noise channel from anatomy, markers, or population."
    },
    {
      "work": "'Name that manufacturer: relating image acquisition bias with task complexity when training deep learning models on head CT'",
      "identifier": "arXiv 2008.08525; found by search 2026-08-18",
      "relation": "Shallow CNN classifies scanner manufacturer from head CT and documents acquisition bias in training -- again detectability, not use, and no stroke-outcome model."
    }
  ],
  "novelty_delta": "No located work tests whether a stroke lesion-outcome model USES the scanner-noise fingerprint, and none anywhere uses a within-case noise-residual transplant between real sites to isolate the noise channel from anatomy, protocol, and population.",
  "why_not_done": "BLIND_SPOT: the forensics community (which owns the fingerprint instrument) and the medical-imaging confounding community (which owns the site-shortcut concern) publish in disjoint venues; site effects are treated as generalization statistics to be harmonized away, not as an isolatable input channel to be use-tested. The two-center, raw-plus-derivative ISLES'24 release makes the transplant experiment newly convenient but not newly possible.",
  "existing_assets": "Public raw and derivative images for 149 cases (Zenodo 16731717); published wavelet-Wiener residual extraction recipes; standard NPS estimation from CT quality assurance; the program's shared audit model planned under this cycle's baseline candidates; official evaluation code.",
  "smallest_decisive_experiment": "Stage 0/1 (decisive for the keystone, model-free): 60 cases stratified 30 per center; extract noise-only patches from raw NCCT, derivative NCCT, and CTP baseline frames; patient-level cross-validated site classifier; prespecified gate: noise-only AUC >= 0.8 on MODEL-FACING derivative inputs (raw-only decodability that dies in preprocessing kills the candidate cleanly). Compute envelope: one Colab GPU session (~15-20 GB download, under 2 GPU-hours; the classifier is minutes). Stage 2 (use test, conditional on the shared audit model): 30 held-out cases x 5 spectral blend doses toward the other site's mean NPS x equal-energy shams, inference only, under 5 GPU-hours -- also one session.",
  "standing_confounds_addressed": "The use test is within-case, fixing anatomy, protocol, positioning, habitus, population, prevalence, and referral by construction. Classifier-reads-anatomy-not-noise is excluded by residual-only patches from homogeneous ROIs after denoising. Transplant artifacts are gated by the sham arm and by evidence-channel invariance checks (bounded per-voxel HU deltas; perfusion maps untouched -- edits apply to image inputs only). Site-versus-vendor attribution is NOT attempted: with two centers, fleet and site are one variable; the claim wording is 'site fingerprint', never 'scanner model'. Labels never enter the primary paired readout.",
  "alternative_explanations": [
    "The model responds to any high-frequency perturbation, not the site signature -- the equal-energy spectrally-neutral sham and the dose-response monotonicity discriminate.",
    "Decodability exists in raw data but not in model-facing derivative data -- this is the stage-0 gate, not a post-hoc excuse.",
    "A positive response reflects general noise-level sensitivity (dose/kernel) rather than site identity -- the blend is toward the other site's measured spectrum at matched total energy, and the classifier-flip manipulation check ties the dose axis to site identity specifically."
  ],
  "anticipated_negative": "After the decodability gate passes, a null is decisive and reassuring: the fingerprint is readable in the inputs, yet the model's forecasts do not move with it -- direct evidence against the site-shortcut concern for this model family on this benchmark. Before the gate, the candidate dies cheaply rather than yielding an uninterpretable null.",
  "cross_domain": {
    "borrowed_construct": "PRNU sensor-pattern-noise fingerprinting from digital image forensics: every sensor leaves a stable stochastic signature, extractable by denoising residuals, sufficient to identify the source device.",
    "measurement_it_implies": "The wavelet-Wiener noise residual and its power spectrum as a device/site fingerprint, plus a source-identification classifier as the decodability gauge.",
    "what_changes_if_dropped": "Without the forensics instrument there is no principled way to separate the stochastic signature from anatomy; the candidate degrades to generic site-generalization statistics, which is exactly the prior art."
  },
  "remaining_legwork": "Download and decodability census: one session, ~2 days wall clock including Zenodo transfer; spectral-reshaping edit machinery and sham construction: 2 days; use test after the shared model exists: 2 days.",
  "design_template": "other:noise-residual-transplant",
  "design_template_justification": "Closest listed grammars are counterfactual-synthesis (8x concentrated in the portfolio) and regional-substitution (6x); both misdescribe the move: nothing anatomical is synthesized and no region is swapped -- the measured stochastic component of the same real acquisition is spectrally reshaped toward another site's measured statistics, globally, with anatomy untouched. Naming it honestly also keeps the homogenization statistics meaningful.",
  "entry_point_2_requirements": "Measurement: noise-residual site classifier AUC (decodability) and signed paired output change under spectral reshaping (use). Confused artifacts: generic noise-level sensitivity and edit artifacts -- addressed by matched-energy blending, sham permutation, dose-response monotonicity, and the classifier-flip manipulation check.",
  "scores": {
    "clarity": {
      "value": 4,
      "why": "One cue channel, one decodability gate, one within-case intervention with prespecified sham and dose gates; the spectral-reshaping recipe needs preregistration detail."
    },
    "identifiability": {
      "value": 3,
      "why": "The within-case transplant cleanly isolates the noise channel, but with two centers the fingerprint cannot be decomposed into hardware versus protocol components, and edit realism carries residual weight despite the sham gate."
    },
    "medical_relevance": {
      "value": 4,
      "why": "A model that conditions infarct forecasts on where the patient was scanned fails silently at new centers; either finding directly informs multi-center deployment and benchmark interpretation."
    },
    "interest": {
      "value": 4,
      "why": "A stroke model reading the hospital's sensor signature the way forensics reads a camera would surprise both the challenge community and forensics; the gated null is also publishable reassurance."
    },
    "prior_legwork": {
      "value": 4,
      "why": "The forensics instrument, NPS tooling, public two-center data, and the shared audit model plan all exist; only the transplant machinery is new."
    },
    "feasibility": {
      "value": 3,
      "why": "Capped at 3: the decodability keystone on model-facing data is not inspected; conditional on the shared audit model like the baseline cards."
    },
    "data_readiness": {
      "value": 4,
      "why": "Fully public raw plus derivative release; large but hosted download."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "Paired output change is direct, but decodability gates, blend doses, and sham construction are custom and need preregistration."
    },
    "negative_result_value": {
      "value": 3,
      "why": "Interpretable only after the decodability gate; then a genuinely useful negative about a named shortcut channel."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Neighbors found by real search bracket the idea from both sides (forensics detectability, ML confounding) with the use-test gap clear, but the search was targeted, not exhaustive."
    },
    "regret": {
      "value": 4,
      "why": "The decodability census is nearly free, the question is the portfolio's cleanest instance of the site-shortcut concern, and the instrument transfers to every multi-center benchmark the lab touches."
    }
  },
  "priority_score": 3.5,
  "unverified_claims": [
    "site decodability from noise-only patches of derivative model-facing inputs",
    "the two centers' scanner fleets actually differ (hardware is unstated in all inspected sources)",
    "spectral reshaping stays within the audit model's in-distribution envelope (sham-gated but not yet shown)",
    "shared audit model reaches non-trivial performance",
    "novelty beyond targeted search"
  ],
  "plain_pitch": "Every camera leaves an invisible noise signature in its photos -- forensic examiners use it to prove which device took a picture, and CT scanners have the same property. This stroke benchmark mixes patients from two hospitals with different scanners, and where you were treated is itself informative about how you will fare. The question: has the damage-forecasting model quietly learned to read the scanner's signature and adjust its forecast by hospital? The test swaps only the invisible noise signature in a patient's scan toward the other hospital's, touching nothing about the anatomy, and watches whether the forecast moves. If it does, the model is partly forecasting the hospital, not the patient -- which would matter anywhere such a model is deployed at a hospital it never saw in training.",
  "charter": "isles24"
}


===== ideas/037/keystone_screen.md =====
# Keystone screen — idea 037 (isles24-scout-004-c06): The scan remembers which hospital took it

Screen date: 2026-08-18. Charter: isles24.

## The keystone as stated

From `idea_card.json`, `keystone_prerequisite`:

> "Site identity is decodable from noise-only patches of the MODEL-FACING
> derivative inputs (registration and resampling may have attenuated the raw
> fingerprint), and the shared audit model reaches non-trivial held-out
> performance."

This keystone has two parts, and both are **empirical outcomes, not
document facts**: (a) the decodability census is itself the card's Stage 0
experiment, and (b) the shared audit model does not exist yet. No primary
source can settle either by inspection. What a document screen CAN settle
is whether the census is *runnable at all* — and that is where the
wrong-keystone check bites (below).

## Mandatory follow-up: what is the card still assuming?

If the card only verified the nearest checkable things (two-center
composition, raw release), the census still silently assumes:

1. **Per-case site labels are recoverable from the public release.**
   Without a case-to-center mapping there is nothing to train the
   Munich-vs-Zurich classifier against and no way to score it — the entire
   Stage 0 census is impossible, decodability true or not. The card never
   lists this as an assumption. This is the load-bearing checkable
   keystone, and I verified it.
2. Both raw (original-space) and derivative (model-facing) images are in
   the release, per case.
3. The two centers' scanner fleets differ (card flags this as assumed, not
   known).

## What I inspected

### 1. Per-case site labels — VERIFIED TRUE (the hidden keystone)

Dataset descriptor paper, arXiv 2408.11142v2 (PDF fetched and text
extracted 2026-08-18), section *Data Records — Folder structure*:

> "An info sheet, included with our data in the repository, defines the
> clinical baseline and outcome parameters. **It also lists all cases with
> their respective originating centers and the sets they are assigned
> to.**"

And *Data Records — Data structure*:

> "The train set contains n = 99 scans from Center 1 and n = 50 cases from
> Center 2 and is publicly available."

Center identities are named in *Methods — Image acquisition*:

> "Healthcare professionals obtained images as part of the clinical imaging
> routine for stroke patients at two stroke centers in Germany and
> Switzerland: Center 1 - University Hospital of the Technical University
> of Munich in Munich, Germany, and Center 2 - University Hospital of
> Zurich in Zurich, Switzerland."

The case-to-center mapping is disclosed by design, in the repository
itself. The census can be trained and scored.

### 2. Raw + derivative release — VERIFIED TRUE

Same paper, *Methods — Data pre-processing*:

> "All images are released 'raw' (i.e., solely anonymized and defaced) and
> preprocessed (i.e., resampled and co-registered to the NCCT space)."

Zenodo record 16731717 (v3, 2025-08-12, train.7z 99.0 GB, 149 cases,
fetched 2026-08-18) confirms on the release page itself:

> "Raw_data refers to the 'raw' acquired scans, which are released in their
> original space, just defaced."

with derivatives described as "all modalities linearly co-registered to
the NCCT space", and admission imaging comprising "non-contrast CT (NCCT),
CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion
maps (Tmax, CBF, CBV, MTT)". Both the raw arm (fingerprint reference) and
the derivative model-facing arm of the census exist per case.

### 3. Fleet separation — UPGRADED from assumed to source-supported

The card recorded: "vendor/protocol identity was not verifiable from the
papers (neither states scanner hardware, checked this stage), so fleet
separation between the centers is assumed, not known." The dataset
descriptor paper (which the card did not inspect) states, *Methods — Image
acquisition*:

> "CT image acquisition was performed on the following devices: Somatom
> Force, Somatom Xcite (Siemens Healthcare), Somatom AS+ (Siemens),
> Brilliance 64, and Ingenuity (Philips Healthcare)."

> "Stemming from two centers and different scanner models and
> manufacturers, the dataset described here allows the development of
> robust and generalizable stroke lesion segmentation algorithms."

Five CT scanner models across two manufacturers. Caveat, stated honestly:
the paper does **not** map devices to centers, so clean between-center
fleet separation remains source-supported interpretation, not verified
fact. Hardware heterogeneity in the dataset is now verbatim on record;
the census answers the per-center split empirically, exactly as the card
already plans.

### 4. The attenuation threat is real and correctly targeted

*Methods — Data pre-processing*:

> "Data pre-processing consisted of image co-registration to compensate
> for head motion and temporal resampling (1 frame/second) of the 4D CTP
> series."

> "CTA, CTP (including derived perfusion maps), and DWI/ADC scans were
> linearly co-registered to the NCCT space using rigid transformations for
> CT-based images, and affine transformations for MRI."

Also relevant to the census's noise-patch plan: "CT scans were defaced
using in-house developed scripts based on TotalSegmentator" (defacing may
remove some extracranial-air ROIs — the card already anticipates this),
and "Laboratory values and times were randomly altered by ± 5 % for
anonymization purposes" (imaging is untouched by that perturbation). The
resampling/registration attenuation risk the keystone names is exactly
what the released derivative data carries; the question is live, not
settled.

## Discrepancy of record

The card (and challenge paper arXiv 2408.10966: "The train (test) set
contains N = 100 (N = 50) scans from the University Hospital of Munich and
N = 50 (N = 50) scans from the University Hospital of Zurich") says 100
Munich train cases; the dataset descriptor and the Zenodo release say 99
Center 1 train cases / 149 total. One case was evidently dropped between
the challenge design and the public release. Immaterial to the keystone;
the card's cohort numbers should read 149 (99 + 50) for the public train
set.

## Residual assumption check

What remains genuinely unverified after this screen — carried forward, not
resolved:

- **Decodability itself** on model-facing derivative inputs: empirical,
  Stage 0's job by design. Cannot be inspected into truth.
- **Shared audit model performance**: the model does not exist yet;
  conditional dependency shared with the cycle's baseline candidates.
- **Per-center fleet composition**: devices verified, device-to-center
  mapping unstated in every inspected source.
- Whether the released info sheet's center column survives intact inside
  train.7z (the paper says it is there; the 99 GB archive was not
  downloaded at screen prices).

None of these is falsifiable from documents; none is demonstrably false;
the first two are exactly what the card's prespecified Stage 0 gate
exists to test, and the card kills cleanly if the gate fails.

## Verdict

The stated keystone is an empirical census outcome and therefore cannot be
document-verified either way — but every checkable prerequisite for
running that census, including the card's unstated load-bearing assumption
(per-case site labels), verified TRUE with verbatim quotes, and one card
assumption (hardware heterogeneity) was upgraded from assumed to
source-supported. Nothing false was found. Honest verdict: UNVERIFIABLE,
passing the idea onward with the empirical gate intact and the census
confirmed runnable.

```json
{"verdict": "UNVERIFIABLE", "evidence": "An info sheet, included with our data in the repository, defines the clinical baseline and outcome parameters. It also lists all cases with their respective originating centers and the sets they are assigned to.", "source": "arXiv 2408.11142v2 (ISLES 2024 dataset descriptor), Data Records - Folder structure; corroborated by Zenodo record 16731717", "note": "Keystone is an empirical Stage-0 census by design; all checkable prerequisites verified true, including the unstated one (per-case center labels are released), so the census is runnable and the gate is live."}
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
