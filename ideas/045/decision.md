# Decision — idea 045, probe contract v3

## Result card

- **Idea:** idea-045 — "Did tissue composition create idea-023's sign
  reversal?"
- **Probe:** probes/045, contract v3 — the pooled-slope attenuation
  attribution analysis: third executed probe in the idea's sequence,
  after the v1 interaction feasibility audit (blob `e7071541…`,
  NEGATIVE_PATTERN) and the v2 pooled-slope feasibility audit (blob
  `5615afea…`, POSITIVE_PATTERN), and the **first outcome-reading
  experiment in this lineage**. One authorized variant, one seed, one
  run.
- **Dataset:** two frozen derived tables from the imported idea-023
  take-13 Phase-C bundle (ISLES'24, Zenodo record 16813698 via the
  parent's provenance), pinned by sha256: `bin_tissue_audit.csv`
  `35e896df…`, `per_patient.csv` `1d01551c…` [cite: input_manifest.csv |
  both rows | sha256].
- **Primary metric:** adjusted band-2 and band-3 equal-patient-weight
  mean final-infarct contrasts (d) at pooled zero centered HU imbalance,
  with 10,000-replicate patient-cluster bootstrap 95% percentile
  intervals and the frozen opposite-sign persistence rule
  (`interpretation_rule`, three classes, frozen precedence).
- **Contract blob:** `b1e283613d4fd47c77bfd1f2838a54791eb25954`,
  matching the human approval marker of 2026-09-01T06:57:20Z (which also
  pins registry sha `1c0e82a6…`) and the bundle's `resolved_config.json`
  (contract_version 3).
- **Results bundle:** `probes/045/results/results_v4/` at commit
  `14b183f0b5696bf7ce1d5320d2b71e95353447a4` (import manifest sha256
  `3bbdd2fd47917fd3305002276d346c045e7a75bb7e7a097d2b9afe74573c3b68`,
  13 files, locally executed, `source_commit` null under the
  local-import ancestry lane).
- **Families:** authoring family claude (this document and
  `interpretation.md`); reviewing family codex (cross-family citation
  review; this is round 1).
- **Out-of-scope warnings — this result must NOT be read as:** evidence
  of no association between HU imbalance and final-infarct contrast (a
  null slope never establishes independence under this contract);
  evidence that tissue composition plays no role in the parent reversal
  (only the linear common-slope median-HU explanation is closed —
  band-antisymmetric, nonlinear, and non-median composition effects were
  unexaminable by construction); a causal claim (severity remains an
  unadjusted common-cause alternative); validation of median NCCT
  attenuation as a tissue or viability measurement; a claim about any
  model's use of any signal; or generalization beyond the 99 analyzed
  cases and released pipeline.

## Layer A — Finding

The pre-registered decisive negative fired: adjusting for measured
tissue-composition imbalance does **not** explain idea-023's sign
reversal [cite: summary.json | status | value:
DECISIVE_MEASURED_EXPLANATION_FAILURE]. After adjustment to pooled zero
HU imbalance, band 2 stays negative (−0.0313, 95% CI [−0.0559, −0.0079])
and band 3 stays positive (+0.0224, 95% CI [+0.0039, +0.0434]) — the
parent's opposite-sign pattern survives with both patient-bootstrap
intervals excluding zero. The failure is structural, not marginal:
bands 2 and 3 carry nearly the same average HU imbalance, so adjustment
moved each band mean by only ±0.00067 and the band gap by −0.0013
against a gap of 0.0537. Confidence rests on the contract's own
uncertainty machinery — a complete 10,000-replicate seed-20260901
patient-cluster bootstrap with zero failed replicates on a
transcription-exact reconstruction of the parent's band means. The most
important caveat: the approved common-slope model cannot represent
opposite-signed HU effects across bands, so only this one measured
explanation is closed — not tissue composition in general, and not the
cause of the reversal, which remains unexplained.

## Layer B — Derivation narrative

1. **Governance chain.** The v1 interaction audit failed feasibility
   (condition 38.89 vs ≤30) and mandated respecification; the v2
   pooled-slope audit passed all ten gates and its ratified
   interpretation authorized drafting this outcome contract. Contract v3
   was drafted through probe-plan (commit `2b816b9`) and human-approved
   at 2026-09-01T06:57:20Z binding blob `b1e28361…` — the approval that
   answered the standing open question (yes, the common slope is worth
   reading d for, as one exploratory analysis). Probe code (run.py
   sha256 `69622688…`) passed cross-family review round 1 (APPROVE,
   `ideas/045/probe_review.md`); the harness self-check passed at
   07:10:41Z [cite: probes/045/verification.json | passed, checked_at |
   values]; the run executed at 07:11:28Z [cite: environment.txt |
   captured_utc | value]; the bundle validated and imported via
   record-result at commit `14b183f` with the transactional tail
   (scrutiny PROBED, digest, state re-materialized) at commit `e73fcef`.
2. **Flow of rows (CONSORT-style).** In: 594 audit rows and 297 outcome
   rows [cite: input_manifest.csv | both rows | total_rows]. Excluded:
   297 rows in 297 per-row records, all reason `non_primary_band` (198
   audit band-1 rows, 99 outcome band-1 rows) [cite: exclusions.csv |
   all rows | reason]; [cite: summary.json | excluded_input_rows,
   exclusion_records | values]. Analyzed: 198 rows from 99 unique cases,
   99 per band [cite: summary.json | analysis_rows, unique_cases |
   values]. Reserved cases touched: 0 [cite: summary.json |
   reserved_cases_accessed | value]. The split was frozen and hashed
   before the outcome file was first opened [cite: split_manifest.json |
   created_before_outcome_file_open | value], byte-identical to both
   feasibility audits' split (hash `6446ad66…`).
3. **Gates.** Authority, input-identity (in-run sha256 enforcement),
   join/cohort (99/99, bidirectional key equality, Q1/Q4 completeness),
   and the parent-reconstruction gate all passed — the unadjusted band
   means equal the parent census values digit-for-digit
   (−0.03200187198047477 / +0.02307549118960302) [cite: summary.json |
   unadjusted_band2_mean, unadjusted_band3_mean | values];
   [cite: probes/023/results/results_v2/per_stratum_summary.csv |
   stratum=2, stratum=3 | mean_d]. The bootstrap completed 10,000/10,000
   with zero failures [cite: bootstrap_summary.json |
   replicates_completed, failed_replicates | values]; start/end
   determinism manifests agree exactly [cite: run_log.txt | phase 4 |
   final line]. The frozen classification then fired the decisive arm;
   per the stopping rule the run wrote its outputs and stopped.
4. **Kill conditions approached.** None fired. The tightest element of
   the decisive conjunction is the adjusted band-3 lower interval edge
   at +0.0038892800799788215 above zero [cite: summary.json |
   primary_metric | adjusted_band3_ci95]; every other clause (bootstrap
   failures 0 allowed 0, wall cap 30 min not approached, no analysis
   deviation possible with a rank-3 three-coefficient design) held with
   wide margin.

## Layer C — Claims table

Bundle root: `probes/045/results/results_v4/` at commit
`14b183f0b5696bf7ce1d5320d2b71e95353447a4`.

| Claim | Value | Source |
|---|---|---|
| Status | DECISIVE_MEASURED_EXPLANATION_FAILURE | [cite: summary.json | status | value] |
| Adjusted band-2 mean / 95% CI | −0.03133128471039588 / [−0.05589866048677166, −0.00789029340507566] | [cite: summary.json | primary_metric | adjusted_band2_mean, adjusted_band2_ci95] |
| Adjusted band-3 mean / 95% CI | 0.022404903919524183 / [0.0038892800799788215, 0.043408163548312576] | [cite: summary.json | primary_metric | adjusted_band3_mean, adjusted_band3_ci95] |
| Opposite-sign precise conjunction | true | [cite: summary.json | primary_metric | opposite_sign_precise] |
| beta_HU (d per HU) / 95% CI | 0.0010664775781553057 / [−0.001291573690909813, 0.003726706840533707] | [cite: summary.json | beta_hu, beta_hu_ci95 | values] |
| Unadjusted band means (b2 / b3) | −0.03200187198047477 / 0.02307549118960302 | [cite: summary.json | unadjusted_band2_mean, unadjusted_band3_mean | values] |
| Parent census band means (identity check) | −0.03200187198047477 / 0.02307549118960302 | [cite: probes/023/results/results_v2/per_stratum_summary.csv | stratum=2, stratum=3 | mean_d] |
| Unadjusted band CIs (b2 / b3) | [−0.056479044230713024, −0.008452118424017972] / [0.004474527044185139, 0.04414153124274204] | [cite: bootstrap_summary.json | intervals | unadjusted_band2_mean, unadjusted_band3_mean] |
| Adjusted band-3 − band-2 / 95% CI | 0.053736188629920065 / [0.025413321882444898, 0.08507011789496013] | [cite: bootstrap_summary.json | point_estimates, intervals | adjusted_band3_minus_band2] |
| Unadjusted band-3 − band-2 / 95% CI | 0.05507736317007779 / [0.026557076228044582, 0.08651935088065663] | [cite: bootstrap_summary.json | point_estimates, intervals | unadjusted_band3_minus_band2] |
| Per-band adjustment change (b2 / b3) | +0.0006705872700788901 / −0.000670587270078838 | [cite: bootstrap_summary.json | point_estimates | band2_adjustment_change, band3_adjustment_change] |
| Absolute band-gap change / 95% CI | −0.0013411745401577246 / [−0.005869901597083304, 0.002309145813085035] | [cite: bootstrap_summary.json | point_estimates, intervals | absolute_band_difference_change] |
| Bootstrap replicates / failed / method / seed | 10000 of 10000 / 0 / percentile_95 / 20260901 | [cite: bootstrap_summary.json | replicates_completed, replicates_requested, failed_replicates, interval_method, seed | values] |
| Model coefficients (intercept / band3 / beta_HU) | −0.03133128471039588 / 0.053736188629920065 / 0.0010664775781553057 | [cite: model_diagnostics.json | coefficients | all keys] |
| Design rank / max leverage / pooled center / RSS | 3 / 0.15486441040641785 / −0.15909079349402225 / 2.4783249809755676 | [cite: model_diagnostics.json | design_rank, maximum_leverage, pooled_hu_imbalance_center, residual_sum_squares | values] |
| Extreme-imbalance rows (heterogeneity note) | sub-stroke0183 b2: imbalance +18.0, d +0.24045261669024046, residual +0.25241763822968855; sub-stroke0109 b3: imbalance −28.0, d 0.0 | [cite: per_patient_attribution.csv | case_id=sub-stroke0183, stratum=2; case_id=sub-stroke0109, stratum=3 | hu_imbalance, d, residual_d] |
| Parent band medians (means-vs-medians caveat) | −0.0005886681383370125 / 0.000556250836852953 | [cite: probes/023/results/results_v2/per_stratum_summary.csv | stratum=2, stratum=3 | median_d] |
| Analysis rows / unique cases | 198 / 99 | [cite: summary.json | analysis_rows, unique_cases | values] |
| Input row accounting | audit 594→396; outcome 297→198; 297 excluded in 297 records, all non_primary_band | [cite: input_manifest.csv | both rows | total_rows, selected_rows]; [cite: exclusions.csv | all rows | reason] |
| Outcome-blindness of design | split frozen before outcome open, hash 6446ad66… identical to v2/v3 | [cite: split_manifest.json | created_before_outcome_file_open, sha256 | values]; [cite: probes/045/results/results_v3/split_manifest.json | sha256 | value] |
| Reserved cases accessed | 0 | [cite: summary.json | reserved_cases_accessed | value] |
| Input pins | bin_tissue_audit.csv 35e896df…; per_patient.csv 1d01551c… | [cite: input_manifest.csv | both rows | sha256] |
| Governing contract blob / version | b1e283613d4fd47c77bfd1f2838a54791eb25954 / 3 | [cite: resolved_config.json | contract_blob, contract_version | values] |
| v1 baseline (why band-specific slopes were not fit) | condition 38.889769743817595 vs ≤30 | [cite: probes/045/results/results_v2/design_diagnostics.json | condition_number | value] |
| Variant / seed / smoke / network | 1 of 1 / 20260901 (1 of 1) / false / 0 | [cite: summary.json | variants_run, smoke | values]; [cite: resolved_config.json | seed, network_calls | values] |
| Environment | numpy 2.5.2, Python 3.13.7, 2026-09-01T07:11:28Z | [cite: environment.txt | numpy, python, captured_utc | values] |

## Decision

**PAUSE.** The card's question is answered on its own pre-registered
terms: Q1-minus-Q4 median NCCT attenuation imbalance does not account
for idea-023's opposite-signed band-2/band-3 contrasts at achieved
precision — the reversal survives adjustment intact. This is the
decisive arm the 2026-09-01 operator ruling explicitly preserved ("a
reversal that persists under adjustment decisively shows attenuation
imbalance does not explain it"), and the revision made this analysis the
whole candidate, so the contract's spent stopping rule closes the card's
scientific program. Nothing further is authorized: the removed
tissue-gated census stays removed, the 49 reserved cases and all other
outcome structure stay unread, and the lineage's own rule against a
third same-taste operationalization applies. Next acts after
cross-family review approves: (1) ratify-interpretation with status
PAUSED, reason recorded as a pre-registered decisive negative for the
measured explanation; (2) register any successor — band-specific
specification solving the v1 conditioning failure, a non-median
composition measurement, or a severity-adjustment design — as a new
candidate through the normal pipeline; (3) ops: add the executed
attribution node to `ideas/045/registry.yaml` and re-ratify (the marker
pins the two-node registry sha `1c0e82a6…`; probe_review finding 7
anticipated this). Round 1: this decision summarizes
`interpretation.md`; no `evidence/decisions.md` entry is appended until
the cross-family review approves.
