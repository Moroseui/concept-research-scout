You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
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


===== STAGE TASK =====
<!-- stage: probe_plan -->
Create the smallest computational feasibility probe for this idea. It must test the riskiest assumption—not attempt the entire proposed system.

Use `templates/probe_contract.yaml`. Keep the probe exploratory, validation-only, no more than 3 variants, one seed unless randomness itself is being tested, and at most 45 GPU minutes by default. Define invalidating failures separately from negative outcomes.

Write `probe_contract.yaml` in the idea folder and `README.md` in probes/IDEA_ID/. Do not implement code yet.

## Contract requirements file (overrides the defaults above)

If the idea folder contains `contract_requirements.md`, it is a
human-authored, ratification-gated specification and it WINS over every
default in this prompt (variant count, seed rule, GPU-minute cap, scale
of the probe). The contract you draft MUST satisfy every requirement in
that file, carry a `contract_version` field, and cite the requirements
file and any decision entries it names. The reviewer will check the
contract against the requirements file line by line; an unmet
requirement is a blocking finding. If a requirement is impossible or
contradictory, do not silently deviate: stop and write the conflict into
the contract draft as a blocking open question for the human.

