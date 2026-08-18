You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/029
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

- **IDENTIFIABILITY_FAILURE** x2: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
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
- **idea-029** [SHORTLISTED/CRITIQUED/baseline] -- The ground truth remembers the algorithm that drafted it
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


===== ideas/029/README.md =====
# Idea 029: The ground truth remembers the algorithm that drafted it

Selected from scouting cycle isles24-004, candidate 1.


===== ideas/029/critique.md =====
FATAL OBJECTION: The historical pre-correction masks are unavailable, so rerun–ground-truth agreement cannot measure an “uncorrected fraction,” and predictions agreeing with the rerun where the released label rejected it cannot identify inheritance through the released label.
EVIDENCE: ISLES'24 paper, arXiv:2408.10966v1, Dataset section; DeepISLES, DOI 10.1038/s41467-025-62373-x; ideas/029/keystone_screen.md §4.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial critique

## 1. The keystone is true, but it is not the keystone the claim needs

The screen correctly verified a useful operational fact: a public DeepISLES implementation can be run on released follow-up DWI/ADC, and its output can be compared voxelwise with the released mask in `space-ncct`. That establishes that a **present-day surrogate output** is computable. It does not establish that the historical draft is recoverable.

The ISLES'24 paper says only that masks were “derived from DWI images using the ISLES'22 ensemble algorithm” and that quality control and correction were performed “when needed” (arXiv:2408.10966v1). It does not identify a commit, weights, input channels, inference settings, native-space preprocessing, threshold, postprocessing, or registration path. The screen itself found two material mismatches: the released follow-up images are already resampled into NCCT space, and follow-up FLAIR—used by the released full ensemble—is absent. The cited weights were published on 2024-11-01, after the ISLES'24 preprint and dataset construction. This does not prove that they differ from the historical weights, but it makes identity unverified.

Therefore `D` is not “the draft”; it is **a rerun of a related released system under a different observable input path**. Calling `D xor G` “the correction field” is false. It mixes human correction, model/version differences, missing FLAIR, resampling, registration, thresholding, and postprocessing. The card acknowledges most of these as depressing agreement, but asymmetric interpretation does not restore the missing estimand.

Most importantly, even a bitwise-identical `D` and `G` does not show that a mask was “uncorrected.” A reviewer may have inspected and accepted it, altered it and happened to produce the same raster, or corrected only regions on which the surrogate rerun also agrees. Conversely, disagreement does not show correction. The proposed “uncorrected fraction” is therefore not observable from the released artifacts. This is an identifiability failure, not merely reduced power.

## 2. Stage 2 reverses the causal logic of label inheritance

The card proposes restricting analysis to voxels where surrogate draft `D` and released label `G` disagree. It then says that an ISLES-trained model “siding with D” there indicates inherited draft conventions. But at precisely those voxels, the model's supervised target was `G`, not `D`. If the historical draft really was corrected from `D` to `G`, the draft signal was removed from the training label at those locations. Agreement with `D` against `G` is a held-out labeling error, not evidence that the model inherited `D` **through the labels**.

Several simpler explanations remain:

- `D` and the acute-CT model can share generic segmentation priors: smooth boundaries, minimum lesion sizes, connectedness, or class-imbalance behavior.
- `D` can be closer than `G` to the lesion geometry predictable from acute CT even when `G` is the more accurate follow-up-MRI delineation.
- `D-G` voxels are selected to be ambiguous or difficult; matching on local intensity, distance to boundary, or uncertainty cannot exhaust their biological and treatment-dependent differences.
- A prediction can agree with `D` after thresholding because of calibration or operating-point choice rather than a learned boundary convention.

The proposed external model does not solve this. It would need the same prediction task, acute modalities, preprocessing, thresholding, cohort support, and performance, while differing only in exposure to ISLES'24 labels. No such model is identified. A model trained on another cohort has different labels, case mix, treatment distribution, scanner distribution, and inductive biases; a difference in draft-siding is multiply confounded. A randomly initialized versus pretrained comparison would not isolate label exposure either.

The only region where label inheritance is mechanically plausible is where historical draft and final mask agree. There, however, draft convention, expert endorsement, and tissue truth are observationally inseparable. Without the actual draft plus an independent de-novo annotation or randomized annotation protocol, the proposed data cannot separate “algorithmic fingerprint” from correct lesion morphology.

