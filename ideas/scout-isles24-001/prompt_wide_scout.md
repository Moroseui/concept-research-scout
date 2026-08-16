You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-isles24-001
Preserve existing files unless the task explicitly requires an update.
Do not claim novelty without verified primary sources.
Do not write code unless this is the probe_code stage and human approval exists.

===== charters/isles24/CHARTER.md =====
# Research charter — isles24

**Status:** human-authored governance document, drafted 2026-08-16 at the
operator's direction following Prof. Gao's suggestion of this dataset.
Scores produced under this charter are scoped to it and are not
comparable with scores from any other charter.

## The driver

Prof. Gao has pointed this program at the **ISLES'24 challenge dataset**
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


===== evidence/ledger_digest.md =====
# Ledger digest (auto-generated -- do not edit; run `python scout.py ledger digest`)

76 tracked ideas. Latest state per idea; full history in ledger.jsonl.

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **DATA_ACCESS** x2: Required data, checkpoints, or mappings are not obtainable in practice.
- **IDENTIFIABILITY_FAILURE** x2: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.
- **ANNOTATION_PROVENANCE** x1: Inference depends on who assigned labels / what they could see, and that is undocumented or contaminated.
- **CIRCULARITY** x1: The endpoint is a re-encoding of the input or of the thing being tested.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **scout-013-c05** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.4, audited 2026-08-15] -- Collateral failure written in the cortical veins
- **scout-013-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.2, audited 2026-08-15] -- The vessel map inside the mosaic-attenuation score
- **scout-012-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 4.1, audited 2026-08-15] -- The dilated esophagus inside the fibrosis score
- **scout-010-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.9, audited 2026-08-12] -- CXR-Age put back together from parts a radiologist can measure
- **scout-014-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.8, audited 2026-08-16] -- Redraw the same airway walls with a sharper pencil: does the peribronchial-thickening score follow Pi10?
- **scout-012-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.8, audited 2026-08-15] -- The race signal in chest CT: measure the bone density everyone names and nobody measured
- **scout-010-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.5, audited 2026-08-12] -- Merlin's cirrhosis signal may be the spleen
- **scout-011-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.3, audited 2026-08-13] -- Does Merlin read renal atrophy when it predicts future CKD?
- **scout-013-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.2, audited 2026-08-15] -- Name the skeletal frailty inside mortality prediction
- **scout-013-c04** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.1, audited 2026-08-15] -- The renal artery as a buckled pressure line
- ... and 34 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- conditional-observational: 12
- regional-substitution: 9
- counterfactual-synthesis: 5
- representation-erasure: 3
- natural-paired: 3
- longitudinal-within-subject: 3
- model-output-perturbation: 2
- regional-removal: 1
- cross-reconstruction: 1

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


===== evidence/portfolio_brief.md =====
# Portfolio brief (auto-generated; run `python scout.py brief`)

Actionable ideas with debate verdicts. A revival/recombination
candidate MUST cite the specific condition below that has changed.

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

## idea-012 [PAUSED] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan

**Verdict:** **PAUSE.** Before deciding otherwise, the human should inspect whether the MD.ai-derived scan-level exclusion membership has become available—and is joinable to a frozen obtainable Sybil evaluation split—because without it the study cannot test the specific residual that defines Idea 012.

## idea-011 [PAUSED] -- Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock

**Verdict:** **PAUSE.** The debate converged after a real, persistent objection; this was not a one-round rubber stamp. Before deciding whether to reopen, the human should look first for the missing identification instrument: a confirmed human chest CT resource with retained spectral base-material or dual-kV raw data and linkable age that can provide a measured, post-preprocessing-matched mineralized-to-soft-tissue contrast. Without that—or another genuinely matched real-tissue control—the current experiment cannot distinguish native use of costal cartilage mineralization from response to the deletion operation, regardless of improvements to masks, models, or supervision audits.

**Unresolved:** Can a measured, properly matched control separate mineralization use from the deletion signature?; Could registered longitudinal CT provide a natural contrast?; Is the editable cartilage mask sufficiently precise in the population where the experiment would run?; Are the other Stage-0 assets actually available and clean?

## idea-008 [ACTIVE] -- Does Sybil use CT-defined emphysema geometry?

**Verdict:** **REVISE.** The debate produced a coherent conditional design, but the current `idea_card.json` still describes the superseded reconstruction arm, rung-3 observational logic, `INSPECTED_TRUE` keystone, and obsolete scores. Before deciding whether to advance, the human should look most closely at whether the proposed tissue-for-tissue edit can be validated as in-distribution with a prespecified sham-effect tolerance; that is now the single fact separating a model-use study from an association-only study.

**Unresolved:** Are the local parenchymal substitutions in-distribution for Sybil?; Does a score response isolate CT-emphysema geometry from remaining visible correlates?; Can the required held-out NLST cohort and covariates actually be recovered?

## idea-007 [ACTIVE] -- The same patient at two degrees of inspiration

**Verdict:** **REVISE.** Update the idea card to the converged state-level claim and corrected scores, then require Stage 0 before a probe contract. The single most important thing for the human to inspect is the prespecified DICOM-to-final-tensor comparability gate: whether enough inhale/exhale pairs truly retain matched reconstruction, coordinates, physical scale, and thoracic coverage through the complete pinned CT-CLIP preprocessing pipeline.

**Unresolved:** Do enough actual pairs pass the reconstruction and framing gate?; Is a common physical box compatible with CT-CLIP preprocessing without state-dependent framing?; Is the optional matched-volume 4DCT jitter floor usable?



===== evidence/librarian_proposals.md =====


===== ideas/scout-isles24-001/README.md =====
# Scouting cycle isles24-001

