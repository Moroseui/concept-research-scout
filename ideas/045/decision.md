# Decision — idea 045, probe contract v2

## Result card

- **Idea:** idea-045 — "Did tissue composition create idea-023's sign reversal?"
- **Probe:** probes/045, contract v2 — outcome-blind pooled-slope design
  feasibility audit. Second experiment in idea 045's sequence, succeeding
  the completed v1 interaction audit (blob `e7071541…`, NEGATIVE_PATTERN)
  under the v1 decision's mandated specification revision; one authorized
  variant, one run.
- **Dataset:** two frozen derived tables from the imported idea-023 take-13
  Phase-C bundle (ISLES'24, Zenodo record 16813698 via the parent's
  provenance), pinned by sha256: `bin_tissue_audit.csv` `35e896df…`,
  `per_patient.csv` `1d01551c…` [cite: input_manifest.csv | both rows |
  sha256].
- **Primary metric:** singular-value condition number of the frozen
  three-column bands-2/3 pooled-slope design (intercept, band-3 indicator,
  centered HU imbalance; no interaction), non-intercept columns
  unit-L2-scaled for the conditioning calculation only; frozen bound ≤ 30.
- **Contract blob:** `5615afea1e2f8309745a2d6558bd9118e5e9f1f3`, matching
  the human approval marker of 2026-09-01T05:36:24Z and the bundle's
  `resolved_config.json` (contract_version 2).
- **Results bundle:** `probes/045/results/results_v3/` at commit
  `7de47840d02d601dc802e151ecc9abde68d8f0ed` (import manifest sha256
  `1e104c8b620b946ffe2d58be328067c2a9b786d0096a74736ed6676958baeed1`,
  12 files).
- **Families:** authoring family claude (this document and
  `interpretation.md`); reviewing family codex (cross-family citation
  review; this is round 1).
- **Out-of-scope warnings — this result must NOT be read as:** evidence for
  or against an HU-imbalance/final-infarct association (zero d values were
  read); evidence about whether tissue composition explains idea-023's
  band-2/band-3 reversal; validation of the common-slope restriction as
  scientifically appropriate — the contract's open question for the human;
  validation of median NCCT attenuation as a tissue or viability
  measurement; a claim about any model's use of any signal; or
  authorization to read outcomes under this contract. It is a
  design-geometry feasibility verdict only, scoped to this frozen
  specification on these 99 cases.

## Layer A — Finding

The outcome-blind v2 feasibility audit returned POSITIVE_PATTERN: the
reduced pooled-slope design passes all ten pre-registered gates [cite:
summary.json | status, contractual_gate_satisfied, gates | values].
Condition number 20.22 sits well inside the frozen ≤ 30 bound, maximum row
leverage 0.1549 inside ≤ 0.20, pooled exposure support 29 distinct values
against ≥ 20, and every one of the 99 leave-one-patient-out deletions
preserves rank, conditioning, and leverage within bounds. Because the probe
is deterministic and the deletion sweep is exhaustive, the pass is
structural to the covariate geometry, not a single-patient accident. Zero
outcome values were read and the 49 reserved cases remain untouched, so
the scientific question is exactly as open as before. The most important
caveat: a feasibility pass certifies numerical geometry only — whether one
pooled slope preserves enough of the band-specific attribution question is
the scientific judgment the contract explicitly reserves for the human at
the next approval gate.

## Layer B — Derivation narrative

1. **Governance chain.** The executed v1 audit (contract blob `e7071541…`)
   returned a decisive feasibility negative mandating specification
   revision; its interpretation passed cross-family review (round-2
   APPROVE) and prescribed the pooled-slope respec. Contract v2 was
   drafted (S2c, 2026-09-01) and human-approved at 05:36:24Z binding blob
   `5615afea…`; probe code (run.py sha256 `9733732c…`, commit `f7aec67`)
   passed cross-family review round 1 (APPROVE,
   `ideas/045/probe_review.md`); the harness self-check passed
   2026-09-01T05:47:02Z (`probes/045/verification.json`); the run executed
   05:47:33Z [cite: environment.txt | captured_utc | value]; the bundle
   validated and imported via the record-result gate at commit `7de4784`;
   the transactional tail appended the scrutiny event and re-materialized
   state at commit `b18cc95`.
