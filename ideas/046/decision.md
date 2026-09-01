# Decision — idea 046, definition-audit probe (contract v1)

This document summarizes `ideas/046/interpretation.md` (round 1, pending
cross-family review). Full derivation and the complete claims table live
there; every number below also appears there with the same citation.

## Result card

- **Idea:** idea-046 — Which observed cases numerically carry the
  band-2/3 reversal? (descriptive contribution census; revise-in-place
  ratified 2026-09-01)
- **Probe:** probe 046, contract v1 — outcome-blind
  contribution-definition audit. First and only probe executed under this
  idea; its positive pattern authorizes only drafting a separate census
  contract, which does not yet exist.
- **Dataset:** imported idea-023 take-13 table
  `probes/023/results/results_v2/per_patient.csv`, SHA-256
  `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c`
  (ISLES'24 lineage, Zenodo record 16813698; no ISLES'24 payload was
  read — only this frozen CSV).
- **Primary metric:** absolute residual of the additive identity
  `abs(sum_i((d_i,3 − d_i,2)/99) − (mean_i(d_i,3) − mean_i(d_i,2)))`,
  stable summation, tolerance 1e-12.
- **Contract blob:** `3996009bccfcfa939984fed051ee303a29a960a0`
  [cite: resolved_config.json | top-level | contract_blob].
- **Results bundle:** `probes/046/results/results_v2` (12 files) at
  commit `dd5962fb7c95edc8589baf020e58b9fa6f0ed332`, import manifest
  SHA-256 `8b813d1d703275a9ee86f3dbb0ad7026a6cd13f75a72cd77aab0f998a58cd79d`
  [cite: ../results_v2.import.json | top-level | file_count,
  manifest_sha256].
- **Families:** probe code codex, probe review claude (round-2 APPROVE);
  interpretation authored by claude, codex review pending.
- **Out-of-scope warnings:** this result says nothing about which cases
  dominate the reversal or how concentrated the estimator is; it is not
  evidence about idea-023's finding beyond arithmetic decomposability; it
  supports no carrier, biological, clinical, causal, predictive, or
  model-use claim; it does not authorize running the census — only
  drafting its contract for human review.

## Layer A — Finding

The outcome-blind definition audit passed: status
`FEASIBLE_DEFINITION_AUDIT` [cite: summary.json | top-level | status],
with the per-case contribution formula reconstructing the equal-patient
band-3-minus-band-2 mean gap to a residual of 6.938893903907228e-18
[cite: definition_audit.json | top-level | stable_summation_residual] —
about five orders of magnitude inside the 1e-12 tolerance. Every frozen
summary is well-posed: all three denominators finite and nonzero, top-k
definable at k = 1, 5, 10, 20, both share targets definable
[cite: summary.json | top-level | all_summaries_defined], and the frozen
case_id tie rule makes both orderings unique
[cite: definition_audit.json | top-level |
deterministic_secondary_case_id_rule_defined]. No case identifier,
contribution value, rank, or share was persisted or logged
[cite: summary.json | top-level | scientific_values_exposed], and zero
reserved cases were touched [cite: summary.json | top-level |
reserved_cases_accessed]. The most important caveat: this is a
feasibility verdict about definitions — it reveals nothing about who
carries the reversal.

## Layer B — Derivation narrative

Gates passed, in order: operator claim-identity ruling (revise-in-place,
`unblock_ack.txt`); feasibility GO (2026-09-01); human approval at
2026-09-01T22:00:13Z binding blob `3996009b…`
(`ideas/046/HUMAN_APPROVED_PROBE`); cross-family probe build — round-1
review REVISE (two blocking findings: residual persistence, hardcoded
ordering verdict), round-2 APPROVE after both were fixed with no scope
expansion; harness smoke verification passed
(`probes/046/verification.json`, forced `SMOKE_ONLY`).

One real variant ran (the contract maximum; seed declared, unused; zero
GPU minutes [cite: resolved_config.json | top-level | variants,
gpu_minutes]). Flow: 297 rows / 99 cases in
[cite: input_manifest.csv | input=per_patient.csv | rows, cases] → 99
band-1 rows excluded, reason `non_primary_band`, per-row provenance
[cite: summary.json | top-level | excluded_rows] → 198 rows analyzed as
99 paired cases with identical band-2/band-3 case sets
[cite: summary.json | top-level | paired_cases] → residual gate passed →
positive pattern selected. The split manifest was frozen before the input
was opened [cite: split_manifest.json | top-level |
created_before_measurement]; start and end determinism manifests are
byte-identical; the wall cap was enforced in-code and not exceeded. The
bundle imported through record-result's local lane and the transactional
tail recorded the PROBED event and re-materialized state (commit
`c882615`). Kill conditions approached: none; no invalidating-failure
class occurred and the negative pattern did not fire.

## Layer C — Deep justification

The complete 26-row claims table is in `ideas/046/interpretation.md`,
Layer C, against bundle root `probes/046/results/results_v2` at commit
`dd5962fb7c95edc8589baf020e58b9fa6f0ed332`. Additional recorded counts,
cited there and restated here for the census-contract author: per-case
delta sign counts positive 54 / zero 6 / negative 39
[cite: definition_audit.json | sign_counts | positive, zero, negative];
exact ties signed 5 / absolute 5
[cite: definition_audit.json | tie_counts | signed, absolute] —
consistent, by IEEE-754 subtraction semantics, only with the six
exact-zero deltas being the sole exact ties (a labeled inference in the
interpretation, not a probe output). These counts are contract-authorized
outputs and must not be read as concentration findings.

## Verdict

- **Demonstrates:** definition coherence (residual 6.94e-18 vs 1e-12),
  well-posedness of every frozen summary, deterministic orderings, cohort
  structure as inspected, full discipline (identity, split-first,
  no-exposure, no reserved contact).
- **Suggests:** nothing scientific, by design; two structural notes for
  the census author (six exactly-zero deltas; ties confined to the zero
  block) are labeled inferences from recorded counts.
- **Does not establish:** dominance, concentration, curve shapes, carrier
  or clinical claims, phenotype completeness, anything beyond this table.
- **Validity failures:** none.
- **Findings:** positive — `FEASIBLE_DEFINITION_AUDIT`; negative — none.
- **Authorized variants:** one real run (reported); plus the non-contract
  `SMOKE_ONLY` harness verification. No other executions exist.

**Next decision:** draft the scientific census contract (encoding the D3
read-restriction protocol, the D4 joint-display rule, the
zero-contribution display convention, and the card's
prohibited-conclusions list) and author `ideas/046/registry.yaml` per the
registry rollout rule, both behind fresh human approval. The optional
clinical rung stays opportunistic on the next archive staging event.

**ADVANCE**
