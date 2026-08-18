You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/038
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

- **IDENTIFIABILITY_FAILURE** x10: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
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
- **idea-037** [REJECTED/DEBATED/wide] -- The scan remembers which hospital took it -- killed: IDENTIFIABILITY_FAILURE
- **idea-038** [SHORTLISTED/CRITIQUED/wide] -- Does the model price the last mile of blood delivery?
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


===== ideas/038/README.md =====
# Idea 038: Does the model price the last mile of blood delivery?

Selected from scouting cycle isles24-003, candidate 7.


===== ideas/038/critique.md =====
FATAL OBJECTION: The destination-swap response cannot identify use of arterial-border distance because changing destination necessarily changes global coordinates, surrounding anatomy, and patch-context compatibility together with the purported vascular “last mile.”
EVIDENCE: `ideas/038/idea_card.json` (`use_vs_association`); Liu et al., Sci Data 2023, DOI 10.1038/s41597-022-01923-0; Volders et al., Sci Rep 2020, PMID 32501132.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial critique

## 1. The intervention does not isolate the claimed variable

The card says that transporting the same joint NCCT/perfusion patch between an interior and a border-zone destination makes a destination-dependent prediction a test of a learned border-distance prior. That conclusion does not follow.

**Verified fact:** the public arterial atlas defines territories in template space from lesion distributions, and vascular territories vary between patients (Liu et al., DOI 10.1038/s41597-022-01923-0, PMID 36739282). A separate digital-border-zone study was motivated specifically by uncertainty in the traditional border location (Phan et al., DOI 10.1159/000214215, PMID 19390177).

**Verified fact:** surrounding perfusion context itself improves voxel-level infarction prediction. Volders et al. compared local perfusion values with cuboid receptive-field information in 144 patients and reported materially higher prediction performance with surrounding context (PMID 32501132).

**Inference:** after a swap, the model can respond to at least four inseparable changes: absolute anatomical coordinate, neighboring tissue/perfusion context, mismatch between transplanted anatomy and its surroundings, and atlas-border distance. Matching cortical depth, tissue class, local vessel density, and four perfusion summaries does not equalize sulcal geometry, white-matter tract layout, multiscale perfusion gradients, receptive-field content, or the learned coordinate implied by skull/ventricle geometry. The parallel-boundary sham controls displacement and interpolation, but it does not control the fact that the border-directed destination is a different anatomical and contextual location.

An edit discriminator and seam checks cannot repair this. Passing them would show only that the chosen detector did not distinguish the edits; it would not establish equality of all features used by the infarct model. Conversely, requiring the transplanted patch and its entire effective receptive field to be identical would leave no independent way to change its anatomical border distance. This is the same structural pattern as the portfolio's repeated `IDENTIFIABILITY_FAILURE`: the claimed mechanism covaries with location and context by construction.

The endpoint is also underspecified. “Continuous probability-mass readout” does not say whether mass is measured inside the transplanted patch, a fixed destination ROI, the whole lesion, or a change relative to an unedited image. Those estimands behave differently when a segmentation model changes boundary probabilities or produces spatial spillover. This is repairable drafting, but it is downstream of the fatal construct problem.

## 2. “Subject-specific competing supply fronts” are not actually measured

**Verified fact:** the ISLES'24 release provides an automatically generated multi-label Circle-of-Willis mask and linearly co-registered acute modalities (Zenodo DOI 10.5281/zenodo.16731717). **Verified fact:** the Liu atlas provides population arterial territories, not patient-specific distal perfusion boundaries.

The card proposes to “refine major-territory seeds” with the CoW mask, but it gives no validated transformation from proximal Circle-of-Willis anatomy to an individual's distal ACA/MCA/PCA competition fronts. Agreement between an atlas-only estimate and a CTA-refined estimate is not validation when both inherit the same atlas boundary. One-voxel registration perturbations quantify numerical stability, not biological validity. Calling the resulting quantity “subject-specific” would therefore be unsupported.

The “last-mile” analogy also slips between two different measurements. Distance to the nearest territory *boundary* is smallest at a border, whereas economic last-mile cost is naturally distance from a supply hub or network path length. The card mentions both boundary distance and CTA centerline distance but never defines a signed direction that makes these equivalent. Near-boundary tissue is not necessarily farthest along a patient-specific vascular route. Thus even a clean border-coordinate effect would not establish that the model prices distal delivery cost or limited redundancy.

## 3. The medical interpretation outruns the experiment