2. **Flow of rows (CONSORT-style).** In: 594 audit rows and 297 key rows
   [cite: input_manifest.csv | both rows | total_rows]. Excluded: 297 rows
   in 2 records, all reason `non_primary_band` — 198 audit band-1 rows, 99
   per-patient band-1 rows [cite: exclusions.csv | case_id=* | count].
   Selected: 396 audit rows, 198 key rows → joined into 198 analysis rows,
   99 unique cases, 99 per band [cite: summary.json | analysis_rows,
   unique_cases | values]. Reserved cases touched: 0; outcome values read:
   0 [cite: summary.json | reserved_cases_accessed, outcome_values_read |
   values]. The split manifest (hash `6446ad66…`) was frozen before the
   outcome file was opened [cite: split_manifest.json |
   created_before_outcome_file_open | value] and is byte-identical to the
   v1 split — same cohort, changed specification.
3. **Gates.** Integrity and join gates all passed. All ten feasibility
   gates passed, by recorded name: `rank_3`, `condition_number_le_30`,
   `each_band_99_cases`, `each_band_nonzero_iqr`,
   `pooled_at_least_20_distinct`, `maximum_leverage_le_0_20`,
   `top_10_include_at_least_5_patients`, `all_loo_rank_3`,
   `all_loo_condition_le_30`, `all_loo_maximum_leverage_le_0_20`
   [cite: design_diagnostics.json | gates | all keys]. Per the frozen
   stopping rule the run stopped after the single design audit; no outcome
   analysis began.
4. **Kill conditions approached.** None fired. The tightest passed margin
   was the v2-added per-deletion leverage gate: deleting sub-stroke0147
   raises the maximum leverage to 0.18137690505955997, about 91% of the
   0.20 bound [cite: design_diagnostics.json |
   leave_one_patient_out_maximum_leverage_max | value]; every other
   diagnostic passed with wide slack. This is a valid pre-registered
   positive, not a near-miss reinterpreted as one.

## Layer C — Claims table

Bundle root: `probes/045/results/results_v3/` at commit
`7de47840d02d601dc802e151ecc9abde68d8f0ed`.

