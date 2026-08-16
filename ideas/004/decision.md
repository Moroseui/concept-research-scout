# Probe decision — idea 004 contract-v2 reconstruction-sensitivity study

**Date:** 2026-08-16
**Decision:** **ADVANCE** to cross-family interpretation review.

The deterministic, frozen-checkpoint study satisfied contract v2. It completed the
full manifest and both authorized analysis tiers with no validity failure. The
anchor-exposed pair remained excluded from confirmatory statistics. [cite:
summary.json | idea_id=idea-004 | contract_satisfied] [cite: summary.json |
idea_id=idea-004 | pair_count] [cite: summary.json | idea_id=idea-004 |
unique_volume_count] [cite: summary.json | idea_id=idea-004 | chunks_complete]

The primary label-free result demonstrates a reconstruction-sensitivity baseline for
the released v2 ClassFine checkpoint on the observed, predominantly Siemens CT-RATE
contrasts. The pattern is head- and contrast-specific: typical signed shifts are
small, while selected heads have measurable upper tails. For example, the
Bl56f|Br40f cardiomegaly 95th-percentile absolute probability change is
0.038668327033519745 with patient-cluster interval 0.02182863108813755 to
0.05057968143373726. [cite: analysis/tier1_bootstrap.csv |
stratum=Bl56f|Br40f, head_name=Cardiomegaly, scale=probability,
statistic=q95_abs | point] [cite: analysis/tier1_bootstrap.csv |
stratum=Bl56f|Br40f, head_name=Cardiomegaly, scale=probability,
statistic=q95_abs | ci95_lo] [cite: analysis/tier1_bootstrap.csv |
stratum=Bl56f|Br40f, head_name=Cardiomegaly, scale=probability,
statistic=q95_abs | ci95_hi]

The result does not establish a specific frequency band, anatomical cue, accuracy,
clinical reliability, concept validity, localization, cross-vendor generalization,
or a universal measurement floor. Tier 2 remains descriptive benchmark
discrimination against report-derived labels and carries no threshold, margin, or
pass/fail interpretation.

No additional inference is authorized. In interpret-build round 1,
`evidence/decisions.md` is intentionally unchanged pending review. The complete
strict interpretation is in `ideas/004/interpretation.md`.

**ADVANCE**
