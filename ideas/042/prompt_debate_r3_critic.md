You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/042
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
- **idea-039** [SHORTLISTED/DEBATED/wide] -- Does the model trust tissue that obeys the flow equation?
- **idea-040** [PAUSED/DEBATED/baseline] -- The pressure history written in a winding artery
- **idea-041** [SHORTLISTED/DEBATED/wide] -- The roughness of a heartbeat through starved tissue
- **idea-042** [SHORTLISTED/CRITIQUED/wide] -- Delay is not dispersion
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
- [isles24] **idea-040** [PAUSED] -- The pressure history written in a winding artery
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


===== ideas/042/README.md =====
# Idea 042: Delay is not dispersion

Selected from scouting cycle isles24-005, candidate 8.


===== ideas/042/critique.md =====
# Critique — Idea 042: Delay is not dispersion

```
FATAL OBJECTION: NONE
EVIDENCE: The dispersion-edit constraint set (contract width while preserving
  area AND peak height) contradicts the card's own realism gate; the closest
  prior work (Amador et al., ISBI 2024, attention analysis of a raw-4D-CTP
  outcome model) is absent from the card despite being flagged in this
  program's own cycle-003 novelty audit; both are repairable.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

## 1. What survives attack

The core question is genuine and well-posed. Delay and dispersion are
physically distinct transport properties (verified fact: Calamante et al.,
DOI 10.1002/mrm.20873, separates them explicitly and shows delay does not
determine dispersion), classical tissue predictors are sensitive to both
(Willats et al. 2012, DOI 10.1161/STROKEAHA.111.635888, found by the
cycle-005 audit as a closer neighbor than the card's own citations), and
raw-time networks exist that could in principle exploit post-alignment curve
shape (Winder et al., Front Neurosci 2022, DOI 10.3389/fnins.2022.1009654 —
full text confirmed by the cycle-005 audit to contain no perturbation or
curve-manipulation experiments). The novelty delta as stated — no located
work causally probes a trained raw-CTP model with transport-cost-matched,
factorized dispersion-only versus delay-only edits — survived my re-check
(see §3). The within-case paired design genuinely neutralizes the standing
IDENTIFIABILITY_FAILURE killers (center, scanner, injection, cardiac output
as *between-case* confounds), and the card's rung-1 cap with collateral
wording demoted to interpretation is the right instinct, though not carried
through to the deliverable sentence (§4).

The keystone screen's UNVERIFIABLE verdict is honest and correctly priced:
raw 4D CTP existence and 1 frame/sec cadence are verified; per-case
baseline/peak/washout coverage and within-delay dispersion variation are
not, and the card's Stage 0 gates (5 pre-arrival frames, peak ≥5 frames
before end, washout to ≤30% of peak, ICC ≥0.85, 90% of 20 cases) are
concrete and killable. Hard caps respected: feasibility 3 and
novelty_confidence 3 under NOT_INSPECTED.

## 2. Objections, in decreasing order of severity

### 2.1 The dispersion edit is over-constrained and collides with its own realism gate

`X_measurement`/`use_vs_association` specify a dispersion-only edit that
"contracts the aligned curve toward the arterial width while preserving
arrival time, area, peak height, and baseline noise power." This constraint
set is mathematically satisfiable only by driving the curve toward
flat-topped (boxcar-like) shapes: at fixed area and fixed peak height, the
minimum-variance curve is a boxcar, and if the arterial width lies below
that boxcar limit the edit is infeasible outright (inference from elementary
moment bounds; no source needed). Physically, a genuinely less-dispersed
bolus at the same delivered contrast (area ≈ CBV·k) has a **taller,
narrower** peak — the tissue curve is AIF ⊛ residue, a smooth gamma-like
family in which width and peak height are anticorrelated at fixed area.
The card's own realism gate is "interpolation between observed same-case
curves" plus nearest-neighbor feature distance — and observed same-case
curves live in exactly that physiological family. So the confirmatory arm
as specified either fails the realism gate (flat-topped curves have no
same-case neighbors) or the gate must be loosened until it stops binding.
The card contradicts itself.

The escape — let the peak rise as physics dictates — creates the confound
the constraint was built to avoid: the dispersion arm then differs from the
delay arm in peak height, a trivial intensity cue (peak concentration is
CBF-coupled), and "responds more to the dispersion edit" no longer isolates
width/skew use from peak-height use. The honest statement is that delay,
peak, and width cannot all be factorized within physiological realism,
because area conservation couples the latter two. The card must choose its
two-way contrast and say so.

**Repair options (any one suffices; the question is unchanged):**
(a) run both dispersion arms — area-preserving/peak-rising (physical) and
peak-preserving (shape-strained) — and require concordant dose-ordered
response, interpreting only the intersection; (b) add a peak-only control
arm (amplitude scaling at fixed width) so peak-height use is measured
rather than assumed away; (c) restate the estimand as "delay-independent
curve shape (width–peak bundle)" and drop the claim to have isolated width
specifically. Option (a)+(b) is strongest; option (c) is the honest floor.

### 2.2 The closest prior work is missing from the card — and this program already knew about it

This is a process failure with a substantive consequence. Scout cycle 003
produced candidate isles24-scout-003-c06, "The bolus spreads like dye in a
river" — the same core intervention (delay- and area-preserving curve
narrowing/broadening applied to a raw-CTP final-infarct model). Its novelty
audit (`ideas/scout-isles24-003/novelty_audit.md`, C6) identified
**Amador et al., ISBI 2024, "Unveiling the Temporal Patterns of a 4D CTP
Stroke Lesion Outcome Prediction Model Through Attention Analysis"
(DOI 10.1109/ISBI56570.2024.10635756)** as "the closest prior work, and
closer than anything cited on the card," downgraded C6 to LIMITED_SEARCH
solely because the paper could only be read at abstract level, and made a
full read a condition of advancement: a curve-shape perturbation in that
paper would make the candidate INCREMENTAL. Idea 042's card cites Amador
ISBI 2024 nowhere, its `dies_like_prior` field does not mention c06, and
the cycle-005 audit granted c08 HIGH_CONFIDENCE without surfacing either.

I re-checked what is publicly accessible (2026-08-19): the
[IEEE Xplore record](https://ieeexplore.ieee.org/document/10635756/) and
[abstract metadata](https://colab.ws/articles/10.1109/isbi56570.2024.10635756)
describe attention-weight analysis only — no perturbation, occlusion, or
curve manipulation — and report that the model "focuses on two specific
temporal patterns associated with observed variations in contrast
concentration dynamics," unnamed at abstract level. Source-supported
interpretation: the delta (causal, cost-matched perturbation versus
correlational attention) survives. But the delta must be *stated against
this paper*, the paper must be read in full before debate (the inherited
c06 condition — if one of the two attended "temporal patterns" is bolus
width, both motivation and priority change), and the card must acknowledge
c06 as a within-portfolio predecessor it supersedes. The same group
(Amador, Winder, Forkert) owns both the model class and the
interpretability question; they are one methods section away from this
experiment, which raises urgency and lowers novelty margin simultaneously.

### 2.3 The model to be interrogated does not exist, and the card's envelope hides that

The smallest decisive experiment reuses "the same frozen shallow raw-time
model and split discipline as c07" — that is idea 041, whose post-debate
revision (`ideas/041/revision.md`, items 11, 14) commits to a
**self-trained frozen surrogate** and records that "reusable code, a
checkpoint, a source generator, and a transport study are absent." No
public raw-CTP final-infarct checkpoint exists anywhere in this program's
records (idea-022 is PAUSED on exactly that gap). So 042's "one Colab
session, at most 10 GPU-hours" is the marginal cost conditional on idea
041 successfully training, gating, and freezing its surrogate — a
dependency the card never names. If 041 dies at feasibility or its
performance gate, 042 inherits model training, split governance, and the
performance-gate risk in full. The card lists "a qualifying raw-time
model" under `unverified_claims`, which is honest, but the costing is not.

Same section, second falsified number: the card budgets "25 GB staged
data." Idea 041's revision (item 14) records the inspected public release
as **approximately 99 GB and monolithic** — the identical 25 GB staging
assumption was explicitly removed from 041's card for that reason. 042
must inherit the correction, not the stale assumption.

### 2.4 The deliverable sentence overclaims relative to the card's own rung cap

"The final-infarct model is using delay-independent bolus dispersion **as a
collateral-route signal**" — the trailing clause is a source attribution
the design cannot establish, as the card itself concedes twice (`rung`:
"rung 2 requires validation against independently measured collateral
status, which ISLES'24 does not provide"; `standing_confounds_addressed`:
"None of this proves collateral anatomy caused X"). The program has just
litigated precisely this pattern: idea 041's debate forced the source words
out of the claim because "curve edits and encoder erasure identify a
quantity, not its source" (revision item 25), and idea 023's operator
ruling fixed claim language at the measurable construct. Dispersion in
real ISLES'24 curves can originate from collateral routes, but also from
motion-correction interpolation, 1 frame/sec temporal resampling, partial
volume, or local AIF misspecification — the edit shows the model uses
curve width; it cannot say which physical process wrote the width into the
data. Leaving "collateral-route signal" in the deliverable sentence
guarantees a debate round that ends in the same demotion; under the
claim-identity rule (decision ledger, 2026-08-10), changing that sentence
later risks REJECTED(superseded) bookkeeping. Fix it now: deliverable =
"using delay-independent bolus dispersion (post-alignment curve shape) as
a signal distinct from delay"; collateral stays in interpretation.

### 2.5 Measurement validity of the moments on this release is thinner than the card assumes

The keystone screen verified 1 frame/sec *resampling* of the CTP series.
That cuts both ways. If X is computed on the preprocessed series, every
curve has passed through temporal interpolation and co-registration —
operations that add spatially varying blur, i.e., synthetic dispersion
(inference; mechanism uncontested in the resampling literature and echoed
by 041's debate finding that preprocessing can write temporal structure
into curves). If X is computed on the raw archive, frame timing is
scanner-protocol-dependent and possibly nonuniform (several ISLES'24
scanner platforms are named in the dataset paper with no timing table —
keystone screen, Image Acquisition quote), and second/especially third
central moments are exquisitely sensitive to timestamp error and late-tail
truncation. The card's ICC gate (two AIF selections) measures reliability
against AIF choice only; it cannot detect a shared timing or interpolation
bias. Stage 0 must therefore also fix *which* series (raw versus
derivative) the moments and the model consume, verify per-frame timing
metadata exists for it, and — cheaply — report moment stability under
frame decimation. Third-moment (skew) stability at voxel level on ~30–60
noisy frames is speculation until measured; the card already marks skew
secondary, which is correct.

### 2.6 Smaller defects

- **Citation misattribution (already ordered fixed):** the Frontiers 2022
  paper is by Winder et al., not "Robben et al." — the cycle-005 audit
  verified content but ordered author correction at next revision. Robben
  et al., Med Image Anal 2020 (PMID 31683091) is a different paper and
  belongs in the neighbor list in its own right.
- **Positive control undefined.** `anticipated_negative` conditions
  decisiveness on "positive-control sensitivity," but no arm is designated.
  Presumably the delay arm (a Tmax-reading model must respond); say so, or
  the negative-result value of 3 is unearned.
- **No margin, no power statement.** Twelve cases, paired within-case
  voxel readout, monotone dose response — no effect-size floor or
  cluster-aware power sketch. Feasibility-memo material, but the card
  should not imply the readout is settled.
- **Template concentration.** This is another regional-substitution design
  (9 already, plus 10 counterfactual-synthesis) on the homogenization
  watch. Not a kill, but the portfolio is buying its tenth variation of
  one scientific move; noted for the shortlist ranking.

## 3. Novelty re-check performed for this critique

Beyond confirming the Amador ISBI 2024 abstract (attention-only;
[IEEE](https://ieeexplore.ieee.org/document/10635756/),
[metadata](https://colab.ws/articles/10.1109/isbi56570.2024.10635756)), I
searched for temporal-perturbation or occlusion analyses from the same
line of work ([TCN 2021](https://proceedings.mlr.press/v143/amador21a.html),
[spatio-temporal transformer, MedIA 2023](https://www.sciencedirect.com/science/article/abs/pii/S1361841522002389),
[clinical-context extension](https://www.sciencedirect.com/science/article/pii/S1532046423002885),
[Winder Frontiers 2022](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9672821/)).
None describes curve-shape or dispersion-specific perturbation of a
trained model. "I did not find it" is not proof of absence; full-text
reading of Amador ISBI 2024 remains a binding pre-debate condition
inherited from the c06 audit.

## 4. Plain-pitch fidelity check (opposite-family duty)

The pitch is largely faithful: the delay/dispersion distinction, the
matched-cost comparison, and the closing hedge ("a separate dataset would
still be needed to prove that the model interprets dispersion as
collateral blood flow") all exist in the card at equal or greater
strength. Two defects, both minor but real:

1. "narrows **only** the spread of the curve" — given §2.1, "only" is not
   currently true of any realizable edit; the pitch inherits the card's
   over-constraint rather than exceeding it, and must be reworded when
   §2.1 is repaired.
2. "This study … compares" presumes a qualifying model exists; the card
   itself lists that model among `unverified_claims`. The pitch should
   carry the conditional ("in a model trained on these scans…") so it is
   not more certain than the card.

Note the asymmetry with §2.4: the pitch is actually *more* careful than
the card's deliverable sentence about collateral attribution. The card
should be brought up to the pitch's standard, not vice versa.

## 5. Required revisions (all before debate)

1. Repair the edit design per §2.1 (two-arm concordance plus peak
   control, or honest bundle restatement).
2. Add Amador et al. ISBI 2024 as closest prior work, read in full;
   add Willats 2012 and Robben 2020; correct Winder attribution;
   acknowledge isles24-scout-003-c06 in `dies_like_prior` as the
   superseded within-portfolio predecessor.
3. Rewrite the deliverable sentence without "collateral-route signal"
   (§2.4) — now, not after a debate forces it.
4. Name the idea-041 model dependency and the fallback cost if 041's
   surrogate never freezes; replace 25 GB with the inspected ~99 GB
   monolithic-archive fact.
5. Extend Stage 0 with series-provenance and timing-metadata gates and a
   frame-decimation moment-stability check (§2.5); designate the positive
   control.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does delay-independent bolus
dispersion, computed from the released ISLES'24 CTP curves, add voxel-level
final-infarct discrimination beyond Tmax/delay within-case — an
association-first study needing no trained model, no checkpoint, and no
curve edits?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — it tests whether the
dispersion signal exists and matters in this cohort, not whether a model
uses it; use-versus-association is exactly the program's own distinction.
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — fold it into 042's Stage 0 as
the decisive precondition: if dispersion carries no within-delay outcome
information in ISLES'24, the model-use question loses its motivation before
any model is trained; if it does, the result is independently reportable
(Willats 2012 predicts it should) and every measurement asset transfers.
IS IT ACTUALLY WORTH DOING? YES — it is one to two days of deterministic
computation on public data with existing ground truth, it is informative in
both directions, and it is the cheapest honest test of whether this card's
entire premise has empirical support in the actual release.
```