| Claim | Value | Source |
|---|---|---|
| Status | POSITIVE_PATTERN | [cite: summary.json | status | value] |
| Contractual gate satisfied | true | [cite: summary.json | contractual_gate_satisfied | value] |
| Condition number (primary metric) | 20.222895326167112 | [cite: summary.json | primary_metric_value | value]; [cite: design_diagnostics.json | condition_number | value] |
| Singular values | 14.089047615314039, 1.0066594185504498, 0.6966879563028607 | [cite: design_diagnostics.json | singular_values | list] |
| Rank | 3 | [cite: design_diagnostics.json | rank | value] |
| Pooled distinct imbalance values / n | 29 / 198 | [cite: design_diagnostics.json | pooled_support | distinct_values, n] |
| Pooled IQR / range | 4.0 / −28.0 to +18.0 | [cite: design_diagnostics.json | pooled_support | iqr, minimum, maximum] |
| Band-2 distinct values / IQR / range | 17 / 2.0 / −16.0 to +18.0 | [cite: design_diagnostics.json | band_support.2 | distinct_values, iqr, minimum, maximum] |
| Band-3 distinct values / IQR / range | 26 / 6.0 / −28.0 to +14.0 | [cite: design_diagnostics.json | band_support.3 | distinct_values, iqr, minimum, maximum] |
| Maximum row leverage | 0.15486441040641785 | [cite: design_diagnostics.json | maximum_row_leverage | value] |
| Max-leverage row identity | sub-stroke0109, band 3, imbalance −28.0 (Q1 30.0, Q4 58.0) | [cite: per_row_design.csv | case_id=sub-stroke0109, stratum=3 | hu_imbalance, q1_median_hu, q4_median_hu, leverage] |
| Leave-one-out condition min / max | 20.042406826639716 (sub-stroke0094) / 20.325983967379745 (sub-stroke0147) | [cite: design_diagnostics.json | leave_one_patient_out_condition_min, leave_one_patient_out_condition_max | value; per-case rows in leave_one_patient_out] |
| Leave-one-out max-leverage min / max | 0.154871023519075 / 0.18137690505955997 (sub-stroke0147) | [cite: design_diagnostics.json | leave_one_patient_out_maximum_leverage_min, leave_one_patient_out_maximum_leverage_max | value] |
| Leave-one-out entries / all rank 3 | 99 / true | [cite: design_diagnostics.json | leave_one_patient_out | count; gates.all_loo_rank_3] |
| Top-10 leverage rows, distinct patients | 9 | [cite: design_diagnostics.json | top_10_distinct_patients | value] |
| Pooled HU-imbalance mean (centering) | −0.15909079349402225 | [cite: design_diagnostics.json | pooled_hu_imbalance_mean | value] |
| Analysis rows / unique cases | 198 / 99 | [cite: summary.json | analysis_rows, unique_cases | values] |
| Input row accounting | audit 594→396; keys 297→198; 297 excluded (2 records) | [cite: input_manifest.csv | both rows | total_rows, selected_rows]; [cite: summary.json | excluded_input_rows, exclusion_records | values]; [cite: exclusions.csv | case_id=* | count] |
| Outcome values read / reserved cases accessed | 0 / 0 | [cite: summary.json | outcome_values_read, reserved_cases_accessed | values] |
| Split frozen before outcome access | true; hash 6446ad66… (identical to v1) | [cite: split_manifest.json | created_before_outcome_file_open, sha256 | values]; [cite: probes/045/results/results_v2/split_manifest.json | sha256 | value] |
| Input pins | bin_tissue_audit.csv 35e896df…; per_patient.csv 1d01551c… | [cite: input_manifest.csv | both rows | sha256] |
| Governing contract blob / version | 5615afea1e2f8309745a2d6558bd9118e5e9f1f3 / 2 | [cite: resolved_config.json | contract_blob, contract_version | values] |
| v1 baseline (historical context, not a rerun) | condition 38.889769743817595; max leverage 0.26358236965333054 | [cite: probes/045/results/results_v2/design_diagnostics.json | condition_number, maximum_row_leverage | value] |
| Variant / seed / smoke / network | 1 of 1 / 0 / false / 0 | [cite: run_log.txt | phase 1 | line 2]; [cite: summary.json | smoke | value]; [cite: resolved_config.json | seed, network_calls | values] |

## Decision

**ADVANCE.** The pre-registered positive pattern executed exactly as
contracted: the pooled-slope specification is numerically feasible, and
per the contract's interpretation clause a pass "supports drafting a
separate outcome-analysis contract for this one common-slope
operationalization" — nothing more. Next acts: draft the outcome-analysis
contract through probe-plan (pooled-slope fit of d with the
equal-patient-weight estimator, patient-bootstrap intervals, and the
card's frozen sensitivity-limited-null classification), for fresh human
approval. That approval must answer the contract's standing open question:
whether one pooled HU-imbalance slope preserves enough of the
band-specific attribution question — a pooled slope cannot exhibit
opposite-signed imbalance effects in bands 2 and 3, so if band-specificity
is judged essential, the path is a redesigned band-specific specification,
not this one. Under the v2 contract itself nothing further may be read;
its stopping rule was honored and the 49 reserved cases and all observed d
values remain unread. Round 1: this decision summarizes
`interpretation.md`; no `evidence/decisions.md` entry is appended until
the cross-family review approves.
