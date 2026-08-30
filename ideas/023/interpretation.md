# Interpretation — idea 023, probe 023 Phase C outcome census (take 13)

## Result card

- **Idea:** idea-023 — "The joint CBV/MTT compensation state at matched flow"
  (charter isles24; reduced claim scope per the 2026-08-17 operator ruling:
  outcome-associated joint CBV/MTT decision boundary only).
- **Probe and position in sequence:** probe 023, contract v1 as amended
  (mirror-free matched-flow design), Phase C real-data census, take 13. This
  is the FIRST and ONLY run in the idea's history that read outcome (lesion)
  data. It was preceded by Phase S synthetic calibration (a separate,
  outcome-blind bundle whose selected operating point and output hash are
  frozen into the contract) and by twelve operational takes that all stopped
  before any outcome access.
- **Dataset:** ISLES'24 public training release, Zenodo record 16813698
  (published 2025-08-12), archive `train.7z`, md5 `36ae28b9a17f7340b8bbef62b595cb57`,
  sha256 `038920e4dc2011a3f47b8bb8421c67e36d07f1d84f1ba442563077480f75d129`,
  2,981 archive members, 149 released cases.
- **Primary metric:** per within-patient CBF-percentile band (three bands:
  [0,33), [33,67), [67,100] of finite deficit CBF), the equal-patient-weight
  mean of d = risk(Q1 low-CBV) − risk(Q4 high-CBV), where Q1/Q4 are the
  patient's own label-blind log-CBV quartile cells inside the eroded
  Tmax>6s deficit region; 95% patient-bootstrap percentile CI, 2,000
  resamples, `numpy default_rng(20260824)`. Preregistered gate: the
  three-band conjunction in `analysis.pass_rule` (same nonzero sign in all
  three bands; ≥2 of 3 CIs excluding zero in that direction; every CI width
  ≤ the frozen 0.15).
- **Contract blob:** `03d4545fe293f0067c69ce9e9e696ec97b894d7b`; the
  standing approval marker (`ideas/023/HUMAN_APPROVED_PROBE`, approved
  2026-08-28T02:31:13Z) binds exactly this blob, and the run's gate recorded
  the same blob for both contract and approval.
- **Results bundle:** `probes/023/results/results_v2/`, imported at commit
  `1c0acdbf5dccabd00449c5235b5e83e3bb369f51`. All citations below resolve
  inside that bundle at that commit unless another path is given.
- **Families:** interpretation authored by the Claude family (interpret-build
  leg 1); cross-family citation review pending (`interpret_review.md`, round 1).
- **Out-of-scope warnings.** This result must NOT be read as: evidence about
  autoregulatory blood-volume reserve, vasodilatory capacity, collateral or
  reperfusion mechanism, or any causal physiology; a CBV-versus-MTT channel
  claim (the central-volume identity holds almost exactly in these maps, so
  they are one degree of freedom at fixed CBF); evidence that any model uses
  or ignores anything (no model was probed); evidence that CBV/MTT lacks
  biological importance; or a statement about the reserved 49 cases, the
  hidden test set, other cohorts, or other map-generation pipelines (all
  maps are icobrain cva output; the treated-cohort scope limit stands).

## Where the uncertainty lives

The census is a deterministic CPU analysis of a frozen case set: pinned
archive, hash-frozen split, fixed bootstrap seed, and byte-identical
start/end determinism manifests (`determinism_manifest_start.json` and
`determinism_manifest_end.json` are identical). There is no training or
seed stochasticity; uncertainty is case-level and is carried by the
contract's own patient-bootstrap machinery. Effect statements below are
therefore judged against those intervals, and remain bounded by cohort
scope: one treated cohort, one vendor's maps, 99 analyzed patients.

## Demonstrates

