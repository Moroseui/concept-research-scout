# Interpretation review — idea 045, probe contract v2

## 1. Citations resolve

I resolved every citation in `interpretation.md` against
`probes/045/results/results_v3/`, the explicitly cited v1 bundle, the import
receipt, the approval marker, and the governing contract.

- `results_v3.import.json`: `manifest_sha256` is
  `1e104c8b620b946ffe2d58be328067c2a9b786d0096a74736ed6676958baeed1`
  and `file_count` is 12.
- `resolved_config.json`: contract blob
  `5615afea1e2f8309745a2d6558bd9118e5e9f1f3`, contract version 2, seed 0,
  network calls 0, smoke false, and output directory
  `/tmp/p45v2/results_v3` all match. The blob matches the live contract and
  `HUMAN_APPROVED_PROBE`; the marker timestamp is
  2026-09-01T05:36:24.184335+00:00.
- `input_manifest.csv`: the audit and key-table hashes are respectively
  `35e896dfe2a5275a9fa8077e990dff96e72ce1ec0e5048079653556e1c7e2cd2`
  and `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c`;
  their total/selected row counts are 594/396 and 297/198.
- `summary.json`: status `POSITIVE_PATTERN`, contractual gate true, 198
  analysis rows, 99 unique cases, 297 excluded rows in 2 records, zero
  outcome values read, zero reserved cases accessed, and smoke false all
  match.
- `split_manifest.json`: 198 rows, 99 cases, frozen-before-outcome true,
  zero reserved cases, and hash
  `6446ad66fc9c5548e4a8ade415d2ec74291798e9da08c62c2fc0389461a96853`
  match. The cited v1 split manifest carries the identical hash.
- `exclusions.csv`: its two aggregate rows exclude 198 audit rows and 99
  key rows, both for `non_primary_band`, totaling 297.
- `run_log.txt`: phase 1 line 2 records `Variant 1/1` and seed 0; the final
  phase-4 line records exact start/end determinism-manifest agreement.
- `design_diagnostics.json`: all ten named gates are true; rank is 3;
  condition number is 20.222895326167112; singular values are
  14.089047615314039, 1.0066594185504498, and 0.6966879563028607; maximum
  leverage is 0.15486441040641785; pooled support is n=198, 29 distinct,
  IQR 4.0, range -28.0 to 18.0; band 2 is n=99, 17 distinct, IQR 2.0,
  q25/q75 -2.0/0.0; band 3 is n=99, 26 distinct, IQR 6.0, q25/q75
  -2.0/4.0; the top ten leverage rows span 9 patients; and pooled imbalance
  mean is -0.15909079349402225. All 99 leave-one-patient-out records have
  rank 3. Their condition-number range is 20.042406826639716 (deleting
  sub-stroke0094) to 20.325983967379745 (deleting sub-stroke0147), and
  their maximum-leverage range is 0.154871023519075 to
  0.18137690505955997, with the latter after deleting sub-stroke0147.
- `per_row_design.csv`: sub-stroke0109 band 3 has Q1/Q4 medians 30.0/58.0,
  imbalance -28.0, and leverage 0.15486441040641785; sub-stroke0183 band 2
  has imbalance 18.0 and leverage 0.07314570734779892; sub-stroke0147 band
  3 has imbalance -27.0.
- Historical `results_v2/design_diagnostics.json`: condition number
  38.889769743817595 and maximum leverage 0.26358236965333054 match.

The prior review's two blocking prose-only percentages have been removed.
No uncited quantitative claim or unresolved citation remains.

## 2. Claim bounds

The interpretation remains inside the outcome-blind design-feasibility
estimand and uses only the contract's pre-registered feasibility thresholds.
There is no tier-2 endpoint, vendor comparison, or anchor-exclusion issue in
this probe. The v1 values are framed as historical context, not a floor or a
new comparator run. No aggregation absent from the cited analysis artifacts
remains. Because the probe is deterministic, uncertainty is correctly handled
through the exhaustive 99-case leave-one-patient-out analysis rather than
seed-level variation.

The text repeatedly states that the pass does not establish an outcome
association, slope homogeneity, tissue-composition explanation, viability
measurement, or model use. `ADVANCE` is limited to drafting a separately
approved outcome-analysis contract, exactly as the governing contract allows.

## 3. Completeness without cherry-picking

I checked all ten gate booleans, both complete band-support summaries, pooled
support, all 99 leave-one-patient-out records and their extrema, the full
per-row leverage extrema, the top-ten patient count, the cited extreme rows,
the complete row accounting, and the v1 headline diagnostics. No omitted
stratum or deletion contradicts the feasibility pass.

The material complication is included: band 2 has only 17 distinct imbalance
values and IQR 2.0, versus 26 and 6.0 in band 3. The interpretation correctly
states that the pooled rule tolerates this compression rather than repairing
it, and that reintroducing band-specific slopes would restore the v1 design
problem.

## 4. Verdict separation

`Demonstrates`, `Suggests`, and `Does not establish` are separated correctly.
Exact gate outputs, row identities, and the exhaustive deletion sweep are
treated as demonstrations. The diagnosis of the v1 interaction pathology,
the meaning of compressed band-2 support, and centering's practical role are
clearly labeled as suggestions. Scientific association, measurement validity,
and model-use conclusions are expressly withheld. The result is called a
valid computational-feasibility positive, not a scientific positive.

## 5. Plain-language fidelity

There is no separate plain-language summary section. The opening bottom line
is a contract-scoped feasibility statement and does not upgrade the result
into a tissue-composition or final-infarct finding.

```json
{"verdict": "APPROVE"}
```