Tracks: baseline, wide, fiction
Charter: isles24 (charters/isles24/CHARTER.md; scores are scoped to this charter and not comparable across charters)


===== ideas/scout-isles24-001/run_provenance.json =====
{
  "timestamp": "2026-08-16T19:39:11+00:00",
  "git_commit": "8f014fe96e89ddb3ebbb5c6378e2651bad171712",
  "claude_cli": "2.1.197 (Claude Code)",
  "codex_cli": "codex-cli 0.147.0",
  "tracks": [
    "baseline",
    "wide",
    "fiction"
  ],
  "seed_concepts": null,
  "prompt_hashes": {
    "actioner.md": "263f5cce53cb0cee",
    "context_memo.md": "4de103654cef2380",
    "critique.md": "5c8ed5c43071eaeb",
    "debate_critic.md": "74f1e299e3c6db50",
    "debate_proposer.md": "6a41797dbc73796a",
    "debate_summary.md": "7243fe771e1f612d",
    "feasibility.md": "48f4f111abfcd1eb",
    "fiction_extract.md": "8ada1a395c25072e",
    "fiction_refine.md": "f2e140a70980fa95",
    "fiction_scout.md": "63b11687055c8624",
    "interpret.md": "7ce78a736a0ae412",
    "interpret_review.md": "c02c16dabab5446d",
    "keystone_screen.md": "f6f206ca8577b47b",
    "librarian.md": "e6977370921ff990",
    "novelty_audit.md": "3139addc91205b1e",
    "probe_code.md": "bc0c52c94d1af371",
    "probe_plan.md": "6249699cb2278e0e",
    "probe_review.md": "6b222a3f766009ea",
    "revise.md": "db7fab4a10c7c32b",
    "scout.md": "c5ae0f349d7a6d67",
    "wide_scout.md": "6f59a27366e2f4a1"
  },
  "agents_toml_hash": "4b0d0da9640a634d"
}


