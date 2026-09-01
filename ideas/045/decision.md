# Decision — idea 045, probe contract v1

## Result card

- **Idea:** idea-045 — "Did tissue composition create idea-023's sign reversal?"
- **Probe:** probes/045, contract v1 — outcome-blind design-matrix
  feasibility audit. First and only experiment in idea 045's sequence
  (parent experiments belong to idea-023); one authorized variant, one run.
- **Dataset:** two frozen derived tables from the imported idea-023 take-13
  Phase-C bundle (ISLES'24, Zenodo record 16813698 via the parent's
  provenance), pinned by sha256: `bin_tissue_audit.csv` `35e896df…`,
  `per_patient.csv` `1d01551c…` [cite: input_manifest.csv | both rows |
  sha256].
- **Primary metric:** singular-value condition number of the frozen
  four-column bands-2/3 design (intercept, band-3 indicator, centered
  HU imbalance, interaction), non-intercept columns unit-L2-scaled for the
  conditioning calculation only; frozen bound ≤ 30.
- **Contract blob:** `e7071541036a17f4a02ec264693209fec5c1337d`, matching
  the human approval marker of 2026-09-01T04:17:08Z and the bundle's
  `resolved_config.json`.
- **Results bundle:** `probes/045/results/results_v2/` at commit
  `fe7d30a3e88726d6ca4929a7badc3144f7338714` (import manifest sha256
  `004253540bab…`).
- **Families:** authoring family claude (this document and
  `interpretation.md`); reviewing family codex (cross-family citation
  review, round 1 pending).
- **Out-of-scope warnings — this result must NOT be read as:** evidence for
  or against an HU-imbalance/final-infarct association; evidence about
  whether tissue composition explains idea-023's band-2/band-3 reversal;
  validation of median NCCT attenuation as a tissue or viability
  measurement; a claim about any model's use of any signal; or a scientific
  negative for the parent lineage. It is a design-geometry feasibility
  verdict only, scoped to this frozen specification on these 99 cases.

## Layer A — Finding

The outcome-blind feasibility audit returned NEGATIVE_PATTERN: the frozen
band-by-imbalance interaction design fails 4 of its 9 pre-registered gates
[cite: summary.json | status, gates | values]. The design is full-rank but
ill-conditioned (condition number 38.89 vs the frozen ≤ 30 bound), band-2
exposure lands on only 17 distinct integer-quantized values (≥ 20 required),
one patient row exceeds the 0.20 leverage bound (0.2636), and no
single-patient deletion restores conditioning (leave-one-out range
35.73–43.82). Because the probe is deterministic and the leave-one-out sweep
covers case-level sensitivity, this failure is structural to the covariate
geometry, not seed noise or a single outlier. The most important caveat cuts
the other way from the usual one: zero outcome values were read, so the
result says nothing about idea 045's scientific question — it says the
current specification may not be used to ask it.

## Layer B — Derivation narrative

1. **Governance chain.** Contract v1 drafted at probe_plan 2026-08-31;
   claim-identity ruling of 2026-09-01 cleared the revised card; probe code
   passed cross-family review round 2 (APPROVE, `ideas/045/probe_review.md`,
   run.py sha256 `8d685dd4…`); harness self-check passed 2026-09-01T04:34Z
   (`probes/045/verification.json`); human approval 04:17Z bound blob
   `e7071541…`; run executed 04:38:58Z [cite: environment.txt |
   captured_utc | value]; bundle validated and imported via the
   record-result gate at commit `fe7d30a` (after two importer-side
   interface fixes, S2/S2b, resolved system-side without touching the
   bundle); ledger scrutiny advanced to PROBED.
2. **Flow of rows (CONSORT-style).** In: 594 audit rows and 297 key rows
   [cite: input_manifest.csv | both rows | total_rows]. Excluded: 297 rows
   in 2 records, all reason `non_primary_band` — 198 audit band-1 rows, 99
   per-patient band-1 rows [cite: exclusions.csv | case_id=* | count].
   Selected: 396 audit rows, 198 key rows → joined into 198 analysis rows,
   99 unique cases, 99 per band [cite: summary.json | analysis_rows,
   unique_cases | values]. Reserved cases touched: 0; outcome values read: 0
   [cite: summary.json | reserved_cases_accessed, outcome_values_read |
   values]. The split manifest (hash `6446ad66…`) was frozen before the
   outcome file was opened [cite: split_manifest.json |
   created_before_outcome_file_open | value].
3. **Gates.** Integrity and join gates all passed. Of the 9 feasibility
   gates: 5 passed (rank 4; 99 cases per band; nonzero IQR both bands;
   top-10 leverage rows span 9 patients; all 99 leave-one-out matrices rank
   4) and 4 failed (condition number; band-2 distinct values; maximum
   leverage; leave-one-out conditioning) [cite: design_diagnostics.json |
   gates | all keys]. Per the frozen stopping rule the run stopped after the
   single design audit; no outcome analysis began.