Mangla et al. review heterogeneous border-zone mechanisms (DOI 10.1148/rg.315105014, PMID 21918038); that literature supports border-zone relevance, not a universal scalar reserve determined by atlas distance. The card itself cites Carpenter et al. as a counterexample to selective chronic border-zone hemodynamic impairment (DOI 10.1212/WNL.40.10.1587, PMID 2215951). More proximal clot location also changes perfusion-defect size and salvage (Sillanpää et al., DOI 10.3174/ajnr.A3149, PMID 22723067), illustrating how occlusion topology and treatment response can generate spatial fate differences not captured by four local maps.

Accordingly, “tissue-vulnerability prior,” “fewer pressure and collateral options,” and the proposed clinical generalization to systemic pressure or arterial anatomy are **speculation**, not consequences isolated by this design. A positive swap response would support only destination sensitivity under a synthetic edit. A null would likewise not show that the model “treats fate as local physiology”: the model could use coarse location, occlusion-territory context, or border information at a scale destroyed or obscured by the edit. The stated negative-result value is therefore overstated.

There is no concept-label circularity in the narrow sense—the follow-up infarct mask is not generated from the atlas distance—but there is **measurement circularity** in validating atlas-only and atlas-refined distances that share the same population territory scaffold.

## 4. Executability and cost are not honestly closed

The keystone screen found no public frozen ISLES'24 final-infarct checkpoint in the official repository or winning-solution materials. That is an open access fact, not proof that no checkpoint can be obtained. Still, “after a shared frozen checkpoint” hides the dominant cost. Training and validating a new model on 149 public cases is not part of the claimed two-GPU-hour experiment, and a self-trained model would change “the model” into a newly selected model family whose result may be seed- and recipe-specific.

The card also mixes development and confirmation. “On all public cases” for the support census, followed by “30 untouched cases,” is impossible unless the split is frozen first and the census is restricted to training/development metadata. Eligibility thresholds, atlas variants, discriminator construction, edit parameters, and checkpoint selection all require development cases. With only 149 public cases, the design needs explicit disjoint train, edit-development, and untouched evaluation partitions plus patient-level inference. The proposed 120 forward passes do not represent the preprocessing, matching, atlas-warping, model-training, realism-model training, or sensitivity-analysis burden.

## 5. Prior-work and novelty audit

The exact model-use intervention was not found in the inspected primary neighbors; that is not evidence of novelty. More importantly, the card understates adjacent legwork:

- Volders et al. already tested whether regional CTP context adds voxel-level final-infarct information (PMID 32501132).
- Peerlings et al. used an atlas of downstream regions and CTP spatial layout to infer occlusion location in 596 patients, finding vessel-architecture variation limiting accuracy (PMID 37064186).
- Phan et al. built a probabilistic MCA/PCA border-region atlas expressly because border locations vary (PMID 19390177).
- Liu et al. released the deformable arterial-territory atlas the card would use (PMID 36739282).

These works do not duplicate an audit of a trained ISLES'24 network. They do show that “spatial context matters” and “atlas border zones can be quantified” are established. The precise remaining delta is model reliance on a border-coordinate signal beyond perfusion—not the broader last-mile story. Because the proposed experiment cannot identify that delta, limited novelty confidence is not the reason to proceed.

## 6. Plain-pitch fidelity

The pitch fails fidelity in two places.

First, “Blood supply has a last-mile problem” converts the card's hedged suspected mechanism (“may,” “fewer ... options”) into a fact. Primary sources establish variable border-zone mechanisms, not that distance to a template territory boundary is a patient-level delivery-cost measure.

Second, “moving the same realistic tissue pattern” omits that realism and common support are uninspected gates and that the edit changes destination context. “Even when local blood-flow measurements look the same” is directionally faithful to matching, but it should not imply equivalence of physiology: four derived perfusion maps do not exhaust collateral state, vascular topology, treatment, or tissue context.

## 7. Easier formulation and low-hanging fruit

The genuinely low-hanging-fruit study is model-free: on a frozen patient split, test whether atlas-border distance adds held-out prediction of follow-up infarction beyond acute CBF, CBV, MTT, Tmax, tissue class, cortical depth, hemisphere, and occlusion category. Use patient-clustered evaluation; report incremental log loss/calibration and stratified effects across atlas variants. The released 149-case images, follow-up masks, LVO/CoW products, and public arterial atlas already exist; no new annotation or checkpoint is required.

This would be **association-only**. It cannot establish pressure reserve, subject-specific collateral redundancy, or model use, and treatment/reperfusion variables may leave serious residual confounding. Its value is nevertheless real: it decides whether there is any stable, out-of-sample border-distance signal worth making explicit in later models. A failure to add predictive information is informative and would stop investment in a much harder interpretability experiment. A positive result would justify a separate candidate comparing otherwise identical models trained with and without an explicit, uncertainty-aware border-distance channel. That later comparison would test utility and robustness, not whether an existing implicit model already uses the construct.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does uncertainty-aware arterial-territory border distance add held-out prediction of follow-up infarction beyond acute perfusion maps and prespecified anatomical/occlusion covariates in ISLES'24?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—because it is a checkpoint-free falsification gate for whether a stable border-location signal exists at all, while explicitly stopping short of physiology or model-use claims.


