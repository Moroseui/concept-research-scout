# Interpretation — idea 004 contract-v2 reconstruction-sensitivity study

**Round:** interpret-build round 1. **Decision:** **ADVANCE** to cross-family
interpretation review. This is not an advance to a new probe and does not authorize
additional inference.

## Bottom line

The released v2 ClassFine checkpoint changes some named abnormality scores when the
same CT acquisition is supplied through a different, geometry-matched reconstruction.
The clearest physician-legible rung-1 sentence supported here is:

> **The model is using reconstruction-dependent image content when it produces some
> named chest-CT abnormality scores.**

That statement is deliberately narrower than the idea card's spatial-frequency
language. The natural pairs identify sensitivity to reconstruction-dependent image
content under the observed contrasts; they do not identify a particular frequency
band, noise statistic, anatomy, or pathology as the used signal.

The result is mixed rather than a single model-wide effect. Typical signed shifts are
small, but their direction and upper-tail magnitude depend on both head and
reconstruction contrast. For example, cardiomegaly under Br40f|Br60f has a median
sharper-minus-softer probability change of 0.00012290477752685547 with a patient-
cluster interval spanning zero, while its 95th percentile absolute change is
0.020362943410873413 (95% interval 0.01600102119147777 to
0.02387432016432283). [cite: analysis/tier1_bootstrap.csv |
stratum=Br40f|Br60f, head_name=Cardiomegaly, scale=probability,
statistic=median_signed | point] [cite: analysis/tier1_bootstrap.csv |
stratum=Br40f|Br60f, head_name=Cardiomegaly, scale=probability,
statistic=median_signed | ci95_lo] [cite: analysis/tier1_bootstrap.csv |
stratum=Br40f|Br60f, head_name=Cardiomegaly, scale=probability,
statistic=median_signed | ci95_hi] [cite:
analysis/tier1_bootstrap.csv | stratum=Br40f|Br60f,
head_name=Cardiomegaly, scale=probability, statistic=q95_abs |
point] [cite: analysis/tier1_bootstrap.csv | stratum=Br40f|Br60f,
head_name=Cardiomegaly, scale=probability, statistic=q95_abs | ci95_lo]
[cite: analysis/tier1_bootstrap.csv | stratum=Br40f|Br60f,
head_name=Cardiomegaly, scale=probability, statistic=q95_abs | ci95_hi]

The cross-family contrasts show larger tails for selected heads. Under Bl56f|Br40f,
cardiomegaly has a 95th-percentile absolute probability change of
0.038668327033519745 (95% interval 0.02182863108813755 to
0.05057968143373726), and pleural effusion has 0.03778819739818573
(0.025120437145233154 to 0.04392303764820094). [cite:
analysis/tier1_bootstrap.csv | stratum=Bl56f|Br40f,
head_name=Cardiomegaly, scale=probability, statistic=q95_abs |
point] [cite: analysis/tier1_bootstrap.csv | stratum=Bl56f|Br40f,
head_name=Cardiomegaly, scale=probability, statistic=q95_abs | ci95_lo]
[cite: analysis/tier1_bootstrap.csv | stratum=Bl56f|Br40f,
head_name=Cardiomegaly, scale=probability, statistic=q95_abs | ci95_hi]
[cite: analysis/tier1_bootstrap.csv |
stratum=Bl56f|Br40f, head_name=Pleural effusion, scale=probability,
statistic=q95_abs | point] [cite: analysis/tier1_bootstrap.csv |
stratum=Bl56f|Br40f, head_name=Pleural effusion, scale=probability,
statistic=q95_abs | ci95_lo] [cite: analysis/tier1_bootstrap.csv |
stratum=Bl56f|Br40f, head_name=Pleural effusion, scale=probability,
statistic=q95_abs | ci95_hi] Under Bl57d|Br36d, pleural
effusion shifts downward in the prespecified sharper-minus-softer direction: median
-0.005872622132301331 (95% interval -0.009120389819145203 to
-0.0018590092658996582), with a 95th-percentile absolute change of
0.0374683603644371 (0.02754848502576351 to 0.047468333207070765).
[cite: analysis/tier1_bootstrap.csv | stratum=Bl57d|Br36d,
head_name=Pleural effusion, scale=probability, statistic=median_signed |
point] [cite: analysis/tier1_bootstrap.csv | stratum=Bl57d|Br36d,
head_name=Pleural effusion, scale=probability, statistic=median_signed |
ci95_lo] [cite: analysis/tier1_bootstrap.csv | stratum=Bl57d|Br36d,
head_name=Pleural effusion, scale=probability, statistic=median_signed |
ci95_hi] [cite: analysis/tier1_bootstrap.csv |
stratum=Bl57d|Br36d, head_name=Pleural effusion, scale=probability,
statistic=q95_abs | point] [cite: analysis/tier1_bootstrap.csv |
stratum=Bl57d|Br36d, head_name=Pleural effusion, scale=probability,
statistic=q95_abs | ci95_lo] [cite: analysis/tier1_bootstrap.csv |
stratum=Bl57d|Br36d, head_name=Pleural effusion, scale=probability,
statistic=q95_abs | ci95_hi]