===== ideas/042/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed intervention does not identify model use of bolus dispersion because its “dispersion-only” curve edit is either physiologically unrealistic or necessarily changes peak height, introducing a simpler intensity cue.

**Argument:** The card requires contraction of post-alignment curve width while preserving arrival time, area, peak height, and baseline noise power. At fixed area and peak, narrowing is bounded and ultimately forces flat-topped, nonphysiologic shapes rather than the smooth tissue concentration curves generated by an arterial input convolved with a residue function; such edits are unlikely to pass the card’s own same-case interpolation and nearest-neighbor realism gates. Allowing the peak to rise restores the expected width–height coupling at fixed area, but then a model response can be explained by peak concentration or CBF-related amplitude rather than dispersion. Equal Wasserstein cost and a delay-only arm do not remove that alternative. This is an identifiability failure at rung 1, not merely an implementation difficulty: a positive response would not establish selective use of delay-independent width/skew. Adding an amplitude-only control and testing both a physiologic area-preserving/peak-varying arm and a deliberately peak-preserving arm would still answer the original question, so that amendment passes the identity check; restating the estimand as a generic width–peak “shape bundle” would not answer the original selective-dispersion question and should instead become a successor candidate.

**What would change my mind:** Show, before model inference, a concrete three-arm construction on released ISLES’24 curves in which (1) area-preserving dispersion edits, (2) peak-only controls at fixed width, and (3) matched delay edits each pass prespecified same-case support and curve-realism gates, then preregister a contrast or concordance criterion that rules out peak-only sensitivity as the explanation for the dispersion response.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card's dispersion arm demands the impossible: at fixed area and fixed peak height, contraction toward the arterial width is bounded by the boxcar limit, so the edit either produces flat-topped curves that fail the card's own same-case realism gates or must let the peak rise, at which point a model response is explainable by peak amplitude — a simpler intensity cue — and the delay arm plus equal transport cost cannot exclude that alternative.