===== ideas/038/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The destination-swap intervention cannot identify use of arterial-border distance because border distance changes only by moving the patch to a different anatomical coordinate and receptive-field context.

**Argument:** The original question is specifically whether a final-infarct model uses arterial-territory border distance beyond local perfusion severity, but the proposed swap jointly changes absolute position, surrounding anatomy, multiscale perfusion context, and patch-to-neighborhood compatibility. Matching CBF, CBV, MTT, Tmax, cortical depth, tissue class, and vessel density, plus a parallel-boundary sham, does not hold those other model-visible variables fixed. This is load-bearing rather than a realism nuisance: Volders et al. found that surrounding CTP context improves voxel-level infarction prediction (PMID 32501132), while the public arterial atlas is population-derived and patient vascular territories vary (Liu et al., DOI 10.1038/s41597-022-01923-0). Therefore, even a gated positive response would establish only destination sensitivity under transplantation, not use of the proposed vascular “last-mile” coordinate. Making the study checkpoint-free and association-only, as suggested in the critique, would be more defensible but would no longer answer the original model-use question; under the identity rule it must be a separate successor candidate, not an amendment to idea 038.

**What would change my mind:** Show an intervention on an obtainable frozen final-infarct model that changes a validated patient-specific arterial-border-distance variable by a prespecified amount while holding the model's entire effective receptive-field input, anatomical coordinate cues, and all non-border spatial features invariant, together with a control proving that any response cannot be reproduced by coordinate or context sensitivity alone.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The destination swap cannot identify use of arterial-border distance because border distance can only be changed by relocating the patch, and relocation necessarily changes anatomical coordinate, surrounding anatomy, multiscale perfusion context, and patch-to-neighborhood compatibility at the same time; matching four local perfusion summaries plus depth, tissue class, and vessel density, and adding a parallel-boundary sham, does not hold those other model-visible variables fixed.

**Response:** CONCEDE

**Argument:** The objection is correct, and it is not repairable within this design. Before conceding I checked the two defenses the card could still mount, and both fail:

1. *Averaging over many matched pairs.* The hope would be that coordinate and context confounds wash out across ≥400 pairs while the border-distance signal accumulates. But the confounding is systematic, not random: border-directed destinations differ from parallel-boundary destinations in correlated, anatomy-typed ways (watershed regions have characteristic depth-of-sulcus geometry, white-matter tract layout, and skull/ventricle-relative position). Aggregation amplifies a systematic bias; it does not cancel it. Volders et al. (PMID 32501132) is direct evidence that the model class has access to exactly this surrounding-context information.

2. *The parallel-boundary sham as a difference-in-differences control.* The sham equalizes displacement magnitude and interpolation, so the contrast (border-directed minus parallel) subtracts edit artifacts. It cannot subtract the destination itself: a border-directed move ends at a systematically different kind of anatomical location than a parallel move of equal length. The residual contrast is "response to border-zone-typed destinations," which is precisely the entanglement of construct and confound the critic names, not a separation of them.

The deeper point, which I accept as constitutive rather than contingent: an image-only model has no border-distance input channel. Border distance is definitionally a function of spatial position given the territory map, so the counterfactual the critic demands — change border distance while holding the entire effective receptive-field input and all coordinate cues invariant — is self-contradictory for this measurement class, not merely expensive. "Use of border distance beyond location and context" is therefore not an identifiable estimand for this design on this data. This is the same failure class that killed ideas 032, 033, 036, and 037 (IDENTIFIABILITY_FAILURE), and the card's own `dies_like_prior` field anticipated dying exactly this way if support was thin; in fact the death is prior to support — no census result could rescue the contrast.

Two subsidiary points for the record. First, the keystone screen independently found no public frozen ISLES'24 final-infarct checkpoint (winning-solution paper has no code/weights statement; official repo has none), an unlisted load-bearing assumption — moot given the concession, but it should accompany the kill record so a revival does not treat the checkpoint as settled. Second, I agree with the critic on the identity rule: the checkpoint-free, association-only formulation from the critique (does uncertainty-aware territory-border distance add held-out prediction of follow-up infarction beyond acute perfusion maps and prespecified anatomical/occlusion covariates?) changes the deliverable sentence from model-use to association and must enter as a successor candidate with parent_ids, not as an amendment.

