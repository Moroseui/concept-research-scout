# Interpretation — idea 045, probe contract v1 (outcome-blind design-matrix feasibility)

Results bundle: `probes/045/results/results_v2/`, imported at commit
`fe7d30a3e88726d6ca4929a7badc3144f7338714` (import receipt
`probes/045/results/results_v2.import.json`, byte-manifest sha256
`004253540bab61d3b71714bcab06ea4304d1bbd0f1c1b12418f67dbf20e1bcd1`, 12 files).
All citations below are relative to that bundle root at that commit.

Governing identity: contract blob `e7071541036a17f4a02ec264693209fec5c1337d`
[cite: resolved_config.json | contract_blob | value], matching the human
approval marker of 2026-09-01T04:17:08Z (`ideas/045/HUMAN_APPROVED_PROBE`) and
the current `ideas/045/probe_contract.yaml` byte-for-byte. Inputs are the two
frozen tables of the imported idea-023 take-13 bundle, identity-pinned:
`bin_tissue_audit.csv` sha256 `35e896df…` and `per_patient.csv` sha256
`1d01551c…` [cite: input_manifest.csv | path=…bin_tissue_audit.csv, …per_patient.csv | sha256].

The probe is fully deterministic (no training, no sampling, no bootstrap;
`randomness: None` in the contract; seed recorded as 0 and unused for any
draw [cite: resolved_config.json | seed | value]). The seed-count rule for
stochastic procedures therefore does not apply; case-level sensitivity is
covered inside the probe by the contract's own leave-one-patient-out
diagnostic. Effect-size language about the scientific question does not arise:
zero outcome values were read [cite: summary.json | outcome_values_read | value].

Bottom line, in the contract's own permitted vocabulary: **the frozen
bands-2/3 attenuation-imbalance design is NOT sufficiently conditioned and
distributed across patients for the prespecified linear interaction
analysis.** Status `NEGATIVE_PATTERN`, `contractual_gate_satisfied: false`
[cite: summary.json | status, contractual_gate_satisfied | value].

---

## Demonstrates

Deterministic computations on frozen, hash-pinned inputs; each is exact, not
an estimate.

1. **The probe executed validly end to end under its contract.** One variant
   of a maximum of one ran (`Variant 1/1`, seed 0) [cite: run_log.txt |
   phase 1 | line 2]; the start and end determinism manifests agree exactly
   [cite: run_log.txt | phase 4 | final line]; no network calls were
   authorized or configured [cite: resolved_config.json | network_calls |
   value]; smoke mode was off [cite: summary.json | smoke | value].

2. **Outcome blindness held.** Zero observed `d` values were parsed or
   retained [cite: summary.json | outcome_values_read | value]; the 198-row
   split was frozen before the outcome file was first opened
   [cite: split_manifest.json | created_before_outcome_file_open | value],
   with split hash `6446ad66…` [cite: split_manifest.json | sha256 | value];
   zero reserved cases were accessed [cite: summary.json |
   reserved_cases_accessed | value].

3. **All join and integrity gates passed.** Exactly 99 unique cases
   [cite: summary.json | unique_cases | value], 99 per primary band
   [cite: design_diagnostics.json | band_support.2, band_support.3 | n], one
   Q1 and one Q4 audit row and one key row per case-band, all derived values
   finite (no value-failure exit occurred; the run reached phase 4). Row
   accounting is complete and reconstructible: audit 594 total rows → 396
   selected; keys 297 → 198 selected [cite: input_manifest.csv | both rows |
   total_rows, selected_rows]; 297 rows excluded in 2 records, all with
   reason `non_primary_band` (198 audit band-1 rows, 99 per-patient band-1
   rows) [cite: exclusions.csv | case_id=* | count]; 198 analysis rows
   [cite: summary.json | analysis_rows | value].

