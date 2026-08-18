You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/027
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

- **IDENTIFIABILITY_FAILURE** x1: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_ACCESS** x1: Required data, checkpoints, or mappings are not obtainable in practice.

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
- **idea-027** [SHORTLISTED/CRITIQUED/baseline] -- When vanished sulci mean rescue, not death
- **idea-028** [SHORTLISTED/SCOUTED/baseline] -- The blood's grayscale oxygen gauge
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


===== ideas/027/README.md =====
# Idea 027: When vanished sulci mean rescue, not death

Selected from scouting cycle isles24-003, candidate 5.


===== ideas/027/critique.md =====
FATAL OBJECTION: The proposed “coherent triad” edit changes the putative collateral anatomy while freezing its perfusion consequences, so a model response cannot identify use of collateral-supported tissue viability rather than response to cross-modal inconsistency or synthesis artifacts.
EVIDENCE: PMID 25931460 reports ISE together with normal-to-increased CBV and prolonged Tmax; `ideas/027/idea_card.json` instead requires holding Tmax/CBF/CBV fixed while swapping CSF and vessel features.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: PAUSE

# Adversarial critique — idea 027

## 1. The confirmatory intervention does not instantiate the claimed mechanism

The suspected mechanism is a causal package: robust leptomeningeal filling produces visible engorged vessels, reduced sulcal CSF space, and a characteristic perfusion state while the underlying gray-white junction remains preserved. The primary series did not report the anatomical sign in isolation: all eight ISE cases had CTA-visible engorged/dilated leptomeningeal vessels and CTP with normal-to-increased CBV plus prolonged Tmax (PMID 25931460; DOI `10.1161/STROKEAHA.115.009304`). The later independent series likewise describes ISE as a marker of sufficient collateral status and increased CBV, and reports correlation with the rLMC collateral score (PMID 32912520; DOI `10.1016/j.jstrokecerebrovasdis.2020.105168`). These are verified primary-source facts.

The card proposes to swap sulcal-CSF fraction, pial-vessel occupancy, and preserved gray-white contrast while **holding Tmax/CBF/CBV fixed**. That is not a coherent collateral-engorgement intervention; it deliberately breaks the cross-modal relationship that motivates the claim. This is an identifiability failure, not merely an edit-realism nuisance. A response could be caused by (i) an impossible CTA/perfusion combination, (ii) boundary or texture artifacts from vessel/CSF synthesis, (iii) NCCT–CTA registration inconsistency, or (iv) genuine use of any one edited channel. Coherent-versus-incoherent component controls do not rescue the inference because the “coherent” arm is coherent only within the edited subset, not across the model's full input.

The repair is to design a source-verified intervention that moves the whole observed collateral phenotype—including its supported perfusion covariates—along the empirical joint distribution, or to abandon intervention and ask an association/error-stratification question. The former preserves the original use question but requires a learned conditional generator or natural matched examples plus much stronger validity gates. The latter changes the estimand and should be a separate candidate.

## 2. There is no defined model asset or endpoint

“An ISLES'24 multimodal model” and “the final-infarct model” do not identify a checkpoint, training split, input channels, preprocessing, or scalar response. That omission is load-bearing:

- The published winning system used a residual nnU-Net after SynthStrip and custom windowing (arXiv `2505.18424`). Its published final-input window table lists CTA, CBF, CBV, MTT, and Tmax, while NCCT is described as the source of the brain mask. On that account, gray-white differentiation and sulcal CSF on NCCT are not established model inputs. A model cannot “use” an NCCT sign it never receives.
- I found a public implementation for a 4D-CTP model, ISLES24-PrediCTP, but its reported performance is low (Dice 0.20; lesion-wise F1 0.02) and its input is raw CTP, not the proposed NCCT/CTA triad. It is not a low-hanging substitute for this question.
- The card says “after model training,” so neither a frozen checkpoint nor an untouched evaluation split presently exists. Training a model and developing the construct on all 149 public cases would create leakage. The hidden 96-case test set remains inaccessible except through challenge evaluation, and it cannot support bespoke per-case intervention analysis. The dataset publication verifies 149 public training and 96 hidden test cases (DOI `10.1148/ryai.250603`).
- “Survival-directed output change” is undefined. It could mean local mean infarct probability, predicted surviving volume inside the edited territory, Dice against follow-up mask, or a change in a thresholded segmentation. Those endpoints answer different questions. A paired, continuous, territory-level infarct-probability change is the least lossy candidate, but its sign, territory definition, aggregation, and exclusion of edit boundaries must be preregistered.

This alone warrants PAUSE: before a use claim, the study needs a frozen model that demonstrably consumes NCCT and CTA, non-trivial held-out performance, a frozen split, and an exact local endpoint.

## 3. The automatic construct is not a label-free solution

The card avoids new expert annotation by defining a computable triad, but that merely replaces an expert phenotype with an unvalidated proxy. It does not establish that low apparent sulcal CSF is sulcal effacement, that local HU contrast corresponds to preserved gray-white *delineation*, or that segmented CTA voxels are engorged pial collaterals rather than veins, normal arteries, bone/contrast contamination, or phase effects.

This creates concept-label circularity at the construct gate: “stronger ipsilateral pial-vessel occupancy without reduced gray-white contrast” is partly the operational definition of the candidate and is then proposed as evidence that the detector found the clinical sign. Registration perturbation tests stability, not semantic validity. The released Circle-of-Willis pseudolabels described in the dataset paper are not pial collateral labels; they do not validate the required distal-vessel measurement (DOI `10.1148/ryai.250603`, “Segmentation of the Circle of Willis for CTA Scans”).

