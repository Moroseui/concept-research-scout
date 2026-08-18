You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-isles24-003
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


===== evidence/ledger_digest.md =====
# Ledger digest (auto-generated -- do not edit; run `python scout.py ledger digest`)

122 tracked ideas. Latest state per idea; full history in ledger.jsonl.

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **DATA_ACCESS** x3: Required data, checkpoints, or mappings are not obtainable in practice.
- **IDENTIFIABILITY_FAILURE** x3: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.
- **ANNOTATION_PROVENANCE** x1: Inference depends on who assigned labels / what they could see, and that is undocumented or contaminated.
- **CIRCULARITY** x1: The endpoint is a re-encoding of the input or of the thing being tested.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **scout-015-c04** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.5, audited 2026-08-17] -- The continuous air tunnel inside the hiatal-hernia score
- **scout-015-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.5, audited 2026-08-17] -- The lung-opacity score may be reading gravity
- **scout-013-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.4, audited 2026-08-15] -- Collateral failure written in the cortical veins
- **scout-012-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.2, audited 2026-08-15] -- The dilated esophagus inside the fibrosis score
- **isles24-scout-001-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.1, audited 2026-08-16] -- A spreading front inside the perfusion deficit
- **scout-013-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.1, audited 2026-08-15] -- The vessel map inside the mosaic-attenuation score
- **isles24-scout-002-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.0, audited 2026-08-16] -- The healthy hemisphere is the ruler
- **scout-016-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.0, audited 2026-08-18] -- Name the noise the kernel writes: the mediator behind idea 004's reconstruction shifts
- **isles24-scout-001-c07** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.0, audited 2026-08-16] -- Does the model mistake the end of the scan for the end of the bolus?
- **isles24-scout-002-c07** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.9, audited 2026-08-16] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
- ... and 68 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- regional-substitution: 17
- counterfactual-synthesis: 15
- conditional-observational: 12
- representation-erasure: 9
- natural-paired: 4
- longitudinal-within-subject: 4
- model-output-perturbation: 4
- regional-removal: 3
- cross-reconstruction: 2
- cross-model-disagreement: 1
- other:remote-perturbation: 1
- other:graph-edge-intervention: 1

## Ideas

- **idea-001** [REJECTED/DEBATED/baseline] -- Have lung nodule concept models been validated against radiologist opinion rather than against disease? -- killed: DATA_INSUFFICIENT -- data: {"primary": "LIDC-IDRI via The Cancer Imaging Archive", "license": "CC BY 3.0", 
- **idea-002** [PAUSED/DEBATED/baseline] -- Dermoscopic concepts predicted from non-dermoscopic photographs: genuine visibility or shortcut? -- data: {"primary": "Derm7pt paired clinical/dermoscopic images", "source": "github.com/
- **idea-003** [REJECTED/DEBATED/baseline] -- Does BI-RADS concept intervention survive realistic clinician behaviour, and does it beat simply reading the BI-RADS category? -- killed: DATA_ACCESS -- data: {"primary": "BUS-BRA (Zenodo 8231412, CC BY 4.0) for the external and baseline a
- **idea-004** [ACTIVE/PROBED/baseline] -- The free test-retest experiment already inside CT-RATE: duplicate reconstructions of the same acquisition
- **idea-005** [REJECTED/DEBATED/baseline] -- Eight named characteristics, or three latent ones? Discriminant validity of the LIDC concept vocabulary -- killed: ANNOTATION_PROVENANCE
- **idea-006** [PAUSED/DEBATED/baseline] -- Ask the chest-CT foundation model to diagnose a volume with no patient in it
- **idea-007** [ACTIVE/DEBATED/baseline] -- The same patient, twice, ten minutes apart, differing only in how much air is in the lungs
- **idea-008** [ACTIVE/DEBATED/baseline] -- Two papers say Sybil's residual signal is the background, one of them names emphysema, and neither measured it
- **idea-009** [REJECTED/DEBATED/baseline] -- Murray's cube law says how a branching tree should be built - ask whether the risk model is reading the lung's departure from it -- killed: IDENTIFIABILITY_FAILURE
- **idea-010** [REJECTED/DEBATED/baseline] -- Cardiomegaly on a CT report is admitted gestalt - ask whether the model has quietly turned it into millilitres -- killed: CIRCULARITY
- **idea-011** [PAUSED/DEBATED/baseline] -- Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock
- **idea-012** [PAUSED/DEBATED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **idea-013** [SHORTLISTED/DEBATED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **idea-014** [PAUSED/DEBATED/baseline] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- **idea-015** [REJECTED/DEBATED/baseline] -- A breast-cancer risk model may be reading the arteries as a vascular clock
- **idea-016** [REJECTED/DEBATED/baseline] -- The PE model may read contrast flowing backward as a pressure gauge -- killed: IDENTIFIABILITY_FAILURE
- **idea-017** [SHORTLISTED/DEBATED/baseline] -- A lung-cancer model may be reading a mechanically remodeled trachea
- **idea-018** [REJECTED/DEBATED/baseline] -- The brain-tumor prognosticator may be weighing the chewing muscle -- killed: DATA_ACCESS
- **idea-019** [SHORTLISTED/DEBATED/wide] -- The fibrosis model may be counting holes at the pleural edge
- **idea-020** [REJECTED/DEBATED/baseline] -- A spreading front inside the perfusion deficit -- killed: IDENTIFIABILITY_FAILURE
- **idea-021** [SHORTLISTED/DEBATED/baseline] -- The healthy hemisphere is the ruler
- **idea-022** [PAUSED/DEBATED/wide] -- Does the model mistake the end of the scan for the end of the bolus?
- **idea-023** [SHORTLISTED/DEBATED/wide] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
- **idea-024** [REJECTED/DEBATED/wide] -- The capillary traffic jam hidden behind the same mean transit time -- killed: DATA_ACCESS
- **idea-025** [PAUSED/DEBATED/wide] -- The scan is also an actigraph: the model may be reading how much the patient moved
- **isles24-scout-001-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Does the winning model rediscover the collateral clock?
- **isles24-scout-001-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The vascular detour the segmentation model can see
- **isles24-scout-001-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Read the stroke from the blood leaving, not only entering
- **isles24-scout-001-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The frail brain around the threatened territory
- **isles24-scout-001-c05** [SCOUT_ONLY/SCOUTED/baseline] -- A spreading front inside the perfusion deficit
- **isles24-scout-001-c06** [SCOUT_ONLY/SCOUTED/wide] -- The capillary traffic jam hidden behind the same mean transit time
- **isles24-scout-001-c07** [SCOUT_ONLY/SCOUTED/wide] -- Does the model mistake the end of the scan for the end of the bolus?
- **isles24-scout-001-c08** [SCOUT_ONLY/SCOUTED/wide] -- The deconvolution algorithm may have signed the image
- **isles24-scout-002-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The water already in the tissue: does the model read the edema clock?
- **isles24-scout-002-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The healthy hemisphere is the ruler
- **isles24-scout-002-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Two tissues, two death thresholds
- **isles24-scout-002-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The barrier is already leaking
- **isles24-scout-002-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The clot that lets contrast through
- **isles24-scout-002-c06** [SCOUT_ONLY/SCOUTED/wide] -- The scan is also an actigraph: the model may be reading how much the patient moved
- **isles24-scout-002-c07** [SCOUT_ONLY/SCOUTED/wide] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
- **isles24-scout-002-c08** [SCOUT_ONLY/SCOUTED/wide] -- Has the deficit percolated? Volume is what the metric sees; connectivity may be what the model uses
- **isles24-scout-003-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Did preprocessing teach the winner to read the disappearing insular ribbon?
- **isles24-scout-003-c02** [SCOUT_ONLY/SCOUTED/baseline] -- How much artery did the clot occupy?
- **isles24-scout-003-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The arterial network's spare route
- **isles24-scout-003-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The blood's grayscale oxygen gauge
- **isles24-scout-003-c05** [SCOUT_ONLY/SCOUTED/baseline] -- When vanished sulci mean rescue, not death
- **isles24-scout-003-c06** [SCOUT_ONLY/SCOUTED/wide] -- The bolus spreads like dye in a river
- **isles24-scout-003-c07** [SCOUT_ONLY/SCOUTED/wide] -- Does the model price the last mile of blood delivery?
- **isles24-scout-003-c08** [SCOUT_ONLY/SCOUTED/wide] -- The skull is a fixed-volume pressure vessel
- **scout-001-c05** [SHORTLISTED/?/baseline] -- (untitled)
- **scout-001-c06** [SHORTLISTED/?/baseline] -- (untitled)
- **scout-001-c07** [SHORTLISTED/?/baseline] -- (untitled)
- **scout-002-c02** [SHORTLISTED/?/baseline] -- (untitled)
- **scout-002-c06** [SHORTLISTED/?/baseline] -- (untitled)
- **scout-002-c07** [SHORTLISTED/?/baseline] -- (untitled)
- **scout-006-c01** [SHORTLISTED/SCOUTED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **scout-006-c02** [SHORTLISTED/SCOUTED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **scout-006-c03** [SCOUT_ONLY/SCOUTED/baseline] -- An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver
- **scout-006-c04** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-006-c05** [SCOUT_ONLY/SCOUTED/baseline] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two
- **scout-007-c01** [SHORTLISTED/SCOUTED/baseline] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- **scout-007-c02** [SHORTLISTED/SCOUTED/baseline] -- A breast-cancer risk model may be reading the arteries as a vascular clock
- **scout-007-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin may be reading fatty kidney rather than kidney shape
- **scout-007-c04** [SHORTLISTED/SCOUTED/baseline] -- The PE model may read contrast flowing backward as a pressure gauge
- **scout-007-c05** [SHORTLISTED/SCOUTED/baseline] -- A lung-cancer model may be reading a mechanically remodeled trachea
- **scout-007-c06** [SCOUT_ONLY/SCOUTED/wide] -- The effusion model may be reading whether pleural fluid still obeys gravity
- **scout-007-c07** [SHORTLISTED/SCOUTED/wide] -- The fibrosis model may be counting holes at the pleural edge
- **scout-007-c08** [SCOUT_ONLY/SCOUTED/wide] -- The PE model may be reading how completely blood and contrast have mixed
- **scout-007-c09** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-007-c10** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-007-c11** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-007-c12** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-007-c13** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-008-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The cirrhosis model may be reading the bumpiness of the liver's edge
- **scout-008-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The chest-CT model may see the heart by watching the airway splay
- **scout-008-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The model that 'predicts a blood count' may just be reading how bright the blood is
- **scout-008-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The emphysema call may read the shape of the holes, not just how many
- **scout-008-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The lung-cancer model may read the aorta as an ageing clock
- **scout-009-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The CT spirometer may be measuring remodeled airway walls
- **scout-009-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The kidney model may be reading fat packed into the renal sinus
- **scout-009-c03** [SHORTLISTED/SCOUTED/baseline] -- The brain-tumor prognosticator may be weighing the chewing muscle
- **scout-009-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The risk model may be reading the breast's lines of force
- **scout-009-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The lung-cancer model may be reading the marrow as a smoking dosimeter
- **scout-009-c06** [SCOUT_ONLY/SCOUTED/wide] -- The CT spirometer may be reading the diaphragm as a pressure-loaded membrane
- **scout-009-c07** [SCOUT_ONLY/SCOUTED/wide] -- Mirai may be detecting broken bilateral symmetry before a lesion exists
- **scout-009-c08** [SCOUT_ONLY/SCOUTED/wide] -- The glioblastoma prognosticator may be reading the invasion front's roughness
- **scout-009-c09** [SCOUT_ONLY/SCOUTED/fiction] -- The arterial-calcification score may be reading inspiratory depth
- **scout-010-c01** [SCOUT_ONLY/SCOUTED/baseline] -- CXR-Age put back together from parts a radiologist can measure -- data: ChestX-ray8 (primary), PadChest (replication); CheXmask for both.
- **scout-010-c02** [SCOUT_ONLY/SCOUTED/baseline] -- Atelectasis vs consolidation: has CT-CLIP learned the radiologist's volume-loss rule? -- data: CT-RATE (validation split; established access and local pipeline).
- **scout-010-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin's cirrhosis signal may be the spleen -- data: Public abdominal CT (AMOS 2022, TotalSegmentator public dataset); Merlin checkpoint from HF.
- **scout-010-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The inferior vena cava as a manometer: does the chest model read venous pressure? -- data: CT-RATE (repeat-session subset; second and final CT-RATE candidate this cycle).
- **scout-010-c05** [SCOUT_ONLY/SCOUTED/baseline] -- Aortic tortuosity as a buckled column: is the hypertension head reading exceeded critical pressure? -- data: Public abdominal CT with age metadata (candidate cohorts: AMOS 2022, TotalSegmentator public dataset - metadata adequacy is Stage 0); Merlin checkpoint from HF. Second and final Merlin/public-abdominal candidate this cycle.
- **scout-011-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Name the bone phenotype hidden in a near-perfect hand-radiograph sex classifier
- **scout-011-c02** [SCOUT_ONLY/SCOUTED/baseline] -- Does Merlin read renal atrophy when it predicts future CKD?
- **scout-011-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Cephalization in 3D: decode CT-CLIP's pulmonary-edema score
- **scout-011-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The air bronchogram as a topological cue
- **scout-011-c05** [SCOUT_ONLY/SCOUTED/baseline] -- A pancreatic fat gauge inside Merlin's diabetes forecast
- **scout-012-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The race signal in chest CT: measure the bone density everyone names and nobody measured -- data: NLST (CDAS; same cohort the anchor paper trained on)
- **scout-012-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The dilated esophagus inside the fibrosis score -- data: CT-RATE (validation split; local inference pipeline already frozen and probe-verified)
- **scout-012-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin's COPD call may come from the lungs it wasn't asked to look at -- data: Public abdominal CT (AMOS 2022 / TotalSegmentator public dataset) + released Merlin checkpoint
- **scout-012-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The non-gated chest CT contains an ECG: heart rate written in motion banding -- data: CT-RATE (second and final CT-RATE candidate this cycle); TCIA gated collections only for validating the X-measurement
- **scout-012-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The prognosis model as a manometer: midline shift is pressure the skull wrote down -- data: Anchor model's cohort (single-institution + TRACK-TBI) - access is the declared rate-limiter; CQ500 (public, has MLS/mass-effect reads but no outcomes) for X-measurement development only
- **scout-013-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The vessel map inside the mosaic-attenuation score -- data: CT-RATE validation split
- **scout-013-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The open fissure inside lung-cancer risk -- data: NLST held-out scans scored by a reproduced or released Sybil model
- **scout-013-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Name the skeletal frailty inside mortality prediction -- data: Public chest-radiograph mortality anchor cohort if obtainable; external measurement development on MIMIC-CXR
- **scout-013-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The renal artery as a buckled pressure line -- data: Public contrast-enhanced abdominal CT compatible with released Merlin checkpoint
- **scout-013-c05** [SCOUT_ONLY/SCOUTED/baseline] -- Collateral failure written in the cortical veins -- data: Paired baseline NCCT and CTA/CTP or DWI stroke cohort from the anchor model; public CQ500 only for measurement robustness
- **scout-014-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The fat around the heart inside the CVD-mortality score: finish the observation Chao et al. started
- **scout-014-c02** [SCOUT_ONLY/SCOUTED/baseline] -- Redraw the same airway walls with a sharper pencil: does the peribronchial-thickening score follow Pi10?
- **scout-014-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The cardiomegaly head may be reading the rib cage: Haller index beyond heart volume
- **scout-014-c04** [SCOUT_ONLY/SCOUTED/baseline] -- Sybil was never given the patient's age; the thymus wrote it down anyway
- **scout-014-c05** [SCOUT_ONLY/SCOUTED/baseline] -- Chronic anemia turns the marrow back on: is Merlin reading red marrow, not just pale blood?
- **scout-015-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Measure the fluid behind the pleural-effusion score
- **scout-015-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The missing branches inside Sybil's risk score
- **scout-015-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The portal vein as the cirrhosis model's pressure gauge
- **scout-015-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The continuous air tunnel inside the hiatal-hernia score
- **scout-015-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The lung-opacity score may be reading gravity
- **scout-016-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Name the noise the kernel writes: the mediator behind idea 004's reconstruction shifts
- **scout-016-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The mortality model is wearing the patient's hardware
- **scout-016-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The fat inside the silhouette: epicardial adipose in the cardiomegaly score
- **scout-016-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The skeleton's tree rings: Harris lines inside the bone-age model
- **scout-016-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The cage remembers the hyperinflation: barrel chest inside the emphysema score


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


===== ideas/scout-isles24-003/README.md =====
# Scouting cycle isles24-003

Tracks: baseline, wide
Charter: isles24 (charters/isles24/CHARTER.md; scores are scoped to this charter and not comparable across charters)


===== ideas/scout-isles24-003/candidates_all.json =====
{
  "cycle": 3,
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
      "id": "isles24-scout-003-c01",
      "parent_ids": [],
      "search_mode": "A",
      "entry_point": 2,
      "title": "Did preprocessing teach the winner to read the disappearing insular ribbon?",
      "question": "Is an ISLES'24 final-infarct model using loss of gray-white differentiation in the insular ribbon and basal ganglia as a map of already injured tissue?",
      "rung": "Target rung 1: use of an automated gray-white attenuation-contrast measurement; rung 2 requires center-held-out replication and convergence across at least two model families.",
      "deliverable_sentence": "The final-infarct model is using loss of gray-white differentiation in established ASPECTS regions as an acute-tissue-injury signal.",
      "X_measurement": "Register an ASPECTS atlas automatically, erode each region, and compute the affected-to-mirrored difference in gray-matter versus adjacent white-matter HU contrast; automated contralateral densitometry is described by Takahashi et al. (PMID 26158082), while automated ASPECTS systems provide directly executable precedents (DOI 10.3174/ajnr.A5889; DOI 10.1002/hbm.25845). Compute-today test: YES on any unseen NCCT using an atlas, midsagittal reflection, tissue masks, and HU arithmetic; no new annotator.",
      "suspected_signal": "Cytotoxic edema blurs the normally higher attenuation of cortex and deep gray matter relative to white matter; the winning recipe's large preprocessing gain makes a low-contrast NCCT cue a plausible unfinished story, although the gain itself does not prove this cue caused it (arXiv:2505.18424).",
      "use_vs_association": "Selective representation erasure: learn a gray-white-contrast direction from held-out-free training cases, remove it at inference while preserving decodability of Tmax burden, lesion side, and global HU, and require a region-specific fall in predicted infarct probability beyond norm-matched random directions; an input-space contrast-restoration dose response is a secondary corroboration.",
      "keystone_prerequisite": "A frozen ISLES'24 model that actually consumes quantitative NCCT achieves non-trivial held-out performance and exposes a representation in which gray-white contrast can be erased without destroying perfusion severity or anatomy.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearby facts—NCCT is released and a winning method used custom windowing—do not establish that the reproduced model uses NCCT or that erasure is selective. Those are the real Stage-0 gates.",
      "rung_reached": "0; rung 1 after selective erasure plus concordant input dose response; rung 2 after model-family and center replication.",
      "dies_like_prior": "Resembles idea-010 (CIRCULARITY), because early injury and final infarct are related. It differs by testing use of a named continuous image contrast while holding perfusion information and anatomy decodable; merely detecting an acute lesion is insufficient to pass selective erasure and graded restoration.",
      "closest_prior_work": "Automated ASPECTS work detects early ischemic change on NCCT (PMID 30498017; PMID 35357053), and the winning ISLES paper reports preprocessing-dependent performance (arXiv:2505.18424). Neither tests whether a final-infarct model uses regional gray-white contrast. This is a targeted gap, not a verified novelty claim.",
      "existing_assets": "Public NCCT and registered perfusion maps for 149 cases; automated ASPECTS and densitometry precedents; reproducible nnU-Net family; official metrics.",
      "smallest_decisive_experiment": "Freeze a center-stratified split; train one NCCT+perfusion model and require prespecified improvement over its perfusion-only twin. On 40 held-out cases, run selective erasure and three-level contrast restoration with random-direction and mirrored-unaffected controls. Roughly 30-50 GPU-hours and 7-10 days to first decision.",
      "standing_confounds_addressed": "Within-case mirroring controls patient, scanner, site, habitus, and prevalence; frozen split prevents leakage; perfusion decodability tests gross collateral damage. Reconstruction and beam hardening are not fully ruled out and require region/site stratification. Follow-up label provenance does not enter the primary paired output change.",
      "alternative_explanations": [
        "Erasure removes generic lesion severity; ruled against by preserved Tmax/core-volume decodability and random directions.",
        "The response is an edit artifact; bounded by physiologic contrast ranges, discriminator checks, and agreement with representation erasure.",
        "Windowing rather than biology explains the signal; this remains a model-mechanism explanation at rung 1 and forbids a claim that the model measures irreversible core."
      ],
      "anticipated_negative": "Decisive only after the NCCT incremental-performance and erasure-selectivity gates; otherwise sensitivity-limited. A gated null shows that the preprocessing success did not translate into use of this radiologist-recognized cue.",
      "remaining_legwork": "2 days for archive/input census, 4-6 days for twin models, 3 days for probes: 7-10 days.",
      "design_template": "representation-erasure",
      "entry_point_2_requirements": "Measurement: mirrored ASPECTS-region gray-white HU contrast. Confused artifact: reconstruction noise and beam hardening; quantify local noise, stratify by site/region, and include unaffected-side controls.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "One named radiologic sign, one quantitative measurement, and a directional intervention."
        },
        "identifiability": {
          "value": 3,
          "why": "Dual representation/input evidence is promising, but selective erasure and reconstruction effects remain unverified."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Gray-white loss is a core acute-stroke reading task and bears on what the model calls already injured."
        },
        "interest": {
          "value": 4,
          "why": "It gives a physiological candidate explanation for the winner's preprocessing-dependent gain."
        },
        "prior_legwork": {
          "value": 4,
          "why": "Measurement and model recipes exist; the actual trained audit model does not."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped because the true model/representation keystone is not inspected."
        },
        "data_readiness": {
          "value": 4,
          "why": "Required public modalities exist, though the archive is large."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Official segmentation metrics exist; selectivity gates are custom."
        },
        "negative_result_value": {
          "value": 3,
          "why": "Useful after the explicit NCCT contribution and sensitivity gates."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Targeted primary-source search found adjacent detection and challenge work, not this audit; not exhaustive."
        },
        "regret": {
          "value": 4,
          "why": "A large preprocessing effect and an established radiologic signal are one experiment apart."
        }
      },
      "priority_score": 3.65,
      "unverified_claims": [
        "NCCT provides incremental performance in the reproduced model",
        "quantitative HU survives released preprocessing",
        "selective representation erasure is achievable",
        "novelty beyond targeted search"
      ],
      "plain_pitch": "Radiologists look for fading contrast between gray and white brain tissue as an early sign of stroke injury. This study asks whether a final-infarct model uses that same sign, rather than merely benefiting from better-looking scans. If true, selectively removing that contrast signal would change predictions in the affected regions while leaving perfusion information intact.",
      "track": "baseline",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-003-c02",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "How much artery did the clot occupy?",
      "question": "Is an ISLES'24 model using clot burden—the length and arterial extent of the occlusion—to predict how much threatened tissue survives reperfusion?",
      "rung": "Target rung 1; rung 2 requires replication across centers and agreement between geometric and artery-segment clot-burden measurements.",
      "deliverable_sentence": "The final-infarct model is using clot burden—the length and arterial extent of the occlusion—beyond the downstream perfusion deficit.",
      "X_measurement": "Compute centerline clot length and an automated modified clot-burden score from the CTA/LVO mask: subtract involved intracranial ICA/M1/M2 segments from a 10-point arterial template. CTA clot burden is an established quantitative construct (PMID 25804568); automatic centerline length requires only the released occlusion mask plus vessel segmentation. Compute-today test: YES if the mask encodes full thrombus extent; that file-level semantic is the keystone.",
      "suspected_signal": "A longer, more proximal clot blocks more arterial branches, carries more fibrin/red-cell material, and is harder to clear quickly; even among successfully reperfused patients it can prolong tissue ischemia and leave a larger final infarct.",
      "use_vs_association": "Regional substitution changes only clot extent along the automatically segmented arterial centerline while keeping occlusion site, perfusion maps, distal vessel image, and all clinical variables fixed; a monotone output response beyond equal-volume vessel and nonvessel shams tests use rather than label association.",
      "keystone_prerequisite": "The released LVO mask delineates enough of the thrombus extent—not merely an occlusion point—to support stable automatic clot-length and burden measurements.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The dataset paper verifies that vessel-occlusion masks exist, but not their voxel semantics or post-erosion extent. Treating that nearby fact as the keystone would repeat the program's wrong-keystone error.",
      "rung_reached": "0; rung 1 after mask census and gated substitution; rung 2 after two-site and two-measurement replication.",
      "dies_like_prior": "Most resembles idea-016 (IDENTIFIABILITY_FAILURE), where contrast flow covaried with disease and protocol. Here the confirmatory edit freezes perfusion, timing, site, and occlusion location and changes only thrombus extent; the remaining threat is edit realism, not protocol confounding.",
      "closest_prior_work": "Clinical studies relate CTA clot burden and NCCT clot characteristics to outcome (PMID 25804568; PMID 27576312). They do not hold the downstream perfusion shadow fixed or audit model use. The exact delta is a within-case use test in a final-infarct model; novelty remains unaudited.",
      "existing_assets": "Co-registered NCCT/CTA/CTP, stated LVO masks, 149 final-infarct cases, vessel-segmentation tools, and official output metrics.",
      "smallest_decisive_experiment": "Inspect all mask headers and 30 random masks; require at least 60 usable full-extent masks and inter-perturbation clot-length ICC >=0.85. On 30 held-out usable cases, apply +/-25% and +/-50% centerline-extent substitutions and shams. Five days after a trained model; under 15 GPU-hours for inference.",
      "standing_confounds_addressed": "Within-case edits fix scanner, vendor, protocol, site, positioning, habitus, prevalence, referral, and treatment covariates; fixed perfusion maps block the dominant hemodynamic mediator. They do not rule out an artificial vessel-discontinuity cue or CTA registration artifacts; centerline-continuity and discriminator gates address but cannot eliminate these.",
      "alternative_explanations": [
        "The model reacts to vessel discontinuity, not clot burden; continuity-preserving inpainting and equal-length contralateral vessel shams test this.",
        "Clot edits are out of distribution; changes are bounded to observed within-site length and attenuation distributions.",
        "The model uses occlusion site; site and proximal endpoint remain fixed."
      ],
      "anticipated_negative": "Decisive if mask, realism, and positive-control gates pass: a null would show the model reads the downstream perfusion consequence but not clot extent itself.",
      "remaining_legwork": "2 days mask census, 2 days vessel-centerline QA, 3-5 days interventions: about one week after the shared model exists.",
      "design_template": "regional-substitution",
      "entry_point_2_requirements": "Measurement: centerline clot length and modified clot-burden score. Confused artifact: vessel segmentation breaks and CTA bolus timing; require continuity QA and use geometry rather than absolute enhancement as primary X.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "Clot length/segment burden and monotone response are explicit."
        },
        "identifiability": {
          "value": 4,
          "why": "Holding perfusion and site fixed isolates clot geometry unusually well, conditional on realistic editing."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Clot burden affects treatment difficulty and infarct evolution."
        },
        "interest": {
          "value": 4,
          "why": "Tests whether multimodal models look upstream at the cause or only downstream at perfusion."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Clinical measures exist, but automatic mask semantics and editing are unfinished."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped by uninspected mask semantics."
        },
        "data_readiness": {
          "value": 3,
          "why": "Public, but useful-case count is unknown."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Paired output change is direct; edit-validity gates are custom."
        },
        "negative_result_value": {
          "value": 4,
          "why": "A gated null cleanly distinguishes upstream clot use from downstream perfusion use."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "No model-use study found in targeted search; not proof of novelty."
        },
        "regret": {
          "value": 4,
          "why": "The stated occlusion masks make this an unusually cheap upstream-versus-downstream test if their semantics hold."
        }
      },
      "priority_score": 3.8,
      "unverified_claims": [
        "LVO masks encode full thrombus extent",
        "at least 60 usable cases",
        "realistic continuity-preserving edits",
        "exact novelty"
      ],
      "plain_pitch": "A clot can block a short piece of one artery or occupy a long stretch with several branches. The study asks whether the model uses that clot burden itself, beyond the perfusion deficit the clot creates. If true, changing only the apparent clot extent while freezing perfusion would shift the predicted final infarct.",
      "track": "baseline",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-003-c03",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "The arterial network's spare route",
      "question": "Is an ISLES'24 model using Circle-of-Willis graph redundancy—the number and caliber of patent alternate paths around the occlusion—as a reserve for maintaining flow?",
      "rung": "Target rung 1 use of a graph-derived image quantity; rung 2 requires external CTA replication and agreement with measured distal collateral filling.",
      "deliverable_sentence": "The final-infarct model is using Circle-of-Willis alternate-path redundancy as an image marker of proximal collateral reserve.",
      "X_measurement": "Convert the released multilabel Circle-of-Willis vessel mask to a graph whose edge weights are centerline minimum radii; remove the occluded edge and compute edge-disjoint source-to-territory paths plus max flow. Compute-today test: YES on an unseen CTA with a multilabel mask, using deterministic skeletonization and graph algorithms; no human labels. Clinical CTA work defines complete, nonisolating-incomplete, and isolating-incomplete variants (PMID 39788631).",
      "suspected_signal": "The Circle of Willis is a hydraulic network: communicating arteries provide parallel routes around a proximal blockage, so topology and caliber determine whether pressure can reach the threatened territory before leptomeningeal routes are recruited.",
      "use_vs_association": "Graph-edge intervention: render patent-to-hypoplastic and hypoplastic-to-patent communicating-artery variants within each case while preserving the occlusion, distal CTA enhancement, brain images, and perfusion maps; require output changes predicted by the signed change in alternate-path capacity and absent for topology-neutral vessel-caliber shams.",
      "keystone_prerequisite": "The released multilabel Circle-of-Willis masks accurately distinguish communicating-artery branches and calibers in enough cases for graph edits to represent real anatomic variants rather than segmentation artifacts.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The Zenodo description's existence claim for automated Circle-of-Willis masks is not evidence of branch-level fidelity. Accuracy, coverage, and usable variant counts are the load-bearing facts.",
      "rung_reached": "0; rung 1 after mask-fidelity and graph-edit gates; rung 2 after external CTA and distal-filling agreement.",
      "dies_like_prior": "Resembles idea-009 (IDENTIFIABILITY_FAILURE), which tried to interpret vascular geometry amid age, disease, and acquisition. This design changes graph connectivity within case while freezing those factors and the perfusion field. It also differs from isles24-scout-001-c02: that candidate tests distal collateral reach; this one tests proximal network redundancy upstream of that reach.",
      "closest_prior_work": "Large CTA studies establish Circle-of-Willis variation frequencies (DOI 10.1016/j.wneu.2017.07.084) and association of variant classes with outcome after successful revascularization (PMID 39788631). They do not audit final-infarct models or intervene on graph topology. Exact novelty is unverified.",
      "existing_assets": "CTA, stated automatic multilabel Circle-of-Willis masks, LVO masks, perfusion maps, two centers, standard skeleton/graph algorithms.",
      "smallest_decisive_experiment": "Stage 0: visually inspect only for tool QA—not new labels—30 masks and quantify graph validity automatically in all cases; require >=20 cases in each of two common editable variant families and stable edge radii under one-voxel perturbation. Then run paired edge interventions on 40 held-out cases. Ten to fourteen days, under 20 GPU-hours after model training.",
      "standing_confounds_addressed": "Within-case intervention holds scanner, vendor, protocol, site, age, habitus, referral, and label prevalence; fixed perfusion separates direct CTA topology use from its existing downstream consequence. It does not fully rule out synthetic-vessel artifacts or CTA phase effects. No new annotation burden is required; visual inspection is QA, not an input or endpoint.",
      "alternative_explanations": [
        "The model detects added bright voxels; topology-neutral added-vessel shams match volume and intensity.",
        "The model uses vessel caliber generally, not alternate paths; edits with equal total vessel volume but different connectivity discriminate them.",
        "Automatic masks hallucinate variants; graph-validity and raw-CTA agreement gates must pass before inference."
      ],
      "anticipated_negative": "Sensitivity-limited if editable variant support is thin; decisive after topology, realism, and positive-control gates. A gated null says the model ignores a proximal collateral route already visible in CTA.",
      "cross_domain": {
        "borrowed_construct": "Network robustness and max-flow/min-cut from graph theory.",
        "measurement_it_implies": "Edge-disjoint paths and caliber-weighted max flow after deleting the occluded edge.",
        "what_changes_if_dropped": "The study could fall back to coarse complete/incomplete anatomy classes, but it would lose the graded intervention and most of its identifiability."
      },
      "remaining_legwork": "3 days mask/variant census, 3 days graph validation, 4-6 days renderer and inference: roughly two weeks.",
      "design_template": "other:graph-edge-intervention",
      "design_template_justification": "The causal unit is graph connectivity, not a contiguous image region; none of the named templates captures matched edge addition/removal with topology-neutral shams.",
      "entry_point_2_requirements": "Measurement: caliber-weighted alternate-path capacity. Confused artifact: CTA phase and automated branch hallucination; fixed within-case intensity plus raw-CTA/mask agreement gates address them.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "The graph quantity is precise, though rendering rules need Stage-0 freezing."
        },
        "identifiability": {
          "value": 4,
          "why": "Connectivity-changing versus volume-matched topology-neutral edits isolate the claimed graph property."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Alternate arterial routes are a plausible determinant of tissue survival during occlusion."
        },
        "interest": {
          "value": 5,
          "why": "It asks whether the network model has learned a literal vascular-network robustness calculation."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Masks are stated and graph tools are mature; fidelity and rendering are not."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped by uninspected mask fidelity and variant support."
        },
        "data_readiness": {
          "value": 3,
          "why": "Public but archive-level mask properties unknown."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Signed paired response is simple; image-validity tests are custom."
        },
        "negative_result_value": {
          "value": 3,
          "why": "Strong only if enough real variant support and edit sensitivity are shown."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Adjacent anatomy/outcome papers found, no use audit; formal audit pending."
        },
        "regret": {
          "value": 5,
          "why": "A released multilabel arterial graph makes an otherwise difficult mechanism unusually testable."
        }
      },
      "priority_score": 3.8,
      "unverified_claims": [
        "branch-level mask fidelity",
        "sufficient editable variant families",
        "model consumes CTA effectively",
        "synthetic graph edits are in distribution",
        "novelty"
      ],
      "plain_pitch": "The arteries at the base of the brain form a loop that can route blood around a blockage. This study turns that loop into a graph and asks whether the model uses the number and size of spare routes. If true, changing connectivity while keeping the total amount of visible vessel and the perfusion maps fixed would change the prediction in the direction expected from the new route.",
      "track": "baseline",
      "charter": "isles24"
    },
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
    },
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
      "use_vs_association": "Counterfactual synthesis swaps the local triad—sulcal CSF fraction, pial-vessel occupancy, and preserved gray-white contrast—between matched delayed territories while holding Tmax/CBF/CBV, tissue location, and total edited volume fixed. A survival-directed output change must occur only for the coherent triad, not isolated CSF deletion or vessel addition.",
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
          "why": "A specific anatomical mechanism—collateral vessels occupying sulci—with three measurable components."
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
    },
    {
      "id": "isles24-scout-003-c06",
      "track": "wide",
      "title": "The bolus spreads like dye in a river",
      "question": "[transport physics / chromatography] Is an ISLES'24 raw-CTP final-infarct model using bolus dispersion—the spreading of contrast arrival times after delay is removed—as a marker of collateral path complexity?",
      "deliverable_sentence": "The final-infarct model is using local bolus dispersion, beyond mean arrival delay and perfusion-map severity, when predicting tissue fate.",
      "cross_field": {
        "borrowed_construct": "Advection-dispersion from transport physics and chromatography: a tracer pulse broadens as paths of different lengths mix.",
        "measurement_it_implies": "Deconvolve the tissue time-attenuation curve by the arterial input, align its first moment, and measure the second central moment and full width at half maximum of the nonnegative residue/transport kernel.",
        "what_changes_if_dropped": "Without advection-dispersion, curve width is an unnamed temporal texture and the signed delay-preserving intervention has no mechanistic interpretation."
      },
      "causal_chain": [
        {
          "link": "Long, heterogeneous collateral routes broaden the tissue bolus even after mean delay is aligned.",
          "check": "Test whether the dispersion measure agrees with independently computed dynamic collateral time and is stable to arterial-input placement."
        },
        {
          "link": "Broader transport kernels mark heterogeneous delivery not fully represented by CBF, CBV, MTT, or Tmax.",
          "check": "Regress dispersion on all four released maps and require substantial within-bin residual variation."
        },
        {
          "link": "A raw-CTP model uses that residual variation.",
          "check": "Apply delay- and area-preserving curve narrowing/broadening within case and measure paired output change."
        }
      ],
      "X_measurement": "For each parenchymal voxel, baseline-correct the 4D CTP curve, use an automatically selected contralateral proximal arterial input, fit a nonnegative delay-dispersion kernel, and report its second central moment (seconds squared) and full width at half maximum. PMID 29500248 establishes that delay/dispersion correction changes ischemic-core measurement; PMID 37693754 provides a dynamic-CT collateral-time comparator. The formula is automatic and computable today, but its stability on the released 1-frame/s series is uninspected.",
      "suspected_signal": "Collateral blood takes multiple routes with different transit times; their mixture broadens the contrast pulse, potentially distinguishing slow but coherent delivery from slow, heterogeneous delivery at the same Tmax.",
      "use_vs_association": "Within each held-out case, convolve or deconvolve only threatened-territory curves with physiologic transport kernels that change variance while preserving area, mean arrival time, baseline, peak support, and the four derived perfusion maps within frozen tolerances; a signed dose response beyond time-shuffled and mean-delay controls tests use rather than association.",
      "keystone_prerequisite": "A frozen raw-4D-CTP model with non-trivial untouched-case performance is obtainable, and the released temporal sampling supports stable dispersion estimates and map-preserving curve edits.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The dataset contains 4D CTP, but neither a suitable checkpoint nor the identifiability of dispersion at 1-frame/s has been inspected. If the model consumes only parametric maps, this candidate dies rather than silently changing its question.",
      "dies_like_prior": "It risks the DATA_ACCESS pause of idea-022 because both require an inspectable raw-CTP model; no changed unblock fact is claimed. It also risks IDENTIFIABILITY_FAILURE from delay and truncation, addressed only if mean delay, curve area, acquisition support, and derived maps remain invariant under the edit. Unlike idea-022, the manipulated estimand is kernel width inside a complete curve, not missing end-of-scan frames.",
      "closest_prior_work": "Lin et al. quantified how delay and dispersion correction changes CTP core estimates (PMID 29500248); Xu et al. quantified collateral time from perfusion CT (PMID 37693754); the ISLES'24 winning-method paper predicts final infarct from multimodal CT (arXiv:2505.18424). These are neighbors, not evidence that a learned model uses dispersion.",
      "novelty_neighbors": [
        "Lin L et al., Stroke 2018, DOI 10.1161/STROKEAHA.117.019562, PMID 29500248 — evaluates delay/dispersion correction in classical CTP quantification.",
        "Xu Y et al., Front Neurol 2023, PMID 37693754 — derives perfusion collateral time and validates it against dynamic CTA.",
        "ISLES'24 winning solution, arXiv:2505.18424 — final-infarct prediction from challenge imaging, without a reported dispersion-use audit."
      ],
      "novelty_delta": "The neighbors measure dispersion effects or train outcome models; the proposed paired audit asks whether the model itself responds to transport-kernel width when delay, area, and standard maps are held fixed.",
      "why_not_done": "NEW_CAPABILITY: ISLES'24 recently coupled public raw 4D CTP, registered maps, treatment-conditioned follow-up infarct masks, and a reproducible challenge recipe; before that combination, a map-preserving raw-curve use audit was difficult to run publicly.",
      "novelty_search_verdict": "NO_DUPLICATE_FOUND_LIMITED_SEARCH",
      "existing_assets": "Public 4D CTP and registered CBF/CBV/MTT/Tmax for 149 training cases; automatic curve fitting; official final-infarct metrics. No qualifying frozen raw-CTP checkpoint has been verified.",
      "smallest_decisive_experiment": "Stage 0 on 20 cases: estimate kernel width under three arterial-input placements and require ICC >=0.80 plus at least 30% residual interquartile range after conditioning on Tmax and MTT. If a frozen raw-CTP model gate passes, edit 24 untouched cases at three empirically supported width doses, with mean-delay, area, truncation, and map-recomputation tolerances frozen before outputs. Primary readout: paired change in predicted infarct probability mass within edited tissue.",
      "compute_envelope": "One Colab GPU session after a checkpoint exists: curve fitting and map checks are CPU work; 24 cases x 7 variants = 168 forward passes, targeted under 3 GPU-hours and 16 GB VRAM. Training a new qualifying model is outside this decisive-session budget and is an explicit prior gate.",
      "standing_confounds_addressed": "Within-case edits freeze patient, center, scanner, treatment, anatomy, and label prevalence. Moment constraints separate dispersion from delay and dose; recomputed-map tolerances separate it from the standard map channels; complete-curve and time-shift controls address truncation. Residual threats are deconvolution regularization and edit realism.",
      "alternative_explanations": [
        "The model reads mean delay: held invariant and separately perturbed as a positive control.",
        "The model reads a standard map changed by the edit: all four maps are recomputed and bounded by frozen tolerances.",
        "The response is convolution blur: an energy-matched temporally scrambled kernel is the sham."
      ],
      "anticipated_negative": "A null is interpretable only after checkpoint, dispersion-reliability, edit-realism, and temporal positive-control gates pass; then it shows that this raw-CTP model reduces temporal information to delay/severity rather than using residual transport width.",
      "verified_dataset_facts": "Relies on the cycle's primary-source verification: 149 public training cases; acute NCCT, CTA, 4D CTP and CBF/CBV/MTT/Tmax maps; post-treatment infarct masks from follow-up DWI/ADC; CC BY-NC-SA 4.0 on the version-pinned Zenodo record (DOI 10.5281/zenodo.16731717; DOI 10.1148/ryai.250603; official GitHub repository).",
      "design_template": "counterfactual-synthesis",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "One physical moment and one delay-preserving intervention define the question."
        },
        "identifiability": {
          "value": 3,
          "why": "Moment and map constraints address the main alternatives, but editable dispersion may not be separable at the released sampling rate."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Collateral transport quality is central to survival of delayed tissue and would affect interpretation of raw-CTP models."
        },
        "interest": {
          "value": 5,
          "why": "It asks whether a network performs a tracer-transport calculation absent from standard map summaries."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Dispersion and collateral-time methods exist; the model and edit validation do not."
        },
        "feasibility": {
          "value": 2,
          "why": "The raw-CTP checkpoint gate that paused idea-022 remains unresolved."
        },
        "data_readiness": {
          "value": 3,
          "why": "The public data exist but are large and temporal adequacy is uninspected."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Paired deltas are direct; map-invariance and realism gates are custom."
        },
        "negative_result_value": {
          "value": 3,
          "why": "Useful only after stringent sensitivity and edit gates."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Targeted primary-source search found close measurement work but no use audit; not exhaustive."
        },
        "regret": {
          "value": 4,
          "why": "Raw curves contain information that map-only evaluations discard, making this an obvious audit if the checkpoint gate opens."
        }
      },
      "priority_score": 3.35,
      "unverified_claims": [
        "a qualifying raw-CTP checkpoint is obtainable",
        "dispersion is identifiable at released temporal sampling",
        "map-preserving curve edits are realistic",
        "the model has temporal sensitivity",
        "exact novelty"
      ],
      "plain_pitch": "A contrast bolus can arrive late as one compact wave or arrive late after spreading through many routes. This study asks whether a model notices that spreading even when the usual blood-flow maps and average delay are kept the same. If it does, widening only the time curve should change predicted tissue death in a graded direction.",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-003-c07",
      "track": "wide",
      "title": "Does the model price the last mile of blood delivery?",
      "question": "[economic geography / facility location] Is an ISLES'24 model using distance to an arterial-territory border—the vascular network's costly last mile—as a vulnerability factor beyond local perfusion severity?",
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
        "Mangla R et al., Radiographics 2011, DOI 10.1148/rg.315105014, PMID 21918038 — border-zone imaging and pathophysiology.",
        "Carpenter DA et al., Neurology 1990, DOI 10.1212/WNL.40.10.1587, PMID 2215951 — PET study finding no selective chronic border-zone hemodynamic impairment.",
        "Deep Learning-Based Prediction of Final Infarct Core from CT Perfusion Data, PMID 41583397 — probabilistic CTP outcome model without a reported border-distance use test."
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
    },
    {
      "id": "isles24-scout-003-c08",
      "track": "wide",
      "title": "The skull is a fixed-volume pressure vessel",
      "question": "[continuum mechanics / pressure-vessel engineering] Is an ISLES'24 model using baseline intracranial compliance—the cerebrospinal-fluid space available to absorb swelling—to expand predicted final-infarct geometry beyond acute tissue injury?",
      "deliverable_sentence": "The final-infarct model is using baseline intracranial cerebrospinal-fluid reserve as a geometric prior on how far the follow-up infarct mask will expand.",
      "cross_field": {
        "borrowed_construct": "Compliance of a closed pressure vessel: added volume produces little displacement while reserve remains, then sharply greater deformation as reserve is exhausted.",
        "measurement_it_implies": "Automatic cerebrospinal-fluid volume divided by intracranial volume, plus local sulcal and ventricular reserve around the threatened hemisphere; response should be nonlinear near low reserve.",
        "what_changes_if_dropped": "Without compliance, cerebrospinal-fluid fraction is merely an age proxy; the borrowed construct supplies the interaction prediction between identical edema-like attenuation change and available reserve."
      },
      "causal_chain": [
        {
          "link": "Baseline cerebrospinal-fluid fraction measures room available for swelling inside the fixed skull.",
          "check": "Automatic segmentation stability and replication of its reported association with malignant edema, association-only."
        },
        {
          "link": "Follow-up masks acquired days later may contain geometry affected by edema as well as irreversibly injured tissue.",
          "check": "Compare mask displacement relative to arterial/perfusion boundaries across follow-up day and reserve strata; this remains an inference because follow-up edema labels are absent."
        },
        {
          "link": "The model uses reserve to shape its prediction.",
          "check": "Factorially edit cerebrospinal-fluid reserve and local edema attenuation while preserving parenchyma/perfusion, testing the compliance interaction rather than a main effect."
        }
      ],
      "X_measurement": "Segment ventricles and sulcal CSF automatically on NCCT and compute CSF/intracranial-volume ratio globally and within the affected hemisphere. PMID 35373655 reports that automatic baseline CSF/ICV improves malignant-edema prediction; PMID 29976584 defines CT net water uptake as an edema marker. The proposed X is reserve, not age or edema itself.",
      "suspected_signal": "Because the skull cannot expand, swelling first consumes cerebrospinal-fluid spaces. A model trained against 2–9-day follow-up masks could learn that identical acute injury produces different apparent lesion geometry in a brain with little versus abundant reserve.",
      "use_vs_association": "A 2x3 counterfactual factorial changes only extra-axial/ventricular CSF reserve (small empirically sampled inward/outward boundary deformations with parenchymal voxels unchanged) and separately changes affected-tissue net-water-uptake attenuation; a compliance mechanism predicts an interaction—larger output expansion from the same water-uptake dose under lower reserve—whereas an age shortcut predicts a CSF main effect.",
      "keystone_prerequisite": "Small CSF-boundary edits can alter measured reserve while keeping every parenchymal model input bit-identical outside a narrow CSF boundary and passing anatomical-realism gates; the frozen model's receptive field must connect those spaces to the threatened territory.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "ISLES'24 does not provide edema or mass-effect ground truth, and its target is infarct tissue rather than swelling. Even a positive model-use result would identify a geometric prior learned from the labels, not prove that reserve biologically changes irreversible infarction.",
      "dies_like_prior": "It directly confronts the endpoint-mismatch reason that dropped cortical atrophy in this cycle: the candidate survives only as a label-geometry/failure-mode audit, not as a tissue-survival claim. It also risks idea-010's CIRCULARITY if water uptake merely redraws acute lesion; the identifying endpoint is the reserve-by-water interaction with unchanged perfusion, not prediction of injury from injury.",
      "closest_prior_work": "Automatic CSF/ICV improves malignant-edema prediction after thrombectomy (PMID 35373655); net water uptake predicts malignant infarction (PMID 29976584); later midline shift predicts poor outcome (PMID 34494212). None of these studies audits whether a final-infarct segmentation model uses baseline reserve or whether follow-up-mask geometry carries that shortcut.",
      "novelty_neighbors": [
        "van der Worp-group registry study, 'Cerebrospinal fluid volume improves prediction of malignant edema after endovascular treatment of stroke,' PMID 35373655.",
        "Broocks G et al., Stroke 2018, DOI 10.1161/STROKEAHA.118.020507, PMID 29976584 — admission CT net water uptake predicts malignant infarction.",
        "McKeown ME et al., Neurocrit Care 2022, DOI 10.1007/s12028-021-01341-x, PMID 34494212 — follow-up midline shift over 3 mm predicts outcome."
      ],
      "novelty_delta": "Prior work predicts edema outcomes from reserve or water uptake; this study tests a specific interaction inside a final-infarct network and asks whether follow-up-label geometry taught the network a compliance shortcut.",
      "why_not_done": "BLIND_SPOT: edema prediction and infarct segmentation are treated as separate tasks, so the possibility that delayed infarct masks transmit pressure-vessel geometry back into the segmentation model falls between literatures.",
      "novelty_search_verdict": "NO_DUPLICATE_FOUND_LIMITED_SEARCH",
      "existing_assets": "NCCT, perfusion maps, follow-up masks acquired 2–9 days later, automatic brain/CSF segmentation tools, and published reserve and water-uptake formulas.",
      "smallest_decisive_experiment": "Stage 0 on 40 cases: require CSF/ICV segmentation ICC >=0.90 under one-voxel perturbation, at least 20 low- and 20 high-reserve held-out cases, and a model receptive field spanning reserve to lesion. Then run 24 cases x six factorial edits plus no-op and age-matched controls; primary statistic is the paired interaction in predicted probability mass and radial boundary displacement, not association with the final mask.",
      "compute_envelope": "One Colab GPU session after a frozen checkpoint: segmentation/edit construction is CPU work; fewer than 200 forward passes and bootstrap analysis target under 3 GPU-hours and 16 GB VRAM.",
      "standing_confounds_addressed": "The factorial interaction separates reserve from the main effects of age/atrophy and acute attenuation; within-case editing fixes patient, scanner, treatment, perfusion, and label. Parenchymal bit-identity and no-op warps control interpolation. Residual threats are unrealistic CSF geometry, architecture receptive field, and inability to validate edema-mediated label expansion directly.",
      "alternative_explanations": [
        "The model uses age-related atrophy: that predicts a CSF main effect, not the prespecified reserve-by-water interaction.",
        "Boundary edits distort cortex: affected parenchymal tensors must remain bit-identical and no-op deformation controls must be null.",
        "The model predicts true biological protection: prohibited; the card supports only use of reserve as a geometric prior."
      ],
      "anticipated_negative": "A null is sensitivity-limited unless receptive-field, edit-realism, water-uptake positive-control, and interaction-power gates pass. After those gates, it usefully shows that the model's delayed-mask predictions are not modulated by visible intracranial reserve.",
      "verified_dataset_facts": "Relies on the cycle's primary-source verification that ISLES'24 pairs acute preintervention CT with final post-treatment infarct masks derived from MRI 2–9 days later in 149 public training cases. No edema or mass-effect annotation is claimed (DOI 10.1148/ryai.250603; DOI 10.5281/zenodo.16731717).",
      "design_template": "model-output-perturbation",
      "design_template_justification": "The identifying statistic is a factorial interaction in the frozen model's output under two orthogonally controlled input quantities; this is closer to a behavioral model-output perturbation than a regional substitution because neither edited region is exchanged with another case.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "The factorial interaction is precise, but the geometric-prior wording needs its prohibition against biological survival claims."
        },
        "identifiability": {
          "value": 3,
          "why": "The interaction separates age from compliance use, but label edema cannot be validated within ISLES'24."
        },
        "medical_relevance": {
          "value": 4,
          "why": "A pressure-reserve shortcut would distort predicted lesion boundaries and challenge interpretation of delayed-MRI ground truth."
        },
        "interest": {
          "value": 5,
          "why": "It links skull mechanics, annotation timing, and model behavior in a surprising falsifiable chain."
        },
        "prior_legwork": {
          "value": 4,
          "why": "Automatic reserve and water-uptake measures and strong clinical cohorts already exist."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped by uninspected edit realism and receptive-field coverage."
        },
        "data_readiness": {
          "value": 4,
          "why": "NCCT and delayed masks are public; no new labels are required for the primary audit."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "The factorial statistic is standard, but anatomical-validity gates are custom."
        },
        "negative_result_value": {
          "value": 2,
          "why": "A null remains weak unless several sensitivity gates pass, so the rubric cap is respected."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Targeted search found the two component literatures but not their model-audit intersection."
        },
        "regret": {
          "value": 5,
          "why": "Delayed ground-truth geometry is a fundamental benchmark issue that can be audited cheaply."
        }
      },
      "priority_score": 3.5,
      "unverified_claims": [
        "CSF edits can be anatomically realistic with parenchymal bit-identity",
        "the model has adequate receptive-field coverage",
        "reserve-by-edema interaction is powered",
        "follow-up mask geometry contains edema-related expansion",
        "exact novelty"
      ],
      "plain_pitch": "The skull is a rigid container, so swelling has very different geometric effects depending on how much fluid space is available. This study asks whether a model trained on scans taken days later learned to use that spare space when drawing the future infarct, even though spare space is not injured tissue. If true, the same simulated tissue swelling would expand the prediction more when visible fluid reserve is low.",
      "charter": "isles24"
    }
  ]
}


===== ideas/scout-isles24-003/run_provenance.json =====
{
  "timestamp": "2026-08-18T06:54:20+00:00",
  "git_commit": "49c1368f6cc5395313ea493f9953b93faf5ecbb2",
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


===== ideas/scout-isles24-003/scout_candidates.json =====
{
  "cycle": "scout-isles24-003",
  "charter": "isles24",
  "date": "2026-08-18",
  "track": "baseline,wide",
  "dataset_verification": {
    "verified_facts": [
      "The primary dataset paper reports 245 patients: 149 in the public training set and 96 in the hidden test set. The earlier challenge report describes the planned split as 150 training and 98 hidden-test cases; this card uses the realized 149/96 counts and records the discrepancy rather than reconciling it by inference (DOI 10.1148/ryai.250603; arXiv:2408.10966).",
      "The official repository's case schema lists acute-session NCCT, CTA, 4D CTP, and four perfusion maps (CBF, CBV, MTT, Tmax). The dataset paper additionally documents follow-up DWI/ADC, clinical data through 3 months, vessel-occlusion masks, and infarct delineations (https://github.com/ezequieldlrosa/isles24; DOI 10.1148/ryai.250603).",
      "The prediction target is final post-treatment infarct tissue on follow-up MRI acquired 2-9 days after the acute CT, not the acute lesion visible at presentation. The reference masks were produced by a hybrid human-AI process initiated with DeepISLES and corrected under expert supervision (DOI 10.1148/ryai.250603; arXiv:2505.18424).",
      "The official evaluation uses per-case Dice, absolute volume difference, lesion-wise F1, and absolute lesion-count difference, with case-and-metric rank aggregation in the MICCAI challenge report (arXiv:2408.10966; https://github.com/ezequieldlrosa/isles24).",
      "The public training archive is hosted on Zenodo under CC BY-NC-SA 4.0 with no DUA or registration stated on the record inspected by the program; the official GitHub README still says CC BY-NC and registration, so downstream use must follow the version-pinned Zenodo record and flag this documentation mismatch before releasing derivatives (DOI 10.5281/zenodo.16731717; https://github.com/ezequieldlrosa/isles24)."
    ],
    "source_supported_interpretations": [
      "Because every included case couples preinterventional CT to post-treatment infarct, ISLES'24 is load-bearing for tests of which acute image quantities a final-infarct model uses after reperfusion; it is not merely another acute-lesion segmentation set.",
      "The public 149-case release is large enough for Stage-0 censuses but may be underpowered for rare signs or vessel variants. None of the five cards assumes the hidden set is downloadable."
    ],
    "unresolved_dataset_facts": [
      "The archive-level completeness and semantics of the LVO and multilabel Circle-of-Willis masks have not been inspected in this stage.",
      "The exact per-case CT acquisition/reconstruction fields and whether resampled NCCT preserves quantitative HU to the required tolerance remain unverified.",
      "No released winning checkpoint with fully inspectable input and normalization semantics was verified; cards therefore begin with a frozen, held-out-performing reproduced model gate."
    ],
    "sources": [
      "https://pubs.rsna.org/doi/10.1148/ryai.250603 (PMID 42017802)",
      "https://arxiv.org/abs/2408.10966",
      "https://arxiv.org/abs/2408.11142",
      "https://github.com/ezequieldlrosa/isles24",
      "https://zenodo.org/records/16731717 (DOI 10.5281/zenodo.16731717)",
      "https://isles-24.grand-challenge.org/"
    ]
  },
  "all_questions": [
    {"n": 1, "question": "Is an ISLES'24 final-infarct model using loss of gray-white differentiation in the insular ribbon and basal ganglia as a map of already injured tissue?", "disposition": "DEVELOPED as isles24-scout-003-c01; radiologist term: loss of gray-white differentiation/ASPECTS early ischemic change."},
    {"n": 2, "question": "Is an ISLES'24 model using clot burden—the length and arterial extent of the occlusion—to predict how much threatened tissue survives reperfusion?", "disposition": "DEVELOPED as isles24-scout-003-c02; radiologist term: clot burden score."},
    {"n": 3, "question": "[Network science] Is an ISLES'24 model using Circle-of-Willis graph redundancy—the number of patent alternate paths around the occlusion—as a reserve for maintaining flow?", "disposition": "DEVELOPED as isles24-scout-003-c03; suspected hard because released mask fidelity and variant support are unknown."},
    {"n": 4, "question": "[Hematology] Is an ISLES'24 model using dural-sinus blood attenuation on NCCT as an image proxy for hematocrit and therefore oxygen-carrying capacity?", "disposition": "DEVELOPED as isles24-scout-003-c04; obviously-wrong slot: a local segmentation network may ignore remote venous blood, but that is not immediately established."},
    {"n": 5, "question": "Is an ISLES'24 multimodal model using isolated sulcal effacement with preserved gray-white junction as a sign of viable tissue supported by engorged collaterals?", "disposition": "DEVELOPED as isles24-scout-003-c05; radiologist term: isolated sulcal effacement."},
    {"n": 6, "question": "Is an ISLES'24 model using the hyperdense artery sign as an image estimate of red-cell-rich thrombus composition?", "disposition": "DROPPED: it overlaps c02 and the prior perviousness candidate; clot extent provides a cleaner intervention than composition inferred from density."},
    {"n": 7, "question": "[Information theory] Is an ISLES'24 model using local entropy of the CTP time curve as a measure of microvascular mixing?", "disposition": "DROPPED: entropy has no uniquely physician-legible physiological referent and is confounded with motion and dose noise."},
    {"n": 8, "question": "Is an ISLES'24 model using carotid-siphon calcification as a marker of chronically impaired cerebrovascular reserve?", "disposition": "DROPPED: calcification is computable, but no within-case edit cleanly separates chronic reserve from age and systemic vascular burden."},
    {"n": 9, "question": "Is an ISLES'24 model using cortical atrophy—the patient's intracranial reserve—to decide how much swelling a predicted infarct can tolerate?", "disposition": "DROPPED: the dataset target is infarct tissue, not edema tolerance or functional recovery, so the attractive reserve story mismatches the segmentation endpoint."},
    {"n": 10, "question": "Is an ISLES'24 model using the CTA spot where the artery tapers before the clot as a signature of embolic versus in-situ occlusion?", "disposition": "DROPPED: no annotation-free validated etiologic measurement was found, so X fails the compute-today eligibility rule."}
  ],
  "quota_note": "The set fills 1 Mode A, 2 Mode B, and 2 Mode C; all five are CT/radiology and all use ISLES'24 because the charter makes that dataset mandatory. The generic instruction allowing no more than two candidates on one dataset conflicts with that charter, so the charter controls and the conflict is disclosed. Zero revivals: no portfolio unblock condition has a newly verified fact. Five different experimental grammars are used; no design template repeats.",
  "candidates": [
    {
      "id": "isles24-scout-003-c01",
      "parent_ids": [],
      "search_mode": "A",
      "entry_point": 2,
      "title": "Did preprocessing teach the winner to read the disappearing insular ribbon?",
      "question": "Is an ISLES'24 final-infarct model using loss of gray-white differentiation in the insular ribbon and basal ganglia as a map of already injured tissue?",
      "rung": "Target rung 1: use of an automated gray-white attenuation-contrast measurement; rung 2 requires center-held-out replication and convergence across at least two model families.",
      "deliverable_sentence": "The final-infarct model is using loss of gray-white differentiation in established ASPECTS regions as an acute-tissue-injury signal.",
      "X_measurement": "Register an ASPECTS atlas automatically, erode each region, and compute the affected-to-mirrored difference in gray-matter versus adjacent white-matter HU contrast; automated contralateral densitometry is described by Takahashi et al. (PMID 26158082), while automated ASPECTS systems provide directly executable precedents (DOI 10.3174/ajnr.A5889; DOI 10.1002/hbm.25845). Compute-today test: YES on any unseen NCCT using an atlas, midsagittal reflection, tissue masks, and HU arithmetic; no new annotator.",
      "suspected_signal": "Cytotoxic edema blurs the normally higher attenuation of cortex and deep gray matter relative to white matter; the winning recipe's large preprocessing gain makes a low-contrast NCCT cue a plausible unfinished story, although the gain itself does not prove this cue caused it (arXiv:2505.18424).",
      "use_vs_association": "Selective representation erasure: learn a gray-white-contrast direction from held-out-free training cases, remove it at inference while preserving decodability of Tmax burden, lesion side, and global HU, and require a region-specific fall in predicted infarct probability beyond norm-matched random directions; an input-space contrast-restoration dose response is a secondary corroboration.",
      "keystone_prerequisite": "A frozen ISLES'24 model that actually consumes quantitative NCCT achieves non-trivial held-out performance and exposes a representation in which gray-white contrast can be erased without destroying perfusion severity or anatomy.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The nearby facts—NCCT is released and a winning method used custom windowing—do not establish that the reproduced model uses NCCT or that erasure is selective. Those are the real Stage-0 gates.",
      "rung_reached": "0; rung 1 after selective erasure plus concordant input dose response; rung 2 after model-family and center replication.",
      "dies_like_prior": "Resembles idea-010 (CIRCULARITY), because early injury and final infarct are related. It differs by testing use of a named continuous image contrast while holding perfusion information and anatomy decodable; merely detecting an acute lesion is insufficient to pass selective erasure and graded restoration.",
      "closest_prior_work": "Automated ASPECTS work detects early ischemic change on NCCT (PMID 30498017; PMID 35357053), and the winning ISLES paper reports preprocessing-dependent performance (arXiv:2505.18424). Neither tests whether a final-infarct model uses regional gray-white contrast. This is a targeted gap, not a verified novelty claim.",
      "existing_assets": "Public NCCT and registered perfusion maps for 149 cases; automated ASPECTS and densitometry precedents; reproducible nnU-Net family; official metrics.",
      "smallest_decisive_experiment": "Freeze a center-stratified split; train one NCCT+perfusion model and require prespecified improvement over its perfusion-only twin. On 40 held-out cases, run selective erasure and three-level contrast restoration with random-direction and mirrored-unaffected controls. Roughly 30-50 GPU-hours and 7-10 days to first decision.",
      "standing_confounds_addressed": "Within-case mirroring controls patient, scanner, site, habitus, and prevalence; frozen split prevents leakage; perfusion decodability tests gross collateral damage. Reconstruction and beam hardening are not fully ruled out and require region/site stratification. Follow-up label provenance does not enter the primary paired output change.",
      "alternative_explanations": ["Erasure removes generic lesion severity; ruled against by preserved Tmax/core-volume decodability and random directions.", "The response is an edit artifact; bounded by physiologic contrast ranges, discriminator checks, and agreement with representation erasure.", "Windowing rather than biology explains the signal; this remains a model-mechanism explanation at rung 1 and forbids a claim that the model measures irreversible core."],
      "anticipated_negative": "Decisive only after the NCCT incremental-performance and erasure-selectivity gates; otherwise sensitivity-limited. A gated null shows that the preprocessing success did not translate into use of this radiologist-recognized cue.",
      "remaining_legwork": "2 days for archive/input census, 4-6 days for twin models, 3 days for probes: 7-10 days.",
      "design_template": "representation-erasure",
      "entry_point_2_requirements": "Measurement: mirrored ASPECTS-region gray-white HU contrast. Confused artifact: reconstruction noise and beam hardening; quantify local noise, stratify by site/region, and include unaffected-side controls.",
      "scores": {
        "clarity": {"value": 5, "why": "One named radiologic sign, one quantitative measurement, and a directional intervention."},
        "identifiability": {"value": 3, "why": "Dual representation/input evidence is promising, but selective erasure and reconstruction effects remain unverified."},
        "medical_relevance": {"value": 4, "why": "Gray-white loss is a core acute-stroke reading task and bears on what the model calls already injured."},
        "interest": {"value": 4, "why": "It gives a physiological candidate explanation for the winner's preprocessing-dependent gain."},
        "prior_legwork": {"value": 4, "why": "Measurement and model recipes exist; the actual trained audit model does not."},
        "feasibility": {"value": 3, "why": "Capped because the true model/representation keystone is not inspected."},
        "data_readiness": {"value": 4, "why": "Required public modalities exist, though the archive is large."},
        "evaluation_readiness": {"value": 3, "why": "Official segmentation metrics exist; selectivity gates are custom."},
        "negative_result_value": {"value": 3, "why": "Useful after the explicit NCCT contribution and sensitivity gates."},
        "novelty_confidence": {"value": 3, "why": "Targeted primary-source search found adjacent detection and challenge work, not this audit; not exhaustive."},
        "regret": {"value": 4, "why": "A large preprocessing effect and an established radiologic signal are one experiment apart."}
      },
      "priority_score": 3.65,
      "unverified_claims": ["NCCT provides incremental performance in the reproduced model", "quantitative HU survives released preprocessing", "selective representation erasure is achievable", "novelty beyond targeted search"],
      "plain_pitch": "Radiologists look for fading contrast between gray and white brain tissue as an early sign of stroke injury. This study asks whether a final-infarct model uses that same sign, rather than merely benefiting from better-looking scans. If true, selectively removing that contrast signal would change predictions in the affected regions while leaving perfusion information intact."
    },
    {
      "id": "isles24-scout-003-c02",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "How much artery did the clot occupy?",
      "question": "Is an ISLES'24 model using clot burden—the length and arterial extent of the occlusion—to predict how much threatened tissue survives reperfusion?",
      "rung": "Target rung 1; rung 2 requires replication across centers and agreement between geometric and artery-segment clot-burden measurements.",
      "deliverable_sentence": "The final-infarct model is using clot burden—the length and arterial extent of the occlusion—beyond the downstream perfusion deficit.",
      "X_measurement": "Compute centerline clot length and an automated modified clot-burden score from the CTA/LVO mask: subtract involved intracranial ICA/M1/M2 segments from a 10-point arterial template. CTA clot burden is an established quantitative construct (PMID 25804568); automatic centerline length requires only the released occlusion mask plus vessel segmentation. Compute-today test: YES if the mask encodes full thrombus extent; that file-level semantic is the keystone.",
      "suspected_signal": "A longer, more proximal clot blocks more arterial branches, carries more fibrin/red-cell material, and is harder to clear quickly; even among successfully reperfused patients it can prolong tissue ischemia and leave a larger final infarct.",
      "use_vs_association": "Regional substitution changes only clot extent along the automatically segmented arterial centerline while keeping occlusion site, perfusion maps, distal vessel image, and all clinical variables fixed; a monotone output response beyond equal-volume vessel and nonvessel shams tests use rather than label association.",
      "keystone_prerequisite": "The released LVO mask delineates enough of the thrombus extent—not merely an occlusion point—to support stable automatic clot-length and burden measurements.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The dataset paper verifies that vessel-occlusion masks exist, but not their voxel semantics or post-erosion extent. Treating that nearby fact as the keystone would repeat the program's wrong-keystone error.",
      "rung_reached": "0; rung 1 after mask census and gated substitution; rung 2 after two-site and two-measurement replication.",
      "dies_like_prior": "Most resembles idea-016 (IDENTIFIABILITY_FAILURE), where contrast flow covaried with disease and protocol. Here the confirmatory edit freezes perfusion, timing, site, and occlusion location and changes only thrombus extent; the remaining threat is edit realism, not protocol confounding.",
      "closest_prior_work": "Clinical studies relate CTA clot burden and NCCT clot characteristics to outcome (PMID 25804568; PMID 27576312). They do not hold the downstream perfusion shadow fixed or audit model use. The exact delta is a within-case use test in a final-infarct model; novelty remains unaudited.",
      "existing_assets": "Co-registered NCCT/CTA/CTP, stated LVO masks, 149 final-infarct cases, vessel-segmentation tools, and official output metrics.",
      "smallest_decisive_experiment": "Inspect all mask headers and 30 random masks; require at least 60 usable full-extent masks and inter-perturbation clot-length ICC >=0.85. On 30 held-out usable cases, apply +/-25% and +/-50% centerline-extent substitutions and shams. Five days after a trained model; under 15 GPU-hours for inference.",
      "standing_confounds_addressed": "Within-case edits fix scanner, vendor, protocol, site, positioning, habitus, prevalence, referral, and treatment covariates; fixed perfusion maps block the dominant hemodynamic mediator. They do not rule out an artificial vessel-discontinuity cue or CTA registration artifacts; centerline-continuity and discriminator gates address but cannot eliminate these.",
      "alternative_explanations": ["The model reacts to vessel discontinuity, not clot burden; continuity-preserving inpainting and equal-length contralateral vessel shams test this.", "Clot edits are out of distribution; changes are bounded to observed within-site length and attenuation distributions.", "The model uses occlusion site; site and proximal endpoint remain fixed."],
      "anticipated_negative": "Decisive if mask, realism, and positive-control gates pass: a null would show the model reads the downstream perfusion consequence but not clot extent itself.",
      "remaining_legwork": "2 days mask census, 2 days vessel-centerline QA, 3-5 days interventions: about one week after the shared model exists.",
      "design_template": "regional-substitution",
      "entry_point_2_requirements": "Measurement: centerline clot length and modified clot-burden score. Confused artifact: vessel segmentation breaks and CTA bolus timing; require continuity QA and use geometry rather than absolute enhancement as primary X.",
      "scores": {
        "clarity": {"value": 5, "why": "Clot length/segment burden and monotone response are explicit."},
        "identifiability": {"value": 4, "why": "Holding perfusion and site fixed isolates clot geometry unusually well, conditional on realistic editing."},
        "medical_relevance": {"value": 4, "why": "Clot burden affects treatment difficulty and infarct evolution."},
        "interest": {"value": 4, "why": "Tests whether multimodal models look upstream at the cause or only downstream at perfusion."},
        "prior_legwork": {"value": 3, "why": "Clinical measures exist, but automatic mask semantics and editing are unfinished."},
        "feasibility": {"value": 3, "why": "Capped by uninspected mask semantics."},
        "data_readiness": {"value": 3, "why": "Public, but useful-case count is unknown."},
        "evaluation_readiness": {"value": 3, "why": "Paired output change is direct; edit-validity gates are custom."},
        "negative_result_value": {"value": 4, "why": "A gated null cleanly distinguishes upstream clot use from downstream perfusion use."},
        "novelty_confidence": {"value": 3, "why": "No model-use study found in targeted search; not proof of novelty."},
        "regret": {"value": 4, "why": "The stated occlusion masks make this an unusually cheap upstream-versus-downstream test if their semantics hold."}
      },
      "priority_score": 3.8,
      "unverified_claims": ["LVO masks encode full thrombus extent", "at least 60 usable cases", "realistic continuity-preserving edits", "exact novelty"],
      "plain_pitch": "A clot can block a short piece of one artery or occupy a long stretch with several branches. The study asks whether the model uses that clot burden itself, beyond the perfusion deficit the clot creates. If true, changing only the apparent clot extent while freezing perfusion would shift the predicted final infarct."
    },
    {
      "id": "isles24-scout-003-c03",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "The arterial network's spare route",
      "question": "Is an ISLES'24 model using Circle-of-Willis graph redundancy—the number and caliber of patent alternate paths around the occlusion—as a reserve for maintaining flow?",
      "rung": "Target rung 1 use of a graph-derived image quantity; rung 2 requires external CTA replication and agreement with measured distal collateral filling.",
      "deliverable_sentence": "The final-infarct model is using Circle-of-Willis alternate-path redundancy as an image marker of proximal collateral reserve.",
      "X_measurement": "Convert the released multilabel Circle-of-Willis vessel mask to a graph whose edge weights are centerline minimum radii; remove the occluded edge and compute edge-disjoint source-to-territory paths plus max flow. Compute-today test: YES on an unseen CTA with a multilabel mask, using deterministic skeletonization and graph algorithms; no human labels. Clinical CTA work defines complete, nonisolating-incomplete, and isolating-incomplete variants (PMID 39788631).",
      "suspected_signal": "The Circle of Willis is a hydraulic network: communicating arteries provide parallel routes around a proximal blockage, so topology and caliber determine whether pressure can reach the threatened territory before leptomeningeal routes are recruited.",
      "use_vs_association": "Graph-edge intervention: render patent-to-hypoplastic and hypoplastic-to-patent communicating-artery variants within each case while preserving the occlusion, distal CTA enhancement, brain images, and perfusion maps; require output changes predicted by the signed change in alternate-path capacity and absent for topology-neutral vessel-caliber shams.",
      "keystone_prerequisite": "The released multilabel Circle-of-Willis masks accurately distinguish communicating-artery branches and calibers in enough cases for graph edits to represent real anatomic variants rather than segmentation artifacts.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The Zenodo description's existence claim for automated Circle-of-Willis masks is not evidence of branch-level fidelity. Accuracy, coverage, and usable variant counts are the load-bearing facts.",
      "rung_reached": "0; rung 1 after mask-fidelity and graph-edit gates; rung 2 after external CTA and distal-filling agreement.",
      "dies_like_prior": "Resembles idea-009 (IDENTIFIABILITY_FAILURE), which tried to interpret vascular geometry amid age, disease, and acquisition. This design changes graph connectivity within case while freezing those factors and the perfusion field. It also differs from isles24-scout-001-c02: that candidate tests distal collateral reach; this one tests proximal network redundancy upstream of that reach.",
      "closest_prior_work": "Large CTA studies establish Circle-of-Willis variation frequencies (DOI 10.1016/j.wneu.2017.07.084) and association of variant classes with outcome after successful revascularization (PMID 39788631). They do not audit final-infarct models or intervene on graph topology. Exact novelty is unverified.",
      "existing_assets": "CTA, stated automatic multilabel Circle-of-Willis masks, LVO masks, perfusion maps, two centers, standard skeleton/graph algorithms.",
      "smallest_decisive_experiment": "Stage 0: visually inspect only for tool QA—not new labels—30 masks and quantify graph validity automatically in all cases; require >=20 cases in each of two common editable variant families and stable edge radii under one-voxel perturbation. Then run paired edge interventions on 40 held-out cases. Ten to fourteen days, under 20 GPU-hours after model training.",
      "standing_confounds_addressed": "Within-case intervention holds scanner, vendor, protocol, site, age, habitus, referral, and label prevalence; fixed perfusion separates direct CTA topology use from its existing downstream consequence. It does not fully rule out synthetic-vessel artifacts or CTA phase effects. No new annotation burden is required; visual inspection is QA, not an input or endpoint.",
      "alternative_explanations": ["The model detects added bright voxels; topology-neutral added-vessel shams match volume and intensity.", "The model uses vessel caliber generally, not alternate paths; edits with equal total vessel volume but different connectivity discriminate them.", "Automatic masks hallucinate variants; graph-validity and raw-CTA agreement gates must pass before inference."],
      "anticipated_negative": "Sensitivity-limited if editable variant support is thin; decisive after topology, realism, and positive-control gates. A gated null says the model ignores a proximal collateral route already visible in CTA.",
      "cross_domain": {"borrowed_construct": "Network robustness and max-flow/min-cut from graph theory.", "measurement_it_implies": "Edge-disjoint paths and caliber-weighted max flow after deleting the occluded edge.", "what_changes_if_dropped": "The study could fall back to coarse complete/incomplete anatomy classes, but it would lose the graded intervention and most of its identifiability."},
      "remaining_legwork": "3 days mask/variant census, 3 days graph validation, 4-6 days renderer and inference: roughly two weeks.",
      "design_template": "other:graph-edge-intervention",
      "design_template_justification": "The causal unit is graph connectivity, not a contiguous image region; none of the named templates captures matched edge addition/removal with topology-neutral shams.",
      "entry_point_2_requirements": "Measurement: caliber-weighted alternate-path capacity. Confused artifact: CTA phase and automated branch hallucination; fixed within-case intensity plus raw-CTA/mask agreement gates address them.",
      "scores": {
        "clarity": {"value": 4, "why": "The graph quantity is precise, though rendering rules need Stage-0 freezing."},
        "identifiability": {"value": 4, "why": "Connectivity-changing versus volume-matched topology-neutral edits isolate the claimed graph property."},
        "medical_relevance": {"value": 4, "why": "Alternate arterial routes are a plausible determinant of tissue survival during occlusion."},
        "interest": {"value": 5, "why": "It asks whether the network model has learned a literal vascular-network robustness calculation."},
        "prior_legwork": {"value": 3, "why": "Masks are stated and graph tools are mature; fidelity and rendering are not."},
        "feasibility": {"value": 3, "why": "Capped by uninspected mask fidelity and variant support."},
        "data_readiness": {"value": 3, "why": "Public but archive-level mask properties unknown."},
        "evaluation_readiness": {"value": 3, "why": "Signed paired response is simple; image-validity tests are custom."},
        "negative_result_value": {"value": 3, "why": "Strong only if enough real variant support and edit sensitivity are shown."},
        "novelty_confidence": {"value": 3, "why": "Adjacent anatomy/outcome papers found, no use audit; formal audit pending."},
        "regret": {"value": 5, "why": "A released multilabel arterial graph makes an otherwise difficult mechanism unusually testable."}
      },
      "priority_score": 3.8,
      "unverified_claims": ["branch-level mask fidelity", "sufficient editable variant families", "model consumes CTA effectively", "synthetic graph edits are in distribution", "novelty"],
      "plain_pitch": "The arteries at the base of the brain form a loop that can route blood around a blockage. This study turns that loop into a graph and asks whether the model uses the number and size of spare routes. If true, changing connectivity while keeping the total amount of visible vessel and the perfusion maps fixed would change the prediction in the direction expected from the new route."
    },
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
      "alternative_explanations": ["The model reacts to any remote bright structure; skull and extracranial-vein shams test this.", "Sinus HU is reconstruction/site, not blood composition; within-case dose response can establish use but not physiology, hence the rung-1 wording.", "The local network has no receptive field from sinus to lesion; receptive-field inspection is an early feasibility gate, and a null is uninterpretable if coverage fails."],
      "anticipated_negative": "Sensitivity-limited unless receptive-field and positive-control gates pass; with them, a null is useful evidence that the model does not exploit this globally available physiologic proxy.",
      "cross_domain": {"borrowed_construct": "Oxygen-delivery accounting from hematology: delivery is blood flow multiplied by arterial oxygen content.", "measurement_it_implies": "Unenhanced venous-blood HU as an image proxy for red-cell concentration.", "what_changes_if_dropped": "Without the hematology link, the experiment becomes an uninteresting remote-intensity shortcut audit and should be killed."},
      "remaining_legwork": "2 days HU/site census, 1 day receptive-field check, 2 days interventions: under one week after model availability.",
      "design_template": "regional-removal",
      "entry_point_2_requirements": "Measurement: median eroded dural-sinus HU. Confused artifact: reconstruction/site and partial-volume skull; local noise normalization, erosion, and site gates are mandatory.",
      "scores": {
        "mechanism_clarity": {"value": 5, "why": "Named physical chain: red-cell concentration to HU and oxygen content, with an exact measurement."},
        "identifiability": {"value": 3, "why": "Use of HU can be identified, but physiological hematocrit attribution cannot within ISLES alone."},
        "interest": {"value": 5, "why": "A routine grayscale value functioning as an oxygen gauge is surprising and falsifiable."},
        "medical_relevance": {"value": 3, "why": "Oxygen delivery matters biologically, but clinical consequence is indirect without laboratory validation."},
        "clarity": {"value": 5, "why": "One remote region, one scalar, one signed dose response."},
        "prior_legwork": {"value": 3, "why": "The HU relationship is established; ISLES validation and model assets remain."},
        "feasibility": {"value": 3, "why": "Reported outside Mode C score and capped by quantitative-HU uncertainty."},
        "data_readiness": {"value": 3, "why": "NCCT is public; lab hematocrit and HU fidelity are not verified."},
        "evaluation_readiness": {"value": 3, "why": "Paired response is ready; proxy-validity gates are custom."},
        "negative_result_value": {"value": 2, "why": "A null remains sensitivity-limited if the model architecture lacks global receptive coverage."},
        "novelty_confidence": {"value": 2, "why": "Only targeted searching was performed."},
        "regret": {"value": 3, "why": "Very cheap and memorable, but the physiology may not survive dataset preprocessing."}
      },
      "mode_c_priority_score": 4.15,
      "unverified_claims": ["quantitative sinus HU fidelity", "absence of contrast contamination", "receptive-field coverage", "sinus HU ranks hematocrit in this cohort", "novelty"],
      "plain_pitch": "Red blood cells make blood look denser on an unenhanced CT scan, and their concentration affects how much oxygen reaches threatened brain tissue. This speculative test asks whether the model reads the large venous sinuses as a crude oxygen gauge. A true result would be a graded change in lesion predictions when only sinus density is altered, but it would not by itself prove that the model has measured anemia."
    },
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
      "use_vs_association": "Counterfactual synthesis swaps the local triad—sulcal CSF fraction, pial-vessel occupancy, and preserved gray-white contrast—between matched delayed territories while holding Tmax/CBF/CBV, tissue location, and total edited volume fixed. A survival-directed output change must occur only for the coherent triad, not isolated CSF deletion or vessel addition.",
      "keystone_prerequisite": "ISLES'24 contains enough automatically detectable isolated-sulcal-effacement territories, and single-phase CTA plus NCCT can distinguish the collateral-engorgement pattern from edema and registration error without new expert labels.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The published sign occurred in only 7.4% of a selected LVO cohort. With 149 ISLES cases, expected support may be single digits, and the automatic construct has never been validated here; this is the real keystone.",
      "rung_reached": "0; rung 1 after support, construct, and coherent-triad gates; rung 3 only with external multiphase/dynamic collateral validation.",
      "dies_like_prior": "Resembles idea-005's ANNOTATION_PROVENANCE risk if a radiologist's call defines the sign. This card avoids annotator-dependent input by prespecifying an image-computable triad, but construct validity is weaker and honestly capped. It also differs from isles24-scout-001-c02 by testing a parenchymal-sulcal sign of collateral support rather than distal arterial reach itself.",
      "closest_prior_work": "The primary case series defined isolated sulcal effacement and linked it to engorged leptomeningeal vessels and spared follow-up tissue (PMID 25931460). Quantitative CTA collateral scoring is acquisition-phase sensitive (PMID 29674417). No located work tests model use of the coherent sign; the rarity and phase dependence make this a deliberately speculative candidate.",
      "existing_assets": "Registered NCCT/CTA/perfusion maps, final MRI masks, automatic tissue and vessel segmentation tools, and a precise prior clinical phenotype.",
      "smallest_decisive_experiment": "Stage 0 on all 149 cases: compute the triad blind to outcomes; require >=15 territories meeting fixed thresholds, stable detection under registration perturbation, and stronger ipsilateral pial-vessel occupancy without reduced gray-white contrast. If passed, run coherent and incoherent edits on the held-out subset. Two weeks; under 15 GPU-hours after model training.",
      "standing_confounds_addressed": "Within-territory matched edits hold scanner, vendor, protocol, site, habitus, prevalence, and referral; fixed perfusion maps separate the sulcal sign from measured delay/flow. CTA phase, edema, registration, and rarity remain major threats. Follow-up labels are secondary; primary evidence is paired model-output change.",
      "alternative_explanations": ["Effacement is edema, not collateral engorgement; preserved gray-white contrast plus pial-vessel occupancy is the discriminating conjunction.", "Single-phase CTA catches different bolus phases; within-case affected/mirror ratios help but cannot fully solve this.", "The coherent edit is simply more complex; each incoherent component and equal-volume controls quantify generic edit response."],
      "anticipated_negative": "Uninterpretable if fewer than 15 territories or construct gates fail; sensitivity-limited even after gates because the sign is rare. Accordingly negative-result value is capped at 2.",
      "remaining_legwork": "4-5 days automatic census and stability analysis, 3 days support review, 4-5 days synthesis: about two weeks if the rarity gate passes.",
      "design_template": "counterfactual-synthesis",
      "entry_point_2_requirements": "Measurement: low sulcal CSF fraction plus preserved gray-white contrast plus increased pial-vessel occupancy. Confused artifact: edema, registration, and CTA phase; the conjunction, perturbation stability, and within-case ratios address but do not eliminate them.",
      "scores": {
        "mechanism_clarity": {"value": 5, "why": "A specific anatomical mechanism—collateral vessels occupying sulci—with three measurable components."},
        "identifiability": {"value": 3, "why": "The coherent-versus-incoherent edit is discriminating, but CTA phase and construct validity remain."},
        "interest": {"value": 5, "why": "It reverses the usual reading of effacement from injury to possible rescue."},
        "medical_relevance": {"value": 4, "why": "Mistaking reversible tissue for core can affect treatment interpretation."},
        "clarity": {"value": 4, "why": "The conjunction is explicit but thresholds require preregistration."},
        "prior_legwork": {"value": 2, "why": "One small clinical series exists; automatic measurement is unvalidated."},
        "feasibility": {"value": 2, "why": "Reported outside Mode C score; rarity may kill it immediately."},
        "data_readiness": {"value": 3, "why": "All modalities are public, but support is unknown."},
        "evaluation_readiness": {"value": 2, "why": "Construct and synthesis gates are custom."},
        "negative_result_value": {"value": 2, "why": "Capped because rarity makes a null potentially uninterpretable."},
        "novelty_confidence": {"value": 2, "why": "Targeted search only and a niche sign invites missed literature."},
        "regret": {"value": 4, "why": "If support exists, ISLES'24 uniquely couples the sign to final tissue fate."}
      },
      "mode_c_priority_score": 4.15,
      "unverified_claims": ["at least 15 qualifying territories", "automatic triad validity", "CTA phase adequacy", "edit realism", "novelty"],
      "plain_pitch": "Flattened brain grooves usually sound like swelling and damage, but one rare stroke pattern may instead come from enlarged rescue vessels filling those grooves while the tissue remains intact. This study asks whether the model recognizes that full pattern. It proceeds only if enough cases can be found automatically and if the pattern can be separated from ordinary edema and scan-timing effects."
    }
  ]
}


===== ideas/scout-isles24-003/wide_candidates.json =====
{
  "candidates": [
    {
      "id": "isles24-scout-003-c06",
      "track": "wide",
      "title": "The bolus spreads like dye in a river",
      "question": "[transport physics / chromatography] Is an ISLES'24 raw-CTP final-infarct model using bolus dispersion—the spreading of contrast arrival times after delay is removed—as a marker of collateral path complexity?",
      "deliverable_sentence": "The final-infarct model is using local bolus dispersion, beyond mean arrival delay and perfusion-map severity, when predicting tissue fate.",
      "cross_field": {"borrowed_construct": "Advection-dispersion from transport physics and chromatography: a tracer pulse broadens as paths of different lengths mix.", "measurement_it_implies": "Deconvolve the tissue time-attenuation curve by the arterial input, align its first moment, and measure the second central moment and full width at half maximum of the nonnegative residue/transport kernel.", "what_changes_if_dropped": "Without advection-dispersion, curve width is an unnamed temporal texture and the signed delay-preserving intervention has no mechanistic interpretation."},
      "causal_chain": [
        {"link": "Long, heterogeneous collateral routes broaden the tissue bolus even after mean delay is aligned.", "check": "Test whether the dispersion measure agrees with independently computed dynamic collateral time and is stable to arterial-input placement."},
        {"link": "Broader transport kernels mark heterogeneous delivery not fully represented by CBF, CBV, MTT, or Tmax.", "check": "Regress dispersion on all four released maps and require substantial within-bin residual variation."},
        {"link": "A raw-CTP model uses that residual variation.", "check": "Apply delay- and area-preserving curve narrowing/broadening within case and measure paired output change."}
      ],
      "X_measurement": "For each parenchymal voxel, baseline-correct the 4D CTP curve, use an automatically selected contralateral proximal arterial input, fit a nonnegative delay-dispersion kernel, and report its second central moment (seconds squared) and full width at half maximum. PMID 29500248 establishes that delay/dispersion correction changes ischemic-core measurement; PMID 37693754 provides a dynamic-CT collateral-time comparator. The formula is automatic and computable today, but its stability on the released 1-frame/s series is uninspected.",
      "suspected_signal": "Collateral blood takes multiple routes with different transit times; their mixture broadens the contrast pulse, potentially distinguishing slow but coherent delivery from slow, heterogeneous delivery at the same Tmax.",
      "use_vs_association": "Within each held-out case, convolve or deconvolve only threatened-territory curves with physiologic transport kernels that change variance while preserving area, mean arrival time, baseline, peak support, and the four derived perfusion maps within frozen tolerances; a signed dose response beyond time-shuffled and mean-delay controls tests use rather than association.",
      "keystone_prerequisite": "A frozen raw-4D-CTP model with non-trivial untouched-case performance is obtainable, and the released temporal sampling supports stable dispersion estimates and map-preserving curve edits.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The dataset contains 4D CTP, but neither a suitable checkpoint nor the identifiability of dispersion at 1-frame/s has been inspected. If the model consumes only parametric maps, this candidate dies rather than silently changing its question.",
      "dies_like_prior": "It risks the DATA_ACCESS pause of idea-022 because both require an inspectable raw-CTP model; no changed unblock fact is claimed. It also risks IDENTIFIABILITY_FAILURE from delay and truncation, addressed only if mean delay, curve area, acquisition support, and derived maps remain invariant under the edit. Unlike idea-022, the manipulated estimand is kernel width inside a complete curve, not missing end-of-scan frames.",
      "closest_prior_work": "Lin et al. quantified how delay and dispersion correction changes CTP core estimates (PMID 29500248); Xu et al. quantified collateral time from perfusion CT (PMID 37693754); the ISLES'24 winning-method paper predicts final infarct from multimodal CT (arXiv:2505.18424). These are neighbors, not evidence that a learned model uses dispersion.",
      "novelty_neighbors": [
        "Lin L et al., Stroke 2018, DOI 10.1161/STROKEAHA.117.019562, PMID 29500248 — evaluates delay/dispersion correction in classical CTP quantification.",
        "Xu Y et al., Front Neurol 2023, PMID 37693754 — derives perfusion collateral time and validates it against dynamic CTA.",
        "ISLES'24 winning solution, arXiv:2505.18424 — final-infarct prediction from challenge imaging, without a reported dispersion-use audit."
      ],
      "novelty_delta": "The neighbors measure dispersion effects or train outcome models; the proposed paired audit asks whether the model itself responds to transport-kernel width when delay, area, and standard maps are held fixed.",
      "why_not_done": "NEW_CAPABILITY: ISLES'24 recently coupled public raw 4D CTP, registered maps, treatment-conditioned follow-up infarct masks, and a reproducible challenge recipe; before that combination, a map-preserving raw-curve use audit was difficult to run publicly.",
      "novelty_search_verdict": "NO_DUPLICATE_FOUND_LIMITED_SEARCH",
      "existing_assets": "Public 4D CTP and registered CBF/CBV/MTT/Tmax for 149 training cases; automatic curve fitting; official final-infarct metrics. No qualifying frozen raw-CTP checkpoint has been verified.",
      "smallest_decisive_experiment": "Stage 0 on 20 cases: estimate kernel width under three arterial-input placements and require ICC >=0.80 plus at least 30% residual interquartile range after conditioning on Tmax and MTT. If a frozen raw-CTP model gate passes, edit 24 untouched cases at three empirically supported width doses, with mean-delay, area, truncation, and map-recomputation tolerances frozen before outputs. Primary readout: paired change in predicted infarct probability mass within edited tissue.",
      "compute_envelope": "One Colab GPU session after a checkpoint exists: curve fitting and map checks are CPU work; 24 cases x 7 variants = 168 forward passes, targeted under 3 GPU-hours and 16 GB VRAM. Training a new qualifying model is outside this decisive-session budget and is an explicit prior gate.",
      "standing_confounds_addressed": "Within-case edits freeze patient, center, scanner, treatment, anatomy, and label prevalence. Moment constraints separate dispersion from delay and dose; recomputed-map tolerances separate it from the standard map channels; complete-curve and time-shift controls address truncation. Residual threats are deconvolution regularization and edit realism.",
      "alternative_explanations": ["The model reads mean delay: held invariant and separately perturbed as a positive control.", "The model reads a standard map changed by the edit: all four maps are recomputed and bounded by frozen tolerances.", "The response is convolution blur: an energy-matched temporally scrambled kernel is the sham."],
      "anticipated_negative": "A null is interpretable only after checkpoint, dispersion-reliability, edit-realism, and temporal positive-control gates pass; then it shows that this raw-CTP model reduces temporal information to delay/severity rather than using residual transport width.",
      "verified_dataset_facts": "Relies on the cycle's primary-source verification: 149 public training cases; acute NCCT, CTA, 4D CTP and CBF/CBV/MTT/Tmax maps; post-treatment infarct masks from follow-up DWI/ADC; CC BY-NC-SA 4.0 on the version-pinned Zenodo record (DOI 10.5281/zenodo.16731717; DOI 10.1148/ryai.250603; official GitHub repository).",
      "design_template": "counterfactual-synthesis",
      "scores": {
        "clarity": {"value": 5, "why": "One physical moment and one delay-preserving intervention define the question."},
        "identifiability": {"value": 3, "why": "Moment and map constraints address the main alternatives, but editable dispersion may not be separable at the released sampling rate."},
        "medical_relevance": {"value": 4, "why": "Collateral transport quality is central to survival of delayed tissue and would affect interpretation of raw-CTP models."},
        "interest": {"value": 5, "why": "It asks whether a network performs a tracer-transport calculation absent from standard map summaries."},
        "prior_legwork": {"value": 3, "why": "Dispersion and collateral-time methods exist; the model and edit validation do not."},
        "feasibility": {"value": 2, "why": "The raw-CTP checkpoint gate that paused idea-022 remains unresolved."},
        "data_readiness": {"value": 3, "why": "The public data exist but are large and temporal adequacy is uninspected."},
        "evaluation_readiness": {"value": 3, "why": "Paired deltas are direct; map-invariance and realism gates are custom."},
        "negative_result_value": {"value": 3, "why": "Useful only after stringent sensitivity and edit gates."},
        "novelty_confidence": {"value": 3, "why": "Targeted primary-source search found close measurement work but no use audit; not exhaustive."},
        "regret": {"value": 4, "why": "Raw curves contain information that map-only evaluations discard, making this an obvious audit if the checkpoint gate opens."}
      },
      "priority_score": 3.35,
      "unverified_claims": ["a qualifying raw-CTP checkpoint is obtainable", "dispersion is identifiable at released temporal sampling", "map-preserving curve edits are realistic", "the model has temporal sensitivity", "exact novelty"],
      "plain_pitch": "A contrast bolus can arrive late as one compact wave or arrive late after spreading through many routes. This study asks whether a model notices that spreading even when the usual blood-flow maps and average delay are kept the same. If it does, widening only the time curve should change predicted tissue death in a graded direction."
    },
    {
      "id": "isles24-scout-003-c07",
      "track": "wide",
      "title": "Does the model price the last mile of blood delivery?",
      "question": "[economic geography / facility location] Is an ISLES'24 model using distance to an arterial-territory border—the vascular network's costly last mile—as a vulnerability factor beyond local perfusion severity?",
      "deliverable_sentence": "The final-infarct model is using proximity to an arterial border zone as a tissue-vulnerability prior beyond the measured local perfusion deficit.",
      "cross_field": {"borrowed_construct": "The last-mile cost from economic geography: locations farthest from supply hubs are least redundant and most expensive to serve.", "measurement_it_implies": "A signed geodesic distance transform to subject-specific competing arterial supply fronts, with uncertainty from atlas and vessel-derived territory estimates.", "what_changes_if_dropped": "Without the last-mile construct this becomes generic location bias; the construct supplies the specific prediction that otherwise matched tissue nearer a competing supply boundary receives a different model response."},
      "causal_chain": [
        {"link": "Arterial border zones are distal from major supply trunks and may have less pressure reserve.", "check": "Compare atlas distance with CTA-derived centerline distance and published border-zone patterns."},
        {"link": "At matched CBF/Tmax, distance to a competing supply front retains variation in final tissue fate.", "check": "Held-out conditional analysis, explicitly association-only."},
        {"link": "The model uses that spatial prior.", "check": "Transport the same empirical multimodal tissue patch between matched interior and border-zone destinations while preserving local anatomy and perfusion statistics."}
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
        "Mangla R et al., Radiographics 2011, DOI 10.1148/rg.315105014, PMID 21918038 — border-zone imaging and pathophysiology.",
        "Carpenter DA et al., Neurology 1990, DOI 10.1212/WNL.40.10.1587, PMID 2215951 — PET study finding no selective chronic border-zone hemodynamic impairment.",
        "Deep Learning-Based Prediction of Final Infarct Core from CT Perfusion Data, PMID 41583397 — probabilistic CTP outcome model without a reported border-distance use test."
      ],
      "novelty_delta": "Clinical work studies whether border zones infarct; the proposed experiment asks whether a final-infarct network applies a border-distance prior to otherwise matched tissue and directly tests that use with destination swaps.",
      "why_not_done": "BLIND_SPOT: stroke prediction work usually represents location implicitly through convolutional coordinates, while perfusion research stratifies named infarct patterns; neither tradition treats learned vascular distance as an auditable model input.",
      "novelty_search_verdict": "NO_DUPLICATE_FOUND_LIMITED_SEARCH",
      "existing_assets": "Registered multimodal images, public territory atlases, CTA and perfusion maps, 149 training cases, and standard registration/distance-transform tools.",
      "smallest_decisive_experiment": "On all public cases, perform a CPU common-support census and require at least 400 eligible patch pairs from at least 30 untouched cases, with median border-distance separation >=15 mm and standardized differences <0.1 for the four maps, cortical depth, tissue class, and vessel density. Then evaluate 30 cases x 4 paired swaps/shams with continuous probability-mass readout.",
      "compute_envelope": "One Colab GPU session after a shared frozen checkpoint: atlas warping and matching are CPU preprocessing; about 120 edited forward passes fit under 2 GPU-hours and 16 GB VRAM.",
      "standing_confounds_addressed": "Within-case swaps fix patient, scanner, center, treatment, and global severity; exact covariate matching addresses local perfusion/anatomy; parallel-boundary moves control displacement and interpolation. Territory uncertainty is propagated across atlas variants. Synthetic seams and unmeasured microvascular anatomy remain threats.",
      "alternative_explanations": ["The model uses cortical depth: explicitly matched and independently shifted in a control arm.", "The model reacts to interpolation: parallel-boundary swaps have the same displacement and interpolation.", "The atlas is wrong for the patient: require consistent sign across atlas-only and CTA-refined distance estimates."],
      "anticipated_negative": "If support, atlas-stability, edit-realism, and a local-perfusion positive control pass, a null is useful: this model treats fate as local physiology rather than pricing vascular location. Failure of common support is not a negative result; it is an identifiability kill.",
      "verified_dataset_facts": "Relies on the cycle's primary-source verification: public acute CTA and registered perfusion maps for 149 cases, post-treatment follow-up infarct masks, and stated automated vessel/Circle-of-Willis products whose fidelity remains unresolved (DOI 10.5281/zenodo.16731717; DOI 10.1148/ryai.250603; official repository).",
      "design_template": "regional-substitution",
      "scores": {
        "clarity": {"value": 4, "why": "Border distance and the destination-swap contrast are explicit; subject-specific territory definition remains conditional."},
        "identifiability": {"value": 3, "why": "Strong matching and shams help, but anatomy and territory uncertainty may leave no valid common support."},
        "medical_relevance": {"value": 4, "why": "A hidden location prior could fail when arterial anatomy or systemic pressure differs from training data."},
        "interest": {"value": 5, "why": "The claim that a model prices the vascular last mile is surprising and clinically legible."},
        "prior_legwork": {"value": 3, "why": "Border-zone science and atlases exist; the matched intervention has not been built."},
        "feasibility": {"value": 3, "why": "Capped by uninspected common support and territory fidelity."},
        "data_readiness": {"value": 3, "why": "Public registered data exist, but vessel-mask fidelity is unresolved."},
        "evaluation_readiness": {"value": 3, "why": "Paired output change is direct; support and edit gates are custom."},
        "negative_result_value": {"value": 3, "why": "A gated null discriminates spatial-prior from local-physiology behavior."},
        "novelty_confidence": {"value": 3, "why": "Three close primary neighbors were checked; the model-audit search was limited."},
        "regret": {"value": 4, "why": "Spatial priors are easy for segmentation networks to learn and almost never reported."}
      },
      "priority_score": 3.45,
      "unverified_claims": ["adequate matched patch support", "stable subject-level border distance", "CTA-derived territory refinement is valid", "patch substitutions are in distribution", "exact novelty"],
      "plain_pitch": "Blood supply has a last-mile problem: tissue near the boundary between two arterial territories may be harder to serve than tissue closer to a main route. This study asks whether the model quietly charges that location a higher risk even when local blood-flow measurements look the same. If true, moving the same realistic tissue pattern to a border location would change the prediction more than moving it the same distance along the border."
    },
    {
      "id": "isles24-scout-003-c08",
      "track": "wide",
      "title": "The skull is a fixed-volume pressure vessel",
      "question": "[continuum mechanics / pressure-vessel engineering] Is an ISLES'24 model using baseline intracranial compliance—the cerebrospinal-fluid space available to absorb swelling—to expand predicted final-infarct geometry beyond acute tissue injury?",
      "deliverable_sentence": "The final-infarct model is using baseline intracranial cerebrospinal-fluid reserve as a geometric prior on how far the follow-up infarct mask will expand.",
      "cross_field": {"borrowed_construct": "Compliance of a closed pressure vessel: added volume produces little displacement while reserve remains, then sharply greater deformation as reserve is exhausted.", "measurement_it_implies": "Automatic cerebrospinal-fluid volume divided by intracranial volume, plus local sulcal and ventricular reserve around the threatened hemisphere; response should be nonlinear near low reserve.", "what_changes_if_dropped": "Without compliance, cerebrospinal-fluid fraction is merely an age proxy; the borrowed construct supplies the interaction prediction between identical edema-like attenuation change and available reserve."},
      "causal_chain": [
        {"link": "Baseline cerebrospinal-fluid fraction measures room available for swelling inside the fixed skull.", "check": "Automatic segmentation stability and replication of its reported association with malignant edema, association-only."},
        {"link": "Follow-up masks acquired days later may contain geometry affected by edema as well as irreversibly injured tissue.", "check": "Compare mask displacement relative to arterial/perfusion boundaries across follow-up day and reserve strata; this remains an inference because follow-up edema labels are absent."},
        {"link": "The model uses reserve to shape its prediction.", "check": "Factorially edit cerebrospinal-fluid reserve and local edema attenuation while preserving parenchyma/perfusion, testing the compliance interaction rather than a main effect."}
      ],
      "X_measurement": "Segment ventricles and sulcal CSF automatically on NCCT and compute CSF/intracranial-volume ratio globally and within the affected hemisphere. PMID 35373655 reports that automatic baseline CSF/ICV improves malignant-edema prediction; PMID 29976584 defines CT net water uptake as an edema marker. The proposed X is reserve, not age or edema itself.",
      "suspected_signal": "Because the skull cannot expand, swelling first consumes cerebrospinal-fluid spaces. A model trained against 2–9-day follow-up masks could learn that identical acute injury produces different apparent lesion geometry in a brain with little versus abundant reserve.",
      "use_vs_association": "A 2x3 counterfactual factorial changes only extra-axial/ventricular CSF reserve (small empirically sampled inward/outward boundary deformations with parenchymal voxels unchanged) and separately changes affected-tissue net-water-uptake attenuation; a compliance mechanism predicts an interaction—larger output expansion from the same water-uptake dose under lower reserve—whereas an age shortcut predicts a CSF main effect.",
      "keystone_prerequisite": "Small CSF-boundary edits can alter measured reserve while keeping every parenchymal model input bit-identical outside a narrow CSF boundary and passing anatomical-realism gates; the frozen model's receptive field must connect those spaces to the threatened territory.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "ISLES'24 does not provide edema or mass-effect ground truth, and its target is infarct tissue rather than swelling. Even a positive model-use result would identify a geometric prior learned from the labels, not prove that reserve biologically changes irreversible infarction.",
      "dies_like_prior": "It directly confronts the endpoint-mismatch reason that dropped cortical atrophy in this cycle: the candidate survives only as a label-geometry/failure-mode audit, not as a tissue-survival claim. It also risks idea-010's CIRCULARITY if water uptake merely redraws acute lesion; the identifying endpoint is the reserve-by-water interaction with unchanged perfusion, not prediction of injury from injury.",
      "closest_prior_work": "Automatic CSF/ICV improves malignant-edema prediction after thrombectomy (PMID 35373655); net water uptake predicts malignant infarction (PMID 29976584); later midline shift predicts poor outcome (PMID 34494212). None of these studies audits whether a final-infarct segmentation model uses baseline reserve or whether follow-up-mask geometry carries that shortcut.",
      "novelty_neighbors": [
        "van der Worp-group registry study, 'Cerebrospinal fluid volume improves prediction of malignant edema after endovascular treatment of stroke,' PMID 35373655.",
        "Broocks G et al., Stroke 2018, DOI 10.1161/STROKEAHA.118.020507, PMID 29976584 — admission CT net water uptake predicts malignant infarction.",
        "McKeown ME et al., Neurocrit Care 2022, DOI 10.1007/s12028-021-01341-x, PMID 34494212 — follow-up midline shift over 3 mm predicts outcome."
      ],
      "novelty_delta": "Prior work predicts edema outcomes from reserve or water uptake; this study tests a specific interaction inside a final-infarct network and asks whether follow-up-label geometry taught the network a compliance shortcut.",
      "why_not_done": "BLIND_SPOT: edema prediction and infarct segmentation are treated as separate tasks, so the possibility that delayed infarct masks transmit pressure-vessel geometry back into the segmentation model falls between literatures.",
      "novelty_search_verdict": "NO_DUPLICATE_FOUND_LIMITED_SEARCH",
      "existing_assets": "NCCT, perfusion maps, follow-up masks acquired 2–9 days later, automatic brain/CSF segmentation tools, and published reserve and water-uptake formulas.",
      "smallest_decisive_experiment": "Stage 0 on 40 cases: require CSF/ICV segmentation ICC >=0.90 under one-voxel perturbation, at least 20 low- and 20 high-reserve held-out cases, and a model receptive field spanning reserve to lesion. Then run 24 cases x six factorial edits plus no-op and age-matched controls; primary statistic is the paired interaction in predicted probability mass and radial boundary displacement, not association with the final mask.",
      "compute_envelope": "One Colab GPU session after a frozen checkpoint: segmentation/edit construction is CPU work; fewer than 200 forward passes and bootstrap analysis target under 3 GPU-hours and 16 GB VRAM.",
      "standing_confounds_addressed": "The factorial interaction separates reserve from the main effects of age/atrophy and acute attenuation; within-case editing fixes patient, scanner, treatment, perfusion, and label. Parenchymal bit-identity and no-op warps control interpolation. Residual threats are unrealistic CSF geometry, architecture receptive field, and inability to validate edema-mediated label expansion directly.",
      "alternative_explanations": ["The model uses age-related atrophy: that predicts a CSF main effect, not the prespecified reserve-by-water interaction.", "Boundary edits distort cortex: affected parenchymal tensors must remain bit-identical and no-op deformation controls must be null.", "The model predicts true biological protection: prohibited; the card supports only use of reserve as a geometric prior."],
      "anticipated_negative": "A null is sensitivity-limited unless receptive-field, edit-realism, water-uptake positive-control, and interaction-power gates pass. After those gates, it usefully shows that the model's delayed-mask predictions are not modulated by visible intracranial reserve.",
      "verified_dataset_facts": "Relies on the cycle's primary-source verification that ISLES'24 pairs acute preintervention CT with final post-treatment infarct masks derived from MRI 2–9 days later in 149 public training cases. No edema or mass-effect annotation is claimed (DOI 10.1148/ryai.250603; DOI 10.5281/zenodo.16731717).",
      "design_template": "model-output-perturbation",
      "design_template_justification": "The identifying statistic is a factorial interaction in the frozen model's output under two orthogonally controlled input quantities; this is closer to a behavioral model-output perturbation than a regional substitution because neither edited region is exchanged with another case.",
      "scores": {
        "clarity": {"value": 4, "why": "The factorial interaction is precise, but the geometric-prior wording needs its prohibition against biological survival claims."},
        "identifiability": {"value": 3, "why": "The interaction separates age from compliance use, but label edema cannot be validated within ISLES'24."},
        "medical_relevance": {"value": 4, "why": "A pressure-reserve shortcut would distort predicted lesion boundaries and challenge interpretation of delayed-MRI ground truth."},
        "interest": {"value": 5, "why": "It links skull mechanics, annotation timing, and model behavior in a surprising falsifiable chain."},
        "prior_legwork": {"value": 4, "why": "Automatic reserve and water-uptake measures and strong clinical cohorts already exist."},
        "feasibility": {"value": 3, "why": "Capped by uninspected edit realism and receptive-field coverage."},
        "data_readiness": {"value": 4, "why": "NCCT and delayed masks are public; no new labels are required for the primary audit."},
        "evaluation_readiness": {"value": 3, "why": "The factorial statistic is standard, but anatomical-validity gates are custom."},
        "negative_result_value": {"value": 2, "why": "A null remains weak unless several sensitivity gates pass, so the rubric cap is respected."},
        "novelty_confidence": {"value": 3, "why": "Targeted search found the two component literatures but not their model-audit intersection."},
        "regret": {"value": 5, "why": "Delayed ground-truth geometry is a fundamental benchmark issue that can be audited cheaply."}
      },
      "priority_score": 3.5,
      "unverified_claims": ["CSF edits can be anatomically realistic with parenchymal bit-identity", "the model has adequate receptive-field coverage", "reserve-by-edema interaction is powered", "follow-up mask geometry contains edema-related expansion", "exact novelty"],
      "plain_pitch": "The skull is a rigid container, so swelling has very different geometric effects depending on how much fluid space is available. This study asks whether a model trained on scans taken days later learned to use that spare space when drawing the future infarct, even though spare space is not injured tissue. If true, the same simulated tissue swelling would expand the prediction more when visible fluid reserve is low."
    }
  ],
  "dropped": [
    {"question": "[porous-media physics] Is the model using clot perviousness as Darcy permeability?", "why": "Dropped because clot perviousness already sits adjacent to this cycle's clot-burden candidate and prior ISLES scouting; the field has an established NCCT/CTA estimator (PMID 26846859), so this would rotate the measurement rather than widen the hypothesis space."},
    {"question": "[seismology] Is the direction of the CTP arrival-time wavefront a compass for retrograde collateral filling?", "why": "Dropped as a re-instrumentation of live collateral-clock and vascular-detour candidates; it does not create a distinct deliverable sentence."},
    {"question": "[hormesis / evolutionary physiology] Does the model treat old infarct scars as ischemic preconditioning?", "why": "One step past defensible: chronic scars are inseparable from vascular burden and anatomy, and removing a scar could establish model use of the scar but not preconditioning. It dies by IDENTIFIABILITY_FAILURE."},
    {"question": "[information theory] Does cross-modal disagreement between CTA and perfusion maps act as an uncertainty code?", "why": "Absence or disagreement is not a physician-legible X, and no intervention separated true physiological discordance from registration and pipeline error without changing both. Ineligible under the use-versus-association rule."},
    {"question": "[ecology / source-sink dynamics] Does the model treat scattered penumbral islands as rescuable habitat patches?", "why": "One step past defensible and duplicative of the live percolation/connectivity candidate isles24-scout-002-c08; changing ecological vocabulary does not change the experimental grammar or estimand."}
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