**Response:** AMEND

**Argument:** The moment-bound argument is correct and I will not contest it. At fixed area A and peak P, the minimum attainable second central moment is that of the boxcar of height P and duration A/P; any contraction demanded below that width is infeasible outright, and approaching it forces exactly the flat-topped shapes the realism gate was written to exclude. The deeper point is also right: because area couples width and peak in the convolution family the realism gate enforces, delay, width, and peak cannot all be independently factorized by any single physiological edit. The constraint set in `X_measurement`/`use_vs_association` is internally contradictory as written, and I concede that a positive result under the "let the peak rise" escape would not, alone, establish selective width/skew use.

The amendment, exactly:

1. **Replace the single dispersion arm with three arms plus the existing delay arm.** (a) *Physiologic dispersion arm:* contraction of the aligned curve toward the arterial width along interpolation paths through observed same-case curves, area preserved, peak permitted to rise as the family dictates; the incidental peak change Δp(d) at each dose d ∈ {25, 50, 75%} is recorded per voxel. (b) *Peak-only control arm:* amplitude scaling at fixed width and fixed arrival time, constructed per voxel to reproduce the same Δp(d), accepting the proportional area change this necessarily entails. (c) *Peak-preserving dispersion arm, secondary and low-dose only:* retained where the boxcar bound leaves headroom (small contractions far from the limit) and the realism gates pass; dropped without prejudice where they do not. (d) *Delay arm:* unchanged, matched transport cost, still the positive control — this also discharges the critique's separate demand that the positive control be designated.

2. **Preregistered criterion (conjunction, both required for the use claim):** R_disp(d) − R_delay(d) positive and dose-ordered, as before; AND R_disp(d) − R_peak(d) positive and dose-ordered, which is the new contrast that rules out peak-only sensitivity. Concordance of the low-dose peak-preserving arm, where constructible, is reported as supporting evidence, not required.

3. **Construction-before-inference gate, folded into Stage 0:** all arms at all doses are built on the 20 inspection cases and must pass the prespecified same-case support and nearest-neighbor realism gates at a preregistered voxel-passage rate before any model is queried. Failure kills the confirmatory design, not merely a dose level. This is precisely the demonstration the critic asked for, made a binding gate rather than a promise.

**What is lost, stated plainly.** First, the elegant one-edit claim — "narrows only the spread" — is gone; the plain pitch and `X_measurement` must be reworded, since no realizable single edit changes width alone at fixed area and peak. Second, identification of width use now rests on an *arm contrast* rather than an *invariance*: the subtraction R_disp − R_peak controls the peak cue only up to approximate additivity of small-dose responses, and the peak-only control carries an incidental area change the dispersion arm does not, so the contrast is not a perfect decomposition — the contract must state the direction in which this is conservative and treat large-dose divergence between the two dispersion arms as uninterpretable rather than adjudicating it post hoc. Third, roughly 50% more inference compute; trivial in absolute terms (the envelope stays inside one session) but the card's costing must say so honestly alongside the idea-041 dependency correction already ordered by the critique.

