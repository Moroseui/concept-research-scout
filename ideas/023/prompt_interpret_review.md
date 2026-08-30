You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/023
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


===== evidence/ledger_digest_isles24.md =====
# Ledger digest -- charter: isles24 (auto-generated; scores are scoped to this charter only)

65 tracked ideas in this charter. Latest state per idea; full history in ledger.jsonl.

Work under other charters: evidence/cross_charter_index.md (facts, no scores).

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **IDENTIFIABILITY_FAILURE** x12: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
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
- **idea-023** [SHORTLISTED/PROBED/wide] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
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
- **idea-044** [REJECTED/DEBATED/baseline] -- The old stroke inside the new forecast -- killed: IDENTIFIABILITY_FAILURE
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

## idea-042 [SHORTLISTED] -- Delay is not dispersion

**Verdict:** **REVISE.** The debate repaired two concrete identifiability failures, but the final rebuttal introduced an unverified load-bearing assertion: that the admissible same-case curve family is effectively one-dimensional after arrival, area, and peak are fixed, so all remaining descriptor changes are manifestations of dispersion rather than operator-specific alternatives. Before deciding, the human should look most closely at whether an empirical, model-blind manifold and alternative-operator test is sufficient to operationalize “dispersion”; that decision determines whether this remains idea 042 or must become a narrower operator-specific successor.

**Unresolved:** Does the common-support edit identify physiological dispersion or only sensitivity to one reshaping operator?; Is the common-support subset large and stable enough for a confirmatory experiment?; Can the required physical-family constraint be justified rather than assumed?

## idea-041 [SHORTLISTED] -- The roughness of a heartbeat through starved tissue

**Verdict:** **REVISE.** The final amendment is responsive to the critic's source-ground-truth requirement, but it arrived after three rounds, was not reviewed by the critic, is absent from the card, and changes the project from a small erasure probe into a multi-stage phantom-validation program. The single most important thing the human should inspect is whether source recovery in the proposed Kudo/Manniesing C0 design, followed by explicitly regime-limited transport to patient support, is enough to justify the words “tissue-flow signal”; if not, this card should stop and any roughness-dependence study must enter as a successor.

**Unresolved:** Does the proposed phantom validation make Arm C a valid physiological source-selectivity test?; Can a phantom-validated generator be transported to processed ISLES'24 patient curves?; Are the required phantom assets and uses obtainable?; Can the full gate stack be passed within an honest resource envelope?; Does the three-repair history warrant one more pipeline stage?

## idea-040 [PAUSED] -- The pressure history written in a winding artery

**Verdict:** **PAUSE.** The single most important thing the human should inspect is whether a volume-preserving common-warp equivariance protocol can be made genuinely selective: after every spatial channel is warped together and the output is inverse-warped, can TI-changing and TI-neutral deformation families be matched closely enough that tortuosity is the only systematic model-visible difference? If not, this idea has no positive test inside the available design and the observational screens should not be allowed to substitute for one.

**Unresolved:** Can a common-warp equivariance design isolate tortuosity use?; Is there an obtainable natural paired design that changes tortuosity selectively?; Should the two kill-only observational screens be run while the causal arm is paused?

## idea-039 [SHORTLISTED] -- Does map inconsistency change what a stroke model trusts?

**Verdict:** **REVISE.** The final amendment is a plausible repair, but it has not been challenged or accepted by the critic and has not been incorporated into the idea card. Before deciding, the human should look most closely at an independent algebraic counterexample review of the complete role-disjoint, r-preserving factorial: can any residual-blind multichannel surrogate still pass every proposed carrier, sign, sham, and set-point gate?

**Unresolved:** Does the round-three compensated factorial identify functional use of the residual as a confidence signal?; Can the released maps support a nontrivial residual and the full edited-cell inventory?; Are the jointly edited cells realistic enough for causal interpretation?; Is a usable surrogate obtainable and demonstrably reliant on the linked channels?; Does the rebuilt study remain worth its cost a

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


===== ideas/023/README.md =====
# Idea 023: Little's law in the penumbra: the model may be reading the vasodilatory counterattack

Selected from scouting cycle isles24-002, candidate 7.


===== ideas/023/consensus.md =====
# Debate summary — idea 023

## Agreed

- The original card named an executability fact as its keystone when the load-bearing interpretability fact is whether final-infarct labels contain a compensation-state signal at matched CBF. In round 2 the critic explicitly accepted the proposer's round-1 repair: K2 becomes the real, `NOT_INSPECTED` keystone; a frozen, patient-clustered outcome census precedes model work; feasibility is capped at 3; and both salvageability wording and a decisive toggle null are conditional on that census passing.
- The model-free census must assess adequate within-patient joint support, precision and directional consistency across matched-rCBF strata, and account for released reperfusion or treatment variables where available. Cases used to estimate the label relationship must be separated from the later toggle-evaluation cases. Both sides accepted this in rounds 1–2.
- A compensated-to-collapsed joint CBV/MTT edit cannot distinguish an autoregulatory-reserve reader from a generic monotone low-CBV reader: both predict the same sign. It can distinguish either from a model that ignores the state, and it gives the opposite prediction from a monotone long-MTT severity reader. The proposer conceded this in round 2, and the critic accepted that concession in round 3.
- When the released maps obey the central-volume identity, CBV and MTT at fixed CBF are one degree of freedom. The study therefore cannot attribute an effect to the CBV channel rather than the MTT channel. Both sides accepted an explicit prohibited conclusion to that effect in rounds 2–3.
- An above-mirror arm needs native empirical support, separate in-distribution checks, physiologic-range bounds, and a prespecified response-shape analysis. If that support gate fails, the current candidate must pause rather than silently narrow to a joint-channel-state claim; that weaker deliverable would be a successor. This was proposed in round 2 and accepted by the critic in round 3.
- Mirror-normal CBV is a reference, not an established physiological ceiling. A kink fixed at `rCBV_mirror = 1` cannot identify reserve use. The proposer conceded this in round 3 and replaced the assumed boundary with a proposed outcome-estimated change point.
- The claim is about a joint compensation state, not whether autoregulatory dilation or collateral inflow produced it. Scanner, site, protocol, positioning, and global injection or cardiac-output scaling are addressed principally by within-case edits and mirror ratios; label provenance is not the dominant failure mode here.
- The queueing/control-engineering analogy is not necessary to the experiment. The measurable mechanism survives in classical autoregulatory and central-volume terminology; the revision should remove decorative Little's-law language rather than treat it as evidence.

## Unresolved

### Does an outcome-derived change point identify autoregulatory reserve rather than a learned nonlinear map pattern?

- **Question:** If a change point in final-infarct risk versus `rCBV_mirror` is estimated in matched-rCBF strata and the model's edited response changes near the same point, is that sufficient to call the model-used signal “autoregulatory blood-volume reserve”?
- **Proposer's position:** Yes, conditionally. Round 3 replaces the assumed kink at 1 with a frozen, patient-clustered G-shape analysis comparing a change-point model with flexible monotone alternatives. The model probe would then test agreement in response shape and change-point location on held-out cases. A construct reader should break near the outcome-derived point, a density/calibration artifact near the support boundary, and a monotone reader nowhere. If the outcome change point and support boundary are inseparable, the study exits as indeterminate.
- **Critic's position:** The last stated critic position, before this amendment, is that neither flattening nor continuation uniquely identifies reserve without independent evidence for the physiological response shape. The critic allowed an outcome-derived shape as one possible repair, but did not respond to the proposer's implementation. It therefore remains unresolved whether same-cohort outcome anchoring satisfies the critic or merely shows that the model learned a nonlinear relationship present in its training target.
- **Evidence that would settle it:** First, a frozen Stage 0 result showing a precise, patient-clustered outcome change point at matched CBF, adequate support on both sides, separation from the empirical support edge, and robustness to available reperfusion/treatment variables. Second, critic or human review must decide whether that cohort-outcome landmark is an independently justified physiological endpoint or only a label-distribution feature. Stronger settlement would come from primary-source or independent-cohort replication of the same shape, or from a separately measured autoregulatory endpoint. If the program requires physiology independent of the training labels, no same-cohort analysis alone can settle it.

### Is the revised deliverable still the same claim?

- **Question:** Does redefining “reserve” as a cohort-specific, outcome-supported ceiling preserve the original deliverable sentence, or cross the claim-identity boundary?
- **Proposer's position:** It preserves identity because the question and sentence remain about blood-volume reserve read against CBF; only an assumed boundary has been replaced by a measured one. The proposer nevertheless acknowledges that the claim is now cohort-anchored rather than universal.
- **Critic's position:** In round 3 the critic said an externally or independently supported outcome/autoregulatory shape could preserve the original question, but did not assess the final same-cohort amendment. Earlier rounds agreed that adding the label gate and a valid saturation discriminator did not itself change identity.
- **Evidence that would settle it:** This is principally a governance judgment, not an empirical fact. The human must decide whether “autoregulatory reserve” may be operationalized by the training cohort's outcome curve. Independent physiological validation would reduce the judgment call but cannot eliminate the need to apply the claim-identity rule.

### Are the necessary Stage 0 conditions present in ISLES'24?

- **Question:** Do the 149 cases provide adequate within-patient matched-rCBF support, an estimable outcome shape, native above-mirror coverage away from the support boundary, usable mirror geometry, compatible grids, and clinical covariates sufficient for the intended interpretation?
- **Proposer's position:** These are measurable CPU-first gates, not assumptions. Failure of G-label, G-hyper, or G-shape pauses this candidate; coincidence of the outcome change point with the support boundary yields an indeterminate exit.
- **Critic's position:** These facts must be directly established before model training or a decisive-negative interpretation. The critic has not accepted any of them as presently true.
- **Evidence that would settle it:** A version- and hash-pinned header/schema census followed by the preregistered patient-clustered Stage 0 analyses, with minimum-support and precision criteria fixed before inspecting outcomes. This evidence does not yet exist in the debate record.

### Whose model can support the eventual wording?

- **Question:** Can the study speak about benchmark models if it probes only a self-trained map-input nnU-Net?
- **Proposer's position:** The proposed machinery assumes a self-trained model, with a Stage 0 inventory for any released challenge weights and maps-only plus multimodal configurations.
- **Critic's position:** Claims and negatives must be scoped to the actual trained model family and recipe unless a released submission is found; multimodal dominance can make a weak toggle response ambiguous.
- **Evidence that would settle it:** An inspected inventory of participant repositories and weights, a frozen input-channel specification, and successful reproduction of the intended model family. Without released challenge weights, only model-family-scoped language is supportable.

## Positions that moved

- **Proposer, round 1:** Conceded that the stated co-registration keystone was adjacent rather than load-bearing. This moved in response to the critic's argument that label-outcome structure gates both salvageability interpretation and negative-result decisiveness. The proposer adopted K2, G-label, split separation, conditional negative interpretation, and the feasibility cap. Earned concession.
- **Critic, round 2:** Accepted the round-1 keystone repair and the claim-identity rationale. This moved because the proposer supplied concrete gates, scoring changes, and failure consequences. Earned concession.
- **Proposer, round 2:** Conceded that the bidirectional basic toggle does not distinguish reserve from monotone CBV use and that CBV-versus-MTT channel attribution is impossible under the identity. This moved in response to the critic's explicit sign analysis. The proposer added G-hyper, a confirmatory above-mirror arm, prohibited conclusions, and reduced identifiability to 3 pending the gate. Earned concession.
- **Critic, round 3:** Accepted the channel-degeneracy limit, confirmatory status of the above-mirror arm, and pause/successor consequence if G-hyper fails. This moved because the proposer made those constraints explicit. Earned concession.
- **Proposer, round 3:** Conceded that a kink at mirror-normal had been assumed rather than measured. This moved in response to the critic's demonstration that true reserve use may continue above 1 and generic nonlinear channel use may flatten there. The proposer replaced it with G-shape and a shape/location comparison. Earned concession.
- No concession in the transcript is UNEARNED. The final round-3 amendment remains unaccepted because the critic had no subsequent turn; it must not be recorded as consensus.

## Amendments made

At round zero, the card claimed that a two-sided, mirror-referenced, manifold-preserving CBV/MTT toggle at fixed CBF could identify use of autoregulatory reserve; treated map co-registration as the inspected keystone; fixed compensation at mirror-normal; described a gated null as decisive; attributed the finding broadly to benchmark models; and presented the experiment as cheap and near-ready.

The debated version instead proposes:

- K2, not map coexistence, as the load-bearing `NOT_INSPECTED` keystone: outcome must encode a compensation-state relationship at matched CBF.
- A frozen CPU-first G-label/G-shape census with patient clustering, joint-support and precision requirements, treatment/reperfusion handling where possible, and separation from held-out toggle cases.
- A continuous outcome-response model that estimates any change point rather than assuming one at `rCBV_mirror = 1`.
- G-hyper and separate in-distribution validity for above-mirror edits, plus an explicit indeterminacy exit when the outcome landmark and support boundary cannot be separated.
- A confirmatory model response-shape/location comparison, with the slope contrast secondary, rather than treating the sign of the basic toggle as construct-specific.
- Explicit prohibition of CBV-versus-MTT channel attribution and model-family-scoped wording unless released challenge weights are found.
- Removal of the Little's-law/control analogy from the evidentiary logic.

What was lost is substantial: feasibility and identifiability fall to 3 pending unrun gates; decisive-negative value is conditional; the simple two-sided toggle no longer identifies the construct; the claim becomes cohort-anchored; at least three Stage 0 death paths and one indeterminacy exit now precede the full probe; the cheapest-candidate claim no longer holds; and a failure may require a separately registered weaker successor. The current `idea_card.json` contains none of these amendments and is materially stale.

## Recommendation

**REVISE.** Rewrite the card to the fully gated, cohort-anchored design before any feasibility memo or model work. The single most important thing for the human to examine is whether matching a model's edit-response change point to a change point estimated from its own training cohort's outcomes is sufficient evidence for the physician-legible phrase “autoregulatory blood-volume reserve,” or whether independent physiological validation is required. That decision controls both claim identity and whether G-shape can ever reach rung 3.

```json
{"verdict": "REVISE", "unblock": "Rewrite the card with K2, G-label/G-shape, G-hyper, support-boundary indeterminacy, channel-attribution limits, and model-family scope, then obtain human agreement that the outcome-derived shape can validly operationalize autoregulatory reserve before Stage 0."}
```


===== ideas/023/critique.md =====
# Critique — Idea 023 (isles24-scout-002-c07): Little's law in the penumbra

