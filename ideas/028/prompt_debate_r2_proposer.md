You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/028
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

- **DATA_ACCESS** x2: Required data, checkpoints, or mappings are not obtainable in practice.
- **IDENTIFIABILITY_FAILURE** x1: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.

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
- **idea-028** [SHORTLISTED/CRITIQUED/baseline] -- The blood's grayscale oxygen gauge
- **idea-029** [SHORTLISTED/SCOUTED/baseline] -- The ground truth remembers the algorithm that drafted it
- **idea-030** [SHORTLISTED/SCOUTED/wide] -- The ground truth was drawn on a swollen brain
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


===== ideas/028/README.md =====
# Idea 028: The blood's grayscale oxygen gauge

Selected from scouting cycle isles24-003, candidate 4.


===== ideas/028/critique.md =====
FATAL OBJECTION: The proposed experiment has no identified NCCT-consuming final-infarct checkpoint, and the released winning ISLES'24 pipeline cannot see dural-sinus HU; even a positive response in a newly trained model would identify use of edited sinus intensity, not use of an oxygen-carrying-capacity proxy.
EVIDENCE: Ren et al., arXiv:2505.18424v2, Methods 3.2–3.3 and Table 1; KurtLabUW/ISLES2024 `inference.py` lines 121–124 at commit `bb6c00c8a58cb57a5a33c133c02885776673d230`; Black et al., DOI 10.3174/ajnr.A2504.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial critique

## 1. The target model does not presently exist in the card

The card moves among “an ISLES'24 model,” “the final-infarct model,” and a model that apparently remains to be trained. Those are not interchangeable experimental objects.

The most relevant released high-performing reference is actively incompatible with the proposed intervention. The winning-method paper says that an NCCT-derived SynthStrip mask was applied to the co-registered scans (Methods 3.2), thereby removing the superior sagittal and straight sinuses from the model field. More decisively, Table 1 enumerates the final model inputs as CTA, CBF, CBV, MTT, and Tmax; it does not include NCCT. The released inference program is narrower still: at repository commit `bb6c00c8a58cb57a5a33c133c02885776673d230`, lines 121–124 construct the four inference channels from preprocessed CBF, CBV, MTT, and Tmax. A Google Drive weights link exists in `model weights.txt`, but those weights do not turn this into an NCCT model. These are **verified facts** from the primary method paper and official implementation.

The public PrediCTP implementation (Amador et al., arXiv:2509.24420; official repository `kimberly-amador/ISLES24-PrediCTP`) consumes native 4D CTP rather than NCCT and reports Dice 0.20. It is not an easier target for a sinus-HU intervention. I found no primary source establishing an obtainable, validated ISLES'24 final-infarct checkpoint that ingests unmasked quantitative NCCT. That search result is not proof that none exists, but it invalidates the card's “three to five days after model training” presentation as data/model readiness. Training, selecting, and validating a new NCCT-inclusive model is the main study, not a preliminary chore; selection on the same 149 cases would also threaten an honest held-out intervention test.

The required repair is therefore: first obtain or preregister and train a quantitatively faithful, unmasked-NCCT model; freeze patient-level training/development/test splits before choosing it; demonstrate non-trivial held-out final-infarct performance and incremental NCCT use over otherwise identical CTP/CTA/clinical inputs; and only then test sinus edits on the untouched subset. This repairs feasibility but still does not repair the card's physiological question.

## 2. The intervention cannot identify the claimed meaning

Black et al. measured the torcular HU in 166 unenhanced head CT examinations and found correlation with contemporaneous hematocrit and hemoglobin (AJNR 2011; DOI 10.3174/ajnr.A2504; PMID 21566009). That is good prior legwork for a **measurement association**. It does not establish that a network's response to synthetic sinus intensities means the network represents hematocrit, anemia, arterial oxygen content, or oxygen delivery.

A signed response to editing only the sinus would establish, at best, causal sensitivity to that edited image region under that editor. The same response is compatible with learned site/protocol cues, reconstruction-kernel cues, partial-volume/skull-edge cues, global intensity calibration, or an anatomically remote brightness feature. Within-case editing fixes the case's acquisition but does not remove acquisition information encoded in the edited value. Site stratification and noise normalization test stability, not semantics. Equal-volume skull and extracranial-vein shams do not exhaust these alternatives because neither sham matches the sinus's location, boundary geometry, tissue interfaces, or training correlation structure.

The card itself recognizes this by declaring target rung 1 to be “use of sinus attenuation, not a claim of measured anemia.” But its question asks whether the model uses attenuation “as an image proxy for hematocrit and therefore oxygen-carrying capacity,” and its deliverable sentence asserts exactly that interpretation. This is an internal claim-identity failure. Narrowing the deliverable to “the model is sensitive to dural-sinus intensity” removes the oxygen-gauge question that makes the candidate interesting; under the program's claim-identity rule, that is a successor, not a revision.

