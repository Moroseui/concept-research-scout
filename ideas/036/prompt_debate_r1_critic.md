You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/036
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

- **IDENTIFIABILITY_FAILURE** x8: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
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
- **idea-036** [SHORTLISTED/CRITIQUED/baseline] -- Does the model bring a vascular map to the scan?
- **idea-037** [SHORTLISTED/SCOUTED/wide] -- The scan remembers which hospital took it
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


===== ideas/036/README.md =====
# Idea 036: Does the model bring a vascular map to the scan?

Selected from scouting cycle isles24-004, candidate 2.


===== ideas/036/critique.md =====
FATAL OBJECTION: A prediction jump at a population-atlas border cannot identify model use of an internal vascular map because the border is not a cutoff-assigned treatment and is itself a locus of real, incompletely measured vascular physiology.
EVIDENCE: Liu et al., Scientific Data 2023, DOI 10.1038/s41597-022-01923-0 (watershed cases excluded; territory assignment not angiographic); ideas/036/keystone_screen.md; Momjian-Mayor & Baron, Brain 2005, DOI 10.1093/brain/awh366.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial critique

## 1. The proposed regression discontinuity does not identify the stated use claim

**Verified fact:** classical and geographic regression-discontinuity designs require a treatment or exposure that changes at a cutoff, plus continuity/local exchangeability of untreated potential outcomes around that cutoff. Territory membership is not an input supplied to the proposed nnU-Net and crossing the registered atlas line does not assign a treatment. The observable contrast is therefore a spatial discontinuity in model output, not an effect of territory membership.

**Verified medical fact:** arterial border zones are not exchangeable tissue separated only by a cartographic label. They are distal junctions of arterial supply and are specifically susceptible to hemodynamic failure and impaired embolus washout. Momjian-Mayor and Baron review this physiology in *Brain* (2005; DOI `10.1093/brain/awh366`). Matching CBF, CBV, MTT, Tmax, NCCT HU, and distance to core cannot establish that collateral routes, arterial arrival curves, bolus truncation, occlusion geometry, tissue history, or nonlocal context are continuous across the border.

**Verified atlas fact:** Liu et al. built the atlas from infarct distributions in 1,298 MRI cases, explicitly excluding infarcts “exclusively within watershed areas,” and acknowledge that territory classification used expert description rather than angiography (only 59% had MRA confirming a single relevant large-artery lesion). The deterministic 30-label map is thus not a patient-specific supply map and was not validated for the very border-zone estimand proposed here (Scientific Data 10:74, DOI `10.1038/s41597-022-01923-0`).

Placebo borders answer only whether arbitrary shifted curves also show jumps. They do not make physiology smooth at the true border, distinguish a learned atlas from a learned spatial/location prior, or distinguish either from use of nonlocal image evidence within the model's receptive field. Contralateral borders have different lesion and occlusion context and do not supply the missing counterfactual. Registration perturbations measure sensitivity to atlas placement, not construct validity.

Consequently, even a clean positive result supports only: **predictions are associated with a registered population-atlas boundary after adjustment for selected released channels.** It does not support the card's deliverable that the model “is using arterial-territory membership ... as a spatial prior.” The card itself admits the residual physiology but scores identifiability as if it were only a ceiling; it is fatal to rung 1.

## 2. Patient-specific anatomy is not an optional rung-2 enhancement

The card postpones anatomically variant cases to rung 2. That is backwards. Dissociation between the population atlas and patient-specific vascular supply is the observation that could discriminate a memorized textbook map from image-derived case evidence. On standard anatomy, atlas location, true supply, lesion prevalence, training-label geometry, and stereotyped spatial coordinates all align.

ISLES'24 releases single-phase CTA, but the inspected materials do not provide patient-specific perfusion-territory labels or selective arterial perfusion imaging. Inferring territories from the same CTA/perfusion inputs used by the model would introduce another model and another construct-validation problem. Without an independently measured patient-specific map or a valid intervention on the alleged internal variable, the original use question is not identified.

