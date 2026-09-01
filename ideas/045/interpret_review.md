# Interpretation review — idea 045, probe contract v1

## 1. Citations resolve

I resolved every citation against `probes/045/results/results_v2/` and checked
the following claims:

- `resolved_config.json`: `contract_blob` is
  `e7071541036a17f4a02ec264693209fec5c1337d`; `seed` is 0;
  `network_calls` is 0.
- `input_manifest.csv`: the two input SHA-256 values begin `35e896df…` and
  `1d01551c…`; their total/selected row counts are 594/396 and 297/198.
- `summary.json`: `outcome_values_read` is 0; status is
  `NEGATIVE_PATTERN`; `contractual_gate_satisfied` is false; `smoke` is
  false; `reserved_cases_accessed` is 0; `unique_cases` is 99; and
  `analysis_rows` is 198.
- `run_log.txt`: phase 1 records `Variant 1/1` and seed 0; the final phase-4
  line says the start/end determinism manifests agree exactly.
- `split_manifest.json`: `created_before_outcome_file_open` is true and the
  SHA-256 is `6446ad66fc9c5548e4a8ade415d2ec74291798e9da08c62c2fc0389461a96853`.
- `exclusions.csv`: the two aggregate records account for 198 and 99 rows,
  both as `non_primary_band`, for 297 excluded rows total.
- `design_diagnostics.json`: each band has 99 cases; the condition number is
  38.889769743817595; the four singular values are transcribed exactly; rank
  is 4; band 2 has 17 distinct values, IQR 2.0, quartiles -2.0/0.0, and range
  -16.0 to 18.0; band 3 has 26 distinct values, IQR 6.0, and range -28.0 to
  14.0; maximum leverage is 0.26358236965333054; leave-one-patient-out
  condition numbers range from 35.731034847011095 for sub-stroke0109 to
  43.82447067610057 for sub-stroke0183; all leave-one-out ranks are 4; the
  top-ten leverage rows span 9 patients; and the pooled imbalance mean is
  -0.15909079349402225.
- `per_row_design.csv`: sub-stroke0183, band 2 has Q1/Q4 medians 23.0/5.0,
  imbalance 18.0, and leverage 0.26358236965333054.

The cited values are transcription-exact. Three uncited or under-supported
quantitative statements are blocking under the stage's strict citation and
no-new-aggregation rules:

1. The opening identifies the import manifest as 12 files without a citation.
   Add a resolvable citation to the import receipt or remove the file count.
2. “4 of 9 gates fail” and the corresponding passed-gate count are derived by
   counting booleans; neither count is a reported analysis-file field. Enumerate
   the named gate results without a count, or cite a bundle field that reports
   the count.
3. The claim that the intercept norm is `sqrt(198) ≈ 14.07` is a new
   calculation from `analysis_rows`, not a value contained in the cited file.
   Remove that calculated number or cite a reported artifact value.

## 2. Claim bounds

The interpretation stays within the outcome-blind feasibility estimand, uses
the contract's frozen thresholds, and repeatedly prohibits any inference about
the HU-imbalance/outcome association, tissue composition, viability, or model
use. Tier-2, vendor, and anchor-exclusion constraints are not applicable to
this probe. The deterministic uncertainty rule is handled correctly: no
seed-level uncertainty is claimed, and the interpretation uses the complete
leave-one-patient-out diagnostic as case-level sensitivity evidence.

One claim-bound issue is blocking. In `Suggests`, “Simple outlier removal
cannot rescue this specification” and “the path forward is respecification,
not case exclusion” extend beyond the evidence. The bundle tests every
single-patient deletion, not arbitrary multi-patient case exclusion. Narrow
this to the demonstrated statement: removing the maximum-leverage patient
does not rescue conditioning, and no single-patient deletion reaches the
frozen condition-number bound. Do not rule out all case-exclusion strategies.

The statement that audit medians are “integer-quantized” is also not resolved
by its cited `band_support` fields. Either cite a bundle artifact/selector that
establishes this across the underlying values or describe only the reported
17-value support and 2.0-HU IQR.

## 3. Completeness without cherry-picking

I checked all nine gate booleans, both bands' complete support summaries, all
99 leave-one-patient-out entries, the maximum-leverage row, and the reported
top-ten patient count. The interpretation includes the material complications:
the design remains rank 4; band 3 passes distinct-value support while band 2
fails; both bands have nonzero IQR; leverage is not concentrated in fewer than
five patients; and every single-patient deletion preserves rank while failing
the condition-number bound. No material reversal or counterexample in the
bundle is omitted.

## 4. Verdict separation

`Demonstrates`, `Suggests`, and `Does not establish` are generally separated
correctly. The core feasibility negative is confirmatory only for the frozen
design question, while proposed transformations remain suggestions. The one
overbroad case-exclusion inference identified above must be narrowed; no new
scientific finding should be added.

## 5. Plain-language fidelity

There is no separate plain-language summary section. The opening bottom line
matches the cited technical verdict and does not upgrade it into a scientific
outcome claim.

```json
{"verdict": "REVISE", "blocking": ["Cite or remove the uncited 12-file import count; remove the derived 4-of-9/5-of-9 gate counts unless a bundle field explicitly reports them; and remove the derived sqrt(198) approximately 14.07 norm because the cited artifact reports only 198 analysis rows.", "Narrow the Suggests claim from all simple case exclusion to what the complete leave-one-patient-out analysis demonstrates: no single-patient deletion, including the maximum-leverage patient, restores the frozen conditioning gate.", "Cite an artifact and selector that establishes integer quantization of the underlying audit medians, or replace that characterization with the directly reported band-2 distinct-value count and IQR."]}
```