Even measured hematocrit in an external cohort would calibrate the image measure, not reveal the ISLES model's interpretation. Physiologically, oxygen delivery depends on flow and arterial oxygen content; arterial oxygen content depends mainly on hemoglobin concentration and oxygen saturation, not hematocrit alone. The card's technical mechanism partially conditions this (“at the same CBF”), but neither the planned experiment nor the ISLES labels isolate that pathway from reperfusion, collateral state, treatment, time, and the many other determinants of final infarct.

## 3. The proposed edit is underspecified and likely out of distribution

“Replace only dural-sinus voxels with intensity-matched surrounding blood values” is not operationally coherent: surrounding the dural sinus is skull, dura, and brain, not a second pool of unenhanced blood. The secondary arterial-HU normalization also risks using small, partially volumed arteries and silently changes the construct from absolute blood attenuation to a venous/arterial ratio.

A constant or rescaled sinus fill changes noise texture, spatial gradients, partial-volume boundaries, and possibly vessel morphology. A three-dose curve can be monotone for an artifact detector. Physiologic-range marginal HU values do not make a conditional edit realistic. A defensible editor would need to preserve the subject's local noise power spectrum, boundary partial volume, and spatial variation, and pass blinded real-versus-edited discrimination or an equivalence gate. Those additions are not excessive compute, but they are essential construct-validity work absent from the card.

The automatic sinus segmentation asset is also merely asserted. Atlas transfer on acute, variably positioned, thick-slice NCCT near skull is not the same as a validated sinus-blood segmentation. The one-voxel erosion ICC measures estimator stability, not anatomical accuracy; two consistently misplaced masks can have ICC 1.0. Manual QC would be new annotation burden unless an independently validated public segmenter is identified. The ≥120/149 threshold, site SMD <0.5, and ICC ≥0.9 have no cited power, error, or biological rationale and could reward a stable but invalid measure.

## 4. Endpoint, leakage, and negative-result problems

“Affected-territory prediction changes” is not defined. The final-infarct ground truth is a post-treatment lesion, while the affected territory must be defined without using that future mask if the readout is meant to represent prospective prediction. Defining it from the label leaks outcome geometry into the endpoint; defining it from baseline perfusion requires a frozen threshold and creates a different selection estimand. The card specifies neither voxelwise statistic nor case aggregation, multiplicity handling across doses/regions, minimum effect, or whether accuracy must remain valid after editing.

A positive output delta need not improve or harm Dice, lesion-wise F1, absolute volume difference, or lesion-count difference—the official ISLES'24 measures in the organizers' repository. Thus the medical consequence is weak: output motion alone can be arbitrary sensitivity. Conversely, a negative remains weak even with theoretical receptive-field coverage. A nominal receptive field is not evidence of effective sensitivity, and failure could reflect model non-use, insufficient natural HU variation, weak NCCT contribution, editor invalidity, or low power. A positive control that merely alters a known salient input verifies the inference pipeline, not sensitivity to subtle remote blood-HU information. The card correctly scores negative-result value only 2, but its prose overstates the value of a gated null.

There is no concept-label circularity in the narrow sense: the follow-up infarct label was not generated from sinus HU. There is, however, semantic circularity in calling the manipulated scalar an “oxygen gauge” because the interpretation comes from the motivating association rather than an independent model-level measurement.

## 5. Prior-work and novelty position

The blood-HU/hematocrit relationship is established prior work, not a new result (Black et al., DOI 10.3174/ajnr.A2504). The official challenge paper and repository establish the dataset and evaluation setup (de la Rosa et al., arXiv:2408.10966; `https://github.com/ezequieldlrosa/isles24`). The winning pipeline and its strong preprocessing dependence are also published (Ren et al., arXiv:2505.18424v2). I did not find a primary paper that performs this exact model-use test in final-infarct prediction, but absence from a bounded search is not novelty evidence. More importantly, the unfilled gap is not yet a sound question because the experiment cannot distinguish proxy semantics from regional intensity use.

## 6. Plain-pitch fidelity

**Named defect: the pitch preserves the anemia disclaimer but drops two load-bearing qualifications.** “Their concentration affects how much oxygen reaches threatened brain tissue” omits the technical card's same-CBF condition and oxygen-saturation dependence. “A true result” then describes a graded lesion-prediction response as evidence for the “oxygen gauge,” although the rung statement concedes that such a response establishes only use of sinus attenuation. The pitch is therefore more physiological and more certain than the proposed evidence permits. A faithful version would say that red-cell concentration is associated with unenhanced blood HU and contributes to oxygen content, while a model response would show only sensitivity to edited sinus intensity unless independently validated.

## 7. Low-hanging fruit

There is no low-hanging-fruit formulation that preserves the original medical claim. Existing ingredients are individually ready—the 149 public training cases, official evaluation code, winner preprocessing/inference code, linked winner weights, and the published torcular-HU formula—but the available winner removes or never consumes the signal of interest. Measuring the ISLES sinus-HU distribution is a cheap dataset-quality audit, yet without laboratory hematocrit it cannot answer whether HU ranks the biological variable in this cohort, and by itself it is not a high-value medical-imaging-AI study.