1. **A valid census completed under the approved contract.** Gate passed on
   blob `03d4545fe293…` [cite: run_log.txt | line 1 | approval line]; the
   archive checksum matched the pinned Zenodo record
   [cite: summary.json | archive_md5 | 36ae28b9a17f7340b8bbef62b595cb57]
   [cite: summary.json | zenodo_checksum | md5:36ae28b9a17f7340b8bbef62b595cb57];
   the Phase-S calibration file consumed at run time hashes to the
   contract-frozen value
   [cite: determinism_manifest_start.json | input_paths.phase_s_csv | sha256 = 59069fa92399cd5c600c89e0d66bb4c7c12679e14f12824b54ae0ce6a6061ef4]
   [cite: summary.json | simulation_output_sha256 | 59069fa9…]. The released
   case count resolved to 149 [cite: summary.json | released_case_count | 149],
   settling the contract's 149-vs-150 discrepancy clause by archive census.
2. **The preregistered G-label gate FAILED — the contract's negative
   pattern, not a power failure.**
   [cite: summary.json | g_label_passed | false]
   [cite: summary.json | status | NEGATIVE_PATTERN]. Per band
   (equal-patient-weight mean d; 95% patient-bootstrap CI):
   - Band 1 (lowest CBF): mean d = 0.006391646480739713, CI
     [−0.026830257261146396, 0.0383678779489388], width 0.06519813521008519 —
     includes zero
     [cite: per_stratum_summary.csv | stratum=1 | mean_d, ci_low, ci_high, ci_width].
   - Band 2 (middle CBF): mean d = −0.03200187198047477, CI
     [−0.05590632802084301, −0.007978192339199943], width 0.04792813568164307 —
     excludes zero, NEGATIVE (higher-CBV voxels carry MORE final-infarct
     membership)
     [cite: per_stratum_summary.csv | stratum=2 | mean_d, ci_low, ci_high, ci_width].
   - Band 3 (highest CBF): mean d = 0.02307549118960302, CI
     [0.004965694506583826, 0.04356979149013058], width 0.038604096983546755 —
     excludes zero, POSITIVE (lower-CBV voxels carry more membership)
     [cite: per_stratum_summary.csv | stratum=3 | mean_d, ci_low, ci_high, ci_width].
   The conjunction fails on direction: signs are (+, −, +), and the two
   intervals that exclude zero do so in OPPOSITE directions. Every CI width
   beats the frozen 0.15 bound and support is 99 contributing patients per
   band against a frozen floor of 20
   [cite: per_stratum_summary.csv | stratum=1,2,3 | patients = 99]
   [cite: resolved_config.json | minimum_contributing_patients_per_stratum | 20]
   [cite: resolved_config.json | maximum_primary_ci_width | 0.15], so the
   negative is the decisive kind the contract defined ("mixed or zero
   directions" with adequate preregistered support), not an
   insufficient-support indeterminate.
3. **The central-volume identity holds essentially by construction in these
   maps.** Median absolute centered residual of u = log(CBF·MTT/CBV):
   0.0077610015869140625 (band 1), 0.003559589385986328 (band 2),
   0.0077877044677734375 (band 3), all far below the invalidating 0.10 limit
   [cite: identity_residual_summary.csv | stratum=1,2,3 | median_absolute_centered_residual]
   [cite: summary.json | identity_mad | 1,2,3]. This directly confirms the
   card's one-degree-of-freedom premise (and its prohibition on channel
   attribution) for the icobrain cva maps.
4. **The two authorized exclusions occurred exactly as pre-specified.** The
   known source-defective CBF member excluded sub-stroke0043
   [cite: exclusions.csv | case_id=sub-stroke0043, record_type=excluded_case | reason = source_corrupt_member]
   [cite: summary.json | excluded_source_corrupt_cases | 1]; the duplicate
   non-canonical lesion archive member for sub-stroke0142 was excluded while
   the case's canonical follow-up derivative was retained and analyzed
   [cite: exclusions.csv | case_id=sub-stroke0142, record_type=excluded_archive_lesion | reason]
   [cite: summary.json | excluded_duplicate_lesion_members | 1]. Analyzed
   n = 99 of 100 census cases
   [cite: summary.json | analyzed_census_case_count | 99]
   [cite: summary.json | census_case_count | 100].

## Suggests (exploratory; single cohort, single operationalization)