## 3. The endpoint is undefined and partly circular

“Boundary conventions” is not operationalized. Dice, bitwise equality, and surface distance quantify agreement; they do not identify smoothness, small-lesion suppression, inclusion habits, or any other named convention. The card needs prespecified features with distinct predictions—for example curvature spectrum, component-size distribution, hole filling, or topology—and an analysis showing that these features are not simply consequences of lesion size, image resolution, or thresholding. At present, a high Dice would be relabeled as “fingerprint” after observing it.

There is also concept-label circularity in the proposed biological contrast. The study has no independent voxelwise “tissue-fate evidence” against which draft convention can be opposed: `G` is the very hybrid label under audit, and `D` is derived from the same follow-up DWI/ADC. Acute CT is not a voxelwise adjudicator of the final post-treatment lesion. Thus “conventions rather than tissue-fate evidence” is not an empirical contrast supplied by this design.

The rung definitions do not repair this. Replication across two acute-CT model families or centers reproduces an association; it does not identify its source. Rung 1 is therefore not reachable by the specified experiment, and rung 2 merely repeats the same non-identifying design.

## 4. Relevance, negative-result value, and cost are overstated

A direct audit of machine-initialized benchmark labels would be relevant to medical-imaging AI. This design cannot deliver that audit. Its clean result is only agreement between one current DeepISLES execution and released masks. Given that the masks were derived using a related high-performing model on the same follow-up modalities, substantial agreement is expected and medically unsurprising. Low agreement is uninterpretable because of the documented execution-path drift. Neither result establishes benchmark contamination, annotation quality, automation bias, or consequences for deployment.

The negative-result language is especially too strong. A stage-2 null could arise from weak subject-model performance, few informative disagreement voxels, surrogate-draft drift, thresholding, insufficient power, or a mismatched external control. It would not reassure the community that the hybrid pipeline “did not measurably contaminate model behavior.” The anticipated negative is therefore sensitivity-limited to uninterpretable, not score 4 under the rubric.

The cost estimate also omits material work. The training archive is approximately 99 GB in the current repository evidence, the DeepISLES weights are about 9.1 GB, the full ensemble's required FLAIR is absent, and stage 2 requires training and selecting a model on only 149 released cases while preserving an untouched patient-level test set. “Nothing must be built except analysis” conflicts with the card's own requirement to train nnU-Net and locate, validate, and harmonize an external control. Stage 1 may fit the stated GPU envelope, but stage 2 is not a two-week plug-in analysis until the subject and control models, split, power, and pipeline are specified.

## 5. Prior work and novelty

The primary DeepISLES paper reports a strong, clinically validated ensemble and even that neuroradiologists preferred its segmentations to manual annotations in a Turing-like test (DOI 10.1038/s41467-025-62373-x). That makes agreement with a DeepISLES-derived label less diagnostic of a harmful “fingerprint”: it may reflect a good segmenter. General annotation-noise and annotator-preference methods are adjacent, as the card states, but they do not validate this causal design.

A bounded search found work on AI-assisted labeling and automation bias, including AI-collaborative voxelwise annotation with quality assurance (Radiology: Artificial Intelligence 2023, DOI 10.1148/ryai.220105) and prospective automation-bias experiments in mammography (Radiology 2023, DOI 10.1148/radiol.222176). These establish that machine assistance can affect human review and that machine prelabels are a legitimate governance concern. They do not establish that ISLES'24 corrections were anchored, nor did I locate a primary study auditing the historical ISLES'24 drafts. “Not located” is not proof of novelty. More importantly, the candidate fails on identifiability before novelty becomes decisive.

## 6. Leakage and split integrity

Stage 1 has no train/test leakage problem because it is a label-provenance description. Stage 2 does. The card proposes training on 149 cases and analyzing held-out disagreements but gives no frozen patient-level split, no minimum number of cases or disagreement voxels, and no rule for selecting the subject model without consuming the analysis set. Hyperparameters, thresholds, and convention definitions could easily be tuned toward `D-G` after viewing all masks. A revision would need a three-way split or nested cross-fitting, precomputed power based only on development data, and an untouched test set. Those safeguards still would not fix the causal objection above.

