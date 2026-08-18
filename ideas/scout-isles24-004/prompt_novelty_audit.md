You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-isles24-004
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

39 tracked ideas in this charter. Latest state per idea; full history in ledger.jsonl.

Work under other charters: evidence/cross_charter_index.md (facts, no scores).

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **IDENTIFIABILITY_FAILURE** x1: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_ACCESS** x1: Required data, checkpoints, or mappings are not obtainable in practice.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **isles24-scout-003-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.2, audited 2026-08-18] -- When vanished sulci mean rescue, not death
- **isles24-scout-003-c04** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.2, audited 2026-08-18] -- The blood's grayscale oxygen gauge
- **isles24-scout-001-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.7, audited 2026-08-16] -- The vascular detour the segmentation model can see
- **isles24-scout-003-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.6, audited 2026-08-18] -- The arterial network's spare route
- **isles24-scout-003-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.6, audited 2026-08-18] -- Did preprocessing teach the winner to read the disappearing insular ribbon?
- **isles24-scout-003-c08** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.5, audited 2026-08-18] -- The skull is a fixed-volume pressure vessel
- **isles24-scout-003-c07** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.5, audited 2026-08-18] -- Does the model price the last mile of blood delivery?
- **isles24-scout-002-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.4, audited 2026-08-16] -- Two tissues, two death thresholds
- **isles24-scout-002-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.2, audited 2026-08-16] -- The clot that lets contrast through
- **isles24-scout-002-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.0, audited 2026-08-16] -- The barrier is already leaking
- ... and 16 more (python scout.py backlog)

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
- **isles24-scout-001-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Does the winning model rediscover the collateral clock?
- **isles24-scout-001-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The vascular detour the segmentation model can see
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
- **isles24-scout-003-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The arterial network's spare route
- **isles24-scout-003-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The blood's grayscale oxygen gauge
- **isles24-scout-003-c05** [SCOUT_ONLY/SCOUTED/baseline] -- When vanished sulci mean rescue, not death
- **isles24-scout-003-c06** [SCOUT_ONLY/SCOUTED/wide] -- The bolus spreads like dye in a river
- **isles24-scout-003-c07** [SCOUT_ONLY/SCOUTED/wide] -- Does the model price the last mile of blood delivery?
- **isles24-scout-003-c08** [SCOUT_ONLY/SCOUTED/wide] -- The skull is a fixed-volume pressure vessel
- **isles24-scout-004-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The ground truth remembers the algorithm that drafted it
- **isles24-scout-004-c02** [SCOUT_ONLY/SCOUTED/baseline] -- Does the model bring a vascular map to the scan?
- **isles24-scout-004-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The heart's signature in the head scan
- **isles24-scout-004-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The model may be watching the patient's eyes
- **isles24-scout-004-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The brain's odometer: calcification as the model's age gauge
- **isles24-scout-004-c06** [SCOUT_ONLY/SCOUTED/wide] -- The scan remembers which hospital took it
- **isles24-scout-004-c07** [SCOUT_ONLY/SCOUTED/wide] -- The edge of the map: the benchmark scores terra incognita
- **isles24-scout-004-c08** [SCOUT_ONLY/SCOUTED/wide] -- The ground truth was drawn on a swollen brain


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


===== ideas/scout-isles24-004/README.md =====
# Scouting cycle isles24-004

Tracks: baseline, wide
Charter: isles24 (charters/isles24/CHARTER.md; scores are scoped to this charter and not comparable across charters)


