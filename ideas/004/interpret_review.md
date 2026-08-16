# Interpret review — idea 004, contract v2 (cross-family checker, round 1)

**Artifact reviewed:** `ideas/004/interpretation.md` against the results bundle
`probes/004/results_v2/` and `ideas/004/probe_contract.yaml`. Role:
verification only; no findings of my own are added.

**Verdict: APPROVE.** Every citation resolves and is transcription-exact;
claim bounds hold; the tables contain no omitted feature that contradicts or
complicates a stated finding; demonstrates / suggests / does not establish are
used per their definitions.

## Check 1 — citations resolve

Every `[cite: ...]` tag was opened, the row selector applied, and the column
read. All values below were compared against the interpretation's prose at the
stated precision.

**summary.json** (idea_id=idea-004):

| Key | File value | Prose | Match |
|---|---|---|---|
| contract_satisfied | true | "contract satisfaction" / "contract_satisfied: true" | exact |
| pair_count | 425 | 425 pairs | exact |
| unique_volume_count | 850 | 850 unique scientific volumes | exact |
| chunks_complete | 17 | 17 completed chunks | exact |
| sessions_used | 5 | 5 sessions | exact |
| analysis.tier2_computed_cells | 48 | 48 cells computed | exact |
| analysis.tier2_excluded_cells | 24 | 24 excluded | exact |

**analysis/tier1_bootstrap.csv** (all probability scale):

| Row selector | point / ci95_lo / ci95_hi (file) | Match |
|---|---|---|
| Br40f\|Br60f, Cardiomegaly, median_signed | 0.00012290477752685547 / −0.0002377629280090332 / 0.0005306601524353027 | point exact; "interval spanning zero" correct (lo < 0 < hi) |
| Br40f\|Br60f, Cardiomegaly, q95_abs | 0.020362943410873413 / 0.01600102119147777 / 0.02387432016432283 | all three exact |
| Bl56f\|Br40f, Cardiomegaly, q95_abs | 0.038668327033519745 / 0.02182863108813755 / 0.05057968143373726 | all three exact |
| Bl56f\|Br40f, Pleural effusion, q95_abs | 0.03778819739818573 / 0.025120437145233154 / 0.04392303764820094 | all three exact |
| Bl56f\|Br40f, Pleural effusion, median_signed | −0.0017284750938415527 / −0.003324061632156372 / −0.0010435283184051514 | point exact; "interval below zero" correct (hi < 0) |
| Bl57d\|Br36d, Pleural effusion, median_signed | −0.005872622132301331 / −0.009120389819145203 / −0.0018590092658996582 | all three exact; interval below zero correct |
| Bl57d\|Br36d, Pleural effusion, q95_abs | 0.0374683603644371 / 0.02754848502576351 / 0.047468333207070765 | all three exact |

**analysis/tier1_stats.csv:** Br40f|Br60f, Medical material, probability →
n_raw 237, n_counted 236: exact. The generalization "for each tier-1 cell" was
verified against the full table: all 18 Br40f|Br60f rows on both the
probability and logit scales carry 237/236.

**anchor/anchor_log.csv:** session 20260815T180544Z-f80be290 anchor_A
max_abs_dev_vs_v1 = 0.0; anchor_A_repeat within_session_bit_identical = true;
session 20260815T231124Z-8e185556 likewise 0.0 / true. All four cited cells
exact.

**analysis/tier2_auroc.csv:** Br40f|Br60f, Mosaic attenuation pattern →
delta_auroc 0.01512226512226511, ci 0.0037551069454458356 to
0.027027027027026976: exact. Bl57d|Br36d, Hiatal hernia → delta_auroc
−0.03541666666666665, ci_lo −0.09483189655172417, ci_hi 3.6764705882260435e-05;
the prose's 0.000036764705882260435 is the exact decimal expansion of the
file's value.

**analysis/tier2_excluded_cells.csv:** Br40f|Br44f, Medical material →
n_counted_pairs 4, n_positive 3, n_negative 1, reason "insufficient labels for
AUROC": exact ("3 positive and 1 negative pair").