## 7. Plain-pitch fidelity

**Named defect: the pitch turns a surrogate-agreement study into direct recovery of annotation history.** “We can redraw every answer and measure exactly how much of the official truth is uncorrected machine output” is stronger than the technical card and contradicted by its residual assumption. The actual historical draft is not released; exact correction status is not inferable from equality with a later rerun. “Then test whether models … learn the drafting algorithm's habits instead of the biology” also drops the card's acknowledged shared-inductive-bias and anchoring limits and asserts a dichotomy the experiment cannot adjudicate. The pitch's “either result matters” likewise omits that low agreement is explicitly ambiguous. These are material overclaims, not harmless simplification.

## 8. Low-hanging fruit and the easiest defensible version

The low-hanging computation is a **reproducibility/agreement census**: run the available DWI/ADC-compatible DeepISLES path on the 149 public cases and report agreement with `G`, stratified by center, lesion size, and boundary distance. The data, labels, container/code, weights, and standard metrics already exist. It must be described only as agreement with a version-pinned surrogate, not an uncorrected fraction or correction field. Because high agreement is expected and low agreement is ambiguous, that census alone is probably too weak for a full candidate; it is useful Stage-0 evidence or a data note, not the card's high-value result.

The genuinely high-value, easier experiment becomes possible if the organizers release the **actual pre-correction masks and exact generation provenance**. Then no acute-CT model is needed initially. Directly quantify which voxels and lesions were changed; characterize edit types; and measure how official metrics and method rankings change when the reference is the draft versus the corrected mask. If archived participant outputs are unavailable, evaluate at least released top methods or frozen cross-validated baselines. An independently de-novo annotated subset would further separate accepted-correct draft from reviewer anchoring, but it is not required for the narrower descriptive question “what was changed and did it matter to benchmark scores?” This is cheaper, more identifiable, and more consequential than the proposed model-behavior stage.

It is worth asking the organizers for those artifacts. Until they exist, the high-value study is paused by data access; substituting a contemporary rerun changes the estimand and does not answer it.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Using the exact archived pre-correction DeepISLES masks, which lesion and boundary edits did supervised review make, and how much do those edits change ISLES'24 model scores and rankings?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—if the historical drafts and provenance are obtained, because it directly measures human correction and its benchmark consequence without pretending that surrogate agreement reveals annotation history.


===== ideas/029/debate.md =====
# Debate transcript