At least a blinded expert audit of candidate-positive and candidate-negative territories is needed. Under the charter this is permissible but incurs fresh annotation burden. A small enrichment audit can estimate positive predictive value, but sensitivity requires reviewing an appropriate sample of detector-negative territories too. The card's “no annotator” claim is therefore unsupported at the rung needed for the clinical phrase.

## 4. Support and power are worse than the card implies

The keystone screen correctly computes an expectation of about 11 cases from 8/108, below the proposed gate of 15. A second primary series found ISE in 12/195 overall (6.2%) and 11.4% among proximal anterior-circulation occlusions (PMID 32912520). This supports reproducibility of the rare sign, but it does not imply 15 usable ISLES territories because ISLES also includes posterior-circulation cases and the automatic construct is stricter/different.

More importantly, `>=15 territories` is not a power calculation. Territories within a patient are clustered; edit effects from perhaps 8–15 positive patients cannot be treated as independent. The threshold is currently convenient rather than tied to a minimum detectable paired response, a precision target, or stability across folds/model seeds. A negative after this gate would remain sensitivity-limited and model-specific. The card appropriately caps negative-result value at 2, but its proposed two-week experiment still risks spending most effort to obtain an uninformative null.

## 5. Clinical relevance is overstated at the deliverable level

The clinical papers support the proposition that ISE should not be interpreted as irreversible injury and may mark favorable collaterals. They do not establish that a final-infarct segmentation model's response to a synthetic ISE edit changes treatment decisions. ISLES is restricted to successfully reperfused patients, so the model predicts post-treatment infarct in a selected cohort; it is not a thrombectomy-selection model. “Mistaking reversible tissue for core can affect treatment interpretation” is a plausible motivation, not a demonstrated consequence of this audit.

The medically relevant model question should instead be: does a deployed or benchmark model systematically overpredict infarction in real, expert-confirmed ISE territories after successful reperfusion? That error question is closer to clinical harm and easier to interpret than a synthetic use claim, although it still requires enough real ISE cases and per-case predictions.

## 6. Prior-work overlap and novelty status

No verified duplicate of the exact model-use experiment was found in the repository's targeted novelty audit. That is not proof of novelty. The clinical phenomenon itself is not new: it has at least the 2015 EVT series (PMID 25931460) and the 2020 IV-thrombolysis series (PMID 32912520). The second series is material closest work missing from the card's `closest_prior_work`; it measured ISE, ASPECTS, and rLMC collateral score and tested response/outcome associations in 195 patients.

The exact delta, if pursued, is therefore not discovery of ISE as a rescue sign. It is either (a) external validation of ISE against spatial follow-up MRI in a public successful-reperfusion cohort, or (b) a model audit asking whether a specified final-infarct model exploits or mishandles that already-described phenotype. Novelty confidence should remain low until the 2020 paper's citation neighborhood and later computational work are audited from primary full texts.

## 7. Leakage and evaluation controls required in any revision

A defensible revision must freeze patient splits before thresholds, detector tuning, or model comparison. Automatic-triad thresholds and synthesis/generator development belong only in training/development data. Expert construct validation and the model-use endpoint need separate held-out patients. If the expected support is only about 8–15 cases, this separation may make the study impossible within ISLES'24 alone; cross-validation cannot turn model-selection data into confirmatory evidence. Multiple territories from one patient must be patient-clustered, and every authorized model seed and edit arm must be reported.

## 8. Plain-pitch fidelity

The pitch mostly preserves the card's speculative wording (“may,” “asks whether,” and the conditional proceed language). One phrase overclaims: “if the pattern can be separated from ordinary edema and scan-timing effects.” The technical card explicitly says within-case ratios and the conjunction **cannot fully solve CTA phase**, and its keystone admits single-phase CTA may not distinguish the pattern without expert labels. The pitch turns mitigation into possible separation and omits the crucial fact that the expected support (~11) is below the proposed 15-territory gate. This is a named pitch-fidelity defect. Revise it to say the study proceeds only if a validated detector finds adequate support, while CTA phase remains a residual limitation.

## 9. Is there a genuinely easier version?

The low-hanging data are real: ISLES'24 already supplies registered admission NCCT/CTA/perfusion, follow-up-MRI infarct masks, vessel-occlusion masks, and outcome data for 149 public cases. The clinical construct also has two prior expert-rated cohorts. What does **not** already exist is equally important: no released ISE label, no validated automatic ISE detector, no pial-collateral label, and no verified frozen high-performing model consuming the required NCCT/CTA information. Thus there is no low-hanging model-*use* experiment.

The easiest scientifically interpretable study is an expert-confirmed observational replication: blind readers to follow-up, label ISE on admission NCCT/CTA, and compare voxelwise infarction within ISE territories against matched Tmax-delayed, non-ISE territories after adjustment/matching for perfusion and location. Existing follow-up masks make the endpoint cheap; new expert ISE annotation is the unavoidable burden. This would test whether the 2015 tissue-sparing result transports to ISLES'24, not whether a model uses the sign. It is worth doing only if a rapid blinded census yields enough patients for a prespecified precision target; otherwise it is merely a tiny third case series.

For a subsequent model audit, the lowest-complexity useful endpoint is error stratification on those same real territories: compare a frozen model's local predicted infarct probability and false-positive burden in expert-confirmed ISE versus matched non-ISE delayed tissue. That is an association/error audit, not a use claim, but avoids invalid image synthesis. A causal use study should wait for a model and a joint-distribution-preserving intervention.