The technically easiest model experiment would compare a frozen NCCT-inclusive model's outputs before and after texture-preserving sinus edits. No such validated frozen model was verified, and the result would only be a shortcut/sensitivity audit. The card explicitly says that version becomes uninteresting if the hematology link is dropped; I agree. It should not be kept alive merely because it is computable.

## Constructive alternative

The scientifically meaningful nearby study requires a different cohort: test whether measured admission hemoglobin (plus oxygen saturation) adds held-out predictive information for final infarct conditional on perfusion, treatment/reperfusion, and time, then test whether NCCT sinus HU mediates or substitutes for that laboratory signal. This directly evaluates the oxygen-delivery hypothesis and gives a negative result interpretable meaning. It needs patient-level labs and adequate multivariable support that have not been verified in ISLES'24, so ISLES'24 would no longer be load-bearing; it must be a separate candidate only after a suitable cohort is identified. That is harder, but it is worth doing in a sufficiently powered treatment-characterized cohort because it separates physiology from image shortcut.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: In a treatment-characterized acute-stroke cohort with admission hemoglobin, oxygen saturation, baseline perfusion, and final infarct, does measured oxygen-carrying capacity add held-out predictive information, and can quantitative NCCT sinus HU substitute for it without loss of calibration?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—if a sufficiently powered cohort with temporally aligned laboratory and reperfusion data is obtainable, because it directly tests the physiology that makes the image feature medically interesting rather than merely demonstrating sensitivity to a bright remote structure.


===== ideas/028/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The experiment cannot answer the original oxygen-carrying-capacity question; its strongest identifiable result is only sensitivity to edited dural-sinus intensity, which is a different claim and therefore a separate candidate.

**Argument:** Black et al. (DOI 10.3174/ajnr.A2504; PMID 21566009) support an association between unenhanced venous-sinus HU and contemporaneous hematocrit/hemoglobin, but that population-level measurement association does not identify what a final-infarct model means by sinus HU. A monotone output response to texture-preserving sinus edits would still be compatible with use of scanner calibration, reconstruction or site signatures, skull-adjacent boundary structure, or a remote brightness shortcut; within-case edits and anatomical shams can narrow these alternatives but cannot turn the response into evidence that the model uses HU *as a proxy for oxygen-carrying capacity*. The card exposes the contradiction itself: its rung-1 limit says “use of sinus attenuation, not a claim of measured anemia,” while its question and deliverable sentence assert proxy semantics and oxygen carrying capacity. Amending the deliverable to regional-intensity sensitivity would cross the repository's claim-identity boundary. Moreover, the released winning system cannot rescue the interpretation: Ren et al. (arXiv:2505.18424v2, Table 1 and Methods 3.2–3.3) excludes NCCT from the final input set, and the official implementation at commit `bb6c00c8a58cb57a5a33c133c02885776673d230` constructs inference inputs from CBF, CBV, MTT, and Tmax. Training a new NCCT-inclusive model may make an intensity-sensitivity study executable, but it does not repair this semantic non-identifiability.

**What would change my mind:** Show, in a frozen NCCT-inclusive final-infarct model evaluated on an untouched treatment-characterized cohort, that measured admission hemoglobin and oxygen saturation predict the model's sinus-HU response conditional on acquisition/site, perfusion, reperfusion, and time, and that replacing sinus HU with the subject's laboratory-implied value mediates the model response while matched nonhematologic intensity edits do not; also show that this cohort is concretely linked to ISLES'24 so the dataset remains load-bearing. Without that evidence, the oxygen-proxy claim must be rejected and any sinus-intensity-use audit registered separately.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The strongest result this design can produce — a monotone, sham-surviving output response to within-case sinus-intensity edits — identifies only sensitivity to the edited region, never that the model treats sinus HU *as a proxy for oxygen-carrying capacity*. The deliverable sentence asserts the proxy semantics anyway; narrowing it to intensity sensitivity would change the claim's identity; and the released winning pipeline cannot even see the sinus (NCCT excluded from its inputs, SynthStrip-masked away), so no existing checkpoint carries the question.

**Response:** CONCEDE

**Argument:** The objection is correct, and it is correct in a way the card itself pre-registered. Three points, none of which I can answer with new evidence:

1. **The semantic gap is intrinsic to the design, not a repairable gate.** Every arm of the proposed intervention — dose response, skull and extracranial-vein shams, site stratification, noise normalization — discriminates *where* and *how strongly* the model responds, never *what the scalar means to it*. The card's own rung ladder admits this: rung 1 is "use of sinus attenuation, not a claim of measured anemia," and rung 2 requires measured hematocrit in an external cohort. The keystone screen (2026-08-18) confirmed the release documents no hematocrit or hemoglobin field, so rung 2 is unreachable inside ISLES'24 by construction; and once an external laboratory cohort becomes the evidential engine, ISLES'24 is no longer load-bearing, which fails the charter's second criterion for the very claim that makes the candidate interesting. The question cannot be answered with the dataset, and the question that can be answered with the dataset is not this question.