===== ideas/scout-isles24-004/candidates_all.json =====
{
  "cycle": 4,
  "charter": "isles24",
  "tracks": [
    "baseline",
    "wide"
  ],
  "notes": {
    "search_mode_missing": 3
  },
  "candidates": [
    {
      "id": "isles24-scout-004-c01",
      "parent_ids": [],
      "search_mode": "A",
      "entry_point": 2,
      "title": "The ground truth remembers the algorithm that drafted it",
      "question": "Is an ISLES'24-trained final-infarct model using the boundary conventions that the DeepISLES draft left in the 'corrected when needed' ground truth, rather than tissue-fate evidence alone?",
      "rung": "Target rung 1: models reproduce draft-specific conventions in expert-overridden voxels; rung 2 requires replication across at least two trained model families and both centers.",
      "deliverable_sentence": "The final-infarct model is using the ground truth's algorithmic fingerprint — DeepISLES boundary conventions inherited through the 'corrected when needed' annotation pipeline — in the voxels where experts overrode the draft.",
      "X_measurement": "Rerun released DeepISLES (Docker isleschallenge/deepisles, weights Zenodo version 14026715) on each case's released follow-up DWI/ADC to obtain draft mask D; X is the draft-versus-released-GT disagreement field D xor G plus draft-agreement statistics (per-case Dice(D,G), bitwise-identical fraction, boundary surface distance). Compute-today test: YES — X is computed from released follow-up images by a public containerized tool, no annotator; note X lives on the follow-up image, while the audited model consumes only acute CT.",
      "suspected_signal": "Not a biological signal but a documented process one: masks were initialized by a public ensemble and corrected only 'when needed', so the released labels carry the initializer's systematic conventions (boundary smoothness, small-lesion suppression or inclusion habits); a model trained on those labels can inherit exactly those conventions, and the benchmark then partially rewards fidelity to the draft algorithm.",
      "use_vs_association": "Stage 1 is model-free description. Stage 2 separates use from association by restricting to disagreement voxels, where the training-label signal G and the draft convention D point in opposite directions: a model merely fitting its labels should side with G on held-out cases; systematic siding with D against evidence-matched baselines indicates inherited conventions. An external stroke model never trained on ISLES'24 labels serves as the shared-inductive-bias control.",
      "keystone_prerequisite": "The correction field is recoverable: the initializing segmenter is public and re-runnable on released follow-up MRI, so draft-versus-final disagreement can be computed per case.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "arXiv 2408.10966v1 (inspected 2026-08-18): 'Lesion masks are derived from DWI images using the ISLES'22 ensemble algorithm. Quality control and correction of the lesion masks are performed when needed by medical students (TAB, HPM) supervised by two neuroradiologists (JSK, BW) with more than 10 years of experience.' github.com/ezequieldlrosa/DeepISLES (inspected): the ISLES'22 ensemble is released with Docker image isleschallenge/deepisles and Zenodo weights (version 14026715); required inputs DWI (b=1000) and ADC, FLAIR 'Required for ensemble (optional for single algorithm outputs)'. zenodo.org/records/16731717 (inspected): each training case includes follow-up 'post-treatment MRI (DWI and ADC)'; 149 cases public.",
      "keystone_residual_assumption": "That the released DeepISLES version approximates the draft actually used: the initializing version/weights are not stated anywhere inspected, and if organizers ran the FLAIR-using ensemble, a DWI/ADC-only rerun differs. High verbatim agreement is version-robust evidence of imprint; LOW agreement is ambiguous between heavy correction and version drift — this asymmetry is prespecified in the analysis, and the weights-release date versus dataset-creation chronology is a stage-0 check.",
      "rung_reached": "0; rung 1 after stage-2 disagreement-voxel analysis with the external-model control; rung 2 after two-family, two-center replication.",
      "dies_like_prior": "Closest to ideas 002 and 005 (annotation provenance undocumented). It differs decisively: here provenance IS documented in the challenge paper, the initializer is a released artifact, and the provenance effect is the measurand rather than an unverifiable assumption. What it cannot do is separate expert anchoring on the draft from genuine agreement with it — stated as a limit, not assumed away.",
      "closest_prior_work": "Label-error and annotation-style work (Zhang et al., Disentangling human error from ground truth, NeurIPS 2020, arXiv 2007.15963; annotation-style effects, arXiv 2210.17398) models rater noise but does not measure AI-initialized draft imprint in a public benchmark. The DeepISLES paper (Nature Communications 2025) validates the segmenter, not its imprint on ISLES'24 ground truth. No located work runs this audit on ISLES'24; novelty confidence remains limited-search.",
      "existing_assets": "All required artifacts are public: 149 cases with follow-up DWI/ADC and GT masks (Zenodo 16731717), DeepISLES container plus weights, nnU-Net training recipes, official evaluation code (utils/eval_utils).",
      "smallest_decisive_experiment": "Stage 1 alone is decisive as a dataset-quality finding: run DeepISLES on all 149 released follow-up DWI/ADC, compute Dice(D,G), bitwise-identical fraction, and boundary distances, stratified by center; prespecify a report of the uncorrected fraction. About 2-3 days including download, under 10 GPU-hours. Stage 2 (train one nnU-Net, analyze held-out disagreement voxels with the external-model control) adds about two weeks.",
      "standing_confounds_addressed": "Scanner/site enter D-G agreement through MRI quality — stratified by center. Genuine boundary ambiguity (both draft and expert defensible) is quantified with a boundary-band analysis. The design does not rule out expert anchoring on the draft (automation bias), which would make even 'corrected' voxels draft-tinted — acknowledged as an unremovable ceiling on interpretation. Label leakage is inverted here: labels are the object of study, and the stage-1 readout needs no trusted labels at all.",
      "alternative_explanations": [
        "Models side with the draft because CNNs share inductive biases with DeepISLES, not because of label inheritance — the external never-trained-on-ISLES'24 model control discriminates this.",
        "Low draft-GT agreement reflects DeepISLES version drift rather than extensive correction — prespecified asymmetric interpretation and chronology check.",
        "Disagreement voxels are simply hard voxels — evidence-matched baselines within the same case address this."
      ],
      "anticipated_negative": "Decisive for stage 1: any measured uncorrected fraction is a benchmark fact of record either way. For stage 2, a null after the external-model control passes is a valuable reassurance that the hybrid annotation pipeline did not measurably contaminate model behavior on this benchmark.",
      "cross_domain": {
        "borrowed_construct": "Automation bias/anchoring from human-factors research: reviewers correct machine drafts less than they should.",
        "measurement_it_implies": "The surviving-draft fraction and draft-siding rate in overridden voxels as anchoring indices.",
        "what_changes_if_dropped": "Nothing mechanical — the study remains a label-provenance audit; the human-factors frame only supplies the interpretation of high uncorrected fractions."
      },
      "remaining_legwork": "Archive download and DeepISLES container runs: 2-3 days to the stage-1 decision; one nnU-Net training plus disagreement analysis: about two weeks to the stage-2 decision.",
      "design_template": "cross-model-disagreement",
      "entry_point_2_requirements": "Measurement: draft-agreement statistics and draft-siding rate in expert-overridden voxels. Confused artifact: shared CNN inductive bias producing draft-like outputs without label inheritance; controlled by the external-model comparison and evidence-matched baselines.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "Two prespecified stages, each with an explicit quantitative readout and a named control."
        },
        "identifiability": {
          "value": 3,
          "why": "Stage 1 is descriptive and clean; stage 2's inheritance claim survives the external-model control but cannot exclude expert anchoring, which is stated as a ceiling."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Every model ranked on ISLES'24 inherits this ground truth; deployment claims trained on it inherit whatever imprint exists."
        },
        "interest": {
          "value": 5,
          "why": "Either answer is consequential for the whole challenge community: substantial algorithmic ground truth, or a documented reassurance that the hybrid pipeline is sound."
        },
        "prior_legwork": {
          "value": 5,
          "why": "Initializer, weights, follow-up images, masks, and evaluation code are all released; nothing must be built except analysis."
        },
        "feasibility": {
          "value": 4,
          "why": "Keystone inspected true; stage 1 is days of container inference on public data."
        },
        "data_readiness": {
          "value": 4,
          "why": "Fully public under CC BY-NC-SA; the archive is large but hosted on Zenodo."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Agreement metrics are standard; imprint and draft-siding statistics are custom and need preregistration."
        },
        "negative_result_value": {
          "value": 4,
          "why": "A low uncorrected fraction plus a stage-2 null is a citable benchmark-integrity result, not a dead end."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Targeted search found adjacent label-noise literature but no ISLES'24 audit; search was not exhaustive."
        },
        "regret": {
          "value": 5,
          "why": "The audit is cheap, uses only released artifacts, and the community will eventually ask this question of any hybrid-annotated benchmark."
        }
      },
      "priority_score": 4.1,
      "unverified_claims": [
        "the DeepISLES version used for initialization matches the released weights",
        "the fraction of uncorrected masks is large enough to matter",
        "an adequate external stroke model exists for the shared-bias control",
        "novelty beyond targeted search"
      ],
      "plain_pitch": "The 'correct answers' in this stroke benchmark were first drawn by an algorithm and only fixed by humans when someone judged it necessary. Because that drafting algorithm is public, we can redraw every answer and measure exactly how much of the official truth is uncorrected machine output — and then test whether models trained on it learn the drafting algorithm's habits instead of the biology. Either result matters: a large imprint would change how the benchmark's rankings are read, and a small one would be documented reassurance.",
      "track": "baseline",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-004-c02",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "Does the model bring a vascular map to the scan?",
      "question": "Is an ISLES'24 final-infarct model using arterial-territory membership — the brain's vascular map — as a spatial prior beyond the case's own perfusion and tissue evidence?",
      "rung": "Target rung 1: use of atlas-defined territory membership; rung 2 requires replication in a second model family and demonstration on anatomically variant cases where prior and evidence dissociate.",
      "deliverable_sentence": "The final-infarct model is using arterial-territory membership — the brain's vascular map — as a spatial prior, producing prediction discontinuities at territory borders between voxels with matched local evidence.",
      "X_measurement": "Register the public digital arterial-territories atlas (Liu et al., Scientific Data 2023, DOI 10.1038/s41597-022-01923-0; github.com/Chin-Fu-Liu/Arterial_Atlas) to each NCCT with standard deformable registration; X is territory membership and signed distance to the territory border per voxel. Compute-today test: YES on any unseen head CT with public atlas and registration tools; no annotator.",
      "suspected_signal": "Emboli follow arterial trees, so real infarcts are territorial; a segmentation network trained on territorial masks can internalize the territory shapes themselves and apply them as a prior. Physicians reason territorially and would want to know whether the model does too — helpful as anatomical plausibility, harmful if the prior overrides case evidence in patients with variant vascular anatomy.",
      "use_vs_association": "Association predicts model output varies smoothly with local hemodynamic evidence; use of a map predicts a jump located exactly at an externally registered anatomical boundary between voxels matched on all released evidence channels. Placebo boundaries (shifted 5-10 mm), contralateral boundaries, and matching on Tmax/CBF/CBV/MTT/NCCT-HU/distance-to-core carry the distinction.",
      "keystone_prerequisite": "A frozen trained final-infarct model with continuous per-voxel output and non-trivial held-out performance exists, and atlas-to-CT registration is accurate to a few millimeters so border-straddling matched pairs are real.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The verified nearby fact is that the atlas is public and covers territories hierarchically; the load-bearing facts — reproduced-model quality and registration accuracy on defaced stroke CT — are the actual stage-0 gates. Matching can only use released evidence channels; unreleased raw-CTP cues correlated with true borderzone physiology remain possible and cap the identifiability score.",
      "rung_reached": "0; rung 1 after the discontinuity analysis with placebo and registration-perturbation gates; rung 2 after a second model family and variant-anatomy cases.",
      "dies_like_prior": "Nearest killed relative is idea-020 (spreading front, IDENTIFIABILITY_FAILURE). Differences: no synthetic intervention is required, the readout is a boundary discontinuity with built-in placebo cutoffs and contralateral controls, and the dominant confound (genuine watershed hemodynamics) is explicitly handled by matching on every released hemodynamic channel plus a prespecified sensitivity band; if matching quality fails its own gate, the result is reported as unidentifiable rather than reinterpreted.",
      "closest_prior_work": "The atlas itself (DOI 10.1038/s41597-022-01923-0) and deliberate atlas-prior segmentation methods exist; Robben et al. (Medical Image Analysis 2020, DOI 10.1016/j.media.2019.101589) predict final infarct from native CTP without auditing spatial priors. No located work tests for emergent territorial priors in stroke models via boundary discontinuity; novelty is unaudited beyond targeted search.",
      "existing_assets": "Public atlas with hierarchical territories, 149 public multimodal cases, registration toolchains (ANTs), nnU-Net recipes, and a label-free readout requiring only model probability maps.",
      "smallest_decisive_experiment": "On 30 held-out cases of one trained nnU-Net: extract about 10^4 border-straddling voxel pairs matched on the five released evidence channels plus distance-to-core; estimate the output discontinuity with patient-clustered bootstrap CIs; compare against 20 placebo borders per case and contralateral borders; registration-perturbation sensitivity analysis. Decision in 3-4 days after model training; under 5 GPU-hours of inference.",
      "standing_confounds_addressed": "Within-case matched pairs fix scanner, vendor, protocol, site, positioning, habitus, prevalence, and referral. Registration error blurs true jumps (conservative for a positive claim, threatening for a null — handled by the perturbation gate). NOT ruled out: model access to unreleased or raw-image correlates of true borderzone physiology at the border; this is the candidate's honest identifiability ceiling. Labels never enter the primary readout.",
      "alternative_explanations": [
        "Genuine watershed hemodynamics differ at borders in ways the released maps do not fully capture — the main residual, stated and scored.",
        "Registration is systematically biased at borders — perturbation and contralateral analyses bound this.",
        "The model produces edges everywhere — placebo borders quantify generic edge behavior."
      ],
      "anticipated_negative": "Decisive given the power and registration gates: the model integrates evidence smoothly with no detectable anatomical prior — directly reassuring for patients with variant vascular anatomy. Sensitivity-limited if registration QA fails its gate.",
      "cross_domain": {
        "borrowed_construct": "Regression discontinuity design from econometrics: units just across a cutoff are exchangeable, so a jump at the cutoff identifies the effect of cutoff-assigned treatment.",
        "measurement_it_implies": "A discontinuity estimate in predicted probability at the registered territory border, with placebo cutoffs and bandwidth sensitivity as validity checks.",
        "what_changes_if_dropped": "The analysis degrades to an ad-hoc matched boundary contrast without the placebo-cutoff and bandwidth discipline that makes the jump interpretable; the question survives but the inferential guarantee weakens."
      },
      "remaining_legwork": "2 days atlas-to-CT registration QA census, 4-6 days model training (shared with other candidates), 2 days discontinuity analysis: about 10 days to first decision.",
      "design_template": "conditional-observational",
      "entry_point_2_requirements": "Measurement: output discontinuity at registered arterial-territory borders under matched local evidence. Confused artifact: real watershed hemodynamics and registration error; placebo borders, five-channel matching, and registration perturbation address them.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "One question, one estimand (the boundary jump), though matching bandwidths need preregistration."
        },
        "identifiability": {
          "value": 3,
          "why": "Placebo cutoffs rule out generic edge behavior, but unreleased borderzone physiology correlated with the border cannot be fully excluded."
        },
        "medical_relevance": {
          "value": 4,
          "why": "An atlas prior that overrides case evidence is a concrete safety issue for variant anatomy; its absence is equally reportable."
        },
        "interest": {
          "value": 4,
          "why": "Whether segmentation models internalize vascular anatomy is a recognizable open question phrased at physician level."
        },
        "prior_legwork": {
          "value": 4,
          "why": "Atlas, registration tools, and model recipes exist; only the trained audit model is missing."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped: the trained-model and registration keystones are not inspected."
        },
        "data_readiness": {
          "value": 4,
          "why": "All inputs public; atlas registration to defaced CT is untested but standard."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "The discontinuity estimator with placebo cutoffs is custom though statistically standard."
        },
        "negative_result_value": {
          "value": 3,
          "why": "A gated null is meaningful (no atlas prior) but conditional on registration and power gates."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Targeted search found no emergent-prior audit; not exhaustive."
        },
        "regret": {
          "value": 4,
          "why": "Cheap, label-free, and the RDD grammar is reusable across the portfolio if it works."
        }
      },
      "priority_score": 3.5,
      "unverified_claims": [
        "deformable atlas registration achieves few-mm accuracy on defaced stroke CT",
        "a reproduced model reaches non-trivial held-out performance",
        "matched pairs exist in sufficient numbers near borders",
        "novelty beyond targeted search"
      ],
      "plain_pitch": "Strokes tend to respect the borders of each artery's supply zone, and doctors carry that vascular map in their heads. This study asks whether the prediction model carries the same map — whether its predicted damage jumps exactly at map borders even when two neighboring tissue spots look hemodynamically identical. If yes, the model imposes anatomy textbook knowledge on individual patients, which is reassuring for typical anatomy but risky for the many people whose vessels deviate from the textbook.",
      "track": "baseline",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-004-c03",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "The heart's signature in the head scan",
      "question": "Is a native-CTP final-infarct model using systemic contrast transit time — the arm-to-brain bolus delay that lengthens when cardiac output falls — as a patient-level severity signal beyond the local perfusion deficit?",
      "rung": "Target rung 1: use of global bolus timing; rung 3 language about cardiac performance would require an external cohort with measured cardiac function and is explicitly out of scope here.",
      "deliverable_sentence": "The final-infarct model is using systemic contrast transit time — the arm-to-brain bolus delay — as a patient-level severity signal.",
      "X_measurement": "From the released CTP resampled at 1 frame/second, automatically select the arterial input function and venous output function (standard components of every deconvolution pipeline) and compute X = bolus arrival delay (series start to AIF onset/peak) with recirculation timing as a secondary quantity. Compute-today test: YES — deterministic curve analysis on the released 4D series, no annotator.",
      "suspected_signal": "Reduced cardiac output (heart failure, atrial fibrillation — the leading stroke etiologies) prolongs arm-to-brain transit and simultaneously lowers collateral perfusion pressure, accelerating penumbra loss. Arrival delay is therefore both readable in the image and plausibly prognostic, and a network consuming the native time series may exploit it as a systemic-state covariate that perfusion maps discard (delay-insensitive deconvolution removes global arrival time by construction).",
      "use_vs_association": "Within-case, shape-preserving re-indexing of the time axis (shift the entire real frame sequence by +/-2, 4, 6 s within measured baseline/tail slack) changes global arrival time while leaving every local perfusion relationship untouched; a monotone signed output response isolates use of global timing. Mere association of delay with severity predicts zero response, because no local evidence changes.",
      "keystone_prerequisite": "Released 4D CTP retains enough pre-bolus baseline and post-venous-return tail on enough cases to permit +/-4 s shifts without truncating the bolus, and a native-CTP final-infarct model (Robben-recipe) can be trained to non-trivial held-out performance on 149 cases.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The verified nearby fact is the uniform 1 frame/second resampling (time axis well defined); the load-bearing facts — per-case baseline/tail slack and trainability of a 4D model at this cohort size — require the download-and-train stage 0. The claim is also scoped to native-CTP models: map-consuming models plausibly never see arrival time, and a null there would be trivial.",
      "rung_reached": "0; rung 1 after slack census, positive-control gate, and monotone dose-response; higher rungs need external cardiac-function data.",
      "dies_like_prior": "Adjacent to paused idea-022 (model mistaking scan end for bolus end) and superficially to killed idea-024 (DATA_ACCESS). Differences from 022: this is a positive-X question (systemic timing as signal), not a truncation-confound audit; it budgets training its own Robben-recipe model rather than waiting for a released checkpoint; and its intervention is gated to keep the full bolus inside the window precisely to avoid the truncation interaction 022 identified. Unlike 024, every required input is in the public release.",
      "closest_prior_work": "Robben et al. (Medical Image Analysis 2020, DOI 10.1016/j.media.2019.101589) trained final-infarct models directly on native CTP plus metadata and showed metadata mattered, but never tested bolus-timing use. Clinical literature associates heart failure and AF with worse stroke outcome (association only). No located model-use test of systemic transit time; novelty unaudited.",
      "existing_assets": "Released raw and 1 fps-resampled 4D CTP for 149 cases, published native-CTP model recipe, standard AIF/VOF selection algorithms, released age/history tabular data for descriptive covariance.",
      "smallest_decisive_experiment": "Stage 0 census without any training: compute per-case AIF onset, baseline frames, and post-VOF tail across 149 cases; require >=40 cases with >=6 s slack on both sides; report the site-stratified arrival-delay distribution and its association with released outcome variables (descriptive). Census decision in about 3 days after download. Full experiment: train one Robben-recipe model, apply the shift ladder plus baseline-permutation shams on 30 slack-verified held-out cases; about 3 weeks total.",
      "standing_confounds_addressed": "The within-case shift fixes scanner, site, protocol, injector settings, habitus, prevalence, and referral by construction; site injection protocols confound only the observational census (stratified, not causal). Motion correction and resampling were applied uniformly by organizers. Scan-end truncation interaction is excluded by the slack gate. Labels never enter the primary paired readout.",
      "alternative_explanations": [
        "The model reacts to frame-edge padding artifacts rather than timing — baseline-only permutation shams that move no bolus discriminate this.",
        "The model uses arrival delay as a deconvolution/site artifact proxy rather than systemic state — rung-1 wording claims use of timing only; cardiac attribution is explicitly prohibited without external validation.",
        "A 4D model this small overfits and responds incoherently — the positive-control gate (response to a perturbation it must detect) precedes interpretation."
      ],
      "anticipated_negative": "Sensitivity-limited before gates; after slack and positive-control gates, a null says native-CTP models ignore globally available systemic timing — a useful entry in the maps-versus-native-input debate, since timing is exactly what maps discard.",
      "cross_domain": {
        "borrowed_construct": "Circulation time from cardiovascular physiology: arm-to-brain indicator transit was a bedside cardiac-function test decades before CT.",
        "measurement_it_implies": "AIF arrival delay as an indicator-dilution circulation-time surrogate.",
        "what_changes_if_dropped": "Without the physiology, the experiment is a bare robustness check to time shifts with no clinical payoff and should be killed."
      },
      "remaining_legwork": "Download plus timing census: ~3 days to the stage-0 decision; 4D model training and shift ladder: ~3 weeks to the use decision; largest compute item in this cycle (rough order 100 GPU-hours).",
      "design_template": "other:temporal-reparameterization",
      "design_template_justification": "No voxel content is synthesized or substituted; only the time index of real acquired frames changes. Calling it counterfactual-synthesis (already 8x concentrated in the portfolio) would misdescribe the intervention and the homogenization statistics.",
      "entry_point_2_requirements": "Measurement: automated AIF/VOF arrival delay and recirculation timing. Confused artifacts: site injection protocol and scan-start conventions (stratified; the within-case intervention is immune) and scan-end truncation (slack gate).",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "One scalar X, one signed intervention ladder, prespecified gates."
        },
        "identifiability": {
          "value": 3,
          "why": "The within-case shift is clean, but padding shams and the truncation interaction must carry real weight."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Whether models read systemic circulatory state from a head scan bears on cardiac comorbidity handling in stroke triage."
        },
        "interest": {
          "value": 4,
          "why": "Perfusion maps mathematically discard arrival time; showing a native model uses it would sharpen the maps-versus-native debate."
        },
        "prior_legwork": {
          "value": 3,
          "why": "The model recipe is published but no public checkpoint was verified; timing tools are standard."
        },
        "feasibility": {
          "value": 2,
          "why": "Requires training a 4D model on 149 cases; the heaviest candidate this cycle even before the cap."
        },
        "data_readiness": {
          "value": 3,
          "why": "Public, but the 4D series is the largest download and slack is unverified."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Paired output change is direct; gates are custom."
        },
        "negative_result_value": {
          "value": 3,
          "why": "Interpretable only after the positive-control gate; then genuinely useful."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Targeted search only."
        },
        "regret": {
          "value": 3,
          "why": "Worth doing, but the model asset cost is real and shared bottleneck risk with idea-022 is acknowledged."
        }
      },
      "priority_score": 3.15,
      "unverified_claims": [
        "per-case baseline/tail slack sufficiency",
        "trainability of a native-CTP model at n=149",
        "arrival delay varies meaningfully across this cohort",
        "cardiac-output-to-arrival-delay strength in this setting",
        "novelty beyond targeted search"
      ],
      "plain_pitch": "When the heart pumps weakly, injected contrast dye takes noticeably longer to travel from the arm to the brain, and that delay is written into the scan's timeline. This study asks whether a model that reads the raw time series uses that delay — effectively reading the patient's heart performance from a head scan — when forecasting the final stroke damage. The test shifts the whole timeline of real frames a few seconds without changing anything local; if predictions move in step with the shift, the model is using the timing signal.",
      "track": "baseline",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-004-c04",
      "parent_ids": [],
      "search_mode": "C",
      "entry_point": 2,
      "title": "The model may be watching the patient's eyes",
      "question": "Is an ISLES'24 final-infarct model using conjugate gaze deviation — which way the patient's eyes point in the scanner — as a stroke-severity signal?",
      "rung": "Mode C target rung 1: use of the image-computable gaze angle; rung 3 language about the model reading examination-grade neurology would require external validation against documented clinical gaze findings.",
      "deliverable_sentence": "The final-infarct model is using conjugate gaze deviation — the direction the patient's eyes point — as a severity signal when predicting final infarct.",
      "X_measurement": "Automatically segment globes and lenses (TotalSegmentator head_glands_cavities task: eye_left/right, eye_lens_left/right) and compute the 3D conjugate gaze vector and deviation angle; an AI 3D implementation exists (conjugate gaze adjusted length, CGAL) that correlated with NIHSS at r=0.72 and identified acute ischemic stroke with sensitivity up to 91% (PMC7717852). Compute-today test: YES on any head CT whose orbits are intact — which is precisely the keystone, not the tool.",
      "suspected_signal": "Acute injury or hypoperfusion of the frontal eye fields and attention network drives sustained conjugate deviation toward the lesioned hemisphere — Prevost's sign, present in over half of admission CTs in acute ischemic stroke per the CGAL literature and an NIHSS examination item ('best gaze'). The orbits sit inside the head-CT field of view, so a whole-head 3D network can read a behavioral severity-and-laterality marker no one intended to give it.",
      "use_vs_association": "Within-case orbit-only substitution: replace orbital content with the same patient's mirror-neutralized orbits and apply graded globe rotations as a dose-response, leaving brain, vessels, skull, and perfusion untouched; output change under orbit-only edits, monotone in rotation angle, with null response to equal-volume extraorbital shams, isolates use. Association (gaze correlates with severity) predicts zero edit response.",
      "keystone_prerequisite": "Globes and lenses are present and geometrically intact in the released defaced NCCT/CTP, and the audited model's input crop includes the orbits.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The documented facts cut both ways: scans are 'defaced based on brain and face masks obtained with TotalSegmentator' (arXiv 2408.10966v1), and the TotalSegmentator README describes the removed class only as 'face_region (for anonymization)' with no statement on globes. Additionally the winning team skull-strips with SynthStrip (arXiv 2505.18424), so the claim is scoped to whole-head-input models, possibly only ones this program trains. All three assumptions are checkable in one hour on three downloaded cases — the honest Mode C posture is to declare, not guess.",
      "rung_reached": "0; rung 1 after the orbit-intactness gate, receptive-field/crop gate, and the substitution dose-response.",
      "dies_like_prior": "Closest process-relative is idea-007, which advanced on a claimed model output that did not exist. The analogous fatal fact here (orbits absent from the release) is named up front with a one-hour stage-0 check rather than discovered in critique. No annotation-provenance dependence: the primary readout is label-free paired output change.",
      "closest_prior_work": "The CGAL paper measures 3D gaze on CT with AI and links it to stroke presence and NIHSS (PMC7717852); visually determined CT eye deviation predicts stroke-code diagnosis (PMID 27576212) and admission eye deviation is associated with larger stroke volumes and 3-month disability (Clinical Radiology, DOI 10.1016/j.crad.2016.06.113 record S0009-9260(16)30320-8). None asks whether a lesion-prediction model reads gaze. Novelty unaudited beyond targeted search.",
      "existing_assets": "Public NCCT/CTP with orbits possibly intact, TotalSegmentator eye/lens classes, published CGAL measurement construct, label-free paired readout, and this program's planned shared audit model.",
      "smallest_decisive_experiment": "Stage 0: download three cases and inspect orbit integrity plus model-crop coverage (one hour after download). If passed: compute gaze angles on all 149 cases (half a day) and report the distribution against the published >55% prevalence; then orbit-neutralization plus graded-rotation edits on 30 held-out cases with the shared whole-head model — about one week after model availability, under 10 GPU-hours.",
      "standing_confounds_addressed": "Within-case edits fix scanner, site, protocol, positioning, habitus, prevalence, and referral. Head rotation versus true gaze deviation is the measurement confound: the edit rotates globes within a fixed head, separating the two by construction. Sedation or eye closure adds noise, not bias, to the paired test. Labels never enter the primary readout.",
      "alternative_explanations": [
        "The model responds to any orbital edit — equal-magnitude extraorbital shams and the monotone dose-response discriminate artifact from signal.",
        "The model reads head positioning rather than gaze — fixed-head globe rotation separates them.",
        "The model never sees the orbits (crop or stripping) — an early architecture/crop gate; a null without it is uninterpretable, hence the capped negative-result score."
      ],
      "anticipated_negative": "Uninterpretable if the orbit-intactness or crop gate fails; after gates, sensitivity-limited (models may downweight extracranial voxels); negative-result value capped at 2 accordingly.",
      "cross_domain": {
        "borrowed_construct": "Bedside behavioral neurology: gaze preference as a physical-examination severity sign (NIHSS item 2).",
        "measurement_it_implies": "An image-computable 3D gaze angle as an imaging surrogate of an examination finding.",
        "what_changes_if_dropped": "Without the examination-sign frame this becomes an arbitrary far-field sensitivity test and should be killed."
      },
      "remaining_legwork": "One hour to the keystone verdict after download; half a day for the cohort gaze census; one week to the use decision after the shared model exists.",
      "design_template": "regional-substitution",
      "design_template_justification": "Shares the substitution skeleton with c05 by necessity; they differ in object (acute behavioral sign in the orbits versus chronic demographic marker at the midline), readout (vector-valued rotation dose-response versus scalar physiologic-range dose), and failure mode probed (severity-proxy shortcut versus demographic-fairness shortcut). Both are retained because each is the natural minimal test of its X.",
      "entry_point_2_requirements": "Measurement: 3D conjugate gaze angle from automated globe/lens segmentation. Confused artifacts: head rotation/positioning and defacing damage; fixed-head globe rotation, head-pose-adjusted geometry, and the stage-0 orbit inspection address them.",
      "scores": {
        "mechanism_clarity": {
          "value": 5,
          "why": "A specific neuro-ophthalmological mechanism (frontal eye field involvement drives ipsilesional deviation) with a named, published, automated measurement."
        },
        "identifiability": {
          "value": 4,
          "why": "Orbit-only edits with rotation dose-response and extraorbital shams isolate the cue unusually cleanly if the data survive defacing."
        },
        "interest": {
          "value": 5,
          "why": "A tissue-segmentation model reading the patient's gaze would genuinely surprise both communities; the null after gates is also tellable."
        },
        "medical_relevance": {
          "value": 3,
          "why": "Gaze is a real severity signal, so use is not an artifact — but it means the model reads behavior rather than tissue, which matters for portability and trust."
        },
        "clarity": {
          "value": 5,
          "why": "One sign, one angle, one graded within-case intervention."
        },
        "prior_legwork": {
          "value": 4,
          "why": "Automated 3D gaze measurement and its clinical correlations are published; only the audit is new."
        },
        "feasibility": {
          "value": 2,
          "why": "Reported outside the Mode C score: the defacing keystone may kill it in the first hour, and a whole-head model must exist."
        },
        "data_readiness": {
          "value": 3,
          "why": "Public data, but orbit survival is the open question."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Paired readout is direct; edit-validity gates are custom."
        },
        "negative_result_value": {
          "value": 2,
          "why": "Capped: a null is uninterpretable unless the crop and intactness gates pass."
        },
        "novelty_confidence": {
          "value": 2,
          "why": "Targeted search only, in a literature this program knows less well."
        },
        "regret": {
          "value": 4,
          "why": "The keystone check costs an hour; if the eyes survived defacing, this is the cheapest memorable use-test in the portfolio."
        }
      },
      "mode_c_priority_score": 4.45,
      "unverified_claims": [
        "globes/lenses survive TotalSegmentator-based defacing in the release",
        "audit-model crop includes orbits",
        "gaze-deviation prevalence in this cohort matches published rates",
        "edit realism of rotated orbital content",
        "novelty"
      ],
      "plain_pitch": "Stroke patients' eyes often drift toward the damaged side of the brain — an old bedside sign that also shows up on the CT scan, where an existing automated tool can measure it. This speculative study asks whether the damage-forecasting model has quietly learned to glance at the patient's eyes as a severity cue. The whole idea lives or dies on one cheap check: whether the anonymization step that removes faces from the public scans spared the eyes; if it did, rotating only the eyes in the image and watching the forecast move would be the demonstration.",
      "track": "baseline",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-004-c05",
      "parent_ids": [],
      "search_mode": "C",
      "entry_point": 2,
      "title": "The brain's odometer: calcification as the model's age gauge",
      "question": "Is an ISLES'24 final-infarct model using physiologic intracranial calcification — the pineal, habenular, and choroid plexus calcium that accumulates with age — as an age gauge that scales its infarct forecast?",
      "rung": "Mode C target rung 1: use of the calcification cue; rung 3 language ('the model estimates age') would require representation-level age probes and an external cohort, out of scope here.",
      "deliverable_sentence": "The final-infarct model is using physiologic midline and choroid plexus calcification as an image-derived age gauge when predicting final infarct.",
      "X_measurement": "Atlas-localize pineal, habenular, and choroid plexus ROIs on NCCT; X = calcified volume and Agatston-style mass (HU >= 130) per structure — deterministic, no annotator. The age link is documented: physiologic intracranial calcifications are present in 50-70% of adults over 30 and prevalence rises with age; an 11,941-subject NCCT study reports choroid plexus calcification in 70.2% and pineal in 71.6% (ScienceDirect S0891061816300783; corroborated by 18F-NaF PET/CT, J Nucl Med 60:267). Compute-today test: YES on any unseen NCCT with an atlas and HU arithmetic.",
      "suspected_signal": "Pineal and choroid plexus calcification accumulates roughly monotonically with age; age in turn tracks collateral quality, white-matter vulnerability, and infarct evolution. These calcifications are bright, stereotyped, midline landmarks — exactly the kind of cue a network can learn as a demographic shortcut, giving older-looking brains systematically different forecasts at matched physiology.",
      "use_vs_association": "Within-case graded editing of only calcification voxels (remove, halve, intensify within the cohort's measured per-structure HU/volume range) in structures remote from the ischemic territory, all else fixed; a monotone signed response of the predicted infarct in the threatened territory, with null response to equal-HU edits at matched non-calcification control sites, isolates use of the cue. Association with age predicts zero edit response.",
      "keystone_prerequisite": "Physiologic calcifications are reliably quantifiable in the released resampled NCCT (resolution and HU fidelity) and vary enough across 149 cases to be learnable (calcified volume correlates with released age, target Spearman >= 0.3).",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The prevalence and age-association literature is from clinical native NCCT, not from ISLES'24 derivatives; resampling may blur small calcifications and quantitative HU integrity of the release is unverified (cycle-003 flagged the same concern for blood HU). Even with the cue verified quantifiable, the claim stops at 'uses the cue' — attributing an age prior needs the descriptive age-covariance analysis in the released demographics and is supporting, not proving.",
      "rung_reached": "0; rung 1 after the learnability census and the graded remote-edit response with control sites.",
      "dies_like_prior": "Cycle 003 dropped carotid-siphon calcification because no within-case edit could separate 'chronic cerebrovascular reserve' from 'age and systemic burden.' This card dissolves that objection instead of fighting it: age-proxy use IS the claim, so no separation is attempted; the burden moves to edit realism and remoteness, both explicitly gated. Distinct from 003-c04 (dural sinus HU as oxygen gauge — different structures, different construct) and 001-c04 (parenchymal frailty features).",
      "closest_prior_work": "Shortcut-learning literature shows radiology models recover demographics (age, sex, race) from images and can use them as prediction shortcuts; brain-age estimation is established for MRI. The calcification-age association is documented (S0891061816300783). No located work tests whether stroke final-infarct models read physiologic calcification as a demographic cue; novelty unaudited beyond targeted search.",
      "existing_assets": "Public NCCT with released patient age in demographics, deterministic HU-threshold measurement, atlas localization tools, the program's shared audit model, and a label-free paired readout.",
      "smallest_decisive_experiment": "Stage 0 census on 149 NCCTs: detectable pineal/choroid calcification rates versus published prevalence, calcified volume versus released age (gate: Spearman >= 0.3), test-retest under one-voxel erosion. If passed: three-dose remote edits plus control-site shams on 40 held-out cases; about one week after the shared model exists, under 10 GPU-hours.",
      "standing_confounds_addressed": "Within-case edits fix scanner, vendor, protocol, site, positioning, habitus, prevalence, and referral; edit realism is gated by staying inside cohort-measured per-structure distributions. NOT excluded: the model may respond to any bright midline change (control sites address but cannot eliminate), and calcification may proxy vascular pathology rather than age alone — the claim wording stays at cue-use for exactly this reason. Labels never enter the primary readout.",
      "alternative_explanations": [
        "Response to arbitrary bright edits — matched control-site shams discriminate.",
        "Calcification proxies systemic vascular burden rather than age — rung-1 wording claims cue-use only; the age-covariance analysis is reported descriptively.",
        "The network's receptive field never links midline structures to the threatened territory — early architecture gate, as in c04; a null before it is uninterpretable."
      ],
      "anticipated_negative": "After the learnability and receptive-field gates, a null is a meaningful negative: the model ignores the most explicit age marker in the image, evidence against the demographic-shortcut concern for this model family. Before gates, sensitivity-limited.",
      "cross_domain": {
        "borrowed_construct": "Shortcut learning and algorithmic fairness: models exploiting demographic proxies invisible in their specification.",
        "measurement_it_implies": "Dose-response of the forecast to a graded, image-computable demographic marker.",
        "what_changes_if_dropped": "The probe remains a valid interpretability experiment on a named radiologic structure, but loses the fairness stake that makes the answer matter beyond this dataset."
      },
      "remaining_legwork": "1-2 days calcification census and age-correlation gate after download; 2 days edit machinery; one week to the use decision after the shared model exists.",
      "design_template": "regional-substitution",
      "design_template_justification": "Shares the substitution skeleton with c04; retained because the two probe different objects (chronic demographic marker versus acute behavioral sign), different readouts (scalar physiologic-range dose versus vector rotation), and different failure modes (fairness shortcut versus severity proxy). See c04 for the paired justification.",
      "entry_point_2_requirements": "Measurement: HU >= 130 calcified volume/mass in atlas-localized pineal, habenular, and choroid plexus ROIs. Confused artifacts: resampling blur and HU quantitative drift (census gate), and generic bright-edit response (control sites).",
      "scores": {
        "mechanism_clarity": {
          "value": 5,
          "why": "A specific physical quantity (calcified volume of named structures), its documented age association, and the exact measurement that would show use."
        },
        "identifiability": {
          "value": 4,
          "why": "Remote graded edits with matched control sites isolate the cue; what remains open is the age-versus-vascular-burden naming, which the wording already concedes."
        },
        "interest": {
          "value": 4,
          "why": "A segmentation model reading the brain's odometer is a memorable, checkable instance of demographic shortcut learning."
        },
        "medical_relevance": {
          "value": 4,
          "why": "If forecasts scale with an age proxy at matched physiology, that is a concrete fairness and trust finding for deployment."
        },
        "clarity": {
          "value": 4,
          "why": "One cue family, one dose ladder; the multi-structure ROI set needs preregistration."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Prevalence literature and measurement are ready; the audit model and edit machinery are not."
        },
        "feasibility": {
          "value": 3,
          "why": "Reported outside the Mode C score; simple edits, but hostage to HU fidelity and the shared model."
        },
        "data_readiness": {
          "value": 3,
          "why": "Public NCCT plus released age; derivative HU fidelity unverified."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Paired dose-response is direct; realism gates are custom."
        },
        "negative_result_value": {
          "value": 3,
          "why": "A gated null meaningfully bounds the shortcut concern for this family."
        },
        "novelty_confidence": {
          "value": 2,
          "why": "Shortcut-learning literature is large; targeted search only."
        },
        "regret": {
          "value": 4,
          "why": "Cheap census, released age variable, and a fairness-relevant answer either way."
        }
      },
      "mode_c_priority_score": 4.3,
      "unverified_claims": [
        "calcifications survive resampling quantifiably",
        "calcified volume correlates with released age in this cohort",
        "edit realism within physiologic range",
        "receptive-field coverage from midline to territory",
        "novelty"
      ],
      "plain_pitch": "As people age, tiny harmless calcium deposits build up in a few midline brain structures, and they glow brightly on CT — a kind of odometer for the brain. This speculative study asks whether the stroke-outcome model has learned to read that odometer and quietly scale its damage forecast by how old the patient looks. The test is to dial those calcium specks up or down in the image, far from the stroke itself, and watch whether the forecast follows; if it does, the model is using an age proxy, which matters for whether older patients get systematically different predictions from the same physiology.",
      "track": "baseline",
      "charter": "isles24"
    },
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
    },
    {
      "id": "isles24-scout-004-c07",
      "parent_ids": [],
      "track": "wide",
      "entry_point": 2,
      "title": "The edge of the map: the benchmark scores terra incognita",
      "question": "Is an ISLES'24 final-infarct model using the perfusion slab's support boundary -- the edge of the sensor, not the edge of the ischemia -- as a determinant of its predicted lesion extent, on a benchmark whose ground truth comes from whole-brain follow-up MRI?",
      "rung": "Target rung 1: the model's predicted extent is determined by sensor support at matched whole-brain evidence. The model-free stage 1 is itself a benchmark-integrity deliverable regardless of any model.",
      "deliverable_sentence": "The final-infarct model is using the perfusion-acquisition support boundary as a spatial determinant of its predicted lesion extent, truncating or extrapolating at the sensor's edge rather than the ischemia's.",
      "X_measurement": "X is the perfusion support mask and signed distance to its boundary, computed per case from the released perfusion maps (the set of voxels where CBF/Tmax are defined/non-degenerate) and the 4D CTP z-extent, expressed in both patient space and atlas space. Compute-today test: YES -- support masks are arithmetic on released volumes, no annotator.",
      "suspected_signal": "CTP acquisitions on many scanners cover a limited z-axis slab (published protocols range ~40-160 mm), while the ground truth is drawn on whole-brain follow-up MRI; the clinical literature shows coverage-dependent underestimation of ischemic volumes. If slabs in ISLES'24 are narrower than the brain, part of the scored ground truth lies where the primary modality never looked, and every trained model must adopt some convention there -- hard truncation at the sensor edge or hallucinated extrapolation from NCCT/CTA alone. Multi-step story, links separately checkable: models' predictions are shaped by the support boundary (X, stage 2), which matters only if ground-truth lesion mass overflows the support (Y, the model-free stage-1 census), which implies part of the official ranking, including the absolute-volume-difference metric, is decided by an unmeasured out-of-sensor convention (Z, computable as a metric-sensitivity bound in stage 1).",
      "use_vs_association": "Slab placement relative to anatomy is set by scanner hardware and head positioning, not by tissue state, so it varies quasi-randomly across patients: the same atlas location lies in-slab for some patients and out-of-slab for others. A systematic prediction difference at the same anatomical location, conditional on matched whole-brain evidence (NCCT and CTA are full-coverage), attributable to slab membership, shows the output is determined by sensor support rather than by the ischemia; the stage-1 ground-truth-overflow census is model-free and needs no such inference.",
      "keystone_prerequisite": "The released perfusion support is actually narrower than the brain in a non-trivial fraction of cases, and ground-truth lesion mass overflows it in enough cases to matter (prespecified: overflow > 5% of lesion volume in >= 10% of cases).",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Verified nearby facts: neither the challenge paper nor the dataset-paper abstract states CTP z-coverage or scanner hardware (both fetched and checked this stage, 2026-08-18), and the clinical literature documents that limited coverage is common and consequential (Neuroradiology 2014, DOI 10.1007/s00234-014-1429-9: ischemic volume underestimated at 80 mm coverage; AJNR 2010, ajnr.org/content/31/4/691: 70-75 mm needed for MCA territory). The load-bearing fact -- actual slab geometry in this release -- is checkable on three downloaded cases in under an hour, and the full census is trivially cheap. If slabs are whole-brain everywhere, the candidate dies for less than one session's cost.",
      "rung_reached": "0; stage 1 alone delivers a benchmark-integrity fact; rung 1 after the stage-2 conditional analysis on the shared audit model.",
      "dies_like_prior": "Kill-code check: nearest pause is idea-022 (does the model mistake the end of the SCAN for the end of the BOLUS) -- the same 'sensor boundary versus physiology' family but on the time axis, and paused because it needs a frozen raw-4D checkpoint plus training-time masking semantics. c07 differs decisively: its decisive stage is model-free arithmetic on released masks and maps (no checkpoint, no masking semantics), and the spatial support boundary is directly observable per case. It shares the boundary-discontinuity estimator with this cycle's baseline c02 (arterial-territory borders) -- shared statistical tooling, different boundary, different claim (sensor artifact versus anatomical prior); if both advance, the estimator is built once. IDENTIFIABILITY_FAILURE risk (idea-020's death) is confined to stage 2 and is honestly stated: less evidence beyond the slab is rational, so stage 2 measures HOW models behave at the edge, not whether behaving differently is irrational; the quantitative benchmark claim rests on stage 1.",
      "closest_prior_work": "Clinical CTP-coverage literature quantifies volume underestimation from limited slabs; final-infarct deep-learning papers use CTP inputs without reporting support handling; no located work measures ground-truth overflow of the sensor support in ISLES'24 or any public stroke benchmark, nor its effect on rankings. See novelty_neighbors.",
      "novelty_neighbors": [
        {
          "work": "'Whole brain CT perfusion in acute anterior circulation ischemia: coverage size matters' (Neuroradiology 2014)",
          "identifier": "DOI 10.1007/s00234-014-1429-9, PMID 25228451; found by search 2026-08-18",
          "relation": "Quantifies clinical underestimation of ischemic volumes at reduced z-coverage (80 mm and below) -- protocol literature, no segmentation models, no benchmark audit."
        },
        {
          "work": "'Optimal brain perfusion CT coverage in patients with acute middle cerebral artery stroke' (AJNR 2010)",
          "identifier": "https://www.ajnr.org/content/31/4/691; found by search 2026-08-18",
          "relation": "Establishes 70-75 mm z-coverage as the minimum for MCA-territory characterization -- the physical basis for expecting overflow, again with no model or benchmark analysis."
        },
        {
          "work": "'Underestimation of follow-up infarct volume by acute CT perfusion imaging' (Neurology 2025)",
          "identifier": "DOI 10.1212/WNL.0000000000213439; found by search 2026-08-18",
          "relation": "Documents that acute CTP-derived volumes underestimate follow-up infarct volumes clinically -- outcome-measurement literature that never separates the sensor-coverage component or touches challenge ground truth."
        }
      ],
      "novelty_delta": "No located work measures how much of a public stroke benchmark's ground truth lies outside the primary sensor's support, bounds the metric consequences (including the official absolute-volume-difference metric), or tests whether trained models' predicted extent is determined by the support boundary.",
      "why_not_done": "BLIND_SPOT: coverage adequacy lives in the clinical protocol literature, which the segmentation-challenge community does not read; challenge pipelines treat released maps as given inputs and their support as preprocessing trivia, so nobody has asked what fraction of the scored target the sensor ever saw.",
      "existing_assets": "Released perfusion maps, 4D CTP, whole-brain NCCT/CTA, ground-truth masks, and the official evaluation code (github.com/ezequieldlrosa/isles24 utils/eval_utils) -- everything stage 1 needs is a small subset of the release; the atlas registration tooling is shared with baseline c02.",
      "smallest_decisive_experiment": "Stage 1, model-free and decisive: download derivative perfusion maps plus ground-truth masks for all 149 cases (small fraction of the archive); compute per-case support masks, slab z-extent census, fraction of ground-truth lesion mass outside support, and the sensor-respecting performance ceiling -- the maximum Dice and minimum absolute volume difference attainable by ANY prediction confined to the support, using the official evaluation code. Prespecified kill: median slab covers the brain and overflow > 5% in < 10% of cases. Compute envelope: one Colab session, CPU-only, well under an hour of compute. Stage 2 (conditional on the shared audit model): boundary-discontinuity analysis at matched NCCT/CTA evidence across patients, under 5 GPU-hours.",
      "standing_confounds_addressed": "Stage 1 is arithmetic on released data -- no confounds, only measurement definitions (support degeneracy criteria preregistered). Stage 2: lesion size correlates with overflow (big lesions overflow more) -- conditioned on lesion volume; slab position may correlate with positioning quality and habitus -- the cross-patient contrast is restricted to atlas locations with both in-slab and out-of-slab representation and matched NCCT evidence; the fundamental entanglement that out-of-slab voxels genuinely have less evidence is stated as a scope limit: stage 2 characterizes the learned convention (truncate versus extrapolate and how sharply), not its irrationality. Labels enter stage 1 as the object of study and are excluded from the stage-2 conditioning variables.",
      "alternative_explanations": [
        "Predictions fade beyond the slab simply because evidence fades -- conceded by design; the claim is about WHERE the extent decision is made (sensor edge versus ischemia edge) and what the benchmark does with it, not about model irrationality.",
        "Support-mask degeneracy is misdefined (zeros versus resampling padding) -- preregistered support criteria with per-case audit dumps.",
        "Overflow is an artifact of registration between MRI-space masks and CT-space maps -- the overflow census is computed in the released common space, and gross misregistration cases are flagged by the c08 census if both advance."
      ],
      "anticipated_negative": "Fully decisive either way at stage 1: substantial overflow is a benchmark fact with a computable metric-sensitivity bound; near-zero overflow is a documented reassurance that ISLES'24's sensor coverage matches its scoring target -- worth one session either way. Stage-2 nulls (no boundary-locked behavior) are informative only after the stage-1 gate passes.",
      "cross_domain": {
        "borrowed_construct": "Swath/footprint analysis from satellite remote sensing: any measurement campaign must report what fraction of the mapping target lies outside the sensor's swath, and maps must distinguish 'observed empty' from 'never observed'.",
        "measurement_it_implies": "The per-case coverage-completeness fraction (target mass inside sensor support) and the observed/unobserved distinction propagated into the evaluation metric.",
        "what_changes_if_dropped": "Without the swath discipline the study collapses into anecdotes about individual cases at the slab edge; the coverage-completeness fraction is what turns it into a quantitative benchmark audit."
      },
      "remaining_legwork": "One session for the full stage-1 census including the metric-ceiling computation; half a day to write the audit report; stage 2 only if the gate passes and the shared model exists (2-3 days).",
      "design_template": "conditional-observational",
      "entry_point_2_requirements": "Measurement: perfusion support mask, ground-truth overflow fraction, sensor-respecting metric ceiling, and boundary-conditional prediction contrast. Confused artifacts: support-mask definition and mask-map registration error -- preregistered support criteria and flagged-case audit; the evidence-availability entanglement in stage 2 is stated as a scope limit, not assumed away.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "Two stages with exact computable readouts; the stage-2 estimand (learned edge convention) needs careful preregistration to stay separated from the rationality question."
        },
        "identifiability": {
          "value": 3,
          "why": "Stage 1 is assumption-free arithmetic; stage 2's use claim is honestly entangled with evidence availability and is scoped to characterizing the convention rather than proving irrationality."
        },
        "medical_relevance": {
          "value": 4,
          "why": "If part of the scored target was never seen by the primary modality, volume-based triage metrics and challenge rankings inherit an unmeasured convention; either census outcome directly informs how the benchmark should be read."
        },
        "interest": {
          "value": 4,
          "why": "'The benchmark scores terra incognita' is a claim every challenge participant would want settled, and the sensor-respecting ceiling is a number nobody has computed for any stroke benchmark."
        },
        "prior_legwork": {
          "value": 4,
          "why": "Everything needed for the decisive stage is released, including the official metric code; the clinical coverage literature supplies priors and framing."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped at 3: the slab-geometry keystone is not inspected -- though it is the cheapest keystone in the portfolio to check."
        },
        "data_readiness": {
          "value": 4,
          "why": "Stage 1 needs only maps and masks, a small public subset; no model required."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "Official evaluation code is public and the ceiling computation reuses it directly; only the support definition is custom."
        },
        "negative_result_value": {
          "value": 4,
          "why": "A near-zero overflow census is a clean, citable reassurance about the benchmark -- decisive, not sensitivity-limited."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Coverage literature is adjacent but the benchmark-audit question is unclaimed in every source found; targeted search only."
        },
        "regret": {
          "value": 4,
          "why": "One CPU session settles a question that becomes obvious in hindsight the first time a large-lesion case is inspected; skipping it risks every model comparison on this benchmark carrying an unexamined convention."
        }
      },
      "priority_score": 3.6,
      "unverified_claims": [
        "CTP slabs in this release are narrower than the brain in a non-trivial fraction of cases",
        "ground-truth lesion mass overflows the support at the prespecified threshold",
        "support masks are recoverable from map degeneracy patterns as assumed",
        "novelty beyond targeted search"
      ],
      "plain_pitch": "The stroke scans that measure blood flow often cover only a slab of the head -- like a satellite that photographs a strip of ground on each pass -- while the 'correct answers' for this benchmark were drawn on later whole-brain MRI. That mismatch would mean models are scored on brain regions their main sensor never saw, and each model must invent its own policy there: stop at the sensor's edge, or guess beyond it. This study first measures, with simple arithmetic on the public data, how much of the official answer lies outside the sensor's view and how much that could move the leaderboard; if the answer is 'a lot', it then checks whether models draw their predicted damage boundary at the sensor's edge rather than the injury's. Either outcome changes how results on this benchmark should be read.",
      "charter": "isles24"
    },
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
  ]
}