## Required revision/unblock conditions

1. Name and freeze a final-infarct model, checkpoint, exact input channels, preprocessing, training data, and untouched evaluation patients; verify that NCCT and CTA intensities—not merely an NCCT-derived brain mask—reach the model.
2. Replace the current edit with a joint-distribution-preserving intervention that includes the perfusion correlates of collateral engorgement, or reduce the claim to real-case error association.
3. Define the primary local continuous endpoint, expected direction, unit of analysis, clustering, multiplicity, and an effect/precision-based support gate rather than `>=15 territories` by fiat.
4. Validate the automatic construct against blinded expert ISE judgments, including detector-negative cases; treat this as new annotation burden.
5. Freeze all construct and edit-validity gates on development patients before model-output inspection. If the cohort cannot support disjoint development and evaluation sets, pause rather than call cross-validated exploration confirmatory.
6. Add PMID 32912520 as closest prior work and complete the primary full-text/citation-neighborhood audit.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: In successfully reperfused ISLES'24 patients, are expert-confirmed ISE territories less likely to infarct than perfusion- and location-matched Tmax-delayed territories without ISE?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes, as a spatial external validation with follow-up MRI if a blinded census meets a prespecified precision target; below that target it is not worth publishing as another underpowered case series.


===== ideas/027/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed counterfactual cannot identify model use of collateral-supported tissue viability because it creates the sulcal/vascular appearance while freezing the perfusion consequences that are part of the claimed collateral phenotype.

**Argument:** The clinical mechanism is not merely low sulcal CSF plus more pial-vessel voxels: in the primary ISE series, the eight ISE cases had CTA-visible engorged leptomeningeal vessels together with normal-to-increased CBV and prolonged Tmax (PMID 25931460; DOI 10.1161/STROKEAHA.115.009304). The card instead swaps sulcal-CSF fraction, vessel occupancy, and gray-white contrast while explicitly holding Tmax, CBF, and CBV fixed. A prediction change under that edit is therefore compatible with response to an abnormal CTA/perfusion combination or synthesis artifact, not specifically use of a viable collateral-supported state. Component and equal-volume controls do not distinguish those explanations because even the purported coherent arm is incoherent across the model's full multimodal input. This remains the original model-use question, but its current intervention does not instantiate the mechanism named in the deliverable sentence.

**What would change my mind:** Show a preregistered intervention that moves NCCT, CTA, and perfusion features jointly along the empirically observed ISE distribution, plus held-out evidence that blinded experts and a modality-consistency test cannot distinguish edited cases from real ISE cases, and demonstrate that the model response exceeds matched joint-distribution-preserving sham edits.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card's edit installs the ISE appearance on NCCT/CTA while freezing Tmax/CBF/CBV, but the verified clinical phenotype (PMID 25931460) is a joint package that includes normal-to-increased CBV and prolonged Tmax. Freezing perfusion therefore manufactures a cross-modal combination that may lie off the empirical ISE manifold, so a model response could reflect reaction to an impossible input, not use of the collateral-supported-viability signal — and the component controls cannot rescue this, because the supposedly coherent arm is itself incoherent across the model's full input.

**Response:** AMEND

**Argument:** The objection is correct as stated against the current card: an edit whose endpoint can land outside the observed joint NCCT/CTA/perfusion distribution cannot support the deliverable sentence, and the coherent-vs-incoherent contrast loses its force if the "coherent" arm is only coherent within the edited subset. I do not rebut that.

The amendment achieves cross-modal coherence by **recipient selection instead of perfusion synthesis**. The critic's condition was that the intervention endpoint must lie on the empirically observed ISE joint distribution; it did not require that perfusion be *moved* to get there. Concretely:

1. **Perfusion-congruence eligibility gate (new, preregistered before any model output).** Recipient territories must already exhibit the ISE-compatible perfusion profile reported in the primary series — prolonged Tmax with normal-to-increased CBV relative to the mirror territory, thresholds frozen at Stage 0. The triad edit is applied only into such territories. After the edit, the case carries ISE appearance + prolonged Tmax + preserved/elevated CBV: the verified joint phenotype, reached without synthesizing a single perfusion voxel. "Holding perfusion fixed" stops being incoherence-by-construction because the fixed values are ISE-consistent by selection. This also removes the critic's stated reason the component controls fail — with the coherent arm now coherent across the full multimodal input, isolated-CSF-deletion and vessel-only arms regain their discriminating role.
2. **Realism gate adopted from the critic's own condition (new).** Before any confirmatory readout, a blinded distinguishability test: edited territories versus real detector-positive ISE territories, judged by a modality-consistency check and blinded readers; failure to reach indistinguishability at the preregistered criterion kills the intervention arm. I note this concedes fresh annotation burden (blinded readers), which the card previously claimed to avoid; the charter permits it with the scoring penalty applied.
3. **Sham-edit exceedance (new).** The confirmatory contrast becomes: coherent-triad response must exceed matched joint-distribution-preserving sham edits (same edit machinery, same volume, applied to perfusion-congruent territories without installing the triad), not merely exceed zero.

**Identity check:** the one-sentence question — is the model using isolated sulcal effacement with preserved gray-white junction as a sign of viable collateral-supported tissue — is unchanged. What changed is the intervention's admissible support: the question is now answered on the subpopulation of perfusion-congruent delayed territories, which is exactly the subpopulation where the clinical phenotype lives. This is a narrowing of the evidence base, not a replacement of the question.