## 3. Leakage and model choice are unresolved

**Verified asset fact:** a frozen winning checkpoint and probability-export path exist, but its public weights were trained on the public challenge training cohort; the hidden 98-case test set is unavailable. Auditing that checkpoint on the same 150 public cases risks measuring memorized training-mask geography. It cannot establish held-out behavior.

Training a new model with 30 held-out cases avoids that leakage but changes the object from “the winning model” to a lab-trained model, leaves roughly 120 training cases on a task whose winner achieved only Dice 0.285 ± 0.213, and requires the performance threshold to be frozen before training. Cross-fitted out-of-fold predictions are possible, but every fold then represents a different fitted model. None of these repairs the causal interpretation above.

The claim of “about 10^4” usable matched pairs is not a sample-size argument. Voxels share patients, borders, receptive fields, and preprocessing; effective sample size is governed principally by patients and boundary segments. A patient-cluster bootstrap alone does not show power for a narrow discontinuity after overlap, registration-QA, and bandwidth gates. The proposed decisive null is therefore overstated: registration blur, low model skill, limited common support, and atlas misplacement can all erase a true effect.

## 4. Prior work and novelty

The atlas and deliberate anatomical-prior segmentation methods establish substantial nearby legwork. Robben et al. (Medical Image Analysis 2020; DOI `10.1016/j.media.2019.101589`) establish final-infarct prediction from CTP, but do not establish this audit. I did not locate a primary study with this exact atlas-border analysis; that is **not proof of novelty**. More importantly, absence of an exact duplicate cannot rescue a non-identifying estimand. The candidate should not claim an econometric inferential guarantee.

## 5. Medical relevance and endpoint

The motivation—failure under variant anatomy—is medically intelligible, but the proposed endpoint never measures performance in variant anatomy or even prediction error. Labels are deliberately excluded from the primary readout. A discontinuity could be anatomically helpful, harmful, or irrelevant; it does not show that the prior “overrides case evidence.” The clinical-safety language outruns the endpoint.

The endpoint is also underspecified: territory hierarchy, border classes, signed orientation, probability scale, bandwidth, matching algorithm, caliper, overlap criterion, aggregation across boundary surfaces, and multiplicity across borders are not frozen. Different choices can reverse or average away heterogeneous effects. These are repairable analytic defects, but they are secondary to the identification failure.

## 6. Plain-pitch fidelity

The pitch fails fidelity in two places. “Two neighboring tissue spots look hemodynamically identical” translates observed matching into physiological identity, despite the card's explicit unreleased-physiology residual. “The model imposes anatomy textbook knowledge on individual patients” states the desired use conclusion as what a positive test establishes, although the design can show only a conditional spatial association. The statement about risk to “the many people” with variant vessels is unquantified and the study contains no variant-anatomy cohort. Hedges and the rung-1 limitation did not survive translation.

## 7. Easier version and existing low-hanging fruit

The low-hanging-fruit formulation is an **out-of-fold error audit by atlas border distance**, not a use test. ISLES'24 already supplies the 150 public multimodal cases, follow-up-MRI-derived masks, NCCT-space perfusion maps, and official evaluation machinery; the atlas and nnU-Net code also exist. Train prespecified cross-validation models, retain out-of-fold probabilities only, register the atlas without viewing model outputs, and ask whether calibration error, false-negative burden, or soft Dice contribution worsens in prespecified border-zone bands versus territory-interior tissue after stratifying by lesion status and perfusion severity. Registration QA and patient-level uncertainty remain mandatory. This uses labels rather than avoiding them, because error—not an unexplained output jump—is the medically relevant endpoint.