===== ideas/029/idea_card.json =====
{
  "id": "isles24-scout-004-c01",
  "parent_ids": [],
  "search_mode": "A",
  "entry_point": 2,
  "title": "The ground truth remembers the algorithm that drafted it",
  "question": "Is an ISLES'24-trained final-infarct model using the boundary conventions that the DeepISLES draft left in the 'corrected when needed' ground truth, rather than tissue-fate evidence alone?",
  "rung": "Target rung 1: models reproduce draft-specific conventions in expert-overridden voxels; rung 2 requires replication across at least two trained model families and both centers.",
  "deliverable_sentence": "The final-infarct model is using the ground truth's algorithmic fingerprint \u2014 DeepISLES boundary conventions inherited through the 'corrected when needed' annotation pipeline \u2014 in the voxels where experts overrode the draft.",
  "X_measurement": "Rerun released DeepISLES (Docker isleschallenge/deepisles, weights Zenodo version 14026715) on each case's released follow-up DWI/ADC to obtain draft mask D; X is the draft-versus-released-GT disagreement field D xor G plus draft-agreement statistics (per-case Dice(D,G), bitwise-identical fraction, boundary surface distance). Compute-today test: YES \u2014 X is computed from released follow-up images by a public containerized tool, no annotator; note X lives on the follow-up image, while the audited model consumes only acute CT.",
  "suspected_signal": "Not a biological signal but a documented process one: masks were initialized by a public ensemble and corrected only 'when needed', so the released labels carry the initializer's systematic conventions (boundary smoothness, small-lesion suppression or inclusion habits); a model trained on those labels can inherit exactly those conventions, and the benchmark then partially rewards fidelity to the draft algorithm.",
  "use_vs_association": "Stage 1 is model-free description. Stage 2 separates use from association by restricting to disagreement voxels, where the training-label signal G and the draft convention D point in opposite directions: a model merely fitting its labels should side with G on held-out cases; systematic siding with D against evidence-matched baselines indicates inherited conventions. An external stroke model never trained on ISLES'24 labels serves as the shared-inductive-bias control.",
  "keystone_prerequisite": "The correction field is recoverable: the initializing segmenter is public and re-runnable on released follow-up MRI, so draft-versus-final disagreement can be computed per case.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "arXiv 2408.10966v1 (inspected 2026-08-18): 'Lesion masks are derived from DWI images using the ISLES'22 ensemble algorithm. Quality control and correction of the lesion masks are performed when needed by medical students (TAB, HPM) supervised by two neuroradiologists (JSK, BW) with more than 10 years of experience.' github.com/ezequieldlrosa/DeepISLES (inspected): the ISLES'22 ensemble is released with Docker image isleschallenge/deepisles and Zenodo weights (version 14026715); required inputs DWI (b=1000) and ADC, FLAIR 'Required for ensemble (optional for single algorithm outputs)'. zenodo.org/records/16731717 (inspected): each training case includes follow-up 'post-treatment MRI (DWI and ADC)'; 149 cases public.",
  "keystone_residual_assumption": "That the released DeepISLES version approximates the draft actually used: the initializing version/weights are not stated anywhere inspected, and if organizers ran the FLAIR-using ensemble, a DWI/ADC-only rerun differs. High verbatim agreement is version-robust evidence of imprint; LOW agreement is ambiguous between heavy correction and version drift \u2014 this asymmetry is prespecified in the analysis, and the weights-release date versus dataset-creation chronology is a stage-0 check.",
  "rung_reached": "0; rung 1 after stage-2 disagreement-voxel analysis with the external-model control; rung 2 after two-family, two-center replication.",
  "dies_like_prior": "Closest to ideas 002 and 005 (annotation provenance undocumented). It differs decisively: here provenance IS documented in the challenge paper, the initializer is a released artifact, and the provenance effect is the measurand rather than an unverifiable assumption. What it cannot do is separate expert anchoring on the draft from genuine agreement with it \u2014 stated as a limit, not assumed away.",
  "closest_prior_work": "Label-error and annotation-style work (Zhang et al., Disentangling human error from ground truth, NeurIPS 2020, arXiv 2007.15963; annotation-style effects, arXiv 2210.17398) models rater noise but does not measure AI-initialized draft imprint in a public benchmark. The DeepISLES paper (Nature Communications 2025) validates the segmenter, not its imprint on ISLES'24 ground truth. No located work runs this audit on ISLES'24; novelty confidence remains limited-search.",
  "existing_assets": "All required artifacts are public: 149 cases with follow-up DWI/ADC and GT masks (Zenodo 16731717), DeepISLES container plus weights, nnU-Net training recipes, official evaluation code (utils/eval_utils).",
  "smallest_decisive_experiment": "Stage 1 alone is decisive as a dataset-quality finding: run DeepISLES on all 149 released follow-up DWI/ADC, compute Dice(D,G), bitwise-identical fraction, and boundary distances, stratified by center; prespecify a report of the uncorrected fraction. About 2-3 days including download, under 10 GPU-hours. Stage 2 (train one nnU-Net, analyze held-out disagreement voxels with the external-model control) adds about two weeks.",
  "standing_confounds_addressed": "Scanner/site enter D-G agreement through MRI quality \u2014 stratified by center. Genuine boundary ambiguity (both draft and expert defensible) is quantified with a boundary-band analysis. The design does not rule out expert anchoring on the draft (automation bias), which would make even 'corrected' voxels draft-tinted \u2014 acknowledged as an unremovable ceiling on interpretation. Label leakage is inverted here: labels are the object of study, and the stage-1 readout needs no trusted labels at all.",
  "alternative_explanations": [
    "Models side with the draft because CNNs share inductive biases with DeepISLES, not because of label inheritance \u2014 the external never-trained-on-ISLES'24 model control discriminates this.",
    "Low draft-GT agreement reflects DeepISLES version drift rather than extensive correction \u2014 prespecified asymmetric interpretation and chronology check.",
    "Disagreement voxels are simply hard voxels \u2014 evidence-matched baselines within the same case address this."
  ],
  "anticipated_negative": "Decisive for stage 1: any measured uncorrected fraction is a benchmark fact of record either way. For stage 2, a null after the external-model control passes is a valuable reassurance that the hybrid annotation pipeline did not measurably contaminate model behavior on this benchmark.",
  "cross_domain": {
    "borrowed_construct": "Automation bias/anchoring from human-factors research: reviewers correct machine drafts less than they should.",
    "measurement_it_implies": "The surviving-draft fraction and draft-siding rate in overridden voxels as anchoring indices.",
    "what_changes_if_dropped": "Nothing mechanical \u2014 the study remains a label-provenance audit; the human-factors frame only supplies the interpretation of high uncorrected fractions."
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
  "plain_pitch": "The 'correct answers' in this stroke benchmark were first drawn by an algorithm and only fixed by humans when someone judged it necessary. Because that drafting algorithm is public, we can redraw every answer and measure exactly how much of the official truth is uncorrected machine output \u2014 and then test whether models trained on it learn the drafting algorithm's habits instead of the biology. Either result matters: a large imprint would change how the benchmark's rankings are read, and a small one would be documented reassurance.",
  "track": "baseline",
  "charter": "isles24"
}


===== ideas/029/keystone_screen.md =====
# Keystone screen — idea 029 (isles24-scout-004-c01)

**Idea:** The ground truth remembers the algorithm that drafted it
**Screen date:** 2026-08-18
**Verdict: PASS** (keystone verified true; residual assumption enlarged — see §4)

## 1. The keystone as stated on the card

> "The correction field is recoverable: the initializing segmenter is public
> and re-runnable on released follow-up MRI, so draft-versus-final
> disagreement can be computed per case."

Card status claimed: `INSPECTED_TRUE`. This screen re-inspected every leg of
that claim against primary sources, plus the mandatory nearest-checkable-thing
follow-up (§4).

## 2. What was inspected, with verbatim evidence

### 2a. The ground truth was drafted by the ISLES'22 ensemble and corrected "when needed"

Source: arXiv 2408.10966v1 (ISLES'24 dataset paper), Dataset section,
https://arxiv.org/html/2408.10966v1 (fetched 2026-08-18):

> "Lesion masks are derived from DWI images using the ISLES'22 ensemble
> algorithm. Quality control and correction of the lesion masks are performed
> when needed by medical students (TAB, HPM) supervised by two
> neuroradiologists (JSK, BW) with more than 10 years of experience."

This matches the card's quote exactly. The hybrid draft-then-correct
provenance — the object of study — is documented in the primary source.

### 2b. The initializing segmenter is public and containerized

Source: https://github.com/ezequieldlrosa/DeepISLES README (fetched
2026-08-18):

> "DeepISLES is an out-of-the-box software tool for processing MRI scans and
> segmenting ischemic stroke lesions, developed in collaboration with leading
> teams from the ISLES'22 MICCAI Challenge."

Docker image: `docker pull isleschallenge/deepisles`. Input requirements as
quoted from the README: DWI (b=1000) required; ADC required; FLAIR

> "Required for ensemble (optional for single algorithm outputs)"

Run-mode flag relevant to the FLAIR issue (README parameter table):
`fast` = "Run a single model for faster execution";
`save_team_outputs` = "Save outputs of individual models before ensembling".

### 2c. The weights are released

Source: https://zenodo.org/records/14026715 (fetched 2026-08-18):
title "Model weights- The ISLES'22 Ensemble Algorithm", version v1,
published 2024-11-01, single file `stroke_ensemble_weights.7z` (9.1 GB).
The record exists and is the one the card cites.

### 2d. The released dataset contains per-case follow-up DWI/ADC — and, decisively, on the SAME grid as the ground-truth mask

Source: https://zenodo.org/records/16731717 (ISLES'24 training data, fetched
2026-08-18): "149 acute ischemic stroke cases"; follow-up imaging includes
"post-treatment MRI (DWI and ADC)"; masks are "binary infarct masks derived
from follow-up MRI (lesion-msk.nii.gz)"; derivatives are "linearly
co-registered to the NCCT space". Per-case derivative files as listed in the
record's BIDS tree:

> `sub-strokecase0001_ses-02_space-ncct_dwi.nii.gz`
> `sub-strokecase0001_ses-02_space-ncct_adc.nii.gz`
> `sub-strokecase0001_ses-02_space-ncct_lesion-msk.nii.gz`

License: CC BY-NC-SA 4.0.

This resolves the question the card never asked (§4a): the follow-up DWI/ADC
and the ground-truth mask are released **in the same space on the same grid**
(`space-ncct`), so a DeepISLES rerun on the released DWI/ADC produces a draft
mask D directly comparable voxelwise to the released G. The disagreement
field D xor G is computable per case with no annotator and no registration
step of our own. The keystone's operational content is TRUE.

## 3. Verdict on the stated keystone

Every leg verified: provenance documented (2a), segmenter public and
containerized (2b), weights released (2c), follow-up MRI released per case
and grid-aligned with the mask (2d). **PASS.**

## 4. Mandatory follow-up: what is the card still assuming?

The card verified "the draft can be recomputed." The load-bearing assumption
underneath is stronger: **that the recomputed draft approximates the draft
the organizers actually produced.** The card acknowledges version drift as
its residual assumption; inspection shows that residual is real and has TWO
components, one of which the card did not name:

**(a) Processing-path drift (not on the card).** The paper states masks were
"derived from DWI images" and that follow-up series were registered to NCCT
with affine transformations. The organizers therefore ran the ensemble on
native-space DWI (or in an unspecified space) and the result reached NCCT
space through their registration; a rerun necessarily consumes the released,
already-resampled `space-ncct` DWI/ADC, because no native-space follow-up
data and no registration transforms appear in the release. Consequence: the
card's "bitwise-identical fraction" statistic is degraded by interpolation
alone and is a **lower bound** on draft survival, not an unbiased estimate.
This lands on the safe side of the card's own prespecified asymmetry (high
agreement remains robust evidence of imprint; low agreement was already
declared ambiguous), so it weakens power, not validity — but the analysis
plan should say "resampling" alongside "version drift" as a cause of
depressed agreement.