4. **The frozen design is algebraically estimable but fails the frozen
   feasibility conjunction: 4 of 9 gates fail** [cite:
   design_diagnostics.json | gates | all keys]:
   - **Conditioning fails.** Primary condition number **38.889769743817595**
     against the frozen ≤ 30 bound [cite: design_diagnostics.json |
     condition_number | value]; singular values 14.089212872412212,
     1.3669879902028013, 0.7029747087392549, 0.36228583931515845
     [cite: design_diagnostics.json | singular_values | list]. Rank is 4, so
     the model is estimable in the strict algebraic sense
     [cite: design_diagnostics.json | rank | value] — the failure is
     conditioning, not rank.
   - **Band-2 exposure variation fails.** 17 distinct HU-imbalance values in
     band 2 against the frozen ≥ 20 bound; band 3 passes with 26
     [cite: design_diagnostics.json | band_support.2, band_support.3 |
     distinct_values]. Band-2 support is compressed: IQR 2.0 HU (q25 −2.0,
     q75 0.0), range −16.0 to +18.0; band 3: IQR 6.0, range −28.0 to +14.0
     [cite: design_diagnostics.json | band_support.2, band_support.3 |
     iqr, q25, q75, minimum, maximum].
   - **Leverage fails.** Maximum row leverage **0.26358236965333054** against
     the frozen ≤ 0.20 bound [cite: design_diagnostics.json |
     maximum_row_leverage | value], at case sub-stroke0183, band 2, whose
     HU imbalance is +18.0 (Q1 median 23.0 HU, Q4 median 5.0 HU)
     [cite: per_row_design.csv | case_id=sub-stroke0183, stratum=2 |
     hu_imbalance, q1_median_hu, q4_median_hu, leverage].
   - **Leave-one-patient-out conditioning fails everywhere.** Across all 99
     single-patient deletions the condition number ranges from
     35.731034847011095 (deleting sub-stroke0109) to 43.82447067610057
     (deleting sub-stroke0183) [cite: design_diagnostics.json |
     leave_one_patient_out_condition_min, leave_one_patient_out_condition_max
     | value]; no deletion reaches the ≤ 30 bound, while every deletion
     preserves rank 4 [cite: design_diagnostics.json | gates |
     all_loo_rank_4].

5. **The passed gates are real and worth recording:** rank 4 including all 99
   deletions; exactly 99 cases per band; nonzero IQR in both bands; the ten
   highest-leverage rows span 9 distinct patients (≥ 5 required)
   [cite: design_diagnostics.json | top_10_distinct_patients | value]. The
   design is not degenerate and not dominated by a tiny patient clique; it is
   ill-conditioned and, in band 2, too coarsely supported.

Because every number above is a deterministic function of the two pinned
input files, and the leave-one-patient-out sweep bounds single-case
sensitivity, the feasibility failure is **structural to the observed
covariate geometry, not an artifact of one patient**: that is demonstrated,
not suggested.

## Suggests

Inferences beyond the frozen gates; deterministic numbers, interpretive
step mine.

1. **Simple outlier removal cannot rescue this specification.** The row that
   breaches the leverage bound (sub-stroke0183, band 2) is also the deletion
   that *worsens* conditioning most (43.82 vs baseline 38.89) [cite:
   design_diagnostics.json | leave_one_patient_out | case_id=sub-stroke0183],
   because band-2 exposure spread collapses further without it. The two
   failed distribution gates pull opposite directions for any drop-the-case
   repair; the path forward is respecification, not case exclusion.

2. **Band-2 quantization is the binding constraint on variation.** The audit
   medians are integer-quantized HU values, and band 2's 99 imbalances land
   on only 17 distinct values with IQR 2.0 [cite: design_diagnostics.json |
   band_support.2 | distinct_values, iqr]. Any revised specification that
   keeps raw band-2 differences as the exposure inherits this grid; a
   coarsened, standardized, or rank-based exposure treatment is the natural
   family to consider.

3. **The condition-number magnitude partly reflects the frozen diagnostic
   convention.** Under the contract's scaling, non-intercept columns are
   unit-L2-normalized while the intercept retains norm √198 ≈ 14.07 (derived
   from the 198 analysis rows [cite: summary.json | analysis_rows | value]);
   the leading singular value is 14.0892 [cite: design_diagnostics.json |
   singular_values | first]. The trailing singular value 0.3623 — near-
   collinearity of the interaction column with its parents given compressed
   band-2 support — is the substantive signal. This observation does not
   soften the verdict (the gate was frozen before inspection, exactly so it
   could not be relitigated afterward); it informs how a successor
   specification should choose and justify its own conditioning diagnostic.