That study would reveal a benchmark failure mode and could motivate a later patient-specific-territory study. It must not be narrated as proof that the model carries or uses a vascular map. Because the deliverable changes from internal use to spatial error concentration, the claim-identity rule requires a separate candidate.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: On strictly out-of-fold ISLES'24 predictions, are calibration and segmentation errors systematically worse in registered arterial border-zone bands than in perfusion- and lesion-status-matched territory interiors?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—if registration and effective patient support pass prespecified gates, it directly tests a clinically recognizable spatial failure mode using existing images, labels, atlas, and training code, with either direction informative for benchmark design.


===== ideas/036/debate.md =====
# Debate transcript



===== ideas/036/idea_card.json =====
{
  "id": "isles24-scout-004-c02",
  "parent_ids": [],
  "search_mode": "B",
  "entry_point": 2,
  "title": "Does the model bring a vascular map to the scan?",
  "question": "Is an ISLES'24 final-infarct model using arterial-territory membership \u2014 the brain's vascular map \u2014 as a spatial prior beyond the case's own perfusion and tissue evidence?",
  "rung": "Target rung 1: use of atlas-defined territory membership; rung 2 requires replication in a second model family and demonstration on anatomically variant cases where prior and evidence dissociate.",
  "deliverable_sentence": "The final-infarct model is using arterial-territory membership \u2014 the brain's vascular map \u2014 as a spatial prior, producing prediction discontinuities at territory borders between voxels with matched local evidence.",
  "X_measurement": "Register the public digital arterial-territories atlas (Liu et al., Scientific Data 2023, DOI 10.1038/s41597-022-01923-0; github.com/Chin-Fu-Liu/Arterial_Atlas) to each NCCT with standard deformable registration; X is territory membership and signed distance to the territory border per voxel. Compute-today test: YES on any unseen head CT with public atlas and registration tools; no annotator.",
  "suspected_signal": "Emboli follow arterial trees, so real infarcts are territorial; a segmentation network trained on territorial masks can internalize the territory shapes themselves and apply them as a prior. Physicians reason territorially and would want to know whether the model does too \u2014 helpful as anatomical plausibility, harmful if the prior overrides case evidence in patients with variant vascular anatomy.",
  "use_vs_association": "Association predicts model output varies smoothly with local hemodynamic evidence; use of a map predicts a jump located exactly at an externally registered anatomical boundary between voxels matched on all released evidence channels. Placebo boundaries (shifted 5-10 mm), contralateral boundaries, and matching on Tmax/CBF/CBV/MTT/NCCT-HU/distance-to-core carry the distinction.",
  "keystone_prerequisite": "A frozen trained final-infarct model with continuous per-voxel output and non-trivial held-out performance exists, and atlas-to-CT registration is accurate to a few millimeters so border-straddling matched pairs are real.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_residual_assumption": "The verified nearby fact is that the atlas is public and covers territories hierarchically; the load-bearing facts \u2014 reproduced-model quality and registration accuracy on defaced stroke CT \u2014 are the actual stage-0 gates. Matching can only use released evidence channels; unreleased raw-CTP cues correlated with true borderzone physiology remain possible and cap the identifiability score.",
  "rung_reached": "0; rung 1 after the discontinuity analysis with placebo and registration-perturbation gates; rung 2 after a second model family and variant-anatomy cases.",
  "dies_like_prior": "Nearest killed relative is idea-020 (spreading front, IDENTIFIABILITY_FAILURE). Differences: no synthetic intervention is required, the readout is a boundary discontinuity with built-in placebo cutoffs and contralateral controls, and the dominant confound (genuine watershed hemodynamics) is explicitly handled by matching on every released hemodynamic channel plus a prespecified sensitivity band; if matching quality fails its own gate, the result is reported as unidentifiable rather than reinterpreted.",
  "closest_prior_work": "The atlas itself (DOI 10.1038/s41597-022-01923-0) and deliberate atlas-prior segmentation methods exist; Robben et al. (Medical Image Analysis 2020, DOI 10.1016/j.media.2019.101589) predict final infarct from native CTP without auditing spatial priors. No located work tests for emergent territorial priors in stroke models via boundary discontinuity; novelty is unaudited beyond targeted search.",
  "existing_assets": "Public atlas with hierarchical territories, 149 public multimodal cases, registration toolchains (ANTs), nnU-Net recipes, and a label-free readout requiring only model probability maps.",
  "smallest_decisive_experiment": "On 30 held-out cases of one trained nnU-Net: extract about 10^4 border-straddling voxel pairs matched on the five released evidence channels plus distance-to-core; estimate the output discontinuity with patient-clustered bootstrap CIs; compare against 20 placebo borders per case and contralateral borders; registration-perturbation sensitivity analysis. Decision in 3-4 days after model training; under 5 GPU-hours of inference.",
  "standing_confounds_addressed": "Within-case matched pairs fix scanner, vendor, protocol, site, positioning, habitus, prevalence, and referral. Registration error blurs true jumps (conservative for a positive claim, threatening for a null \u2014 handled by the perturbation gate). NOT ruled out: model access to unreleased or raw-image correlates of true borderzone physiology at the border; this is the candidate's honest identifiability ceiling. Labels never enter the primary readout.",
  "alternative_explanations": [
    "Genuine watershed hemodynamics differ at borders in ways the released maps do not fully capture \u2014 the main residual, stated and scored.",
    "Registration is systematically biased at borders \u2014 perturbation and contralateral analyses bound this.",
    "The model produces edges everywhere \u2014 placebo borders quantify generic edge behavior."
  ],
  "anticipated_negative": "Decisive given the power and registration gates: the model integrates evidence smoothly with no detectable anatomical prior \u2014 directly reassuring for patients with variant vascular anatomy. Sensitivity-limited if registration QA fails its gate.",
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
  "plain_pitch": "Strokes tend to respect the borders of each artery's supply zone, and doctors carry that vascular map in their heads. This study asks whether the prediction model carries the same map \u2014 whether its predicted damage jumps exactly at map borders even when two neighboring tissue spots look hemodynamically identical. If yes, the model imposes anatomy textbook knowledge on individual patients, which is reassuring for typical anatomy but risky for the many people whose vessels deviate from the textbook.",
  "track": "baseline",
  "charter": "isles24"
}