These are case-level estimates from a deterministic frozen-checkpoint procedure. The
relevant uncertainty is patient sampling, handled by the preregistered patient-
cluster bootstrap; training-seed uncertainty is not the limiting issue. The findings
remain specific to these pairs and a predominantly Siemens cohort.

## Strict contract interpretation

### Demonstrates

- The contracted execution completed validly: the frozen manifest was hash-matched,
  every planned chunk completed, all scientific volumes were scored, and the frozen
  two-tier analysis ran. The bundle records contract satisfaction, 425 pairs, 850
  unique scientific volumes, 17 completed chunks, and 5 sessions. [cite:
  summary.json | idea_id=idea-004 | contract_satisfied] [cite: summary.json |
  idea_id=idea-004 | pair_count] [cite: summary.json | idea_id=idea-004 |
  unique_volume_count] [cite: summary.json | idea_id=idea-004 |
  chunks_complete] [cite: summary.json | idea_id=idea-004 | sessions_used]
- The anchor-exposed pair was excluded from confirmatory analysis. The
  Br40f|Br60f stratum therefore contains 237 raw pairs and 236 counted pairs for
  each tier-1 cell. [cite: analysis/tier1_stats.csv |
  stratum=Br40f|Br60f, head_name=Medical material, scale=probability |
  n_raw] [cite: analysis/tier1_stats.csv | stratum=Br40f|Br60f,
  head_name=Medical material, scale=probability | n_counted]
- The deterministic protections passed. Across the recorded sessions, anchor A and
  B had maximum absolute deviation 0.0 from the v1 reference, and every within-
  session A repeat was bit-identical. [cite: anchor/anchor_log.csv |
  session_id=20260815T180544Z-f80be290, execution=anchor_A |
  max_abs_dev_vs_v1] [cite: anchor/anchor_log.csv |
  session_id=20260815T180544Z-f80be290, execution=anchor_A_repeat |
  within_session_bit_identical] [cite: anchor/anchor_log.csv |
  session_id=20260815T231124Z-8e185556, execution=anchor_A |
  max_abs_dev_vs_v1] [cite: anchor/anchor_log.csv |
  session_id=20260815T231124Z-8e185556, execution=anchor_A_repeat |
  within_session_bit_identical]
- The label-free primary result demonstrates contrast- and head-specific
  reconstruction sensitivity of this checkpoint. The paired changes are not merely
  unquantified score movements: their case-level distributions and patient-cluster
  intervals were computed on both prespecified scales. No cross-head average is
  used.

### Suggests

- The larger upper tails for cardiomegaly and pleural effusion in the two
  cross-family contrasts suggest those output scores are more reconstruction-
  sensitive under those particular composite kernel substitutions than under the
  within-family Br40f|Br60f substitution. This is a descriptive comparison across
  separately sampled strata, not a randomized comparison of kernel families.
- Directional medians suggest the response is structured rather than pure numerical
  jitter. For pleural effusion, the median is negative under both cross-family
  contrasts: -0.0017284750938415527 for Bl56f|Br40f and
  -0.005872622132301331 for Bl57d|Br36d, with both patient-cluster intervals below
  zero. [cite: analysis/tier1_bootstrap.csv | stratum=Bl56f|Br40f,
  head_name=Pleural effusion, scale=probability, statistic=median_signed |
  point] [cite: analysis/tier1_bootstrap.csv | stratum=Bl56f|Br40f,
  head_name=Pleural effusion, scale=probability, statistic=median_signed |
  ci95_lo] [cite: analysis/tier1_bootstrap.csv | stratum=Bl56f|Br40f,
  head_name=Pleural effusion, scale=probability, statistic=median_signed |
  ci95_hi] [cite: analysis/tier1_bootstrap.csv |
  stratum=Bl57d|Br36d, head_name=Pleural effusion, scale=probability,
  statistic=median_signed | point] [cite: analysis/tier1_bootstrap.csv |
  stratum=Bl57d|Br36d, head_name=Pleural effusion, scale=probability,
  statistic=median_signed | ci95_lo] [cite: analysis/tier1_bootstrap.csv |
  stratum=Bl57d|Br36d, head_name=Pleural effusion, scale=probability,
  statistic=median_signed | ci95_hi]
