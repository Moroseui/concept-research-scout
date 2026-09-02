You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/047
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

## 2026-08-24 - Probe 023 review ruling (round 2: REVISE, three Phase-C blockers)

Operator ruling: Phase S execution AUTHORIZED with the current run.py -- the
reviewer confirms Phase S is contract-faithful and all blocking findings
(B1 lesion filename, B2 compute plan, B3 missing secondary metrics) are
confined to Phase C, which is already locked behind the contract amendment
and fresh approval. B1-B3, the NaN-background finiteness ambiguity, and the
NCCT-location correction MUST be resolved before the Phase-C approval is
granted. Review rounds preserved in git.

Design note: the one-revision cap on probe-build review is provisionally too
tight relative to debate max_rounds=3; queue a configurable
probe_review.max_revisions knob with an ambiguity-escalation rule. B1/B3 are
agent-resolvable and go back through probe-build at amendment time; B2 and
the finiteness ambiguity are operator decisions.

## 2026-08-24 - Contract 023 amendment (Phase S -> Phase C gates)

Phase S completed on Colab (bundle on results/probe-023-4a46713d1b81,
simulation sha256 59069fa9...): 52/60 candidates eligible; the frozen
lexicographic rule selected N=20 patients/stratum, M=100 voxels/cell,
maximum CI width 0.15. Amendment applied deterministically via the new
amend-contract subcommand; no agent involvement. Prior approval is stale
by design; fresh approval required after the finiteness and NCCT clause
edits below.

Design requirement (queued, 2b-adjacent): an operator interrogation channel.
At any point the operator can put a question or new information to the
system about a specific artifact (verdict, contract, probe code, debate
position) and receive a justification or proposed revision as a reviewable
artifact -- generalizing the reconcile stage shape. Must answer/propose,
never silently edit; human gate on any resulting change. 2b issue-based
gates are the natural transport.

Clause rulings at amendment (probe_review.md N2 + NCCT finding): (1) the
finiteness gate is scoped to analyzed voxels -- nonfinite values outside the
analysis region are permitted, excluded, and counted, harmonizing grid_gate
with the invalidating-failure class; (2) required_inputs now includes the
rawdata NCCT, which the official release tree places under rawdata only --
the feasibility memo claim of a "registered NCCT" in derivatives is
corrected forward here, not edited; (3) brain_and_mirror_gate references the
rawdata NCCT on the common grid. probe-build must state the exact
extraction set in the probe README.

## 2026-08-25 - External review round 4 intake + 023 Phase-C execution receipt

Round-4 repo audit (ChatGPT, deep-research; evidence/external_reviews/
2026-08-25_round4_repo_audit.pdf) registered. Adopted: amended freeze
(science frozen; deterministic transport/validator fixes permitted with
synthetic-fixture tests); contract-declared result interface replacing the
004-era validator ontology; completion single-sourced via bundle-complete;
launcher must satisfy probe-declared dependencies (--phase-s-dir guard);
per-phase output dirs; state.json as materialized view never authority;
receipts inside run_agent; fail-closed git sync; privilege separation before
autonomy; meta-loop emits schema-validated proposals only, zero write
credentials; EXPLANATION vs CHANGE_PROPOSAL interrogation receipts; category
budgets over daily caps; reseeding before quotas; validated-reviewer-yield
telemetry; generation backpressure; prospective-only third charter. Elo
deferral endorsed.

Execution receipt, 023 Phase C attempt 1 (2026-08-25T00:54Z): committed
launcher invoked run.py --phase C with data-dir/archive/record on Drive but
WITHOUT --phase-s-dir; approval gate PASSED on blob 349af5ad, then run.py
refused with exit 2 before touching any data. Partial bundle (Phase-S
outputs + Phase-C provenance carrying the exact argv) pushed to
results/probe-023-349af5ad0b3e as the honest record. Archive and extracted
subset persist on Drive; rerun re-pays digests and census only. Root cause:
generator omitted the round-3-added dependency; fixed generically this
commit.

## 2026-08-25 - Round-4 checkpoint evaluation: dispositions

Reviewer verdict: proceed to 2a; immediates correctly targeted; do not
redesign. Fixed this commit: librarian.yml fail-closed rescue (plus an
invariant test scanning every workflow for swallowed rebases); _digest_path
fail-local for named charters (global-digest leak class closed, matching the
portfolio-brief fix); author-family label stripped from probe_review with a
content-only instruction -- recorded as label blinding only, since two-family
structural opposition makes true author blinding impossible. Routed to 2a:
registry-declared upstream-bundle dependencies retire the launcher run.py
string inspection; probe-spec-declared terminal statuses retire the
POSITIVE/NEGATIVE_PATTERN literals in bundle_complete; execution receipts
move inside run_agent; state.json as materialized view + registry.yaml per
the round-4 schema.

## 2026-08-25 - 023 Phase C attempt 2: exit 5, archive census 0 cases -- root cause and directive

Execution receipt: take-2 run (with --phase-s-dir) passed the approval gate
on blob 349af5ad, verified the Phase-S hash, completed both archive digest
passes, then FAILED loudly at the census: run.py line 229 globs
sub-strokecase*_ses-*_space-ncct_cbf.nii* but the archive contains ZERO
strokecase members. Bundle with archive_manifest.csv (2983 members) pushed
at 2026-08-25T02:00:48Z.

Ground truth from the archive manifest itself, one full case:
  train/derivatives/sub-stroke0001/ses-01/perfusion-maps/sub-stroke0001_ses-01_space-ncct_cbf.nii.gz (+cbv, mtt, tmax)
  train/derivatives/sub-stroke0001/ses-02/sub-stroke0001_ses-02_space-ncct_lesion-msk.nii.gz
  train/raw_data/sub-stroke0001/ses-01/sub-stroke0001_ses-01_ncct.nii.gz
Counts: 149 cbf, 149 rawdata NCCT (cohort = 149, settled from the payload);
150 lesion-msk rows for 149 cases -- one extra/duplicate exists and must be
named, not silently absorbed.

Correction (forward, append-only): round-2 review finding B1 and the
operator both verified filenames against the Zenodo record DESCRIPTION
(sub-strokecaseNNNN..., rawdata/). The payload uses sub-strokeNNNN and
raw_data/. Lesson: the archive member manifest outranks dataset
documentation; filename claims verify against payload, never prose.

Directive for the probe-code revision: derive case discovery from observed
archive members (tolerate sub-stroke\d+ and sub-strokecase\d+; handle
raw_data and rawdata); surface the 150th lesion row explicitly in
schema_census.csv and route it through exclusions.csv with a reason; change
nothing else -- the contract, gates, thresholds, and analysis are untouched
and the standing approval remains valid.

## 2026-08-25 - 023 attempts 3-4: Drive FUSE mount crash + Zenodo version-drift hazard

Attempt-3 receipt (02:35Z bundle): the Colab Drive mount died mid-session
(Transport endpoint is not connected). Three symptoms, one cause: extraction
find limped; run.py correctly exit-3d on the invisible extracted dir; and
the staging pin cell, seeing RECORD_JSON as missing, silently re-resolved
the concept to a NEWER child record (17652035) published since our
download -- old bytes, new record, a checksum failure waiting to happen.
Lesson: a pin that can re-resolve at runtime is not a pin. Fixed in the
generator: --staging-record declares the immutable child at packaging time;
existing pins are never silently re-resolved; drift is healed toward the
declaration with a loud warning. Take 4 declares record 16813698 (md5
36ae28b9... matches the held archive); run.py checksum gate arbitrates
definitively.

## 2026-08-25 - 023 take 5: exit 5 (census 0) -- third Drive-FUSE casualty; local-SSD strategy adopted

Take-5 receipt: gate passed on 349af5ad, tolerant census still found 0 cases,
and the session transport never landed a bundle. Third failure localized to
the same component: the 894-file extracted tree on the Drive FUSE mount
(attempt-3 transport-endpoint death; take-5 zero-visibility; same-session
repo-dir loss). Ruling: heavy inputs localize to session SSD -- one bounded
FUSE read copies the archive local; extraction, digests, and census run on
local disk with a fail-loud extraction floor (>=800 files) so a broken tree
can never reach the census again. Outputs/checkpoints remain on Drive.
Driver polish: clone cell cds to /content before rm -rf (same-session rerun
cwd death).

## 2026-08-25 - Round-5 whole-2a review: intake and dispositions

Verdict accepted: approve architecture, fix semantics before consumers.
All five verified defects fixed in 2a-4 (tombstone parity; binding artifact
deps + launcher-as-DAG-edge + pre-run pin staleness + bundle uniqueness;
approval-bound terminal authority; fail-closed contract interface with
containment; receipt provenance restored with configured/effective family).
Coverage-honest verify commands + --require-all; source fingerprints;
honest nulls; AST suite hygiene; CI gates both runners. Deferred per the
reviewer own P1 gates, queued: structured core return (A7), stage-outcome
records (A8), immutable role maps (A10), ledger event ids (A12), forensic
failure checkpoints (A13), override-matrix telemetry, multi-axis diversity
stats. Pushback recorded: the ZIP-based 023 merge hazard dissolved under a
real git merge (performed first, frozen driver preserved byte-identical);
reviewer full-suite timeout was environmental. Merge order adopted:
023 record-result -> frozen-023 hash check -> merge 2a -> author 023
registry + driver_spec -> shadow soak -> read-only consumer flip -> 2b.

## 2026-08-25 - Round-5.5 re-review: intake and closeout (2a-5)

Adopted and shipped, actions 1-8 + 13 + the charter-hardening test:
CI now enforces state-verify --require-all and registry-validate over a
fully materialized 44-idea corpus; registry validation is schema-strict
and fail-closed (closed key sets, type guards, path containment -- a typo
like dependz_on can no longer silently drop a dependency); a pinned node
with a MISSING current contract is STALE, never COMPLETE; COMPLETE is
validation-aware (invalid bundles surface as RESULT_PRESENT); approve-probe
now binds registry_sha256 prospectively; git SHA is computed fresh per
receipt (tool versions stay cached); a receipt-write failure after a
successful invocation fails closed; a numbered idea directory without its
card fails closed; AST hygiene extended to top-level symbols and duplicate
dict keys -- and caught a real pre-existing duplicate (keystone_status) on
first run. Deferred on the reviewer own gates: structured RunResult (A9,
pre-2b), ROLE_BOUND role freezing (A10, pre-consumer-flip), node-addressed
launcher + driver_spec (A11/A12, with post-023 registry work), workflow
helper factoring (A14, cleanup). Adopted for 023: append-only
REGISTRY_RATIFIED retrospective binding; the historical approval is never
rewritten.
## 2026-08-25 - 023 take 6 receipt + staging second-opinion intake (take 7 v2)

Take-6, two layers: (1) the in-flight ~85% run died to a Colab VM recycle
(bare gate line -- a killed VM cannot print FAIL); no defect. (2) The fresh
VM Drive->local copy was size-exact (99022114670) but md5-wrong; run.py
exit-4d correctly. Classified as suspected DriveFS/FUSE read-path
corruption (mechanism not asserted); the stored Drive master is presumed
good from its historical gate pass and is NOT judged through the suspect
path.
External staging review (archived): adopted in full. Kept: generator-level
change, verify-before-extract, one bounded retry, loud refusal, regression
asserts. Changed per review: checksum resolved by exact archive filename;
missing record md5 is a driver-configuration error (fail closed); .part
transfer with atomic promotion; neutral corruption wording; FUSE-mediated
"Drive master arbitration" REMOVED (a suspect witness cannot acquit
itself) -- replaced by classified stop FUSE_LOCALIZATION_INTEGRITY_FAILURE
with origin_direct pre-authorized as the next sanctioned attempt.
Queued to driver_spec (post-023): drive_api_cache as preferred transport
(Drive stays the cache, FUSE leaves the input path), largest_local_scratch
working-volume policy, and a governed driver-revise route so operational
incidents flow to agent-proposed, cross-family-reviewed spec revisions
instead of external patches.

## 2026-08-26 - 023 take 7: FUSE casualty #7; pre-authorized origin_direct pivot executed

Take-7 receipt: on a brand-fresh VM, minutes old, the very first sequential
read of the archive died with OSError 107 (Transport endpoint is not
connected) inside shutil.copyfile -- the loud variant of the read-path
failure, on the simplest possible access pattern. Seven casualties now span
deep trees, empty views, pin re-resolution, silent size-exact corruption,
and outright transport death across four fresh VMs. Threshold met under the
recorded pre-authorization and the external staging review ruling: the big
input leaves FUSE entirely. Take 8 = origin_direct, now a declared
generator mode (--staging-mode): pin, record JSON, and archive all come
directly from the immutable Zenodo record to local scratch (16-way aria2c,
.part -> md5 -> atomic promote, one retry, classified
ORIGIN_DOWNLOAD_INTEGRITY_FAILURE stop). drive_fuse_cache remains available
but transitional; drive_api_cache stays the driver_spec target. The Drive
mount retains only small-file duties (Phase-S read, checkpoints, outputs).

## 2026-08-26 - 023 exit 8: pre-registered unit contingency executed; amendment directive

Take-8 receipt: staging fully solved (aria2c 14 min, checksum and census
passed); the probe stopped at its first scientific act per contract clause
66 -- CBV units are documented nowhere: zero JSON sidecars among the
archive 2,983 members, empty NIfTI descrip fields, and every dataset
descriptor (Zenodo record page, TU/e portal, challenge paper) lists
modalities without units; the icobrain-cva chain implies the convention
but states none. The contract said stop for amendment before outcomes are
read, and it did.

DIRECTIVE for the next probe-build round (amendment authorized, option B,
human gate retained): amend clause 66 so the sole unit-dependent rule
becomes unit-free -- vessel exclusion = voxels with CBV above the
per-patient 98th percentile of finite positive CBV in the map -- recording
in the clause WHY (the payload evidence above) and noting that under the
conventional scale this targets approximately the vessel fraction the
8 mL/100 g cap intended. Update kill-code 104 to mark the unit-failure
contingency executed and retired. Clause 72 is already unit-robust and
must not change. In run.py: implement the percentile exclusion; retire
confirm_cbv_units into a RECORDED finding (identity.json gains
units_documented: false with the evidence summary); change nothing else.
The amendment changes the contract blob: the standing approval goes stale
by design and re-approval follows human review of the diff.

## 2026-08-26 - 023 take 9: checkpoint-identity guard fired correctly; output dirs now blob-scoped

Take-9 receipt: gate passed on the amended blob 468974a7, staging and census
passed silently, and run.py refused at the checkpoint store: the shared
Drive dir 023_C still held take-8 phase_c_cache pinned to the OLD blob
349af5ad and old run.py hash. Fail-closed cache-poisoning prevention
working as designed -- a checkpoint written under one contract/code may
never be consumed under another. Driver fix (one line): OUTPUT_DIR is now
blob-scoped ({idea}_{phase}_{blob12}), mirroring the results-branch scheme,
so each contract era gets a pristine cache and console; superseded dirs
remain as untouched evidence. No probe or contract change; approval stands.

## 2026-08-26 - Pre-registered adjudication for the inf-ratio edge (committed before outcomes are seen)

During the take-10 map pass, two RuntimeWarning classes were observed:
all-NaN neighborhood windows (handled by design: excluded voxels, counted
per case in the checkpoint exclusions record) and overflow in the
rcbf/rcbv division (tiny positive mirror denominators pass valid_den, so
isolated infinite ratios can be admitted to stratum membership, where the
screen is only ratio > 0). Per-case selective repair is FORBIDDEN: the code
is deterministic and uniform, and mixed-provenance case sets are exactly
what the checkpoint identity mechanism prevents.
Pre-registered plan: (1) take 11 completes untouched; its bundle is the
primary result under the approved code. (2) A one-line finiteness
tightening (stratum admission additionally requires finite rcbf and rcbv)
is routed through probe-build with cross-family review, and the map pass
recomputes under the new identity. (3) Interpretation cites BOTH runs: if
they agree, immateriality is demonstrated and the primary stands with the
robustness check noted; if they diverge, the revised run is canonical and
the divergence is reported as a finding. This criterion is committed before
any stratum outcome has been inspected.

## 2026-08-26 - 023 take 10: truncated extracted member + the Drive-artifact mystery closed

Two findings. First, take-10 origin_direct incidentally settled take-6: the
TRUE Zenodo object is 99,014,629,647 bytes (md5-verified); the Drive-cached
wget artifact was 99,022,114,670 -- ~7.5 MB oversized, a Franken-file from
the record-drift era (wget -c declares fully-retrieved whenever local >=
remote), which is why its md5 could never match. origin_direct fully
vindicated. Second, take-10 receipt: staging verified, census passed, map
pass reached case 21 (sub-stroke0043, 20 cases checkpointed) and died on a
TRUNCATED extracted .nii.gz (gzip EOFError; run.py wrapped it honestly as
exit 13). Root cause class: the extraction 7z exit status was unchecked and
the file-count floor cannot see single-member truncation -- count is not
integrity. Driver fix (both staging modes): extraction is now rc-checked
and quiet; a per-member gzip -t sweep follows; bad members are deleted and
re-extracted individually once; a second failure refuses loudly as
EXTRACTION_INTEGRITY_FAILURE naming the files.

## 2026-08-26 - 023 take 11: SOURCE data defect proven; paired-run plan superseded; dual directive

Take-11 receipt: the integrity sweep worked exactly as designed and proved
the truncation is IN THE ARCHIVE: fresh VM, fresh md5-verified download,
rc-clean extraction, exactly one bad member -- sub-stroke0043 ses-01
space-ncct CBF, the same file that killed take 10 -- which failed gzip -t
AGAIN after targeted re-extraction from the verified archive. The member is
size-typical (7.70 MB) with an invalid gzip stream: corrupted before the
dataset creators archived it. Authority split: the driver guarantees
fidelity to the archive (achieved -- it reproduced the defect twice);
content validity is the contract domain. Driver upgraded: the sweep now
arbitrates via 7z t -- stored-CRC-valid members that fail gzip are
announced as SOURCE_MEMBER_DEFECT and tolerated; only true extraction
infidelity refuses.

SUPERSESSION (before any outcomes were seen): the pre-registered paired-run
plan assumed take 11 completes untouched as primary; it cannot -- case 21
blocks on the source defect under current code. Both revisions therefore
fold into ONE canonical run.

DIRECTIVE for the next probe-build round: (a) a case whose required input
is a source-defective member (unreadable gzip from the verified archive)
routes to exclusions.csv with reason source_corrupt_member naming the file,
and the map pass CONTINUES; the summary and interpretation must surface the
excluded count; (b) stratum admission additionally requires finite rcbf and
rcbv (the pre-registered finiteness tightening). Change nothing else. If
the reviewer judges (a) to require a contract amendment (cohort/selection
language), author the amendment in the same round; otherwise the standing
approval holds. Courtesy task queued: report the defective member upstream
to the ISLES 24 maintainers.

## 2026-08-26 - 023 take 12: COMPLETE map pass; pre-registered mirror gate stop (exit 7) with decision-grade evidence

Take-12 receipt: staging flawless (sweep tolerated the known source defect
live); the label-blind map pass completed 100/100 with sub-stroke0043
excluded per policy (99 computed); the run stopped at the frozen mirror
gate: 21/99 patients meet (registration_error <= 1.0 voxel AND
usable_brain_fraction >= 0.90); floor is 90. Evidence from mirror_qc.csv
(label-blind): registration errors are lattice-quantized (median 1.41,
q75 2.00, max 4.36 voxels) -- clinical positioning, not registration
failure; usable-fraction median 0.856 sits below the 0.90 floor; and
NMAE rises MONOTONICALLY with registration error (0.129 / 0.191 / 0.236 /
0.291 / 0.357 across buckets <=1.0 to >2.5), so displacement measurably
degrades mirror fidelity: the gate is doing real epistemics, not
cleanroom strictness. Threshold relaxation is therefore weakly justified;
the supported-subgroup path risks severity-correlated selection. Live
fork: (A) registration-robust redesign (region-level contralateral
reference; identity coordinate is mirror-free and survives) with new
Phase-S calibration and full re-run, or (B) kill with code
MIRROR_PRECONDITION_UNSUPPORTED and harvest (A) as successor idea.
DECISION DEFERRED to the human gate augmented by advisor input
(2026-08-27 meeting): voxelwise-vs-region reference is a domain call.
No PR opened; results-validate red on a stopped bundle is correct
behavior; the record-result and merge train wait on this fork.
Queue item (operator observation): the interpret stage decodes terminal
results only; pre-registered STOPS should generate their own briefing
artifact (gate context + relevant QC tables) -- a stop-report generator
joins the driver_spec-era work list.

## 2026-08-27 - Design queued: stop-report stage (failure-to-analysis routing)

Operator observation, validated by the 023 arc: three pre-registered stops
each produced decision-grade DATA but no decision-grade BRIEFING; all
forensics were ad hoc. Design: stops route to an interpret-variant stage
producing (1) an EXPLANATION record -- gate context + evidence tables,
citation mandate, inputs mechanically restricted to the label-blind
artifacts the stop certifies -- and optionally (2) a CHANGE_PROPOSAL from
a CLOSED vocabulary mapping to existing pipeline edges: AMEND_CONTRACT,
REVISE_PROBE, REDESIGN, KILL, or ESCALATE_ONLY (explicit deferral, a
first-class output -- the 023 mirror fork is the canonical case where any
machine recommendation would overstep a domain judgment). Explanations are
zero-authority; proposals carry base hashes, cannot modify targets,
re-enter every normal gate, and receive cross-family review. Sequencing:
first consumer of the 2b record envelope -- build it as 2b opening move,
after record-result -> 2a merge -> registry -> driver_spec.

## 2026-08-27 - Operator reframe AND DECISION: 023 goes mirror-free; directive for the amendment round

Reframe (operator-caught): idea 023 claim is the joint CBV/MTT compensation
state AT MATCHED FLOW; hemispheric mirroring is idea 021 ("The healthy
hemisphere is the ruler") and entered 023 only as the operationalization of
matched flow. The exit-7 stop is a verdict on a borrowed ruler, not on the
claim, the signal, or the dataset (QC distributions describe ordinary
clinical positioning; neither clinical software nor models require
voxel-mirror symmetry). mirror_qc.csv is harvested as empirical
feasibility evidence FOR idea 021. The conflation passed agent authorship,
cross-family review, and twelve operator takes; caught at the human gate.

DECISION (human gate, 2026-08-27): mirror-free within-patient flow
matching. DIRECTIVE for the next probe-build round: amend the contract so
matched flow = per-patient CBF percentile bands WITHIN the eroded deficit
region (three fixed bands, 0-33 / 33-67 / 67-100 percentile of finite
deficit CBF; deterministic, label-blind, no external reference). REMOVE
the mirror machinery entirely: mirror construction, registration QC, the
exit-7 gate, and mirror-relative ratios; the region definition (Tmax>6s,
erosion, midline band, per-patient p98 vessel exclusion), the identity
coordinate u = log(CBF*MTT/CBV), the identity-residual gate, per-stratum
coverage floors, and the source-corrupt exclusion policy are UNCHANGED.
Phase S must be recalibrated for the new strata (synthetic planted effects
under percentile binning; same detectability-floor logic). Keep gates
minimal: coverage + identity only; introduce no new reference anatomy.
This de-couples 023 from 021 by construction.

## 2026-08-28 - Meeting outcome: dual-track sprint; HU audit ACTIVATED; clinical-scores secondary pre-registered

Advisor meeting (2026-08-27): system-refinement arc APPROVED, and a signal
read from idea 023 requested within the week -> dual track. The previously
drafted parked/strategic-pause entries were never committed and are
superseded by this plan; the refinement arc proceeds in parallel with a
bounded 023 signal sprint.

ACTIVATED DIRECTIVE (tissue-composition audit, previously drafted as
parked; an outcome-reading run is now scheduled, so it applies): before
take 13, a probe revision adds a label-blind per-bin per-style NCCT HU
audit -- during the map pass record, per case, per flow bin, per style
group, the median and IQR of NCCT attenuation over member voxels, into the
per-case cache and a bin_tissue_audit.csv. No estimator changes, no new
gates, run.py only (contract untouched; standing approval holds through
verify). Pre-registered interpretation rule: HU-balanced styles within
bins -> the compensation reading stands; systematic imbalance -> report as
conditional predictive information WITH a tissue-composition caveat and
design a tissue-normalized successor. Rationale: the retired contralateral
mirror was incidentally the tissue-type normalizer (gray-matter baseline
flow ~2-3x white matter); percentile bins do not restore this.

PRE-REGISTERED SECONDARY (advisor side-interest): after the take-13
outcome read and record-result, a patient-level join of census per-patient
aggregates against the dataset clinical outcome scores (phenotype
ses-02 outcome.csv, mRS/NIHSS-type). Clinical scores are outcome labels
and remain behind the same label-blind until that step; no take-13 scope
change; phenotype files staged separately when needed.

Sequence: audit revision -> verify -> mechanical amend-contract from the
mirror-free Phase-S bundle (status PHASE_S_COMPLETE_REQUIRES_AMENDMENT)
-> approve (new blob) -> package take 13 -> outcome read -> record-result
-> interpret -> signal answer.

## 2026-08-28 - Amender sentinel-quoting tolerance (fail-closed drift, resolved system-side)

The mechanical amend-contract refused on the mirror-free contract: the
agent rewrite left three numeric placeholders unquoted while the amender
demanded the quoted byte-form. Correct refusal, wrong rigidity: the
sentinel format is the amender own interface convention, so the tool (not
the contract) was fixed -- both quotings accepted, exactly-one-total and
single-shot semantics unchanged, tested for both styles. The contract was
never hand-edited.

## 2026-08-28 - 2a-state merged to main (gate disposition + refresh receipt)

The reviewer merge gate -- originally "after 023 record-result," re-scoped
to current-arc resolution -- is receipted as satisfied under the
advisor-approved dual-track plan: take 13 (blob 03d4545fe293) was packaged
and in flight at merge time; its record-result follows on landing and
retro-binds via the queued REGISTRY_RATIFIED design. results-validate.yml
is byte-identical across the merge, so the in-flight take is unaffected.

Refresh merge (main -> 2a-state): one conflict, evidence/decisions.md,
both-appended-at-tail; resolved by union (review-intake entries then the
023 arc entries; nothing dropped). scout.py and tests auto-merged. Both
runners green on the merged tree (152). State corpus re-materialized: 43
of 44 byte-identical, ideas/023/state.json alone updated (five
contract_blob pointers -> 03d4545fe293). state-verify --require-all and
registry-validate green. CI steps (compile incl. orchestrator modules,
doctor, both runners, state invariants) reproduced green pre-push.
Post-merge queue unchanged: 023 registry.yaml + REGISTRY_RATIFIED design,
driver_spec.yaml (operator-driver-patch era ends there), shadow soak,
read-only consumer flip.


## 2026-08-28 - Round-6 post-2a review: intake and dispositions

External review of main @ 2725262 plus the post-2a patch plan. Verdict
accepted: 2a stays merged; the plan is directionally sound; the P1
registry must not be authored until registry semantics and schema
containment are corrected. All findings independently re-verified against
the code before intake; every claim confirmed by direct reading, with one
divergence recorded below.

ACCEPTED P0 (blocks the 023 registry):
(1) Node contract semantics: derive_status stales ANY node whose pinned
contract_hash differs from the current idea contract, before consulting
bundle evidence -- so a historical Phase-S pin goes STALE and Phase-C
BLOCKED. Ruling: node.contract_hash means "the immutable approved
contract version governing this node." A node holding a terminal,
validated bundle is judged against its own pin: an approval record for
that hash must exist, the bundle's recorded executed-contract hash must
equal the pin, and consumed-artifact hashes must verify. Only nodes
without terminal evidence track the current contract for staleness.
Durable historical identity needs no new store: the pins are git blob
hashes, retrievable from the object store; approval + bundle provenance
are the proof.
(2) The plan's depends_on example used a bare list; the shipped schema
requires depends_on: {all_of: [{probe: ...}]}. Plan corrected; schema
syntax is henceforth bound from the validator, like every other value.

ACCEPTED P0/P1 (same patch): close the nested schema before the first
production registry -- schema_version == 1 enforced; produces and
artifact output validated as contained relative paths; nested key sets
(depends_on, all_of, artifacts, launcher, upstream_bundle) closed and
typed; contract_hash format-checked; canonical path normalization before
uniqueness; validation refuses BEFORE any status derivation consumes
registry paths. Reviewer-demonstrated traversal (produces/output with
..) and schema_version: 999 both currently pass -- confirmed in code.

ACCEPTED P1: (a) registry-status CLI omits the bundle validator that the
state-materialize path injects, so a terminal-looking invalid bundle can
print COMPLETE -- all status consumers route through one
validation-aware path; COMPLETE never derives from summary text alone.
(b) The state source fingerprint omits the result-status inputs that
determine registry node statuses -- fold summary/manifest and
consumed-artifact hashes into materialization.sources before
registry-backed state gains consumer authority. (c) approval.stale is
False when the current contract is MISSING -- missing current contract
plus historical approval becomes stale/invalid before the consumer flip.

RATIFICATION MECHANICS (accepted, strengthens the draft): ordering proof
is repository ancestry, not timestamps. REGISTRY_RATIFIED becomes a
dedicated append-only governance-event artifact (not a latest-wins
ledger row) binding idea, registry sha256, approval artifact sha256s,
covered contract hashes, operator decision identity, git commit, and a
stable event id; activation is a human-merged PR (same authority model
as record-result); record-result refuses unless the required
ratification artifact is present and valid in its checked-out tree.
Historical failed C takes stay OUT of the DAG: registry is the
scientific dependency graph; attempts and stops live in
receipts/results/decisions.

SEQUENCING (accepted): structured RunResult + stage-outcome records pull
forward from the 2b batch to land BEFORE stop-report/design-review --
new governance stages will not be built on LAST_RUN mutation and print
semantics. Soak becomes coverage-based (zero state-verify divergence
across the window; clean rematerialization on multiple independent
commits; several real lifecycle mutations across more than one idea; at
least one real registry-backed node transition; one synthetic
hand-edited-state refusal; ROLE_BOUND active) with seven green events as
a floor, not the definition. Advisory coupling confirmed at
approve-time, outcome-neutral; the minimal advisory/event schema lands
before design-review emits production advisories.

DRIVER-SPEC REVISIONS (accepted for P3): the spec references the
approved dataset identity (dataset_ref by hash) rather than restating
record/md5/bytes as a second editable authority; drive_api_cache is
implemented and tested before it may become preferred -- origin_direct
remains the proven heavy-input path; largest_local scratch with a
minimum-free-bytes floor; tool/prerequisite failures become a named
DRIVER_PREREQUISITE_FAILURE stop; staging tests move from
string-presence to executable policy/renderer tests; the audit packet
maps FINAL established incident explanations (e.g., the Drive master was
7.5 MB oversized -- the earlier same-size-corruption working diagnosis
is superseded and must not freeze into policy).

RECORDED WITH NUANCE:
(d) Full-suite certification: the reviewer's environment could not
complete the full runs or reach the public repo. On record here: both
runners green (152) locally on 2725262, and CI success for 2725262,
1f03e59, and 3be88ae confirmed via the Actions API.
(e) Isolated TestDebate: the reviewer's 1-failed reproduction did not
reproduce in this environment (4/4 pass) -- the defect is latent and
order/environment-dependent. The unhygienic mechanism (fixture
sys.path.insert + importlib.reload with rmtree-only teardown, no
sys.modules restoration) is confirmed in the test code and will be fixed
regardless: centralized fixture-import lifecycle plus an
isolated/shuffled selection gate.

TAKE-13 ORDERING RULE (adopted, per reviewer): the record-result path
for take 13 does NOT block on registry work. If a valid bundle lands
before ratification machinery exists, it imports through the existing
approved path and the DAG is ratified retrospectively afterward. Result
identity binding outranks governance ordering.

REVISED NEAR SEQUENCE: R1 registry semantic + schema hardening (with the
counterexample regression: historical-approved S remains COMPLETE while
current-approved C depends on it) -> R2 state-view fixes + test-fixture
hygiene + P2 cleanups (docstring, INVALID_ROW taxonomy note, action
pinning) -> R3 023 registry + PR-gated ancestry-bound REGISTRY_RATIFIED
-> M1 take-13 record-result/interpret whenever the bundle lands -> R4
structured RunResult + stage-outcome records -> driver_spec -> ROLE_BOUND
-> coverage-based soak -> consumer flip -> stop-report -> design-review
-> advisory register -> gate calibration -> 2b remainder -> 2c.


## 2026-08-28 - R1 landed: registry semantic + schema hardening (round-6 P0s)

contract_hash now means the immutable approved contract GOVERNING the
node. Nodes without terminal evidence track the current contract (pin
mismatch = STALE, unchanged). A node holding a terminal result is judged
against its own pin: the pin must be attested (HUMAN_APPROVED_PROBE or a
REGISTRY_RATIFIED row in the new append-only
ideas/NNN/governance_events.jsonl sidecar, v1 schema closed to that one
event), the bundle's provenance.contract_blob must equal it, and the
bundle must validate under that immutable contract -- validate_bundle
gained expected_blob, reading historical contract text from the git
object store; the default (current) import gate is byte-for-byte
unchanged. History no longer goes stale because an amendment moved the
current contract; the review counterexample (historical-approved S stays
COMPLETE while current-approved C depends on it) is a regression test.

Schema closed and contained: schema_version == 1 required; produces,
results_bundle, and artifact outputs must be canonical contained
relative paths; depends_on/all_of/artifacts/launcher/upstream_bundle key
sets closed (legacy upstream_bundle.probe retired); artifact sha256 now
REQUIRED 64-hex -- a binding dependency cannot be unhashed; contract_hash
must be 40-hex. Validation precedes derivation: derive_status raises on
an invalid registry, registry-status exits nonzero, and
terminal_statuses_if_approved / upstream_bundle_requirement refuse
invalid registries outright. One validation-aware status path: the CLI
now injects the same bundle validator as state materialization, and with
no validator a terminal summary is RESULT_PRESENT, never COMPLETE --
COMPLETE is unreachable without validation, everywhere.

Tightening note: a pinless terminal node whose bundle provenance does
not name the current contract is now STALE (previously COMPLETE-able
from summary text alone). Gates: 165/165 both runners (13 new tests),
state-verify --require-all 44/44 byte-identical, registry-validate and
doctor green. Next: R2 (state-view approval-staleness on missing
contract, fingerprint completeness, fixture import hygiene, P2
cleanups), then R3 authors the 023 registry with PR-gated ancestry-bound
ratification. Take-13 record-result remains not blocked on any of this.


## 2026-08-28 - R2 landed: state-view + hygiene pre-flip fixes (round-6 batch)

Approval staleness corrected: an approval whose CURRENT contract is
MISSING is now stale/invalid in materialized state (previously reported
fresh) -- an approved contract that no longer exists is not a fresh
approval. Source fingerprint made complete: when a registry exists,
materialization.sources gains registry_result_inputs -- per-node hashes
of summary.json, provenance.json, and every declared consumed-artifact
file (new experiment_registry.result_input_hashes, deterministic,
containment-guarded) -- so the watermark MOVES whenever a derivable node
status can move. MATERIALIZER_VERSION bumped 2 -> 3 and all 44 state
files re-materialized; the corpus delta is provably one line per file
(the version field), fingerprints and approval flags byte-unchanged for
every current idea (only 004 and 023 hold approvals; both contracts
present, so the staleness fix flips nothing retroactively).

Fixture-import hygiene centralized: Harness.tearDown now purges every
sys.path entry and loaded module rooted in the test's temp dir, and the
two debate tests use a single _import_fixture_scout helper instead of
inline insert+reload -- no later or isolated test can inherit a loader
bound to a deleted repository (the TestDebate order-dependence class
from external review; latent here, fixed regardless). check.yml gains an
isolation canary running the exact reviewer selection
(pytest ::TestDebate) so hermetic selection is CI-enforced.

Supply-chain pins: all six workflows now reference
actions/checkout, setup-python, setup-node by full commit sha (resolved
live from the upstream tags, comment-annotated with the major version);
CI pytest pinned to 9.1.1 to match the gated local runs; a hygiene test
asserts every workflow uses: line is sha-pinned. Taxonomy: ledger gains
TOMBSTONE_STATUS = INVALID_ROW, deliberately excluded from settable
STATUSES (repair-tool-only), with the load() exclusion referencing the
constant. The _digest_path docstring now states the fail-local behavior
the code always had.

Gates: 171/171 both runners (6 new tests); isolated-class runs hermetic
(TestDebate, R1, R2, StateMaterializer selections each pass alone);
state-verify --require-all 44/44 byte-identical under materializer v3;
registry-validate and doctor green. Patch verified by applying to a
pristine worktree of origin/main: applied tracked tree is git-identical
to the gated commit. Next: review packet (fresh main ZIP + R3 design:
draft 023 registry, REGISTRY_RATIFIED artifact spec, PR-gated
ancestry-bound ratification flow, and the four discretionary R1
decisions listed for ratify-or-object) BEFORE R3 lands. Take-13
record-result remains not blocked on any of this.


## 2026-08-28 - M1-pre landed: two-source bundle governance identity (F1)

Root cause, verified against the real Phase-S bundle on
results/probe-023-0e223c82f9eb: validate_bundle check #2 read
provenance.json:contract_blob, but the frozen driver's gate() has always
recorded the governing identity in resolved_config.json
(contract_blob + approval_blob); run.py's provenance.json is
run-environment provenance and never carried the field. Check #2 (E1,
2026-08-15) had therefore only ever been exercised by fixtures; on
landing, take-13's results-validate would have refused its own valid
bundle and no record-result PR would have opened.

