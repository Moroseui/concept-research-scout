# Decision — idea 046, contribution census (contract v2)

This document summarizes `ideas/046/interpretation.md` (round 1, pending
cross-family review). Full derivation and the complete 42-row claims
table live there; every number below also appears there with the same
citation. The superseded v1 definition-audit decision is preserved at git
blob `740effa34b9f201e06348f264337899bb4293157` (see the interpretation's
file-lineage note).

## Result card

- **Idea:** idea-046 — Which observed cases numerically carry the
  band-2/3 reversal? (descriptive finite-population contribution census;
  revise-in-place ratified 2026-09-01)
- **Probe:** probe 046, contract v2 — the contribution census itself; the
  second and final probe of the primary rung, executing what the
  completed v1 definition audit authorized to be drafted.
- **Dataset:** imported idea-023 take-13 table
  `probes/023/results/results_v2/per_patient.csv`, SHA-256
  `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c`
  (ISLES'24 lineage, Zenodo record 16813698; only this frozen CSV was
  read).
- **Primary metric:** `complete_finite_population_contribution_accounting`
  — the full ordered per-case signed contribution table
  (`c_i = (d_i,band3 − d_i,band2)/99`) and signed cumulative sequence,
  gated by the additive identity at tolerance 1e-12
  [cite: summary.json | top-level | primary_metric_name,
  primary_metric_pass].
- **Contract blob:** `942e530737c90b666baa4c9985fd0329296ef140`
  (approved 2026-09-01T22:37:49Z)
  [cite: resolved_config.json | top-level | contract_blob].
- **Results bundle:** `probes/046/results/results_v3` (15 files) at
  commit `30c360113e669542397288437a8690a561f40eb1`, import manifest
  SHA-256 `997914ac477909b4077c2fd0a18d3fbea3054e7df0cd058344422527aededd60`
  [cite: ../results_v3.import.json | top-level | file_count,
  manifest_sha256]; record-result transaction at commit `0d36ee0`.
- **Families:** probe code codex, probe review claude (round-2 APPROVE);
  interpretation authored by claude, codex review pending.
- **Out-of-scope warnings:** this result is not a diffuse-versus-
  concentrated classification in any wording; it names no stable
  carrier, subtype, or clinically distinct group; it makes no
  biological, clinical, causal, predictive, or model-use claim; rank
  stability under repeat measurement is unaddressable in this dataset;
  nothing generalizes beyond these 99 cases and this frozen estimator;
  the optional clinical rung remains behind its own future contract.

## Layer A — Finding

The census completed (`CENSUS_COMPLETE`
[cite: summary.json | top-level | status]) and exactly reconstructs the
realized band-3-minus-band-2 contrast of +0.0550774 (residual
6.938893903907228e-18 vs tolerance 1e-12
[cite: census_summary.json | top-level | additive_identity_residual]).
The largest single contribution, sub-stroke0153, supplies 12.97% of the
net gap; the five largest 48.16%, the ten largest 79.29%, the twenty
largest 109.51% — above 100% because the remaining 79 cases sum to a net
negative [cite: census_summary.json | top_k 1, 5, 10, 20 |
signed_head_net_gap_share]. 54 cases contribute positively (+0.070661),
39 negatively (−0.015584, derived), 6 exactly zero
[cite: census_summary.json | sign_counts, denominators]; the 8 largest
positive contributions reach 53.05% of positive mass and the 17 largest
80.76% [cite: census_summary.json | positive_mass_crossings 0.5, 0.8 |
smallest_k, achieved_share]. By absolute mass the largest case holds
8.28%, the ten largest 50.64%, the twenty largest 73.35%
[cite: census_summary.json | top_k | absolute_mass_share]. These are
exact finite-population facts of this one realized estimator; by
contract they carry no diffuse-versus-concentrated verdict, no
stable-carrier or clinical reading, and no generalization.

## Layer B — Derivation narrative

