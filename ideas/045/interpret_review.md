# Interpretation review — idea 045, probe contract v3

## 1. Citations resolve

I resolved the interpretation's citations against
`probes/045/results/results_v4/`, the cited idea-023 and idea-045 historical
bundles, the import receipt, the verification receipt, and the governing
contract.

- `resolved_config.json`: contract blob
  `b1e283613d4fd47c77bfd1f2838a54791eb25954`, contract version 3, network
  calls 0, output directory `/tmp/p45v3/results_v4`, and seed 20260901 all
  match.
- `input_manifest.csv`: the audit and outcome hashes are respectively
  `35e896dfe2a5275a9fa8077e990dff96e72ce1ec0e5048079653556e1c7e2cd2`
  and `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c`;
  row accounting is 594 total/396 selected and 297 total/198 selected.
- `bootstrap_summary.json`: seed 20260901; 10,000 requested and completed;
  zero failures; every quoted point estimate and interval matches. This
  includes the adjusted band means and gap, unadjusted band means and gap,
  both adjustment changes, absolute-gap change, and beta-HU interval.
- `summary.json`: status `DECISIVE_MEASURED_EXPLANATION_FAILURE`; adjusted
  band 2 -0.03133128471039588 with interval
  [-0.05589866048677166, -0.00789029340507566]; adjusted band 3
  0.022404903919524183 with interval [0.0038892800799788215,
  0.043408163548312576]; `opposite_sign_precise: true`; beta-HU and its
  interval; unadjusted means; 198 rows; 99 cases; 297 excluded rows and
  records; zero reserved cases accessed; one variant; and `smoke: false`
  all match.
- `run_log.txt`: phase-1 line 2 records the one approved variant and seed;
  the final phase-4 line records exact start/end determinism-manifest
  agreement.
- `probes/045/verification.json`: `passed: true` and checked time
  `2026-09-01T07:10:41.507360+00:00` match.
- `split_manifest.json`: 198 rows, 99 cases, frozen-before-outcome true,
  zero reserved cases accessed, and hash
  `6446ad66fc9c5548e4a8ade415d2ec74291798e9da08c62c2fc0389461a96853`
  match. The cited v2 feasibility split manifest has the same hash.
- `exclusions.csv`: 297 data rows are present and every reason is
  `non_primary_band`.
- `probes/023/results/results_v2/per_stratum_summary.csv`: band-2 and band-3
  means exactly equal the quoted unadjusted means; their medians are
  -0.0005886681383370125 and 0.000556250836852953.
- `model_diagnostics.json`: all three coefficients, rank 3, maximum leverage
  0.15486441040641785, and pooled center -0.15909079349402225 match.
- `per_patient_attribution.csv`: all 198 rows contain the cited fitted,
  residual, and leverage columns. The quoted sub-stroke0183 band-2 and
  sub-stroke0109 band-3 rows are transcription-exact.
- `probes/045/results/results_v2/design_diagnostics.json`: the historical
  condition number 38.889769743817595 matches.
- `probes/045/results/results_v4.import.json`: file count 13 matches.

Three citation defects are blocking under the stage's hard citation mandate:

1. The `Suggests` section derives a new relative statement — that the
   absolute-gap adjustment is “less than 0.006” of the approximately 0.054
   adjusted gap. Neither cited artifact contains that ratio. Remove it or
   add a governed analysis output that contains it; checker-side arithmetic
   cannot supply an analysis-file aggregation.
2. The same paragraph asserts that the two bands have nearly the same
   average HU imbalance and that their band-mean centered imbalances are
   equal and opposite. No cited result file reports either per-band mean
   imbalance. The algebra may be correct, but it is a new uncited
   aggregation. Remove this rationale or cite a governed output containing
   the two band means and the stated relationship.
3. The sentence “Extreme attenuation imbalance and extreme outcome contrast
   do not coincide in these data” generalizes from two cited rows. The cited
   selectors establish that those rows have the quoted values, but no cited
   artifact identifies the outcome extrema or reports a complete extremum
   comparison. Narrow the sentence to the two examples actually cited, or
   cite a governed summary that supports the cohort-wide claim.

There are also exact identity/count claims outside citation tags: the import
commit, import manifest hash and file count in the opening parenthesis; the
approval-marker timestamp; the recomputed `run.py` hash; and the statement
that 49 reserved cases remain untouched. Add formal `[cite: ...]` tags for
each exact claim or remove the exact values. A prose path in parentheses is
not a citation tag under this checker contract. The bundle establishes zero
reserved cases accessed, but does not establish the total of 49; that count
needs its own resolvable source.

## 2. Claim bounds

The principal result is bounded correctly to the approved common-slope,
median-HU explanation. The interpretation does not turn the imprecise
beta-HU slope into evidence of independence, does not claim causation,
measurement validity, model use, or generalization, and preserves the
opened-outcome/exploratory scope. The decisive status is the contract's
pre-registered primary classification, not tier-2 threshold language.

Uncertainty is handled at the patient level with the contracted clustered
bootstrap. No seed-level uncertainty is invented for this deterministic
fit. The parent reconstruction and v1 feasibility values are used as
identity/lineage context, not as post-hoc floors.

Subject to removing or sourcing the new aggregations identified in check 1,
the claim bounds are compliant.

## 3. Completeness without cherry-picking

I checked both primary bands, all reported bootstrap intervals, the complete
198-row attribution table, the full 297-row exclusion log, the parent means
and medians, and the historical v1 conditioning failure. The interpretation
includes the material complications: beta-HU is imprecise; the approved
common-slope model cannot test band-antisymmetric effects; the earlier
interaction specification failed its conditioning gate; the parent medians
are near zero despite nonzero means; severity remains an unadjusted common
cause; and nonlinear, non-median, and spatial composition effects remain
open.

No omitted reported stratum reverses the stated primary pattern. The only
completeness defect is the cohort-wide extrema sentence identified above:
two selected examples cannot establish the generalized comparison as
written.

## 4. Verdict separation

The `Demonstrates`, `Suggests`, and `Does not establish` sections otherwise
respect their roles. Contract outputs and the frozen classification appear
under demonstrations; mechanistic readings are labeled suggestions; and
the limitations explicitly prevent a measured-explanation failure from
becoming a broad tissue-composition or no-association claim. The proposed
`PAUSE` follows the card's stopping rule and is not presented as a new
scientific finding.

## 5. Plain-language fidelity

There is no separate plain-language summary section. The bold bottom line is
contract-scoped and is supported by the cited adjusted band estimates and
intervals. It does not upgrade the result beyond failure of the measured
median-HU explanation.

```json
{"verdict": "REVISE", "blocking": ["Remove or source the uncited derived ratio and per-band mean-imbalance algebra in Suggests item 1; the cited analysis files do not contain those aggregations.", "Narrow or source the cohort-wide extrema claim in Suggests item 3; two selected rows do not establish that extreme attenuation and outcome contrasts do not coincide across the data.", "Add formal resolvable citation tags for the exact import identity, approval timestamp, run.py hash, and 49-case reserved-count claims, or remove those exact claims."]}
```