Fix, applied identically in validate_bundle and in the registry status
path (_bundle_governing_blob, replacing the single-file reader): the
bundle's governing identity is provenance.json:contract_blob when
present, else resolved_config.json:contract_blob; if BOTH files carry a
value they must agree, and disagreement is a hard failure surfaced as
such (import refusal / node STALE), never a silent pick. Neither-source
still refuses exactly as before. resolved_config.json is a
contract-required output written by the frozen driver's own gate, so
reading the identity the run actually recorded strengthens evidence; no
gate is loosened, and bundle files are never mutated post-run.
Consequently, materialization.sources.registry_result_inputs (R2, v3,
not yet materialized anywhere -- zero live registries) now also
fingerprints resolved_config.json per node, since it co-determines
derived status; no corpus state bytes change and no version bump is
required for a pre-first-use field addition.

Shipped ahead of the pending external review round per the adopted
ordering rule (result-identity binding outranks governance ordering);
the review packet discloses the finding, the remedy, and this
possibility verbatim, and asks for retrospective ratification (Q2).
Gates: 176/176 both runners (5 new tests, including a fixture shaped
like the real S/take-13 bundle passing the import gate, a
disagreement hard-fail, and the registry-side COMPLETE via
resolved_config identity); isolated selections hermetic; state-verify
--require-all 44/44 byte-identical; registry-validate and doctor green;
patch verified git-identical against a pristine origin/main worktree.


## 2026-08-28 - Round-7 review intake + R3a landed (consolidation-close corrections)

Round-7 verdict accepted: architecture green, complexity yellow;
consolidate before expanding. Rulings recorded: D1, D2, D5, D6 and the
F1 fix RATIFIED; the historical-import doctrine refinement, ancestry
rule, and marker-untouchability CONFIRMED; results_v2-<blob12> accepted
as a migration convention with the future per-node
probes/NNN/results/<node>/<blob>/ layout noted for post-023 work. The
utility reframe is adopted as the standing success metric: decisive,
evidence-backed answers per hour of operator attention, with the
reviewer's metric table queued for the measurement window. Generation
automation moves to explicit maintenance mode in the P10 slot
(transition receipts on saturation entry/exit, no nightly same-fact
commits). Roadmap sequence adopted as ordered; blackboard arbiter,
meta-loop, third charter, and tournament selection stay deferred.
Structured RunResult gains consumed/produced artifact refs and the
common event envelope lands before any P5-P8 stage emits events. CSV
dual-write removal and the global scout-target charter bypass are
queued for the legacy-retirement window; coverage/durations as a
periodic diagnostic job and REVAMP.md reconciliation queued as P2.

R3a lands the three P0s the reviewer set for closing this round:

(1) Fixture-import isolation, mechanism-level. Honest reproduction
record: the reviewer's failing ordering did NOT reproduce here -- full
suite green under both pytest 9.1.1 and a dep-complete 9.0.2 venv.
The attempt instead surfaced a real adjacent finding: in a lean
environment three tests silently REQUIRED nbformat/jsonschema and read
as code failures (exactly the packages the reviewer's sandbox could not
install); they now skip explicitly with named reasons. The isolation
mechanism is hardened regardless, per standing rule for latent
environment-dependent defects: Harness temp dirs are resolved at
creation; the purge compares realpaths on both sides and invalidates
import caches; _import_fixture_scout no longer relies on path-priority
reload -- it evicts the fixture-sensitive namespace (scout, state_view,
experiment_registry, ledger), invalidates caches, imports fresh, and
self-checks the resolved origin loudly. The reviewer's sequence
(root import first, then fixture import) is codified as a regression,
and the CI canary is now the mixed three-class selection
(TestDebate + TestR2StateAndHygiene + TestM1PreGovernanceIdentity).

(2) Ratification binding schema finalized BEFORE the first live row
(D3 amendment). governance_events.jsonl v1 rows now carry structured
bindings -- a non-empty list of closed {contract_blob, approval_commit,
approval_sha256} mappings -- replacing the parallel
approvals/contract_hashes arrays that could not mechanically encode
which approval attested which contract. git_commit is renamed
base_commit (the authoring HEAD; a row cannot embed the sha of the
commit that will contain it), format-checked 7-40 hex. Attestation
reads binding contract_blobs. D4 is accepted as conditioned: a
syntactically valid row is necessary, never sufficient -- the R3b
ratify CLI must mechanically verify each binding (the marker bytes at
approval_commit hash to approval_sha256 AND that marker text binds the
contract_blob) with forgery regressions, and the ratification PR binds
the source results-branch commit and the imported bundle manifest
sha256 alongside the bindings.

(3) F2 resolved as ruled: a NARROW legacy rule, never generic
infrastructure. _HISTORICAL_RESULT_INTERFACES keys on
(governing blob, bundle phase); its single entry is the executed
Phase-S interface under 0e223c82f9eb (resolved_config,
simulation_operating_characteristics.csv, simulation_summary.json,
summary, provenance, environment.txt, run_log.txt), marked removable
after 023 ratifies. The historical contract text is not consulted on
that path (its top-level required_outputs describe the study-terminal
bundle); identity, provenance, and hashing checks bind unchanged, and
the phase-sanity gate accepts the table-keyed single-letter phase.
Regressions: the real-S-shaped bundle validates cleanly under its own
blob; an unlisted blob gets no skip; a terminal Phase-C bundle missing
a required output still hard-fails. Future contracts get phase-scoped
result_interfaces instead of table growth.

Gates: 180/180 on BOTH runners AND under the pytest 9.0.2 venv;
isolated and mixed-class selections hermetic; state-verify
--require-all 44/44 byte-identical; registry-validate and doctor green;
patch verified git-identical against a pristine origin/main worktree.
Next: R3b -- the real 023 registry, ratify-registry CLI with mechanical
binding verification and the three import bindings, record-result
ancestry refusal, and the OR-ratified extension of
terminal_statuses_if_approved.


## 2026-08-30 - Take-13 landing: two gate findings, M2-pre, operator import

Take 13 (Phase C, contract 03d4545fe293) completed 2026-08-28 07:28 UTC
and pushed results/probe-023-03d4545fe293 (tip eb6083e) with status
NEGATIVE_PATTERN, 99/100 census cases analyzed, all integrity gates
green, CI widths 0.039-0.065 against the frozen 0.15 bound. The
branch-side landing automation went red and no record-result PR opened.
Two distinct causes, both diagnosed before import:

FINDING (branch vintage of F1): push-triggered workflows execute the
pushed branch's own snapshot of the code, and the take-13 launcher was
packaged before M1-pre -- the branch's frozen validator read
provenance.json for a contract_blob the driver has always written to
resolved_config.json, refused the valid bundle, and the auto-PR step
never ran. The fix has been live on main since M1-pre; it cannot reach
a branch's frozen copy. The automation failed CLOSED: main untouched.
Old PR #1 (the idea-004 import, 2026-08-16) is unrelated; its ref
merely persists.

FINDING F3 (caught in operator-side rehearsal, before any command ran
on the operator machine): the frozen contract's single top-level
required_outputs list conflates BOTH phases' interfaces -- it names the
two Phase-S simulation artifacts, which the Phase-C bundle rightly does
not contain (it consumed the S csv via --phase-s-dir and re-verified it
by sha; summary.simulation_output_sha256 equals the contract's frozen
pin). No single-phase bundle can satisfy the list literally; this is
the exact mirror of F2 and the same class round-7 ruled on.

M2-PRE (landed with this import): the legacy result-interface table now
keys on the GOVERNING blob -- pinned or current alike -- and gains the
(03d4545fe293, 'C') entry: the contract's required_outputs minus the
two simulation artifacts. Narrow, blob+phase-bound, no generic
phase-skip rule, removable after 023 ratifies; regression proves an
unlisted blob still requires the full list. 181/181 both runners;
state-verify 44/44; the staged real bundle validates and record-result
was rehearsed end-to-end in a pristine worktree before handoff.

IMPORT RULING: the bundle totals 1030.1 MB, of which 1029.6 MB is
phase_c_cache/ per-case resume checkpoints -- operational scratch, not
claim-bearing output. The import carries the scientific bundle
byte-verbatim WITHOUT phase_c_cache (19 files); the checkpoints remain
verbatim on the results branch and on Drive as evidence.

AUTHORITY NOTE: the record-result PR exists to route AUTOMATED imports
through a human; with the branch-side automation failed closed, the
operator executes the import and push directly, satisfying the same
human-authority requirement by construction. Queued: flag F3 to the
external reviewer next round; future contracts get phase-scoped
result_interfaces (round-7 direction); P3 adds a launcher-vintage rule
so results branches carry current gate code or main-side revalidation;
R3b ratifies this import retrospectively per the adopted ordering rule.
Next: interpret stage, PAUSED transition per the pre-registered
negative_pattern ruling, the pre-registered clinical-outcome join, and
the signal writeup.


## 2026-08-30 - Correction: post-import state refresh missed in runbook

The take-13 import runbook omitted a step: record-result's PROBED
scrutiny event changes idea 023's ledger inputs, so the committed
ideas/023/state.json was no longer a faithful materialization and
state-verify --require-all correctly went red on main (one CI run).
This was a runbook/rehearsal gap on the assistant side -- the rehearsal
enumerated the import's side-effect files but did not re-run
state-verify on the post-import tree. No data issue; the invariant
refused hand-stale state exactly as designed (the R2 fingerprint moved:
event_count 6 -> 7, scrutiny DEBATED -> PROBED). Remedy: re-run
state-materialize --idea 23, commit the regenerated view, and push;
verified 44/44 byte-identical and 181/181 on both runners before
handoff. Standing runbook rule adopted: any operation that appends
ledger events (record-result, status transitions) is followed by
state-materialize + state-verify before push.


## 2026-08-30 - Interpret stage gains a phone-dispatch surface

interpret-build (cross-family adversarial interpretation: one family
writes interpretation.md under the hard citation mandate, the other
resolves every citation against the analysis files and checks claim
bounds, one revision maximum, verdict JSON) was laptop-only. A
workflow_dispatch surface (.github/workflows/interpret.yml) now exposes
it from the GitHub mobile app, mirroring the actioner's execution
pattern exactly: pinned actions, agent CLIs + existing secrets,
deterministic tests BEFORE any agent runs, scout-bot identity,
SCOUT_CI, serialized under the scout-cycle concurrency group, and a
fail-closed rebase-then-push that also preserves FAILED partial output
(interpret-build commits every leg). The stage moves no scientific
authority by itself: it produces interpretation.md /
interpret_review.md / decision.md for human ratification; the PAUSED
transition and any successor-contract proposal remain operator acts.
Gates: 181/181 both runners including the workflow sha-pin hygiene
scan; patch verified git-identical against a pristine origin/main
worktree.

## 2026-08-30 - Interpret run: codex auth rotation incident + resume capability

First dispatch of the interpret workflow: the generator leg (claude,
498s, exit ok) produced interpretation.md and decision.md -- committed
and preserved. The review leg (codex) failed in 3.5 seconds with
exit_class error: wall-to-wall 401s ending in refresh_token_reused
("Your refresh token has already been used"). Root cause: Codex refresh
tokens are SINGLE-USE; any local CLI refresh invalidates the chain the
CODEX_AUTH_JSON Actions secret snapshots, and the quiet nightlies let
the stale secret go unnoticed. The harness behaved exactly as designed:
partial output committed, receipts written for both legs, workflow red,
nothing ratified.

Ops rule adopted: export ~/.codex/auth.json to the CODEX_AUTH_JSON
secret IMMEDIATELY BEFORE dispatching any agent workflow, and avoid
local codex use until the run completes. Queued for the P10 ops batch:
a named auth-preflight step (fail fast with CODEX_AUTH_EXPIRED before
any leg runs, instead of a 3.9k-line 401 log).

M3-pre landed: interpret-build gains --resume-review (and the workflow
a matching boolean input) -- when a preserved round-1 interpretation
exists, the run skips the generator and proceeds directly to the
adversarial review; it refuses when no interpretation exists.
Rationale: an infrastructure failure must not burn a good leg, and a
regenerated round-1 would silently replace the exact text under review.
Two regressions prove the skip and the refusal; 183/183 both runners;
patch verified git-identical against a pristine origin/main worktree.
The round-1 interpretation remains UNRATIFIED pending the cross-family
review it was always owed.


## 2026-08-30 - Round-8 review intake: interaction is the frontier

Full-system audit absorbed (robustness, interaction, scientific
utility, path forward; literature-grounded against AI Scientist,
Co-Scientist, Agent Laboratory, Robin, ScientistOne, AutoGen,
LangGraph, multi-agent-debate and injection-security work). Verdict:
green scientific integrity, green-to-yellow failure containment,
yellow automation and maintainability, clearly yellow human<->system
interaction -- the system's biggest remaining weakness is not safety,
ideation, or execution; it is interaction. Standing goal reformulated
and adopted verbatim as the project's articulation: a human-directed
research instrument in which strong models do most of the cognitive
and mechanical work required to turn vague scientific possibilities
into falsifiable, evidence-traceable conclusions, while deterministic
infrastructure preserves identity, provenance, authority and
reproducibility.

CORRECTIONS RECORDED. (1) Milestone phrasing: idea 023 is the first
complete experimental-and-interpretive lifecycle; its final governance
transition awaits operator ratification (decision.md carries stale
pre-review prose; state remains SHORTLISTED while the decision
recommends PAUSE) -- our "first complete idea lifecycle" wording was
premature. (2) The 2026-08-30 manual state-refresh runbook rule is
itself exception-handling: authority-mutating commands must own their
derived-state transaction (append -> materialize -> verify -> succeed);
the manual rule is superseded by that design. (3) Our draft
note-blocking formulation ("every stage refuses on any open note") was
too broad -- an accidental denial-of-service; notes bind to explicitly
named response boundaries. (4) Packet said 181 tests; the reviewed ZIP
carries 183 (post-resume-review chronology), noted for the record.

Q0 RATIFIED: M2-pre as a narrow temporary compatibility mechanism with
an explicit retirement destination; the 1 GB phase_c_cache exclusion
(resume scratch is not claim-bearing output); the operator-executed
import as an exceptional equivalent human-authority path -- future
operator imports must emit the same structured authority receipt as the
automated route; the phone-dispatch interpret workflow. A1 resolved:
branch-vintage is eliminated by MAIN-OWNED revalidation
(repository_dispatch: current main as executable code, exact results
commit as data) -- never by copying orchestration into result branches.

ADOPTED ARCHITECTURAL RULINGS. Three-register input taxonomy becomes a
primitive: integrity-invalid -> hard refuse; well-formed but
semantically inconsistent -> dissent-and-clarify; ordinary -> proceed.
Division of labor: deterministic machinery answers "may this happen",
models answer "does this make scientific sense and what are we
missing", the human answers "which judgment do we authorize"; models
never waive integrity rules, hard code never adjudicates scientific
ambiguity a frontier model reasons about better. Semantic anomalies
route to an opposing-family clarification ("valid but conflicts with
X; interpretations A/B; which did you intend?"). ratify-interpretation
becomes a deterministic authority primitive (verify interpretation/
review/verdict/decision/contract/bundle identities, then one
transaction: ratification event + authorized status transition +
materialize + verify); lifecycle status is machine-derived from the
authority act, science prose is never rewritten. One symmetric
note/advisory schema on the R4 event envelope -- no pre-R4 interaction
file formats; responses required at named boundaries; a valid response
includes evidence-backed rebuttal; advisories never dictate the human,
notes never dictate the model. Adversarial reads of operator acts:
judgment-rich only (ratifications, overrides, kill/revive against
machine advice, approving over open advisories), returning
NO_MATERIAL_DISSENT or DISSENT{finding,evidence,why}; dissent is never
veto; health metric = material dissent that changed a decision / all
reads, plus operator minutes per useful catch; a reviewer producing no
useful dissent gets respecified. Interpretation gains a first-class
operator objection: distinct authored object, one bounded operator
reconsideration even after the machine revision is consumed, and the
agent may defend the original with citations. confer: read-only,
bounded, receipted, artifact-hash-bound single exchange, landed after
the substrate; conclusions promoted to notes, transcripts never enter
core context. Minority-dissent lifecycle telemetry (raised -> adopted/
rebutted/overruled -> vindicated/falsified) preferred over agreement
rate; never majority-vote truth. decisions.md remains the append-only
human authority log but STOPS being whole-file prompt context; R4
derives applicable-decision context per idea/charter/system. Security
doctrine: prompts explicitly separate TRUSTED INSTRUCTIONS from
UNTRUSTED EVIDENCE (results, transcripts, note bodies, external text);
evidence text is never executable instruction; judgment stages reading
untrusted text run least-privilege; citations and cross-family review
are scientific defenses, not sandboxes.

MULTISTEP (Q1): R3b proves the real S->C registry before any schema
expansion; phase-scoped result_interfaces enter NEW contracts (the
contract, not the registry, owns what counts as a valid result);
launcher upstream becomes an inputs LIST beside P3's node-addressed
driver; results converge on probes/NNN/results/<node>/<contract-blob>/
replacing results_v2 semantics; no any_of, quorums, dynamic branching,
or per-node contract documents absent demonstrated need -- the six-blob
amendment chain proved historical pinning works.

Q8 AUDIT TABLE ADOPTED with its classifications and retirements:
keep (baseline-charter fallback, tombstones, two-source governance,
contract-owned exclusions like sub-stroke0043); retire on trigger
(historical interface table after 023 ratifies + phase-scoped
interfaces; M/B legacy path after migration; phase-s source sniff and
results_v2 assumptions at P3; --resume-review absorbed into R4 generic
resumable stage outcomes; drive_fuse at P3; CSV dual-write and global
scout-target in the legacy window; whole-log prompt injection at R4;
manual codex refresh -> P10 preflight now, durable credential model
later; global-cycle roles -> ROLE_BOUND before flip). Transitional-debt
convention adopted: constructs marked # TRANSITIONAL with owner and
retire_when, indexed in a CI-checked transitional_debt.yaml -- a
transitional construct outliving its trigger fails CI. Verdict on the
discipline: mostly general mechanisms, close enough to the boundary
that mechanical retirement now matters.

REVISED SEQUENCE ADOPTED: M4 ratify-interpretation + transactional
authority mutations (immediate; closes 023 governance) -> R3b real 023
registry + ratification -> R4 typed RunResult + common event envelope +
generic resumption identity + decisions-context derivation -> P3
driver_spec + launcher inputs list + main-owned dispatch revalidation +
node-addressed results -> ROLE_BOUND -> derived-state soak + consumer
flip -> interaction substrate (symmetric notes/advisories, operator
reconsideration, confer) -> stop-report (successor-question generator
only; never amends the current experiment) -> design-review -> gate
calibration -> measured-need expansion. Blackboard arbiter, meta-loop,
third charter, tournaments remain deferred: the human plus this
repository already is the blackboard; first make it interactive and
typed. Consolidate-before-expanding remains binding. scout.py 2c split
after R4/P3 interfaces stabilize.


## 2026-08-30 - M4 landed: ratify-interpretation + transactional record-result

The round-8 authority primitive. ratify-interpretation IDEA --status S
verifies six identities -- interpretation.md, interpret_review.md, its
APPROVE verdict (ratification never bypasses the machine review;
operator reconsideration remains a distinct future path), decision.md,
the governing contract blob, and the validated results bundle -- then
performs ONE transaction: a ledger INTERPRETATION_RATIFIED event
carrying the authorized status transition plus all six identity hashes
(the existing append-only ledger is the substrate; no new event format
before R4) -> digest -> re-materialize the idea's state -> state-verify
-> single commit. Lifecycle status is machine-derived from the human
authority act; science prose is never rewritten. record-result gained
the same transactional tail (scrutiny event -> digest -> materialize ->
verify -> commit), so the 2026-08-30 manual state-refresh runbook rule
is now superseded by construction for both current authority mutators,
exactly as round-8 ruled. Shared _result_bundle_for helper replaces the
inline discovery in interpret-build. Four regressions: the full happy
transaction (event fields, hashes, PAUSED state, verify-clean, commit
message), refusal without machine APPROVE (no event lands), refusal on
unknown status and missing documents, and record-result owning its
state transaction end-to-end. Gates: 187/187 both runners (also re-run
green on the pristine-applied tree), state-verify 44/44, registry-
validate and doctor green; patch verified git-identical against a
pristine origin/main worktree. Next operator act: ratify idea 023 ->
PAUSED, closing the first experimental-and-interpretive lifecycle's
governance per the pre-registered negative_pattern ruling.


## 2026-08-30 - R5a landed: the Research Card (derived view)

Answering the operator's standing need -- "the idea is in one place, but
nothing describes results, position, and connections together" -- and
the context-window motivation behind it: ideas/NNN/CARD.md is a
deterministic derived VIEW (card-materialize IDEA; --check verifies
byte-identity, mirroring the state invariant) rendering an idea's
scattered authorities onto one compact, human- and model-readable page:
identity and ledger position; the question; DECLARED-vs-DERIVED status
with drift flagged and never silently reconciled (idea 023's card
immediately surfaced its own stale keystone_status: NOT_INSPECTED
against the ratified NEGATIVE -> PAUSED -- the first machine-generated
candidate operator update); the full contract-blob lineage recovered
from approval-marker history (023 renders its six-blob amendment
chain); experiment position and bundle identity; headline per-stratum
results verbatim from summary.json (every number already
citation-checked by the cross-family review); interpretation/review/
decision hashes and the ratification row; connections via a new
OPTIONAL related_ideas list on the existing idea_card.json (no new
authority, no new event format -- pure consolidation-doctrine view);
and document pointers. The card is the designated compact context
object for the coming confer primitive. ideas/023/CARD.md is committed
and check-verified cross-machine. Three regressions (lineage ordering,
drift flag, determinism, stale-byte refusal, related-ideas rendering);
190/190 both runners, also green on the pristine-applied tree;
state-verify 44/44; patch git-identical against pristine origin/main.
Next: R5b confer-v0 (read-only, receipted, trusted/untrusted prompt
separation, advisory-only suggestions) under a TRANSITIONAL marker with
a resequencing disclosure addendum to the external reviewer.

## 2026-08-30 - R5b landed: confer-v0, transitional-debt ledger, driving framework

confer IDEA "question" -- the read-only half of the interaction layer,
pulled forward under the ship-with-disclosure class (addendum authored
for the external reviewer; see below). Round-8 rulings implemented
verbatim: bounded single exchange; receipted via run_agent; READ-ONLY
(scope-guarded to ideas/, produces only ideas/NNN/confer/qXXXX.md plus
prompt, grounding, log); hash-grounded (qXXXX_grounding.json binds the
question to the exact sha256 of every context artifact -- the research
card and the idea's claim-bearing documents); three-register behavior
mandated in the prompt (ordinary -> answer; premise conflicts evidence
-> PREMISE CHECK with citations then best faithful answer, rebuttal
expected; unresolvable -> say so and name the resolving artifact);
citation mandate; SUGGESTED UPDATES rendered advisory-only, applied by
the operator through normal commands, never amendments to closed
experiments. First implementation of the round-8 security doctrine:
TRUSTED INSTRUCTIONS strictly precede UNTRUSTED EVIDENCE, evidence is
data, instruction-shaped evidence text is reported, never obeyed.
Family: explicit roles.confer override, else the interpret family
(claude -- codex credentials not required for confer). Phone surface:
.github/workflows/confer.yml (pinned, tests-first, fail-closed push).

transitional_debt.yaml bootstrapped with ten entries spanning the
round-8 audit table (confer_v0_pre_substrate, historical_result_
interfaces, resume_review_flag markered in code; seven more ledgered
with locations and triggers). TestTransitionalDebt enforces the
convention bidirectionally: a markered entry without its code marker,
or an in-code TRANSITIONAL token missing from the ledger, fails CI.
Retirement is now state, not intention.

DRIVING FRAMEWORK codified (operator+assistant, this evening's cadence
and standing policy): three concurrent lanes -- A build (patch ritual:
pristine-proof, both runners, echo, operator box), B external review
(async, batched, never blocking A except class 1), C live exercise
(real use on idea 023's lineage doubling as organic soak evidence).
Review-trigger classes: (1) design-before-code for authority semantics,
gate meaning, schemas, sequence changes; (2) ship-with-disclosure for
urgent landing-path fixes (M1-pre precedent) and disclosed
resequencings; (3) batch closeout after each coherent 2-4-patch
cluster or before first live use of new AUTHORITY machinery; (4) no
review for views, tests, docs, neutral refactors -- logged and audited
at the next batch. Tuesday night is a patch freeze ahead of the
Wednesday advisor meeting. Gates: 194/194 both runners (also green on
the pristine-applied tree); state-verify 44/44; patch git-identical
against pristine origin/main.

## 2026-08-30 - R5c landed: reviewed confer with role rotation + enforced docs

Operator directions, adopted verbatim. (1) The adversarial two-model
pattern is the accuracy mechanism, so confer answers do not run
unopposed: a second, opposing-family leg reviews five meat-level
properties -- thesis correctness against the evidence, OVERVIEW
fidelity (simplification must never become distortion; over- and
under-statement are findings), citation resolution, premise-check
appropriateness, claim bounds -- returning CONCUR or CONTEST; CONTEST
triggers ONE bounded revision, a second CONTEST stops for the
operator. (2) Clarity leads: the draft leg's trusted block mandates a
plain-language ## OVERVIEW any reader can understand -- carrying no
claim the ## DETAILS below do not support -- before the cited
reasoning; the reviewer deliberates on the OVERARCHING answer, not
line-by-line prose. (3) Diversity: the families SWAP roles across
exchanges (exchange 1 drafts with pair[0] and reviews with pair[1];
exchange 2 swaps; explicit roles.confer/confer_review override), so
neither family owns drafting or reviewing; cross-family holds in every
exchange, and the codex credential-freshness rule now applies to every
confer dispatch. Every leg committed and receipted; the final answer
carries the reviewer's verdict in-tree.

Documentation becomes state, not intention: README.md gains a complete
Operator Command Reference (all 35 CLI subcommands indexed; detailed
entries for confer, card-materialize, ratify-interpretation,
transactional record-result, interpret-build --resume-review; a phone-
surfaces section with the credential rule), and TestDocsHygiene fails
CI whenever any registered subcommand is missing from the README.
Driving framework gains rule 5: patches touching the operator surface
update the command reference in the same patch. Gates: 197/197 both
runners (green again on the pristine-applied tree, including the
family-swap and docs-coverage regressions); state-verify 44/44; patch
git-identical against pristine origin/main.

## 2026-08-30 - R5d landed: durable codex auth for Actions

The ChatGPT OAuth chain rotates its refresh token on every use, and an
Actions runner that rotates discards the successor when it dies -- so
the CODEX_AUTH_JSON snapshot was structurally a coin flip: any agent
run could silently consume the chain and strand the next one (the
2026-08-30 interpret incident was this class). Remedy, landing ahead of
the P10 durable-credential item: all six agent workflows (scout-cycle,
idea-pipeline, actioner, librarian, interpret, confer) now prefer an
OPENAI_API_KEY repository secret -- API keys do not rotate on use and
live until revoked -- with the OAuth snapshot kept as automatic
fallback when the key is absent. The auth step logs which mode it took;
scout-cycle's dry-run guard preserved; every workflow YAML-validated;
CI and local codex now hold fully independent credentials, retiring
the "no local codex during runs / re-export before dispatch" rule
whenever the key is set (the rule remains documented for fallback
mode). README phone-surfaces section updated per docs rule 5. Cost
note: API-key legs bill the platform account per token (CI review legs
are short); the ChatGPT subscription continues to cover local use.
Gates: 197/197 both runners, green again on the pristine-applied tree;
patch git-identical against pristine origin/main.

## 2026-08-30 - R5e landed: confer never vaporizes evidence

The first live confer dispatch failed with ZERO repository trace -- no
commits, no receipts, no logs. Root of the silence (root of the failure
itself pending the Actions log): run_agent raises on agent failure, and
cmd_confer, unlike interpret_build, did not wrap its legs in a
catch-and-commit-partial handler -- any leg-level raise discarded the
grounding, prompt, receipt, and log with the runner. Two invariants
land: (1) the question, grounding sidecar, and prompt are COMMITTED
before any agent leg runs ("question registered"), so a run that
reaches the command can never again disappear without trace and a
zero-commit failure now cleanly indicts the pre-command workflow steps;
(2) the entire leg loop is wrapped so ANY raise -- SystemExit or
otherwise -- commits partial evidence (receipts included) before
propagating, mirroring and strengthening the interpret pattern.
Regression proves both: a raising leg leaves the registration commit
and a FAILED(type) commit behind. 198/198 both runners, green again on
the pristine-applied tree; state-verify 44/44; patch git-identical
against pristine origin/main. Diagnosis of the actual trigger proceeds
from the Actions step log; the next dispatch self-documents either way.

## 2026-09-01 - R5f: codex API-key auth materialized (confer incident #2 closed)

R5e's evidence invariants worked on first contact: the re-dispatched
confer left the question-registered commit, the FAILED(SystemExit)
commit, the receipt (codex draft leg, error, 15.1s, model None -- also
documenting that AGENTS.toml's rotation pair orders codex first, so
odd exchanges draft with codex and claude reviews; cross-family holds),
and the verbatim log: 401 Unauthorized "Missing bearer or basic
authentication in header" at api.openai.com. Diagnosis: the API-key
branch correctly fired (the secret is set), but this codex CLI version
does not read OPENAI_API_KEY from the environment for auth -- with no
auth.json present it selected the API transport and sent no
credentials. Remedy across all six agent workflows: the API-key branch
now writes the key into codex's own auth store ({"OPENAI_API_KEY":
...} in ~/.codex/auth.json, chmod 600) and sets preferred_auth_method
= "apikey" in ~/.codex/config.toml; the OAuth-snapshot fallback branch
is unchanged. Queued for round 9 (operator direction): a question
funnel -- not every confer deserves the full adversarial treatment;
tiering simple/factual asks to a lighter path with escalation rules,
plus an open-source survey of routing/cascade precedents. All
workflows YAML-validated; 198/198; patch git-identical against
pristine origin/main.

## 2026-09-01 - Round-9 intake + S1 landed (round-9 immediates)

Round-9 full audit absorbed. Verdict: sound and increasingly useful;
not yet bloated but at the inflection where breadth must stop outrunning
production exercise. Standing strategic rule adopted verbatim: make what
already exists become unavoidable, generic, live-tested and boring; and
the architecture budget: no new persistent mechanism until the
preceding one has been exercised on at least one live scientific
lifecycle.

DISPOSITIONS RECEIVED: all six R5 patches RATIFIED (R5a with a
generality caveat -- the card's headline renderer knows 023-specific
fields; R5e strongly). Confer's artifact shape does not prejudice R4.
The five-property review mandate gains a SIXTH property. The credential
fork is DECIDED: (A) a non-rotating API credential for CI, subscription
OAuth strictly local/manual; the self-refreshing-PAT loop is rejected
as an endpoint (privilege increase, serialization-dependent mutable
chain) and acceptable only as an explicitly transitional mechanism if
cost blocks A. Auth preflight pulled forward from P10 to NOW. The
confer FUNNEL design is received and adopted for the post-R4 slot:
deterministic four tiers (local no-LLM; light single-model; reviewed
draft+review; authority-adjacent reviewed+operator-gate) with
auto-escalation on numerical claims, source contradictions, PREMISE
CHECK, SUGGESTED UPDATES, interpretation proposals, governance
consequences, unresolved evidence, or missing citation support;
learned routing (RouteLLM-class) only after real routing outcomes
accumulate; routes become receipted outcomes, hence post-R4.

ADOPTED ARCHITECTURE RULINGS: AiiDA's two-graph lesson shapes R4 --
data provenance (dataset -> run -> bundle -> interpretation) and
logical/governance provenance (approval -> contract -> registry ->
authorization; review -> ratification -> transition; note ->
acknowledgment) stay separate typed structures linked by ids/hashes,
never one giant ledger schema. The generic trusted/untrusted evidence
envelope extends confer's doctrine to ALL stage prompts (queued
immediately after R3b, with an injection-fixture regression). The
adversarial pre-read of operator acts is scoped to consequential acts
only (approvals, amendments, ratifications, overrides, registry
ratification, high-severity acknowledgments) with catch-rate
measurement. Two-A is declared merged-not-consolidated; the reviewer's
twelve-item checklist is adopted verbatim as the soak's acceptance
bar. driver_spec sketch, ten driver acceptance tests, and
drive_api_cache endpoint absorbed into P3. scout.py modularization by
authority boundary queued post-R4/P3. Roadmap sequence adopted: R3b ->
R4 (typed outcomes + envelope) -> multi-input launcher + phase-scoped
result_interfaces -> driver_spec -> ROLE_BOUND -> soak/flip ->
notes/advisories -> funnel -> scoped decisions context -> split ->
stop-report/design-review/calibration; arbiter, meta-loop, third
charter deferred until measured need.