**What is lost, plainly:**

- **Support shrinks further below an already-marginal gate.** The keystone screen put expected donor support at ~11 territories against the card's ≥15 gate. The amendment adds pair-eligibility constraints (recipient perfusion congruence, location matching), so usable donor-recipient pairs will be fewer than donors. The probability that this idea dies at the Stage-0 census has gone up, and the census must now count eligible *pairs*, not positives.
- **The "no annotator" claim is gone.** The realism gate requires blinded expert reads; the card's annotation-free framing was one of its selling points and is withdrawn.
- **Coherence is enforced at the phenotype-category level only.** With eight cases in the primary series, the fine conditional structure (e.g., whether degree of vessel engorgement co-varies with degree of CBV elevation) is unknowable; selection cannot enforce correlations no source documents. This residual caps the claim at rung 1 regardless of gate outcomes, and the card's rung language must say so.

One residual the amendment does not solve, stated so the critic need not restate it: donor-to-recipient transplantation across patients can carry texture/geometry mismatch detectable by the model even when readers are fooled; the sham-exceedance arm bounds but does not eliminate this. And this round addresses only the identifiability objection; the critique's separate model-asset objection (no named frozen checkpoint verified to consume NCCT/CTA intensities) stands unanswered by this amendment and must be resolved before any feasibility memo.

**Status:** OPEN

## Round 2 — CRITIC

**Position:** The amended intervention still cannot answer the original model-use question because no frozen, non-trivially performing final-infarct model has been identified whose actual inputs include the NCCT and CTA intensities carrying the proposed sign.

**Argument:** The amendment passes the identity check: restricting recipients to perfusion-congruent delayed territories narrows the population but still asks whether a final-infarct model uses isolated sulcal effacement with preserved gray-white differentiation as a survival signal. Its recipient-selection, blinded-realism, and sham-exceedance gates adequately repair my Round 1 objection at the phenotype-category level. But those gates operate on an unspecified model. The critique records that the published winning residual nnU-Net's final-input table lists CTA, CBF, CBV, MTT, and Tmax, while NCCT is described as supplying the brain mask; on the available account, the NCCT sulcal-CSF and gray-white-intensity features central to the question may never reach that model. The public raw-4D-CTP alternative likewise does not consume the proposed NCCT/CTA triad and reportedly has Dice 0.20 and lesion-wise F1 0.02. Training a new model does not by itself solve this: its channels, preprocessing, split, performance gate, and untouched evaluation patients would have to be frozen before construct or edit development, especially because ISLES'24 exposes only 149 public cases and bespoke intervention analysis cannot be performed on the hidden challenge test cases. Until such an asset exists, a positive response is not a test of the named sign by a credible final-infarct model, and the experiment cannot even be specified without risking model-selection leakage.

**What would change my mind:** Identify and freeze a checkpoint with verified non-trivial held-out final-infarct performance; show from its executable preprocessing and forward path that registered NCCT and CTA voxel intensities, not merely an NCCT-derived mask, reach the network; and freeze disjoint model-training, construct/edit-development, and untouched intervention-evaluation patients before any model-output inspection.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** No existing frozen final-infarct model is verified to receive the NCCT and CTA intensities that carry the sign — the published winner's input table omits NCCT intensities (mask source only), and the public 4D-CTP alternative neither consumes the triad nor performs non-trivially. Training a bespoke model only helps if its channels, preprocessing, split, performance gate, and untouched evaluation patients are frozen before any construct or edit development, and 149 public cases must accommodate all three disjoint roles because the hidden test set cannot host per-case intervention analysis.

**Response:** AMEND

**Argument:** The fact base is conceded in full: no located checkpoint is verified to consume NCCT and CTA voxel intensities, and a model cannot use a sign it never receives. I read the critic's what-would-change-my-mind not as an impossibility claim but as a buildable specification, and this amendment adopts it wholesale as binding preconditions.

**Amendment — the model asset is constructed under a frozen preregistered protocol, with disjointness reconciled to 149 cases by a leave-two-folds-out ensemble:**

1. **Frozen training recipe, channel-verified.** The recipe is preregistered before any construct or edit development: the published winning residual nnU-Net configuration, modified in exactly one declared way — registered NCCT and CTA intensity volumes enter as input channels alongside the perfusion maps. Channel receipt is verified from the executable path, not the paper: perturb NCCT voxels in a declared region and assert the network's input tensor changes (the critic's mask-only failure mode is thereby excluded by test, not by reading).
2. **Disjointness via leave-two-folds-out.** A fixed development quarantine (~30 patients) is carved out first; detector thresholds, edit machinery, realism-gate calibration, and sham-edit tuning live only there, and those patients are never donors or recipients. The remaining ~119 patients are partitioned into 5 folds; the frozen recipe is trained once per fold-pair-exclusion (10 trainings). Every confirmatory intervention with donor d and recipient r is scored only by the ensemble member whose training excluded both d's and r's folds. No model ever scores a patient it trained on, and no donor tissue a scoring model could have memorized enters its inputs. The fold assignment is frozen at Stage 0, before any model output exists.
3. **Performance gate with kill semantics.** Each ensemble member must reach a preregistered Dice floor on its own excluded folds — floor set from published challenge results as context, explicitly not a same-split comparison — before any edit is scored. A member that misses the floor kills the arm; it is not reinterpreted or retrained.

