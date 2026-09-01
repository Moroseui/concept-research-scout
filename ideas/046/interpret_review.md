# Interpretation review — idea 046, contract v2, round 1

## 1. Citations resolve

I resolved every citation in `interpretation.md` against
`probes/046/results/results_v3/` and the adjacent import receipt. All
quantitative transcriptions are exact to the precision stated.

- `resolved_config.json`: contract blob
  `942e530737c90b666baa4c9985fd0329296ef140`, contract version 2, input
  SHA-256 `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c`,
  variants 1, GPU minutes 0, and `smoke=false`. The contract blob also
  equals the Git blob of the current contract and the value in
  `HUMAN_APPROVED_PROBE`.
- `environment.txt`: dependencies are exactly `Python standard library
  only`.
- `split_manifest.json`: `created_before_measurement=true`, 99 opened
  census cases, zero reserved cases accessed, and SHA-256
  `532b1060662957c88712e3fbc2f7f81bbcc427b2b6229827cac0939872a764cf`.
- `determinism_manifest_start.json` and
  `determinism_manifest_end.json`: both record 99 cases, 297 rows, the
  pinned input hash, seed 20260901, and `smoke=false`; the files are
  byte-identical.
- `input_manifest.csv`, row `input=per_patient.csv`: 297 rows, 99 cases,
  and the pinned SHA-256. I independently recomputed that SHA-256 on the
  source table and obtained the same value.
- `exclusions.csv`, all rows selected by `reason=non_primary_band`: 99
  rows, all with that reason, at source lines 2 through 296 in steps of
  three. `summary.json` independently reports 99 excluded rows.
- `summary.json`: status `CENSUS_COMPLETE`; primary metric
  `complete_finite_population_contribution_accounting`; primary metric
  pass true; 99 paired cases and per-case outputs; 99 signed-curve rows;
  100 absolute-Lorenz rows; 54 positive-mass rows; 99 exclusions; and
  zero reserved cases accessed.
- `census_summary.json`: additive residual
  `6.938893903907228e-18`, within-1e-12 true; direct gap
  `0.0550773631700778`; net contribution and signed denominator
  `0.055077363170077796`; positive mass `0.0706613032599503`; absolute
  mass `0.08624524334982282`; signs 54/6/39; ties 5/5. The derived
  negative total is exactly `-0.015583940089872504`.
- `census_summary.json`, fixed summaries: signed-head shares for k = 1,
  5, 10, 20 are respectively `0.12966704886255284`,
  `0.48163202301973784`, `0.7928912778985707`, and
  `1.0951142730999406`; absolute-mass shares are
  `0.08280710754594581`, `0.3075766362974946`,
  `0.5063509495830807`, and `0.7335301076368037`; positive-mass
  crossings are k=8 at `0.5305392350631275` and k=17 at
  `0.8076125481655062`.
- `census_summary.json`, v1 lineage guard: status
  `MATCHED_V1_DEFINITION_AUDIT`, `compared=true`, tie space
  `delta_before_division_by_99`, with observed and expected values equal
  for every recorded guard.
- `per_case_contributions.csv`: sub-stroke0153 is rank 1 at
  `0.007141719141395045`; sub-stroke0002 and sub-stroke0166 are ranks 2
  and 3 at `0.005930555633540115` and `0.004849834482535765`; the rank
  1–10 case order is exactly 0153, 0002, 0166, 0181, 0014, 0098, 0090,
  0114, 0025, 0136. The two most negative cases are 0137 at
  `-0.0029141878799591753` (rank 99) and 0183 at
  `-0.002031107751158429` (rank 98). Cases 0094, 0141, 0142, 0147,
  0163, and 0175 occupy ranks 55–60 and have both operands and the
  contribution exactly zero. For the post-hoc observation, all ten head
  cases have negative band-2 values and nine have positive band-3 values;
  case 0114 has band-3 value `-0.04584335824840224`.
- `signed_cumulative_curve.csv`: ranks 2 and 3 have fractions
  `0.2373438745527493` and `0.3253988249605888`; rank 54 is case 0079
  with cumulative `0.0706613032599503` and fraction
  `1.282946372028552`; ranks 55–60 are flat; rank 99 terminates at
  `0.055077363170077796` and fraction 1.0.
- `absolute_lorenz_curve.csv`: the explicit endpoints are (0,0) at rank
  0 and (1,1) at rank 99. `positive_mass_curve.csv` terminates at rank
  54, case 0079, share 1.0.
- `results_v3.import.json`: 15 files, manifest SHA-256
  `997914ac477909b4077c2fd0a18d3fbea3054e7df0cd058344422527aededd60`,
  import time `2026-09-01T22:53:56+00:00`, and null source commit.

I found no uncited quantitative scientific result. Repository-governance
identities such as approval, bundle, transaction, and historical-artifact
commits are explicitly separated as repo-level anchors rather than result
claims.

## 2. Claim bounds

The interpretation stays within contract v2's finite-population descriptive
scope. It assigns no diffuse/concentrated label, uncertainty estimate,
population inference, stable-carrier status, clinical meaning, biological
mechanism, or model-use claim. Its percentages are direct frozen summaries,
not unsupported aggregation. The signed share above 100% is correctly
explained as cancellation by the remaining negative contributions and is not
called a Lorenz share.

The task template's tier-2 threshold, vendor-scope, anchor-exclusion, and
baseline-versus-floor checks are inapplicable: this probe has no tier 2,
vendor comparison, anchor case, or performance baseline. The v1 audit is
correctly used only as a lineage guard. Because the probe is deterministic
and its estimand is the enumerated 99-case finite population, the
interpretation correctly avoids seed-level uncertainty and sharply limits
the exact findings to this table and estimator.

## 3. Completeness without cherry-picking

I checked every field of `summary.json` and `census_summary.json`, all 99
per-case rows, all 99 signed-curve rows, all 100 Lorenz rows, all 54
positive-mass rows, all 99 exclusions, and both determinism manifests. The
reported positive, zero, and negative counts exhaust the cohort; the head,
opposing tail, zero block, peak signed fraction, terminal values, every
frozen k, both target crossings, and all denominators are represented. The
Lorenz and positive-mass curves are monotone and reach their required
endpoints. I found no omitted stratum, subgroup, reversal, denominator issue,
or material table feature that contradicts the stated findings.

## 4. Verdict separation

`Demonstrates` is limited to exact census accounting, frozen shares, named
finite-population contributions, lineage continuity, and execution
discipline. The three additional row-level observations are correctly placed
under `Suggests` and labeled post hoc. `Does not establish` preserves all
material contract prohibitions. `CENSUS_COMPLETE` is correctly treated as a
successful descriptive output, not as a directional scientific verdict.

## 5. Plain-language fidelity

There is no separately labeled plain-language summary. The Layer A finding
serves the concise-summary role and is faithful to the cited tables: it keeps
the finite-population boundary, explains the greater-than-100% signed share,
and retains the explicit prohibition on diffuse/concentrated, stable-carrier,
clinical, and generalization claims.

```json
{"verdict": "APPROVE"}
```