S1 LANDED (the four smallest immediates; R3b is next and separate):
(1) load_agent_config fails CLOSED with AGENT_CONFIG_INVALID when
AGENTS.toml exists but cannot parse -- configuration corruption never
again degrades into default role identity; absence still means
defaults. (2) Every agent workflow gains a Codex auth preflight
BEFORE any scientific leg, with the reviewer's named failures:
CODEX_CREDENTIAL_MISSING (no key, no snapshot -> hard stop),
CODEX_CREDENTIAL_REJECTED (401 on a zero-cost models probe -> hard
stop), inconclusive HTTP -> proceed with notice. (3) run_agent's
receipt classifier names in-run credential/billing failures from the
leg log (CODEX_ACCOUNT_UNFUNDED, CODEX_CREDENTIAL_REJECTED prefixes on
exit_detail) -- a red leg is now diagnosable from the repository
alone, completing the arc the three confer failures began. (4) The
confer review gains property six: question coverage -- every part of
the operator's question answered or declared unanswerable, unresolved
assumptions named, never papered over (README updated per docs rule).
(5) The 023-specific card headline renderer is ledgered:
TRANSITIONAL(card_headline_023_fields), retiring when headline fields
become contract/registry-declared. Two regressions (config fail-closed
incl. absent-vs-malformed split; unfunded receipt naming end-to-end
through run_agent). Gates: 200/200 both runners, green again on the
pristine-applied tree; state-verify 44/44; all workflows
YAML-validated; patch git-identical against pristine origin/main.

OPERATOR ACTION PER THE RATIFIED FORK: fund the platform API balance
(~$10); the subscription OAuth remains local-only. Next build: R3b --
the production 023 registry and its ratification, the first live
exercise of the registry substrate. Tuesday night remains the patch
freeze before the Wednesday advisor meeting.

## 2026-09-01 - R3b landed: the production 023 registry and its ratification

The registry substrate carries real science for the first time.
ideas/023/registry.yaml declares the two-node DAG: phase_s pinned to
its historical contract 0e223c82f9eb..., phase_c to the current
03d4545fe293..., joined by an all_of edge, a BINDING artifact
dependency on the Phase-S operating-characteristics csv at its exact
sha (59069fa9...), and the launcher upstream_bundle plumbing bound to
that edge. Governance rows gain the round-7/8 IMPORT BINDINGS: a
closed `imports` list ({node, source_commit, manifest_sha256, bundle})
validated alongside bindings. Ratified rows now confer terminal
authority (ratified_binds_current extends the A3 interim: marker-bound
OR a well-formed REGISTRY_RATIFIED event binding the current bytes).

record-result gains the historical lane: --expected-blob validates the
bundle under its own immutable contract, --source-commit triggers the
ANCESTRY refusal (the source snapshot must carry the approval marker
binding that pin) and the VERBATIM check (every staged byte must equal
the source tree, compared blob-by-blob), the destination becomes
results_v2-<blob12>, and EVERY import now writes the structured
authority receipt round-9 required (<dest>.import.json: source commit,
byte-manifest sha256, file count).

ratify-registry IDEA --operator NAME is the authority transaction:
bindings are DERIVED from approval-marker history and each is
mechanically verified (marker bytes at the bound commit hash to the
recorded sha AND textually bind the pin); every pinned node's import
receipt is re-verified (manifest recomputed, ancestry re-checked);
refusals name their forgery class. Then one transaction: append the
REGISTRY_RATIFIED event -> registry-validate -> derive with the
validator injected, EVERY node required COMPLETE -> state-materialize
-> state-verify -> card re-render -> single commit.

The rehearsal (throwaway worktree, real repo, real S branch) executed
the whole arc: S bundle imported verbatim from 5aa8b5a1... (manifest
7248cd0f8551, receipt written), then ratification produced bindings
03d4545fe293@1ad4885 (sha 325703c888df) and 0e223c82f9eb@68057ec (sha
012e114d67ea), the phase_s import binding, and BOTH NODES DERIVED
COMPLETE -- each validated under its own immutable contract, the exact
counterexample class round 5 demanded, now production truth. The
rehearsal also CAUGHT a real regression before it shipped: with the S
import present, bundle discovery's alphabetical glob preferred the
historical directory; discovery now prefers the current-era fixed name
until P3's node-addressed layout (regression added). Pre-import, the
committed card honestly shows both nodes STALE (phase_c's declared
input missing) -- the operator's import + ratification visibly heal
the DAG. The F2/F3 historical-interface table's retirement trigger is
now armed (retires with phase-scoped result_interfaces, next batch).
Six new regressions (transaction end-to-end incl. OR-ratified;
pin-outside-lineage; receipt-manifest and ancestry forgeries;
historical lane incl. verbatim refusal; discovery preference) plus the
governance-schema imports coverage. Gates: 205/205 both runners;
state-verify and card --check green on BOTH the build tree and the
pristine-applied tree; patch git-identical against pristine
origin/main.


## 2026-09-01 - Operator ruling: idea-045 claim-identity gate (revise-in-place)

The 045 debate ended REVISE with an explicit human unblock: decide
whether stripping the "decisively refuses / lineage-terminal" negative
changes the candidate's identity under the claim-identity rule --
revise in place if not, supersede with a new registration if so.
RULING: identity preserved; the revision is ratified in place. The
question ("did tissue composition create idea-023's sign reversal?")
is unchanged; what moved is the epistemic ceiling of one answer arm --
nulls become sensitivity-limited because no external bound exists on
HU-by-outcome effect modification -- and a card must not be forced
into a new identity for becoming more honest about what a null can
mean. The surviving decisive arm is correctly scoped: a reversal that
persists under adjustment decisively shows attenuation imbalance does
not explain it. deliverable_original preserves the pre-revision claim
for lineage, per convention.

Governance observation recorded for round 10: the pipeline's
auto-revise executed the rewrite BEFORE this human gate was formally
resolved -- benign here (the rewrite implemented exactly the debate's
conditions and this ruling ratifies it), but the ordering inverts the
unblock's letter. This is a live specimen for the reconsideration /
notes-substrate design: machine revisions that a debate conditions on
a human ruling should be able to WAIT on that ruling. Also observed:
the idea-pipeline stages did not advance the ledger scrutiny ladder
(045 remains SCOUTED after keystone/critique/debate); queued as a
small fix. Idea 045 is now cleared to proceed to probe-plan ->
human contract approval -> probe-build under existing machinery.

## 2026-09-01 - S2: contract-authoritative bundle interfaces (045 import unblocked)

Live exercise caught the seam within hours of R3b: idea 045's first
bundle -- complete per its APPROVED contract -- was refused by the
import gate because validate_bundle force-unioned provenance.json into
every declared interface, a 023-era assumption encoded in scout.py:
exactly the class round-9 ordered retired ("required result files
should be phase/node-scoped in the contract, not encoded in
compatibility tables"). Executed narrowly: when the governing contract
declares required_outputs, that set plus summary.json IS the core;
governing identity remains enforced by the two-source check against
whichever carrier the bundle includes (the identity reader now
tolerates an absent carrier instead of misreporting it as unparseable
json -- previously unreachable because the old core masked it). Legacy
bundles with no declared interface keep the full historical core; the
F2/F3 historical table and M/B paths are untouched. Regression covers
both directions (declared interface without provenance validates;
undeclared legacy still demands it). First fix attempt over-forced
resolved_config.json and broke four legacy fixtures -- caught by the
suite before packaging reached the operator; recorded as the gates
working on their author. Also recorded: the operator's first
record-result 45 invocation hung >60s with no output and no commits;
unexplained (validation provably returns instantly), watching the
rerun; strace next if it recurs. 206/206 both runners, green on the
pristine-applied tree; state-verify 45/45; patch git-identical against
pristine origin/main. Rerun sequence: record-result 45 -> interpret.

## 2026-09-01 - S2b: phase optional under declared interfaces; 045's first result is in hand

Second head of the S2 hydra, caught by the very next import attempt:
summary `phase` is an importer-side convention no contract clause ever
required, and idea 045's contract-faithful bundle omitted it. Same
ruling applied: under a declared interface, phase is optional; when
present it must still be a single letter; legacy/no-interface bundles
unchanged. record-result messaging tolerates the absence. Proven
end-to-end before shipping: the probe was executed deterministically in
the build sandbox against the frozen repo inputs and the resulting
bundle validates to [] under this patch. Regression covers
absent-phase-passes and malformed-phase-still-fails. 206/206 both
runners, green on the pristine-applied tree; patch git-identical.

And the sandbox execution surfaced the scientific news a turn early:
045's outcome-blind feasibility gate returns NEGATIVE_PATTERN --
condition number 38.89 against the frozen <=30 bound (singular values
14.09 to 0.36), fewer than 20 distinct imbalance values in at least
one band (integer-quantized audit medians collapse Q1-Q4 differences
onto a small grid), and a patient row exceeding the 0.20 leverage
bound. Coherent diagnosis: the frozen band-by-imbalance interaction
design is fragile on the covariate's real geometry. Per the contract's
own words this mandates SPECIFICATION REVISION (centering/
standardization, pooled-slope reduction, or rank transform -- each a
new pre-registered spec) and is expressly NOT evidence against tissue
composition or the parent association. Zero outcome values were read;
the reserved cases remain untouched. Import and adversarial
interpretation proceed next; R10 gains a third interface-hydra note:
summary conventions (idea_id/phase/status) should be stated where
contract and probe authors can see them.

## 2026-09-01 - S2c: governing-blob-aware bundle discovery (v2 lane unblocked)

Pre-registered stopgap (disclosed to the reviewer in R10 Q3 before
building): with idea 045's v2 respec approved, a second same-idea
bundle becomes imminent and the fixed-name discovery preference would
ground interpret/confer/card on the stale v1 result. Discovery now
prefers the candidate whose recorded governing blob (two-source read,
tolerant of absent carriers) equals the CURRENT contract -- the
current-era result by definition; the legacy fixed name remains the
fallback, then newest; 023's behavior is unchanged (its results_v2
carries the current blob). Regression proves the current-blob bundle
beats the legacy name. P3's node-addressed layout retires this whole
mechanism (transitional_debt: results_v2_fixed_naming). 207/207 both
runners, green on the pristine-applied tree; state-verify 45/45; patch
git-identical against pristine origin/main. The v2 contract
(pooled-slope reduction, blob 5615afea1e2f, contract_version 2)
awaits the operator's read and approval; sequence thereafter:
probe-build -> verify -> run to results_v3 -> record-result ->
interpret -> ratify.

## 2026-09-01 - Round-10 intake + P0 authority closeout landed

Round-10 verdict absorbed: progressing properly, demonstrably more
useful, interaction showing real scientific value; the danger has
shifted from can-it-be-trusted to can-the-core-stay-comprehensible.
Standing instruction adopted: fix the two authority defects, land R4
and the common interfaces, consolidate the monolith -- then let the
agents become more flexible, not the orchestration more complicated.

DISPOSITIONS RECEIVED: S1 ratified. R3b architecture and the
legitimate 023 transaction ratified WITH the new P0 (read-time
verification) mandated immediately -- the reviewer forged a
schema-valid REGISTRY_RATIFIED binding (approval_sha256 all-zeros,
commit deadbee) and the system accepted it end to end: write-path
checks were a promise, not an invariant. S2/S2b ratified
(contract-authoritative interfaces correct; no new exception-table
entries; a versioned validator-owned bundle envelope is the durable
home, injected into prompts -- schemas are executable contracts,
prompts are advisory). S2c blessed as an acceptable emergency stopgap
pending node/blob/run addressing. Taxonomy ruled: pause REASON CODES
as fields/events, never statuses; SUPERSEDED accepted only as an
authority act binding successor_id, operator identity, and claim
identities. Consequential-act pre-read moves ahead of stop-report but
AFTER the R4 envelope + minimal advisory event. Auto-revise ruling:
thinking ahead allowed, binding ahead not -- draft lanes fine,
authoritative mutation waits. Registry rollout rule adopted: every new
approved probe gets a registry (one-node skeletons generated
deterministically) -- idea 045 gets one before its next experiment.
Also queued from the audit: ROLE_BOUND spec restated;
REMOTE_ADVANCED_RETRY_REQUIRED preferred over rebase of derived
transactions (eventual); typed RunResult replaces LAST_RUN (R4);
events() ledger API; suite split fast/integration (fixture scaling
declared SOLVED, subprocess cost is the bottleneck); scout.py split by
authority boundary; ARCHITECTURE/DESIGN_HISTORY doc split; narrow the
broad excepts around bundle probing; interaction funnel and
NEEDS_CLARIFICATION taxonomy confirmed for the substrate era; 12-item
consolidation checklist adopted as the closing bar.

P0 AUTHORITY CLOSEOUT LANDED (this patch):
(1) verify_ratification_event(): every REGISTRY_RATIFIED row's claims
are mechanically re-proven at READ time -- registry bytes bound,
marker bytes at each binding's commit hash to the recorded sha AND
textually bind the blob, every import's bundle bytes match the
ratified manifest and its source snapshot carries the approval for
that node's pin. _attested_hashes and ratified_binds_current consume
ONLY mechanically-verified rows; registry-validate re-proves every row
so forged-but-well-formed rows fail loudly; derive_status refuses
derivation on an invalid registry. governance_events.jsonl bytes now
enter materialized-state sources (023 re-materialized; any governance
mutation moves the fingerprint). LIVE ACCEPTANCE: the reviewer's exact
mutation, replayed against the real 023 row in a scratch worktree, now
produces named validate failures, refused status derivation, and a
state-verify error -- while the untouched row still verifies and both
nodes stay COMPLETE. (2) Human-unblock ordering: run revise refuses
under a debate REVISE-with-unblock until the operator acknowledges
(--unblock-ack "one-line ruling", recorded to unblock_ack.txt);
draft-only lanes arrive with R4. (3) GIT_HISTORY_REQUIRED: a failing
git invocation during approval-lineage derivation is a named integrity
refusal, never a silent "(no approval marker history)" that could let
a card rewrite committed truth. (4) Every orchestration git call now
runs through one bounded, traced helper: 30s timeout raises
GIT_COMMAND_TIMEOUT, SCOUT_GIT_TRACE=1 logs per-command durations --
the unexplained record-result stalls get named or localized next time.
Two latent import gaps (top-level time, sys) surfaced by the helper
and fixed. Fixture world upgraded to the stricter reality: attestation
fixtures now MINT real evidence (marker commits with true shas) the
same way production does; three new regressions (the verbatim
reviewer exploit; unblock blocking + ack flow; named history refusal).
210/210 both runners, green on the pristine-applied tree; state-verify
45/45; card 23 --check byte-identical; patch git-identical against
pristine origin/main. Next per the ratified roadmap: 045 registry,
then the attribution contract; R4 after the Wednesday freeze.

## 2026-09-01 - idea 045 registry authored + local-import ancestry lane

Round-10's registry-per-probe rule executed for its first beneficiary:
ideas/045/registry.yaml declares the two sibling outcome-blind
feasibility gates (feasibility_v1 pinned e7071541036a..., NEGATIVE;
feasibility_v2 pinned 5615afea1e2f..., POSITIVE) -- no edge, since v2
was informed by v1's geometry but consumes no artifact from it. One
small mechanism accompanied it: locally executed bundles import
through the normal lane with source_commit null in their authority
receipts, so ratify-registry now falls back to the bundle's FIRST-ADD
commit in main history -- the commit that introduced the bytes, whose
tree must carry the approval binding that pin -- and records that
commit in the governance imports row, where round-10's read-time
verification re-proves it forever after. Regression proves the
recorded ancestry survives verify_ratification_event; a fixture
lesson en route: the template ships the production .gitignore, so
fixtures must add -f bundles exactly as record-result does.
REHEARSED on the real repository: ratify-registry 45 produced
bindings e7071541036a@f40b247 and 5615afea1e2f@fb05835, import
feasibility_v1 <- fe7d30a (manifest 004253540bab), BOTH NODES
COMPLETE each under its own immutable contract, card RATIFIED,
state-verify 45/45. 211/211 both runners on build and
pristine-applied trees; patch git-identical. Operator sequence:
apply, then ratify-registry 45 --operator, then the attribution
contract may be drafted.

## 2026-09-01 - Idea 046 gauntlet + P0b: the unblock guard's first live test failed and is now closed

The 046 pipeline ran overnight: keystone INSPECTED the imported
per_patient table directly (297 rows, 99 unique cases per primary
band), critique and three debate rounds then narrowed the candidate in
the same direction 045's did -- every proposed binary
carrier-versus-diffuse classifier was found to require uncertainty or
repeat-measurement information the dataset cannot supply, so the
deliverable was reduced to a FINITE-POPULATION DESCRIPTIVE
CONTRIBUTION CENSUS: exact signed per-case contributions
c_i = (d_i,band3 - d_i,band2)/99, dominance and Lorenz-style
summaries, all frozen before computation, explicitly an estimator
audit rather than a mechanism test; the clinical rung survives as the
frozen stratifier comparison with honestly re-costed phenotype
acquisition. Verdict REVISE with an explicit HUMAN unblock on claim
identity.

INCIDENT, recorded plainly: the round-10 P0 unblock guard did NOT
fire -- auto-revise executed the rewrite before the ruling, exactly
the ordering the fix was shipped to prevent. Root cause: the guard
covered the CLI door (run stage revise) while the pipeline invokes
revise through _pipeline_stage directly; the live run found the
uncovered path within hours, and the unit test had tested only the
covered one. P0b closes it at both layers: the pipeline call site now
pauses with HUMAN_UNBLOCK_REQUIRED (a green, loud, mutation-free stop
naming the exact follow-up command) and _pipeline_stage's revise entry
refuses outright absent an acknowledgment file; the test fake's
legacy hardcoded unblock filler is env-gated so fixtures mean what
they say; the regression reproduces the live failure end-to-end
through the real pipeline subprocess. 212/212 both runners, green on
the pristine-applied tree, patch git-identical.

OPERATOR RULING (046 claim identity, revise-in-place): identity
preserved; the revision is ratified in place. The registered question
-- which observed cases contribute most to the band-2/3 reversal, and
do high-contribution cases differ on a short frozen variable list --
is unchanged; what was relinquished is binary packaging ("carrier"
labels, diffuse-versus-concentrated verdicts) that the data cannot
support, and a card must not be re-registered for becoming more
modest. The applied revision implemented the debate's own conditions;
this ruling ratifies it and the unblock acknowledgment artifact is
written for the record. Second consecutive specimen for the
draft-versus-binding lane the R4 envelope will make structural.

## 2026-09-01/02 - Registry closeout: 045 gov-0002, 046 gov-0001; supersede semantics; right-sizing guidance

Executed the census interpretation's own Next-decision item 3 and the
round-10 registry-per-probe rule in one batch. ideas/046/registry.yaml
declares the blind definition audit (pin 3996009b..., results_v2,
FEASIBLE/REVISION terminals) gating the open contribution census (pin
942e5307..., results_v3, CENSUS_COMPLETE) via an all_of edge.
ideas/045/registry.yaml gains attribution_v3 (pin b1e28361...,
results_v4, the three-outcome terminal set) depending on
feasibility_v2. Rehearsal on the real repository surfaced a designed
deadlock before the operator could hit it: editing a ratified registry
staled the prior row's registry_sha256, read-time verification flagged
it, validation failed, and ratify-registry refused because validation
failed -- re-ratification was impossible by construction. Semantics
corrected: a row bound to SUPERSEDED registry bytes is historical
record that confers nothing and is skipped silently; only rows binding
the CURRENT bytes undergo, and must pass, the loud mechanical
verification (the round-10 forgery exploit remains loudly caught,
since it forges evidence under a valid sha; forging the sha itself
merely forfeits all authority). Lifecycle regression added
(edit-then-gov-0002 end-to-end). Second rehearsal: 045 gov-0002 binds
all three pins with both local-ancestry imports and derives THREE
nodes COMPLETE; 046 gov-0001 binds both pins with the audit import and
derives TWO nodes COMPLETE; state-verify 46/46 on the ratified tree.
probe-plan gains the operator's right-sizing ruling (prefer one
contract with pre-registered ordered phases/branches over serial
contracts when later phases are deterministic and equally blindable;
separate contracts only for new authority scope). Deferred
consciously: feasibility joining pipeline default stages (test fake
lacks the branch; post-meeting batch). 045/046 state+CARD
re-materialized in-patch. 213/213 both runners; state-verify 46/46 on
build and pristine-applied trees; patch git-identical.

OPERATOR STATUS NOTE (idea 046): the ratified census interpretation
recommended PAUSED (clinical rung opportunistic on the next archive
staging; no active work now); the operator's transition was ACTIVE,
issued before the recommendation was read -- the assistant supplied
the status ahead of the document and owns the ordering error. Ruling
recorded: the divergence stands consciously; ACTIVE reflects the
operator's intent to register the clinical/stability successor
promptly rather than opportunistically; no work runs under idea 046's
spent contracts either way. Queued for the reviewer: whether ratify-
interpretation should display the document's recommended status before
accepting the operator's choice.


## 2026-09-02 - Operator note to the next scout cycle: open successor direction (describe-level steering; not a card)