No unresolvable citation and no mis-transcription anywhere. No standalone
number in the prose lacks support: every transcribed value carries its own
cite. Three sentences make for-all claims cited by exemplar rows rather than
by every row ("anchor A and B had maximum absolute deviation 0.0" cites the
anchor_A rows only; "for each tier-1 cell"; "every tier-2 head in that stratum
was excluded"). I verified each universal against the complete table: both
anchor_B rows also record max_abs_dev_vs_v1 = 0.0 and in_tolerance = true;
all 36 tier-1 stats rows in Br40f|Br60f carry 237/236; all 18 Br40f|Br44f
tier-2 cells are excluded. All true; exemplar citation of a table-level claim
is accepted, not blocking.

## Check 2 — claim bounds

- **Tier-2 threshold language:** none. The only occurrences of
  threshold/cutoff/margin/pass-fail vocabulary are the meta-statements that no
  such comparison is made. No tier-2 quantity is compared to any number; the
  CT-Scroll context values are not invoked at all (permitted, since citing
  them is optional and for scale only).
- **Aggregation:** every quantity in the interpretation is a cell that exists
  in the analysis files. No cross-head average appears in any form. "Typical
  signed shifts are small" is a qualitative characterization consistent with
  the full table (largest |median_signed| on the probability scale is 0.0059,
  Bl57d|Br36d pleural effusion).
- **Vendor scope:** stated in the bottom line ("predominantly Siemens
  cohort"), in positive findings ("vendor-scoped"), and in does-not-establish
  (no cross-vendor/site behavior).
- **Anchor exclusion:** stated exactly where the counts appear (237 raw / 236
  counted, demonstrates bullet 2); the confirmatory examples all use
  counted-236 cells.
- **Baseline-not-floor:** respected — "does not establish a universal
  measurement floor" and "baseline ... not a general property of chest-CT
  models."
- **Uncertainty constraint for a deterministic probe:** applied correctly —
  the estimates are framed as case-level with patient-cluster bootstrap as the
  relevant uncertainty, and training-seed uncertainty explicitly set aside.

## Check 3 — completeness without cherry-picking

What I checked for, against the full tables:

- **Reversal of the "larger cross-family tails" pattern.** All four underlying
  comparisons hold in point estimate: cardiomegaly q95_abs 0.0204
  (Br40f|Br60f) vs 0.0387 (Bl56f|Br40f) and 0.0262 (Bl57d|Br36d); pleural
  effusion 0.0199 vs 0.0378 and 0.0375. The Bl57d|Br36d cardiomegaly interval
  (0.0221–0.0405) overlaps the within-family interval, but the interpretation
  already restricts this claim to a descriptive comparison across separately
  sampled strata, in "suggests". No omitted reversal.
- **Counterexamples to the directional-structure claim.** Pleural effusion's
  median is negative with its interval below zero in all three bootstrap
  strata (including Br40f|Br60f, uncited but consistent), and no head shows
  opposite-sign medians with intervals excluding zero in different strata. The
  stated "several head/contrast cells have directional median intervals
  excluding zero" understates the table: 36 of 54 probability-scale median
  cells exclude zero. Selectivity here is conservative, not favorable.
- **Tier-2 counter-features.** Exactly 1 of the 48 computed cells (mosaic
  attenuation, Br40f|Br60f) has a delta-AUROC interval excluding zero.
  "Mostly imprecise relative to its point estimates" and "the clearest
  observed row" are both accurate; "can sometimes alter benchmark ranking" is
  if anything understated by the table itself.
- **Session/anchor bookkeeping.** sessions_used is 5 while anchor_log.csv
  records 2 sessions. Resolved from the bundle: sessions/session_attempts.csv
  lists 5 phase-B attempts; the chunks' environment.json records show all 17
  chunks were scored in the two anchor-logged sessions (4 + 13), so the three
  unlogged attempts scored nothing (the exit-12 harness-fault attempts in the
  2026-08-15 ledger entry). "Across the recorded sessions" is therefore
  accurate, and every chunk-scoring session has full anchor coverage. Not a
  contradiction.
- **Exploratory stratum placement.** Br40f|Br44f is absent from tier1_stats
  and tier1_bootstrap and present only as 72 per-pair rows (4 pairs × 18
  heads) in tier1_differences; all 18 of its tier-2 cells are excluded.
  Matches "consists only of exploratory per-pair values" exactly.
- **Count arithmetic.** 48 computed + 24 excluded = 72 = 18 heads × 4 strata
  (excluded = 6 Bl57d|Br36d + 18 Br40f|Br44f); tier1_bootstrap_rows 324 =
  18 × 3 strata × 2 scales × 3 statistics; tier1_difference_rows 7650 =
  425 × 18; pair_manifest_sha256 in summary.json equals the contract pin. All
  consistent.

## Check 4 — verdict separation

- **Demonstrates** contains only execution validity (contract_satisfied and
  its gates) and nonzero head/contrast-specific sensitivity, which the
  confirmatory tier-1 cells with intervals excluding zero support. The
  bottom-line rung-1 sentence is deliberately narrower than the idea card's
  ("reconstruction-dependent image content", with the frequency-band
  attribution explicitly refused) — consistent with the card's prohibited
  conclusion 5 and the contract's claim discipline.
- **Suggests** holds the cross-stratum tail comparison (flagged as
  non-randomized), the directional-structure reading, and the tier-2 ranking
  observation — all correctly sub-confirmatory.
- **Does not establish** covers the universal floor, invariance, vendor/site
  generalization, anatomical attribution, accuracy/actionability, tier-2
  pass/fail, and Br40f|Br44f.
- Nothing exploratory is stated confirmatorily: Br40f|Br44f appears only
  inside "does not establish", and no tier-2 quantity is treated as
  confirmatory.

```json
{"verdict": "APPROVE"}
```