1. **Band-dependent, opposite-signed label structure.** Only the three-band
   conjunction was preregistered as the gate; the per-band contrasts are its
   components. Read exploratorily, they suggest the released labels carry a
   real but non-uniform relationship to the joint CBV/MTT coordinate: in the
   middle flow band high CBV accompanies MORE infarct membership, in the
   highest band less. This is a citable observation about a modern,
   reperfusion-treated cohort's outcome structure (the census side-result
   the critique anticipated), but with the tissue-composition caveat below
   it must not be promoted to a physiological statement.
2. **The typical patient shows almost no contrast; the means are
   tail-driven.** Median patient-level d is 0.0 (band 1),
   −0.0005886681383370125 (band 2), 0.000556250836852953 (band 3), with
   median CIs hugging zero
   [cite: per_stratum_summary.csv | stratum=1,2,3 | median_d, median_ci_low, median_ci_high],
   while individual patients reach large contrasts of either sign (e.g.
   sub-stroke0002, band 1: d = −0.20385563685311792
   [cite: per_patient.csv | case_id=sub-stroke0002, stratum=1 | d]). The
   band-level means are carried by a minority of patients, which further
   weakens any reading of a cohort-wide encoded association.
3. **The CBV-quartile cells are NOT tissue-matched — the pre-registered HU
   audit found systematic imbalance.** The label-blind NCCT audit
   (594 rows = 99 cases × 3 bands × 2 cells
   [cite: summary.json | bin_tissue_audit_rows | 594]) shows, by inspection
   of the full table (no aggregate statistic exists in the bundle; the
   per-case rows are the recorded output):
   - In band 1 (lowest CBF), Q1 low-CBV cells sit at markedly lower NCCT
     attenuation than Q4 cells in most cases, often by 10–20 HU, with Q1
     medians at frankly hypodense values — e.g. sub-stroke0092: Q1 median
     3.0 HU vs Q4 23.0 HU
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0092, stratum=1, style_group=Q1_low_CBV | median_hu = 3.0]
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0092, stratum=1, style_group=Q4_high_CBV | median_hu = 23.0];
     sub-stroke0057: 5.0 vs 24.0; sub-stroke0189: 6.0 vs 25.0
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0057, stratum=1 | median_hu rows]
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0189, stratum=1 | median_hu rows].
   - In band 2 the cells are near-balanced in most cases (typical median
     difference ≤ 2 HU, e.g. sub-stroke0002: 21.0 vs 21.0
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0002, stratum=2 | median_hu rows]),
     with exceptions in both directions (e.g. sub-stroke0183: 23.0 vs 5.0
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0183, stratum=2 | median_hu rows]).
   - In band 3 the direction is mixed and Q4 cells often show very wide HU
     spread (e.g. sub-stroke0109: Q1 30.0 vs Q4 58.0
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0109, stratum=3 | median_hu rows];
     sub-stroke0133 Q4 IQR 314.5
     [cite: bin_tissue_audit.csv | case_id=sub-stroke0133, stratum=3, style_group=Q4_high_CBV | iqr_hu]),
     consistent with residual vessel/hyperdense contamination surviving the
     per-patient p98 CBV cap.
   INFERENCE (labeled as such): in the lowest-flow band, low-CBV voxels are
   substantially voxels that are already hypodense on NCCT — established
   tissue injury or partial-volume CSF — so the Q1-vs-Q4 contrast partly
   re-measures visible tissue state rather than a hemodynamic state at
   matched tissue. Under the pre-registered 2026-08-28 interpretation rule,
   this is the "systematic imbalance" branch: any predictive information in
   these bins is conditional and carries a tissue-composition caveat, and a
   tissue-normalized successor design is the recorded consequence. (The
   other branch — "the compensation reading stands" — is moot here because
   G-label failed regardless.)

## Does not establish

- That final-infarct outcome in ISLES'24 carries NO joint CBV/MTT
  information. The gate tests one operationalization: within-patient CBF
  percentile bands, per-patient log-CBV quartile extremes, equal patient
  weights. The HU audit shows this operationalization mixes tissue types
  within cells; a tissue-normalized reference (the retired contralateral
  mirror was, incidentally, exactly that) could still reveal a consistent
  association.
- Anything about autoregulatory reserve, vasodilatory capacity, or the
  physiological cause of the band-2/band-3 sign difference.
- Anything about any model — no model existed or was probed; the planned
  model-use probe was contingent on this gate passing.