For candidate generation: the research record now contains a decided,
ratified structure with no registered follow-up. The idea-046
contribution census (probes/046/results/results_v3, interpretation
ratified) established that the band-3-minus-band-2 final-infarct
contrast from idea-023 is head-dominated in the realized estimator:
the ten largest of 99 cases account for roughly 79 percent of the net
gap, the single largest about 13 percent, 39 cases push the opposite
direction, and the top cases individually exhibit the full sign flip
at magnitudes ten to twenty times the cohort means. The idea-046
interpretation (Next decision, item 4) states that any stability,
carrier, clinical, or model-use question about these cases must enter
as a separately registered successor citing that census. A
patient-level clinical-outcome join (released mRS/NIHSS-type phenotype
table, ses-02 outcome family) was pre-registered on 2026-08-28, was
folded into idea 046 as an optional rung, and remains unexecuted; the
ratified record specifies a D3 read-restriction protocol for the
phenotype restage and a D4 joint-display rule for any clinical
comparison. Candidates continuing this line belong in the
descriptive/association register, not model-use. This note states an
open direction the operator wants candidates FOR; it deliberately does
not supply a question wording, design, or scores -- generation,
critique, and debate own those. Discovery-track candidates unrelated
to this direction remain welcome in the same cycle.


## 2026-09-02 - Operator note to the next scout cycle: the CLINICAL successor specifically (second steering pass)

The previous cycle produced one lineage-anchored candidate; it took
the model-use angle. For THIS cycle the operator seeks candidates for
a different, specific open direction, and model-use formulations of it
are explicitly not wanted here: the spiritual successor to ideas
023 -> 045 -> 046 in the DESCRIPTIVE register. The open question
family: the idea-046 census identified, by frozen rule, which of the
99 observed cases numerically dominate the band-3-minus-band-2
reversal (top ten roughly 79 percent of the net gap; 39 cases oppose;
top cases individually exhibit the full sign flip). Nothing is known
about WHO these high-contribution patients are: whether they differ
from the rest on the released clinical outcome scores (mRS/NIHSS-type
phenotype table, ses-02 outcome family -- pre-registered for exactly
this join on 2026-08-28, never executed, with a ratified D3
read-restriction protocol for the phenotype restage and a D4
joint-display rule for clinical comparisons) or on already-computed
per-case imaging features in the imported bundles. Any candidate here
is exploratory by construction (the 99 outcomes were opened in
idea-023) and must say so; aggregate description only, no per-patient
clinical claims, no model probing. The operator wants the question,
design, framing, and scores to come from generation and the gauntlet
-- this note supplies direction and pointers only. Discovery
candidates outside this direction may still appear, but at least one
serious candidate FOR this direction is the purpose of the cycle.


===== evidence/ledger_digest_isles24.md =====
# Ledger digest -- charter: isles24 (auto-generated; scores are scoped to this charter only)

84 tracked ideas in this charter. Latest state per idea; full history in ledger.jsonl.

Work under other charters: evidence/cross_charter_index.md (facts, no scores).

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **IDENTIFIABILITY_FAILURE** x12: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_ACCESS** x3: Required data, checkpoints, or mappings are not obtainable in practice.
- **EFFECT_UNREACHABLE** x1: The claimed effect cannot exceed a published bound / measurement floor.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **isles24-scout-009-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.0, audited 2026-09-02] -- The keystone patients: ten cases may teach the model the reversal
- **isles24-scout-008-c08** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.6, audited 2026-09-02] -- The model speaks one vendor's dialect: swap the deconvolution, keep the patient
- **isles24-scout-008-c07** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.6, audited 2026-09-02] -- Caught mid-swallow: does the model read acquisition luck as collateral biology?
- **isles24-scout-002-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.4, audited 2026-08-16] -- Two tissues, two death thresholds
- **isles24-scout-004-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.1, audited 2026-08-18] -- The heart's signature in the head scan
- **isles24-scout-005-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 2.9, audited 2026-08-19] -- The bottleneck before the brain
- **isles24-scout-004-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.3, audited 2026-08-18] -- The brain's odometer: calcification as the model's age gauge
- **isles24-scout-002-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.2, audited 2026-08-16] -- The clot that lets contrast through
- **isles24-scout-002-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.0, audited 2026-08-16] -- The barrier is already leaking
- **isles24-scout-008-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.8, audited 2026-09-02] -- The blood arrives backwards: filling direction as the model's collateral gauge
- ... and 19 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- counterfactual-synthesis: 10
- regional-substitution: 9
- representation-erasure: 7
- conditional-observational: 6
- cross-model-disagreement: 4
- natural-paired: 2
- regional-removal: 2
- other:label-geometry-audit: 2
- other:remote-perturbation: 1
- other:graph-edge-intervention: 1
- model-output-perturbation: 1
- other:temporal-reparameterization: 1
- other:noise-residual-transplant: 1
- other:geometry-conditioned-boundary-test: 1
- other:vector-field-alignment: 1
- other:objective-ablation: 1
- other:acquired-frame-substitution: 1
- cross-reconstruction: 1
- other:atlas-frame-randomization: 1
- other:value-lattice-audit: 1

## Ideas

- **idea-020** [REJECTED/DEBATED/baseline] -- A spreading front inside the perfusion deficit -- killed: IDENTIFIABILITY_FAILURE
- **idea-021** [SHORTLISTED/DEBATED/baseline] -- The healthy hemisphere is the ruler
- **idea-022** [PAUSED/DEBATED/wide] -- Does the model mistake the end of the scan for the end of the bolus?
- **idea-023** [PAUSED/PROBED/wide] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
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
- **idea-045** [PAUSED/PROBED/wide] -- Tissue-normalized joint CBV/MTT compensation at matched flow
- **idea-046** [ACTIVE/PROBED/wide] -- Who carries the band-2/3 reversal, and do the carriers differ clinically?
- **idea-047** [ACTIVE/PROBED/wide] -- The keystone ten meet the clinic: is estimator dominance clinically marked or clinically silent?
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
- **isles24-scout-006-c01** [SHORTLISTED/?/baseline] -- (untitled)
- **isles24-scout-007-c01** [SHORTLISTED/?/baseline] -- (untitled)
- **isles24-scout-008-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The ghost core and the water clock: what the NCCT-only winner knows that the perfusion thresholds don't
- **isles24-scout-008-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The unpredictable infarct: how much of the benchmark happened after the scan
- **isles24-scout-008-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Written off by depth: the internal borderzone in the model's triage
- **isles24-scout-008-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The blood arrives backwards: filling direction as the model's collateral gauge
- **isles24-scout-008-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The rough edge grows: boundary geometry as the model's stability gauge
- **isles24-scout-008-c06** [SCOUT_ONLY/SCOUTED/wide] -- The forecaster's hedge: the model's volume is a bet, not a belief
- **isles24-scout-008-c07** [SCOUT_ONLY/SCOUTED/wide] -- Caught mid-swallow: does the model read acquisition luck as collateral biology?
- **isles24-scout-008-c08** [SCOUT_ONLY/SCOUTED/wide] -- The model speaks one vendor's dialect: swap the deconvolution, keep the patient
- **isles24-scout-009-c01** [SCOUT_ONLY/SCOUTED/wide] -- The keystone patients: ten cases may teach the model the reversal
- **isles24-scout-009-c02** [SCOUT_ONLY/SCOUTED/wide] -- The model's hidden disability map
- **isles24-scout-009-c03** [SCOUT_ONLY/SCOUTED/wide] -- The atlas prior hidden under the perfusion maps
- **isles24-scout-010-c01** [SHORTLISTED/SCOUTED/wide] -- The keystone ten meet the clinic: is estimator dominance clinically marked or clinically silent?
- **isles24-scout-010-c02** [SCOUT_ONLY/SCOUTED/wide] -- Split the bolus movie in half: a parallel-forms noise floor for the benchmark's perfusion measures
- **isles24-scout-010-c03** [SCOUT_ONLY/SCOUTED/wide] -- Graph-paper physiology: the value lattice under the penumbra thresholds


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

## idea-023 [PAUSED] -- The joint CBV/MTT compensation state at matched flow

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
- [isles24] **idea-023** [PAUSED] -- Little's law in the penumbra: the model may be reading the vasodilatory counterattack
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
- [isles24] **idea-045** [PAUSED] -- Tissue-normalized joint CBV/MTT compensation at matched flow
- [isles24] **idea-046** [ACTIVE] -- Who carries the band-2/3 reversal, and do the carriers differ clinically?
- [isles24] **idea-047** [ACTIVE] -- The keystone ten meet the clinic: is estimator dominance clinically marked or clinically silent?
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
- [isles24] **isles24-scout-006-c01** [SHORTLISTED] -- 
- [isles24] **isles24-scout-007-c01** [SHORTLISTED] -- 
- [isles24] **isles24-scout-008-c01** [SCOUT_ONLY] -- The ghost core and the water clock: what the NCCT-only winner knows that the perfusion thresholds don't
- [isles24] **isles24-scout-008-c02** [SCOUT_ONLY] -- The unpredictable infarct: how much of the benchmark happened after the scan
- [isles24] **isles24-scout-008-c03** [SCOUT_ONLY] -- Written off by depth: the internal borderzone in the model's triage
- [isles24] **isles24-scout-008-c04** [SCOUT_ONLY] -- The blood arrives backwards: filling direction as the model's collateral gauge
- [isles24] **isles24-scout-008-c05** [SCOUT_ONLY] -- The rough edge grows: boundary geometry as the model's stability gauge
- [isles24] **isles24-scout-008-c06** [SCOUT_ONLY] -- The forecaster's hedge: the model's volume is a bet, not a belief
- [isles24] **isles24-scout-008-c07** [SCOUT_ONLY] -- Caught mid-swallow: does the model read acquisition luck as collateral biology?
- [isles24] **isles24-scout-008-c08** [SCOUT_ONLY] -- The model speaks one vendor's dialect: swap the deconvolution, keep the patient
- [isles24] **isles24-scout-009-c01** [SCOUT_ONLY] -- The keystone patients: ten cases may teach the model the reversal
- [isles24] **isles24-scout-009-c02** [SCOUT_ONLY] -- The model's hidden disability map
- [isles24] **isles24-scout-009-c03** [SCOUT_ONLY] -- The atlas prior hidden under the perfusion maps
- [isles24] **isles24-scout-010-c01** [SHORTLISTED] -- The keystone ten meet the clinic: is estimator dominance clinically marked or clinically silent?
- [isles24] **isles24-scout-010-c02** [SCOUT_ONLY] -- Split the bolus movie in half: a parallel-forms noise floor for the benchmark's perfusion measures
- [isles24] **isles24-scout-010-c03** [SCOUT_ONLY] -- Graph-paper physiology: the value lattice under the penumbra thresholds
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
- [baseline] **scout-019-c01** [SCOUT_ONLY] -- Name the vessel-tree phenotype inside retinal sex prediction
- [baseline] **scout-019-c02** [SCOUT_ONLY] -- The spleen as the fatty-liver model's calibration patch
- [baseline] **scout-019-c03** [SCOUT_ONLY] -- The azygos vein inside the edema score
- [baseline] **scout-019-c04** [SCOUT_ONLY] -- The meniscus inside the pleural-effusion score
- [baseline] **scout-019-c05** [SCOUT_ONLY] -- The opening in the diaphragm inside the hiatal-hernia score


===== evidence/librarian_proposals.md =====


===== ideas/047/CARD.md =====
# Research Card - idea-047

GENERATED VIEW (R5a). Never edit: regenerate with `python scout.py card-materialize 47`. Edits belong in the source artifacts this card renders.

## Identity
- title: The keystone ten meet the clinic: aggregate clinical profile and support-share arithmetic of the census head
- charter: isles24   track: wide   card-id: isles24-scout-010-c01
- ledger status: SHORTLISTED   scrutiny: SCOUTED   ledger events: 1

## Question
[ecology] In the frozen 99-case idea-046 census cohort, do the ten largest signed contributors to the band-2/3 reversal (the frozen signed-rank top ten) differ in aggregate on a pre-frozen released clinical variable list from the other 89 cases -- and how does their exact share of total absolute contribution compare with their exact share of total eligible deficit support, the per-case eroded Tmax>6s region voxel count recomputed under the ratified take-13 parameters?

## Declared vs derived status
- idea_card.keystone_status: 'INSPECTED_TRUE'
- system-derived: no interpretation

## Contract lineage (approval marker history, oldest -> newest)
- (no approval marker history)

## Experiment position
- no imported results bundle

## Interpretation and authority
- interpretation.md: missing
- interpret_review.md: missing
- decision.md: missing
- ratified: no

## Connections
- (none recorded; add an optional related_ideas list to idea_card.json)

## Documents
- ideas/047/idea_card.json
- ideas/047/probe_contract.yaml  (absent)
- ideas/047/interpretation.md  (absent)
- ideas/047/interpret_review.md  (absent)
- ideas/047/decision.md  (absent)
- ideas/047/state.json


===== ideas/047/README.md =====
# Idea 047: The keystone ten meet the clinic: is estimator dominance clinically marked or clinically silent?

Selected from scouting cycle isles24-010, candidate 1.


===== ideas/047/consensus.md =====
# Debate summary — idea 047

## Agreed

- The candidate has two claim-bearing clauses: an aggregate clinical description of the frozen top ten versus the other 89 cases, and a comparison of contribution dominance with an imaging-support quantity. Deleting the second clause would not answer the registered question (round 1).
- The original burden formulation was not reproducible. Exact eroded Tmax>6 s volume is absent from the imported tables, and the proposed residual of `|c_i|` on burden left the burden definition, model form, scale, and leverage handling open (round 1).
- The in-repository candidate burden variable is `S_i`, the sum across all three flow bands of `q1_voxels + q4_voxels`, honestly named **eligible extreme-quartile support**, not deficit volume. Its provenance and its relation to total eligible support must be verified from the frozen take-13 implementation before phenotype rows are opened; if that check fails, exact eligible support must be recomputed from the 99 Tmax maps under the ratified region machinery (round 1).
- No fitted-residual subgroup should be created. The clinical group remains the already frozen signed-rank top ten; the burden analysis is continuous and descriptive (round 1, retained through round 3).
- Random-ten-subset permutation inference is invalid here. The top ten were deterministically selected by signed contribution from a complete 99-case census, so random subsets are not licensed by the design and selection on contribution mechanically favors extreme contribution ranks (round 2).
- The burden clause is a finite-population description of these 99 realized cases, with no sampling uncertainty, hypothesis test, threshold, or claim that the pattern generalizes to new patients. The full rank-discrepancy distribution and Spearman correlation may be displayed descriptively (round 2).
- The sole burden-disproportionality comparison is the top ten's share of total absolute contribution, `sum_head |c_i| / sum_all |c_i|`, beside their share of total eligible support, `sum_head S_i / sum_all S_i` (round 3).
- The 79.29% net signed-gap share remains only as a separately labeled lineage/accounting statistic. Because 39 cases contribute in the opposite direction, cancellation affects its denominator; neither that statistic nor its difference from support share may be interpreted as contribution per unit support (round 3).
- These repairs preserve the candidate's identity: the frozen cohort, top-ten membership, clinical clause, and burden-proportionality clause remain, while the latter receives a valid operational definition (rounds 2 and 3).

## Unresolved

There is no remaining disagreement between proposer and critic at the close of round 3. Two factual implementation gates remain:

### Does eligible extreme-quartile support validly proxy the estimator's total eligible support?

- **Proposer's position:** `S_i` should be an approximately 50% deterministic fraction of total eligible support if Q1 and Q4 are the within-band per-case quartiles produced by the frozen take-13 code.
- **Critic's position:** The critic accepted this operational path subject to the specified provenance check; the debate did not independently establish the code fact.
- **What evidence would settle it:** Inspect the frozen take-13 implementation and reproduce the derivation from the 297-row `per_patient.csv`. If the relationship fails, selectively restage the 99 Tmax maps and recompute exact eligible support with the ratified region machinery.

### Which released clinical fields and time points are actually usable?

- **Proposer's position:** The debate leaves intact the critique's requirement to inspect only `clinical_data-description.xlsx`, then freeze the exact variable names, time points, coding, missingness rules, and short analysis list before opening case-level phenotype rows.
- **Critic's position:** Admission NIHSS must not be treated as interchangeable with the lineage's previously named 24-hour NIHSS, and conditional additions such as “treatment fields if present” are not a frozen plan.
- **What evidence would settle it:** A dictionary-only schema inventory followed by a frozen specification. The later D3-restricted staging of the 99 phenotype rows settles completeness and usable sample sizes.

## Positions that moved

- In round 1, the proposer conceded that exact deficit burden was not already available, the residual analysis was underspecified, a clinical-only repair would change the question, and the original “~50 kB, under five minutes” statement understated acquisition and staging cost. This was earned by the critic's concrete inventory and specification argument.
- In round 2, the proposer withdrew the random-subset permutation null and permutation interval after the critic showed that the top ten are outcome-selected and nonexchangeable and that the rank statistic partly rewards its own selection rule. This was an earned concession based on a new inferential objection.
- In round 3, the proposer demoted net signed share from the burden comparison and adopted absolute-contribution share after the critic identified denominator cancellation from the 39 opposing cases. This was an earned concession based on a new measurement objection.
- No concession was unearned.

## Amendments made

At round zero, the idea proposed two top-ten-versus-rest contrasts, called the imaging quantity deficit burden, used an unspecified residual of `|c_i|` on burden to create a second “disproportionality top-decile,” proposed permutation tests and binary proportionate/keystone-like language, and connected the 79.29% net signed share directly to burden disproportionality.

The amended idea keeps one frozen clinical group: the ten largest signed contributors versus the other 89. Before phenotype access, it defines `S_i` from the existing label-blind extreme-quartile support counts, subject to code verification and an exact-map contingency. For these 99 cases, it compares the top ten's absolute-contribution share with their eligible-support share; it may show casewise rank discrepancies and Spearman correlation descriptively. The 79.29% signed-net statistic is reported separately as reversal accounting. The clinical output is an aggregate estimation table with uncertainty and missingness, not a significance-selected or clinically explanatory verdict.

What is lost is the fitted residual subgroup, inferential calibration for the burden clause, generalization beyond the realized 99 cases, the phrase “deficit burden” for the proxy, the clinical-versus-imaging dichotomy, and the ability to use the dramatic 79.29% statistic as evidence of burden-disproportionate dominance. End-to-end cost must include dictionary inspection and restricted archive staging, and possibly map restaging.

## Recommendation

**REVISE.** The debate resolved its scientific objections, but the current `idea_card.json` still contains the superseded residual subgroup, permutation-null language, conditional clinical fields, understated cost, “clinically silent” framing, and the cancellation-confounded use of the 79.29% statistic. The single most important thing for the human to inspect is whether the frozen take-13 code establishes that `S_i` is the claimed deterministic proxy for total eligible support; that check determines whether the low-cost in-repository path is valid or exact support must be recomputed from maps.

## In plain terms

This idea asks whether the ten cases that contribute most to a previously observed stroke-imaging pattern look clinically different from the other 89 cases. It also asks whether those ten contribute unusually much relative to the amount of eligible image support they contain.

The debate concluded that the question is worth retaining, but the original analysis was not validly specified. The revised version uses exact descriptive shares for these 99 cases, avoids an unjustified statistical test, and keeps the cancellation-sensitive 79.29% figure separate from the burden comparison. The card must be rewritten before the study advances.

The human is being asked to check whether the proposed support count really has the relationship to total eligible support claimed from the frozen earlier pipeline.

```json
{"verdict": "REVISE", "unblock": "Rewrite the card to the round-3 finite-population design and verify from the frozen take-13 implementation that S_i is the claimed proxy for total eligible support, otherwise freeze the exact-map recomputation branch."}
```


===== ideas/047/critique.md =====
FATAL OBJECTION: NONE
EVIDENCE: `ideas/046/idea_card.json` freezes NIHSS at 24 hours and deficit-region voxel count, while idea 047 substitutes admission NIHSS and leaves its burden extraction and endpoint undefined.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION

# Adversarial critique — idea 047

## Bottom line

The clinical join is worth doing, but the current card is not contract-ready. Its strongest defensible product is a small exploratory descriptive table for a subgroup frozen by earlier work. The card instead adds an inadequately defined “keystone” residual, implies that a small-sample null can distinguish clinical signal from imaging geometry, and prices only the extracted CSV bytes rather than the archive restage and image-derived burden calculation. None of those defects requires changing the central question, but all require narrowing the interpretation and freezing the actual variables and estimands.

## The decisive defects

### D1 — The clinical endpoint has drifted from the ratified lineage