```
FATAL OBJECTION: NONE
EVIDENCE: ISLES'24 report arXiv:2408.10966 (maps from icobrain cva tracer-kinetics
deconvolution); Zenodo 16731717/16813698; winning-solution paper arXiv:2505.18424
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

No single objection kills this card. But three repairs are mandatory before a
feasibility memo, and one of them (the CBV/MTT degeneracy, §2) quietly narrows
what the deliverable sentence is allowed to mean. The card is unusually honest
about its residual assumptions; the problems below are the ones it did not list.

---

## 1. What I verified (sources checked this stage)

- **Map provenance.** The ISLES'24 report states CTP preprocessing used the
  FDA-cleared clinical software **icobrain cva**: motion correction, temporal
  resampling to 1 frame/s, then perfusion maps "generated using a conventional
  tracer-kinetics deconvolution algorithm" (arXiv:2408.10966). This is the fact
  that drives §2 below. The card never asks how the maps were made; it should.
- **Dataset schema.** Confirmed independently of the keystone screen: the Zenodo
  release contains 149 training cases with per-case Tmax/CBF/CBV/MTT derivatives
  co-registered to NCCT space, CC BY-NC-SA 4.0. **Version churn exists**: the
  record the keystone screen inspected (16731717) is one of several versions;
  16813698 is "v3" (2025-08-12) and itself points to a newer version. Schema is
  stable across the two versions inspected, so the keystone stands, but the
  record/version and file hashes must be pinned at Stage 0.
- **Winning solution.** arXiv:2505.18424: a residual-encoder nnU-Net with
  SynthStrip skull-stripping and custom intensity windowing. The paper does not
  state its exact input-channel configuration and releases no code or checkpoint
  I could find. The card's "self-trained nnU-Net stands in" assumption is
  therefore load-bearing (§4).
- **Prior work / novelty.** The counterfactual literature in this niche perturbs
  *clinical/treatment* variables (Robben et al. 2020, PMID 31683091; Amador et
  al., ScienceDirect S1532046423002885) or ablates whole input channels. I found
  no work that toggles the physiological state jointly encoded by the perfusion
  maps while preserving inter-map consistency. The novelty delta survives this
  critique. Amador's clinical-counterfactual line should be added to
  `novelty_neighbors` as the nearest methodological relative.

## 2. Principal objection: at fixed CBF, CBV and MTT are one channel, not two

A conventional tracer-kinetics deconvolution pipeline derives MTT from the
central volume theorem — MTT := CBV/CBF is typically an algebraic step of the
software, not an independent measurement. icobrain cva's internals are
proprietary, so Stage 0's identity-residual census is the right check, but the
card must face the dilemma it creates, because **both horns cost something**:

- **If the residual is ~0 (identity holds by construction):** the "Little's-law
  identity" is a tautology of the vendor pipeline, not a physiological manifold.
  Two consequences. (a) The "does the model check inter-map consistency" probe
  loses its physiological framing — it is a pure never-seen-input OOD probe
  (idea-006 shape; the card correctly quarantines it, but the "does the model
  know Little's law" interest hook deflates to nothing). (b) More important: the
  confirmatory co-edit moves CBV and MTT **in lockstep at fixed CBF — they carry
  identical information**. A positive result cannot attribute the response to
  "blood volume held up" versus "transit time prolonged." The deliverable
  sentence names the *blood-volume* reserve; the experiment can only ever
  establish use of the *compensation state* (the joint CBV/MTT configuration at
  matched flow deficit). These coincide physiologically but not as
  channel-attribution claims, and a reviewer will read the current sentence as
  the latter.
- **If the residual is large:** the maps do not live on the claimed manifold,
  the co-scaling rule is wrong, and the card's own fallback (edit along the
  empirical joint distribution) applies — which is fine, but then the entire
  Little's-law apparatus contributed nothing (see §6).

**Repair (within the same question):** keep the sentence's own definition —
"capillary volume held at or above mirror-normal while flow falls" is a *state*
description and can stand — but add an explicit prohibited-conclusion: no claim
that the model reads the CBV channel as opposed to the MTT channel; at matched
CBF they are not separable in principle when the identity holds. This is wording
honesty, not a new deliverable, so the claim-identity rule is not triggered.

## 3. The two-sided discriminator is under-designed for its main job

Alternative explanation 1 (the card's own) is the crux: reserve-construct reader
vs. generic monotone-CBV-severity reader. Work the signs through:

- Toggle compensated→collapsed (CBV↓, MTT↓, CBF and Tmax fixed): the construct
  reader predicts infarct probability **rises**. A monotone "low CBV = bad"
  channel reader predicts it **rises too**. Same sign. The toggles as listed in
  `smallest_decisive_experiment` (compensated↔collapsed at three magnitudes)
  therefore do **not** separate the two hypotheses — they separate both from
  "ignores CBV/MTT entirely."
- The separation the card gestures at ("including above-mirror values") requires
  an **explicit above-mirror arm**: push CBV *above* mirror-level at matched
  CBF. The construct reader predicts saturation (already compensated; no further
  benefit), the monotone reader predicts a continued response. That arm is
  mentioned in the alternatives list but absent from the experiment description,
  and it is the only part of the design that earns the word "construct" in the
  deliverable. It is also the arm with the weakest physiological cover story
  (post-ischemic hyperperfusion does occur in infarcted tissue) and the greatest
  OOD risk, so it needs its own empirical-support gate in Stage 0.
- One incidental gain: a monotone-MTT-severity reader ("long MTT = bad")
  predicts the *opposite* sign under the joint toggle, so the basic arm does
  falsify that particular generic reader. Worth stating — it is the one clean
  discrimination the basic toggles do achieve.

**Repair:** promote the above-mirror saturation arm into the confirmatory
design with a prespecified dose-response shape readout (response flattens above
rCBV_mirror = 1 vs. continues), or demote the claim from "uses the reserve
construct" to "uses the compensation state," which is still a finding but a
smaller one. Identifiability at 4 is not defensible until one of these happens;
as written it is a 3.

## 4. The missing Stage 0 gate: does the *label* even carry the interaction?

The card's premise is that "every training case showed the model the
consequence" of the compensated/collapsed difference. That is an assumption
about the ground truth, and it is checkable on CPU before any model exists: at
matched CBF decrement, do final-infarct membership rates actually differ
between compensated and collapsed voxels in the 149 released cases? This is
simultaneously (a) a re-litigation of Wintermark-vs-Campbell on a modern,
reperfusion-treated cohort — a citable side result on its own — and (b) the
precondition for the whole study: **if the labels do not encode the state's
prognostic value at matched CBF, the toggle null is preordained and
uninterpretable as a model finding.** Two aggravating factors make this gate
non-optional: the cohort is all-treated with heterogeneous reperfusion success
(penumbra fate is partly stochastic from the image alone), and n=149. Add it to
Stage 0 alongside the identity-residual and joint-support censuses. The
`anticipated_negative` classification ("decisive") is conditional on this gate
passing and should say so.

## 5. Scope honesty: whose model is being audited?

The deliverable and the anticipated negative speak of "the final-infarct model"
and "what benchmark models internalized." What will actually be probed is a
self-trained nnU-Net, because no challenge checkpoint is confirmed released
(§1). Three consequences:

1. The quotable-negative claim ("siding with the rCBF camp") must be scoped to
   *this model family under this training recipe*, not "benchmark models."
2. The shared-model input specification is silently load-bearing: the edits
   enter through the perfusion-map channels, so the cycle-shared model **must**
   take the four maps as inputs. A raw-4D-CTP model (Amador-style) or an
   NCCT/CTA-dominant model gives the probe no port of entry. This is
   controllable (we train it) but must be prespecified, and it couples c07 to
   every other candidate sharing that checkpoint.
3. With a multimodal input (NCCT+CTA+maps), a weak toggle response is ambiguous
   between "ignores the state" and "NCCT evidence dominates" — established
   hypodensity on NCCT will rationally cap how far a CBV edit can move the
   prediction. Cheap fix, worth adopting: train the maps-only configuration as
   well and run the probe on both; divergence between them is itself
   informative. The Tmax positive control calibrates channel sensitivity but
   not cross-channel dominance.

Stage 0 should also inventory released ISLES'24 participant repositories
(e.g., the official docker template, kimberly-amador/ISLES24-PrediCTP,
Mahsa0M/isles2024_docker) for released *weights*; if any trained submission is
public, probing it alongside the self-trained model materially strengthens the
"benchmark" framing at near-zero cost.

## 6. Analogy audit (charter test: what changes if dropped?)

The card's own answer is half-right. The two-sided deviation-from-mirror
prediction is genuinely load-bearing — but it comes from classical stroke
physiology (Wintermark's autoregulation account), not from control engineering.
Little's law adds nothing beyond the central volume principle, which the CTP
literature has cited under that name since the 1990s; and if §2's first horn
holds, the "manifold constraint" it supplies is the vendor pipeline's algebra.
The experiment would be identical with the queueing/control vocabulary deleted
and "autoregulatory compensation (Wintermark 2006) vs. flow-only (Campbell
2011)" put in its place. This is decoration on top of a real mechanism, not
fluent nonsense — the named quantity and measurement survive the deletion — so
the charter's remedy is rewrite-without-analogy, not discard. The revision
should do that; it will also make the card more legible to the stroke-imaging
reviewer the deliverable sentence is aimed at.

## 7. Kill-attempts that failed (recorded so they are not re-run)

- **Prior-work overlap:** searched; nearest neighbors are channel ablations and
  clinical-variable counterfactuals; no consistency-preserving state toggle
  found (§1). Novelty delta stands.
- **Circularity (idea-010 shape):** X is computed from the model's inputs, but
  the endpoint is output change under input intervention, not a re-encoding of
  the input. Not circular.
- **Label leakage:** ground truth from follow-up MRI; inputs are acute-phase
  only. No path.
- **Annotation provenance:** primary readout is label-free paired deltas; the
  GT enters only through the §4 gate and training, both with documented
  provenance (DOI 10.1148/ryai.250603). The dominant program failure mode does
  not apply.
- **Confounding (scanner/protocol/site):** within-case paired edits hold all of
  it fixed; the mirror ratio kills global scaling. The card's treatment is
  correct.
- **Excessive compute:** ~320 forward passes is trivial; the real costs are the
  one-time ~100 GB archive download (the 99 GB train.7z is monolithic — check
  at Stage 0 whether derivatives can be fetched separately) and the shared
  nnU-Net training, which is a cycle-level cost amortized across the ISLES
  candidates but should stop being invisible in this card's "cheapest wide
  candidate" claim.
- **Unavailable data:** public, CC BY-NC-SA 4.0, no DUA. Fine for this program.
- **idea-016 and idea-006 resemblance:** the card's `dies_like_prior` answers
  are adequate; the mirror ratio and empirical-range bounds are real structural
  differences, and the OOD-flavored identity-violating probe is quarantined.

## 8. Easier versions (low-hanging fruit, in ascending cost)

1. **Model-free, CPU-only (§4 gate as a result):** the GT-interaction census on
   149 cases. Data and labels already exist; no training. If it fails, the
   candidate dies for ~zero cost; if it passes, it is a citable observation
   about the Wintermark/Campbell debate in a treated cohort either way.
2. **Observational stratification (no edits):** once the shared model exists,
   compare its predicted-infarct probability for compensated vs. collapsed
   voxels at matched CBF. Confounded (state correlates with everything), so it
   cannot replace the toggles, but it costs one inference pass over held-out
   cases and yields the effect-size estimate the toggle arm needs for power.
3. **Released-submission probe:** if the Stage 0 checkpoint inventory (§5)
   finds any public trained ISLES'24 submission, run arms 1–2 on it before
   training anything.

These are stages of the same candidate, not separate candidates.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does a map-input final-infarct model
trained on ISLES'24 respond to the autoregulatory compensation state — the
joint CBV/MTT configuration at matched CBF decrement, with an explicit
above-mirror saturation arm — and does the cohort's ground truth even encode
that state's prognostic value at matched flow?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — same deliverable sentence, narrowed
attribution; revision-in-place under the claim-identity rule.
IS IT ACTUALLY WORTH DOING? YES — the §8.1 census alone is worth running this
week on existing public data, and it decides for free whether the rest deserves
GPU time; the full study is worth doing only conditional on that gate.
```


===== ideas/023/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The card names the wrong keystone: co-registered maps make the experiment executable, but the study is uninterpretable unless ISLES'24 final-infarct labels actually encode a prognostic difference between compensated and collapsed tissue at matched CBF deficit.

**Argument:** The claimed mechanism is learned use of an autoregulatory compensation state for tissue salvageability. Yet the 149-case cohort is reperfusion-treated, and final infarct depends on treatment timing and success as well as baseline perfusion; map availability does not establish that voxels with rCBV at or above mirror-normal have different final-infarct membership from low-rCBV voxels after matching on rCBF. If that conditional association is absent, a null toggle response cannot be called a decisive finding that the model “sides with the rCBF camp”: the training target supplied no detectable compensation-state lesson, so failure to learn it is preordained or sensitivity-limited. Conversely, a positive toggle response could reflect a model exploiting a channel pattern without that pattern being outcome-relevant in this cohort. This is the charter's wrong-keystone error: the inspected adjacent fact is that all maps coexist in NCCT space; the load-bearing fact is that the outcome supports the interaction the deliverable attributes to salvageability. The repair remains the original question and does not trigger a claim-identity change: before model training or edits, prespecify a patient-clustered, held-out model-free census testing final-infarct risk across compensated versus collapsed states within matched-rCBF strata, with treatment/reperfusion variables handled if released, an effect-size precision requirement, and a minimum joint-support gate. Until that passes, the proposed negative is not decisive and `negative_result_value` cannot remain 4.

**What would change my mind:** Show a frozen Stage 0 analysis plan and results on the released ISLES'24 cases demonstrating adequate joint support and a precisely estimated, directionally consistent difference in final-infarct membership between compensated and collapsed voxels at matched rCBF, robust to patient clustering and available reperfusion/treatment covariates; or narrow the claim to model use of an input-map state without calling it a salvageability signal, which would be a different candidate under the claim-identity rule.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card verified the executability fact (four maps coexist in NCCT space) but the load-bearing fact is different: unless the released final-infarct labels themselves show, at matched rCBF decrement, a prognostic difference between compensated and collapsed voxels, the toggle experiment is uninterpretable — the "decisive" negative is preordained, and `negative_result_value: 4` and `keystone_status: INSPECTED_TRUE` overstate the card's position.

**Response:** AMEND

**Argument:** The objection is substantially correct and I adopt its repair in full; critique §4 identified the same missing gate independently, so this amendment discharges both. One narrow point is rebutted at the end.

What changes in the card, exactly:

1. **The keystone is split into two named parts.** K1 (executability): per-case CBV/CBF/MTT/Tmax maps co-registered in NCCT space — remains `INSPECTED_TRUE` on the Zenodo/GitHub schema evidence. K2 (interpretability, the load-bearing one the critic names): *final-infarct membership differs, directionally and with adequate precision, between compensated (rCBV_mirror ≥ 1) and collapsed (rCBV_mirror < 1) voxels within matched rCBF-decrement strata in the released 149-case cohort.* K2 becomes the card's `keystone_prerequisite`; its status is `NOT_INSPECTED`. Per the charter's caps, **feasibility drops 4 → 3** until K2 is measured. The mitigating fact — and the reason this is an amendment rather than a concession — is that K2 is directly measurable on CPU from released public data with no annotator, before any training or download of model machinery. This is the rare instance where the wrong-keystone trap is escapable by measurement rather than by assumption, and the card should have said so itself.