===== ideas/scout-isles24-001/scout_candidates.json =====
{
  "cycle": "scout-isles24-001",
  "charter": "isles24",
  "date": "2026-08-16",
  "track": "baseline,wide,fiction",
  "dataset_verification": {
    "verified_facts": [
      "The 2026 dataset paper reports 245 adult patients from two centers: 149 public training cases and 96 hidden test cases; the older 2024 challenge preprint reported planned counts of 150/100, so the later published realized counts govern (DOI 10.1148/ryai.250603, lines 77, 122-131 of the full text).",
      "Each included case has hyperacute pre-intervention NCCT, CTA and CTP; the release includes raw motion-corrected 4D CTP resampled to 1 frame/s plus CBF, CBV, MTT and Tmax maps, follow-up DWI/ADC acquired 2-9 days after successful reperfusion, and structured baseline/outcome data (DOI 10.1148/ryai.250603; arXiv:2408.10966).",
      "The final-infarct reference was initialized by the ISLES'22 ensemble on DWI and manually corrected in ITK-SNAP by a trained medical student and a neuroradiologist in training; the later paper reports agreement checks against two experienced raters (DOI 10.1148/ryai.250603, methods lines 112-116 and interrater section).",
      "The official repository tree exposes NCCT, CTA, raw CTP, registered perfusion maps, DWI, ADC, lesion masks and phenotype CSVs; the 2026 paper additionally documents machine-generated Circle-of-Willis CTA pseudolabels as nonexpert reference standards (https://github.com/ezequieldlrosa/isles24; DOI 10.1148/ryai.250603).",
      "Official challenge measures are Dice, absolute volume difference, absolute lesion-count difference and lesion-wise F1; ranking averaged per-case metric ranks (official repository and arXiv:2408.10966).",
      "The public training release is CC BY-NC-SA 4.0 on Zenodo DOI 10.5281/zenodo.16731717; the hidden test set remains evaluation-server-only. Registration/verified Grand Challenge accounts were required during the challenge. The code repository is MIT licensed."
    ],
    "source_supported_interpretations": [
      "Because baseline CT precedes treatment while the target is post-treatment DWI, this is an outcome-prediction dataset, not a contemporaneous CT lesion-segmentation dataset.",
      "Successful reperfusion is an inclusion condition, narrowing treatment variation but not eliminating time-to-reperfusion, residual reperfusion-grade, center or protocol effects."
    ],
    "sources": [
      "Riedel et al., Radiology: Artificial Intelligence 2026, DOI 10.1148/ryai.250603, PMID 42017802",
      "de la Rosa et al., arXiv:2408.10966",
      "https://github.com/ezequieldlrosa/isles24",
      "https://doi.org/10.5281/zenodo.16731717",
      "https://isles-24.grand-challenge.org/"
    ]
  },
  "all_questions": [
    {"n": 1, "question": "Is an ISLES'24 final-infarct model using hypoperfusion intensity ratio, the fraction of delayed tissue with severe Tmax delay?", "disposition": "DEVELOPED as isles24-scout-001-c01"},
    {"n": 2, "question": "Is an ISLES'24 model using arterial collateral reach from the occlusion to the threatened territory rather than perfusion deficit volume alone?", "disposition": "DEVELOPED as isles24-scout-001-c02"},
    {"n": 3, "question": "Is an ISLES'24 raw-CTP model using delayed cortical venous drainage as a vascular-reserve signal?", "disposition": "DEVELOPED as isles24-scout-001-c03"},
    {"n": 4, "question": "Is an ISLES'24 model using leukoaraiosis burden as a brain-frailty modifier of final infarction?", "disposition": "DEVELOPED as isles24-scout-001-c04"},
    {"n": 5, "question": "Is an ISLES'24 model using the topology of the perfusion-deficit boundary, like a spreading fire front, to distinguish tissue that will die from tissue that will recover?", "disposition": "DEVELOPED as isles24-scout-001-c05"},
    {"n": 6, "question": "Is an ISLES'24 model using clot burden score from CTA to set the downstream infarct extent?", "disposition": "DROPPED: clot burden and occlusion location are too close to c02 but provide less mechanism-specific information than collateral reach."},
    {"n": 7, "question": "Is an ISLES'24 model using admission ASPECTS from NCCT as a prior on final infarct topology?", "disposition": "DROPPED: automated ASPECTS is computable, but it risks becoming a circular compression of early ischemic change rather than an unexpected signal."},
    {"n": 8, "question": "Is an ISLES'24 model using hemispheric sulcal effacement as a tissue-pressure gauge before visible infarction?", "disposition": "DROPPED (radiology term, too hard): a fully automatic, validated sulcal-effacement measure on hyperacute NCCT was not verified today."},
    {"n": 9, "question": "Is an ISLES'24 raw-CTP model using cardiac pulsatility embedded in the bolus curve to infer collateral competence?", "disposition": "DROPPED (obviously-wrong slot): pulse-related oscillation is measurable, but 1-Hz resampling aliases normal heart rates and makes physiology inseparable from sampling artifact."},
    {"n": 10, "question": "Is an ISLES'24 model using graph-theoretic betweenness of the Circle of Willis as a network-resilience reserve?", "disposition": "DROPPED (cross-domain network science): static CTA often cannot establish communicating-artery patency reliably enough, and c02 asks the more local, identifiable vascular question."}
  ],
  "quota_note": "The requested mode quota is filled (1 A, 2 B, 2 C), all five are CT/radiology, and two explicitly borrow from fields outside medical imaging. Zero revivals: no portfolio unblock condition has a newly verified fact. The instruction 'no more than two on any single dataset' conflicts with this charter's hard requirement that every developed idea concretely use ISLES'24; all five therefore use the single mandated dataset, while no auxiliary dataset is used more than twice. This conflict is disclosed rather than hidden. Three experimental grammars are represented: representation-erasure, regional-substitution and counterfactual-synthesis; the duplicated grammars reflect two distinct paired intervention targets rather than rotating nouns in one observational template.",
  "candidates": [
    {
      "id": "isles24-scout-001-c01",
      "search_mode": "A",
      "entry_point": 1,
      "title": "Does the winning model rediscover the collateral clock?",
      "question": "Is an ISLES'24 final-infarct model using hypoperfusion intensity ratio (HIR), the fraction of delayed tissue with severe Tmax delay?",
      "rung": "Target rung 1: model use of HIR; move to rung 2 with center-held-out replication and a map intervention that changes HIR while preserving total Tmax>6 volume.",
      "deliverable_sentence": "The final-infarct model is using hypoperfusion intensity ratio, a quantitative marker of collateral failure and fast infarct growth.",
      "X_measurement": "HIR = volume(Tmax >10 s) / volume(Tmax >6 s), computed directly from the released Tmax NIfTI after brain masking; no annotator is needed. The established formula and relation to angiographic collaterals are reported in Guenego et al., Eur J Neurol 2020, DOI 10.1111/ene.14181, PMID 32068938. Compute-today test: YES.",
      "suspected_signal": "Severely delayed tissue occupies a larger fraction of the hypoperfused territory when collateral delivery is poor, so less threatened tissue remains viable until reperfusion.",
      "use_vs_association": "Hold total Tmax>6 volume and occlusion territory fixed, then erase the scalar HIR direction from a frozen model representation; a selective loss in prediction and HIR-decoding, beyond matched random directions, distinguishes use from case-level association.",
      "keystone_prerequisite": "A reproducible high-performing ISLES'24 model or checkpoint exposes an internal representation in which HIR is decodable while total hypoperfusion volume can be matched.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The challenge paper verifies that the best multimodal nnU-Net reached only modest Dice, but it does not establish checkpoint availability or HIR decodability; those are the actual load-bearing checks.",
      "rung_reached": "0 now; rung 1 after selective representation erasure; rung 2 after held-out-center and input-space intervention agreement.",
      "dies_like_prior": "Closest is idea-010 (CIRCULARITY). Different because HIR is an independently computed physical ratio and the endpoint is a change in frozen model output under selective erasure, not prediction of a training label from its synonym. DATA_ACCESS remains a live risk because a winning checkpoint was not verified.",
      "closest_prior_work": "de la Rosa et al., arXiv:2408.10966 reports challenge performance and modality use but not a model-use audit for HIR. Guenego et al. (DOI 10.1111/ene.14181) establishes HIR as a collateral/growth marker but studies patients, not model representations. Exact delta: test whether an outcome model operationalizes that named marker.",
      "existing_assets": "149 public cases with Tmax, final masks and clinical tables; official metric code; nnU-Net baseline family; published HIR formula.",
      "smallest_decisive_experiment": "Freeze a model and split by center; within the validation center, match cases on Tmax>6 volume and occlusion territory, train a linear HIR probe on development representations, erase its direction, and compare per-case prediction change with 100 norm-matched random directions. About 149 cases, one model, three seeds, <20 GPU-hours after model availability.",
      "standing_confounds_addressed": "Matching addresses deficit volume and territory; center-held-out evaluation addresses site/vendor partially; random-direction controls address generic representation damage. It does not rule out HIR as a proxy for unmeasured time-to-reperfusion or deconvolution bias. Labels are unused in the primary score-change test; annotation provenance therefore does not drive it.",
      "alternative_explanations": ["Erasure removes a broader severity direction; volume/NIHSS probes before and after are mandatory specificity controls.", "HIR reflects vendor-specific deconvolution; center-held-out replication reduces but does not eliminate this.", "The model uses a correlated spatial pattern rather than HIR itself; an input-space HIR edit is required to move beyond rung 1."],
      "anticipated_negative": "Sensitivity-limited: a null is informative only if HIR is decoded above a preregistered cross-validated threshold and positive-control lesion-volume erasure changes output.",
      "cross_domain": {"borrowed_construct": "A reserve-rate ratio analogous to severity fractions in reliability engineering.", "measurement_it_implies": "The severe-delay fraction within the whole delayed territory.", "what_changes_if_dropped": "Nothing essential; the clinical HIR definition and experiment remain intact."},
      "remaining_legwork": "1-2 days to locate/reproduce a checkpoint, 2 days for metadata audit and split freeze, roughly one week to first decision after a usable model exists.",
      "design_template": "representation-erasure",
      "scores": {
        "clarity": {"value": 5, "why": "One named scalar and one selective-use test."}, "identifiability": {"value": 3, "why": "Erasure plus controls tests use, but correlated severity directions remain."}, "medical_relevance": {"value": 4, "why": "HIR is a recognized collateral and growth marker."}, "interest": {"value": 4, "why": "It asks whether multimodal AI learned a clinician-legible physiological rule."}, "prior_legwork": {"value": 4, "why": "Data, formula, metrics and model family exist; checkpoint status is open."}, "feasibility": {"value": 3, "why": "Capped because the checkpoint/decodability keystone is uninspected."}, "data_readiness": {"value": 4, "why": "Public noncommercial training data; hidden test remains server-only."}, "evaluation_readiness": {"value": 4, "why": "Official segmentation metrics and standard probe controls exist."}, "negative_result_value": {"value": 3, "why": "Useful only after probe sensitivity and positive controls pass."}, "novelty_confidence": {"value": 3, "why": "No verified exhaustive novelty search; precise delta found in primary anchors."}, "regret": {"value": 4, "why": "A cheap interpretability layer on an already trained model."}
      },
      "unverified_claims": ["Winning checkpoint availability", "HIR decodability", "adequate matched support across centers", "novelty beyond searched primary anchors"]
    },
    {
      "id": "isles24-scout-001-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The vascular detour the segmentation model can see",
      "question": "Is an ISLES'24 model using arterial collateral reach from the CTA occlusion to the threatened territory rather than perfusion-deficit volume alone?",
      "rung": "Target rung 1; move toward rung 3 only if the machine measure agrees with an established collateral score in an external labeled cohort.",
      "deliverable_sentence": "The final-infarct model is using the amount of distal arterial territory reached around the occlusion—collateral reach—not merely the size of the perfusion deficit.",
      "X_measurement": "From CTA, use the released TopCoW-style vessel mask plus occlusion mask to compute affected/contralateral distal vessel-length density within atlas-defined downstream territories, normalized by territory volume. This is fully automatic graph/mask arithmetic on a new scan. Compute-today test: YES, conditional on the released pseudolabel files being present per case.",
      "suspected_signal": "Pial and communicating collateral pathways preserve distal arterial filling beyond an occlusion and delay irreversible tissue failure after proximal flow stops.",
      "use_vs_association": "Remove only distal vessel voxels downstream of the occlusion and replace them with contralateral, intensity-matched vessel/background patches while holding CTP and lesion-size priors fixed; a selective output change relative to upstream-vessel and nonvascular shams tests use.",
      "keystone_prerequisite": "The public 149-case release actually contains per-case occlusion masks and Circle-of-Willis/distal-vessel pseudolabels in a coordinate system usable with CTA, with sufficient distal coverage for the proposed reach measure.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The 2026 paper verifies the pseudolabel-generation method, but the official README tree does not enumerate these files; file-level completeness and distal-vessel coverage are the real keystone.",
      "rung_reached": "0; rung 1 after validated regional substitutions; rung 2 after cross-center consistency; rung 3 after measurement validation.",
      "dies_like_prior": "Closest is idea-006: its deletion was extreme OOD. This uses tissue-for-tissue, contralateral intensity-matched substitution and requires discriminator/segmentation-validity gates. Closest kill code is IDENTIFIABILITY_FAILURE; holding the CTP channels fixed separates vascular depiction from perfusion volume, subject to edit validity.",
      "closest_prior_work": "Yang et al., TopCoW challenge, arXiv:2312.17670, supplies topology-aware vessel segmentation; Riedel et al., DOI 10.1148/ryai.250603 documents ISLES'24 vessel pseudolabels. Neither tests whether a final-infarct predictor uses patient-specific distal arterial reach.",
      "existing_assets": "CTA registered to NCCT, occlusion/vessel pseudolabel method, contralateral anatomy, final masks, two-center cohort.",
      "smallest_decisive_experiment": "Stage 0 on 20 cases: verify masks and stable reach measurement. Then train one CTA+CTP model on a frozen center-stratified split and run downstream-vessel, upstream-vessel and nonvascular matched substitutions on 40 held-out cases; report lesion-probability change inside the threatened territory. Approximately 30 GPU-hours plus segmentation QA; no new annotation.",
      "standing_confounds_addressed": "Within-scan contralateral construction holds patient, site, scanner, habitus and referral fixed; keeping CTP fixed separates displayed vessels from perfusion. It does not remove bolus-timing asymmetry, registration error or pseudolabel error. Training-mask provenance is documented; vessel pseudolabels are explicitly nonexpert references and are not treated as ground truth.",
      "alternative_explanations": ["The edit changes contrast texture rather than vessels; vessel-free intensity-matched shams test this.", "The model reads occlusion laterality; upstream-vessel control tests this.", "Pseudolabel truncation creates the apparent reach; file/coverage Stage 0 is mandatory."],
      "anticipated_negative": "Decisive only if edits preserve global intensity distributions, remain in-distribution to a held-out discriminator, and a positive-control occlusion edit moves output; otherwise uninterpretable.",
      "remaining_legwork": "One day for Zenodo file audit, 2-3 days for 20-case measurement validation, 1-2 weeks to first model-use result.",
      "design_template": "regional-substitution",
      "entry_point_2_requirements": "Measurement: affected/contralateral distal vessel-length density. Artifact confusion: bolus timing and substitution seams; both receive explicit controls.",
      "scores": {
        "clarity": {"value": 4, "why": "Named vascular quantity, though its exact distal territory needs freezing."}, "identifiability": {"value": 3, "why": "Modalities are held fixed and shams are strong, but edit validity is load-bearing."}, "medical_relevance": {"value": 5, "why": "Collateral supply governs tissue survival and transfer/treatment decisions."}, "interest": {"value": 5, "why": "A patient-specific vascular detour inside a voxel model is compelling and legible."}, "prior_legwork": {"value": 4, "why": "Registered CTA and vessel-label method exist; per-case files unverified."}, "feasibility": {"value": 3, "why": "Capped by uninspected file coverage and edit validity."}, "data_readiness": {"value": 3, "why": "Public under noncommercial terms but file completeness needs inspection."}, "evaluation_readiness": {"value": 3, "why": "Official output metrics exist; intervention validity metrics are custom."}, "negative_result_value": {"value": 3, "why": "A gated clean null would exclude a specific vascular channel."}, "novelty_confidence": {"value": 3, "why": "Precise gap not exhaustively audited."}, "regret": {"value": 5, "why": "The dataset uniquely co-releases the needed vascular and outcome views."}
      },
      "unverified_claims": ["Per-case public vessel/occlusion mask completeness", "distal-vessel resolution", "in-distribution substitution", "checkpoint availability"]
    },
    {
      "id": "isles24-scout-001-c03",
      "search_mode": "B",
      "entry_point": 2,
      "title": "Read the stroke from the blood leaving, not only entering",
      "question": "Is an ISLES'24 raw-CTP model using delayed cortical venous drainage as a vascular-reserve signal?",
      "rung": "Target rung 1; move to rung 2 with center-held-out temporal controls and to rung 3 only after external validation against COVES/time-resolved venous scoring.",
      "deliverable_sentence": "The raw-CTP model is using delayed cortical venous drainage on the affected side as a marker of tissue that will infarct despite reperfusion.",
      "X_measurement": "Segment major cortical veins/sinuses from late 4D-CTP frames, extract affected/contralateral time-to-peak and area-under-curve ratios, and aggregate vein of Labbé, superficial middle cerebral and Trolard territories. Singh et al., Neuroradiology 2022, PMID 34704112, established time-resolved venous opacification; Wang et al., Eur J Radiol 2026, DOI 10.1016/j.ejrad.2026.112671, gives HU-ratio formulas. Compute-today test: YES as a defined automatic intensity/time-curve measurement, although a released vein segmenter was not verified.",
      "suspected_signal": "Slow or incomplete venous filling integrates upstream collateral delivery and microvascular transit; ischemic tissue with poor inflow/outflow reserve has delayed, asymmetric venous return.",
      "use_vs_association": "Temporally replace only venous-phase curves in affected venous masks with contralateral curves while preserving arterial bolus, baseline anatomy and perfusion-map channels; compare against equal-volume parenchymal and temporal-shift shams.",
      "keystone_prerequisite": "The released 1-frame/s motion-corrected 4D CTP retains late venous coverage and sufficient temporal duration to estimate affected/contralateral cortical-vein curves in most cases.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The methods verify resampling and raw-series release but do not report temporal coverage or venous visibility; this is deliberately the true inference prerequisite, not merely 'raw CTP exists'.",
      "rung_reached": "0; rung 1 after valid venous-curve substitutions; higher only after cross-center and clinical-measure validation.",
      "dies_like_prior": "Closest is idea-016, killed because reflux and protocol were inseparable. This design uses within-scan affected/contralateral timing and preserves the patient's arterial input function during substitution, but injection timing and truncation remain explicit threats. It also inherits idea-006's OOD warning and gates edits.",
      "closest_prior_work": "Singh et al. (PMID 34704112) associated temporal venous scores with outcome but found no added outcome benefit beyond arterial collaterals; Wang et al. (DOI 10.1016/j.ejrad.2026.112671) quantified CTA venous HU ratios. Neither asks whether a raw-CTP infarct model uses venous dynamics. Negative prior evidence makes the model-use question sharper, not novel by assertion.",
      "existing_assets": "Raw 4D CTP, registered maps, final masks, two centers, contralateral internal control, established vein/time-curve definitions.",
      "smallest_decisive_experiment": "Stage 0: inspect time axes and vein contrast in all 149 headers plus 20 representative series; require >=80% analyzable late venous curves. If passed, train raw-CTP and map-only matched models, then run venous substitutions on 40 frozen cases. Roughly two weeks and 40-80 GPU-hours; no annotation.",
      "standing_confounds_addressed": "Within-scan ratios hold patient/site/vendor/habitus fixed; preserving arterial input reduces injection-timing confounding; map-only model is a modality control. Not ruled out: center-specific temporal truncation, motion correction artifacts and vein-segmentation error. Labels are unnecessary for the primary paired output delta.",
      "alternative_explanations": ["The model reads generic late enhancement; equal-volume parenchymal controls test this.", "The model reads arterial delay leaking into vein masks; eroded venous masks and arterial-curve preservation test this.", "Temporal truncation encodes site; center-held-out and duration stratification are mandatory."],
      "anticipated_negative": "Decisive if venous curves are measurable and raw-CTP model responds to arterial positive-control edits; otherwise sensitivity-limited.",
      "remaining_legwork": "1-2 days for header audit, 3-5 days for automated vein-mask feasibility, 2 weeks to first result if the gate passes.",
      "design_template": "regional-substitution",
      "entry_point_2_requirements": "Measurement: affected/contralateral venous time-to-peak and AUC. Artifact confusion: site-specific truncation and arterial contamination.",
      "scores": {
        "clarity": {"value": 4, "why": "Specific vessels, curves and intervention."}, "identifiability": {"value": 3, "why": "Within-scan temporal intervention is strong but mask contamination remains."}, "medical_relevance": {"value": 4, "why": "Venous reserve could explain failure despite arterial reperfusion."}, "interest": {"value": 5, "why": "Most stroke AI looks at inflow; testing outflow is a sharp inversion."}, "prior_legwork": {"value": 3, "why": "Clinical measures and raw data exist; no verified automatic vein tool."}, "feasibility": {"value": 3, "why": "Capped; temporal coverage is uninspected."}, "data_readiness": {"value": 4, "why": "Raw time series are explicitly released."}, "evaluation_readiness": {"value": 3, "why": "Paired deltas are simple; vein-quality gates are custom."}, "negative_result_value": {"value": 3, "why": "Useful after coverage and positive-control gates."}, "novelty_confidence": {"value": 3, "why": "No exhaustive search."}, "regret": {"value": 4, "why": "The rare raw time series makes the question unusually cheap here."}
      },
      "unverified_claims": ["Late venous temporal coverage", "automatic vein-mask accuracy", "raw-CTP model performance", "clean arterial/venous separation"]
    },
    {
      "id": "isles24-scout-001-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The frail brain around the threatened territory",
      "question": "Is an ISLES'24 model using leukoaraiosis burden as a brain-frailty modifier of final infarction?",
      "rung": "Mode C, target rung 1. Move up only with spatially localized edits and replication outside this successful-reperfusion cohort.",
      "deliverable_sentence": "The final-infarct model is using pre-existing leukoaraiosis—the chronic white-matter injury visible on NCCT—as a modifier of which hypoperfused tissue dies.",
      "X_measurement": "Compute bilateral periventricular/deep white-matter low-attenuation burden from NCCT using atlas registration, CSF exclusion and age-adjusted HU z-scores; report volume and radial distribution. This is a deterministic image measurement on an unseen scan with no annotator, though clinical validity on acute defaced NCCT is unverified. Compute-today test: YES technically.",
      "suspected_signal": "Chronic small-vessel injury reduces microvascular reserve and tissue resilience, so equal acute hypoperfusion may yield different final injury in a structurally frail white-matter bed.",
      "use_vs_association": "Within narrow HIR, deficit-volume, age and NIHSS strata, remove the learned leukoaraiosis representation and require region-specific output changes inside threatened white matter; observational association alone is explicitly insufficient.",
      "keystone_prerequisite": "An automatic NCCT leukoaraiosis measure has test-retest/contrast robustness adequate to separate chronic white-matter low attenuation from acute ischemia and CSF in ISLES'24.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "NCCT and follow-up DWI are verified, but the measurement's construct validity in acute stroke is unverified and load-bearing; a clean-looking segmentation is not enough.",
      "rung_reached": "0; rung 1 after measurement validation plus selective representation removal; rung 2 requires external replication.",
      "dies_like_prior": "Closest is idea-005 (ANNOTATION_PROVENANCE), but no human rating is used. The more relevant danger is CIRCULARITY: acute hypodensity could be mislabeled as chronic leukoaraiosis. Contralateral symmetry, DWI exclusion and periventricular priors reduce but may not eliminate it; failure of that gate kills the idea.",
      "closest_prior_work": "The ISLES'24 papers do not report leukoaraiosis decomposition. Clinical literature relates white-matter disease to stroke outcomes, but a primary automated-NCCT measurement paper and exact model-use duplicate remain to be pinned; novelty is not claimed.",
      "existing_assets": "Baseline NCCT, registered acute modalities, follow-up DWI lesion mask, age and NIHSS, two-center design, public brain atlases.",
      "smallest_decisive_experiment": "Stage 0 on 30 cases: compute the measure twice across plausible NCCT windows/registrations, exclude acute DWI territory mapped back to NCCT, and require stability plus age association. If passed, probe/erase the leukoaraiosis direction in one frozen model on center-held-out cases. 2-3 weeks, <30 GPU-hours.",
      "standing_confounds_addressed": "Age, HIR, deficit volume, NIHSS, center/vendor and territory enter matching; DWI exclusion addresses acute-lesion contamination. Not ruled out: generalized atrophy, occult old infarcts, scanner HU calibration and referral selection. Label provenance is documented but follow-up labels are not the primary use readout.",
      "alternative_explanations": ["The measure is atrophy/CSF partial volume; explicit CSF distance and brain-volume controls test this.", "It captures acute ischemia; mapped DWI/acute perfusion exclusion tests this imperfectly.", "It is an age proxy; age matching tests measured age but not all aging phenotypes."],
      "anticipated_negative": "Uninterpretable if measurement validity fails; otherwise sensitivity-limited because representation removal may miss distributed use.",
      "cross_domain": {"borrowed_construct": "Material fatigue: chronic microvascular damage as reduced reserve before an acute load.", "measurement_it_implies": "Background white-matter damage burden interacting with acute perfusion stress.", "what_changes_if_dropped": "The experiment survives; only the mechanistic metaphor and interaction emphasis weaken."},
      "remaining_legwork": "One week literature/tool audit, one week 30-case measurement gate, another week for a first model test.",
      "design_template": "representation-erasure",
      "entry_point_2_requirements": "Measurement: automatic chronic white-matter low-attenuation burden. Artifact confusion: acute ischemia and CSF partial volume.",
      "scores": {
        "mechanism_clarity": {"value": 4, "why": "Named chronic microvascular injury and reserve interaction, with a concrete measure."}, "identifiability": {"value": 2, "why": "Acute/chronic hypodensity and age remain difficult to separate."}, "medical_relevance": {"value": 4, "why": "Tissue resilience could alter prognostication at equal perfusion."}, "interest": {"value": 4, "why": "It reframes background brain disease as a model-used modifier."}, "clarity": {"value": 4, "why": "Precise claim, with a candid measurement caveat."}, "prior_legwork": {"value": 2, "why": "Dataset assets exist but the measurement tool is not pinned."}, "feasibility": {"value": 2, "why": "Construct validation is a serious barrier."}, "data_readiness": {"value": 4, "why": "All required images/covariates are in the public train set."}, "evaluation_readiness": {"value": 2, "why": "No verified accepted NCCT leukoaraiosis benchmark in this cohort."}, "negative_result_value": {"value": 2, "why": "Distributed-use and measurement sensitivity limit a null."}, "novelty_confidence": {"value": 2, "why": "Closest-work audit incomplete."}, "regret": {"value": 3, "why": "High upside but measurement validity may consume the story."}
      },
      "mode_c_priority_score": 3.6,
      "unverified_claims": ["NCCT leukoaraiosis construct validity", "robust automated measurement", "independent joint support", "novelty"]
    },
    {
      "id": "isles24-scout-001-c05",
      "search_mode": "C",
      "entry_point": 2,
      "title": "A spreading front inside the perfusion deficit",
      "question": "Is an ISLES'24 model using the topology of the perfusion-deficit boundary to distinguish tissue that will die from tissue that will recover?",
      "rung": "Mode C, target rung 1; move up by reproducing the effect across deconvolution implementations and centers.",
      "deliverable_sentence": "The final-infarct model is using the shape of the severe-delay front—its fragmentation, curvature and contact with the existing core—not only perfusion volumes.",
      "X_measurement": "Threshold Tmax at 6 and 10 s; compute connected-component count, Euler characteristic, surface-to-volume ratio, boundary curvature and contact fraction between Tmax>10 and low-CBF regions using standard voxel morphology. Every quantity is deterministic on a new scan without annotation. Compute-today test: YES.",
      "suspected_signal": "Collateral failure advances through vascular territories as a spatial front: compact severe-delay regions contiguous with core may represent coherent failing supply, whereas fragmented peripheral delay may be better collateralized or artifactual.",
      "use_vs_association": "Generate topology-swapped Tmax fields that preserve the exact value histogram, total threshold volumes, hemisphere, distance-to-occlusion and smoothness spectrum but alter component connectivity/contact; paired prediction changes test topology use rather than volume association.",
      "keystone_prerequisite": "A counterfactual generator can alter connectedness/contact while preserving clinically salient Tmax intensity, territory and spatial-frequency distributions closely enough to remain in-distribution.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The maps and target are verified; intervention validity, not map availability, is the true keystone. No existing generator satisfying these constraints was verified.",
      "rung_reached": "0; rung 1 only after all counterfactual validity gates pass; no higher claim from this cohort alone.",
      "dies_like_prior": "Closest is idea-008's unresolved edit-validity problem and idea-006's OOD deletion. This proposes value-histogram- and spectrum-preserving topology swaps plus sham edits, but until a discriminator and blinded image-statistic suite pass, the study is explicitly speculative. Annotation provenance does not enter the primary paired delta.",
      "closest_prior_work": "ISLES'24 challenge methods optimize voxelwise final-infarct prediction; no primary source located that isolates perfusion-front topology at fixed perfusion volumes. Prior perfusion literature, including Guenego et al. DOI 10.1111/ene.14181, emphasizes threshold volumes/ratios, not topology. This is a search result, not proof of novelty.",
      "existing_assets": "Registered Tmax/CBF maps, raw CTP for realism checks, final masks, official per-lesion metrics and two centers.",
      "smallest_decisive_experiment": "On 30 held-out cases, create five topology-altered and five topology-preserving sham maps per case at exactly matched histograms/volumes; require a held-out real-vs-edit discriminator near chance and preserved standard perfusion summaries, then measure local output changes. About 3 weeks and 50 GPU-hours after a frozen model.",
      "standing_confounds_addressed": "Exact volume/histogram matching rules out threshold-volume explanations; territory/distance matching addresses occlusion geography; shams address generic editing. It does not fully rule out deconvolution artifacts, unmeasured vascular topology or generator fingerprints. Center-held-out replication is required.",
      "alternative_explanations": ["Generator seams drive output; spectrum-preserving shams and discriminator gate test this.", "Curvature proxies distance from core/occlusion; those distances are explicitly matched.", "Map topology is deconvolution software topology, not physiology; raw-CTP-derived replication is needed to move up."],
      "anticipated_negative": "Decisive only after a powered sensitivity test using a positive-control volume edit; otherwise sensitivity-limited.",
      "cross_domain": {"borrowed_construct": "Reaction-front geometry from combustion/percolation physics.", "measurement_it_implies": "Connectivity, curvature and core-contact of severe-delay regions at fixed mass.", "what_changes_if_dropped": "The exact morphological experiment remains; only the biological story becomes a generic shape-use audit."},
      "remaining_legwork": "1 week to audit topology literature, 1-2 weeks to validate counterfactuals, one week for the first paired model test.",
      "design_template": "counterfactual-synthesis",
      "entry_point_2_requirements": "Measurement: topology statistics at fixed perfusion volume. Artifact confusion: generator fingerprints and deconvolution-induced islands.",
      "scores": {
        "mechanism_clarity": {"value": 5, "why": "A named failing-supply front and exact topology measurements/intervention."}, "identifiability": {"value": 3, "why": "Fixed histograms and geography isolate topology if edit realism passes."}, "medical_relevance": {"value": 3, "why": "Could improve tissue-fate explanation, though clinical terminology is less established."}, "interest": {"value": 5, "why": "Tests whether spatial organization carries fate information beyond standard volumes."}, "clarity": {"value": 4, "why": "Precise family of quantities; one must be frozen before testing."}, "prior_legwork": {"value": 2, "why": "Data and morphology operators exist; valid generator does not."}, "feasibility": {"value": 2, "why": "Edit realism is hard but appropriate for Mode C."}, "data_readiness": {"value": 4, "why": "Required registered maps are released."}, "evaluation_readiness": {"value": 3, "why": "Official lesion metrics help; counterfactual validity remains custom."}, "negative_result_value": {"value": 3, "why": "A gated null would reject topology beyond volume for this model."}, "novelty_confidence": {"value": 2, "why": "No exhaustive verified gap search."}, "regret": {"value": 4, "why": "Standard perfusion summaries may be throwing away exactly this structure."}
      },
      "mode_c_priority_score": 4.1,
      "unverified_claims": ["In-distribution topology generator", "topology not already covered in stroke AI", "adequate topological variation", "raw-CTP replication feasibility"]
    }
  ]
}