4. **Kill conditions approached.** None. No invalidating-failure clause
   fired; determinism manifests agreed exactly [cite: run_log.txt | phase 4
   | final line]. This is a valid pre-registered negative, not a failure
   reinterpreted as one.

## Layer C — Claims table

Bundle root: `probes/045/results/results_v2/` at commit
`fe7d30a3e88726d6ca4929a7badc3144f7338714`.

| Claim | Value | Source |
|---|---|---|
| Status | NEGATIVE_PATTERN | [cite: summary.json | status | value] |
| Contractual gate satisfied | false | [cite: summary.json | contractual_gate_satisfied | value] |
| Condition number (primary metric) | 38.889769743817595 | [cite: summary.json | primary_metric_value | value]; [cite: design_diagnostics.json | condition_number | value] |
| Singular values | 14.089212872412212, 1.3669879902028013, 0.7029747087392549, 0.36228583931515845 | [cite: design_diagnostics.json | singular_values | list] |
| Rank | 4 | [cite: design_diagnostics.json | rank | value] |
| Band-2 distinct imbalance values | 17 | [cite: design_diagnostics.json | band_support.2 | distinct_values] |
| Band-3 distinct imbalance values | 26 | [cite: design_diagnostics.json | band_support.3 | distinct_values] |
| Band-2 IQR / range | 2.0 / −16.0 to +18.0 | [cite: design_diagnostics.json | band_support.2 | iqr, minimum, maximum] |
| Band-3 IQR / range | 6.0 / −28.0 to +14.0 | [cite: design_diagnostics.json | band_support.3 | iqr, minimum, maximum] |
| Maximum row leverage | 0.26358236965333054 | [cite: design_diagnostics.json | maximum_row_leverage | value] |
| Max-leverage row identity | sub-stroke0183, band 2, imbalance +18.0 (Q1 23.0, Q4 5.0) | [cite: per_row_design.csv | case_id=sub-stroke0183, stratum=2 | hu_imbalance, q1_median_hu, q4_median_hu, leverage] |
| Leave-one-out condition min / max | 35.731034847011095 (sub-stroke0109) / 43.82447067610057 (sub-stroke0183) | [cite: design_diagnostics.json | leave_one_patient_out_condition_min, leave_one_patient_out_condition_max | value; per-case rows in leave_one_patient_out] |
| Leave-one-out entries / all rank 4 | 99 / true | [cite: design_diagnostics.json | leave_one_patient_out | count; gates.all_loo_rank_4] |
| Top-10 leverage rows, distinct patients | 9 | [cite: design_diagnostics.json | top_10_distinct_patients | value] |
| Pooled HU-imbalance mean (centering) | −0.15909079349402225 | [cite: design_diagnostics.json | pooled_hu_imbalance_mean | value] |
| Analysis rows / unique cases | 198 / 99 | [cite: summary.json | analysis_rows, unique_cases | values] |
| Input row accounting | audit 594→396; keys 297→198; 297 excluded (2 records) | [cite: input_manifest.csv | both rows | total_rows, selected_rows]; [cite: summary.json | excluded_input_rows, exclusion_records | values]; [cite: exclusions.csv | case_id=* | count] |
| Outcome values read / reserved cases accessed | 0 / 0 | [cite: summary.json | outcome_values_read, reserved_cases_accessed | values] |
| Split frozen before outcome access | true; hash 6446ad66… | [cite: split_manifest.json | created_before_outcome_file_open, sha256 | values] |
| Input pins | bin_tissue_audit.csv 35e896df…; per_patient.csv 1d01551c… | [cite: input_manifest.csv | both rows | sha256] |
| Governing contract blob | e7071541036a17f4a02ec264693209fec5c1337d | [cite: resolved_config.json | contract_blob | value] |
| Variant / seed / smoke / network | 1 of 1 / 0 / false / 0 | [cite: run_log.txt | phase 1 | line 2]; [cite: summary.json | smoke | value]; [cite: resolved_config.json | seed, network_calls | values] |

## Decision

**REVISE.** The pre-registered negative pattern executed exactly as
contracted: a decisive feasibility negative for the current linear
interaction specification, mandating specification revision before any
outcome value is read. The idea's scientific question is untouched — the
probe was outcome-blind, so its geometry (band-2 quantization, the
leverage/conditioning tension around sub-stroke0183, the intercept-scaling
convention) can inform a revised, re-frozen specification without
contaminating the future analysis. Next acts: draft a revised specification
(candidates: standardized or rank-transformed exposure, pooled-slope
reduction, or coarsened exposure bins) through probe-plan with fresh frozen
thresholds and a new human approval; the 49 reserved cases and all observed
d values remain unread. Round 1: this decision summarizes
`interpretation.md`, which awaits cross-family review; no
`evidence/decisions.md` entry is appended in this round.