**Identity check:** the one-sentence question — is the model using delay-independent bolus dispersion as a signal distinct from delay — is unchanged. What changed is how the peak confound is handled: measured and contrasted out rather than held fixed by an impossible constraint. The critic pre-registered that exactly this amendment passes the identity check, and I am taking that path rather than the shape-bundle restatement, which I agree would be a different question.

**Status:** OPEN

## Round 2 — CRITIC

**Position:** The amendment preserves the original question, but its new dispersion-minus-peak contrast still cannot identify selective dispersion use because the two arms differ in area and the claimed cancellation assumes an untested additive model response.

**Argument:** The identity check passes: the proposed conclusion remains that the model uses post-alignment width/skew distinctly from delay, rather than the weaker width–peak bundle. The amendment also concedes the original impossible invariance and adds the right control family. But its confirmatory conjunction does not deliver the promised identification. In the physiologic dispersion arm, area is fixed while width contracts and peak rises; in the peak-only arm, width is fixed while peak is matched and area rises proportionally. Therefore `R_disp − R_peak` contrasts `(width change + peak change at fixed area)` with `(peak change + area change at fixed width)`. A positive difference may arise because the model responds negatively to the control arm's added area, because peak interacts nonlinearly with width, or because changing total contrast moves the control through a different part of the model's response surface—not because it selectively uses dispersion. The proposer explicitly acknowledges that subtraction works only under “approximate additivity,” but neither a realism gate nor dose ordering tests that assumption, and there is no justified direction in which the unmatched area change is necessarily conservative for an arbitrary raw-time neural network. The optional peak-preserving arm could address this only if it were confirmatory on a prespecified common-support voxel set; making it secondary, constructible only opportunistically, and droppable without prejudice leaves the primary positive result multiply interpretable. Thus the amendment is a useful feasibility repair but not yet an identifiability repair for the original claim.

**What would change my mind:** Before inference, define a prespecified common-support subset on which a low-dose peak-preserving dispersion edit and matched peak-only and delay controls all pass the same realism gates, and make concordance on that subset necessary for the selective-dispersion claim; alternatively, provide a validated factorial response-surface design that independently varies width, peak, and area within observed ISLES'24 support and empirically bounds the relevant interactions rather than assuming additivity.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The round-one repair traded an impossible invariance for an invalid subtraction: because the peak-only control necessarily changes area while the physiologic dispersion arm holds it fixed, R_disp − R_peak differences width against area under an additivity assumption no gate tests, and no conservativeness direction can be asserted for an arbitrary raw-time network. The only arm that carries the clean invariance — the peak-preserving dispersion edit — was left optional and droppable, so the primary positive result remains multiply interpretable.

**Response:** AMEND

**Argument:** Correct on every step. The subtraction was doing inferential work that only an invariance can do, and I asserted "approximate additivity" and "a conservative direction" without any instrument in the design that could check either. A nonlinear network gives no license for arm-difference algebra across arms that move different variable pairs. I take the critic's first offered path exactly, and I decline the factorial alternative for an honest reason stated below.

The amendment, exactly:

1. **The confirmatory arm is now the low-dose peak-preserving dispersion edit, on a prespecified common-support subset S.** On S, this edit contracts post-alignment width while holding arrival time, area, AND peak height simultaneously fixed — the invariance the original card promised, asserted only where it is realizable instead of pretended everywhere. No subtraction against a peak arm is needed on S, because the peak never moves; the selective-use criterion is invariance-based, not decomposition-based, and requires no additivity assumption.

2. **S is defined deterministically before any model inference.** During Stage 0, on the inspection cases: doses are restricted to the range where the contracted width retains prespecified headroom above the boxcar bound (so the edit stays inside the smooth same-case family), and a voxel enters S only if the peak-preserving dispersion edit, the physiologic dispersion edit, the peak-only control, and the matched delay edit ALL pass the identical same-case support and nearest-neighbor realism gates at every retained dose. Membership is computed from unedited data plus edit constructions and frozen before the model is queried.

3. **S carries its own kill gate.** A minimum size — a prespecified fraction of gated affected-tissue voxels per case and a minimum number of contributing cases, with the numbers fixed at Stage 0 from the 20 inspection cases before any selection — below which the confirmatory design dies. An empty or thin S is a kill, not a downgrade to the physiologic arm.

4. **Preregistered confirmatory conjunction, all evaluated on S, all required:** (i) peak-preserving dispersion response exceeds the matched-transport-cost delay response, dose-ordered over the retained low doses — primary; (ii) the physiologic dispersion arm is concordant on S (same sign, dose-ordered) — required, because if the machinery that generalizes beyond S disagrees with the clean invariance where both exist, the generalization is unearned; (iii) the peak-only control on S is reported as the measured magnitude of the pure-amplitude cue — it no longer participates in any subtraction, and a large peak response does not rescue or sink (i), it contextualizes how much of the physiologic arm's response the peak cue could explain outside S. Discordance between (i) and (ii) is itself a reportable finding — the model responds to the width–peak bundle but not to width alone — not a post hoc adjudication.

5. **The 50% and 75% physiologic doses are demoted to exploratory.** They exist to describe the response surface at large perturbations, and nothing confirmatory rests on them.

**Why not the factorial alternative:** a validated factorial design would need to vary width, peak, and area independently within observed ISLES'24 support — but the round-one concession was precisely that the physiological curve family does not span that cube; area couples the other two. A factorial response surface built inside a non-spanning family would estimate interactions from extrapolated corners and launder the same additivity assumption through a regression. The common-support path is weaker in scope and honest; the factorial path is broader in scope and fake.

**What is lost, stated plainly.** First, the confirmatory dose range shrinks to small contractions; nothing is claimed about large dispersion changes. Second, the population narrows to S, and S is not a random subset — headroom above the boxcar bound selects voxels whose curves are already wide relative to their area/peak ratio, i.e., the more dispersed tissue. The conclusion therefore reads "in tissue dispersed enough for the edit to be constructible, the model uses width distinctly from delay" — arguably the tissue the question was always about, but a genuine scope reduction that the card and plain pitch must state. Third, a new kill mode: if S is empty or thin on the real release, the confirmatory design dies at Stage 0 having consumed the inspection budget. Fourth, this is the second amendment of the debate; under the debate rules a third would be strong evidence the original idea was wrong. What remains contestable — the specific headroom multiple, gate thresholds, and minimum-S numbers — is feasibility-memo material, not debate material, and I do not believe any objection to the identification logic itself remains unanswered.