===== STAGE TASK =====
<!-- stage: wide_scout -->
# Wide-mode scouting: raise the ceiling, keep the floor

This track exists because the baseline track selects for ideas that are safe by
sentence two. Here the *hypothesis space* is opened up while the *evidence
standards* stay exactly where the charter puts them. Ambitious in what is
claimed, conservative in how it would be shown.

## What is different from the baseline track

- Multi-step causal stories are allowed: "the model uses X, which it can only
  see because of Y, which implies Z about its failure mode" is eligible if each
  link is separately checkable.
- Cross-field transplants are mandatory, not optional: every candidate must
  borrow a construct, instrument, or law from a field outside medical imaging
  (physiology, physics, forensics, ecology, economics, materials, anything) and
  name the measurement the borrowed construct implies.
- Mechanistic surprise is the selection criterion. Ask: would a radiologist
  raise an eyebrow at the claim, and would they *change something* if it were
  true?

## What is NOT different

- The charter's hard constraint holds: X must be computable from an image
  today, by an existing tool or well-defined formula, with no human annotator.
- The deliverable sentence still has the form "the model is using X." Absence
  of a confound is still not X.
- The use-vs-association test still applies at generation time: for each
  candidate, state in one line how the design distinguishes "the model uses X"
  from "X is merely correlated with the label." If you cannot, the candidate is
  ineligible -- this single pattern killed nine of eleven ideas in cycle one.