**Spin-off:** Register as a new candidate (parent: idea-038 / isles24-scout-003-c07): a model-free, patient-clustered incremental-prediction study of atlas-border distance for follow-up infarction on the 149 public ISLES'24 cases, association-only by declaration, valuable as a falsification gate — if border distance adds nothing out of sample, the harder interpretability question is not worth building.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposer’s mechanism-level concession is adequate: Idea 038 should be rejected, and the association-only formulation cannot repair it because it asks a different question.

**Argument:** The proposer supplied the decisive argument rather than merely accepting the verdict: border distance for an image-only model is encoded through spatial position and its anatomical and perfusion context, so changing the proposed construct while holding those model-visible inputs invariant is not an available counterfactual. The further analysis of the parallel-boundary sham is also sufficient: it controls displacement and interpolation but leaves the systematically different destination context in the estimand, while Volders et al. (PMID 32501132) establishes that surrounding CTP context can carry infarct-prediction information. No common-support census, realism discriminator, larger sample, or checkpoint acquisition can resolve that constitutive entanglement. The identity check therefore controls the disposition: the suggested ISLES'24 study of incremental held-out association between atlas-border distance and follow-up infarction drops the original claim that an existing model *uses* a vascular last-mile prior. It may be worth scouting, but only as a new candidate with `parent_ids`; it is not an amendment to Idea 038. The absence of a located public checkpoint should be recorded as an additional unresolved access fact, not confused with the reason for rejection.

**What would change my mind:** A new measurement design that, on an obtainable frozen final-infarct model, independently manipulates a validated arterial-border variable while holding coordinate and receptive-field context fixed—or otherwise supplies a negative control that uniquely excludes coordinate/context sensitivity—would justify reconsidering the original model-use claim; the proposed association-only study would not.

**Status:** CONVERGED