`ideas/046/idea_card.json` freezes the optional clinical comparison to deficit-region voxel count, vessel-cap statistic, exclusion flags, **NIHSS at 24 hours**, and mRS at 3 months. Idea 047 asks for **admission NIHSS**, age, sex, and conditionally treatment fields. The official challenge design lists NIHSS at admission, NIHSS at discharge, 90-day mRS, time since onset, and reperfusion fields (ISLES'24 challenge design, official repository URL: https://zenodo.org/records/10991145/files/Ischemic%20Stroke%20Lesion%20Segmentation%20Challenge%202024.pdf), while the current Zenodo record promises admission NIHSS and 3-month mRS more generally (official record: https://zenodo.org/records/16813698). These sources do not establish that “NIHSS at 24 hours” and “admission NIHSS” are interchangeable.

This is not merely wording. Baseline neurological severity and post-treatment neurological status answer different questions and sit at different causal positions. Revision must first read only `clinical_data-description.xlsx`, freeze exact field names, time points, coding, missing-value rules, and the hierarchy of primary versus contextual variables, and then preserve the D3 restriction when case rows are staged. If the release lacks the previously frozen 24-hour field, state the forward correction and use admission NIHSS as a newly specified contextual variable; do not describe it as execution of the old frozen list.

### D2 — “Keystone-like” is not yet a reproducible endpoint

The top-ten group is reproducible: it is the already frozen signed ranks 1–10. The second proposed group is not. “Residual of |c_i| on burden” leaves open the burden definition, scale, functional form, nonlinear terms, treatment of zero contributions, leverage handling, and whether the residual is signed, absolute, studentized, or rank-based. Turning the ten largest residuals into another group after choosing among these options creates an analyst-defined result, not a frozen ecological measurement.

There is also a construct mismatch. The borrowed ecological analogy concerns impact disproportionate to abundance, but here `c_i` is algebraically a patient-specific band contrast divided by the fixed cohort size. “Abundance” has no unique analogue. Deficit volume is a plausible nuisance/exposure measure, not a validated translation of ecological abundance. The study may call the result “contribution disproportionate to measured deficit support”; it should not make “keystone” the scientific endpoint.

Repair: make the frozen top-ten-versus-rest comparison primary and treat contribution-versus-burden as a continuous descriptive plot. Predefine one burden measure and one simple model before phenotype access. Do not dichotomize fitted residuals unless a separate sensitivity analysis demonstrates that the conclusion is stable across reasonable burden definitions and functional forms.

### D3 — The proposed burden measure is not already available, and cost is understated

The low-hanging-fruit input table does **not** contain total deficit burden. `probes/023/results/results_v2/per_patient.csv` contains only `case_id,stratum,q1_voxels,q4_voxels,d`; `probes/046/results/results_v3/per_case_contributions.csv` contains contribution quantities only. The card proposes recomputing eroded Tmax>6 s voxel counts from maps, yet says the experiment uses “two 99-file CSV families totaling ~50 kB” and takes under five minutes. Those statements describe final extracted bytes, not acquisition and preprocessing.

The lineage feasibility memo already gives the honest cost: the phenotype members are inside `train.7z`, so the clinical rung requires selective extraction from/restaging of the checksum-pinned approximately 99 GB archive (`ideas/046/feasibility.md`, sections 3 and 5). Recomputing exact burden also requires the map payload and the frozen take-13 region implementation, its contract identity, and a reproducibility comparison against cached case counts. This remains feasible and GPU-free, but “minutes on 50 kB” is not an honest end-to-end envelope.

An easier option already exists: use a clearly labeled **eligible-extreme-quartile support proxy** derived from the existing q1/q4 counts, after verifying its relationship to total eligible support from the frozen take-13 definitions. It must not silently be renamed “deficit burden.” If exact eroded deficit volume is scientifically necessary, pay and state the archive/map restage cost.

### D4 — A null cannot support “clinically silent” or favor imaging geometry

Ten versus 89 is a weak design for detecting anything but large distributional separation, especially for ordinal mRS, incompletely observed clinical variables, and multiple predeclared fields. Permutation tests do not cure low power. No smallest effect of interest, precision target, or missingness floor is specified. Therefore a failure to detect a difference is sensitivity-limited; it cannot show the dominant cases are clinically silent, and it cannot push explanation toward “imaging geometry.”

This defect appears in the title, `audience_relevance`, the negative-result rationale, and the plain pitch (“whether the dominant patients look clinically different ... or ... only for imaging-arithmetic reasons”). The technical card partly concedes sensitivity limitation, but then restores the stronger dichotomy elsewhere. Revision should replace “clinically silent” with “no large clinical separation detected at the achieved precision” and require confidence intervals or randomization intervals for effect sizes. The useful negative result is bounded: it excludes only effects larger than the reported uncertainty.

### D5 — A positive comparison remains confounded and selection-specific

The group was selected for a realized final-infarct-derived contribution. mRS and later NIHSS are downstream of infarct burden and treatment; admission NIHSS reflects baseline severity, occlusion territory, collaterals, and time. Deficit volume is only one common cause or mediator. Even after displaying volume, a positive association cannot establish a clinical subtype or explain why these cases dominate. Treatment/reperfusion, onset-to-imaging time, occlusion site, and missingness could all structure the comparison.

The card's association register prevents this from becoming fatal, provided it remains strict: report joint distributions and standardized contrasts; do not say clinical variables “explain” dominance; do not fit a multivariable model with ten exposed cases and a growing covariate list. Conditional “treatment fields if present” is not a frozen analysis plan. Inventory first, then predeclare a very short contextual set.

### D6 — Endpoint and multiplicity are still unclear

The card names standardized mean differences, rank tests, and permutation nulls across mixed continuous, binary, and ordinal variables but defines no primary endpoint, test statistic, sidedness, permutation unit, missing-data rule, or interpretation threshold. “Does / does not differ” invites a binary conclusion that the proposed all-variable table cannot honestly deliver. The most defensible endpoint is not a global discovery test. It is an estimation display: for each frozen variable, give both groups' distributions, an appropriate standardized effect with uncertainty, effective sample size, and the same display stratified or accompanied by the frozen burden measure. Label all inferential p-values exploratory and do not select a headline by significance.

## Prior work, relevance, circularity, and leakage

I found no verified exact duplicate of the proposed ISLES'24 contribution-census/phenotype join. The organizers' paper uses multimodal imaging and clinical data for final-infarct prediction (arXiv:2408.10966; DOI 10.48550/arXiv.2408.10966), which overlaps in variables but not in estimand. Maier-Hein et al. show that biomedical challenge conclusions can be sensitive to the sampled test cases and aggregation choices (DOI 10.1038/s41467-018-07619-7), supporting the general benchmark-audit motivation but not establishing novelty. Broocks et al. is a thematic neighbor for clinically characterizing perfusion-threshold error (DOI 10.1148/radiol.231750; PMID 39078297), not a duplicate. The card's “appears unpublished” language is appropriately hedged; it must not be upgraded to a novelty claim, especially while the cited 2026 near-miss remains unread.

There is no concept-label circularity in the narrow descriptive join: group membership is frozen from imaging/final-infarct quantities, not defined from mRS, NIHSS, age, or sex. There is nevertheless outcome coupling: both contribution and 3-month disability are consequences of the same stroke and treatment course. That is confounding/shared-outcome structure, not prohibited leakage, as long as the analysis is explicitly exploratory and does not claim independent validation.

Medical relevance is moderate, not high. The result could tell researchers whether a program-central estimator anomaly visibly coincides with broad clinical severity. It cannot validate a perfusion biomarker, alter treatment, or characterize a population from 99 selected training cases. Its strongest audience is benchmark methodologists and researchers interpreting this exact lineage.

## Plain-pitch fidelity

**Named defect: PLAIN-PITCH OVERCLAIM.** The pitch accurately preserves the 99-case scope, aggregate-only rule, exploratory status, and absence of individual claims. It does not preserve the technical card's sensitivity-limited-null caveat. “Whether the dominant patients look clinically different ... or whether they stand out only for imaging-arithmetic reasons” presents exhaustive alternatives that this observational, underpowered comparison cannot distinguish. “Either answer changes how researchers should read” similarly overstates an imprecise null. Replace this with: the analysis can reveal a large clinical separation if present; otherwise it reports how much separation the small frozen subgroup comparison can exclude.

## Low-hanging fruit and simplest defensible execution

The easiest useful version requires no new image calculation and no model or checkpoint:

1. Freeze the schema from the already public 12.1 kB `clinical_data-description.xlsx` before opening case rows.
2. Select the already frozen signed-rank top ten from `per_case_contributions.csv`; do not create a fitted-residual subgroup.
3. Selectively extract only the 99 permitted baseline/outcome CSV pairs from the already held, checksum-verified archive under D3.
4. Produce a single aggregate table for exact available versions of mRS, NIHSS, age, and sex, with completeness, group distributions, effect sizes, uncertainty, and the existing q1/q4 support counts shown as a labeled imaging-support proxy.
5. Report all rows jointly and stop. No significance-based headline, clinical subtype language, causal adjustment, or per-patient output.

Data and labels already exist; the case group is frozen; code logic for the census and archive integrity already exists; no checkpoint, GPU, or new annotation is needed. The operational low-hanging fruit is real, although the archive extraction is not equivalent to a 50 kB download.

## Required revision

- Reconcile admission versus 24-hour/discharge NIHSS using the data dictionary and explicitly document any departure from idea 046's frozen optional rung.
- Replace “clinically silent” and the clinical-versus-imaging dichotomy throughout, including title, negative-result value, audience relevance, and plain pitch.
- Choose one exact burden/support variable, show where it comes from, and price its extraction honestly.
- Drop the residual top-decile confirmatory contrast or fully prespecify and demote it to sensitivity analysis.
- Make the primary deliverable an estimation table with uncertainty and missingness, not a binary “differs / does not differ” verdict.
- Freeze a short variable list after dictionary-only inspection; remove conditional analyst discretion such as “treatment fields if present.”
- Bind D3 to exact permitted identifiers and D4 to an exact joint display. Preserve aggregate-only outputs and suppress small cells if any categorical cross-tab risks case re-identification.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Among the frozen ten largest signed contributors and the other 89 analyzed cases, what are the aggregate differences and uncertainty in the release-defined mRS, NIHSS, age, and sex distributions when displayed jointly with one predeclared imaging-support measure?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes — it cheaply closes a specifically preregistered, still-open clinical-description rung, provided its value is an honest bounded description rather than a clinical-subtype or explanatory claim.


===== ideas/047/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed repair silently drops the card's burden-normalized “keystone-like” question, so it does not yet preserve the candidate's claim identity.

**Argument:** The registered question is compound: it asks both whether the frozen top ten differ clinically and whether their dominance is disproportionate to deficit burden. Yet neither the card nor the imported idea-046 tables define the required burden quantity: `per_patient.csv` contains only extreme-quartile support counts, while exact eroded Tmax>6 s volume would require restaging the maps and reproducing the take-13 region machinery. More importantly, “residual of |c_i| on burden” leaves the model, scale, leverage treatment, and even the analogue of ecological abundance unspecified. The critique's nearest defensible experiment therefore removes the residual subgroup and substitutes a continuous support display. That is a sensible clinical-description study, but it answers only the first half of the original question; it cannot conclude whether dominance is burden-proportionate or “keystone-like.” Under the claim-identity rule, feasibility obtained by deleting a named deliverable is not a revision unless the proposer either operationalizes that deliverable prospectively or formally narrows the deliverable while showing that the central question was always the clinical top-ten comparison. This objection outranks the other statistical defects because an impeccably executed aggregate table would still not answer the card as registered.

**What would change my mind:** Before any phenotype rows are opened, specify one exact label-blind burden variable available for all 99 cases, its extraction provenance and reproducibility check, and one frozen continuous estimand relating signed contribution magnitude to burden with uncertainty and leverage handling; then rewrite the deliverable so that this descriptive estimand—not a post-fit residual top-decile label—answers the burden-proportionality clause. Alternatively, provide a claim-identity ruling that the burden/keystone clause is removable without changing the candidate; absent that ruling, the clinical-only table should be a separately registered successor.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The critique's "nearest defensible experiment" quietly deletes the burden-proportionality ("keystone-like") clause of the registered compound question. Under the claim-identity rule that deletion is not a repair; the candidate survives only if the clause is operationalized prospectively — one exact label-blind burden variable available for all 99 cases with stated provenance, plus one frozen continuous estimand with uncertainty and leverage handling — or if an explicit identity ruling declares the clause removable.

**Response:** AMEND

**Argument:** The critic's factual premises are correct and I accept them: exact eroded Tmax>6 s volume is not in any imported table; "residual of |c_i| on burden" as written on the card was analyst-discretionary, not frozen; and answering only the clinical half would be a different study wearing this card's title. I therefore take the critic's first offered path — prospective operationalization — not the ruling path, which the amendment makes unnecessary.

The amendment, all parts frozen before any phenotype row is opened:

1. **The burden variable exists in-repo, label-blind, for all 99 cases.** Define S_i = Σ over the three flow bands of (q1_voxels + q4_voxels) from `probes/023/results/results_v2/per_patient.csv` (297 data rows = 99 cases × 3 bands; produced by the take-13 label-blind map pass, before any outcome contact). It is named honestly as **eligible extreme-quartile support** and never called "deficit volume." Its relationship to total eligible deficit support is verified at spec time from the frozen take-13 code, with no archive restage and no outcome contact: if Q1/Q4 are within-band per-case quartiles — which the data already fingerprint, since q1_voxels ≈ q4_voxels in every row (e.g. sub-stroke0002 band 1: 3969 vs 3970) — then S_i is a deterministic ≈50% fraction of total eligible support, hence monotone in it by construction. Contingency if that code check fails: selectively extract the 99 Tmax maps from the held, checksum-verified archive and recompute exact eroded deficit support with the ratified region machinery, CPU-only — priced honestly as an increment to the D3 phenotype staging event, which already requires opening the same `train.7z`. Either branch yields one exact, provenance-stated, label-blind burden variable for all 99.

2. **The frozen continuous estimand replaces the post-fit residual subgroup entirely.** Per-case rank discrepancy D_i = rank(|c_i|) − rank(S_i) over the 99 cases. Ranks remove the functional-form, scale, and leverage choices the critic correctly listed as unspecified — no model is fit, so no residual, leverage, or studentization decision exists to make. The burden-proportionality clause is answered by two pre-frozen quantities: (a) Spearman ρ between |c_i| and S_i with a permutation interval, and (b) the mean of D_i over the already-frozen signed-rank top ten, referred to a permutation null of random 10-subsets of the 99. No fitted-residual top-decile group is ever formed; "keystone-like" becomes the reported magnitude of the top-ten mean rank discrepancy, a continuous description, not a second dichotomy.

3. **The deliverable sentence's second clause is rewritten to match:** "...and their dominance is / is not disproportionate to eligible deficit support, measured as the pre-frozen rank discrepancy between contribution magnitude and support." The first (clinical) clause is untouched.

**Identity check:** the revised design still answers the registered one-sentence question in both of its clauses — do the top ten differ clinically, and is their dominance burden-proportionate or disproportionate. The second clause changes from unmeasurable-as-written to measured; the question itself does not change.

**What is lost, stated plainly:** (i) "Deficit burden" narrows to *eligible deficit support* — the take-13 analysis region after erosion, vessel exclusion, and finiteness filtering — which is a subset of gross lesion burden; a disproportionality finding on this axis speaks to the estimator's own support base, not to clinical lesion size, and the writeup must say so. (ii) The punchy keystone-versus-rest second contrast becomes a continuous estimand plus one top-ten statistic — less headline, more honesty. (iii) The card's "~50 kB, under five minutes" envelope is conceded as describing final bytes rather than acquisition (critique D3 was right); the envelope is re-priced around the D3 archive staging event it always implicitly required.

**Status:** OPEN

## Round 2 — CRITIC

**Position:** The amendment preserves claim identity, but its proposed random-subset null cannot turn the burden comparison into an uncertainty-bearing test because the “top ten” are a fixed, outcome-selected finite-population subset.

**Argument:** The amendment now does answer both parts of the registered question: eligible extreme-quartile support is an honest operational substitute for the previously undefined burden term, and the continuous rank discrepancy retains the disproportionate-dominance clause. The remaining defect is inferential. The ten cases were selected deterministically as the largest signed contributions in the complete 99-case census; they are not a random sample or treatment assignment. Comparing their mean `rank(|c_i|) - rank(S_i)` with random 10-subsets manufactures a reference distribution from an exchangeability assumption that the design does not supply. It also partly rewards the selection rule mechanically: selecting the largest positive `c_i` forces those cases toward extreme `|c_i|` ranks, so departure from random subsets is not evidence that the observed head is unexpectedly disproportionate to support. Spearman rho over all 99 describes monotone association but does not repair that top-ten calibration or supply sampling uncertainty for this fixed realized cohort. The defensible result is a finite-population descriptive decomposition: report the frozen top ten's share of total signed contribution beside their share of total eligible support, plus the casewise rank-discrepancy distribution and sensitivity to the exact-support contingency, without permutation p-values, “intervals,” or an is/is-not verdict. This preserves the original descriptive question but limits the answer to the realized 99 cases, consistent with idea 046's ratified census framing.

**What would change my mind:** Provide a prespecified probability model that makes the 99 case labels exchangeable under a scientifically meaningful null while respecting selection of the top ten by signed contribution, and show by simulation that the proposed statistic is calibrated after that selection; otherwise replace the permutation analysis and binary wording with the exact finite-population contribution-share versus support-share display and explicitly make no inferential claim beyond these 99 cases.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** My round-1 random-10-subset permutation null is invalid: the top ten are a fixed subset selected deterministically by the very statistic (largest signed c_i) from a complete finite-population census, so no exchangeability assumption licenses the reference distribution, and the statistic mean(rank(|c_i|) − rank(S_i)) is partly rewarded mechanically — selection on c forces the |c_i| ranks toward the extreme, so departure from random subsets is not evidence of burden-disproportionality. The defensible answer is the exact finite-population share decomposition, with no inferential claim beyond the 99.

**Response:** AMEND

**Argument:** The critic is right, and I take the second path they offered rather than attempt the exchangeability model. Two reasons for declining the first path, stated so the choice is on the record. First, the mechanical-selection point is correct as charged: the D_i statistic mixes rank(|c_i|) into the quantity being tested, and the selection rule guarantees the head sits at the top of that scale, so the random-subset comparison confounds "selected to be extreme in c" with "disproportionate relative to S" — a simulation would show miscalibration, not rescue it. Second, even the repairable variant I considered — fix the head, permute only the S values across the 99, test whether the head's mean support rank is extreme under a null of c⊥S — is exact only under an independence hypothesis about how support values are assigned to cases, which is a superpopulation-style claim about a generating process this lineage deliberately forswore: the idea-046 census was ratified as a finite-population estimator audit ("exact signed per-case contributions," no sampling story), and the 99 outcomes are already open. Manufacturing a probability model here would reintroduce exactly the inference-without-a-sampling-frame class of error the parent framing was built to avoid.

The amendment, replacing round-1 item 2 entirely (items 1 and 3's burden variable and its contingency branch are unchanged):

1. **The burden-proportionality clause is answered by exact finite-population arithmetic, in the same currency as the parent census.** Pre-frozen displays: (a) the frozen top ten's share of total |c_i| (and of net signed contribution, matching the census's 79.29% convention) beside their share of total eligible support Σ S_i — the direct operationalization of the borrowed keystone construct, impact share versus abundance share; (b) the full casewise distribution of rank(|c_i|) − rank(S_i) as a descriptive display, with the head's ten values marked, no summary tested; (c) Spearman ρ over the 99 reported as a descriptive number for the realized cohort, its permutation interval dropped; (d) all of (a)-(c) recomputed under the exact-support contingency branch as a frozen sensitivity display. No permutation p-values, no intervals, no random-subset null anywhere in the burden clause.

2. **Wording rule, frozen now:** the deliverable's second clause reports magnitudes — "the top ten carry X% of contribution against Y% of eligible support in these 99 cases" — with no threshold adjudicating "keystone-like" (the amended-pin-2 lesson: an unstated cutoff re-enters at interpretation time if any is/is-not language survives). "Disproportionate" may be used only as an arithmetic comparison of the two exact shares, scoped to the realized 99, never as a generalization.

3. **Consistency obligation acknowledged:** the same finite-population discipline already binds the clinical clause via critique D4/D6 (estimation display, exploratory-only p-values, no significance headline); nothing in this amendment relaxes that.

**Identity check:** the registered question asks whether the top ten's dominance is proportionate to deficit burden or disproportionate per unit burden. In a complete census this is an observable, not an estimand: the two shares are exact population quantities, so the question is answered — for these 99 cases — with no uncertainty machinery at all, exactly as the parent census answered "who carries the reversal." The clause is not weakened into unanswerable; it is answered in the only register the cohort supports. Identity preserved.

**What is lost, stated plainly:** (i) Any claim that the observed proportionality pattern would recur in new cases — the answer is a fact about the realized 99 and nothing more; a generalizing version would need a cohort with a real sampling frame and unopened outcomes, and would be a successor, not this card. (ii) The appearance of a hypothesis test on the headline clause — the reader receives two exact shares and judges the magnitude; the card gains decisiveness at the population it covers and gives up reach beyond it. (iii) A residual asymmetry worth admitting: the clinical clause keeps exploratory permutation displays (per the critique's D6 repair) while the burden clause now has none; the writeup must not let the clinical p-values imply an inferential license the burden clause honestly refused.

**Status:** CONVERGED

## Round 3 — CRITIC

**Position:** The finite-population repair preserves claim identity, but net signed-contribution share cannot be compared to support share as a measure of burden-disproportionate dominance because its denominator is altered by cancellation from the 39 opposing cases.

**Argument:** The proposer has adequately answered the round-two objection by abandoning the random-subset null and limiting the burden result to exact arithmetic for these 99 cases. The revised design still answers both clauses of the registered question, so the identity check passes. The remaining measurement problem is narrower but material: eligible support is nonnegative and additive, whereas the reported 79.29% quantity is the top ten's share of the *net signed* band-3-minus-band-2 gap. Because 39 cases contribute in the opposite direction, that ratio reflects both head magnitude and cancellation in the other 89; it can become large, exceed 100%, or change sharply as opposing contributions change even when the head's contribution magnitudes and support are fixed. Comparing that signed-net ratio directly with the top ten's support share therefore does not operationalize impact per unit support. The amendment already names the valid currency: the top ten's share of total absolute contribution, `sum_head |c_i| / sum_all |c_i|`, compared with `sum_head S_i / sum_all S_i`. The signed 79.29% share remains scientifically useful as a lineage/accounting statistic, but it must be displayed separately and must not carry the “disproportionate to support” interpretation. This restriction does not change the question; it makes its second clause measurable without sign-cancellation confounding.

**What would change my mind:** Freeze absolute-contribution share versus eligible-support share as the sole burden-disproportionality comparison, retain net signed share only as a separately labeled reversal-accounting quantity, and prohibit interpreting their numerical difference as contribution per unit support.

**Status:** OPEN

## Round 3 — PROPOSER

**Responding to:** The net signed share (the census's 79.29% convention) is an invalid numerator for the burden-disproportionality comparison: because 39 of the 99 cases contribute with opposite sign, the net-gap denominator is shrunk by cancellation, so the head's signed share conflates head magnitude with cancellation in the other 89 — it can exceed 100% and can move sharply while the head's own contributions and support are fixed. Only the absolute-contribution share, `sum_head |c_i| / sum_all |c_i|`, lives in the same nonnegative additive currency as the support share and can carry the "impact per unit support" reading.

**Response:** AMEND

**Argument:** Correct as charged, and the defect was latent in my own round-2 display (a), which offered both shares side by side without ranking their evidentiary roles. The arithmetic is not disputable: eligible support is nonnegative and additive, so a share of it is a genuine composition; the net signed gap is a difference of opposing sums, so a share of it is a leverage-on-a-residual statistic, not a composition. The census itself proved the denominators differ materially — with 39 opposing cases, `sum_all |c_i|` strictly exceeds the net gap's magnitude, so the head's 79.29% signed share is mechanically inflated relative to its absolute share. Comparing the inflated ratio against a composition-valued support share would have manufactured "disproportionality" partly out of sign cancellation.

The amendment adopts the critic's freeze verbatim, modifying round-2 item 1(a) and item 2; everything else stands:

1. **Sole disproportionality comparison, frozen:** the frozen signed-rank top ten's share of total absolute contribution, `Σ_head |c_i| / Σ_all |c_i|`, displayed beside their share of total eligible support, `Σ_head S_i / Σ_all S_i`. These are the only two numbers the "proportionate or disproportionate per unit burden" clause may cite. The head itself remains defined by signed rank — the identity of the ten is untouched; only the currency in which their weight is measured changes.

2. **The net signed share (79.29%) is demoted to a separately labeled reversal-accounting quantity.** It remains in the report — it is the lineage statistic that motivated the candidate and the link to the parent census — but under an explicit label stating it measures share of the net band-2/3 gap after cancellation, and a frozen prohibition: neither it nor its numerical difference from the support share may be interpreted as contribution per unit support or as evidence of keystone-like dominance.

3. **Consequential honesty item, stated now so it cannot surprise later:** the absolute share will be smaller than 79.29% by construction. If the head's absolute-contribution share turns out close to its support share, the burden clause's answer is "proportionate," and the dramatic signed number survives only as an accounting fact about cancellation. That is not a weakening of the study; it is the study working — the two readings the question poses are exactly what this display separates.

**Identity check:** the registered question asks whether the top ten's dominance is proportionate to deficit burden or disproportionate per unit burden. The amendment changes which exact ratio measures "dominance" for that clause — from a cancellation-contaminated share to a composition-valued one — while the cohort, the frozen head, the support variable, the finite-population register, and both clauses of the question are unchanged. The clause becomes measurable without confounding; the question does not move. Identity preserved.

**What is lost, stated plainly:** (i) The headline continuity between the question's own wording ("the ten cases that carry 79.29% of the ... reversal") and the disproportionality verdict — the number that names the head can no longer be the number that judges it, and the writeup must carry both with distinct labels, at some cost in rhetorical cleanness. (ii) Any possibility of reporting a share pair as dramatic as the signed one; the honest comparison is expected to be less striking. (iii) Nothing else: no display, contrast, or clause is dropped.

**Status:** CONVERGED


===== ideas/047/decision.md =====
# Decision — idea 047, Phase A

## Result card

- **Idea:** idea-047
- **Probe and sequence position:** probe 047, contract v2, Phase A of the planned two-phase experiment; phenotype-blind support/provenance and dictionary phase, before amendment and Phase B.
- **Dataset and pin:** ISLES'24 training release, immutable Zenodo record 16813698; Phase A used frozen imported tables and the pinned clinical dictionary only.
- **Primary metric:** frozen top-ten share of total absolute contribution beside frozen top-ten share of total eligible deficit support across the realized 99 cases.
- **Contract blob:** `b4887c05a21bfe870589b5d9982066943df679d5`
- **Results-bundle commit:** `6037f24122766fe1c68f16eb9f38d9a16c2c5e66`
- **Authoring family:** Codex. **Reviewing family:** Claude (pending).
- **Out of scope:** no clinical comparison, clinical-silence/markedness verdict, keystone classification, causal or model-use claim, per-patient clinical claim, or generalization beyond these 99 cases. Phase B is not authorized by this document.

## Layer A — Finding

The frozen top ten carry 50.63509495830807% of total absolute contribution and 8.961200117675944% of eligible support in the realized 99-case cohort [cite: support_shares.json | sole_disproportionality_comparison | head_abs_contribution_share,head_support_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
The all-case descriptive rank association is small, rho 0.07085961657390227, without an interval or sampling claim [cite: support_shares.json | descriptive_displays | spearman_rho_abs_contribution_vs_support | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
The separate 79.28912778985707% signed share is net-reversal accounting after cancellation, not contribution per unit support [cite: support_shares.json | reversal_accounting | signed_head_net_gap_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
The clinical dictionary passed the minimum schema gate, but zero phenotype rows were opened, so no clinical conclusion exists yet [cite: summary.json | clinical_minimum_set_supported=true,phenotype_rows_opened=0 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
The main caveat is finite-population, outcome-selected scope: the arithmetic is exact for these cases but does not establish recurrence or explanation.

## Layer B — Derivation narrative

The human-approved contract and two-round cross-family code review preceded one deterministic authorized Phase-A variant. The provenance flow was 101 exclusions-table records in, two bookkeeping records excluded (`sub-stroke0142` duplicate/noncanonical lesion bookkeeping and `sub-stroke0043` source-corrupt case), and 99 unique cases analyzed with an exact contribution-table ID match [cite: provenance_gate.json | analyzed_rows=99,bookkeeping_rows,unique_analyzed_ids=true,id_set_matches_contribution_table=true | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66]. All 99 support counts were finite positive integers, all frozen census cross-checks passed, and no discrepancy was recorded [cite: provenance_gate.json | b_finite_positive_integer_count=99,census_cross_checks.checks,pass=true,discrepancies=[] | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66]. The authorized support arithmetic used 0.04367036086720666 of 0.08624524334982282 absolute contribution and 2,025,630 of 22,604,450 support voxels for the frozen head [cite: support_shares.json | sole_disproportionality_comparison | head_abs_contribution_sum,total_abs_contribution_sum,head_support_voxels,total_support_voxels | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66]. The dictionary inventory documented the proposed clinical constructs without opening a phenotype row, and Phase A reached `PHASE_A_COMPLETE_REQUIRES_AMENDMENT`; neither preregistered stop fired [cite: proposed_variable_freeze.json | constructs,minimum_set.supported=true | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: summary.json | phenotype_rows_opened=0,status=PHASE_A_COMPLETE_REQUIRES_AMENDMENT | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].

## Layer C — Deep justification

| Class | Decision-grade claim | Exact source |
|---|---|---|
| Demonstrates | Exact finite-population concentration: absolute-contribution share 0.5063509495830807 versus support share 0.08961200117675944. | [cite: support_shares.json | sole_disproportionality_comparison | head_abs_contribution_share,head_support_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Suggests | Eligible-support quantity alone does not describe the realized concentration well; this is only suggestive because there is no case-level sampling uncertainty and the subgroup was selected from the same census. | [cite: support_shares.json | sole_disproportionality_comparison | head_abs_contribution_share,head_support_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: support_shares.json | descriptive_displays | spearman_rho_abs_contribution_vs_support | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Positive finding | Phase A completed its preregistered successful terminal with the provenance and minimum-schema gates passed. | [cite: provenance_gate.json | pass=true | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: summary.json | clinical_minimum_set_supported=true,status=PHASE_A_COMPLETE_REQUIRES_AMENDMENT | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Negative finding | The descriptive rho is 0.07085961657390227; it is not an inferential null or evidence of independence. | [cite: support_shares.json | descriptive_displays | spearman_rho_abs_contribution_vs_support | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Does not establish | Any clinical association or absence of one: phenotype rows opened = 0. | [cite: summary.json | phenotype_rows_opened=0 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Validity failures | None observed; the provenance gate passed with no discrepancies, and the clinical schema was supported. | [cite: provenance_gate.json | pass=true,discrepancies=[] | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: summary.json | clinical_minimum_set_supported=true | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |

The procedure was deterministic. Seed uncertainty does not apply to Phase-A arithmetic; uncertainty lies in case selection and external scope. Therefore exact cohort arithmetic is demonstrated, while broader effect language is not.

## Next decision

**ADVANCE — narrowly to the Phase-B contract amendment and fresh human approval.** Bind the dictionary-derived variable list and Phase-A artifact hashes, replace the required-output interface, register Phase A as a consumed artifact, and do not stage or read phenotype bytes until the amended blob is approved. This does not authorize execution and does not complete idea 047.


===== ideas/047/feasibility.md =====
# Feasibility memo — idea 047

**Idea:** Aggregate clinical profile and support-share arithmetic of the frozen
idea-046 top ten.  
**Stage:** feasibility. **Date:** 2026-09-02.  
**Verdict:** **REVISE** — feasible after a material simplification; do not
approve the current draft contract.

This memo evaluates the post-debate, post-ruling card. Labels distinguish
directly verified facts, source-supported interpretations, and unresolved
assumptions. No phenotype row, lesion mask, or reserved case was opened during
this stage.

## 1. Decisive repository finding

**Verified fact:** the proposed support variable already exists in the
ratified take-13 bundle. `probes/023/results/results_v2/exclusions.csv`
(SHA-256
`58e9f8ab7cea38e6717319a26ea6a590dc7d1ad0d42d6b30dca648b0509a5a71`)
contains 99 `analyzed_case` rows, one for every case in the frozen idea-046
contribution table, and a populated integer `eroded_region_voxels` value for
each. The frozen take-13 code defines that field at `coordinate_arrays()` as
the eligible region after Tmax > 6 s thresholding, six-neighbor one-voxel
erosion, array-midline exclusion, per-patient CBV-p98 vessel exclusion, and
map finiteness/positivity filtering. This is exactly the card's `B_i`, not the
rejected q1+q4 proxy.

The extra manifest row for `sub-stroke0142` is explicitly an
`excluded_archive_lesion` bookkeeping row with blank support fields; filtering
on `record_type == analyzed_case` yields the unambiguous 99-row one-to-one
join. The contribution-table and census-summary hashes also reproduce their
contract pins.

**Consequence:** Phase A as drafted would selectively extract 693 archive
members, stage about 3 GB of maps, and rerun 99 cases merely to recreate an
already imported claim-bearing output. That is unnecessary and creates new
environment, extraction, and transcription failure surfaces. It also conflicts
with the collaborator rule to prefer the smallest decisive experiment. The
operator's ruling correctly rejected q1+q4 as total support; it did not make
the already recorded exact `eroded_region_voxels` invalid. Because the current
contract explicitly freezes map recomputation, changing this requires a
reviewed contract revision, not an informal execution choice.

## 2. Dataset, access, license, modalities, and labels

**Verified from the official Zenodo API for immutable record 16813698 on
2026-09-02:** `train.7z` is 99,014,629,647 bytes with MD5
`36ae28b9a17f7340b8bbef62b595cb57`; `clinical_data-description.xlsx` is
12,149 bytes with MD5 `c8d806a021614c6bb9f732756f9701d4`; the license is
CC BY-NC-SA 4.0. The record is openly retrievable without a DUA or account.
The held archive has already passed the same archive MD5 in the parent work.
Any released derivative must respect the noncommercial/share-alike terms.

**Verified from the official dataset paper** (Riedel et al., Radiology:
Artificial Intelligence, DOI `10.1148/ryai.250603`) and challenge report
(de la Rosa et al., arXiv `2408.10966`): ISLES'24 contains acute NCCT, CTA,
4-D CTP and derived perfusion maps, subacute follow-up MRI at 2–9 days, and
longitudinal clinical data. The published dataset comprises 245 cases across
two centers (149 released training cases and 96 held-out cases in the final
paper); earlier challenge documents state approximately 150/100, so payload
counts, not early prose, govern this study. Final-infarct delineations are
derived from follow-up MRI with automated segmentation and expert quality
control. The official challenge evaluates final-infarct segmentation with
Dice and absolute volume difference using case-level rank aggregation.

Those segmentation labels and official metrics are contextual here, not this
study's outcomes. **Source-supported interpretation:** the parent `c_i` values
are outcome-derived because idea 023 used the follow-up-infarct masks, but idea
047 neither rereads nor revalidates those masks. Its clinical variables are
released measurements, not new annotations. Consequently there is no fresh
annotation burden, but the analysis is necessarily exploratory and cannot be
an independent validation of the outcome-derived head.

## 3. Clinical schema and label availability

The official `clinical_data-description.xlsx` was downloaded by immutable
record-file URL and checksum-verified during this stage; only this dictionary
was read. **Verified fields** include `Age`, `Sex`, `NIHSS at admission`,
`NIHSS 24h`, `NIHSS discharge`, `MRS 3 months`, and `mTici
postinterventional`, with descriptions and data types. This resolves the
card's time-point uncertainty: the release documents both admission and 24-hour
NIHSS, so the lineage's 24-hour field need not be replaced by admission NIHSS.

The archive manifest contains one baseline-demographic and one outcome CSV for
each of the 149 released cases, with 99/99 file-level coverage of the analyzed
cohort. **Not verified by design:** case-row column spellings, actual
missingness, usable n per field, or whether all dictionary fields are populated
for these cases. Those facts require the D3-restricted phenotype read. The
dataset paper explicitly reports smaller denominators for some clinical
variables, so missingness is expected rather than hypothetical.

The minimum clinical schema gate in the draft contract therefore passes at the
documentation level. It does not establish statistical sensitivity in a
10-versus-89 comparison.

## 4. Sample structure and split unit

The analysis unit is the patient/case. The frozen table has 99 unique cases;
the head is the already ratified signed-rank 1–10 group and the comparison is
the remaining 89. No voxel may be treated as an independent clinical sample.
The 49 non-analyzed released cases remain an untouched reserve and are outside
this candidate; `sub-stroke0043` is already excluded for its documented corrupt
CBF member.

No train/validation/test split can make this confirmatory: the 99 imaging
outcomes were opened in idea 023 and the subgroup was selected from their
realized contributions. Freezing the phenotype analysis before the first
clinical-row read prevents analyst adaptation but does not undo this outcome
selection. Results are finite-population descriptions of these 99 cases only.

## 5. Closest work and exact gap

- **Closest clinical/perfusion error study:** Broocks et al., Radiology 2024,
  DOI `10.1148/radiol.231750`, PMID `39078297`, analyzed 721 thrombectomy
  patients and associated CTP core overestimation with baseline core volume and
  reperfusion. It clinically profiles threshold error, but not a frozen
  per-case contribution head from an ISLES'24 band estimator.
- **Closest ISLES'24 clinical secondary analysis found:** “Infarct-volume
  prognostic value depends on outcome ascertainment and validation design in
  public stroke MRI datasets,” European Journal of Radiology (online 2026),
  DOI `10.1016/j.ejrad.2026.113200`, uses ISLES'24 mRS and explicitly audits
  center and outcome-availability effects. This materially narrows the claimed
  gap: joining ISLES'24 imaging summaries to clinical outcomes is no longer an
  unpublished category. Its estimand is incremental prognostic value of infarct
  volume under center-held-out validation, not clinical description of the
  frozen idea-046 contribution head or absolute-contribution-share versus
  eligible-support-share arithmetic.
- Maier-Hein et al., Nature Communications 2018, DOI
  `10.1038/s41467-018-07619-7`, establish that challenge conclusions can change
  with cases, metrics, aggregation, and annotations. This supports the
  benchmark-audit motivation but is not an estimand-level predecessor.
- The ISLES'24 challenge report, arXiv `2408.10966`, uses clinical data as model
  inputs and reports segmentation performance; it does not publish this
  contribution census.

**Search result, not proof of novelty:** no exact duplicate of the frozen
top-ten clinical profile plus support-share decomposition was located. The card
must delete the broader statement that no ISLES'24 phenotype-join secondary
analysis was found and cite the 2026 EJR paper as the closest dataset-specific
neighbor. The exact gap remains narrow and repository-lineage-specific.

## 6. Existing assets, baselines, metrics, and compute

Existing assets are unusually strong: the contribution table, head membership,
absolute-mass share, exact eligible-support table, frozen region implementation,
archive manifest, D3/D4 governance, and checksum-pinned archive are all present.
No model, checkpoint, GPU, or new annotation is required.

The appropriate baselines are internal arithmetic identities, not challenge
segmentation scores:

1. exactly 99 analyzed support rows join one-to-one to 99 contribution rows;
2. frozen head membership and the previously ratified absolute-contribution
   share reproduce from the pinned contribution table;
3. the head's share of total `eroded_region_voxels` is computed once and shown
   beside the absolute-contribution share;
4. all 99 cases appear in the rank-discrepancy display, with fixed tie handling.

For the clinical clause, accepted descriptive outputs are group distributions,
missingness, and prespecified standardized/ordinal/binary contrasts. There is no
accepted benchmark metric for “clinical markedness,” and the contract correctly
prohibits such a verdict. The proposed random-relabeling “95% ranges” are not
sampling confidence intervals because neither group assignment nor the 99 cases
were randomized. They may be shown only as explicitly hypothetical
exchangeability references; a safer finite-population robustness display is
leave-one-head-case-out sensitivity. The uncertainty currency remains a human
decision and should be resolved in the revision before approval.

**Revised compute estimate:** Phase A can be a hash-and-join audit of four small
in-repo files and should take seconds, not 90 minutes. Phase B still requires a
selective read of 198 tiny phenotype members. If the held archive is locally
available and selective 7z extraction works, CPU time should be minutes; if the
archive must be reacquired, the honest worst case is the proven ~99 GB immutable
download plus integrity check (the parent origin-direct download took about 14
minutes on Colab, but this transfer time is environment-dependent). The current
3 GB map staging and 99-case image pass should be removed.

## 7. Leakage, confounds, and construct limits

The dominant confounds are not scanner or model leakage:

- **Selection/outcome coupling:** head membership comes from a final-infarct
  outcome-derived statistic. Later mRS and NIHSS share stroke severity,
  treatment, territory, and time pathways with that statistic. A positive
  clinical contrast cannot identify a subtype or explain dominance.
- **Eligible-support mediation:** larger eligible regions may mechanically
  increase absolute contribution and correlate with clinical severity. Showing
  every clinical contrast jointly with `B_i` reveals but does not remove this
  structure; no adjustment model is licensed with only ten head cases.
- **Center and missingness:** the official dataset is two-center, and the 2026
  EJR neighbor shows that outcome availability and center-held-out validation
  matter in ISLES'24. Center must therefore be included in the dictionary-frozen
  context if available, and missingness must be reported by group. With only ten
  head cases, this is descriptive context, not a corrected causal estimate.
- **Multiplicity/privacy:** every frozen variable must be displayed, no
  significance-selected headline is allowed, and small cells must remain
  suppressed. Aggregate output does not authorize patient-level clinical claims.

Concept validity is correspondingly bounded. mRS is global disability, NIHSS is
neurologic deficit severity at a named time point, and eligible support is the
take-13 estimator's analysis territory—not gross infarct volume, tissue at risk,
or biological “abundance.” The study measures association and arithmetic only.

## 8. Smallest probe of the riskiest remaining assumption

The map-reproduction gate is no longer the smallest probe because its intended
output is already present. The smallest decisive probe is phenotype-blind and
table-only:

1. hash `exclusions.csv`, `per_case_contributions.csv`, and
   `census_summary.json` against frozen identities;
2. filter `exclusions.csv` to `record_type == analyzed_case`;
3. require 99 unique case IDs and an exact set match to the contribution table;
4. require 99 finite positive integer `eroded_region_voxels` values and no
   duplicate analyzed rows;
5. verify from frozen code/blob and contract/blob that this field has exactly
   the `B_i` definition claimed; then freeze the support input hash.

That probe tests the real remaining support risk—provenance and join identity—
without touching maps or clinical rows. The riskiest assumption after it is
phenotype completeness. The smallest probe for that is the already planned
dictionary freeze followed, only after fresh authorization, by a D3-restricted
schema/missingness census of the 198 phenotype files before any contrast is
calculated. If fewer than seven head cases are nonmissing for a variable, that
row is descriptive but too weak for a bounded-null claim.

## 9. Required revision before GO

1. Replace map restaging/recomputation with the pinned, 99-row analyzed-case
   extract from `exclusions.csv`; add its SHA-256 and exact provenance checks.
2. Remove the 495 image/NCCT members from Phase A. Stage only the dictionary
   and, behind the Phase-B authority gate, the 198 phenotype members.
3. Update the dictionary freeze: both admission and 24-hour NIHSS are officially
   documented; choose the lineage-preserving 24-hour field as primary/contextual
   according to the revised analysis specification rather than treating its
   existence as unknown.
4. Resolve the clinical uncertainty display before approval. Do not label a
   random-relabeling range as confidence or sampling uncertainty; either retain
   it as an explicitly hypothetical reference plus leave-one-head-out sensitivity,
   or use only effect estimates and deterministic sensitivity displays.
5. Add center and per-group missingness to the mandatory context if the schema
   permits, and cite DOI `10.1016/j.ejrad.2026.113200`; narrow the novelty text.
6. Preserve the two-phase authority boundary: no phenotype row read before the
   amended contract receives fresh human approval.

This is a **REVISE**, not a pause or scientific no-go. All essential data exist,
the primary support quantity is already computed under the exact frozen method,
and the clinical schema is documented. The revision removes work and risk while
leaving both registered clauses intact.

## In plain terms

Yes, this study can be done, but the current plan is more expensive than it
needs to be. The exact imaging-support number is already stored for all 99
patients, so the imaging rerun should be replaced by a quick provenance and
join check; the remaining work is a restricted read of small clinical files
inside a checksum-pinned 99 GB archive. The biggest practical risk is that only
ten patients are in the dominant group and some clinical fields may be missing,
so an unremarkable comparison could be too imprecise to say much. **Verdict:
REVISE.**


===== ideas/047/idea_card.json =====
{
  "id": "isles24-scout-010-c01",
  "track": "wide",
  "title": "The keystone ten meet the clinic: aggregate clinical profile and support-share arithmetic of the census head",
  "question": "[ecology] In the frozen 99-case idea-046 census cohort, do the ten largest signed contributors to the band-2/3 reversal (the frozen signed-rank top ten) differ in aggregate on a pre-frozen released clinical variable list from the other 89 cases -- and how does their exact share of total absolute contribution compare with their exact share of total eligible deficit support, the per-case eroded Tmax>6s region voxel count recomputed under the ratified take-13 parameters?",
  "register": "descriptive-association. Operator steering note of 2026-09-02 (evidence/decisions.md) requests exactly this successor in the descriptive register and explicitly excludes model-use formulations of this direction; the wide-track deliverable template ('the model is using X') is overridden for this candidate by that human-authored direction.",
  "parent_ids": [
    "idea-046",
    "idea-045",
    "idea-023"
  ],
  "lineage_note": "Enters as a separately registered successor citing the idea-046 census and debate, per ideas/046/interpretation.md Next-decision item 4. The phenotype join was pre-registered 2026-08-28 and never executed. Debate closed REVISE; the operator ruling in ideas/047/unblock_ack.txt resolved the debate's open code question -- the cached q1+q4 counts are per-band quartile-cell counts, not total eligible support -- freezing the exact-map recomputation branch and adopting the round-3 finite-population design, which this revision implements.",
  "design_template": "conditional-observational",
  "design_template_justification": "The lineage direction is definitionally observational (aggregate description of frozen strata). Diversity across this cycle's set is carried by c02 (natural-paired) and c03 (other:value-lattice-audit); no two candidates share a grammar.",
  "borrowed_construct": "Ecology's keystone-species framing (Power et al. 1996, BioScience 46:609-620, DOI 10.2307/1312990): impact disproportionate to abundance. Demoted per critique D2 from endpoint to motivation: 'abundance' has no unique analogue here, so the construct is operationalized only as exact share arithmetic -- the head's share of total absolute contribution beside its share of total eligible deficit support -- with no regression, no residual subgroup, and no 'keystone' verdict. 'Disproportionate' may be used only as an arithmetic comparison of the two exact shares, scoped to the realized 99 cases.",
  "deliverable_sentence": "In the frozen 99-case idea-046 census cohort, one pre-frozen aggregate estimation table: (a) for the frozen signed-rank top ten versus the other 89 cases, per-variable distributions, standardized contrasts with exploratory-labeled uncertainty, and missingness for a clinical variable list frozen from clinical_data-description.xlsx before any case-level read (targeting the release's 3-month mRS, admission NIHSS, age, and sex fields), every row displayed jointly with eligible deficit support per D4; and (b) the head's exact share of total absolute contribution beside its exact share of total eligible deficit support (per-case eroded Tmax>6s region voxels recomputed under the ratified take-13 parameters), with the casewise rank-discrepancy distribution and Spearman rho shown descriptively and the 79.29% net signed share reported only as separately labeled reversal accounting -- an exploratory, aggregate-only, association-register description of these 99 realized cases under the D3 read-restriction, with no per-patient claims, no significance-selected headline, no generalization beyond the 99 cases, and no model probing.",
  "X_measurement": "Contribution: per-case signed c_i and signed_rank, frozen in probes/046/results/results_v3/per_case_contributions.csv. The head's absolute-contribution share sum_head|c_i|/sum_all|c_i| is already tabulated in the ratified census: census_summary.json top_k 10 absolute_mass_share = 0.5063509495830807, valid for the signed-rank head because the signed and absolute top-ten sets coincide (see keystone_evidence). Support: B_i = exact eligible deficit support, the voxel count of the take-13 eligible analysis region -- eroded Tmax>6s deficit under the ratified take-13 parameters, including the frozen midline-band, per-patient p98 vessel-exclusion, and finiteness rules -- recomputed label-blind from the archive's 99 tmax/cbf/cbv/mtt maps with the frozen take-13 region machinery (contract 03d4545fe293 era). The 2026-09-02 operator ruling (ideas/047/unblock_ack.txt) froze this exact-map branch after code inspection showed the cached q1+q4 counts are per-band quartile-cell counts, not total eligible support. Reproducibility gate: before any B_i is used, the recomputation must reproduce all 297 cached per-band q1_voxels/q4_voxels values in probes/023/results/results_v2/per_patient.csv exactly; any mismatch stops the support clause for escalation rather than admitting a variant region. Clinical: variable list frozen from clinical_data-description.xlsx (dictionary-only read) before any case-level phenotype file is opened, targeting the release's 3-month mRS, admission NIHSS, age, and sex fields, with exact field names, time points, coding, missingness rules, and the per-variable contrast statistic fixed at that step; at most three additional contextual fields (e.g. reperfusion status, onset-to-imaging time) may be predeclared at the same step if the dictionary shows them -- one decision, made once, before any case row.",
  "use_vs_association": "No use claim is made anywhere: the candidate is deliberately in the association register per the operator steering note. The discriminating content is descriptive twice over: whether the head's dominance is proportionate to its eligible imaging territory (exact arithmetic), and whether large aggregate clinical separation accompanies it (estimation display). Neither reading attributes anything to a model.",
  "keystone_prerequisite": "(1) The frozen per-case contribution table exists in-repo under the ratified census; (2) per-case phenotype files carrying the ses-02 outcome family and ses-01 baseline variables exist inside the held, checksum-verified training archive; (3) per-case perfusion-map members (tmax, cbf, cbv, mtt) required by the frozen exact-map support recomputation exist in the same archive for all 99 analyzed cases.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "(1) probes/046/results/results_v3/per_case_contributions.csv on main: header 'case_id,d_band2,d_band3,delta,contribution,signed_rank', 99 data rows, top row 'sub-stroke0153,...,0.007141719141395045,1'; census_summary.json: signed head share 0.7928912778985707 and absolute-mass head share 0.5063509495830807 (top_k 10); 39 negative contributions. Signed and absolute top-ten sets coincide: the largest negative magnitude 0.0029141878799591753 is smaller than the tenth-largest positive contribution 0.002976074880714717 (sorted-column check, 2026-09-02). (2) Archive manifest at origin/results/probe-023-349af5ad0b3e:probes/023/results_v2/archive_manifest.csv (manifest of the md5-verified train.7z): rows 'train/phenotype/sub-stroke0001/ses-01/sub-stroke0001_ses-01_demographic_baseline.csv,405,184c4588' and 'train/phenotype/sub-stroke0001/ses-02/sub-stroke0001_ses-02_outcome.csv,98,6f8fa8cd'; 149 members each; keystone screen verified 99/99 coverage for both families. (3) Same manifest, verbatim row 'train/derivatives/sub-stroke0001/ses-01/perfusion-maps/sub-stroke0001_ses-01_space-ncct_tmax.nii.gz,6580435,bf32937b'; unique-case joins of manifest members against the 99 census ids give 99/99 for each of tmax, cbf, cbv, and mtt, and 99/99 for the rawdata NCCT (verified 2026-09-02 at revision). The single known source-defective member (sub-stroke0043 ses-01 cbf) belongs to a case already excluded from the 99.",
  "verified_dataset_facts": [
    "Zenodo record 16813698 (v3, 2025-08-12): open access, license 'Creative Commons Attribution Non Commercial Share Alike 4.0 International'; files train.7z (99.0 GB) and clinical_data-description.xlsx (12.1 kB); description states clinical data 'demographics, patient history, admission NIHSS, 3-month functional outcome (mRS), etc.' and '149 acute ischemic stroke cases'. This is the exact record this program holds (md5 36ae28b9... match recorded in evidence/decisions.md, 2026-08-25).",
    "Dataset paper arXiv:2408.11142 (Radiology: AI DOI 10.1148/ryai.250603): follow-up MRI at 2-9 days; 'delineated infarction masks in follow-up MRI'; multicenter, 245 cases total across splits.",
    "Challenge paper arXiv:2408.10966: training n=150 with hidden test set (abstract fetch reported 150/98; a secondary read of the updated version reported 149/96); the held training payload contains 149 cases -- payload count outranks prose per the 2026-08-25 standing lesson.",
    "The 99 analyzed census cases are the take-13 cohort (149 minus exclusions; sub-stroke0043 source-defective member excluded per contract policy).",
    "Archive member manifest of the md5-verified train.7z: per-case perfusion maps live under train/derivatives/<id>/ses-01/perfusion-maps/ (tmax, cbf, cbv, mtt; 149 members each; ~6.6 MB for the case-0001 tmax member), and all four families plus the rawdata NCCT cover 99/99 of the analyzed census cases (joins performed 2026-09-02)."
  ],
  "smallest_decisive_experiment": "Frozen ordered plan, no step reordered at execution: (a) dictionary-only read of clinical_data-description.xlsx; freeze exact variable names, time points, coding, missingness rules, per-variable contrast statistics, and any predeclared contextual fields (max three); document the NIHSS time-point reconciliation against idea-046's frozen 24-hour field. (b) One selective-extraction staging event from the held archive: the 99 cases' tmax/cbf/cbv/mtt maps plus the 99 phenotype CSV pairs, identifiers restricted per D3. (c) Run the frozen take-13 region machinery; pass the exact reproducibility gate (all 297 cached q1/q4 counts reproduced); emit B_i label-blind. (d) Support clause: report sum_head|c_i|/sum_all|c_i| beside sum_head B_i/sum_all B_i; display the casewise rank(|c_i|)-rank(B_i) distribution with the head's ten values marked and descriptive Spearman rho; report the 79.29% signed share separately as reversal accounting. (e) Clinical clause: open phenotype rows only now; produce the single aggregate estimation table, every variable displayed jointly with B_i per D4, small cells suppressed. (f) Stop. No permutation machinery anywhere in the support clause; clinical uncertainty exploratory-labeled only.",
  "compute_envelope": "Honestly priced end-to-end: one selective-extraction staging event against the held, md5-verified ~99 GB train.7z (the same event the D3 phenotype staging requires), yielding ~3 GB of perfusion maps (396 files at ~7 MB each by manifest) plus ~50 kB of phenotype CSVs and the 12.1 kB dictionary; a CPU-only region pass over 99 cases (the take-13 label-blind map pass over this cohort completed within one Colab session, and this pass re-runs only its region machinery); then minutes of arithmetic on tables under 100 kB. No GPU, no model, no checkpoint, no new annotation.",
  "most_dangerous_confound": "Deficit-burden mediation (the lineage's D4 concern): larger eligible territory both mechanically inflates |c_i| and predicts worse clinical outcomes for ordinary reasons, so 'the dominant cases are sicker' can be pure volume. The design measures this rival directly: the support-share axis prices exactly how much of the head's dominance its territory accounts for, and every clinical row is displayed jointly with support per D4. What the design cannot cure (critique D5): the head is selected on a realized outcome-derived quantity, so any positive clinical association remains observational and selection-structured and cannot establish a clinical subtype or explain dominance; the card's wording rules prohibit those readings.",
  "standing_confounds_addressed": "(1) Volume mediation -- measured as the support-share axis; see most_dangerous_confound. (2) Opened outcomes: the 99 imaging outcomes were read in idea-023, so the study is exploratory by construction and says so; freezing definitions before computation is a discipline commitment, not blindness. (3) Multiplicity: short dictionary-frozen variable list, every row reported jointly, no significance-selected headline, all inferential displays labeled exploratory. (4) Selection: both strata are frozen by prior ratified artifacts, and the analyst-defined residual subgroup is removed, so no post-hoc grouping exists anywhere in the design. (5) Phenotype staging and reads restricted to the 99 analyzed identifiers per D3; categorical cross-tabs suppress small cells to avoid case re-identification.",
  "dies_like_prior": "IDENTIFIABILITY_FAILURE (x12) killed model-use attributions; this candidate makes no use claim, and its main rival reading (territory mediation) is measured as an exact axis rather than left as a confound. DATA_ACCESS (x3): every input is member-verified in held assets -- contribution table in-repo; phenotype 99/99 x2 and perfusion maps 99/99 x4 confirmed in the checksum-verified archive manifest. EFFECT_UNREACHABLE (x1): no effect-size floor is claimed; the clinical null is declared sensitivity-limited up front, and the support clause has no sensitivity limit at its stated scope.",
  "closest_prior_work": "Broocks et al., Radiology 2024 (DOI 10.1148/radiol.231750, PMID 39078297): in 721 private-cohort patients, showed rCBF-threshold core overestimation is clinically marked (larger baseline core, successful recanalization). Exact delta: they profile deviation from a single fixed threshold on a private cohort; this candidate profiles frozen per-case contribution shares of a band contrast on a public benchmark, adds an exact contribution-share versus support-share comparison, and is bound to pre-registered read-restriction and joint-display rules.",
  "novelty_neighbors": [
    "Maier-Hein et al., 'Why rankings of biomedical image analysis competitions should be interpreted with care', Nature Communications 2018, DOI 10.1038/s41467-018-07619-7 -- benchmark conclusions hinge on test-set composition (bootstrap over cases), but no frozen per-case contribution census and no clinical profiling of influential cases.",
    "de la Rosa et al., 'ISLES'24: Final Infarct Prediction with Multimodal Imaging and Clinical Data', arXiv:2408.10966 -- the organizers use the clinical variables as model inputs for prediction; no influence decomposition, no dominant-versus-rest description.",
    "Broocks et al., Radiology 2024, DOI 10.1148/radiol.231750 -- closest in spirit; delta as stated in closest_prior_work."
  ],
  "novelty_delta": "No published secondary analysis joining ISLES'24 imaging with its released phenotype tables was found by search (one unconfirmed near-miss: Tomography 2026, DOI 10.3390/tomography12030029, full text inaccessible); the specific object -- descriptive clinical profiling of a frozen estimator-dominance census with an exact contribution-share versus support-share comparison -- appears unpublished.",
  "why_not_done": "NEW_CAPABILITY: the frozen, ratified per-case contribution census (probes/046/results/results_v3, imported 2026-09-01) exists only inside this program, and the ISLES'24 phenotype tables have been public only since 2024-2025.",
  "audience_relevance": "Anyone reusing threshold- or band-based perfusion contrasts on this public benchmark inherits the head-dominance the census proved. This study prices that dominance twice: the support-share comparison settles, exactly and for these 99 cases, how much of it is proportionate to eligible imaging territory; the clinical table either surfaces a large aggregate separation worth a properly sampled successor or bounds how much separation a 10-versus-89 comparison could have detected. Both outputs discipline how band contrasts on this dataset may be read.",
  "unverified_claims": [
    "Exact column names, coding, and per-case missingness of outcome.csv and demographic_baseline.csv -- deliberately unverified until the dictionary-only freeze; the D3 protocol forbids earlier case-level reads.",
    "Whether the release contains a 24-hour NIHSS field: idea-046's frozen optional rung named NIHSS at 24 hours, while the record-level description promises admission NIHSS. Reconciled at the dictionary freeze; if a 24-hour field is absent, admission NIHSS enters as a documented forward correction, not as execution of the old frozen list (critique D1).",
    "The reproducibility gate has not yet been run: the recomputed take-13 region machinery must reproduce all 297 cached q1_voxels/q4_voxels values exactly before any B_i is used; on mismatch the support clause stops and escalates rather than substituting a variant region.",
    "The Tomography 2026 near-miss (DOI 10.3390/tomography12030029) remains unread in full; whether it joins ISLES'24 phenotype tables is unconfirmed."
  ],
  "scores": {
    "clarity": {
      "value": 4,
      "why": "One compound sentence with every term operationalized: frozen head, exact shares, named support variable with a frozen recomputation branch and reproducibility gate, dictionary-first clinical freeze. Below 5 only because the exact release field names and coding are frozen at the dictionary step rather than already known."
    },
    "identifiability": {
      "value": 3,
      "why": "For a descriptive claim, the design measures the main rival reading -- territory-proportionate dominance -- as an exact arithmetic axis instead of leaving it as a confound, and no analyst-defined subgroup exists anywhere. Irreducible residuals are stated: observational selection structure (critique D5) and 10-versus-89 sensitivity limits on the clinical clause."
    },
    "medical_relevance": {
      "value": 3,
      "why": "Tells researchers whether a reproducible perfusion-band anomaly on a public benchmark coincides with distinctive aggregate clinical severity; plausible utility for interpreting such contrasts, but no direct care consequence and no biomarker validation from 99 selected training cases."
    },
    "interest": {
      "value": 3,
      "why": "Program-central and operator-requested closure of a pre-registered join; outside the program it is a useful niche result about who carries benchmark-scale contrasts."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Census frozen and ratified in-repo (including the head's absolute-contribution share), D3/D4 protocols ratified, archive held and checksum-verified, take-13 region machinery frozen and complete; but the support variable itself must still be recomputed from maps -- real new execution, not a table read."
    },
    "feasibility": {
      "value": 4,
      "why": "Keystone INSPECTED_TRUE lifts the cap. One selective staging event from the held 99 GB archive (~3 GB of maps plus ~50 kB phenotype), a CPU-only 99-case region pass bound by an exact reproducibility gate, then minutes of arithmetic: first result in days, honestly priced -- not the 'minutes on 50 kB' the pre-revision card claimed."
    },
    "data_readiness": {
      "value": 4,
      "why": "All inputs member-verified in held assets: contribution table in-repo; phenotype (99/99 x2) and perfusion maps (99/99 x4, plus NCCT) confirmed in the md5-verified archive manifest. One staging event stands between held bytes and analysis-ready files."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "The support clause needs no custom metric -- two exact finite-population shares. The clinical clause is a custom but fully pre-frozen estimation display; no accepted external metric exists for it."
    },
    "negative_result_value": {
      "value": 3,
      "why": "Split by clause: the support-share comparison is decisive either way at its stated 99-case scope (exact arithmetic, no sensitivity limit); the clinical null is sensitivity-limited at 10-versus-89 but bounded -- the table reports the effect sizes its precision could have excluded, and no stronger 'clinically silent' reading is permitted."
    },
    "novelty_confidence": {
      "value": 4,
      "why": "Searched: no ISLES'24 phenotype-join secondary analysis found; nearest work (Broocks 2024) differs in cohort, estimand, and design; the census object is unique to this program. Not 5: absence of evidence from search is not proof."
    },
    "regret": {
      "value": 4,
      "why": "Pre-registered 2026-08-28, never executed, and explicitly requested by the operator steering note; skipping it again would be obvious-in-hindsight."
    }
  },
  "plain_pitch": "An earlier experiment in this program found that a puzzling reversal in how stroke lesions relate to blood-flow levels is carried mostly by about ten of 99 patients. This study does two modest things. First, it computes, for each patient, how much eligible imaging territory their contribution came from, and reports plain arithmetic on these 99 cases: the ten dominant patients' share of the total contribution beside their share of the total territory. That comparison is exact for these patients whichever way it comes out. Second, it describes, in aggregate only, how the ten compare with the other 89 on the dataset's released clinical records -- disability three months after the stroke, stroke severity at admission, age, and sex. A large clinical difference, if present, would show up; if none appears, the study reports how much difference a ten-versus-89 comparison could have detected, which is a bounded and honest answer. Because these patients' images were already examined earlier in the program, the study is exploratory by construction and makes no claim about any individual patient or about patients outside this dataset.",
  "charter": "isles24"
}


===== ideas/047/interpret_review.md =====
# Interpret review — idea 047, Phase A (cross-family checker)

Reviewing family: Claude. Document under review:
`ideas/047/interpretation.md` (round 1). Results bundle:
`probes/047/results/results_v2/` at commit
`6037f24122766fe1c68f16eb9f38d9a16c2c5e66` (verified: that commit
introduces exactly the 17 bundle files plus the import receipt).
Governing contract blob `b4887c05a21bfe870589b5d9982066943df679d5`
(corroborated in `resolved_config.json:contract_blob` and
`ideas/047/state.json` approval, stale=false).

Note on check 2's inherited wording: the stage checklist's "tier 2 /
vendor scope / anchor exclusion / baseline-not-floor" items are 004-era
specifics. Their 047 analogs, applied here: no threshold/margin/verdict
language in the support clause; finite-population scope and the two
bookkeeping exclusions stated wherever counts appear; the reversal-
accounting share never read as contribution per unit support; and the
deterministic-probe uncertainty constraint (uncertainty located in case
selection and scope, not seeds).

## Check 1 — Citations resolve (transcription-exact)

Every `[cite: ...]` tag was opened and resolved against the bundle.
All pass. Enumerated:

1. `support_shares.json | sole_disproportionality_comparison |
   head_abs_contribution_share,head_support_share` — file holds
   0.5063509495830807 and 0.08961200117675944. Layer A's
   "50.63509495830807%" and "8.961200117675944%" are exact digit-shift
   conversions; Layer C row 1 quotes the raw fractions verbatim. PASS.
2. `support_shares.json | descriptive_displays |
   spearman_rho_abs_contribution_vs_support` — 0.07085961657390227,
   quoted verbatim in Layer A, the Suggests row, and the
   negative-finding row. Independently recomputed by this reviewer from
   the file's own `rank_discrepancy_sum_d_squared` = 150242:
   1 − 6·150242/(99·(99²−1)) = 1 − 901452/970200 =
   0.07085961657390227. PASS.
3. `support_shares.json | reversal_accounting |
   signed_head_net_gap_share[,label]` — 0.7928912778985707
   ("79.28912778985707%"), with the `label` field stating exactly the
   after-cancellation / not-per-unit-support restriction the
   interpretation paraphrases. PASS.
4. `summary.json | clinical_minimum_set_supported=true,
   phenotype_rows_opened=0` — both present with those values. PASS.
5. `resolved_config.json | contract_blob=b4887c05...,
   contract_version=2,variants=1,gpu_minutes=0,seed=20260902` — all
   five fields present with exactly those values. PASS.
6. `determinism_manifest_end.json | row_counts.exclusions.csv=101,
   row_counts.per_case_contributions.csv=99` — exact. The narrative
   claim "hashed at the start and end; the recorded manifests agree"
   was verified directly: `diff determinism_manifest_start.json
   determinism_manifest_end.json` is empty, and the manifests cover
   the three frozen tables, take-13 source, and dictionary. PASS.
7. `provenance_gate.json | analyzed_rows=99,bookkeeping_rows,
   unique_analyzed_ids=true,id_set_matches_contribution_table=true` —
   all exact; `bookkeeping_rows` names sub-stroke0142
   (excluded_archive_lesion) and sub-stroke0043 (excluded_case,
   source_corrupt_member), matching the CONSORT sentence. PASS.
8. `summary.json | reserved_cases_accessed=0,phenotype_rows_opened=0`
   — exact. PASS.
9. `provenance_gate.json | b_finite_positive_integer_count=99,
   b_min=1401,b_max=617540,discrepancies=[]` — exact; min/max
   independently confirmed from `per_case_support.csv` column 6
   (sorted: 1401 … 617540). PASS.
10. `provenance_gate.json | census_cross_checks.sign_counts.positive=54,
    zero=6,negative=39,census_cross_checks.checks` — exact; all seven
    check booleans true. The pinned values were additionally re-read
    from the frozen `probes/046/results/results_v3/census_summary.json`
    (top_k 10 absolute_mass_share 0.5063509495830807,
    signed_head_net_gap_share 0.7928912778985707, sign counts 54/6/39).
    PASS.
11. `provenance_gate.json | pass=true,discrepancies=[]` — exact (used
    in three places). PASS.
12. `support_shares.json | sole_disproportionality_comparison |
    head_abs_contribution_sum,total_abs_contribution_sum,
    head_support_voxels,total_support_voxels,...` —
    0.04367036086720666, 0.08624524334982282, 2025630, 22604450, all
    quoted exactly. Reviewer recomputation: summing the ten
    `in_head=True` rows of `per_case_support.csv` by hand reproduces
    2,025,630 voxels and 0.04367036086720666 exactly; the share
    quotients are consistent. PASS.
13. `proposed_variable_freeze.json | dictionary.bytes=12149,
    dictionary.md5=c8d806a021614c6bb9f732756f9701d4` — exact, and the
    staged xlsx in the bundle is 12,149 bytes per the commit stat. PASS.
14. `summary.json | dictionary_cells_inventoried=148` — exact
    (consistent with the 149-line dictionary_inventory.csv incl.
    header). PASS.
15. `proposed_variable_freeze.json | constructs,center.documented=false`
    — constructs mrs_3month, nihss_24h, nihss_admission, age, sex all
    `matched: true` with verbatim dictionary rows; `center.documented:
    false` with empty matches; `minimum_set.supported: true`. The
    interpretation's "proposed bindings, not analyzed clinical
    variables" framing matches the file's own binding_note. PASS.
16. `summary.json | status=PHASE_A_COMPLETE_REQUIRES_AMENDMENT,
    wall_seconds=0.013` — exact. PASS.
17. `summary.json | phenotype_rows_opened=0,analyzed_cases=99` (Layer C
    does-not-establish row) — exact. PASS.

Uncited-quantitative-claim scan: every number outside the result-card
identity block carries a cite. Process facts (human approval of the
exact blob; probe review approved "after two rounds") verify against
`ideas/047/state.json` and `ideas/047/probe_review.md` (revision round
2, APPROVE). No unresolvable citation, no mis-transcription found.

## Check 2 — Claim bounds

- No threshold, cutoff, margin, interval, test, or is/is-not verdict
  appears anywhere in the support-clause prose; Layer A explicitly
  frames the share pair as "an exact descriptive concentration rather
  than a thresholded verdict," and Layer B item 5 states no interval,
  test, margin, or alternative subgroup was run (confirmed: none exists
  in the bundle). Grep for prohibited vocabulary ("clinically
  silent/marked", "keystone", "disproportionate", "significant",
  "p-value", "confidence interval") finds hits only inside the
  out-of-scope disclaimer and the idea title — negations, permitted.
- The Suggests-row phrasing "not simply proportional ... the share pair
  is widely separated" was scrutinized against the contract's
  interpretation_rule and round-3 freeze. It is an arithmetic
  comparison of the two exact shares, scoped with "realized," carries
  no generalization, and is demoted to Suggests with the stated reason
  (no case-level uncertainty machinery; outcome-selected head). Within
  bounds.
- The 79.29% signed share appears only under reversal-accounting
  language and is twice explicitly barred from a per-unit-support
  reading — matching the frozen label in the file. PASS.
- No aggregation appears that the analysis files do not themselves
  contain (shares, sums, rho, sign counts, min/max are all stored
  fields; nothing was pooled or averaged by the author).
- Scope and exclusions stated where counts appear: 99 analyzed of 101
  records, both bookkeeping rows named with reasons, zero reserved
  cases and zero phenotype rows, finite-population caveat in Layer A.
- Deterministic-probe uncertainty constraint: correctly applied. The
  Uncertainty location section places uncertainty in case selection and
  scope, not seeds, and correctly notes the fixed seed 20260902 is
  reserved for Phase-B relabelings (matches the contract's randomness
  clause). PASS.

## Check 3 — Completeness without cherry-picking

What I checked for, in the tables the interpretation draws on:

- `rank_discrepancy.csv` / `per_case_support.csv` (99 rows each,
  consistent head marks): the ten head cases are heterogeneous in
  support — eight have strongly negative rank discrepancies (−32 to
  −91), while sub-stroke0014 and sub-stroke0114 hold support ranks 1
  and 4 (the largest and fourth-largest eligible-support values in the
  whole cohort, 617,540 and 583,847 voxels; discrepancy +4 each). This
  is the closest thing to a complicating feature in the bundle. It does
  not contradict any stated claim: the interpretation's concentration
  claims are aggregate share arithmetic (exact regardless of within-
  head composition), it never asserts that head cases individually
  have small support, and the b_max=617540 the narrative quotes is in
  fact a head case. Omitting the casewise breakdown is legitimate
  selectivity, not suppression.
- Sign structure: the 39 opposing and 6 zero cases are reported (sign
  counts), and the cancellation caveat on the signed share is carried.
- `summary.json` and `provenance_gate.json` were scanned for any field
  contradicting the narrative (discrepancies, kill conditions, smoke
  flag, head_size): none exists; `discrepancies` is empty and
  `pass: true`.
- No stratum-reversal analog exists in this bundle (single cohort, one
  comparison); nothing material is omitted. PASS.

## Check 4 — Verdict separation

- Demonstrates rows are exclusively deterministic finite-population
  arithmetic under frozen inputs, or mechanically gated process facts —
  correct register for a deterministic probe.
- The proportionality reading is confined to Suggests with an explicit
  stated reason; the small rho is classified as a negative finding with
  the "not an inferential null / does not establish independence"
  guard.
- Does-not-establish rows correctly cover all clinical readings
  (phenotype_rows_opened=0) and the signed-share misreading.
- The terminal status is presented as successful completion of Phase A
  only, "not completion of the study," matching the contract's
  positive_pattern, and the Next decision advances only to the
  amendment gate, not Phase B. No exploratory statement is worded
  confirmatorily. PASS.

## Check 5 — Plain-language fidelity

`interpretation.md` contains no plain-summary section (headers: Result
card, Layer A–C, Uncertainty location, Next decision), so this check is
not applicable to the document under review. No hedge-dropping exists
anywhere in it.

## Verdict

All five checks pass. The interpretation is transcription-exact,
bounded within the contract's claim discipline, complete with respect
to the bundle's material content, and correctly separates demonstrated
arithmetic from suggested readings.

```json
{"verdict": "APPROVE"}
```


===== ideas/047/interpretation.md =====
# Interpretation — idea 047, Phase A

## Result card

- **Idea:** idea-047, “The keystone ten meet the clinic”
- **Probe and sequence position:** probe 047, contract v2, **Phase A of two**. This is the phenotype-blind support/provenance and dictionary phase; it precedes the contract amendment, fresh human approval, phenotype staging, and Phase-B clinical comparison.
- **Dataset and pinned release:** ISLES'24 training release, immutable Zenodo record **16813698**; Phase A used only frozen imported program tables and the checksum-pinned `clinical_data-description.xlsx`, not case-level phenotype rows.
- **Primary metric:** the frozen signed-rank top ten's share of total absolute contribution displayed beside their share of total eligible deficit support (`eroded_region_voxels`) across the realized 99-case cohort.
- **Governing contract blob:** `b4887c05a21bfe870589b5d9982066943df679d5`
- **Results-bundle commit:** `6037f24122766fe1c68f16eb9f38d9a16c2c5e66`
- **Authoring family:** Codex. **Reviewing family:** Claude (pending cross-family review at this writing).
- **Out of scope:** This result must not be read as a clinical comparison, a claim that the ten cases are clinically marked or silent, a “keystone” classification, a causal or model-use finding, a per-patient clinical claim, or a generalization beyond these 99 realized cases. It contains no phenotype-row result and does not authorize Phase B.

## Layer A — Finding

The frozen top ten carry 50.63509495830807% of total absolute contribution but 8.961200117675944% of eligible support in these 99 cases, an exact descriptive concentration rather than a thresholded verdict [cite: support_shares.json | sole_disproportionality_comparison | head_abs_contribution_share,head_support_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
Across all 99 cases, absolute contribution and support have only a small descriptive rank association, Spearman rho 0.07085961657390227, with no interval or sampling claim authorized [cite: support_shares.json | descriptive_displays | spearman_rho_abs_contribution_vs_support | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
The separate 79.28912778985707% signed share describes the net reversal after cancellation and does not measure contribution per unit support [cite: support_shares.json | reversal_accounting | signed_head_net_gap_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
The dictionary supports the preregistered minimum clinical schema, but zero phenotype rows were opened, so this phase establishes no clinical difference [cite: summary.json | clinical_minimum_set_supported=true,phenotype_rows_opened=0 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
The most important caveat is that all effect-like quantities are finite-population descriptions of a subgroup selected from the same realized outcome-derived contribution census; they have no sampling uncertainty machinery and cannot establish recurrence in new patients.

## Layer B — Derivation narrative

1. **Authority and review gates.** The exact contract blob was human-approved, and the cross-family probe-code review approved Phase A after two rounds. The executed configuration records contract v2, one authorized variant, zero GPU minutes, and the fixed seed `20260902`; the scientific share arithmetic itself is deterministic and does not depend on that seed [cite: resolved_config.json | contract_blob=b4887c05a21bfe870589b5d9982066943df679d5,contract_version=2,variants=1,gpu_minutes=0,seed=20260902 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
2. **Input identity and split freeze.** All three frozen tables, the take-13 source, and the dictionary were hashed at the start and end; the recorded manifests agree. The phenotype-blind exclusions table contained 101 data rows: 99 analyzed cases plus two bookkeeping exclusions [cite: determinism_manifest_end.json | row_counts.exclusions.csv=101,row_counts.per_case_contributions.csv=99 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
3. **CONSORT-style flow.** Of 101 exclusions-table records entering the provenance gate, two were not analyzed: `sub-stroke0142` was an `excluded_archive_lesion` bookkeeping row and `sub-stroke0043` was an `excluded_case` for `source_corrupt_member`; 99 unique analyzed IDs remained and matched the contribution-table IDs exactly [cite: provenance_gate.json | analyzed_rows=99,bookkeeping_rows,unique_analyzed_ids=true,id_set_matches_contribution_table=true | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66]. No reserved case and no phenotype row was accessed [cite: summary.json | reserved_cases_accessed=0,phenotype_rows_opened=0 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
4. **Support provenance gate.** All 99 analyzed cases had finite positive integer support counts; support ranged from 1,401 to 617,540 voxels, with no discrepancy recorded [cite: provenance_gate.json | b_finite_positive_integer_count=99,b_min=1401,b_max=617540,discrepancies=[] | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66]. The census cross-checks reproduced the frozen sign counts—54 positive, 6 zero, 39 negative—and both frozen head-share identities [cite: provenance_gate.json | census_cross_checks.sign_counts.positive=54,census_cross_checks.sign_counts.zero=6,census_cross_checks.sign_counts.negative=39,census_cross_checks.checks | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66]. No support-provenance kill condition was approached: the gate reports `pass: true` and an empty discrepancy list [cite: provenance_gate.json | pass=true,discrepancies=[] | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
5. **Authorized support analysis.** The head was the frozen signed ranks 1–10. Its absolute contribution was 0.04367036086720666 of 0.08624524334982282 total, while its support was 2,025,630 of 22,604,450 voxels, yielding shares 0.5063509495830807 and 0.08961200117675944 [cite: support_shares.json | sole_disproportionality_comparison | head_abs_contribution_sum,total_abs_contribution_sum,head_support_voxels,total_support_voxels,head_abs_contribution_share,head_support_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66]. The one authorized variant was reported; no support-clause interval, test, margin, or alternative subgroup was run.
6. **Dictionary-only clinical preparation.** The 12,149-byte dictionary matched its pinned MD5 and 148 cells were inventoried [cite: proposed_variable_freeze.json | dictionary.bytes=12149,dictionary.md5=c8d806a021614c6bb9f732756f9701d4 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: summary.json | dictionary_cells_inventoried=148 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66]. It documented 3-month mRS, 24-hour NIHSS, admission NIHSS, age, and sex, while no center/site field was found; these are proposed bindings, not analyzed clinical variables [cite: proposed_variable_freeze.json | constructs,center.documented=false | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
7. **Terminal.** Phase A ended in the preregistered positive terminal `PHASE_A_COMPLETE_REQUIRES_AMENDMENT` after 0.013 wall-seconds [cite: summary.json | status=PHASE_A_COMPLETE_REQUIRES_AMENDMENT,wall_seconds=0.013 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66]. This is successful completion of Phase A, not completion of the study.

## Layer C — Deep justification

### Claims table

| Classification | Claim | Exact source |
|---|---|---|
| Demonstrates | The frozen top ten account for 0.5063509495830807 of absolute contribution and 0.08961200117675944 of eligible support in the realized 99-case cohort. These are deterministic finite-population arithmetic under the frozen inputs. | [cite: support_shares.json | sole_disproportionality_comparison | head_abs_contribution_share,head_support_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Demonstrates | The support comparison used 99 analyzed cases, with 2 documented bookkeeping exclusions and an exact ID-set join. | [cite: provenance_gate.json | analyzed_rows=99,bookkeeping_rows,id_set_matches_contribution_table=true | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Demonstrates | Every analyzed support count was a finite positive integer; the provenance gate passed with no discrepancy. | [cite: provenance_gate.json | b_finite_positive_integer_count=99,pass=true,discrepancies=[] | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Demonstrates | Phase A did not access phenotype rows or reserved cases. | [cite: summary.json | phenotype_rows_opened=0,reserved_cases_accessed=0 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Demonstrates | The pinned dictionary supports the minimum preregistered schema and documents the proposed named constructs; it does not demonstrate their case-level completeness. | [cite: summary.json | clinical_minimum_set_supported=true | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: proposed_variable_freeze.json | constructs,minimum_set.supported=true | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Suggests | The realized contribution concentration is not simply proportional to eligible-support quantity: the share pair is widely separated, and rho is 0.07085961657390227. “Suggests” is used because the contract supplies no case-level uncertainty or sampling model and the head was selected from this same realized census. | [cite: support_shares.json | sole_disproportionality_comparison | head_abs_contribution_share,head_support_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: support_shares.json | descriptive_displays | spearman_rho_abs_contribution_vs_support | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Positive finding | Phase A reached its preregistered successful terminal, with all identity, provenance, census, support, and dictionary gates satisfied. | [cite: summary.json | status=PHASE_A_COMPLETE_REQUIRES_AMENDMENT | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: provenance_gate.json | pass=true,census_cross_checks.checks | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Negative finding | The descriptive all-case rank association is small (rho 0.07085961657390227), but this is not an inferential null and does not establish independence. | [cite: support_shares.json | descriptive_displays | spearman_rho_abs_contribution_vs_support | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Does not establish | No clinical difference, clinical silence/markedness, treatment association, subtype, causal explanation, model use, individual-patient result, or generalization beyond the 99 cases. | [cite: summary.json | phenotype_rows_opened=0,analyzed_cases=99 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Does not establish | The signed share 0.7928912778985707 is not contribution per unit support; it is net-gap accounting after cancellation. | [cite: support_shares.json | reversal_accounting | signed_head_net_gap_share,label | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Validity failures | None observed. No invalidating failure occurred, and neither preregistered stop (`SUPPORT_PROVENANCE_FAILURE` or clinical-schema unsupported) fired. | [cite: provenance_gate.json | pass=true,discrepancies=[] | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: summary.json | clinical_minimum_set_supported=true,status=PHASE_A_COMPLETE_REQUIRES_AMENDMENT | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |

### Uncertainty location

This was a deterministic table audit and arithmetic decomposition, not stochastic training. The fixed seed was reserved for Phase-B hypothetical relabeling and did not generate the Phase-A share or rank outputs. Uncertainty therefore lies in scope and selection: these are all 99 realized analyzed cases, the head was selected from their outcome-derived contributions, and the contract deliberately provides no sampling model or interval for the support clause. Exact arithmetic supports **DEMONSTRATES** at this finite-population scope; any claim about recurrence, clinical meaning, or a general relationship is unsupported, while the qualitative “not simply proportional” reading remains only **SUGGESTS** because no case-level uncertainty machinery licenses broader effect language.

## Next decision

**ADVANCE — only to the contract amendment and fresh human review for Phase B.** Bind the Phase-A proposed clinical variable freeze and the hashes of `proposed_variable_freeze.json` and `per_case_support.csv`, replace the result interface with the Phase-B interface, register the consumed-artifact edge, and seek fresh human approval before staging any phenotype byte. The amendment review should explicitly decide whether to retain both exploratory clinical uncertainty displays exactly as drafted; it must not revisit the already completed support arithmetic or add variables in response to its result.



===== ideas/047/keystone_screen.md =====
# Keystone screen — idea-047 (isles24-scout-010-c01)

Screened 2026-09-02.

## Keystone as stated on the card

> (1) The frozen per-case contribution table exists in-repo under the
> ratified census; (2) per-case phenotype files carrying the ses-02
> outcome family and ses-01 baseline variables exist inside the held,
> checksum-verified training archive.

## What was inspected

### Part 1 — the frozen contribution table (in-repo, primary artifact)

`probes/046/results/results_v3/per_case_contributions.csv` on main:

- Header (verbatim, line 1): `case_id,d_band2,d_band3,delta,contribution,signed_rank`
- Top data row (verbatim, line 2):
  `sub-stroke0153,-0.11497326203208558,0.5920569329660239,0.7070301949981095,0.007141719141395045,1`
- `wc -l` = 100 lines → 99 data rows, and the 99 `case_id` values are
  unique (`sort -u` count 99).

`probes/046/results/results_v3/census_summary.json` (verbatim excerpts):

- `"10": { ... "signed_head_net_gap_share": 0.7928912778985707 }` under
  `top_k` — the 79.29% top-ten share the question cites.
- `"sign_counts": { "negative": 39, "positive": 54, "zero": 6 }` — the
  39 opposing cases the card cites.

All values match the card's `keystone_evidence` exactly. **Part 1
VERIFIED (verified fact).**

### Part 2 — phenotype members inside the held archive (primary manifest)

`archive_manifest.csv` read from the results branch at
`origin/results/probe-023-349af5ad0b3e:probes/023/results_v2/archive_manifest.csv`
(the manifest of the md5-verified `train.7z`; 2,982 lines):

- Verbatim rows, matching the card byte-for-byte:
  - `train/phenotype/sub-stroke0001/ses-01/sub-stroke0001_ses-01_demographic_baseline.csv,405,184c4588`
  - `train/phenotype/sub-stroke0001/ses-02/sub-stroke0001_ses-02_outcome.csv,98,6f8fa8cd`
- `grep -c 'ses-02_outcome.csv'` = **149**;
  `grep -c 'demographic_baseline.csv'` = **149**.

**Sharper check than the card states** (coverage for the analysis cohort,
not just file existence): joining the 99 census `case_id`s against the
manifest, every one of the 99 has BOTH
`train/phenotype/<id>/ses-02/<id>_ses-02_outcome.csv` and
`train/phenotype/<id>/ses-01/<id>_ses-01_demographic_baseline.csv`
(`comm -23` of the sorted id sets is empty in both directions).
**Part 2 VERIFIED with 99/99 coverage (verified fact).**

### Record-level variable promise (the follow-up the deliverable leans on)

Zenodo record https://zenodo.org/records/16813698 (fetched 2026-09-02),
verbatim from the record description:

> "Clinical data: demographics, patient history, admission NIHSS,
> 3-month functional outcome (mRS), etc."

Files on the record: `clinical_data-description.xlsx` (12.1 kB) and
`train.7z` (99.0 GB); license "Creative Commons Attribution Non
Commercial Share Alike 4.0 International"; Version v3, published
August 12, 2025. All match the card's `verified_dataset_facts`.

## Residual assumption check (wrong-keystone test)

The stated keystone is existence of two file families. The actually
load-bearing assumption for the deliverable sentence is stronger: that
the phenotype files *contain the named variables with usable values for
the 99 cases*. Decomposed:

1. **Variables named at record level** — now VERIFIED (quote above):
   the dataset publisher states admission NIHSS and 3-month mRS are in
   the clinical data.
2. **Per-case files exist for all 99 analyzed cases** — now VERIFIED
   (99/99 join above), which the card's own evidence (149 counts) only
   implied.
3. **Exact column names/coding and per-case missingness** — NOT
   verified, and deliberately so: the card's own D3 read-restriction
   protocol forbids opening case-level phenotype files before the
   frozen spec exists, and the mitigation (freeze the variable list
   from `clinical_data-description.xlsx` first) is the correct order.
   Consistent side evidence without opening anything: `outcome.csv` is
   98 bytes per the manifest — a one-row, few-column table, as
   expected. Residual risk is missing values shrinking the effective
   99; that degrades sensitivity (already scored as a limitation), it
   does not make the study impossible or uninterpretable.

No wrong-keystone error found: the nearest-checkable things beyond the
stated keystone were checked here, and the remaining assumption (3) is
unverifiable by design at this stage, not by neglect.

## Verdict

```json
{"verdict": "PASS", "evidence": "Clinical data: demographics, patient history, admission NIHSS, 3-month functional outcome (mRS), etc.", "source": "https://zenodo.org/records/16813698 (record description); train/phenotype/sub-stroke0001/ses-02/sub-stroke0001_ses-02_outcome.csv,98,6f8fa8cd in origin/results/probe-023-349af5ad0b3e:probes/023/results_v2/archive_manifest.csv", "note": "Both keystone parts verified verbatim; sharper 99/99 phenotype coverage join also passes; only column-level coding remains open, correctly deferred behind the D3 protocol."}
```


===== ideas/047/probe_contract.yaml =====
# Probe contract v2 -- idea 047, keystone-ten clinical profile and
# support-share arithmetic of the census head.
# Draft only. Nothing here authorizes code, staging, execution, or any
# phenotype access. Phase A requires human approval of this exact blob.
# Phase B additionally requires the pre-registered amendment below and a
# fresh human approval of the amended blob; the phenotype rows stay
# unread until then.
#
# v2 supersedes the v1 draft per the feasibility memo's REVISE verdict
# (ideas/047/feasibility.md, sections 1, 6, 8, 9). The decisive finding,
# re-verified against the repository at this drafting (2026-09-02): the
# support variable B_i already exists as a claim-bearing output of the
# ratified take-13 bundle -- probes/023/results/results_v2/exclusions.csv
# carries a populated integer eroded_region_voxels for all 99 analyzed
# cases, written by the frozen implementation's coordinate_arrays()
# (probes/023/run.py lines 486-523 at the pinned blob) as exactly the
# eligible region after Tmax>6.0 thresholding, six-neighbor one-voxel
# erosion, border and two-voxel array-midline exclusion, per-patient
# CBV-p98 vessel exclusion, and finiteness/positivity filtering.
# Consequences implemented here: no map staging, no NCCT, no region
# recomputation, no 297-row reproducibility gate; Phase A becomes a
# hash-and-join audit of three pinned in-repo tables plus the frozen
# code blob, and Phase B alone stages the 198 phenotype members. The
# retired per_patient.csv pin is dropped with the gate that consumed it
# (its d column is therefore untouchable by construction).
#
# Right-sizing (2026-09-01 operator ruling): one contract with two
# pre-registered ordered phases, not serial contracts. Phase B is
# deterministic on Phase A's outputs once the amendment freezes the
# clinical variable list, and blindness is preserved by ordering -- now
# strictly stronger than v1: no phenotype byte is even staged to disk
# until the Phase-B approval exists. The genuinely new authority scope
# -- first-ever read of the released clinical outcome rows -- sits
# behind the amendment plus fresh approval (023 Phase S -> Phase C
# precedent).

idea_id: "idea-047"
contract_version: 2
track: exploratory

authorities:
  charter: "charters/isles24/CHARTER.md"
  collaborator_rules: "docs/COLLABORATOR_RULES.md"
  scoring_rubric: "docs/SCORING_RUBRIC.md"
  idea_card: "ideas/047/idea_card.json"
  critique: "ideas/047/critique.md (defects D1-D6)"
  debate: "ideas/047/debate.md and ideas/047/consensus.md (round-3 frozen design)"
  revision: "ideas/047/revision.md"
  operator_ruling: "ideas/047/unblock_ack.txt (q1+q4 proxy rejected; exact eroded Tmax>6s support under the ratified take-13 parameters adopted; round-3 finite-population design). See open question 1: this v2 satisfies the ruling's quantity via the ratified cached output rather than literal re-execution."
  feasibility: "ideas/047/feasibility.md (REVISE; section 9 directives 1-6 implemented by this v2; nearest dataset-specific neighbor EJR 2026, DOI 10.1016/j.ejrad.2026.113200)"
  d3_d4_protocols: "ideas/046/interpretation.md (ratified D3 read-restriction and D4 joint-display rules)"
  take13_contract: "ideas/023/probe_contract.yaml at git blob 03d4545fe293f0067c69ce9e9e696ec97b894d7b (the ratified take-13 parameters)"
  take13_implementation: "probes/023/run.py at git blob 0e9a40b453b6d4b653841d6ea70f2e4b75cce9be (frozen region machinery; byte-verified only, never executed under this contract)"
  decision_entries:
    - "2026-09-02 - Operator note to the next scout cycle: the CLINICAL successor specifically"
    - "2026-09-01/02 - Registry closeout: 045 gov-0002, 046 gov-0001; supersede semantics; right-sizing guidance"
    - "2026-08-28 - Meeting outcome: dual-track sprint (pre-registered clinical-scores secondary)"
    - "2026-08-26 - 023 take 11: SOURCE data defect proven (sub-stroke0043 exclusion policy)"
    - "2026-08-25 - 023 attempts 3-4 (a pin that can re-resolve at runtime is not a pin)"

question: "In the frozen 99-case idea-046 census cohort, do the ten largest signed contributors to the band-2/3 reversal differ in aggregate on a pre-frozen released clinical variable list from the other 89 cases -- and how does their exact share of total absolute contribution compare with their exact share of total eligible deficit support B_i, the per-case eroded Tmax>6s eligible-region voxel count produced under the ratified take-13 parameters?"

risky_assumption_tested: "The riskiest assumption is that the cached take-13 support extract is valid and joinable: exclusions.csv at its pinned SHA-256, filtered to record_type == analyzed_case, must yield exactly 99 unique case ids set-equal to the frozen contribution table's ids, each with a finite positive integer eroded_region_voxels, with the only non-analyzed rows the two documented bookkeeping rows (sub-stroke0142 excluded_archive_lesion; sub-stroke0043 excluded_case); and probes/023/run.py must byte-match frozen blob 0e9a40b453b6d4b653841d6ea70f2e4b75cce9be, whose coordinate_arrays() writes eroded_region_voxels as the eligible-region voxel count. All of this was verified by hand at drafting (2026-09-02: hashes reproduce; join exact 99/99; B_i range 1401-617540, all positive integers; code lines 486-523 quoted in feasibility.md); the probe re-verifies it mechanically before any science is emitted. Secondary risky assumption, tested at the dictionary step before any case-level read: clinical_data-description.xlsx identifies a minimum usable variable set (at least one of 3-month mRS / NIHSS at any documented time point, and at least one of age / sex)."

phases:
  phase_a: "Phenotype-blind, table-and-dictionary-only; no archive access, no map member, no image byte. Ordered steps: (1) input-identity gates (all frozen-input SHA-256s; take-13 implementation byte-verification); (2) the support provenance-and-join gate; (3) census cross-checks; (4) support-clause outputs; (5) dictionary staging and inventory with a machine-derived proposed variable freeze. Terminal status PHASE_A_COMPLETE_REQUIRES_AMENDMENT (or PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED under the pre-registered branch below)."
  amendment: "Mechanical contract amendment: binds the frozen clinical variable list from the Phase-A dictionary inventory, swaps required_outputs to the Phase-B interface, and records the Phase-A bundle identity as a consumed artifact. The amendment stales the Phase-A approval by construction; fresh human approval of the amended blob authorizes Phase B."
  phase_b: "One selective-extraction staging event of exactly the 198 phenotype members from the held archive under D3, then opens exactly the 99 analyzed cases' phenotype rows and emits the single aggregate clinical estimation table under D4. Terminal status STUDY_COMPLETE."

scope:
  included: "One deterministic CPU-only pipeline over the 99 analyzed census cases: Phase A hash-and-join audit of three pinned in-repo tables plus the frozen implementation blob; the frozen finite-population support-clause displays; dictionary-only schema inventory; and, after amendment and fresh approval, Phase B staging of exactly 198 phenotype members and one aggregate 10-versus-89 clinical estimation table with exploratory-labeled uncertainty, joint support display, and small-cell suppression."
  excluded:
    - "Any archive member other than the 198 Phase-B phenotype files: no perfusion map, no NCCT, no lesion-mask member is staged or read in either phase. No take-13 region code is executed under this contract."
    - "The 49 reserved cases, sub-stroke0043, any non-census case, band-1 outcome values, raw 4D CTP."
    - "Any permutation test, interval, threshold, or is/is-not adjudication anywhere in the support clause; any random-subset null anywhere (round-2 debate concession)."
    - "Any fitted residual, analyst-defined subgroup, regression of contribution on support, or 'keystone' verdict (critique D2)."
    - "Any per-case clinical value in any output; any cross-tabulation of two or more clinical variables; any significance-selected headline; any multivariable model (critique D5/D6)."
    - "Any model inference, model-use claim, causal or clinical-subtype claim, or generalization beyond the realized 99 cases."
    - "Any variant support definition, any recomputation of the support variable, or reinterpretation of a gate failure as a scientific result."

dataset:
  name: "ISLES'24 training release (held archive, Phase B only) plus imported program tables"
  archive:
    zenodo_record: "16813698 (immutable child record; staging must declare it; silent re-resolution to any other record is invalidating)"
    file: "train.7z, 99014629647 bytes, md5 36ae28b9a17f7340b8bbef62b595cb57 (verified held copy; evidence/decisions.md 2026-08-25/26)"
    member_manifest: "archive_manifest.csv at results branch origin/results/probe-023-349af5ad0b3e:probes/023/results_v2/archive_manifest.csv, git blob edb9a8c2ceb90df214cdd7ec167f0b1e8c858bb2 (member sizes and CRC32s)"
    dictionary: "clinical_data-description.xlsx, 12149 bytes, md5 c8d806a021614c6bb9f732756f9701d4 (pinned at drafting from the record's files listing, verified 2026-09-02 in feasibility.md; a fetch not matching this md5 is invalidating -- the pin never re-resolves at runtime)"
  frozen_inputs:
    # probes/023/results/results_v2/exclusions.csv -- 102 lines: header,
    # 99 analyzed_case rows (case_id, ..., eroded_region_voxels = B_i),
    # and exactly two non-analyzed bookkeeping rows (sub-stroke0142
    # excluded_archive_lesion; sub-stroke0043 excluded_case). Ratified
    # take-13 output (023 gov ratification; each node COMPLETE under its
    # own immutable contract).
    exclusions.csv: "58e9f8ab7cea38e6717319a26ea6a590dc7d1ad0d42d6b30dca648b0509a5a71"
    # probes/046/results/results_v3/per_case_contributions.csv -- 99 data
    # rows, columns case_id,d_band2,d_band3,delta,contribution,signed_rank.
    per_case_contributions.csv: "aba525122f796618761e6c4d29b664647760e8dff4987932c3ff6ab5456faae9"
    # probes/046/results/results_v3/census_summary.json -- cross-check
    # values only.
    census_summary.json: "189c0ce846cffd2eff76e896bfa35156893568d5ee64868caae0b8609bd4c761"
    # per_patient.csv is deliberately NOT an input of this contract: the
    # v1 reproducibility gate that consumed it is retired with the
    # recomputation path (feasibility section 9 item 1), and no other
    # computation may touch it.
  extraction_set: "Phase B only. Exactly 198 members, enumerated per analyzed case id from the 99 rows of per_case_contributions.csv: train/phenotype/<id>/ses-01/<id>_ses-01_demographic_baseline.csv and train/phenotype/<id>/ses-02/<id>_ses-02_outcome.csv. Member discovery tolerates the sub-stroke/sub-strokecase spellings per the 2026-08-25 payload-outranks-prose lesson. Phase A stages nothing from the archive; the dictionary is fetched from the immutable record (or a held copy) against its pinned md5."

split_policy: "The 99 analyzed take-13 census cases only, as enumerated in the frozen contribution table. This is exploratory reuse of the already-open idea-023 imaging outcomes plus a first, phase-gated read of the released clinical rows for the same 99 cases; it is not a fresh confirmatory split. The 49 reserved cases and the excluded sub-stroke0043 must remain untouched and absent from every staged member, output, and receipt (sub-stroke0043's bookkeeping row in exclusions.csv is read only to confirm its record_type and exclusion)."

preprocessing:
  step_1_identity_gates: "Hash all three frozen inputs against their pins. Byte-verify probes/023/run.py in the working tree against git blob 0e9a40b453b6d4b653841d6ea70f2e4b75cce9be and record in resolved_config.json the verbatim coordinate_arrays() lines defining eroded_region_voxels (the code is evidence, never executed). Any mismatch is an invalidating input-identity failure."
  step_2_support_gate: "The provenance-and-join gate, emitted to provenance_gate.json: (a) filter exclusions.csv to record_type == analyzed_case; require exactly 99 rows with unique case ids; (b) require exact set equality with the 99 case ids of the frozen contribution table; (c) require every eroded_region_voxels value to parse as a finite positive integer; (d) require the non-analyzed remainder to be exactly the two documented bookkeeping rows (sub-stroke0142 excluded_archive_lesion with blank support fields; sub-stroke0043 excluded_case source_corrupt_member). On any failure: write provenance_gate.json with the discrepancy, write no support-clause output, and stop with status SUPPORT_PROVENANCE_FAILURE for escalation. No substitute support source may be consulted."
  step_3_census_cross_checks: "Recompute from the frozen contribution table and match against census_summary.json before emission: head absolute-mass share 0.5063509495830807; signed head share 0.7928912778985707; sign counts 54 positive / 6 zero / 39 negative; signed and absolute top-ten set coincidence. Any mismatch is invalidating transcription failure, never a result."
  step_4_support_clause: "Only after gates pass. B_i := the analyzed-case eroded_region_voxels value, verbatim. All quantities are exact finite-population arithmetic over the realized 99 cases, in IEEE-754 doubles, with no uncertainty machinery of any kind."
  step_5_dictionary: "Fetch clinical_data-description.xlsx and verify its pinned md5. Emit dictionary_inventory.csv (every documented sheet, field, description, time point, coding, missing-value convention, verbatim) and proposed_variable_freeze.json via the frozen targeting rule below. Both artifacts are written and hashed into the run log; no case-level file exists on disk in this phase, so the proposal cannot be influenced by any clinical byte. Pre-registered branch: if no field maps to (3-month mRS OR any documented NIHSS time point) or none to (age OR sex), record CLINICAL_SCHEMA_UNSUPPORTED; Phase A still completes its support clause and terminates PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED; no amendment path exists and successor handling is an operator decision."
  targeting_rule: "Feasibility verified the dictionary documents Age, Sex, NIHSS at admission, NIHSS 24h, NIHSS discharge, MRS 3 months, and mTici postinterventional. Target constructs, in the lineage-reconciled priority the memo directed (item 3; critique D1): 3-month mRS; 24-hour NIHSS as the lineage-preserving field of idea-046's frozen optional rung; admission NIHSS as documented baseline-severity context (never presented as interchangeable with the 24-hour field); age; sex. At most two additional contextual fields may be proposed only if the dictionary shows them (e.g. mTici postinterventional, onset-to-imaging time). Center: if the schema documents a center/site identifier it is a mandatory contextual variable outside that cap (feasibility item 5); if not, its absence is recorded in the reconciliation field of proposed_variable_freeze.json. The inventory binds exact release spellings; the amendment binds the final list."

analysis:
  analysis_unit: "One analyzed census case (Phase A); the frozen 10-versus-89 strata (Phase B)."
  support_clause:
    head_definition: "The frozen signed-rank top ten, signed_rank 1-10 in the frozen contribution table. Membership is never recomputed or reselected."
    sole_disproportionality_comparison: "sum_head |c_i| / sum_all |c_i| displayed beside sum_head B_i / sum_all B_i. These are the only two numbers the proportionality clause may cite (round-3 freeze, verbatim)."
    descriptive_displays: "Casewise rank(|c_i|) - rank(B_i) distribution with the head's ten values marked (ranks 1..99, 1 = largest, ties broken by case_id ascending), and Spearman rho between |c_i| and B_i as a bare descriptive number. No interval, test, or threshold accompanies either."
    reversal_accounting: "The signed head share (expected 0.7928912778985707) is reported only under an explicit reversal-accounting label stating it measures share of the net band-2/3 gap after cancellation across 39 opposing cases. Neither it nor its difference from the support share may be interpreted as contribution per unit support (round-3 freeze)."
  clinical_clause:
    # The sentinel below is the only placeholder in this contract. The
    # amendment replaces it with the bound list; rule lines refer to it
    # by field name, never by its literal value (2026-08-15 placeholder
    # lesson).
    frozen_variable_list: "<<TO_BE_FROZEN_AT_AMENDMENT>>"
    variable_freeze: "The analyzed variable list is bound at the amendment from the Phase-A dictionary inventory, replacing the frozen_variable_list sentinel: for each variable, exact field name, time point, type, coding, missingness rule, and contrast statistic from the closed menu below -- one decision, bound in the amendment, before any case row is read. Amendment deviations from proposed_variable_freeze.json require a recorded dictionary-grounded reason; additions motivated by any Phase-A scientific output are prohibited and invalidating."
    closed_statistic_menu: "Continuous: group mean/SD and median/IQR; contrast = standardized mean difference (pooled SD) and difference in medians. Ordinal: per-level group counts and cumulative distribution; contrast = difference in medians and rank-biserial. Binary: group counts/proportions; contrast = difference in proportions. No other statistic is available to the amendment."
    uncertainty: "Two frozen displays per contrast, both exploratory-labeled, resolving feasibility item 4: (1) deterministic leave-one-head-case-out sensitivity -- the contrast recomputed ten times, each omitting one head case, reported as the min/max range; (2) a hypothetical exchangeability reference range -- the central 95% of the contrast under 10000 random relabelings of the 10/89 split, frozen seed 20260902 -- carried under the explicit label 'hypothetical exchangeability reference; not a confidence interval; not sampling inference' (neither group assignment nor the 99 cases were randomized). No p-value is selected, ranked, or headlined; all frozen variables are reported jointly (critique D4/D6)."
    joint_display: "Per D4, every variable row carries the head and rest group B_i medians and the two Phase-A support shares. Missingness (non-missing n per group) is reported per variable; a head-group non-missing count below 7 is flagged as insufficient head coverage and still reported. If a center variable is bound, its display is group counts per center under the suppression rule -- descriptive context only, never a corrected estimate."
    suppression: "Aggregate-only outputs: no per-case clinical value anywhere; no cross-tabulation of two or more clinical variables; any categorical or ordinal level containing 1 or 2 head cases is reported as '<3' (zero may be reported as 0)."
  interpretation_rule: "The support clause reports the two exact shares and judges nothing: 'disproportionate' may be used only as an arithmetic comparison of the two shares, scoped to the realized 99 cases. The clinical clause reports estimates with exploratory uncertainty and missingness; absence of large separation is stated only as 'no separation larger than the displayed exploratory ranges was observed at the achieved precision', never as clinical silence. No status, share value, or table content upgrades any claim beyond claim_discipline."

primary_metric: "The exact share pair -- the frozen top ten's share of total absolute contribution beside their share of total eligible deficit support -- for the realized 99 cases, plus the single pre-frozen aggregate 10-versus-89 clinical estimation table."
secondary_metrics:
  - "Per-case B_i extract with the provenance-and-join gate record."
  - "Casewise rank-discrepancy distribution with head marks; descriptive Spearman rho."
  - "Separately labeled signed reversal-accounting share."
  - "Dictionary inventory, NIHSS time-point reconciliation record (both admission and 24-hour fields are documented; the 24-hour field preserves the idea-046 lineage), and the proposed variable freeze."
baselines:
  - "Ratified census values (frozen cross-checks, not comparators): head absolute-mass share 0.5063509495830807; signed head share 0.7928912778985707; sign counts 54/6/39."
  - "Drafting-time support fingerprint (lineage evidence only, not a runtime gate): analyzed-case B_i spans 1401 to 617540 voxels across the 99 cases."

maximum_variants: 1
maximum_gpu_minutes: 0
maximum_seeds: 1
randomness: "Phase A is fully deterministic; the seed allowance is unused there. Phase B uses exactly one frozen seed, 20260902, solely for the hypothetical exchangeability reference relabelings. No scientific point estimate depends on randomness."
stopping_rule: "Stop immediately on any invalidating failure or pre-registered stop. Phase A stops after its required outputs are written (total CPU wall time capped at 10 minutes; no staging transport exists in this phase beyond the 12 kB dictionary fetch). Phase B stops after the single estimation table is written (post-staging CPU wall time capped at 15 minutes; staging transport uncapped but receipted in staging_audit.json). A wall-time stop is incomplete and invalid, not a negative. No additional variant, follow-up analysis, or opportunistic secondary read is authorized."

positive_pattern: "PHASE_A_COMPLETE_REQUIRES_AMENDMENT: all identity, provenance, cross-check, and output requirements pass and the phenotype-blind support clause is emitted -- a successful descriptive result regardless of the share values, carrying no proportionality verdict. STUDY_COMPLETE (Phase B, post-amendment): the frozen clinical estimation table is emitted -- successful regardless of what it shows, carrying no separation verdict."
negative_pattern: "NO DIRECTIONAL NEGATIVE IS DEFINED. Pre-registered stops are decision-grade stops, not negatives and not invalidating: SUPPORT_PROVENANCE_FAILURE (the cached support extract fails the join/definition gate; the gate record is the deliverable and escalation is the next act) and PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED (dictionary cannot support the minimum variable set; support clause still delivered; clinical clause requires operator decision). A small clinical separation at achieved precision is a bounded exploratory description, never evidence of clinical silence."

invalidating_failures:
  - "Authority failure: any execution without fresh human approval binding the exact governing contract blob; any Phase-B activity before the amendment and its fresh approval; any Phase-B activity while the frozen_variable_list field still holds its pre-amendment sentinel value."
  - "Input-identity failure: any frozen-input SHA-256 mismatch; probes/023/run.py not byte-identical to its pinned blob; archive md5 mismatch; staging resolves to any Zenodo record other than 16813698; dictionary md5 mismatch against the pinned value."
  - "Scope failure: any archive member outside the 198-member Phase-B extraction set staged or extracted; any perfusion-map, NCCT, or lesion-mask member staged or read in either phase; any take-13 region code executed; any reserved or excluded case's phenotype member touched."
  - "Blindness failure: any phenotype byte staged or read before Phase-B authorization; probes/023/results/results_v2/per_patient.csv consumed by any computation."
  - "Staging-integrity failure (Phase B): extraction return code nonzero; any staged member failing the manifest size/CRC comparison; a staged-member count other than 198."
  - "Cross-check failure: any recomputed census cross-check value disagreeing with census_summary.json."
  - "Analysis deviation: any threshold, interval, or permutation machinery in the support clause; any statistic outside the closed menu; any variable not in the amended frozen list; any deviation from the frozen seed or relabeling count; any significance-selected emphasis."
  - "Selective-output failure: any of the 99 cases, any frozen display row, or any frozen variable omitted, suppressed beyond the frozen suppression rule, or filtered."
  - "Lineage failure: any imported bundle (probes/023 or probes/046 results) modified or overwritten."
  - "Output/provenance failure: any required artifact, hash, receipt, environment record, or run log missing."

claim_discipline:
  permitted:
    - "The frozen top ten carry X% of total absolute contribution against Y% of total eligible deficit support in these 99 cases (exact arithmetic, realized cohort only)."
    - "Aggregate estimation statements about the frozen variable list with exploratory-labeled uncertainty and stated missingness."
    - "No separation larger than the displayed exploratory ranges was observed at the achieved precision (bounded null)."
    - "'Disproportionate' strictly as the arithmetic comparison of the two exact shares, scoped to the realized 99 cases."
  prohibited:
    - "Any keystone verdict, clinical-subtype claim, explanation of dominance, or clinically-silent/clinically-marked language."
    - "Interpreting the signed reversal-accounting share, or its difference from the support share, as contribution per unit support."
    - "Any per-patient claim, any model-use or causal claim, any generalization beyond the realized 99 cases, this frozen estimator, and these frozen inputs."
    - "Upgrading exploratory ranges or any p-like quantity into inferential support, or letting clinical uncertainty displays imply an inferential license the support clause refused."
    - "Upgrading the hedged novelty language of the card; the 2026 EJR ISLES'24 clinical secondary analysis (DOI 10.1016/j.ejrad.2026.113200) is the named nearest dataset-specific neighbor, and the Tomography 2026 near-miss remains unread."

# Phase-A result interface (governing while this pre-amendment blob is
# current). The amendment replaces this list with phase_b_required_outputs.
required_outputs:
  - resolved_config.json
  - input_manifest.csv
  - provenance_gate.json
  - per_case_support.csv
  - support_shares.json
  - rank_discrepancy.csv
  - dictionary_inventory.csv
  - proposed_variable_freeze.json
  - summary.json
  - environment.txt
  - run_log.txt

amendment_protocol:
  trigger: "PHASE_A_COMPLETE_REQUIRES_AMENDMENT bundle validated and imported."
  binds:
    - "The frozen clinical variable list (exact field names, time points, coding, missingness rules, per-variable contrast statistics from the closed menu, contextual fields per the targeting rule), replacing the frozen_variable_list sentinel; the NIHSS time-point reconciliation is documented in the bound list (critique D1; feasibility item 3)."
    - "The Phase-A bundle identity and the SHA-256 of proposed_variable_freeze.json and per_case_support.csv as consumed artifacts (registry artifact edge)."
    - "required_outputs replaced by phase_b_required_outputs (F3 lesson: no single list may conflate two phases' interfaces; each bundle validates under its own governing blob)."
  approval: "The amendment stales the Phase-A approval by construction. Fresh human approval of the amended blob is the sole authorization for Phase B, for the staging of any phenotype member, and for the first read of any phenotype row."

phase_b_required_outputs:
  - resolved_config.json
  - input_manifest.csv
  - staging_audit.json
  - clinical_estimation_table.csv
  - clinical_uncertainty.json
  - suppression_log.csv
  - summary.json
  - environment.txt
  - run_log.txt

open_questions_for_human:
  - "Support path: the unblock ruling froze 'the exact-map recomputation branch'. Feasibility then verified (and this drafting re-verified against the repository) that the identical quantity -- exact eroded Tmax>6s eligible support under the ratified take-13 parameters -- already exists as a hash-pinned, code-verified output of the ratified take-13 bundle. This v2 adopts that cached extract and retires the recomputation, the 3 GB map staging, and the 297-row reproducibility gate (feasibility section 9 item 1: provenance replaces reproduction; same bytes, fewer failure surfaces). Approving this blob ratifies the substitution and supersedes the card's X_measurement recomputation/reproducibility-gate wording; if you want literal re-execution anyway, reject and direct reversion to the v1 Phase-A steps."
  - "Uncertainty currency (feasibility item 4): this contract freezes TWO clinical displays -- deterministic leave-one-head-case-out ranges, plus a relabeling range explicitly labeled 'hypothetical exchangeability reference, not a confidence interval'. If you prefer only deterministic displays, strike the relabeling range before approval; the leave-one-out display stands either way."
  - "Structure (carried from v1, never yet ruled): does the amendment-plus-fresh-approval gate satisfy the right-sizing carve-out for the new phenotype exposure, or do you want Phase B as a separately registered contract? Approving this v2 blob adopts the one-contract two-phase design; Phase B remains unreachable without the later amendment approval either way."

human_approved: false


===== ideas/047/probe_review.md =====
# Probe code review — idea 047, contract v2, Phase A, revision round 2

## Verdict

**APPROVE.** The revision closes all three prior blockers without changing the
scientific scope. Phase A implements the approved support-share arithmetic on
the frozen 99-case cohort, preserves the phenotype boundary, writes the
contract-required interface, and labels every terminal result within the
contract's descriptive claim ceiling. No `ideas/047/contract_requirements.md`
exists, so the requirements-governed tier/head/manifest checks do not apply.

## Blocking findings

None.

## Resolution of the prior blocking findings

- **Hard standard 4 — resolved.** A real run now requires a pre-staged
  `--dictionary-file` and refuses when it is absent
  (`probes/047/run.py:205-211`, `probes/047/run.py:1073-1080`). The held file is
  checked against the frozen byte-count and MD5 pins before parsing
  (`probes/047/run.py:710-735`). The remaining Zenodo URL is provenance text,
  not an executed fetch (`probes/047/run.py:102-105`); no network-capable
  import or call remains. The operator command documents the required offline
  input (`probes/047/README.md:11-24`).
- **Hard standard 5 — resolved.** Before the outcome-derived contribution
  table or census summary is opened, the code pin-verifies and reads only the
  phenotype-blind exclusions table, writes the actual analyzed case IDs plus
  the two bookkeeping exclusions to `split_manifest.csv`, and hashes that
  manifest (`probes/047/run.py:294-333`, `probes/047/run.py:1090-1110`). After
  contribution access, the support gate requires exact equality between its
  IDs and the frozen split IDs and records the split hash in the gate artifact
  (`probes/047/run.py:456-483`, `probes/047/run.py:515-522`). A count-preserving
  case substitution therefore fails visibly.
- **Hard standard 1 — resolved.** Both determinism manifests cover the three
  frozen tables, frozen take-13 source, pre-staged dictionary, seed, mode, and
  parsed row counts (`probes/047/run.py:1089-1127`). The common finalizer
  re-hashes those inputs, requires exact start/end equality, writes the end
  manifest, and runs on both normal completion and the registered
  `SUPPORT_PROVENANCE_FAILURE` path (`probes/047/run.py:1024-1039`,
  `probes/047/run.py:1144-1159`, `probes/047/run.py:1286-1289`).

## Contract fidelity and silent-failure review

- The analysis uses exactly the frozen signed-rank top ten and 99-case input,
  computes the sole authorized comparison—absolute-contribution share beside
  eligible-support share—and keeps the signed share in a separately labeled
  reversal-accounting field (`probes/047/run.py:614-699`,
  `probes/047/run.py:1178-1205`). No support-clause hypothesis test, interval,
  residual subgroup, or model analysis is present.
- Input pins, exact row/ID/rank structure, finite values, bookkeeping rows,
  census identities, and output arithmetic fail closed
  (`probes/047/run.py:343-385`, `probes/047/run.py:399-532`,
  `probes/047/run.py:543-699`). The provenance-stop path writes no scientific
  support output and calls itself a decision-grade stop, not a negative
  (`probes/047/run.py:1144-1159`).
- The normal path writes every Phase-A `required_outputs` artifact named by
  the contract (`probes/047/run.py:1186-1221`, `probes/047/run.py:1240-1309`).
  `per_case_support.csv` is the contract's concrete per-case output; the
  generic stage-task reference to `per_sample.csv` does not override the
  approved interface.
- Limits are explicit and respected: one variant, zero GPU minutes, one
  declared seed, and a 600-second Phase-A wall cap
  (`probes/047/run.py:65-72`, `probes/047/run.py:1178-1181`,
  `probes/047/run.py:1236-1244`). Phase B is unreachable because this code
  requires the pre-amendment sentinel and current approval binding
  (`probes/047/run.py:264-285`).

## Hard standards and practical verification

- **Standard 2:** `probe_exclusions.csv` records both non-analyzed cases with
  record type and reason (`probes/047/run.py:1136-1142`).
- **Standard 3:** transforms carry explicit checks or assertions for table
  identity, contribution algebra, ranks, shares, dictionary staging/parsing,
  and smoke construction (`probes/047/run.py:399-699`,
  `probes/047/run.py:710-856`, `probes/047/run.py:859-1010`).
- **Standard 6:** `python3 probes/047/run.py --smoke --output-dir <new-dir>`
  completed with exit 0 in under one second in this review. It emitted
  `SMOKE_ONLY`, start/end manifests compared equal, and the dictionary was
  present in both manifests. Smoke uses 12 synthetic cases and a three-case
  head, skips approval, and cannot emit a contractual Phase-A terminal
  (`probes/047/run.py:859-930`, `probes/047/run.py:1065-1072`,
  `probes/047/run.py:1224-1234`).
- `python3 -m py_compile probes/047/run.py` passed. Requirements are standard
  library only, paths are explicit, output is controlled by `--output-dir`,
  and there are no prompts or GPU dependencies (`probes/047/requirements.txt`,
  `probes/047/run.py:199-212`).

## Non-blocking findings

- Several transform invariants use Python `assert` and would disappear under
  `python -O` (`probes/047/run.py:406`, `probes/047/run.py:451-452`,
  `probes/047/run.py:616-665`, `probes/047/run.py:1214-1216`). The documented
  command does not enable optimization, and surrounding pin/shape/cross-check
  gates cover the claim-bearing structure, so this does not block this bounded
  probe. Explicit fail-closed checks would nevertheless be preferable in a
  future neutral hardening pass.
- The registered provenance-stop path intentionally emits a reduced interface
  rather than all normal Phase-A outputs. This matches the contract's statement
  that the gate record is the stop deliverable and does not masquerade as a
  completed Phase-A bundle.

```json
{"verdict": "APPROVE", "blocking": [], "note": "All prior blockers are closed; smoke and compilation pass, and Phase A is contract-faithful, offline, split-bound before outcome access, and determinism-complete on every registered terminal path."}
```


===== ideas/047/revision.md =====
# Revision — idea 047 (post-critique, post-debate, post-ruling)

Revised 2026-09-02 in response to `critique.md` (six decisive defects
D1–D6), the three-round debate (`debate.md`, `consensus.md`, verdict
REVISE), and the operator ruling recorded in
`ideas/047/unblock_ack.txt`, which resolved the debate's single open
code question:

> ruling: S_i in the frozen take-13 table is per-band quartile-cell
> voxel counts (q1_voxels plus q4_voxels), not total eligible support;
> freeze the exact-map recomputation branch: eroded Tmax>6s deficit
> voxel count per case from the held maps under the ratified take-13
> parameters. Adopt the round-3 finite-population design.

The revision narrows the card to one clean compound question (the same
two clauses the debate ruled identity-preserving), removes every piece
of architecture the gauntlet invalidated, and preserves a meaningful
negative outcome in both clauses.

## Material changes

### 1. The support variable: exact-map branch frozen (operator ruling; debate round 1)

- The round-1 `S_i` proxy (sum of q1+q4 quartile-cell counts) is
  **removed entirely** — not demoted to sensitivity display. The ruling
  establishes it is not total eligible support, so retaining it would
  reintroduce a discredited measure.
- The frozen burden variable is now `B_i` = exact eligible deficit
  support: the voxel count of the take-13 eligible analysis region
  (eroded Tmax>6s deficit under the ratified take-13 parameters,
  including the frozen midline-band, per-patient p98 vessel-exclusion,
  and finiteness rules), recomputed label-blind from the held maps.
- **New reproducibility gate** (answers critique D3's "reproducibility
  comparison against cached case counts"): before any `B_i` is used,
  the re-run region machinery must reproduce all 297 cached per-band
  `q1_voxels`/`q4_voxels` values in
  `probes/023/results/results_v2/per_patient.csv` exactly. A mismatch
  stops the support clause for escalation; no variant region may be
  silently substituted.

### 2. Burden-disproportionality currency (debate rounds 2–3)

- The random-10-subset permutation null and permutation intervals are
  **removed** (round-2 concession: the head is outcome-selected and
  nonexchangeable; the statistic partly rewards its own selection
  rule). No permutation machinery exists anywhere in the support
  clause.
- The **sole** disproportionality comparison is
  `sum_head |c_i| / sum_all |c_i|` beside
  `sum_head B_i / sum_all B_i` (round-3 freeze, adopted verbatim).
- The 79.29% net signed share is **demoted to separately labeled
  reversal accounting** with a frozen prohibition: neither it nor its
  difference from the support share may be read as contribution per
  unit support or as evidence of keystone-like dominance.
- The casewise `rank(|c_i|) − rank(B_i)` distribution (head's ten
  marked) and Spearman rho remain as descriptive displays only.
- The whole clause is finite-population arithmetic about the realized
  99 cases: no sampling story, no generalization, no is/is-not
  threshold language.

### 3. Residual subgroup and keystone endpoint removed (critique D2)

- "Residual of |c_i| on burden" and the "disproportionality
  top-decile" group are **deleted**. No fitted quantity, no
  analyst-defined subgroup, no leverage/functional-form discretion
  survives anywhere in the design.
- The borrowed ecological construct is demoted from endpoint to
  motivation; "keystone" is never a verdict, and "disproportionate" is
  licensed only as a comparison of the two exact shares.

### 4. Clinical clause: dictionary-first freeze and forward correction (critique D1, D5, D6)

- **D1:** the card no longer treats admission NIHSS as interchangeable
  with the lineage's frozen "NIHSS at 24 hours." The dictionary-only
  read of `clinical_data-description.xlsx` freezes exact field names,
  time points, coding, and missingness rules; if the release lacks a
  24-hour field, admission NIHSS enters as a documented forward
  correction, not as execution of idea-046's frozen list.
- **D5/D6:** the conditional "treatment fields if present" discretion
  is removed. At most three contextual fields may be predeclared at
  the dictionary step — one decision, made once, before any case row.
  Per-variable contrast statistics are also frozen at that step.
- The primary clinical deliverable is an **estimation table**: group
  distributions, standardized contrasts with exploratory-labeled
  uncertainty (descriptive calibration for the realized cohort, never
  sampling inference), and missingness; every row reported jointly; no
  significance-selected headline; small cells suppressed. The binary
  "does / does not differ" packaging is gone.

### 5. "Clinically silent" dichotomy removed throughout (critique D4 + plain-pitch defect)

- Title, question, deliverable sentence, audience_relevance,
  negative-result rationale, and plain pitch no longer contain
  "clinically silent," "clinically marked," or the exhaustive
  clinical-versus-imaging-geometry alternatives. The clinical null is
  reframed as bounded: the table reports how much separation a
  10-versus-89 comparison could have excluded.
- New title: "The keystone ten meet the clinic: aggregate clinical
  profile and support-share arithmetic of the census head."

### 6. Honest cost (critique D3)

- The "~50 kB, under five minutes" envelope is replaced: one
  selective-extraction staging event against the held md5-verified
  ~99 GB archive (the same event D3 phenotype staging requires),
  ~3 GB of maps (396 files), a CPU-only 99-case region pass, then
  minutes of table arithmetic. First result in days, not minutes.
  Feasibility and prior-legwork scores lowered accordingly.

### 7. New verification performed at this revision

- **Map coverage for the frozen exact-map branch** (now load-bearing):
  unique-case joins of the md5-verified archive manifest
  (`origin/results/probe-023-349af5ad0b3e:probes/023/results_v2/archive_manifest.csv`)
  against the 99 census ids give **99/99 for each of tmax, cbf, cbv,
  mtt, and the rawdata NCCT**. Verbatim row:
  `train/derivatives/sub-stroke0001/ses-01/perfusion-maps/sub-stroke0001_ses-01_space-ncct_tmax.nii.gz,6580435,bf32937b`.
  The one known source-defective member (sub-stroke0043 ses-01 cbf)
  belongs to a case already excluded from the 99. Keystone
  prerequisite (3) added and marked inspected on this evidence;
  `keystone_status` remains INSPECTED_TRUE.
- **The head's absolute-contribution share already exists in the
  ratified census**: `census_summary.json` `top_k.10.absolute_mass_share`
  = 0.5063509495830807. This is valid for the *signed-rank* head
  because the signed and absolute top-ten sets coincide: the largest
  negative magnitude (0.0029141878799591753) is smaller than the
  tenth-largest positive contribution (0.002976074880714717)
  (sorted-column check on `per_case_contributions.csv`, 2026-09-02).
  Round 3's predicted deflation is therefore already a fact of record:
  the honest share is 50.64%, against the 79.29% signed accounting
  figure. Only the support side of the comparison awaits computation.

### 8. Score changes

| dimension | before | after | why |
|---|---|---|---|
| feasibility | 5 | 4 | honest end-to-end envelope (staging event + map pass), per D3 |
| prior_legwork | 5 | 4 | the support table must be recomputed, not read |
| evaluation_readiness | 2 | 3 | support clause is exact arithmetic needing no custom metric |
| clarity | 4 | 4 | why updated: conditional treatment arm gone; residual openness is only the dictionary step |
| negative_result_value | 3 | 3 | why rewritten: support clause decisive at scope; clinical null bounded, never "silent" |

All other values unchanged; every `why` rewritten to match the revised
design.

## What is lost (stated plainly, from the debate's own accounting)

- The dramatic 79.29% figure can name the head but no longer judge it;
  the honest currency (50.64% absolute share) is known to be less
  striking.
- Any claim that the proportionality pattern or clinical profile would
  recur in new cases: the answer is a fact about the realized 99 and
  nothing more; a generalizing version requires a sampled cohort with
  unopened outcomes and would be a successor candidate.
- The phrase "deficit burden" for the support variable: `B_i` is
  estimator-eligible support (the take-13 analysis region), a subset
  of gross lesion burden, and the writeup must say so.
- The low-cost table-only path: ruled out by the operator's code
  inspection; the study pays for map restaging.
- The residual asymmetry is acknowledged: the clinical clause retains
  exploratory-labeled uncertainty displays (per D6) while the support
  clause has none; the writeup must not let clinical p-values imply an
  inferential license the support clause honestly refused.

## Claim retention

The original deliverable (ledger `deliverable_original`) asked, for the
same frozen 99-case cohort and the same frozen high-contribution
stratum, (i) whether the stratum differs in aggregate on released
clinical variables and (ii) whether its dominance is accounted for by
deficit burden, as an exploratory aggregate-only association-register
description under D3/D4. The revised deliverable answers exactly those
two clauses for exactly that cohort and stratum, with: binary
"does / does not" packaging replaced by estimation displays and exact
finite-population shares; "deficit burden" narrowed to the operational
eligible-deficit-support variable the ruling froze; the conditional
treatment arm replaced by a bounded dictionary-step predeclaration; and
generalization beyond the 99 explicitly renounced. Both debate identity
checks (rounds 2 and 3) found these repairs identity-preserving, the
operator ruling adopted the round-3 design, and per the standing
precedent (ideas 045 and 046 rulings) a card is not re-registered for
becoming more modest. This is a narrowing of the same claim.

```json
{"claim_retention": "narrowed"}
```


===== ideas/047/state.json =====
{
  "approval": {
    "contract_blob": "b4887c05a21bfe870589b5d9982066943df679d5",
    "stale": false
  },
  "charter": "isles24",
  "claim": "In the frozen 99-case idea-046 census cohort, the high-contribution stratum does / does not differ in aggregate on a pre-frozen released clinical variable list (3-month mRS, admission NIHSS, age, sex, plus treatment fields if present in the release) from the remaining cases, and its dominance is / is not accounted for by deficit burden -- an exploratory, aggregate-only, association-register description under the D3 read-restriction and D4 joint-display rules, with no per-patient claims and no model probing.",
  "contract_blob": "b4887c05a21bfe870589b5d9982066943df679d5",
  "corrections": null,
  "idea_id": "idea-047",
  "idea_no": "047",
  "kill_code": null,
  "materialization": {
    "event_count": 6,
    "materializer_version": 3,
    "source_fingerprint_sha256": "6c983cbe03fe990a49d4cdfe440bd29145dd0031a79f96d47c7ea6cabbe976e1",
    "sources": {
      "approval_sha256": "4b3ec937d36ba73a45485a4c51b8fdfbd0434115240a8670f653f4c7524d154c",
      "contract_blob": "b4887c05a21bfe870589b5d9982066943df679d5",
      "idea_card_sha256": "8cbbbb971bf2fe8e8b9d1bc1c5cc6a99100d7b9b31b34660ff14da387081583f",
      "ledger_events_sha256": "48937ffd091d21625813e1f846e7dfd6c8985bb3cad5de8e90226c8ebf038544",
      "registry_sha256": null
    }
  },
  "pending_decisions": null,
  "registry": null,
  "schema_version": 1,
  "scrutiny": "PROBED",
  "status": "ACTIVE",
  "title": "The keystone ten meet the clinic: is estimator dominance clinically marked or clinically silent?"
}


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

## Right-sizing (2026-09-01 operator ruling, round-10 aligned)
Prefer ONE contract with pre-registered ordered phases or decision
branches over serial contracts, whenever the later phase is
deterministic on the earlier phase's outputs and can be kept equally
blind by ordering (validate/gate first, abort before any scientific
output on failure, emit science only on pass). Reserve a separate
contract for genuinely new authority scope: new data access, new
outcome exposure, or a new replication unit. Cheap deterministic
gates folded into the science contract cost nothing and halve
operator ceremony; do not multiply contracts to signal caution.

