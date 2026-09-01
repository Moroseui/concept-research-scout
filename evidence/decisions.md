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