2. **A prespecified, frozen Stage 0 gate (G-label) is added ahead of all model work.** Frozen before any voxel of the label data is examined: (a) prespecified rCBF_mirror-decrement bins; (b) within each bin, compare final-infarct membership rates for compensated vs. collapsed voxels; (c) patient-clustered inference (cluster bootstrap over the 149 patients), never pooled-voxel CIs; (d) a minimum joint-support requirement — at least N patients each contributing at least M voxels of *both* states within the same bin, N and M fixed in the frozen plan before data touch; (e) a precision requirement on the stratum-wise risk difference (maximum CI width), not merely a significance test; (f) directional consistency across bins; (g) a prior inventory of released clinical variables — if reperfusion status (e.g., mTICI) or treatment-timing fields are in the release, the census stratifies or adjusts on them; if they are absent, that absence is recorded as a scope limit on the salvageability wording, not silently ignored. Holding out cases from the census for the later toggle arm (the critic's "held-out" condition) is adopted: the census freezes on a split, and the toggle arm's 40 cases come from the complement.

3. **Consequences are reclassified as conditional.** `anticipated_negative` = decisive holds **only conditional on G-label passing**; the card now says so in the field itself. If G-label fails, the toggle experiment is not run, the candidate PAUSEs, and the census result stands alone as the deliverable — which has independent worth either way: it is a direct re-litigation of the Wintermark-2006 vs. Campbell-2011 core-definition debate on a modern, reperfusion-treated cohort, a citable observation under the charter's "evidence that a popular assumption is unsupported" success class. `negative_result_value` stays 4 only as a conditional score with the condition printed in the `why`; unconditionally it is the census, not the toggle null, that carries guaranteed value.

4. **What was lost.** This is not free. The negative's decisiveness is now conditional rather than intrinsic; feasibility drops a point until Stage 0 runs; the "cheapest wide candidate this cycle" claim must absorb a mandatory CPU census and the ~100 GB archive download earlier in the critical path; and there is now a named, prespecified way for the candidate to die before any model exists. I consider that last item a feature, but it is honestly a narrowing of what the card promised.

**Partial rebuttal — the positive arm.** The critic writes that a positive toggle response "could reflect a model exploiting a channel pattern without that pattern being outcome-relevant in this cohort," implying the positive is also hostage to K2. Half of that is right and already handled: the salvageability *wording* of the deliverable sentence is conditional on G-label, and with the §2 critique repair the confirmatory claim is about the compensation *state*, with channel-level attribution prohibited. But the rung-1 content of a positive — *this model's output responds, signed and paired, to the compensation state at matched CBF* — is a fact about the model that no property of the labels can retroactively falsify. If G-label failed and a toggle response nonetheless existed, that would be a learned reliance the training target does not support — a shortcut-flavored finding with a different, weaker sentence. The amended design orders the stages so this ambiguity never arises (census first; toggles only on pass), but the asymmetry matters for scoring: K2 gates the *interpretation* and the *negative*, not the existence of the rung-1 positive. That is why the amendment conditions the wording and the negative's classification on G-label rather than making the whole candidate's meaning contingent on it.

**Identity check:** the one-sentence question — is the model using the blood-volume reserve, read against CBF, to separate salvageable from lost tissue — is unchanged; the deliverable sentence is unchanged; the gate is a precondition inserted before the same experiment. The critic's own round states the repair "remains the original question and does not trigger a claim-identity change." Revision-in-place.

**Spin-off (noted, not debated):** if G-label *fails*, the census itself — "in a treated 2024 cohort, the CBV/CBF interaction the pre-2011 literature built core definitions on is absent from final-infarct outcomes" — could re-enter as a standalone model-free candidate.

**Status:** OPEN

## Round 2 — CRITIC

**Position:** The G-label amendment preserves the original question and resolves the keystone objection, but the proposed toggle still cannot distinguish use of an autoregulatory compensation construct from a generic monotone response to CBV/MTT.

**Argument:** I concede Round 1 because the proposer adopted the load-bearing K2, made it `NOT_INSPECTED`, capped feasibility at 3, and conditioned both the salvageability interpretation and decisive-negative claim on a prespecified patient-clustered outcome census; those are substantive arguments and gates, not restatement. The identity check also passes: G-label is a prerequisite for the same question, not a substitute endpoint. The strongest remaining defect is identifiability. In the stated compensated-to-collapsed edit, CBV falls and MTT is co-scaled downward while CBF and Tmax are fixed. Both the claimed construct reader (loss of reserve means greater infarct probability) and a generic monotone low-CBV severity reader predict the same signed increase. Reversing that edit adds no discrimination; it merely reverses both predictions. Because conventional deconvolution may make MTT algebraically dependent on CBV/CBF, the design also cannot attribute the effect to CBV rather than MTT, as the critique already notes. The card gestures toward “including above-mirror values,” but neither the amended Stage 0 plan nor `smallest_decisive_experiment` makes an above-mirror saturation arm confirmatory or gives it an empirical-support gate and a prespecified response-shape contrast. Without that arm, a positive result supports only “the model uses the joint CBV/MTT compensation-state channels at matched CBF,” not the deliverable’s stronger claim that it uses blood-volume reserve as a tissue-salvageability construct. This is not an identity-changing repair: explicitly testing saturation once rCBV reaches mirror-normal directly operationalizes the original reserve question. If that arm is infeasible or unsupported, the weaker channel-state sentence must become a separate successor because it changes the deliverable claim.

**What would change my mind:** Amend the confirmatory design to include an empirically supported above-mirror arm, gated in Stage 0, with a frozen dose-response contrast that distinguishes saturation at rCBV_mirror approximately 1 from a continuing monotone CBV/MTT response, plus the explicit prohibited conclusion that the experiment cannot separate CBV-channel use from MTT-channel use when the central-volume identity holds.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** With the G-label gate settled, the surviving defect is identifiability of the *construct*: the compensated-to-collapsed toggle (and its reverse) produces the same signed prediction from a reserve-construct reader and from a generic monotone low-CBV/short-MTT severity reader, so as designed the confirmatory arm cannot earn the word "reserve." The only discriminating test — saturation of the response above rCBV_mirror ≈ 1 — is currently a gesture in the alternatives list, not a gated confirmatory arm; and when the central-volume identity holds, CBV and MTT carry identical information at fixed CBF, so channel-level attribution is impossible in principle.

**Response:** AMEND

**Argument:** The sign analysis is correct and I will not relitigate it: below mirror level, both hypotheses predict the same direction, and reversing the edit reverses both predictions together. Critique §3 reached the identical conclusion independently. The two-sided toggle separates "uses the CBV/MTT state at matched CBF" from "ignores it," and separates a monotone-MTT reader (which predicts the opposite sign under the joint co-scaled edit — the one clean discrimination the basic arm does achieve, now stated in the card); it does not separate construct from monotone-CBV reader. The amendment adopts the critic's change-my-mind conditions in full, item by item:

1. **The above-mirror saturation arm becomes confirmatory.** Third toggle family, same within-case paired machinery: at matched CBF and Tmax, CBV is moved *above* mirror level (MTT co-scaled to stay on the manifold), in steps spanning the empirically observed above-mirror range in cohort deficit tissue. The frozen, prespecified readout is a **dose-response shape contrast**, not a threshold on any single delta: the construct hypothesis predicts the response flattens at rCBV_mirror ≈ 1 (below-mirror segment slope large, above-mirror segment slope compatible with the sham-derived noise floor); the monotone hypothesis predicts the above-mirror slope continues with the same sign as below. The contrast statistic (ratio of segment slopes with patient-clustered CIs, segments and step grid fixed in advance) is frozen in the probe contract before any model inference. A monotone continuation is itself reportable: "the model treats CBV as unbounded severity, not as a reserve with a ceiling" — a directional finding either way, which is what makes this arm confirmatory rather than exploratory.

2. **The arm gets its own Stage 0 empirical-support gate (G-hyper).** The same CPU census that runs G-label counts, per patient and per rCBF-decrement bin, deficit-tissue voxels with rCBV_mirror > 1 natively present in the cohort (post-ischemic hyperperfusion and luxury-perfusion states make this plausible, but plausibility is not support). Edit bounds are capped at the observed above-mirror quantiles; the discriminator/in-distribution gate applies to this arm separately, because it is the arm with the weakest physiological cover story and the greatest OOD risk. If G-hyper fails — insufficient native above-mirror support at matched CBF — the arm does not run.

3. **The prohibited conclusion is added to the card verbatim.** No claim that the model reads the CBV channel as opposed to the MTT channel: when the released maps satisfy the central-volume identity, CBV and MTT at fixed CBF are one degree of freedom, and the Stage 0 identity-residual census determines whether that degeneracy holds by construction. The deliverable sentence already names a *state* ("capillary volume held at or above mirror-normal while flow falls"), and the card now says explicitly that this is a state claim, never a channel-attribution claim.

4. **Scores follow the design as written, not as promised.** `identifiability` drops 4 → 3 in the card now, with the `why` stating it returns to 4 only if G-hyper passes and the saturation arm runs as confirmatory. This mirrors the feasibility 4 → 3 cap from round 1: the score reflects what has been gated, not what is hoped.

**What was lost.** More than round 1's amendment. (a) The strong claim — "uses the reserve as a construct" — is now hostage to the single most OOD-fragile arm of the design; the card acquires a second named death path (G-hyper) alongside G-label. (b) If G-hyper fails, the candidate cannot silently narrow to "uses the joint CBV/MTT compensation-state channels": the critic is right, and I accept, that this weaker sentence is a *different deliverable* under the claim-identity rule. In that world the candidate PAUSEs and the channel-state question registers as a successor with parent_id, re-entering through a normal cycle — no inherited queue position. That is the honest price: the original question now has two prespecified ways to die before its decisive arm runs, and one of them demotes rather than kills, into a successor I do not get to keep. (c) This is amendment two of two rounds. The standing rule says three amendments usually means the idea was wrong; I note the trajectory. My defense of stopping at two: both amendments installed gates *in front of* the original experiment demanded by two independent reviews (critique §§3–4 and both critic rounds converge on the same repairs); neither changed the question, the deliverable sentence, or the toggle machinery itself. If the next objection requires changing what the sentence claims, the idea was wrong and I will say so.

**Identity check:** the one-sentence question — is the model using the blood-volume reserve, read against CBF, to separate salvageable from lost tissue — is unchanged. The saturation arm does not replace that question; it is the part of the design that finally *operationalizes* the word "reserve" (a reserve is exactly the thing whose marginal value vanishes once replenished — flattening above mirror level is what "reserve" means in prediction space). The critic's own round states this repair is not identity-changing. Revision-in-place.

**Status:** OPEN

## Round 3 — CRITIC

**Position:** The saturation amendment preserves the original question but assumes, rather than establishes, that autoregulatory blood-volume reserve must produce a prediction kink at `rCBV_mirror = 1`, so its confirmatory contrast still does not identify the claimed construct.

**Argument:** Round 2's amendment adequately accepts the channel-degeneracy limit, makes the above-mirror arm confirmatory, and correctly pauses rather than silently changing the deliverable if G-hyper fails; those are substantive repairs, and the identity check passes. The remaining problem is the discriminator's physiological premise. Mirror-normal CBV is a reference value, not a demonstrated ceiling on autoregulatory vasodilation or on the prognostic value of blood volume. The card's own Wintermark framing permits normal-to-*increased* CBV in penumbra, and G-hyper explicitly expects native deficit tissue above 1. A genuine reserve reader could therefore continue changing its output above `rCBV_mirror = 1` because progressively elevated CBV may encode greater vasodilation, collateral filling, delay, or reperfusion state; conversely, a generic nonlinear CBV/MTT reader could flatten near 1 because of training-density saturation or network calibration. Thus the proposed slope ratio has no unique mapping: continuation does not refute construct use, and flattening does not establish it. G-label only tests compensated-versus-collapsed outcome association after dichotomizing at the same assumed boundary, while G-hyper only establishes support, so neither validates the kink prediction. This matters at rung 3: the design can identify use of a nonlinear joint CBV/MTT state at matched CBF, but it cannot call that nonlinearity “autoregulatory reserve” without an independently justified physiological response shape. The amendment therefore operationalizes the original words but not yet the original mechanism.

**What would change my mind:** Show primary-source or independent cohort evidence that, at matched CBF deficit and relevant reperfusion status, tissue outcome or a separately measured autoregulatory endpoint has a prespecified plateau or change point at (or estimably near) mirror-normal CBV; then freeze that externally derived shape before probing the model. Alternatively, measure an independent autoregulatory quantity available in the cases and show that the proposed CBV/MTT dose-response discriminates it from flexible monotone and saturating channel-only baselines. Without one of those facts, the weaker joint-state claim must be a successor candidate.

**Status:** OPEN

## Round 3 — PROPOSER

**Responding to:** The saturation arm's discriminator rests on an *assumed* physiological premise: that reserve use must produce a prediction kink at rCBV_mirror = 1. Mirror-normal is a reference value, not a demonstrated ceiling — the card's own Wintermark framing allows normal-to-increased CBV in penumbra — so a genuine reserve reader may keep responding above 1, while a generic nonlinear reader may flatten near 1 for training-density or calibration reasons. The slope-ratio contrast therefore has no unique mapping to the construct, and neither G-label (which dichotomizes at the same assumed boundary) nor G-hyper (support only) validates the kink.

**Response:** AMEND

**Argument:** The objection is correct and I will not defend the kink-at-1. I asserted in round 2 that "flattening above mirror level is what reserve means in prediction space" — that was the construct's *definition* doing the work an *measurement* should do, the same class of error as the original K1/K2 keystone swap: the easy fact (mirror-normal is a natural reference) stood in for the load-bearing one (the outcome-relevant ceiling, if any, sits at or near that reference in this cohort). The critic's first change-my-mind branch, however, names a repair that stays inside the original question — "tissue outcome ... has a ... change point at (or estimably near) mirror-normal CBV; then freeze that externally derived shape before probing the model" — and the amendment implements exactly that branch, on data already inside the design's critical path.

1. **The assumed boundary is replaced by an estimated one (G-shape).** The G-label census is upgraded from a dichotomous comparison at rCBV_mirror = 1 to a continuous dose-response estimate: within matched rCBF-decrement strata, final-infarct membership as a function of rCBV_mirror, fit with a prespecified change-point model against flexible monotone alternatives, patient-clustered throughout. The dichotomous compensated/collapsed comparison survives as a summary statistic, not the gate. G-shape passes only if the outcome data themselves show a plateau or change point, with a cluster-bootstrap CI on its location c. The frozen referent for the model probe is then the *outcome-derived* shape and location — not rCBV_mirror = 1, and not any value I assume. "Estimably near mirror-normal" is reported, not required: if the outcome ceiling sits at, say, rCBV_mirror ≈ 1.3, that is the reserve ceiling this cohort supports, and the probe tests against it.

2. **The model contrast becomes a shape-and-location match, which is what defuses both of the critic's failure directions.** (a) *Continuation above 1 no longer refutes construct use* — if the outcome curve itself declines past 1 up to c, a reserve reader tracking the outcome-supported construct should too; the probe asks whether the model's dose-response breaks where the outcome's does. (b) *Flattening no longer spuriously confirms it* — training-density saturation predicts flattening at the empirical support boundary (the observed above-mirror quantile where data thins), not at c. G-hyper already measures that boundary, so the design now carries three distinguishable landmark predictions: construct reader breaks near c; density/calibration saturation breaks near the support edge; monotone severity reader breaks nowhere. The frozen statistic is the location of the model's estimated change point (with patient-clustered CI) relative to c and to the support boundary, plus the round-2 slope contrast retained as a secondary. If c and the support boundary coincide in this cohort, the landmarks are not separable, the probe cannot discriminate, and the arm reports exactly that instead of running to a foregone verdict — a prespecified indeterminacy exit, stated in the contract.

3. **Circularity check, faced rather than waved at.** The shape is derived from the same cohort's labels that train the model. That is deliberate, not a compromise: the question was always whether the model internalized the lesson *its own training target* teaches — G-shape establishes what that lesson is before asking whether the model learned it. Two firewalls keep this from becoming self-confirmation: the census freezes on the round-1 split and the probe runs on the held-out complement; and the match criterion compares two independently estimated quantities (outcome change point from labels; model change point from paired edits) that no shared fitting step connects. External literature (Wintermark 2006, the porcine CBF×CBV interaction study) now supplies motivation and plausibility for a ceiling existing at all — it is no longer cited as if it had established the ceiling's location.

4. **What was lost — and it is the largest loss of the three rounds.** (a) The construct claim is now *cohort-anchored*: "autoregulatory reserve" in the deliverable sentence means the outcome-supported ceiling shape in this treated cohort, not a universal physiological constant. A reviewer may fairly read that as a narrower sentence than the card first promised, though the words and the question are unchanged. (b) A third named death path: if the outcome dose-response is smoothly monotone with no estimable change point, this cohort's labels do not encode a reserve-with-ceiling, G-shape fails, the candidate PAUSEs, and the joint-state question registers as a successor — same disposition as a G-hyper failure. (c) A fourth exit (indeterminacy) if c and the support boundary coincide. (d) The probe needs a finer edit grid and a change-point estimation layer in the frozen analysis — the "cheapest wide candidate" claim is now dead and the card should stop making it. (e) This is amendment three, and the standing rule says three amendments usually means the idea was wrong. I will not argue the rule away; the honest reading of the trajectory is that the original card was underspecified in exactly the places two reviewers independently probed: it assumed its keystone, then its discriminator, then its discriminator's premise. What I can say is that all three amendments implemented the critic's own stated resolution conditions, none moved the question or the deliverable sentence, and each installed a measurement where an assumption stood. If the critic judges the cohort-anchoring of "reserve" in (a) to have crossed the claim-identity line, or finds a defect this structure still cannot answer, I will concede rather than amend a fourth time — the pre-commitment from round 2 stands.

**Identity check:** the one-sentence question — is the model using the blood-volume reserve, read against CBF, to separate salvageable from lost tissue — is unchanged, and the deliverable sentence is unchanged. What changed is where the word "reserve" gets its operational content: from an assumed kink location to a measured, frozen, outcome-derived one. That is the critic's own branch-one repair, executed on the cohort the study already owns. Revision-in-place.

**Status:** OPEN


===== ideas/023/decision.md =====
# Decision — idea 023, probe 023 Phase C outcome census (take 13)

## Result card

- **Idea:** idea-023 — "The joint CBV/MTT compensation state at matched flow"
  (charter isles24; reduced claim: outcome-associated joint CBV/MTT decision
  boundary; the phrase "autoregulatory blood-volume reserve" is prohibited).
- **Probe / sequence position:** probe 023, contract v1 as amended
  (mirror-free design), Phase C real-data census, take 13 — the first and
  only outcome-reading run for this idea. Preceded by outcome-blind Phase S
  synthetic calibration and twelve operational takes that stopped before any
  label access.
- **Dataset / pin:** ISLES'24 public training release, Zenodo record
  16813698 (published 2025-08-12), `train.7z` md5
  `36ae28b9a17f7340b8bbef62b595cb57`, sha256 `038920e4dc2011a3…`, 149
  released cases.
- **Primary metric:** per within-patient CBF-percentile band ([0,33),
  [33,67), [67,100] of finite deficit CBF), equal-patient-weight mean of
  d = risk(Q1 low-CBV) − risk(Q4 high-CBV) over the patient's own label-blind
  log-CBV quartile cells in the eroded Tmax>6s deficit region; 95%
  patient-bootstrap percentile CI (2,000 resamples, seed 20260824).
  Preregistered gate: three-band conjunction (common nonzero sign; ≥2 of 3
  CIs excluding zero in that direction; all CI widths ≤ 0.15).
- **Contract blob:** `03d4545fe293f0067c69ce9e9e696ec97b894d7b`; approval
  marker bound to the same blob (2026-08-28T02:31:13Z).
- **Results bundle:** `probes/023/results/results_v2/` at commit
  `1c0acdbf5dccabd00449c5235b5e83e3bb369f51`; all citations resolve there.
- **Families:** authored by the Claude family (interpret-build leg 1);
  revised in round 2 per the round-1 cross-family review; re-review
  pending.
- **Out-of-scope warnings:** not evidence about autoregulatory reserve,
  vasodilatory capacity, or any causal physiology; no CBV-vs-MTT channel
  claim (the central-volume identity holds in these maps); no model was
  probed, so nothing about model use; not evidence that CBV/MTT lacks
  biological importance; scope is 99 analyzed treated patients, icobrain cva
  maps, this operationalization only — reserved cases and hidden test set
  untouched.

## Layer A — Finding

The take-13 census completed validly and its preregistered three-band gate
FAILED on direction: the ISLES'24 census labels do not carry a directionally
consistent joint CBV/MTT–outcome association at matched flow under this
operationalization. The middle flow band shows higher final-infarct
membership in high-CBV voxels (mean d = −0.032, 95% CI [−0.056, −0.008]),
the highest band the opposite (mean d = +0.023, CI [+0.005, +0.044]), and
the lowest band is indistinguishable from zero. All CI widths (0.039–0.065)
beat the frozen 0.15 precision bound with 99 contributing patients per band
against a floor of 20, so this is the contract's decisive negative, not a
power or support failure. Idea 023's Stage-0 keystone is therefore absent
as operationalized, and the contract PAUSEs the idea; the planned model-use
probe does not run. The single most important caveat: the label-blind NCCT
audit recorded per-case tissue composition for the CBV quartile cells, and
its cited example cases show large Q1-vs-Q4 attenuation differences (in the
lowest band, with frankly hypodense low-CBV cells); how prevalent that
imbalance is across the cohort was not quantified, so this negative binds
the percentile-band operationalization on these vendor maps — it does not
show the joint state is biologically or predictively empty.

## Layer B — Derivation narrative

1. **Governance.** Contract amended to the mirror-free design and frozen at
   blob `03d4545fe293…`; fresh human approval bound to that blob
   (2026-08-28T02:31Z); probe code approved through nine cross-family
   review rounds; the run's gate verified contract and approval blobs at
   start. Phase S (outcome-blind) had frozen the operating point —
   ≥20 patients/stratum, ≥100 voxels/cell, CI width ≤0.15 — and its output
   hash was re-verified at Phase C load.
2. **Provenance.** Zenodo record 16813698 pinned; archive md5 matched the
   record checksum; 2,981 members manifested; split frozen from immutable
   hashed IDs BEFORE any label access (manifest sha
   `da79e94b…`): 149 released cases → 100 census / 49 reserved.
3. **CONSORT flow.** 100 census cases in; 1 excluded (sub-stroke0043,
   pre-authorized `source_corrupt_member` — the archive-verified defective
   CBF member); 1 duplicate non-canonical lesion archive member excluded
   for sub-stroke0142 with the canonical derivative retained (case
   analyzed); 99 cases analyzed. All 99 contributed to all three bands
   (`per_patient.csv`: 297 rows); nonfinite voxels occurred only where
   permitted and were counted per case.
4. **Gates.** Grid/coverage: passed (resampling recorded per case in
   `schema_census.csv`). Identity coordinate: median absolute centered
   residual 0.0078 / 0.0036 / 0.0078 across bands vs the 0.10 kill limit —
   passed with an order of magnitude of headroom (no kill condition was
   approached). Support: 99 ≥ 20 per band — passed. Precision: max CI width
   0.0652 ≤ 0.15 — passed. Direction: signs (+, −, +) with the two
   zero-excluding intervals in opposite directions — FAILED. Result:
   `g_label_passed: false`, status `NEGATIVE_PATTERN`.
5. **Diagnostics.** The pre-registered label-blind HU tissue audit
   recorded 594 per-case rows; the bundle contains no aggregate HU
   statistic and cohort prevalence of imbalance was not computed. Cited
   example rows document Q1-vs-Q4 attenuation imbalance in band 1 (e.g.
   3.0 vs 23.0 HU), one balanced and one oppositely imbalanced case in
   band 2, and a very-wide-spread Q4 cell in band 3. Because cohort-wide
   HU balance was therefore not demonstrated, the 2026-08-28 rule's
   "balanced" branch cannot be certified and the tissue-composition caveat
   is applied conservatively, pointing any successor at a tissue-normalized
   reference. Median patient-level d is ~0 in every band while the band-2
   and band-3 mean CIs exclude zero, indicating between-patient
   heterogeneity; no contribution analysis was computed, so which or how
   many patients drive the means is not claimed.
6. **Variants.** All authorized variants are reported: Phase S (separate
   bundle, hash-pinned), this single Phase C analysis
   (`maximum_variants: 1`, one seed), and the estimator-untouched HU audit.
   Prior takes 1–12 never opened outcome data; the label freeze held.

## Layer C — Claims table

All rows cite `probes/023/results/results_v2/` at commit
`1c0acdbf5dccabd00449c5235b5e83e3bb369f51`.

| # | Claim | Value as cited | Source |
|---|---|---|---|
| 1 | Run status | NEGATIVE_PATTERN | [cite: summary.json | status] |
| 2 | Gate outcome | false | [cite: summary.json | g_label_passed] |
| 3 | Census / analyzed cases | 100 / 99 | [cite: summary.json | census_case_count, analyzed_census_case_count] |
| 4 | Released / reserved cases | 149 / 49 | [cite: summary.json | released_case_count, reserved_case_count] |
| 5 | Record pin | 16813698, 2025-08-12 | [cite: summary.json | record_id, publication_date] |
| 6 | Archive md5 = Zenodo checksum | 36ae28b9a17f7340b8bbef62b595cb57 | [cite: summary.json | archive_md5, zenodo_checksum] |
| 7 | Archive sha256 | 038920e4dc2011a3f47b8bb8421c67e36d07f1d84f1ba442563077480f75d129 | [cite: provenance.json | archive_sha256] |
| 8 | Archive members | 2981 | [cite: provenance.json | archive_member_count] |
| 9 | Split manifest sha256 | da79e94bdae3f59d23db497d5f26f0d57aa4f279847fe57ec9a8d05ebcf18843 | [cite: summary.json | split_manifest_sha256] |
| 10 | Band 1 mean d; CI; width | 0.006391646480739713; [−0.026830257261146396, 0.0383678779489388]; 0.06519813521008519 | [cite: per_stratum_summary.csv | stratum=1 | mean_d, ci_low, ci_high, ci_width] |
| 11 | Band 2 mean d; CI; width | −0.03200187198047477; [−0.05590632802084301, −0.007978192339199943]; 0.04792813568164307 | [cite: per_stratum_summary.csv | stratum=2 | mean_d, ci_low, ci_high, ci_width] |
| 12 | Band 3 mean d; CI; width | 0.02307549118960302; [0.004965694506583826, 0.04356979149013058]; 0.038604096983546755 | [cite: per_stratum_summary.csv | stratum=3 | mean_d, ci_low, ci_high, ci_width] |
| 13 | Median d per band | 0.0; −0.0005886681383370125; 0.000556250836852953 | [cite: per_stratum_summary.csv | stratum=1,2,3 | median_d] |
| 14 | Contributing patients per band | 99, 99, 99 | [cite: per_stratum_summary.csv | stratum=1,2,3 | patients] |
| 15 | Frozen support/precision minima | 20 patients; 100 voxels/cell; 0.15 width | [cite: resolved_config.json | minimum_contributing_patients_per_stratum, minimum_voxels_per_patient_quantile_cell, maximum_primary_ci_width] |
| 16 | Identity residual MAD per band (limit 0.10) | 0.0077610015869140625; 0.003559589385986328; 0.0077877044677734375 | [cite: identity_residual_summary.csv | stratum=1,2,3 | median_absolute_centered_residual] |
| 17 | Phase-S csv hash verified at load | 59069fa92399cd5c600c89e0d66bb4c7c12679e14f12824b54ae0ce6a6061ef4 | [cite: determinism_manifest_start.json | input_paths.phase_s_csv | sha256] |
| 18 | Source-corrupt exclusion | sub-stroke0043, source_corrupt_member | [cite: exclusions.csv | case_id=sub-stroke0043 | record_type, reason] |
| 19 | Duplicate lesion member excluded, case retained | sub-stroke0142 | [cite: exclusions.csv | case_id=sub-stroke0142, record_type=excluded_archive_lesion | reason] |
| 20 | HU audit rows | 594 | [cite: summary.json | bin_tissue_audit_rows] |
| 21 | Band-1 imbalance example | Q1 3.0 HU vs Q4 23.0 HU | [cite: bin_tissue_audit.csv | case_id=sub-stroke0092, stratum=1 | median_hu, both style_group rows] |
| 22 | Band-2 balance example | 21.0 vs 21.0 HU | [cite: bin_tissue_audit.csv | case_id=sub-stroke0002, stratum=2 | median_hu, both style_group rows] |
| 23 | Band-3 spread example | Q4 iqr_hu 314.5 | [cite: bin_tissue_audit.csv | case_id=sub-stroke0133, stratum=3, style_group=Q4_high_CBV | iqr_hu] |
| 24 | Large single-patient contrast example | d = −0.20385563685311792 | [cite: per_patient.csv | case_id=sub-stroke0002, stratum=1 | d] |
| 25 | Permitted nonfinite example | 302261 nonfinite MTT voxels | [cite: exclusions.csv | case_id=sub-stroke0113 | nonfinite_mtt_voxels] |
| 26 | Approval binding | blob 03d4545fe293f0067c69ce9e9e696ec97b894d7b, 2026-08-28T02:31:13Z | [cite: ../../../ideas/023/HUMAN_APPROVED_PROBE | full text] (repo path, outside bundle) |
| 27 | Gate line at run start | approval gate passed on 03d4545fe293… | [cite: run_log.txt | line 1] |

The HU-audit rows cited above verify those individual cases only. The
bundle contains no aggregate HU statistic, and no cohort-level frequency or
prevalence of imbalance is claimed anywhere in this decision.

## Verdict

**PAUSE.** The valid census matched the contract's negative_pattern: the
Stage-0 keystone (a precise, directionally consistent outcome association
with the joint CBV/MTT state at matched flow) is not present in the census
labels as operationalized, so idea 023 pauses and the model-use probe is not
authorized. This is a decisive negative for the keystone, not evidence that
the joint state lacks biological or predictive content — the HU audit's
cited example cases show tissue-imbalanced quartile cells (cohort
prevalence not quantified), and the band-2/band-3 sign reversal plus the
per-case audit table are the empirical starting points for any
tissue-normalized successor (parent idea-023) via the normal pipeline. The
separately pre-registered clinical-outcome join and the PAUSED transition
itself remain operator acts. Full analysis: `ideas/023/interpretation.md`
(revised per the round-1 cross-family review; decisions.md entry deferred
until the interpretation passes review).


===== ideas/023/feasibility.md =====
# Feasibility memo — idea 023 (isles24-scout-002-c07)

**Question under feasibility review:** Does a specified map-input final-infarct
model use the joint CBV/MTT compensation state at matched CBF deficit when that
state has a precise outcome relationship in the training cohort?

**Authorized claim scope (binding, per decisions.md 2026-08-17):** the claim
language is fixed as an *outcome-associated joint CBV/MTT decision boundary*.
The phrase "autoregulatory blood-volume reserve" is prohibited; physiological
naming requires a successor with challenge-based validation. This memo assesses
feasibility of the reduced claim only.

**Mandated condition discharged in §3:** prior art on map-editing and
counterfactual-perturbation mechanisms, plus a concrete stay-in-distribution
edit strategy with numbers. Per the operator ruling, absence of workable
precedent would be a legitimate kill; §3 concludes precedent is sufficient.

Verification statuses used below: **VERIFIED** (primary source fetched and read
this stage, or inspected in a prior recorded stage), **SOURCE-SUPPORTED**
(quoted in the operator-commissioned external review brief of 2026-08-17, not
independently re-fetched), **UNVERIFIED** (stated by no inspected source; must
be resolved at Stage 0), **INFERENCE** (my reasoning from verified facts).

---

## 1. Closest work and exact gap

**Closest work, verified this stage:**

- Robben et al. 2020, *Medical Image Analysis* (PMID 31683091;
  arXiv:1812.02496): predicts final infarct volume from **native CTP** plus
  treatment metadata and analyzes the effect of varying treatment parameters
  (time, recanalization) — counterfactuals on *metadata*, not on map values.
  VERIFIED (PubMed record and arXiv abstract this stage; also verified during
  critique).
- Amador et al. 2024, *J Biomed Inform* (S1532046423002885): cross-attention
  model on 4D CTP + clinical metadata; explicitly "allows generating attention
  maps and counterfactual outcome scenarios to investigate the relevance of
  **clinical variables**." Again metadata counterfactuals. VERIFIED (publisher
  page this stage).
