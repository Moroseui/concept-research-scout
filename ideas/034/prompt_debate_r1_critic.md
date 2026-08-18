You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/034
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

- **IDENTIFIABILITY_FAILURE** x6: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
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
- **idea-034** [SHORTLISTED/CRITIQUED/wide] -- The edge of the map: the benchmark scores terra incognita
- **idea-035** [SHORTLISTED/SCOUTED/wide] -- The skull is a fixed-volume pressure vessel
- **idea-036** [SHORTLISTED/SCOUTED/baseline] -- Does the model bring a vascular map to the scan?
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


===== ideas/034/README.md =====
# Idea 034: The edge of the map: the benchmark scores terra incognita

Selected from scouting cycle isles24-004, candidate 7.


===== ideas/034/critique.md =====
FATAL OBJECTION: The proposed observational stage 2 cannot distinguish use of the slab boundary itself from use of the perfusion evidence that necessarily disappears at that boundary, so it cannot support the deliverable sentence.
EVIDENCE: Official ISLES'24 repository task definition; `ideas/034/idea_card.json` (`use_vs_association`, `standing_confounds_addressed`); ISLES 2018 analysis, PMCID PMC8240494.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial review

## 1. What is verified, and what is not

Verified fact: ISLES'24 asks algorithms to predict follow-up infarct lesions from acute NCCT, CTA, CTP/perfusion maps, and clinical tabular data. The official repository lists Dice, absolute volume difference, absolute lesion-count difference, and lesion-wise F1 as ranking metrics (official repository: https://github.com/ezequieldlrosa/isles24; challenge paper: arXiv:2408.10966).

Source-supported fact, with the provenance limitation already recorded in `keystone_screen.md`: the official challenge forum contains a report that case 0019 has 1,685 labeled lesion voxels outside the CTP extent, and the organizer says such voxels are not masked from evaluation. This verifies existence in kind, not the card's population threshold of overflow greater than 5% in at least 10% of cases.

Verified prior legwork: limited CTP coverage is not a hidden problem newly imported from remote sensing. The retrospective ISLES 2018 analysis states that CTP coverage ranged from 2.4 to 16 cm and that lesion prediction was performed only within the acquired image volume; it explicitly discusses the effect of limited coverage on absolute volumetric error (PMCID PMC8240494; PMID 33957774; DOI 10.1161/STROKEAHA.120.030696). A prior benchmarking tool likewise evaluated CTP against DWI with 4.4–16 cm coverage (PMCID PMC5076783; DOI 10.1177/0271678X15610586). The exact ISLES'24 whole-cohort census may still be unreported, but the card's claim that the challenge community has not asked what the sensor saw is too broad and its `why_not_done` story is speculation.

## 2. Fatal identifiability failure in the model claim

The deliverable says the model uses the *support boundary* as a determinant, “rather than the ischemia.” The proposed comparison is across patients at atlas locations that happen to be inside versus outside their CTP slabs. That exposure changes at least three things together:

- availability of every perfusion value;
- acquisition protocol/scanner and cranio-caudal positioning;
- anatomical and stroke-population mix near each slab edge.

Matching on NCCT appearance, CTA appearance, atlas location, and lesion volume cannot make the missing perfusion evidence equal. Indeed, the card concedes that “out-of-slab voxels genuinely have less evidence.” A prediction discontinuity can therefore be caused by ordinary use of local CBF/Tmax evidence; it does not show that the network treats the padding/support indicator as a spatial stopping rule. Conditioning on lesion volume also uses the follow-up outcome and does not restore exchangeability.

Calling the estimand merely “how models behave” does not repair the mismatch. The title, question, rung, deliverable sentence, and plain pitch all make a use claim contrasting the sensor edge with the injury edge. The observational estimator identifies an association between prediction and evidence availability, not use of the boundary cue. A within-case crop intervention would still remove true perfusion evidence while moving the boundary and would introduce a training-distribution shift; it has the same mechanistic ambiguity in a different form. No specified obtainable contrast moves the boundary while preserving the perfusion evidence whose disappearance defines that boundary.

This dies by the portfolio's recurrent `IDENTIFIABILITY_FAILURE`: the claimed mechanism cannot be separated from a co-varying acquisition property. Removing stage 2 changes the deliverable from a model-use claim to a dataset/evaluation audit, which is a different question and therefore a successor under the claim-identity rule in `evidence/decisions.md`.

## 3. The “sensor-respecting performance ceiling” is mislabeled

For a prediction constrained to support \(S\), the label clipped to \(S\) gives an oracle maximum Dice of \(2|Y \cap S|/(|Y|+|Y \cap S|)\). That is a valid *CTP-support-constrained oracle score*. It is not a ceiling for an ISLES'24 algorithm, because an eligible algorithm can use NCCT, CTA, anatomy, and clinical variables rather than confining predictions to the CTP slab. The official task is not CTP-only.