**Identity check:** the card's question says "an ISLES'24 multimodal model," indefinite by its own wording, and a frozen trilogy-consuming model trained on ISLES'24 under a preregistered recipe is an instance of it. The one-sentence question is unchanged. But I state the pragmatic shift plainly rather than hide it behind the wording: a natural reading of the card was "audit the benchmark's winning model," and that reading is now known to be unanswerable — on the verified account the winner is structurally blind to the NCCT half of the sign. If the human judges that the pragmatic reading was the claim's identity, this idea dies here and the bespoke-model study registers as a successor; I judge it survives because the card never named the winner and the motivating question — does this sign carry a survival signal a model that can see it will use — is the one the amended design answers.

**What is lost, plainly:**

- **The audit framing is gone.** The deliverable is now scoped to a model family we train ourselves: "a competently performing multimodal model consuming the full CT trilogy uses/does not use the sign." That is weaker audience-relevance than auditing a deployed or winning system, and the card must say so. One corollary is worth recording because it survives even if the idea dies at Stage 0: if the published input table is accurate, the benchmark's winning configuration cannot exploit the NCCT-borne components of a clinically documented viability sign — a benchmark-design observation, not a new candidate.
- **The compute claim was hiding the model.** "Under 15 GPU-hours after model training" is withdrawn; ten nnU-Net trainings put honest compute at order 100+ GPU-hours plus the census and synthesis work, and "about two weeks" becomes several weeks.
- **Support arithmetic worsens a second time.** The development quarantine removes ~30 patients from the donor pool; at the verified 7.4% base rate the expected detector-positive donors in the remaining ~119 are ~9, before round 1's pair-eligibility constraints. Against a support gate that must now be precision-derived rather than >=15-by-fiat (critique condition 3), the most probable outcome is that the Stage-0 census kills this idea. I state that as the expected result, not a residual risk: the design is now defensible and the cohort is probably too small for it.

**Amendment tally, per the rules:** this is the second structural amendment, and both repaired the same underlying defect — the card was written without either a coherent intervention or a model that could receive it. If the next objection requires a third structural amendment, I will concede rather than amend.

**Status:** OPEN

## Round 3 — CRITIC

**Position:** The bespoke leave-two-folds-out model changes the claim from auditing whether a final-infarct model uses the clinical sign to asking whether a model deliberately built to see that sign can learn to use it, so the amendment fails the identity check and belongs in a successor candidate.

**Argument:** The Round 2 amendment is a substantive answer to the asset and leakage objection: executable-path verification would establish receipt of NCCT/CTA intensities, pair-excluded scoring would prevent direct donor or recipient training leakage, and a frozen performance gate would prevent interpreting an incompetent model. But those safeguards solve a different study. The existing deliverable sentence is definite—“The final-infarct model is using...” —and the card frames a model-use audit whose scientific value comes from discovering what a benchmark model already uses. The amendment instead modifies the winner’s architecture by adding NCCT and CTA channels, trains ten new models, and explicitly replaces the deliverable with a family-scoped statement about “a competently performing multimodal model consuming the full CT trilogy.” A positive result could then arise because the investigator-created input design and ISLES'24 training correlations enabled the new family to learn the sign; it would not establish that the original benchmark model, or any independently existing final-infarct model, uses it. This is not merely narrower scope: the audited object and the deliverable sentence both change. The repository’s 2026-08-10 claim-identity rule requires a new candidate when the deliverable sentence changes, even if the successor experiment is technically defensible. The proposer’s appeal to the indefinite wording in the question does not overcome the definite deliverable, the original audit framing, or its own express concession that “the audit framing is gone.”

**What would change my mind:** Produce an independently existing, frozen, non-trivially performing final-infarct checkpoint whose original executable forward path already consumes NCCT and CTA intensities, so the revised protocol audits rather than creates the model behavior; otherwise register the bespoke full-trilogy model experiment as a successor with idea 027 as its parent.

**Status:** CONCEDED

## Round 3 — PROPOSER

**Responding to:** The Round 2 amendment does not repair idea 027; it replaces it. The original deliverable sentence is definite — "The final-infarct model is using..." — and the study's value came from auditing what an existing benchmark model already does. Building ten new models with investigator-added NCCT/CTA channels changes both the audited object and the deliverable sentence, and under the repository's 2026-08-10 claim-identity rule a changed deliverable sentence means REJECT (superseded) plus a new registered successor, regardless of the successor's technical merit.

**Response:** CONCEDE

**Argument:** The objection is correct, and I concede on three independent grounds rather than attempt a rebuttal.

First, the claim-identity ruling is right on its own terms. I argued in round 2 that the question's indefinite wording ("an ISLES'24 multimodal model") licensed a bespoke instance, but the critic correctly ranks the definite deliverable sentence above the indefinite question wording — the 2026-08-10 rule keys identity to the deliverable sentence, and mine changed from "the final-infarct model is using the sign" to a family-scoped statement about a model trained to be able to see it. Those are different claims with different epistemic content: an audit discovers behavior that exists independently of the investigator; the bespoke design measures the learnability of a signal under an input configuration I chose. A positive in the second study says nothing about any model anyone actually deployed or benchmarked. I flagged this exact fork in round 2 ("if the human judges that the pragmatic reading was the claim's identity, this idea dies here") and the critic has now made the case that ruling should go against survival; I have no new argument on the other side.