- One compute envelope: the smallest decisive experiment must fit one Colab
  GPU session on public data. State the envelope explicitly per candidate.
- Read `evidence/ledger_digest.md` (in your context) before writing anything.
  Fill `dies_like_prior` against the kill-code table, per candidate.

## Keystone evidence rule

Any `keystone_status: INSPECTED_TRUE` claim MUST include a
`keystone_evidence` field quoting the artifact that proves it (URL,
file path, table row, or verbatim excerpt). A bare INSPECTED_TRUE
without evidence is mechanically demoted to NOT_INSPECTED at merge.

## Procedure

1. Write **eight** one-line questions. At least five must connect medical
   imaging to a distinct outside field (name the field in brackets). At least
   two should feel one step past what you believe defensible.
2. Develop **three**. For the five dropped, one line each on why.
3. For each developed candidate, produce the same fields as the baseline scout
   (deliverable_sentence, X_measurement, keystone_prerequisite / status /
   evidence, dies_like_prior, closest_prior_work, smallest_decisive_experiment,
   standing_confounds_addressed, scores, unverified_claims), **plus** a novelty
   triplet:
   - `novelty_neighbors`: the three closest prior works with identifiers,
     found by actually searching, not recalled;
   - `novelty_delta`: the precise difference in one sentence;
   - `why_not_done`: one of `NEW_CAPABILITY` (name the capability or dataset
     that only recently exists), `BLIND_SPOT` (state the reason the field
     missed it), or `TRIED_AND_FAILED` (cite it -- and treat this as a red
     flag, not a disqualifier).
   If you cannot find neighbors, say so in prose and leave the verdict to
   the calibrated novelty vocabulary (`NO_DUPLICATE_FOUND_LIMITED_SEARCH`) -- that is a flag
   for human verification, never proof of novelty.
4. Set `"track": "wide"` on every candidate.

Write `wide_candidates.json` with the shape
`{"candidates": [...], "dropped": [{"question": "...", "why": "..."}]}`.
The `candidates` array contains ONLY the three fully developed candidates;
the one-line notes on dropped questions go under `dropped`, never as stub
entries in `candidates` (stubs are filtered out at merge and waste the slot).
Do not write code. Do not modify any other file.

## Design template (required field)

Set `design_template` to the experimental GRAMMAR of the candidate, one of:
natural-paired, cross-reconstruction, regional-removal,
regional-substitution, representation-erasure, counterfactual-synthesis,
conditional-observational, longitudinal-within-subject,
cross-model-disagreement, model-output-perturbation.
The digest counts these: homogenization is measured by repeated grammar,
not repeated nouns. Pick the closest; if truly none fits, use
`other:<short-name>` and justify it in the card.