===== ideas/038/idea_card.json =====
{
  "id": "isles24-scout-003-c07",
  "track": "wide",
  "title": "Does the model price the last mile of blood delivery?",
  "question": "[economic geography / facility location] Is an ISLES'24 model using distance to an arterial-territory border\u2014the vascular network's costly last mile\u2014as a vulnerability factor beyond local perfusion severity?",
  "deliverable_sentence": "The final-infarct model is using proximity to an arterial border zone as a tissue-vulnerability prior beyond the measured local perfusion deficit.",
  "cross_field": {
    "borrowed_construct": "The last-mile cost from economic geography: locations farthest from supply hubs are least redundant and most expensive to serve.",
    "measurement_it_implies": "A signed geodesic distance transform to subject-specific competing arterial supply fronts, with uncertainty from atlas and vessel-derived territory estimates.",
    "what_changes_if_dropped": "Without the last-mile construct this becomes generic location bias; the construct supplies the specific prediction that otherwise matched tissue nearer a competing supply boundary receives a different model response."
  },
  "causal_chain": [
    {
      "link": "Arterial border zones are distal from major supply trunks and may have less pressure reserve.",
      "check": "Compare atlas distance with CTA-derived centerline distance and published border-zone patterns."
    },
    {
      "link": "At matched CBF/Tmax, distance to a competing supply front retains variation in final tissue fate.",
      "check": "Held-out conditional analysis, explicitly association-only."
    },
    {
      "link": "The model uses that spatial prior.",
      "check": "Transport the same empirical multimodal tissue patch between matched interior and border-zone destinations while preserving local anatomy and perfusion statistics."
    }
  ],
  "X_measurement": "Warp a public arterial-territory atlas to NCCT, refine major-territory seeds with the released CTA vessel mask when valid, and calculate millimeter geodesic distance to the nearest boundary between anterior, middle, and posterior cerebral arterial territories. Repeat across atlas variants and one-voxel registration perturbations; X is the median signed distance and its uncertainty. Border-zone anatomy and mechanisms are established in DOI 10.1148/rg.315105014 (PMID 21918038).",
  "suspected_signal": "Two voxels with the same measured hypoperfusion may not have equal reserve: tissue at a distal supply frontier has fewer pressure and collateral options than tissue closer to a dominant arterial trunk.",
  "use_vs_association": "Use matched real-tissue patch substitution: exchange a small joint NCCT/perfusion signature between same-tissue, same-hemisphere locations matched on CBF, CBV, MTT, Tmax, cortical depth, and local vessel density but differing in border distance; compare against equally distant moves parallel to the boundary. A destination-dependent response tests a learned spatial prior rather than correlation of natural border-zone lesions with severity.",
  "keystone_prerequisite": "Enough held-out tissue pairs exist with overlapping anatomy and perfusion support but materially different, registration-stable border distance; substituted patches pass local continuity and real-versus-edited discriminator gates.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_residual_assumption": "Canonical arterial territories vary between people, and the released Circle-of-Willis masks have not been fidelity-audited. The candidate therefore cannot treat atlas distance as subject-specific truth; agreement across atlas-only and vessel-refined estimates is a gate.",
  "dies_like_prior": "It risks idea-009's IDENTIFIABILITY_FAILURE because border distance covaries with anatomy, occlusion site, and severity. The paired destination swap and parallel-boundary sham attempt to isolate location, but if common support is thin the card dies. It differs from the earlier percolation candidate, which changes deficit connectivity, and from the Circle-of-Willis candidate, which changes proximal graph redundancy.",
  "closest_prior_work": "Mangla et al. review border-zone infarct mechanisms (PMID 21918038); Carpenter et al. found no selective chronic border-zone impairment in a PET cohort (PMID 2215951), an important counterexample; a recent CTP probability model predicts final core without auditing spatial priors (PMID 41583397).",
  "novelty_neighbors": [
    "Mangla R et al., Radiographics 2011, DOI 10.1148/rg.315105014, PMID 21918038 \u2014 border-zone imaging and pathophysiology.",
    "Carpenter DA et al., Neurology 1990, DOI 10.1212/WNL.40.10.1587, PMID 2215951 \u2014 PET study finding no selective chronic border-zone hemodynamic impairment.",
    "Deep Learning-Based Prediction of Final Infarct Core from CT Perfusion Data, PMID 41583397 \u2014 probabilistic CTP outcome model without a reported border-distance use test."
  ],
  "novelty_delta": "Clinical work studies whether border zones infarct; the proposed experiment asks whether a final-infarct network applies a border-distance prior to otherwise matched tissue and directly tests that use with destination swaps.",
  "why_not_done": "BLIND_SPOT: stroke prediction work usually represents location implicitly through convolutional coordinates, while perfusion research stratifies named infarct patterns; neither tradition treats learned vascular distance as an auditable model input.",
  "novelty_search_verdict": "NO_DUPLICATE_FOUND_LIMITED_SEARCH",
  "existing_assets": "Registered multimodal images, public territory atlases, CTA and perfusion maps, 149 training cases, and standard registration/distance-transform tools.",
  "smallest_decisive_experiment": "On all public cases, perform a CPU common-support census and require at least 400 eligible patch pairs from at least 30 untouched cases, with median border-distance separation >=15 mm and standardized differences <0.1 for the four maps, cortical depth, tissue class, and vessel density. Then evaluate 30 cases x 4 paired swaps/shams with continuous probability-mass readout.",
  "compute_envelope": "One Colab GPU session after a shared frozen checkpoint: atlas warping and matching are CPU preprocessing; about 120 edited forward passes fit under 2 GPU-hours and 16 GB VRAM.",
  "standing_confounds_addressed": "Within-case swaps fix patient, scanner, center, treatment, and global severity; exact covariate matching addresses local perfusion/anatomy; parallel-boundary moves control displacement and interpolation. Territory uncertainty is propagated across atlas variants. Synthetic seams and unmeasured microvascular anatomy remain threats.",
  "alternative_explanations": [
    "The model uses cortical depth: explicitly matched and independently shifted in a control arm.",
    "The model reacts to interpolation: parallel-boundary swaps have the same displacement and interpolation.",
    "The atlas is wrong for the patient: require consistent sign across atlas-only and CTA-refined distance estimates."
  ],
  "anticipated_negative": "If support, atlas-stability, edit-realism, and a local-perfusion positive control pass, a null is useful: this model treats fate as local physiology rather than pricing vascular location. Failure of common support is not a negative result; it is an identifiability kill.",
  "verified_dataset_facts": "Relies on the cycle's primary-source verification: public acute CTA and registered perfusion maps for 149 cases, post-treatment follow-up infarct masks, and stated automated vessel/Circle-of-Willis products whose fidelity remains unresolved (DOI 10.5281/zenodo.16731717; DOI 10.1148/ryai.250603; official repository).",
  "design_template": "regional-substitution",
  "scores": {
    "clarity": {
      "value": 4,
      "why": "Border distance and the destination-swap contrast are explicit; subject-specific territory definition remains conditional."
    },
    "identifiability": {
      "value": 3,
      "why": "Strong matching and shams help, but anatomy and territory uncertainty may leave no valid common support."
    },
    "medical_relevance": {
      "value": 4,
      "why": "A hidden location prior could fail when arterial anatomy or systemic pressure differs from training data."
    },
    "interest": {
      "value": 5,
      "why": "The claim that a model prices the vascular last mile is surprising and clinically legible."
    },
    "prior_legwork": {
      "value": 3,
      "why": "Border-zone science and atlases exist; the matched intervention has not been built."
    },
    "feasibility": {
      "value": 3,
      "why": "Capped by uninspected common support and territory fidelity."
    },
    "data_readiness": {
      "value": 3,
      "why": "Public registered data exist, but vessel-mask fidelity is unresolved."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "Paired output change is direct; support and edit gates are custom."
    },
    "negative_result_value": {
      "value": 3,
      "why": "A gated null discriminates spatial-prior from local-physiology behavior."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Three close primary neighbors were checked; the model-audit search was limited."
    },
    "regret": {
      "value": 4,
      "why": "Spatial priors are easy for segmentation networks to learn and almost never reported."
    }
  },
  "priority_score": 3.45,
  "unverified_claims": [
    "adequate matched patch support",
    "stable subject-level border distance",
    "CTA-derived territory refinement is valid",
    "patch substitutions are in distribution",
    "exact novelty"
  ],
  "plain_pitch": "Blood supply has a last-mile problem: tissue near the boundary between two arterial territories may be harder to serve than tissue closer to a main route. This study asks whether the model quietly charges that location a higher risk even when local blood-flow measurements look the same. If true, moving the same realistic tissue pattern to a border location would change the prediction more than moving it the same distance along the border.",
  "charter": "isles24"
}