2. **The card contains its own kill condition, and the critic has triggered it.** Under `cross_domain.what_changes_if_dropped` the card states: "Without the hematology link, the experiment becomes an uninteresting remote-intensity shortcut audit and should be killed." Round 1 establishes that the hematology link cannot be carried by any evidence obtainable within this design. The identity check on AMEND forbids the only available dodge: rewriting the deliverable sentence from "image proxy for oxygen-carrying capacity" to "sensitive to dural-sinus intensity" is a change of claim identity under the 2026-08-10 rule (idea-015 precedent), so it must be a successor registration, not an amendment. I decline to submit that amendment and concede instead.

3. **The model-asset facts are verified and undisputed.** Ren et al. (arXiv:2505.18424v2, Table 1) list CTA, CBF, CBV, MTT, and Tmax as the final inputs — no NCCT — and the official `inference.py` (commit `bb6c00c8a58cb57a5a33c133c02885776673d230`, lines 121–124) builds four inference channels from perfusion maps only; Methods 3.2 applies SynthStrip brain masking that removes the dural sinuses from the field entirely. Mode C tolerates the resulting feasibility cost (training a new NCCT-inclusive model), but feasibility was never the fatal axis; even a purpose-trained model inherits point 1 unchanged.

**Spin-off (for separate registration, not defended here):** The critique's constructive alternative is the honest version of the motivating physiology and should enter as a new candidate with `parent_ids: ["isles24-scout-003-c04"]`: in a treatment-characterized acute-stroke cohort with admission hemoglobin and oxygen saturation, test whether measured oxygen-carrying capacity adds held-out predictive information for final infarct conditional on perfusion, reperfusion, and time, and whether quantitative NCCT sinus HU can substitute for the laboratory value without loss of calibration. This requires identifying such a cohort first; ISLES'24 is not it, so the successor either waits on cohort identification or registers outside this charter. I deliberately do **not** register the bare sinus-intensity-sensitivity audit as a spin-off: the card's own kill clause says that study is not worth running without the hematology link, and I agree.

**Fact of record worth preserving:** the keystone screen's verified finding — raw, defaced-only, non-skull-stripped NCCT with intact sinus-region HU for all 149 cases — remains true and reusable by any future NCCT-quantitative candidate under this charter. The concession is about claim identifiability, not data availability.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** I concede the debate because the proposer accepts that ISLES'24 cannot identify the original oxygen-carrying-capacity proxy claim and that narrowing the study to sinus-intensity sensitivity would change the claim's identity.

**Argument:** The proposer answered the decisive objection with an argument rather than insistence: the available intervention arms can identify where and how strongly a model responds, but none can establish what sinus HU means to the model; the release provides no verified hematocrit or hemoglobin measurement with which to bridge that semantic gap; and the obtainable winning system excludes NCCT from its final inputs and brain-masks the sinus region (Ren et al., arXiv:2505.18424v2; official implementation commit `bb6c00c8a58cb57a5a33c133c02885776673d230`). The card's own rung limit and kill condition therefore control. The identity check is also resolved: changing the deliverable from use of venous attenuation *as an oxygen-carrying-capacity proxy* to sensitivity to edited dural-sinus intensity changes the scientific claim, so it cannot repair idea 028 under the 2026-08-10 rule. The proposed laboratory-data study may preserve the medical motivation, but because its evidential engine is a different treatment-characterized cohort rather than ISLES'24, it is a separate candidate and does not rescue this charter-scoped idea.

**What would change my mind:** The evidence specified in round 1: an obtainable frozen NCCT-inclusive final-infarct model and an untouched cohort concretely linked to ISLES'24 containing temporally aligned hemoglobin, oxygen saturation, acquisition/site, perfusion, reperfusion, and time variables, together with a preregistered mediation/substitution experiment showing that laboratory-implied sinus HU explains the model response while matched nonhematologic edits do not.

**Status:** CONCEDED


