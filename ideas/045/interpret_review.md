# Interpretation review — idea 045, probe contract v1

## 1. Citations resolve

I resolved every citation in `interpretation.md` against
`probes/045/results/results_v2/` and the adjacent import receipt.

- `results_v2.import.json`: the import manifest SHA-256 is
  `004253540bab61d3b71714bcab06ea4304d1bbd0f1c1b12418f67dbf20e1bcd1`
  and `file_count` is 12.
- `resolved_config.json`: `contract_blob` is
  `e7071541036a17f4a02ec264693209fec5c1337d`; `seed` is 0; and
  `network_calls` is 0.
- `input_manifest.csv`: the two input hashes are
  `35e896dfe2a5275a9fa8077e990dff96e72ce1ec0e5048079653556e1c7e2cd2`
  and `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c`;
  total/selected row counts are 594/396 and 297/198.
- `summary.json`: status is `NEGATIVE_PATTERN`;
  `contractual_gate_satisfied` is false; `outcome_values_read` and
  `reserved_cases_accessed` are both 0; `smoke` is false; and the bundle
  reports 99 unique cases, 198 analysis rows, 297 excluded input rows, and
  2 exclusion records.
- `split_manifest.json`: `created_before_outcome_file_open` is true and the
  split SHA-256 is
  `6446ad66fc9c5548e4a8ade415d2ec74291798e9da08c62c2fc0389461a96853`.
- `exclusions.csv`: the two aggregate rows report 198 and 99 exclusions,
  both for `non_primary_band`, totaling 297.
- `run_log.txt`: phase 1 records `Variant 1/1` and seed 0; the final line
  states that the start and end determinism manifests agree exactly.
- `design_diagnostics.json`: rank is 4; condition number is
  38.889769743817595; the four singular values are transcribed exactly;
  band 2 has 99 cases, 17 distinct values, IQR 2.0, quartiles -2.0/0.0,
  and range -16.0 to 18.0; band 3 has 99 cases, 26 distinct values, IQR
  6.0, and range -28.0 to 14.0. Maximum leverage is
  0.26358236965333054; the top-ten rows span 9 patients; pooled imbalance
  mean is -0.15909079349402225; all leave-one-patient-out ranks are 4; and
  leave-one-patient-out condition numbers range from 35.731034847011095
  for `sub-stroke0109` to 43.82447067610057 for `sub-stroke0183`.
- `per_row_design.csv`: `sub-stroke0183`, band 2 has Q1/Q4 medians
  23.0/5.0, imbalance 18.0, and leverage 0.26358236965333054.

All cited quantitative statements are transcription-exact to their stated
precision. The round-1 blockers are resolved: the import file count now has
a source, the interpretation enumerates gate names rather than introducing
uncited gate counts, and the uncited intercept-norm calculation was removed.

## 2. Claim bounds

The interpretation remains inside the approved outcome-blind feasibility
estimand. It uses the contract's frozen thresholds only for the design audit
and repeatedly prohibits inference about the HU-imbalance/outcome
association, tissue composition, viability, or model use. Tier-2,
vendor-scope, anchor-exclusion, and baseline-floor constraints are not
applicable to this probe. Deterministic uncertainty is handled correctly:
no seed-level uncertainty is claimed, and the complete single-patient
deletion sweep is used only as case-level sensitivity evidence.

The revised `Suggests` section correctly limits the exclusion conclusion to
what was tested: no single-patient deletion, including deletion of the
maximum-leverage patient, restores the frozen conditioning gate. It
explicitly leaves multi-case exclusion untested. The earlier unsupported
integer-quantization characterization is also gone; the text now reports
only the bundle's distinct-value count and IQR.

## 3. Completeness without cherry-picking

I checked all nine gate booleans, both complete band-support summaries, all
99 leave-one-patient-out entries, the maximum-leverage row, and the
top-ten-patient count. The interpretation includes every material
complication: the matrix remains rank 4; band 3 passes distinct-value
support while band 2 fails; both bands have nonzero IQR; the highest-leverage
rows are not confined to fewer than five patients; and every
single-patient deletion preserves rank while failing the condition-number
bound. No table feature contradicting the stated feasibility verdict is
omitted.

## 4. Verdict separation

`Demonstrates`, `Suggests`, and `Does not establish` are used consistently.
The deterministic gate results and complete single-patient sensitivity
sweep appear as demonstrations; possible respecifications and explanations
of the diagnostic geometry remain suggestions; and the scientific
association, tissue-composition explanation, measurement validity, and
model-use claims are expressly withheld. No exploratory result is upgraded
to a confirmatory scientific finding.

## 5. Plain-language fidelity

There is no separate plain-language summary section. The opening bottom line
is a faithful restatement of the contract-scoped feasibility verdict and
does not turn it into a result about tissue composition or final infarction.

```json
{"verdict": "APPROVE"}
```
