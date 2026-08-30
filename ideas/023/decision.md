# Decision — idea 023, probe 023 Phase C outcome census (take 13)

## Result card

- **Idea:** idea-023 — "The joint CBV/MTT compensation state at matched flow"
  (charter isles24; reduced claim: outcome-associated joint CBV/MTT decision
  boundary; the phrase "autoregulatory blood-volume reserve" is prohibited).
- **Probe / sequence position:** probe 023, contract v1 as amended
  (mirror-free design), Phase C real-data census, take 13 — the first and
  only outcome-reading run for this idea. Preceded by outcome-blind Phase S
  synthetic calibration and twelve operational takes that stopped before any
  label access.
- **Dataset / pin:** ISLES'24 public training release, Zenodo record
  16813698 (published 2025-08-12), `train.7z` md5
  `36ae28b9a17f7340b8bbef62b595cb57`, sha256 `038920e4dc2011a3…`, 149
  released cases.
- **Primary metric:** per within-patient CBF-percentile band ([0,33),
  [33,67), [67,100] of finite deficit CBF), equal-patient-weight mean of
  d = risk(Q1 low-CBV) − risk(Q4 high-CBV) over the patient's own label-blind
  log-CBV quartile cells in the eroded Tmax>6s deficit region; 95%
  patient-bootstrap percentile CI (2,000 resamples, seed 20260824).
  Preregistered gate: three-band conjunction (common nonzero sign; ≥2 of 3
  CIs excluding zero in that direction; all CI widths ≤ 0.15).
- **Contract blob:** `03d4545fe293f0067c69ce9e9e696ec97b894d7b`; approval
  marker bound to the same blob (2026-08-28T02:31:13Z).
- **Results bundle:** `probes/023/results/results_v2/` at commit
  `1c0acdbf5dccabd00449c5235b5e83e3bb369f51`; all citations resolve there.
- **Families:** authored by the Claude family (interpret-build leg 1);
  revised in round 2 per the round-1 cross-family review; re-review
  pending.
- **Out-of-scope warnings:** not evidence about autoregulatory reserve,
  vasodilatory capacity, or any causal physiology; no CBV-vs-MTT channel
  claim (the central-volume identity holds in these maps); no model was
  probed, so nothing about model use; not evidence that CBV/MTT lacks
  biological importance; scope is 99 analyzed treated patients, icobrain cva
  maps, this operationalization only — reserved cases and hidden test set
  untouched.

## Layer A — Finding

The take-13 census completed validly and its preregistered three-band gate
FAILED on direction: the ISLES'24 census labels do not carry a directionally
consistent joint CBV/MTT–outcome association at matched flow under this
operationalization. The middle flow band shows higher final-infarct
membership in high-CBV voxels (mean d = −0.032, 95% CI [−0.056, −0.008]),
the highest band the opposite (mean d = +0.023, CI [+0.005, +0.044]), and
the lowest band is indistinguishable from zero. All CI widths (0.039–0.065)
beat the frozen 0.15 precision bound with 99 contributing patients per band
against a floor of 20, so this is the contract's decisive negative, not a
power or support failure. Idea 023's Stage-0 keystone is therefore absent
as operationalized, and the contract PAUSEs the idea; the planned model-use
probe does not run. The single most important caveat: the label-blind NCCT
audit recorded per-case tissue composition for the CBV quartile cells, and
its cited example cases show large Q1-vs-Q4 attenuation differences (in the
lowest band, with frankly hypodense low-CBV cells); how prevalent that
imbalance is across the cohort was not quantified, so this negative binds
the percentile-band operationalization on these vendor maps — it does not
show the joint state is biologically or predictively empty.

## Layer B — Derivation narrative

1. **Governance.** Contract amended to the mirror-free design and frozen at
   blob `03d4545fe293…`; fresh human approval bound to that blob
   (2026-08-28T02:31Z); probe code approved through nine cross-family
   review rounds; the run's gate verified contract and approval blobs at
   start. Phase S (outcome-blind) had frozen the operating point —
   ≥20 patients/stratum, ≥100 voxels/cell, CI width ≤0.15 — and its output
   hash was re-verified at Phase C load.
2. **Provenance.** Zenodo record 16813698 pinned; archive md5 matched the
   record checksum; 2,981 members manifested; split frozen from immutable
   hashed IDs BEFORE any label access (manifest sha
   `da79e94b…`): 149 released cases → 100 census / 49 reserved.