- Amador et al. 2022, *Medical Image Analysis* (S1361841522002389):
  treatment-specific lesion outcome prediction from 4D CTP — the
  treatment-arm-swap counterfactual in the same task family. VERIFIED
  (publisher listing this stage; abstract only).
- ISLES'24 challenge report (arXiv:2408.10966): the benchmark itself — 150
  train / 98 hidden test, top Dice 0.285, rCBF<30% clinical baseline Dice
  0.163, ground truth from follow-up DWI. VERIFIED this stage.

**Exact gap (unchanged from the debated card, now re-checked):** no located
work perturbs the *values of the released perfusion maps themselves* along the
native joint CBV/MTT conditional distribution at fixed CBF and Tmax, within
case, to test whether a final-infarct model responds to the compensation
state. Published counterfactuals in this task family perturb clinical/treatment
variables or ablate whole channels. This remains a targeted gap statement, not
a proof of novelty ("I did not find it" is not proof).

## 2. Dataset access, license, versioning

- **Access:** public Zenodo, no DUA, registration-free API access confirmed.
  VERIFIED this stage via the Zenodo REST API.
- **License:** CC BY-NC-SA 4.0 on both inspected versions. VERIFIED.
  Non-commercial research use is compliant with program constraints.
- **Version churn is real and must be pinned.** The version inspected at
  keystone screen (record 16731717 — the concept/parent DOI) now resolves
  through at least: record 16813698 ("version 2", train.7z ≈ 92.2 GB **plus a
  separately downloadable `clinical_data-description.xlsx`, ≈ 12 MB**) and a
  latest version, record **17652035 ("version 6", published 2025-11-20,
  train.7z = 99.0 GB as the only listed file)**. VERIFIED this stage (API).
  Consequences: (a) Stage 0 must pin one record id and its file MD5s before
  anything else; (b) the clinical-data description file is listed on v2 but
  was not returned in the v6 file listing — which record carries it must be
  established at pin time; (c) the critique's instruction to pin hashes is
  retroactively vindicated.
- **Monolithic archive confirmed:** the training data is a single `train.7z`
  (92–99 GB depending on version). **Derivative-only retrieval is not
  offered.** VERIFIED. Mitigation (INFERENCE, standard 7z behavior): 7z
  supports selective extraction by path, so the ~99 GB download is
  unavoidable but the uncompressed footprint can be limited to
  `derivatives/` (maps, registered NCCT, lesion masks) plus `phenotype/`,
  discarding the raw 4D CTP series, which dominates the archive. Uncompressed
  selective footprint is UNVERIFIED; estimate < 20 GB.
- **Case-count discrepancy, must resolve at Stage 0:** Zenodo descriptions say
  **149** training cases; the challenge paper says **150** (100 Munich, 50
  Zurich). VERIFIED that the discrepancy exists; its cause is UNVERIFIED
  (plausibly a withdrawn case). Non-blocking; affects only bookkeeping.

## 3. Prior art on map-editing and counterfactual perturbation (mandated section)

### 3a. Direct input-value perturbation in medical imaging models

- **Occlusion/perturbation sensitivity** is a standard, widely published probe
  family in medical imaging (Zeiler & Fergus occlusion, arXiv:1311.2901; Fong
  & Vedaldi meaningful perturbation, arXiv:1704.03296; both applied repeatedly
  to medical segmentation and classification). These methods *zero or blur*
  input regions — interventions far **more** out-of-distribution than the
  bounded value edits proposed here. SOURCE-SUPPORTED / method anchors
  VERIFIED as papers; their medical uptake is common ground in the critique
  and external brief.
- **Robben et al. and Amador et al.** (§1) establish the counterfactual-probing
  precedent *on this exact task* (CTP-based final-infarct prediction), though
  on metadata rather than map values. VERIFIED.

### 3b. Generative/causal counterfactual image editing

- Pawlowski, Castro & Glocker, *Deep Structural Causal Models for Tractable
  Counterfactual Inference*, NeurIPS 2020 (arXiv:2006.06485; code
  biomedia-mira/deepscm): do-interventions producing counterfactual **brain
  MRI** images. VERIFIED this stage.
- Sanchez & Tsaftaris, *Diffusion Causal Models for Counterfactual
  Estimation*, CLeaR 2022 (arXiv:2202.10166; code vios-s/Diff-SCM):
  diffusion-based counterfactual estimation demonstrated on imaging data.
  VERIFIED this stage.
- These show the field accepts model-probing via synthesized/edited medical
  images when validity is argued; our design is *more* conservative than
  generative synthesis because it edits released map values directly under
  empirical-support bounds rather than sampling from a learned generator.
  INFERENCE.

### 3c. Perfusion-map manipulation as an accepted measurement operation

- Kellner et al., AJNR 2024;45(3):277, "Reducing False-Positives in CT
  Perfusion Infarct Core Segmentation Using Contralateral Local
  Normalization": clinical-methods work that **arithmetically manipulates
  perfusion maps** (voxelwise division by a mirrored, clipped, smoothed copy)
  as a legitimate operation on clinical maps. SOURCE-SUPPORTED (quoted in the
  2026-08-17 external brief).
- The DEFUSE-3/DAWN rCBF<30%-of-contralateral core definition means
  ratio-transformed map values are the *clinical standard*, so mirror-ratio
  arithmetic on these maps is squarely inside accepted practice.
  SOURCE-SUPPORTED.

### 3d. What has no precedent

No located published work performs a **consistency-preserving joint edit along
a physiological identity** (CBV and MTT co-scaled at fixed CBF = CBV/MTT) on
clinical perfusion maps to probe a trained model. The nearest neighbors are
§3a–3c. This is the novelty delta *and* the residual risk: no external
calibration of expected effect sizes or of edit-realism failure modes exists.
The claim "no precedent" is a search result, not a proof.

### 3e. Concrete stay-in-distribution strategy (numbers are Stage-0 defaults, to be frozen before outcome inspection)

1. **Edit region:** deficit tissue defined as Tmax > 6 s (the DEFUSE-family
   penumbra threshold), eroded by 1 voxel; exclude voxels within 2 voxels of
   the estimated midline and vascular voxels (CBV above a frozen vessel cap,
   default 8 mL/100 g, to be checked against released map units at census).
2. **Strata:** mirror-normalized CBF (rCBF_mirror) bins [0.15, 0.30),
   [0.30, 0.45), [0.45, 0.60) — bracketing the clinically load-bearing
   rCBF ≈ 0.30 landmark.
3. **Edit operator:** multiply CBV and MTT voxelwise by the same factor
   f ∈ {0.70, 0.85, 1.15, 1.30} (CBF and Tmax untouched; CBF = CBV/MTT
   preserved by construction where the identity holds), plus f = 1.00
   zero-dose repeat.
4. **Support bounds:** post-edit rCBV_mirror must remain within the stratum's
   native [q05, q95] estimated from census-split patients only; voxels that
   would exceed bounds are clamped; any case-stratum cell with > 10% clamped
   voxels is excluded from that dose.
5. **In-distribution gate:** ≥ 99% of edited-voxel joint (rCBF_mirror,
   rCBV_mirror) values must fall inside the 99% highest-density region of the
   native joint distribution of the same stratum (census split); report the
   outside fraction per case and dose.
6. **Controls:** bit-identical zero-dose repeat; matched-magnitude sham (same
   |f| with spatially permuted direction); off-deficit edits in mirror-normal
   tissue; independently specified Tmax positive control (+2 s, +4 s within
   the deficit) as the channel-sensitivity floor.
7. **Identity residual:** the census measures the voxelwise residual of
   MTT − CBV/CBF on released maps; if the identity does not hold (large
   residual), the co-scaling rule is replaced by movement along the empirical
   conditional joint curve, per the card.

### 3f. Judgment on the operator's kill condition

Workable precedent **exists** at every layer the design actually needs:
input-perturbation probing on this exact task family (§3a), accepted
counterfactual image editing in neuroimaging (§3b), and routine arithmetic
manipulation of these exact map types in clinical methods work (§3c). The
genuinely unprecedented element — the identity-preserving joint edit — is a
*constraint added on top of* precedented operations that makes the
intervention strictly closer to the data manifold than published occlusion
probes, and §3e gives it a numeric, checkable realism budget. The
absence-of-precedent kill is therefore **not triggered**. What the missing
exact precedent does cost is effect-size calibration, which is why the
equivalence margin must come from sham variability (already in the card) and
why the census precedes all model work.

## 4. Labels, concept validity, annotation provenance

- **Ground truth:** final-infarct masks derived from follow-up MRI (DWI, 2–9
  days post-acute) using DeepISLES, with quality control and correction by
  medical students supervised by two neuroradiologists (>10 y experience).
  VERIFIED this stage (challenge paper). Provenance is documented — the
  program's dominant ANNOTATION_PROVENANCE failure mode does not apply to the
  primary readout, which is a label-free paired model-output delta; labels
  enter only the census (K2) and model training.
- **X is computable without an annotator:** rCBF_mirror and rCBV_mirror are
  deterministic arithmetic on released maps plus automatic midline
  estimation. Mirror-estimation quality is a Stage 0 gate (UNVERIFIED).
- **Clinical covariates:** the challenge paper promises "demographics,
  clinical history, laboratory results, neurological scores, and outcome
  measures" including admission NIHSS and 3-month mRS; a
  `clinical_data-description.xlsx` is separately downloadable from the v2
  Zenodo record. **Whether reperfusion status (mTICI) and treatment times are
  released is UNVERIFIED** — no inspected source names mTICI. This matters:
  the census's treatment-handling clause activates only if these fields
  exist; if absent, that absence is a recorded scope limit (per the card),
  not a blocker. Resolving this costs a 12 MB download and is the cheapest
  outstanding fact in the whole study.

## 5. Sample structure and split unit

- 149–150 cases, one acute session per patient; **split unit = patient**
  (equivalently case). VERIFIED structure via Zenodo/BIDS description.
- The challenge's 98-case test set is hidden; all work happens on the released
  training cases. The card's census/probe separation (census patients vs
  held-out toggle patients, frozen before outcome inspection) is the split
  that matters; with ~150 patients, a 100/50 or 110/40 census/probe split is
  the realistic envelope. INFERENCE.
- **Power is the honest weak point:** patient-clustered estimation of a
  continuous outcome–state relationship (and any change point) from ~100
  census patients across three strata may fail the precision gate. That is
  what the gate is for; it is a named, cheap death, not a hidden one.

## 6. Existing code and checkpoints (material update to the card)

The card assumed no released challenge weights. That is now **false in a
useful direction** (all VERIFIED this stage from the challenge paper §Code
Availability and the repos):

- **#1 Kurtlab** (Dice 0.285): github.com/KurtLabUW/ISLES2024 — inference
  Docker + preprocessing + nnU-Net folder; weights via a Google Drive link in
  `model weights.txt`. Exact input channels NOT stated in the paper
  (arXiv:2505.18424 describes NCCT-based skull-strip + windowing applied to
  co-registered scans); channels must be read off the repo/plans file at
  Stage 0. Link liveness UNVERIFIED.
- **#2 AMC-Axolotls** (Dice 0.263): github.com/Mahsa0M/isles2024_docker —
  nnU-Net v2 3d_fullres, **six declared input channels: NCCT, CTA, rCBF,
  rCBV, MTT, Tmax**, weights via Google Drive
  (drive.google.com/file/d/1i9GvcanpopV-M6omJ8w-NbNv4ZoLyKnM). The perfusion
  maps are input channels, so the proposed edits have a port of entry into a
  real benchmark submission. Multimodal (NCCT+CTA present), so per the card
  it is a *secondary* probe target, and the maps-only self-trained model
  remains primary. Link liveness and license of the weights UNVERIFIED.
- **#3 Ninjas**: github.com/jaymoz/ISLES-Challenge-2024 — not yet inspected.
- **kimberly-amador/ISLES24-PrediCTP**: takes 4D CTP, no released weights —
  no port of entry for map edits; excluded. VERIFIED.

Consequence: the model gate is stronger than the card assumed. The Stage 0
weight inventory has concrete targets, and the "benchmark model" framing can
be partially earned (scoped to the specific probed submissions) rather than
resting only on a self-trained family.

## 7. Compute estimate

- **Download:** one-time ~99 GB from Zenodo. Selective 7z extraction keeps
  disk below ~120 GB transient / ~20 GB persistent (estimate; UNVERIFIED).
- **Stage 0 census:** CPU-only, hours on the derivative subset once
  extracted; no GPU.
- **Self-trained maps-only model:** nnU-Net ResEnc M is the honest Colab
  target — documented at 9–11 GB VRAM and ~12 h per fold on an A100
  (VERIFIED, nnU-Net resenc_presets.md). ResEnc L (24 GB, ~35 h/fold) fits an
  A100-40GB Colab session budget only with checkpoint-resume across sessions;
  the winner's ResEnc-L-class recipe is therefore reproducible but expensive.
  Recommend freezing ResEnc M (or standard 3d_fullres), 1–2 folds on a frozen
  split, not 10-fold. Total: roughly 1–3 A100-days, resumable.
- **Probe inference:** ~40 held-out cases × (4 doses + zero-dose + sham +
  off-deficit + 2 Tmax-control variants ≈ 9 variants) ≈ 360–800 forward
  passes; nnU-Net 3D inference ~1–2 min/case-variant → ~10–25 GPU-hours.
  Fits single-GPU sessions. INFERENCE from standard nnU-Net behavior.

## 8. Baselines and accepted metrics

- Challenge metrics are established: Dice, absolute volume difference,
  lesion-wise F1, absolute lesion count difference (VERIFIED, official repo
  evaluation notebook + challenge paper).
- Published anchors for the model-performance gate: winner 0.285 ± 0.213
  Dice / 21.2 ± 37.2 mL AVD; #2 0.263; #3 0.255; **clinical rCBF<30%
  baseline 0.163 Dice**. A self-trained maps-only model must beat the
  rCBF<30% baseline on its own frozen validation split to be worth probing —
  a natural, externally anchored floor. Proposed gate (to freeze at Stage 0):
  cross-validated Dice ≥ 0.20 and above the rCBF<30% baseline computed on
  the same split. The primary endpoint (paired within-case output deltas)
  does not use these metrics; they gate model adequacy only.

## 9. Leakage and confounds

- **Within-case paired edits** hold scanner, vendor, site, protocol,
  reconstruction, positioning, habitus, prevalence, and referral pathway
  fixed by construction; mirror ratios kill global scaling. Unchanged from
  the debated card; still correct.
- **Vendor map-generation dependence** (icobrain cva 1.5.0 only —
  VERIFIED via challenge paper + SOURCE-SUPPORTED version number) is the
  admitted rung-2 limit; no released second-vendor map set exists in-cohort.
- **Normalization coupling — imported lesson from idea 021 (external brief,
  2026-08-17):** nnU-Net applies per-channel normalization; whether the
  probed models use per-instance (per-case z-score) or dataset-level fixed
  statistics for the map channels determines whether an edit to deficit-ROI
  values shifts whole-volume statistics and produces a spurious global
  response. The edits here are regional (deficit ROI), so the coupling is
  smaller than 021's hemisphere-scale edits, but the memo adopts the same
  control: **verify the normalization scheme of every probed model
  (plans/preprocessing files) at Stage 0, and add a
  normalization-statistics-held-fixed variant** (reuse the unedited volume's
  normalization constants for the edited volume) as a required validity arm.
  This is a new, concrete Stage 0 item that the card's gate list should
  absorb into the model gate.