===== ideas/028/idea_card.json =====
{
  "id": "isles24-scout-003-c04",
  "parent_ids": [],
  "search_mode": "C",
  "entry_point": 2,
  "title": "The blood's grayscale oxygen gauge",
  "question": "Is an ISLES'24 model using dural-sinus blood attenuation on noncontrast CT as an image proxy for hematocrit and therefore oxygen-carrying capacity?",
  "rung": "Mode C target rung 1: use of sinus attenuation, not a claim of measured anemia; rung 2 requires measured hematocrit in an external cohort.",
  "deliverable_sentence": "The final-infarct model is using noncontrast-CT attenuation of venous blood as an image proxy for oxygen-carrying capacity.",
  "X_measurement": "Automatically segment the superior sagittal/straight sinuses on NCCT and take median HU after erosion, normalized to scanner noise and, secondarily, arterial blood HU. In 166 NCCTs, sinus attenuation correlated with hematocrit and hemoglobin (PMID 21566009). Compute-today test: YES with an automatic atlas/segmentation and HU measurement; no annotator, though quantitative-HU integrity is unverified.",
  "suspected_signal": "Red-cell concentration raises unenhanced blood attenuation and determines arterial oxygen content; at the same CBF, lower hematocrit delivers less oxygen, potentially accelerating tissue death before reperfusion.",
  "use_vs_association": "Remote regional removal/substitution: replace only dural-sinus voxels with intensity-matched surrounding blood values across a physiologic HU dose range while leaving brain, arteries, CTA, CTP, and clinical inputs unchanged; require affected-territory prediction changes, a signed dose response, and null responses to equal-volume skull and extracranial-vein shams.",
  "keystone_prerequisite": "Released NCCT retains quantitative intravascular HU and contains enough artifact-free dural-sinus voxels for sinus attenuation to rank hematocrit rather than reconstruction/site.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_residual_assumption": "The primary hematocrit paper proves the relationship in clinical NCCT, not in resampled ISLES derivatives. No ISLES laboratory hematocrit field has been verified, so the card cannot claim physiological validation within this dataset.",
  "rung_reached": "0; rung 1 after remote dose-response and site robustness; rung 2 only with external measured-hematocrit validation.",
  "dies_like_prior": "Resembles idea-010 (CIRCULARITY) least and idea-016 (IDENTIFIABILITY_FAILURE) most: blood HU can be a scanner/protocol effect. Within-scan substitution, local noise normalization, site stratification, and remote shams address protocol; external hematocrit is explicitly required before naming anemia rather than image-proxy use.",
  "closest_prior_work": "Black et al. established the sinus-HU/hematocrit relation (PMID 21566009). Stroke physiology links oxygen delivery to CBF times arterial oxygen content, but no primary model-use paper was found that tests whether final-infarct networks read blood HU. This is speculative and not a novelty claim.",
  "existing_assets": "NCCT, multimodal final-infarct target, deterministic sinus HU formula, atlas/segmentation methods, two-site structure.",
  "smallest_decisive_experiment": "Stage 0 on all 149 NCCTs: require >=120 measurable sinuses, between-site standardized-mean difference <0.5 after noise normalization, and test-retest ICC >=0.9 across one-voxel erosions. Then run three-dose substitutions on 40 held-out cases. Three to five days after model training; under 10 GPU-hours.",
  "standing_confounds_addressed": "Within-case edits fix anatomy, scanner, vendor, protocol, site, habitus, prevalence, referral, and labels; site/noise gates test quantitative portability. They do not establish that HU equals hematocrit in ISLES, exclude unrecorded contrast contamination, or distinguish hematocrit from other blood-composition effects.",
  "alternative_explanations": [
    "The model reacts to any remote bright structure; skull and extracranial-vein shams test this.",
    "Sinus HU is reconstruction/site, not blood composition; within-case dose response can establish use but not physiology, hence the rung-1 wording.",
    "The local network has no receptive field from sinus to lesion; receptive-field inspection is an early feasibility gate, and a null is uninterpretable if coverage fails."
  ],
  "anticipated_negative": "Sensitivity-limited unless receptive-field and positive-control gates pass; with them, a null is useful evidence that the model does not exploit this globally available physiologic proxy.",
  "cross_domain": {
    "borrowed_construct": "Oxygen-delivery accounting from hematology: delivery is blood flow multiplied by arterial oxygen content.",
    "measurement_it_implies": "Unenhanced venous-blood HU as an image proxy for red-cell concentration.",
    "what_changes_if_dropped": "Without the hematology link, the experiment becomes an uninteresting remote-intensity shortcut audit and should be killed."
  },
  "remaining_legwork": "2 days HU/site census, 1 day receptive-field check, 2 days interventions: under one week after model availability.",
  "design_template": "regional-removal",
  "entry_point_2_requirements": "Measurement: median eroded dural-sinus HU. Confused artifact: reconstruction/site and partial-volume skull; local noise normalization, erosion, and site gates are mandatory.",
  "scores": {
    "mechanism_clarity": {
      "value": 5,
      "why": "Named physical chain: red-cell concentration to HU and oxygen content, with an exact measurement."
    },
    "identifiability": {
      "value": 3,
      "why": "Use of HU can be identified, but physiological hematocrit attribution cannot within ISLES alone."
    },
    "interest": {
      "value": 5,
      "why": "A routine grayscale value functioning as an oxygen gauge is surprising and falsifiable."
    },
    "medical_relevance": {
      "value": 3,
      "why": "Oxygen delivery matters biologically, but clinical consequence is indirect without laboratory validation."
    },
    "clarity": {
      "value": 5,
      "why": "One remote region, one scalar, one signed dose response."
    },
    "prior_legwork": {
      "value": 3,
      "why": "The HU relationship is established; ISLES validation and model assets remain."
    },
    "feasibility": {
      "value": 3,
      "why": "Reported outside Mode C score and capped by quantitative-HU uncertainty."
    },
    "data_readiness": {
      "value": 3,
      "why": "NCCT is public; lab hematocrit and HU fidelity are not verified."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "Paired response is ready; proxy-validity gates are custom."
    },
    "negative_result_value": {
      "value": 2,
      "why": "A null remains sensitivity-limited if the model architecture lacks global receptive coverage."
    },
    "novelty_confidence": {
      "value": 2,
      "why": "Only targeted searching was performed."
    },
    "regret": {
      "value": 3,
      "why": "Very cheap and memorable, but the physiology may not survive dataset preprocessing."
    }
  },
  "mode_c_priority_score": 4.15,
  "unverified_claims": [
    "quantitative sinus HU fidelity",
    "absence of contrast contamination",
    "receptive-field coverage",
    "sinus HU ranks hematocrit in this cohort",
    "novelty"
  ],
  "plain_pitch": "Red blood cells make blood look denser on an unenhanced CT scan, and their concentration affects how much oxygen reaches threatened brain tissue. This speculative test asks whether the model reads the large venous sinuses as a crude oxygen gauge. A true result would be a graded change in lesion predictions when only sinus density is altered, but it would not by itself prove that the model has measured anemia.",
  "track": "baseline",
  "charter": "isles24"
}