===== ideas/036/keystone_screen.md =====
# Keystone screen — idea 036 (Does the model bring a vascular map to the scan?)

Screened 2026-08-18 against primary sources, inspected first-hand where
possible: the arterial-territories atlas repository, cloned and read
(github.com/Chin-Fu-Liu/Arterial_Atlas, commit
`fbeb3fe70b6fb8185244d02f9c6b6e07c13235e0`); the official ISLES'24
challenge repository, cloned and read (github.com/ezequieldlrosa/isles24,
commit `94b34863a099a8aeae6cf9b989c78ff2c767b80e`); the winning team's
released inference code, cloned and read (github.com/KurtLabUW/ISLES2024,
commit `bb6c00c8a58cb57a5a33c133c02885776673d230`); the challenge results
paper (arXiv 2408.10966, abstract); the winning team's method paper
(arXiv 2505.18424v1); the dataset paper (arXiv 2408.11142, abstract); and
the Zenodo challenge record (zenodo.org/records/10991145).

## The keystone as stated

> "A frozen trained final-infarct model with continuous per-voxel output
> and non-trivial held-out performance exists, and atlas-to-CT
> registration is accurate to a few millimeters so border-straddling
> matched pairs are real."

Two components: (K1) the model, (K2) registration accuracy. The card's
own `keystone_residual_assumption` concedes that the verified-nearby fact
is only "the atlas is public and covers territories hierarchically" and
that K1/K2 are stage-0 gates. This screen verified everything
document-checkable in that chain and applied the mandatory wrong-keystone
follow-up (section 4).

## What was inspected

### 1. The matching channels exist and share one space (VERIFIED TRUE)

The design needs voxel pairs matched on "Tmax/CBF/CBV/MTT/NCCT-HU" in a
single coordinate frame. The official challenge repository's README
documents the per-case release, including a `derivatives` tree with all
four perfusion maps resampled into NCCT space:

> ```
> +-- derivatives
> |   +-- sub-strokecase0001
> |       +-- ses-0001
> |           +-- perfusion-maps
> |               +-- sub-strokecase0001_ses-0001_space-ncct_tmax.nii.gz
> |               +-- sub-strokecase0001_ses-0001_space-ncct_mtt.nii.gz
> |               +-- sub-strokecase0001_ses-0001_space-ncct_cbf.nii.gz
> |               +-- sub-strokecase0001_ses-0001_space-ncct_cbv.nii.gz
> ```
> — github.com/ezequieldlrosa/isles24 commit `94b34863`, README.md, "Data"

The repo also ships sample derivative files matching this schema exactly
(`utils/data/derivatives/sub-stroke0014/ses-01/perfusion-maps/
sub-stroke0014_ses-01_space-ncct_{cbf,cbv,mtt,tmax}.nii.gz`), with the
follow-up lesion mask in `ses-02`. Raw NCCT, CTA, and 4D CTP are in
`rawdata`. License per the same README: "The dataset is released under
the CC BY-NC (Attribution-NonCommercial) license." The dataset paper's
abstract confirms modality families and ground-truth provenance:
"(sub-)acute CT imaging with angiography and perfusion, follow-up MRI
after 2-9 days" with "delineated infarction masks in follow-up MRI"
(arXiv 2408.11142, abstract). So the five matching channels are released,
co-registered to the NCCT frame, and one atlas-to-NCCT transform per case
serves both the border geometry and the matching. Cohort per the results
paper abstract: "a train set of 150 cases" and "the hidden test set of 98
cases" (arXiv 2408.10966) — the card's "149 public multimodal cases" is
one off from the documented 150; immaterial here, flag for critique.

### 2. The atlas is real, public, hierarchical, deformable-format (VERIFIED TRUE)

From the cloned repository README:

> "This deformable 3D digital atlas allows automatic and reproducible
> exploration of large-scaled data." … "ArterialAtlas.nii: Image defining
> 30 arterial territories and ventricles." … "ArterialAtlas_level2.nii:
> The combination of ArterialAtlas.nii parcels in 4 major territories
> (ACA, MCA, PCA, VB)." … "Images in "Atlas" folder are in MNI
> coordinates in 181x217x181 mm^3"
> — github.com/Chin-Fu-Liu/Arterial_Atlas commit `fbeb3fe7`, README.md

The label table (`data/ArterialAtlasLables.txt`) lists all 30 level-1
territories with a level-2 rollup; the NIfTI files are present in the
clone (14.2 MB each). LICENSE is CC Attribution-ShareAlike 4.0. Two
facts the card understates: the repo contains **label maps only, no
registration template** — the atlas is MRI-derived and lives in MNI
space, so mapping it onto a patient NCCT requires a template-mediated,
**cross-modal** registration path (e.g. NCCT→CT-template→MNI), not a
direct "standard deformable registration" of atlas to CT. Probability
maps and border-zone ratio maps exist but are hosted separately on NITRC
per the README.

### 3. K1 — a frozen model with continuous per-voxel output (VERIFIED TRUE at document level, with a performance-ceiling caveat)

The card plans to train its own nnU-Net, but a public frozen
challenge-winning model also exists (first established by the idea-035
screen; re-verified first-hand here). The KurtLab repo's
`model weights.txt` contains a publicly resolving Google Drive link
(`https://drive.google.com/drive/folders/1ZoTjTzbMT5EHo5KJZp6CL2U8qBLMZbXu`),
and `inference.py:136-138` runs
`nnUNet.nnunetv2.inference.predict_from_raw_data -d 150 ... -p
nnUNetResEncUNetLPlans`. The vendored nnU-Net exposes continuous
per-voxel output by flag: `save_probabilities: bool = False`
(`nnUNet/nnunetv2/inference/predict_from_raw_data.py:165`) — the deployed
container writes a binary mask, but softmax probability export is
available from the same frozen weights by construction. Weights-file
integrity was not download-verified at this stage (same standing caveat
as the idea-035 screen; an idea-004-class load probe applies).