Second, the critic's remaining escape route — produce an independently existing, frozen, non-trivially performing checkpoint whose original forward path already consumes NCCT and CTA intensities — is not something I can satisfy. The critique stage searched: the published winner's input table omits NCCT intensities (mask source only) and the one public alternative consumes raw 4D CTP at Dice 0.20. Asserting that such a checkpoint exists somewhere unverified would violate the primary-source rule; hoping one appears is not a defense.

Third, I bound myself in round 2: two structural amendments had already repaired the same underlying defect — the card was written with neither a coherent intervention nor a model that could receive the sign — and I said a third would mean concession. Answering this objection within idea 027 would require exactly that third amendment. Per the debate rules, the card as scouted was wrong about its two load-bearing enablers, and speed of concession from here is the only value left to add.

**Spin-off (for registration as successors with parent_id idea-027, not defended here):**

1. **Bespoke trilogy-model learnability study** — the full Round 1 + Round 2 amended design (perfusion-congruent recipient selection, blinded realism gate, sham-edit exceedance, frozen leave-two-folds-out recipe with channel-receipt verification, kill-semantics performance floor). Honest deliverable: "a competently performing multimodal model trained to consume the full CT trilogy does/does not use isolated sulcal effacement with preserved gray-white differentiation as a survival signal." Registers with its known burdens: ~100+ GPU-hours, fresh annotation for the realism gate, and an expected-fatal Stage-0 support census (~9 expected donors in the post-quarantine pool before pair-eligibility constraints).
2. **Benchmark-design observation (cheap, survives this death)** — if the winning system's published input table is accurate, the ISLES'24 benchmark's winning configuration is structurally blind to the NCCT-borne components of a clinically documented viability sign (PMID 25931460). Verifying this from the winner's released code/configuration rather than the paper table is a small, model-free evaluation-rigor finding aligned with the lab's benchmarking interest.
3. **Observational ISE replication** — already recorded by the critique as the nearest defensible high-value question: in successfully reperfused ISLES'24 patients, are expert-confirmed ISE territories less likely to infarct than perfusion- and location-matched Tmax-delayed territories without ISE? Requires new expert annotation and a precision-gated census; it tests the clinical claim's transport, not model use.

Idea 027 should be recorded as REJECTED (superseded) with the identity-rule citation, and its verified assets — the keystone screen's dataset facts, the 7.4% base-rate arithmetic, and the two amended gate designs — pass to the successors through parent lineage.

**Status:** CONCEDED