===== ideas/028/keystone_screen.md =====
# Keystone screen — idea 028 (isles24-scout-003-c04, "The blood's grayscale oxygen gauge")

Screen date: 2026-08-18. Stage: keystone (pre-critique gate).

## Keystone as stated on the card

> "Released NCCT retains quantitative intravascular HU and contains enough
> artifact-free dural-sinus voxels for sinus attenuation to rank hematocrit
> rather than reconstruction/site."

Decomposed, this is three claims of different kinds:

- **K-a (document-checkable):** the ISLES'24 release contains NCCT volumes in
  which dural-sinus voxels physically survive with their acquired HU values —
  i.e., the released NCCT is not skull-stripped, brain-masked, intensity-
  windowed, or otherwise processed in a way that destroys intravascular HU.
- **K-b (document-checkable in part):** nothing in the documented pipeline
  (registration, resampling, defacing) is declared to alter NCCT intensities.
- **K-c (empirical, not document-checkable):** the surviving sinus voxels are
  numerous and artifact-free enough that sinus attenuation ranks hematocrit
  rather than reconstruction/site. This is exactly what the card's own Stage 0
  gates (≥120 measurable sinuses, between-site SMD < 0.5, erosion ICC ≥ 0.9)
  are prespecified to measure. No document can settle it.

## What I inspected