**Identity check:** the one-sentence question — is the model using delay-independent bolus dispersion as a signal distinct from delay — is unchanged. The revised design answers it by exhibiting the originally promised invariance on the subdomain where physics permits it, rather than by an algebraic contrast that assumed what it needed to prove. Domain narrowed; question identical.

**Status:** OPEN


===== ideas/042/idea_card.json =====
{
  "id": "isles24-scout-005-c08",
  "parent_ids": [],
  "track": "wide",
  "entry_point": 2,
  "title": "Delay is not dispersion",
  "question": "Is a raw-CT-perfusion final-infarct model using bolus dispersion\u2014the width and skew of contrast passage after arrival-time alignment\u2014as a collateral-route signal distinct from simple delay?",
  "rung": "Target rung 1: selective use of delay-independent bolus dispersion; rung 2 requires validation against independently measured collateral status, which ISLES'24 does not provide.",
  "deliverable_sentence": "The final-infarct model is using delay-independent bolus dispersion as a collateral-route signal.",
  "X_measurement": "Extract an arterial input curve automatically from high-peak, early-arrival intracranial arterial voxels. For each tissue voxel, baseline-subtract and normalize the contrast curve, align its first temporal moment to the arterial curve, and compute dispersion X as the square-root difference in second central moments, with signed third standardized moment (skewness) secondary. These chromatography-style moment formulas are deterministic and annotator-free. Delay and dispersion are explicitly distinguished in Calamante et al., DOI 10.1002/mrm.20873, and in Konstas et al., PMCID PMC7051660.",
  "suspected_signal": "Collateral blood reaches threatened tissue along longer, branching routes. After removing pure arrival delay, those multiple paths can broaden and reshape the bolus. Conventional Tmax conflates timing and curve shape; a raw-time network could use residual width/skew as evidence about route complexity and therefore tissue survival, but it could also be reading cardiac output, injection quality, or noise.",
  "use_vs_association": "Within each affected voxel, construct two optimal-transport curve substitutions: a dispersion-only edit that contracts the aligned curve toward the arterial width while preserving arrival time, area, peak height, and baseline noise power, and a delay-only edit of equal temporal transport cost that preserves width and skew. A stronger, dose-ordered model response to the dispersion edit demonstrates use distinct from delay association.",
  "keystone_prerequisite": "The released raw CTP captures baseline, arterial peak, and washout sufficiently to estimate delay-independent second and third moments without truncation, and dispersion has within-delay variation in affected tissue.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_residual_assumption": "Raw CTP availability is verified, but full-bolus capture and frame timing have not been inspected. Stage 0 must require at least 90% of 20 cases to have 5 or more pre-arrival frames, an arterial peak at least 5 frames before acquisition end, venous downslope captured to at most 30% of peak, and dispersion test-retest ICC at least 0.85 across two automatic arterial-input selections. Failure kills the card.",
  "rung_reached": "0; rung 1 after capture, measurement, model-performance, edit-realism, delay-discrimination, and dose-response gates. The word collateral remains source-supported interpretation, not confirmed physiology, until external validation.",
  "dies_like_prior": "It overlaps the broad territory of isles24-scout-001-c01 (collateral clock), c03 (blood leaving), and idea-022 (end of bolus), but changes the estimand and the failure test. c01 uses conventional delay burden, c03 uses venous asymmetry, and idea-022 studies scan truncation; c08 explicitly holds arrival time and curve area fixed while changing only post-alignment width/skew. It still risks IDENTIFIABILITY_FAILURE if cardiac/injection effects cannot be removed, so the confirmatory unit is within-case local tissue and the biological collateral wording is capped at rung 1.",
  "closest_prior_work": "Perfusion physics has long shown that delay and dispersion are distinct and that uncorrected dispersion can create large perfusion errors. Collateral studies relate delay thresholds and contrast transit to outcome, and raw-time networks predict tissue outcome. The located primary work does not selectively exchange dispersion and delay in a model-use test.",
  "novelty_neighbors": [
    {
      "work": "Calamante et al., Bolus delay and dispersion in perfusion MRI: implications for tissue predictor models in stroke",
      "identifier": "DOI 10.1002/mrm.20873; PMID 16598717",
      "relation": "Shows that delay does not reliably determine dispersion and that observed dispersion can cause substantial perfusion errors; it analyzes measurement physics, not learned-model use."
    },
    {
      "work": "Lin et al., Perfusion Computed Tomography Accurately Quantifies Collateral Flow After Acute Ischemic Stroke",
      "identifier": "DOI 10.1161/STROKEAHA.119.028284; PMID 31948385",
      "relation": "Validates a delay-time volume ratio against dynamic-angiographic collateral scores; it motivates collateral relevance but does not isolate bolus width from delay."
    },
    {
      "work": "Robben et al., Predicting the tissue outcome of acute ischemic stroke from acute 4D CT perfusion imaging using temporal features and deep learning",
      "identifier": "DOI 10.3389/fnins.2022.1009654; PMCID PMC9672821",
      "relation": "Demonstrates raw concentration-time and residue-curve outcome models and learned temporal features, but does not intervene separately on dispersion and delay."
    }
  ],
  "novelty_delta": "The proposed paired curve transport is the first located experiment to hold arrival time, area, peak, and noise fixed while selectively changing bolus dispersion and asking whether a raw final-infarct model responds more than to a matched delay edit.",
  "why_not_done": "NEW_CAPABILITY: ISLES'24 newly combines public raw four-dimensional CTP, acute multimodal context, treatment-era follow-up infarct masks, and registered derivatives, making a controlled raw-curve use test reproducible rather than dependent on a private perfusion cohort.",
  "existing_assets": "Official raw CTP, registered maps and final masks; published automatic arterial-input strategies in the perfusion literature; moment and one-dimensional optimal-transport formulas; a compact raw-time model design from the closest neighbor.",
  "smallest_decisive_experiment": "Stage 0 inspects bolus capture and moment stability in 20 cases, then selects 12 with at least 10 mL of Tmax>6 s tissue spanning two dispersion tertiles. Using the same frozen shallow raw-time model and split discipline as c07, perform 25/50/75% local dispersion contraction, matched delay shifts, and contralateral normal-tissue edits. Primary readout is the paired affected-tissue probability contrast (dispersion edit minus delay edit), conditioned on equal Wasserstein transport cost; require monotone dose response. Compute envelope: one Colab GPU session, at most 10 GPU-hours and 25 GB staged data; the intervention experiment can reuse a qualifying frozen model but is scientifically independent; no new annotation.",
  "standing_confounds_addressed": "Within-case local edits hold patient cardiac output, injection, scanner, center, treatment, anatomy, and global arterial curve fixed. Arrival-time alignment and the matched delay arm isolate dispersion from delay. Area, peak, baseline noise power, and transport cost are held or matched; contralateral edits test generic curve manipulation. Truncation is a hard exclusion, not an adjusted covariate. None of this proves collateral anatomy caused X, so independent collateral validation is required before rung 2.",
  "alternative_explanations": [
    "Dispersion reflects cardiac output or injection rather than collateral routes; within-case normalization removes global effects but not regional arterial-input misspecification.",
    "Curve contraction creates unrealistic kinetics; interpolation between observed same-case curves and nearest-neighbor feature-distance gates bound this risk.",
    "The model uses ordinary Tmax; matched delay edits and preserved arrival time directly test that alternative."
  ],
  "anticipated_negative": "Decisive for dispersion-versus-delay use in the tested model if full-bolus capture, X reliability, performance, realism, and positive-control sensitivity all pass; otherwise sensitivity-limited.",
  "cross_domain": {
    "borrowed_construct": "Residence-time distributions from chemical engineering and chromatography: a transported tracer's mean arrival and its dispersion are separate system properties, with path multiplicity broadening the distribution even after the mean is aligned.",
    "measurement_it_implies": "Central moments of the normalized tissue concentration curve relative to the arterial input, and optimal-transport edits that independently alter the mean or width at matched cost.",
    "what_changes_if_dropped": "Without residence-time theory the card collapses into another Tmax perturbation and cannot make or test the crucial delay-versus-dispersion distinction."
  },
  "remaining_legwork": "One day for capture and arterial-input stability; one Colab session for the paired interventions if a qualifying model exists; external collateral validation is a separate successor requirement.",
  "design_template": "regional-substitution",
  "entry_point_2_requirements": "Measurement: aligned curve variance and skew relative to the arterial input. Confused artifacts: simple delay, global injection/cardiac effects, truncation, and edit cost; matched delay transport, within-case normalization, hard capture gates, and equal-cost controls address them.",
  "scores": {
    "clarity": {
      "value": 5,
      "why": "Delay and dispersion are separately defined, measured, edited, and compared."
    },
    "identifiability": {
      "value": 3,
      "why": "The paired edit isolates dispersion use from delay, but collateral-route attribution remains vulnerable to local arterial-input error."
    },
    "medical_relevance": {
      "value": 4,
      "why": "Distinguishing late arrival from dispersed collateral passage could change interpretation and temporal-augmentation choices for raw-CTP models."
    },
    "interest": {
      "value": 5,
      "why": "The claim that two visually similar late boluses mean different things to a model is mechanistically surprising and clinically legible."
    },
    "prior_legwork": {
      "value": 4,
      "why": "The transport physics, stroke dispersion evidence, collateral relevance, and raw-model architecture all exist."
    },
    "feasibility": {
      "value": 3,
      "why": "Capped because full-bolus capture and stable local dispersion on this release are uninspected."
    },
    "data_readiness": {
      "value": 4,
      "why": "Raw public time series and outcomes are available, though staged download is required."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "Paired dose-response is direct; transport realism and arterial-input stability need custom gates."
    },
    "negative_result_value": {
      "value": 3,
      "why": "A gated null distinguishes this descriptor from delay for one model but does not cover all raw architectures."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Three close primary works were searched and the precise intervention was absent; systematic novelty review is still pending."
    },
    "regret": {
      "value": 4,
      "why": "The raw curves already contain the needed distinction, and collapsing both effects into Tmax may be an avoidable modeling error."
    }
  },
  "priority_score": 3.7,
  "unverified_claims": [
    "full bolus and washout capture in at least 90% of inspected cases",
    "automatic arterial-input stability",
    "sufficient within-delay dispersion variation",
    "physiological realism of curve transport",
    "a qualifying raw-time model",
    "collateral interpretation and novelty beyond targeted search"
  ],
  "plain_pitch": "Contrast can reach threatened brain late, but it can also arrive spread out after taking many winding routes; those are different physical effects. This study holds arrival time and total contrast fixed, then narrows only the spread of the curve and compares that with an equally large pure time shift. If the model reacts specifically to narrowing, it is reading bolus dispersion rather than merely a late arrival\u2014although a separate dataset would still be needed to prove that the model interprets dispersion as collateral blood flow.",
  "charter": "isles24"
}