- Tier 2 suggests that reconstruction substitution can sometimes alter benchmark
  ranking. The clearest observed row is mosaic attenuation under Br40f|Br60f:
  delta-AUROC 0.01512226512226511 with patient-cluster interval
  0.0037551069454458356 to 0.027027027027026976. This is descriptive benchmark
  discrimination against report-derived labels only. [cite:
  analysis/tier2_auroc.csv | stratum=Br40f|Br60f,
  head_name=Mosaic attenuation pattern | delta_auroc] [cite:
  analysis/tier2_auroc.csv | stratum=Br40f|Br60f,
  head_name=Mosaic attenuation pattern | delta_auroc_ci95_lo] [cite:
  analysis/tier2_auroc.csv | stratum=Br40f|Br60f,
  head_name=Mosaic attenuation pattern | delta_auroc_ci95_hi]

### Does not establish

- It does not establish a universal measurement floor, reconstruction invariance,
  robustness outside the observed contrasts, or behavior across vendors or sites.
- It does not establish that the model uses a named anatomical or physiological
  feature. The study reaches rung 1. Measuring frequency-energy or noise-power
  properties and intervening on them independently would be needed to identify the
  card's more specific spatial-frequency X and approach rung 3.
- It does not establish accuracy, clinical diagnostic performance, clinical
  actionability, concept validity, localization, or a causal effect of any specific
  kernel property.
- It does not establish a pass/fail judgment for tier 2. No tier-2 result is compared
  with a threshold, cutoff, or margin; CT-Scroll remains context only.
- It does not support confirmatory interpretation of Br40f|Br44f. That authorized
  variant consists only of exploratory per-pair values; every tier-2 head in that
  stratum was excluded for insufficient labels. For example, Medical material has
  3 positive and 1 negative pair. [cite: analysis/tier2_excluded_cells.csv |
  stratum=Br40f|Br44f, head_name=Medical material |
  n_counted_pairs] [cite: analysis/tier2_excluded_cells.csv |
  stratum=Br40f|Br44f, head_name=Medical material | n_positive] [cite:
  analysis/tier2_excluded_cells.csv | stratum=Br40f|Br44f,
  head_name=Medical material | n_negative] [cite:
  analysis/tier2_excluded_cells.csv | stratum=Br40f|Br44f,
  head_name=Medical material | reason]

### Validity failures

None. The results bundle records `contract_satisfied: true`; provenance, manifest,
determinism, same-session pairing, environment, anchor, and budget gates passed.
[cite: summary.json | idea_id=idea-004 | contract_satisfied]

## Positive and negative findings

**Positive findings.** The operational positive pattern passed, and the scientific
readout is not uniformly zero: several head/contrast cells have directional median
intervals excluding zero and nontrivial upper tails. The strongest defensible claim
is a vendor-scoped reconstruction-sensitivity baseline for this released checkpoint,
not a general property of chest-CT models.

**Negative findings.** There is no contract-defined failing magnitude. Some common
contrast/head combinations are tightly centered: the Br40f|Br60f cardiomegaly
median interval spans zero even though its upper tail is measurable. Tier 2 is mostly
imprecise relative to its point estimates; a particularly clear example is
Bl57d|Br36d hiatal hernia, delta-AUROC -0.03541666666666665 with interval
-0.09483189655172417 to 0.000036764705882260435. This remains a descriptive result,
not evidence of equivalence or no effect. [cite: analysis/tier2_auroc.csv |
stratum=Bl57d|Br36d, head_name=Hiatal hernia | delta_auroc] [cite:
analysis/tier2_auroc.csv | stratum=Bl57d|Br36d,
head_name=Hiatal hernia | delta_auroc_ci95_lo] [cite:
analysis/tier2_auroc.csv | stratum=Bl57d|Br36d, head_name=Hiatal hernia |
delta_auroc_ci95_hi]

Tier-2 coverage is also incomplete by design: 48 cells were computed and 24 were
excluded under the frozen sparse-label rule. [cite: summary.json | idea_id=idea-004
| analysis.tier2_computed_cells] [cite: summary.json | idea_id=idea-004 |
analysis.tier2_excluded_cells] Exclusion is a data-
coverage finding, not a validity failure and not a negative scientific result.

## Next decision

**ADVANCE** to the required cross-family interpretation review. If ratified, append a
scoped result entry to `evidence/decisions.md` and update the idea's state without
authorizing further inference. A separate successor—not a silent extension of idea
004—would be required to identify which independently measurable spatial-frequency
or noise-texture quantity mediates the observed score changes.