- Anything about the reserved 49 cases (untouched
  [cite: summary.json | reserved_case_count | 49]), the hidden test set,
  untreated cohorts, or maps from any pipeline other than icobrain cva.
- CBV-versus-MTT channel structure — explicitly prohibited, and the
  near-zero identity residual confirms the degeneracy is real.

## Validity failures

None. No invalidating-failure class in the contract was triggered: split
frozen before label access (manifest sha256
`da79e94bdae3f59d23db497d5f26f0d57aa4f279847fe57ec9a8d05ebcf18843`
[cite: summary.json | split_manifest_sha256]); provenance, checksum, and
census gates all passed; nonfinite voxels occurred only where permitted and
were counted per case (largest example: sub-stroke0113, 302,261 nonfinite
MTT voxels excluded and recorded
[cite: exclusions.csv | case_id=sub-stroke0113 | nonfinite_mtt_voxels]);
patient clustering and equal weighting preserved by the frozen estimator;
determinism manifests identical at start and end. The take-8 unit
contingency remains executed-and-retired: the vessel exclusion ran as the
unit-free per-patient p98 rule, recorded per case (e.g. sub-stroke0002
vessel_cbv_p98 = 29.140625
[cite: exclusions.csv | case_id=sub-stroke0002 | vessel_cbv_p98]).

## Authorized variants — all reported

- **Phase S (synthetic calibration; outcome-blind).** Separate bundle
  (results branch `results/probe-023-0e223c82f9eb`); its selected operating
  point — 20 patients/stratum minimum, 100 voxels/cell minimum, 0.15 CI
  width — and output hash are frozen in the contract and were re-verified
  at Phase C load [cite: resolved_config.json | minimum_contributing_patients_per_stratum, minimum_voxels_per_patient_quantile_cell, maximum_primary_ci_width]
  [cite: determinism_manifest_start.json | input_paths.phase_s_csv | sha256].
- **Phase C (this run).** `maximum_variants: 1`, one frozen analysis, one
  seed (20260824 [cite: resolved_config.json | seed]). No other analysis
  variant, stratum selection, pooled fallback, or alternate threshold was
  run.
- **Label-blind NCCT tissue audit.** The 2026-08-28-activated run.py-only
  diagnostic; recorded per case/band/cell in `bin_tissue_audit.csv`
  (594 rows); no estimator or gate consumed it.
- **Prior takes 1–12.** Operational stops under this and superseded
  contract eras (staging, census, unit, and mirror-gate stops); none opened
  outcome or lesion data. The label freeze held until take 13.

## Positive and negative findings

- **Negative (primary, preregistered):** G-label failed on directional
  consistency; the Stage-0 keystone — a precise, directionally stable
  outcome association with the joint CBV/MTT state at matched flow — is NOT
  present in the census labels under this operationalization. Per the
  contract this is a scientific negative for the keystone and PAUSEs
  idea 023; it is not evidence that CBV/MTT lacks biological importance.
- **Positive (secondary, exploratory):** (a) the identity-residual census
  confirms the central-volume identity in the released maps (validating the
  one-degree-of-freedom framing); (b) two bands show precise, opposite-signed
  associations — an interpretable observation about label structure in a
  treated cohort, conditional on the tissue caveat; (c) the HU audit
  documents, quantitatively and per case, that per-patient CBV quartiles at
  matched flow percentile are tissue-imbalanced — direct empirical design
  input for any successor.

## Next decision

**PAUSE**, exactly as the contract's negative_pattern prescribes. No model
work, weight download, or edit inference is authorized; the reserved 49
cases stay untouched. Recommended operator sequence (all outside this
probe's authority): (1) ratify the PAUSED transition; (2) run the
separately pre-registered patient-level clinical-outcome join
(2026-08-28 entry) as its own gated step; (3) if the joint-state question
is to continue, register a tissue-normalized matched-flow successor
(parent idea-023) through the normal pipeline — the HU audit and the
band-2/band-3 sign reversal are its empirical starting points — noting
that the retired mirror design was the implicit tissue normalizer;
(4) the queued upstream report of the sub-stroke0043 source defect stands.