===== ideas/042/keystone_screen.md =====
# Keystone screen — Idea 042: Delay is not dispersion

## Keystone as stated

> The released raw CTP captures baseline, arterial peak, and washout sufficiently to estimate delay-independent second and third moments without truncation, and dispersion has within-delay variation in affected tissue.

This is a compound empirical prerequisite. It requires (1) adequate temporal support in the released cases and (2) measurable dispersion variation after conditioning on delay. Merely establishing that a four-dimensional CTP file exists is not enough.

## What was inspected

### Primary dataset paper

The published ISLES'24 dataset paper confirms the modality and the preprocessing cadence. In **Materials and Methods → Data Preprocessing**, it states:

> “Four-dimensional CT perfusion series underwent image co-registration and temporal resampling (1 frame/sec); perfusion maps (cerebral blood flow, cerebral blood volume, mean transit time, and time-to-maximum) were derived using the clinical, U.S. Food and Drug Administration–cleared software icobrain cva (version 1.5.0, icometrix).”

Source: Riedel et al., *Radiology: Artificial Intelligence* (2026), DOI 10.1148/ryai.250603, [HTML, Data Preprocessing, lines 102–105](https://pubs.rsna.org/doi/10.1148/ryai.250603).

The same paper's **Image Acquisition** section names several scanners but gives no CTP acquisition duration, number of temporal frames, precontrast-frame count, injection timing, or washout/truncation statistic:

> “Imaging at two centers—University Hospital Munich and University Hospital Zurich—used various CT (Siemens Somatom Force, Somatom Xcite, Somatom AS+ and Philips Brilliance 64, Ingenuity) and MRI (3-T Philips Achieva, Ingenia; 3-T Siemens Verio, Trio and 1.5-T Avanto) systems.”

Source: same paper, [Image Acquisition, lines 94–100](https://pubs.rsna.org/doi/10.1148/ryai.250603).

### Primary dataset record/schema

The creator-authored dataset record confirms that the per-case release includes a CTP time-series file:

> “Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

It also shows the concrete path `raw_data/.../sub-strokecase0001_ses-0001_ctp.nii.gz`, but publishes no temporal dimension or per-case timing table.

Source: official institutional dataset record for Zenodo DOI 10.5281/zenodo.16731717, [Description and Data structure, lines 35–46](https://research.tue.nl/en/datasets/isles24-a-real-world-longitudinal-multimodal-stroke-dataset/).

## Residual-assumption check

The nearest checkable fact is therefore **raw 4D CTP exists and a processed series was resampled to 1 frame/sec**. The card is still assuming that the series begins early enough, ends late enough, and has enough uncontaminated samples to support stable second and especially third central moments. A sampling interval does not determine acquisition duration or bolus coverage. Neither inspected primary source reports the card's proposed gates: five pre-arrival frames, arterial peak at least five frames before the end, venous downslope to at most 30% of peak, or passage of those gates in at least 90% of 20 cases.

The second half of the stated keystone—within-delay dispersion variation in affected tissue—is also a property of the voxel data, not established by the paper or schema. It requires direct case-level inspection. No primary-source statement found supplies that measurement.

The load-bearing assumption was correctly named in the card, but it was not verified by the nearest available release documentation. At this screen price, the evidence supports neither PASS nor KILL: the raw archive must be inspected case by case.

```json
{"verdict":"UNVERIFIABLE","evidence":"Four-dimensional CT perfusion series underwent image co-registration and temporal resampling (1 frame/sec); perfusion maps (cerebral blood flow, cerebral blood volume, mean transit time, and time-to-maximum) were derived using the clinical, U.S. Food and Drug Administration–cleared software icobrain cva (version 1.5.0, icometrix).","source":"https://pubs.rsna.org/doi/10.1148/ryai.250603 — Materials and Methods, Data Preprocessing (HTML lines 102–105)","note":"The sources verify raw 4D CTP and cadence, but not per-case baseline/peak/washout coverage or within-delay dispersion variation; direct archive inspection is required."}
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
This is round 3. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed intervention does not identify model use of bolus dispersion because its “dispersion-only” curve edit is either physiologically unrealistic or necessarily changes peak height, introducing a simpler intensity cue.

**Argument:** The card requires contraction of post-alignment curve width while preserving arrival time, area, peak height, and baseline noise power. At fixed area and peak, narrowing is bounded and ultimately forces flat-topped, nonphysiologic shapes rather than the smooth tissue concentration curves generated by an arterial input convolved with a residue function; such edits are unlikely to pass the card’s own same-case interpolation and nearest-neighbor realism gates. Allowing the peak to rise restores the expected width–height coupling at fixed area, but then a model response can be explained by peak concentration or CBF-related amplitude rather than dispersion. Equal Wasserstein cost and a delay-only arm do not remove that alternative. This is an identifiability failure at rung 1, not merely an implementation difficulty: a positive response would not establish selective use of delay-independent width/skew. Adding an amplitude-only control and testing both a physiologic area-preserving/peak-varying arm and a deliberately peak-preserving arm would still answer the original question, so that amendment passes the identity check; restating the estimand as a generic width–peak “shape bundle” would not answer the original selective-dispersion question and should instead become a successor candidate.

**What would change my mind:** Show, before model inference, a concrete three-arm construction on released ISLES’24 curves in which (1) area-preserving dispersion edits, (2) peak-only controls at fixed width, and (3) matched delay edits each pass prespecified same-case support and curve-realism gates, then preregister a contrast or concordance criterion that rules out peak-only sensitivity as the explanation for the dispersion response.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card's dispersion arm demands the impossible: at fixed area and fixed peak height, contraction toward the arterial width is bounded by the boxcar limit, so the edit either produces flat-topped curves that fail the card's own same-case realism gates or must let the peak rise, at which point a model response is explainable by peak amplitude — a simpler intensity cue — and the delay arm plus equal transport cost cannot exclude that alternative.

**Response:** AMEND

**Argument:** The moment-bound argument is correct and I will not contest it. At fixed area A and peak P, the minimum attainable second central moment is that of the boxcar of height P and duration A/P; any contraction demanded below that width is infeasible outright, and approaching it forces exactly the flat-topped shapes the realism gate was written to exclude. The deeper point is also right: because area couples width and peak in the convolution family the realism gate enforces, delay, width, and peak cannot all be independently factorized by any single physiological edit. The constraint set in `X_measurement`/`use_vs_association` is internally contradictory as written, and I concede that a positive result under the "let the peak rise" escape would not, alone, establish selective width/skew use.

The amendment, exactly:

1. **Replace the single dispersion arm with three arms plus the existing delay arm.** (a) *Physiologic dispersion arm:* contraction of the aligned curve toward the arterial width along interpolation paths through observed same-case curves, area preserved, peak permitted to rise as the family dictates; the incidental peak change Δp(d) at each dose d ∈ {25, 50, 75%} is recorded per voxel. (b) *Peak-only control arm:* amplitude scaling at fixed width and fixed arrival time, constructed per voxel to reproduce the same Δp(d), accepting the proportional area change this necessarily entails. (c) *Peak-preserving dispersion arm, secondary and low-dose only:* retained where the boxcar bound leaves headroom (small contractions far from the limit) and the realism gates pass; dropped without prejudice where they do not. (d) *Delay arm:* unchanged, matched transport cost, still the positive control — this also discharges the critique's separate demand that the positive control be designated.

2. **Preregistered criterion (conjunction, both required for the use claim):** R_disp(d) − R_delay(d) positive and dose-ordered, as before; AND R_disp(d) − R_peak(d) positive and dose-ordered, which is the new contrast that rules out peak-only sensitivity. Concordance of the low-dose peak-preserving arm, where constructible, is reported as supporting evidence, not required.

3. **Construction-before-inference gate, folded into Stage 0:** all arms at all doses are built on the 20 inspection cases and must pass the prespecified same-case support and nearest-neighbor realism gates at a preregistered voxel-passage rate before any model is queried. Failure kills the confirmatory design, not merely a dose level. This is precisely the demonstration the critic asked for, made a binding gate rather than a promise.

**What is lost, stated plainly.** First, the elegant one-edit claim — "narrows only the spread" — is gone; the plain pitch and `X_measurement` must be reworded, since no realizable single edit changes width alone at fixed area and peak. Second, identification of width use now rests on an *arm contrast* rather than an *invariance*: the subtraction R_disp − R_peak controls the peak cue only up to approximate additivity of small-dose responses, and the peak-only control carries an incidental area change the dispersion arm does not, so the contrast is not a perfect decomposition — the contract must state the direction in which this is conservative and treat large-dose divergence between the two dispersion arms as uninterpretable rather than adjudicating it post hoc. Third, roughly 50% more inference compute; trivial in absolute terms (the envelope stays inside one session) but the card's costing must say so honestly alongside the idea-041 dependency correction already ordered by the critique.

**Identity check:** the one-sentence question — is the model using delay-independent bolus dispersion as a signal distinct from delay — is unchanged. What changed is how the peak confound is handled: measured and contrasted out rather than held fixed by an impossible constraint. The critic pre-registered that exactly this amendment passes the identity check, and I am taking that path rather than the shape-bundle restatement, which I agree would be a different question.

**Status:** OPEN

## Round 2 — CRITIC

**Position:** The amendment preserves the original question, but its new dispersion-minus-peak contrast still cannot identify selective dispersion use because the two arms differ in area and the claimed cancellation assumes an untested additive model response.

**Argument:** The identity check passes: the proposed conclusion remains that the model uses post-alignment width/skew distinctly from delay, rather than the weaker width–peak bundle. The amendment also concedes the original impossible invariance and adds the right control family. But its confirmatory conjunction does not deliver the promised identification. In the physiologic dispersion arm, area is fixed while width contracts and peak rises; in the peak-only arm, width is fixed while peak is matched and area rises proportionally. Therefore `R_disp − R_peak` contrasts `(width change + peak change at fixed area)` with `(peak change + area change at fixed width)`. A positive difference may arise because the model responds negatively to the control arm's added area, because peak interacts nonlinearly with width, or because changing total contrast moves the control through a different part of the model's response surface—not because it selectively uses dispersion. The proposer explicitly acknowledges that subtraction works only under “approximate additivity,” but neither a realism gate nor dose ordering tests that assumption, and there is no justified direction in which the unmatched area change is necessarily conservative for an arbitrary raw-time neural network. The optional peak-preserving arm could address this only if it were confirmatory on a prespecified common-support voxel set; making it secondary, constructible only opportunistically, and droppable without prejudice leaves the primary positive result multiply interpretable. Thus the amendment is a useful feasibility repair but not yet an identifiability repair for the original claim.

**What would change my mind:** Before inference, define a prespecified common-support subset on which a low-dose peak-preserving dispersion edit and matched peak-only and delay controls all pass the same realism gates, and make concordance on that subset necessary for the selective-dispersion claim; alternatively, provide a validated factorial response-surface design that independently varies width, peak, and area within observed ISLES'24 support and empirically bounds the relevant interactions rather than assuming additivity.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The round-one repair traded an impossible invariance for an invalid subtraction: because the peak-only control necessarily changes area while the physiologic dispersion arm holds it fixed, R_disp − R_peak differences width against area under an additivity assumption no gate tests, and no conservativeness direction can be asserted for an arbitrary raw-time network. The only arm that carries the clean invariance — the peak-preserving dispersion edit — was left optional and droppable, so the primary positive result remains multiply interpretable.

**Response:** AMEND

**Argument:** Correct on every step. The subtraction was doing inferential work that only an invariance can do, and I asserted "approximate additivity" and "a conservative direction" without any instrument in the design that could check either. A nonlinear network gives no license for arm-difference algebra across arms that move different variable pairs. I take the critic's first offered path exactly, and I decline the factorial alternative for an honest reason stated below.

The amendment, exactly:

1. **The confirmatory arm is now the low-dose peak-preserving dispersion edit, on a prespecified common-support subset S.** On S, this edit contracts post-alignment width while holding arrival time, area, AND peak height simultaneously fixed — the invariance the original card promised, asserted only where it is realizable instead of pretended everywhere. No subtraction against a peak arm is needed on S, because the peak never moves; the selective-use criterion is invariance-based, not decomposition-based, and requires no additivity assumption.

2. **S is defined deterministically before any model inference.** During Stage 0, on the inspection cases: doses are restricted to the range where the contracted width retains prespecified headroom above the boxcar bound (so the edit stays inside the smooth same-case family), and a voxel enters S only if the peak-preserving dispersion edit, the physiologic dispersion edit, the peak-only control, and the matched delay edit ALL pass the identical same-case support and nearest-neighbor realism gates at every retained dose. Membership is computed from unedited data plus edit constructions and frozen before the model is queried.

3. **S carries its own kill gate.** A minimum size — a prespecified fraction of gated affected-tissue voxels per case and a minimum number of contributing cases, with the numbers fixed at Stage 0 from the 20 inspection cases before any selection — below which the confirmatory design dies. An empty or thin S is a kill, not a downgrade to the physiologic arm.

4. **Preregistered confirmatory conjunction, all evaluated on S, all required:** (i) peak-preserving dispersion response exceeds the matched-transport-cost delay response, dose-ordered over the retained low doses — primary; (ii) the physiologic dispersion arm is concordant on S (same sign, dose-ordered) — required, because if the machinery that generalizes beyond S disagrees with the clean invariance where both exist, the generalization is unearned; (iii) the peak-only control on S is reported as the measured magnitude of the pure-amplitude cue — it no longer participates in any subtraction, and a large peak response does not rescue or sink (i), it contextualizes how much of the physiologic arm's response the peak cue could explain outside S. Discordance between (i) and (ii) is itself a reportable finding — the model responds to the width–peak bundle but not to width alone — not a post hoc adjudication.

5. **The 50% and 75% physiologic doses are demoted to exploratory.** They exist to describe the response surface at large perturbations, and nothing confirmatory rests on them.

**Why not the factorial alternative:** a validated factorial design would need to vary width, peak, and area independently within observed ISLES'24 support — but the round-one concession was precisely that the physiological curve family does not span that cube; area couples the other two. A factorial response surface built inside a non-spanning family would estimate interactions from extrapolated corners and launder the same additivity assumption through a regression. The common-support path is weaker in scope and honest; the factorial path is broader in scope and fake.

**What is lost, stated plainly.** First, the confirmatory dose range shrinks to small contractions; nothing is claimed about large dispersion changes. Second, the population narrows to S, and S is not a random subset — headroom above the boxcar bound selects voxels whose curves are already wide relative to their area/peak ratio, i.e., the more dispersed tissue. The conclusion therefore reads "in tissue dispersed enough for the edit to be constructible, the model uses width distinctly from delay" — arguably the tissue the question was always about, but a genuine scope reduction that the card and plain pitch must state. Third, a new kill mode: if S is empty or thin on the real release, the confirmatory design dies at Stage 0 having consumed the inspection budget. Fourth, this is the second amendment of the debate; under the debate rules a third would be strong evidence the original idea was wrong. What remains contestable — the specific headroom multiple, gate thresholds, and minimum-S numbers — is feasibility-memo material, not debate material, and I do not believe any objection to the identification logic itself remains unanswered.

**Identity check:** the one-sentence question — is the model using delay-independent bolus dispersion as a signal distinct from delay — is unchanged. The revised design answers it by exhibiting the originally promised invariance on the subdomain where physics permits it, rather than by an algebraic contrast that assumed what it needed to prove. Domain narrowed; question identical.

**Status:** OPEN

