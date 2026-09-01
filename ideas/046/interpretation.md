# Interpretation — idea 046, definition-audit probe (contract v1)

## Result card

- **Idea:** idea-046 — Which observed cases numerically carry the band-2/3
  reversal? (post-revision descriptive contribution census; revise-in-place
  ratified by the operator 2026-09-01, `unblock_ack.txt` on record)
- **Probe:** probe 046, contract v1 — the outcome-blind
  contribution-definition audit. Position in the experiment sequence: the
  first and only probe executed under this idea; the contract itself binds
  its successor ("authorizes only drafting a separate scientific census
  contract after human review"), which has not been drafted.
- **Dataset:** the imported idea-023 take-13 per-patient table,
  `probes/023/results/results_v2/per_patient.csv`, SHA-256
  `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c`
  (contract-pinned). Upstream lineage: idea-023 take-13 (contract
  `03d4545fe293…`), derived from ISLES'24, Zenodo record 16813698. The
  probe read no ISLES'24 payload, image, phenotype, or cache file — only
  this one frozen CSV.
- **Primary metric:** absolute algebraic residual
  `abs(sum_i(c_i) − (mean_i(d_i,band3) − mean_i(d_i,band2)))` with
  `c_i = (d_i,band3 − d_i,band2)/99`, computed under stable summation
  (`math.fsum`), required ≤ 1e-12 in IEEE-754 double precision.
- **Contract blob:** `3996009bccfcfa939984fed051ee303a29a960a0`
  (verified against `ideas/046/HUMAN_APPROVED_PROBE` and recorded by the
  run itself [cite: resolved_config.json | top-level | contract_blob]).
- **Results bundle:** `probes/046/results/results_v2`, 12 files, imported
  2026-09-01T22:15:39Z at commit `dd5962fb7c95edc8589baf020e58b9fa6f0ed332`
  (byte-manifest SHA-256 `8b813d1d703275a9ee86f3dbb0ad7026a6cd13f75a72cd77aab0f998a58cd79d`
  [cite: ../results_v2.import.json | top-level | manifest_sha256]).
- **Families:** probe code authored by the codex family, probe review by
  the claude family (two rounds, round-2 APPROVE). This interpretation is
  authored by the claude family; cross-family review by the codex family
  is pending (round 1).
- **Out-of-scope warnings — this result must NOT be read as:**
  - any statement about which cases dominate the band-2/3 reversal, how
    concentrated the realized estimator is, or whether a small set
    carries it — the probe was designed not to reveal that and did not;
  - evidence for or against idea-023's scientific finding, beyond the
    arithmetic fact that its band-gap estimator admits an exact per-case
    decomposition;
  - any stable-carrier, patient-subtype, population, biological,
    clinical, causal, predictive, or model-use claim;
  - authorization to run the census. The positive pattern authorizes
    exactly one thing: drafting a separate census contract for human
    review.

## Layer A — Finding

The outcome-blind definition audit passed on the exact frozen table: the
status is `FEASIBLE_DEFINITION_AUDIT`, with the per-case contribution
formula reconstructing the equal-patient band-3-minus-band-2 mean gap to
a residual of 6.938893903907228e-18 — about five orders of magnitude
inside the 1e-12 tolerance. Every frozen descriptive summary is
mathematically well-posed: all three denominators (signed total, positive
mass, absolute mass) are finite and nonzero, top-k shares are definable at
k = 1, 5, 10, and 20, and both positive-mass share targets (50%, 80%) are
definable. The frozen case_id tie rule makes both contract orderings
unique, so every future census output is deterministic. No case
identifier, contribution value, rank, share, or band mean was persisted or
logged, and zero reserved cases were touched. The single most important
caveat: this is a feasibility verdict about definitions, not a scientific
result — it reveals nothing about who carries the reversal, and it
authorizes only the drafting of a separate census contract.

## Layer B — Derivation narrative

**Gates before execution.** The candidate reached this probe through: the
three-round debate (REVISE with a human unblock), the operator's
claim-identity ruling of 2026-09-01 (revise-in-place ratified,
`ideas/046/unblock_ack.txt`), the feasibility GO of 2026-09-01, contract
v1 drafting, and human approval at 2026-09-01T22:00:13Z binding contract
blob `3996009bccfcfa939984fed051ee303a29a960a0`
(`ideas/046/HUMAN_APPROVED_PROBE`; the in-file `human_approved: false`
line is the standing marker convention — authority lives in the marker
file, as recorded in probe_review round-1 finding 1). Probe code was
built cross-family: round-1 review returned REVISE with two blocking
findings (B1: residual values not persisted; B2: ordering-uniqueness
verdict hardcoded); round 2 resolved both exactly as specified and
returned APPROVE with no scope expansion. The harness smoke verification
completed under 60 seconds with matching determinism manifests
(`probes/046/verification.json`, passed, 2026-09-01T22:14:53Z); smoke is
forced to `SMOKE_ONLY` and can never satisfy a contractual pattern.

**The run (single authorized variant).** One real variant executed
(`variants: 1, gpu_minutes: 0, smoke: false`
[cite: resolved_config.json | top-level | variants, gpu_minutes, smoke]),
Python-stdlib-only environment [cite: environment.txt | top-level |
dependencies]. The declared seed (20260901) exists for harness
reproducibility only; the approved analysis uses no randomness. Order of
operations, as the contract requires: the anonymous split manifest was
frozen before the input CSV was first opened
[cite: split_manifest.json | top-level | created_before_measurement],
then the input identity gate passed against the approved SHA-256
[cite: determinism_manifest_start.json | top-level | input_sha256].

**CONSORT-style flow.** In: 297 data rows, 99 unique cases
[cite: input_manifest.csv | input=per_patient.csv | rows, cases].
Excluded: 99 rows, all with reason `non_primary_band` — the band-1 rows,
source lines 2–296 [cite: exclusions.csv | reason=non_primary_band | all
99 data rows] ([cite: summary.json | top-level | excluded_rows]).
Analyzed: 198 rows forming 99 paired cases with identical band-2 and
band-3 case sets and no duplicate keys (cohort gate; enforced in code,
reflected in [cite: summary.json | top-level | paired_cases] and the 99
all-finite pair rows of [cite: sample_audit.csv | all data rows |
paired_rows, finite_inputs, finite_delta]). Reserved cases accessed: 0
[cite: summary.json | top-level | reserved_cases_accessed].

**Measurement and close-out.** The algebra and denominator audit ran
in-memory in a single pass; the residual gate passed
[cite: definition_audit.json | top-level |
algebra_residual_within_tolerance]; the status classifier selected the
contract's positive pattern [cite: summary.json | top-level | status].
The five-minute wall cap was enforced in-code and not exceeded (a breach
exits 8 before any status is written; the run completed with status and
all required outputs). Start and end determinism manifests are
byte-identical (verified by diff during this interpretation). All six
contract-required outputs are present, plus the split, exclusion,
sample-audit, and determinism artifacts. No-result-exposure held:
`scientific_values_exposed: false` [cite: summary.json | top-level |
scientific_values_exposed], and no output or log line contains a case
identifier, d/delta/c value, rank, share, curve coordinate, band mean, or
gap value.

**Import.** The bundle was imported through record-result's local lane
(`source_commit: null`, first-add ancestry) with 12 files
[cite: ../results_v2.import.json | top-level | file_count], validated
under the contract-declared interface (phase field absent, tolerated per
S2b), and the transactional tail recorded the PROBED scrutiny event,
digest, and re-materialized state at commit `c882615`.

**Kill conditions approached: none.** No invalidating-failure class
(authority, input-identity, cohort, algebra, exposure, scope/leakage,
deviation, output/provenance) occurred or was neared; the negative
pattern `DEFINITION_REVISION_REQUIRED` did not occur.

## Layer C — Deep justification (claims table)

Bundle root: `probes/046/results/results_v2` at commit
`dd5962fb7c95edc8589baf020e58b9fa6f0ed332`. Every quantitative claim in
this document resolves to one of these rows.

| # | Claim | Value | Citation |
|---|-------|-------|----------|
| 1 | Status is the contract's positive pattern | `FEASIBLE_DEFINITION_AUDIT` | [cite: summary.json \| top-level \| status] |
| 2 | Primary metric name | `additive_residual_within_1e-12` | [cite: summary.json \| top-level \| primary_metric_name] |
| 3 | Primary metric passed | `true` | [cite: summary.json \| top-level \| primary_metric_pass] |
| 4 | Stable-summation residual | 6.938893903907228e-18 | [cite: definition_audit.json \| top-level \| stable_summation_residual] |
| 5 | Ordinary-summation residual (diagnostic only, no gate role) | 6.938893903907228e-18 | [cite: definition_audit.json \| top-level \| ordinary_summation_residual_diagnostic_only] |
| 6 | Residual within tolerance | `true` | [cite: definition_audit.json \| top-level \| algebra_residual_within_tolerance] |
| 7 | Signed total finite and nonzero | `true` | [cite: definition_audit.json \| denominators \| signed_total_finite_nonzero] |
| 8 | Positive mass finite and nonzero | `true` | [cite: definition_audit.json \| denominators \| positive_mass_finite_nonzero] |
| 9 | Absolute mass finite and nonzero | `true` | [cite: definition_audit.json \| denominators \| absolute_mass_finite_nonzero] |
| 10 | Sign counts of per-case deltas | positive 54, zero 6, negative 39 | [cite: definition_audit.json \| sign_counts \| positive, zero, negative] |
| 11 | Exact-tie counts under the frozen orderings | signed 5, absolute 5 | [cite: definition_audit.json \| tie_counts \| signed, absolute] |
| 12 | Deterministic case_id tie rule resolves every tie | `true` | [cite: definition_audit.json \| top-level \| deterministic_secondary_case_id_rule_defined] |
| 13 | Top-k definable at k = 1, 5, 10, 20 | all `true` | [cite: definition_audit.json \| top_k_definable \| 1, 5, 10, 20] |
| 14 | 50% and 80% positive-mass targets definable | both `true` | [cite: definition_audit.json \| target_share_definable \| 0.5, 0.8] |
| 15 | All frozen summaries defined | `true` | [cite: summary.json \| top-level \| all_summaries_defined] |
| 16 | Input identity | SHA-256 `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c` | [cite: resolved_config.json \| top-level \| input_sha256]; identically in [cite: input_manifest.csv \| input=per_patient.csv \| sha256] |
| 17 | Input size | 297 rows, 99 cases | [cite: input_manifest.csv \| input=per_patient.csv \| rows, cases] |
| 18 | Paired cases analyzed | 99 | [cite: summary.json \| top-level \| paired_cases] |
| 19 | Rows excluded (band 1) | 99, all `non_primary_band` | [cite: summary.json \| top-level \| excluded_rows]; [cite: exclusions.csv \| reason=non_primary_band \| all 99 data rows] |
| 20 | Reserved cases accessed | 0 | [cite: summary.json \| top-level \| reserved_cases_accessed]; [cite: split_manifest.json \| top-level \| reserved_cases_accessed] |
| 21 | Split frozen before measurement, 99 opened-census slots | `true`, 99 | [cite: split_manifest.json \| top-level \| created_before_measurement, opened_census_cases] |
| 22 | No scientific value exposed | `false` (exposure flag) | [cite: summary.json \| top-level \| scientific_values_exposed] |
| 23 | Governing contract blob recorded by the run | `3996009bccfcfa939984fed051ee303a29a960a0` | [cite: resolved_config.json \| top-level \| contract_blob] |
| 24 | Caps honored | variants 1, gpu_minutes 0, smoke false | [cite: resolved_config.json \| top-level \| variants, gpu_minutes, smoke] |
| 25 | Determinism manifests identical | start = end (byte-identical) | [cite: determinism_manifest_start.json \| top-level \| all keys] vs [cite: determinism_manifest_end.json \| top-level \| all keys] |
| 26 | Import identity | 12 files, manifest SHA-256 `8b813d1d703275a9ee86f3dbb0ad7026a6cd13f75a72cd77aab0f998a58cd79d`, 2026-09-01T22:15:39Z | [cite: ../results_v2.import.json \| top-level \| file_count, manifest_sha256, imported_utc] |

Repo-level (non-bundle) anchors: approval timestamp and blob —
`ideas/046/HUMAN_APPROVED_PROBE`; smoke verification —
`probes/046/verification.json` (`passed: true`,
2026-09-01T22:14:53Z); bundle commit — `dd5962f`; record-result
transaction commit — `c882615`.

## Demonstrates

All of the following are hard-constraint outcomes of a deterministic,
randomness-free procedure; none depends on an effect size, so
DEMONSTRATES is the correct register (the single-seed rule does not
apply — the seed is declared and unused).

1. **The frozen contribution definition is algebraically coherent on the
   real table.** The additive identity holds with residual
   6.938893903907228e-18 against the 1e-12 tolerance (claims 3, 4, 6) —
   roughly 1.4 × 10^5 times smaller than the bound. The
   ordinary-summation diagnostic equals the stable residual (claim 5), so
   the identity does not depend on the summation routine at this scale.
2. **Every frozen summary is well-posed.** All three denominators are
   finite and nonzero; top-k is definable at each frozen k; both share
   targets are definable (claims 7–9, 13–15). The negative pattern
   (`DEFINITION_REVISION_REQUIRED`) has no surviving trigger.
3. **The frozen orderings are deterministic.** The case_id secondary rule
   resolves all ties in both orderings (claims 11, 12), so the future
   census output is unique and reproducible by construction.
4. **Cohort structure matches the inspected keystone.** 297 rows in, 99
   band-1 rows excluded with per-row provenance, 99 paired cases with
   identical band-2/band-3 case sets (claims 17–19), reproducing the
   keystone census a fourth time, now under the approved gate.
5. **Discipline held.** Input identity, split-before-measurement,
   zero reserved-case contact, no-result-exposure, byte-identical
   determinism manifests, all required outputs, one variant, zero GPU
   (claims 16, 20–25).

## Suggests

Nothing in this probe suggests anything about the scientific question —
by design. Two structural notes, each a **source-supported inference**
from recorded counts (not from any exposed value), are recorded for the
census-contract author:

1. Six of the 99 per-case deltas are exactly zero (claim 10). In IEEE-754
   arithmetic a subtraction of finite doubles is exactly zero only when
   the operands compare equal, so six cases have numerically equal
   band-2 and band-3 `d` values; the difference of equal operands is
   `+0.0` under round-to-nearest, so all six zero deltas share one
   representation.
2. Both tie counts equal 5 (claim 11) — exactly what the six identical
   zero deltas contribute (6 − 1 = 5) — so the zeros are the only exact
   ties under the signed ordering, and the matching absolute count
   further implies no duplicated magnitude among the nonzero deltas. In
   practice the case_id tiebreak will arbitrate only within the
   zero-contribution block; the census contract should state how
   zero-contribution cases are displayed.

These notes must not be extended into any statement about dominance or
concentration; the sign split (54/6/39) is a recorded count, not a
finding about who carries the reversal.

## Does not establish

- Which cases dominate the band-3-minus-band-2 contrast, the shape of
  the ranked or Lorenz curves, any top-k share, or any smallest-k value —
  none was computed to an artifact, and none may be anticipated from
  this result.
- Whether the reversal is diffuse or concentrated in any sense — the
  debate already removed that binary from the candidate, and this probe
  adds nothing to it.
- Any stable-carrier, biological, clinical, causal, predictive,
  population, or model-use claim (prohibited by contract).
- Anything about idea-023's scientific interpretation beyond the
  arithmetic decomposability of its frozen estimator.
- Phenotype content-level completeness (populated NIHSS/mRS values for
  the 99 cases) — untouched by this probe; it remains the optional
  clinical rung's honest unknown.
- Transport beyond this exact table: the verdict is about these frozen
  definitions on these 99 cases under this contract, nothing wider.

## Validity failures

None. No invalidating-failure class in the contract occurred: authority
verified (fresh marker binding the exact blob), input identity exact,
cohort gate clean, algebra within tolerance, no exposure event, no
scope/leakage contact (no phenotype, reserved-case, image, voxel, or
cache read), no analysis deviation (one variant, frozen formulas, no
randomness consumed), and all required outputs present with provenance.
No run was invalidated and no result was reinterpreted.

## Positive and negative findings

- **Positive finding:** `FEASIBLE_DEFINITION_AUDIT` (claim 1) — the
  contract's positive pattern, carrying its stated and only consequence:
  a separate scientific census contract may now be drafted for human
  review.
- **Negative findings:** none. The negative pattern did not occur; no
  frozen summary is undefined.

## Authorized variants (complete report)

The contract caps `maximum_variants: 1`. Exactly one real variant was
executed and is reported above; it is the variant this interpretation
describes (claims 1, 24). Additionally, the probe-build harness smoke ran
on synthetic input during verification (status `SMOKE_ONLY`,
`probes/046/verification.json`); it is not a contract variant, satisfies
no contractual pattern by construction, and touched no real data. No
other execution of this probe exists.

## Next decision

**ADVANCE**, with the contract's own narrow semantics: the positive
pattern authorizes only drafting the separate scientific census contract,
behind fresh human approval. Concretely, in order:

1. Draft the census contract for the frozen Rung-0 outputs (signed
   contributions, cumulative and Lorenz curves, fixed top-k shares,
   smallest-k targets), encoding: the D3 read-restriction protocol for
   any future phenotype restage, the D4 joint-display rule for clinical
   contrasts, the exploratory-by-construction label, the zero-contribution
   display convention (see Suggests), and the prohibited-conclusions list
   verbatim from the card.
2. Per the 2026-09-01 registry rollout rule ("every new approved probe
   gets a registry"), author `ideas/046/registry.yaml` covering this
   executed definition-audit node before the census contract is approved.
3. The optional clinical rung remains opportunistic on the next archive
   staging event; nothing here advances or blocks it.

No census computation, no phenotype access, and no further inference are
authorized by this interpretation.