Gates passed, in order: v1 definition audit complete
(`FEASIBLE_DEFINITION_AUDIT`, cross-family APPROVE, decision ADVANCE
authorizing exactly this contract's drafting); human approval at
2026-09-01T22:37:49Z binding blob `942e5307…`
(`ideas/046/HUMAN_APPROVED_PROBE`); cross-family probe build — round-1
review REVISE (one blocking finding: the contract-mandated v1
lineage-guard comparison was absent), round-2 APPROVE after it was
closed exactly as specified; harness verification passed
(`probes/046/verification.json`, 2026-09-01T22:53:16Z).

One real variant ran (the contract maximum; seed declared, unused; zero
GPU [cite: resolved_config.json | top-level | variants, gpu_minutes]).
Flow: 297 rows / 99 cases in
[cite: input_manifest.csv | input=per_patient.csv | rows, cases] → split
manifest frozen and hashed before the input was opened
[cite: split_manifest.json | top-level | created_before_measurement] →
99 band-1 rows excluded, reason `non_primary_band`, per-row provenance
[cite: summary.json | top-level | excluded_rows] → 198 rows analyzed as
99 paired cases [cite: summary.json | top-level | paired_cases] → v1
lineage guard recomputed and MATCHED (residual bit-identical, sign
counts 54/6/39, delta-space ties 5/5)
[cite: census_summary.json | v1_lineage_guard_comparison | status] →
additive-identity gate passed → positive pattern selected. All 99
contributions, the 99-row signed curve, the 100-row Lorenz curve with
endpoints, and the 54-row positive-mass curve were emitted
[cite: summary.json | top-level | per_case_outputs, signed_curve_rows,
absolute_lorenz_rows, positive_mass_rows]; determinism manifests are
byte-identical; reserved cases accessed 0; the wall cap was not
exceeded. The bundle imported through record-result's local lane and the
transactional tail recorded the PROBED event and re-materialized state
(commit `0d36ee0`). Kill conditions approached: none; the contract
defines no directional negative pattern.

## Layer C — Deep justification

The complete 42-row claims table is in `ideas/046/interpretation.md`,
Layer C, against bundle root `probes/046/results/results_v3` at commit
`30c360113e669542397288437a8690a561f40eb1`. Named cases of record (a
contract-permitted output form): ten largest signed contributors, in
order — sub-stroke0153, 0002, 0166, 0181, 0014, 0098, 0090, 0114, 0025,
0136 [cite: per_case_contributions.csv | signed_rank=1..10 | case_id];
two most negative — sub-stroke0137 (−0.0029142), sub-stroke0183
(−0.0020311) [cite: per_case_contributions.csv | case_id=sub-stroke0137,
sub-stroke0183 | contribution]; six exact zeros with both band d values
exactly 0.0 — sub-stroke0094, 0141, 0142, 0147, 0163, 0175
[cite: per_case_contributions.csv | case_id=… | d_band2, d_band3].
Labeled post-hoc observations (never frozen summaries): the ten head
cases all have negative band-2 d and nine of ten have positive band-3 d;
the case_id tiebreak arbitrated only the zero block.

## Verdict

- **Demonstrates:** exact, complete finite-population accounting of the
  realized estimator (residual 6.94e-18); the frozen share summaries as
  exact facts (top-k signed 12.97/48.16/79.29/109.51%, absolute
  8.28/30.76/50.64/73.35%, positive-mass crossings k=8 at 53.05% and
  k=17 at 80.76%); the sign structure 54/6/39; bit-exact lineage
  continuity with the v1 audit; full discipline (identity, split-first,
  no reserved contact, caps, determinism, complete outputs).
- **Suggests:** three labeled structural observations for successors —
  head cases individually pair negative band-2 with positive band-3
  values; the six zero contributions are zeros in both operands; ties
  are confined to the zero block.
- **Does not establish:** any diffuse-versus-concentrated label;
  carrier, subtype, stability, biological, clinical, causal, predictive,
  or model-use claims; anything beyond these 99 cases and this frozen
  estimator; phenotype completeness.
- **Validity failures:** none — every invalidating-failure class was
  walked and none occurred.
- **Findings:** positive — `CENSUS_COMPLETE`; instantiated deliverable:
  in the realized 99-case estimator, the ten named largest signed
  contributions account for 79.29% of the net band-3-minus-band-2
  contrast, the single largest for 12.97%. Negative — none defined by
  the contract; none occurred.
- **Authorized variants:** one real run (reported); plus the
  non-contract `SMOKE_ONLY` harness verification on synthetic data. No
  other executions exist.

**Next decision:** cross-family review of the interpretation, then
operator ratification. Recommended ledger transition at ratification:
**PAUSED** — the primary deliverable is complete and positive; the
optional clinical rung (D3 read-restriction, D4 joint-display) stays
opportunistic on the next archive staging event. Author and ratify
`ideas/046/registry.yaml` covering both executed nodes (v1 audit, v2
census) per the registry rollout rule. Any stability, carrier, clinical,
or model-use question enters as a separately registered successor with a
real replication unit.

**ADVANCE**