The analogous minimum absolute volume difference is also not generally determined by overflow. A support-confined mask may match the total lesion volume by adding false-positive voxels inside the slab, producing zero absolute volume difference whenever enough support volume exists. Thus “minimum absolute volume difference attainable by ANY prediction confined to the support” may be zero even when much of the lesion lies outside support. If the intended oracle forbids false positives or fixes the in-support prediction to the in-support label, that is a different, explicitly constrained quantity—not the metric's mathematical minimum.

Nor does either oracle say “how much [overflow] could move the leaderboard.” Actual rank sensitivity requires team predictions (or at least controlled synthetic prediction families), all four metrics, per-case rank aggregation, and the hidden test cohort. Training-set oracle penalties do not determine a leaderboard displacement. This is repairable within the dataset-audit successor by reporting descriptive overflow, a clearly named CTP-confinement Dice penalty, and metric sensitivity under explicit counterfactual scoring rules; it does not rescue the current model-use question.

## 4. Relevance, circularity, leakage, access, and cost

There is no concept-label circularity: the label is appropriately the object being audited. There is also no training leakage in the model-free census. But stage 2's proposal to compare a model on the same 149 labeled cases used to characterize the phenomenon is underspecified: it names no frozen checkpoint, training cohort, held-out split, or independently preserved evaluation set. The card itself says the “shared audit model” may not exist. Therefore the stated under-five-GPU-hour estimate omits model acquisition/training and cannot be credited as concrete feasibility.

The stage-1 data are available and the compute is genuinely low. The 99 GB archive noted in the keystone screen is manageable, and derivative maps plus masks may be obtainable more cheaply from the mirror. No new annotation is needed. These strengths favor the narrower audit; they do not compensate for the invalid mechanistic endpoint.

The negative-result claim is only partly sound. Near-zero overflow would be useful reassurance about the *149 released training cases under the chosen support definition*. It would not establish that “ISLES'24's sensor coverage matches its scoring target” on the hidden test cohort unless the test geometry and overflow distribution are released or organizer-verified. A stage-2 null would be sensitivity-limited because an observational discontinuity test can miss diffuse, learned handling of missing perfusion or be underpowered in the small joint-support strata.

## 5. Plain-pitch fidelity failure

The pitch does not preserve the card's limitations:

- “their main sensor never saw” collapses a multimodal task into CTP; NCCT and CTA still image those locations.
- “each model must invent its own policy there” overstates the dilemma: a model may infer from NCCT, CTA, anatomy, clinical variables, and learned spatial priors rather than merely truncate or hallucinate.
- “how much that could move the leaderboard” promises an analysis not specified or supported by the proposed oracle calculation.
- “checks whether models draw their predicted damage boundary at the sensor's edge rather than the injury's” states the causal contrast more strongly than the admitted evidence-availability confounding permits.
- “Either outcome changes how results on this benchmark should be read” generalizes a training-cohort finding to the unreleased test cohort.

These are material overclaims, not harmless simplifications.

## 6. Easier formulation and existing low-hanging fruit

The low-hanging-fruit experiment is a model-free, training-set coverage audit. All required inputs already exist: 149 released labels, raw perfusion maps, NCCT-space derivative maps, official evaluation code, and a named positive case from the challenge forum. It should preregister at least two support definitions (raw 4D spatial extent and nondegenerate-map support), require agreement or adjudicate discrepancies, report per-case lesion fraction and lesion-component count outside support, stratify by scanner/protocol where metadata allow, and show sensitivity to registration/erosion-dilation of the support edge.

The primary endpoint should simply be the empirical proportion of released cases with more than 5% of labeled lesion volume outside CTP support, with a binomial interval and the full distribution. Secondary outputs can include a precisely named CTP-confinement oracle Dice and rescoring of public predictions if such predictions are actually available. Do not call anything a leaderboard effect without prediction submissions and the official aggregation. Confirm the forum posts directly through registered access before publication.

This is worth doing because it cheaply quantifies a documented but currently unmeasured evaluation condition in the released ISLES'24 cohort and can motivate an observed/unobserved-region metric breakdown. Its claim is narrower: it says what fraction of the reference target lacks CTP coverage, not what a multimodal model uses.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: In the 149 released ISLES'24 training cases, what fraction of follow-up lesion volume and lesion components lies outside acute CTP support, and what Dice constraint does that impose specifically on predictions confined to that support?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—because the data, labels, and metric code already exist, and a one-session census would replace an organizer-acknowledged anecdote with a cohort-level benchmark-integrity result, provided claims remain training-cohort and CTP-coverage specific.