3. **CONSORT flow.** 100 census cases in; 1 excluded (sub-stroke0043,
   pre-authorized `source_corrupt_member` — the archive-verified defective
   CBF member); 1 duplicate non-canonical lesion archive member excluded
   for sub-stroke0142 with the canonical derivative retained (case
   analyzed); 99 cases analyzed. All 99 contributed to all three bands
   (`per_patient.csv`: 297 rows); nonfinite voxels occurred only where
   permitted and were counted per case.
4. **Gates.** Grid/coverage: passed (resampling recorded per case in
   `schema_census.csv`). Identity coordinate: median absolute centered
   residual 0.0078 / 0.0036 / 0.0078 across bands vs the 0.10 kill limit —
   passed with an order of magnitude of headroom (no kill condition was
   approached). Support: 99 ≥ 20 per band — passed. Precision: max CI width
   0.0652 ≤ 0.15 — passed. Direction: signs (+, −, +) with the two
   zero-excluding intervals in opposite directions — FAILED. Result:
   `g_label_passed: false`, status `NEGATIVE_PATTERN`.
5. **Diagnostics.** The pre-registered label-blind HU tissue audit
   recorded 594 per-case rows; the bundle contains no aggregate HU
   statistic and cohort prevalence of imbalance was not computed. Cited
   example rows document Q1-vs-Q4 attenuation imbalance in band 1 (e.g.
   3.0 vs 23.0 HU), one balanced and one oppositely imbalanced case in
   band 2, and a very-wide-spread Q4 cell in band 3. Because cohort-wide
   HU balance was therefore not demonstrated, the 2026-08-28 rule's
   "balanced" branch cannot be certified and the tissue-composition caveat
   is applied conservatively, pointing any successor at a tissue-normalized
   reference. Median patient-level d is ~0 in every band while the band-2
   and band-3 mean CIs exclude zero, indicating between-patient
   heterogeneity; no contribution analysis was computed, so which or how
   many patients drive the means is not claimed.
6. **Variants.** All authorized variants are reported: Phase S (separate
   bundle, hash-pinned), this single Phase C analysis
   (`maximum_variants: 1`, one seed), and the estimator-untouched HU audit.
   Prior takes 1–12 never opened outcome data; the label freeze held.

## Layer C — Claims table

All rows cite `probes/023/results/results_v2/` at commit
`1c0acdbf5dccabd00449c5235b5e83e3bb369f51`.