===== ideas/038/keystone_screen.md =====
# Keystone screen — idea 038 (isles24-scout-003-c07)

Screen date: 2026-08-18. Charter: isles24.

## Keystone as stated on the card

> "Enough held-out tissue pairs exist with overlapping anatomy and perfusion
> support but materially different, registration-stable border distance;
> substituted patches pass local continuity and real-versus-edited
> discriminator gates."

## Decomposition: what is checkable at screen prices

The stated keystone is an **empirical census claim**: whether ≥400 eligible
matched patch pairs from ≥30 cases exist, and whether edited patches pass
realism gates. No primary source can answer that; it is decidable only by
running the card's own smallest decisive experiment (the CPU common-support
census, which the card itself designates as the Stage-0 gate). What CAN be
verified against primary sources are the enabling facts the census silently
depends on:

1. The public ISLES'24 release contains co-registered NCCT, CTA, perfusion
   maps (CBF/CBV/MTT/Tmax), and follow-up-derived infarct masks for ~149
   cases (needed for within-case matched swaps in one space).
2. Released CTA-derived vessel / Circle-of-Willis products exist (needed for
   the atlas-vs-vessel-refined distance agreement gate).
3. A public deformable arterial-territory atlas with anterior/middle/
   posterior territory boundaries exists (needed to define X at all).
4. A trained final-infarct model exists to probe (needed for any forward
   pass; see wrong-keystone check).

## Inspections

### 1. ISLES'24 data release — VERIFIED TRUE

Source: Zenodo record https://zenodo.org/records/16731717 (the DOI the card
cites, 10.5281/zenodo.16731717). The record states the training set
comprises "149 acute ischemic stroke cases" with admission imaging
"non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time
series, and perfusion maps (Tmax, CBF, CBV, MTT)". The load-bearing
registration fact — the derivatives folder contains

> "all modalities linearly co-registered to the NCCT space"

while raw data are "released in their original space, just defaced".
Annotations include

> "binary infarct masks derived from follow-up MRI (lesion-msk.nii.gz),
> large vessel occlusion binary masks derived from CTA (lvo-msk.nii.gz),
> and the multi-labeled Circle of Willis anatomy generated with an
> automatic algorithm over CTA (cow-msk.nii.gz)."

This confirms enabling facts 1 and 2, including the card's premise that the
CoW product is automatic (fidelity unaudited — the card already carries this
as `keystone_residual_assumption`). Note the registration is stated as
**linear**; residual local misregistration is possible, which is exactly
what the card's one-voxel perturbation repeats are for. Consistent facts in
the dataset paper (arXiv 2408.11142): "This multicenter dataset consists of
245 cases" total, with "vessel occlusion masks from acute CT angiography and
delineated infarction masks in follow-up MRI" — so 149 public training cases
of 245, remainder hidden test; the card's "all public cases" framing is
consistent.

### 2. Arterial-territory atlas — VERIFIED TRUE

Source: NITRC project page https://www.nitrc.org/projects/arterialatlas
(the release repository of Liu et al., Sci Data 2023, DOI
10.1038/s41597-022-01923-0, PMID 36739282). The project description states:

> "The atlas covers supra- and infra-tentorial regions and contains
> hierarchical segmentation levels created by a fusion of vascular and
> classical anatomical criteria."

Download packages are listed for immediate download (ArterialAtlas.zip,
Atlas_MNI152.zip, Vascular_Probabilistic_Maps.nii) under an Attribution
license. The publication (per its own description and the GitHub mirror
github.com/Chin-Fu-Liu/Arterial_Atlas) defines the four major territories —
Anterior, Middle, Posterior Cerebral Arteries and Vertebro-Basilar — in MNI
space, NIfTI format. This is sufficient for the card's ACA/MCA/PCA boundary
distance measure, and the probabilistic maps support the card's
atlas-uncertainty propagation.