===== ideas/027/idea_card.json =====
{
  "id": "isles24-scout-003-c05",
  "parent_ids": [],
  "search_mode": "C",
  "entry_point": 2,
  "title": "When vanished sulci mean rescue, not death",
  "question": "Is an ISLES'24 multimodal model using isolated sulcal effacement with preserved gray-white junction as a sign of viable tissue supported by engorged collaterals?",
  "rung": "Mode C target rung 1 use of an automatic isolated-effacement index; rung 3 language about viable collateral-supported tissue requires external physiological validation.",
  "deliverable_sentence": "The final-infarct model is using isolated sulcal effacement with preserved gray-white differentiation as a tissue-survival signal.",
  "X_measurement": "Within the Tmax-delayed territory, automatically quantify affected/mirrored sulcal CSF fraction from NCCT and retain voxels whose local gray-white HU contrast is within 1 SD of the mirror; combine this with CTA pial-vessel volume in the same region. The clinical sign and its association with preserved tissue were reported in 108 LVO cases, 8 with isolated sulcal effacement and no follow-up infarct in the effaced area (PMID 25931460). Compute-today test: YES from registered NCCT, CTA, and Tmax using automatic CSF/tissue/vessel segmentation; no annotator.",
  "suspected_signal": "Dilated leptomeningeal collateral vessels can crowd cerebrospinal-fluid spaces and efface sulci while preserving underlying tissue attenuation; unlike edema-driven effacement, this pattern may mark robust collateral filling and reversibility.",
  "use_vs_association": "Counterfactual synthesis swaps the local triad\u2014sulcal CSF fraction, pial-vessel occupancy, and preserved gray-white contrast\u2014between matched delayed territories while holding Tmax/CBF/CBV, tissue location, and total edited volume fixed. A survival-directed output change must occur only for the coherent triad, not isolated CSF deletion or vessel addition.",
  "keystone_prerequisite": "ISLES'24 contains enough automatically detectable isolated-sulcal-effacement territories, and single-phase CTA plus NCCT can distinguish the collateral-engorgement pattern from edema and registration error without new expert labels.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_residual_assumption": "The published sign occurred in only 7.4% of a selected LVO cohort. With 149 ISLES cases, expected support may be single digits, and the automatic construct has never been validated here; this is the real keystone.",
  "rung_reached": "0; rung 1 after support, construct, and coherent-triad gates; rung 3 only with external multiphase/dynamic collateral validation.",
  "dies_like_prior": "Resembles idea-005's ANNOTATION_PROVENANCE risk if a radiologist's call defines the sign. This card avoids annotator-dependent input by prespecifying an image-computable triad, but construct validity is weaker and honestly capped. It also differs from isles24-scout-001-c02 by testing a parenchymal-sulcal sign of collateral support rather than distal arterial reach itself.",
  "closest_prior_work": "The primary case series defined isolated sulcal effacement and linked it to engorged leptomeningeal vessels and spared follow-up tissue (PMID 25931460). Quantitative CTA collateral scoring is acquisition-phase sensitive (PMID 29674417). No located work tests model use of the coherent sign; the rarity and phase dependence make this a deliberately speculative candidate.",
  "existing_assets": "Registered NCCT/CTA/perfusion maps, final MRI masks, automatic tissue and vessel segmentation tools, and a precise prior clinical phenotype.",
  "smallest_decisive_experiment": "Stage 0 on all 149 cases: compute the triad blind to outcomes; require >=15 territories meeting fixed thresholds, stable detection under registration perturbation, and stronger ipsilateral pial-vessel occupancy without reduced gray-white contrast. If passed, run coherent and incoherent edits on the held-out subset. Two weeks; under 15 GPU-hours after model training.",
  "standing_confounds_addressed": "Within-territory matched edits hold scanner, vendor, protocol, site, habitus, prevalence, and referral; fixed perfusion maps separate the sulcal sign from measured delay/flow. CTA phase, edema, registration, and rarity remain major threats. Follow-up labels are secondary; primary evidence is paired model-output change.",
  "alternative_explanations": [
    "Effacement is edema, not collateral engorgement; preserved gray-white contrast plus pial-vessel occupancy is the discriminating conjunction.",
    "Single-phase CTA catches different bolus phases; within-case affected/mirror ratios help but cannot fully solve this.",
    "The coherent edit is simply more complex; each incoherent component and equal-volume controls quantify generic edit response."
  ],
  "anticipated_negative": "Uninterpretable if fewer than 15 territories or construct gates fail; sensitivity-limited even after gates because the sign is rare. Accordingly negative-result value is capped at 2.",
  "remaining_legwork": "4-5 days automatic census and stability analysis, 3 days support review, 4-5 days synthesis: about two weeks if the rarity gate passes.",
  "design_template": "counterfactual-synthesis",
  "entry_point_2_requirements": "Measurement: low sulcal CSF fraction plus preserved gray-white contrast plus increased pial-vessel occupancy. Confused artifact: edema, registration, and CTA phase; the conjunction, perturbation stability, and within-case ratios address but do not eliminate them.",
  "scores": {
    "mechanism_clarity": {
      "value": 5,
      "why": "A specific anatomical mechanism\u2014collateral vessels occupying sulci\u2014with three measurable components."
    },
    "identifiability": {
      "value": 3,
      "why": "The coherent-versus-incoherent edit is discriminating, but CTA phase and construct validity remain."
    },
    "interest": {
      "value": 5,
      "why": "It reverses the usual reading of effacement from injury to possible rescue."
    },
    "medical_relevance": {
      "value": 4,
      "why": "Mistaking reversible tissue for core can affect treatment interpretation."
    },
    "clarity": {
      "value": 4,
      "why": "The conjunction is explicit but thresholds require preregistration."
    },
    "prior_legwork": {
      "value": 2,
      "why": "One small clinical series exists; automatic measurement is unvalidated."
    },
    "feasibility": {
      "value": 2,
      "why": "Reported outside Mode C score; rarity may kill it immediately."
    },
    "data_readiness": {
      "value": 3,
      "why": "All modalities are public, but support is unknown."
    },
    "evaluation_readiness": {
      "value": 2,
      "why": "Construct and synthesis gates are custom."
    },
    "negative_result_value": {
      "value": 2,
      "why": "Capped because rarity makes a null potentially uninterpretable."
    },
    "novelty_confidence": {
      "value": 2,
      "why": "Targeted search only and a niche sign invites missed literature."
    },
    "regret": {
      "value": 4,
      "why": "If support exists, ISLES'24 uniquely couples the sign to final tissue fate."
    }
  },
  "mode_c_priority_score": 4.15,
  "unverified_claims": [
    "at least 15 qualifying territories",
    "automatic triad validity",
    "CTA phase adequacy",
    "edit realism",
    "novelty"
  ],
  "plain_pitch": "Flattened brain grooves usually sound like swelling and damage, but one rare stroke pattern may instead come from enlarged rescue vessels filling those grooves while the tissue remains intact. This study asks whether the model recognizes that full pattern. It proceeds only if enough cases can be found automatically and if the pattern can be separated from ordinary edema and scan-timing effects.",
  "track": "baseline",
  "charter": "isles24"
}


===== ideas/027/keystone_screen.md =====
# Keystone screen — idea 027 (isles24-scout-003-c05)

**Card:** "When vanished sulci mean rescue, not death"
**Stage:** keystone screen, run 2026-08-18.

## The keystone as stated

> "ISLES'24 contains enough automatically detectable isolated-sulcal-effacement
> territories, and single-phase CTA plus NCCT can distinguish the
> collateral-engorgement pattern from edema and registration error without new
> expert labels."

Two clauses: (a) sufficient support in the cohort (the card's own Stage-0 gate
is >=15 qualifying territories); (b) the released modalities can carry the
discriminating triad without new annotation.

## What was inspected

### 1. ISLES'24 dataset composition (charter hard rule + keystone clause b)