===== ideas/scout-isles24-004/run_provenance.json =====
{
  "timestamp": "2026-08-18T16:39:19+00:00",
  "git_commit": "9777f6fac353c178736c8c47e0d2590351d57775",
  "claude_cli": "2.1.197 (Claude Code)",
  "codex_cli": "codex-cli 0.147.0",
  "tracks": [
    "baseline",
    "wide"
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


===== ideas/scout-isles24-004/scout_candidates.json =====
{
  "cycle": "scout-isles24-004",
  "charter": "isles24",
  "date": "2026-08-18",
  "track": "baseline,wide",
  "dataset_verification": {
    "verified_facts": [
      "Zenodo record 16731717 (inspected 2026-08-18): each case provides admission NCCT, CTA, 4D CTP time series, and perfusion maps (Tmax, CBF, CBV, MTT); follow-up 'post-treatment MRI (DWI and ADC)'; 'binary infarct masks derived from follow-up MRI (lesion-msk.nii.gz)'; LVO binary masks from CTA; automatic multilabel Circle-of-Willis masks; clinical data (demographics, history, admission NIHSS, 3-month mRS). 149 training cases, open access, CC BY-NC-SA 4.0. Verbatim: \"'Raw_data' refers to the 'raw' acquired scans, which are released in their original space, just defaced.\" (DOI 10.5281/zenodo.16731717)",
      "Ground truth, verbatim from the challenge paper HTML (arXiv 2408.10966v1, inspected 2026-08-18): 'Lesion masks are derived from DWI images using the ISLES'22 ensemble algorithm. Quality control and correction of the lesion masks are performed when needed by medical students (TAB, HPM) supervised by two neuroradiologists (JSK, BW) with more than 10 years of experience.' The ISLES'22 ensemble algorithm is publicly released as DeepISLES: Docker image isleschallenge/deepisles, weights on Zenodo (version 14026715), inputs DWI (b=1000) and ADC required with FLAIR 'Required for ensemble (optional for single algorithm outputs)', Apache-2.0, Nature Communications 2025 (github.com/ezequieldlrosa/DeepISLES, inspected 2026-08-18).",
      "Organizer preprocessing, verbatim (arXiv 2408.10966v1): 'All scans are defaced based on brain and face masks obtained with TotalSegmentator. CTP series are motion-corrected through image co-registration and temporally resampled at 1 frame/second. All imaging series registered to NCCT scans using rigid transformations (affine for MRI).' Perfusion maps: 'Preprocessing of the CTP series has been performed using the FDA-approved clinical software icobrain cva. Perfusion maps are generated using a traditional tracer-kinetics deconvolution algorithm.'",
      "Cohort and split: 250 planned sets — 150 training (100 University Hospital Munich, 50 University Hospital Zurich) and 100 test from the same two centers (50 each), per arXiv 2505.18424v1 and 2408.10966v1 (both inspected); the dataset paper reports 245 realized cases and the public Zenodo training release holds 149 (arXiv 2408.11142 abstract, inspected; published as Radiology: Artificial Intelligence DOI 10.1148/ryai.250603, PMID 42017802). Follow-up MRI is acquired 2-9 days after acute imaging (arXiv 2408.11142 abstract, verbatim 'follow-up MRI after 2-9 days'). The 150/149 and 250/245 planned-versus-realized discrepancy is recorded, not reconciled.",
      "Official evaluation: Dice, absolute volume difference, lesion-wise F1, and absolute lesion count difference, ranked by averaging per-case ranks across metrics (github.com/ezequieldlrosa/isles24 utils/eval_utils, inspected; arXiv 2408.10966v1).",
      "The winning method's preprocessing used SynthStrip skull-stripping and custom intensity windowing, with windowing reported to improve CT-based segmentation by 10 Dice points; no code or checkpoint release statement was found in the paper (arXiv 2505.18424v1, inspected 2026-08-18)."
    ],
    "source_supported_interpretations": [
      "'Correction ... performed when needed' implies an unknown, possibly large fraction of released ground-truth masks are uncorrected ensemble output; that fraction is measurable because the initializing segmenter is public and the follow-up DWI/ADC it consumes are released (basis of c01).",
      "Because derivative CTP is uniformly motion-corrected and resampled at 1 frame/second, the released time axis is well defined in seconds, making bolus-timing quantities computable per case (basis of c03); the scan-start-to-injection offset remains a site protocol variable.",
      "Because top pipelines skull-strip, any extracranial cue (orbits, calcified midline structures near ventricles are intracranial and survive) is testable only in whole-head-input models; c04 is scoped accordingly."
    ],
    "unresolved_dataset_facts": [
      "Whether the TotalSegmentator 'face_region (for anonymization)' class used for defacing includes the globes/orbits — the TotalSegmentator README (inspected) does not specify; decisive for c04 and checkable in one hour on three downloaded cases.",
      "Which DeepISLES version/weights initialized the ground-truth drafts, and whether the organizers ran the FLAIR-using full ensemble or a DWI/ADC-only configuration (FLAIR is not in the release).",
      "Per-case 4D CTP baseline and tail durations (frames before bolus arrival and after venous return) — needed by c03, not verifiable without download.",
      "Whether treatment/reperfusion fields (TICI, thrombectomy, thrombolysis) are in the released clinical tables — the challenge paper lists demographics, history, admission NIHSS, and 3-month mRS explicitly; treatment fields were not confirmed on the record inspected.",
      "Quantitative HU fidelity of resampled derivative NCCT (inherited concern from cycle 003, relevant to c05)."
    ],
    "sources": [
      "https://zenodo.org/records/16731717 (DOI 10.5281/zenodo.16731717)",
      "https://arxiv.org/html/2408.10966v1 and https://arxiv.org/abs/2408.10966",
      "https://arxiv.org/abs/2408.11142 (published: DOI 10.1148/ryai.250603, PMID 42017802)",
      "https://arxiv.org/html/2505.18424v1",
      "https://github.com/ezequieldlrosa/isles24",
      "https://github.com/ezequieldlrosa/DeepISLES",
      "https://github.com/wasserth/TotalSegmentator",
      "https://github.com/Chin-Fu-Liu/Arterial_Atlas (DOI 10.1038/s41597-022-01923-0)"
    ]
  },
  "all_questions": [
    {"n": 1, "question": "Is an ISLES'24-trained final-infarct model using the boundary conventions that the public DeepISLES draft left in the 'corrected when needed' ground truth, rather than tissue-fate evidence alone?", "disposition": "DEVELOPED as isles24-scout-004-c01 (Mode A); the annotation pipeline is documented and the initializer is re-runnable."},
    {"n": 2, "question": "Is an ISLES'24 final-infarct model using arterial-territory membership — the brain's vascular map — as a spatial prior beyond the case's own perfusion and tissue evidence?", "disposition": "DEVELOPED as isles24-scout-004-c02 (Mode B); radiologist word: vascular territory/watershed; cross-domain borrow: regression discontinuity from econometrics."},
    {"n": 3, "question": "Is a native-CTP final-infarct model using systemic contrast transit time — the arm-to-brain bolus delay that lengthens when cardiac output falls — as a patient-level severity signal?", "disposition": "DEVELOPED as isles24-scout-004-c03 (Mode B); cross-domain borrow: circulation time from cardiovascular physiology; suspected hard (requires training a native-4D model)."},
    {"n": 4, "question": "Is an ISLES'24 final-infarct model using conjugate gaze deviation — which way the patient's eyes point in the scanner — as a stroke-severity signal?", "disposition": "DEVELOPED as isles24-scout-004-c04 (Mode C); the obviously-wrong slot I cannot refute without inspecting whether defacing spared the globes; radiologist word: Prevost's sign / conjugate eye deviation."},
    {"n": 5, "question": "Is an ISLES'24 final-infarct model using physiologic intracranial calcification — the pineal, habenular, and choroid plexus calcium that accumulates with age — as an age gauge that scales its infarct forecast?", "disposition": "DEVELOPED as isles24-scout-004-c05 (Mode C); radiologist word: physiologic calcification."},
    {"n": 6, "question": "Is the model using white-matter fiber orientation — the brain's grain — to shape how the predicted infarct extends beyond the perfusion core?", "disposition": "DROPPED: dies like idea-020 (IDENTIFIABILITY_FAILURE); no intervention exists and no null yet separates tract-aligned growth from co-aligned territory and perfusion-gradient geometry."},
    {"n": 7, "question": "Is the model using beat-to-beat oscillations in the contrast time-attenuation curves as a cardiac-rhythm (atrial fibrillation) marker?", "disposition": "DROPPED by verification: the released CTP is temporally resampled at 1 frame/second (arXiv 2408.10966v1 verbatim), below Nyquist for cardiac frequencies; the too-hard slot resolved as refuted."},
    {"n": 8, "question": "Is the model using calcified plaque at the occlusion site to treat atherosclerotic occlusions differently from embolic ones?", "disposition": "DROPPED: outcome direction is ambiguous (chronically preconditioned collaterals versus reocclusion risk), and etiology validation would require new annotation; cycle-003's siphon-calcification drop reasoning partially applies."},
    {"n": 9, "question": "Is the model using ventricular and sulcal CSF volume as a compliance reservoir that determines how much swelling a predicted infarct can tolerate?", "disposition": "DROPPED: duplicates isles24-scout-003-c08 (skull as pressure vessel) and 001-c04 (frail brain), and the endpoint mismatches the tissue-fate target."},
    {"n": 10, "question": "Are high-ranking models using a few-large-blobs shape convention that the lesion-wise F1 and lesion-count metrics forgive, at the expense of scattered embolic infarcts?", "disposition": "DROPPED this cycle: X is an output convention, not an image-computable input quantity, so it fails the 'model is using X' eligibility form; recorded as an evaluation-critique seed for a future cycle."}
  ],
  "quota_note": "Quotas filled without padding: 1 Mode A (c01), 2 Mode B (c02, c03), 2 Mode C (c04, c05); all five are CT/radiology; zero dermatology. All five use ISLES'24 because the charter mandates that dataset; the generic no-more-than-two-per-dataset rule conflicts with the charter, and the charter controls (same disclosure as cycle 003). All five declare entry_point 2 — no documented model-beats-human gap for ISLES'24 was verified, so entry_point 1 was not honestly available. Zero revivals: no unblock condition in the portfolio brief has a newly verified fact; c03 is deliberately a NEW question adjacent to paused idea-022 (different estimand, new model asset) and is not a revival of it. Design templates: cross-model-disagreement, conditional-observational, other:temporal-reparameterization, and regional-substitution twice (c04/c05, justified in both cards per the diversity mandate).",
  "candidates": [
    {
      "id": "isles24-scout-004-c01",
      "parent_ids": [],
      "search_mode": "A",
      "entry_point": 2,
      "title": "The ground truth remembers the algorithm that drafted it",
      "question": "Is an ISLES'24-trained final-infarct model using the boundary conventions that the DeepISLES draft left in the 'corrected when needed' ground truth, rather than tissue-fate evidence alone?",
      "rung": "Target rung 1: models reproduce draft-specific conventions in expert-overridden voxels; rung 2 requires replication across at least two trained model families and both centers.",
      "deliverable_sentence": "The final-infarct model is using the ground truth's algorithmic fingerprint — DeepISLES boundary conventions inherited through the 'corrected when needed' annotation pipeline — in the voxels where experts overrode the draft.",
      "X_measurement": "Rerun released DeepISLES (Docker isleschallenge/deepisles, weights Zenodo version 14026715) on each case's released follow-up DWI/ADC to obtain draft mask D; X is the draft-versus-released-GT disagreement field D xor G plus draft-agreement statistics (per-case Dice(D,G), bitwise-identical fraction, boundary surface distance). Compute-today test: YES — X is computed from released follow-up images by a public containerized tool, no annotator; note X lives on the follow-up image, while the audited model consumes only acute CT.",
      "suspected_signal": "Not a biological signal but a documented process one: masks were initialized by a public ensemble and corrected only 'when needed', so the released labels carry the initializer's systematic conventions (boundary smoothness, small-lesion suppression or inclusion habits); a model trained on those labels can inherit exactly those conventions, and the benchmark then partially rewards fidelity to the draft algorithm.",
      "use_vs_association": "Stage 1 is model-free description. Stage 2 separates use from association by restricting to disagreement voxels, where the training-label signal G and the draft convention D point in opposite directions: a model merely fitting its labels should side with G on held-out cases; systematic siding with D against evidence-matched baselines indicates inherited conventions. An external stroke model never trained on ISLES'24 labels serves as the shared-inductive-bias control.",
      "keystone_prerequisite": "The correction field is recoverable: the initializing segmenter is public and re-runnable on released follow-up MRI, so draft-versus-final disagreement can be computed per case.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "arXiv 2408.10966v1 (inspected 2026-08-18): 'Lesion masks are derived from DWI images using the ISLES'22 ensemble algorithm. Quality control and correction of the lesion masks are performed when needed by medical students (TAB, HPM) supervised by two neuroradiologists (JSK, BW) with more than 10 years of experience.' github.com/ezequieldlrosa/DeepISLES (inspected): the ISLES'22 ensemble is released with Docker image isleschallenge/deepisles and Zenodo weights (version 14026715); required inputs DWI (b=1000) and ADC, FLAIR 'Required for ensemble (optional for single algorithm outputs)'. zenodo.org/records/16731717 (inspected): each training case includes follow-up 'post-treatment MRI (DWI and ADC)'; 149 cases public.",
      "keystone_residual_assumption": "That the released DeepISLES version approximates the draft actually used: the initializing version/weights are not stated anywhere inspected, and if organizers ran the FLAIR-using ensemble, a DWI/ADC-only rerun differs. High verbatim agreement is version-robust evidence of imprint; LOW agreement is ambiguous between heavy correction and version drift — this asymmetry is prespecified in the analysis, and the weights-release date versus dataset-creation chronology is a stage-0 check.",
      "rung_reached": "0; rung 1 after stage-2 disagreement-voxel analysis with the external-model control; rung 2 after two-family, two-center replication.",
      "dies_like_prior": "Closest to ideas 002 and 005 (annotation provenance undocumented). It differs decisively: here provenance IS documented in the challenge paper, the initializer is a released artifact, and the provenance effect is the measurand rather than an unverifiable assumption. What it cannot do is separate expert anchoring on the draft from genuine agreement with it — stated as a limit, not assumed away.",
      "closest_prior_work": "Label-error and annotation-style work (Zhang et al., Disentangling human error from ground truth, NeurIPS 2020, arXiv 2007.15963; annotation-style effects, arXiv 2210.17398) models rater noise but does not measure AI-initialized draft imprint in a public benchmark. The DeepISLES paper (Nature Communications 2025) validates the segmenter, not its imprint on ISLES'24 ground truth. No located work runs this audit on ISLES'24; novelty confidence remains limited-search.",
      "existing_assets": "All required artifacts are public: 149 cases with follow-up DWI/ADC and GT masks (Zenodo 16731717), DeepISLES container plus weights, nnU-Net training recipes, official evaluation code (utils/eval_utils).",
      "smallest_decisive_experiment": "Stage 1 alone is decisive as a dataset-quality finding: run DeepISLES on all 149 released follow-up DWI/ADC, compute Dice(D,G), bitwise-identical fraction, and boundary distances, stratified by center; prespecify a report of the uncorrected fraction. About 2-3 days including download, under 10 GPU-hours. Stage 2 (train one nnU-Net, analyze held-out disagreement voxels with the external-model control) adds about two weeks.",
      "standing_confounds_addressed": "Scanner/site enter D-G agreement through MRI quality — stratified by center. Genuine boundary ambiguity (both draft and expert defensible) is quantified with a boundary-band analysis. The design does not rule out expert anchoring on the draft (automation bias), which would make even 'corrected' voxels draft-tinted — acknowledged as an unremovable ceiling on interpretation. Label leakage is inverted here: labels are the object of study, and the stage-1 readout needs no trusted labels at all.",
      "alternative_explanations": ["Models side with the draft because CNNs share inductive biases with DeepISLES, not because of label inheritance — the external never-trained-on-ISLES'24 model control discriminates this.", "Low draft-GT agreement reflects DeepISLES version drift rather than extensive correction — prespecified asymmetric interpretation and chronology check.", "Disagreement voxels are simply hard voxels — evidence-matched baselines within the same case address this."],
      "anticipated_negative": "Decisive for stage 1: any measured uncorrected fraction is a benchmark fact of record either way. For stage 2, a null after the external-model control passes is a valuable reassurance that the hybrid annotation pipeline did not measurably contaminate model behavior on this benchmark.",
      "cross_domain": {"borrowed_construct": "Automation bias/anchoring from human-factors research: reviewers correct machine drafts less than they should.", "measurement_it_implies": "The surviving-draft fraction and draft-siding rate in overridden voxels as anchoring indices.", "what_changes_if_dropped": "Nothing mechanical — the study remains a label-provenance audit; the human-factors frame only supplies the interpretation of high uncorrected fractions."},
      "remaining_legwork": "Archive download and DeepISLES container runs: 2-3 days to the stage-1 decision; one nnU-Net training plus disagreement analysis: about two weeks to the stage-2 decision.",
      "design_template": "cross-model-disagreement",
      "entry_point_2_requirements": "Measurement: draft-agreement statistics and draft-siding rate in expert-overridden voxels. Confused artifact: shared CNN inductive bias producing draft-like outputs without label inheritance; controlled by the external-model comparison and evidence-matched baselines.",
      "scores": {
        "clarity": {"value": 5, "why": "Two prespecified stages, each with an explicit quantitative readout and a named control."},
        "identifiability": {"value": 3, "why": "Stage 1 is descriptive and clean; stage 2's inheritance claim survives the external-model control but cannot exclude expert anchoring, which is stated as a ceiling."},
        "medical_relevance": {"value": 4, "why": "Every model ranked on ISLES'24 inherits this ground truth; deployment claims trained on it inherit whatever imprint exists."},
        "interest": {"value": 5, "why": "Either answer is consequential for the whole challenge community: substantial algorithmic ground truth, or a documented reassurance that the hybrid pipeline is sound."},
        "prior_legwork": {"value": 5, "why": "Initializer, weights, follow-up images, masks, and evaluation code are all released; nothing must be built except analysis."},
        "feasibility": {"value": 4, "why": "Keystone inspected true; stage 1 is days of container inference on public data."},
        "data_readiness": {"value": 4, "why": "Fully public under CC BY-NC-SA; the archive is large but hosted on Zenodo."},
        "evaluation_readiness": {"value": 3, "why": "Agreement metrics are standard; imprint and draft-siding statistics are custom and need preregistration."},
        "negative_result_value": {"value": 4, "why": "A low uncorrected fraction plus a stage-2 null is a citable benchmark-integrity result, not a dead end."},
        "novelty_confidence": {"value": 3, "why": "Targeted search found adjacent label-noise literature but no ISLES'24 audit; search was not exhaustive."},
        "regret": {"value": 5, "why": "The audit is cheap, uses only released artifacts, and the community will eventually ask this question of any hybrid-annotated benchmark."}
      },
      "priority_score": 4.1,
      "unverified_claims": ["the DeepISLES version used for initialization matches the released weights", "the fraction of uncorrected masks is large enough to matter", "an adequate external stroke model exists for the shared-bias control", "novelty beyond targeted search"],
      "plain_pitch": "The 'correct answers' in this stroke benchmark were first drawn by an algorithm and only fixed by humans when someone judged it necessary. Because that drafting algorithm is public, we can redraw every answer and measure exactly how much of the official truth is uncorrected machine output — and then test whether models trained on it learn the drafting algorithm's habits instead of the biology. Either result matters: a large imprint would change how the benchmark's rankings are read, and a small one would be documented reassurance."
    },
    {
      "id": "isles24-scout-004-c02",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "Does the model bring a vascular map to the scan?",
      "question": "Is an ISLES'24 final-infarct model using arterial-territory membership — the brain's vascular map — as a spatial prior beyond the case's own perfusion and tissue evidence?",
      "rung": "Target rung 1: use of atlas-defined territory membership; rung 2 requires replication in a second model family and demonstration on anatomically variant cases where prior and evidence dissociate.",
      "deliverable_sentence": "The final-infarct model is using arterial-territory membership — the brain's vascular map — as a spatial prior, producing prediction discontinuities at territory borders between voxels with matched local evidence.",
      "X_measurement": "Register the public digital arterial-territories atlas (Liu et al., Scientific Data 2023, DOI 10.1038/s41597-022-01923-0; github.com/Chin-Fu-Liu/Arterial_Atlas) to each NCCT with standard deformable registration; X is territory membership and signed distance to the territory border per voxel. Compute-today test: YES on any unseen head CT with public atlas and registration tools; no annotator.",
      "suspected_signal": "Emboli follow arterial trees, so real infarcts are territorial; a segmentation network trained on territorial masks can internalize the territory shapes themselves and apply them as a prior. Physicians reason territorially and would want to know whether the model does too — helpful as anatomical plausibility, harmful if the prior overrides case evidence in patients with variant vascular anatomy.",
      "use_vs_association": "Association predicts model output varies smoothly with local hemodynamic evidence; use of a map predicts a jump located exactly at an externally registered anatomical boundary between voxels matched on all released evidence channels. Placebo boundaries (shifted 5-10 mm), contralateral boundaries, and matching on Tmax/CBF/CBV/MTT/NCCT-HU/distance-to-core carry the distinction.",
      "keystone_prerequisite": "A frozen trained final-infarct model with continuous per-voxel output and non-trivial held-out performance exists, and atlas-to-CT registration is accurate to a few millimeters so border-straddling matched pairs are real.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The verified nearby fact is that the atlas is public and covers territories hierarchically; the load-bearing facts — reproduced-model quality and registration accuracy on defaced stroke CT — are the actual stage-0 gates. Matching can only use released evidence channels; unreleased raw-CTP cues correlated with true borderzone physiology remain possible and cap the identifiability score.",
      "rung_reached": "0; rung 1 after the discontinuity analysis with placebo and registration-perturbation gates; rung 2 after a second model family and variant-anatomy cases.",
      "dies_like_prior": "Nearest killed relative is idea-020 (spreading front, IDENTIFIABILITY_FAILURE). Differences: no synthetic intervention is required, the readout is a boundary discontinuity with built-in placebo cutoffs and contralateral controls, and the dominant confound (genuine watershed hemodynamics) is explicitly handled by matching on every released hemodynamic channel plus a prespecified sensitivity band; if matching quality fails its own gate, the result is reported as unidentifiable rather than reinterpreted.",
      "closest_prior_work": "The atlas itself (DOI 10.1038/s41597-022-01923-0) and deliberate atlas-prior segmentation methods exist; Robben et al. (Medical Image Analysis 2020, DOI 10.1016/j.media.2019.101589) predict final infarct from native CTP without auditing spatial priors. No located work tests for emergent territorial priors in stroke models via boundary discontinuity; novelty is unaudited beyond targeted search.",
      "existing_assets": "Public atlas with hierarchical territories, 149 public multimodal cases, registration toolchains (ANTs), nnU-Net recipes, and a label-free readout requiring only model probability maps.",
      "smallest_decisive_experiment": "On 30 held-out cases of one trained nnU-Net: extract about 10^4 border-straddling voxel pairs matched on the five released evidence channels plus distance-to-core; estimate the output discontinuity with patient-clustered bootstrap CIs; compare against 20 placebo borders per case and contralateral borders; registration-perturbation sensitivity analysis. Decision in 3-4 days after model training; under 5 GPU-hours of inference.",
      "standing_confounds_addressed": "Within-case matched pairs fix scanner, vendor, protocol, site, positioning, habitus, prevalence, and referral. Registration error blurs true jumps (conservative for a positive claim, threatening for a null — handled by the perturbation gate). NOT ruled out: model access to unreleased or raw-image correlates of true borderzone physiology at the border; this is the candidate's honest identifiability ceiling. Labels never enter the primary readout.",
      "alternative_explanations": ["Genuine watershed hemodynamics differ at borders in ways the released maps do not fully capture — the main residual, stated and scored.", "Registration is systematically biased at borders — perturbation and contralateral analyses bound this.", "The model produces edges everywhere — placebo borders quantify generic edge behavior."],
      "anticipated_negative": "Decisive given the power and registration gates: the model integrates evidence smoothly with no detectable anatomical prior — directly reassuring for patients with variant vascular anatomy. Sensitivity-limited if registration QA fails its gate.",
      "cross_domain": {"borrowed_construct": "Regression discontinuity design from econometrics: units just across a cutoff are exchangeable, so a jump at the cutoff identifies the effect of cutoff-assigned treatment.", "measurement_it_implies": "A discontinuity estimate in predicted probability at the registered territory border, with placebo cutoffs and bandwidth sensitivity as validity checks.", "what_changes_if_dropped": "The analysis degrades to an ad-hoc matched boundary contrast without the placebo-cutoff and bandwidth discipline that makes the jump interpretable; the question survives but the inferential guarantee weakens."},
      "remaining_legwork": "2 days atlas-to-CT registration QA census, 4-6 days model training (shared with other candidates), 2 days discontinuity analysis: about 10 days to first decision.",
      "design_template": "conditional-observational",
      "entry_point_2_requirements": "Measurement: output discontinuity at registered arterial-territory borders under matched local evidence. Confused artifact: real watershed hemodynamics and registration error; placebo borders, five-channel matching, and registration perturbation address them.",
      "scores": {
        "clarity": {"value": 4, "why": "One question, one estimand (the boundary jump), though matching bandwidths need preregistration."},
        "identifiability": {"value": 3, "why": "Placebo cutoffs rule out generic edge behavior, but unreleased borderzone physiology correlated with the border cannot be fully excluded."},
        "medical_relevance": {"value": 4, "why": "An atlas prior that overrides case evidence is a concrete safety issue for variant anatomy; its absence is equally reportable."},
        "interest": {"value": 4, "why": "Whether segmentation models internalize vascular anatomy is a recognizable open question phrased at physician level."},
        "prior_legwork": {"value": 4, "why": "Atlas, registration tools, and model recipes exist; only the trained audit model is missing."},
        "feasibility": {"value": 3, "why": "Capped: the trained-model and registration keystones are not inspected."},
        "data_readiness": {"value": 4, "why": "All inputs public; atlas registration to defaced CT is untested but standard."},
        "evaluation_readiness": {"value": 3, "why": "The discontinuity estimator with placebo cutoffs is custom though statistically standard."},
        "negative_result_value": {"value": 3, "why": "A gated null is meaningful (no atlas prior) but conditional on registration and power gates."},
        "novelty_confidence": {"value": 3, "why": "Targeted search found no emergent-prior audit; not exhaustive."},
        "regret": {"value": 4, "why": "Cheap, label-free, and the RDD grammar is reusable across the portfolio if it works."}
      },
      "priority_score": 3.5,
      "unverified_claims": ["deformable atlas registration achieves few-mm accuracy on defaced stroke CT", "a reproduced model reaches non-trivial held-out performance", "matched pairs exist in sufficient numbers near borders", "novelty beyond targeted search"],
      "plain_pitch": "Strokes tend to respect the borders of each artery's supply zone, and doctors carry that vascular map in their heads. This study asks whether the prediction model carries the same map — whether its predicted damage jumps exactly at map borders even when two neighboring tissue spots look hemodynamically identical. If yes, the model imposes anatomy textbook knowledge on individual patients, which is reassuring for typical anatomy but risky for the many people whose vessels deviate from the textbook."
    },
    {
      "id": "isles24-scout-004-c03",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "The heart's signature in the head scan",
      "question": "Is a native-CTP final-infarct model using systemic contrast transit time — the arm-to-brain bolus delay that lengthens when cardiac output falls — as a patient-level severity signal beyond the local perfusion deficit?",
      "rung": "Target rung 1: use of global bolus timing; rung 3 language about cardiac performance would require an external cohort with measured cardiac function and is explicitly out of scope here.",
      "deliverable_sentence": "The final-infarct model is using systemic contrast transit time — the arm-to-brain bolus delay — as a patient-level severity signal.",
      "X_measurement": "From the released CTP resampled at 1 frame/second, automatically select the arterial input function and venous output function (standard components of every deconvolution pipeline) and compute X = bolus arrival delay (series start to AIF onset/peak) with recirculation timing as a secondary quantity. Compute-today test: YES — deterministic curve analysis on the released 4D series, no annotator.",
      "suspected_signal": "Reduced cardiac output (heart failure, atrial fibrillation — the leading stroke etiologies) prolongs arm-to-brain transit and simultaneously lowers collateral perfusion pressure, accelerating penumbra loss. Arrival delay is therefore both readable in the image and plausibly prognostic, and a network consuming the native time series may exploit it as a systemic-state covariate that perfusion maps discard (delay-insensitive deconvolution removes global arrival time by construction).",
      "use_vs_association": "Within-case, shape-preserving re-indexing of the time axis (shift the entire real frame sequence by +/-2, 4, 6 s within measured baseline/tail slack) changes global arrival time while leaving every local perfusion relationship untouched; a monotone signed output response isolates use of global timing. Mere association of delay with severity predicts zero response, because no local evidence changes.",
      "keystone_prerequisite": "Released 4D CTP retains enough pre-bolus baseline and post-venous-return tail on enough cases to permit +/-4 s shifts without truncating the bolus, and a native-CTP final-infarct model (Robben-recipe) can be trained to non-trivial held-out performance on 149 cases.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The verified nearby fact is the uniform 1 frame/second resampling (time axis well defined); the load-bearing facts — per-case baseline/tail slack and trainability of a 4D model at this cohort size — require the download-and-train stage 0. The claim is also scoped to native-CTP models: map-consuming models plausibly never see arrival time, and a null there would be trivial.",
      "rung_reached": "0; rung 1 after slack census, positive-control gate, and monotone dose-response; higher rungs need external cardiac-function data.",
      "dies_like_prior": "Adjacent to paused idea-022 (model mistaking scan end for bolus end) and superficially to killed idea-024 (DATA_ACCESS). Differences from 022: this is a positive-X question (systemic timing as signal), not a truncation-confound audit; it budgets training its own Robben-recipe model rather than waiting for a released checkpoint; and its intervention is gated to keep the full bolus inside the window precisely to avoid the truncation interaction 022 identified. Unlike 024, every required input is in the public release.",
      "closest_prior_work": "Robben et al. (Medical Image Analysis 2020, DOI 10.1016/j.media.2019.101589) trained final-infarct models directly on native CTP plus metadata and showed metadata mattered, but never tested bolus-timing use. Clinical literature associates heart failure and AF with worse stroke outcome (association only). No located model-use test of systemic transit time; novelty unaudited.",
      "existing_assets": "Released raw and 1 fps-resampled 4D CTP for 149 cases, published native-CTP model recipe, standard AIF/VOF selection algorithms, released age/history tabular data for descriptive covariance.",
      "smallest_decisive_experiment": "Stage 0 census without any training: compute per-case AIF onset, baseline frames, and post-VOF tail across 149 cases; require >=40 cases with >=6 s slack on both sides; report the site-stratified arrival-delay distribution and its association with released outcome variables (descriptive). Census decision in about 3 days after download. Full experiment: train one Robben-recipe model, apply the shift ladder plus baseline-permutation shams on 30 slack-verified held-out cases; about 3 weeks total.",
      "standing_confounds_addressed": "The within-case shift fixes scanner, site, protocol, injector settings, habitus, prevalence, and referral by construction; site injection protocols confound only the observational census (stratified, not causal). Motion correction and resampling were applied uniformly by organizers. Scan-end truncation interaction is excluded by the slack gate. Labels never enter the primary paired readout.",
      "alternative_explanations": ["The model reacts to frame-edge padding artifacts rather than timing — baseline-only permutation shams that move no bolus discriminate this.", "The model uses arrival delay as a deconvolution/site artifact proxy rather than systemic state — rung-1 wording claims use of timing only; cardiac attribution is explicitly prohibited without external validation.", "A 4D model this small overfits and responds incoherently — the positive-control gate (response to a perturbation it must detect) precedes interpretation."],
      "anticipated_negative": "Sensitivity-limited before gates; after slack and positive-control gates, a null says native-CTP models ignore globally available systemic timing — a useful entry in the maps-versus-native-input debate, since timing is exactly what maps discard.",
      "cross_domain": {"borrowed_construct": "Circulation time from cardiovascular physiology: arm-to-brain indicator transit was a bedside cardiac-function test decades before CT.", "measurement_it_implies": "AIF arrival delay as an indicator-dilution circulation-time surrogate.", "what_changes_if_dropped": "Without the physiology, the experiment is a bare robustness check to time shifts with no clinical payoff and should be killed."},
      "remaining_legwork": "Download plus timing census: ~3 days to the stage-0 decision; 4D model training and shift ladder: ~3 weeks to the use decision; largest compute item in this cycle (rough order 100 GPU-hours).",
      "design_template": "other:temporal-reparameterization",
      "design_template_justification": "No voxel content is synthesized or substituted; only the time index of real acquired frames changes. Calling it counterfactual-synthesis (already 8x concentrated in the portfolio) would misdescribe the intervention and the homogenization statistics.",
      "entry_point_2_requirements": "Measurement: automated AIF/VOF arrival delay and recirculation timing. Confused artifacts: site injection protocol and scan-start conventions (stratified; the within-case intervention is immune) and scan-end truncation (slack gate).",
      "scores": {
        "clarity": {"value": 4, "why": "One scalar X, one signed intervention ladder, prespecified gates."},
        "identifiability": {"value": 3, "why": "The within-case shift is clean, but padding shams and the truncation interaction must carry real weight."},
        "medical_relevance": {"value": 4, "why": "Whether models read systemic circulatory state from a head scan bears on cardiac comorbidity handling in stroke triage."},
        "interest": {"value": 4, "why": "Perfusion maps mathematically discard arrival time; showing a native model uses it would sharpen the maps-versus-native debate."},
        "prior_legwork": {"value": 3, "why": "The model recipe is published but no public checkpoint was verified; timing tools are standard."},
        "feasibility": {"value": 2, "why": "Requires training a 4D model on 149 cases; the heaviest candidate this cycle even before the cap."},
        "data_readiness": {"value": 3, "why": "Public, but the 4D series is the largest download and slack is unverified."},
        "evaluation_readiness": {"value": 3, "why": "Paired output change is direct; gates are custom."},
        "negative_result_value": {"value": 3, "why": "Interpretable only after the positive-control gate; then genuinely useful."},
        "novelty_confidence": {"value": 3, "why": "Targeted search only."},
        "regret": {"value": 3, "why": "Worth doing, but the model asset cost is real and shared bottleneck risk with idea-022 is acknowledged."}
      },
      "priority_score": 3.15,
      "unverified_claims": ["per-case baseline/tail slack sufficiency", "trainability of a native-CTP model at n=149", "arrival delay varies meaningfully across this cohort", "cardiac-output-to-arrival-delay strength in this setting", "novelty beyond targeted search"],
      "plain_pitch": "When the heart pumps weakly, injected contrast dye takes noticeably longer to travel from the arm to the brain, and that delay is written into the scan's timeline. This study asks whether a model that reads the raw time series uses that delay — effectively reading the patient's heart performance from a head scan — when forecasting the final stroke damage. The test shifts the whole timeline of real frames a few seconds without changing anything local; if predictions move in step with the shift, the model is using the timing signal."
    },
    {
      "id": "isles24-scout-004-c04",
      "parent_ids": [],
      "search_mode": "C",
      "entry_point": 2,
      "title": "The model may be watching the patient's eyes",
      "question": "Is an ISLES'24 final-infarct model using conjugate gaze deviation — which way the patient's eyes point in the scanner — as a stroke-severity signal?",
      "rung": "Mode C target rung 1: use of the image-computable gaze angle; rung 3 language about the model reading examination-grade neurology would require external validation against documented clinical gaze findings.",
      "deliverable_sentence": "The final-infarct model is using conjugate gaze deviation — the direction the patient's eyes point — as a severity signal when predicting final infarct.",
      "X_measurement": "Automatically segment globes and lenses (TotalSegmentator head_glands_cavities task: eye_left/right, eye_lens_left/right) and compute the 3D conjugate gaze vector and deviation angle; an AI 3D implementation exists (conjugate gaze adjusted length, CGAL) that correlated with NIHSS at r=0.72 and identified acute ischemic stroke with sensitivity up to 91% (PMC7717852). Compute-today test: YES on any head CT whose orbits are intact — which is precisely the keystone, not the tool.",
      "suspected_signal": "Acute injury or hypoperfusion of the frontal eye fields and attention network drives sustained conjugate deviation toward the lesioned hemisphere — Prevost's sign, present in over half of admission CTs in acute ischemic stroke per the CGAL literature and an NIHSS examination item ('best gaze'). The orbits sit inside the head-CT field of view, so a whole-head 3D network can read a behavioral severity-and-laterality marker no one intended to give it.",
      "use_vs_association": "Within-case orbit-only substitution: replace orbital content with the same patient's mirror-neutralized orbits and apply graded globe rotations as a dose-response, leaving brain, vessels, skull, and perfusion untouched; output change under orbit-only edits, monotone in rotation angle, with null response to equal-volume extraorbital shams, isolates use. Association (gaze correlates with severity) predicts zero edit response.",
      "keystone_prerequisite": "Globes and lenses are present and geometrically intact in the released defaced NCCT/CTP, and the audited model's input crop includes the orbits.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The documented facts cut both ways: scans are 'defaced based on brain and face masks obtained with TotalSegmentator' (arXiv 2408.10966v1), and the TotalSegmentator README describes the removed class only as 'face_region (for anonymization)' with no statement on globes. Additionally the winning team skull-strips with SynthStrip (arXiv 2505.18424), so the claim is scoped to whole-head-input models, possibly only ones this program trains. All three assumptions are checkable in one hour on three downloaded cases — the honest Mode C posture is to declare, not guess.",
      "rung_reached": "0; rung 1 after the orbit-intactness gate, receptive-field/crop gate, and the substitution dose-response.",
      "dies_like_prior": "Closest process-relative is idea-007, which advanced on a claimed model output that did not exist. The analogous fatal fact here (orbits absent from the release) is named up front with a one-hour stage-0 check rather than discovered in critique. No annotation-provenance dependence: the primary readout is label-free paired output change.",
      "closest_prior_work": "The CGAL paper measures 3D gaze on CT with AI and links it to stroke presence and NIHSS (PMC7717852); visually determined CT eye deviation predicts stroke-code diagnosis (PMID 27576212) and admission eye deviation is associated with larger stroke volumes and 3-month disability (Clinical Radiology, DOI 10.1016/j.crad.2016.06.113 record S0009-9260(16)30320-8). None asks whether a lesion-prediction model reads gaze. Novelty unaudited beyond targeted search.",
      "existing_assets": "Public NCCT/CTP with orbits possibly intact, TotalSegmentator eye/lens classes, published CGAL measurement construct, label-free paired readout, and this program's planned shared audit model.",
      "smallest_decisive_experiment": "Stage 0: download three cases and inspect orbit integrity plus model-crop coverage (one hour after download). If passed: compute gaze angles on all 149 cases (half a day) and report the distribution against the published >55% prevalence; then orbit-neutralization plus graded-rotation edits on 30 held-out cases with the shared whole-head model — about one week after model availability, under 10 GPU-hours.",
      "standing_confounds_addressed": "Within-case edits fix scanner, site, protocol, positioning, habitus, prevalence, and referral. Head rotation versus true gaze deviation is the measurement confound: the edit rotates globes within a fixed head, separating the two by construction. Sedation or eye closure adds noise, not bias, to the paired test. Labels never enter the primary readout.",
      "alternative_explanations": ["The model responds to any orbital edit — equal-magnitude extraorbital shams and the monotone dose-response discriminate artifact from signal.", "The model reads head positioning rather than gaze — fixed-head globe rotation separates them.", "The model never sees the orbits (crop or stripping) — an early architecture/crop gate; a null without it is uninterpretable, hence the capped negative-result score."],
      "anticipated_negative": "Uninterpretable if the orbit-intactness or crop gate fails; after gates, sensitivity-limited (models may downweight extracranial voxels); negative-result value capped at 2 accordingly.",
      "cross_domain": {"borrowed_construct": "Bedside behavioral neurology: gaze preference as a physical-examination severity sign (NIHSS item 2).", "measurement_it_implies": "An image-computable 3D gaze angle as an imaging surrogate of an examination finding.", "what_changes_if_dropped": "Without the examination-sign frame this becomes an arbitrary far-field sensitivity test and should be killed."},
      "remaining_legwork": "One hour to the keystone verdict after download; half a day for the cohort gaze census; one week to the use decision after the shared model exists.",
      "design_template": "regional-substitution",
      "design_template_justification": "Shares the substitution skeleton with c05 by necessity; they differ in object (acute behavioral sign in the orbits versus chronic demographic marker at the midline), readout (vector-valued rotation dose-response versus scalar physiologic-range dose), and failure mode probed (severity-proxy shortcut versus demographic-fairness shortcut). Both are retained because each is the natural minimal test of its X.",
      "entry_point_2_requirements": "Measurement: 3D conjugate gaze angle from automated globe/lens segmentation. Confused artifacts: head rotation/positioning and defacing damage; fixed-head globe rotation, head-pose-adjusted geometry, and the stage-0 orbit inspection address them.",
      "scores": {
        "mechanism_clarity": {"value": 5, "why": "A specific neuro-ophthalmological mechanism (frontal eye field involvement drives ipsilesional deviation) with a named, published, automated measurement."},
        "identifiability": {"value": 4, "why": "Orbit-only edits with rotation dose-response and extraorbital shams isolate the cue unusually cleanly if the data survive defacing."},
        "interest": {"value": 5, "why": "A tissue-segmentation model reading the patient's gaze would genuinely surprise both communities; the null after gates is also tellable."},
        "medical_relevance": {"value": 3, "why": "Gaze is a real severity signal, so use is not an artifact — but it means the model reads behavior rather than tissue, which matters for portability and trust."},
        "clarity": {"value": 5, "why": "One sign, one angle, one graded within-case intervention."},
        "prior_legwork": {"value": 4, "why": "Automated 3D gaze measurement and its clinical correlations are published; only the audit is new."},
        "feasibility": {"value": 2, "why": "Reported outside the Mode C score: the defacing keystone may kill it in the first hour, and a whole-head model must exist."},
        "data_readiness": {"value": 3, "why": "Public data, but orbit survival is the open question."},
        "evaluation_readiness": {"value": 3, "why": "Paired readout is direct; edit-validity gates are custom."},
        "negative_result_value": {"value": 2, "why": "Capped: a null is uninterpretable unless the crop and intactness gates pass."},
        "novelty_confidence": {"value": 2, "why": "Targeted search only, in a literature this program knows less well."},
        "regret": {"value": 4, "why": "The keystone check costs an hour; if the eyes survived defacing, this is the cheapest memorable use-test in the portfolio."}
      },
      "mode_c_priority_score": 4.45,
      "unverified_claims": ["globes/lenses survive TotalSegmentator-based defacing in the release", "audit-model crop includes orbits", "gaze-deviation prevalence in this cohort matches published rates", "edit realism of rotated orbital content", "novelty"],
      "plain_pitch": "Stroke patients' eyes often drift toward the damaged side of the brain — an old bedside sign that also shows up on the CT scan, where an existing automated tool can measure it. This speculative study asks whether the damage-forecasting model has quietly learned to glance at the patient's eyes as a severity cue. The whole idea lives or dies on one cheap check: whether the anonymization step that removes faces from the public scans spared the eyes; if it did, rotating only the eyes in the image and watching the forecast move would be the demonstration."
    },
    {
      "id": "isles24-scout-004-c05",
      "parent_ids": [],
      "search_mode": "C",
      "entry_point": 2,
      "title": "The brain's odometer: calcification as the model's age gauge",
      "question": "Is an ISLES'24 final-infarct model using physiologic intracranial calcification — the pineal, habenular, and choroid plexus calcium that accumulates with age — as an age gauge that scales its infarct forecast?",
      "rung": "Mode C target rung 1: use of the calcification cue; rung 3 language ('the model estimates age') would require representation-level age probes and an external cohort, out of scope here.",
      "deliverable_sentence": "The final-infarct model is using physiologic midline and choroid plexus calcification as an image-derived age gauge when predicting final infarct.",
      "X_measurement": "Atlas-localize pineal, habenular, and choroid plexus ROIs on NCCT; X = calcified volume and Agatston-style mass (HU >= 130) per structure — deterministic, no annotator. The age link is documented: physiologic intracranial calcifications are present in 50-70% of adults over 30 and prevalence rises with age; an 11,941-subject NCCT study reports choroid plexus calcification in 70.2% and pineal in 71.6% (ScienceDirect S0891061816300783; corroborated by 18F-NaF PET/CT, J Nucl Med 60:267). Compute-today test: YES on any unseen NCCT with an atlas and HU arithmetic.",
      "suspected_signal": "Pineal and choroid plexus calcification accumulates roughly monotonically with age; age in turn tracks collateral quality, white-matter vulnerability, and infarct evolution. These calcifications are bright, stereotyped, midline landmarks — exactly the kind of cue a network can learn as a demographic shortcut, giving older-looking brains systematically different forecasts at matched physiology.",
      "use_vs_association": "Within-case graded editing of only calcification voxels (remove, halve, intensify within the cohort's measured per-structure HU/volume range) in structures remote from the ischemic territory, all else fixed; a monotone signed response of the predicted infarct in the threatened territory, with null response to equal-HU edits at matched non-calcification control sites, isolates use of the cue. Association with age predicts zero edit response.",
      "keystone_prerequisite": "Physiologic calcifications are reliably quantifiable in the released resampled NCCT (resolution and HU fidelity) and vary enough across 149 cases to be learnable (calcified volume correlates with released age, target Spearman >= 0.3).",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The prevalence and age-association literature is from clinical native NCCT, not from ISLES'24 derivatives; resampling may blur small calcifications and quantitative HU integrity of the release is unverified (cycle-003 flagged the same concern for blood HU). Even with the cue verified quantifiable, the claim stops at 'uses the cue' — attributing an age prior needs the descriptive age-covariance analysis in the released demographics and is supporting, not proving.",
      "rung_reached": "0; rung 1 after the learnability census and the graded remote-edit response with control sites.",
      "dies_like_prior": "Cycle 003 dropped carotid-siphon calcification because no within-case edit could separate 'chronic cerebrovascular reserve' from 'age and systemic burden.' This card dissolves that objection instead of fighting it: age-proxy use IS the claim, so no separation is attempted; the burden moves to edit realism and remoteness, both explicitly gated. Distinct from 003-c04 (dural sinus HU as oxygen gauge — different structures, different construct) and 001-c04 (parenchymal frailty features).",
      "closest_prior_work": "Shortcut-learning literature shows radiology models recover demographics (age, sex, race) from images and can use them as prediction shortcuts; brain-age estimation is established for MRI. The calcification-age association is documented (S0891061816300783). No located work tests whether stroke final-infarct models read physiologic calcification as a demographic cue; novelty unaudited beyond targeted search.",
      "existing_assets": "Public NCCT with released patient age in demographics, deterministic HU-threshold measurement, atlas localization tools, the program's shared audit model, and a label-free paired readout.",
      "smallest_decisive_experiment": "Stage 0 census on 149 NCCTs: detectable pineal/choroid calcification rates versus published prevalence, calcified volume versus released age (gate: Spearman >= 0.3), test-retest under one-voxel erosion. If passed: three-dose remote edits plus control-site shams on 40 held-out cases; about one week after the shared model exists, under 10 GPU-hours.",
      "standing_confounds_addressed": "Within-case edits fix scanner, vendor, protocol, site, positioning, habitus, prevalence, and referral; edit realism is gated by staying inside cohort-measured per-structure distributions. NOT excluded: the model may respond to any bright midline change (control sites address but cannot eliminate), and calcification may proxy vascular pathology rather than age alone — the claim wording stays at cue-use for exactly this reason. Labels never enter the primary readout.",
      "alternative_explanations": ["Response to arbitrary bright edits — matched control-site shams discriminate.", "Calcification proxies systemic vascular burden rather than age — rung-1 wording claims cue-use only; the age-covariance analysis is reported descriptively.", "The network's receptive field never links midline structures to the threatened territory — early architecture gate, as in c04; a null before it is uninterpretable."],
      "anticipated_negative": "After the learnability and receptive-field gates, a null is a meaningful negative: the model ignores the most explicit age marker in the image, evidence against the demographic-shortcut concern for this model family. Before gates, sensitivity-limited.",
      "cross_domain": {"borrowed_construct": "Shortcut learning and algorithmic fairness: models exploiting demographic proxies invisible in their specification.", "measurement_it_implies": "Dose-response of the forecast to a graded, image-computable demographic marker.", "what_changes_if_dropped": "The probe remains a valid interpretability experiment on a named radiologic structure, but loses the fairness stake that makes the answer matter beyond this dataset."},
      "remaining_legwork": "1-2 days calcification census and age-correlation gate after download; 2 days edit machinery; one week to the use decision after the shared model exists.",
      "design_template": "regional-substitution",
      "design_template_justification": "Shares the substitution skeleton with c04; retained because the two probe different objects (chronic demographic marker versus acute behavioral sign), different readouts (scalar physiologic-range dose versus vector rotation), and different failure modes (fairness shortcut versus severity proxy). See c04 for the paired justification.",
      "entry_point_2_requirements": "Measurement: HU >= 130 calcified volume/mass in atlas-localized pineal, habenular, and choroid plexus ROIs. Confused artifacts: resampling blur and HU quantitative drift (census gate), and generic bright-edit response (control sites).",
      "scores": {
        "mechanism_clarity": {"value": 5, "why": "A specific physical quantity (calcified volume of named structures), its documented age association, and the exact measurement that would show use."},
        "identifiability": {"value": 4, "why": "Remote graded edits with matched control sites isolate the cue; what remains open is the age-versus-vascular-burden naming, which the wording already concedes."},
        "interest": {"value": 4, "why": "A segmentation model reading the brain's odometer is a memorable, checkable instance of demographic shortcut learning."},
        "medical_relevance": {"value": 4, "why": "If forecasts scale with an age proxy at matched physiology, that is a concrete fairness and trust finding for deployment."},
        "clarity": {"value": 4, "why": "One cue family, one dose ladder; the multi-structure ROI set needs preregistration."},
        "prior_legwork": {"value": 3, "why": "Prevalence literature and measurement are ready; the audit model and edit machinery are not."},
        "feasibility": {"value": 3, "why": "Reported outside the Mode C score; simple edits, but hostage to HU fidelity and the shared model."},
        "data_readiness": {"value": 3, "why": "Public NCCT plus released age; derivative HU fidelity unverified."},
        "evaluation_readiness": {"value": 3, "why": "Paired dose-response is direct; realism gates are custom."},
        "negative_result_value": {"value": 3, "why": "A gated null meaningfully bounds the shortcut concern for this family."},
        "novelty_confidence": {"value": 2, "why": "Shortcut-learning literature is large; targeted search only."},
        "regret": {"value": 4, "why": "Cheap census, released age variable, and a fairness-relevant answer either way."}
      },
      "mode_c_priority_score": 4.3,
      "unverified_claims": ["calcifications survive resampling quantifiably", "calcified volume correlates with released age in this cohort", "edit realism within physiologic range", "receptive-field coverage from midline to territory", "novelty"],
      "plain_pitch": "As people age, tiny harmless calcium deposits build up in a few midline brain structures, and they glow brightly on CT — a kind of odometer for the brain. This speculative study asks whether the stroke-outcome model has learned to read that odometer and quietly scale its damage forecast by how old the patient looks. The test is to dial those calcium specks up or down in the image, far from the stroke itself, and watch whether the forecast follows; if it does, the model is using an age proxy, which matters for whether older patients get systematically different predictions from the same physiology."
    }
  ]
}


===== ideas/scout-isles24-004/wide_candidates.json =====
{
  "cycle": "scout-isles24-004",
  "charter": "isles24",
  "date": "2026-08-18",
  "track": "wide",
  "stage_verification_note": "This stage independently re-verified the load-bearing facts it uses. (1) arXiv html 2408.10966v1, fetched 2026-08-18 by this stage: 'all remaining images are registered following rigid transformations. Registration is performed using the Elastix and NiftyReg toolboxes.' and 'Except for the MRI scans, where affine transformations are used'; follow-up imaging 'was acquired 2 to 9 days later and included DWI and ADC.' (2) The same paper and the dataset-paper abstract (arXiv 2408.11142, fetched 2026-08-18) contain NO statement of CTP z-axis coverage, scanner models, or whether CTP covers the whole brain -- recorded as an unresolved dataset fact, decisive for c07 and checkable from released map support masks on three downloaded cases. (3) Two-center composition (train 100 Munich / 50 Zurich) re-confirmed verbatim from 2408.10966v1. (4) Clinical edema time course: peak brain edema at 3-5 days post-stroke is the consensus across Stroke-journal sources (DOI 10.1161/STROKEAHA.114.006884; DOI 10.1161/STROKEAHA.123.045941), overlapping the dataset's 2-9-day follow-up window. All other dataset facts are inherited from this cycle's scout-stage verification recorded in scout_candidates.json (Zenodo 16731717; DeepISLES; icobrain cva preprocessing).",
  "all_questions": [
    {"n": 1, "question": "[digital image forensics -- PRNU camera fingerprinting] Is the model using the scanner-noise fingerprint readable in signal-free voxels -- the CT analogue of camera-sensor forensics -- as a site-identity prior that shifts its infarct forecast?", "disposition": "DEVELOPED as isles24-scout-004-c06."},
    {"n": 2, "question": "[geodesy -- datum shift] Is the model using a swelling-displaced lesion halo, baked into the ground truth by affine-only registration of peak-edema follow-up MRI, rather than acute tissue evidence -- even predicting infarct on voxels that are CSF on the acute scan?", "disposition": "DEVELOPED as isles24-scout-004-c08."},
    {"n": 3, "question": "[remote sensing -- swath coverage] Is the model using the perfusion slab's support boundary -- the edge of the sensor, not the edge of the ischemia -- as a determinant of predicted lesion extent, on a benchmark whose ground truth comes from whole-brain MRI?", "disposition": "DEVELOPED as isles24-scout-004-c07."},
    {"n": 4, "question": "[granular physics -- clogging] Is the model using clot length, the logjam variable that determines recanalization probability, to interpolate between treated-success and treated-failure outcomes in its post-treatment infarct forecast?", "disposition": "DROPPED."},
    {"n": 5, "question": "[chronobiology] Is the model using circadian acquisition-time proxies to encode wake-up-stroke versus witnessed-onset case mix?", "disposition": "DROPPED."},
    {"n": 6, "question": "[nondestructive testing -- artifact metrology] Is the model using posterior-fossa beam-hardening texture as a 'do not trust this region' prior that suppresses cerebellar and brainstem infarct calls?", "disposition": "DROPPED."},
    {"n": 7, "question": "[psychophysics -- Weber's law] Is the model's deficit readout ratio-scaled to the contralateral hemisphere rather than absolute, following Weber-like relative coding?", "disposition": "DROPPED."},
    {"n": 8, "question": "[economics -- rational expectations] Is the model pricing in each center's treatment-success base rate, using site identity as a stand-in for the treatment policy the input images never show?", "disposition": "DROPPED."}
  ],
  "dropped": [
    {"question": "[granular physics -- clogging] Clot length as the recanalization-probability variable the model uses to interpolate between treated and untreated outcomes.", "why": "Same story skeleton as backlog candidate isles24-scout-002-c05 (clot permeability as recanalization predictor read by the model); developing a second X inside that skeleton adds portfolio homogenization, not information -- revisit only if 002-c05 advances and needs a competing clot feature."},
    {"question": "[chronobiology] Circadian acquisition-time proxies encoding wake-up-stroke case mix.", "why": "Acquisition clock time is DICOM metadata, not an image-computable X, and no verified image surrogate for time-of-day exists; fails the charter's hard X-computability constraint."},
    {"question": "[nondestructive testing] Posterior-fossa beam-hardening texture as a regional distrust prior.", "why": "No validated streak-injection simulator exists for the released resampled derivative CT, so the intervention's realism cannot be gated, and an anterior-LVO cohort underpowers posterior-fossa strata -- dies like idea-020 (IDENTIFIABILITY_FAILURE) with no repair this cycle."},
    {"question": "[psychophysics -- Weber's law] Ratio-scaled contralateral deficit coding.", "why": "Duplicates the normalization/reference question inside shortlisted idea-021 (the healthy hemisphere is the ruler); any residual delta belongs in that idea's design space, not a new card."},
    {"question": "[economics -- rational expectations] The model prices in center-specific treatment-success base rates.", "why": "The construct has no image-computable X of its own: any site cue could carry it, so its only testable content is exactly c06's site-fingerprint experiment, and WHAT the model does with site identity is not separately identifiable there; folded into c06's interpretation limits."}
  ],
  "candidates": [
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
        {"work": "Kharboutly, Puech, Subsol, Hoa -- 'CT-Scanner identification based on sensor noise analysis' (EUVIP 2014) and 'Improving sensor noise analysis for CT-scanner identification' (EUSIPCO 2015)", "identifier": "HAL lirmm-01379581 and lirmm-01379558; EUSIPCO 2015 paper 1570103637; found by search 2026-08-18", "relation": "Establishes that individual CT scanners are identifiable from wavelet-Wiener noise residuals -- the measurement instrument this candidate borrows -- but is pure forensics: no clinical prediction model, no use test."},
        {"work": "Zech et al. -- 'Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs' (PLoS Medicine 2018)", "identifier": "DOI 10.1371/journal.pmed.1002683; found by search 2026-08-18", "relation": "Showed CNNs robustly identify hospital system and that this confounds disease prediction -- association and generalization-gap evidence on 2D radiographs, with no intervention isolating the noise channel from anatomy, markers, or population."},
        {"work": "'Name that manufacturer: relating image acquisition bias with task complexity when training deep learning models on head CT'", "identifier": "arXiv 2008.08525; found by search 2026-08-18", "relation": "Shallow CNN classifies scanner manufacturer from head CT and documents acquisition bias in training -- again detectability, not use, and no stroke-outcome model."}
      ],
      "novelty_delta": "No located work tests whether a stroke lesion-outcome model USES the scanner-noise fingerprint, and none anywhere uses a within-case noise-residual transplant between real sites to isolate the noise channel from anatomy, protocol, and population.",
      "why_not_done": "BLIND_SPOT: the forensics community (which owns the fingerprint instrument) and the medical-imaging confounding community (which owns the site-shortcut concern) publish in disjoint venues; site effects are treated as generalization statistics to be harmonized away, not as an isolatable input channel to be use-tested. The two-center, raw-plus-derivative ISLES'24 release makes the transplant experiment newly convenient but not newly possible.",
      "existing_assets": "Public raw and derivative images for 149 cases (Zenodo 16731717); published wavelet-Wiener residual extraction recipes; standard NPS estimation from CT quality assurance; the program's shared audit model planned under this cycle's baseline candidates; official evaluation code.",
      "smallest_decisive_experiment": "Stage 0/1 (decisive for the keystone, model-free): 60 cases stratified 30 per center; extract noise-only patches from raw NCCT, derivative NCCT, and CTP baseline frames; patient-level cross-validated site classifier; prespecified gate: noise-only AUC >= 0.8 on MODEL-FACING derivative inputs (raw-only decodability that dies in preprocessing kills the candidate cleanly). Compute envelope: one Colab GPU session (~15-20 GB download, under 2 GPU-hours; the classifier is minutes). Stage 2 (use test, conditional on the shared audit model): 30 held-out cases x 5 spectral blend doses toward the other site's mean NPS x equal-energy shams, inference only, under 5 GPU-hours -- also one session.",
      "standing_confounds_addressed": "The use test is within-case, fixing anatomy, protocol, positioning, habitus, population, prevalence, and referral by construction. Classifier-reads-anatomy-not-noise is excluded by residual-only patches from homogeneous ROIs after denoising. Transplant artifacts are gated by the sham arm and by evidence-channel invariance checks (bounded per-voxel HU deltas; perfusion maps untouched -- edits apply to image inputs only). Site-versus-vendor attribution is NOT attempted: with two centers, fleet and site are one variable; the claim wording is 'site fingerprint', never 'scanner model'. Labels never enter the primary paired readout.",
      "alternative_explanations": ["The model responds to any high-frequency perturbation, not the site signature -- the equal-energy spectrally-neutral sham and the dose-response monotonicity discriminate.", "Decodability exists in raw data but not in model-facing derivative data -- this is the stage-0 gate, not a post-hoc excuse.", "A positive response reflects general noise-level sensitivity (dose/kernel) rather than site identity -- the blend is toward the other site's measured spectrum at matched total energy, and the classifier-flip manipulation check ties the dose axis to site identity specifically."],
      "anticipated_negative": "After the decodability gate passes, a null is decisive and reassuring: the fingerprint is readable in the inputs, yet the model's forecasts do not move with it -- direct evidence against the site-shortcut concern for this model family on this benchmark. Before the gate, the candidate dies cheaply rather than yielding an uninterpretable null.",
      "cross_domain": {"borrowed_construct": "PRNU sensor-pattern-noise fingerprinting from digital image forensics: every sensor leaves a stable stochastic signature, extractable by denoising residuals, sufficient to identify the source device.", "measurement_it_implies": "The wavelet-Wiener noise residual and its power spectrum as a device/site fingerprint, plus a source-identification classifier as the decodability gauge.", "what_changes_if_dropped": "Without the forensics instrument there is no principled way to separate the stochastic signature from anatomy; the candidate degrades to generic site-generalization statistics, which is exactly the prior art."},
      "remaining_legwork": "Download and decodability census: one session, ~2 days wall clock including Zenodo transfer; spectral-reshaping edit machinery and sham construction: 2 days; use test after the shared model exists: 2 days.",
      "design_template": "other:noise-residual-transplant",
      "design_template_justification": "Closest listed grammars are counterfactual-synthesis (8x concentrated in the portfolio) and regional-substitution (6x); both misdescribe the move: nothing anatomical is synthesized and no region is swapped -- the measured stochastic component of the same real acquisition is spectrally reshaped toward another site's measured statistics, globally, with anatomy untouched. Naming it honestly also keeps the homogenization statistics meaningful.",
      "entry_point_2_requirements": "Measurement: noise-residual site classifier AUC (decodability) and signed paired output change under spectral reshaping (use). Confused artifacts: generic noise-level sensitivity and edit artifacts -- addressed by matched-energy blending, sham permutation, dose-response monotonicity, and the classifier-flip manipulation check.",
      "scores": {
        "clarity": {"value": 4, "why": "One cue channel, one decodability gate, one within-case intervention with prespecified sham and dose gates; the spectral-reshaping recipe needs preregistration detail."},
        "identifiability": {"value": 3, "why": "The within-case transplant cleanly isolates the noise channel, but with two centers the fingerprint cannot be decomposed into hardware versus protocol components, and edit realism carries residual weight despite the sham gate."},
        "medical_relevance": {"value": 4, "why": "A model that conditions infarct forecasts on where the patient was scanned fails silently at new centers; either finding directly informs multi-center deployment and benchmark interpretation."},
        "interest": {"value": 4, "why": "A stroke model reading the hospital's sensor signature the way forensics reads a camera would surprise both the challenge community and forensics; the gated null is also publishable reassurance."},
        "prior_legwork": {"value": 4, "why": "The forensics instrument, NPS tooling, public two-center data, and the shared audit model plan all exist; only the transplant machinery is new."},
        "feasibility": {"value": 3, "why": "Capped at 3: the decodability keystone on model-facing data is not inspected; conditional on the shared audit model like the baseline cards."},
        "data_readiness": {"value": 4, "why": "Fully public raw plus derivative release; large but hosted download."},
        "evaluation_readiness": {"value": 3, "why": "Paired output change is direct, but decodability gates, blend doses, and sham construction are custom and need preregistration."},
        "negative_result_value": {"value": 3, "why": "Interpretable only after the decodability gate; then a genuinely useful negative about a named shortcut channel."},
        "novelty_confidence": {"value": 3, "why": "Neighbors found by real search bracket the idea from both sides (forensics detectability, ML confounding) with the use-test gap clear, but the search was targeted, not exhaustive."},
        "regret": {"value": 4, "why": "The decodability census is nearly free, the question is the portfolio's cleanest instance of the site-shortcut concern, and the instrument transfers to every multi-center benchmark the lab touches."}
      },
      "priority_score": 3.5,
      "unverified_claims": ["site decodability from noise-only patches of derivative model-facing inputs", "the two centers' scanner fleets actually differ (hardware is unstated in all inspected sources)", "spectral reshaping stays within the audit model's in-distribution envelope (sham-gated but not yet shown)", "shared audit model reaches non-trivial performance", "novelty beyond targeted search"],
      "plain_pitch": "Every camera leaves an invisible noise signature in its photos -- forensic examiners use it to prove which device took a picture, and CT scanners have the same property. This stroke benchmark mixes patients from two hospitals with different scanners, and where you were treated is itself informative about how you will fare. The question: has the damage-forecasting model quietly learned to read the scanner's signature and adjust its forecast by hospital? The test swaps only the invisible noise signature in a patient's scan toward the other hospital's, touching nothing about the anatomy, and watches whether the forecast moves. If it does, the model is partly forecasting the hospital, not the patient -- which would matter anywhere such a model is deployed at a hospital it never saw in training."
    },
    {
      "id": "isles24-scout-004-c07",
      "parent_ids": [],
      "track": "wide",
      "entry_point": 2,
      "title": "The edge of the map: the benchmark scores terra incognita",
      "question": "Is an ISLES'24 final-infarct model using the perfusion slab's support boundary -- the edge of the sensor, not the edge of the ischemia -- as a determinant of its predicted lesion extent, on a benchmark whose ground truth comes from whole-brain follow-up MRI?",
      "rung": "Target rung 1: the model's predicted extent is determined by sensor support at matched whole-brain evidence. The model-free stage 1 is itself a benchmark-integrity deliverable regardless of any model.",
      "deliverable_sentence": "The final-infarct model is using the perfusion-acquisition support boundary as a spatial determinant of its predicted lesion extent, truncating or extrapolating at the sensor's edge rather than the ischemia's.",
      "X_measurement": "X is the perfusion support mask and signed distance to its boundary, computed per case from the released perfusion maps (the set of voxels where CBF/Tmax are defined/non-degenerate) and the 4D CTP z-extent, expressed in both patient space and atlas space. Compute-today test: YES -- support masks are arithmetic on released volumes, no annotator.",
      "suspected_signal": "CTP acquisitions on many scanners cover a limited z-axis slab (published protocols range ~40-160 mm), while the ground truth is drawn on whole-brain follow-up MRI; the clinical literature shows coverage-dependent underestimation of ischemic volumes. If slabs in ISLES'24 are narrower than the brain, part of the scored ground truth lies where the primary modality never looked, and every trained model must adopt some convention there -- hard truncation at the sensor edge or hallucinated extrapolation from NCCT/CTA alone. Multi-step story, links separately checkable: models' predictions are shaped by the support boundary (X, stage 2), which matters only if ground-truth lesion mass overflows the support (Y, the model-free stage-1 census), which implies part of the official ranking, including the absolute-volume-difference metric, is decided by an unmeasured out-of-sensor convention (Z, computable as a metric-sensitivity bound in stage 1).",
      "use_vs_association": "Slab placement relative to anatomy is set by scanner hardware and head positioning, not by tissue state, so it varies quasi-randomly across patients: the same atlas location lies in-slab for some patients and out-of-slab for others. A systematic prediction difference at the same anatomical location, conditional on matched whole-brain evidence (NCCT and CTA are full-coverage), attributable to slab membership, shows the output is determined by sensor support rather than by the ischemia; the stage-1 ground-truth-overflow census is model-free and needs no such inference.",
      "keystone_prerequisite": "The released perfusion support is actually narrower than the brain in a non-trivial fraction of cases, and ground-truth lesion mass overflows it in enough cases to matter (prespecified: overflow > 5% of lesion volume in >= 10% of cases).",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Verified nearby facts: neither the challenge paper nor the dataset-paper abstract states CTP z-coverage or scanner hardware (both fetched and checked this stage, 2026-08-18), and the clinical literature documents that limited coverage is common and consequential (Neuroradiology 2014, DOI 10.1007/s00234-014-1429-9: ischemic volume underestimated at 80 mm coverage; AJNR 2010, ajnr.org/content/31/4/691: 70-75 mm needed for MCA territory). The load-bearing fact -- actual slab geometry in this release -- is checkable on three downloaded cases in under an hour, and the full census is trivially cheap. If slabs are whole-brain everywhere, the candidate dies for less than one session's cost.",
      "rung_reached": "0; stage 1 alone delivers a benchmark-integrity fact; rung 1 after the stage-2 conditional analysis on the shared audit model.",
      "dies_like_prior": "Kill-code check: nearest pause is idea-022 (does the model mistake the end of the SCAN for the end of the BOLUS) -- the same 'sensor boundary versus physiology' family but on the time axis, and paused because it needs a frozen raw-4D checkpoint plus training-time masking semantics. c07 differs decisively: its decisive stage is model-free arithmetic on released masks and maps (no checkpoint, no masking semantics), and the spatial support boundary is directly observable per case. It shares the boundary-discontinuity estimator with this cycle's baseline c02 (arterial-territory borders) -- shared statistical tooling, different boundary, different claim (sensor artifact versus anatomical prior); if both advance, the estimator is built once. IDENTIFIABILITY_FAILURE risk (idea-020's death) is confined to stage 2 and is honestly stated: less evidence beyond the slab is rational, so stage 2 measures HOW models behave at the edge, not whether behaving differently is irrational; the quantitative benchmark claim rests on stage 1.",
      "closest_prior_work": "Clinical CTP-coverage literature quantifies volume underestimation from limited slabs; final-infarct deep-learning papers use CTP inputs without reporting support handling; no located work measures ground-truth overflow of the sensor support in ISLES'24 or any public stroke benchmark, nor its effect on rankings. See novelty_neighbors.",
      "novelty_neighbors": [
        {"work": "'Whole brain CT perfusion in acute anterior circulation ischemia: coverage size matters' (Neuroradiology 2014)", "identifier": "DOI 10.1007/s00234-014-1429-9, PMID 25228451; found by search 2026-08-18", "relation": "Quantifies clinical underestimation of ischemic volumes at reduced z-coverage (80 mm and below) -- protocol literature, no segmentation models, no benchmark audit."},
        {"work": "'Optimal brain perfusion CT coverage in patients with acute middle cerebral artery stroke' (AJNR 2010)", "identifier": "https://www.ajnr.org/content/31/4/691; found by search 2026-08-18", "relation": "Establishes 70-75 mm z-coverage as the minimum for MCA-territory characterization -- the physical basis for expecting overflow, again with no model or benchmark analysis."},
        {"work": "'Underestimation of follow-up infarct volume by acute CT perfusion imaging' (Neurology 2025)", "identifier": "DOI 10.1212/WNL.0000000000213439; found by search 2026-08-18", "relation": "Documents that acute CTP-derived volumes underestimate follow-up infarct volumes clinically -- outcome-measurement literature that never separates the sensor-coverage component or touches challenge ground truth."}
      ],
      "novelty_delta": "No located work measures how much of a public stroke benchmark's ground truth lies outside the primary sensor's support, bounds the metric consequences (including the official absolute-volume-difference metric), or tests whether trained models' predicted extent is determined by the support boundary.",
      "why_not_done": "BLIND_SPOT: coverage adequacy lives in the clinical protocol literature, which the segmentation-challenge community does not read; challenge pipelines treat released maps as given inputs and their support as preprocessing trivia, so nobody has asked what fraction of the scored target the sensor ever saw.",
      "existing_assets": "Released perfusion maps, 4D CTP, whole-brain NCCT/CTA, ground-truth masks, and the official evaluation code (github.com/ezequieldlrosa/isles24 utils/eval_utils) -- everything stage 1 needs is a small subset of the release; the atlas registration tooling is shared with baseline c02.",
      "smallest_decisive_experiment": "Stage 1, model-free and decisive: download derivative perfusion maps plus ground-truth masks for all 149 cases (small fraction of the archive); compute per-case support masks, slab z-extent census, fraction of ground-truth lesion mass outside support, and the sensor-respecting performance ceiling -- the maximum Dice and minimum absolute volume difference attainable by ANY prediction confined to the support, using the official evaluation code. Prespecified kill: median slab covers the brain and overflow > 5% in < 10% of cases. Compute envelope: one Colab session, CPU-only, well under an hour of compute. Stage 2 (conditional on the shared audit model): boundary-discontinuity analysis at matched NCCT/CTA evidence across patients, under 5 GPU-hours.",
      "standing_confounds_addressed": "Stage 1 is arithmetic on released data -- no confounds, only measurement definitions (support degeneracy criteria preregistered). Stage 2: lesion size correlates with overflow (big lesions overflow more) -- conditioned on lesion volume; slab position may correlate with positioning quality and habitus -- the cross-patient contrast is restricted to atlas locations with both in-slab and out-of-slab representation and matched NCCT evidence; the fundamental entanglement that out-of-slab voxels genuinely have less evidence is stated as a scope limit: stage 2 characterizes the learned convention (truncate versus extrapolate and how sharply), not its irrationality. Labels enter stage 1 as the object of study and are excluded from the stage-2 conditioning variables.",
      "alternative_explanations": ["Predictions fade beyond the slab simply because evidence fades -- conceded by design; the claim is about WHERE the extent decision is made (sensor edge versus ischemia edge) and what the benchmark does with it, not about model irrationality.", "Support-mask degeneracy is misdefined (zeros versus resampling padding) -- preregistered support criteria with per-case audit dumps.", "Overflow is an artifact of registration between MRI-space masks and CT-space maps -- the overflow census is computed in the released common space, and gross misregistration cases are flagged by the c08 census if both advance."],
      "anticipated_negative": "Fully decisive either way at stage 1: substantial overflow is a benchmark fact with a computable metric-sensitivity bound; near-zero overflow is a documented reassurance that ISLES'24's sensor coverage matches its scoring target -- worth one session either way. Stage-2 nulls (no boundary-locked behavior) are informative only after the stage-1 gate passes.",
      "cross_domain": {"borrowed_construct": "Swath/footprint analysis from satellite remote sensing: any measurement campaign must report what fraction of the mapping target lies outside the sensor's swath, and maps must distinguish 'observed empty' from 'never observed'.", "measurement_it_implies": "The per-case coverage-completeness fraction (target mass inside sensor support) and the observed/unobserved distinction propagated into the evaluation metric.", "what_changes_if_dropped": "Without the swath discipline the study collapses into anecdotes about individual cases at the slab edge; the coverage-completeness fraction is what turns it into a quantitative benchmark audit."},
      "remaining_legwork": "One session for the full stage-1 census including the metric-ceiling computation; half a day to write the audit report; stage 2 only if the gate passes and the shared model exists (2-3 days).",
      "design_template": "conditional-observational",
      "entry_point_2_requirements": "Measurement: perfusion support mask, ground-truth overflow fraction, sensor-respecting metric ceiling, and boundary-conditional prediction contrast. Confused artifacts: support-mask definition and mask-map registration error -- preregistered support criteria and flagged-case audit; the evidence-availability entanglement in stage 2 is stated as a scope limit, not assumed away.",
      "scores": {
        "clarity": {"value": 4, "why": "Two stages with exact computable readouts; the stage-2 estimand (learned edge convention) needs careful preregistration to stay separated from the rationality question."},
        "identifiability": {"value": 3, "why": "Stage 1 is assumption-free arithmetic; stage 2's use claim is honestly entangled with evidence availability and is scoped to characterizing the convention rather than proving irrationality."},
        "medical_relevance": {"value": 4, "why": "If part of the scored target was never seen by the primary modality, volume-based triage metrics and challenge rankings inherit an unmeasured convention; either census outcome directly informs how the benchmark should be read."},
        "interest": {"value": 4, "why": "'The benchmark scores terra incognita' is a claim every challenge participant would want settled, and the sensor-respecting ceiling is a number nobody has computed for any stroke benchmark."},
        "prior_legwork": {"value": 4, "why": "Everything needed for the decisive stage is released, including the official metric code; the clinical coverage literature supplies priors and framing."},
        "feasibility": {"value": 3, "why": "Capped at 3: the slab-geometry keystone is not inspected -- though it is the cheapest keystone in the portfolio to check."},
        "data_readiness": {"value": 4, "why": "Stage 1 needs only maps and masks, a small public subset; no model required."},
        "evaluation_readiness": {"value": 4, "why": "Official evaluation code is public and the ceiling computation reuses it directly; only the support definition is custom."},
        "negative_result_value": {"value": 4, "why": "A near-zero overflow census is a clean, citable reassurance about the benchmark -- decisive, not sensitivity-limited."},
        "novelty_confidence": {"value": 3, "why": "Coverage literature is adjacent but the benchmark-audit question is unclaimed in every source found; targeted search only."},
        "regret": {"value": 4, "why": "One CPU session settles a question that becomes obvious in hindsight the first time a large-lesion case is inspected; skipping it risks every model comparison on this benchmark carrying an unexamined convention."}
      },
      "priority_score": 3.6,
      "unverified_claims": ["CTP slabs in this release are narrower than the brain in a non-trivial fraction of cases", "ground-truth lesion mass overflows the support at the prespecified threshold", "support masks are recoverable from map degeneracy patterns as assumed", "novelty beyond targeted search"],
      "plain_pitch": "The stroke scans that measure blood flow often cover only a slab of the head -- like a satellite that photographs a strip of ground on each pass -- while the 'correct answers' for this benchmark were drawn on later whole-brain MRI. That mismatch would mean models are scored on brain regions their main sensor never saw, and each model must invent its own policy there: stop at the sensor's edge, or guess beyond it. This study first measures, with simple arithmetic on the public data, how much of the official answer lies outside the sensor's view and how much that could move the leaderboard; if the answer is 'a lot', it then checks whether models draw their predicted damage boundary at the sensor's edge rather than the injury's. Either outcome changes how results on this benchmark should be read."
    },
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
        {"work": "Brett, Leff, Rorden, Ashburner -- 'Spatial normalization of brain images with focal lesions using cost function masking' (NeuroImage 2001)", "identifier": "DOI 10.1006/nimg.2001.0845; found by search 2026-08-18", "relation": "Canonical demonstration that lesions corrupt registration and must be masked out of the cost function -- the exact instrument c08 reuses -- developed for template normalization in lesion-symptom mapping, never applied to auditing challenge ground truth."},
        {"work": "Nachev, Coulthard, Jaeger, Kennard, Husain -- 'Enantiomorphic normalization of focally lesioned brains' (NeuroImage 2008)", "identifier": "PMC2658465, DOI 10.1016/j.neuroimage.2007.10.002; found by search 2026-08-18", "relation": "Improves lesioned-brain registration using contralateral-hemisphere filling; again lesion-symptom-mapping methodology, quantifying that lesion-vicinity registration error grows with lesion size -- the same error family c08 measures in ISLES'24."},
        {"work": "Bertels, Robben, Vandermeulen, Lemmens -- 'Final infarct prediction in acute ischemic stroke' (review)", "identifier": "arXiv 2211.04850; found by search 2026-08-18, abstract fetched", "relation": "Review from the group behind native-CTP final-infarct prediction covering how follow-up imaging defines the target; the surrounding literature acknowledges edema-inflated follow-up volumes and attempted CSF exclusion, but neither this nor any located work measures the released ISLES'24 masks' geometric error or model inheritance of it."}
      ],
      "novelty_delta": "No located work quantifies the mass-effect registration error inside a public benchmark's RELEASED ground truth via a physically-impossible-voxel criterion, nor tests whether models trained on that benchmark reproduce the error.",
      "why_not_done": "BLIND_SPOT: the people who know lesioned-brain registration is fragile (lesion-symptom-mapping community, 2001-2012) and the people who build final-infarct benchmarks (segmentation-challenge community) are different communities; challenges treat registration as solved preprocessing, and the impossible-voxel criterion -- which sidesteps the 'which registration is correct' debate entirely -- appears in neither literature.",
      "existing_assets": "Released follow-up DWI/ADC, acute NCCT, ground-truth masks in the common derivative space (Zenodo 16731717); public registration tools (ANTs, SynthMorph) and the cost-function-masking recipe; SynthSeg and HU arithmetic for acute CSF; baseline c01's planned DeepISLES rerun as the untrained comparator; official evaluation code.",
      "smallest_decisive_experiment": "Stage 1 census on 30 cases stratified by lesion volume: compute the impossible-voxel fraction (primary, registration-free) and the affine-versus-deformable peri-lesional displacement (secondary, cost-function-masked), and correlate both with lesion volume and midline shift (mass-effect signature: error growing with severity is the fingerprint of unmodeled deformation, not random noise). Prespecified benchmark-relevance readout: recompute official Dice and absolute-volume-difference on the census cases with impossible voxels removed from the ground truth -- the metric shift bounds how much the halo moves scores. Compute envelope: one Colab GPU session (SynthMorph registration runs in seconds-to-minutes per pair; ~10-15 GB download). Full 149-case census: one further session. Stage 2 (conditional on the shared audit model): predicted-mask CSF-overlap rate versus the ground truth's own rate and versus the DeepISLES comparator, inference only, under 5 GPU-hours.",
      "standing_confounds_addressed": "Genuine infarct growth versus geometric error: separated by the physical-impossibility criterion (growth cannot occupy acute CSF), the primary endpoint. Partial volume and CSF-segmentation error: 1-2 voxel erosion, conservative HU window, two-tool cross-check, and a reported sensitivity band. Ventricular compression at follow-up cuts the OTHER way -- compressed ventricles make CSF overlap less likely, so the census is conservative. Deformable-reference circularity: the displacement field is secondary and direction-reported-both-ways; the primary endpoint uses no registration. Site and scanner: stratified by center. Labels are the object of study in stage 1; stage 2's readout is a comparison of overlap rates, not a Dice contest.",
      "alternative_explanations": ["Impossible voxels come from mask interpolation during resampling rather than affine failure -- distinguishable because interpolation error is thin-shell and uncorrelated with mass effect, while swelling displacement grows with lesion volume and midline shift; the correlation analysis is prespecified.", "The model predicts into CSF because of its own smoothing, not label inheritance -- the DeepISLES comparator (never trained on these transferred labels) and the tracking of per-case ground-truth impossible rates discriminate.", "Experts corrected masks in acute space, so the halo is small -- then the census returns a small number and the benchmark gets a documented clean bill on geometry; explicitly a valuable outcome."],
      "anticipated_negative": "Decisive either way at stage 1: a large impossible-voxel fraction rising with mass effect is a benchmark-integrity finding with a computable metric bound; a near-zero fraction is citable evidence that the affine pipeline did not measurably corrupt the released masks. Stage 2's null (models ignore the halo and stay on tissue) is a genuinely reassuring property of the model family, interpretable because the stage-1 gate quantified the available halo first.",
      "cross_domain": {"borrowed_construct": "Datum shift from geodesy and surveying: coordinates are only meaningful relative to a reference frame, and transferring measurements between frames with an insufficient transformation model (e.g., a global affine for locally deformed terrain) produces systematic, spatially-structured position error that must be surveyed, not assumed away.", "measurement_it_implies": "The residual displacement field between the insufficient transform and a locally-adequate one, plus known-impossible landmark checks (the surveying practice of closing the traverse) -- here, CSF voxels as landmarks where infarct provably cannot be.", "what_changes_if_dropped": "Without the datum-error frame the study becomes 'registration is imperfect', a truism with no measurement discipline; the impossible-landmark check is what converts it into a falsifiable audit with a primary endpoint that needs no reference registration at all."},
      "remaining_legwork": "One session to the 30-case stage-1 decision; one further session for the full-cohort census and the metric-shift bound; stage 2 within a week once the shared audit model and the c01 DeepISLES rerun exist.",
      "design_template": "other:label-geometry-audit",
      "design_template_justification": "Nearest listed grammar is cross-model-disagreement, but the primary readout requires no second trained model: it is agreement of masks and predictions with a physically-impossible voxel set derived from the acute image itself. Counting it as cross-model-disagreement would overstate that template's concentration; the audit grammar (measure a documented provenance error, then test whether models inherit it) is shared with baseline c01 and is named the same way here for honest homogenization accounting.",
      "entry_point_2_requirements": "Measurement: impossible-voxel fraction of ground truth and predictions (acute-CSF overlap) and the affine-versus-deformable peri-lesional displacement field. Confused artifacts: partial volume, CSF-segmentation error, mask-interpolation shells, and deformable-reference error -- addressed by erosion margins, two-tool cross-check, the mass-effect correlation signature, and demoting all registration-dependent quantities to secondary endpoints.",
      "scores": {
        "clarity": {"value": 4, "why": "One documented mechanism, one registration-free primary endpoint, one prespecified correlation signature; the multi-tool CSF definition needs preregistration."},
        "identifiability": {"value": 4, "why": "The physical-impossibility criterion sidesteps the 'which registration is truth' debate that would otherwise sink the design; residual threats (partial volume, interpolation shells) are bounded and direction-signed."},
        "medical_relevance": {"value": 4, "why": "If voxel-level ground truth is geometrically wrong preferentially in severe strokes, every Dice- and volume-ranked conclusion from this benchmark inherits it, and 'model predicts infarct inside a ventricle' is a clinically legible defect."},
        "interest": {"value": 5, "why": "The ground truth being drawn on a swollen brain and transferred with a transform that cannot represent swelling -- during the documented edema peak -- is an obvious-once-said claim that no one has measured; both outcomes are tellable to the whole challenge community."},
        "prior_legwork": {"value": 4, "why": "Twenty years of lesion-registration methodology supplies the instruments; all data and the comparator pipeline (via c01) are public or already planned."},
        "feasibility": {"value": 4, "why": "Keystone inspected true with verbatim quotes; the decisive census is one GPU session with modern learned registration, and the primary endpoint is registration-free arithmetic."},
        "data_readiness": {"value": 4, "why": "Follow-up DWI, acute NCCT, and masks are all in the public release; only a modest subset is needed for the decisive stage."},
        "evaluation_readiness": {"value": 3, "why": "The impossible-voxel and displacement metrics are custom (though simple); the metric-shift bound reuses official evaluation code."},
        "negative_result_value": {"value": 4, "why": "A near-zero halo is a clean, citable geometric validation of the benchmark's ground truth -- decisive, not sensitivity-limited, because the criterion is physical."},
        "novelty_confidence": {"value": 3, "why": "Strong adjacent literature on both sides with the specific audit unclaimed in every source found; capped by targeted-search scope despite the inspected keystone."},
        "regret": {"value": 5, "why": "Cheap, keystone-verified, composes with c01, and the question will eventually be asked of every follow-up-derived ground truth; being scooped on an obvious-in-hindsight audit of the program's own charter dataset would sting."}
      },
      "priority_score": 4.05,
      "unverified_claims": ["magnitude of the impossible-voxel fraction in the released masks (could be near zero if organizers corrected in acute space)", "acute-CSF segmentation reliability on the resampled derivative NCCT", "SynthMorph/ANTs with cost-function masking is adequate as the secondary displacement reference", "the shared audit model materializes for stage 2", "novelty beyond targeted search"],
      "plain_pitch": "The 'correct answers' for this stroke benchmark were drawn on MRI scans taken 2 to 9 days after the stroke -- exactly when the injured brain is most swollen -- and then copied onto the earlier CT scans using a simple global alignment that cannot account for swelling. That would smear each answer's position, worst in the biggest strokes, sometimes marking 'dead brain tissue' on spots that are plainly fluid on the early scan, where there is no brain tissue to die. This study first measures that error directly on the public data, using fluid spaces as tamper-proof landmarks, and then asks whether prediction models trained on these answers have learned to copy the error -- forecasting damage in places where damage is physically impossible. Either way the benchmark community learns something it currently assumes: how much of the official ground truth is geometry gone wrong, or that the pipeline survived the swelling problem intact."
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