### 3. Model to probe — NOT FOUND PUBLICLY (absence, not proof of absence)

The card's experiment requires forward passes through "the final-infarct
model" and budgets compute "after a shared frozen checkpoint". Inspected:

- The winning-solution paper (arXiv 2505.18424, "How We Won the ISLES'24
  Challenge by Preprocessing", full HTML fetched): describes preprocessing —
  "First, we applied SynthStrip on the non-contrast CT (NCCT) scans to
  obtain a brain masks. Then, we applied this brain mask to the other
  co-registered scans (CTP, CTA, etc.)" — and "the 'large' 3D residual
  encoder nnU-Net", but contains **no code-availability statement, no
  repository URL, and no weights release** anywhere in the fetched text.
- The official challenge repository (https://github.com/ezequieldlrosa/isles24)
  contains a data-loading notebook and evaluation utilities only; no
  baseline or participant checkpoints are documented.

Per rules, "I did not find it" is not proof it does not exist (participant
containers may be obtainable via grand-challenge.org or author
correspondence, and the program may train its own nnU-Net on the public
split). But as of this screen, no public frozen ISLES'24 final-infarct
checkpoint was located.

## Wrong-keystone check (mandatory follow-up)

If this card only verified the nearest checkable thing (data + atlas exist),
it is still assuming two things:

1. **The common-support census passes.** The card is honest about this: it
   is the stated keystone, it is `NOT_INSPECTED`, and the card's own
   smallest decisive experiment is the census with a declared kill
   condition ("Failure of common support is not a negative result; it is an
   identifiability kill"). Nothing at screen prices can settle it.
2. **A frozen final-infarct checkpoint is obtainable.** This is the
   assumption the stated keystone does NOT cover and the card's
   `unverified_claims` list omits. My inspection found no released winner
   weights and none in the official repo. This same dependency is already a
   known program-wide feasibility question (ideas 021/023 were forwarded to
   feasibility with model-verification conditions), so it is not unique to
   this card — but it is load-bearing here and must be carried forward
   explicitly: if no checkpoint can be obtained or trained, the swap
   experiment has nothing to probe.

Neither assumption is demonstrably false, so no KILL is available. The
first is the census; the second is an access question with live paths
(grand-challenge containers, self-training nnU-Net on the 149 public
cases). Both are recorded for critique/feasibility.

## Verdict

Every screen-checkable enabling fact is verified TRUE with quoted primary
sources: co-registered multimodal maps and masks for 149 public cases,
released automatic CoW/LVO products, and a public deformable arterial
atlas with the required territory boundaries. The stated keystone itself
(pair support + edit-realism gates) is an empirical Stage-0 census that no
primary source can decide, and the unlisted checkpoint assumption is open.
Honest verdict: UNVERIFIABLE, passed onward with both residuals recorded.

```json
{"verdict": "UNVERIFIABLE", "evidence": "all modalities linearly co-registered to the NCCT space", "source": "https://zenodo.org/records/16731717 (ISLES'24 training release, Derivatives folder description)", "note": "All checkable enabling facts verified true (149-case co-registered release, CoW/LVO masks, public NITRC arterial atlas); the stated keystone is a Stage-0 census only the experiment can answer, and the card additionally assumes an obtainable frozen final-infarct checkpoint, which was not found publicly."}
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

**Position:** The destination-swap intervention cannot identify use of arterial-border distance because border distance changes only by moving the patch to a different anatomical coordinate and receptive-field context.

**Argument:** The original question is specifically whether a final-infarct model uses arterial-territory border distance beyond local perfusion severity, but the proposed swap jointly changes absolute position, surrounding anatomy, multiscale perfusion context, and patch-to-neighborhood compatibility. Matching CBF, CBV, MTT, Tmax, cortical depth, tissue class, and vessel density, plus a parallel-boundary sham, does not hold those other model-visible variables fixed. This is load-bearing rather than a realism nuisance: Volders et al. found that surrounding CTP context improves voxel-level infarction prediction (PMID 32501132), while the public arterial atlas is population-derived and patient vascular territories vary (Liu et al., DOI 10.1038/s41597-022-01923-0). Therefore, even a gated positive response would establish only destination sensitivity under transplantation, not use of the proposed vascular “last-mile” coordinate. Making the study checkpoint-free and association-only, as suggested in the critique, would be more defensible but would no longer answer the original model-use question; under the identity rule it must be a separate successor candidate, not an amendment to idea 038.

**What would change my mind:** Show an intervention on an obtainable frozen final-infarct model that changes a validated patient-specific arterial-border-distance variable by a prespecified amount while holding the model's entire effective receptive-field input, anatomical coordinate cues, and all non-border spatial features invariant, together with a control proving that any response cannot be reproduced by coordinate or context sensitivity alone.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The destination swap cannot identify use of arterial-border distance because border distance can only be changed by relocating the patch, and relocation necessarily changes anatomical coordinate, surrounding anatomy, multiscale perfusion context, and patch-to-neighborhood compatibility at the same time; matching four local perfusion summaries plus depth, tissue class, and vessel density, and adding a parallel-boundary sham, does not hold those other model-visible variables fixed.

**Response:** CONCEDE

**Argument:** The objection is correct, and it is not repairable within this design. Before conceding I checked the two defenses the card could still mount, and both fail:

1. *Averaging over many matched pairs.* The hope would be that coordinate and context confounds wash out across ≥400 pairs while the border-distance signal accumulates. But the confounding is systematic, not random: border-directed destinations differ from parallel-boundary destinations in correlated, anatomy-typed ways (watershed regions have characteristic depth-of-sulcus geometry, white-matter tract layout, and skull/ventricle-relative position). Aggregation amplifies a systematic bias; it does not cancel it. Volders et al. (PMID 32501132) is direct evidence that the model class has access to exactly this surrounding-context information.

2. *The parallel-boundary sham as a difference-in-differences control.* The sham equalizes displacement magnitude and interpolation, so the contrast (border-directed minus parallel) subtracts edit artifacts. It cannot subtract the destination itself: a border-directed move ends at a systematically different kind of anatomical location than a parallel move of equal length. The residual contrast is "response to border-zone-typed destinations," which is precisely the entanglement of construct and confound the critic names, not a separation of them.

The deeper point, which I accept as constitutive rather than contingent: an image-only model has no border-distance input channel. Border distance is definitionally a function of spatial position given the territory map, so the counterfactual the critic demands — change border distance while holding the entire effective receptive-field input and all coordinate cues invariant — is self-contradictory for this measurement class, not merely expensive. "Use of border distance beyond location and context" is therefore not an identifiable estimand for this design on this data. This is the same failure class that killed ideas 032, 033, 036, and 037 (IDENTIFIABILITY_FAILURE), and the card's own `dies_like_prior` field anticipated dying exactly this way if support was thin; in fact the death is prior to support — no census result could rescue the contrast.

Two subsidiary points for the record. First, the keystone screen independently found no public frozen ISLES'24 final-infarct checkpoint (winning-solution paper has no code/weights statement; official repo has none), an unlisted load-bearing assumption — moot given the concession, but it should accompany the kill record so a revival does not treat the checkpoint as settled. Second, I agree with the critic on the identity rule: the checkpoint-free, association-only formulation from the critique (does uncertainty-aware territory-border distance add held-out prediction of follow-up infarction beyond acute perfusion maps and prespecified anatomical/occlusion covariates?) changes the deliverable sentence from model-use to association and must enter as a successor candidate with parent_ids, not as an amendment.

**Spin-off:** Register as a new candidate (parent: idea-038 / isles24-scout-003-c07): a model-free, patient-clustered incremental-prediction study of atlas-border distance for follow-up infarction on the 149 public ISLES'24 cases, association-only by declaration, valuable as a falsification gate — if border distance adds nothing out of sample, the harder interpretability question is not worth building.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposer’s mechanism-level concession is adequate: Idea 038 should be rejected, and the association-only formulation cannot repair it because it asks a different question.

**Argument:** The proposer supplied the decisive argument rather than merely accepting the verdict: border distance for an image-only model is encoded through spatial position and its anatomical and perfusion context, so changing the proposed construct while holding those model-visible inputs invariant is not an available counterfactual. The further analysis of the parallel-boundary sham is also sufficient: it controls displacement and interpolation but leaves the systematically different destination context in the estimand, while Volders et al. (PMID 32501132) establishes that surrounding CTP context can carry infarct-prediction information. No common-support census, realism discriminator, larger sample, or checkpoint acquisition can resolve that constitutive entanglement. The identity check therefore controls the disposition: the suggested ISLES'24 study of incremental held-out association between atlas-border distance and follow-up infarction drops the original claim that an existing model *uses* a vascular last-mile prior. It may be worth scouting, but only as a new candidate with `parent_ids`; it is not an amendment to Idea 038. The absence of a located public checkpoint should be recorded as an additional unresolved access fact, not confused with the reason for rejection.

**What would change my mind:** A new measurement design that, on an obtainable frozen final-infarct model, independently manipulates a validated arterial-border variable while holding coordinate and receptive-field context fixed—or otherwise supplies a negative control that uniquely excludes coordinate/context sensitivity—would justify reconsidering the original model-use claim; the proposed association-only study would not.

**Status:** CONVERGED

