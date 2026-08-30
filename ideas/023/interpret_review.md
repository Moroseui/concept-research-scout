# Interpretation review — idea 023, round 1

## 1. Citations resolve

I resolved every citation in `interpretation.md` against
`probes/023/results/results_v2/` (and the approval marker where applicable).
The following citations are transcription-exact:

- `run_log.txt`, line 1: Phase-C approval passed on contract blob
  `03d4545fe293f0067c69ce9e9e696ec97b894d7b`.
- `summary.json`: `archive_md5`, `zenodo_checksum`,
  `simulation_output_sha256`, `released_case_count`, `g_label_passed`,
  `status`, `identity_mad` for strata 1–3,
  `excluded_source_corrupt_cases`, `excluded_duplicate_lesion_members`,
  `analyzed_census_case_count`, `census_case_count`,
  `bin_tissue_audit_rows`, `reserved_case_count`, and
  `split_manifest_sha256`.
- `determinism_manifest_start.json`:
  `input_paths.phase_s_csv.sha256`; it is
  `59069fa92399cd5c600c89e0d66bb4c7c12679e14f12824b54ae0ce6a6061ef4`.
  The start and end determinism manifests are byte-identical as stated.
- `per_stratum_summary.csv`, strata 1–3: `patients`, `mean_d`, `ci_low`,
  `ci_high`, `ci_width`, `median_d`, `median_ci_low`, and
  `median_ci_high`. All displayed full-precision values match.
- `resolved_config.json`: minimum 20 contributing patients per stratum,
  minimum 100 voxels per patient-quantile cell, maximum primary CI width
  0.15, and seed 20260824.
- `identity_residual_summary.csv`, strata 1–3:
  `median_absolute_centered_residual` values 0.0077610015869140625,
  0.003559589385986328, and 0.0077877044677734375.
- `exclusions.csv`: sub-stroke0043 is an `excluded_case` for
  `source_corrupt_member`; sub-stroke0142 is an
  `excluded_archive_lesion` while the follow-up derivative is retained;
  sub-stroke0113 has 302261 nonfinite MTT voxels; and sub-stroke0002 has
  `vessel_cbv_p98` 29.140625.
- `per_patient.csv`: sub-stroke0002, stratum 1 has
  `d = -0.20385563685311792`.
- `bin_tissue_audit.csv`: all cited example rows resolve exactly:
  sub-stroke0092 stratum 1 Q1/Q4 medians 3.0/23.0;
  sub-stroke0057 stratum 1 5.0/24.0; sub-stroke0189 stratum 1 6.0/25.0;
  sub-stroke0002 stratum 2 21.0/21.0; sub-stroke0183 stratum 2 23.0/5.0;
  sub-stroke0109 stratum 3 30.0/58.0; and sub-stroke0133 stratum 3 Q4
  `iqr_hu = 314.5`.

The approval marker also binds the stated contract blob and timestamp.

## 2. Claim bounds

The primary gate language matches the contract: the result is
`NEGATIVE_PATTERN`, support and precision pass, and directional consistency
fails because the two zero-excluding intervals have opposite signs. The text
correctly scopes uncertainty to patients rather than seeds, states the
icobrain-cva/vendor and 99-patient limits, preserves the reserved 49 cases,
does not claim model use, and keeps autoregulatory, causal, and CBV-versus-MTT
claims out of scope. There is no tier-2 threshold issue in this probe, no
anchor population, and no baseline is incorrectly promoted to a floor.

**Blocking:** the HU and tail descriptions introduce aggregations that no
claim-bearing analysis file contains. In particular, “in most cases,”
“often by 10–20 HU,” “near-balanced in most cases (typical median difference
<= 2 HU),” “Q4 cells often show very wide HU spread,” and “the band-level
means are carried by a minority of patients” are cohort-level frequency or
contribution claims inferred by the author from row-level tables. The
interpretation itself acknowledges that no aggregate HU statistic exists.
The stage rule forbids creating an aggregation in prose that the analysis
files do not contain. The cited examples verify those cases only; they do not
support the frequency words. Revise these passages to example-bounded,
row-level observations and state that the existing outputs do not quantify
the prevalence of imbalance, or cite an authorized claim-bearing aggregate
artifact if one is produced through the governed analysis path. Likewise,
median-near-zero plus one extreme case supports heterogeneity, but not the
specific “minority carried the means” attribution without a recorded
contribution analysis.

## 3. Completeness without cherry-picking

I checked all three primary strata, all reported median contrasts and
intervals, the 297 per-patient rows, all 594 tissue-audit rows, the complete
exclusions table, and the three identity-residual rows. The interpretation
does not hide the material reversal: stratum 2 is negative while stratum 3 is
positive, and stratum 1 includes zero. It reports both authorized exclusions,
the tissue-audit heterogeneity, the central-volume result, and the untouched
reserved cases. No omitted table feature contradicts the primary negative.
The only completeness problem is the unsupported aggregation described in
check 2, not omission of an adverse result.

## 4. Verdict separation

The preregistered gate failure and provenance facts are correctly placed
under “Demonstrates.” Per-band pattern interpretation, patient heterogeneity,
and tissue-composition implications are placed under “Suggests,” and the
“Does not establish” section correctly blocks physiological, model-use,
channel-attribution, and external-generalization upgrades. Subject to removing
the unrecorded aggregations above, the separation is sound.

## 5. Plain-language fidelity

There is no distinct plain-language summary section. The “Next decision” and
positive/negative recap retain the main hedges and do not upgrade the primary
finding, but their statements that the HU audit demonstrates tissue imbalance
inherit the blocking aggregation problem above and must be narrowed with it.

```json
{"verdict": "REVISE", "blocking": ["Remove or replace the cohort-level HU-frequency and tail-contribution claims that are not present in a claim-bearing analysis artifact: 'most cases', 'often by 10–20 HU', 'typical median difference <=2 HU', 'often show very wide HU spread', and 'means are carried by a minority of patients'. Keep only cited row-level examples and explicitly say prevalence was not computed, or route a computed aggregate through the governed analysis path and cite it. Narrow the recap's unqualified tissue-imbalance claim consistently."]}
```