- **Label leakage:** none identified — inputs are acute-phase, ground truth
  from follow-up MRI; report text is not an input. Unchanged.
- **Census→probe leakage:** handled by the frozen patient split; the
  equivalence margin derives from sham variability on validation patients
  only.

## 10. Riskiest assumption and its smallest probe

**Riskiest assumption (K2, unchanged):** the released outcomes encode a
precise, directionally stable relationship with the continuous joint CBV/MTT
state within matched-rCBF strata, estimable with patient-clustered inference
from ~100 census patients, with an outcome feature separable from the support
boundary.

**Smallest probes, in ascending cost, all pre-authorized-shape (no model
work, no code beyond the census plan):**

1. **Zero-data probes (minutes):** (a) download
   `clinical_data-description.xlsx` from the pinned record and inventory
   reperfusion/treatment fields; (b) test the two Google Drive weight links
   for liveness and record hashes; (c) enumerate the pinned Zenodo record's
   file list and MD5s via API.
2. **Synthetic power check (CPU, no real data):** before freezing the census
   plan, simulate the planned patient-clustered estimator at n = 100 census
   patients under plausible effect sizes and within-patient voxel counts to
   fix the minimum-support and CI-width numbers in the freeze with known
   operating characteristics — this spends no real outcomes and prevents an
   avoidably underpowered freeze.
3. **The census itself (CPU, days):** the frozen G-label/G-shape analysis on
   the census split; it is simultaneously the keystone inspection and, either
   way it comes out, a citable observation on the CBV/CBF-interaction debate
   in a modern treated cohort.

## 11. Constraint and cap compliance

- Compute: fits Colab Pro+ single-GPU sessions (§7). No DUA. No radiologist
  annotation. Primary readout label-free. Confirmatory/exploratory separation
  and freeze-before-look are encoded in the card's Stage 0.
- `keystone_status` remains `NOT_INSPECTED`; feasibility and
  novelty_confidence stay capped at 3. Nothing in this memo lifts the cap —
  only the census can.

## 12. Verdict

**GO — scoped to Stage 0.** Authorized next steps: pin the Zenodo record and
hashes; the zero-data probes of §10.1; the synthetic power check of §10.2;
freeze the census plan; run the census on the census split. No model
training, no weight download beyond liveness checks, no edit inference is
authorized by this memo; those require the census to pass and a fresh
contract. Three Stage-0 additions beyond the card are recorded here and
should be carried into the contract: (a) the normalization-scheme inspection
and statistics-held-fixed variant (§9), (b) the released-weights inventory
now has two concrete targets with the #2 submission confirmed maps-in-channels
(§6), (c) the census freeze must be preceded by the simulation-based power
check (§10.2).

## In plain terms

This study can be done: the data is public, free, and licensed for research;
the perfusion maps the experiment would edit are confirmed present for every
patient; and — new since the card was written — the top two challenge teams
released their trained models, one of which verifiably takes the perfusion
maps as inputs, so there is a real benchmark model to probe as well as the
planned self-trained one. The cost is one ~99 GB download, a few days of
CPU analysis, and roughly one to three GPU-days of training that only happen
if the cheap analysis passes. Editing input maps to probe a model has
published precedent in this exact disease area (researchers have varied
treatment variables and routinely blank out image regions, which is a harsher
intervention than the bounded edits planned here), so the required
prior-art bar is met. The single biggest practical risk is statistical: with
only about 150 patients, the planned outcome analysis may be too imprecise to
establish the relationship the whole experiment depends on — in which case
the project stops early, cheaply, and with a small publishable observation
rather than a wasted model study.


===== ideas/023/idea_card.json =====
{
  "id": "isles24-scout-002-c07",
  "track": "wide",
  "search_mode": "C",
  "title": "The joint CBV/MTT compensation state at matched flow",
  "question": "Does a specified map-input final-infarct model use the joint CBV/MTT compensation state at matched CBF deficit when that state has a precise outcome relationship in the training cohort?",
  "deliverable_original": "The final-infarct model is using the autoregulatory blood-volume reserve -- capillary volume held at or above mirror-normal while flow falls -- as its tissue-salvageability signal, distinguishing the still-compensating penumbra from the collapsed core at matched flow deficit.",
  "deliverable_sentence": "This map-input final-infarct model is using the joint CBV/MTT compensation state at matched CBF deficit when it predicts tissue fate in this ISLES'24 cohort.",
  "rung": "Rung 1 conditional on the Stage 0 and edit-validity gates. Rung 2 requires reconstruction across map-generation variants or independent validation that the response is not peculiar to icobrain cva. Rung 3 would require an independently measured autoregulatory endpoint; the present study must not call the state autoregulatory reserve.",
  "scientific_uncertainty": "At the same relative CBF deficit, does the model use the remaining one-degree-of-freedom joint CBV/MTT state, or does it ignore that state and rely on other inputs?",
  "X_measurement": "For each voxel, measure mirror-normalized CBF and CBV from the released registered maps. Within prespecified rCBF-deficit strata, X is the position along the native joint CBV/MTT curve. If the released maps obey the central-volume identity, CBV and MTT are treated as one joint degree of freedom, never as separable concepts. Automatic midsagittal estimation and released maps make X computable without an annotator.",
  "mechanism": "Preserved versus reduced blood volume at matched flow is a named hemodynamic state. The biological cause may be autoregulatory dilation, collateral filling, reperfusion, or their mixture; this experiment does not separate them.",
  "analogy_audit": "The Little's-law and control-engineering analogy has been removed. Dropping it changes no measurement or experiment; central-volume terminology is sufficient.",
  "keystone_prerequisite": "Before model work, final-infarct membership must show a precise, directionally stable relationship with the continuous joint CBV/MTT state within matched-rCBF strata, with adequate within-patient support and separation from the empirical support boundary.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_residual_assumption": "If I have only verified the nearest checkable thing, what am I still assuming? The inspected release schema proves that all four maps coexist in NCCT space, but it does not prove that the outcome contains a learnable joint-state relationship, that both sides of any response change are supported, or that the maps share directly compatible grids. Those are load-bearing Stage 0 gates.",
  "existing_legwork": "The official ISLES'24 release documents 149 training cases with Tmax, CBF, CBV, and MTT derivatives in NCCT space (Zenodo 16731717; official repository). The challenge report documents icobrain cva tracer-kinetics deconvolution (arXiv:2408.10966). Wintermark et al. motivate CBV/CBF interaction physiologically (DOI 10.1161/01.STR.0000209238.61459.39), while Campbell et al. support rCBF as a core marker (DOI 10.1161/STROKEAHA.111.618355).",
  "closest_prior_work": "Robben et al. predict final infarct from native CTP and treatment variables and use input/metadata ablations (PMID 31683091; arXiv:1812.02496). Amador et al. use clinical-variable counterfactuals (article S1532046423002885). The exact delta is a within-case, native-support-bounded edit along the joint CBV/MTT state at fixed CBF and Tmax. This is a targeted gap statement, not a verified novelty claim.",
  "dies_like_prior": "No prior failure mode is yet escaped. It risks idea-009/016 IDENTIFIABILITY_FAILURE if the joint state cannot be separated from support density, map generation, or treatment; Stage 0 pauses rather than interprets that case. It differs from idea-006 only if native support and discriminator/sham gates establish that the edits are in distribution. ANNOTATION_PROVENANCE is not dominant because X and the primary paired model-output delta require no reader labels; outcome labels enter the prerequisite census and model training with documented provenance.",
  "stage_0": {
    "freeze_first": "Before inspecting outcomes, freeze patient splits, rCBF strata, minimum patients and within-patient voxels per state, CI-width requirement, directional-consistency rule, flexible monotone and change-point candidate models, support-edge separation rule, and handling of released treatment/reperfusion variables.",
    "schema_gate": "Pin release version and file hashes; census missing files, dimensions, voxel sizes, affines, coverage, map units, mirror quality, and the residual of the central-volume identity.",
    "outcome_gate": "On census-only patients, estimate patient-clustered final-infarct risk continuously over the joint CBV/MTT state within matched-rCBF strata. Require adequate joint support, precision, directional stability, and an outcome feature distinguishable from the support edge. Do not assume a kink at mirror-normal CBV.",
    "native_support_gate": "Define all edit targets from native conditional quantiles and require support on both sides of every confirmatory contrast. If the outcome feature and support boundary cannot be separated, exit indeterminate.",
    "model_gate": "Inventory released participant weights and exact inputs. Otherwise freeze a reproducible self-trained maps-only model; any conclusion is limited to that model family and recipe. Multimodal models, if used, are separate secondary analyses.",
    "failure_consequence": "Failure of the outcome, support, grid, or model gate pauses this candidate. It does not justify silently substituting an autoregulatory-reserve claim or treating a later null as decisive."
  },
  "smallest_decisive_experiment": "After Stage 0 passes, use held-out patients excluded from the outcome census. Within eroded deficit tissue and prespecified rCBF strata, move CBV and MTT together along the native conditional joint curve while holding CBF, Tmax, anatomy, scanner, site, protocol, positioning, and all other voxels fixed. Use several native-support-bounded doses in both directions. The primary endpoint is the patient-clustered paired change in predicted infarct probability mass as a function of joint-state displacement. Off-deficit edits, zero-dose repeats, matched sham edits, and an independently specified Tmax positive control gate interpretability. Identity-violating edits are exploratory and never pooled.",
  "confirmatory_separation": "The confirmatory question is use versus non-use of the joint state, not reserve versus generic CBV use. A flexible response curve is reported without assigning a physiological ceiling. CBV-channel versus MTT-channel attribution is prohibited when the central-volume identity holds.",
  "claim_identifiability": {
    "positive": "A gated, dose-ordered paired response identifies use of the joint CBV/MTT state by the tested model at matched CBF. It does not identify autoregulation, collateral inflow, or a particular input channel.",
    "alternatives": [
      "Edit artifact or out-of-distribution response: addressed by native conditional bounds, zero-dose repeat, shams, off-deficit edits, and discriminator gates.",
      "Scanner, vendor, site, acquisition protocol, reconstruction, positioning, body habitus, prevalence, referral pathway, or report-label leakage: held fixed by within-case editing; vendor map-generation dependence remains a rung-2 limit.",
      "Support-density or calibration saturation: not interpreted physiologically; any response feature coincident with the support boundary is indeterminate.",
      "Other modalities dominate: prevented in the primary maps-only model; multimodal results are secondary and model-specific."
    ]
  },
  "anticipated_negative": {
    "classification": "Decisive, conditional",
    "meaning": "If the outcome, support, model-performance, positive-control, and edit-validity gates all pass, an equivalence-bounded near-zero response decisively weakens the claim that this tested model uses the joint CBV/MTT state at matched CBF. It does not show that benchmark models generally 'side with rCBF,' and it does not show the state lacks biological importance.",
    "equivalence_requirement": "Freeze a minimum detectable paired response and equivalence margin from validation-only sham variability and a scientifically justified effect scale before held-out inference; simple non-rejection is sensitivity-limited, not decisive."
  },
  "prohibited_conclusions": [
    "Do not call the measured state autoregulatory blood-volume reserve without an independent autoregulatory endpoint or external physiological validation.",
    "Do not attribute a response to CBV rather than MTT when the central-volume identity makes them one degree of freedom at fixed CBF.",
    "Do not generalize from a self-trained model to challenge winners or benchmark models.",
    "Do not interpret a response change point as physiology when it coincides with the native support boundary.",
    "Do not interpret a failed Stage 0 gate or invalid edit as a scientific negative."
  ],
  "data_and_compute": "Public ISLES'24 training data, CC BY-NC-SA 4.0, no DUA. Stage 0 is CPU-first but may require the approximately 99 GB archive unless derivative-only retrieval is confirmed. Model training and held-out inference must fit single-GPU sessions; exact forward-pass count follows the frozen dose grid rather than the obsolete 320-pass estimate.",
  "verified_facts": [
    "Official release schema: 149 cases and per-case Tmax/CBF/CBV/MTT derivatives co-registered to NCCT space (Zenodo 16731717 and official repository, inspected 2026-08-17).",
    "Challenge report: perfusion maps were generated with icobrain cva using conventional tracer-kinetics deconvolution (arXiv:2408.10966, inspected during critique)."
  ],
  "unverified_claims": [
    "Outcome relationship and precision at matched rCBF",
    "Adequate native joint support away from its boundary",
    "Exact grid compatibility and usable map scaling",
    "Mirror-estimation quality",
    "Availability of released participant weights and exact channel specifications",
    "In-distribution validity and sensitivity of joint-state edits",
    "Novelty beyond the searched neighbors"
  ],
  "design_template": "counterfactual-synthesis",
  "scores": {
    "clarity": {"value": 4, "why": "One model-use question, one measured joint state, and explicit boundaries on interpretation."},
    "identifiability": {"value": 3, "why": "Within-case edits isolate joint-state use if validity gates pass, but vendor map generation and edit validity prevent a stronger score."},
    "medical_relevance": {"value": 4, "why": "It tests whether tissue-fate prediction uses hemodynamic information beyond matched flow deficit, without overstating the biology."},
    "interest": {"value": 4, "why": "It revisits the CBV-versus-CBF question inside a learned predictor with a direct use test."},
    "prior_legwork": {"value": 3, "why": "Maps, outcome labels, physiology, and model recipes exist, but the load-bearing census and exact model asset do not."},
    "feasibility": {"value": 3, "why": "Capped because the keystone is NOT_INSPECTED; Stage 0 is practical but has several legitimate pause gates."},
    "data_readiness": {"value": 3, "why": "Public data and schema are verified, but archive retrieval, headers, covariates, and derivative-only access still require inspection."},
    "evaluation_readiness": {"value": 3, "why": "Paired endpoints and controls are clear, but equivalence margin, dose grid, and support criteria must be frozen."},
    "negative_result_value": {"value": 4, "why": "Conditional on all gates and a prespecified equivalence margin, a null decisively rejects joint-state use for the tested model."},
    "novelty_confidence": {"value": 3, "why": "Capped by the uninspected keystone and because targeted search found no duplicate but cannot prove novelty."},
    "regret": {"value": 4, "why": "A CPU-first census can cheaply prevent wasted model work and the valid probe would answer a neglected mechanism question."},
    "mechanism_clarity": {"value": 4, "why": "The joint CBV/MTT state at matched CBF and its intervention are explicit; its biological cause is intentionally not identified."}
  },
  "mode_c_priority_score": {"value": 3.75, "why": "0.30*4 mechanism clarity + 0.25*3 identifiability + 0.20*4 interest + 0.15*4 medical relevance + 0.10*4 clarity."},
  "charter": "isles24"
}


===== ideas/023/interpret_review.md =====
# Interpretation review — idea 023, round 1

## 1. Citations resolve

I resolved every citation in `interpretation.md` against
`probes/023/results/results_v2/` (and the approval marker where applicable).
The following citations are transcription-exact:

- `run_log.txt`, line 1: Phase-C approval passed on contract blob
  `03d4545fe293f0067c69ce9e9e696ec97b894d7b`.
- `summary.json`: `archive_md5`, `zenodo_checksum`,
  `simulation_output_sha256`, `released_case_count`, `g_label_passed`,
  `status`, `identity_mad` for strata 1–3,
  `excluded_source_corrupt_cases`, `excluded_duplicate_lesion_members`,
  `analyzed_census_case_count`, `census_case_count`,
  `bin_tissue_audit_rows`, `reserved_case_count`, and
  `split_manifest_sha256`.
- `determinism_manifest_start.json`:
  `input_paths.phase_s_csv.sha256`; it is
  `59069fa92399cd5c600c89e0d66bb4c7c12679e14f12824b54ae0ce6a6061ef4`.
  The start and end determinism manifests are byte-identical as stated.
- `per_stratum_summary.csv`, strata 1–3: `patients`, `mean_d`, `ci_low`,
  `ci_high`, `ci_width`, `median_d`, `median_ci_low`, and
  `median_ci_high`. All displayed full-precision values match.
- `resolved_config.json`: minimum 20 contributing patients per stratum,
  minimum 100 voxels per patient-quantile cell, maximum primary CI width
  0.15, and seed 20260824.
- `identity_residual_summary.csv`, strata 1–3:
  `median_absolute_centered_residual` values 0.0077610015869140625,
  0.003559589385986328, and 0.0077877044677734375.
- `exclusions.csv`: sub-stroke0043 is an `excluded_case` for
  `source_corrupt_member`; sub-stroke0142 is an
  `excluded_archive_lesion` while the follow-up derivative is retained;
  sub-stroke0113 has 302261 nonfinite MTT voxels; and sub-stroke0002 has
  `vessel_cbv_p98` 29.140625.
- `per_patient.csv`: sub-stroke0002, stratum 1 has
  `d = -0.20385563685311792`.
- `bin_tissue_audit.csv`: all cited example rows resolve exactly:
  sub-stroke0092 stratum 1 Q1/Q4 medians 3.0/23.0;
  sub-stroke0057 stratum 1 5.0/24.0; sub-stroke0189 stratum 1 6.0/25.0;
  sub-stroke0002 stratum 2 21.0/21.0; sub-stroke0183 stratum 2 23.0/5.0;
  sub-stroke0109 stratum 3 30.0/58.0; and sub-stroke0133 stratum 3 Q4
  `iqr_hu = 314.5`.

The approval marker also binds the stated contract blob and timestamp.

## 2. Claim bounds

The primary gate language matches the contract: the result is
`NEGATIVE_PATTERN`, support and precision pass, and directional consistency
fails because the two zero-excluding intervals have opposite signs. The text
correctly scopes uncertainty to patients rather than seeds, states the
icobrain-cva/vendor and 99-patient limits, preserves the reserved 49 cases,
does not claim model use, and keeps autoregulatory, causal, and CBV-versus-MTT
claims out of scope. There is no tier-2 threshold issue in this probe, no
anchor population, and no baseline is incorrectly promoted to a floor.

**Blocking:** the HU and tail descriptions introduce aggregations that no
claim-bearing analysis file contains. In particular, “in most cases,”
“often by 10–20 HU,” “near-balanced in most cases (typical median difference
<= 2 HU),” “Q4 cells often show very wide HU spread,” and “the band-level
means are carried by a minority of patients” are cohort-level frequency or
contribution claims inferred by the author from row-level tables. The
interpretation itself acknowledges that no aggregate HU statistic exists.
The stage rule forbids creating an aggregation in prose that the analysis
files do not contain. The cited examples verify those cases only; they do not
support the frequency words. Revise these passages to example-bounded,
row-level observations and state that the existing outputs do not quantify
the prevalence of imbalance, or cite an authorized claim-bearing aggregate
artifact if one is produced through the governed analysis path. Likewise,
median-near-zero plus one extreme case supports heterogeneity, but not the
specific “minority carried the means” attribution without a recorded
contribution analysis.

## 3. Completeness without cherry-picking

I checked all three primary strata, all reported median contrasts and
intervals, the 297 per-patient rows, all 594 tissue-audit rows, the complete
exclusions table, and the three identity-residual rows. The interpretation
does not hide the material reversal: stratum 2 is negative while stratum 3 is
positive, and stratum 1 includes zero. It reports both authorized exclusions,
the tissue-audit heterogeneity, the central-volume result, and the untouched
reserved cases. No omitted table feature contradicts the primary negative.
The only completeness problem is the unsupported aggregation described in
check 2, not omission of an adverse result.

## 4. Verdict separation