"Non-trivial held-out performance" now has a documented ceiling. The
results paper abstract:

> "a multimodal nnU-Net-based architecture" achieved "a Dice score of
> 0.285 (+/- 0.213) and an absolute volume difference of 21.2 (+/- 37.2)
> mL" — arXiv 2408.10966, abstract

and the authors state the results "underline the significant challenges
posed by this task." The best model in the challenge scores Dice ~0.29
with per-case standard deviation nearly as large as the mean; a locally
reproduced single nnU-Net trained on the 150 public cases will sit at or
below this. Not a kill — the keystone asks for "non-trivial," and the
discontinuity readout needs continuous output, not high Dice — but the
"non-trivial performance" bar MUST be prespecified numerically before
training, or it will be set post hoc around whatever emerges. If the
public frozen winner is used instead, note from its inspected
`inference.py:121-125`: it consumes cbf/cbv/mtt/tmax/CTA and **not
NCCT** (idea-035 screen finding, re-confirmed) — harmless to the matching
(matching covariates need not be model inputs) but the atlas transform
must land in that model's output space, and its deployed preprocessing
applies per-volume windowing plus global histogram equalization
(`preprocessing.py:21`), no skull-stripping.

### 4. K2 — few-mm registration on released stroke CT (UNVERIFIABLE at screen prices)

No document can settle registration accuracy on this data; it is an
empirical stage-0 gate, and the card already routes it there with a
perturbation-sensitivity analysis. Contributing unknowns recorded: the
defacing/skull status of the released NCCT is stated nowhere I fetched
(dataset paper abstract, Zenodo record, challenge README are all silent);
and the cross-modal MNI-to-CT path from section 2 is the specific
mechanism the QA census must exercise. Nothing found suggests
infeasibility; nothing found demonstrates the few-mm claim.

## Residual assumption check (mandatory follow-up)

If this card only verified the nearest checkable thing, it is still
assuming: (a) K2 wholesale — untestable from documents, correctly
gated at stage 0; (b) that "non-trivial performance" is meaningful under
a Dice-0.285 task ceiling — the bar must be frozen before training;
(c) that enough border-straddling voxel pairs survive five-channel
matching — a count the card already assigns to stage 0; (d) that the
cross-modal template-mediated registration path (not named in the card)
is the "standard deformable registration" it invokes. The card's stated
keystone and its actual load-bearing assumptions coincide — no
wrong-keystone substitution found; the checkable enabling chain
(channels, common space, atlas, frozen model, continuous output) is
verified true end to end.

## Verdict

Everything document-checkable is verified true, first-hand where
possible; the one unverifiable component (K2) is an empirical stage-0
gate the card itself prespecifies, and nothing inspected makes any
component demonstrably false.

```json
{"verdict": "PASS", "evidence": "a multimodal nnU-Net-based architecture ... a Dice score of 0.285 (+/- 0.213) and an absolute volume difference of 21.2 (+/- 37.2) mL", "source": "arXiv 2408.10966 abstract (https://arxiv.org/abs/2408.10966); frozen winner re-verified at github.com/KurtLabUW/ISLES2024 commit bb6c00c8 (weights link in 'model weights.txt', save_probabilities in vendored nnUNet predict_from_raw_data.py:165); matching channels verified at github.com/ezequieldlrosa/isles24 commit 94b34863 README 'space-ncct_{tmax,mtt,cbf,cbv}' derivatives", "note": "All checkable enabling facts true (atlas public/hierarchical/MNI, five evidence channels co-registered to NCCT space, public frozen winner with continuous-output flag); registration accuracy stays an honest stage-0 gate, and the non-trivial-performance bar must be prespecified against the Dice-0.285 challenge ceiling."}
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
You are codex. Your interlocutor is claude.
This is round 1. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript


