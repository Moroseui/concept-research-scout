You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-isles24-005
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

59 tracked ideas in this charter. Latest state per idea; full history in ledger.jsonl.

Work under other charters: evidence/cross_charter_index.md (facts, no scores).

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **IDENTIFIABILITY_FAILURE** x11: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
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
- **isles24-scout-005-c06** [UNAUDITED, score 4.0] -- Does the model trust tissue that obeys the flow equation?
- ... and 12 more (python scout.py backlog)

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
- **isles24-scout-005-c01** [SCOUT_ONLY/SCOUTED/baseline] -- What the winner's brain window revealed
- **isles24-scout-005-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The old stroke inside the new forecast
- **isles24-scout-005-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The bottleneck before the brain
- **isles24-scout-005-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The pressure history written in a winding artery
- **isles24-scout-005-c05** [SCOUT_ONLY/SCOUTED/baseline] -- Do sulci pin the predicted infarct edge?
- **isles24-scout-005-c06** [SCOUT_ONLY/SCOUTED/wide] -- Does the model trust tissue that obeys the flow equation?
- **isles24-scout-005-c07** [SCOUT_ONLY/SCOUTED/wide] -- The roughness of a heartbeat through starved tissue
- **isles24-scout-005-c08** [SCOUT_ONLY/SCOUTED/wide] -- Delay is not dispersion


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
- [isles24] **isles24-scout-005-c01** [SCOUT_ONLY] -- What the winner's brain window revealed
- [isles24] **isles24-scout-005-c02** [SCOUT_ONLY] -- The old stroke inside the new forecast
- [isles24] **isles24-scout-005-c03** [SCOUT_ONLY] -- The bottleneck before the brain
- [isles24] **isles24-scout-005-c04** [SCOUT_ONLY] -- The pressure history written in a winding artery
- [isles24] **isles24-scout-005-c05** [SCOUT_ONLY] -- Do sulci pin the predicted infarct edge?
- [isles24] **isles24-scout-005-c06** [SCOUT_ONLY] -- Does the model trust tissue that obeys the flow equation?
- [isles24] **isles24-scout-005-c07** [SCOUT_ONLY] -- The roughness of a heartbeat through starved tissue
- [isles24] **isles24-scout-005-c08** [SCOUT_ONLY] -- Delay is not dispersion
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


===== ideas/scout-isles24-005/README.md =====
# Scouting cycle isles24-005

Tracks: baseline, wide
Charter: isles24 (charters/isles24/CHARTER.md; scores are scoped to this charter and not comparable across charters)


===== ideas/scout-isles24-005/candidates_all.json =====
{
  "cycle": 5,
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
      "id": "isles24-scout-005-c01",
      "parent_ids": [],
      "search_mode": "A",
      "entry_point": 2,
      "title": "What the winner's brain window revealed",
      "question": "Is an ISLES'24 final-infarct model using the acute gray-to-white matter attenuation ratio as a quantitative tissue-injury signal?",
      "rung": "Target rung 1: demonstrate model use of gray-to-white attenuation contrast; rung 2 requires the same signed response in at least two model families and both centers.",
      "deliverable_sentence": "The final-infarct model is using the acute gray-to-white matter attenuation ratio as a tissue-injury signal.",
      "X_measurement": "Register a standard brain atlas, take median HU in paired cortical/deep-gray and adjacent white-matter regions outside bone and vessels, and compute GWR = median(gray HU)/median(white HU), plus the affected-to-contralateral ratio. This is the standard gray-white ratio arithmetic and can be automated with atlas ROIs; an automated CT implementation is described in Tsai et al., Critical Care 2024, DOI 10.1186/s13054-024-04895-2. Compute-today test: YES on any unseen quantitative NCCT, without an annotator, conditional on HU preservation.",
      "suspected_signal": "Cytotoxic edema increases tissue water, reducing gray-matter attenuation and normal gray-white differentiation before a mature infarct is conspicuous. Narrow brain windows amplify that low-amplitude attenuation contrast.",
      "use_vs_association": "Erase only the gray-versus-white contrast component inside affected atlas regions by shifting gray and white voxels toward their local pooled mean while preserving regional mean HU, texture residuals, perfusion maps, and all contralateral inputs; compare with equal-energy common-mode HU shifts. A selective output loss under contrast erasure distinguishes use from mere correlation.",
      "keystone_prerequisite": "The released NCCT preserves local quantitative HU contrast closely enough that automated regional GWR is stable under registration and resampling.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Native-space availability does not itself prove cross-scanner HU calibration or atlas-GWR repeatability. A Stage-0 test must require ICC at least 0.9 across two reasonable registrations and rank correlation at least 0.8 between raw and derivative GWR; failure kills the mechanistic card rather than becoming a negative result.",
      "rung_reached": "0; rung 1 after the measurement gate, selective-erasure response, common-mode sham, and held-out replication.",
      "dies_like_prior": "Closest to idea-033 (insular-ribbon preprocessing), rejected for IDENTIFIABILITY_FAILURE. This is narrower and quantitatively intervenes on gray-white contrast while preserving the regional mean and using a common-mode sham; it does not claim the insular ribbon or preprocessing itself is causal. It still cannot distinguish cytotoxic edema from any other cause of lowered GWR, so the deliverable remains cue use, not pathology identification.",
      "closest_prior_work": "The winning ISLES'24 report shows a windowing gain but does not identify the exploited attenuation quantity (arXiv:2505.18424). Automated GWR has been measured on NCCT after global hypoxic injury (Tsai et al., DOI 10.1186/s13054-024-04895-2). Automated net-water-uptake work in acute stroke predicts outcome (Front Neurol 2025, DOI 10.3389/fneur.2025.1629434) but does not perform a model-use intervention on ISLES'24. No novelty claim is made beyond this targeted comparison.",
      "existing_assets": "149 raw NCCTs, co-registered acute modalities, final masks for evaluation only, atlas software, a deterministic GWR formula, and a documented competitive preprocessing recipe.",
      "smallest_decisive_experiment": "Freeze a center-stratified 5-fold split; train one winner-style nnU-Net; on 30 untouched cases run local contrast erasure, common-mode HU shams, and dose levels 25/50/75/100%. Primary readout is paired change in predicted lesion probability inside the perfusion-deficit region, label-free. Stage 0 takes 1 day; one model and interventions take 5-7 GPU-days on one 24-GB GPU.",
      "standing_confounds_addressed": "Within-case edits fix scanner, vendor, site, protocol, positioning, habitus, prevalence, referral, and patient anatomy. Common-mode shams address generic HU sensitivity; texture preservation addresses blur. Cross-center replication tests calibration. The design does not eliminate unmeasured reconstruction effects or prove edema is the sole biological source. Labels are absent from the primary readout; leakage is controlled by untouched folds.",
      "alternative_explanations": [
        "The model responds to any intensity edit; common-mode and equal-energy shams test this.",
        "Erasure changes local texture; residual texture is explicitly restored and a Fourier-energy check gates validity.",
        "Low GWR reflects chronic small-vessel disease rather than acute edema; affected-versus-contralateral localization and acute perfusion overlap reduce but do not eliminate this."
      ],
      "anticipated_negative": "Sensitivity-limited if the trained model underperforms; decisive after a preregistered held-out Dice gate and the common-mode positive-control checks.",
      "remaining_legwork": "One day for HU/GWR stability; 1 week for training and the first held-out intervention decision; approximately 7 GPU-days and no new annotation.",
      "design_template": "representation-erasure",
      "entry_point_2_requirements": "Measurement: automated atlas GWR. Confused artifact: generic HU/window sensitivity or edit-induced texture loss; common-mode shams and texture-energy preservation separate them.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "One scalar contrast, one selective erasure, and explicit shams."
        },
        "identifiability": {
          "value": 3,
          "why": "The design isolates contrast use but not cytotoxic edema as its unique biological cause."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Gray-white loss is a clinically recognized early ischemic sign and may explain a large benchmark preprocessing gain."
        },
        "interest": {
          "value": 4,
          "why": "It converts a reported engineering gain into a physician-legible mechanism."
        },
        "prior_legwork": {
          "value": 4,
          "why": "Recipe, raw NCCT, atlas methods, and quantitative measurements exist."
        },
        "feasibility": {
          "value": 3,
          "why": "Native raw NCCT availability is inspected, but the actual HU/GWR stability keystone has not been checked."
        },
        "data_readiness": {
          "value": 4,
          "why": "Public 149-case archive; large but directly usable."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "Paired probability change and standard segmentation metrics are ready."
        },
        "negative_result_value": {
          "value": 3,
          "why": "Useful after model-performance and measurement gates, otherwise sensitivity-limited."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Closest work inspected, but no systematic novelty audit."
        },
        "regret": {
          "value": 4,
          "why": "A direct explanation for a ten-point preprocessing effect is an obvious next experiment."
        }
      },
      "priority_score": 3.6,
      "unverified_claims": [
        "GWR stability across the two centers",
        "texture-preserving erasure realism",
        "availability of a competitive checkpoint",
        "precise novelty gap"
      ],
      "plain_pitch": "A stroke makes water enter injured cells, subtly washing out the normal brightness difference between gray and white brain tissue on CT. The winning challenge system improved sharply when those faint shades were displayed differently, but nobody showed which shade difference mattered. This experiment removes only that contrast from the same scan; if the forecast weakens while equally large brightness-control edits do not, the model is using the classic early-injury sign.",
      "track": "baseline",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-005-c02",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "The old stroke inside the new forecast",
      "question": "Is the model using contralateral chronic infarct cavities as a marker of reduced brain reserve when forecasting new infarction?",
      "rung": "Target rung 1: use of remote chronic-infarct appearance; rung 2 requires replication with a separately trained model and an external acute-stroke cohort.",
      "deliverable_sentence": "The final-infarct model is using remote chronic infarct cavities as a brain-reserve signal when forecasting new infarction.",
      "X_measurement": "Within brain parenchyma outside ventricles and the acute Tmax>6 s territory, X is connected CSF-like hypodensity (0-30 HU) with a surrounding gliotic low-attenuation rim and atlas-inconsistent tissue loss; quantify volume and surface area, with contralateral lesions primary. A deterministic threshold/connected-component measurement can be run today on unseen NCCT after automated brain/ventricle segmentation, without an annotator; measurement validity is a gate rather than assumed diagnosis.",
      "suspected_signal": "Chronic infarcts leave encephalomalacic cavities and volume loss. They encode prior vascular injury and reduced reserve, which may lead a model to enlarge expected tissue loss even when the old lesion is remote from the current perfusion deficit.",
      "use_vs_association": "Within each case, fill only contralateral remote cavities with texture sampled from mirrored homologous tissue, while holding all acute CT, CTA, perfusion, and affected-hemisphere voxels fixed. A predicted-lesion change in the affected hemisphere, exceeding equal-volume normal-CSF and random-parenchyma shams, demonstrates use; cross-sectional correlation alone is supporting only.",
      "keystone_prerequisite": "A nontrivial subset of admission NCCTs contains automatically separable remote chronic infarct cavities rather than only nonspecific low attenuation.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The 0-30 HU morphology rule may confuse enlarged perivascular spaces, arachnoid cysts, surgical cavities, and severe leukoaraiosis. The first 20 cases require blinded algorithmic stability checks across thresholds; without released chronic-lesion labels, a positive use result supports use of cavity-like tissue loss, not proven prior infarction.",
      "rung_reached": "0; rung 1 after prevalence, stability, remoteness, realism, and sham gates.",
      "dies_like_prior": "Closest to isles24-scout-001-c04 (frail brain) but differs in a discrete, remotely editable lesion rather than diffuse correlated frailty. It avoids idea-020's geometry confounding by editing contralateral tissue while freezing the affected input. Annotation provenance is not load-bearing because the primary endpoint is paired model output.",
      "closest_prior_work": "Prior-infarct burden is a recognized imaging marker, while infarct pattern predicts function independent of volume (Radiology 2021, DOI 10.1148/radiol.2021203964). The ISLES'24 dataset paper includes patient history but does not report a model-use test for old cavities (DOI 10.1148/ryai.250603). No verified prior intervention study on this question was found; that is not proof of novelty.",
      "existing_assets": "Raw NCCT, registered acute maps, automatic brain/ventricle segmentation tools, mirrored tissue donor regions, and label-free paired output comparison.",
      "smallest_decisive_experiment": "Census the first 30 cases; proceed only if at least 15 have stable remote cavity volume of at least 1 mL. On those cases perform cavity fill, ventricle-adjacent CSF fill, and random-parenchyma shams. About 2 days measurement work and 20 GPU-hours once a model is frozen.",
      "standing_confounds_addressed": "Paired edits fix scanner, vendor, protocol, site, positioning, habitus, prevalence, referral, and all acute pathology. Contralateral remoteness prevents direct lesion overlap. Shams address generic filling and CSF-boundary effects. It does not prove the cavity's etiology or distinguish prior-injury reserve from a learned age proxy.",
      "alternative_explanations": [
        "The response is to any CSF boundary; ventricle and arachnoid-space shams test this.",
        "The cavity is a proxy for age, not reserve; age-stratified response is reported but cannot fully distinguish the two.",
        "Inpainting artifacts drive the response; use two independent fill methods and require concordance."
      ],
      "anticipated_negative": "Decisive only if prevalence, segmentation stability, model performance, and two-method edit realism gates pass; otherwise sensitivity-limited.",
      "remaining_legwork": "2 days to the prevalence kill decision; 4-6 days to paired results; under 20 GPU-hours; no new labels requested.",
      "design_template": "regional-removal",
      "entry_point_2_requirements": "Measurement: remote CSF-like cavity burden. Confused artifacts: ventricles/other CSF spaces and inpainting seams; anatomic shams and two fill methods address them.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "The cue and paired edit are clear, though lesion classification needs a gate."
        },
        "identifiability": {
          "value": 3,
          "why": "Remote editing identifies cavity use but not whether the model interprets it as reserve or age."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Prior injury is clinically meaningful context for tissue vulnerability and transportability."
        },
        "interest": {
          "value": 4,
          "why": "A new-lesion model consulting old damage is plausible but not routinely measured."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Segmentation ingredients exist, but no released chronic-lesion labels."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped because the prevalence and separability keystone is uninspected."
        },
        "data_readiness": {
          "value": 4,
          "why": "All images are public and no external outcomes are needed."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Paired output is direct; cavity-validity metrics are custom."
        },
        "negative_result_value": {
          "value": 3,
          "why": "Useful after stringent prevalence and realism gates."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Limited primary-source search only."
        },
        "regret": {
          "value": 3,
          "why": "Worth a cheap census before more elaborate reserve experiments."
        }
      },
      "priority_score": 3.4,
      "unverified_claims": [
        "remote chronic-cavity prevalence",
        "automatic specificity",
        "edit realism",
        "novelty"
      ],
      "plain_pitch": "An old stroke can leave a fluid-filled cavity in the brain. This study asks whether a model predicting a new stroke looks across the brain at that old damage and treats the patient as more vulnerable. Filling only the old-looking cavity in a copy of the scan, while leaving the new stroke and its blood-flow maps untouched, would reveal whether that remote history changes the forecast.",
      "track": "baseline",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-005-c03",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "The bottleneck before the brain",
      "question": "Is the model using ipsilateral cervical carotid stenosis as an upstream flow constraint beyond the measured intracranial perfusion deficit?",
      "rung": "Target rung 1: use of the stenotic lumen; rung 2 requires a flow-consistent intervention or natural paired study that also identifies upstream resistance.",
      "deliverable_sentence": "The final-infarct model is using ipsilateral cervical carotid stenosis as an upstream flow constraint beyond the measured intracranial perfusion deficit.",
      "X_measurement": "Segment the cervical ICA lumen on CTA and compute NASCET stenosis = 100*(1 - minimum residual lumen diameter/distal normal ICA diameter). Semi-automated CTA NASCET measurement is established (White et al., PMID 20724259, DOI 10.1017/S0317167100010532); CarotidNet provides fully automatic CTA segmentation for stenosis quantification (PMID 33392012, DOI 10.21037/qims-20-286). Compute-today test: YES on an unseen CTA if its field of view includes the bifurcation and distal reference.",
      "suspected_signal": "A narrowed cervical carotid increases upstream hydraulic resistance and reduces pressure reserve. At matched acute perfusion maps, a model may treat severe ipsilateral stenosis as evidence that threatened tissue has less capacity to survive or re-perfuse.",
      "use_vs_association": "Create a lumen-restored CTA counterfactual by replacing only the stenotic segment with a patient-specific centerline tube whose diameter equals the distal reference, preserving plaque exterior, distal vessels, NCCT and every CTP-derived map; compare with an equal-volume lumen edit in the contralateral carotid and a nonstenotic-segment sham. Output change demonstrates visual use, not merely cohort association.",
      "keystone_prerequisite": "Released raw CTA consistently covers the cervical carotid bifurcation and distal normal ICA needed for NASCET measurement.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Even with coverage, a synthetic open lumen paired with unchanged downstream perfusion is physiologically inconsistent. A positive response establishes use of stenosis appearance, but the 'upstream flow constraint' interpretation remains rung 1 unless a flow-consistent model or natural pre/post-treatment pair is added.",
      "rung_reached": "0; rung 1 after coverage, segmentation, realism, receptive-field, and laterality-sham gates.",
      "dies_like_prior": "Resembles idea-032 (spare routes), killed because anatomy covaried with physiology. This card makes a narrower visual-use claim with a direct lumen edit while freezing downstream physiology; it therefore identifies cue use but deliberately does not claim causal collateral flow. The physiological wording is the residual weakness and caps identifiability.",
      "closest_prior_work": "CTA NASCET measurement and automated carotid segmentation are established (DOI 10.1017/S0317167100010532; DOI 10.21037/qims-20-286). The challenge and winning papers do not test whether final-infarct models use cervical stenosis (arXiv:2408.10966; arXiv:2505.18424). No systematic novelty audit has been completed.",
      "existing_assets": "Raw CTA, acute perfusion maps, automatic vessel segmentation literature/code pathway, standard NASCET formula, and paired label-free readout.",
      "smallest_decisive_experiment": "Inspect CTA coverage in 20 cases in half a day. If at least 90% cover the required anatomy and at least 20 cases in the cohort have measurable ipsilateral stenosis above 30%, run three lumen-restoration doses and shams on those 20; 1 week and under 30 GPU-hours after model freeze.",
      "standing_confounds_addressed": "Within-case edits fix scanner, site, protocol, positioning, habitus, prevalence, referral, and distal perfusion. Contralateral and nonstenotic shams address generic bright-lumen edits. Not ruled out: plaque texture, calcification, centerline geometry, or physiologic inconsistency may drive response. Reconstruction and bolus timing can affect segmentation and are audited, not eliminated.",
      "alternative_explanations": [
        "The model reads plaque/calcification rather than narrowing; preserve the plaque exterior and vary only lumen diameter.",
        "Any vessel edit changes output; contralateral and nonstenotic shams test this.",
        "The inconsistent CTA-perfusion pair is detected as out of distribution; feature-distance and a natural low-stenosis reference bank provide only partial protection."
      ],
      "anticipated_negative": "Uninterpretable if the receptive field excludes the neck or severe stenosis is rare; after those gates, sensitivity-limited because realistic lumen counterfactuals remain difficult.",
      "cross_domain": {
        "borrowed_construct": "Hydraulic resistance in a supply pipe upstream of a network.",
        "measurement_it_implies": "NASCET diameter loss and a graded virtual lumen-restoration response.",
        "what_changes_if_dropped": "The experiment still tests use of a stenosis image sign, but no longer supports language about upstream flow reserve."
      },
      "remaining_legwork": "Half a day for coverage, 2 days for stenosis census, and about 1 week for edits; under 30 GPU-hours; no new annotations.",
      "design_template": "counterfactual-synthesis",
      "entry_point_2_requirements": "Measurement: automated NASCET percent stenosis. Confused artifacts: plaque calcification and CTA bolus/reconstruction; lumen-only editing and shams address but do not fully remove them.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "A standard measurement and graded intervention, with a clear residual interpretive limit."
        },
        "identifiability": {
          "value": 2,
          "why": "Visual cue use is testable, but physiologic inconsistency leaves multiple explanations."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Upstream stenosis affects reserve and treatment context."
        },
        "interest": {
          "value": 4,
          "why": "It asks whether a brain model reads a bottleneck outside the brain."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Measurement and segmentation exist; field of view and model coverage do not."
        },
        "feasibility": {
          "value": 2,
          "why": "Coverage, prevalence, and realistic editing are unverified."
        },
        "data_readiness": {
          "value": 3,
          "why": "CTA is public, but anatomical coverage is unknown."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Paired output is ready; realism gates are bespoke."
        },
        "negative_result_value": {
          "value": 2,
          "why": "A null remains sensitivity-limited even after gates."
        },
        "novelty_confidence": {
          "value": 2,
          "why": "Only a targeted search was performed and keystone is uninspected."
        },
        "regret": {
          "value": 3,
          "why": "A cheap coverage census determines whether the memorable question is viable."
        }
      },
      "priority_score": 2.85,
      "unverified_claims": [
        "cervical CTA coverage",
        "stenosis prevalence",
        "CarotidNet portability",
        "counterfactual realism",
        "novelty"
      ],
      "plain_pitch": "A severe narrowing in the neck artery is a bottleneck before blood ever reaches the injured brain. The perfusion maps show what is happening downstream, but the model may also inspect that upstream bottleneck and assume the tissue has less room for recovery. Virtually reopening only the narrowed lumen while leaving the measured brain perfusion unchanged tests whether the visible bottleneck itself changes the forecast, though it cannot by itself prove the model understands blood-flow physics.",
      "track": "baseline",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-005-c04",
      "parent_ids": [],
      "search_mode": "C",
      "entry_point": 2,
      "title": "The pressure history written in a winding artery",
      "question": "Is the model using intracranial arterial tortuosity as a vascular-age and long-term pressure-load gauge?",
      "rung": "Mode C target rung 1: use of tortuosity; rung 3 requires external validation that the representation tracks age/pressure load rather than ancestry, anatomy, or disease subtype.",
      "deliverable_sentence": "The final-infarct model is using intracranial arterial tortuosity as a vascular-age and long-term pressure-load gauge.",
      "X_measurement": "From CTA vessel centerlines, compute tortuosity index TI = 100*(centerline length/chord length - 1) for bilateral MCA and basilar arteries, then average. This exact formula is reported in Kim et al., Investig Magn Reson Imaging 2018, DOI 10.13104/imri.2018.22.3.150, and is computable today from an unseen CTA using an automatic vessel mask and skeletonization, without annotation.",
      "suspected_signal": "Years of pulsatile pressure and arterial-wall remodeling lengthen and curve large arteries. Primary CTA studies associate carotid or intracranial tortuosity with age and hypertension, although effects vary by population (DOI 10.3389/fneur.2024.1307984; DOI 10.13104/imri.2018.22.3.150). A model could use this stable geometry as a vascular-age shortcut when estimating tissue resilience.",
      "use_vs_association": "Primary evidence would be a conditional-observational test: within narrow strata of age, site, occlusion location, perfusion-deficit volume, HIR, and Circle-of-Willis topology, test whether case-level tortuosity explains prediction residuals but not ground-truth residuals. This can falsify the simplest shortcut account but cannot prove use; a later geometry-preserving counterfactual is required for rung 1.",
      "keystone_prerequisite": "Automated centerlines in the released CTA recover MCA and basilar paths with sufficient continuity and tortuosity variation across 149 cases.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Even perfect centerlines leave tortuosity entangled with age, hypertension, ancestry, and vessel elongation. The proposed conditional test is discovery, not a use demonstration; this is why identifiability is low and the card is Mode C.",
      "rung_reached": "0; rung 1 only after a credible selective tortuosity intervention or natural paired validation, not merely a significant regression coefficient.",
      "dies_like_prior": "Closest to isles24-scout-004-c05 (calcification age gauge) and idea-032 (vascular anatomy). It differs in a continuous mechanical-history quantity rather than calcium or collateral connectivity, but it has not yet escaped their proxy-identifiability problem; the card labels that limitation rather than claiming a solved mechanism.",
      "closest_prior_work": "Intracranial tortuosity measurement and population-specific associations with age/hypertension are reported in DOI 10.13104/imri.2018.22.3.150; carotid tortuosity associations are reported in DOI 10.3389/fneur.2024.1307984. Neither paper audits a final-infarct network. Novelty is not established.",
      "existing_assets": "CTA, automatic Circle-of-Willis masks, standard centerline arithmetic, demographics and hypertension history, perfusion maps, and final masks.",
      "smallest_decisive_experiment": "Run automatic vessel extraction on 30 cases; continue only if at least 80% yield continuous bilateral MCA and basilar centerlines and test-retest TI ICC is at least 0.9. Then conduct a preregistered nested cross-validated residual analysis on all 149 cases. Two to four days, under 10 GPU-hours.",
      "standing_confounds_addressed": "Matching/adjustment addresses measured age, hypertension, site, occlusion, perfusion severity, and topology. Scanner, reconstruction, and bolus affect segmentation and require sensitivity analysis. Ancestry is not released and cannot be ruled out. Label leakage is avoided through out-of-fold predictions. The design does not yet distinguish use from association, explicitly preventing rung advancement.",
      "alternative_explanations": [
        "Tortuosity is only an age or ancestry proxy; measured age can be adjusted, ancestry cannot.",
        "Segmentation quality varies with CTA bolus; centerline continuity and intensity sensitivity analyses test this.",
        "Tortuous vessels covary with collateral anatomy; topology-stratified analysis reduces but does not remove it."
      ],
      "anticipated_negative": "Sensitivity-limited: a null could reflect small n, noisy centerlines, or a genuinely unused cue; useful mainly as a cheap kill before intervention development.",
      "cross_domain": {
        "borrowed_construct": "Cumulative mechanical load recorded as permanent curvature in a repeatedly pressurized pipe.",
        "measurement_it_implies": "Centerline excess length over chord length, tested against age and hypertension history.",
        "what_changes_if_dropped": "The study becomes a generic vessel-shape association and loses both its proposed mechanism and most of its interest."
      },
      "remaining_legwork": "1 day centerline gate and 2-3 days conditional analysis; a convincing intervention would require an additional 2-3 weeks and may fail.",
      "design_template": "conditional-observational",
      "entry_point_2_requirements": "Measurement: centerline tortuosity index. Confused artifacts: CTA bolus/segmentation quality and collateral topology; quality gates and stratification address them incompletely.",
      "scores": {
        "mechanism_clarity": {
          "value": 5,
          "why": "Named arterial-wall remodeling mechanism and exact geometric quantity."
        },
        "identifiability": {
          "value": 3,
          "why": "Conditional analysis removes major measured alternatives but cannot establish use or remove ancestry."
        },
        "interest": {
          "value": 4,
          "why": "A model reading lifetime pressure history from vessel shape is unexpected and testable."
        },
        "medical_relevance": {
          "value": 3,
          "why": "Vascular age is plausible context but the immediate clinical consequence is indirect."
        },
        "clarity": {
          "value": 4,
          "why": "The discovery test is precise and its inability to reach rung 1 is explicit."
        },
        "prior_legwork": {
          "value": 3,
          "why": "Measurement literature and masks exist, but intervention work does not."
        },
        "feasibility": {
          "value": 3,
          "why": "Reported outside Mode C score and capped because centerline recovery is uninspected."
        },
        "data_readiness": {
          "value": 4,
          "why": "CTA and covariates are public."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "Residual analysis is standard; use-test evaluation is absent."
        },
        "negative_result_value": {
          "value": 2,
          "why": "A null is sensitivity-limited but can kill the expensive next step."
        },
        "novelty_confidence": {
          "value": 2,
          "why": "Targeted search only; no novelty claim."
        },
        "regret": {
          "value": 3,
          "why": "Cheap enough to screen despite the proxy problem."
        }
      },
      "mode_c_priority_score": 3.9,
      "unverified_claims": [
        "centerline continuity",
        "tortuosity variance",
        "adequate conditional overlap",
        "availability of ancestry control",
        "novelty"
      ],
      "plain_pitch": "Arteries can grow longer and more winding after years of aging and high blood pressure, much as a repeatedly stressed hose changes shape. This speculative screen asks whether a stroke model reads that winding geometry as a summary of the patient's vascular history. A statistical link after matching similar strokes would justify building a harder intervention, but it would not yet prove that the model actually uses the shape.",
      "track": "baseline",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-005-c05",
      "parent_ids": [],
      "search_mode": "C",
      "entry_point": 2,
      "title": "Do sulci pin the predicted infarct edge?",
      "question": "Is the model using local sulcal depth and cortical curvature as a geometric scaffold for where infarct boundaries stop?",
      "rung": "Mode C target rung 1: prediction boundaries depend on cortical folding after local tissue evidence is controlled; rung 2 requires replication across model families and an external cohort.",
      "deliverable_sentence": "The final-infarct model is using local sulcal depth and cortical curvature as a geometric scaffold for predicted infarct boundaries.",
      "X_measurement": "Reconstruct the pial/gray-white surfaces from NCCT with atlas-constrained automated tissue segmentation; X is signed mean curvature and geodesic sulcal depth at each cortical vertex, with boundary alignment measured by excess predicted-boundary density within 2 mm of curvature extrema. These are deterministic differential-geometric quantities computable on an unseen scan without human input if surface reconstruction passes stability gates.",
      "suspected_signal": "Cortical folds organize gray/white interfaces, pial vessels, partial-volume edges, and convolutional image gradients. A network may use curvature ridges as learned stopping boundaries even when true tissue fate crosses them; the proposed physical analogue is interface pinning at a pre-existing geometric ridge, not a claim that sulci biologically halt ischemia.",
      "use_vs_association": "Use a held-out-structure prediction test: match boundary and non-boundary cortical vertices within case on Tmax, CBF, CBV, MTT, NCCT HU, tissue class, arterial territory, and distance to occlusion; ask whether curvature still predicts model boundary but not ground-truth boundary. Then locally erase curvature information in intermediate representations with a cross-validated linear concept direction while preserving perfusion features; selective boundary displacement is the use test. Observational alignment alone does not count.",
      "keystone_prerequisite": "Atlas-constrained cortical surfaces and curvature estimates are stable on acute NCCT at the released resolution, including near ischemic cortex.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Even stable curvature covaries with tissue interfaces, vascular territories, and partial volume. Linear representation erasure may remove correlated anatomy rather than curvature alone; the strongest possible conclusion is model dependence on a curvature-associated representation, not a biological barrier.",
      "rung_reached": "0; rung 1 only after surface stability, overlap, ground-truth-negative-control, erasure selectivity, and sham-direction gates.",
      "dies_like_prior": "Most resembles idea-020 (spreading front), killed because geometry and perfusion gradients co-varied. This design matches local perfusion and asks for model-boundary enrichment absent from ground truth, then erases a representation direction. That is a real difference, but selective erasure may still remove co-encoded anatomy, so identifiability remains deliberately low.",
      "closest_prior_work": "Infarct pattern and cortical/deep structure carry prognostic information independent of volume (Radiology 2021, DOI 10.1148/radiol.2021203964), but that does not test sulcal curvature use. Concept erasure methods exist generally, yet no primary work was verified that applies curvature erasure to ISLES'24. Novelty remains unaudited.",
      "existing_assets": "NCCT, co-registered perfusion maps, atlas surface templates, model feature maps, final masks as a negative-control boundary, and standard curvature formulas.",
      "smallest_decisive_experiment": "On 20 cases, reconstruct surfaces twice with perturbed registration; kill unless curvature ICC exceeds 0.85 and at least 10,000 matched cortical vertices retain overlap. Fit the matched boundary model on held-out cases; attempt representation erasure only if model-boundary enrichment is present and ground-truth enrichment is absent. Three days for the screen, about 2 weeks for erasure, under 40 GPU-hours.",
      "standing_confounds_addressed": "Within-case matching addresses site, scanner, protocol, position, habitus, prevalence, referral, local perfusion, HU, tissue class, territory, and occlusion distance. Ground-truth boundaries distinguish network convention from biological anatomy. Reconstruction and partial-volume artifacts remain serious. Out-of-fold features prevent label leakage; no new annotations are required.",
      "alternative_explanations": [
        "Curvature only marks gray-white or CSF interfaces; match tissue class and intensity gradient, then report residual dependence.",
        "Vascular territories follow folds; match territory and use ground-truth-boundary behavior as control.",
        "Erasure removes generic spatial position; random and coordinate-direction shams test selectivity but cannot prove perfect isolation."
      ],
      "anticipated_negative": "Sensitivity-limited if surfaces or concept directions are noisy; after all gates, a null is useful evidence against a seductive architectural-boundary story for this model.",
      "cross_domain": {
        "borrowed_construct": "Interface pinning from materials physics, where a moving boundary catches on a pre-existing geometric ridge.",
        "measurement_it_implies": "Excess prediction-boundary density at curvature extrema and displacement after curvature-direction erasure.",
        "what_changes_if_dropped": "The measurement remains valid, but the claim shrinks to generic anatomical edge following and loses the proposed mechanism."
      },
      "remaining_legwork": "3 days to the surface/association kill decision; about 2 further weeks for representation erasure; under 40 GPU-hours and no annotation.",
      "design_template": "other:geometry-conditioned-boundary-test",
      "design_template_justification": "The grammar combines within-case matched held-out-structure prediction with representation erasure; no listed single template captures the required ground-truth-negative-control boundary comparison.",
      "entry_point_2_requirements": "Measurement: cortical mean curvature, sulcal depth, and excess boundary density. Confused artifact: tissue-interface partial volume and vascular-territory geometry; matching and ground-truth-boundary controls address them incompletely.",
      "scores": {
        "mechanism_clarity": {
          "value": 4,
          "why": "A named geometric ridge and explicit boundary measurement, though the biological relevance is intentionally not asserted."
        },
        "identifiability": {
          "value": 2,
          "why": "Curvature is tightly co-encoded with anatomy and representation erasure may not isolate it."
        },
        "interest": {
          "value": 5,
          "why": "The obviously-wrong possibility of folds pinning model boundaries would expose a memorable architectural prior."
        },
        "medical_relevance": {
          "value": 3,
          "why": "Boundary validity matters, but the construct is primarily about model behavior rather than treatment."
        },
        "clarity": {
          "value": 4,
          "why": "The staged falsification criteria and prohibited conclusion are explicit."
        },
        "prior_legwork": {
          "value": 2,
          "why": "Geometry tools exist, but NCCT surface stability and the erasure bridge are unproven."
        },
        "feasibility": {
          "value": 2,
          "why": "Reported outside Mode C score; two major gates may fail."
        },
        "data_readiness": {
          "value": 4,
          "why": "All required images and masks are public."
        },
        "evaluation_readiness": {
          "value": 2,
          "why": "Metrics are custom and require careful matching diagnostics."
        },
        "negative_result_value": {
          "value": 2,
          "why": "Mostly sensitivity-limited, though it can kill an attractive story."
        },
        "novelty_confidence": {
          "value": 2,
          "why": "No systematic audit and keystone uninspected."
        },
        "regret": {
          "value": 3,
          "why": "The cheap association screen is worthwhile before dismissing the idea."
        }
      },
      "mode_c_priority_score": 3.55,
      "unverified_claims": [
        "NCCT surface stability",
        "matched-support size",
        "curvature enrichment",
        "selective erasure validity",
        "novelty"
      ],
      "plain_pitch": "The brain's surface is deeply folded into ridges and grooves. This intentionally speculative idea asks whether a segmentation model treats those folds like convenient fence lines when drawing the predicted edge of a stroke, even when the actual later injury does not. If matched regions with the same blood-flow injury show model boundaries collecting at folds—and removing the model's fold representation moves those boundaries—the model is using cortical geometry as a scaffold.",
      "track": "baseline",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-005-c06",
      "parent_ids": [],
      "track": "wide",
      "entry_point": 2,
      "title": "Does the model trust tissue that obeys the flow equation?",
      "question": "Is an ISLES'24 final-infarct model using voxelwise violation of the central-volume identity CBV = CBF x MTT as a hidden confidence map for the released perfusion estimates?",
      "rung": "Target rung 1: selective use of the cross-map inconsistency residual; rung 2 requires the response to replicate across model families and across independently regenerated perfusion maps.",
      "deliverable_sentence": "The final-infarct model is using violation of the central-volume identity as a hidden confidence map for perfusion evidence.",
      "X_measurement": "Inside brain tissue, fit the unit/scale constant on normal contralateral voxels and compute X = |log(CBV) - log(CBF) - log(MTT/60) - k_case|, with cerebral blood volume (CBV) in mL/100 g, cerebral blood flow (CBF) in mL/100 g/min, and mean transit time (MTT) in seconds. Report median X and connected high-X islands inside the acute Tmax>6 s territory. The formula is deterministic and annotator-free; the central-volume theorem is described in Konstas et al., AJNR 2009, PMID 19270105, and the three registered maps are in the official ISLES'24 release (Zenodo DOI 10.5281/zenodo.16731717).",
      "suspected_signal": "For an ideal indicator-dilution calculation the three maps are not independent: CBV equals CBF multiplied by MTT after unit conversion. Noise, delay sensitivity, regularization, map clipping, and implementation details can break that identity locally. A multichannel model could learn that high-residual tissue is an unreliable measurement region and discount or reinterpret its perfusion deficit, even though no explicit uncertainty map was supplied.",
      "use_vs_association": "Project each affected-region map triplet onto the nearest central-volume-consistent manifold while preserving the local CBF and Tmax ranks, then compare the prediction with equal-energy perturbations tangent to that manifold; a selective, graded response to removing only the normal residual is evidence of use rather than correlation.",
      "keystone_prerequisite": "The released CBF, CBV, and MTT maps have meaningful common support and scaling such that a stable, nontrivial central-volume residual can be computed rather than merely rediscovering zeros, support edges, or arbitrary normalization.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The theorem is verified, and all three maps are verified as released, but the release's value units, clipping rules, and local algebraic consistency have not been inspected. Stage 0 must read headers and value distributions in 10 cases, exclude zero/support boundaries, and require residual rank correlation at least 0.8 under two defensible normal-tissue masks. If X collapses to a constant, a support mask, or a unit error, the candidate dies.",
      "rung_reached": "0; rung 1 only after measurement, manifold-projection realism, model-performance, dose-response, and tangent-sham gates.",
      "dies_like_prior": "This is adjacent to isles24-scout-001-c08 (the deconvolution algorithm may have signed the image) and idea-037 (site identity), both vulnerable to IDENTIFIABILITY_FAILURE. It differs by naming an invariant that is calculable within every case and selectively removable without swapping sites or algorithms. A positive result would establish use of cross-map inconsistency, not which vendor produced it or why it arose; that narrower claim avoids the unsupported provenance attribution.",
      "closest_prior_work": "Indicator-dilution theory fixes the algebraic relation among CBF, CBV, and MTT; commercial packages applied to identical stroke source data nevertheless produce materially different maps. Infarct networks fuse these maps, but the searched primary work does not test whether a network reads their internal physical inconsistency as uncertainty. No novelty claim beyond this targeted comparison is made.",
      "novelty_neighbors": [
        {
          "work": "Konstas et al., Theoretic Basis and Technical Implementations of CT Perfusion in Acute Ischemic Stroke, Part 1",
          "identifier": "PMID 19270105; AJNR 2009; official full text https://pmc.ncbi.nlm.nih.gov/articles/PMC7051780/",
          "relation": "Defines the central-volume theorem and explains that MTT is calculated from CBV/CBF; supplies the physical invariant but does not audit model use of its residual."
        },
        {
          "work": "Kudo et al., Differences in CT Perfusion Maps Generated by Different Commercial Software",
          "identifier": "DOI 10.1148/radiol.254082000; PMID 20032153",
          "relation": "Shows that identical acute-stroke source data produce significantly different maps across software, motivating a hidden map-quality cue; it does not study learned final-infarct models or the within-triplet residual."
        },
        {
          "work": "Liu et al., ISP-Net: Fusing features to predict ischemic stroke infarct core on CT perfusion maps",
          "identifier": "DOI 10.1016/j.cmpb.2022.106630",
          "relation": "A primary example of a network fusing native perfusion, CBF, CBV, MTT, and Tmax; it reports prediction performance, not a conservation-law intervention."
        }
      ],
      "novelty_delta": "The proposed experiment is the first located test that removes only the voxelwise violation of a known perfusion identity and asks whether a final-infarct model changes its forecast while physiology-preserving tangent shams do not.",
      "why_not_done": "BLIND_SPOT: perfusion papers treat disagreement as a software-validation problem and model papers treat registered maps as independent input channels, leaving the algebraic residual between those channels uninterrogated as a learned uncertainty signal.",
      "existing_assets": "Official registered CBF, CBV, MTT, and Tmax maps for 149 public training cases; raw CTP for later regeneration; final masks; official metrics; standard projection and paired-output arithmetic; a winner-style surrogate can be trained if no checkpoint is obtainable.",
      "smallest_decisive_experiment": "Stage 0 on 10 cases computes support, units, X stability, and whether X contains more than border/zero artifacts. Freeze a center-stratified split and one compact 2D multichannel U-Net; require held-out median Dice at least 0.20 and lesion-wise F1 above a frozen all-zero baseline. On 20 untouched cases run 25/50/75/100% residual removal, tangent shams matched in per-channel L2 energy, and a support-edge sham. Primary readout: paired change in predicted lesion probability within Tmax>6 s tissue, with monotone residual-dose response and residual-over-sham contrast. Compute envelope: one Colab GPU session, at most 10 GPU-hours, using 2D patches and the public registered maps; no new annotation.",
      "standing_confounds_addressed": "Within-case projections hold center, scanner, protocol, positioning, anatomy, treatment, and lesion prevalence fixed. Excluding zeros and eroding support edges prevents X from becoming a coverage mask. Tangent shams test generic sensitivity to map edits; fixed CBF/Tmax ranks protect the main perfusion ordering; two projection metrics test dependence on the chosen geometry. The experiment still cannot identify the source of inconsistency or prove calibrated uncertainty, so those conclusions are prohibited.",
      "alternative_explanations": [
        "The model responds to any violation-correction edit; equal-energy tangent shams and a monotone residual-specific contrast test this.",
        "X is only a map-support or clipping detector; eroded common support, clipped-voxel exclusion, and a support-edge sham test this.",
        "Projection moves cases off the training distribution; nearest-neighbor feature distance and two small-dose arms gate the confirmatory result but cannot prove perfect realism."
      ],
      "anticipated_negative": "Decisive if X is stable, the model passes its frozen performance gate, the small-dose edits remain in distribution, and shams produce detectable generic sensitivity; otherwise the null is sensitivity-limited.",
      "cross_domain": {
        "borrowed_construct": "Conservation-law residuals from process control: redundant sensors linked by a physical balance equation provide a residual that detects unreliable measurements without an external fault label.",
        "measurement_it_implies": "The absolute log residual of CBV = CBF x MTT and a projection that removes that residual while retaining the physiological coordinates along the constraint manifold.",
        "what_changes_if_dropped": "Without the process-control construct this becomes generic channel ablation, which cannot distinguish use of perfusion physiology from use of cross-map inconsistency."
      },
      "remaining_legwork": "Half a day for the 10-case algebra/support kill gate; one Colab session for the surrogate and 20-case intervention; a later raw-CTP regeneration study is outside this card.",
      "design_template": "counterfactual-synthesis",
      "entry_point_2_requirements": "Measurement: central-volume residual X. Confused artifacts: common-support edges, zeros, clipping, and generic multichannel perturbation; erosion, clipped-voxel exclusion, tangent shams, and dose response separate them.",
      "scores": {
        "clarity": {
          "value": 5,
          "why": "One physical identity, one residual, and a selective projection with explicit shams."
        },
        "identifiability": {
          "value": 4,
          "why": "The intervention isolates residual use, although it cannot identify the residual's technical cause or prove uncertainty calibration."
        },
        "medical_relevance": {
          "value": 4,
          "why": "A model silently discounting physically inconsistent perfusion could determine where it trusts the acute scan and how it transports across software."
        },
        "interest": {
          "value": 5,
          "why": "A stroke model acting as its own physics-based quality controller is surprising and directly actionable."
        },
        "prior_legwork": {
          "value": 4,
          "why": "The invariant, map inputs, software-variability evidence, and model family all exist."
        },
        "feasibility": {
          "value": 3,
          "why": "Capped because the released maps' units and residual stability have not been inspected."
        },
        "data_readiness": {
          "value": 4,
          "why": "All maps and outcomes are public and registered, with a modest download path."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "Paired probability response, dose response, shams, and official segmentation metrics are ready."
        },
        "negative_result_value": {
          "value": 4,
          "why": "After the algebra and model gates, a selective null rules out this specific hidden-confidence mechanism."
        },
        "novelty_confidence": {
          "value": 3,
          "why": "Three close primary neighbors were searched, but no systematic review was performed and the keystone remains uninspected."
        },
        "regret": {
          "value": 5,
          "why": "The required redundant maps are already in the benchmark, making this a cheap obvious-in-hindsight audit."
        }
      },
      "priority_score": 3.95,
      "unverified_claims": [
        "the released map units permit a stable central-volume residual",
        "the residual is not dominated by support or clipping",
        "a compact surrogate reaches the frozen performance gate in one session",
        "manifold projections remain in distribution",
        "the precise novelty gap beyond the targeted search"
      ],
      "plain_pitch": "Blood flow, blood volume, and transit time are tied by a simple physical equation, yet stroke software can produce maps that locally disagree with it. This study asks whether the prediction model notices those disagreements and quietly treats them as a warning that a region's blood-flow estimate is unreliable. If correcting only the disagreement changes the forecast while equally sized, physics-preserving edits do not, the model is using an accidental quality-control signal that could fail when the hospital changes software.",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-005-c07",
      "parent_ids": [],
      "track": "wide",
      "entry_point": 2,
      "title": "The roughness of a heartbeat through starved tissue",
      "question": "Is a raw-CT-perfusion final-infarct model using the temporal fractal dimension of each voxel's contrast curve as a deconvolution-free tissue-flow signal?",
      "rung": "Target rung 1: selective model use of Higuchi temporal fractal dimension; rung 2 requires replication in a second raw-time-series architecture and on a non-ISLES cohort.",
      "deliverable_sentence": "The final-infarct model is using temporal fractal dimension of the raw contrast curve as a tissue-flow signal.",
      "X_measurement": "For each brain voxel's baseline-subtracted raw four-dimensional CT-perfusion attenuation series, compute Higuchi fractal dimension using the frame-count-adapted kmax procedure of Lim et al. The measurement is deterministic, voxelwise, annotator-free, and has already been run on all 149 public ISLES'24 perfusion studies (PMID 40824507).",
      "suspected_signal": "A bolus curve is not only a peak and delay; its multiscale temporal roughness reflects how contrast concentration changes across sampling intervals. Lim et al. found that this fractal dimension tracks simulated flow and separates normal, penumbral, and core tissue on ISLES'24. A raw-time-series network may exploit that compact, deconvolution-free descriptor even when its architecture never names it.",
      "use_vs_association": "At each affected voxel, replace only the component of the time curve that predicts Higuchi fractal dimension using a cross-validated concept direction in the model's temporal encoder, while preserving curve area, peak time, peak height, first two moments, and spatial anatomy; compare with random orthogonal directions and with explicit X-preserving temporal jitter. Selective output loss under X erasure is the use test.",
      "keystone_prerequisite": "Higuchi temporal fractal dimension is computable and nondegenerate on the released raw ISLES'24 time series, and differs across relevant tissue states.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "Lim et al., 'Time series-derived fractal dimension of CT perfusion in acute ischemic stroke: a promising marker for hypoperfused tissue quantification,' PMID 40824507, inspected via the PubMed primary abstract on 2026-08-18: 'Fractal analysis was applied to voxel-wise time-series data from both simulated phantom datasets and 149 CTP images from the publicly available ... ISLES 2024 dataset'; FD differed across core, penumbra, and normal tissue (p<0.001), achieved penumbra-versus-normal AUC 0.732, and correlated with true CBF at rho>0.9 in the phantom after kmax optimization.",
      "keystone_residual_assumption": "The paper establishes measurement feasibility and association on the exact images, not that any final-infarct model uses X. Fractal dimension may mostly encode ordinary CBF, noise, or temporal sampling. Moment preservation, CBF-stratified analysis, and noise/sampling shams are therefore necessary, and even a positive result supports use of the descriptor rather than a unique microvascular mechanism.",
      "rung_reached": "0; rung 1 after raw-model performance, concept decodability, selectivity, CBF-matched, sampling, and noise gates.",
      "dies_like_prior": "This could die like idea-024 (capillary traffic jam; DATA_ACCESS) or idea-020 (IDENTIFIABILITY_FAILURE). The exact raw data and exact measurement have now been demonstrated on all 149 ISLES'24 cases, changing the access premise. Unlike a biological capillary-state claim, this card asks only whether a named mathematical descriptor is used and requires erasure beyond curve moments and CBF; it does not call the descriptor capillary transit heterogeneity.",
      "closest_prior_work": "One 2025 paper computes this exact feature on ISLES'24 and shows tissue discrimination; raw-CTP deep-learning papers show that temporal encoders learn features related to but not exhausted by standard maps. None of the located primary works selectively erases fractal dimension from a final-infarct model.",
      "novelty_neighbors": [
        {
          "work": "Lim et al., Time series-derived fractal dimension of CT perfusion in acute ischemic stroke",
          "identifier": "PMID 40824507",
          "relation": "Exact X on the exact 149-case dataset; establishes association and measurement feasibility but contains no trained-model use test."
        },
        {
          "work": "Robben et al., Predicting the tissue outcome of acute ischemic stroke from acute 4D CT perfusion imaging using temporal features and deep learning",
          "identifier": "DOI 10.3389/fnins.2022.1009654; PMCID PMC9672821",
          "relation": "Compares raw concentration-time and residue-curve networks and inspects correlations between learned features and conventional maps, but does not measure or erase Higuchi fractal dimension."
        },
        {
          "work": "van Os et al., Integrating regional perfusion CT information to improve prediction of infarction after stroke",
          "identifier": "PMID 32501132; PMCID PMC7922756",
          "relation": "Shows that local spatial context improves tissue-outcome prediction beyond single-voxel perfusion values; it uses conventional maps rather than temporal fractal structure or a model-use intervention."
        }
      ],
      "novelty_delta": "The exact ISLES'24 fractal biomarker has been validated as an association, but the proposed study asks the missing causal model-behavior question: does selective removal of that descriptor from a raw temporal encoder move final-infarct predictions beyond matched flow and curve moments?",
      "why_not_done": "NEW_CAPABILITY: the public release of all 149 raw four-dimensional ISLES'24 scans with registered follow-up infarct masks, followed by the 2025 exact-dataset fractal measurement, makes a reproducible use test newly practical.",
      "existing_assets": "Approximately 99 GB official archive with raw CTP and registered final masks; a published exact-dataset Higuchi recipe; raw-time-series model designs from DOI 10.3389/fnins.2022.1009654; standard concept-direction and paired-output controls.",
      "smallest_decisive_experiment": "Use a 30-case subset cached slice-wise. Train a shallow causal 2D+time U-Net on center-stratified patches, with 20 training, 5 validation, and 5 untouched cases; require validation AUC at least 0.70 within Tmax>6 s tissue and prediction volume above zero in at least 4/5 test cases. Decode X from the frozen temporal features, erase its cross-validated linear direction at four doses, and compare 20 random orthogonal directions plus X-preserving jitter. Primary readout: paired probability change in held-out perfusion-deficit voxels matched in CBF deciles and curve area. Compute envelope: one Colab GPU session, at most 12 GPU-hours and 25 GB staged data; no new annotation.",
      "standing_confounds_addressed": "Patient-level splitting prevents voxel leakage. CBF-decile and curve-moment matching test whether X merely renames flow or bolus magnitude. Frame-drop and synthetic-noise arms test temporal sampling and noise sensitivity; random directions test nonspecific feature deletion. The small model is a mechanistic probe, not a competitive benchmark claim. Linear erasure may remove correlated temporal features, so the conclusion remains dependence on an X-associated representation.",
      "alternative_explanations": [
        "X is a nonlinear re-encoding of CBF; primary matching and residualized X test incremental use but cannot prove complete independence.",
        "X tracks scanner noise or frame count; noise-injection and frame-drop shams test this and may reveal a technical rather than physiological use mechanism.",
        "Any encoder-direction deletion harms output; orthogonal directions matched for activation variance provide the selectivity comparison."
      ],
      "anticipated_negative": "Decisive for this architecture only if X is decodable, the model passes the frozen AUC/coverage gates, and positive-control directions alter output; otherwise it is sensitivity-limited.",
      "cross_domain": {
        "borrowed_construct": "Fractal time-series analysis from nonlinear dynamics, where scale-dependent path roughness summarizes structure that is not captured by a single amplitude or period.",
        "measurement_it_implies": "Voxelwise Higuchi fractal dimension over the contrast-time curve, plus selective erasure of its representation after controlling conventional curve moments.",
        "what_changes_if_dropped": "The experiment becomes an unconstrained temporal-feature probe; the exact, falsifiable X and the primary paper on the same dataset disappear."
      },
      "remaining_legwork": "One day to reproduce X on five downloaded scans; one session for the small raw-time model and erasure; full-cohort or second-family replication would be a successor.",
      "design_template": "representation-erasure",
      "entry_point_2_requirements": "Measurement: Higuchi temporal fractal dimension. Confused artifacts: CBF, curve area, temporal sampling, and noise; CBF/moment matching plus frame/noise shams address them.",
      "scores": {
        "clarity": {
          "value": 4,
          "why": "The feature and erasure are explicit, though linear concept isolation remains imperfect."
        },
        "identifiability": {
          "value": 3,
          "why": "Controls separate several ordinary curve statistics, but X remains correlated with flow and noise."
        },
        "medical_relevance": {
          "value": 3,
          "why": "A deconvolution-free signal could improve robustness, but this small probe does not establish clinical superiority."
        },
        "interest": {
          "value": 5,
          "why": "A network reading the fractal roughness of a contrast heartbeat is mechanistically surprising and grounded in an exact-dataset result."
        },
        "prior_legwork": {
          "value": 5,
          "why": "The exact feature has already been computed on all 149 cases and raw temporal architectures exist."
        },
        "feasibility": {
          "value": 4,
          "why": "The X keystone is inspected true and the decisive probe uses a staged 30-case subset in one session."
        },
        "data_readiness": {
          "value": 4,
          "why": "Public and exact, but the archive is large and requires staged download."
        },
        "evaluation_readiness": {
          "value": 3,
          "why": "AUC, paired deltas, and erasure shams are ready; representation selectivity is custom."
        },
        "negative_result_value": {
          "value": 3,
          "why": "A gated null rules out the mechanism for one temporal architecture, not raw-CTP models generally."
        },
        "novelty_confidence": {
          "value": 4,
          "why": "The exact X paper and two closest model families were inspected; none contains a use intervention, and the keystone is true."
        },
        "regret": {
          "value": 4,
          "why": "The biomarker paper has already completed the expensive measurement legwork, leaving one experiment to convert association into a model-behavior result."
        }
      },
      "priority_score": 3.8,
      "unverified_claims": [
        "the published Higuchi procedure reproduces from available methodological detail",
        "a small raw-time model passes the frozen performance gate",
        "fractal dimension is linearly decodable from its temporal encoder",
        "erasure can preserve the listed curve properties",
        "novelty outside the targeted neighbors"
      ],
      "plain_pitch": "A contrast bolus passing through brain tissue leaves a short brightness trace over time. A recent study on these exact public scans found that the trace's multiscale roughness—a mathematical quantity called fractal dimension—separates healthy, threatened, and later-infarcted tissue. This experiment asks whether a prediction model actually uses that roughness; if selectively erasing its internal representation changes forecasts after ordinary blood flow, curve size, and scanner noise are controlled, it does.",
      "charter": "isles24"
    },
    {
      "id": "isles24-scout-005-c08",
      "parent_ids": [],
      "track": "wide",
      "entry_point": 2,
      "title": "Delay is not dispersion",
      "question": "Is a raw-CT-perfusion final-infarct model using bolus dispersion—the width and skew of contrast passage after arrival-time alignment—as a collateral-route signal distinct from simple delay?",
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
      "plain_pitch": "Contrast can reach threatened brain late, but it can also arrive spread out after taking many winding routes; those are different physical effects. This study holds arrival time and total contrast fixed, then narrows only the spread of the curve and compares that with an equally large pure time shift. If the model reacts specifically to narrowing, it is reading bolus dispersion rather than merely a late arrival—although a separate dataset would still be needed to prove that the model interprets dispersion as collateral blood flow.",
      "charter": "isles24"
    }
  ]
}


===== ideas/scout-isles24-005/run_provenance.json =====
{
  "timestamp": "2026-08-18T23:50:39+00:00",
  "git_commit": "5f2e8b7de6a0d644396d05a74ad092b8cf3b1c5a",
  "claude_cli": "2.1.197 (Claude Code)",
  "codex_cli": "codex-cli 0.148.0",
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


===== ideas/scout-isles24-005/scout_candidates.json =====
{
  "cycle": "scout-isles24-005",
  "charter": "isles24",
  "date": "2026-08-18",
  "track": "baseline,wide",
  "dataset_verification": {
    "verified_facts": [
      "The official Zenodo release (DOI 10.5281/zenodo.16731717, record version inspected 2026-08-18) contains 149 training cases. Per case it lists admission NCCT, CTA, raw 4D CTP, and Tmax/CBF/CBV/MTT maps; follow-up DWI and ADC; clinical demographics, history, admission NIHSS and 3-month mRS; final-infarct, LVO, and automatic multilabel Circle-of-Willis masks. Raw scans are in original space after defacing; derivatives are registered to NCCT.",
      "The challenge methods paper (arXiv:2408.10966v1) states that final lesion masks were derived from follow-up DWI with the ISLES'22 ensemble, with quality control and correction when needed by medical students supervised by two neuroradiologists. The dataset paper reports follow-up MRI 2-9 days after admission imaging (arXiv:2408.11142; published DOI 10.1148/ryai.250603, PMID 42017802).",
      "The planned split was 150 training cases and 100 hidden test cases from two centers; the released training archive contains 149 and the final dataset paper reports 245 total realized cases. These planned-versus-realized counts are reported rather than silently reconciled (arXiv:2408.10966v1; arXiv:2408.11142; Zenodo 16731717).",
      "Official evaluation uses Dice, absolute volume difference, lesion-wise F1, and absolute lesion-count difference, with per-case ranks averaged across measures (official repository https://github.com/ezequieldlrosa/isles24, utils/eval_utils; arXiv:2408.10966v1).",
      "The release is open access under CC BY-NC-SA 4.0 and is approximately 99 GB (official Zenodo record). Challenge submissions predict follow-up infarct from acute CT inputs; the winning report gives mean hidden-test Dice 28.5 (SD 21.27) and reports that skull stripping plus custom intensity windowing improved CT segmentation by about 10 Dice points (arXiv:2505.18424v1)."
    ],
    "source_supported_interpretations": [
      "The winner's large preprocessing gain makes attenuation contrast a documented unfinished story, but it does not establish which tissue signal the model used; c01 proposes a use test for one named candidate signal.",
      "Because CTA and clinical history are released, chronic vascular morphology and prior injury are measurable candidate context signals, but only within-case intervention can separate their use from association with outcome.",
      "The automatic Circle-of-Willis mask is an annotation asset, not independently verified vascular ground truth; candidates do not treat it as a trusted outcome label."
    ],
    "unresolved_dataset_facts": [
      "Quantitative HU preservation after the released resampling and registration pipeline.",
      "Whether every raw CTA covers the cervical carotid bifurcation and a NASCET reference segment.",
      "Whether the winning checkpoint or any other competitive ISLES'24 checkpoint is obtainable; cards allow a reproducible surrogate trained with frozen splits if not.",
      "The prevalence and separability of chronic infarct cavities in the 149 admission NCCTs.",
      "Whether cortical surfaces reconstructed from the released NCCT are stable enough for the Mode C folding experiment."
    ],
    "sources": [
      "https://zenodo.org/records/16731717 (DOI 10.5281/zenodo.16731717)",
      "https://arxiv.org/abs/2408.10966",
      "https://arxiv.org/abs/2408.11142 (DOI 10.1148/ryai.250603; PMID 42017802)",
      "https://github.com/ezequieldlrosa/isles24",
      "https://arxiv.org/abs/2505.18424"
    ]
  },
  "all_questions": [
    {"n": 1, "question": "Is an ISLES'24 final-infarct model using the acute gray-to-white matter attenuation ratio as a quantitative tissue-injury signal?", "disposition": "DEVELOPED as isles24-scout-005-c01 (Mode A); it turns the winner's documented windowing gain into a named-signal use test."},
    {"n": 2, "question": "Is the model using contralateral chronic infarct cavities as a marker of reduced brain reserve when forecasting new infarction?", "disposition": "DEVELOPED as isles24-scout-005-c02 (Mode B); radiologist word: chronic infarct/encephalomalacia."},
    {"n": 3, "question": "Is the model using ipsilateral cervical carotid stenosis as an upstream flow constraint beyond the measured intracranial perfusion deficit?", "disposition": "DEVELOPED as isles24-scout-005-c03 (Mode B); radiologist word and measurement: NASCET stenosis."},
    {"n": 4, "question": "Is the model using intracranial arterial tortuosity as a vascular-age and long-term pressure-load gauge?", "disposition": "DEVELOPED as isles24-scout-005-c04 (Mode C); cross-domain borrow: pipe curvature and accumulated mechanical load."},
    {"n": 5, "question": "Is the model using local sulcal depth and cortical curvature as a geometric scaffold for where infarct boundaries stop?", "disposition": "DEVELOPED as isles24-scout-005-c05 (Mode C); the deliberately implausible question that could not be immediately refuted; cross-domain borrow: boundary pinning from interface physics."},
    {"n": 6, "question": "Is the model using the hyperdense artery sign as a direct estimate of clot composition?", "disposition": "DROPPED: overlaps prior blood-HU and clot-permeability candidates, and acute blood attenuation cannot identify clot composition without hematocrit or retrieved-thrombus validation."},
    {"n": 7, "question": "Is the model using automated ASPECTS region involvement as a map of tissue eloquence?", "disposition": "DROPPED: ASPECTS is largely a spatial summary of the same acute attenuation/perfusion evidence, so the proposed interventions could not separate named-region use from ordinary local image use."},
    {"n": 8, "question": "Is the model using fetal posterior cerebral artery anatomy to reinterpret posterior circulation perfusion delay?", "disposition": "DROPPED: dies like idea-032 and the existing vascular-detour candidates; no new fact changes the prior identifiability objection."},
    {"n": 9, "question": "Is the model using venous sinus caliber as a proxy for intracranial compliance?", "disposition": "DROPPED: single-phase CTA caliber mixes timing, hydration, pressure, and anatomy, leaving a positive result multiply interpretable."},
    {"n": 10, "question": "Is the model using skull diploic thickness as a lifetime frailty marker?", "disposition": "DROPPED: the biological bridge from calvarial thickness to acute tissue fate is too weak to justify development even as Mode C."}
  ],
  "quota_note": "Quotas met without revival padding: 1 Mode A, 2 Mode B, and 2 Mode C; all five are CT/radiology; zero dermatology. All five necessarily use ISLES'24 because the governing charter makes that dataset load-bearing, so the generic two-per-dataset quota conflicts with and yields to the charter. Zero revivals: the portfolio brief supplies no new checkable fact satisfying any recorded unblock condition. Entry point 2 is used throughout because no model-beats-human gap was verified. The five templates are representation-erasure, regional-removal, counterfactual-synthesis, conditional-observational, and other:geometry-conditioned-boundary-test; none repeats a design skeleton.",
  "candidates": [
    {
      "id": "isles24-scout-005-c01",
      "parent_ids": [],
      "search_mode": "A",
      "entry_point": 2,
      "title": "What the winner's brain window revealed",
      "question": "Is an ISLES'24 final-infarct model using the acute gray-to-white matter attenuation ratio as a quantitative tissue-injury signal?",
      "rung": "Target rung 1: demonstrate model use of gray-to-white attenuation contrast; rung 2 requires the same signed response in at least two model families and both centers.",
      "deliverable_sentence": "The final-infarct model is using the acute gray-to-white matter attenuation ratio as a tissue-injury signal.",
      "X_measurement": "Register a standard brain atlas, take median HU in paired cortical/deep-gray and adjacent white-matter regions outside bone and vessels, and compute GWR = median(gray HU)/median(white HU), plus the affected-to-contralateral ratio. This is the standard gray-white ratio arithmetic and can be automated with atlas ROIs; an automated CT implementation is described in Tsai et al., Critical Care 2024, DOI 10.1186/s13054-024-04895-2. Compute-today test: YES on any unseen quantitative NCCT, without an annotator, conditional on HU preservation.",
      "suspected_signal": "Cytotoxic edema increases tissue water, reducing gray-matter attenuation and normal gray-white differentiation before a mature infarct is conspicuous. Narrow brain windows amplify that low-amplitude attenuation contrast.",
      "use_vs_association": "Erase only the gray-versus-white contrast component inside affected atlas regions by shifting gray and white voxels toward their local pooled mean while preserving regional mean HU, texture residuals, perfusion maps, and all contralateral inputs; compare with equal-energy common-mode HU shifts. A selective output loss under contrast erasure distinguishes use from mere correlation.",
      "keystone_prerequisite": "The released NCCT preserves local quantitative HU contrast closely enough that automated regional GWR is stable under registration and resampling.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Native-space availability does not itself prove cross-scanner HU calibration or atlas-GWR repeatability. A Stage-0 test must require ICC at least 0.9 across two reasonable registrations and rank correlation at least 0.8 between raw and derivative GWR; failure kills the mechanistic card rather than becoming a negative result.",
      "rung_reached": "0; rung 1 after the measurement gate, selective-erasure response, common-mode sham, and held-out replication.",
      "dies_like_prior": "Closest to idea-033 (insular-ribbon preprocessing), rejected for IDENTIFIABILITY_FAILURE. This is narrower and quantitatively intervenes on gray-white contrast while preserving the regional mean and using a common-mode sham; it does not claim the insular ribbon or preprocessing itself is causal. It still cannot distinguish cytotoxic edema from any other cause of lowered GWR, so the deliverable remains cue use, not pathology identification.",
      "closest_prior_work": "The winning ISLES'24 report shows a windowing gain but does not identify the exploited attenuation quantity (arXiv:2505.18424). Automated GWR has been measured on NCCT after global hypoxic injury (Tsai et al., DOI 10.1186/s13054-024-04895-2). Automated net-water-uptake work in acute stroke predicts outcome (Front Neurol 2025, DOI 10.3389/fneur.2025.1629434) but does not perform a model-use intervention on ISLES'24. No novelty claim is made beyond this targeted comparison.",
      "existing_assets": "149 raw NCCTs, co-registered acute modalities, final masks for evaluation only, atlas software, a deterministic GWR formula, and a documented competitive preprocessing recipe.",
      "smallest_decisive_experiment": "Freeze a center-stratified 5-fold split; train one winner-style nnU-Net; on 30 untouched cases run local contrast erasure, common-mode HU shams, and dose levels 25/50/75/100%. Primary readout is paired change in predicted lesion probability inside the perfusion-deficit region, label-free. Stage 0 takes 1 day; one model and interventions take 5-7 GPU-days on one 24-GB GPU.",
      "standing_confounds_addressed": "Within-case edits fix scanner, vendor, site, protocol, positioning, habitus, prevalence, referral, and patient anatomy. Common-mode shams address generic HU sensitivity; texture preservation addresses blur. Cross-center replication tests calibration. The design does not eliminate unmeasured reconstruction effects or prove edema is the sole biological source. Labels are absent from the primary readout; leakage is controlled by untouched folds.",
      "alternative_explanations": ["The model responds to any intensity edit; common-mode and equal-energy shams test this.", "Erasure changes local texture; residual texture is explicitly restored and a Fourier-energy check gates validity.", "Low GWR reflects chronic small-vessel disease rather than acute edema; affected-versus-contralateral localization and acute perfusion overlap reduce but do not eliminate this."],
      "anticipated_negative": "Sensitivity-limited if the trained model underperforms; decisive after a preregistered held-out Dice gate and the common-mode positive-control checks.",
      "remaining_legwork": "One day for HU/GWR stability; 1 week for training and the first held-out intervention decision; approximately 7 GPU-days and no new annotation.",
      "design_template": "representation-erasure",
      "entry_point_2_requirements": "Measurement: automated atlas GWR. Confused artifact: generic HU/window sensitivity or edit-induced texture loss; common-mode shams and texture-energy preservation separate them.",
      "scores": {
        "clarity": {"value": 5, "why": "One scalar contrast, one selective erasure, and explicit shams."},
        "identifiability": {"value": 3, "why": "The design isolates contrast use but not cytotoxic edema as its unique biological cause."},
        "medical_relevance": {"value": 4, "why": "Gray-white loss is a clinically recognized early ischemic sign and may explain a large benchmark preprocessing gain."},
        "interest": {"value": 4, "why": "It converts a reported engineering gain into a physician-legible mechanism."},
        "prior_legwork": {"value": 4, "why": "Recipe, raw NCCT, atlas methods, and quantitative measurements exist."},
        "feasibility": {"value": 3, "why": "Native raw NCCT availability is inspected, but the actual HU/GWR stability keystone has not been checked."},
        "data_readiness": {"value": 4, "why": "Public 149-case archive; large but directly usable."},
        "evaluation_readiness": {"value": 4, "why": "Paired probability change and standard segmentation metrics are ready."},
        "negative_result_value": {"value": 3, "why": "Useful after model-performance and measurement gates, otherwise sensitivity-limited."},
        "novelty_confidence": {"value": 3, "why": "Closest work inspected, but no systematic novelty audit."},
        "regret": {"value": 4, "why": "A direct explanation for a ten-point preprocessing effect is an obvious next experiment."}
      },
      "priority_score": 3.6,
      "unverified_claims": ["GWR stability across the two centers", "texture-preserving erasure realism", "availability of a competitive checkpoint", "precise novelty gap"],
      "plain_pitch": "A stroke makes water enter injured cells, subtly washing out the normal brightness difference between gray and white brain tissue on CT. The winning challenge system improved sharply when those faint shades were displayed differently, but nobody showed which shade difference mattered. This experiment removes only that contrast from the same scan; if the forecast weakens while equally large brightness-control edits do not, the model is using the classic early-injury sign."
    },
    {
      "id": "isles24-scout-005-c02",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "The old stroke inside the new forecast",
      "question": "Is the model using contralateral chronic infarct cavities as a marker of reduced brain reserve when forecasting new infarction?",
      "rung": "Target rung 1: use of remote chronic-infarct appearance; rung 2 requires replication with a separately trained model and an external acute-stroke cohort.",
      "deliverable_sentence": "The final-infarct model is using remote chronic infarct cavities as a brain-reserve signal when forecasting new infarction.",
      "X_measurement": "Within brain parenchyma outside ventricles and the acute Tmax>6 s territory, X is connected CSF-like hypodensity (0-30 HU) with a surrounding gliotic low-attenuation rim and atlas-inconsistent tissue loss; quantify volume and surface area, with contralateral lesions primary. A deterministic threshold/connected-component measurement can be run today on unseen NCCT after automated brain/ventricle segmentation, without an annotator; measurement validity is a gate rather than assumed diagnosis.",
      "suspected_signal": "Chronic infarcts leave encephalomalacic cavities and volume loss. They encode prior vascular injury and reduced reserve, which may lead a model to enlarge expected tissue loss even when the old lesion is remote from the current perfusion deficit.",
      "use_vs_association": "Within each case, fill only contralateral remote cavities with texture sampled from mirrored homologous tissue, while holding all acute CT, CTA, perfusion, and affected-hemisphere voxels fixed. A predicted-lesion change in the affected hemisphere, exceeding equal-volume normal-CSF and random-parenchyma shams, demonstrates use; cross-sectional correlation alone is supporting only.",
      "keystone_prerequisite": "A nontrivial subset of admission NCCTs contains automatically separable remote chronic infarct cavities rather than only nonspecific low attenuation.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The 0-30 HU morphology rule may confuse enlarged perivascular spaces, arachnoid cysts, surgical cavities, and severe leukoaraiosis. The first 20 cases require blinded algorithmic stability checks across thresholds; without released chronic-lesion labels, a positive use result supports use of cavity-like tissue loss, not proven prior infarction.",
      "rung_reached": "0; rung 1 after prevalence, stability, remoteness, realism, and sham gates.",
      "dies_like_prior": "Closest to isles24-scout-001-c04 (frail brain) but differs in a discrete, remotely editable lesion rather than diffuse correlated frailty. It avoids idea-020's geometry confounding by editing contralateral tissue while freezing the affected input. Annotation provenance is not load-bearing because the primary endpoint is paired model output.",
      "closest_prior_work": "Prior-infarct burden is a recognized imaging marker, while infarct pattern predicts function independent of volume (Radiology 2021, DOI 10.1148/radiol.2021203964). The ISLES'24 dataset paper includes patient history but does not report a model-use test for old cavities (DOI 10.1148/ryai.250603). No verified prior intervention study on this question was found; that is not proof of novelty.",
      "existing_assets": "Raw NCCT, registered acute maps, automatic brain/ventricle segmentation tools, mirrored tissue donor regions, and label-free paired output comparison.",
      "smallest_decisive_experiment": "Census the first 30 cases; proceed only if at least 15 have stable remote cavity volume of at least 1 mL. On those cases perform cavity fill, ventricle-adjacent CSF fill, and random-parenchyma shams. About 2 days measurement work and 20 GPU-hours once a model is frozen.",
      "standing_confounds_addressed": "Paired edits fix scanner, vendor, protocol, site, positioning, habitus, prevalence, referral, and all acute pathology. Contralateral remoteness prevents direct lesion overlap. Shams address generic filling and CSF-boundary effects. It does not prove the cavity's etiology or distinguish prior-injury reserve from a learned age proxy.",
      "alternative_explanations": ["The response is to any CSF boundary; ventricle and arachnoid-space shams test this.", "The cavity is a proxy for age, not reserve; age-stratified response is reported but cannot fully distinguish the two.", "Inpainting artifacts drive the response; use two independent fill methods and require concordance."],
      "anticipated_negative": "Decisive only if prevalence, segmentation stability, model performance, and two-method edit realism gates pass; otherwise sensitivity-limited.",
      "remaining_legwork": "2 days to the prevalence kill decision; 4-6 days to paired results; under 20 GPU-hours; no new labels requested.",
      "design_template": "regional-removal",
      "entry_point_2_requirements": "Measurement: remote CSF-like cavity burden. Confused artifacts: ventricles/other CSF spaces and inpainting seams; anatomic shams and two fill methods address them.",
      "scores": {
        "clarity": {"value": 4, "why": "The cue and paired edit are clear, though lesion classification needs a gate."},
        "identifiability": {"value": 3, "why": "Remote editing identifies cavity use but not whether the model interprets it as reserve or age."},
        "medical_relevance": {"value": 4, "why": "Prior injury is clinically meaningful context for tissue vulnerability and transportability."},
        "interest": {"value": 4, "why": "A new-lesion model consulting old damage is plausible but not routinely measured."},
        "prior_legwork": {"value": 3, "why": "Segmentation ingredients exist, but no released chronic-lesion labels."},
        "feasibility": {"value": 3, "why": "Capped because the prevalence and separability keystone is uninspected."},
        "data_readiness": {"value": 4, "why": "All images are public and no external outcomes are needed."},
        "evaluation_readiness": {"value": 3, "why": "Paired output is direct; cavity-validity metrics are custom."},
        "negative_result_value": {"value": 3, "why": "Useful after stringent prevalence and realism gates."},
        "novelty_confidence": {"value": 3, "why": "Limited primary-source search only."},
        "regret": {"value": 3, "why": "Worth a cheap census before more elaborate reserve experiments."}
      },
      "priority_score": 3.4,
      "unverified_claims": ["remote chronic-cavity prevalence", "automatic specificity", "edit realism", "novelty"],
      "plain_pitch": "An old stroke can leave a fluid-filled cavity in the brain. This study asks whether a model predicting a new stroke looks across the brain at that old damage and treats the patient as more vulnerable. Filling only the old-looking cavity in a copy of the scan, while leaving the new stroke and its blood-flow maps untouched, would reveal whether that remote history changes the forecast."
    },
    {
      "id": "isles24-scout-005-c03",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "The bottleneck before the brain",
      "question": "Is the model using ipsilateral cervical carotid stenosis as an upstream flow constraint beyond the measured intracranial perfusion deficit?",
      "rung": "Target rung 1: use of the stenotic lumen; rung 2 requires a flow-consistent intervention or natural paired study that also identifies upstream resistance.",
      "deliverable_sentence": "The final-infarct model is using ipsilateral cervical carotid stenosis as an upstream flow constraint beyond the measured intracranial perfusion deficit.",
      "X_measurement": "Segment the cervical ICA lumen on CTA and compute NASCET stenosis = 100*(1 - minimum residual lumen diameter/distal normal ICA diameter). Semi-automated CTA NASCET measurement is established (White et al., PMID 20724259, DOI 10.1017/S0317167100010532); CarotidNet provides fully automatic CTA segmentation for stenosis quantification (PMID 33392012, DOI 10.21037/qims-20-286). Compute-today test: YES on an unseen CTA if its field of view includes the bifurcation and distal reference.",
      "suspected_signal": "A narrowed cervical carotid increases upstream hydraulic resistance and reduces pressure reserve. At matched acute perfusion maps, a model may treat severe ipsilateral stenosis as evidence that threatened tissue has less capacity to survive or re-perfuse.",
      "use_vs_association": "Create a lumen-restored CTA counterfactual by replacing only the stenotic segment with a patient-specific centerline tube whose diameter equals the distal reference, preserving plaque exterior, distal vessels, NCCT and every CTP-derived map; compare with an equal-volume lumen edit in the contralateral carotid and a nonstenotic-segment sham. Output change demonstrates visual use, not merely cohort association.",
      "keystone_prerequisite": "Released raw CTA consistently covers the cervical carotid bifurcation and distal normal ICA needed for NASCET measurement.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Even with coverage, a synthetic open lumen paired with unchanged downstream perfusion is physiologically inconsistent. A positive response establishes use of stenosis appearance, but the 'upstream flow constraint' interpretation remains rung 1 unless a flow-consistent model or natural pre/post-treatment pair is added.",
      "rung_reached": "0; rung 1 after coverage, segmentation, realism, receptive-field, and laterality-sham gates.",
      "dies_like_prior": "Resembles idea-032 (spare routes), killed because anatomy covaried with physiology. This card makes a narrower visual-use claim with a direct lumen edit while freezing downstream physiology; it therefore identifies cue use but deliberately does not claim causal collateral flow. The physiological wording is the residual weakness and caps identifiability.",
      "closest_prior_work": "CTA NASCET measurement and automated carotid segmentation are established (DOI 10.1017/S0317167100010532; DOI 10.21037/qims-20-286). The challenge and winning papers do not test whether final-infarct models use cervical stenosis (arXiv:2408.10966; arXiv:2505.18424). No systematic novelty audit has been completed.",
      "existing_assets": "Raw CTA, acute perfusion maps, automatic vessel segmentation literature/code pathway, standard NASCET formula, and paired label-free readout.",
      "smallest_decisive_experiment": "Inspect CTA coverage in 20 cases in half a day. If at least 90% cover the required anatomy and at least 20 cases in the cohort have measurable ipsilateral stenosis above 30%, run three lumen-restoration doses and shams on those 20; 1 week and under 30 GPU-hours after model freeze.",
      "standing_confounds_addressed": "Within-case edits fix scanner, site, protocol, positioning, habitus, prevalence, referral, and distal perfusion. Contralateral and nonstenotic shams address generic bright-lumen edits. Not ruled out: plaque texture, calcification, centerline geometry, or physiologic inconsistency may drive response. Reconstruction and bolus timing can affect segmentation and are audited, not eliminated.",
      "alternative_explanations": ["The model reads plaque/calcification rather than narrowing; preserve the plaque exterior and vary only lumen diameter.", "Any vessel edit changes output; contralateral and nonstenotic shams test this.", "The inconsistent CTA-perfusion pair is detected as out of distribution; feature-distance and a natural low-stenosis reference bank provide only partial protection."],
      "anticipated_negative": "Uninterpretable if the receptive field excludes the neck or severe stenosis is rare; after those gates, sensitivity-limited because realistic lumen counterfactuals remain difficult.",
      "cross_domain": {"borrowed_construct": "Hydraulic resistance in a supply pipe upstream of a network.", "measurement_it_implies": "NASCET diameter loss and a graded virtual lumen-restoration response.", "what_changes_if_dropped": "The experiment still tests use of a stenosis image sign, but no longer supports language about upstream flow reserve."},
      "remaining_legwork": "Half a day for coverage, 2 days for stenosis census, and about 1 week for edits; under 30 GPU-hours; no new annotations.",
      "design_template": "counterfactual-synthesis",
      "entry_point_2_requirements": "Measurement: automated NASCET percent stenosis. Confused artifacts: plaque calcification and CTA bolus/reconstruction; lumen-only editing and shams address but do not fully remove them.",
      "scores": {
        "clarity": {"value": 4, "why": "A standard measurement and graded intervention, with a clear residual interpretive limit."},
        "identifiability": {"value": 2, "why": "Visual cue use is testable, but physiologic inconsistency leaves multiple explanations."},
        "medical_relevance": {"value": 4, "why": "Upstream stenosis affects reserve and treatment context."},
        "interest": {"value": 4, "why": "It asks whether a brain model reads a bottleneck outside the brain."},
        "prior_legwork": {"value": 3, "why": "Measurement and segmentation exist; field of view and model coverage do not."},
        "feasibility": {"value": 2, "why": "Coverage, prevalence, and realistic editing are unverified."},
        "data_readiness": {"value": 3, "why": "CTA is public, but anatomical coverage is unknown."},
        "evaluation_readiness": {"value": 3, "why": "Paired output is ready; realism gates are bespoke."},
        "negative_result_value": {"value": 2, "why": "A null remains sensitivity-limited even after gates."},
        "novelty_confidence": {"value": 2, "why": "Only a targeted search was performed and keystone is uninspected."},
        "regret": {"value": 3, "why": "A cheap coverage census determines whether the memorable question is viable."}
      },
      "priority_score": 2.85,
      "unverified_claims": ["cervical CTA coverage", "stenosis prevalence", "CarotidNet portability", "counterfactual realism", "novelty"],
      "plain_pitch": "A severe narrowing in the neck artery is a bottleneck before blood ever reaches the injured brain. The perfusion maps show what is happening downstream, but the model may also inspect that upstream bottleneck and assume the tissue has less room for recovery. Virtually reopening only the narrowed lumen while leaving the measured brain perfusion unchanged tests whether the visible bottleneck itself changes the forecast, though it cannot by itself prove the model understands blood-flow physics."
    },
    {
      "id": "isles24-scout-005-c04",
      "parent_ids": [],
      "search_mode": "C",
      "entry_point": 2,
      "title": "The pressure history written in a winding artery",
      "question": "Is the model using intracranial arterial tortuosity as a vascular-age and long-term pressure-load gauge?",
      "rung": "Mode C target rung 1: use of tortuosity; rung 3 requires external validation that the representation tracks age/pressure load rather than ancestry, anatomy, or disease subtype.",
      "deliverable_sentence": "The final-infarct model is using intracranial arterial tortuosity as a vascular-age and long-term pressure-load gauge.",
      "X_measurement": "From CTA vessel centerlines, compute tortuosity index TI = 100*(centerline length/chord length - 1) for bilateral MCA and basilar arteries, then average. This exact formula is reported in Kim et al., Investig Magn Reson Imaging 2018, DOI 10.13104/imri.2018.22.3.150, and is computable today from an unseen CTA using an automatic vessel mask and skeletonization, without annotation.",
      "suspected_signal": "Years of pulsatile pressure and arterial-wall remodeling lengthen and curve large arteries. Primary CTA studies associate carotid or intracranial tortuosity with age and hypertension, although effects vary by population (DOI 10.3389/fneur.2024.1307984; DOI 10.13104/imri.2018.22.3.150). A model could use this stable geometry as a vascular-age shortcut when estimating tissue resilience.",
      "use_vs_association": "Primary evidence would be a conditional-observational test: within narrow strata of age, site, occlusion location, perfusion-deficit volume, HIR, and Circle-of-Willis topology, test whether case-level tortuosity explains prediction residuals but not ground-truth residuals. This can falsify the simplest shortcut account but cannot prove use; a later geometry-preserving counterfactual is required for rung 1.",
      "keystone_prerequisite": "Automated centerlines in the released CTA recover MCA and basilar paths with sufficient continuity and tortuosity variation across 149 cases.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Even perfect centerlines leave tortuosity entangled with age, hypertension, ancestry, and vessel elongation. The proposed conditional test is discovery, not a use demonstration; this is why identifiability is low and the card is Mode C.",
      "rung_reached": "0; rung 1 only after a credible selective tortuosity intervention or natural paired validation, not merely a significant regression coefficient.",
      "dies_like_prior": "Closest to isles24-scout-004-c05 (calcification age gauge) and idea-032 (vascular anatomy). It differs in a continuous mechanical-history quantity rather than calcium or collateral connectivity, but it has not yet escaped their proxy-identifiability problem; the card labels that limitation rather than claiming a solved mechanism.",
      "closest_prior_work": "Intracranial tortuosity measurement and population-specific associations with age/hypertension are reported in DOI 10.13104/imri.2018.22.3.150; carotid tortuosity associations are reported in DOI 10.3389/fneur.2024.1307984. Neither paper audits a final-infarct network. Novelty is not established.",
      "existing_assets": "CTA, automatic Circle-of-Willis masks, standard centerline arithmetic, demographics and hypertension history, perfusion maps, and final masks.",
      "smallest_decisive_experiment": "Run automatic vessel extraction on 30 cases; continue only if at least 80% yield continuous bilateral MCA and basilar centerlines and test-retest TI ICC is at least 0.9. Then conduct a preregistered nested cross-validated residual analysis on all 149 cases. Two to four days, under 10 GPU-hours.",
      "standing_confounds_addressed": "Matching/adjustment addresses measured age, hypertension, site, occlusion, perfusion severity, and topology. Scanner, reconstruction, and bolus affect segmentation and require sensitivity analysis. Ancestry is not released and cannot be ruled out. Label leakage is avoided through out-of-fold predictions. The design does not yet distinguish use from association, explicitly preventing rung advancement.",
      "alternative_explanations": ["Tortuosity is only an age or ancestry proxy; measured age can be adjusted, ancestry cannot.", "Segmentation quality varies with CTA bolus; centerline continuity and intensity sensitivity analyses test this.", "Tortuous vessels covary with collateral anatomy; topology-stratified analysis reduces but does not remove it."],
      "anticipated_negative": "Sensitivity-limited: a null could reflect small n, noisy centerlines, or a genuinely unused cue; useful mainly as a cheap kill before intervention development.",
      "cross_domain": {"borrowed_construct": "Cumulative mechanical load recorded as permanent curvature in a repeatedly pressurized pipe.", "measurement_it_implies": "Centerline excess length over chord length, tested against age and hypertension history.", "what_changes_if_dropped": "The study becomes a generic vessel-shape association and loses both its proposed mechanism and most of its interest."},
      "remaining_legwork": "1 day centerline gate and 2-3 days conditional analysis; a convincing intervention would require an additional 2-3 weeks and may fail.",
      "design_template": "conditional-observational",
      "entry_point_2_requirements": "Measurement: centerline tortuosity index. Confused artifacts: CTA bolus/segmentation quality and collateral topology; quality gates and stratification address them incompletely.",
      "scores": {
        "mechanism_clarity": {"value": 5, "why": "Named arterial-wall remodeling mechanism and exact geometric quantity."},
        "identifiability": {"value": 3, "why": "Conditional analysis removes major measured alternatives but cannot establish use or remove ancestry."},
        "interest": {"value": 4, "why": "A model reading lifetime pressure history from vessel shape is unexpected and testable."},
        "medical_relevance": {"value": 3, "why": "Vascular age is plausible context but the immediate clinical consequence is indirect."},
        "clarity": {"value": 4, "why": "The discovery test is precise and its inability to reach rung 1 is explicit."},
        "prior_legwork": {"value": 3, "why": "Measurement literature and masks exist, but intervention work does not."},
        "feasibility": {"value": 3, "why": "Reported outside Mode C score and capped because centerline recovery is uninspected."},
        "data_readiness": {"value": 4, "why": "CTA and covariates are public."},
        "evaluation_readiness": {"value": 3, "why": "Residual analysis is standard; use-test evaluation is absent."},
        "negative_result_value": {"value": 2, "why": "A null is sensitivity-limited but can kill the expensive next step."},
        "novelty_confidence": {"value": 2, "why": "Targeted search only; no novelty claim."},
        "regret": {"value": 3, "why": "Cheap enough to screen despite the proxy problem."}
      },
      "mode_c_priority_score": 3.9,
      "unverified_claims": ["centerline continuity", "tortuosity variance", "adequate conditional overlap", "availability of ancestry control", "novelty"],
      "plain_pitch": "Arteries can grow longer and more winding after years of aging and high blood pressure, much as a repeatedly stressed hose changes shape. This speculative screen asks whether a stroke model reads that winding geometry as a summary of the patient's vascular history. A statistical link after matching similar strokes would justify building a harder intervention, but it would not yet prove that the model actually uses the shape."
    },
    {
      "id": "isles24-scout-005-c05",
      "parent_ids": [],
      "search_mode": "C",
      "entry_point": 2,
      "title": "Do sulci pin the predicted infarct edge?",
      "question": "Is the model using local sulcal depth and cortical curvature as a geometric scaffold for where infarct boundaries stop?",
      "rung": "Mode C target rung 1: prediction boundaries depend on cortical folding after local tissue evidence is controlled; rung 2 requires replication across model families and an external cohort.",
      "deliverable_sentence": "The final-infarct model is using local sulcal depth and cortical curvature as a geometric scaffold for predicted infarct boundaries.",
      "X_measurement": "Reconstruct the pial/gray-white surfaces from NCCT with atlas-constrained automated tissue segmentation; X is signed mean curvature and geodesic sulcal depth at each cortical vertex, with boundary alignment measured by excess predicted-boundary density within 2 mm of curvature extrema. These are deterministic differential-geometric quantities computable on an unseen scan without human input if surface reconstruction passes stability gates.",
      "suspected_signal": "Cortical folds organize gray/white interfaces, pial vessels, partial-volume edges, and convolutional image gradients. A network may use curvature ridges as learned stopping boundaries even when true tissue fate crosses them; the proposed physical analogue is interface pinning at a pre-existing geometric ridge, not a claim that sulci biologically halt ischemia.",
      "use_vs_association": "Use a held-out-structure prediction test: match boundary and non-boundary cortical vertices within case on Tmax, CBF, CBV, MTT, NCCT HU, tissue class, arterial territory, and distance to occlusion; ask whether curvature still predicts model boundary but not ground-truth boundary. Then locally erase curvature information in intermediate representations with a cross-validated linear concept direction while preserving perfusion features; selective boundary displacement is the use test. Observational alignment alone does not count.",
      "keystone_prerequisite": "Atlas-constrained cortical surfaces and curvature estimates are stable on acute NCCT at the released resolution, including near ischemic cortex.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "Even stable curvature covaries with tissue interfaces, vascular territories, and partial volume. Linear representation erasure may remove correlated anatomy rather than curvature alone; the strongest possible conclusion is model dependence on a curvature-associated representation, not a biological barrier.",
      "rung_reached": "0; rung 1 only after surface stability, overlap, ground-truth-negative-control, erasure selectivity, and sham-direction gates.",
      "dies_like_prior": "Most resembles idea-020 (spreading front), killed because geometry and perfusion gradients co-varied. This design matches local perfusion and asks for model-boundary enrichment absent from ground truth, then erases a representation direction. That is a real difference, but selective erasure may still remove co-encoded anatomy, so identifiability remains deliberately low.",
      "closest_prior_work": "Infarct pattern and cortical/deep structure carry prognostic information independent of volume (Radiology 2021, DOI 10.1148/radiol.2021203964), but that does not test sulcal curvature use. Concept erasure methods exist generally, yet no primary work was verified that applies curvature erasure to ISLES'24. Novelty remains unaudited.",
      "existing_assets": "NCCT, co-registered perfusion maps, atlas surface templates, model feature maps, final masks as a negative-control boundary, and standard curvature formulas.",
      "smallest_decisive_experiment": "On 20 cases, reconstruct surfaces twice with perturbed registration; kill unless curvature ICC exceeds 0.85 and at least 10,000 matched cortical vertices retain overlap. Fit the matched boundary model on held-out cases; attempt representation erasure only if model-boundary enrichment is present and ground-truth enrichment is absent. Three days for the screen, about 2 weeks for erasure, under 40 GPU-hours.",
      "standing_confounds_addressed": "Within-case matching addresses site, scanner, protocol, position, habitus, prevalence, referral, local perfusion, HU, tissue class, territory, and occlusion distance. Ground-truth boundaries distinguish network convention from biological anatomy. Reconstruction and partial-volume artifacts remain serious. Out-of-fold features prevent label leakage; no new annotations are required.",
      "alternative_explanations": ["Curvature only marks gray-white or CSF interfaces; match tissue class and intensity gradient, then report residual dependence.", "Vascular territories follow folds; match territory and use ground-truth-boundary behavior as control.", "Erasure removes generic spatial position; random and coordinate-direction shams test selectivity but cannot prove perfect isolation."],
      "anticipated_negative": "Sensitivity-limited if surfaces or concept directions are noisy; after all gates, a null is useful evidence against a seductive architectural-boundary story for this model.",
      "cross_domain": {"borrowed_construct": "Interface pinning from materials physics, where a moving boundary catches on a pre-existing geometric ridge.", "measurement_it_implies": "Excess prediction-boundary density at curvature extrema and displacement after curvature-direction erasure.", "what_changes_if_dropped": "The measurement remains valid, but the claim shrinks to generic anatomical edge following and loses the proposed mechanism."},
      "remaining_legwork": "3 days to the surface/association kill decision; about 2 further weeks for representation erasure; under 40 GPU-hours and no annotation.",
      "design_template": "other:geometry-conditioned-boundary-test",
      "design_template_justification": "The grammar combines within-case matched held-out-structure prediction with representation erasure; no listed single template captures the required ground-truth-negative-control boundary comparison.",
      "entry_point_2_requirements": "Measurement: cortical mean curvature, sulcal depth, and excess boundary density. Confused artifact: tissue-interface partial volume and vascular-territory geometry; matching and ground-truth-boundary controls address them incompletely.",
      "scores": {
        "mechanism_clarity": {"value": 4, "why": "A named geometric ridge and explicit boundary measurement, though the biological relevance is intentionally not asserted."},
        "identifiability": {"value": 2, "why": "Curvature is tightly co-encoded with anatomy and representation erasure may not isolate it."},
        "interest": {"value": 5, "why": "The obviously-wrong possibility of folds pinning model boundaries would expose a memorable architectural prior."},
        "medical_relevance": {"value": 3, "why": "Boundary validity matters, but the construct is primarily about model behavior rather than treatment."},
        "clarity": {"value": 4, "why": "The staged falsification criteria and prohibited conclusion are explicit."},
        "prior_legwork": {"value": 2, "why": "Geometry tools exist, but NCCT surface stability and the erasure bridge are unproven."},
        "feasibility": {"value": 2, "why": "Reported outside Mode C score; two major gates may fail."},
        "data_readiness": {"value": 4, "why": "All required images and masks are public."},
        "evaluation_readiness": {"value": 2, "why": "Metrics are custom and require careful matching diagnostics."},
        "negative_result_value": {"value": 2, "why": "Mostly sensitivity-limited, though it can kill an attractive story."},
        "novelty_confidence": {"value": 2, "why": "No systematic audit and keystone uninspected."},
        "regret": {"value": 3, "why": "The cheap association screen is worthwhile before dismissing the idea."}
      },
      "mode_c_priority_score": 3.55,
      "unverified_claims": ["NCCT surface stability", "matched-support size", "curvature enrichment", "selective erasure validity", "novelty"],
      "plain_pitch": "The brain's surface is deeply folded into ridges and grooves. This intentionally speculative idea asks whether a segmentation model treats those folds like convenient fence lines when drawing the predicted edge of a stroke, even when the actual later injury does not. If matched regions with the same blood-flow injury show model boundaries collecting at folds—and removing the model's fold representation moves those boundaries—the model is using cortical geometry as a scaffold."
    }
  ]
}


===== ideas/scout-isles24-005/wide_candidates.json =====
{
  "candidates": [
    {
      "id": "isles24-scout-005-c06",
      "parent_ids": [],
      "track": "wide",
      "entry_point": 2,
      "title": "Does the model trust tissue that obeys the flow equation?",
      "question": "Is an ISLES'24 final-infarct model using voxelwise violation of the central-volume identity CBV = CBF x MTT as a hidden confidence map for the released perfusion estimates?",
      "rung": "Target rung 1: selective use of the cross-map inconsistency residual; rung 2 requires the response to replicate across model families and across independently regenerated perfusion maps.",
      "deliverable_sentence": "The final-infarct model is using violation of the central-volume identity as a hidden confidence map for perfusion evidence.",
      "X_measurement": "Inside brain tissue, fit the unit/scale constant on normal contralateral voxels and compute X = |log(CBV) - log(CBF) - log(MTT/60) - k_case|, with cerebral blood volume (CBV) in mL/100 g, cerebral blood flow (CBF) in mL/100 g/min, and mean transit time (MTT) in seconds. Report median X and connected high-X islands inside the acute Tmax>6 s territory. The formula is deterministic and annotator-free; the central-volume theorem is described in Konstas et al., AJNR 2009, PMID 19270105, and the three registered maps are in the official ISLES'24 release (Zenodo DOI 10.5281/zenodo.16731717).",
      "suspected_signal": "For an ideal indicator-dilution calculation the three maps are not independent: CBV equals CBF multiplied by MTT after unit conversion. Noise, delay sensitivity, regularization, map clipping, and implementation details can break that identity locally. A multichannel model could learn that high-residual tissue is an unreliable measurement region and discount or reinterpret its perfusion deficit, even though no explicit uncertainty map was supplied.",
      "use_vs_association": "Project each affected-region map triplet onto the nearest central-volume-consistent manifold while preserving the local CBF and Tmax ranks, then compare the prediction with equal-energy perturbations tangent to that manifold; a selective, graded response to removing only the normal residual is evidence of use rather than correlation.",
      "keystone_prerequisite": "The released CBF, CBV, and MTT maps have meaningful common support and scaling such that a stable, nontrivial central-volume residual can be computed rather than merely rediscovering zeros, support edges, or arbitrary normalization.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The theorem is verified, and all three maps are verified as released, but the release's value units, clipping rules, and local algebraic consistency have not been inspected. Stage 0 must read headers and value distributions in 10 cases, exclude zero/support boundaries, and require residual rank correlation at least 0.8 under two defensible normal-tissue masks. If X collapses to a constant, a support mask, or a unit error, the candidate dies.",
      "rung_reached": "0; rung 1 only after measurement, manifold-projection realism, model-performance, dose-response, and tangent-sham gates.",
      "dies_like_prior": "This is adjacent to isles24-scout-001-c08 (the deconvolution algorithm may have signed the image) and idea-037 (site identity), both vulnerable to IDENTIFIABILITY_FAILURE. It differs by naming an invariant that is calculable within every case and selectively removable without swapping sites or algorithms. A positive result would establish use of cross-map inconsistency, not which vendor produced it or why it arose; that narrower claim avoids the unsupported provenance attribution.",
      "closest_prior_work": "Indicator-dilution theory fixes the algebraic relation among CBF, CBV, and MTT; commercial packages applied to identical stroke source data nevertheless produce materially different maps. Infarct networks fuse these maps, but the searched primary work does not test whether a network reads their internal physical inconsistency as uncertainty. No novelty claim beyond this targeted comparison is made.",
      "novelty_neighbors": [
        {
          "work": "Konstas et al., Theoretic Basis and Technical Implementations of CT Perfusion in Acute Ischemic Stroke, Part 1",
          "identifier": "PMID 19270105; AJNR 2009; official full text https://pmc.ncbi.nlm.nih.gov/articles/PMC7051780/",
          "relation": "Defines the central-volume theorem and explains that MTT is calculated from CBV/CBF; supplies the physical invariant but does not audit model use of its residual."
        },
        {
          "work": "Kudo et al., Differences in CT Perfusion Maps Generated by Different Commercial Software",
          "identifier": "DOI 10.1148/radiol.254082000; PMID 20032153",
          "relation": "Shows that identical acute-stroke source data produce significantly different maps across software, motivating a hidden map-quality cue; it does not study learned final-infarct models or the within-triplet residual."
        },
        {
          "work": "Liu et al., ISP-Net: Fusing features to predict ischemic stroke infarct core on CT perfusion maps",
          "identifier": "DOI 10.1016/j.cmpb.2022.106630",
          "relation": "A primary example of a network fusing native perfusion, CBF, CBV, MTT, and Tmax; it reports prediction performance, not a conservation-law intervention."
        }
      ],
      "novelty_delta": "The proposed experiment is the first located test that removes only the voxelwise violation of a known perfusion identity and asks whether a final-infarct model changes its forecast while physiology-preserving tangent shams do not.",
      "why_not_done": "BLIND_SPOT: perfusion papers treat disagreement as a software-validation problem and model papers treat registered maps as independent input channels, leaving the algebraic residual between those channels uninterrogated as a learned uncertainty signal.",
      "existing_assets": "Official registered CBF, CBV, MTT, and Tmax maps for 149 public training cases; raw CTP for later regeneration; final masks; official metrics; standard projection and paired-output arithmetic; a winner-style surrogate can be trained if no checkpoint is obtainable.",
      "smallest_decisive_experiment": "Stage 0 on 10 cases computes support, units, X stability, and whether X contains more than border/zero artifacts. Freeze a center-stratified split and one compact 2D multichannel U-Net; require held-out median Dice at least 0.20 and lesion-wise F1 above a frozen all-zero baseline. On 20 untouched cases run 25/50/75/100% residual removal, tangent shams matched in per-channel L2 energy, and a support-edge sham. Primary readout: paired change in predicted lesion probability within Tmax>6 s tissue, with monotone residual-dose response and residual-over-sham contrast. Compute envelope: one Colab GPU session, at most 10 GPU-hours, using 2D patches and the public registered maps; no new annotation.",
      "standing_confounds_addressed": "Within-case projections hold center, scanner, protocol, positioning, anatomy, treatment, and lesion prevalence fixed. Excluding zeros and eroding support edges prevents X from becoming a coverage mask. Tangent shams test generic sensitivity to map edits; fixed CBF/Tmax ranks protect the main perfusion ordering; two projection metrics test dependence on the chosen geometry. The experiment still cannot identify the source of inconsistency or prove calibrated uncertainty, so those conclusions are prohibited.",
      "alternative_explanations": [
        "The model responds to any violation-correction edit; equal-energy tangent shams and a monotone residual-specific contrast test this.",
        "X is only a map-support or clipping detector; eroded common support, clipped-voxel exclusion, and a support-edge sham test this.",
        "Projection moves cases off the training distribution; nearest-neighbor feature distance and two small-dose arms gate the confirmatory result but cannot prove perfect realism."
      ],
      "anticipated_negative": "Decisive if X is stable, the model passes its frozen performance gate, the small-dose edits remain in distribution, and shams produce detectable generic sensitivity; otherwise the null is sensitivity-limited.",
      "cross_domain": {
        "borrowed_construct": "Conservation-law residuals from process control: redundant sensors linked by a physical balance equation provide a residual that detects unreliable measurements without an external fault label.",
        "measurement_it_implies": "The absolute log residual of CBV = CBF x MTT and a projection that removes that residual while retaining the physiological coordinates along the constraint manifold.",
        "what_changes_if_dropped": "Without the process-control construct this becomes generic channel ablation, which cannot distinguish use of perfusion physiology from use of cross-map inconsistency."
      },
      "remaining_legwork": "Half a day for the 10-case algebra/support kill gate; one Colab session for the surrogate and 20-case intervention; a later raw-CTP regeneration study is outside this card.",
      "design_template": "counterfactual-synthesis",
      "entry_point_2_requirements": "Measurement: central-volume residual X. Confused artifacts: common-support edges, zeros, clipping, and generic multichannel perturbation; erosion, clipped-voxel exclusion, tangent shams, and dose response separate them.",
      "scores": {
        "clarity": {"value": 5, "why": "One physical identity, one residual, and a selective projection with explicit shams."},
        "identifiability": {"value": 4, "why": "The intervention isolates residual use, although it cannot identify the residual's technical cause or prove uncertainty calibration."},
        "medical_relevance": {"value": 4, "why": "A model silently discounting physically inconsistent perfusion could determine where it trusts the acute scan and how it transports across software."},
        "interest": {"value": 5, "why": "A stroke model acting as its own physics-based quality controller is surprising and directly actionable."},
        "prior_legwork": {"value": 4, "why": "The invariant, map inputs, software-variability evidence, and model family all exist."},
        "feasibility": {"value": 3, "why": "Capped because the released maps' units and residual stability have not been inspected."},
        "data_readiness": {"value": 4, "why": "All maps and outcomes are public and registered, with a modest download path."},
        "evaluation_readiness": {"value": 4, "why": "Paired probability response, dose response, shams, and official segmentation metrics are ready."},
        "negative_result_value": {"value": 4, "why": "After the algebra and model gates, a selective null rules out this specific hidden-confidence mechanism."},
        "novelty_confidence": {"value": 3, "why": "Three close primary neighbors were searched, but no systematic review was performed and the keystone remains uninspected."},
        "regret": {"value": 5, "why": "The required redundant maps are already in the benchmark, making this a cheap obvious-in-hindsight audit."}
      },
      "priority_score": 3.95,
      "unverified_claims": [
        "the released map units permit a stable central-volume residual",
        "the residual is not dominated by support or clipping",
        "a compact surrogate reaches the frozen performance gate in one session",
        "manifold projections remain in distribution",
        "the precise novelty gap beyond the targeted search"
      ],
      "plain_pitch": "Blood flow, blood volume, and transit time are tied by a simple physical equation, yet stroke software can produce maps that locally disagree with it. This study asks whether the prediction model notices those disagreements and quietly treats them as a warning that a region's blood-flow estimate is unreliable. If correcting only the disagreement changes the forecast while equally sized, physics-preserving edits do not, the model is using an accidental quality-control signal that could fail when the hospital changes software."
    },
    {
      "id": "isles24-scout-005-c07",
      "parent_ids": [],
      "track": "wide",
      "entry_point": 2,
      "title": "The roughness of a heartbeat through starved tissue",
      "question": "Is a raw-CT-perfusion final-infarct model using the temporal fractal dimension of each voxel's contrast curve as a deconvolution-free tissue-flow signal?",
      "rung": "Target rung 1: selective model use of Higuchi temporal fractal dimension; rung 2 requires replication in a second raw-time-series architecture and on a non-ISLES cohort.",
      "deliverable_sentence": "The final-infarct model is using temporal fractal dimension of the raw contrast curve as a tissue-flow signal.",
      "X_measurement": "For each brain voxel's baseline-subtracted raw four-dimensional CT-perfusion attenuation series, compute Higuchi fractal dimension using the frame-count-adapted kmax procedure of Lim et al. The measurement is deterministic, voxelwise, annotator-free, and has already been run on all 149 public ISLES'24 perfusion studies (PMID 40824507).",
      "suspected_signal": "A bolus curve is not only a peak and delay; its multiscale temporal roughness reflects how contrast concentration changes across sampling intervals. Lim et al. found that this fractal dimension tracks simulated flow and separates normal, penumbral, and core tissue on ISLES'24. A raw-time-series network may exploit that compact, deconvolution-free descriptor even when its architecture never names it.",
      "use_vs_association": "At each affected voxel, replace only the component of the time curve that predicts Higuchi fractal dimension using a cross-validated concept direction in the model's temporal encoder, while preserving curve area, peak time, peak height, first two moments, and spatial anatomy; compare with random orthogonal directions and with explicit X-preserving temporal jitter. Selective output loss under X erasure is the use test.",
      "keystone_prerequisite": "Higuchi temporal fractal dimension is computable and nondegenerate on the released raw ISLES'24 time series, and differs across relevant tissue states.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "Lim et al., 'Time series-derived fractal dimension of CT perfusion in acute ischemic stroke: a promising marker for hypoperfused tissue quantification,' PMID 40824507, inspected via the PubMed primary abstract on 2026-08-18: 'Fractal analysis was applied to voxel-wise time-series data from both simulated phantom datasets and 149 CTP images from the publicly available ... ISLES 2024 dataset'; FD differed across core, penumbra, and normal tissue (p<0.001), achieved penumbra-versus-normal AUC 0.732, and correlated with true CBF at rho>0.9 in the phantom after kmax optimization.",
      "keystone_residual_assumption": "The paper establishes measurement feasibility and association on the exact images, not that any final-infarct model uses X. Fractal dimension may mostly encode ordinary CBF, noise, or temporal sampling. Moment preservation, CBF-stratified analysis, and noise/sampling shams are therefore necessary, and even a positive result supports use of the descriptor rather than a unique microvascular mechanism.",
      "rung_reached": "0; rung 1 after raw-model performance, concept decodability, selectivity, CBF-matched, sampling, and noise gates.",
      "dies_like_prior": "This could die like idea-024 (capillary traffic jam; DATA_ACCESS) or idea-020 (IDENTIFIABILITY_FAILURE). The exact raw data and exact measurement have now been demonstrated on all 149 ISLES'24 cases, changing the access premise. Unlike a biological capillary-state claim, this card asks only whether a named mathematical descriptor is used and requires erasure beyond curve moments and CBF; it does not call the descriptor capillary transit heterogeneity.",
      "closest_prior_work": "One 2025 paper computes this exact feature on ISLES'24 and shows tissue discrimination; raw-CTP deep-learning papers show that temporal encoders learn features related to but not exhausted by standard maps. None of the located primary works selectively erases fractal dimension from a final-infarct model.",
      "novelty_neighbors": [
        {
          "work": "Lim et al., Time series-derived fractal dimension of CT perfusion in acute ischemic stroke",
          "identifier": "PMID 40824507",
          "relation": "Exact X on the exact 149-case dataset; establishes association and measurement feasibility but contains no trained-model use test."
        },
        {
          "work": "Robben et al., Predicting the tissue outcome of acute ischemic stroke from acute 4D CT perfusion imaging using temporal features and deep learning",
          "identifier": "DOI 10.3389/fnins.2022.1009654; PMCID PMC9672821",
          "relation": "Compares raw concentration-time and residue-curve networks and inspects correlations between learned features and conventional maps, but does not measure or erase Higuchi fractal dimension."
        },
        {
          "work": "van Os et al., Integrating regional perfusion CT information to improve prediction of infarction after stroke",
          "identifier": "PMID 32501132; PMCID PMC7922756",
          "relation": "Shows that local spatial context improves tissue-outcome prediction beyond single-voxel perfusion values; it uses conventional maps rather than temporal fractal structure or a model-use intervention."
        }
      ],
      "novelty_delta": "The exact ISLES'24 fractal biomarker has been validated as an association, but the proposed study asks the missing causal model-behavior question: does selective removal of that descriptor from a raw temporal encoder move final-infarct predictions beyond matched flow and curve moments?",
      "why_not_done": "NEW_CAPABILITY: the public release of all 149 raw four-dimensional ISLES'24 scans with registered follow-up infarct masks, followed by the 2025 exact-dataset fractal measurement, makes a reproducible use test newly practical.",
      "existing_assets": "Approximately 99 GB official archive with raw CTP and registered final masks; a published exact-dataset Higuchi recipe; raw-time-series model designs from DOI 10.3389/fnins.2022.1009654; standard concept-direction and paired-output controls.",
      "smallest_decisive_experiment": "Use a 30-case subset cached slice-wise. Train a shallow causal 2D+time U-Net on center-stratified patches, with 20 training, 5 validation, and 5 untouched cases; require validation AUC at least 0.70 within Tmax>6 s tissue and prediction volume above zero in at least 4/5 test cases. Decode X from the frozen temporal features, erase its cross-validated linear direction at four doses, and compare 20 random orthogonal directions plus X-preserving jitter. Primary readout: paired probability change in held-out perfusion-deficit voxels matched in CBF deciles and curve area. Compute envelope: one Colab GPU session, at most 12 GPU-hours and 25 GB staged data; no new annotation.",
      "standing_confounds_addressed": "Patient-level splitting prevents voxel leakage. CBF-decile and curve-moment matching test whether X merely renames flow or bolus magnitude. Frame-drop and synthetic-noise arms test temporal sampling and noise sensitivity; random directions test nonspecific feature deletion. The small model is a mechanistic probe, not a competitive benchmark claim. Linear erasure may remove correlated temporal features, so the conclusion remains dependence on an X-associated representation.",
      "alternative_explanations": [
        "X is a nonlinear re-encoding of CBF; primary matching and residualized X test incremental use but cannot prove complete independence.",
        "X tracks scanner noise or frame count; noise-injection and frame-drop shams test this and may reveal a technical rather than physiological use mechanism.",
        "Any encoder-direction deletion harms output; orthogonal directions matched for activation variance provide the selectivity comparison."
      ],
      "anticipated_negative": "Decisive for this architecture only if X is decodable, the model passes the frozen AUC/coverage gates, and positive-control directions alter output; otherwise it is sensitivity-limited.",
      "cross_domain": {
        "borrowed_construct": "Fractal time-series analysis from nonlinear dynamics, where scale-dependent path roughness summarizes structure that is not captured by a single amplitude or period.",
        "measurement_it_implies": "Voxelwise Higuchi fractal dimension over the contrast-time curve, plus selective erasure of its representation after controlling conventional curve moments.",
        "what_changes_if_dropped": "The experiment becomes an unconstrained temporal-feature probe; the exact, falsifiable X and the primary paper on the same dataset disappear."
      },
      "remaining_legwork": "One day to reproduce X on five downloaded scans; one session for the small raw-time model and erasure; full-cohort or second-family replication would be a successor.",
      "design_template": "representation-erasure",
      "entry_point_2_requirements": "Measurement: Higuchi temporal fractal dimension. Confused artifacts: CBF, curve area, temporal sampling, and noise; CBF/moment matching plus frame/noise shams address them.",
      "scores": {
        "clarity": {"value": 4, "why": "The feature and erasure are explicit, though linear concept isolation remains imperfect."},
        "identifiability": {"value": 3, "why": "Controls separate several ordinary curve statistics, but X remains correlated with flow and noise."},
        "medical_relevance": {"value": 3, "why": "A deconvolution-free signal could improve robustness, but this small probe does not establish clinical superiority."},
        "interest": {"value": 5, "why": "A network reading the fractal roughness of a contrast heartbeat is mechanistically surprising and grounded in an exact-dataset result."},
        "prior_legwork": {"value": 5, "why": "The exact feature has already been computed on all 149 cases and raw temporal architectures exist."},
        "feasibility": {"value": 4, "why": "The X keystone is inspected true and the decisive probe uses a staged 30-case subset in one session."},
        "data_readiness": {"value": 4, "why": "Public and exact, but the archive is large and requires staged download."},
        "evaluation_readiness": {"value": 3, "why": "AUC, paired deltas, and erasure shams are ready; representation selectivity is custom."},
        "negative_result_value": {"value": 3, "why": "A gated null rules out the mechanism for one temporal architecture, not raw-CTP models generally."},
        "novelty_confidence": {"value": 4, "why": "The exact X paper and two closest model families were inspected; none contains a use intervention, and the keystone is true."},
        "regret": {"value": 4, "why": "The biomarker paper has already completed the expensive measurement legwork, leaving one experiment to convert association into a model-behavior result."}
      },
      "priority_score": 3.8,
      "unverified_claims": [
        "the published Higuchi procedure reproduces from available methodological detail",
        "a small raw-time model passes the frozen performance gate",
        "fractal dimension is linearly decodable from its temporal encoder",
        "erasure can preserve the listed curve properties",
        "novelty outside the targeted neighbors"
      ],
      "plain_pitch": "A contrast bolus passing through brain tissue leaves a short brightness trace over time. A recent study on these exact public scans found that the trace's multiscale roughness—a mathematical quantity called fractal dimension—separates healthy, threatened, and later-infarcted tissue. This experiment asks whether a prediction model actually uses that roughness; if selectively erasing its internal representation changes forecasts after ordinary blood flow, curve size, and scanner noise are controlled, it does."
    },
    {
      "id": "isles24-scout-005-c08",
      "parent_ids": [],
      "track": "wide",
      "entry_point": 2,
      "title": "Delay is not dispersion",
      "question": "Is a raw-CT-perfusion final-infarct model using bolus dispersion—the width and skew of contrast passage after arrival-time alignment—as a collateral-route signal distinct from simple delay?",
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
        "clarity": {"value": 5, "why": "Delay and dispersion are separately defined, measured, edited, and compared."},
        "identifiability": {"value": 3, "why": "The paired edit isolates dispersion use from delay, but collateral-route attribution remains vulnerable to local arterial-input error."},
        "medical_relevance": {"value": 4, "why": "Distinguishing late arrival from dispersed collateral passage could change interpretation and temporal-augmentation choices for raw-CTP models."},
        "interest": {"value": 5, "why": "The claim that two visually similar late boluses mean different things to a model is mechanistically surprising and clinically legible."},
        "prior_legwork": {"value": 4, "why": "The transport physics, stroke dispersion evidence, collateral relevance, and raw-model architecture all exist."},
        "feasibility": {"value": 3, "why": "Capped because full-bolus capture and stable local dispersion on this release are uninspected."},
        "data_readiness": {"value": 4, "why": "Raw public time series and outcomes are available, though staged download is required."},
        "evaluation_readiness": {"value": 3, "why": "Paired dose-response is direct; transport realism and arterial-input stability need custom gates."},
        "negative_result_value": {"value": 3, "why": "A gated null distinguishes this descriptor from delay for one model but does not cover all raw architectures."},
        "novelty_confidence": {"value": 3, "why": "Three close primary works were searched and the precise intervention was absent; systematic novelty review is still pending."},
        "regret": {"value": 4, "why": "The raw curves already contain the needed distinction, and collapsing both effects into Tmax may be an avoidable modeling error."}
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
      "plain_pitch": "Contrast can reach threatened brain late, but it can also arrive spread out after taking many winding routes; those are different physical effects. This study holds arrival time and total contrast fixed, then narrows only the spread of the curve and compares that with an equally large pure time shift. If the model reacts specifically to narrowing, it is reading bolus dispersion rather than merely a late arrival—although a separate dataset would still be needed to prove that the model interprets dispersion as collateral blood flow."
    }
  ],
  "dropped": [
    {
      "question": "[topology / percolation] Is the model using the persistence lifetime of connected Tmax islands as a tipping-point signal that threatened tissue has become one spanning cluster?",
      "why": "Dropped as a near-duplicate of isles24-scout-002-c08 ('Has the deficit percolated?'); changing connected components to persistent homology does not change the scientific estimand enough to survive the duplicate and homogenization checks."
    },
    {
      "question": "[information theory] Is the model using cross-hemispheric compression distance between perfusion fields as a code-length measure of abnormality?",
      "why": "Dropped because the compression score is not a physician-legible mechanism and selective intervention on code length without changing lesion geometry or intensity was not credibly specified; it would die on IDENTIFIABILITY_FAILURE."
    },
    {
      "question": "[fluid mechanics / watershed bifurcation] Is the model using the angle between the local perfusion gradient and atlas arterial-territory boundaries to forecast where infarct growth stops?",
      "why": "Dropped because atlas boundaries, collateral anatomy, and the perfusion gradient co-vary; no public patient-specific territorial ground truth or intervention separates them, repeating the failure of idea-020 and idea-038."
    },
    {
      "question": "[signal detection theory] Is the model using clipped plateaus at the maximum value of a released perfusion map as an ordinal alarm code rather than as quantitative physiology?",
      "why": "Dropped pending a direct value census: neither the official papers nor the inspected release description verifies that the maps contain a common cap or plateau. Without that image-computable keystone, the question is premature and would amount to inventing a dataset artifact."
    },
    {
      "question": "[control theory / observability] Is the model using the spatial disagreement between CTA vessel arrival and CTP delay ridges as a sensor-synchronization error signal?",
      "why": "Dropped because CTA is single-phase and separately acquired, so vessel visibility, bolus phase, registration, and physiology cannot be separated in this cohort; it dies like the motion and site-signature candidates on IDENTIFIABILITY_FAILURE."
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