The preregistered gate failure and provenance facts are correctly placed
under “Demonstrates.” Per-band pattern interpretation, patient heterogeneity,
and tissue-composition implications are placed under “Suggests,” and the
“Does not establish” section correctly blocks physiological, model-use,
channel-attribution, and external-generalization upgrades. Subject to removing
the unrecorded aggregations above, the separation is sound.

## 5. Plain-language fidelity

There is no distinct plain-language summary section. The “Next decision” and
positive/negative recap retain the main hedges and do not upgrade the primary
finding, but their statements that the HU audit demonstrates tissue imbalance
inherit the blocking aggregation problem above and must be narrowed with it.

```json
{"verdict": "REVISE", "blocking": ["Remove or replace the cohort-level HU-frequency and tail-contribution claims that are not present in a claim-bearing analysis artifact: 'most cases', 'often by 10–20 HU', 'typical median difference <=2 HU', 'often show very wide HU spread', and 'means are carried by a minority of patients'. Keep only cited row-level examples and explicitly say prevalence was not computed, or route a computed aggregate through the governed analysis path and cite it. Narrow the recap's unqualified tissue-imbalance claim consistently."]}
```


===== ideas/023/interpretation.md =====
# Interpretation — idea 023, probe 023 Phase C outcome census (take 13)

## Result card

- **Idea:** idea-023 — "The joint CBV/MTT compensation state at matched flow"
  (charter isles24; reduced claim scope per the 2026-08-17 operator ruling:
  outcome-associated joint CBV/MTT decision boundary only).
- **Probe and position in sequence:** probe 023, contract v1 as amended
  (mirror-free matched-flow design), Phase C real-data census, take 13. This
  is the FIRST and ONLY run in the idea's history that read outcome (lesion)
  data. It was preceded by Phase S synthetic calibration (a separate,
  outcome-blind bundle whose selected operating point and output hash are
  frozen into the contract) and by twelve operational takes that all stopped
  before any outcome access.
- **Dataset:** ISLES'24 public training release, Zenodo record 16813698
  (published 2025-08-12), archive `train.7z`, md5 `36ae28b9a17f7340b8bbef62b595cb57`,
  sha256 `038920e4dc2011a3f47b8bb8421c67e36d07f1d84f1ba442563077480f75d129`,
  2,981 archive members, 149 released cases.
- **Primary metric:** per within-patient CBF-percentile band (three bands:
  [0,33), [33,67), [67,100] of finite deficit CBF), the equal-patient-weight
  mean of d = risk(Q1 low-CBV) − risk(Q4 high-CBV), where Q1/Q4 are the
  patient's own label-blind log-CBV quartile cells inside the eroded
  Tmax>6s deficit region; 95% patient-bootstrap percentile CI, 2,000
  resamples, `numpy default_rng(20260824)`. Preregistered gate: the
  three-band conjunction in `analysis.pass_rule` (same nonzero sign in all
  three bands; ≥2 of 3 CIs excluding zero in that direction; every CI width
  ≤ the frozen 0.15).
- **Contract blob:** `03d4545fe293f0067c69ce9e9e696ec97b894d7b`; the
  standing approval marker (`ideas/023/HUMAN_APPROVED_PROBE`, approved
  2026-08-28T02:31:13Z) binds exactly this blob, and the run's gate recorded
  the same blob for both contract and approval.
- **Results bundle:** `probes/023/results/results_v2/`, imported at commit
  `1c0acdbf5dccabd00449c5235b5e83e3bb369f51`. All citations below resolve
  inside that bundle at that commit unless another path is given.
- **Families:** interpretation authored by the Claude family (interpret-build
  leg 1); revised in round 2 per the round-1 cross-family review
  (`interpret_review.md`); re-review pending.
- **Out-of-scope warnings.** This result must NOT be read as: evidence about
  autoregulatory blood-volume reserve, vasodilatory capacity, collateral or
  reperfusion mechanism, or any causal physiology; a CBV-versus-MTT channel
  claim (the central-volume identity holds almost exactly in these maps, so
  they are one degree of freedom at fixed CBF); evidence that any model uses
  or ignores anything (no model was probed); evidence that CBV/MTT lacks
  biological importance; or a statement about the reserved 49 cases, the
  hidden test set, other cohorts, or other map-generation pipelines (all
  maps are icobrain cva output; the treated-cohort scope limit stands).

## Where the uncertainty lives

The census is a deterministic CPU analysis of a frozen case set: pinned
archive, hash-frozen split, fixed bootstrap seed, and byte-identical
start/end determinism manifests (`determinism_manifest_start.json` and
`determinism_manifest_end.json` are identical). There is no training or
seed stochasticity; uncertainty is case-level and is carried by the
contract's own patient-bootstrap machinery. Effect statements below are
therefore judged against those intervals, and remain bounded by cohort
scope: one treated cohort, one vendor's maps, 99 analyzed patients.

## Demonstrates

1. **A valid census completed under the approved contract.** Gate passed on
   blob `03d4545fe293…` [cite: run_log.txt | line 1 | approval line]; the
   archive checksum matched the pinned Zenodo record
   [cite: summary.json | archive_md5 | 36ae28b9a17f7340b8bbef62b595cb57]
   [cite: summary.json | zenodo_checksum | md5:36ae28b9a17f7340b8bbef62b595cb57];
   the Phase-S calibration file consumed at run time hashes to the
   contract-frozen value
   [cite: determinism_manifest_start.json | input_paths.phase_s_csv | sha256 = 59069fa92399cd5c600c89e0d66bb4c7c12679e14f12824b54ae0ce6a6061ef4]
   [cite: summary.json | simulation_output_sha256 | 59069fa9…]. The released
   case count resolved to 149 [cite: summary.json | released_case_count | 149],
   settling the contract's 149-vs-150 discrepancy clause by archive census.
2. **The preregistered G-label gate FAILED — the contract's negative
   pattern, not a power failure.**
   [cite: summary.json | g_label_passed | false]
   [cite: summary.json | status | NEGATIVE_PATTERN]. Per band
   (equal-patient-weight mean d; 95% patient-bootstrap CI):
   - Band 1 (lowest CBF): mean d = 0.006391646480739713, CI
     [−0.026830257261146396, 0.0383678779489388], width 0.06519813521008519 —
     includes zero
     [cite: per_stratum_summary.csv | stratum=1 | mean_d, ci_low, ci_high, ci_width].
   - Band 2 (middle CBF): mean d = −0.03200187198047477, CI
     [−0.05590632802084301, −0.007978192339199943], width 0.04792813568164307 —
     excludes zero, NEGATIVE (higher-CBV voxels carry MORE final-infarct
     membership)
     [cite: per_stratum_summary.csv | stratum=2 | mean_d, ci_low, ci_high, ci_width].
   - Band 3 (highest CBF): mean d = 0.02307549118960302, CI
     [0.004965694506583826, 0.04356979149013058], width 0.038604096983546755 —
     excludes zero, POSITIVE (lower-CBV voxels carry more membership)
     [cite: per_stratum_summary.csv | stratum=3 | mean_d, ci_low, ci_high, ci_width].
   The conjunction fails on direction: signs are (+, −, +), and the two
   intervals that exclude zero do so in OPPOSITE directions. Every CI width
   beats the frozen 0.15 bound and support is 99 contributing patients per
   band against a frozen floor of 20
   [cite: per_stratum_summary.csv | stratum=1,2,3 | patients = 99]
   [cite: resolved_config.json | minimum_contributing_patients_per_stratum | 20]
   [cite: resolved_config.json | maximum_primary_ci_width | 0.15], so the
   negative is the decisive kind the contract defined ("mixed or zero
   directions" with adequate preregistered support), not an
   insufficient-support indeterminate.
3. **The central-volume identity holds essentially by construction in these
   maps.** Median absolute centered residual of u = log(CBF·MTT/CBV):
   0.0077610015869140625 (band 1), 0.003559589385986328 (band 2),
   0.0077877044677734375 (band 3), all far below the invalidating 0.10 limit
   [cite: identity_residual_summary.csv | stratum=1,2,3 | median_absolute_centered_residual]
   [cite: summary.json | identity_mad | 1,2,3]. This directly confirms the
   card's one-degree-of-freedom premise (and its prohibition on channel
   attribution) for the icobrain cva maps.
4. **The two authorized exclusions occurred exactly as pre-specified.** The
   known source-defective CBF member excluded sub-stroke0043
   [cite: exclusions.csv | case_id=sub-stroke0043, record_type=excluded_case | reason = source_corrupt_member]
   [cite: summary.json | excluded_source_corrupt_cases | 1]; the duplicate
   non-canonical lesion archive member for sub-stroke0142 was excluded while
   the case's canonical follow-up derivative was retained and analyzed
   [cite: exclusions.csv | case_id=sub-stroke0142, record_type=excluded_archive_lesion | reason]
   [cite: summary.json | excluded_duplicate_lesion_members | 1]. Analyzed
   n = 99 of 100 census cases
   [cite: summary.json | analyzed_census_case_count | 99]
   [cite: summary.json | census_case_count | 100].

## Suggests (exploratory; single cohort, single operationalization)

1. **Band-dependent, opposite-signed label structure.** Only the three-band
   conjunction was preregistered as the gate; the per-band contrasts are its
   components. Read exploratorily, they suggest the released labels carry a
   real but non-uniform relationship to the joint CBV/MTT coordinate: in the
   middle flow band high CBV accompanies MORE infarct membership, in the
   highest band less. This is a citable observation about a modern,
   reperfusion-treated cohort's outcome structure (the census side-result
   the critique anticipated), but with the tissue-composition caveat below
   it must not be promoted to a physiological statement.
2. **The median patient shows almost no contrast; means and medians
   diverge.** Median patient-level d is 0.0 (band 1),
   −0.0005886681383370125 (band 2), 0.000556250836852953 (band 3), with
   median CIs hugging zero
   [cite: per_stratum_summary.csv | stratum=1,2,3 | median_d, median_ci_low, median_ci_high],
   while individual patients can reach large contrasts (cited example:
   sub-stroke0002, band 1: d = −0.20385563685311792
   [cite: per_patient.csv | case_id=sub-stroke0002, stratum=1 | d]). The
   divergence between near-zero medians and the band-2/band-3 means whose
   CIs exclude zero indicates between-patient heterogeneity, which weakens
   any reading of a cohort-wide encoded association. The bundle contains no per-patient
   contribution analysis, so how many patients drive the band means was
   not computed and is not claimed.
3. **The pre-registered HU audit documents Q1-vs-Q4 attenuation imbalance
   in specific cited cases; cohort prevalence was not computed.** The
   label-blind NCCT audit recorded per-case, per-band, per-cell HU
   statistics (594 rows = 99 cases × 3 bands × 2 cells
   [cite: summary.json | bin_tissue_audit_rows | 594]). The bundle contains
   no aggregate HU statistic; the per-case rows are the recorded output,
   and no cohort-level frequency of imbalance is claimed here. The
   following are cited row-level examples only:
   - Band 1 (lowest CBF): cited example cases show Q1 low-CBV cells at
     markedly lower, frankly hypodense median attenuation than their Q4
     cells — sub-stroke0092: Q1 median 3.0 HU vs Q4 23.0 HU
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0092, stratum=1, style_group=Q1_low_CBV | median_hu = 3.0]
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0092, stratum=1, style_group=Q4_high_CBV | median_hu = 23.0];
     sub-stroke0057: 5.0 vs 24.0; sub-stroke0189: 6.0 vs 25.0
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0057, stratum=1 | median_hu rows]
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0189, stratum=1 | median_hu rows].
   - Band 2: cited examples include one balanced case (sub-stroke0002:
     21.0 vs 21.0
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0002, stratum=2 | median_hu rows])
     and one imbalanced in the opposite direction (sub-stroke0183: 23.0 vs
     5.0
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0183, stratum=2 | median_hu rows]).
   - Band 3: cited examples include a higher-attenuation Q4 cell
     (sub-stroke0109: Q1 30.0 vs Q4 58.0
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0109, stratum=3 | median_hu rows])
     and a Q4 cell with very wide HU spread (sub-stroke0133: Q4 IQR 314.5
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0133, stratum=3, style_group=Q4_high_CBV | iqr_hu]),
     the latter consistent, in that case, with residual vessel/hyperdense
     contamination surviving the per-patient p98 CBV cap.
   How often such imbalance occurs across the 99 patients was NOT
   quantified: no governed aggregate analysis of the audit exists, and
   producing one is successor work.
   INFERENCE (labeled as such, bounded to the cited cases): in the cited
   band-1 cases, the frankly hypodense Q1 medians mean the low-CBV voxels
   there are substantially voxels already hypodense on NCCT — established
   tissue injury or partial-volume CSF — so in those cases the Q1-vs-Q4
   contrast partly re-measures visible tissue state rather than a
   hemodynamic state at matched tissue. Under the pre-registered
   2026-08-28 interpretation rule, the recorded outputs cannot certify the
   "HU-balanced" branch (cohort-wide balance was not demonstrated), so the
   tissue-composition caveat is applied conservatively and a
   tissue-normalized successor design is the recorded consequence; whether
   the imbalance is systematic cohort-wide would require a governed
   aggregate analysis that does not exist. (The other branch — "the
   compensation reading stands" — is moot here because G-label failed
   regardless.)

## Does not establish

- That final-infarct outcome in ISLES'24 carries NO joint CBV/MTT
  information. The gate tests one operationalization: within-patient CBF
  percentile bands, per-patient log-CBV quartile extremes, equal patient
  weights. The HU audit's cited example rows show this operationalization
  can mix tissue types within cells (prevalence not quantified); a
  tissue-normalized reference (the retired contralateral mirror was,
  incidentally, exactly that) could still reveal a consistent association.
- How prevalent the Q1-vs-Q4 tissue imbalance is across the cohort, or
  which patients drive the band-level means — no aggregate HU statistic or
  per-patient contribution analysis was computed.
- Anything about autoregulatory reserve, vasodilatory capacity, or the
  physiological cause of the band-2/band-3 sign difference.
- Anything about any model — no model existed or was probed; the planned
  model-use probe was contingent on this gate passing.
- Anything about the reserved 49 cases (untouched
  [cite: summary.json | reserved_case_count | 49]), the hidden test set,
  untreated cohorts, or maps from any pipeline other than icobrain cva.
- CBV-versus-MTT channel structure — explicitly prohibited, and the
  near-zero identity residual confirms the degeneracy is real.

## Validity failures

None. No invalidating-failure class in the contract was triggered: split
frozen before label access (manifest sha256
`da79e94bdae3f59d23db497d5f26f0d57aa4f279847fe57ec9a8d05ebcf18843`
[cite: summary.json | split_manifest_sha256]); provenance, checksum, and
census gates all passed; nonfinite voxels occurred only where permitted and
were counted per case (largest example: sub-stroke0113, 302,261 nonfinite
MTT voxels excluded and recorded
[cite: exclusions.csv | case_id=sub-stroke0113 | nonfinite_mtt_voxels]);
patient clustering and equal weighting preserved by the frozen estimator;
determinism manifests identical at start and end. The take-8 unit
contingency remains executed-and-retired: the vessel exclusion ran as the
unit-free per-patient p98 rule, recorded per case (e.g. sub-stroke0002
vessel_cbv_p98 = 29.140625
[cite: exclusions.csv | case_id=sub-stroke0002 | vessel_cbv_p98]).

## Authorized variants — all reported

- **Phase S (synthetic calibration; outcome-blind).** Separate bundle
  (results branch `results/probe-023-0e223c82f9eb`); its selected operating
  point — 20 patients/stratum minimum, 100 voxels/cell minimum, 0.15 CI
  width — and output hash are frozen in the contract and were re-verified
  at Phase C load [cite: resolved_config.json | minimum_contributing_patients_per_stratum, minimum_voxels_per_patient_quantile_cell, maximum_primary_ci_width]
  [cite: determinism_manifest_start.json | input_paths.phase_s_csv | sha256].
- **Phase C (this run).** `maximum_variants: 1`, one frozen analysis, one
  seed (20260824 [cite: resolved_config.json | seed]). No other analysis
  variant, stratum selection, pooled fallback, or alternate threshold was
  run.
- **Label-blind NCCT tissue audit.** The 2026-08-28-activated run.py-only
  diagnostic; recorded per case/band/cell in `bin_tissue_audit.csv`
  (594 rows); no estimator or gate consumed it.
- **Prior takes 1–12.** Operational stops under this and superseded
  contract eras (staging, census, unit, and mirror-gate stops); none opened
  outcome or lesion data. The label freeze held until take 13.

## Positive and negative findings

- **Negative (primary, preregistered):** G-label failed on directional
  consistency; the Stage-0 keystone — a precise, directionally stable
  outcome association with the joint CBV/MTT state at matched flow — is NOT
  present in the census labels under this operationalization. Per the
  contract this is a scientific negative for the keystone and PAUSEs
  idea 023; it is not evidence that CBV/MTT lacks biological importance.
- **Positive (secondary, exploratory):** (a) the identity-residual census
  confirms the central-volume identity in the released maps (validating the
  one-degree-of-freedom framing); (b) two bands show precise, opposite-signed
  associations — an interpretable observation about label structure in a
  treated cohort, conditional on the tissue caveat; (c) the HU audit
  provides per-case tissue-composition measurements for every analyzed
  case, and its cited example rows document large Q1-vs-Q4 attenuation
  imbalance in specific cases (cohort prevalence not quantified) — direct
  empirical design input for any successor.

## Next decision

