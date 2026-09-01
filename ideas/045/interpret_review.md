# Interpretation review — idea 045, probe contract v3, round 2

## 1. Citations resolve

I re-resolved every citation in the revised interpretation against the
committed result bundle, the named lineage artifacts, the approval marker,
and the governing contract. The three round-1 citation blockers are closed.

- `probes/045/results/results_v4.import.json`: manifest sha256
  `3bbdd2fd47917fd3305002276d346c045e7a75bb7e7a097d2b9afe74573c3b68`,
  file count 13, null source commit, and import time
  `2026-09-01T07:11:29+00:00` all match.
- `resolved_config.json`: contract blob
  `b1e283613d4fd47c77bfd1f2838a54791eb25954`, contract version 3,
  network calls 0, and output directory `/tmp/p45v3/results_v4` match.
- `ideas/045/HUMAN_APPROVED_PROBE`: approval time
  `2026-09-01T06:57:20.966365+00:00`, the same contract blob, and registry
  sha256 `1c0e82a68e184a30346228b5745525f50f5b86f938178401dc0d3829fe26a636`
  match. Direct `git hash-object` inspection also confirms that the current
  contract has the cited blob.
- `input_manifest.csv`: the audit and outcome sha256 values are respectively
  `35e896dfe2a5275a9fa8077e990dff96e72ce1ec0e5048079653556e1c7e2cd2`
  and `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c`;
  row accounting is 594 total/396 selected and 297 total/198 selected.
- `bootstrap_summary.json`: seed 20260901; 10,000 requested and completed;
  zero failures; all quoted point estimates and percentile intervals match.
  This includes both adjusted means, the adjusted gap, beta-HU, both
  adjustment changes, and the absolute-gap change.
- `summary.json`: status `DECISIVE_MEASURED_EXPLANATION_FAILURE`; adjusted
  band-2 mean -0.03133128471039588 with interval
  [-0.05589866048677166, -0.00789029340507566]; adjusted band-3 mean
  0.022404903919524183 with interval [0.0038892800799788215,
  0.043408163548312576]; `opposite_sign_precise: true`; beta-HU and its
  interval; unadjusted means; 198 rows; 99 cases; 297 exclusions; zero
  reserved cases accessed; one variant; and `smoke: false` all match.
- `run_log.txt`: phase-1 line 2 records the sole variant and seed; the final
  phase-4 line records exact start/end determinism-manifest agreement.
- `probes/045/verification.json`: `passed: true` and checked time
  `2026-09-01T07:10:41.507360+00:00` match.
- `split_manifest.json`: the split was created before outcome-file access;
  it has 198 rows, 99 cases, zero reserved cases, and sha256
  `6446ad66fc9c5548e4a8ade415d2ec74291798e9da08c62c2fc0389461a96853`.
  The cited `results_v3/split_manifest.json` carries the same split hash.
- `exclusions.csv`: 297 data rows are present and every row has reason
  `non_primary_band`.
- `probes/023/results/results_v2/per_stratum_summary.csv`: band-2 and band-3
  means exactly equal the quoted unadjusted means; their medians are
  -0.0005886681383370125 and 0.000556250836852953.
- `probes/023/results/results_v2/summary.json`: `reserved_case_count` is 49.
- `model_diagnostics.json`: all three coefficients, rank 3, maximum leverage
  0.15486441040641785, and pooled center -0.15909079349402225 match.
- `per_patient_attribution.csv`: there are 198 rows with the cited fitted,
  residual, and leverage fields. The HU-imbalance extrema are -28.0 and
  +18.0. The quoted sub-stroke0183 band-2 and sub-stroke0109 band-3 rows are
  transcription-exact. The revised prose now limits its interpretation to
  these two rows rather than asserting an unsupported cohort-wide outcome
  extremum comparison.
- `probes/045/results/results_v2/design_diagnostics.json`: the historical
  interaction-design condition number is 38.889769743817595, correctly
  rounded to 38.89 against the frozen threshold of 30.
- `ideas/045/probe_review.md`: the opening paragraph carries the cited
  `run.py` sha256 and APPROVE verdict.

The round-1 unsupported derived ratio and per-band mean-imbalance algebra
have been removed. I found no remaining unresolved citation,
mis-transcription, or uncited quantitative result.

## 2. Claim bounds

The primary conclusion remains bounded to the approved linear common-slope,
median-HU explanation. The interpretation explicitly does not infer no
association from the imprecise pooled slope, does not claim causation,
measurement validity, model use, or generalization, and does not claim that
tissue composition generally has been excluded. It also names the key model
limitation: opposite-signed HU effects by band were not estimable under this
specification.

The adjusted and unadjusted estimates are contract-declared scientific
outputs, not tier-2 context, and no prohibited external margin or baseline
floor is introduced. The historical condition-number threshold is used only
to explain why the earlier interaction specification stopped. Uncertainty is
correctly case-level: the deterministic point estimates are accompanied by
the contracted patient-cluster bootstrap, with no invented seed-level
uncertainty.

## 3. Completeness without cherry-picking

I checked both primary bands, every interval in `bootstrap_summary.json`, all
198 attribution rows, all 297 exclusion rows, the parent means and medians,
and the earlier interaction-design failure. No omitted primary stratum
reverses the reported decisive pattern.

The interpretation includes the material complications present in the
artifacts: beta-HU is imprecise; the common-slope model cannot test
band-antisymmetric effects; the interaction design failed its conditioning
gate; the parent medians are near zero despite nonzero means; severity is an
unadjusted common cause; and nonlinear, non-median, and spatial composition
effects remain untested. The two selected extreme-imbalance rows are now
explicitly presented as examples rather than as a complete cohort-wide
extremum result.

## 4. Verdict separation

`Demonstrates` is restricted to contract execution and reported outputs.
`Suggests` labels the structural and row-level readings as interpretation.
`Does not establish` contains the necessary exclusions and prevents the
measured-explanation failure from becoming a broad null. The proposed PAUSE
is a governance recommendation following the card's spent stopping rule, not
a new scientific finding.

## 5. Plain-language fidelity

There is no separate plain-language summary. The emphasized bottom line uses
the contract's permitted negative wording and is supported by the cited
adjusted band estimates and intervals; it does not upgrade the result beyond
failure of the measured median-HU explanation at achieved precision.

```json
{"verdict": "APPROVE"}
```