===== ideas/034/debate.md =====
# Debate transcript



===== ideas/034/idea_card.json =====
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
}


===== ideas/034/keystone_screen.md =====
# Keystone screen — idea 034 (isles24-scout-004-c07)

Stage run 2026-08-18. Screener: keystone stage, full network access, sandboxed
execution (no local data downloads possible; see §4).

## 1. The keystone as stated

From `idea_card.json`, `keystone_prerequisite`:

> The released perfusion support is actually narrower than the brain in a
> non-trivial fraction of cases, and ground-truth lesion mass overflows it in
> enough cases to matter (prespecified: overflow > 5% of lesion volume in
> >= 10% of cases).

`keystone_status` on the card: `NOT_INSPECTED`.

## 2. What I inspected

### 2a. Primary papers: coverage is genuinely undocumented (confirms the card's negative claim)

- **Dataset paper** (arXiv 2408.11142, "ISLES'24 — A Real-World Longitudinal
  Multimodal Stroke Dataset"; published as Radiology: Artificial Intelligence,
  DOI 10.1148/ryai.250603). Full-text extraction (via jina reader over
  https://arxiv.org/pdf/2408.11142) found **no statement of CTP z-coverage,
  slab thickness, slice count, or perfusion-map spatial extent**. The scanner
  list is stated:
  > "CT image acquisition was performed on the following devices: Somatom
  > Force, Somatom Xcite (Siemens Healthcare), Somatom AS+ (Siemens),
  > Brilliance 64, and Ingenuity (Philips Healthcare)."
  The only coverage remark concerns CTA, not CTP ("Since the CTAs were cropped
  uniformly and cover only the head and not the neck…"). Perfusion maps:
  > "perfusion maps (cerebral blood flow, cerebral blood volume, mean transit
  > time, and time-to-maximum) were derived using the clinical, U.S. Food and
  > Drug Administration–cleared software icobrain cva (version 1.5.0,
  > icometrix)."
- **Challenge paper** (arXiv 2408.10966v2, HTML): no passage on CTP coverage,
  slab, missing slices, or lesions beyond CTP extent, in methods, team
  descriptions, or limitations (targeted extraction, two passes).
- **Winning-team preprocessing paper** (arXiv 2505.18424v1): no mention of
  perfusion coverage or map/ground-truth extent mismatch.

Inference (labeled as such, not load-bearing): a Philips Brilliance 64 is a
64-row scanner whose CTP acquisitions are physically slab-limited; its
presence in the device list makes whole-brain CTP for all cases implausible.
This inference was NOT used for the verdict; direct evidence follows.

### 2b. The decisive evidence: the challenge's own forum thread

An official ISLES'24 Grand Challenge forum thread exists titled **"How will
lesion voxels outside the field of view of the CTP imaging be handled?"**
Canonical URL (301 target of the indexed Grand Challenge forums URL):
`https://isles-24.grand-challenge.org/forum/topics/how-will-lesion-voxels-outside-the-field-of-view-of-the-ctp-imag/`
(indexed form:
`https://grand-challenge.org/forums/forum/ischemic-stroke-lesion-segmentation-challenge-2024-722/topic/how-will-lesion-voxels-outside-the-image-extent-of-the-baseline-imaging-be-handled-2451/?post=6348`).

Content retrieved via search-engine index of that page (provenance caveat in
§2c). Participant report, quoted:

> "For a number of patients in ISLES'24, the field of view captured by the
> CTP is smaller than that of the DWI, and as a result, some tissue that is
> visible on DWI simply was not imaged via CTP. In many cases, some of the
> tissue that was imaged via DWI but not CTP (these voxels are completely
> empty in the derived CTP images) are segmented as part of the lesion."

> "For patient 0019, for example, there are 1685 voxels (occurring on slices
> 58, 59 and 60) that were segmented as lesion on DWI, but are outside the
> image extents of the CTP data."

> "It is impossible to predict this part of the lesion using information from
> the CTP data since the CTP image is completely blank on the slices where
> this part of the lesion occurs."

Organizer response (same thread, retrieved the same way):

> the organizers "are not masking out voxels outside the field of view, as
> the lesions do exist in the considered brain, and the reduced field of view
> is just a technical limitation" — because "this is a lesion segmentation
> challenge (not a sole CTP-centered lesion segmentation challenge)."

This establishes, on the challenge's own record, all qualitative components
of the keystone: (i) CTP support narrower than the scored target in "a number
of patients" of this release; (ii) ground-truth lesion mass overflowing the
support in a concrete released training case (patient 0019, 1685 voxels,
slices 58–60); (iii) out-of-support voxels are deliberately NOT masked in
evaluation, so the overflow is scored — the metric consequence the idea
targets is real, and is an explicit organizer design decision; (iv) the
out-of-support region is "completely empty" in the derived maps, directly
supporting the card's assumption that support masks are recoverable from map
degeneracy.

