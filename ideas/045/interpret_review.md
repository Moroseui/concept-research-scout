# Interpretation review — idea 045, probe contract v2

## 1. Citations resolve

I resolved the interpretation's citations against
`probes/045/results/results_v3/`, the explicitly cited historical v1 bundle,
the import receipt, the approval marker, and the governing contract.

- `results_v3.import.json`: `manifest_sha256` is
  `1e104c8b620b946ffe2d58be328067c2a9b786d0096a74736ed6676958baeed1`
  and `file_count` is 12.
- `resolved_config.json`: `contract_blob` is
  `5615afea1e2f8309745a2d6558bd9118e5e9f1f3`, `contract_version` is 2,
  `seed` and `network_calls` are 0, `smoke` is false, and `output_dir` is
  `/tmp/p45v2/results_v3`. The contract blob matches both the live contract's
  recomputed git blob and `HUMAN_APPROVED_PROBE`; the marker timestamp is
  2026-09-01T05:36:24.184335+00:00.
- `input_manifest.csv`: the audit and key-table hashes are respectively
  `35e896dfe2a5275a9fa8077e990dff96e72ce1ec0e5048079653556e1c7e2cd2`
  and `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c`;
  their total/selected counts are 594/396 and 297/198.
- `summary.json`: status is `POSITIVE_PATTERN` and
  `contractual_gate_satisfied` is true; analysis rows are 198, unique cases
  are 99, exclusion rows/records are 297/2, and outcome values read,
  reserved cases accessed, and smoke are 0, 0, and false.
- `split_manifest.json`: the split has 198 rows and 99 cases,
  `created_before_outcome_file_open` is true, and its SHA-256 is
  `6446ad66fc9c5548e4a8ade415d2ec74291798e9da08c62c2fc0389461a96853`.
  The explicitly cited v1 `split_manifest.json` carries the same hash.
- `exclusions.csv`: its two rows contain 198 audit exclusions and 99 key
  exclusions, both for `non_primary_band`, totaling 297.
- `run_log.txt`: phase 1 says `Variant 1/1` and seed 0; the final phase-4
  line says the start/end determinism manifests agree exactly.
- `design_diagnostics.json`: all ten named gates are true; rank is 3;
  condition number is 20.222895326167112; singular values are
  14.089047615314039, 1.0066594185504498, and 0.6966879563028607; maximum
  leverage is 0.15486441040641785; pooled support is n=198, 29 distinct,
  IQR 4.0, range -28.0 to 18.0; band 2 is n=99, 17 distinct, IQR 2.0,
  q25/q75 -2.0/0.0; band 3 is n=99, 26 distinct, IQR 6.0, q25/q75
  -2.0/4.0; the top ten leverage rows span 9 patients; pooled imbalance
  mean is -0.15909079349402225. All 99 leave-one-patient-out entries have
  rank 3; the condition range is 20.042406826639716 (sub-stroke0094) to
  20.325983967379745 (sub-stroke0147), and the maximum-leverage range is
  0.154871023519075 to 0.18137690505955997, with the maximum after deleting
  sub-stroke0147.
- `per_row_design.csv`: sub-stroke0109 band 3 has Q1/Q4 medians 30.0/58.0,
  imbalance -28.0, and leverage 0.15486441040641785; sub-stroke0183 band 2
  has imbalance 18.0 and leverage 0.07314570734779892; sub-stroke0147 band
  3 has imbalance -27.0.
- Historical `results_v2/design_diagnostics.json`: condition number is
  38.889769743817595 and maximum leverage is 0.26358236965333054.

All cited file values are transcription-exact. The blocking problem is not
a mistranscription: two additional percentages are calculated in the prose
rather than reported by an analysis artifact.

## 2. Claim bounds

The interpretation stays within the outcome-blind design-feasibility
estimand, uses the contract's frozen thresholds only for its primary
feasibility gates, and repeatedly excludes association, tissue-composition,
viability, and model-use claims. Tier-2, vendor, and anchor-exclusion rules
are not applicable to this probe. The deterministic uncertainty constraint
is handled correctly with the complete case-level leave-one-patient-out
sweep rather than seed-level uncertainty.

One issue is blocking under the explicit no-new-aggregation rule: the
`Suggests` section says the maximum-leverage row is “still 23% below the
bound” and the deletion maximum is “about 91% of the 0.20 bound.” Neither
percentage is present in the cited analysis files. Remove those percentage
calculations and report only the already-cited raw leverage values and frozen
0.20 bound. The same uncited 91% calculation also appears in `decision.md`,
but this review's permitted revision target is `interpretation.md` only.

## 3. Completeness without cherry-picking

I checked all ten gate booleans, both complete band-support summaries, pooled
support, all 99 leave-one-patient-out records, the full leverage extrema, the
top-ten patient count, the cited extreme rows, and the v1 headline
diagnostics. No omitted stratum or deletion contradicts the valid feasibility
pass. The interpretation appropriately carries forward the principal
complication: band 2 still has only 17 distinct imbalance values and IQR 2.0,
and the pooled rule tolerates rather than repairs that band-specific
compression.

## 4. Verdict separation

`Demonstrates`, `Suggests`, and `Does not establish` are otherwise separated
correctly. Exact gate outputs and the exhaustive deletion sweep are treated
as demonstrations; explanations of why v1 failed and how the reduced design
absorbs extreme rows remain suggestions; scientific association, measurement
validity, and model-use conclusions are expressly withheld. `ADVANCE` is
limited to drafting a separately approved outcome-analysis contract, exactly
as the governing contract permits.

## 5. Plain-language fidelity

There is no separate plain-language summary section. The opening bottom line
is a faithful contract-scoped feasibility statement and does not upgrade the
result into a tissue-composition or final-infarct finding.

```json
{"verdict": "REVISE", "blocking": ["Remove the two prose-only leverage percentages ('23% below the bound' and 'about 91% of the 0.20 bound'); they are new aggregations absent from the analysis files. Retain the cited raw leverage values and frozen bound instead."]}
```