**Primary data-hosting page** — Zenodo record 16813698, "ISLES'24 — A
Real-World Longitudinal Multimodal Stroke Dataset"
(https://zenodo.org/records/16813698), fetched 2026-08-18:

- Per-case imaging (verbatim): admission "non-contrast CT (NCCT), CT
  angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps
  (Tmax, CBF, CBV, MTT)" plus "post-treatment MRI (DWI and ADC)" at follow-up.
- Cohort (verbatim): "149 acute ischemic stroke cases" — the released
  training set. Matches the card's "all 149 cases".
- Registration (verbatim): raw data "released in their original space, just
  defaced"; derivatives with "all modalities linearly co-registered to the
  NCCT space". The card's assumption of registered NCCT/CTA/perfusion maps
  holds in the derivatives release.
- Ground truth (verbatim): "binary infarct masks derived from follow-up MRI
  (lesion-msk.nii.gz)".
- License: Creative Commons Attribution Non Commercial Share Alike 4.0
  International. Public download (train.7z, 99.0 GB).

**Challenge paper** — arXiv:2408.10966 ("ISLES'24: Final Infarct Prediction
with Multimodal Imaging and Clinical Data"), Methods/Dataset section, fetched
2026-08-18:

> "acute imaging data have been acquired at patient admission and include the
> diagnostic CT trilogy: NCCT, CTA, and CTP, as well as CTP-derived perfusion
> maps (namely CBF, cerebral blood volume (CBV), mean transit time (MTT), and
> time-to-maximum of the residue function (Tmax)). The follow-up imaging data
> were acquired 2 to 9 days later and included DWI and ADC."

> "Preprocessing of the images has been performed by linearly interpolating
> and registering all the imaging series to the NCCT scans."

> "Lesion masks are derived from the follow-up MRI using DeepISLES. Quality
> control and correction of the lesion masks are performed when needed by
> medical students supervised by two neuroradiologists with more than 10
> years of experience."

Cohort selection (Discussion/Limitations, verbatim):

> "the inclusion criteria of the ISLES'24 dataset were restricted to patients
> with favorable recanalization outcomes (i.e., thrombolysis in cerebral
> infarction -TICI- scores 2B and 3)."

Split accounting (Methods, verbatim): "The dataset (N = 248) is split into
train (N = 150) and test subsets (N = 98)." The public Zenodo release states
149; the one-case discrepancy between the paper's split table and the released
training set is noted, non-blocking, and consistent with the card's 149.

### 2. The cited clinical series (the base rate behind clause a)

**PMID 25931460** — abstract retrieved via NCBI E-utilities
(https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=25931460&rettype=abstract&retmode=text),
Stroke. 2015 Jun;46(6):1704-6, fetched 2026-08-18. Verbatim:

- "Out of the 568 patients who underwent intra-arterial therapy between March
  2011 and September 2014, 108 fulfilled inclusion criteria."
- "ISE was present in 8 (7.4%) patients"
- "Follow-up imaging confirmed no infarct in the ISE area in all patients"
- "Computed tomography angiogram revealed engorged/dilated leptomeningeal
  vessels obliterating the sulci within the areas of effacement"

The card's factual citations (108 cases, 8 with the sign, no follow-up infarct
in the effaced area, CTA-visible engorged vessels) are transcription-accurate.

## The support-count arithmetic (inference, not verified fact)

Both cohorts are endovascular-therapy populations (the series: intra-arterial
therapy; ISLES'24: thrombectomy with TICI 2B/3), so the 7.4% base rate is at
least the right population family. Scaled to 149 cases: expected support
~11 territories. Hand-computed Clopper-Pearson 95% interval for 8/108 is
approximately 3.3%-14.0%, i.e. roughly 5 to 21 cases in 149. The point
estimate falls BELOW the card's own >=15 Stage-0 gate; the interval spans
both failure and pass. The automatic triad is additionally not the same
construct as the radiologist-called sign, so its firing rate may differ in
either direction. This clause is therefore genuinely undecidable from
primary sources — it is exactly what the card's Stage-0 census (blind,
cheap, no model needed) exists to decide.

## Residual assumption check (mandatory follow-up)

If this card only verified the nearest checkable things (modalities exist,
the series says what it says), it is still assuming:

1. **Support >=15** — undecidable without the census; point estimate ~11 is
   short of the gate (above).
2. **Construct validity of the automatic triad** — that sulcal-CSF fraction +
   preserved gray-white contrast + pial-vessel occupancy computed from the
   registered volumes reproduces the radiologist's sign. No primary source
   can settle this; the card honestly gates on it.
3. **NCCT/CTA spatial quality** — the real-world admission NCCT slice
   thickness is not stated in the challenge paper or the Zenodo record I
   could access; thick-slice NCCT would degrade automatic sulcal-CSF and
   gray-white measurement. Unverified either way; forward to Stage 0 as an
   explicit early check.
4. **CTA phase adequacy** — single-phase CTA timing variability (the card
   cites PMID 29674417) remains a stated, unresolved threat; the dataset
   provides no multiphase CTA to rescue it.

The card's stated keystone and its `keystone_residual_assumption` field
already name (1) and (2) as the real keystone — no wrong-keystone error
found. The load-bearing assumption the card states is the load-bearing
assumption that exists.

## Verdict

All checkable enabling facts verified TRUE with quotes: the dataset publicly
provides every modality the triad needs, co-registered to NCCT space, with
follow-up-derived lesion masks, on a 149-case thrombectomy cohort. The
keystone's decisive clause — enough detectable territories — cannot be
verified or falsified from any primary source; it requires the Stage-0
census, and the verified base-rate arithmetic says the outcome is marginal
(expected ~11 vs. a >=15 gate). Not demonstrably false, so not a KILL;
not verifiable, so not a PASS.

```json
{"verdict": "UNVERIFIABLE", "evidence": "ISE was present in 8 (7.4%) patients", "source": "PMID 25931460 (Stroke. 2015;46(6):1704-6), abstract via NCBI E-utilities efetch", "note": "All modality/registration/access prerequisites verified true on Zenodo 16813698 and arXiv:2408.10966; the support-count clause is undecidable pre-census, with expected ~11 territories vs the card's own >=15 gate (95% CI spans 5-21)."}
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