### 2c. Provenance caveat on the forum quotes

The forum page itself returns 403 to anonymous fetches (both direct and via
proxy), and no Wayback snapshot exists (checked
`archive.org/wayback/available` for both URL forms, both empty). The quotes
above come from search-engine-indexed content of the official thread,
returned consistently across three independent queries — including an
exact-phrase query (`"1685 voxels" "outside the image extents"`) whose top
hit is precisely this thread, which is strong evidence the strings appear
verbatim on the page. Classification per COLLABORATOR_RULES:
**source-supported quotes**, one step short of a directly loaded page.
Cheap hardening action for the feasibility stage: anyone with a (free)
challenge registration loads the thread and confirms the two quoted posts.

### 2d. Data access (bears on the census's checkability)

- The full 149-case training set is now **openly downloadable without
  challenge registration**: Zenodo record 16813698 ("ISLES'24 - A Real-World
  Longitudinal Multimodal Stroke Dataset", `train.7z`, 99.0 GB, license
  CC BY-NC-SA 4.0, access: open; DOI 10.5281/zenodo.16813698), plus a
  Hugging Face mirror (`hugging-science/isles24-stroke`, 149 per-case parquet
  shards, ~26 GB). The card assumed challenge-site registration; access is
  strictly easier than assumed.
- Release structure confirms both spaces the census needs: raw perfusion maps
  and derivatives "linearly co-registered to the NCCT space", with the lesion
  mask in the same derivative tree (official repo README,
  github.com/ezequieldlrosa/isles24: derivative filenames
  `sub-strokecase0001_ses-0001_space-ncct_tmax.nii.gz`,
  `…_ses-0002_lesion-msk.nii.gz`; evaluation code at `utils/eval_utils`, MIT).

## 3. Residual assumption check (mandatory follow-up)

*If this screen only verified the nearest checkable thing, what is the card
still assuming?*

1. **The quantitative thresholds** (overflow > 5% of lesion volume in ≥ 10%
   of cases) remain unmeasured. This is not a wrong-keystone situation: the
   card itself prespecifies these as stage 1's kill criterion, and stage 1 is
   the census that measures them. The screen's finding is that the phenomenon
   exists in the release and is scored by the official metrics; magnitude is
   exactly what the one-session stage 1 is for.
2. **Support-mask recoverability**: supported by "completely empty in the
   derived CTP images", but zeros-vs-NaN convention and degeneracy criteria
   still need the preregistered definition the card already promises. Both
   raw-space maps and NCCT-space derivatives exist, so support can be
   computed in raw space and transformed as a cross-check.
3. **Forum quote provenance** (§2c): verbatim page-level confirmation
   requires a challenge login; flagged as a feasibility-stage action, not a
   blocker.
4. Stage 2 (model behavior at the boundary) additionally assumes the shared
   audit model exists; the card already gates stage 2 on that and the verdict
   here does not depend on it.

## 4. Execution note

Local inspection of actual NIfTI geometry (the card's "three downloaded
cases in under an hour") was attempted and is impossible in this sandbox:
network Bash and Python execution are blocked (unsandboxed run denied). A
draft probe script written for that attempt was deleted unexecuted, in
keeping with the coding gate; no code deliverable exists from this stage.
The verdict rests entirely on the documentary evidence above.

## 5. Verdict

The keystone is verified in kind on the challenge's own record — CTP support
narrower than the scored target, released ground truth overflowing it in a
named training case, out-of-support voxels deliberately scored — with
magnitude left to the prespecified stage-1 census, which is what stage 1 is
for. The card's premise is not built on data the dataset lacks; it is built
on a property the organizers themselves acknowledged and chose to keep.

```json
{"verdict": "PASS", "evidence": "For patient 0019, for example, there are 1685 voxels (occurring on slices 58, 59 and 60) that were segmented as lesion on DWI, but are outside the image extents of the CTP data.", "source": "Official ISLES'24 challenge forum thread 'How will lesion voxels outside the field of view of the CTP imaging be handled?' (isles-24.grand-challenge.org/forum/topics/how-will-lesion-voxels-outside-the-field-of-view-of-the-ctp-imag/); retrieved via search-engine index of the page (page 403 to anonymous access), exact-phrase match confirmed", "note": "Slab-narrower-than-target confirmed qualitatively on the challenge's own forum, organizers confirm out-of-FOV lesion voxels are scored; quantitative 5%/10% thresholds remain stage 1's prespecified census; forum quotes need one page-level confirmation by a registered user at feasibility."}
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