| # | Claim | Value as cited | Source |
|---|---|---|---|
| 1 | Run status | NEGATIVE_PATTERN | [cite: summary.json | status] |
| 2 | Gate outcome | false | [cite: summary.json | g_label_passed] |
| 3 | Census / analyzed cases | 100 / 99 | [cite: summary.json | census_case_count, analyzed_census_case_count] |
| 4 | Released / reserved cases | 149 / 49 | [cite: summary.json | released_case_count, reserved_case_count] |
| 5 | Record pin | 16813698, 2025-08-12 | [cite: summary.json | record_id, publication_date] |
| 6 | Archive md5 = Zenodo checksum | 36ae28b9a17f7340b8bbef62b595cb57 | [cite: summary.json | archive_md5, zenodo_checksum] |
| 7 | Archive sha256 | 038920e4dc2011a3f47b8bb8421c67e36d07f1d84f1ba442563077480f75d129 | [cite: provenance.json | archive_sha256] |
| 8 | Archive members | 2981 | [cite: provenance.json | archive_member_count] |
| 9 | Split manifest sha256 | da79e94bdae3f59d23db497d5f26f0d57aa4f279847fe57ec9a8d05ebcf18843 | [cite: summary.json | split_manifest_sha256] |
| 10 | Band 1 mean d; CI; width | 0.006391646480739713; [−0.026830257261146396, 0.0383678779489388]; 0.06519813521008519 | [cite: per_stratum_summary.csv | stratum=1 | mean_d, ci_low, ci_high, ci_width] |
| 11 | Band 2 mean d; CI; width | −0.03200187198047477; [−0.05590632802084301, −0.007978192339199943]; 0.04792813568164307 | [cite: per_stratum_summary.csv | stratum=2 | mean_d, ci_low, ci_high, ci_width] |
| 12 | Band 3 mean d; CI; width | 0.02307549118960302; [0.004965694506583826, 0.04356979149013058]; 0.038604096983546755 | [cite: per_stratum_summary.csv | stratum=3 | mean_d, ci_low, ci_high, ci_width] |
| 13 | Median d per band | 0.0; −0.0005886681383370125; 0.000556250836852953 | [cite: per_stratum_summary.csv | stratum=1,2,3 | median_d] |
| 14 | Contributing patients per band | 99, 99, 99 | [cite: per_stratum_summary.csv | stratum=1,2,3 | patients] |
| 15 | Frozen support/precision minima | 20 patients; 100 voxels/cell; 0.15 width | [cite: resolved_config.json | minimum_contributing_patients_per_stratum, minimum_voxels_per_patient_quantile_cell, maximum_primary_ci_width] |
| 16 | Identity residual MAD per band (limit 0.10) | 0.0077610015869140625; 0.003559589385986328; 0.0077877044677734375 | [cite: identity_residual_summary.csv | stratum=1,2,3 | median_absolute_centered_residual] |
| 17 | Phase-S csv hash verified at load | 59069fa92399cd5c600c89e0d66bb4c7c12679e14f12824b54ae0ce6a6061ef4 | [cite: determinism_manifest_start.json | input_paths.phase_s_csv | sha256] |
| 18 | Source-corrupt exclusion | sub-stroke0043, source_corrupt_member | [cite: exclusions.csv | case_id=sub-stroke0043 | record_type, reason] |
| 19 | Duplicate lesion member excluded, case retained | sub-stroke0142 | [cite: exclusions.csv | case_id=sub-stroke0142, record_type=excluded_archive_lesion | reason] |
| 20 | HU audit rows | 594 | [cite: summary.json | bin_tissue_audit_rows] |
| 21 | Band-1 imbalance example | Q1 3.0 HU vs Q4 23.0 HU | [cite: bin_tissue_audit.csv | case_id=sub-stroke0092, stratum=1 | median_hu, both style_group rows] |
| 22 | Band-2 balance example | 21.0 vs 21.0 HU | [cite: bin_tissue_audit.csv | case_id=sub-stroke0002, stratum=2 | median_hu, both style_group rows] |
| 23 | Band-3 spread example | Q4 iqr_hu 314.5 | [cite: bin_tissue_audit.csv | case_id=sub-stroke0133, stratum=3, style_group=Q4_high_CBV | iqr_hu] |
| 24 | Large single-patient contrast example | d = −0.20385563685311792 | [cite: per_patient.csv | case_id=sub-stroke0002, stratum=1 | d] |
| 25 | Permitted nonfinite example | 302261 nonfinite MTT voxels | [cite: exclusions.csv | case_id=sub-stroke0113 | nonfinite_mtt_voxels] |
| 26 | Approval binding | blob 03d4545fe293f0067c69ce9e9e696ec97b894d7b, 2026-08-28T02:31:13Z | [cite: ../../../ideas/023/HUMAN_APPROVED_PROBE | full text] (repo path, outside bundle) |
| 27 | Gate line at run start | approval gate passed on 03d4545fe293… | [cite: run_log.txt | line 1] |

The HU-audit rows cited above verify those individual cases only. The
bundle contains no aggregate HU statistic, and no cohort-level frequency or
prevalence of imbalance is claimed anywhere in this decision.

## Verdict

**PAUSE.** The valid census matched the contract's negative_pattern: the
Stage-0 keystone (a precise, directionally consistent outcome association
with the joint CBV/MTT state at matched flow) is not present in the census
labels as operationalized, so idea 023 pauses and the model-use probe is not
authorized. This is a decisive negative for the keystone, not evidence that
the joint state lacks biological or predictive content — the HU audit's
cited example cases show tissue-imbalanced quartile cells (cohort
prevalence not quantified), and the band-2/band-3 sign reversal plus the
per-case audit table are the empirical starting points for any
tissue-normalized successor (parent idea-023) via the normal pipeline. The
separately pre-registered clinical-outcome join and the PAUSED transition
itself remain operator acts. Full analysis: `ideas/023/interpretation.md`
(revised per the round-1 cross-family review; decisions.md entry deferred
until the interpretation passes review).
