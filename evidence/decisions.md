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