**(b) The FLAIR gap (partially on the card).** The released ensemble
requires FLAIR; ISLES'24 releases no follow-up FLAIR ("included DWI and
ADC"). Either the organizers ran a no-FLAIR configuration (consistent with
"derived from DWI images") or they used FLAIR that was never released. A
rerun must use the DWI/ADC-only path (single-algorithm outputs, or the
ensemble's no-FLAIR mode if its code permits — a stage-0 configuration
check). This is the card's stated residual assumption, confirmed as real and
narrowed to a concrete configuration question.

Neither component falsifies the keystone: the disagreement field is
computable and the prespecified asymmetric interpretation absorbs both drift
sources. They are recorded here so the stage-0/analysis plan inherits them
explicitly.

## 5. Classification of evidence

Verified fact: §2a–2d quotes and file listings. Source-supported
interpretation: same-grid comparability of D and G (filenames' shared
`space-ncct` label plus the record's co-registration statement). Inference:
processing-path drift in §4a (organizers ran on pre-registration images;
"derived from DWI images" + no transforms in release). Nothing in this
screen rests on memory.

```json
{"verdict": "PASS", "evidence": "Lesion masks are derived from DWI images using the ISLES'22 ensemble algorithm. Quality control and correction of the lesion masks are performed when needed by medical students (TAB, HPM) supervised by two neuroradiologists (JSK, BW) with more than 10 years of experience.", "source": "arXiv 2408.10966v1, Dataset section (https://arxiv.org/html/2408.10966v1); same-grid comparability from https://zenodo.org/records/16731717 derivative filenames (space-ncct dwi/adc/lesion-msk); segmenter at github.com/ezequieldlrosa/DeepISLES with weights zenodo.org/records/14026715", "note": "Keystone true and stronger than claimed (draft and GT share the released space-ncct grid); residual assumption enlarged to include resampling-induced drift alongside version drift — bitwise-identical fraction is a lower bound."}
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