**PAUSE**, exactly as the contract's negative_pattern prescribes. No model
work, weight download, or edit inference is authorized; the reserved 49
cases stay untouched. Recommended operator sequence (all outside this
probe's authority): (1) ratify the PAUSED transition; (2) run the
separately pre-registered patient-level clinical-outcome join
(2026-08-28 entry) as its own gated step; (3) if the joint-state question
is to continue, register a tissue-normalized matched-flow successor
(parent idea-023) through the normal pipeline — the HU audit and the
band-2/band-3 sign reversal are its empirical starting points — noting
that the retired mirror design was the implicit tissue normalizer;
(4) the queued upstream report of the sub-stroke0043 source defect stands.


===== ideas/023/keystone_screen.md =====
# Keystone screen

## Keystone as stated

> Per-case CBV, CBF, MTT, and Tmax maps coexist co-registered in a common (NCCT) space so mirror indices and joint channel edits run automatically on every case.

## What I inspected

I inspected the official ISLES'24 GitHub repository's data schema and the official Zenodo release record for the public training archive, rather than relying on an abstract or search result.

The official Zenodo record states that the release contains 149 training cases and then makes the per-case completeness claim explicitly:

> “For each case, the following data are included: Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

Source: https://zenodo.org/records/16731717, **Description**, opening paragraph and first bullet under the case contents (record metadata inspected through https://zenodo.org/api/records/16731717 on 2026-08-17).

The same record defines the derivative-space relationship:

> “'Derivatives' include all modalities linearly co-registered to the NCCT space.”

Source: https://zenodo.org/records/16731717, **Data structure** paragraph.

Its displayed derivative schema places all four files under the same subject, acute session, and `perfusion-maps` directory, with `space-ncct` in every filename:

> “sub-strokecase0001_ses-0001_space-ncct_tmax.nii.gz”  
> “sub-strokecase0001_ses-0001_space-ncct_mtt.nii.gz”  
> “sub-strokecase0001_ses-0001_space-ncct_cbf.nii.gz”  
> “sub-strokecase0001_ses-0001_space-ncct_cbv.nii.gz”

Source: https://zenodo.org/records/16731717, **Data structure**, `derivatives/sub-strokecase0001/ses-0001/perfusion-maps/` listing. The same four-file layout is independently reproduced in the official repository at https://github.com/ezequieldlrosa/isles24/blob/main/README.md, lines 26–35.

These statements jointly verify the stated prerequisite: the four named maps coexist per case and derivative versions are in NCCT space. This is schema-level inspection of the official release, not a census of the headers inside the 99 GB `train.7z` archive.

## Residual-assumption check

**Mandatory question:** If this card only verified the nearest checkable thing, what is it still assuming?

The nearest fact would have been merely that the release contains four map *types*. The additional load-bearing facts are that they coexist for each case and that the derivative copies share NCCT physical space. The official release description explicitly verifies both, so the card did not stop at the nearest fact.

One narrower implementation assumption remains: “co-registered to NCCT space” does not verbatim promise byte-identical NIfTI dimensions, voxel sizes, or affine matrices across the four files. That does not overturn the stated keystone because common NCCT physical space permits deterministic resampling before voxelwise measurement or editing. A header census should nevertheless gate later work; missing files or irreconcilable affine/coverage differences would be a release-integrity exception, not evidence currently contradicting the official per-case schema.

The card also assumes that mirror estimation will be reliable and that the map values have usable joint support and scaling. Those are explicitly listed Stage 0 validity gates. They affect interpretability of the proposed experiment but are not substitutes for the present data-existence/co-registration keystone.

```json
{"verdict": "PASS", "evidence": "For each case, the following data are included: Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).", "source": "https://zenodo.org/records/16731717 — Description, first case-contents bullet; paired with Data structure statement that derivatives include all modalities linearly co-registered to NCCT space", "note": "Official release schema verifies per-case coexistence and common NCCT space; exact NIfTI grid/header compatibility remains a cheap Stage 0 census."}
```


===== ideas/023/probe_contract.yaml =====
# Probe contract v1 -- idea 023, mirror-free Stage-0 outcome census only.
# Drafted at probe_plan on 2026-08-24. No probe code or execution is
# authorized until the human approval gate is satisfied.

idea_id: "idea-023"
contract_version: 1
track: exploratory

authorities:
  charter: "charters/isles24/CHARTER.md"
  idea_card: "ideas/023/idea_card.json"
  feasibility_memo: "ideas/023/feasibility.md"
  reconciliation: "ideas/023/reconciliation.md"
  decision_entries:
    - "2026-08-17 -- Ideas 021 and 023: human inspection questions answered"
    - "2026-08-24 -- Reconciliation ruling: idea 023"
    - "2026-08-27 -- Operator reframe AND DECISION: 023 goes mirror-free; directive for the amendment round"

question: "In a frozen census subset of released ISLES'24 training patients, is final-infarct membership associated precisely and directionally with the native joint CBV/MTT state within three within-patient CBF-percentile bands, with enough support to justify a later model-use probe?"
risky_assumption_tested: "The released outcome labels contain a patient-replicated, estimable joint-CBV/MTT association at matched CBF; map coexistence alone does not establish this keystone."

scope:
  included: "CPU-only schema and map census, synthetic operating-characteristic calibration, and one frozen model-free outcome analysis on census patients."
  excluded:
    - "Model training, model-weight download, inference, counterfactual map editing, and any test of model use."
    - "Any claim of autoregulatory reserve, remaining vasodilatory capacity, causal physiology, or CBV-channel rather than MTT-channel use."
    - "Any analysis of the hidden ISLES'24 test set or of patients reserved for a later toggle evaluation."

approval_and_phasing:
  phase_S_synthetic_freeze:
    approval_scope: "Synthetic data and outcome-blind release metadata only. No real lesion mask, outcome field, or label-derived statistic may be opened, summarized, or logged."
    work: "Recalibrate the exact patient-clustered estimator at census n=100 for three within-patient CBF-percentile bands and within-band CBV quartiles. Select the smallest support requirements and largest admissible CI-width threshold that achieve both >=0.80 power at the frozen minimum relevant risk difference and <=0.05 false-positive rate under the null."
    frozen_simulation_constants:
      census_patients: 100
      reserved_patients: "all remaining released training patients; expected 49 or 50 pending the pinned-release case census"
      rng_seed: 20260824
      bootstrap_replicates: 2000
      minimum_relevant_absolute_risk_difference: 0.05
      null_replicates: 2000
      alternative_replicates: 2000
      candidate_minimum_contributing_patients: [20, 25, 30, 35, 40]
      candidate_minimum_voxels_per_patient_cell: [50, 100, 200]
      candidate_maximum_ci_width: [0.08, 0.10, 0.12, 0.15]
      data_generating_grid: "For each candidate N and M and each of three within-patient CBF-percentile bands, draw one latent patient risk p_i from Beta(alpha, beta), where alpha = p0*(1/rho - 1), beta = (1-p0)*(1/rho - 1), p0 is in {0.10, 0.30, 0.50}, and rho is in {0.01, 0.05, 0.10}. Draw high-CBV-quartile infarct count as Binomial(M, p_i) and low-CBV-quartile count as Binomial(M, min(p_i + delta, 1)); delta=0 for null replicates and delta=0.05 for alternative replicates. Analyze each replicate with the exact three-band conjunction and patient bootstrap specified for Phase C."
      selection_rule: "A candidate (N, M, CI width) is eligible only if the conjunction's false-positive rate is <=0.05 for every (p0, rho) null cell and power is >=0.80 for every (p0, rho) alternative cell. Select lexicographically by smallest N, then smallest M, then largest eligible CI width. If no candidate is eligible, Phase S fails and Phase C is not authorized; changing the grid or effect size requires a new contract."
    outputs_to_amend:
      minimum_contributing_patients_per_stratum: 20
      minimum_voxels_per_patient_quantile_cell: 100
      maximum_primary_ci_width: 0.15
      simulation_output_sha256: "59069fa92399cd5c600c89e0d66bb4c7c12679e14f12824b54ae0ce6a6061ef4"
    exit: "Record the selected values and simulation-output SHA-256 in this contract. That amendment changes the contract blob and invalidates the Phase-S approval by construction. Fresh human approval against the amended contract is required for Phase C."
  phase_C_real_census:
    entry_condition: "Every Phase-S placeholder has been replaced, the simulation output hash verifies, and a fresh HUMAN_APPROVED_PROBE marker is bound to this amended contract blob."
    scope: "Pin and inspect the released data, deterministically freeze the patient split without reading labels, then run exactly the outcome census specified below."

dataset:
  name: "ISLES'24 public training release"
  source: "Official Zenodo concept record 16731717; select one immutable child record at Phase C and record its record id, publication date, train.7z checksum supplied by Zenodo, downloaded SHA-256, case count, and archive member manifest before analysis."
  expected_population: "149 or 150 acute-stroke cases; the recorded discrepancy between release description and challenge paper must be resolved by archive census rather than assumed."
  required_inputs: "Per-case NCCT-space CBF, CBV, MTT, Tmax derivatives and the final-infarct mask. NCCT is no longer required because the approved mirror-free design contains no brain reflection or reference anatomy. Raw 4D CTP, NCCT, CTA, clinical covariates, and model assets are outside this probe. The verified source-defective member train/derivatives/sub-stroke0043/ses-01/perfusion-maps/sub-stroke0043_ses-01_space-ncct_cbf.nii.gz is CRC-valid in the checksum-verified source archive but has an unreadable gzip stream; exclude that case as source_corrupt_member, name the member in schema_census.csv and exclusions.csv, continue the analysis, and surface the excluded case count. Any other unreadable required member is not authorized for exclusion and fails loudly."
  license: "CC BY-NC-SA 4.0, non-commercial research use."
split_policy: "Development data only. Sort immutable case identifiers lexicographically, hash each as SHA-256('idea-023-v1|' + case_id), assign the 100 lowest hashes to the census and reserve every other case untouched for any later contract. Freeze split_manifest.csv and its SHA-256 before opening lesion masks. No case crosses populations."

preprocessing:
  grid_gate: "For every census case, require finite CBF/CBV/MTT/Tmax and lesion-mask values in all analyzed voxels (nonfinite values outside the analysis region are permitted, excluded, and counted), compatible physical coverage, and a deterministic common NCCT grid. Header mismatches may be resolved only by the preregistered interpolation rule: linear for maps, nearest-neighbor for labels; record every resampling. Irreconcilable coverage is invalidating."
  region: "Tmax > 6 s deficit tissue, eroded by one voxel; exclude voxels within two voxels of the array midline and voxels with CBV above the per-patient 98th percentile of finite positive CBV in that patient's map. The midline exclusion is an unchanged region-boundary safeguard, not reference anatomy. This unit-free vessel rule replaces the planned 8 mL/100 g cap because the payload has zero JSON sidecars, empty NIfTI descrip fields, and no inspected dataset descriptor states CBV units; under the conventional CBV scale, the percentile targets approximately the vessel fraction that the 8 mL/100 g cap intended."
  matched_flow: "Within each patient, rank finite CBF values inside the final eroded deficit region and form three fixed bands using deterministic percentile boundaries: [0,33), [33,67), and [67,100]. Ties at a boundary are assigned by stable voxel-index order so every eligible voxel belongs to exactly one band. No contralateral or external reference is used."
  cbf_strata:
    - "within-patient CBF percentile [0,33)"
    - "within-patient CBF percentile [33,67)"
    - "within-patient CBF percentile [67,100]"
  joint_state: "Within each patient's matched-flow band, primary coordinate z = log(CBV), and Q1 versus Q4 is defined by that patient's own label-blind CBV quartiles. MTT is not a second independent predictor. Where all terms are positive, compute u = log(MTT) - log(CBV) + log(CBF), then subtract the census-wide median u so constant unit-conversion factors cancel. Report this centered identity residual; a median absolute centered residual exceeding 0.10 in any band invalidates this coordinate and stops before outcome modeling."

analysis:
  analysis_unit: "Patient. Voxel observations are never treated as independent for uncertainty. Each patient contributes equal total weight within each CBF-percentile band regardless of voxel count."
  native_quantiles: "Within each patient's CBF-percentile band, estimate that patient's z quartile cut points without labels. For every patient with sufficient voxels in both Q1 and Q4, compute final-infarct fraction in Q1 and Q4 and the signed contrast d = risk(Q1 low-CBV) - risk(Q4 high-CBV)."
  primary_metric: "Per CBF-percentile band, the equal-patient-weight mean of d with a patient bootstrap percentile 95% CI (2000 resamples, numpy default_rng(20260824)). Positive d means lower joint-state position is associated with greater final-infarct membership within that patient's matched-flow band."
  secondary_metrics:
    - "Median patient-level d and its patient-bootstrap 95% CI per stratum."
    - "Counts of patients and voxels in each patient-by-band-by-quantile cell and exclusion fractions."
    - "A label-blind native-support plot of z by within-patient CBF-percentile band and the identity-residual distribution."
  pass_rule: "G-label passes only if all three strata meet the Phase-S-frozen support minimum; all three primary point estimates have the same nonzero sign; at least two of three 95% CIs exclude zero in that common direction; and every primary CI width is <= the Phase-S-frozen maximum. Otherwise G-label does not pass."
  multiplicity_and_scope: "The three-stratum conjunction is the single preregistered gate; no stratum selection, pooled fallback, alternate threshold, or post-hoc subgroup can rescue a failure."

primary_metric: "Per within-patient CBF-percentile band, equal-patient-weight mean risk(Q1 low-CBV) minus risk(Q4 high-CBV), with a 2000-replicate patient-bootstrap percentile 95% CI; the preregistered gate is the three-band conjunction in analysis.pass_rule."
secondary_metrics:
  - "Median patient-level Q1-minus-Q4 risk contrast with patient-bootstrap 95% CI per stratum."
  - "Patient/voxel support, exclusion fractions, and central-volume identity residuals."

maximum_variants: 1
maximum_gpu_minutes: 0
maximum_seeds: 1
stopping_rule: "Stop after Phase S until the contract is amended and freshly approved. In Phase C, stop when the frozen census and required outputs complete, immediately on an invalidating failure, or when any scope boundary would be crossed. Do not proceed to model work regardless of result."

positive_pattern: "The schema, grid, central-volume, and support gates pass; the three within-patient CBF-band contrasts share a direction; at least two intervals exclude zero; and every interval satisfies the frozen precision bound. This supports only that the outcome-associated joint-state prerequisite is present in the census population and permits a later, separately approved model-probe contract to be considered."
negative_pattern: "A valid completed census fails the directional/precision conjunction: mixed or zero directions, fewer than two intervals excluding zero, or intervals wider than the frozen bound despite adequate preregistered support. This is a scientific negative for the Stage-0 keystone and PAUSEs idea 023; it is not evidence that CBV/MTT lacks biological importance or that any model ignores it."

invalidating_failures:
  - "Approval breach: any real outcome or lesion-mask access during Phase S, or Phase C execution without a fresh approval bound to the post-Phase-S contract blob."
  - "Provenance failure: the immutable Zenodo child record, archive checksum, downloaded SHA-256, archive member manifest, or split manifest is missing or mismatched."
  - "Population failure: duplicate patient identity, inability to resolve the released case count, a missing required map or label for a census patient (distinct from a present source_corrupt_member handled by dataset.required_inputs), or any reserved patient entering analysis."
  - "Grid/coverage failure: required images cannot be placed on a common NCCT physical grid by the frozen rule, or nonfinite values remain in analyzed voxels."
  - "Retired contingency (formerly kill-code 104): undocumented CBV units triggered the preregistered stop before outcomes were read; this amendment executes and retires that unit-failure path by replacing the sole unit-dependent rule with the frozen percentile exclusion."
  - "Coordinate failure: central-volume identity residual exceeds the frozen 0.10 limit in any stratum; the empirical-curve fallback requires a new contract and is not a negative result."
  - "Support invalidity: any stratum fails the Phase-S-frozen minimum contributing-patient or voxel-cell requirement. Insufficient support is invalidating/indeterminate, not a negative association."
  - "Analysis deviation: labels influence preprocessing, split assignment, quantile boundaries, exclusions, or choice of analysis; an unregistered variant or seed is run; or patient clustering/equal weighting is not preserved."
  - "Output failure: required per-patient contributions, exclusions, configurations, provenance, or environment records are missing or nonfinite."

baselines:
  - "Zero association: primary patient-level contrast d = 0."
  - "Outcome-blind coverage and support gates; these validate measurement and cannot count as positive evidence."

claim_discipline:
  permitted: "In this frozen ISLES'24 census subset, lower versus higher native joint CBV/MTT position within within-patient CBF-percentile bands was (or was not) associated with final-infarct membership with the reported patient-clustered precision."
  prohibited:
    - "Autoregulatory blood-volume reserve, remaining dilation capacity, collateral mechanism, reperfusion mechanism, or causal tissue salvageability."
    - "CBV-channel attribution rather than MTT-channel attribution."
    - "Model use, benchmark-model behavior, generalization to the hidden test set, or clinical utility."
    - "Treating an invalidating failure, insufficient support, or an invalid run as a scientific negative."

required_outputs:
  - resolved_config.json
  - simulation_operating_characteristics.csv
  - simulation_summary.json
  - provenance.json
  - archive_manifest.csv
  - split_manifest.csv
  - schema_census.csv
  - per_patient.csv
  - per_stratum_summary.csv
  - support_summary.csv
  - identity_residual_summary.csv
  - exclusions.csv
  - summary.json
  - environment.txt
  - run_log.txt

open_questions_for_human:
  - "Approval-flow confirmation: first approval authorizes Phase S only. Real-data Phase C requires the Phase-S values and output hash to be amended into this file and a fresh hash-bound approval."
  - "The contract deliberately omits treatment/reperfusion adjustment because the reduced claim is association in the released cohort and inspected sources have not verified that mTICI/timing fields are present in the latest release. If those covariates are required for the intended claim, amend the contract before Phase S; do not add them after outcome inspection."

human_approved: false


===== ideas/023/probe_review.md =====
# Probe code review — idea 023, round 9 (re-review of the HU tissue-audit revision after the round-8 blocking fixes)

**Reviewed artifacts:** `probes/023/run.py` (SHA-256
`ff237ea7af332554daed8cd295204084a2b4a9394761b66f78dd1bd5f3a5bf23`),
`probes/023/README.md` (SHA-256 `e5a02810…`), `probes/023/requirements.txt`
(SHA-256 `ff705c03…`, byte-identical since round 2), and
`ideas/023/probe_contract.yaml` (git blob
`0e223c82f9eb879652a549df9bf857c155ef61db`, byte-identical to the round-7
amended contract and to the blob round 8 reviewed). All hashes recomputed
this round and matching `probes/023/verification.json`.

**Hash lineage (verified):** approved run.py `80af2c87…` is byte-identical
at the approval commit (`68057ec`) and at the revision parent (`8df3a95`);
the round-8-reviewed HU-audit code is `ecb2e0f9…` (commit `4403d4c`); the
present artifact is `ff237ea7…` (commit `0e840d0`). The `9e843c7..0e840d0`
probe delta is 13 lines in run.py (one hunk, inside `tissue_audit`),
18 lines in README.md, and the verification.json refresh — nothing else.
The complete delta from the approved artifacts is therefore the round-8
audited 63-line HU-audit diff plus this bounded two-finding fix.

**Approval state (verified):** `ideas/023/HUMAN_APPROVED_PROBE` binds blob
`0e223c82…` and the contract is still blob `0e223c82…` — the standing
approval **remains valid**, per the 2026-08-28 activation ("contract
untouched; standing approval holds through verify"). Fail-closed sequencing
is unchanged: the Phase-S placeholders still block Phase C, the pending
mechanical amendment will stale this approval by construction, and the
Phase-C checkpoint identity includes the run.py hash (run.py:768), so
nothing checkpointed under either superseded code revision can be consumed
by this one (exit 4 at run.py:771-772).

**Requirements conformance (review rule 5):**
`ideas/023/contract_requirements.md` does not exist (verified this round);
not a requirements-governed contract. Not applicable.

**Review basis:** as in rounds 3–8, this review environment cannot execute
Python; executed-check attestations in verification.json (py_compile, smoke
0.303 s with `contract_satisfied: false`, and the four fixtures including
the new `empty_flow_band_tissue_audit_fixture`) plus line-level static
tracing are the basis.

---

## Disposition of the round-8 blocking findings

**B1 (empty flow band crashed the take as exit 13) — RESOLVED, verified
against every interacting invariant.** The fix is exactly the prescribed
shape. `tissue_audit` now branches on `z.size` (run.py:567-576): a
non-empty band keeps the original finite-cut assert and style selections;
an empty band asserts the cuts are NaN and emits both style rows with
empty selections, which flow into the existing empty-support branch
(run.py:591-596) as `member_voxels: 0` with blank HU statistics. Checked
against the code it must agree with:

- **The NaN asserts are internal-consistency checks, not a new gate.** The
  sole `tissue_audit` call site (run.py:811) passes quartiles computed at
  run.py:804-810, which are NaN exactly when a band is empty and
  `np.quantile` of the band's finite log-CBV otherwise — so neither branch
  assert can fire on contract-valid input. Region construction guarantees
  finite positive CBV/CBF/MTT in every band member (run.py:512, 520-522),
  so a non-empty band always yields finite ordered cuts.
- **Empty bands genuinely occur on valid input**, confirming the finding
  was real: `flow_band_labels` leaves band 3 empty for a two-voxel region
  and bands 2-3 empty for one voxel (run.py:535-538), and a fully
  eroded-away region produces three empty bands while still flowing
  through `coordinate_arrays`, `patient_native_z`, and the census
  aggregation (the all-patients-empty case still fails loudly at
  run.py:850-851).
- **All three row-count invariants survive:** `assert len(rows) == 6`
  (run.py:599), the resume-path assert (run.py:784), and the CSV
  reconciliation `6 × analyzed cases` (run.py:846).
- **Symmetry with the estimator's tolerance is restored:**
  `patient_measure` skips `z.size < 4` cells before touching the cached
  cuts (run.py:613-615), so NaN cuts are never read anywhere, and the
  frozen support gates — not a crash — now decide the small-deficit
  patient in both the audit and the estimator. The row's
  finite/nonfinite/member accounting assert holds trivially (0+0=0,
  run.py:597).

**B2 (README extraction set omitted the NCCT the code requires) —
RESOLVED.** `README.md:28` adds `{raw_data,rawdata}/**/*_ncct.nii.gz` to
the mandated extraction set, tolerating both payload spellings in the same
declaration style as the existing derivative globs, and `README.md:40-41`
now states "Rawdata NCCT is used only for the label-blind per-bin
tissue-composition audit; raw 4D CTP and CTA are not used" — matching
run.py:454 (NCCT hard-required per census case) and run.py:452-453 (the
diagnostic-only framing). `find_one` resolves by recursive glob with exact
filename suffix (run.py:255, 259-260), so it is directory-spelling
agnostic and fails loudly (exit 5) on zero or multiple matches; the NCCT
stream passes through `verify_required_gzip` with every other required
member (run.py:459-460). The take-13 launcher regenerated from this
declaration at package-colab will now extract what the code needs (R15).

**R12 (README duplicate-lesion sentence mispredicted the payload) —
RESOLVED in the same authorized touch, as round 8 requested.** The new
sentence (README.md:33-38) now states the code's actual policy and matches
`archive_case_inventory` clause for clause: the unique canonical follow-up
`ses-02` derivative is preferred (run.py:302-307), deterministic
lexicographic selection is permitted only when all candidates share
identical archive size and CRC (run.py:311-317), anything else stops as a
population failure (exit 5, run.py:315-316), and every non-retained member
is named in both `schema_census.csv` and `exclusions.csv`
(run.py:319-324, 749-761) with the count surfaced in `summary.json`
(run.py:962). Pass two loads the lesion by its exact selected archive path
(`find_archive_selected`, run.py:634), so the additionally extracted
duplicate member cannot trip a `find_one` multiplicity failure.

## Delta audit (nothing beyond the fixes)

The single run.py hunk touches only `tissue_audit`'s selection logic.
`patient_measure`, the bootstrap, the three-band conjunction, all gates,
Phase S, the split machinery, checkpoint identity, and the exit taxonomy
are byte-identical to the round-8-reviewed code, which was itself verified
against the approved baseline. The closing summary and interpretation
templates are unchanged (run.py:957-966, 1004-1010): status is reported
only as the contract's POSITIVE_PATTERN/NEGATIVE_PATTERN language, and no
HU-balance judgment is made — the pre-registered balanced/imbalanced rule
stays with the interpret stage. requirements.txt is byte-identical; no new
dependency, RNG, or network access enters. verification.json was refreshed
in the same commit with matching hashes and a new attested fixture for the
empty-band path ("six rows with zero members and blank HU statistics"),
which agrees with the static trace above.

## Standards checklist

(1) Start/end determinism manifests present and asserted equal in both
phases (run.py:242-244, 968-970). (2) Exclusions log with reasons:
unchanged, plus the duplicate-lesion and source-corrupt rows in both audit
CSVs. (3) Assertion per transform: the fix replaces the one wrong-in-kind
assert with branch-appropriate internal-consistency asserts; shape,
band-size, quantile-ordering, and voxel-accounting asserts all retained.
(4) Seeds and paths declared; no hidden state or analysis-time network.
(5) Split manifest hashed before any outcome/label access; the audit runs
entirely in the label-blind pass one. (6) `--smoke` synthetic-only,
attested 0.303 s, `contract_satisfied: false`, and cannot reach Phase C or
the audit. All six met.

## Carried non-blocking findings

- **N1 (contract text still declares NCCT outside the probe):** carries to
  the mechanical Phase-S amendment — the operator decides there whether
  the amendment absorbs a sentence naming the rawdata NCCT as an
  audit-only diagnostic input and whether `bin_tissue_audit.csv` joins
  `required_outputs`. Nothing in this round changes that analysis.
- **N2 (missing/unreadable NCCT exit-class labels are latent
  misclassifications):** carries unchanged; fail-loud remains the
  conservative default and both classes remain latent per the archive
  manifest and the two integrity sweeps.
- **N3 (audit rows inherit R16's degenerate-quartile overlap semantics):**
  carries. The README touch was correctly scoped to B2+R12 and did not add
  the R16/N3 sentence; when the README next gains it, extend one clause to
  the audit rows so the interpret stage does not rediscover the overlap.
- **R13 (dead `load_label=True` branch of `load_case`, run.py:455-456):**
  hygiene carry; sole call site still passes False.
- **R14 (nonpositive-map voxel exclusions uncounted in the exclusions
  record):** carries unchanged.
- **R15 (launcher is the Phase-S-era artifact):** `colab_probe_023.ipynb`
  is untouched since `aadb44e`, as expected; the take-13 Phase-C launcher
  must be regenerated at package-colab from the now-corrected README
  declaration, NCCT glob included.
- **R17/N4 (cosmetics):** carry; `resolved_config.json` still reports
  `"label_blind_ncct_tissue_audit": true` in phases where no audit runs
  (run.py:992).

## Verdict

Both round-8 blocking findings are fixed exactly as specified and nothing
else moved: the empty-band guard makes the audit tolerate the same input
class the estimator already tolerates while preserving every row-count
invariant, the README's extraction set and input declarations now match
the code (closing the launcher-omission class that killed Phase-C
attempt 1), and the stale duplicate-lesion sentence was corrected against
the actual selection logic in the same touch. The contract blob is
untouched, the standing approval remains validly bound, the estimator,
gates, and claim language are byte-identical to the approved-plus-audited
baseline, and the delta from the approved code is fully accounted for.
The code is ready for the next sequence step: the mechanical amend-contract
from the mirror-free Phase-S bundle (where N1 is queued for the operator),
fresh approval against the new blob, and package-colab regeneration of the
take-13 launcher.

```json
{"verdict": "APPROVE", "blocking": [], "note": "Round-8 B1 (empty-band assert crash) and B2 (README extraction set omitting the required NCCT) plus carried R12 are fixed exactly as prescribed with a 13-line run.py hunk and a scoped README touch; estimator, gates, contract blob, and approval binding all verified unchanged — clear for the mechanical Phase-S amendment, fresh approval, and take-13 packaging."}
```


===== ideas/023/reconciliation.md =====
# Reconciliation audit — idea 023

## Scope and charter comparison

All archived stage prompts required by this audit are present and readable:
`prompt_critique.md`, six round-specific debate prompts,
`prompt_debate_summary.md`, `prompt_revise.md`,
`prompt_keystone_screen.md`, and `prompt_feasibility.md`.

Their injected charter sections are identical to one another (the extracted
sections have the same SHA-256,
`190a2a5c425368df89f36a094c03113f04b6ce83faf6ac5958c80d627c0e411d`) but
diverge from the current `charters/isles24/CHARTER.md`. The archived prompts
contain the baseline program to decode signals used by medical-imaging models,
including the mandatory physician-readable “the model is using X” deliverable,
the three-rung framework, and the hard rule that X be measurable without a
human annotator. The corrected charter instead makes ISLES'24 the program
driver, admits a broad range of testable uses of the dataset, and penalizes
only *new* annotation burden.

The rulings below therefore are dependency rulings, not trivial text-identity
rulings. Mentions of the old charter's vocabulary were not treated as taint
unless a recorded conclusion required the divergent rule.

## Ruling table

| Artifact | Ruling | One-line basis |
|---|---|---|
| `critique.md` | STANDS | Its `ADVANCE TO REVISION` conclusion follows from dataset/map provenance, CBV–MTT degeneracy, intervention identifiability, outcome-label support, model scope, and feasibility; none requires the baseline-only deliverable or annotation rule. |
| `debate.md` | STANDS | The debate's successive repairs concern the load-bearing outcome gate, joint-channel identifiability, the unsupported mirror-normal kink, and model-family scope; these scientific objections remain operative under the ISLES'24 charter. |
| `consensus.md` | STANDS | The summary accurately records the debate's agreements, unresolved construct-validity issue, amendments, and `REVISE` recommendation; that recommendation is grounded in measurement validity rather than the divergent program focus. |
| `revision.md` | STANDS | The narrowed joint-state claim implements the later human ruling recorded in `evidence/decisions.md` and the scientific finding that baseline maps cannot measure remaining vasodilatory capacity; its use of “rungs” is inherited terminology, not a dependency of the narrowing decision. |
| `keystone_screen.md` | STANDS | This is a factual official-release schema ruling about the presence and NCCT-space registration of CBF, CBV, MTT, and Tmax maps; the charter mismatch has no bearing on its `PASS`. |
| `feasibility.md` | STANDS | The scoped Stage-0 `GO` is based on verified ISLES'24 access, license, cohort, maps, labels, released models, compute, and edit-validity gates, and explicitly follows the binding human reduced-claim decision. |

## Dependency findings

No artifact is TAINTED, so no stage is identified for re-running.

Several artifacts visibly use concepts emphasized by the archived baseline
charter—especially “rung 1/2/3,” a physician-legible named signal, automatic X
measurement, and the analogy audit. Those passages do not control the recorded
verdicts here. The current ISLES'24 charter independently permits
interpretability studies, values testability and concrete dataset use, and
retains the use-versus-association and identifiability discipline. Moreover,
the stricter baseline no-annotator rule did not exclude this candidate: its X
is computed from released maps, its primary readout is label-free, and use of
the existing final-infarct labels incurs no penalty under the corrected
annotation rule.

The most consequential narrowing—from “autoregulatory blood-volume reserve”
to an “outcome-associated joint CBV/MTT decision boundary”—also does not depend
on the baseline charter. It is fixed by the 2026-08-17 human decision after the
construct-validity question was answered: ISLES'24 has baseline maps but no
vasodilatory challenge, so the data cannot measure remaining dilation capacity.
That reasoning is scientific and dataset-specific, and is at least as relevant
under the corrected charter.

## Overall recommendation

**CLEAR-TO-CONTRACT.** Every audited artifact STANDS. This is a reconciliation
recommendation only; it does not authorize a contract, Stage 0 execution,
model training, or probe work, and the human gate remains controlling.

## In plain terms

The earlier stages were run with the wrong general research charter in their
prompts. I checked whether that wrong text actually caused any of their
decisions. It did not: the criticism, revisions, factual data check, and
feasibility decision all rest on properties of ISLES'24, the physiology the
dataset can and cannot measure, and the validity of the proposed experiment.
Some older vocabulary remains in the documents, but removing that vocabulary
would not change a verdict. No stage needs to be rerun for charter reasons.


===== ideas/023/revision.md =====
# Revision — idea 023

## Outcome

The card now asks one defensible rung-1 question: whether a specified map-input final-infarct model uses the joint CBV/MTT compensation state at matched CBF deficit. It no longer claims that the experiment identifies autoregulatory reserve. That physiological name requires an independent endpoint that ISLES'24 does not currently supply.

No probe or model work is authorized by this revision. Stage 0 and human review remain prerequisites.

## Material changes

1. **Narrowed the deliverable.** The original autoregulatory-reserve sentence is retained verbatim in `deliverable_original`. The revised sentence is cohort- and model-scoped and names only the independently computable joint CBV/MTT state at matched CBF.

2. **Made rung limits explicit.** The card claims only conditional rung 1. Vendor/map-generation robustness is required for rung 2; an independently measured autoregulatory endpoint is required for rung 3.

3. **Removed decorative architecture.** Little's law, queueing, and control-engineering language no longer motivates or determines the experiment. The central-volume identity remains only as a map-dependence and edit-validity constraint.

4. **Replaced the wrong keystone.** Map coexistence is recorded as an inspected executability fact, not the keystone. The real `NOT_INSPECTED` prerequisite is a precise, supported outcome relationship with the continuous joint state at matched CBF. Feasibility and novelty confidence are capped at 3.

5. **Answered the mandatory residual question.** The card states that schema inspection does not establish the outcome relationship, native support, or grid compatibility. These assumptions become explicit gates.

6. **Added a frozen, CPU-first Stage 0.** Before outcome inspection it freezes patient splits, support and precision criteria, rCBF strata, candidate response shapes, support-edge separation, and treatment/reperfusion handling. It then audits file headers, map identity residuals, mirror quality, outcome shape, native support, and model assets.

7. **Removed the assumed mirror-normal ceiling.** No kink at `rCBV_mirror = 1` is presumed. The outcome census is continuous. A feature inseparable from the empirical support boundary produces an indeterminate exit, not a reserve claim.

8. **Separated census and probe patients.** Cases used to estimate the outcome relationship cannot supply the later confirmatory edit evaluation.

9. **Simplified the experiment.** The confirmatory intervention moves CBV and MTT jointly along the native conditional curve at fixed CBF and Tmax. The question is use versus non-use of that one joint state. The earlier construct-versus-generic-channel saturation architecture is removed because it did not identify autoregulation.

10. **Prohibited channel attribution.** When the central-volume identity holds, CBV and MTT are one degree of freedom at fixed CBF. The study cannot say which channel the model reads.

11. **Scoped the model claim.** The primary model is maps-only and must have a frozen recipe. A self-trained model supports claims only about that family and recipe. Released participant weights are included only after their exact inputs and provenance are inspected; multimodal models are secondary.

12. **Strengthened edit-validity controls.** Native conditional bounds, zero-dose repeats, off-deficit edits, matched shams, a Tmax positive control, and an indeterminate support-edge rule are now required. Identity-violating edits are exploratory only.

13. **Made alternatives explicit.** The revision addresses scanner, vendor, site, protocol, reconstruction, positioning, habitus, prevalence, referral pathway, report leakage, support-density saturation, multimodal dominance, and edit artifacts. Vendor map-generation dependence remains an admitted rung-2 limit.

14. **Preserved a meaningful negative.** After every prerequisite and validity gate passes, an equivalence-bounded null decisively weakens joint-state use for the tested model. It no longer implies that benchmark models generally side with rCBF or that the physiological state is unimportant. Without a frozen equivalence margin, non-rejection is only sensitivity-limited.

15. **Updated prior-failure analysis.** The card now admits that idea-009/016-style identifiability failure and idea-006-style OOD failure remain live until the gates pass. Annotation provenance is not the primary-readout dependency.

16. **Corrected readiness and compute claims.** The obsolete “cheapest candidate” and fixed 320-pass claims are removed. Public access is verified, but archive retrieval, headers, covariates, exact weights, and input channels remain unverified.

17. **Qualified novelty.** The exact delta from ablations and clinical-variable counterfactuals is stated, but absence of a found duplicate is not called proof of novelty.

18. **Rescored the card.** Identifiability is 3, feasibility is capped at 3, and Mode C mechanism clarity is 4. The Mode C weighted priority is 3.75. Negative-result value remains 4 only because its equivalence-bounded interpretation is explicitly conditional on all gates.

## Claim-identity judgment

This is a narrowed claim, not the same evidentiary promise. It preserves the original model-use object—blood-volume/transit state read against matched flow—but removes the unsupported assertion that the state has been identified as autoregulatory reserve. A future rung-3 reserve claim would require independent physiological validation and a fresh governance decision; it cannot be inferred from same-cohort outcome shape alone.

```json
{"claim_retention": "narrowed"}
```


===== ideas/023/state.json =====
{
  "approval": {
    "contract_blob": "03d4545fe293f0067c69ce9e9e696ec97b894d7b",
    "stale": false
  },
  "charter": "isles24",
  "claim": "The final-infarct model is using the autoregulatory blood-volume reserve -- capillary volume held at or above mirror-normal while flow falls -- as its tissue-salvageability signal, distinguishing the still-compensating penumbra from the collapsed core at matched flow deficit.",
  "contract_blob": "03d4545fe293f0067c69ce9e9e696ec97b894d7b",
  "corrections": null,
  "idea_id": "idea-023",
  "idea_no": "023",
  "kill_code": null,
  "materialization": {
    "event_count": 7,
    "materializer_version": 3,
    "source_fingerprint_sha256": "ce604ebfa577919d8bd45834eccea1d410a9dd6b94edc6264051cda2a3fdd2f6",
    "sources": {
      "approval_sha256": "325703c888df79f90ec21e88c962b7bb5893b21e14c43f92633df27b7e1d9624",
      "contract_blob": "03d4545fe293f0067c69ce9e9e696ec97b894d7b",
      "idea_card_sha256": "f7043f2cfedb68887b2421a0d29070002f39ff951bf4d8338eaf3891885c40dd",
      "ledger_events_sha256": "dcffc97ec0fe8ccafb1cccb696a3f80d535db92345cd38f601b7e877f81b5382",
      "registry_sha256": null
    }
  },
  "pending_decisions": null,
  "registry": null,
  "schema_version": 1,
  "scrutiny": "PROBED",
  "status": "SHORTLISTED",
  "title": "Little's law in the penumbra: the model may be reading the vasodilatory counterattack"
}


===== STAGE TASK =====
<!-- STAGE_SENTINEL: INTERPRET_REVIEW_CHECKER_V1 (machine marker; do not quote in prose) -->
You are the cross-family checker for an interpretation of probe
results. The interpretation is `interpretation.md` in your assigned
folder; the results bundle it interprets is under probes/NNN/ (the
interpretation's citations name the files). Your job is verification,
not co-authorship: you check what is written against what is in the
files and against the contract. You do not add findings of your own.

Checks, each BLOCKING on failure:

1. CITATIONS RESOLVE. Open every file named in a [cite: ...] tag,
   apply the row selector, read the column, and confirm the sentence's
   number matches the cited value (transcription exact to the stated
   precision). Any uncited quantitative claim, unresolvable citation,
   or mis-transcription is blocking. List each one you checked.
2. CLAIM BOUNDS. No threshold/cutoff/margin/pass-fail language about
   tier 2 anywhere (context values may be cited for scale only). No
   aggregation the analysis files do not themselves contain. Vendor
   scope and anchor exclusion stated where counts appear. The
   baseline-not-floor framing respected. The uncertainty constraint in
   the interpret prompt applied correctly for a deterministic probe
   (case-level, not seed-level).
3. COMPLETENESS WITHOUT CHERRY-PICKING. The interpretation may be
   selective, but if the tables contain a material feature that
   contradicts or complicates a stated finding (e.g. a stratum where a
   claimed pattern reverses), omitting it is blocking. Name what you
   checked for.
4. VERDICT SEPARATION. demonstrates / suggests / does not establish
   are used per their definitions; nothing exploratory is stated
   confirmatorily.

Write `interpret_review.md` in the assigned folder: per-check findings
with the citations you resolved, then a fenced json block:

```json
{"verdict": "APPROVE"}
```

or {"verdict": "REVISE", "blocking": ["...", "..."]} with each blocking
finding concrete enough to fix without interpretation. At most one
revision round exists; do not hold approval hostage to preferences.
Modify no file other than interpret_review.md.

5. PLAIN-LANGUAGE FIDELITY. If the interpretation contains a plain
   summary section, verify it claims nothing the cited technical
   findings do not; a plain section that drops a hedge or upgrades a
   "suggests" to a "shows" is BLOCKING.