4. **Centering was nearly inert.** The pooled HU-imbalance mean is
   −0.15909079349402225 [cite: design_diagnostics.json |
   pooled_hu_imbalance_mean | value], so the failure is not a centering
   artifact; standardization or transformation, not re-centering, is the
   live lever.

## Does not establish

- **Anything about the association between HU imbalance and final-infarct
  contrast d.** Zero d values were read [cite: summary.json |
  outcome_values_read | value]; no slope, no adjusted contrast, no direction
  exists anywhere in this bundle.
- **Anything about whether tissue composition explains, contributes to, or
  fails to explain idea-023's band-2/band-3 reversal.** The contract's own
  negative_pattern language governs: this outcome "is not evidence against
  tissue composition or the parent association."
- **Anything about median NCCT attenuation as a viability or tissue-type
  measurement**, or about any model's use of any signal.
- **That no attribution analysis is feasible.** The verdict is scoped to the
  current frozen linear interaction specification on this exposure geometry.
  Whether a revised, re-frozen specification passes its own gates is an open
  empirical question the probe explicitly does not answer.

## Validity failures

None. No invalidating-failure clause fired: no outcome-access breach (0
values read), no input-identity failure (both sha256 pins recorded and
matching the feasibility memo), no join failure (99/99 per band, no
duplicates, no reserved case encountered), no nonfinite value, no analysis
deviation (one variant, band 1 excluded, thresholds byte-identical to the
approved contract per the in-run literal-drift guard), no missing required
output (all seven contract-required artifacts present, plus determinism and
split manifests and `exclusions.csv`). This is a **valid negative**, not an
invalid run reinterpreted as one.

## Findings, stated positively and negatively

- **Positive findings:** the machinery works — identity pinning, outcome
  blindness, bidirectional join gating, complete row accounting, and exact
  determinism all held on real inputs; the design is full-rank with 99
  patients per band and influence spread across ≥ 9 patients in the top-10
  leverage rows.
- **Negative finding (the result):** the frozen feasibility conjunction
  fails on 4 of 9 gates — conditioning (38.89 > 30), band-2 distinct-value
  support (17 < 20), maximum leverage (0.2636 > 0.20), and
  leave-one-patient-out conditioning (min 35.73 > 30). Under the contract's
  pre-registered classification this is a **decisive feasibility negative
  for the current linear interaction specification** — decisive for the
  design question the probe asked, and only for it. It mandates
  specification revision before any outcome value may be read.

## Authorized variants

One variant was authorized (`maximum_variants: 1`) and exactly one was run:
the approved real-input design audit, seed 0, smoke off [cite: run_log.txt |
phase 1 | line 2; cite: summary.json | smoke | value]. No other variant,
seed, threshold, or transform was executed. (The separate
`probes/045/verification.json` receipt records the pre-approval harness
self-check of 2026-09-01T04:34:21Z on synthetic data; it is a code-review
artifact, not a scientific variant.)

## Next decision

**REVISE.** The contract's negative_pattern prescribes it: the current
specification "requires revision before any outcome analysis." Concretely:

1. Draft a revised, pre-registered specification informed by this bundle's
   geometry — the candidate family consistent with the record: standardized
   or rank-transformed exposure, a pooled-slope (no-interaction) reduction,
   or coarsened exposure bins — each with its own re-frozen feasibility
   thresholds and diagnostic convention, through probe-plan and a fresh
   human approval.
2. Because this probe was outcome-blind (0 d values read), using its
   geometry to redesign the specification contaminates nothing: the
   scientific analysis remains unread and the 49 reserved cases untouched.
3. Do not read any outcome value under the current contract; its stopping
   rule has been honored and its authority is spent.

The scientific question of idea 045 — whether attenuation imbalance accounts
for the parent reversal — is neither supported nor weakened by this result.
The cheap, decision-grade attribution analysis the critique and debate
converged on is still worth buying; it needs a better-conditioned
specification first.