**1. The official Zenodo data release (the actual hosting page).**
Zenodo record 17652035, "ISLES'24 - A Real-World Longitudinal Multimodal
Stroke Dataset", open access, CC BY-NC-SA 4.0, single file `train.7z`
(99,022,114,670 bytes, MD5 `4959a5dd2438d53e3c86d6858484e781`), 149 training
cases. The description states, verbatim (confirmed via two independent
fetches of https://zenodo.org/records/17652035 and the API endpoint
https://zenodo.org/api/records/17652035):

> "'Raw_data' refers to the 'raw' acquired scans, which are released in their
> original space, just defaced."

and

> "'Derivatives' include all modalities linearly co-registered to the NCCT
> space."

Raw NCCT is released in original acquisition space with defacing as the only
stated modification. The derivatives are registered **to** NCCT space, i.e.,
the NCCT itself is the fixed reference and is not resampled in the
derivatives either.

**2. The official challenge repository (cloned and read).**
https://github.com/ezequieldlrosa/isles24, `README.md` lines 12–22: the
documented BIDS tree places the NCCT under the raw branch:

```
+-- rawdata
|   +-- sub-strokecase0001
|       +-- ses-0001
|           ...
|           +-- sub-strokecase0001_ses-0001_ncct.nii.gz
```

The repo's bundled sample data contains only perfusion maps and lesion masks
("Given data size constrains, only a few images for the sample case are
uploaded", README.md line 55), so no NCCT voxels could be inspected directly
without the 99 GB download.

**3. The challenge organizers' paper (arXiv 2408.10966, Methods/Dataset).**

> "The dataset is released in raw and preprocessed formats, thus allowing
> participants to devise algorithms with diverse degrees of freedom."

> "all scans are defaced based on brain and face masks obtained with
> TotalSegmentator"

No intensity windowing, clipping, or normalization of NCCT is documented
anywhere in the release description or the paper.

**4. Independent confirmation that released scans retain the skull (and
therefore the peri-cranial anatomy where the sinuses sit).**
The ISLES'24 winning team's paper (arXiv 2505.18424, Methods 3.2) describes
the released data they received:

> "The scans in the ISLES'24 brain imaging dataset contain non-brain
> structures such as the skull and background artifacts, which can hinder
> model training"

and they had to apply their own brain extraction:

> "We applied SynthStrip on the non-contrast CT (NCCT) scans to obtain a
> brain masks."

This is third-party, hands-on-the-data confirmation that the released NCCT is
**not** skull-stripped — the failure mode that would have deleted the
superior sagittal sinus (which lies against the inner table) and killed the
idea at this screen.

## Mandatory follow-up: what is the card still assuming?

"If this card only verified the nearest checkable thing, what is it still
assuming?" The nearest checkable thing was data availability; the residuals:

1. **Defacing does not clip the sinus region.** Defacing is face removal;
   the superior sagittal/straight sinuses are parieto-occipital and remote
   from any face mask. This is a source-supported inference from the stated
   method ("brain and face masks obtained with TotalSegmentator"), not a
   voxel-level verification. First contact with the actual volumes in Stage 0
   must confirm the vertex and torcular are intact.
2. **DICOM→NIfTI conversion preserved calibrated HU.** Standard and stated
   nowhere to be violated ("original space, just defaced"), but numeric
   fidelity per scanner is unverified until inspected. The card already
   lists "quantitative sinus HU fidelity" as unverified.
3. **K-c (sinus HU ranks hematocrit here, not reconstruction/site).**
   Untestable from documents by construction; the card's Stage 0 gates are
   the prespecified test and must remain mandatory.
4. **No hematocrit/hemoglobin field is documented in the released clinical
   tables** (documented variables: "demographics, patient history, admission
   NIHSS, 3-month functional outcome (mRS), etc."; laboratory variables carry
   ±5% de-identification noise per arXiv 2408.10966). The card is already
   consistent with this — it claims rung 1 (use of sinus HU) and defers
   hematocrit attribution to an external cohort — so this is a confirmation
   of the card's stated limits, not a new gap. If a hematocrit column does
   turn up in the phenotype CSVs, note the ±5% noise before any use.

The stated keystone and the load-bearing assumption coincide here: the study
is impossible only if sinus voxels or their HU values are absent from the
release. That is the fact verified above. No wrong-keystone substitution
found.

## Verdict

The document-checkable core (K-a, K-b) is verified with verbatim primary-
source evidence; the empirical tail (K-c) is precisely what the card's own
Stage 0 is designed to answer and cannot be decided at screen prices.
Nothing inspected falsifies the keystone.

```json
{"verdict": "PASS", "evidence": "'Raw_data' refers to the 'raw' acquired scans, which are released in their original space, just defaced.", "source": "https://zenodo.org/records/17652035 (ISLES'24 training-set release, description field; corroborated by github.com/ezequieldlrosa/isles24 README.md lines 12-22 rawdata/*_ncct.nii.gz and arXiv 2505.18424 Methods 3.2 'contain non-brain structures such as the skull')", "note": "Raw, defaced-only, non-skull-stripped NCCT for 149 cases is publicly released; sinus-voxel survival of defacing and HU fidelity remain Stage 0 first checks, and the rank-hematocrit clause is empirical by construction (card's Stage 0 gates are the test)."}
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
You are claude. Your interlocutor is codex.
This is round 2. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The experiment cannot answer the original oxygen-carrying-capacity question; its strongest identifiable result is only sensitivity to edited dural-sinus intensity, which is a different claim and therefore a separate candidate.

**Argument:** Black et al. (DOI 10.3174/ajnr.A2504; PMID 21566009) support an association between unenhanced venous-sinus HU and contemporaneous hematocrit/hemoglobin, but that population-level measurement association does not identify what a final-infarct model means by sinus HU. A monotone output response to texture-preserving sinus edits would still be compatible with use of scanner calibration, reconstruction or site signatures, skull-adjacent boundary structure, or a remote brightness shortcut; within-case edits and anatomical shams can narrow these alternatives but cannot turn the response into evidence that the model uses HU *as a proxy for oxygen-carrying capacity*. The card exposes the contradiction itself: its rung-1 limit says “use of sinus attenuation, not a claim of measured anemia,” while its question and deliverable sentence assert proxy semantics and oxygen carrying capacity. Amending the deliverable to regional-intensity sensitivity would cross the repository's claim-identity boundary. Moreover, the released winning system cannot rescue the interpretation: Ren et al. (arXiv:2505.18424v2, Table 1 and Methods 3.2–3.3) excludes NCCT from the final input set, and the official implementation at commit `bb6c00c8a58cb57a5a33c133c02885776673d230` constructs inference inputs from CBF, CBV, MTT, and Tmax. Training a new NCCT-inclusive model may make an intensity-sensitivity study executable, but it does not repair this semantic non-identifiability.

**What would change my mind:** Show, in a frozen NCCT-inclusive final-infarct model evaluated on an untouched treatment-characterized cohort, that measured admission hemoglobin and oxygen saturation predict the model's sinus-HU response conditional on acquisition/site, perfusion, reperfusion, and time, and that replacing sinus HU with the subject's laboratory-implied value mediates the model response while matched nonhematologic intensity edits do not; also show that this cohort is concretely linked to ISLES'24 so the dataset remains load-bearing. Without that evidence, the oxygen-proxy claim must be rejected and any sinus-intensity-use audit registered separately.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The strongest result this design can produce — a monotone, sham-surviving output response to within-case sinus-intensity edits — identifies only sensitivity to the edited region, never that the model treats sinus HU *as a proxy for oxygen-carrying capacity*. The deliverable sentence asserts the proxy semantics anyway; narrowing it to intensity sensitivity would change the claim's identity; and the released winning pipeline cannot even see the sinus (NCCT excluded from its inputs, SynthStrip-masked away), so no existing checkpoint carries the question.

**Response:** CONCEDE

**Argument:** The objection is correct, and it is correct in a way the card itself pre-registered. Three points, none of which I can answer with new evidence:

1. **The semantic gap is intrinsic to the design, not a repairable gate.** Every arm of the proposed intervention — dose response, skull and extracranial-vein shams, site stratification, noise normalization — discriminates *where* and *how strongly* the model responds, never *what the scalar means to it*. The card's own rung ladder admits this: rung 1 is "use of sinus attenuation, not a claim of measured anemia," and rung 2 requires measured hematocrit in an external cohort. The keystone screen (2026-08-18) confirmed the release documents no hematocrit or hemoglobin field, so rung 2 is unreachable inside ISLES'24 by construction; and once an external laboratory cohort becomes the evidential engine, ISLES'24 is no longer load-bearing, which fails the charter's second criterion for the very claim that makes the candidate interesting. The question cannot be answered with the dataset, and the question that can be answered with the dataset is not this question.

2. **The card contains its own kill condition, and the critic has triggered it.** Under `cross_domain.what_changes_if_dropped` the card states: "Without the hematology link, the experiment becomes an uninteresting remote-intensity shortcut audit and should be killed." Round 1 establishes that the hematology link cannot be carried by any evidence obtainable within this design. The identity check on AMEND forbids the only available dodge: rewriting the deliverable sentence from "image proxy for oxygen-carrying capacity" to "sensitive to dural-sinus intensity" is a change of claim identity under the 2026-08-10 rule (idea-015 precedent), so it must be a successor registration, not an amendment. I decline to submit that amendment and concede instead.

3. **The model-asset facts are verified and undisputed.** Ren et al. (arXiv:2505.18424v2, Table 1) list CTA, CBF, CBV, MTT, and Tmax as the final inputs — no NCCT — and the official `inference.py` (commit `bb6c00c8a58cb57a5a33c133c02885776673d230`, lines 121–124) builds four inference channels from perfusion maps only; Methods 3.2 applies SynthStrip brain masking that removes the dural sinuses from the field entirely. Mode C tolerates the resulting feasibility cost (training a new NCCT-inclusive model), but feasibility was never the fatal axis; even a purpose-trained model inherits point 1 unchanged.

**Spin-off (for separate registration, not defended here):** The critique's constructive alternative is the honest version of the motivating physiology and should enter as a new candidate with `parent_ids: ["isles24-scout-003-c04"]`: in a treatment-characterized acute-stroke cohort with admission hemoglobin and oxygen saturation, test whether measured oxygen-carrying capacity adds held-out predictive information for final infarct conditional on perfusion, reperfusion, and time, and whether quantitative NCCT sinus HU can substitute for the laboratory value without loss of calibration. This requires identifying such a cohort first; ISLES'24 is not it, so the successor either waits on cohort identification or registers outside this charter. I deliberately do **not** register the bare sinus-intensity-sensitivity audit as a spin-off: the card's own kill clause says that study is not worth running without the hematology link, and I agree.

**Fact of record worth preserving:** the keystone screen's verified finding — raw, defaced-only, non-skull-stripped NCCT with intact sinus-region HU for all 149 cases — remains true and reusable by any future NCCT-quantitative candidate under this charter. The concession is about claim identifiability, not data availability.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** I concede the debate because the proposer accepts that ISLES'24 cannot identify the original oxygen-carrying-capacity proxy claim and that narrowing the study to sinus-intensity sensitivity would change the claim's identity.

**Argument:** The proposer answered the decisive objection with an argument rather than insistence: the available intervention arms can identify where and how strongly a model responds, but none can establish what sinus HU means to the model; the release provides no verified hematocrit or hemoglobin measurement with which to bridge that semantic gap; and the obtainable winning system excludes NCCT from its final inputs and brain-masks the sinus region (Ren et al., arXiv:2505.18424v2; official implementation commit `bb6c00c8a58cb57a5a33c133c02885776673d230`). The card's own rung limit and kill condition therefore control. The identity check is also resolved: changing the deliverable from use of venous attenuation *as an oxygen-carrying-capacity proxy* to sensitivity to edited dural-sinus intensity changes the scientific claim, so it cannot repair idea 028 under the 2026-08-10 rule. The proposed laboratory-data study may preserve the medical motivation, but because its evidential engine is a different treatment-characterized cohort rather than ISLES'24, it is a separate candidate and does not rescue this charter-scoped idea.

**What would change my mind:** The evidence specified in round 1: an obtainable frozen NCCT-inclusive final-infarct model and an untouched cohort concretely linked to ISLES'24 containing temporally aligned hemoglobin, oxygen saturation, acquisition/site, perfusion, reperfusion, and time variables, together with a preregistered mediation/substitution experiment showing that laboratory-implied sinus HU explains the model response while matched nonhematologic edits do not.

**Status:** CONCEDED

